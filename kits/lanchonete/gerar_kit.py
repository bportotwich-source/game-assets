"""Kit 36: lanchonete com drive-thru, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Predio de 12 x 10 m: paredes de reboco creme sobre barra de tijolo com capa de pedra, cornija com modilhoes e faixa amarela,
mansarda de telhas a 60 graus com rincoes, calhas e condutores, laje plana com 2 condensadoras e exaustores. Torre de entrada
vermelha com telhado em piramide de chapa com juntas em pe, sol raiado (sem texto) e portas duplas de vidro. Anexo envidracado
de salao com montantes amarelos e um milk-shake gigante no telhado. Janelas com toldos listrados, janela do drive-thru com
marquise, porta de servico. Dentro: salao com piso xadrez, forro modular com luminarias, balcao com caixas e quadros de cardapio
sem texto, cabines (booths), mesas, cozinha com chapa, fritadeiras, coifa, bancada e geladeira, 2 banheiros.
Fora: pista do drive-thru com setas, painel de pedidos com icones, interfone, portico de altura, estacionamento com vagas,
calcadas com rampa, patio com gradil e ombrelones, placa com hamburguer gigante, postes, ilhas de grama, arvores.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString
from shapely import affinity
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'render': (228, 208, 164), 'brick': (148, 66, 52), 'cill': (200, 192, 178), 'trim': (238, 230, 208), 'accent': (234, 178, 44),
                  'red': (176, 48, 40), 'redm': (170, 42, 36), 'shingles': (104, 68, 50), 'ridge': (70, 52, 44), 'frame': (70, 60, 52),
                  'frost': (214, 224, 228), 'canvas_r': (190, 46, 40), 'canvas_w': (240, 236, 224), 'plaster': (238, 230, 212),
                  'ceil': (238, 236, 228), 'tbar': (248, 248, 246), 'tile_r': (170, 50, 42), 'tile_w': (236, 228, 208), 'quarry': (150, 88, 66),
                  'steel': (196, 198, 200), 'membrane': (188, 188, 184), 'unit': (176, 180, 178), 'formica': (238, 222, 186), 'booth': (178, 40, 36),
                  'menu': (36, 32, 30), 'menu_lit': (248, 238, 210), 'bun': (204, 132, 58), 'patty': (90, 50, 34), 'cheese': (242, 184, 40),
                  'lettuce': (112, 170, 62), 'tomato': (204, 54, 42), 'seed': (246, 234, 200), 'cup_w': (244, 240, 230), 'cream': (252, 246, 236),
                  'asphalt': (66, 66, 68), 'paint_w': (234, 234, 228), 'paint_y': (230, 190, 52), 'concrete': (184, 180, 172), 'paver': (172, 112, 88),
                  'curb': (196, 192, 184), 'grass': (100, 146, 70), 'hedge': (64, 104, 52), 'leaf': (86, 130, 62), 'leaf2': (110, 146, 70),
                  'bark': (96, 72, 52), 'mulch': (88, 64, 46), 'porcelain': (242, 242, 238), 'door': (176, 48, 40), 'door_int': (226, 214, 186),
                  'gutter': (232, 224, 200), 'wood': (150, 104, 66), 'canvas_y': (226, 172, 62)},
           texturas={'render': 'render', 'red': 'render', 'brick': 'brick', 'shingles': 'shingles', 'plaster': 'plaster', 'quarry': 'stone',
                     'asphalt': 'render', 'concrete': 'render', 'paver': 'brick', 'grass': 'render', 'membrane': 'render', 'wood': 'planks'},
           out=OUT)
D.METAL.update({'redm', 'steel', 'unit'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.25; RAISE = 0.15; H0 = 3.6
Y0 = RAISE; YE = Y0 + H0                             # piso e topo das paredes
HX = 6.0; HZ = 5.0                                   # predio: x de -6 a 6, z de -5 a 5, frente para +Z
XI = HX - T; ZI = HZ - T
WAIN = 0.9                                           # barra de tijolo (capa de pedra no topo)
ANG = 60.0; KR = math.tan(math.radians(ANG)); CS = math.cos(math.radians(ANG))
MF, MB = 0.2, -0.6                                   # mansarda: pe (sobre a cornija) e topo, medidos da face da parede
RISE = KR * (MF - MB)
TV = 0.07; BUMP = 0.02
configurar_telhado(TV, BUMP, ANG)
TWH = 5.6; TCEIL = 3.0                               # torre: topo das paredes e forro do vestibulo (sobre o piso)
OPEN_H = 2.55; VEST_H = 2.7                          # vao para o anexo e vao do vestibulo
AW = 2.0; AD = 3.0                                   # anexo: meia-largura e profundidade (x de -6 a -2, z de 5 a 8)
SILL = 0.5                                           # mureta do anexo
ZR = -0.1                                            # parede dos banheiros
XK = -1.0                                            # parede oeste da cozinha
XD = -3.4                                            # divisoria entre os banheiros

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
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p
def mitre_pair(p, mat, prof):
    """Canto externo de um perfil (z, y) que corre nas duas fachadas (pivo na quina, paredes em -X e -Z): 2 cunhas em meia-esquadria."""
    D_ = max(z for z, y in prof) + 0.001
    q = Piece(); prof_x(q, mat, 0.0, D_, prof); p.add(mat, slice_keep(q.parts[mat][0], [0, 0, 0], np.array([-1, 0, 1]) / math.sqrt(2)))
    q = Piece(); prof_z(q, mat, 0.0, D_, prof); p.add(mat, slice_keep(q.parts[mat][0], [0, 0, 0], np.array([1, 0, -1]) / math.sqrt(2)))
def rot_y(deg, t=(0, 0, 0)):
    M = trimesh.transformations.rotation_matrix(math.radians(deg), [0, 1, 0]); M[:3, 3] = t; return M
def along(p, q, x0, z0, x1, z1, y=0.0):
    """Coloca a sub-peca q (construida ao longo de +X a partir da origem) no segmento (x0, z0) -> (x1, z1), eixo horizontal."""
    ang = math.degrees(math.atan2(-(z1 - z0), x1 - x0)); p.merge(q, rot_y(ang, (x0, y, z0)))
def clipped(p, planes):
    """Corta todas as malhas da peca pelos planos (origem, normal), mantendo o lado da normal (com tampa)."""
    q = Piece(); q.uv = p.uv
    for mat, ms in p.parts.items():
        for m in ms:
            mm = m
            for (o, n) in planes:
                mm = slice_keep(mm, o, np.array(n, float) / np.linalg.norm(n))
                if mm is None or len(mm.faces) == 0: break
            if mm is not None and len(mm.faces): q.add(mat, mm)
    return q
def segs_excl(gaps, a0=-1.0, a1=1.0, pad=0.0):
    segs = [(a0, a1)]
    for (a, b) in gaps: segs = [s for (c, d) in segs for s in ((c, min(d, a - pad)), (max(c, b + pad), d)) if s[1] - s[0] > 1e-3]
    return segs
def checker(p, poly, y0, y1, step=0.5, ma='tile_r', mb='tile_w', ox=0.0, oz=0.0):
    """Piso xadrez de ladrilhos de 'step' alinhado na grade global (ox, oz = deslocamento do pivo)."""
    b = poly.bounds; A = []; B = []
    for i in range(int(math.floor((b[0] + ox) / step)), int(math.ceil((b[2] + ox) / step))):
        for j in range(int(math.floor((b[1] + oz) / step)), int(math.ceil((b[3] + oz) / step))):
            sq = sbox(i * step - ox, j * step - oz, (i + 1) * step - ox, (j + 1) * step - oz).intersection(poly)
            if sq.area > 1e-6: (A if (i + j) % 2 == 0 else B).append(sq)
    ext_y(p, ma, unary_union(A), y0, y1); ext_y(p, mb, unary_union(B), y0, y1)

# ============================================================================ paredes de reboco sobre barra de tijolo
CAP_PROF = [(0.0, WAIN - 0.08), (0.045, WAIN - 0.08), (0.045, WAIN - 0.045), (0.0, WAIN)]
BASE_IN = [(-T, 0.0), (-T - 0.016, 0.0), (-T - 0.016, 0.1), (-T - 0.008, 0.115), (-T, 0.118)]
def wall_core(p, holes, top=H0):
    """Parede: tijolo ate a capa (e abaixo do piso), reboco acima, gesso por dentro (para 5 mm abaixo do topo)."""
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([-RAISE, 0.0, WAIN, top - 0.005, top] + [v for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'brick'
        if k == 0: return None if ys[j] >= top - 0.0051 else 'plaster'
        return 'brick' if cy < WAIN else 'render'
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
def storefront(p, a, b, y0, y1, mat='frame', glass='glass', mull=(), tr=None, zf=(-0.16, -0.06)):
    """Caixilho de aluminio no vao (face externa em z = 0): quadro, travessa da bandeira, montantes e vidro."""
    z0, z1 = zf; f = 0.05; zg = (z0 + z1) / 2
    p.box(mat, a, a + f, y0, y1, z0, z1); p.box(mat, b - f, b, y0, y1, z0, z1)
    p.box(mat, a + f, b - f, y1 - f, y1, z0, z1); p.box(mat, a + f, b - f, y0, y0 + 0.06, z0, z1)
    p.box(glass, a + f, b - f, y0 + 0.06, y1 - f, zg - 0.003, zg + 0.003)
    if tr: p.box(mat, a + f, b - f, tr - 0.025, tr + 0.025, z0 + 0.01, z1 - 0.01)
    for x in mull: p.box(mat, x - 0.025, x + 0.025, y0 + 0.06, (tr - 0.025) if tr else (y1 - f), z0 + 0.01, z1 - 0.01)
def awning(p, w=0.92, y_top=3.12, y_front=2.72, d=0.72, n=10):
    """Toldo listrado: lona inclinada em gomos vermelho e branco, sanefa com recortes em meia-lua, abas laterais e bracos de ferro."""
    xs = np.linspace(-w, w, n + 1); yv = 0.17; zv = d
    for i in range(n):
        a, b = xs[i], xs[i + 1]; mat = 'canvas_r' if i % 2 == 0 else 'canvas_w'
        p.hull(mat, [(x, y + dy, z) for x in (a, b) for (z, y) in ((0.005, y_top), (zv, y_front)) for dy in (0.0, 0.012)])
        r = (b - a) / 2; poly = unary_union([sbox(a, y_front - yv + r, b, y_front + 0.012), Point((a + b) / 2, y_front - yv + r).buffer(r, 8).intersection(sbox(a, y_front - yv, b, y_front - yv + r))])
        ext(p, mat, poly, zv - 0.006, zv + 0.004)
    for s in (-1, 1):
        a, b = sorted((s * w, s * (w + 0.01)))
        tri = Polygon([(0.005, y_top + 0.012), (zv, y_front + 0.012), (zv, y_front - 0.06), (0.005, y_top - 0.3)])
        m = trimesh.creation.extrude_polygon(tri, b - a); v = m.vertices.copy(); m.vertices = np.stack([a + v[:, 2], v[:, 1], v[:, 0]], 1); p.add('canvas_r', D._fix(m))
        seg_cyl(p, 'iron', (s * (w - 0.04), y_top - 0.42, 0.0), (s * (w - 0.04), y_front - 0.01, zv - 0.03), 0.012, 6)
        p.cham('iron', s * (w - 0.04) - 0.03, s * (w - 0.04) + 0.03, y_top - 0.46, y_top - 0.38, 0.0, 0.02, 0.004)
    seg_cyl(p, 'iron', (-w + 0.01, y_front - 0.005, zv - 0.03), (w - 0.01, y_front - 0.005, zv - 0.03), 0.01, 6)
def win_unit(p):
    """Janela grande do salao: caixilho bronze com bandeira, peitoril interno, verga de pedra e toldo listrado."""
    a, b = -0.65, 0.65; y0, y1 = WAIN, 2.6
    storefront(p, a, b, y0, y1, mull=(0.0,), tr=2.15)
    p.box('trim', a - 0.05, b + 0.05, y0 - 0.03, y0 + 0.02, -T - 0.04, -0.16)
    p.cham('cill', a - 0.12, b + 0.12, y1, y1 + 0.12, 0.0, 0.03, 0.006)
    awning(p)
    return [(a, b)]
def hwin_unit(p):
    a, b = -0.45, 0.45; y0, y1 = 1.9, 2.5
    storefront(p, a, b, y0, y1, glass='frost', mull=(0.0,))
    prof_x(p, 'cill', a - 0.1, b + 0.1, [(0.0, y0 - 0.06), (0.05, y0 - 0.06), (0.05, y0 - 0.035), (0.0, y0)])
    p.cham('cill', a - 0.1, b + 0.1, y1, y1 + 0.12, 0.0, 0.03, 0.006)
def dt_unit(p):
    """Janela do drive-thru: quadro de aco, folha fixa e folha corrida aberta, prateleiras de inox dentro e fora com misulas,
    moldura vermelha, marquise de chapa com tirantes e luminaria."""
    a, b = -0.6, 0.6; y0, y1 = 0.95, 2.2
    p.box('steel', a, a + 0.05, y0, y1, -0.16, -0.06); p.box('steel', b - 0.05, b, y0, y1, -0.16, -0.06)
    p.box('steel', a + 0.05, b - 0.05, y1 - 0.05, y1, -0.16, -0.06); p.box('steel', a + 0.05, b - 0.05, y0, y0 + 0.03, -0.16, -0.06)
    for (xa, xb, za, zb) in ((a + 0.05, 0.02, -0.105, -0.075), (a + 0.09, 0.06, -0.15, -0.12)):     # folha fixa e folha corrida (aberta, atras)
        p.box('steel', xa, xa + 0.04, y0 + 0.03, y1 - 0.05, za, zb); p.box('steel', xb - 0.04, xb, y0 + 0.03, y1 - 0.05, za, zb)
        p.box('steel', xa + 0.04, xb - 0.04, y0 + 0.03, y0 + 0.08, za, zb); p.box('steel', xa + 0.04, xb - 0.04, y1 - 0.09, y1 - 0.05, za, zb)
        p.box('glass', xa + 0.04, xb - 0.04, y0 + 0.08, y1 - 0.09, (za + zb) / 2 - 0.003, (za + zb) / 2 + 0.003)
    p.box('steel', 0.02, 0.05, y0 + 0.9, y0 + 1.0, -0.075, -0.045)                                     # puxador
    p.cham('steel', a - 0.06, b + 0.06, y0 - 0.025, y0 + 0.005, -0.06, 0.34, 0.004)                             # prateleira externa
    for s in (-1, 1): p.hull('steel', [(s * 0.45 + dx, y, z) for dx in (-0.01, 0.01) for (z, y) in ((0.0, y0 - 0.03), (0.3, y0 - 0.03), (0.0, y0 - 0.3))])
    p.cham('steel', a - 0.06, b + 0.06, y0 - 0.025, y0 + 0.005, -T - 0.3, -0.16, 0.004)                         # prateleira interna
    for (xa, xb, ya, yb) in ((a - 0.12, a, y0, y1 + 0.12), (b, b + 0.12, y0, y1 + 0.12), (a, b, y1, y1 + 0.12)):
        p.box('red', xa, xb, ya, yb, 0.0, 0.025)
    yc = 2.62                                                                                          # marquise
    p.hull('redm', [(x, y, z) for x in (-0.95, 0.95) for (z, y) in ((0.005, yc + 0.08), (0.005, yc + 0.12), (1.0, yc - 0.02), (1.0, yc + 0.02))])
    p.box('accent', -0.97, 0.97, yc - 0.14, yc + 0.03, 1.0, 1.03)
    for s in (-1, 1): p.box('accent', *sorted((s * 0.95, s * 0.98)), yc - 0.14, yc + 0.03, 0.005, 1.03)
    for s in (-1, 1):
        seg_cyl(p, 'steel', (s * 0.85, 3.05, 0.0), (s * 0.85, yc + 0.03, 0.95), 0.012, 6)
        p.cham('steel', s * 0.85 - 0.04, s * 0.85 + 0.04, 3.0, 3.1, 0.0, 0.02, 0.004)
    p.box('lamp_glass', -0.2, 0.2, yc - 0.03, yc - 0.01, 0.4, 0.6); p.box('steel', -0.22, 0.22, yc - 0.01, yc + 0.03, 0.38, 0.62)
def louver(p, w, h, yc, n=None):
    """Grelha de ventilacao sobreposta a fachada (aletas inclinadas numa moldura)."""
    a, b = -w / 2, w / 2; y0, y1 = yc - h / 2, yc + h / 2
    p.box('unit', a, b, y0, y1, 0.0, 0.012)
    for (xa, xb, ya, yb) in ((a, a + 0.04, y0, y1), (b - 0.04, b, y0, y1), (a, b, y0, y0 + 0.04), (a, b, y1 - 0.04, y1)): p.box('unit', xa, xb, ya, yb, 0.012, 0.05)
    n = n or int((h - 0.08) / 0.06)
    for i in range(n):
        y = y0 + 0.06 + i * (h - 0.1) / n
        p.hull('unit', [(x, yy, z) for x in (a + 0.04, b - 0.04) for (z, yy) in ((0.012, y + 0.035), (0.012, y + 0.045), (0.045, y), (0.045, y + 0.01))])
def wall(kind='plain'):
    """Modulo de 2 m (pivo: face externa, cota do piso). kind: plain, win, hwin, dt (drive-thru), bdoor (servico), vent, louver,
    open_a / open_b (vao para o anexo), vest_l / vest_r (vao para o vestibulo da torre)."""
    p = Piece(); holes = []
    if kind == 'win': holes = [(-0.65, 0.65, WAIN, 2.6)]
    if kind == 'hwin': holes = [(-0.45, 0.45, 1.9, 2.5)]
    if kind == 'dt': holes = [(-0.6, 0.6, 0.95, 2.2)]
    if kind == 'bdoor': holes = [(-0.5, 0.5, 0.0, 2.2)]
    if kind == 'open_a': holes = [(-0.77, 1.0, 0.0, OPEN_H)]
    if kind == 'open_b': holes = [(-1.0, 0.75, 0.0, OPEN_H)]
    if kind == 'vest_l': holes = [(-0.25, 1.0, 0.0, VEST_H)]
    if kind == 'vest_r': holes = [(-1.0, 0.25, 0.0, VEST_H)]
    wall_core(p, holes)
    gaps = [(a, b) for (a, b, c, d) in holes if c == 0.0]
    if kind == 'win': win_unit(p)
    if kind == 'hwin': hwin_unit(p)
    if kind == 'dt': dt_unit(p)
    if kind == 'vent': louver(p, 0.5, 0.36, 2.75)
    if kind == 'louver': louver(p, 0.9, 0.7, 2.45)
    pad = 0.0
    if kind == 'bdoor':
        q = Piece(); door_casing(q, 1.0, T, 2.2); p.merge(q, trimesh.transformations.translation_matrix([0, 0, -T / 2])); pad = 0.09
        q = wall_lantern(); p.merge(q, trimesh.transformations.translation_matrix([0, 2.6, 0.0]))
    for (a, b) in gaps: p.box('cill', a + (0.001 if abs(a + 1) < 1e-6 else 0.0), b - (0.001 if abs(b - 1) < 1e-6 else 0.0), -0.03, 0.006, -T + 0.004, 0.05 if kind == 'bdoor' else -0.002)
    bsegs = {'vest_l': [(-1.0, -0.5)], 'vest_r': [(0.5, 1.0)]}.get(kind, segs_excl(gaps, pad=pad))
    for (a, b) in bsegs: prof_x(p, 'cill', a, b, CAP_PROF)
    for (a, b) in segs_excl(gaps, -0.999, 0.999, pad): prof_x(p, 'trim', a, b, BASE_IN)
    return p
def corner():
    """Quina (pivo: quina externa, cota do piso; paredes em -X e -Z): nucleo de tijolo e reboco, capa da barra em meia-esquadria."""
    p = Piece(); e = 0.004
    p.box('brick', -T + e, e, -RAISE, WAIN - 0.08, -T + e, e); p.box('render', -T + e, e, WAIN - 0.08, H0 - 0.004, -T + e, e)
    mitre_pair(p, 'cill', CAP_PROF)
    return p

# ============================================================================ mansarda de 60 graus (pivo: face da parede, cota do topo da parede)
CORN_PROF = [(0.0, -0.32), (0.04, -0.32), (0.04, -0.27), (0.08, -0.25), (0.26, -0.2), (0.3, -0.2), (0.3, 0.0), (0.0, 0.0)]
def mansard(kind=''):
    """Faixa de 2 m da mansarda: forro de tabuas, fiadas de telhas a 60 graus, cornija com modilhoes, faixa amarela no friso,
    calha K, capa de pedra no topo. kind: '' (meio), 'a' / 'b' (pontas com rincao a 45 graus em x- / x+), 'tl' / 'tr' (cortadas
    pela torre de entrada)."""
    p = Piece(); x0 = -1.5 if kind == 'a' else -1.0; x1 = 1.5 if kind == 'b' else 1.0
    f = lambda a, b: KR * (MF - b)
    poly = sbox(x0, MB, x1, MF)
    sheared(p, 'dark', poly, 0.0, 0.02, f)
    sheared_courses(p, sbox(x0, MB + 0.08, x1, MF), f, lambda a, b: MF - b, lambda d0, d1: sbox(-50, MF - d1, 50, MF - d0), MF - MB - 0.07,
                    lambda v, n: np.stack([v[:, 0] / TILE, (MF - v[:, 2]) / CS / TILE], 1))
    prof_x(p, 'trim', x0, x1, CORN_PROF)
    prof_x(p, 'accent', x0, x1, [(-0.005, -0.47), (0.02, -0.47), (0.02, -0.37), (-0.005, -0.37)])
    for xm in np.arange(-1.2, 1.21, 0.4):
        if x0 - 0.05 < xm < x1 + 0.05 and abs(abs(xm) - 1.0) > 0.1:
            p.hull('trim', [(xm + dx, y, z) for dx in (-0.035, 0.035) for (z, y) in ((0.04, -0.3), (0.21, -0.3), (0.04, -0.24), (0.21, -0.19))])
    gutter_run(p, x0, x1, 0.3, 0.03)
    p.box('cill', x0, x1, RISE + 0.02, RISE + 0.14, MB - 0.12, MB + 0.08)
    if kind == 'a': p = clipped(p, [((-1.0, 0, 0), (1, 0, 1))])
    if kind == 'b': p = clipped(p, [((1.0, 0, 0), (-1, 0, 1))])
    if kind == 'tl': p = clipped(p, [((-0.4, 0, 0), (-1, 0, 0))])
    if kind == 'tr': p = clipped(p, [((0.4, 0, 0), (1, 0, 0))])
    return p
def hip():
    """Capa do rincao da mansarda (pivo: quina externa, cota do topo da parede; paredes em -X e -Z)."""
    p = Piece(); yo = TV + BUMP + 0.004; pts = []
    for h in (MF + 0.03, MB):
        y = KR * (MF - h) + yo
        pts += [(h, y + 0.045, h), (h - 0.09, y, h), (h, y, h - 0.09), (h - 0.07, y - 0.02, h), (h, y - 0.02, h - 0.07)]
    p.hull('ridge', pts)
    return p
def roof_flat():
    """Laje plana dentro da mansarda (pivo: centro, cota do topo da parede): manta, alcapao, respiros e calcadas de servico."""
    p = Piece(); y = RISE + 0.02
    p.box('membrane', -HX + 0.55, HX - 0.55, RISE - 0.1, y, -HZ + 0.55, HZ - 0.55)
    p.cham('unit', 2.2, 3.1, y, y + 0.35, -3.6, -2.7, 0.01); p.cham('unit', 2.15, 3.15, y + 0.35, y + 0.42, -3.65, -2.65, 0.01)   # alcapao
    for (x, z) in ((-4.4, -3.4), (-3.9, -3.4), (-2.2, -3.6)):
        p.cyl('dark', 0.07, y, y + 0.02, x, z, 10); p.cyl('unit', 0.045, y + 0.02, y + 0.5, x, z, 10); p.cyl('unit', 0.06, y + 0.5, y + 0.53, x, z, 10)
    for (x0, x1, z0, z1) in ((-2.0, 2.0, 0.6, 1.2), (3.0, 3.6, -2.6, 1.0)):
        for xx in np.arange(x0, x1 - 0.01, 0.6): p.box('concrete', xx + 0.01, xx + 0.59, y, y + 0.04, z0, z1)
    return p
def hvac():
    """Condensadora no telhado (pivo: base, no centro): trilhos, gabinete com aletas, grade do ventilador com helice, paineis."""
    p = Piece()
    for z in (-0.35, 0.35): p.box('dark', -0.95, 0.95, 0.0, 0.12, z - 0.05, z + 0.05)
    p.cham('unit', -0.8, 0.8, 0.12, 1.1, -0.5, 0.5, 0.015)
    for s in (-1, 1):
        for i in range(12):
            y = 0.25 + i * 0.06
            p.hull('unit', [(x, yy, s * z) for x in (-0.72, 0.05) for (z, yy) in ((0.5, y + 0.035), (0.5, y + 0.045), (0.53, y), (0.53, y + 0.01))])
        p.box('dark', 0.15, 0.17, 0.2, 1.02, *sorted((s * 0.5, s * 0.506)))
        p.box('dark', 0.45, 0.75, 0.55, 0.95, *sorted((s * 0.5, s * 0.504)))
    p.cyl('dark', 0.36, 1.1, 1.13, 0.35, 0.0, 24)
    lathe(p, 'unit', [(0.4, 1.1), (0.4, 1.16), (0.36, 1.16), (0.36, 1.13)], 0.35, 0.0, 0.0, 24)
    for k in range(4):
        a = k * math.pi / 4; seg_cyl(p, 'steel', (0.35 - 0.37 * math.cos(a), 1.16, -0.37 * math.sin(a)), (0.35 + 0.37 * math.cos(a), 1.16, 0.37 * math.sin(a)), 0.006, 4)
    for r in (0.12, 0.24):
        m = trimesh.creation.annulus(r_min=r - 0.006, r_max=r + 0.006, height=0.012, sections=24); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0.35, 1.16, 0]); p.add('steel', m)
    p.cyl('steel', 0.06, 1.13, 1.16, 0.35, 0.0, 10)
    for k in range(3):
        a = k * 2 * math.pi / 3; p.hull('dark', [(0.35 + r * math.cos(a + d), 1.135, r * math.sin(a + d)) for r in (0.06, 0.3) for d in (-0.2, 0.2)] + [(0.35 + 0.18 * math.cos(a), 1.15, 0.18 * math.sin(a))])
    p.cham('unit', -0.6, -0.2, 1.1, 1.14, -0.3, 0.3, 0.006)
    p.box('unit', -0.6, -0.4, -0.02, 0.12, -0.12, 0.12)
    return p
def exhaust_fan():
    p = Piece()
    p.cham('unit', -0.35, 0.35, 0.0, 0.35, -0.35, 0.35, 0.01); p.cham('unit', -0.4, 0.4, 0.35, 0.39, -0.4, 0.4, 0.008)
    p.cyl('unit', 0.24, 0.39, 0.62, 0, 0, 16); p.cyl('dark', 0.22, 0.62, 0.74, 0, 0, 16)
    lathe(p, 'unit', [(0.48, 0.7), (0.48, 0.74), (0.42, 0.86), (0.25, 0.95), (0.0, 0.98)], sec=20)
    return p

# ============================================================================ torre de entrada (pivo: face da frente do predio no eixo, cota do piso)
def skin(Ln, y0, y1, holes, inner_top, outer='red', t=T, ends=False):
    """Parede da torre ao longo de +X (face externa em z = 0, interna em z = -t): tijolo ate a capa, cor externa acima, gesso
    por dentro ate inner_top."""
    q = Piece()
    xs = sorted(set([0.0, Ln] + ([t, Ln - t] if ends else []) + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, y1] + [v for v in [0.0, WAIN, inner_top] + [v for hh in holes for v in hh[2:]] if y0 < v < y1]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'brick'
        if k == 0 and not (ends and (cx < t or cx > Ln - t)): return 'plaster' if cy < inner_top else outer
        return 'brick' if cy < WAIN else outer
    for m, mesh in grid_solid(xs, ys, [-t, -t + 0.02, 0.0], cell).items(): q.add(m, mesh)
    return q
def door_leaf_glass(w=0.84, h=2.28, t=0.045):
    """Folha de porta de vidro com quadro de aluminio bronze, rodape alto e puxador vertical / barra (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.1
    p.box('frame', 0.0, s, 0.0, h, -t / 2, t / 2); p.box('frame', w - s, w, 0.0, h, -t / 2, t / 2)
    p.box('frame', s, w - s, h - s, h, -t / 2, t / 2); p.box('frame', s, w - s, 0.0, 0.26, -t / 2, t / 2)
    p.box('frame', s, w - s, 1.0, 1.06, -t / 2 + 0.008, t / 2 - 0.008)
    p.box('glass', s, w - s, 0.26, h - s, -0.004, 0.004)
    for z in (1, -1):
        seg_cyl(p, 'steel', (w - 0.17, 0.85, z * (t / 2 + 0.05)), (w - 0.17, 1.55, z * (t / 2 + 0.05)), 0.016, 8)
        for y in (0.9, 1.5): seg_cyl(p, 'steel', (w - 0.17, y, z * t / 2), (w - 0.17, y, z * (t / 2 + 0.05)), 0.01, 6)
    for yy in (0.2, 2.0): p.cyl('steel', 0.01, yy, yy + 0.08, 0.0, t / 2 + 0.002, 8)
    return p
def tower():
    """Torre de entrada: paredes vermelhas sobre tijolo, porta dupla de vidro com bandeira, faixa amarela, sol raiado no alto
    (sem texto), cornija amarela, beiral, telhado em piramide de chapa vermelha com juntas em pe, cumeeiras amarelas e pinaculo.
    Dentro: piso xadrez, tapete, forro com luminaria."""
    p = Piece(); y1 = TWH - 0.01; Hc = H0 - 0.35
    p.merge(skin(2.75, -RAISE, y1, [(0.0, 1.0, -RAISE, Hc)], TCEIL), rot_y(-90, (-1.5, 0, -1.0)))
    p.merge(skin(2.75, -RAISE, y1, [(1.75, 2.75, -RAISE, Hc)], TCEIL), rot_y(90, (1.5, 0, 1.75)))
    p.merge(skin(3.0, -RAISE, y1, [(0.6, 2.4, 0.0, 2.75)], TCEIL, ends=True), rot_y(0, (-1.5, 0, 2.0)))
    p.merge(skin(3.0, Hc, y1, [], TCEIL), rot_y(180, (1.5, 0, -1.0)))
    # caixilho da porta e bandeira
    zf0, zf1 = 2.0 - 0.16, 2.0 - 0.06
    p.box('frame', -0.9, -0.85, 0.0, 2.75, zf0, zf1); p.box('frame', 0.85, 0.9, 0.0, 2.75, zf0, zf1)
    p.box('frame', -0.85, 0.85, 2.7, 2.75, zf0, zf1); p.box('frame', -0.85, 0.85, 2.3, 2.36, zf0, zf1)
    p.box('glass', -0.85, 0.85, 2.36, 2.7, 1.887, 1.893); p.box('frame', -0.02, 0.02, 2.36, 2.7, zf0 + 0.01, zf1 - 0.01)
    p.box('cill', -0.899, 0.899, -0.03, 0.006, 1.754, 2.06)
    # capa da barra, faixa amarela e cornija do topo
    for (xa, xb) in ((-1.545, -0.9), (0.9, 1.545)): p.box('cill', xa, xb, WAIN - 0.08, WAIN, 2.0, 2.045)
    for s in (-1, 1): p.box('cill', *sorted((s * 1.5, s * 1.545)), WAIN - 0.08, WAIN, 0.0, 2.045)
    for (ya, yb, d) in ((3.0, 3.12, 0.03), (TWH - 0.26, y1, 0.08)):
        p.box('accent', -1.5 - d, 1.5 + d, ya, yb, 2.0, 2.0 + d)
        for s in (-1, 1): p.box('accent', *sorted((s * 1.5, s * (1.5 + d))), ya, yb, -1.0 - d if yb > H0 else 0.0, 2.0 + d)
        if yb > H0: p.box('accent', -1.5 - d, 1.5 + d, ya, yb, -1.0 - d, -1.0)
    # sol raiado (sem texto)
    yc = 3.3; R = 1.0
    p.box('accent', -1.08, 1.08, yc - 0.06, yc, 2.0, 2.03)
    for i in range(10):
        a0, a1 = math.pi * i / 10, math.pi * (i + 1) / 10
        ray = Polygon([(0.38 * math.cos(a0), yc + 0.38 * math.sin(a0)), (R * math.cos(a0), yc + R * math.sin(a0)), (R * math.cos(a1), yc + R * math.sin(a1)), (0.38 * math.cos(a1), yc + 0.38 * math.sin(a1))])
        ext(p, 'accent' if i % 2 == 0 else 'trim', ray, 2.0, 2.02)
    ext(p, 'accent', Point(0, yc).buffer(1.08, 32).difference(Point(0, yc).buffer(R, 32)).intersection(sbox(-2, yc, 2, 9)), 2.0, 2.03)
    ext(p, 'accent', Point(0, yc).buffer(0.38, 24).intersection(sbox(-2, yc, 2, 9)), 2.0, 2.035)
    ext(p, 'red', Point(0, yc).buffer(0.26, 24).intersection(sbox(-2, yc, 2, 9)), 2.035, 2.045)
    # beiral e piramide
    zc = 0.5; E = 1.8; yt = TWH + 0.03; AP = 1.9
    p.box('trim', -E, E, y1, yt, zc - E, zc + E)
    for s in (-1, 1):
        p.box('accent', -E - 0.03, E + 0.03, y1 - 0.01, yt + 0.03, *sorted((zc + s * E, zc + s * (E + 0.03))))
        p.box('accent', *sorted((s * E, s * (E + 0.03))), y1 - 0.01, yt + 0.03, zc - E, zc + E)
    nrm = np.array([0.0, E, AP]) / math.hypot(E, AP)
    for k in range(4):
        q = Piece()
        q.hull('redm', [(x, yt + dy, E) for x in (-E, E) for dy in (0.0, 0.04)] + [(0, yt + AP, 0), (0, yt + AP + 0.04, 0)])
        for u in np.arange(-1.6, 1.61, 0.32):
            t_ = 1 - abs(u) / E; a = np.array([u, yt + 0.04, E]) + nrm * 0.012; b = np.array([u, yt + 0.04 + AP * t_, E - E * t_]) + nrm * 0.012
            if t_ > 0.05: q.seg('redm', a, b, 0.022, 0.03)
        q.seg('accent', (E, yt + 0.06, E), (0.0, yt + AP + 0.06, 0.0), 0.09, 0.07)
        p.merge(q, rot_y(90 * k, (0, 0, zc)))
    lathe(p, 'accent', [(0.12, yt + AP - 0.1), (0.12, yt + AP + 0.12), (0.08, yt + AP + 0.18), (0.0, yt + AP + 0.2)], 0.0, zc, 0.0, 12)
    p.sphere('accent', 0.11, 0.0, yt + AP + 0.3, zc, 1); seg_cyl(p, 'steel', (0, yt + AP + 0.38, zc), (0, yt + AP + 0.85, zc), 0.012, 6)
    # dentro: piso, tapete, rodapes, forro e luminaria
    fl = sbox(-1.25, 0.0, 1.25, 1.75)
    checker(p, fl, -0.012, 0.0, ox=0.0, oz=HZ); ext_y(p, 'concrete', fl.buffer(-0.02, join_style=2), -RAISE + 0.02, -0.012)
    p.cham('dark', -0.75, 0.75, 0.0, 0.01, 0.3, 1.5, 0.004)
    for s in (-1, 1):
        q = Piece(); prof_x(q, 'trim', 0.0, 1.75, [(0.0, 0.0), (0.016, 0.0), (0.016, 0.1), (0.008, 0.115), (0.0, 0.118)]); p.merge(q, rot_y(-90 * s, (s * 1.25, 0, 0.0 if s < 0 else 1.75)))
        prof_x(p, 'trim', *sorted((s * 1.25, s * 0.9)), [(1.75, 0.0), (1.734, 0.0), (1.734, 0.1), (1.742, 0.115), (1.75, 0.118)])
    ext_y(p, 'ceil', fl, TCEIL, TCEIL + 0.03)
    p.cyl('steel', 0.2, TCEIL - 0.015, TCEIL, 0.0, 0.9, 20); p.cyl('lamp_glass', 0.17, TCEIL - 0.02, TCEIL - 0.015, 0.0, 0.9, 20)
    return p

# ============================================================================ anexo envidracado (pivo: face da frente do predio, x = -4, cota do piso)
def annex():
    """Salao envidracado: mureta de tijolo com capa, caixilhos amarelos com bandeira, cantoneiras, platibanda vermelha com friso
    amarelo e capa, laje plana com buzinote e condutor. Dentro: piso xadrez, forro com luminarias."""
    p = Piece(); A = AW; Dp = AD; t = T
    # mureta (tijolo)
    for (x0, x1, z0, z1) in ((-A, A, Dp - t, Dp), (-A, -A + t, 0.0, Dp), (A - t, A, 0.0, Dp)): p.box('brick', x0, x1, -RAISE + 0.003, SILL, z0, z1)
    for (x0, x1, z0, z1) in ((-A - 0.03, A + 0.03, Dp - t - 0.03, Dp + 0.03), (-A - 0.03, -A + t + 0.03, 0.003, Dp + 0.03), (A - t - 0.03, A + 0.03, 0.003, Dp + 0.03)):
        p.cham('cill', x0, x1, SILL, SILL + 0.06, z0, z1, 0.006)
    yb, yh = SILL + 0.06, 2.42
    # caixilhos (amarelos): frente e laterais
    zf = (Dp - 0.17, Dp - 0.07); zg = Dp - 0.12
    p.box('accent', -A + 0.12, A - 0.12, yb, yb + 0.06, *zf); p.box('accent', -A + 0.12, A - 0.12, 2.0, 2.05, *zf); p.box('accent', -A + 0.12, A - 0.12, yh - 0.06, yh, *zf)
    for x in (-1.0, 0.0, 1.0): p.box('accent', x - 0.03, x + 0.03, yb + 0.06, yh - 0.06, zf[0] + 0.01, zf[1] - 0.01)
    p.box('glass', -A + 0.121, A - 0.121, yb + 0.06, yh - 0.06, zg - 0.003, zg + 0.003)
    for s in (-1, 1):
        xf = (s * (A - 0.17), s * (A - 0.07)); xa, xb = sorted(xf); xg = s * (A - 0.12)
        p.box('accent', xa, xb, yb, yb + 0.06, 0.12, Dp - 0.12); p.box('accent', xa, xb, 2.0, 2.05, 0.12, Dp - 0.12); p.box('accent', xa, xb, yh - 0.06, yh, 0.12, Dp - 0.12)
        for z in (1.0, 2.0): p.box('accent', xa + 0.01, xb - 0.01, yb + 0.06, yh - 0.06, z - 0.03, z + 0.03)
        p.box('glass', xg - 0.003, xg + 0.003, yb + 0.06, yh - 0.06, 0.121, Dp - 0.121)
        for z0 in (0.0, Dp - 0.12):                                                                      # cantoneiras
            p.cham('accent', *sorted((s * A, s * (A - 0.12))), yb, yh, z0 + (0.003 if z0 == 0 else 0.0), z0 + 0.12, 0.008)
    # platibanda vermelha, friso amarelo, capa
    for (x0, x1, z0, z1) in ((-A - 0.05, A + 0.05, Dp - 0.08, Dp + 0.05), (-A - 0.05, -A + 0.08, 0.003, Dp + 0.05), (A - 0.08, A + 0.05, 0.003, Dp + 0.05)):
        p.box('red', x0, x1, yh, 2.7, z0, z1)
    for (x0, x1, z0, z1) in ((-A - 0.06, A + 0.06, Dp + 0.05, Dp + 0.06), (-A - 0.06, -A - 0.05, 0.003, Dp + 0.06), (A + 0.05, A + 0.06, 0.003, Dp + 0.06)):
        p.box('accent', x0, x1, 2.5, 2.56, z0, z1)
    for (x0, x1, z0, z1) in ((-A - 0.08, A + 0.08, Dp - 0.12, Dp + 0.08), (-A - 0.08, -A + 0.12, 0.003, Dp + 0.08), (A - 0.12, A + 0.08, 0.003, Dp + 0.08)):
        p.cham('cill', x0, x1, 2.7, 2.78, z0, z1, 0.006)
    p.box('membrane', -A + 0.08, A - 0.08, OPEN_H, 2.7, 0.0, Dp - 0.08)
    p.box('ceil', -A + t, A - t, OPEN_H - 0.03, OPEN_H, 0.0, Dp - t)
    for (x, z) in ((-1.0, 1.4), (1.0, 1.4)):
        p.box('steel', x - 0.32, x + 0.32, OPEN_H - 0.04, OPEN_H - 0.03, z - 0.32, z + 0.32); p.box('lamp_glass', x - 0.3, x + 0.3, OPEN_H - 0.045, OPEN_H - 0.04, z - 0.3, z + 0.3)
    # buzinote e condutor na quina da frente-oeste
    p.box('gutter', -A - 0.2, -A - 0.05, 2.58, 2.64, Dp - 0.5, Dp - 0.4)
    seg_cyl(p, 'gutter', (-A - 0.16, 2.6, Dp - 0.45), (-A - 0.16, 0.25, Dp - 0.45), 0.035, 10)
    seg_cyl(p, 'gutter', (-A - 0.16, 0.25, Dp - 0.45), (-A - 0.36, 0.08, Dp - 0.45), 0.035, 10)
    for y in (0.9, 1.8): p.box('gutter', -A - 0.2, -A - 0.0, y, y + 0.03, Dp - 0.465, Dp - 0.435)
    # piso
    fl = sbox(-A + t, 0.0, A - t, Dp - t)
    checker(p, fl, -0.012, 0.0, ox=-4.0, oz=HZ); ext_y(p, 'concrete', fl.buffer(-0.02, join_style=2), -RAISE + 0.02, -0.012)
    for (a, b) in ((-A + t, A - t),): prof_x(p, 'trim', a, b, [(Dp - t, 0.0), (Dp - t - 0.016, 0.0), (Dp - t - 0.016, 0.1), (Dp - t - 0.008, 0.115), (Dp - t, 0.118)])
    return p
def milkshake():
    """Milk-shake gigante no telhado do anexo (pivo: base, sobre a laje): base amarela, copo listrado, tampa, chantili em
    espiral, cereja e canudo."""
    p = Piece()
    p.cyl('accent', 0.5, 0.0, 0.15, 0, 0, 24)
    lathe(p, 'cup_w', [(0.3, 0.15), (0.45, 1.25), (0.47, 1.3), (0.0, 1.3)], sec=24)
    for y in (0.4, 0.75, 1.1):
        r = 0.3 + 0.15 * (y - 0.15) / 1.1
        lathe(p, 'red', [(r + 0.006, y), (r + 0.006 + 0.15 * 0.1 / 1.1, y + 0.1)], sec=24)
    lathe(p, 'cup_w', [(0.48, 1.3), (0.48, 1.36), (0.4, 1.42), (0.0, 1.43)], sec=24)
    for k, (r, y) in enumerate(((0.38, 1.42), (0.3, 1.58), (0.21, 1.72), (0.12, 1.84))):
        lathe(p, 'cream', [(r, y), (r + 0.03, y + 0.07), (r - 0.04, y + 0.16), (0.0, y + 0.18)], sec=18)
    p.sphere('tomato', 0.09, 0.0, 2.08, 0.0, 2); seg_cyl(p, 'patty', (0.0, 2.15, 0.0), (0.04, 2.32, 0.05), 0.008, 5)
    seg_cyl(p, 'red', (0.12, 1.3, 0.05), (0.32, 2.35, 0.12), 0.035, 10)
    return p

# ============================================================================ portas internas, paredes, pisos e forros
def run_wall(Ln, h, doors=(), ow=0.86, t=0.12, end_gap=(0.0, 0.0)):
    """Parede interna de comprimento livre (pivo: inicio, eixo; vai para +X), com portas centradas em 'doors'."""
    p = Piece(); xs = sorted(set([0.0, Ln] + [c + s * ow / 2 for c in doors for s in (-1, 1)]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2
        return None if (j == 0 and any(abs(cx - c) < ow / 2 for c in doors)) else 'plaster'
    for m, mesh in grid_solid(xs, [0.0, 2.1, h], [-t / 2, t / 2], cell).items(): p.add(m, mesh)
    segs = [(end_gap[0], Ln - end_gap[1])]
    for c in doors:
        q = Piece(); door_casing(q, ow, t); p.merge(q, trimesh.transformations.translation_matrix([c, 0, 0]))
        segs = segs_excl([(c - ow / 2, c + ow / 2)], segs[0][0], segs[-1][1], 0.09) if len(segs) == 1 else [s_ for (a, b) in segs for s_ in segs_excl([(c - ow / 2, c + ow / 2)], a, b, 0.09)]
    for a, b in segs:
        if b - a > 0.02: baseboard(p, a, b, t)
    return p
def floor_tile(kind, trim=(0, 0, 0, 0), ox=0.0, oz=0.0):
    """Placa de 2 x 2 m: 'dine' (ladrilho xadrez), 'kit' (lajota da cozinha), 'ceil' / 'ceill' (forro modular, com luminarias).
    trim = recuo em metros (x-, x+, z-, z+)."""
    p = Piece(); x0, x1, z0, z1 = -1 + trim[0], 1 - trim[1], -1 + trim[2], 1 - trim[3]
    sq = sbox(x0, z0, x1, z1)
    if kind in ('ceil', 'ceill'):
        ext_y(p, 'ceil', sq, -0.03, 0.0)
        for v in (-1.0, -0.5, 0.0, 0.5):
            if x0 - 1e-6 <= v < x1 - 0.012: p.box('tbar', v, v + 0.012 if v == -1.0 else v + 0.006, -0.042, -0.03, z0, z1) if v == -1.0 else p.box('tbar', v - 0.006, v + 0.006, -0.042, -0.03, z0, z1)
            if z0 - 1e-6 <= v < z1 - 0.012: p.box('tbar', x0, x1, -0.04, -0.03, v, v + 0.012) if v == -1.0 else p.box('tbar', x0, x1, -0.04, -0.03, v - 0.006, v + 0.006)
        if kind == 'ceill':
            for (a, b, c, d) in ((0.01, 0.49, -0.49, -0.01), (-0.49, -0.01, 0.01, 0.49)):
                p.box('lamp_glass', a, b, -0.034, -0.03, c, d)
        return p
    if kind == 'dine': checker(p, sq, -0.012, 0.0, ox=1.0, oz=1.0)
    elif kind == 'half': checker(p, sq.intersection(sbox(-2, -2, 0, 2)), -0.012, 0.0, ox=1.0, oz=1.0); ext_y(p, 'quarry', sq.intersection(sbox(0, -2, 2, 2)), -0.012, 0.0)
    else: ext_y(p, 'quarry', sq, -0.012, 0.0)
    ext_y(p, 'concrete', sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0)), -RAISE + 0.02, -0.012)
    return p

# ============================================================================ salao e cozinha
def chair(p, x, z, ry, mat='steel', seat='booth'):
    q = Piece()
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): seg_cyl(q, mat, (sx * 0.18, 0.0, sz * 0.18), (sx * 0.17, 0.45, sz * 0.17), 0.012, 6)
    q.cham(seat, -0.21, 0.21, 0.45, 0.5, -0.21, 0.21, 0.015)
    for sx in (-1, 1): seg_cyl(q, mat, (sx * 0.17, 0.48, -0.19), (sx * 0.19, 0.88, -0.24), 0.012, 6)
    q.cham(seat, -0.2, 0.2, 0.68, 0.88, -0.27, -0.22, 0.015)
    p.merge(q, rot_y(ry, (x, 0, z)))
def table_set(n=4, r=0.38, square=True, umbrella=None):
    """Mesa com cadeiras estofadas (pivo: centro, no piso): tampo de formica com borda de aco, coluna e pe."""
    p = Piece()
    lathe(p, 'steel', [(0.24, 0.0), (0.24, 0.02), (0.05, 0.06), (0.035, 0.7), (0.1, 0.72)], sec=12)
    if square: p.cham('formica', -r, r, 0.72, 0.755, -r, r, 0.006); p.box('steel', -r - 0.006, r + 0.006, 0.715, 0.735, -r - 0.006, r + 0.006)
    else: p.cyl('formica', r, 0.72, 0.755, 0, 0, 24)
    for k in range(n):
        a = 2 * math.pi * k / n + (math.pi / 4 if not square else 0.0); d = r + 0.3
        chair(p, d * math.cos(a), d * math.sin(a), -math.degrees(a) - 90)
    if umbrella:
        p.cyl('steel', 0.02, 0.755, 2.4, 0, 0, 8); R = 1.1; yc = 2.25
        pts = [(R * math.cos(t), yc, R * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        p.hull(umbrella, pts + [(0, yc + 0.35, 0)])
        for t in np.linspace(0, 2 * math.pi, 8, endpoint=False):
            p.hull(umbrella, [(R * math.cos(t + s * math.pi / 8) * 0.98, yc + dy, R * math.sin(t + s * math.pi / 8) * 0.98) for s in (-1, 1) for dy in (-0.14, 0.0)] + [(R * math.cos(t), yc - 0.18, R * math.sin(t))])
            seg_cyl(p, 'steel', (0, 1.9, 0), (0.85 * math.cos(t), yc - 0.02, 0.85 * math.sin(t)), 0.008, 5)
        p.sphere('steel', 0.04, 0, yc + 0.38, 0, 1)
    return p
def booth():
    """Cabine (booth) encostada na parede (pivo: face interna da parede, no piso; sai para +Z): mesa de formica com borda de aco
    presa na parede e em coluna, 2 bancos estofados com encosto alto capitonê e laterais de formica."""
    p = Piece(); Lz = 1.3
    p.cham('formica', -0.38, 0.38, 0.72, 0.755, 0.01, 1.12, 0.006); p.box('steel', -0.386, 0.386, 0.715, 0.735, 0.004, 1.126)
    lathe(p, 'steel', [(0.22, 0.0), (0.22, 0.02), (0.05, 0.06), (0.035, 0.7), (0.1, 0.715)], 0.0, 0.8, 0.0, 12)
    p.box('steel', -0.2, 0.2, 0.6, 0.715, 0.004, 0.03)
    for s in (-1, 1):
        a, b = sorted((s * 0.48, s * 0.98))
        p.box('formica', a, b, 0.0, 0.4, 0.004, Lz)
        p.cham('booth', a, b, 0.4, 0.52, 0.01, Lz - 0.02, 0.04)
        c, d = sorted((s * 0.86, s * 0.98))
        for k in range(4):                                                                              # encosto capitonê em gomos
            z0 = 0.01 + k * (Lz - 0.03) / 4; z1 = z0 + (Lz - 0.03) / 4
            p.hull('booth', [(xx, y, z) for (xx, y) in ((s * 0.98, 0.52), (s * 0.98, 1.12), (s * 0.84, 0.54), (s * 0.88, 1.1)) for z in (z0 + 0.01, z1 - 0.01)] + [(s * 0.82, 0.82, (z0 + z1) / 2)])
        e, f = sorted((s * 0.98, s * 1.04))
        p.cham('formica', e, f, 0.0, 1.18, 0.004, Lz + 0.02, 0.008); p.box('steel', e - 0.004, f + 0.004, 1.16, 1.19, 0.008, Lz + 0.024)
    return p
def pendant(drop=1.3):
    p = Piece(); p.cyl('steel', 0.06, -0.03, 0.0, 0, 0, 10); p.cyl('dark', 0.004, -drop + 0.25, -0.03, 0, 0, 6)
    lathe(p, 'red', [(0.03, -drop + 0.25), (0.06, -drop + 0.22), (0.2, -drop + 0.04), (0.23, -drop)], sec=16)
    p.sphere('lamp_glass', 0.07, 0, -drop + 0.05, 0, 1)
    return p
def menu_header(Ln):
    """Sanca sobre o balcao (pivo: ponta x0, eixo da parede dos banheiros + 0,14, no piso; vai para +X) com 4 quadros de cardapio
    iluminados sem texto: icones abstratos de lanche, copo e batatas e barras de preco em branco."""
    p = Piece(); zf = 0.08; ya, yb = 2.45, H0 - 0.005
    p.box('plaster', 0.0, Ln, ya, yb, -0.04, zf); p.box('trim', 0.0, Ln, ya - 0.02, ya, -0.05, zf + 0.01)
    n = 4; w = (Ln - 0.6) / n
    for i in range(n):
        x0 = 0.3 + i * w + 0.05; x1 = x0 + w - 0.1; y0, y1 = 2.55, 3.3
        p.box('accent', x0, x1, y0, y1, zf, zf + 0.03); p.box('menu', x0 + 0.04, x1 - 0.04, y0 + 0.04, y1 - 0.04, zf + 0.03, zf + 0.035)
        cw = (x1 - x0 - 0.12) / 3
        for c in range(3):
            cx = x0 + 0.06 + (c + 0.5) * cw; cy = 3.02
            p.box('menu_lit', cx - cw / 2 + 0.02, cx + cw / 2 - 0.02, 2.88, 3.24, zf + 0.035, zf + 0.04)
            kind = (i + c) % 3; zi = zf + 0.04
            if kind == 0:
                ext(p, 'bun', Point(cx, cy + 0.06).buffer(0.11, 12).intersection(sbox(cx - 1, cy + 0.06, cx + 1, cy + 1)), zi, zi + 0.004)
                p.box('lettuce', cx - 0.11, cx + 0.11, cy + 0.025, cy + 0.06, zi, zi + 0.004); p.box('patty', cx - 0.11, cx + 0.11, cy - 0.03, cy + 0.025, zi, zi + 0.004)
                p.box('bun', cx - 0.1, cx + 0.1, cy - 0.07, cy - 0.03, zi, zi + 0.004)
            elif kind == 1:
                ext(p, 'red', Polygon([(cx - 0.08, cy + 0.12), (cx + 0.08, cy + 0.12), (cx + 0.06, cy - 0.1), (cx - 0.06, cy - 0.1)]), zi, zi + 0.004)
                p.box('cup_w', cx - 0.085, cx + 0.085, cy + 0.12, cy + 0.15, zi, zi + 0.004); p.box('menu', cx + 0.02, cx + 0.03, cy + 0.15, cy + 0.22, zi, zi + 0.004)
            else:
                for k in range(5): p.box('cheese', cx - 0.07 + k * 0.032, cx - 0.05 + k * 0.032, cy - 0.02, cy + 0.12 + 0.02 * (k % 2), zi, zi + 0.004)
                ext(p, 'red', Polygon([(cx - 0.09, cy + 0.02), (cx + 0.09, cy + 0.02), (cx + 0.07, cy - 0.1), (cx - 0.07, cy - 0.1)]), zi + 0.004, zi + 0.008)
            for r in range(3): p.box('paint_w', cx - cw / 2 + 0.05, cx + cw / 2 - 0.05 - 0.08 * (r % 2), 2.62 + r * 0.07, 2.65 + r * 0.07, zf + 0.035, zf + 0.039)
    p.box('steel', 0.2, Ln - 0.2, 3.36, 3.4, zf, zf + 0.12); p.box('lamp_glass', 0.22, Ln - 0.22, 3.355, 3.36, zf + 0.02, zf + 0.11)
    return p
def service_counter(Ln):
    """Balcao de atendimento (pivo: ponta x0, frente em z = 0, no piso; fundo em z = -0,6): frente de ladrilho vermelho com faixa
    amarela e rodape recuado, tampo de inox, 3 caixas registradoras sem texto, porta-guardanapos, bandejas e prateleira por dentro."""
    p = Piece(); d = 0.6
    p.box('dark', 0.02, Ln - 0.02, 0.0, 0.1, -d + 0.03, -0.06)
    p.box('tile_r', 0.0, Ln, 0.1, 0.92, -d, 0.0)
    p.box('accent', 0.0, Ln, 0.62, 0.72, 0.0, 0.012)
    for i in range(1, int(Ln / 0.3)):
        x = i * Ln / int(Ln / 0.3); p.box('tile_w', x - 0.004, x + 0.004, 0.1, 0.62, 0.0, 0.004)
    p.cham('steel', -0.03, Ln + 0.03, 0.92, 0.96, -d - 0.02, 0.05, 0.006)
    p.box('steel', 0.04, Ln - 0.04, 0.5, 0.52, -d + 0.02, -0.25)
    for x in (0.9, Ln / 2, Ln - 0.9):
        p.cham('dark', x - 0.18, x + 0.18, 0.96, 1.02, -0.45, -0.15, 0.008); p.cyl('dark', 0.03, 1.02, 1.2, x, -0.38, 8)
        p.hull('dark', [(x + dx, 1.18 + dy, -0.38 + dz) for dx in (-0.16, 0.16) for (dy, dz) in ((0.0, -0.04), (0.24, 0.02), (0.0, 0.0), (0.24, 0.06))])
        p.hull('menu_lit', [(x + dx, 1.2 + dy, -0.38 + dz) for dx in (-0.13, 0.13) for (dy, dz) in ((0.0, 0.004), (0.2, 0.054))])
    for x in (2.0, Ln - 2.0):
        p.box('steel', x - 0.1, x + 0.1, 0.96, 1.16, -0.18, -0.06); p.box('cup_w', x - 0.08, x + 0.08, 1.0, 1.12, -0.061, -0.058)
    for k in range(6): p.cham('red', 0.15, 0.6, 0.96 + k * 0.022, 0.98 + k * 0.022, -0.5, -0.15, 0.004)
    return p
def drink_station():
    """Maquina de refrigerante sobre armario (pivo: encostada na parede, no piso; frente +Z): 6 bicos, bandeja, copos empilhados."""
    p = Piece()
    p.box('steel', 0.0, 1.2, 0.08, 0.9, 0.0, 0.6); p.box('dark', 0.04, 1.16, 0.0, 0.08, 0.03, 0.56)
    for x in (0.3, 0.9): p.box('steel', x - 0.002, x + 0.002, 0.12, 0.86, 0.6, 0.604)
    p.box('steel', 0.1, 1.1, 0.9, 1.65, 0.05, 0.45); p.box('red', 0.12, 1.08, 1.4, 1.62, 0.45, 0.46)
    for k in range(6):
        x = 0.2 + k * 0.16; p.box('steel', x - 0.04, x + 0.04, 1.25, 1.33, 0.45, 0.5); p.cyl('dark', 0.012, 1.2, 1.25, x, 0.48, 6)
        p.box(('tomato', 'cheese', 'lettuce', 'bun', 'red', 'patty')[k], x - 0.035, x + 0.035, 1.3, 1.36, 0.46, 0.462)
    p.box('dark', 0.12, 1.08, 0.9, 0.95, 0.3, 0.56); p.box('steel', 0.14, 1.06, 0.95, 0.96, 0.32, 0.54)
    for (x, n) in ((0.05, 7), (1.13, 5)):
        for k in range(n): lathe(p, 'cup_w', [(0.035, 1.65 + k * 0.03), (0.045, 1.65 + k * 0.03 + 0.1)], x, 0.25, 0.0, 10) if False else None
        lathe(p, 'cup_w', [(0.035, 1.65), (0.045, 1.65 + 0.12 + n * 0.02), (0.0, 1.65 + 0.12 + n * 0.02)], x + 0.0, 0.25, 0.0, 12)
    return p
def grill_line():
    """Linha de coccao (pivo: inicio, encostada na parede, no piso; frente +Z, vai para +X): chapa com espirrador e botoes,
    2 fritadeiras com cestos, estacao de escorrer com lampada, coifa de inox com filtros inclinados e duto ate o forro."""
    p = Piece(); d = 0.8; Ln = 2.9
    p.box('steel', 0.0, 1.2, 0.1, 0.85, 0.0, d); p.box('dark', 0.03, 1.17, 0.0, 0.1, 0.05, d - 0.05)
    p.box('dark', 0.03, 1.17, 0.85, 0.9, 0.05, d - 0.02); p.box('steel', 0.0, 1.2, 0.85, 1.15, 0.0, 0.06)
    for s in (0.0, 1.17): p.box('steel', s, s + 0.03, 0.9, 1.0, 0.06, d - 0.02)
    p.box('steel', 0.0, 1.2, 0.82, 0.85, d - 0.02, d + 0.04)
    for k in range(4): p.cyl('dark', 0.025, 0.65, 0.68, 0.18 + k * 0.28, d, 10) if False else p.box('dark', 0.15 + k * 0.28, 0.21 + k * 0.28, 0.6, 0.66, d, d + 0.03)
    for i, x0 in enumerate((1.25, 1.7)):
        p.box('steel', x0, x0 + 0.42, 0.0, 0.92, 0.02, d)
        p.box('dark', x0 + 0.04, x0 + 0.38, 0.86, 0.921, 0.1, d - 0.12)
        for xx in (x0 + 0.06, x0 + 0.22):
            p.box('steel', xx, xx + 0.14, 0.93, 1.05, 0.2, 0.42); seg_cyl(p, 'dark', (xx + 0.07, 1.0, 0.42), (xx + 0.07, 1.08, 0.7), 0.012, 6)
        p.box('dark', x0 + 0.05, x0 + 0.37, 0.4, 0.7, d, d + 0.005)
    p.box('steel', 2.15, Ln, 0.0, 0.9, 0.02, d); p.box('steel', 2.2, Ln - 0.05, 0.9, 0.93, 0.1, d - 0.05)
    p.box('cheese', 2.25, Ln - 0.1, 0.93, 0.98, 0.15, d - 0.1)
    p.box('steel', 2.2, Ln - 0.05, 1.5, 1.55, 0.2, 0.6); p.box('lamp_glass', 2.25, Ln - 0.1, 1.48, 1.5, 0.25, 0.55)
    for x in (2.25, Ln - 0.1): p.box('steel', x - 0.015, x + 0.015, 0.93, 1.5, 0.22, 0.25)
    # coifa
    yb, yt = 2.0, 2.6
    p.hull('steel', [(x, y, z) for x in (-0.1, Ln + 0.1) for (z, y) in ((0.0, yb), (0.0, yt), (1.1, yb), (1.1, yb + 0.25), (0.7, yt))])
    p.box('dark', -0.06, Ln + 0.06, yb - 0.002, yb + 0.001, 0.05, 1.05)
    for k in range(int(Ln / 0.5)):
        x = 0.05 + k * 0.5; p.hull('steel', [(xx, y, z) for xx in (x + 0.02, x + 0.46) for (z, y) in ((0.06, yb + 0.1), (0.06, yb + 0.12), (0.35, yb + 0.002), (0.37, yb + 0.002))])
    p.box('steel', 1.0, 1.6, yt, H0 - 0.005, 0.1, 0.6)
    return p
def prep_table():
    p = Piece(); L1, d = 1.8, 0.7
    p.cham('steel', 0.0, L1, 0.88, 0.92, 0.0, d, 0.006)
    for x in (0.04, L1 - 0.04):
        for z in (0.04, d - 0.04): p.cyl('steel', 0.02, 0.0, 0.88, x, z, 8)
    p.box('steel', 0.04, L1 - 0.04, 0.2, 0.22, 0.04, d - 0.04)
    p.box('wood', 0.2, 0.75, 0.92, 0.95, 0.15, 0.5); p.box('red', 1.0, 1.5, 0.92, 1.0, 0.2, 0.55)
    for k in range(3): p.box('steel', 0.1 + k * 0.55, 0.55 + k * 0.55, 0.22, 0.32, 0.12, 0.6)
    return p
def fridge():
    p = Piece(); L1, d, h = 1.4, 0.8, 2.0
    p.box('steel', 0.0, L1, 0.12, h, 0.0, d)
    for x in (0.03, L1 - 0.06): p.cyl('dark', 0.025, 0.0, 0.12, x + 0.015, d - 0.06, 8)
    for (x0, x1) in ((0.01, L1 / 2 - 0.005), (L1 / 2 + 0.005, L1 - 0.01)):
        p.cham('steel', x0, x1, 0.15, h - 0.25, d, d + 0.03, 0.004)
        xh = x1 - 0.06 if x0 < L1 / 2 else x0 + 0.06; seg_cyl(p, 'steel', (xh, 0.9, d + 0.08), (xh, 1.5, d + 0.08), 0.014, 8)
        for y in (0.95, 1.45): seg_cyl(p, 'steel', (xh, y, d + 0.03), (xh, y, d + 0.08), 0.01, 6)
    p.box('dark', 0.05, L1 - 0.05, h - 0.22, h - 0.04, d, d + 0.005)
    return p
def dt_counter():
    p = Piece(); L1, d = 2.0, 0.6
    p.box('steel', 0.0, L1, 0.1, 0.88, -d, 0.0); p.box('dark', 0.03, L1 - 0.03, 0.0, 0.1, -d + 0.03, -0.03)
    p.cham('steel', -0.02, L1 + 0.02, 0.88, 0.91, -d - 0.02, 0.02, 0.006)
    p.cham('dark', 1.2, 1.55, 0.91, 0.97, -0.58, -0.36, 0.008); p.hull('dark', [(x, y, z) for x in (1.22, 1.53) for (y, z) in ((0.97, -0.55), (1.2, -0.57), (0.97, -0.51), (1.2, -0.53))])
    p.box('menu_lit', 1.25, 1.5, 1.0, 1.18, -0.513, -0.51)
    return p
def trash_station():
    p = Piece(); L1, d = 1.0, 0.55
    p.box('wood', 0.0, L1, 0.0, 1.05, 0.0, d); p.cham('formica', -0.02, L1 + 0.02, 1.05, 1.09, -0.02, d + 0.02, 0.006)
    p.box('steel', 0.15, 0.85, 0.65, 0.85, d, d + 0.01); p.box('dark', 0.2, 0.8, 0.68, 0.82, d + 0.01, d + 0.012)
    p.box('wood', 0.05, 0.95, 1.3, 1.34, 0.0, 0.35); p.box('wood', 0.05, 0.09, 1.09, 1.3, 0.0, 0.35); p.box('wood', 0.91, 0.95, 1.09, 1.3, 0.0, 0.35)
    for k in range(4): p.cham('red', 0.2, 0.62, 1.09 + k * 0.022, 1.11 + k * 0.022, 0.05, 0.4, 0.004)
    return p
def toilet():
    p = Piece()
    lathe(p, 'porcelain', [(0.12, 0.0), (0.14, 0.1), (0.13, 0.25), (0.19, 0.38), (0.2, 0.4), (0.0, 0.4)], 0.0, 0.0, 0.0, 16)
    p.hull('porcelain', [(x * 0.19, 0.38, z) for x in (-1, 1) for z in (0.0, 0.3)] + [(0, 0.38, 0.42)] + [(x * 0.19, 0.4, z) for x in (-1, 1) for z in (0.0, 0.3)] + [(0, 0.4, 0.42)])
    p.cham('porcelain', -0.2, 0.2, 0.42, 0.44, -0.02, 0.44, 0.02)
    p.cham('porcelain', -0.22, 0.22, 0.42, 0.8, -0.22, -0.04, 0.02); p.cham('porcelain', -0.23, 0.23, 0.8, 0.84, -0.23, -0.03, 0.01)
    p.box('steel', 0.12, 0.18, 0.72, 0.74, -0.04, -0.01)
    return p
def sink():
    """Lavatorio de parede com espelho, torneira e porta-toalha (pivo: face da parede, no piso; frente +Z)."""
    p = Piece()
    p.cham('porcelain', -0.28, 0.28, 0.7, 0.85, 0.0, 0.45, 0.03); p.cyl('dark', 0.03, 0.849, 0.852, 0.0, 0.25, 10)
    p.cyl('steel', 0.02, 0.85, 1.0, 0.0, 0.07, 8); seg_cyl(p, 'steel', (0.0, 0.98, 0.07), (0.0, 0.98, 0.17), 0.012, 6)
    p.cyl('steel', 0.016, 0.3, 0.7, 0.0, 0.1, 8)
    p.box('steel', -0.33, 0.33, 1.15, 1.95, 0.0, 0.02); p.box('glass', -0.31, 0.31, 1.17, 1.93, 0.02, 0.025)
    p.box('steel', 0.42, 0.72, 1.0, 1.35, 0.0, 0.12)
    return p

# ============================================================================ placa, painel do drive-thru e moveis externos
def star(cx, cy, r1, r2, n=5, a0=math.pi / 2):
    return Polygon([(cx + (r1 if k % 2 == 0 else r2) * math.cos(a0 + k * math.pi / n), cy + (r1 if k % 2 == 0 else r2) * math.sin(a0 + k * math.pi / n)) for k in range(2 * n)])
def burger_sign():
    """Placa no poste (pivo: base, no chao): sapata, poste de aco, painel vermelho com borda amarela e estrelas (sem texto) e um
    hamburguer gigante no topo: pao com gergelim, alface, tomate, queijo derretido e carne."""
    p = Piece()
    p.cham('concrete', -0.5, 0.5, 0.0, 0.4, -0.5, 0.5, 0.02)
    lathe(p, 'steel', [(0.3, 0.4), (0.3, 0.44), (0.18, 0.5)], sec=16); p.cyl('steel', 0.16, 0.44, 6.62, 0, 0, 16)
    PY0, PY1, PW = 3.7, 5.0, 1.55
    p.cham('red', -PW, PW, PY0, PY1, -0.18, 0.18, 0.02)
    for z in (1, -1):
        za, zb = sorted((z * 0.18, z * 0.2))
        for (x0, x1, y0, y1) in ((-PW, PW, PY0, PY0 + 0.1), (-PW, PW, PY1 - 0.1, PY1), (-PW, -PW + 0.1, PY0 + 0.1, PY1 - 0.1), (PW - 0.1, PW, PY0 + 0.1, PY1 - 0.1)):
            p.box('accent', x0, x1, y0, y1, za, zb)
        q = Piece(); ext(q, 'cream', sbox(-PW + 0.16, PY0 + 0.16, PW - 0.16, PY1 - 0.16), 0.18, 0.192)
        ext(q, 'red', unary_union([star(x, (PY0 + PY1) / 2, 0.2, 0.08) for x in (-0.95, 0.0, 0.95)]), 0.192, 0.2)
        ext(q, 'accent', unary_union([sbox(-1.25, PY0 + 0.25, 1.25, PY0 + 0.32), sbox(-1.25, PY1 - 0.32, 1.25, PY1 - 0.25)]), 0.192, 0.198)
        p.merge(q, rot_y(0 if z > 0 else 180))
    yb = 6.6; R = 1.12
    lathe(p, 'bun', [(0.0, yb), (0.85, yb), (1.02, yb + 0.06), (1.1, yb + 0.18), (1.08, yb + 0.3), (0.0, yb + 0.32)], sec=32)
    y = yb + 0.32
    lathe(p, 'patty', [(0.0, y), (R, y), (R + 0.05, y + 0.06), (R + 0.05, y + 0.22), (R, y + 0.28), (0.0, y + 0.28)], sec=32)
    y += 0.28
    ch = [(sx * 0.82, y + 0.0, sz * 0.82) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * 0.82, y + 0.04, sz * 0.82) for sx in (-1, 1) for sz in (-1, 1)]
    ch += [(sx * 1.25, y - 0.14, 0.0) for sx in (-1, 1)] + [(0.0, y - 0.14, sz * 1.25) for sz in (-1, 1)] + [(sx * 1.25, y - 0.1, 0.0) for sx in (-1, 1)] + [(0.0, y - 0.1, sz * 1.25) for sz in (-1, 1)]
    cq = Piece(); cq.hull('cheese', ch); p.merge(cq, rot_y(45))
    y += 0.04
    lathe(p, 'tomato', [(0.0, y), (1.06, y), (1.06, y + 0.07), (0.0, y + 0.07)], sec=28)
    lathe(p, 'lettuce', [(0.0, y + 0.07), (1.16, y + 0.07), (1.2, y + 0.1), (1.16, y + 0.13), (0.0, y + 0.13)], sec=32)
    for k in range(20):
        a = 2 * math.pi * k / 20; p.sphere('lettuce', 0.08, 1.18 * math.cos(a), y + 0.08 + 0.03 * (k % 2), 1.18 * math.sin(a), 1)
    yt = y + 0.13
    prof = [(1.14 * math.sin(t), yt + 0.82 * math.cos(t)) for t in np.linspace(math.pi / 2, 0.0, 9)]
    lathe(p, 'bun', [(0.0, yt)] + prof, sec=32)
    rng = np.random.default_rng(7)
    for k in range(34):
        t = rng.uniform(0.25, 1.2); ph = rng.uniform(0, 2 * math.pi)
        x, yy, z = 1.14 * math.sin(t) * math.cos(ph), yt + 0.82 * math.cos(t), 1.14 * math.sin(t) * math.sin(ph)
        s_ = trimesh.creation.icosphere(subdivisions=1, radius=1.0); s_.apply_scale([0.05, 0.022, 0.03]); s_.apply_transform(rot_y(math.degrees(ph))); s_.apply_translation([x, yy, z]); p.add('seed', s_)
    return p
def dt_menu():
    """Painel de pedidos do drive-thru (pivo: base, no centro; frente +Z): 2 postes, caixa vermelha com moldura amarela, quadros
    iluminados com icones (sem texto) e barras de preco em branco, chapeu com friso e sapata de concreto."""
    p = Piece()
    p.cham('concrete', -1.1, 1.1, 0.0, 0.2, -0.3, 0.3, 0.02)
    for s in (-1, 1): p.box('steel', s * 0.8 - 0.05, s * 0.8 + 0.05, 0.2, 2.3, -0.05, 0.05)
    p.cham('red', -1.0, 1.0, 0.85, 2.35, -0.16, 0.1, 0.012)
    p.box('accent', -0.95, 0.95, 0.9, 2.3, 0.1, 0.11)
    p.box('menu', -0.9, 0.9, 0.95, 2.25, 0.11, 0.115)
    for r in range(3):
        for c in range(3):
            cx = -0.6 + c * 0.6; cy = 1.18 + r * 0.4
            p.box('menu_lit', cx - 0.27, cx + 0.27, cy - 0.17, cy + 0.17, 0.115, 0.12)
            k = (r + c) % 3; z = 0.12
            if k == 0:
                ext(p, 'bun', Point(cx - 0.12, cy + 0.02).buffer(0.08, 10).intersection(sbox(cx - 1, cy + 0.02, cx + 1, cy + 1)), z, z + 0.004)
                p.box('patty', cx - 0.2, cx - 0.04, cy - 0.03, cy + 0.02, z, z + 0.004); p.box('bun', cx - 0.19, cx - 0.05, cy - 0.07, cy - 0.03, z, z + 0.004)
            elif k == 1:
                ext(p, 'red', Polygon([(cx - 0.18, cy + 0.08), (cx - 0.06, cy + 0.08), (cx - 0.08, cy - 0.1), (cx - 0.16, cy - 0.1)]), z, z + 0.004)
            else:
                for j in range(4): p.box('cheese', cx - 0.19 + j * 0.03, cx - 0.17 + j * 0.03, cy - 0.04, cy + 0.08, z, z + 0.004)
                ext(p, 'red', Polygon([(cx - 0.2, cy), (cx - 0.07, cy), (cx - 0.09, cy - 0.1), (cx - 0.18, cy - 0.1)]), z + 0.004, z + 0.008)
            for j in range(2): p.box('paint_w', cx + 0.0, cx + 0.2 - 0.06 * j, cy + 0.02 - j * 0.07, cy + 0.05 - j * 0.07, z, z + 0.003)
    p.hull('redm', [(x, y, z) for x in (-1.12, 1.12) for (z, y) in ((-0.22, 2.4), (-0.22, 2.46), (0.36, 2.36), (0.36, 2.42))])
    p.box('accent', -1.13, 1.13, 2.3, 2.42, 0.36, 0.38)
    p.box('steel', -0.9, 0.9, 2.3, 2.34, 0.12, 0.2); p.box('lamp_glass', -0.88, 0.88, 2.295, 2.3, 0.13, 0.19)
    return p
def dt_speaker():
    p = Piece()
    p.cham('concrete', -0.3, 0.3, 0.0, 0.15, -0.3, 0.3, 0.015)
    p.cham('red', -0.18, 0.18, 0.15, 1.35, -0.14, 0.14, 0.012); p.box('accent', -0.185, 0.185, 1.2, 1.26, -0.145, 0.145)
    p.cham('dark', -0.13, 0.13, 0.9, 1.15, 0.14, 0.16, 0.006)
    for i in range(5):
        for j in range(4): p.cyl('steel', 0.012, 0.0, 0.004, -0.08 + i * 0.04, 0.0, 6) if False else p.box('steel', -0.09 + i * 0.045, -0.075 + i * 0.045, 0.95 + j * 0.05, 0.965 + j * 0.05, 0.16, 0.163)
    p.box('lamp_glass', -0.05, 0.05, 0.82, 0.86, 0.14, 0.15)
    p.hull('accent', [(x, y, z) for x in (-0.24, 0.24) for (z, y) in ((-0.2, 1.44), (-0.2, 1.48), (0.26, 1.36), (0.26, 1.4))])
    return p
def clearance_bar(L1=4.0):
    """Portico de altura na entrada da pista (pivo: centro, no chao): 2 postes amarelos com sapatas e barra listrada pendurada
    em correntes."""
    p = Piece(); y = 3.2
    for s in (-1, 1):
        x = s * L1 / 2
        p.cham('concrete', x - 0.25, x + 0.25, 0.0, 0.25, -0.25, 0.25, 0.015)
        p.cham('accent', x - 0.08, x + 0.08, 0.25, y + 0.1, -0.08, 0.08, 0.01)
        for k in range(5): p.box('dark', x - 0.082, x + 0.082, 0.5 + k * 0.5, 0.65 + k * 0.5, -0.082, 0.082)
    p.cham('accent', -L1 / 2 - 0.1, L1 / 2 + 0.1, y + 0.1, y + 0.2, -0.08, 0.08, 0.01)
    yb = 2.9; n = 10
    for k in range(n):
        x0 = -L1 / 2 + 0.15 + k * (L1 - 0.3) / n; x1 = x0 + (L1 - 0.3) / n
        p.box('accent' if k % 2 == 0 else 'dark', x0, x1, yb - 0.06, yb + 0.06, -0.06, 0.06)
    for x in (-L1 / 2 + 0.4, 0.0, L1 / 2 - 0.4):
        for k in range(4): seg_cyl(p, 'steel', (x, yb + 0.06 + k * 0.06, 0), (x, yb + 0.06 + (k + 1) * 0.06, 0), 0.008, 5)
    return p
def light_pole(h=7.0):
    p = Piece()
    p.cyl('concrete', 0.3, 0.0, 0.6, 0, 0, 16)
    p.hull('steel', [(sx * 0.09, 0.6, sz * 0.09) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * 0.05, h, sz * 0.05) for sx in (-1, 1) for sz in (-1, 1)])
    p.box('steel', -0.13, 0.13, 0.6, 0.66, -0.13, 0.13)
    for s in (-1, 1):
        p.box('steel', -0.03, 0.03, h - 0.12, h - 0.06, *sorted((0.0, s * 1.0)))
        p.cham('steel', -0.2, 0.2, h - 0.2, h - 0.04, *sorted((s * 0.95, s * 1.55)), 0.02)
        p.box('lamp_glass', -0.17, 0.17, h - 0.205, h - 0.2, *sorted((s * 0.98, s * 1.52)))
    p.cyl('steel', 0.06, h, h + 0.08, 0, 0, 10)
    return p
def bollard():
    p = Piece(); p.cyl('accent', 0.1, 0.0, 0.95, 0, 0, 14); p.sphere('accent', 0.1, 0, 0.95, 0, 1)
    for y in (0.7, 0.8): p.cyl('trim', 0.103, y, y + 0.04, 0, 0, 14)
    return p
def wheel_stop():
    p = Piece(); p.cham('concrete', -0.9, 0.9, 0.0, 0.12, -0.08, 0.08, 0.02)
    for s in (-1, 1): p.box('paint_y', *sorted((s * 0.9, s * 0.6)), 0.12, 0.122, -0.06, 0.06)
    return p
def bin_():
    p = Piece(); p.cham('red', -0.28, 0.28, 0.0, 1.0, -0.28, 0.28, 0.02)
    p.hull('red', [(sx * 0.31, 1.0, sz * 0.31) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * 0.2, 1.15, sz * 0.2) for sx in (-1, 1) for sz in (-1, 1)])
    p.box('dark', -0.15, 0.15, 0.85, 0.97, 0.28, 0.284); p.box('accent', -0.285, 0.285, 0.2, 0.26, -0.285, 0.285)
    return p
def tree(h=5.2, r=1.7, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.16, 0.0), (0.12, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)):
        seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65)
        p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    ext_y(p, 'mulch', Point(0, 0).buffer(0.8, 20), 0.0, 0.02)
    return p
def bush(r=0.5):
    p = Piece(); rng = np.random.default_rng(3)
    p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def planter():
    p = Piece(); p.cham('concrete', -0.6, 0.6, 0.0, 0.55, -0.3, 0.3, 0.02); p.box('mulch', -0.54, 0.54, 0.5, 0.551, -0.24, 0.24)
    rng = np.random.default_rng(11)
    for k in range(5): p.sphere('hedge', 0.2, -0.4 + k * 0.2, 0.62 + rng.uniform(0, 0.08), rng.uniform(-0.06, 0.06), 1)
    return p

# ============================================================================ terreno
SX0, SX1, SZ0, SZ1 = -12.0, 13.5, -12.0, 20.0
FOOT = unary_union([sbox(-HX, -HZ, HX, HZ), sbox(-4 - AW, HZ, -4 + AW, HZ + AD), sbox(-1.5, HZ, 1.5, HZ + 2.0)])
WALK_F = sbox(-6.8, HZ, 6.9, 9.4); WALK_W = sbox(-6.8, -HZ, -HX, HZ); STOOP = sbox(1.9, -6.1, 4.1, -HZ)
RAMP = sbox(-1.0, 9.4, 1.0, 10.6); PATIO = sbox(2.0, HZ, 6.9, 9.4)
PLANTER = sbox(HX, 0.6, 6.9, HZ)
ISL_E = sbox(10.6, SZ0, SX1, 17.6); LAWN_W = sbox(SX0, SZ0, -10.4, 17.6); LAWN_S = sbox(-10.4, SZ0, 10.6, -10.0); LI_W = sbox(-7.8, 9.6, -6.4, 14.6)
STREET = sbox(SX0, 17.6, SX1, SZ1).difference(sbox(-3.0, 17.6, 9.0, SZ1))
GRASS = unary_union([PLANTER, ISL_E, LAWN_W, LAWN_S, LI_W])
CONC = unary_union([WALK_F.difference(PATIO), WALK_W, STOOP, STREET]).difference(FOOT)
STALLS = [-6.4, -3.8, -1.2, 1.2, 3.8, 6.4]                       # linhas das vagas (2 vagas de cada lado da faixa de pedestres)
def paving(poly, y1, joints=1.5, mat='concrete', gap=0.006):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + gap, z + gap, x + joints - gap, z + joints - gap).intersection(poly)
            ext_y(p, mat, q, 0.0, y1)
    ext_y(p, 'dark', poly.buffer(-0.002), 0.0, y1 - 0.008)
    return p
def asphalt():
    p = Piece(); g = sbox(SX0, SZ0, SX1, SZ1)
    for h in (FOOT, WALK_F, WALK_W, STOOP, RAMP, GRASS, STREET): g = g.difference(h)
    ext_y(p, 'asphalt', g.buffer(-0.001, join_style=2), 0.0, 0.03)
    return p
def walks():
    """Calcadas de concreto com juntas (0,15 m, no nivel do piso), rampa de acesso com faixa tatil, patio de blocos."""
    p = paving(CONC, Y0)
    q = paving(PATIO.difference(FOOT), Y0, 0.4, 'paver', 0.004); p.merge(q)
    p.hull('concrete', [(x, y, z) for x in (-1.0, 1.0) for (z, y) in ((9.4, 0.0), (9.4, Y0), (10.6, 0.0), (10.6, 0.03))])
    for k in range(6):
        z = 10.0 + k * 0.1; yy = Y0 - (Y0 - 0.03) * (z - 9.4) / 1.2
        p.hull('paint_y', [(x, yy + dy - (Y0 - 0.03) * dz / 1.2, z + dz) for x in (-0.6, 0.6) for dz in (0.0, 0.05) for dy in (0.0, 0.004)])
    return p
def lawn():
    """Ilhas e faixas de grama com guia de concreto."""
    p = Piece(); inner = GRASS.buffer(-0.15, join_style=2)
    ext_y(p, 'grass', inner, 0.0, 0.13); ext_y(p, 'curb', GRASS.difference(inner).buffer(-0.001, join_style=2), 0.0, 0.16)
    return p
def arrow(x, z, ang, L1=2.4):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    pts = [(-L1 / 2, -0.12), (L1 / 2 - 0.7, -0.12), (L1 / 2 - 0.7, -0.4), (L1 / 2, 0.0), (L1 / 2 - 0.7, 0.4), (L1 / 2 - 0.7, 0.12), (-L1 / 2, 0.12)]
    return Polygon([(x + u * c - v * s, z + u * s + v * c) for (u, v) in pts])
def markings():
    """Pintura: linhas das vagas, faixa de pedestres, setas da pista do drive-thru e faixa de parada."""
    p = Piece(); y0, y1 = 0.03, 0.034; W_ = []; Y_ = []
    for x in STALLS:
        if abs(x) > 1.3: W_.append(sbox(x - 0.05, 10.0, x + 0.05, 14.6))
    for x in (-6.4, 1.2): W_.append(sbox(x, 14.5, x + 5.2, 14.6))
    for k in range(5): W_.append(sbox(-1.1, 10.8 + k * 0.75, 1.1, 11.2 + k * 0.75))
    W_ += [arrow(8.75, 6.0, -90), arrow(8.75, -6.5, -90), arrow(2.0, -7.6, 180), arrow(-6.0, -7.6, 180), arrow(-8.6, 2.0, 90), arrow(-9.1, 12.5, 90)]
    W_.append(sbox(6.95, 4.35, 10.5, 4.6))
    Y_.append(sbox(6.95, -0.6, 7.05, -3.4))
    ext_y(p, 'paint_w', unary_union(W_), y0, y1); ext_y(p, 'paint_y', unary_union(Y_), y0, y1)
    return p
def patio_fence():
    """Gradil do patio (coordenadas do terreno): mureta baixa, postes, corrimao e barras verticais."""
    p = Piece()
    def run(Ln):
        q = Piece(); n = max(1, int(round(Ln / 1.4)))
        for i in range(n + 1):
            x = i * Ln / n; q.box('iron', x - 0.03, x + 0.03, 0.0, 1.0, -0.03, 0.03); q.sphere('iron', 0.04, x, 1.03, 0.0, 1)
        q.box('iron', 0.0, Ln, 0.92, 0.96, -0.02, 0.02); q.box('iron', 0.0, Ln, 0.1, 0.13, -0.015, 0.015)
        for x in np.arange(0.12, Ln - 0.05, 0.12):
            if min(abs(x - i * Ln / n) for i in range(n + 1)) > 0.05: q.box('iron', x - 0.008, x + 0.008, 0.13, 0.92, -0.008, 0.008)
        return q
    along(p, run(4.3), 6.82, 5.05, 6.82, 9.32, Y0)
    along(p, run(3.42), 3.4, 9.32, 6.82, 9.32, Y0)
    return p

# ============================================================================ pecas
pieces = {
    'corner': corner(), 'hip': hip(), 'roof_flat': roof_flat(), 'hvac': hvac(), 'exhaust_fan': exhaust_fan(),
    'tower': tower(), 'annex': annex(), 'milkshake': milkshake(),
    'downspout': downspout(YE + 0.03, 0.365), 'downspout_w': downspout(YE + 0.03 - Y0, 0.365),
    'door_leaf_glass': door_leaf_glass(), 'door_leaf_back': door_back(0.88, 2.14), 'door_leaf_interior': door_interior(0.82, 2.06),
    'booth': booth(), 'cafe_table': table_set(4), 'table2': table_set(2, 0.32, False), 'pendant': pendant(1.4), 'pendant_s': pendant(0.55),
    'drink_station': drink_station(), 'grill_line': grill_line(), 'prep_table': prep_table(), 'fridge': fridge(), 'dt_counter': dt_counter(),
    'trash_station': trash_station(), 'toilet': toilet(), 'sink': sink(),
    'asphalt': asphalt(), 'walks': walks(), 'lawn': lawn(), 'markings': markings(), 'patio_fence': patio_fence(),
    'burger_sign': burger_sign(), 'dt_menu': dt_menu(), 'dt_speaker': dt_speaker(), 'clearance_bar': clearance_bar(3.9),
    'light_pole': light_pole(), 'bollard': bollard(), 'wheel_stop': wheel_stop(), 'bin': bin_(), 'planter': planter(),
    'umbrella_table_r': table_set(4, 0.4, False, 'canvas_r'), 'umbrella_table_y': table_set(4, 0.4, False, 'canvas_y'),
    'tree': tree(), 'tree_b': tree(4.4, 1.4, 'leaf2', 4), 'bush': bush(), 'player_scale_ref': player_ref()}
for k in ('plain', 'win', 'hwin', 'dt', 'bdoor', 'vent', 'louver', 'open_a', 'open_b', 'vest_l', 'vest_r'): pieces[f'w_{k}'] = wall(k)
for k in ('', 'a', 'b', 'tl', 'tr'): pieces['mans' + (f'_{k}' if k else '')] = mansard(k)

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
XM = [-5, -3, -1, 1, 3, 5]; ZM = [-4, -2, 0, 2, 4]
FRONT = {-5: 'open_a', -3: 'open_b', -1: 'vest_l', 1: 'vest_r', 3: 'win', 5: 'win'}
BACK = {-5: 'plain', -3: 'vent', -1: 'plain', 1: 'louver', 3: 'bdoor', 5: 'plain'}          # x do mundo
WEST = {-4: 'hwin', -2: 'plain', 0: 'plain', 2: 'win', 4: 'win'}
EAST = {-4: 'plain', -2: 'dt', 0: 'plain', 2: 'win', 4: 'win'}
for x in XM: put(f'w_{FRONT[x]}', x, Y0, HZ, 0, ['front', 'ext']); put(f'w_{BACK[x]}', x, Y0, -HZ, 180, ['back', 'ext'])
for z in ZM: put(f'w_{WEST[z]}', -HX, Y0, z, -90, ['left', 'ext']); put(f'w_{EAST[z]}', HX, Y0, z, 90, ['right', 'ext'])
for (x, z, ry) in ((HX, HZ, 0), (-HX, HZ, -90), (HX, -HZ, 90), (-HX, -HZ, 180)): put('corner', x, Y0, z, ry, ['ext']); put('hip', x, YE, z, ry, ['roof'])
# mansarda
for x in XM:
    nf = {-5: 'mans_a', 5: 'mans_b', -1: 'mans_tl', 1: 'mans_tr'}.get(x, 'mans'); nb = {-5: 'mans_b', 5: 'mans_a'}.get(x, 'mans')
    put(nf, x, YE, HZ, 0, ['roof']); put(nb, x, YE, -HZ, 180, ['roof'])
for z in ZM:
    put({4: 'mans_b', -4: 'mans_a'}.get(z, 'mans'), -HX, YE, z, -90, ['roof']); put({4: 'mans_a', -4: 'mans_b'}.get(z, 'mans'), HX, YE, z, 90, ['roof'])
put('roof_flat', 0, YE, 0, 0, ['roof'])
YR = YE + RISE + 0.02
put('hvac', -2.6, YR, -1.6, 0, ['roof']); put('hvac', 2.6, YR, 2.4, 0, ['roof'])
put('exhaust_fan', 1.6, YR, -3.4, 0, ['roof']); put('exhaust_fan', 0.4, YR, -3.4, 0, ['roof'])
for (x, z, ry, nm) in ((-5.75, -HZ, 180, 'downspout'), (5.75, -HZ, 180, 'downspout'), (-HX, 0.2, -90, 'downspout_w'), (HX, 0.2, 90, 'downspout')):
    put(nm, x, 0.0 if nm == 'downspout' else Y0, z, ry, ['ext'])
# torre e anexo
put('tower', 0, Y0, HZ, 0, ['front', 'ext']); put('annex', -4.0, Y0, HZ, 0, ['front', 'ext'])
put('milkshake', -3.2, Y0 + 2.7, HZ + 1.6, 0, ['front', 'ext'])
put('door_leaf_glass', -0.86, Y0 + 0.012, HZ + 2.0 - 0.11, 0, ['front', 'ext'], door=95)
put('door_leaf_glass', 0.86, Y0 + 0.012, HZ + 2.0 - 0.11, 180, ['front', 'ext'], door=-95)
hx, hz = hinge(3.0, -HZ, 180, -0.44, -0.12); put('door_leaf_back', hx, Y0 + 0.012, hz, 180, ['back', 'ext'], door=90)
# interior: pisos e forros
for x in XM:
    for z in ZM:
        tr = (T if x == -5 else 0.0, T if x == 5 else 0.0, T if z == -4 else 0.0, T if z == 4 else 0.0)
        kind = 'kit' if (z < 0 and x >= 1) else ('half' if (z < 0 and x == -1) else 'dine')
        ck = 'ceill' if ((x + 5) // 2 + (z + 4) // 2) % 2 == 0 else 'ceil'
        for kd, y, tg in ((kind, Y0, ['floor0']), (ck, YE, ['floor0', 'roof'])):
            sfx = ('_e' + '_'.join(str(int(round(t * 100))) for t in tr)) if any(tr) else ''
            nm = f'floor_{kd}{sfx}'
            if nm not in pieces: pieces[nm] = floor_tile(kd, tr)
            put(nm, x, y, z, 0, tg)
HI = H0 - 0.005
pieces['pw_rest'] = run_wall(XI + XK + 0.06, HI, doors=(-4.6 + XI, -2.2 + XI))
put('pw_rest', -XI, Y0, ZR, 0, ['floor0'])
for c in (-4.6, -2.2):
    hx, hz = hinge(c, ZR, 0, -0.41, 0); put('door_leaf_interior', hx, Y0 + 0.01, hz, 0, ['floor0'], door=90)
LK = round(ZI + (ZR - 0.06), 3)
pieces['pw_kit'] = run_wall(LK, HI, end_gap=(0.0, 0.0)); put('pw_kit', XK, Y0, -ZI, -90, ['floor0'])
pieces['pw_div'] = run_wall(LK, HI); put('pw_div', XD, Y0, -ZI, -90, ['floor0'])
LH = XI - XK; pieces['menu_header'] = menu_header(LH); put('menu_header', XK, Y0, 0.0, 0, ['floor0'])
LC = 5.0 - (XK + 0.06); pieces['service_counter'] = service_counter(LC); put('service_counter', XK + 0.06, Y0, 0.0, 0, ['floor0'])
put('drink_station', XK + 0.06, Y0, -1.95, 90, ['floor0'])
put('grill_line', -0.6, Y0, -ZI, 0, ['floor0'])
put('fridge', 4.25, Y0, -ZI, 0, ['floor0'])
put('prep_table', 0.6, Y0, -2.9, 0, ['floor0'])
put('dt_counter', XI, Y0, -1.0, 90, ['floor0'])
for (x, z, ry) in ((-XI, 1.15, 90), (-XI, 3.65, 90), (XI, 3.65, -90)): put('booth', x, Y0, z, ry, ['floor0'])
for (x, z) in ((-2.1, 2.5), (2.4, 2.4)): put('cafe_table', x, Y0, z, 0, ['floor0'])
put('trash_station', -3.9, Y0, ZR + 0.06, 0, ['floor0'])
for (x, z) in ((-5.1, 1.15), (-5.1, 3.65), (5.1, 3.65), (-2.1, 2.5), (2.4, 2.4)): put('pendant', x, YE - 0.03, z, 0, ['floor0'])
for (x, z) in ((-4.8, 6.5), (-3.0, 6.9)): put('table2', x, Y0, z, 0, ['floor0']); put('pendant_s', x, Y0 + OPEN_H - 0.03, z, 0, ['floor0'])
put('toilet', -5.0, Y0, -ZI + 0.24, 0, ['floor0']); put('toilet', -2.2, Y0, -ZI + 0.24, 0, ['floor0'])
put('sink', -XI, Y0, -1.6, 90, ['floor0']); put('sink', XD + 0.06, Y0, -1.6, 90, ['floor0'])
# terreno
for nm in ('asphalt', 'walks', 'lawn', 'markings', 'patio_fence'): put(nm, 0, 0, 0, 0, ['site'])
put('burger_sign', 12.0, 0.16, 10.5, -20, ['site'])
put('dt_menu', 6.45, 0.13, 3.0, 90, ['site']); put('dt_speaker', 6.5, 0.13, 1.4, 90, ['site'])
put('clearance_bar', 8.75, 0.0, 8.9, 0, ['site'])
for (x, z) in ((-7.1, 12.1), (11.4, -4.0), (11.4, 6.0), (-11.2, 2.0), (-11.2, -8.0)): put('light_pole', x, 0.13, z, 0, ['site'])
for (x, z) in ((6.35, -0.6), (6.35, -3.4), (-5.0, 9.15), (-3.0, 9.15)): put('bollard', x, 0.03 if x > 6 else Y0, z, 0, ['site'])
for x in (-5.1, -2.5, 2.5, 5.1): put('wheel_stop', x, 0.03, 10.25, 0, ['site'])
for (x, z) in ((1.9, 7.6), (6.4, 5.6)): put('bin', x, Y0, z, 0, ['site'])
put('planter', 4.2, Y0, 5.45, 0, ['site'])
put('umbrella_table_r', 3.4, Y0, 7.3, 0, ['site']); put('umbrella_table_y', 5.6, Y0, 7.9, 0, ['site'])
for (x, z, k) in ((-11.1, -5.0, 'tree'), (-11.1, 9.0, 'tree_b'), (-11.1, 15.5, 'tree'), (12.1, -8.0, 'tree_b'), (12.1, 1.5, 'tree'), (12.1, 15.0, 'tree_b'),
                  (-6.0, -11.0, 'tree'), (4.0, -11.0, 'tree_b')): put(k, x, 0.13, z, 0, ['site'])
for (x, z) in ((6.45, 0.95), (6.45, 4.6), (-7.1, 10.3), (-7.1, 13.9), (11.0, 13.5), (-10.9, -10.5)): put('bush', x, 0.13, z, 0, ['site'])
put('player_scale_ref', 0.0, 0.03, 12.0); put('player_scale_ref', 0.6, Y0, 2.0, 0, ['floor0'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_height': H0, 'wall_thickness': T, 'floor_raise': RAISE,
                       'building': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 1, 'wall_top': YE, 'mansard_top': YE + RISE, 'mansard_pitch_deg': ANG,
                                    'tower': {'x': [-1.5, 1.5], 'z': [HZ, HZ + 2.0], 'wall_top': Y0 + TWH},
                                    'annex': {'x': [-4 - AW, -4 + AW], 'z': [HZ, HZ + AD], 'roof_top': Y0 + 2.78}},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1], 'walk_level': Y0, 'drive_thru_window': {'x': HX, 'z': -2.0}},
                       'roof': '60 deg shingle mansard with hips around a flat membrane roof; pyramid standing-seam roof on the entry tower',
                       'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
              'placements': L}
    json.dump(layout, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc2 = trimesh.Scene(); tot = 0
    for e in L:
        T_ = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T_[:3, 3] = e['pos']
        sc = pieces[e['piece']].scene(e['piece'])
        for nm, g in sc.geometry.items(): g2 = g.copy(); g2.apply_transform(T_); sc2.add_geometry(g2); tot += len(g2.faces)
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:10]: print(f'  {n:30s} {p.tris():6d} tri')
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
