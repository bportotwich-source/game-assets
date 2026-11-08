"""Kit 35: parque com casa de barcos, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Pavilhao de madeira de 8 x 10 m em estilo 'stick': paredes de tabua e mata-junta verde sobre embasamento de pedra, janelas de
guilhotina com frontaozinho, portas-balcao para a varanda, telhado de 45 graus de telhas de madeira com cumeeira, calhas e
condutores, lanternim com venezianas e cata-vento, chamine de tijolo, frontao com escamas e tesoura decorativa, chapeu sobre a
porta dupla. Varanda coberta de chapa com mao-francesa e frisos de fusos, deck sobre o lago com guarda-corpo e escadas.
Dentro: salao com balcao de cafe e mesas, deposito de barcos com prateleira de canoas e escritorio.
Parque: lago de 2 lobos com borda de pedra, ponte em arco de pedra com balaustres e lampioes, praca com chafariz de 2 tacas,
balaustrada, caminhos de saibro com guias, gradil de ferro em pilares de pedra com portao, lampioes, bancos, arvores, arbustos,
pedestal com urna, barcos a remo e mesas com ombrelones no deck.
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
configurar(cores={'boards': (58, 88, 70), 'trim': (232, 222, 190), 'frame': (232, 222, 190), 'sash': (238, 230, 204), 'stone': (150, 142, 128),
                  'shingles': (112, 80, 58), 'ridge': (74, 62, 54), 'scale': (190, 140, 76), 'door': (110, 64, 40), 'door_int': (226, 214, 186),
                  'floor': (170, 126, 84), 'plaster': (236, 228, 206), 'ceil': (214, 192, 150), 'deck': (152, 112, 76), 'vroof': (66, 96, 80),
                  'brick': (148, 74, 56), 'cill': (190, 184, 170), 'copper': (98, 152, 132), 'water': (64, 118, 138), 'rimstone': (156, 150, 136),
                  'bstone': (176, 168, 150), 'carve': (206, 198, 180), 'paving': (196, 186, 164), 'gravel': (204, 184, 148), 'edge': (150, 120, 96),
                  'grass': (98, 144, 70), 'hedge': (64, 104, 52), 'leaf': (86, 130, 62), 'leaf2': (110, 146, 70), 'bark': (96, 72, 52),
                  'mulch': (88, 64, 46), 'concrete': (180, 176, 168), 'canvas_r': (192, 62, 50), 'canvas_w': (236, 232, 220),
                  'canvas_y': (226, 172, 62), 'boat': (156, 98, 60), 'boat_in': (196, 160, 112), 'boat_g': (50, 96, 82), 'wood': (150, 104, 66),
                  'menu': (40, 46, 42), 'gutter': (74, 66, 58), 'flash': (120, 124, 126), 'soil': (90, 70, 50)},
           texturas={'boards': 'paint', 'stone': 'stone2', 'shingles': 'shingles', 'scale': 'paint', 'floor': 'planks', 'plaster': 'plaster',
                     'ceil': 'planks', 'deck': 'deck', 'brick': 'brick', 'rimstone': 'stone2', 'bstone': 'stone', 'carve': 'plaster',
                     'paving': 'stone', 'gravel': 'render', 'grass': 'render', 'concrete': 'render', 'wood': 'planks'},
           out=OUT)
D.METAL.update({'vroof', 'copper', 'flash'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.2; RAISE = 0.45; H0 = 3.4
Y0 = RAISE; YE = Y0 + H0                            # piso e frechal
HX = 4.0; HZ = 5.0                                  # pavilhao: x de -4 a 4, z de -5 a 5, frente para +Z
ANG = 45.0; KR = math.tan(math.radians(ANG)); CS = math.cos(math.radians(ANG))
SX = HX; RIDGE = SX * KR
OVE = 0.45; OVF = 0.35                              # beiral nas laterais e avanco nas empenas
TV = 0.07; BUMP = 0.02
configurar_telhado(TV, BUMP, ANG)
FT = 0.2; FR = 0.3                                  # testeira (water table) no pe e friso no topo das paredes
VD = 2.4; DD = 5.5; DZ0, DZ1 = -4.0, 3.0            # varanda (profundidade) e deck (ate x = -DD, de DZ0 a DZ1), medidos da parede oeste
VK = 0.18; VY = 2.75                                # caimento e altura (sobre o piso) da cobertura da varanda junto a parede
vr = lambda x: VY + VK * x                          # face de baixo da cobertura da varanda (x local, negativo para fora)
XI = HX - T; ZI = HZ - T
ZP1 = -2.6                                          # parede entre o salao e os fundos
XP2 = 1.2                                           # parede entre o deposito e o escritorio

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

# ============================================================================ paredes de tabua e mata-junta
WT_PROF = [(0.0, -0.02), (0.035, -0.02), (0.035, FT - 0.03), (0.0, FT)]           # testeira do pe com chanfro (pingadeira)
STONE_PROF = lambda y0: [(0.0, y0), (0.04, y0), (0.04, -0.02), (0.0, -0.02)]
FRIEZE_PROF = [(0.0, H0 - FR), (0.03, H0 - FR), (0.03, H0 - 0.06), (0.05, H0 - 0.05), (0.05, H0), (0.0, H0)]
def wall_core(p, y0, top, holes):
    """Parede: pedra ate o piso, tabuas pintadas por fora e gesso por dentro (para 5 mm abaixo do topo)."""
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, 0.0, top - 0.005, top] + [max(y0, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'stone'
        if k == 0: return None if ys[j] >= top - 0.0051 else 'plaster'
        return 'boards'
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
def battens(p, holes, ya=FT, yb=H0 - FR, x0=-W / 2, x1=W / 2):
    """Mata-juntas de 6 cm a cada 1/3 m, interrompidas nas guarnicoes (holes = retangulos (x0, x1, y0, y1))."""
    for k in range(6):
        xc = x0 + (k + 0.5) * (x1 - x0) / 6; a, b = xc - 0.03, xc + 0.03
        segs = [(ya, yb)]
        for (hx0, hx1, hy0, hy1) in holes:
            if b > hx0 and a < hx1: segs = [s for (c, d) in segs for s in ((c, min(d, hy0)), (max(c, hy1), d)) if s[1] - s[0] > 0.02]
        for (c, d) in segs: p.cham('boards', a, b, c, d, 0.0, 0.022, 0.006)
OW, OY0, OY1 = 1.0, 0.8, 2.65                      # janela de guilhotina
def dh_window(p, ow=OW, oy0=OY0, oy1=OY1, hood=True):
    """Janela de guilhotina 2 sobre 2 no vao (face externa em z = 0): marco, folha de baixo e de cima com pinazio, peitoril com
    pingadeira, guarnicoes lisas, verga com frontaozinho sobre misulas recortadas. Devolve o retangulo coberto (para os mata-juntas)."""
    x = ow / 2; f = 0.05; zf0, zf1 = -0.16, -0.05
    p.box('frame', -x, -x + f, oy0, oy1, zf0, zf1); p.box('frame', x - f, x, oy0, oy1, zf0, zf1)
    p.box('frame', -x + f, x - f, oy1 - f, oy1, zf0, zf1); p.box('frame', -x + f, x - f, oy0, oy0 + 0.03, zf0, zf1)
    ym = (oy0 + oy1) / 2
    for (c, d, za, zb) in ((oy0 + 0.03, ym + 0.02, -0.105, -0.065), (ym - 0.02, oy1 - f, -0.145, -0.105)):
        sash(p, -x + f, x - f, c, d, za, zb, bot=0.07 if c < ym else 0.05)
        p.box('glass', -x + f + 0.046, x - f - 0.046, c + 0.045, d - 0.045, (za + zb) / 2 - 0.003, (za + zb) / 2 + 0.003)
        p.cham('sash', -0.014, 0.014, c + 0.045, d - 0.045, za + 0.006, zb - 0.006, 0.004)
    p.box('brass', -0.05, 0.05, ym + 0.02, ym + 0.035, -0.07, -0.06)
    # peitoril e avental
    prof_x(p, 'trim', -x - 0.14, x + 0.14, [(zf0 + 0.005, oy0 - 0.05), (0.07, oy0 - 0.05), (0.075, oy0 - 0.035), (0.075, oy0 - 0.02), (0.0, oy0 + 0.004), (zf0 + 0.005, oy0 + 0.004)])
    p.box('trim', -x - 0.08, x + 0.08, oy0 - 0.2, oy0 - 0.05, 0.0, 0.025)
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x + 0.1))); p.box('trim', a, b, oy0 - 0.05, oy1, 0.0, 0.03)
    p.box('trim', -x - 0.1, x + 0.1, oy1, oy1 + 0.16, 0.0, 0.03)
    if not hood:
        prof_x(p, 'trim', -x - 0.13, x + 0.13, [(0.0, oy1 + 0.16), (0.06, oy1 + 0.16), (0.06, oy1 + 0.19), (0.04, oy1 + 0.21), (0.0, oy1 + 0.215)])
        return (-x - 0.13, x + 0.13, oy0 - 0.2, oy1 + 0.215)
    # frontaozinho (hood) sobre misulas
    yh = oy1 + 0.16; tri = Polygon([(-x - 0.2, yh + 0.06), (x + 0.2, yh + 0.06), (0.0, yh + 0.36)])
    p.cham('trim', -x - 0.2, x + 0.2, yh, yh + 0.06, -0.005, 0.09, 0.008)
    ext(p, 'trim', tri, 0.0, 0.05); ext(p, 'boards', tri.buffer(-0.05, join_style=2), 0.05, 0.06)
    for s in (-1, 1):
        a, b = sorted((s * (x + 0.2), 0.0))
        p.hull('trim', [(xx, yh + 0.06 + (x + 0.2 - abs(xx)) * 0.3 / (x + 0.2) + dy, z) for xx in (a, b) for dy in (0.0, 0.04) for z in (-0.005, 0.1)])
    for s in (-1, 1):
        xx = s * (x + 0.05)
        p.hull('trim', [(xx + dx, y, z) for dx in (-0.025, 0.025) for (z, y) in ((0.03, yh), (0.1, yh), (0.03, yh - 0.22))])
    return (-x - 0.1, x + 0.1, oy0 - 0.2, yh + 0.36)
def door_frame(p, a, b, oh, transom=None):
    """Marco de porta no vao (x de a a b, ate oh), com bandeira opcional na altura 'transom'."""
    p.box('frame', a, a + 0.06, 0.0, oh, -0.17, -0.05); p.box('frame', b - 0.06, b, 0.0, oh, -0.17, -0.05)
    p.box('frame', a + 0.06, b - 0.06, oh - 0.06, oh, -0.17, -0.05)
    if transom:
        p.box('frame', a + 0.06, b - 0.06, transom - 0.04, transom + 0.02, -0.17, -0.05)
        p.box('glass', a + 0.06, b - 0.06, transom + 0.02, oh - 0.06, -0.113, -0.107)
        n = max(1, int(round((b - a) / 0.3)))
        for i in range(1, n): xx = a + 0.06 + i * (b - a - 0.12) / n; p.box('frame', xx - 0.012, xx + 0.012, transom + 0.02, oh - 0.06, -0.125, -0.095)
def casing(p, a, b, oh, sides=(True, True)):
    for (on, xa, xb) in ((sides[0], a - 0.1, a), (sides[1], b, b + 0.1)):
        if on: p.box('trim', xa, xb, FT, oh, 0.0, 0.03)
    p.box('trim', a - (0.1 if sides[0] else 0.0), b + (0.1 if sides[1] else 0.0), oh, oh + 0.16, 0.0, 0.03)
    p.cham('trim', a - (0.12 if sides[0] else 0.0), b + (0.12 if sides[1] else 0.0), oh + 0.16, oh + 0.21, 0.0, 0.07, 0.008)
FDW, FDH = 1.44, 2.4                                # porta-balcao (2 folhas)
MDH, MTR = 2.85, 2.4                                # porta principal: vao ate 2,85, bandeira a partir de 2,4; meio-vao de 0,8
def wall(kind='plain', y0=-RAISE):
    """Modulo de 2 m (pivo: face externa, cota do piso). kind: plain, win, fdoor (porta-balcao), bdoor (servico), door_l / door_r
    (metades da porta dupla da frente)."""
    p = Piece(); top = H0; holes = []; gaps = []; cover = []
    if kind == 'win': holes = [(-OW / 2, OW / 2, OY0, OY1)]
    if kind == 'vwin': holes = [(-OW / 2, OW / 2, OY0, 2.5)]
    if kind == 'fdoor': holes = [(-FDW / 2, FDW / 2, 0.0, FDH)]; gaps = [(-FDW / 2, FDW / 2)]
    if kind == 'bdoor': holes = [(-0.5, 0.5, 0.0, 2.2)]; gaps = [(-0.5, 0.5)]
    if kind in ('door_l', 'door_r'):
        s = 1 if kind == 'door_l' else -1; a, b = sorted((s * 0.2, s * 1.0)); holes = [(a, b, 0.0, MDH)]; gaps = [(a, b)]
    wall_core(p, y0, top, holes)
    if kind == 'win': cover.append(dh_window(p))
    if kind == 'vwin': cover.append(dh_window(p, oy1=2.5, hood=False))
    if kind == 'fdoor':
        door_frame(p, -FDW / 2, FDW / 2, FDH); casing(p, -FDW / 2, FDW / 2, FDH); cover.append((-FDW / 2 - 0.12, FDW / 2 + 0.12, 0.0, FDH + 0.21))
    if kind == 'bdoor':
        door_frame(p, -0.5, 0.5, 2.2); casing(p, -0.5, 0.5, 2.2); cover.append((-0.62, 0.62, 0.0, 2.41))
    if kind in ('door_l', 'door_r'):
        s = 1 if kind == 'door_l' else -1; a, b = sorted((s * 0.2, s * 1.0))
        inner = b if s > 0 else a                      # lado do eixo da porta (sem guarnicao, continua no outro modulo)
        p.box('frame', *sorted((s * 0.2, s * 0.26)), 0.0, MDH, -0.17, -0.05)
        p.box('frame', a if s < 0 else a + 0.06, b if s > 0 else b - 0.06, MDH - 0.06, MDH, -0.17, -0.05)
        p.box('frame', a if s < 0 else a + 0.06, b if s > 0 else b - 0.06, MTR - 0.04, MTR + 0.02, -0.17, -0.05)
        p.box('glass', a if s < 0 else a + 0.06, b if s > 0 else b - 0.06, MTR + 0.02, MDH - 0.06, -0.113, -0.107)
        for xx in (s * 0.47, s * 0.73): p.box('frame', xx - 0.012, xx + 0.012, MTR + 0.02, MDH - 0.06, -0.125, -0.095)
        xa, xb = sorted((s * 0.1, s * 0.2)); p.box('trim', xa, xb, FT, MDH, 0.0, 0.03)
        xa, xb = sorted((s * 0.1, s * 1.0)); p.box('trim', xa, xb, MDH, MDH + 0.16, 0.0, 0.03)
        xa, xb = sorted((s * 0.08, s * 1.0)); p.cham('trim', xa, xb, MDH + 0.16, MDH + 0.21, 0.0, 0.07, 0.008) if False else prof_x(p, 'trim', xa, xb, [(0.0, MDH + 0.16), (0.07, MDH + 0.16), (0.07, MDH + 0.2), (0.0, MDH + 0.21)])
        cover.append((min(s * 0.08, s * 1.0), max(s * 0.08, s * 1.0), 0.0, MDH + 0.21))
    # soleiras
    for (a, b) in gaps: p.box('trim', a + (0.001 if abs(a + 1) < 1e-6 else 0.0), b - (0.001 if abs(b - 1) < 1e-6 else 0.0), -0.03, 0.012, -T + 0.004, 0.05)
    # testeira do pe (para nas portas), pedra saliente, friso do topo, mata-juntas
    segs = [(-W / 2, W / 2)]
    for (a, b) in gaps: segs = [s_ for (c, d) in segs for s_ in ((c, min(d, a - (0.1 if kind not in ('door_l', 'door_r') else 0.1))), (max(c, b + 0.1), d)) if s_[1] - s_[0] > 1e-3]
    if kind in ('door_l', 'door_r'):
        s = 1 if kind == 'door_l' else -1; a, b = sorted((s * -1.0, s * 0.1)); segs = [(a, b)]
    for (a, b) in segs: prof_x(p, 'trim', a, b, WT_PROF)
    prof_x(p, 'stone', -W / 2, W / 2, STONE_PROF(y0))
    prof_x(p, 'trim', -W / 2, W / 2, FRIEZE_PROF)
    battens(p, cover)
    return p
def corner():
    """Quina (pivo: quina externa, cota do piso; paredes em -X e -Z): nucleo, pedra, testeira e friso em meia-esquadria, cantoneiras."""
    p = Piece(); e = 0.004
    p.box('boards', -T + 0.004, e, -RAISE + 0.003, H0 - 0.004, -T + 0.004, e)
    mitre_pair(p, 'stone', STONE_PROF(-RAISE)); mitre_pair(p, 'trim', WT_PROF); mitre_pair(p, 'trim', FRIEZE_PROF)
    p.box('trim', -0.15, 0.032, FT, H0 - FR, 0.0, 0.032); p.box('trim', 0.0, 0.032, FT, H0 - FR, -0.15, 0.0)
    return p

# ============================================================================ frontoes, chamine e lanternim
def scale_field(p, poly, y0, mat='scale'):
    """Escamas de peixe: fiadas de 12 cm com a borda de baixo em meias-luas, alternando a profundidade."""
    k = 0; y = y0; r = 0.075
    while y < poly.bounds[3]:
        off = (k % 2) * r
        discs = [Point(x, y + r).buffer(r, 3) for x in np.arange(-5.0 + off, 5.0, 2 * r)]
        band = unary_union([sbox(-5.0, y + r, 5.0, y + 0.12 + r + 0.035)] + discs).intersection(poly)
        z0 = 0.004 + 0.011 * (k % 2)
        ext(p, mat, band, z0, z0 + 0.011); y += 0.12; k += 1
def bargeboards(p, A):
    """Testeiras recortadas ao longo das empenas, atras da borda do telhado, com gotas e furos."""
    zb = OVF - 0.08
    for s in (-1, 1):
        x0, x1 = s * (HX + OVF - 0.05), 0.0
        top = lambda x: (HX - abs(x)) * KR - 0.01
        board = Polygon([(x0, top(x0)), (x1, top(x1)), (x1, top(x1) - 0.3), (x0, top(x0) - 0.3)])
        cuts = []; L = math.hypot(x1 - x0, top(x1) - top(x0)); n = int(L / 0.3)
        for i in range(n):
            t_ = (i + 0.5) / n; xx = x0 + (x1 - x0) * t_; yy = top(xx) - 0.3
            cuts.append(Point(xx, yy).buffer(0.1, 4)); cuts.append(Point(xx, yy + 0.18).buffer(0.03, 3))
        ext(p, 'trim', board.difference(unary_union(cuts)), zb, zb + 0.04)
    for s in (-1, 1):   # gotas nas pontas da testeira
        xx = s * (HX + OVF - 0.12); yy = (HX - abs(xx)) * KR - 0.3
        lathe(p, 'trim', [(0.04, yy + 0.02), (0.05, yy - 0.08), (0.03, yy - 0.18), (0.0, yy - 0.26)], xx, zb + 0.02, 0.0, 8)
def gable(front=True):
    """Frontao (pivo: face da parede no eixo, cota do frechal): miolo de tabuas, faixa, escamas, testeiras recortadas; na frente
    tesoura decorativa com pendente e pinaculo, nos fundos veneziana redonda."""
    p = Piece(); A = RIDGE - 0.02
    core = Polygon([(-HX, 0.0), (HX, 0.0), (0.0, A)])
    ext(p, 'boards', core, -T, 0.0)
    ext(p, 'trim', core.intersection(sbox(-HX, 0.0, HX, 0.14)), 0.0, 0.04)
    inner = core.buffer(-0.04, join_style=2).difference(sbox(-HX, -1, HX, 0.14))
    vy = 1.55; vent = Point(0, vy).buffer(0.32, 24)
    if not front: inner = inner.difference(vent.buffer(0.09))
    scale_field(p, inner, 0.14)
    if front:
        zt = 0.2; yc = 1.5; xe = (RIDGE - yc) / KR - 0.04
        p.cham('trim', -xe, xe, yc - 0.06, yc + 0.06, zt, zt + 0.08, 0.008)                        # linha (tirante)
        p.cham('trim', -0.05, 0.05, yc - 0.32, A - 0.15, zt + 0.01, zt + 0.09, 0.008)                # pendural
        for s in (-1, 1):
            q = Piece(); Ln = math.hypot(xe * 0.55, A - 0.6 - yc)
            p.seg('trim', (s * xe * 0.6, yc + 0.05, zt + 0.04), (s * 0.05, A - 0.7, zt + 0.04), 0.07, 0.07)       # escoras
            for k in range(1, 6):                                                                   # fusos sob o tirante
                xx = s * (xe * k / 6.0)
                if abs(xx) < 0.12: continue
                lathe(p, 'trim', [(0.012, yc - 0.3), (0.02, yc - 0.26), (0.012, yc - 0.18), (0.018, yc - 0.1), (0.012, yc - 0.06)], xx, zt + 0.04, 0.0, 6)
            p.cham('trim', *sorted((s * 0.05, s * xe)), yc - 0.33, yc - 0.3, zt + 0.02, zt + 0.06, 0.004)
        lathe(p, 'trim', [(0.05, yc - 0.32), (0.07, yc - 0.4), (0.05, yc - 0.5), (0.03, yc - 0.6), (0.0, yc - 0.66)], 0.0, zt + 0.05, 0.0, 10)
        # pinaculo na ponta
        zf = OVF - 0.06
        lathe(p, 'trim', [(0.06, A - 0.2), (0.06, A + 0.25), (0.08, A + 0.29), (0.045, A + 0.36), (0.055, A + 0.46), (0.025, A + 0.58)], 0.0, zf, 0.0, 10)
        p.sphere('trim', 0.05, 0.0, A + 0.62, zf, 1); seg_cyl(p, 'iron', (0.0, A + 0.64, zf), (0.0, A + 0.95, zf), 0.01, 6)
    else:
        ext(p, 'trim', vent.buffer(0.09).difference(vent), 0.0, 0.045); ext(p, 'dark', vent, -0.02, 0.003)
        for i in range(8):
            yy = vy - 0.28 + i * 0.08; w_ = math.sqrt(max(0.0, 0.32 ** 2 - (yy - vy) ** 2))
            if w_ > 0.03: p.hull('trim', [(x, y, z) for x in (-w_, w_) for (y, z) in ((yy, 0.004), (yy + 0.012, 0.004), (yy - 0.03, 0.045), (yy - 0.018, 0.045))])
        zf = OVF - 0.06
        lathe(p, 'trim', [(0.06, A - 0.2), (0.06, A + 0.2), (0.04, A + 0.3), (0.0, A + 0.36)], 0.0, zf, 0.0, 10)
    bargeboards(p, A)
    return p
def chimney(y0, y1):
    """Chamine de tijolo do fogao (pivo: centro do pe): fuste, 2 fiadas salientes, capa de pedra e chapeu de chapa."""
    p = Piece(); a, b = 0.3, 0.3
    p.box('brick', -a, a, y0, y1, -b, b)
    for (ya, d) in ((y1 - 0.42, 0.03), (y1 - 0.35, 0.05)): p.box('brick', -a - d, a + d, ya, ya + 0.07, -b - d, b + d)
    p.cham('cill', -a - 0.06, a + 0.06, y1, y1 + 0.06, -b - 0.06, b + 0.06, 0.01)
    p.cyl('iron', 0.1, y1 + 0.06, y1 + 0.36, 0.0, 0.0, 12)
    p.hull('iron', [(0.2 * math.cos(t), y1 + 0.36, 0.2 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 12, endpoint=False)] + [(0, y1 + 0.5, 0)])
    for k in range(3): p.cyl('iron', 0.012, y1 + 0.34, y1 + 0.42, 0.13 * math.cos(k * 2.1), 0.13 * math.sin(k * 2.1), 6)
    return p
def cupola():
    """Lanternim (pivo: eixo da cumeeira, cota do frechal): base de tabuas assentada no telhado, venezianas nas 4 faces com
    colunelos, cornija, cupula de cobre de 4 aguas com beiral virado, esfera e cata-vento (seta e rosa dos ventos sem letras)."""
    p = Piece(); a = 0.6; y0 = RIDGE + 0.7
    p.hull('boards', [(sx * a, RIDGE - a * KR + 0.03, sz * a) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * a, y0 - 0.02, sz * a) for sx in (-1, 1) for sz in (-1, 1)])
    p.cham('trim', -a - 0.04, a + 0.04, y0 - 0.12, y0, -a - 0.04, a + 0.04, 0.01)
    b = 0.5; y1 = y0 + 0.75
    for sx in (-1, 1):
        for sz in (-1, 1): p.cham('trim', sx * b - 0.06, sx * b + 0.06, y0, y1, sz * b - 0.06, sz * b + 0.06, 0.008)
    p.box('dark', -b + 0.04, b - 0.04, y0, y1, -b + 0.04, b - 0.04)
    for k in range(8):   # venezianas inclinadas nas 4 faces
        yy = y0 + 0.08 + k * 0.08
        for ry in (0, 90, 180, 270):
            q = Piece(); q.hull('trim', [(x, y, z) for x in (-b + 0.06, b - 0.06) for (y, z) in ((yy + 0.05, b - 0.08), (yy + 0.06, b - 0.08), (yy - 0.01, b - 0.01), (yy, b - 0.01))])
            p.merge(q, rot_y(ry))
    prof = [(0.0, y1), (0.06, y1), (0.08, y1 + 0.04), (0.08, y1 + 0.1), (0.0, y1 + 0.12)]
    for ry in (0, 90, 180, 270):
        q = Piece(); prof_x(q, 'trim', -b - 0.09, b + 0.09, [(z + b, y) for (z, y) in prof]); m = q.parts['trim'][0]
        m = slice_keep(m, [b, 0, b], np.array([-1, 0, 1]) / math.sqrt(2)); m = slice_keep(m, [-b, 0, b], np.array([1, 0, 1]) / math.sqrt(2))
        q2 = Piece(); q2.add('trim', m); p.merge(q2, rot_y(ry))
    yr = y1 + 0.12; e = b + 0.2
    p.hull('copper', [(sx * e, yr, sz * e) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * e, yr + 0.03, sz * e) for sx in (-1, 1) for sz in (-1, 1)] + [(0, yr + 0.85, 0)])
    for ry in (0, 90):   # nervuras nas arestas
        for s in (-1, 1):
            q = Piece(); seg_cyl(q, 'copper', (s * e, yr + 0.03, s * e), (0, yr + 0.86, 0), 0.016, 6); p.merge(q, rot_y(ry))
    lathe(p, 'copper', [(0.06, yr + 0.8), (0.08, yr + 0.9), (0.04, yr + 0.98)], sec=10); p.sphere('copper', 0.08, 0, yr + 1.05, 0, 1)
    yv = yr + 1.1; seg_cyl(p, 'iron', (0, yv, 0), (0, yv + 0.9, 0), 0.012, 6)
    for (dx, dz) in ((1, 0), (0, 1)): seg_cyl(p, 'iron', (-dx * 0.32, yv + 0.35, -dz * 0.32), (dx * 0.32, yv + 0.35, dz * 0.32), 0.008, 6)
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)): p.sphere('iron', 0.03, dx * 0.34, yv + 0.35, dz * 0.34, 1)
    seg_cyl(p, 'iron', (-0.45, yv + 0.65, 0), (0.4, yv + 0.65, 0), 0.01, 6)
    ext(p, 'iron', Polygon([(0.38, yv + 0.57), (0.55, yv + 0.65), (0.38, yv + 0.73)]), -0.006, 0.006)
    ext(p, 'iron', Polygon([(-0.45, yv + 0.65), (-0.3, yv + 0.65), (-0.38, yv + 0.8), (-0.55, yv + 0.8)]), -0.006, 0.006)
    return p

# ============================================================================ telhado de telhas de madeira a 45 graus
def roof_strip(x0=-W / 2, x1=W / 2, rake=0, over=OVE):
    """Faixa de 2 m de uma agua (pivo: plano da parede, cota do frechal; beiral em z = over, sobe para -Z ate a cumeeira em z = -SX):
    forro de tabuas por baixo, fiadas de telhas de madeira, testeira, calha; rake = -1/+1: testeira inclinada na ponta x0/x1."""
    p = Piece(); f = lambda a, b: -KR * b
    poly = sbox(x0, -SX, x1, over)
    sheared(p, 'ceil', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: over - b, lambda d0, d1: sbox(-50, over - d1, 50, over - d0), over + SX + 0.01,
                    lambda v, n: np.stack([v[:, 0] / TILE, (over - v[:, 2]) / CS / TILE], 1))
    yb = -KR * over
    a = x0 + (-0.03 if rake < 0 else 0.001); b = x1 + (0.03 if rake > 0 else -0.001)
    prof_x(p, 'trim', a, b, crect(over - 0.02, over + 0.03, yb - 0.17, yb + 0.05, 0.006, (0, 1, 1, 0)))
    oz = over - 0.02
    for k in range(4):   # pontas dos caibros aparentes sob o beiral
        xc = -W / 2 + (k + 0.5) * W / 4
        p.hull('trim', [(xx, y, z) for xx in (xc - 0.03, xc + 0.03) for (z, y) in ((0.0, -0.002), (oz, -KR * oz - 0.002), (oz, -KR * oz - 0.12), (0.0, -0.15))])
    gutter_run(p, x0 - (0.03 if rake < 0 else 0), x1 + (0.03 if rake > 0 else 0), over + 0.03, yb + 0.02, caps=(rake < 0, rake > 0))
    if rake:
        xr = x0 if rake < 0 else x1; xa, xb = sorted((xr, xr + rake * 0.035))
        z0 = over + 0.03
        tp = lambda z: -KR * z + TV + BUMP + 0.03
        prof_x(p, 'trim', xa, xb, [(z0, tp(z0)), (-SX, tp(-SX)), (-SX, KR * SX - 0.22), (z0, -KR * z0 - 0.22)])
    return p
def ridge_cap(z0, z1):
    """Cumeeira de tabuas em V com rolo de chapa (pivo: eixo, cota do frechal)."""
    p = Piece(); y = TV + BUMP + RIDGE
    for s in (-1, 1):
        p.hull('ridge', [(x, y - KR * abs(x) + dy, z) for x in (0.0, s * 0.16) for dy in (-0.01, 0.025) for z in (z0, z1)])
    q = trimesh.creation.cylinder(radius=0.045, height=z1 - z0 + 0.04, sections=12); q.apply_translation([0, y + 0.03, (z0 + z1) / 2]); p.add('ridge', q)
    return p

# ============================================================================ porta, chapeu e escadas
def door_leaf_main(w=0.73, h=2.34, t=0.05):
    """Folha da porta dupla: vidro de 4 quadros em cima, 2 almofadas embaixo, puxador e espelho."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.12, w - 0.12, 1.15, h - 0.14, -t, t)] + [tbox(0.12, w - 0.12, y0, y1, z - 0.01, z + 0.01) for (y0, y1) in ((0.16, 0.5), (0.6, 0.98)) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', 0.116, w - 0.116, 1.146, h - 0.136, -0.004, 0.004)
    p.cham('door', w / 2 - 0.014, w / 2 + 0.014, 1.15, h - 0.14, -0.014, 0.014, 0.004)
    p.cham('door', 0.12, w - 0.12, 1.66, 1.69, -0.014, 0.014, 0.004)
    for z in (1, -1):
        p.cham('brass', w - 0.1, w - 0.06, 0.85, 1.2, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.seg('brass', (w - 0.08, 1.02, z * t / 2), (w - 0.08, 1.02, z * (t / 2 + 0.05)), 0.016)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def door_leaf_french(w=0.66, h=2.32, t=0.045):
    """Folha da porta-balcao: 10 vidros (2 x 5) e almofada no pe."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.09, w - 0.09, 0.38, h - 0.09, -t, t)] + [tbox(0.09, w - 0.09, 0.1, 0.3, z - 0.01, z + 0.01) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.004, segments=2))
    p.box('glass', 0.086, w - 0.086, 0.376, h - 0.086, -0.003, 0.003)
    p.cham('door', w / 2 - 0.012, w / 2 + 0.012, 0.38, h - 0.09, -0.012, 0.012, 0.003)
    for k in range(1, 5):
        yy = 0.38 + k * (h - 0.47) / 5; p.cham('door', 0.09, w - 0.09, yy - 0.012, yy + 0.012, -0.012, 0.012, 0.003)
    for z in (1, -1):
        p.sphere('brass', 0.024, w - 0.06, 1.0, z * (t / 2 + 0.045)); p.seg('brass', (w - 0.06, 1.0, z * t / 2), (w - 0.06, 1.0, z * (t / 2 + 0.035)), 0.012)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.007, yy, yy + 0.09, 0.0, t / 2 + 0.002, 8)
    return p
def hood():
    """Chapeu da porta principal (pivo: face da fachada no eixo, cota do piso): misulas curvas recortadas, testeira, frontao com
    escamas e telhado de 2 aguas de telhas de madeira com cumeeira, lanterna pendente."""
    p = Piece(); y = 3.12; d = 1.0; w = 1.35; k = 0.8
    for s in (-1, 1):
        x = s * (w - 0.1)
        arc_pts = [(0.0, y - 0.7)] + [(d * 0.75 * (1 - math.cos(t)), y - 0.7 + 0.7 * math.sin(t)) for t in np.linspace(0, math.pi / 2, 7)]
        br = Polygon([(0.0, y)] + [(z, yy) for (z, yy) in arc_pts][::-1] + [(d * 0.75, y)]).buffer(0)
        br = sbox(0.0, y - 0.72, d * 0.8, y).difference(Point(d * 0.85, y - 0.75).buffer(0.62, 24))
        for g in getattr(br, 'geoms', [br]):
            if g.area < 1e-4: continue
            m = trimesh.creation.extrude_polygon(Polygon([(yy, z) for (z, yy) in g.exterior.coords]), 0.08)
            v = m.vertices.copy(); m.vertices = np.stack([x - 0.04 + v[:, 2], v[:, 0], v[:, 1]], 1); p.add('trim', D._fix(m))
    p.cham('trim', -w, w, y - 0.02, y + 0.06, -0.01, d, 0.01)
    f = lambda x: y + 0.06 + (w + 0.08 - abs(x)) * k
    for s in (-1, 1):
        for i in range(10):
            xa, xb = sorted((s * (0.01 + i * 0.14), s * (0.01 + (i + 1) * 0.14)))
            if abs(xb) > w + 0.1: xb = math.copysign(w + 0.1, xb) if xb > 0 else xb
            if abs(xa) > w + 0.1: continue
            xa = max(xa, -w - 0.1); xb = min(xb, w + 0.1)
            p.hull('shingles', [(x, f(x) + dy, z) for x in (xa, xb) for z in (-0.01, d + 0.08) for dy in (0.0, 0.04)])
    tri = Polygon([(-w, y + 0.06), (w, y + 0.06), (0.0, y + 0.06 + w * k)])
    ext(p, 'trim', tri, d - 0.04, d)
    q = Piece(); scale_field(q, tri.buffer(-0.06, join_style=2), y + 0.1); p.merge(q, trimesh.transformations.translation_matrix([0, 0, d - 0.01]))
    for s in (-1, 1):
        a, b = sorted((0.0, s * (w + 0.1)))
        p.hull('trim', [(x, f(x) - 0.12 + dy, z) for x in (a, b) for dy in (0.0, 0.12) for z in (d + 0.01, d + 0.05)])
    p.hull('ridge', [(x, f(0.0) + 0.04 + dy, z) for x in (-0.05, 0.05) for dy in (0.0, 0.05) for z in (-0.01, d + 0.1)])
    lathe(p, 'trim', [(0.05, f(0.0) - 0.05), (0.05, f(0.0) + 0.2), (0.03, f(0.0) + 0.3), (0.0, f(0.0) + 0.38)], 0.0, d + 0.03, 0.0, 8)
    q = porch_lantern(); p.merge(q, trimesh.transformations.translation_matrix([0, y - 0.02, d * 0.5]))
    return p
def steps(w=1.3, n=3, d=1.0, h=RAISE):
    """Patamar e degraus de pedra (pivo: face da parede no eixo, cota do piso; descem para +Z ate o chao)."""
    p = Piece(); r = h / n
    p.cham('cill', -w, w, -0.05, 0.0, 0.003, d, 0.008); p.box('stone', -w + 0.01, w - 0.01, -h + 0.003, -0.05, 0.003, d - 0.01)
    for i in range(1, n):
        y = -i * r; z0 = d + (i - 1) * 0.32
        p.cham('cill', -w, w, y - 0.05, y, z0 - 0.01, z0 + 0.32, 0.008); p.box('stone', -w + 0.01, w - 0.01, -h + 0.003, y - 0.05, z0 - 0.01, z0 + 0.31)
    return p

# ============================================================================ varanda e deck (pivo: face da parede oeste, cota do piso; x local = x + 4)
def lattice(L, h):
    """Treliça de ripas em X (ao longo de +X a partir da origem, de y = 0 a h, face em z = 0..0.04) com moldura."""
    p = Piece(); box_ = sbox(0.0, 0.0, L, h)
    for sgn, z0 in ((1, 0.005), (-1, 0.02)):
        lines = [LineString([(x, 0.0), (x + sgn * 3.0, 3.0)]).buffer(0.018, cap_style=2) for x in np.arange(-3.0, L + 3.0, 0.16)]
        ext(p, 'trim', unary_union(lines).intersection(box_), z0, z0 + 0.014)
    p.box('trim', 0.0, L, h - 0.06, h, 0.0, 0.04)
    return p
def rail_run(p, a, b, posts=(True, True), y=0.0, h=0.95):
    """Guarda-corpo entre os pontos a e b (x, z): corrimao, rodape, balaustres quadrados e postes com capitel."""
    (x0, z0), (x1, z1) = a, b; Ln = math.hypot(x1 - x0, z1 - z0)
    q = Piece()
    q.cham('trim', 0.0, Ln, h - 0.07, h, -0.045, 0.045, 0.008); q.box('trim', 0.0, Ln, 0.08, 0.14, -0.03, 0.03)
    n = int(Ln / 0.13)
    for i in range(1, n): xx = i * Ln / n; q.box('trim', xx - 0.02, xx + 0.02, 0.14, h - 0.07, -0.02, 0.02)
    for xx, on in zip((0.0, Ln), posts):
        if on:
            q.cham('trim', xx - 0.06, xx + 0.06, 0.0, h + 0.1, -0.06, 0.06, 0.01); q.cham('trim', xx - 0.08, xx + 0.08, h + 0.1, h + 0.14, -0.08, 0.08, 0.008)
            q.sphere('trim', 0.05, xx, h + 0.18, 0.0, 1)
    along(p, q, x0, z0, x1, z1, y)
def stair_run(p, xa, xb, z0, n, sgn=1, h=RAISE):
    """Escada de madeira de n degraus no deck (de xa a xb), descendo para +Z (sgn = 1) a partir da borda em z0, com corrimaos."""
    r = h / n
    for i in range(1, n + 1):
        y = -i * r; za = z0 + (i - 1) * 0.3
        if i < n: p.box('deck', xa + 0.04, xb - 0.04, y - 0.04, y, za + 0.003, za + 0.32)
        p.box('trim', xa + 0.05, xb - 0.05, y, y + r - 0.04 if i > 1 else y + r - 0.045, za - 0.012, za)
    for x in (xa, xb):
        p.hull('trim', [(xx, y, z) for xx in (x - 0.02, x + 0.02) for (z, y) in ((z0, -0.06), (z0, -0.25), (z0 + n * 0.3, -h + 0.005), (z0 + (n - 1) * 0.3, -h + 0.005))])
        p.cham('trim', x - 0.06, x + 0.06, -h + 0.005, 1.0 - h, z0 + n * 0.3 - 0.12, z0 + n * 0.3, 0.008)
        p.sphere('trim', 0.05, x, 1.08 - h, z0 + n * 0.3 - 0.06, 1)
        p.seg('trim', (x, 0.92, z0 + 0.06), (x, 0.92 - h, z0 + n * 0.3 - 0.06), 0.07, 0.07)
def veranda():
    """Varanda coberta (2,4 m) ao longo da fachada oeste e deck aberto sobre o lago: tabuas, vigas, estacas, treliça, postes com
    mao-francesa e friso de fusos, viga, caibros, forro, cobertura de chapa com juntas em pe, calha e condutor, guarda-corpos e
    2 escadas."""
    p = Piece(); h = RAISE
    # piso de tabuas (correm em Z)
    def boards(xa, xb, za, zb):
        n = int(round((xb - xa) / 0.15)); w_ = (xb - xa) / n
        for i in range(n): p.box('deck', xa + i * w_ + 0.003, xa + (i + 1) * w_ - 0.003, -0.04, 0.0, za, zb)
    boards(-VD, 0.0, -HZ, HZ); boards(-DD, -VD, DZ0, DZ1)
    foot = unary_union([sbox(-VD, -HZ, 0.0, HZ), sbox(-DD, DZ0, -VD + 0.001, DZ1)])
    ring = foot.buffer(0.035, join_style=2).difference(foot).difference(sbox(-0.001, -9, 1, 9))
    ext_y(p, 'trim', ring, -0.25, 0.012)
    for z in np.arange(-HZ + 0.3, HZ, 0.6):    # vigas
        xa = -VD + 0.05 if not (DZ0 + 0.05 < z < DZ1 - 0.05) else -DD + 0.05
        p.box('wood', xa, -0.02, -0.22, -0.04, z - 0.025, z + 0.025)
    for x in (-VD + 0.15, -1.2):                # estacas de pedra sob a varanda
        for z in np.arange(-HZ + 0.4, HZ, 1.6): p.box('stone', x - 0.1, x + 0.1, -h + 0.005, -0.22, z - 0.12, z + 0.12)
    for x in (-DD + 0.12, -4.0, -VD - 0.25):    # estacas redondas sob o deck
        for z in np.linspace(DZ0 + 0.15, DZ1 - 0.15, 5): p.cyl('wood', 0.09, -h + 0.005, -0.22, x, z, 10)
    # trelica no contorno da varanda (onde nao ha deck nem escada)
    for (za, zb) in ((-HZ + 0.04, DZ0), (DZ1, HZ - 0.04)):
        along(p, lattice(zb - za, h - 0.25), -VD - 0.04, za, -VD - 0.04, zb, -h)
    along(p, lattice(VD - 0.04, h - 0.25), -0.04, -HZ - 0.04, -VD, -HZ - 0.04, -h)
    # postes, mao-francesa, viga, friso de fusos
    yb = vr(-2.3) - 0.2
    PZ = [-HZ + 0.1, -2.5 + 0.1, 0.0, 2.5 - 0.1, HZ - 0.1]
    for z in PZ:
        x = -2.3
        p.cham('trim', x - 0.07, x + 0.07, 0.0, yb, z - 0.07, z + 0.07, 0.012)
        p.cham('trim', x - 0.09, x + 0.09, 0.0, 0.2, z - 0.09, z + 0.09, 0.01); p.cham('trim', x - 0.09, x + 0.09, yb - 0.12, yb - 0.06, z - 0.09, z + 0.09, 0.01)
        for s in (-1, 1):
            if (z + s * 0.6) > HZ or (z + s * 0.6) < -HZ: continue
            p.seg('trim', (x, yb - 0.55, z + s * 0.06), (x, yb - 0.02, z + s * 0.55), 0.06, 0.06)
        p.seg('trim', (x + 0.06, yb - 0.5, z), (x + 0.5, yb - 0.02 + VK * 0.44, z), 0.06, 0.06)
    p.box('trim', -2.37, -2.23, yb, vr(-2.37) - 0.002, -HZ, HZ)
    for (za, zb) in zip(PZ[:-1], PZ[1:]):
        za += 0.09; zb -= 0.09
        p.box('trim', -2.33, -2.27, yb - 0.32, yb - 0.27, za, zb)
        for z in np.arange(za + 0.08, zb - 0.04, 0.09): lathe(p, 'trim', [(0.012, yb - 0.27), (0.018, yb - 0.22), (0.01, yb - 0.14), (0.016, yb - 0.06), (0.012, yb)], -2.3, z, 0.0, 6)
    # caibros, forro e chapa
    p.box('trim', -0.05, 0.0, vr(0.0) - 0.2, vr(0.0), -HZ, HZ)                                   # contrafrechal
    for z in np.arange(-HZ + 0.05, HZ, 0.6):
        p.hull('wood', [(x, vr(x) + dy, zz) for x in (-0.05, -2.6) for dy in (-0.14, 0.0) for zz in (z - 0.025, z + 0.025)])
    poly = sbox(-2.62, -HZ - 0.06, 0.0, HZ + 0.06); fv = lambda a, b: vr(a)
    sheared(p, 'ceil', poly, 0.0, 0.02, fv); sheared(p, 'vroof', poly, 0.02, 0.032, fv)
    for z in np.arange(-HZ + 0.17, HZ, 0.42): sheared(p, 'vroof', sbox(-2.62, z - 0.012, -0.012, z + 0.012), 0.032, 0.065, fv)
    p.hull('flash', [(x, vr(x) + dy, z) for x in (0.0, -0.2) for dy in (0.033, 0.045) for z in (-HZ - 0.06, HZ + 0.06)])
    p.box('flash', -0.012, 0.0, vr(0.0) + 0.045, vr(0.0) + 0.2, -HZ - 0.06, HZ + 0.06)
    xe = -2.62; ye = vr(xe)
    p.box('trim', xe - 0.035, xe, ye - 0.18, ye + 0.035, -HZ - 0.06, HZ + 0.06)
    for s in (-1, 1):
        zz = sorted((s * (HZ + 0.06), s * (HZ + 0.095)))
        p.hull('trim', [(x, vr(x) + dy, z) for x in (xe - 0.035, 0.0) for dy in (-0.18, 0.035) for z in zz])
    q = Piece(); gutter_run(q, -HZ - 0.1, HZ + 0.1, 0.0, ye + 0.02, caps=(True, True)); p.merge(q, rot_y(-90, (xe - 0.035, 0, 0)))
    zd = -HZ + 0.3; xd = xe - 0.1
    seg_cyl(p, 'gutter', (xd, ye - 0.08, zd), (xd, ye - 0.3, zd), 0.035, 10); seg_cyl(p, 'gutter', (xd, ye - 0.3, zd), (-2.3 - 0.11, ye - 0.5, zd), 0.035, 10)
    seg_cyl(p, 'gutter', (-2.41, ye - 0.5, zd), (-2.41, -h + 0.15, zd), 0.035, 10); seg_cyl(p, 'gutter', (-2.41, -h + 0.15, zd), (-2.6, -h + 0.06, zd), 0.035, 10)
    # guarda-corpos
    rail_run(p, (-DD + 0.06, DZ0 + 0.06), (-DD + 0.06, DZ1 - 0.06))
    rail_run(p, (-DD + 0.06, DZ0 + 0.06), (-2.3, DZ0 + 0.06), (False, False))
    rail_run(p, (-DD + 0.06, DZ1 - 0.06), (-4.3, DZ1 - 0.06), (False, True))
    rail_run(p, (-2.9, DZ1 - 0.06), (-2.3, DZ1 - 0.06), (True, False))
    rail_run(p, (-2.3, -HZ + 0.06), (-0.0 - 0.05, -HZ + 0.06), (False, False))
    rail_run(p, (-2.3, -HZ + 0.1), (-2.3, DZ0), (False, False))
    rail_run(p, (-2.3, DZ1), (-2.3, HZ - 0.1), (False, False))
    rail_run(p, (-2.3, HZ - 0.06), (-2.0, HZ - 0.06), (False, True))
    rail_run(p, (-0.6, HZ - 0.06), (-0.05, HZ - 0.06), (True, False))
    stair_run(p, -4.3, -2.9, DZ1, 3); stair_run(p, -2.0, -0.6, HZ, 3)
    return p

# ============================================================================ interior
def run_wall(Ln, h, door_at=None, ow=0.86, t=0.12, end_gap=(0.0, 0.0)):
    """Parede interna de comprimento livre (pivo: inicio, eixo; vai para +X), com porta opcional centrada em door_at."""
    p = Piece(); xs = [0.0, Ln]; c = door_at
    if c is not None: xs = [0.0, c - ow / 2, c + ow / 2, Ln]
    for m, mesh in grid_solid(xs, [0.0, 2.1, h], [-t / 2, t / 2], lambda i, j, k: None if (c is not None and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    segs = [(end_gap[0], Ln - end_gap[1])]
    if c is not None:
        q = Piece(); door_casing(q, ow, t); p.merge(q, trimesh.transformations.translation_matrix([c, 0, 0]))
        segs = [(end_gap[0], c - ow / 2 - 0.09), (c + ow / 2 + 0.09, Ln - end_gap[1])]
    for a, b in segs:
        if b - a > 0.02: baseboard(p, a, b, t)
    return p
def floor_tile(kind, trim=(0, 0, 0, 0)):
    """Placa de 2 x 2 m: assoalho ('wood', com corpo ate o chao) ou forro de tabuas ('ceil', na cota do frechal).
    trim = recuo em metros (x-, x+, z-, z+)."""
    p = Piece(); x0, x1, z0, z1 = -1 + trim[0], 1 - trim[1], -1 + trim[2], 1 - trim[3]
    sq = sbox(x0, z0, x1, z1)
    if kind == 'ceil':
        ext_y(p, 'ceil', sq, -0.03, 0.0); return p
    ext_y(p, 'floor', sq, -0.03, 0.0)
    ext_y(p, 'concrete', sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0)), -RAISE + 0.02, -0.03)
    return p
def counter(Ln=2.4, d=0.6):
    """Balcao do cafe (pivo: ponta x0, frente para +Z, no piso): frente de lambri com almofadas, tampo de madeira com bordo,
    apoio de pes de latao, prateleira por dentro, vitrine de doces e caixa registradora sem texto."""
    p = Piece()
    p.box('boards', 0.0, Ln, 0.1, 1.0, -d, 0.0); p.box('dark', 0.02, Ln - 0.02, 0.0, 0.1, -d + 0.03, -0.02)
    n = int(Ln / 0.6)
    for i in range(n):
        a = i * Ln / n + 0.08; b = (i + 1) * Ln / n - 0.08; p.box('trim', a, b, 0.25, 0.85, 0.0, 0.015)
        p.box('boards', a + 0.05, b - 0.05, 0.3, 0.8, 0.015, 0.025)
    p.cham('wood', -0.04, Ln + 0.04, 1.0, 1.06, -d - 0.04, 0.06, 0.012)
    seg_cyl(p, 'brass', (0.05, 0.18, 0.14), (Ln - 0.05, 0.18, 0.14), 0.022, 10)
    for x in (0.2, Ln / 2, Ln - 0.2): p.box('brass', x - 0.015, x + 0.015, 0.15, 0.2, 0.025, 0.14)
    p.box('wood', 0.04, Ln - 0.04, 0.5, 0.53, -d + 0.02, -d + 0.35)
    p.box('glass', 0.3, 1.1, 1.06, 1.4, -0.45, -0.1); p.box('wood', 0.3, 1.1, 1.4, 1.42, -0.45, -0.1)
    p.box('dark', 1.6, 1.95, 1.06, 1.25, -0.45, -0.15); p.box('dark', 1.62, 1.93, 1.25, 1.36, -0.45, -0.38)
    return p
def chair(p, x, z, ry, mat='iron', seat='wood'):
    q = Piece()
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): seg_cyl(q, mat, (sx * 0.18, 0.0, sz * 0.18), (sx * 0.17, 0.45, sz * 0.17), 0.012, 6)
    q.cham(seat, -0.21, 0.21, 0.45, 0.48, -0.21, 0.21, 0.01)
    for sx in (-1, 1): seg_cyl(q, mat, (sx * 0.17, 0.48, -0.19), (sx * 0.19, 0.88, -0.24), 0.012, 6)
    q.cham(seat, -0.2, 0.2, 0.72, 0.86, -0.25, -0.22, 0.008)
    p.merge(q, rot_y(ry, (x, 0, z)))
def table_set(umbrella=None, n=4, r=0.4):
    """Mesa redonda com cadeiras (pivo: centro, no piso); umbrella = material da lona do ombrelone (None = sem)."""
    p = Piece()
    lathe(p, 'iron', [(0.25, 0.0), (0.25, 0.03), (0.05, 0.08), (0.035, 0.7), (0.08, 0.72)], sec=12)
    p.cyl('wood', r, 0.72, 0.76, 0, 0, 20)
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / 4; d = r + 0.32
        chair(p, d * math.cos(a), d * math.sin(a), -math.degrees(a) - 90)
    if umbrella:
        p.cyl('wood', 0.02, 0.76, 2.4, 0, 0, 8); R = 1.0; yc = 2.2
        pts = [(R * math.cos(t), yc, R * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        p.hull(umbrella, pts + [(0, yc + 0.35, 0)])
        for t in np.linspace(0, 2 * math.pi, 8, endpoint=False):
            p.hull(umbrella, [(R * math.cos(t + s * math.pi / 8) * 0.98, yc + dy, R * math.sin(t + s * math.pi / 8) * 0.98) for s in (-1, 1) for dy in (-0.14, 0.0)] + [(R * math.cos(t) * 1.0, yc - 0.18, R * math.sin(t) * 1.0)])
            seg_cyl(p, 'wood', (0, 1.85, 0), (0.8 * math.cos(t), yc - 0.02, 0.8 * math.sin(t)), 0.008, 5)
        p.sphere('wood', 0.04, 0, yc + 0.38, 0, 1)
    return p
def boat_rack():
    """Prateleira de canoas (pivo: inicio, encostada na parede, no piso; vai para +X, frente +Z): 3 bracos de madeira com 2 canoas
    emborcadas e remos pendurados."""
    p = Piece(); Ln = 4.2
    for x in (0.3, Ln / 2, Ln - 0.3):
        p.box('wood', x - 0.05, x + 0.05, 0.0, 2.2, 0.0, 0.08)
        for y in (0.7, 1.45): p.box('wood', x - 0.04, x + 0.04, y, y + 0.08, 0.08, 0.75)
    for y in (0.78, 1.53):
        q = Piece(); canoe(q, 3.8); p.merge(q, rot_y(0, (Ln / 2, y + 0.2, 0.42)) @ trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    for k in range(3):
        x = 0.7 + k * 0.4; seg_cyl(p, 'wood', (x, 2.1, 0.12), (x + 0.05, 0.3, 0.12), 0.02, 6); p.box('wood', x - 0.07, x + 0.12, 0.05, 0.45, 0.1, 0.14)
    return p
def canoe(p, Ln=3.8, w=0.42, h=0.3):
    """Casco de canoa (centro, borda em y = 0, quilha para baixo): oco por booleana, bancos."""
    def sec_pts(scale):
        pts = []
        for t in np.linspace(-1, 1, 15):
            x = t * Ln / 2; k = math.sqrt(max(0.0, 1 - t ** 2)) ** 0.8
            for (zz, yy) in ((-w * k, 0.0), (w * k, 0.0), (-w * 0.7 * k, -h * 0.6), (w * 0.7 * k, -h * 0.6), (0.0, -h * (0.5 + 0.5 * k))):
                pts.append((x * scale, yy * scale + (1 - scale) * 0.0, zz * scale))
        return pts
    outer = trimesh.convex.convex_hull(np.array(sec_pts(1.0)))
    inner = trimesh.convex.convex_hull(np.array(sec_pts(0.9))); inner.apply_translation([0, 0.03, 0])
    p.add('boat_g', bl_detail(outer, [inner], bevel=0.0))
    for x in (-Ln * 0.25, Ln * 0.25): p.box('boat_in', x - 0.05, x + 0.05, -0.06, -0.035, -w * 0.82, w * 0.82)
def rowboat():
    """Barco a remo (pivo: centro, na linha d'agua): casco de tabuas oco, borda, 3 bancos, toletes e 2 remos."""
    p = Piece(); Ln = 3.2; w = 0.62; h = 0.45
    def pts(sc, dy=0.0):
        out = []
        for t in np.linspace(-1, 1, 17):
            x = t * Ln / 2; k = math.sqrt(max(0.0, 1 - t ** 2)) ** (0.55 if t > 0 else 0.25)
            ww = w * (k if t > 0 else max(0.55, k)); top = h * (0.62 + 0.1 * t ** 2)
            for (zz, yy) in ((-ww, top), (ww, top), (-ww * 0.75, 0.12), (ww * 0.75, 0.12), (0.0, 0.0)):
                out.append((x * sc, yy + dy, zz * sc))
        return out
    outer = trimesh.convex.convex_hull(np.array(pts(1.0))); inner = trimesh.convex.convex_hull(np.array(pts(0.92, 0.06)))
    p.add('boat', bl_detail(outer, [inner], bevel=0.0))
    for x, y in ((-0.9, 0.3), (0.0, 0.3), (0.85, 0.32)): p.box('boat_in', x - 0.12, x + 0.12, y, y + 0.03, -w * 0.82, w * 0.82)
    for s in (-1, 1):
        p.cyl('iron', 0.012, 0.3, 0.42, 0.0, s * w * 0.95, 6)
        seg_cyl(p, 'wood', (-0.9, 0.36, s * w * 0.6), (1.1, 0.33, s * w * 0.3), 0.02, 6)
        p.box('wood', 1.05, 1.45, 0.32, 0.34, s * w * 0.3 - 0.07, s * w * 0.3 + 0.07)
    return p
def desk():
    p = Piece(); p.cham('wood', 0.0, 1.2, 0.72, 0.76, 0.0, 0.6, 0.01)
    for x in (0.03, 0.75): p.box('wood', x, x + 0.42 if x > 0.5 else x + 0.04, 0.0, 0.72, 0.03, 0.57)
    for k in range(3): p.box('wood', 0.79, 1.15, 0.08 + k * 0.21, 0.27 + k * 0.21, -0.02, 0.0); p.box('brass', 0.94, 1.0, 0.16 + k * 0.21, 0.18 + k * 0.21, -0.04, -0.02)
    p.box('dark', 0.2, 0.55, 0.76, 0.78, 0.15, 0.4)
    return p
def pendant(drop=1.1):
    p = Piece(); p.cyl('iron', 0.06, -0.03, 0.0, 0, 0, 10); p.cyl('iron', 0.006, -drop + 0.2, -0.03, 0, 0, 6)
    lathe(p, 'iron', [(0.03, -drop + 0.2), (0.06, -drop + 0.16), (0.2, -drop + 0.02), (0.22, -drop)], sec=14)
    p.sphere('lamp_glass', 0.07, 0, -drop + 0.03, 0, 1)
    return p
def menu_board():
    p = Piece(); p.box('wood', 0.0, 1.2, 0.0, 0.8, 0.0, 0.03); p.box('menu', 0.05, 1.15, 0.05, 0.75, 0.03, 0.035); return p

# ============================================================================ parque
CH = sbox(-15.0, 2.0, -12.0, 8.0)
LOBE_A = affinity.scale(Point(0, 0).buffer(1.0, 48), 5.0, 5.5).buffer(0); LOBE_A = affinity.translate(LOBE_A, -12.5, -2.0)
LOBE_B = affinity.scale(Point(0, 0).buffer(1.0, 48), 5.0, 3.2); LOBE_B = affinity.translate(LOBE_B, -14.0, 10.5)
POND = unary_union([LOBE_A, LOBE_B, CH]).buffer(1.0, 16).buffer(-1.0, 16).simplify(0.01)
RIM = 0.45; WY = 0.1; RIMY = 0.22
BX0, BX1, BZ = -17.0, -10.0, 5.5; BW = 1.1          # ponte
PLC = (0.0, 10.5); PLR = 4.6                         # praca
SX0, SX1, SZ0, SZ1 = -24.0, 10.0, -12.5, 17.5        # terreno do parque
def water():
    p = Piece(); ext_y(p, 'water', POND.buffer(0.002), 0.02, WY); return p
def pond_rim():
    """Borda do lago: blocos de pedra irregulares ao longo da margem e pedras soltas."""
    p = Piece(); ring = POND.buffer(RIM, 16).difference(POND)
    L_ = POND.exterior.length; n = int(L_ / 0.7)
    for i in range(n):
        a = POND.exterior.interpolate(i * L_ / n); b = POND.exterior.interpolate((i + 1) * L_ / n)
        seg = LineString([a, b]).buffer(RIM + 0.3, cap_style=2).intersection(ring)
        cut = seg.buffer(-0.012)
        if cut.is_empty: continue
        yy = RIMY - 0.02 * ((i * 7) % 3)
        ext_y(p, 'rimstone', cut, 0.0, yy)
    rng = np.random.default_rng(5)
    for i in range(14):
        d = rng.uniform(0, L_); pt = POND.exterior.interpolate(d)
        p.sphere('rimstone', rng.uniform(0.18, 0.32), pt.x, 0.05, pt.y, 1)
    return p
def bridge():
    """Ponte em arco de pedra sobre o canal (coordenadas do parque): tabuleiro em curva suave, timpanos de cantaria, arco de aduelas
    salientes, piso de lajes, guarda-corpo de balaustres com corrimao e 4 pilaretes com lampioes."""
    p = Piece(); xc = (BX0 + BX1) / 2; hl = (BX1 - BX0) / 2
    yd = lambda x: 0.04 + 1.0 * (0.5 + 0.5 * math.cos(math.pi * np.clip((x - xc) / hl, -1, 1)))
    xs = np.linspace(BX0, BX1, 41)
    top = [(x, yd(x)) for x in xs]
    body = Polygon([(BX0, 0.0)] + top + [(BX1, 0.0)])
    ar = 1.7; ay = 0.78
    arch = unary_union([Polygon([(xc + ar * math.cos(t), ay * math.sin(t)) for t in np.linspace(0, math.pi, 25)]), sbox(xc - ar, -0.5, xc + ar, 0.0)])
    span = body.difference(arch)
    q = Piece(); ext(q, 'bstone', span, -BW, BW); p.merge(q, trimesh.transformations.translation_matrix([0, 0, BZ]))
    vous = Polygon([(xc + (ar + 0.28) * math.cos(t), (ay + 0.28) * math.sin(t)) for t in np.linspace(0, math.pi, 25)]).difference(arch)
    cuts = [LineString([(xc + 0.0 * math.cos(t), 0.0), (xc + 3 * math.cos(t), 3 * math.sin(t) * (ay + 0.28) / (ar + 0.28))]).buffer(0.008) for t in np.linspace(0, math.pi, 14)[1:-1]]
    vous = vous.difference(unary_union(cuts))
    for s in (-1, 1):
        q = Piece(); ext(q, 'carve', vous, *sorted((s * BW, s * (BW + 0.04)))); p.merge(q, trimesh.transformations.translation_matrix([0, 0, BZ]))
    # piso de lajes acompanhando a curva
    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]
        p.hull('paving', [(x, yd(x) + dy, BZ + z) for x in (a + 0.004, b - 0.004) for dy in (0.0, 0.03) for z in (-BW + 0.22, BW - 0.22)])
    # guarda-corpos: mureta, balaustres e corrimao
    for s in (-1, 1):
        za, zb = sorted((s * (BW - 0.22), s * BW))
        for i in range(len(xs) - 1):
            a, b = xs[i], xs[i + 1]
            p.hull('bstone', [(x, yd(x) + dy, BZ + z) for x in (a, b) for dy in (0.0, 0.22) for z in (za, zb)])
            p.hull('carve', [(x, yd(x) + dy, BZ + z) for x in (a, b) for dy in (0.78, 0.86) for z in (za - 0.03, zb + 0.03)])
        zc = BZ + (za + zb) / 2
        for x in np.arange(BX0 + 0.45, BX1 - 0.4, 0.2):
            y = yd(x) + 0.22
            lathe(p, 'carve', [(0.05, y), (0.035, y + 0.06), (0.06, y + 0.25), (0.03, y + 0.45), (0.045, y + 0.52), (0.05, y + 0.56)], x, zc, 0.0, 8)
        for x in (BX0 + 0.2, BX1 - 0.2):
            y = yd(x)
            p.cham('bstone', x - 0.205, x + 0.205, y, y + 1.0, BZ + za - 0.05, BZ + zb + 0.05, 0.01)
            p.cham('carve', x - 0.24, x + 0.24, y + 1.0, y + 1.08, BZ + za - 0.09, BZ + zb + 0.09, 0.01)
            p.cyl('iron', 0.04, y + 1.08, y + 2.2, x, zc, 10)
            p.box('lamp_glass', x - 0.1, x + 0.1, y + 2.25, y + 2.6, zc - 0.1, zc + 0.1)
            for sx in (-1, 1):
                for sz in (-1, 1): p.box('iron', x + sx * 0.11 - 0.01, x + sx * 0.11 + 0.01, y + 2.2, y + 2.62, zc + sz * 0.11 - 0.01, zc + sz * 0.11 + 0.01)
            p.box('iron', x - 0.13, x + 0.13, y + 2.18, y + 2.25, zc - 0.13, zc + 0.13)
            p.hull('iron', [(x + sx * 0.16, y + 2.62, zc + sz * 0.16) for sx in (-1, 1) for sz in (-1, 1)] + [(x, y + 2.82, zc)])
    return p
def fountain():
    """Chafariz (pivo: centro, no chao): tanque circular de pedra com borda moldurada, espelho d'agua, coluna com 2 tacas,
    pinha no topo e cortinas d'agua."""
    p = Piece(); R = 2.3
    lathe(p, 'carve', [(R + 0.12, 0.0), (R + 0.12, 0.1), (R + 0.05, 0.14), (R + 0.05, 0.46), (R + 0.12, 0.5), (R + 0.12, 0.58), (R - 0.2, 0.58), (R - 0.2, 0.0)], sec=48)
    p.cyl('water', R - 0.2 + 0.002, 0.0, 0.42, 0, 0, 48)
    lathe(p, 'carve', [(0.5, 0.42), (0.42, 0.55), (0.3, 0.62), (0.26, 1.0), (0.3, 1.05), (0.12, 1.1), (1.15, 1.25), (1.2, 1.32), (1.05, 1.36), (0.0, 1.36)], sec=36)
    p.cyl('water', 1.03, 1.2, 1.33, 0, 0, 36)
    lathe(p, 'carve', [(0.16, 1.36), (0.12, 1.7), (0.16, 1.75), (0.08, 1.8), (0.65, 1.92), (0.7, 1.98), (0.58, 2.0), (0.0, 2.0)], sec=28)
    p.cyl('water', 0.57, 1.88, 1.97, 0, 0, 28)
    lathe(p, 'carve', [(0.1, 2.0), (0.12, 2.1), (0.14, 2.3), (0.1, 2.45), (0.04, 2.55), (0.0, 2.58)], sec=12)
    for (r, y0, y1) in ((0.7, 1.32, 1.98), (1.2, 0.42, 1.32)):
        m = trimesh.creation.annulus(r_min=r - 0.006, r_max=r + 0.006, height=y1 - y0, sections=40); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
        m.apply_translation([0, (y0 + y1) / 2, 0]); p.add('water', m)
    return p
def paving(poly, y1=0.04, joints=0.6, mat='paving'):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + 0.006, z + 0.006, x + joints - 0.006, z + joints - 0.006).intersection(poly)
            ext_y(p, mat, q, 0.0, y1)
    ext_y(p, 'dark', poly.buffer(-0.002), 0.0, y1 - 0.008)
    return p
def plaza():
    """Praca do chafariz: lajes em aneis concentricos e faixa de borda."""
    p = Piece(); c = Point(PLC).buffer(PLR, 64)
    rr = [2.45, 3.2, 3.9, PLR - 0.3]
    for (r0, r1) in zip(rr[:-1], rr[1:]):
        ring = Point(PLC).buffer(r1, 64).difference(Point(PLC).buffer(r0, 64)); n = int(2 * math.pi * r1 / 0.7)
        for k in range(n):
            a0 = 2 * math.pi * k / n; a1 = 2 * math.pi * (k + 1) / n
            wedge = Polygon([PLC] + [(PLC[0] + 9 * math.cos(t), PLC[1] + 9 * math.sin(t)) for t in np.linspace(a0, a1, 4)])
            ext_y(p, 'paving', ring.intersection(wedge).buffer(-0.006), 0.0, 0.04)
    ext_y(p, 'edge', c.difference(Point(PLC).buffer(PLR - 0.3, 64)).buffer(-0.004), 0.0, 0.05)
    ext_y(p, 'dark', Point(PLC).buffer(PLR - 0.3, 64).difference(Point(PLC).buffer(2.45, 64)).buffer(-0.002), 0.0, 0.032)
    return p
PATHS = [[(0.0, 14.0), (0.0, 17.8)], [(-3.6, 8.8), (-7.0, 7.4), (-9.4, 5.5), (-10.4, 5.5)], [(-5.3, 5.9), (-5.6, 7.8)],
         [(-7.6, 3.85), (-7.85, 6.5)], [(-16.6, 5.5), (-19.5, 5.5), (-21.0, 2.0), (-20.5, -6.0), (-16.0, -9.6), (-8.0, -9.0),
         (-4.5, -7.2), (0.0, -7.2), (5.5, -6.5), (6.5, -2.0), (6.5, 7.5), (3.8, 9.6)], [(4.85, -4.0), (5.8, -4.0)]]
def path_poly():
    g = unary_union([LineString(l).buffer(1.1, 8, join_style=1) for l in PATHS[:1]] + [LineString(l).buffer(1.0, 8, join_style=1) for l in PATHS[1:]])
    g = g.difference(Point(PLC).buffer(PLR - 0.02, 64)).difference(sbox(-HX - 0.01, -HZ - 0.01, HX + 0.01, HZ + 0.01))
    g = g.difference(sbox(-HX - VD - 0.05, -HZ - 0.05, -HX, HZ + 0.05)).difference(sbox(-HX - DD - 0.05, DZ0 - 0.05, -HX, DZ1 + 0.05))
    g = g.difference(sbox(-30, 17.6, 30, 30)).difference(POND.buffer(RIM + 0.02))
    return g
def paths():
    """Caminhos de saibro com guias de tijolo em pe."""
    p = Piece(); g = path_poly()
    inner = g.buffer(-0.1, join_style=2)
    ext_y(p, 'gravel', inner, 0.0, 0.035); ext_y(p, 'edge', g.difference(inner), 0.0, 0.05)
    return p
def lawn():
    p = Piece(); g = sbox(SX0, SZ0, SX1, SZ1)
    holes = [path_poly(), Point(PLC).buffer(PLR, 64), POND.buffer(RIM, 16), sbox(-HX, -HZ, HX, HZ), sbox(-1.3, HZ, 1.3, HZ + 1.65),
             sbox(4.0, -4.6, 5.3, -3.4)]
    for h in holes: g = g.difference(h.buffer(0.001))
    ext_y(p, 'grass', g, 0.002, 0.03); return p
def sidewalk():
    p = Piece(); x0, x1, z0, z1 = SX0 - 1.0, SX1 + 1.0, SZ1 + 0.16, SZ1 + 3.2
    for x in np.arange(x0, x1, 1.5): ext_y(p, 'concrete', sbox(x + 0.005, z0, min(x + 1.5, x1) - 0.005, z1), 0.0, 0.08)
    ext_y(p, 'dark', sbox(x0 + 0.01, z0 + 0.01, x1 - 0.01, z1 - 0.01), 0.0, 0.07)
    return p
def fence(pier=True, L=2.0):
    """Gradil de L m (pivo: centro do pilar inicial, no chao; vai para +X): pilar de pedra com capa e bola, mureta, grade de ferro com
    lancas e 2 travessas."""
    p = Piece(); a = 0.2
    if pier:
        p.cham('bstone', -a, a, 0.0, 1.3, -a, a, 0.01); p.cham('carve', -a - 0.04, a + 0.04, 1.3, 1.38, -a - 0.04, a + 0.04, 0.01)
        p.sphere('carve', 0.13, 0.0, 1.5, 0.0, 1); p.cyl('carve', 0.08, 1.38, 1.42, 0, 0, 10)
    if L <= 2 * a + 0.01: return p
    p.cham('bstone', a + 0.002, L - a - 0.002, 0.0, 0.32, -0.14, 0.14, 0.008); p.cham('carve', a + 0.002, L - a - 0.002, 0.32, 0.37, -0.17, 0.17, 0.008)
    for y in (0.48, 1.08): p.box('iron', a + 0.002, L - a - 0.002, y, y + 0.03, -0.015, 0.015)
    for x in np.arange(a + 0.08, L - a - 0.04, 0.12):
        p.box('iron', x - 0.01, x + 0.01, 0.37, 1.18, -0.01, 0.01); p.hull('iron', [(x + dx, 1.18, dz) for dx in (-0.018, 0.018) for dz in (-0.018, 0.018)] + [(x, 1.28, 0)])
    return p
def gate():
    """Portao (pivo: eixo, no chao): 2 pilares altos com capitel e lampiao, arco de ferro com volutas e folhas abertas."""
    p = Piece(); a = 0.28; xg = 1.9
    for s in (-1, 1):
        x = s * xg
        p.cham('bstone', x - a, x + a, 0.0, 2.2, -a, a, 0.012); p.cham('carve', x - a - 0.05, x + a + 0.05, 2.2, 2.32, -a - 0.05, a + 0.05, 0.012)
        p.cham('carve', x - a - 0.03, x + a + 0.03, 0.0, 0.3, -a - 0.03, a + 0.03, 0.01)
        p.cyl('iron', 0.05, 2.32, 2.42, x, 0, 10); p.box('lamp_glass', x - 0.11, x + 0.11, 2.45, 2.8, -0.11, 0.11)
        for sx in (-1, 1):
            for sz in (-1, 1): p.box('iron', x + sx * 0.12 - 0.01, x + sx * 0.12 + 0.01, 2.42, 2.82, sz * 0.12 - 0.01, sz * 0.12 + 0.01)
        p.box('iron', x - 0.14, x + 0.14, 2.4, 2.45, -0.14, 0.14); p.hull('iron', [(x + sx * 0.17, 2.82, sz * 0.17) for sx in (-1, 1) for sz in (-1, 1)] + [(x, 3.02, 0)])
        # folha aberta encostada (girada 90 graus, para dentro do parque)
        xl = s * (xg - a - 0.05)
        for k in range(10):
            zz = -0.1 - k * 0.15; p.box('iron', xl - 0.01, xl + 0.01, 0.1, 1.9, zz - 0.01, zz + 0.01)
            p.hull('iron', [(xl + dx, 1.9, zz + dz) for dx in (-0.018, 0.018) for dz in (-0.018, 0.018)] + [(xl, 2.0, zz)])
        for y in (0.15, 1.0, 1.75): p.box('iron', xl - 0.015, xl + 0.015, y, y + 0.04, -1.55, -0.05)
    arc_ = [(xg * math.cos(t) * 0.86, 2.3 + 0.55 * math.sin(t)) for t in np.linspace(0, math.pi, 21)]
    for i in range(len(arc_) - 1): seg_cyl(p, 'iron', (arc_[i][0], arc_[i][1], 0), (arc_[i + 1][0], arc_[i + 1][1], 0), 0.03, 6)
    for t in np.linspace(0.2, math.pi - 0.2, 7):
        seg_cyl(p, 'iron', (xg * math.cos(t) * 0.86, 2.3 + 0.55 * math.sin(t), 0), (xg * math.cos(t) * 0.86, 2.32, 0), 0.012, 6)
    seg_cyl(p, 'iron', (-xg * 0.86, 2.32, 0), (xg * 0.86, 2.32, 0), 0.025, 6)
    for s in (-1, 1): ext(p, 'iron', Point(s * 0.35, 2.55).buffer(0.13, 12).difference(Point(s * 0.35, 2.55).buffer(0.1, 12)), -0.01, 0.01)
    return p
def lamp_post():
    """Lampiao de ferro fundido com globo (pivo: base, no chao)."""
    p = Piece()
    lathe(p, 'iron', [(0.16, 0.0), (0.16, 0.06), (0.11, 0.12), (0.08, 0.3), (0.055, 0.42)], sec=12)
    p.cyl('iron', 0.045, 0.42, 3.3, 0.0, 0.0, 10)
    for yy in (0.7, 1.5, 3.0): p.cyl('iron', 0.06, yy, yy + 0.05, 0.0, 0.0, 10)
    lathe(p, 'iron', [(0.05, 3.3), (0.12, 3.36), (0.1, 3.4)], sec=12)
    p.sphere('lamp_glass', 0.22, 0.0, 3.6, 0.0, 2)
    p.cyl('iron', 0.08, 3.8, 3.84, 0, 0, 10); p.sphere('iron', 0.035, 0, 3.88, 0, 1)
    return p
def bench():
    """Banco de praca (pivo: centro, no chao; frente para +Z): laterais de ferro fundido em voluta, assento e encosto de ripas."""
    p = Piece(); L1 = 1.8
    for s in (-1, 1):
        x = s * 0.75
        p.seg('iron', (x, 0.0, 0.22), (x, 0.44, 0.18), 0.05, 0.05); p.seg('iron', (x, 0.0, -0.22), (x, 0.44, -0.16), 0.05, 0.05)
        p.seg('iron', (x, 0.44, 0.24), (x, 0.44, -0.22), 0.05, 0.05); p.seg('iron', (x, 0.44, -0.2), (x, 0.88, -0.3), 0.05, 0.05)
        p.seg('iron', (x, 0.62, 0.22), (x, 0.66, -0.12), 0.04, 0.04)
    for i in range(5): z = -0.2 + i * 0.09; p.cham('wood', -L1 / 2, L1 / 2, 0.465, 0.495, z, z + 0.075, 0.006)
    for k, y in enumerate((0.58, 0.68, 0.78)):
        zz = -0.205 - (y - 0.48) * 0.22; p.cham('wood', -L1 / 2, L1 / 2, y, y + 0.075, zz - 0.03, zz, 0.006)
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
    ext_y(p, 'mulch', Point(0, 0).buffer(0.8, 20), 0.0, 0.05)
    return p
def bush(r=0.5):
    p = Piece(); rng = np.random.default_rng(3)
    p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def monument():
    """Pedestal de pedra com urna (pivo: centro, no chao): 2 degraus, dado com almofadas, cornija e urna com alcas."""
    p = Piece()
    p.cham('bstone', -0.9, 0.9, 0.0, 0.2, -0.9, 0.9, 0.01); p.cham('bstone', -0.7, 0.7, 0.2, 0.4, -0.7, 0.7, 0.01)
    p.cham('carve', -0.55, 0.55, 0.4, 0.55, -0.55, 0.55, 0.01); p.box('bstone', -0.45, 0.45, 0.55, 1.6, -0.45, 0.45)
    for ry in (0, 90, 180, 270):
        q = Piece(); q.cham('carve', -0.3, 0.3, 0.75, 1.4, 0.44, 0.47, 0.008); p.merge(q, rot_y(ry))
    p.cham('carve', -0.55, 0.55, 1.6, 1.75, -0.55, 0.55, 0.012); p.cham('carve', -0.5, 0.5, 1.75, 1.82, -0.5, 0.5, 0.01)
    lathe(p, 'carve', [(0.25, 1.82), (0.18, 1.9), (0.12, 1.98), (0.3, 2.2), (0.36, 2.45), (0.3, 2.65), (0.22, 2.72), (0.26, 2.78), (0.12, 2.86), (0.05, 3.0), (0.0, 3.02)], sec=20)
    for s in (-1, 1): ext(p, 'carve', Point(s * 0.38, 2.5).buffer(0.1, 10).difference(Point(s * 0.38, 2.5).buffer(0.06, 10)), -0.02, 0.02)
    return p
def bin_():
    p = Piece(); lathe(p, 'iron', [(0.25, 0.0), (0.25, 0.05), (0.27, 0.9), (0.29, 0.92)], sec=16)
    p.cyl('dark', 0.24, 0.85, 0.921, 0, 0, 16); p.hull('iron', [(0.3 * math.cos(t), 0.94, 0.3 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)] + [(0, 1.05, 0)])
    for y in (0.3, 0.6): p.cyl('iron', 0.268, y, y + 0.04, 0, 0, 16)
    return p
def service_steps():
    """Degraus de pedra da porta de servico (pivo: face da parede leste no eixo da porta, cota do piso; descem para +Z)."""
    return steps(0.6, 3, 0.6)
def downspout_piece(top):
    return downspout(top + 0.02 - KR * OVE, OVE + 0.03 + 0.065)

# ============================================================================ pecas
pieces = {
    'chimney': chimney(RIDGE - 1.2, RIDGE + 0.9), 'cupola': cupola(), 'hood': hood(), 'front_steps': steps(), 'service_steps': service_steps(),
    'gable_front': gable(True), 'gable_back': gable(False),
    'roof_eave': roof_strip(), 'roof_eave_a': roof_strip(x0=-W / 2 - OVF, rake=-1), 'roof_eave_b': roof_strip(x1=W / 2 + OVF, rake=1),
    'ridge': ridge_cap(-HZ - OVF, HZ + OVF), 'downspout': downspout_piece(YE), 'corner': corner(), 'veranda': veranda(),
    'door_leaf_main': door_leaf_main(), 'door_leaf_french': door_leaf_french(), 'door_leaf_back': door_back(0.88, 2.16), 'door_leaf_interior': door_interior(0.82, 2.06),
    'counter': counter(), 'cafe_table': table_set(None, 3, 0.36), 'boat_rack': boat_rack(), 'desk': desk(), 'pendant': pendant(), 'menu_board': menu_board(),
    'porch_lantern': porch_lantern(),
    'water': water(), 'pond_rim': pond_rim(), 'bridge': bridge(), 'fountain': fountain(), 'plaza': plaza(), 'paths': paths(), 'lawn': lawn(), 'sidewalk': sidewalk(),
    'fence': fence(), 'fence_np': fence(False), 'fence_pier': fence(True, 0.4), 'gate': gate(), 'lamp_post': lamp_post(), 'bench': bench(),
    'tree': tree(), 'tree_b': tree(4.4, 1.4, 'leaf2', 4), 'bush': bush(), 'monument': monument(), 'rowboat': rowboat(),
    'umbrella_table_r': table_set('canvas_r'), 'umbrella_table_w': table_set('canvas_w'), 'umbrella_table_y': table_set('canvas_y'),
    'bin': bin_(), 'player_scale_ref': player_ref()}
for k in ('plain', 'win', 'vwin', 'fdoor', 'bdoor', 'door_l', 'door_r'): pieces[f'w_{k}'] = wall(k)

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
XM = [-3, -1, 1, 3]; ZM = [-4, -2, 0, 2, 4]
FRONT = {-3: 'win', -1: 'door_l', 1: 'door_r', 3: 'win'}
BACK = {-3: 'win', -1: 'plain', 1: 'plain', 3: 'win'}            # x do mundo
WEST = {-4: 'vwin', -2: 'vwin', 0: 'fdoor', 2: 'fdoor', 4: 'vwin'}
EAST = {-4: 'bdoor', -2: 'win', 0: 'win', 2: 'win', 4: 'win'}
for x in XM: put(f'w_{FRONT[x]}', x, Y0, HZ, 0, ['front', 'ext']); put(f'w_{BACK[x]}', x, Y0, -HZ, 180, ['back', 'ext'])
for z in ZM: put(f'w_{WEST[z]}', -HX, Y0, z, -90, ['left', 'ext']); put(f'w_{EAST[z]}', HX, Y0, z, 90, ['right', 'ext'])
for (x, z, ry) in ((HX, HZ, 0), (-HX, HZ, -90), (HX, -HZ, 90), (-HX, -HZ, 180)): put('corner', x, Y0, z, ry, ['ext'])
put('gable_front', 0, YE, HZ, 0, ['front', 'roof']); put('gable_back', 0, YE, -HZ, 180, ['back', 'roof'])
put('hood', 0, Y0, HZ, 0, ['front', 'ext']); put('front_steps', 0, Y0, HZ, 0, ['front', 'ext'])
put('service_steps', HX, Y0, -4.0, 90, ['right', 'ext'])
put('veranda', -HX, Y0, 0, 0, ['left', 'ext'])
for (s, x) in ((-1, -0.8), (1, 0.8)):
    if s < 0: put('door_leaf_main', -0.74, Y0 + 0.012, HZ - 0.11, 0, ['front', 'ext'], door=95)
    else: put('door_leaf_main', 0.74, Y0 + 0.012, HZ - 0.11, 180, ['front', 'ext'], door=-95)
for zc in (0.0, 2.0):   # portas-balcao (abrem para dentro)
    put('door_leaf_french', -HX + 0.12, Y0 + 0.012, zc + FDW / 2 - 0.06, 90, ['left', 'ext'], door=-95)
    put('door_leaf_french', -HX + 0.12, Y0 + 0.012, zc - FDW / 2 + 0.06, -90, ['left', 'ext'], door=95)
hx, hz = hinge(HX, -4.0, 90, -0.44, -0.12); put('door_leaf_back', hx, Y0 + 0.012, hz, 90, ['right', 'ext'], door=90)
# telhado
for (side, ry) in ((1, 90), (-1, -90)):
    for z in ZM:
        if z == 4: nm = 'roof_eave' + ('_a' if side > 0 else '_b')
        elif z == -4: nm = 'roof_eave' + ('_b' if side > 0 else '_a')
        else: nm = 'roof_eave'
        put(nm, side * HX, YE, z, ry, ['roof'])
put('ridge', 0, YE, 0, 0, ['roof']); put('cupola', 0, YE, 0.0, 0, ['roof']); put('chimney', 0, YE, -3.3, 0, ['roof'])
for z in (HZ - 0.27, -HZ + 0.28): put('downspout', HX, 0.0, z, 90, ['ext'])
# interior
for x in XM:
    for z in ZM:
        tr = (T if x == -3 else 0.0, T if x == 3 else 0.0, T if z == -4 else 0.0, T if z == 4 else 0.0)
        for kind, y, tg in (('wood', Y0, ['floor0']), ('ceil', YE, ['floor0', 'roof'])):
            nm = f'floor_{kind}' + ('_e' + '_'.join(str(int(round(t * 100))) for t in tr) if any(tr) else '')
            if nm not in pieces: pieces[nm] = floor_tile(kind, tr)
            put(nm, x, y, z, 0, tg)
HI = H0 - 0.005
pieces['pw_hall'] = run_wall(2 * XI, HI, door_at=XI - 1.5)
put('pw_hall', -XI, Y0, ZP1, 0, ['floor0'])
hx, hz = hinge(-1.5, ZP1, 0, -0.41, 0); put('door_leaf_interior', hx, Y0 + 0.01, hz, 0, ['floor0'], door=-90)
LP2 = round(ZI + (ZP1 - 0.06), 3); pieces['pw_office'] = run_wall(LP2, HI, door_at=0.95, end_gap=(0.016, 0.0))
put('pw_office', XP2, Y0, ZP1 - 0.06, 90, ['floor0'])
hx, hz = hinge(XP2, ZP1 - 0.06 - 0.95, 90, -0.41, 0); put('door_leaf_interior', hx, Y0 + 0.01, hz, 90, ['floor0'], door=90)
put('counter', 1.4, Y0, -0.6, 0, ['floor0']); put('menu_board', 2.0, Y0 + 1.6, ZP1 + 0.06, 0, ['floor0'])
for (x, z) in ((2.4, 3.3), (2.4, 1.15), (-2.2, 3.7)): put('cafe_table', x, Y0, z, 0, ['floor0'])
put('boat_rack', -XI + 0.2, Y0, -ZI, 0, ['floor0'])
put('desk', 2.2, Y0, ZP1 - 0.06 - 0.6, 0, ['floor0'])
for (x, z) in ((-2.0, 2.6), (2.0, 2.6), (-2.0, 0.0), (2.0, -0.2)): put('pendant', x, YE - 0.03, z, 0, ['floor0'])
for z in (-3.2, 0.9, 3.4): put('porch_lantern', -HX - 1.3, Y0 + vr(-1.3), z, 0, ['left', 'ext'])
# parque
for nm in ('water', 'pond_rim', 'bridge', 'plaza', 'paths', 'lawn', 'sidewalk'): put(nm, 0, 0, 0, 0, ['site'])
put('fountain', PLC[0], 0.0, PLC[1], 0, ['site'])
for x0 in np.arange(SX0, -1.9 - 2.0 + 0.01, 2.0): put('fence', float(x0), 0.0, SZ1, 0, ['site'])
put('gate', 0.0, 0.0, SZ1, 0, ['site'])
for x0 in np.arange(2.0, SX1 - 0.01, 2.0): put('fence' if x0 > 2.0 else 'fence_np', float(x0), 0.0, SZ1, 0, ['site'])
for z0 in np.arange(SZ1, SZ0 + 0.01, -2.0): put('fence', SX1, 0.0, float(z0), 90, ['site'])
put('fence_pier', SX1, 0.0, SZ0, 90, ['site'])
for (x, z) in ((-7.8, 9.4), (5.2, 12.2), (-19.2, 3.8), (-12.0, -10.9), (4.6, -8.6), (-21.9, -2.0), (8.0, 1.0)): put('lamp_post', x, 0.0, z, 0, ['site'])
for (x, z, ry) in ((-3.75, 10.5, 90), (3.75, 10.5, -90), (-22.4, -3.0, 90), (-12.0, -11.3, 0), (8.2, 5.0, -90)): put('bench', x, 0.04 if abs(x) < 4 else 0.0, z, ry, ['site'])
for (x, z, k) in ((-22.0, -10.5, 'tree'), (-22.0, 13.5, 'tree_b'), (8.3, -10.5, 'tree'), (8.6, 3.2, 'tree_b'), (8.3, 14.3, 'tree'),
                  (-3.2, -10.6, 'tree_b'), (-18.5, 15.6, 'tree'), (-7.5, 15.0, 'tree_b'), (3.6, 15.6, 'tree_b')): put(k, x, 0.0, z, 0, ['site'])
for (x, z) in ((-1.9, 6.4), (1.9, 6.4), (-4.7, -5.6), (4.7, 5.5), (-22.8, 7.5), (6.0, 15.8), (-5.0, 16.0)): put('bush', x, 0.0, z, 0, ['site'])
put('monument', -7.2, 0.0, 13.4, 0, ['site'])
for (x, z, ry) in ((-13.6, -3.6, 30), (-14.6, 10.8, -20), (-10.4, -1.0, 90)): put('rowboat', x, WY - 0.12, z, ry, ['site'])
for (x, z, k) in ((-8.5, -3.2, 'r'), (-8.5, -0.7, 'w'), (-8.5, 1.8, 'y')): put(f'umbrella_table_{k}', x, Y0, z, 0, ['left', 'ext'])
for (x, z) in ((1.6, 16.0), (-8.6, 6.2), (6.0, -7.8)): put('bin', x, 0.0 if abs(x) > 2 else 0.035, z, 0, ['site'])
put('player_scale_ref', -1.6, 0.04, 8.0); put('player_scale_ref', -1.0, Y0, 1.5, 0, ['floor0'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_height': H0, 'wall_thickness': T, 'floor_raise': RAISE,
                       'building': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 1, 'eave_level': YE, 'ridge_level': YE + RIDGE, 'roof_pitch_deg': ANG,
                                    'veranda': {'x': [-HX - VD, -HX], 'z': [-HZ, HZ]}, 'deck': {'x': [-HX - DD, -HX - VD], 'z': [DZ0, DZ1]}},
                       'park': {'x': [SX0, SX1], 'z': [SZ0, SZ1], 'water_level': WY, 'bridge': {'x': [BX0, BX1], 'z': BZ}, 'plaza_center': list(PLC)},
                       'roof': 'wood shingle gable roof at 45 deg with cupola; standing-seam metal veranda roof',
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
