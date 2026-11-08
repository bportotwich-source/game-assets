"""Kit 57: campo de beisebol infantil de bairro, em ALTO DETALHE (scripts/detalhe).
Campo com diamante de 18,29 m, montinho do arremessador, bases, linhas de cal, saibro do infield, gramado listrado e pista de
alerta; alambrado de tela (backstop alto atras da base, cercas das laterais e cerca do outfield com faixas de pictogramas e
capa amarela), postes de falta, 2 bancos de reservas de bloco com telhado colorido, 3 arquibancadas de aluminio, cabine de 2
pavimentos (lanchonete e banheiros embaixo, cabine de transmissao em cima, escada externa, telhado de 4 aguas e mastro),
placar com lampadas, 4 torres de iluminacao, gaiola de rebatidas, galpao de equipamentos, estacionamento com carros genericos.
Arte original e sem texto (so pictogramas). Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
CAR_COLS = {'car_r': (172, 62, 56), 'car_b': (64, 100, 150), 'car_g': (86, 118, 84), 'car_y': (206, 176, 90), 'car_w': (222, 218, 206),
            'car_k': (48, 50, 54), 'car_s': (170, 174, 176), 'car_t': (92, 150, 146)}
configurar(cores=dict({'grass': (98, 150, 66), 'grass2': (84, 136, 56), 'grass_o': (116, 150, 78), 'clay': (186, 120, 80), 'track': (160, 112, 82),
                       'chalk': (246, 246, 240), 'concrete': (192, 188, 178), 'conc_s': (180, 176, 168), 'asphalt': (80, 82, 84), 'curb': (200, 198, 190),
                       'block': (206, 202, 192), 'block_p': (232, 226, 210), 'plaster': (238, 234, 224), 'ceil': (244, 242, 236), 'siding': (236, 230, 214),
                       'trim': (122, 40, 46), 'trim_w': (244, 240, 230), 'shingle': (128, 44, 48), 'shingle_c': (108, 36, 40), 'roof_b': (52, 86, 140), 'roof_r': (150, 48, 44),
                       'galv': (168, 174, 176), 'alu': (196, 200, 204), 'metal': (176, 180, 184), 'chrome': (212, 216, 220), 'steel': (120, 126, 132),
                       'steel_d': (56, 60, 64), 'iron': (40, 42, 44), 'paint_y': (236, 196, 50), 'paint_w': (240, 240, 234), 'paint_g': (40, 92, 62),
                       'pad_g': (34, 84, 58), 'pad_b': (40, 70, 120), 'pad_r': (150, 44, 44), 'pad_y': (226, 180, 50), 'pad_k': (40, 44, 48),
                       'board': (30, 64, 46), 'board_k': (28, 30, 32), 'seg_off': (52, 56, 54), 'seg_on': (255, 196, 90), 'lamp_r': (230, 70, 50), 'lamp_g': (90, 210, 100),
                       'wood': (176, 132, 88), 'dkwood': (110, 78, 54), 'bench_w': (168, 124, 80), 'door': (122, 40, 46), 'door_g': (40, 92, 62), 'frame': (232, 230, 222),
                       'glass': (150, 186, 204), 'mirror': (200, 214, 220), 'lamp_glass': (255, 238, 196), 'dark': (34, 34, 36), 'rubber': (30, 30, 32),
                       'counter': (214, 206, 188), 'ctop': (226, 222, 206), 'formica': (200, 70, 64), 'enamel': (240, 238, 232), 'porcelain': (244, 244, 240),
                       'tile_w': (236, 236, 230), 'tile_g': (150, 170, 160), 'vinyl_f': (196, 188, 170), 'vinyl': (70, 60, 56), 'vinyl_r': (170, 60, 56), 'vinyl_g': (70, 110, 80),
                       'fabric2': (90, 100, 120), 'cream': (240, 232, 214), 'paper': (236, 232, 220), 'net': (40, 44, 46), 'leather': (150, 92, 50), 'helmet_b': (40, 70, 130),
                       'helmet_r': (160, 44, 44), 'ball': (246, 244, 236), 'stitch': (200, 50, 50), 'cooler_o': (226, 120, 40), 'cooler_b': (60, 110, 170),
                       'food_r': (190, 60, 50), 'food_y': (230, 190, 70), 'food_g': (90, 140, 60), 'pop': (250, 236, 180), 'flag_r': (180, 50, 50), 'flag_b': (40, 60, 120),
                       'flag_w': (244, 244, 240), 'leaf': (86, 128, 62), 'leaf2': (108, 150, 70), 'bark': (120, 96, 72), 'plant': (70, 120, 60), 'pot': (230, 226, 214),
                       'brass': (196, 164, 90), 'gold': (210, 176, 90), 'line_w': (236, 236, 230), 'line_y': (226, 190, 70), 'player': (90, 140, 220),
                       'bench_g': (60, 100, 70), 'basket': (150, 110, 70), 'cart_w': (200, 200, 196), 'iron_r': (130, 70, 50), 'canvas': (60, 110, 80),
                       'mulch': (110, 84, 62), 'dirt': (150, 128, 98), 'tarp': (70, 90, 120), 'neon_r': (220, 60, 50), 'flag_o': (230, 140, 50)}, **CAR_COLS),
           texturas={'grass': 'render', 'grass2': 'render', 'grass_o': 'render', 'clay': 'render', 'track': 'render', 'concrete': 'render',
                     'conc_s': 'render', 'asphalt': 'render', 'curb': 'render', 'block': 'plaster', 'block_p': 'plaster', 'plaster': 'plaster', 'ceil': 'plaster',
                     'siding': 'paint', 'wood': 'planks', 'dkwood': 'planks', 'bench_w': 'planks', 'bark': 'render', 'mulch': 'render', 'dirt': 'render',
                     'shingle': 'render', 'shingle_c': 'render', 'vinyl_f': 'render'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4
for k in ('seg_on', 'lamp_r', 'lamp_g'): MATS[k].emissiveFactor = [c / 255 for c in D.COL[k]]

# ============================================================================ medidas
W = 2.0; T = 0.2; t_ = 0.1; GY = -0.3
BASE = 18.29; HB = BASE / math.sqrt(2)                          # diamante de 60 pes; meia diagonal 12,93
RUB = 14.02                                                      # distancia da base ao arremessador (46 pes)
RF = 55.0                                                        # raio da cerca do outfield (a partir da base)
OF = 8.0                                                         # afastamento das cercas laterais em relacao as linhas de falta
SQ2 = math.sqrt(2)
def lp(s, o, side=1):
    """Ponto (x, z) a s metros da base pela linha de falta (side 1 = 1a base, -1 = 3a) e o metros para fora."""
    return (side * (s + o) / SQ2, (o - s) / SQ2)
S_END = math.sqrt(RF ** 2 - OF ** 2)                             # cerca lateral encontra a do outfield
BSW = 1.0                                                        # inicio da cerca lateral (fim da asa do backstop)
BKZ = 7.6; BKX = 4.0                                             # painel do meio do backstop (25 pes atras da base)
DUG = (5.0, 12.0)                                                # trecho da cerca lateral ocupado pelo banco de reservas
DUGD = 2.6                                                       # fundo do banco de reservas
GATE_S = (13.2, 14.4)                                            # portao de pedestre nas cercas laterais
BLS = (15.0, 22.0)                                               # arquibancadas laterais (trecho em s, atras da cerca)
Y0 = 0.15; H = 3.0                                               # cabine: piso do terreo e altura do pavimento
BX, BZ = 3.0, 2.5                                                # cabine: meia largura (x local) e meio fundo (z local)
BC = (10.8, 12.8); BRY = -140.0                                  # centro da cabine e giro (frente local +Z olha a base)
PKZ = (18.5, 31.0); PKX = (-28.0, 28.0)                          # estacionamento
SX0, SX1, SZ0, SZ1 = -52.0, 52.0, -68.0, 34.0                    # terreno
DH = 2.1
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
def wc():
    """Vaso de louca com caixa acoplada e assento (pivo: face da parede, piso)."""
    p = Piece()
    lathe(p, 'porcelain', [(0.13, 0.0), (0.15, 0.1), (0.14, 0.28), (0.2, 0.4), (0.2, 0.42), (0.0, 0.42)], 0.0, 0.42, 0.0, 16)
    p.hull('porcelain', [(x * 0.17, y, z) for x in (-1, 1) for z in (0.15, 0.4) for y in (0.0, 0.42)])
    p.cham('porcelain', -0.2, 0.2, 0.42, 0.8, 0.0, 0.18, 0.03); p.cham('porcelain', -0.21, 0.21, 0.8, 0.83, -0.0, 0.19, 0.01)
    p.cham('dark', -0.19, 0.19, 0.42, 0.45, 0.2, 0.62, 0.03); p.box('chrome', 0.1, 0.16, 0.74, 0.76, 0.18, 0.2)
    return p
def urinal():
    p = Piece(); p.hull('porcelain', [(x, y, z) for x in (-0.2, 0.2) for (y, z) in ((0.45, 0.0), (0.45, 0.3), (1.05, 0.0), (1.05, 0.2))])
    p.box('dark', -0.12, 0.12, 0.6, 0.98, 0.2, 0.25) if False else None
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

# ============================================================================ moveis reaproveitados
def office_chair(mat='vinyl'):
    """Cadeira giratoria (pivo: centro, chao; encosto em -Z): base de 5 patas com rodizios, coluna, assento e encosto estofados."""
    p = Piece()
    for k in range(5):
        a = k * 2 * math.pi / 5; ex, ez = 0.3 * math.cos(a), 0.3 * math.sin(a)
        seg_cyl(p, 'steel_d', (0, 0.08, 0), (ex, 0.05, ez), 0.02, 6); p.sphere('dark', 0.03, ex, 0.03, ez, 1)
    p.cyl('chrome', 0.025, 0.08, 0.42, 0, 0, 10)
    p.cham(mat, -0.25, 0.25, 0.42, 0.5, -0.24, 0.24, 0.04)
    p.cham(mat, -0.23, 0.23, 0.58, 1.0, -0.3, -0.24, 0.03); p.box('steel_d', -0.03, 0.03, 0.44, 0.62, -0.26, -0.22)
    for s in (-1, 1): p.box('steel_d', s * 0.25 - 0.015, s * 0.25 + 0.015, 0.5, 0.66, -0.12, 0.12); p.cham('dark', s * 0.25 - 0.03, s * 0.25 + 0.03, 0.66, 0.69, -0.16, 0.12, 0.01)
    return p
def guest_chair(mat='vinyl'):
    """Cadeira de visita de tubo de aco com assento e encosto estofados (pivo: centro, chao; encosto em -Z)."""
    p = Piece()
    for s in (-1, 1):
        seg_cyl(p, 'chrome', (s * 0.22, 0.0, 0.2), (s * 0.22, 0.44, 0.2), 0.012, 6); seg_cyl(p, 'chrome', (s * 0.22, 0.0, 0.2), (s * 0.22, 0.0, -0.2), 0.012, 6)
        seg_cyl(p, 'chrome', (s * 0.22, 0.0, -0.2), (s * 0.22, 0.88, -0.22), 0.012, 6)
    p.cham(mat, -0.23, 0.23, 0.44, 0.5, -0.2, 0.22, 0.02); p.cham(mat, -0.22, 0.22, 0.55, 0.85, -0.25, -0.21, 0.02)
    return p
def sofa(n=3, mat='fabric2'):
    """Sofa de courvin de linhas retas (pivo: centro de tras, chao; assento para +Z) com pes cromados."""
    p = Piece(); L1 = 0.62 * n + 0.3; x = L1 / 2
    p.cham(mat, -x, x, 0.12, 0.42, 0.0, 0.82, 0.03); p.cham(mat, -x, x, 0.42, 0.85, 0.0, 0.2, 0.03)
    for s in (-1, 1): p.cham(mat, *sorted((s * x, s * (x - 0.15))), 0.42, 0.62, 0.0, 0.82, 0.03)
    for i in range(n):
        a = -x + 0.15 + i * 0.62 + 0.01; b = a + 0.6; p.cham(mat, a, b, 0.42, 0.52, 0.2, 0.8, 0.04); p.cham(mat, a, b, 0.52, 0.82, 0.2, 0.32, 0.04)
    for (a, c) in ((-x + 0.08, 0.08), (x - 0.08, 0.08), (-x + 0.08, 0.74), (x - 0.08, 0.74)): p.cyl('chrome', 0.025, 0.0, 0.12, a, c, 8)
    return p
def plant(h=1.4):
    """Vaso de planta (pivo: centro, chao): vaso de ceramica e folhas em leque."""
    p = Piece(); lathe(p, 'pot', [(0.18, 0.0), (0.24, 0.45), (0.25, 0.47), (0.0, 0.47)], sec=16); p.cyl('dark', 0.22, 0.45, 0.46, 0, 0, 16)
    rng = np.random.default_rng(5)
    for k in range(9):
        a = k * 2 * math.pi / 9 + rng.uniform(-0.2, 0.2); r = rng.uniform(0.25, 0.5); yy = rng.uniform(h * 0.6, h)
        seg_cyl(p, 'plant', (0, 0.46, 0), (r * math.cos(a), yy, r * math.sin(a)), 0.012, 4)
        c = np.array([r * math.cos(a), yy, r * math.sin(a)]); u = np.array([math.cos(a), 0.2, math.sin(a)]); u /= np.linalg.norm(u); v = np.array([-math.sin(a), 0, math.cos(a)])
        p.hull('plant', [c - 0.35 * u, c + 0.05 * u + 0.09 * v, c + 0.05 * u - 0.09 * v, c + 0.25 * u, c - 0.1 * u + 0.01 * np.array([0, 1, 0])])
    return p
def trash_can():
    p = Piece(); lathe(p, 'steel_d', [(0.26, 0.0), (0.28, 0.9), (0.0, 0.9)], sec=20)
    for y in (0.15, 0.75): ring_y(p, 'steel', 0.28, 0.29, y, y + 0.04, 0, 0, 20)
    lathe(p, 'steel_d', [(0.3, 0.9), (0.3, 0.96), (0.2, 1.02), (0.0, 1.03)], sec=20); return p
def tree(h=6.0, r=1.9, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.18, -0.2), (0.13, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('leaf', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('leaf2', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
# ============================================================================ moveis e postes (do kit 48)
def counter_k(L1=5.5):
    """Balcao de atendimento (pivo: face da parede, piso; balcao para +Z): corpo de madeira, tampo, prateleira e copos."""
    p = Piece(); x = L1 / 2
    p.cham('dkwood', -x, x, 0.0, 0.88, 0.0, 0.55, 0.01); p.cham('wood', -x - 0.02, x + 0.02, 0.88, 0.92, 0.0, 0.6, 0.006)
    p.box('dark', -x + 0.04, x - 0.04, 0.0, 0.1, 0.55, 0.56)
    for xx in np.arange(-x + 0.6, x - 0.3, 0.9): p.box('wood', xx - 0.01, xx + 0.01, 0.12, 0.84, 0.55, 0.565)
    return p
def register():
    p = Piece(); p.hull('dark', [(x, y, z) for x in (-0.2, 0.2) for (y, z) in ((0.0, -0.2), (0.0, 0.22), (0.08, 0.22), (0.16, -0.2))])
    p.cham('steel', -0.16, 0.16, 0.16, 0.2, -0.2, -0.04, 0.005)
    for i in range(4):
        for j in range(3): p.box('paper', -0.12 + i * 0.06, -0.08 + i * 0.06, 0.08 + j * 0.024 + 0.005, 0.088 + j * 0.024 + 0.008, 0.12 - j * 0.07, 0.16 - j * 0.07) if False else p.box('paper', -0.12 + i * 0.06, -0.08 + i * 0.06, 0.1 + (2 - j) * 0.02, 0.112 + (2 - j) * 0.02, 0.02 + j * 0.06, 0.06 + j * 0.06)
    p.hull('dark', [(x, y, z) for x in (-0.1, 0.1) for (y, z) in ((0.15, -0.12), (0.15, -0.18), (0.3, -0.16), (0.3, -0.2))])
    p.box('food_g', -0.08, 0.08, 0.22, 0.28, -0.162, -0.155)
    return p
def fridge():
    """Geladeira de bebidas com porta de vidro e prateleiras de garrafas (pivo: centro de tras, piso; porta +Z)."""
    p = Piece(); p.cham('cart_w', -0.4, 0.4, 0.0, 1.95, 0.0, 0.7, 0.012)
    p.box('frame', -0.38, 0.38, 0.1, 1.75, 0.7, 0.73); p.box('glass', -0.34, 0.34, 0.14, 1.71, 0.73, 0.736)
    p.box('dark', -0.34, 0.34, 0.14, 1.71, 0.69, 0.7)
    for k, y in enumerate((0.25, 0.65, 1.05, 1.45)):
        p.box('steel', -0.33, 0.33, y - 0.01, y, 0.1, 0.68)
        for i, x in enumerate(np.linspace(-0.28, 0.28, 7)): p.cyl(['flag_r', 'food_g', 'food_y', 'flag_b'][(i + k) % 4], 0.03, y, y + 0.24, x, 0.55, 10)
    p.box('flag_b', -0.4, 0.4, 1.78, 1.92, 0.7, 0.715); p.box('chrome', 0.33, 0.36, 0.7, 1.2, 0.736, 0.77)
    return p
def shelves(L1=1.6):
    """Estante de aco com caixas e embalagens sem texto (pivo: centro de tras, piso)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(11)
    for s in (-1, 1):
        for z in (0.02, 0.38): p.box('steel', s * x - 0.02 * (s > 0) * 2 + (0 if s > 0 else 0), s * x + (0.0 if s > 0 else 0.04), 0.0, 1.9, z, z + 0.03) if False else p.box('steel', *sorted((s * x, s * (x - 0.03))), 0.0, 1.9, z, z + 0.03)
    for y in (0.1, 0.55, 1.0, 1.45, 1.88):
        p.box('metal', -x + 0.03, x - 0.03, y, y + 0.02, 0.02, 0.41)
        if y > 1.8: continue
        xx = -x + 0.08
        while xx < x - 0.25:
            w = rng.uniform(0.18, 0.32); h = rng.uniform(0.18, 0.36); m = ['basket', 'paper', 'food_r', 'food_y', 'cart_w'][int(rng.integers(5))]
            p.cham(m, xx, xx + w, y + 0.02, y + 0.02 + h, 0.06, 0.38, 0.006); xx += w + 0.03
    return p

def park_bench(L1=1.8):
    """Banco de praca: 2 pes de ferro fundido em curva, assento e encosto de 6 ripas pintadas (pivo: centro, chao; senta-se de frente para +Z)."""
    p = Piece(); x = L1 / 2 - 0.12
    for s in (-1, 1):
        xx = s * x
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.0, 0.22), (0.0, 0.28), (0.42, 0.2), (0.42, 0.16))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.0, -0.24), (0.0, -0.3), (0.42, -0.2), (0.42, -0.14))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.4, -0.24), (0.44, -0.24), (0.4, 0.24), (0.44, 0.24))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.42, -0.2), (0.42, -0.26), (0.86, -0.34), (0.86, -0.29))])
        p.hull('iron', [(xx + d, y, z) for d in (-0.025, 0.025) for (y, z) in ((0.62, -0.26), (0.66, -0.26), (0.66, 0.22), (0.62, 0.22))])
        p.sphere('iron', 0.035, xx, 0.66, 0.24, 1)
    for k in range(4):
        z0 = -0.22 + k * 0.115; p.cham('bench_g', -L1 / 2, L1 / 2, 0.44, 0.475, z0, z0 + 0.095, 0.006)
    for k in range(3):
        t0 = 0.48 + k * 0.13; z0 = -0.22 - (t0 - 0.42) * 0.27; y0 = t0
        p.hull('bench_g', [(xx, y0 + dy, z0 - dy * 0.27 + dz) for xx in (-L1 / 2, L1 / 2) for dy in (0.0, 0.1) for dz in (-0.035, 0.0)])
    return p
def lamp_post(h=3.8):
    """Poste de lanterna de ferro: base moldada, fuste canelado, braco com volutas e lanterna de 4 vidros (pivo: centro, chao)."""
    p = Piece()
    lathe(p, 'iron', [(0.18, 0.0), (0.18, 0.12), (0.14, 0.16), (0.14, 0.45), (0.1, 0.55), (0.08, 0.62)], sec=16)
    for k in range(8):
        a = k * math.pi / 4; p.box('iron', 0, 0, 0, 0, 0, 0) if False else seg_cyl(p, 'iron', (0.062 * math.cos(a), 0.62, 0.062 * math.sin(a)), (0.05 * math.cos(a), h - 0.5, 0.05 * math.sin(a)), 0.018, 6)
    p.cyl('iron', 0.05, 0.62, h - 0.5, 0, 0, 12)
    lathe(p, 'iron', [(0.06, h - 0.5), (0.1, h - 0.44), (0.07, h - 0.38), (0.12, h - 0.34)], sec=16)
    yb = h - 0.34
    p.hull('iron', [(x, yb, z) for x in (-0.17, 0.17) for z in (-0.17, 0.17)] + [(x, yb + 0.05, z) for x in (-0.15, 0.15) for z in (-0.15, 0.15)])
    p.box('lamp_glass', -0.13, 0.13, yb + 0.05, yb + 0.48, -0.13, 0.13)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('iron', sx * 0.14 - 0.015, sx * 0.14 + 0.015, yb + 0.05, yb + 0.5, sz * 0.14 - 0.015, sz * 0.14 + 0.015)
    p.hull('iron', [(x, yb + 0.5, z) for x in (-0.22, 0.22) for z in (-0.22, 0.22)] + [(0, yb + 0.78, 0)]); p.sphere('iron', 0.04, 0, yb + 0.8, 0, 1)
    return p
# ============================================================================ carros genericos dos anos 70/80 (do kit 47; pivo: meio entre os eixos, chao; frente +Z)
CAR_SPEC = {
    'sedan':  dict(zf=2.42, zr=-2.42, wf=1.38, wr=-1.38, cab=(0.78, -1.5, 0.05, -1.05), top=1.38),
    'wagon':  dict(zf=2.42, zr=-2.48, wf=1.38, wr=-1.4, cab=(0.78, -2.4, 0.05, -2.3), top=1.4),
    'coupe':  dict(zf=2.35, zr=-2.3, wf=1.3, wr=-1.3, cab=(0.7, -1.7, -0.05, -0.85), top=1.3),
    'hatch':  dict(zf=1.92, zr=-1.86, wf=1.15, wr=-1.15, cab=(0.5, -1.78, -0.15, -1.55), top=1.36),
    'pickup': dict(zf=2.5, zr=-2.5, wf=1.6, wr=-1.5, cab=(0.92, -0.56, 0.3, -0.52), top=1.55, bed=-0.62)}
def car(mat='car_r', kind='sedan', tag=False, bumper='chrome', wheels=True):
    """Carro generico de linhas retas (anos 70/80, sem marca): carroceria em 2 faixas com caixas de roda, cabine de vidro com
    colunas, teto, para-choques, grade, farois retangulares, piscas, lanternas, placas lisas, frisos, macanetas, retrovisores,
    limpadores, bancos e painel por dentro, rodas com calota. tag = cartao de preco sem texto no painel e adesivo no vidro."""
    S = CAR_SPEC[kind]; zf, zr, wf, wr = S['zf'], S['zr'], S['wf'], S['wr']; cf, cr, tf, trr = S['cab']; top = S['top']
    p = Piece(); hw = 0.88; yb = 0.3; ym = 0.7; yh = 0.9; ar = 0.42
    # faixa de baixo (entre as caixas de roda)
    for (z0, z1, front) in ((wf + ar, zf, 1), (wr + ar, wf - ar, 0), (zr, wr - ar, -1)):
        if front == 1: pr = [(yb, z0), (ym, z0), (ym, z1), (0.42, z1), (0.34, z1 - 0.05)]
        elif front == -1: pr = [(yb, z1), (ym, z1), (ym, z0), (0.42, z0), (0.34, z0 + 0.05)]
        else: pr = [(yb, z0), (ym, z0), (ym, z1), (yb, z1)]
        p.hull(mat, [(x, y, z) for x in (-hw, hw) for (y, z) in pr])
    for wz in (wf, wr): p.box('rubber', -hw + 0.3, hw - 0.3, 0.32, ym, wz - ar, wz + ar)
    # faixa de cima
    bed = S.get('bed')
    zre = bed if bed is not None else zr
    up = [(ym, zf), (ym, zre), (yh - (0.0 if bed is not None else 0.16), zre), (yh, zre + (0.0 if bed is not None else 0.15)), (yh, cf), (yh - 0.04, zf - 0.15)]
    p.hull(mat, [(x, y, z) for x in (-hw, hw) for (y, z) in up])
    if bed is not None:
        p.box('dark', -hw + 0.06, hw - 0.06, ym, ym + 0.04, zr + 0.06, bed - 0.06)
        for s in (-1, 1): p.box(mat, *sorted((s * hw, s * (hw - 0.06))), ym, 1.02, zr, bed)
        p.box(mat, -hw + 0.06, hw - 0.06, ym, 1.02, bed - 0.06, bed); p.box(mat, -hw + 0.06, hw - 0.06, ym + 0.04, 1.0, zr, zr + 0.06)
        for s in (-1, 1): p.box('chrome', *sorted((s * (hw - 0.07), s * (hw + 0.005))), 1.02, 1.035, zr + 0.05, bed - 0.03)
        p.box('chrome', -0.12, 0.12, 0.88, 0.92, zr - 0.012, zr)
    # cabine de vidro, teto e colunas
    gw0, gw1 = 0.82, 0.72
    p.hull('glass', [(s * gw0, yh, z) for s in (-1, 1) for z in (cf, cr)] + [(s * gw1, top, z) for s in (-1, 1) for z in (tf, trr)])
    p.hull(mat, [(s * (gw1 + 0.015), y, z) for s in (-1, 1) for y in (top - 0.012, top + 0.04) for z in (tf - 0.03, trr + 0.03)])
    def pil(zb, zt, wb=0.1, wt=0.08):
        pts = []
        for s in (-1, 1):
            for (w, y, z, ww) in ((gw0 + 0.012, yh + 0.005, zb, wb), (gw1 + 0.012, top - 0.005, zt, wt)):
                for dz in (-ww / 2, ww / 2):
                    for dx in (0.0, 0.025): pts.append((s * (w + dx), y, z + dz))
        return pts
    for s in (-1, 1):
        for (zb, zt, wb, wt) in ((cf - 0.05, tf + 0.02, 0.08, 0.06), ((cf + cr) / 2 + 0.1, (tf + trr) / 2 + 0.05, 0.12, 0.1), (cr + 0.08, trr - 0.03, 0.18, 0.12)):
            p.hull(mat, [pt for pt in pil(zb, zt, wb, wt) if np.sign(pt[0]) == s])
    # para-choques, grade, farois e lanternas
    bm = bumper
    p.cham(bm, -hw - 0.02, hw + 0.02, 0.3, 0.46, zf - 0.03, zf + 0.12, 0.025); p.cham(bm, -hw - 0.02, hw + 0.02, 0.3, 0.46, zr - 0.12, zr + 0.03, 0.025)
    for z0 in (zf + 0.12, zr - 0.13): p.box('paint_w', -0.2, 0.2, 0.32, 0.44, z0, z0 + 0.01)
    p.box('chrome', -0.56, 0.56, 0.48, 0.69, zf, zf + 0.008); p.box('dark', -0.53, 0.53, 0.5, 0.67, zf + 0.002, zf + 0.012)
    for k in range(3): p.box('chrome', -0.53, 0.53, 0.535 + k * 0.045, 0.545 + k * 0.045, zf + 0.004, zf + 0.016)
    for s in (-1, 1):
        a, b = sorted((s * 0.58, s * 0.84)); p.box('chrome', a, b, 0.5, 0.68, zf, zf + 0.008); p.box('lamp_glass', a + 0.02 * s * s, b - 0.02, 0.53, 0.65, zf + 0.002, zf + 0.014)
        a, b = sorted((s * 0.6, s * 0.82)); p.box('flag_o', a, b, 0.465, 0.495, zf, zf + 0.01)
        a, b = sorted((s * 0.45, s * 0.84)); p.box('chrome', a, b, 0.5, 0.69, zr - 0.008, zr); p.box('neon_r', a + 0.02, b - 0.02, 0.53, 0.66, zr - 0.014, zr - 0.002)
        a, b = sorted((s * 0.62, s * 0.7)); p.box('paint_w', a, b, 0.54, 0.65, zr - 0.016, zr - 0.012)
    # frisos, emendas de porta, macanetas, retrovisores
    for s in (-1, 1):
        xa, xb = sorted((s * hw, s * (hw + 0.006)))
        for (z0, z1) in ((wr + ar + 0.04, wf - ar - 0.04), (wf + ar + 0.04, zf - 0.1), (zr + 0.1, wr - ar - 0.04)):
            if z1 - z0 > 0.05: p.box('chrome', xa + 0.001 * s * 0 , xb, 0.6, 0.625, z0, z1) if False else p.box('chrome', *sorted((s * (hw + 0.001), s * (hw + 0.007))), 0.6, 0.625, z0, z1)
        seams = [cf - 0.08, (cf + cr) / 2 + 0.1] + ([cr + 0.1] if kind in ('sedan', 'wagon') else [])
        for zz in seams:
            arch = abs(zz - wf) < ar + 0.02 or abs(zz - wr) < ar + 0.02
            if not arch: p.box('dark', *sorted((s * hw, s * (hw + 0.003))), yb + 0.06, 0.575, zz - 0.006, zz + 0.006)
            p.box('dark', *sorted((s * hw, s * (hw + 0.003))), 0.71 if arch else 0.65, yh - 0.02, zz - 0.006, zz + 0.006)
        for zz in seams[1:] + ([cr + 0.1 - 0.0] if False else []):
            p.box('chrome', *sorted((s * hw, s * (hw + 0.02))), 0.76, 0.79, zz - 0.2, zz - 0.06)
        p.cham(mat, *sorted((s * 0.8, s * 1.0)), yh + 0.02, yh + 0.13, cf - 0.18, cf - 0.08, 0.015); p.box('mirror', *sorted((s * 0.86, s * 0.99)), yh + 0.035, yh + 0.115, cf - 0.181, cf - 0.18 + 0.0)
    # limpadores, antena, escapamento
    for x in (-0.35, 0.25): seg_cyl(p, 'dark', (x, yh + 0.012, cf + 0.03), (x + 0.4, yh + 0.07, cf - 0.08), 0.008, 4)
    seg_cyl(p, 'chrome', (0.75, ym + 0.15, wf + 0.6), (0.72, 1.6, wf + 0.4), 0.004, 4)
    disc_z(p, 'steel', 0.035, zr - 0.15, zr + 0.3, 0.45, 0.25, 10)
    # bancos e painel (dentro)
    yi = yh + 0.006
    p.cham('dark', -0.74, 0.74, yi, yi + 0.1, cf - 0.5, cf - 0.22, 0.03)
    m = trimesh.creation.torus(major_radius=0.17, minor_radius=0.018, major_sections=20, minor_sections=6)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-25), [1, 0, 0])); m.apply_translation([-0.4, yi + 0.18, cf - 0.62]); p.add('dark', m)
    sb = cr + 0.22 if kind == 'pickup' else (cf + cr) / 2 if kind == 'coupe' else cf - 1.1
    for s in (-1, 1): p.cham('vinyl', *sorted((s * 0.12, s * 0.68)), yi, yi + 0.32, sb - 0.12, sb, 0.04); p.cham('vinyl', *sorted((s * 0.25, s * 0.55)), yi + 0.335, top - 0.07, sb - 0.1, sb - 0.02, 0.03)
    if kind in ('sedan', 'wagon', 'hatch'):
        zb_ = cr + (0.55 if kind == 'sedan' else 0.3 if kind == 'hatch' else 0.9)
        p.cham('vinyl', -0.7, 0.7, yi, yi + 0.28, zb_ - 0.12, zb_, 0.04)
    if tag:
        p.box('paper', 0.12, 0.42, yi + 0.11, yi + 0.22, cf - 0.51, cf - 0.5); p.box('flag_r', 0.15, 0.39, yi + 0.18, yi + 0.21, cf - 0.5, cf - 0.497)
        p.box('dark', 0.17, 0.37, yi + 0.13, yi + 0.16, cf - 0.5, cf - 0.497)
    # rodas
    for wz in ((wf, wr) if wheels else ()):
        for s in (-1, 1):
            disc_x(p, 'rubber', 0.32, *sorted((s * (hw - 0.27), s * (hw - 0.04))), 0.32, wz, 28)
            disc_x(p, 'chrome', 0.19, *sorted((s * (hw - 0.05), s * (hw - 0.03))), 0.32, wz, 20)
            disc_x(p, 'steel', 0.07, *sorted((s * (hw - 0.03), s * (hw - 0.02))), 0.32, wz, 12)
            for k in range(6):
                a = k * math.pi / 3; p.box('dark', *sorted((s * (hw - 0.034), s * (hw - 0.026))), 0.32 + 0.13 * math.sin(a) - 0.015, 0.32 + 0.13 * math.sin(a) + 0.015, wz + 0.13 * math.cos(a) - 0.015, wz + 0.13 * math.cos(a) + 0.015)
    return p
def picto_car(p, mat, cx, cy, s, z0, z1):
    """Silhueta de carro de perfil no plano x-y, extrudada de z0 a z1 (s = comprimento)."""
    body = Polygon([(cx - 0.5 * s, cy - 0.12 * s), (cx + 0.5 * s, cy - 0.12 * s), (cx + 0.5 * s, cy + 0.02 * s), (cx + 0.3 * s, cy + 0.06 * s),
                    (cx + 0.16 * s, cy + 0.24 * s), (cx - 0.22 * s, cy + 0.24 * s), (cx - 0.36 * s, cy + 0.06 * s), (cx - 0.5 * s, cy + 0.03 * s)])
    win = unary_union([Polygon([(cx + 0.13 * s, cy + 0.08 * s), (cx + 0.02 * s, cy + 0.08 * s), (cx + 0.02 * s, cy + 0.2 * s), (cx + 0.1 * s, cy + 0.2 * s)]),
                       Polygon([(cx - 0.03 * s, cy + 0.08 * s), (cx - 0.3 * s, cy + 0.08 * s), (cx - 0.19 * s, cy + 0.2 * s), (cx - 0.03 * s, cy + 0.2 * s)])])
    wh = unary_union([Point(cx + x * s, cy - 0.12 * s).buffer(0.11 * s, 16) for x in (-0.3, 0.3)])
    shape = body.difference(win).difference(unary_union([Point(cx + x * s, cy - 0.12 * s).buffer(0.135 * s, 16) for x in (-0.3, 0.3)])).union(wh)
    ext(p, mat, shape.buffer(0), z0, z1)
def picto_wrench(p, mat, cx, cy, s, z0, z1):
    head = Point(cx + 0.3 * s, cy + 0.3 * s).buffer(0.2 * s, 20).difference(sbox(cx + 0.27 * s, cy + 0.27 * s, cx + 0.6 * s, cy + 0.6 * s))
    from shapely import affinity
    handle = affinity.rotate(sbox(cx - 0.06 * s, cy - 0.45 * s, cx + 0.06 * s, cy + 0.2 * s), 45, origin=(cx, cy))
    ext(p, mat, unary_union([head, handle, Point(cx - 0.3 * s, cy - 0.3 * s).buffer(0.1 * s, 16)]).buffer(0), z0, z1)
# ============================================================================ paredes (do kit 56)
def wall2(p, axis, u0, u1, vo, vi, holes, ya, yb, out='block_p', inn='plaster', split=0.5):
    """Parede de 2 camadas com vaos (a, b, y0, y1). axis 'x': corre em X, espessura em Z de vo (face externa) a vi; 'z': corre em Z."""
    vm = vo + (vi - vo) * split
    us = sorted(set([u0, u1] + [h for q in holes for h in q[:2] if u0 < h < u1]))
    ys = sorted(set([ya, yb] + [h for q in holes for h in q[2:4] if ya < h < yb]))
    vs = sorted([vo, vm, vi]); outer_first = vo < vi
    def cell(i, j, k):
        cu = (us[i] + us[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for q in holes:
            if q[0] < cu < q[1] and q[2] < cy < q[3]: return None
        return (out if k == 0 else inn) if outer_first else (inn if k == 0 else out)
    for m, mesh in grid_solid(us, ys, vs, cell).items():
        if axis == 'z':
            v = mesh.vertices.copy(); mesh.vertices = np.stack([v[:, 2], v[:, 1], v[:, 0]], 1); mesh.invert()
        p.add(m, mesh)
def wall_grid(p, axis, u0, u1, v0, v1, holes, ya, yb, mat='plaster'):
    wall2(p, axis, u0, u1, v0, v1, holes, ya, yb, mat, mat)
def polys(g): return [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon' and q.area > 1e-5]

# ============================================================================ geometria do campo (no plano x-z; a base fica na origem)
def wedge(r, a0, a1, n=72, c=(0.0, 0.0)):
    return Polygon([c] + [(c[0] + r * math.sin(math.radians(a)), c[1] - r * math.cos(math.radians(a))) for a in np.linspace(a0, a1, n)])
B1, B2, B3 = (HB, -HB), (0.0, -2 * HB), (-HB, -HB)
P_END1 = lp(S_END, OF, 1); A_END = math.degrees(math.atan2(P_END1[0], -P_END1[1]))     # canto cerca lateral x outfield (53,4 graus)
FENCE_PTS = ([(-BKX, BKZ), (BKX, BKZ), lp(BSW, OF, 1), P_END1]
             + [(RF * math.sin(math.radians(a)), -RF * math.cos(math.radians(a))) for a in np.linspace(A_END, -A_END, 42)[1:-1]]
             + [lp(S_END, OF, -1), lp(BSW, OF, -1)])
FENCED = Polygon(FENCE_PTS)
FAIR = wedge(RF + 5, -45, 45)
HOME_C = Point(0, 0).buffer(4.0, 48); MOUND_C = Point(0, -RUB).buffer(3.0, 48)
DIAMOND = Polygon([(0, 0), B1, B2, B3])
IN_GRASS = DIAMOND.buffer(-1.15, join_style=2).difference(HOME_C).difference(MOUND_C)
ARC = Point(0, -RUB).buffer(15.24, 96).intersection(wedge(30, -47, 47))
PATHS = unary_union([LineString([(0, 0), B1]).buffer(0.9, cap_style=2), LineString([(0, 0), B3]).buffer(0.9, cap_style=2)])
TRACK = FENCED.difference(FENCED.buffer(-3.0, join_style=2))
CLAY = unary_union([ARC, HOME_C, MOUND_C, PATHS]).intersection(FENCED).difference(IN_GRASS).difference(TRACK)
GRASS = FENCED.difference(CLAY).difference(TRACK)
def side_strip(side, s0, s1, o0, o1): return Polygon([lp(s0, o0, side), lp(s1, o0, side), lp(s1, o1, side), lp(s0, o1, side)])
PLAZA = unary_union([sbox(-24.0, 1.0, 24.0, 18.0)] + [side_strip(sd, -3.0, 26.0, OF, OF + 7.5) for sd in (1, -1)]).difference(FENCED)
PARK = unary_union([sbox(PKX[0], 18.3, PKX[1], PKZ[1]), sbox(SX0, PKZ[1], SX1, SZ1)])
CURB = sbox(PKX[0], 18.0, PKX[1], 18.3)
CAGE = (-35.2, -31.0, -14.0, 3.0)                                # gaiola de rebatidas (x0, x1, z0, z1)
SHED = (-27.0, 7.0)                                              # galpao (centro)
SHED_PAD = sbox(SHED[0] - 2.6, SHED[1] - 2.0, SHED[0] + 2.6, SHED[1] + 2.6)
CAGE_PATH = sbox(CAGE[0] + 0.6, CAGE[3], CAGE[1] - 0.6, 12.0)
OUTER = sbox(SX0, SZ0, SX1, SZ1).difference(FENCED).difference(PLAZA).difference(PARK).difference(CURB).difference(SHED_PAD).difference(CAGE_PATH)

def field():
    """Campo: gramado listrado (faixas de 4 m alternando 2 verdes), saibro do infield (arco, circulo da base, montinho e caminhos
    das bases) e pista de alerta junto a cerca. Tudo com topo em y = 0."""
    p = Piece()
    stripes = unary_union([sbox(x, SZ0, x + 4.0, SZ1) for x in np.arange(-60.0, 60.0, 8.0)])
    ext_y(p, 'grass', GRASS.intersection(stripes), GY, 0.0); ext_y(p, 'grass2', GRASS.difference(stripes), GY, 0.0)
    ext_y(p, 'clay', CLAY, GY, 0.0); ext_y(p, 'track', TRACK, GY, 0.0)
    return p
def site():
    """Terreno fora da cerca: gramado, praca de concreto com juntas (atras do backstop e ao longo das laterais), guia, estacionamento
    e rua de asfalto com vagas pintadas, faixa amarela e batentes; base do galpao e caminho da gaiola."""
    p = Piece()
    ext_y(p, 'grass_o', OUTER, GY, 0.0)
    p.merge(paving(PLAZA, 0.0, 2.0, 'concrete')); p.merge(paving(SHED_PAD, 0.0, 1.3, 'conc_s')); p.merge(paving(CAGE_PATH, 0.0, 1.2, 'conc_s'))
    ext_y(p, 'curb', CURB, GY, 0.12)
    ext_y(p, 'asphalt', PARK, GY, -0.03)
    for k in range(21):
        x = PKX[0] + 0.3 + k * 2.7; ext_y(p, 'line_w', sbox(x - 0.05, 18.6, x + 0.05, 23.8), -0.03, -0.027)
    for x in np.arange(SX0 + 1.0, SX1 - 2.0, 4.0): ext_y(p, 'line_y', sbox(x, 32.4, x + 2.0, 32.52), -0.03, -0.027)
    ext_y(p, 'line_w', sbox(PKX[0], 30.85, PKX[1], 30.95), -0.03, -0.027)
    return p
def chalk():
    """Linhas de cal: linhas de falta ate a cerca, caixas do rebatedor e do receptor, caixas dos tecnicos, circulos de espera."""
    p = Piece(); w = 0.04; y1 = 0.004; G = []
    for sd in (1, -1):
        a = (sd * 0.3, -0.3); b = (sd * (RF - 0.3) / SQ2, -(RF - 0.3) / SQ2)
        G.append(LineString([a, b]).buffer(w, cap_style=2))
    def outline(x0, z0, x1, z1): return sbox(x0 - w, z0 - w, x1 + w, z1 + w).difference(sbox(x0 + w, z0 + w, x1 - w, z1 - w))
    for sd in (1, -1): a_, b_ = sorted((sd * 0.3, sd * 1.2)); G.append(outline(a_, -1.1, b_, 0.7))            # caixas do rebatedor
    G.append(outline(-0.6, 0.9, 0.6, 2.6).difference(sbox(-0.5, 0.8, 0.5, 0.95)))               # caixa do receptor
    for sd in (1, -1):
        c = lp(HB, 4.0, sd); bx = Polygon([(c[0] - 1.2, c[1] - 1.2), (c[0] + 1.2, c[1] - 1.2), (c[0] + 1.2, c[1] + 1.2), (c[0] - 1.2, c[1] + 1.2)])
        bx = affinity.rotate(bx, 45, origin=c); G.append(bx.exterior.buffer(w, join_style=2).intersection(bx.buffer(w, join_style=2)))
        oc = Point(lp(4.5, 5.0, sd)); G.append(oc.buffer(0.78, 40).difference(oc.buffer(0.7, 40)))
    ext_y(p, 'chalk', unary_union(G).difference(Point(0, -0.2).buffer(0.36, 24)), 0.0, y1)
    return p
def home_plate():
    """Base do batedor: pentagono de borracha branca com borda chanfrada, enterrado no saibro (pivo: ponta de tras)."""
    p = Piece(); poly = Polygon([(0.0, 0.0), (0.216, -0.216), (0.216, -0.432), (-0.216, -0.432), (-0.216, -0.216)])
    ext_y(p, 'rubber', poly, -0.05, 0.004); ext_y(p, 'paint_w', poly.buffer(-0.012, join_style=2), 0.004, 0.012)
    return p
def base_bag():
    """Base de lona (38 cm) estofada com cantos arredondados, fita e pino de ancoragem (pivo: centro, chao)."""
    p = Piece(); s = 0.19
    p.cham('paint_w', -s, s, 0.0, 0.07, -s, s, 0.025); p.cham('paint_w', -s + 0.01, s - 0.01, 0.07, 0.08, -s + 0.01, s - 0.01, 0.006)
    for x in (-0.14, 0.14): p.box('steel', x - 0.01, x + 0.01, 0.0, 0.074, -s - 0.003, s + 0.003)
    p.cyl('steel', 0.03, -0.25, 0.0, 0, 0, 10)
    return p
def mound():
    """Montinho do arremessador: cone baixo de saibro com topo plano, placa de borracha e saco de breu (pivo: centro da placa, chao)."""
    p = Piece()
    lathe(p, 'clay', [(1.6, 0.0), (1.2, 0.06), (0.8, 0.12), (0.55, 0.15), (0.0, 0.15)], z=0.4, sec=40)
    p.box('paint_w', -0.23, 0.23, 0.1, 0.158, -0.05, 0.05)
    p.cham('paper', 0.6, 0.72, 0.15 - 0.02, 0.18, 0.5, 0.6, 0.02)
    return p
def on_deck_mat():
    """Tapete de espera com 2 tacos de peso apoiados (pivo: centro)."""
    p = Piece(); disc = Point(0, 0).buffer(0.66, 32); ext_y(p, 'grass2', disc, 0.004, 0.018)
    for a in (20.0, 40.0):
        q = Piece(); lathe(q, 'leather', [(0.03, 0.0), (0.035, 0.05), (0.02, 0.06), (0.012, 0.25), (0.03, 0.7), (0.033, 0.78), (0.0, 0.79)], sec=10)
        M = rot_y(a) @ trimesh.transformations.rotation_matrix(math.radians(88), [1, 0, 0]); M[:3, 3] = [0.0, 0.05, -0.3]; p.merge(q, M)
    return p
# ============================================================================ alambrado
def wires_mesh(segs, w, z0, z1):
    """Muitos arames retos (segmentos 2D (x, y) no plano da tela) como prismas finos de 4 faces laterais e tampas: uma malha so."""
    V = []; F = []
    for (a, b) in segs:
        a = np.array(a, float); b = np.array(b, float); d = b - a; Ln = np.linalg.norm(d)
        if Ln < 1e-4: continue
        n = np.array([-d[1], d[0]]) / Ln * (w / 2); k = len(V)
        for q in (a - n, a + n, b + n, b - n):
            V.append((q[0], q[1], z0)); V.append((q[0], q[1], z1))
        # 0..7: (a-n,z0),(a-n,z1),(a+n,z0),(a+n,z1),(b+n,z0),(b+n,z1),(b-n,z0),(b-n,z1)
        quads = [(0, 2, 4, 6), (1, 7, 5, 3), (0, 1, 3, 2), (2, 3, 5, 4), (4, 5, 7, 6), (6, 7, 1, 0)]
        for (i, j, l, m) in quads: F += [[k + i, k + j, k + l], [k + i, k + l, k + m]]
    m = trimesh.Trimesh(np.array(V), np.array(F), process=False)
    if m.volume < 0: m.invert()
    return m
def diag_segs(L1, y0, y1, pitch, sgn):
    """Arames a 45 graus que cobrem o retangulo [0, L1] x [y0, y1] (sgn = +1 sobe para a direita, -1 desce)."""
    h = y1 - y0; out = []
    for c in np.arange(-h + pitch / 2, L1, pitch):
        # reta x = c + sgn*(y - y0) (sgn=+1) ou x = c + (y1 - y) (sgn=-1), recortada
        xa, ya, xb, yb = c, y0, c + h, y1
        if xa < 0: ya += -xa; xa = 0.0
        if xb > L1: yb -= xb - L1; xb = L1
        if xb - xa < 0.01: continue
        if sgn > 0: out.append(((xa, ya), (xb, yb)))
        else: out.append(((L1 - xa, ya), (L1 - xb, yb)))
    return out
def chain(p, L1, y0, y1, pitch=0.1, mat='galv', w=0.0045):
    """Tela de alambrado (losangos de arame) no plano z = 0 da peca local, de x = 0 a L1; as 2 direcoes em camadas separadas."""
    p.add(mat, wires_mesh(diag_segs(L1, y0, y1, pitch, 1), w, -0.004, 0.0)); p.add(mat, wires_mesh(diag_segs(L1, y0, y1, pitch, -1), w, 0.0, 0.004))
def picto(p, kind, mat, cx, cy, s, z0, z1):
    """Pictogramas das faixas (sem texto): bola, taco, luva, estrela, bone, trofeu."""
    def disc(x, y, r, n=24):
        m = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=n); m.apply_translation([x, y, (z0 + z1) / 2]); p.add(mat, m)
    def bar(x0, y0, x1, y1, w):
        m = D._fix(trimesh.creation.extrude_polygon(LineString([(x0, y0), (x1, y1)]).buffer(w / 2, cap_style=1), z1 - z0)); m.apply_translation([0, 0, z0]); p.add(mat, m)
    if kind == 'ball':
        disc(cx, cy, 0.42 * s)
    elif kind == 'bat':
        bar(cx - 0.45 * s, cy - 0.35 * s, cx + 0.4 * s, cy + 0.3 * s, 0.09 * s); bar(cx - 0.1 * s, cy - 0.08 * s, cx + 0.42 * s, cy + 0.32 * s, 0.17 * s); disc(cx - 0.47 * s, cy - 0.37 * s, 0.07 * s, 12)
    elif kind == 'star':
        pts = [(cx + (0.45 if k % 2 == 0 else 0.19) * s * math.sin(k * math.pi / 5), cy + (0.45 if k % 2 == 0 else 0.19) * s * math.cos(k * math.pi / 5)) for k in range(10)]
        m = D._fix(trimesh.creation.extrude_polygon(Polygon(pts), z1 - z0)); m.apply_translation([0, 0, z0]); p.add(mat, m)
    elif kind == 'glove':
        g = unary_union([Point(cx, cy - 0.08 * s).buffer(0.3 * s, 24)] + [LineString([(cx + dx * s, cy), (cx + dx * 1.25 * s, cy + 0.38 * s)]).buffer(0.065 * s) for dx in (-0.2, -0.07, 0.06, 0.19)]
                        + [LineString([(cx - 0.25 * s, cy - 0.1 * s), (cx - 0.46 * s, cy + 0.12 * s)]).buffer(0.075 * s)])
        m = D._fix(trimesh.creation.extrude_polygon(g, z1 - z0)); m.apply_translation([0, 0, z0]); p.add(mat, m)
    elif kind == 'cap':
        g = unary_union([Point(cx, cy - 0.05 * s).buffer(0.3 * s, 24).intersection(sbox(cx - s, cy - 0.05 * s, cx + s, cy + s)), sbox(cx - 0.05 * s, cy - 0.12 * s, cx + 0.5 * s, cy - 0.04 * s)])
        m = D._fix(trimesh.creation.extrude_polygon(g, z1 - z0)); m.apply_translation([0, 0, z0]); p.add(mat, m)
    elif kind == 'cup':
        g = unary_union([Polygon([(cx - 0.25 * s, cy + 0.3 * s), (cx + 0.25 * s, cy + 0.3 * s), (cx + 0.12 * s, cy - 0.05 * s), (cx - 0.12 * s, cy - 0.05 * s)]),
                         sbox(cx - 0.04 * s, cy - 0.3 * s, cx + 0.04 * s, cy - 0.05 * s), sbox(cx - 0.18 * s, cy - 0.4 * s, cx + 0.18 * s, cy - 0.3 * s)])
        m = D._fix(trimesh.creation.extrude_polygon(g, z1 - z0)); m.apply_translation([0, 0, z0]); p.add(mat, m)
BANNERS = [('pad_b', 'ball'), ('pad_r', 'star'), ('pad_g', 'glove'), ('pad_y', 'bat'), ('pad_b', 'cap'), ('pad_r', 'cup')]
def fence_run(p, pts, h, step=2.5, cap=None, rails=(), banner_every=0, kick=0.0, inside=None, closed=False, pitch=0.1):
    """Cerca de alambrado ao longo da polilinha pts (x, z), com postes de tubo galvanizado, travessa no topo (ou capa amarela de
    espuma), travessas intermediarias, arame de tensao embaixo, chapa de rodape opcional e faixas com pictogramas do lado de dentro."""
    k_ban = 0
    segs = list(zip(pts[:-1], pts[1:]))
    for (a, b) in segs:
        dx, dz = b[0] - a[0], b[1] - a[1]; Ln = math.hypot(dx, dz); n = max(1, int(math.ceil(Ln / step - 1e-6))); l = Ln / n
        for i in range(n):
            x0, z0 = a[0] + dx * i / n, a[1] + dz * i / n; x1, z1 = a[0] + dx * (i + 1) / n, a[1] + dz * (i + 1) / n
            q = Piece(); chain(q, l, 0.05 + kick, h - 0.03, pitch)
            seg_cyl(q, 'galv', (0.0, 0.06 + kick, 0.0), (l, 0.06 + kick, 0.0), 0.004, 4)
            if cap: seg_cyl(q, cap, (0.0, h, 0.0), (l, h, 0.0), 0.05, 10)
            else: seg_cyl(q, 'galv', (0.0, h, 0.0), (l, h, 0.0), 0.021, 8)
            for y in rails: seg_cyl(q, 'galv', (0.0, y, 0.0), (l, y, 0.0), 0.021, 8)
            sgn = 1.0
            if inside is not None:
                mx, mz = (x0 + x1) / 2, (z0 + z1) / 2; ux, uz = -(z1 - z0) / l, (x1 - x0) / l
                if not inside.contains(Point(mx + ux * 0.3, mz + uz * 0.3)): sgn = -1.0
            if kick > 0: q.box('galv', 0.0, l, 0.0, kick + 0.02, sgn * 0.03, sgn * 0.034) if sgn > 0 else q.box('galv', 0.0, l, 0.0, kick + 0.02, -0.034, -0.03)
            if banner_every and (i + k_ban) % banner_every == 0:
                mat, kind = BANNERS[(k_ban // banner_every + i) % len(BANNERS)]
                za, zb = (0.015, 0.035) if sgn > 0 else (-0.035, -0.015)
                q.box(mat, 0.08, l - 0.08, 0.35, h - 0.2, za, zb)
                zc0, zc1 = (zb, zb + 0.005) if sgn > 0 else (za - 0.005, za)
                q.box('flag_w', 0.16, l - 0.16, h - 0.32, h - 0.28, zc0, zc1); q.box('flag_w', 0.16, l - 0.16, 0.47, 0.51, zc0, zc1)
                picto(q, kind, 'flag_w', l / 2, (0.35 + h - 0.2) / 2 + 0.03, 0.75, zc0, zc1)
                for x in (0.12, l - 0.12):
                    for y in (0.45, h - 0.3): seg_cyl(q, 'chrome', (x, y, 0.0), (x, y, za if sgn > 0 else zb), 0.006, 4)
            along(p, q, x0, z0, x1, z1)
        k_ban += n
    for (a, b) in segs:
        dx, dz = b[0] - a[0], b[1] - a[1]; Ln = math.hypot(dx, dz); n = max(1, int(math.ceil(Ln / step - 1e-6)))
        for i in range(n + 1):
            if i == 0 and (a is not pts[0]): continue
            x, z = a[0] + dx * i / n, a[1] + dz * i / n
            r = 0.04 if (i == 0 or i == n) else 0.032
            seg_cyl(p, 'galv', (x, -0.25, z), (x, h + 0.06, z), r, 10); lathe(p, 'galv', [(r + 0.008, h + 0.06), (r + 0.008, h + 0.08), (r * 0.6, h + 0.11), (0.0, h + 0.115)], x=x, z=z, sec=10)
def outfield_fence():
    """Cerca do outfield em arco (1,83 m) com capa amarela, faixas de pictogramas e postes; vai de uma cerca lateral a outra."""
    p = Piece(); pts = FENCE_PTS[3:-1]
    fence_run(p, pts, 1.83, 2.6, cap='paint_y', rails=(1.0,), banner_every=2, inside=FENCED, pitch=0.1)
    return p
def side_fence(sd):
    """Cerca lateral (1,22 m) de uma linha de falta, do backstop ao outfield, com vaos do banco de reservas e do portao."""
    p = Piece()
    for (s0, s1) in ((BSW, DUG[0]), (DUG[1], GATE_S[0]), (GATE_S[1], S_END)):
        fence_run(p, [lp(s0, OF, sd), lp(s1, OF, sd)], 1.22, 2.5, rails=(), inside=FENCED)
    return p
def backstop():
    """Backstop: alambrado alto (5,5 m no meio, asas de 4 m) com 3 travessas, chapa de rodape e topo inclinado para o campo."""
    p = Piece()
    fence_run(p, [(-BKX, BKZ), (BKX, BKZ)], 5.5, 2.0, rails=(1.2, 2.6, 4.0), kick=0.45, inside=FENCED)
    for sd in (1, -1):
        a, b = ((BKX, BKZ), lp(BSW, OF, 1)) if sd > 0 else (lp(BSW, OF, -1), (-BKX, BKZ))
        fence_run(p, [a, b], 4.0, 2.0, rails=(1.2, 2.6), kick=0.45, inside=FENCED)
    # mãos-francesas dos postes do meio (escoras para tras)
    for x in (-BKX, -2.0, 0.0, 2.0, BKX):
        seg_cyl(p, 'galv', (x, 3.6, BKZ), (x, 0.0, BKZ + 1.6), 0.03, 8); p.cyl('concrete', 0.12, -0.2, 0.06, x, BKZ + 1.62, 12)
    return p
def foul_pole():
    """Poste de falta amarelo de 9 m com tela lateral (asa) do lado justo e base de concreto (pivo: pe; a asa fica para +X)."""
    p = Piece(); h = 9.0
    p.cyl('paint_y', 0.1, -0.3, h, 0, 0, 16); lathe(p, 'paint_y', [(0.12, h), (0.12, h + 0.04), (0.0, h + 0.08)], sec=16)
    lathe(p, 'concrete', [(0.32, -0.3), (0.32, 0.04), (0.28, 0.08), (0.0, 0.08)], sec=20)
    for y in (2.2, 8.6): seg_cyl(p, 'paint_y', (0.08, y, 0), (0.58, y, 0), 0.03, 8)
    seg_cyl(p, 'paint_y', (0.58, 2.2, 0), (0.58, 8.6, 0), 0.03, 8)
    q = Piece(); xs = np.linspace(0.12, 0.54, 8); ys = np.linspace(2.25, 8.55, 64)
    segs = [((x, 2.25), (x, 8.55)) for x in xs] + [((0.12, y), (0.54, y)) for y in ys]
    p.add('paint_y', wires_mesh([s for s in segs if s[0][0] == s[1][0]], 0.012, -0.004, 0.0)); p.add('paint_y', wires_mesh([s for s in segs if s[0][1] == s[1][1]], 0.012, 0.0, 0.004))
    return p
def field_gate(w=1.18, h=1.18):
    """Portao de alambrado: quadro de tubo, tela, travessa, trinco de garfo (pivo: dobradica, embaixo)."""
    p = Piece(); r = 0.02
    for x in (0.03, w - 0.03): seg_cyl(p, 'galv', (x, 0.08, 0), (x, h, 0), r, 8)
    for y in (0.08, h - 0.02, 0.62): seg_cyl(p, 'galv', (0.03, y, 0), (w - 0.03, y, 0), r * 0.85, 8)
    q = Piece(); chain(q, w - 0.1, 0.1, h - 0.05, 0.1); p.merge(q, tr(0.05, 0, 0))
    p.box('galv', w - 0.05, w + 0.03, 0.9, 0.94, -0.03, 0.03)
    for y in (0.2, h - 0.2): p.cyl('galv', 0.03, y - 0.05, y + 0.05, 0.0, 0.0, 10)
    return p

# ============================================================================ banco de reservas (pivo: meio da frente, chao; campo para +Z)
DGX = 3.5
def dugout(roof):
    """Abrigo dos jogadores: piso de concreto, paredes de bloco aparente com capa, porta de servico no fundo, frente de alambrado com
    2 saidas para o campo, pilares e viga de aco, cobertura de telha metalica ondulada colorida com rufo, calha e forro."""
    p = Piece(); d = DUGD; hb = 2.35
    ext_y(p, 'concrete', sbox(-DGX, -d, DGX, 0.0), 0.0, 0.1)
    door = (2.2, 3.1)
    wall_grid(p, 'x', -DGX, DGX, -d, -d + 0.2, [(door[0], door[1], 0.0, 0.1 + DH)], 0.1, hb, 'block')
    for s in (-1, 1):
        a, b = sorted((s * DGX, s * (DGX - 0.2))); wall_grid(p, 'z', -d + 0.2, -0.0, a, b, [], 0.1, hb, 'block')
    # capa de concreto no alto das paredes
    cap = unary_union([sbox(-DGX - 0.02, -d - 0.02, DGX + 0.02, -d + 0.22), sbox(-DGX - 0.02, -d, -DGX + 0.22, 0.02), sbox(DGX - 0.22, -d, DGX + 0.02, 0.02)])
    ext_y(p, 'conc_s', cap, hb, hb + 0.06)
    # frente: pilares, viga, alambrado entre as saidas
    for x in (-2.4, 0.0, 2.4):
        p.box('steel_d', x - 0.05, x + 0.05, 0.1, hb + 0.06, -0.1, 0.0)
    p.box('steel_d', -DGX + 0.2, DGX - 0.2, hb - 0.12, hb + 0.06, -0.1, 0.0)
    for (a, b) in ((-2.35, -0.05), (0.05, 2.35)):
        q = Piece(); chain(q, b - a, 0.12, hb - 0.14, 0.1); p.merge(q, tr(a, 0.0, -0.05))
        seg_cyl(p, 'galv', (a, 1.0, -0.05), (b, 1.0, -0.05), 0.018, 8)
    # cobertura de telha ondulada: chapa, ondas, rufo, calha na frente e forro
    yr = hb + 0.06; ov = 0.35
    ext_y(p, 'ceil', sbox(-DGX - ov, -d - ov, DGX + ov, ov), yr, yr + 0.02)
    ext_y(p, roof, sbox(-DGX - ov, -d - ov, DGX + ov, ov), yr + 0.02, yr + 0.05)
    for x in np.arange(-DGX - ov + 0.1, DGX + ov - 0.05, 0.2):
        p.hull(roof, [(xx, yy, z) for z in (-d - ov, ov) for (xx, yy) in ((x - 0.05, yr + 0.05), (x + 0.05, yr + 0.05), (x - 0.025, yr + 0.085), (x + 0.025, yr + 0.085))])
    a = sbox(-DGX - ov - 0.03, -d - ov - 0.03, DGX + ov + 0.03, ov + 0.03); ext_y(p, 'trim_w', a.difference(a.buffer(-0.035, join_style=2)), yr - 0.12, yr + 0.1)
    prof_x(p, 'trim_w', -DGX - ov - 0.03, DGX + ov + 0.03, [(ov + 0.03, yr - 0.04), (ov + 0.16, yr - 0.04), (ov + 0.18, yr + 0.06), (ov + 0.16, yr + 0.06), (ov + 0.15, yr - 0.02), (ov + 0.03, yr - 0.02)])
    for s in (-1, 1): seg_cyl(p, 'trim_w', (s * (DGX + ov - 0.2), yr - 0.03, ov + 0.1), (s * (DGX + ov - 0.2), 0.12, ov + 0.1), 0.035, 10)
    # luminaria no forro e caixa de luz
    p.box('metal', -0.5, 0.5, yr - 0.06, yr, -d / 2 - 0.08, -d / 2 + 0.08); p.box('lamp_glass', -0.47, 0.47, yr - 0.075, yr - 0.06, -d / 2 - 0.06, -d / 2 + 0.06)
    p.box('steel', -DGX + 0.2, -DGX + 0.26, 1.6, 1.9, -d + 0.6, -d + 0.8)
    return p
def dugout_bench(L1=5.2):
    """Banco corrido de 3 tabuas sobre maos-francesas de aco e prateleira de baixo para as bolsas (pivo: meio, chao; senta-se para +Z)."""
    p = Piece(); x0, x1 = -L1 / 2, L1 / 2
    for k in range(3): p.cham('bench_w', x0, x1, 0.43, 0.47, 0.02 + k * 0.13, 0.13 + k * 0.13, 0.006)
    for k in range(2): p.cham('bench_w', x0, x1, 0.12, 0.15, 0.04 + k * 0.16, 0.19 + k * 0.16, 0.005)
    for x in np.linspace(x0 + 0.15, x1 - 0.15, 4):
        p.box('steel_d', x - 0.025, x + 0.025, 0.0, 0.43, 0.32, 0.36); p.box('steel_d', x - 0.025, x + 0.025, 0.39, 0.43, 0.0, 0.4)
        p.box('steel_d', x - 0.025, x + 0.025, 0.08, 0.12, 0.0, 0.36); p.box('steel_d', x - 0.025, x + 0.025, 0.0, 0.43, 0.0, 0.03)
    for (x, m) in ((-1.6, 'canvas'), (0.4, 'tarp'), (1.5, 'canvas')):
        p.cham(m, x - 0.35, x + 0.35, 0.15, 0.4, 0.06, 0.32, 0.04); p.box('dark', x - 0.2, x + 0.2, 0.4, 0.42, 0.18, 0.2)
    return p
def helmet(p, m, x, y, z, ry=0.0):
    q = Piece(); r = 0.13
    sph = trimesh.creation.icosphere(subdivisions=2, radius=r); sph = slice_keep(sph, [0, 0, 0], [0, 1, 0]); q.add(m, sph)
    q.hull(m, [(xx, 0.0, zz) for (xx, zz) in ((-0.1, 0.1), (0.1, 0.1), (-0.06, 0.2), (0.06, 0.2))] + [(xx, 0.015, zz) for (xx, zz) in ((-0.1, 0.1), (0.1, 0.1))])
    for s in (-1, 1): q.hull(m, [(s * 0.125, yy, zz) for yy in (-0.1, 0.02) for zz in (-0.03, 0.05)] + [(s * 0.135, -0.05, 0.0)])
    p.merge(q, rot_y(ry, (x, y, z)))
def helmet_rack():
    """Cubiculos de madeira para capacetes (2 x 4) com capacetes azuis e vermelhos e um saco de bolas (pivo: meio, chao; frente +Z)."""
    p = Piece(); w, h, d = 1.6, 0.95, 0.36
    xs = np.linspace(-w / 2, w / 2, 5)
    for x in xs: p.box('wood', x - 0.009, x + 0.009, 0.3, 0.3 + h, 0.0, d)
    for y in (0.3, 0.3 + h / 2, 0.3 + h): p.box('wood', -w / 2 - 0.009, w / 2 + 0.009, y - 0.009, y + 0.009, 0.0, d)
    p.box('wood', -w / 2 - 0.009, w / 2 + 0.009, 0.309, 0.3 + h - 0.009, 0.0, 0.012)
    for x in (-w / 2 + 0.05, w / 2 - 0.05): p.box('steel_d', x - 0.02, x + 0.02, 0.0, 0.3, 0.05, d - 0.05)
    for i in range(4):
        for j in range(2):
            if (i, j) == (2, 1): continue
            helmet(p, 'helmet_b' if (i + j) % 2 else 'helmet_r', (xs[i] + xs[i + 1]) / 2, 0.3 + 0.009 + j * h / 2 + 0.105, d / 2, 180.0)
    return p
def bat(p, x, y, z, ax=0.0, az=0.0, mat='wood'):
    q = Piece(); lathe(q, mat, [(0.0, 0.0), (0.03, 0.0), (0.032, 0.015), (0.014, 0.03), (0.013, 0.3), (0.02, 0.45), (0.032, 0.62), (0.033, 0.78), (0.0, 0.79)], sec=10)
    lathe(q, 'rubber', [(0.015, 0.06), (0.015, 0.28)], sec=10)
    M = tr(x, y, z) @ trimesh.transformations.rotation_matrix(math.radians(ax), [1, 0, 0]) @ trimesh.transformations.rotation_matrix(math.radians(az), [0, 0, 1]); p.merge(q, M)
def bat_rack():
    """Porta-tacos de parede: travessa com recortes e 6 tacos de madeira e aluminio apoiados em pe (pivo: meio, chao; frente +Z)."""
    p = Piece(); L1 = 1.2
    p.box('wood', -L1 / 2, L1 / 2, 0.82, 0.92, 0.0, 0.14); p.box('wood', -L1 / 2, L1 / 2, 0.0, 0.06, 0.0, 0.18)
    for k, x in enumerate(np.linspace(-L1 / 2 + 0.12, L1 / 2 - 0.12, 6)):
        p.box('dark', x - 0.025, x + 0.025, 0.92, 0.921, 0.07, 0.14)
        bat(p, x, 0.06, 0.1, -3.0, (k % 3 - 1) * 2.0, 'alu' if k % 2 else 'wood')
    return p
def water_cooler():
    """Garrafao termico laranja com torneira sobre banquinho de aco e pilha de copos (pivo: centro, chao)."""
    p = Piece()
    for (x, z) in ((-0.17, -0.17), (0.17, -0.17), (0.17, 0.17), (-0.17, 0.17)): seg_cyl(p, 'steel', (x, 0.0, z), (x * 0.8, 0.55, z * 0.8), 0.014, 6)
    p.box('steel', -0.2, 0.2, 0.55, 0.58, -0.2, 0.2)
    lathe(p, 'cooler_o', [(0.0, 0.58), (0.17, 0.58), (0.18, 0.6), (0.18, 1.0), (0.17, 1.02), (0.0, 1.02)], sec=20)
    lathe(p, 'paint_w', [(0.0, 1.02), (0.16, 1.02), (0.16, 1.06), (0.1, 1.08), (0.0, 1.08)], sec=20)
    for y in (0.66, 0.94): ring_y(p, 'paint_w', 0.18, 0.186, y, y + 0.03, 0, 0, 20)
    p.box('paint_w', -0.025, 0.025, 0.66, 0.71, 0.17, 0.23); p.box('paint_w', -0.012, 0.012, 0.71, 0.75, 0.2, 0.22)
    lathe(p, 'paper', [(0.0, 0.58), (0.035, 0.58), (0.04, 0.72), (0.0, 0.72)], x=0.13, z=-0.1, sec=10)
    return p
def ball_bucket():
    """Balde de bolas com 9 bolas por cima (pivo: centro, chao)."""
    p = Piece(); lathe(p, 'paint_w', [(0.0, 0.0), (0.14, 0.0), (0.16, 0.4), (0.15, 0.4), (0.13, 0.02), (0.0, 0.02)], sec=18)
    for (x, z) in ((0, 0), (0.07, 0.05), (-0.07, 0.04), (0.04, -0.08), (-0.05, -0.07), (0.1, -0.03), (-0.1, -0.01), (0.0, 0.1), (0.02, -0.02)):
        p.sphere('ball', 0.037, x, 0.36 + (0.03 if (x, z) == (0.02, -0.02) else 0.0), z, 1)
    seg_cyl(p, 'steel', (-0.155, 0.38, 0), (0.0, 0.5, 0), 0.004, 4); seg_cyl(p, 'steel', (0.0, 0.5, 0), (0.155, 0.38, 0), 0.004, 4)
    return p

# ============================================================================ arquibancada de aluminio (pivo: meio da frente, chao; plateia olha para +Z)
NROW = 5; RD = 0.72
def bleacher(L1=7.0):
    """Arquibancada de 5 fileiras: assentos e pisos de perfil de aluminio (2 tabuas cada), corredor do meio com degraus, estrutura
    de cantoneiras de aco em A, guarda-corpo atras e nos lados, corrimao do corredor e sapatas."""
    p = Piece(); hx = L1 / 2; ax = 0.8
    for i in range(NROW):
        z0 = -i * RD; yf = 0.2 + 0.4 * i; ys = yf + 0.42
        for (a, b) in ((-hx, -ax), (ax, hx)):
            for k in range(2):
                p.cham('alu', a, b, yf - 0.04, yf, z0 - 0.3 + k * 0.15, z0 - 0.165 + k * 0.15, 0.006)
                p.cham('alu', a, b, ys - 0.05, ys, z0 - 0.64 + k * 0.14, z0 - 0.505 + k * 0.14, 0.006)
            for x in (a, b): p.box('alu', x - 0.004 if x == b else x, x if x == b else x + 0.004, ys - 0.07, ys, z0 - 0.64, z0 - 0.365)
            p.box('alu', a, b, yf - 0.24, yf - 0.04, z0 - 0.004, z0)       # espelho (rodape) da fileira
        # degraus do corredor: meio degrau no piso e outro na altura do assento - 0,22
        p.cham('alu', -ax + 0.02, ax - 0.02, yf - 0.04, yf, z0 - 0.36, z0, 0.006)
        p.cham('alu', -ax + 0.02, ax - 0.02, yf + 0.16, yf + 0.2, z0 - 0.72, z0 - 0.36, 0.006)
        p.box('paint_y', -ax + 0.02, ax - 0.02, yf + 0.2, yf + 0.203, z0 - 0.4, z0 - 0.36); p.box('paint_y', -ax + 0.02, ax - 0.02, yf, yf + 0.003, z0 - 0.04, z0)
    ytop = 0.2 + 0.4 * NROW; zb = -NROW * RD
    p.cham('alu', -hx, hx, ytop - 0.04, ytop, zb - 0.3, zb, 0.006)
    # estrutura em A
    for x in list(np.linspace(-hx + 0.15, hx - 0.15, 4)) + [-ax - 0.03, ax + 0.03]:
        seg_cyl(p, 'steel', (x, 0.0, 0.0), (x, ytop - 0.04, zb - 0.15), 0.025, 6)
        seg_cyl(p, 'steel', (x, 0.0, zb - 0.25), (x, ytop - 0.04, zb - 0.25), 0.025, 6)
        for i in range(NROW):
            z0 = -i * RD; yf = 0.2 + 0.4 * i
            seg_cyl(p, 'steel', (x, yf - 0.05, z0 - 0.02), (x, yf - 0.05, z0 - 0.7), 0.018, 6)
            seg_cyl(p, 'steel', (x, yf + 0.37, z0 - 0.36), (x, yf + 0.37, z0 - 0.7), 0.018, 6)
            seg_cyl(p, 'steel', (x, yf - 0.05, z0 - 0.5), (x, yf + 0.37, z0 - 0.5), 0.018, 6)
        seg_cyl(p, 'steel', (x, 0.0, zb - 0.25), (x, ytop * 0.6, zb * 0.45), 0.02, 6)
        for z in (0.0, zb - 0.25): p.box('steel_d', x - 0.08, x + 0.08, 0.0, 0.012, z - 0.08, z + 0.08)
    for y in (0.3, 1.2): seg_cyl(p, 'steel', (-hx + 0.15, y, zb - 0.25), (hx - 0.15, y, zb - 0.25), 0.018, 6)
    # guarda-corpo de tras (1,07 m acima do ultimo piso) e dos lados
    for x in np.linspace(-hx + 0.03, hx - 0.03, 8): seg_cyl(p, 'alu', (x, ytop, zb - 0.27), (x, ytop + 1.07, zb - 0.27), 0.02, 8)
    for y in (ytop + 0.5, ytop + 1.07): seg_cyl(p, 'alu', (-hx + 0.03, y, zb - 0.27), (hx - 0.03, y, zb - 0.27), 0.024, 8)
    for s in (-1, 1):
        x = s * (hx + 0.03)
        seg_cyl(p, 'alu', (x, 0.2 + 1.07, -0.05), (x, ytop + 1.07, zb - 0.27), 0.024, 8); seg_cyl(p, 'alu', (x, 0.2 + 0.55, -0.05), (x, ytop + 0.5, zb - 0.27), 0.02, 8)
        for i in range(NROW + 1):
            z0 = -i * RD if i < NROW else zb - 0.27; yf = 0.2 + 0.4 * i
            seg_cyl(p, 'alu', (x, yf - 0.04, z0 - 0.05 if i < NROW else z0), (x, yf + 1.07 if i < NROW else ytop + 1.07, z0 - 0.05 if i < NROW else z0), 0.02, 8)
    # corrimao do corredor
    for i in range(0, NROW, 2): seg_cyl(p, 'alu', (0.0, 0.2 + 0.4 * i, -i * RD - 0.3), (0.0, 0.2 + 0.4 * i + 0.9, -i * RD - 0.3), 0.02, 8)
    seg_cyl(p, 'alu', (0.0, 0.2 + 0.9, -0.3), (0.0, 0.2 + 0.4 * (NROW - 1) + 0.9, -(NROW - 1) * RD - 0.3), 0.024, 8)
    return p
# ============================================================================ cabine (lanchonete + banheiros embaixo, cabine de transmissao em cima)
# coordenadas locais da cabine: x de -BX a BX, z de -BZ a BZ, frente (+Z) olhando a base; pivo no chao
F1 = Y0 + H; ST = 0.25; CH1 = 2.6; YE = F1 + CH1                     # piso de cima 3,15; beiral 5,75
IX, IZ = BX - T, BZ - T
PART_X = (0.8, 1.0); RR_Z = (-0.05, 0.05)                           # parede lanchonete/banheiros e divisoria dos banheiros
SERV = (-2.3, 0.3, Y0 + 0.95, Y0 + 2.05)                            # janela de atendimento (frente)
BDOOR = (-1.6, -0.7)                                                # porta dos fundos da lanchonete
RDOORS = ((0.55, 1.45), (-1.45, -0.55))                             # portas dos banheiros (face +X, em z)
UDOOR = (-2.1, -1.2)                                                # porta da cabine de cima (fundos)
STZ = (-BZ - 1.15, -BZ - 0.05); SNR = 18; SRR = F1 / SNR; STRD = 0.26
SX_BOT = 3.57; SX_TOP = SX_BOT - (SNR - 1) * STRD; LND = (-2.45, SX_TOP)  # escada sobe para -X; patamar
def slider(p, a, b, ya, yb, z0=-0.17):
    """Janela de correr de aluminio (do kit 56): 2 folhas, trilhos, fecho e puxador."""
    f = 0.045; zf0, zf1 = z0, z0 + 0.09
    p.box('alu', a, a + f, ya, yb, zf0, zf1); p.box('alu', b - f, b, ya, yb, zf0, zf1)
    p.box('alu', a + f, b - f, yb - f, yb, zf0, zf1); p.box('alu', a + f, b - f, ya, ya + f, zf0, zf1)
    xm = (a + b) / 2; s = 0.035; ia, ib, ja, jb = a + f, b - f, ya + f, yb - f
    for (u, v, za, zb) in ((ia, xm + 0.02, zf1 - 0.035, zf1 - 0.012), (xm - 0.02, ib, zf0 + 0.012, zf0 + 0.035)):
        p.box('alu', u, u + s, ja, jb, za, zb); p.box('alu', v - s, v, ja, jb, za, zb)
        p.box('alu', u + s, v - s, jb - s, jb, za, zb); p.box('alu', u + s, v - s, ja, ja + s, za, zb)
        p.box('glass', u + s - 0.004, v - s + 0.004, ja + s - 0.004, jb - s + 0.004, (za + zb) / 2 - 0.002, (za + zb) / 2 + 0.002)
    ym = (ja + jb) / 2; p.box('chrome', xm - 0.04, xm - 0.016, ym - 0.05, ym + 0.05, zf0 - 0.002, zf0 + 0.012)
def casing(p, a, b, ya, yb, w=0.09, d=0.025, sill=True, mat='trim_w'):
    """Guarnicao de tabua em volta do vao (por fora, z de 0 a d) com peitoril saliente."""
    p.box(mat, a - w, a, ya - (0.0 if sill else 0.0), yb + w, 0.0, d); p.box(mat, b, b + w, ya, yb + w, 0.0, d); p.box(mat, a, b, yb, yb + w, 0.0, d)
    if sill: p.box(mat, a - w - 0.04, b + w + 0.04, ya - 0.05, ya, 0.0, d + 0.04)
def battens(p, x0, x1, y0, y1, skip, step=0.4, d=0.02):
    """Ripas verticais (tabua e mata-junta) a cada 0,4 m na face externa; param nas guarnicoes dos vaos."""
    for x in np.arange(x0 + step / 2, x1 - 0.05, step):
        segs = [(y0, y1)]
        for (a, b, ya, yb) in skip:
            if a - 0.12 < x < b + 0.12: segs = [s for (c, e) in segs for s in ((c, min(e, ya - 0.05)), (max(c, yb + 0.09), e)) if s[1] - s[0] > 0.05]
        for (c, e) in segs: p.box('trim_w', x - 0.03, x + 0.03, c, e, 0.0, d)
FACES = {'front': (rot_y(0, (0, 0, BZ)), BX), 'back': (rot_y(180, (0, 0, -BZ)), BX), 'right': (rot_y(90, (BX, 0, 0)), IZ), 'left': (rot_y(-90, (-BX, 0, 0)), IZ)}
def cabin_face(face, floor):
    """Uma fachada da cabine, num pavimento, na coordenada local da fachada (x ao longo, face externa em z = 0, parede para -Z)."""
    M, hl = FACES[face]; q = Piece(); holes = []; win = []; doors = []
    if floor == 0:
        y0, y1, out = 0.0, F1, 'block_p'
        if face == 'front': win = [SERV]
        if face == 'back': doors = [(-BDOOR[1], -BDOOR[0])]
        if face == 'right': doors = [(-b, -a) for (a, b) in RDOORS]
        if face == 'left': win = [(-0.6, 0.6, Y0 + 1.55, Y0 + 2.15)]
    else:
        y0, y1, out = F1, YE, 'siding'
        if face == 'front': win = [(-2.55, -0.05, F1 + 0.95, F1 + 2.1), (0.05, 2.55, F1 + 0.95, F1 + 2.1)]
        if face == 'back': doors = [(-UDOOR[1], -UDOOR[0])]
        if face in ('right', 'left'): win = [(-0.75, 0.75, F1 + 0.95, F1 + 2.1)]
    dh = [(a, b, (Y0 if floor == 0 else F1) - 0.001, (Y0 if floor == 0 else F1) + DH) for (a, b) in doors]
    if face == 'front' and floor == 1:
        holes = [(-2.55, 2.55, F1 + 0.95, F1 + 2.1)]
    else: holes = list(win)
    holes += dh
    wall2(q, 'x', -hl, hl, 0.0, -T, holes, y0, y1, out, 'plaster')
    for (a, b, ya, yb) in win:
        slider(q, a, b, ya, yb, -0.14)
        if (a, b, ya, yb) != SERV: casing(q, a, b, ya, yb)
    if face == 'front' and floor == 1: q.box('alu', -0.05, 0.05, F1 + 0.95, F1 + 2.1, -0.14, -0.05)
    for (a, b, ya, yb) in dh:
        casing(q, a, b, ya + 0.001, yb, sill=False)
        q.box('alu', a, b, ya, ya + 0.012, -T, 0.0)
        q.box('trim_w', a, a + 0.04, ya + 0.013, yb, -T + 0.02, -0.02); q.box('trim_w', b - 0.04, b, ya + 0.013, yb, -T + 0.02, -0.02); q.box('trim_w', a + 0.04, b - 0.04, yb - 0.04, yb, -T + 0.02, -0.02)
    if floor == 1:
        battens(q, -hl + 0.12, hl - 0.12, y0 + 0.2, y1 - 0.1, [h_ for h_ in holes])
    else:
        # embasamento pintado (para nas portas) e cantoneira de cima
        gaps = [(a - 0.09, b + 0.09) for (a, b, ya, yb) in dh]
        for (a, b) in segs_excl(gaps, -hl + (0.0 if face in ('front', 'back') else 0.0), hl): q.box('trim', a, b, 0.0, 0.45, 0.0, 0.012)
    # lampada e plaquetas de pictograma junto das portas
    for (a, b, ya, yb) in dh:
        xl = b + 0.3
        q.box('metal', xl - 0.07, xl + 0.07, yb + 0.15, yb + 0.33, 0.0, 0.04); q.hull('lamp_glass', [(xl + dx, yb + dy, z) for dx in (-0.06, 0.06) for dy in (0.17, 0.31) for z in (0.04, 0.14)])
        if face == 'right' and floor == 0:
            q.box('pad_b', xl - 0.12, xl + 0.12, 1.45, 1.75, 0.0, 0.012); ped = (xl, 1.6)
            pic = Piece(); picto_person(pic, 'flag_w', xl, 1.6, 0.26, 0.012, 0.016, woman=(a < 0))
            q.merge(pic)
    return q, M
def picto_person(p, mat, cx, cy, s, z0, z1, woman=False):
    """Pictograma de pessoa (cabeca + corpo; saia se woman) para as portas dos banheiros."""
    def ex(g):
        m = D._fix(trimesh.creation.extrude_polygon(g, z1 - z0)); m.apply_translation([0, 0, z0]); p.add(mat, m)
    ex(Point(cx, cy + 0.36 * s).buffer(0.1 * s, 16))
    if woman: ex(Polygon([(cx - 0.08 * s, cy + 0.22 * s), (cx + 0.08 * s, cy + 0.22 * s), (cx + 0.2 * s, cy - 0.15 * s), (cx - 0.2 * s, cy - 0.15 * s)]))
    else: ex(sbox(cx - 0.13 * s, cy - 0.12 * s, cx + 0.13 * s, cy + 0.22 * s))
    for dx in (-0.06, 0.06): ex(sbox(cx + dx * s - 0.035 * s, cy - 0.45 * s, cx + dx * s + 0.035 * s, cy - 0.12 * s))
def cabin_shell(floor):
    """Envoltoria de um pavimento da cabine (4 fachadas) com quinas, paredes internas, pisos e forro."""
    p = Piece()
    for face in FACES:
        q, M = cabin_face(face, floor); p.merge(q, M)
    y0, y1 = (0.0, F1) if floor == 0 else (F1, YE)
    # cantoneiras de quina (tabua por fora, de 2 faces)
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * BX, sz * BZ; a, b = sorted((x, x + sx * 0.03)); c, d = sorted((z - sz * 0.14, z + sz * 0.03))
            p.box('trim_w', a, b, y0 + (0.45 if floor == 0 else 0.0), y1, c, d); a, b = sorted((x - sx * 0.14, x)); c, d = sorted((z, z + sz * 0.03))
            p.box('trim_w', a, b, y0 + (0.45 if floor == 0 else 0.0), y1, c, d)
    if floor == 0:
        ext_y(p, 'concrete', sbox(-IX, -IZ, IX, IZ), 0.0, Y0 - 0.012)
        ext_y(p, 'vinyl_f', sbox(-IX, -IZ, PART_X[0], IZ), Y0 - 0.012, Y0)
        ext_y(p, 'tile_w', sbox(PART_X[1], -IZ, IX, IZ).difference(sbox(PART_X[1], RR_Z[0], IX, RR_Z[1])), Y0 - 0.012, Y0)
        wall_grid(p, 'z', -IZ, IZ, PART_X[0], PART_X[1], [], Y0, F1 - ST, 'plaster')
        wall_grid(p, 'x', PART_X[1], IX, RR_Z[0], RR_Z[1], [], Y0 - 0.012, F1 - ST, 'tile_g')
        # azulejo dos banheiros ate 1,4 m e rodapes
        for (z0, z1) in ((RR_Z[1], IZ), (-IZ, RR_Z[0])):
            for x in (PART_X[1],): p.box('tile_g', x, x + 0.008, Y0, Y0 + 1.4, z0, z1)
            sg = 1 if z0 > 0 else -1
            zw = IZ if z0 > 0 else -IZ; a, b = sorted((zw, zw - sg * 0.008)); p.box('tile_g', PART_X[1] + 0.008, IX, Y0, Y0 + 1.4, a, b)
            gaps = [(a_, b_) for (a_, b_) in RDOORS if z0 < (a_ + b_) / 2 < z1]
            for (c, d) in segs_excl([(g0 - 0.005, g1 + 0.005) for (g0, g1) in gaps], z0, z1): p.box('tile_g', IX - 0.008, IX, Y0, Y0 + 1.4, c, d)
        # rodape da lanchonete (para na porta)
        for (a, b) in segs_excl([BDOOR], -IX, PART_X[0]): p.box('vinyl', a, b, Y0, Y0 + 0.1, -IZ, -IZ + 0.012)
        p.box('vinyl', -IX, PART_X[0], Y0, Y0 + 0.1, IZ - 0.012, IZ)
        p.box('vinyl', -IX, -IX + 0.012, Y0, Y0 + 0.1, -IZ + 0.012, IZ - 0.012); p.box('vinyl', PART_X[0] - 0.012, PART_X[0], Y0, Y0 + 0.1, -IZ + 0.012, IZ - 0.012)
        # faixa (cinta) entre os pavimentos
        ring = sbox(-BX - 0.04, -BZ - 0.04, BX + 0.04, BZ + 0.04).difference(sbox(-BX, -BZ, BX, BZ))
        ext_y(p, 'trim', ring, F1 - 0.12, F1 + 0.06)
    else:
        ext_y(p, 'wood', sbox(-IX, -IZ, IX, IZ), F1, F1 + 0.012)
        for (a, b) in segs_excl([UDOOR], -IX, IX): p.box('trim_w', a, b, F1 + 0.012, F1 + 0.1, -IZ, -IZ + 0.012)
        p.box('trim_w', -IX, IX, F1 + 0.012, F1 + 0.1, IZ - 0.012, IZ)
        for s in (-1, 1): a, b = sorted((s * IX, s * (IX - 0.012))); p.box('trim_w', a, b, F1 + 0.012, F1 + 0.1, -IZ + 0.012, IZ - 0.012)
    return p
def cabin_slab():
    """Laje entre os pavimentos: forro do terreo, laje de concreto e luminarias."""
    p = Piece(); ext_y(p, 'ceil', sbox(-IX, -IZ, IX, IZ), F1 - ST, F1 - ST + 0.012); ext_y(p, 'conc_s', sbox(-IX, -IZ, IX, IZ), F1 - ST + 0.012, F1)
    for (x, z) in ((-1.0, 0.0), (1.9, 1.2), (1.9, -1.2)):
        p.box('metal', x - 0.3, x + 0.3, F1 - ST - 0.05, F1 - ST, z - 0.1, z + 0.1); p.box('lamp_glass', x - 0.28, x + 0.28, F1 - ST - 0.065, F1 - ST - 0.05, z - 0.08, z + 0.08)
    return p

# ============================================================================ telhado de 4 aguas com fiadas de telha em geometria
RX0, RZ0, RANG = BX + 0.38, BZ + 0.38, 26.0
def hip_roof():
    """Telhado de 4 aguas: nucleo, fiadas de telha asfaltica com degrau na ponta (cada fiada um pouco mais inclinada), capas nas
    cumeeiras e espigoes, testeira com rufo, forro do beiral, 2 cornetas de som e para-raios."""
    p = Piece(); ta = math.tan(math.radians(RANG)); e = 0.16; butt = 0.022
    yr = YE + RZ0 * ta; rx = RX0 - RZ0
    ext_y(p, 'ceil', sbox(-IX, -IZ, IX, IZ), YE - 0.17, YE - 0.15)
    p.hull('ceil', [(x, YE - 0.06, z) for x in (-RX0 + 0.03, RX0 - 0.03) for z in (-RZ0 + 0.03, RZ0 - 0.03)] + [(x, YE, z) for x in (-RX0 + 0.03, RX0 - 0.03) for z in (-RZ0 + 0.03, RZ0 - 0.03)])
    p.hull('shingle_c', [(x, YE, z) for x in (-RX0, RX0) for z in (-RZ0, RZ0)] + [(x, yr - 0.004, 0.0) for x in (-rx, rx)])
    def course(side, d0, d1, y_top0, y_top1):
        pts = []
        for d, yt in ((d0, y_top0), (d1, y_top1)):
            yb = YE + d * ta - 0.003
            if side in ('f', 'b'):
                sz = 1 if side == 'f' else -1; xe = RX0 - d; z = sz * (RZ0 - d)
                pts += [(-xe, yb, z), (xe, yb, z), (-xe, yt, z), (xe, yt, z)]
            else:
                sx = 1 if side == 'r' else -1; ze = RZ0 - d; x = sx * (RX0 - d)
                pts += [(x, yb, -ze), (x, yb, ze), (x, yt, -ze), (x, yt, ze)]
        p.hull('shingle', pts)
    nk = int(math.ceil(RZ0 / e))
    for side in ('f', 'b', 'r', 'l'):
        for k in range(nk):
            d0 = k * e; d1 = min(d0 + 2 * e, RZ0 - 0.002)
            if d1 - d0 < 0.02: continue
            course(side, d0, d1, YE + d0 * ta + butt, YE + d1 * ta + 0.004)
    # capas: cumeeira e 4 espigoes (pecas curtas sobrepostas)
    def cap(pa, pb, side_dirs):
        pa, pb = np.array(pa, float), np.array(pb, float); pts = []
        for q in (pa, pb):
            pts.append(q + [0, 0.05, 0])
            for dv in side_dirs: pts += [q + np.array(dv) * 0.13 + [0, 0.012, 0], q + np.array(dv) * 0.13 + [0, 0.032, 0]]
        p.hull('shingle_c', pts)
    xs = np.linspace(-rx - 0.05, rx + 0.05, 5)
    for a, b in zip(xs[:-1], xs[1:]): cap((a, yr, 0), (b + 0.03, yr, 0), [(0, -ta, 1), (0, -ta, -1)])
    for sx in (-1, 1):
        for sz in (-1, 1):
            A = np.array([sx * RX0, YE, sz * RZ0]); B = np.array([sx * rx, yr, 0.0]); n = 9
            for i in range(n):
                qa = A + (B - A) * i / n; qb = A + (B - A) * min(1.0, (i + 1.15) / n)
                cap(qa, qb, [(-sx, 0, 0), (0, 0, -sz)])
    # testeira com rufo e forro do beiral
    ring = sbox(-RX0, -RZ0, RX0, RZ0).difference(sbox(-RX0 + 0.03, -RZ0 + 0.03, RX0 - 0.03, RZ0 - 0.03))
    ext_y(p, 'trim_w', ring, YE - 0.22, YE - 0.003)
    ext_y(p, 'ceil', sbox(-RX0 + 0.03, -RZ0 + 0.03, RX0 - 0.03, RZ0 - 0.03).difference(sbox(-BX, -BZ, BX, BZ)), YE - 0.2, YE - 0.18)
    for (x, z) in ((-1.5, BZ + 0.2), (1.5, BZ + 0.2), (0.0, -BZ - 0.2)):
        p.box('dark', x - 0.12, x + 0.12, YE - 0.203, YE - 0.2, z - 0.04, z + 0.04)
    # cornetas de som nas quinas da frente
    for sx in (-1, 1):
        x = sx * (BX - 0.2); z = RZ0 - 0.1
        p.box('steel', x - 0.03, x + 0.03, YE - 0.5, YE - 0.2, z - 0.06, z)
        q = Piece(); lathe(q, 'paint_w', [(0.06, 0.0), (0.07, 0.12), (0.12, 0.3), (0.22, 0.42), (0.2, 0.42), (0.1, 0.3), (0.04, 0.12), (0.0, 0.12)], sec=16)
        q.cyl('paint_w', 0.08, -0.12, 0.0, 0, 0, 14)
        M = tr(x, YE - 0.42, z + 0.04) @ trimesh.transformations.rotation_matrix(math.radians(-70), [1, 0, 0]) @ trimesh.transformations.rotation_matrix(math.radians(sx * -25), [0, 0, 1]); p.merge(q, M)
    seg_cyl(p, 'chrome', (0.0, yr + 0.04, 0.0), (0.0, yr + 0.7, 0.0), 0.008, 6); p.sphere('chrome', 0.03, 0.0, yr + 0.72, 0.0, 1)
    return p

# ============================================================================ escada externa de aco (fundos), patamar e guarda-corpos
def cabin_stair():
    p = Piece(); z0, z1 = STZ
    for i in range(1, SNR):
        x1 = SX_BOT - (i - 1) * STRD; x0 = x1 - STRD; y = i * SRR
        p.box('steel', x0 - 0.02, x1, y - 0.04, y, z0 + 0.06, z1 - 0.06); p.box('steel_d', x0 - 0.02, x0 + 0.01, y - 0.18, y - 0.04, z0 + 0.06, z1 - 0.06)
        for xx in np.arange(x0 + 0.03, x1 - 0.02, 0.05): p.box('steel_d', xx, xx + 0.012, y + 0.0, y + 0.003, z0 + 0.08, z1 - 0.08)
    xt = SX_TOP; yt = F1
    for z in (z0 + 0.035, z1 - 0.035):
        p.hull('trim', [(x, y, zz) for zz in (z - 0.03, z + 0.03) for (x, y) in ((SX_BOT + 0.15, 0.0), (SX_BOT + 0.15, 0.3), (xt - 0.035, yt + 0.02), (xt - 0.035, yt - 0.3))])
    # patamar
    p.box('steel_d', LND[0], LND[1], yt - 0.18, yt - 0.012, z0, -BZ); p.box('steel', LND[0], LND[1], yt - 0.012, yt, z0, -BZ)
    for x in (LND[0] + 0.05, LND[1] - 0.05): p.box('trim', x - 0.05, x + 0.05, 0.0, yt - 0.18, z0 + 0.005, z0 + 0.105)
    for x in (LND[0] + 0.05, LND[1] - 0.05): p.box('concrete', x - 0.15, x + 0.15, -0.2, 0.06, z0 - 0.05, z0 + 0.15)
    p.box('concrete', SX_BOT - 0.05, SX_BOT + 0.3, -0.2, 0.06, z0 - 0.05, z1 + 0.05)
    # guarda-corpo de fora (lance + patamar) e corrimao junto da parede
    zr = z0 + 0.03
    for i in range(0, SNR, 3):
        x = SX_BOT - i * STRD + 0.1; y = i * SRR
        seg_cyl(p, 'trim', (x, y, zr), (x, y + 0.95, zr), 0.022, 8)
    seg_cyl(p, 'trim', (SX_BOT + 0.1, 0.95, zr), (xt, yt + 0.95, zr), 0.026, 10)
    seg_cyl(p, 'trim', (SX_BOT + 0.1, 0.5, zr), (xt, yt + 0.5, zr), 0.018, 8)
    for x in np.linspace(LND[0] + 0.03, xt, 5): seg_cyl(p, 'trim', (x, yt, zr), (x, yt + 1.0, zr), 0.022, 8)
    seg_cyl(p, 'trim', (xt, yt + 1.0, zr), (LND[0] + 0.03, yt + 1.0, zr), 0.026, 10); seg_cyl(p, 'trim', (xt, yt + 0.5, zr), (LND[0] + 0.03, yt + 0.5, zr), 0.018, 8)
    for y in (0.5, 1.0): seg_cyl(p, 'trim', (LND[0] + 0.03, yt + y, zr), (LND[0] + 0.03, yt + y, -BZ - 0.02), 0.022 if y > 0.6 else 0.018, 8)
    seg_cyl(p, 'trim', (LND[0] + 0.03, yt, -BZ - 0.06), (LND[0] + 0.03, yt + 1.0, -BZ - 0.06), 0.022, 8)
    zw = -BZ - 0.09
    seg_cyl(p, 'trim', (SX_BOT - 0.3, 0.9 + 0.3 * SRR / STRD, zw), (xt + 0.2, yt + 0.9 - 0.2 * SRR / STRD, zw), 0.02, 8)
    for x in (SX_BOT - 0.6, (SX_BOT + xt) / 2, xt + 0.4):
        yy = (SX_BOT - x) / STRD * SRR + 0.9; seg_cyl(p, 'trim', (x, yy, zw), (x, yy, -BZ - 0.003), 0.008, 6); p.box('trim', x - 0.03, x + 0.03, yy - 0.04, yy + 0.04, -BZ - 0.012, -BZ - 0.003)
    return p
# ============================================================================ interiores da cabine (pivo da cabine; y = chao)
def hotdog_roller(p, x, y, z):
    p.cham('chrome', x - 0.3, x + 0.3, y, y + 0.16, z - 0.22, z + 0.22, 0.01)
    for k in range(7): seg_cyl(p, 'chrome', (x - 0.24, y + 0.18, z - 0.18 + k * 0.06), (x + 0.24, y + 0.18, z - 0.18 + k * 0.06), 0.012, 8)
    for k in (1, 3, 4, 6): seg_cyl(p, 'food_r', (x - 0.16, y + 0.205, z - 0.18 + k * 0.06), (x + 0.16, y + 0.205, z - 0.18 + k * 0.06), 0.014, 8)
def popcorn_cart(p, x, y, z):
    """Pipoqueira de vitrine sobre carrinho vermelho com rodas (frente +Z)."""
    p.cham('formica', x - 0.32, x + 0.32, y + 0.15, y + 0.85, z - 0.25, z + 0.25, 0.01)
    for (dx, dz) in ((-0.26, -0.2), (0.26, -0.2), (0.26, 0.2), (-0.26, 0.2)):
        p.cyl('steel_d', 0.012, y + 0.08, y + 0.15, x + dx, z + dz, 6); disc_x(p, 'rubber', 0.07, x + dx - 0.02, x + dx + 0.02, y + 0.07, z + dz, 12)
    p.cham('formica', x - 0.3, x + 0.3, y + 0.85, y + 0.92, z - 0.24, z + 0.24, 0.008)
    for xx in (x - 0.29, x + 0.27):
        for zz in (z - 0.23, z + 0.21): p.box('chrome', xx, xx + 0.02, y + 0.92, y + 1.5, zz, zz + 0.02)
    p.box('glass', x - 0.27, x + 0.27, y + 0.93, y + 1.48, z + 0.215, z + 0.219); p.box('glass', x - 0.27, x + 0.27, y + 0.93, y + 1.48, z - 0.229, z - 0.225)
    for xx in (x - 0.285, x + 0.285): p.box('glass', xx - 0.002, xx + 0.002, y + 0.93, y + 1.48, z - 0.21, z + 0.2)
    ext_y(p, 'pop', sbox(x - 0.27, z - 0.21, x + 0.27, z + 0.2), y + 0.92, y + 1.06)
    for (dx, dz) in ((-0.15, -0.05), (0.05, 0.08), (0.18, -0.1), (-0.05, -0.12), (0.12, 0.1)): p.sphere('pop', 0.06, x + dx, y + 1.07, z + dz, 1)
    lathe(p, 'steel', [(0.0, y + 1.24), (0.1, y + 1.26), (0.12, y + 1.32), (0.0, y + 1.33)], x=x, z=z, sec=16)
    seg_cyl(p, 'chrome', (x, y + 1.33, z), (x, y + 1.48, z), 0.01, 6)
    p.box('formica', x - 0.32, x + 0.32, y + 1.5, y + 1.62, z - 0.25, z + 0.25); p.box('pad_y', x - 0.33, x + 0.33, y + 1.54, y + 1.58, z - 0.252, z + 0.252)
def concession():
    """Lanchonete: balcao de atendimento com caixa, guardanapos e bombas de molho; balcao do fundo com chapa, rolo de salsicha e pia;
    geladeira de vidro, freezer horizontal, pipoqueira de carrinho, prateleiras com copos e caixas sem texto, extintor."""
    p = Piece(); y = Y0
    # balcao de atendimento sob a janela
    p.box('counter', -2.6, 0.55, y, y + 0.88, 1.65, IZ - 0.05); p.box('vinyl', -2.6, 0.55, y, y + 0.1, 1.62, 1.65)
    p.box('ctop', -2.62, 0.57, y + 0.88, y + 0.92, 1.6, IZ)
    for x in np.linspace(-2.4, 0.3, 5): p.box('dark', x - 0.002, x + 0.002, y + 0.15, y + 0.8, 1.615, 1.62)
    q = register(); p.merge(q, rot_y(180, (-1.9, y + 0.92, 1.95)))
    p.cham('chrome', -1.2, -1.04, y + 0.92, y + 1.08, 2.0, 2.12, 0.008); p.box('paper', -1.18, -1.06, y + 1.02, y + 1.07, 2.01, 2.11)
    for (k, m) in enumerate(('food_r', 'food_y', 'food_g')):
        x = -0.6 + k * 0.16; lathe(p, m, [(0.0, y + 0.92), (0.055, y + 0.92), (0.055, y + 1.12), (0.035, y + 1.16), (0.0, y + 1.16)], x=x, z=2.0, sec=14)
        seg_cyl(p, 'dark', (x, y + 1.16, 2.0), (x, y + 1.24, 2.0), 0.01, 6); seg_cyl(p, 'dark', (x, y + 1.24, 2.0), (x, y + 1.24, 2.08), 0.008, 6)
    lathe(p, 'paper', [(0.0, y + 0.92), (0.045, y + 0.92), (0.05, y + 1.18), (0.0, y + 1.18)], x=0.2, z=1.95, sec=12)
    # balcao do fundo (a direita da porta) com chapa, rolo de salsicha e pia
    xa, xb = BDOOR[1] + 0.1, PART_X[0] - 0.02
    p.box('counter', xa, xb, y, y + 0.88, -IZ, -IZ + 0.6); p.box('ctop', xa - 0.01, xb, y + 0.88, y + 0.92, -IZ, -IZ + 0.63)
    p.cham('steel', xa + 0.05, xa + 0.65, y + 0.92, y + 1.0, -IZ + 0.05, -IZ + 0.55, 0.01); p.box('dark', xa + 0.08, xa + 0.62, y + 1.0, y + 1.004, -IZ + 0.08, -IZ + 0.5)
    for k in range(2): p.box('dark', xa + 0.2 + k * 0.25, xa + 0.26 + k * 0.25, y + 0.95, y + 0.99, -IZ + 0.548, -IZ + 0.57)
    hotdog_roller(p, xa + 1.0, y + 0.92, -IZ + 0.3)
    # geladeira de vidro e freezer horizontal
    q = fridge(); p.merge(q, rot_y(0, (-2.25, y, -IZ)))
    p.cham('enamel', -IX, -IX + 0.7, y, y + 0.86, -0.6, 0.6, 0.02); p.box('steel_d', -IX + 0.02, -IX + 0.68, y + 0.86, y + 0.88, -0.58, 0.58)
    p.box('chrome', -IX + 0.6, -IX + 0.66, y + 0.75, y + 0.78, -0.3, 0.3)
    popcorn_cart(p, -2.3, y, 1.0)
    # prateleiras na parede da divisoria com copos, caixas e guardanapos
    for yy in (y + 1.3, y + 1.7, y + 2.1):
        p.box('steel', PART_X[0] - 0.32, PART_X[0], yy - 0.02, yy, -1.6, 0.9)
        for k, z in enumerate(np.arange(-1.5, 0.85, 0.3)):
            m = ['paper', 'flag_b', 'food_y', 'paper', 'food_r', 'cream', 'paper', 'flag_r'][k % 8]
            if (k + int(yy * 10)) % 3 == 0: lathe(p, m, [(0.0, yy), (0.04, yy), (0.05, yy + 0.22), (0.0, yy + 0.22)], x=PART_X[0] - 0.16, z=z, sec=10)
            else: p.cham(m, PART_X[0] - 0.3, PART_X[0] - 0.04, yy, yy + 0.18 + 0.04 * (k % 2), z - 0.12, z + 0.12, 0.006)
    for yy in (y + 1.3, y + 1.7, y + 2.1):
        for z in (-1.55, 0.85): p.box('steel', PART_X[0] - 0.05, PART_X[0], yy - 0.15, yy - 0.02, z - 0.015, z + 0.015)
    # extintor e lixeira
    lathe(p, 'flag_r', [(0.0, y + 0.6), (0.07, y + 0.6), (0.07, y + 1.05), (0.04, y + 1.12), (0.0, y + 1.12)], x=-0.6, z=-IZ + 0.09, sec=14)
    p.box('steel_d', -0.64, -0.56, y + 0.95, y + 1.1, -IZ, -IZ + 0.02)
    lathe(p, 'steel_d', [(0.0, y), (0.18, y), (0.2, y + 0.7), (0.0, y + 0.7)], x=0.45, z=1.2, sec=16)
    return p
def menu_board():
    """Quadro do cardapio na fachada (so pictogramas): cachorro-quente, copo, pipoca e picole, com moldura e 2 lampadas."""
    p = Piece(); x0, x1, y0, y1 = 0.45, 2.45, 1.25, 2.25
    p.box('trim', x0, x1, y0, y1, 0.0, 0.04); p.box('board', x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, 0.04, 0.05)
    for k, (cx, cy) in enumerate(((0.95, 1.95), (1.95, 1.95), (0.95, 1.55), (1.95, 1.55))):
        def ex(g, mat, z0=0.05, z1=0.056):
            m = D._fix(trimesh.creation.extrude_polygon(g, z1 - z0)); m.apply_translation([0, 0, z0]); p.add(mat, m)
        if k == 0:
            ex(LineString([(cx - 0.22, cy), (cx + 0.22, cy)]).buffer(0.07), 'food_y'); ex(LineString([(cx - 0.2, cy), (cx + 0.2, cy)]).buffer(0.04), 'food_r', 0.056, 0.062)
        if k == 1:
            ex(Polygon([(cx - 0.13, cy + 0.17), (cx + 0.13, cy + 0.17), (cx + 0.09, cy - 0.17), (cx - 0.09, cy - 0.17)]), 'flag_r'); ex(sbox(cx + 0.02, cy + 0.17, cx + 0.05, cy + 0.3), 'flag_w')
        if k == 2:
            ex(Polygon([(cx - 0.14, cy + 0.08), (cx + 0.14, cy + 0.08), (cx + 0.1, cy - 0.17), (cx - 0.1, cy - 0.17)]), 'flag_w')
            for dx in (-0.1, 0.0, 0.1): ex(Point(cx + dx, cy + 0.12).buffer(0.065, 12), 'pop', 0.056, 0.062)
        if k == 3:
            ex(Point(cx, cy + 0.06).buffer(0.11, 16).union(sbox(cx - 0.11, cy - 0.06, cx + 0.11, cy + 0.06)), 'flag_b'); ex(sbox(cx - 0.02, cy - 0.22, cx + 0.02, cy - 0.06), 'wood')
        ex(Point(cx + 0.33, cy - 0.12).buffer(0.05, 12), 'food_y')
    for x in (0.9, 2.0):
        seg_cyl(p, 'steel_d', (x, y1 + 0.05, 0.0), (x, y1 + 0.18, 0.25), 0.012, 6)
        q = Piece(); lathe(q, 'steel_d', [(0.0, 0.0), (0.09, 0.0), (0.05, 0.1), (0.0, 0.11)], sec=14); q.cyl('lamp_glass', 0.06, -0.01, 0.0, 0, 0, 12)
        p.merge(q, tr(x, y1 + 0.1, 0.28))
    return p
def service_window():
    """Acabamento externo da janela de atendimento: balcao de inox com maos-francesas, porta de enrolar recolhida na caixa, guias
    laterais e toldo de chapa com faixas e lambrequim."""
    p = Piece(); a, b, ya, yb = SERV
    p.box('chrome', a - 0.1, b + 0.1, ya - 0.04, ya, 0.0, 0.38); p.box('chrome', a - 0.1, b + 0.1, ya - 0.09, ya - 0.04, 0.34, 0.38)
    for x in (a + 0.2, (a + b) / 2, b - 0.2): p.hull('steel_d', [(xx, y, z) for xx in (x - 0.015, x + 0.015) for (y, z) in ((ya - 0.04, 0.0), (ya - 0.04, 0.3), (ya - 0.35, 0.0), (ya - 0.32, 0.03))])
    for x in (a - 0.06, b + 0.02): p.box('alu', x, x + 0.04, ya, yb, 0.0, 0.06)
    p.box('alu', a - 0.1, b + 0.1, yb, yb + 0.3, 0.0, 0.24)
    # toldo
    y0, y1, d = yb + 0.65, yb + 0.35, 1.0
    p.hull('trim', [(x, y0, 0.0) for x in (a - 0.3, b + 0.3)] + [(x, y0 + 0.03, 0.0) for x in (a - 0.3, b + 0.3)] + [(x, y1, d) for x in (a - 0.3, b + 0.3)] + [(x, y1 + 0.03, d) for x in (a - 0.3, b + 0.3)])
    for k, x in enumerate(np.arange(a - 0.3, b + 0.3 - 0.01, 0.29)):
        if k % 2: p.hull('trim_w', [(xx, y0 + 0.03, 0.0) for xx in (x, x + 0.29)] + [(xx, y0 + 0.036, 0.0) for xx in (x, x + 0.29)] + [(xx, y1 + 0.03, d) for xx in (x, x + 0.29)] + [(xx, y1 + 0.036, d) for xx in (x, x + 0.29)])
    for k, x in enumerate(np.arange(a - 0.3, b + 0.3 - 0.01, 0.29)):
        p.box('trim' if k % 2 == 0 else 'trim_w', x, x + 0.29, y1 - 0.18, y1 + 0.03, d, d + 0.012)
    for s in (a - 0.25, b + 0.25): seg_cyl(p, 'steel_d', (s, y0 - 0.3, 0.0), (s, y1 + 0.01, d - 0.05), 0.012, 6)
    return p
def restroom():
    """Banheiro (sala de 1,8 x 2,25 m na metade +Z): vaso, pia de coluna com espelho, porta-papel, barra de apoio, secador de maos,
    lixeira e luminaria (pivo da cabine)."""
    p = Piece(); y = Y0; xr0, xr1, zr0, zr1 = PART_X[1], IX, RR_Z[1], IZ
    q = wc_low(); p.merge(q, rot_y(180, (1.55, y, zr1 - 0.008)))
    seg_cyl(p, 'chrome', (xr0 + 0.05, y + 0.8, zr1 - 0.9), (xr0 + 0.05, y + 0.8, zr1 - 0.25), 0.017, 8)
    for z in (zr1 - 0.9, zr1 - 0.25): seg_cyl(p, 'chrome', (xr0 + 0.008, y + 0.8, z), (xr0 + 0.05, y + 0.8, z), 0.012, 6)
    p.cham('chrome', xr0 + 0.008, xr0 + 0.13, y + 0.55, y + 0.7, zr1 - 1.1, zr1 - 0.95, 0.01)
    # pia de coluna e espelho na divisoria
    zs = zr0 + 0.7
    lathe(p, 'porcelain', [(0.07, y), (0.06, y + 0.4), (0.09, y + 0.7), (0.0, y + 0.7)], x=xr0 + 0.25, z=zs, sec=16)
    p.cham('porcelain', xr0 + 0.008, xr0 + 0.48, y + 0.7, y + 0.82, zs - 0.26, zs + 0.26, 0.03); p.cham('enamel', xr0 + 0.12, xr0 + 0.42, y + 0.815, y + 0.823, zs - 0.18, zs + 0.18, 0.004)
    seg_cyl(p, 'chrome', (xr0 + 0.06, y + 0.82, zs), (xr0 + 0.06, y + 0.95, zs), 0.014, 8); seg_cyl(p, 'chrome', (xr0 + 0.06, y + 0.95, zs), (xr0 + 0.16, y + 0.95, zs), 0.01, 8)
    p.box('mirror', xr0 + 0.008, xr0 + 0.014, y + 1.1, y + 1.75, zs - 0.25, zs + 0.25); p.box('chrome', xr0 + 0.008, xr0 + 0.02, y + 1.08, y + 1.1, zs - 0.27, zs + 0.27)
    p.cham('paint_w', xr0 + 0.008, xr0 + 0.12, y + 1.15, y + 1.45, zs - 0.62, zs - 0.4, 0.02)
    lathe(p, 'steel', [(0.0, y), (0.14, y), (0.15, y + 0.5), (0.0, y + 0.5)], x=xr1 - 0.25, z=zr1 - 0.25, sec=14)
    return p
def wc_low():
    """Vaso sanitario com caixa acoplada (pivo: centro de tras, piso; frente +Z)."""
    p = Piece()
    p.hull('porcelain', [(x, 0.0, z) for x in (-0.12, 0.12) for z in (0.12, 0.45)] + [(x, 0.38, z) for x in (-0.18, 0.18) for z in (0.1, 0.62)])
    p.cham('porcelain', -0.19, 0.19, 0.38, 0.41, 0.12, 0.66, 0.03); p.cham('paint_w', -0.18, 0.18, 0.41, 0.43, 0.14, 0.64, 0.02)
    p.cham('porcelain', -0.2, 0.2, 0.43, 0.82, 0.0, 0.18, 0.02); p.cham('porcelain', -0.21, 0.21, 0.82, 0.85, -0.005, 0.19, 0.01)
    p.box('chrome', 0.1, 0.16, 0.74, 0.76, 0.18, 0.21)
    return p
def press_box():
    """Cabine de transmissao: bancada corrida sob a janela, mesa de som, microfone de mesa, caixa de controle do placar com botoes,
    livro de pontuacao, radio, 3 cadeiras, prateleira, frigobar, ventilador, cabideiro e quadro de avisos (pivo da cabine)."""
    p = Piece(); y = F1 + 0.012; yt = y + 0.75
    p.box('ctop', -IX, IX, yt - 0.04, yt, 1.62, IZ); p.box('counter', -IX, IX, y, yt - 0.04, IZ - 0.06, IZ)
    for x in (-2.3, -0.9, 0.9, 2.3): p.box('counter', x - 0.02, x + 0.02, y, yt - 0.04, 1.7, IZ - 0.06)
    # mesa de som
    p.hull('dark', [(x, yt, z) for x in (-1.45, -0.75) for z in (1.75, 2.15)] + [(x, yt + 0.09, z) for x in (-1.45, -0.75) for z in (2.0, 2.15)] + [(x, yt + 0.03, 1.75) for x in (-1.45, -0.75)])
    for i in range(8):
        for j in range(3): p.cyl(['seg_on', 'chrome', 'chrome'][j], 0.01, yt + 0.035 + j * 0.02, yt + 0.06 + j * 0.02, -1.4 + i * 0.085, 1.85 + j * 0.09, 8)
    # microfone
    lathe(p, 'steel_d', [(0.0, yt), (0.07, yt), (0.06, yt + 0.02), (0.0, yt + 0.025)], x=-0.4, z=1.85, sec=14)
    seg_cyl(p, 'chrome', (-0.4, yt + 0.02, 1.85), (-0.4, yt + 0.22, 1.85), 0.006, 6); seg_cyl(p, 'chrome', (-0.4, yt + 0.22, 1.85), (-0.4, yt + 0.3, 1.97), 0.006, 6)
    p.sphere('steel_d', 0.03, -0.4, yt + 0.31, 1.99, 1)
    # controle do placar
    p.cham('paint_g', 0.2, 0.75, yt, yt + 0.08, 1.75, 2.1, 0.01)
    for i in range(5):
        for j in range(3): p.box(['flag_w', 'lamp_g', 'lamp_r'][j], 0.25 + i * 0.1, 0.31 + i * 0.1, yt + 0.08, yt + 0.095, 1.8 + j * 0.1, 1.86 + j * 0.1)
    seg_cyl(p, 'dark', (0.47, yt + 0.02, 2.1), (0.47, yt - 0.04, 2.2), 0.008, 6)
    # livro de pontuacao e lapis
    p.box('book_b' if 'book_b' in MATS else 'flag_b', 1.1, 1.5, yt, yt + 0.025, 1.75, 2.05); p.box('paper', 1.12, 1.48, yt + 0.025, yt + 0.03, 1.77, 2.03)
    seg_cyl(p, 'paint_y', (1.55, yt + 0.007, 1.8), (1.7, yt + 0.007, 1.95), 0.004, 6)
    # radio
    p.cham('steel_d', 1.9, 2.3, yt, yt + 0.16, 1.9, 2.05, 0.01); disc_z(p, 'chrome', 0.045, 2.05, 2.055, 2.0, yt + 0.08, 14)
    seg_cyl(p, 'chrome', (2.25, yt + 0.16, 1.95), (2.15, yt + 0.5, 1.95), 0.003, 4)
    # cadeiras
    for x in (-1.1, 0.4, 1.6):
        q = office_chair('vinyl_r'); p.merge(q, rot_y(180, (x, y, 1.1)))
    # prateleira, frigobar, ventilador, cabideiro, quadro de avisos
    p.box('wood', 0.6, 2.4, y + 1.6, y + 1.63, -IZ, -IZ + 0.3)
    for k, x in enumerate(np.arange(0.7, 2.3, 0.12)): p.box(['flag_b', 'flag_r', 'paper', 'paint_g'][k % 4], x, x + 0.09, y + 1.63, y + 1.9 - 0.03 * (k % 3), -IZ + 0.04, -IZ + 0.26)
    p.cham('enamel', 1.8, 2.3, y, y + 0.55, -IZ, -IZ + 0.5, 0.02); p.box('chrome', 2.22, 2.25, y + 0.3, y + 0.5, -IZ + 0.5, -IZ + 0.52)
    lathe(p, 'steel_d', [(0.0, y + 0.55), (0.1, y + 0.55), (0.08, y + 0.57), (0.0, y + 0.58)], x=2.05, z=-IZ + 0.25, sec=14)
    seg_cyl(p, 'steel_d', (2.05, y + 0.57, -IZ + 0.25), (2.05, y + 0.8, -IZ + 0.25), 0.01, 6)
    ring_y(p, 'steel', 0.16, 0.17, y + 0.78, y + 0.8, 2.05, -IZ + 0.3, 20)
    p.box('dkwood', 0.0, 0.5, y + 1.6, y + 1.68, -IZ, -IZ + 0.02)
    for x in (0.08, 0.25, 0.42): seg_cyl(p, 'brass', (x, y + 1.62, -IZ + 0.02), (x, y + 1.66, -IZ + 0.09), 0.008, 6)
    p.cham('helmet_b', 0.12, 0.38, y + 1.25, y + 1.6, -IZ + 0.02, -IZ + 0.08, 0.02)
    p.box('wood', -IX + 0.012, -IX + 0.03, y + 1.1, y + 1.8, -1.2, 0.0); p.box('mulch', -IX + 0.03, -IX + 0.034, y + 1.13, y + 1.77, -1.17, -0.03)
    for k, (z, yy, m) in enumerate(((-0.9, 1.6, 'paper'), (-0.4, 1.45, 'pad_y'), (-0.6, 1.3, 'paper'), (-0.2, 1.62, 'flag_b'))):
        xo = -IX + 0.034 + k * 0.004; p.box(m, xo, xo + 0.003, y + yy - 0.1, y + yy + 0.1, z - 0.12, z + 0.12)
    p.box('metal', -0.3, 0.3, YE - 0.2, YE - 0.17, -0.1, 0.1); p.box('lamp_glass', -0.28, 0.28, YE - 0.215, YE - 0.2, -0.08, 0.08)
    return p
# ============================================================================ placar, torres de luz, gaiola, galpao e acessorios
def seg7(p, x, y, s, z0, z1, lit=()):
    """Digito de 7 segmentos (apagado, so os segmentos 'lit' acesos): barras chanfradas sobre o painel."""
    w = 0.1 * s; L1 = 0.5 * s
    S = {'a': (x, y + 2 * L1, 1), 'g': (x, y + L1, 1), 'd': (x, y, 1), 'f': (x - L1 / 2, y + 1.5 * L1, 0), 'b': (x + L1 / 2, y + 1.5 * L1, 0),
         'e': (x - L1 / 2, y + 0.5 * L1, 0), 'c': (x + L1 / 2, y + 0.5 * L1, 0)}
    for k, (cx, cy, hz) in S.items():
        m = 'seg_on' if k in lit else 'seg_off'
        if hz: p.hull(m, [(cx - L1 / 2 + w / 2 + dx, cy + dy, z) for z in (z0, z1) for (dx, dy) in ((0, 0), (w / 2, w / 2), (w / 2, -w / 2), (L1 - w, 0), (L1 - w * 1.5, w / 2), (L1 - w * 1.5, -w / 2))])
        else: p.hull(m, [(cx + dx, cy - L1 / 2 + w / 2 + dy, z) for z in (z0, z1) for (dx, dy) in ((0, 0), (w / 2, w / 2), (-w / 2, w / 2), (0, L1 - w), (w / 2, L1 - w * 1.5), (-w / 2, L1 - w * 1.5))])
def scoreboard():
    """Placar do centro do campo: 2 colunas de perfil I com base de concreto, painel verde com moldura, 2 times (bandeirinhas de cor),
    6 entradas e total em digitos de segmentos apagados, lampadas de bola, strike e out, pictograma de bola no alto,
    chapeu de chapa, passarela de servico atras com escada de marinheiro (pivo: centro, chao; frente +Z)."""
    p = Piece(); w, y0, y1 = 7.2, 3.2, 6.8; d = 0.45
    for x in (-2.6, 2.6):
        p.box('steel_d', x - 0.15, x + 0.15, 0.0, y1, -0.6, -0.58); p.box('steel_d', x - 0.15, x + 0.15, 0.0, y1, -0.42, -0.4); p.box('steel_d', x - 0.01, x + 0.01, 0.0, y1, -0.58, -0.42)
        lathe(p, 'concrete', [(0.45, -0.3), (0.45, 0.1), (0.4, 0.15), (0.0, 0.15)], x=x, z=-0.5, sec=20)
    p.cham('board', -w / 2, w / 2, y0, y1, -0.4, 0.0, 0.02)
    a = sbox(-w / 2 - 0.08, y0 - 0.08, w / 2 + 0.08, y1 + 0.08).difference(sbox(-w / 2 + 0.06, y0 + 0.06, w / 2 - 0.06, y1 - 0.06))
    ext(p, 'paint_w', a, 0.0, 0.05)
    # linhas dos times: bandeira de cor + 6 entradas + total
    for r, (yy, m) in enumerate(((5.45, 'pad_b'), (4.55, 'pad_r'))):
        p.box(m, -3.3, -2.5, yy - 0.22, yy + 0.28, 0.0, 0.03); p.box('flag_w', -3.22, -2.58, yy - 0.04, yy + 0.1, 0.03, 0.034)
        for c in range(6):
            x = -2.0 + c * 0.66; p.box('board_k', x - 0.27, x + 0.27, yy - 0.3, yy + 0.36, 0.0, 0.02)
            seg7(p, x, yy - 0.22, 0.55, 0.02, 0.035, lit=())
        p.box('board_k', 2.25, 3.25, yy - 0.34, yy + 0.4, 0.0, 0.02)
        for dx in (-0.22, 0.22): seg7(p, 2.75 + dx, yy - 0.25, 0.6, 0.02, 0.035, lit=())
    # entradas: marcadores redondos em cima das colunas (sem numeros)
    for c in range(6): disc_z(p, 'flag_w', 0.06, 0.0, 0.012, -2.0 + c * 0.66, 6.15, 14)
    disc_z(p, 'flag_w', 0.09, 0.0, 0.012, 2.75, 6.15, 14)
    # bola, strike, out
    for g, (x0, n, m) in enumerate(((-2.6, 3, 'lamp_g'), (-0.3, 2, 'lamp_r'), (1.8, 2, 'lamp_r'))):
        p.box('board_k', x0 - 0.1, x0 + 0.42 * n + 0.1, 3.45, 3.95, 0.0, 0.02)
        for k in range(n):
            x = x0 + 0.21 + k * 0.42; disc_z(p, 'dark', 0.17, 0.02, 0.03, x, 3.7, 20)
            disc_z(p, m if k == 0 else 'seg_off', 0.13, 0.03, 0.045, x, 3.7, 20)
        for k in range(g + 1): p.box('flag_w', x0 - 0.06 + k * 0.08, x0 - 0.02 + k * 0.08, 4.05, 4.17, 0.0, 0.012)
    # pictograma de bola no alto e chapeu
    disc_z(p, 'board', 0.68, -0.25, -0.05, 0.0, y1 + 0.75, 32); disc_z(p, 'ball', 0.6, -0.05, 0.0, 0.0, y1 + 0.75, 32)
    for sx in (-1, 1):
        pts = [(sx * (0.32 + 0.12 * math.cos(t)), y1 + 0.75 + 0.45 * math.sin(t)) for t in np.linspace(-1.1, 1.1, 9)]
        for (u, v) in zip(pts[:-1], pts[1:]): p.seg('stitch', (u[0], u[1], 0.004), (v[0], v[1], 0.004), 0.03, 0.008)
        for (u, v) in pts[1:-1]: p.seg('stitch', (u - 0.05, v + 0.03, 0.008), (u + 0.05, v - 0.03, 0.008), 0.018, 0.006)
    p.box('steel_d', -0.12, 0.12, y1, y1 + 0.2, -0.2, -0.06)
    p.box('paint_g', -w / 2 - 0.15, -0.7, y1 + 0.08, y1 + 0.14, -0.5, 0.25); p.box('paint_g', 0.7, w / 2 + 0.15, y1 + 0.08, y1 + 0.14, -0.5, 0.25)
    for x in np.linspace(-w / 2 + 0.3, w / 2 - 0.3, 5): p.box('steel_d', x - 0.05, x + 0.05, y1 + 0.04, y1 + 0.078, -0.4, 0.2)
    # passarela e escada atras
    p.box('galv', -w / 2, w / 2, y0 - 0.3, y0 - 0.25, -1.4, -0.62)
    for x in np.linspace(-w / 2 + 0.05, w / 2 - 0.05, 9): seg_cyl(p, 'galv', (x, y0 - 0.25, -1.36), (x, y0 + 0.8, -1.36), 0.018, 6)
    for y in (y0 + 0.4, y0 + 0.8): seg_cyl(p, 'galv', (-w / 2 + 0.05, y, -1.36), (w / 2 - 0.05, y, -1.36), 0.02, 8)
    for x in (-2.6, 2.6): p.hull('steel_d', [(x + dx, y, z) for dx in (-0.04, 0.04) for (y, z) in ((y0 - 0.3, -0.6), (y0 - 0.3, -1.4), (y0 - 0.35, -1.4), (y0 - 1.0, -0.62))])
    for x in (2.25, 2.75): seg_cyl(p, 'galv', (x, 0.0, -0.75), (x, y0 + 0.8, -0.75), 0.02, 8)
    for y in np.arange(0.3, y0 - 0.2, 0.3): seg_cyl(p, 'galv', (2.25, y, -0.75), (2.75, y, -0.75), 0.013, 6)
    p.box('steel_d', 1.8, 2.3, 1.2, 1.9, -0.75, -0.6)
    return p
def light_tower(h=18.0):
    """Torre de iluminacao: poste conico galvanizado de 8 lados com flange e chumbadores, degraus de grampo, caixa de disjuntores,
    eletroduto, cruzeta de treliça com 2 fileiras de 3 refletores mirando +Z (para baixo 35 graus) e plataforma (pivo: pe)."""
    p = Piece(); r0, r1 = 0.3, 0.13
    lathe(p, 'concrete', [(0.7, -0.3), (0.7, 0.35), (0.62, 0.42), (0.0, 0.42)], sec=24)
    lathe(p, 'galv', [(0.42, 0.42), (0.42, 0.47), (r0, 0.47), (r1, h), (0.0, h)], sec=8)
    for k in range(8): a = k * math.pi / 4 + math.pi / 8; p.cyl('steel_d', 0.022, 0.42, 0.55, 0.36 * math.cos(a), 0.36 * math.sin(a), 6)
    for i, y in enumerate(np.arange(2.5, h - 0.6, 0.38)):
        rr = r0 + (r1 - r0) * (y - 0.47) / (h - 0.47)
        q = Piece(); seg_cyl(q, 'galv', (rr - 0.01, 0.0, -0.05), (rr + 0.12, 0.0, -0.05), 0.01, 6); seg_cyl(q, 'galv', (rr - 0.01, 0.0, 0.05), (rr + 0.12, 0.0, 0.05), 0.01, 6)
        seg_cyl(q, 'galv', (rr + 0.12, 0.0, -0.06), (rr + 0.12, 0.0, 0.06), 0.01, 6); p.merge(q, rot_y(90 + (35 if i % 2 else -35), (0, y, 0)))
    p.box('paint_w', -0.22, 0.22, 1.2, 1.9, r0 + 0.02, r0 + 0.25); p.box('dark', -0.03, 0.03, 1.45, 1.65, r0 + 0.25, r0 + 0.28)
    seg_cyl(p, 'galv', (0.12, 0.0, r0 + 0.04), (0.12, 1.2, r0 + 0.1), 0.03, 8)
    # cruzeta: 2 vigas, montantes e 6 refletores
    yc = h - 0.2; L1 = 2.6
    for y in (yc - 0.9, yc + 0.6):
        seg_cyl(p, 'galv', (-L1 / 2, y, 0.25), (L1 / 2, y, 0.25), 0.04, 8); seg_cyl(p, 'galv', (-L1 / 2, y, 0.05), (L1 / 2, y, 0.05), 0.03, 8)
    for x in np.linspace(-L1 / 2, L1 / 2, 5): seg_cyl(p, 'galv', (x, yc - 0.9, 0.25), (x, yc + 0.6, 0.25), 0.03, 6)
    seg_cyl(p, 'galv', (-L1 / 2, yc - 0.9, 0.25), (L1 / 2, yc + 0.6, 0.25), 0.025, 6)
    p.box('galv', -L1 / 2, L1 / 2, yc - 1.12, yc - 1.08, -0.4, 0.15)
    for x in np.linspace(-L1 / 2, L1 / 2, 6): seg_cyl(p, 'galv', (x, yc - 1.08, -0.38), (x, yc - 0.1, -0.38), 0.015, 6)
    seg_cyl(p, 'galv', (-L1 / 2, yc - 0.1, -0.38), (L1 / 2, yc - 0.1, -0.38), 0.02, 6)
    for row, y in enumerate((yc - 0.9 + 0.05, yc + 0.6 - 0.05)):
        for x in (-0.85, 0.0, 0.85):
            q = Piece()
            lathe(q, 'steel_d', [(0.0, 0.0), (0.3, 0.0), (0.33, 0.06), (0.33, 0.24), (0.36, 0.26), (0.36, 0.3), (0.0, 0.3)], sec=18)
            lathe(q, 'lamp_glass', [(0.31, 0.3), (0.0, 0.305)], sec=18)
            seg_cyl(q, 'galv', (0.0, -0.05, 0.0), (0.0, -0.25, 0.0), 0.03, 6)
            M = tr(x, y, 0.55) @ trimesh.transformations.rotation_matrix(math.radians(90 - 35), [1, 0, 0]); p.merge(q, M)
    p.box('paint_w', -0.25, 0.25, yc - 2.0, yc - 1.4, -0.32, -0.12)
    return p
def batting_cage():
    """Gaiola de rebatidas (16 x 3,6 x 3,6 m): portico de tubo a cada 3,2 m, rede de malha nas laterais, no teto e no fundo,
    cortina na entrada, grama sintetica com base e tapete do batedor, tela L de protecao, maquina de arremesso e balde de bolas
    (pivo: meio da entrada, chao; a gaiola corre para -Z)."""
    p = Piece(); hw, h, Ln = 1.8, 3.6, 16.0
    ext_y(p, 'grass2', sbox(-hw, -Ln, hw, 0.0), 0.0, 0.015)
    ext_y(p, 'clay', sbox(-0.8, -1.8, 0.8, -0.2), 0.015, 0.02); p.box('paint_w', -0.21, 0.21, 0.02, 0.026, -1.25, -0.82)
    for z in np.linspace(0.0, -Ln, 6):
        for x in (-hw, hw): seg_cyl(p, 'galv', (x, -0.3, z), (x, h, z), 0.04, 10)
        seg_cyl(p, 'galv', (-hw, h, z), (hw, h, z), 0.035, 10)
    for x in (-hw, hw): seg_cyl(p, 'galv', (x, h, 0.0), (x, h, -Ln), 0.03, 8)
    def net(segs_h, segs_v, M, off=0.0):
        q = Piece(); q.add('net', wires_mesh(segs_h, 0.006, off, off + 0.003)); q.add('net', wires_mesh(segs_v, 0.006, off + 0.003, off + 0.006)); p.merge(q, M)
    st = 0.15
    for sx in (-1, 1):
        segs_h = [((0.0, y), (Ln, y)) for y in np.arange(0.1, h - 0.05, st)]; segs_v = [((x, 0.05), (x, h - 0.05)) for x in np.arange(0.05, Ln, st)]
        M = rot_y(90, (sx * (hw - 0.05), 0.0, 0.0)); net(segs_h, segs_v, M)
    segs_h = [((-hw + 0.05, z), (hw - 0.05, z)) for z in np.arange(0.05, Ln, st)]; segs_v = [((x, 0.05), (x, Ln - 0.05)) for x in np.arange(-hw + 0.1, hw - 0.05, st)]
    M = trimesh.transformations.rotation_matrix(math.radians(90), [1, 0, 0]); M[:3, 3] = [0, h - 0.06, 0]; net(segs_h, segs_v, M)
    segs_h = [((-hw + 0.05, y), (hw - 0.05, y)) for y in np.arange(0.1, h - 0.05, st)]; segs_v = [((x, 0.05), (x, h - 0.05)) for x in np.arange(-hw + 0.1, hw - 0.05, st)]
    net(segs_h, segs_v, tr(0, 0, -Ln + 0.05))
    # cortina da entrada so na metade
    segs_h = [((0.4, y), (hw - 0.05, y)) for y in np.arange(0.3, h - 0.05, st)]; segs_v = [((x, 0.3), (x, h - 0.05)) for x in np.arange(0.45, hw - 0.05, st)]
    net(segs_h, segs_v, tr(0, 0, -0.06))
    # tela L
    zl = -11.5
    for (a, b) in (((-0.9, 0.0), (0.9, 0.0)), ((-0.9, 0.0), (-0.9, 2.1)), ((0.9, 0.0), (0.9, 1.1)), ((-0.9, 2.1), (-0.1, 2.1)), ((-0.1, 2.1), (-0.1, 1.1)), ((-0.1, 1.1), (0.9, 1.1))):
        seg_cyl(p, 'galv', (a[0], a[1] + 0.015, zl), (b[0], b[1] + 0.015, zl), 0.025, 8)
    segs = [((x, 0.05), (x, 2.08 if x < -0.1 else 1.08)) for x in np.arange(-0.85, 0.88, 0.1)]
    segs2 = [((-0.88, y), (-0.12 if y > 1.1 else 0.88, y)) for y in np.arange(0.1, 2.08, 0.1)]
    q = Piece(); q.add('net', wires_mesh(segs, 0.008, -0.003, 0.0)); q.add('net', wires_mesh(segs2, 0.008, 0.0, 0.003)); p.merge(q, tr(0, 0.015, zl))
    for x in (-0.9, 0.9): seg_cyl(p, 'galv', (x, 0.04, zl), (x, 0.04, zl - 0.5), 0.02, 6)
    # maquina de arremesso
    zm = -13.2
    for a in (0.0, 120.0, 240.0):
        ax = math.radians(a); seg_cyl(p, 'steel_d', (0.0, 0.85, zm), (0.55 * math.sin(ax), 0.015, zm + 0.55 * math.cos(ax)), 0.02, 6)
    p.cham('paint_y', -0.25, 0.25, 0.85, 1.15, zm - 0.2, zm + 0.2, 0.03)
    for s in (-1, 1): disc_x(p, 'rubber', 0.2, s * 0.1 - 0.05, s * 0.1 + 0.05, 1.05, zm + 0.12, 18)
    seg_cyl(p, 'steel', (0.0, 1.15, zm), (0.0, 1.5, zm - 0.1), 0.06, 10); lathe(p, 'steel', [(0.0, 1.5), (0.22, 1.62), (0.24, 1.8), (0.0, 1.8)], z=zm - 0.12, sec=16)
    for (x, z) in ((0.05, 0.0), (-0.06, 0.05), (0.0, -0.08)): p.sphere('ball', 0.037, x, 1.78, zm - 0.12 + z, 1)
    return p
def shed():
    """Galpao de equipamentos (4 x 3,2 m): base de concreto, paredes de chapa de madeira com mata-juntas, quinas, porta de
    tabuas em Z, janelinha com grade, telhado de 2 aguas de chapa ondulada com cumeeira e beiral (pivo: centro, chao; porta +Z)."""
    p = Piece(); hx, hz, h = 2.0, 1.6, 2.4; t = 0.12; ya = 0.12
    ext_y(p, 'concrete', sbox(-hx, -hz, hx, hz), 0.0, ya)
    door = (-0.55, 0.55)
    wall2(p, 'x', -hx, hx, hz, hz - t, [(door[0], door[1], ya, ya + DH)], ya, h, 'siding', 'wood')
    wall2(p, 'x', -hx, hx, -hz, -hz + t, [], ya, h, 'siding', 'wood')
    for s in (-1, 1):
        a, b = sorted((s * hx, s * (hx - t))); wall2(p, 'z', -hz + t, hz - t, a, b, [(-0.4, 0.4, 1.3, 1.9)] if s > 0 else [], ya, h, 'siding', 'wood')
    # mata-juntas e quinas
    for x in np.arange(-hx + 0.3, hx - 0.1, 0.4):
        for zf, sg in ((hz, 1), (-hz, -1)):
            if zf > 0 and door[0] - 0.12 < x < door[1] + 0.12: continue
            a, b = sorted((zf, zf + sg * 0.018)); p.box('trim_w', x - 0.03, x + 0.03, ya, h, a, b)
    for z in np.arange(-hz + 0.3, hz - 0.1, 0.4):
        for xf, sg in ((hx, 1), (-hx, -1)):
            if xf > 0 and -0.52 < z < 0.52: continue
            a, b = sorted((xf, xf + sg * 0.018)); p.box('trim_w', a, b, ya, h, z - 0.03, z + 0.03)
    for sx in (-1, 1):
        for sz in (-1, 1):
            a, b = sorted((sx * hx, sx * (hx + 0.025))); c, d = sorted((sz * (hz - 0.1), sz * (hz + 0.025))); p.box('trim', a, b, ya, h, c, d)
            a, b = sorted((sx * (hx - 0.1), sx * hx)); c, d = sorted((sz * hz, sz * (hz + 0.025))); p.box('trim', a, b, ya, h, c, d)
    p.box('trim', door[0] - 0.09, door[0], ya, ya + DH + 0.09, hz, hz + 0.022); p.box('trim', door[1], door[1] + 0.09, ya, ya + DH + 0.09, hz, hz + 0.022)
    p.box('trim', door[0], door[1], ya + DH, ya + DH + 0.09, hz, hz + 0.022)
    # janelinha com grade (lado +X)
    p.box('glass', hx - t / 2 - 0.002, hx - t / 2 + 0.002, 1.3, 1.9, -0.4, 0.4)
    for z in np.linspace(-0.3, 0.3, 4): seg_cyl(p, 'iron', (hx + 0.03, 1.3, z), (hx + 0.03, 1.9, z), 0.01, 6)
    p.box('trim', hx, hx + 0.03, 1.22, 1.3, -0.48, 0.48); p.box('trim', hx, hx + 0.02, 1.9, 1.98, -0.48, 0.48)
    for z in (-0.48, 0.4): p.box('trim', hx, hx + 0.02, 1.3, 1.9, z, z + 0.08)
    # telhado de 2 aguas (cumeeira em X)
    ov = 0.3; rise = 0.7; yr = h + rise
    for sz in (-1, 1):
        q = Piece()
        q.hull('ceil', [(x, h - 0.02, sz * (hz + ov)) for x in (-hx - ov, hx + ov)] + [(x, yr - 0.02, 0.0) for x in (-hx - ov, hx + ov)] + [(x, h, sz * (hz + ov)) for x in (-hx - ov, hx + ov)] + [(x, yr, 0.0) for x in (-hx - ov, hx + ov)])
        for x in np.arange(-hx - ov + 0.08, hx + ov - 0.02, 0.16):
            q.hull('galv', [(xx, yy, z) for (z, y) in ((sz * (hz + ov), h), (0.0, yr)) for (xx, yy) in ((x - 0.05, y), (x + 0.05, y), (x - 0.025, y + 0.03), (x + 0.025, y + 0.03))])
        p.merge(q)
    p.hull('galv', [(x, yr + 0.0, z) for x in (-hx - ov - 0.02, hx + ov + 0.02) for z in (-0.2, 0.2)] + [(x, yr + 0.06, 0.0) for x in (-hx - ov - 0.02, hx + ov + 0.02)])
    for sx in (-1, 1):
        x = sx * (hx + ov + 0.01)
        p.hull('trim', [(x + dx, y, z) for dx in (-0.015, 0.015) for (y, z) in ((h - 0.1, -(hz + ov)), (h, -(hz + ov)), (yr + 0.03, 0.0), (yr - 0.07, 0.0))])
        p.hull('trim', [(x + dx, y, z) for dx in (-0.015, 0.015) for (y, z) in ((h - 0.1, hz + ov), (h, hz + ov), (yr + 0.03, 0.0), (yr - 0.07, 0.0))])
    # empena: fecha o triangulo entre a parede e o telhado
    for sx in (-1, 1):
        x0 = sx * hx; a, b = sorted((x0, x0 - sx * t))
        p.hull('siding', [(x, y, z) for x in (a, b) for (y, z) in ((h, -hz), (h, hz), (h + rise * (1 - hz / (hz + ov)) - 0.03, 0.0))])
    return p
def door_planks(w=1.08, h=2.1, t=0.045):
    """Porta de tabuas verticais com travessas em Z, dobradicas de ferro e ferrolho (pivo: dobradica, embaixo)."""
    p = Piece(); n = 7
    for k in range(n): p.cham('door_g', k * w / n + 0.002, (k + 1) * w / n - 0.002, 0.0, h, -t / 2, t / 2, 0.004)
    for y in (0.25, h - 0.25): p.box('door_g', 0.06, w - 0.06, y - 0.07, y + 0.07, t / 2, t / 2 + 0.025)
    a, b = np.array([0.1, 0.32]), np.array([w - 0.1, h - 0.32]); p.seg('door_g', (a[0], a[1], t / 2 + 0.012), (b[0], b[1], t / 2 + 0.012), 0.13, 0.024)
    for y in (0.25, h - 0.25): p.box('iron', -0.01, 0.4, y - 0.025, y + 0.025, t / 2 + 0.025, t / 2 + 0.03)
    p.box('iron', w - 0.2, w - 0.06, 1.02, 1.08, t / 2 + 0.025, t / 2 + 0.035); p.box('iron', w - 0.08, w - 0.05, 0.98, 1.12, t / 2 + 0.035, t / 2 + 0.06)
    return p
def rake(p, x, z, ry, lean=12.0):
    """Rastelo de saibro (cabo e cabeca larga de aluminio) encostado."""
    q = Piece(); seg_cyl(q, 'wood', (0, 0.12, 0), (0, 1.75, 0), 0.016, 8); q.box('alu', -0.45, 0.45, 0.02, 0.14, -0.02, 0.02)
    for xx in np.linspace(-0.4, 0.4, 12): q.box('alu', xx - 0.006, xx + 0.006, 0.0, 0.03, -0.02, 0.02)
    M = rot_y(ry, (x, 0.0, z)) @ trimesh.transformations.rotation_matrix(math.radians(lean), [1, 0, 0]); p.merge(q, M)
def shed_stuff():
    """Dentro do galpao: carrinho de marcar cal, sacos de cal empilhados, estante com bases e cones, mangueira enrolada, carrinho de mao
    e 2 rastelos (pivo do galpao)."""
    p = Piece(); y = 0.12
    # carrinho de cal
    xc, zc = -1.2, 0.6
    p.hull('paint_y', [(xc + dx, y + yy, zc + dz) for dx in (-0.18, 0.18) for dz in (-0.25, 0.25) for yy in (0.15, 0.5)]); lathe(p, 'paper', [(0.0, y + 0.5), (0.16, y + 0.5), (0.16, y + 0.51), (0.0, y + 0.51)], x=xc, z=zc, sec=14)
    for s in (-1, 1): disc_x(p, 'rubber', 0.13, xc + s * 0.2 - 0.025, xc + s * 0.2 + 0.025, y + 0.13, zc - 0.1, 16)
    seg_cyl(p, 'steel', (xc - 0.15, y + 0.45, zc + 0.2), (xc - 0.15, y + 0.95, zc + 0.75), 0.012, 6); seg_cyl(p, 'steel', (xc + 0.15, y + 0.45, zc + 0.2), (xc + 0.15, y + 0.95, zc + 0.75), 0.012, 6)
    seg_cyl(p, 'rubber', (xc - 0.18, y + 0.95, zc + 0.75), (xc + 0.18, y + 0.95, zc + 0.75), 0.018, 8)
    # sacos de cal
    for k in range(5):
        x = -1.55 + (k % 3) * 0.5; yy = y + (k // 3) * 0.13; p.cham('paper', x - 0.22, x + 0.22, yy, yy + 0.13, -1.35, -0.95, 0.04)
    # estante com bases e cones
    x0, x1 = 0.3, 1.8
    for yy in (y + 0.4, y + 1.0, y + 1.6): p.box('wood', x0, x1, yy - 0.025, yy, -1.48, -1.1)
    for x in (x0, x1 - 0.04): p.box('wood', x, x + 0.04, y, y + 1.65, -1.48, -1.1)
    for k in range(3): p.cham('paint_w', x0 + 0.1 + k * 0.45, x0 + 0.48 + k * 0.45, y + 0.4, y + 0.47, -1.45, -1.12, 0.02)
    for k in range(4): lathe(p, 'flag_o', [(0.12, y + 1.0), (0.12, y + 1.02), (0.02, y + 1.3), (0.0, y + 1.3)], x=x0 + 0.2 + k * 0.38, z=-1.3, sec=12)
    # mangueira e carrinho de mao
    q = Piece(); m = trimesh.creation.annulus(r_min=0.14, r_max=0.24, height=0.08, sections=24); q.add('food_g', m)
    p.merge(q, tr(1.9, 1.2, 0.7) @ trimesh.transformations.rotation_matrix(math.radians(90), [0, 1, 0]))
    p.box('steel_d', 1.82, 1.88, 1.05, 1.35, 0.6, 0.8)
    p.hull('flag_r', [(x, y + yy, z) for (x, yy) in ((0.3, 0.3), (0.85, 0.3), (0.2, 0.6), (0.95, 0.6)) for z in (-0.1, 0.45)])
    disc_x(p, 'rubber', 0.18, 0.55, 0.62, y + 0.18, 0.8, 16)
    for x in (0.32, 0.86): seg_cyl(p, 'steel', (x, y + 0.35, 0.8), (x, y + 0.55, -0.6), 0.015, 6)
    rake(p, 1.7, 1.42, 180); rake(p, 1.2, 1.42, 180, 9)
    return p
def flagpole(h=8.0):
    """Mastro de aluminio com base de concreto, polia, cordas, cunho e bandeira da liga (verde com faixas amarelas e bola nos 2 lados, sem texto)."""
    p = Piece()
    lathe(p, 'concrete', [(0.35, -0.3), (0.35, 0.1), (0.3, 0.15), (0.0, 0.15)], sec=20)
    lathe(p, 'alu', [(0.07, 0.15), (0.06, 0.4), (0.045, h), (0.0, h)], sec=14); p.sphere('gold', 0.08, 0.0, h + 0.07, 0.0, 1)
    p.cyl('alu', 0.06, h - 0.1, h - 0.02, 0.0, 0.0, 12)
    seg_cyl(p, 'paper', (0.06, 1.2, 0.0), (0.05, h - 0.05, 0.0), 0.004, 4); seg_cyl(p, 'paper', (0.06, 1.2, 0.03), (0.05, h - 0.05, 0.03), 0.004, 4)
    p.box('alu', 0.05, 0.08, 1.15, 1.3, -0.02, 0.05)
    fw, fh = 1.8, 1.1; y1 = h - 0.15
    p.box('pad_g', 0.07, 0.07 + fw, y1 - fh, y1, -0.004, 0.004)
    for sz in (-1, 1):
        a, b = sorted((sz * 0.004, sz * 0.008))
        p.box('pad_y', 0.07, 0.07 + fw, y1 - 0.12, y1 - 0.06, a, b); p.box('pad_y', 0.07, 0.07 + fw, y1 - fh + 0.06, y1 - fh + 0.12, a, b)
        disc_z(p, 'ball', 0.3, a, b, 0.07 + fw / 2, y1 - fh / 2, 28)
        for sx in (-1, 1):
            pts = [(0.07 + fw / 2 + sx * (0.16 + 0.07 * math.cos(t)), y1 - fh / 2 + 0.24 * math.sin(t)) for t in np.linspace(-1.1, 1.1, 7)]
            c, d = sorted((sz * 0.008, sz * 0.011))
            for (u, v) in zip(pts[:-1], pts[1:]): p.seg('stitch', (u[0], u[1], (c + d) / 2), (v[0], v[1], (c + d) / 2), 0.018, 0.003)
    return p
def picnic_table():
    """Mesa de piquenique de tabuas com bancos presos em pes de aco em A (pivo: centro, chao)."""
    p = Piece(); L1 = 1.8
    for k in range(5): p.cham('bench_w', -L1 / 2, L1 / 2, 0.72, 0.76, -0.4 + k * 0.16, -0.26 + k * 0.16, 0.006)
    for s in (-1, 1):
        for k in range(2): p.cham('bench_w', -L1 / 2, L1 / 2, 0.42, 0.46, s * 0.55 - 0.12 + k * 0.13, s * 0.55 - 0.01 + k * 0.13, 0.006)
    for x in (-0.7, 0.7):
        for s in (-1, 1): seg_cyl(p, 'steel_d', (x, 0.0, s * 0.75), (x, 0.72, s * 0.08), 0.025, 8)
        p.box('steel_d', x - 0.025, x + 0.025, 0.38, 0.42, -0.75, 0.75)
    return p
def bike_rack():
    """Bicicletario de arcos de tubo galvanizado sobre trilho (pivo: centro, chao)."""
    p = Piece()
    for x in np.linspace(-1.2, 1.2, 5):
        pts = [(x, 0.0, -0.3)] + [(x, 0.55 + 0.25 * math.sin(t), -0.25 * math.cos(t)) for t in np.linspace(0, math.pi, 9)] + [(x, 0.0, 0.3)]
        for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'galv', a, b, 0.024, 8)
    for z in (-0.3, 0.3): p.box('galv', -1.3, 1.3, 0.0, 0.05, z - 0.04, z + 0.04)
    return p
def fountain():
    """Bebedouro de coluna de concreto com bacia de inox e degrau para criancas (pivo: centro, chao; uso pela frente +Z)."""
    p = Piece(); lathe(p, 'conc_s', [(0.22, 0.0), (0.2, 0.05), (0.14, 0.1), (0.12, 0.85), (0.0, 0.85)], sec=20)
    lathe(p, 'chrome', [(0.0, 0.85), (0.2, 0.85), (0.22, 0.95), (0.2, 0.96), (0.16, 0.9), (0.0, 0.9)], sec=20)
    p.cyl('chrome', 0.012, 0.9, 0.98, 0.0, 0.05, 8); p.box('chrome', -0.03, 0.03, 0.86, 0.9, 0.2, 0.24)
    p.cham('conc_s', -0.3, 0.3, 0.0, 0.2, 0.25, 0.55, 0.02)
    return p
def scorer_table():
    """Mesa dobravel com 2 cadeiras do apontador e uma caixa termica (pivo: centro, chao)."""
    p = Piece(); p.cham('paint_w', -0.9, 0.9, 0.72, 0.76, -0.38, 0.38, 0.01)
    for x in (-0.75, 0.75):
        for s in (-1, 1): seg_cyl(p, 'steel', (x, 0.0, s * 0.3), (x, 0.72, s * 0.05), 0.014, 6)
    for x in (-0.45, 0.45):
        p.box('steel_d', x - 0.2, x + 0.2, 0.44, 0.47, -0.88, -0.5); p.box('steel_d', x - 0.2, x + 0.2, 0.47, 0.85, -0.92, -0.89)
        for (dx, dz) in ((-0.18, -0.52), (0.18, -0.52), (-0.18, -0.88), (0.18, -0.88)): seg_cyl(p, 'steel', (x + dx, 0.0, dz), (x + dx, 0.44, dz), 0.011, 6)
    p.cham('cooler_b', 0.55, 0.95, 0.0, 0.35, 0.45, 0.75, 0.03); p.cham('paint_w', 0.54, 0.96, 0.35, 0.4, 0.44, 0.76, 0.02)
    p.box('paper', -0.3, 0.1, 0.76, 0.775, -0.2, 0.1)
    return p
def wheel_stop2(): return wheel_stop()
def bush_row(n=4, r=0.55):
    p = Piece()
    for k in range(n):
        q = bush(r, 3 + k); p.merge(q, tr((k - (n - 1) / 2) * r * 1.6, 0.0, 0.0))
    return p
# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def put_f(frame, n, lx, ly, lz, lry=0.0, tags=(), door=None):
    """Peca numa moldura local (pivo (x, z), giro ry): usada na cabine, nos bancos de reservas e nas arquibancadas."""
    (fx, fz), fr = frame; a = math.radians(fr)
    put(n, fx + math.cos(a) * lx + math.sin(a) * lz, ly, fz - math.sin(a) * lx + math.cos(a) * lz, fr + lry, tags, door)
CAB = (BC, BRY)
DUGS = {1: (lp(sum(DUG) / 2, OF, 1), -135.0), -1: (lp(sum(DUG) / 2, OF, -1), 135.0)}
pieces = {
    'site': site(), 'field': field(), 'chalk': chalk(), 'home_plate': home_plate(), 'base': base_bag(), 'mound': mound(), 'on_deck': on_deck_mat(),
    'outfield_fence': outfield_fence(), 'side_fence_1': side_fence(1), 'side_fence_3': side_fence(-1), 'backstop': backstop(), 'foul_pole': foul_pole(),
    'gate_field': field_gate(1.18, 1.18),
    'dugout_b': dugout('roof_b'), 'dugout_r': dugout('roof_r'), 'dugout_bench': dugout_bench(5.2), 'helmet_rack': helmet_rack(), 'bat_rack': bat_rack(),
    'water_cooler': water_cooler(), 'ball_bucket': ball_bucket(), 'bleacher': bleacher(7.0),
    'cabin_ground': cabin_shell(0), 'cabin_slab': cabin_slab(), 'cabin_upper': cabin_shell(1), 'cabin_roof': hip_roof(), 'cabin_stair': cabin_stair(),
    'concession': concession(), 'menu_board': menu_board(), 'service_window': service_window(), 'restroom_a': restroom(),
    'restroom_b': mirrored(restroom(), np.diag([1.0, 1.0, -1.0, 1.0])), 'press_box': press_box(), 'door_service': door_metal(0.88, DH - 0.012, 0.045),
    'scoreboard': scoreboard(), 'light_tower': light_tower(18.0), 'batting_cage': batting_cage(), 'shed': shed(), 'door_shed': door_planks(1.08, DH - 0.012),
    'shed_stuff': shed_stuff(), 'flagpole': flagpole(8.0), 'picnic_table': picnic_table(), 'bike_rack': bike_rack(), 'fountain': fountain(),
    'scorer_table': scorer_table(), 'park_bench': park_bench(1.8), 'trash_can': trash_can(), 'lamp_post': lamp_post(4.2), 'wheel_stop': wheel_stop(),
    'tree': tree(7.0, 2.3, 'leaf', 2), 'tree_b': tree(5.5, 1.8, 'leaf2', 5), 'bush_row': bush_row(4, 0.55),
    'car_sedan_r': car('car_r', 'sedan'), 'car_wagon_b': car('car_b', 'wagon'), 'car_hatch_y': car('car_y', 'hatch'), 'car_pickup_s': car('car_s', 'pickup'),
    'player_scale_ref': player_ref()}

# ============================================================================ montagem
F = ['campo']; G = ['predio']; J = ['rua']
def fl(k): return G + [f'floor{k}']
put('site', 0, 0, 0, 0, J); put('field', 0, 0, 0, 0, F); put('chalk', 0, 0, 0, 0, F)
put('home_plate', 0, 0, 0, 0, F); put('mound', 0, 0, -RUB, 0, F)
put('base', HB - 0.269, 0, -HB, 45, F); put('base', 0, 0, -2 * HB, 45, F); put('base', -HB + 0.269, 0, -HB, 45, F)
for sd in (1, -1): x, z = lp(4.5, 5.0, sd); put('on_deck', x, 0, z, 0, F)
put('outfield_fence', 0, 0, 0, 0, F); put('side_fence_1', 0, 0, 0, 0, F); put('side_fence_3', 0, 0, 0, 0, F); put('backstop', 0, 0, 0, 0, F)
r = RF + 0.12; put('foul_pole', r / SQ2, 0, -r / SQ2, 135, F); put('foul_pole', -r / SQ2, 0, -r / SQ2, 45, F)
x, z = lp(GATE_S[0] + 0.01, OF, 1); put('gate_field', x, 0.0, z, 45, F, door=90)
x, z = lp(GATE_S[0] + 0.01, OF, -1); put('gate_field', x, 0.0, z, 135, F, door=-90)
# bancos de reservas
for sd, roof in ((1, 'dugout_b'), (-1, 'dugout_r')):
    fr = DUGS[sd]; put_f(fr, roof, 0, 0, 0, 0, G)
    put_f(fr, 'dugout_bench', -0.5, 0.1, -DUGD + 0.2, 0, G)
    put_f(fr, 'helmet_rack', -DGX + 0.2, 0.1, -1.15, 90, G); put_f(fr, 'bat_rack', DGX - 0.2, 0.1, -0.85, -90, G)
    put_f(fr, 'water_cooler', 1.3, 0.1, -0.5, 0, G); put_f(fr, 'ball_bucket', -1.4, 0.1, -0.55, 0, G); put_f(fr, 'trash_can', 0.4, 0.1, -DUGD + 0.85, 0, G)
    put_f(fr, 'door_service', 2.2 + 0.01, 0.1, -DUGD + 0.1, 0, G, door=-90)
# arquibancadas
for sd in (1, -1):
    x, z = lp(sum(BLS) / 2, OF + 0.6, sd); put('bleacher', x, 0, z, -135 if sd > 0 else 135, J)
put('bleacher', 0.0, 0.0, BKZ + 2.2, 180, J)
# cabine
put_f(CAB, 'cabin_ground', 0, 0, 0, 0, fl(0) + ['ext']); put_f(CAB, 'cabin_slab', 0, 0, 0, 0, fl(1)); put_f(CAB, 'cabin_upper', 0, 0, 0, 0, fl(1) + ['ext'])
put_f(CAB, 'cabin_roof', 0, 0, 0, 0, G + ['roof']); put_f(CAB, 'cabin_stair', 0, 0, 0, 0, G)
put_f(CAB, 'concession', 0, 0, 0, 0, fl(0)); put_f(CAB, 'restroom_a', 0, 0, 0, 0, fl(0)); put_f(CAB, 'restroom_b', 0, 0, 0, 0, fl(0)); put_f(CAB, 'press_box', 0, 0, 0, 0, fl(1))
put_f(CAB, 'menu_board', 0, 0, BZ, 0, fl(0) + ['ext']); put_f(CAB, 'service_window', 0, 0, BZ, 0, fl(0) + ['ext'])
put_f(CAB, 'door_service', BDOOR[0] + 0.01, Y0 + 0.012, -BZ + T / 2, 0, fl(0), door=-90)
put_f(CAB, 'door_service', UDOOR[0] + 0.01, F1 + 0.012, -BZ + T / 2, 0, fl(1), door=-90)
for (a, b) in RDOORS: put_f(CAB, 'door_service', BX - T / 2, Y0 + 0.012, a + 0.01, -90, fl(0), door=-90)
put_f(CAB, 'flagpole', BX + 1.0, 0, BZ + 1.0, 0, J)
for (lx, lz) in ((-BX - 1.4, 1.6), (-BX - 1.4, -1.0)): put_f(CAB, 'picnic_table', lx, 0, lz, 90, J)
put_f(CAB, 'trash_can', -BX - 0.5, 0, BZ + 0.5, 0, J)
# campo: torres, placar, gaiola, galpao
for (x, z) in (lp(24, 13, 1), lp(24, 13, -1), (25.4, -60.5), (-25.4, -60.5)):
    put('light_tower', x, 0, z, math.degrees(math.atan2(0.0 - x, -25.0 - z)), J + ['roof'])
put('scoreboard', 0, 0, -61.5, 0, J + ['roof'])
put('batting_cage', (CAGE[0] + CAGE[1]) / 2, 0, CAGE[3], 0, J + ['roof'])
put('shed', SHED[0], 0, SHED[1], 0, G); put('shed_stuff', SHED[0], 0, SHED[1], 0, G); put('door_shed', SHED[0] - 0.55 + 0.01, 0.12, SHED[1] + 1.6 - 0.06, 0, G, door=90)
# praca, estacionamento e paisagismo
put('scorer_table', -5.5, 0, 11.4, 180, J); put('fountain', -6.2, 0, 8.6, 180, J)
for (x, z, ry) in ((-9.0, 14.5, 180), (-14.0, 14.5, 180), (14.5, 4.0, -90)): put('park_bench', x, 0, z, ry, J)
for (x, z) in ((-4.3, 13.6), (5.0, 15.8), (-16.0, 2.0), (20.0, -3.0), (-21.0, -6.0)): put('trash_can', x, 0, z, 0, J)
put('bike_rack', -18.0, 0, 16.6, 0, J)
for x in (-20.0, 0.0, 20.0): put('lamp_post', x, 0.12, 18.15, 0, J)
stalls = [PKX[0] + 0.3 + 2.7 * (k + 0.5) for k in range(20)]
for k, x in enumerate(stalls): put('wheel_stop', x, -0.03, 19.0, 0, J)
for (k, n) in ((3, 'car_sedan_r'), (4, 'car_wagon_b'), (8, 'car_hatch_y'), (12, 'car_pickup_s'), (15, 'car_sedan_r')): put(n, stalls[k], -0.03, 21.3, 180, J)
for (x, z, n) in ((-40.0, 10.0, 'tree'), (-46.0, -6.0, 'tree_b'), (40.0, 8.0, 'tree'), (46.0, -12.0, 'tree_b'), (34.0, 14.0, 'tree_b'),
                  (-12.0, -64.0, 'tree'), (14.0, -65.0, 'tree_b'), (-38.0, -48.0, 'tree'), (40.0, -46.0, 'tree'), (-30.0, 15.0, 'tree_b')):
    put(n, x, 0, z, 0, J + ['roof'])
for (x, z, ry) in ((-23.0, 16.5, 0), (23.0, 16.5, 0)): put('bush_row', x, 0, z, ry, J)
put('player_scale_ref', -2.0, 0, 11.0, 0, J); put('player_scale_ref', 2.0, 0, -6.0, 0, F)

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'ground': 0.0, 'cabin_floors': [Y0, F1], 'cabin': {'center': list(BC), 'rotY': BRY, 'half_size': [BX, BZ]},
                       'diamond': {'base_distance': BASE, 'home': [0, 0], 'first': list(B1), 'second': list(B2), 'third': list(B3), 'rubber': [0, -RUB]},
                       'outfield_fence_radius': RF, 'side_fence_offset': OF, 'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
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
