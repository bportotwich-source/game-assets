"""Kit 51: pista de skate, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Praca de concreto alisado com juntas, cercada de mourao e 3 travessas. Plataforma elevada de 14 x 13 m a 1,6 m do chao com bowl em
forma de estadio (12 x 7 m, 2,3 m de fundo, transicao de 2 m de raio, coping de tubo de aco), corrimaos de tubo nas bordas, escada com
muretas e corrimaos e um bank de descida. Snake run de concreto em S afundado no piso, quarter pipe de 1,5 m com plataforma e
guarda-corpo, manual pad, ledge com cantoneira, flat rail e kicker. Banheiro de blocos de concreto com 2 sanitarios (pictogramas,
sem texto), bebedouro na parede e marquise de laje sobre pilares com bancos. 4 torres de refletores, bancos, lixeiras, skates
coloridos, placa de pictogramas, arvores, gramado e calcada. Arte original e sem texto. Y para cima, 1 unidade = 1 m.
Padrao de medidas: PADRAO_METRICAS.md.
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
configurar(cores={'concrete': (196, 194, 188), 'slab': (206, 204, 198), 'bowl': (190, 188, 184), 'coping': (222, 220, 214), 'cmu': (214, 210, 198),
                  'cmu2': (110, 128, 150), 'plaster': (240, 238, 230), 'ceil': (240, 240, 236), 'tile': (230, 234, 234), 'tile_b': (80, 120, 160),
                  'wood': (170, 120, 76), 'dkwood': (92, 64, 44), 'post': (84, 60, 42), 'metal': (176, 180, 184), 'frame': (60, 62, 66),
                  'chrome': (216, 220, 224), 'steel': (120, 126, 132), 'steel_d': (56, 60, 64), 'iron': (34, 38, 40), 'galv': (168, 172, 170),
                  'trim': (232, 230, 222), 'door': (70, 110, 150), 'door_int': (204, 180, 140), 'lamp_glass': (255, 238, 196), 'dark': (34, 34, 36),
                  'porcelain': (244, 244, 240), 'mirror': (200, 214, 220), 'frost': (214, 226, 232), 'rubber': (28, 28, 30), 'paint_w': (244, 244, 240),
                  'paint_y': (240, 196, 40), 'paint_r': (206, 60, 50), 'paint_b': (50, 110, 190), 'paint_g': (70, 160, 90), 'paint_o': (236, 128, 44),
                  'paint_p': (150, 80, 170), 'grip': (30, 30, 32), 'wheel_w': (240, 236, 220), 'board': (196, 156, 104),
                  'grass': (108, 156, 74), 'grass2': (96, 142, 66), 'leaf': (80, 134, 62), 'leaf2': (104, 150, 70), 'bark': (112, 86, 62),
                  'bench_g': (40, 92, 62), 'player': (90, 140, 220), 'pot': (176, 110, 80), 'plant': (70, 120, 60), 'paper': (238, 234, 222)},
           texturas={'concrete': 'render', 'slab': 'plaster', 'bowl': 'plaster', 'coping': 'render', 'cmu': 'stone', 'cmu2': 'stone', 'plaster': 'plaster',
                     'wood': 'planks', 'dkwood': 'planks', 'post': 'planks', 'grass': 'render', 'grass2': 'render', 'bark': 'render'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.2; t_ = 0.12
Y0 = 0.15                                   # praca de concreto e piso do banheiro
YL = 0.05                                   # gramado
GY = -0.2
PX0, PX1, PZ0, PZ1 = -19.0, 19.0, -13.0, 13.0  # praca
SX0, SX1, SZ0, SZ1 = -22.0, 22.0, -16.0, 16.0  # terreno
FX, FZ = 20.0, 14.0                         # cerca
GATE = (-2.0, 2.0)                          # entrada na cerca da frente
DX0, DX1, DZ0, DZ1, DT = -18.0, -4.0, -12.0, 1.0, 1.6   # plataforma
BC0, BC1, BCZ, BR = -13.5, -8.5, -5.5, 3.5  # bowl: centros do estadio (x), z, raio na borda
BTR, BVW, BDEP = 2.0, 0.3, 2.3              # raio da transicao, parede reta, fundo (a partir do topo)
SZA, SZB = -1.0, 1.0                        # escada (z)
NSTEP = 9; RISE = (DT - Y0) / NSTEP; TREAD = 0.3
SX_END = DX1 + (NSTEP - 1) * TREAD           # pe da escada (x)
BKZ0, BKZ1, BKX1 = -11.0, -6.0, -0.9        # bank (z e pe em x)
SNX, SNA, SNZ0, SNZ1 = 7.5, 2.3, -11.5, 6.5     # snake: eixo em x, amplitude do S, comeco e fim em z
SNW, SNB, SND = 2.4, 0.8, 1.3               # snake: meia largura, meia largura do fundo, profundidade
QX0, QZ0, QZ1, QR, QD = 15.5, -10.0, -2.0, 1.5, 1.2   # quarter pipe: pe em x, z, raio (= altura), plataforma
RX0, RX1, RZ0, RZ1 = -18.0, -12.0, 6.0, 10.0  # banheiro
RH = 3.0; RCEIL = 2.8; RCAN = 11.5          # topo das paredes, forro, frente da marquise (z)
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

# ============================================================================ ajudantes de superficie
def surf(V, F, mat, p, up=True):
    """Superficie aberta (pista): vira as faces para cima (ou para fora) e adiciona."""
    m = trimesh.Trimesh(np.array(V, float), np.array(F), process=True)
    if (m.face_normals[:, 1] * m.area_faces).sum() < 0 if up else False: m.invert()
    p.add(mat, m); return m
def grid_faces(nr, nc, wrap=False):
    F = []; cc = nc if wrap else nc - 1
    for i in range(nr - 1):
        for j in range(cc):
            a = i * nc + j; b = i * nc + (j + 1) % nc; c = (i + 1) * nc + (j + 1) % nc; d = (i + 1) * nc + j
            F += [[a, b, c], [a, c, d]]
    return F
def rail_run(p, a, b, y, h=1.0, mat='galv', step=2.0, r=0.024, ends=(True, True)):
    """Guarda-corpo de tubo: montantes a cada 2 m (no maximo), corrimao e travessa do meio."""
    a, b = np.array(a, float), np.array(b, float); Ln = np.linalg.norm(b - a); n = max(1, int(math.ceil(Ln / step)))
    for i in range(n + 1):
        if (i == 0 and not ends[0]) or (i == n and not ends[1]): continue
        c = a + (b - a) * i / n; seg_cyl(p, mat, (c[0], y - 0.05, c[1]), (c[0], y + h, c[1]), r * 1.25, 8)
        p.cyl(mat, 0.07, y, y + 0.012, c[0], c[1], 10)
    seg_cyl(p, mat, (a[0], y + h, a[1]), (b[0], y + h, b[1]), r, 8); seg_cyl(p, mat, (a[0], y + h * 0.5, a[1]), (b[0], y + h * 0.5, b[1]), r * 0.8, 8)

# ============================================================================ plataforma com bowl, escada e bank (pivo: origem, coordenadas absolutas)
DECK = sbox(DX0, DZ0, DX1, DZ1)
def stad(r, res=32): return LineString([(BC0, BCZ), (BC1, BCZ)]).buffer(r, res)
def stad_ring(nc=18, ns=12):
    """Amostras (base, normal) em volta do estadio do bowl, sentido anti-horario visto de cima."""
    out = []
    for k in range(ns): out.append(((BC0 + (BC1 - BC0) * k / ns, BCZ), 90.0))
    for k in range(nc): out.append(((BC1, BCZ), 90.0 - 180.0 * k / nc))
    for k in range(ns): out.append(((BC1 - (BC1 - BC0) * k / ns, BCZ), -90.0))
    for k in range(nc): out.append(((BC0, BCZ), -90.0 - 180.0 * k / nc))
    return out
def ring_poly(r): return Polygon([(bx + r * math.cos(math.radians(a)), bz + r * math.sin(math.radians(a))) for ((bx, bz), a) in stad_ring()]).buffer(0)
def deck():
    """Plataforma de concreto a 1,6 m: muro de arrimo, piso alisado, capa nas bordas, bowl em estadio com parede reta, transicao
    de 2 m, fundo chato com ralo, coping de tubo de aco; escada de 9 espelhos com bocel de aco, muretas e corrimaos; bank; guarda-corpos."""
    p = Piece(); B = ring_poly(BR)
    ext_y(p, 'concrete', DECK.difference(B), GY, DT - 0.02); ext_y(p, 'slab', DECK.difference(B), DT - 0.02, DT)
    lip = off(DECK, 0.03).difference(off(DECK, -0.28)).difference(sbox(DX1 - 0.5, SZA - 0.3, DX1 + 0.5, SZB + 0.3)).difference(sbox(DX1 - 0.5, BKZ0, DX1 + 0.5, BKZ1))
    ext_y(p, 'coping', lip, DT, DT + 0.025)
    ext_y(p, 'coping', ring_poly(BR + 0.4).difference(B), DT, DT + 0.02)
    # bowl
    ring = stad_ring(); nc = len(ring)
    prof = [(BTR - BTR * math.cos(f), DT - BVW - BTR * math.sin(f)) for f in np.linspace(0, math.pi / 2, 13)]
    V = []
    for (d, y) in prof:
        for ((bx, bz), a) in ring:
            r = BR - d; V.append((bx + r * math.cos(math.radians(a)), y, bz + r * math.sin(math.radians(a))))
    surf(V, grid_faces(len(prof), nc, True), 'bowl', p)
    yb = DT - BDEP; ext_y(p, 'bowl', ring_poly(BR - BTR), yb - 0.15, yb)
    p.cyl('iron', 0.18, yb, yb + 0.006, (BC0 + BC1) / 2, BCZ, 20)
    for k in range(-2, 3): p.box('dark', (BC0 + BC1) / 2 + k * 0.05 - 0.012, (BC0 + BC1) / 2 + k * 0.05 + 0.012, yb + 0.006, yb + 0.007, BCZ - 0.12, BCZ + 0.12)
    for i in range(nc):   # coping de tubo
        (b0, a0), (b1, a1) = ring[i], ring[(i + 1) % nc]
        q0 = (b0[0] + BR * math.cos(math.radians(a0)), DT - 0.02, b0[1] + BR * math.sin(math.radians(a0)))
        q1 = (b1[0] + BR * math.cos(math.radians(a1)), DT - 0.02, b1[1] + BR * math.sin(math.radians(a1)))
        seg_cyl(p, 'steel', q0, q1, 0.042, 8)
    # escada
    pts = [(DX1, GY), (SX_END, GY)]
    for k in range(NSTEP - 1, 0, -1):
        xr = DX1 + k * TREAD; y = DT - k * RISE; pts += [(xr, y), (xr - TREAD, y)]
    pts = [pts[0], pts[1]] + pts[2:]
    prof_z(p, 'concrete', SZA, SZB, pts)
    for k in range(1, NSTEP):
        xr = DX1 + k * TREAD; y = DT - k * RISE; p.box('steel', xr - 0.05, xr + 0.004, y, y + 0.006, SZA + 0.02, SZB - 0.02)
    for (z0, z1) in ((SZA - 0.25, SZA), (SZB, SZB + 0.25)):
        prof_z(p, 'concrete', z0, z1, [(DX1, GY), (SX_END + 0.2, GY), (SX_END + 0.2, Y0 + 0.3), (DX1, DT + 0.3)])
        zc = (z0 + z1) / 2; yc = lambda x: DT + 0.3 - (x - DX1) * (DT - Y0) / (SX_END + 0.2 - DX1)
        for x in (DX1 + 0.3, SX_END - 0.1): seg_cyl(p, 'galv', (x, yc(x) - 0.05, zc), (x, yc(x) + 0.85, zc), 0.03, 8)
        seg_cyl(p, 'galv', (DX1 + 0.1, yc(DX1 + 0.1) + 0.85, zc), (SX_END + 0.1, yc(SX_END + 0.1) + 0.85, zc), 0.024, 8)
    # bank
    prof_z(p, 'slab', BKZ0, BKZ1, [(DX1, GY), (BKX1, GY), (BKX1, Y0), (DX1, DT)])
    # guarda-corpos (fundos, oeste, frente e leste fora da escada e do bank)
    y = DT + 0.025
    rail_run(p, (DX0 + 0.12, DZ0 + 0.12), (DX1 - 0.12, DZ0 + 0.12), y); rail_run(p, (DX0 + 0.12, DZ0 + 0.12), (DX0 + 0.12, DZ1 - 0.12), y, ends=(False, True))
    rail_run(p, (DX0 + 0.12, DZ1 - 0.12), (DX1 - 0.12, DZ1 - 0.12), y, ends=(False, True))
    rail_run(p, (DX1 - 0.12, DZ0 + 0.12), (DX1 - 0.12, BKZ0 - 0.1), y, ends=(False, True))
    rail_run(p, (DX1 - 0.12, BKZ1 + 0.1), (DX1 - 0.12, SZA - 0.3), y)
    return p

# ============================================================================ snake run (pivo: origem, coordenadas absolutas)
def catmull(pts, step=0.25):
    P = [np.array(pts[0]) * 2 - np.array(pts[1])] + [np.array(q, float) for q in pts] + [np.array(pts[-1]) * 2 - np.array(pts[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]; n = max(2, int(np.linalg.norm(p2 - p1) / step))
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return np.array(out)
SN_C = np.array([(SNX + SNA * math.sin(2 * math.pi * (z - SNZ0) / (SNZ1 - SNZ0)), z) for z in np.linspace(SNZ0, SNZ1, 145)])   # S de um periodo (raio minimo ~3,6 m)
def sn_frame():
    C = SN_C; T_ = np.gradient(C, axis=0); T_ /= np.linalg.norm(T_, axis=1)[:, None]; N = np.stack([-T_[:, 1], T_[:, 0]], 1)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]); return C, N, s
def sn_poly():
    C, N, s = sn_frame(); L_ = C + N * SNW; R_ = C - N * SNW
    return Polygon([tuple(q) for q in L_] + [tuple(q) for q in R_[::-1]]).buffer(0)
def snake():
    """Snake run em S afundado no piso: fundo chato, transicoes que sobem ate a borda, profundidade que nasce e morre nas pontas,
    coping de tubo de aco nas bordas onde e fundo."""
    p = Piece(); C, N, s = sn_frame(); Ls = s[-1]
    us = [SNW * math.sin(math.pi / 2 * t) for t in np.linspace(-1, 1, 25)]
    def env(v): t = min(1.0, v / 3.5, (Ls - v) / 3.5); t = max(0.0, t); return t * t * (3 - 2 * t)
    def shape(u):
        a = abs(u)
        if a <= SNB: return 1.0
        t = min(1.0, (a - SNB) / (SNW - SNB)); return math.cos(math.pi / 2 * t)
    V = []
    for i in range(len(C)):
        e = env(s[i])
        for u in us:
            q = C[i] + N[i] * u; V.append((q[0], Y0 - SND * e * shape(u), q[1]))
    surf(V, grid_faces(len(C), len(us)), 'bowl', p)
    for side in (1, -1):
        for i in range(len(C) - 1):
            if env(s[i]) < 0.6 or env(s[i + 1]) < 0.6: continue
            q0 = C[i] + N[i] * side * SNW; q1 = C[i + 1] + N[i + 1] * side * SNW
            seg_cyl(p, 'steel', (q0[0], Y0 - 0.02, q0[1]), (q1[0], Y0 - 0.02, q1[1]), 0.042, 8)
    return p

# ============================================================================ quarter pipe (pivo: origem, coordenadas absolutas)
def quarter_pipe():
    """Quarter pipe de 1,5 m virado para -X: curva de concreto, coping de tubo, chapa de aco na borda, plataforma com guarda-corpo
    e escada de marinheiro atras."""
    p = Piece(); xb = QX0 + QR + QD
    pts = [(QX0, GY)] + [(QX0 + QR * math.sin(a), Y0 + QR * (1 - math.cos(a))) for a in np.linspace(0, math.pi / 2, 17)] + [(xb, Y0 + QR), (xb, GY)]
    prof_z(p, 'slab', QZ0, QZ1, pts)
    seg_cyl(p, 'steel', (QX0 + QR - 0.02, Y0 + QR - 0.02, QZ0 + 0.01), (QX0 + QR - 0.02, Y0 + QR - 0.02, QZ1 - 0.01), 0.042, 10)
    p.box('steel', QX0 + QR, QX0 + QR + 0.3, Y0 + QR, Y0 + QR + 0.006, QZ0 + 0.01, QZ1 - 0.01)
    y = Y0 + QR
    rail_run(p, (xb - 0.1, QZ0 + 0.1), (xb - 0.1, QZ1 - 0.1), y)
    for z in (QZ0 + 0.1, QZ1 - 0.1): rail_run(p, (QX0 + QR + 0.35, z), (xb - 0.1, z), y, ends=(True, False))
    for z in (-6.4, -5.6): seg_cyl(p, 'galv', (xb + 0.1, Y0 - 0.05, z), (xb + 0.1, y + 1.0, z), 0.025, 8)
    for yy in np.arange(Y0 + 0.3, y + 0.9, 0.3): seg_cyl(p, 'galv', (xb + 0.1, yy, -6.4), (xb + 0.1, yy, -5.6), 0.016, 6)
    for z in (-6.4, -5.6): p.box('galv', xb, xb + 0.12, y - 0.1, y - 0.04, z - 0.025, z + 0.025)
    return p

# ============================================================================ obstaculos de rua (pivo: centro, piso; comprimento em X)
def manual_pad(L1=4.0, d=1.5, h=0.3):
    p = Piece(); p.cham('concrete', -L1 / 2, L1 / 2, -0.1, h, -d / 2, d / 2, 0.01)
    for s in (-1, 1):
        a, b = sorted((s * d / 2, s * (d / 2 - 0.05)))
        p.box('steel', -L1 / 2 + 0.02, L1 / 2 - 0.02, h, h + 0.006, a, b); p.box('steel', -L1 / 2 + 0.02, L1 / 2 - 0.02, h - 0.05, h + 0.006, *sorted((s * d / 2, s * (d / 2 + 0.006))))
    return p
def ledge(L1=3.5, d=0.5, h=0.45):
    p = Piece(); p.cham('concrete', -L1 / 2, L1 / 2, -0.1, h, -d / 2, d / 2, 0.006)
    for s in (-1, 1):
        a, b = sorted((s * d / 2, s * (d / 2 - 0.05)))
        p.box('steel', -L1 / 2 + 0.01, L1 / 2 - 0.01, h, h + 0.006, a, b); p.box('steel', -L1 / 2 + 0.01, L1 / 2 - 0.01, h - 0.05, h + 0.006, *sorted((s * d / 2, s * (d / 2 + 0.006))))
    p.box('paint_y', -L1 / 2 + 0.01, L1 / 2 - 0.01, 0.0, 0.08, *sorted((d / 2, d / 2 + 0.004)))
    return p
def flat_rail(L1=4.0, h=0.35):
    p = Piece()
    for x in (-L1 / 2 + 0.3, L1 / 2 - 0.3):
        p.box('steel_d', x - 0.03, x + 0.03, 0.0, h - 0.04, -0.03, 0.03); p.box('steel_d', x - 0.12, x + 0.12, 0.0, 0.01, -0.12, 0.12)
        for (a, b) in ((-0.08, -0.08), (0.08, 0.08), (-0.08, 0.08), (0.08, -0.08)): p.cyl('chrome', 0.012, 0.01, 0.02, x + a, b, 6)
    p.box('paint_y', -L1 / 2, L1 / 2, h - 0.04, h, -0.025, 0.025)
    p.box('steel_d', -L1 / 2 - 0.004, -L1 / 2, h - 0.04, h, -0.025, 0.025); p.box('steel_d', L1 / 2, L1 / 2 + 0.004, h - 0.04, h, -0.025, 0.025)
    return p
def kicker(w=1.5, L1=1.4, h=0.45):
    """Rampinha de madeira com chapa de aco na boca e estrutura de cantoneira (sobe para +Z)."""
    p = Piece(); pts = [(0.0, 0.0), (L1, 0.0), (L1, h), (L1 - 0.15, h)] + [(L1 - 0.15 - (L1 - 0.15) * t, h * (1 - t) ** 1.6) for t in np.linspace(0.1, 1, 8)]
    q = Polygon([(z, y) for (z, y) in pts]).buffer(0)
    prof_x(p, 'wood', -w / 2, w / 2, [tuple(c) for c in list(q.exterior.coords)[:-1]])
    for s in (-1, 1):
        a, b = sorted((s * w / 2, s * (w / 2 + 0.03))); prof_x(p, 'steel_d', a, b, [(0.0, 0.0), (L1, 0.0), (L1, h + 0.02), (L1 - 0.1, h + 0.02)])
    p.box('steel', -w / 2 + 0.01, w / 2 - 0.01, -0.0, 0.004, -0.2, 0.0)
    return p
def skateboard(c='paint_r', g='grip'):
    """Skate: shape de madeira com nose e tail levantados, lixa, 2 trucks e 4 rodinhas (pivo: centro, chao; comprimento em X)."""
    p = Piece(); y0 = 0.075
    for (x0, x1, ya, yb_) in ((-0.3, 0.3, y0, y0), (0.3, 0.4, y0, y0 + 0.05), (-0.4, -0.3, y0 + 0.05, y0)):
        p.hull(c, [(x, y + e, z) for (x, y) in ((x0, ya), (x1, yb_)) for e in (0.0, 0.012) for z in (-0.1, 0.1)])
        p.hull(g, [(x, y + 0.012 + e, z) for (x, y) in ((x0, ya), (x1, yb_)) for e in (0.0, 0.002) for z in (-0.097, 0.097)])
    for x in (-0.22, 0.22):
        p.box('metal', x - 0.03, x + 0.03, 0.045, y0, -0.03, 0.03); seg_cyl(p, 'metal', (x, 0.03, -0.1), (x, 0.03, 0.1), 0.008, 6)
        for z in (-0.095, 0.095): disc_z(p, 'wheel_w', 0.027, z - 0.018 if z < 0 else z - 0.0, z + 0.0 if z < 0 else z + 0.018, x, 0.027, 12)
    return p
def skate_lean(c='paint_b'):
    """Skate encostado em pe (pivo: ponto no chao, encosta em -Z)."""
    p = Piece(); M = trimesh.transformations.rotation_matrix(math.radians(76), [0, 0, 1]); M[1, 3] = 0.41
    p.merge(skateboard(c), rot_y(90) @ M); return p

# ============================================================================ banheiro: modulos de bloco de concreto (pivo: face externa, cota do piso; dentro em -Z)
def r_core(p, holes, xa, xb, ea=0.0, eb=0.0):
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([GY - Y0, 0.0, 0.6, 1.4, RH] + [v for h in holes for v in h[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        if k == 0: return 'tile' if cy < 1.4 else 'plaster'
        return 'cmu2' if cy < 0.6 else 'cmu'
    for m, mesh in grid_solid(xs, ys, [-T, -0.1, 0.0], cell).items(): p.add(m, mesh)
    gaps = [(a - 0.02, b + 0.02) for (a, b, c, d) in holes if c < 0.7]
    for (a, b) in segs_excl(gaps, xa - ea, xb + eb):     # capa do soco azul
        prof_x(p, 'coping', a, b, [(0.0, 0.6), (0.03, 0.6), (0.03, 0.64), (0.0, 0.66)])
def pict_person(p, x, y, z, dress=False, col='paint_w'):
    """Placa quadrada azul com pictograma de pessoa (sem texto)."""
    p.cham('paint_b', x - 0.15, x + 0.15, y - 0.15, y + 0.15, z, z + 0.015, 0.004)
    disc_z(p, col, 0.025, z + 0.015, z + 0.022, x, y + 0.09, 14)
    if dress: p.hull(col, [(x + a, y + yy, zz) for (a, yy) in ((-0.055, -0.05), (0.055, -0.05), (0.022, 0.055), (-0.022, 0.055)) for zz in (z + 0.015, z + 0.022)])
    else: p.box(col, x - 0.03, x + 0.03, y - 0.03, y + 0.055, z + 0.015, z + 0.022)
    for s in (-1, 1): p.box(col, x + s * 0.02 - 0.011, x + s * 0.02 + 0.011, y - 0.11, y - 0.03, z + 0.015, z + 0.022)
def r_mod(kind='plain', tl=0.0, tr_=0.0, ea=0.0, eb=0.0):
    """plain, win (basculante alta de vidro fosco), door_m / door_f (porta com batente de aco e pictograma), fount (bebedouro de parede)."""
    p = Piece(); xa, xb = -W / 2 + tl, W / 2 - tr_
    if kind == 'win':
        r_core(p, [(-0.7, 0.7, 2.1, 2.55)], xa, xb, ea, eb)
        p.box('frame', -0.7, 0.7, 2.1, 2.14, -0.14, -0.06); p.box('frame', -0.7, 0.7, 2.51, 2.55, -0.14, -0.06)
        for x in (-0.7, -0.02, 0.66): p.box('frame', x, x + 0.04, 2.14, 2.51, -0.14, -0.06)
        p.box('frost', -0.66, 0.66, 2.14, 2.51, -0.103, -0.097)
        prof_x(p, 'coping', -0.78, 0.78, [(-0.06, 2.07), (0.05, 2.06), (0.05, 2.104), (-0.06, 2.104)])
    elif kind in ('door_m', 'door_f'):
        r_core(p, [(-0.5, 0.5, 0.0, 2.3)], xa, xb, ea, eb)
        for s in (-1, 1):
            a, b = sorted((s * 0.5, s * 0.45)); p.box('steel_d', a, b, 0.0, 2.3, -T, 0.02)
        p.box('steel_d', -0.45, 0.45, 2.25, 2.3, -T, 0.02); p.cham('steel', -0.5, 0.5, -0.02, 0.006, -T + 0.004, 0.03, 0.003)
        pict_person(p, 0.8, 1.6, 0.0, kind == 'door_f')
    elif kind == 'fount':
        r_core(p, [], xa, xb, ea, eb)
        p.cham('steel', -0.25, 0.25, 0.75, 0.95, 0.0, 0.32, 0.01); p.box('dark', -0.18, 0.18, 0.948, 0.952, 0.06, 0.28)
        p.hull('steel', [(x, y, z) for x in (-0.22, 0.22) for (y, z) in ((0.75, 0.0), (0.75, 0.3), (0.55, 0.0))])
        seg_cyl(p, 'chrome', (0.0, 0.95, 0.08), (0.0, 1.02, 0.1), 0.012, 6); p.box('chrome', 0.15, 0.21, 0.86, 0.92, 0.32, 0.34)
        p.box('paint_b', -0.12, 0.12, 1.25, 1.49, 0.0, 0.012); disc_z(p, 'paint_w', 0.04, 0.012, 0.018, 0.0, 1.4, 14)
        p.hull('paint_w', [(x, y, z) for (x, y) in ((-0.06, 1.32), (0.06, 1.32), (0.0, 1.27)) for z in (0.012, 0.018)])
    else:
        r_core(p, [], xa, xb, ea, eb)
    return p

# ============================================================================ banheiro: laje com marquise, piso, divisoria (pivo: origem, cota do piso)
RB = sbox(RX0, RZ0, RX1, RZ1); RI = off(RB, -T)
def r_roof():
    """Forro com plafons, laje com marquise ate a frente, testeira, manta, ralos com condutores, pilares de aco e luminarias da marquise."""
    p = Piece()
    ext_y(p, 'ceil', RI, RCEIL, RCEIL + 0.03)
    for x in (-16.5, -13.5):
        p.cyl('trim', 0.18, RCEIL - 0.012, RCEIL, x, 8.0, 18); p.cyl('lamp_glass', 0.15, RCEIL - 0.05, RCEIL - 0.012, x, 8.0, 18)
    S = sbox(RX0 - 0.3, RZ0 - 0.3, RX1 + 0.3, RCAN)
    ext_y(p, 'concrete', S, RH, RH + 0.25); ext_y(p, 'dark', off(S, -0.06), RH + 0.25, RH + 0.27)
    ext_y(p, 'trim', off(S, 0.03).difference(off(S, -0.06)), RH + 0.1, RH + 0.4)
    for x in (RX0 - 0.1, -15.0, RX1 + 0.1):
        p.box('steel_d', x - 0.07, x + 0.07, 0.0, RH, RCAN - 0.35, RCAN - 0.21); p.box('steel_d', x - 0.14, x + 0.14, 0.0, 0.012, RCAN - 0.42, RCAN - 0.14)
    for x in (-16.5, -13.5):
        p.box('steel_d', x - 0.5, x + 0.5, RH - 0.06, RH, 10.65, 10.85); p.box('lamp_glass', x - 0.46, x + 0.46, RH - 0.08, RH - 0.06, 10.67, 10.83)
    for x in (RX0 + 0.4, RX1 - 0.4):
        p.box('galv', x - 0.06, x + 0.06, RH + 0.12, RH + 0.2, RZ0 - 0.34, RZ0 - 0.3)
        seg_cyl(p, 'galv', (x, RH + 0.15, RZ0 - 0.4), (x, -Y0 + YL + 0.05, RZ0 - 0.4), 0.045, 10)
        seg_cyl(p, 'galv', (x, RH + 0.15, RZ0 - 0.34), (x, RH + 0.15, RZ0 - 0.45), 0.045, 10)
    return p
def r_floor():
    p = Piece(); ext_y(p, 'concrete', RI, GY - Y0 + 0.02, -0.012); b = RI.bounds; step = 0.3
    for i in range(int(math.ceil((b[2] - b[0]) / step))):
        for j in range(int(math.ceil((b[3] - b[1]) / step))):
            q = sbox(b[0] + i * step, b[1] + j * step, b[0] + (i + 1) * step, b[1] + (j + 1) * step).intersection(RI)
            if q.area > 1e-6: ext_y(p, 'tile' if (i + j) % 2 == 0 else 'tile_b', q, -0.012, 0.0)
    return p
def r_plan():
    """Divisoria entre os 2 sanitarios (com rodape) e secadores de mao."""
    p = Piece(); p.merge(run_wall(RZ1 - RZ0 - 2 * T, RCEIL), rot_y(-90, (-15.0, 0, RZ0 + T)))
    for (x, z, ry) in ((RX0 + T, 9.0, 90), (RX1 - T, 9.4, -90)):
        q = Piece(); q.cham('paint_w', -0.13, 0.13, 1.1, 1.4, 0.0, 0.16, 0.02); q.cyl('chrome', 0.035, 1.05, 1.1, 0.0, 0.1, 10); p.merge(q, rot_y(ry, (x, 0, z)))
    return p

# ============================================================================ torres, cerca e sinalizacao (pivo: centro, chao)
def floodlight(h=9.0, face=0.0):
    """Torre de refletores: base de concreto, poste conico de aco galvanizado, caixa de comando, braco com 3 refletores inclinados."""
    p = Piece(); p.cyl('concrete', 0.38, -0.15, 0.35, 0, 0, 20)
    lathe(p, 'galv', [(0.2, 0.35), (0.2, 0.45), (0.15, 0.5), (0.1, h)], 0, 0, 0.0, 14)
    p.cham('steel', -0.18, 0.18, 1.0, 1.55, 0.12, 0.3, 0.01); p.box('steel_d', -0.12, 0.12, 1.15, 1.4, 0.3, 0.305)
    p.box('galv', -1.1, 1.1, h - 0.1, h + 0.05, -0.06, 0.06)
    for x in (-0.8, 0.0, 0.8):
        q = Piece(); q.cham('steel_d', -0.32, 0.32, -0.22, 0.22, -0.16, 0.12, 0.02); q.box('lamp_glass', -0.28, 0.28, -0.18, 0.18, 0.12, 0.13)
        for k in range(4): q.box('steel_d', -0.3, 0.3, -0.2 + k * 0.12, -0.19 + k * 0.12, -0.18, -0.16)
        M = tr(x, h - 0.32, 0.2) @ trimesh.transformations.rotation_matrix(math.radians(35), [1, 0, 0]); p.merge(q, M)
        p.box('galv', x - 0.03, x + 0.03, h - 0.3, h - 0.1, 0.0, 0.12)
    seg_cyl(p, 'steel_d', (0.0, 1.55, 0.21), (0.0, h - 0.2, 0.12), 0.015, 6)
    return p
def rail_fence():
    """Cerca de mourao de madeira com 3 travessas em volta da praca, com a entrada da frente aberta."""
    p = Piece(); x0, x1, z0, z1 = -FX, FX, -FZ, FZ
    runs = [((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x0, z1), (x0, z0)), ((x0, z1), (GATE[0], z1)), ((GATE[1], z1), (x1, z1))]
    done = set()
    for (a, b) in runs:
        a, b = np.array(a), np.array(b); Ln = np.linalg.norm(b - a); d = (b - a) / Ln; n_ = int(math.ceil(Ln / 2.4))
        for i in range(n_ + 1):
            c = a + d * Ln * i / n_; key = (round(c[0], 2), round(c[1], 2))
            if key in done: continue
            done.add(key); p.cham('post', c[0] - 0.07, c[0] + 0.07, -0.15, 1.25, c[1] - 0.07, c[1] + 0.07, 0.01)
            p.hull('post', [(c[0] + sx * 0.07, 1.25, c[1] + sz * 0.07) for sx in (-1, 1) for sz in (-1, 1)] + [(c[0], 1.32, c[1])])
        for y in (0.35, 0.7, 1.05):
            ra, rb_ = a + d * 0.07, b - d * 0.07
            if abs(d[0]) > 0.5: p.cham('post', min(ra[0], rb_[0]), max(ra[0], rb_[0]), y, y + 0.1, a[1] - 0.025, a[1] + 0.025, 0.006)
            else: p.cham('post', a[0] - 0.025, a[0] + 0.025, y, y + 0.1, min(ra[1], rb_[1]), max(ra[1], rb_[1]), 0.006)
    return p
def sign_board():
    """Placa de entrada com pictogramas (skatista, capacete, sem bicicleta) em 2 postes de madeira, sem texto."""
    p = Piece()
    for x in (-0.9, 0.9): p.cham('post', x - 0.06, x + 0.06, -0.15, 2.2, -0.06, 0.06, 0.008)
    p.cham('dkwood', -1.05, 1.05, 1.2, 2.1, 0.06, 0.1, 0.008); p.box('paint_w', -1.0, 1.0, 1.25, 2.05, 0.1, 0.106)
    for (xc, col) in ((-0.62, 'paint_g'), (0.0, 'paint_b'), (0.62, 'paint_r')): disc_z(p, col, 0.27, 0.106, 0.114, xc, 1.65, 28)
    xc = -0.62   # skatista
    disc_z(p, 'paint_w', 0.04, 0.114, 0.12, xc + 0.04, 1.8, 12)
    p.hull('paint_w', [(xc + a, y, z) for (a, y) in ((0.0, 1.74), (0.05, 1.74), (-0.02, 1.6), (-0.07, 1.62)) for z in (0.114, 0.12)])
    p.hull('paint_w', [(xc + a, y, z) for (a, y) in ((-0.07, 1.6), (-0.02, 1.6), (-0.1, 1.5), (-0.14, 1.52)) for z in (0.114, 0.12)])
    p.hull('paint_w', [(xc + a, y, z) for (a, y) in ((-0.02, 1.6), (0.02, 1.62), (0.1, 1.5), (0.06, 1.48)) for z in (0.114, 0.12)])
    p.box('paint_w', xc - 0.2, xc + 0.16, 1.46, 1.48, 0.114, 0.12)
    for dx in (-0.14, 0.1): disc_z(p, 'paint_w', 0.02, 0.114, 0.12, xc + dx, 1.43, 10)
    xc = 0.0     # capacete
    q = Polygon([(xc + 0.16 * math.cos(t), 1.6 + 0.14 * math.sin(t)) for t in np.linspace(0, math.pi, 17)]); ext(p, 'paint_w', q, 0.114, 0.12)
    p.box('paint_w', xc - 0.2, xc + 0.18, 1.57, 1.6, 0.114, 0.12)
    xc = 0.62    # bicicleta cortada
    for dx in (-0.1, 0.1):
        m = trimesh.creation.annulus(r_min=0.06, r_max=0.078, height=0.006, sections=18); m.apply_translation([xc + dx, 1.6, 0.117]); p.add('paint_w', m)
    p.hull('paint_w', [(xc + a, y, z) for (a, y) in ((-0.1, 1.6), (0.0, 1.66), (0.1, 1.6), (0.0, 1.62)) for z in (0.114, 0.12)])
    p.hull('dark', [(xc + 0.17 * c_ + 0.025 * s_ * -sn, 1.65 + 0.17 * sn + 0.025 * s_ * c_, z) for (c_, sn) in ((math.cos(0.8), math.sin(0.8)), (-math.cos(0.8), -math.sin(0.8))) for s_ in (-1, 1) for z in (0.12, 0.126)])
    return p
def bleacher(L1=4.0, rows=3):
    """Arquibancada de aluminio de 3 degraus com estrutura de aco (pivo: centro da frente, chao; sobe para -Z)."""
    p = Piece()
    for k in range(rows):
        y = 0.4 + 0.35 * k; z = -0.35 - 0.6 * k
        for j in range(2): p.cham('metal', -L1 / 2, L1 / 2, y, y + 0.05, z - 0.12 + j * 0.14 - 0.04, z - 0.0 + j * 0.14 - 0.04 - 0.02, 0.006)
        p.box('metal', -L1 / 2, L1 / 2, y - 0.25, y - 0.22, z + 0.12, z + 0.15)
    for x in np.linspace(-L1 / 2 + 0.15, L1 / 2 - 0.15, 3):
        for k in range(rows):
            z = -0.35 - 0.6 * k; seg_cyl(p, 'steel_d', (x, 0.0, z), (x, 0.4 + 0.35 * k, z), 0.03, 8)
        seg_cyl(p, 'steel_d', (x, 0.4, -0.35), (x, 0.4 + 0.35 * (rows - 1), -0.35 - 0.6 * (rows - 1)), 0.025, 6)
    return p

# ============================================================================ terreno (pivo: origem)
SITE = sbox(SX0, SZ0, SX1, SZ1); PLAZA = sbox(PX0, PZ0, PX1, PZ1)
HOLES_ = unary_union([DECK, sbox(DX1, SZA - 0.25, SX_END + 0.2, SZB + 0.25), sbox(DX1, BKZ0, BKX1, BKZ1), sn_poly(),
                      sbox(QX0, QZ0, QX0 + QR + QD, QZ1), RB])
PAVE = PLAZA.difference(HOLES_).buffer(0)
WALK = unary_union([sbox(SX0, 14.6, SX1, SZ1), sbox(GATE[0] + 0.2, PZ1, GATE[1] - 0.2, 14.6)]).buffer(0)
GRASS = SITE.difference(PLAZA).difference(WALK).buffer(0)
def site():
    """Praca de concreto alisado em placas de 3 m com juntas, calcada e caminho da entrada, gramado em volta."""
    p = Piece(); p.merge(paving(PAVE, Y0, 3.0, 'slab', 0.008)); p.merge(paving(WALK, Y0, 1.5, 'concrete'))
    ext_y(p, 'grass', GRASS, GY, YL)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
pieces = {}
def wm(kind, tl=0.0, tr_=0.0, ea=0.0, eb=0.0):
    n = 'r_' + kind + ('_l' if tl else '') + ('_r' if tr_ else '') + ('_ea' if ea else '') + ('_eb' if eb else '')
    if n not in pieces: pieces[n] = r_mod(kind, tl, tr_, ea, eb)
    return n
pieces.update({
    'deck': deck(), 'snake': snake(), 'quarter_pipe': quarter_pipe(), 'manual_pad': manual_pad(), 'ledge': ledge(), 'flat_rail': flat_rail(),
    'kicker': kicker(), 'skate_r': skateboard('paint_r'), 'skate_b': skateboard('paint_b'), 'skate_y': skateboard('paint_y'),
    'skate_lean_g': skate_lean('paint_g'), 'skate_lean_p': skate_lean('paint_p'),
    'r_roof': r_roof(), 'r_floor': r_floor(), 'r_plan': r_plan(), 'wc': wc(), 'urinal': urinal(), 'sink': sink_bank(1, 0.8),
    'floodlight': floodlight(9.0), 'fence': rail_fence(), 'sign_board': sign_board(), 'bleacher': bleacher(4.0, 3),
    'bench': park_bench(), 'trash_can': trash_can(), 'tree': tree(6.0, 2.0), 'tree_b': tree(5.0, 1.6, 'leaf2', 4), 'bush': bush(), 'site': site(),
    'door_back': door_back(0.88, 2.24), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
y = Y0; R = ['banheiro']
for x, k in ((-17, 'door_m'), (-15, 'fount'), (-13, 'door_f')): put(wm(k, ea=T if x == -17 else 0.0, eb=T if x == -13 else 0.0), x, y, RZ1, 0, R + ['ext', 'front'])
for x, k in ((-17, 'win'), (-15, 'plain'), (-13, 'win')): put(wm(k, ea=T if x == -13 else 0.0, eb=T if x == -17 else 0.0), x, y, RZ0, 180, R + ['ext'])
for z in (7, 9):
    put(wm('plain', T if z == 7 else 0.0, T if z == 9 else 0.0, T if z == 7 else 0.0, T if z == 9 else 0.0), RX0, y, z, -90, R + ['ext'])
    put(wm('plain', T if z == 9 else 0.0, T if z == 7 else 0.0, T if z == 9 else 0.0, T if z == 7 else 0.0), RX1, y, z, 90, R + ['ext'])
put('r_roof', 0, y, 0, 0, R + ['roof']); put('r_floor', 0, y, 0, 0, R); put('r_plan', 0, y, 0, 0, R)
for xd in (-17.0, -13.0):
    hx, hz = hinge(xd, RZ1, 0, -0.44, -T / 2); put('door_back', hx, y + 0.005, hz, 0, R, door=90)
put('wc', -17.2, y, RZ0 + T, 0, R); put('urinal', -15.6, y, RZ0 + T, 0, R); put('sink', RX0 + T, y, 7.9, 90, R)
put('wc', -12.8, y, RZ0 + T, 0, R); put('sink', RX1 - T, y, 8.0, -90, R)
# pista
S = ['pista']
put('site', 0, 0, 0, 0, S); put('fence', 0, 0, 0, 0, S); put('deck', 0, 0, 0, 0, S); put('snake', 0, 0, 0, 0, S); put('quarter_pipe', 0, 0, 0, 0, S)
put('manual_pad', 3.0, y, 9.5, 0, S); put('flat_rail', 8.0, y, 10.5, 0, S); put('ledge', 13.0, y, 10.5, 0, S); put('kicker', 16.8, y, 9.2, -90, S)
put('ledge', 13.5, y, -12.2, 0, S); put('flat_rail', 1.5, y, -12.2, 0, S)
for (x, z, r) in ((-6.0, -1.3, 30), (-15.5, -11.0, -70)): put('skate_r' if x > -10 else 'skate_y', x, DT, z, r, S)
put('skate_b', -11.0, DT - BDEP, -5.3, 15, S); put('skate_y', 5.5, y, 10.9, 100, S); put('skate_r', 15.8, y, -1.2, 10, S)
put('bleacher', -9.5, y, 4.0, 90, S)
put('skate_lean_g', -9.4, y, 1.95, 0, S); put('skate_lean_p', 13.3, y, 11.1, 0, S)
for (x, z) in ((-18.8, -12.6), (18.8, -12.6), (-18.8, 12.6), (18.8, 12.6)): put('floodlight', x, y, z, math.degrees(math.atan2(-x, -z)), S + ['roof'])
for (x, z, r) in ((10.0, 12.6, 180), (16.0, 12.6, 180), (-7.0, 12.6, 180), (18.4, 4.0, -90), (-1.0, 4.5, 90)): put('bench', x, y, z, r, S)
for (x, z) in ((-10.5, 12.6), (4.6, 12.6), (18.4, 6.2), (18.4, -11.5), (-3.2, -12.5)): put('trash_can', x, y, z, 0, S)
put('sign_board', 3.6, YL, 13.55, 0, S)
for k, (x, z) in enumerate(((-21.0, -14.5), (-21.0, -6.0), (-21.0, 3.0), (-21.0, 11.0), (21.0, -14.5), (21.0, -5.0), (21.0, 4.0), (21.0, 11.0),
                            (-12.0, -15.0), (-3.0, -15.0), (6.0, -15.0), (14.0, -15.0))):
    put('tree' if k % 2 == 0 else 'tree_b', x, YL, z, 0, S + ['roof'])
for (x, z) in ((-3.0, 13.5), (-5.0, 13.5), (5.5, 13.5), (-19.5, 13.4), (19.5, 13.4)): put('bush', x, YL, z, 0, S)
put('player_scale_ref', -1.0, y, 7.0, 0, S); put('player_scale_ref', -8.0, DT, -0.5, 0, S)


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'plaza_level': Y0, 'lawn_level': YL,
                       'deck': {'x': [DX0, DX1], 'z': [DZ0, DZ1], 'top': DT, 'stairs_z': [SZA, SZB], 'bank_z': [BKZ0, BKZ1]},
                       'bowl': {'centers_x': [BC0, BC1], 'z': BCZ, 'radius': BR, 'transition': BTR, 'depth': BDEP},
                       'snake': {'axis_x': SNX, 'amplitude': SNA, 'z': [SNZ0, SNZ1], 'half_width': SNW, 'depth': SND},
                       'quarter_pipe': {'x0': QX0, 'z': [QZ0, QZ1], 'radius': QR, 'deck': QD},
                       'restroom': {'x': [RX0, RX1], 'z': [RZ0, RZ1], 'wall_top': RH, 'canopy_front_z': RCAN},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]}, 'fence': {'x': [-FX, FX], 'z': [-FZ, FZ], 'gate_x': list(GATE)},
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
