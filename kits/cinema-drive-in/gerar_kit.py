"""Kit 43: cinema drive-in (anos 50), em ALTO DETALHE (scripts/detalhe/detalhe.py).
Telao de 20 x 9 m com imagem pintada sem texto (deserto com mesas e sol), parede de tabuas embaixo, estrutura de aco trelicada atras
com passarela e escada. Lanchonete oval streamline no meio do patio (14 x 8 m): reboco creme, rodape de azulejo vermelho, 3 frisos
vermelhos, janelas em fita, marquise com neon sobre a porta dupla e lanterna vermelha na cobertura. Dentro: salao com piso xadrez,
balcao de lanches com pipoqueira, refrigeradora, chapa de cachorro-quente e cafeteira, quadro de cardapio so com pictogramas, mesas
com banquetas, fliperamas e jukebox; cabine de projecao com 2 projetores mirando o telao pelas janelinhas; banheiros com porta para fora.
Fora: 4 fileiras de rampas em arco com postes de alto-falante, carros dos anos 50 em 4 cores, parquinho (balanco, escorregador e
gira-gira), bilheteria na entrada, letreiro luminoso sem texto (rolo de filme e estrela) com seta, cerca de tabuas, postes, arvores,
calcada e rua.
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
configurar(cores={'render': (238, 228, 204), 'tile_r': (178, 52, 44), 'trim_r': (190, 56, 46), 'roof_r': (186, 58, 48), 'coping': (204, 206, 208),
                  'plaster': (240, 234, 222), 'ceil': (246, 244, 236), 'tile': (236, 234, 226), 'tile_k': (180, 50, 44), 'concrete': (188, 184, 176),
                  'metal': (190, 194, 198), 'frame': (186, 190, 194), 'chrome': (216, 220, 224), 'steel': (120, 126, 132), 'steel_d': (64, 68, 72),
                  'brass': (200, 164, 84), 'wood': (150, 108, 70), 'dkwood': (96, 64, 44), 'trim': (110, 74, 50), 'door_int': (150, 104, 66),
                  'boards': (170, 172, 170), 'screen_w': (244, 244, 238), 'sky1': (120, 186, 222), 'sky2': (178, 214, 230), 'sand': (232, 196, 132),
                  'mesa': (196, 112, 70), 'mesa2': (164, 88, 60), 'sun': (250, 206, 70), 'cactus': (80, 134, 76), 'dark': (36, 36, 38),
                  'neon': (150, 240, 210), 'neon_r': (255, 110, 100), 'lamp_glass': (255, 238, 196), 'vinyl_r': (196, 56, 50), 'cream': (240, 232, 210),
                  'porcelain': (244, 244, 240), 'mirror': (200, 214, 220), 'stall': (196, 70, 60), 'paper': (238, 234, 222), 'pop': (250, 236, 170),
                  'soda_b': (60, 110, 170), 'yellowp': (234, 190, 50), 'green_p': (70, 140, 90), 'blue_p': (60, 110, 170), 'orange_p': (226, 120, 50),
                  'gravel': (172, 164, 150), 'gravel_r': (146, 138, 124), 'asphalt': (70, 72, 74), 'grass': (100, 148, 70), 'leaf': (86, 132, 64), 'leaf2': (112, 150, 72),
                  'bark': (110, 84, 60), 'curb': (196, 192, 184), 'rubber': (26, 26, 28), 'paint_w': (238, 238, 232), 'sign_b': (40, 60, 120),
                  'car_a': (196, 60, 60), 'car_b': (90, 170, 170), 'car_c': (240, 224, 170), 'car_d': (80, 110, 170), 'car_w': (240, 240, 236),
                  'membrane': (118, 118, 116), 'film': (40, 40, 44)},
           texturas={'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'asphalt': 'render', 'gravel': 'render', 'gravel_r': 'render', 'grass': 'render',
                     'wood': 'planks', 'dkwood': 'planks', 'boards': 'planks', 'membrane': 'render', 'curb': 'render', 'sand': 'render'},
           out=OUT)
D.METAL.update({'metal', 'frame', 'chrome', 'steel', 'steel_d', 'brass', 'coping'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.12                               # modulo, parede externa, parede interna
Y0 = 0.15                                                  # piso da lanchonete (patio em 0)
CEIL = 3.0; HW = 3.3; HP = 3.75                            # forro, topo da laje, topo da platibanda (sobre o piso)
BX, BR = 3.0, 4.0                                          # lanchonete: retas de x = -3 a 3 em z = +-4, pontas em meio-circulo de raio 4
NF = 8; AH = math.radians(180 / NF / 2); AP = BR * math.cos(AH); FW = 2 * BR * math.sin(AH)
BASE = 0.6; SPEED = (3.42, 3.52, 3.62)                     # rodape de azulejo, frisos
ZPR = -1.2; XPR = 1.0                                      # cabine de projecao: x de -3 a 1, z de -4 a -1,2
SZF = -18.0; SW = 10.0; SY0, SY1 = 4.5, 13.5               # telao: face em z = -18, x de -10 a 10, imagem de 4,5 a 13,5 m
RC = (0.0, -40.0); ROWS = [26.6, 33.0, 46.6, 52.6]; ROW_GAP = {33.0: math.radians(15.0)}         # centro dos arcos das rampas e raio da borda da frente de cada fileira
RH = 0.45; RUP, RDN = 0.9, 4.4                             # altura da rampa, subida e fim da descida (a partir da borda)
FX0, FX1, FZ0, FZ1 = -21.0, 21.0, -23.0, 18.5              # cerca
GATE = (11.0, 19.0)                                        # entrada (na frente)
ISL = (13.8, 16.2, 17.6, 20.2)                             # ilha da bilheteria
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

# ============================================================================ lanchonete: contorno, facetas e modulos
def outline_pts():
    pts = [(BX + BR * math.cos(a), BR * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, NF + 1)]
    pts += [(-BX + BR * math.cos(a), BR * math.sin(a)) for a in np.linspace(math.pi / 2, 3 * math.pi / 2, NF + 1)]
    return pts
OUTL = Polygon(outline_pts()); INNER = off(OUTL, -T)
def facet_pos(end, k):
    th = (-math.pi / 2 if end > 0 else math.pi / 2) + (k + 0.5) * 2 * AH; cx = BX * end
    return cx + AP * math.cos(th), AP * math.sin(th), 90 - math.degrees(th)
def facet_clip(q):
    c, s = math.cos(AH), math.sin(AH); o = (0.0, 0.0, -AP)
    return clipped(q, [(o, (c, 0, s)), (o, (-c, 0, s))])
def wall_core(p, holes, xs0=(-W / 2, W / 2), h=HP):
    xs = sorted(set(list(xs0) + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([-Y0, 0.0, BASE, CEIL, HW, h] + [v for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        if k == 0: return 'plaster' if cy < HW else 'render'
        return 'tile_r' if cy < BASE else 'render'
    for m, mesh in grid_solid(xs, ys, [-T, -0.15, 0.0], cell).items(): p.add(m, mesh)
def sill_out(p, a, b, y):
    prof_x(p, 'coping', a, b, [(-0.1, y - 0.04), (0.06, y - 0.04), (0.07, y - 0.025), (0.07, y - 0.012), (-0.1, y + 0.005)])
def stool_in(p, a, b, y):
    p.cham('wood', a, b, y - 0.03, y + 0.004, -T - 0.04, -0.15, 0.005)
def window(p, a, b, y0, y1, mull=True):
    alu_frame(p, a, b, y0, y1, f=0.045, z0=-0.17, z1=-0.08, mulls=((a + b) / 2,) if mull else (), trans=(y0 + 0.62 * (y1 - y0),))
    p.box('glass', a + 0.045, b - 0.045, y0 + 0.045, y1 - 0.045, -0.128, -0.122)
    sill_out(p, a - 0.04, b + 0.04, y0); stool_in(p, a - 0.02, b + 0.02, y0)
def door_frame(p, a, b, h):
    p.box('steel', a, a + 0.05, 0.0, h, -0.18, -0.06); p.box('steel', b - 0.05, b, 0.0, h, -0.18, -0.06); p.box('steel', a + 0.05, b - 0.05, h - 0.05, h, -0.18, -0.06)
    p.cham('concrete', a, b, -0.02, 0.008, -T + 0.004, 0.02, 0.004)
def wall(kind='plain'):
    """Modulo reto de 2 m (pivo: face externa, cota do piso): win (janela em fita), port (2 janelinhas de projecao com visor de vidro,
    guilhotina de aco levantada e capuz), door2 (porta dupla de vidro com bandeira), plain."""
    p = Piece(); holes = []
    if kind == 'win': holes = [(-0.9, 0.9, 1.0, 2.3)]
    if kind == 'port': holes = [(-0.75, -0.25, 1.7, 2.05), (0.25, 0.75, 1.7, 2.05)]
    if kind == 'door2': holes = [(-0.95, 0.95, 0.0, 2.6)]
    wall_core(p, holes)
    if kind == 'win': window(p, -0.9, 0.9, 1.0, 2.3)
    if kind == 'port':
        for c in (-0.5, 0.5):
            for (a, b) in ((c - 0.25, c - 0.21), (c + 0.21, c + 0.25)): p.box('steel_d', a, b, 1.7, 2.05, -0.2, -0.05)
            p.box('steel_d', c - 0.21, c + 0.21, 1.7, 1.74, -0.2, -0.05); p.box('steel_d', c - 0.21, c + 0.21, 2.01, 2.05, -0.2, -0.05)
            p.box('glass', c - 0.21, c + 0.21, 1.74, 2.01, -0.123, -0.117)
            p.cham('steel_d', c - 0.3, c + 0.3, 2.08, 2.46, -T - 0.08, -T - 0.04, 0.004)
            for s in (-1, 1): p.box('steel_d', c + s * 0.27 - 0.015, c + s * 0.27 + 0.015, 1.68, 2.5, -T - 0.04, -T)
            p.hull('steel_d', [(c + a, y, z) for a in (-0.32, 0.32) for (y, z) in ((2.1, 0.0), (2.1, 0.25), (2.14, 0.25), (2.3, 0.0))])
    if kind == 'door2':
        alu_frame(p, -0.95, 0.95, 0.0, 2.6, f=0.05, z0=-0.17, z1=-0.07, trans=(2.2,))
        p.box('glass', -0.9, 0.9, 2.225, 2.55, -0.123, -0.117); p.cham('concrete', -0.95, 0.95, -0.02, 0.008, -T + 0.004, 0.02, 0.004)
    return p
def facet(kind='plain'):
    """Faceta da ponta redonda (pivo: centro da face externa, cota do piso; cortada em meia-esquadria): win, high (janelinha alta de
    banheiro com vidro canelado), door (porta de servico com arandela), plain."""
    q = Piece(); w2 = FW / 2 + 0.35; holes = []
    if kind == 'win': holes = [(-0.5, 0.5, 1.0, 2.3)]
    if kind == 'high': holes = [(-0.42, 0.42, 2.0, 2.6)]
    if kind == 'door': holes = [(-0.46, 0.46, 0.0, 2.2)]
    wall_core(q, holes, (-w2, w2))
    if kind == 'win': window(q, -0.5, 0.5, 1.0, 2.3, mull=False)
    if kind == 'high': window(q, -0.42, 0.42, 2.0, 2.6, mull=False)
    if kind == 'door':
        door_frame(q, -0.46, 0.46, 2.2); q.merge(wall_lamp(), tr(0.0, 2.5, 0.0))
    return facet_clip(q)
DOORS = [('w', 1), ('w', 6), ('e', 4)]                     # facetas com porta: 2 banheiros (oeste) e servico (leste)
EAST_K = {0: 'plain', 1: 'win', 2: 'win', 3: 'win', 4: 'door', 5: 'win', 6: 'win', 7: 'plain'}
WEST_K = {0: 'plain', 1: 'door', 2: 'plain', 3: 'high', 4: 'high', 5: 'plain', 6: 'door', 7: 'plain'}
def door_gaps(pad=0.0):
    from shapely import affinity
    gs = [sbox(-0.95 - pad, BR - 0.6, 0.95 + pad, BR + 0.6)]
    for (e, k) in DOORS:
        x, z, ry = facet_pos(1 if e == 'e' else -1, k)
        gs.append(affinity.rotate(sbox(x - 0.46 - pad, z - 0.6, x + 0.46 + pad, z + 0.6), -ry, origin=(x, z)))
    return unary_union(gs)
def trims():
    """Aneis continuos em volta da lanchonete (pivo: origem, cota do piso): 3 frisos vermelhos, capa do azulejo (para nas portas),
    rufo da platibanda, manta por dentro e rodape interno (para nas portas)."""
    p = Piece(); gaps = door_gaps()
    for y in SPEED: ext_y(p, 'trim_r', off(OUTL, 0.045).difference(OUTL), y, y + 0.07)
    ext_y(p, 'tile_r', off(OUTL, 0.022).difference(OUTL).difference(gaps), BASE - 0.02, BASE + 0.025)
    ext_y(p, 'coping', off(OUTL, 0.05).difference(off(OUTL, -T - 0.03)), HP, HP + 0.06)
    ext_y(p, 'membrane', INNER.difference(off(OUTL, -T - 0.03)), HW, HW + 0.15)
    ext_y(p, 'trim', INNER.difference(off(OUTL, -T - 0.016)).difference(door_gaps(0.0)), 0.001, 0.12)
    return p
def roof():
    """Laje de cobertura com forro, manta, lanterna vermelha com venezianas e telhadinho de 2 aguas, 2 respiros e ralos."""
    p = Piece()
    ext_y(p, 'ceil', INNER, CEIL - 0.01, CEIL); ext_y(p, 'concrete', INNER, CEIL, HW - 0.012); ext_y(p, 'membrane', INNER, HW - 0.012, HW)
    x0, x1, z0, z1 = -1.5, 2.5, -1.4, 1.4; y0 = HW; y1 = HW + 1.3
    p.box('roof_r', x0, x1, y0, y1, z0, z1)
    for z in (z0, z1):
        s = 1 if z > 0 else -1
        for x in np.arange(x0 + 0.5, x1 - 0.3, 1.0):
            p.box('paint_w', x - 0.35, x + 0.35, y0 + 0.35, y0 + 1.05, *sorted((z, z + s * 0.01)))
            for k in range(6): yy = y0 + 0.42 + k * 0.105; p.hull('dark', [(x + a, yy + d, z + s * e) for a in (-0.32, 0.32) for (d, e) in ((0.0, 0.012), (0.06, 0.012), (0.0, 0.05))])
    pts = [(z0 - 0.25, y1), (0.0, y1 + 0.7), (z1 + 0.25, y1), (z1 + 0.25, y1 - 0.06), (0.0, y1 + 0.62), (z0 - 0.25, y1 - 0.06)]
    prof_x(p, 'roof_r', x0 - 0.25, x1 + 0.25, pts); prof_x(p, 'paint_w', x0 - 0.27, x1 + 0.27, [(z0 - 0.27, y1 - 0.08), (0.0, y1 + 0.6), (z1 + 0.27, y1 - 0.08), (z1 + 0.27, y1 - 0.12), (0.0, y1 + 0.56), (z0 - 0.27, y1 - 0.12)])
    for (x, z) in ((-4.5, -1.5), (5.0, 1.8)): p.cyl('metal', 0.08, HW, HW + 0.7, x, z, 12); lathe(p, 'metal', [(0.0, HW + 0.85), (0.16, HW + 0.72), (0.12, HW + 0.68)], x, z, 0.0, 12)
    for (x, z) in ((-5.5, 1.0), (5.5, -1.0)): p.cyl('dark', 0.12, HW, HW + 0.004, x, z, 12)
    return p
def front_canopy():
    """Marquise oval da porta (pivo: face da parede, cota do piso): laje com testeira vermelha, 2 tubos de neon e luzes embaixo."""
    p = Piece(); from shapely import affinity
    E = affinity.scale(Point(0, 0).buffer(1.0, 48), 2.4, 1.5).intersection(sbox(-5, 0.0, 5, 5))
    ext_y(p, 'ceil', E, 2.75, 2.76); ext_y(p, 'concrete', E, 2.76, 2.98)
    rim = off(E, 0.04).difference(E).difference(sbox(-5, -1, 5, 0.03)); ext_y(p, 'trim_r', rim, 2.66, 3.04)
    for (y, m) in ((2.74, 'neon'), (2.92, 'neon_r')):
        ring = off(E, 0.055).difference(off(E, 0.04)).difference(sbox(-5, -1, 5, 0.05)); ext_y(p, m, ring, y, y + 0.035)
    for x in (-1.4, -0.5, 0.5, 1.4): p.cyl('lamp_glass', 0.09, 2.74, 2.75, x, 0.8, 16)
    return p

# ============================================================================ piso, paredes internas e interior (pivo: origem, cota do piso)
REST = INNER.intersection(sbox(-20, -20, -BX - t_ / 2, 20)); PROJ = sbox(-BX + t_ / 2, -BR + T, XPR - t_ / 2, ZPR - t_ / 2)
HALL = INNER.difference(sbox(-20, -20, -BX + t_ / 2, 20)).difference(sbox(-20, -20, XPR + t_ / 2, ZPR + t_ / 2))
def checker(p, poly, y0, y1, step, ma, mb, ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step, oz + j * step, ox + (i + 1) * step, oz + (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
def floor_piece():
    """Piso: xadrez vermelho e creme de 40 cm no salao, ladrilho miudo nos banheiros, concreto pintado na cabine de projecao."""
    p = Piece(); ext_y(p, 'concrete', INNER, -Y0 + 0.02, -0.012)
    checker(p, HALL, -0.012, 0.0, 0.4, 'tile_k', 'tile', 0.2, 0.2); zi = BR - T
    U = unary_union([sbox(-BX - t_ / 2, -zi, -BX + t_ / 2, zi), sbox(-BX + t_ / 2, ZPR - t_ / 2, XPR + t_ / 2, ZPR + t_ / 2), sbox(XPR - t_ / 2, -zi, XPR + t_ / 2, ZPR - t_ / 2)])
    ext_y(p, 'concrete', U.intersection(INNER), -0.012, 0.0)
    checker(p, REST, -0.012, 0.0, 0.2, 'tile', 'porcelain', 0.1, 0.1); ext_y(p, 'steel_d', PROJ, -0.012, 0.0)
    return p
def plan():
    """Paredes internas: parede dos banheiros e da cabine (x = -3), divisoria dos banheiros, cabine de projecao com porta, divisoria
    de box no banheiro feminino e entre os mictorios."""
    p = Piece(); zi = BR - T
    p.merge(run_wall(2 * zi, CEIL), rot_y(-90, (-BX, 0, -zi)))
    p.merge(run_wall(-BX - t_ / 2 + (BX + BR - T / math.cos(AH) + 0.02), CEIL), tr(-(BX + BR - T / math.cos(AH) + 0.02), 0, 0.0))
    x0 = -BX + t_ / 2; p.merge(run_wall(XPR + t_ / 2 - x0, CEIL, [(-0.5 - x0, 0.9, 0.0, 2.1, 'door')]), tr(x0, 0, ZPR))
    p.merge(run_wall(ZPR - t_ / 2 + zi, CEIL), rot_y(-90, (XPR, 0, -zi)))
    p.box('stall', -4.7, -BX - t_ / 2, 0.15, 2.0, 1.98, 2.02); p.cyl('chrome', 0.02, 0.0, 0.15, -4.65, 2.0, 8)
    p.box('stall', -4.6 - 0.015, -4.6 + 0.015, 0.4, 1.6, -0.06 - 0.6, -0.06)
    return p
def ceiling_light():
    p = Piece(); p.cyl('chrome', 0.24, -0.03, 0.0, 0, 0, 24); p.cyl('lamp_glass', 0.2, -0.05, -0.03, 0, 0, 24); return p
def projector():
    """Projetor de cinema (pivo: centro do pe, piso; lente para -Z): pedestal de ferro, corpo com mecanismo, casa da lampada com
    chamine ate o forro, magazines de filme em cima e embaixo, lente, manivela e caixa de som."""
    p = Piece(); p.hull('steel_d', [(a, 0.0, c) for a in (-0.35, 0.35) for c in (-0.45, 0.45)] + [(a, 0.9, c) for a in (-0.18, 0.18) for c in (-0.25, 0.25)])
    p.cham('steel', -0.2, 0.2, 0.9, 1.65, -0.45, 0.15, 0.02); p.cham('steel_d', -0.25, 0.25, 1.5, 2.1, 0.15, 0.85, 0.03)
    p.cyl('steel_d', 0.1, 2.1, CEIL, 0.0, 0.5, 12); p.box('dark', -0.22, 0.22, 1.7, 1.9, 0.85, 0.87)
    disc_z(p, 'chrome', 0.07, -0.75, -0.45, 0.0, 1.88, 16); disc_z(p, 'dark', 0.055, -0.76, -0.75, 0.0, 1.88, 16)
    for (y, r) in ((2.35, 0.48), (0.55, 0.42)):
        disc_x(p, 'steel', r, -0.08, 0.08, y, -0.15, 32); disc_x(p, 'film', r - 0.06, -0.085, 0.085, y, -0.15, 32) if False else None
        disc_x(p, 'chrome', 0.06, -0.12, 0.12, y, -0.15, 12)
    p.box('steel', -0.06, 0.06, 1.65, 1.95, -0.2, -0.1)
    seg_cyl(p, 'chrome', (0.2, 1.3, -0.1), (0.35, 1.3, -0.1), 0.015, 6); seg_cyl(p, 'chrome', (0.35, 1.3, -0.1), (0.35, 1.15, -0.1), 0.015, 6)
    p.cham('steel_d', -0.5, -0.22, 0.9, 1.3, -0.2, 0.2, 0.02)
    return p
def rewind_bench(L1=1.4):
    """Bancada de rebobinar (pivo: centro de tras, piso): tampo, 2 rebobinadeiras com rolos e lata de filme."""
    p = Piece(); x = L1 / 2; p.cham('wood', -x, x, 0.85, 0.9, 0.0, 0.6, 0.006)
    for xx in (-x + 0.05, x - 0.05): p.box('steel', xx - 0.03, xx + 0.03, 0.0, 0.85, 0.05, 0.55)
    for xx in (-0.4, 0.4):
        p.box('steel_d', xx - 0.04, xx + 0.04, 0.9, 1.15, 0.25, 0.35); disc_z(p, 'steel', 0.3, 0.36, 0.38, xx, 1.2, 28); disc_z(p, 'film', 0.24, 0.355, 0.385, xx, 1.2, 28)
    p.cyl('steel', 0.2, 0.9, 0.96, 0.0, 0.4, 24)
    return p
def film_rack(L1=1.2):
    p = Piece(); x = L1 / 2
    for xx in (-x, x): p.box('steel', xx - 0.02, xx + 0.02, 0.0, 1.8, 0.0, 0.4)
    for y in (0.1, 0.6, 1.1, 1.6):
        p.box('steel', -x, x, y, y + 0.02, 0.0, 0.4)
        if y < 1.5:
            for xx in np.arange(-x + 0.12, x - 0.1, 0.18): disc_x(p, 'steel', 0.18, xx - 0.03, xx + 0.03, y + 0.2, 0.2, 20)
    return p
def snack_counter():
    """Balcao de lanches (pivo: origem, cota do piso; atende para -X): frente de azulejo vermelho com frisos cromados, tampo creme
    com borda, caixa registradora, guardanapeiras e bisnagas; atras, bancada com pipoqueira, refrigeradora de 4 torneiras, chapa de
    cachorro-quente, cafeteira e pilha de copos."""
    p = Piece(); x0, x1, z0, z1 = 3.6, 4.2, -2.4, 2.4
    p.box('tile_r', x0, x1, 0.1, 0.95, z0, z1); p.box('dark', x0 + 0.06, x1, 0.0, 0.1, z0, z1)
    for y in (0.3, 0.55, 0.8): p.box('chrome', x0 - 0.012, x0, y, y + 0.025, z0, z1)
    p.cham('cream', x0 - 0.08, x1 + 0.05, 0.95, 1.0, z0 - 0.05, z1 + 0.05, 0.008); ring = None
    p.box('chrome', x0 - 0.09, x1 + 0.06, 0.94, 0.95, z0 - 0.06, z1 + 0.06)
    p.cham('chrome', 3.75, 4.1, 1.0, 1.25, 1.5, 1.95, 0.02); p.hull('chrome', [(3.75, 1.25, 1.5), (3.75, 1.25, 1.95), (3.95, 1.4, 1.5), (3.95, 1.4, 1.95), (4.1, 1.25, 1.5), (4.1, 1.25, 1.95)])
    for z in (-1.6, 0.0):
        p.box('chrome', 3.75, 3.85, 1.0, 1.15, z - 0.07, z + 0.07)
        for (dz, m) in ((0.14, 'tile_r'), (0.22, 'yellowp')): lathe(p, m, [(0.03, 1.0), (0.03, 1.15), (0.01, 1.2)], 3.8, z + dz, 0.0, 10)
    bx0, bx1, bz0, bz1 = 5.0, 5.6, -1.8, 1.8
    p.box('metal', bx0, bx1, 0.1, 0.88, bz0, bz1); p.box('dark', bx0, bx1 - 0.05, 0.0, 0.1, bz0, bz1); p.cham('chrome', bx0 - 0.03, bx1, 0.88, 0.92, bz0, bz1, 0.006)
    z = -1.2; p.cham('tile_r', 5.05, 5.55, 0.92, 1.0, z - 0.3, z + 0.3, 0.01)
    for (a, b) in ((-0.28, -0.26), (0.26, 0.28)): p.box('chrome', 5.07, 5.53, 1.0, 1.7, z + a, z + b)
    p.box('glass', 5.08, 5.52, 1.0, 1.68, z - 0.26, z + 0.26) if False else None
    for (xa, xb) in ((5.07, 5.09), (5.51, 5.53)): p.box('glass', xa, xb, 1.0, 1.68, z - 0.26, z + 0.26)
    p.cham('tile_r', 5.04, 5.56, 1.7, 1.82, z - 0.3, z + 0.3, 0.01); p.hull('pop', [(5.12, 1.0, z - 0.2), (5.48, 1.0, z - 0.2), (5.12, 1.0, z + 0.2), (5.48, 1.0, z + 0.2), (5.3, 1.35, z)])
    p.cyl('steel', 0.08, 1.45, 1.6, 5.3, z, 12)
    z = 0.0; p.cham('cream', 5.1, 5.6, 0.92, 1.6, z - 0.4, z + 0.4, 0.02); p.box('soda_b', 5.08, 5.1, 1.2, 1.5, z - 0.35, z + 0.35)
    for dz in (-0.27, -0.09, 0.09, 0.27):
        p.box('chrome', 5.0, 5.1, 1.32, 1.38, z + dz - 0.03, z + dz + 0.03); seg_cyl(p, 'chrome', (5.02, 1.32, z + dz), (5.02, 1.24, z + dz), 0.012, 6)
    p.box('chrome', 4.95, 5.1, 0.92, 0.94, z - 0.4, z + 0.4)
    z = 0.95; p.cham('chrome', 5.08, 5.55, 0.92, 1.0, z - 0.3, z + 0.3, 0.01)
    for k in range(6): seg_cyl(p, 'chrome', (5.12 + k * 0.075, 1.02, z - 0.25), (5.12 + k * 0.075, 1.02, z + 0.25), 0.02, 8)
    for k in (0, 2, 4): seg_cyl(p, 'tile_r', (5.12 + k * 0.075, 1.05, z - 0.2), (5.12 + k * 0.075, 1.05, z + 0.2), 0.016, 8)
    lathe(p, 'chrome', [(0.13, 0.92), (0.13, 1.35), (0.1, 1.42), (0.03, 1.48)], 5.3, 1.5, 0.0, 16)
    for k in range(5): p.cyl('paint_w', 0.045, 0.92 + k * 0.004, 0.92 + (k + 1) * 0.004 + 0.1, 5.35, -0.6 + 0.0, 12) if False else None
    lathe(p, 'paint_w', [(0.04, 0.92), (0.05, 1.2)], 5.35, -0.6, 0.0, 12)
    return p
def menu_board():
    """Quadro de cardapio sem texto (pivo: centro, alto; frente -X): moldura cromada, 5 pictogramas (pipoca, refrigerante,
    cachorro-quente, cafe e sorvete) com bolinhas de preco coloridas, correntes ate o forro."""
    p = Piece(); p.box('chrome', -0.03, 0.03, -0.42, 0.42, -1.55, 1.55); p.box('dark', -0.04, 0.0, -0.38, 0.38, -1.5, 1.5)
    xs = -0.042
    def tile(z, items):
        for i, (m, pts) in enumerate(items): p.hull(m, [(xs - d - 0.002 * i, y, z + q) for (q, y) in pts for d in (0.0, 0.004)])
    zs = [-1.2, -0.6, 0.0, 0.6, 1.2]
    tile(zs[0], [('paint_w', [(-0.12, -0.15), (0.12, -0.15), (0.15, 0.12), (-0.15, 0.12)]), ('pop', [(-0.15, 0.12), (0.15, 0.12), (0.1, 0.25), (-0.1, 0.25), (0.0, 0.28)])])
    p.box('tile_r', xs - 0.006, xs - 0.004, -0.15, 0.12, zs[0] - 0.03, zs[0] + 0.03)
    tile(zs[1], [('soda_b', [(-0.1, -0.15), (0.1, -0.15), (0.13, 0.15), (-0.13, 0.15)]), ('paint_w', [(0.02, 0.15), (0.05, 0.15), (0.1, 0.3), (0.07, 0.3)])])
    tile(zs[2], [('sand', [(-0.2, -0.05), (0.2, -0.05), (0.22, 0.03), (-0.22, 0.03)]), ('tile_r', [(-0.24, 0.0), (0.24, 0.0), (0.24, 0.05), (-0.24, 0.05)])])
    tile(zs[3], [('paint_w', [(-0.1, -0.12), (0.1, -0.12), (0.12, 0.08), (-0.12, 0.08)]), ('dkwood', [(-0.1, 0.03), (0.1, 0.03), (0.1, 0.07), (-0.1, 0.07)])])
    tile(zs[4], [('sand', [(-0.08, 0.0), (0.08, 0.0), (0.0, -0.18)]), ('pop', [(-0.1, 0.0), (0.1, 0.0), (0.1, 0.12), (0.0, 0.18), (-0.1, 0.12)])])
    for z in zs:
        for k in range(2): p.sphere(('yellowp', 'neon')[k], 0.025, xs - 0.01, -0.3, z - 0.05 + k * 0.1, 1)
    for z in (-1.4, 1.4): seg_cyl(p, 'chrome', (0, 0.42, z), (0, 0.42 + 0.5, z), 0.006, 4)
    return p
def table_stools():
    """Mesa redonda de pe central com 3 banquetas giratorias vermelhas (pivo: centro, piso)."""
    p = Piece(); p.cyl('chrome', 0.25, 0.0, 0.03, 0, 0, 20); seg_cyl(p, 'chrome', (0, 0.03, 0), (0, 0.74, 0), 0.04, 10)
    p.cyl('cream', 0.45, 0.74, 0.77, 0, 0, 32); ring_y(p, 'chrome', 0.45, 0.465, 0.735, 0.775, 0, 0, 32)
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.3; x, z = 0.75 * math.cos(a), 0.75 * math.sin(a)
        p.cyl('chrome', 0.18, 0.0, 0.02, x, z, 16); seg_cyl(p, 'chrome', (x, 0.02, z), (x, 0.5, z), 0.03, 8); lathe(p, 'vinyl_r', [(0.17, 0.5), (0.18, 0.53), (0.17, 0.58), (0.0, 0.59)], x, z, 0.0, 18)
    return p
def arcade():
    """Fliperama sem texto (pivo: centro de tras, piso; frente +Z): gabinete com laterais curvas, tela com figuras, painel de controle
    com alavanca e botoes, letreiro iluminado com estrelas."""
    p = Piece(); side = [(0.0, 0.0), (0.7, 0.0), (0.7, 0.85), (0.55, 1.0), (0.45, 1.45), (0.55, 1.75), (0.55, 1.85), (0.0, 1.85)]
    for x in (-0.33, 0.3): prof_x(p, 'blue_p', x, x + 0.03, [(z, y) for (z, y) in side])
    p.box('dark', -0.3, 0.3, 0.02, 0.85, 0.0, 0.68); p.hull('dark', [(x, y, z) for x in (-0.3, 0.3) for (y, z) in ((0.85, 0.0), (0.85, 0.68), (1.0, 0.53), (1.0, 0.0))])
    p.hull('dark', [(x, y, z) for x in (-0.3, 0.3) for (y, z) in ((1.0, 0.0), (1.0, 0.53), (1.45, 0.43), (1.45, 0.0))]); p.box('dark', -0.3, 0.3, 1.45, 1.85, 0.0, 0.5)
    q = [(x, y, z) for x in (-0.24, 0.24) for (y, z) in ((1.06, 0.523), (1.4, 0.442))]; p.hull('neon', [(a, b, c + 0.004) for (a, b, c) in q] + q)
    for (x, y, m) in ((-0.1, 1.2, 'yellowp'), (0.1, 1.28, 'tile_r'), (0.0, 1.14, 'neon_r')): p.sphere(m, 0.025, x, y, 0.51 - (y - 1.06) * 0.24 + 0.012, 1)
    seg_cyl(p, 'dark', (-0.12, 0.93, 0.5), (-0.12, 1.03, 0.52), 0.008, 6); p.sphere('tile_r', 0.025, -0.12, 1.04, 0.52, 1)
    for (x, m) in ((0.05, 'yellowp'), (0.14, 'tile_r')): p.cyl(m, 0.022, 0.93, 0.95, x, 0.48, 10)
    p.box('yellowp', -0.27, 0.27, 1.55, 1.78, 0.5, 0.505)
    for x in (-0.15, 0.0, 0.15): p.hull('tile_r', [(x + 0.06 * math.cos(a), 1.665 + 0.06 * math.sin(a), 0.507) for a in np.linspace(0, 6.28, 6, endpoint=False)] + [(x, 1.665, 0.51)])
    return p
def jukebox():
    """Jukebox de arco (pivo: centro de tras, piso; frente +Z): corpo de madeira, arco de tubos coloridos, vidro com discos, grade."""
    p = Piece(); p.cham('dkwood', -0.42, 0.42, 0.0, 1.05, 0.0, 0.6, 0.02)
    arc_pts = [(0.42 * math.cos(a), 1.05 + 0.5 * math.sin(a)) for a in np.linspace(0, math.pi, 13)]
    prof_z(p, 'dkwood', 0.0, 0.6, [(0.42, 1.05)] + arc_pts[1:-1] + [(-0.42, 1.05)])
    for (r, m, z) in ((0.4, 'neon_r', 0.6), (0.34, 'yellowp', 0.605), (0.28, 'neon', 0.61)):
        pts = [(r * math.cos(a), 1.05 + r * 1.2 * math.sin(a), z) for a in np.linspace(0, math.pi, 13)]
        for u, v in zip(pts[:-1], pts[1:]): seg_cyl(p, m, u, v, 0.022, 6)
    p.box('glass', -0.22, 0.22, 1.05, 1.32, 0.6, 0.604); p.box('chrome', -0.3, 0.3, 0.2, 0.7, 0.6, 0.61)
    for y in np.arange(0.25, 0.68, 0.05): p.box('dark', -0.26, 0.26, y, y + 0.02, 0.61, 0.615)
    for k in range(5): p.cyl('film', 0.09, 1.08 + k * 0.035, 1.1 + k * 0.035, 0.0, 0.35, 16)
    return p
def condiments():
    p = Piece(); p.cham('chrome', -0.35, 0.35, 0.0, 0.95, 0.0, 0.45, 0.02); p.cham('cream', -0.37, 0.37, 0.95, 0.99, -0.01, 0.47, 0.006)
    for (x, m) in ((-0.2, 'tile_r'), (-0.08, 'yellowp'), (0.05, 'green_p')): lathe(p, m, [(0.035, 0.99), (0.035, 1.17), (0.012, 1.23)], x, 0.25, 0.0, 10)
    p.box('chrome', 0.15, 0.3, 0.99, 1.12, 0.15, 0.3); return p
def trash_can():
    p = Piece(); lathe(p, 'tile_r', [(0.22, 0.0), (0.24, 0.85), (0.25, 0.87), (0.1, 0.97), (0.0, 0.98)], sec=16); p.box('dark', -0.1, 0.1, 0.8, 0.88, 0.235, 0.26); return p

# ============================================================================ telao (pivo: origem, chao)
def screen():
    """Telao de 20 x 9 m: painel branco com paisagem pintada sem texto (ceu em 2 faixas, sol, 3 mesas, estrada e cacto), moldura
    preta, rufo; embaixo, parede de tabuas com mata-juntas; atras, 6 pilares de aco, escoras inclinadas, travessas, contraventamento,
    passarela com guarda-corpo, escada de marinheiro e sapatas."""
    p = Piece(); z = SZF; e = 0.004
    p.box('screen_w', -SW, SW, SY0, SY1, z - 0.12, z)
    p.box('sky1', -9.8, 9.8, 9.0, 13.3, z, z + e); p.box('sky2', -9.8, 9.8, 6.6, 9.0, z, z + e); p.box('sand', -9.8, 9.8, 4.7, 6.6, z, z + e)
    disc_z(p, 'sun', 1.1, z + e, z + 2 * e, 5.5, 11.0, 40)
    for (m, pts) in (('mesa', [(-9.8, 6.6), (-9.8, 8.2), (-8.6, 8.6), (-6.2, 8.6), (-5.6, 7.6), (-4.8, 6.6)]), ('mesa2', [(-3.5, 6.6), (-2.6, 7.8), (0.5, 7.9), (1.4, 6.6)]),
                     ('mesa', [(6.5, 6.6), (7.0, 7.4), (9.8, 7.5), (9.8, 6.6)]), ('dark', [(-1.6, 4.7), (1.6, 4.7), (0.12, 6.6), (-0.12, 6.6)])):
        prof_z(p, m, z + e, z + 2 * e, pts)
    for (a, b, c, d) in ((3.0, 3.35, 4.9, 7.2), (2.4, 2.65, 5.8, 6.7), (2.4, 3.0, 5.6, 5.85), (3.35, 3.95, 6.1, 6.35), (3.7, 3.95, 6.35, 7.0)): p.box('cactus', a, b, c, d, z + 2 * e, z + 3 * e)
    for k in range(-15, 16, 3): p.box('paint_w', k * 0.05 - 0.02, k * 0.05 + 0.02, 4.75 + abs(k) * 0.0 + 0.3 * (1 - abs(k) / 15) * 0 + 0.0, 4.75, z, z) if False else None
    for (y0, y1) in ((5.0, 5.3), (5.6, 5.85), (6.1, 6.3)): p.box('yellowp', -0.05, 0.05, y0, y1, z + 2 * e, z + 3 * e)
    p.box('dark', -10.3, 10.3, 4.4, 4.7, z - 0.15, z + 0.02); p.box('dark', -10.3, 10.3, 13.3, 13.6, z - 0.15, z + 0.02)
    for s in (-1, 1): p.box('dark', *sorted((s * 9.8, s * 10.3)), 4.7, 13.3, z - 0.15, z + 0.02)
    p.box('metal', -10.4, 10.4, 13.6, 13.7, z - 0.3, z + 0.08)
    p.box('boards', -10.3, 10.3, 0.0, 4.4, z - 0.2, z); p.box('concrete', -10.4, 10.4, -0.2, 0.05, z - 0.3, z + 0.1)
    for x in np.arange(-10.0, 10.05, 0.6): p.box('boards', x - 0.03, x + 0.03, 0.05, 4.4, z, z + 0.022)
    p.box('boards', -10.3, 10.3, 4.2, 4.36, z, z + 0.03)
    xs = (-10.0, -6.0, -2.0, 2.0, 6.0, 10.0); zc = z - 0.33; zb = z - 4.0
    for x in xs:
        p.box('steel_d', x - 0.12, x + 0.12, 0.05, 13.6, zc - 0.12, zc + 0.13); p.cham('concrete', x - 0.4, x + 0.4, -0.2, 0.15, zc - 0.4, zc + 0.4, 0.02)
        p.seg('steel_d', (x, 0.1, zb), (x, 10.5, zc - 0.12), 0.2, 0.2); p.cham('concrete', x - 0.35, x + 0.35, -0.2, 0.15, zb - 0.35, zb + 0.35, 0.02)
        for (y, f) in ((3.0, 3.0 / 10.4), (6.5, 6.5 / 10.4)): p.seg('steel', (x, y, zc - 0.12), (x, y, zb + (zc - zb) * f), 0.1, 0.1)
    for y in (2.5, 6.0, 9.5, 12.8): p.box('steel', -10.1, 10.1, y - 0.08, y + 0.08, zc - 0.2, zc - 0.12)
    for (a, b) in zip(xs[:-1], xs[1:]):
        for (y0, y1) in ((2.6, 5.9), (6.1, 9.4), (9.6, 12.7)):
            seg_cyl(p, 'steel', (a + 0.12, y0, zc - 0.16), (b - 0.12, y1, zc - 0.16), 0.02, 6); seg_cyl(p, 'steel', (b - 0.12, y0, zc - 0.16), (a + 0.12, y1, zc - 0.16), 0.02, 6)
    yw = 4.2; zw0, zw1 = zc - 1.3, zc - 0.2
    p.box('steel', -10.0, 10.0, yw, yw + 0.05, zw0, zw1)
    for x in np.arange(-10.0, 10.01, 2.0): p.cyl('steel', 0.025, yw + 0.05, yw + 1.1, x, zw0 + 0.04, 8)
    for y in (yw + 0.55, yw + 1.1): seg_cyl(p, 'steel', (-10.0, y, zw0 + 0.04), (10.0, y, zw0 + 0.04), 0.025, 8)
    for x in (-0.25, 0.25): p.seg('steel', (x, 0.0, zw0 - 0.3), (x, yw + 1.1, zw0 - 0.3), 0.05, 0.012)
    for y in np.arange(0.3, yw + 1.0, 0.3): seg_cyl(p, 'steel', (-0.25, y, zw0 - 0.3), (0.25, y, zw0 - 0.3), 0.014, 6)
    for y in (0.6, 2.6): p.seg('steel', (-0.25, y, zw0 - 0.3), (-0.25, y, zw0), 0.04, 0.01); p.seg('steel', (0.25, y, zw0 - 0.3), (0.25, y, zw0), 0.04, 0.01)
    return p

# ============================================================================ rampas, postes de som e carros
def ramp_h(r, r0): 
    d = r - r0
    if d <= 0 or d >= RDN: return 0.01
    return 0.01 + (RH * d / RUP if d < RUP else RH * (RDN - d) / (RDN - RUP))
def row_phi(r0):
    lims = [math.asin(min(1.0, 18.5 / (r0 + RDN)))]; c = (-16.2 - RC[1]) / r0
    if c < 1: lims.append(math.acos(c))
    return min(lims)
def row_segs(r0):
    ph = row_phi(r0); g = ROW_GAP.get(r0, 0.0)
    return [(-ph, ph)] if g <= 0 else [(-ph, -g), (g, ph)]
def ramp(r0):
    """Fileira de rampa em arco (pivo: origem, chao): subida curta para o telao e descida longa, de brita compactada; a 2a fileira
    se divide em 2 trechos para contornar a lanchonete."""
    p = Piece(); mp = lambda u, v: (RC[0] + v * math.sin(u), RC[1] + v * math.cos(u))
    vs = [r0, r0 + RUP * 0.5, r0 + RUP, r0 + RUP + 0.4, r0 + 1.8, r0 + 2.6, r0 + 3.4, r0 + RDN - 0.4, r0 + RDN]
    for (a, b) in row_segs(r0):
        us = np.linspace(a, b, max(12, int((b - a) * r0 / 0.6)))
        p.add('gravel_r', grid_map(us, vs, mp, lambda u, v: -0.1, lambda u, v: ramp_h(v, r0)))
    return p
def slots(r0):
    rm = r0 + 2.5; cars, posts = [], []
    for (a, b) in row_segs(r0):
        n = max(1, int((b - a) * rm / 3.6)); dp = (b - a) / n
        cars += [a + (i + 0.5) * dp for i in range(n)]; posts += [a + (i + 1) * dp for i in range(0, n - 1, 2)]
    return cars, posts
def speaker_post():
    """Poste de alto-falante (pivo: topo da rampa; ao longo de X): cano, caixa de ligacao, 2 alto-falantes de janela pendurados e
    lampadinha de orientacao."""
    p = Piece(); p.cyl('steel', 0.035, -0.4, 1.15, 0, 0, 10); p.cham('steel_d', -0.08, 0.08, 0.55, 0.8, -0.06, 0.06, 0.01)
    seg_cyl(p, 'steel', (-0.25, 1.15, 0), (0.25, 1.15, 0), 0.02, 8)
    for s in (-1, 1):
        x = s * 0.25; seg_cyl(p, 'steel', (x, 1.15, 0), (x, 1.05, 0), 0.008, 4)
        p.cham('steel_d', x - 0.09, x + 0.09, 0.8, 1.05, -0.06, 0.06, 0.015); disc_x(p, 'chrome', 0.07, *sorted((x + s * 0.09, x + s * 0.095)), 0.925, 0.0, 16)
        seg_cyl(p, 'dark', (x, 0.82, 0.0), (s * 0.05, 0.6, 0.0), 0.006, 4)
    p.sphere('neon', 0.03, 0, 1.2, 0, 1)
    return p
PITCH = math.degrees(math.atan2(ramp_h(0, -1.0) - ramp_h(4.0, 0.0), 3.0))
def car(mat='car_a', top='car_w'):
    """Carro dos anos 50 generico (pivo: meio entre os eixos, chao; frente +Z; inclinado como na rampa): carroceria com rabos de peixe,
    capota de 2 cores, vidros, para-choques cromados, grade, farois, lanternas, frisos laterais e rodas de faixa branca."""
    q = Piece()
    body = [(x, y, z) for x in (-0.95, 0.95) for (y, z) in ((0.32, -2.55), (0.32, 2.55), (0.8, 2.6), (0.92, 2.2), (0.95, -2.3), (0.82, -2.62))]
    q.hull(mat, body)
    for s in (-1, 1): q.hull(mat, [(s * x, y, z) for x in (0.78, 0.95) for (y, z) in ((0.9, -2.6), (1.12, -2.55), (0.95, -1.5))])
    cab = [(s * w, y, z) for s in (-1, 1) for (w, y, z) in ((0.86, 0.94, -1.25), (0.86, 0.94, 0.75), (0.72, 1.42, -0.95), (0.72, 1.42, 0.3))]
    q.hull('glass', cab); q.hull(top, [(s * 0.74, y, z) for s in (-1, 1) for (y, z) in ((1.38, -0.92), (1.38, 0.27), (1.46, -0.85), (1.46, 0.2))])
    for s in (-1, 1): q.hull(top, [(s * w, y, z) for w in (0.7, 0.87) for (y, z) in ((0.94, -0.3), (0.94, -0.15), (1.4, -0.4), (1.4, -0.28))])
    for (z0, z1) in ((2.55, 2.72), (-2.72, -2.55)): q.cham('chrome', -0.98, 0.98, 0.33, 0.5, z0, z1, 0.03)
    q.box('chrome', -0.6, 0.6, 0.52, 0.72, 2.56, 2.6)
    for k in range(5): q.box('dark', -0.56, 0.56, 0.54 + k * 0.035, 0.555 + k * 0.035, 2.6, 2.605)
    for s in (-1, 1):
        disc_z(q, 'chrome', 0.12, 2.5, 2.6, s * 0.72, 0.72, 16); disc_z(q, 'lamp_glass', 0.095, 2.6, 2.61, s * 0.72, 0.72, 16)
        disc_z(q, 'neon_r', 0.06, -2.62, -2.55, s * 0.86, 1.0, 12)
        q.box('chrome', *sorted((s * 0.95, s * 0.965)), 0.7, 0.73, -2.2, 2.3)
        for z in (-1.5, 1.5):
            disc_x(q, 'rubber', 0.36, *sorted((s * 0.74, s * 0.96)), 0.36, z, 24); disc_x(q, 'paint_w', 0.25, *sorted((s * 0.73, s * 0.965)), 0.36, z, 24)
            disc_x(q, 'chrome', 0.15, *sorted((s * 0.72, s * 0.972)), 0.36, z, 16)
        q.box('chrome', *sorted((s * 0.87, s * 0.9)), 0.95, 1.02, 0.6, 0.7)
    p = Piece(); p.merge(q, trimesh.transformations.rotation_matrix(math.radians(-PITCH), [1, 0, 0])); return p

# ============================================================================ parquinho (pivo: chao)
def swing_set():
    """Balanco de 3 lugares: 2 cavaletes de cano, travessa, correntes e assentos de borracha."""
    p = Piece(); h = 2.4; L1 = 3.6
    for x in (-L1 / 2, L1 / 2):
        for s in (-1, 1): seg_cyl(p, 'blue_p', (x, -0.3, s * 0.9), (x, h, 0.0), 0.04, 10)
        seg_cyl(p, 'blue_p', (x, 0.6, -0.68), (x, 0.6, 0.68), 0.03, 8)
    seg_cyl(p, 'blue_p', (-L1 / 2 - 0.1, h, 0), (L1 / 2 + 0.1, h, 0), 0.05, 12)
    for x in (-1.1, 0.0, 1.1):
        for dx in (-0.2, 0.2): seg_cyl(p, 'steel', (x + dx, h - 0.04, 0), (x + dx, 0.5, 0), 0.008, 4)
        p.cham('rubber', x - 0.24, x + 0.24, 0.45, 0.5, -0.1, 0.1, 0.01)
    return p
def slide():
    """Escorregador: escada de cano, plataforma com guarda-corpo e rampa de chapa com bordas (desce para +Z)."""
    p = Piece(); hp = 1.5
    for x in (-0.25, 0.25): seg_cyl(p, 'yellowp', (x, -0.3, -1.2), (x, hp + 0.9, -0.3), 0.03, 8)
    for k in range(5):
        yy = (k + 1) * 0.3; zz = -1.2 + (yy + 0.3) * 0.9 / 2.7; seg_cyl(p, 'steel', (-0.25, yy, zz), (0.25, yy, zz), 0.015, 6)
    p.box('steel', -0.3, 0.3, hp - 0.04, hp, -0.45, 0.1)
    for (x, z) in ((-0.3, 0.1), (0.3, 0.1)): seg_cyl(p, 'yellowp', (x, -0.3, z), (x, hp + 0.6, z), 0.03, 8)
    for s in (-1, 1): seg_cyl(p, 'yellowp', (s * 0.3, hp + 0.6, 0.1), (s * 0.3, hp + 0.6, -0.4), 0.025, 8)
    a = np.array([0, hp, 0.1]); b = np.array([0, 0.2, 2.6])
    for (dx, dy, m) in ((0.0, 0.0, 'chrome'),):
        p.hull(m, [a + np.array([s * 0.28, d, 0]) for s in (-1, 1) for d in (-0.03, 0.0)] + [b + np.array([s * 0.28, d, 0]) for s in (-1, 1) for d in (-0.03, 0.0)])
    for s in (-1, 1): p.hull('yellowp', [a + np.array([s * 0.28 + q, d, 0]) for q in (0.0, s * 0.03) for d in (0.0, 0.15)] + [b + np.array([s * 0.28 + q, d, 0]) for q in (0.0, s * 0.03) for d in (0.0, 0.15)])
    seg_cyl(p, 'yellowp', (0, 0.6, 1.9), (0, -0.3, 1.9), 0.03, 8)
    return p
def merry_go_round():
    """Gira-gira: disco de chapa com eixo e 4 barras de segurar."""
    p = Piece(); p.cyl('steel_d', 0.15, -0.3, 0.2, 0, 0, 12); p.cyl('orange_p', 1.0, 0.2, 0.26, 0, 0, 40); ring_y(p, 'steel', 1.0, 1.03, 0.19, 0.27, 0, 0, 40)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4; c, s = math.cos(a), math.sin(a)
        seg_cyl(p, 'steel', (0.9 * c, 0.26, 0.9 * s), (0.15 * c, 0.9, 0.15 * s), 0.02, 6)
    p.cyl('steel', 0.06, 0.26, 0.95, 0, 0, 10)
    return p

# ============================================================================ bilheteria, letreiro, cerca e terreno
def ticket_booth():
    """Bilheteria (pivo: centro, piso da ilha): casinha de reboco com rodape vermelho, janela de atendimento com balcao e vidro de
    correr no lado de entrada, porta e janelinha atras, telhado de 4 aguas vermelho com beiral, tubo de neon e luz; dentro, balcao,
    caixa registradora, maquina de ingressos e banqueta."""
    p = Piece(); x0, x1, z0, z1 = -1.2, 1.2, -1.0, 1.0; t = 0.12; hh = 2.45
    ring = sbox(x0, z0, x1, z1).difference(sbox(x0 + t, z0 + t, x1 - t, z1 - t))
    cuts = [sbox(x0 - 0.1, -0.7, x0 + t + 0.1, 0.7), sbox(x1 - t - 0.1, -0.45, x1 + 0.1, 0.45), sbox(-0.5, z1 - t - 0.1, 0.5, z1 + 0.1)]
    def cut_mesh(poly, ya, yb, holes):
        q = Piece(); ext_y(q, 'x', poly, ya, yb); m = q.parts['x'][0]
        for (box2, y0, y1) in holes:
            c = trimesh.creation.extrude_polygon(box2, y1 - y0); v = c.vertices.copy(); c.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1); c = D._fix(c)
            m = trimesh.boolean.difference([m, c], engine='manifold')
        return m
    holes = [(cuts[0], 0.95, 2.0), (cuts[1], -0.1, 2.15), (cuts[2], 1.3, 2.0)]
    p.add('tile_r', cut_mesh(ring, 0.0, 0.5, holes)); p.add('render', cut_mesh(ring, 0.5, hh, holes))
    ext_y(p, 'concrete', sbox(x0 + t, z0 + t, x1 - t, z1 - t), 0.0, 0.02)
    for (a, b) in ((-0.7, -0.66), (0.66, 0.7), (-0.02, 0.02)): p.box('metal', x0 - 0.01, x0 + 0.06, 0.95, 2.0, a, b)
    p.box('metal', x0 - 0.01, x0 + 0.06, 1.96, 2.0, -0.66, 0.66); p.box('glass', x0 + 0.01, x0 + 0.017, 1.0, 1.96, -0.66, -0.02); p.box('glass', x0 + 0.035, x0 + 0.042, 1.0, 1.96, 0.02, 0.66)
    p.cham('wood', x0 - 0.3, x0 + 0.5, 0.93, 0.97, -0.75, 0.75, 0.006); p.box('dkwood', x0 + t, x0 + 0.5, 0.02, 0.93, -0.7, 0.7)
    for (a, b) in ((-0.5, -0.46), (0.46, 0.5)): p.box('metal', -0.5 if a < 0 else 0.46, -0.46 if a < 0 else 0.5, 1.3, 2.0, z1 - t - 0.01, z1 + 0.01)
    p.box('metal', -0.46, 0.46, 1.3, 1.34, z1 - t - 0.01, z1 + 0.01); p.box('metal', -0.46, 0.46, 1.96, 2.0, z1 - t - 0.01, z1 + 0.01); p.box('glass', -0.46, 0.46, 1.34, 1.96, z1 - 0.063, z1 - 0.057)
    for (zz) in ((-0.45, -0.41), (0.41, 0.45)): p.box('steel', x1 - t - 0.01, x1 + 0.01, 0.0, 2.15, *zz)
    p.box('steel', x1 - t - 0.01, x1 + 0.01, 2.11, 2.15, -0.41, 0.41)
    ye = hh + 0.02; p.hull('roof_r', [(x, ye, z) for x in (x0 - 0.5, x1 + 0.5) for z in (z0 - 0.5, z1 + 0.5)] + [(x, ye + 0.75, 0.0) for x in (-0.5, 0.5)] + [(x, ye - 0.06, z) for x in (x0 - 0.5, x1 + 0.5) for z in (z0 - 0.5, z1 + 0.5)])
    p.box('render', x0 - 0.05, x1 + 0.05, hh, ye, z0 - 0.05, z1 + 0.05)
    E = sbox(x0 - 0.52, z0 - 0.52, x1 + 0.52, z1 + 0.52).difference(sbox(x0 - 0.5, z0 - 0.5, x1 + 0.5, z1 + 0.5)); ext_y(p, 'neon', E, ye - 0.06, ye - 0.03)
    p.cyl('lamp_glass', 0.1, ye - 0.1, ye - 0.06, x0 - 0.3, 0.0, 12)
    p.cham('metal', x0 + 0.2, x0 + 0.45, 0.97, 1.15, 0.25, 0.55, 0.01); p.box('dark', x0 + 0.22, x0 + 0.43, 1.15, 1.2, 0.28, 0.52)
    p.cham('tile_r', x0 + 0.15, x0 + 0.4, 0.97, 1.12, -0.5, -0.2, 0.01); p.box('paper', x0 + 0.1, x0 + 0.15, 1.02, 1.08, -0.42, -0.28)
    p.cyl('chrome', 0.18, 0.02, 0.04, 0.0, 0.0, 14); seg_cyl(p, 'chrome', (0, 0.04, 0), (0, 0.7, 0), 0.025, 8); lathe(p, 'vinyl_r', [(0.17, 0.7), (0.18, 0.73), (0.0, 0.76)], sec=16)
    return p
def marquee_sign():
    """Letreiro luminoso sem texto (pivo: chao; frente +Z): 2 pilares de aco, caixa azul com borda vermelha e lampadas, rolo de filme,
    estrela, tira de filme com furos e seta vermelha com lampadas apontando para a entrada."""
    p = Piece(); y0, y1 = 3.2, 5.6; x0, x1 = -2.8, 2.8
    for x in (-2.2, 2.2): p.box('steel_d', x - 0.12, x + 0.12, -0.2, y0 + 0.2, -0.12, 0.12); p.cham('concrete', x - 0.35, x + 0.35, -0.2, 0.15, -0.35, 0.35, 0.02)
    p.cham('sign_b', x0, x1, y0, y1, -0.2, 0.2, 0.02)
    for s in (-1, 1):
        zz = sorted((s * 0.2, s * 0.215))
        for (a, b, c, d) in ((x0, x1, y1 - 0.12, y1), (x0, x1, y0, y0 + 0.12), (x0, x0 + 0.12, y0 + 0.12, y1 - 0.12), (x1 - 0.12, x1, y0 + 0.12, y1 - 0.12)): p.box('trim_r', a, b, c, d, *zz)
        zl = s * 0.23
        for x in np.arange(x0 + 0.2, x1 - 0.1, 0.3): p.sphere('lamp_glass', 0.035, x, y1 - 0.06, zl, 1); p.sphere('lamp_glass', 0.035, x, y0 + 0.06, zl, 1)
        zf = sorted((s * 0.2, s * 0.21)); zf2 = sorted((s * 0.21, s * 0.22))
        disc_z(p, 'paint_w', 0.85, *zf, -1.4, 4.4, 40); disc_z(p, 'film', 0.18, *zf2, -1.4, 4.4, 20)
        for k in range(5):
            a = k * 2 * math.pi / 5 + 0.3; disc_z(p, 'sign_b', 0.2, *zf2, -1.4 + 0.5 * math.cos(a), 4.4 + 0.5 * math.sin(a), 16)
        pts = []
        for k in range(10):
            a = math.pi / 2 + k * math.pi / 5; r = 0.7 if k % 2 == 0 else 0.3; pts.append((1.2 + r * math.cos(a), 4.45 + r * math.sin(a)))
        prof_z(p, 'yellowp', *zf, pts)
        p.box('film', 0.0, 2.4, 3.4, 3.62, *zf)
        for x in np.arange(0.1, 2.4, 0.2): p.box('paint_w', x, x + 0.08, 3.44, 3.49, *zf2); p.box('paint_w', x, x + 0.08, 3.53, 3.58, *zf2)
    arrow = [(-2.4, 2.4), (1.6, 2.4), (1.6, 2.1), (2.6, 2.6), (1.6, 3.1), (1.6, 2.8), (-2.4, 2.8)]
    prof_z(p, 'trim_r', -0.08, 0.08, arrow)
    for s in (-1, 1):
        for x in np.arange(-2.2, 1.5, 0.3): p.sphere('lamp_glass', 0.035, x, 2.6, s * 0.09, 1)
    return p
def fence_w(L1=2.5):
    """Trecho de cerca de tabuas (pivo: inicio, chao; ao longo de +X, lado de fora em +Z): mourao, 2 travessas por dentro e tabuas
    verticais com fresta, capa."""
    p = Piece(); h = 1.9
    p.box('dkwood', -0.06, 0.06, -0.3, h + 0.05, -0.1, 0.02)
    for y in (0.35, 1.45): p.box('dkwood', 0.06, L1 - 0.06, y - 0.05, y + 0.05, -0.05, -0.0)
    xs = np.arange(0.07, L1 - 0.07, 0.16)
    for x in xs: p.box('wood', x, min(x + 0.14, L1 - 0.06), 0.06, h - 0.05, 0.0, 0.022)
    p.box('dkwood', 0.06, L1 - 0.06, h - 0.05, h, -0.05, 0.03)
    return p
def fence_post():
    p = Piece(); p.box('dkwood', -0.06, 0.06, -0.3, 1.95, -0.1, 0.02); return p
def lot_lamp():
    """Poste do patio (pivo: chao): coluna de aco, travessa com 2 refletores e caixa."""
    p = Piece(); lathe(p, 'steel', [(0.15, -0.2), (0.15, 0.3), (0.08, 0.5), (0.06, 6.0)], sec=14)
    seg_cyl(p, 'steel', (-0.6, 6.0, 0), (0.6, 6.0, 0), 0.04, 8)
    for s in (-1, 1):
        x = s * 0.55; p.cham('metal', x - 0.18, x + 0.18, 5.75, 6.0, -0.15, 0.15, 0.02); p.box('lamp_glass', x - 0.15, x + 0.15, 5.73, 5.75, -0.12, 0.12)
    p.box('metal', -0.1, 0.1, 1.2, 1.6, 0.06, 0.14); return p
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
SX0, SX1, SZ0, SZ1 = -24.0, 24.0, -26.0, 25.0
GY = -0.2
PLAY = sbox(-7.0, -16.5, 7.0, -14.4); APRON = off(OUTL, 1.0).difference(OUTL)
LOT = sbox(-20.0, -16.5, 20.0, 17.5).difference(PLAY).difference(off(OUTL, 1.0))
ISLAND = sbox(ISL[0], ISL[2], ISL[1], ISL[3]); ENTRY = sbox(GATE[0], 17.5, GATE[1], 22.0).difference(ISLAND)
SIDEWALK = sbox(SX0, 20.5, SX1, 22.0).difference(sbox(GATE[0], 17.5, GATE[1], 22.0)); STREET = sbox(SX0, 22.0, SX1, SZ1)
def site():
    """Terreno: patio de brita, calcada de placas em volta da lanchonete, parquinho de areia com borda de dormente, entrada de asfalto
    com ilha, gramado, calcada com juntas e rua com faixa amarela."""
    p = Piece(); box_ = sbox(SX0, SZ0, SX1, SZ1)
    ext_y(p, 'gravel', LOT, GY, 0.0); p.merge(paving(APRON, Y0)); p.merge(paving(SIDEWALK, Y0))
    ext_y(p, 'sand', PLAY.buffer(-0.15, join_style=2), GY, 0.05); ext_y(p, 'dkwood', PLAY.difference(PLAY.buffer(-0.15, join_style=2)), GY, 0.15)
    ext_y(p, 'asphalt', ENTRY, GY, 0.0); ext_y(p, 'asphalt', STREET, GY, 0.0); ext_y(p, 'curb', ISLAND, GY, Y0)
    grass = box_.difference(unary_union([LOT, PLAY, off(OUTL, 1.0), ENTRY, ISLAND, SIDEWALK, STREET])); ext_y(p, 'grass', grass, GY, 0.05)
    for x in np.arange(SX0 + 0.5, SX1 - 1.0, 3.0): p.box('yellowp', x, x + 1.5, 0.0, 0.004, 23.45, 23.57)
    for (x, s) in (((GATE[0] + ISL[0]) / 2, -1), ((ISL[1] + GATE[1]) / 2, 1)):
        z = 19.5; p.hull('paint_w', [(x + dx, y, z + s * dz) for (dx, dz) in ((-0.08, -0.9), (0.08, -0.9), (-0.08, 0.0), (0.08, 0.0)) for y in (0.0, 0.004)])
        p.hull('paint_w', [(x + dx, y, z + s * dz) for (dx, dz) in ((-0.35, 0.0), (0.35, 0.0), (0.0, 0.6)) for y in (0.0, 0.004)])
    return p
# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
pieces = {'w_win': wall('win'), 'w_port': wall('port'), 'w_door2': wall('door2'), 'w_plain': wall('plain'),
          'f_win': facet('win'), 'f_high': facet('high'), 'f_door': facet('door'), 'f_plain': facet('plain')}
pieces.update({
    'trims': trims(), 'roof': roof(), 'front_canopy': front_canopy(), 'floor': floor_piece(), 'plan': plan(), 'ceiling_light': ceiling_light(),
    'projector': projector(), 'rewind_bench': rewind_bench(), 'film_rack': film_rack(1.0), 'snack_counter': snack_counter(), 'menu_board': menu_board(),
    'table_stools': table_stools(), 'arcade': arcade(), 'jukebox': jukebox(), 'condiments': condiments(), 'trash_can': trash_can(),
    'wc': wc(), 'urinal': urinal(), 'sink_bank': sink_bank(2, 1.6), 'sink_one': sink_bank(1, 0.8),
    'screen': screen(), 'speaker_post': speaker_post(),
    'car_a': car('car_a'), 'car_b': car('car_b'), 'car_c': car('car_c'), 'car_d': car('car_d'),
    'swing_set': swing_set(), 'slide': slide(), 'merry_go_round': merry_go_round(), 'ticket_booth': ticket_booth(), 'marquee_sign': marquee_sign(),
    'fence_w': fence_w(2.5), 'fence_w2': fence_w(2.0), 'fence_w15': fence_w(1.5), 'fence_post': fence_post(), 'lot_lamp': lot_lamp(),
    'tree': tree(), 'tree_b': tree(5.0, 1.6, 'leaf2', 4), 'bush': bush(), 'site': site(),
    'door_leaf_glass': door_glass(0.88, 2.13, 0.05), 'door_leaf_metal': door_metal(0.8, 2.12), 'door_leaf_booth': door_metal(0.8, 2.08),
    'door_leaf_int': door_interior(0.86, 2.08), 'player_scale_ref': player_ref()})
for i, r0 in enumerate(ROWS): pieces[f'ramp_{i}'] = ramp(r0)

# ============================================================================ montagem
tg = ['house', 'ext']; y = Y0; yf = Y0 + 0.01
for x, k in ((-2, 'w_win'), (0, 'w_door2'), (2, 'w_win')): put(k, x, y, BR, 0, tg + ['front'])
for x, k in ((-2, 'w_port'), (0, 'w_port'), (2, 'w_win')): put(k, x, y, -BR, 180, tg + ['back'])
for (e, KK) in ((1, EAST_K), (-1, WEST_K)):
    for k in range(NF):
        fx, fz, ry = facet_pos(e, k); put('f_' + KK[k], fx, y, fz, ry, tg + (['front'] if fz > 0 else ['back']))
        if KK[k] == 'door':
            hx, hz = hinge(fx, fz, ry, -0.405, -0.12); put('door_leaf_metal', hx, yf, hz, ry, tg + (['front'] if fz > 0 else ['back']), door=90)
put('trims', 0, y, 0, 0, tg + ['front']); put('roof', 0, y, 0, 0, ['house', 'roof']); put('front_canopy', 0, y, BR, 0, tg + ['front'])
put('door_leaf_glass', -0.895, yf, BR - 0.12, 0, tg + ['front'], door=90); put('door_leaf_glass', 0.895, yf, BR - 0.12, 180, tg + ['front'], door=-90)
g = ['house']
for n in ('floor', 'plan', 'snack_counter'): put(n, 0, y, 0, 0, g)
put('door_leaf_int', -0.5 - 0.43, y + 0.005, ZPR, 0, g, door=-90)
for (x, z) in ((-1.5, 1.8), (1.5, 1.8), (2.6, -1.8), (5.0, 0.0), (-4.6, -1.8), (-4.6, 1.8), (-1.0, -2.5)): put('ceiling_light', x, y + CEIL - 0.01, z, 0, g + ['roof'])
# cabine de projecao
for x in (-1.5, 0.5): put('projector', x, y, -2.9, 0, g)
put('rewind_bench', -BX + t_ / 2, y, -2.5, 90, g); put('film_rack', XPR - t_ / 2, y, -1.85, -90, g)
# salao
put('menu_board', 3.9, y + CEIL - 0.92, 0.0, 0, g)
for (x, z) in ((-1.8, 0.4), (-1.8, 2.5), (2.3, 0.0)): put('table_stools', x, y, z, 0, g)
for x in (1.5, 2.3): put('arcade', x, y, -BR + T, 0, g)
put('jukebox', 2.0, y, BR - T, 180, g); put('condiments', 3.1, y, -BR + T + 0.002, 0, g); put('trash_can', -2.6, y, 3.4, 0, g)
# banheiros (masculino ao sul da divisoria, feminino ao norte)
xw = -BX - t_ / 2
put('sink_bank', xw, y, -1.6, -90, g); put('wc', xw, y, -3.1, -90, g)
for x in (-4.0, -5.2): put('urinal', x, y, -t_ / 2, 180, g)
put('wc', xw, y, 1.1, -90, g); put('wc', xw, y, 2.9, -90, g); put('sink_one', -5.6, y, t_ / 2, 0, g)
# telao, rampas, carros e alto-falantes
st = ['site']; put('site', 0, 0, 0, 0, st); put('screen', 0, 0, 0, 0, st)
CARS = ['car_a', 'car_b', 'car_c', 'car_d']; ci = 0
for i, r0 in enumerate(ROWS):
    put(f'ramp_{i}', 0, 0, 0, 0, st); cs, ps = slots(r0); rm = r0 + 2.5; yc = ramp_h(rm, r0)
    for j, ph in enumerate(cs):
        if (i * 7 + j * 3) % 5 == 2: continue                        # vagas vazias
        ry = math.degrees(ph) + 180 + (2.0 if j % 2 else -2.0); d = (ry + 45) % 90 - 45          # carros meio tortos na vaga
        if abs(d) < 3.5: ry += (3.5 - abs(d)) * (1 if d >= 0 else -1)
        put(CARS[ci % 4], RC[0] + rm * math.sin(ph), yc, RC[1] + rm * math.cos(ph), ry, st); ci += 1
    rp = r0 + RUP
    for ph in ps: put('speaker_post', RC[0] + rp * math.sin(ph), RH + 0.01, RC[1] + rp * math.cos(ph), math.degrees(ph), st)
for (x, z) in ((-9.0, 0.0), (9.0, 0.0), (-16.0, -3.0), (16.0, -3.0)): put('lot_lamp', x, 0, z, 0, st)
# parquinho
put('swing_set', -4.0, 0.05, -15.45, 0, st); put('slide', 0.5, 0.05, -15.45, 90, st); put('merry_go_round', 4.6, 0.05, -15.45, 0, st)
# entrada
bx, bz = 15.0, 18.9; put('ticket_booth', bx, Y0, bz, 0, st)
hx, hz = hinge(bx + 1.2, bz, 90, -0.405, -0.06); put('door_leaf_booth', hx, Y0 + 0.02, hz, 90, st, door=90)
put('marquee_sign', -8.0, 0, 19.5, 0, st)
def fence_run(x0, z0, ry, total, end_post):
    r = math.radians(ry); dx, dz = math.cos(r), -math.sin(r); n = int(total // 2.5 + 1e-6); rem = round(total - 2.5 * n, 3); s = 0.0
    for k in range(n): put('fence_w', x0 + dx * s, 0, z0 + dz * s, ry, st); s += 2.5
    if rem > 0.01: put({2.0: 'fence_w2', 1.5: 'fence_w15'}[rem], x0 + dx * s, 0, z0 + dz * s, ry, st); s += rem
    if end_post: put('fence_post', x0 + dx * s, 0, z0 + dz * s, ry, st)
fence_run(FX0, FZ1, 0, GATE[0] - FX0, True); fence_run(GATE[1], FZ1, 0, FX1 - GATE[1], False)
fence_run(FX1, FZ1, 90, FZ1 - FZ0, False); fence_run(FX1, FZ0, 180, FX1 - FX0, False); fence_run(FX0, FZ0, -90, FZ1 - FZ0, False)
for k, (x, z) in enumerate(((-15.0, -21.2), (-6.0, -21.6), (5.0, -21.3), (15.5, -21.5), (-17.5, 20.0), (-1.0, 19.8), (4.5, 19.9), (22.5, 10.0), (22.5, -6.0), (-22.5, 2.0))):
    put('tree' if k % 2 == 0 else 'tree_b', x, 0, z, 0, st)
for (x, z) in ((-11.6, 19.3), (-4.4, 19.3), (-12.8, 19.6), (7.0, 19.4), (9.5, 19.6)): put('bush', x, 0.05, z, 0, st)
put('player_scale_ref', 13.0, 0, 21.0); put('player_scale_ref', 1.0, Y0, 1.5, 0, ['house'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_level': Y0,
                       'building': {'shape': 'stadium', 'straight_x': [-BX, BX], 'radius': BR, 'facets_per_end': NF, 'floors': 1, 'ceiling': CEIL, 'parapet_top': HP},
                       'screen': {'z': SZF, 'width': 2 * SW, 'y': [SY0, SY1]},
                       'ramps': {'center': list(RC), 'rows_r0': ROWS, 'rise': RH, 'up': RUP, 'down': RDN,
                                 'note': 'ramp height h(r) = 0.01 + RH*d/RUP (d<RUP) or RH*(RDN-d)/(RDN-RUP), d = r - r0'},
                       'fence': {'x': [FX0, FX1], 'z': [FZ0, FZ1], 'gate_x': list(GATE)},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
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
