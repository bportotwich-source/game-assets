"""Kit 48: parque com concha acustica, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Palco de 22 x 12 m com cantos da frente arredondados, a 1,2 m do chao, com escada na frente e nas 2 laterais, ribalta e corrimaos.
Concha de 5 arcos semi-elipticos telescopicos (o maior com 9 m de raio e 8,2 m de altura), reboco creme por fora, forro de madeira
por dentro, friso dourado no arco da frente e refletores. Atras, o predio dos bastidores (14 x 6 m, tijolo) com corredor, 2 camarins
(bancada com espelho de lampadas, arara de figurino, sofa) e banheiro, porta para o palco e porta lateral com escada. No palco, banda
generica: bateria, piano de armario, cadeiras, estantes de partitura, caixas de som e pedestais de microfone. Gramado com 3 arcos de
bancos de praca virados para o palco, corredor de cascalho no meio, cangas de piquenique com cestas, postes de lanterna, varal de luzes,
arvores, cerca viva, bebedouro, lixeiras, carrinho de sorvete com guarda-sol e quiosque de lanches de tijolo com telhado de 4 aguas,
2 janelas de atendimento com toldo listrado, balcao e equipamentos por dentro. Calcada em volta de tudo.
Arte original e sem texto. Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
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
configurar(cores={'render': (238, 228, 204), 'plaster': (240, 236, 226), 'ceil': (244, 242, 236), 'concrete': (190, 186, 178), 'stone': (196, 186, 166),
                  'brick': (156, 70, 54), 'coping': (214, 208, 196), 'wood': (168, 120, 76), 'dkwood': (100, 68, 46), 'stage_w': (128, 88, 56),
                  'shell_in': (150, 110, 74), 'gold': (206, 168, 82), 'brass': (204, 166, 84), 'metal': (176, 180, 184), 'frame': (60, 62, 66),
                  'chrome': (216, 220, 224), 'steel': (110, 116, 122), 'steel_d': (52, 56, 60), 'iron': (34, 40, 36), 'bench_g': (40, 92, 62),
                  'trim': (90, 72, 56), 'door': (110, 46, 40), 'door_int': (204, 180, 140), 'lamp_glass': (255, 238, 196), 'dark': (34, 34, 36),
                  'porcelain': (244, 244, 240), 'mirror': (200, 214, 220), 'tile': (226, 230, 230), 'tile_b': (180, 70, 60),
                  'grass': (98, 150, 70), 'grass2': (112, 162, 78), 'gravel': (178, 170, 154), 'paver': (196, 192, 184), 'leaf': (86, 132, 64),
                  'leaf2': (112, 150, 72), 'bark': (110, 84, 60), 'roof_d': (70, 70, 74), 'gutter': (80, 80, 84), 'rubber': (28, 28, 30),
                  'paint_w': (240, 240, 236), 'sash': (236, 228, 204), 'pot': (176, 110, 80), 'plant': (70, 120, 60), 'flag_r': (204, 52, 46), 'flag_y': (240, 196, 50), 'flag_b': (52, 104, 180), 'flag_g': (60, 150, 84),
                  'fabric': (150, 60, 70), 'fabric2': (60, 80, 140), 'vinyl': (120, 40, 40), 'cymbal': (210, 176, 90), 'drum_w': (236, 232, 220),
                  'piano': (40, 30, 26), 'keys': (244, 242, 236), 'paper': (238, 234, 222), 'food_r': (200, 60, 50), 'food_y': (230, 190, 80),
                  'food_g': (110, 160, 70), 'basket': (176, 130, 76), 'cart_w': (240, 236, 226), 'umbrella': (246, 200, 60)},
           texturas={'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'stone': 'stone', 'brick': 'brick', 'wood': 'planks',
                     'dkwood': 'planks', 'stage_w': 'deck', 'shell_in': 'planks', 'grass': 'render', 'grass2': 'render', 'gravel': 'render',
                     'paver': 'render', 'roof_d': 'shingles'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'gold', 'brass', 'iron', 'cymbal', 'gutter'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.12
Y0 = 0.15                                  # calcadas e piso do quiosque
GY = -0.2
SH = 1.2                                   # topo do palco
STX, STZ0, STZ1, STR = 11.0, -8.0, 4.0, 3.0  # palco: x de -11 a 11, z de -8 a 4, cantos da frente com raio 3
RINGS = [(9.0 - 0.9 * k, 8.2 - 0.8 * k, -1.5 * k, (-1.5 * k - 1.6) if k < 4 else -8.0) for k in range(5)]   # (a, b, z frente, z fundo)
SHT = 0.28                                 # espessura dos arcos
BX0, BX1, BZ0, BZ1 = -7.0, 7.0, -14.0, -8.0  # bastidores (piso em SH)
BH = 5.4; BCEIL = 3.2; BROOF = 4.9         # bastidores: platibanda, forro, laje (sobre o piso)
BZP = -9.6                                 # divisoria do corredor
KX0, KX1, KZ0, KZ1 = 13.0, 19.0, -17.0, -13.0  # quiosque (piso em Y0)
KH = 2.8; KCEIL = 2.6
PX0, PX1, PZ0, PZ1 = -26.0, 26.0, -22.0, 24.0  # parque (calcada de 2,5 m por dentro da borda)
SX0, SX1, SZ0, SZ1 = -28.0, 28.0, -24.0, 26.0  # terreno
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

# ============================================================================ palco (pivo: origem; coordenadas absolutas)
STAGE = unary_union([sbox(-STX, STZ0, STX, STZ1 - STR), sbox(-STX + STR, STZ0, STX - STR, STZ1)] +
                    [Point(s * (STX - STR), STZ1 - STR).buffer(STR, 48) for s in (-1, 1)]).intersection(sbox(-STX, STZ0, STX, STZ1)).buffer(0)
YB = -0.15                                  # fundo das escadas e patamares (enterrado sob a calcada)
FSX = 1.5; FSZ = STZ1                       # escada da frente: x de -1,5 a 1,5, sai de z = 4 para +Z
SSZ0, SSZ1 = -2.5, -0.9                     # escadas laterais: z de -2,5 a -0,9
NST = 6; RISE = (SH - Y0) / (NST + 1); TREAD = 0.3
def stair_profile(base):
    """Degraus em (u, y): u = distancia a partir da face do palco (u = 0) para fora. Corpo de pedra, piso de cada degrau com capa."""
    pts = [(base, YB), (base + TREAD * NST, YB)]
    for k in range(1, NST + 1):
        u1 = base + TREAD * (NST + 1 - k); u0 = base + TREAD * (NST - k); y = Y0 + RISE * k - 0.03
        pts += [(u1, y), (u0, y)] if k == NST else [(u1, y)]
        if k < NST: pts.append((u0, y))
    caps = [(base + TREAD * (NST - k), base + TREAD * (NST + 1 - k) + 0.025, Y0 + RISE * k) for k in range(1, NST + 1)]
    return pts, caps
def stage():
    """Palco de 22 x 12 m com cantos da frente arredondados: embasamento de pedra com rodape, capa de pedra clara, piso de tablado;
    escada de 6 degraus na frente e nas 2 laterais com capas e corrimaos de ferro, ribalta de lampadas na borda da frente."""
    p = Piece()
    ext_y(p, 'stone', STAGE, GY, SH - 0.12)
    ext_y(p, 'coping', off(STAGE, 0.04).difference(off(STAGE, -0.3)), SH - 0.12, SH - 0.06)
    ext_y(p, 'concrete', off(STAGE, 0.03).difference(off(STAGE, -0.2)), Y0 - 0.02, Y0 + 0.2)          # rodape de concreto
    ext_y(p, 'stage_w', STAGE, SH - 0.06, SH)
    # escada da frente
    pts, caps = stair_profile(0.0)
    prof_x(p, 'stone', -FSX, FSX, [(FSZ + u, y) for (u, y) in pts])
    for (u0, u1, y) in caps: p.box('coping', -FSX - 0.02, FSX + 0.02, y - 0.03, y, FSZ + u0, FSZ + u1)
    for s in (-1, 1):
        for sw in (s * (FSX - 0.06),):
            zb, zt = FSZ + TREAD * NST - 0.15, FSZ + 0.15
            yb, yt = Y0 + RISE, Y0 + RISE * NST
            seg_cyl(p, 'iron', (sw, yb, zb), (sw, yb + 0.92, zb), 0.025, 8); seg_cyl(p, 'iron', (sw, yt, zt), (sw, yt + 0.92, zt), 0.025, 8)
            seg_cyl(p, 'iron', (sw, SH, FSZ - 0.35), (sw, SH + 0.92, FSZ - 0.35), 0.025, 8)
            seg_cyl(p, 'iron', (sw, yb + 0.92, zb), (sw, yt + 0.92, zt), 0.022, 8); seg_cyl(p, 'iron', (sw, yt + 0.92, zt), (sw, SH + 0.92, FSZ - 0.35), 0.022, 8)
            seg_cyl(p, 'iron', (sw, yb + 0.46, zb), (sw, yt + 0.46, zt), 0.012, 6)
            for y_, z_ in ((yb, zb), (yt, zt)): p.sphere('iron', 0.04, sw, y_ + 0.95, z_, 1)
    # escadas laterais (leste; a oeste e o espelho)
    q = Piece(); pts, caps = stair_profile(0.0)
    prof_z(q, 'stone', SSZ0, SSZ1, [(STX + u, y) for (u, y) in pts])
    for (u0, u1, y) in caps: q.box('coping', STX + u0, STX + u1, y - 0.03, y, SSZ0 - 0.02, SSZ1 + 0.02)
    for sz in (SSZ0 + 0.06, SSZ1 - 0.06):
        xb, xt = STX + TREAD * NST - 0.15, STX + 0.15
        yb, yt = Y0 + RISE, Y0 + RISE * NST
        seg_cyl(q, 'iron', (xb, yb, sz), (xb, yb + 0.92, sz), 0.025, 8); seg_cyl(q, 'iron', (xt, yt, sz), (xt, yt + 0.92, sz), 0.025, 8)
        seg_cyl(q, 'iron', (xb, yb + 0.92, sz), (xt, yt + 0.92, sz), 0.022, 8); seg_cyl(q, 'iron', (xb, yb + 0.46, sz), (xt, yt + 0.46, sz), 0.012, 6)
        for y_, x_ in ((yb, xb), (yt, xt)): q.sphere('iron', 0.04, x_, y_ + 0.95, sz, 1)
    p.merge(q); p.merge(q, mirror_x())
    # ribalta: lampadas em caixinhas na borda da frente
    for x in np.arange(-7.5, 7.6, 1.0):
        if abs(x) < FSX + 0.3: continue
        p.box('steel_d', x - 0.14, x + 0.14, SH, SH + 0.08, FSZ - 0.36, FSZ - 0.2)
        p.hull('lamp_glass', [(x + a, SH + 0.08, FSZ - 0.355) for a in (-0.1, 0.1)] + [(x + a, SH + 0.03, FSZ - 0.205) for a in (-0.1, 0.1)] +
               [(x + a, SH + 0.081, FSZ - 0.34) for a in (-0.1, 0.1)])
    return p

# ============================================================================ concha acustica (pivo: origem)
def semi(a, b, n=72): return Polygon([(a * math.cos(t), b * math.sin(t)) for t in np.linspace(0, math.pi, n)])
def arch(a0, b0, a1, b1, n=72):
    """Faixa semi-eliptica entre a elipse externa (a0, b0) e a interna (a1, b1), apoiada em y = 0."""
    inner = unary_union([semi(a1, b1, n), sbox(-a1, -1.0, a1, 0.0)])
    return semi(a0, b0, n).difference(inner).buffer(0)
def lift(poly, dy):
    from shapely import affinity
    return affinity.translate(poly, 0, dy)
def shell():
    """Concha de 5 arcos semi-elipticos telescopicos: reboco creme por fora, forro de madeira por dentro, testa de cada arco com o degrau
    fechado ate o arco seguinte, friso dourado e fileira de lampadas no arco da frente, vara de refletores e pinaculo dourado."""
    p = Piece()
    for k, (a, b, zf, zb) in enumerate(RINGS):
        ext(p, 'render', lift(arch(a, b, a - 0.1, b - 0.1), SH), zb if k < 4 else zb + 0.004, zf)
        ext(p, 'shell_in', lift(arch(a - 0.1, b - 0.1, a - SHT, b - SHT), SH), zb if k < 4 else zb + 0.004, zf)
        if k < 4:
            an, bn = RINGS[k + 1][0], RINGS[k + 1][1]
            ext(p, 'shell_in', lift(arch(a - SHT, b - SHT, an, bn), SH), zb, zb + 0.05)
        # cordao de reboco na testa de cada arco
        ext(p, 'render', lift(arch(a + 0.04, b + 0.04, a - 0.06, b - 0.06), SH + 0.0), zf, zf + 0.05) if k == 0 else None
    a, b = RINGS[0][0], RINGS[0][1]
    ext(p, 'gold', lift(arch(a - 0.1, b - 0.1, a - 0.16, b - 0.16), SH), 0.0, 0.03)
    for t in np.linspace(0.03, math.pi - 0.03, 41):
        r_a, r_b = a - 0.22, b - 0.22; p.sphere('lamp_glass', 0.04, r_a * math.cos(t), SH + r_b * math.sin(t), 0.03, 1)
    # vara de refletores dentro do 3o arco
    a2, b2 = RINGS[2][0] - SHT, RINGS[2][1] - SHT; yv = 5.4; zv = -3.8
    xe = a2 * math.sqrt(1 - (yv / b2) ** 2)
    seg_cyl(p, 'steel_d', (-xe - 0.05, SH + yv, zv), (xe + 0.05, SH + yv, zv), 0.03, 10)
    for x in np.linspace(-2.6, 2.6, 6):
        seg_cyl(p, 'steel_d', (x, SH + yv - 0.02, zv), (x, SH + yv - 0.2, zv), 0.012, 6)
        p.box('steel_d', x - 0.13, x - 0.11, SH + yv - 0.42, SH + yv - 0.18, zv - 0.03, zv + 0.03); p.box('steel_d', x + 0.11, x + 0.13, SH + yv - 0.42, SH + yv - 0.18, zv - 0.03, zv + 0.03)
        c0 = np.array([x, SH + yv - 0.32, zv - 0.16]); c1 = np.array([x, SH + yv - 0.42, zv + 0.2])
        seg_cyl(p, 'dark', c0, c1, 0.1, 14); seg_cyl(p, 'lamp_glass', c1, c1 + (c1 - c0) / np.linalg.norm(c1 - c0) * 0.01, 0.085, 14)
    # pinaculo dourado no alto do arco da frente
    lathe(p, 'gold', [(0.2, -0.03), (0.14, 0.12), (0.06, 0.3), (0.16, 0.46), (0.06, 0.62), (0.0, 0.95)], 0.0, -0.8, SH + b, 16)
    return p

# ============================================================================ bastidores: modulos de tijolo (pivo: face externa, cota do piso SH; dentro em -Z)
def bs_core(p, holes, xa, xb):
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([GY - SH, 0.0, 0.3, BROOF, BH] + [v for h in holes for v in h[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'stone' if k == 1 else 'concrete'
        if k == 0: return 'brick' if cy > BROOF else 'plaster'
        return 'stone' if cy < 0.3 else 'brick'
    for m, mesh in grid_solid(xs, ys, [-T, -0.12, 0.0], cell).items(): p.add(m, mesh)
    prof_x(p, 'stone', xa, xb, [(0.0, 0.3), (0.04, 0.3), (0.04, 0.33), (0.0, 0.36)])                     # capa do embasamento
    for y in (2.9,):                                                                                    # friso de tijolo em pe
        prof_x(p, 'coping', xa, xb, [(0.0, y), (0.025, y), (0.025, y + 0.08), (0.0, y + 0.08)])
def bs_door(p, lamp=True):
    for s in (-1, 1):
        a, b = sorted((s * 0.5, s * 0.46)); p.box('trim', a, b, 0.0, 2.3, -0.2, -0.04)
    p.box('trim', -0.46, 0.46, 2.26, 2.3, -0.2, -0.04)
    p.cham('steel', -0.5, 0.5, -0.02, 0.006, -T + 0.004, 0.03, 0.003)
    p.box('stone', -0.62, 0.62, 2.3, 2.52, 0.0, 0.03)                                                     # verga de pedra
    if lamp: p.merge(wall_lantern(), tr(0.8, 2.45, 0.0))
def bs_mod(kind='plain', tl=0.0, tr_=0.0):
    """plain (tijolo), win (janela de guilhotina alta), door (porta com verga de pedra e arandela), door_s (porta para o palco)."""
    p = Piece(); xa, xb = -W / 2 + tl, W / 2 - tr_
    if kind == 'win':
        bs_core(p, [(-0.55, 0.55, 1.5, 2.6)], xa, xb); window(p, 1.1, 1.5, 2.6, 2)
    elif kind in ('door', 'door_s'):
        bs_core(p, [(-0.5, 0.5, 0.0, 2.3)], xa, xb); bs_door(p, kind == 'door')
    else:
        bs_core(p, [], xa, xb)
    return p

# ============================================================================ quiosque: modulos de tijolo (pivo: face externa, cota do piso Y0)
def ki_core(p, holes, xa, xb):
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([GY - Y0, 0.0, 0.3, 1.2, KH] + [v for h in holes for v in h[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        if k == 0: return 'tile' if cy < 1.2 else 'plaster'
        return 'concrete' if cy < 0.3 else 'brick'
    for m, mesh in grid_solid(xs, ys, [-T, -0.12, 0.0], cell).items(): p.add(m, mesh)
def awning(p, w=1.9, d=0.85, y0=2.18, y1=2.6, n=9):
    """Toldo listrado inclinado com bambinela e bracos de ferro (pivo: face da parede, centro)."""
    cols = ['flag_r', 'paint_w']; xs = np.linspace(-w / 2, w / 2, n + 1)
    for i in range(n):
        a, b = xs[i], xs[i + 1]; m = cols[i % 2]
        p.hull(m, [(x, y, z) for x in (a, b) for (y, z) in ((y1, 0.01), (y1 - 0.012, 0.01), (y0, d), (y0 - 0.012, d))])
        p.hull(m, [(x, y, z) for x in (a, b) for (y, z) in ((y0, d), (y0 - 0.18, d), (y0, d + 0.012), (y0 - 0.18, d + 0.012))])
    for s in (-1, 1):
        x = s * (w / 2 - 0.03)
        seg_cyl(p, 'iron', (x, y0 - 0.45, 0.0), (x, y0 - 0.03, d - 0.02), 0.012, 6); p.box('iron', x - 0.03, x + 0.03, y0 - 0.5, y0 - 0.4, 0.0, 0.015)
    seg_cyl(p, 'iron', (-w / 2, y1 + 0.02, 0.03), (w / 2, y1 + 0.02, 0.03), 0.025, 8)
def ki_mod(kind='plain', tl=0.0, tr_=0.0):
    """plain, svc (janela de atendimento com balcao de fora e toldo listrado), door (porta dos fundos), sign (placa redonda de picole)."""
    p = Piece(); xa, xb = -W / 2 + tl, W / 2 - tr_
    if kind == 'svc':
        ki_core(p, [(-0.75, 0.75, 0.95, 2.05)], xa, xb)
        for s in (-1, 1):
            a, b = sorted((s * 0.75, s * 0.71)); p.box('trim', a, b, 0.99, 2.05, -0.2, -0.04)
        p.box('trim', -0.71, 0.71, 2.01, 2.05, -0.2, -0.04)
        p.cham('wood', -0.86, 0.86, 0.95, 0.99, -T - 0.02, 0.32, 0.006)
        for s in (-1, 1): seg_cyl(p, 'iron', (s * 0.7, 0.6, 0.0), (s * 0.7, 0.948, 0.28), 0.012, 6)
        p.box('stone', -0.88, 0.88, 2.05, 2.15, 0.0, 0.03)
        awning(p)
    elif kind == 'door':
        ki_core(p, [(-0.5, 0.5, 0.0, 2.3)], xa, xb); bs_door(p, True)
    else:
        ki_core(p, [], xa, xb)
        if kind == 'sign':
            disc_z(p, 'trim', 0.46, 0.0, 0.04, 0.0, 1.75, 32); disc_z(p, 'cart_w', 0.42, 0.04, 0.06, 0.0, 1.75, 32)
            p.hull('food_y', [(x, y, z) for (x, y) in ((-0.13, 1.85), (0.13, 1.85), (0.0, 1.45)) for z in (0.06, 0.072)])
            for (x, y, m) in ((-0.06, 1.9, 'food_r'), (0.07, 1.92, 'food_g'), (0.0, 2.0, 'paint_w')):
                c = trimesh.creation.cylinder(radius=0.09, height=0.014, sections=20); c.apply_translation([x, y, 0.07 + {'food_r': 0.0, 'food_g': 0.002, 'paint_w': 0.004}[m]]); p.add(m, c)
    return p

# ============================================================================ coberturas, pisos e plantas (pivo: origem; bastidores na cota SH, quiosque na cota Y0)
BB = sbox(BX0, BZ0, BX1, BZ1); BI = off(BB, -T)
KB = sbox(KX0, KZ0, KX1, KZ1); KI = off(KB, -T)
def bs_roof():
    """Bastidores: forro com plafons, laje com manta, rufo da platibanda, alcapao, 2 exaustores e buzinote com condutor."""
    p = Piece()
    ext_y(p, 'ceil', BI, BCEIL, BCEIL + 0.03)
    for (x, z) in ((-5.0, -8.9), (-2.0, -8.9), (2.0, -8.9), (5.0, -8.9), (-4.0, -11.8), (4.0, -11.8), (0.0, -11.8)):
        p.cyl('trim', 0.2, BCEIL - 0.01, BCEIL, x, z, 20); p.cyl('lamp_glass', 0.17, BCEIL - 0.06, BCEIL - 0.01, x, z, 20)
    ext_y(p, 'concrete', BI, BROOF, BROOF + 0.2); ext_y(p, 'dark', off(BI, -0.01), BROOF + 0.2, BROOF + 0.215)
    ext_y(p, 'coping', off(BB, 0.04).difference(off(BB, -T - 0.04)), BH, BH + 0.06)
    y = BROOF + 0.215
    p.box('metal', -5.4, -4.6, y, y + 0.3, -12.4, -11.6); p.box('metal', -5.45, -4.55, y + 0.3, y + 0.34, -12.45, -11.55)
    for (x, z) in ((2.0, -11.5), (4.5, -10.0)):
        p.cyl('metal', 0.14, y, y + 0.5, x, z, 14); lathe(p, 'metal', [(0.0, y + 0.75), (0.3, y + 0.58), (0.26, y + 0.54)], x, z, 0.0, 16)
    for sx in (-1, 1):
        for (za, zb_) in ((BZ1 - T, BZ1 + 0.04), (BZ0 - 0.04, BZ0 + T)):
            xa_, xb_ = sorted((sx * BX1, sx * (BX1 + 0.04))); p.box('stone', xa_, xb_, 0.3, 0.33, za, zb_)
            xa_, xb_ = sorted((sx * BX1, sx * (BX1 + 0.025))); p.box('coping', xa_, xb_, 2.9, 2.98, za if za > BZ1 - 1 else za, zb_ if za > BZ1 - 1 else zb_)
    p.box('gutter', BX1 - 0.2, BX1 + 0.12, y + 0.0, y + 0.12, -12.6, -12.4)
    seg_cyl(p, 'gutter', (BX1 + 0.06, y + 0.02, -12.5), (BX1 + 0.06, -SH + 0.16, -12.5), 0.05, 10)
    return p
def ki_roof():
    """Quiosque: forro, telhado de 4 aguas de telhas com beiral, cumeeira e espigoes, testeira, calhas e 2 condutores."""
    p = Piece(); o = 0.4
    ext_y(p, 'ceil', KI, KCEIL, KCEIL + 0.03)
    for x in (14.6, 17.4): p.box('trim', x - 0.5, x + 0.5, KCEIL - 0.008, KCEIL, -15.1, -14.9); p.box('lamp_glass', x - 0.46, x + 0.46, KCEIL - 0.03, KCEIL - 0.008, -15.08, -14.92)
    X0, X1, Z0, Z1 = KX0 - o, KX1 + o, KZ0 - o, KZ1 + o; ye, yt, yr = 2.75, 2.9, 4.0
    zc = (Z0 + Z1) / 2; h = (Z1 - Z0) / 2; xr0, xr1 = X0 + h, X1 - h
    p.hull('roof_d', [(x, y, z) for x in (X0, X1) for z in (Z0, Z1) for y in (ye, yt)] + [(xr0, yr, zc), (xr1, yr, zc)])
    seg_cyl(p, 'dark', (xr0, yr + 0.02, zc), (xr1, yr + 0.02, zc), 0.06, 8)
    for (x, z, xx) in ((X0, Z0, xr0), (X0, Z1, xr0), (X1, Z0, xr1), (X1, Z1, xr1)): seg_cyl(p, 'dark', (x, yt + 0.02, z), (xx, yr + 0.02, zc), 0.05, 8)
    for (x0, x1, z0, z1) in ((X0 - 0.025, X1 + 0.025, Z1, Z1 + 0.025), (X0 - 0.025, X1 + 0.025, Z0 - 0.025, Z0), (X0 - 0.025, X0, Z0, Z1), (X1, X1 + 0.025, Z0, Z1)):
        p.box('trim', x0, x1, ye - 0.04, yt, z0, z1)
    for zz, sg, xs_ in ((Z1 + 0.025, 1, (KX1 - 0.3,)), (Z0 - 0.025, -1, (KX0 + 0.3, KX1 - 0.3))):
        prof = [(0.0, ye + 0.06), (0.0, ye - 0.06), (0.12, ye - 0.06), (0.14, ye + 0.06), (0.12, ye + 0.06), (0.105, ye - 0.04), (0.015, ye - 0.04), (0.015, ye + 0.06)]
        prof_x(p, 'gutter', X0 - 0.025, X1 + 0.025, [(zz + sg * u, y) for (u, y) in prof])
        zw = KZ1 + 0.06 if sg > 0 else KZ0 - 0.06; zc_ = zz + sg * 0.065
        for x in xs_:
            seg_cyl(p, 'gutter', (x, ye - 0.05, zc_), (x, ye - 0.3, zc_), 0.04, 10); seg_cyl(p, 'gutter', (x, ye - 0.3, zc_), (x, ye - 0.55, zw), 0.04, 10)
            seg_cyl(p, 'gutter', (x, ye - 0.55, zw), (x, -Y0 + 0.08, zw), 0.04, 10)
            for yy in (0.8, 1.9): p.box('gutter', x - 0.05, x + 0.05, yy, yy + 0.03, *sorted((zw, KZ1 if sg > 0 else KZ0)))
    return p
CORR = sbox(BX0 + T, BZP, BX1 - T, BZ1 - T)
RM_A = sbox(BX0 + T, BZ0 + T, -1.0, BZP); RM_W = sbox(-1.0, BZ0 + T, 1.0, BZP); RM_B = sbox(1.0, BZ0 + T, BX1 - T, BZP)
def checker(p, poly, y0, y1, step, ma, mb, ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step, oz + j * step, ox + (i + 1) * step, oz + (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
def bs_floor():
    """Bastidores: aterro sobre o palco, assoalho no corredor e nos camarins, ladrilho no banheiro (cota do piso em 0)."""
    p = Piece(); ext_y(p, 'concrete', BI, GY - SH + 0.02, -0.012)
    ext_y(p, 'wood', unary_union([CORR, RM_A, RM_B]).buffer(0).difference(RM_W), -0.012, 0.0)
    checker(p, RM_W, -0.012, 0.0, 0.2, 'tile', 'tile_b')
    return p
def ki_floor():
    p = Piece(); ext_y(p, 'concrete', KI, GY - Y0 + 0.02, -0.012); checker(p, KI, -0.012, 0.0, 0.3, 'tile', 'tile_b', 0.0, 0.0); return p
def bs_plan():
    """Divisoria do corredor com 3 portas, paredes entre camarins e banheiro, rodapes nas paredes externas."""
    p = Piece(); L1 = (BX1 - T) - (BX0 + T)
    cuts = [(c - (BX0 + T), 0.9, 0.0, 2.1, 'door') for c in (-3.9, 0.0, 3.9)]
    p.merge(run_wall(L1, BCEIL, cuts), tr(BX0 + T, 0, BZP))
    for x in (-1.0, 1.0): p.merge(run_wall(BZP - (BZ0 + T), BCEIL), rot_y(-90, (x, 0, BZ0 + T)))
    band = BI.difference(off(BI, -0.016))
    dr = unary_union([sbox(-0.6, BZ1 - T - 0.1, 0.6, BZ1 - T + 0.1), sbox(BX1 - T - 0.1, -9.6, BX1 - T + 0.1, -8.4)] +
                     [sbox(x - 0.09, BZ0, x + 0.09, BZP + 0.1) for x in (-1.0, 1.0)] + [sbox(-99, BZP - 0.09, 99, BZP + 0.09)])
    ext_y(p, 'trim', band.difference(dr), 0.0, 0.1)
    return p
def ki_plan():
    p = Piece(); band = KI.difference(off(KI, -0.016))
    dr = sbox(15.4, KZ0 + T - 0.1, 16.6, KZ0 + T + 0.1)
    ext_y(p, 'trim', band.difference(dr), 0.0, 0.1); return p
def bs_stairs():
    """Patamar e escada de 6 degraus de concreto na porta lateral dos bastidores, com guarda-corpo de ferro (pivo: origem)."""
    p = Piece(); x0, z0, z1 = BX1, -9.6, -8.4; xl = BX1 + 1.2
    p.box('concrete', x0, xl, YB, SH - 0.03, z0, z1); p.box('coping', x0, xl + 0.025, SH - 0.03, SH, z0 - 0.02, z1 + 0.02)
    pts, caps = stair_profile(0.0)
    prof_z(p, 'concrete', z0, z1, [(xl + u, y) for (u, y) in pts])
    for (u0, u1, y) in caps: p.box('coping', xl + u0, xl + u1, y - 0.03, y, z0 - 0.02, z1 + 0.02)
    for sz in (z0 + 0.04, z1 - 0.04):
        xb, xt = xl + TREAD * NST - 0.15, xl + 0.15; yb, yt = Y0 + RISE, Y0 + RISE * NST
        pts3 = [(xb, yb, sz), (xt, yt, sz), (x0 + 0.1, SH, sz)] if sz < z1 - 0.1 else [(xb, yb, sz), (xt, yt, sz), (x0 + 0.1, SH, sz)]
        for (x, y_, z) in pts3: seg_cyl(p, 'iron', (x, y_, z), (x, y_ + 0.95, z), 0.022, 8)
        seg_cyl(p, 'iron', (xb, yb + 0.95, sz), (xt, yt + 0.95, sz), 0.02, 8); seg_cyl(p, 'iron', (xt, yt + 0.95, sz), (x0 + 0.1, SH + 0.95, sz), 0.02, 8)
        seg_cyl(p, 'iron', (xb, yb + 0.45, sz), (xt, yt + 0.45, sz), 0.012, 6); seg_cyl(p, 'iron', (xt, yt + 0.45, sz), (x0 + 0.1, SH + 0.45, sz), 0.012, 6)
        for xx in np.arange(x0 + 0.25, xl - 0.05, 0.12): seg_cyl(p, 'iron', (xx, SH, sz), (xx, SH + 0.45, sz), 0.008, 6)
    return p

# ============================================================================ banda no palco (pivo: centro, piso; frente para +Z)
def drum(p, r, d, x, y, z, ax='z', shell='drum_w'):
    """Tambor: casco, 2 aros cromados e peles (eixo em z ou y)."""
    if ax == 'z':
        disc_z(p, shell, r, z - d / 2 + 0.02, z + d / 2 - 0.02, x, y, 24)
        for zz in (z - d / 2, z + d / 2 - 0.02): disc_z(p, 'chrome', r + 0.012, zz, zz + 0.02, x, y, 24)
        for zz in (z - d / 2 - 0.004, z + d / 2 - 0.0): disc_z(p, 'paper', r - 0.004, zz, zz + 0.004, x, y, 24)
    else:
        p.cyl(shell, r, y - d / 2 + 0.02, y + d / 2 - 0.02, x, z, 24)
        for yy in (y - d / 2, y + d / 2 - 0.02): ring_y(p, 'chrome', r - 0.01, r + 0.012, yy, yy + 0.02, x, z, 24)
        p.cyl('paper', r - 0.004, y + d / 2 - 0.016, y + d / 2 + 0.004, x, z, 24)
def tripod(p, x, z, y1, r=0.28, mat='chrome'):
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.5; seg_cyl(p, mat, (x, 0.35, z), (x + r * math.cos(a), 0.0, z + r * math.sin(a)), 0.01, 6)
    seg_cyl(p, mat, (x, 0.0, z), (x, y1, z), 0.014, 8)
def cymbal(p, x, y, z, r=0.22, tilt=0.12):
    m = trimesh.creation.cone(radius=r, height=0.035, sections=28); m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    m.apply_transform(trimesh.transformations.rotation_matrix(tilt, [1, 0, 0]))
    m.apply_translation([x, y, z]); p.add('cymbal', m)
def drum_kit():
    """Bateria sobre um praticavel: bumbo, caixa, 2 tons, surdo, chimbal, 2 pratos e banco (pivo: centro do praticavel)."""
    p = Piece(); H = 0.3
    p.cham('dkwood', -1.3, 1.3, 0.0, H - 0.02, -1.2, 1.2, 0.01); p.box('dark', -1.32, 1.32, H - 0.02, H, -1.22, 1.22)
    y = H
    drum(p, 0.28, 0.42, 0.0, y + 0.3, 0.25, 'z', 'flag_r')
    for s in (-1, 1): seg_cyl(p, 'chrome', (s * 0.2, y + 0.12, 0.42), (s * 0.3, y, 0.55), 0.01, 6)
    disc_z(p, 'dark', 0.12, 0.465, 0.47, 0.0, y + 0.3, 20)
    drum(p, 0.17, 0.14, 0.38, y + 0.62, -0.1, 'y', 'flag_r'); tripod(p, 0.38, -0.1, 0.55);
    for (x, z, r, d) in ((-0.15, 0.2, 0.13, 0.2), (0.17, 0.2, 0.14, 0.22)): drum(p, r, d, x, y + 0.82, z, 'y', 'flag_r')
    seg_cyl(p, 'chrome', (0.0, y + 0.58, 0.22), (0.0, y + 0.72, 0.2), 0.014, 8)
    drum(p, 0.2, 0.42, -0.5, y + 0.3, -0.25, 'y', 'flag_r')
    for k in range(3):
        a = k * 2 * math.pi / 3; seg_cyl(p, 'chrome', (-0.5 + 0.2 * math.cos(a), y + 0.2, -0.25 + 0.2 * math.sin(a)), (-0.5 + 0.26 * math.cos(a), y, -0.25 + 0.26 * math.sin(a)), 0.01, 6)
    tripod(p, 0.72, 0.1, 0.95); p.box('chrome', 0, 0, 0, 0, 0, 0) if False else None
    for yy in (0.92, 0.95): cymbal(p, 0.72, y + yy, 0.1, 0.18, 0.0)
    for (x, z, h) in ((-0.55, 0.35, 1.3), (0.65, 0.5, 1.4)): tripod(p, x, z, h); cymbal(p, x, y + h, z, 0.24)
    p.cyl('dark', 0.18, y + 0.5, y + 0.58, 0.0, -0.55, 20); seg_cyl(p, 'chrome', (0.0, y, -0.55), (0.0, y + 0.5, -0.55), 0.02, 8)
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.3; seg_cyl(p, 'chrome', (0.0, y + 0.2, -0.55), (0.25 * math.cos(a), y, -0.55 + 0.25 * math.sin(a)), 0.012, 6)
    for x in (-0.3, 0.3): p.box('dark', x - 0.05, x + 0.05, y, y + 0.03, 0.0, 0.25)
    return p
def piano():
    """Piano de armario com teclado de 52 teclas brancas e pretas, tampa, castical e banqueta (pivo: centro de tras, piso; teclas para +Z)."""
    p = Piece(); w = 1.48
    p.cham('piano', -w / 2, w / 2, 0.06, 1.28, 0.0, 0.34, 0.012); p.cham('piano', -w / 2 - 0.01, w / 2 + 0.01, 1.28, 1.32, -0.01, 0.36, 0.008)
    for s in (-1, 1): p.cham('piano', s * w / 2 - 0.05, s * w / 2 + 0.05 * 0 + (0.0 if s > 0 else 0.05) - (0.05 if s > 0 else 0.0) + (0.05 if s > 0 else 0.0), 0.0, 0.82, 0.34, 0.6, 0.008) if False else None
    for s in (-1, 1):
        a, b = sorted((s * w / 2, s * (w / 2 - 0.05))); p.cham('piano', a, b, 0.06, 0.8, 0.34, 0.6, 0.008)
        seg_cyl(p, 'piano', (s * (w / 2 - 0.025), 0.06, 0.56), (s * (w / 2 - 0.025), 0.0, 0.56), 0.02, 8)
    p.box('piano', -w / 2 + 0.05, w / 2 - 0.05, 0.62, 0.7, 0.34, 0.6)
    n = 52; kw = (w - 0.14) / n
    for i in range(n):
        x0 = -w / 2 + 0.07 + i * kw; p.box('keys', x0 + 0.001, x0 + kw - 0.001, 0.7, 0.725, 0.42, 0.58)
    for i in range(n - 1):
        if i % 7 in (2, 6): continue
        x = -w / 2 + 0.07 + (i + 1) * kw; p.box('dark', x - kw * 0.3, x + kw * 0.3, 0.725, 0.745, 0.42, 0.52)
    p.box('piano', -w / 2 + 0.05, w / 2 - 0.05, 0.725, 0.84, 0.34, 0.4); p.cham('piano', -w / 2 + 0.05, w / 2 - 0.05, 0.84, 0.86, 0.34, 0.46, 0.005)
    p.cham('piano', -0.4, 0.4, 0.92, 1.12, 0.36, 0.38, 0.004)
    for x in (-0.15, 0.15): p.box('brass', x - 0.05, x - 0.01, 0.12, 0.14, 0.34, 0.38)
    p.cham('piano', -0.42, 0.42, 0.44, 0.5, 0.75, 1.1, 0.01)
    for (x, z) in ((-0.38, 0.79), (0.38, 0.79), (-0.38, 1.06), (0.38, 1.06)): p.box('piano', x - 0.025, x + 0.025, 0.0, 0.44, z - 0.025, z + 0.025)
    return p
def folding_chair():
    """Cadeira dobravel de aco com assento e encosto pintados (pivo: centro, chao; encosto em -Z)."""
    p = Piece()
    for s in (-1, 1):
        seg_cyl(p, 'steel_d', (s * 0.2, 0.0, 0.22), (s * 0.2, 0.88, -0.2), 0.011, 6); seg_cyl(p, 'steel_d', (s * 0.2, 0.0, -0.22), (s * 0.2, 0.46, 0.12), 0.011, 6)
    p.cham('steel_d', -0.21, 0.21, 0.44, 0.47, -0.18, 0.2, 0.01); p.cham('steel_d', -0.19, 0.19, 0.68, 0.86, -0.21, -0.18, 0.008)
    seg_cyl(p, 'steel_d', (-0.2, 0.1, 0.18), (0.2, 0.1, 0.18), 0.008, 6); return p
def music_stand():
    """Estante de partitura: tripe, haste e bandeja inclinada com folha em branco (pivo: centro, chao; frente para +Z)."""
    p = Piece(); tripod(p, 0.0, 0.0, 1.05, 0.26, 'dark')
    c = np.array([0.0, 1.15, 0.0]); n = unit((0.0, 0.5, 1.0)); u = np.array([1.0, 0, 0]); v = np.cross(n, u)
    pts = [c + a * u + b * v + d * n for a in (-0.25, 0.25) for b in (-0.17, 0.17) for d in (0.0, 0.006)]; p.hull('dark', pts)
    p.hull('dark', [c + a * u + w_ * v + b * n for a in (-0.25, 0.25) for b in (0.0, 0.05) for w_ in (-0.17, -0.155)])
    p.hull('paper', [c + a * u + b * v + d * n for a in (-0.2, 0.2) for b in (-0.14, 0.15) for d in (0.006, 0.009)])
    return p
def speaker():
    """Caixa de som de palco: gabinete com cantos de metal, alto-falante grande, corneta e alcas (pivo: centro de tras, piso; frente +Z)."""
    p = Piece(); p.cham('dark', -0.32, 0.32, 0.0, 1.05, 0.0, 0.5, 0.02)
    for (x, y) in ((-0.3, 0.025), (0.3, 0.025), (-0.3, 1.025), (0.3, 1.025)): p.box('steel', x - 0.03, x + 0.03, y - 0.02, y + 0.02, 0.47, 0.505)
    disc_z(p, 'steel_d', 0.24, 0.5, 0.505, 0.0, 0.38, 28); disc_z(p, 'rubber', 0.2, 0.505, 0.512, 0.0, 0.38, 28); disc_z(p, 'dark', 0.06, 0.512, 0.53, 0.0, 0.38, 16)
    p.box('steel_d', -0.2, 0.2, 0.76, 0.96, 0.5, 0.505); p.hull('rubber', [(x, y, 0.51) for x in (-0.16, 0.16) for y in (0.8, 0.92)] + [(x, y, 0.47) for x in (-0.04, 0.04) for y in (0.84, 0.88)])
    for s in (-1, 1): a, b = sorted((s * 0.32, s * 0.335)); p.box('steel', a, b, 0.7, 0.74, 0.18, 0.32)
    return p
def mic_stand():
    """Pedestal de microfone com base redonda, haste, girafa e microfone com cabo (pivo: base, chao; microfone para +Z)."""
    p = Piece(); p.cyl('dark', 0.15, 0.0, 0.025, 0, 0, 20); seg_cyl(p, 'chrome', (0, 0.02, 0), (0, 1.3, 0), 0.012, 8)
    seg_cyl(p, 'dark', (0, 1.3, 0), (0, 1.45, 0.35), 0.009, 6); p.sphere('dark', 0.022, 0, 1.3, 0, 1)
    seg_cyl(p, 'dark', (0, 1.45, 0.35), (0, 1.43, 0.48), 0.02, 10); p.sphere('steel', 0.03, 0, 1.425, 0.5, 1)
    seg_cyl(p, 'rubber', (0, 1.42, 0.38), (0, 0.6, 0.05), 0.006, 4); seg_cyl(p, 'rubber', (0, 0.6, 0.05), (0.3, 0.004, 0.3), 0.006, 4)
    return p

# ============================================================================ camarins
def makeup_counter(L1=2.4):
    """Bancada de camarim com espelho emoldurado por lampadas, gavetas e potes (pivo: face da parede, piso)."""
    p = Piece(); x = L1 / 2
    p.cham('wood', -x, x, 0.74, 0.78, 0.0, 0.52, 0.008)
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x - 0.45))); p.cham('dkwood', a + 0.01, b - 0.01, 0.0, 0.74, 0.02, 0.48, 0.008)
        for k in range(3): y = 0.06 + k * 0.22; p.box('wood', a + 0.03, b - 0.03, y, y + 0.2, 0.48, 0.495); p.box('brass', (a + b) / 2 - 0.05, (a + b) / 2 + 0.05, y + 0.12, y + 0.14, 0.495, 0.51)
    p.cham('dkwood', -x + 0.02, x - 0.02, 0.95, 1.9, 0.0, 0.03, 0.006); p.box('mirror', -x + 0.08, x - 0.08, 1.01, 1.84, 0.03, 0.034)
    for k in range(int(L1 / 0.24) + 1):
        xx = -x + 0.05 + k * (L1 - 0.1) / int(L1 / 0.24); p.sphere('lamp_glass', 0.035, xx, 1.87, 0.05, 1)
    for k in range(4):
        yy = 1.05 + k * 0.25; p.sphere('lamp_glass', 0.035, -x + 0.05, yy, 0.05, 1); p.sphere('lamp_glass', 0.035, x - 0.05, yy, 0.05, 1)
    for (xx, zz, r, h, m) in ((-0.6, 0.3, 0.04, 0.12, 'porcelain'), (-0.48, 0.32, 0.03, 0.08, 'flag_r'), (0.3, 0.28, 0.035, 0.1, 'brass'), (0.5, 0.35, 0.05, 0.05, 'paper')):
        p.cyl(m, r, 0.78, 0.78 + h, xx, zz, 12)
    return p
def clothes_rack():
    """Arara de figurino com rodizios, cabides e roupas de varias cores (pivo: centro, chao; ao longo de X)."""
    p = Piece(); x = 0.75
    for s in (-1, 1):
        seg_cyl(p, 'chrome', (s * x, 0.08, 0.0), (s * x, 1.7, 0.0), 0.016, 8); seg_cyl(p, 'chrome', (s * x, 0.08, -0.25), (s * x, 0.08, 0.25), 0.016, 8)
        for z in (-0.25, 0.25): p.sphere('rubber', 0.04, s * x, 0.04, z, 1)
    seg_cyl(p, 'chrome', (-x, 1.7, 0.0), (x, 1.7, 0.0), 0.014, 8)
    cols = ['fabric', 'fabric2', 'flag_y', 'flag_g', 'paint_w', 'fabric', 'flag_b', 'vinyl']
    for i, xx in enumerate(np.linspace(-0.6, 0.6, 8)):
        seg_cyl(p, 'chrome', (xx, 1.7, 0.0), (xx, 1.62, 0.0), 0.004, 4)
        p.hull('dark', [(xx, 1.62, 0.0), (xx - 0.01, 1.58, -0.2), (xx - 0.01, 1.58, 0.2), (xx + 0.01, 1.58, -0.2), (xx + 0.01, 1.58, 0.2)])
        lo = 0.75 if i % 3 == 0 else 1.0
        p.hull(cols[i], [(xx + d, y, z) for d in (-0.035, 0.035) for (y, z) in ((1.58, -0.2), (1.58, 0.2), (lo, -0.24 - (0.04 if lo < 0.8 else 0.0)), (lo, 0.24 + (0.04 if lo < 0.8 else 0.0)))])
    return p
def wardrobe_trunk():
    """Bau de turne com cantoneiras, fechos e alca (pivo: centro, chao)."""
    p = Piece(); p.cham('vinyl', -0.45, 0.45, 0.0, 0.55, -0.28, 0.28, 0.01)
    for (x, z) in ((-0.45, -0.28), (0.45, -0.28), (-0.45, 0.28), (0.45, 0.28)):
        for y in (0.0, 0.55): p.box('brass', x - 0.04, x + 0.04, y - 0.04 + (0.04 if y == 0 else 0), y + (0.04 if y == 0 else 0.0) - (0 if y == 0 else 0.0), z - 0.04, z + 0.04) if False else None
    p.box('dark', -0.46, 0.46, 0.4, 0.43, -0.29, 0.29)
    for x in (-0.25, 0.25): p.box('brass', x - 0.03, x + 0.03, 0.38, 0.46, 0.285, 0.3)
    seg_cyl(p, 'dark', (-0.1, 0.56, 0.0), (0.1, 0.56, 0.0), 0.012, 6); return p

# ============================================================================ quiosque por dentro
def counter_k(L1=5.5):
    """Balcao de atendimento (pivo: face da parede, piso; balcao para +Z): corpo de madeira, tampo, prateleira e copos."""
    p = Piece(); x = L1 / 2
    p.cham('dkwood', -x, x, 0.0, 0.88, 0.0, 0.55, 0.01); p.cham('wood', -x - 0.02, x + 0.02, 0.88, 0.92, 0.0, 0.6, 0.006)
    p.box('dark', -x + 0.04, x - 0.04, 0.0, 0.1, 0.55, 0.56)
    for xx in np.arange(-x + 0.6, x - 0.3, 0.9): p.box('wood', xx - 0.01, xx + 0.01, 0.12, 0.84, 0.55, 0.565)
    return p
def popcorn_machine():
    """Maquina de pipoca: carrinho de vidro com cupula vermelha, panela e pipoca (pivo: centro, base)."""
    p = Piece(); p.cham('flag_r', -0.3, 0.3, 0.0, 0.18, -0.22, 0.22, 0.01)
    for (x, z) in ((-0.28, -0.2), (0.28, -0.2), (-0.28, 0.2), (0.28, 0.2)): p.box('flag_r', x - 0.02, x + 0.02, 0.18, 0.72, z - 0.02, z + 0.02)
    p.box('glass', -0.26, 0.26, 0.18, 0.7, 0.198, 0.202); p.box('glass', -0.26, 0.26, 0.18, 0.7, -0.202, -0.198)
    for s in (-1, 1): a, b = sorted((s * 0.26, s * 0.262)); p.box('glass', a, b, 0.18, 0.7, -0.18, 0.18)
    p.cham('flag_r', -0.31, 0.31, 0.72, 0.8, -0.23, 0.23, 0.01); p.hull('flag_r', [(x, 0.8, z) for x in (-0.3, 0.3) for z in (-0.22, 0.22)] + [(0, 0.95, 0)])
    p.cyl('chrome', 0.1, 0.55, 0.62, 0, 0, 16); seg_cyl(p, 'chrome', (0, 0.62, 0), (0, 0.72, 0), 0.01, 6)
    rng = np.random.default_rng(7)
    p.box('food_y', -0.25, 0.25, 0.18, 0.3, -0.18, 0.18)
    for _ in range(40): p.sphere('paper', 0.02, rng.uniform(-0.23, 0.23), 0.3 + rng.uniform(0, 0.02), rng.uniform(-0.16, 0.16), 0)
    return p
def soda_fountain():
    """Refresqueira de 3 bicos com bandeja e pilha de copos (pivo: centro de tras, base; frente +Z)."""
    p = Piece(); p.cham('metal', -0.3, 0.3, 0.0, 0.62, 0.0, 0.42, 0.01)
    for (x, m) in ((-0.18, 'flag_r'), (0.0, 'food_y'), (0.18, 'food_g')):
        p.box(m, x - 0.07, x + 0.07, 0.38, 0.56, 0.42, 0.425); seg_cyl(p, 'chrome', (x, 0.36, 0.42), (x, 0.32, 0.47), 0.012, 6)
    p.box('steel', -0.28, 0.28, 0.0, 0.03, 0.42, 0.58)
    lathe(p, 'paper', [(0.035, 0.0), (0.045, 0.3), (0.0, 0.3)], 0.42, 0.25, 0.0, 12)
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

# ============================================================================ gramado e passeios
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
LP_H = 3.8; LP_TOP = 3.15
LAMPS = [(-22.2, 20.2), (-8.0, 20.2), (8.0, 20.2), (22.2, 20.2), (-22.2, 5.0), (-12.5, 5.5), (12.5, 5.5), (22.2, 5.0)]
RUNS = [(0, 1), (1, 2), (2, 3), (0, 4), (3, 7), (4, 5), (6, 7), (5, 1), (6, 2)]
def string_lights():
    """Varal de luzes: fio com barriga entre os postes e lampadas penduradas a cada 60 cm (pivo: origem)."""
    p = Piece()
    for (ia, ib) in RUNS:
        a = np.array([LAMPS[ia][0], LP_TOP, LAMPS[ia][1]]); b = np.array([LAMPS[ib][0], LP_TOP, LAMPS[ib][1]])
        L1 = np.linalg.norm((b - a)[[0, 2]]); sag = 0.05 * L1
        f = lambda t: a + (b - a) * t - np.array([0, 4 * sag * t * (1 - t), 0])
        ts = np.linspace(0, 1, 21)
        for k in range(20): seg_cyl(p, 'dark', f(ts[k]), f(ts[k + 1]), 0.006, 4)
        n = int(L1 / 0.6)
        for i in range(1, n):
            c = f(i / n); seg_cyl(p, 'dark', c, c - np.array([0, 0.07, 0]), 0.005, 4); p.sphere('lamp_glass', 0.035, c[0], c[1] - 0.1, c[2], 1)
    for (x, z) in LAMPS: seg_cyl(p, 'iron', (x, LP_TOP + 0.06, z), (x, LP_TOP - 0.06, z), 0.065, 10)
    return p
def blanket(c1='flag_r', c2='paint_w', w=1.6, d=1.4, seed=1):
    """Canga xadrez de piquenique com cesta de vime, pratos, frutas, garrafa e guardanapos (pivo: centro, chao)."""
    p = Piece(); rng = np.random.default_rng(seed); n = 8
    for i in range(n):
        for j in range(n):
            x0 = -w / 2 + i * w / n; z0 = -d / 2 + j * d / n
            p.box(c1 if (i + j) % 2 == 0 else c2, x0, x0 + w / n, 0.0, 0.008 + (0.001 if (i + j) % 2 else 0.0), z0, z0 + d / n)
    x, z = 0.35, -0.3
    p.cham('basket', x - 0.22, x + 0.22, 0.008, 0.26, z - 0.15, z + 0.15, 0.02)
    for k in range(5): yy = 0.04 + k * 0.045; p.box('dkwood', x - 0.222, x + 0.222, yy, yy + 0.01, z - 0.152, z + 0.152)
    for k in range(9): xx = x - 0.2 + k * 0.05; seg_cyl(p, 'basket', (xx, 0.26, z), (xx, 0.26, z), 0.0, 4) if False else None
    for s in (-1, 1): seg_cyl(p, 'dkwood', (x + s * 0.18, 0.26, z), (x + s * 0.1, 0.42, z), 0.01, 6)
    seg_cyl(p, 'dkwood', (x - 0.1, 0.42, z), (x + 0.1, 0.42, z), 0.01, 6)
    p.cham('basket', x - 0.23, x + 0.23, 0.26, 0.28, z - 0.16, z + 0.02, 0.008)
    for (px, pz) in ((-0.4, 0.25), (0.0, 0.35), (-0.3, -0.2)):
        lathe(p, 'porcelain', [(0.06, 0.009), (0.11, 0.022), (0.12, 0.026), (0.0, 0.026) if False else (0.11, 0.026)], px, pz, 0.0, 18); p.cyl('porcelain', 0.06, 0.009, 0.014, px, pz, 18)
        p.sphere(['food_r', 'food_g', 'food_y'][int(rng.integers(3))], 0.035, px + 0.03, 0.05, pz, 1)
    for (fx, fz, m) in ((-0.05, -0.05, 'food_r'), (0.02, -0.08, 'food_r'), (0.0, 0.0, 'food_g')): p.sphere(m, 0.04, fx, 0.048, fz, 1)
    lathe(p, 'food_g', [(0.04, 0.009), (0.04, 0.2), (0.015, 0.26), (0.015, 0.3), (0.0, 0.3)], 0.15, 0.25, 0.0, 12)
    p.box('paper', -0.6, -0.42, 0.009, 0.014, -0.5, -0.35)
    return p
def ice_cream_cart():
    """Carrinho de sorvete: caixa termica de chapa com 2 tampas, faixa, rodas de raios, alca, pes e guarda-sol listrado (pivo: centro, chao)."""
    p = Piece(); p.cham('cart_w', -0.6, 0.6, 0.35, 1.05, -0.35, 0.35, 0.03)
    p.box('flag_b', -0.602, 0.602, 0.75, 0.83, -0.352, 0.352)
    for s in (-1, 1): p.cham('chrome', *sorted((0.0, s * 0.56)), 1.05, 1.08, -0.31, 0.31, 0.01); p.box('chrome', s * 0.3 - 0.04, s * 0.3 + 0.04, 1.08, 1.1, -0.02, 0.02)
    for s in (-1, 1):
        z = s * 0.4
        disc_z(p, 'rubber', 0.3, *sorted((z, z + s * 0.04)), 0.35, 0.3, 28) if False else None
        m = trimesh.creation.annulus(r_min=0.26, r_max=0.3, height=0.04, sections=28); m.apply_translation([0.25, 0.3, z]); p.add('rubber', m)
        for k in range(8):
            a = k * math.pi / 4; seg_cyl(p, 'chrome', (0.25, 0.3, z), (0.25 + 0.26 * math.cos(a), 0.3 + 0.26 * math.sin(a), z), 0.008, 4)
        disc_z(p, 'chrome', 0.04, z - 0.03, z + 0.03, 0.25, 0.3, 12)
    seg_cyl(p, 'chrome', (0.25, 0.3, -0.42), (0.25, 0.3, 0.42), 0.015, 8)
    for z in (-0.25, 0.25): seg_cyl(p, 'chrome', (-0.5, 0.35, z), (-0.5, 0.0, z), 0.018, 6); p.sphere('rubber', 0.03, -0.5, 0.02, z, 1)
    for z in (-0.25, 0.25): seg_cyl(p, 'chrome', (-0.6, 0.95, z), (-0.95, 1.0, z), 0.016, 6)
    seg_cyl(p, 'rubber', (-0.95, 1.0, -0.27), (-0.95, 1.0, 0.27), 0.022, 8)
    seg_cyl(p, 'chrome', (0.0, 1.08, 0.0), (0.0, 2.3, 0.0), 0.018, 8)
    n = 12; R = 1.0; y0, y1 = 2.0, 2.35
    for k in range(n):
        a0, a1 = k * 2 * math.pi / n, (k + 1) * 2 * math.pi / n
        p.hull('umbrella' if k % 2 == 0 else 'paint_w', [(R * math.cos(a), y0, R * math.sin(a)) for a in (a0, a1)] + [(R * math.cos(a), y0 + 0.012, R * math.sin(a)) for a in (a0, a1)] + [(0, y1, 0), (0, y1 + 0.012, 0)])
    p.sphere('chrome', 0.03, 0, y1 + 0.03, 0, 1)
    return p
def drinking_fountain():
    """Bebedouro de pedestal: coluna de concreto, cuba de inox com bico e botao, degrau para criancas (pivo: centro, chao)."""
    p = Piece(); lathe(p, 'concrete', [(0.25, 0.0), (0.25, 0.08), (0.14, 0.12), (0.12, 0.75), (0.18, 0.82), (0.2, 0.86)], sec=20)
    lathe(p, 'steel', [(0.2, 0.86), (0.22, 0.92), (0.19, 0.93), (0.06, 0.88), (0.0, 0.88)], sec=24)
    seg_cyl(p, 'chrome', (0.0, 0.88, -0.1), (0.0, 0.97, -0.08), 0.012, 6); p.box('chrome', -0.03, 0.03, 0.8, 0.86, 0.17, 0.2)
    p.cham('concrete', -0.25, 0.25, 0.0, 0.18, 0.25, 0.5, 0.01); return p
def hedge(L1=2.0, h=1.0, d=0.7, seed=1):
    """Cerca viva aparada (pivo: centro, chao; ao longo de X): bloco de folhagem com ondulacoes."""
    p = Piece(); rng = np.random.default_rng(seed)
    p.cham('leaf', -L1 / 2, L1 / 2, 0.0, h, -d / 2, d / 2, 0.08)
    for k in range(5):
        x = -L1 / 2 + 0.2 + k * (L1 - 0.4) / 4; p.sphere('leaf2', 0.28, x + rng.uniform(-0.1, 0.1), h - 0.12, rng.uniform(-0.12, 0.12), 1)
    return p
def lawn_sign():
    """Placa de grama com pictograma de nota musical (pivo: centro, chao)."""
    p = Piece(); seg_cyl(p, 'iron', (-0.25, 0.0, 0), (-0.25, 0.9, 0), 0.02, 6); seg_cyl(p, 'iron', (0.25, 0.0, 0), (0.25, 0.9, 0), 0.02, 6)
    p.cham('bench_g', -0.32, 0.32, 0.55, 1.0, -0.02, 0.02, 0.008)
    for s in (-1, 1):
        z0, z1 = sorted((s * 0.02, s * 0.026))
        ext(p, 'paint_w', unary_union([Point(-0.06, 0.66).buffer(0.05, 16), sbox(-0.02, 0.66, 0.0, 0.92), Point(0.1, 0.7).buffer(0.05, 16), sbox(0.14, 0.7, 0.16, 0.92), sbox(-0.02, 0.88, 0.16, 0.92)]), z0, z1)
    return p

# ============================================================================ terreno (pivo: origem)
PARK = sbox(PX0, PZ0, PX1, PZ1); INNER = off(PARK, -2.5); SITE = sbox(SX0, SZ0, SX1, SZ1)
BLD = unary_union([STAGE, BB, KB])
PAVE = unary_union([PARK.difference(INNER), off(STAGE, 1.5), off(BB, 1.2), off(KB, 1.2),
                    sbox(STX + 1.5, -2.6, PX1 - 2.5, -0.8), sbox(PX0 + 2.5, -2.6, -STX - 1.5, -0.8),
                    sbox(BX1, -9.7, PX1 - 2.5, -8.3), sbox(15.2, PZ0 + 2.5, 16.8, KZ0)]).difference(BLD).buffer(0)
GRAVEL = unary_union([sbox(-1.6, 5.0, 1.6, PZ1 - 2.5), sbox(12.5, -11.8, 19.5, -9.7)]).difference(PAVE).difference(BLD).buffer(0)
LAWN = INNER.difference(PAVE).difference(GRAVEL).difference(BLD).buffer(0)
def site():
    """Terreno: calcada de placas em volta do parque, do palco, dos bastidores e do quiosque, caminhos laterais, corredor de cascalho
    no meio do gramado, gramado e faixa de grama de fora."""
    p = Piece()
    p.merge(paving(PAVE, Y0, 1.5, 'paver'))
    curb = unary_union([poly.difference(off(poly, -0.08)) for poly in getattr(GRAVEL, 'geoms', [GRAVEL])]).difference(off(PAVE, 0.001)).buffer(0)
    ext_y(p, 'gravel', GRAVEL.difference(curb).buffer(0), GY, 0.1); ext_y(p, 'concrete', curb, GY, 0.14)
    ext_y(p, 'grass', LAWN, GY, 0.05)
    ext_y(p, 'grass2', SITE.difference(PARK), GY, 0.05)
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
def wm(fn, kind, tl=0.0, tr_=0.0):
    n = f"{'b' if fn is bs_mod else 'q'}_{kind}" + ('_l' if tl else '') + ('_r' if tr_ else '')
    if n not in pieces: pieces[n] = fn(kind, tl, tr_)
    return n
pieces.update({
    'stage': stage(), 'shell': shell(), 'bs_roof': bs_roof(), 'bs_floor': bs_floor(), 'bs_plan': bs_plan(), 'bs_stairs': bs_stairs(),
    'ki_roof': ki_roof(), 'ki_floor': ki_floor(), 'ki_plan': ki_plan(),
    'drum_kit': drum_kit(), 'piano': piano(), 'folding_chair': folding_chair(), 'music_stand': music_stand(), 'speaker': speaker(), 'mic_stand': mic_stand(),
    'makeup_counter': makeup_counter(2.4), 'clothes_rack': clothes_rack(), 'trunk': wardrobe_trunk(), 'sofa': sofa(2), 'guest_chair': guest_chair('fabric'),
    'wc': wc(), 'sink_one': sink_bank(1, 0.8),
    'counter_k': counter_k(5.5), 'popcorn': popcorn_machine(), 'soda': soda_fountain(), 'register': register(), 'fridge': fridge(), 'shelves': shelves(1.6),
    'bench': park_bench(), 'lamp_post': lamp_post(LP_H), 'string_lights': string_lights(), 'blanket_r': blanket('flag_r', 'paint_w', seed=1),
    'blanket_b': blanket('flag_b', 'paper', seed=2), 'ice_cream_cart': ice_cream_cart(), 'fountain': drinking_fountain(), 'hedge': hedge(),
    'lawn_sign': lawn_sign(), 'trash_can': trash_can(), 'tree': tree(6.2, 2.0), 'tree_b': tree(5.2, 1.6, 'leaf2', 4), 'bush': bush(), 'site': site(),
    'door_back': door_back(0.94, 2.26), 'door_int': door_interior(0.86, 2.08), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
B = ['bastidores']; Q = ['quiosque']; ys = SH; yq = Y0
put('stage', 0, 0, 0, 0, ['palco']); put('shell', 0, 0, 0, 0, ['palco', 'concha', 'front'])
for x in range(-6, 7, 2): put(wm(bs_mod, 'door_s' if x == 0 else 'plain'), x, ys, BZ1, 0, B + ['ext', 'front'])
for x in range(-6, 7, 2): put(wm(bs_mod, 'win' if x in (-6, 0, 6) else 'plain'), x, ys, BZ0, 180, B + ['ext'])
for z, k in ((-13, 'plain'), (-11, 'win'), (-9, 'plain')): put(wm(bs_mod, k, T if z == -13 else 0.0, T if z == -9 else 0.0), BX0, ys, z, -90, B + ['ext'])
for z, k in ((-13, 'plain'), (-11, 'win'), (-9, 'door')): put(wm(bs_mod, k, T if z == -9 else 0.0, T if z == -13 else 0.0), BX1, ys, z, 90, B + ['ext'])
put('bs_roof', 0, ys, 0, 0, B + ['roof']); put('bs_floor', 0, ys, 0, 0, B); put('bs_plan', 0, ys, 0, 0, B); put('bs_stairs', 0, 0, 0, 0, B)
hx, hz = hinge(0.0, BZ1, 0, -0.47, -0.125); put('door_back', hx, ys + 0.005, hz, 0, B, door=-90)   # abre para o palco
hx, hz = hinge(BX1, -9.0, 90, -0.47, -0.125); put('door_back', hx, ys + 0.005, hz, 90, B, door=90)
for c in (-3.9, 0.0, 3.9): put('door_int', c - 0.43, ys + 0.005, BZP, 0, B, door=90)
for s in (-1, 1):
    put('makeup_counter', s * 3.9, ys, BZ0 + T, 0, B)
    for x in (3.2, 4.6): put('guest_chair', s * x, ys, -12.7, 180, B)
    put('clothes_rack', s * 5.9, ys, -11.5, 90, B); put('sofa', s * (1.0 + t_ / 2), ys, -11.2, 90 * s, B); put('trunk', s * 6.0, ys, -10.3, 0, B)
put('wc', 0.0, ys, BZ0 + T, 0, B); put('sink_one', -1.0 + t_ / 2, ys, -11.6, 90, B)
# quiosque
for x, k in ((14, 'svc'), (16, 'svc'), (18, 'sign')): put(wm(ki_mod, k), x, yq, KZ1, 0, Q + ['ext'])
for x, k in ((14, 'plain'), (16, 'door'), (18, 'plain')): put(wm(ki_mod, k), x, yq, KZ0, 180, Q + ['ext'])
for z in (-16, -14): put(wm(ki_mod, 'plain', T if z == -16 else 0.0, T if z == -14 else 0.0), KX0, yq, z, -90, Q + ['ext'])
for z in (-16, -14): put(wm(ki_mod, 'plain', T if z == -14 else 0.0, T if z == -16 else 0.0), KX1, yq, z, 90, Q + ['ext'])
put('ki_roof', 0, yq, 0, 0, Q + ['roof']); put('ki_floor', 0, yq, 0, 0, Q); put('ki_plan', 0, yq, 0, 0, Q)
hx, hz = hinge(16.0, KZ0, 180, -0.47, -0.125); put('door_back', hx, yq + 0.005, hz, 180, Q, door=90)
put('counter_k', 16.0, yq, KZ1 - T, 180, Q); put('popcorn', 18.1, yq + 0.92, -13.6, 180, Q); put('soda', 17.2, yq + 0.92, -13.3, 180, Q)
put('register', 15.0, yq + 0.92, -13.55, 180, Q); put('fridge', 13.75, yq, KZ0 + T, 0, Q); put('shelves', 18.0, yq, KZ0 + T, 0, Q)
put('sink_one', KX1 - T, yq, -15.0, -90, Q)
# banda no palco
P = ['palco']
put('drum_kit', -3.5, SH, -5.0, 0, P); put('piano', 3.8, SH, -6.6, 0, P)
for (x, z, r) in ((-5.6, -2.0, 18), (-4.3, -1.2, 10), (4.3, -1.2, -10), (5.6, -2.0, -18), (2.4, -3.6, -12)):
    put('folding_chair', x, SH, z, r, P); put('music_stand', x + 0.75 * math.sin(math.radians(r)), SH, z + 0.75 * math.cos(math.radians(r)), r + 180, P)
for s in (-1, 1): put('speaker', s * 7.4, SH, 2.5, -12 * s, P); put('mic_stand', s * 1.8, SH, 2.3, -20 * s, P)
# gramado
st = ['parque']; yl = 0.05
put('site', 0, 0, 0, 0, st); put('string_lights', 0, 0, 0, 0, st + ['roof'])
for r in (10.5, 14.0, 17.5):
    a0 = math.degrees(math.asin(2.8 / r)); da = math.degrees(2.6 / r); a = a0
    while a <= 55.0:
        for s in (-1, 1):
            x, z = r * math.sin(math.radians(s * a)), r * math.cos(math.radians(a)); put('bench', x, yl, z, math.degrees(math.atan2(-x, -z)), st)
        a += da
for (x, z) in LAMPS: put('lamp_post', x, yl, z, 0, st + ['roof'])
for (x, z, n, r) in ((-12.0, 19.0, 'blanket_r', 12), (10.5, 18.8, 'blanket_b', -20), (-19.0, 8.0, 'blanket_b', 35), (19.0, 9.0, 'blanket_r', -8)): put(n, x, yl, z, r, st)
put('ice_cream_cart', 15.5, yl, 12.6, 30, st); put('fountain', 2.6, yl, 19.9, 0, st); put('lawn_sign', -3.0, yl, 19.9, 8, st)
for (x, z) in ((-2.3, 7.9), (2.3, 7.9), (-2.3, 15.6), (2.3, 15.6), (13.0, -10.6), (21.0, -10.3), (-13.4, -3.4)):
    put('trash_can', x, Y0 if PAVE.contains(Point(x, z)) else (0.1 if GRAVEL.contains(Point(x, z)) else yl), z, 0, st)
hz_ = PZ1 - 2.5 - 0.35
for s in (-1, 1):
    for k in range(10): put('hedge', s * (PX1 - 3.5 - 2 * k), yl, hz_, 0, st)
def side_runs(gaps):
    out = []; z = PZ1 - 2.5 - 0.7 - 1.0
    while z - 1.0 > PZ0 + 2.5 + 0.7:
        if not any(a - 0.1 < z + 1.0 and z - 1.0 < b + 0.1 for (a, b) in gaps): out.append(z)
        z -= 2.0
    return out
for z in side_runs([(-2.6, -0.8)]): put('hedge', PX0 + 2.5 + 0.35, yl, z, 90, st)
for z in side_runs([(-2.6, -0.8), (-9.7, -8.3)]): put('hedge', PX1 - 2.5 - 0.35, yl, z, 90, st)
for k in range(23):
    x = PX0 + 2.5 + 0.7 + 1.0 + 2 * k
    if x + 1.0 > PX1 - 2.5 - 0.7: break
    if x + 1.1 > 15.2 and x - 1.1 < 16.8: continue
    put('hedge', x, yl, PZ0 + 2.5 + 0.35, 0, st)
for k, (x, z) in enumerate(((-20.0, -6.0), (20.0, -5.0), (-20.0, 14.0), (20.0, 14.5), (-17.0, -15.0), (-10.0, -16.5), (9.0, -16.0), (-3.5, -17.0),
                            (3.5, -17.2), (21.6, -15.0), (-21.5, -12.0))):
    put('tree' if k % 2 == 0 else 'tree_b', x, yl, z, 0, st + ['roof'])
for (x, z) in ((-9.2, -12.0), (9.4, -12.4), (-13.4, -6.0), (13.4, -6.2), (-13.4, 1.6), (13.4, 1.8), (-9.0, -15.4)): put('bush', x, yl, z, 0, st)
put('player_scale_ref', 1.0, Y0, 6.2, 0, st); put('player_scale_ref', -1.2, SH, 1.0, 0, P)


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'walk_level': Y0, 'lawn_level': 0.05,
                       'stage': {'x': [-STX, STX], 'z': [STZ0, STZ1], 'top': SH, 'front_corner_radius': STR},
                       'shell': {'rings': [{'a': a, 'b': b, 'z_front': zf, 'z_back': zb} for (a, b, zf, zb) in RINGS], 'thickness': SHT},
                       'backstage': {'x': [BX0, BX1], 'z': [BZ0, BZ1], 'floor': SH, 'ceiling': SH + BCEIL, 'parapet_top': SH + BH, 'corridor_wall_z': BZP},
                       'kiosk': {'x': [KX0, KX1], 'z': [KZ0, KZ1], 'floor': Y0, 'wall_top': Y0 + KH},
                       'park': {'x': [PX0, PX1], 'z': [PZ0, PZ1], 'sidewalk_width': 2.5}, 'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
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
