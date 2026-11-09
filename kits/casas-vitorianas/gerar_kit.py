"""Kit 31: casas vitorianas coloridas (fileira de 5 sobrados geminados de madeira), em ALTO DETALHE (scripts/detalhe/detalhe.py).
Cada casa tem 6 x 12 m, porao alto de 1,5 m, 2 andares de 3,2 m e frontao de 50 graus para a rua. Fachada de tabuas sobrepostas,
bay window chanfrada de 2 andares com colunetas e cornija com misulas, janelas de guilhotina com frontaozinho, porta com bandeira,
pilastras e chapeu sobre misulas, escada de entrada de 10 degraus com balaustres e postes com globo. Frontao com escamas de peixe,
par de janelas em arco, tesoura decorativa com fusos e raios, lambrequim recortado e pinaculo. Telhado de telhas em fiadas, calhas
nos vales entre as casas, cumeeira e calhas nas pontas. Dentro: sala e jantar, hall com escada, 2 quartos no 1o andar.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)

HUES = ['a', 'b', 'c', 'd', 'e']
BODY = {'a': (232, 196, 112), 'b': (168, 188, 140), 'c': (136, 192, 182), 'd': (150, 180, 214), 'e': (232, 150, 122)}
ACC = {'a': (176, 88, 70), 'b': (112, 126, 92), 'c': (214, 176, 104), 'd': (72, 92, 136), 'e': (108, 142, 122)}
DOORC = {'a': (110, 40, 40), 'b': (92, 60, 40), 'c': (40, 92, 72), 'd': (150, 40, 44), 'e': (196, 118, 48)}
cores = {'trim': (244, 238, 222), 'frame': (244, 238, 222), 'sash': (250, 248, 240), 'shingles': (70, 74, 82), 'ridge': (58, 60, 66),
         'deck': (130, 96, 66), 'floor': (160, 112, 72), 'attic': (150, 120, 86), 'plaster': (240, 234, 222), 'concrete': (178, 174, 166),
         'plinth': (150, 144, 136), 'grass': (96, 140, 70), 'marble': (232, 228, 218), 'slate': (70, 72, 76), 'tile': (226, 228, 224),
         'dark': (30, 30, 32), 'iron': (34, 36, 38), 'flash': (150, 154, 156), 'player': (90, 140, 220)}
for c in HUES:
    cores[f'siding_{c}'] = BODY[c]; cores[f'acc_{c}'] = ACC[c]; cores[f'door_{c}'] = DOORC[c]
tex = {'deck': 'deck', 'floor': 'planks', 'attic': 'planks', 'plaster': 'plaster', 'concrete': 'render', 'plinth': 'stone2', 'shingles': 'shingles'}
for c in HUES: tex[f'siding_{c}'] = 'siding'
configurar(cores=cores, texturas=tex, out=OUT)
D.METAL.update({'flash'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.3; H = 3.2; SLAB = 0.2; RAISE = 1.5
H0 = H - SLAB
def lvl(fl): return RAISE + fl * H
Y0 = lvl(0); YE = lvl(2)                         # piso do terreo e topo das paredes (beiral)
HX = 3.0; HZ = 6.0; PT = 0.15; NH = 5            # meia largura e meia profundidade de cada casa, meia parede-meia
XC = [-12.0 + 6.0 * i for i in range(NH)]
ANG = 50.0; KR = math.tan(math.radians(ANG)); CS = math.cos(math.radians(ANG))
SX = HX; RIDGE = SX * KR                         # cumeeira (face de baixo) acima do beiral
OVE = 0.45; OVF = 0.45                           # beiral das pontas e avanco do frontao
TV = 0.08; BUMP = 0.022
configurar_telhado(TV, BUMP, ANG)
NR = 18; RS_ = H / NR; TR = 0.26; SW_ = 1.1; RUN = (NR - 1) * TR
SZ0 = -3.6; SZ1 = SZ0 + RUN                      # escada: pe (fundo) e topo (frente), sobe para +Z
WIN0 = (0.9, 0.55, 2.45); WIN1 = (0.9, 0.6, 2.35)  # janelas (largura, peitoril, verga) do terreo e do andar
DOOR = (1.0, 2.3, 2.65)                          # vao da porta: largura, verga da folha, topo da bandeira
BAYW = 0.95; BAYF = 0.55; BAYD = 0.55; BT = 0.12   # bay: meia largura na parede, meia largura da frente, avanco, parede

# ============================================================================ ferramentas
def ext(p, mat, poly, z0, z1):
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type == 'Polygon' and g.area > 1e-6:
            m = trimesh.creation.extrude_polygon(g, z1 - z0); m.apply_translation([0, 0, z0]); p.add(mat, D._fix(m))
def ext_y(p, mat, poly, y0, y1):
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type == 'Polygon' and g.area > 1e-6:
            m = trimesh.creation.extrude_polygon(g, y1 - y0); v = m.vertices.copy()
            m.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1); m.invert(); p.add(mat, D._fix(m))
def seg_cyl(p, mat, p0, p1, r, sec=8):
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1 - p0; Ln = np.linalg.norm(v)
    c = trimesh.creation.cylinder(radius=r, height=Ln, sections=sec); z = np.array([0, 0, 1.0]); v = v / Ln
    ax = np.cross(z, v); ang = math.acos(np.clip(np.dot(z, v), -1, 1))
    if np.linalg.norm(ax) > 1e-6: c.apply_transform(trimesh.transformations.rotation_matrix(ang, ax))
    elif v[2] < 0: c.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    c.apply_translation((p0 + p1) / 2); return p.add(mat, c)
def lathe(p, mat, prof, x=0.0, z=0.0, y0=0.0, sec=14):
    for (r0, ya), (r1, yb) in zip(prof[:-1], prof[1:]):
        if abs(yb - ya) < 1e-6: continue
        pts = [(x + r * math.cos(a), y0 + y, z + r * math.sin(a)) for (r, y) in ((r0, ya), (r1, yb)) for a in np.linspace(0, 2 * math.pi, sec, endpoint=False)]
        p.hull(mat, pts)
def arch_geom(w, ys, rise):
    R = (w * w / 4 + rise * rise) / (2 * rise); return R, ys + rise - R
def opening(w, sill, ys, rise, x=0.0):
    R, cy = arch_geom(w, ys, rise)
    top = Point(x, cy).buffer(R, 48).intersection(sbox(x - w / 2, ys - 0.001, x + w / 2, ys + rise + 0.01))
    return unary_union([sbox(x - w / 2, sill, x + w / 2, ys), top]).buffer(0)
def frame_of(u, n, o, ang=None):
    """Matriz que leva coordenadas locais (x ao longo de u, y para cima, z ao longo de n) para o plano, com origem o (x, z)."""
    M = np.eye(4); M[0, 0], M[2, 0] = u; M[0, 2], M[2, 2] = n; M[0, 3], M[2, 3] = o; return M
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p
def recolor(p, c):
    """Troca os materiais genericos (siding, acc, door) pelos da casa c."""
    for k in ('siding', 'acc', 'door'):
        if k in p.parts: p.parts[f'{k}_{c}'] = p.parts.pop(k)
        if k in p.uv: p.uv[f'{k}_{c}'] = p.uv.pop(k)
    return p
def courses(fl):
    """Tabuas da fachada: no terreo de 0 a 3,0 (15 fiadas); no andar de -0,2 a 3,2 (17 fiadas), sempre na mesma fase."""
    if fl == 0: configurar_tabuas(0.0, H0, 0.2)
    else: configurar_tabuas(-SLAB, H, 0.2)

# ============================================================================ janelas, porta e enfeites
def hood(p, ow, oy1, pediment=True):
    """Chapeu da janela sobre a verga da biblioteca: 2 misulas recortadas, prateleira com pingadeira e frontaozinho."""
    x = ow / 2 + 0.11
    for s in (-1, 1):
        xx = s * x
        p.hull('trim', [(xx + dx, yy, zz) for dx in (-0.022, 0.022) for (zz, yy) in ((-0.01, oy1 + 0.03), (-0.01, oy1 + 0.25), (0.1, oy1 + 0.25), (0.1, oy1 + 0.2), (0.03, oy1 + 0.06))])
    prof_x(p, 'trim', -x - 0.07, x + 0.07, [(-0.01, oy1 + 0.25), (0.12, oy1 + 0.25), (0.13, oy1 + 0.262), (0.13, oy1 + 0.285), (0.11, oy1 + 0.3), (-0.01, oy1 + 0.3)])
    if pediment:
        y0 = oy1 + 0.3; w2 = x + 0.04
        tri = Polygon([(-w2, y0), (w2, y0), (0, y0 + 0.24)])
        ext(p, 'trim', tri, -0.01, 0.04)
        ext(p, 'acc', tri.buffer(-0.045, join_style=2), 0.04, 0.05)
        for s in (-1, 1):   # molduras inclinadas
            a = (s * (w2 + 0.04), y0 - 0.005); b = (0, y0 + 0.28)
            ln = LineString([a, b]).buffer(0.025, cap_style=2); ext(p, 'trim', ln.intersection(sbox(-w2 - 0.06, y0, w2 + 0.06, y0 + 0.4)), -0.01, 0.065)
def door_victorian(w=0.92, h=2.28, t=0.05):
    """Folha da porta da frente: 2 vidros altos em arco no alto, almofada larga no meio e 2 almofadas embaixo; macaneta e campainha."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2); cut = []
    for (a, b) in ((0.11, 0.42), (0.5, 0.81)):
        cut.append(tbox(a, b, 1.25, h - 0.3, -t, t))
        for z in (t / 2, -t / 2): cut.append(tbox(a, b, 0.16, 0.78, z - 0.01, z + 0.01))
    for z in (t / 2, -t / 2): cut.append(tbox(0.11, w - 0.11, 0.88, 1.15, z - 0.01, z + 0.01))
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    for (a, b) in ((0.11, 0.42), (0.5, 0.81)):
        p.box('glass', a - 0.004, b + 0.004, 1.246, h - 0.296, -0.004, 0.004)
        for z in (1, -1):    # arco de madeira por cima do vidro
            z0, z1 = sorted((z * 0.004, z * (t / 2 - 0.005)))
            arc_ = Point((a + b) / 2, h - 0.3 - (b - a) / 2).buffer((b - a) / 2, 16).intersection(sbox(a, h - 0.3 - (b - a) / 2, b, h))
            ext(p, 'door', sbox(a, h - 0.3 - (b - a) / 2, b, h - 0.3).difference(arc_), z0, z1)
    for z in (1, -1):
        p.cham('brass', w - 0.115, w - 0.065, 0.85, 1.1, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.sphere('brass', 0.03, w - 0.09, 1.0, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.09, 1.0, z * t / 2), (w - 0.09, 1.0, z * (t / 2 + 0.04)), 0.016)
    p.cyl('brass', 0.03, 1.4, 1.42, w / 2, 0.0, 12) if False else p.cham('brass', w / 2 - 0.06, w / 2 + 0.06, 1.38, 1.42, t / 2, t / 2 + 0.012, 0.003)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def door_back_leaf(w=0.86, h=2.2, t=0.045):
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.13, w - 0.13, 1.2, 2.04, -t, t)] + [tbox(0.13, w - 0.13, y0, y1, z - 0.01, z + 0.01) for (y0, y1) in ((0.16, 0.6), (0.7, 1.08)) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', 0.126, w - 0.126, 1.196, 2.044, -0.004, 0.004)
    p.cham('door', w / 2 - 0.014, w / 2 + 0.014, 1.2, 2.04, -0.013, 0.013, 0.004)
    for z in (1, -1):
        p.sphere('brass', 0.028, w - 0.085, 1.0, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.085, 1.0, z * t / 2), (w - 0.085, 1.0, z * (t / 2 + 0.04)), 0.015)
    for yy in (0.25, 1.1, 1.85): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p

# ============================================================================ paredes externas de tabuas
def wall_core(p, fl, holes, top):
    """Parede estanque: miolo de tabuas (cor da casa) com camada interna de gesso; no terreo, abaixo do piso, o porao (cor de
    destaque). holes = [(x0, x1, y0, y1)]."""
    y0 = -RAISE if fl == 0 else -SLAB
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, top - 0.005, top] + ([0.0] if fl == 0 else []) + [max(y0, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return None if ys[j] >= top - 0.0051 else 'plaster'
        return 'acc' if cy < 0 else 'siding'
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
WTB = [(0.0, -0.24), (0.04, -0.24), (0.04, -0.035), (0.075, -0.03), (0.085, -0.018), (0.085, 0.0), (0.0, 0.012)]
def base_trim(p, segs, vent=False):
    """Porao: fundacao de pedra, almofadas com moldura, mesa de agua com pingadeira na linha do piso; vent = respiro com grade."""
    for (a, b) in segs:
        prof_x(p, 'plinth', a, b, crect(0.0, 0.04, -RAISE, -RAISE + 0.3, 0.008, (0, 0, 1, 0)))
        prof_x(p, 'trim', a, b, WTB)
        prof_x(p, 'trim', a, b, crect(0.0, 0.03, -RAISE + 0.3, -RAISE + 0.4, 0.006, (0, 1, 1, 0)))
    for (a, b) in segs:
        L = b - a
        if L < 0.5: continue
        n = 1 if vent else max(1, int(round(L / 0.95)))
        for i in range(n):
            xa = a + i * L / n + 0.08; xb = a + (i + 1) * L / n - 0.08
            ring = sbox(xa, -RAISE + 0.5, xb, -0.36).difference(sbox(xa + 0.06, -RAISE + 0.56, xb - 0.06, -0.42))
            ext(p, 'trim', ring, -0.01, 0.035)
            if vent:
                xm = (xa + xb) / 2; ext(p, 'dark', sbox(xm - 0.22, -0.85, xm + 0.22, -0.65), -0.01, 0.0 + 0.004)
                for k in range(7): xx = xm - 0.18 + k * 0.06; p.box('iron', xx - 0.008, xx + 0.008, -0.85, -0.65, 0.004, 0.02)
                ext(p, 'trim', sbox(xm - 0.26, -0.89, xm + 0.26, -0.61).difference(sbox(xm - 0.22, -0.85, xm + 0.22, -0.65)), 0.004, 0.03)
def f_wall(kind='win', fl=0, back=False):
    """Modulo de 2 m de parede externa de tabuas (pivo: face externa, cota do piso). kind: 'win' (guilhotina com frontaozinho),
    'plain', 'door' (porta com bandeira, pilastras e chapeu), 'bay' (vao largo para a bay window). back = fundos (sem frontaozinho)."""
    p = Piece(); top = H0 if fl == 0 else H; courses(fl); holes = []; sid = []
    ow, oy0, oy1 = WIN0 if fl == 0 else WIN1
    if kind == 'win': holes = [(-ow / 2, ow / 2, oy0, oy1)]
    if kind == 'door': holes = [(-DOOR[0] / 2, DOOR[0] / 2, 0.0, DOOR[2])]
    if kind == 'bay': holes = [(-BAYW, BAYW, -0.03, 2.75)]
    wall_core(p, fl, holes, top)
    if kind == 'win':
        sid.append(window(p, ow, oy0, oy1, 1)); hood(p, ow, oy1, pediment=(fl == 0 and not back))
        sid[-1] = (sid[-1][0], sid[-1][1], sid[-1][2] - 0.2, sid[-1][3])
    if kind == 'door':
        x = DOOR[0] / 2; yt = DOOR[2]
        p.box('frame', -x, -x + 0.07, 0.0, yt, -0.2, -0.05); p.box('frame', x - 0.07, x, 0.0, yt, -0.2, -0.05)
        p.box('frame', -x + 0.07, x - 0.07, yt - 0.06, yt, -0.2, -0.05); p.box('frame', -x + 0.07, x - 0.07, DOOR[1], DOOR[1] + 0.05, -0.2, -0.05)
        p.box('glass', -x + 0.066, x - 0.066, DOOR[1] + 0.046, yt - 0.056, -0.13, -0.124)
        for i in (1, 2): xm = -x + 0.07 + (DOOR[0] - 0.14) * i / 3; p.box('frame', xm - 0.012, xm + 0.012, DOOR[1] + 0.05, yt - 0.06, -0.14, -0.11)
        p.box('frame', -x + 0.07, -x + 0.085, 0.015, DOOR[1], -0.13, -0.11); p.box('frame', x - 0.085, x - 0.07, 0.015, DOOR[1], -0.13, -0.11)
        prof_x(p, 'trim', -x, x, [(-T + 0.004, -0.03), (0.05, -0.03), (0.06, -0.02), (0.06, 0.012), (-T + 0.004, 0.012)])
        if not back:
            for s in (-1, 1):   # pilastras com base e capitel
                a, b = sorted((s * x, s * (x + 0.15)))
                prof_y(p, 'trim', 0.012, yt, crect(a, b, 0.0, 0.05, 0.006, (0, 0, 1, 1)))
                p.cham('trim', a - 0.015, b + 0.015, 0.012, 0.22, -0.01, 0.065, 0.006); p.cham('trim', a - 0.02, b + 0.02, yt - 0.12, yt, -0.01, 0.07, 0.006)
                ext(p, 'acc', sbox(a + 0.04, 0.35, b - 0.04, yt - 0.25), 0.05, 0.056)
            prof_x(p, 'trim', -x - 0.17, x + 0.17, crect(0.0, 0.06, yt, yt + 0.14, 0.006, (0, 1, 1, 0)))
            for s in (-1, 1):
                xx = s * (x + 0.08)
                p.hull('trim', [(xx + dx, yy, zz) for dx in (-0.03, 0.03) for (zz, yy) in ((-0.01, yt - 0.2), (-0.01, yt + 0.14), (0.3, yt + 0.14), (0.28, yt + 0.08), (0.06, yt - 0.1))])
            prof_x(p, 'trim', -x - 0.25, x + 0.25, [(-0.01, yt + 0.14), (0.33, yt + 0.14), (0.35, yt + 0.16), (0.35, yt + 0.2), (0.3, yt + 0.23), (-0.01, yt + 0.235)])
            sid.append((-x - 0.2, x + 0.2, -1.0, yt + 0.24))
        else:
            for s in (-1, 1):
                a, b = sorted((s * x, s * (x + 0.11))); prof_y(p, 'trim', 0.012, yt + 0.025, crect(a, b, 0.0, 0.036, 0.006, (0, 0, 1, 1)))
            prof_x(p, 'trim', -x - 0.13, x + 0.13, crect(0.0, 0.04, yt + 0.025, yt + 0.18, 0.006, (0, 1, 1, 0)))
            prof_x(p, 'trim', -x - 0.16, x + 0.16, [(0.0, yt + 0.18), (0.07, yt + 0.18), (0.07, yt + 0.205), (0.05, yt + 0.225), (0.0, yt + 0.235)])
            sid.append((-x - 0.03, x + 0.03, -1.0, yt + 0.05))
    if kind == 'bay': sid.append((-BAYW, BAYW, -1.0, 9.0))
    siding_field(p, sid, mat='siding')
    if fl == 0:
        if kind == 'door' and not back: segs = [(-W / 2, -0.8), (0.8, W / 2)]
        elif kind == 'door': segs = [(-W / 2, -0.6), (0.6, W / 2)]
        elif kind == 'bay': segs = [(-W / 2, -BAYW - 0.005), (BAYW + 0.005, W / 2)]
        else: segs = [(-W / 2, W / 2)]
        base_trim(p, segs, vent=(kind in ('win', 'plain')))
    return p
def cornice(p, F, x0=-W / 2, x1=W / 2, top=H, brackets=()):
    """Cornija italianizante no topo do andar (pivo: face da parede): friso, denticulos, misulas e coroa, seguindo a planta F
    (poligono que inclui a parede, z <= 0); as camadas sao F engordado e cortado em z >= 0."""
    clip = sbox(x0, 0.0, x1, 5.0)
    def layer(mat, d, ya, yb): ext_y(p, mat, F.buffer(d, join_style=2).intersection(clip), ya, yb)
    layer('trim', 0.03, top - 0.45, top - 0.2); layer('acc', 0.025, top - 0.2, top - 0.17); layer('trim', 0.05, top - 0.17, top - 0.1)
    layer('trim', 0.34, top - 0.1, top - 0.06); layer('trim', 0.37, top - 0.06, top + 0.02); layer('trim', 0.32, top + 0.02, top + 0.06)
    # denticulos ao longo do contorno
    ring = LineString(list(F.buffer(0.03, join_style=2).exterior.coords)).intersection(clip)
    for g in getattr(ring, 'geoms', [ring]):
        if g.length < 0.05: continue
        n = int(g.length / 0.09)
        for i in range(n):
            q = g.interpolate((i + 0.5) * g.length / n); qa = g.interpolate(max(0, (i + 0.5) * g.length / n - 0.01)); qb = g.interpolate(min(g.length, (i + 0.5) * g.length / n + 0.01))
            ux, uz = qb.x - qa.x, qb.y - qa.y; L_ = math.hypot(ux, uz)
            if L_ < 1e-6: continue
            ux, uz = ux / L_, uz / L_; nx, nz = uz, -ux
            if F.buffer(0.03, join_style=2).contains(Point(q.x + nx * 0.01, q.y + nz * 0.01)): nx, nz = -nx, -nz
            pts = [(q.x + ux * du + nx * dn, y, q.y + uz * du + nz * dn) for du in (-0.022, 0.022) for dn in (-0.005, 0.045) for y in (top - 0.2, top - 0.14)]
            p.hull('trim', pts)
    for (bx, bz, ang) in brackets:
        q = Piece()
        q.hull('trim', [(dx, yy, zz) for dx in (-0.035, 0.035) for (zz, yy) in ((0.0, top - 0.55), (0.0, top - 0.1), (0.32, top - 0.1), (0.3, top - 0.18), (0.12, top - 0.3), (0.06, top - 0.5))])
        q.sphere('acc', 0.03, 0.0, top - 0.42, 0.075, 0)
        M = trimesh.transformations.rotation_matrix(ang, [0, 1, 0]); M[0, 3], M[2, 3] = bx, bz; p.merge(q, M)
def cornice_flat():
    p = Piece(); cornice(p, sbox(-W / 2, -T, W / 2, 0.0), brackets=((-0.8, 0.03, 0.0), (0.8, 0.03, 0.0))); return p

# ============================================================================ bay window chanfrada de 2 andares
BAYO = Polygon([(-BAYW, 0.0), (BAYW, 0.0), (BAYF, BAYD), (-BAYF, BAYD)])
def bay_inner():
    k = (BAYW - BAYF) / BAYD; dx = BT * math.hypot(1, k)
    xl = lambda z: -BAYW + k * z + dx
    zi = BAYD - BT
    return Polygon([(xl(-0.01), -0.01), (-xl(-0.01), -0.01), (-xl(zi), zi), (xl(zi), zi)])
BAYI = bay_inner()
BAYV = [(-BAYW, 0.0), (-BAYF, BAYD), (BAYF, BAYD), (BAYW, 0.0)]
def bay_faces():
    out = []
    for a, b in zip(BAYV[:-1], BAYV[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L); n = (-u[1], u[0])
        out.append((a, u, n, L))
    return out
def bay_window_face(p, L, wy0, wy1, top, y0):
    """Uma face da bay em coordenadas locais (x ao longo da face, z para fora): almofada de tabuas, guilhotina e testeira."""
    q = Piece(); ww = min(0.8, L - 0.26); a = (L - ww) / 2; b = a + ww; f = 0.045
    q.box('frame', a, a + f, wy0, wy1, -0.1, -0.02); q.box('frame', b - f, b, wy0, wy1, -0.1, -0.02); q.box('frame', a + f, b - f, wy1 - f, wy1, -0.1, -0.02)
    q.box('frame', a + f, b - f, wy0, wy0 + 0.03, -0.1, -0.02)
    mid = (wy0 + 0.03 + wy1 - f) / 2
    sash(q, a + f, b - f, wy0 + 0.03, mid + 0.02, -0.09, -0.06, 1, 0.06)
    sash(q, a + f + 0.008, b - f - 0.008, mid - 0.02, wy1 - f, -0.055, -0.025, 1, 0.045)
    prof_x(q, 'trim', a - 0.05, b + 0.05, [(-BT + 0.005, wy0 - 0.03), (0.06, wy0 - 0.03), (0.07, wy0 - 0.02), (0.07, wy0), (-0.02, wy0 + 0.02), (-BT + 0.005, wy0 + 0.02)])
    q.box('trim', a, b, wy1, wy1 + 0.12, 0.0, 0.03)
    prof_x(q, 'trim', a - 0.03, b + 0.03, [(-0.01, wy1 + 0.12), (0.06, wy1 + 0.12), (0.06, wy1 + 0.14), (0.04, wy1 + 0.16), (-0.01, wy1 + 0.165)])
    configurar_tabuas(-SLAB, H, 0.2)
    siding_field(q, [(a - 0.02, b + 0.02, wy0 - 0.03, wy1 + 0.17)], x0=0.07, x1=L - 0.07, mat='siding')
    p_ = q
    # paineis rebaixados abaixo da janela
    ext_box = sbox(a + 0.03, y0 + 0.12, b - 0.03, wy0 - 0.08)
    if ext_box.area > 0.01: ext(q, 'trim', ext_box.difference(ext_box.buffer(-0.04, join_style=2)), -0.005, 0.04)
    return q
def bay_story(fl):
    """Um andar da bay (pivo: face da parede no eixo do modulo, cota do piso). Parede de 12 cm com colunetas torneadas nas
    quinas, 3 guilhotinas, piso por dentro e, no andar de cima, cornija com misulas que vira o teto da bay."""
    p = Piece(); top = H0 if fl == 0 else H - 0.45; wy0, wy1 = WIN0[1:] if fl == 0 else WIN1[1:]
    ring = BAYO.difference(BAYI)
    cuts = []
    for (a, u, n, L) in bay_faces():
        ww = min(0.8, L - 0.26); s0 = (L - ww) / 2; s1 = s0 + ww
        pa = (a[0] + u[0] * s0, a[1] + u[1] * s0); pb = (a[0] + u[0] * s1, a[1] + u[1] * s1)
        cuts.append(Polygon([(pa[0] + n[0] * 0.2, pa[1] + n[1] * 0.2), (pb[0] + n[0] * 0.2, pb[1] + n[1] * 0.2), (pb[0] - n[0] * 0.4, pb[1] - n[1] * 0.4), (pa[0] - n[0] * 0.4, pa[1] - n[1] * 0.4)]))
    yb = -0.03
    ext_y(p, 'siding', ring, yb, wy0); ext_y(p, 'siding', ring.difference(unary_union(cuts)), wy0, wy1); ext_y(p, 'siding', ring, wy1, top)
    if fl == 0:
        ext_y(p, 'floor', BAYI.union(sbox(-BAYW, -T, BAYW, 0.0)).difference(ring), -0.03, 0.0)
    else:
        ext_y(p, 'plaster', BAYO, -SLAB, -0.03); ext_y(p, 'floor', BAYI.union(sbox(-BAYW, -T, BAYW, 0.0)).difference(ring), -0.03, 0.0)
        ext_y(p, 'trim', BAYO.buffer(0.045, join_style=2).difference(BAYO).intersection(sbox(-1.0, 0.0, 1.0, 2.0)), -SLAB - 0.08, 0.0)
    for (a, u, n, L) in bay_faces():
        q = bay_window_face(p, L, wy0, wy1, top, yb); p.merge(q, frame_of(u, n, a))
    for v in BAYV:   # colunetas nas quinas
        x, z = v
        if abs(z) < 1e-6: x = x + (0.05 if x < 0 else -0.05); z = 0.05
        lathe(p, 'trim', [(0.06, yb + 0.004), (0.06, 0.12), (0.04, 0.16), (0.035, top - 0.2), (0.05, top - 0.15), (0.06, top - 0.005)], x, z, 0.0, 10)
    if fl == 1:
        F = unary_union([sbox(-W / 2, -T, W / 2, 0.0), BAYO])
        br = [(-0.8, 0.03, 0.0), (0.8, 0.03, 0.0)]
        for (a, u, n, L) in bay_faces():
            for t_ in (0.12, L - 0.12):
                br.append((a[0] + u[0] * t_ + n[0] * 0.03, a[1] + u[1] * t_ + n[1] * 0.03, math.atan2(n[0], n[1])))
        cornice(p, F, top=H, brackets=br)
        ext_y(p, 'plaster', BAYI.union(sbox(-BAYW, -T + 0.02, BAYW, 0.0)), top - 0.005, H - 0.45 + 0.0001) if False else None
    return p
def bay_base():
    """Porao da bay (pivo: face da parede, cota do piso): bloco chanfrado com almofadas, fundacao e mesa de agua."""
    p = Piece()
    ext_y(p, 'acc', BAYO, -RAISE, -0.03)
    clip = sbox(-1.2, 0.0, 1.2, 2.0)
    ext_y(p, 'plinth', BAYO.buffer(0.04, join_style=2).intersection(clip).difference(BAYO), -RAISE, -RAISE + 0.3)
    ext_y(p, 'trim', BAYO.buffer(0.03, join_style=2).intersection(clip).difference(BAYO), -RAISE + 0.3, -RAISE + 0.4)
    ext_y(p, 'trim', BAYO.buffer(0.04, join_style=2).intersection(clip).difference(BAYO), -0.24, -0.035)
    ext_y(p, 'trim', BAYO.buffer(0.085, join_style=2).intersection(clip).difference(BAYO), -0.035, 0.0)
    for (a, u, n, L) in bay_faces():
        q = Piece(); ring = sbox(0.1, -RAISE + 0.5, L - 0.1, -0.36).difference(sbox(0.16, -RAISE + 0.56, L - 0.16, -0.42))
        ext(q, 'trim', ring, -0.01, 0.035); p.merge(q, frame_of(u, n, a))
    return p

# ============================================================================ frontoes
def scale_field(p, poly, y0, mat='acc'):
    """Escamas de peixe: fiadas de 12 cm com a borda de baixo em meias-luas, alternando a profundidade para mostrar o recobrimento."""
    k = 0; y = y0; r = 0.075
    while y < poly.bounds[3]:
        off = (k % 2) * r
        discs = [Point(x, y + r).buffer(r, 3) for x in np.arange(-4.0 + off, 4.0, 2 * r)]
        band = unary_union([sbox(-4.0, y + r, 4.0, y + 0.12 + r + 0.035)] + discs).intersection(poly)
        z0 = 0.004 + 0.011 * (k % 2)
        ext(p, mat, band, z0, z0 + 0.011); y += 0.12; k += 1
def gable_front():
    """Frontao da rua (pivo: face da fachada no eixo da casa, cota do beiral): miolo, faixa, escamas, par de janelas em arco,
    tesoura com fusos e raios, lambrequim recortado e pinaculo."""
    p = Piece(); A = RIDGE - 0.02
    core = Polygon([(-HX, 0.0), (HX, 0.0), (0.0, A)])
    wx = 0.42; ww = 0.5; ws, wsp, wr = 0.55, 1.45, 0.25
    ops = [opening(ww, ws, wsp, wr, s * wx) for s in (-1, 1)]
    ext(p, 'siding', core.difference(unary_union(ops)), -T, 0.0)
    ext(p, 'trim', core.intersection(sbox(-HX, 0.0, HX, 0.16)), -0.01, 0.045)
    inner = core.buffer(-0.06, join_style=2)
    surr = [o.buffer(0.09, join_style=2) for o in ops]
    scale_field(p, inner.difference(sbox(-HX, -1, HX, 0.16)).difference(unary_union(surr)), 0.16)
    for o, s in zip(ops, (-1, 1)):
        xc = s * wx
        ext(p, 'trim', o.buffer(0.09, join_style=2).difference(o), 0.0, 0.045)
        ext(p, 'frame', o.difference(o.buffer(-0.05, join_style=2)), -0.14, -0.04)
        ext(p, 'glass', o.buffer(-0.05, join_style=2), -0.093, -0.087)
        p.box('frame', xc - 0.012, xc + 0.012, ws + 0.05, wsp + wr - 0.05, -0.1, -0.08); p.box('frame', xc - 0.2, xc + 0.2, ws + 0.62, ws + 0.645, -0.1, -0.08)
        ext(p, 'dark', o, -T + 0.01, -T + 0.02)
        prof_x(p, 'trim', xc - ww / 2 - 0.12, xc + ww / 2 + 0.12, [(0.0, ws - 0.08), (0.07, ws - 0.08), (0.08, ws - 0.065), (0.08, ws - 0.035), (0.06, ws - 0.02), (0.0, ws)])
        p.cham('trim', xc - 0.045, xc + 0.045, wsp + wr + 0.04, wsp + wr + 0.17, 0.0, 0.07, 0.008)
    # tesoura decorativa sob o avanco do telhado
    zt = 0.3; yc = 2.35; xe = (RIDGE - yc) / KR
    p.cham('trim', -xe + 0.05, xe - 0.05, yc - 0.06, yc + 0.03, zt, zt + 0.08, 0.008)
    for x in np.arange(-xe + 0.12, xe - 0.08, 0.09): lathe(p, 'trim', [(0.014, yc - 0.33), (0.022, yc - 0.27), (0.012, yc - 0.18), (0.02, yc - 0.1), (0.012, yc - 0.06)], x, zt + 0.04, 0.0, 6)
    p.box('trim', -0.05, 0.05, yc + 0.02, A - 0.02, zt, zt + 0.08)
    lathe(p, 'acc', [(0.0, yc + 0.03), (0.12, yc + 0.06), (0.12, yc + 0.1), (0.0, yc + 0.13)], 0.0, zt + 0.1, 0.0, 12) if False else None
    for k in range(1, 8):
        a = math.pi * k / 8; c, s = math.cos(a), math.sin(a)
        Ln = 0.95
        while Ln > 0.2 and (yc + 0.03 + s * Ln * 0.9) > (HX - abs(c * Ln)) * KR - 0.07: Ln -= 0.02
        seg_cyl(p, 'trim', (0.0, yc + 0.03, zt + 0.04), (c * Ln, yc + 0.03 + s * Ln * 0.9, zt + 0.04), 0.013, 6)
    hub = Point(0, yc + 0.03).buffer(0.16, 16).intersection(sbox(-1, yc + 0.025, 1, yc + 0.3)); ext(p, 'acc', hub, zt - 0.005, zt + 0.085)
    # lambrequim recortado ao longo das empenas (atras da testeira do telhado)
    zb = OVF - 0.07
    for s in (-1, 1):
        x0, x1 = s * (HX - 0.02), 0.0
        top = lambda x: (HX - abs(x)) * KR - 0.005
        pts = [(x0, top(x0)), (x1, top(x1)), (x1, top(x1) - 0.26), (x0, top(x0) - 0.26)]
        board = Polygon(pts)
        holes = []
        L = math.hypot(x1 - x0, top(x1) - top(x0)); n = int(L / 0.22)
        for i in range(n):
            t_ = (i + 0.5) / n; xx = x0 + (x1 - x0) * t_; yy = top(xx) - 0.26
            holes.append(Point(xx, yy).buffer(0.08, 4)); holes.append(Point(xx, yy + 0.15).buffer(0.025, 2))
        ext(p, 'trim', board.difference(unary_union(holes)), zb, zb + 0.04)
    # pinaculo
    lathe(p, 'trim', [(0.07, A - 0.25), (0.07, A + 0.2), (0.09, A + 0.24), (0.05, A + 0.3), (0.06, A + 0.4), (0.03, A + 0.5)], 0.0, OVF - 0.05, 0.0, 10)
    p.sphere('trim', 0.06, 0.0, A + 0.55, OVF - 0.05, 1); seg_cyl(p, 'iron', (0.0, A + 0.6, OVF - 0.05), (0.0, A + 0.95, OVF - 0.05), 0.012, 6)
    return p
def gable_back():
    """Frontao dos fundos (pivo: face da parede no eixo, cota do beiral, girado 180): tabuas e veneziana redonda."""
    p = Piece(); A = RIDGE - 0.02; core = Polygon([(-HX, 0.0), (HX, 0.0), (0.0, A)])
    ext(p, 'siding', core, -T, 0.0)
    vy = 1.6; vent = Point(0, vy).buffer(0.3, 24)
    configurar_tabuas(0.0, 4.0, 0.2)
    inner = core.buffer(-0.03, join_style=2)
    for k in range(int(A / 0.2) + 1):
        b0 = k * 0.2; b1 = b0 + 0.2 + D.LAP
        g = inner.intersection(sbox(-4, b0, 4, b1)).difference(vent.buffer(0.08))
        for gg in getattr(g, 'geoms', [g]):
            if gg.geom_type != 'Polygon' or gg.area < 1e-5: continue
            th = lambda y: D.TB - (D.TB - D.TT) * (y - b0) / (b1 - b0)
            pts = list(gg.exterior.coords)[:-1]
            p.hull('siding', [(px, py, 0.0) for px, py in pts] + [(px, py, th(py)) for px, py in pts])
    ext(p, 'trim', vent.buffer(0.08).difference(vent), -0.01, 0.045); ext(p, 'dark', vent, -0.01, 0.005)
    for i in range(7):
        yy = vy - 0.24 + i * 0.08; w_ = math.sqrt(max(0.0, 0.3 ** 2 - (yy - vy) ** 2))
        if w_ > 0.03: p.hull('trim', [(x, y, z) for x in (-w_, w_) for (y, z) in ((yy, 0.005), (yy + 0.012, 0.005), (yy - 0.03, 0.05), (yy - 0.018, 0.05))])
    return p

# ============================================================================ telhado: fiadas a 50 graus, cumeeira ao longo de Z
def roof_strip(x0=-W / 2, x1=W / 2, rake=0, over=0.0):
    """Faixa de 2 m de uma agua (pivo: plano da parede lateral ou da parede-meia, cota do beiral; o beiral fica em z = over e a
    agua sobe para -Z ate a cumeeira em z = -SX). over = 0 nas paredes-meias (vale com rufo) e OVE nas pontas da fileira (testeira
    e calha). rake = -1/+1: ponta de frontao (testeira inclinada) do lado x0/x1."""
    p = Piece(); f = lambda a, b: -KR * b
    poly = sbox(x0, -SX, x1, over)
    sheared(p, 'plaster', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: over - b, lambda d0, d1: sbox(-50, over - d1, 50, over - d0), over + SX + 0.01,
                    lambda v, n: np.stack([v[:, 0] / TILE, (over - v[:, 2]) / CS / TILE], 1))
    if over > 0:
        yb = -KR * over
        a = x0 + (-0.03 if rake < 0 else 0.001); b = x1 + (0.03 if rake > 0 else -0.001)
        prof_x(p, 'trim', a, b, crect(over - 0.02, over + 0.03, yb - 0.15, yb + 0.05, 0.006, (0, 1, 1, 0)))
        gutter_run(p, x0 - (0.03 if rake < 0 else 0), x1 + (0.03 if rake > 0 else 0), over + 0.03, yb + 0.02, caps=(rake < 0, rake > 0))
        for xx in (-0.75, -0.25, 0.25, 0.75):
            if x0 + 0.05 < xx < x1 - 0.05: p.hull('trim', [(xx + dx, -KR * z + dy, z) for dx in (-0.025, 0.025) for z in (0.01, over - 0.022) for dy in (0.0, -0.12)])
    if rake:
        xr = x0 if rake < 0 else x1; xa, xb = sorted((xr, xr + rake * 0.04))
        z0 = over + (0.03 if over > 0 else 0.0)
        tp = lambda z: -KR * z + TV + BUMP + 0.03
        prof_x(p, 'trim', xa, xb, [(z0, tp(z0)), (-SX, tp(-SX)), (-SX, KR * SX - 0.16), (z0, -KR * z0 - 0.16)])
        xa, xb = sorted((xr - rake * 0.06, xr + rake * 0.04))
        prof_x(p, 'trim', xa, xb, [(-SX, KR * SX - 0.16), (z0, -KR * z0 - 0.16), (z0, -KR * z0 - 0.22), (-SX, KR * SX - 0.22)])
    return p
def ridge_cap(z0, z1):
    p = Piece(); y = TV + BUMP + RIDGE; d = 0.16
    p.hull('ridge', [(x, yy, z) for z in (z0, z1) for (yy, x) in ((y - d * KR - 0.04, d), (y - d * KR - 0.04, -d), (y + 0.075, 0.0), (y + 0.06, 0.06), (y + 0.06, -0.06), (y - 0.12, 0.0))])
    return p
def valley(z0, z1):
    """Rufo de chapa no vale entre duas casas (pivo: plano da parede-meia, cota do beiral): 2 abas sobre as fiadas e canaleta."""
    p = Piece(); y = TV + BUMP
    for s in (-1, 1):
        a, b = sorted((0.0, s * 0.32))
        p.hull('flash', [(x, KR * abs(x) + y + dy, z) for x in (a, b) for z in (z0, z1) for dy in (0.004, 0.012)])
    p.hull('flash', [(x, yy, z) for x in (-0.06, 0.06) for z in (z0, z1) for yy in (y - 0.02, y + 0.012)])
    return p

# ============================================================================ escada de entrada (stoop)
def stoop(w=0.75, landing=1.2, n=10, rail_newel=True, lamps=True):
    """Escada de entrada (pivo: face da fachada, eixo da porta, cota do piso; desce para +Z ate o chao): patamar e degraus de
    madeira sobre um corpo pintado com almofadas, longarinas, balaustres, corrimao e postes torneados com globo."""
    p = Piece(); r = RAISE / n; run = 0.28; z1 = landing + (n - 1) * run
    prof = [(0.002, -RAISE), (0.002, -0.04)] + [(landing + i * run, -0.04 - i * r) for i in range(0, n) for _ in (0,)][:1]
    pts = [(0.002, -RAISE), (0.002, -0.035), (landing, -0.035)]
    for i in range(1, n):
        pts += [(landing + (i - 1) * run, -i * r - 0.035), (landing + i * run, -i * r - 0.035)]
    pts += [(z1, -RAISE)]
    clean = []
    for q in pts:
        if not clean or (abs(clean[-1][0] - q[0]) > 1e-6 or abs(clean[-1][1] - q[1]) > 1e-6): clean.append(q)
    body = Polygon(clean).buffer(0)
    q = Piece()
    for g in getattr(body, 'geoms', [body]):
        m = trimesh.creation.extrude_polygon(g, 2 * w - 0.08); v = m.vertices.copy()
        m.vertices = np.stack([v[:, 2] - (w - 0.04), v[:, 1], v[:, 0]], 1); m.invert(); p.add('trim', D._fix(m))
    p.box('deck', -w, w, -0.035, 0.0, 0.002, landing + 0.03)
    for i in range(1, n):
        y = -i * r; za = landing + (i - 1) * run
        p.box('deck', -w, w, y - 0.035, y, za, za + run + 0.03)
        p.box('trim', -w + 0.03, w - 0.03, y, y + r - 0.035, za - 0.006, za + 0.004) if False else None
    # longarinas laterais e almofadas
    for s in (-1, 1):
        xa, xb = sorted((s * (w - 0.045), s * (w + 0.01)))
        top_ = lambda z: -0.035 - max(0.0, (z - landing) / run) * r - 0.04 if z > landing else -0.075
        p.hull('trim', [(x, y, z) for x in (xa, xb) for (z, y) in ((0.002, -0.3), (0.002, -0.075), (landing, -0.075), (landing, -0.3))])
        p.hull('trim', [(x, y, z) for x in (xa, xb) for (z, y) in ((landing, -0.075), (landing, -0.3), (z1, -RAISE + 0.1), (z1, -RAISE + 0.25 + r))])
        xp, xq = sorted((s * (w - 0.045), s * (w + 0.002)))
        for (za, zb_, ya, yb) in ((0.15, 0.55, -RAISE + 0.2, -0.45), (0.65, 1.05, -RAISE + 0.2, -0.45), (1.3, 1.9, -RAISE + 0.2, -0.75), (2.0, 2.6, -RAISE + 0.2, -1.1)):
            p.box('acc', xp, xq, ya + 0.005, yb - 0.005, za + 0.005, zb_ - 0.005)
            for (a, b, c, d) in ((ya, ya + 0.04, za, zb_), (yb - 0.04, yb, za, zb_), (ya, yb, za, za + 0.04), (ya, yb, zb_ - 0.04, zb_)):
                xr0, xr1 = sorted((s * (w - 0.045), s * (w + 0.012))); p.box('trim', xr0, xr1, a, b, c, d)
    # guarda-corpos
    hr = lambda z: 0.92 if z <= landing else 0.92 - (z - landing) / run * r
    zn = z1 - 0.12
    for s in (-1, 1):
        xr = s * (w - 0.06)
        seg_cyl(p, 'trim', (xr, 0.92, 0.06), (xr, 0.92, landing), 0.03, 8)
        seg_cyl(p, 'trim', (xr, 0.92, landing), (xr, hr(zn - 0.1), zn - 0.1), 0.03, 8)
        for z in list(np.arange(0.14, landing - 0.05, 0.13)) + list(np.arange(landing + 0.07, zn - 0.15, 0.14)):
            yb = 0.0 if z <= landing else -(math.floor((z - landing) / run) + 1) * r
            yt = hr(z) - 0.02
            p.cham('trim', xr - 0.018, xr + 0.018, yb, yb + 0.12, z - 0.018, z + 0.018, 0.004)
            lathe(p, 'trim', [(0.014, yb + 0.12), (0.024, yb + 0.25), (0.012, yb + 0.4), (0.012, yt - 0.12), (0.02, yt - 0.06), (0.012, yt)], xr, z, 0.0, 6)
        p.cham('trim', xr - 0.07, xr + 0.07, 0.0, 1.05, 0.0 + 0.003, 0.14, 0.01) if False else p.cham('trim', xr - 0.07, xr + 0.07, 0.0, 1.05, landing - 0.07, landing + 0.07, 0.01)
        yl = -(n - 1) * r
        p.cham('trim', xr - 0.1, xr + 0.1, yl, yl + 0.25, zn - 0.1, zn + 0.1, 0.012)
        p.cham('trim', xr - 0.08, xr + 0.08, yl + 0.25, yl + 1.05, zn - 0.08, zn + 0.08, 0.01)
        p.cham('trim', xr - 0.1, xr + 0.1, yl + 1.05, yl + 1.12, zn - 0.1, zn + 0.1, 0.01)
        if lamps:
            p.cyl('iron', 0.04, yl + 1.12, yl + 1.2, xr, zn, 10); p.sphere('lamp_glass', 0.13, xr, yl + 1.33, zn, 1)
        else:
            p.sphere('trim', 0.07, xr, yl + 1.18, zn, 1)
    return p

# ============================================================================ interior
def party_wall(fl):
    """Parede-meia entre duas casas (pivo: eixo, cota do piso, ao longo de X local de face a face das paredes da frente e dos fundos),
    gesso dos 2 lados e rodape."""
    p = Piece(); y0 = -RAISE if fl == 0 else -SLAB; top = H0 if fl == 0 else H; L = HZ - T
    p.box('plaster', -L, L, y0 + 0.003, top, -PT, PT)
    baseboard(p, -L, L, 2 * PT)
    return p
def interior_wall(doorway, h, ow=0.9, end=False):
    p = Piece(); t = 0.14; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2] + ([-ow / 2, ow / 2] if doorway else []) + [x1]; ys = [0.0, 2.1, h] if doorway else [0.0, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (doorway and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    if doorway:
        door_casing(p, ow, t)
        for a, b in ((-W / 2, -ow / 2 - 0.09), (ow / 2 + 0.09, x1)): baseboard(p, a, b, t)
    else: baseboard(p, -W / 2, x1, t)
    return p
XW = 1.0; XWF = XW - 0.07                       # parede do hall (eixo) e sua face do lado das salas
def cross_wall(h, dx=1.0, ow=0.9):
    """Parede entre os quartos do 1o andar (pivo: face da parede-meia, eixo da parede, cota do piso), de x = 0 ate a face
    da parede do hall, com porta centrada em dx (medido da face da parede-meia, 0 = x local -HX + PT)."""
    p = Piece(); t = 0.14; L = (XWF) - (-HX + PT); c = dx
    xs = [0.0, c - ow / 2, c + ow / 2, L]; ys = [0.0, 2.1, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    q = Piece(); door_casing(q, ow, t); p.merge(q, trimesh.transformations.translation_matrix([c, 0, 0]))
    for a, b in ((0.0, c - ow / 2 - 0.09), (c + ow / 2 + 0.09, L - 0.017)): baseboard(p, a, b, t)
    return p
def floor_tile(kind, lv, rect=(-1, 1, -1, 1), holes=(), trim=(0, 0, 0, 0)):
    """Piso de 2 x 2 m: tacos, xadrez (hall), ladrilho (cozinha) ou forro do sotao. lv 'g' = terreo (corpo ate o chao do
    porao), 'u' = andar, 'c' = forro do 2o andar (tabuas do sotao em cima). trim = recuo em metros de cada lado (x-, x+, z-, z+)."""
    p = Piece(); x0, x1, z0, z1 = rect[0] + trim[0], rect[1] - trim[1], rect[2] + trim[2], rect[3] - trim[3]
    sq = sbox(x0, z0, x1, z1)
    for (a, b, c, d) in holes: sq = sq.difference(sbox(a, b, c, d))
    if kind in ('hall', 'tile'):
        s = 0.4 if kind == 'hall' else 0.25; n = int(round(2 / s)); ma, mb = ('marble', 'slate') if kind == 'hall' else ('tile', 'slate')
        for i in range(n):
            for j in range(n):
                q = sbox(rect[0] + i * s, rect[2] + j * s, rect[0] + (i + 1) * s, rect[2] + (j + 1) * s).intersection(sq)
                ext_y(p, ma if (i + j) % 2 == 0 else mb, q, -0.03, 0.0)
    else: ext_y(p, 'attic' if lv == 'c' else 'floor', sq, -0.03, 0.0)
    if lv == 'g':
        ext_y(p, 'plinth', sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0)), -RAISE + 0.02, -0.03)
    else:
        sqi = sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0))
        for (a, b, c, d) in holes: sqi = sqi.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
        ext_y(p, 'plaster', sqi, -SLAB - 0.005, -0.03)
    return p
def stair():
    """Lance reto de madeira (pivo: canto do primeiro degrau, cota do piso; sobe para -Z local): pisos com bocel, espelhos,
    banzos, corrimao com balaustres torneados no lado aberto (x = w) e pilarete no pe."""
    p = Piece(); w = SW_
    for i in range(NR - 1):
        y = (i + 1) * RS_; z0 = -i * TR
        p.box('floor', 0.0, w, y - 0.035, y, z0 - TR, z0 + 0.03)
        p.box('trim', 0.0, w, y - RS_ - 0.002 if i else 0.0, y - 0.035, z0 - 0.02, z0)
    p.box('trim', 0.0, w, H - RS_ - 0.002, H - 0.035, -RUN - 0.02, -RUN)
    for (a, b) in ((w + 0.002, w + 0.05), (-0.03, -0.002)):
        p.hull('trim', [(x, y, z) for x in (a, b) for (z, y) in ((0.03, 0.0), (0.28, 0.0), (-RUN + 0.02, H - RS_ - 0.25), (-RUN + 0.02, H + 0.08), (0.03, RS_ + 0.08))])
    k = RS_ / TR; hr = lambda z: 0.9 + k * (-z)
    xr = w + 0.025
    seg_cyl(p, 'deck', (xr, hr(0.0) + 0.05, 0.0), (xr, hr(-RUN) + 0.05, -RUN), 0.03, 10)
    for i in range(NR - 1):
        for dz in (0.25, 0.75):
            z = -i * TR - TR * dz; y = (i + 1) * RS_
            lathe(p, 'trim', [(0.014, y), (0.022, y + 0.1), (0.012, y + 0.25), (0.012, hr(z) - 0.1), (0.018, hr(z) - 0.05), (0.012, hr(z) + 0.03)], xr, z, 0.0, 6)
    p.cham('deck', xr - 0.07, xr + 0.07, 0.0, 1.0, -0.1, 0.04, 0.01); lathe(p, 'deck', [(0.06, 1.0), (0.07, 1.06), (0.04, 1.12), (0.0, 1.16)], xr, -0.03, 0.0, 12)
    # armario embaixo da escada: parede almofadada no lado aberto e parede no fim, para ninguem entrar no vao baixo
    ly = lambda z: (0.28 - z) / (0.28 + RUN - 0.02) * (H - RS_ - 0.25) - 0.05
    za = -1.2
    p.hull('plaster', [(x, y, z) for x in (w - 0.07, w - 0.03) for (z, y) in ((za, 0.0), (-RUN + 0.08, 0.0), (-RUN + 0.08, ly(-RUN + 0.08)), (za, ly(za)))])
    p.box('plaster', 0.004, w - 0.07, 0.0, H - RS_ - 0.32, -RUN + 0.02, -RUN + 0.08)
    for (z0, z1) in ((za + 0.1, -2.2), (-2.35, -3.4)):
        ya = 0.18; yb = ly(z0) - 0.12
        if yb - ya > 0.3: p.hull('trim', [(x, y, z) for x in (w - 0.03, w - 0.02) for (z, y) in ((z0, ya), (z1, ya), (z1, ly(z1) - 0.12), (z0, yb))])
    return p
def rail(Ln, posts=(True, True)):
    p = Piece()
    p.box('trim', 0.0, Ln, 0.003, 0.08, -0.03, 0.03); p.box('deck', 0.0, Ln, 0.92, 0.98, -0.04, 0.04)
    n = int(Ln / 0.11)
    for i in range(1, n):
        x = i * Ln / n; lathe(p, 'trim', [(0.014, 0.08), (0.022, 0.2), (0.012, 0.35), (0.012, 0.82), (0.018, 0.87), (0.012, 0.92)], x, 0.0, 0.0, 6)
    for x, ok in zip((0.0, Ln), posts):
        if ok: p.cham('deck', x - 0.045, x + 0.045, 0.0015, 1.06, -0.045, 0.045, 0.008)
    return p

# ============================================================================ rua
def sidewalk():
    """Modulo de calcada de 2 x 2,2 m (pivo: eixo, borda do jardim, no chao) com meio-fio de pedra."""
    p = Piece(); z0, z1 = 0.0, 2.2
    ext_y(p, 'concrete', sbox(-1.0, z0, 1.0, z1 - 0.2), 0.0, 0.12)
    p.box('plinth', -1.0, 1.0, -0.05, 0.15, z1 - 0.2, z1)
    p.box('dark', -1.0, -0.996, 0.118, 0.1205, z0, z1 - 0.2) if False else None
    for zz in (z0 + 1.0,): ext_y(p, 'dark', sbox(-0.998, zz - 0.004, 0.998, zz + 0.004), 0.12, 0.122)
    return p
def lawn():
    p = Piece(); ext_y(p, 'grass', sbox(-HX, 0.0, HX, 4.2), 0.002, 0.03); return p
def fence(post=True):
    """Gradil de ferro de 2 m sobre mureta (pivo: inicio do modulo em x = -1, no topo da calcada): lancas, 2 travessas e poste."""
    p = Piece()
    if post is not True:
        p.box('plinth', -0.12, 0.12, 0.0, 0.3, -0.12, 0.12); p.cham('iron', -0.05, 0.05, 0.3, 1.15, -0.05, 0.05, 0.01)
        p.sphere('iron', 0.06, 0.0, 1.2, 0.0, 1); return p
    p.box('plinth', -0.92, 0.92, 0.0, 0.22, -0.09, 0.09)
    p.cham('plinth', -1.12, -0.88, 0.0, 0.3, -0.12, 0.12, 0.01); p.cham('iron', -1.05, -0.95, 0.3, 1.15, -0.05, 0.05, 0.01); p.sphere('iron', 0.06, -1.0, 1.2, 0.0, 1)
    for yy in (0.32, 0.95): p.box('iron', -0.95, 0.95, yy, yy + 0.025, -0.012, 0.012)
    for x in np.arange(-0.86, 0.9, 0.12):
        p.box('iron', x - 0.008, x + 0.008, 0.22, 1.02, -0.008, 0.008)
        p.hull('iron', [(x + dx, 1.02, dz) for dx in (-0.02, 0.02) for dz in (-0.012, 0.012)] + [(x, 1.1, 0.0)])
    return p
def globe_lamp():
    p = Piece()
    lathe(p, 'iron', [(0.14, 0.0), (0.14, 0.05), (0.1, 0.1), (0.07, 0.25), (0.05, 0.35)], sec=12)
    p.cyl('iron', 0.04, 0.35, 3.2, 0.0, 0.0, 10)
    for yy in (0.6, 1.4, 2.9): p.cyl('iron', 0.055, yy, yy + 0.05, 0.0, 0.0, 10)
    p.hull('iron', [(0.12 * math.cos(a), 3.2, 0.12 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)] + [(0, 3.15, 0)])
    p.box('lamp_glass', -0.1, 0.1, 3.25, 3.6, -0.1, 0.1)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('iron', sx * 0.11 - 0.01, sx * 0.11 + 0.01, 3.22, 3.62, sz * 0.11 - 0.01, sz * 0.11 + 0.01)
    p.box('iron', -0.13, 0.13, 3.2, 3.25, -0.13, 0.13)
    p.hull('iron', [(sx * 0.16, 3.62, sz * 0.16) for sx in (-1, 1) for sz in (-1, 1)] + [(0, 3.85, 0)]); p.sphere('iron', 0.04, 0, 3.88, 0, 1)
    return p
def corner(fl):
    """Quina externa das casas das pontas (pivo: quina externa, cota do piso; paredes em -X e -Z): cantoneiras de tabua,
    nucleo, porao com fundacao e mesa de agua."""
    p = Piece(); e = 0.05; y0 = -RAISE if fl == 0 else -SLAB; top = H0 if fl == 0 else H
    p.box('trim', -T + 0.004, 0.004, y0 + 0.003, top - 0.004, -T + 0.004, 0.004)
    ya = 0.0 if fl == 0 else y0 + 0.003; yb = top - (0.45 if fl == 1 else 0.004)
    prof_y(p, 'trim', ya, yb, [(-0.16, -0.01), (e, -0.01), (e, e), (-0.01, e), (-0.01, -0.16), (-0.16, -0.16)][::1] if False else
           [(-0.17, -0.005), (e, -0.005), (e, e - 0.006), (e - 0.006, e), (-0.005, e), (-0.005, -0.17), (-0.17, -0.17)])
    if fl == 0:
        p.box('acc', -0.19, 0.045, -RAISE + 0.2, -0.24, -0.19, 0.045)
        p.box('plinth', -0.22, 0.05, -RAISE + 0.004, -RAISE + 0.32, -0.22, 0.05)
        p.box('trim', -0.2, 0.045, -0.24, 0.0, -0.2, 0.045); p.box('trim', -0.21, 0.09, -0.035, 0.012, -0.21, 0.09)
    if fl == 1: p.box('trim', -0.2, 0.06, top - 0.45, top - 0.004, -0.2, 0.06)
    return p
def pilaster(fl):
    """Pilastra de tabua que cobre a divisa entre 2 casas na fachada (pivo: divisa, face da fachada, cota do piso)."""
    p = Piece(); top = H0 if fl == 0 else H - 0.45; ya = 0.012 if fl == 0 else -SLAB
    prof_y(p, 'trim', ya, top, crect(-0.15, 0.15, -0.01, 0.05, 0.008, (0, 0, 1, 1)))
    ext(p, 'acc', sbox(-0.09, ya + 0.3 if fl == 0 else ya + 0.2, 0.09, top - 0.25), 0.05, 0.056)
    if fl == 0:
        p.box('acc', -0.15, 0.15, -RAISE + 0.004, -0.24, -0.01, 0.05)
        prof_y(p, 'trim', -0.24, -0.035, crect(-0.16, 0.16, -0.01, 0.06, 0.006, (0, 0, 1, 1)))
    if fl == 1:
        p.cham('trim', -0.17, 0.17, top - 0.12, top, -0.01, 0.07, 0.008)
    return p
def downspout_piece():
    return downspout(YE + 0.02 - KR * OVE, OVE + 0.03 + 0.065)

# ============================================================================ pecas
pieces = {}
for c in HUES:
    for fl, nm in ((0, 'g'), (1, 'u')):
        for k in ('win', 'plain', 'bay', 'door'):
            if k == 'door' and fl == 1: continue
            pieces[f'f_{nm}_{k}_{c}'] = recolor(f_wall(k, fl), c)
        pieces[f'b_{nm}_win_{c}'] = recolor(f_wall('win', fl, back=True), c)
    pieces[f'b_g_door_{c}'] = recolor(f_wall('door', 0, back=True), c)
    pieces[f'bay_base_{c}'] = recolor(bay_base(), c); pieces[f'bay_g_{c}'] = recolor(bay_story(0), c); pieces[f'bay_u_{c}'] = recolor(bay_story(1), c)
    pieces[f'gable_front_{c}'] = recolor(gable_front(), c); pieces[f'gable_back_{c}'] = recolor(gable_back(), c)
    pieces[f'door_leaf_front_{c}'] = recolor(door_victorian(), c)
    pieces[f'pilaster_g_{c}'] = recolor(pilaster(0), c); pieces[f'pilaster_u_{c}'] = recolor(pilaster(1), c)
    pieces[f'corner_g_{c}'] = recolor(corner(0), c); pieces[f'corner_u_{c}'] = recolor(corner(1), c)
    pieces[f'cornice_{c}'] = recolor(cornice_flat(), c); pieces[f'stoop_{c}'] = recolor(stoop(), c); pieces[f'back_stoop_{c}'] = recolor(stoop(0.6, 0.9, 10, lamps=False), c)
pieces.update({
    'roof_valley': roof_strip(), 'roof_valley_a': roof_strip(x0=-W / 2 - OVF, rake=-1), 'roof_valley_b': roof_strip(x1=W / 2 + OVF, rake=1),
    'roof_eave': roof_strip(over=OVE), 'roof_eave_a': roof_strip(x0=-W / 2 - OVF, rake=-1, over=OVE), 'roof_eave_b': roof_strip(x1=W / 2 + OVF, rake=1, over=OVE),
    'ridge': ridge_cap(-HZ - OVF - 0.02, HZ + OVF + 0.02), 'valley': valley(-HZ - OVF, HZ + OVF), 'downspout': downspout_piece(),
    'party_g': party_wall(0), 'party_u': party_wall(1),
    'iw_plain': interior_wall(False, H0 - 0.005), 'iw_doorway': interior_wall(True, H0 - 0.005), 'iw_end_plain': interior_wall(False, H0 - 0.005, end=True),
    'iw_end_doorway': interior_wall(True, H0 - 0.005, end=True), 'iw_cross': cross_wall(H0 - 0.005),
    'stair': stair(), 'door_leaf_back': door_back_leaf(), 'door_leaf_interior': door_interior(),
    'sidewalk': sidewalk(), 'lawn': lawn(), 'fence': fence(), 'fence_post': fence('post'), 'street_lamp': globe_lamp(), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
def ftag(fl): return f'floor{fl}'
TILE_N = {}
def tile_piece(kind, lv, holes, trim):
    key = (kind, lv, tuple(holes), trim)
    if key not in TILE_N:
        nm = f'floor_{kind}_{lv}' + ('_e' + '_'.join(str(int(round(t * 100))) for t in trim) if any(trim) else ''); base = nm; i = 2
        while nm in pieces: nm = f'{base}_h{i}'; i += 1
        pieces[nm] = floor_tile(kind, lv, (-1, 1, -1, 1), holes, trim); TILE_N[key] = nm
    return TILE_N[key]
ZM = [-5, -3, -1, 1, 3, 5]
HOLE1 = (XW + 0.07, SZ0 + 1.3, HX - PT, SZ1)     # vao da escada no 1o andar (coordenadas da casa)
for i, xc in enumerate(XC):
    c = HUES[i]; ht = f'house{i + 1}'
    # fachada
    for fl, nm in ((0, 'g'), (1, 'u')):
        kinds = {-2: 'bay', 0: 'win', 2: 'door' if fl == 0 else 'win'}
        for dx, k in kinds.items(): put(f'f_{nm}_{k}_{c}', xc + dx, lvl(fl), HZ, 0, ['front', 'ext', ht, ftag(fl)])
        for dx, k in ((-2, 'win'), (0, 'door' if fl == 0 else 'win'), (2, 'win')): put(f'b_{nm}_{k}_{c}', xc + dx, lvl(fl), -HZ, 180, ['back', 'ext', ht, ftag(fl)])
    put(f'bay_base_{c}', xc - 2, Y0, HZ, 0, ['front', 'ext', ht]); put(f'bay_g_{c}', xc - 2, lvl(0), HZ, 0, ['front', 'ext', ht, ftag(0)])
    put(f'bay_u_{c}', xc - 2, lvl(1), HZ, 0, ['front', 'ext', ht, ftag(1)])
    for dx in (0, 2): put(f'cornice_{c}', xc + dx, lvl(1), HZ, 0, ['front', 'ext', ht])
    put(f'gable_front_{c}', xc, YE, HZ, 0, ['front', 'roof', ht]); put(f'gable_back_{c}', xc, YE, -HZ, 180, ['back', 'roof', ht])
    if i < NH - 1:
        for fl, nm in ((0, 'g'), (1, 'u')): put(f'pilaster_{nm}_{c}', xc + HX, lvl(fl), HZ, 0, ['front', 'ext', ht])
    put(f'stoop_{c}', xc + 2, Y0, HZ, 0, ['front', 'ext', ht]); put(f'back_stoop_{c}', xc, Y0, -HZ, 180, ['back', 'ext', ht])
    hx, hz = hinge(xc + 2, HZ, 0, -0.46, -0.16); put(f'door_leaf_front_{c}', hx, Y0 + 0.013, hz, 0, ['front', 'ext', ht, ftag(0)], door=85)
    hx, hz = hinge(xc, -HZ, 180, -0.43, -0.16); put('door_leaf_back', hx, Y0 + 0.013, hz, 180, ['back', 'ext', ht, ftag(0)], door=-85)
    # telhado
    for (side, ry) in ((1, 90), (-1, -90)):
        outer = (i == 0 and side < 0) or (i == NH - 1 and side > 0)
        base = 'roof_eave' if outer else 'roof_valley'
        for z in ZM:
            if z == 5: nm = base + ('_a' if side > 0 else '_b')
            elif z == -5: nm = base + ('_b' if side > 0 else '_a')
            else: nm = base
            put(nm, xc + side * HX, YE, z, ry, ['roof', ht])
    put('ridge', xc, YE, 0.0, 0, ['roof', ht])
    if i < NH - 1: put('valley', xc + HX, YE, 0.0, 0, ['roof'])
    # jardim e calcada
    put('lawn', xc, 0.0, HZ, 0, ['street', ht])
    for dx in (-2, 0, 2):
        put('sidewalk', xc + dx, 0.0, HZ + 4.2, 0, ['street'])
        if dx != 2: put('fence', xc + dx, 0.12, HZ + 4.3, 0, ['street', ht])
    put('fence_post', xc + 1, 0.12, HZ + 4.3, 0, ['street', ht])
    # interior
    for fl in (0, 1):
        y = lvl(fl)
        for z in ZM:
            end = abs(z) == 5
            if fl == 0: d = z in (5, -5)
            else: d = z == 3
            ry = (90 if z == -5 else -90) if end else 90
            put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), xc + XW, y, z, ry, [ht, ftag(fl)])
            if d:
                hx, hz = hinge(xc + XW, z, 90, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, 90, [ht, ftag(fl)], door=90)
    put('iw_cross', xc - HX + PT, lvl(1), -1.0, 0, [ht, ftag(1)])
    hx, hz = hinge(xc - HX + PT + 1.0, -1.0, 0, -0.43, 0); put('door_leaf_interior', hx, lvl(1) + 0.01, hz, 0, [ht, ftag(1)], door=-90)
    put('stair', xc + HX - PT - 0.05, lvl(0), SZ0, 180, [ht, ftag(0)])
    for nm, x0, z0, x1, z1 in (('rail_a', XW + 0.07, SZ1, XW + 0.07 + 0.55, SZ1), ('rail_b', XW + 0.07, HOLE1[1], HX - PT, HOLE1[1])):
        Lr = round(x1 - x0, 3); rn = f'rail_{int(round(Lr * 100))}'
        if rn not in pieces: pieces[rn] = rail(Lr, (False, True) if nm == 'rail_a' else (False, False))
        put(rn, xc + x0, lvl(1), z0, 0, [ht, ftag(1)])
    for fl in (0, 1, 2):
        lv = 'g' if fl == 0 else ('c' if fl == 2 else 'u')
        for dx in (-2, 0, 2):
            for z in ZM:
                tx0 = (T if i == 0 else PT) if dx == -2 else 0.0; tx1 = (T if i == NH - 1 else PT) if dx == 2 else 0.0
                tr = (tx0, tx1, T if z == -5 else 0.0, T if z == 5 else 0.0)
                hs = []
                if fl == 1:
                    r_ = sbox(dx - 1, z - 1, dx + 1, z + 1).intersection(sbox(HOLE1[0], HOLE1[1], HOLE1[2], HOLE1[3]))
                    if r_.area > 1e-6: bb = r_.bounds; hs.append((round(bb[0] - dx, 3), round(bb[1] - z, 3), round(bb[2] - dx, 3), round(bb[3] - z, 3)))
                kind = 'wood'
                if fl == 0 and dx == 2: kind = 'hall'
                if fl == 0 and dx in (-2, 0) and z == -5: kind = 'tile'
                if fl == 2: kind = 'wood'
                put(tile_piece(kind, lv, hs, tuple(round(t, 3) for t in tr)), xc + dx, lvl(fl), z, 0, [ht, ftag(fl) if fl < 2 else 'roof'])
    if i < NH - 1:
        for fl in (0, 1): put('party_g' if fl == 0 else 'party_u', xc + HX, lvl(fl), 0.0, 90, [ftag(fl)])
# paredes das pontas da fileira
for (x, ry, c, tg) in ((-15.0, -90, 'a', 'left'), (15.0, 90, 'e', 'right')):
    for fl, nm in ((0, 'g'), (1, 'u')):
        for z in ZM:
            k = 'win' if z in (-3, 1, 3) else 'plain'
            put(f'f_{nm}_{k}_{c}', x, lvl(fl), z, ry, [tg, 'ext', ftag(fl)])
    for zs_, dry in ((HZ, 0), (-HZ, 0)):
        pass
    put('downspout', x, 0.0, 5.2, ry, [tg, 'ext']); put('downspout', x, 0.0, -5.2, ry, [tg, 'ext'])
for (x, z, ry, c) in ((15.0, HZ, 0, 'e'), (-15.0, HZ, -90, 'a'), (15.0, -HZ, 90, 'e'), (-15.0, -HZ, 180, 'a')):
    for fl, nm in ((0, 'g'), (1, 'u')): put(f'corner_{nm}_{c}', x, lvl(fl), z, ry, ['ext', ftag(fl)])
put('fence_post', 15.0, 0.12, HZ + 4.3, 0, ['street'])
for x in (-15.0, 15.0): put('sidewalk', x + (1.0 if x < 0 else -1.0) * 0, 0.0, HZ + 4.2, 0, ['street']) if False else None
for x in (-7.5, 7.5): put('street_lamp', x, 0.12, HZ + 5.9, 0, ['street'])
put('player_scale_ref', 3.0, 0.12, HZ + 5.0); put('player_scale_ref', XC[2] - 1.0, Y0, 2.0, 0, [ftag(0)])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE,
                       'houses': [{'x': [xc - HX, xc + HX], 'z': [-HZ, HZ], 'color': c} for xc, c in zip(XC, HUES)],
                       'eave_level': YE, 'roof_pitch_deg': ANG, 'ridge_level': YE + RIDGE, 'party_wall_thickness': 2 * PT,
                       'stair_holes': {'1': [[HOLE1[0], HOLE1[1], HOLE1[2], HOLE1[3]]]}, 'stair_holes_frame': 'house-local x, z',
                       'roof': 'gable roofs (50 deg) facing the street, flashed valleys between houses',
                       'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
              'placements': L}
    json.dump(layout, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc2 = trimesh.Scene(); tot = 0
    for e in L:
        T_ = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T_[:3, 3] = e['pos']
        sc = pieces[e['piece']].scene(e['piece'])
        for nm, g in sc.geometry.items(): g2 = g.copy(); g2.apply_transform(T_); sc2.add_geometry(g2); tot += len(g2.faces)
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:12]: print(f'  {n:30s} {p.tris():6d} tri')
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
# folha da janela em no proprio, para o jogo abrir (scripts/detalhe/folhas.py, grava janelas.json)
import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe')); import folhas as _folhas
_folhas.kit(OUT)
# vao da janela rebocado por dentro (scripts/detalhe/vao.py)
import vao as _vao, glob as _gl
for _f in _gl.glob(_o.path.join(OUT, 'pieces', '*win*.glb')): _vao.rebocar(_f)
