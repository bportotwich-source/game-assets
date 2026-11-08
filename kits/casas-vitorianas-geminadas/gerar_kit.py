"""Kit 61: par de casas geminadas vitorianas de tijolo (estilo ingles), em ALTO DETALHE (scripts/detalhe).
Par de casas espelhadas (12,8 x 9 m + anexo dos fundos), terreo elevado, 1 andar e sotao: fachadas de tijolo vermelho com faixas
de tijolo amarelo, embasamento de tijolo escuro, peitoris e vergas de pedra; bay windows chanfradas de 2 andares com cornija e
telhadinho de ardosia, empena com lambrequim e pinaculo em cima de cada bay, porta de entrada com bandeira em arco e degraus de
pedra. Telhado de 4 aguas de ardosia em fiadas com cumeeiras de barro, calhas de ferro, condutores e 4 chamines com potes.
Por dentro: hall com piso de ladrilho xadrez, escada em U de madeira com passadeira, sala com bay, sala de jantar, cozinha e
area de servico no anexo, 2 quartos e banheiro no andar, quarto no sotao; lareiras na parede de meia, rodapes altos, sanca e
rosetas. Jardim da frente com muro baixo, portao, caminho xadrez e cerca viva; quintal com gramado, galpao e varal; rua.
Arte original, sem texto. Y para cima, 1 unidade = 1 m. Padrao: PADRAO_METRICAS.md.
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
                       'shingles': (78, 84, 94), 'shingle_c': (92, 70, 58), 'gutter': (44, 46, 48), 'plaster': (238, 234, 226), 'ceil': (244, 242, 236),
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
                       'cushion': (200, 150, 70), 'flag_o': (230, 140, 50), 'flag_r': (180, 50, 50), 'flag_b': (40, 60, 120), 'neon_r': (220, 60, 50), 'food_g': (90, 140, 60), 'food_r': (190, 60, 50), 'food_y': (230, 190, 70), 'basket': (150, 110, 70), 'cream': (240, 232, 214), 'terrazzo': (204, 198, 188), 'bench_g': (60, 100, 70), 'cart_w': (200, 200, 196), 'screen_g': (60, 200, 120), 'grille': (60, 62, 64), 'brick': (156, 68, 50), 'brick2': (128, 56, 44), 'stone_c': (214, 204, 182), 'cornice': (54, 88, 70), 'shop_f': (50, 78, 64), 'shop_f2': (92, 44, 40), 'tin': (236, 230, 212), 'wood_f': (168, 120, 78), 'roofing': (120, 120, 116), 'tank': (150, 108, 72), 'awn_r': (176, 52, 46), 'awn_g': (52, 110, 76), 'awn_w': (238, 234, 222), 'radiator': (222, 220, 212), 'hydrant': (196, 54, 44), 'signal': (230, 180, 40), 'sig_r': (230, 60, 40), 'sig_g': (60, 220, 120), 'tile_k': (40, 42, 44), 'tile_hex': (240, 240, 236), 'washer': (236, 238, 238), 'mailbox': (40, 70, 140), 'conc_r': (166, 162, 154), 'slate': (78, 84, 94), 'slate_c': (60, 64, 72), 'ridge_c': (150, 78, 56), 'brick_y': (214, 182, 120), 'brick_d': (70, 46, 44), 'door_g': (34, 64, 52), 'lead': (110, 114, 118), 'quarry': (150, 70, 50), 'tile_w2': (236, 234, 226), 'tile_b': (34, 34, 36), 'tile_r': (164, 74, 52), 'bin_g': (60, 90, 70), 'bin_b': (40, 44, 50), 'paint_c': (230, 222, 200), 'wallpaper': (204, 186, 160), 'wallpaper2': (172, 190, 176), 'velvet': (98, 32, 42), 'mahog': (96, 52, 36), 'carpet_r': (130, 40, 44), 'mantel': (232, 228, 220), 'lawn': (98, 140, 64), 'gravel': (170, 162, 150), 'shed': (90, 110, 96), 'clay': (172, 96, 62), }, **CAR_COLS),
           texturas={'brick': 'brick', 'siding': 'paint', 'shingles': 'shingles', 'plaster': 'plaster', 'ceil': 'plaster', 'carpet': 'render', 'carpet2': 'render',
                     'concrete': 'render', 'conc_s': 'render', 'asphalt': 'render', 'curb': 'render', 'grass': 'render', 'mulch': 'render', 'stone': 'stone',
                     'deck': 'deck', 'wood': 'planks', 'dkwood': 'planks', 'laminate': 'planks', 'bark': 'render', 'vinyl_f': 'render', 'hedge': 'render', 'terrazzo': 'render', 'brick2': 'brick', 'stone_c': 'stone', 'wood_f': 'planks', 'roofing': 'render', 'tank': 'planks', 'conc_r': 'render', 'slate': 'shingles', 'brick_y': 'brick', 'brick_d': 'brick', 'quarry': 'render', 'lawn': 'render', 'gravel': 'render', 'wallpaper': 'plaster', 'wallpaper2': 'plaster', 'mahog': 'planks', 'shed': 'planks'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu', 'alu_d'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4
for k in ('screen_g', 'sig_r', 'sig_g'): MATS[k].emissiveFactor = [c / 255 for c in D.COL[k]]

# ============================================================================ medidas (casa da direita: x 0..6,4, z -4,5..4,5, frente +z; a da esquerda e o espelho em x)
W = 2.0; T = 0.3; TP = 0.12; TD = 0.2; t_ = 0.1; GY = -0.3
Y0 = 0.45; H = 3.0; ST = 0.2; CH = H - ST; NL = 2
LV = [Y0 + k * H for k in range(NL + 1)]                         # 0,45 (terreo), 3,45 (andar), 6,45 (sotao)
YK = 0.6; YE = LV[2] + YK                                          # parede do sotao (meia-agua) ate 7,05 = linha do telhado na face
MX, MZ = 6.4, 4.5; PW = 0.15                                       # casa: x 0..6,4 (parede de meia ate 0,15), z -4,5..4,5
OXR, OZ1 = 2.8, -8.7                                               # anexo dos fundos (cozinha): x 0..2,8, z -8,7..-4,5
FOOT = sbox(0.0, -MZ, MX, MZ); OFOOT = sbox(0.0, OZ1, OXR, -MZ)
INNER = sbox(PW, -MZ + T, MX - T, MZ - T)                         # x 0,15..6,1, z -4,2..4,2
OINNER = sbox(PW, OZ1 + T, OXR - T, -MZ)                           # x 0,15..2,5, z -8,4..-4,5
XH = 3.88                                                          # parede do hall (x 3,82..3,94); hall/escada de 3,94 a 6,1
SXA = (5.08, MX - T); SXB = (XH + TP / 2, 4.96)                    # lance A (junto da parede lateral) e lance B (junto do hall)
SNR = 16; SRR = H / SNR; STRD = 0.25; ZF = -1.2                    # 16 espelhos de 0,1875; lance A sobe para -z a partir de z = -1,2
ZM = ZF - (SNR // 2 - 1) * STRD                                    # -2,95: borda do patamar intermediario (ate a parede, -4,2)
DW = 0.9; DH = 2.1; ID = 0.8
BAYC = 2.0; BAY_W = 1.45; BAY_P = 0.8; BAY_F = 0.65; BT = 0.25     # bay window: meia-largura na parede, saliencia, meia-frente, parede
OPH = BAY_W - BT * math.sqrt(2.0)                                  # meia-largura do vao da bay na parede (1,096)
FDOOR = (4.25, 5.15); FD_H = 2.72                                  # porta da frente com bandeira em arco
SX0, SX1, SZ0, SZ1 = -12.0, 12.0, -17.0, 20.0                     # terreno (rua na frente, +z)
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
# ============================================================================ telhados por faces planas (coordenadas do mundo, casa da direita x >= 0)
BIG = 60.0
def hp(a, b, c):
    """Semiplano a*x + b*z + c >= 0 (poligono grande)."""
    n = math.hypot(a, b)
    if n < 1e-12: return sbox(-BIG, -BIG, BIG, BIG) if c >= 0 else Polygon()
    a, b, c = a / n, b / n, c / n; px, pz = -a * c, -b * c; dx, dz = -b, a
    return Polygon([(px + dx * BIG, pz + dz * BIG), (px - dx * BIG, pz - dz * BIG), (px - dx * BIG + a * BIG, pz - dz * BIG + b * BIG),
                    (px + dx * BIG + a * BIG, pz + dz * BIG + b * BIG)])
class Pl:
    """Agua do telhado: y = ye na linha (ex, ez) e sobe com inclinacao s para dentro (n = horizontal apontando para o beiral)."""
    def __init__(s, ye, nx, nz, ex, ez, slope):
        L = math.hypot(nx, nz); s.n = (nx / L, nz / L); s.e = s.n[0] * ex + s.n[1] * ez; s.s = slope
        s.gx, s.gz, s.c = -slope * s.n[0], -slope * s.n[1], ye + slope * s.e
    def y(s, x, z): return s.c + s.gx * x + s.gz * z
    def d(s, x, z): return s.e - (s.n[0] * x + s.n[1] * z)
def facets(objs):
    """objs: [(dominio, [aguas])]. Cada telhado e o minimo das suas aguas no dominio; entre telhados vence o mais alto.
    Devolve [(poligono, agua, indice do telhado)]: cada face e plana, entao as fiadas nao dobram."""
    out = []
    for oi, (dom, pls) in enumerate(objs):
        for i, P in enumerate(pls):
            r = dom
            for j, Q in enumerate(pls):
                if j != i: r = r.intersection(hp(Q.gx - P.gx, Q.gz - P.gz, Q.c - P.c))
            for oj, (dom2, pls2) in enumerate(objs):
                if oj == oi: continue
                above = dom2
                for Q in pls2: above = above.intersection(hp(Q.gx - P.gx, Q.gz - P.gz, Q.c - P.c))
                r = r.difference(above)
            for g in polys(r):
                if g.area > 2e-4: out.append((g, P, oi))
    return out
def slate_uv(v, n):
    h = n[:, [0, 2]].copy(); L = np.linalg.norm(h, axis=1); L[L < 1e-6] = 1.0; h = h / L[:, None]
    u = -h[:, 1] * v[:, 0] + h[:, 0] * v[:, 2]; w = -(h[:, 0] * v[:, 0] + h[:, 1] * v[:, 2]) / 0.77
    return np.stack([u, w], 1) / TILE
def on_plane(P, poly, y0, y1, mat, p):
    """Prisma do poligono do chao (y0) ate a agua P deslocada de y1 (topo inclinado: paredes de meia-agua e empenas)."""
    for g in polys(poly):
        m = trimesh.creation.extrude_polygon(g, 1.0); v = m.vertices.copy(); a, b, t = v[:, 0], v[:, 1], v[:, 2]
        m.vertices = np.stack([a, y0 + t * (P.y(a, b) + y1 - y0), b], 1); m.invert(); p.add(mat, _fix(m))
def under_roof(p, fs, poly, y0, off, mat):
    for (g, P, oi) in fs: on_plane(P, poly.intersection(g), y0, off, mat, p)
def roof_faces(p, fs, th, deg, inner=None, cut=None, tv=0.055, bump=0.012):
    """Nucleo (caibros e ripas) de espessura th, fiadas de ardosia com degrau e, em 'inner', forro de gesso inclinado do sotao."""
    configurar_telhado(tv, bump, deg)
    for (g, P, oi) in fs:
        if cut is not None: g = g.difference(cut)
        for q in polys(g):
            f = (lambda P: (lambda a, b: P.y(a, b)))(P)
            sheared(p, 'slate_c', q, -th, 0.0, f)
            ds = [P.d(x, z) for (x, z) in q.exterior.coords]; d0, d1 = min(ds), max(ds)
            fd = (lambda P, d0: (lambda a, b: P.d(a, b) - d0))(P, d0)
            strip = (lambda P, d0: (lambda u, v: hp(-P.n[0], -P.n[1], P.e - d0 - u).intersection(hp(P.n[0], P.n[1], -(P.e - d0 - v)))))(P, d0)
            for qc in polys(q.buffer(-0.002, join_style=2)):   # fiadas 2 mm para dentro das bordas do nucleo
                sheared_courses(p, qc, (lambda P: (lambda a, b: P.y(a, b) - 0.02))(P), fd, strip, d1 - d0 + 1e-3, slate_uv)
            if inner is not None:
                for qi in polys(q.intersection(inner)): sheared(p, 'ceil', qi, -th - 0.012, -th, f)
def ridge_caps(p, fs, r=0.075, lift=0.07, crest=True):
    """Cumeeiras e espigoes de barro (rolo) nas arestas entre aguas do mesmo telhado; crista recortada nas cumeeiras horizontais."""
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            gi, Pi, oi = fs[i]; gj, Pj, oj = fs[j]
            if oi != oj: continue
            a, b, c = Pi.gx - Pj.gx, Pi.gz - Pj.gz, Pi.c - Pj.c; L = math.hypot(a, b)
            if L < 1e-9: continue
            px, pz = -a * c / L ** 2, -b * c / L ** 2; dx, dz = -b / L, a / L
            line = LineString([(px - dx * BIG, pz - dz * BIG), (px + dx * BIG, pz + dz * BIG)])
            zone = gi.buffer(2e-3).intersection(gj.buffer(2e-3))
            seg = line.intersection(zone)
            for s in getattr(seg, 'geoms', [seg]):
                if s.geom_type != 'LineString' or s.length < 0.08: continue
                (x0, z0), (x1, z1) = s.coords[0], s.coords[-1]
                A = (x0, Pi.y(x0, z0) + lift, z0); B = (x1, Pi.y(x1, z1) + lift, z1)
                seg_cyl(p, 'ridge_c', A, B, r, 10)
                if crest and abs(A[1] - B[1]) < 0.01:
                    n = int(s.length / 0.3)
                    for k in range(n):
                        t = (k + 0.5) / n; x = x0 + (x1 - x0) * t; z = z0 + (z1 - z0) * t; y = A[1] + r * 0.8
                        ux, uz = (x1 - x0) / s.length, (z1 - z0) / s.length
                        p.hull('ridge_c', [(x + ux * du, y + dy, z + uz * du + w) for (du, dy) in ((-0.06, 0.0), (0.06, 0.0), (-0.02, 0.1), (0.02, 0.1), (0.0, 0.14)) for w in (-0.012, 0.012)])
def eave_trim(p, dom_full, foot_full, ys, ytop, clip, skip=None):
    """Forro do beiral (embaixo do nucleo) e testeira por fora do dominio."""
    so = dom_full.difference(foot_full).intersection(clip)
    if skip is not None: so = so.difference(skip)
    ext_y(p, 'trim', so, ys - 0.02, ys)
    ring = dom_full.buffer(0.03, join_style=2).difference(dom_full).intersection(clip)
    if skip is not None: ring = ring.difference(skip)
    ext_y(p, 'trim', ring, ys - 0.17, ytop)
    return so

# ---------------------------------------------------------------------------- geometria dos telhados
OH = 0.35; T40 = math.tan(math.radians(40)); T55 = math.tan(math.radians(55)); T35 = math.tan(math.radians(35))
RTH = 0.2                                                          # espessura do nucleo (caibro + ripa)
GA, GB = BAYC - 1.5, BAYC + 1.5; GOH = 0.3; GF = 0.2                # empena sobre a bay: x 0,5..3,5, beiral lateral 0,3, frente 0,2
XR = 0.0                                                           # o telhado da casa da direita vai de x = 0 para +x
CLIP = sbox(XR, -BIG, BIG, BIG)
def mxp(g): return affinity.scale(g, -1.0, 1.0, origin=(0, 0))
CHIM_C = sbox(-0.6, -0.45, 0.6, 0.45)                              # chamine da parede de meia (na cumeeira)
CHIM_S = sbox(MX, -2.9, MX + 0.45, -2.05)                          # chamine lateral (encostada na parede de fora)
CHIM_O = sbox(-0.6, -6.84, 0.6, -5.6)                              # chamine do fogao da cozinha (anexo)
NOTCH = sbox(GA - GOH, MZ, GB + GOH, MZ + OH + 0.1)
MAIN_D = sbox(-MX - OH, -MZ - OH, MX + OH, MZ + OH).difference(NOTCH).difference(mxp(NOTCH))
MAIN_P = [Pl(YE, 0, 1, 0, MZ, T40), Pl(YE, 0, -1, 0, -MZ, T40), Pl(YE, 1, 0, MX, 0, T40), Pl(YE, -1, 0, -MX, 0, T40)]
WING_D = sbox(GA - GOH, 1.0, GB + GOH, MZ + GF)
WING_P = [Pl(YE, -1, 0, GA, 0, T55), Pl(YE, 1, 0, GB, 0, T55)]
BAY_O = [(BAYC - BAY_W, MZ), (BAYC - BAY_F, MZ + BAY_P), (BAYC + BAY_F, MZ + BAY_P), (BAYC + BAY_W, MZ)]
BAY_POLY = Polygon(BAY_O)
YB = LV[2] + 0.28                                                  # beiral do telhadinho da bay (na face)
BAY_D = Polygon([(BAYC - BAY_W - 1.0, MZ - 1.0)] + BAY_O[1:3] + [(BAYC + BAY_W + 1.0, MZ - 1.0)]).buffer(0.14, join_style=2).intersection(sbox(-BIG, MZ, BIG, BIG))
BAY_PL = [Pl(YB, 0, 1, 0, MZ + BAY_P, T35), Pl(YB, -1, 1, BAYC - BAY_F, MZ + BAY_P, T35), Pl(YB, 1, 1, BAYC + BAY_F, MZ + BAY_P, T35)]
YO = LV[1] + 0.25                                                  # linha do telhado do anexo na face da parede
OUT_D = sbox(-OXR - 0.3, OZ1 - 0.3, OXR + 0.3, -MZ)
OUT_P = [Pl(YO, 0, -1, 0, OZ1, T35), Pl(YO, 1, 0, OXR, 0, T35), Pl(YO, -1, 0, -OXR, 0, T35)]
def roof_main_facets():
    objs = [(MAIN_D.intersection(CLIP), MAIN_P), (WING_D, WING_P)]
    return facets(objs)
FS_MAIN = None
def main_fs():
    global FS_MAIN
    if FS_MAIN is None: FS_MAIN = roof_main_facets()
    return FS_MAIN
def bargeboard(p):
    """Lambrequim da empena: tabua recortada com gotas, pinaculo torneado na ponta e pendente embaixo."""
    z0, z1 = MZ + GF, MZ + GF + 0.04; P1, P2 = WING_P; xa = GA - GOH; xb = GB + GOH; xm = BAYC; ya = P1.y(xm, 0)
    for (P, xs, xe) in ((P1, xa, xm), (P2, xm, xb)):
        p.hull('trim', [(x, P.y(x, 0) + dy, z) for x in (xs, xe) for dy in (0.07, -0.3) for z in (z0, z1)])
        n = int(abs(xe - xs) / 0.2)
        for k in range(n):
            x = xs + (xe - xs) * (k + 0.5) / n; y = P.y(x, 0) - 0.3; disc_z(p, 'trim', 0.06, z0 + 0.005, z1 - 0.005, x, y, 10)
            disc_z(p, 'slate_c', 0.022, z1 - 0.004, z1 + 0.002, x, P.y(x, 0) - 0.15, 8)
    lathe(p, 'trim', [(0.0, ya - 0.75), (0.035, ya - 0.7), (0.05, ya - 0.55), (0.03, ya - 0.45), (0.045, ya - 0.3), (0.0, ya - 0.3)], xm, (z0 + z1) / 2, sec=10)
    lathe(p, 'trim', [(0.0, ya + 0.02), (0.05, ya + 0.02), (0.05, ya + 0.3), (0.07, ya + 0.36), (0.03, ya + 0.42), (0.02, ya + 0.7), (0.035, ya + 0.78), (0.0, ya + 0.9)], xm, (z0 + z1) / 2 - 0.1, sec=10)
def chimney(p, poly, y0, y1, pots=2):
    """Chamine de tijolo com 3 fiadas em balanco, capa de pedra e potes de barro (y0..y1 e o corpo)."""
    # na parede de meia a chamine e cortada em x = 0 (a outra metade e a da casa espelhada)
    cl = (lambda g: g.intersection(CLIP)) if poly.bounds[0] < 1e-6 else (lambda g: g)
    ext_y(p, 'brick', poly, y0, y1)
    for k, d in enumerate((0.04, 0.08, 0.04)):
        ext_y(p, 'brick' if k < 2 else 'brick_d', cl(poly.buffer(d, join_style=2)), y1 + k * 0.08, y1 + (k + 1) * 0.08)
    ext_y(p, 'stone_c', cl(poly.buffer(0.02, join_style=2)), y1 + 0.24, y1 + 0.3)
    b = poly.bounds; cx, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; along_x = (b[2] - b[0]) > (b[3] - b[1])
    for k in range(pots):
        t = (k + 0.5) / pots - 0.5; x = cx + (t * (b[2] - b[0]) if along_x else 0.0); z = cz + (0.0 if along_x else t * (b[3] - b[1]))
        if not poly.contains(Point(x, z)): continue
        lathe(p, 'clay', [(0.0, y1 + 0.3), (0.13, y1 + 0.3), (0.13, y1 + 0.36), (0.1, y1 + 0.42), (0.085, y1 + 0.8), (0.11, y1 + 0.86), (0.11, y1 + 0.9), (0.07, y1 + 0.9), (0.07, y1 + 0.5), (0.0, y1 + 0.5)], x, z, sec=14)
def gutter_line(p, x0, x1, z0, ytop, rot, mitre=(), caps=(False, False)):
    g = Piece(); gutter_run(g, x0, x1, z0, ytop, mitre=mitre, caps=caps); p.merge(g, rot_y(rot))
def roof():
    """Telhado da casa da direita (pivo: chao do mundo): 4 aguas de 40 graus de ardosia, empena de 55 graus sobre a bay com
    lambrequim e pinaculo, telhadinho da bay, cumeeiras e espigoes de barro com crista, forro e testeira do beiral, calhas de
    ferro com meia-esquadria, condutores, chamine da parede de meia e chamine lateral, forro inclinado do sotao."""
    p = Piece(); fs = main_fs()
    cut = unary_union([CHIM_C, CHIM_S]).buffer(0.01, join_style=2)
    attic_in = INNER.buffer(0.0)
    roof_faces(p, fs, RTH, 40, inner=attic_in, cut=cut); ridge_caps(p, fs)
    bargeboard(p)
    ye = YE - T40 * OH; ys = ye - RTH
    full = sbox(-MX - OH, -MZ - OH, MX + OH, MZ + OH).difference(NOTCH).difference(mxp(NOTCH))
    footf = sbox(-MX, -MZ, MX, MZ)
    skip = unary_union([sbox(GA - GOH - 0.05, MZ - 0.01, GB + GOH + 0.05, MZ + OH + 0.2), CHIM_S.buffer(0.01, join_style=2)])
    eave_trim(p, full, footf, ys, ye + 0.012, CLIP, skip)
    # calhas: frente (x 3,8..6,75), lado (com a chamine no meio) e fundos (ate a parede de meia)
    X0, Z0 = MX + OH + 0.03, MZ + OH + 0.03; yt = ye - 0.03
    gutter_line(p, GB + GOH + 0.03, X0, Z0, yt, 0, mitre=((X0, 1),), caps=(True, False))
    gutter_line(p, -Z0, 2.05 - 0.01, X0, yt, 90, mitre=((-Z0, -1),), caps=(False, True))
    gutter_line(p, 2.9 + 0.01, Z0, X0, yt, 90, mitre=((Z0, 1),), caps=(True, False))
    gutter_line(p, -X0, 0.0, Z0, yt, 180, mitre=((-X0, -1),))
    for (x, z, r) in ((6.05, MZ, 0), (6.05, -MZ, 180)):
        p.merge(downspout(yt - 0.1, OH + 0.03 + 0.065), rot_y(r, (x, 0.0, z)))
    # chamines
    chimney(p, CHIM_C.intersection(CLIP), LV[2], 11.9, 2); chimney(p, CHIM_S, LV[2], 9.9, 2)
    # telhadinho da bay
    bfs = facets([(BAY_D, BAY_PL)]); roof_faces(p, bfs, 0.12, 35); ridge_caps(p, bfs, 0.05, 0.05, False)
    yb_e = YB - T35 * 0.14
    ext_y(p, 'trim', BAY_D.difference(BAY_POLY), yb_e - 0.12 - 0.02, yb_e - 0.12)
    ring = BAY_D.buffer(0.03, join_style=2).difference(BAY_D).intersection(sbox(-BIG, MZ + 0.01, BIG, BIG)); ext_y(p, 'trim', ring, yb_e - 0.26, yb_e + 0.012)
    # rufo de chumbo onde o telhadinho encosta na empena
    p.box('lead', BAYC - BAY_W - 0.1, BAYC + BAY_W + 0.1, YB + T35 * BAY_P - 0.02, YB + T35 * BAY_P + 0.16, MZ + 0.004, MZ + 0.016)
    return p
def out_roof():
    """Cobertura do anexo da cozinha (pivo: chao do mundo): 3 aguas de 35 graus de ardosia encostadas na parede dos fundos,
    cumeeira e espigoes, forro e testeira, calhas, condutor, rufo de chumbo na parede e chamine do fogao."""
    p = Piece(); fs = facets([(OUT_D.intersection(CLIP), OUT_P)])
    roof_faces(p, fs, RTH, 35, cut=CHIM_O.buffer(0.01, join_style=2)); ridge_caps(p, fs)
    ye = YO - T35 * 0.3; ys = ye - RTH; full = OUT_D; footf = sbox(-OXR, OZ1, OXR, -MZ)
    eave_trim(p, full, footf, ys, ye + 0.012, CLIP.intersection(sbox(-BIG, -BIG, BIG, -MZ - 0.001)), CHIM_O.buffer(0.01, join_style=2))
    X0, Z0 = OXR + 0.33, -OZ1 + 0.33; yt = ye - 0.03
    gutter_line(p, MZ, Z0, X0, yt, 90, mitre=((Z0, 1),), caps=(True, False))
    gutter_line(p, -X0, -0.56, Z0, yt, 180, mitre=((-X0, -1),), caps=(False, True))
    p.merge(downspout(yt - 0.1, 0.33 + 0.065), rot_y(90, (OXR, 0.0, OZ1 + 0.35)))
    # rufo de chumbo na parede dos fundos da casa (por cima da agua que encosta)
    for (g, P, oi) in fs:
        seg = g.intersection(sbox(0.0, -MZ - 0.25, BIG, -MZ))
        for q in polys(seg): sheared(p, 'lead', q, 0.075, 0.085, (lambda P: (lambda a, b: P.y(a, b)))(P))
    # forro liso da cozinha e da area de servico
    ext_y(p, 'ceil', OINNER, LV[0] + CH, LV[0] + CH + 0.012)
    chimney(p, CHIM_O.intersection(CLIP), LV[1], 6.3, 1)
    return p
# ============================================================================ fachadas (envoltoria de um pavimento da casa da direita, pivo: piso)
# (nome, eixo, coordenada da face, sentido para fora, u0, u1)
FACS = [('S', 'x', MZ, 1, 0.0, MX), ('E', 'z', MX, 1, -MZ + T, MZ - T), ('N', 'x', -MZ, -1, 0.0, MX)]
O_FACS = [('OE', 'z', OXR, 1, OZ1 + T, -MZ), ('ON', 'x', OZ1, -1, 0.0, OXR)]
KDOOR = (1.2, 2.0)                                                 # porta da sala de jantar para a cozinha (parede dos fundos)
BDOOR = (-8.22, -7.42)                                             # porta dos fundos (area de servico, parede lateral do anexo)
def ops_of(n, kind):
    """Vaos da fachada em u (x ou z do mundo): (a, b, ya, yb, tipo)."""
    if kind == '0':
        return {'S': [(BAYC - OPH, BAYC + OPH, 0.0, CH, 'bay'), (FDOOR[0], FDOOR[1], 0.0, FD_H, 'fdoor')],
                'E': [(1.4, 2.2, 0.9, 2.4, 'win')],
                'N': [(2.98, 3.68, 0.85, 2.4, 'win'), (4.6, 5.4, 1.65, 2.65, 'winl'), (KDOOR[0], KDOOR[1], 0.0, DH, 'idoor')],
                'OE': [(-6.3, -5.3, 0.95, 2.35, 'win'), (BDOOR[0], BDOOR[1], 0.0, DH, 'bdoor')],
                'ON': [(0.7, 1.4, 1.0, 2.3, 'win')]}.get(n, [])
    if kind == '1':
        return {'S': [(BAYC - OPH, BAYC + OPH, 0.0, CH, 'bay'), (4.3, 5.1, 0.95, 2.35, 'win1')],
                'E': [(0.0, 0.8, 0.9, 2.35, 'win1')],
                'N': [(2.45, 3.35, 0.85, 2.35, 'win1'), (4.6, 5.4, 1.65, 2.65, 'winl')]}.get(n, [])
    return []
def fac_frame(f):
    """Moldura local da fachada (x ao longo, +z para fora, face em z = 0): (matriz, sinal de u -> x local)."""
    n, ax, c, s = f[:4]
    if ax == 'x': return (rot_y(0, (0, 0, c)), 1) if s > 0 else (rot_y(180, (0, 0, c)), -1)
    return (rot_y(90, (c, 0, 0)), -1) if s > 0 else (rot_y(-90, (c, 0, 0)), 1)
def int_casing(p, a, b, ya, yb, stool=True, t=T):
    """Guarnicao interna larga (face interna em z = -t) e peitoril interno."""
    z0, z1 = -t - 0.018, -t
    for (u, v) in ((a - 0.11, a), (b, b + 0.11)): p.cham('trim', u, v, (ya - 0.09) if stool else 0.0, yb + 0.11, z0, z1, 0.004)
    p.cham('trim', a - 0.13, b + 0.13, yb + 0.11, yb + 0.15, z0 - 0.01, z1, 0.004)
    if stool: p.cham('trim', a - 0.14, b + 0.14, ya - 0.025, ya + 0.012, -t - 0.06, -t + 0.06, 0.004); p.box('trim', a - 0.11, b + 0.11, ya - 0.12, ya - 0.025, z0, z1)
def stone_sill(p, a, b, ya):
    prof_x(p, 'stone_c', a - 0.08, b + 0.08, [(-0.04, ya - 0.07), (0.05, ya - 0.07), (0.06, ya - 0.055), (0.062, ya - 0.02), (0.0, ya + 0.004), (-0.04, ya + 0.02)])
def stone_lintel(p, a, b, yb, key=True):
    p.box('stone_c', a - 0.1, b + 0.1, yb, yb + 0.22, 0.0, 0.025)
    prof_x(p, 'stone_c', a - 0.12, b + 0.12, [(0.0, yb + 0.22), (0.045, yb + 0.22), (0.045, yb + 0.235), (0.03, yb + 0.255), (0.0, yb + 0.26)])
    if key:
        xm = (a + b) / 2
        p.hull('stone_c', [(x, y, z) for (x, y) in ((xm - 0.07, yb - 0.03), (xm + 0.07, yb - 0.03), (xm - 0.095, yb + 0.25), (xm + 0.095, yb + 0.25)) for z in (0.0, 0.045)])
def sash_frame(q, a, b, ya, yb, lites=2, z0=-0.2):
    """Caixilho de madeira com 2 folhas de guilhotina (2 sobre 2), cordao da folha de cima e fecho de latao."""
    f = 0.05; xm = (a + b) / 2
    q.box('frame', a, a + f, ya, yb, z0, z0 + 0.15); q.box('frame', b - f, b, ya, yb, z0, z0 + 0.15); q.box('frame', a + f, b - f, yb - f, yb, z0, z0 + 0.15)
    q.box('frame', a + f, b - f, ya, ya + 0.02, z0, z0 + 0.15)
    mid = ya + 0.02 + (yb - f - ya - 0.02) * 0.5
    sash(q, a + f, b - f, ya + 0.025, mid + 0.02, z0 + 0.04, z0 + 0.08, lites, 0.075)
    sash(q, a + f + 0.008, b - f - 0.008, mid - 0.02, yb - f, z0 + 0.1, z0 + 0.14, lites, 0.05)
    q.box('brass', xm - 0.04, xm + 0.04, mid + 0.015, mid + 0.03, z0 + 0.07, z0 + 0.085)
def hung_window(p, a, b, ya, yb, key=True):
    sash_frame(p, a, b, ya, yb); stone_sill(p, a, b, ya); stone_lintel(p, a, b, yb, key)
def landing_window(p, a, b, ya, yb):
    """Janela da escada: caixilho fixo com vitral geometrico (losangos coloridos) e peitoril de pedra."""
    f = 0.05; z0, z1 = -0.18, -0.06
    for (u, v) in ((a, a + f), (b - f, b)): p.box('frame', u, v, ya, yb, z0, z1)
    for (y0, y1) in ((ya, ya + f), (yb - f, yb)): p.box('frame', a + f, b - f, y0, y1, z0, z1)
    p.box('glass', a + f - 0.004, b - f + 0.004, ya + f - 0.004, yb - f + 0.004, -0.123, -0.117)
    cx, cy = (a + b) / 2, (ya + yb) / 2; w, h = (b - a) / 2 - f - 0.04, (yb - ya) / 2 - f - 0.04
    for (dx, dy, m) in ((0, 0, 'flag_r'), (-w * 0.55, h * 0.5, 'blue'), (w * 0.55, h * 0.5, 'blue'), (-w * 0.55, -h * 0.5, 'leaf2'), (w * 0.55, -h * 0.5, 'leaf2')):
        s = 0.11 if m == 'flag_r' else 0.07
        p.hull(m, [(cx + dx + ex, cy + dy + ey, z) for (ex, ey) in ((s, 0), (-s, 0), (0, s * 1.4), (0, -s * 1.4)) for z in (-0.117, -0.114)])
    for t in (-1, 1):
        seg_cyl(p, 'dark', (cx - w, cy - t * h, -0.113), (cx + w, cy + t * h, -0.113), 0.006, 4)
    stone_sill(p, a, b, ya); stone_lintel(p, a, b, yb, False)
def front_door_frame(p, a, b, yh):
    """Porta da frente: arco pleno de tijolo com aduelas de pedra alternadas, bandeira em leque, batentes e soleira de pedra."""
    xm = (a + b) / 2; r = (b - a) / 2; yc = yh - r
    # tympanum: tijolo que fecha os cantos do vao retangular em volta do arco
    tym = sbox(a, yc, b, yh).difference(Point(xm, yc).buffer(r, 32))
    for g in polys(tym): prof_z(p, 'brick', -T, 0.0, list(g.exterior.coords)[:-1])
    for k in range(13):   # aduelas
        t0 = math.pi * k / 13; t1 = math.pi * (k + 1) / 13; m = 'stone_c' if k % 2 == 0 else 'brick_y'
        pts = [(xm + rr * math.cos(t), yc + rr * math.sin(t)) for (rr, t) in ((r, t0), (r + 0.2, t0), (r + 0.2, t1), (r, t1))]
        p.hull(m, [(x, y, z) for (x, y) in pts for z in (0.0, 0.03)])
    p.hull('stone_c', [(x, y, z) for (x, y) in ((xm - 0.08, yc + r - 0.03), (xm + 0.08, yc + r - 0.03), (xm - 0.1, yc + r + 0.24), (xm + 0.1, yc + r + 0.24)) for z in (0.0, 0.065)])
    for s in (-1, 1): p.box('stone_c', *sorted((xm + s * r, xm + s * (r + 0.22))), yc - 0.14, yc, 0.0, 0.04)   # impostas
    z0, z1 = -0.2, -0.1; f = 0.06; yt = 2.2
    for (u, v) in ((a, a + f), (b - f, b)): p.box('trim', u, v, 0.0, yc, z0, z1)
    p.box('trim', a + f, b - f, yt, yt + 0.06, z0, z1)
    fan = Point(xm, yc).buffer(r, 32).intersection(sbox(a, yt + 0.06, b, yh))
    for g in polys(fan.difference(Point(xm, yc).buffer(r - 0.05, 32))): prof_z(p, 'trim', z0, z1, list(g.exterior.coords)[:-1])
    for g in polys(sbox(a + f, yt + 0.06, b - f, yc)): prof_z(p, 'glass', -0.153, -0.147, list(g.exterior.coords)[:-1])
    for g in polys(Point(xm, yc).buffer(r - 0.05, 32).intersection(sbox(a, yc, b, yh))): prof_z(p, 'glass', -0.153, -0.147, list(g.exterior.coords)[:-1])
    for k in range(1, 6):
        t = math.pi * k / 6; seg_cyl(p, 'trim', (xm, yc, -0.15), (xm + (r - 0.04) * math.cos(t), yc + (r - 0.04) * math.sin(t), -0.15), 0.01, 4)
    disc_z(p, 'trim', 0.08, -0.16, -0.14, xm, yc, 14)
    p.box('stone_c', a + 0.002, b - 0.002, -0.012, 0.004, -T - 0.01, 0.02)
def rear_door_frame(p, a, b, yh):
    for (u, v) in ((a, a + 0.06), (b - 0.06, b)): p.box('frame', u, v, 0.0, yh, -0.2, -0.08)
    p.box('frame', a + 0.06, b - 0.06, yh - 0.06, yh, -0.2, -0.08)
    p.box('stone_c', a + 0.002, b - 0.002, -0.012, 0.004, -T - 0.01, 0.05); stone_lintel(p, a, b, yh, False)
def facade(f, kind, gaps):
    """Uma fachada de um pavimento na moldura local: parede de tijolo (camada interna de gesso), janelas e portas. 'gaps' recebe
    as faixas (no plano do mundo) onde as faixas de tijolo amarelo param."""
    M, us = fac_frame(f); q = Piece(); n = f[0]
    l0, l1 = sorted((us * f[4], us * f[5]))
    ops = [(*sorted((us * a, us * b)), ya, yb, k) for (a, b, ya, yb, k) in ops_of(n, kind)]
    y0 = GY - Y0 if kind == '0' else 0.0
    segs = [(l0, l1, 'brick')]
    if n == 'N' and kind == '0':                                     # trecho dentro do anexo: as 2 faces sao de gesso
        c = us * (OXR - T); segs = [(min(c, l1), l1, 'plaster'), (l0, min(c, l1), 'brick')] if us < 0 else [(l0, c, 'plaster'), (c, l1, 'brick')]
    for (u0, u1, om) in segs:
        hs = [o[:4] for o in ops if o[0] < u1 and o[1] > u0]
        wall2(q, 'x', u0, u1, 0.0, -T, hs, y0, H, om, 'plaster')
    for (a, b, ya, yb, k) in ops:
        if k == 'win': hung_window(q, a, b, ya, yb, True); int_casing(q, a, b, ya, yb)
        elif k == 'win1': hung_window(q, a, b, ya, yb, False); int_casing(q, a, b, ya, yb)
        elif k == 'winl': landing_window(q, a, b, ya, yb); int_casing(q, a, b, ya, yb)
        elif k == 'fdoor': front_door_frame(q, a, b, yb); int_casing(q, a, b, 0.0, yb, False)
        elif k == 'bdoor': rear_door_frame(q, a, b, yb); int_casing(q, a, b, 0.0, yb, False)
        elif k == 'idoor':                                          # porta interna na parede grossa: guarnicao dos 2 lados e soleira
            int_casing(q, a, b, 0.0, yb, False)
            for (u, v) in ((a - 0.11, a), (b, b + 0.11)): q.cham('trim', u, v, 0.0, yb + 0.11, 0.0, 0.018, 0.004)
            q.cham('trim', a - 0.13, b + 0.13, yb + 0.11, yb + 0.15, 0.0, 0.028, 0.004)
            q.box('trim', a, a + 0.02, 0.0, yb, -T, 0.0); q.box('trim', b - 0.02, b, 0.0, yb, -T, 0.0); q.box('trim', a + 0.02, b - 0.02, yb - 0.02, yb, -T, 0.0)
        if k in ('win', 'win1', 'winl', 'fdoor', 'bdoor'):
            ga, gb = (a - 0.13, b + 0.13) if k != 'fdoor' else (a - 0.25, b + 0.25)
            pts = [trimesh.transformations.transform_points([[x, 0, z]], M)[0] for (x, z) in ((ga, -0.05), (gb, -0.05), (gb, 0.3), (ga, 0.3))]
            gaps.append(Polygon([(v[0], v[2]) for v in pts]))
    return q, M

# ---------------------------------------------------------------------------- bay window chanfrada (2 andares)
BAY2 = Polygon([(BAYC - BAY_W - 1.0, MZ - 1.0)] + BAY_O[1:3] + [(BAYC + BAY_W + 1.0, MZ - 1.0)])
BAY_IN = BAY2.buffer(-BT, join_style=2).intersection(sbox(-BIG, MZ - T, BIG, BIG))      # vao + interior da bay
BAY_RING = BAY_POLY.difference(BAY2.buffer(-BT, join_style=2))
BAY_RB = BAY_POLY.difference(BAY2.buffer(-0.12, join_style=2)); BAY_RP = BAY_RING.difference(BAY_RB)
BAY_WIN = [(0.56, 0), (0.8, 1), (0.56, 2)]                          # (largura, face) das janelas da bay
def bay_faces():
    """Faces da bay: (centro externo x, z, angulo, comprimento externo)."""
    o = BAY_O; fs = []
    for i in range(3):
        (x0, z0), (x1, z1) = o[i], o[i + 1]; dx, dz = x1 - x0, z1 - z0; L = math.hypot(dx, dz)
        nx, nz = dz / L, -dx / L
        fs.append(((x0 + x1) / 2, (z0 + z1) / 2, math.degrees(math.atan2(nx, nz)), L))
    return fs
def bay(p, kind):
    """Um pavimento da bay: embasamento, peitoril e verga de pedra corridos, montantes de tijolo, 3 janelas de guilhotina,
    cornija de pedra com dentilhoes; no andar, a parede sobe ate o telhadinho."""
    sill, head = (0.75, 2.45) if kind == '0' else (0.75, 2.35)
    slots = []
    for (w, i) in BAY_WIN:
        cx, cz, ang, L = bay_faces()[i]; M = rot_y(ang, (cx, 0, cz))
        pts = trimesh.transformations.transform_points([[x, 0, z] for (x, z) in ((-w / 2, -BT - 0.02), (w / 2, -BT - 0.02), (w / 2, 0.02), (-w / 2, 0.02))], M)
        slots.append(Polygon([(v[0], v[2]) for v in pts]))
        q = Piece(); sash_frame(q, -w / 2, w / 2, sill, head, 2, -0.2); p.merge(q, M)
    sl = unary_union(slots); y0 = GY - Y0 if kind == '0' else 0.0
    for (g, m) in ((BAY_RB, 'brick'), (BAY_RP, 'plaster')):
        if kind == '0': ext_y(p, 'brick_d' if m == 'brick' else m, g, y0, 0.0)
        ext_y(p, m, g, 0.0, sill); ext_y(p, m, g.difference(sl), sill, head); ext_y(p, m, g, head, H)
    ring = lambda d: BAY_POLY.buffer(d, join_style=2).difference(BAY_POLY).intersection(sbox(-BIG, MZ, BIG, BIG))
    ext_y(p, 'stone_c', ring(0.05), sill - 0.08, sill); ext_y(p, 'stone_c', ring(0.03), sill - 0.1, sill - 0.08)       # peitoril corrido
    ext_y(p, 'stone_c', ring(0.025), head, head + 0.22); ext_y(p, 'stone_c', ring(0.045), head + 0.22, head + 0.26)     # verga corrida
    # peitoril interno (tabua) e guarnicao das janelas por dentro
    ext_y(p, 'trim', BAY_IN.intersection(BAY2.buffer(-BT + 0.0, join_style=2)).difference(BAY2.buffer(-BT - 0.05, join_style=2)).intersection(sbox(-BIG, MZ + 0.01, BIG, BIG)), sill - 0.02, sill + 0.012)
    if kind == '1':   # a bay continua acima do andar ate o telhadinho
        bfs = facets([(BAY_D, BAY_PL)])
        for (g, m) in ((BAY_RB, 'brick'), (BAY_RP, 'plaster')):
            for (gg, P, oi) in bfs: on_plane(P, g.intersection(gg), H, -0.12 - LV[1], m, p)
    if kind == '0':
        ext_y(p, 'stone_c', ring(0.035), -0.08, 0.0)
def belts(p, kind, gaps):
    """Faixas em anel no contorno da casa (e da bay): embasamento escuro e capa de pedra no terreo, faixa de pedra no nivel do
    andar, faixas de tijolo amarelo na altura das vergas (param nas janelas)."""
    out = FOOT.union(OFOOT) if kind == '0' else FOOT
    full = out.union(BAY_POLY); clip = sbox(0.0, -BIG, BIG, BIG)
    ring = lambda g, d: g.buffer(d, join_style=2).difference(g).intersection(clip).difference(sbox(-0.5, -BIG, 0.0005, BIG))
    G = unary_union(gaps) if gaps else Polygon()
    steps = sbox(FDOOR[0] - 0.3, MZ - 0.1, FDOOR[1] + 0.3, MZ + 1.2)
    if kind == '0':
        ext_y(p, 'brick_d', ring(out, 0.025).difference(steps).difference(BAY_POLY), GY - Y0, -0.08)
        ext_y(p, 'stone_c', ring(out, 0.04).difference(steps).difference(BAY_POLY), -0.08, 0.0)
        for (yy0, yy1) in ((1.05, 1.2), (2.42, 2.57)): ext_y(p, 'brick_y', ring(out, 0.006).difference(G).difference(BAY_POLY.buffer(0.1)), yy0, yy1)
    if kind == '1':
        ext_y(p, 'stone_c', ring(full, 0.05), -0.12, 0.06); prof_ring(p, full, clip)
        for (yy0, yy1) in ((1.05, 1.2), (2.37, 2.52)): ext_y(p, 'brick_y', ring(out, 0.006).difference(G).difference(BAY_POLY.buffer(0.1)), yy0, yy1)
def prof_ring(p, full, clip):
    """Dentilhoes embaixo da faixa de pedra do andar, na bay."""
    for (cx, cz, ang, L) in bay_faces():
        n = int((L - 0.1) / 0.12)
        for k in range(n):
            u = -L / 2 + 0.05 + (k + 0.5) * (L - 0.1) / n; q = Piece(); q.box('stone_c', u - 0.03, u + 0.03, -0.2, -0.12, -0.04, 0.0); p.merge(q, rot_y(ang, (cx, 0, cz)))
def front_steps(p):
    """3 degraus de pedra com focinho, muretas laterais de tijolo com capa e raspador de botas (pivo: piso do terreo)."""
    a, b = FDOOR[0] - 0.2, FDOOR[1] + 0.2
    for k in range(3):
        yt = -0.15 * k; z1 = MZ + 0.3 * (k + 1)
        p.cham('stone_c', a, b, yt - 0.15, yt, MZ, z1, 0.008); prof_x(p, 'stone_c', a, b, [(z1, yt - 0.03), (z1 + 0.025, yt - 0.025), (z1 + 0.025, yt), (z1, yt)])
    p.box('conc_s', a, b, GY - Y0, -0.45 - 0.15 + 0.0, MZ, MZ + 0.9)
    for (u, v) in ((a - 0.22, a), (b, b + 0.22)):
        p.hull('brick', [(x, y, z) for x in (u, v) for (y, z) in ((-Y0, MZ), (0.55, MZ), (0.25, MZ + 0.9), (-Y0, MZ + 0.9))])
        p.hull('stone_c', [(x, y, z) for x in (u - 0.03, v + 0.03) for (y, z) in ((0.55, MZ), (0.62, MZ), (0.32, MZ + 0.95), (0.25, MZ + 0.95))])
    x = b + 0.11; p.box('iron', x - 0.12, x + 0.12, -0.2, -0.19, MZ + 0.5, MZ + 0.505)
def chimney_breast(p, y0, y1):
    ext_y(p, 'brick', CHIM_S, y0, y1)
def shell(kind):
    """Envoltoria de um pavimento ('0' terreo, '1' andar) da casa da direita: 3 fachadas de tijolo (a parede de meia e de gesso),
    bay window, faixas, porta com arco e degraus, anexo da cozinha no terreo e a chamine lateral."""
    p = Piece(); gaps = []
    for f in FACS + (O_FACS if kind == '0' else []):
        q, M = facade(f, kind, gaps); p.merge(q, M)
    y0 = GY - Y0 if kind == '0' else 0.0
    p.box('plaster', 0.0, PW, y0, H, -MZ + T, MZ - T)
    if kind == '0': p.box('plaster', 0.0, PW, y0, H, OZ1 + T, -MZ)
    bay(p, kind); belts(p, kind, gaps); chimney_breast(p, y0, H)
    if kind == '0':
        front_steps(p); p.merge(wall_lantern(), tr(FDOOR[1] + 0.35, 1.95, MZ))
        p.merge(wall_lantern(), rot_y(90, (OXR, 1.95, BDOOR[0] - 0.3)))
    return p

# ---------------------------------------------------------------------------- sotao: paredes de meia-agua, empena com janela, parede de meia ate o telhado
GW = (1.62, 2.38, 1.0, 1.85)                                       # janela da empena (x0, x1, peitoril, verga) no sotao
def shell_a():
    """Envoltoria do sotao (pivo: piso do sotao): paredes de meia-agua com o topo seguindo as aguas, empena de tijolo com
    janela de guilhotina e peitoril de pedra, parede de meia de gesso ate o telhado (recortada na chamine)."""
    p = Piece(); fs = main_fs(); off = -RTH - LV[2]
    def wall_pair(poly_b, poly_p, y0=0.0):
        under_roof(p, fs, poly_b, y0, off, 'brick'); under_roof(p, fs, poly_p, y0, off, 'plaster')
    zb = MZ - 0.15
    # frente: fora da empena, empena (colunas da janela) e embaixo/em cima da janela
    for (u, v) in ((0.0, GA), (GB, MX)):
        wall_pair(sbox(u, zb, v, MZ), sbox(u, MZ - T, v, zb))
    for (u, v) in ((GA, GW[0]), (GW[1], GB)):
        wall_pair(sbox(u, zb, v, MZ), sbox(u, MZ - T, v, zb))
    ext_y(p, 'brick', sbox(GW[0], zb, GW[1], MZ), 0.0, GW[2]); ext_y(p, 'plaster', sbox(GW[0], MZ - T, GW[1], zb), 0.0, GW[2])
    wall_pair(sbox(GW[0], zb, GW[1], MZ), sbox(GW[0], MZ - T, GW[1], zb), GW[3])
    q = Piece(); sash_frame(q, GW[0], GW[1], GW[2], GW[3], 2); stone_sill(q, GW[0], GW[1], GW[2])
    prof_x(q, 'stone_c', GW[0] - 0.08, GW[1] + 0.08, [(0.0, GW[3]), (0.05, GW[3]), (0.05, GW[3] + 0.05), (0.0, GW[3] + 0.1)])
    int_casing(q, GW[0], GW[1], GW[2], GW[3]); p.merge(q, tr(0, 0, MZ))
    # lado e fundos
    wall_pair(sbox(MX - 0.15, -MZ + T, MX, MZ - T), sbox(MX - T, -MZ + T, MX - 0.15, MZ - T))
    wall_pair(sbox(0.0, -MZ, MX, -MZ + 0.15), sbox(0.0, -MZ + 0.15, MX, -MZ + T))
    under_roof(p, fs, sbox(0.0, -MZ + T, PW, MZ - T).difference(CHIM_C), 0.0, off, 'plaster')
    return p
# ============================================================================ paredes internas, pisos, lajes e escada (casa da direita, pivo: piso)
ZBATH = 1.66                                                       # parede do banheiro do andar (z 1,6..1,72)
ZK = -6.9                                                          # parede entre a cozinha e a area de servico (anexo)
# (eixo, linha central, de, ate, espessura, portas [(a, b)])
WALLS = {'0': [('z', XH, -MZ + T, MZ - T, TP, [(2.6, 3.4), (-1.1, -0.3)]), ('x', 0.0, PW, XH - TP / 2, TP, []),
               ('x', ZK, PW, OXR - T, TP, [(1.5, 2.3)])],
         '1': [('z', XH, -MZ + T, MZ - T, TP, [(0.45, 1.25), (-1.1, -0.3)]), ('x', 0.0, PW, XH - TP / 2, TP, []),
               ('x', ZBATH, XH + TP / 2, MX - T, TP, [(4.4, 5.2)])],
         'a': []}
def wall_rect(w):
    ax, c, a, b, t, ds = w
    return sbox(a, c - t / 2, b, c + t / 2) if ax == 'x' else sbox(c - t / 2, a, c + t / 2, b)
def door_rects(w, pad=0.0):
    ax, c, a, b, t, ds = w
    return [sbox(u, c - t / 2 - pad, v, c + t / 2 + pad) if ax == 'x' else sbox(c - t / 2 - pad, u, c + t / 2 + pad, v) for (u, v) in ds]
def wall_u(ws): return unary_union([wall_rect(w) for w in ws] + [Polygon()]).difference(unary_union([r for w in ws for r in door_rects(w, 0.01)] + [Polygon()]))
WALL_U = {k: wall_u(v) for k, v in WALLS.items()}
STAIR_Z = sbox(XH + TP / 2, -MZ + T, MX - T, ZF)                  # vao da escada em U (x 3,94..6,1, z -4,2..-1,2)
BREAST = [sbox(PW, -2.6, 0.55, -1.2), sbox(PW, 1.3, 0.55, 2.7)]    # peitos de lareira na parede de meia (jantar/quarto e sala/quarto)
BREAST_K = sbox(PW, ZK + TP / 2, 0.6, -5.6)                       # peito do fogao da cozinha
BAY_STRIP = sbox(BAYC - OPH, MZ - T, BAYC + OPH, MZ)                # vao da bay na parede (o piso passa por cima com soleira)
def floor_poly(kind):
    g = INNER.union(BAY_IN.intersection(sbox(-BIG, MZ, BIG, BIG))) if kind != 'a' else INNER
    if kind == '0': g = g.union(OINNER)
    return g
def free_poly(kind):
    br = BREAST + ([BREAST_K] if kind == '0' else [])
    return floor_poly(kind).difference(WALL_U[kind]).difference(unary_union(br)) if kind != 'a' else floor_poly(kind).difference(sbox(XH - TP / 2, -MZ, XH + TP / 2, ZF)).difference(CHIM_C)
def door_cuts(kind):
    cz = []
    for w in WALLS[kind]:
        ax, c, a, b, t, ds = w
        for (u, v) in ds: cz.append(sbox(u - 0.12, c - t / 2 - 0.05, v + 0.12, c + t / 2 + 0.05) if ax == 'x' else sbox(c - t / 2 - 0.05, u - 0.12, c + t / 2 + 0.05, v + 0.12))
    if kind == '0':
        cz += [sbox(FDOOR[0] - 0.12, MZ - T - 0.1, FDOOR[1] + 0.12, MZ), sbox(KDOOR[0] - 0.12, -MZ - 0.1, KDOOR[1] + 0.12, -MZ + T + 0.1),
               sbox(OXR - T - 0.1, BDOOR[0] - 0.12, OXR, BDOOR[1] + 0.12)]
    return unary_union(cz + [Polygon()])
def casing(p, ax, c, t, a, b, h=DH):
    """Batente e guarnicoes largas dos 2 lados de um vao de porta em parede interna (com plinto na base)."""
    for s in (-1, 1):
        v0 = c + s * t / 2; v1 = v0 + s * 0.018
        for (u0, u1) in ((a - 0.11, a), (b, b + 0.11)):
            bx(p, 'trim', ax, u0, u1, 0.0, h + 0.11, v0, v1); bx(p, 'trim', ax, u0 - 0.005, u1 + 0.005, 0.0, 0.24, v0, v0 + s * 0.028)
        bx(p, 'trim', ax, a - 0.13, b + 0.13, h + 0.11, h + 0.15, v0, v0 + s * 0.028)
    bx(p, 'trim', ax, a, a + 0.015, 0.0, h, c - t / 2, c + t / 2); bx(p, 'trim', ax, b - 0.015, b, 0.0, h, c - t / 2, c + t / 2)
    bx(p, 'trim', ax, a + 0.015, b - 0.015, h - 0.015, h, c - t / 2, c + t / 2)
def mouldings(p, kind):
    """Rodape alto (22 cm, com moldura), sanca de 2 degraus no teto e, no hall, rodameio. Param nas portas."""
    free = free_poly(kind); cut = door_cuts(kind)
    stair = sbox(XH + TP / 2 - 0.01, -MZ + T - 0.01, MX - T + 0.01, ZF + 0.03)
    band = lambda d: free.difference(free.buffer(-d, join_style=2))
    sk = band(0.016).difference(cut)
    if kind != 'a': sk = sk.difference(stair)
    else: sk = sk.difference(sbox(XH, -MZ, MX, ZF + 0.03))
    ext_y(p, 'trim', sk, 0.0, 0.2); ext_y(p, 'trim', band(0.022).difference(cut).intersection(sk.buffer(0.01)), 0.19, 0.22)
    if kind == 'a': return
    fc = floor_poly(kind).difference(unary_union([wall_rect(w) for w in WALLS[kind]] + BREAST + ([BREAST_K] if kind == '0' else [])))
    bandc = lambda d: fc.difference(fc.buffer(-d, join_style=2))
    ext_y(p, 'trim', bandc(0.06), CH - 0.04, CH); ext_y(p, 'trim', bandc(0.03), CH - 0.13, CH - 0.04)
    hall = sbox(XH + TP / 2, ZF, MX - T, MZ - T) if kind == '0' else sbox(XH + TP / 2, ZF, MX - T, ZBATH - TP / 2)
    ext_y(p, 'trim', band(0.018).intersection(hall.buffer(0.03)).difference(cut).difference(stair), 0.88, 0.93)
def walls(kind):
    """Paredes internas de um pavimento: divisorias de gesso, portas com batente e guarnicoes, rodapes, sancas e rodameio."""
    p = Piece()
    for w in WALLS[kind]:
        ax, c, a, b, t, ds = w
        wall_grid(p, ax, a, b, c - t / 2, c + t / 2, [(u, v, 0.0, DH) for (u, v) in ds], 0.0, CH, 'plaster')
        for (u, v) in ds: casing(p, ax, c, t, u, v)
    for g in (BREAST + ([BREAST_K] if kind == '0' else [])) if kind != 'a' else []:
        ext_y(p, 'plaster', g, 0.0, CH)
    if kind == 'a':   # parede da escada no sotao ate o telhado
        under_roof(p, main_fs(), sbox(XH - TP / 2, -MZ + T, XH + TP / 2, ZF), 0.0, -RTH - LV[2], 'plaster')
    mouldings(p, kind)
    return p

# ---------------------------------------------------------------------------- pisos
def boards(p, poly, y0, y1, mat='wood', w=0.14, axis='z'):
    """Assoalho de tabuas corridas (14 cm) com junta escura."""
    b = poly.bounds
    if axis == 'z':
        for i in range(int(math.floor(b[0] / w)), int(math.ceil(b[2] / w))):
            q = sbox(i * w + 0.0015, b[1], (i + 1) * w - 0.0015, b[3]).intersection(poly)
            if q.area > 1e-5: ext_y(p, mat, q, y0, y1)
    else:
        for j in range(int(math.floor(b[1] / w)), int(math.ceil(b[3] / w))):
            q = sbox(b[0], j * w + 0.0015, b[2], (j + 1) * w - 0.0015).intersection(poly)
            if q.area > 1e-5: ext_y(p, mat, q, y0, y1)
    ext_y(p, 'dkwood', poly.buffer(-0.001, join_style=2), y0, y1 - 0.003)
def checker(p, poly, y0, y1, s=0.2, ma='tile_b', mb='tile_w2', border='tile_r'):
    """Ladrilho hidraulico em xadrez na diagonal com barra de terracota (piso do hall)."""
    inner = poly.buffer(-0.15, join_style=2)
    ext_y(p, border, poly.difference(inner), y0, y1)
    b = inner.bounds; cx, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; n = int(max(b[2] - b[0], b[3] - b[1]) / s) + 3
    for i in range(-n, n):
        for j in range(-n, n):
            sq = affinity.rotate(sbox(i * s + 0.002, j * s + 0.002, (i + 1) * s - 0.002, (j + 1) * s - 0.002), 45, origin=(0, 0))
            sq = affinity.translate(sq, cx, cz); q = sq.intersection(inner)
            if q.area > 1e-5: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
    ext_y(p, 'grille', inner.buffer(-0.001, join_style=2), y0, y1 - 0.003)
HALL0 = sbox(XH + TP / 2, ZF, MX - T, MZ - T)
KIT_F = sbox(PW, OZ1 + T, OXR - T, -MZ)
BATH_F = sbox(XH + TP / 2, ZBATH + TP / 2, MX - T, MZ - T)
LIGHTS = {'0': [(1.98, 2.3, 'rose'), (1.98, -2.1, 'rose'), (5.02, 2.2, 'lan'), (1.33, -5.7, 'lan'), (1.33, -7.65, 'lan')],
          '1': [(1.98, 2.2, 'rose'), (1.98, -2.1, 'rose'), (5.02, 0.2, 'lan'), (5.02, 2.95, 'lan')],
          'a': []}
def ceiling_lights(p, y, kind):
    """Rosetas de gesso com pendente de vidro nas salas e quartos; arandela de teto nos outros comodos."""
    for (x, z, k) in LIGHTS[kind]:
        if k == 'rose':
            lathe(p, 'trim', [(0.3, y), (0.28, y - 0.02), (0.2, y - 0.03), (0.12, y - 0.045), (0.05, y - 0.06), (0.0, y - 0.065)], x, z, sec=28)
            for a in np.linspace(0, 2 * math.pi, 12, endpoint=False): p.sphere('trim', 0.025, x + 0.2 * math.cos(a), y - 0.03, z + 0.2 * math.sin(a), 0)
            seg_cyl(p, 'brass', (x, y - 0.06, z), (x, y - 0.6, z), 0.006, 4)
            lathe(p, 'lamp_glass', [(0.0, y - 0.6), (0.06, y - 0.6), (0.17, y - 0.72), (0.2, y - 0.8), (0.14, y - 0.84), (0.0, y - 0.86)], x, z, sec=18)
        else:
            p.cyl('brass', 0.08, y - 0.03, y, x, z, 14); lathe(p, 'lamp_glass', [(0.07, y - 0.03), (0.11, y - 0.12), (0.06, y - 0.2), (0.0, y - 0.21)], x, z, sec=16)
def thresholds(kind):
    r = [d for w in WALLS[kind] for d in door_rects(w)]
    if kind == '0': r.append(sbox(KDOOR[0], -MZ, KDOOR[1], -MZ + T))
    return r
def floors(p, kind, y1=0.0):
    thr = thresholds(kind)
    free = floor_poly(kind).difference(WALL_U[kind]).difference(unary_union(thr + [Polygon()]))
    if kind == '0':
        hall = free.intersection(HALL0); checker(p, hall, y1 - 0.012, y1)
        k = free.intersection(KIT_F); tiles(p, k, y1 - 0.012, y1, 0.225, 'quarry', 0.003, 'grille')
        boards(p, free.difference(HALL0).difference(KIT_F), y1 - 0.012, y1)
    elif kind == '1':
        bath = free.intersection(BATH_F); tiles(p, bath, y1 - 0.012, y1, 0.12, 'tile_hex', 0.003, 'grille')
        boards(p, free.difference(BATH_F).difference(STAIR_Z), y1 - 0.012, y1)
    else:
        boards(p, free.difference(STAIR_Z), y1 - 0.012, y1, 'wood', 0.18, 'x')
    for g in thr: ext_y(p, 'wood', g, y1 - 0.012, y1 + 0.004)             # soleiras de madeira nas portas
    if kind != 'a': ext_y(p, 'wood', BAY_STRIP, y1, y1 + 0.006)            # soleira no vao da bay (em cima da parede)
def slab(kind):
    """Laje de um pavimento (pivo: piso). '0': contrapiso no chao com ladrilho xadrez no hall, ladrilho de barro na cozinha e
    assoalho; '1' e 'a': forro de gesso do pavimento de baixo, estrutura, vao da escada e pisos (sextavado no banheiro)."""
    p = Piece(); fp = floor_poly(kind)
    if kind == '0':
        ext_y(p, 'conc_s', fp.difference(unary_union(thresholds(kind))), GY - Y0, -0.012)
        for g in thresholds(kind): ext_y(p, 'conc_s', g, GY - Y0 + 0.002, -0.012)
        floors(p, kind); return p
    below = floor_poly('1') if kind == 'a' else floor_poly('0').difference(OINNER)
    hole = STAIR_Z
    ext_y(p, 'ceil', below.difference(hole), -ST, -ST + 0.012); ext_y(p, 'conc_s', below.difference(hole), -ST + 0.012, -0.012)
    if kind == 'a': ext_y(p, 'conc_s', below.difference(fp), -0.012, 0.0)                          # bay: topo da laje embaixo do telhadinho
    floors(p, kind)
    p.box('dark', XH + TP / 2 + 0.005, MX - T - 0.005, -0.04, 0.003, ZF - 0.003, ZF + 0.05)           # focinho na borda da laje
    ceiling_lights(p, -ST, '0' if kind == '1' else '1')
    return p

# ---------------------------------------------------------------------------- escada em U de madeira (entre 2 pavimentos)
SXC = (SXB[0] + SXA[1]) / 2; SXW = (SXA[1] - SXB[0]) / 2          # centro (5,02) e meia-largura (1,08) da caixa da escada
def stair(kind):
    """Escada em U de madeira (pivo: piso de baixo): lance A sobe para -z junto da parede lateral ate o patamar, lance B volta
    para +z. Degraus de madeira com passadeira vermelha e varoes de latao, pilares torneados com pinha, balaustres torneados
    brancos e corrimao de mogno. No terreo, o vao embaixo do lance A e do patamar e fechado com almofadas."""
    p = Piece(); n2 = SNR // 2; yL = n2 * SRR; xg = 0.06; xw = SXW; HZI = -MZ + T
    pr = [(ZF, 0.0)]
    for i in range(1, n2): pr += [(ZF - (i - 1) * STRD, i * SRR), (ZF - i * STRD, i * SRR)]
    pr += [(ZM, yL - 0.25), (ZF - 0.9, 0.0)]
    prof_x(p, 'wood', xg, xw, pr)
    pr = [(ZM, yL)]
    for j in range(1, n2): pr += [(ZM + (j - 1) * STRD, yL + j * SRR), (ZM + j * STRD, yL + j * SRR)]
    pr += [(ZF, H - ST - 0.25), (ZM, yL - 0.2)]
    prof_x(p, 'wood', -xw, -xg, pr)
    p.box('wood', -xw, xw, yL - 0.2, yL, HZI, ZM)
    # passadeira com varoes (lances e patamar)
    for i in range(1, n2):
        zf = ZF - (i - 1) * STRD; y = i * SRR
        p.box('carpet_r', xg + 0.2, xw - 0.2, y, y + 0.006, zf - STRD, zf + 0.004); p.box('carpet_r', xg + 0.2, xw - 0.2, y - SRR, y, zf + 0.004, zf + 0.01)
        seg_cyl(p, 'brass', (xg + 0.16, y + 0.012, zf - STRD + 0.015), (xw - 0.16, y + 0.012, zf - STRD + 0.015), 0.006, 6)
        zb = ZM + (i - 1) * STRD; y = yL + i * SRR
        p.box('carpet_r', -xw + 0.2, -xg - 0.2, y, y + 0.006, zb - 0.004, zb + STRD); p.box('carpet_r', -xw + 0.2, -xg - 0.2, y - SRR, y, zb - 0.01, zb - 0.004)
        seg_cyl(p, 'brass', (-xw + 0.16, y + 0.012, zb + STRD - 0.015), (-xg - 0.16, y + 0.012, zb + STRD - 0.015), 0.006, 6)
    p.box('carpet_r', -xw + 0.2, xw - 0.2, yL, yL + 0.006, HZI + 0.2, ZM)
    for i in range(1, n2):   # focinhos
        zf = ZF - (i - 1) * STRD; p.box('dkwood', xg + 0.003, xw - 0.003, i * SRR - 0.03, i * SRR + 0.002, zf - 0.025, zf + 0.012)
        zb = ZM + (i - 1) * STRD; p.box('dkwood', -xw + 0.003, -xg - 0.003, yL + i * SRR - 0.03, yL + i * SRR + 0.002, zb - 0.012, zb + 0.025)
    p.box('dkwood', -xw + 0.003, xw - 0.003, yL - 0.03, yL + 0.002, ZM - 0.012, ZM + 0.025)
    # banzos pintados nas paredes
    y1 = lambda z: SRR + (ZF - z) / STRD * SRR; y2 = lambda z: yL + SRR + (z - ZM) / STRD * SRR
    for (x, za, zb, fy) in ((xw - 0.025, ZF - 0.004, ZM + 0.003, y1), (-xw + 0.025, ZM + 0.003, ZF - 0.004, y2)):
        p.hull('trim', [(x + dx + (0.002 if dx * x > 0 else 0.0) * math.copysign(1, x), fy(z) + dy, z) for dx in (-0.025, 0.025) for (z, dy) in ((za, -0.25), (za, 0.08), (zb, -0.25), (zb, 0.08))])   # face de tras 2 mm dentro da parede
    # guarda-corpo entre os lances: banzo, corrimao de mogno, balaustres torneados e pilares
    def baluster(x, y, z, h):
        lathe(p, 'trim', [(0.0, y), (0.022, y), (0.022, y + 0.08), (0.014, y + 0.12), (0.02, y + 0.2), (0.012, y + 0.36), (0.012, y + h - 0.2),
                          (0.02, y + h - 0.14), (0.014, y + h - 0.08), (0.02, y + h - 0.04), (0.02, y + h), (0.0, y + h)], x, z, sec=8)
    def newel(x, y, z, h):
        p.cham('mahog', x - 0.055, x + 0.055, y, y + h, z - 0.055, z + 0.055, 0.008)
        p.cham('mahog', x - 0.065, x + 0.065, y + h, y + h + 0.05, z - 0.065, z + 0.065, 0.01)
        lathe(p, 'mahog', [(0.0, y + h + 0.05), (0.04, y + h + 0.05), (0.05, y + h + 0.1), (0.03, y + h + 0.16), (0.0, y + h + 0.18)], x, z, sec=12)
    for (x, za, zb, fy) in ((xg + 0.03, ZF, ZM, y1), (-xg - 0.03, ZM, ZF, y2)):
        ya, yb = fy(za), fy(zb)
        p.hull('trim', [(x + dx, y, z) for dx in (-0.02, 0.02) for (y, z) in ((ya - 0.12, za), (ya + 0.04, za), (yb - 0.12, zb), (yb + 0.04, zb))])
        seg_cyl(p, 'mahog', (x, ya + 0.92, za), (x, yb + 0.92, zb), 0.03, 10)
        n = int(abs(zb - za) / 0.125)
        for k in range(1, n):
            z = za + (zb - za) * k / n; y = ya + (yb - ya) * k / n; baluster(x, y + 0.03, z, 0.86)
        newel(x, ya - 0.196, za, 1.15); newel(x, yb - 0.196, zb, 1.15)
    seg_cyl(p, 'mahog', (xg + 0.03, yL + 0.92, ZM), (-xg - 0.03, yL + 0.92, ZM), 0.03, 10)
    if kind == '0':   # almofadas fechando o vao embaixo do lance A (entre os lances) e embaixo do patamar
        x0 = xg + 0.008
        p.hull('trim', [(x, y, z) for x in (x0, x0 + 0.02) for (y, z) in ((0.0, ZF - 0.2), (0.0, ZM), (yL - 0.22, ZM), (SRR - 0.2, ZF - 0.2))])
        p.box('trim', -xw, xw, 0.0, yL - 0.2, ZM - 0.02, ZM)
        for (a, b) in ((-xw + 0.12, -0.12), (0.12, xw - 0.12)):
            p.cham('trim', a, b, 0.25, yL - 0.4, ZM - 0.002, ZM + 0.012, 0.004)
        disc_z(p, 'brass', 0.02, ZM - 0.0, ZM + 0.03, -0.3, 0.8, 10)
    r = Piece(); r.merge(p, tr(SXC, 0, 0)); return r
def stair_rail_a():
    """Guarda-corpo do sotao na borda do vao (sobre o lance A), pivo: piso do sotao."""
    p = Piece(); x0, x1 = SXC + 0.06, MX - T; z = ZF + 0.06
    p.box('trim', x0, x1, 0.0, 0.08, z - 0.02, z + 0.02); seg_cyl(p, 'mahog', (x0, 0.92, z), (x1 - 0.005, 0.92, z), 0.03, 10)
    for x in np.arange(x0 + 0.1, x1 - 0.05, 0.125):
        lathe(p, 'trim', [(0.0, 0.08), (0.02, 0.08), (0.014, 0.14), (0.012, 0.75), (0.02, 0.82), (0.02, 0.9), (0.0, 0.9)], x, z, sec=8)
    p.cham('mahog', x0 - 0.055, x0 + 0.055, 0.0, 1.0, z - 0.055, z + 0.055, 0.008)
    lathe(p, 'mahog', [(0.0, 1.0), (0.04, 1.0), (0.05, 1.05), (0.03, 1.11), (0.0, 1.13)], x0, z, sec=12)
    return p
# ============================================================================ moveis da casa vitoriana (pivo: centro de tras, piso; frente +Z, salvo aviso)
def fireplace(w=1.36, h=1.18, big=True):
    """Lareira no peito da parede: moldura de marmore pintado com consolos e prateleira, insercao de ferro fundido com arco,
    azulejos de barro nas laterais, grelha com carvao, lareira de pedra no chao, espelho com moldura dourada, relogio e castiçais."""
    p = P(); x = w / 2
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x - 0.2)))
        p.cham('mantel', a, b, 0.03, h - 0.12, 0.0, 0.07, 0.006); p.cham('mantel', a - 0.01, b + 0.01, 0.03, 0.15, 0.0, 0.085, 0.006)
        c = s * (x - 0.1); p.hull('mantel', [(c + dx, y, z) for dx in (-0.06, 0.06) for (y, z) in ((h - 0.32, 0.07), (h - 0.12, 0.07), (h - 0.12, 0.15), (h - 0.2, 0.15))])
    p.cham('mantel', -x + 0.2, x - 0.2, h - 0.32, h - 0.12, 0.0, 0.07, 0.006)
    prof_x(p, 'mantel', -x - 0.06, x + 0.06, [(0.0, h - 0.12), (0.2, h - 0.12), (0.22, h - 0.1), (0.22, h - 0.06), (0.2, h - 0.04), (0.0, h - 0.04)])
    # insercao de ferro com arco e azulejos laterais
    xi = x - 0.2; yi = h - 0.32
    arch = sbox(-0.28, 0.0, 0.28, 0.55).union(Point(0.0, 0.55).buffer(0.28, 24)).intersection(sbox(-1, 0, 1, yi))
    plate = sbox(-xi, 0.03, xi, yi).difference(arch)
    for g in polys(plate.intersection(sbox(-0.36, 0, 0.36, yi))): prof_z(p, 'iron', 0.002, 0.03, list(g.exterior.coords)[:-1])
    for s in (-1, 1):
        a, b = sorted((s * 0.36, s * xi))
        for k in range(int(yi / 0.15)): p.box('tile_r' if k % 2 == 0 else 'brick_y', a + 0.005, b - 0.005, k * 0.15 + 0.005, (k + 1) * 0.15 - 0.005, 0.002, 0.012)
    p.box('dark', -0.3, 0.3, 0.03, 0.85, -0.25, 0.006)
    for zz in (0.0, 0.08, 0.16): p.box('iron', -0.24, 0.24, 0.12, 0.13, 0.01 + zz * 0.5, 0.02 + zz * 0.5)
    for i in range(7): p.sphere('dark', 0.04, -0.18 + i * 0.06, 0.16, 0.06, 0)
    p.box('stone_c', -x - 0.08, x + 0.08, 0.002, 0.03, 0.004, 0.48)
    # espelho, relogio e castiçais
    if big:
        p.cham('brass', -0.5, 0.5, h + 0.1, h + 1.1, 0.0, 0.04, 0.01); p.box('mirror', -0.44, 0.44, h + 0.16, h + 1.04, 0.04, 0.043)
    lathe(p, 'dkwood', [(0.0, h - 0.04), (0.09, h - 0.04), (0.09, h + 0.18), (0.05, h + 0.24), (0.0, h + 0.25)], 0.0, 0.12, sec=12)
    disc_z(p, 'paper', 0.06, 0.2, 0.215, 0.0, h + 0.12, 16)
    for s in (-1, 1): lathe(p, 'brass', [(0.0, h - 0.04), (0.04, h - 0.04), (0.012, h + 0.03), (0.01, h + 0.2), (0.025, h + 0.22), (0.0, h + 0.23)], s * 0.45, 0.12, sec=8); p.cyl('paper', 0.01, h + 0.23, h + 0.33, s * 0.45, 0.12, 6)
    return p
def chesterfield(L1=1.9, mat='velvet'):
    """Sofa Chesterfield: bracos rolados na altura do encosto, capitone (botoes) e pes torneados."""
    p = P(); x = L1 / 2
    p.cham(mat, -x, x, 0.12, 0.42, 0.0, 0.88, 0.03); p.cham(mat, -x + 0.18, x - 0.18, 0.42, 0.78, 0.0, 0.2, 0.04)
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x - 0.18))); p.cham(mat, a, b, 0.42, 0.7, 0.0, 0.88, 0.03)
        seg_cyl(p, mat, ((a + b) / 2, 0.7, 0.0), ((a + b) / 2, 0.7, 0.88), 0.1, 12)
    seg_cyl(p, mat, (-x + 0.1, 0.78, 0.1), (x - 0.1, 0.78, 0.1), 0.1, 12)
    for i in range(3):
        a = -x + 0.18 + i * (L1 - 0.36) / 3; p.cham(mat, a + 0.005, a + (L1 - 0.36) / 3 - 0.005, 0.42, 0.54, 0.2, 0.86, 0.04)
    for gx in np.linspace(-x + 0.3, x - 0.3, 7):
        for gy in (0.52, 0.66): p.sphere('dark', 0.012, gx, gy, 0.2, 0)
    for (a, c) in ((-x + 0.08, 0.08), (x - 0.08, 0.08), (-x + 0.08, 0.8), (x - 0.08, 0.8)):
        lathe(p, 'mahog', [(0.0, 0.0), (0.03, 0.0), (0.04, 0.05), (0.025, 0.12), (0.0, 0.12)], a, c, sec=10)
    return p
def armchair_v(mat='velvet'):
    """Poltrona de espaldar alto (pivo: centro de tras, piso)."""
    p = P(); p.cham(mat, -0.4, 0.4, 0.14, 0.44, 0.0, 0.8, 0.03); p.cham(mat, -0.36, 0.36, 0.44, 1.12, 0.0, 0.18, 0.05)
    for s in (-1, 1):
        a, b = sorted((s * 0.4, s * 0.28)); p.cham(mat, a, b, 0.44, 0.68, 0.05, 0.8, 0.03); seg_cyl(p, mat, ((a + b) / 2, 0.68, 0.05), ((a + b) / 2, 0.68, 0.8), 0.07, 10)
        p.hull(mat, [(s * 0.36, y, z) for (y, z) in ((0.8, 0.0), (1.12, 0.0), (1.0, 0.25), (0.8, 0.25))] + [(s * 0.46, 0.95, 0.12)])
    p.cham(mat, -0.27, 0.27, 0.44, 0.54, 0.18, 0.78, 0.04)
    for (a, c) in ((-0.34, 0.06), (0.34, 0.06), (-0.34, 0.74), (0.34, 0.74)): lathe(p, 'mahog', [(0.0, 0.0), (0.025, 0.0), (0.035, 0.07), (0.0, 0.14)], a, c, sec=8)
    return p
def side_table(r=0.3, h=0.62, lamp=True):
    p = P(); p.cyl('mahog', r, h - 0.03, h, 0, 0.0, 20)
    lathe(p, 'mahog', [(0.0, 0.0), (0.18, 0.0), (0.06, 0.08), (0.035, 0.2), (0.05, 0.35), (0.03, 0.5), (0.05, h - 0.03), (0.0, h - 0.03)], 0.0, 0.0, sec=12)
    if lamp:
        lathe(p, 'brass', [(0.0, h), (0.08, h), (0.03, h + 0.05), (0.02, h + 0.35), (0.0, h + 0.35)], 0.0, 0.0, sec=10)
        lathe(p, 'cream', [(0.18, h + 0.28), (0.1, h + 0.5), (0.09, h + 0.5), (0.17, h + 0.28)], 0.0, 0.0, sec=16); p.sphere('lamp_glass', 0.045, 0, h + 0.38, 0, 1)
    return p
def piano():
    """Piano de armario com tampa, teclado, castiçais e banqueta (pivo: centro de tras, piso)."""
    p = P(); x = 0.75
    p.cham('mahog', -x, x, 0.0, 1.25, 0.0, 0.6, 0.01); p.cham('mahog', -x - 0.02, x + 0.02, 1.25, 1.29, -0.01, 0.62, 0.008)
    p.cham('mahog', -x, x, 0.72, 0.76, 0.6, 0.85, 0.005)
    for i in range(36):
        a = -0.62 + i * 1.24 / 36; p.box('porcelain', a + 0.002, a + 1.24 / 36 - 0.002, 0.76, 0.785, 0.62, 0.84)
        if i % 7 not in (2, 6): p.box('dark', a + 1.24 / 36 * 0.7, a + 1.24 / 36 * 1.3, 0.785, 0.8, 0.62, 0.74)
    for s in (-1, 1): p.cham('mahog', s * x - 0.05, s * x + 0.05, 0.0, 0.8, 0.6, 0.85, 0.008); p.cyl('mahog', 0.03, 0.0, 0.72, s * (x - 0.05), 0.82, 8)
    p.box('paper', -0.25, 0.25, 0.9, 1.15, 0.58, 0.6)
    p.cham('mahog', -0.4, 0.4, 0.45, 0.5, 1.0, 1.35, 0.01); p.cham('velvet', -0.38, 0.38, 0.5, 0.54, 1.02, 1.33, 0.01)
    for (a, c) in ((-0.36, 1.03), (0.36, 1.03), (-0.36, 1.32), (0.36, 1.32)): p.box('mahog', a - 0.02, a + 0.02, 0.0, 0.45, c - 0.02, c + 0.02)
    return p
def bookcase(L1=1.6, h=2.1):
    """Estante de mogno com cornija, portas de vidro em cima, livros coloridos e armario embaixo."""
    p = P(); x = L1 / 2; d = 0.38
    p.box('mahog', -x, x, 0.0, h, 0.0, 0.02); p.cham('mahog', -x, -x + 0.03, 0.0, h, 0.0, d, 0.004); p.cham('mahog', x - 0.03, x, 0.0, h, 0.0, d, 0.004)
    p.cham('mahog', -x, x, 0.0, 0.8, 0.0, d + 0.04, 0.008); prof_x(p, 'mahog', -x - 0.03, x + 0.03, [(0.0, h), (d + 0.06, h), (d + 0.06, h + 0.05), (d + 0.02, h + 0.1), (0.0, h + 0.1)])
    for (a, b) in ((-x + 0.05, -0.02), (0.02, x - 0.05)): p.cham('mahog', a, b, 0.08, 0.72, d + 0.04, d + 0.06, 0.004)
    rng = np.random.default_rng(13)
    for y in (0.82, 1.24, 1.66):
        p.box('mahog', -x + 0.03, x - 0.03, y - 0.02, y, 0.02, d)
        xx = -x + 0.05
        while xx < x - 0.1:
            w = rng.uniform(0.025, 0.05); hh = rng.uniform(0.26, 0.36); m = ('book', 'book2', 'leaf2', 'cushion', 'velvet')[rng.integers(5)]
            p.box(m, xx, xx + w - 0.003, y, y + hh, 0.06, d - 0.04); xx += w
    for (a, b) in ((-x + 0.03, -0.01), (0.01, x - 0.03)):
        for (u, v) in ((a, a + 0.03), (b - 0.03, b)): p.box('mahog', u, v, 0.8, h - 0.02, d, d + 0.025)
        p.box('mahog', a, b, h - 0.05, h - 0.02, d, d + 0.025); p.box('glass', a + 0.03, b - 0.03, 0.8, h - 0.05, d + 0.008, d + 0.012)
    return p
def sideboard_v(L1=1.7):
    """Aparador de mogno com gavetas, portas almofadadas, espelho de fundo e travessa (sala de jantar)."""
    p = P(); x = L1 / 2; d = 0.5
    p.cham('mahog', -x, x, 0.12, 0.9, 0.0, d, 0.008); p.cham('mahog', -x - 0.02, x + 0.02, 0.9, 0.94, -0.0, d + 0.03, 0.008)
    for s in (-1, 1):
        for c in (0.06, d - 0.06): lathe(p, 'mahog', [(0.0, 0.0), (0.03, 0.0), (0.035, 0.06), (0.0, 0.12)], s * (x - 0.06), c, sec=8)
    for i in range(3):
        a = -x + 0.04 + i * (L1 - 0.08) / 3; b = a + (L1 - 0.08) / 3 - 0.01
        p.cham('mahog', a, b, 0.72, 0.86, d, d + 0.02, 0.004); p.box('brass', (a + b) / 2 - 0.05, (a + b) / 2 + 0.05, 0.78, 0.8, d + 0.02, d + 0.035)
        p.cham('mahog', a, b, 0.16, 0.68, d, d + 0.02, 0.004); p.cham('mahog', a + 0.05, b - 0.05, 0.22, 0.62, d + 0.02, d + 0.03, 0.004)
    p.cham('mahog', -x + 0.1, x - 0.1, 0.94, 1.6, 0.0, 0.04, 0.008); p.box('mirror', -x + 0.16, x - 0.16, 1.0, 1.54, 0.04, 0.043)
    lathe(p, 'porcelain', [(0.0, 0.94), (0.14, 0.94), (0.2, 0.97), (0.0, 0.97)], 0.3, 0.3, sec=18)
    for s in (-1, 1): lathe(p, 'brass', [(0.0, 0.94), (0.05, 0.94), (0.015, 1.0), (0.012, 1.2), (0.03, 1.22), (0.0, 1.23)], s * 0.6, 0.25, sec=8)
    return p
def dining_set_v(n_side=2):
    """Mesa de jantar de mogno (1,6 x 0,9) com pes torneados, 6 cadeiras, toalha de centro, fruteira e lustre de teto (pivo: centro)."""
    p = P(); x, z = 0.8, 0.45
    p.cham('mahog', -x, x, 0.72, 0.76, -z, z, 0.01); p.box('mahog', -x + 0.06, x - 0.06, 0.62, 0.72, -z + 0.06, z - 0.06)
    for (a, c) in ((-x + 0.08, -z + 0.08), (x - 0.08, -z + 0.08), (-x + 0.08, z - 0.08), (x - 0.08, z - 0.08)):
        lathe(p, 'mahog', [(0.0, 0.0), (0.03, 0.0), (0.045, 0.1), (0.03, 0.25), (0.045, 0.45), (0.035, 0.62), (0.0, 0.62)], a, c, sec=10)
    for i in range(n_side):
        xx = -0.4 + i * 0.8
        for (dz, r) in ((-z - 0.25, 0), (z + 0.25, 180)): place(p, dining_chair(), xx, 0.0, dz, r)
    for (dx, r) in ((-x - 0.25, 90), (x + 0.25, -90)): place(p, dining_chair(), dx, 0.0, 0.0, r)
    p.box('paper', -0.5, 0.5, 0.76, 0.763, -0.15, 0.15)
    lathe(p, 'porcelain', [(0.0, 0.763), (0.06, 0.763), (0.04, 0.8), (0.15, 0.86), (0.0, 0.86)], 0.0, 0.0, sec=16)
    for (a, c, m) in ((-0.05, 0.03, 'food_r'), (0.06, -0.02, 'food_y'), (0.0, -0.06, 'food_g')): p.sphere(m, 0.045, a, 0.86, c, 1)
    return p
def kitchener():
    """Fogao a lenha de ferro fundido (pivo: centro de tras, piso): forno duplo, chapa com argolas, porta da fornalha, varao
    de latao, prateleira e coifa de tijolo."""
    p = P(); x = 0.55
    p.cham('iron', -x, x, 0.0, 0.85, 0.0, 0.58, 0.01); p.box('iron', -x - 0.02, x + 0.02, 0.85, 0.88, -0.0, 0.62)
    for (cx, r) in ((-0.25, 0.1), (0.05, 0.12)): ring_y(p, 'steel_d', r - 0.02, r, 0.88, 0.89, cx, 0.32, 20); ring_y(p, 'steel_d', r * 0.4 - 0.015, r * 0.4, 0.88, 0.89, cx, 0.32, 14)
    for (a, b) in ((-x + 0.04, -0.16), (0.24, x - 0.04)):
        p.cham('iron', a, b, 0.12, 0.72, 0.58, 0.61, 0.006); disc_z(p, 'brass', 0.025, 0.61, 0.63, b - 0.05, 0.45, 10)
        for k in range(3): p.box('steel_d', a + 0.04, b - 0.04, 0.2 + k * 0.18, 0.21 + k * 0.18, 0.61, 0.615)
    p.cham('iron', -0.13, 0.21, 0.32, 0.62, 0.58, 0.61, 0.006)
    for k in range(5): p.box('dark', -0.1 + k * 0.06, -0.08 + k * 0.06, 0.38, 0.56, 0.61, 0.615)
    seg_cyl(p, 'brass', (-x, 0.78, 0.66), (x, 0.78, 0.66), 0.012, 8)
    for s in (-1, 1): seg_cyl(p, 'brass', (s * x, 0.78, 0.58), (s * x, 0.78, 0.66), 0.01, 6)
    p.box('iron', -x, x, 1.3, 1.33, 0.0, 0.24)
    for (a, m) in ((-0.35, 'chrome'), (-0.1, 'brass'), (0.2, 'chrome')): lathe(p, m, [(0.0, 1.33), (0.07, 1.33), (0.08, 1.45), (0.0, 1.45)], a, 0.12, sec=12)
    p.box('dark', -x - 0.03, x + 0.03, 0.88, 2.0, 0.001, 0.02)
    return p
def belfast_sink(L1=1.8):
    """Bancada de madeira com cuba de louca funda (Belfast), torneiras de latao de parede, armario com cortina e escorredor."""
    p = P(); x = L1 / 2; d = 0.6; xs = -0.25
    p.box('wood', -x, xs - 0.32, 0.86, 0.9, 0.0, d); p.box('wood', xs + 0.32, x, 0.86, 0.9, 0.0, d)
    for s in (-1, 1): p.box('wood', s * x - 0.03 * s - 0.03, s * x - 0.03 * s + 0.03, 0.0, 0.86, 0.04, d - 0.04)
    p.box('cab', -x + 0.06, x - 0.06, 0.08, 0.1, 0.04, d - 0.04)
    xs = -0.25; p.cham('porcelain', xs - 0.32, xs + 0.32, 0.62, 0.9, 0.04, d - 0.02, 0.02); p.box('chrome', xs - 0.26, xs + 0.26, 0.85, 0.902, 0.1, d - 0.08)
    for (a, m) in ((-x + 0.06, 'curtain'), (xs + 0.34, 'curtain')):
        b = xs - 0.34 if a < xs else x - 0.06
        for k in range(int((b - a) / 0.08)):
            u = a + k * 0.08; p.box(m, u, u + 0.08, 0.1, 0.84, d - 0.05 + (0.012 if k % 2 else 0.0), d - 0.04 + (0.012 if k % 2 else 0.0))
    for s in (-1, 1):
        seg_cyl(p, 'brass', (xs + s * 0.1, 1.15, 0.004), (xs + s * 0.1, 1.15, 0.16), 0.014, 8); seg_cyl(p, 'brass', (xs + s * 0.1, 1.15, 0.16), (xs + s * 0.1, 1.06, 0.18), 0.012, 8)
        lathe(p, 'porcelain', [(0.0, 1.17), (0.02, 1.17), (0.03, 1.2), (0.0, 1.21)], xs + s * 0.1, 0.06, sec=8)
    p.box('tile_w', -x, x, 0.9, 1.4, 0.0, 0.008)
    for y in np.arange(0.975, 1.4, 0.075): p.box('ctop', -x, x, y - 0.0015, y, 0.008, 0.0088)
    for i in range(5): p.box('wood', 0.25 + i * 0.07, 0.26 + i * 0.07, 0.9, 1.1, 0.2, 0.5)
    for i in range(3): disc_x(p, 'porcelain', 0.11, 0.28 + i * 0.12, 0.29 + i * 0.12, 1.02, 0.35, 16)
    return p
def welsh_dresser(L1=1.4):
    """Guarda-louca de madeira (armario embaixo, prateleiras abertas com pratos e canecas em cima)."""
    p = P(); x = L1 / 2; d = 0.5
    p.cham('wood', -x, x, 0.0, 0.88, 0.0, d, 0.008); p.cham('wood', -x - 0.02, x + 0.02, 0.88, 0.92, -0.0, d + 0.02, 0.008)
    for (a, b) in ((-x + 0.04, -0.01), (0.01, x - 0.04)):
        p.cham('wood', a, b, 0.62, 0.84, d, d + 0.02, 0.004); p.cham('wood', a, b, 0.08, 0.58, d, d + 0.02, 0.004); p.cyl('brass', 0.015, 0.72, 0.75, b - 0.06, d + 0.03, 8)
    p.box('wood', -x, x, 0.92, 2.05, 0.0, 0.02); p.cham('wood', -x, -x + 0.03, 0.92, 2.05, 0.0, 0.3, 0.004); p.cham('wood', x - 0.03, x, 0.92, 2.05, 0.0, 0.3, 0.004)
    prof_x(p, 'wood', -x - 0.03, x + 0.03, [(0.0, 2.05), (0.34, 2.05), (0.34, 2.1), (0.3, 2.14), (0.0, 2.14)])
    for y in (1.3, 1.68):
        p.box('wood', -x + 0.03, x - 0.03, y - 0.02, y, 0.02, 0.28); p.box('wood', -x + 0.03, x - 0.03, y + 0.04, y + 0.06, 0.24, 0.26)
        for i in range(6):
            xx = -x + 0.15 + i * (L1 - 0.3) / 5; disc_z(p, 'porcelain' if i % 2 else 'blue', 0.065, 0.04 + 0.006 * (i % 2), 0.05 + 0.006 * (i % 2), xx, y + 0.09, 18)
    for i in range(6): xx = -x + 0.12 + i * (L1 - 0.24) / 5; lathe(p, 'porcelain' if i % 2 else 'blue', [(0.0, 1.0), (0.04, 1.0), (0.045, 1.1), (0.0, 1.1)], xx, 0.14, sec=10)
    return p
def pedestal_sink():
    """Pia de coluna de louca com torneiras de latao, espelho com prateleira e saboneteira (pivo: parede, piso)."""
    p = P(); lathe(p, 'porcelain', [(0.0, 0.0), (0.12, 0.0), (0.08, 0.06), (0.07, 0.7), (0.0, 0.7)], 0.0, 0.25, sec=14)
    p.cham('porcelain', -0.3, 0.3, 0.7, 0.85, 0.0, 0.46, 0.03); p.cham('porcelain', -0.24, 0.24, 0.84, 0.851, 0.06, 0.4, 0.02)
    for s in (-1, 1): seg_cyl(p, 'brass', (s * 0.14, 0.85, 0.06), (s * 0.14, 0.95, 0.06), 0.012, 6); seg_cyl(p, 'brass', (s * 0.14, 0.95, 0.06), (s * 0.14, 0.93, 0.14), 0.01, 6); p.cyl('porcelain', 0.025, 0.95, 0.98, s * 0.14, 0.06, 8)
    p.cham('mahog', -0.28, 0.28, 1.15, 1.85, 0.0, 0.03, 0.006); p.box('mirror', -0.24, 0.24, 1.19, 1.81, 0.03, 0.033)
    p.cham('mahog', -0.3, 0.3, 1.1, 1.13, 0.0, 0.12, 0.004); lathe(p, 'blue', [(0.0, 1.13), (0.03, 1.13), (0.03, 1.25), (0.0, 1.26)], 0.18, 0.06, sec=8)
    return p
def high_wc():
    """Vaso com caixa de descarga alta de ferro, cano, corrente com puxador e assento de madeira (pivo: parede, piso)."""
    p = wc(); p.box('dark', -0.19, 0.19, 0.42, 0.45, 0.2, 0.62)
    p.cham('iron', -0.24, 0.24, 1.95, 2.2, 0.0, 0.2, 0.01); seg_cyl(p, 'chrome', (0.0, 1.95, 0.08), (0.0, 0.8, 0.08), 0.02, 8)
    p.box('iron', -0.06, 0.06, 1.9, 1.95, 0.0, 0.15); seg_cyl(p, 'chrome', (0.18, 1.95, 0.16), (0.18, 1.4, 0.16), 0.003, 4); lathe(p, 'porcelain', [(0.0, 1.32), (0.015, 1.34), (0.015, 1.4), (0.0, 1.4)], 0.18, 0.16, sec=8)
    return p
def hall_stand():
    """Cabideiro de hall de mogno com espelho, ganchos, gaveta e porta-guarda-chuvas (pivo: parede, piso)."""
    p = P(); x = 0.45
    for s in (-1, 1): p.cham('mahog', s * x - 0.03, s * x + 0.03, 0.0, 2.0, 0.0, 0.32, 0.006)
    p.cham('mahog', -x, x, 0.7, 0.75, 0.0, 0.32, 0.006); p.cham('mahog', -x + 0.03, x - 0.03, 0.62, 0.7, 0.2, 0.32, 0.004)
    p.cham('mahog', -x, x, 0.9, 2.0, 0.0, 0.03, 0.006); p.box('mirror', -0.24, 0.24, 1.2, 1.7, 0.03, 0.033)
    prof_x(p, 'mahog', -x - 0.03, x + 0.03, [(0.0, 2.0), (0.06, 2.0), (0.08, 2.06), (0.0, 2.1)])
    for (a, y) in ((-0.36, 1.5), (-0.32, 1.85), (0.32, 1.85), (0.36, 1.5)): seg_cyl(p, 'brass', (a, y, 0.03), (a, y + 0.04, 0.14), 0.01, 6); p.sphere('brass', 0.018, a, y + 0.05, 0.15, 0)
    p.box('mahog', -x, x, 0.1, 0.13, 0.05, 0.3); seg_cyl(p, 'dark', (-0.35, 0.13, 0.2), (-0.38, 0.95, 0.18), 0.02, 6)
    p.box('bed_b', 0.3, 0.42, 1.45, 1.55, 0.04, 0.1); p.hull('dark', [(0.25, 1.05, 0.12), (0.4, 1.05, 0.12), (0.28, 1.4, 0.06), (0.37, 1.4, 0.06)])
    return p
def console_v(L1=1.0):
    p = P(); x = L1 / 2; p.cham('mahog', -x, x, 0.78, 0.82, 0.0, 0.36, 0.008); p.box('mahog', -x + 0.04, x - 0.04, 0.68, 0.78, 0.02, 0.34)
    for s in (-1, 1):
        for c in (0.04, 0.32): lathe(p, 'mahog', [(0.0, 0.0), (0.02, 0.0), (0.03, 0.2), (0.02, 0.4), (0.025, 0.68), (0.0, 0.68)], s * (x - 0.04), c, sec=8)
    lathe(p, 'porcelain', [(0.0, 0.82), (0.07, 0.82), (0.09, 0.95), (0.05, 1.1), (0.06, 1.15), (0.0, 1.15)], -0.25, 0.18, sec=12)
    p.box('paper', 0.05, 0.3, 0.82, 0.83, 0.08, 0.28)
    return p
def runner(x0, x1, z0, z1):
    p = P(); p.box('carpet_r', x0, x1, 0.0, 0.007, z0, z1); p.box('cushion', x0 + 0.05, x1 - 0.05, 0.007, 0.008, z0 + 0.05, z0 + 0.1); p.box('cushion', x0 + 0.05, x1 - 0.05, 0.007, 0.008, z1 - 0.1, z1 - 0.05); return p
def brass_bed(w=1.4, L1=2.0):
    """Cama de ferro e latao com cabeceira e pezeira de barras, colcha de retalhos e travesseiros (pivo: centro da cabeceira)."""
    p = P(); x = w / 2
    for (z, h) in ((0.0, 1.25), (L1, 0.85)):
        for s in (-1, 1): seg_cyl(p, 'iron', (s * x, 0.0, z), (s * x, h, z), 0.022, 8); p.sphere('brass', 0.035, s * x, h + 0.02, z, 1)
        seg_cyl(p, 'brass', (-x, h - 0.05, z), (x, h - 0.05, z), 0.016, 8); seg_cyl(p, 'iron', (-x, 0.4, z), (x, 0.4, z), 0.014, 6)
        for xx in np.linspace(-x + 0.12, x - 0.12, 7): seg_cyl(p, 'iron', (xx, 0.4, z), (xx, h - 0.05, z), 0.008, 6)
    for s in (-1, 1): p.box('iron', s * x - 0.02, s * x + 0.02, 0.3, 0.36, 0.0, L1)
    p.cham('bed_w', -x + 0.02, x - 0.02, 0.36, 0.56, 0.02, L1 - 0.02, 0.04)
    for i in range(6):
        for j in range(8):
            m = ('velvet', 'cushion', 'bed_b', 'leaf2', 'cream', 'blue')[(i + j * 2) % 6]
            a = -x - 0.03 + i * (w + 0.06) / 6; c = 0.45 + j * (L1 - 0.45) / 8
            p.box(m, a + 0.002, a + (w + 0.06) / 6 - 0.002, 0.56, 0.585, c + 0.002, c + (L1 - 0.45) / 8 - 0.002)
    for s in (-1, 1): p.cham('bed_w', s * 0.32 - 0.26, s * 0.32 + 0.26, 0.56, 0.7, 0.06, 0.42, 0.05)
    return p
def trunk():
    p = P(); p.cham('dkwood', -0.45, 0.45, 0.0, 0.42, 0.0, 0.5, 0.01); p.hull('dkwood', [(x, y, z) for x in (-0.45, 0.45) for (y, z) in ((0.42, 0.0), (0.42, 0.5), (0.5, 0.06), (0.5, 0.44))])
    for x in (-0.3, 0.3): p.box('brass', x - 0.025, x + 0.025, 0.002, 0.506, -0.004, 0.504)
    p.box('brass', -0.04, 0.04, 0.3, 0.4, 0.5, 0.51); return p
def boxes(n=3, seed=2):
    p = P(); rng = np.random.default_rng(seed); y = 0.0
    for k in range(n):
        w = rng.uniform(0.35, 0.55); h = rng.uniform(0.25, 0.4); p.cham('basket', -w / 2, w / 2, y, y + h, 0.0, rng.uniform(0.35, 0.5), 0.006); y += h
    return p
def towel_rad():
    """Toalheiro aquecido de tubos (pivo: parede, piso)."""
    p = P()
    for s in (-1, 1): seg_cyl(p, 'chrome', (s * 0.25, 0.15, 0.06), (s * 0.25, 1.0, 0.06), 0.016, 8); seg_cyl(p, 'chrome', (s * 0.25, 0.3, 0.0), (s * 0.25, 0.3, 0.06), 0.01, 6)
    for y in (0.3, 0.55, 0.8, 0.95): seg_cyl(p, 'chrome', (-0.25, y, 0.06), (0.25, y, 0.06), 0.012, 6)
    p.box('bed_w', -0.2, 0.2, 0.42, 0.81, 0.07, 0.085); return p
def curtains(L1, h=2.5, mat='velvet'):
    """Varao de latao com cortinas de veludo abertas nos 2 lados (pivo: centro, piso, face da parede; +Z)."""
    p = P(); x = L1 / 2; seg_cyl(p, 'brass', (-x - 0.1, h, 0.1), (x + 0.1, h, 0.1), 0.014, 8)
    for s in (-1, 1): p.sphere('brass', 0.03, s * (x + 0.12), h, 0.1, 1); seg_cyl(p, 'brass', (s * x, h, 0.0), (s * x, h, 0.1), 0.01, 6)
    for s in (-1, 1):
        for k in range(5):
            u = s * (x - 0.02 - k * 0.07); p.box(mat, u - 0.04, u + 0.04, 0.02, h - 0.04, 0.08 + (0.02 if k % 2 else 0.0), 0.1 + (0.02 if k % 2 else 0.0))
    return p

# ---------------------------------------------------------------------------- mobilia por pavimento (casa da direita, pivo: piso)
XF = 0.55                                                          # face dos peitos de lareira
def furn(kind):
    p = P()
    if kind == '0':
        # sala de visitas (com a bay): lareira, Chesterfield, 2 poltronas, mesinha, piano, estante, mesa redonda na bay, cortinas
        place(p, fireplace(), XF, 0.0, 2.0, 90)
        place(p, rug(-1.3, 1.3, -0.9, 0.9), 1.85, 0.0, 2.0, 90)
        place(p, chesterfield(1.9), 3.15, 0.0, 1.7, -90)
        place(p, armchair_v(), 1.15, 0.0, 0.95, 20); place(p, armchair_v('fabric_g'), 1.15, 0.0, 3.1, 160)
        p.cham('mahog', 1.75, 2.35, 0.4, 0.44, 1.55, 2.25, 0.008)
        for (a, c) in ((1.8, 1.6), (2.3, 1.6), (1.8, 2.2), (2.3, 2.2)): lathe(p, 'mahog', [(0.0, 0.0), (0.02, 0.0), (0.03, 0.2), (0.0, 0.4)], a, c, sec=8)
        place(p, bookcase(1.6), 2.6, 0.0, 0.08, 0)
        place(p, side_table(0.36, 0.7, False), BAYC, 0.0, MZ + 0.25); place(p, plant(0.9), BAYC, 0.7, MZ + 0.25)
        place(p, side_table(0.22, 0.6, True), 0.55, 0.0, 0.5)
        place(p, curtains(2 * OPH - 0.3, 2.6), BAYC, 0.0, MZ - T, 180)
        place(p, wall_art(0.7, 0.9, 21), XH - TP / 2, 1.6, 1.2, -90)
        # sala de jantar: lareira, mesa com 6 cadeiras, aparador, quadro, cortina
        place(p, fireplace(1.3, 1.15), XF, 0.0, -1.9, 90)
        place(p, rug(-1.4, 1.4, -1.0, 1.0), 2.2, 0.0, -2.15, 0)
        place(p, dining_set_v(2), 2.2, 0.0, -2.15, 0)
        place(p, sideboard_v(1.6), XH - TP / 2, 0.0, -3.1, -90)
        place(p, wall_art(1.0, 0.7, 22), 2.2, 1.65, -TP / 2, 180)
        place(p, curtains(0.7, 2.5), 3.33, 0.0, -MZ + T, 0)
        # hall: cabideiro, aparador, passadeira
        place(p, hall_stand(), MX - T, 0.0, 0.7, -90); place(p, console_v(0.9), XH + TP / 2, 0.0, 1.6, 90)
        place(p, runner(4.45, 5.6, -0.9, 3.6), 0.0, 0.0, 0.0)
        place(p, wall_art(0.5, 0.7, 23), XH + TP / 2, 1.55, 0.4, 90)
        # cozinha: fogao de ferro no peito, pia Belfast embaixo da janela, guarda-louca, mesinha
        place(p, kitchener(), 0.6, 0.0, -6.22, 90)
        place(p, belfast_sink(1.4), OXR - T, 0.0, -6.1, -90)
        place(p, welsh_dresser(1.0), PW, 0.0, -5.05, 90)
        place(p, fridge_home(), OXR - T, 0.0, -5.0, -90)
        # area de servico: tanque, lavadora, vaso de descarga alta, prateleira
        place(p, high_wc(), PW, 0.0, -7.75, 90)
        place(p, washer_dryer(), 1.95, 0.0, OZ1 + T, 0)
        p.box('wood', 1.6, 2.5, 1.95, 1.98, OZ1 + T, OZ1 + T + 0.3)
        for i in range(4): p.cyl(('blue', 'paint_w', 'food_y', 'leaf2')[i], 0.05, 1.98, 2.2, 1.75 + i * 0.2, OZ1 + T + 0.15, 10)
    if kind == '1':
        # quarto da frente (bay): cama de latao, criados, guarda-roupa, penteadeira na bay, lareira pequena
        place(p, fireplace(1.2, 1.1, False), XF, 0.0, 2.0, 90)
        place(p, brass_bed(1.4, 2.0), 2.45, 0.0, 0.1, 0)
        for x in (1.45, 3.45): place(p, nightstand(), x, 0.0, 0.06, 0)
        place(p, wardrobe2(1.1), XH - TP / 2, 0.0, 3.3, -90)
        place(p, rug(-0.9, 0.9, -0.6, 0.6), 2.45, 0.0, 2.6, 0)
        place(p, curtains(2 * OPH - 0.3, 2.5, 'curtain'), BAYC, 0.0, MZ - T, 180)
        place(p, armchair_v('fabric_g'), BAYC, 0.0, MZ + 0.15, 180)
        # quarto dos fundos: cama de solteiro, escrivaninha na janela, guarda-roupa, lareira
        place(p, fireplace(1.1, 1.05, False), XF, 0.0, -1.9, 90)
        place(p, bed(1.0, 1.95, 'bed_g'), 2.3, 0.0, -TP / 2, 180)
        place(p, desk(), 2.9, 0.0, -MZ + T, 0); place(p, dining_chair(), 2.9, 0.0, -3.55, 180)
        place(p, wardrobe2(1.0), PW, 0.0, -3.6, 90)
        place(p, curtains(0.9, 2.45, 'curtain'), 2.9, 0.0, -MZ + T, 0)
        # banheiro: banheira de pes, pia de coluna, vaso de descarga alta, toalheiro
        place(p, clawfoot_tub(), MX - T, 0.0, 2.0, -90)
        place(p, pedestal_sink(), XH + TP / 2, 0.0, 3.35, 90)
        place(p, high_wc(), XH + TP / 2, 0.0, 2.35, 90)
        place(p, towel_rad(), 4.8, 0.0, MZ - T, 180)
        # patamar: aparador com planta
        place(p, plant(1.0), 5.7, 0.0, 1.25)
    if kind == 'a':
        # quarto do sotao: cama no meio (embaixo da cumeeira), bau, estante baixa, poltrona e mesa na janela da empena, caixas
        place(p, bed(1.4, 2.0, 'bed_b'), 0.62, 0.0, 1.55, 90)
        place(p, trunk(), 2.9, 0.0, 1.55, -90)
        place(p, desk(), BAYC, 0.0, MZ - T, 180); place(p, dining_chair(), BAYC, 0.0, 3.55, 0)
        place(p, armchair_v('fabric_t'), 3.3, 0.0, -1.2, 200)
        place(p, rug(-1.0, 1.0, -0.7, 0.7), 2.1, 0.0, 0.05, 0)
        place(p, bookcase(1.2, 1.1), 2.0, 0.0, -2.4, 0)
        for (x, z, s) in ((0.9, -3.4, 2), (1.6, -3.5, 5), (3.2, -3.4, 7)): place(p, boxes(3, s), x, 0.0, z, 0)
    return p
# ============================================================================ portas, jardim, rua e objetos externos
def door4(w, h, t, mat, front=False):
    """Folha de 4 almofadas (2 altas em cima, 2 baixas embaixo) com rebaixo nas 2 faces (pivo: dobradica, embaixo)."""
    p = P(); slab = tbox(0, w, 0, h, -t / 2, t / 2); cut = []
    rows = [(0.16, 0.86), (1.0, h - 0.14)]
    for (y0, y1) in rows:
        for (a, b) in ((0.12, w / 2 - 0.045), (w / 2 + 0.045, w - 0.12)):
            for z in (t / 2, -t / 2): cut.append(tbox(a, b, y0, y1, z - 0.009, z + 0.009))
    p.add(mat, bl_detail(slab, cut, bevel=0.004, segments=2))
    for (y0, y1) in rows:   # bolecos das almofadas
        for (a, b) in ((0.12, w / 2 - 0.045), (w / 2 + 0.045, w - 0.12)):
            for z in (1, -1):
                zz = z * (t / 2 - 0.009)
                for (u0, u1, v0, v1) in ((a, b, y0, y0 + 0.015), (a, b, y1 - 0.015, y1), (a, a + 0.015, y0, y1), (b - 0.015, b, y0, y1)):
                    p.box(mat, u0, u1, v0, v1, *sorted((zz, zz + z * 0.006)))
    for z in (1, -1):
        zz = z * t / 2
        p.cham('brass', w - 0.11, w - 0.06, 0.9, 1.1, *sorted((zz, zz + z * 0.008)), 0.003); lathe_z(p, 'brass', w - 0.085, 1.0, zz, z, 0.028)
    if front:   # aldrava, abertura de cartas e olho magico na face de fora (+z)
        zz = t / 2; p.cham('brass', w / 2 - 0.15, w / 2 + 0.15, 0.92, 0.98, zz, zz + 0.012, 0.003); p.box('dark', w / 2 - 0.12, w / 2 + 0.12, 0.94, 0.96, zz + 0.012, zz + 0.013)
        p.cham('brass', w / 2 - 0.05, w / 2 + 0.05, 1.45, 1.55, zz, zz + 0.015, 0.004)
        seg_cyl(p, 'brass', (w / 2, 1.43, zz + 0.03), (w / 2, 1.3, zz + 0.04), 0.012, 8); ring_y(p, 'brass', 0.04, 0.052, 1.27, 1.29, w / 2, zz + 0.04, 14)
    for yy in (0.25, h / 2, h - 0.25): p.cyl('brass', 0.008, yy - 0.06, yy + 0.06, -0.004, t / 2 + 0.002, 8)
    return p
def lathe_z(p, mat, x, y, z0, s, r):
    """Macaneta redonda saindo da face (sentido s)."""
    m = trimesh.creation.cylinder(radius=r * 0.4, height=0.05, sections=10); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([x, y, z0 + s * 0.025]); p.add(mat, m)
    p.sphere(mat, r, x, y, z0 + s * 0.06, 1)
def door_front(): return door4(FDOOR[1] - FDOOR[0] - 0.14, 2.19, 0.05, 'door_g', True)
def door_int(): return door4(ID - 0.02, DH - 0.012, 0.04, 'door_int')
def door_back():
    """Porta dos fundos de tabuas com travessas e meia-luz de vidro de 4 folhas (pivo: dobradica)."""
    w, h, t = BDOOR[1] - BDOOR[0] - 0.14, 2.03, 0.045; p = P()
    for k in range(int(w / 0.11)): p.cham('paint_c', k * w / int(w / 0.11) + 0.002, (k + 1) * w / int(w / 0.11) - 0.002, 0.0, 1.15, -t / 2, t / 2, 0.004)
    for (u, v) in ((0.0, 0.07), (w - 0.07, w)): p.box('paint_c', u, v, 1.15, h, -t / 2, t / 2)
    p.box('paint_c', 0.07, w - 0.07, h - 0.08, h, -t / 2, t / 2); p.box('paint_c', 0.07, w - 0.07, 1.15, 1.2, -t / 2, t / 2)
    p.box('glass', 0.07, w - 0.07, 1.2, h - 0.08, -0.003, 0.003)
    p.box('paint_c', w / 2 - 0.015, w / 2 + 0.015, 1.2, h - 0.08, -0.015, 0.015); p.box('paint_c', 0.07, w - 0.07, (1.2 + h - 0.08) / 2 - 0.015, (1.2 + h - 0.08) / 2 + 0.015, -0.015, 0.015)
    for y in (0.2, 0.9): p.box('paint_c', 0.03, w - 0.03, y, y + 0.12, -t / 2 - 0.022, -t / 2)
    p.hull('paint_c', [(x, y, z) for (x, y) in ((0.05, 0.32), (0.13, 0.32), (w - 0.13, 0.9), (w - 0.05, 0.9)) for z in (-t / 2 - 0.022, -t / 2)])
    for z in (1, -1): lathe_z(p, 'iron', w - 0.08, 1.0, z * t / 2, z, 0.026)
    return p
def gate_iron(w=1.14, h=0.95):
    """Portao de ferro batido do jardim: barras com pontas de lanca, travessas, volutas e trinco (pivo: dobradica, chao)."""
    p = P()
    for x in (0.02, w - 0.02): p.box('iron', x - 0.02, x + 0.02, 0.05, h, -0.02, 0.02)
    for y in (0.12, h - 0.15, h - 0.05): p.box('iron', 0.02, w - 0.02, y - 0.015, y + 0.015, -0.012, 0.012)
    for x in np.arange(0.11, w - 0.06, 0.1):
        seg_cyl(p, 'iron', (x, 0.12, 0), (x, h + 0.08, 0), 0.009, 6); p.hull('iron', [(x + dx, h + 0.08, dz) for (dx, dz) in ((-0.022, 0), (0.022, 0), (0, -0.012), (0, 0.012))] + [(x, h + 0.16, 0)])
    for k in range(3):
        cx = w * (k + 1) / 4
        for a in np.linspace(0, 2 * math.pi, 10, endpoint=False): p.box('iron', cx + 0.08 * math.cos(a) - 0.008, cx + 0.08 * math.cos(a) + 0.008, h - 0.36 + 0.08 * math.sin(a) - 0.008, h - 0.36 + 0.08 * math.sin(a) + 0.008, -0.008, 0.008)
    p.box('iron', w - 0.09, w - 0.02, 0.6, 0.64, 0.012, 0.03)
    return p
def gate_wood(w=0.95, h=1.8):
    """Portao lateral de tabuas com travessas e trinco (pivo: dobradica, chao)."""
    p = P()
    for k in range(int(w / 0.12)): p.cham('wood', k * w / int(w / 0.12) + 0.002, (k + 1) * w / int(w / 0.12) - 0.002, 0.05, h, -0.012, 0.012, 0.003)
    for y in (0.3, h - 0.3): p.box('wood', 0.03, w - 0.03, y, y + 0.1, 0.012, 0.035)
    p.hull('wood', [(x, y, z) for (x, y) in ((0.05, 0.4), (0.14, 0.4), (w - 0.14, h - 0.4), (w - 0.05, h - 0.4)) for z in (0.012, 0.035)])
    p.box('iron', w - 0.12, w - 0.03, 1.0, 1.03, 0.035, 0.05); return p

# ---------------------------------------------------------------------------- terreno (lote do par de casas e rua)
ZW = 8.6                                                           # muro da frente (face da calcada)
WALK = (ZW, 11.0); CURB = (11.0, 11.15); ROAD = (11.15, 18.15); WALK2 = (18.15, 20.0)
PX = 8.4                                                           # divisa lateral do lote (de cada casa)
ZBK = -16.0                                                        # cerca dos fundos
PATH = (FDOOR[0] - 0.15, FDOOR[1] + 0.15)                          # caminho xadrez (x)
GATE_S = (6.5, 7.45)                                               # portao lateral (x), na linha z = 3,0
def checker_sq(p, poly, y0, y1, s=0.2, ma='tile_b', mb='tile_w2'):
    b = poly.bounds
    for i in range(int(math.floor(b[0] / s)), int(math.ceil(b[2] / s))):
        for j in range(int(math.floor(b[1] / s)), int(math.ceil(b[3] / s))):
            q = sbox(i * s + 0.002, j * s + 0.002, (i + 1) * s - 0.002, (j + 1) * s - 0.002).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
    ext_y(p, 'grille', poly.buffer(-0.001, join_style=2), y0, y1 - 0.003)
def low_wall(p, x0, x1, z, h=0.6, along='x'):
    """Mureta de tijolo com capa de pedra chanfrada (eixo x ou z)."""
    t = 0.23
    if along == 'x':
        p.box('brick', x0, x1, -0.3, h, z - t / 2, z + t / 2)
        prof_x(p, 'stone_c', x0, x1, [(z - t / 2 - 0.04, h), (z + t / 2 + 0.04, h), (z + t / 2 + 0.04, h + 0.04), (z, h + 0.1), (z - t / 2 - 0.04, h + 0.04)])
    else:
        p.box('brick', z - t / 2, z + t / 2, -0.3, h, x0, x1)
        prof_z(p, 'stone_c', x0, x1, [(z - t / 2 - 0.04, h), (z + t / 2 + 0.04, h), (z + t / 2 + 0.04, h + 0.04), (z, h + 0.1), (z - t / 2 - 0.04, h + 0.04)])
def pier(p, x, z, h=0.95, s=0.38):
    p.box('brick', x - s / 2, x + s / 2, -0.29, h, z - s / 2, z + s / 2)
    p.cham('stone_c', x - s / 2 - 0.05, x + s / 2 + 0.05, h, h + 0.08, z - s / 2 - 0.05, z + s / 2 + 0.05, 0.01)
    p.hull('stone_c', [(x + dx, h + 0.08, z + dz) for dx in (-s / 2, s / 2) for dz in (-s / 2, s / 2)] + [(x, h + 0.3, z)])
def site():
    """Lote da casa da direita (pivo: chao; o da esquerda e o espelho): jardim da frente com gramado, canteiro na bay, caminho
    de ladrilho xadrez com meio-fio de corda, mureta com capa de pedra e pilares com pinaculo; corredor lateral e patio de
    lajotas; quintal com gramado, caminho de cascalho e base do galpao."""
    p = Piece()
    front = sbox(0.0, MZ, PX, ZW - 0.23).difference(BAY_POLY)
    path = sbox(PATH[0], MZ + 0.95, PATH[1], ZW - 0.23)
    bed = BAY_POLY.buffer(0.6, join_style=2).intersection(front).difference(BAY_POLY).difference(sbox(0, MZ - 1, 0.12, ZW)).difference(sbox(-BIG, MZ - 1, BIG, MZ + 0.003))
    side = sbox(MX, -MZ, PX, MZ)
    lawn = front.difference(path.buffer(0.06, join_style=2)).difference(bed).difference(sbox(MX - 0.05, MZ, PX, ZW)).difference(sbox(FDOOR[0] - 0.45, MZ, FDOOR[1] + 0.45, MZ + 0.95))
    lawn = lawn.difference(sbox(0.0, MZ + BAY_P + 0.6, 0.115, ZW))
    ext_y(p, 'lawn', lawn, -0.3, 0.0); ext_y(p, 'mulch', bed, -0.3, -0.02)
    checker_sq(p, path, -0.012, 0.012); ext_y(p, 'conc_s', path, -0.3, -0.012)
    for s in (-1, 1):   # meio-fio de corda (ladrilhos com topo arredondado)
        x = PATH[0] - 0.03 if s < 0 else PATH[1] + 0.03
        for z in np.arange(MZ + 0.97, ZW - 0.31, 0.08): p.box('tile_r', x - 0.025, x + 0.025, -0.05, 0.05, z, z + 0.075); p.sphere('tile_r', 0.03, x, 0.05, z + 0.037, 0)
    # degrau: base da escada (piso de pedra no pe)
    ext_y(p, 'stone_c', sbox(FDOOR[0] - 0.45, MZ, FDOOR[1] + 0.45, MZ + 0.95).difference(sbox(FDOOR[0] - 0.2, MZ, FDOOR[1] + 0.2, MZ + 0.9)), -0.3, 0.0)
    tiles(p, side.difference(CHIM_S), -0.3, 0.0, 0.6, 'stone_c', 0.006, 'conc_s')
    tiles(p, sbox(MX - 0.05, MZ, PX, ZW - 0.23), -0.3, 0.0, 0.6, 'stone_c', 0.006, 'conc_s')
    ext_y(p, 'stone_c', sbox(PATH[0] - 0.01, ZW - 0.23, PATH[1] + 0.01, ZW), -0.3, 0.012)
    # fundos: patio de lajotas (corredor lateral do anexo), quintal com gramado, caminho de cascalho
    yard = sbox(OXR, OZ1, PX, -MZ).union(sbox(0.0, OZ1 - 1.6, PX, OZ1))
    tiles(p, yard, -0.3, 0.0, 0.6, 'stone_c', 0.006, 'conc_s')
    back = sbox(0.0, ZBK, PX, OZ1 - 1.6)
    gp = sbox(5.6, ZBK + 2.6, 6.4, OZ1 - 1.6)
    ext_y(p, 'gravel', gp, -0.3, 0.0); ext_y(p, 'lawn', back.difference(gp).difference(sbox(5.0, ZBK, PX, ZBK + 2.6)), -0.3, 0.0)
    ext_y(p, 'conc_s', sbox(5.0, ZBK + 0.06, PX - 0.06, ZBK + 2.6), -0.3, 0.02)
    # muro da frente com pilares e o portao (vao do caminho); mureta entre os jardins (x = 0)
    for (a, b) in ((0.0, PATH[0] - 0.22), (PATH[1] + 0.22, PX - 0.19)): low_wall(p, a, b, ZW - 0.115)
    for x in (PATH[0] - 0.2, PATH[1] + 0.2): pier(p, x, ZW - 0.115)
    pier(p, PX - 0.19, ZW - 0.115, 0.8)
    return p
def party_front():
    """Mureta entre os 2 jardins da frente, no eixo x = 0 (pivo: chao; uma so para o par)."""
    p = P(); low_wall(p, MZ + BAY_P + 0.6, ZW - 0.23, 0.0, 0.5, 'z'); return p
def street():
    """Calcada, guia, sarjeta e rua (asfalto com faixa central tracejada) na frente do par de casas, e a calcada do outro lado."""
    p = Piece(); X0, X1 = SX0, SX1
    tiles(p, sbox(X0, WALK[0], X1, WALK[1]), -0.3, 0.0, 0.6, 'conc_s', 0.006, 'conc_r')
    ext_y(p, 'curb', sbox(X0, CURB[0], X1, CURB[1]), -0.3, 0.0); prof_x(p, 'curb', X0, X1, [(CURB[1], -0.15), (CURB[1] + 0.3, -0.15), (CURB[1] + 0.3, -0.13), (CURB[1], -0.12)])
    ext_y(p, 'asphalt', sbox(X0, CURB[1] + 0.3, X1, ROAD[1] - 0.3), -0.3, -0.15)
    ext_y(p, 'curb', sbox(X0, ROAD[1], X1, ROAD[1] + 0.15), -0.3, 0.0); prof_x(p, 'curb', X0, X1, [(ROAD[1] - 0.3, -0.15), (ROAD[1], -0.15), (ROAD[1], -0.12), (ROAD[1] - 0.3, -0.13)])
    for x in np.arange(X0 + 0.5, X1 - 1.0, 4.0): p.box('line_w', x, x + 2.0, -0.15, -0.148, (ROAD[0] + ROAD[1]) / 2 - 0.06, (ROAD[0] + ROAD[1]) / 2 + 0.06)
    tiles(p, sbox(X0, ROAD[1] + 0.15, X1, WALK2[1]), -0.3, 0.0, 0.6, 'conc_s', 0.006, 'conc_r')
    for x in (-9.5, 9.5): ext_y(p, 'mulch', sbox(x - 0.6, 9.7, x + 0.6, 10.9), -0.3, -0.03)          # caldeiras das arvores
    # gramado das laterais do terreno (alem das cercas) e fundos
    ext_y(p, 'lawn', sbox(X0, ZBK - 1.0, X1, ZBK), -0.3, 0.0)
    for (a, b) in ((X0, -PX), (PX, X1)): ext_y(p, 'lawn', sbox(a, ZBK, b, ZW), -0.3, 0.0)
    return p
def hedge(L1, h=0.75, d=0.45, seed=1):
    """Cerca viva aparada (pivo: inicio, chao, ao longo de +X)."""
    p = P(); rng = np.random.default_rng(seed); p.cham('hedge', 0.0, L1, 0.0, h, -d / 2, d / 2, 0.08)
    for k in range(int(L1 / 0.25)):
        x = rng.uniform(0.05, L1 - 0.05); p.sphere('hedge', rng.uniform(0.08, 0.14), x, h - 0.02, rng.uniform(-d / 3, d / 3), 1)
    return p
def wheelie_bin(mat='bin_g'):
    """Lixeira de rodinhas generica (pivo: centro, chao; alca para -z): caixa afunilada, tampa, eixo e 2 rodas."""
    p = P(); p.hull(mat, [(x, 0.06, z) for x in (-0.24, 0.24) for z in (-0.3, 0.26)] + [(x, 0.98, z) for x in (-0.29, 0.29) for z in (-0.36, 0.34)])
    p.cham(mat, -0.31, 0.31, 0.98, 1.03, -0.4, 0.37, 0.01); seg_cyl(p, mat, (-0.25, 0.98, -0.42), (0.25, 0.98, -0.42), 0.02, 8)
    seg_cyl(p, 'steel_d', (-0.3, 0.1, -0.33), (0.3, 0.1, -0.33), 0.015, 6)
    for s in (-1, 1): disc_x(p, 'rubber', 0.1, *sorted((s * 0.26, s * 0.32)), 0.1, -0.33, 14)
    p.box('dark', -0.12, 0.12, 0.6, 0.7, 0.27, 0.29)
    return p
def shed():
    """Galpao de jardim de tabuas com telhado de 2 aguas de feltro, porta, janela e prateleira (pivo: centro, chao; porta +z)."""
    p = P(); x, z, h = 1.1, 0.9, 2.0; ya = 2.45
    p.box('conc_s', -x - 0.05, x + 0.05, 0.0, 0.1, -z - 0.05, z + 0.05)
    for k in range(int(2 * z / 0.15)):
        a = -z + k * 0.15
        for s in (-1, 1): p.box('shed', *sorted((s * x, s * (x - 0.02))), 0.1, h, a + 0.002, a + 0.148)
    for k in range(int(2 * x / 0.15)):
        a = -x + k * 0.15; top = lambda u: h + (ya - h) * (1 - abs(u) / x)
        for s in (-1, 1):
            if s > 0 and -0.4 < a + 0.075 < 0.4: continue
            p.hull('shed', [(u, y, s * z + dz) for u in (a + 0.002, a + 0.148) for y in (0.1, top(u)) for dz in (0.0, -s * 0.02)])
    p.box('shed', -0.42, 0.42, h - 0.05, h, z - 0.02, z)
    for s in (-1, 1): p.hull('dark', [(xx, h + (ya - h) * (1 - abs(xx) / x) + 0.01 + dy, zz) for xx in (0.0, s * (x + 0.12)) for zz in (-z - 0.12, z + 0.12) for dy in (0.0, 0.03)])
    p.box('glass', x - 0.01, x + 0.003, 1.1, 1.6, -0.4, 0.2); p.box('trim', x, x + 0.03, 1.08, 1.62, -0.42, 0.22)
    return p
def shed_door():
    w, h = 0.8, 1.88; p = P()
    for k in range(6): p.cham('shed', k * w / 6 + 0.002, (k + 1) * w / 6 - 0.002, 0.0, h, -0.015, 0.015, 0.003)
    for y in (0.25, h - 0.3): p.box('shed', 0.03, w - 0.03, y, y + 0.1, 0.015, 0.035)
    p.box('iron', w - 0.1, w - 0.03, 1.0, 1.03, 0.035, 0.05); return p
def washing_line():
    """Varal entre 2 postes em T com roupas (pivo: chao, ao longo de +X, 5 m)."""
    p = P()
    for x in (0.0, 5.0): p.box('steel', x - 0.03, x + 0.03, 0.0, 1.9, -0.03, 0.03); p.box('steel', x - 0.03, x + 0.03, 1.9, 1.94, -0.35, 0.35)
    for z in (-0.3, 0.0, 0.3): seg_cyl(p, 'paper', (0.0, 1.92, z), (5.0, 1.86, z), 0.004, 4)
    for (x, w, h, m, z) in ((0.8, 0.5, 0.6, 'bed_w', 0.0), (1.5, 0.4, 0.5, 'blue', 0.0), (2.4, 0.7, 0.9, 'bed_b', 0.3), (3.4, 0.35, 0.4, 'velvet', -0.3), (4.0, 0.45, 0.55, 'cushion', 0.0)):
        p.box(m, x, x + w, 1.88 - h, 1.88, z - 0.004, z + 0.004)
    return p
def garden_bench():
    p = P()
    for x in (-0.65, 0.65): p.hull('iron', [(x + dx, y, z) for dx in (-0.02, 0.02) for (y, z) in ((0.0, -0.25), (0.0, 0.25), (0.45, 0.2), (0.85, -0.25))])
    for k in range(4): p.cham('wood', -0.75, 0.75, 0.43, 0.46, -0.2 + k * 0.11, -0.12 + k * 0.11, 0.005)
    for k in range(3): p.cham('wood', -0.75, 0.75, 0.55 + k * 0.1, 0.62 + k * 0.1, -0.26 - k * 0.012, -0.23 - k * 0.012, 0.005)
    return p
def pot_plant(r=0.22, seed=4):
    p = P(); lathe(p, 'clay', [(0.0, 0.0), (r * 0.7, 0.0), (r, 0.36), (r + 0.03, 0.4), (0.0, 0.4)], sec=14); p.merge(bush(r + 0.12, seed), tr(0, 0.4, 0)); return p
def street_lamp(): return lamp_post(4.2)
def post():
    p = P(); p.box('dkwood', -0.05, 0.05, -0.1, 1.9, -0.05, 0.05); p.hull('dkwood', [(x, 1.9, z) for x in (-0.06, 0.06) for z in (-0.06, 0.06)] + [(0, 1.98, 0)]); return p
def fence(L1=2.4, h=1.8):
    """Painel de cerca de tabuas de madeira (pivo: inicio, chao; ao longo de +X): mourao, 2 travessas e tabuas."""
    p = Piece(); p.box('dkwood', 0.0, 0.1, -0.1, h + 0.1, -0.05, 0.05)
    for y in (0.3, h - 0.3): p.box('wood', 0.1, L1, y, y + 0.09, 0.05, 0.09)
    for x in np.arange(0.1, L1 - 0.01, 0.145): p.box('wood', x + 0.003, min(x + 0.142, L1), 0.05, h, 0.09, 0.11)
    return p
# ============================================================================ pecas
def mir(p): return mirrored(p, mirror_x(0.0))
pieces = {}
def both(n, q): pieces[n + '_r'] = q; pieces[n + '_l'] = mir(q)
for k in ('0', '1'): both(f'shell_{k}', shell(k)); both(f'stair_{k}', stair(k))
both('shell_a', shell_a())
for k in ('0', '1', 'a'): both(f'slab_{k}', slab(k)); both(f'walls_{k}', walls(k)); both(f'furn_{k}', furn(k))
both('rail_a', stair_rail_a()); both('roof', roof()); both('out_roof', out_roof()); both('site', site())
pieces.update({'door_front': door_front(), 'door_int': door_int(), 'door_back': door_back(), 'gate_iron': gate_iron(PATH[1] - PATH[0] + 0.38), 'gate_wood': gate_wood(GATE_S[1] - GATE_S[0]),
               'shed_door': shed_door(), 'street': street(), 'party_front': party_front(), 'hedge': hedge(3.2), 'bin_g': wheelie_bin('bin_g'), 'bin_b': wheelie_bin('bin_b'),
               'shed': shed(), 'washing_line': washing_line(), 'garden_bench': garden_bench(), 'pot_plant': pot_plant(), 'fence': fence(2.4, 1.8),
               'fence_s': fence(2.2, 1.8), 'fence_h': fence(1.2, 1.8), 'fence_g': fence(PX - GATE_S[1], 1.8), 'post': post(), 'street_lamp': street_lamp(),
               'tree': tree(6.5, 2.0, 'leaf', 2), 'tree_b': tree(5.5, 1.8, 'leaf2', 5), 'bush': bush(0.45, 3),
               'car_sedan_r': car('car_r', 'sedan'), 'car_hatch_b': car('car_b', 'hatch'), 'car_wagon_g': car('car_g', 'wagon'), 'car_coupe_y': car('car_y', 'coupe')})
pieces['player_scale_ref'] = player_ref()

# ============================================================================ montagem
G = ['casas']; J = ['rua']
def fl(k): return G + [f'floor{k}']
def door_b(n, axis, a, b, c, y, hinge, into, tags): door_at(n, axis, a, b, c, y, hinge, into, tags)
def door_m(n, axis, a, b, c, y, hinge, into, tags):
    """Porta da casa da direita e a espelhada na casa da esquerda."""
    door_b(n, axis, a, b, c, y, hinge, into, tags)
    if axis == 'x': door_b(n, axis, -b, -a, c, y, 'b' if hinge == 'a' else 'a', into, tags)
    else: door_b(n, axis, a, b, -c, y, hinge, -into, tags)
for s in 'rl':
    side = ['casa_d' if s == 'r' else 'casa_e']
    for k in range(NL + 1):
        y = LV[k]; t = fl(k) + side; kk = 'a' if k == NL else str(k)
        put(f'shell_{kk}_{s}', 0, y, 0, 0, t + ['ext']); put(f'slab_{kk}_{s}', 0, y, 0, 0, t); put(f'walls_{kk}_{s}', 0, y, 0, 0, t); put(f'furn_{kk}_{s}', 0, y, 0, 0, t)
        if k < NL: put(f'stair_{kk}_{s}', 0, y, 0, 0, t)
    put(f'rail_a_{s}', 0, LV[NL], 0, 0, fl(NL) + side)
    put(f'roof_{s}', 0, 0, 0, 0, G + ['roof'] + side); put(f'out_roof_{s}', 0, 0, 0, 0, fl(1) + side + ['ext'])
    put(f'site_{s}', 0, 0, 0, 0, J + side)
y = LV[0]
door_m('door_front', 'x', FDOOR[0] + 0.07, FDOOR[1] - 0.07, MZ - 0.245, y, 'a', -1, fl(0))
for (z0, z1, h) in ((2.6, 3.4, 'b'), (-1.1, -0.3, 'a')):
    door_m('door_int', 'z', z0, z1, XH, y, h, -1, fl(0))
door_m('door_int', 'x', KDOOR[0], KDOOR[1], -MZ + T / 2, y, 'a', -1, fl(0))
door_m('door_int', 'x', 1.5, 2.3, ZK, y, 'b', -1, fl(0))
door_m('door_back', 'z', BDOOR[0] + 0.07, BDOOR[1] - 0.07, OXR - 0.245, y, 'a', -1, fl(0))
y = LV[1]
for (z0, z1, h) in ((0.45, 1.25, 'a'), (-1.1, -0.3, 'a')): door_m('door_int', 'z', z0, z1, XH, y, h, -1, fl(1))
door_m('door_int', 'x', 4.4, 5.2, ZBATH, y, 'b', 1, fl(1))
# jardim e quintal
door_m('gate_iron', 'x', PATH[0] - 0.19, PATH[1] + 0.19, ZW - 0.115, 0.0, 'a', -1, J)
door_m('gate_wood', 'x', GATE_S[0], GATE_S[1], 3.0, 0.0, 'a', -1, J)
for sx in (1, -1):
    put('post', sx * (GATE_S[0] - 0.05), 0.0, 3.0, 0, J)
    put('fence_g', GATE_S[1] if sx > 0 else -PX, 0.0, 3.0, 0, J)
    xb = sx * PX
    for i in range(7): put('fence', xb, 0.0, ZBK + i * 2.4, -90, J)
    put('fence_s', xb, 0.0, ZBK + 7 * 2.4, -90, J)
    for i in range(3): put('fence', (0.0 if sx > 0 else -PX) + i * 2.4, 0.0, ZBK, 0, J)
    put('fence_h', (7.2 if sx > 0 else -1.2), 0.0, ZBK, 0, J)
    put('shed', sx * 6.8, 0.0, ZBK + 1.3, 0, J); put('shed_door', sx * 6.8 - 0.4, 0.1, ZBK + 2.19, 0, J, door=-80)
    put('washing_line', 0.9 if sx > 0 else -5.9, 0.0, -12.0, 0, J)
    put('garden_bench', sx * 4.6, 0.0, OZ1 - 1.0, 180, J)
    for (x, z) in ((3.1, -5.0), (6.1, -8.4)): put('pot_plant', sx * x, 0.0, z, 0, J)
    for (x, z) in ((0.9, 5.75), (2.0, 5.9), (3.1, 5.75)): put('bush', sx * x, 0.0, z, 0, J)
    put('hedge', 0.3 if sx > 0 else -3.5, 0.0, ZW - 0.58, 0, J)
    for (x, n) in ((6.95, 'bin_g'), (7.65, 'bin_b')): put(n, sx * x, 0.0, ZW - 0.75, 180, J)
    put('tree', sx * 3.0, 0.0, -13.0, 0, J + ['roof'])
for i in range(3): put('fence', 0.0, 0.0, ZBK + i * 2.4, -90, J)
put('party_front', 0, 0, 0, 0, J)
put('street', 0, 0, 0, 0, J)
for x in (-4.0, 4.0, -11.0, 11.0): put('street_lamp', x, 0.0, WALK[1] - 0.45, 0, J)
for (x, n) in ((-9.5, 'tree'), (9.5, 'tree_b')): put(n, x, 0.0, 10.3, 0, J + ['roof'])
for (x, n) in ((-8.0, 'car_sedan_r'), (-1.8, 'car_hatch_b'), (5.2, 'car_wagon_g')): put(n, x, -0.15, CURB[1] + 1.15, -90, J)
for (x, n) in ((-4.5, 'car_coupe_y'), (8.5, 'car_sedan_r')): put(n, x, -0.15, ROAD[1] - 1.15, 90, J)
put('player_scale_ref', 5.6, 0.0, 9.6, 0, J); put('player_scale_ref', 5.0, LV[0], 2.6, 0, fl(0))

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'ground': 0.0, 'floor_height': H, 'floor_levels': LV, 'floors': NL + 1, 'footprint': [list(c) for c in sbox(-MX, -MZ, MX, MZ).exterior.coords],
                       'wall_thickness': T, 'partition_thickness': TP, 'stair': {'risers': SNR, 'rise': SRR, 'tread': STRD, 'x': [SXB[0], SXA[1]], 'z': [-MZ + T, ZF]},
                       'bay_window': {'center_x': BAYC, 'half_width': BAY_W, 'projection': BAY_P}, 'roof_pitch_deg': 40,
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
