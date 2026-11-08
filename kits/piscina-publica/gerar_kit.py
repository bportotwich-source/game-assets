"""Kit 45: piscina publica dos anos 50, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Vestiario de tijolo (20 x 8 m) com embasamento de concreto, cinta de concreto, janelas altas de caixilho de aco e telhado de 4 aguas
de telhas com calhas e condutores; marquise azul na entrada e bilheteria com guiche. Dentro: saguao com caixa, bebedouro e banco;
vestiarios masculino e feminino com armarios, bancos, chuveiros, boxes de vaso, mictorios e pias. Atras, deck de concreto cercado
por gradil: piscina de 25 x 12 m com 5 raias (boias), blocos de largada, escadinhas, degraus na parte rasa, trampolins de 1 e 3 m,
escorregador de calha, cadeiras de salva-vidas, mesas com guarda-sol, espreguicadeiras, area de jatos com cogumelo, mastro, relogio,
chuveirinhos, boias de resgate e filtros. Fora: calcada, rua, postes, bancos, bicicletario, arbustos e arvores.
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
from trimesh.visual.material import PBRMaterial
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'brick': (164, 82, 60), 'concrete': (192, 188, 180), 'plaster': (238, 234, 222), 'ceil': (240, 238, 232), 'tile_w': (208, 228, 222),
                  'tile_c': (150, 196, 186), 'tile_a': (214, 214, 208), 'tile_b': (92, 120, 128), 'terrazzo': (206, 198, 184), 'shingles': (128, 60, 44),
                  'ridge': (110, 52, 40), 'trim': (238, 236, 228), 'gutter': (226, 224, 218), 'frame': (60, 84, 92), 'metal': (118, 124, 130),
                  'steel': (82, 88, 92), 'canopy_b': (40, 96, 138), 'deck': (210, 204, 192), 'coping': (230, 226, 216), 'pool_w': (150, 206, 214),
                  'lane': (30, 62, 112), 'chrome': (212, 214, 216), 'porcelain': (244, 244, 238), 'dark': (34, 36, 38), 'vinyl_g': (92, 138, 122),
                  'vinyl_r': (180, 50, 44), 'wood': (170, 124, 78), 'dkwood': (100, 70, 48), 'rubber': (30, 30, 30), 'float_r': (210, 50, 44),
                  'float_w': (240, 240, 236), 'float_b': (40, 90, 170), 'orange_u': (232, 112, 58), 'white_u': (244, 240, 230), 'yellowp': (236, 192, 48),
                  'blue_p': (52, 112, 182), 'board': (56, 146, 156), 'grip': (200, 196, 170), 'splash': (70, 150, 204), 'grass': (100, 150, 70),
                  'asphalt': (76, 78, 80), 'curb': (178, 174, 166), 'paint_w': (244, 242, 236), 'leaf': (82, 130, 62), 'leaf2': (110, 150, 70),
                  'hedge': (64, 108, 54), 'bark': (98, 74, 54), 'mirror': (196, 210, 216), 'cream': (240, 234, 216), 'iron': (40, 42, 44),
                  'flag_a': (40, 80, 150), 'flag_b': (244, 240, 230), 'flag_c': (200, 48, 44), 'tank': (60, 120, 170), 'pump': (70, 110, 90),
                  'plastic_w': (240, 240, 234), 'plastic_b': (64, 132, 190), 'canvas': (236, 230, 210), 'soil': (100, 76, 54), 'stall': (124, 156, 170),
                  'glass_f': (200, 214, 216), 'brass': (196, 160, 82), 'gauge': (240, 240, 232), 'redp': (190, 52, 44), 'plant': (70, 120, 56), 'clay': (176, 98, 66)},
           texturas={'brick': 'brick', 'concrete': 'render', 'plaster': 'plaster', 'shingles': 'shingles', 'deck': 'render', 'pool_w': 'render',
                     'terrazzo': 'render', 'grass': 'render', 'asphalt': 'render', 'curb': 'render', 'wood': 'planks', 'dkwood': 'planks', 'soil': 'render'},
           out=OUT)
D.METAL.update({'chrome', 'metal', 'steel', 'frame', 'iron', 'brass'}); MATS = D.MATS; TEX = D.TEX
for k in ('chrome', 'mirror'): MATS[k].roughnessFactor = 0.15; MATS[k].metallicFactor = 0.9
MATS['water'] = PBRMaterial(name='water', baseColorFactor=[0.32, 0.62, 0.74, 0.55], alphaMode='BLEND', metallicFactor=0.1, roughnessFactor=0.05, doubleSided=True)
MATS['spray'] = PBRMaterial(name='spray', baseColorFactor=[0.8, 0.92, 0.98, 0.45], alphaMode='BLEND', metallicFactor=0.0, roughnessFactor=0.1)

# ============================================================================ medidas
W = 2.0; T = 0.3; t_ = 0.12                                # modulo, parede de tijolo, divisoria
Y0 = 0.15; DY = 0.12; GY = -0.2; GR = 0.05                 # piso do vestiario, deck e calcadas, base das lajes, gramado
HX, HZ = 10.0, 4.0                                         # vestiario: x de -10 a 10, z de -4 a 4, frente para +Z (rua)
CEIL = 3.0; YW = Y0 + 3.35                                 # forro (sobre o piso), topo das paredes (face de baixo do telhado)
BASE = 0.55; BAND = (Y0 + 1.94, Y0 + 2.0)                  # embasamento de concreto, cinta de concreto (peitoril das janelas altas)
WIN = (Y0 + 2.0, Y0 + 2.85)                                # janelas altas
PITCH = 24.0; K = math.tan(math.radians(PITCH)); CS = math.cos(math.radians(PITCH)); OV = 0.6
RX = HX - HZ; YR = YW + K * HZ                             # meia cumeeira, face de baixo na cumeeira
configurar_telhado(0.07, 0.02, PITCH)
SWL = (2 * HZ - 2 * T) / 4                                 # modulos das laterais (1,85 m)
PX = 4.0                                                   # divisorias do saguao em x = -4 e 4
DZ = -2.4                                                  # portas do saguao para os vestiarios (centro em z)
POOL = (-14.0, 11.0, -24.0, -12.0)                         # piscina (agua): x0, x1, z0, z1
WY = DY - 0.25                                             # nivel da agua
LANES = 5; LW = (POOL[3] - POOL[2]) / LANES
FX = 18.0; FZ0 = -30.0; FZF = HZ                           # gradil: x de -18 a 18, z de -30 a 4
SPL = (14.0, -0.6, 2.6)                                    # area de jatos: centro e raio
SX0, SX1, SZ0, SZ1 = -24.0, 24.0, -36.0, 18.0              # terreno
SIDEW = (8.6, 11.0); STREET = (11.0, SZ1)                  # calcada e rua (z)
def depth(x):
    """Profundidade da piscina ao longo de x: rasa (1,0 m) na ponta oeste, funda (3,6 m) na ponta leste, com rampa."""
    x0, x1 = POOL[0], POOL[1]
    if x <= -2.0: return 1.0 + 0.4 * (x - x0) / (-2.0 - x0)
    if x <= 4.0: return 1.4 + 2.2 * (x + 2.0) / 6.0
    return 3.6
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

# ============================================================================ vestiario: paredes externas (pivo: face externa, chao)
def in_holes(cx, cy, holes): return any(a < cx < b and y0 < cy < y1 for (a, b, y0, y1, _) in holes)
def wall_core(p, holes, x0=-W / 2, x1=W / 2, ix=None):
    """Parede de tijolo com reboco por dentro e embasamento de concreto; holes = (a, b, y0, y1, tipo) com y absoluto."""
    xs = sorted(set([x0, x1] + [v for h in holes for v in h[:2]])); ys = sorted(set([GY, Y0, BASE, YW] + [v for h in holes for v in h[2:4]]))
    zs = [-T, -T + 0.015, 0.0]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        if in_holes(cx, cy, holes): return None
        if k == 0: return 'plaster' if cy > Y0 else 'concrete'
        return 'brick' if cy > BASE else 'concrete'
    for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)
    gaps = [(a - 0.08, b + 0.08) for (a, b, y0, y1, k) in holes if k == 'door']
    for (a, b) in segs_excl(gaps, x0, x1):
        p.box('concrete', a, b, GY, BASE, 0.0, 0.02)                                                                # embasamento
        prof_x(p, 'concrete', a, b, [(0.0, BASE), (0.02, BASE), (0.035, BASE + 0.012), (0.0, BASE + 0.04)])           # capa chanfrada
    for (a, b) in segs_excl([(a, b) for (a, b, y0, y1, k) in holes if y1 > BAND[0]], x0, x1):
        prof_x(p, 'concrete', a, b, [(0.0, BAND[0] - 0.02), (0.035, BAND[0]), (0.035, BAND[1]), (0.0, BAND[1] + 0.012)])    # cinta
    prof_x(p, 'concrete', x0, x1, crect(0.0, 0.02, YW - 0.32, YW - 0.12, 0.004, (0, 1, 1, 0)))                       # friso sob o beiral
    for (a, b) in segs_excl([(a - (0.09 if k == 'door' else 0), b + (0.09 if k == 'door' else 0)) for (a, b, y0, y1, k) in holes if y0 < Y0 + 1.5], *(ix or (x0, x1))):                       # azulejo ate 1,5 m
        p.box('tile_w', a, b, Y0, Y0 + 1.48, -T - 0.008, -T)
        prof_x(p, 'tile_c', a, b, [(-T, Y0 + 1.48), (-T - 0.02, Y0 + 1.48), (-T - 0.02, Y0 + 1.5), (-T - 0.008, Y0 + 1.52), (-T, Y0 + 1.52)])
        p.box('tile_c', a, b, Y0, Y0 + 0.12, -T - 0.016, -T - 0.008)                                                # rodape de azulejo
def steel_win(p, a, b, y0, y1, zf=-0.12, cols=3, rows=2):
    """Caixilho de aco com vidro e basculante no meio (no vao a..b, y0..y1)."""
    f = 0.045; z0, z1 = zf - 0.04, zf
    alu_frame(p, a, b, y0, y1, f, z0, z1)
    for k in range(1, cols): x = a + (b - a) * k / cols; p.box('frame', x - 0.016, x + 0.016, y0 + f, y1 - f, z0 + 0.008, z1 - 0.008)
    for k in range(1, rows): y = y0 + (y1 - y0) * k / rows; p.box('frame', a + f, b - f, y - 0.016, y + 0.016, z0 + 0.008, z1 - 0.008)
    p.box('glass_f', a + f - 0.004, b - f + 0.004, y0 + f - 0.004, y1 - f + 0.004, zf - 0.022, zf - 0.018)
    ym = y0 + (y1 - y0) / rows; yt = y0 + 2 * (y1 - y0) / rows if rows > 1 else y1
    for (x_, d) in ((a + f, 0.0),): pass
def win_dress(p, a, b, y0, y1):
    """Verga de concreto, peitoril interno de azulejo (a cinta faz o peitoril de fora)."""
    p.box('concrete', a - 0.12, b + 0.12, y1, y1 + 0.14, 0.0, 0.012)
    p.cham('tile_c', a, b, y0 - 0.002, y0 + 0.03, -T - 0.05, -0.16, 0.006)
def module(kind='plain', x0=-W / 2, x1=W / 2, end=0):
    p = Piece(); holes = []; ix = (x0 + T, x1) if end < 0 else (x0, x1 - T) if end > 0 else None
    if kind == 'win': holes = [(-0.7, 0.7, *WIN, 'win')]
    if kind == 'win_s': holes = [(-0.55, 0.55, *WIN, 'win')]
    if kind == 'door': holes = [(-0.47, 0.47, Y0, Y0 + 2.2, 'door')]
    if kind == 'gdoor': holes = [(-0.5, 0.5, Y0, Y0 + 2.75, 'door')]
    if kind == 'ticket': holes = [(-0.6, 0.6, Y0 + 0.95, BAND[0], 'tk'), (-0.55, 0.55, *WIN, 'win')]
    if kind == 'entry': holes = [(-0.95, 0.95, Y0, Y0 + 2.55, 'door')]
    wall_core(p, holes, x0, x1, ix)
    for (a, b, y0, y1, k) in holes:
        if k == 'win': steel_win(p, a, b, y0, y1); win_dress(p, a, b, y0, y1)
        if k == 'door':
            for s in (-1, 1): p.box('frame', *sorted((s * b, s * (b - 0.06))), Y0, y1, -0.2, -0.1)                     # batente de aco
            p.box('frame', a + 0.06, b - 0.06, y1 - 0.06, y1, -0.2, -0.1)
            p.box('concrete', a - 0.15, b + 0.15, y1, y1 + 0.18, 0.0, 0.015)                                         # verga
            p.cham('concrete', a, b, Y0 - 0.02, Y0 + 0.005, -T + 0.005, 0.06, 0.006)                                 # soleira
            if kind in ('gdoor', 'entry'):                                                                           # bandeira de vidro
                yt = Y0 + 2.3 if kind == 'entry' else Y0 + 2.22
                p.box('frame', a + 0.06, b - 0.06, yt, yt + 0.05, -0.2, -0.1); p.box('glass', a + 0.06, b - 0.06, yt + 0.05, y1 - 0.06, -0.152, -0.148)
                if kind == 'entry': p.box('frame', -0.025, 0.025, yt + 0.05, y1 - 0.06, -0.2, -0.1)
            for (a2, b2) in ((a - 0.09, a), (b, b + 0.09)): p.box('tile_c', a2, b2, Y0, y1, -T - 0.018, -T)          # guarnicao interna de azulejo
            p.box('tile_c', a - 0.09, b + 0.09, y1, y1 + 0.09, -T - 0.018, -T)
        if k == 'tk':                                                                                               # guiche da bilheteria
            p.box('frame', a, b, y0, y0 + 0.04, -0.2, -0.1); p.box('frame', a, a + 0.04, y0, y1, -0.2, -0.1); p.box('frame', b - 0.04, b, y0, y1, -0.2, -0.1)
            p.box('frame', a, b, y1 - 0.04, y1, -0.2, -0.1); p.box('frame', -0.02, 0.02, y0 + 0.04, y1 - 0.04, -0.2, -0.1)
            p.box('glass', a + 0.04, -0.02, y0 + 0.04, y1 - 0.04, -0.17, -0.165); p.box('glass', 0.02, b - 0.04, y0 + 0.04, y1 - 0.04, -0.135, -0.13)
            p.cham('concrete', a - 0.1, b + 0.1, y0 - 0.06, y0, -0.1, 0.32, 0.008)                                 # balcao de fora
            for s in (-1, 1): p.hull('concrete', [(s * (b - 0.05), yy, zz) for yy, zz in ((y0 - 0.06, 0.0), (y0 - 0.06, 0.26), (y0 - 0.4, 0.0))] + [(s * (b - 0.12), yy, zz) for yy, zz in ((y0 - 0.06, 0.0), (y0 - 0.06, 0.26), (y0 - 0.4, 0.0))])
            p.cham('dark', -0.12, 0.12, y0 - 0.002, y0 + 0.004, -0.05, 0.12, 0.002)                                  # passa-troco
            p.box('tile_w', a, b, Y0, Y0 + 0.9, -T - 0.008, -T); p.box('tile_c', a, b, Y0, Y0 + 0.12, -T - 0.016, -T - 0.008)
            for (yy, zz) in ((y1 + 0.12, 0.0),):                                                                     # toldo de chapa
                p.hull('canopy_b', [(x, y, z) for x in (a - 0.15, b + 0.15) for (y, z) in ((y1 + 0.32, 0.015), (y1 + 0.36, 0.015), (y1 + 0.06, 0.55), (y1 + 0.1, 0.55))])
            p.cham('canopy_b', a - 0.15, b + 0.15, y1 + 0.0, y1 + 0.08, 0.5, 0.56, 0.006)
    return p
PROF_BASE = [(0.0, GY), (0.02, GY), (0.02, BASE), (0.035, BASE + 0.012), (0.0, BASE + 0.04)]
PROF_BAND = [(0.0, BAND[0] - 0.02), (0.035, BAND[0]), (0.035, BAND[1]), (0.0, BAND[1] + 0.012)]
PROF_FRZ = [(0.0, YW - 0.32), (0.02, YW - 0.32), (0.02, YW - 0.12), (0.0, YW - 0.12)]
def corner(ext_x=False):
    """Quina externa (pivo: quina, chao; paredes em -X e -Z): retornos do embasamento, da cinta e do friso em meia-esquadria; o
    retorno da fachada lateral (a que para antes da quina) vai ate -T."""
    p = Piece(); r2 = math.sqrt(2)
    for prof in (PROF_BASE, PROF_BAND, PROF_FRZ):
        D_ = max(o for o, y in prof) + 0.001
        q = Piece(); prof_x(q, 'concrete', -T if ext_x else 0.0, D_, prof); p.add('concrete', slice_keep(q.parts['concrete'][0], [0, 0, 0], np.array([-1, 0, 1]) / r2))
        q = Piece(); prof_z(q, 'concrete', 0.0 if ext_x else -T, D_, prof); p.add('concrete', slice_keep(q.parts['concrete'][0], [0, 0, 0], np.array([1, 0, -1]) / r2))
    return p

# ============================================================================ telhado de 4 aguas (pivo: origem do vestiario, chao)
def roof_face(R, ridge_caps=True):
    """Uma agua (local: parede em z = HZ, beiral em HZ + OV, cumeeira de -R a R em z = 0): tabuado, telhas em fiadas, testeira e calha
    em meia-esquadria, forro do beiral com respiros e, nas aguas grandes, as 2 capas dos espigoes."""
    p = Piece(); ZE = HZ + OV; E = R + ZE
    poly = Polygon([(-E, ZE), (E, ZE), (R, 0.0), (-R, 0.0)]) if R > 0 else Polygon([(-E, ZE), (E, ZE), (0.0, 0.0)])
    f = lambda a, b: YW + K * (HZ - b)
    sheared(p, 'wood', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: ZE - b, lambda d0, d1: sbox(-60, ZE - d1, 60, ZE - d0), ZE + 0.01,
                    lambda v, n: np.stack([v[:, 0] / TILE, (ZE - v[:, 2]) / CS / TILE], 1))
    yb = f(0, ZE); r2 = math.sqrt(2)
    planes = [((E, 0, ZE), (-1, 0, 1)), ((-E, 0, ZE), (1, 0, 1))]
    q = Piece(); prof_x(q, 'trim', -E - 0.3, E + 0.3, crect(ZE - 0.02, ZE + 0.03, yb - 0.17, yb + 0.05, 0.006, (0, 1, 1, 0)))       # testeira
    q.box('trim', -E - 0.3, E + 0.3, yb - 0.17, yb - 0.15, HZ + 0.001, ZE - 0.02)                                              # forro do beiral
    p.merge(clipped(q, planes))
    for xx in np.arange(-R - 1.2, R + 1.3, 1.2): p.box('dark', xx - 0.12, xx + 0.12, yb - 0.172, yb - 0.17, HZ + 0.18, HZ + 0.3)  # respiros
    gutter_run(p, -E - 0.3, E + 0.3, ZE + 0.03, yb + 0.02, mitre=((E, 1), (-E, -1)))
    if ridge_caps:
        yo = TV + BUMP + 0.03
        for s in (-1, 1):
            a = np.array([s * (E + 0.02), f(0, ZE + 0.02) + yo, ZE + 0.02]); b = np.array([s * R, YR + yo, 0.0])
            pts = []
            for c in (a, b):
                pts += [tuple(c + [0, 0.07, 0]), tuple(c + [s * 0.1, -0.02 - 0.1 * K, 0]), tuple(c + [0, -0.02 - 0.1 * K, 0.1]),
                        tuple(c + [s * 0.11, -0.05 - 0.1 * K, 0]), tuple(c + [0, -0.05 - 0.1 * K, 0.11])]
            p.hull('ridge', pts)
    return p
def roof_ridge():
    p = Piece(); y = YR + TV + BUMP + 0.03; d = 0.17
    p.hull('ridge', [(x, yy, z) for x in (-RX - 0.03, RX + 0.03) for (yy, z) in ((y - d * K - 0.04, d), (y - d * K - 0.04, -d), (y + 0.075, 0.0), (y + 0.06, 0.06), (y + 0.06, -0.06), (y - 0.1, 0.0))])
    return p
def roof_vent():
    """Respiro de chapa no telhado (pivo: centro no telhado, com o pe enterrado nas telhas; frente descendo para +Z)."""
    p = Piece(); p.cham('metal', -0.3, 0.3, -0.25, 0.3, -0.3, 0.3, 0.02)
    p.hull('metal', [(x, y, z) for x in (-0.36, 0.36) for (y, z) in ((0.3, -0.36), (0.3, 0.36), (0.42, -0.36), (0.36, 0.36))])
    for k in range(5): z = -0.22 + k * 0.11; p.box('dark', -0.26, 0.26, 0.05, 0.25, z - 0.012, z + 0.012) if False else p.box('dark', -0.24, 0.24, 0.08, 0.24, 0.3, 0.302) if k == 0 else None
    for k in range(4): y = 0.1 + k * 0.045; p.box('metal', -0.25, 0.25, y, y + 0.012, 0.3, 0.33)
    return p
def vent_pipe():
    p = Piece(); p.cyl('metal', 0.05, -0.3, 0.55, 0, 0, 12); p.cyl('metal', 0.075, -0.3, 0.06, 0, 0, 16); p.cyl('dark', 0.035, 0.55, 0.552, 0, 0, 10); return p
def ceiling():
    """Forro de gesso dos 3 ambientes (pivo: origem, chao)."""
    p = Piece(); ext_y(p, 'ceil', sbox(-HX + T, -HZ + T, HX - T, HZ - T), Y0 + CEIL, Y0 + CEIL + 0.04)
    for x in (-PX, PX): p.box('trim', x - t_ / 2 - 0.04, x + t_ / 2 + 0.04, Y0 + CEIL - 0.05, Y0 + CEIL, -HZ + T + 0.001, HZ - T - 0.001) if False else None
    return p
def ceiling_light():
    """Luminaria de sobrepor redonda com globo leitoso (pivo: no forro)."""
    p = Piece(); p.cyl('metal', 0.16, -0.04, 0.0, 0, 0, 20); lathe(p, 'lamp_glass', [(0.15, -0.04), (0.16, -0.08), (0.12, -0.15), (0.0, -0.17)], sec=20); return p

# ============================================================================ dentro: divisorias, pisos e louças
def partition():
    """Divisoria entre o saguao e um vestiario (pivo: inicio em z = -HZ + T, eixo, piso; corre para +X local): alvenaria rebocada
    com azulejo ate 1,5 m dos 2 lados, porta com guarnicao."""
    p = Piece(); Ln = 2 * (HZ - T); h = CEIL; dc = DZ + HZ - T; holes = [(dc - 0.45, dc + 0.45, 0.0, 2.1, 'door')]
    xs = sorted(set([0.0, Ln] + [v for c in holes for v in c[:2]])); ys = sorted(set([0.0, h] + [v for c in holes for v in c[2:4]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        return None if in_holes(cx, cy, holes) else 'plaster'
    for m, mesh in grid_solid(xs, ys, [-t_ / 2, t_ / 2], cell).items(): p.add(m, mesh)
    q = Piece(); door_casing(q, 0.9, t_, 2.1); p.merge(q, tr(dc, 0, 0))
    for s in (-1, 1):
        z0 = s * t_ / 2; z1 = s * (t_ / 2 + 0.008); z2 = s * (t_ / 2 + 0.02); z3 = s * (t_ / 2 + 0.016)
        for (a, b) in segs_excl([(dc - 0.45 - 0.09, dc + 0.45 + 0.09)], 0.0, Ln):
            p.box('tile_w', a, b, 0.0, 1.48, *sorted((z0, z1)))
            prof_x(p, 'tile_c', a, b, [(z0, 1.48), (z2, 1.48), (z2, 1.5), (z1, 1.52), (z0, 1.52)][::(1 if s > 0 else -1)])
            p.box('tile_c', a, b, 0.0, 0.12, *sorted((z1, z3)))
    return p
def checker(p, poly, y0, y1, step, ma, mb, ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step, oz + j * step, ox + (i + 1) * step, oz + (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
LRX = (HX - T - PX - t_ / 2) / 2; LRC = PX + t_ / 2 + LRX        # meia largura e centro de um vestiario
def floor_lr():
    """Piso de um vestiario (pivo: centro do vestiario, chao): ladrilho xadrez de 30 cm, ralos."""
    p = Piece(); poly = sbox(-LRX, -HZ + T, LRX, HZ - T)
    ext_y(p, 'concrete', poly, GY, Y0 - 0.02); checker(p, poly, Y0 - 0.02, Y0, 0.3, 'tile_a', 'tile_b', -LRX, -HZ + T)
    for (x, z) in ((0.0, 0.0),):
        p.box('chrome', x - 0.1, x + 0.1, Y0, Y0 + 0.003, z - 0.1, z + 0.1)
        for k in range(5): xx = x - 0.07 + k * 0.035; p.box('dark', xx - 0.008, xx + 0.008, Y0 + 0.003, Y0 + 0.004, z - 0.07, z + 0.07)
    return p
def floor_lobby():
    """Piso do saguao de granilite com faixa (pivo: origem, chao); passa por baixo das divisorias."""
    p = Piece(); poly = sbox(-PX - t_ / 2, -HZ + T, PX + t_ / 2, HZ - T); inner = sbox(-PX + 0.5, -HZ + T + 0.5, PX - 0.5, HZ - T - 0.5)
    ext_y(p, 'concrete', poly, GY, Y0 - 0.02)
    ext_y(p, 'terrazzo', poly.difference(inner.buffer(0.15, join_style=2)), Y0 - 0.02, Y0); ext_y(p, 'terrazzo', inner, Y0 - 0.02, Y0)
    ext_y(p, 'tile_b', inner.buffer(0.15, join_style=2).difference(inner), Y0 - 0.02, Y0)
    ext_y(p, 'dark', sbox(-0.9, HZ - T - 1.2, 0.9, HZ - T - 0.02), Y0, Y0 + 0.012)                                      # capacho
    return p
def lr_bench(L1=2.4):
    """Banco de vestiario: tampo de ripas sobre 2 pes de cano com sapata (pivo: centro, piso)."""
    p = Piece(); x = L1 / 2
    for k in range(4): z = -0.15 + k * 0.1; p.cham('wood', -x, x, 0.42, 0.46, z - 0.04, z + 0.04, 0.006)
    for xx in (-x + 0.3, x - 0.3):
        p.box('steel', xx - 0.03, xx + 0.03, 0.38, 0.42, -0.19, 0.19); seg_cyl(p, 'steel', (xx, 0.02, 0), (xx, 0.38, 0), 0.03, 10); p.cyl('steel', 0.12, 0.0, 0.02, xx, 0, 14)
    return p
def shower_bay(n=3, sp=0.95):
    """Chuveiros de parede (pivo: face da parede, piso; ao longo de +X, local +Z para dentro): canos, registros, crivos, divisorias de
    azulejo com capa e mureta na frente."""
    p = Piece(); x0 = -n * sp / 2
    for i in range(n):
        x = x0 + (i + 0.5) * sp
        seg_cyl(p, 'chrome', (x, 1.0, 0.03), (x, 2.0, 0.03), 0.014, 8); seg_cyl(p, 'chrome', (x, 2.0, 0.03), (x, 2.08, 0.2), 0.014, 8)
        lathe(p, 'chrome', [(0.02, 0.06), (0.07, 0.0), (0.07, -0.02), (0.0, -0.025)], x, 0.22, 2.06, 16)
        for dx in (-0.1, 0.1): p.cyl('chrome', 0.03, 0.0, 0.0, 0, 0) if False else (disc_z(p, 'chrome', 0.035, 0.0, 0.03, x + dx, 1.1, 14), seg_cyl(p, 'chrome', (x + dx - 0.04, 1.1, 0.045), (x + dx + 0.04, 1.1, 0.045), 0.01, 6))
        p.box('chrome', x - 0.1, x + 0.1, 1.09, 1.11, 0.0, 0.025)
        p.cham('chrome', x - 0.08, x + 0.08, 1.35, 1.4, 0.0, 0.08, 0.008)                                                  # saboneteira
    for i in range(n + 1):
        x = x0 + i * sp
        p.box('tile_w', x - 0.05, x + 0.05, 0.0, 1.8, 0.0, 1.0); p.cham('tile_c', x - 0.06, x + 0.06, 1.8, 1.84, 0.0, 1.02, 0.01)
    p.box('tile_c', x0 - 0.05, -x0 + 0.05, 0.0, 0.1, 1.0, 1.1)                                                            # mureta
    p.box('tile_c', x0 + 0.05, -x0 - 0.05, -0.002, 0.003, 0.002, 1.0)                                                      # piso do box
    for i in range(n): x = x0 + (i + 0.5) * sp; p.box('chrome', x - 0.06, x + 0.06, 0.003, 0.005, 0.5, 0.62)
    return p
def stalls(n=2, w=1.0, d=1.5):
    """Boxes de vaso com divisorias de chapa, pilares com sapata cromada, travessa e portas entreabertas (pivo: canto da parede do
    fundo, piso; boxes ao longo de +X, local +Z para a frente)."""
    p = Piece(); h0, h1 = 0.3, 1.85
    for i in range(1, n): x = i * w; p.box('stall', x - 0.0125, x + 0.0125, h0, h1, 0.0, d - 0.03)
    p.box('stall', n * w - 0.0125, n * w + 0.0125, h0, h1, 0.0, d - 0.03)
    for i in range(n + 1):
        x = i * w; p.box('stall', x - 0.03, x + 0.03, 0.0, 2.05, d - 0.03, d + 0.02) if i > 0 else p.box('stall', 0.0, 0.06, 0.0, 2.05, d - 0.03, d + 0.02)
        p.box('chrome', max(x - 0.04, 0.002), x + 0.04, 0.0, 0.12, d - 0.04, d + 0.03)
    p.box('chrome', 0.0, n * w + 0.03, 2.05, 2.09, d - 0.02, d + 0.02)
    for i in range(n):
        a = i * w + 0.035; b = (i + 1) * w - 0.035; q = Piece(); q.box('stall', 0.0, b - a, h0, h1, -0.0125, 0.0125); q.box('chrome', b - a - 0.12, b - a - 0.04, 1.0, 1.06, -0.04, 0.04)
        p.merge(q, rot_y(-25, (a, 0, d)))
    return p
def urinal_screen():
    p = Piece(); p.box('stall', -0.0125, 0.0125, 0.45, 1.7, 0.02, 0.5); p.box('chrome', -0.02, 0.02, 1.0, 1.4, 0.0, 0.02); return p
def wc():
    """Vaso de louca com caixa acoplada e assento (pivo: face da parede, piso)."""
    p = Piece()
    lathe(p, 'porcelain', [(0.13, 0.0), (0.15, 0.1), (0.14, 0.28), (0.2, 0.4), (0.2, 0.42), (0.0, 0.42)], 0.0, 0.42, 0.0, 16)
    p.hull('porcelain', [(x * 0.17, y, z) for x in (-1, 1) for z in (0.15, 0.4) for y in (0.0, 0.42)])
    p.cham('porcelain', -0.2, 0.2, 0.42, 0.8, 0.0, 0.18, 0.03); p.cham('porcelain', -0.21, 0.21, 0.8, 0.83, -0.0, 0.19, 0.01)
    p.cham('dark', -0.19, 0.19, 0.42, 0.45, 0.2, 0.62, 0.03); p.box('chrome', 0.1, 0.16, 0.74, 0.76, 0.18, 0.2)
    p.cyl('chrome', 0.05, 0.9, 0.95, 0.35, 0.05, 14) if False else None
    return p
def urinal():
    p = Piece(); p.hull('porcelain', [(x, y, z) for x in (-0.2, 0.2) for (y, z) in ((0.45, 0.0), (0.45, 0.3), (1.05, 0.0), (1.05, 0.2))])
    p.box('dark', -0.08, 0.08, 0.6, 0.62, 0.05, 0.22) if False else None
    seg_cyl(p, 'chrome', (0, 1.05, 0.06), (0, 1.4, 0.06), 0.015, 6); p.box('chrome', -0.04, 0.04, 1.3, 1.36, 0.06, 0.1)
    return p
def sink_bank(n=2, L1=1.6):
    """Bancada de pias de louca com torneiras cromadas e espelho com moldura de aco (pivo: face da parede, piso)."""
    p = Piece(); x = L1 / 2
    p.cham('porcelain', -x, x, 0.8, 0.88, 0.0, 0.5, 0.02)
    for s in (-1, 1): p.box('chrome', s * (x - 0.08) - 0.02, s * (x - 0.08) + 0.02, 0.0, 0.8, 0.4, 0.44)
    for i in range(n):
        xc = -x + (i + 0.5) * L1 / n; p.box('dark', xc - 0.2, xc + 0.2, 0.875, 0.882, 0.12, 0.42)
        seg_cyl(p, 'chrome', (xc, 0.88, 0.06), (xc, 1.08, 0.06), 0.014, 6); seg_cyl(p, 'chrome', (xc, 1.08, 0.06), (xc, 1.04, 0.2), 0.012, 6)
        p.cham('chrome', xc - 0.32, xc + 0.32, 1.2, 1.95, 0.0, 0.02, 0.006); p.box('mirror', xc - 0.29, xc + 0.29, 1.23, 1.92, 0.02, 0.026)
    return p
def towel_disp():
    """Toalheiro de papel e lixeira de parede (pivo: face da parede, piso)."""
    p = Piece(); p.cham('chrome', -0.15, 0.15, 1.3, 1.65, 0.0, 0.12, 0.01); p.box('dark', -0.1, 0.1, 1.296, 1.3, 0.03, 0.09)
    p.cham('chrome', -0.18, 0.18, 0.0, 0.7, 0.0, 0.25, 0.01); p.box('dark', -0.14, 0.14, 0.7, 0.702, 0.04, 0.2); return p
def lockers2(): return lockers(1.8, 3)

# ============================================================================ saguao, marquise e coisas de fora
def cashier():
    """Caixa da bilheteria (pivo: canto da parede da frente com a divisoria oeste, piso; local +X para leste, -Z para dentro):
    bancada sob o guiche, balcao para o saguao com tampo de madeira e frente de azulejo, portinhola, caixa registradora e banqueta."""
    p = Piece(); zf = -0.02
    p.cham('wood', 0.0, 2.0, 0.78, 0.82, zf - 0.6, zf, 0.008); p.box('tile_c', 0.05, 1.95, 0.0, 0.78, zf - 0.55, zf - 0.5)          # bancada
    zc = -2.0
    p.box('tile_b', 0.0, 1.6, 0.0, 0.95, zc - 0.25, zc); p.cham('wood', -0.02, 1.62, 0.95, 1.0, zc - 0.35, zc + 0.05, 0.008)          # balcao
    for x in np.arange(0.1, 1.55, 0.3): p.box('tile_c', x, x + 0.26, 0.15, 0.85, zc - 0.258, zc - 0.25)
    p.box('wood', 1.62, 1.66, 0.0, 0.95, zc - 0.25, zc) if False else None
    q = Piece(); q.box('wood', 0.0, 0.5, 0.1, 0.9, -0.02, 0.02); q.box('dkwood', 0.04, 0.46, 0.85, 0.905, -0.025, 0.025); p.merge(q, rot_y(30, (1.66, 0, zc - 0.12)))  # portinhola
    rx = 1.0; ry_ = 0.82                                                                                                           # caixa registradora
    p.cham('steel', rx - 0.22, rx + 0.22, ry_, ry_ + 0.12, zf - 0.5, zf - 0.12, 0.01)
    p.hull('steel', [(x, y, z) for x in (rx - 0.2, rx + 0.2) for (y, z) in ((ry_ + 0.12, zf - 0.5), (ry_ + 0.12, zf - 0.22), (ry_ + 0.28, zf - 0.22), (ry_ + 0.24, zf - 0.42))])
    for i in range(4):
        for j in range(3): p.cham('cream', rx - 0.16 + i * 0.08, rx - 0.11 + i * 0.08, ry_ + 0.19 - j * 0.0, ry_ + 0.21, zf - 0.45 + j * 0.06, zf - 0.41 + j * 0.06, 0.004) if False else p.box('cream', rx - 0.16 + i * 0.08, rx - 0.11 + i * 0.08, ry_ + 0.16 + j * 0.022, ry_ + 0.18 + j * 0.022, zf - 0.27 - j * 0.05, zf - 0.23 - j * 0.05)
    p.box('dark', rx - 0.14, rx + 0.14, ry_ + 0.28, ry_ + 0.36, zf - 0.3, zf - 0.26); p.box('cream', rx - 0.12, rx + 0.12, ry_ + 0.29, ry_ + 0.35, zf - 0.262, zf - 0.258)
    q = Piece(); q.merge(stool()); p.merge(q, tr(1.0, 0, zf - 0.95))
    p.cham('dkwood', 0.3, 0.7, 0.82, 0.86, zf - 0.45, zf - 0.15, 0.006)                                                            # bloco de ingressos
    return p
def lobby_bench(L1=2.4):
    """Banco do saguao de ripas com encosto e pes de ferro (pivo: face da parede, piso; local +Z para dentro)."""
    p = Piece(); x = L1 / 2
    for k in range(4): z = 0.17 + k * 0.1; p.cham('wood', -x, x, 0.43, 0.46, z - 0.04, z + 0.04, 0.006)
    for k in range(3): y = 0.6 + k * 0.13; p.cham('wood', -x, x, y, y + 0.09, 0.05, 0.08, 0.006)
    for xx in (-x + 0.2, x - 0.2):
        p.box('iron', xx - 0.025, xx + 0.025, 0.0, 0.43, 0.48, 0.52); p.box('iron', xx - 0.025, xx + 0.025, 0.0, 0.95, 0.08, 0.12)
        p.box('iron', xx - 0.025, xx + 0.025, 0.4, 0.43, 0.08, 0.52)
    return p
def fountain():
    """Bebedouro de parede de louca com botao (pivo: face da parede, piso)."""
    p = Piece(); p.cham('porcelain', -0.22, 0.22, 0.75, 0.92, 0.0, 0.4, 0.03); p.box('dark', -0.16, 0.16, 0.92, 0.922, 0.06, 0.34)
    p.cham('chrome', -0.03, 0.03, 0.92, 0.98, 0.18, 0.24, 0.01); p.cham('chrome', 0.12, 0.2, 0.8, 0.86, 0.4, 0.43, 0.006)
    seg_cyl(p, 'chrome', (0, 0.3, 0.03), (0, 0.75, 0.03), 0.02, 8); return p
def poster(kind=0):
    """Quadro com pictogramas (sem texto) em moldura de aluminio (pivo: face da parede, centro)."""
    p = Piece(); w, h = 0.5, 0.7
    p.cham('chrome', -w / 2, w / 2, -h / 2, h / 2, 0.0, 0.02, 0.004); p.box('cream', -w / 2 + 0.03, w / 2 - 0.03, -h / 2 + 0.03, h / 2 - 0.03, 0.02, 0.022)
    cols = ['float_b', 'redp', 'board']
    for i in range(3):
        y = h / 2 - 0.15 - i * 0.2; c = cols[(i + kind) % 3]
        p.cyl(c, 0.0, 0, 0) if False else disc_z(p, c, 0.06, 0.022, 0.026, -0.12, y, 16)
        p.box(c, -0.02, 0.18, y - 0.012, y + 0.012, 0.022, 0.026)
        if (i + kind) % 2 == 0: seg_cyl(p, 'dark', (-0.17, y + 0.06, 0.028), (-0.07, y - 0.06, 0.028), 0.008, 4)
    return p
def lifebuoy_wall():
    """Boia de salvamento laranja e branca no suporte (pivo: face da parede, centro)."""
    p = Piece(); R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    for k in range(8):
        a0, a1 = k * math.pi / 4, (k + 1) * math.pi / 4; m = trimesh.creation.torus(0.25, 0.06, major_sections=8, minor_sections=8) if False else None
        pts = []
        for a in (a0, a1):
            for (r, dz) in ((0.19, 0.0), (0.31, 0.0), (0.25, 0.06), (0.25, -0.06), (0.21, 0.045), (0.29, 0.045), (0.21, -0.045), (0.29, -0.045)):
                pts.append((r * math.cos(a), r * math.sin(a), 0.07 + dz))
        p.hull('orange_u' if k % 2 == 0 else 'white_u', pts)
    p.box('steel', -0.03, 0.03, 0.15, 0.2, 0.0, 0.08); return p
def plant_pot():
    p = Piece(); lathe(p, 'clay', [(0.18, 0.0), (0.24, 0.5), (0.26, 0.55), (0.0, 0.55)], sec=16); p.cyl('soil', 0.23, 0.5, 0.52, 0, 0, 16)
    for k in range(9):
        a = k * 2.4; r = 0.1 + 0.03 * (k % 3); p.hull('plant', [(0, 0.52, 0), (0.04 * math.cos(a + 1.5), 0.6, 0.04 * math.sin(a + 1.5)), (r * 2.2 * math.cos(a), 0.95 + 0.06 * (k % 4), r * 2.2 * math.sin(a)), (r * 2.4 * math.cos(a + 0.2), 0.88, r * 2.4 * math.sin(a + 0.2))])
    return p
def trash_can():
    p = Piece(); lathe(p, 'steel', [(0.2, 0.0), (0.22, 0.85), (0.0, 0.85)], sec=16); lathe(p, 'dark', [(0.23, 0.85), (0.23, 0.9), (0.12, 0.98), (0.0, 0.99)], sec=16)
    for k in range(8): a = k * math.pi / 4; p.box('steel', -0.01, 0.01, 0.0, 0.0, 0, 0) if False else seg_cyl(p, 'metal', (0.21 * math.cos(a), 0.05, 0.21 * math.sin(a)), (0.225 * math.cos(a), 0.8, 0.225 * math.sin(a)), 0.012, 4)
    return p
def entry_canopy():
    """Marquise da entrada (pivo: face da parede da frente, chao): laje fina com testeira azul, forro com 2 spots, 2 colunas de cano
    com sapata e 2 tirantes ate a parede."""
    p = Piece(); x = 2.1; d = 2.5; yt = Y0 + 2.87; yb = Y0 + 2.62
    p.cham('canopy_b', -x, x, yb, yt, 0.002, d, 0.01)
    p.cham('trim', -x - 0.03, x + 0.03, yt - 0.02, yt + 0.02, -0.0, d + 0.03, 0.006) if False else p.box('metal', -x + 0.02, x - 0.02, yt, yt + 0.025, 0.02, d - 0.02)
    p.box('trim', -x + 0.04, x - 0.04, yb - 0.004, yb, 0.04, d - 0.04)
    for xx in (-1.0, 1.0): p.cyl('metal', 0.09, yb - 0.02, yb - 0.004, xx, d / 2, 16); p.cyl('lamp_glass', 0.07, yb - 0.025, yb - 0.02, xx, d / 2, 16)
    for xx in (-x + 0.25, x - 0.25):
        p.cyl('steel', 0.06, DY, yb, xx, d - 0.25, 14); p.cyl('steel', 0.12, DY, DY + 0.03, xx, d - 0.25, 16); p.cyl('steel', 0.08, yb - 0.08, yb, xx, d - 0.25, 14)
        seg_cyl(p, 'steel', (xx, yt + 0.02, d - 0.3), (xx, YW - 0.56, 0.02), 0.014, 6); p.box('steel', xx - 0.05, xx + 0.05, YW - 0.62, YW - 0.5, 0.0, 0.02)
    return p
def lamp_post():
    """Poste de jardim de ferro fundido com lanterna (pivo: chao)."""
    p = Piece(); lathe(p, 'iron', [(0.16, -0.2), (0.16, 0.2), (0.12, 0.3), (0.09, 0.45), (0.06, 0.6), (0.05, 3.2), (0.07, 3.3), (0.12, 3.36), (0.0, 3.38)], sec=14)
    for k in range(8): a = k * math.pi / 4; seg_cyl(p, 'iron', (0.052 * math.cos(a), 0.65, 0.052 * math.sin(a)), (0.052 * math.cos(a), 3.1, 0.052 * math.sin(a)), 0.012, 4)
    lathe(p, 'lamp_glass', [(0.1, 3.38), (0.17, 3.5), (0.18, 3.8), (0.12, 3.9), (0.0, 3.9)], sec=14)
    for k in range(4): a = k * math.pi / 2 + math.pi / 4; seg_cyl(p, 'iron', (0.1 * math.cos(a), 3.38, 0.1 * math.sin(a)), (0.19 * math.cos(a), 3.82, 0.19 * math.sin(a)), 0.012, 4)
    lathe(p, 'iron', [(0.24, 3.85), (0.24, 3.88), (0.12, 4.02), (0.03, 4.08), (0.03, 4.18), (0.0, 4.2)], sec=14)
    return p
def park_bench(L1=1.8):
    """Banco de praca: ripas de madeira, cabeceiras de ferro fundido com braco (pivo: centro, chao; frente +Z)."""
    p = Piece(); x = L1 / 2
    for k in range(4): z = -0.15 + k * 0.11; p.cham('wood', -x, x, 0.42, 0.45, z - 0.045, z + 0.045, 0.006)
    for k in range(3): y = 0.55 + k * 0.12; z = -0.24 - (y - 0.55) * 0.18; p.cham('wood', -x, x, y, y + 0.08, z - 0.02, z + 0.015, 0.006)
    for xx in (-x + 0.12, x - 0.12):
        for (a, b) in (((xx, -0.25, -0.22), (xx, 0.0, -0.3)), ((xx, -0.25, 0.25), (xx, 0.0, 0.3))): pass
        p.hull('iron', [(xx + dx, y, z) for dx in (-0.025, 0.025) for (y, z) in ((0.0, -0.32), (0.0, -0.26), (0.42, -0.2), (0.42, -0.26))])
        p.hull('iron', [(xx + dx, y, z) for dx in (-0.025, 0.025) for (y, z) in ((0.0, 0.28), (0.0, 0.22), (0.42, 0.18), (0.42, 0.24))])
        p.box('iron', xx - 0.025, xx + 0.025, 0.38, 0.42, -0.26, 0.22)
        p.hull('iron', [(xx + dx, y, z) for dx in (-0.025, 0.025) for (y, z) in ((0.42, -0.22), (0.42, -0.27), (0.92, -0.37), (0.92, -0.32))])
        p.hull('iron', [(xx + dx, y, z) for dx in (-0.03, 0.03) for (y, z) in ((0.62, -0.28), (0.66, -0.28), (0.66, 0.2), (0.62, 0.2))])
        p.hull('iron', [(xx + dx, y, z) for dx in (-0.02, 0.02) for (y, z) in ((0.42, 0.16), (0.42, 0.2), (0.62, 0.2), (0.62, 0.16))])
    return p
def bike_rack(n=5):
    """Bicicletario de tubo em ondas (pivo: centro, chao; ao longo de X)."""
    p = Piece(); L1 = n * 0.6
    for i in range(n):
        x = -L1 / 2 + (i + 0.5) * 0.6; pts = [(x - 0.22, 0.0), (x - 0.22, 0.6), (x - 0.15, 0.78), (x, 0.82), (x + 0.15, 0.78), (x + 0.22, 0.6), (x + 0.22, 0.0)]
        for (a, b) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', (a[0], a[1], 0), (b[0], b[1], 0), 0.024, 8)
    seg_cyl(p, 'chrome', (-L1 / 2, 0.08, 0), (L1 / 2, 0.08, 0), 0.02, 8); return p

# ============================================================================ piscina
PR = sbox(POOL[0], POOL[2], POOL[1], POOL[3])
def basin():
    """Tanque da piscina (pivo: origem, chao): paredes e fundo pintados, faixa de azulejo escuro na linha d'agua, raias e alvos no
    fundo, alvos nas cabeceiras, degraus na ponta rasa e agua."""
    p = Piece(); x0, x1, z0, z1 = POOL; yc = DY - 0.07; ybot = DY - 4.0
    ring = off(PR, T).difference(PR)
    ext_y(p, 'pool_w', ring, ybot, yc)
    us = sorted(set(list(np.linspace(x0, x1, 26)) + [-2.0, 4.0])); vs = [z0, z1]
    p.add('pool_w', grid_map(us, vs, lambda u, v: (u, v), lambda u, v: ybot, lambda u, v: DY - depth(u)))
    ext_y(p, 'lane', off(PR, 0.004).difference(off(PR, -0.004)).intersection(sbox(-99, -99, 99, 99)), WY - 0.12, yc) if False else None
    for (a, b, c, d) in ((x0 - 0.001, x1 + 0.001, z0, z0 + 0.004), (x0 - 0.001, x1 + 0.001, z1 - 0.004, z1), (x0, x0 + 0.004, z0 + 0.004, z1 - 0.004), (x1 - 0.004, x1, z0 + 0.004, z1 - 0.004)):
        p.box('lane', a, b, WY - 0.12, yc, c, d)                                                                       # faixa de azulejo
    for i in range(LANES):                                                                                              # raias no fundo
        zc = z0 + (i + 0.5) * LW; us2 = [u for u in us if x0 + 1.8 <= u <= x1 - 1.8]
        us2 = sorted(set([x0 + 1.8, x1 - 1.8] + us2))
        p.add('lane', grid_map(us2, [zc - 0.13, zc + 0.13], lambda u, v: (u, v), lambda u, v: DY - depth(u) - 0.01, lambda u, v: DY - depth(u) + 0.004))
        for xe in (x0 + 1.8, x1 - 1.8):
            us3 = [xe - 0.5, xe, xe + 0.5]; p.add('lane', grid_map(us3, [zc - 0.5, zc - 0.37], lambda u, v: (u, v), lambda u, v: DY - depth(u) - 0.01, lambda u, v: DY - depth(u) + 0.004)) if False else None
            p.add('lane', grid_map([xe - 0.13, xe + 0.13], [zc - 0.5, zc + 0.5], lambda u, v: (u, v), lambda u, v: DY - depth(u) - 0.012, lambda u, v: DY - depth(u) + 0.006))
        for (xw, s) in ((x0, 1), (x1, -1)):                                                                             # alvos nas cabeceiras
            yb_ = DY - depth(xw + s * 0.01) + 0.1; a, b = sorted((xw, xw + s * 0.004))
            p.box('lane', a, b, yb_, WY - 0.6, zc - 0.13, zc + 0.13); p.box('lane', a, b, WY - 0.6, WY - 0.35, zc - 0.4, zc + 0.4)
    for (k, (za, zb)) in enumerate(((-12.4, -12.0), (-12.8, -12.4), (-13.2, -12.8))):                                    # degraus na ponta rasa
        yt = DY - 0.33 - 0.24 * k; p.box('pool_w', x0 + 0.6, x0 + 2.4, DY - 1.2, yt, za, zb)
        p.box('lane', x0 + 0.6, x0 + 2.4, yt, yt + 0.004, zb - 0.06, zb)
    ext_y(p, 'water', off(PR, -0.006), WY - 0.03, WY)
    return p
def coping():
    """Borda de concreto boleada em volta do tanque (pivo: origem, chao), um pouco acima do deck, com faixa antiderrapante."""
    p = Piece(); yc = DY - 0.07
    ext_y(p, 'coping', off(PR, 0.36).difference(off(PR, -0.02)), yc, DY + 0.005)
    ext_y(p, 'coping', off(PR, -0.02).difference(off(PR, -0.04)), yc + 0.012, DY - 0.01)
    ext_y(p, 'lane', off(PR, 0.3).difference(off(PR, 0.24)), DY + 0.005, DY + 0.007)
    return p
def deck_slab():
    """Deck de concreto com juntas de 3 m e ralos (pivo: origem, chao), entre o gradil, o vestiario, a borda e a area de jatos."""
    area = sbox(-FX, FZ0, FX, FZF).difference(off(sbox(-HX, -HZ, HX, HZ), 0.02)).difference(off(PR, 0.36)).difference(Point(SPL[0], SPL[1]).buffer(SPL[2] + 0.2, 48))
    area = area.difference(sbox(-16.6, 0.2, -12.4, 3.4))
    p = Piece(); b = area.bounds
    for x in np.arange(-FX, FX, 3.0):
        for z in np.arange(FZ0, FZF, 3.0):
            q = sbox(x + 0.005, z + 0.005, x + 2.995, z + 2.995).intersection(area); ext_y(p, 'deck', q, GY, DY)
    ext_y(p, 'dark', area.buffer(-0.002, join_style=2), GY, DY - 0.01)
    for (x, z) in [(x, z) for x in (-11.5, -1.5, 8.5) for z in (-9.9, -26.1)] + [(-15.9, -18.0), (13.0, -18.0)]:
        p.box('steel', x - 0.15, x + 0.15, DY, DY + 0.003, z - 0.08, z + 0.08)
        for k in range(6): xx = x - 0.12 + k * 0.048; p.box('dark', xx - 0.01, xx + 0.01, DY + 0.003, DY + 0.004, z - 0.06, z + 0.06)
    return p
def ladder():
    """Escadinha de inox (pivo: borda da agua, deck; local +Z para dentro da piscina): 2 corrimaos curvos chumbados no deck e 3
    degraus dentro d'agua."""
    p = Piece()
    for x in (-0.25, 0.25):
        pts = [(x, DY, -0.55), (x, DY + 0.75, -0.5), (x, DY + 0.86, -0.36), (x, DY + 0.82, -0.16), (x, DY + 0.6, 0.04), (x, DY + 0.2, 0.09), (x, WY - 1.15, 0.09)]
        for (a, b) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', a, b, 0.024, 10)
        for q in (pts[0],): p.cyl('chrome', 0.05, DY, DY + 0.01, x, -0.55, 14)
        seg_cyl(p, 'chrome', (x, WY - 1.15, 0.09), (x, WY - 1.15, 0.006), 0.02, 8)
    for k in range(3): y = WY - 0.25 - k * 0.3; p.cham('chrome', -0.25, 0.25, y - 0.025, y, 0.04, 0.17, 0.006)
    return p
def start_block():
    """Bloco de largada (pivo: borda da agua, deck; local +Z para a piscina): pedestal, tampo inclinado antiderrapante, alcas de
    costas e quadro de cor da raia."""
    p = Piece()
    p.cham('coping', -0.25, 0.25, DY, DY + 0.62, -0.55, -0.05, 0.02)
    p.hull('coping', [(x, y, z) for x in (-0.28, 0.28) for (y, z) in ((DY + 0.62, -0.6), (DY + 0.62, 0.04), (DY + 0.7, -0.6), (DY + 0.66, 0.04))])
    p.hull('grip', [(x, y, z) for x in (-0.26, 0.26) for (y, z) in ((DY + 0.701, -0.58), (DY + 0.661, 0.02), (DY + 0.705, -0.58), (DY + 0.665, 0.02))])
    for x in (-0.22, 0.22): seg_cyl(p, 'chrome', (x, DY + 0.62, 0.02), (x, DY + 0.35, 0.1), 0.014, 8); seg_cyl(p, 'chrome', (x, DY + 0.35, 0.1), (x, DY + 0.3, 0.02), 0.014, 8)
    seg_cyl(p, 'chrome', (-0.22, DY + 0.35, 0.1), (0.22, DY + 0.35, 0.1), 0.014, 8)
    p.box('float_b', -0.15, 0.15, DY + 0.3, DY + 0.5, -0.552, -0.55)
    return p
def lane_rope(L1):
    """Raia de boias (pivo: inicio, na linha d'agua; ao longo de +X): boias em gomos de cores, cabo e esticadores nas pontas."""
    p = Piece(); n = int(L1 / 0.25)
    for i in range(n):
        a = i * L1 / n; b = (i + 1) * L1 / n - 0.012
        c = 'float_r' if (i < 20 or i >= n - 20) else ('float_w' if (i // 4) % 2 else 'float_b')
        disc_x(p, c, 0.06, a + 0.012, b, 0.0, 0.0, 10); disc_x(p, 'dark', 0.035, b, b + 0.012, 0.0, 0.0, 8)
    for x in (0.0, L1): p.box('chrome', x - 0.02, x + 0.02, -0.04, 0.04, -0.04, 0.04)
    return p
def lane_anchor():
    p = Piece(); p.box('chrome', -0.03, 0.03, -0.12, 0.0, -0.05, 0.05); seg_cyl(p, 'chrome', (0.0, -0.03, 0.0), (0.12, -0.03, 0.0), 0.012, 6); return p
def diving_board(h=1.0):
    """Trampolim (pivo: borda da agua, deck; local +Z sobre a agua): prancha de fibra com lixa, base de concreto (1 m) ou torre de
    aco com escada (3 m), apoio de giro amarelo, corrimaos."""
    p = Piece(); yb = DY + h; z0, z1 = -1.8, 3.0
    p.cham('board', -0.25, 0.25, yb, yb + 0.06, z0, z1, 0.015); p.box('grip', -0.22, 0.22, yb + 0.06, yb + 0.063, z0 + 0.1, z1 - 0.1)
    if h < 2:
        p.cham('coping', -0.45, 0.45, DY, yb - 0.08, z0 - 0.1, z0 + 0.5, 0.02); p.cham('steel', -0.3, 0.3, yb - 0.08, yb, z0, z0 + 0.4, 0.01)
        p.cham('yellowp', -0.35, 0.35, DY, yb - 0.12, -0.35, -0.05, 0.015); p.cyl('steel', 0.06, yb - 0.12, yb, 0.0, -0.2, 12)
        for s in (-1, 1):
            pts = [(s * 0.45, DY, z0 - 0.6), (s * 0.45, yb + 0.9, z0 - 0.3), (s * 0.4, yb + 0.9, z0 + 0.6), (s * 0.35, yb + 0.1, z0 + 1.2)]
            for (a, b) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', a, b, 0.024, 10)
        for k in range(3): y = DY + (k + 1) * h / 4; p.cham('coping', -0.4 + 0.012 * k, 0.4 - 0.012 * k, DY, y, z0 - 0.5 - (2 - k) * 0.26, z0 - 0.08, 0.01)
    else:
        for (x, z) in ((-0.55, z0 - 0.2), (0.55, z0 - 0.2), (-0.55, z0 + 1.2), (0.55, z0 + 1.2)):
            p.box('steel', x - 0.06, x + 0.06, DY, yb - 0.2, z - 0.06, z + 0.06); p.box('steel', x - 0.12, x + 0.12, DY, DY + 0.02, z - 0.12, z + 0.12)
        for y in (DY + 0.9, DY + 1.9):
            for (a, b) in (((-0.55, z0 - 0.2), (0.55, z0 - 0.2)), ((-0.55, z0 + 1.2), (0.55, z0 + 1.2)), ((-0.55, z0 - 0.2), (-0.55, z0 + 1.2)), ((0.55, z0 - 0.2), (0.55, z0 + 1.2))):
                seg_cyl(p, 'steel', (a[0], y, a[1]), (b[0], y, b[1]), 0.03, 8)
        p.cham('steel', -0.62, 0.62, yb - 0.2, yb - 0.08, z0 - 0.3, z0 + 1.3, 0.01); p.box('grip', -0.6, 0.6, yb - 0.08, yb - 0.077, z0 - 0.28, z0 + 0.2)
        p.cham('yellowp', -0.2, 0.2, yb - 0.08, yb, z0 + 0.9, z0 + 1.1, 0.01)
        for s in (-1, 1):
            for (a, b) in (((s * 0.6, yb - 0.08, z0 - 0.28), (s * 0.6, yb + 1.0, z0 - 0.28)), ((s * 0.6, yb + 1.0, z0 - 0.28), (s * 0.6, yb + 1.0, z0 + 1.25)),
                           ((s * 0.6, yb - 0.08, z0 + 1.25), (s * 0.6, yb + 1.0, z0 + 1.25)), ((s * 0.6, yb + 0.5, z0 - 0.28), (s * 0.6, yb + 0.5, z0 + 1.25)),
                           ((s * 0.45, yb + 1.0, z0 + 1.25), (s * 0.35, yb + 0.15, z0 + 2.2)), ((s * 0.6, yb + 1.0, z0 + 1.25), (s * 0.45, yb + 1.0, z0 + 1.25))):
                seg_cyl(p, 'chrome', a, b, 0.024, 10)
        za, zb = z0 - 0.3, z0 - 0.3 - (yb - DY) * 0.6                                                                    # escada
        for s in (-1, 1):
            p.seg('steel', (s * 0.4, DY, zb), (s * 0.4, yb - 0.1, za), 0.05, 0.16)
            seg_cyl(p, 'chrome', (s * 0.46, DY + 0.9, zb + 0.05), (s * 0.46, yb + 0.9, za), 0.024, 10); seg_cyl(p, 'chrome', (s * 0.46, DY, zb + 0.05), (s * 0.46, DY + 0.9, zb + 0.05), 0.024, 10)
        n = 12
        for k in range(1, n):
            t = k / n; y = DY + t * (yb - 0.1 - DY); z = zb + t * (za - zb); p.cham('grip', -0.37, 0.37, y - 0.03, y, z - 0.1, z + 0.1, 0.006)
    return p

# ============================================================================ deck: escorregador, salva-vidas, mobiliario, jatos
def bez(p0, p1, p2, p3, t):
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3)); u = 1 - t
    return u ** 3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t ** 3 * p3
def water_slide():
    """Escorregador (pivo: borda da agua, deck; local +Z para a piscina): torre de cano com escada e plataforma, calha de fibra em
    U fazendo curva, com apoios, saida sobre a agua."""
    p = Piece(); hp = 2.7; tx, tz = -1.6, -2.6                                                                           # plataforma
    for (x, z) in ((tx - 0.45, tz - 0.45), (tx + 0.45, tz - 0.45), (tx - 0.45, tz + 0.45), (tx + 0.45, tz + 0.45)):
        p.cyl('blue_p', 0.05, DY, hp + 1.0, x, z, 12); p.cyl('blue_p', 0.1, DY, DY + 0.02, x, z, 14)
    p.cham('steel', tx - 0.5, tx + 0.5, hp - 0.06, hp, tz - 0.5, tz + 0.5, 0.01); p.box('grip', tx - 0.48, tx + 0.48, hp, hp + 0.003, tz - 0.48, tz + 0.48)
    for y in (hp + 0.5, hp + 1.0):
        for (a, b) in (((tx - 0.45, tz - 0.45), (tx - 0.45, tz + 0.45)), ((tx - 0.45, tz + 0.45), (tx + 0.45, tz + 0.45))):
            seg_cyl(p, 'blue_p', (a[0], y, a[1]), (b[0], y, b[1]), 0.03, 8)
    for y in (0.9, 1.8): seg_cyl(p, 'blue_p', (tx - 0.45, y, tz - 0.45), (tx + 0.45, y, tz + 0.45), 0.025, 8) if False else seg_cyl(p, 'blue_p', (tx - 0.45, y, tz + 0.45), (tx + 0.45, y, tz + 0.45), 0.025, 8)
    for s in (-1, 1): seg_cyl(p, 'blue_p', (tx + s * 0.3, DY, tz - 1.6), (tx + s * 0.3, hp + 0.9, tz - 0.45), 0.03, 8)             # escada
    for k in range(1, 9):
        t = k / 9; y = DY + t * (hp - DY); z = tz - 1.6 + t * 1.15; p.cham('steel', tx - 0.3, tx + 0.3, y - 0.03, y, z - 0.06, z + 0.06, 0.006)
    a0 = (tx + 0.5, hp + 0.02, tz); P = [a0, (tx + 2.2, hp - 0.2, tz), (0.4, 1.4, -1.8), (0.0, DY + 0.35, 0.3)]
    N = 26; cs = []
    for i in range(N + 1):
        t = i / N; c = bez(*P, t); c2 = bez(*P, min(1, t + 0.01)); c1 = bez(*P, max(0, t - 0.01)); d = c2 - c1; d[1] = 0; d = d / np.linalg.norm(d)
        n = np.array([-d[2], 0, d[0]]); cs.append((c, n))
    for (c0, n0), (c1, n1) in zip(cs[:-1], cs[1:]):
        for (u0, u1, v0, v1, m) in ((-0.3, 0.3, -0.05, 0.0, 'blue_p'), (-0.33, -0.28, -0.05, 0.3, 'blue_p'), (0.28, 0.33, -0.05, 0.3, 'blue_p'), (-0.27, 0.27, 0.0, 0.004, 'white_u')):
            pts = [tuple(c + n * u + np.array([0, v, 0])) for (c, n) in ((c0, n0), (c1, n1)) for u in (u0, u1) for v in (v0, v1)]
            p.hull(m, pts)
    for t in (0.35, 0.6, 0.85):
        c = bez(*P, t); p.cyl('blue_p', 0.05, DY, c[1] - 0.05, c[0], c[2], 12); p.cyl('blue_p', 0.1, DY, DY + 0.02, c[0], c[2], 14)
    return p
def guard_chair():
    """Cadeira de salva-vidas (pivo: chao; frente +Z): estrutura de cano, assento alto com encosto, apoio de pes, escada atras,
    guarda-sol de lona e boia de resgate."""
    p = Piece(); hs = DY + 1.9
    for (x, z0, z1) in ((-0.4, -0.7, -0.2), (0.4, -0.7, -0.2)):
        seg_cyl(p, 'chrome', (x, DY, z0), (x, hs + 0.9, z1 + 0.05), 0.03, 10); seg_cyl(p, 'chrome', (x, DY, 0.5), (x, hs - 0.05, 0.05), 0.03, 10)
    for y in (DY + 0.6, DY + 1.2): seg_cyl(p, 'chrome', (-0.4, y, -0.48), (0.4, y, -0.48), 0.02, 8)
    for k in range(1, 6): y = DY + k * 0.33; z = -0.7 + (y - DY) / (hs + 0.9 - DY) * 0.55; p.cham('wood', -0.38, 0.38, y - 0.03, y, z - 0.07, z + 0.07, 0.006)
    p.cham('wood', -0.42, 0.42, hs - 0.04, hs, -0.2, 0.25, 0.008); p.cham('wood', -0.42, 0.42, hs + 0.1, hs + 0.6, -0.26, -0.22, 0.008)
    p.cham('wood', -0.42, 0.42, hs - 0.75, hs - 0.71, 0.35, 0.6, 0.008)
    seg_cyl(p, 'chrome', (0.42, hs - 0.5, -0.2), (0.42, hs + 2.0, -0.2), 0.02, 8)
    lathe(p, 'canvas', [(0.0, hs + 2.15), (0.75, hs + 1.85), (0.76, hs + 1.82)], 0.42, -0.2, 0.0, 12)
    q = Piece(); q.hull('orange_u', [(x, y, z) for x in (-0.07, 0.07) for (y, z) in ((0.0, 0.0), (0.0, 0.1), (0.9, 0.0), (0.9, 0.1))]); p.merge(q, tr(-0.5, hs - 1.0, 0.0))
    return p
def umbrella_table():
    """Mesa redonda com guarda-sol listrado e 4 cadeiras de plastico (pivo: centro, deck)."""
    p = Piece(); y = DY
    p.cyl('plastic_w', 0.45, y + 0.7, y + 0.73, 0, 0, 24); p.cyl('steel', 0.035, y, y + 0.7, 0, 0, 10); p.cyl('steel', 0.3, y, y + 0.02, 0, 0, 16)
    p.cyl('steel', 0.02, y + 0.73, y + 2.45, 0, 0, 8)
    n = 12; r = 1.25; ya, yt = y + 2.05, y + 2.5
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n; m = 'orange_u' if k % 2 == 0 else 'white_u'
        p.hull(m, [(0, yt, 0), (0, yt - 0.01, 0), (r * math.cos(a0), ya, r * math.sin(a0)), (r * math.cos(a1), ya, r * math.sin(a1)), (r * math.cos(a0), ya - 0.012, r * math.sin(a0)), (r * math.cos(a1), ya - 0.012, r * math.sin(a1))])
        p.hull(m, [(r * math.cos(a), yy, r * math.sin(a)) for a in (a0, a1) for yy in (ya - 0.012, ya - 0.18)] + [(r * 1.003 * math.cos(a), ya - 0.18, r * 1.003 * math.sin(a)) for a in (a0, a1)])
    p.sphere('steel', 0.04, 0, yt + 0.02, 0, 1)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4; cx, cz = 0.85 * math.cos(a), 0.85 * math.sin(a); q = chair_p(); p.merge(q, rot_y(90 - math.degrees(a), (cx, y, cz)))
    return p
def chair_p():
    """Cadeira de plastico empilhavel (pivo: centro, chao; frente para -Z, que aponta para a mesa)."""
    p = Piece()
    for (x, z) in ((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)): seg_cyl(p, 'plastic_w', (x * 1.1, 0.0, z * 1.1), (x, 0.43, z), 0.02, 8)
    p.cham('plastic_w', -0.23, 0.23, 0.43, 0.47, -0.23, 0.22, 0.02)
    p.hull('plastic_w', [(x, y, z) for x in (-0.22, 0.22) for (y, z) in ((0.47, 0.2), (0.47, 0.24), (0.85, 0.28), (0.85, 0.32))])
    for k in range(4): x = -0.15 + k * 0.1; p.box('dark', x - 0.015, x + 0.015, 0.6, 0.78, 0.25, 0.3) if False else None
    return p
def lounger():
    """Espreguicadeira de ripas de plastico com encosto levantado e rodinhas (pivo: centro, deck; cabeceira em -Z)."""
    p = Piece(); y = DY
    for s in (-1, 1):
        seg_cyl(p, 'steel', (s * 0.3, y + 0.33, -0.9), (s * 0.3, y + 0.33, 0.95), 0.02, 8)
        for z in (-0.75, 0.85): seg_cyl(p, 'steel', (s * 0.3, y + 0.06, z), (s * 0.3, y + 0.33, z), 0.02, 8)
        disc_x(p, 'rubber', 0.07, s * 0.33 - 0.02, s * 0.33 + 0.02, y + 0.07, -0.85, 14) if False else disc_x(p, 'rubber', 0.07, *sorted((s * 0.31, s * 0.35)), y + 0.07, -0.85, 14)
    for k in range(13): z = -0.15 + k * 0.085; p.cham('plastic_b', -0.3, 0.3, y + 0.33, y + 0.36, z, z + 0.07, 0.006)
    for k in range(7):
        t = k * 0.11; p.hull('plastic_b', [(x, y + 0.36 + t * 0.62 + dy, -0.2 - t * 0.79 + dz) for x in (-0.3, 0.3) for (dy, dz) in ((0.0, 0.0), (0.03, 0.0), (0.06, -0.06), (0.03, -0.06))])
    seg_cyl(p, 'steel', (0.0, y + 0.33, -0.15), (0.0, y + 0.55, -0.42), 0.015, 6)
    return p
def splash_pad():
    """Area de jatos (pivo: centro, chao): piso de borracha azul com circulo amarelo, cogumelo de agua com chapeu laranja e borrifo,
    6 bicos no chao com jatos, arco de cano com chuveiro e ralo."""
    p = Piece(); R = SPL[2] + 0.2
    ext_y(p, 'concrete', Point(0, 0).buffer(R, 48), GY, DY - 0.04); ext_y(p, 'splash', Point(0, 0).buffer(R, 48), DY - 0.04, DY + 0.01)
    ring_y(p, 'yellowp', 1.4, 1.55, DY + 0.01, DY + 0.014, 0, 0, 48); ring_y(p, 'coping', R - 0.12, R, DY + 0.01, DY + 0.03, 0, 0, 48)
    p.cyl('chrome', 0.18, DY + 0.01, DY + 0.014, 0, 0, 16)
    lathe(p, 'blue_p', [(0.12, DY + 0.01), (0.1, DY + 0.12), (0.07, DY + 0.25), (0.07, DY + 1.9), (0.0, DY + 1.9)], sec=14)
    lathe(p, 'orange_u', [(0.07, DY + 1.85), (0.9, DY + 1.95), (1.0, DY + 2.02), (0.95, DY + 2.1), (0.6, DY + 2.28), (0.0, DY + 2.35)], sec=24)
    ring_y(p, 'spray', 0.96, 1.0, DY + 0.4, DY + 1.85, 0, 0, 32) if False else None
    for k in range(16):
        a = 2 * math.pi * k / 16; seg_cyl(p, 'spray', (0.97 * math.cos(a), DY + 1.88, 0.97 * math.sin(a)), (1.08 * math.cos(a), DY + 0.02, 1.08 * math.sin(a)), 0.012, 4)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3; x, z = 2.0 * math.cos(a), 2.0 * math.sin(a)
        p.cyl('chrome', 0.05, DY + 0.01, DY + 0.016, x, z, 12); seg_cyl(p, 'spray', (x, DY + 0.016, z), (x * 0.98, DY + 0.9 + 0.2 * (k % 2), z * 0.98), 0.02, 6)
    for s in (-1, 1): p.cyl('yellowp', 0.05, DY + 0.01, DY + 2.1, s * 1.9, -1.0, 12)
    q = Piece()
    for k in range(13):
        a0, a1 = math.pi * k / 13, math.pi * (k + 1) / 13; seg_cyl(q, 'yellowp', (1.9 * math.cos(a0), 0.4 * math.sin(a0), 0), (1.9 * math.cos(a1), 0.4 * math.sin(a1), 0), 0.05, 10)
    p.merge(q, tr(0, DY + 2.1, -1.0))
    for x in (-0.8, 0.0, 0.8): lathe(p, 'chrome', [(0.03, 0.0), (0.09, -0.06), (0.0, -0.07)], x, -1.0, DY + 2.5 - 0.0, 12); seg_cyl(p, 'spray', (x, DY + 2.43, -1.0), (x, DY + 0.02, -1.0), 0.05, 6)
    return p
def flagpole():
    """Mastro de bandeira de aco com bola, roldana, adrica e bandeira listrada sem simbolos (pivo: chao)."""
    p = Piece(); h = 9.0
    lathe(p, 'concrete', [(0.35, -0.2), (0.35, 0.15), (0.3, 0.2), (0.0, 0.2)], sec=8)
    lathe(p, 'chrome', [(0.07, 0.2), (0.06, 4.0), (0.04, h), (0.0, h)], sec=12); p.sphere('brass', 0.08, 0, h + 0.06, 0, 1)
    p.cyl('chrome', 0.06, h - 0.1, h - 0.02, 0, 0, 12); seg_cyl(p, 'dark', (0.065, h - 0.08, 0.0), (0.065, 1.3, 0.0), 0.004, 4); p.box('chrome', 0.04, 0.1, 1.2, 1.35, -0.015, 0.015)
    fy0, fy1, fx = h - 1.5, h - 0.15, 2.2                                                                              # flamula do clube: campo verde-agua com boia
    p.hull('board', [(0.07 + x, y, dz) for x in (0.0, fx) for y in (fy0, fy1) for dz in (-0.004, 0.004)])
    cx, cy = 0.07 + fx * 0.45, (fy0 + fy1) / 2
    for (r, t, m) in ((0.46, 0.006, 'white_u'), (0.36, 0.008, 'orange_u'), (0.2, 0.01, 'white_u')): disc_z(p, m, r, -t, t, cx, cy, 28)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4; p.hull('white_u', [(cx + rr * math.cos(a + da), cy + rr * math.sin(a + da), dz) for rr in (0.2, 0.36) for da in (-0.2, 0.2) for dz in (-0.009, 0.009)])
    return p
def pole_clock():
    """Relogio de poste de 2 faces, sem numeros (pivo: chao)."""
    p = Piece(); lathe(p, 'iron', [(0.18, -0.2), (0.18, 0.25), (0.1, 0.35), (0.07, 0.5), (0.06, 2.8), (0.1, 2.85), (0.0, 2.86)], sec=14)
    p.cyl('iron', 0.47, 2.85, 3.85, 0, 0, 24) if False else None
    c = trimesh.creation.cylinder(radius=0.46, height=0.16, sections=32); c.apply_translation([0, 0, 0]); c.apply_translation([0, 3.35, 0]); p.add('iron', c)
    for s in (-1, 1):
        q = wall_clock(0.4); p.merge(q, rot_y(0 if s > 0 else 180, (0, 3.35, s * 0.08)))
    p.sphere('iron', 0.08, 0, 3.86, 0, 1); p.cyl('iron', 0.03, 3.8, 3.86, 0, 0, 8)
    return p
def foot_shower():
    """Chuveirinho de deck: coluna de inox com crivo, botao de empurrar e grelha no chao (pivo: chao)."""
    p = Piece(); p.box('chrome', -0.4, 0.4, DY, DY + 0.02, -0.4, 0.4)
    for k in range(9): x = -0.34 + k * 0.085; p.box('dark', x - 0.015, x + 0.015, DY + 0.02, DY + 0.021, -0.34, 0.34)
    p.cyl('chrome', 0.05, DY, DY + 2.3, -0.32, -0.32, 12); seg_cyl(p, 'chrome', (-0.32, DY + 2.3, -0.32), (-0.05, DY + 2.3, -0.05), 0.025, 8)
    lathe(p, 'chrome', [(0.02, 0.05), (0.1, -0.02), (0.0, -0.03)], -0.05, -0.05, DY + 2.25, 16); p.cham('chrome', -0.3, -0.22, DY + 1.0, DY + 1.08, -0.3, -0.24, 0.008)
    return p
def buoy_post():
    """Poste de boia de resgate com vara de gancho (pivo: chao)."""
    p = Piece(); p.box('redp', -0.05, 0.05, -0.2, 1.7, -0.05, 0.05); q = lifebuoy_wall(); p.merge(q, tr(0, 1.25, 0.05))
    p.box('steel', -0.08, 0.08, 0.5, 0.53, 0.05, 0.12); seg_cyl(p, 'metal', (0.1, 0.52, 0.1), (0.1, 3.1, 0.1), 0.018, 6)
    seg_cyl(p, 'metal', (0.1, 3.1, 0.1), (0.25, 3.25, 0.1), 0.015, 6); seg_cyl(p, 'metal', (0.25, 3.25, 0.1), (0.35, 3.05, 0.1), 0.015, 6)
    return p
def filters():
    """Casa de maquinas a ceu aberto (pivo: centro da base, chao): base de concreto, 2 filtros de areia, bomba com motor, tubos com
    registros e manometros, quadro eletrico."""
    p = Piece(); p.cham('concrete', -2.1, 2.1, GY, DY + 0.15, -1.6, 1.6, 0.02); y = DY + 0.15
    for x in (-1.1, 0.3):
        lathe(p, 'tank', [(0.0, y), (0.45, y + 0.05), (0.6, y + 0.3), (0.62, y + 1.2), (0.5, y + 1.45), (0.0, y + 1.55)], x, 0.3, 0.0, 20)
        for k in range(3): a = k * 2 * math.pi / 3; seg_cyl(p, 'steel', (x + 0.5 * math.cos(a), y, 0.3 + 0.5 * math.sin(a)), (x + 0.45 * math.cos(a), y + 0.25, 0.3 + 0.45 * math.sin(a)), 0.03, 6)
        p.cyl('steel', 0.08, y + 1.5, y + 1.62, x, 0.3, 12); disc_z(p, 'gauge', 0.06, 0.92, 0.95, x, y + 1.0, 14) if False else None
        seg_cyl(p, 'steel', (x, y + 1.58, 0.3), (x, y + 1.58, -1.0), 0.05, 10); disc_z(p, 'chrome', 0.07, -0.42, -0.36, x, y + 1.58, 14)
        p.cyl('steel', 0.012, y + 1.63, y + 1.75, x, 0.0, 6); disc_z(p, 'gauge', 0.05, -0.02, 0.0, x, y + 1.8, 14); disc_z(p, 'chrome', 0.055, -0.03, -0.02, x, y + 1.8, 14)
    p.cham('pump', 1.0, 1.4, y, y + 0.32, -0.6, 0.0, 0.02); p.cyl('pump', 0.18, y + 0.32, y + 0.62, 1.2, -0.3, 16)
    disc_x(p, 'pump', 0.2, 1.4, 1.95, y + 0.45, -0.3, 16); disc_x(p, 'dark', 0.21, 1.95, 1.97, y + 0.45, -0.3, 16)
    seg_cyl(p, 'steel', (-1.1, y + 1.58, -1.0), (1.2, y + 1.58, -1.0), 0.05, 10); seg_cyl(p, 'steel', (1.2, y + 1.58, -1.0), (1.2, y + 0.62, -1.0), 0.05, 10)
    seg_cyl(p, 'steel', (1.2, y + 0.62, -1.0), (1.2, y + 0.62, -0.3), 0.05, 10)
    seg_cyl(p, 'steel', (1.2, y + 0.45, 0.0), (1.2, y + 0.45, 1.6), 0.06, 10); seg_cyl(p, 'steel', (1.2, y + 0.45, 1.6), (1.2, GY, 1.6), 0.06, 10)
    p.cham('steel', -2.0, -1.8, y, y + 1.6, 1.0, 1.5, 0.006); p.cham('metal', -1.8, -1.55, y + 0.7, y + 1.5, 1.02, 1.48, 0.01); p.box('dark', -1.552, -1.546, y + 1.0, y + 1.2, 1.15, 1.35)
    return p
def fence_p(L1=2.0):
    """Gradil de ferro (pivo: inicio, chao; ao longo de +X): mourao quadrado com capa, 2 travessas e grades com ponta."""
    p = Piece(); h = 1.6
    p.box('iron', -0.04, 0.04, -0.3, h + 0.06, -0.04, 0.04); p.hull('iron', [(x, h + 0.06, z) for x in (-0.05, 0.05) for z in (-0.05, 0.05)] + [(0, h + 0.14, 0)])
    for y in (0.12, h - 0.1): p.box('iron', 0.04, L1 - 0.04, y, y + 0.04, -0.015, 0.015)
    for x in np.arange(0.12, L1 - 0.06, 0.12):
        p.box('iron', x - 0.009, x + 0.009, 0.06, h, -0.009, 0.009); p.hull('iron', [(x + dx, h, z) for dx in (-0.016, 0.016) for z in (-0.016, 0.016)] + [(x, h + 0.07, 0)])
    return p
def fence_end():
    p = Piece(); p.box('iron', -0.04, 0.04, -0.3, 1.66, -0.04, 0.04); p.hull('iron', [(x, 1.66, z) for x in (-0.05, 0.05) for z in (-0.05, 0.05)] + [(0, 1.74, 0)]); return p
def tree(h=6.0, r=1.9, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.18, -0.2), (0.13, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('leaf2', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def site():
    """Terreno (pivo: origem): gramado, calcada da frente com juntas, caminho e patamar da entrada, guia, rua com faixa amarela e
    canteiros de terra junto do gradil."""
    p = Piece(); box_ = sbox(SX0, SZ0, SX1, SZ1)
    enc = sbox(-FX, FZ0, FX, FZF); bh = off(sbox(-HX, -HZ, HX, HZ), 0.02)
    apron = sbox(-HX - 0.02, HZ + 0.02, HX + 0.02, HZ + 1.4).union(sbox(-1.8, HZ + 1.4, 1.8, SIDEW[0]))
    side = sbox(SX0, SIDEW[0], SX1, SIDEW[1]); street = sbox(SX0, STREET[0] + 0.15, SX1, SZ1); curb = sbox(SX0, STREET[0], SX1, STREET[0] + 0.15)
    p.merge(paving(apron, DY, 1.5)); p.merge(paving(side, DY, 1.5))
    ext_y(p, 'curb', curb, GY, DY); ext_y(p, 'asphalt', street, GY, 0.0)
    beds = unary_union([sbox(x0, z0, x1, z1) for (x0, z0, x1, z1) in ((-FX - 1.2, FZ0 - 1.2, -FX - 0.1, FZF), (FX + 0.1, FZ0 - 1.2, FX + 1.2, FZF), (-FX - 1.2, FZ0 - 1.2, FX + 1.2, FZ0 - 0.1))])
    ext_y(p, 'soil', beds, GY, GR + 0.02)
    grass = box_.difference(unary_union([enc, bh, apron, side, street, curb, beds])); ext_y(p, 'grass', grass, GY, GR)
    for x in np.arange(SX0 + 0.5, SX1 - 1.0, 3.0): p.box('yellowp', x, x + 1.5, 0.0, 0.004, (STREET[0] + SZ1) / 2 + 0.1, (STREET[0] + SZ1) / 2 + 0.22)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
pieces = {'w_win': module('win'), 'w_win_s': module('win_s'), 'w_door': module('door'), 'w_ticket': module('ticket'), 'w_entry': module('entry', -2.0, 2.0),
          'w_gdoor': module('gdoor', -2.0, 2.0), 'w_side': module('win_s', -SWL / 2, SWL / 2), 'w_corner': corner(), 'w_corner_b': corner(True), 'w_end_l': module('win_s', end=-1), 'w_end_r': module('win_s', end=1),
          'roof_main': roof_face(RX), 'roof_end': roof_face(0.0, False), 'roof_ridge': roof_ridge(), 'roof_vent': roof_vent(), 'vent_pipe': vent_pipe(),
          'downspout': downspout(YW - K * OV + 0.02 - 0.12, OV + 0.095), 'entry_canopy': entry_canopy(), 'wall_lamp': wall_lamp(), 'lifebuoy_wall': lifebuoy_wall(),
          'ceiling': ceiling(), 'ceiling_light': ceiling_light(), 'partition': partition(), 'floor_lobby': floor_lobby(), 'floor_lr': floor_lr(),
          'door_leaf_glass': door_glass(0.87, 2.28), 'door_leaf_back': door_glass(0.86, 2.2), 'door_leaf_metal': door_metal(0.8, 2.12), 'door_leaf_int': door_interior(0.84, 2.07),
          'cashier': cashier(), 'lobby_bench': lobby_bench(), 'fountain': fountain(), 'wall_clock': wall_clock(0.3), 'poster': poster(0), 'poster_b': poster(1),
          'plant_pot': plant_pot(), 'trash_can': trash_can(), 'lockers': lockers(1.8, 3), 'lr_bench': lr_bench(), 'shower_bay': shower_bay(), 'stalls': stalls(),
          'wc': wc(), 'urinal': urinal(), 'urinal_screen': urinal_screen(), 'sink_bank': sink_bank(), 'towel_disp': towel_disp(),
          'basin': basin(), 'coping': coping(), 'deck': deck_slab(), 'ladder': ladder(), 'start_block': start_block(), 'lane_rope': lane_rope(POOL[1] - POOL[0]),
          'lane_anchor': lane_anchor(), 'board_1m': diving_board(1.0), 'board_3m': diving_board(3.0), 'water_slide': water_slide(), 'guard_chair': guard_chair(),
          'umbrella_table': umbrella_table(), 'lounger': lounger(), 'splash_pad': splash_pad(), 'flagpole': flagpole(), 'pole_clock': pole_clock(),
          'foot_shower': foot_shower(), 'buoy_post': buoy_post(), 'filters': filters(), 'fence_2': fence_p(2.0), 'fence_195': fence_p(1.95), 'fence_end': fence_end(),
          'lamp_post': lamp_post(), 'park_bench': park_bench(), 'bike_rack': bike_rack(), 'site': site(), 'tree': tree(), 'tree_b': tree(5.0, 1.6, 'leaf2', 4),
          'bush': bush(), 'player_scale_ref': player_ref()}

# ============================================================================ montagem: vestiario
ex = ['bath', 'ext', 'floor0']
for (x, k) in ((-9, 'w_end_l'), (-7, 'w_win'), (-5, 'w_win'), (-3, 'w_ticket'), (0, 'w_entry'), (3, 'w_win'), (5, 'w_win'), (7, 'w_win'), (9, 'w_end_r')):
    put(k, x, 0, HZ, 0, ex + ['front'])
for (x, k) in ((-9, 'w_end_r'), (-7, 'w_door'), (-5, 'w_win'), (-3, 'w_win_s'), (0, 'w_gdoor'), (3, 'w_win_s'), (5, 'w_win'), (7, 'w_door'), (9, 'w_end_l')):
    put(k, x, 0, -HZ, 180, ex + ['back'])
for k in range(4):
    z = -HZ + T + SWL * (k + 0.5); put('w_side', -HX, 0, z, -90, ex + ['left']); put('w_side', HX, 0, z, 90, ex + ['right'])
for (x, z, ry, tg) in ((HX, HZ, 0, 'front'), (HX, -HZ, 90, 'back'), (-HX, -HZ, 180, 'back'), (-HX, HZ, -90, 'front')): put('w_corner' if ry in (0, 180) else 'w_corner_b', x, 0, z, ry, ex + [tg])
for (x, z, ry) in ((-HX, 3.55, -90), (-HX, -3.55, -90), (HX, 3.55, 90), (HX, -3.55, 90)): put('downspout', x, 0, z, ry, ex)
rf = ['bath', 'roof']
put('roof_main', 0, 0, 0, 0, rf); put('roof_main', 0, 0, 0, 180, rf); put('roof_end', RX, 0, 0, 90, rf); put('roof_end', -RX, 0, 0, -90, rf); put('roof_ridge', 0, 0, 0, 0, rf)
for x in (-3.0, 3.0): put('roof_vent', x, YW + K * (HZ - 2.0) + 0.04, -2.0, 180, rf)
for x in (-6.5, 6.5): put('vent_pipe', x, YW + K * (HZ - 1.6) + 0.03, -1.6, 0, rf)
put('ceiling', 0, 0, 0, 0, rf)
for (x, z) in [(x, z) for x in (-1.8, 1.8) for z in (-1.6, 1.6)] + [(s * x, z) for s in (-1, 1) for x in (5.6, 8.2) for z in (-1.8, 1.8)]: put('ceiling_light', x, Y0 + CEIL, z, 0, rf)
put('entry_canopy', 0, 0, HZ, 0, ex + ['front'])
for x in (-1.45, 1.45): put('wall_lamp', x, Y0 + 2.45, -HZ, 180, ex + ['back'])
for x in (-7.0, 7.0): put('wall_lamp', x, Y0 + 2.75, -HZ, 180, ex + ['back'])
for x in (-4.0, 4.0): put('lifebuoy_wall', x, Y0 + 1.55, -HZ, 180, ex + ['back'])
# ---------------------------------------------------------------- portas
dt = ['bath', 'floor0']
put('door_leaf_glass', -0.89, Y0 + 0.008, HZ - 0.15, 0, dt, door=-90); put('door_leaf_glass', 0.89, Y0 + 0.008, HZ - 0.15, 180, dt, door=90)
put('door_leaf_back', -0.44, Y0 + 0.008, -HZ + 0.15, 0, dt, door=90)
for x in (-7.0, 7.0): put('door_leaf_metal', x - 0.41, Y0 + 0.008, -HZ + 0.15, 0, dt, door=90)
put('door_leaf_int', -PX, Y0 + 0.005, DZ - 0.42, -90, dt, door=-90); put('door_leaf_int', PX, Y0 + 0.005, DZ - 0.42, -90, dt, door=90)
# ---------------------------------------------------------------- dentro
it = ['bath', 'floor0']; WI = HZ - T - 0.016; XI = HX - T - 0.016; PI = PX + t_ / 2 + 0.016
put('floor_lobby', 0, 0, 0, 0, it); put('floor_lr', -LRC, 0, 0, 180, it); put('floor_lr', LRC, 0, 0, 0, it)
for x in (-PX, PX): put('partition', x, Y0, -HZ + T, -90, it)
put('cashier', -PX + t_ / 2, Y0, WI, 0, it); put('lobby_bench', PX - t_ / 2 - 0.016, Y0, 0.6, -90, it)
put('fountain', -1.6, Y0, -WI, 0, it); put('wall_clock', PX - t_ / 2, Y0 + 2.3, 0.6, -90, it)
put('poster', -PX + t_ / 2, Y0 + 1.95, -0.6, 90, it); put('poster_b', -PX + t_ / 2, Y0 + 1.95, 0.3, 90, it)
for x in (-1.5, 1.5): put('plant_pot', x, Y0, WI - 0.45, 0, it)
put('trash_can', 2.9, Y0, -WI + 0.4, 0, it)
for s in (-1, 1):
    for x in (6.3, 8.2): put('lockers', s * x, Y0, WI, 180, it)
    for z in (2.15, 0.6): put('lr_bench', s * 6.75, Y0, z, 0, it)
    put('shower_bay', s * XI, Y0, 0.6, -90 * s, it)
    put('sink_bank', s * 5.4, Y0, -WI, 0, it)
    put('towel_disp', s * PI, Y0, -1.3, 90 * s, it)
put('stalls', -XI, Y0, -WI, 0, it); put('stalls', XI, Y0, -WI, -90, it)
for x in (-XI + 0.5, -XI + 1.5): put('wc', x, Y0, -WI, 0, it)
for z in (-WI + 0.5, -WI + 1.5): put('wc', XI, Y0, z, -90, it)
for z in (0.8, 1.6): put('urinal', -PI, Y0, z, -90, it)
for z in (0.4, 1.2, 2.0): put('urinal_screen', -PI, Y0, z, -90, it)
put('sink_bank', PI, Y0, 1.2, 90, it)
# ---------------------------------------------------------------- piscina e deck
pl = ['pool']
for n in ('deck', 'coping', 'basin'): put(n, 0, 0, 0, 0, pl)
x0, x1, z0, z1 = POOL
for x in (-6.0, 8.0): put('ladder', x, 0, z1, 180, pl); put('ladder', x, 0, z0, 0, pl)
for i in range(LANES): put('start_block', x0, 0, z0 + (i + 0.5) * LW, 90, pl)
for k in range(1, LANES):
    z = z0 + k * LW; put('lane_rope', x0, WY, z, 0, pl); put('lane_anchor', x0, WY, z, 0, pl); put('lane_anchor', x1, WY, z, 180, pl)
put('board_3m', x1, 0, z0 + 0.5 * LW, -90, pl); put('board_1m', x1, 0, z1 - 0.5 * LW, -90, pl)
put('water_slide', -9.0, 0, z0, 0, pl)
put('guard_chair', 0.0, 0, -10.9, 180, pl); put('guard_chair', 2.0, 0, -25.4, 0, pl)
for (x, z) in ((-16.0, -8.0), (14.6, -8.2), (14.0, -27.2)): put('umbrella_table', x, 0, z, 0, pl)
for z in (-15.6, -17.1, -18.6, -20.1): put('lounger', 16.6, 0, z, 90, pl)
for x in (4.5, 6.0, 7.5, 9.0): put('lounger', x, 0, -27.6, 0, pl)
put('splash_pad', SPL[0], 0, SPL[1], 0, pl); put('flagpole', 11.6, 0, -6.2, 0, pl); put('pole_clock', -11.6, 0, -6.2, 0, pl)
for x in (-9.2, 9.2): put('foot_shower', x, 0, -5.4, 0, pl)
for (x, z) in ((-15.4, -11.0), (12.3, -11.0), (-15.4, -25.0), (12.6, -25.4)): put('buoy_post', x, 0, z, 0, pl)
put('filters', -14.5, 0, 1.8, 0, pl)
for (x, z) in ((-12.4, -5.0), (13.4, -4.6), (-4.0, -28.8)): put('trash_can', x, DY, z, 0, pl)
# ---------------------------------------------------------------- gradil, terreno
st = ['site']
def run(seq, x0_, z0_, ry, end_post=False):
    r = math.radians(ry); dx, dz = math.cos(r), -math.sin(r); s_ = 0.0
    for (n, Ln) in seq: put(n, x0_ + dx * s_, 0, z0_ + dz * s_, ry, st); s_ += Ln
    if end_post: put('fence_end', x0_ + dx * s_, 0, z0_ + dz * s_, ry, st)
F2 = ('fence_2', 2.0); F195 = ('fence_195', 1.95)
run([F2] * 3 + [F195], -FX, FZF, 0, True); run([F2] * 3 + [F195], FX, FZF, 180, True)
run([F2] * 17, -FX, FZ0, -90); run([F2] * 17, FX, FZF, 90); run([F2] * 18, FX, FZ0, 180)
put('site', 0, 0, 0, 0, st)
for x in (-14.0, -6.0, 6.0, 14.0): put('lamp_post', x, 0, 7.6, 0, st)
for x in (-10.0, -3.6, 3.6, 10.0): put('park_bench', x, 0, 7.2, 0, st)
put('bike_rack', 6.6, DY, 4.9, 0, st)
for z in np.arange(-28.0, 3.0, 3.0): put('bush', -18.7, 0, z, 0, st); put('bush', 18.7, 0, z, 0, st)
for x in np.arange(-16.5, 17.0, 3.0): put('bush', x, 0, -30.7, 0, st)
for x in (-8.0, -12.0, 8.0, 12.0, -16.0, 16.0): put('bush', x, 0, 6.2, 0, st)
for k, (x, z) in enumerate(((-21.5, -33.0), (21.5, -33.0), (-21.5, -14.0), (21.5, -14.0), (-21.5, 6.0), (21.5, 6.0), (0.0, -33.5))):
    put('tree' if k % 2 == 0 else 'tree_b', x, 0, z, 0, st)
put('player_scale_ref', 2.0, DY, 6.5); put('player_scale_ref', 1.0, Y0, 0.0, 0, ['bath']); put('player_scale_ref', -2.0, DY, -8.0, 0, pl)


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_height': CEIL,
                       'bathhouse': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floor': Y0, 'ceiling': Y0 + CEIL, 'wall_top': YW,
                                     'roof': {'type': 'hip', 'pitch_deg': PITCH, 'overhang': OV, 'ridge_x': [-RX, RX], 'ridge_underside': round(YR, 3)}},
                       'pool': {'x': [POOL[0], POOL[1]], 'z': [POOL[2], POOL[3]], 'deck': DY, 'water': WY, 'depth': [1.0, 3.6], 'lanes': LANES},
                       'fence': {'x': [-FX, FX], 'z': [FZ0, FZF]}, 'splash_pad': {'center': [SPL[0], SPL[1]], 'radius': SPL[2] + 0.2},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]}, 'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
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
