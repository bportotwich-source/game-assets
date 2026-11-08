"""Kit 55: loft industrial convertido, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Antigo armazem de tijolo de 20 x 14 m e 7 pavimentos convertido em lofts: pilares de tijolo salientes e paineis rebaixados,
janelas de aco de muitos vidros com bascula central, peitoris de pedra, vergas de tijolo em pe, embasamento de pedra,
cornija de tijolo em cachorrada com capa de pedra. Terreo com cafe (vitrines de madeira, toldo listrado, balcao, mesas) e
portaria dos lofts (porta com bandeira, marquise de aco, caixas de correio). Estrutura interna de madeira (pilares, vigas e
barrotes aparentes), piso de tabuas, escada em U enclausurada e elevador. Um loft mobiliado por andar (cozinha, ilha, jantar,
sala, quarto atras de divisoria de aco e vidro, escritorio, banheiro). Escada de incendio externa em zigue-zague com
plataformas de grelha, escada de mao basculante e escada de marinheiro ate a cobertura. Cobertura com casa de maquinas,
caixa d'agua de madeira sobre torre de aco, deck com pergolado, floreiras, espreguicadeiras e condensadoras. Calcada com
arvores, postes, bancos, bicicletario, hidrante, food truck amarelo e carros genericos. Arte original e sem texto.
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
from shapely import affinity
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
CAR_COLS = {'car_r': (176, 70, 58), 'car_b': (70, 96, 140), 'car_g': (88, 120, 86), 'car_y': (206, 176, 90), 'car_w': (222, 218, 206),
            'car_o': (186, 104, 56), 'car_t': (92, 146, 142), 'car_k': (48, 50, 54)}
configurar(cores=dict({'render': (222, 212, 186), 'plaster': (236, 232, 222), 'ceil': (244, 242, 236), 'concrete': (186, 182, 174),
                       'asphalt': (84, 86, 88), 'conc_s': (178, 176, 170), 'conc_d': (150, 148, 142), 'coping': (206, 202, 192), 'glass_t': (120, 160, 180), 'gravel': (170, 162, 148), 'grass': (116, 150, 78), 'dirt': (150, 128, 98),
                       'skirt': (214, 204, 182), 'skirt_g': (170, 172, 168), 'panel': (186, 150, 108), 'carpet': (150, 128, 110), 'carpet_b': (110, 124, 140),
                       'vinyl_f': (214, 206, 186), 'tile_a': (222, 224, 220), 'cab': (176, 132, 86), 'ctop': (226, 218, 196), 'enamel': (240, 238, 232),
                       'alu': (196, 200, 204), 'metal': (176, 180, 184), 'frame': (60, 62, 66), 'chrome': (210, 214, 218), 'steel': (120, 126, 132),
                       'steel_d': (56, 60, 64), 'iron': (40, 42, 44), 'galv': (164, 170, 170), 'rust': (140, 70, 40), 'trim': (110, 80, 56),
                       'wood': (176, 132, 88), 'dkwood': (110, 78, 54), 'deck': (164, 124, 84), 'pallet': (176, 140, 96), 'lattice': (232, 228, 216),
                       'lamp_glass': (255, 238, 196), 'dark': (34, 34, 36), 'rubber': (30, 30, 32), 'glass': (150, 186, 204), 'mirror': (200, 214, 220),
                       'fabric': (120, 100, 80), 'fabric2': (110, 120, 90), 'fabric3': (150, 90, 70), 'bed_w': (236, 232, 222), 'bed_b': (90, 120, 160),
                       'porcelain': (244, 244, 240), 'paper': (236, 232, 220), 'vinyl': (70, 60, 56), 'vinyl_b': (60, 80, 120), 'screen': (30, 40, 48),
                       'leaf': (86, 128, 62), 'leaf2': (108, 144, 70), 'bark': (110, 84, 60), 'plant': (70, 120, 60), 'pot': (176, 110, 80),
                       'paint_w': (238, 238, 232), 'paint_y': (232, 190, 50), 'paint_r': (196, 52, 44), 'paint_g': (52, 110, 70), 'paint_b': (50, 100, 170),
                       'food_g': (110, 160, 70), 'food_r': (200, 60, 50), 'food_y': (230, 190, 80), 'flag_r': (200, 50, 44), 'flag_b': (52, 104, 180),
                       'cloth_r': (196, 80, 70), 'cloth_y': (230, 200, 110), 'cloth_b': (100, 140, 190), 'bench_g': (40, 92, 62), 'brick': (150, 70, 52), 'brick_i': (168, 96, 74), 'brick_d': (120, 56, 42), 'stone': (204, 196, 178), 'win_k': (46, 52, 50), 'shop_g': (42, 76, 60), 'timber': (150, 110, 72), 'floor_w': (170, 128, 86), 'awn_g': (44, 92, 70), 'awn_w': (236, 228, 206), 'membrane': (104, 106, 108), 'corten': (140, 80, 50), 'truck_y': (230, 186, 40), 'tank_w': (138, 104, 72), 'leather': (130, 80, 50), 'rug': (170, 70, 60), 'rug2': (60, 80, 110), 'tile_h': (212, 208, 198), 'cream': (240, 232, 214), 'coffee': (80, 54, 40), 'basket': (180, 150, 100), 'door': (92, 60, 40), 'door_int': (196, 178, 150), 'sash': (240, 238, 232), 'cast': (52, 70, 66), 'seam': (88, 90, 92), 'tile_a': (226, 230, 228), 'marble': (232, 230, 224), 'cab_g': (108, 128, 110), 'cake': (214, 170, 120), 'chalk': (40, 46, 44),
                       'propane': (236, 236, 230), 'brass': (190, 160, 90), 'gold': (200, 170, 90), 'cart_w': (240, 236, 226), 'flag_o': (230, 140, 50), 'neon_r': (220, 60, 50), 'vinyl_g': (80, 110, 80), 'vinyl_r': (140, 60, 50), 'dumpster': (60, 104, 76), 'player': (90, 140, 220), 'water': (150, 190, 220)}, **CAR_COLS),
           texturas={'conc_s': 'render', 'conc_d': 'render', 'coping': 'render', 'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'asphalt': 'render', 'gravel': 'render', 'grass': 'render',
                     'dirt': 'render', 'wood': 'planks', 'dkwood': 'planks', 'deck': 'planks', 'pallet': 'planks', 'panel': 'planks', 'cab': 'planks',
                     'carpet': 'render', 'carpet_b': 'render', 'bark': 'render', 'brick': 'brick', 'brick_i': 'brick', 'stone': 'render', 'timber': 'planks', 'floor_w': 'planks', 'membrane': 'render', 'tank_w': 'planks', 'tile_h': 'plaster'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4

# ============================================================================ medidas
W = 2.0; T = 0.45; t_ = 0.12
Y0 = 0.15; GH = 4.2; H = 3.4; ST = 0.3; GY = -0.3
LV = [Y0, Y0 + GH] + [Y0 + GH + k * H for k in range(1, 7)]      # 0,15 4,35 7,75 ... 24,75 (cobertura)
NF = 7                                                           # pavimentos (terreo + 6)
BX, BZ = 10.0, 7.0                                               # predio de -10 a 10 em X e -7 a 7 em Z
IX, IZ = BX - T, BZ - T                                          # faces internas 9,55 e 6,55
BAYS_L = (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5); BAYS_S = (-4.5, -1.5, 1.5, 4.5)
RW = 1.3; OW = 1.1                                               # meia largura do painel rebaixado e do vao
SY, HY = 0.95, 2.75                                              # peitoril e verga das janelas tipo
GSY, GHY = 0.95, 3.2                                             # janelas do terreo
PAR = 1.25                                                       # topo da platibanda acima da cobertura
# nucleo: escada em U (lances em Z junto a parede leste), elevador e hall
LA = (8.35, IX); LB = (7.05, 8.25); SWX = (6.85, 7.05)           # lances A e B, parede oeste da escada
HWX = (4.45, 4.65); HFZ = (-0.2, 0.0)                            # parede oeste do hall e parede da frente
SHZ = (-4.55, -4.35); MZ = -5.35                                 # parede da frente do poco e borda do patamar intermediario
TRD = 0.28
NRG, NRT = 12, 10                                                # espelhos por lance (terreo, tipo)
RUNG, RUNT = (NRG - 1) * TRD, (NRT - 1) * TRD                    # 3,08 e 2,52
ZG, ZT = MZ + RUNG, MZ + RUNT                                    # inicio dos lances: -2,27 e -2,83
EDX = 5.75                                                       # eixo da porta do elevador
LDX = (5.3, 6.2); SDZ = (-1.6, -0.7)                             # porta do loft (hall) e porta da escada
BWX = (2.8, 3.0); BWZ = (-3.4, -3.2); BDX = (3.42, 4.27)         # banheiro do loft
CWX = (2.9, 3.1)                                                 # parede entre cafe e portaria
PX = (-6.0, 0.0, 5.0); PZ = (-3.0, 3.0)                          # pilares internos
GD = 0.62; JD = 0.22                                              # altura total viga+barrote, barrote
FW = 1.75; FEX = (10.0, 10.0 + FW); FEL = 10.0 + (0.8 + FW - 0.06) / 2                                  # escada de incendio: plataforma e eixo da faixa do lance
SX0, SX1, SZ0, SZ1 = -14.0, 17.0, -11.0, 18.0
SWZ = 10.6; CZ = 10.8; EWX = 13.6                                # calcada da frente ate z 10,6, guia, calcada leste ate x 13,6
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

# ============================================================================ fachadas (pivo local: face externa em z = 0, parede para -Z, x ao longo)
ZS = [-T, -T + 0.015, -0.1, -0.06, 0.0]
REC_TOP_P = 0.45
def hole_of(c, k, st):
    if k == 'win': return (c - OW, c + OW, *((GSY, GHY) if st == 'g' else (SY, HY)))
    if k == 'fe': return (c - OW, c + OW, 0.2, HY)
    if k == 'shop': return (c - 1.25, c + 1.25, 0.0, GHY)
    if k == 'door': return (c - OW, c + OW, 0.0, GHY)
    if k == 'sdoor': return (c - 0.5, c + 0.5, 0.0, 2.2)
    return None
def soldier(p, c, y, w=1.2):
    n = int((2 * w + 0.012) / 0.082); b = (2 * w - (n - 1) * 0.012) / n
    for i in range(n):
        x = c - w + i * (b + 0.012); p.box('brick_d', x, x + b, y, y + 0.24, -0.06, -0.046)
def lite_grid(p, ia, ib, ja, jb, ncol, nrow, skip=None, mat='win_k', z=(-0.19, -0.15), gz=(-0.172, -0.168), bw=0.0125):
    """Grade de vidros: barras verticais inteiras e travessas entre elas; skip = retangulo sem barras nem vidro (bascula)."""
    xe = list(np.linspace(ia, ib, ncol + 1)); ye = list(np.linspace(ja, jb, nrow + 1))
    for x in xe[1:-1]:
        cuts = [(ja, jb)]
        if skip is not None and skip[0] + 1e-6 < x < skip[1] - 1e-6: cuts = segs_excl([(skip[2] + bw, skip[3] - bw)], ja, jb)
        for (a, b) in cuts: p.box(mat, x - bw, x + bw, a, b, *z)
    for y in ye[1:-1]:
        for (a, b) in zip(xe[:-1], xe[1:]):
            xa = a + (bw if a > ia + 1e-6 else 0.0); xb = b - (bw if b < ib - 1e-6 else 0.0)
            if skip is not None and skip[2] + 1e-6 < y < skip[3] - 1e-6 and skip[0] - 1e-6 <= a and b <= skip[1] + 1e-6: continue
            p.box(mat, xa, xb, y - bw, y + bw, z[0] + 0.002, z[1] - 0.002)
    if skip is None: p.box('glass', ia - 0.01, ib + 0.01, ja - 0.01, jb + 0.01, *gz)
    else:
        s0, s1, s2, s3 = skip
        for (a, b, c_, d) in ((ia - 0.01, ib + 0.01, ja - 0.01, s2), (ia - 0.01, ib + 0.01, s3, jb + 0.01), (ia - 0.01, s0, s2, s3), (s1, ib + 0.01, s2, s3)):
            if b - a > 1e-3 and d - c_ > 1e-3: p.box('glass', a, b, c_, d, *gz)
def vent(p, x0, x1, y0, y1, ang=-7.0):
    """Bascula central de eixo horizontal: quadro de 3 cm, cruzeta e vidro, girada ang graus."""
    q = Piece(); s = 0.03; g = 0.016; a, b, c, d = x0 + g, x1 - g, y0 + g, y1 - g; z0, z1 = -0.186, -0.154
    q.box('win_k', a, a + s, c, d, z0, z1); q.box('win_k', b - s, b, c, d, z0, z1)
    q.box('win_k', a + s, b - s, c, c + s, z0, z1); q.box('win_k', a + s, b - s, d - s, d, z0, z1)
    xm, ym = (a + b) / 2, (c + d) / 2
    q.box('win_k', xm - 0.01, xm + 0.01, c + s, d - s, z0 + 0.003, z1 - 0.003)
    for (u, v) in ((a + s, xm - 0.01), (xm + 0.01, b - s)): q.box('win_k', u, v, ym - 0.01, ym + 0.01, z0 + 0.005, z1 - 0.005)
    q.box('glass', a + 0.01, b - 0.01, c + 0.01, d - 0.01, -0.171, -0.167)
    M = trimesh.transformations.rotation_matrix(math.radians(ang), [1, 0, 0], [0, (y0 + y1) / 2, -0.17]); p.merge(q, M)
    for s_ in (-1, 1):
        e = a if s_ < 0 else b; p.box('steel', e - 0.014, e + 0.014, ym - 0.02, ym + 0.02, -0.196, -0.192)
def steel_window(p, c, ya, yb, nrow=5, door=False):
    """Janela de aco de fabrica: quadro de 5 cm, grade de 4 x nrow vidros e bascula central (ou porta de saida no meio)."""
    f = 0.05; Z0, Z1 = -0.2, -0.14; xa, xb = c - OW, c + OW; yf = ya + 0.006
    p.box('win_k', xa, xa + f, yf, yb, Z0, Z1); p.box('win_k', xb - f, xb, yf, yb, Z0, Z1); p.box('win_k', xa + f, xb - f, yb - f, yb, Z0, Z1)
    ia, ib, ja, jb = xa + f, xb - f, yf + f, yb - f
    if not door:
        p.box('win_k', xa + f, xb - f, yf, yf + f, Z0, Z1)
        xe = np.linspace(ia, ib, 5); ye = np.linspace(ja, jb, nrow + 1); r0, r1 = nrow - 3, nrow - 1
        sk = (xe[1], xe[3], ye[r0], ye[r1]); lite_grid(p, ia, ib, ja, jb, 4, nrow, sk); vent(p, *sk)
    else:
        DH = 2.3; dp = 0.45
        for s in (-1, 1):
            a, b = sorted((c + s * dp, c + s * (dp + 0.05))); p.box('win_k', a, b, yf, DH + 0.05, Z0, Z1)
            a, b = (xa + f, c - dp - 0.05) if s < 0 else (c + dp + 0.05, xb - f); p.box('win_k', a, b, yf, yf + f, Z0, Z1)
            lite_grid(p, a, b, ja, jb, 1, 6)
        p.box('win_k', c - dp, c + dp, DH, DH + 0.05, Z0, Z1); lite_grid(p, c - dp, c + dp, DH + 0.05, jb, 2, 1)
def stone_sill(p, c, y, inner=True, w=1.2):
    p.box('stone', c - w, c + w, y - 0.07, y + 0.006, -0.2, 0.04)
    p.box('stone', c - w + 0.02, c + w - 0.02, y - 0.1, y - 0.07, -0.056, 0.02)
    if inner: p.box('timber', c - OW - 0.05, c + OW + 0.05, y, y + 0.035, -T - 0.03, -0.2)
def lintel(p, c, y, w=1.15):
    p.box('win_k', c - w, c + w, y - 0.008, y, -0.13, -0.065)
def storefront(p, c, hw=1.25, door=False):
    """Vitrine de madeira pintada (ou porta com 2 bandeiras laterais): rodape almofadado, peitoril, vidro, travessa e bandeira."""
    m = 'shop_g'; z0, z1 = -0.28, -0.18; top = GHY; xa, xb = c - hw, c + hw; j = 0.08
    p.box(m, xa, xa + j, 0.012, top, z0, z1); p.box(m, xb - j, xb, 0.012, top, z0, z1); p.box(m, xa + j, xb - j, top - j, top, z0, z1)
    TB = 2.42 if door else 2.5
    p.box(m, xa + j, xb - j, TB, TB + 0.08, z0 - 0.01, z1 + 0.01)
    spans = [(xa + j, xb - j)] if not door else [(xa + j, c - 0.57), (c + 0.57, xb - j)]
    if door:
        for s in (-1, 1): a, b = sorted((c + s * 0.5, c + s * 0.57)); p.box(m, a, b, 0.012, TB, z0, z1)
    for (a, b) in spans:
        p.box(m, a, b, 0.012, 0.5, z0 + 0.01, z1 - 0.01); p.box(m, a, b, 0.5, 0.58, z0 - 0.015, z1 + 0.02)
        n = max(1, int(round((b - a) / 0.75)))
        for i in range(n):
            u = a + (b - a) * i / n + 0.06; v = a + (b - a) * (i + 1) / n - 0.06; p.cham(m, u, v, 0.1, 0.42, z1 - 0.011, z1 + 0.006, 0.006)
        if not door and b - a > 1.6: p.box(m, (a + b) / 2 - 0.035, (a + b) / 2 + 0.035, 0.58, TB, z0, z1)
        p.box('glass', a - 0.01, b + 0.01, 0.58, TB, -0.232, -0.228)
    for x in np.linspace(xa + j, xb - j, 5)[1:-1]: p.box(m, x - 0.025, x + 0.025, TB + 0.08, top - j, z0 + 0.01, z1 - 0.01)
    p.box('glass', xa + j - 0.01, xb - j + 0.01, TB + 0.08, top - j + 0.01, -0.232, -0.228)
    p.box('stone', xa, xb, -0.02, 0.012, -0.3, 0.04)
    # testeira de letreiro (sem texto) com capa e frisos dourados
    p.box(m, xa, xb, top + 0.04, top + 0.3, -0.06, -0.025); p.box(m, xa - 0.02, xb + 0.02, top + 0.3, top + 0.36, -0.06, 0.004)
    p.box('gold', xa + 0.08, xb - 0.08, top + 0.09, top + 0.105, -0.025, -0.02); p.box('gold', xa + 0.08, xb - 0.08, top + 0.24, top + 0.255, -0.025, -0.02)
def service_door(p, c):
    z0, z1 = -0.3, -0.16
    p.box('steel_d', c - 0.5, c - 0.45, 0.012, 2.2, z0, z1); p.box('steel_d', c + 0.45, c + 0.5, 0.012, 2.2, z0, z1); p.box('steel_d', c - 0.45, c + 0.45, 2.15, 2.2, z0, z1)
    p.box('concrete', c - 0.5, c + 0.5, -0.02, 0.012, -0.32, 0.04)
    p.merge(wall_lamp(), tr(c, 2.75, -0.06))
def facade(Lh, bays, st):
    p = Piece(); y0, y1 = {'g': (GY - Y0, GH - ST), 't': (-ST, H - ST), 'p': (-ST, PAR - 0.08)}[st]
    holes, blinds, recs = [], [], []
    for (c, k) in bays:
        recs.append((c - RW, c + RW))
        if st == 'p': continue
        h = hole_of(c, k, st)
        if h: holes.append(h)
        if k == 'blind': blinds.append((c - OW, c + OW, *((GSY, GHY) if st == 'g' else (SY, HY))))
    rtop = REC_TOP_P if st == 'p' else y1
    xs = sorted(set([-Lh, Lh] + [v for r in recs for v in r] + [v for h in holes + blinds for v in h[:2]]))
    ys = sorted(set([y0, y1, rtop] + [v for h in holes + blinds for v in h[2:]]))
    def inr(x, y, rs): return any(a < x < b and c < y < d for (a, b, c, d) in rs)
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        if inr(cx, cy, holes): return None
        if k == 0: return 'brick' if st == 'p' else 'brick_i'
        if k == 1: return 'brick'
        if k == 2: return None if inr(cx, cy, blinds) else 'brick'
        return 'brick' if (cy > rtop or not any(a < cx < b for (a, b) in recs)) else None
    for m, mesh in grid_solid(xs, ys, ZS, cell).items(): p.add(m, mesh)
    if st == 'p':
        for (a, b) in recs:                                           # cachorrada no topo de cada painel rebaixado
            for x in np.arange(a + 0.1, b - 0.05, 0.2): p.box('brick_d', x - 0.06, x + 0.06, REC_TOP_P - 0.1, REC_TOP_P, -0.06, -0.025)
        for x in np.arange(-Lh + 0.14, Lh - 0.05, 0.25): p.box('brick_d', x - 0.055, x + 0.055, 0.52, 0.6, 0.0, 0.05)
        return p
    for (c, k) in bays:
        if k == 'win':
            ya, yb = (GSY, GHY) if st == 'g' else (SY, HY)
            steel_window(p, c, ya, yb, 6 if st == 'g' else 5); stone_sill(p, c, ya); soldier(p, c, yb); lintel(p, c, yb)
        if k == 'fe': steel_window(p, c, 0.2, HY, door=True); p.box('stone', c - 1.2, c + 1.2, 0.13, 0.206, -0.3, 0.04); soldier(p, c, HY); lintel(p, c, HY)
        if k == 'blind':
            ya, yb = (GSY, GHY) if st == 'g' else (SY, HY); stone_sill(p, c, ya, inner=False); soldier(p, c, yb)
        if k == 'shop': storefront(p, c)
        if k == 'door': storefront(p, c, OW, door=True)
        if k == 'sdoor': service_door(p, c); soldier(p, c, 2.2, 0.62); lintel(p, c, 2.2, 0.55)
    return p
SIDES = {'front': (tr(0, 0, BZ), BX, lambda c: c), 'back': (rot_y(180, (0, 0, -BZ)), BX, lambda c: -c),
         'east': (rot_y(90, (BX, 0, 0)), IZ, lambda c: -c), 'west': (rot_y(-90, (-BX, 0, 0)), IZ, lambda c: c)}
WIN_L = [(c, 'win') for c in BAYS_L]; WIN_S = [(c, 'win') for c in BAYS_S]
BAYDEF = {'g': {'front': [(-7.5, 'shop'), (-4.5, 'shop'), (-1.5, 'shop'), (1.5, 'door'), (4.5, 'door'), (7.5, 'shop')],
                'back': [(-7.5, 'win'), (-4.5, 'win'), (-1.5, 'sdoor'), (1.5, 'win'), (4.5, 'blind'), (7.5, 'blind')],
                'east': WIN_S, 'west': WIN_S},
          't': {'front': WIN_L, 'back': [(-7.5, 'win'), (-4.5, 'win'), (-1.5, 'win'), (1.5, 'win'), (4.5, 'blind'), (7.5, 'blind')],
                'east': [(-4.5, 'win'), (-1.5, 'win'), (1.5, 'fe'), (4.5, 'win')], 'west': WIN_S}}
BAYDEF['p'] = BAYDEF['t']
def rect(d=0.0): return off(sbox(-BX, -BZ, BX, BZ), d) if d else sbox(-BX, -BZ, BX, BZ)
def ring(d0, d1): return rect(d1).difference(rect(d0))
def openings_world(st):
    """Vaos que vao ate o chao (para interromper o embasamento), no plano x-z."""
    out = []
    for side, (M, Lh, f) in SIDES.items():
        for (cw, k) in BAYDEF[st][side]:
            h = hole_of(f(cw), k, st) if k in ('shop', 'door', 'sdoor') else None
            if not h: continue
            pts = np.array([[h[0], 0, -1.0, 1], [h[1], 0, 1.0, 1]]) @ M.T
            out.append(sbox(min(pts[:, 0]), min(pts[:, 2]), max(pts[:, 0]), max(pts[:, 2])))
    return unary_union(out)
def envelope(st):
    """Envoltoria de um pavimento (4 fachadas), pivo: x = z = 0, y = piso do pavimento."""
    p = Piece()
    for side, (M, Lh, f) in SIDES.items(): p.merge(facade(Lh, [(f(c), k) for (c, k) in BAYDEF[st][side]], st), M)
    if st == 'g':
        ext_y(p, 'stone', ring(-0.06, 0.04).difference(openings_world('g')), GY - Y0 + 0.003, 0.55)
        ext_y(p, 'stone', ring(-0.06, 0.06), GH - ST - 0.28, GH - ST - 0.04)
        ext_y(p, 'stone', ring(-0.06, 0.08), GH - ST - 0.04, GH - ST - 0.003)
    return p
def parapet():
    """Platibanda com cachorrada, faixas de tijolo, capa de pedra e rufo da manta por dentro (pivo: y = cobertura)."""
    p = envelope('p')
    ext_y(p, 'brick_d', ring(0.0, 0.08), 0.6, 0.72); ext_y(p, 'brick', ring(0.0, 0.12), 0.72, 0.8)
    ext_y(p, 'stone', ring(-T - 0.04, 0.06), PAR - 0.08, PAR)
    ext_y(p, 'membrane', ring(-T - 0.01, -T), 0.012, 0.35); ext_y(p, 'galv', ring(-T - 0.018, -T), 0.33, 0.37)
    return p
def wall_grid(p, axis, u0, u1, v0, v1, holes, ya, yb, mat='concrete', inner='plaster'):
    """Parede da torre com vaos: axis = 'x' (corre em X, espessura em Z de v0 a v1) ou 'z'. holes = (a, b, y0, y1)."""
    us = sorted(set([u0, u1] + [h for q in holes for h in q[:2]])); ys = sorted(set([ya, yb] + [h for q in holes for h in q[2:]]))
    def cell(i, j, k):
        cu = (us[i] + us[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cu < b and c < cy < d: return None
        return mat
    for m, mesh in grid_solid(us, ys, [v0, v1], cell).items():
        if axis == 'z':
            v = mesh.vertices.copy(); mesh.vertices = np.stack([v[:, 2], v[:, 1], v[:, 0]], 1); mesh.invert()
        p.add(m, mesh)
def elev_door():
    """Portas de elevador de aco escovado, 2 folhas, com batente, soleira, botoeira e indicador (pivo: centro embaixo, frente +Z)."""
    p = Piece(); w = 0.9
    for s in (-1, 1):
        a, b = sorted((0.0, s * w / 2)); p.box('steel', a + s * 0.003, b, 0.0, 2.1, -0.06, -0.03)
    for s in (-1, 1): p.box('chrome', *sorted((s * w / 2, s * (w / 2 + 0.06))), 0.0, 2.16, 0.0, 0.02)
    p.box('chrome', -w / 2 - 0.06, w / 2 + 0.06, 2.1, 2.16, 0.0, 0.02); p.box('chrome', -w / 2, w / 2, 0.0, 0.006, -0.1, 0.02)
    p.cham('chrome', -w / 2 - 0.32, -w / 2 - 0.2, 1.0, 1.3, 0.0, 0.02, 0.005)
    for y in (1.1, 1.2): disc_z(p, 'lamp_glass', 0.02, 0.02, 0.03, -w / 2 - 0.26, y, 12)
    p.box('dark', -0.15, 0.15, 2.22, 2.32, 0.0, 0.02); p.box('neon_r', -0.06, 0.06, 2.25, 2.29, 0.02, 0.024)
    return p

# ============================================================================ lajes (pivo: x = z = 0, y = topo do piso)
LOFT_HALL = sbox(HWX[0], -IZ, IX, HFZ[1])
SHAFT = sbox(HWX[1], -IZ, SWX[0], SHZ[0])
def stair_hole(zh): return sbox(SWX[1], -IZ, IX, zh)
INNER = sbox(-IX, -IZ, IX, IZ)
def boards(p, poly, y0=-0.016, y1=0.0, w=0.15, gap=0.004, along='z', mat='floor_w'):
    """Piso de tabuas corridas (sobre fundo escuro que aparece nas juntas)."""
    b = poly.bounds; ext_y(p, 'dark', poly.buffer(-0.003, join_style=2), y0 - 0.004, y1 - 0.004)
    if along == 'z':
        for x in np.arange(b[0], b[2], w): ext_y(p, mat, sbox(x + gap / 2, b[1], x + w - gap / 2, b[3]).intersection(poly), y0, y1)
    else:
        for z in np.arange(b[1], b[3], w): ext_y(p, mat, sbox(b[0], z + gap / 2, b[2], z + w - gap / 2).intersection(poly), y0, y1)
def checker(p, poly, y0, y1, s=0.3, m1='tile_h', m2='stone', gap=0.003):
    b = poly.bounds; ext_y(p, 'dark', poly.buffer(-0.0045, join_style=2), y0 - 0.004, y1 - 0.004)
    for i, x in enumerate(np.arange(b[0], b[2], s)):
        for j, z in enumerate(np.arange(b[1], b[3], s)):
            q = sbox(x + gap, z + gap, x + s - gap, z + s - gap).intersection(poly)
            if q.area > 1e-6: ext_y(p, m1 if (i + j) % 2 == 0 else m2, q, y0, y1)
def framing(p, core=True):
    """Estrutura de madeira sob a laje: forro de tabuas, barrotes a cada 80 cm e 2 vigas mestras sobre os pilares."""
    for x in np.arange(-IX + 0.3, IX - 0.1, 0.8):
        z0 = HFZ[1] if (x + 0.04 > HWX[0] and core) else -IZ
        p.box('timber', x - 0.04, x + 0.04, -ST - JD, -ST, z0, IZ)
    for z in PZ:
        x1 = HWX[0] if (z < 0 and core) else IX
        p.cham('timber', -IX, x1, -ST - GD, -ST - JD, z - 0.15, z + 0.15, 0.012)
def slab(kind):
    """Laje de piso: forro de tabuas por baixo, concreto, piso de tabuas no loft e ladrilho no hall; furos da escada e do elevador.
    kind: '1' (1o andar: furo da escada ate o fim do lance do terreo), 't' (tipo) ou 'r' (cobertura com manta)."""
    p = Piece(); zh = ZG if kind == '1' else ZT
    region = INNER.difference(SHAFT).difference(stair_hole(zh))
    ext_y(p, 'timber', region, -ST, -ST + 0.02); ext_y(p, 'conc_s', region, -ST + 0.02, -0.02)
    if kind == 'r':
        ext_y(p, 'conc_s', region, -0.02, 0.0)
        mem = region.difference(LOFT_HALL); ext_y(p, 'membrane', mem, 0.0, 0.012)
        for x in np.arange(-IX + 1.0, IX - 0.5, 1.0):
            q = sbox(x - 0.03, -IZ, x + 0.03, IZ).intersection(mem); ext_y(p, 'seam', q, 0.012, 0.018)
        ext_y(p, 'conc_s', LOFT_HALL.difference(SHAFT).difference(stair_hole(zh)), 0.0, 0.012)
    else:
        boards(p, region.difference(LOFT_HALL), along='z')
        ext_y(p, 'tile_h', LOFT_HALL.intersection(region), -0.02, 0.0)
    framing(p)
    return p
def ground_slab():
    """Piso do terreo: tabuas no cafe, ladrilho xadrez na portaria, ladrilho liso no hall, fundo do poco do elevador."""
    p = Piece(); y0 = GY - Y0
    ext_y(p, 'conc_s', INNER.difference(SHAFT), y0, -0.02); ext_y(p, 'dark', SHAFT, y0, -1.0) if False else ext_y(p, 'conc_s', SHAFT, y0, -0.05)
    cafe = sbox(-IX, -IZ, CWX[0], IZ); lobby = INNER.difference(cafe).difference(LOFT_HALL)
    boards(p, cafe, along='x'); checker(p, lobby, -0.016, 0.0)
    ext_y(p, 'tile_h', LOFT_HALL.difference(SHAFT), -0.02, 0.0)
    return p

# ============================================================================ nucleo: hall, poco do elevador e caixa da escada (pivo: origem, y = piso)
def core(kind):
    """Paredes do nucleo em um pavimento: hall (oeste e frente), frente do poco com o vao do elevador, parede da escada com a porta.
    kind: 'g' (terreo: passagem livre para a portaria), 't' (tipo: porta do loft)."""
    p = Piece(); h = (GH if kind == 'g' else H) - ST; DH = 2.1
    wall_grid(p, 'z', -IZ, HFZ[0], HWX[0], HWX[1], [], 0.0, h, 'plaster')
    wall_grid(p, 'x', HWX[1], SWX[0], SHZ[0], SHZ[1], [(EDX - 0.45, EDX + 0.45, 0.0, DH)], 0.0, h, 'plaster')
    wall_grid(p, 'z', -IZ, HFZ[0], SWX[0], SWX[1], [(SDZ[0], SDZ[1], 0.0, DH)], 0.0, h, 'plaster')
    lw = (LDX[0], LDX[1], 0.0, 2.4 if kind == 'g' else DH)
    wall_grid(p, 'x', HWX[0], IX, HFZ[0], HFZ[1], [lw], 0.0, h, 'plaster')
    # batentes e guarnicoes
    q = Piece(); door_casing(q, SDZ[1] - SDZ[0], SWX[1] - SWX[0], DH); p.merge(q, rot_y(-90, ((SWX[0] + SWX[1]) / 2, 0, (SDZ[0] + SDZ[1]) / 2)))
    q = Piece(); door_casing(q, LDX[1] - LDX[0], HFZ[1] - HFZ[0], lw[3]); p.merge(q, tr((LDX[0] + LDX[1]) / 2, 0, (HFZ[0] + HFZ[1]) / 2))
    # rodapes do hall
    for (a, b) in ((SHZ[1], HFZ[0]),): p.box('dkwood', HWX[1], HWX[1] + 0.015, 0.0, 0.1, a, b)
    for (a, b) in segs_excl([(SDZ[0] - 0.09, SDZ[1] + 0.09)], SHZ[1], HFZ[0]): p.box('dkwood', SWX[0] - 0.015, SWX[0], 0.0, 0.1, a, b)
    for (a, b) in segs_excl([(LDX[0] - 0.09, LDX[1] + 0.09)], HWX[1], SWX[0]): p.box('dkwood', a, b, 0.0, 0.1, HFZ[0] - 0.015, HFZ[0])
    for (a, b) in segs_excl([(EDX - 0.6, EDX + 0.6)], HWX[1] + 0.015, SWX[0] - 0.015): p.box('dkwood', a, b, 0.0, 0.1, SHZ[1], SHZ[1] + 0.015)
    # luminaria do hall e da escada, extintor
    for (x, z) in ((EDX, -2.4), (8.3, -1.4)):
        p.cyl('metal', 0.18, h - 0.06, h - 0.002, x, z, 16); p.cyl('lamp_glass', 0.15, h - 0.075, h - 0.06, x, z, 16)
    p.cham('paint_r', HWX[1] + 0.03, HWX[1] + 0.2, 0.25, 0.75, -3.0, -2.84, 0.02) if False else None
    p.cyl('paint_r', 0.08, 0.3, 0.8, HWX[1] + 0.12, -3.2, 12); p.box('steel_d', HWX[1] + 0.005, HWX[1] + 0.05, 0.6, 0.66, -3.24, -3.16)
    return p

# ============================================================================ escada em U (lances em Z)
def flight_z(p, x0, x1, zs, d, y0, nr, rr):
    """Lance de nr espelhos que sobe para d (+1/-1 em Z) a partir de zs, y0: degraus macicos com bocel de aco e laje inclinada."""
    for i in range(1, nr):
        a, b = sorted((zs + d * (i - 1) * TRD, zs + d * i * TRD)); y = y0 + i * rr
        p.box('conc_s', x0 + 0.003, x1 - 0.003, y - 0.42, y, a, b)
        e = zs + d * (i - 1) * TRD; a2, b2 = sorted((e - d * 0.003, e + d * 0.045)); p.box('steel', x0 + 0.02, x1 - 0.02, y - 0.006, y + 0.003, a2, b2)
    ze = zs + d * (nr - 1) * TRD
    p.hull('concrete', [(x, y0 + (z - zs) * d / TRD * rr + dd, z) for z in (zs + d * 0.003, ze - d * 0.003) for x in (x0 + 0.006, x1 - 0.006) for dd in (-0.3, -0.45)])
def rail_z(p, x, zs, d, y0, nr, rr):
    ze = zs + d * (nr - 1) * TRD
    for i in range(1, nr):
        z = zs + d * (i - 0.5) * TRD; y = y0 + i * rr; p.box('steel_d', x - 0.012, x + 0.012, y, y + 0.92, z - 0.012, z + 0.012)
    seg_cyl(p, 'steel_d', (x, y0 + 0.92 + rr * 0.5, zs), (x, y0 + (nr - 1) * rr + 0.92 + rr * 0.5, ze), 0.022, 8)
def stair(kind):
    """Um pavimento da escada: lance A (junto a parede leste, sobe para -Z), patamar intermediario, lance B (sobe para +Z),
    corrimaos de tubo e guarda-corpo central (pivo: origem, y = piso). kind: 'g', '1' (com o pedaco de patamar sobre o lance
    do terreo) ou 't'."""
    p = Piece(); g = kind == 'g'; nr = NRG if g else NRT; hh = GH if g else H; rr = hh / (2 * nr); zs = ZG if g else ZT
    p.box('conc_s', LB[0], LA[1], hh / 2 - 0.22, hh / 2, -IZ, MZ)
    flight_z(p, LA[0], LA[1], zs, -1, 0.0, nr, rr); flight_z(p, LB[0], LB[1], MZ, 1, hh / 2, nr, rr)
    rail_z(p, LA[0] + 0.03, zs, -1, 0.0, nr, rr); rail_z(p, LB[1] - 0.03, MZ, 1, hh / 2, nr, rr)
    for x in (LA[0] + 0.03, LB[1] - 0.03): p.box('steel_d', x - 0.015, x + 0.015, hh / 2, hh / 2 + 1.0, MZ - 0.05, MZ - 0.02)
    p.box('steel_d', LB[1] - 0.045, LA[0] + 0.045, hh / 2 + 0.96, hh / 2 + 1.0, MZ - 0.05, MZ - 0.02)
    # corrimao de parede (lance A, parede leste) com suportes
    xw = IX - 0.07
    seg_cyl(p, 'steel_d', (xw, 0.9 + rr, zs), (xw, 0.9 + (nr - 1) * rr + rr, MZ), 0.02, 8)
    for i in (2, nr - 2):
        z = zs - i * TRD; y = 0.9 + i * rr + rr * 0.5; p.box('steel_d', xw, IX - 0.003, y - 0.015, y + 0.015, z - 0.015, z + 0.015)
    if kind == '1': p.box('conc_s', LA[0] - 0.05, LA[1], -ST, 0.0, ZT, ZG); p.box('tile_h', LA[0] - 0.05, LA[1], -0.001, 0.0005, ZT + 0.003, ZG) if False else None
    return p
def stair_door():
    return door_metal(0.88, 2.07)

# ============================================================================ estrutura interna e portas
def post_t():
    """Pilar de madeira de 26 cm com chanfro, sapata e capitel de aco (pivo: centro, piso)."""
    p = Piece(); h = H - ST - GD
    p.cham('timber', -0.13, 0.13, 0.012, h - 0.005, -0.13, 0.13, 0.02)
    p.box('steel_d', -0.16, 0.16, 0.0, 0.012, -0.16, 0.16)
    p.box('steel_d', -0.16, 0.16, h - 0.1, h, -0.137, -0.13); p.box('steel_d', -0.16, 0.16, h - 0.1, h, 0.13, 0.137)
    p.box('steel_d', -0.16, 0.16, h - 0.012, h, -0.13, 0.13)
    for s in (-1, 1):
        for z in (-0.06, 0.06): p.box('steel', z - 0.02, z + 0.02, h - 0.07, h - 0.03, *sorted((0.137 * s, 0.144 * s)))
    return p
def post_g():
    """Coluna de ferro fundido do terreo: base moldada, fuste com entase e capitel com abaco (pivo: centro, piso)."""
    p = Piece(); h = GH - ST - GD
    lathe(p, 'cast', [(0.2, 0.0), (0.2, 0.08), (0.16, 0.12), (0.14, 0.3), (0.125, h - 0.5), (0.11, h - 0.36), (0.16, h - 0.2), (0.2, h - 0.12)], sec=20)
    p.box('cast', -0.22, 0.22, h - 0.12, h, -0.22, 0.22)
    for y in (0.24, h - 0.42): ring_y(p, 'cast', 0.125, 0.15, y, y + 0.04, 0, 0, 20)
    return p
def door_plank(w=0.88, h=2.07, t=0.05):
    """Porta de tabuas com friso em V, travessas de aco, macaneta de alavanca (porta do loft; pivo: dobradica, embaixo)."""
    p = Piece(); n = 6; b = w / n
    for i in range(n): p.cham('door', i * b + 0.002, (i + 1) * b - 0.002, 0.0, h, -t / 2, t / 2, 0.006)
    for y in (0.35, h - 0.35):
        for z in (1, -1): p.box('steel_d', 0.02, w - 0.02, y - 0.04, y + 0.04, *sorted((z * t / 2, z * (t / 2 + 0.008))))
    for z in (1, -1):
        p.box('steel_d', w - 0.1, w - 0.06, 0.9, 1.1, *sorted((z * t / 2, z * (t / 2 + 0.01))))
        seg_cyl(p, 'steel_d', (w - 0.08, 1.04, z * (t / 2 + 0.01)), (w - 0.08, 1.04, z * (t / 2 + 0.05)), 0.009, 6)
        seg_cyl(p, 'steel_d', (w - 0.08, 1.04, z * (t / 2 + 0.05)), (w - 0.2, 1.04, z * (t / 2 + 0.05)), 0.01, 6)
    return p
def door_shop(w=0.99, h=2.4, t=0.05):
    """Porta da loja: quadro de madeira pintada com vidro grande, chapa de chute, puxador de latao (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.1; m = 'shop_g'
    p.cham(m, 0, s, 0, h, -t / 2, t / 2, 0.006); p.cham(m, w - s, w, 0, h, -t / 2, t / 2, 0.006)
    p.cham(m, s - 0.002, w - s + 0.002, 0, 0.32, -t / 2, t / 2, 0.006); p.cham(m, s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.006)
    p.box('glass', s - 0.004, w - s + 0.004, 0.316, h - s + 0.004, -0.003, 0.003)
    for z in (1, -1):
        p.box('brass', 0.04, w - 0.04, 0.03, 0.26, *sorted((z * t / 2, z * (t / 2 + 0.003))))
        seg_cyl(p, 'brass', (w - 0.1, 0.8, z * (t / 2 + 0.05)), (w - 0.1, 1.4, z * (t / 2 + 0.05)), 0.016, 8)
        for y in (0.85, 1.35): seg_cyl(p, 'brass', (w - 0.1, y, z * t / 2), (w - 0.1, y, z * (t / 2 + 0.05)), 0.01, 6)
    return p
def door_fe(w=0.88, h=2.08, t=0.045):
    """Porta de aco envidracada da saida para a escada de incendio (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.06; m = 'win_k'
    p.box(m, 0, s, 0, h, -t / 2, t / 2); p.box(m, w - s, w, 0, h, -t / 2, t / 2); p.box(m, s, w - s, 0, 0.35, -t / 2, t / 2); p.box(m, s, w - s, h - s, h, -t / 2, t / 2)
    lite_grid(p, s, w - s, 0.35, h - s, 2, 4, z=(-0.015, 0.015), gz=(-0.002, 0.002), bw=0.012)
    p.box('steel', 0.1, w - 0.1, 1.0, 1.05, -t / 2 - 0.05, -t / 2 - 0.01); p.box('steel', w - 0.14, w - 0.08, 0.98, 1.06, t / 2, t / 2 + 0.04)
    return p

# ============================================================================ loft: cozinha e jantar
def kitchen():
    """Cozinha de parede (pivo: face interna da parede dos fundos, x do mundo, piso; para +Z): geladeira, armarios com
    tampo de concreto, pia sob a janela, fogao com coifa no pilar e prateleiras abertas."""
    p = Piece(); d = 0.62; xa, xb = -8.7, -1.25
    p.cham('chrome', -9.5, -8.76, 0.0, 2.0, 0.003, 0.72, 0.01); p.box('dark', -9.49, -8.77, 1.195, 1.205, 0.718, 0.724)
    for (y0, y1) in ((0.2, 1.1), (1.3, 1.9)): seg_cyl(p, 'steel_d', (-8.84, y0, 0.76), (-8.84, y1, 0.76), 0.012, 6)
    for y in (0.2, 1.1, 1.3, 1.9): seg_cyl(p, 'steel_d', (-8.84, y, 0.72), (-8.84, y, 0.76), 0.008, 6)
    for (a, b) in segs_excl([(-6.38, -5.62)], xa, xb):
        p.box('dark', a + 0.02, b - 0.02, 0.0, 0.1, 0.003, d - 0.06); p.box('cab', a, b, 0.1, 0.88, 0.003, d - 0.02)
        n = max(1, int(round((b - a) / 0.6)))
        for i in range(n):
            u = a + (b - a) * i / n + 0.004; v = a + (b - a) * (i + 1) / n - 0.004
            p.cham('cab_g', u, v, 0.11, 0.7, d - 0.02, d, 0.004); p.cham('cab_g', u, v, 0.71, 0.87, d - 0.02, d, 0.004)
            p.box('brass', (u + v) / 2 - 0.08, (u + v) / 2 + 0.08, 0.78, 0.8, d, d + 0.02)
        p.box('stone', a - 0.01, b + 0.01, 0.88, 0.92, 0.003, d + 0.03)
    p.box('dark', -5.0, -4.0, 0.84, 0.921, 0.1, 0.5)
    seg_cyl(p, 'chrome', (-4.5, 0.92, 0.12), (-4.5, 1.25, 0.12), 0.015, 8); seg_cyl(p, 'chrome', (-4.5, 1.25, 0.12), (-4.5, 1.2, 0.32), 0.013, 8)
    p.cham('chrome', -6.38, -5.62, 0.0, 0.9, 0.003, 0.64, 0.008); p.box('dark', -6.3, -5.7, 0.15, 0.62, 0.64, 0.645)
    p.box('chrome', -6.25, -5.75, 0.68, 0.7, 0.645, 0.69)
    for (x, z) in ((-6.18, 0.15), (-5.82, 0.15), (-6.18, 0.45), (-5.82, 0.45)): ring_y(p, 'iron', 0.06, 0.09, 0.9, 0.93, x, z, 16)
    p.box('steel_d', -6.38, -5.62, 0.9, 1.0, 0.006, 0.08)
    p.hull('chrome', [(x, y, z) for x in (-6.4, -5.6) for (y, z) in ((1.65, 0.003), (1.65, 0.55), (1.75, 0.55), (2.0, 0.003))])
    p.box('chrome', -6.15, -5.85, 1.95, H - ST - JD, 0.003, 0.25)
    for y in (1.3, 1.7, 2.1):
        p.box('timber', -3.38, -2.62, y, y + 0.04, 0.003, 0.3)
        for i, x in enumerate((-3.28, -3.08, -2.88, -2.7)): p.cyl(['porcelain', 'glass', 'pot', 'food_y'][(i + int(y * 10)) % 4], 0.05, y + 0.04, y + 0.2, x, 0.15, 12)
        for x in (-3.3, -2.7): p.box('steel_d', x - 0.01, x + 0.01, y - 0.12, y, 0.003, 0.28)
    p.cham('timber', -7.6, -7.2, 0.92, 0.95, 0.15, 0.45, 0.01); p.cyl('steel', 0.09, 0.92, 1.08, -8.2, 0.3, 14); p.cyl('food_r', 0.12, 0.92, 0.98, -2.0, 0.3, 14)
    return p
def island(L1=2.4):
    """Ilha com tampo de madeira macica, armarios e 3 banquetas do lado +Z (pivo: centro, piso)."""
    p = Piece(); x = L1 / 2
    p.box('dark', -x + 0.05, x - 0.05, 0.0, 0.1, -0.4, 0.3); p.box('cab_g', -x + 0.02, x - 0.02, 0.1, 0.88, -0.42, 0.32)
    for i in range(4):
        u = -x + 0.02 + i * (L1 - 0.04) / 4 + 0.004; v = -x + 0.02 + (i + 1) * (L1 - 0.04) / 4 - 0.004
        p.cham('cab_g', u, v, 0.12, 0.86, -0.44, -0.42, 0.004); p.box('brass', (u + v) / 2 - 0.06, (u + v) / 2 + 0.06, 0.78, 0.8, -0.46, -0.44)
    p.cham('timber', -x, x, 0.88, 0.94, -0.47, 0.5, 0.008)
    for i in (-1, 0, 1): p.merge(stool(), tr(i * 0.75, 0.0, 0.75))
    return p
def chair_w(mat='timber'):
    """Cadeira de madeira com encosto de ripas (pivo: centro, piso; encosto em -Z)."""
    p = Piece()
    for (x, z) in ((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)): p.box(mat, x - 0.018, x + 0.018, 0.0, 0.44, z - 0.018, z + 0.018)
    p.cham(mat, -0.23, 0.23, 0.44, 0.475, -0.23, 0.23, 0.01)
    for x in (-0.2, 0.2): p.box(mat, x - 0.018, x + 0.018, 0.475, 0.92, -0.23, -0.194)
    for y in (0.62, 0.74, 0.86): p.box(mat, -0.182, 0.182, y, y + 0.06, -0.225, -0.2)
    return p
def dining(L1=2.0, n=3):
    """Mesa de jantar de tabuas com pes de aco em grampo e 6 cadeiras (pivo: centro, piso)."""
    p = Piece(); x = L1 / 2
    p.cham('timber', -x, x, 0.72, 0.77, -0.45, 0.45, 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            b = (sx * (x - 0.2), 0.0, sz * 0.36)
            seg_cyl(p, 'steel_d', (sx * (x - 0.12), 0.72, sz * 0.33), b, 0.009, 6); seg_cyl(p, 'steel_d', (sx * (x - 0.12), 0.72, sz * 0.27), b, 0.009, 6)
    for i in range(n):
        xc = -x + (i + 0.5) * L1 / n
        p.merge(chair_w(), rot_y(180, (xc, 0, -0.72))); p.merge(chair_w(), tr(xc, 0, 0.72))
    for xc in (-0.5, 0.4): p.cyl('porcelain', 0.12, 0.77, 0.79, xc, 0.0, 16)
    p.cyl('glass', 0.07, 0.77, 1.0, 0.0, 0.05, 14); p.sphere('plant', 0.12, 0.0, 1.06, 0.05, 1)
    return p
def pendant(drop=0.9, r=0.22, mat='steel_d'):
    """Pendente industrial de cupula de aco (pivo: ponto de fixacao no teto)."""
    p = Piece(); p.cyl('steel_d', 0.05, -0.02, 0.0, 0, 0, 10); seg_cyl(p, 'dark', (0, -0.02, 0), (0, -drop + 0.1, 0), 0.005, 4)
    lathe(p, mat, [(0.03, -drop + 0.12), (0.05, -drop + 0.08), (r * 0.6, -drop - 0.02), (r, -drop - 0.12), (r, -drop - 0.13)], sec=20)
    p.sphere('lamp_glass', 0.06, 0, -drop - 0.08, 0, 1)
    return p

# ============================================================================ loft: sala, quarto, escritorio, banheiro
def sofa_l(mat='fabric'):
    """Sofa em L (pivo: centro de tras do braco longo, piso; assento para +Z; chaise para +X)."""
    p = Piece(); L1 = 2.8; x = L1 / 2; dd = 0.95
    p.box('dark', -x + 0.05, x - 0.05, 0.0, 0.08, 0.05, dd - 0.05); p.box('dark', x - dd + 0.05, x - 0.05, 0.0, 0.08, dd - 0.05, 1.85)
    p.cham(mat, -x, x, 0.08, 0.42, 0.0, dd, 0.04); p.cham(mat, x - dd, x, 0.08, 0.42, dd - 0.001, 1.9, 0.04)
    p.cham(mat, -x, x, 0.42, 0.85, 0.0, 0.22, 0.04); p.cham(mat, -x, -x + 0.2, 0.42, 0.65, 0.22, dd, 0.04)
    for i in range(3):
        a = -x + 0.2 + i * 0.62 + 0.01; p.cham(mat, a, a + 0.6, 0.42, 0.53, 0.22, dd, 0.05); p.cham(mat, a, a + 0.6, 0.53, 0.83, 0.22, 0.36, 0.05)
    p.cham(mat, x - dd + 0.01, x - 0.01, 0.42, 0.53, 0.22, 1.88, 0.05); p.cham(mat, x - 0.2, x, 0.42, 0.65, dd, 1.9, 0.04)
    for (a, c) in ((-1.0, 0.45), (0.3, 0.42)): p.hull('cloth_y', [(a + dx, 0.53 + dy, c + dz) for dx in (0, 0.4) for dy in (0, 0.38) for dz in (0, 0.12)])
    return p
def coffee_table():
    p = Piece(); p.cham('timber', -0.65, 0.65, 0.36, 0.42, -0.35, 0.35, 0.01)
    for sx in (-1, 1):
        p.box('steel_d', sx * 0.6 - 0.02, sx * 0.6 + 0.02, 0.0, 0.36, -0.32, -0.28); p.box('steel_d', sx * 0.6 - 0.02, sx * 0.6 + 0.02, 0.0, 0.36, 0.28, 0.32)
        p.box('steel_d', sx * 0.6 - 0.02, sx * 0.6 + 0.02, 0.0, 0.03, -0.28, 0.28)
    p.box('paper', -0.3, 0.05, 0.42, 0.45, -0.15, 0.12); p.cyl('porcelain', 0.05, 0.42, 0.52, 0.3, 0.05, 12)
    return p
def rug(w=3.2, d=2.4, mat='rug'):
    p = Piece(); p.box(mat, -w / 2, w / 2, 0.002, 0.01, -d / 2, d / 2)
    for zz in ((-d / 2 + 0.12, -d / 2 + 0.2), (d / 2 - 0.2, d / 2 - 0.12)): p.box('cream', -w / 2 + 0.12, w / 2 - 0.12, 0.01, 0.0115, *zz)
    return p
def armchair(mat='leather'):
    """Poltrona de couro com bracos (pivo: centro, piso; encosto em -Z)."""
    p = Piece(); p.box('dark', -0.38, 0.38, 0.0, 0.1, -0.38, 0.38)
    p.cham(mat, -0.42, 0.42, 0.1, 0.42, -0.42, 0.42, 0.04); p.cham(mat, -0.42, 0.42, 0.42, 0.92, -0.42, -0.22, 0.05)
    for s in (-1, 1): p.cham(mat, *sorted((s * 0.42, s * 0.28)), 0.42, 0.66, -0.22, 0.42, 0.05)
    p.cham(mat, -0.28, 0.28, 0.42, 0.52, -0.22, 0.4, 0.05); return p
def floor_lamp():
    """Luminaria de arco com base de marmore (pivo: base; arco para +Z)."""
    p = Piece(); p.cham('marble', -0.18, 0.18, 0.0, 0.08, -0.18, 0.18, 0.01)
    pts = [(0.0, 0.08 + 1.9 * math.sin(a), 1.4 * (1 - math.cos(a))) for a in np.linspace(0, math.pi / 2 + 0.25, 9)]
    for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', a, b, 0.012, 6)
    e = pts[-1]; lathe(p, 'chrome', [(0.02, e[1] - 0.02), (0.18, e[1] - 0.2), (0.18, e[1] - 0.21)], x=0.0, z=e[2], sec=18); p.sphere('lamp_glass', 0.05, 0, e[1] - 0.15, e[2], 1)
    return p
def tv_unit():
    """Movel baixo de madeira com tela plana (pivo: centro de tras, piso; tela para +Z)."""
    p = Piece(); p.cham('timber', -0.9, 0.9, 0.12, 0.55, 0.0, 0.42, 0.01)
    for x in (-0.85, 0.85): p.box('steel_d', x - 0.02, x + 0.02, 0.0, 0.12, 0.04, 0.38)
    for i in range(3): u = -0.88 + i * 0.59; p.box('dkwood', u + 0.01, u + 0.57, 0.15, 0.52, 0.42, 0.43)
    p.box('dark', -0.06, 0.06, 0.55, 0.62, 0.1, 0.3); p.box('dark', -0.02, 0.02, 0.62, 0.8, 0.18, 0.22)
    p.cham('dark', -0.65, 0.65, 0.78, 1.52, 0.17, 0.21, 0.006); p.box('screen', -0.62, 0.62, 0.81, 1.49, 0.21, 0.214)
    return p
def bed(mat='bed_b'):
    """Cama de casal (pivo: centro da cabeceira, piso; pes para +Z)."""
    p = Piece(); x = 0.82; Lb = 2.1
    p.cham('timber', -x, x, 0.12, 0.32, 0.06, Lb, 0.01)
    for (a, c) in ((-x + 0.05, 0.12), (x - 0.05, 0.12), (-x + 0.05, Lb - 0.06), (x - 0.05, Lb - 0.06)): p.box('timber', a - 0.04, a + 0.04, 0.0, 0.12, c - 0.04, c + 0.04)
    p.cham('bed_w', -x + 0.03, x - 0.03, 0.32, 0.52, 0.09, Lb - 0.03, 0.04)
    p.cham(mat, -x, x, 0.44, 0.56, 0.7, Lb - 0.01, 0.04); p.cham(mat, -x + 0.02, x - 0.02, 0.33, 0.48, Lb - 0.03, Lb + 0.02, 0.02)
    for s in (-1, 1): p.cham(mat, *sorted((s * x, s * (x + 0.03))), 0.3, 0.55, 0.72, Lb, 0.01)
    for s in (-1, 1): p.cham('bed_w', s * 0.38 - 0.3, s * 0.38 + 0.3, 0.52, 0.66, 0.15, 0.55, 0.05)
    p.cham('fabric2', -x - 0.06, x + 0.06, 0.12, 1.2, 0.0, 0.08, 0.03)
    return p
def nightstand():
    p = Piece(); p.cham('timber', -0.24, 0.24, 0.0, 0.55, 0.0, 0.4, 0.008); p.box('dkwood', -0.2, 0.2, 0.3, 0.5, 0.4, 0.41)
    p.box('brass', -0.05, 0.05, 0.39, 0.41, 0.41, 0.43)
    lathe(p, 'pot', [(0.07, 0.55), (0.09, 0.62), (0.05, 0.75)], x=0.05, z=0.2, sec=14); seg_cyl(p, 'brass', (0.05, 0.75, 0.2), (0.05, 0.86, 0.2), 0.008, 6)
    lathe(p, 'lattice', [(0.13, 0.82), (0.09, 1.0), (0.0, 1.0)], x=0.05, z=0.2, sec=16)
    return p
def wardrobe():
    """Arara de roupas de tubo de aco com prateleira, roupas e sapatos (pivo: centro, piso)."""
    p = Piece(); x = 0.75
    for s in (-1, 1):
        seg_cyl(p, 'steel_d', (s * x, 0.0, -0.25), (s * x, 1.8, 0.0), 0.014, 6); seg_cyl(p, 'steel_d', (s * x, 0.0, 0.25), (s * x, 1.8, 0.0), 0.014, 6)
    seg_cyl(p, 'steel_d', (-x, 1.8, 0.0), (x, 1.8, 0.0), 0.014, 8); p.box('timber', -x + 0.02, x - 0.02, 0.25, 0.28, -0.2, 0.2)
    cols = ['cloth_r', 'cloth_b', 'bed_w', 'fabric2', 'cloth_y', 'dark', 'cloth_b', 'fabric3', 'bed_w']
    for i, xx in enumerate(np.linspace(-x + 0.12, x - 0.12, len(cols))):
        y0 = 0.85 + (i % 3) * 0.12; p.hull(cols[i], [(xx + dx, y, z) for dx in (-0.03, 0.03) for (y, z) in ((1.76, -0.05), (1.76, 0.05), (y0, -0.24), (y0, 0.24))])
        seg_cyl(p, 'chrome', (xx, 1.76, 0.0), (xx, 1.8, 0.0), 0.004, 4)
    for i, xx in enumerate((-0.5, -0.2, 0.15, 0.45)): p.cham(['leather', 'dark', 'cloth_b', 'fabric3'][i], xx - 0.12, xx + 0.12, 0.28, 0.4, -0.14, 0.14, 0.02)
    return p
def partition():
    """Divisoria de aco e vidro do quarto (pivo: origem do loft, piso): trecho em z = 3 com vao de passagem e trecho em x = -3."""
    p = Piece(); h = H - ST - GD; zc = PZ[1]; m = 'win_k'; t = 0.03
    def run(Ln):
        q = Piece(); n = max(2, int(round(Ln / 0.9)))
        q.box(m, 0.0, Ln, 0.003, 0.08, -t, t); q.box(m, 0.0, Ln, h - 0.06, h, -t, t); q.box(m, 0.0, 0.05, 0.08, h - 0.06, -t, t); q.box(m, Ln - 0.05, Ln, 0.08, h - 0.06, -t, t)
        lite_grid(q, 0.05, Ln - 0.05, 0.08, h - 0.06, n, 4, z=(-t + 0.004, t - 0.004), gz=(-0.003, 0.003), bw=0.014)
        return q
    for (a, b) in ((-IX, -5.2), (-4.2, -3.0 - t)): p.merge(run(b - a), tr(a, 0, zc))
    p.merge(run(IZ - zc + t), rot_y(-90, (-3.0, 0, zc - t)))
    return p
def desk():
    """Escrivaninha de tampo de madeira e cavaletes de aco com monitor, luminaria e livros (pivo: centro de tras, piso; para +Z)."""
    p = Piece(); x = 0.7
    p.cham('timber', -x, x, 0.72, 0.76, 0.0, 0.7, 0.008)
    for s in (-1, 1):
        for (z0, z1) in ((0.05, 0.08), (0.62, 0.65)): p.box('steel_d', s * (x - 0.08) - 0.015, s * (x - 0.08) + 0.015, 0.0, 0.72, z0, z1)
        p.box('steel_d', s * (x - 0.08) - 0.015, s * (x - 0.08) + 0.015, 0.0, 0.03, 0.08, 0.62)
    p.box('dark', -0.1, 0.1, 0.76, 0.78, 0.12, 0.28); p.box('dark', -0.02, 0.02, 0.78, 0.95, 0.18, 0.22)
    p.cham('dark', -0.32, 0.32, 0.92, 1.28, 0.2, 0.23, 0.005); p.box('screen', -0.3, 0.3, 0.94, 1.26, 0.23, 0.233)
    p.box('dark', -0.22, 0.22, 0.76, 0.775, 0.38, 0.52)
    seg_cyl(p, 'steel_d', (0.55, 0.76, 0.12), (0.5, 1.15, 0.2), 0.008, 6); seg_cyl(p, 'steel_d', (0.5, 1.15, 0.2), (0.4, 1.12, 0.38), 0.008, 6)
    lathe(p, 'paint_y', [(0.02, 1.15), (0.08, 1.05), (0.08, 1.04)], x=0.4, z=0.38, sec=14)
    for i, c in enumerate(['cloth_r', 'cloth_b', 'paper', 'paint_g']): p.box(c, -0.66 + i * 0.045, -0.62 + i * 0.045, 0.76, 0.98, 0.08, 0.28)
    return p
def bookcase(L1=2.4, h=2.2):
    """Estante alta de aco e madeira com livros e vasos (pivo: centro de tras, piso; para +Z)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(21); d = 0.34; xs = np.linspace(-x, x, 4)
    for xx in xs: p.box('steel_d', xx - 0.015, xx + 0.015, 0.0, h, 0.0, d)
    for y in np.linspace(0.08, h - 0.04, 6):
        p.box('timber', -x + 0.015, x - 0.015, y, y + 0.03, 0.004, d - 0.004)
        if y > h - 0.2: continue
        for (a, b) in zip(xs[:-1], xs[1:]):
            xx = a + 0.04
            while xx < b - 0.12:
                w = rng.uniform(0.025, 0.05); hh = rng.uniform(0.2, 0.32); c = ['cloth_r', 'cloth_b', 'paper', 'paint_g', 'dkwood', 'cloth_y', 'dark'][int(rng.integers(7))]
                if rng.random() < 0.08: p.cyl('pot', 0.06, y + 0.03, y + 0.2, xx + 0.06, 0.17, 12); xx += 0.16; continue
                p.box(c, xx, xx + w, y + 0.03, y + 0.03 + hh, 0.04, 0.3); xx += w + 0.003
    return p
def bathroom():
    """Banheiro do loft em caixa aberta no alto (pivo: origem do loft, piso): paredes de 2,3 m com azulejo por dentro,
    chuveiro com box de vidro, vaso, bancada de madeira com cuba, espelho, toalheiro."""
    p = Piece(); h = 2.3; DH = 2.05
    wall_grid(p, 'z', -IZ, BWZ[1], BWX[0], BWX[1], [], 0.0, h, 'plaster')
    wall_grid(p, 'x', BWX[1], HWX[0], BWZ[0], BWZ[1], [(BDX[0], BDX[1], 0.0, DH)], 0.0, h, 'plaster')
    q = Piece(); door_casing(q, BDX[1] - BDX[0], BWZ[1] - BWZ[0], DH); p.merge(q, tr((BDX[0] + BDX[1]) / 2, 0, (BWZ[0] + BWZ[1]) / 2))
    p.box('timber', BWX[0] - 0.012, BWX[1] + 0.012, h, h + 0.03, -IZ, BWZ[1] + 0.012)
    p.box('timber', BWX[1] + 0.012, HWX[0], h, h + 0.03, BWZ[0] - 0.012, BWZ[1] + 0.012)
    p.box('tile_a', BWX[1], BWX[1] + 0.01, 0.0, 2.1, -IZ + 0.01, BWZ[0])
    for (a, b) in segs_excl([(BDX[0] - 0.09, BDX[1] + 0.09)], BWX[1] + 0.01, HWX[0] - 0.01): p.box('tile_a', a, b, 0.0, 2.1, BWZ[0] - 0.01, BWZ[0])
    p.box('tile_a', HWX[0] - 0.01, HWX[0], 0.0, 2.1, -IZ + 0.01, BWZ[0] - 0.01); p.box('tile_a', BWX[1], HWX[0], 0.0, 2.1, -IZ, -IZ + 0.01)
    p.box('tile_a', BWX[1] + 0.01, HWX[0] - 0.01, 0.0, 0.05, -IZ + 0.01, -5.6); p.box('dark', 3.68, 3.76, 0.05, 0.052, -6.1, -6.02)
    p.box('glass', BWX[1] + 0.01, 3.9, 0.05, 1.99, -5.61, -5.6); p.box('chrome', BWX[1] + 0.01, 3.9, 1.98, 2.0, -5.616, -5.594)
    seg_cyl(p, 'chrome', (3.72, 1.0, -IZ + 0.03), (3.72, 2.0, -IZ + 0.03), 0.012, 6)
    seg_cyl(p, 'chrome', (3.72, 2.0, -IZ + 0.03), (3.72, 2.0, -6.25), 0.012, 6); p.cyl('chrome', 0.1, 1.97, 1.99, 3.72, -6.25, 16)
    p.merge(wc(), rot_y(-90, (BWX[1] + 0.013, 0, -4.9)))
    p.cham('timber', HWX[0] - 0.5, HWX[0] - 0.01, 0.82, 0.87, -4.6, -3.75, 0.006); p.cyl('porcelain', 0.18, 0.87, 0.98, HWX[0] - 0.27, -4.17, 18)
    seg_cyl(p, 'chrome', (HWX[0] - 0.05, 0.87, -4.17), (HWX[0] - 0.05, 1.1, -4.17), 0.012, 6); seg_cyl(p, 'chrome', (HWX[0] - 0.05, 1.1, -4.17), (HWX[0] - 0.17, 1.08, -4.17), 0.01, 6)
    for z in (-4.55, -3.8): p.box('steel_d', HWX[0] - 0.48, HWX[0] - 0.45, 0.0, 0.82, z - 0.015, z + 0.015)
    p.cham('steel_d', HWX[0] - 0.035, HWX[0] - 0.01, 1.15, 1.85, -4.5, -3.85, 0.004); p.box('mirror', HWX[0] - 0.04, HWX[0] - 0.035, 1.18, 1.82, -4.47, -3.88)
    seg_cyl(p, 'chrome', (BWX[1] + 0.06, 1.3, -4.0), (BWX[1] + 0.06, 1.3, -3.6), 0.01, 6); p.box('bed_w', BWX[1] + 0.04, BWX[1] + 0.08, 0.8, 1.32, -3.95, -3.65)
    return p
def coat_bench():
    """Banco de entrada com cabideiro de tubo e casacos (pivo: centro de tras, piso; para +Z)."""
    p = Piece(); p.cham('timber', -0.6, 0.6, 0.42, 0.46, 0.0, 0.38, 0.008)
    for x in (-0.55, 0.55): p.box('steel_d', x - 0.02, x + 0.02, 0.0, 1.85, 0.02, 0.06); p.box('steel_d', x - 0.02, x + 0.02, 0.0, 0.42, 0.32, 0.36)
    p.box('steel_d', -0.57, 0.57, 1.8, 1.84, 0.02, 0.06)
    for i, x in enumerate((-0.35, 0.0, 0.35)):
        seg_cyl(p, 'brass', (x, 1.7, 0.06), (x, 1.75, 0.14), 0.01, 6)
        p.hull(['cloth_b', 'leather', 'fabric3'][i], [(x + dx, y, z) for dx in (-0.16, 0.16) for (y, z) in ((1.72, 0.08), (1.72, 0.16), (0.95, 0.07), (0.95, 0.2))])
    p.cham('dark', -0.45, -0.15, 0.0, 0.1, 0.06, 0.32, 0.02); return p

# ============================================================================ cafe e portaria (terreo)
def cafe_counter():
    """Balcao do cafe (pivo: origem, piso; mundo): balcao de atendimento com frente de tabuas, tampo de marmore, vitrine de
    bolos, caixa; balcao dos fundos com maquina de espresso, moedor, xicaras e lousa com pictograma de xicara no pilar."""
    p = Piece(); z0, z1 = -5.05, -4.4; xa, xb = -8.6, -3.2
    p.box('dark', xa + 0.05, xb - 0.05, 0.0, 0.1, z0 + 0.03, z1 - 0.05); p.box('dkwood', xa, xb, 0.1, 1.0, z0, z1 - 0.02)
    for x in np.arange(xa, xb - 0.05, 0.12): p.box('timber', x + 0.004, min(x + 0.116, xb), 0.12, 0.98, z1 - 0.02, z1)
    p.box('marble', xa - 0.03, xb + 0.03, 1.0, 1.05, z0 - 0.03, z1 + 0.04)
    # vitrine de bolos
    vx = (-5.2, -3.4); p.box('chrome', vx[0], vx[1], 1.05, 1.09, z0 + 0.05, z1 - 0.02)
    p.box('glass', vx[0], vx[0] + 0.006, 1.09, 1.45, z0 + 0.05, z1 - 0.02); p.box('glass', vx[1] - 0.006, vx[1], 1.09, 1.45, z0 + 0.05, z1 - 0.02)
    p.hull('glass', [(x, y, z) for x in vx for (y, z) in ((1.09, z1 - 0.03), (1.09, z1 - 0.02), (1.45, z1 - 0.2), (1.45, z1 - 0.21))])
    p.box('glass', vx[0], vx[1], 1.45, 1.456, z0 + 0.05, z1 - 0.2); p.box('chrome', vx[0] + 0.02, vx[1] - 0.02, 1.25, 1.26, z0 + 0.07, z1 - 0.12)
    for i, x in enumerate(np.linspace(vx[0] + 0.2, vx[1] - 0.2, 5)):
        p.cyl('porcelain', 0.12, 1.09, 1.1, x, -4.75, 16); p.cyl(['cake', 'food_r', 'coffee', 'food_y', 'cake'][i], 0.1, 1.1, 1.18, x, -4.75, 16)
        p.cyl('porcelain', 0.1, 1.26, 1.27, x, -4.8, 14); p.sphere(['food_y', 'cake', 'food_r', 'coffee', 'cake'][i], 0.05, x, 1.3, -4.8, 1)
    p.merge(register(), rot_y(180, (-7.0, 1.05, -4.75)))
    # balcao dos fundos
    bz0, bz1 = -IZ, -5.95
    for (a, b) in segs_excl([(-2.1, -0.9)], -9.5, -2.6):
        p.box('dark', a + 0.03, b - 0.03, 0.0, 0.1, bz0 + 0.003, bz1 - 0.05); p.box('cab', a, b, 0.1, 0.88, bz0 + 0.003, bz1 - 0.02)
        for x in np.arange(a, b - 0.3, 0.6): p.cham('dkwood', x + 0.004, min(x + 0.596, b - 0.004), 0.12, 0.86, bz1 - 0.02, bz1, 0.004)
        p.box('stone', a - 0.01, b + 0.01, 0.88, 0.92, bz0 + 0.003, bz1 + 0.03)
    # maquina de espresso
    ex = -7.5; p.cham('chrome', ex - 0.4, ex + 0.4, 0.92, 1.38, -6.5, -6.0, 0.02); p.box('dark', ex - 0.36, ex + 0.36, 1.38, 1.4, -6.45, -6.05)
    for i in range(3): x = ex - 0.25 + i * 0.25; p.cyl('steel_d', 0.03, 1.08, 1.16, x, -5.96, 12); seg_cyl(p, 'dark', (x, 1.14, -5.96), (x, 1.14, -5.82), 0.01, 6); p.box('steel_d', x - 0.06, x + 0.06, 0.92, 0.94, -6.0, -5.9)
    for i in range(6): p.cyl('porcelain', 0.035, 1.4, 1.46, ex - 0.3 + i * 0.12, -6.25, 10)
    seg_cyl(p, 'chrome', (ex + 0.32, 1.2, -5.98), (ex + 0.34, 1.0, -5.9), 0.006, 6)
    p.cyl('dark', 0.08, 0.92, 1.0, -6.6, -6.3, 12); p.cyl('steel_d', 0.05, 1.0, 1.25, -6.6, -6.3, 12); lathe(p, 'glass', [(0.03, 1.25), (0.09, 1.32), (0.08, 1.48), (0.0, 1.5)], x=-6.6, z=-6.3, sec=12)
    # lousa no pilar entre as janelas
    p.box('dkwood', -6.38, -5.62, 1.3, 2.3, -IZ, -IZ + 0.03); p.box('chalk', -6.33, -5.67, 1.35, 2.25, -IZ + 0.03, -IZ + 0.035)
    q = Piece()
    q.box('cream', -0.18, 0.12, -0.12, 0.12, 0.0, 0.004); q.box('cream', 0.12, 0.2, 0.0, 0.06, 0.0, 0.004); q.box('cream', -0.24, 0.26, -0.18, -0.15, 0.0, 0.004)
    for x in (-0.1, 0.0, 0.08): q.box('cream', x - 0.012, x + 0.012, 0.16, 0.28, 0.0, 0.004)
    p.merge(q, tr(-6.0, 1.95, -IZ + 0.035))
    for y in (1.48, 1.58, 1.68): p.box('cream', -6.25, -5.75, y, y + 0.02, -IZ + 0.035, -IZ + 0.039)
    return p
def bistro(n=2, mat='bench_g'):
    """Mesa de bistro de tampo de marmore com pe de ferro fundido e cadeiras de ferro (pivo: centro, piso)."""
    p = Piece(); p.cyl('marble', 0.33, 0.72, 0.75, 0, 0, 24)
    lathe(p, 'cast', [(0.24, 0.0), (0.22, 0.03), (0.05, 0.08), (0.03, 0.4), (0.05, 0.68), (0.12, 0.72)], sec=16)
    for i in range(n):
        a = i * 2 * math.pi / n + math.pi / 2; q = Piece()
        for (x, z) in ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)): seg_cyl(q, 'cast', (x, 0.0, z), (x * 0.9, 0.45, z * 0.9), 0.012, 6)
        q.cyl(mat, 0.22, 0.45, 0.48, 0, 0, 18)
        for x in (-0.16, 0.16): seg_cyl(q, 'cast', (x, 0.48, -0.16), (x * 1.1, 0.86, -0.22), 0.01, 6)
        q.hull('cast', [(x, y, -0.22 + (y - 0.6) * -0.1) for x in (-0.18, 0.18) for y in (0.62, 0.86)] + [(x, y, -0.235 + (y - 0.6) * -0.1) for x in (-0.18, 0.18) for y in (0.62, 0.86)])
        p.merge(q, rot_y(math.degrees(-a) + 90, (0.6 * math.cos(a), 0, 0.6 * math.sin(a))))
    p.cyl('porcelain', 0.04, 0.75, 0.82, 0.08, 0.05, 12); p.cyl('coffee', 0.033, 0.8, 0.821, 0.08, 0.05, 12)
    return p
def banquette(L1=6.0):
    """Banco estofado corrido junto a parede (pivo: centro de tras, piso; assento para +Z)."""
    p = Piece(); x = L1 / 2
    p.box('dkwood', -x, x, 0.0, 0.45, 0.0, 0.55); p.cham('vinyl_g', -x, x, 0.45, 0.52, 0.0, 0.55, 0.02)
    for i in range(int(L1 / 0.6)):
        a = -x + i * 0.6 + 0.005; p.cham('vinyl_g', a, a + 0.59, 0.52, 0.88, 0.0, 0.14, 0.03)
    return p
def mailboxes():
    """Caixas de correio de latao (pivo: face da parede, centro, piso; para +Z)."""
    p = Piece(); p.cham('dkwood', -0.8, 0.8, 0.9, 1.9, 0.0, 0.08, 0.008)
    for i in range(4):
        for j in range(3):
            x0 = -0.76 + i * 0.38; y0 = 0.94 + j * 0.31
            p.box('brass', x0 + 0.01, x0 + 0.37, y0 + 0.01, y0 + 0.3, 0.08, 0.09); p.box('dark', x0 + 0.08, x0 + 0.3, y0 + 0.2, y0 + 0.22, 0.09, 0.093)
            p.box('gold', x0 + 0.3, x0 + 0.33, y0 + 0.06, y0 + 0.12, 0.09, 0.1)
    return p
def bike_rack(n=4):
    """Bicicletario de tubo em U chumbado no piso (pivo: centro, piso; ao longo de X)."""
    p = Piece()
    for i in range(n):
        x = (i - (n - 1) / 2) * 0.7; pts = [(x + 0.3 * math.cos(a), 0.55 + 0.25 * math.sin(a) if a > 0 else 0.55, 0.0) for a in np.linspace(0, math.pi, 7)]
        for a_, b_ in zip(pts[:-1], pts[1:]): seg_cyl(p, 'galv', a_, b_, 0.024, 8)
        for s in (-1, 1): seg_cyl(p, 'galv', (x + s * 0.3, 0.0, 0.0), (x + s * 0.3, 0.55, 0.0), 0.024, 8); p.cyl('galv', 0.05, 0.0, 0.01, x + s * 0.3, 0.0, 10)
    return p
def bicycle(mat='paint_b'):
    """Bicicleta (pivo: chao, centro; ao longo de X)."""
    p = Piece()
    for x in (-0.52, 0.52):
        m = trimesh.creation.annulus(r_min=0.3, r_max=0.34, height=0.04, sections=28); m.apply_translation([x, 0.34, 0]); p.add('rubber', m)
        for k in range(8): a = k * math.pi / 8; seg_cyl(p, 'chrome', (x - 0.3 * math.cos(a), 0.34 - 0.3 * math.sin(a), 0), (x + 0.3 * math.cos(a), 0.34 + 0.3 * math.sin(a), 0), 0.003, 3)
    for (a, b) in (((-0.52, 0.34), (-0.05, 0.34)), ((-0.05, 0.34), (-0.18, 0.85)), ((-0.18, 0.85), (0.38, 0.85)), ((0.38, 0.85), (-0.05, 0.34)), ((-0.52, 0.34), (-0.18, 0.85)), ((0.52, 0.34), (0.38, 0.85)), ((0.38, 0.85), (0.34, 1.0))):
        seg_cyl(p, mat, (a[0], a[1], 0), (b[0], b[1], 0), 0.018, 6)
    p.cham('dark', -0.3, -0.06, 0.9, 0.94, -0.06, 0.06, 0.01); seg_cyl(p, 'chrome', (0.34, 1.0, -0.25), (0.34, 1.0, 0.25), 0.012, 6)
    disc_z(p, 'steel_d', 0.09, -0.05, -0.03, -0.05, 0.34, 16)
    return p

# ============================================================================ escada de incendio (pivo: face leste x = BX, y = piso do pavimento, z = 0)
DY = 0.2; PL = 3.6; HX0, HX1 = 0.8, FW - 0.06           # deck 20 cm acima do piso; faixa do lance (furo) em x local
NFE = 17; RFE = H / NFE; RUNF = 2.72; TFE = RUNF / (NFE - 1)
def fe_platform(hole=None, ladder_z=None):
    """Plataforma de grelha de aco: cantoneiras, barras de grelha, travessas, guarda-corpo com balaustres, guarda do furo do lance
    e maos-francesas para a parede. hole = (z0, z1) do furo na faixa externa."""
    p = Piece(); y = DY; m = 'iron'
    p.box(m, 0.02, 0.08, y - 0.12, y, -PL, PL); p.box(m, FW - 0.06, FW, y - 0.12, y, -PL, PL)
    for s in (-1, 1): p.box(m, 0.08, FW - 0.06, y - 0.12, y, *sorted((s * PL, s * (PL - 0.06))))
    for z in np.arange(-PL + 0.06, PL - 0.06, 0.05):
        zc = z + 0.025
        if hole and hole[0] - 0.03 < zc < hole[1] + 0.03: p.box(m, 0.08, HX0 - 0.03, y - 0.03, y, zc - 0.006, zc + 0.006)
        else: p.box(m, 0.08, FW - 0.06, y - 0.03, y, zc - 0.006, zc + 0.006)
    # chapa sob a grelha (da apoio continuo ao jogador)
    pl = sbox(0.08, -PL + 0.06, FW - 0.06, PL - 0.06)
    if hole: pl = pl.difference(sbox(HX0 - 0.03, hole[0] - 0.03, FW, hole[1] + 0.03))
    ext_y(p, m, pl, y - 0.04, y - 0.03)
    for z in (-2.4, -1.2, 0.0, 1.2, 2.4):
        if hole and hole[0] - 0.05 < z < hole[1] + 0.05: p.box(m, 0.08, HX0 - 0.03, y - 0.12, y - 0.031, z - 0.03, z + 0.03); continue
        p.box(m, 0.08, FW - 0.06, y - 0.12, y - 0.031, z - 0.03, z + 0.03)
    if hole:
        p.box(m, HX0 - 0.03, HX0, y - 0.12, y, hole[0] - 0.03, hole[1] + 0.03)
        for zz in (hole[0] - 0.03, hole[1]): p.box(m, HX0, FW - 0.06, y - 0.12, y, zz, zz + 0.03)
        # guarda do furo
        for zz in (hole[0] + 0.02, hole[1] - 0.02): p.box(m, HX0 - 0.025, HX0 - 0.005, y, y + 1.0, zz - 0.01, zz + 0.01)
        p.box(m, HX0 - 0.03, HX0, y + 0.97, y + 1.0, hole[0], hole[1]); p.box(m, HX0 - 0.025, HX0 - 0.005, y + 0.48, y + 0.5, hole[0] + 0.03, hole[1] - 0.03)
    # guarda-corpo
    for z in np.arange(-PL + 0.03, PL, 1.2): p.box(m, FW - 0.05, FW - 0.01, y, y + 1.05, z - 0.02, z + 0.02)
    p.box(m, FW - 0.05, FW - 0.01, y, y + 1.05, PL - 0.05, PL - 0.01)
    p.box(m, FW - 0.06, FW, y + 1.05, y + 1.09, -PL, PL); p.box(m, FW - 0.04, FW - 0.02, y + 0.12, y + 0.14, -PL + 0.05, PL - 0.05)
    for s in (-1, 1):
        zz = sorted((s * (PL - 0.04), s * (PL - 0.0))); p.box(m, 0.05, FW - 0.06, y + 1.05, y + 1.09, *zz); p.box(m, 0.05, FW - 0.05, y + 0.12, y + 0.14, *zz)
        p.box(m, 0.05, 0.09, y, y + 1.05, *zz)
        for x in np.arange(0.17, FW - 0.1, 0.12): p.box(m, x - 0.006, x + 0.006, y + 0.14, y + 1.05, *sorted((s * (PL - 0.026), s * (PL - 0.014))))
    for z in np.arange(-PL + 0.12, PL - 0.06, 0.12):
        if any(abs(z - zz) < 0.04 for zz in np.arange(-PL + 0.03, PL, 1.2)): continue
        p.box(m, FW - 0.036, FW - 0.024, y + 0.14, y + 1.05, z - 0.006, z + 0.006)
    # maos-francesas nos pilares (z = -3, 0, 3) com chapa na parede
    for z in (-3.0, 0.0, 3.0):
        p.box(m, 0.0, 0.012, y - 1.0, y - 0.1, z - 0.08, z + 0.08)
        p.hull(m, [(x, yy, z + dz) for (x, yy) in ((0.012, y - 0.95), (0.012, y - 0.85), (FW - 0.1, y - 0.12), (FW - 0.22, y - 0.12)) for dz in (-0.02, 0.02)])
        for yy in (y - 0.9, y - 0.2): p.cyl('steel', 0.02, 0.0, 0.0, 0, 0) if False else disc_x(p, 'steel', 0.018, 0.012, 0.03, yy, z, 8)
    if ladder_z is not None:                                          # guias da escada basculante
        for s in (-1, 1): p.box(m, FEL - BX + s * 0.22 - 0.02, FEL - BX + s * 0.22 + 0.02, y - 0.3, y, ladder_z - 0.06, ladder_z - 0.02)
    return p
def fe_stair():
    """Lance da escada de incendio (pivo: eixo da faixa, topo do deck de baixo; sobe para +Z): 2 banzos de chapa, degraus de
    grelha, corrimaos de tubo dos dois lados."""
    p = Piece(); m = 'iron'; w = 0.4; z0 = 0.2
    for s in (-1, 1):
        x = s * w
        p.hull(m, [(x + dx, yy, zz) for dx in (-0.006, 0.006) for (yy, zz) in ((0.0, z0 - 0.05), (0.0, z0 + 0.18), (H, z0 + RUNF + 0.05), (H - 0.2, z0 + RUNF + 0.05))])
    for i in range(1, NFE):
        y = i * RFE; z = z0 + (i - 1) * TFE + 0.01
        for k in range(4): zz = z + k * 0.045; p.box(m, -w + 0.006, w - 0.006, y - 0.025, y, zz, zz + 0.012)
        p.box(m, -w + 0.006, w - 0.006, y - 0.03, y - 0.025, z, z + 0.16)
    for s in (-1, 1):
        x = s * (w + 0.03)
        seg_cyl(p, m, (x, 0.95, z0 + 0.02), (x, H + 0.9, z0 + RUNF - 0.02), 0.02, 8)
        for (yy, zz) in ((0.0, z0 + 0.02), (H - 0.1, z0 + RUNF - 0.02)): p.box(m, x - 0.015, x + 0.015, yy, yy + 0.95 + (0.0 if yy == 0 else 0.9) - (0.9 if yy > 0 else 0.0), zz - 0.015, zz + 0.015)
        p.box(m, x - 0.035, x - 0.006 if s > 0 else x + 0.035, 0.6, 0.63, z0 + 0.4, z0 + 0.43) if False else None
    return p
def fe_ladder():
    """Escada basculante recolhida sob a plataforma do 1o andar (pivo: eixo, topo do deck): banzos, degraus redondos, contrapeso."""
    p = Piece(); m = 'iron'; y0, y1 = -2.75, 0.35
    for s in (-1, 1): p.box(m, s * 0.2 - 0.02, s * 0.2 + 0.02, y0, y1, -0.006, 0.006)
    for y in np.arange(y0 + 0.2, y1 - 0.05, 0.3): seg_cyl(p, 'steel', (-0.18, y, 0), (0.18, y, 0), 0.012, 6)
    seg_cyl(p, m, (0.2, y1 - 0.1, 0.0), (0.2, y1 + 0.5, 0.6), 0.015, 6); p.cham('steel_d', 0.12, 0.28, y1 + 0.42, y1 + 0.62, 0.55, 0.75, 0.02)
    return p
def fe_roof_ladder():
    """Escada de marinheiro da plataforma do ultimo andar ate a cobertura, passando sobre a platibanda (pivo: x = BX, deck)."""
    p = Piece(); m = 'iron'; xo, xi = 0.35, -0.75; yt = (LV[7] + PAR) - (LV[6] + DY) + 1.0; yr = LV[7] - (LV[6] + DY) + 0.012
    for s in (-1, 1):
        z = s * 0.22
        p.box(m, xo - 0.03, xo + 0.03, 0.0, yt, z - 0.006, z + 0.006); p.box(m, xi - 0.03, xo + 0.03, yt, yt + 0.06, z - 0.006, z + 0.006)
        p.box(m, xi - 0.03, xi + 0.03, yr, yt, z - 0.006, z + 0.006)
    for y in np.arange(0.3, yt - 0.1, 0.3): seg_cyl(p, 'steel', (xo, y, -0.21), (xo, y, 0.21), 0.012, 6)
    for x in np.arange(xi + 0.3, xo - 0.1, 0.3): seg_cyl(p, 'steel', (x, yt + 0.03, -0.21), (x, yt + 0.03, 0.21), 0.012, 6)
    for y in (1.0, 3.0):
        p.box(m, 0.0, xo - 0.03, y - 0.02, y + 0.02, -0.02, 0.02); p.box(m, xo - 0.03, xo + 0.03, y - 0.02, y + 0.02, -0.216, 0.216)
    p.box(m, xi - 0.06, xi + 0.06, yr, yr + 0.01, -0.26, 0.26)
    return p

# ============================================================================ cobertura (pivo: origem, y = cobertura)
BK = (HWX[0], -IZ, IX, HFZ[1]); BH = 3.0; BDX_ = (7.85, 8.75)
def bulkhead():
    """Casa de maquinas e saida da escada na cobertura: paredes de tijolo, porta de aco, janelinha, laje com capa, poco do
    elevador mais alto, respiro e luminaria."""
    p = Piece(); y0 = 0.012; y1 = BH; x0, z0, x1, z1 = BK; e = 0.022
    wall_grid(p, 'z', z0 + e, z1 - 0.25, x0, x0 + 0.25, [(-2.4, -1.6, 1.2, 2.0)], y0, y1, 'brick')
    wall_grid(p, 'x', x0, x1 - e, z1 - 0.25, z1, [(BDX_[0], BDX_[1], y0, 2.1)], y0, y1, 'brick')
    wall_grid(p, 'z', z0 + e, z1 - 0.25, x1 - 0.25 - e, x1 - e, [], y0, y1, 'brick')
    wall_grid(p, 'x', x0 + 0.25, x1 - 0.25 - e, z0 + e, z0 + 0.25 + e, [], y0, y1, 'brick')
    wall_grid(p, 'x', x0 + 0.25, SWX[0], SHZ[0], SHZ[1], [], y0, y1, 'plaster'); wall_grid(p, 'z', z0 + 0.25 + e, SHZ[1], SWX[0], SWX[1], [], y0, y1, 'plaster')
    ext_y(p, 'concrete', sbox(x0, z0 + e, x1 - e, z1), y1, y1 + 0.25)
    ext_y(p, 'stone', off(sbox(x0, z0 + e, x1 - e, z1), 0.04).difference(off(sbox(x0, z0 + e, x1 - e, z1), -0.2)), y1 + 0.25, y1 + 0.32)
    ext_y(p, 'membrane', off(sbox(x0, z0 + e, x1 - e, z1), -0.2).difference(sbox(x0, z0 + e, SWX[1], SHZ[1])), y1 + 0.25, y1 + 0.262)
    # poco do elevador mais alto
    ox0, oz0, ox1, oz1 = x0, z0 + e, SWX[1], SHZ[1] + 0.0
    wall_grid(p, 'x', ox0, ox1, oz0, oz0 + 0.25, [], y1 + 0.25, y1 + 1.4, 'brick'); wall_grid(p, 'x', ox0, ox1, oz1 - 0.25, oz1, [], y1 + 0.25, y1 + 1.4, 'brick')
    wall_grid(p, 'z', oz0 + 0.25, oz1 - 0.25, ox0, ox0 + 0.25, [], y1 + 0.25, y1 + 1.4, 'brick'); wall_grid(p, 'z', oz0 + 0.25, oz1 - 0.25, ox1 - 0.25, ox1, [], y1 + 0.25, y1 + 1.4, 'brick')
    ext_y(p, 'concrete', sbox(ox0, oz0, ox1, oz1), y1 + 1.4, y1 + 1.6); ext_y(p, 'stone', off(sbox(ox0, oz0, ox1, oz1), 0.04).difference(off(sbox(ox0, oz0, ox1, oz1), -0.15)), y1 + 1.6, y1 + 1.66)
    # porta: verga e soleira; janela
    p.box('stone', BDX_[0] - 0.1, BDX_[1] + 0.1, 2.104, 2.3, z1 - 0.004, z1 + 0.03); p.box('concrete', BDX_[0], BDX_[1], y0, y0 + 0.02, z1 - 0.25, z1 + 0.15)
    for (a, b, c, d) in ((x0 + 0.06, x0 + 0.12, -2.4, -1.6),):
        p.box('win_k', a, b, 1.2, 1.24, c, d); p.box('win_k', a, b, 1.96, 2.0, c, d); p.box('win_k', a, b, 1.24, 1.96, c, c + 0.04); p.box('win_k', a, b, 1.24, 1.96, d - 0.04, d)
        p.box('win_k', a, b, 1.24, 1.96, -2.02, -1.98); p.box('glass', a + 0.028, a + 0.032, 1.24, 1.96, c + 0.04, d - 0.04)
        p.box('stone', x0 - 0.04, x0 + 0.1, 1.13, 1.206, c - 0.06, d + 0.06)
    p.merge(wall_lamp(), tr(8.3, 2.45, z1))
    seg_cyl(p, 'galv', (6.0, y1 + 0.262, -2.5), (6.0, y1 + 0.9, -2.5), 0.12, 12); lathe(p, 'galv', [(0.2, y1 + 0.9), (0.2, y1 + 1.0), (0.0, y1 + 1.1)], x=6.0, z=-2.5, sec=12)
    p.cyl('metal', 0.18, y1 - 0.06, y1 - 0.002, 8.3, -1.4, 16); p.cyl('lamp_glass', 0.15, y1 - 0.075, y1 - 0.06, 8.3, -1.4, 16)
    return p
def water_tower():
    """Caixa d'agua de madeira sobre torre de aco (pivo: centro, cobertura): 4 pernas com contraventamento, plataforma de
    tabuas com guarda-corpo, tanque de aduelas com cintas, teto conico, escadas e tubo de descida."""
    p = Piece(); L = 1.5; yd = 4.5; R0, R1, yt = 2.0, 1.92, 4.62 + 3.6
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * L, sz * L
            p.cham('concrete', x - 0.3, x + 0.3, 0.012, 0.16, z - 0.3, z + 0.3, 0.01); p.box('steel_d', x - 0.18, x + 0.18, 0.16, 0.18, z - 0.18, z + 0.18)
            p.box('steel_d', x - 0.1, x + 0.1, 0.18, yd, z - 0.02, z + 0.02); p.box('steel_d', x - 0.1, x + 0.1, 0.18, yd, z - 0.1, z - 0.08); p.box('steel_d', x - 0.1, x + 0.1, 0.18, yd, z + 0.08, z + 0.1)
    for y in (2.3, yd - 0.12):
        for s in (-1, 1):
            p.box('steel_d', -L + 0.1, L - 0.1, y, y + 0.12, s * L - 0.05, s * L + 0.05); p.box('steel_d', s * L - 0.05, s * L + 0.05, y, y + 0.12, -L + 0.1, L - 0.1)
    for (ya, yb) in ((0.3, 2.3), (2.42, yd - 0.12)):
        for s in (-1, 1):
            for (a, b) in (((-L, ya), (L, yb)), ((L, ya), (-L, yb))):
                seg_cyl(p, 'steel', (a[0], a[1], s * (L + 0.11)), (b[0], b[1], s * (L + 0.11)), 0.016, 6)
                seg_cyl(p, 'steel', (s * (L + 0.11), a[1], a[0]), (s * (L + 0.11), b[1], b[0]), 0.016, 6)
    # plataforma
    for x in np.arange(-2.4, 2.4, 0.15): p.box('tank_w', x + 0.004, x + 0.146, yd, yd + 0.06, -2.4, 2.4)
    for z in (-2.3, 0.0, 2.3): p.box('steel_d', -2.4, 2.4, yd - 0.14, yd, z - 0.05, z + 0.05)
    for s in (-1, 1):
        for x in (-2.37, 0.0, 2.37):
            p.box('steel_d', x - 0.02, x + 0.02, yd + 0.06, yd + 1.1, s * 2.37 - 0.02, s * 2.37 + 0.02); p.box('steel_d', s * 2.37 - 0.02, s * 2.37 + 0.02, yd + 0.06, yd + 1.1, x - 0.02, x + 0.02) if x != 0.0 or True else None
        p.box('steel_d', -2.4, 2.4, yd + 1.06, yd + 1.1, s * 2.37 - 0.03, s * 2.37 + 0.03); p.box('steel_d', s * 2.37 - 0.03, s * 2.37 + 0.03, yd + 1.06, yd + 1.1, -2.34, 2.34)
        p.box('steel_d', -2.37, 2.37, yd + 0.55, yd + 0.58, s * 2.37 - 0.012, s * 2.37 + 0.012); p.box('steel_d', s * 2.37 - 0.012, s * 2.37 + 0.012, yd + 0.55, yd + 0.58, -2.355, 2.355)
    # tanque de aduelas
    n = 40; yb = yd + 0.12
    for k in range(4): p.box('tank_w', -1.9, 1.9, yd + 0.06, yb, -1.5 + k * 1.0 - 0.06, -1.5 + k * 1.0 + 0.06)
    for i in range(n):
        a0 = 2 * math.pi * (i + 0.04) / n; a1 = 2 * math.pi * (i + 0.96) / n
        pts = []
        for (r, y) in ((R0, yb), (R1, yt)):
            for rr in (r, r - 0.07):
                for a in (a0, a1): pts.append((rr * math.cos(a), y, rr * math.sin(a)))
        p.hull('tank_w', pts)
    p.cyl('dkwood', R0 - 0.05, yb + 0.003, yb + 0.05, 0, 0, n)
    for y in np.linspace(yb + 0.25, yt - 0.25, 7):
        r = R0 + (R1 - R0) * (y - yb) / (yt - yb); ring_y(p, 'steel_d', r - 0.01, r + 0.015, y - 0.025, y + 0.025, 0, 0, n)
    lathe(p, 'tank_w', [(R1 + 0.12, yt), (R1 + 0.12, yt + 0.05), (0.3, yt + 1.1), (0.0, yt + 1.15)], sec=n)
    lathe(p, 'steel_d', [(0.0, yt + 1.12), (0.1, yt + 1.15), (0.06, yt + 1.35)], sec=12); p.sphere('steel_d', 0.1, 0, yt + 1.4, 0, 1)
    p.cham('tank_w', 0.6, 1.1, yt + 0.45, yt + 0.55, -0.3, 0.3, 0.01) if False else None
    # tubo e escadas
    seg_cyl(p, 'galv', (0.0, 0.16, 0.6), (0.0, yd - 0.14, 0.6), 0.1, 12); p.cyl('concrete', 0.25, 0.012, 0.16, 0.0, 0.6, 12)
    for s in (-1, 1): p.box('steel_d', L + 0.3, L + 0.34, 0.012, yd + 1.0, s * 0.22 - 0.006, s * 0.22 + 0.006)
    for y in np.arange(0.3, yd - 0.05, 0.3): seg_cyl(p, 'steel', (L + 0.32, y, -0.21), (L + 0.32, y, 0.21), 0.012, 6)
    for s in (-1, 1): p.box('steel_d', R0 + 0.09, R0 + 0.12, yd + 0.06, yt + 0.4, s * 0.2 - 0.006, s * 0.2 + 0.006)
    for y in np.arange(yd + 0.35, yt + 0.3, 0.3): seg_cyl(p, 'steel', (R0 + 0.105, y, -0.19), (R0 + 0.105, y, 0.19), 0.01, 6)
    return p
def roof_deck():
    """Deck de madeira com pergolado, varal de luzes e borda de chapa (pivo: origem, y = cobertura)."""
    p = Piece(); x0, x1, z0, z1 = -8.6, 2.6, 1.2, 6.2; y = 0.18
    for (x, z) in [(x, z) for x in np.arange(x0 + 0.3, x1, 1.0) for z in (z0 + 0.3, (z0 + z1) / 2, z1 - 0.3)]: p.box('dark', x - 0.1, x + 0.1, 0.012, y - 0.06, z - 0.1, z + 0.1)
    for z in np.arange(z0 + 0.3, z1 - 0.1, 0.6): p.box('timber', x0 + 0.05, x1 - 0.05, y - 0.06, y - 0.025, z - 0.04, z + 0.04)
    for z in np.arange(z0, z1 - 0.01, 0.14): p.box('deck', x0, x1, y - 0.025, y, z + 0.003, min(z + 0.137, z1))
    for (a, b, c, d) in ((x0 - 0.02, x1 + 0.02, z0 - 0.02, z0), (x0 - 0.02, x1 + 0.02, z1, z1 + 0.02), (x0 - 0.02, x0, z0, z1), (x1, x1 + 0.02, z0, z1)): p.box('deck', a, b, 0.012, y, c, d)
    # pergolado
    px0, px1, pz0, pz1, ph = -8.2, -3.2, 1.6, 5.8, 2.6
    for x in (px0, px1):
        for z in (pz0, pz1): p.box('timber', x - 0.07, x + 0.07, y + 0.012, y + ph, z - 0.07, z + 0.07); p.box('steel_d', x - 0.1, x + 0.1, y, y + 0.012, z - 0.1, z + 0.1)
    for z in (pz0, pz1): p.box('timber', px0 - 0.3, px1 + 0.3, y + ph, y + ph + 0.22, z + 0.075, z + 0.145); p.box('timber', px0 - 0.3, px1 + 0.3, y + ph, y + ph + 0.22, z - 0.145, z - 0.075)
    for x in np.arange(px0 - 0.15, px1 + 0.2, 0.35): p.box('timber', x - 0.025, x + 0.025, y + ph + 0.22, y + ph + 0.34, pz0 - 0.35, pz1 + 0.35)
    # luzes: 2 fios entre o pergolado e postes na ponta do deck
    for x in (x1 - 0.15,):
        for z in (z0 + 0.2, z1 - 0.2): p.box('steel_d', x - 0.025, x + 0.025, y, y + 2.6, z - 0.025, z + 0.025)
    for (za, zb) in ((pz0, z0 + 0.2), (pz1, z1 - 0.2)):
        a = np.array([px1 + 0.07, y + ph, za]); b = np.array([x1 - 0.15, y + 2.55, zb]); pts = [a + (b - a) * t + np.array([0, -0.35 * 4 * t * (1 - t), 0]) for t in np.linspace(0, 1, 11)]
        for u, v in zip(pts[:-1], pts[1:]): seg_cyl(p, 'dark', u, v, 0.004, 4)
        for u in pts[1:-1]: p.sphere('lamp_glass', 0.035, u[0], u[1] - 0.05, u[2], 1)
    return p
def lounger():
    """Espreguicadeira de madeira com colchonete (pivo: centro, piso; encosto em -Z)."""
    p = Piece()
    for s in (-1, 1): p.box('timber', s * 0.3 - 0.02, s * 0.3 + 0.02, 0.0, 0.32, -0.95, 0.95)
    for z in np.arange(-0.25, 0.93, 0.11): p.box('timber', -0.32, 0.32, 0.32, 0.35, z, z + 0.09)
    p.hull('timber', [(x, y, z) for x in (-0.32, 0.32) for (y, z) in ((0.35, -0.3), (0.38, -0.3), (0.9, -0.85), (0.87, -0.88))])
    p.cham('awn_w', -0.29, 0.29, 0.35, 0.41, -0.25, 0.9, 0.02)
    p.hull('awn_w', [(x, y, z) for x in (-0.29, 0.29) for (y, z) in ((0.38, -0.27), (0.44, -0.25), (0.92, -0.8), (0.88, -0.84))])
    return p
def planter_box(L1=1.6, d=0.5, h=0.6, n=3):
    """Floreira de aco corten com arbustos (pivo: centro, piso)."""
    p = Piece(); x = L1 / 2
    p.box('corten', -x, x, 0.0, h, -d / 2, d / 2); p.box('dirt', -x + 0.02, x - 0.02, h - 0.08, h - 0.01, -d / 2 + 0.02, d / 2 - 0.02)
    for i in range(n):
        q = bush(0.3, 3 + i); p.merge(q, tr(-x + (i + 0.5) * L1 / n, h - 0.06, 0))
    return p
def umbrella():
    """Guarda-sol de lona (pivo: base, piso)."""
    p = Piece(); p.cyl('steel_d', 0.25, 0.0, 0.05, 0, 0, 16); seg_cyl(p, 'chrome', (0, 0.05, 0), (0, 2.4, 0), 0.02, 8)
    n = 8
    for k in range(n):
        a0, a1 = k * 2 * math.pi / n, (k + 1) * 2 * math.pi / n
        p.hull('awn_g' if k % 2 else 'awn_w', [(0, 2.45, 0), (0, 2.44, 0)] + [(1.3 * math.cos(a), 2.0 + d, 1.3 * math.sin(a)) for a in (a0, a1) for d in (0.0, 0.01)])
    return p
def hvac():
    """Condensadora de cobertura sobre trilhos (pivo: centro, cobertura): gabinete, aletas, grade do ventilador, tubos."""
    p = Piece(); x, z, h = 0.6, 0.5, 1.0
    for s in (-1, 1): p.box('steel_d', -x - 0.1, x + 0.1, 0.012, 0.12, s * 0.35 - 0.04, s * 0.35 + 0.04)
    p.cham('metal', -x, x, 0.12, 0.12 + h, -z, z, 0.01)
    for s in (-1, 1):
        for y in np.arange(0.2, h, 0.05): p.box('steel', -x + 0.05, x - 0.05, y, y + 0.012, *sorted((s * z, s * (z + 0.01))))
    ring_y(p, 'dark', 0.38, 0.42, 0.12 + h, 0.12 + h + 0.02, 0, 0, 24)
    for k in range(8): a = k * math.pi / 8; p.box('dark', -0.4 * math.cos(a) - 0.01, 0.4 * math.cos(a) + 0.01, 0.12 + h, 0.12 + h + 0.015, -0.01, 0.01) if k == 0 else seg_cyl(p, 'dark', (-0.39 * math.cos(a), 0.12 + h + 0.01, -0.39 * math.sin(a)), (0.39 * math.cos(a), 0.12 + h + 0.01, 0.39 * math.sin(a)), 0.006, 4)
    for dz in (-0.1, 0.1): seg_cyl(p, 'chrome', (x, 0.4, dz), (x + 0.3, 0.4, dz), 0.02, 6); seg_cyl(p, 'chrome', (x + 0.3, 0.4, dz), (x + 0.3, 0.012, dz), 0.02, 6)
    return p

# ============================================================================ rua e fachada (pivo indicado)
def awning():
    """Toldo listrado do cafe sobre as 3 vitrines (pivo: x = 0, calcada, face da fachada da frente; para +Z)."""
    p = Piece(); x0, x1 = -8.9, -0.1; yb, yf, zf = GHY, GHY - 0.6, 1.5; n = int((x1 - x0) / 0.3)
    for i in range(n):
        a = x0 + i * (x1 - x0) / n; b = a + (x1 - x0) / n; m = 'awn_g' if i % 2 == 0 else 'awn_w'
        p.hull(m, [(x, y + d, z) for x in (a, b) for (y, z) in ((yb, 0.02), (yf, zf)) for d in (0.0, 0.012)])
        p.box(m, a, b, yf - 0.28, yf + 0.006, zf, zf + 0.012)
        p.hull(m, [(x, yf - 0.28 - (0.06 if j else 0.0), zf + 0.006) for x in (a, b) for j in (0,)] + [((a + b) / 2, yf - 0.36, zf + 0.006), ((a + b) / 2, yf - 0.36, zf + 0.012)] + [(x, yf - 0.28, zf + 0.012) for x in (a, b)])
    for x in (x0, x1):
        p.hull('awn_g', [(x + d, y, z) for d in (0.0, 0.012 if x == x0 else -0.012) for (y, z) in ((yb, 0.02), (yf, zf), (yf - 0.28, zf), (yb - 0.25, 0.02))])
    seg_cyl(p, 'steel_d', (x0 + 0.004, yb + 0.03, 0.03), (x1 - 0.004, yb + 0.03, 0.03), 0.025, 8); seg_cyl(p, 'steel_d', (x0 + 0.004, yf - 0.01, zf - 0.02), (x1 - 0.004, yf - 0.01, zf - 0.02), 0.02, 8)
    for x in (x0 + 0.05, (x0 + x1) / 2, x1 - 0.05): seg_cyl(p, 'steel_d', (x, yb - 0.6, 0.02), (x, yf - 0.03, zf - 0.05), 0.016, 6); p.box('steel_d', x - 0.05, x + 0.05, yb - 0.66, yb - 0.54, 0.0, 0.02)
    return p
def entry_canopy():
    """Marquise de aco da portaria com tirantes e luminaria embutida (pivo: eixo da porta, calcada, face da fachada)."""
    p = Piece(); x = 1.25; y0, y1 = 3.6, 3.74; z0, z1 = 0.09, 1.5
    p.cham('steel_d', -x, x, y0, y1, z0, z1, 0.008); p.box('lamp_glass', -0.3, 0.3, y0 - 0.006, y0, 0.6, 1.0)
    for s in (-1, 1):
        seg_cyl(p, 'steel_d', (s * (x - 0.15), y1, z1 - 0.1), (s * (x - 0.15), 4.6, 0.02), 0.012, 6); p.box('steel_d', s * (x - 0.15) - 0.06, s * (x - 0.15) + 0.06, 4.54, 4.66, 0.0, 0.02)
    p.box('steel_d', -x, x, y0 + 0.02, y1 - 0.02, z0 - 0.09, z0) if False else p.box('steel_d', -x + 0.2, x - 0.2, y0 + 0.02, y1 - 0.02, 0.06, z0)
    return p
def tree_grate():
    p = Piece(); s = 0.6
    for (a, b, c, d) in ((-s, s, -s, -s + 0.06), (-s, s, s - 0.06, s), (-s, -s + 0.06, -s + 0.06, s - 0.06), (s - 0.06, s, -s + 0.06, s - 0.06)): p.box('cast', a, b, -0.03, 0.006, c, d)
    for k in range(16):
        a = k * math.pi / 8; seg_cyl(p, 'cast', (0.2 * math.cos(a), -0.012, 0.2 * math.sin(a)), (0.54 * math.cos(a), -0.012, 0.54 * math.sin(a)), 0.012, 4)
    ring_y(p, 'cast', 0.18, 0.22, -0.03, 0.0, 0, 0, 20); p.box('dirt', -s + 0.06, s - 0.06, -0.08, -0.06, -s + 0.06, s - 0.06)
    return p
def hydrant():
    p = Piece(); lathe(p, 'paint_r', [(0.14, 0.0), (0.14, 0.04), (0.11, 0.06), (0.11, 0.58), (0.13, 0.6), (0.13, 0.64), (0.09, 0.7), (0.03, 0.78)], sec=16)
    for s in (-1, 1): disc_x(p, 'paint_r', 0.05, *sorted((s * 0.1, s * 0.2)), 0.45, 0.0, 12); disc_x(p, 'chrome', 0.055, *sorted((s * 0.2, s * 0.22)), 0.45, 0.0, 12)
    disc_z(p, 'paint_r', 0.065, 0.1, 0.2, 0.0, 0.42, 12); return p
def dumpster():
    """Cacamba de lixo de aco com tampas de plastico (pivo: centro, piso)."""
    p = Piece(); x, z = 0.95, 0.6
    for (xx, zz) in ((-x + 0.1, -z + 0.1), (x - 0.1, -z + 0.1), (-x + 0.1, z - 0.1), (x - 0.1, z - 0.1)): p.cyl('rubber', 0.06, 0.0, 0.12, xx, zz, 10)
    p.hull('dumpster', [(sx * x, 0.12, sz * z) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * (x + 0.05), 1.15, sz * (z + 0.05)) for sx in (-1, 1) for sz in (-1, 1)])
    for s in (-1, 1): p.hull('dark', [(xx, y, zz) for xx in sorted((0.0, s * (x + 0.06))) for (y, zz) in ((1.15, -z - 0.08), (1.15, z + 0.06), (1.27, z + 0.06), (1.27, -z + 0.1))])
    p.box('steel_d', -x - 0.08, x + 0.08, 0.95, 1.0, -z - 0.02, -z + 0.03) if False else None
    return p
def food_truck():
    """Food truck amarelo generico (pivo: centro, rua; frente para +X; janela de servico do lado -Z): chassi, rodas, cabine,
    bau com janela, aba levantada, balcao, toldo, luzes, pictograma de xicara e sem texto."""
    p = Piece(); x0, x1, w = -2.9, 2.9, 1.1; yb = 0.55; yt = 3.1; cab = 1.6
    for (x, s) in [(x, s) for x in (-1.9, 1.9) for s in (-1, 1)]:
        m = trimesh.creation.cylinder(radius=0.42, height=0.28, sections=24); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([x, 0.42, s * 0.88]); p.add('rubber', m)
        disc_z(p, 'chrome', 0.24, *sorted((s * 1.02, s * 1.03)), x, 0.42, 16)
    p.box('dark', x0 + 0.2, x1 - 0.2, 0.32, yb, -0.85, 0.85)
    p.cham('truck_y', x0, x1 - cab, yb, yt, -w, w, 0.06)
    p.hull('truck_y', [(x, y, z) for z in (-w + 0.02, w - 0.02) for (x, y) in ((x1 - cab, yb), (x1 - cab, 2.6), (x1 - 0.6, 2.5), (x1, 1.5), (x1, yb), (x1 - 0.25, 2.2))])
    p.hull('glass', [(x, y, z) for z in (-w + 0.15, w - 0.15) for (x, y) in ((x1 - 0.28, 1.65), (x1 - 0.66, 2.36), (x1 - 0.67, 2.35), (x1 - 0.29, 1.64))] + [(x1 - 0.2, 1.62, 0.0)])
    for s in (-1, 1): p.box('glass', x1 - 1.3, x1 - 0.5, 1.4, 2.2, *sorted((s * (w - 0.01), s * (w + 0.002))))
    p.box('cream', x0 + 0.05, x1 - cab - 0.05, 1.05, 1.15, -w - 0.004, -w + 0.01); p.box('cream', x0 + 0.05, x1 - cab - 0.05, 1.05, 1.15, w - 0.01, w + 0.004)
    # janela de servico
    a, b, y0, y1 = x0 + 0.6, x1 - cab - 0.4, 1.35, 2.45
    p.box('dark', a, b, y0, y1, -w - 0.003, -w + 0.05); p.box('steel', a - 0.05, b + 0.05, y0 - 0.06, y0, -w - 0.4, -w + 0.02)
    p.hull('truck_y', [(x, y, z) for x in (a, b) for (y, z) in ((y1 + 0.02, -w - 0.01), (y1 + 0.03, -w - 0.03), (y1 + 0.5, -w - 0.95), (y1 + 0.47, -w - 0.96))])
    for x in (a + 0.1, b - 0.1): seg_cyl(p, 'chrome', (x, y1, -w - 0.02), (x, y1 + 0.47, -w - 0.92), 0.01, 6)
    for i in range(4): p.cyl('porcelain', 0.035, y0, y0 + 0.1, a + 0.3 + i * 0.25, -w - 0.2, 10)
    q = Piece(); q.box('truck_y', -0.22, 0.14, -0.16, 0.16, 0.0, 0.01); q.box('truck_y', 0.14, 0.26, -0.04, 0.08, 0.0, 0.01); q.box('truck_y', -0.3, 0.32, -0.24, -0.2, 0.0, 0.01)
    p.box('cream', a + 0.3 - 0.4, a + 0.3 + 0.4, 2.62, 3.0, -w - 0.006, -w); p.merge(q, rot_y(180, (a + 0.3, 2.82, -w - 0.006)))
    p.box('dark', x1 - 0.03, x1 + 0.01, 0.6, 0.9, -0.7, 0.7); p.box('chrome', x1 - 0.02, x1 + 0.04, 0.5, 0.62, -w + 0.05, w - 0.05)
    for s in (-1, 1): p.box('lamp_glass', x1 - 0.01, x1 + 0.012, 1.0, 1.15, s * 0.8 - 0.12, s * 0.8 + 0.12); p.box('neon_r', x0 - 0.012, x0 + 0.01, 0.7, 0.85, s * 0.9 - 0.1, s * 0.9 + 0.1)
    p.box('steel_d', x0 + 0.3, x0 + 1.0, yt, yt + 0.25, -0.5, 0.4)
    return p
def site():
    """Terreno: calcadas de placas com covas de arvore, guias, rua com faixa central, viela dos fundos e lateral."""
    p = Piece()
    walk = sbox(SX0, -8.4, EWX, SWZ).difference(rect()).buffer(0)
    pits = [sbox(x - 0.6, z - 0.6, x + 0.6, z + 0.6) for (x, z) in TREES]
    walk = walk.difference(unary_union(pits))
    p.merge(paving(walk, Y0, 1.5, 'concrete'))
    for q in pits: ext_y(p, 'dirt', q, GY, Y0 - 0.08)
    for q in (sbox(SX0, SWZ, SX1, CZ), sbox(EWX, SZ0, EWX + 0.2, SWZ), sbox(SX0, -8.6, EWX, -8.4)): ext_y(p, 'concrete', q.difference(sbox(EWX, SWZ - 0.0, EWX + 0.2, CZ)) if False else q, GY, Y0)
    ext_y(p, 'asphalt', sbox(SX0, CZ, SX1, SZ1), GY, 0.0); ext_y(p, "asphalt", sbox(EWX + 0.2, SZ0, SX1, SWZ), GY, 0.0); ext_y(p, 'asphalt', sbox(SX0, SZ0, EWX, -8.6), GY, 0.0)
    for x in np.arange(SX0 + 1.0, SX1 - 1.0, 3.0): p.box('paint_y', x, x + 1.5, 0.0, 0.003, 14.36, 14.48)
    ext_y(p, 'concrete', sbox(EWX + 0.2, SWZ, SX1, CZ), GY, Y0) if False else None
    return p
TREES = [(-11.5, 9.4), (-3.0, 9.4), (7.2, 9.4), (12.4, 5.9)]

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
pieces = {
    'site': site(), 'ground_slab': ground_slab(), 'envelope_ground': envelope('g'), 'envelope_storey': envelope('t'), 'parapet': parapet(),
    'slab_1': slab('1'), 'slab_storey': slab('t'), 'slab_roof': slab('r'), 'core_ground': core('g'), 'core_storey': core('t'),
    'stair_ground': stair('g'), 'stair_1': stair('1'), 'stair_storey': stair('t'), 'elev_door': elev_door(), 'door_stair': door_metal(0.88, 2.07),
    'door_loft': door_plank(), 'door_bath': door_interior(0.83, 2.03), 'door_shop': door_shop(), 'door_service': door_metal(0.88, 2.13),
    'door_fire_escape': door_fe(), 'door_roof': door_metal(0.88, 2.07), 'post_timber': post_t(), 'post_iron': post_g(),
    'kitchen': kitchen(), 'island': island(), 'dining': dining(), 'sofa_a': sofa_l('fabric'), 'sofa_b': sofa_l('fabric3'), 'coffee_table': coffee_table(),
    'rug_a': rug(3.4, 2.6, 'rug'), 'rug_b': rug(3.4, 2.6, 'rug2'), 'rug_lobby': rug(2.4, 1.6, 'rug2'), 'armchair': armchair(), 'floor_lamp': floor_lamp(), 'tv_unit': tv_unit(),
    'bed_a': bed('bed_b'), 'bed_b': bed('cloth_r'), 'nightstand': nightstand(), 'wardrobe': wardrobe(), 'partition': partition(), 'desk': desk(),
    'office_chair': office_chair(), 'bookcase': bookcase(), 'bathroom': bathroom(), 'coat_bench': coat_bench(), 'plant': plant(1.5),
    'pendant': pendant(0.9), 'pendant_long': pendant(1.4, 0.26, 'shop_g'), 'cafe_counter': cafe_counter(), 'bistro_2': bistro(2), 'bistro_1': bistro(1),
    'banquette': banquette(6.0), 'bench_lobby': banquette(1.8), 'mailboxes': mailboxes(), 'bike_rack': bike_rack(3), 'bicycle_b': bicycle('paint_b'), 'bicycle_r': bicycle('paint_r'),
    'fe_platform_low': fe_platform(None, ladder_z=1.8), 'fe_platform_a': fe_platform((-2.97, -0.15)), 'fe_platform_b': fe_platform((0.15, 2.97)),
    'fe_stair': fe_stair(), 'fe_ladder': fe_ladder(), 'fe_roof_ladder': fe_roof_ladder(),
    'bulkhead': bulkhead(), 'water_tower': water_tower(), 'roof_deck': roof_deck(), 'lounger': lounger(), 'planter_box': planter_box(), 'umbrella': umbrella(), 'hvac': hvac(),
    'awning': awning(), 'entry_canopy': entry_canopy(), 'street_lamp': lamp_post(4.2), 'tree': tree(6.5, 1.7, 'leaf', 2), 'tree_grate': tree_grate(), 'hydrant': hydrant(),
    'trash_can': trash_can(), 'bench': park_bench(), 'dumpster': dumpster(), 'food_truck': food_truck(), 'car_sedan_b': car('car_b', 'sedan'), 'car_hatch_g': car('car_g', 'hatch'),
    'player_scale_ref': player_ref()}

# ============================================================================ montagem
G = ['predio']; J = ['rua']
def fl(k): return G + [f'floor{k}']
put('site', 0, 0, 0, 0, J); put('ground_slab', 0, Y0, 0, 0, fl(0))
put('envelope_ground', 0, LV[0], 0, 0, G + ['front', 'ext', 'floor0'])
for k in range(1, NF): put('envelope_storey', 0, LV[k], 0, 0, G + ['front', 'ext', f'floor{k}'])
put('parapet', 0, LV[7], 0, 0, G + ['roof', 'ext'])
put('slab_1', 0, LV[1], 0, 0, fl(1))
for k in range(2, NF): put('slab_storey', 0, LV[k], 0, 0, fl(k))
put('slab_roof', 0, LV[7], 0, 0, G + ['roof'])
put('core_ground', 0, LV[0], 0, 0, fl(0)); put('stair_ground', 0, LV[0], 0, 0, fl(0))
for k in range(1, NF): put('core_storey', 0, LV[k], 0, 0, fl(k)); put('stair_1' if k == 1 else 'stair_storey', 0, LV[k], 0, 0, fl(k))
for k in range(NF):
    put('elev_door', EDX, LV[k], SHZ[1], 0, fl(k))
    put('door_stair', (SWX[0] + SWX[1]) / 2, LV[k], SDZ[0] + 0.01, -90, fl(k), door=90)
    for (x, z) in [(x, z) for x in PX for z in PZ if not (x > HWX[0] and z < 0)]: put('post_iron' if k == 0 else 'post_timber', x, LV[k], z, 0, fl(k))
# portas da rua
for c in (1.5, 4.5): put('door_shop', c - 0.495, LV[0] + 0.012, BZ - 0.23, 0, G + ['floor0'], door=90)
put('door_service', -1.5 + 0.445, LV[0] + 0.012, -BZ + 0.23, 180, G + ['floor0'], door=90)
# lofts (andares 1 a 6)
for k in range(1, NF):
    y = LV[k]; t = fl(k); v = 'a' if k % 2 else 'b'
    put('door_loft', LDX[0] + 0.01, y, (HFZ[0] + HFZ[1]) / 2, 0, t, door=90)
    put('door_fire_escape', BX - 0.17, y + 0.206, 1.5 + 0.44, 90, t, door=90)
    put('bathroom', 0, y, 0, 0, t); put('door_bath', BDX[0] + 0.01, y, (BWZ[0] + BWZ[1]) / 2, 0, t, door=-90)
    put('kitchen', 0, y, -IZ, 0, t); put('island', -5.2, y, -4.4, 0, t); put('dining', -6.2, y, -0.6, 0, t)
    for x in (-5.25, -4.45): put('pendant', x, y + H - ST - JD, -4.4, 0, t)
    put('pendant', -6.05, y + H - ST - JD, -0.6, 0, t)
    put(f'rug_{v}', 2.7, y, 4.6, 0, t); put(f'sofa_{v}', 2.5, y, 6.3, 180, t); put('coffee_table', 2.8, y, 4.4, 0, t)
    put('tv_unit', 2.8, y, 3.2, 0, t); put('armchair', 4.6, y, 4.6, -90, t); put('floor_lamp', 4.9, y, 5.9, 180, t)
    put('partition', 0, y, 0, 0, t); put(f'bed_{v}', -7.6, y, PZ[1] + 0.04, 0, t)
    for x in (-8.7, -6.5): put('nightstand', x, y, PZ[1] + 0.04, 0, t)
    put('wardrobe', -4.0, y, 5.6, 90, t)
    put('desk', 1.5, y, -IZ + 0.05, 0, t); put('office_chair', 1.5, y, -5.55, 180, t); put('bookcase', BWX[0], y, -5.0, -90, t)
    put('coat_bench', 7.5, y, HFZ[1], 0, t)
    for (x, z) in ((-9.0, 5.9), (8.9, 6.0), (-0.5, -5.9)): put('plant', x, y, z, 0, t)
# cafe e portaria (terreo)
y = LV[0]; t = fl(0)
put('cafe_counter', 0, y, 0, 0, t); put('banquette', -IX + 0.003, y, 1.5, 90, t)
for z in (-0.5, 1.5, 3.5): put('bistro_1', -8.55, y, z, 90, t)
for (x, z) in ((-4.2, 1.2), (-2.6, 4.9), (-1.6, -0.6), (-5.6, 5.2)): put('bistro_2', x, y, z, 0, t)
for x in (-7.65, -6.05, -4.45): put('pendant_long', x, y + GH - ST - JD, -4.7, 0, t)
for (x, z) in ((-3.65, 2.0), (-1.25, 4.4), (-5.25, 4.4)): put('pendant_long', x, y + GH - ST - JD, z, 0, t)
put('mailboxes', CWX[1], y, 2.0, 90, t); put('bench_lobby', IX, y, 3.0, -90, t); put('rug_lobby', 6.3, y, 2.8, 0, t)
put('pendant_long', 5.95, y + GH - ST - JD, 2.8, 0, t)
for (x, z) in ((3.6, 6.0), (8.9, 6.0)): put('plant', x, y, z, 0, t)
put('bike_rack', 3.75, y, -3.5, 90, t); put('bicycle_b', 3.55, y, -4.3, 90, t); put('bicycle_r', 3.95, y, -2.7, 90, t)
# escada de incendio
FE_SIDE = {1: 'fe_platform_low', 2: 'fe_platform_a', 3: 'fe_platform_b', 4: 'fe_platform_a', 5: 'fe_platform_b', 6: 'fe_platform_a'}
FT = G + ['fire_escape', 'ext']
for k in range(1, NF):
    put(FE_SIDE[k], BX, LV[k], 0, 0, FT)
    if k < NF - 1: put('fe_stair', FEL, LV[k] + DY, 0.0, 180 if k % 2 else 0, FT)
put('fe_ladder', FEL, LV[1] + DY, 1.8, 0, FT); put('fe_roof_ladder', BX, LV[6] + DY, 3.0, 0, FT)
# cobertura
R = G + ['roof']; y = LV[7]
put('bulkhead', 0, y, 0, 0, R); put('door_roof', BDX_[0] + 0.01, y + 0.012, HFZ[1] - 0.125, 0, R, door=-90)
put('water_tower', -6.5, y, -3.8, 0, R); put('roof_deck', 0, y, 0, 0, R)
for (x, z) in ((-1.2, -5.3), (0.6, -5.3), (2.4, -5.3)): put('hvac', x, y, z, 0, R)
for x in (-1.2, 0.8): put('lounger', x, y + 0.18, 3.6, 180, R)
put('bistro_2', -5.7, y + 0.18, 3.7, 0, R); put('umbrella', -0.2, y + 0.18, 5.2, 0, R)
for x in (-7.1, -5.3, -1.6, 0.2): put('planter_box', x, y + 0.18, 5.85, 0, R)
# rua
put('awning', 0, Y0, BZ, 0, J + ['ext']); put('entry_canopy', 4.5, Y0, BZ, 0, J + ['ext'])
for (x, z) in TREES: put('tree_grate', x, Y0, z, 0, J); put('tree', x, Y0 - 0.06, z, 0, J + ['roof'])
for (x, z) in ((-12.6, 10.0), (1.0, 10.0), (12.9, 10.0), (12.9, -6.0)): put('street_lamp', x, Y0, z, 0, J + ['roof'])
for (x, z) in ((-6.0, 8.7), (-1.0, 8.9)): put('bistro_2', x, Y0, z, 0, J)
for x in (0.25, 2.75): put('planter_box', x, Y0, 7.4, 0, J) if False else None
put('bench', -8.5, Y0, 10.0, 180, J); put('bike_rack', 9.2, Y0, 9.6, 0, J); put('bicycle_b', 8.85, Y0, 9.85, 0, J)
put('hydrant', 11.9, Y0, 10.15, 0, J); put('trash_can', -13.2, Y0, 10.1, 0, J); put('trash_can', 10.4, Y0, 10.1, 0, J)
put('dumpster', -4.0, Y0, -7.8, 0, J); put('food_truck', 4.0, 0, 12.3, 0, J)
put('car_sedan_b', -8.0, 0, 12.2, 90, J); put('car_hatch_g', 11.5, 0, 16.3, -90, J)
put('player_scale_ref', -12.0, Y0, 8.5, 0, J); put('player_scale_ref', 6.0, LV[1], 1.8, 0, fl(1))

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'ground_floor': Y0, 'storey_height': H, 'ground_storey_height': GH, 'levels': LV, 'slab': ST,
                       'building': {'x': [-BX, BX], 'z': [-BZ, BZ]}, 'wall': T, 'stair_core': {'x': [HWX[0], IX], 'z': [-IZ, HFZ[1]]},
                       'fire_escape': {'x': [BX, BX + FW], 'z': [-PL, PL]}, 'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
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
