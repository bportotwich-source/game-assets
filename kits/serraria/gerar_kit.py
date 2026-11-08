"""Kit 49: serraria, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Galpao da serra de 12 x 10 m (tabua e mata-junta pintada de cinza, telhado de chapa ondulada de 2 aguas com lanternim de janelas,
portao de correr de 4 m, porta de servico, janelas de 4 vidros) com a serra de fita, o carro porta-toras sobre trilhos, a mesa de
roletes, a refiladeira, a bancada, carrinhos de tabuas e montes de serragem. Ao lado, o queimador conico de chapa enferrujada (8,4 m
de base, 11,5 m de altura) com tela no topo, base de concreto e portinhola, ligado ao galpao por uma esteira inclinada em trelica.
Galpao aberto de 16 x 8 m em pilares de madeira com pilhas de tabuas tabicadas, pilhas de toras com o carregador amarelo, caminhao
de toras, escritorio de tabuas com fogao a lenha e chamine, pilhas de tabuas sobre paletes, patio de terra com cascalho, cerca de
madeira com porteira, poste de luz e pinheiros. Arte original e sem texto. Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
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
configurar(cores={'siding': (150, 156, 158), 'batten': (136, 142, 146), 'trim': (232, 230, 222), 'plaster': (214, 196, 160), 'ceil': (200, 182, 150),
                  'concrete': (186, 182, 174), 'conc_f': (170, 168, 162), 'wood': (196, 156, 104), 'lumber': (214, 182, 132), 'dkwood': (120, 86, 56),
                  'post': (132, 98, 66), 'roofm': (128, 134, 138), 'rust': (150, 76, 46), 'rust_d': (110, 56, 36), 'mesh': (70, 66, 62),
                  'metal': (170, 174, 178), 'frame': (60, 62, 66), 'chrome': (214, 218, 222), 'steel': (120, 126, 132), 'steel_d': (60, 64, 68),
                  'iron': (40, 42, 44), 'yellow': (230, 178, 40), 'truck_r': (176, 46, 40), 'rubber': (28, 28, 30), 'dark': (34, 34, 36),
                  'door': (150, 60, 44), 'door_int': (196, 170, 130), 'lamp_glass': (255, 238, 196), 'paper': (238, 234, 222), 'tool_r': (196, 52, 44),
                  'drum_b': (40, 84, 150), 'bark': (104, 78, 54), 'log_end': (206, 168, 112), 'sawdust': (214, 180, 120), 'dirt': (150, 122, 88),
                  'gravel': (168, 160, 146), 'grass': (110, 140, 74), 'leaf': (86, 124, 62), 'leaf2': (106, 140, 70), 'pine': (52, 92, 62),
                  'pine2': (64, 108, 70), 'fabric': (120, 60, 50), 'vinyl': (90, 70, 56), 'sash': (232, 230, 222), 'paint_w': (240, 240, 236),
                  'yellowp': (238, 196, 54), 'glass': (150, 186, 204), 'tank_g': (80, 110, 80)},
           texturas={'siding': 'planks', 'batten': 'planks', 'plaster': 'planks', 'concrete': 'render', 'conc_f': 'render', 'wood': 'planks',
                     'lumber': 'planks', 'dkwood': 'planks', 'post': 'planks', 'rust': 'render', 'rust_d': 'render', 'bark': 'render',
                     'dirt': 'render', 'gravel': 'render', 'grass': 'render', 'sawdust': 'render', 'ceil': 'planks'},
           out=OUT)
D.METAL.update({'metal', 'frame', 'chrome', 'steel', 'steel_d', 'iron', 'roofm', 'yellow', 'truck_r', 'mesh', 'tool_r'}); MATS = D.MATS; TEX = D.TEX
for k in ('rust', 'rust_d'): MATS[k].metallicFactor = 0.4; MATS[k].roughnessFactor = 0.8

# ============================================================================ medidas
W = 2.0; T = 0.22; t_ = 0.12
Y0 = 0.15                                   # pisos dos predios (patio de terra em 0)
GY = -0.2
MX0, MX1, MZ0, MZ1 = -12.0, 0.0, -14.0, -4.0   # galpao da serra
ME = 5.0; MPITCH = math.radians(25)            # beiral e inclinacao do telhado (cumeeira ao longo de X)
MOV = 0.5                                      # beiral
BUR_X, BUR_Z, BUR_R0, BUR_R1, BUR_H = 9.0, -9.0, 4.2, 1.4, 11.5   # queimador conico
SHX0, SHX1, SHZ0, SHZ1 = -14.0, 2.0, 2.0, 10.0  # galpao aberto
SHE = 4.0; SHR = 5.6                           # beiral e cumeeira do galpao aberto
OX0, OX1, OZ0, OZ1 = 12.0, 16.0, 6.0, 10.0     # escritorio
OE = 2.8
SX0, SX1, SZ0, SZ1 = -24.0, 24.0, -18.0, 18.0  # terreno (cerca a 0,5 m da borda)
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

# ============================================================================ moveis reaproveitados (kit 47)
def desk(w=1.5, d=0.75):
    """Mesa de escritorio (pivo: centro, chao): tampo de madeira com borda, pes de aco, painel frontal, gaveteiro, telefone,
    papeis e porta-lapis. O lado de quem atende fica em -Z."""
    p = Piece(); x = w / 2; z = d / 2
    p.cham('wood', -x, x, 0.72, 0.75, -z, z, 0.006)
    for s in (-1, 1):
        p.box('steel_d', s * (x - 0.04) - 0.02, s * (x - 0.04) + 0.02, 0.0, 0.72, -z + 0.03, z - 0.03)
    p.box('steel_d', -x + 0.06, x - 0.06, 0.3, 0.7, z - 0.04, z - 0.02)
    p.cham('steel', x - 0.5, x - 0.08, 0.02, 0.7, -z + 0.04, z - 0.08, 0.008)
    for k in range(3): y = 0.06 + k * 0.215; p.box('chrome', x - 0.34, x - 0.24, y + 0.15, y + 0.17, -z + 0.035, -z + 0.04)
    p.cham('dark', -x + 0.15, -x + 0.37, 0.75, 0.8, -0.1, 0.1, 0.01); p.box('dark', -x + 0.16, -x + 0.36, 0.8, 0.83, -0.08, 0.0)
    for k in range(3): p.box('paper', -0.2 + k * 0.01, 0.1 + k * 0.01, 0.75 + k * 0.003, 0.752 + k * 0.003, -0.15 + k * 0.02, 0.15 + k * 0.02)
    p.cyl('dark', 0.035, 0.75, 0.85, x - 0.25, 0.15, 10)
    return p
def workbench(L1=2.0):
    """Bancada de oficina (pivo: centro de tras, chao; para +Z): estrutura de aco, tampo de madeira, prateleira de baixo, morsa, painel
    perfurado com ferramentas, luminaria e tomadas."""
    p = Piece(); x = L1 / 2
    p.cham('wood', -x, x, 0.86, 0.92, 0.0, 0.72, 0.006)
    for (a, c) in ((-x + 0.05, 0.05), (x - 0.05, 0.05), (-x + 0.05, 0.67), (x - 0.05, 0.67)): p.box('steel_d', a - 0.025, a + 0.025, 0.0, 0.86, c - 0.025, c + 0.025)
    p.box('steel_d', -x + 0.03, x - 0.03, 0.2, 0.23, 0.05, 0.69)
    for k in range(3): p.cham('drum_b', -x + 0.1 + k * 0.4, -x + 0.45 + k * 0.4, 0.23, 0.5, 0.15, 0.55, 0.02)
    p.box('dkwood', -x, x, 1.0, 1.9, 0.0, 0.02)
    for i in range(24):
        for j in range(10): p.box('dark', -x + 0.05 + i * 0.08, -x + 0.06 + i * 0.08, 1.04 + j * 0.085, 1.05 + j * 0.085, 0.02, 0.021)
    for k in range(5):
        xx = -x + 0.25 + k * 0.18; p.box('steel', xx - 0.012, xx + 0.012, 1.25, 1.55 + k * 0.03, 0.03, 0.05)
        p.cyl('steel', 0.035, 1.55 + k * 0.03, 1.56 + k * 0.03, xx, 0.04, 10)
    p.box('dkwood', 0.2, 0.24, 1.2, 1.5, 0.03, 0.06); p.box('steel_d', 0.12, 0.32, 1.5, 1.58, 0.03, 0.08)
    for k in range(4): xx = 0.5 + k * 0.1; p.box('tool_r', xx - 0.015, xx + 0.015, 1.25, 1.45, 0.03, 0.06); p.box('steel', xx - 0.005, xx + 0.005, 1.45, 1.6, 0.04, 0.05)
    p.cham('steel_d', x - 0.42, x - 0.12, 0.92, 1.0, 0.45, 0.65, 0.01); p.box('steel_d', x - 0.34, x - 0.2, 1.0, 1.1, 0.48, 0.62)
    p.box('steel', x - 0.36, x - 0.18, 1.1, 1.13, 0.52, 0.58); seg_cyl(p, 'chrome', (x - 0.27, 1.04, 0.62), (x - 0.27, 1.04, 0.8), 0.01, 6)
    p.cham('metal', -x + 0.1, x - 0.1, 2.1, 2.18, 0.1, 0.3, 0.01); p.box('lamp_glass', -x + 0.14, x - 0.14, 2.095, 2.1, 0.14, 0.26)
    for xx in (-x + 0.2, x - 0.2): p.box('metal', xx - 0.01, xx + 0.01, 2.18, 2.4, 0.02, 0.2)
    return p
def drum(mat='drum_b'):
    p = Piece(); p.cyl(mat, 0.29, 0.0, 0.88, 0, 0, 24)
    for y in (0.02, 0.3, 0.58, 0.86): ring_y(p, mat, 0.29, 0.305, y, y + 0.025, 0, 0, 24)
    p.cyl('steel', 0.03, 0.88, 0.9, 0.15, 0.0, 10); return p
def fl_light():
    """Luminaria fluorescente pendente (pivo: ponto de fixacao no teto, eixo X): calha de chapa, 2 tubos e correntes."""
    p = Piece(); y0 = -0.9
    p.cham('metal', -0.62, 0.62, y0, y0 + 0.08, -0.12, 0.12, 0.01)
    for z in (-0.05, 0.05): disc_x(p, 'lamp_glass', 0.022, -0.58, 0.58, y0 - 0.005, z, 10)
    for x in (-0.45, 0.45): seg_cyl(p, 'steel', (x, y0 + 0.08, 0), (x, 0.0, 0), 0.006, 4)
    return p

# ============================================================================ paredes de tabua e mata-junta (pivo: face externa, cota do piso; dentro em -Z)
def w_core(p, holes, xa, xb, H, cas=()):
    """Parede de tabuas pintadas com mata-juntas a cada 40 cm, embasamento de concreto e faixa de pingadeira.
    holes = (x0, x1, y0, y1); cas = faixas (x0, x1, y0, y1) onde as mata-juntas param (guarnicoes)."""
    xs = sorted(set([xa, xb] + [v for h in holes for v in h[:2] if xa < v < xb]))
    ys = sorted(set([GY - Y0, 0.0, 0.3, H] + [v for h in holes for v in h[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0.3: return 'concrete'
        return 'siding' if k == 1 else 'plaster'
    for m, mesh in grid_solid(xs, ys, [-T, -0.05, 0.0], cell).items(): p.add(m, mesh)
    gaps = [(a - 0.12, b + 0.12) for (a, b, c, d) in holes if c < 0.43]
    for (a, b) in segs_excl(gaps, xa, xb):
        if b - a > 0.01: p.box('trim', a, b, 0.3, 0.42, 0.0, 0.02)
    for x in np.arange(-0.8, 0.81, 0.4):
        if x - 0.03 < xa or x + 0.03 > xb: continue
        ys_ = [(0.42, H)]
        for (a, b, c, d) in list(cas):
            if a - 0.03 < x < b + 0.03: ys_ = [s for (y0, y1) in ys_ for s in ((y0, min(y1, c)), (max(y0, d), y1)) if s[1] - s[0] > 0.02]
        for (y0, y1) in ys_: p.box('batten', x - 0.03, x + 0.03, y0, y1, 0.0, 0.022)
def w_casing(p, a, b, y0, y1, sill=True):
    """Guarnicao larga de tabua em volta do vao, com testeira e (janela) peitoril com pingadeira."""
    for (c, d) in ((a - 0.12, a), (b, b + 0.12)): p.box('trim', c, d, 0.0 if y0 < 0.43 else y0 - 0.06, y1 + 0.12, 0.0, 0.025)
    p.box('trim', a, b, y1, y1 + 0.12, 0.0, 0.025); p.box('trim', a - 0.15, b + 0.15, y1 + 0.12, y1 + 0.16, 0.0, 0.05)
    if sill: prof_x(p, 'trim', a - 0.15, b + 0.15, [(-0.1, y0 - 0.04), (0.06, y0 - 0.06), (0.06, y0 - 0.02), (-0.1, y0 + 0.004)])
    return (a - 0.12, b + 0.12, y0 - 0.1 if sill else -1.0, y1 + 0.17)
def w_sash(p, a, b, y0, y1, nx=2, ny=2):
    """Caixilho fixo de madeira com vidros em grade (no meio da espessura)."""
    f = 0.045
    p.box('trim', a, a + f, y0, y1, -0.13, -0.07); p.box('trim', b - f, b, y0, y1, -0.13, -0.07)
    p.box('trim', a + f, b - f, y0, y0 + 0.06, -0.13, -0.07); p.box('trim', a + f, b - f, y1 - f, y1, -0.13, -0.07)
    for i in range(1, nx): x = a + (b - a) * i / nx; p.box('trim', x - 0.015, x + 0.015, y0 + 0.06, y1 - f, -0.12, -0.08)
    for j in range(1, ny): y = y0 + 0.06 + (y1 - f - y0 - 0.06) * j / ny; p.box('trim', a + f, b - f, y - 0.015, y + 0.015, -0.12, -0.08)
    p.box('glass', a + f - 0.004, b - f + 0.004, y0 + 0.056, y1 - f + 0.004, -0.103, -0.097)
def w_mod(kind='plain', tl=0.0, tr_=0.0, H=ME):
    """plain, win (janela de 4 vidros), door (porta de tabuas), bay (modulo de 4 m com portao de correr aberto para a direita),
    chute (abertura da esteira de serragem)."""
    p = Piece(); hw = 2.0 if kind == 'bay' else 1.0; xa, xb = -hw + tl, hw - tr_
    if kind == 'win':
        cas = [w_casing(p, -0.5, 0.5, 1.4, 2.6)]; w_core(p, [(-0.5, 0.5, 1.4, 2.6)], xa, xb, H, cas); w_sash(p, -0.5, 0.5, 1.4, 2.6)
    elif kind == 'door':
        cas = [w_casing(p, -0.5, 0.5, 0.0, 2.3, False)]; w_core(p, [(-0.5, 0.5, 0.0, 2.3)], xa, xb, H, cas)
        for s in (-1, 1): a, b = sorted((s * 0.5, s * 0.47)); p.box('trim', a, b, 0.0, 2.3, -0.2, -0.05)
        p.box('trim', -0.47, 0.47, 2.27, 2.3, -0.2, -0.05); p.cham('steel', -0.5, 0.5, -0.02, 0.006, -T + 0.004, 0.03, 0.003)
        p.merge(wall_lantern(), tr(0.82, 2.4, 0.025))
    elif kind == 'chute':
        cas = [w_casing(p, -0.6, 0.6, 3.2, 4.2)]; w_core(p, [(-0.6, 0.6, 3.2, 4.2)], xa, xb, H, cas)
        p.box('steel_d', -0.6, 0.6, 3.2, 3.24, -T, 0.0)
    elif kind == 'bay':
        a, b = -1.8, 1.8
        cas = [w_casing(p, a, b, 0.0, 4.0, False)]; w_core(p, [(a, b, 0.0, 4.0)], xa, xb, H, cas)
        for s in (-1, 1): c, d = sorted((s * 1.8, s * 1.76)); p.box('trim', c, d, 0.0, 4.0, -T, -0.0)
        p.box('steel', a, b, -0.02, 0.006, -T + 0.004, 0.04)
        # trilho, suportes e portao de correr aberto (sobre os modulos da direita)
        p.box('steel_d', -1.95, 6.0, 4.3, 4.38, 0.06, 0.12)
        for x in np.arange(-1.7, 5.9, 1.0): p.box('steel_d', x - 0.04, x + 0.04, 4.26, 4.42, 0.001, 0.06)
        x0, x1, y0, y1, z0, z1 = 2.05, 5.85, 0.06, 4.2, 0.13, 0.18
        n = 19
        for i in range(n):
            u0 = x0 + (x1 - x0) * i / n + 0.003; u1 = x0 + (x1 - x0) * (i + 1) / n - 0.003; p.box('door', u0, u1, y0, y1, z0, z1)
        p.box('dkwood', x0 + 0.01, x1 - 0.01, y0 + 0.02, y1 - 0.02, z0 + 0.01, z1 - 0.01)
        for (yy0, yy1) in ((y0, y0 + 0.18), ((y0 + y1) / 2 - 0.09, (y0 + y1) / 2 + 0.09), (y1 - 0.18, y1)): p.box('trim', x0, x1, yy0, yy1, z1, z1 + 0.025)
        for (xx0, xx1) in ((x0, x0 + 0.18), (x1 - 0.18, x1)): p.box('trim', xx0, xx1, y0 + 0.18, y1 - 0.18, z1, z1 + 0.025)
        for (ya, yb) in ((y0 + 0.18, (y0 + y1) / 2 - 0.09), ((y0 + y1) / 2 + 0.09, y1 - 0.18)):
            q = Polygon([(x0 + 0.18, ya), (x0 + 0.38, ya), (x1 - 0.18, yb - 0.2), (x1 - 0.18, yb), (x1 - 0.38, yb), (x0 + 0.18, ya + 0.2)]); ext(p, 'trim', q, z1, z1 + 0.025)
        for x in (x0 + 0.5, x1 - 0.5):
            p.box('steel_d', x - 0.04, x + 0.04, y1 - 0.1, 4.36, z0 + 0.0, z0 - 0.0 + 0.04) if False else p.box('steel_d', x - 0.04, x + 0.04, y1 - 0.25, 4.34, z0 - 0.04, z0)
            disc_z(p, 'steel', 0.07, 0.065, 0.1, x, 4.34, 16)
            seg_cyl(p, 'steel_d', (x, 4.34, 0.06), (x, 4.34, z0 - 0.04), 0.015, 6)
        p.box('steel_d', x0 + 0.2, x0 + 0.26, 1.0, 1.4, z1 + 0.025, z1 + 0.07)
    else:
        w_core(p, [], xa, xb, H)
    return p
def door_plank(w=0.94, h=2.26, t=0.05):
    """Porta de tabuas verticais com travessas e mao-francesa em Z, dobradicas de ferro em T e trinco (pivo: dobradica, embaixo)."""
    p = Piece(); n = 7
    for i in range(n):
        a = w * i / n + 0.002; b = w * (i + 1) / n - 0.002; p.box('door', a, b, 0.0, h, -t / 2, t / 2 - 0.012)
    p.box('dkwood', 0.006, w - 0.006, 0.01, h - 0.01, -t / 2 + 0.004, t / 2 - 0.016)
    for (y0, y1) in ((0.18, 0.34), (h / 2 - 0.08, h / 2 + 0.08), (h - 0.34, h - 0.18)): p.box('door', 0.04, w - 0.04, y0, y1, t / 2 - 0.012, t / 2 + 0.014)
    for (ya, yb) in ((0.34, h / 2 - 0.08), (h / 2 + 0.08, h - 0.34)):
        q = Polygon([(0.06, ya), (0.22, ya), (w - 0.06, yb - 0.16), (w - 0.06, yb), (w - 0.22, yb), (0.06, ya + 0.16)]); ext(p, 'door', q, t / 2 - 0.012, t / 2 + 0.01)
    for (y0, y1) in ((0.24, 0.28), (h - 0.28, h - 0.24)): p.box('iron', -0.01, 0.5, y0, y1, t / 2 + 0.014, t / 2 + 0.02); p.box('iron', -0.01, 0.03, y0 - 0.08, y1 + 0.08, t / 2 + 0.014, t / 2 + 0.02)
    for z in (1, -1):
        p.box('iron', w - 0.14, w - 0.08, 0.92, 1.12, *sorted((z * (t / 2 + (0.014 if z > 0 else 0.0)), z * (t / 2 + (0.03 if z > 0 else 0.016)))))
        seg_cyl(p, 'iron', (w - 0.11, 1.0, z * (t / 2 + (0.03 if z > 0 else 0.016))), (w - 0.11, 1.0, z * (t / 2 + 0.07)), 0.012, 6)
    return p

# ============================================================================ telhados de chapa ondulada (pivo: origem, coordenadas absolutas)
def corr_roof(p, x0, x1, z0, z1, ye, pitch, ov_e, ov_g, Ti, along='x', th=0.06, fascia=True):
    """Telhado de 2 aguas de chapa ondulada: placas, nervuras a cada 20 cm, cumeeira, testeiras nos beirais e nas empenas.
    A face de baixo passa pela face interna das paredes (Ti para dentro) na cota ye. along = direcao da cumeeira.
    Devolve (y_rufo(d), yr): altura da face de baixo em funcao da distancia d da cumeeira, e a altura da cumeeira."""
    tn = math.tan(pitch)
    if along == 'x': c = (z0 + z1) / 2; hw = (z1 - z0) / 2; a0, a1 = x0 - ov_g, x1 + ov_g
    else: c = (x0 + x1) / 2; hw = (x1 - x0) / 2; a0, a1 = z0 - ov_g, z1 + ov_g
    yr = ye + (hw - Ti) * tn
    yb = lambda d: yr - d * tn
    def P(a, d, y):   # a ao longo da cumeeira, d distancia com sinal a partir da cumeeira
        return (a, y, c + d) if along == 'x' else (c + d, y, a)
    de = hw + ov_e
    for s in (-1, 1):
        p.hull('roofm', [P(a, s * d, yb(d) + e) for a in (a0, a1) for d in (0.0, de) for e in (0.0, th)])
        for a in np.arange(a0 + 0.1, a1 - 0.05, 0.2):
            p.seg('roofm', P(a, s * 0.16, yb(0.16) + th + 0.008), P(a, s * de, yb(de) + th + 0.008), 0.035, 0.022)
        if fascia:
            ya, yb_ = yb(de) - 0.16, yb(de) + th
            if along == 'x': p.box('trim', a0 - 0.03, a1 + 0.03, ya, yb_, *sorted((c + s * de, c + s * (de + 0.03))))
            else: p.box('trim', *sorted((c + s * de, c + s * (de + 0.03))), ya, yb_, a0 - 0.03, a1 + 0.03)
        for a, sa in ((a0, -1), (a1, 1)):   # testeiras das empenas (inclinadas)
            pts = [P(a + sa * e, s * d, y) for e in (0.0, 0.03) for (d, y) in ((0.0, yb(0.0) - 0.16), (0.0, yb(0.0) + th + 0.03), (de, yb(de) - 0.16), (de, yb(de) + th + 0.03))]
            p.hull('trim', pts)
    p.hull('roofm', [P(a, d, yb(abs(d)) + th + e) for a in (a0 - 0.02, a1 + 0.02) for (d, e) in ((-0.25, 0.01), (0.25, 0.01), (0.0, 0.09))])
    return yb, yr
def gable(p, z0, z1, ye, yr, xo, xi, ridge_c, Ti, inner='plaster', plane='x'):
    """Empena triangular de tabua e mata-junta. plane='x': parede no plano x (face externa em xo, interna em xi), triangulo em z.
    plane='z': parede no plano z, triangulo em x. A borda de cima acompanha a face de baixo do telhado."""
    hw = (z1 - z0) / 2; tn = (yr - ye) / (hw - Ti)
    top = lambda u: yr - abs(u - ridge_c) * tn
    pts = [(z0 + Ti, ye), (z1 - Ti, ye), (ridge_c, yr)]
    xm = xo + (0.05 if xi > xo else -0.05)
    for (a, b, m) in ((xo, xm, 'siding'), (xm, xi, inner)):
        a, b = sorted((a, b))
        if plane == 'x': prof_x(p, m, a, b, [(z, y) for (z, y) in pts])
        else: prof_z(p, m, a, b, [(z, y) for (z, y) in pts])
    s = 1 if xo > xi else -1
    for u in np.arange(z0 + 0.2, z1 - 0.1, 0.4):
        if u - 0.03 < z0 + Ti or u + 0.03 > z1 - Ti: continue
        y1 = top(u) - 0.05
        if y1 - ye < 0.05: continue
        a, b = sorted((xo, xo + s * 0.022))
        if plane == 'x': p.box('batten', a, b, ye, y1, u - 0.03, u + 0.03)
        else: p.box('batten', u - 0.03, u + 0.03, ye, y1, a, b)

# ============================================================================ galpao da serra
MB = sbox(MX0, MZ0, MX1, MZ1); MI = off(MB, -T)
def m_roof():
    """Galpao da serra: empenas, telhado de chapa ondulada com lanternim de janelas, tesouras de madeira, cantoneiras de tabua."""
    p = Piece(); zc = (MZ0 + MZ1) / 2
    yb, yr = corr_roof(p, MX0, MX1, MZ0, MZ1, ME, MPITCH, MOV, 0.35, T)
    for (xo, xi) in ((MX0, MX0 + T), (MX1, MX1 - T)): gable(p, MZ0, MZ1, ME, yr, xo, xi, zc, T)
    # lanternim
    tn = math.tan(MPITCH); h0 = yb(0.9) - 0.05; ht = yr + 0.95
    for s in (-1, 1):
        z = zc + s * 0.9; za, zb = sorted((z, z - s * 0.05))
        p.box('siding', -10.0, -2.0, h0, ht, za, zb); p.box('plaster', -10.0, -2.0, h0, ht, *sorted((z - s * 0.05, z - s * 0.12)))
        for k in range(6):
            x = -9.6 + k * 1.3; a, b = x, x + 1.0
            p.box('trim', a - 0.08, b + 0.08, yr + 0.18, yr + 0.82, *sorted((z, z + s * 0.025)))
            p.box('glass', a, b, yr + 0.26, yr + 0.74, *sorted((z + s * 0.025, z + s * 0.031)))
            p.box('trim', (a + b) / 2 - 0.015, (a + b) / 2 + 0.015, yr + 0.26, yr + 0.74, *sorted((z + s * 0.031, z + s * 0.045)))
    for x in (-10.0, -2.0):
        a, b = sorted((x, x + (0.05 if x > -6 else -0.05)))
        prof_x(p, 'siding', a, b, [(zc - 0.9, h0), (zc + 0.9, h0), (zc + 0.9, ht), (zc, ht + 0.9 * tn), (zc - 0.9, ht)])
    corr_roof(p, -10.0, -2.0, zc - 0.9, zc + 0.9, ht, MPITCH, 0.3, 0.25, 0.0, th=0.05)
    # tesouras
    for x in np.arange(-10.0, -1.9, 2.0):
        zi0, zi1 = MZ0 + T, MZ1 - T; w_ = 0.09
        p.seg('dkwood', (x, ME - 0.12, zi0), (x, ME - 0.12, zi1), w_, 0.2)
        for s in (-1, 1):
            zi = zc + s * (5.0 - T)
            p.seg('dkwood', (x, ME - 0.1, zi), (x, yr - 0.12, zc), w_, 0.2)
            p.seg('dkwood', (x, ME - 0.1, zc + s * 2.2), (x, yb(2.2) - 0.18 + 0.0 + 0.6 * 0, zc + s * 1.0), w_, 0.12) if False else p.seg('dkwood', (x, ME - 0.05, zc + s * 2.0), (x, yb(1.0) - 0.2, zc + s * 1.0), w_, 0.12)
        p.seg('dkwood', (x, ME - 0.22, zc), (x, yr - 0.2, zc), w_, 0.14)
    for x in np.arange(-11.5, -0.4, 1.0): pass
    # cantoneiras de tabua nas quinas
    for (x, z, sx, sz) in ((MX0, MZ1, -1, 1), (MX1, MZ1, 1, 1), (MX0, MZ0, -1, -1), (MX1, MZ0, 1, -1)):
        a, b = sorted((x, x - sx * 0.14)); c, d = sorted((z + sz * 0.002, z + sz * 0.032)); p.box('trim', a, b, 0.31, ME, c, d)
        a, b = sorted((x + sx * 0.002, x + sx * 0.032)); c, d = sorted((z + sz * 0.032, z - sz * 0.14)); p.box('trim', a, b, 0.31, ME, c, d)
    return p
def m_floor():
    """Piso de concreto com juntas, trilhos do carro porta-toras e manchas de serragem."""
    p = Piece(); ext_y(p, 'conc_f', MI, GY - Y0 + 0.02, 0.0)
    for x in np.arange(MX0 + T + 2.0, MX1 - T, 2.0): p.box('dark', x - 0.006, x + 0.006, 0.0, 0.001, MZ0 + T, MZ1 - T)
    for z in (-10.35, -9.65):
        p.box('steel', -11.4, -1.6, 0.0, 0.06, z - 0.03, z + 0.03); p.box('steel', -11.4, -1.6, 0.06, 0.09, z - 0.025, z + 0.025)
        for x in np.arange(-11.2, -1.6, 0.8): p.box('dkwood', x - 0.08, x + 0.08, 0.0, 0.03, z - 0.2, z + 0.2) if False else None
    for x in (-11.45, -1.55): p.box('steel_d', x - 0.05, x + 0.05, 0.0, 0.3, -10.5, -9.5)
    return p

# ============================================================================ escritorio
OB = sbox(OX0, OZ0, OX1, OZ1); OI = off(OB, -T)
def o_roof():
    """Escritorio: forro, empenas da frente e dos fundos, telhado de chapa ondulada com cumeeira ao longo de Z, chamine do fogao."""
    p = Piece(); ext_y(p, 'ceil', OI, 2.6, 2.63)
    p.box('frame', 13.6, 14.4, 2.594, 2.6, 7.6, 8.4); p.box('lamp_glass', 13.65, 14.35, 2.588, 2.594, 7.65, 8.35)
    yb, yr = corr_roof(p, OX0, OX1, OZ0, OZ1, OE, math.radians(30), 0.4, 0.35, T, along='z')
    for (zo, zi) in ((OZ0, OZ0 + T), (OZ1, OZ1 - T)): gable(p, OX0, OX1, OE, yr, zo, zi, (OX0 + OX1) / 2, T, plane='z')
    x, z = 15.0, 7.0
    p.cyl('iron', 0.08, 2.63, yr + 1.0, x, z, 14); lathe(p, 'iron', [(0.0, yr + 1.32), (0.2, yr + 1.12), (0.17, yr + 1.08)], x, z, 0.0, 14)
    for k in range(3): seg_cyl(p, 'iron', (x + 0.15 * math.cos(k * 2.1), yr + 1.1, z + 0.15 * math.sin(k * 2.1)), (x, yr + 1.0, z), 0.008, 4)
    lathe(p, 'iron', [(0.25, yb(1.0) + 0.04), (0.12, yb(1.0) + 0.14), (0.0, yb(1.0) + 0.14)] if False else [(0.22, yb(1.0) + 0.03), (0.1, yb(1.0) + 0.2)], x, z, 0.0, 14)
    for (xx, zz, sx, sz) in ((OX0, OZ1, -1, 1), (OX1, OZ1, 1, 1), (OX0, OZ0, -1, -1), (OX1, OZ0, 1, -1)):
        a, b = sorted((xx, xx - sx * 0.14)); c, d = sorted((zz + sz * 0.002, zz + sz * 0.032)); p.box('trim', a, b, 0.31, OE, c, d)
        a, b = sorted((xx + sx * 0.002, xx + sx * 0.032)); c, d = sorted((zz + sz * 0.032, zz - sz * 0.14)); p.box('trim', a, b, 0.31, OE, c, d)
    return p
def o_floor():
    p = Piece(); ext_y(p, 'concrete', OI, GY - Y0 + 0.02, -0.012); ext_y(p, 'wood', OI, -0.012, 0.0)
    p.box('concrete', 12.4, 13.6, GY, 0.0 + Y0 - 0.0, OZ1, OZ1 + 0.8) if False else ext_y(p, 'concrete', sbox(12.35, OZ1, 13.65, OZ1 + 0.8), GY, Y0)
    ext_y(p, 'trim', OI.difference(off(OI, -0.016)).difference(sbox(12.4, OZ1 - T - 0.1, 13.6, OZ1 - T + 0.1)), 0.0, 0.1)
    return p

# ============================================================================ queimador conico e esteira (pivo: origem)
def bur_r(y): return BUR_R0 + (BUR_R1 - BUR_R0) * (y - 0.9) / (BUR_H - 0.9)
def on_cone(a, y, d=0.0):
    r = bur_r(y) + d; return (BUR_X + r * math.cos(a), y, BUR_Z + r * math.sin(a))
def burner():
    """Queimador conico de chapa enferrujada: base de concreto, costuras verticais, aros, portinhola de inspecao, boca da esteira,
    escada de marinheiro e tela em cupula no topo."""
    p = Piece(); x, z = BUR_X, BUR_Z
    p.cyl('concrete', BUR_R0 + 0.25, GY, 0.9, x, z, 40); p.cyl('concrete', BUR_R0 + 0.3, 0.84, 0.9, x, z, 40) if False else ring_y(p, 'concrete', BUR_R0 + 0.25, BUR_R0 + 0.32, 0.8, 0.9, x, z, 40)
    lathe(p, 'rust', [(BUR_R0, 0.9), (BUR_R1, BUR_H)], x, z, 0.0, 40)
    for k in range(20):
        a = k * 2 * math.pi / 20; seg_cyl(p, 'rust_d', on_cone(a, 0.9, -0.01), on_cone(a, BUR_H, -0.01), 0.035, 6)
    for y in (2.4, 4.3, 6.2, 8.1, 10.0):
        r = bur_r(y); ring_y(p, 'rust_d', r - 0.06, r + 0.05, y, y + 0.1, x, z, 40)
    ring_y(p, 'rust_d', BUR_R1 - 0.1, BUR_R1 + 0.08, BUR_H - 0.02, BUR_H + 0.14, x, z, 32); p.cyl('dark', BUR_R1 - 0.12, BUR_H, BUR_H + 0.004, x, z, 32)
    for k in range(16):   # cupula de tela
        a = k * 2 * math.pi / 16; pts = [(x + BUR_R1 * math.cos(t) * math.cos(a), BUR_H + 0.14 + BUR_R1 * 0.75 * math.sin(t), z + BUR_R1 * math.cos(t) * math.sin(a)) for t in np.linspace(0, math.pi / 2, 6)]
        for i in range(5): seg_cyl(p, 'mesh', pts[i], pts[i + 1], 0.018, 4)
    for t in (0.35, 0.7, 1.05):
        rr = BUR_R1 * math.cos(t); yy = BUR_H + 0.14 + BUR_R1 * 0.75 * math.sin(t)
        pts = [(x + rr * math.cos(a), yy, z + rr * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)]
        for i in range(24): seg_cyl(p, 'mesh', pts[i], pts[i + 1], 0.015, 4)
    p.sphere('mesh', 0.06, x, BUR_H + 0.14 + BUR_R1 * 0.75, z, 1)
    # portinhola de frente para o patio (+Z)
    a0 = math.pi / 2; da = 0.6 / BUR_R0
    p.hull('steel_d', [on_cone(a, y, d) for a in (a0 - da, a0 + da) for y in (1.2, 2.5) for d in (0.0, 0.05)])
    for y in (1.4, 2.3): seg_cyl(p, 'iron', on_cone(a0 - da, y, 0.07), on_cone(a0 - da * 0.6, y, 0.07), 0.025, 6)
    seg_cyl(p, 'iron', on_cone(a0 + da * 0.6, 1.85, 0.05), on_cone(a0 + da * 0.6, 1.85, 0.16), 0.02, 6)
    # boca da esteira (lado do galpao, -X)
    a1 = math.pi
    p.hull('rust_d', [on_cone(a1 + s * 0.2, y, -0.05) for s in (-1, 1) for y in (7.3, 8.9)] + [(x - bur_r(8.1) - 0.7, y, z + s * 0.6) for s in (-1, 1) for y in (7.5, 8.7)])
    # escada de marinheiro no lado de tras (+X)
    a2 = 0.0
    for s in (-1, 1):
        aa = a2 + s * 0.22 / BUR_R0; seg_cyl(p, 'steel_d', on_cone(aa, 0.9, 0.22), on_cone(aa, BUR_H - 0.3, 0.22), 0.02, 6)
        for y in np.arange(1.2, BUR_H - 0.3, 0.3): seg_cyl(p, 'steel_d', on_cone(aa, y, 0.0), on_cone(aa, y, 0.22), 0.012, 4) if abs(y - 1.2) < 0.01 or abs(y % 1.8) < 0.15 else None
    for y in np.arange(1.2, BUR_H - 0.3, 0.3): seg_cyl(p, 'steel_d', on_cone(a2 - 0.22 / BUR_R0, y, 0.22), on_cone(a2 + 0.22 / BUR_R0, y, 0.22), 0.014, 4)
    return p
CONV_A = np.array([-0.6, Y0 + 3.3, -9.0]); CONV_B = np.array([BUR_X - bur_r(8.1) - 0.7, 7.9, -9.0])
def conveyor():
    """Esteira de serragem inclinada em trelica de cantoneira: banzos, montantes, diagonais, roletes, correia, chapas laterais,
    passarela com guarda-corpo e cavalete de apoio com contraventamento (pivo: origem)."""
    p = Piece(); A, B = CONV_A, CONV_B; u = (B - A) / np.linalg.norm(B - A); Ln = np.linalg.norm(B - A); n = int(Ln / 0.8)
    up = np.array([-u[1], u[0], 0.0]); up /= np.linalg.norm(up)
    for zz in (-0.4, 0.4):
        o = np.array([0, 0, zz])
        seg_cyl(p, 'steel_d', A + o, B + o, 0.035, 6); seg_cyl(p, 'steel_d', A + o + 0.6 * up, B + o + 0.6 * up, 0.03, 6)
        for i in range(n + 1):
            q = A + o + u * Ln * i / n; seg_cyl(p, 'steel_d', q, q + 0.6 * up, 0.018, 4)
            if i < n: seg_cyl(p, 'steel_d', q, A + o + u * Ln * (i + 1) / n + 0.6 * up, 0.015, 4)
        p.hull('metal', [A + o + 0.1 * up + np.array([0, 0, -0.01 if zz < 0 else 0.0]), B + o + 0.1 * up, A + o + 0.32 * up, B + o + 0.32 * up,
                         A + o + 0.1 * up + np.array([0, 0, 0.01]), B + o + 0.1 * up + np.array([0, 0, 0.01]), A + o + 0.32 * up + np.array([0, 0, 0.01]), B + o + 0.32 * up + np.array([0, 0, 0.01])])
    for i in range(n * 2 + 1):
        q = A + u * Ln * i / (2 * n) + 0.08 * up; seg_cyl(p, 'steel', q + np.array([0, 0, -0.36]), q + np.array([0, 0, 0.36]), 0.03, 8)
    p.hull('rubber', [A + e * up + np.array([0, 0, s * 0.34]) for e in (0.11, 0.125) for s in (-1, 1)] + [B + e * up + np.array([0, 0, s * 0.34]) for e in (0.11, 0.125) for s in (-1, 1)])
    for i in range(n * 3):
        q = A + u * Ln * (i + 0.5) / (3 * n) + 0.13 * up; p.sphere('sawdust', 0.08, q[0], q[1], q[2] + ((i * 37) % 5 - 2) * 0.06, 0)
    # cavalete
    t = (3.2 - A[0]) / (B[0] - A[0]); q = A + (B - A) * t
    for zz in (-0.6, 0.6):
        seg_cyl(p, 'steel_d', (3.2, 0.0, -9.0 + zz), (3.2, q[1] - 0.04, -9.0 + zz), 0.06, 8); p.box('concrete', 2.9, 3.5, -0.1, 0.12, -9.3 + zz, -8.7 + zz)
    seg_cyl(p, 'steel_d', (3.2, q[1] - 0.05, -9.6), (3.2, q[1] - 0.05, -8.4), 0.04, 6)
    for (y0, y1) in ((0.4, q[1] - 0.3), ):
        seg_cyl(p, 'steel_d', (3.2, y0, -9.6), (3.2, y1, -8.4), 0.025, 6); seg_cyl(p, 'steel_d', (3.2, y0, -8.4), (3.2, y1, -9.6), 0.025, 6)
    # funil de entrada dentro do galpao
    p.hull('rust_d', [(A[0] + dx, A[1] + dy, A[2] + dz) for (dx, dy, dz) in ((-0.6, 0.6, -0.6), (-0.6, 0.6, 0.6), (0.2, 0.6, -0.6), (0.2, 0.6, 0.6), (-0.3, 0.1, -0.3), (-0.3, 0.1, 0.3), (0.1, 0.1, -0.3), (0.1, 0.1, 0.3))])
    for zz in (-0.5, 0.5): seg_cyl(p, 'steel_d', (A[0] - 0.4, 0.0 + Y0, A[2] + zz), (A[0] - 0.4, A[1] + 0.2, A[2] + zz), 0.035, 6)
    return p

# ============================================================================ galpao aberto de tabuas (pivo: origem)
SH_POSTS = [-14.0, -10.0, -6.0, -2.0, 2.0]
SH_PITCH = math.atan((SHR - SHE) / ((SHZ1 - SHZ0) / 2 - 0.1))
def lumber_shed():
    """Galpao aberto: laje de concreto, pilares de madeira sobre blocos, vigas, maos-francesas, tirantes, caibros, cumeeira e
    telhado de chapa ondulada de 2 aguas com beiral largo."""
    p = Piece(); zc = (SHZ0 + SHZ1) / 2
    ext_y(p, 'concrete', sbox(SHX0 - 0.4, SHZ0 - 0.4, SHX1 + 0.4, SHZ1 + 0.4), GY, Y0)
    for x in SH_POSTS:
        for z in (SHZ0, SHZ1):
            p.cham('concrete', x - 0.2, x + 0.2, Y0, Y0 + 0.3, z - 0.2, z + 0.2, 0.02); p.box('post', x - 0.1, x + 0.1, Y0 + 0.3, SHE - 0.4, z - 0.1, z + 0.1)
            p.box('steel_d', x - 0.11, x + 0.11, Y0 + 0.3, Y0 + 0.5, z - 0.11, z + 0.11)
            for s in (-1, 1):
                if SHX0 - 0.01 < x + s * 0.9 < SHX1 + 0.01: p.seg('post', (x + s * 0.05, SHE - 1.3, z), (x + s * 0.85, SHE - 0.42, z), 0.08, 0.1)
        p.seg('post', (x, SHE - 0.55, SHZ0 + 0.1), (x, SHE - 0.55, SHZ1 - 0.1), 0.1, 0.18)
        p.seg('post', (x, SHE - 0.46, zc), (x, SHR - 0.25, zc), 0.1, 0.12)
    for z in (SHZ0, SHZ1): p.box('post', SHX0 - 0.1, SHX1 + 0.1, SHE - 0.4, SHE - 0.1, z - 0.1, z + 0.1)
    yb, yr = corr_roof(p, SHX0, SHX1, SHZ0, SHZ1, SHE, SH_PITCH, 0.7, 0.5, 0.1)
    p.box('post', SHX0 - 0.3, SHX1 + 0.3, yr - 0.32, yr - 0.02, zc - 0.06, zc + 0.06)
    for x in np.arange(SHX0 - 0.3, SHX1 + 0.31, 0.8):
        for s in (-1, 1):
            d0, d1 = 0.06, (SHZ1 - SHZ0) / 2 + 0.6
            p.seg('post', (x, yb(d0) - 0.1, zc + s * d0), (x, yb(d1) - 0.1, zc + s * d1), 0.06, 0.18)
    return p

# ============================================================================ maquinas da serra (pivo: chao)
def log(p, x0, x1, y, z, r, seed=0, along='x'):
    """Tora: casca, topos de madeira clara com aneis e um leve cerne."""
    if along == 'x':
        disc_x(p, 'bark', r, x0, x1, y, z, 14)
        for (a, b) in ((x0 - 0.012, x0), (x1, x1 + 0.012)): disc_x(p, 'log_end', r - 0.03, a, b, y, z, 14)
        for (a, b) in ((x0 - 0.016, x0 - 0.012), (x1 + 0.012, x1 + 0.016)): disc_x(p, 'bark', r * 0.25, a, b, y, z, 10)
    else:
        disc_z(p, 'bark', r, x0, x1, y, z, 14) if False else None
        m = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=14); m.apply_translation([z, y, (x0 + x1) / 2]); p.add('bark', m)
        for (a, b) in ((x0 - 0.012, x0), (x1, x1 + 0.012)): disc_z(p, 'log_end', r - 0.03, a, b, z, y, 14)
        for (a, b) in ((x0 - 0.016, x0 - 0.012), (x1 + 0.012, x1 + 0.016)): disc_z(p, 'bark', r * 0.25, a, b, z, y, 10)
def band_saw():
    """Serra de fita de cabeceira: coluna, volantes de cima e de baixo com protetores, lamina, guias, motor e painel (pivo: lamina, chao;
    o carro passa em +Z)."""
    p = Piece()
    p.cham('concrete', -1.2, 1.2, 0.0, 0.25, -1.1, -0.2, 0.02)
    p.cham('tank_g', -0.35, 0.35, 0.25, 4.1, -0.95, -0.45, 0.03)
    for (y, r) in ((3.3, 0.85), (0.95, 0.75)):
        disc_z(p, 'tank_g', r + 0.08, -0.42, -0.12, 0.0, y, 32); disc_z(p, 'steel_d', 0.16, -0.45, -0.42, 0.0, y, 16) if False else disc_z(p, 'steel', 0.16, -0.12, -0.09, 0.0, y, 16)
    p.box('chrome', 0.78, 0.8, 0.95, 3.3, -0.2, -0.1); p.box('chrome', -0.8, -0.78, 0.95, 3.3, -0.2, -0.1)
    p.cham('tank_g', 0.62, 0.98, 1.95, 2.5, -0.3, -0.05, 0.01); p.box('steel', 0.7, 0.9, 1.7, 1.95, -0.22, -0.12)
    p.cham('dark', -1.1, -0.45, 0.25, 0.9, -1.0, -0.5, 0.02); disc_x(p, 'steel_d', 0.2, -1.2, -1.1, 0.6, -0.75, 16)
    p.cham('steel_d', 0.45, 0.85, 0.9, 1.7, -1.05, -0.95, 0.01)
    for k, m in enumerate(('lamp_glass', 'tool_r', 'yellow')): p.cyl(m, 0.03, 1.4 - k * 0.15, 1.42 - k * 0.15, 0.65, -0.94, 10) if False else disc_z(p, m, 0.03, -0.95, -0.93, 0.65, 1.45 - k * 0.15, 10)
    return p
def carriage():
    """Carro porta-toras sobre trilhos: chassi, 4 rodas de flange, 3 cabecotes com esquadros amarelos e a tora presa por garras
    (pivo: centro, cota do trilho; anda em X)."""
    p = Piece(); L1 = 3.0; x = L1 / 2
    for z in (-0.35, 0.35):
        for xx in (-x + 0.35, x - 0.35): disc_z(p, 'steel_d', 0.14, z - 0.04, z + 0.04, xx, 0.23, 16)
    p.cham('steel_d', -x, x, 0.26, 0.42, -0.45, 0.45, 0.02)
    for xx in (-x + 0.3, 0.0, x - 0.3):
        p.cham('steel_d', xx - 0.15, xx + 0.15, 0.42, 0.55, -0.45, 0.4, 0.01)
        p.cham('yellow', xx - 0.1, xx + 0.1, 0.55, 1.35, -0.5, -0.38, 0.01)
        seg_cyl(p, 'steel', (xx, 1.2, -0.38), (xx, 1.05, -0.1), 0.025, 6)
    log(p, -x + 0.05, x - 0.05, 0.55 + 0.34, 0.0, 0.34)
    p.cham('steel_d', -x - 0.3, -x, 0.26, 1.1, -0.2, 0.2, 0.01); p.cham('dark', -x - 0.28, -x - 0.02, 1.1, 1.3, -0.18, 0.18, 0.01)
    return p
def roller_table(L1=4.0):
    """Mesa de roletes com cavaletes de aco e uma tabua em cima (pivo: centro, chao; ao longo de X)."""
    p = Piece(); x = L1 / 2
    for z in (-0.35, 0.35): p.box('steel_d', -x, x, 0.72, 0.8, z - 0.03, z + 0.03)
    for xx in np.arange(-x + 0.3, x - 0.2, 1.2):
        for z in (-0.35, 0.35): p.box('steel_d', xx - 0.03, xx + 0.03, 0.0, 0.72, z - 0.03, z + 0.03)
        p.box('steel_d', xx - 0.03, xx + 0.03, 0.25, 0.3, -0.32, 0.32)
    for xx in np.arange(-x + 0.2, x - 0.1, 0.4): seg_cyl(p, 'steel', (xx, 0.84, -0.32), (xx, 0.84, 0.32), 0.04, 10)
    p.box('lumber', -x + 0.4, x - 0.6, 0.88, 0.93, -0.12, 0.18); return p
def edger():
    """Refiladeira: carcaca verde com mesa de entrada, rolos de tracao, motor e caixa de serragem (pivo: centro, chao; entrada em -X)."""
    p = Piece(); p.cham('tank_g', -0.6, 0.6, 0.0, 1.2, -0.6, 0.6, 0.03); p.hull('tank_g', [(x, y, z) for x in (-0.55, 0.55) for (y, z) in ((1.2, -0.6), (1.2, 0.6), (1.45, -0.4), (1.45, 0.4))])
    p.box('steel_d', -1.5, -0.6, 0.78, 0.84, -0.5, 0.5)
    for xx in (-1.3, -0.9): seg_cyl(p, 'steel', (xx, 0.88, -0.45), (xx, 0.88, 0.45), 0.045, 10)
    for z in (-0.45, 0.45): p.box('steel_d', -1.45, -1.39, 0.0, 0.78, z - 0.03, z + 0.03)
    p.cham('dark', 0.6, 1.1, 0.2, 0.7, -0.3, 0.3, 0.02); disc_x(p, 'steel', 0.12, 1.1, 1.15, 0.45, 0.0, 14)
    p.cham('steel_d', -0.3, 0.3, 1.45, 1.7, -0.3, 0.3, 0.01); return p
def lumber_cart(L1=2.4, layers=5):
    """Carrinho de tabuas: plataforma de chapa com 4 rodizios, puxador e uma pilha de tabuas (pivo: centro, chao; ao longo de X)."""
    p = Piece(); x = L1 / 2
    for (a, c) in ((-x + 0.15, -0.4), (x - 0.15, -0.4), (-x + 0.15, 0.4), (x - 0.15, 0.4)): disc_z(p, 'rubber', 0.08, c - 0.03, c + 0.03, a, 0.08, 12)
    p.cham('steel_d', -x, x, 0.16, 0.24, -0.5, 0.5, 0.01); seg_cyl(p, 'steel_d', (-x, 0.24, -0.3), (-x - 0.4, 0.9, -0.3), 0.02, 6); seg_cyl(p, 'steel_d', (-x, 0.24, 0.3), (-x - 0.4, 0.9, 0.3), 0.02, 6)
    seg_cyl(p, 'rubber', (-x - 0.4, 0.9, -0.32), (-x - 0.4, 0.9, 0.32), 0.025, 6)
    for j in range(layers):
        for i in range(6): z0 = -0.45 + i * 0.152; p.box('lumber', -x + 0.05, x - 0.05, 0.24 + j * 0.052, 0.29 + j * 0.052, z0, z0 + 0.145)
    return p
def lumber_stack(L1=3.6, layers=9, n=7, seed=1):
    """Pilha de tabuas tabicada: camadas de tabuas com frestas separadas por tabiques, apoiada em barrotes (pivo: centro, chao; ao longo de X)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(seed); w = n * 0.165
    for xx in np.linspace(-x + 0.2, x - 0.2, 4): p.box('dkwood', xx - 0.05, xx + 0.05, 0.0, 0.1, -w / 2 - 0.05, w / 2 + 0.05)
    y = 0.1
    for j in range(layers):
        for i in range(n):
            z0 = -w / 2 + i * 0.165 + 0.01; d = rng.uniform(-0.04, 0.04); p.box('lumber', -x + d, x + d * 0.5, y, y + 0.05, z0, z0 + 0.145)
        y += 0.05
        if j < layers - 1:
            for xx in np.linspace(-x + 0.2, x - 0.2, 4): p.box('dkwood', xx - 0.02, xx + 0.02, y, y + 0.025, -w / 2, w / 2)
            y += 0.025
    return p
def pallet_stack(seed=2):
    """Palete com um fardo de tabuas cintado (pivo: centro, chao)."""
    p = Piece()
    for z in (-0.45, 0.0, 0.45):
        for x in (-0.55, 0.0, 0.55): p.box('wood', x - 0.07, x + 0.07, 0.0, 0.1, z - 0.07, z + 0.07)
        p.box('wood', -0.6, 0.6, 0.1, 0.122, z - 0.05, z + 0.05)
    for k in range(7): z = -0.48 + k * 0.16; p.box('wood', -0.6, 0.6, 0.122, 0.142, z - 0.06, z + 0.06)
    q = lumber_stack(1.1, 5, 6, seed); p.merge(q, tr(0, 0.142, 0) @ rot_y(90))
    for x in (-0.3, 0.3):
        y1 = 0.242 + 5 * 0.05 + 4 * 0.025
        p.box('steel_d', x - 0.015, x + 0.015, y1, y1 + 0.004, -0.52, 0.52)
        for s in (-1, 1): a, b = sorted((s * 0.5, s * 0.504)); p.box('steel_d', x - 0.015, x + 0.015, 0.142, y1 + 0.004, a, b)
    return p
def log_pile(rows=5, L1=6.0, seed=3):
    """Pilha de toras em triangulo (pivo: centro, chao; toras ao longo de X)."""
    p = Piece(); rng = np.random.default_rng(seed); r0 = 0.3; dz = 2 * r0 + 0.02
    for j in range(rows):
        n = rows - j
        for i in range(n):
            z = (i - (n - 1) / 2) * dz; y = r0 + j * dz * 0.87; r = r0 - rng.uniform(0.0, 0.05); s = rng.uniform(-0.25, 0.25)
            log(p, -L1 / 2 + s, L1 / 2 + s, y, z, r)
    for s in (-1, 1): p.box('post', -0.1 + s * 1.8, 0.1 + s * 1.8, 0.0, 0.6, *sorted((s * ((rows - 1) / 2 * dz + r0 + 0.02), s * ((rows - 1) / 2 * dz + r0 + 0.22))))
    return p
def sawdust_pile(r=1.8, h=1.1, seed=4):
    p = Piece(); rng = np.random.default_rng(seed); pts = [(0, h, 0)]
    for k in range(18):
        a = k * 2 * math.pi / 18; rr = r * rng.uniform(0.85, 1.1); pts.append((rr * math.cos(a), 0.0, rr * math.sin(a)))
        rr2 = rr * 0.55; pts.append((rr2 * math.cos(a + 0.1), h * rng.uniform(0.55, 0.75), rr2 * math.sin(a + 0.1)))
    p.hull('sawdust', pts); return p

# ============================================================================ veiculos (pivo: chao; frente +Z)
def wheel(p, x0, x1, y, z, r=0.5, hub='steel'):
    disc_x(p, 'rubber', r, x0, x1, y, z, 20)
    s = 1 if x1 > 0 else -1; xo = x1 if s > 0 else x0
    disc_x(p, hub, r * 0.55, *sorted((xo, xo + s * 0.012)), y, z, 16); disc_x(p, 'steel_d', r * 0.2, *sorted((xo + s * 0.012, xo + s * 0.05)), y, z, 10)
def log_truck():
    """Caminhao de toras: cavalo de capo vermelho com grade cromada, farois, para-lamas, cabine com vidros, escapamento, tanques,
    eixo dianteiro e 2 eixos de tras com rodado duplo, protecao de cabine, 2 fueiros com estacas e 7 toras."""
    p = Piece(); hw = 1.25
    for x in (-0.45, 0.45): p.box('steel_d', x - 0.08, x + 0.08, 0.75, 1.0, -5.4, 4.1)
    for (z, dual) in ((3.3, False), (-3.1, True), (-4.45, True)):
        for s in (-1, 1):
            if dual: wheel(p, *sorted((s * 0.62, s * 0.92)), 0.5, z, 0.5); wheel(p, *sorted((s * 0.94, s * 1.22)), 0.5, z, 0.5)
            else: wheel(p, *sorted((s * 0.88, s * 1.2)), 0.5, z, 0.5)
        seg_cyl(p, 'steel_d', (-0.9, 0.5, z), (0.9, 0.5, z), 0.07, 8)
    p.cham('truck_r', -0.62, 0.62, 1.0, 1.9, 2.3, 4.0, 0.06)
    p.hull('truck_r', [(x, y, z) for x in (-0.62, 0.62) for (y, z) in ((1.9, 2.3), (1.9, 3.95), (1.98, 2.5), (1.95, 3.8))])
    p.box('chrome', -0.55, 0.55, 1.08, 1.85, 4.0, 4.03)
    for k in range(9): y = 1.14 + k * 0.08; p.box('dark', -0.5, 0.5, y, y + 0.035, 4.03, 4.035)
    p.cham('chrome', -1.2, 1.2, 0.7, 0.95, 4.05, 4.25, 0.03)
    for s in (-1, 1):
        disc_z(p, 'chrome', 0.13, 3.98, 4.08, s * 0.85, 1.55, 16); disc_z(p, 'lamp_glass', 0.1, 4.08, 4.09, s * 0.85, 1.55, 16)
        p.hull('truck_r', [(s * x, y, z) for x in (0.62, 1.24) for (y, z) in ((1.0, 2.6), (1.0, 4.0), (1.15, 2.8), (1.15, 3.8))])
        p.box('rubber', *sorted((s * 0.62, s * 1.24)), 0.98, 1.0, 2.7, 3.9)
        for z0 in (2.5, -1.9): p.cham('chrome', *sorted((s * 0.62, s * 1.0)), 0.95, 1.0, z0 - 0.0, z0 + 0.25, 0.005) if False else None
        disc_z(p, 'chrome', 0.26, 0.6, 1.7, s * 1.05, 0.85, 16) if False else None
        m = trimesh.creation.cylinder(radius=0.26, height=1.1, sections=16); m.apply_translation([s * 0.85, 0.85, 1.25]); p.add('chrome', m)
        p.box('rubber', *sorted((s * 0.62, s * 1.2)), 0.25, 0.85, -5.0, -4.98)
    p.cham('truck_r', -hw + 0.1, hw - 0.1, 1.0, 2.85, 0.9, 2.35, 0.05)
    p.box('glass', -hw + 0.22, hw - 0.22, 2.0, 2.7, 2.35, 2.36)
    for s in (-1, 1): p.box('glass', *sorted((s * (hw - 0.1), s * (hw - 0.09))), 1.95, 2.65, 1.5, 2.2); p.box('dark', *sorted((s * (hw - 0.1), s * (hw - 0.09))), 1.88, 1.92, 1.5, 2.2)
    p.box('glass', -0.8, 0.8, 2.1, 2.6, 0.89, 0.9)
    p.cham('truck_r', -0.6, 0.6, 2.85, 2.95, 1.2, 2.0, 0.02)
    for s in (-1, 1):
        seg_cyl(p, 'chrome', (s * 1.0, 1.1, 0.75), (s * 1.0, 3.7, 0.75), 0.07, 12); p.cyl('chrome', 0.08, 3.65, 3.75, s * 1.0, 0.75, 12)
        seg_cyl(p, 'chrome', (s * 1.18, 2.4, 2.38), (s * 1.42, 2.3, 2.5), 0.012, 4); p.box('dark', *sorted((s * 1.42, s * 1.46)), 2.0, 2.45, 2.42, 2.58)
    for x in np.linspace(-1.1, 1.1, 7): seg_cyl(p, 'steel_d', (x, 1.0, 0.65), (x, 3.0, 0.65), 0.025, 6)
    for y in (1.5, 2.2, 3.0): seg_cyl(p, 'steel_d', (-1.15, y, 0.65), (1.15, y, 0.65), 0.03, 6)
    for z in (0.0, -4.0):
        p.cham('steel_d', -hw, hw, 1.0, 1.15, z - 0.12, z + 0.12, 0.01)
        for s in (-1, 1): p.box('steel_d', *sorted((s * hw, s * (hw - 0.1))), 1.15, 2.8, z - 0.05, z + 0.05)
    rng = np.random.default_rng(9)
    for (x, y) in ((-0.86, 1.45), (-0.29, 1.45), (0.29, 1.45), (0.86, 1.45), (-0.57, 1.97), (0.0, 1.97), (0.57, 1.97)):
        r = 0.29 - rng.uniform(0, 0.03); s = rng.uniform(-0.2, 0.2); log(p, -5.6 + s, 0.45 + s, y, x, r, along='z')
    return p
def loader():
    """Carregadeira de toras amarela: chassi articulado, 4 pneus grandes, motor com grade, cabine de grades com teto, bracos e garra
    segurando uma tora (pivo: centro, chao; frente +Z)."""
    p = Piece()
    for z in (1.1, -1.1):
        for s in (-1, 1): wheel(p, *sorted((s * 0.85, s * 1.4)), 0.65, z, 0.65, 'yellow')
    p.cham('yellow', -0.8, 0.8, 0.6, 1.4, 0.2, 1.9, 0.04); p.cham('yellow', -0.85, 0.85, 0.6, 1.7, -2.0, 0.1, 0.04)
    p.cham('steel_d', -0.3, 0.3, 0.7, 1.2, 0.05, 0.3, 0.02)
    for k in range(6): p.box('dark', -0.7, 0.7, 0.85 + k * 0.12, 0.9 + k * 0.12, -2.005, -2.0)
    for x in (-0.75, 0.75):
        for z in (-0.9, 0.0): p.box('steel_d', x - 0.04, x + 0.04, 1.7, 3.0, z - 0.04, z + 0.04)
    p.cham('yellow', -0.85, 0.85, 3.0, 3.1, -1.0, 0.1, 0.02); p.box('glass', -0.71, 0.71, 1.8, 2.9, 0.03, 0.04)
    p.cham('dark', -0.3, 0.3, 1.7, 2.3, -0.7, -0.2, 0.04); seg_cyl(p, 'iron', (0.6, 1.7, -1.6), (0.6, 2.9, -1.6), 0.06, 10)
    for x in (-0.5, 0.5):
        seg_cyl(p, 'yellow', (x, 1.1, 0.8), (x, 2.4, 2.4), 0.11, 10); seg_cyl(p, 'yellow', (x, 2.4, 2.4), (x, 1.7, 3.2), 0.1, 10)
    seg_cyl(p, 'steel_d', (-0.6, 1.7, 3.2), (0.6, 1.7, 3.2), 0.08, 10)
    for x in (-0.45, 0.45):
        for s in (-1, 1):
            pts = [(x, 1.7, 3.2), (x, 1.5, 3.2 + s * 0.4), (x, 1.05, 3.2 + s * 0.45), (x, 0.75, 3.2 + s * 0.2)]
            for i in range(3): seg_cyl(p, 'steel_d', pts[i], pts[i + 1], 0.05, 6)
    log(p, -3.0, 3.0, 1.2, 3.2, 0.3)
    return p

# ============================================================================ escritorio, patio e vegetacao
def wood_stove():
    """Fogao a lenha de ferro: corpo, pes, porta com visor aceso, gaveta de cinzas, colarinho e cano ate o forro (pivo: centro, chao)."""
    p = Piece(); p.box('steel', -0.55, 0.55, 0.0, 0.01, -0.55, 0.65)
    for (x, z) in ((-0.25, -0.2), (0.25, -0.2), (-0.25, 0.2), (0.25, 0.2)): p.box('iron', x - 0.03, x + 0.03, 0.01, 0.18, z - 0.03, z + 0.03)
    p.cham('iron', -0.3, 0.3, 0.18, 0.75, -0.25, 0.25, 0.02); p.cham('iron', -0.32, 0.32, 0.75, 0.79, -0.27, 0.27, 0.01)
    p.box('iron', -0.2, 0.2, 0.32, 0.65, 0.25, 0.27); p.box('lamp_glass', -0.12, 0.12, 0.4, 0.58, 0.27, 0.272)
    p.box('iron', -0.15, 0.15, 0.2, 0.28, 0.25, 0.27); seg_cyl(p, 'chrome', (0.16, 0.5, 0.27), (0.16, 0.5, 0.33), 0.012, 6)
    p.cyl('iron', 0.1, 0.79, 0.9, 0, 0, 14); p.cyl('iron', 0.08, 0.9, 2.6, 0, 0, 14)
    for k in range(4): p.box('dkwood', -0.5 + k * 0.08, -0.43 + k * 0.08, 0.01, 0.08, 0.35, 0.6) if False else log(p, 0.36, 0.6, 0.06 + (k // 2) * 0.1, -0.44 + (k % 2) * 0.11, 0.05) if False else None
    return p
def pine(h=8.0, r=1.8, seed=1):
    """Pinheiro: tronco e 5 saias de galhos em cone (pivo: centro, chao)."""
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.2, -0.15), (0.15, 1.0), (0.06, h * 0.85)], sec=10)
    for k in range(5):
        y0 = h * (0.18 + k * 0.15); rr = r * (1.0 - k * 0.17); ht = h * 0.3
        lathe(p, 'pine' if k % 2 == 0 else 'pine2', [(rr, y0), (rr * 0.85, y0 + 0.12), (0.0, y0 + ht)], 0.0, 0.0, 0.0, 12)
    return p
FX0, FX1, FZ0, FZ1 = SX0 + 0.5, SX1 - 0.5, SZ0 + 0.5, SZ1 - 0.5
GATE = (2.0, 11.0)
def fence():
    """Cerca de mourao e 3 travessas em volta do terreno, com porteira de 2 folhas aberta para fora na frente (pivo: origem)."""
    p = Piece()
    def run(a, b):
        a = np.array(a, float); b = np.array(b, float); Ln = np.linalg.norm(b - a); n = max(1, int(round(Ln / 2.4)))
        for i in range(n + 1):
            q = a + (b - a) * i / n; p.cham('post', q[0] - 0.07, q[0] + 0.07, 0.0, 1.35, q[1] - 0.07, q[1] + 0.07, 0.015)
        for y in (0.35, 0.75, 1.15):
            d = (b - a) / Ln; nrm = np.array([-d[1], d[0]]) * 0.09
            p.seg('wood', (a[0] + nrm[0], y, a[1] + nrm[1]), (b[0] + nrm[0], y, b[1] + nrm[1]), 0.12, 0.04) if False else \
                p.seg('wood', (a[0] + nrm[0], y, a[1] + nrm[1]), (b[0] + nrm[0], y, b[1] + nrm[1]), 0.04, 0.12)
    run((FX0, FZ0), (FX1, FZ0)); run((FX0, FZ0), (FX0, FZ1)); run((FX1, FZ0), (FX1, FZ1))
    run((FX0, FZ1), (GATE[0], FZ1)); run((GATE[1], FZ1), (FX1, FZ1))
    for x in GATE: p.cham('post', x - 0.12, x + 0.12, 0.0, 1.8, FZ1 - 0.12, FZ1 + 0.12, 0.02)
    for (x0, s) in ((GATE[0], -1), (GATE[1], 1)):
        z = FZ1 + 0.25; xa, xb = sorted((x0 + s * 0.15, x0 + s * 4.4))
        for y in (0.3, 0.7, 1.1, 1.4): p.box('wood', xa, xb, y, y + 0.1, z - 0.03, z + 0.03)
        for xx in (xa, xb - 0.1, (xa + xb) / 2): p.box('wood', xx, xx + 0.1, 0.3, 1.5, z - 0.05, z - 0.03) if False else p.box('wood', xx, xx + 0.1, 0.3, 1.5, z + 0.03, z + 0.07)
        p.seg('wood', (xa + 0.1, 0.4, z + 0.05), (xb - 0.1, 1.4, z + 0.05), 0.1, 0.04)
        seg_cyl(p, 'iron', (x0, 0.5, FZ1 + 0.12), (x0, 0.5, z), 0.02, 6); seg_cyl(p, 'iron', (x0, 1.3, FZ1 + 0.12), (x0, 1.3, z), 0.02, 6)
    return p
def yard_light():
    """Poste de madeira com cruzeta, isoladores e luminaria de braco (pivo: centro, chao)."""
    p = Piece(); lathe(p, 'post', [(0.16, -0.3), (0.12, 8.0)], sec=12)
    p.box('post', -0.9, 0.9, 7.4, 7.55, -0.06, 0.06)
    for x in (-0.75, 0.75, 0.0): p.cyl('glass', 0.04, 7.55, 7.68, x, 0.0, 8)
    seg_cyl(p, 'steel', (0.0, 6.2, 0.12), (0.0, 6.5, 1.4), 0.03, 6)
    p.hull('metal', [(x, y, z) for x in (-0.15, 0.15) for (y, z) in ((6.42, 1.2), (6.52, 1.2), (6.4, 1.9), (6.5, 1.85))]); p.box('lamp_glass', -0.1, 0.1, 6.395, 6.405, 1.3, 1.8)
    p.cham('steel_d', -0.18, 0.18, 6.6, 7.0, 0.12, 0.42, 0.02)
    return p

# ============================================================================ terreno (pivo: origem)
SITE = sbox(SX0, SZ0, SX1, SZ1)
APRON = sbox(MX0 - 0.3, MZ1, MX1 + 0.3, MZ1 + 1.6)
STOOP = sbox(12.35, OZ1, 13.65, OZ1 + 0.8)
SHED = sbox(SHX0 - 0.4, SHZ0 - 0.4, SHX1 + 0.4, SHZ1 + 0.4)
BURN = Point(BUR_X, BUR_Z).buffer(BUR_R0 + 0.32 + 0.0, 40)
CUT = unary_union([MB, OB, STOOP, SHED, BURN, APRON])
GRASS = SITE.difference(sbox(SX0 + 0.9, SZ0 + 0.9, SX1 - 0.9, SZ1 - 0.9)).difference(sbox(GATE[0], SZ1 - 1.0, GATE[1], SZ1))
GRAVEL = unary_union([sbox(GATE[0], 4.0, GATE[1], SZ1), sbox(2.4, -3.0, 14.0, 4.0), sbox(14.0, -13.0, 20.6, 4.0)]).difference(CUT).difference(GRASS).buffer(0)
DIRT = SITE.difference(GRASS).difference(GRAVEL).difference(CUT).buffer(0)
def site():
    """Patio de terra batida, cascalho na entrada, no patio da frente e no lugar do caminhao, calcada de concreto na frente do galpao
    da serra, gramado em volta da cerca e manchas de serragem."""
    p = Piece()
    ext_y(p, 'dirt', DIRT, GY, 0.0); ext_y(p, 'gravel', GRAVEL, GY, 0.04); ext_y(p, 'grass', GRASS, GY, 0.06)
    ext_y(p, 'concrete', APRON, GY, Y0)
    for x in np.arange(MX0 + 2.0, MX1, 2.0): p.box('dark', x - 0.006, x + 0.006, Y0, Y0 + 0.001, MZ1, MZ1 + 1.6)
    for (x, z, r) in ((-6.5, -1.5, 1.6), (-13.5, -7.0, 1.4), (4.0, -10.6, 1.2)):
        q = Point(x, z).buffer(r, 20).intersection(DIRT); ext_y(p, 'sawdust', q, 0.0, 0.012)
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
def wm(kind, tl=0.0, tr_=0.0, H=ME):
    n = ('m_' if H == ME else 'o_') + kind + ('_l' if tl else '') + ('_r' if tr_ else '')
    if n not in pieces: pieces[n] = w_mod(kind, tl, tr_, H)
    return n
pieces.update({
    'm_roof': m_roof(), 'm_floor': m_floor(), 'o_roof': o_roof(), 'o_floor': o_floor(), 'burner': burner(), 'conveyor': conveyor(),
    'lumber_shed': lumber_shed(), 'band_saw': band_saw(), 'carriage': carriage(), 'roller_table': roller_table(4.0), 'edger': edger(),
    'lumber_cart': lumber_cart(), 'stack_a': lumber_stack(3.6, 9, 7, 1), 'stack_b': lumber_stack(3.6, 6, 7, 2), 'pallet_stack': pallet_stack(),
    'log_pile': log_pile(5, 6.0, 3), 'log_pile_b': log_pile(4, 5.0, 5), 'sawdust_pile': sawdust_pile(), 'log_truck': log_truck(), 'loader': loader(),
    'workbench': workbench(2.0), 'drum': drum('drum_b'), 'fl_light': fl_light(), 'desk': desk(), 'office_chair': office_chair('vinyl'),
    'guest_chair': guest_chair('vinyl'), 'file_cab': file_cab(), 'wood_stove': wood_stove(), 'pine': pine(8.5, 1.9, 1), 'pine_b': pine(6.5, 1.5, 2),
    'fence': fence(), 'yard_light': yard_light(), 'site': site(),
    'door_plank': door_plank(0.94, 2.26), 'door_back': door_back(0.94, 2.26), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
y = Y0; M = ['serraria']; O = ['escritorio']
for x, k in ((-11, 'plain'), (-8, 'bay'), (-5, 'plain'), (-3, 'plain'), (-1, 'win')): put(wm(k), x, y, MZ1, 0, M + ['ext', 'front'])
for x, k in zip(range(-11, 0, 2), ['win', 'plain', 'win', 'plain', 'win', 'plain']): put(wm(k), x, y, MZ0, 180, M + ['ext'])
for z, k in zip((-13, -11, -9, -7, -5), ['plain', 'win', 'plain', 'win', 'plain']): put(wm(k, T if z == -13 else 0.0, T if z == -5 else 0.0), MX0, y, z, -90, M + ['ext'])
for z, k in zip((-13, -11, -9, -7, -5), ['plain', 'win', 'chute', 'door', 'plain']): put(wm(k, T if z == -5 else 0.0, T if z == -13 else 0.0), MX1, y, z, 90, M + ['ext'])
put('m_roof', 0, y, 0, 0, M + ['roof']); put('m_floor', 0, y, 0, 0, M)
hx, hz = hinge(MX1, -7.0, 90, -0.47, -0.125); put('door_plank', hx, y + 0.005, hz, 90, M, door=90)
put('band_saw', -6.0, y, -10.75, 0, M); put('carriage', -7.0, y, -10.0, 0, M); put('roller_table', -4.75, y, -12.6, 0, M); put('edger', -1.4, y, -12.6, 0, M)
put('lumber_cart', -10.5, y, -5.6, 0, M); put('lumber_cart', -3.2, y, -5.5, 0, M); put('workbench', -9.0, y, MZ0 + T, 0, M)
for (x, z) in ((-11.3, -12.9), (-11.3, -12.25)): put('drum', x, y, z, 0, M)
for x in (-10.0, -6.0, -2.0):
    for z in (-11.0, -7.0): put('fl_light', x, y + ME - 0.22, z, 0, M + ['roof'])
# escritorio
for x, k in ((13, 'door'), (15, 'win')): put(wm(k, H=OE), x, y, OZ1, 0, O + ['ext', 'front'])
for x, k in ((13, 'win'), (15, 'plain')): put(wm(k, H=OE), x, y, OZ0, 180, O + ['ext'])
put(wm('win', T, 0.0, OE), OX0, y, 7, -90, O + ['ext']); put(wm('plain', 0.0, T, OE), OX0, y, 9, -90, O + ['ext'])
put(wm('win', T, 0.0, OE), OX1, y, 9, 90, O + ['ext']); put(wm('plain', 0.0, T, OE), OX1, y, 7, 90, O + ['ext'])
put('o_roof', 0, y, 0, 0, O + ['roof']); put('o_floor', 0, y, 0, 0, O)
hx, hz = hinge(13.0, OZ1, 0, -0.47, -0.125); put('door_back', hx, y + 0.005, hz, 0, O, door=90)
put('desk', 13.2, y, 7.4, 0, O); put('office_chair', 13.2, y, 6.75, 0, O); put('guest_chair', 14.4, y, 8.4, 210, O)
put('wood_stove', 15.0, y, 7.0, 0, O); put('file_cab', OX0 + T, y, 8.8, 90, O)
# patio
st = ['patio']
put('site', 0, 0, 0, 0, st); put('fence', 0, 0, 0, 0, st); put('lumber_shed', 0, 0, 0, 0, st + ['roof'])
put('burner', 0, 0, 0, 0, st); put('conveyor', 0, 0, 0, 0, st)
for (x, z, n) in ((-12.0, 3.6, 'stack_a'), (-12.0, 6.0, 'stack_b'), (-12.0, 8.4, 'stack_a'), (-4.0, 3.6, 'stack_b'), (-4.0, 6.0, 'stack_a'), (0.0, 8.4, 'stack_a'),
                  (0.0, 3.6, 'stack_a'), (-4.0, 8.4, 'stack_b')):
    put(n, x, Y0, z, 0, st)
put('log_pile', -18.5, 0, -12.0, 0, st); put('log_pile_b', -18.5, 0, -4.5, 0, st); put('loader', -15.0, 0, -8.3, -80, st)
put('log_truck', 17.5, 0, -6.5, 0, st)
for (x, z) in ((8.5, 12.4), (10.0, 12.4), (8.5, 14.1)): put('pallet_stack', x, 0.04, z, 0, st)
put('sawdust_pile', 5.2, 0, -12.8, 0, st); put('sawdust_pile', -15.5, 0, 0.4, 40, st)
for (x, z) in ((1.0, -12.6), (1.0, -13.3)): put('drum', x, 0, z, 0, st)
put('yard_light', 5.8, 0.04, 1.5, 0, st + ['roof'])
for k, (x, z) in enumerate(((-22.0, -16.0), (-18.0, -16.6), (-8.0, -16.6), (-2.5, -16.5), (3.0, -16.4), (14.0, -16.5), (21.5, -16.0), (22.2, -8.0),
                            (22.2, 4.0), (22.2, 12.0), (-22.2, 8.0), (-22.2, 14.0), (-22.0, 1.5))):
    put('pine' if k % 2 == 0 else 'pine_b', x, 0.0, z, 0, st + ['roof'])
put('player_scale_ref', -8.0, Y0, -3.0, 0, st); put('player_scale_ref', 13.8, Y0, 8.6, 0, O)


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_level': Y0, 'yard_level': 0.0,
                       'mill': {'x': [MX0, MX1], 'z': [MZ0, MZ1], 'eave': ME, 'pitch_deg': math.degrees(MPITCH)},
                       'burner': {'center': [BUR_X, BUR_Z], 'base_radius': BUR_R0, 'top_radius': BUR_R1, 'height': BUR_H},
                       'lumber_shed': {'x': [SHX0, SHX1], 'z': [SHZ0, SHZ1], 'eave': SHE, 'ridge': SHR},
                       'office': {'x': [OX0, OX1], 'z': [OZ0, OZ1], 'eave': OE},
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
