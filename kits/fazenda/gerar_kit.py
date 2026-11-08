"""Kit 44: fazenda americana, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Casa de 2 andares de tabuas sobrepostas (10 x 8 m) sobre embasamento de pedra, com venezianas, varanda na frente com colunas
torneadas, guarda-corpo e telhado de telhas, telhado de 2 aguas a 40 graus com 2 chamines, calhas e condutores. Dentro: sala com
lareira, cozinha com fogao a lenha, hall com escada; em cima, 2 quartos e banheiro. Celeiro vermelho de 16 x 18 m de tabua e
mata-junta com telhado holandes, portoes de 2 folhas, porta do palheiro com capuz da talha, cupula com cata-vento; dentro, corredor,
baias, cochos e jiraus de feno com escada. Silo de concreto com cupula, cata-vento de agua com bebedouro, horta cercada com milho e
canteiros, carroca de feno, bomba manual, lenha, caixa de correio, cerca de 3 travessas, estrada, arvores.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'siding': (234, 228, 208), 'shingles': (104, 106, 112), 'deck': (150, 116, 82), 'floor': (168, 120, 78), 'stone': (150, 144, 134),
                  'brick': (156, 72, 54), 'ceiling': (238, 236, 226), 'shutter': (46, 52, 50), 'door': (52, 74, 62), 'barn': (152, 42, 36),
                  'planks': (160, 126, 90), 'metal': (120, 124, 130), 'gutter': (200, 200, 196), 'concrete': (178, 174, 166), 'silo_c': (196, 192, 182),
                  'gravel': (164, 156, 142), 'grass': (104, 150, 70), 'soil': (104, 78, 56), 'asphalt': (78, 80, 82), 'yellowp': (230, 190, 50),
                  'leaf': (82, 128, 60), 'leaf2': (108, 144, 66), 'bark': (98, 74, 54), 'corn': (122, 156, 62), 'tassel': (214, 184, 104),
                  'hay': (214, 182, 104), 'galv': (178, 182, 184), 'wood': (156, 112, 70), 'dkwood': (98, 66, 44), 'rail': (128, 104, 80),
                  'porcelain': (244, 244, 238), 'chrome': (210, 212, 214), 'rubber': (32, 32, 32), 'quilt': (176, 60, 52), 'linen': (240, 236, 224),
                  'rug': (140, 70, 52), 'fabric': (84, 104, 120), 'water': (70, 110, 130), 'paint_w': (244, 242, 236), 'redp': (178, 40, 34),
                  'green_v': (70, 120, 50), 'pumpkin': (220, 120, 40), 'tomato': (196, 50, 40), 'enamel': (240, 238, 228), 'lino': (196, 60, 52)},
           texturas={'siding': 'siding', 'shingles': 'shingles', 'plaster': 'plaster', 'deck': 'deck', 'floor': 'planks', 'stone': 'stone2',
                     'brick': 'brick', 'barn': 'paint', 'planks': 'planks', 'cap': 'plaster', 'concrete': 'render', 'silo_c': 'render',
                     'gravel': 'render', 'grass': 'render', 'soil': 'render', 'asphalt': 'render', 'wood': 'planks', 'dkwood': 'planks',
                     'rail': 'planks', 'ceiling': 'plaster'},
           out=OUT)
D.METAL.update({'galv', 'chrome', 'metal'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.3; t_ = 0.12; H = 3.0; SLAB = 0.2; RAISE = 0.6
def lvl(fl): return RAISE + fl * H
HX, HZ = 5.0, 4.0                                       # casa: x de -5 a 5, z de -4 a 4, frente para +Z
FRIEZE = 2.72; FT = H; WT = 0.12; HW = H + 0.03
configurar_tabuas(WT, FRIEZE, 0.2)
PITCH = 40.0; KR = math.tan(math.radians(PITCH)); CS = math.cos(math.radians(PITCH))
YE = lvl(1) + H - 0.03; OV = 0.45; RAKE = 0.35         # face de baixo do telhado na face da parede, beiral, beiral do oitao
YRIDGE = YE + KR * HZ
configurar_telhado(0.08, 0.022, PITCH)
CHX = 4.35; CHW = 0.4; CHD = 0.45                       # chamines: centro em x = +-4,35, meia largura e meia profundidade
PD = 2.4; PFL = RAISE - 0.03; PB = PFL + 2.45; PBT = PB + 0.25   # varanda: fundo, deck, viga
PZ = HZ + PD; PXW = HX + 0.3; PRY = lvl(1) + 0.42; KP = (PRY - PBT) / (PD + 0.05); POV = 0.35
POSTS = [-5.1, -3.0, -1.0, 1.0, 3.0, 5.1]
STZ0, NR, RR, RN = 2.2, 16, H / 16, 0.26                # escada: pe em z = 2,2, sobe para -Z, 16 espelhos
STZ1 = STZ0 - (NR - 1) * RN
# celeiro (holandes): largura 16, comprimento 18
BW = 8.0; BD = 9.0; RB = 0.15; YEB = 3.6; OVB = 0.3; OVR = 0.3; R1 = 1.8
T1 = math.tan(math.radians(60)); T2 = math.tan(math.radians(22))
YK = YEB + R1 * T1; YRB = YK + (BW - R1) * T2
BX, BZ = -6.0, -22.0                                    # centro do celeiro (paredes de x -14 a 2 e z -31 a -13), portao para +Z
GU = [(-BW - OVB, YEB - OVB * T1), (-BW + R1, YK), (0.0, YRB), (BW - R1, YK), (BW + OVB, YEB - OVB * T1)]
LOFT = 3.3; LX = 2.4                                    # jiraus de feno: piso em 3,3, de |x| = 2,4 ate a parede
SILO = (-16.95, -25.0); SR = 2.4; SH = 13.0
MILL = (-25.0, -6.0); GARDEN = (-22.0, -1.0, -10.0, 11.0)
SX0, SX1, SZ0, SZ1 = -34.0, 30.0, -36.0, 28.0
FZF = 20.0; DRIVE = (9.0, 13.0); ROAD = (21.5, 27.5)
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
def mirror_x(x0=0.0):
    M = np.eye(4); M[0, 0] = -1; M[0, 3] = 2 * x0; return M
def tr(x=0.0, y=0.0, z=0.0): return trimesh.transformations.translation_matrix([x, y, z])
def along(p, q, x0, z0, x1, z1, y=0.0):
    ang = math.degrees(math.atan2(-(z1 - z0), x1 - x0)); p.merge(q, rot_y(ang, (x0, y, z0)))
def segs_excl(gaps, a0=-1.0, a1=1.0, pad=0.0):
    segs = [(a0, a1)]
    for (a, b) in gaps: segs = [s for (c, d) in segs for s in ((c, min(d, a - pad)), (max(c, b + pad), d)) if s[1] - s[0] > 1e-3]
    return segs
def mirrored(p, M):
    q = Piece(); q.merge(p, M); return q
def clipped(p, planes):
    """Corta todas as malhas pelos planos (origem, normal), mantendo o lado da normal (com tampa)."""
    q = Piece(); q.uv = dict(p.uv)
    for mat, ms in p.parts.items():
        for m in ms:
            mm = m
            for (o, n) in planes:
                n = np.array(n, float); b = mm.bounds; d = np.dot(n, o)
                ds = [np.dot(n, [x, y, z]) for x in b[:, 0] for y in b[:, 1] for z in b[:, 2]]
                if min(ds) >= d - 1e-9: continue
                if max(ds) <= d + 1e-9: mm = None; break
                mm = slice_keep(mm, o, n / np.linalg.norm(n))
                if mm is None or len(mm.faces) == 0: mm = None; break
            if mm is not None: q.add(mat, mm)
    return q
def subtract_prism(p, poly, y0, y1):
    """Tira de cada malha o prisma vertical (poligono no plano x-z, de y0 a y1): usado para o telhado encostar no torreao."""
    cut = trimesh.creation.extrude_polygon(poly, y1 - y0); v = cut.vertices.copy(); cut.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1); cut.invert(); cut = D._fix(cut)
    bx = poly.bounds; q = Piece(); q.uv = dict(p.uv)
    for mat, ms in p.parts.items():
        for m in ms:
            b = m.bounds
            if b[1, 0] < bx[0] or b[0, 0] > bx[2] or b[1, 2] < bx[1] or b[0, 2] > bx[3] or b[1, 1] < y0 or b[0, 1] > y1: q.add(mat, m); continue
            try:
                r = trimesh.boolean.difference([m, cut], engine='manifold')
                if r is not None and len(r.faces): q.add(mat, r)
            except Exception:
                c = m.centroid
                if not Point(c[0], c[2]).within(poly): q.add(mat, m)
    return q
def poly_ngon(cx, cz, r, n=12, a0=0.0):
    return Polygon([(cx + r * math.cos(a0 + 2 * math.pi * k / n), cz + r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)])
def alu_frame(p, a, b, y0, y1, f=0.05, z0=-0.2, z1=-0.1, mulls=(), trans=()):
    p.box('frame', a, a + f, y0, y1, z0, z1); p.box('frame', b - f, b, y0, y1, z0, z1)
    p.box('frame', a + f, b - f, y1 - f, y1, z0, z1); p.box('frame', a + f, b - f, y0, y0 + f, z0, z1)
    for x in mulls: p.box('frame', x - f / 2, x + f / 2, y0 + f, y1 - f, z0, z1)
    for y in trans: p.box('frame', a + f, b - f, y - f / 2, y + f / 2, z0, z1)
def wall_lamp():
    """Arandela redonda de chapa (pivo: face da parede, centro)."""
    p = Piece(); p.cyl('metal', 0.12, -0.12, 0.0, 0, 0, 16) if False else None
    m = trimesh.creation.cylinder(radius=0.13, height=0.05, sections=20); m.apply_translation([0, 0, 0.025]); p.add('metal', m)
    m = trimesh.creation.cylinder(radius=0.1, height=0.05, sections=20); m.apply_translation([0, 0, 0.074]); p.add('lamp_glass', m)
    p.box('metal', -0.14, 0.14, 0.13, 0.15, 0.0, 0.12)
    return p
def tiles(p, poly, y0, y1, step, mat, gap=0.005, fill='brass', ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step + gap, oz + j * step + gap, ox + (i + 1) * step - gap, oz + (j + 1) * step - gap).intersection(poly)
            if q.area > 1e-6: ext_y(p, mat, q, y0, y1)
    ext_y(p, fill, poly.buffer(-0.001, join_style=2), y0, y1 - 0.003)
def run_wall(Ln, h, cuts=(), t=t_):
    """Parede interna (pivo: inicio, eixo; vai para +X). cuts = (centro, largura, y0, y1, tipo): door (porta com guarnicao),
    pass (vao livre), counter (balcao com aba), grille (guiche com grade cromada e passa-volumes)."""
    p = Piece(); cs = [(c - w / 2, c + w / 2, y0, y1, k) for (c, w, y0, y1, k) in cuts]
    xs = sorted(set([0.0, Ln] + [v for c in cs for v in c[:2]])); ys = sorted(set([0.0, h] + [v for c in cs for v in c[2:4]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        return None if any(a < cx < b and y0 < cy < y1 for (a, b, y0, y1, _) in cs) else 'plaster'
    for m, mesh in grid_solid(xs, ys, [-t / 2, t / 2], cell).items(): p.add(m, mesh)
    for (a, b, y0, y1, k) in cs:
        if k == 'door': q = Piece(); door_casing(q, b - a, t, y1); p.merge(q, tr((a + b) / 2, 0, 0))
        if k in ('counter', 'grille'):
            p.cham('wood', a - 0.06, b + 0.06, y0 - 0.04, y0 + 0.004, -t / 2 - 0.3, t / 2 + 0.3, 0.006)
            for s in (-1, 1):
                zz = sorted((s * t / 2, s * (t / 2 + 0.02)))
                p.box('metal', a - 0.06, a - 0.002, y0, y1 + 0.06, *zz); p.box('metal', b + 0.002, b + 0.06, y0, y1 + 0.06, *zz); p.box('metal', a - 0.002, b + 0.002, y1 + 0.002, y1 + 0.06, *zz)
        if k == 'glaze':
            for s_ in (-1, 1): p.box('gold', a + 0.001 if s_ < 0 else b - 0.04, a + 0.04 if s_ < 0 else b - 0.001, y0, y1, -t / 2 - 0.012, t / 2 + 0.012)
            p.box('gold', a + 0.04, b - 0.04, y1 - 0.04, y1 - 0.001, -t / 2 - 0.012, t / 2 + 0.012); p.box('gold', a + 0.04, b - 0.04, y0 + 0.001, y0 + 0.04, -t / 2 - 0.012, t / 2 + 0.012)
            for xm in np.linspace(a, b, max(2, int(round((b - a) / 1.0))) + 1)[1:-1]: p.box('gold', xm - 0.02, xm + 0.02, y0 + 0.04, y1 - 0.04, -0.03, 0.03)
            p.box('glass', a + 0.04, b - 0.04, y0 + 0.04, y1 - 0.04, -0.004, 0.004)
        if k == 'grille':
            for x in np.arange(a + 0.06, b - 0.04, 0.06): p.cyl('chrome', 0.006, y0 + 0.22, y1, x, 0.0, 6)
            p.box('chrome', a, b, y0 + 0.2, y0 + 0.23, -0.01, 0.01); p.box('chrome', a, b, y1 - 0.05, y1 - 0.02, -0.01, 0.01)
            p.box('glass', a + 0.002, b - 0.002, y0 + 0.23, y1 - 0.05, 0.03, 0.036)
    for side in (1, -1):
        gaps = [(a - (0.09 if k == 'door' else 0.0), b + (0.09 if k == 'door' else 0.0)) for (a, b, y0, y1, k) in cs if y0 < 0.01]
        for (a, b) in segs_excl(gaps, 0.0, Ln):
            if b - a > 0.02: prof_x(p, 'dkwood', a, b, D.BASE_PROF(t) if side > 0 else [(-z, y) for (z, y) in D.BASE_PROF(t)][::-1])
    return p
PART = [(-8.2, 0.9, 0.0, 2.1, 'door'), (-4.85, 0.9, 0.0, 2.1, 'door'), (-2.3, 1.6, 0.95, 2.2, 'counter'), (-0.9, 0.9, 0.0, 2.1, 'door'),
        (2.3, 1.0, 1.0, 2.1, 'grille'), (3.8, 1.0, 1.0, 2.1, 'grille'), (5.0, 0.9, 0.0, 2.1, 'door'), (7.6, 3.0, 0.0, 2.4, 'pass')]
ZST = -4.25                                                # frente das cabines dos banheiros
def lockers(L1=1.8, rows=3):
    """Guarda-volumes de aco (pivo: centro de tras, piso): base, portas com veneziana, puxador e fechadura, sem numeros."""
    p = Piece(); x = L1 / 2; h = 1.95; n = int(round(L1 / 0.45))
    p.box('steel', -x, x, 0.1, h, 0.0, 0.48); p.box('dark', -x + 0.02, x - 0.02, 0.0, 0.1, 0.0, 0.44); p.cham('steel', -x - 0.01, x + 0.01, h, h + 0.04, 0.0, 0.5, 0.005)
    for i in range(n):
        for j in range(rows):
            a = -x + i * L1 / n + 0.012; b = -x + (i + 1) * L1 / n - 0.012; y0 = 0.12 + j * (h - 0.14) / rows + 0.01; y1 = 0.12 + (j + 1) * (h - 0.14) / rows - 0.01
            p.box('vinyl_g', a, b, y0, y1, 0.48, 0.49)
            for k in range(4): yy = y1 - 0.08 - k * 0.035; p.box('dark', a + 0.08, b - 0.08, yy, yy + 0.012, 0.49, 0.494)
            p.box('chrome', b - 0.07, b - 0.04, (y0 + y1) / 2 - 0.05, (y0 + y1) / 2 + 0.05, 0.49, 0.51); p.cyl('brass', 0.012, (y0 + y1) / 2 + 0.08, (y0 + y1) / 2 + 0.1, b - 0.055, 0.5, 8) if False else p.box('brass', b - 0.065, b - 0.045, (y0 + y1) / 2 + 0.08, (y0 + y1) / 2 + 0.1, 0.49, 0.5)
    return p
def wall_clock(r=0.4):
    """Relogio de parede sem numeros (pivo: face da parede, centro): aro cromado, mostrador, marcas das horas e ponteiros."""
    p = Piece(); R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    for (rr, z0, z1, m) in ((r, 0.0, 0.06, 'chrome'), (r - 0.04, 0.06, 0.065, 'cream')):
        c = trimesh.creation.cylinder(radius=rr, height=z1 - z0, sections=40); c.apply_translation([0, 0, (z0 + z1) / 2]); p.add(m, c)
    for k in range(12):
        a = k * math.pi / 6; l = 0.07 if k % 3 == 0 else 0.04
        seg_cyl(p, 'dark', ((r - 0.06) * math.sin(a), (r - 0.06) * math.cos(a), 0.067), ((r - 0.06 - l) * math.sin(a), (r - 0.06 - l) * math.cos(a), 0.067), 0.008, 4)
    for (a, l, w_) in ((math.radians(300), r * 0.55, 0.012), (math.radians(60), r * 0.78, 0.008)): seg_cyl(p, 'dark', (0, 0, 0.072), (l * math.sin(a), l * math.cos(a), 0.072), w_, 4)
    p.sphere('dark', 0.02, 0, 0, 0.075, 0)
    return p
def stool():
    p = Piece(); p.cyl('chrome', 0.2, 0.0, 0.02, 0, 0, 16); seg_cyl(p, 'chrome', (0, 0.02, 0), (0, 0.66, 0), 0.03, 8)
    m = trimesh.creation.annulus(r_min=0.15, r_max=0.17, height=0.015, sections=20); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.3, 0]); p.add('chrome', m) if False else p.cyl('chrome', 0.17, 0.3, 0.315, 0, 0, 20)
    lathe(p, 'vinyl_r', [(0.18, 0.66), (0.19, 0.7), (0.18, 0.76), (0.0, 0.77)], sec=20); return p
def safe_box():
    p = Piece(); p.cham('dark', -0.35, 0.35, 0.0, 0.9, 0.0, 0.6, 0.02); p.box('steel', -0.3, 0.3, 0.1, 0.8, 0.6, 0.61)
    c = trimesh.creation.cylinder(radius=0.08, height=0.03, sections=16); c.apply_translation([0, 0.5, 0.625]); p.add('chrome', c)
    p.box('chrome', 0.15, 0.2, 0.3, 0.55, 0.61, 0.64); return p
def file_cab():
    p = Piece(); p.box('steel', -0.25, 0.25, 0.0, 1.35, 0.0, 0.62)
    for k in range(4): y = 0.05 + k * 0.33; p.box('steel', -0.23, 0.23, y, y + 0.3, 0.62, 0.635); p.box('chrome', -0.06, 0.06, y + 0.2, y + 0.23, 0.635, 0.66)
    return p

# ============================================================================ plataforma coberta (pivo: face da parede oeste, chao; local +Z para fora)
CAN_Y0, CAN_Y1 = 3.75, 4.05
CAN_COLS = [-5.0, -1.7, 1.7, 5.0]; CAN_ZC = 5.6
def paving(poly, y1, joints=1.5, mat='concrete', gap=0.006):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + gap, z + gap, x + joints - gap, z + joints - gap).intersection(poly); ext_y(p, mat, q, GY, y1)
    ext_y(p, 'dark', poly.buffer(-0.002, join_style=2), GY, y1 - 0.008)
    return p
def wheel_stop():
    p = Piece(); p.cham('concrete', -0.9, 0.9, 0.0, 0.12, -0.1, 0.1, 0.02)
    for x in (-0.6, 0.6): p.box('paint_y', x - 0.15, x + 0.15, 0.12, 0.123, -0.08, 0.08)
    return p
def door_glass(w=0.87, h=2.36, t=0.05):
    """Porta de vidro de quadro de aluminio com barra de empurrar e chute de chapa (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.06
    p.cham('frame', 0, s, 0, h, -t / 2, t / 2, 0.004); p.cham('frame', w - s, w, 0, h, -t / 2, t / 2, 0.004)
    p.cham('frame', s - 0.002, w - s + 0.002, 0, 0.25, -t / 2, t / 2, 0.004); p.cham('frame', s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.004)
    p.box('glass', s - 0.004, w - s + 0.004, 0.246, h - s + 0.004, -0.004, 0.004)
    for z in (1, -1):
        seg_cyl(p, 'chrome', (s, 1.05, z * (t / 2 + 0.05)), (w - s, 1.05, z * (t / 2 + 0.05)), 0.018, 8)
        for x in (s + 0.04, w - s - 0.04): seg_cyl(p, 'chrome', (x, 1.05, z * t / 2), (x, 1.05, z * (t / 2 + 0.05)), 0.01, 6)
    return p
def door_metal(w=0.88, h=2.13, t=0.045):
    """Porta de servico de chapa com visor redondo, barra antipanico e mola (pivo: dobradica, embaixo)."""
    p = Piece(); p.cham('metal', 0.0, w, 0.0, h, -t / 2, t / 2, 0.004)
    for z in (1, -1):
        c = trimesh.creation.annulus(r_min=0.12, r_max=0.15, height=0.012, sections=24); c.apply_translation([w / 2, 1.55, z * (t / 2 + 0.006)]); p.add('chrome', c)
    p.cyl('glass', 0.0, 0, 0, 0, 0) if False else None
    m = trimesh.creation.cylinder(radius=0.12, height=0.008, sections=24); m.apply_translation([w / 2, 1.55, 0]); p.add('dark', m)
    p.box('chrome', 0.1, w - 0.08, 1.0, 1.06, -t / 2 - 0.06, -t / 2 - 0.02); p.box('chrome', w - 0.12, w - 0.06, 1.0, 1.08, t / 2, t / 2 + 0.05)
    p.box('dark', 0.05, 0.4, h - 0.12, h - 0.06, -t / 2 - 0.06, -t / 2)
    return p

# ============================================================================ pecas
L = []

def unit(v): v = np.array(v, float); return v / np.linalg.norm(v)
def ring_y(p, mat, r0, r1, y0, y1, x=0.0, z=0.0, sec=96):
    m = trimesh.creation.annulus(r_min=r0, r_max=r1, height=y1 - y0, sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([x, (y0 + y1) / 2, z]); return p.add(mat, m)
def disc_z(p, mat, r, z0, z1, x, y, sec=20):
    m = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sec); m.apply_translation([x, y, (z0 + z1) / 2]); return p.add(mat, m)
def disc_x(p, mat, r, x0, x1, y, z, sec=20):
    m = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=sec); m.apply_transform(rot_y(90)); m.apply_translation([(x0 + x1) / 2, y, z]); return p.add(mat, m)
def off(poly, d): return poly.buffer(d, join_style=2, mitre_limit=10)
def grid_map(us, vs, mp, fb, ft):
    """Solido entre y = fb(u, v) e y = ft(u, v) sobre a grade us x vs, com (x, z) = mp(u, v) (estanque)."""
    nu, nv = len(us), len(vs); V = []
    for f in (ft, fb):
        for u in us:
            for v in vs: x, z = mp(u, v); V.append((x, f(u, v), z))
    N = nu * nv; idx = lambda i, j, b=0: b * N + i * nv + j; F = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a, b_, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1); F += [[a, c, b_], [a, d, c]]
            a, b_, c, d = idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j + 1, 1), idx(i, j + 1, 1); F += [[a, b_, c], [a, c, d]]
    ring = [(i, 0) for i in range(nu)] + [(nu - 1, j) for j in range(1, nv)] + [(i, nv - 1) for i in range(nu - 2, -1, -1)] + [(0, j) for j in range(nv - 2, 0, -1)]
    for k in range(len(ring)):
        (i0, j0), (i1, j1) = ring[k], ring[(k + 1) % len(ring)]
        a, b_ = idx(i0, j0), idx(i1, j1); c, d = idx(i1, j1, 1), idx(i0, j0, 1); F += [[a, b_, c], [a, c, d]]
    m = trimesh.Trimesh(np.array(V, float), np.array(F), process=True); m.fix_normals(); return D._fix(m)

# ============================================================================ lanchonete: contorno, facetas e modulos

# ============================================================================ casa: paredes de tabuas (pivo: face externa, cota do piso do andar)
def water_table(p, x0=-W / 2, x1=W / 2):
    p.box('stone', x0, x1, -RAISE, 0.0, -T, 0.0)
    prof_x(p, 'trim', x0, x1, [(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)])
def belt(p, x0=-W / 2, x1=W / 2):
    prof_x(p, 'trim', x0, x1, [(0.0, 0.0), (0.034, 0.0), (0.034, 0.09), (0.046, 0.094), (0.046, 0.104), (0.0, 0.118)])
def frieze(p, x0=-W / 2, x1=W / 2):
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE), (0.034, FRIEZE), (0.034, FT), (0.0, FT)])
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE - 0.05), (0.03, FRIEZE - 0.035), (0.042, FRIEZE - 0.012), (0.042, FRIEZE + 0.02), (0.0, FRIEZE + 0.02)])
def shutters(p, ow, oy0, oy1):
    """Par de venezianas de madeira pintada (quadro, 2 almofadas de palhetas inclinadas, travessa), dobradicas e prendedores em S."""
    x = ow / 2 + 0.13; sw = min(0.42, W / 2 - 0.03 - x); y0, y1 = oy0 - 0.04, oy1 + 0.03; z0, z1 = 0.03, 0.058; ym = (y0 + y1) / 2
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x + sw)))
        for (u0, u1, v0, v1) in ((a, a + 0.05, y0, y1), (b - 0.05, b, y0, y1), (a + 0.05, b - 0.05, y0, y0 + 0.07), (a + 0.05, b - 0.05, y1 - 0.06, y1), (a + 0.05, b - 0.05, ym - 0.03, ym + 0.03)):
            p.cham('shutter', u0, u1, v0, v1, z0, z1, 0.004)
        p.box('dark', a + 0.05, b - 0.05, y0 + 0.07, y1 - 0.06, z0 + 0.002, z0 + 0.006)
        for (v0, v1) in ((y0 + 0.07, ym - 0.03), (ym + 0.03, y1 - 0.06)):
            n = int((v1 - v0) / 0.05)
            for i in range(n):
                yy = v0 + (i + 0.5) * (v1 - v0) / n
                p.hull('shutter', [(u, yy + dy, z) for u in (a + 0.05, b - 0.05) for (dy, z) in ((-0.022, z0 + 0.006), (-0.012, z0 + 0.006), (0.022, z1 - 0.004), (0.012, z1 - 0.004))])
        xh = s * x
        for yy in (y0 + 0.2, y1 - 0.2): p.box('iron', *sorted((xh - s * 0.03, xh + s * 0.08)), yy - 0.015, yy + 0.015, z1, z1 + 0.006)
        xd = s * (x + sw + 0.03 if x + sw + 0.03 < W / 2 - 0.01 else x + sw - 0.02)
        p.seg('iron', (xd, y0 + 0.35, 0.025), (xd, y0 + 0.35, z1 + 0.02), 0.012); p.hull('iron', [(xd + dx, y0 + 0.35 + dy, z1 + 0.02) for dx in (-0.025, 0.025) for dy in (-0.05, 0.05)] + [(xd, y0 + 0.35, z1 + 0.03)])
def hwall(kind='plain', fl=0, ns=False):
    """Modulo de 2 m de tabuas sobrepostas. kind: win (guilhotina 0,9 x 1,5 com venezianas), small (0,6 x 0,8, banheiro), plain, door."""
    p = Piece(); h = H if fl == 0 else HW
    if kind == 'door':
        ow = 1.0; x = ow / 2; oy0 = 0.015; oy1 = 2.3
        wall_with_opening(p, 'siding', ow, oy0, oy1, h)
        p.box('frame', -x, -x + 0.07, oy0, oy1, -0.24, 0.0); p.box('frame', x - 0.07, x, oy0, oy1, -0.24, 0.0); p.box('frame', -x, x, oy1 - 0.07, oy1, -0.24, 0.0)
        p.box('frame', -x + 0.07, -x + 0.085, oy0, oy1 - 0.07, -0.2, -0.16); p.box('frame', x - 0.085, x - 0.07, oy0, oy1 - 0.07, -0.2, -0.16)
        prof_x(p, 'cap', -x + 0.07, x - 0.07, [(-0.24, 0.012), (0.03, 0.012), (0.05, 0.0), (0.05, -0.03), (-0.24, -0.03)])
        p.box('stone', -W / 2, W / 2, -RAISE, -0.03, -T, 0.0); p.box('stone', -W / 2, -x, -0.03, 0.0, -T, 0.0); p.box('stone', x, W / 2, -0.03, 0.0, -T, 0.0)
        for (a, b) in ((-W / 2, -x - 0.12), (x + 0.12, W / 2)):
            prof_x(p, 'trim', a, b, [(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)])
        for s in (-1, 1):
            a, b = sorted((s * x, s * (x + 0.12))); prof_y(p, 'trim', -0.03, oy1 + 0.025, crect(a, b, 0.0, 0.036, 0.006, (0, 0, 1, 1)))
            a, b = sorted((s * (x + 0.005), s * (x + 0.125))); p.cham('trim', a, b, -0.06, 0.16, 0.0, 0.05, 0.008)
        prof_x(p, 'trim', -x - 0.14, x + 0.14, crect(0.0, 0.04, oy1 + 0.025, oy1 + 0.2, 0.006, (0, 1, 1, 0)))
        prof_x(p, 'trim', -x - 0.17, x + 0.17, [(0.0, oy1 + 0.2), (0.075, oy1 + 0.2), (0.075, oy1 + 0.225), (0.05, oy1 + 0.245), (0.0, oy1 + 0.255)])
        siding_field(p, [(-x - 0.03, x + 0.03, -1.0, oy1 + 0.05)]); frieze(p)
        p.merge(wall_lantern(), tr(x + 0.38, 1.85, 0.0)); return p
    if kind == 'win': ow, oy0, oy1, li = 0.9, 0.8, 2.3, 2
    elif kind == 'small': ow, oy0, oy1, li = 0.6, 1.5, 2.3, 1
    else: ow = 0
    wall_with_opening(p, 'siding', ow, oy0 if ow else 0, oy1 if ow else 0, h)
    holes = [window(p, ow, oy0, oy1, li)] if ow else []
    if kind == 'win' and not ns: shutters(p, ow, oy0, oy1)
    siding_field(p, holes); (water_table if fl == 0 else belt)(p); frieze(p); return p
def hcorner():
    """Cantoneira dos 2 andares, canto do embasamento de pedra, testeira, cintas e frisos."""
    p = Piece(); e = 0.045
    prof_y(p, 'trim', 0.0, 2 * H, [(-T - 0.01, -T - 0.01), (e, -T - 0.01), (e, e - 0.006), (e - 0.006, e), (-T - 0.01, e)])
    p.box('stone', -T - 0.01, 0.01, -RAISE, 0, -T - 0.01, 0.01)
    prof_y(p, 'trim', -0.1, 0.092, [(-T, -T), (e + 0.062, -T), (e + 0.062, e + 0.062), (-T, e + 0.062)])
    p.hull('trim', [(x, y, z) for (x, z) in ((-T, -T), (e + 0.062, -T), (e + 0.062, e + 0.062), (-T, e + 0.062)) for y in (0.092, 0.104)] + [(x, 0.118, z) for (x, z) in ((-T, -T), (e, -T), (e, e), (-T, e))])
    for yb in (FRIEZE, H + FRIEZE): prof_y(p, 'trim', yb - 0.05, yb + 0.02, [(-T, -T), (e + 0.012, -T), (e + 0.012, e + 0.012), (-T, e + 0.012)])
    prof_y(p, 'trim', H + 0.09, H + 0.118, [(-T, -T), (e + 0.012, -T), (e + 0.012, e + 0.012), (-T, e + 0.012)])
    return p

# ============================================================================ oitao (pivo: face externa da parede do oitao, no chao; ao longo de X)
def under(u): return YE + KR * (HZ - abs(u))       # face de baixo do telhado a u da cumeeira
def gable():
    """Oitao de tabuas acima do 2o andar: nucleo, testeira de baixo, fiadas de tabua cortadas sob o telhado, janelinha do sotao
    com venezianas e friso de arremate sob o beiral do oitao."""
    p = Piece(); y0 = lvl(1) + HW; xa = HZ - (y0 - YE) / KR
    tri = Polygon([(-xa, y0), (xa, y0), (0.0, YRIDGE)])
    ow, oy0, oy1 = 0.7, 7.55, 8.45; hole = sbox(-ow / 2, oy0, ow / 2, oy1)
    ext(p, 'siding', tri.difference(hole), -T, 0.0)
    window(p, ow, oy0, oy1, 2); shutters(p, ow, oy0, oy1)
    prof_x(p, 'trim', -xa + 0.02, xa - 0.02, [(0.0, y0 - 0.03), (0.034, y0 - 0.03), (0.034, y0 + 0.12), (0.046, y0 + 0.124), (0.046, y0 + 0.134), (0.0, y0 + 0.148)])
    k = 0
    while True:
        b0 = y0 + 0.148 + k * 0.2; b1 = b0 + 0.23; k += 1
        if b0 > YRIDGE - 0.25: break
        hx = (YRIDGE - 0.18 - b1) / KR
        if hx < 0.05: break
        segs = [(-hx, hx)]
        if b1 > oy0 - 0.08 and b0 < oy1 + 0.26: segs = [(-hx, -ow / 2 - 0.12), (ow / 2 + 0.12, hx)]
        for (a, b) in segs:
            if b - a > 0.02: p.hull('siding', [(x, y, z) for x in (a, b) for (y, z) in ((b0, 0.0), (b0, 0.024), (b1, 0.0), (b1, 0.007))])
    for s in (-1, 1):   # friso sob o beiral do oitao, ao longo da agua
        pts = [(s * 0.0, YRIDGE - 0.01), (s * xa, y0 - 0.0)]
        a = np.array(pts[0]); b = np.array(pts[1]); n = np.array([0.0, -1.0]) * 0.17
        p.hull('trim', [(q_[0], q_[1] + dy, z) for q_ in (a, b) for dy in (0.0, -0.17) for z in (0.0, 0.04)])
    return p

# ============================================================================ telhado de 2 aguas (pivo: origem, chao), agua para +Z
def roof_slope():
    p = Piece(); XE = HX + RAKE; ZE = HZ + OV
    poly = sbox(-XE, 0.0, XE, ZE)
    for s in (-1, 1): poly = poly.difference(sbox(s * CHX - CHW - 0.02, -1, s * CHX + CHW + 0.02, CHD + 0.02))
    f = lambda a, b: YE + KR * (HZ - b)
    sheared(p, 'ceiling', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: ZE - b, lambda d0, d1: sbox(-50, ZE - d1, 50, ZE - d0), ZE + 0.01,
                    lambda v, n: np.stack([v[:, 0] / TILE, (ZE - v[:, 2]) / CS / TILE], 1))
    yb = f(0, ZE)
    prof_x(p, 'trim', -XE - 0.035, XE + 0.035, crect(ZE - 0.02, ZE + 0.03, yb - 0.17, yb + 0.05, 0.006, (0, 1, 1, 0)))
    p.box('trim', -XE, XE, yb - 0.17, yb - 0.15, HZ + 0.001, ZE - 0.02)                                     # forro do beiral
    for xx in np.arange(-XE + 0.6, XE - 0.3, 1.2): p.box('dark', xx - 0.1, xx + 0.1, yb - 0.172, yb - 0.17, HZ + 0.12, HZ + 0.24)  # respiros do beiral
    gutter_run(p, -XE - 0.035, XE + 0.035, ZE + 0.03, yb + 0.02, caps=(True, True))
    for s in (-1, 1):   # testeira do oitao, ao longo da agua
        a, b = sorted((s * XE, s * (XE + 0.035)))
        prof_x(p, 'trim', a, b, [(0.0, f(0, 0) - 0.17), (ZE + 0.03, f(0, ZE + 0.03) - 0.17), (ZE + 0.03, f(0, ZE + 0.03) + 0.135), (0.0, f(0, 0) + 0.135)])
    for s in (-1, 1):   # rufo em volta das chamines
        x0, x1 = s * CHX - CHW - 0.02, s * CHX + CHW + 0.02
        p.hull('metal', [(x, f(0, z) + 0.02 + dy, z) for x in (x0 - 0.06, x1 + 0.06) for z in (CHD + 0.03, CHD + 0.14) for dy in (0.0, 0.11 + (0.02 if z < CHD + 0.1 else 0.0))])
    return p
def ridge_cap(x0, x1):
    p = Piece(); y = YRIDGE + 0.02 + 0.1; d = 0.17
    p.hull('ridge', [(x, yy, z) for x in (x0, x1) for (yy, z) in ((y - d * KR - 0.03, d), (y - d * KR - 0.03, -d), (y + 0.075, 0.0), (y + 0.06, 0.06), (y + 0.06, -0.06), (y - 0.1, 0.0))]); return p
def roof_ridge():
    p = Piece(); XE = HX + RAKE + 0.04
    for (a, b) in ((-XE, -CHX - CHW - 0.03), (-CHX + CHW + 0.03, CHX - CHW - 0.03), (CHX + CHW + 0.03, XE)): p.merge(ridge_cap(a, b))
    return p
def chimney_stack():
    """Chamine de tijolo do sotao ate acima da cumeeira (pivo: centro, piso do sotao): corpo, 2 fiadas de cimalha, capa e 2 manilhas."""
    p = Piece(); y0 = lvl(1) + H; h = YRIDGE + 1.2 - y0; w, d = CHW, CHD
    p.box('brick', -w, w, 0.0, h - 0.25, -d, d)
    p.box('brick', -w - 0.03, w + 0.03, h - 0.25, h - 0.125, -d - 0.03, d + 0.03); p.box('brick', -w - 0.06, w + 0.06, h - 0.125, h, -d - 0.06, d + 0.06)
    p.hull('cap', [(x, y, z) for (x, z) in ((-w - 0.09, -d - 0.09), (w + 0.09, -d - 0.09), (w + 0.09, d + 0.09), (-w - 0.09, d + 0.09)) for y in (h, h + 0.06)] + [(x, h + 0.12, z) for (x, z) in ((-w, -d), (w, -d), (w, d), (-w, d))])
    for zz in (-0.18, 0.18):
        p.cyl('clay', 0.085, h + 0.08, h + 0.42, 0.0, zz, 12); p.cyl('dark', 0.065, h + 0.4, h + 0.425, 0.0, zz, 12); p.cyl('clay', 0.1, h + 0.36, h + 0.42, 0.0, zz, 12)
    return p

# ============================================================================ varanda (pivo: origem, chao)
def porch_deck():
    """Deck de tabuas de 0,14 m ao longo de Z com frestas, pilaretes de pedra, testeira e saia de tabuas com fresta entre os pilaretes."""
    p = Piece(); x0, x1 = -PXW, PXW; z0, z1 = HZ + 0.065, PZ + 0.03
    n = int(round((x1 - x0) / 0.14))
    for i in range(n):
        a = x0 + i * (x1 - x0) / n + 0.003; b = x0 + (i + 1) * (x1 - x0) / n - 0.003
        prof_z(p, 'deck', z0, z1, crect(a, b, PFL - 0.03, PFL, 0.004, (0, 0, 1, 1)))
    p.box('dark', x0 + 0.03, x1 - 0.03, PFL - 0.2, PFL - 0.03, HZ + 0.065, PZ - 0.06)
    for x in POSTS: p.box('stone', x - 0.2, x + 0.2, 0.0, PFL - 0.2, PZ - 0.35, PZ + 0.05)
    p.box('stone', -PXW + 0.0, -PXW + 0.4, 0.0, PFL - 0.2, HZ + 0.065, HZ + 0.45); p.box('stone', PXW - 0.4, PXW, 0.0, PFL - 0.2, HZ + 0.065, HZ + 0.45)
    prof_x(p, 'trim', x0 - 0.03, x1 + 0.03, crect(PZ + 0.05, PZ + 0.08, PFL - 0.26, PFL - 0.03, 0.005, (0, 1, 1, 0)))
    for s in (-1, 1):
        a, b = sorted((s * PXW, s * (PXW + 0.03)))
        prof_z(p, 'trim', HZ + 0.065, PZ + 0.05, crect(a, b, PFL - 0.26, PFL - 0.03, 0.005))
    gaps = [(x - 0.2, x + 0.2) for x in POSTS]
    for (a, b) in segs_excl(gaps, x0 + 0.05, x1 - 0.05):            # saia da frente (tabuas verticais com fresta)
        m = max(1, int((b - a) / 0.12))
        for i in range(m): u = a + i * (b - a) / m + 0.008; v = a + (i + 1) * (b - a) / m - 0.008; p.box('trim', u, v, 0.0, PFL - 0.26, PZ - 0.02, PZ + 0.0)
        p.box('dark', a, b, 0.0, PFL - 0.26, PZ - 0.06, PZ - 0.02)
    for s in (-1, 1):
        a, b = HZ + 0.45, PZ - 0.35; m = int((b - a) / 0.12)
        for i in range(m):
            u = a + i * (b - a) / m + 0.008; v = a + (i + 1) * (b - a) / m - 0.008; xa, xb = sorted((s * (PXW - 0.02), s * PXW)); p.box('trim', xa, xb, 0.0, PFL - 0.26, u, v)
        xa, xb = sorted((s * (PXW - 0.06), s * (PXW - 0.02))); p.box('dark', xa, xb, 0.0, PFL - 0.26, a, b)
    return p
def porch_steps(w=1.6, n=4):
    """Degraus de madeira da varanda: 2 pranchas laterais, pisos de tabua com bocel, espelhos e base de pedra (pivo: borda do deck, centro;
    descem para +Z)."""
    p = Piece(); rise = PFL / n; run = 0.3
    for i in range(1, n):
        top = PFL - i * rise; z0 = (i - 1) * run; z1 = i * run + 0.03
        for k in range(3):
            a = -w / 2 + 0.05 + k * (w - 0.1) / 3 + 0.003; b = -w / 2 + 0.05 + (k + 1) * (w - 0.1) / 3 - 0.003
            prof_x(p, 'deck', a, b, crect(z0, z1, top - 0.035, top, 0.006, (0, 1, 1, 0)))
        p.box('trim', -w / 2 + 0.05, w / 2 - 0.05, top - 0.035 - (rise - 0.035), top - 0.035, z0 - 0.0, z0 + 0.025) if i > 1 else None
    for s in (-1, 1):
        a, b = sorted((s * (w / 2 - 0.05), s * w / 2))
        p.hull('trim', [(x, y, z) for x in (a, b) for (z, y) in ((0.0, PFL - 0.03), (0.0, PFL - 0.3), (n * run - 0.2, 0.0), ((n - 1) * run + 0.05, 0.0), ((n - 1) * run + 0.05, rise))])
    p.box('stone', -w / 2 - 0.05, w / 2 + 0.05, -0.1, 0.03, (n - 1) * run + 0.08, n * run + 0.08)
    return p
def porch_post():
    """Coluna torneada (pivo: pe, sobre o deck): base quadrada, fuste com aneis e bojo, colarinho e capitel quadrado."""
    p = Piece(); h = PB - PFL
    p.cham('trim', -0.1, 0.1, 0.0, 0.42, -0.1, 0.1, 0.01); p.cham('trim', -0.1, 0.1, h - 0.38, h, -0.1, 0.1, 0.01)
    prof = [(0.07, 0.42), (0.085, 0.45), (0.085, 0.48), (0.06, 0.52), (0.075, 0.8), (0.085, 1.05), (0.07, 1.3), (0.06, h - 0.62), (0.08, h - 0.5),
            (0.08, h - 0.47), (0.06, h - 0.44), (0.07, h - 0.38)]
    lathe(p, 'trim', [(0.0, 0.42)] + prof + [(0.0, h - 0.38)], sec=14)
    p.cham('trim', -0.12, 0.12, 0.42, 0.46, -0.12, 0.12, 0.008); p.cham('trim', -0.12, 0.12, h - 0.42, h - 0.38, -0.12, 0.12, 0.008)
    return p
def porch_rail(L):
    """Guarda-corpo de um vao (pivo: inicio, sobre o deck; ao longo de +X): corrimao com capa, travessa de baixo, balaustres quadrados."""
    p = Piece(); hb = 0.1; ht = 0.86
    p.cham('trim', 0.0, L, hb, hb + 0.06, -0.035, 0.035, 0.006)
    prof_x(p, 'trim', 0.0, L, [(-0.045, ht), (0.045, ht), (0.045, ht + 0.035), (0.03, ht + 0.06), (-0.03, ht + 0.06), (-0.045, ht + 0.035)])
    p.box('trim', 0.0, L, ht - 0.05, ht, -0.03, 0.03)
    m = int(L / 0.11)
    for i in range(m):
        x = (i + 0.5) * L / m; p.cham('trim', x - 0.02, x + 0.02, hb + 0.06, ht - 0.05, -0.02, 0.02, 0.004)
    for x in (L * 0.33, L * 0.67): p.box('stone', x - 0.05, x + 0.05, 0.0, hb, -0.04, 0.04) if False else p.box('trim', x - 0.03, x + 0.03, 0.0, hb, -0.03, 0.03)
    return p
def porch_roof():
    """Telhado da varanda em uma agua (17 graus) de telhas, forro inclinado, vigas, testeira, calha, rufo na parede e 2 lanternas."""
    p = Piece(); XE = PXW + 0.15; ZE = PZ + POV
    f = lambda a, b: PRY - KP * (b - HZ)
    poly = sbox(-XE, HZ + 0.003, XE, ZE)
    sheared(p, 'ceiling', poly, 0.0, 0.02, f)
    for xx in np.arange(-XE + 0.1, XE - 0.05, 0.1): p.hull('dark', [(xx + dx, f(0, z) - 0.002, z) for dx in (-0.004, 0.004) for z in (HZ + 0.01, ZE - 0.05)] + [(xx, f(0, z) + 0.0005, z) for z in (HZ + 0.01, ZE - 0.05)])
    sheared_courses(p, poly, f, lambda a, b: ZE - b, lambda d0, d1: sbox(-50, ZE - d1, 50, ZE - d0), ZE - HZ + 0.01,
                    lambda v, n: np.stack([v[:, 0] / TILE, (ZE - v[:, 2]) / TILE], 1))
    yb = f(0, ZE)
    prof_x(p, 'trim', -XE - 0.03, XE + 0.03, crect(ZE - 0.02, ZE + 0.03, yb - 0.17, yb + 0.05, 0.006, (0, 1, 1, 0)))
    gutter_run(p, -XE - 0.03, XE + 0.03, ZE + 0.03, yb + 0.02, caps=(True, True))
    for s in (-1, 1):
        a, b = sorted((s * XE, s * (XE + 0.03)))
        prof_x(p, 'trim', a, b, [(HZ + 0.001, f(0, HZ) - 0.17), (ZE + 0.03, f(0, ZE + 0.03) - 0.17), (ZE + 0.03, f(0, ZE + 0.03) + 0.12), (HZ + 0.001, f(0, HZ) + 0.12)])
    prof_x(p, 'trim', -XE, XE, crect(PZ - 0.25, PZ - 0.05, PB, PBT, 0.008))                                            # viga da frente
    p.hull('trim', [(x, y, z) for x in (-XE, XE) for (z, y) in ((PZ - 0.24, PBT), (PZ - 0.06, PBT), (PZ - 0.24, f(0, PZ - 0.24) + 0.001), (PZ - 0.06, f(0, PZ - 0.06) + 0.001))])
    for x in (-PXW + 0.2, PXW - 0.2):                                                                                  # vigas dos lados
        p.box('trim', x - 0.08, x + 0.08, PB + 0.05, PBT, HZ + 0.001, PZ - 0.25)
    p.hull('metal', [(x, f(0, z) + 0.02 + dy, z) for x in (-XE, XE) for z in (HZ + 0.001, HZ + 0.12) for dy in (0.0, 0.11 if z > HZ + 0.1 else 0.2)])
    for x in (-2.0, 2.0): p.merge(porch_lantern(), tr(x, f(0, HZ + 1.2) - 0.0, HZ + 1.2))
    return p

# ============================================================================ pisos, forros, paredes internas, escada (pivo: origem, chao)
INNER = sbox(-HX + T, -HZ + T, HX - T, HZ - T)
KITCH = sbox(1.0 + t_ / 2, -HZ + T, HX - T, HZ - T); BATH = sbox(1.0 + t_ / 2, -HZ + T, HX - T, -0.6 - t_ / 2)
HOLE = sbox(0.0, STZ1, 1.0 - t_ / 2, STZ0 + 0.25)
def boards(p, poly, y0, y1, mat='floor', w=0.14):
    """Assoalho de tabuas ao longo de Z, com frestas finas (fundo escuro)."""
    b = poly.bounds; ext_y(p, 'dark', poly.buffer(-0.003, join_style=2), y0, y1 - 0.004)
    for i in range(int(math.floor(b[0] / w)), int(math.ceil(b[2] / w))):
        q = sbox(i * w + 0.0025, b[1], (i + 1) * w - 0.0025, b[3]).intersection(poly)
        if q.area > 1e-6: ext_y(p, mat, q, y1 - 0.02, y1)
def checker(p, poly, y0, y1, step, ma, mb):
    b = poly.bounds
    for i in range(int(math.floor(b[0] / step)), int(math.ceil(b[2] / step))):
        for j in range(int(math.floor(b[1] / step)), int(math.ceil(b[3] / step))):
            q = sbox(i * step, j * step, (i + 1) * step, (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
def floor0():
    """Terreo: assoalho nos comodos e no hall, linoleo xadrez na cozinha; poraos fechados por baixo."""
    p = Piece(); ext_y(p, 'dark', INNER, 0.02, RAISE - 0.03)
    boards(p, INNER.difference(KITCH), RAISE - 0.03, RAISE); checker(p, KITCH, RAISE - 0.012, RAISE, 0.3, 'lino', 'enamel'); ext_y(p, 'dark', KITCH, RAISE - 0.03, RAISE - 0.012)
    return p
def slab(fl, hole=True, bath=True):
    """Laje de madeira entre andares: forro de gesso embaixo, assoalho (ou ladrilho no banheiro) em cima, furo da escada."""
    p = Piece(); y1 = lvl(fl); y0 = y1 - SLAB; poly = INNER.difference(HOLE) if hole else INNER
    ext_y(p, 'ceiling', poly, y0, y0 + 0.012); ext_y(p, 'planks', poly, y0 + 0.012, y1 - 0.03)
    if bath:
        boards(p, poly.difference(BATH), y1 - 0.03, y1); checker(p, BATH, y1 - 0.012, y1, 0.15, 'porcelain', 'tile'); ext_y(p, 'dark', BATH, y1 - 0.03, y1 - 0.012)
    else: ext_y(p, 'planks', poly, y1 - 0.03, y1)
    if hole:
        for (a, b, c, d) in ((HOLE.bounds[0], HOLE.bounds[0] + 0.01, HOLE.bounds[1], HOLE.bounds[3] - 0.01), (HOLE.bounds[0] + 0.01, HOLE.bounds[2], HOLE.bounds[3] - 0.01, HOLE.bounds[3])):
            p.box('trim', a, b, y0 - 0.0, y1, c, d)
    return p
def plan(fl):
    """Paredes internas de um andar (rebocadas, com guarnicoes e rodapes): hall entre x = -1 e 1, divisoria do banheiro em cima."""
    p = Piece(); zi = HZ - T; hh = H - SLAB
    dw = [(2.95, 0.9, 0.0, 2.1, 'door')] if True else []
    p.merge(run_wall(2 * zi, hh, [(2.95 + zi, 0.9, 0.0, 2.1, 'door')]), rot_y(-90, (-1.0, 0, -zi)))
    de = [(-2.7 + zi, 0.9, 0.0, 2.1, 'door')] + ([(2.95 + zi, 0.9, 0.0, 2.1, 'door')] if fl == 1 else [])
    p.merge(run_wall(2 * zi, hh, de), rot_y(-90, (1.0, 0, -zi)))
    if fl == 1: p.merge(run_wall(HX - T - 1.0 - t_ / 2, hh), tr(1.0 + t_ / 2, 0, -0.6))
    gaps = [sbox(-0.6, HZ - T - 0.1, 0.6, HZ), sbox(-0.6, -HZ, 0.6, -HZ + T + 0.1)] if fl == 0 else []
    ring = INNER.difference(INNER.buffer(-0.016, join_style=2))
    for g in gaps: ring = ring.difference(g)
    for g in (sbox(-1.0 - t_ / 2 - 0.02, -9, -1.0 + t_ / 2 + 0.02, 9), sbox(1.0 - t_ / 2 - 0.02, -9, 1.0 + t_ / 2 + 0.02, 9)): ring = ring.difference(g)
    if fl == 1: ring = ring.difference(sbox(1.0, -0.6 - t_ / 2 - 0.02, 9, -0.6 + t_ / 2 + 0.02))
    if fl == 0: ring = ring.difference(sbox(-9, -0.85, -HX + T + 0.1, 0.85)).difference(sbox(HX - T - 0.1, -0.6, 9, 0.6))
    ext_y(p, 'trim', ring, 0.0, 0.12)
    return p
def stair():
    """Escada reta de 16 espelhos (pivo: origem, chao): pisos com bocel, espelhos, banzo, painel de lambri por baixo, corrimao com
    balaustres e pilar de arranque torneado."""
    p = Piece(); xa, xb = 0.0 + 0.0, 1.0 - t_ / 2; y0 = lvl(0)
    for i in range(NR):
        zf = STZ0 - i * RN; yr0 = y0 + i * RR; yr1 = y0 + (i + 1) * RR
        if i < NR - 1:
            prof_x(p, 'deck', xa + 0.06, xb - 0.002, crect(zf - RN, zf + 0.03, yr1 - 0.03, yr1, 0.008, (0, 1, 1, 0)))
            p.box('trim', xa + 0.06, xb - 0.002, yr0 if i == 0 else yr0 - 0.0, yr1 - 0.03, zf - 0.02, zf)
        else: p.box('trim', xa + 0.06, xb - 0.002, yr0, yr1 - 0.004, STZ1, STZ1 + 0.02)
    p.hull('trim', [(x, y, z) for x in (xa, xa + 0.06) for (z, y) in ((STZ0 + 0.03, y0), (STZ0 + 0.03, y0 + RR + 0.12), (STZ1, lvl(1) - 0.004), (STZ1, lvl(1) - SLAB - 0.15))])
    p.hull('trim', [(x, y, z) for x in (xa + 0.012, xa + 0.05) for (z, y) in ((STZ0 - 0.02, y0), (STZ1 + 0.02, y0), (STZ1 + 0.02, lvl(1) - SLAB - 0.17), (STZ0 - 0.02, y0 + 0.08))])
    for i in range(1, NR - 1):
        zc = STZ0 - i * RN + RN / 2; yt = y0 + (i + 1) * RR
        p.cham('trim', xa + 0.01, xa + 0.05, yt, yt + 0.86, zc - 0.02, zc + 0.02, 0.004)
    a = np.array([xa + 0.03, y0 + 2 * RR + 0.88, STZ0 - RN]); b = np.array([xa + 0.03, y0 + NR * RR + 0.88, STZ1])
    p.seg('dkwood', tuple(a + [0, 0, 0.3]), tuple(b), 0.06, 0.05)
    lathe(p, 'dkwood', [(0.0, y0 + 0.002), (0.07, y0 + 0.002), (0.07, y0 + 0.15), (0.05, y0 + 0.2), (0.045, y0 + 0.9), (0.06, y0 + 1.0), (0.06, y0 + 1.12), (0.03, y0 + 1.18), (0.0, y0 + 1.2)], xa + 0.03, STZ0 - 0.1, 0.0, 12)
    return p
def stair_rail():
    """Guarda-corpo do furo da escada no 2o andar (pivo: origem, chao)."""
    p = Piece(); y = lvl(1); x0, z0, x1, z1 = HOLE.bounds
    q = porch_rail(z1 - z0 - 0.06); p.merge(q, rot_y(-90, (x0 - 0.04, y, z0 + 0.06)))
    q = porch_rail(x1 - x0 + 0.0); p.merge(q, tr(x0 - 0.04, y, z1 + 0.05))
    for (x, z) in ((x0 - 0.04, z1 + 0.05), (x0 - 0.04, z0 + 0.06)): p.cham('dkwood', x - 0.05, x + 0.05, y, y + 1.0, z - 0.05, z + 0.05, 0.008)
    return p
def fireplace():
    """Lareira de tijolo com cornija de madeira, misulas, boca escura com grelha e lenha, e peito de tijolo ate o forro
    (pivo: face da parede, piso; frente +Z)."""
    p = Piece(); w = 0.85; d = 0.5; hh = H - SLAB
    p.box('brick', -w, w, 0, 1.25, 0, d)
    prof_x(p, 'wood', -w - 0.12, w + 0.12, [(0.0, 1.25), (d + 0.1, 1.25), (d + 0.12, 1.265), (d + 0.12, 1.31), (d + 0.09, 1.33), (0.0, 1.33)])
    for s in (-1, 1):
        a, b = sorted((s * (w - 0.02), s * (w - 0.12))); p.hull('wood', [(x, y, z) for x in (a, b) for (z, y) in ((d, 1.25), (d + 0.09, 1.25), (d, 1.05))])
    p.box('dark', -0.45, 0.45, 0.12, 0.85, d - 0.3, d - 0.12)
    p.box('brick', -0.55, 0.55, 0.85, 1.25, d - 0.12, d + 0.001) if False else None
    p.box('dark', -0.45, 0.45, 0.12, 0.85, d - 0.121, d - 0.12)
    for (a, b) in ((-w, -0.45), (0.45, w)): pass
    for xx in (-0.25, 0.0, 0.25): p.seg('iron', (xx, 0.13, d - 0.25), (xx, 0.13, d - 0.15), 0.02)
    p.box('iron', -0.3, 0.3, 0.2, 0.22, d - 0.28, d - 0.14)
    for (x0_, x1_, y_) in ((-0.25, 0.2, 0.26), (-0.15, 0.25, 0.32)): p.seg('bark', (x0_, y_, d - 0.2), (x1_, y_ + 0.02, d - 0.22), 0.09)
    prof_x(p, 'stone', -w - 0.1, w + 0.1, crect(d, d + 0.45, 0.0, 0.06, 0.01, (0, 1, 1, 0)))
    p.box('brick', -0.6, 0.6, 1.33, hh, 0, 0.4)
    for k in range(3): p.cyl('brass', 0.04, 1.33, 1.5 + 0.05 * k, -0.5 + 0.5 * k, 0.15, 10) if k != 1 else p.cham('wood', -0.2, 0.2, 1.33, 1.65, 0.05, 0.12, 0.01)
    return p
def chimney_breast(): p = Piece(); p.box('brick', -0.5, 0.5, 0.0, H - SLAB, 0.0, 0.4); return p
def back_steps(w=1.5, n=4):
    """Degraus de pedra da porta dos fundos com pisos de bocel e muretas (pivo: borda de cima, centro; descem para +Z)."""
    p = Piece(); rise = RAISE / n; run = 0.3
    for i in range(n):
        top = RAISE - (i + 1) * rise if i < n - 1 else 0.02; z0, z1 = i * run, (i + 1) * run
        p.box('stone', -w / 2, w / 2, 0.0, top - 0.04, z0, z1 - 0.02)
        prof_x(p, 'cap', -w / 2 + 0.002, w / 2 - 0.002, [(z0, top - 0.04)] + arc(z1 + 0.012, top - 0.02, 0.02, -math.pi / 2, math.pi / 2, 6) + [(z0, top)])
    L = n * run + 0.05
    for s in (-1, 1):
        a, b = sorted((s * (w / 2), s * (w / 2 + 0.22))); p.box('stone', a, b, 0.0, RAISE - 0.05, 0.0, L)
        p.hull('cap', [(xx, y, z) for xx in (a - 0.02 * (s < 0), b + 0.02 * (s > 0)) for (z, y) in ((0.0, RAISE - 0.05), (0.0, RAISE), (L + 0.03, RAISE - 0.05), (L + 0.03, RAISE - 0.035))])
    return p

# ============================================================================ moveis da casa (pivo: centro de tras, piso; frente +Z)
def legs(p, mat, x, z0, z1, h, r=0.025):
    for xx in (-x, x):
        for zz in (z0, z1): p.cham(mat, xx - r, xx + r, 0.0, h, zz - r, zz + r, 0.004)
def sofa(L=2.0):
    """Sofa de bracos rolados: base de madeira, assento com 3 almofadas, encosto, bracos e pes torneados."""
    p = Piece(); x = L / 2; d = 0.85
    for (xx, zz) in ((-x + 0.08, 0.1), (x - 0.08, 0.1), (-x + 0.08, d - 0.08), (x - 0.08, d - 0.08)): lathe(p, 'dkwood', [(0.0, 0.0), (0.03, 0.0), (0.04, 0.08), (0.025, 0.16), (0.0, 0.16)], xx, zz, 0.0, 8)
    p.cham('fabric', -x, x, 0.16, 0.42, 0.0, d, 0.03); p.cham('fabric', -x + 0.05, x - 0.05, 0.42, 0.9, 0.0, 0.22, 0.05)
    for i in range(3):
        a = -x + 0.2 + i * (L - 0.4) / 3 + 0.01; b = a + (L - 0.4) / 3 - 0.02; p.cham('fabric', a, b, 0.42, 0.55, 0.22, d - 0.02, 0.04)
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x - 0.2))); p.cham('fabric', a, b, 0.42, 0.64, 0.0, d, 0.04); seg_cyl(p, 'fabric', ((a + b) / 2, 0.66, 0.02), ((a + b) / 2, 0.66, d - 0.02), 0.1, 12)
    p.box('dkwood', -x + 0.02, x - 0.02, 0.14, 0.18, d - 0.01, d + 0.012)
    return p
def armchair():
    p = Piece(); p.merge(sofa(0.95)); return p
def rocking_chair():
    """Cadeira de balanco: 2 balancos curvos, pernas, assento de palha, encosto de fusos com travessa curva e bracos."""
    p = Piece(); x = 0.26
    for s in (-1, 1):
        pts = [(s * x, 0.05 + 0.25 * (u / 0.45) ** 2, u) for u in np.linspace(-0.45, 0.55, 8)]
        for a, b in zip(pts[:-1], pts[1:]): p.seg('wood', a, b, 0.035, 0.05)
        p.seg('wood', (s * x, 0.06, 0.4), (s * x, 0.45, 0.42), 0.035, 0.035); p.seg('wood', (s * x, 0.06, 0.02), (s * x, 1.1, -0.08), 0.035, 0.035)
        p.seg('wood', (s * x, 0.66, 0.0), (s * x, 0.68, 0.48), 0.04, 0.06)
    p.cham('hay', -x, x, 0.43, 0.47, 0.0, 0.44, 0.01)
    for i in range(5): xx = -0.18 + i * 0.09; p.seg('wood', (xx, 0.47, 0.0), (xx, 1.02, -0.07), 0.02, 0.02)
    p.seg('wood', (-x, 1.05, -0.075), (x, 1.05, -0.075), 0.06, 0.04)
    return p
def rug(w=2.4, d=1.7):
    p = Piece(); p.box('rug', -w / 2, w / 2, 0.0, 0.006, -d / 2, d / 2); p.box('hay', -w / 2 + 0.12, w / 2 - 0.12, 0.006, 0.009, -d / 2 + 0.12, d / 2 - 0.12)
    p.box('rug', -w / 2 + 0.25, w / 2 - 0.25, 0.009, 0.012, -d / 2 + 0.25, d / 2 - 0.25); return p
def oil_lamp(p, x, y, z):
    lathe(p, 'brass', [(0.0, y), (0.06, y), (0.065, y + 0.02), (0.04, y + 0.06), (0.06, y + 0.12), (0.03, y + 0.18), (0.0, y + 0.18)], x, z, 0.0, 12)
    lathe(p, 'lamp_glass', [(0.0, y + 0.18), (0.035, y + 0.18), (0.05, y + 0.24), (0.025, y + 0.32), (0.02, y + 0.4), (0.0, y + 0.4)], x, z, 0.0, 12)
def side_table(lamp=True):
    p = Piece(); legs(p, 'dkwood', 0.2, 0.06, 0.34, 0.66, 0.02); p.cham('dkwood', -0.25, 0.25, 0.66, 0.7, 0.0, 0.4, 0.008)
    p.cham('dkwood', -0.21, 0.21, 0.55, 0.63, 0.04, 0.36, 0.006)
    if lamp: oil_lamp(p, 0.05, 0.7, 0.2)
    return p
def bookcase(L=1.0, h=1.9):
    p = Piece(); x = L / 2; d = 0.32; rng = np.random.default_rng(5)
    p.box('dkwood', -x, -x + 0.03, 0, h, 0, d); p.box('dkwood', x - 0.03, x, 0, h, 0, d); p.box('dkwood', -x + 0.03, x - 0.03, 0, h, 0, 0.015)
    cols = ['quilt', 'fabric', 'green_v', 'hay', 'rug', 'dkwood']
    for k in range(5):
        y = 0.06 + k * (h - 0.1) / 4.6; p.cham('dkwood', -x + 0.03, x - 0.03, y - 0.03, y, 0.015, d, 0.004)
        if k < 4:
            xx = -x + 0.05
            while xx < x - 0.1:
                bw = rng.uniform(0.03, 0.06); bh = rng.uniform(0.2, 0.3); p.cham(cols[int(rng.integers(6))], xx, xx + bw - 0.003, y, y + bh, 0.03, d - 0.03 - rng.uniform(0, 0.03), 0.003); xx += bw
    p.cham('dkwood', -x - 0.02, x + 0.02, h, h + 0.05, 0.0, d + 0.03, 0.008)
    return p
def hall_tree():
    """Cabideiro de hall: banco com tampa, espelho com moldura e 4 ganchos de latao."""
    p = Piece(); p.cham('dkwood', -0.5, 0.5, 0.0, 0.45, 0.0, 0.38, 0.01); p.cham('dkwood', -0.52, 0.52, 0.45, 0.49, 0.0, 0.42, 0.008)
    p.box('dkwood', -0.5, 0.5, 0.49, 1.9, 0.0, 0.03); p.box('dkwood', -0.3, 0.3, 1.0, 1.6, 0.03, 0.05); p.box('glass', -0.24, 0.24, 1.06, 1.54, 0.05, 0.053)
    for x in (-0.42, -0.36, 0.36, 0.42): p.seg('brass', (x, 1.7, 0.03), (x, 1.62, 0.14), 0.016)
    p.cham('dkwood', -0.55, 0.55, 1.9, 1.98, -0.01, 0.08, 0.01); return p
def wood_stove():
    """Fogao a lenha de ferro fundido: corpo, forno com porta e puxador, fornalha, 4 bocas com tampas, estufa em cima, pes curvos,
    cano ate o forro."""
    p = Piece(); w = 0.55; d = 0.7
    for xx in (-w + 0.06, w - 0.06):
        for zz in (0.08, d - 0.08): p.hull('iron', [(xx + dx, 0.0, zz + dz) for dx in (-0.03, 0.03) for dz in (-0.03, 0.03)] + [(xx, 0.2, zz)])
    p.cham('iron', -w, w, 0.18, 0.8, 0.0, d, 0.02); p.cham('iron', -w - 0.03, w + 0.03, 0.8, 0.84, -0.02, d + 0.03, 0.01)
    for (a, b) in ((-w + 0.05, -0.05), (0.05, w - 0.05)): p.cham('chrome', a, b, 0.25, 0.7, d, d + 0.02, 0.01)
    p.seg('chrome', (0.15, 0.62, d + 0.05), (0.4, 0.62, d + 0.05), 0.02)
    for (x, z) in ((-0.28, 0.2), (0.0, 0.2), (-0.28, 0.48), (0.0, 0.48)): p.cyl('dark', 0.11, 0.84, 0.85, x, z, 16)
    p.box('iron', 0.2, w, 0.84, 0.95, 0.0, d) if False else p.cham('iron', 0.22, w, 0.84, 0.94, 0.05, d - 0.05, 0.01)
    p.box('iron', -w, w, 0.84, 1.45, 0.0, 0.08); p.cham('iron', -w, w, 1.2, 1.45, 0.0, 0.3, 0.01); p.box('chrome', -w + 0.02, w - 0.02, 1.15, 1.2, 0.08, 0.3)
    p.cyl('iron', 0.075, 1.45, H - SLAB, 0.25, 0.1, 14); p.cyl('iron', 0.09, 1.9, 1.94, 0.25, 0.1, 14)
    return p
def sink_cabinet():
    """Pia de cozinha: armario de 2 portas, tampo de madeira, cuba esmaltada, bomba manual de ferro e escorredor."""
    p = Piece(); x = 0.7; d = 0.6
    p.cham('wood', -x, x, 0.0, 0.86, 0.0, d, 0.01); p.cham('wood', -x - 0.02, x + 0.02, 0.86, 0.9, 0.0, d + 0.03, 0.006)
    for (a, b) in ((-x + 0.04, -0.02), (0.02, x - 0.04)):
        p.cham('wood', a, b, 0.08, 0.8, d, d + 0.02, 0.006); p.box('dkwood', a + 0.06, b - 0.06, 0.16, 0.72, d + 0.02, d + 0.024)
        p.sphere('brass', 0.015, (b - 0.05) if a < 0 else (a + 0.05), 0.55, d + 0.035)
    p.box('enamel', -0.45, 0.25, 0.9, 0.93, 0.08, 0.52); p.box('dark', -0.4, 0.2, 0.92, 0.931, 0.13, 0.47)
    p.cyl('iron', 0.05, 0.9, 1.3, 0.35, 0.2, 12); p.seg('iron', (0.35, 1.2, 0.2), (0.15, 1.15, 0.3), 0.03); p.seg('iron', (0.35, 1.3, 0.2), (0.35, 1.45, 0.42), 0.022)
    p.box('wood', -x + 0.02, x - 0.02, 0.9, 1.4, 0.0, 0.02) if False else p.box('tile', -x, x, 0.9, 1.4, 0.0, 0.01)
    return p
def icebox():
    p = Piece(); p.cham('wood', -0.4, 0.4, 0.08, 1.35, 0.0, 0.55, 0.015); legs(p, 'wood', 0.36, 0.04, 0.5, 0.08, 0.03)
    for (y0, y1) in ((0.15, 0.7), (0.78, 1.28)):
        p.cham('wood', -0.36, 0.0, y0, y1, 0.55, 0.57, 0.006); p.cham('wood', 0.02, 0.36, y0, y1, 0.55, 0.57, 0.006)
        for xx in (-0.06, 0.08): p.box('brass', xx - 0.012, xx + 0.012, (y0 + y1) / 2 - 0.05, (y0 + y1) / 2 + 0.05, 0.57, 0.585)
    for (y) in (0.3, 1.0): p.box('brass', -0.36, -0.32, y, y + 0.08, 0.57, 0.58)
    return p
def hutch():
    """Armario de cozinha (aparador com prateleiras de vidro em cima, pratos e jarras)."""
    p = Piece(); x = 0.5
    p.cham('wood', -x, x, 0.0, 0.9, 0.0, 0.5, 0.01); p.cham('wood', -x - 0.02, x + 0.02, 0.9, 0.93, 0.0, 0.52, 0.006)
    for (a, b) in ((-x + 0.04, -0.02), (0.02, x - 0.04)): p.cham('wood', a, b, 0.08, 0.84, 0.5, 0.52, 0.006)
    p.box('wood', -x, x, 0.93, 2.0, 0.0, 0.03); p.box('wood', -x, -x + 0.03, 0.93, 2.0, 0.03, 0.32); p.box('wood', x - 0.03, x, 0.93, 2.0, 0.03, 0.32)
    p.cham('wood', -x - 0.03, x + 0.03, 2.0, 2.06, -0.01, 0.36, 0.01)
    for y in (1.3, 1.65): p.box('wood', -x + 0.03, x - 0.03, y - 0.02, y, 0.03, 0.32)
    for i in range(4): xx = -0.33 + i * 0.22; disc = trimesh.creation.cylinder(radius=0.09, height=0.012, sections=20); disc.apply_translation([xx, 1.4, 0.06]); p.add('enamel', disc)
    for i in range(3): xx = -0.25 + i * 0.25; lathe(p, 'quilt' if i % 2 else 'enamel', [(0.0, 1.65), (0.05, 1.65), (0.06, 1.75), (0.035, 1.82), (0.0, 1.82)], xx, 0.18, 0.0, 10)
    for (a, b) in ((-x + 0.03, -0.01), (0.01, x - 0.03)):
        for (u0, u1, v0, v1) in ((a, a + 0.04, 0.96, 1.97), (b - 0.04, b, 0.96, 1.97), (a, b, 0.96, 1.0), (a, b, 1.93, 1.97)): p.cham('wood', u0, u1, v0, v1, 0.32, 0.345, 0.004)
        p.box('glass', a + 0.04, b - 0.04, 1.0, 1.93, 0.33, 0.334)
    return p
def ladder_chair():
    """Cadeira de encosto de travessas e assento de palha (pivo: centro do assento no chao; frente +Z)."""
    p = Piece(); x = 0.21
    for s in (-1, 1):
        p.seg('wood', (s * x, 0.0, 0.2), (s * x, 0.45, 0.2), 0.035, 0.035); p.seg('wood', (s * x, 0.0, -0.2), (s * x, 1.0, -0.24), 0.035, 0.035)
    p.cham('hay', -x, x, 0.42, 0.46, -0.21, 0.22, 0.01)
    for y in (0.65, 0.8, 0.95): p.seg('wood', (-x, y, -0.2 - 0.04 * (y - 0.45) / 0.55), (x, y, -0.2 - 0.04 * (y - 0.45) / 0.55), 0.06, 0.02)
    for y in (0.15,): p.seg('wood', (-x, y, 0.2), (x, y, 0.2), 0.02, 0.02); p.seg('wood', (-x, y, -0.2), (x, y, -0.2), 0.02, 0.02)
    return p
def kitchen_table():
    p = Piece(); legs(p, 'wood', 0.6, -0.35, 0.35, 0.72, 0.03); p.cham('wood', -0.75, 0.75, 0.72, 0.76, -0.45, 0.45, 0.01)
    p.box('linen', -0.5, 0.5, 0.76, 0.763, -0.47, 0.47); oil_lamp(p, 0.0, 0.763, 0.0)
    for (x, z, ry) in ((0.0, -0.75, 0), (0.0, 0.75, 180), (-1.05, 0.0, 90), (1.05, 0.0, -90)): p.merge(ladder_chair(), rot_y(ry, (x, 0, z)))
    return p
def bed(w=1.4, L=2.0):
    """Cama de casal: cabeceira e peseira de ferro com fusos e bolas de latao, colchao, lencol, colcha de retalhos e 2 travesseiros
    (pivo: centro da cabeceira, piso; pes para +Z)."""
    p = Piece(); x = w / 2
    for (z, hh) in ((0.03, 1.2), (L - 0.03, 0.85)):
        for s in (-1, 1): p.cyl('iron', 0.025, 0.0, hh, s * x, z, 10); p.sphere('brass', 0.04, s * x, hh + 0.03, z, 1)
        seg_cyl(p, 'iron', (-x, hh - 0.05, z), (x, hh - 0.05, z), 0.018, 8); seg_cyl(p, 'iron', (-x, 0.45, z), (x, 0.45, z), 0.018, 8)
        for i in range(1, 9): xx = -x + i * w / 9; seg_cyl(p, 'iron', (xx, 0.45, z), (xx, hh - 0.05, z), 0.008, 6)
    p.box('iron', -x, x, 0.3, 0.36, 0.03, L - 0.03)
    p.cham('linen', -x + 0.02, x - 0.02, 0.36, 0.58, 0.05, L - 0.05, 0.05)
    p.cham('quilt', -x - 0.03, x + 0.03, 0.42, 0.6, 0.6, L - 0.02, 0.03); p.box('hay', -x + 0.1, x - 0.1, 0.6, 0.603, 0.75, L - 0.15)
    for i in range(3):
        for j in range(4): p.box(('quilt', 'fabric', 'paint_w')[(i + j) % 3], -x + 0.15 + i * (w - 0.3) / 3, -x + 0.15 + (i + 1) * (w - 0.3) / 3 - 0.02, 0.603, 0.606, 0.8 + j * 0.28, 1.06 + j * 0.28)
    for s in (-1, 1): p.cham('linen', s * 0.33 - 0.28, s * 0.33 + 0.28, 0.58, 0.72, 0.1, 0.5, 0.06)
    return p
def dresser(mirror=True):
    p = Piece(); x = 0.55; d = 0.48
    p.cham('dkwood', -x, x, 0.08, 0.92, 0.0, d, 0.01); legs(p, 'dkwood', x - 0.04, 0.04, d - 0.04, 0.08, 0.03)
    p.cham('dkwood', -x - 0.02, x + 0.02, 0.92, 0.95, 0.0, d + 0.02, 0.006)
    for k in range(3):
        y0 = 0.12 + k * 0.26; p.cham('wood', -x + 0.04, x - 0.04, y0, y0 + 0.23, d, d + 0.02, 0.006)
        for xx in (-0.25, 0.25): p.sphere('brass', 0.016, xx, y0 + 0.115, d + 0.03, 1)
    if mirror:
        for s in (-1, 1): p.box('dkwood', s * 0.4 - 0.025, s * 0.4 + 0.025, 0.95, 1.75, 0.04, 0.08)
        p.cham('dkwood', -0.36, 0.36, 1.05, 1.7, 0.05, 0.08, 0.01); p.box('glass', -0.31, 0.31, 1.1, 1.65, 0.08, 0.083)
        lathe(p, 'enamel', [(0.0, 0.95), (0.09, 0.95), (0.1, 1.05), (0.06, 1.12), (0.0, 1.12)], -0.3, 0.25, 0.0, 12)
    return p
def wardrobe():
    p = Piece(); x = 0.5; d = 0.55
    p.cham('dkwood', -x, x, 0.06, 2.0, 0.0, d, 0.01); p.cham('dkwood', -x - 0.03, x + 0.03, 2.0, 2.08, -0.01, d + 0.04, 0.01)
    for (a, b) in ((-x + 0.04, -0.01), (0.01, x - 0.04)):
        p.cham('wood', a, b, 0.4, 1.95, d, d + 0.02, 0.006); p.box('dkwood', a + 0.07, b - 0.07, 0.5, 1.85, d + 0.02, d + 0.024)
    p.cham('wood', -x + 0.04, x - 0.04, 0.1, 0.36, d, d + 0.02, 0.006)
    for xx in (-0.05, 0.05): p.box('brass', xx - 0.01, xx + 0.01, 1.1, 1.25, d + 0.02, d + 0.035)
    return p
def chest():
    p = Piece(); p.cham('wood', -0.45, 0.45, 0.0, 0.42, 0.0, 0.45, 0.01); p.hull('wood', [(x, y, z) for x in (-0.46, 0.46) for (y, z) in ((0.42, -0.01), (0.42, 0.46), (0.5, 0.02), (0.5, 0.43))])
    for x in (-0.3, 0.3): p.box('iron', x - 0.03, x + 0.03, 0.0, 0.5, 0.455, 0.465)
    p.box('brass', -0.04, 0.04, 0.3, 0.4, 0.455, 0.47); return p
def clawfoot_tub():
    """Banheira de pes de garra: cuba arredondada esmaltada com borda, interior, 4 pes de garra, torneira e ralo (pivo: centro de tras,
    piso; ao longo de X)."""
    p = Piece(); L = 1.6; w = 0.76
    q = trimesh.creation.capsule(height=L - w, radius=w / 2, count=[16, 12]); q.apply_transform(rot_y(90)); q.apply_scale([1.0, 0.75, 1.0])
    q.apply_translation([0, 0.62, w / 2]); q = slice_keep(q, [0, 0.62, 0], [0, -1, 0]); p.add('enamel', q)
    o = sbox(-L / 2 + w / 2, w / 2 - 0.001, L / 2 - w / 2, w / 2 + 0.001).buffer(w / 2 + 0.01, 24)
    ext_y(p, 'enamel', o.difference(o.buffer(-0.05)), 0.62, 0.65); ext_y(p, 'water', o.buffer(-0.05), 0.62, 0.63)
    for (x, z) in ((-0.55, 0.12), (0.55, 0.12), (-0.55, w - 0.12), (0.55, w - 0.12)):
        p.seg('brass', (x, 0.0, z), (x * 0.9, 0.2, z * 0.95 + 0.02), 0.05); p.sphere('brass', 0.04, x, 0.03, z, 1)
    p.cyl('chrome', 0.015, 0.65, 0.85, -L / 2 + 0.08, w / 2, 8); seg_cyl(p, 'chrome', (-L / 2 + 0.08, 0.85, w / 2), (-L / 2 + 0.2, 0.85, w / 2), 0.015, 8)
    return p
def toilet_tank():
    """Vaso com caixa de descarga alta de madeira e corrente (pivo: face da parede, piso; frente +Z)."""
    p = Piece(); lathe(p, 'porcelain', [(0.0, 0.0), (0.13, 0.0), (0.11, 0.2), (0.18, 0.38), (0.18, 0.4), (0.0, 0.4)], 0.0, 0.32, 0.0, 16)
    p.cham('wood', -0.2, 0.2, 0.4, 0.43, 0.12, 0.58, 0.02); p.cham('wood', -0.25, 0.25, 1.8, 2.1, 0.0, 0.22, 0.01)
    p.cyl('chrome', 0.02, 0.4, 1.8, 0.0, 0.1, 8); seg_cyl(p, 'chrome', (0.15, 1.8, 0.15), (0.15, 1.3, 0.2), 0.006, 4); p.sphere('dkwood', 0.03, 0.15, 1.28, 0.2, 1)
    return p
def pedestal_sink():
    p = Piece(); lathe(p, 'porcelain', [(0.0, 0.0), (0.14, 0.0), (0.08, 0.1), (0.07, 0.7), (0.0, 0.7)], 0.0, 0.25, 0.0, 14)
    p.cham('porcelain', -0.3, 0.3, 0.7, 0.85, 0.0, 0.45, 0.04); p.box('chrome', -0.2, 0.2, 0.851, 0.853, 0.12, 0.35)
    for x in (-0.12, 0.12): p.cyl('chrome', 0.015, 0.85, 0.95, x, 0.06, 8)
    p.cham('dkwood', -0.28, 0.28, 1.2, 1.8, 0.0, 0.03, 0.01); p.box('glass', -0.24, 0.24, 1.24, 1.76, 0.03, 0.033)
    return p
def gy(x):   # face de baixo do telhado (forro de tabuas) no ponto x
    xs = [q[0] for q in GU]; ys = [q[1] for q in GU]; return float(np.interp(x, xs, ys))
def offset_line(pts, d, vertical_ends=True):
    P = np.array(pts, float); N = []
    for i in range(len(P) - 1):
        v = P[i + 1] - P[i]; v /= np.linalg.norm(v); N.append(np.array([-v[1], v[0]]))
    out = []
    for i in range(len(P)):
        if i == 0 or i == len(P) - 1:
            j = 0 if i == 0 else len(N) - 1; q = P[i] + d * N[j]
            if vertical_ends:
                v = P[j + 1] - P[j]; v /= np.linalg.norm(v); t = (P[i][0] - q[0]) / v[0]; q = q + t * v
            out.append(q)
        else:
            m = N[i - 1] + N[i]; m /= np.linalg.norm(m); out.append(P[i] + m * d / np.dot(m, N[i]))
    return [tuple(q) for q in out]
def band(pts, d0, d1): return offset_line(pts, d0) + offset_line(pts, d1)[::-1]
def clip_line(x0, x1):
    pts = [(x0, gy(x0))] + [q for q in GU if x0 < q[0] < x1] + [(x1, gy(x1))]; return pts
DK = 0.025; MS = 0.02     # forro de tabuas e chapa
def ytop(x): return gy(x) + (DK + MS) / math.cos(math.atan(T1 if abs(x) > BW - R1 else T2))
def barn_roof(z0=-1.0, z1=1.0, rake=False):
    """Faixa de 2 m (ao longo de Z) do telhado holandes inteiro: forro de tabuas, chapa, nervuras a cada 0,4 m, cumeeira,
    testeiras, calhas dos 2 beirais, caibros e tirante por dentro. Pivo: eixo do celeiro, cota do piso do celeiro."""
    p = Piece()
    prof_z(p, 'planks', z0, z1, band(GU, 0.0, DK)); prof_z(p, 'metal', z0, z1, band(GU, DK, DK + MS))
    zs = [z for z in np.arange(-0.8, (1.21 if rake else 0.81), 0.4)]
    for zc in zs: prof_z(p, 'metal', zc - 0.012, zc + 0.012, band(GU, DK + MS, DK + MS + 0.032))
    zc0, zc1 = z0 - 0.0, z1 + (0.04 if rake else 0.0)
    yt = ytop(0.3)
    prof_z(p, 'metal', zc0, zc1, [(-0.32, ytop(-0.32) - 0.006), (-0.32, ytop(-0.32) + 0.045), (0.0, ytop(0.0) + 0.1), (0.32, ytop(0.32) + 0.045), (0.32, ytop(0.32) - 0.006), (0.0, ytop(0.0) + 0.02)])
    ye = GU[0][1]
    for s in (-1, 1):
        xa, xb = sorted((s * (BW + OVB), s * (BW + OVB + 0.03)))
        prof_z(p, 'trim', z0 + 0.001 * (not rake and False), z1 + (0.03 if rake else 0.0), crect(xa, xb, ye - 0.16, ye + 0.05, 0.006))
        g = Piece(); gutter_run(g, *((-(z1 + (0.03 if rake else 0.0)), -z0) if s > 0 else (z0, z1 + (0.03 if rake else 0.0))), 0.0, ye + 0.02, caps=(rake and s > 0, rake and s < 0))
        R = trimesh.transformations.rotation_matrix(s * math.pi / 2, [0, 1, 0])
        for m in g.parts['gutter']: m.apply_transform(R); m.apply_translation([s * (BW + OVB + 0.03), 0, 0]); p.add('gutter', m)
    # caibros e tirante (por dentro), no meio da faixa
    zr = 0.0 if not rake else -0.4
    prof_z(p, 'planks', zr - 0.03, zr + 0.03, band(clip_line(-BW + T, BW - T), -0.16, -0.0001))
    p.box('planks', -(BW - R1) - 0.05, (BW - R1) + 0.05, YK - 0.36, YK - 0.2, zr + 0.03, zr + 0.08)
    if rake:   # testeira ao longo do perfil holandes, na ponta
        prof_z(p, 'trim', z1, z1 + 0.03, band(GU, -0.16, DK + MS + 0.045))
    return p
def battens(p, xa, xb, y0, y1, holes=(), z=0.0):
    n = int(round((xb - xa) / 0.2857))
    for i in range(n):
        xx = xa + (i + 0.5) * (xb - xa) / n; segs = [(y0, y1)]
        for (a, b, c, d) in holes:
            if a - 0.03 < xx < b + 0.03: segs = [s for (u, v) in segs for s in ((u, min(v, c)), (max(u, d), v)) if s[1] - s[0] > 0.02]
        for (u, v) in segs: p.cham('barn', xx - 0.03, xx + 0.03, u, v, z, z + 0.022, 0.006)
def planks_uv(v, n):
    """Projecao em caixa, mas faces horizontais com cor lisa (como o reboco): os topos das camadas internas se cruzam nas quinas."""
    uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1)
    uv[ax == 0] = v[ax == 0][:, [2, 1]]; uv[ax == 2] = v[ax == 2][:, [0, 1]]; uv /= TILE; uv[ax == 1] = 0.37; return uv
def barn_wall_grid(p, xa, xb, h, holes=(), y0=0.1):
    xs = sorted(set([xa, xb] + [v for hh in holes for v in hh[:2]])); ys = sorted(set([y0, h - 0.005, h] + [max(y0, v) for hh in holes for v in hh[2:]]))
    zs = [-T, -T + 0.02, 0.0]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0 and ys[j] >= h - 0.0051: return None
        return 'planks' if k == 0 else 'barn'
    for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)
    p.uv['planks'] = planks_uv
def barn_base(p, xa, xb, gaps=()):
    xs = [xa] + [v for g in gaps for v in g] + [xb]
    for i in range(0, len(xs) - 1):
        top = 0.006 if i % 2 == 1 else 0.1
        p.box('concrete', xs[i], xs[i + 1], -RB, top, -T, 0.03)
    for i in range(0, len(xs) - 1, 2):   # testeira de baixo sobre o baldrame
        if xs[i + 1] - xs[i] > 0.01: prof_x(p, 'trim', xs[i] + 0.001, xs[i + 1] - 0.001, crect(0.0, 0.03, 0.1, 0.24, 0.006, (0, 1, 1, 0)))
def barn_top(p, xa, xb): prof_x(p, 'trim', xa + 0.001, xb - 0.001, crect(0.0, 0.03, YEB - 0.26, YEB, 0.006, (0, 1, 1, 0)))
def barn_window_frame(p, ow=0.9, oy0=1.5, oy1=2.5):
    x = ow / 2; f = 0.05
    p.box('frame', -x, -x + f, oy0, oy1, -0.285, -0.03); p.box('frame', x - f, x, oy0, oy1, -0.285, -0.03)   # batentes na espessura toda da parede
    p.box('frame', -x + f, x - f, oy1 - f, oy1, -0.285, -0.03); p.box('frame', -x + f, x - f, oy0, oy0 + f, -0.285, -0.03)
    p.box('glass', -x + f - 0.004, x - f + 0.004, oy0 + f - 0.004, oy1 - f + 0.004, -0.123, -0.117)
    p.cham('frame', -0.016, 0.016, oy0 + f, oy1 - f, -0.14, -0.1, 0.005); p.cham('frame', -x + f, x - f, (oy0 + oy1) / 2 - 0.016, (oy0 + oy1) / 2 + 0.016, -0.14, -0.1, 0.005)
    for (a, b, c, d) in ((-x - 0.1, -x, oy0 - 0.02, oy1 + 0.1), (x, x + 0.1, oy0 - 0.02, oy1 + 0.1), (-x - 0.1, x + 0.1, oy1, oy1 + 0.1)):
        p.cham('trim', a, b, c, d, 0.0, 0.035, 0.006)
    prof_x(p, 'trim', -x - 0.14, x + 0.14, [(-0.03, oy0 - 0.06), (0.06, oy0 - 0.06), (0.075, oy0 - 0.045), (0.06, oy0 - 0.02), (-0.03, oy0 - 0.02)])
    p.box('trim', -x + f, x - f, oy0 - 0.02, oy0 + 0.012, -0.19, 0.02)
    return (-x - 0.1, x + 0.1, oy0 - 0.06, oy1 + 0.1)
def barn_wall_plain():
    p = Piece(); barn_wall_grid(p, -W / 2, W / 2, YEB); barn_base(p, -W / 2, W / 2); barn_top(p, -W / 2, W / 2); battens(p, -W / 2, W / 2, 0.24, YEB - 0.26); return p
def barn_wall_window():
    p = Piece(); hole = (-0.45, 0.45, 1.5, 2.5); barn_wall_grid(p, -W / 2, W / 2, YEB, [hole]); barn_base(p, -W / 2, W / 2); barn_top(p, -W / 2, W / 2)
    h = barn_window_frame(p); battens(p, -W / 2, W / 2, 0.24, YEB - 0.26, [h]); return p
def barn_wall_door():
    p = Piece(); x = 0.5; oy1 = 2.25
    barn_wall_grid(p, -W / 2, W / 2, YEB, [(-x, x, 0.0, oy1)]); barn_base(p, -W / 2, W / 2, [(-x, x)]); barn_top(p, -W / 2, W / 2)
    p.box('frame', -x, -x + 0.06, 0.0, oy1, -0.2, -0.03); p.box('frame', x - 0.06, x, 0.0, oy1, -0.2, -0.03); p.box('frame', -x, x, oy1 - 0.06, oy1, -0.2, -0.03)
    for (a, b, c, d) in ((-x - 0.12, -x, 0.1, oy1 + 0.12), (x, x + 0.12, 0.1, oy1 + 0.12), (-x - 0.12, x + 0.12, oy1, oy1 + 0.12)): p.cham('trim', a, b, c, d, 0.0, 0.035, 0.006)
    p.box('frame', -x + 0.06, x - 0.06, -0.02, 0.012, -0.2, -0.03)
    battens(p, -W / 2, W / 2, 0.24, YEB - 0.26, [(-x - 0.12, x + 0.12, -1, oy1 + 0.12)]); return p
BDW = 3.6; BDH = 3.3
def barn_wall_bigdoor():
    """Modulo de 4 m com o portao de 3,6 x 3,3 m: batentes, verga, guarnicoes e ferragens do trinco."""
    p = Piece(); x = BDW / 2; L = 2.0
    barn_wall_grid(p, -L, L, YEB, [(-x, x, 0.0, BDH)]); barn_base(p, -L, L, [(-x, x)]); barn_top(p, -L, L)
    p.box('frame', -x, -x + 0.08, 0.0, BDH, -0.24, -0.03); p.box('frame', x - 0.08, x, 0.0, BDH, -0.24, -0.03); p.box('frame', -x, x, BDH - 0.08, BDH, -0.24, -0.03)
    for (a, b, c, d) in ((-x - 0.15, -x, 0.1, BDH + 0.15), (x, x + 0.15, 0.1, BDH + 0.15), (-x - 0.15, x + 0.15, BDH, BDH + 0.15)): p.cham('trim', a, b, c, d, 0.0, 0.04, 0.008)
    p.box('frame', -x + 0.08, x - 0.08, -0.02, 0.012, -0.24, -0.03)
    battens(p, -L, L, 0.24, YEB - 0.26, [(-x - 0.15, x + 0.15, -1, BDH + 0.15)]); return p
def barn_corner():
    p = Piece(); e = 0.045
    prof_y(p, 'trim', -RB, YEB - 0.1, [(-T - 0.01, -T - 0.01), (e, -T - 0.01), (e, e - 0.006), (e - 0.006, e), (-T - 0.01, e)]); return p
def barn_floor():
    p = Piece(); p.box('concrete', -W / 2 + 0.004, W / 2 - 0.004, -RB, 0.0, -W / 2 + 0.004, W / 2 - 0.004); p.box('dark', -W / 2, W / 2, -RB, -0.004, -W / 2, W / 2); return p
def barn_ramp(w=4.2, L=1.2):
    p = Piece(); p.hull('concrete', [(x, y, z) for x in (-w / 2, w / 2) for (z, y) in ((0.03, 0.0), (0.03, -RB), (L, -RB), (L, -RB + 0.01))]); return p
def barn_gable(front=True):
    """Oitao holandes acima do beiral: tabua e mata-junta, faixa de arremate sob o telhado, porta do palheiro e, na frente,
    capuz da talha com viga e gancho. Pivo: face da parede, eixo, cota do piso do celeiro."""
    p = Piece()
    pts = [(-BW, YEB)] + [(q[0], q[1] + 0.01) for q in GU[1:-1]] + [(BW, YEB)]
    prof_z(p, 'barn', -T + 0.02, 0.0, pts); prof_z(p, 'planks', -T, -T + 0.02, [(x, y - (0.005 if y > YEB else 0)) for x, y in pts])
    prof_z(p, 'trim', 0.0, 0.03, band(clip_line(-BW, BW), -0.2, 0.0))
    ld = (-1.0, 1.0, 4.6, 6.8) if front else (-0.6, 0.6, 5.0, 6.4)
    n = int(round(2 * BW / 0.2857))
    for i in range(n):
        xx = -BW + (i + 0.5) * 2 * BW / n; y1 = min(gy(xx - 0.03), gy(xx + 0.03)) - 0.2 - 0.04
        segs = [(YEB, y1)]
        a, b, c, d = ld
        if a - 0.13 < xx < b + 0.13: segs = [s for (u, v) in segs for s in ((u, min(v, c - 0.13)), (max(u, d + 0.13), v)) if s[1] - s[0] > 0.02]
        for (u, v) in segs:
            if v - u > 0.02: p.cham('barn', xx - 0.03, xx + 0.03, u, v, 0.0, 0.022, 0.006)
    a, b, c, d = ld
    p.box('barn', a, b, c, d, 0.0, 0.03)
    for i in range(1, int((b - a) / 0.16)): xx = a + i * (b - a) / int((b - a) / 0.16); p.box('dark', xx - 0.004, xx + 0.004, c + 0.01, d - 0.01, 0.03, 0.032)
    for (u0, u1, v0, v1) in ((a - 0.12, a, c - 0.12, d + 0.12), (b, b + 0.12, c - 0.12, d + 0.12), (a, b, d, d + 0.12), (a, b, c - 0.12, c)): p.cham('trim', u0, u1, v0, v1, 0.0, 0.045, 0.008)
    for (P0, P1) in (((a + 0.05, c + 0.05), (b - 0.05, d - 0.05)), ((a + 0.05, d - 0.05), (b - 0.05, c + 0.05))):
        p.seg('trim', (P0[0], P0[1], 0.045), (P1[0], P1[1], 0.045), 0.1, 0.03)
    if front:   # capuz da talha
        yr = YRB - 0.12; ye = YRB - 0.62; hw = 0.95; L = 1.2
        for s in (-1, 1):
            p.hull('metal', [(x, y + dy, z) for (x, y) in ((0.0, yr), (s * hw, ye)) for z in (0.0, L) for dy in (0.0, 0.025)])
            p.hull('trim', [(x, y + dy, z) for (x, y) in ((0.0, yr), (s * hw, ye)) for z in (L - 0.03, L) for dy in (-0.16, -0.001)])
        p.box('trim', -0.07, 0.07, ye - 0.3, ye - 0.14, -0.1, L - 0.03)
        p.box('iron', -0.012, 0.012, ye - 0.7, ye - 0.3, L - 0.2, L - 0.176); p.cyl('iron', 0.05, ye - 0.33, ye - 0.29, 0, L - 0.19, 12)
        p.box('iron', -0.04, 0.04, ye - 0.74, ye - 0.7, L - 0.22, L - 0.16)
    return p
def barn_door_leaf(w=1.71, h=3.2, t=0.05):
    """Folha do portao: tabuas verticais com frestas, quadro e X brancos, dobradicas de ferro em faixa. Pivo: dobradica, embaixo."""
    p = Piece(); n = int(round(w / 0.18))
    for i in range(n):
        a = i * w / n + 0.003; b = (i + 1) * w / n - 0.003; p.cham('barn', a, b, 0.0, h, -t / 2, t / 2 - 0.01, 0.004)
    p.box('dark', 0.01, w - 0.01, 0.01, h - 0.01, -t / 2 + 0.01, t / 2 - 0.015)
    for sz in (1, -1):   # quadro e X nas 2 faces (a folha da direita vai girada 180 graus)
        z0, z1 = sorted((sz * (t / 2 - 0.01), sz * (t / 2 + 0.02)))
        if sz < 0: z0, z1 = sorted((-t / 2 - 0.02, -t / 2 + 0.001))
        for (a, b, c, d) in ((0.0, 0.14, 0.0, h), (w - 0.14, w, 0.0, h), (0.14, w - 0.14, h - 0.14, h), (0.14, w - 0.14, 0.0, 0.14), (0.14, w - 0.14, h / 2 - 0.07, h / 2 + 0.07)):
            p.cham('trim', a, b, c, d, z0, z1, 0.006)
        zc = sz * (t / 2 + 0.005)
        for (y0, y1) in ((0.14, h / 2 - 0.07), (h / 2 + 0.07, h - 0.14)):
            p.seg('trim', (0.2, y0 + 0.06, zc), (w - 0.2, y1 - 0.06, zc), 0.12, 0.028)
            p.seg('trim', (0.2, y1 - 0.06, zc + sz * 0.001), (w - 0.2, y0 + 0.06, zc + sz * 0.001), 0.12, 0.026)
    for yy in (0.45, h - 0.45):
        p.box('iron', 0.0, 0.7, yy - 0.04, yy + 0.04, t / 2 + 0.02, t / 2 + 0.028); p.cyl('iron', 0.022, yy - 0.06, yy + 0.06, 0.0, t / 2 + 0.01, 10)
    p.box('iron', w - 0.11, w - 0.07, 1.0, 1.4, t / 2 + 0.02, t / 2 + 0.03); p.seg('iron', (w - 0.09, 1.05, t / 2 + 0.03), (w - 0.09, 1.05, t / 2 + 0.08), 0.02)
    p.seg('iron', (w - 0.09, 1.35, t / 2 + 0.03), (w - 0.09, 1.35, t / 2 + 0.08), 0.02); p.box('iron', w - 0.105, w - 0.075, 1.04, 1.36, t / 2 + 0.07, t / 2 + 0.09)
    return p
def barn_small_leaf(w=0.88, h=2.17, t=0.045):
    """Porta de servico do celeiro: tabuas com frestas e Z de travessas, dobradicas em T, trinco."""
    p = Piece(); n = 5
    for i in range(n): a = i * w / n + 0.003; b = (i + 1) * w / n - 0.003; p.cham('barn', a, b, 0.0, h, -t / 2, t / 2, 0.004)
    p.box('dark', 0.01, w - 0.01, 0.01, h - 0.01, -t / 2 + 0.005, t / 2 - 0.005)
    for yy in (0.25, h - 0.25):
        p.cham('trim', 0.04, w - 0.04, yy - 0.07, yy + 0.07, t / 2, t / 2 + 0.025, 0.006); p.cham('trim', 0.04, w - 0.04, yy - 0.07, yy + 0.07, -t / 2 - 0.025, -t / 2, 0.006)
        p.box('iron', 0.0, 0.45, yy - 0.025, yy + 0.025, t / 2 + 0.025, t / 2 + 0.032)
    p.seg('trim', (0.1, 0.3, t / 2 + 0.012), (w - 0.1, h - 0.3, t / 2 + 0.012), 0.12, 0.025)
    p.box('iron', w - 0.1, w - 0.07, 0.95, 1.15, t / 2, t / 2 + 0.012); p.seg('iron', (w - 0.085, 1.0, t / 2), (w - 0.085, 1.0, t / 2 + 0.06), 0.018)
    p.seg('iron', (w - 0.085, 1.0, -t / 2), (w - 0.085, 1.0, -t / 2 - 0.06), 0.018)
    return p


# ============================================================================ celeiro: piso, cupula, jiraus, baias (pivo: centro do celeiro, piso)
def barn_floor_all():
    """Piso do celeiro: corredor de concreto com canaleta, baias de terra batida com palha."""
    p = Piece(); xi, zi = BW - T, BD - T
    ext_y(p, 'concrete', sbox(-LX, -zi, LX, zi), -RB, 0.0)
    for s in (-1, 1):
        a, b = sorted((s * LX, s * xi)); ext_y(p, 'soil', sbox(a, -zi, b, zi), -RB, -0.02)
        rng = np.random.default_rng(3 + s)
        for k in range(40):
            x = rng.uniform(min(a, b) + 0.3, max(a, b) - 0.3); z = rng.uniform(-zi + 0.3, zi - 0.3); r = rng.uniform(0.3, 0.6)
            p.hull('hay', [(x + r * math.cos(t), -0.02, z + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 7)[:-1]] + [(x, 0.03 + 0.02 * (k % 3), z)])
    for s in (-1, 1): p.box('dark', *sorted((s * (LX - 0.05), s * (LX - 0.25))), -0.08, -0.001, -zi + 0.01, zi - 0.01)
    return p
def cupola():
    """Cupula de ventilacao na cumeeira: base de tabua e mata-junta, 4 venezianas brancas, telhado de 4 aguas de chapa com beiral,
    pinaculo e cata-vento (seta e cruz com bolas, sem letras). Pivo: centro da cumeeira, piso do celeiro."""
    p = Piece(); w = 0.85; y0 = ytop(w) - 0.06; y1 = YRB + 0.9; y2 = y1 + 0.9
    p.box('barn', -w, w, y0, y1 - 0.15, -w, w)
    for s in (-1, 1):
        for zz in np.linspace(-w + 0.1, w - 0.1, 7): p.cham('barn', *sorted((s * w, s * (w + 0.02))), y0 + 0.2, y1 - 0.2, zz - 0.025, zz + 0.025, 0.004)
    for s in (-1, 1):
        for (ax, sx) in ((0, s), (2, s)):
            lo, hi = sorted((s * w, s * (w + 0.05)))
            if ax == 0:
                for (u0, u1, v0, v1) in ((-0.5, -0.42, y1 - 0.15, y2 - 0.2), (0.42, 0.5, y1 - 0.15, y2 - 0.2), (-0.5, 0.5, y1 - 0.15, y1 - 0.07), (-0.5, 0.5, y2 - 0.28, y2 - 0.2)): p.box('trim', lo, hi, v0, v1, u0, u1)
                for k in range(7):
                    yy = y1 - 0.02 + k * 0.08; p.hull('paint_w', [(x, yy + dy, z) for z in (-0.42, 0.42) for (x, dy) in ((s * (w - 0.04), 0.035), (s * (w + 0.03), -0.02))])
            else:
                for (u0, u1, v0, v1) in ((-0.5, -0.42, y1 - 0.15, y2 - 0.2), (0.42, 0.5, y1 - 0.15, y2 - 0.2), (-0.5, 0.5, y1 - 0.15, y1 - 0.07), (-0.5, 0.5, y2 - 0.28, y2 - 0.2)): p.box('trim', u0, u1, v0, v1, lo, hi)
                for k in range(7):
                    yy = y1 - 0.02 + k * 0.08; p.hull('paint_w', [(x, yy + dy, z) for x in (-0.42, 0.42) for (z, dy) in ((s * (w - 0.04), 0.035), (s * (w + 0.03), -0.02))])
    p.box('dark', -w + 0.05, w - 0.05, y1 - 0.15, y2 - 0.2, -w + 0.05, w - 0.05)
    for (a, b, c, d) in ((-w, -0.5, y1 - 0.15, y2 - 0.2), (0.5, w, y1 - 0.15, y2 - 0.2)):
        p.box('barn', a, b, c, d, -w, w); p.box('barn', -w, w, c, d, a, b)
    p.cham('trim', -w - 0.08, w + 0.08, y1 - 0.24, y1 - 0.15, -w - 0.08, w + 0.08, 0.01)
    e = w + 0.25; p.hull('metal', [(sx * e, y2 - 0.25, sz * e) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * e, y2 - 0.2, sz * e) for sx in (-1, 1) for sz in (-1, 1)] + [(0, y2 + 0.75, 0)])
    p.cham('trim', -w - 0.02, w + 0.02, y2 - 0.32, y2 - 0.25, -w - 0.02, w + 0.02, 0.008)
    lathe(p, 'copper' if 'copper' in MATS else 'brass', [(0.0, y2 + 0.7), (0.05, y2 + 0.72), (0.06, y2 + 0.8), (0.0, y2 + 0.86)], sec=12)
    p.cyl('iron', 0.012, y2 + 0.86, y2 + 1.9, 0, 0, 8); yv = y2 + 1.35
    for (dx, dz) in ((1, 0), (0, 1)):
        p.seg('iron', (-0.4 * dx, yv, -0.4 * dz), (0.4 * dx, yv, 0.4 * dz), 0.012)
        for s in (-1, 1): p.sphere('brass', 0.03, s * 0.4 * dx, yv, s * 0.4 * dz, 1)
    ya = y2 + 1.7; p.box('iron', -0.55, 0.45, ya - 0.012, ya + 0.012, -0.004, 0.004)
    p.hull('iron', [(0.45, ya + d, z) for d in (-0.08, 0.08) for z in (-0.004, 0.004)] + [(0.65, ya, z) for z in (-0.004, 0.004)])
    p.hull('iron', [(x, ya + d, z) for (x, d) in ((-0.55, 0.0), (-0.75, 0.14), (-0.75, -0.14), (-0.6, 0.0)) for z in (-0.004, 0.004)])
    p.sphere('brass', 0.05, 0, y2 + 1.2, 0, 1)
    return p
def lofts():
    """Jiraus de feno dos 2 lados: pilares e vigas de madeira, barrotes, assoalho, rodape de borda e escada de mao fixa."""
    p = Piece(); xi, zi = BW - T, BD - T
    for s in (-1, 1):
        a, b = sorted((s * LX, s * xi))
        for z in np.linspace(-zi + 0.2, zi - 0.2, 7):
            p.cham('wood', s * LX - 0.1, s * LX + 0.1, 0.0, LOFT - 0.25, z - 0.1, z + 0.1, 0.01)
            p.hull('wood', [(s * LX + s * 0.1, LOFT - 0.25, z + dz) for dz in (-0.05, 0.05)] + [(s * LX + s * 0.6, LOFT - 0.25, z + dz) for dz in (-0.05, 0.05)] + [(s * LX + s * 0.1, LOFT - 0.75, z + dz) for dz in (-0.05, 0.05)])
        p.box('wood', s * LX - 0.12, s * LX + 0.12, LOFT - 0.25, LOFT - 0.05, -zi, zi)
        for z in np.arange(-zi + 0.3, zi, 0.6): p.box('wood', *sorted((s * (LX + 0.12), s * xi)), LOFT - 0.23, LOFT - 0.05, z - 0.04, z + 0.04)
        n = int(round((zi * 2) / 0.2))
        for i in range(n):
            u = -zi + i * 2 * zi / n + 0.003; v = -zi + (i + 1) * 2 * zi / n - 0.003; p.box('planks', a, b, LOFT - 0.05, LOFT, u, v)
        p.box('dark', a, b, LOFT - 0.05, LOFT - 0.048, -zi, zi) if False else None
        p.box('wood', *sorted((s * (LX - 0.02), s * (LX + 0.03))), LOFT, LOFT + 0.2, -zi, zi)
    for k in range(13): y = 0.3 + k * 0.28; p.seg('wood', (-LX + 0.13, y, -0.25), (-LX + 0.13, y, 0.25), 0.04)
    for z in (-0.28, 0.28): p.box('wood', -LX + 0.1, -LX + 0.18, 0.0, LOFT + 0.9, z - 0.03, z + 0.03)
    return p
def stalls():
    """Baias dos 2 lados do corredor: divisorias de tabuas com montantes e cochos de madeira (pivo: centro do celeiro, piso)."""
    p = Piece(); xi, zi = BW - T, BD - T; xf = LX + 0.15
    for s in (-1, 1):
        for z in np.arange(-zi + 3.0, zi - 1.0, 3.0):
            a, b = sorted((s * xf, s * xi))
            for k in range(5): y = 0.08 + k * 0.26; p.cham('planks', a, b, y, y + 0.24, z - 0.03, z + 0.03, 0.004)
            p.cham('wood', s * xf - 0.07, s * xf + 0.07, 0.0, 1.55, z - 0.07, z + 0.07, 0.01)
            p.cham('wood', *sorted((s * (xf + 0.07), s * xi)), 1.38, 1.46, z - 0.05, z + 0.05, 0.006)
        for z in np.arange(-zi + 1.5, zi, 3.0):
            x0, x1 = sorted((s * (xf + 0.05), s * (xf + 0.5)))
            p.hull('wood', [(x, y, zz) for (x, y) in ((x0, 0.3), (x1, 0.3), (x0 - 0.05 * (s > 0) + 0.0, 0.6), (x1 + 0.05 * (s > 0), 0.6)) for zz in (z - 0.9, z + 0.9)])
            p.box('hay', x0 + 0.04, x1 - 0.04, 0.55, 0.58, z - 0.86, z + 0.86)
    return p
def bale():
    """Fardo de feno de 0,9 x 0,45 x 0,36 m com 2 amarras (pivo: centro de baixo)."""
    p = Piece(); p.cham('hay', -0.45, 0.45, 0.0, 0.36, -0.225, 0.225, 0.03)
    for x in (-0.22, 0.22): p.box('dkwood', x - 0.008, x + 0.008, 0.001, 0.359, -0.228, 0.228)
    return p
def pitchfork_rack():
    """Ferramentas na parede: forcado, pa, ancinho e rolo de corda (pivo: face da parede, piso; frente +Z)."""
    p = Piece(); p.box('wood', -0.8, 0.8, 1.55, 1.63, 0.0, 0.04)
    for (x, tool) in ((-0.55, 'fork'), (-0.1, 'shovel'), (0.35, 'rake')):
        p.cyl('wood', 0.018, 0.25, 1.75, x, 0.08, 8); p.seg('iron', (x, 1.6, 0.04), (x, 1.6, 0.1), 0.02)
        if tool == 'fork':
            for dx in (-0.06, -0.02, 0.02, 0.06): p.seg('iron', (x + dx * 0.5, 0.28, 0.08), (x + dx, 0.0, 0.1), 0.012)
        if tool == 'shovel': p.hull('iron', [(x + dx, y, 0.08 + dz) for dx in (-0.12, 0.12) for (y, dz) in ((0.27, 0.0), (0.0, 0.03))] + [(x, -0.05, 0.1)])
        if tool == 'rake': p.box('iron', x - 0.2, x + 0.2, 0.22, 0.26, 0.06, 0.1); [p.seg('iron', (x + dx, 0.22, 0.08), (x + dx, 0.12, 0.12), 0.01) for dx in np.linspace(-0.18, 0.18, 9)]
    lathe(p, 'hay', [(0.12, 1.2), (0.2, 1.22), (0.2, 1.4), (0.12, 1.42)], 0.65, 0.12, 0.0, 14)
    return p
def wheelbarrow():
    p = Piece(); p.hull('galv', [(x, 0.35, z) for x in (-0.3, 0.3) for z in (-0.4, 0.3)] + [(x, 0.65, z) for x in (-0.38, 0.38) for z in (-0.55, 0.42)])
    p.hull('dark', [(x, 0.6, z) for x in (-0.33, 0.33) for z in (-0.5, 0.37)] + [(x, 0.651, z) for x in (-0.36, 0.36) for z in (-0.53, 0.4)])
    for s in (-1, 1): p.seg('wood', (s * 0.25, 0.5, 0.5), (s * 0.3, 0.6, -1.0), 0.04); p.seg('iron', (s * 0.25, 0.35, -0.3), (s * 0.25, 0.0, -0.35), 0.025)
    disc_x(p, 'rubber', 0.2, -0.04, 0.04, 0.2, 0.62, 16); disc_x(p, 'iron', 0.08, -0.05, 0.05, 0.2, 0.62, 10)
    return p

# ============================================================================ silo (pivo: centro da base, chao)
def silo():
    """Silo de aduelas de concreto: cilindro, cintas de aco a cada 0,6 m, cupula de chapa com respiro, calha de descarga com portinholas
    virada para +X, escada de marinheiro com gaiola e base de concreto."""
    p = Piece(); r = SR
    p.cyl('concrete', r + 0.15, 0.0, 0.3, 0, 0, 40); p.cyl('silo_c', r, 0.3, SH, 0, 0, 40)
    for y in np.arange(0.9, SH - 0.2, 0.6):
        m = trimesh.creation.annulus(r_min=r - 0.01, r_max=r + 0.025, height=0.03, sections=40); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, y, 0]); p.add('galv', m)
    prof = [(0.0, SH + 2.0)] + [((r + 0.1) * math.sin(a), SH + 2.0 * math.cos(a)) for a in np.linspace(0.15, math.pi / 2, 9)] + [(r + 0.1, SH - 0.08), (r - 0.05, SH - 0.08)]
    lathe(p, 'metal', prof, sec=40)
    for k in range(16):
        a = 2 * math.pi * k / 16; c, s_ = math.cos(a), math.sin(a)
        p.seg('metal', (0.3 * c, SH + 1.98, 0.3 * s_), ((r + 0.1) * c, SH, (r + 0.1) * s_), 0.04, 0.03)
    p.cyl('metal', 0.35, SH + 1.9, SH + 2.3, 0, 0, 14); lathe(p, 'metal', [(0.0, SH + 2.65), (0.5, SH + 2.3), (0.45, SH + 2.25), (0.0, SH + 2.5)], sec=14)
    x0 = r - 0.15; w = 0.45
    p.box('silo_c', x0, x0 + 0.65, 0.3, SH + 0.5, -w, w); p.hull('metal', [(x0, SH + 1.2, z) for z in (-w - 0.05, w + 0.05)] + [(x0 + 0.72, SH + 0.45, z) for z in (-w - 0.05, w + 0.05)] + [(x0, SH + 0.45, z) for z in (-w - 0.05, w + 0.05)])
    for y in np.arange(1.0, SH - 0.5, 1.6):
        p.cham('wood', x0 + 0.65, x0 + 0.68, y, y + 1.2, -w + 0.06, w - 0.06, 0.006); p.box('iron', x0 + 0.68, x0 + 0.69, y + 0.55, y + 0.65, -0.3, 0.3)
    xl = x0 + 0.95
    for z in (-0.22, 0.22): p.box('iron', xl - 0.02, xl + 0.02, 0.0, SH + 0.6, z - 0.03, z + 0.03)
    for y in np.arange(0.3, SH + 0.5, 0.3): p.seg('iron', (xl, y, -0.22), (xl, y, 0.22), 0.025)
    for y in np.arange(2.6, SH + 0.4, 0.9):
        pts = [(x0 + 0.68 + 0.38 * (1 + math.cos(a)), y, 0.38 * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, 7)]
        for a_, b_ in zip(pts[:-1], pts[1:]): p.seg('iron', a_, b_, 0.04, 0.012)
    for a in np.linspace(-math.pi / 2, math.pi / 2, 5): p.box('iron', x0 + 0.68 + 0.38 * (1 + math.cos(a)) - 0.012, x0 + 0.68 + 0.38 * (1 + math.cos(a)) + 0.012, 2.6, SH + 0.4, 0.38 * math.sin(a) - 0.02, 0.38 * math.sin(a) + 0.02)
    return p

# ============================================================================ cata-vento de agua (pivo: centro da base, chao; roda para +Z)
def windmill():
    """Torre de cantoneiras de 4 pes (10 m), travessas e X, plataforma, cabecote com roda de 18 pas, leme, haste da bomba, bomba e
    sapatas de concreto."""
    p = Piece(); hb, ht, h = 1.5, 0.35, 10.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.seg('galv', (sx * hb, 0.0, sz * hb), (sx * ht, h, sz * ht), 0.07, 0.07); p.box('concrete', sx * hb - 0.25, sx * hb + 0.25, -0.1, 0.15, sz * hb - 0.25, sz * hb + 0.25)
    lv = [0.0, 2.2, 4.4, 6.4, 8.3, h]
    for i in range(len(lv)):
        y = lv[i]; hw = hb + (ht - hb) * y / h
        if i > 0:
            for (a, b) in (((-hw, -hw), (hw, -hw)), ((hw, -hw), (hw, hw)), ((hw, hw), (-hw, hw)), ((-hw, hw), (-hw, -hw))):
                p.seg('galv', (a[0], y, a[1]), (b[0], y, b[1]), 0.05, 0.05)
        if i < len(lv) - 1:
            y2 = lv[i + 1]; hw2 = hb + (ht - hb) * y2 / h
            for (c, d) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
                p.seg('galv', (c[0] * hw, y + 0.05, c[1] * hw), (d[0] * hw2, y2 - 0.05, d[1] * hw2), 0.025, 0.012)
                p.seg('galv', (d[0] * hw, y + 0.05, d[1] * hw), (c[0] * hw2, y2 - 0.05, c[1] * hw2), 0.025, 0.012)
    p.box('wood', -0.8, 0.8, h - 1.25, h - 1.2, -0.8, 0.8)
    p.cyl('galv', 0.06, h, h + 0.5, 0, 0, 10); p.cham('galv', -0.22, 0.22, h + 0.4, h + 0.8, -0.35, 0.35, 0.04)
    yc = h + 0.62; zc = 0.6; R = 1.9
    p.seg('galv', (0, yc, 0.3), (0, yc, zc + 0.15), 0.07)
    for rr in (0.6, R - 0.05):
        pts = [(rr * math.cos(a), yc + rr * math.sin(a), zc) for a in np.linspace(0, 2 * math.pi, 25)]
        for a_, b_ in zip(pts[:-1], pts[1:]): p.seg('galv', a_, b_, 0.03, 0.03)
    for k in range(18):
        a = 2 * math.pi * k / 18; c, s_ = math.cos(a), math.sin(a); t = np.array([-s_, c]) * 0.11
        p.hull('galv', [(rr * c + q * t[0], yc + rr * s_ + q * t[1], zc + q * 0.06) for rr in (0.45, R) for q in (-1, 1)] + [(rr * c, yc + rr * s_, zc + 0.012) for rr in (0.45, R)])
    for k in range(6): a = 2 * math.pi * k / 6; p.seg('galv', (0, yc, zc), (0.62 * math.cos(a), yc + 0.62 * math.sin(a), zc), 0.025)
    p.sphere('galv', 0.12, 0, yc, zc + 0.08, 1)
    p.seg('galv', (0, yc + 0.05, -0.2), (0, yc + 0.2, -2.4), 0.05); p.seg('galv', (0, yc - 0.1, -0.2), (0, yc + 0.05, -2.4), 0.03)
    p.hull('paint_w', [(x, yc + y, z) for x in (-0.006, 0.006) for (y, z) in ((-0.2, -1.6), (0.65, -1.7), (0.75, -2.9), (-0.25, -2.75))])
    p.cyl('iron', 0.015, 0.4, h, 0, 0, 6)
    p.cyl('iron', 0.07, 0.15, 0.95, 0.0, 0.0, 10); p.seg('iron', (0, 0.75, 0), (0.0, 0.75, 2.05), 0.035); p.box('wood', -0.04, 0.04, 0.0, 0.73, 1.2, 1.28); p.cyl('stone', 0.4, 0.0, 0.15, 0, 0, 14)
    return p
def stock_tank():
    """Bebedouro redondo de chapa galvanizada com borda enrolada, aneis de reforco e agua (pivo: centro, chao)."""
    p = Piece(); r = 1.3; h = 0.6
    m = trimesh.creation.annulus(r_min=r - 0.02, r_max=r, height=h, sections=40); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, h / 2, 0]); p.add('galv', m)
    p.cyl('galv', r - 0.02, 0.0, 0.03, 0, 0, 40); p.cyl('water', r - 0.02, 0.03, h - 0.1, 0, 0, 40)
    for y in (0.15, 0.35, h - 0.02):
        m = trimesh.creation.annulus(r_min=r - 0.005, r_max=r + 0.02, height=0.03, sections=40); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, y, 0]); p.add('galv', m)
    return p

# ============================================================================ horta (pivo: origem, chao), cercas, carroca e miudezas
GX0, GZ0, GX1, GZ1 = GARDEN
BEDS = [(GX0 + 0.5 + i * 1.8, GX0 + 1.7 + i * 1.8) for i in range(6)]; BZ0_, BZ1_ = GZ0 + 0.8, GZ1 - 0.8
def corn(p, x, z, rng, y0):
    h = rng.uniform(1.7, 2.2); seg_cyl(p, 'corn', (x, y0, z), (x + rng.uniform(-0.04, 0.04), y0 + h, z + rng.uniform(-0.04, 0.04)), 0.018, 5)
    for k in range(4):
        a = rng.uniform(0, 2 * math.pi); y = y0 + 0.35 + k * h * 0.17; L = rng.uniform(0.45, 0.65); c, s = math.cos(a), math.sin(a)
        p.hull('corn' if k % 2 else 'green_v', [(x, y, z), (x - s * 0.04, y + 0.05, z + c * 0.04), (x + c * L * 0.5 - s * 0.05, y + 0.22, z + s * L * 0.5 + c * 0.05), (x + c * L, y + 0.05, z + s * L)])
    p.hull('tassel', [(x, y0 + h, z), (x + 0.08, y0 + h + 0.22, z), (x - 0.06, y0 + h + 0.2, z + 0.05), (x, y0 + h + 0.25, z - 0.06)])
    a = rng.uniform(0, 2 * math.pi); p.seg('green_v', (x + 0.02 * math.cos(a), y0 + h * 0.55, z + 0.02 * math.sin(a)), (x + 0.1 * math.cos(a), y0 + h * 0.55 + 0.22, z + 0.1 * math.sin(a)), 0.06)
def garden():
    """Horta: 6 canteiros elevados com bordas de tabua; 3 de milho, tomates em estacas, repolhos e aboboras com rama; espantalho."""
    p = Piece(); rng = np.random.default_rng(11); y0 = 0.17
    for i, (a, b) in enumerate(BEDS):
        p.box('dkwood', a, b, 0.0, 0.2, BZ0_, BZ0_ + 0.05); p.box('dkwood', a, b, 0.0, 0.2, BZ1_ - 0.05, BZ1_)
        p.box('dkwood', a, a + 0.05, 0.0, 0.2, BZ0_ + 0.05, BZ1_ - 0.05); p.box('dkwood', b - 0.05, b, 0.0, 0.2, BZ0_ + 0.05, BZ1_ - 0.05)
        p.box('soil', a + 0.05, b - 0.05, 0.0, y0, BZ0_ + 0.05, BZ1_ - 0.05)
        for z in np.arange(BZ0_ + 0.3, BZ1_ - 0.2, 0.5): p.hull('soil', [(x, y0, zz) for x in (a + 0.1, b - 0.1) for zz in (z - 0.15, z + 0.15)] + [(x, y0 + 0.05, z) for x in (a + 0.1, b - 0.1)]) if i >= 3 and False else None
        if i < 3:
            for xr in (a + 0.35, b - 0.35):
                for z in np.arange(BZ0_ + 0.35, BZ1_ - 0.3, 0.42): corn(p, xr + rng.uniform(-0.05, 0.05), z, rng, y0)
        elif i == 3:
            for z in np.arange(BZ0_ + 0.5, BZ1_ - 0.4, 0.8):
                xc = (a + b) / 2; p.box('wood', xc - 0.02, xc + 0.02, y0, y0 + 1.3, z - 0.02, z + 0.02)
                for k in range(5):
                    yy = y0 + 0.2 + k * 0.22; p.sphere('green_v', 0.18 - 0.02 * k, xc + rng.uniform(-0.1, 0.1), yy, z + rng.uniform(-0.1, 0.1), 1)
                for k in range(3): p.sphere('tomato', 0.045, xc + rng.uniform(-0.15, 0.15), y0 + rng.uniform(0.3, 1.0), z + rng.uniform(-0.15, 0.15), 1)
        elif i == 4:
            for xr in (a + 0.32, b - 0.32):
                for z in np.arange(BZ0_ + 0.35, BZ1_ - 0.3, 0.55):
                    p.sphere('green_v', 0.17, xr, y0 + 0.12, z, 1)
                    for k in range(5): aa = k * 2 * math.pi / 5; p.hull('leaf2', [(xr, y0 + 0.05, z), (xr + 0.3 * math.cos(aa), y0 + 0.12, z + 0.3 * math.sin(aa)), (xr + 0.2 * math.cos(aa + 0.4), y0 + 0.2, z + 0.2 * math.sin(aa + 0.4)), (xr + 0.22 * math.cos(aa - 0.4), y0 + 0.16, z + 0.22 * math.sin(aa - 0.4))])
        else:
            for z in np.arange(BZ0_ + 0.8, BZ1_ - 0.5, 1.6):
                xc = (a + b) / 2 + rng.uniform(-0.15, 0.15); r = rng.uniform(0.18, 0.26)
                lathe(p, 'pumpkin', [(0.0, y0), (r * 0.7, y0 + 0.01), (r, y0 + r * 0.6), (r * 0.8, y0 + r * 1.2), (0.03, y0 + r * 1.35), (0.0, y0 + r * 1.3)], xc, z, 0.0, 12)
                p.cyl('green_v', 0.02, y0 + r * 1.3, y0 + r * 1.5, xc, z, 6)
                for k in range(6): aa = rng.uniform(0, 2 * math.pi); d = rng.uniform(0.3, 0.6); p.hull('leaf', [(xc + d * math.cos(aa) + dx, y0 + 0.1, z + d * math.sin(aa) + dz) for (dx, dz) in ((-0.12, 0.0), (0.12, 0.0), (0.0, 0.15), (0.0, -0.1))] + [(xc + d * math.cos(aa), y0 + 0.16, z + d * math.sin(aa))])
    xs, zs = (BEDS[2][1] + BEDS[3][0]) / 2, BZ1_ + 0.3
    p.box('wood', xs - 0.04, xs + 0.04, 0.0, 2.1, zs - 0.04, zs + 0.04); p.box('wood', xs - 0.7, xs + 0.7, 1.55, 1.62, zs - 0.03, zs + 0.03)
    p.hull('fabric', [(xs + x, y, zs + z) for (x, y) in ((-0.55, 1.5), (0.55, 1.5), (-0.25, 1.0), (0.25, 1.0), (-0.3, 1.68), (0.3, 1.68)) for z in (-0.1, 0.1)])
    p.sphere('hay', 0.16, xs, 1.85, zs, 1); lathe(p, 'hay', [(0.0, 1.95), (0.3, 1.95), (0.28, 1.98), (0.12, 2.0), (0.1, 2.15), (0.0, 2.15)], xs, zs, 0.0, 14)
    for s in (-1, 1): p.hull('hay', [(xs + s * 0.55, 1.5, zs), (xs + s * 0.7, 1.45, zs + 0.05), (xs + s * 0.72, 1.58, zs - 0.04), (xs + s * 0.66, 1.52, zs - 0.06)])
    return p
def picket(L=2.0, h=1.0):
    """Cerca de estacas branca (pivo: inicio, chao; ao longo de +X, lado de fora em +Z): mourao com capa, 2 travessas por dentro e estacas
    com ponta."""
    p = Piece(); p.cham('paint_w', -0.045, 0.045, -0.2, h + 0.1, -0.045, 0.045, 0.006); p.hull('paint_w', [(sx * 0.055, h + 0.1, sz * 0.055) for sx in (-1, 1) for sz in (-1, 1)] + [(0, h + 0.17, 0)])
    for y in (0.25, h - 0.15): p.box('paint_w', 0.045, L - 0.045, y - 0.04, y + 0.04, -0.045, -0.005)
    n = int((L - 0.1) / 0.12)
    for i in range(n):
        x = 0.05 + (i + 0.5) * (L - 0.1) / n
        p.hull('paint_w', [(x + dx, y, z) for dx in (-0.035, 0.035) for y in (0.06, h - 0.06) for z in (-0.005, 0.015)] + [(x, h, z) for z in (-0.005, 0.015)])
    return p
def picket_post(h=1.0):
    p = Piece(); p.cham('paint_w', -0.045, 0.045, -0.2, h + 0.1, -0.045, 0.045, 0.006); p.hull('paint_w', [(sx * 0.055, h + 0.1, sz * 0.055) for sx in (-1, 1) for sz in (-1, 1)] + [(0, h + 0.17, 0)]); return p
def picket_gate(L=0.9, h=1.0):
    """Portao de estacas (pivo: dobradica, chao): quadro com diagonal, estacas, 2 dobradicas e trinco."""
    p = Piece()
    for y in (0.2, h - 0.2): p.box('paint_w', 0.02, L - 0.02, y - 0.04, y + 0.04, -0.045, -0.005)
    p.seg('paint_w', (0.06, 0.24, -0.025), (L - 0.06, h - 0.24, -0.025), 0.06, 0.035)
    n = 7
    for i in range(n):
        x = 0.03 + (i + 0.5) * (L - 0.06) / n
        p.hull('paint_w', [(x + dx, y, z) for dx in (-0.035, 0.035) for y in (0.08, h - 0.08) for z in (-0.005, 0.015)] + [(x, h, z) for z in (-0.005, 0.015)])
    for y in (0.2, h - 0.2): p.box('iron', 0.0, 0.18, y - 0.02, y + 0.02, -0.05, -0.045)
    p.box('iron', L - 0.08, L, 0.62, 0.66, -0.05, -0.045); return p
def rail_fence(L=3.0):
    """Cerca de 3 travessas de madeira rustica (pivo: mourao do inicio, chao; ao longo de +X)."""
    p = Piece(); p.cham('rail', -0.07, 0.07, -0.3, 1.3, -0.07, 0.07, 0.015); p.hull('rail', [(sx * 0.07, 1.3, sz * 0.07) for sx in (-1, 1) for sz in (-1, 1)] + [(0, 1.36, 0)])
    rng = np.random.default_rng(int(L * 10))
    for y in (0.35, 0.7, 1.05):
        d = rng.uniform(-0.015, 0.015)
        p.hull('rail', [(x, y + dy + d * (x / L), z) for x in (0.07, L - 0.07) for (dy, z) in ((-0.06, -0.03), (-0.04, 0.035), (0.05, 0.035), (0.06, -0.03))])
    return p
def rail_post():
    p = Piece(); p.cham('rail', -0.07, 0.07, -0.3, 1.3, -0.07, 0.07, 0.015); p.hull('rail', [(sx * 0.07, 1.3, sz * 0.07) for sx in (-1, 1) for sz in (-1, 1)] + [(0, 1.36, 0)]); return p
def wheel(p, r, x0, x1, y, z, n=12):
    m = trimesh.creation.annulus(r_min=r - 0.06, r_max=r, height=x1 - x0, sections=28); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([(x0 + x1) / 2, y, z]); p.add('wood', m)
    m = trimesh.creation.annulus(r_min=r - 0.005, r_max=r + 0.012, height=x1 - x0 - 0.01, sections=28); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([(x0 + x1) / 2, y, z]); p.add('iron', m)
    disc_x(p, 'wood', 0.1, x0 - 0.04, x1 + 0.04, y, z, 12)
    for k in range(n): a = 2 * math.pi * k / n; p.seg('wood', ((x0 + x1) / 2, y + 0.08 * math.sin(a), z + 0.08 * math.cos(a)), ((x0 + x1) / 2, y + (r - 0.05) * math.sin(a), z + (r - 0.05) * math.cos(a)), 0.03)
def hay_wagon():
    """Carroca de feno de madeira (pivo: centro, chao; frente +Z): rodas raiadas com aro de ferro, eixos, estrado com tabuas, fueiros
    e grades nas pontas, lanca."""
    p = Piece(); L = 4.0; w = 1.1; yb = 0.95
    for (z, r) in ((1.4, 0.45), (-1.4, 0.6)):
        for s in (-1, 1): wheel(p, r, s * (w + 0.05), s * (w + 0.05) + 0.08 * s if s > 0 else s * (w + 0.05) + 0.0, r, z) if False else wheel(p, r, *sorted((s * (w + 0.04), s * (w + 0.12))), r, z)
        p.box('dkwood', -w - 0.04, w + 0.04, r - 0.05, r + 0.05, z - 0.05, z + 0.05)
        p.box('dkwood', -w + 0.1, w - 0.1, r + 0.05, yb - 0.08, z - 0.08, z + 0.08)
    for x in (-0.7, 0.0, 0.7): p.box('dkwood', x - 0.06, x + 0.06, yb - 0.12, yb - 0.04, -L / 2, L / 2)
    n = int(2 * w / 0.15)
    for i in range(n): a = -w + i * 2 * w / n + 0.004; b = a + 2 * w / n - 0.008; p.cham('wood', a, b, yb - 0.04, yb, -L / 2, L / 2, 0.004)
    for s in (-1, 1):
        for z in (-1.6, -0.5, 0.5, 1.6): p.cham('wood', s * w - 0.04, s * w + 0.04, yb, yb + 0.8, z - 0.04, z + 0.04, 0.006)
        p.box('wood', *sorted((s * w, s * (w + 0.06))), yb + 0.15, yb + 0.25, -L / 2, L / 2); p.box('wood', *sorted((s * w, s * (w + 0.06))), yb + 0.6, yb + 0.7, -L / 2, L / 2)
    for zz in (-L / 2, L / 2):
        for x in np.linspace(-w + 0.1, w - 0.1, 6): p.box('wood', x - 0.03, x + 0.03, yb, yb + 1.4, zz - 0.03, zz + 0.03)
        for y in (yb + 0.6, yb + 1.35): p.box('wood', -w, w, y, y + 0.06, zz - 0.04, zz + 0.04)
    p.seg('dkwood', (0, 0.45, 1.4), (0, 0.55, 3.6), 0.08); p.seg('iron', (0, 0.55, 3.55), (0, 0.55, 3.75), 0.04)
    return p
def mailbox():
    """Caixa de correio rural: poste de madeira, braco, caixa de chapa com tampa arredondada, porta e bandeira vermelha (frente +Z)."""
    p = Piece(); p.cham('wood', -0.05, 0.05, -0.3, 1.0, -0.05, 0.05, 0.008); p.cham('wood', -0.05, 0.05, 1.0, 1.08, -0.3, 0.12, 0.008)
    p.box('galv', -0.1, 0.1, 1.08, 1.2, -0.3, 0.2); m = trimesh.creation.cylinder(radius=0.1, height=0.5, sections=16); m.apply_translation([0, 1.2, -0.05]); p.add('galv', m)
    p.box('galv', -0.105, 0.105, 1.08, 1.21, 0.2, 0.21)
    p.box('redp', 0.105, 0.115, 1.12, 1.3, -0.12, -0.08); p.box('redp', 0.105, 0.115, 1.25, 1.33, -0.08, 0.06)
    return p
def hand_pump():
    """Poco com bomba manual: mureta redonda de pedra, tampa de tabuas, bomba de ferro com alavanca e bica, balde (pivo: centro, chao)."""
    p = Piece(); m = trimesh.creation.annulus(r_min=0.5, r_max=0.75, height=0.6, sections=24); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.3, 0]); p.add('stone', m)
    p.cyl('dark', 0.5, 0.0, 0.5, 0, 0, 24)
    for i in range(7): x = -0.6 + i * 0.17 + 0.005; p.box('wood', x, x + 0.16, 0.6, 0.64, -0.62 + 0.0, 0.62)
    p.cyl('iron', 0.06, 0.64, 1.3, 0.0, 0.0, 12); lathe(p, 'iron', [(0.0, 1.3), (0.08, 1.3), (0.08, 1.38), (0.03, 1.45), (0.0, 1.45)], sec=12)
    p.seg('iron', (0.0, 1.05, 0.05), (0.0, 1.0, 0.3), 0.04); p.seg('iron', (0.0, 1.35, -0.05), (0.0, 1.6, -0.6), 0.03)
    lathe(p, 'galv', [(0.0, 0.64), (0.1, 0.64), (0.12, 0.9), (0.115, 0.9), (0.095, 0.66), (0.0, 0.66)], 0.25, 0.35, 0.0, 14)
    return p
def woodpile(L=3.0):
    """Pilha de lenha entre 2 estacas, com cepo de rachar e machado (pivo: centro de tras, chao; frente +Z)."""
    p = Piece(); rng = np.random.default_rng(4)
    for x in (-L / 2, L / 2): p.box('wood', x - 0.05, x + 0.05, 0.0, 1.3, 0.0, 0.5)
    for k in range(8):
        y = 0.08 + k * 0.135; n = int((L - 0.1) / 0.14)
        for i in range(n):
            x = -L / 2 + 0.07 + (i + 0.5) * (L - 0.14) / n + (0.035 if k % 2 else 0.0)
            if x > L / 2 - 0.1: continue
            m = trimesh.creation.cylinder(radius=0.065, height=0.48, sections=7)
            m.apply_translation([x, y, 0.25]); p.add('bark' if (i + k) % 3 else 'wood', m)
    p.cyl('bark', 0.25, 0.0, 0.5, 0.6, 1.2, 12); p.cyl('wood', 0.24, 0.5, 0.505, 0.6, 1.2, 12)
    p.seg('wood', (0.6, 0.5, 1.2), (0.7, 1.2, 1.35), 0.035); p.hull('iron', [(0.6 + dx, 0.5 + dy, 1.2 + dz) for (dx, dy, dz) in ((-0.02, 0.0, -0.1), (0.02, 0.0, -0.1), (-0.02, 0.0, 0.08), (0.02, 0.0, 0.08), (0.0, 0.12, 0.0))])
    return p
def clothesline(L=6.0):
    """Varal de 2 postes em T com 3 fios, lencois, colcha e camisas pendurados (pivo: poste do inicio, chao; ao longo de +X)."""
    p = Piece()
    for x in (0.0, L):
        p.cham('wood', x - 0.05, x + 0.05, -0.3, 2.0, -0.05, 0.05, 0.008); p.cham('wood', x - 0.04, x + 0.04, 1.9, 1.98, -0.6, 0.6, 0.008)
    for z in (-0.5, 0.0, 0.5): seg_cyl(p, 'paint_w', (0.0, 1.95, z), (L / 2, 1.88, z), 0.004, 4); seg_cyl(p, 'paint_w', (L / 2, 1.88, z), (L, 1.95, z), 0.004, 4)
    for (x0, x1, z, m, hh) in ((0.6, 2.0, -0.5, 'linen', 1.1), (2.3, 3.6, -0.5, 'quilt', 1.0), (3.9, 5.4, 0.0, 'linen', 1.2), (0.8, 1.4, 0.5, 'fabric', 0.6), (1.7, 2.3, 0.5, 'paint_w', 0.6), (4.2, 4.8, 0.5, 'fabric', 0.55)):
        yt = 1.95 - 0.07 * (1 - abs((x0 + x1) / 2 - L / 2) / (L / 2)) - 0.01
        p.hull(m, [(x, y, z + dz) for x in (x0, x1) for (y, dz) in ((yt, -0.006), (yt, 0.006), (yt - hh, -0.006 + 0.02), (yt - hh, 0.006 + 0.02))])
        for x in (x0 + 0.05, x1 - 0.05): p.box('wood', x - 0.01, x + 0.01, yt - 0.03, yt + 0.03, z - 0.012, z + 0.012)
    return p
def tree(h=6.0, r=1.9, mat='leaf', seed=1, fruit=False):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.0, -0.2), (0.2, -0.2), (0.15, 0.5), (0.1, h * 0.6), (0.0, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    if fruit:
        for _ in range(18):
            a = rng.uniform(0, 2 * math.pi); b = rng.uniform(-0.6, 0.9); rr = r * 1.02
            p.sphere('tomato', 0.06, rr * math.cos(a) * math.cos(b), h * 0.78 + rr * math.sin(b), rr * math.sin(a) * math.cos(b), 1)
    return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('leaf', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('leaf2', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p

# ============================================================================ terreno (pivo: origem, chao)
GY = -0.2
YARD = sbox(-14.0, -13.0, DRIVE[1], -6.5); DRV = sbox(DRIVE[0], -6.5, DRIVE[1], ROAD[0])
PATH_R = [sbox(-0.6, PZ + 1.25, 0.6, 12.2), sbox(0.6, 11.0, DRIVE[0], 12.2)]
APRON_B = sbox(BX - 2.6, BZ + BD, BX + 2.6, BZ + BD + 1.4)
def site():
    """Terreno: gramado, patio e estrada de cascalho, caminho de lajes da varanda ate a estrada de cascalho, rampa de concreto do
    portao do celeiro, estrada asfaltada com acostamento de cascalho e faixa amarela tracejada."""
    p = Piece(); box_ = sbox(SX0, SZ0, SX1, SZ1)
    gravel = unary_union([YARD, DRV]).difference(APRON_B)
    road = sbox(SX0, ROAD[0] + 0.6, SX1, ROAD[1] - 0.6); shoulder = sbox(SX0, ROAD[0], SX1, ROAD[1]).difference(road).difference(DRV)
    ext_y(p, 'gravel', gravel, GY, 0.0); ext_y(p, 'asphalt', road, GY, 0.0); ext_y(p, 'gravel', shoulder, GY, 0.0)
    ext_y(p, 'concrete', APRON_B, GY, 0.05)
    grass = box_.difference(unary_union([gravel, road, shoulder, APRON_B])); ext_y(p, 'grass', grass, GY, 0.0)
    for x in np.arange(SX0 + 0.5, SX1 - 1.0, 4.0): p.box('yellowp', x, x + 2.0, 0.0, 0.004, (ROAD[0] + ROAD[1]) / 2 - 0.06, (ROAD[0] + ROAD[1]) / 2 + 0.06)
    rng = np.random.default_rng(9)
    for g in PATH_R:
        b = g.bounds; along_x = (b[2] - b[0]) > (b[3] - b[1])
        n = int(((b[2] - b[0]) if along_x else (b[3] - b[1])) / 0.7)
        for i in range(n):
            if along_x: a0 = b[0] + i * (b[2] - b[0]) / n + 0.04; q = sbox(a0, b[1] + 0.05, a0 + (b[2] - b[0]) / n - 0.08, b[3] - 0.05)
            else: a0 = b[1] + i * (b[3] - b[1]) / n + 0.04; q = sbox(b[0] + 0.05, a0, b[2] - 0.05, a0 + (b[3] - b[1]) / n - 0.08)
            q = q.intersection(g.buffer(-0.02))
            if q.area > 0.05: ext_y(p, 'stone', q, 0.0, 0.03 + rng.uniform(0, 0.01))
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
pieces = {'h_win0': hwall('win', 0), 'h_plain0': hwall('plain', 0), 'h_door0': hwall('door', 0),
          'h_win1': hwall('win', 1), 'h_win0_ns': hwall('win', 0, True), 'h_win1_ns': hwall('win', 1, True), 'h_small1': hwall('small', 1), 'h_plain1': hwall('plain', 1), 'h_corner': hcorner(), 'h_gable': gable(),
          'roof_slope': roof_slope(), 'roof_ridge': roof_ridge(), 'chimney_stack': chimney_stack(),
          'downspout_house': downspout(YE - KR * OV + 0.02 - 0.12, OV + 0.095),
          'porch_deck': porch_deck(), 'porch_steps': porch_steps(), 'porch_post': porch_post(), 'porch_rail_19': porch_rail(1.9), 'porch_rail_18': porch_rail(1.8),
          'porch_rail_side': porch_rail(HZ * 0 + PZ - 0.25 - HZ - 0.07), 'porch_roof': porch_roof(), 'back_steps': back_steps(),
          'floor0': floor0(), 'slab1': slab(1), 'slab2': slab(2, hole=False, bath=False), 'plan0': plan(0), 'plan1': plan(1), 'stair': stair(), 'stair_rail': stair_rail(),
          'fireplace': fireplace(), 'chimney_breast': chimney_breast(),
          'sofa': sofa(), 'armchair': armchair(), 'rocking_chair': rocking_chair(), 'rug': rug(), 'rug_s': rug(1.6, 1.0), 'side_table': side_table(), 'bookcase': bookcase(),
          'hall_tree': hall_tree(), 'wood_stove': wood_stove(), 'sink_cabinet': sink_cabinet(), 'icebox': icebox(), 'hutch': hutch(), 'kitchen_table': kitchen_table(),
          'bed': bed(), 'dresser': dresser(), 'wardrobe': wardrobe(), 'chest': chest(), 'clawfoot_tub': clawfoot_tub(), 'toilet_tank': toilet_tank(), 'pedestal_sink': pedestal_sink(),
          'door_leaf_front': door_front(0.85, 2.2), 'door_leaf_back': door_back(0.85, 2.2), 'door_leaf_int': door_interior(0.84, 2.07),
          'barn_wall_plain': barn_wall_plain(), 'barn_wall_window': barn_wall_window(), 'barn_wall_door': barn_wall_door(), 'barn_wall_bigdoor': barn_wall_bigdoor(),
          'barn_corner': barn_corner(), 'barn_floor': barn_floor_all(), 'barn_ramp': barn_ramp(), 'barn_ramp_small': barn_ramp(1.3, 0.7),
          'barn_gable_front': barn_gable(True), 'barn_gable_back': barn_gable(False), 'barn_roof': barn_roof(), 'barn_roof_end': barn_roof(z1=1.0 + OVR, rake=True),
          'barn_door_leaf': barn_door_leaf(), 'barn_door_small': barn_small_leaf(), 'downspout_barn': downspout(RB + GU[0][1] + 0.02 - 0.12, OVB + 0.095),
          'cupola': cupola(), 'lofts': lofts(), 'stalls': stalls(), 'bale': bale(), 'tool_rack': pitchfork_rack(), 'wheelbarrow': wheelbarrow(),
          'silo': silo(), 'windmill': windmill(), 'stock_tank': stock_tank(), 'garden': garden(),
          'picket': picket(), 'picket_1': picket(1.0), 'picket_post': picket_post(), 'picket_gate': picket_gate(),
          'rail_fence': rail_fence(3.0), 'rail_fence_2': rail_fence(2.0), 'rail_post': rail_post(),
          'hay_wagon': hay_wagon(), 'mailbox': mailbox(), 'hand_pump': hand_pump(), 'woodpile': woodpile(), 'clothesline': clothesline(),
          'tree': tree(), 'tree_b': tree(5.0, 1.6, 'leaf2', 4), 'tree_f': tree(3.6, 1.4, 'leaf', 7, True), 'bush': bush(), 'site': site(), 'player_scale_ref': player_ref()}

# ============================================================================ montagem: casa
tg = ['house', 'ext']
G0 = {'front': {-4: 'h_win0', -2: 'h_win0', 0: 'h_door0', 2: 'h_win0', 4: 'h_win0'}, 'back': {-4: 'h_win0_ns', -2: 'h_win0', 0: 'h_door0', 2: 'h_win0', 4: 'h_win0_ns'},
      'left': {-3: 'h_win0', -1: 'h_plain0', 1: 'h_plain0', 3: 'h_win0'}, 'right': {-3: 'h_win0', -1: 'h_plain0', 1: 'h_plain0', 3: 'h_win0'}}
G1 = {'front': {-4: 'h_win1', -2: 'h_win1', 0: 'h_win1', 2: 'h_win1', 4: 'h_win1'}, 'back': {-4: 'h_win1_ns', -2: 'h_win1', 0: 'h_win1', 2: 'h_small1', 4: 'h_small1'},
      'left': {-3: 'h_win1', -1: 'h_plain1', 1: 'h_plain1', 3: 'h_win1'}, 'right': {-3: 'h_small1', -1: 'h_plain1', 1: 'h_plain1', 3: 'h_win1'}}
for fl, GG in ((0, G0), (1, G1)):
    y = lvl(fl); ft = tg + [f'floor{fl}']
    for x, k in GG['front'].items(): put(k, x, y, HZ, 0, ft + ['front'])
    for x, k in GG['back'].items(): put(k, x, y, -HZ, 180, ft + ['back'])
    for z, k in GG['left'].items(): put(k, -HX, y, z, -90, ft + ['left'])
    for z, k in GG['right'].items(): put(k, HX, y, z, 90, ft + ['right'])
for (x, z, ry) in ((HX, HZ, 0), (HX, -HZ, 90), (-HX, -HZ, 180), (-HX, HZ, -90)): put('h_corner', x, lvl(0), z, ry, tg)
put('h_gable', HX, 0, 0, 90, tg + ['roof']); put('h_gable', -HX, 0, 0, -90, tg + ['roof'])
put('roof_slope', 0, 0, 0, 0, ['house', 'roof']); put('roof_slope', 0, 0, 0, 180, ['house', 'roof']); put('roof_ridge', 0, 0, 0, 0, ['house', 'roof'])
for s in (-1, 1): put('chimney_stack', s * CHX, lvl(1) + H, 0, 0, ['house', 'roof'])
for x in (-HX + 0.15, HX - 0.15): put('downspout_house', x, 0, -HZ, 180, tg + ['back'])
put('porch_deck', 0, 0, 0, 0, tg + ['front']); put('porch_roof', 0, 0, 0, 0, ['house', 'roof', 'front']); put('porch_steps', 0, 0, PZ + 0.08, 0, tg + ['front'])
for x in POSTS: put('porch_post', x, PFL, PZ - 0.15, 0, tg + ['front'])
for (x0, n) in ((-5.0, 'porch_rail_19'), (-2.9, 'porch_rail_18'), (1.1, 'porch_rail_18'), (3.1, 'porch_rail_19')): put(n, x0, PFL, PZ - 0.15, 0, tg + ['front'])
for s in (-1, 1): put('porch_rail_side', s * POSTS[-1], PFL, HZ + 0.07, -90, tg + ['front'])
put('back_steps', 0, 0, -HZ, 180, tg + ['back'])
for (x, ry) in ((-3.8, 0), (3.8, -20)): put('rocking_chair', x, PFL, 5.0, ry, tg + ['front'])
g0 = ['house', 'floor0']; g1 = ['house', 'floor1']; y0, y1 = lvl(0), lvl(1)
put('floor0', 0, 0, 0, 0, g0); put('slab1', 0, 0, 0, 0, g1); put('slab2', 0, 0, 0, 0, ['house', 'roof'])
put('plan0', 0, y0, 0, 0, g0); put('plan1', 0, y1, 0, 0, g1); put('stair', 0, 0, 0, 0, g0); put('stair_rail', 0, 0, 0, 0, g1)
yf = y0 + 0.013
hx, hz = hinge(0, HZ, 0, -0.425, -0.135); put('door_leaf_front', hx, yf, hz, 0, tg + ['front'], door=90)
hx, hz = hinge(0, -HZ, 180, -0.425, -0.135); put('door_leaf_back', hx, yf, hz, 180, tg + ['back'], door=90)
for (fl, x, zc, op) in ((0, -1.0, 2.95, -90), (0, 1.0, -2.7, 90), (1, -1.0, 2.95, -90), (1, 1.0, 2.95, 90), (1, 1.0, -2.7, 90)):
    put('door_leaf_int', x, lvl(fl) + 0.005, zc - 0.42, -90, ['house', f'floor{fl}'], door=op)
put('fireplace', -HX + T, y0, 0, 90, g0); put('chimney_breast', HX - T, y0, 0, -90, g0)
put('chimney_breast', -HX + T, y1, 0, 90, g1); put('chimney_breast', HX - T, y1, 0, -90, g1)
put('sofa', -2.2, y0, 0.0, -90, g0); put('rug', -2.85, y0, 0.0, 90, g0); put('rocking_chair', -3.5, y0, 2.3, -125, g0); put('armchair', -3.6, y0, -2.3, 30, g0)
put('side_table', -2.0, y0, 1.45, -90, g0); put('bookcase', -2.6, y0, -HZ + T + 0.02, 0, g0); put('hall_tree', -1.0 + t_ / 2, y0, -3.1, 90, g0)
put('wood_stove', HX - T - 0.4, y0, 0.0, -90, g0); put('sink_cabinet', 2.6, y0, -HZ + T, 0, g0); put('icebox', HX - T, y0, -2.6, -90, g0)
put('hutch', 3.0, y0, HZ - T, 180, g0); put('kitchen_table', 2.9, y0, 1.1, 0, g0); put('rug_s', 0.0, y0, 3.15, 0, g0)
put('bed', -HX + T, y1, 2.0, 90, g1); put('dresser', -3.0, y1, -HZ + T, 0, g1); put('wardrobe', -HX + T, y1, -2.2, 90, g1); put('rug', -3.0, y1, 1.9, 90, g1)
put('bed', HX - T, y1, 1.6, -90, g1); put('chest', 2.62, y1, 1.6, -90, g1); put('dresser', 3.0, y1, HZ - T, 180, g1)
put('clawfoot_tub', 3.8, y1, -HZ + T, 0, g1); put('toilet_tank', 2.0, y1, -0.6 - t_ / 2, 180, g1); put('pedestal_sink', 3.3, y1, -0.6 - t_ / 2, 180, g1)

# ============================================================================ montagem: celeiro, silo, cata-vento
bt = ['barn', 'ext']; YB = RB
BS = {'left': {-8: 'P', -6: 'W', -4: 'P', -2: 'P', 0: 'W', 2: 'P', 4: 'W', 6: 'D', 8: 'P'}, 'right': {-8: 'P', -6: 'W', -4: 'P', -2: 'W', 0: 'P', 2: 'W', 4: 'P', 6: 'W', 8: 'D'},
      'front': {-7: 'P', -5: 'W', -3: 'P', 3: 'P', 5: 'W', 7: 'P'}, 'back': {-7: 'P', -5: 'W', -3: 'P', -1: 'P', 1: 'P', 3: 'D', 5: 'W', 7: 'P'}}
BN = {'P': 'barn_wall_plain', 'W': 'barn_wall_window', 'D': 'barn_wall_door'}
for u, k in BS['left'].items(): put(BN[k], BX - BW, YB, BZ + u, -90, bt + ['left'])
for u, k in BS['right'].items(): put(BN[k], BX + BW, YB, BZ + u, 90, bt + ['right'])
for u, k in BS['front'].items(): put(BN[k], BX + u, YB, BZ + BD, 0, bt + ['front'])
for u, k in BS['back'].items(): put(BN[k], BX + u, YB, BZ - BD, 180, bt + ['back'])
put('barn_wall_bigdoor', BX, YB, BZ + BD, 0, bt + ['front'])
for ry, x, z in ((0, BW, BD), (90, BW, -BD), (180, -BW, -BD), (-90, -BW, BD)): put('barn_corner', BX + x, YB, BZ + z, ry, bt)
put('barn_gable_front', BX, YB, BZ + BD, 0, ['barn', 'front']); put('barn_gable_back', BX, YB, BZ - BD, 180, ['barn', 'back'])
for u in range(-8, 9, 2):
    if abs(u) == 8: put('barn_roof_end', BX, YB, BZ + u, 0 if u > 0 else 180, ['barn', 'roof'])
    else: put('barn_roof', BX, YB, BZ + u, 0, ['barn', 'roof'])
put('cupola', BX, YB, BZ, 0, ['barn', 'roof'])
gb = ['barn']
for n in ('barn_floor', 'lofts', 'stalls'): put(n, BX, YB, BZ, 0, gb)
put('barn_ramp', BX, YB, BZ + BD, 0, ['barn', 'front'])
put('barn_ramp_small', BX - BW, YB, BZ + 6, -90, ['barn', 'left']); put('barn_ramp_small', BX + BW, YB, BZ + 8, 90, ['barn', 'right']); put('barn_ramp_small', BX + 3, YB, BZ - BD, 180, ['barn', 'back'])
BDW = 3.6
for s, ry, op in ((-1, 0, 85), (1, 180, -85)): put('barn_door_leaf', BX + s * (BDW / 2 - 0.08), YB + 0.005, BZ + BD - 0.15, ry, bt + ['front'], door=op)
for (x, z, ry) in ((-BW, 6.0, -90), (BW, 8.0, 90), (3.0, -BD, 180)):
    hx, hz = hinge(x, z, ry, -0.44, -0.14); put('barn_door_small', BX + hx, YB + 0.005, BZ + hz, ry, bt, door=85)
for x, z, ry in ((-BW, BD - 0.35, -90), (-BW, -BD + 0.35, -90), (BW, BD - 0.35, 90), (BW, -BD + 0.35, 90)): put('downspout_barn', BX + x, 0, BZ + z, ry, bt)
put('wall_lantern', BX + 2.35, YB + 3.0, BZ + BD + 0.04, 0, ['barn', 'front']) if 'wall_lantern' in pieces else None
put('tool_rack', BX + 3.0, YB, BZ + BD - T, 180, gb); put('wheelbarrow', BX + 1.0, YB, BZ + 4.5, 160, gb)
for (s, z0, nz, layers) in ((-1, -BD + T + 0.4, 10, 2), (1, 1.0, 8, 1)):
    for i in range(nz):
        for xx in (4.0, 5.0, 6.0):
            for ly in range(layers): put('bale', BX + s * xx, YB + LOFT + ly * 0.36, BZ + z0 + i * 0.46, 0, gb)
for (x, z) in ((-1.4, -6.0), (-1.4, -5.54)): put('bale', BX + x, YB, BZ + z, 90, gb)
put('silo', SILO[0], 0, SILO[1], -90, ['silo'])
put('windmill', MILL[0], 0, MILL[1], 0, ['site']); put('stock_tank', MILL[0], 0, MILL[1] + 3.2, 0, ['site'])

# ============================================================================ montagem: horta, cercas, terreno
st = ['site']; put('site', 0, 0, 0, 0, st); put('garden', 0, 0, 0, 0, st)
def run(piece_seq, x0, z0, ry, end_post=None):
    r = math.radians(ry); dx, dz = math.cos(r), -math.sin(r); s = 0.0
    for (n, Ln) in piece_seq: put(n, x0 + dx * s, 0, z0 + dz * s, ry, st); s += Ln
    if end_post: put(end_post, x0 + dx * s, 0, z0 + dz * s, ry, st)
P2 = ('picket', 2.0)
run([P2] * 6, GX0, GZ1, 0); run([P2] * 6, GX1, GZ0, 180); run([P2] * 6, GX0, GZ0, -90)
run([P2] * 3, GX1, GZ1, 90, 'picket_post'); run([P2, P2, ('picket_1', 1.0)], GX1, 4.0, 90)
hx, hz = hinge(GX1, 4.95, 90, 0.0, 0.0); put('picket_gate', GX1, 0, 4.95, 90, st, door=-90)
R3 = ('rail_fence', 3.0); R2 = ('rail_fence_2', 2.0)
FX0_, FX1_, FZ0_ = SX0 + 1.0, SX1 - 1.0, SZ0 + 1.0
run([R3] * 14, FX0_, FZF, 0, 'rail_post'); run([R3] * 4 + [R2] * 2, DRIVE[1], FZF, 0)
run([R3] * 17 + [R2] * 2, FX1_, FZF, 90); run([R3] * 20 + [R2], FX1_, FZ0_, 180); run([R3] * 17 + [R2] * 2, FX0_, FZ0_, -90)
cx, cz, wr = 4.0, -9.8, 90; put('hay_wagon', cx, 0, cz, wr, st)
for (lx, lz, ly) in [(sx, z, 0) for sx in (-0.5, 0.5) for z in np.arange(-1.6, 1.7, 0.46)] + [(sx, z, 1) for sx in (-0.5, 0.5) for z in np.arange(-1.15, 1.2, 0.46)]:
    x_, z_ = hinge(cx, cz, wr, lx, lz); put('bale', x_, 0.95 + ly * 0.36, z_, wr, st)
put('mailbox', DRIVE[1] + 1.2, 0, FZF + 0.9, 0, st); put('hand_pump', -8.0, 0, -3.0, 0, st); put('woodpile', 7.0, 0, -6.0, 0, st); put('clothesline', -16.5, 0, -8.6, 0, st)
for k, (x, z) in enumerate(((7.6, -1.0), (-7.5, 6.5), (16.0, 15.0), (-28.0, 14.0), (-28.0, -20.0), (7.5, -24.0), (-26.0, -31.0), (24.0, 17.0))):
    put('tree' if k % 2 == 0 else 'tree_b', x, 0, z, 0, st)
for i, x in enumerate((17.0, 21.0, 25.0)):
    for j, z in enumerate((-18.0, -13.0, -8.0, -3.0, 2.0)): put('tree_f', x + (0.6 if j % 2 else 0.0), 0, z, 0, st)
for (x, z) in ((-2.2, PZ + 0.55), (2.2, PZ + 0.55), (-4.2, PZ + 0.55), (4.2, PZ + 0.55), (-5.8, 2.5), (5.8, 2.5)): put('bush', x, 0, z, 0, st)
put('player_scale_ref', 2.0, 0, 13.5); put('player_scale_ref', -0.5, lvl(0), 1.0, 0, ['house'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_height': H, 'house': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 2, 'floor_levels': [lvl(0), lvl(1)],
                                                                                       'roof': {'pitch_deg': PITCH, 'ridge_along': 'x', 'underside_at_wall': YE, 'ridge': round(YRIDGE, 3)}},
                       'porch': {'z': [HZ, PZ], 'deck': PFL}, 'barn': {'x': [BX - BW, BX + BW], 'z': [BZ - BD, BZ + BD], 'floor': RB, 'eave': YEB, 'ridge': round(YRB, 3), 'loft': LOFT},
                       'silo': {'center': list(SILO), 'radius': SR, 'height': SH}, 'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
                       'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
              'placements': L}
    json.dump(layout, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc2 = trimesh.Scene(); tot = 0
    for e in L:
        T_ = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T_[:3, 3] = e['pos']
        sc = pieces[e['piece']].scene(e['piece'])
        for nm, g_ in sc.geometry.items(): g2 = g_.copy(); g2.apply_transform(T_); sc2.add_geometry(g2); tot += len(g2.faces)
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:10]: print(f'  {n:30s} {p.tris():6d} tri')
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
