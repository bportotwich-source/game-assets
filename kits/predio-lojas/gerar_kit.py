"""Kit 60: predio de apartamentos com lojas (walk-up de 6 pavimentos), em ALTO DETALHE (scripts/detalhe).
Predio de esquina de 24 x 12 m e 6 pavimentos de 3,0 m: fachadas de tijolo vermelho com vergas de pedra com fecho, peitoris
de pedra, faixas de pedra, grande cornija de chapa com misulas e friso; 2 escadas de incendio de aco na frente (plataformas com
alcapao, lances em zigue-zague, escada de descida e escada de gancho ate o telhado). Terreo com mercearia e lavanderia
(vitrines com bandeira, toldos listrados, forro de chapa estampada), hall com caixas de correio e escada em U ate o telhado.
5 andares com 2 apartamentos cada (10 no total): sala, cozinha com copa, 2 quartos, banheiro com banheira de pes, closet,
piso de taco e radiadores. Telhado plano com casa de escada, caixa-d'agua de madeira sobre torre de aco, chamine e respiros.
Calcadas de esquina, rua, hidrante, semaforo, carros genericos. Arte original, sem texto (so pictogramas).
Y para cima, 1 unidade = 1 m. Padrao: PADRAO_METRICAS.md.
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
CAR_COLS = {'car_r': (150, 56, 52), 'car_b': (60, 92, 140), 'car_g': (90, 116, 92), 'car_y': (200, 172, 92), 'car_w': (226, 224, 216), 'car_s': (168, 172, 176),
            'car_k': (46, 48, 52), 'car_t': (96, 140, 138)}
configurar(cores=dict({'siding': (224, 208, 178), 'wrap': (200, 190, 170), 'trim': (244, 242, 236), 'frame': (244, 242, 236), 'sash': (248, 248, 244),
                       'shingles': (104, 80, 66), 'shingle_c': (92, 70, 58), 'gutter': (240, 238, 232), 'plaster': (238, 234, 226), 'ceil': (244, 242, 236),
                       'carpet': (176, 164, 146), 'carpet2': (150, 150, 140), 'vinyl_f': (206, 196, 176), 'tile_f': (214, 210, 200), 'tile_w': (232, 234, 232),
                       'deck': (150, 132, 112), 'concrete': (190, 186, 178), 'conc_s': (176, 172, 164), 'asphalt': (72, 74, 76), 'curb': (200, 198, 192),
                       'grass': (110, 148, 72), 'mulch': (104, 78, 58), 'hedge': (70, 112, 58), 'stone': (190, 180, 160), 'coping': (214, 208, 194),
                       'alu': (196, 200, 204), 'alu_d': (90, 96, 102), 'metal': (176, 180, 184), 'chrome': (212, 216, 220), 'steel': (120, 126, 132), 'steel_d': (56, 60, 64),
                       'iron': (40, 42, 44), 'galv': (168, 174, 176), 'glass': (150, 186, 204), 'mirror': (200, 214, 220), 'lamp_glass': (255, 238, 196),
                       'paint_w': (240, 240, 234), 'paint_y': (236, 196, 50), 'blue': (40, 92, 160), 'line_w': (236, 236, 230), 'line_y': (226, 190, 70),
                       'door': (64, 82, 92), 'door_int': (240, 238, 230), 'door_m': (180, 186, 190), 'wood': (176, 132, 88), 'dkwood': (110, 78, 54), 'laminate': (200, 170, 130),
                       'cab': (238, 236, 228), 'ctop': (120, 110, 100), 'counter': (226, 222, 212), 'porcelain': (244, 244, 240), 'appl': (226, 228, 228), 'appl_d': (40, 42, 44),
                       'dark': (34, 34, 36), 'rubber': (30, 30, 32), 'vinyl': (60, 70, 80), 'fabric2': (90, 110, 130), 'fabric_g': (110, 120, 104), 'fabric_t': (166, 120, 90),
                       'bed_w': (244, 244, 240), 'bed_b': (120, 140, 170), 'bed_g': (150, 170, 140), 'curtain': (200, 190, 160), 'screen': (30, 34, 38), 'paper': (236, 232, 220),
                       'leaf': (86, 128, 62), 'leaf2': (108, 150, 70), 'bark': (120, 96, 72), 'plant': (70, 120, 60), 'pot': (190, 110, 80), 'brass': (196, 164, 90),
                       'player': (90, 140, 220), 'mail': (190, 180, 150), 'dumpster': (40, 90, 70), 'rug': (150, 80, 70), 'book': (120, 60, 50), 'book2': (60, 90, 120),
                       'cushion': (200, 150, 70), 'flag_o': (230, 140, 50), 'flag_r': (180, 50, 50), 'flag_b': (40, 60, 120), 'neon_r': (220, 60, 50), 'food_g': (90, 140, 60), 'food_r': (190, 60, 50), 'food_y': (230, 190, 70), 'basket': (150, 110, 70), 'cream': (240, 232, 214), 'terrazzo': (204, 198, 188), 'bench_g': (60, 100, 70), 'cart_w': (200, 200, 196), 'screen_g': (60, 200, 120), 'grille': (60, 62, 64), 'brick': (156, 68, 50), 'brick2': (128, 56, 44), 'stone_c': (214, 204, 182), 'cornice': (54, 88, 70), 'shop_f': (50, 78, 64), 'shop_f2': (92, 44, 40), 'tin': (236, 230, 212), 'wood_f': (168, 120, 78), 'roofing': (120, 120, 116), 'tank': (150, 108, 72), 'awn_r': (176, 52, 46), 'awn_g': (52, 110, 76), 'awn_w': (238, 234, 222), 'radiator': (222, 220, 212), 'hydrant': (196, 54, 44), 'signal': (230, 180, 40), 'sig_r': (230, 60, 40), 'sig_g': (60, 220, 120), 'tile_k': (40, 42, 44), 'tile_hex': (240, 240, 236), 'washer': (236, 238, 238), 'mailbox': (40, 70, 140), 'conc_r': (166, 162, 154)}, **CAR_COLS),
           texturas={'brick': 'brick', 'siding': 'paint', 'shingles': 'shingles', 'plaster': 'plaster', 'ceil': 'plaster', 'carpet': 'render', 'carpet2': 'render',
                     'concrete': 'render', 'conc_s': 'render', 'asphalt': 'render', 'curb': 'render', 'grass': 'render', 'mulch': 'render', 'stone': 'stone',
                     'deck': 'deck', 'wood': 'planks', 'dkwood': 'planks', 'laminate': 'planks', 'bark': 'render', 'vinyl_f': 'render', 'hedge': 'render', 'terrazzo': 'render', 'brick2': 'brick', 'stone_c': 'stone', 'wood_f': 'planks', 'roofing': 'render', 'tank': 'planks', 'conc_r': 'render'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu', 'alu_d'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4
for k in ('screen_g', 'sig_r', 'sig_g'): MATS[k].emissiveFactor = [c / 255 for c in D.COL[k]]

# ============================================================================ medidas (moldura do predio: x -12..12, z -6..6, frente +z)
W = 2.0; T = 0.3; TP = 0.12; TD = 0.2; t_ = 0.1; GY = -0.3
Y0 = 0.15; H = 3.0; ST = 0.2; NL = 6; CH = H - ST
LV = [Y0 + k * H for k in range(NL + 1)]                         # 0,15 ... 15,15 e 18,15 (telhado)
BX, BZ = 12.0, 6.0
FOOT = sbox(-BX, -BZ, BX, BZ)
HX = 2.0; HZ0 = 0.54                                              # hall da escada: x -2..2, z 0,54..6 (paredes de 0,2 m)
SNR = 16; SRR = H / SNR; STRD = 0.26                              # 16 espelhos de 0,1875 m, piso 0,26
ZF = 4.0; ZM = ZF - (SNR // 2 - 1) * STRD                         # borda do patamar do andar (4,0) e do patamar intermediario (2,18)
HZI = HZ0 + 0.1                                                   # face interna do fundo do hall (0,64)
DW = 0.9; DH = 2.1                                                # portas
UDOOR = (4.5, 5.4)                                                # porta do apartamento na parede x = 2 (em z)
ZB = 0.5                                                          # parede entre a frente (sala/cozinha) e os quartos
SX0, SX1, SZ0, SZ1 = -22.0, 32.0, -16.0, 24.0                     # terreno (esquina: rua na frente +z e a leste +x)
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
    p = Piece()
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
            p.box('chrome', b - 0.07, b - 0.04, (y0 + y1) / 2 - 0.05, (y0 + y1) / 2 + 0.05, 0.49, 0.51); p.box('brass', b - 0.065, b - 0.045, (y0 + y1) / 2 + 0.08, (y0 + y1) / 2 + 0.1, 0.49, 0.5)
    return p
def wall_clock(r=0.4):
    """Relogio de parede sem numeros (pivo: face da parede, centro): aro cromado, mostrador, marcas das horas e ponteiros."""
    p = Piece(); R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    for (rr, z0, z1, m) in ((r, 0.0, 0.06, 'chrome'), (r - 0.04, 0.06, 0.065, 'cream')):
        c = trimesh.creation.cylinder(radius=rr, height=z1 - z0, sections=28); c.apply_translation([0, 0, (z0 + z1) / 2]); p.add(m, c)
    for k in range(12):
        a = k * math.pi / 6; l = 0.07 if k % 3 == 0 else 0.04
        seg_cyl(p, 'dark', ((r - 0.06) * math.sin(a), (r - 0.06) * math.cos(a), 0.067), ((r - 0.06 - l) * math.sin(a), (r - 0.06 - l) * math.cos(a), 0.067), 0.008, 4)
    for (a, l, w_) in ((math.radians(300), r * 0.55, 0.012), (math.radians(60), r * 0.78, 0.008)): seg_cyl(p, 'dark', (0, 0, 0.072), (l * math.sin(a), l * math.cos(a), 0.072), w_, 4)
    p.sphere('dark', 0.02, 0, 0, 0.075, 0)
    return p
def stool():
    p = Piece(); p.cyl('chrome', 0.2, 0.0, 0.02, 0, 0, 16); seg_cyl(p, 'chrome', (0, 0.02, 0), (0, 0.66, 0), 0.03, 8)
    m = trimesh.creation.annulus(r_min=0.15, r_max=0.17, height=0.015, sections=20); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.3, 0]); p.cyl('chrome', 0.17, 0.3, 0.315, 0, 0, 20)
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
        for j in range(3): p.box('paper', -0.12 + i * 0.06, -0.08 + i * 0.06, 0.1 + (2 - j) * 0.02, 0.112 + (2 - j) * 0.02, 0.02 + j * 0.06, 0.06 + j * 0.06)
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
        for z in (0.02, 0.38): p.box('steel', *sorted((s * x, s * (x - 0.03))), 0.0, 1.9, z, z + 0.03)
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
        a = k * math.pi / 4; seg_cyl(p, 'iron', (0.062 * math.cos(a), 0.62, 0.062 * math.sin(a)), (0.05 * math.cos(a), h - 0.5, 0.05 * math.sin(a)), 0.018, 6)
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
            if z1 - z0 > 0.05: p.box('chrome', *sorted((s * (hw + 0.001), s * (hw + 0.007))), 0.6, 0.625, z0, z1)
        seams = [cf - 0.08, (cf + cr) / 2 + 0.1] + ([cr + 0.1] if kind in ('sedan', 'wagon') else [])
        for zz in seams:
            arch = abs(zz - wf) < ar + 0.02 or abs(zz - wr) < ar + 0.02
            if not arch: p.box('dark', *sorted((s * hw, s * (hw + 0.003))), yb + 0.06, 0.575, zz - 0.006, zz + 0.006)
            p.box('dark', *sorted((s * hw, s * (hw + 0.003))), 0.71 if arch else 0.65, yh - 0.02, zz - 0.006, zz + 0.006)
        for zz in seams[1:]:
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
# ============================================================================ utilitarios (paredes, janelas, portas)
def wall2(p, axis, u0, u1, vo, vi, holes, ya, yb, out='brick', inn='plaster', split=0.5):
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
def bx(p, mat, axis, u0, u1, y0, y1, v0, v1):
    """Caixa em coordenadas de parede (u ao longo, v na espessura)."""
    if axis == 'x': p.box(mat, u0, u1, y0, y1, *sorted((v0, v1)))
    else: p.box(mat, *sorted((v0, v1)), y0, y1, u0, u1)
def slider(p, a, b, ya, yb, z0=-0.17, f=0.045):
    """Janela de correr de aluminio: 2 folhas, trilhos, fecho e puxador (em coordenadas locais de fachada: x ao longo, z para fora)."""
    zf0, zf1 = z0, z0 + 0.09
    p.box('alu', a, a + f, ya, yb, zf0, zf1); p.box('alu', b - f, b, ya, yb, zf0, zf1)
    p.box('alu', a + f, b - f, yb - f, yb, zf0, zf1); p.box('alu', a + f, b - f, ya, ya + f, zf0, zf1)
    xm = (a + b) / 2; s = 0.035; ia, ib, ja, jb = a + f, b - f, ya + f, yb - f
    for (u, v, za, zb) in ((ia, xm + 0.02, zf1 - 0.035, zf1 - 0.012), (xm - 0.02, ib, zf0 + 0.012, zf0 + 0.035)):
        p.box('alu', u, u + s, ja, jb, za, zb); p.box('alu', v - s, v, ja, jb, za, zb)
        p.box('alu', u + s, v - s, jb - s, jb, za, zb); p.box('alu', u + s, v - s, ja, ja + s, za, zb)
        p.box('glass', u + s - 0.004, v - s + 0.004, ja + s - 0.004, jb - s + 0.004, (za + zb) / 2 - 0.002, (za + zb) / 2 + 0.002)
    ym = (ja + jb) / 2; p.box('chrome', xm - 0.04, xm - 0.016, ym - 0.05, ym + 0.05, zf0 - 0.002, zf0 + 0.012)
def hung(p, a, b, ya, yb, z0=-0.17, f=0.05):
    """Janela de aluminio de 2 folhas de guilhotina com bandeira fixa em cima (coordenadas de fachada)."""
    zf0, zf1 = z0, z0 + 0.1
    p.box('alu', a, a + f, ya, yb, zf0, zf1); p.box('alu', b - f, b, ya, yb, zf0, zf1)
    p.box('alu', a + f, b - f, yb - f, yb, zf0, zf1); p.box('alu', a + f, b - f, ya, ya + f, zf0, zf1)
    yt = ya + (yb - ya) * 0.72; p.box('alu', a + f, b - f, yt - 0.025, yt + 0.025, zf0, zf1)
    p.box('glass', a + f - 0.004, b - f + 0.004, yt + 0.021, yb - f + 0.004, z0 + 0.048, z0 + 0.052)
    ym = (ya + f + yt - 0.025) / 2; s = 0.04
    for (y0, y1, za, zb) in ((ya + f, ym + 0.02, zf0 + 0.06, zf0 + 0.088), (ym - 0.02, yt - 0.025, zf0 + 0.012, zf0 + 0.04)):
        p.box('alu', a + f, a + f + s, y0, y1, za, zb); p.box('alu', b - f - s, b - f, y0, y1, za, zb)
        p.box('alu', a + f + s, b - f - s, y1 - s, y1, za, zb); p.box('alu', a + f + s, b - f - s, y0, y0 + s, za, zb)
        p.box('glass', a + f + s - 0.004, b - f - s + 0.004, y0 + s - 0.004, y1 - s + 0.004, (za + zb) / 2 - 0.002, (za + zb) / 2 + 0.002)
    xm = (a + b) / 2; p.box('chrome', xm - 0.05, xm + 0.05, ym + 0.02, ym + 0.04, zf0 + 0.088, zf0 + 0.1)
    p.box('chrome', xm - 0.06, xm + 0.06, ya + f + 0.05, ya + f + 0.07, zf0 + 0.088, zf0 + 0.104)

# ============================================================================ montagem: lista de posicoes e portas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def l2w(frame, lx, lz):
    (fx, fz), fr = frame; a = math.radians(fr)
    return fx + math.cos(a) * lx + math.sin(a) * lz, fz - math.sin(a) * lx + math.cos(a) * lz
def put_f(frame, n, lx, ly, lz, lry=0.0, tags=(), door=None):
    x, z = l2w(frame, lx, lz); put(n, x, ly, z, frame[1] + lry, tags, door)
def door_at(n, axis, a, b, c, y, hinge, into, tags, gap=0.01):
    """Folha de porta no vao [a, b] de uma parede (eixo 'x' ou 'z', linha c), dobradica na ponta 'a' ou 'b', abrindo para o lado into (+1/-1)."""
    if axis == 'x':
        if hinge == 'a': put(n, a + gap, y, c, 0, tags, door=-90 * into)
        else: put(n, b - gap, y, c, 180, tags, door=90 * into)
    else:
        if hinge == 'a': put(n, c, y, a + gap, -90, tags, door=90 * into)
        else: put(n, c, y, b - gap, 90, tags, door=-90 * into)

# ============================================================================ quartos (retangulo interno no mundo + lado do corredor)
ROOMS = {'N1': (-13.7, -10.06, -5.7, -1.12, 'z1'), 'N2': (-9.94, -6.06, -5.7, -1.12, 'z1'), 'N3': (-5.94, -2.06, -5.7, -1.12, 'z1'), 'N4': (6.06, 9.7, -5.7, -1.12, 'z1'),
         'S1': (-13.7, -10.06, 1.12, 5.7, 'z0'), 'S2': (-9.94, -6.06, 1.12, 5.7, 'z0'), 'S3': (-5.94, -2.06, 1.12, 5.7, 'z0'), 'S4': (-1.94, 1.94, 1.12, 5.7, 'z0'),
         'W1': (0.3, 3.88, 5.82, 9.94, 'x1'), 'W2': (0.3, 3.88, 10.06, 13.94, 'x1'), 'W3': (0.3, 3.88, 14.06, 17.7, 'x1'),
         'E0': (6.12, 9.7, 1.12, 5.94, 'x0'), 'E1': (6.12, 9.7, 6.06, 9.94, 'x0'), 'E2': (6.12, 9.7, 10.06, 13.94, 'x0'), 'E3': (6.12, 9.7, 14.06, 17.7, 'x0')}
def ac_unit():
    """Condensadora de ar-condicionado (pivo: centro, chao): gabinete com aletas, 2 ventiladores com grade no topo, base e tubos."""
    p = Piece(); x, z = 1.1, 0.5
    for s in (-1, 1): p.box('steel_d', -x, x, 0.0, 0.12, s * (z - 0.08) - 0.05, s * (z - 0.08) + 0.05)
    p.cham('galv', -x, x, 0.12, 1.2, -z, z, 0.012)
    for y in np.arange(0.22, 1.12, 0.06):
        for s in (-1, 1): p.box('steel', -x + 0.06, x - 0.06, y, y + 0.02, *sorted((s * z, s * (z + 0.01))))
    for xc in (-0.52, 0.52):
        p.cyl('dark', 0.42, 1.2, 1.205, xc, 0.0, 24)
        ring_y(p, 'steel', 0.42, 0.45, 1.2, 1.24, xc, 0.0, 24)
        for k in range(7): yy = 1.24; seg_cyl(p, 'steel', (xc - 0.43, yy, -0.42 + k * 0.14), (xc + 0.43, yy, -0.42 + k * 0.14), 0.006, 4)
        p.cyl('steel_d', 0.08, 1.205, 1.23, xc, 0.0, 10)
        for k in range(4):
            a = k * math.pi / 2 + 0.4; p.hull('alu_d', [(xc + r * math.cos(a + da), yy + dy, r * math.sin(a + da)) for (r, da, yy) in ((0.06, 0.0, 1.21), (0.36, 0.3, 1.212), (0.36, -0.2, 1.218)) for dy in (0.0, 0.006)])
    for (y, r) in ((0.4, 0.02), (0.55, 0.012)): seg_cyl(p, 'brass', (x - 0.2, y, z), (x - 0.2, y, z + 0.35), r, 8); seg_cyl(p, 'brass', (x - 0.2, y, z + 0.35), (x - 0.2, 0.15, z + 0.35), r, 8)
    p.box('dark', -x + 0.1, -x + 0.4, 0.41, 0.76, z + 0.012, z + 0.03)
    return p
def lamp_pole(h=6.0):
    """Poste de iluminacao moderno: base de concreto, poste conico de aco, braco e luminaria de LED (pivo: centro, chao; luz para +Z)."""
    p = Piece(); p.cyl('concrete', 0.25, -0.05, 0.4, 0, 0, 16)
    lathe(p, 'steel_d', [(0.1, 0.4), (0.09, 0.5), (0.06, h)], sec=12)
    seg_cyl(p, 'steel_d', (0.0, h - 0.1, 0.0), (0.0, h - 0.05, 0.9), 0.04, 8)
    p.cham('steel_d', -0.18, 0.18, h - 0.12, h - 0.02, 0.8, 1.4, 0.02); p.box('lamp_glass', -0.15, 0.15, h - 0.125, h - 0.115, 0.85, 1.35)
    return p
def bollard():
    p = Piece(); p.cyl('steel_d', 0.1, 0.0, 0.9, 0, 0, 14); lathe(p, 'steel_d', [(0.1, 0.9), (0.07, 0.96), (0.0, 0.98)], sec=14)
    ring_y(p, 'paint_y', 0.1, 0.105, 0.7, 0.8, 0, 0, 14); return p
# ============================================================================ fachadas (envoltoria de um pavimento do predio)
# (nome, eixo, coordenada da face, sentido para fora, u0, u1)
FACS = [('S', 'x', BZ, 1, -BX, BX), ('N', 'x', -BZ, -1, -BX, BX), ('E', 'z', BX, 1, -BZ + T, BZ - T), ('W', 'z', -BX, -1, -BZ + T, BZ - T)]
WIN = (0.85, 2.3)                                                  # peitoril e verga das janelas
SHOP = (3.2, 11.2); SHOP_H = 2.6                                   # vitrine da loja da direita (a da esquerda e o espelho)
SHOP_D = (6.66, 7.74)                                              # porta da loja (vao com batentes)
HALL_DOOR = (-0.55, 0.55); HALL_H = 2.62                           # porta do hall com bandeira
RDOOR = [(6.0, 6.95), (-6.95, -6.0), (-0.45, 0.5)]                 # portas dos fundos: loja da direita, da esquerda e casa de maquinas
WIN_T = {'S': [(-0.6, 0.6, 1.0), (2.9, 3.9), (5.2, 6.2), (7.7, 8.7), (10.0, 11.0)],
         'N': [(1.5, 2.7), (5.25, 5.95, 1.5, 2.25), (8.8, 10.0)], 'EW': [(1.65, 2.65, 1.05), (-3.4, -2.2), (4.3, 5.3)]}
def _sym(lst):
    o = []
    for w in lst:
        a, b = w[:2]; ya = w[2] if len(w) > 2 else WIN[0]; yb = w[3] if len(w) > 3 else WIN[1]
        o.append((a, b, ya, yb, 'win'))
        if a > 0: o.append((-b, -a, ya, yb, 'win'))
    return o
def ops_of(f, kind):
    """Vaos da fachada em u: [(a, b, ya, yb, tipo)]. O lado esquerdo e o espelho do direito."""
    n = f[0]; o = []
    if kind == 't':
        if n == 'S': o = _sym(WIN_T['S'])
        if n == 'N': o = _sym(WIN_T['N'])
        if n in ('E', 'W'): o = [(w[0], w[1], w[2] if len(w) > 2 else WIN[0], WIN[1], 'win') for w in WIN_T['EW']]
        return o
    if n == 'S':
        o = [(SHOP[0], SHOP[1], 0.0, SHOP_H, 'shop'), (-SHOP[1], -SHOP[0], 0.0, SHOP_H, 'shop'), (HALL_DOOR[0], HALL_DOOR[1], 0.0, HALL_H, 'hdoor')]
    if n == 'N':
        o = [(a, b, 0.0, 2.15, 'rdoor') for (a, b) in RDOOR] + [(9.0, 10.2, 1.5, 2.2, 'winb'), (-10.2, -9.0, 1.5, 2.2, 'winb'), (2.5, 3.1, 1.6, 2.2, 'winb'), (-3.1, -2.5, 1.6, 2.2, 'winb')]
    if n in ('E', 'W'): o = [(0.6, 2.8, 0.5, 2.4, 'disp'), (3.3, 5.1, 0.5, 2.4, 'disp'), (-4.6, -3.6, 1.4, 2.2, 'winb')]
    return o
def fac_frame(f):
    """Moldura local da fachada (x ao longo, +z para fora, face em z = 0): (matriz, sinal de u -> x local)."""
    n, ax, c, s = f[:4]
    if ax == 'x': return (rot_y(0, (0, 0, c)), 1) if s > 0 else (rot_y(180, (0, 0, c)), -1)
    return (rot_y(90, (c, 0, 0)), -1) if s > 0 else (rot_y(-90, (c, 0, 0)), 1)
def int_casing(p, a, b, ya, yb, stool=True):
    """Guarnicao interna (face interna da parede em z = -T) e peitoril interno."""
    z0, z1 = -T - 0.014, -T
    for (u, v) in ((a - 0.07, a), (b, b + 0.07)): p.box('trim', u, v, (ya - 0.07) if stool else ya, yb + 0.07, z0, z1)
    p.box('trim', a - 0.07, b + 0.07, yb, yb + 0.07, z0 - 0.002, z1)
    if stool: p.box('trim', a - 0.1, b + 0.1, ya - 0.02, ya + 0.012, -T - 0.06, -T + 0.04); p.box('trim', a - 0.07, b + 0.07, ya - 0.1, ya - 0.02, z0, z1)
def stone_sill(p, a, b, ya):
    """Peitoril de pedra com caimento e pingadeira (sai 6 cm da face)."""
    prof_x(p, 'stone_c', a - 0.08, b + 0.08, [(-0.04, ya - 0.07), (0.05, ya - 0.07), (0.06, ya - 0.055), (0.062, ya - 0.02), (0.0, ya + 0.004), (-0.04, ya + 0.02)])
def stone_lintel(p, a, b, yb, key=True):
    """Verga de pedra plana com fecho saliente."""
    p.box('stone_c', a - 0.1, b + 0.1, yb, yb + 0.22, 0.0, 0.025)
    prof_x(p, 'stone_c', a - 0.12, b + 0.12, [(0.0, yb + 0.22), (0.045, yb + 0.22), (0.045, yb + 0.235), (0.03, yb + 0.255), (0.0, yb + 0.26)])
    if key:
        xm = (a + b) / 2
        p.hull('stone_c', [(x, y, z) for (x, y) in ((xm - 0.07, yb - 0.03), (xm + 0.07, yb - 0.03), (xm - 0.095, yb + 0.25), (xm + 0.095, yb + 0.25)) for z in (0.0, 0.045)])
def hung_window(p, a, b, ya, yb, lites=1):
    """Janela de guilhotina de madeira pintada no vao de tijolo: caixilho, 2 folhas, baguete e peitoril de pedra, verga com fecho."""
    x = (b - a) / 2; xm = (a + b) / 2; f = 0.05; q = Piece()
    q.box('frame', -x, -x + f, ya, yb, -0.2, -0.05); q.box('frame', x - f, x, ya, yb, -0.2, -0.05); q.box('frame', -x + f, x - f, yb - f, yb, -0.2, -0.05)
    q.box('frame', -x + f, x - f, ya, ya + 0.02, -0.2, -0.05)
    mid = ya + 0.02 + (yb - f - ya - 0.02) * 0.5
    sash(q, -x + f, x - f, ya + 0.025, mid + 0.02, -0.16, -0.12, 1, 0.075)
    sash(q, -x + f + 0.008, x - f - 0.008, mid - 0.02, yb - f, -0.1, -0.06, lites, 0.05)
    q.box('chrome', -0.04, 0.04, mid + 0.015, mid + 0.03, -0.13, -0.115)
    p.merge(q, tr(xm, 0, 0)); stone_sill(p, a, b, ya); stone_lintel(p, a, b, yb)
def barred_window(p, a, b, ya, yb):
    """Janela basculante pequena com grade de ferro por fora (fundos e depositos)."""
    f = 0.05; p.box('frame', a, a + f, ya, yb, -0.2, -0.06); p.box('frame', b - f, b, ya, yb, -0.2, -0.06)
    p.box('frame', a + f, b - f, yb - f, yb, -0.2, -0.06); p.box('frame', a + f, b - f, ya, ya + f, -0.2, -0.06)
    p.box('glass', a + f - 0.004, b - f + 0.004, ya + f - 0.004, yb - f + 0.004, -0.133, -0.127)
    p.box('frame', a + f, b - f, (ya + yb) / 2 - 0.02, (ya + yb) / 2 + 0.02, -0.15, -0.11)
    for x in np.arange(a + 0.08, b - 0.04, 0.12): p.box('iron', x - 0.008, x + 0.008, ya + 0.02, yb - 0.02, 0.035, 0.051)
    for y in (ya + 0.06, yb - 0.06): p.box('iron', a - 0.04, b + 0.04, y - 0.015, y + 0.015, 0.03, 0.035)
    stone_sill(p, a, b, ya); stone_lintel(p, a, b, yb, False)
def display_window(p, a, b, ya, yb):
    """Vitrine lateral da loja: caixilho de madeira escura, vidro inteiro, bandeira e peitoril de pedra."""
    f = 0.06; z0, z1 = -0.18, -0.08; yt = yb - 0.42
    for (u, v) in ((a, a + f), (b - f, b)): p.cham('shop_f', u, v, ya, yb, z0, z1, 0.006)
    for (y0, y1) in ((ya, ya + f), (yt - 0.03, yt + 0.03), (yb - f, yb)): p.cham('shop_f', a + f - 0.002, b - f + 0.002, y0, y1, z0, z1, 0.006)
    nm = max(1, int(round((b - a) / 1.3)))
    for i in range(1, nm): xm = a + (b - a) * i / nm; p.cham('shop_f', xm - 0.025, xm + 0.025, ya + f, yb - f, z0 + 0.01, z1 - 0.01, 0.005)
    p.box('glass', a + f - 0.004, b - f + 0.004, ya + f - 0.004, yt - 0.026, -0.133, -0.127)
    for j in range(max(2, int(round((b - a) / 0.3)))):
        u0 = a + f + j * (b - a - 2 * f) / max(2, int(round((b - a) / 0.3))); u1 = u0 + (b - a - 2 * f) / max(2, int(round((b - a) / 0.3)))
        p.box('glass', u0 + 0.006, u1 - 0.006, yt + 0.034, yb - f + 0.004, -0.133, -0.127); p.box('shop_f', u1 - 0.008, u1 + 0.008, yt + 0.03, yb - f, -0.14, -0.12) if u1 < b - f - 0.01 else None
    stone_sill(p, a, b, ya); p.box('steel_d', a - 0.12, b + 0.12, yb, yb + 0.2, 0.0, 0.02)
    for x in (a - 0.06, b + 0.06): disc_z(p, 'iron', 0.022, 0.02, 0.035, x, yb + 0.1, 10)
def storefront(p, a, b, side):
    """Fachada de loja no vao (a, b) x (0, 2,6): rodape almofadado, vitrines com montantes, bandeira de vidrinhos, porta recuada
    com bandeira, pilastras de ferro fundido, testeira sem letreiro com pictograma, toldo listrado de lona com armacao."""
    z0, z1 = -0.15, -0.07; f = 0.06; yk, ys, yt, yh = 0.55, 0.6, 2.15, SHOP_H
    d0, d1 = sorted((side * SHOP_D[0], side * SHOP_D[1]))
    for (u, v) in ((a, d0), (d1, b)):
        # rodape de madeira com almofadas
        p.cham('shop_f', u, v, 0.0, yk, z0, z1, 0.008); p.box('dark', u + 0.01, v - 0.01, 0.0, 0.08, z1, z1 + 0.012)
        n = max(1, int(round((v - u) / 0.9)))
        for i in range(n):
            c0 = u + i * (v - u) / n + 0.08; c1 = u + (i + 1) * (v - u) / n - 0.08; p.cham('shop_f', c0, c1, 0.14, yk - 0.08, z1, z1 + 0.018, 0.006)
        p.cham('shop_f', u - 0.01, v + 0.01, yk, ys, z0 - 0.02, z1 + 0.05, 0.008)        # peitoril da vitrine
        for (c0, c1) in ((u, u + f), (v - f, v)): p.cham('shop_f', c0, c1, ys, yh, z0, z1, 0.006)
        n = max(1, int(round((v - u) / 1.25)))
        for i in range(1, n): xm = u + (v - u) * i / n; p.cham('shop_f', xm - 0.03, xm + 0.03, ys, yh - f, z0, z1, 0.005)
        p.box('glass', u + f - 0.004, v - f + 0.004, ys - 0.004, yt - 0.03, -0.113, -0.107)
        p.cham('shop_f', u + f - 0.002, v - f + 0.002, yt - 0.04, yt + 0.04, z0 - 0.01, z1 + 0.01, 0.006)
        nk = max(2, int(round((v - u - 2 * f) / 0.24)))
        for j in range(nk):
            c0 = u + f + j * (v - u - 2 * f) / nk; c1 = c0 + (v - u - 2 * f) / nk
            p.box('glass', c0 + 0.008, c1 - 0.008, yt + 0.036, yh - f + 0.004, -0.113, -0.107)
            if j < nk - 1: p.box('shop_f', c1 - 0.01, c1 + 0.01, yt + 0.04, yh - f, -0.125, -0.095)
        p.cham('shop_f', u + f - 0.002, v - f + 0.002, yh - f, yh, z0, z1, 0.006)
    # porta (batentes, travessa e bandeira)
    for (c0, c1) in ((d0, d0 + f), (d1 - f, d1)): p.cham('shop_f', c0, c1, 0.0, yh, z0, z1, 0.006)
    p.cham('shop_f', d0 + f - 0.002, d1 - f + 0.002, 2.15, 2.23, z0, z1, 0.006); p.cham('shop_f', d0 + f - 0.002, d1 - f + 0.002, yh - f, yh, z0, z1, 0.006)
    p.box('glass', d0 + f - 0.004, d1 - f + 0.004, 2.226, yh - f + 0.004, -0.113, -0.107)
    p.box('alu', d0 + f, d1 - f, -0.012, 0.012, z0 - 0.12, z1 + 0.06)
    # pilastras de ferro fundido nas pontas do vao, com base e capitel
    for x in (a, b):
        u, v = (x - 0.22, x + 0.02) if x == a else (x - 0.02, x + 0.22)
        p.cham('shop_f', u, v, 0.0, 2.55, 0.0, 0.06, 0.008); p.cham('shop_f', u - 0.02, v + 0.02, 0.0, 0.3, 0.0, 0.08, 0.008)
        p.cham('shop_f', u - 0.03, v + 0.03, 2.55, 2.66, 0.0, 0.09, 0.008)
        for xx in np.linspace(u + 0.05, v - 0.05, 3): p.box('shop_f', xx - 0.012, xx + 0.012, 0.36, 2.48, 0.06, 0.07)
    # testeira (sem texto) com moldura e pictograma, e cornija de pedra do terreo
    p.cham('shop_f', a - 0.24, b + 0.24, 2.66, 2.93, 0.0, 0.04, 0.006)
    for (y0, y1) in ((2.7, 2.72), (2.87, 2.89)): p.box('trim', a - 0.1, b + 0.1, y0, y1, 0.04, 0.05)
    xm = (a + b) / 2
    if side > 0:   # mercearia: pictograma de fruta com folha
        disc_z(p, 'cream', 0.07, 0.04, 0.052, xm, 2.795, 18); p.hull('leaf2', [(xm + dx, 2.86 + dy, z) for (dx, dy) in ((0.0, 0.0), (0.07, 0.02), (0.03, 0.045)) for z in (0.04, 0.053)])
    else:          # lavanderia: pictograma de maquina de lavar
        p.box('cream', xm - 0.08, xm + 0.08, 2.725, 2.865, 0.04, 0.048); disc_z(p, 'shop_f', 0.05, 0.05, 0.056, xm, 2.785, 18); disc_z(p, 'glass', 0.035, 0.056, 0.058, xm, 2.785, 18)
    # toldo de lona listrada com armacao de tubo
    awn = 'awn_r' if side > 0 else 'awn_g'; ya, yf, zf = 2.66, 2.25, 1.1; n = int(round((b - a + 0.2) / 0.3))
    for i in range(n):
        u0 = a - 0.1 + i * (b - a + 0.2) / n; u1 = u0 + (b - a + 0.2) / n; m = awn if i % 2 == 0 else 'awn_w'
        p.hull(m, [(x, y, z) for x in (u0, u1) for (y, z) in ((ya, 0.06), (ya - 0.012, 0.06), (yf, zf), (yf - 0.012, zf))])
        p.box(m, u0, u1, yf - 0.26, yf, zf - 0.005, zf + 0.005)
        p.hull(m, [(x, y, z) for x in (u0, u1) for y in (yf - 0.26, yf - 0.28) for z in (zf - 0.005, zf + 0.005)] + [((u0 + u1) / 2, yf - 0.34, zf - 0.005), ((u0 + u1) / 2, yf - 0.34, zf + 0.005)])   # bico do babado
    for x in (a - 0.1, b + 0.1):
        p.hull(awn, [(x + dx, y, z) for dx in ((0.0, 0.01) if x > xm else (-0.01, 0.0)) for (y, z) in ((ya, 0.06), (yf, zf), (yf - 0.26, zf), (yf - 0.26, 0.9))])
        seg_cyl(p, 'steel_d', (x, ya - 0.02, 0.03), (x, yf - 0.02, zf - 0.02), 0.012, 6); seg_cyl(p, 'steel_d', (x, yf - 0.5, 0.0), (x, yf - 0.03, zf - 0.04), 0.01, 6)
    seg_cyl(p, 'steel_d', (a - 0.1, yf - 0.02, zf - 0.02), (b + 0.1, yf - 0.02, zf - 0.02), 0.014, 8)
    p.box('steel_d', a - 0.1, b + 0.1, ya - 0.05, ya - 0.005, 0.0, 0.06)
def hall_entry(p, a, b, yh):
    """Porta do hall: batentes, bandeira de vidro, pilastras de pedra com capitel, entablamento e marquise de chapa com tirantes."""
    z0, z1 = -0.2, -0.1; f = 0.05
    for (u, v) in ((a, a + f), (b - f, b)): p.box('door', u, v, 0.0, yh, z0, z1)
    p.box('door', a + f, b - f, 2.2, 2.26, z0, z1); p.box('door', a + f, b - f, yh - f, yh, z0, z1)
    p.box('glass', a + f - 0.004, b - f + 0.004, 2.256, yh - f + 0.004, -0.153, -0.147)
    for x in np.linspace(a + f, b - f, 4)[1:-1]: p.box('door', x - 0.012, x + 0.012, 2.26, yh - f, -0.16, -0.14)
    p.box('stone_c', a + 0.002, b - 0.002, -0.012, 0.012, -T - 0.01, 0.03)
    for s in (-1, 1):
        u, v = sorted((s * (b + 0.0), s * (b + 0.3)))
        p.cham('stone_c', u, v, 0.0, 2.5, 0.0, 0.07, 0.008); p.cham('stone_c', u - 0.03, v + 0.03, 0.0, 0.35, 0.0, 0.09, 0.008)
        prof_y(p, 'stone_c', 2.5, 2.62, crect(u - 0.035, v + 0.035, 0.0, 0.1, 0.01))
        for xx in np.linspace(u + 0.07, v - 0.07, 3): p.box('stone_c', xx - 0.015, xx + 0.015, 0.4, 2.42, 0.07, 0.08)
    p.cham('stone_c', -(b + 0.36), b + 0.36, 2.62, 2.92, 0.0, 0.1, 0.01)
    prof_x(p, 'stone_c', -(b + 0.4), b + 0.4, [(0.0, 2.92), (0.14, 2.92), (0.14, 2.95), (0.0, 2.95)])
    # marquise de chapa preta com tirantes e luminaria pendente
    p.cham('iron', -1.0, 1.0, 2.66, 2.74, 0.1, 1.0, 0.01); p.box('iron', -1.0, 1.0, 2.6, 2.66, 0.96, 1.0)
    for x in (-0.9, 0.9): seg_cyl(p, 'iron', (x, 2.73, 0.95), (x, 3.4, 0.1), 0.01, 6); disc_z(p, 'iron', 0.04, 0.1, 0.12, x, 3.4, 10)
    p.merge(porch_lantern(), tr(0.0, 2.66, 0.55))
def rear_door_frame(p, a, b, yh):
    """Porta dos fundos de chapa: batente de aco, verga de aco e soleira de concreto."""
    for (u, v) in ((a, a + 0.05), (b - 0.05, b)): p.box('steel_d', u, v, 0.0, yh, -0.2, -0.05)
    p.box('steel_d', a + 0.05, b - 0.05, yh - 0.05, yh, -0.2, -0.05)
    p.box('conc_s', a + 0.002, b - 0.002, -0.012, 0.012, -T - 0.01, 0.06)
    p.box('steel_d', a - 0.15, b + 0.15, yh, yh + 0.2, 0.0, 0.02)
    p.merge(wall_lantern(), tr((a + b) / 2, yh + 0.45, 0.0))
def facade(f, kind):
    """Uma fachada de um pavimento na moldura local, toda de tijolo. Terreo ('g'): embasamento de pedra, vitrines, porta do hall,
    faixa de pedra no alto. Andares ('t'): janelas de guilhotina com peitoril e verga de pedra com fecho."""
    M, us = fac_frame(f); q = Piece(); n = f[0]
    l0, l1 = sorted((us * f[4], us * f[5]))
    ops = [(*sorted((us * a, us * b)), ya, yb, k) for (a, b, ya, yb, k) in ops_of(f, kind)]
    y0 = GY - Y0 if kind == 'g' else 0.0
    wall2(q, 'x', l0, l1, 0.0, -T, [o[:4] for o in ops], y0, H, 'brick', 'plaster')
    for (a, b, ya, yb, k) in ops:
        if k == 'win': hung_window(q, a, b, ya, yb, 1); int_casing(q, a, b, ya, yb)
        elif k == 'winb': barred_window(q, a, b, ya, yb); int_casing(q, a, b, ya, yb)
        elif k == 'disp': display_window(q, a, b, ya, yb); int_casing(q, a, b, ya, yb)
        elif k == 'shop': storefront(q, a, b, 1 if a > 0 else -1); q.box('stone_c', a + 0.002, b - 0.002, -0.012, 0.004, -T - 0.01, -0.15)
        elif k == 'hdoor': hall_entry(q, a, b, yb); int_casing(q, a, b, 0.0, yb, False)
        elif k == 'rdoor': rear_door_frame(q, a, b, yb); int_casing(q, a, b, 0.0, yb, False)
    v0, v1 = (-BX, BX) if f[1] == 'x' else (-BZ, BZ)                  # faixas correm ate a quina (as quinas tem meia-esquadria)
    if kind == 'g':
        gaps = [(a - (0.26 if k == 'shop' else 0.4 if k == 'hdoor' else 0.02), b + (0.26 if k == 'shop' else 0.4 if k == 'hdoor' else 0.02)) for (a, b, ya, yb, k) in ops if ya < 0.01]
        for (u, v) in segs_excl(gaps, v0, v1):
            q.box('stone_c', u, v, GY - Y0, 0.36, 0.0, 0.03)                                         # embasamento de pedra
            prof_x(q, 'stone_c', u, v, [(0.0, 0.36), (0.03, 0.36), (0.03, 0.38), (0.012, 0.4), (0.0, 0.4)])
        # faixa de pedra no alto do terreo (corre em toda a volta, acima de todos os vaos)
        prof_x(q, 'stone_c', v0, v1, BELT)
    return q, M
BELT = [(0.0, 2.95), (0.06, 2.95), (0.07, 2.97), (0.07, 3.1), (0.05, 3.12), (0.0, 3.13)]
def belt_corners(p):
    """Quinas da faixa de pedra do terreo (meia-esquadria)."""
    prof = BELT
    for (x, z, r) in ((BX, BZ, 0), (-BX, BZ, -90), (-BX, -BZ, 180), (BX, -BZ, 90)):
        q = Piece(); mitre_pair(q, 'stone_c', prof); p.merge(q, rot_y(r, (x, 0, z)))
        q = Piece(); mitre_pair(q, 'stone_c', [(0.0, GY - Y0), (0.03, GY - Y0), (0.03, 0.36), (0.0, 0.36)]); p.merge(q, rot_y(r, (x, 0, z)))
        q = Piece(); mitre_pair(q, 'stone_c', [(0.0, 0.36), (0.03, 0.36), (0.03, 0.38), (0.012, 0.4), (0.0, 0.4)]); p.merge(q, rot_y(r, (x, 0, z)))
def shell(kind):
    """Envoltoria de um pavimento (pivo: piso do pavimento, centro do predio): 4 fachadas de tijolo, rodape interno e, no terreo,
    as quinas da faixa e do embasamento."""
    p = Piece()
    for f in FACS:
        q, M = facade(f, kind); p.merge(q, M)
    if kind == 'g': belt_corners(p)
    # rodape interno (para nas portas e vitrines do terreo; o hall tem o seu)
    WU = WALL_U_G if kind == 'g' else WALL_U
    bb = INNER.difference(INNER.buffer(-0.012, join_style=2))
    cut = [sbox(-HX - 0.12, BZ - T - 0.1, HX + 0.12, BZ - T + 0.1)]
    if kind == 'g':
        cut += [sbox(s * SHOP[0] - 0.3, BZ - T - 0.1, s * SHOP[1] + 0.3, BZ - T + 0.1) for s in (1,)] + [sbox(-SHOP[1] - 0.3, BZ - T - 0.1, -SHOP[0] + 0.3, BZ - T + 0.1)]
        cut += [sbox(a - 0.08, -BZ + T - 0.1, b + 0.08, -BZ + T + 0.1) for (a, b) in RDOOR]
    ext_y(p, 'trim', bb.difference(unary_union(cut)).difference(WU), 0.0, 0.1)
    if kind == 'g':
        for s in (-1, 1): p.merge(wall_lantern(), tr(s * 1.25, 1.9, BZ))
    return p
INNER = FOOT.buffer(-T, join_style=2)
# ============================================================================ paredes internas, lajes, escada (moldura do predio)
HZB = 0.44                                                          # fundo do hall: parede z 0,44..0,64
ID = 0.8                                                            # portas internas
DOORS_R = [('x', ZB, 2.65, 2.65 + ID, 'bed2'), ('x', ZB, 5.1, 5.1 + ID, 'bath'), ('x', ZB, 7.55, 7.55 + ID, 'master'), ('z', 6.96, -5.1, -5.1 + ID, 'closet')]
# paredes (eixo, linha central, de, ate, espessura, portas [(a, b)]) do apartamento da direita (o da esquerda e o espelho)
WALLS_R = [('z', HX, HZI, BZ - T, TD, [UDOOR]),                     # hall | sala (porta do apartamento)
           ('x', ZB, HX + TD / 2, BX - T, TP, [(2.65, 2.65 + ID), (5.1, 5.1 + ID), (7.55, 7.55 + ID)]),
           ('z', 4.36, -BZ + T, ZB - TP / 2, TP, []), ('x', -3.06, 4.42, 6.9, TP, []), ('z', 6.96, -BZ + T, ZB - TP / 2, TP, [(-5.1, -5.1 + ID)])]
WALLS_C = [('x', HZB + 0.1, -HX - TD / 2, HX + TD / 2, TD, []), ('z', 0.0, -BZ + T, HZB, TD, [])]   # fundo do hall e parede entre os quartos 2
def mirror_wall(w):
    ax, c, a, b, t, ds = w
    if ax == 'z': return (ax, -c, a, b, t, ds)
    return (ax, c, -b, -a, t, [(-v, -u) for (u, v) in ds])
WALLS = WALLS_C + WALLS_R + [mirror_wall(w) for w in WALLS_R]
def wall_rect(w):
    ax, c, a, b, t, ds = w
    return sbox(a, c - t / 2, b, c + t / 2) if ax == 'x' else sbox(c - t / 2, a, c + t / 2, b)
def door_rects(w, pad=0.0):
    ax, c, a, b, t, ds = w
    return [sbox(u, c - t / 2 - pad, v, c + t / 2 + pad) if ax == 'x' else sbox(c - t / 2 - pad, u, c + t / 2 + pad, v) for (u, v) in ds]
def wall_u(ws): return unary_union([wall_rect(w) for w in ws]).difference(unary_union([r for w in ws for r in door_rects(w, 0.01)]))
WALL_U = wall_u(WALLS)
# terreo: fundo do hall, paredes do hall ate os fundos (casa de maquinas atras), deposito e lavabo das lojas
WALLS_GR = [('z', HX, -BZ + T, BZ - T, TD, []), ('x', -2.45, HX + TD / 2, BX - T, TP, [(9.4, 9.4 + ID)]), ('z', 3.6, -BZ + T, -2.45 - TP / 2, TP, [(-4.4, -4.4 + ID)])]
WALLS_G = [('x', HZB + 0.1, -HX + TD / 2, HX - TD / 2, TD, [])] + WALLS_GR + [mirror_wall(w) for w in WALLS_GR]
WALL_U_G = wall_u(WALLS_G)
DOORS_G = [('x', -2.45, 9.4, 9.4 + ID, 'back'), ('z', 3.6, -4.4, -4.4 + ID, 'wc')]
def casing(p, ax, c, t, a, b, h=DH):
    """Batente (forra) e guarnicoes dos 2 lados de um vao de porta em parede interna."""
    for s in (-1, 1):
        v0 = c + s * t / 2; v1 = v0 + s * 0.014
        for (u0, u1) in ((a - 0.07, a), (b, b + 0.07)): bx(p, 'trim', ax, u0, u1, 0.0, h + 0.07, v0, v1)
        bx(p, 'trim', ax, a, b, h, h + 0.07, v0, v1)
    bx(p, 'trim', ax, a, a + 0.015, 0.0, h, c - t / 2, c + t / 2); bx(p, 'trim', ax, b - 0.015, b, 0.0, h, c - t / 2, c + t / 2)
    bx(p, 'trim', ax, a + 0.015, b - 0.015, h - 0.015, h, c - t / 2, c + t / 2)
def walls(kind):
    """Paredes internas de um pavimento (pivo: piso): divisorias de gesso pintado, portas com batente e guarnicoes, rodape que
    para nas portas. No terreo: paredes do hall, deposito e lavabo das lojas e parede embaixo da escada com caixas de correio."""
    p = Piece(); WS = WALLS_G if kind == 'g' else WALLS; WU = WALL_U_G if kind == 'g' else WALL_U
    for w in WS:
        ax, c, a, b, t, ds = w
        wall_grid(p, ax, a, b, c - t / 2, c + t / 2, [(u, v, 0.0, DH) for (u, v) in ds], 0.0, CH, 'plaster')
        for (u, v) in ds: casing(p, ax, c, t, u, v)
    cz = []
    for w in WS:
        ax, c, a, b, t, ds = w
        for (u, v) in ds: cz.append(sbox(u - 0.07, c - t / 2 - 0.05, v + 0.07, c + t / 2 + 0.05) if ax == 'x' else sbox(c - t / 2 - 0.05, u - 0.07, c + t / 2 + 0.05, v + 0.07))
    bb = WU.buffer(0.012, join_style=2).difference(WU).intersection(INNER.buffer(-0.0005, join_style=2)).difference(unary_union(cz))
    if kind == 't':
        bb = bb.difference(sbox(-HX + 0.1, HZI - 0.05, HX - 0.1, ZF + 0.02))       # nao passa no vao da escada
    ext_y(p, 'trim', bb, 0.0, 0.1)
    if kind == 'g':
        # parede embaixo do lance B (fecha o vao) e caixas de correio embutidas
        p.hull('plaster', [(x, y, z) for x in (-HX + TD / 2, -0.08) for z in (ZF - 0.12, ZF) for y in (0.0, 2.52)])
        x0, x1, y0, y1 = -1.65, -0.35, 0.9, 1.75
        p.cham('mail', x0, x1, y0, y1, ZF, ZF + 0.04, 0.006)
        for i in range(4):
            for j in range(3):
                a = x0 + 0.05 + i * (x1 - x0 - 0.1) / 4; b = a + (x1 - x0 - 0.1) / 4 - 0.015; c0 = y0 + 0.05 + j * (y1 - y0 - 0.1) / 3; d0 = c0 + (y1 - y0 - 0.1) / 3 - 0.015
                p.box('alu', a, b, c0, d0, ZF + 0.04, ZF + 0.048); p.box('dark', b - 0.06, b - 0.03, (c0 + d0) / 2 - 0.012, (c0 + d0) / 2 + 0.012, ZF + 0.048, ZF + 0.056)
        p.box('trim', -HX + 0.1, -0.08, 0.0, 0.1, ZF + 0.0, ZF + 0.012)
    return p

# ---------------------------------------------------------------------------- lajes e pisos
ROOMS_F = {'wood_f': [sbox(HX, ZB + 0.06, 7.4, BZ), sbox(0.0, -BZ, 4.36, ZB + 0.06), sbox(4.36, -BZ, 6.96, -3.06), sbox(6.96, -BZ, BX, ZB - 0.06)],
           'vinyl_f': [sbox(7.4, ZB - 0.06, BX, BZ)], 'tile_hex': [sbox(4.36, -3.06, 6.96, ZB + 0.06)]}
def mx(g): return affinity.scale(g, -1.0, 1.0, origin=(0, 0))
HALL_F = sbox(-HX - 0.1, HZB + 0.1, HX + 0.1, BZ)
STAIR_HOLE = sbox(-HX + TD / 2, HZI, HX - TD / 2, ZF)
SHOP_F = sbox(HX + TD / 2, -2.45 + TP / 2, BX - T, BZ - T)                # area de venda da loja da direita
def parquet(p, poly, y0, y1, mat='wood_f'):
    """Piso de taco em espinha simplificada: reguas de 0,9 x 0,15 em quadros alternados de 90 cm, com junta."""
    b = poly.bounds; s = 0.9; n = 6; w = s / n
    for i in range(int(math.floor(b[0] / s)), int(math.ceil(b[2] / s))):
        for j in range(int(math.floor(b[1] / s)), int(math.ceil(b[3] / s))):
            for k in range(n):
                if (i + j) % 2 == 0: r = sbox(i * s + 0.002, j * s + k * w + 0.002, (i + 1) * s - 0.002, j * s + (k + 1) * w - 0.002)
                else: r = sbox(i * s + k * w + 0.002, j * s + 0.002, i * s + (k + 1) * w - 0.002, (j + 1) * s - 0.002)
                q = r.intersection(poly)
                if q.area > 1e-5: ext_y(p, mat, q, y0, y1)
    ext_y(p, 'dkwood', poly.buffer(-0.001, join_style=2), y0, y1 - 0.003)
def floors(p, y1=0.0):
    """Acabamentos de piso (12 mm) por comodo: taco na sala e nos quartos, vinilico na cozinha, ladrilho sextavado no banheiro."""
    free = INNER.difference(WALL_U)
    for mat, zs in ROOMS_F.items():
        g = free.intersection(unary_union(zs + [mx(z) for z in zs]).difference(HALL_F))
        if mat == 'wood_f': parquet(p, g, y1 - 0.012, y1)
        elif mat == 'tile_hex': tiles(p, g, y1 - 0.012, y1, 0.15, 'tile_hex', 0.003, 'grille')
        else: ext_y(p, mat, g, y1 - 0.012, y1)
    return free
LIGHTS_R = [(4.75, 3.2), (8.3, 2.3), (10.5, 2.0), (2.2, -2.6), (5.66, -1.3), (5.66, -4.4), (9.36, -2.6)]
def ceiling_lights(p, y, apt=True):
    pts = ((LIGHTS_R + [(-x, z) for (x, z) in LIGHTS_R]) if apt else []) + [(0.0, 4.85)]
    for (x, z) in pts:
        p.cyl('paint_w', 0.17, y - 0.02, y, x, z, 20); lathe(p, 'lamp_glass', [(0.15, y - 0.02), (0.13, y - 0.06), (0.07, y - 0.085), (0.0, y - 0.09)], x, z, sec=20)
    if apt:
        for (x, z) in ((3.4, 1.4), (-3.4, 1.4)):   # detector de fumaca
            p.cyl('paint_w', 0.06, y - 0.03, y, x, z, 14); p.cyl('screen_g', 0.006, y - 0.032, y - 0.03, x + 0.03, z, 6)
def slab(kind):
    """Laje de um pavimento (pivo: piso). 'g': contrapiso no chao com pisos do terreo (ladrilho nas lojas, concreto no deposito,
    granilite no hall); 't': laje com forro do pavimento de baixo, vao da escada, pisos dos apartamentos e luminarias de baixo;
    't1': igual, sobre as lojas (o forro de chapa e as luminarias das lojas vem com a mobilia); 'r': laje do telhado (forro do
    ultimo andar; a impermeabilizacao vem com o telhado)."""
    p = Piece(); hall = INNER.intersection(HALL_F).difference(WALL_U)
    if kind == 'g':
        ext_y(p, 'conc_s', INNER, GY - Y0, -0.012)
        free = INNER.difference(WALL_U_G)
        hall = free.intersection(sbox(-HX + TD / 2, HZB + 0.2, HX - TD / 2, BZ))
        tiles(p, hall, -0.012, 0.0, 0.5, 'terrazzo', 0.004, 'stone_c')
        for g in (SHOP_F, mx(SHOP_F)): tiles(p, free.intersection(g), -0.012, 0.0, 0.3, 'tile_f', 0.003, 'grille')
        for g in (sbox(3.6 + TP / 2, -BZ + T, BX - T, -2.45 - TP / 2), sbox(-BX + T, -BZ + T, -3.6 - TP / 2, -2.45 - TP / 2), sbox(-HX + TD / 2, -BZ + T, HX - TD / 2, HZB)):
            ext_y(p, 'conc_r', free.intersection(g), -0.012, 0.0)
        for g in (sbox(HX + TD / 2, -BZ + T, 3.6 - TP / 2, -2.45 - TP / 2), sbox(-3.6 + TP / 2, -BZ + T, -HX - TD / 2, -2.45 - TP / 2)):
            tiles(p, free.intersection(g), -0.012, 0.0, 0.15, 'tile_hex', 0.003, 'grille')
        for (ax, c, a, b, nm) in DOORS_G:   # soleiras das portas do terreo (as paredes vao ate o contrapiso)
            for s in (1, -1):
                if ax == 'x': u0, u1 = sorted((s * a, s * b)); ext_y(p, 'stone_c', sbox(u0, c - TP / 2, u1, c + TP / 2), -0.012, 0.004)
                else: u0, u1 = sorted((s * (c - TP / 2), s * (c + TP / 2))); ext_y(p, 'stone_c', sbox(u0, a, u1, b), -0.012, 0.004)
        return p
    hole = STAIR_HOLE
    ext_y(p, 'ceil', INNER.difference(hole), -ST, -ST + 0.012); ext_y(p, 'conc_s', INNER.difference(hole), -ST + 0.012, -0.012)
    tiles(p, hall.difference(hole), -0.012, 0.0, 0.5, 'terrazzo', 0.004, 'stone_c')
    p.box('dark', -HX + TD / 2 + 0.005, HX - TD / 2 - 0.005, -0.04, 0.003, ZF - 0.003, ZF + 0.05)                 # focinho do ultimo degrau (borda da laje)
    if kind != 'r': floors(p)
    ceiling_lights(p, -ST, kind != 't1')
    if kind == 'r': ext_y(p, 'conc_s', INNER.difference(hall).difference(hole), -0.012, 0.0)
    return p

# ---------------------------------------------------------------------------- escada do hall
def stair():
    """Escada em U entre 2 pavimentos (pivo: piso de baixo): lance A sobe para -z (x > 0) ate o patamar do fundo, lance B volta
    para +z (x < 0). Concreto com piso de granilite, focinho de borracha, corrimao de madeira nas paredes e guarda-corpo de aco
    com balaustres entre os lances."""
    p = Piece(); n2 = SNR // 2; yL = n2 * SRR; xg = 0.06; xw = HX - TD / 2
    pr = [(ZF, 0.0)]
    for i in range(1, n2):
        pr += [(ZF - (i - 1) * STRD, i * SRR), (ZF - i * STRD, i * SRR)]
    pr += [(ZM, yL - 0.25), (ZF - 0.9, 0.0)]
    prof_x(p, 'terrazzo', xg, xw, pr)
    pr = [(ZM, yL)]
    for j in range(1, n2):
        pr += [(ZM + (j - 1) * STRD, yL + j * SRR), (ZM + j * STRD, yL + j * SRR)]
    pr += [(ZF, H - ST - 0.25), (ZM, yL - 0.2)]
    prof_x(p, 'terrazzo', -xw, -xg, pr)
    p.box('terrazzo', -xw, xw, yL - 0.2, yL, HZI, ZM)
    for i in range(1, n2):
        zf = ZF - (i - 1) * STRD; p.box('dark', xg + 0.02, xw - 0.02, i * SRR - 0.03, i * SRR + 0.003, zf - 0.05, zf + 0.003)
        zb = ZM + (i - 1) * STRD; p.box('dark', -xw + 0.02, -xg - 0.02, yL + i * SRR - 0.03, yL + i * SRR + 0.003, zb - 0.003, zb + 0.05)
    p.box('dark', xg + 0.02, xw - 0.02, yL - 0.03, yL + 0.003, ZM - 0.003, ZM + 0.05)
    # corrimaos de madeira nas paredes (suportes de aco)
    y1 = lambda z: SRR + (ZF - z) / STRD * SRR; y2 = lambda z: yL + SRR + (z - ZM) / STRD * SRR
    for (x, za, zb, fy) in ((xw - 0.075, ZF, ZM, y1), (-xw + 0.075, ZM, ZF, y2)):
        ya, yb = fy(za) + 0.88, fy(zb) + 0.88; dz = math.copysign(0.3, zb - za)
        seg_cyl(p, 'wood', (x, ya, za - dz), (x, ya, za), 0.024, 10); seg_cyl(p, 'wood', (x, ya, za), (x, yb, zb), 0.024, 10); seg_cyl(p, 'wood', (x, yb, zb), (x, yb, zb + dz), 0.024, 10)
        for t in (0.15, 0.5, 0.85):
            z = za + (zb - za) * t; y = ya + (yb - ya) * t; xs = math.copysign(1, x)
            seg_cyl(p, 'steel_d', (x, y - 0.03, z), (x + xs * 0.06, y - 0.07, z), 0.008, 6); disc_x(p, 'steel_d', 0.03, *sorted((x + xs * 0.06, x + xs * 0.075)), y - 0.07, z, 10)
    # guarda-corpo entre os lances: banzo, corrimao e balaustres
    for (x, za, zb, fy) in ((xg + 0.03, ZF, ZM, y1), (-xg - 0.03, ZM, ZF, y2)):
        ya, yb = fy(za), fy(zb)
        p.hull('steel_d', [(x + dx, y, z) for dx in (-0.012, 0.012) for (y, z) in ((ya - 0.05, za), (ya + 0.06, za), (yb - 0.05, zb), (yb + 0.06, zb))])
        seg_cyl(p, 'wood', (x, ya + 0.92, za), (x, yb + 0.92, zb), 0.028, 10)
        n = int(abs(zb - za) / 0.12)
        for k in range(n + 1):
            z = za + (zb - za) * k / n; y = ya + (yb - ya) * k / n; seg_cyl(p, 'steel_d', (x, y + 0.05, z), (x, y + 0.9, z), 0.008, 6)
        for z, y in ((za, ya), (zb, yb)): p.box('steel_d', x - 0.025, x + 0.025, y - 0.02, y + 0.95, z - 0.025, z + 0.025)
    seg_cyl(p, 'wood', (xg + 0.03, yL + 0.92, ZM), (-xg - 0.03, yL + 0.92, ZM), 0.028, 10)
    return p
def hall_rail():
    """Guarda-corpo do ultimo andar na borda do vao da escada (pivo: piso)."""
    p = Piece(); x0, x1 = 0.06, HX - TD / 2; z = ZF + 0.1
    p.box('steel_d', x0, x1, 0.0, 0.05, z - 0.02, z + 0.02); seg_cyl(p, 'wood', (x0 + 0.005, 0.95, z), (x1 - 0.005, 0.95, z), 0.028, 10)
    for x in np.arange(x0 + 0.06, x1, 0.12): seg_cyl(p, 'steel_d', (x, 0.05, z), (x, 0.93, z), 0.008, 6)
    for x in (x0 + 0.025, x1 - 0.025): p.box('steel_d', x - 0.025, x + 0.025, 0.0, 0.97, z - 0.025, z + 0.025)
    return p
# ============================================================================ moveis e equipamentos dos apartamentos
def P(): return Piece()
def place(p, q, x, y, z, ry=0.0): p.merge(q, rot_y(ry, (x, y, z)))
def handle_bar(p, x0, x1, y, z, axis='x'):
    if axis == 'x':
        p.box('chrome', x0, x1, y - 0.008, y + 0.008, z + 0.022, z + 0.03)
        for x in (x0 + 0.01, x1 - 0.01): p.box('chrome', x - 0.005, x + 0.005, y - 0.006, y + 0.006, z, z + 0.022)
    else:
        p.box('chrome', x0 - 0.008, x0 + 0.008, y, y + (x1 - x0), z + 0.022, z + 0.03)
        for yy in (y + 0.01, y + (x1 - x0) - 0.01): p.box('chrome', x0 - 0.005, x0 + 0.005, yy - 0.006, yy + 0.006, z, z + 0.022)
def base_cab(L1, plan, top=True, hole=None, d=0.6):
    """Armario de base (pivo: canto de tras a esquerda, piso; frente +Z): rodape recuado, caixa, frentes de porta/gaveta com
    puxador, tampo de granito escuro com saia e frontao de azulejo. plan = [(largura, tipo)] tipo 'dd' 2 portas, 'd' porta,
    'g' gaveteiro, 'x' vao (maquina). hole = (x0, x1, z0, z1) recorte da cuba no tampo."""
    p = P(); p.box('dark', 0.0, L1, 0.0, 0.1, 0.0, d - 0.08); p.box('cab', 0.0, L1, 0.1, 0.87, 0.0, d - 0.022)
    x = 0.0
    for (w, k) in plan:
        a, b = x + 0.003, x + w - 0.003; zf0, zf1 = d - 0.022, d
        if k == 'g':
            for (y0, y1) in ((0.1, 0.36), (0.364, 0.62), (0.624, 0.84)): p.cham('cab', a, b, y0, y1, zf0, zf1, 0.004); handle_bar(p, (a + b) / 2 - 0.08, (a + b) / 2 + 0.08, y1 - 0.05, zf1)
        elif k in ('d', 'dd'):
            p.cham('cab', a, b, 0.66, 0.84, zf0, zf1, 0.004); handle_bar(p, (a + b) / 2 - 0.08, (a + b) / 2 + 0.08, 0.79, zf1)
            if k == 'dd':
                m = (a + b) / 2
                for (u, v, hx) in ((a, m - 0.002, m - 0.04), (m + 0.002, b, m + 0.04)): p.cham('cab', u, v, 0.1, 0.656, zf0, zf1, 0.004); p.box('chrome', hx - 0.008, hx + 0.008, 0.46, 0.6, zf1, zf1 + 0.025)
            else:
                p.cham('cab', a, b, 0.1, 0.656, zf0, zf1, 0.004); p.box('chrome', b - 0.05, b - 0.034, 0.46, 0.6, zf1, zf1 + 0.025)
        x += w
    if top:
        g = sbox(0.0, 0.0, L1, d + 0.03)
        if hole: g = g.difference(sbox(hole[0], hole[2], hole[1], hole[3]))
        ext_y(p, 'ctop', g, 0.87, 0.9); p.box('tile_w', 0.0, L1, 0.9, 1.45, 0.0, 0.008)
    return p
def upper_cab(L1, n):
    """Armario aereo de 2 a 4 portas (pivo: canto de tras a esquerda, piso; frente +Z)."""
    p = P(); p.box('cab', 0.0, L1, 1.47, 2.2, 0.0, 0.31); w = L1 / n
    for i in range(n):
        a, b = i * w + 0.003, (i + 1) * w - 0.003; p.cham('cab', a, b, 1.475, 2.195, 0.31, 0.33, 0.004)
        hx = b - 0.04 if i % 2 == 0 else a + 0.04; p.box('chrome', hx - 0.008, hx + 0.008, 1.5, 1.64, 0.33, 0.355)
    return p
def sink_bowl(p, x0, x1, z0, z1):
    """Cuba dupla de inox embaixo do recorte do tampo, torneira gourmet e registro."""
    xm = (x0 + x1) / 2; yb, yt = 0.68, 0.9
    for (a, b) in ((x0, xm - 0.02), (xm + 0.02, x1)):
        p.box('chrome', a, b, yb, yb + 0.01, z0, z1)
        for (u, v, c, e) in ((a, a + 0.01, z0, z1), (b - 0.01, b, z0, z1), (a, b, z0, z0 + 0.01), (a, b, z1 - 0.01, z1)): p.box('chrome', u, v, yb + 0.01, yt - 0.003, c, e)
        p.cyl('steel_d', 0.035, yb + 0.01, yb + 0.013, (a + b) / 2, (z0 + z1) / 2, 12)
    p.box('chrome', xm - 0.02, xm + 0.02, yb, yt - 0.003, z0, z1)
    zt = z0 - 0.05; p.cyl('chrome', 0.025, 0.9, 0.95, xm, zt, 12)
    seg_cyl(p, 'chrome', (xm, 0.95, zt), (xm, 1.25, zt), 0.014, 8); seg_cyl(p, 'chrome', (xm, 1.25, zt), (xm, 1.22, zt + 0.22), 0.012, 8)
    seg_cyl(p, 'chrome', (xm, 1.22, zt + 0.22), (xm, 1.15, zt + 0.23), 0.016, 8); seg_cyl(p, 'chrome', (xm + 0.03, 1.0, zt), (xm + 0.12, 1.05, zt), 0.008, 6)
def range_oven():
    """Fogao de piso de 76 cm (pivo: centro de tras, piso; frente +Z): mesa de vidro com 4 bocas, painel de botoes, porta do
    forno com visor e puxador, gaveta."""
    p = P(); x = 0.38; p.box('appl', -x, x, 0.0, 0.9, 0.02, 0.64); p.box('appl_d', -x, x, 0.9, 0.912, 0.02, 0.66)
    for (cx, cz, r) in ((-0.17, 0.2, 0.1), (0.17, 0.2, 0.08), (-0.17, 0.48, 0.08), (0.17, 0.48, 0.1)): ring_y(p, 'steel', r - 0.012, r, 0.912, 0.914, cx, cz, 20)
    p.box('appl', -x, x, 0.912, 1.08, 0.02, 0.1)
    for k in range(5): disc_z(p, 'dark', 0.022, 0.1, 0.13, -0.28 + k * 0.14, 1.0, 10)
    p.cham('appl', -x + 0.01, x - 0.01, 0.18, 0.8, 0.64, 0.67, 0.006); p.box('appl_d', -0.26, 0.26, 0.36, 0.66, 0.67, 0.673)
    seg_cyl(p, 'chrome', (-0.3, 0.74, 0.7), (0.3, 0.74, 0.7), 0.012, 8)
    for xx in (-0.28, 0.28): seg_cyl(p, 'chrome', (xx, 0.74, 0.67), (xx, 0.74, 0.7), 0.008, 6)
    p.cham('appl', -x + 0.01, x - 0.01, 0.03, 0.16, 0.64, 0.665, 0.006); p.box('dark', -x + 0.02, x - 0.02, 0.0, 0.03, 0.04, 0.6)
    return p
def hood_mw():
    """Micro-ondas sobre o fogao com exaustor (pivo: centro de tras, piso)."""
    p = P(); p.cham('appl', -0.38, 0.38, 1.5, 1.9, 0.0, 0.38, 0.01); p.box('appl_d', -0.34, 0.12, 1.56, 1.84, 0.38, 0.383)
    p.box('dark', 0.16, 0.34, 1.6, 1.84, 0.38, 0.384); p.box('chrome', 0.12, 0.14, 1.58, 1.82, 0.383, 0.41)
    p.box('grille', -0.34, 0.34, 1.497, 1.5, 0.05, 0.34)
    return p
def fridge_home():
    """Geladeira duplex (pivo: centro de tras, piso; frente +Z): freezer em cima, puxadores verticais e grade embaixo."""
    p = P(); x = 0.375; p.cham('appl', -x, x, 0.0, 1.76, 0.0, 0.66, 0.02)
    p.cham('appl', -x + 0.005, x - 0.005, 1.22, 1.755, 0.66, 0.7, 0.012); p.cham('appl', -x + 0.005, x - 0.005, 0.1, 1.215, 0.66, 0.7, 0.012)
    p.box('grille', -x + 0.04, x - 0.04, 0.02, 0.09, 0.62, 0.665)
    for (y0, y1) in ((1.3, 1.6), (0.75, 1.15)):
        p.box('chrome', x - 0.07, x - 0.05, y0, y1, 0.73, 0.75)
        for y in (y0 + 0.02, y1 - 0.02): p.box('chrome', x - 0.07, x - 0.05, y - 0.012, y + 0.012, 0.7, 0.73)
    return p
def dishwasher_front(p, x0, x1, d=0.6):
    p.cham('appl', x0 + 0.003, x1 - 0.003, 0.1, 0.84, d - 0.022, d, 0.004); p.box('appl_d', x0 + 0.02, x1 - 0.02, 0.76, 0.83, d, d + 0.002)
    p.box('chrome', x0 + 0.1, x1 - 0.1, 0.72, 0.74, d + 0.01, d + 0.03); p.box('cab', x0, x1, 0.84, 0.87, 0.0, d - 0.022)
def kitchen():
    """Cozinha em L (moldura do apartamento da direita): base e aereos, cuba dupla embaixo da janela, lava-loucas, fogao,
    micro-ondas com exaustor, geladeira, frontao de azulejo e objetos (escorredor, chaleira, fruteira, panos)."""
    p = P(); zb = ZB + TP / 2; xe = BX - T
    # perna A, ao longo da parede z = 0,56 (frente +z): geladeira 9,2..9,95, gaveteiro, fogao 10,4..11,16, canto
    place(p, fridge_home(), 9.575, 0.0, zb)
    place(p, base_cab(0.45, [(0.45, 'g')]), 9.95, 0.0, zb)
    place(p, range_oven(), 10.78, 0.0, zb); place(p, hood_mw(), 10.78, 0.0, zb)
    place(p, base_cab(xe - 11.16, [(xe - 11.16, 'd')]), 11.16, 0.0, zb)
    place(p, upper_cab(0.45, 1), 9.95, 0.0, zb); place(p, upper_cab(xe - 11.16, 1), 11.16, 0.0, zb)
    p.box('cab', 9.2, 9.95, 1.8, 2.2, zb, zb + 0.62)                                               # aereo sobre a geladeira
    # perna B, ao longo da parede x = 11,7 (frente -x), de z = 1,16 a 3,0: lava-loucas, pia dupla embaixo da janela e gaveteiro
    z0 = zb + 0.6; L1 = 3.0 - z0
    q = base_cab(L1, [(0.6, 'x'), (0.84, 'dd'), (L1 - 1.44, 'g')], hole=(0.66, 1.38, 0.12, 0.52))
    dishwasher_front(q, 0.0, 0.6); sink_bowl(q, 0.66, 1.38, 0.12, 0.52)
    place(p, q, xe, 0.0, z0, -90)
    # objetos
    p.cham('steel', xe - 0.5, xe - 0.2, 0.9, 0.98, 2.6, 2.9, 0.01)                                 # escorredor
    lathe(p, 'appl_d', [(0.08, 0.9), (0.1, 0.98), (0.07, 1.1), (0.0, 1.12)], 10.6, zb + 0.3, sec=14)   # chaleira na boca
    lathe(p, 'wood', [(0.0, 0.9), (0.14, 0.9), (0.16, 0.96), (0.15, 0.97), (0.12, 0.92), (0.0, 0.92)], xe - 0.3, 1.2, sec=16)
    for (dx, dz, m) in ((0.0, 0.0, 'food_r'), (0.06, 0.05, 'food_y'), (-0.05, 0.04, 'leaf2')): p.sphere('rug' if m == 'food_r' else ('paint_y' if m == 'food_y' else 'leaf2'), 0.04, xe - 0.3 + dx, 0.96, 1.2 + dz, 1)
    p.box('curtain', 11.3, 11.42, 0.62, 0.8, zb + 0.62, zb + 0.635)
    return p
def dining_chair():
    p = P()
    for (x, z) in ((-0.19, -0.19), (0.19, -0.19), (-0.19, 0.19), (0.19, 0.19)): p.box('wood', x - 0.02, x + 0.02, 0.0, 0.45, z - 0.02, z + 0.02)
    p.cham('wood', -0.22, 0.22, 0.45, 0.48, -0.22, 0.22, 0.008); p.cham('cushion', -0.2, 0.2, 0.48, 0.51, -0.2, 0.2, 0.01)
    for x in (-0.19, 0.19): p.box('wood', x - 0.02, x + 0.02, 0.48, 0.92, -0.23, -0.19)
    for y in (0.7, 0.85): p.box('wood', -0.19, 0.19, y, y + 0.06, -0.225, -0.2)
    return p
def dining_set():
    p = P(); cx, cz = 10.3, 4.45
    p.cham('wood', cx - 0.42, cx + 0.42, 0.72, 0.76, cz - 0.65, cz + 0.65, 0.008)
    for (x, z) in ((-0.36, -0.58), (0.36, -0.58), (-0.36, 0.58), (0.36, 0.58)): p.box('wood', cx + x - 0.025, cx + x + 0.025, 0.0, 0.72, cz + z - 0.025, cz + z + 0.025)
    for (dx, dz, r) in ((0.0, -0.95, 0), (0.0, 0.95, 180), (-0.68, -0.3, 90), (0.68, 0.3, -90)): place(p, dining_chair(), cx + dx, 0.0, cz + dz, r)
    lathe(p, 'glass', [(0.0, 0.76), (0.05, 0.76), (0.04, 0.9), (0.02, 0.98), (0.0, 0.98)], cx, cz, sec=12)
    for (dx, dz) in ((-0.2, -0.35), (0.2, 0.35)): p.cham('curtain', cx + dx - 0.18, cx + dx + 0.18, 0.76, 0.765, cz + dz - 0.13, cz + dz + 0.13, 0.002)
    seg_cyl(p, 'dark', (cx, CH - 0.002, cz), (cx, CH - 0.7, cz), 0.006, 4)
    lathe(p, 'paint_w', [(0.0, CH - 0.7), (0.04, CH - 0.7), (0.2, CH - 0.92), (0.19, CH - 0.93), (0.0, CH - 0.93)], cx, cz, sec=18)
    return p
def tv_set():
    """Rack baixo com TV de tela plana, caixa de som e livros (pivo: centro de tras, piso; frente +Z)."""
    p = P(); p.cham('dkwood', -0.8, 0.8, 0.08, 0.52, 0.0, 0.42, 0.01)
    for x in (-0.75, 0.75): p.box('steel_d', x - 0.02, x + 0.02, 0.0, 0.08, 0.04, 0.38)
    for (a, b) in ((-0.78, -0.27), (-0.25, 0.25), (0.27, 0.78)): p.cham('dkwood', a, b, 0.11, 0.49, 0.42, 0.44, 0.004)
    p.box('steel_d', -0.1, 0.1, 0.52, 0.54, 0.12, 0.28); p.box('steel_d', -0.02, 0.02, 0.54, 0.62, 0.185, 0.215)
    p.cham('dark', -0.62, 0.62, 0.6, 1.32, 0.18, 0.22, 0.006); p.box('screen', -0.6, 0.6, 0.62, 1.3, 0.22, 0.222)
    p.cham('dark', -0.4, 0.4, 0.52, 0.58, 0.28, 0.36, 0.01)
    for i, m in enumerate(('book', 'book2', 'cushion', 'book')): p.box(m, 0.4 + i * 0.05, 0.44 + i * 0.05, 0.52, 0.76 - i * 0.02, 0.1, 0.3)
    return p
def coffee_table():
    p = P(); p.cham('wood', -0.55, 0.55, 0.38, 0.42, -0.3, 0.3, 0.01); p.box('wood', -0.5, 0.5, 0.1, 0.12, -0.25, 0.25)
    for (x, z) in ((-0.5, -0.25), (0.5, -0.25), (-0.5, 0.25), (0.5, 0.25)): p.box('dkwood', x - 0.025, x + 0.025, 0.0, 0.38, z - 0.025, z + 0.025)
    p.box('book2', -0.3, 0.0, 0.42, 0.45, -0.1, 0.12); lathe(p, 'pot', [(0.0, 0.42), (0.06, 0.42), (0.08, 0.5), (0.0, 0.5)], 0.25, 0.0, sec=12)
    return p
def floor_lamp():
    p = P(); p.cyl('steel_d', 0.16, 0.0, 0.02, 0, 0, 16); seg_cyl(p, 'steel_d', (0, 0.02, 0), (0, 1.5, 0), 0.012, 6)
    lathe(p, 'curtain', [(0.18, 1.35), (0.14, 1.62), (0.13, 1.62), (0.17, 1.35)], sec=18); p.sphere('lamp_glass', 0.05, 0, 1.45, 0, 1)
    return p
def rug(x0, x1, z0, z1, mat='rug'):
    p = P(); p.box(mat, x0, x1, 0.0, 0.008, z0, z1); p.box('cushion', x0 + 0.08, x1 - 0.08, 0.008, 0.009, z0 + 0.08, z0 + 0.14); p.box('cushion', x0 + 0.08, x1 - 0.08, 0.008, 0.009, z1 - 0.14, z1 - 0.08)
    return p
def wall_art(w=0.8, h=0.6, seed=1):
    """Quadro abstrato (pivo: centro, face da parede; +Z): moldura e manchas de cor, sem nenhum texto."""
    p = P(); p.box('dkwood', -w / 2, w / 2, -h / 2, h / 2, 0.0, 0.03); p.box('paper', -w / 2 + 0.04, w / 2 - 0.04, -h / 2 + 0.04, h / 2 - 0.04, 0.03, 0.032)
    rng = np.random.default_rng(seed)
    for k, m in enumerate(('blue', 'cushion', 'leaf2', 'rug')):
        cx = rng.uniform(-w / 2 + 0.15, w / 2 - 0.15); cy = rng.uniform(-h / 2 + 0.12, h / 2 - 0.12); r = rng.uniform(0.05, 0.12)
        m_ = trimesh.creation.cylinder(radius=r, height=0.002, sections=16); m_.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m_.apply_translation([cx, cy, 0.033 + 0.001 * k]); p.add(m, m_)
    return p
def bed(w=1.6, L1=2.05, mat='bed_b'):
    """Cama (pivo: centro da cabeceira, piso; pes para +Z): estrado de madeira, colchao, edredom com dobra, 2 travesseiros e
    cabeceira estofada."""
    p = P(); x = w / 2
    p.cham('dkwood', -x - 0.03, x + 0.03, 0.08, 0.32, 0.05, L1 + 0.05, 0.01)
    for (a, c) in ((-x, 0.1), (x - 0.05, 0.1), (-x, L1), (x - 0.05, L1)): p.box('dkwood', a, a + 0.05, 0.0, 0.08, c - 0.05, c)
    p.cham('bed_w', -x, x, 0.32, 0.56, 0.08, L1, 0.04)
    p.cham(mat, -x - 0.02, x + 0.02, 0.4, 0.6, 0.6, L1 + 0.02, 0.05); p.cham('bed_w', -x - 0.015, x + 0.015, 0.56, 0.6, 0.45, 0.62, 0.03)
    for s in ((-1, 1) if w > 1.2 else (0,)):
        cx = s * x / 2 if w > 1.2 else 0.0; p.cham('bed_w', cx - 0.33, cx + 0.33, 0.56, 0.7, 0.12, 0.48, 0.06)
    p.cham('fabric2' if mat != 'bed_g' else 'fabric_g', -x - 0.04, x + 0.04, 0.2, 1.15, 0.0, 0.06, 0.03)
    return p
def nightstand(lamp=True):
    p = P(); p.cham('wood', -0.24, 0.24, 0.06, 0.58, 0.0, 0.4, 0.008)
    for x in (-0.22, 0.22): p.box('dkwood', x - 0.02, x + 0.02, 0.0, 0.06, 0.02, 0.38)
    for (y0, y1) in ((0.08, 0.32), (0.34, 0.56)): p.cham('wood', -0.22, 0.22, y0, y1, 0.4, 0.418, 0.004); p.box('brass', -0.04, 0.04, (y0 + y1) / 2 - 0.01, (y0 + y1) / 2 + 0.01, 0.418, 0.43)
    if lamp:
        lathe(p, 'pot', [(0.0, 0.58), (0.07, 0.58), (0.09, 0.7), (0.05, 0.82), (0.0, 0.82)], 0.0, 0.2, sec=14)
        lathe(p, 'curtain', [(0.14, 0.82), (0.1, 1.0), (0.095, 1.0), (0.135, 0.82)], 0.0, 0.2, sec=16)
    return p
def dresser(L1=1.2, tv=False):
    p = P(); x = L1 / 2; p.cham('wood', -x, x, 0.08, 0.86, 0.0, 0.48, 0.01)
    for xx in (-x + 0.04, x - 0.04): p.box('dkwood', xx - 0.03, xx + 0.03, 0.0, 0.08, 0.03, 0.45)
    for k in range(3):
        y0 = 0.1 + k * 0.25; y1 = y0 + 0.24
        for (a, b) in ((-x + 0.02, -0.003), (0.003, x - 0.02)): p.cham('wood', a, b, y0, y1, 0.48, 0.498, 0.004); p.box('brass', (a + b) / 2 - 0.06, (a + b) / 2 + 0.06, y1 - 0.06, y1 - 0.045, 0.498, 0.512)
    if tv:
        p.box('dark', -0.12, 0.12, 0.86, 0.88, 0.1, 0.3); p.box('dark', -0.02, 0.02, 0.88, 0.95, 0.18, 0.22)
        p.cham('dark', -0.5, 0.5, 0.93, 1.52, 0.18, 0.22, 0.006); p.box('screen', -0.48, 0.48, 0.95, 1.5, 0.22, 0.222)
    else:
        p.cham('mirror', -0.4, 0.4, 0.95, 1.65, 0.02, 0.05, 0.01); p.box('wood', -0.43, 0.43, 0.86, 0.95, 0.01, 0.06)
    return p
def desk():
    p = P(); p.cham('wood', -0.6, 0.6, 0.72, 0.75, 0.0, 0.6, 0.006)
    for x in (-0.57, 0.57): p.box('steel_d', x - 0.02, x + 0.02, 0.0, 0.72, 0.03, 0.57)
    p.box('steel_d', -0.55, 0.55, 0.62, 0.68, 0.03, 0.05)
    p.cham('dark', -0.17, 0.17, 0.75, 0.77, 0.25, 0.48, 0.005); p.cham('dark', -0.17, 0.17, 0.77, 0.99, 0.24, 0.26, 0.004)
    lathe(p, 'steel_d', [(0.0, 0.75), (0.07, 0.75), (0.07, 0.76), (0.0, 0.76)], 0.45, 0.12, sec=12); seg_cyl(p, 'steel_d', (0.45, 0.76, 0.12), (0.42, 1.12, 0.2), 0.008, 6)
    p.hull('steel_d', [(0.42 + dx, 1.12 + dy, 0.2 + dz) for dx in (-0.06, 0.06) for dy in (-0.03, 0.03) for dz in (0.0, 0.12)])
    return p
def wardrobe2(w=1.0):
    """Guarda-roupa de 2 portas (pivo: centro de tras, piso; frente +Z)."""
    p = P(); x = w / 2; p.cham('wood', -x, x, 0.06, 2.1, 0.0, 0.58, 0.01); p.box('dkwood', -x + 0.02, x - 0.02, 0.0, 0.06, 0.02, 0.55)
    for (a, b, hx) in ((-x + 0.01, -0.003, -0.05), (0.003, x - 0.01, 0.05)): p.cham('wood', a, b, 0.08, 2.08, 0.58, 0.6, 0.004); p.box('brass', hx - 0.01, hx + 0.01, 0.9, 1.3, 0.6, 0.625)
    return p
def closet_shelves(L1):
    """Prateleira com cabideiro e roupas penduradas (pivo: canto de tras esquerdo, piso; frente +Z)."""
    p = P(); p.box('trim', 0.0, L1, 1.7, 1.72, 0.0, 0.4); seg_cyl(p, 'chrome', (0.02, 1.62, 0.3), (L1 - 0.02, 1.62, 0.3), 0.012, 8)
    for x in (0.02, L1 - 0.02): p.box('trim', x - 0.01, x + 0.01, 1.55, 1.72, 0.0, 0.4)
    cols = ('fabric2', 'bed_b', 'cushion', 'paper', 'fabric_t', 'dark', 'bed_g')
    for i, x in enumerate(np.arange(0.12, L1 - 0.1, 0.11)):
        p.box(cols[i % len(cols)], x - 0.02, x + 0.02, 0.85 + 0.12 * (i % 3), 1.58, 0.1, 0.5)
    for i, x in enumerate(np.arange(0.1, L1 - 0.15, 0.3)): p.box(cols[(i + 2) % len(cols)], x, x + 0.22, 1.72, 1.8, 0.05, 0.35)
    for i, x in enumerate(np.arange(0.1, L1 - 0.2, 0.32)): p.cham('dark', x, x + 0.26, 0.0, 0.1, 0.05, 0.35, 0.01)
    return p
def bathtub():
    """Banheira de 1,5 m com saia (pivo: canto de tras esquerdo, piso; frente +Z), revestimento de azulejo nas 3 paredes,
    misturador, chuveiro, varao e cortina."""
    p = P(); L1, d, h = 1.54, 0.76, 0.5
    p.box('porcelain', 0.0, L1, 0.0, 0.05, 0.0, d); p.box('porcelain', 0.0, L1, 0.05, h, d - 0.06, d)
    p.box('porcelain', 0.0, 0.08, 0.05, h, 0.0, d - 0.06); p.box('porcelain', L1 - 0.08, L1, 0.05, h, 0.0, d - 0.06); p.box('porcelain', 0.08, L1 - 0.08, 0.05, h, 0.0, 0.06)
    p.box('porcelain', 0.08, L1 - 0.08, 0.05, 0.08, 0.06, d - 0.06); p.cyl('chrome', 0.03, 0.08, 0.083, 0.2, d / 2, 10)
    # azulejo (fundo e lados), da borda ate 2,0 m
    p.box('tile_w', 0.0, L1, h, 2.0, 0.0, 0.008); p.box('tile_w', 0.0, 0.008, h, 2.0, 0.008, d); p.box('tile_w', L1 - 0.008, L1, h, 2.0, 0.008, d)
    for y in np.arange(h + 0.15, 2.0, 0.15): p.box('ctop', 0.0, L1, y - 0.002, y, 0.008, 0.009)
    x = 0.008; p.cham('chrome', x, x + 0.01, 1.0, 1.2, d / 2 - 0.08, d / 2 + 0.08, 0.004); disc_x(p, 'chrome', 0.03, x + 0.01, x + 0.06, 1.1, d / 2, 12)
    seg_cyl(p, 'chrome', (x, 1.85, d / 2), (x + 0.2, 1.8, d / 2), 0.012, 8); lathe(p, 'chrome', [(0.0, 1.76), (0.05, 1.76), (0.03, 1.8), (0.0, 1.8)], x + 0.2, d / 2, sec=12)
    seg_cyl(p, 'chrome', (x, 0.42, d / 2), (x + 0.14, 0.42, d / 2), 0.014, 8)
    seg_cyl(p, 'chrome', (0.01, 1.95, d - 0.04), (L1 - 0.01, 1.95, d - 0.04), 0.012, 8)
    for i in range(7): xa = 0.05 + i * 0.06; p.box('curtain', xa, xa + 0.055, 0.6, 1.93, d - 0.045 + (0.012 if i % 2 else 0.0), d - 0.035 + (0.012 if i % 2 else 0.0))
    return p
def clawfoot_tub():
    """Banheira de pes de ferro esmaltado (pivo: canto de tras esquerdo, piso; frente +Z): casco oval com borda rolada, 4 pes
    de garra, torneira de ganso, cano do chuveiro com aro da cortina e cortina, azulejo de metro nas paredes ate 1,2 m."""
    p = P(); L1, d = 1.6, 0.78; cx, cz = L1 / 2 + 0.04, d / 2 + 0.04
    def ring(a, b, y): return [(cx + a * math.cos(t), y, cz + b * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
    outer = trimesh.convex.convex_hull(np.array(ring(0.66, 0.3, 0.16) + ring(0.76, 0.36, 0.4) + ring(0.8, 0.38, 0.6), float))
    inner = trimesh.convex.convex_hull(np.array(ring(0.58, 0.24, 0.24) + ring(0.7, 0.31, 0.45) + ring(0.74, 0.33, 0.7), float))
    try: body = trimesh.boolean.difference([outer, inner], engine='manifold')
    except Exception: body = outer
    p.add('porcelain', body)
    rim = Point(0, 0).buffer(1.0, 28); r0 = affinity.scale(rim, 0.82, 0.4).difference(affinity.scale(rim, 0.74, 0.33))
    ext_y(p, 'porcelain', affinity.translate(r0, cx, cz), 0.6, 0.64)
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = cx + sx * 0.5, cz + sz * 0.16
            seg_cyl(p, 'brass', (x, 0.2, z), (x + sx * 0.04, 0.04, z + sz * 0.03), 0.03, 8); p.sphere('brass', 0.035, x + sx * 0.045, 0.035, z + sz * 0.035, 1)
    xt = cx - 0.62; seg_cyl(p, 'chrome', (xt - 0.12, 0.0, cz), (xt - 0.12, 0.75, cz), 0.014, 8); seg_cyl(p, 'chrome', (xt - 0.12, 0.75, cz), (xt - 0.02, 0.72, cz), 0.012, 8)
    seg_cyl(p, 'chrome', (xt - 0.12, 0.75, cz), (xt - 0.12, 1.95, cz), 0.012, 8); seg_cyl(p, 'chrome', (xt - 0.12, 1.95, cz), (xt + 0.05, 1.95, cz), 0.012, 8)
    lathe(p, 'chrome', [(0.0, 1.88), (0.07, 1.88), (0.03, 1.94), (0.0, 1.94)], xt + 0.05, cz, sec=14)
    ring_ = affinity.scale(rim, 0.86, 0.44).difference(affinity.scale(rim, 0.84, 0.42)); ext_y(p, 'chrome', affinity.translate(ring_, cx, cz), 2.0, 2.02)
    seg_cyl(p, 'chrome', (cx, 2.02, cz), (cx, CH - 0.002, cz), 0.008, 6)
    for k in range(16):
        t = math.pi * 0.15 + k * math.pi * 0.7 / 15; x = cx + 0.85 * math.cos(t); z = cz + 0.43 * math.sin(t)
        p.box('curtain', x - 0.06, x + 0.06, 0.7, 1.98, z - 0.006 + (0.02 if k % 2 else 0.0), z + 0.006 + (0.02 if k % 2 else 0.0))
    # azulejo de metro (7,5 x 15) ate 1,2 m nas duas paredes, com friso
    p.box('tile_w', 0.0, L1 + 0.1, 0.1, 1.2, 0.0, 0.008); p.box('tile_w', 0.0, 0.008, 0.1, 1.2, 0.008, d + 0.1)
    for y in np.arange(0.175, 1.2, 0.075): p.box('ctop', 0.008, L1 + 0.1, y - 0.0015, y, 0.008, 0.0088); p.box('ctop', 0.008, 0.0088, y - 0.0015, y, 0.0088, d + 0.1)
    p.box('tile_w', 0.0, L1 + 0.12, 1.2, 1.24, 0.0, 0.02); p.box('tile_w', 0.0, 0.02, 1.2, 1.24, 0.02, d + 0.12)
    return p
def radiator(n=10):
    """Radiador de colunas de ferro fundido (pivo: centro de tras, piso; frente +Z) com pes, registro e cano no piso."""
    p = P(); w = 0.065; x0 = -n * w / 2
    for i in range(n):
        a = x0 + i * w + 0.004; b = a + w - 0.008
        for (z0, z1) in ((0.05, 0.11), (0.13, 0.19)): p.cham('radiator', a, b, 0.12, 0.72, z0, z1, 0.012)
        p.box('radiator', a + 0.005, b - 0.005, 0.14, 0.7, 0.11, 0.13)
    for y in (0.16, 0.68): seg_cyl(p, 'radiator', (x0, y, 0.12), (-x0, y, 0.12), 0.022, 8)
    for x in (x0 + 0.04, -x0 - 0.04): p.box('radiator', x - 0.025, x + 0.025, 0.0, 0.12, 0.08, 0.16)
    seg_cyl(p, 'brass', (-x0, 0.16, 0.12), (-x0 + 0.08, 0.16, 0.12), 0.016, 8); seg_cyl(p, 'brass', (-x0 + 0.08, 0.16, 0.12), (-x0 + 0.08, 0.0, 0.12), 0.016, 8)
    disc_x(p, 'dark', 0.04, -x0 + 0.06, -x0 + 0.1, 0.24, 0.12, 12); seg_cyl(p, 'brass', (-x0 + 0.08, 0.16, 0.12), (-x0 + 0.08, 0.24, 0.12), 0.012, 6)
    return p
def vanity(L1=1.0):
    """Gabinete com tampo e cuba oval, torneira, espelho e luminaria (pivo: canto de tras esquerdo, piso; frente +Z)."""
    p = P(); d = 0.55; p.box('dark', 0.0, L1, 0.002, 0.1, 0.0, d - 0.08); p.box('cab', 0.0, L1, 0.1, 0.8, 0.0, d - 0.02)
    for (a, b) in ((0.003, L1 / 2 - 0.002), (L1 / 2 + 0.002, L1 - 0.003)): p.cham('cab', a, b, 0.12, 0.78, d - 0.02, d, 0.004); hx = b - 0.04 if a < 0.01 else a + 0.04; p.box('chrome', hx - 0.008, hx + 0.008, 0.6, 0.72, d, d + 0.025)
    xm = L1 / 2; ell = Point(xm, d / 2).buffer(1.0, 24); ell = affinity.scale(ell, 0.2, 0.15)
    ext_y(p, 'porcelain', sbox(0.0, 0.0, L1, d + 0.02).difference(ell), 0.8, 0.83); p.box('porcelain', 0.0, L1, 0.83, 0.93, 0.0, 0.012)
    m = trimesh.creation.cylinder(radius=1.0, height=0.12, sections=24); m.apply_transform(np.diag([0.2, 1, 0.15, 1])); m.apply_translation([xm, 0.75, d / 2]); p.add('porcelain', m)
    m = trimesh.creation.cylinder(radius=1.0, height=0.004, sections=24); m.apply_transform(np.diag([0.17, 1, 0.12, 1])); m.apply_translation([xm, 0.812, d / 2]); p.add('chrome', m)
    p.cyl('chrome', 0.022, 0.83, 0.86, xm, 0.08, 10); seg_cyl(p, 'chrome', (xm, 0.86, 0.08), (xm, 1.0, 0.08), 0.012, 8); seg_cyl(p, 'chrome', (xm, 1.0, 0.08), (xm, 0.97, 0.2), 0.01, 8)
    seg_cyl(p, 'chrome', (xm, 1.0, 0.08), (xm, 1.04, 0.02 + 0.06), 0.006, 6)
    p.cham('trim', 0.08, L1 - 0.08, 1.05, 1.85, 0.0, 0.025, 0.006); p.box('mirror', 0.11, L1 - 0.11, 1.08, 1.82, 0.025, 0.028)
    p.box('chrome', 0.15, L1 - 0.15, 1.92, 1.98, 0.0, 0.07)
    for x in np.linspace(0.25, L1 - 0.25, 3): p.sphere('lamp_glass', 0.04, x, 1.95, 0.09, 1)
    lathe(p, 'blue', [(0.0, 0.83), (0.03, 0.83), (0.03, 0.98), (0.012, 1.0), (0.0, 1.02)], 0.15, 0.12, sec=10)
    return p
def washer_dryer():
    """Lavadora e secadora empilhadas (pivo: centro de tras, piso; frente +Z)."""
    p = P(); x = 0.3
    for (y0, y1) in ((0.0, 0.86), (0.88, 1.74)):
        p.cham('appl', -x, x, y0, y1, 0.0, 0.62, 0.012); p.box('appl_d', -x + 0.03, x - 0.03, y1 - 0.12, y1 - 0.03, 0.62, 0.624)
        disc_z(p, 'chrome', 0.2, 0.62, 0.64, 0.0, y0 + 0.4, 24); disc_z(p, 'glass', 0.15, 0.64, 0.645, 0.0, y0 + 0.4, 24)
        for k in range(2): disc_z(p, 'dark', 0.018, 0.624, 0.64, 0.18 - k * 0.08, y1 - 0.075, 10)
    p.box('steel', -0.28, 0.28, 0.86, 0.88, 0.02, 0.6)
    return p
def towel_bar(L1=0.5, y=1.25, mat='bed_b'):
    """Toalheiro de barra com toalha (pivo: centro, piso, face da parede; +Z)."""
    p = P(); x = L1 / 2; seg_cyl(p, 'chrome', (-x, y, 0.06), (x, y, 0.06), 0.01, 6)
    for xx in (-x, x): seg_cyl(p, 'chrome', (xx, y, 0.0), (xx, y, 0.06), 0.01, 6)
    p.box(mat, -x + 0.06, x - 0.06, y - 0.4, y + 0.012, 0.05, 0.072); return p
def apartment():
    """Apartamento da direita mobiliado (moldura do predio, pivo: piso). Sala, copa, cozinha, quarto de casal, quarto 2,
    banheiro com banheira de pes e closet, com radiadores embaixo das janelas. O da esquerda e o espelho."""
    p = kitchen(); p.merge(dining_set())
    zf = ZB + TP / 2
    # sala: TV na parede do hall, sofa de frente, poltrona, mesa de centro, tapete, abajur, quadro e planta
    place(p, tv_set(), HX + TD / 2, 0.0, 2.6, 90)
    place(p, sofa(3, 'fabric_g'), 5.9, 0.0, 2.6, -90)
    place(p, sofa(1, 'fabric_t'), 6.75, 0.0, 1.15, -60)
    place(p, coffee_table(), 4.0, 0.0, 2.6, 90)
    place(p, rug(-1.2, 1.2, -0.9, 0.9), 4.0, 0.0, 2.6, 90)
    place(p, floor_lamp(), 6.25, 0.0, 4.15); place(p, plant(1.3), 2.55, 0.0, 0.95)
    place(p, wall_art(0.9, 0.6, 3), 6.5, 1.55, zf, 0)
    # quarto de casal: cama encostada na parede x = 7,02, criados, comoda com TV, cortina
    xm0 = 6.96 + TP / 2
    place(p, bed(1.6, 2.05, 'bed_b'), xm0, 0.0, -2.0, 90)
    for z in (-3.12, -0.88): place(p, nightstand(), xm0, 0.0, z, 90)
    place(p, dresser(1.3, True), BX - T, 0.0, -0.9, -90)
    place(p, wall_art(1.1, 0.5, 7), xm0, 1.55, -2.0, 90)
    # quarto 2: cama de solteiro, criado, escrivaninha embaixo da janela, cadeira, guarda-roupa
    place(p, bed(1.0, 1.95, 'bed_g'), TD / 2, 0.0, -3.9, 90); place(p, nightstand(), TD / 2, 0.0, -2.95, 90)
    place(p, desk(), 2.1, 0.0, -BZ + T, 0); place(p, office_chair('fabric_t'), 2.1, 0.0, -4.65, 180)
    place(p, wardrobe2(1.1), 4.3, 0.0, -1.3, -90)
    place(p, wall_art(0.6, 0.8, 11), TD / 2, 1.5, -1.6, 90)
    # banheiro: banheira no fundo, gabinete na parede x = 4,42, vaso, lavadora e secadora, toalheiro
    place(p, clawfoot_tub(), 4.42, 0.0, -3.0)
    place(p, vanity(1.0), 4.42, 0.0, -0.45, 90)
    place(p, wc(), 6.9, 0.0, -1.45, -90)
    place(p, washer_dryer(), 6.9, 0.0, 0.05, -90)
    place(p, towel_bar(0.45), 4.8, 0.0, ZB - TP / 2, 180)
    p.cham('trim', 6.34, 6.9, 1.6, 2.1, -2.95, -2.65, 0.008)                                 # armario sobre o vaso (lado)
    seg_cyl(p, 'chrome', (6.9, 0.75, -0.95), (6.84, 0.75, -0.95), 0.01, 6); disc_x(p, 'paper', 0.055, 6.74, 6.84, 0.72, -0.95, 12)
    # closet: prateleiras nas 2 paredes
    place(p, closet_shelves(2.4), 4.45, 0.0, -BZ + T)
    place(p, closet_shelves(1.4), 4.42, 0.0, -3.5, 90)
    # radiadores de ferro embaixo das janelas (sala, copa e quarto de casal)
    for (x, z, r, n) in ((3.4, BZ - T, 180, 10), (5.7, BZ - T, 180, 10), (BX - T, 4.8, -90, 8), (BX - T, -2.8, -90, 10)):
        place(p, radiator(n), x, 0.0, z, r)
    return p
def door_unit(w=DW - 0.02, h=DH - 0.012, t=0.045):
    """Porta de entrada do apartamento (pivo: dobradica, embaixo): 6 almofadas, olho magico, fechadura tetra, macaneta de
    alavanca e numero em pictograma (pontos)."""
    p = P(); slab = tbox(0, w, 0, h, -t / 2, t / 2); cut = []
    rows = [(0.16, 0.72), (0.8, 1.5), (1.58, h - 0.14)]
    for (y0, y1) in rows:
        for (a, b) in ((0.12, w / 2 - 0.04), (w / 2 + 0.04, w - 0.12)):
            for z in (t / 2, -t / 2): cut.append(tbox(a, b, y0, y1, z - 0.008, z + 0.008))
    p.add('door', bl_detail(slab, cut, bevel=0.004, segments=2))
    for z in (1, -1):
        zz = z * t / 2
        p.cham('chrome', w - 0.1, w - 0.06, 0.92, 1.12, *sorted((zz, zz + z * 0.008)), 0.003)
        seg_cyl(p, 'chrome', (w - 0.08, 1.0, zz), (w - 0.08, 1.0, zz + z * 0.05), 0.011, 6); seg_cyl(p, 'chrome', (w - 0.08, 1.0, zz + z * 0.05), (w - 0.21, 1.0, zz + z * 0.05), 0.011, 6)
        disc_z(p, 'chrome', 0.025, *sorted((zz, zz + z * 0.012)), w - 0.08, 1.25, 12)
        disc_z(p, 'chrome', 0.012, *sorted((zz, zz + z * 0.01)), w / 2, 1.55, 10)
    for i in range(3): p.box('brass', w / 2 - 0.05 + i * 0.04, w / 2 - 0.03 + i * 0.04, 1.68, 1.7, t / 2, t / 2 + 0.006)
    for yy in (0.25, h / 2, h - 0.25): p.cyl('chrome', 0.008, yy - 0.06, yy + 0.06, -0.004, t / 2 + 0.002, 8)
    return p
# ============================================================================ escadas de incendio (moldura do predio, pivo: piso do andar k)
FE_X = (2.6, 7.4); FE_D = 1.45; FE_Y = 0.35                       # plataforma da direita: x 2,6..7,4, sai 1,45 m da fachada, 35 cm acima do piso
FE_B = (0.86, 1.38)                                               # faixa do lance (a de dentro e o passeio junto a parede)
FE_N = 12; FE_R = H / FE_N; FE_T = 0.175; FE_RUN = (FE_N - 1) * FE_T
def fe_dir(k): return 1 if k % 2 == 0 else -1                     # sentido em que sobe o lance que chega no andar k
def fe_top(k):
    d = fe_dir(k); return (FE_X[1] - 0.5) if d > 0 else (FE_X[0] + 0.5)
def fe_hatch(k):
    if k == 1: return (2.8, 3.55)
    xt = fe_top(k); return tuple(sorted((xt - fe_dir(k) * FE_RUN * 0.78, xt)))
def fe_flight(p, k, y0):
    """Lance de aco que sobe da plataforma de baixo (y0) ate a do andar k: banzos de perfil U, degraus de chapa xadrez com
    focinho, corrimao do lado do passeio."""
    d = fe_dir(k); xt = fe_top(k); xb = xt - d * FE_RUN; z0, z1 = BZ + FE_B[0], BZ + FE_B[1]
    X = lambda u: xb + d * u
    for (z, zz) in ((z0, z0 + 0.012), (z1 - 0.012, z1)):
        p.hull('steel_d', [(X(u), y0 + y, zc) for (u, y) in ((-0.12, -0.04), (-0.12, 0.16), (FE_RUN + 0.02, H - 0.03), (FE_RUN + 0.02, H - 0.2)) for zc in (z, zz)])
    for i in range(1, FE_N):
        u0, u1 = (i - 1) * FE_T, i * FE_T + 0.015; yt = y0 + i * FE_R
        p.box('steel_d', *sorted((X(u0), X(u1))), yt - 0.012, yt, z0 + 0.012, z1 - 0.012)
        p.box('steel_d', *sorted((X(u1 - 0.02), X(u1))), yt - 0.05, yt - 0.012, z0 + 0.012, z1 - 0.012)
        for j in range(3): zc = z0 + 0.1 + j * (z1 - z0 - 0.2) / 2; p.box('dark', *sorted((X(u0 + 0.04), X(u1 - 0.05))), yt - 0.008, yt + 0.001, zc - 0.03, zc + 0.03)
    yr = lambda u: y0 + 0.92 + FE_R * (1 + u / FE_T)
    za = z0 - 0.02
    seg_cyl(p, 'steel_d', (X(0.05), yr(0.05), za), (X(FE_RUN - 0.05), yr(FE_RUN - 0.05), za), 0.02, 8)
    for u in (0.05, FE_RUN * 0.5, FE_RUN - 0.05):
        y = y0 + FE_R * (1 + u / FE_T); seg_cyl(p, 'steel_d', (X(u), y - 0.08, za), (X(u), yr(u), za), 0.014, 6)
def fe_platform(p, k):
    """Plataforma de grade: perfis em balanco engastados na parede, cantoneira de borda, barras do piso (alcapao no lance que
    chega), guarda-corpo com corrimao chato, travessa e balaustres, tirantes ate a parede."""
    xa, xb = FE_X; y = FE_Y; h0, h1 = fe_hatch(k); z0, z1 = BZ + FE_B[0], BZ + FE_B[1]
    for x in (xa + 0.06, (xa + xb) / 2, xb - 0.06):
        p.box('steel_d', x - 0.035, x + 0.035, y - 0.18, y - 0.04, BZ - 0.1, BZ + FE_D - 0.02)
        if k == 1:   # no 1o andar, tirantes ate a parede (embaixo ficam os toldos)
            disc_z(p, 'steel_d', 0.05, BZ, BZ + 0.015, x, y + 1.75, 10); seg_cyl(p, 'steel_d', (x, y + 1.75, BZ + 0.01), (x, y - 0.06, BZ + FE_D - 0.04), 0.012, 6)
        else:        # misula de cantoneira embaixo do perfil
            p.hull('steel_d', [(x + dx, yy, zz) for dx in (-0.02, 0.02) for (yy, zz) in ((y - 0.18, BZ + 1.05), (y - 0.18, BZ + 1.0), (y - 0.95, BZ), (y - 0.88, BZ))])
            p.box('steel_d', x - 0.05, x + 0.05, y - 1.0, y - 0.18, BZ, BZ + 0.012)
    p.box('steel_d', xa, xb, y - 0.13, y, BZ + FE_D - 0.04, BZ + FE_D); p.box('steel_d', xa, xb, y - 0.13, y - 0.045, BZ + 0.02, BZ + 0.06)
    for x in (xa, xb): p.box('steel_d', *sorted((x, x + (0.04 if x == xa else -0.04))), y - 0.13, y - 0.045, BZ + 0.06, BZ + FE_D - 0.04)
    zz = BZ + 0.07
    while zz < BZ + FE_D - 0.06:
        za, zb_ = zz, zz + 0.03
        inb = za > z0 - 0.01 and zb_ < z1 + 0.01
        for (u, v) in (segs_excl([(h0, h1)], xa + 0.04, xb - 0.04) if inb else [(xa + 0.04, xb - 0.04)]): p.box('steel_d', u, v, y - 0.04, y - 0.004, za, zb_)
        zz += 0.052
    for x in (h0, h1):
        if xa + 0.05 < x < xb - 0.05: p.box('steel_d', x - 0.02, x + 0.02, y - 0.045, y, z0 - 0.02, z1 + 0.02)
    # guarda-corpo (frente e pontas)
    zf = BZ + FE_D - 0.02
    for (a, b) in ((xa, xb),):
        p.box('steel_d', a, b, y + 0.98, y + 1.02, zf - 0.025, zf + 0.025); p.box('steel_d', a, b, y + 0.1, y + 0.13, zf - 0.015, zf + 0.015)
        for x in np.arange(a + 0.1, b - 0.05, 0.11): p.box('steel_d', x - 0.008, x + 0.008, y + 0.13, y + 0.98, zf - 0.008, zf + 0.008)
    for x in (xa + 0.02, xb - 0.02):
        p.box('steel_d', x - 0.025, x + 0.025, y + 0.98, y + 1.02, BZ + 0.02, zf - 0.025); p.box('steel_d', x - 0.015, x + 0.015, y + 0.1, y + 0.13, BZ + 0.02, zf - 0.015)
        for z in np.arange(BZ + 0.12, zf - 0.05, 0.11): p.box('steel_d', x - 0.008, x + 0.008, y + 0.13, y + 0.98, z - 0.008, z + 0.008)
        p.box('steel_d', x - 0.03, x + 0.03, y - 0.15, y + 1.04, zf - 0.03, zf + 0.03)
        disc_z(p, 'steel_d', 0.05, BZ, BZ + 0.015, x, y + 1.0, 10)
    for x in np.linspace(xa + 1.2, xb - 1.2, 3): p.box('steel_d', x - 0.02, x + 0.02, y - 0.15, y + 1.0, zf - 0.018, zf + 0.018)
def fe_level(k):
    """Um andar da escada de incendio da direita: plataforma e lance que chega de baixo (andar 1: escada de descida de correr
    presa no alcapao; ultimo andar: escada de gancho ate o telhado por cima da cornija)."""
    p = Piece(); fe_platform(p, k)
    if k >= 2: fe_flight(p, k, FE_Y - H)
    if k == 1:   # escada de descida recolhida (corre nas guias)
        h0, h1 = fe_hatch(1); zc = BZ + (FE_B[0] + FE_B[1]) / 2
        for x in (h0 + 0.08, h1 - 0.08):
            p.box('steel_d', x - 0.025, x + 0.025, FE_Y - 0.95, FE_Y + 1.05, zc - 0.03, zc + 0.03)
            p.box('steel_d', x - 0.035, x + 0.035, FE_Y - 0.06, FE_Y + 1.0, zc + 0.03, zc + 0.05)
        for yy in np.arange(FE_Y - 0.85, FE_Y + 1.0, 0.3): seg_cyl(p, 'steel_d', (h0 + 0.1, yy, zc), (h1 - 0.1, yy, zc), 0.014, 6)
        p.box('steel_d', h0 + 0.05, h1 - 0.05, FE_Y + 1.02, FE_Y + 1.06, zc - 0.03, zc + 0.05)
    if k == NL - 1:   # escada de gancho
        zl = BZ + 0.95; yt = H + 1.18
        for x in (6.55, 7.05):
            seg_cyl(p, 'steel_d', (x, FE_Y, zl), (x, yt, zl), 0.02, 8); seg_cyl(p, 'steel_d', (x, yt, zl), (x, yt, BZ - 0.6), 0.02, 8); seg_cyl(p, 'steel_d', (x, yt, BZ - 0.6), (x, H + 0.04, BZ - 0.6), 0.02, 8)
            p.box('steel_d', x - 0.06, x + 0.06, H + 0.04, H + 0.055, BZ - 0.66, BZ - 0.54)
        for yy in np.arange(FE_Y + 0.3, yt - 0.1, 0.3): seg_cyl(p, 'steel_d', (6.55, yy, zl), (7.05, yy, zl), 0.012, 6)
        for yy in np.arange(H + 0.3, yt - 0.1, 0.3): seg_cyl(p, 'steel_d', (6.55, yy, BZ - 0.6), (7.05, yy, BZ - 0.6), 0.012, 6)
    return p

# ============================================================================ telhado (pivo: laje do telhado, y = 18,15)
CORN = [(0.0, -0.14), (0.07, -0.14), (0.1, -0.09), (0.1, 0.38), (0.6, 0.38), (0.6, 0.48), (0.63, 0.5), (0.63, 0.62), (0.68, 0.7), (0.72, 0.86),
        (0.74, 0.92), (0.74, 0.98), (0.0, 1.02)]
FRIEZE = [(0.0, -0.42), (0.03, -0.42), (0.03, -0.14), (0.0, -0.14)]
BRACKET = [(0.0, -0.4), (0.1, -0.4), (0.16, -0.32), (0.16, -0.12), (0.28, 0.06), (0.46, 0.2), (0.56, 0.3), (0.56, 0.38), (0.0, 0.38)]
BULK = sbox(-HX - 0.1, HZB - 0.1, HX + 0.1, BZ)                   # casa da escada no telhado (frente na fachada)
BK_H = 2.9
def cornice_run(p, L1):
    """Cornija de chapa de uma fachada (moldura local: x de -L1/2 a L1/2, face em z = 0): coroa, denticulos, misulas e friso."""
    x = L1 / 2; prof_x(p, 'cornice', -x, x, CORN); prof_x(p, 'cornice', -x, x, FRIEZE)
    n = int(round((L1 - 0.6) / 0.95)); xs = np.linspace(-x + 0.4, x - 0.4, n + 1)
    for xx in xs: prof_x(p, 'cornice', xx - 0.07, xx + 0.07, BRACKET); disc_x(p, 'cornice', 0.045, xx - 0.08, xx + 0.08, -0.3, 0.12, 12)
    for (a, b) in zip(xs[:-1], xs[1:]): p.box('cornice', a + 0.14, b - 0.14, -0.36, -0.2, 0.03, 0.045)
    for xx in np.arange(-x + 0.14, x - 0.1, 0.09): p.box('cornice', xx - 0.025, xx + 0.025, -0.08, -0.02, 0.1, 0.13)
def roof():
    """Telhado plano: manta, parapeito de tijolo com rufo e capa, cornija nas 4 fachadas com quinas em meia-esquadria, casa da
    escada com porta de chapa e antena, chamine de tijolo, respiros e caixa-d'agua de madeira numa torre de aco."""
    p = Piece(); ring = FOOT.difference(INNER)
    ext_y(p, 'roofing', INNER.difference(BULK), 0.0, 0.04)
    ext_y(p, 'brick', ring.difference(BULK), 0.0, 1.0)
    ext_y(p, 'coping', FOOT.difference(INNER.buffer(-0.04, join_style=2)).difference(BULK.buffer(0.001, join_style=2)), 1.0, 1.06)
    # rufo no pe do parapeito
    fl = INNER.difference(INNER.buffer(-0.1, join_style=2)).difference(BULK.buffer(0.1, join_style=2))
    ext_y(p, 'roofing', fl, 0.04, 0.12)
    for (L1, M) in ((2 * BX, rot_y(0, (0, 0, BZ))), (2 * BX, rot_y(180, (0, 0, -BZ))), (2 * BZ, rot_y(90, (BX, 0, 0))), (2 * BZ, rot_y(-90, (-BX, 0, 0)))):
        q = Piece(); cornice_run(q, L1); p.merge(q, M)
    for (x, z, r) in ((BX, BZ, 0), (-BX, BZ, -90), (-BX, -BZ, 180), (BX, -BZ, 90)):
        for prof in (CORN, FRIEZE): q = Piece(); mitre_pair(q, 'cornice', prof); p.merge(q, rot_y(r, (x, 0, z)))
    # casa da escada
    x0, z0, x1, z1 = BULK.bounds; t = 0.2
    hole = [(4.5, 5.4, 0.04, 2.15)]
    wall2(p, 'z', z0 + t, z1 - T, x1, x1 - t, hole, 0.0, BK_H, 'brick', 'plaster')
    wall2(p, 'z', z0 + t, z1 - T, x0, x0 + t, [], 0.0, BK_H, 'brick', 'plaster')
    wall2(p, 'x', x0, x1, z0, z0 + t, [], 0.0, BK_H, 'brick', 'plaster')
    wall2(p, 'x', x0, x1, z1, z1 - T, [], 0.0, BK_H, 'brick', 'plaster')
    for (u, v) in ((4.5, 4.55), (5.35, 5.4)): p.box('steel_d', x1 - 0.2, x1 - 0.05, 0.04, 2.15, u, v)
    p.box('steel_d', x1 - 0.2, x1 - 0.05, 2.1, 2.15, 4.55, 5.35); p.box('conc_s', x1 - t - 0.01, x1 + 0.06, 0.002, 0.05, 4.502, 5.398)
    ext_y(p, 'ceil', sbox(x0 + t, z0 + t, x1 - t, z1 - T), BK_H - 0.16, BK_H - 0.148); ext_y(p, 'conc_s', sbox(x0 + t, z0 + t, x1 - t, z1 - T), BK_H - 0.148, BK_H)
    ext_y(p, 'roofing', BULK, BK_H, BK_H + 0.04)
    ext_y(p, 'coping', BULK.buffer(0.04, join_style=2).difference(BULK.buffer(-0.2, join_style=2)), BK_H + 0.04, BK_H + 0.1)
    p.cyl('paint_w', 0.17, BK_H - 0.18, BK_H - 0.16, 0.0, 2.5, 20); lathe(p, 'lamp_glass', [(0.15, BK_H - 0.18), (0.13, BK_H - 0.22), (0.07, BK_H - 0.245), (0.0, BK_H - 0.25)], 0.0, 2.5, sec=20)
    p.merge(wall_lantern(), rot_y(90, (x1, 2.45, 4.95)))
    seg_cyl(p, 'steel', (-1.2, BK_H + 0.04, 1.2), (-1.2, BK_H + 2.2, 1.2), 0.025, 8)
    for (y, L1) in ((BK_H + 1.4, 1.2), (BK_H + 1.7, 0.9), (BK_H + 2.0, 0.6)): seg_cyl(p, 'steel', (-1.2, y, 1.2 - L1 / 2), (-1.2, y, 1.2 + L1 / 2), 0.008, 6)
    for z in (0.9, 1.5): seg_cyl(p, 'steel', (-1.2, BK_H + 1.4, z), (-1.0, BK_H + 1.4, z), 0.006, 4)
    # chamine e respiros
    p.box('brick', 7.2, 8.0, 0.0, 2.4, -BZ + T, -BZ + T + 0.6); p.cham('coping', 7.14, 8.06, 2.4, 2.48, -BZ + T - 0.06, -BZ + T + 0.66, 0.01)
    for x in (7.4, 7.8): p.cyl('conc_s', 0.1, 2.48, 2.7, x, -BZ + T + 0.3, 12)
    for (x, z) in ((5.6, -1.6), (-5.6, -1.6), (8.4, 1.2), (-8.4, 1.2)):
        p.cyl('steel_d', 0.05, 0.04, 0.6, x, z, 10); p.cyl('steel_d', 0.08, 0.04, 0.1, x, z, 10)
    p.merge(water_tank(), tr(-7.0, 0.04, -2.6))
    return p
def water_tank():
    """Caixa-d'agua de madeira (pivo: centro, laje): torre de 4 pernas de aco com contraventamento e bases de concreto, estrado
    de vigas, tanque de aduelas com 7 aros de aco, tampa conica com respiro, escada de marinheiro e canos."""
    p = Piece(); r = 1.45; y0, y1, y2 = 2.7, 2.9, 5.7
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * 1.15, sz * 1.15; p.box('conc_s', x - 0.25, x + 0.25, 0.0, 0.18, z - 0.25, z + 0.25)
            p.box('steel_d', x - 0.08, x + 0.08, 0.18, y0, z - 0.08, z + 0.08)
    for (a, b) in (((-1.15, -1.15), (1.15, -1.15)), ((1.15, -1.15), (1.15, 1.15)), ((1.15, 1.15), (-1.15, 1.15)), ((-1.15, 1.15), (-1.15, -1.15))):
        seg_cyl(p, 'steel_d', (a[0], 0.3, a[1]), (b[0], y0 - 0.1, b[1]), 0.016, 6); seg_cyl(p, 'steel_d', (a[0], y0 - 0.1, a[1]), (b[0], 0.3, b[1]), 0.016, 6)
        p.box('steel_d', *sorted((a[0], b[0])), y0 - 0.12, y0, *sorted((a[1], b[1]))) if a[0] != b[0] and False else None
    for z in (-1.15, 1.15): p.box('steel_d', -1.25, 1.25, y0 - 0.14, y0, z - 0.06, z + 0.06)
    for x in (-1.15, 1.15): p.box('steel_d', x - 0.06, x + 0.06, y0 - 0.14, y0, -1.09, 1.09)
    for x in np.linspace(-1.3, 1.3, 6): p.box('dkwood', x - 0.08, x + 0.08, y0, y1, -1.4, 1.4)
    n = 56
    for i in range(n):
        a0 = 2 * math.pi * i / n; a1 = 2 * math.pi * (i + 1) / n - 0.004
        pts = [(rr * math.cos(a), y, rr * math.sin(a)) for rr in (r, r - 0.06) for a in (a0, a1) for y in (y1, y2)]
        p.hull('tank', pts)
    for y in np.linspace(y1 + 0.25, y2 - 0.25, 7): ring_y(p, 'steel_d', r + 0.002, r + 0.025, y - 0.02, y + 0.02, 0.0, 0.0, 56)
    ext_y(p, 'dkwood', Point(0, 0).buffer(r - 0.06, 28), y2 - 0.3, y2 - 0.26)
    lathe(p, 'tank', [(r + 0.08, y2), (r + 0.08, y2 + 0.04), (0.12, y2 + 0.72), (0.0, y2 + 0.74)], sec=40)
    lathe(p, 'steel_d', [(0.0, y2 + 0.72), (0.08, y2 + 0.72), (0.08, y2 + 0.9), (0.14, y2 + 0.92), (0.0, y2 + 1.0)], sec=12)
    xl = r + 0.18
    for z in (-0.22, 0.22): seg_cyl(p, 'steel_d', (xl, 0.18, z), (xl, y2 + 0.3, z), 0.018, 6)
    for yy in np.arange(0.5, y2 + 0.2, 0.3): seg_cyl(p, 'steel_d', (xl, yy, -0.22), (xl, yy, 0.22), 0.011, 6)
    for yy in (1.5, y2 - 0.2): seg_cyl(p, 'steel_d', (xl, yy, 0.0), (r - 0.04, yy, 0.0), 0.014, 6)
    for (x, z) in ((0.4, 0.3), (-0.3, -0.5)): seg_cyl(p, 'galv', (x, 0.0, z), (x, y1 - 0.01, z), 0.06, 10)
    return p
# ============================================================================ lojas do terreo (moldura do predio, pivo: piso do terreo)
def tin_ceiling(p, poly, y=CH):
    """Forro de chapa estampada: placa lisa, quadros de 60 cm com almofada em 2 niveis e roseta, e sanca nas paredes."""
    ext_y(p, 'tin', poly, y - 0.012, y - 0.001); b = poly.bounds; s = 0.6
    for i in range(int(math.floor(b[0] / s)), int(math.ceil(b[2] / s))):
        for j in range(int(math.floor(b[1] / s)), int(math.ceil(b[3] / s))):
            q = sbox(i * s + 0.06, j * s + 0.06, (i + 1) * s - 0.06, (j + 1) * s - 0.06)
            if q.within(poly):
                ext_y(p, 'tin', q, y - 0.024, y - 0.012); ext_y(p, 'tin', q.buffer(-0.12, join_style=2), y - 0.032, y - 0.024)
                p.cyl('tin', 0.04, y - 0.04, y - 0.032, (i + 0.5) * s, (j + 0.5) * s, 10)
    ring = poly.difference(poly.buffer(-0.12, join_style=2)); ext_y(p, 'tin', ring, y - 0.13, y - 0.012)
    ext_y(p, 'tin', poly.difference(poly.buffer(-0.16, join_style=2)).difference(ring), y - 0.06, y - 0.012)
def pendant(p, x, z, y=CH):
    """Luminaria pendente de vidro leitoso (estilo escola) com haste."""
    seg_cyl(p, 'steel_d', (x, y - 0.04, z), (x, y - 0.6, z), 0.008, 6); p.cyl('steel_d', 0.05, y - 0.07, y - 0.035, x, z, 10)
    lathe(p, 'lamp_glass', [(0.06, y - 0.6), (0.16, y - 0.68), (0.19, y - 0.8), (0.17, y - 0.9), (0.0, y - 0.93)], x, z, sec=18)
def fluor(p, x, z, L1=1.2, y=CH):
    p.cham('paint_w', x - L1 / 2, x + L1 / 2, y - 0.1, y - 0.04, z - 0.12, z + 0.12, 0.01); p.box('lamp_glass', x - L1 / 2 + 0.03, x + L1 / 2 - 0.03, y - 0.104, y - 0.1, z - 0.1, z + 0.1)
    for dx in (-L1 / 2 + 0.1, L1 / 2 - 0.1): seg_cyl(p, 'steel_d', (x + dx, y - 0.04, z), (x + dx, y - 0.04 + 0.039, z), 0.004, 4)
def produce_stand():
    """Banca de frutas de madeira com 3 degraus de caixotes inclinados (pivo: centro de tras, piso; frente +Z)."""
    p = P(); x = 1.3
    for (k, (y, z0, z1)) in enumerate(((0.0, 0.0, 0.85), (0.32, 0.0, 0.55), (0.64, 0.0, 0.28))):
        p.box('dkwood', -x, x, y, y + 0.3, z0, z1)
        for i in range(5):
            a = -x + 0.03 + i * (2 * x - 0.06) / 5; b = a + (2 * x - 0.06) / 5 - 0.03; zc0 = z1 - 0.28; mat = ['food_r', 'food_y', 'leaf2', 'food_g', 'cushion'][(i + k) % 5]
            p.box('basket', a, b, y + 0.3, y + 0.38, zc0, z1 - 0.02)
            for (u, v) in ((a + 0.07, zc0 + 0.07), (b - 0.07, zc0 + 0.07), ((a + b) / 2, z1 - 0.09), (a + 0.07, z1 - 0.09), (b - 0.07, z1 - 0.09)): p.sphere(mat, 0.05, u, y + 0.42, v, 1)
    return p
def gondola(L1=4.8):
    """Gondola dupla: 3 modulos de estante de cada lado, costas de chapa e testeira na ponta (pivo: centro, piso; ao longo de Z)."""
    p = P(); n = 3; w = L1 / n
    for i in range(n):
        zc = -L1 / 2 + (i + 0.5) * w
        place(p, shelves(w - 0.02), -0.02, 0.0, zc, -90); place(p, shelves(w - 0.02), 0.02, 0.0, zc, 90)
    p.box('steel', -0.02, 0.02, 0.0, 1.95, -L1 / 2, L1 / 2)
    for s in (-1, 1): p.cham('steel', -0.44, 0.44, 0.0, 1.5, *sorted((s * L1 / 2, s * (L1 / 2 + 0.3))), 0.01); p.box('food_y', -0.3, 0.3, 1.5, 1.8, *sorted((s * (L1 / 2 + 0.2), s * (L1 / 2 + 0.22))))
    return p
def coffee_station():
    p = P(); p.cham('dkwood', -0.5, 0.5, 0.0, 0.9, 0.0, 0.55, 0.01); p.cham('ctop', -0.52, 0.52, 0.9, 0.93, 0.0, 0.58, 0.004)
    for x in (-0.25, 0.15):
        p.cham('appl_d', x - 0.14, x + 0.14, 0.93, 1.38, 0.05, 0.38, 0.01); lathe(p, 'glass', [(0.0, 0.95), (0.08, 0.95), (0.09, 1.08), (0.04, 1.12), (0.0, 1.12)], x, 0.42, sec=12)
    for k in range(3): p.cyl('paper', 0.04, 0.93, 1.05 + k * 0.004, 0.38, 0.3, 12)
    return p
def ice_box():
    p = P(); p.cham('cart_w', -0.6, 0.6, 0.0, 1.0, 0.0, 0.7, 0.012); p.box('flag_b', -0.6, 0.6, 0.6, 0.9, 0.7, 0.705)
    for x in (-0.3, 0.3): p.box('chrome', x - 0.05, x + 0.05, 0.92, 0.95, 0.7, 0.74)
    return p
def mop_sink():
    p = P(); p.cham('conc_s', -0.35, 0.35, 0.0, 0.3, 0.0, 0.6, 0.02); p.box('dark', -0.29, 0.29, 0.26, 0.302, 0.06, 0.54)
    seg_cyl(p, 'chrome', (0.0, 0.9, 0.02), (0.0, 0.9, 0.15), 0.012, 6); seg_cyl(p, 'chrome', (0.0, 0.9, 0.15), (0.0, 0.8, 0.15), 0.01, 6)
    seg_cyl(p, 'wood', (0.25, 0.0, 0.05), (0.32, 1.4, 0.03), 0.014, 6); p.box('dark', -0.12, 0.12, 0.0, 0.2, 0.64, 0.84)
    return p
def water_heater(r=0.28, h=1.5):
    p = P(); p.cyl('paint_w', r, 0.04, h, 0, 0, 18); lathe(p, 'paint_w', [(r, h), (r - 0.04, h + 0.06), (0.0, h + 0.07)], sec=18)
    for x in (-0.1, 0.1): seg_cyl(p, 'brass', (x, h + 0.05, 0.0), (x, CH - 0.01, 0.0), 0.014, 6)
    p.cyl('dark', r * 0.9, 0.0, 0.04, 0, 0, 14); p.box('appl_d', -0.08, 0.08, 0.2, 0.36, r - 0.02, r + 0.04); return p
def wall_sink():
    p = P(); p.cham('porcelain', -0.25, 0.25, 0.68, 0.82, 0.0, 0.4, 0.03); p.box('dark', -0.18, 0.18, 0.818, 0.822, 0.08, 0.32)
    seg_cyl(p, 'chrome', (0.0, 0.82, 0.05), (0.0, 0.95, 0.05), 0.012, 6); seg_cyl(p, 'chrome', (0.0, 0.95, 0.05), (0.0, 0.92, 0.14), 0.01, 6)
    p.cham('chrome', -0.22, 0.22, 1.1, 1.6, 0.0, 0.015, 0.004); p.box('mirror', -0.2, 0.2, 1.12, 1.58, 0.015, 0.018); return p
def back_room(p, s):
    """Deposito e lavabo de uma loja (coordenadas da loja da direita; s = -1 espelha)."""
    def pl(q, x, y, z, r): place(p, q, s * x, y, z, r if s > 0 else -r)
    for x in (4.6, 6.3, 8.0): pl(shelves(1.6), x, 0.0, -BZ + T, 0)
    pl(shelves(1.6), BX - T, 0.0, -4.2, -90)
    for (x, z, n) in ((10.5, -3.1, 3), (11.0, -3.5, 2)):
        for k in range(n): pl(Piece().box('basket', -0.25, 0.25, 0.0, 0.32, -0.2, 0.2), x, k * 0.32, z, 15 * k)
    pl(mop_sink(), 3.66 + 0.06 + 0.45, 0.0, -2.45 - TP / 2, 180)
    pl(water_heater(), 4.35, 0.0, -3.6, 0)
    pl(wc(), 2.1 + 0.02, 0.0, -4.9, 90); pl(wall_sink(), 2.82, 0.0, -BZ + T, 0)
    pl(towel_bar(0.4, 1.1, 'paper'), 3.5 - 0.06, 0.0, -3.4, -90)
    for (x, z) in ((7.0, -4.1), (2.82, -4.1)): p.cyl('paint_w', 0.12, CH - 0.03, CH - 0.002, s * x, z, 14); p.sphere('lamp_glass', 0.08, s * x, CH - 0.06, z, 1)
def shop_ceil():
    """Forros de chapa estampada das 2 lojas, com pendentes na mercearia e calhas fluorescentes na lavanderia (pivo: piso do
    terreo; fica com o 1o andar para a vista de cima do terreo)."""
    p = P(); tin_ceiling(p, SHOP_F); tin_ceiling(p, mx(SHOP_F))
    for x in (4.2, 7.0, 9.8):
        for z in (0.2, 3.6): pendant(p, x, z)
    for x in (-4.2, -7.0, -9.8):
        for z in (-0.5, 1.8, 4.1): fluor(p, x, z)
    return p
def shop_grocery():
    """Mercearia (loja da direita): 3 gondolas, geladeiras no fundo, estantes na parede do hall,
    balcao com caixa e cafe, banca de frutas na vitrine, freezer de gelo, deposito e lavabo."""
    p = P()
    for x in (4.3, 6.1, 7.9): place(p, gondola(4.2), x, 0.0, 0.85)
    for i in range(7): place(p, fridge(), 3.0 + i * 0.82, 0.0, -2.45 + TP / 2 + 0.01, 0)
    for z in (-1.4, 0.3, 2.0): place(p, shelves(1.6), HX + TD / 2, 0.0, z, 90)
    place(p, counter_k(2.6), 10.1, 0.0, 2.55, -90); place(p, register(), 9.8, 0.92, 3.3, 90)
    p.cham('dark', 9.55, 9.75, 0.92, 1.25, 1.6, 2.0, 0.01); p.box('screen', 9.548, 9.552, 0.98, 1.2, 1.64, 1.96)
    place(p, shelves(1.6), BX - T, 0.0, -1.0, -90); place(p, coffee_station(), 10.6, 0.0, -2.45 + TP / 2, 0)
    place(p, produce_stand(), 4.85, 0.0, BZ - T - 0.95, 0)
    place(p, ice_box(), 9.4, 0.0, BZ - T - 0.75, 0)
    place(p, office_chair('vinyl'), 11.0, 0.0, 3.0, 90)
    back_room(p, 1)
    return p
def washer_fl():
    """Lavadora de abertura frontal de lavanderia (pivo: centro de tras, piso; frente +Z) com painel de moedas sem texto."""
    p = P(); p.cham('washer', -0.34, 0.34, 0.0, 1.0, 0.0, 0.72, 0.015); p.box('dark', -0.32, 0.32, 0.0, 0.08, 0.68, 0.73)
    disc_z(p, 'chrome', 0.24, 0.72, 0.745, 0.0, 0.5, 26); disc_z(p, 'glass', 0.19, 0.745, 0.752, 0.0, 0.5, 26); disc_z(p, 'dark', 0.15, 0.7, 0.744, 0.0, 0.5, 20)
    p.cham('steel', -0.3, 0.3, 0.82, 0.96, 0.72, 0.74, 0.006)
    for x in (-0.18, 0.0): p.box('dark', x - 0.04, x + 0.04, 0.86, 0.92, 0.74, 0.748)
    p.box('screen_g', 0.12, 0.24, 0.87, 0.91, 0.74, 0.745); p.box('chrome', 0.27, 0.31, 0.45, 0.6, 0.72, 0.76)
    return p
def dryer_stack():
    """Secadoras de lavanderia empilhadas (2 tambores, pivo: centro de tras, piso; frente +Z)."""
    p = P(); p.cham('washer', -0.38, 0.38, 0.0, 1.92, 0.0, 0.8, 0.015); p.box('dark', -0.36, 0.36, 0.0, 0.08, 0.76, 0.81)
    for y in (0.55, 1.42):
        disc_z(p, 'chrome', 0.27, 0.8, 0.82, 0.0, y, 26); disc_z(p, 'glass', 0.22, 0.82, 0.826, 0.0, y, 26); disc_z(p, 'dark', 0.18, 0.79, 0.82, 0.0, y, 20)
        p.box('steel', -0.3, 0.3, y + 0.3, y + 0.4, 0.8, 0.815); p.box('screen_g', 0.12, 0.24, y + 0.33, y + 0.37, 0.815, 0.82)
    p.box('steel', -0.38, 0.38, 0.96, 1.0, 0.8, 0.81)
    return p
def laundry_cart():
    p = P()
    for (x, z) in ((-0.3, -0.22), (0.3, -0.22), (-0.3, 0.22), (0.3, 0.22)): seg_cyl(p, 'chrome', (x, 0.08, z), (x, 0.85, z), 0.012, 6); p.sphere('dark', 0.035, x, 0.035, z, 1)
    for y in (0.5, 0.85):
        for (a, b) in (((-0.3, -0.22), (0.3, -0.22)), ((0.3, -0.22), (0.3, 0.22)), ((0.3, 0.22), (-0.3, 0.22)), ((-0.3, 0.22), (-0.3, -0.22))): seg_cyl(p, 'chrome', (a[0], y, a[1]), (b[0], y, b[1]), 0.01, 6)
    for x in np.arange(-0.24, 0.25, 0.08): seg_cyl(p, 'chrome', (x, 0.5, -0.22), (x, 0.5, 0.22), 0.005, 4)
    seg_cyl(p, 'chrome', (-0.3, 0.85, -0.22), (-0.3, 1.25, -0.22), 0.012, 6); seg_cyl(p, 'chrome', (0.3, 0.85, -0.22), (0.3, 1.25, -0.22), 0.012, 6)
    seg_cyl(p, 'chrome', (-0.3, 1.25, -0.22), (0.3, 1.25, -0.22), 0.012, 6)
    p.cham('bed_b', -0.26, 0.26, 0.52, 0.72, -0.18, 0.18, 0.05)
    return p
def vending():
    """Maquina de sabao em po e moedas sem texto (pivo: centro de tras, piso; frente +Z)."""
    p = P(); p.cham('flag_b', -0.4, 0.4, 0.0, 1.8, 0.0, 0.7, 0.012); p.box('glass', -0.34, 0.12, 0.7, 1.7, 0.7, 0.706)
    for k, y in enumerate((0.75, 1.0, 1.25, 1.5)):
        for x in np.linspace(-0.28, 0.06, 4): p.box(['food_y', 'flag_o', 'cart_w', 'leaf2'][k], x - 0.035, x + 0.035, y, y + 0.16, 0.45, 0.6)
    p.box('dark', 0.18, 0.34, 1.2, 1.5, 0.7, 0.71); p.box('chrome', 0.2, 0.32, 0.4, 0.5, 0.7, 0.74)
    return p
def folding_table(L1=2.4):
    p = P(); x = L1 / 2; p.cham('ctop', -x, x, 0.86, 0.9, -0.45, 0.45, 0.01); p.box('cab', -x + 0.04, x - 0.04, 0.1, 0.86, -0.4, 0.4)
    p.box('dark', -x + 0.06, x - 0.06, 0.0, 0.1, -0.36, 0.36)
    for (dx, dz, m) in ((-0.6, 0.1, 'bed_w'), (-0.3, -0.15, 'bed_b'), (0.4, 0.0, 'bed_g')): p.cham(m, dx - 0.18, dx + 0.18, 0.9, 0.97, dz - 0.14, dz + 0.14, 0.02)
    p.cham('basket', 0.75, 1.1, 0.9, 1.15, -0.2, 0.2, 0.02); return p
def shop_laundry():
    """Lavanderia (loja da esquerda): 7 lavadoras na parede do hall, 7 colunas de
    secadoras no fundo, mesa de dobrar, cadeiras de espera na vitrine, carrinhos, maquina de sabao, TV, deposito e lavabo."""
    p = P()
    for i in range(7): place(p, washer_fl(), -HX - TD / 2, 0.0, -1.0 + i * 0.74, -90)
    for i in range(7): place(p, dryer_stack(), -2.9 - i * 0.82, 0.0, -2.45 + TP / 2, 0)
    place(p, folding_table(2.6), -6.3, 0.0, 1.4)
    for i in range(5): place(p, guest_chair('vinyl'), -BX + T + 0.4, 0.0, 0.9 + i * 0.6, 90)
    for (x, z, r) in ((-4.6, 3.6, 20), (-8.4, 0.2, -10), (-3.4, 4.8, 0)): place(p, laundry_cart(), x, 0.0, z, r)
    place(p, vending(), -BX + T, 0.0, -1.1, 90)
    place(p, tv_wall(), -HX - TD / 2, 1.9, 4.3, -90)
    p.cham('steel', -11.7, -11.66, 1.0, 1.6, -0.2, 0.3, 0.005)
    place(p, plant(1.1), -10.9, 0.0, 5.2)
    back_room(p, -1)
    return p
def tv_wall():
    p = P(); p.box('dark', -0.12, 0.12, -0.12, 0.12, 0.0, 0.06); p.cham('dark', -0.55, 0.55, -0.32, 0.32, 0.06, 0.11, 0.01); p.box('screen', -0.52, 0.52, -0.29, 0.29, 0.11, 0.112); return p
def boiler_room():
    """Casa de maquinas atras do hall: caldeira com queimador e tubulacao, aquecedor, quadro de medidores e luminaria."""
    p = P(); x0, x1, z0, z1 = -HX + TD / 2, HX - TD / 2, -BZ + T, HZB
    p.cham('steel_d', -1.6, -0.4, 0.0, 1.7, -4.6, -3.2, 0.03); p.box('conc_s', -1.7, -0.3, -0.012, 0.1, -4.7, -3.1)
    p.box('dark', -1.3, -0.7, 0.3, 0.7, -3.2, -3.17); p.cham('appl_d', -1.4, -0.6, 1.7, 1.9, -4.4, -3.4, 0.02)
    seg_cyl(p, 'galv', (-1.0, 1.9, -3.9), (-1.0, CH - 0.002, -3.9), 0.12, 14)
    for (x, z) in ((-0.6, -3.5), (-1.4, -3.5)): seg_cyl(p, 'brass', (x, 1.7, z), (x, CH - 0.2, z), 0.035, 8)
    seg_cyl(p, 'brass', (-1.4, CH - 0.2, -3.5), (1.6, CH - 0.2, -3.5), 0.035, 8)
    place(p, water_heater(0.3, 1.5), 1.2, 0.0, -4.9, 0)
    p.cham('steel', -1.2, 1.2, 1.0, 2.0, z1 - 0.1 - 0.06, z1 - 0.1, 0.01)
    for i in range(6):
        x = -1.0 + i * 0.4; p.cham('glass', x - 0.1, x + 0.1, 1.55, 1.85, z1 - 0.1 - 0.12, z1 - 0.16, 0.02); disc_z(p, 'dark', 0.06, z1 - 0.2, z1 - 0.18, x, 1.7, 12)
        p.box('dark', x - 0.06, x + 0.06, 1.15, 1.45, z1 - 0.2, z1 - 0.16)
    seg_cyl(p, 'galv', (0.0, 2.0, z1 - 0.13), (0.0, CH - 0.002, z1 - 0.13), 0.03, 8)
    p.cyl('paint_w', 0.12, CH - 0.03, CH - 0.002, 0.0, -2.5, 14); p.sphere('lamp_glass', 0.08, 0.0, CH - 0.06, -2.5, 1)
    return p
def door_shop(w=0.94, h=2.14, t=0.05):
    """Porta de loja de madeira com vidro inteiro, puxador vertical, barra e chute de latao (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.1
    p.cham('shop_f', 0, s, 0, h, -t / 2, t / 2, 0.005); p.cham('shop_f', w - s, w, 0, h, -t / 2, t / 2, 0.005)
    p.cham('shop_f', s - 0.002, w - s + 0.002, 0, 0.3, -t / 2, t / 2, 0.005); p.cham('shop_f', s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.005)
    p.box('glass', s - 0.004, w - s + 0.004, 0.296, h - s + 0.004, -0.004, 0.004)
    for z in (1, -1):
        zz = z * t / 2; p.box('brass', 0.03, w - 0.03, 0.04, 0.26, *sorted((zz, zz + z * 0.004)))
        seg_cyl(p, 'brass', (w - 0.08, 0.9, zz), (w - 0.08, 0.9, zz + z * 0.05), 0.01, 6); seg_cyl(p, 'brass', (w - 0.08, 1.3, zz), (w - 0.08, 1.3, zz + z * 0.05), 0.01, 6)
        seg_cyl(p, 'brass', (w - 0.08, 0.86, zz + z * 0.05), (w - 0.08, 1.34, zz + z * 0.05), 0.014, 8)
    for yy in (0.25, 1.9): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def door_entry(w=0.98, h=2.18, t=0.05):
    """Porta do hall: madeira envernizada com vidro e grade de ferro decorativa, 2 almofadas embaixo, macaneta e chute de latao."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.14, w - 0.14, 0.95, h - 0.14, -t, t)] + [tbox(a, b, 0.16, 0.8, z - 0.01, z + 0.01) for (a, b) in ((0.14, w / 2 - 0.03), (w / 2 + 0.03, w - 0.14)) for z in (t / 2, -t / 2)]
    p.add('dkwood', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', 0.136, w - 0.136, 0.946, h - 0.136, -0.004, 0.004)
    for x in np.linspace(0.14, w - 0.14, 6)[1:-1]: p.box('iron', x - 0.008, x + 0.008, 0.95, h - 0.14, t / 2 - 0.004, t / 2 + 0.012)
    for y in (1.2, 1.6): p.box('iron', 0.14, w - 0.14, y - 0.008, y + 0.008, t / 2 - 0.004, t / 2 + 0.012)
    for z in (1, -1):
        zz = z * t / 2; p.box('brass', 0.03, w - 0.03, 0.03, 0.14, *sorted((zz, zz + z * 0.004)))
        p.cham('brass', w - 0.11, w - 0.06, 0.88, 1.12, *sorted((zz, zz + z * 0.006)), 0.003); p.sphere('brass', 0.03, w - 0.085, 1.0, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.085, 1.0, zz), (w - 0.085, 1.0, z * (t / 2 + 0.04)), 0.016)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p

# ============================================================================ rua e objetos externos
WALK_IN = 10.4; SIDE_IN = 16.4                                   # borda das calcadas do predio (frente z, lado x)
ROAD_F = (10.55, 21.4); ROAD_S = (16.55, 27.4)                   # pistas: rua da frente (em z) e rua do lado (em x)
CELLAR = sbox(9.0, 6.25, 10.6, 7.45)                             # portas de alcapao do porao na calcada
PITS = [(-17.0, 9.4), (-8.0, 9.4), (4.0, 9.4), (15.4, -3.0), (15.4, -11.0), (-12.0, 22.7), (0.0, 22.7), (12.0, 22.7), (28.7, 4.0), (28.7, -8.0)]
def site():
    """Terreno da esquina (pivo: origem): calcadas de concreto com juntas e caldeiras de arvore, guias, ruas de asfalto com faixa
    amarela dupla, faixas de pedestre e linhas de parada, calcadas do outro lado, quintal de concreto, passagem lateral e grama."""
    p = Piece(); F = FOOT
    walk = unary_union([sbox(SX0, BZ, SIDE_IN, WALK_IN), sbox(BX, SZ0, SIDE_IN, WALK_IN)]).difference(F)
    walk_o = unary_union([sbox(SX0, ROAD_F[1] + 0.15, SX1, SZ1), sbox(ROAD_S[1] + 0.15, SZ0, SX1, SZ1)])
    pits = unary_union([sbox(x - 0.6, z - 0.6, x + 0.6, z + 0.6) for (x, z) in PITS])
    p.merge(paving(walk.difference(pits).difference(CELLAR), 0.12, 1.5, 'concrete')); p.merge(paving(walk_o.difference(pits), 0.12, 1.5, 'concrete'))
    ext_y(p, 'mulch', pits, GY, 0.06)
    for (x, z) in PITS:
        ring = sbox(x - 0.6, z - 0.6, x + 0.6, z + 0.6).difference(sbox(x - 0.56, z - 0.56, x + 0.56, z + 0.56)); ext_y(p, 'steel_d', ring, GY, 0.125)
    curb = unary_union([sbox(SX0, WALK_IN, SIDE_IN + 0.15, WALK_IN + 0.15), sbox(SIDE_IN, SZ0, SIDE_IN + 0.15, WALK_IN)])
    curb_o = unary_union([sbox(SX0, ROAD_F[1], ROAD_S[1] + 0.15, ROAD_F[1] + 0.15), sbox(ROAD_S[1], SZ0, ROAD_S[1] + 0.15, ROAD_F[1])])
    ext_y(p, 'curb', unary_union([curb, curb_o]), GY, 0.15)
    road = sbox(SX0, SZ0, SX1, SZ1).difference(unary_union([walk, walk_o, curb, curb_o, F])).difference(sbox(SX0, SZ0, SIDE_IN + 0.15, WALK_IN + 0.15))
    ext_y(p, 'asphalt', road, GY, 0.0)
    # quintal, passagem lateral e grama
    yard = sbox(-BX - 2.0, -14.0, BX, -BZ); p.merge(paving(yard, 0.1, 2.0, 'concrete'))
    side = sbox(-BX - 2.0, -BZ, -BX, BZ); p.merge(paving(side, 0.1, 2.0, 'concrete'))
    p.box('stone_c', CELLAR.bounds[0] + 0.0, CELLAR.bounds[2], GY, 0.1, CELLAR.bounds[1], CELLAR.bounds[3])
    for (a, b) in ((CELLAR.bounds[0] + 0.02, 9.79), (9.81, CELLAR.bounds[2] - 0.02)):
        p.box('steel', a, b, 0.1, 0.118, CELLAR.bounds[1] + 0.02, CELLAR.bounds[3] - 0.02)
        for k in range(10):
            for j in range(5):
                x = a + 0.06 + k * (b - a - 0.12) / 9; z = CELLAR.bounds[1] + 0.1 + j * 0.25; p.box('steel', x - 0.02, x + 0.02, 0.118, 0.122, z - 0.006 + (k % 2) * 0.06, z + 0.006 + (k % 2) * 0.06)
        p.box('chrome', (a + b) / 2 - 0.08, (a + b) / 2 + 0.08, 0.118, 0.13, 6.8, 6.84)
    grass = sbox(SX0, SZ0, SX1, SZ1).difference(unary_union([walk, walk_o, curb, curb_o, road, F, yard, side, pits, CELLAR]))
    ext_y(p, 'grass', grass, GY, 0.06)
    # faixas: amarela dupla, faixas de pedestre e linhas de parada
    for z in (15.9, 16.05): p.box('line_y', SX0, ROAD_S[0] - 4.0, 0.0, 0.003, z - 0.05, z + 0.05)
    for x in (21.9, 22.05): p.box('line_y', x - 0.05, x + 0.05, 0.0, 0.003, SZ0, ROAD_F[0] - 4.0)
    for k in range(9): x = ROAD_S[0] + 0.5 + k * 1.2; p.box('line_w', x, x + 0.5, 0.0, 0.003, 6.8, 9.8)
    for k in range(9): z = ROAD_F[0] + 0.5 + k * 1.2; p.box('line_w', 12.8, 15.8, 0.0, 0.003, z, z + 0.5)
    p.box('line_w', ROAD_S[0] + 0.2, 21.9 - 0.2, 0.0, 0.003, 5.9, 6.2); p.box('line_w', 11.6, 11.9, 0.0, 0.003, 16.2, ROAD_F[1] - 0.2)
    return p
def hydrant():
    """Hidrante de coluna de ferro (pivo: centro, calcada): base, corpo, 2 bocas laterais com tampa, boca frontal, castelo e porca."""
    p = Piece(); lathe(p, 'hydrant', [(0.16, 0.0), (0.16, 0.05), (0.12, 0.08), (0.11, 0.55), (0.14, 0.58), (0.14, 0.62), (0.1, 0.66), (0.0, 0.7)], sec=16)
    for s in (-1, 1): disc_x(p, 'hydrant', 0.05, *sorted((s * 0.1, s * 0.2)), 0.42, 0.0, 12); disc_x(p, 'hydrant', 0.06, *sorted((s * 0.19, s * 0.23)), 0.42, 0.0, 6)
    disc_z(p, 'hydrant', 0.07, 0.08, 0.2, 0.0, 0.36, 12); disc_z(p, 'hydrant', 0.08, 0.19, 0.23, 0.0, 0.36, 6)
    p.cyl('hydrant', 0.03, 0.7, 0.76, 0, 0, 5)
    return p
def traffic_signal(ang_a=0.0, ang_b=90.0):
    """Semaforo de esquina (pivo: centro, calcada): coluna com base, 2 bracos com grupo focal de 3 luzes com pala virados para as
    2 ruas, botoeira e focos de pedestre com pictograma (boneco e mao)."""
    p = Piece(); p.cyl('steel_d', 0.2, 0.0, 0.3, 0, 0, 12); lathe(p, 'steel_d', [(0.12, 0.3), (0.09, 0.4), (0.08, 5.6)], sec=12)
    for (ang, L1, lit, f) in ((ang_a, 5.0, ('sig_r', 'dark', 'dark'), 1), (ang_b, 7.5, ('dark', 'dark', 'sig_g'), -1)):
        q = Piece(); seg_cyl(q, 'steel_d', (0.0, 5.3, 0.0), (0.0, 5.3, L1), 0.05, 8); seg_cyl(q, 'steel_d', (0.0, 4.6, 0.0), (0.0, 5.28, 1.4), 0.025, 6)
        for zc in (L1 - 0.4, L1 * 0.55):
            q.cham('signal', -0.18, 0.18, 4.3, 5.25, zc - 0.13, zc + 0.13, 0.02); q.box('dark', -0.25, 0.25, 4.25, 5.3, zc + 0.13, zc + 0.15)
            for (k, m) in enumerate(lit):
                y = 5.05 - k * 0.3; disc_x(q, m, 0.1, *sorted((f * 0.18, f * 0.2)), y, zc, 18)
                q.hull('dark', [(f * (0.2 + dx), y + 0.12, zc + dz) for dx in (0.0, 0.18) for dz in (-0.12, 0.12)] + [(f * 0.2, y + 0.06, zc + dz) for dz in (-0.12, 0.12)])
        p.merge(q, rot_y(ang))
    for ang in (ang_a + 180, ang_b + 180):
        q = Piece(); q.cham('signal', -0.17, 0.17, 2.4, 2.9, 0.1, 0.32, 0.015); q.box('dark', -0.15, 0.15, 2.42, 2.88, 0.32, 0.325)
        q.box('cream', -0.03, 0.03, 2.7, 2.82, 0.325, 0.328); q.box('cream', -0.06, 0.06, 2.48, 2.56, 0.325, 0.328)
        q.cham('signal', -0.06, 0.06, 1.05, 1.25, 0.08, 0.14, 0.01); disc_z(q, 'dark', 0.025, 0.14, 0.155, 0.0, 1.15, 12)
        p.merge(q, rot_y(ang))
    return p
def mailbox_st():
    """Caixa de correio de rua azul sem texto (pivo: centro, calcada; boca para +Z): 4 pes, corpo com tampa curva e boca basculante."""
    p = Piece()
    for (x, z) in ((-0.2, -0.22), (0.2, -0.22), (-0.2, 0.22), (0.2, 0.22)): p.box('mailbox', x - 0.025, x + 0.025, 0.0, 0.3, z - 0.025, z + 0.025)
    p.cham('mailbox', -0.26, 0.26, 0.3, 1.05, -0.3, 0.3, 0.015)
    for k in range(9):
        a0 = math.pi * k / 9; a1 = math.pi * (k + 1) / 9
        p.hull('mailbox', [(x, 1.05 + 0.3 * math.sin(a), -0.3 * math.cos(a) * 1.0) for x in (-0.26, 0.26) for a in (a0, a1)] + [(x, 1.05, 0.0) for x in (-0.26, 0.26)])
    p.cham('mailbox', -0.2, 0.2, 1.0, 1.12, 0.29, 0.32, 0.01); p.box('chrome', -0.08, 0.08, 1.08, 1.1, 0.32, 0.34)
    p.box('cream', -0.1, 0.1, 0.6, 0.75, 0.3, 0.303); p.hull('mailbox', [(x, 0.63 + dy, 0.303) for x in (-0.07, 0.07) for dy in (0.0, 0.06)] + [(0.0, 0.66, 0.306)])
    return p
def news_box():
    """Caixa de jornal de rua sem texto (pivo: centro, calcada; porta +Z)."""
    p = Piece(); p.box('steel_d', -0.2, 0.2, 0.0, 0.4, -0.18, 0.18); p.cham('flag_r', -0.25, 0.25, 0.4, 1.05, -0.22, 0.22, 0.012)
    p.box('glass', -0.19, 0.19, 0.62, 0.98, 0.22, 0.226); p.box('paper', -0.17, 0.17, 0.64, 0.9, 0.15, 0.2); p.box('chrome', -0.06, 0.06, 0.55, 0.58, 0.22, 0.25)
    p.cham('flag_r', -0.26, 0.26, 1.05, 1.09, -0.23, 0.23, 0.008); return p
def ac_window():
    """Ar-condicionado de janela (pivo: face da fachada, peitoril; para fora +Z): gabinete, grade frontal, aletas laterais e suporte."""
    p = Piece(); p.cham('appl', -0.31, 0.31, 0.03, 0.41, -0.1, 0.45, 0.012)
    for y in np.arange(0.07, 0.38, 0.03): p.box('grille', -0.28, 0.28, y, y + 0.012, 0.45, 0.456)
    for s in (-1, 1):
        for z in np.arange(0.05, 0.42, 0.04): p.box('grille', *sorted((s * 0.31, s * 0.314)), 0.18, 0.36, z, z + 0.014)
    for x in (-0.25, 0.25): p.hull('steel_d', [(x + dx, y, z) for dx in (-0.012, 0.012) for (y, z) in ((0.03, 0.0), (0.03, 0.4), (-0.35, 0.0), (-0.31, 0.0))])
    for x in (-0.25, 0.25): p.box('steel_d', x - 0.012, x + 0.012, -0.03, 0.03, 0.0, 0.42)
    p.box('cab', -0.36, -0.31, 0.03, 0.41, -0.14, -0.1); p.box('cab', 0.31, 0.36, 0.03, 0.41, -0.14, -0.1)
    return p
def trash_bin():
    p = Piece(); lathe(p, 'steel_d', [(0.22, 0.0), (0.25, 0.75), (0.0, 0.75)], sec=16)
    for y in (0.1, 0.65): ring_y(p, 'steel', 0.25, 0.262, y, y + 0.03, 0, 0, 16)
    lathe(p, 'steel_d', [(0.27, 0.75), (0.27, 0.79), (0.1, 0.84), (0.0, 0.85)], sec=16); seg_cyl(p, 'steel', (-0.07, 0.86, 0.0), (0.07, 0.86, 0.0), 0.012, 6)
    return p
def dumpster():
    p = Piece(); p.hull('dumpster', [(x, y, z) for x in (-0.95, 0.95) for (y, z) in ((0.15, -0.6), (0.15, 0.6), (1.25, -0.75), (1.25, 0.75))])
    for z in (-0.62, 0.62): p.box('steel_d', -1.0, 1.0, 0.0, 0.15, z - 0.04, z + 0.04)
    for (x0, x1) in ((-0.95, -0.01), (0.01, 0.95)): p.hull('dark', [(x, y, z) for x in (x0, x1) for (y, z) in ((1.25, -0.76), (1.29, -0.76), (1.25, 0.8), (1.29, 0.8))])
    for x in (-0.95, 0.95): p.box('steel_d', *sorted((x, x + math.copysign(0.03, x))), 0.6, 0.7, -0.4, 0.4)
    return p
def fence(L1=2.4, h=1.8):
    """Painel de cerca de tabuas de madeira (pivo: inicio, chao; ao longo de +X): mourao, 2 travessas e tabuas."""
    p = Piece(); p.box('dkwood', 0.0, 0.1, -0.1, h + 0.1, -0.05, 0.05)
    for y in (0.3, h - 0.3): p.box('wood', 0.1, L1, y, y + 0.09, 0.05, 0.09)
    for x in np.arange(0.1, L1 - 0.01, 0.145): p.box('wood', x + 0.003, x + 0.142, 0.05, h, 0.09, 0.11)
    return p
def bike_rack():
    p = Piece()
    for x in np.arange(-1.0, 1.01, 0.5):
        seg_cyl(p, 'galv', (x, -0.05, -0.3), (x, 0.7, -0.3), 0.025, 8); seg_cyl(p, 'galv', (x, 0.7, -0.3), (x, 0.7, 0.3), 0.025, 8); seg_cyl(p, 'galv', (x, 0.7, 0.3), (x, -0.05, 0.3), 0.025, 8)
    return p

# ---------------------------------------------------------------------------- terreno
LOT = sbox(0.0, -5.0, 34.0, 15.0).union(sbox(26.0, 15.0, 33.0, 23.0))          # estacionamento e acesso da rua
ROAD = sbox(SX0, 26.0, SX1, SZ1); WALK = sbox(SX0, 23.0, SX1, 25.6); CURB = sbox(SX0, 25.6, SX1, 26.0)
STALL_N = [(2.0 + i * 2.7, -5.0) for i in range(9)]                            # fileira norte (embaixo da garagem coberta)
STALL_S = [(2.0 + i * 2.7, 15.0) for i in range(9)]                            # fileira sul
# ============================================================================ pecas
def mir(p): return mirrored(p, mirror_x(0.0))
pieces = {
    'shell_g': shell('g'), 'shell_t': shell('t'), 'slab_g': slab('g'), 'slab_t1': slab('t1'), 'slab_t': slab('t'), 'slab_r': slab('r'),
    'walls_g': walls('g'), 'walls_t': walls('t'), 'stair': stair(), 'hall_rail': hall_rail(), 'roof': roof(),
    'shop_grocery': shop_grocery(), 'shop_laundry': shop_laundry(), 'shop_ceil': shop_ceil(), 'boiler_room': boiler_room()}
A = apartment(); pieces['apt_r'] = A; pieces['apt_l'] = mir(A)
FE = {'fe_1': fe_level(1), 'fe_e': fe_level(2), 'fe_o': fe_level(3), 'fe_top': fe_level(NL - 1)}
for n, q in FE.items(): pieces[n + '_r'] = q; pieces[n + '_l'] = mir(q)
pieces.update({'door_unit': door_unit(), 'door_int': door_interior(ID - 0.02, DH - 0.012, 0.04), 'door_entry': door_entry(), 'door_shop': door_shop(),
               'door_back': door_metal(0.83, 2.08), 'door_roof': door_metal(0.78, 2.08)})
pieces.update({'site': site(), 'hydrant': hydrant(), 'traffic_signal': traffic_signal(90.0, 0.0), 'mailbox_st': mailbox_st(), 'news_box': news_box(),
               'ac_window': ac_window(), 'trash_bin': trash_bin(), 'trash_can': trash_can(), 'dumpster': dumpster(), 'fence': fence(), 'bike_rack': bike_rack(),
               'lamp_pole': lamp_pole(6.0), 'tree': tree(7.0, 2.0, 'leaf', 2), 'tree_b': tree(6.0, 1.7, 'leaf2', 5),
               'car_sedan_r': car('car_r', 'sedan'), 'car_wagon_b': car('car_b', 'wagon'), 'car_hatch_y': car('car_y', 'hatch'), 'car_pickup_s': car('car_s', 'pickup'),
               'car_coupe_g': car('car_g', 'coupe'), 'car_sedan_w': car('car_w', 'sedan'), 'car_hatch_t': car('car_t', 'hatch')})
pieces['player_scale_ref'] = player_ref()

# ============================================================================ montagem
G = ['predio']; J = ['rua']
def fl(k): return G + [f'floor{k}']
def door_b(n, axis, a, b, c, y, hinge, into, tags): door_at(n, axis, a, b, c, y, hinge, into, tags)
def door_m(n, axis, a, b, c, y, hinge, into, tags):
    """Porta do lado direito e a sua espelhada no lado esquerdo."""
    door_b(n, axis, a, b, c, y, hinge, into, tags)
    if axis == 'x': door_b(n, axis, -b, -a, c, y, 'b' if hinge == 'a' else 'a', into, tags)
    else: door_b(n, axis, a, b, -c, y, hinge, -into, tags)
for k in range(NL):
    y = LV[k]; t = fl(k); g = k == 0
    put('shell_g' if g else 'shell_t', 0, y, 0, 0, t + ['ext'])
    put('slab_g' if g else ('slab_t1' if k == 1 else 'slab_t'), 0, y, 0, 0, t); put('walls_g' if g else 'walls_t', 0, y, 0, 0, t)
    put('stair', 0, y, 0, 0, t)
    if g:
        put('shop_grocery', 0, y, 0, 0, t + ['mercearia']); put('shop_laundry', 0, y, 0, 0, t + ['lavanderia']); put('boiler_room', 0, y, 0, 0, t); put('shop_ceil', 0, y, 0, 0, fl(1))
        door_b('door_entry', 'x', HALL_DOOR[0] + 0.05, HALL_DOOR[1] - 0.05, BZ - 0.15, y, 'a', -1, t)
        door_m('door_shop', 'x', SHOP_D[0] + 0.06, SHOP_D[1] - 0.06, BZ - 0.11, y, 'a', -1, t)
        for (ax, c, a, b, nm) in DOORS_G:
            if nm == 'back': door_m('door_int', 'x', a, b, c, y, 'a', -1, t)
            else: door_m('door_int', 'z', a, b, c, y, 'b', 1, t)
        for (a, b) in RDOOR: door_b('door_back', 'x', a + 0.05, b - 0.05, -BZ + 0.125, y, 'a', 1, t)
        continue
    put('apt_r', 0, y, 0, 0, t); put('apt_l', 0, y, 0, 0, t)
    door_m('door_unit', 'z', UDOOR[0], UDOOR[1], HX, y, 'b', 1, t)
    for (ax, c, a, b, nm) in DOORS_R:
        if nm == 'closet': door_m('door_int', 'z', a, b, c, y, 'b', 1, t)
        else: door_m('door_int', 'x', a, b, c, y, 'a' if nm != 'master' else 'b', -1, t)
    fe = 'fe_1' if k == 1 else ('fe_top' if k == NL - 1 else ('fe_e' if k % 2 == 0 else 'fe_o'))
    for s in 'rl': put(f'{fe}_{s}', 0, y, 0, 0, t + ['ext', 'escada_incendio'])
put('slab_r', 0, LV[NL], 0, 0, fl(NL)); put('roof', 0, LV[NL], 0, 0, G + ['roof']); put('hall_rail', 0, LV[NL], 0, 0, G + ['roof'])
door_b('door_roof', 'z', 4.55, 5.35, HX - 0.025, LV[NL] + 0.05, 'a', 1, G + ['roof'])
# ar-condicionado de janela em algumas janelas (fachada, x ou z, andar)
for (f, u, k) in (('S', 8.2, 1), ('S', -10.5, 2), ('S', 10.5, 3), ('S', -8.2, 4), ('S', 8.2, 5), ('E', -2.8, 2), ('E', 4.8, 4), ('W', -2.8, 3), ('W', 4.8, 1), ('N', 9.4, 2), ('N', -2.1, 4), ('N', -9.4, 5)):
    y = LV[k] + WIN[0] + 0.022
    if f == 'S': put('ac_window', u, y, BZ, 0, fl(k) + ['ext'])
    if f == 'N': put('ac_window', u, y, -BZ, 180, fl(k) + ['ext'])
    if f == 'E': put('ac_window', BX, y, u, 90, fl(k) + ['ext'])
    if f == 'W': put('ac_window', -BX, y, u, -90, fl(k) + ['ext'])
# rua
put('site', 0, 0, 0, 0, J)
for i, (x, z) in enumerate(PITS): put('tree' if i % 2 == 0 else 'tree_b', x, 0.06, z, 0, J + ['roof'])
for (x, z, r) in ((-15.0, 10.0, 0), (-3.0, 10.0, 0), (9.0, 10.0, 0), (16.0, -7.0, 90), (16.0, -15.0, 90), (-6.0, 21.95, 180), (6.0, 21.95, 180), (27.95, -2.0, -90)):
    put('lamp_pole', x, 0.12, z, r, J)
put('traffic_signal', SIDE_IN - 0.25, 0.12, WALK_IN - 0.25, 0, J); put('traffic_signal', ROAD_S[1] + 0.4, 0.12, ROAD_F[1] + 0.4, 180, J)
put('hydrant', SIDE_IN - 0.4, 0.12, 5.0, 0, J); put('hydrant', -9.6, 0.12, WALK_IN - 0.4, 0, J)
put('mailbox_st', 11.0, 0.12, WALK_IN - 0.45, 180, J); put('news_box', 12.0, 0.12, WALK_IN - 0.4, 180, J)
put('trash_can', 13.2, 0.12, WALK_IN - 0.45, 0, J); put('trash_can', -5.6, 0.12, WALK_IN - 0.45, 0, J); put('trash_can', SIDE_IN - 0.45, 0.12, -6.0, 0, J)
put('bike_rack', -12.6, 0.12, WALK_IN - 0.8, 0, J)
for (x, n) in ((-18.0, 'car_sedan_r'), (-12.0, 'car_hatch_t'), (-6.0, 'car_wagon_b'), (1.5, 'car_coupe_g'), (8.0, 'car_sedan_w')): put(n, x, 0.0, ROAD_F[0] + 1.0, -90, J)
for (z, n) in ((-14.0, 'car_pickup_s'), (-7.5, 'car_hatch_y'), (-1.5, 'car_sedan_r')): put(n, ROAD_S[0] + 1.0, 0.0, z, 0, J)
for (x, n) in ((-15.0, 'car_hatch_y'), (-2.0, 'car_wagon_b')): put(n, x, 0.0, ROAD_F[1] - 1.0, 90, J)
# quintal
put('dumpster', 7.5, 0.1, -12.6, 0, J)
for x in (-6.2, -5.6, -5.0, -4.4): put('trash_bin', x, 0.1, -6.7, 0, J)
for i in range(10): put('fence', -BX - 2.0 + i * 2.4, 0.1, -14.0, 0, J)
for i in range(3): put('fence', -BX - 2.0, 0.1, -14.0 + i * 2.4, -90, J)
put('player_scale_ref', 5.0, 0.12, 8.4, 0, J); put('player_scale_ref', 6.0, LV[2], 3.0, 0, fl(2))

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'ground': 0.0, 'floor_height': H, 'floor_levels': LV, 'floors': NL, 'footprint': [list(c) for c in FOOT.exterior.coords],
                       'wall_thickness': T, 'partition_thickness': TP, 'stair': {'risers': SNR, 'rise': SRR, 'tread': STRD, 'hall': [-HX, HX, HZ0, BZ]},
                       'fire_escape': {'x': list(FE_X), 'depth': FE_D, 'platform_above_floor': FE_Y, 'risers': FE_N, 'tread': FE_T},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]}, 'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
              'placements': L}
    json.dump(layout, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc2 = trimesh.Scene(); tot = 0
    for e in L:
        T_ = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T_[:3, 3] = e['pos']
        sc = pieces[e['piece']].scene(e['piece'])
        for nm, g_ in sc.geometry.items(): g2 = g_.copy(); g2.apply_transform(T_); sc2.add_geometry(g2); tot += len(g2.faces)
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:12]: print(f'  {n:30s} {p.tris():6d} tri')
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
