"""Kit 56: predio de apartamentos com patio e piscina (garden apartments dos anos 60), em ALTO DETALHE (scripts/detalhe).
Duas alas de 2 pavimentos de reboco verde-claro, uma de frente para a outra, com o patio e a piscina no meio. Galerias externas
no 1o andar com guarda-corpo de barras e painel de losangos, escada de aco aberta em cada ala, telhado plano com cascalho,
platibanda com rufo, condensadoras e antena de TV. Fachada da rua lisa com estrela atomica e ondas em relevo (sem texto).
Garagem coberta embaixo da ala oeste (pilares de tubo, vigas, luminarias, armarios), escritorio da administracao com vitrine e
lavanderia no terreo da ala leste. 10 apartamentos mobiliados no estilo dos anos 60 (sala, cozinha, jantar, quarto e banheiro).
Patio com piscina azulejada, deque, espreguicadeiras, mesa com guarda-sol, mesas de piquenique, churrasqueira, palmeiras,
floreiras, caixas de correio e portao com muretas de cobogo. Calcada, rua, postes e carros genericos. Arte original e sem texto.
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
CAR_COLS = {'car_r': (176, 70, 58), 'car_b': (70, 110, 150), 'car_g': (88, 120, 86), 'car_y': (206, 176, 90), 'car_w': (222, 218, 206),
            'car_o': (186, 104, 56), 'car_t': (92, 150, 146), 'car_k': (48, 50, 54), 'car_p': (214, 150, 160)}
configurar(cores=dict({'stucco': (204, 220, 196), 'stucco_w': (236, 234, 222), 'plaster': (238, 234, 224), 'ceil': (244, 242, 236),
                       'concrete': (190, 186, 176), 'conc_s': (184, 180, 170), 'conc_d': (150, 148, 142), 'coping': (230, 228, 218), 'asphalt': (84, 86, 88),
                       'gravel': (172, 166, 152), 'grass': (118, 152, 80), 'dirt': (150, 128, 98), 'membrane': (110, 112, 114), 'block': (214, 212, 202),
                       'accent': (200, 62, 112), 'accent2': (64, 150, 156), 'accent3': (232, 176, 60), 'plinth': (120, 128, 118),
                       'carpet': (176, 150, 104), 'carpet_b': (120, 140, 130), 'vinyl_f': (226, 220, 200), 'vinyl_k': (60, 110, 120), 'tile_b': (150, 196, 206),
                       'tile_p': (226, 170, 178), 'tile_w': (240, 240, 236), 'pool_t': (60, 150, 196), 'water': (110, 190, 220), 'grout': (200, 200, 196),
                       'cab_y': (236, 214, 150), 'cab_t': (150, 196, 186), 'ctop': (226, 222, 206), 'formica': (230, 140, 120), 'enamel': (240, 238, 232),
                       'alu': (196, 200, 204), 'metal': (176, 180, 184), 'frame': (232, 230, 222), 'chrome': (212, 216, 220), 'steel': (120, 126, 132),
                       'steel_d': (56, 60, 64), 'iron': (40, 42, 44), 'galv': (164, 170, 170), 'trim': (232, 226, 210), 'teak': (150, 96, 56),
                       'wood': (176, 132, 88), 'dkwood': (110, 78, 54), 'deck': (164, 124, 84), 'lamp_glass': (255, 238, 196), 'dark': (34, 34, 36),
                       'rubber': (30, 30, 32), 'glass': (150, 186, 204), 'mirror': (200, 214, 220), 'jal': (176, 206, 214),
                       'fabric_o': (214, 120, 60), 'fabric_t': (60, 140, 140), 'fabric_m': (170, 160, 130), 'fabric_y': (226, 196, 90), 'vinyl_w': (236, 230, 214),
                       'vinyl_r': (180, 64, 60), 'bed_w': (238, 234, 222), 'bed_p': (220, 150, 160), 'bed_g': (150, 180, 130), 'porcelain': (244, 244, 240),
                       'porc_p': (232, 180, 186), 'screen': (40, 50, 50), 'leaf': (86, 128, 62), 'leaf2': (108, 150, 70), 'frond': (92, 140, 64),
                       'bark': (130, 104, 76), 'palm_t': (150, 124, 92), 'plant': (70, 120, 60), 'pot': (230, 226, 214), 'pot_o': (210, 110, 70),
                       'umb_y': (240, 196, 60), 'umb_w': (244, 240, 228), 'pic_t': (64, 160, 160), 'pic_m': (210, 84, 120), 'pic_y': (232, 196, 80),
                       'paint_w': (240, 240, 234), 'paint_y': (232, 196, 60), 'paint_b': (60, 110, 170), 'brass': (196, 164, 90), 'gold': (210, 176, 90),
                       'coal': (40, 38, 36), 'flame_r': (200, 80, 40), 'paper': (236, 232, 220), 'book_r': (170, 70, 60), 'book_b': (60, 90, 140),
                       'book_g': (80, 120, 80), 'book_y': (210, 170, 70), 'cream': (240, 232, 214), 'player': (90, 140, 220), 'door': (200, 62, 112),
                       'door_t': (64, 150, 156), 'door_int': (230, 222, 204), 'tv_s': (60, 70, 72), 'hedge': (74, 116, 58), 'mulch': (110, 84, 62),
                       'line_w': (236, 236, 230), 'line_y': (226, 190, 70), 'curb': (200, 198, 190), 'flag_o': (230, 140, 50), 'neon_r': (220, 60, 50), 'vinyl': (70, 60, 56)}, **CAR_COLS),
           texturas={'stucco': 'render', 'stucco_w': 'render', 'plaster': 'plaster', 'ceil': 'plaster', 'concrete': 'render', 'conc_s': 'render',
                     'conc_d': 'render', 'asphalt': 'render', 'gravel': 'render', 'grass': 'render', 'dirt': 'render', 'block': 'plaster',
                     'carpet': 'render', 'carpet_b': 'render', 'teak': 'planks', 'wood': 'planks', 'dkwood': 'planks', 'deck': 'deck',
                     'bark': 'render', 'palm_t': 'render', 'membrane': 'render', 'mulch': 'render', 'curb': 'render', 'coping': 'render'},
           out=OUT)
D.METAL.update({'metal', 'chrome', 'steel', 'steel_d', 'iron', 'galv', 'alu'} | set(CAR_COLS)); MATS = D.MATS; TEX = D.TEX
for k in CAR_COLS: MATS[k].roughnessFactor = 0.45; MATS[k].metallicFactor = 0.4
MATS['water'].roughnessFactor = 0.05; MATS['water'].metallicFactor = 0.1; MATS['water'].alphaMode = 'BLEND'; MATS['water'].baseColorFactor = [110 / 255, 190 / 255, 220 / 255, 0.55]

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.1
Y0 = 0.15; H = 3.0; ST = 0.25; GY = -0.3
LV = [Y0, Y0 + H, Y0 + 2 * H]                                    # 0,15 terreo, 3,15 1o andar, 6,15 cobertura
CH = H - ST                                                      # pe-direito 2,75
WX = (-12.0, -5.0); IXW = (WX[0] + T, WX[1] - T)                 # ala oeste (a leste e a mesma girada 180 graus)
ZE = 9.75; IZE = ZE - T                                          # alas de -9,75 a 9,75 em Z
PW = 0.2; UW = 6.2                                               # paredes entre apartamentos e largura interna de um apartamento
UZ = (6.4, 0.0, -6.4)                                            # centros dos 3 apartamentos de cada ala (frente, meio, fundos)
PWZ = (3.2, -3.2)                                                # eixos das paredes entre apartamentos
HU = UW / 2                                                      # 3,1: meia largura interna
# apartamento (oeste, x do mundo, u = z - zc)
P1X = (-8.6, -8.5)                                               # parede entre sala e quarto/banheiro
P2U = (0.6, 0.7)                                                 # parede entre quarto e banheiro
DOOR_U = (-2.8, -1.9)                                            # porta de entrada (parede do patio)
LWIN_U = (-1.3, 1.1); KWIN_U = (1.9, 2.9)                        # janela da sala e da cozinha (patio)
BWIN_U = (-2.15, -0.35); JWIN_U = (1.1, 1.9)                     # janela do quarto e basculante do banheiro (fundos)
BDOOR_U = (-2.85, -2.05); WDOOR_U = (1.4, 2.2)                   # portas do quarto e do banheiro (parede P1)
DH = 2.1; IDH = 2.04
# galeria e escada (oeste; a leste e girada 180 graus)
GX = (WX[1], -3.6)                                               # galeria de 1,4 m
GPZ = (-9.48, -6.4, -3.0, 0.0, 3.8, 6.6, 9.48)                     # pilares da galeria
SXR = (-3.55, -2.4)                                              # faixa da escada (fora da galeria)
NR = 17; RR = H / NR; TRD = 0.27                                 # espelhos, altura e piso dos degraus
SZ0 = -2.0; SZ1 = SZ0 + (NR - 1) * TRD                           # inicio e topo do lance (2,32)
LZ = (SZ1, SZ1 + 1.2)                                            # patamar de chegada
GOZ = (LZ[0] + 0.1, LZ[1] - 0.1)                                 # abertura no guarda-corpo da galeria
PAR = 0.5                                                        # platibanda
# garagem (terreo da frente da ala oeste) e escritorio/lavanderia (terreo da frente da ala leste)
CPZ = (PWZ[0] + PW / 2, ZE)
OFZ = 6.2                                                        # parede entre escritorio (frente) e lavanderia
# piscina e terreno
POOL = (-1.6, 1.6, -6.6, 2.4); PD = (-1.05, -1.7)                # piscina e profundidades (raso, fundo)
SX0, SX1, SZ0S, SZ1S = -16.0, 16.0, -13.0, 18.0
SWZ0, SWZ1 = 10.6, 12.6; CZ = 12.75                              # calcada e guia
YD = Y0 - 0.02                                                   # piso do patio (2 cm abaixo dos apartamentos)
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

# ============================================================================ paredes (pivo local da fachada: face externa em z = 0, parede para -Z, x ao longo)
def wall2(p, axis, u0, u1, vo, vi, holes, ya, yb, out='stucco', inn='plaster', split=0.5):
    """Parede de 2 camadas (reboco por fora, massa por dentro) com vaos (a, b, y0, y1). axis 'x': corre em X, espessura em Z
    de vo (face externa) a vi; 'z': corre em Z, espessura em X."""
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

def slider(p, a, b, ya, yb, z0=-0.17, mull=True):
    """Janela de correr de aluminio (2 folhas, uma fixa por fora e a de correr por dentro), com trilho, fecho e puxador."""
    f = 0.045; zf0, zf1 = z0, z0 + 0.09
    p.box('alu', a, a + f, ya, yb, zf0, zf1); p.box('alu', b - f, b, ya, yb, zf0, zf1)
    p.box('alu', a + f, b - f, yb - f, yb, zf0, zf1); p.box('alu', a + f, b - f, ya, ya + f, zf0, zf1)
    xm = (a + b) / 2; s = 0.035; ia, ib, ja, jb = a + f, b - f, ya + f, yb - f
    for (u, v, za, zb) in ((ia, xm + 0.02, zf1 - 0.035, zf1 - 0.012), (xm - 0.02, ib, zf0 + 0.012, zf0 + 0.035)):
        p.box('alu', u, u + s, ja, jb, za, zb); p.box('alu', v - s, v, ja, jb, za, zb)
        p.box('alu', u + s, v - s, jb - s, jb, za, zb); p.box('alu', u + s, v - s, ja, ja + s, za, zb)
        p.box('glass', u + s - 0.004, v - s + 0.004, ja + s - 0.004, jb - s + 0.004, (za + zb) / 2 - 0.002, (za + zb) / 2 + 0.002)
    ym = (ja + jb) / 2; p.box('chrome', xm - 0.04, xm - 0.016, ym - 0.05, ym + 0.05, zf0 - 0.002, zf0 + 0.012)
    p.box('chrome', ib - 0.045, ib - 0.03, ym - 0.12, ym + 0.12, zf0 - 0.012, zf0 + 0.012)
def jalousie(p, a, b, ya, yb, z0=-0.17):
    """Basculante de palhetas de vidro (anos 60): caixilho, 8 palhetas inclinadas com garras e manivela."""
    f = 0.04; zf0, zf1 = z0, z0 + 0.08
    p.box('alu', a, a + f, ya, yb, zf0, zf1); p.box('alu', b - f, b, ya, yb, zf0, zf1)
    p.box('alu', a + f, b - f, yb - f, yb, zf0, zf1); p.box('alu', a + f, b - f, ya, ya + f, zf0, zf1)
    n = 8; hh = (yb - ya - 2 * f) / n; zc = z0 + 0.04
    for i in range(n):
        yc = ya + f + (i + 0.5) * hh; q = Piece(); q.box('jal', a + f + 0.012, b - f - 0.012, -hh * 0.55, hh * 0.55, -0.003, 0.003)
        p.merge(q, tr(0, yc, zc) @ trimesh.transformations.rotation_matrix(math.radians(-35), [1, 0, 0]))
        for x in (a + f + 0.004, b - f - 0.016): p.box('alu', x, x + 0.012, yc - 0.03, yc + 0.03, zc - 0.015, zc + 0.015)
    seg_cyl(p, 'chrome', (b - f - 0.06, ya + f + 0.02, zf0 - 0.002), (b - f - 0.06, ya + f + 0.02, zf0 - 0.05), 0.008, 6)
    seg_cyl(p, 'chrome', (b - f - 0.06, ya + f + 0.02, zf0 - 0.05), (b - f - 0.14, ya + f + 0.02, zf0 - 0.05), 0.007, 6)
def eyebrow(p, a, b, ya, yb, w=0.1, d=0.07, sill=True):
    """Moldura saliente de reboco claro em volta do vao (tipica dos predios dingbat) e peitoril com pingadeira."""
    m = 'stucco_w'
    p.box(m, a - w, a, ya - (0.0 if sill else w), yb + w, 0.0, d); p.box(m, b, b + w, ya - (0.0 if sill else w), yb + w, 0.0, d)
    p.box(m, a, b, yb, yb + w, 0.0, d)
    if sill:
        p.box(m, a - w - 0.05, b + w + 0.05, ya - 0.07, ya, 0.0, d + 0.04)
        p.box(m, a - w - 0.03, b + w + 0.03, ya - 0.09, ya - 0.07, d, d + 0.03)
    else: p.box(m, a, b, ya - w, ya, 0.0, d)
def stool(p, a, b, y):
    p.box('trim', a - 0.06, b + 0.06, y - 0.02, y + 0.012, -T - 0.035, -0.17)
def door_frame(p, a, b, h, z0=-T, z1=0.0, mat='trim', ext_lamp=True, plaque=True):
    """Batente de madeira pintada no vao (pivo local da fachada), soleira de aluminio, arandela cilindrica e plaqueta lisa."""
    j = 0.035
    p.box(mat, a, a + j, 0.0, h, z0 + 0.03, -0.03); p.box(mat, b - j, b, 0.0, h, z0 + 0.03, -0.03); p.box(mat, a + j, b - j, h - j, h, z0 + 0.03, -0.03)
    p.box('alu', a + j, b - j, 0.0, 0.012, z0 + 0.03, 0.0)
    if ext_lamp:
        xl = b + 0.32
        p.box('metal', xl - 0.05, xl + 0.05, 1.9, 2.19, 0.0, 0.03)
        seg_cyl(p, 'metal', (xl, 2.05, 0.03), (xl, 2.05, 0.1), 0.015, 6)
        lathe(p, 'lamp_glass', [(0.06, 1.88), (0.07, 1.92), (0.07, 2.18), (0.06, 2.22), (0.0, 2.22)], x=xl, z=0.17, sec=16)
        lathe(p, 'metal', [(0.075, 1.86), (0.075, 1.88), (0.0, 1.88)], x=xl, z=0.17, sec=16); lathe(p, 'metal', [(0.075, 2.22), (0.075, 2.25), (0.0, 2.25)], x=xl, z=0.17, sec=16)
    if plaque:
        xp = b + 0.32; p.cham('brass', xp - 0.09, xp + 0.09, 1.45, 1.6, 0.0, 0.012, 0.004)
        for k in range(3): p.box('dark', xp - 0.06 + k * 0.045, xp - 0.03 + k * 0.045, 1.49, 1.56, 0.012, 0.014)
def plinth_run(p, segs, y0, y1=0.35):
    for (a, b) in segs:
        if b - a > 0.01: p.box('plinth', a, b, y0, y1, 0.0, 0.014); p.box('plinth', a, b, y1, y1 + 0.015, 0.0, 0.006)
def starburst(p, cx, cy, r=0.9, n=12):
    """Estrela atomica de chapa: disco central, raios alternados longos e curtos e bolinhas nas pontas."""
    disc_z(p, 'gold', 0.12, 0.0, 0.03, cx, cy, 24); disc_z(p, 'accent', 0.07, 0.03, 0.045, cx, cy, 20)
    for k in range(n):
        a = 2 * math.pi * k / n + 0.13; L_ = r if k % 2 == 0 else r * 0.6; w = 0.035 if k % 2 == 0 else 0.025
        ca, sa = math.cos(a), math.sin(a); px, py = -sa, ca
        pts = [(cx + ca * 0.1 + px * w, cy + sa * 0.1 + py * w), (cx + ca * 0.1 - px * w, cy + sa * 0.1 - py * w), (cx + ca * L_, cy + sa * L_)]
        p.hull('gold' if k % 2 == 0 else 'accent', [(x, y, z) for (x, y) in pts for z in (0.004, 0.022)])
        if k % 2 == 0: p.sphere('accent', 0.04, cx + ca * (L_ + 0.03), cy + sa * (L_ + 0.03), 0.03, 1)
def waves(p, x0, cy, n=3, s=0.55, mat='accent'):
    """Ondas em relevo (pictograma abstrato no lugar do nome do predio): 3 arcos de tubo."""
    for i in range(n):
        xc = x0 + i * s; pts = [(xc + s * t, cy + 0.14 * math.sin(math.pi * t * 2)) for t in np.linspace(0, 1, 13)]
        for (u, v) in zip(pts[:-1], pts[1:]): seg_cyl(p, mat, (u[0], u[1], 0.03), (v[0], v[1], 0.03), 0.028, 8)
        p.sphere(mat, 0.028, pts[0][0], pts[0][1], 0.03, 1)
    p.sphere(mat, 0.028, x0 + n * s, cy, 0.03, 1)

def facade(x0, x1, y0, y1, ops, st, plinth=False, deco=None, out='stucco'):
    """Uma fachada: parede com vaos e o acabamento de cada vao. ops = (a, b, ya, yb, tipo): slider, jal, door, store, void."""
    p = Piece(); holes = [(a, b, ya, yb) for (a, b, ya, yb, k) in ops]
    wall2(p, 'x', x0, x1, 0.0, -T, holes, y0, y1, out, 'plaster')
    for (a, b, ya, yb, k) in ops:
        if k == 'slider': slider(p, a, b, ya, yb); eyebrow(p, a, b, ya, yb); stool(p, a, b, ya)
        if k == 'jal': jalousie(p, a, b, ya, yb); eyebrow(p, a, b, ya, yb, 0.08, 0.05); stool(p, a, b, ya)
        if k == 'door': door_frame(p, a, b, yb)
        if k == 'ldoor': door_frame(p, a, b, yb, plaque=False)
        if k == 'store': storefront(p, a, b, yb)
    if plinth:
        gaps = [(a - 0.001, b + 0.001) for (a, b, ya, yb, k) in ops if ya < 0.05]
        plinth_run(p, segs_excl(gaps, x0, x1), y0 + 0.003)
    if deco: deco(p)
    return p
def storefront(p, a, b, h):
    """Vitrine de aluminio do escritorio: montantes, travessa da bandeira, rodape de chapa, vidros e vao da porta (no meio)."""
    f = 0.05; z0, z1 = -0.16, -0.06; xm = (a + b) / 2; dw = 0.5
    p.box('alu', a, a + f, 0.0, h, z0, z1); p.box('alu', b - f, b, 0.0, h, z0, z1); p.box('alu', a + f, b - f, h - f, h, z0, z1)
    TB = 2.2
    for (u, v) in ((a + f, xm - dw - f), (xm + dw + f, b - f)):
        p.box('alu', u, v, 0.0, 0.3, z0, z1); p.box('alu', u, v, TB - f / 2, TB + f / 2, z0, z1)
        p.box('glass', u - 0.003, v + 0.003, 0.3, TB - f / 2, -0.112, -0.108)
        if v - u > 1.2: xc = (u + v) / 2; p.box('alu', xc - f / 2, xc + f / 2, 0.3, TB - f / 2, z0, z1)
    for x in (xm - dw - f, xm + dw): p.box('alu', x, x + f, 0.0, h - f, z0, z1)
    p.box('alu', xm - dw, xm + dw, TB - f / 2, TB + f / 2, z0, z1)
    p.box('glass', a + f - 0.003, b - f + 0.003, TB + f / 2, h - f, -0.112, -0.108)
    p.box('alu', xm - dw, xm + dw, 0.0, 0.012, -T + 0.02, 0.0)
    # marquise de concreto com faixa colorida
    p.box('stucco_w', a - 0.3, b + 0.3, h + 0.2, h + 0.32, 0.0, 1.3); p.box('accent', a - 0.3, b + 0.3, h + 0.2, h + 0.32, 1.3, 1.34)
    for x in np.linspace(a + 0.2, b - 0.2, 4): p.cyl('metal', 0.09, h + 0.18, h + 0.2, x, 0.8, 16); p.cyl('lamp_glass', 0.07, h + 0.165, h + 0.18, x, 0.8, 16)

# ============================================================================ aberturas das alas
def unit_ops_court(zc, st, x_of):
    """Vaos da parede do patio de um apartamento (u = z - zc), em x local da fachada."""
    ops = []
    for (u0, u1, k, ya, yb) in ((DOOR_U[0], DOOR_U[1], 'door', 0.0, DH), (LWIN_U[0], LWIN_U[1], 'slider', 0.9, DH), (KWIN_U[0], KWIN_U[1], 'slider', 1.1, DH)):
        a, b = sorted((x_of(zc + u0), x_of(zc + u1))); ops.append((a, b, ya, yb, k))
    return ops
def unit_ops_back(zc, x_of):
    ops = []
    for (u0, u1, k, ya, yb) in ((BWIN_U[0], BWIN_U[1], 'slider', 0.9, DH), (JWIN_U[0], JWIN_U[1], 'jal', 1.4, DH)):
        a, b = sorted((x_of(zc + u0), x_of(zc + u1))); ops.append((a, b, ya, yb, k))
    return ops
def wing_sides(wing):
    """(M local->mundo, x0, x1, x_of(z ou x do mundo)) de cada fachada da ala: court, back, street, rear."""
    if wing == 'w':
        xa, xb = WX
        return {'court': (rot_y(90, (xb, 0, 0)), -IZE, IZE, lambda z: -z), 'back': (rot_y(-90, (xa, 0, 0)), -IZE, IZE, lambda z: z),
                'street': (tr(0, 0, ZE), xa, xb, lambda x: x), 'rear': (rot_y(180, (0, 0, -ZE)), -xb, -xa, lambda x: -x)}
    xa, xb = -WX[1], -WX[0]
    return {'court': (rot_y(-90, (xa, 0, 0)), -IZE, IZE, lambda z: z), 'back': (rot_y(90, (xb, 0, 0)), -IZE, IZE, lambda z: -z),
            'street': (tr(0, 0, ZE), xa, xb, lambda x: x), 'rear': (rot_y(180, (0, 0, -ZE)), -xb, -xa, lambda x: -x)}
def unit_centers(wing, st):
    """Centros (z do mundo) dos apartamentos da ala no pavimento; z_u: z do mundo = z_u(zc, u)."""
    zs = list(UZ) if wing == 'w' else [-z for z in UZ]
    if st == 'g': zs = [z for z in zs if z < 3.0]
    return zs
def u_sign(wing): return 1 if wing == 'w' else -1
def envelope(wing, st):
    """Envoltoria de uma ala em um pavimento (st 'g' ou 't'): 4 fachadas, paredes entre apartamentos e acabamentos.
    Pivo: origem, y = piso do pavimento."""
    p = Piece(); S = wing_sides(wing); sg = u_sign(wing); y0 = (GY - Y0) if st == 'g' else 0.0; y1 = H
    xs_w = (WX if wing == 'w' else (-WX[1], -WX[0]))
    for side, (M, x0, x1, x_of) in S.items():
        ops = []; deco = None
        if side == 'court':
            for zc in unit_centers(wing, st):
                for (a, b, ya, yb, k) in unit_ops_court(0.0, st, lambda u: x_of(zc + sg * u)): ops.append((a, b, ya, yb, k))
            if st == 'g' and wing == 'w':                         # garagem: parede do patio vira cobogo (peca propria)
                a, b = sorted((x_of(CPZ[0]), x_of(IZE))); ops.append((a, b, -1.0, CH, 'void'))
            if st == 'g' and wing == 'e':                         # lavanderia: porta e janela para o patio
                for (z0, z1, k, ya, yb) in ((3.7, 4.6, 'ldoor', 0.0, DH), (4.9, 6.0, 'slider', 1.1, DH)):
                    a, b = sorted((x_of(z0), x_of(z1))); ops.append((a, b, ya, yb, k))
        if side == 'back':
            for zc in unit_centers(wing, st):
                for (a, b, ya, yb, k) in unit_ops_back(0.0, lambda u: x_of(zc + sg * u)): ops.append((a, b, ya, yb, k))
            if st == 'g' and wing == 'w':
                for zz in (5.0, 7.8): a, b = sorted((x_of(zz - 0.6), x_of(zz + 0.6))); ops.append((a, b, 2.0, 2.45, 'slider'))
            if st == 'g' and wing == 'e':
                for (z0, z1) in ((4.1, 5.3), (7.2, 8.6)): a, b = sorted((x_of(z0), x_of(z1))); ops.append((a, b, 1.2, DH, 'slider'))
        if side == 'street':
            if st == 'g' and wing == 'w': ops.append((xs_w[0] + T, xs_w[1] - T, -1.0, CH, 'void'))
            if st == 'g' and wing == 'e': ops.append((xs_w[0] + 1.3, xs_w[1] - 1.3, 0.0, 2.5, 'store'))
            if st == 't':
                cx = (xs_w[0] + xs_w[1]) / 2 + (1.2 if wing == 'w' else -1.2)
                wx = cx - 3.1 if wing == 'w' else cx + 1.6
                def deco(q, cx=cx, wx=wx): starburst(q, cx, 1.55, 1.0); waves(q, wx, 0.7)
        if st == 'g' and wing == 'w' and side == 'street':
            q = Piece()
            # so as pontas da parede (pilares de canto) e a viga sobre a entrada da garagem
            wall2(q, 'x', x0, x0 + T, 0.0, -T, [], y0, y1); wall2(q, 'x', x1 - T, x1, 0.0, -T, [], y0, y1)
            wall2(q, 'x', x0 + T, x1 - T, 0.0, -T, [], CH, y1)
            plinth_run(q, [(x0, x0 + T), (x1 - T, x1)], y0 + 0.003)
            p.merge(q, M); continue
        p.merge(facade(x0, x1, y0, y1, ops, st, plinth=(st == 'g'), deco=deco), M)
    # paredes entre apartamentos (massa dos dois lados; no terreo da garagem e do escritorio, reboco do lado de la)
    xa, xb = (IXW if wing == 'w' else (-IXW[1], -IXW[0]))
    for zp in PWZ:
        wall2(p, 'x', xa, xb, zp + PW / 2, zp - PW / 2, [], 0.0, CH, 'plaster', 'plaster')
    # quinas: faixa colorida vertical nas quinas da rua (pavimento de cima)
    if st == 't':
        for x in (xs_w[0], xs_w[1]):
            s = -1 if x == xs_w[0] else 1; a, b = sorted((x, x - s * 0.18))
            p.box('accent', a, b, 0.0, H, ZE, ZE + 0.02)
    return p

# ============================================================================ lajes (pivo: origem, y = piso do pavimento)
def wing_inner(wing):
    xa, xb = IXW if wing == 'w' else (-IXW[1], -IXW[0]); return sbox(xa, -IZE, xb, IZE)
def wing_box(wing):
    xa, xb = WX if wing == 'w' else (-WX[1], -WX[0]); return sbox(xa, -ZE, xb, ZE)
def ground_slab():
    """Piso do terreo das 2 alas: concreto (os apartamentos poem o proprio piso por cima), garagem com faixas e mancha de oleo,
    escritorio de vinil xadrez e lavanderia de vinil liso."""
    p = Piece(); y0 = GY - Y0
    for wing in ('w', 'e'): ext_y(p, 'conc_s', wing_inner(wing), y0, 0.0)
    # garagem: faixas das 2 vagas e manchas
    for x in (-8.5,): ext_y(p, 'line_w', sbox(x - 0.05, 4.6, x + 0.05, 9.2), 0.0, 0.002)
    for (x, z) in ((-10.2, 6.2), (-6.9, 6.6)): ext_y(p, 'dark', Point(x, z).buffer(0.35, 12), 0.0, 0.0012)
    # escritorio (frente da ala leste) e lavanderia
    of = sbox(-IXW[1], OFZ + 0.05, -IXW[0], IZE); la = sbox(-IXW[1], PWZ[0] + PW / 2, -IXW[0], OFZ - 0.05)
    tiles_k(p, of, 0.0, 0.012, 0.3, 'vinyl_f', 'vinyl_k'); tiles_k(p, la, 0.0, 0.012, 0.3, 'vinyl_f', 'vinyl_f')
    return p
def tiles_k(p, poly, y0, y1, s, m1, m2, gap=0.003, ox=0.0, oz=0.0):
    """Ladrilhos em xadrez (m1/m2) sobre fundo de rejunte."""
    b = poly.bounds; ext_y(p, 'grout', poly.buffer(-0.004, join_style=2), y0, y1 - 0.004)
    for i in range(int(math.floor((b[0] - ox) / s)), int(math.ceil((b[2] - ox) / s))):
        for j in range(int(math.floor((b[1] - oz) / s)), int(math.ceil((b[3] - oz) / s))):
            q = sbox(ox + i * s + gap, oz + j * s + gap, ox + (i + 1) * s - gap, oz + (j + 1) * s - gap).intersection(poly)
            if q.area > 1e-6: ext_y(p, m1 if (i + j) % 2 == 0 else m2, q, y0, y1)
def slab_1():
    """Laje do 1o andar das 2 alas: forro de massa por baixo e concreto (pivo: y = piso do 1o andar)."""
    p = Piece()
    for wing in ('w', 'e'):
        r = wing_inner(wing); ext_y(p, 'ceil', r, -ST, -ST + 0.012); ext_y(p, 'conc_s', r, -ST + 0.012, 0.0)
        # luminarias de sobrepor da garagem / escritorio / lavanderia (ficam no forro)
    for (x, z) in ((-10.0, 6.4), (-7.0, 6.4)):
        p.box('metal', x - 0.6, x + 0.6, -ST - 0.06, -ST, z - 0.1, z + 0.1); p.box('lamp_glass', x - 0.56, x + 0.56, -ST - 0.075, -ST - 0.06, z - 0.07, z + 0.07)
    for (x, z) in ((8.5, 8.0), (8.5, 4.75)):
        p.cyl('metal', 0.2, -ST - 0.05, -ST, x, z, 20); p.cyl('lamp_glass', 0.17, -ST - 0.09, -ST - 0.05, x, z, 20)
    return p
def roof():
    """Cobertura das 2 alas (pivo: y = cobertura): laje com forro, manta, cascalho, platibanda com capa e rufo, marquise sobre a
    galeria com faixa colorida e forro, buzinotes e respiros."""
    p = Piece()
    for wing in ('w', 'e'):
        sg = 1 if wing == 'w' else -1
        def X(x): return sg * x
        r = wing_inner(wing); ext_y(p, 'ceil', r, -ST, -ST + 0.012); ext_y(p, 'conc_s', r, -ST + 0.012, 0.0)
        xo, xc = X(WX[0]), X(WX[1]); xg = X(GX[1])                      # face de fora, face do patio, borda da galeria
        # laje da marquise da galeria (entre a parede do patio e a borda)
        can = sbox(min(xc, xg), -ZE, max(xc, xg), ZE)
        ext_y(p, 'ceil', can, -0.22, -0.208); ext_y(p, 'conc_s', can, -0.208, 0.0)
        # manta e cascalho (dentro da platibanda; vai ate a borda da galeria)
        a, b = sorted((X(WX[0] + T), xg - sg * 0.12)); mem = sbox(a, -IZE, b, IZE)
        ext_y(p, 'membrane', mem, 0.0, 0.012); ext_y(p, 'gravel', mem.buffer(-0.25, join_style=2), 0.012, 0.03)
        # platibanda nos 3 lados (fundos e 2 pontas), capa e rufo
        pr = []
        a, b = sorted((xo, X(WX[0] + T))); pr.append(sbox(a, -ZE, b, ZE))
        a, b = sorted((xo, xc)); pr += [sbox(a, IZE, b, ZE), sbox(a, -ZE, b, -IZE)]
        par = unary_union(pr)
        ext_y(p, 'stucco', par, 0.0, PAR - 0.05); ext_y(p, 'coping', par.buffer(0.03, join_style=2), PAR - 0.05, PAR)
        inner = sbox(*sorted((X(WX[0] + T), xc)), -IZE, IZE)
        # rufo: manta subindo na face interna da platibanda e chapa por cima
        ring_in = inner.difference(inner.buffer(-0.012, join_style=2)).intersection(par.buffer(0.013, join_style=2))
        ext_y(p, 'membrane', ring_in, 0.012, 0.25); ext_y(p, 'galv', inner.difference(inner.buffer(-0.02, join_style=2)).intersection(par.buffer(0.021, join_style=2)), 0.25, 0.27)
        # faixa colorida (fascia) em volta da marquise da galeria e na borda da platibanda da rua
        a, b = sorted((xg, xg + sg * 0.05)); fas = [sbox(a, -ZE - 0.05, b, ZE + 0.05)]
        a, b = sorted((xc + sg * 0.004, xg)); fas += [sbox(a, ZE, b, ZE + 0.05), sbox(a, -ZE - 0.05, b, -ZE)]
        ext_y(p, 'accent', unary_union(fas), -0.32, 0.16)
        # guarda do cascalho na borda da galeria
        a, b = sorted((xg - sg * 0.12, xg - sg * 0.05)); ext_y(p, 'galv', sbox(a, -IZE, b, IZE), 0.0, 0.1)
        # buzinotes na platibanda de fundos
        for z in (-6.4, 0.0, 6.4):
            x = X(WX[0]); a, b = sorted((x, x - sg * 0.3)); p.box('galv', a, b, 0.0, 0.1, z - 0.12, z + 0.12)
    return p

# ============================================================================ galeria do 1o andar (ala oeste; a leste e a mesma girada 180 graus; pivo: y = piso da galeria)
def rail_run(p, axis, a, b, c, y0=0.0, h=1.0, mat='steel_d', panel='accent'):
    """Guarda-corpo de barras: montantes, corrimao chato, travessa de baixo, barras verticais e faixa de losangos coloridos."""
    def bx(u0, u1, ya, yb, v0, v1):
        if axis == 'z': p.box(mat, v0, v1, ya, yb, u0, u1)
        else: p.box(mat, u0, u1, ya, yb, v0, v1)
    n = max(1, int(math.ceil((b - a) / 1.25))); xs = np.linspace(a, b, n + 1)
    for x in xs: bx(x - 0.025, x + 0.025, y0, y0 + h, c - 0.025, c + 0.025)
    bx(a - 0.025, b + 0.025, y0 + h, y0 + h + 0.04, c - 0.04, c + 0.04)
    bx(a + 0.025, b - 0.025, y0 + 0.08, y0 + 0.12, c - 0.02, c + 0.02)
    bx(a + 0.025, b - 0.025, y0 + 0.62, y0 + 0.65, c - 0.015, c + 0.015); bx(a + 0.025, b - 0.025, y0 + 0.83, y0 + 0.86, c - 0.015, c + 0.015)
    for (u, v) in zip(xs[:-1], xs[1:]):
        m = int((v - u - 0.05) / 0.11)
        for k in range(m):
            x = u + 0.025 + (v - u - 0.05) * (k + 0.5) / m
            for (ya, yb) in ((0.12, 0.62), (0.86, h)): bx(x - 0.008, x + 0.008, y0 + ya, y0 + yb, c - 0.008, c + 0.008)
        # faixa de losangos entre as 2 travessas
        k2 = int((v - u - 0.05) / 0.22)
        for k in range(k2):
            x = u + 0.025 + (v - u - 0.05) * (k + 0.5) / k2; ym = y0 + 0.74
            pts = [(x - 0.09, ym), (x, ym + 0.085), (x + 0.09, ym), (x, ym - 0.085)]
            if axis == 'z': p.hull(panel, [(c + dz, y, xx) for (xx, y) in pts for dz in (-0.006, 0.006)])
            else: p.hull(panel, [(xx, y, c + dz) for (xx, y) in pts for dz in (-0.006, 0.006)])
def gallery():
    """Galeria externa do 1o andar: laje em balanco com pingadeira, forro com luminarias, pilares de tubo quadrado ate a
    marquise, guarda-corpo de barras com losangos e abertura para a escada, calha e condutor."""
    p = Piece(); x0, x1 = GX; yb = -0.2; ytop = H - 0.22
    deck = sbox(x0, -ZE, x1, ZE)
    ext_y(p, 'ceil', deck, yb, yb + 0.012); ext_y(p, 'concrete', deck, yb + 0.012, -0.012); ext_y(p, 'conc_s', sbox(x0, -ZE, x1 - 0.003, ZE), -0.012, 0.0)
    for (a, b) in segs_excl([LZ], -ZE, ZE):                               # testeira da laje (interrompida no patamar)
        p.box('stucco_w', x1, x1 + 0.04, yb - 0.04, 0.03, a, b); p.box('stucco_w', x1 + 0.04, x1 + 0.055, yb - 0.04, yb - 0.02, a, b)
    p.box('stucco_w', x1, x1 + 0.04, yb - 0.04, -0.2, *LZ)
    for z in (-ZE, ZE):
        a, b = sorted((z, z + (0.04 if z > 0 else -0.04))); p.box('stucco_w', x0, x1 + 0.04, yb - 0.04, 0.03, a, b)
    # pilares (do patio ate a marquise)
    yg = YD - LV[1]
    for z in GPZ:
        p.box('accent', x1 - 0.1, x1, yg + 0.012, ytop, z - 0.05, z + 0.05)
        p.box('steel_d', x1 - 0.13, x1 + 0.03, yg, yg + 0.012, z - 0.08, z + 0.08)
    # guarda-corpo: borda externa (com abertura da escada) e as 2 pontas
    for (a, b) in segs_excl([GOZ], -ZE + 0.06, ZE - 0.06):
        segs = segs_excl([(z - 0.06, z + 0.06) for z in GPZ], a, b)
        for (u, v) in segs: rail_run(p, 'z', u, v, x1 - 0.05)
    for z in (-ZE + 0.06, ZE - 0.06): rail_run(p, 'x', x0 + 0.03, x1 - 0.11, z)
    # luminarias no forro (uma por porta)
    for zc in UZ:
        z = zc + (DOOR_U[0] + DOOR_U[1]) / 2 + 0.9
        p.cyl('metal', 0.14, yb - 0.035, yb, (x0 + x1) / 2 + 0.1, z, 16); p.cyl('lamp_glass', 0.12, yb - 0.06, yb - 0.035, (x0 + x1) / 2 + 0.1, z, 16)
    # calha da marquise e condutores nas pontas
    for z in (-ZE + 0.2, ZE - 0.2):
        seg_cyl(p, 'galv', (x1 - 0.05, ytop + 0.1, z), (x1 - 0.05, ytop, z), 0.035, 10)
        seg_cyl(p, 'galv', (x1 - 0.05, ytop, z), (x1 - 0.05, yg + 0.25, z), 0.035, 10)
        seg_cyl(p, 'galv', (x1 - 0.05, yg + 0.25, z), (x1 + 0.2, yg + 0.05, z), 0.035, 10)
    return p

# ============================================================================ escada externa (ala oeste, sobe para +Z; pivo: origem do mundo, y = 0)
def stair_ext():
    """Escada aberta de aco: 2 banzos de perfil U coloridos, degraus de chapa dobrada com enchimento de concreto e bocel,
    corrimaos de tubo nos 2 lados, patamar de chegada ligado a galeria, pilares e base de concreto."""
    p = Piece(); x0, x1 = SXR; rr = (LV[1] - YD) / NR; z0 = SZ0
    for i in range(1, NR):
        y = YD + i * rr; a = z0 + (i - 1) * TRD; b = z0 + i * TRD
        p.box('steel_d', x0 + 0.06, x1 - 0.06, y - 0.05, y - 0.04, a, b + 0.03)
        p.box('steel_d', x0 + 0.06, x1 - 0.06, y - 0.05, y, b, b + 0.03)
        p.box('conc_s', x0 + 0.06, x1 - 0.06, y - 0.04, y - 0.003, a + 0.003, b)
        p.box('steel', x0 + 0.062, x1 - 0.062, y - 0.003, y + 0.002, b - 0.04, b + 0.033)
    zt = z0 + (NR - 1) * TRD
    for x in (x0, x1 - 0.06):
        p.hull('accent', [(xx, y, z) for xx in (x, x + 0.06) for (y, z) in ((YD, z0 - 0.05), (YD + 0.3, z0 - 0.05), (LV[1] + 0.05, zt + 0.02), (LV[1] - 0.28, zt + 0.02))])
    # patamar
    ly = LV[1]; pa, pb = LZ
    p.box('steel_d', SXR[0] - 0.05, x1 - 0.004, ly - 0.2, ly - 0.012, pa, pb); p.box('conc_s', SXR[0] - 0.05, x1 - 0.004, ly - 0.012, ly, pa, pb)
    for x in (x1 - 0.08,):
        for z in (pa + 0.05, pb - 0.05): p.box('accent', x - 0.04, x + 0.04, YD, ly - 0.2, z - 0.04, z + 0.04)
    # guarda-corpo do patamar (lado de fora e fundo)
    rail_run(p, 'z', pa + 0.03, pb - 0.03, x1 - 0.03, ly)
    rail_run(p, 'x', SXR[0] - 0.02, x1 - 0.06, pb - 0.03, ly)
    # corrimaos dos lances (tubo sobre montantes)
    for x in (x0 + 0.03, x1 - 0.03):
        for i in range(2, NR, 4):
            z = z0 + (i - 0.5) * TRD; y = YD + i * rr; seg_cyl(p, 'steel_d', (x, y, z), (x, y + 0.9, z), 0.018, 8)
        seg_cyl(p, 'steel_d', (x, YD + 0.9 + rr, z0 + 0.2), (x, ly + 0.9 + 0.05, zt + 0.05), 0.022, 10)
    seg_cyl(p, 'steel_d', (x1 - 0.03, ly + 0.95, zt + 0.05), (x1 - 0.03, ly + 1.0, pa + 0.05), 0.022, 10)
    # base de concreto
    p.box('concrete', x0 - 0.05, x1 + 0.05, YD - 0.05, YD + 0.06, z0 - 0.3, z0 + 0.1)
    return p

# ============================================================================ garagem (terreo da frente da ala oeste; pivo: origem, y = Y0)
def carport():
    """Coluna de tubo, batentes de concreto, armarios de chapa no fundo, torneira, extintor e para-choque de borracha."""
    p = Piece()
    seg_cyl(p, 'accent', (-8.5, 0.03, ZE - 0.22), (-8.5, CH - 0.03, ZE - 0.22), 0.07, 14)
    lathe(p, 'steel_d', [(0.14, 0.0), (0.14, 0.03), (0.08, 0.05), (0.0, 0.05)], x=-8.5, z=ZE - 0.22, sec=16)
    lathe(p, 'steel_d', [(0.0, CH - 0.05), (0.08, CH - 0.05), (0.14, CH - 0.03), (0.14, CH), (0.0, CH)], x=-8.5, z=ZE - 0.22, sec=16)
    for x in (-10.15, -6.85):
        p.cham('concrete', x - 0.8, x + 0.8, 0.0, 0.12, 3.95, 4.15, 0.02)
        for s in (-1, 1): p.box('paint_y', x + s * 0.5 - 0.12, x + s * 0.5 + 0.12, 0.12, 0.123, 3.97, 4.13)
    # armarios de deposito na parede do fundo (z = 3,3)
    z0 = CPZ[0]
    for i in range(6):
        x = -11.55 + i * 0.95; p.box('steel', x, x + 0.92, 0.0, 0.1, z0, z0 + 0.5); p.box('metal', x, x + 0.92, 0.1, 2.0, z0, z0 + 0.55)
        p.box('steel', x + 0.03, x + 0.89, 0.15, 1.95, z0 + 0.55, z0 + 0.56)
        for k in range(5): yy = 1.7 - k * 0.04; p.box('dark', x + 0.25, x + 0.67, yy, yy + 0.015, z0 + 0.56, z0 + 0.563)
        p.box('chrome', x + 0.8, x + 0.84, 0.9, 1.05, z0 + 0.56, z0 + 0.59); p.box('brass', x + 0.4, x + 0.52, 1.85, 1.9, z0 + 0.56, z0 + 0.562)
    p.box('metal', -11.6, -5.85, 2.0, 2.03, z0, z0 + 0.58)
    # torneira e extintor na parede de fora (x = -11,75)
    xi = IXW[0]
    p.box('galv', xi, xi + 0.04, 0.5, 0.56, 8.2, 8.26); seg_cyl(p, 'galv', (xi + 0.04, 0.53, 8.23), (xi + 0.12, 0.5, 8.23), 0.015, 6)
    p.box('paint_y', xi, xi + 0.02, 1.0, 1.5, 4.6, 4.9)
    p.cyl('vinyl_r', 0.08, 1.05, 1.55, xi + 0.11, 4.75, 12); p.box('dark', xi + 0.02, xi + 0.05, 1.45, 1.5, 4.72, 4.78)
    return p
def breeze(p, axis, a, b, c, y0, y1, t=0.2, s=0.4, mat='block', gaps=()):
    """Parede de cobogo: blocos de 40 cm com quadrado e cruz vazados (4 petalas); gaps = trechos sem blocos."""
    for (u0, u1) in segs_excl(gaps, a, b):
        n = max(1, int(round((u1 - u0) / s))); su = (u1 - u0) / n; m = max(1, int(round((y1 - y0) / s))); sy = (y1 - y0) / m
        for i in range(n):
            for j in range(m):
                ua, ub = u0 + i * su, u0 + (i + 1) * su; ya, yb = y0 + j * sy, y0 + (j + 1) * sy; e = 0.035; uc = (ua + ub) / 2; yc = (ya + yb) / 2
                boxes = [(ua, ub, ya, ya + e), (ua, ub, yb - e, yb), (ua, ua + e, ya + e, yb - e), (ub - e, ub, ya + e, yb - e),
                         (uc - 0.025, uc + 0.025, ya + e, yb - e), (ua + e, uc - 0.025, yc - 0.025, yc + 0.025), (uc + 0.025, ub - e, yc - 0.025, yc + 0.025)]
                for (u, v, w0, w1) in boxes:
                    if axis == 'z': p.box(mat, c - t / 2, c + t / 2, w0, w1, u, v)
                    else: p.box(mat, u, v, w0, w1, c - t / 2, c + t / 2)
                # aneis diagonais (losango) em volta do centro
                for (dx, dy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    q_ = (su / 2 - e - 0.025) / 2; qy = (sy / 2 - e - 0.025) / 2
                    cu = uc + dx * (0.025 + q_); cy = yc + dy * (0.025 + qy); r, ry = q_ + 0.005, qy + 0.005
                    pts = [(cu - r, cy), (cu, cy + ry), (cu + r, cy), (cu, cy - ry)]
                    if axis == 'z': p.hull(mat, [(c + dz, y, u) for (u, y) in pts for dz in (-t / 2 + 0.03, t / 2 - 0.03)])
                    else: p.hull(mat, [(u, y, c + dz) for (u, y) in pts for dz in (-t / 2 + 0.03, t / 2 - 0.03)])
def carport_screen():
    """Cobogo da garagem para o patio (x = -5,1), com a passagem de pedestres e o batente."""
    p = Piece(); c = WX[1] - 0.1
    breeze(p, 'z', CPZ[0], IZE, c, 0.0, CH, gaps=[(4.0, 5.0)])
    return p
def court_walls():
    """Muretas do patio: na rua (reboco com paineis de cobogo, pilaretes com capa e o vao do portao) e nos fundos (muro com
    portao de servico). Pivo: origem, y = Y0."""
    p = Piece(); y0 = YD - Y0; zf = ZE - 0.1; zr = -ZE + 0.1
    # frente: pilaretes e paineis de cobogo entre eles
    posts = [-4.85, -2.6, -0.85, 0.85, 2.6, 4.85]
    for x in posts:
        p.box('stucco', x - 0.15, x + 0.15, y0, 1.25, zf - 0.15, zf + 0.15); p.box('coping', x - 0.19, x + 0.19, 1.25, 1.31, zf - 0.19, zf + 0.19)
        if abs(x) < 1: p.sphere('stucco_w', 0.1, x, 1.41, zf, 1)
    for (a, b) in ((-4.7, -2.75), (-2.45, -1.0), (1.0, 2.45), (2.75, 4.7)):
        p.box('stucco', a, b, y0, 0.4, zf - 0.1, zf + 0.1); p.box('coping', a, b, 0.4, 0.44, zf - 0.13, zf + 0.13)
        breeze(p, 'x', a, b, zf, 0.44, 1.24, mat='block')
        p.box('coping', a, b, 1.24, 1.28, zf - 0.12, zf + 0.12)
    # fundos: muro liso de 1,8 m com o vao do portao (x 2,0 a 3,0)
    for (a, b) in ((-5.0, 1.88), (3.12, 5.0)):
        p.box('stucco', a, b, y0, 1.75, zr - 0.1, zr + 0.1); p.box('coping', a, b, 1.75, 1.8, zr - 0.13, zr + 0.13)
        p.box('plinth', a, b, 0.0, 0.3, zr + 0.1, zr + 0.114)
    for x in (2.0, 3.0): p.box('stucco', x - 0.12 if x < 2.5 else x, x if x < 2.5 else x + 0.12, y0, 2.1, zr - 0.12, zr + 0.12)
    p.box('stucco', 1.88, 3.12, 2.1, 2.25, zr - 0.12, zr + 0.12)
    return p

# ============================================================================ apartamento (ala oeste, x do mundo, u = z - centro; a ala leste usa as mesmas pecas giradas 180 graus)
FRONT = (P1X[1], IXW[1])                                         # sala/cozinha: x -8,5 a -5,25
BACKZ = (IXW[0], P1X[0])                                         # quarto/banheiro: x -11,75 a -8,6
def rbox(p, mat, x0, x1, y0, y1, u0, u1): p.box(mat, x0, x1, y0, y1, u0, u1)
def bb_x(p, x, a, b, side, h=0.1, mat='trim'):
    """Rodape junto a uma parede em x (face em x, side = +1 para o lado +X)."""
    if b - a > 0.02: u, v = sorted((x, x + side * 0.012)); p.box(mat, u, v, 0.012, h, a, b)
def bb_u(p, u, a, b, side, h=0.1, mat='trim'):
    if b - a > 0.02: u0, u1 = sorted((u, u + side * 0.012)); p.box(mat, a, b, 0.012, h, u0, u1)
def floor_area(p, poly, mat, y1=0.012):
    ext_y(p, mat, poly, 0.0, y1)
def unit_shell():
    """Casca interna do apartamento: pisos (carpete na sala e no quarto, vinil na cozinha, ladrilho no banheiro), parede com as
    portas do quarto e do banheiro, parede entre os dois, armario embutido de correr, rodapes, tomadas, interruptores,
    termostato e luminarias de teto."""
    p = Piece(); xa, xb = IXW; hu = HU
    # pisos
    floor_area(p, sbox(FRONT[0], -hu, FRONT[1], P2U[0]), 'carpet')
    tiles_k(p, sbox(FRONT[0], P2U[0], FRONT[1], hu), 0.0, 0.012, 0.3, 'vinyl_f', 'vinyl_k', ox=0.0, oz=0.0)
    floor_area(p, sbox(BACKZ[0], -hu, BACKZ[1], P2U[0]), 'carpet_b')
    tiles_k(p, sbox(BACKZ[0], P2U[1], BACKZ[1], hu), 0.0, 0.012, 0.15, 'tile_w', 'tile_p')
    # soleiras das portas internas (dentro da parede P1)
    for (a, b) in (BDOOR_U, WDOOR_U): p.box('alu', P1X[0], P1X[1], 0.0, 0.012, a, b)
    # parede P1 (com as 2 portas) e P2
    holes = [(BDOOR_U[0], BDOOR_U[1], 0.0, IDH + 0.03), (WDOOR_U[0], WDOOR_U[1], 0.0, IDH + 0.03)]
    wall_grid(p, 'z', -hu, hu, P1X[0], P1X[1], holes, 0.0, CH, 'plaster')
    wall_grid(p, 'x', BACKZ[0], P1X[0], P2U[0], P2U[1], [], 0.0, CH, 'plaster')
    for (a, b) in (BDOOR_U, WDOOR_U):
        q = Piece(); door_casing(q, b - a, P1X[1] - P1X[0], IDH + 0.03); p.merge(q, rot_y(-90, ((P1X[0] + P1X[1]) / 2, 0, (a + b) / 2)))
    # rodapes (param nas portas, nos armarios e nas quinas)
    dg = [(BDOOR_U[0] - 0.09, BDOOR_U[1] + 0.09), (WDOOR_U[0] - 0.09, WDOOR_U[1] + 0.09)]
    for (a, b) in segs_excl(dg, -hu, 2.4): bb_x(p, P1X[1], a, b, 1)
    for (a, b) in segs_excl([DOOR_U], -hu, KWIN_U[0] - 0.15): bb_x(p, xb, a, b, -1)
    bb_u(p, -hu, FRONT[0] + 0.012, xb - 0.012, 1)
    for (a, b) in segs_excl(dg, -hu, P2U[0]): bb_x(p, P1X[0], a, b, -1)
    bb_x(p, xa, -2.45, P2U[0], 1)
    bb_u(p, P2U[0], xa + 0.012, P1X[0] - 0.012, -1); bb_u(p, -hu, -10.25, P1X[0] - 0.012, 1)
    # banheiro: azulejo ate 1,2 m (1,9 m em volta da banheira) com filete colorido
    tw = 'tile_p'
    for (a, b) in segs_excl([(WDOOR_U[0] - 0.09, WDOOR_U[1] + 0.09)], P2U[1], hu): p.box(tw, P1X[0] - 0.008, P1X[0], 0.012, 1.2, a, b)
    for (a, b, h) in ((P2U[1], JWIN_U[0] - 0.08, 1.9), (JWIN_U[0] - 0.08, JWIN_U[1] + 0.08, 1.38), (JWIN_U[1] + 0.08, 2.32, 1.9), (2.32, hu, 1.2)):
        p.box(tw, xa, xa + 0.008, 0.012, h, a, b)
    p.box(tw, xa + 0.008, -11.0, 0.012, 1.9, P2U[1], P2U[1] + 0.008); p.box(tw, -11.0, P1X[0] - 0.008, 0.012, 1.2, P2U[1], P2U[1] + 0.008)
    p.box(tw, xa + 0.008, P1X[0] - 0.008, 0.012, 1.2, hu - 0.008, hu)
    p.box('accent2', xa + 0.008, xa + 0.014, 1.2, 1.24, 2.32, hu - 0.008); p.box('accent2', -11.0, P1X[0] - 0.008, 1.2, 1.24, P2U[1] + 0.008, P2U[1] + 0.014)
    p.box('accent2', xa + 0.014, P1X[0] - 0.008, 1.2, 1.24, hu - 0.014, hu - 0.008)
    # armario embutido do quarto: testa lateral, testeira, trilhos, 2 portas de correr com puxador embutido, prateleira e cabideiro
    ca, cb, cu0, cu1 = xa, -10.25, -hu, -2.45
    p.box('plaster', cb - 0.05, cb, 0.0, CH, cu0 + 0.003, cu1)
    p.box('plaster', ca, cb - 0.05, 2.2, CH, cu1 - 0.06, cu1)
    p.box('alu', ca, cb - 0.05, 2.18, 2.2, cu1 - 0.12, cu1 - 0.04); p.box('alu', ca, cb - 0.05, 0.012, 0.03, cu1 - 0.12, cu1 - 0.04)
    for (u0, u1, z0) in ((ca + 0.005, ca + 0.76, cu1 - 0.075), (ca + 0.71, cb - 0.055, cu1 - 0.11)):
        p.box('door_int', u0, u1, 0.03, 2.18, z0, z0 + 0.028)
        e_ = u1 - 0.08 if z0 < cu1 - 0.1 else u0 + 0.05
        p.box('dark', e_, e_ + 0.03, 0.95, 1.15, z0 - 0.002, z0); p.box('dark', e_, e_ + 0.03, 0.95, 1.15, z0 + 0.028, z0 + 0.03)
    p.box('dkwood', ca + 0.03, cb - 0.08, 1.75, 1.77, cu0 + 0.03, cu1 - 0.15); seg_cyl(p, 'chrome', (ca + 0.03, 1.68, -2.8), (cb - 0.08, 1.68, -2.8), 0.012, 8)
    # tomadas e interruptores
    for (x, u, ax) in ((-6.0, -hu, 'u+'), (-8.2, -hu, 'u+'), (P1X[1], 0.3, 'x+'), (P1X[0], -0.6, 'x-'), (-6.6, hu, 'u-')):
        if ax[0] == 'u': s = 1 if ax[1] == '+' else -1; a, b = sorted((u, u + s * 0.008)); p.box('cream', x - 0.04, x + 0.04, 0.3, 0.42, a, b)
        else: s = 1 if ax[1] == '+' else -1; a, b = sorted((x, x + s * 0.008)); p.box('cream', a, b, 0.3, 0.42, u - 0.04, u + 0.04)
    for (x, u) in ((P1X[1], BDOOR_U[1] + 0.15), (P1X[1], WDOOR_U[0] - 0.15), (P1X[0], BDOOR_U[1] + 0.15), (P1X[0], WDOOR_U[0] - 0.15)):
        s = 1 if x == P1X[1] else -1; o = 0.008 if (x == P1X[0] and u > P2U[1]) else 0.0      # sobre o azulejo do banheiro
        a, b = sorted((x + s * o, x + s * (o + 0.008))); p.box('cream', a, b, 1.15, 1.27, u - 0.04, u + 0.04)
        a, b = sorted((x + s * (o + 0.008), x + s * (o + 0.016))); p.box('dkwood', a, b, 1.19, 1.23, u - 0.008, u + 0.008)
    a, b = sorted((xb, xb - 0.01)); p.box('cream', a, b, 1.15, 1.27, DOOR_U[1] + 0.12, DOOR_U[1] + 0.2)
    a, b = sorted((xb, xb - 0.03)); p.cham('cream', a, b, 1.45, 1.57, DOOR_U[1] + 0.35, DOOR_U[1] + 0.47, 0.008)   # termostato
    # luminarias de teto (plafons de vidro leitoso e luminaria fluorescente na cozinha)
    for (x, u, r) in ((-6.9, -1.3, 0.22), (-10.2, -1.3, 0.2), (-7.0, 1.4, 0.18), (-6.0, -2.4, 0.14)):
        p.cyl('metal', r + 0.02, CH - 0.03, CH, x, u, 20); lathe(p, 'lamp_glass', [(r, CH - 0.03), (r * 0.8, CH - 0.11), (0.0, CH - 0.12)], x=x, z=u, sec=20)
    return p

# ---------------------------------------------------------------------------- moveis anos 60
def leg(p, mat, x, z, y0, y1, r0=0.02, r1=0.012, lean=(0.0, 0.0), sec=8):
    """Perna conica e levemente inclinada (palito)."""
    lathe_pts = [(x + lean[0] * (1 - t), y0 + (y1 - y0) * t, z + lean[1] * (1 - t)) for t in (0.0, 1.0)]
    p.hull(mat, [(px + r * math.cos(a), py, pz + r * math.sin(a)) for ((px, py, pz), r) in zip(lathe_pts, (r1, r0)) for a in np.linspace(0, 2 * math.pi, sec, endpoint=False)])
def sofa60(mat='fabric_o', L1=2.0):
    """Sofa baixo de linhas retas (pivo: centro da frente embaixo; para +Z): base de madeira, pernas palito, assento de 3
    almofadas, encosto com botoes e bracos finos."""
    p = Piece(); x = L1 / 2; d = 0.82
    p.box('teak', -x, x, 0.18, 0.26, -d, 0.0)
    for sx in (-1, 1):
        for (zz, lz) in ((-0.06, 0.04), (-d + 0.06, -0.04)): leg(p, 'teak', sx * (x - 0.08), zz, 0.0, 0.18, 0.022, 0.012, (sx * 0.03, lz))
    n = 3
    for i in range(n):
        a = -x + 0.1 + i * (2 * x - 0.2) / n + 0.006; b = -x + 0.1 + (i + 1) * (2 * x - 0.2) / n - 0.006
        p.cham(mat, a, b, 0.26, 0.42, -d + 0.18, -0.02, 0.04)
        p.cham(mat, a, b, 0.42, 0.82, -d + 0.02, -d + 0.2, 0.04)
        for (bx_, by) in (((a + b) / 2 - 0.15, 0.56), ((a + b) / 2 + 0.15, 0.56), ((a + b) / 2, 0.7)): p.sphere(mat, 0.018, bx_, by, -d + 0.2, 0)
    for sx in (-1, 1):
        a, b = sorted((sx * x, sx * (x - 0.1))); p.cham(mat, a, b, 0.26, 0.6, -d, -0.02, 0.03); p.box('teak', a, b, 0.6, 0.63, -d, -0.0)
    return p
def coffee_kidney():
    """Mesa de centro de tampo em feijao (boomerang) com pes palito."""
    p = Piece(); pts = []
    for t in np.linspace(0, 2 * math.pi, 40, endpoint=False):
        r = 0.5 + 0.08 * math.cos(2 * t) - 0.06 * math.sin(t); pts.append((r * math.cos(t) * 1.0, 0.55 * r * math.sin(t) + 0.04 * math.cos(3 * t)))
    poly = Polygon(pts); ext_y(p, 'formica', poly, 0.38, 0.4); ext_y(p, 'teak', poly.buffer(0.012), 0.36, 0.38)
    for (x, z) in ((-0.36, -0.12), (0.36, -0.12), (0.0, 0.18)): leg(p, 'teak', x, z, 0.0, 0.36, 0.018, 0.01, (x * 0.12, z * 0.2))
    return p
def armchair60(mat='fabric_t'):
    """Poltrona de braco de madeira (pivo: centro da frente embaixo, para +Z): estrutura de teca, almofadas soltas."""
    p = Piece(); x = 0.38; d = 0.78
    for sx in (-1, 1):
        xx = sx * (x - 0.03)
        p.hull('teak', [(xx + dx, y, z) for dx in (-0.025, 0.025) for (y, z) in ((0.0, -0.06), (0.04, -0.06), (0.62, -0.1), (0.58, -0.12))])
        p.hull('teak', [(xx + dx, y, z) for dx in (-0.025, 0.025) for (y, z) in ((0.0, -d + 0.04), (0.04, -d + 0.04), (0.62, -d + 0.1), (0.58, -d + 0.08))])
        p.box('teak', xx - 0.035, xx + 0.035, 0.58, 0.62, -d + 0.04, -0.04)
    p.box('teak', -x + 0.03, x - 0.03, 0.26, 0.3, -d + 0.08, -0.08)
    p.cham(mat, -x + 0.06, x - 0.06, 0.3, 0.44, -d + 0.12, -0.04, 0.035)
    p.hull(mat, [(sx * (x - 0.06), y, z) for sx in (-1, 1) for (y, z) in ((0.44, -d + 0.14), (0.44, -d + 0.3), (0.86, -d + 0.04), (0.86, -d + 0.18))])
    return p
def tv_console():
    """Movel de TV dos anos 60 (pivo: face de tras embaixo, para +Z): caixa de teca em pernas palito, tela curva, grade de
    alto-falante, botoes; vaso e livros em cima."""
    p = Piece(); x = 0.6; d = 0.45
    for sx in (-1, 1):
        for z in (0.06, d - 0.06): leg(p, 'teak', sx * (x - 0.08), z, 0.0, 0.22, 0.02, 0.012, (sx * 0.03, 0.0))
    p.cham('teak', -x, x, 0.22, 0.86, 0.0, d, 0.012)
    p.cham('tv_s', -x + 0.08, 0.15, 0.32, 0.78, d - 0.005, d + 0.012, 0.03)
    p.box('dark', -x + 0.1, 0.13, 0.34, 0.76, d + 0.012, d + 0.016)
    for k in range(9): yy = 0.36 + k * 0.045; p.box('dkwood', 0.24, x - 0.06, yy, yy + 0.02, d, d + 0.008)
    for yy in (0.72, 0.64): disc_z(p, 'chrome', 0.022, d, d + 0.025, 0.2, yy, 12)
    disc_z(p, 'chrome', 0.015, d, d + 0.02, 0.2, 0.36, 10)
    p.cyl('pot_o', 0.07, 0.86, 1.06, -0.4, 0.22, 14); p.sphere('leaf', 0.1, -0.4, 1.12, 0.22, 1)
    for (i, m) in enumerate(('book_r', 'book_b', 'book_y')): p.box(m, 0.25 + i * 0.05, 0.29 + i * 0.05, 0.86, 1.08 - i * 0.02, 0.12, 0.32)
    return p
def tripod_lamp():
    """Luminaria de pe de tripe com cupula de tambor."""
    p = Piece()
    for k in range(3):
        a = 2 * math.pi * k / 3; seg_cyl(p, 'teak', (0.25 * math.cos(a), 0.0, 0.25 * math.sin(a)), (0.0, 1.1, 0.0), 0.014, 6)
    seg_cyl(p, 'chrome', (0, 1.08, 0), (0, 1.38, 0), 0.01, 6)
    lathe(p, 'cream', [(0.22, 1.35), (0.22, 1.62), (0.2, 1.62)], sec=20); lathe(p, 'lamp_glass', [(0.18, 1.4), (0.0, 1.4)], sec=16)
    return p
def rug_round(r=1.1, mat='fabric_y'):
    p = Piece(); ext_y(p, mat, Point(0, 0).buffer(r, 32), 0.012, 0.02); ext_y(p, 'fabric_o', Point(0, 0).buffer(r, 32).difference(Point(0, 0).buffer(r - 0.08, 32)), 0.02, 0.022)
    return p
def dinette():
    """Mesa redonda de formica com pe central cromado e 3 cadeiras de vinil e tubo cromado (pivo: centro, piso)."""
    p = Piece(); r = 0.45
    p.cyl('formica', r, 0.72, 0.745, 0, 0, 32); ring_y(p, 'chrome', r, r + 0.012, 0.715, 0.75, 0, 0, 32)
    seg_cyl(p, 'chrome', (0, 0.0, 0), (0, 0.72, 0), 0.035, 12)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; seg_cyl(p, 'chrome', (0, 0.02, 0), (0.32 * math.cos(a), 0.01, 0.32 * math.sin(a)), 0.018, 8)
    for k, ang in enumerate((90, 210, 330)):
        q = Piece(); q.cham('vinyl_r', -0.21, 0.21, 0.44, 0.5, -0.2, 0.2, 0.03); q.cham('vinyl_r', -0.2, 0.2, 0.62, 0.86, 0.2, 0.26, 0.03)
        for sx in (-1, 1):
            seg_cyl(q, 'chrome', (sx * 0.19, 0.0, -0.18), (sx * 0.19, 0.44, -0.16), 0.011, 6); seg_cyl(q, 'chrome', (sx * 0.19, 0.0, 0.2), (sx * 0.19, 0.86, 0.22), 0.011, 6)
            seg_cyl(q, 'chrome', (sx * 0.19, 0.44, -0.16), (sx * 0.19, 0.44, 0.21), 0.01, 6)
        p.merge(q, rot_y(ang) @ tr(0, 0, 0.62))
    return p
def bed60(mat='bed_p'):
    """Cama de casal (pivo: centro da cabeceira embaixo, para +Z): cabeceira de teca com 3 paineis, estrado em pernas palito,
    colchao, colcha com barra, 2 travesseiros."""
    p = Piece(); x = 0.72; L1 = 2.02
    p.cham('teak', -x - 0.04, x + 0.04, 0.0, 1.0, 0.0, 0.05, 0.01)
    for k in range(3): a = -x + 0.04 + k * (2 * x - 0.08) / 3 + 0.02; b = -x + 0.04 + (k + 1) * (2 * x - 0.08) / 3 - 0.02; p.cham('dkwood', a, b, 0.5, 0.92, 0.05, 0.065, 0.01)
    p.box('teak', -x, x, 0.22, 0.32, 0.05, L1)
    for sx in (-1, 1): leg(p, 'teak', sx * (x - 0.06), L1 - 0.08, 0.0, 0.22, 0.022, 0.012, (sx * 0.03, 0.03))
    p.cham('bed_w', -x + 0.02, x - 0.02, 0.32, 0.52, 0.06, L1 - 0.02, 0.05)
    p.cham(mat, -x - 0.01, x + 0.01, 0.4, 0.545, 0.6, L1, 0.03); p.box(mat, -x - 0.01, x + 0.01, 0.3, 0.42, L1 - 0.02, L1 + 0.005)
    for sx in (-1, 1): p.box(mat, *sorted((sx * (x + 0.01), sx * (x + 0.02))), 0.28, 0.545, 0.6, L1)
    for sx in (-1, 1): p.cham('bed_w', sx * 0.35 - 0.3, sx * 0.35 + 0.3, 0.52, 0.64, 0.1, 0.5, 0.05)
    return p
def nightstand60():
    p = Piece(); p.cham('teak', -0.24, 0.24, 0.2, 0.55, 0.0, 0.4, 0.01)
    for (sx, z) in ((-1, 0.05), (1, 0.05), (-1, 0.35), (1, 0.35)): leg(p, 'teak', sx * 0.19, z, 0.0, 0.2, 0.016, 0.01, (sx * 0.02, 0.0))
    p.box('dkwood', -0.2, 0.2, 0.32, 0.5, 0.4, 0.41); p.box('brass', -0.05, 0.05, 0.4, 0.42, 0.41, 0.425)
    lathe(p, 'cream', [(0.07, 0.55), (0.09, 0.62), (0.06, 0.78), (0.03, 0.8)], z=0.18, sec=16)
    lathe(p, 'paper', [(0.15, 0.8), (0.12, 1.02), (0.11, 1.02)], z=0.18, sec=18)
    return p
def dresser60():
    """Comoda baixa de 6 gavetas com puxadores de latao e espelho redondo (pivo: face de tras embaixo, para +Z)."""
    p = Piece(); x = 0.6; d = 0.45
    for sx in (-1, 1):
        for z in (0.05, d - 0.05): leg(p, 'teak', sx * (x - 0.06), z, 0.0, 0.18, 0.02, 0.012, (sx * 0.02, 0.0))
    p.cham('teak', -x, x, 0.18, 0.8, 0.0, d, 0.012)
    for i in range(2):
        for j in range(3):
            a = -x + 0.03 + i * (x - 0.03) + 0.005; b = a + x - 0.04; y0 = 0.21 + j * 0.19; y1 = y0 + 0.17
            p.box('dkwood', a, b, y0, y1, d, d + 0.008); p.box('brass', (a + b) / 2 - 0.06, (a + b) / 2 + 0.06, y1 - 0.05, y1 - 0.03, d + 0.008, d + 0.022)
    disc_z(p, 'teak', 0.42, 0.0, 0.03, 0.0, 1.32, 32); disc_z(p, 'mirror', 0.38, 0.03, 0.034, 0.0, 1.32, 32)
    p.box('teak', -0.04, 0.04, 0.8, 0.92, 0.0, 0.03)
    return p
def plant60(h=1.1):
    """Planta (espada-de-sao-jorge) em vaso de ceramica cilindrico sobre suporte de pernas."""
    p = Piece()
    for k in range(3): a = 2 * math.pi * k / 3; seg_cyl(p, 'steel_d', (0.16 * math.cos(a), 0.0, 0.16 * math.sin(a)), (0.12 * math.cos(a), 0.2, 0.12 * math.sin(a)), 0.01, 6)
    lathe(p, 'pot', [(0.13, 0.2), (0.15, 0.5), (0.0, 0.5)], sec=18); p.cyl('mulch', 0.135, 0.48, 0.495, 0, 0, 16)
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.3; r = 0.05 + 0.04 * (k % 3); hh = h * (0.6 + 0.4 * ((k * 7) % 5) / 4)
        bx_, bz = r * math.cos(a), r * math.sin(a); tx, tz = bx_ * 2.2, bz * 2.2
        p.hull('plant', [(bx_ - 0.03, 0.49, bz), (bx_ + 0.03, 0.49, bz), (tx, 0.49 + hh * 0.6 - 0.0, tz + 0.01), (tx * 1.1, 0.49 + hh * 0.6, tz - 0.01), (bx_ * 1.6, 0.49 + hh * 0.3, bz * 1.6 + 0.015)])
    return p
def wall_art(w=0.9, h=0.6):
    """Quadro abstrato (pivo: face da parede, centro): moldura fina e formas geometricas coloridas."""
    p = Piece(); p.box('teak', -w / 2, w / 2, -h / 2, h / 2, 0.0, 0.025); p.box('cream', -w / 2 + 0.03, w / 2 - 0.03, -h / 2 + 0.03, h / 2 - 0.03, 0.025, 0.028)
    disc_z(p, 'accent3', 0.13, 0.028, 0.031, -0.15, 0.05, 24); p.box('accent2', 0.02, 0.3, -0.2, 0.15, 0.028, 0.031); p.box('accent', -0.35, 0.1, -0.22, -0.16, 0.031, 0.034)
    return p

# ---------------------------------------------------------------------------- cozinha e banheiro
def kitchen60():
    """Cozinha em L dos anos 60 (pivo do apartamento; x do mundo, u local): armarios de baixo e de cima com portas lisas e
    puxadores de barra, bancada de formica com friso cromado e espelho de azulejo, pia dupla sob a janela, fogao de 4 bocas
    com espelho de comandos e relogio, coifa, geladeira de cantos arredondados."""
    p = Piece(); uw = HU; d = 0.6; xa, xb = -7.7, IXW[1]; cab = 'cab_t'
    # base ao longo da parede entre apartamentos (u = 3,1), menos o fogao
    RNG = (-7.65, -6.9)
    # trechos de base: (x0, x1) ao longo de u = 3,1
    for (x0, x1) in ((RNG[1] + 0.005, xb - d),):
        p.box('dark', x0, x1, 0.012, 0.1, uw - d + 0.06, uw); p.box(cab, x0, x1, 0.1, 0.86, uw - d + 0.02, uw)
        n = int(round((x1 - x0) / 0.5))
        for i in range(n):
            a = x0 + i * (x1 - x0) / n + 0.004; b = x0 + (i + 1) * (x1 - x0) / n - 0.004
            p.box(cab, a, b, 0.66, 0.84, uw - d + 0.003, uw - d + 0.02); p.box(cab, a, b, 0.11, 0.64, uw - d + 0.003, uw - d + 0.02)
            p.box('chrome', (a + b) / 2 - 0.08, (a + b) / 2 + 0.08, 0.76, 0.775, uw - d - 0.012, uw - d + 0.003); p.box('chrome', b - 0.05, b - 0.035, 0.45, 0.6, uw - d - 0.012, uw - d + 0.003)
    # canto e trecho sob a janela (parede do patio, x = -5,25)
    u0c = KWIN_U[0] - 0.15
    p.box('dark', xb - d + 0.06, xb, 0.012, 0.1, u0c, uw - d); p.box(cab, xb - d + 0.02, xb, 0.1, 0.86, u0c, uw - d + 0.02)
    n = 2
    for i in range(n):
        a = u0c + i * (uw - d - u0c) / n + 0.004; b = u0c + (i + 1) * (uw - d - u0c) / n - 0.004
        p.box(cab, xb - d + 0.003, xb - d + 0.02, 0.11, 0.84, a, b); p.box('chrome', xb - d - 0.012, xb - d + 0.003, 0.45, 0.6, b - 0.05, b - 0.035)
    # bancada de formica com friso cromado
    top = unary_union([sbox(RNG[1], uw - d - 0.03, xb, uw), sbox(xb - d - 0.03, u0c - 0.02, xb, uw)])
    ext_y(p, 'formica', top, 0.86, 0.9)
    for (a, b, c0, c1) in ((RNG[1], xb - d - 0.03, uw - d - 0.036, uw - d - 0.03),):
        p.box('chrome', a, b, 0.855, 0.9, c0, c1)
    p.box('chrome', xb - d - 0.036, xb - d - 0.03, 0.855, 0.9, u0c - 0.02, uw - d - 0.03); p.box('chrome', xb - d - 0.036, xb, 0.855, 0.9, u0c - 0.026, u0c - 0.02)
    # espelho de azulejo
    p.box('tile_b', RNG[0] - 0.75, xb, 0.9, 1.45, uw - 0.008, uw)
    for (a, b) in segs_excl([KWIN_U], u0c - 0.02, uw - 0.008): p.box('tile_b', xb - 0.008, xb, 0.9, 1.45 if True else 1.1, a, b)
    p.box('tile_b', xb - 0.008, xb, 0.9, 1.1, KWIN_U[0], KWIN_U[1])
    # pia dupla de inox sob a janela
    uc = (KWIN_U[0] + KWIN_U[1]) / 2; xs = xb - 0.32
    for du in (-0.22, 0.22): p.box('dark', xs - 0.19, xs + 0.19, 0.84, 0.902, uc + du - 0.19, uc + du + 0.19); p.box('chrome', xs - 0.2, xs + 0.2, 0.9, 0.904, uc + du - 0.2, uc + du - 0.19); p.box('chrome', xs - 0.2, xs + 0.2, 0.9, 0.904, uc + du + 0.19, uc + du + 0.2)
    seg_cyl(p, 'chrome', (xb - 0.06, 0.9, uc), (xb - 0.06, 1.12, uc), 0.016, 8); seg_cyl(p, 'chrome', (xb - 0.06, 1.12, uc), (xb - 0.28, 1.08, uc), 0.013, 8)
    for du in (-0.08, 0.08): seg_cyl(p, 'chrome', (xb - 0.06, 0.9, uc + du), (xb - 0.06, 0.96, uc + du), 0.02, 8)
    # fogao de 4 bocas com espelho de comandos
    a, b = RNG; p.cham('enamel', a, b, 0.0, 0.9, uw - 0.64, uw - 0.005, 0.01)
    p.box('dark', a + 0.03, b - 0.03, 0.12, 0.62, uw - 0.645, uw - 0.64); p.box('chrome', a + 0.06, b - 0.06, 0.66, 0.68, uw - 0.66, uw - 0.645)
    for (x, u) in ((a + 0.19, uw - 0.48), (b - 0.19, uw - 0.48), (a + 0.19, uw - 0.2), (b - 0.19, uw - 0.2)):
        ring_y(p, 'dark', 0.06, 0.1, 0.9, 0.915, x, u, 16); p.cyl('steel_d', 0.05, 0.9, 0.91, x, u, 12)
    p.cham('enamel', a, b, 0.9, 1.2, uw - 0.1, uw - 0.01, 0.01)
    for x in np.linspace(a + 0.1, b - 0.1, 4): seg_cyl(p, 'dark', (x, 0.98, uw - 0.1), (x, 0.98, uw - 0.13), 0.022, 10)
    seg_cyl(p, 'cream', ((a + b) / 2, 1.1, uw - 0.1), ((a + b) / 2, 1.1, uw - 0.104), 0.05, 18)
    # armarios de cima e coifa
    for (x0, x1) in ((-8.45, RNG[0] - 0.02), (RNG[1] + 0.02, xb - 0.002)):
        if x1 - x0 < 0.2: continue
        p.box(cab, x0, x1, 1.45 if x0 > -8 else 1.8, 2.15, uw - 0.34, uw)
        n = max(1, int(round((x1 - x0) / 0.45)))
        for i in range(n):
            u_a = x0 + i * (x1 - x0) / n + 0.004; u_b = x0 + (i + 1) * (x1 - x0) / n - 0.004
            p.box(cab, u_a, u_b, (1.47 if x0 > -8 else 1.82), 2.13, uw - 0.355, uw - 0.34); p.box('chrome', u_b - 0.05, u_b - 0.035, 1.5 if x0 > -8 else 1.85, 1.65 if x0 > -8 else 2.0, uw - 0.37, uw - 0.355)
    p.hull('enamel', [(x, y, u) for x in (a - 0.01, b + 0.01) for (y, u) in ((1.6, uw), (1.6, uw - 0.5), (1.72, uw - 0.5), (1.82, uw))])
    p.box('enamel', a + 0.15, b - 0.15, 1.82, 2.15, uw - 0.25, uw)
    # geladeira de cantos arredondados
    fx0, fx1 = -8.45, -7.7; fu = uw - 0.7
    p.cham('cab_t', fx0, fx1, 0.0, 1.68, fu, uw - 0.02, 0.06); p.box('dark', fx0 + 0.02, fx1 - 0.02, 1.2, 1.205, fu - 0.002, fu + 0.004)
    p.box('chrome', fx1 - 0.08, fx1 - 0.05, 0.9, 1.15, fu - 0.04, fu); p.box('chrome', fx1 - 0.08, fx1 - 0.05, 1.28, 1.42, fu - 0.04, fu)
    p.box('chrome', fx0 + 0.04, fx1 - 0.04, 0.05, 0.09, fu - 0.006, fu)
    # utensilios: torradeira, vasilhas, pano de prato
    p.cham('chrome', -6.6, -6.35, 0.9, 1.08, uw - 0.4, uw - 0.25, 0.02)
    for (i, m) in enumerate(('accent3', 'accent2', 'accent')): p.cyl(m, 0.06 - i * 0.008, 0.9, 1.02 + i * 0.02, -6.0 + i * 0.15, uw - 0.18, 14)
    return p
def bath60():
    """Banheiro rosa dos anos 60 (pivo do apartamento): banheira de louca com saia, registro e chuveiro, varao em L com cortina,
    vaso, gabinete com cuba e espelho de armario, prateleira de vidro, toalheiro e tapete."""
    p = Piece(); xa = IXW[0]; u0, u1 = P2U[1], HU
    # banheira (encostada na parede dos fundos, de u0 a 2,32)
    ta, tb = u0 + 0.008, 2.32; x1 = -11.0
    p.box('porc_p', xa + 0.008, x1, 0.0, 0.12, ta, tb); p.box('porcelain', xa + 0.078, x1 - 0.07, 0.12, 0.13, ta + 0.07, tb - 0.07)
    for (a, b, c, d) in ((xa + 0.008, xa + 0.078, ta, tb), (x1 - 0.07, x1, ta, tb), (xa + 0.078, x1 - 0.07, ta, ta + 0.07), (xa + 0.078, x1 - 0.07, tb - 0.07, tb)):
        p.box('porc_p', a, b, 0.12, 0.5, c, d)
    p.box('porc_p', x1, x1 + 0.012, 0.0, 0.08, ta, tb)
    p.cyl('chrome', 0.025, 0.13, 0.135, -11.4, ta + 0.2, 12)
    seg_cyl(p, 'chrome', (xa + 0.012, 0.62, ta + 0.25), (xa + 0.1, 0.6, ta + 0.25), 0.015, 8)
    for du in (-0.1, 0.1): disc_x(p, 'chrome', 0.035, xa + 0.008, xa + 0.03, 0.8, ta + 0.25 + du, 12)
    seg_cyl(p, 'chrome', (xa + 0.012, 1.85, ta + 0.25), (xa + 0.15, 1.9, ta + 0.25), 0.012, 8); lathe(p, 'chrome', [(0.0, 1.84), (0.05, 1.86), (0.04, 1.92), (0.0, 1.92)], x=xa + 0.17, z=ta + 0.25, sec=12)
    # varao e cortina
    seg_cyl(p, 'chrome', (x1 - 0.02, 2.0, u0 + 0.01), (x1 - 0.02, 2.0, tb + 0.02), 0.012, 8)
    seg_cyl(p, 'chrome', (x1 - 0.02, 2.0, tb + 0.02), (xa + 0.01, 2.0, tb + 0.02), 0.012, 8)
    for k in range(6):
        uu = u0 + 0.05 + k * 0.06; p.box('fabric_t', x1 - 0.06 + (0.02 if k % 2 else 0.0), x1 - 0.03 + (0.02 if k % 2 else 0.0), 0.6, 1.98, uu, uu + 0.06)
    # vaso (encostado na parede entre apartamentos, virado para -u)
    q = wc_p(); p.merge(q, rot_y(180, (-10.25, 0.012, u1 - 0.008)))
    seg_cyl(p, 'chrome', (-9.72, 0.7, u1 - 0.008), (-9.72, 0.7, u1 - 0.1), 0.008, 6); disc_z(p, 'paper', 0.055, u1 - 0.11, u1 - 0.03, -9.72, 0.7, 14)
    # gabinete com cuba (encostado em P2, virado para +u)
    gx0, gx1 = -9.65, -8.95; gu = u0 + 0.5
    p.box('cab_y', gx0, gx1, 0.1, 0.84, u0 + 0.008, gu); p.box('dark', gx0 + 0.04, gx1 - 0.04, 0.012, 0.1, u0 + 0.008, gu - 0.05)
    for (a, b) in ((gx0 + 0.01, (gx0 + gx1) / 2 - 0.004), ((gx0 + gx1) / 2 + 0.004, gx1 - 0.01)):
        p.box('cab_y', a, b, 0.12, 0.8, gu, gu + 0.015); p.box('chrome', (a + b) / 2 - 0.05, (a + b) / 2 + 0.05, 0.72, 0.735, gu + 0.015, gu + 0.03)
    p.box('formica', gx0 - 0.02, gx1 + 0.02, 0.84, 0.87, u0 + 0.008, gu + 0.03); p.box('porc_p', gx0 + 0.15, gx1 - 0.15, 0.83, 0.871, gu - 0.38, gu - 0.06)
    seg_cyl(p, 'chrome', ((gx0 + gx1) / 2, 0.87, u0 + 0.06), ((gx0 + gx1) / 2, 1.0, u0 + 0.06), 0.012, 8); seg_cyl(p, 'chrome', ((gx0 + gx1) / 2, 1.0, u0 + 0.06), ((gx0 + gx1) / 2, 0.98, u0 + 0.2), 0.01, 8)
    p.cham('chrome', gx0 - 0.02, gx1 + 0.02, 1.15, 1.85, u0 + 0.015, u0 + 0.137, 0.008); p.box('mirror', gx0 + 0.01, gx1 - 0.01, 1.18, 1.82, u0 + 0.137, u0 + 0.141)
    p.box('metal', gx0, gx1, 1.95, 2.02, u0 + 0.008, u0 + 0.1); p.box('lamp_glass', gx0 + 0.04, gx1 - 0.04, 1.96, 2.01, u0 + 0.1, u0 + 0.11)
    # toalheiro com toalha (na parede P1, x = -8,6) e tapete
    seg_cyl(p, 'chrome', (P1X[0] - 0.06, 1.1, 2.5), (P1X[0] - 0.06, 1.1, 2.95), 0.01, 8)
    for uu in (2.5, 2.95): p.box('chrome', P1X[0] - 0.07, P1X[0] - 0.008, 1.09, 1.11, uu - 0.01, uu + 0.01)
    p.box('bed_g', P1X[0] - 0.075, P1X[0] - 0.045, 0.6, 1.12, 2.55, 2.9)
    p.cham('fabric_t', -10.7, -10.0, 0.012, 0.025, 1.0, 1.6, 0.01)
    return p
def wc_p():
    """Vaso de louca rosa com caixa acoplada (pivo: face da parede, piso; para +Z)."""
    p = Piece()
    lathe(p, 'porc_p', [(0.13, 0.0), (0.15, 0.1), (0.14, 0.28), (0.2, 0.4), (0.2, 0.42), (0.0, 0.42)], 0.0, 0.42, 0.0, 16)
    p.hull('porc_p', [(x * 0.17, y, z) for x in (-1, 1) for z in (0.17, 0.4) for y in (0.0, 0.42)])
    p.cham('porc_p', -0.2, 0.2, 0.42, 0.8, 0.0, 0.18, 0.03); p.cham('porc_p', -0.21, 0.21, 0.8, 0.83, 0.0, 0.19, 0.01)
    p.cham('porcelain', -0.19, 0.19, 0.425, 0.45, 0.2, 0.62, 0.03); p.box('chrome', 0.1, 0.16, 0.74, 0.76, 0.18, 0.2)
    return p
def door_unit(mat='door'):
    """Porta de entrada dos anos 60: folha lisa pintada com 3 visores escalonados, olho magico, macaneta de bola e chapa de chute."""
    p = Piece(); w = 0.82; h = DH - 0.045; t = 0.045
    slab = tbox(0, w, 0, h, -t / 2, t / 2); lites = [(0.2, 0.36, 1.25, 1.42), (0.33, 0.49, 1.47, 1.64), (0.46, 0.62, 1.69, 1.86)]
    cuts = [tbox(a, b, c, d, -t, t) for (a, b, c, d) in lites]
    p.add(mat, bl_detail(slab, cuts, bevel=0.004, segments=2))
    for (a, b, c, d) in lites: p.box('glass', a - 0.003, b + 0.003, c - 0.003, d + 0.003, -0.003, 0.003)
    for z in (1, -1):
        s0, s1 = sorted((z * t / 2, z * (t / 2 + 0.003))); p.box('brass', 0.04, w - 0.04, 0.03, 0.25, s0, s1)
        p.sphere('brass', 0.03, w - 0.08, 0.98, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.08, 0.98, z * t / 2), (w - 0.08, 0.98, z * (t / 2 + 0.04)), 0.016)
        disc_z(p, 'brass', 0.035, *sorted((z * t / 2, z * (t / 2 + 0.005))), w - 0.08, 0.98, 16)
    disc_z(p, 'brass', 0.012, -t / 2 - 0.006, t / 2 + 0.006, w / 2, 1.55, 10)
    for yy in (0.25, 1.0, 1.75): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def door_flush(w=0.74, h=IDH, t=0.04):
    """Porta interna lisa de compensado (mogno) com macaneta de bola cromada."""
    p = Piece(); p.cham('teak', 0.0, w, 0.0, h, -t / 2, t / 2, 0.004)
    for z in (1, -1):
        p.sphere('chrome', 0.028, w - 0.07, 0.97, z * (t / 2 + 0.05)); p.seg('chrome', (w - 0.07, 0.97, z * t / 2), (w - 0.07, 0.97, z * (t / 2 + 0.04)), 0.014)
        disc_z(p, 'chrome', 0.03, *sorted((z * t / 2, z * (t / 2 + 0.004))), w - 0.07, 0.97, 14)
    for yy in (0.25, 1.7): p.cyl('chrome', 0.007, yy, yy + 0.09, 0.0, t / 2 + 0.002, 8)
    return p
def door_store(w=0.92, h=2.17, t=0.05):
    return door_glass(w, h, t)

# ============================================================================ escritorio e lavanderia (frente do terreo da ala leste, mundo)
OXA, OXB = -IXW[1], -IXW[0]                                       # 5,25 a 11,75
def office_room():
    """Parede entre escritorio e lavanderia com porta, rodapes, quadro de avisos, armario de chaves e relogio."""
    p = Piece(); z0, z1 = OFZ - 0.05, OFZ + 0.05; LD = (10.0, 10.84)
    wall_grid(p, 'x', OXA, OXB, z0, z1, [(LD[0], LD[1], 0.0, IDH + 0.03)], 0.0, CH, 'plaster')
    q = Piece(); door_casing(q, LD[1] - LD[0], z1 - z0, IDH + 0.03); p.merge(q, tr((LD[0] + LD[1]) / 2, 0, OFZ))
    for (a, b) in segs_excl([(LD[0] - 0.09, LD[1] + 0.09)], OXA + 0.012, OXB - 0.012):
        p.box('trim', a, b, 0.012, 0.1, z1, z1 + 0.012); p.box('trim', a, b, 0.012, 0.1, z0 - 0.012, z0)
    for (a, b) in ((OFZ + 0.062, IZE),): p.box('trim', OXA, OXA + 0.012, 0.012, 0.1, a, b); p.box('trim', OXB - 0.012, OXB, 0.012, 0.1, a, b)
    # quadro de avisos de cortica com papeis coloridos (sem texto)
    p.box('teak', 6.0, 7.4, 1.1, 1.9, z1, z1 + 0.025); p.box('dirt', 6.04, 7.36, 1.14, 1.86, z1 + 0.025, z1 + 0.03)
    for (i, (x, y, m)) in enumerate(((6.3, 1.6, 'paper'), (6.7, 1.45, 'accent3'), (7.05, 1.65, 'paper'), (6.5, 1.25, 'accent2'), (7.0, 1.28, 'bed_p'))):
        zo = z1 + 0.03 + i * 0.004; p.box(m, x - 0.11, x + 0.11, y - 0.14, y + 0.14, zo, zo + 0.003); p.sphere('accent', 0.012, x, y + 0.12, zo + 0.006, 0)
    # armario de chaves com ganchos
    p.box('steel', 8.0, 8.6, 1.3, 1.8, z1, z1 + 0.08); p.box('steel_d', 8.02, 8.58, 1.32, 1.78, z1 + 0.08, z1 + 0.085)
    q = wall_clock_s(); p.merge(q, tr(9.2, 2.1, z1))
    return p
def wall_clock_s(r=0.17):
    p = Piece(); disc_z(p, 'accent3', r, 0.0, 0.03, 0, 0, 28); disc_z(p, 'cream', r - 0.025, 0.03, 0.034, 0, 0, 28)
    for k in range(12): a = k * math.pi / 6; seg_cyl(p, 'dark', ((r - 0.04) * math.sin(a), (r - 0.04) * math.cos(a), 0.036), ((r - 0.06) * math.sin(a), (r - 0.06) * math.cos(a), 0.036), 0.005, 4)
    seg_cyl(p, 'dark', (0, 0, 0.038), (0.05, 0.06, 0.038), 0.006, 4); seg_cyl(p, 'dark', (0, 0, 0.04), (-0.02, 0.1, 0.04), 0.004, 4)
    return p
def office_desk():
    """Escrivaninha de aco dos anos 60 (pivo: centro da frente embaixo, para +Z = lado do visitante): tampo de formica,
    gaveteiro, telefone de disco, luminaria, porta-papeis e fichario."""
    p = Piece(); x = 0.75; d = 0.75
    p.box('formica', -x, x, 0.73, 0.76, -d, 0.0); p.box('steel', -x, x, 0.7, 0.73, -d + 0.01, -0.01)
    p.box('steel', -x, -x + 0.42, 0.0, 0.7, -d + 0.01, -0.02); p.box('steel', x - 0.04, x, 0.06, 0.7, -d + 0.01, -0.02)
    p.box('steel', -x + 0.42, x - 0.04, 0.3, 0.7, -0.03, -0.02)
    for j in range(3): y0 = 0.04 + j * 0.22; p.box('steel_d', -x + 0.02, -x + 0.4, y0, y0 + 0.2, -d + 0.005, -d + 0.012); p.box('chrome', -x + 0.15, -x + 0.27, y0 + 0.15, y0 + 0.17, -d - 0.01, -d + 0.005)
    # telefone de disco
    p.cham('accent', 0.3, 0.52, 0.76, 0.84, -0.55, -0.35, 0.03); p.cyl('cream', 0.055, 0.84, 0.85, 0.41, -0.45, 16)
    seg_cyl(p, 'accent', (0.31, 0.88, -0.45), (0.51, 0.88, -0.45), 0.025, 8)
    # luminaria de mesa articulada
    p.cyl('steel_d', 0.07, 0.76, 0.78, -0.55, -0.6, 14); seg_cyl(p, 'steel_d', (-0.55, 0.78, -0.6), (-0.5, 1.1, -0.5), 0.01, 6); seg_cyl(p, 'steel_d', (-0.5, 1.1, -0.5), (-0.35, 1.15, -0.3), 0.01, 6)
    lathe(p, 'accent3', [(0.0, 1.17), (0.05, 1.16), (0.09, 1.06), (0.085, 1.05)], x=-0.35, z=-0.3, sec=14)
    # papeis e pasta
    p.box('paper', -0.15, 0.13, 0.76, 0.765, -0.5, -0.3); p.box('book_b', -0.2, 0.1, 0.765, 0.79, -0.7, -0.52)
    return p
def office_chair60():
    return office_chair('vinyl_r')
def water_cooler():
    p = Piece(); p.cham('enamel', -0.17, 0.17, 0.0, 0.95, -0.17, 0.17, 0.02); p.box('chrome', -0.12, 0.12, 0.95, 0.97, -0.12, 0.12)
    lathe(p, 'jal', [(0.03, 0.97), (0.14, 1.02), (0.15, 1.35), (0.12, 1.4), (0.0, 1.42)], sec=18)
    p.box('dark', -0.1, 0.1, 0.62, 0.82, 0.17, 0.18); p.box('chrome', -0.04, 0.04, 0.84, 0.88, 0.17, 0.2)
    return p
def file_cab60():
    p = Piece(); p.box('cab_t', -0.24, 0.24, 0.0, 1.32, 0.0, 0.62)
    for k in range(4): y = 0.04 + k * 0.32; p.box('cab_t', -0.22, 0.22, y, y + 0.3, 0.62, 0.635); p.box('chrome', -0.07, 0.07, y + 0.2, y + 0.22, 0.635, 0.655); p.box('cream', -0.05, 0.05, y + 0.12, y + 0.16, 0.635, 0.64)
    return p
def bench60(L1=1.8):
    """Banco de espera de ripas de teca sobre estrutura de tubo (pivo: centro de tras, piso; para +Z)."""
    p = Piece(); x = L1 / 2
    for k in range(5): z = 0.08 + k * 0.08; p.box('teak', -x, x, 0.42, 0.45, z, z + 0.065)
    for k in range(3): y = 0.6 + k * 0.1; p.box('teak', -x, x, y, y + 0.07, 0.03, 0.05)
    for sx in (-1, 1):
        xx = sx * (x - 0.12); seg_cyl(p, 'chrome', (xx, 0.0, 0.42), (xx, 0.42, 0.42), 0.014, 8); seg_cyl(p, 'chrome', (xx, 0.0, 0.06), (xx, 0.9, 0.06), 0.014, 8)
        seg_cyl(p, 'chrome', (xx, 0.41, 0.06), (xx, 0.41, 0.44), 0.012, 8)
    return p
def washer():
    """Lavadora de abrir por cima com painel de botoes (pivo: face de tras embaixo, para +Z)."""
    p = Piece(); w = 0.34; d = 0.66
    p.cham('enamel', -w, w, 0.0, 0.92, 0.0, d, 0.02); p.cham('enamel', -w, w, 0.92, 1.12, 0.0, 0.12, 0.015)
    p.box('accent2', -w + 0.03, w - 0.03, 0.96, 1.08, 0.12, 0.125)
    for x in (-0.18, 0.0, 0.18): seg_cyl(p, 'chrome', (x, 1.02, 0.125), (x, 1.02, 0.145), 0.022, 12)
    p.box('dark', -w + 0.04, w - 0.04, 0.919, 0.921, 0.18, d - 0.04); p.box('chrome', -0.1, 0.1, 0.92, 0.935, d - 0.08, d - 0.05)
    p.box('steel', -w + 0.05, -w + 0.15, 0.95, 0.952, 0.07, 0.1)
    return p
def dryer():
    """Secadora de porta redonda com visor e painel."""
    p = Piece(); w = 0.34; d = 0.66
    p.cham('enamel', -w, w, 0.0, 0.92, 0.0, d, 0.02); p.cham('enamel', -w, w, 0.92, 1.12, 0.0, 0.12, 0.015)
    p.box('accent', -w + 0.03, w - 0.03, 0.96, 1.08, 0.12, 0.125)
    for x in (-0.15, 0.15): seg_cyl(p, 'chrome', (x, 1.02, 0.125), (x, 1.02, 0.145), 0.022, 12)
    disc_z(p, 'chrome', 0.24, d, d + 0.03, 0.0, 0.5, 28); disc_z(p, 'glass', 0.18, d + 0.03, d + 0.034, 0.0, 0.5, 24); p.box('chrome', 0.17, 0.21, 0.45, 0.55, d + 0.03, d + 0.06)
    return p
def folding_table():
    p = Piece(); p.box('formica', -0.9, 0.9, 0.86, 0.9, -0.38, 0.38)
    for sx in (-1, 1):
        for sz in (-1, 1): seg_cyl(p, 'chrome', (sx * 0.82, 0.0, sz * 0.3), (sx * 0.82, 0.86, sz * 0.3), 0.016, 8)
        seg_cyl(p, 'chrome', (sx * 0.82, 0.15, -0.3), (sx * 0.82, 0.15, 0.3), 0.012, 6)
    for (x, m) in ((-0.5, 'bed_w'), (-0.2, 'bed_p'), (0.4, 'fabric_t')): p.cham(m, x - 0.15, x + 0.15, 0.9, 0.96, -0.2, 0.2, 0.02)
    p.cham('teak', 0.55, 0.85, 0.9, 1.15, -0.2, 0.2, 0.03)
    return p
def utility_sink():
    p = Piece(); p.cham('enamel', -0.35, 0.35, 0.62, 0.9, 0.0, 0.55, 0.02); p.box('dark', -0.3, 0.3, 0.7, 0.901, 0.05, 0.5)
    for sx in (-1, 1):
        for z in (0.05, 0.5): seg_cyl(p, 'chrome', (sx * 0.3, 0.0, z), (sx * 0.3, 0.62, z), 0.018, 8)
    seg_cyl(p, 'chrome', (0, 0.9, 0.02), (0, 1.12, 0.02), 0.014, 8); seg_cyl(p, 'chrome', (0, 1.12, 0.02), (0, 1.08, 0.22), 0.012, 8)
    p.box('teak', -0.6, 0.6, 1.5, 1.53, 0.0, 0.28)
    for (i, m) in enumerate(('accent2', 'accent3', 'accent', 'paint_b')): p.cham(m, -0.5 + i * 0.26, -0.3 + i * 0.26, 1.53, 1.8 - (i % 2) * 0.06, 0.05, 0.2, 0.01)
    return p

# ============================================================================ piscina (pivo: centro do mundo em x/z, y = piso do patio)
PX0, PX1, PZ0, PZ1 = POOL
def pool_floor_y(z):
    """Fundo da piscina: raso ate z = -1, rampa ate z = -3,5, fundo ate a ponta."""
    if z >= -1.0: return PD[0]
    if z <= -3.5: return PD[1]
    t = (-1.0 - z) / 2.5; return PD[0] + (PD[1] - PD[0]) * t
def pool():
    """Piscina azulejada: paredes e fundo de pastilha azul com faixa escura na linha d'agua, faixa de raia no fundo, degraus
    com bocel, escada de inox, borda de concreto boleada, skimmers, refletores, ralo de fundo e espelho d'agua."""
    p = Piece(); P = sbox(PX0, PZ0, PX1, PZ1); yb = PD[1] - 0.3
    ring = P.buffer(0.25, join_style=2).difference(P)
    ext_y(p, 'concrete', ring, yb, -0.06)
    # borda (capa) e bocel
    cop = P.buffer(0.32, join_style=2).difference(P.buffer(-0.04, join_style=2))
    ext_y(p, 'coping', cop.difference(P), -0.06, 0.02)
    # azulejo das paredes (por dentro do anel de concreto) e faixa da linha d'agua
    tl = P.difference(P.buffer(-0.012, join_style=2))
    ext_y(p, 'pool_t', tl, yb + 0.2, -0.2); ext_y(p, 'accent2', tl, -0.2, -0.06)
    # fundo em 3 trechos (prismas) e azulejo do fundo
    segs = [(PZ1, -1.0), (-1.0, -3.5), (-3.5, PZ0)]
    for (za, zb) in segs:
        ya, yb2 = pool_floor_y(za), pool_floor_y(zb); a, b = sorted((za, zb))
        p.hull('concrete', [(x, y, z) for x in (PX0 + 0.012, PX1 - 0.012) for (y, z) in ((yb, za), (yb, zb), (ya - 0.02, za), (yb2 - 0.02, zb))])
        p.hull('pool_t', [(x, y, z) for x in (PX0 + 0.012, PX1 - 0.012) for (y, z) in ((ya - 0.02, za), (yb2 - 0.02, zb), (ya, za), (yb2, zb))])
        # faixa escura da raia
        p.hull('dark', [(x, y + 0.004, z) for x in (-0.12, 0.12) for (y, z) in ((ya, za if za < PZ1 - 0.5 else PZ1 - 0.6), (yb2, zb if zb > PZ0 + 0.5 else PZ0 + 0.6))] + [(x, y + 0.008, z) for x in (-0.12, 0.12) for (y, z) in ((ya, za if za < PZ1 - 0.5 else PZ1 - 0.6), (yb2, zb if zb > PZ0 + 0.5 else PZ0 + 0.6))])
    p.box('dark', -0.5, 0.5, PD[1] + 0.004, PD[1] + 0.008, PZ0 + 0.5, PZ0 + 0.7)
    # degraus na ponta rasa
    for i, (top, dz) in enumerate(((-0.3, 0.35), (-0.56, 0.7), (-0.82, 1.05))):
        a = PZ1 - dz; p.box('pool_t', PX0 + 0.012, PX1 - 0.012, PD[0] - 0.02, top, a, PZ1 - 0.012)
        p.box('accent2', PX0 + 0.012, PX1 - 0.012, top - 0.05, top + 0.003, a - 0.003, a + 0.05)
    # escada de inox na parede leste da parte funda
    zl = -5.4
    for dz in (-0.25, 0.25):
        z = zl + dz
        seg_cyl(p, 'chrome', (PX1 - 0.12, PD[1] + 0.3, z), (PX1 - 0.12, 0.1, z), 0.022, 10)
        pts = [(PX1 - 0.12 + 0.35 * (1 - math.cos(t)), 0.1 + 0.6 * math.sin(t), z) for t in np.linspace(0, math.pi / 2, 7)] + [(PX1 + 0.45, 0.02, z)]
        for (u, v) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', u, v, 0.022, 10)
    for y in (-0.35, -0.65, -0.95): p.box('chrome', PX1 - 0.16, PX1 - 0.06, y - 0.015, y + 0.015, zl - 0.25, zl + 0.25)
    # refletores, ralo, skimmers e retorno
    for z in (-4.0, 0.5): disc_x(p, 'lamp_glass', 0.1, PX0 + 0.014, PX0 + 0.021, -0.55, z, 16); disc_x(p, 'chrome', 0.12, PX0 + 0.012, PX0 + 0.018, -0.55, z, 16)
    p.box('dark', -0.2, 0.2, PD[1] + 0.003, PD[1] + 0.01, PZ0 + 1.2, PZ0 + 1.6)
    for (x, z) in ((PX0 - 0.2, -2.0), (PX1 + 0.2, 1.0)): p.box('alu', x - 0.12, x + 0.12, 0.02, 0.026, z - 0.12, z + 0.12)
    # espelho d'agua (fino, translucido)
    ext_y(p, 'water', P.buffer(-0.013, join_style=2), -0.14, -0.13)
    return p

# ============================================================================ patio e moveis de fora
def lounger():
    """Espreguicadeira de tubo de aluminio com tiras de vinil e encosto inclinado (pivo: centro, chao; pes para +Z)."""
    p = Piece(); x = 0.32; L1 = 1.9
    for sx in (-1, 1):
        xx = sx * x
        pts = [(xx, 0.0, 0.9), (xx, 0.3, 0.9), (xx, 0.32, -0.3), (xx, 0.85, -0.95), (xx, 0.3, -0.95), (xx, 0.0, -0.95)]
        for (u, v) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'alu', u, v, 0.014, 8)
    for z in (0.9, -0.95): seg_cyl(p, 'alu', (-x, 0.3, z), (x, 0.3, z), 0.012, 8)
    seg_cyl(p, 'alu', (-x, 0.85, -0.95), (x, 0.85, -0.95), 0.012, 8)
    for (i, z) in enumerate(np.arange(-0.25, 0.88, 0.09)): p.box('vinyl_w' if i % 2 else 'accent2', -x, x, 0.305, 0.32, z, z + 0.06)
    for k in range(7):
        t = (k + 0.5) / 7; y = 0.32 + 0.53 * t; z = -0.3 - 0.65 * t
        q = Piece(); q.box('vinyl_w' if k % 2 else 'accent2', -x, x, -0.008, 0.008, -0.035, 0.035); p.merge(q, tr(0, y, z) @ rot_y(0) @ trimesh.transformations.rotation_matrix(math.atan2(0.53, 0.65), [1, 0, 0]))
    for sx in (-1, 1): p.cyl('rubber', 0.04, -0.003, 0.02, sx * x, 0.9, 10); p.cyl('rubber', 0.04, -0.003, 0.02, sx * x, -0.95, 10)
    p.cham('bed_w', -0.27, 0.27, 0.32, 0.4, 0.2, 0.8, 0.03)
    return p
def umbrella_table():
    """Mesa redonda de chapa perfurada com 4 cadeiras de arame e guarda-sol de 8 gomos amarelos e brancos (pivo: centro, chao)."""
    p = Piece(); r = 0.5
    p.cyl('paint_w', r, 0.7, 0.72, 0, 0, 32); ring_y(p, 'paint_w', r, r + 0.02, 0.68, 0.72, 0, 0, 32)
    for k in range(12): a = 2 * math.pi * k / 12; p.cyl('dark', 0.025, 0.72, 0.7205, 0.32 * math.cos(a), 0.32 * math.sin(a), 8)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; seg_cyl(p, 'paint_w', (0.42 * math.cos(a), 0.69, 0.42 * math.sin(a)), (0.55 * math.cos(a), 0.0, 0.55 * math.sin(a)), 0.014, 8)
    seg_cyl(p, 'chrome', (0, 0.0, 0), (0, 2.3, 0), 0.022, 10); p.cyl('steel_d', 0.2, 0.0, 0.05, 0, 0, 16)
    n = 8; R = 1.3; yt, yr = 2.45, 2.05
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        pts = [(0, yt, 0), (0, yt - 0.01, 0)] + [(R * math.cos(a), yr + d, R * math.sin(a)) for a in (a0, a1) for d in (0.0, 0.012)]
        p.hull('umb_y' if k % 2 else 'umb_w', pts)
        am = (a0 + a1) / 2; seg_cyl(p, 'paint_w', (0, 2.2, 0), (R * 0.6 * math.cos(a0), yr + 0.18, R * 0.6 * math.sin(a0)), 0.006, 4)
    p.sphere('paint_w', 0.04, 0, yt + 0.03, 0, 1)
    # babado
    for k in range(n * 2):
        a = 2 * math.pi * (k + 0.5) / (n * 2); x, z = R * math.cos(a), R * math.sin(a)
        p.hull('umb_y' if (k // 2) % 2 else 'umb_w', [(x + dx, y, z + dz) for (dx, dz) in ((-0.25 * math.sin(a), 0.25 * math.cos(a)), (0.25 * math.sin(a), -0.25 * math.cos(a))) for y in (yr - 0.12, yr)] + [(x * 0.995, yr - 0.12, z * 0.995)])
    for ang in (0, 90, 180, 270):
        q = wire_chair(); p.merge(q, rot_y(ang) @ tr(0, 0, 0.82))
    return p
def wire_chair():
    """Cadeira de arame com almofada (pivo: centro da cadeira, chao; olha para -Z)."""
    p = Piece()
    for sx in (-1, 1):
        seg_cyl(p, 'paint_w', (sx * 0.22, 0.0, -0.2), (sx * 0.22, 0.44, -0.18), 0.01, 6); seg_cyl(p, 'paint_w', (sx * 0.22, 0.0, 0.2), (sx * 0.22, 0.44, 0.18), 0.01, 6)
        seg_cyl(p, 'paint_w', (sx * 0.22, 0.44, 0.18), (sx * 0.24, 0.85, 0.26), 0.01, 6)
    for k in range(9):
        x = -0.2 + k * 0.05; seg_cyl(p, 'paint_w', (x, 0.44, -0.2), (x, 0.44, 0.18), 0.005, 4); seg_cyl(p, 'paint_w', (x, 0.44, 0.18), (x * 1.08, 0.85, 0.26), 0.005, 4)
    seg_cyl(p, 'paint_w', (-0.24, 0.85, 0.26), (0.24, 0.85, 0.26), 0.01, 6); seg_cyl(p, 'paint_w', (-0.22, 0.44, -0.2), (0.22, 0.44, -0.2), 0.01, 6)
    p.cham('accent3', -0.2, 0.2, 0.45, 0.5, -0.18, 0.16, 0.02)
    return p
def picnic(mat='pic_t'):
    """Mesa de piquenique de tabuas com bancos presos e pes em X pintados (pivo: centro, chao; comprida em X)."""
    p = Piece(); L1 = 1.8; x = L1 / 2
    for k in range(5): z = -0.38 + k * 0.155; p.cham('teak', -x, x, 0.72, 0.76, z, z + 0.145, 0.006)
    for sz in (-1, 1):
        for k in range(2): z = sz * (0.52 + k * 0.13); p.cham('teak', -x, x, 0.42, 0.455, z - 0.06, z + 0.06, 0.006)
    for sx in (-1, 1):
        xx = sx * (x - 0.25)
        for sz in (-1, 1): p.hull(mat, [(xx + dx, y, z) for dx in (-0.04, 0.04) for (y, z) in ((0.0, sz * 0.7), (0.0, sz * 0.62), (0.72, sz * 0.06), (0.72, -sz * 0.02))])
        p.box(mat, xx - 0.04, xx + 0.04, 0.38, 0.42, -0.76, 0.76); p.box(mat, xx - 0.04, xx + 0.04, 0.68, 0.72, -0.4, 0.4)
    p.box(mat, -x + 0.25, x - 0.25, 0.3, 0.34, -0.03, 0.03)
    return p
def bbq():
    """Churrasqueira de bola (anos 60): bacia e tampa esmaltadas, respiros, alca, 3 pernas com rodas, grelha e mesinha lateral."""
    p = Piece(); R = 0.3; yc = 0.78
    lathe(p, 'accent', [(0.0, yc - R), (R * 0.7, yc - R * 0.7), (R, yc), (R + 0.01, yc + 0.01)], sec=24)
    lathe(p, 'accent', [(R + 0.01, yc + 0.012), (R, yc + 0.03), (R * 0.7, yc + R * 0.7), (0.0, yc + R)], sec=24)
    ring_y(p, 'chrome', R - 0.02, R, yc - 0.005, yc + 0.005, 0, 0, 24)
    for k in range(6): seg_cyl(p, 'chrome', (-R + 0.04 + k * 0.1, yc + 0.002, -0.25), (-R + 0.04 + k * 0.1, yc + 0.002, 0.25), 0.004, 4)
    p.cyl('chrome', 0.05, yc + R - 0.01, yc + R + 0.01, 0, 0, 14); seg_cyl(p, 'teak', (-0.08, yc + R + 0.06, 0), (0.08, yc + R + 0.06, 0), 0.02, 8)
    for sx in (-1, 1): seg_cyl(p, 'chrome', (sx * 0.07, yc + R, 0), (sx * 0.07, yc + R + 0.06, 0), 0.008, 6)
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 2; seg_cyl(p, 'steel_d', (0.2 * math.cos(a), yc - 0.22, 0.2 * math.sin(a)), (0.4 * math.cos(a), 0.08, 0.4 * math.sin(a)), 0.015, 8)
        if k < 2: disc_x(p, 'rubber', 0.08, 0.4 * math.cos(a) - 0.02, 0.4 * math.cos(a) + 0.02, 0.08, 0.4 * math.sin(a), 14)
        else: p.cyl('rubber', 0.02, 0.0, 0.08, 0.4 * math.cos(a), 0.4 * math.sin(a), 8)
    p.cyl('steel', 0.18, 0.25, 0.27, 0, 0, 16)
    p.box('teak', 0.32, 0.68, 0.72, 0.75, -0.18, 0.18); seg_cyl(p, 'steel_d', (0.3, 0.73, 0.0), (0.33, 0.73, 0.0), 0.01, 6)
    return p
def palm(h=7.2, n=11, seed=4):
    """Palmeira: tronco de aneis levemente curvo, bainhas no topo, folhas pinadas arqueadas e cacho de cocos."""
    p = Piece(); rng = np.random.RandomState(seed); lean = 0.35
    def axis(t): return (lean * t * t, h * t, 0.12 * t * t)
    k = 0
    for i in range(int(h / 0.18)):
        t0, t1 = i * 0.18 / h, min(1.0, (i + 1) * 0.18 / h)
        (x0, y0, z0), (x1, y1, z1) = axis(t0), axis(t1); r0 = 0.2 - 0.06 * t0; r1 = 0.2 - 0.06 * t1
        pts = [(x0 + (r0 + 0.012) * math.cos(a), y0, z0 + (r0 + 0.012) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)] + [(x1 + r1 * math.cos(a), y1 - 0.004, z1 + r1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
        p.hull('palm_t', pts)
    tx, ty, tz = axis(1.0)
    p.sphere('bark', 0.22, tx, ty + 0.05, tz, 1)
    for c in range(5): a = 2 * math.pi * c / 5; p.sphere('book_y', 0.07, tx + 0.15 * math.cos(a), ty - 0.12, tz + 0.15 * math.sin(a), 1)
    for f in range(n):
        a = 2 * math.pi * f / n + rng.uniform(-0.15, 0.15); L_ = 2.0 + rng.uniform(-0.25, 0.2); up = rng.uniform(0.3, 0.9)
        ca, sa = math.cos(a), math.sin(a); prev = None
        for s in range(9):
            t = s / 8; d = L_ * t; y = ty + up * math.sin(math.pi * t * 0.7) * 0.9 - 1.6 * t * t
            c = (tx + ca * d, y, tz + sa * d)
            if prev is not None: seg_cyl(p, 'frond', prev, c, 0.018 * (1 - 0.6 * t) + 0.006, 5)
            if 0 < s < 8:
                w = 0.55 * math.sin(math.pi * t) + 0.08
                for side in (-1, 1):
                    lx, lz = -sa * side * w, ca * side * w
                    p.hull('frond' if s % 2 else 'leaf2', [c, (c[0] + ca * 0.12, c[1], c[2] + sa * 0.12), (c[0] + lx + ca * 0.05, c[1] - 0.25 * w, c[2] + lz + sa * 0.05), (c[0] + lx + ca * 0.1, c[1] - 0.25 * w - 0.01, c[2] + lz + sa * 0.1)])
            prev = c
    return p
def bed_edge(L1=1.7, Wd=3.6):
    """Canteiro do patio: guia de concreto, terra coberta de casca e sebe baixa no fundo (pivo: centro, piso do patio)."""
    p = Piece(); x, z = L1 / 2, Wd / 2; b = sbox(-x, -z, x, z)
    ext_y(p, 'concrete', b.difference(b.buffer(-0.08, join_style=2)), -0.1, 0.1)
    ext_y(p, 'mulch', b.buffer(-0.08, join_style=2), -0.1, 0.02)
    for k in range(5):
        zz = -z + 0.5 + k * (2 * z - 1.0) / 4; p.sphere('hedge', 0.32, -x + 0.4, 0.3, zz, 2)
    for (xx, zz) in ((0.25, -1.1), (0.3, 1.2)):
        for j in range(7): a = 2 * math.pi * j / 7; p.hull('plant', [(xx, 0.02, zz), (xx + 0.05 * math.cos(a), 0.02, zz + 0.05 * math.sin(a)), (xx + 0.35 * math.cos(a), 0.35, zz + 0.35 * math.sin(a)), (xx + 0.38 * math.cos(a), 0.33, zz + 0.38 * math.sin(a) + 0.02)])
    return p
def planter60():
    """Floreira de concreto em taca sobre pe com agave."""
    p = Piece()
    lathe(p, 'stucco_w', [(0.18, 0.0), (0.18, 0.06), (0.08, 0.1), (0.08, 0.3), (0.38, 0.45), (0.42, 0.62), (0.0, 0.62)], sec=24)
    p.cyl('mulch', 0.37, 0.62, 0.63, 0, 0, 20)
    for j in range(11):
        a = 2 * math.pi * j / 11; L_ = 0.45 + 0.1 * (j % 3)
        p.hull('cab_t', [(0.04 * math.cos(a), 0.63, 0.04 * math.sin(a)), (0.08 * math.cos(a + 0.3), 0.63, 0.08 * math.sin(a + 0.3)), (L_ * math.cos(a), 0.63 + L_ * 0.8, L_ * math.sin(a)), (0.1 * math.cos(a - 0.3), 0.66, 0.1 * math.sin(a - 0.3))])
    return p
def mailboxes():
    """Caixas de correio em bloco sobre pedestal (2 x 5 portinhas de latao com fenda e fechadura, sem numeros; pivo: centro de
    tras, chao; frente +Z)."""
    p = Piece(); x = 0.6
    p.box('stucco', -0.25, 0.25, 0.0, 0.9, 0.0, 0.3); p.box('coping', -0.3, 0.3, 0.88, 0.92, -0.03, 0.33)
    p.cham('alu', -x, x, 0.92, 1.62, 0.0, 0.36, 0.01); p.box('alu', -x - 0.02, x + 0.02, 1.62, 1.66, -0.02, 0.4)
    for i in range(5):
        for j in range(2):
            a = -x + 0.04 + i * (2 * x - 0.08) / 5 + 0.008; b = -x + 0.04 + (i + 1) * (2 * x - 0.08) / 5 - 0.008; y0 = 0.96 + j * 0.32; y1 = y0 + 0.3
            p.box('brass', a, b, y0, y1, 0.36, 0.368); p.box('dark', a + 0.03, b - 0.03, y1 - 0.08, y1 - 0.06, 0.368, 0.37); disc_z(p, 'steel_d', 0.014, 0.368, 0.375, (a + b) / 2, y0 + 0.08, 10)
    return p
def globe_lamp(h=2.6):
    """Poste de jardim dos anos 60: tubo fino, braco duplo e 2 globos leitosos."""
    p = Piece(); p.cyl('steel_d', 0.12, 0.0, 0.05, 0, 0, 16); seg_cyl(p, 'steel_d', (0, 0.05, 0), (0, h, 0), 0.03, 10)
    for sx in (-1, 1):
        seg_cyl(p, 'steel_d', (0, h - 0.3, 0), (sx * 0.3, h - 0.15, 0), 0.015, 6); p.sphere('lamp_glass', 0.14, sx * 0.3, h - 0.02, 0, 2)
        p.cyl('steel_d', 0.05, h - 0.16, h - 0.13, sx * 0.3, 0, 12)
    p.sphere('lamp_glass', 0.16, 0, h + 0.14, 0, 2); p.cyl('steel_d', 0.05, h, h + 0.02, 0, 0, 12)
    return p
def cobra_lamp(h=7.5):
    """Poste de rua de cabeca de cobra (anos 60): coluna conica de aco galvanizado, braco curvo e luminaria chata."""
    p = Piece(); lathe(p, 'galv', [(0.2, 0.0), (0.2, 0.08), (0.11, 0.12), (0.08, h)], sec=16)
    pts = [(0.0, h), (0.4, h + 0.5), (1.2, h + 0.75), (2.2, h + 0.8)]
    for (u, v) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'galv', (0, u[1], u[0]), (0, v[1], v[0]), 0.05, 10)
    p.hull('galv', [(x, y, z) for x in (-0.18, 0.18) for (y, z) in ((h + 0.75, 2.15), (h + 0.86, 2.15), (h + 0.82, 2.85), (h + 0.72, 2.85))])
    p.box('lamp_glass', -0.14, 0.14, h + 0.7, h + 0.73, 2.25, 2.8)
    return p
def hydrant():
    p = Piece(); lathe(p, 'paint_y', [(0.13, 0.0), (0.13, 0.05), (0.1, 0.08), (0.1, 0.6), (0.12, 0.62), (0.12, 0.66), (0.08, 0.72), (0.0, 0.78)], sec=16)
    for a in (0, 180): q = Piece(); disc_x(q, 'paint_y', 0.05, 0.0, 0.1, 0.45, 0.0, 12); disc_x(q, 'chrome', 0.04, 0.1, 0.13, 0.45, 0.0, 10); p.merge(q, rot_y(a))
    disc_z(p, 'paint_y', 0.06, 0.0, 0.13, 0, 0.4, 12); disc_z(p, 'chrome', 0.05, 0.13, 0.16, 0, 0.4, 10)
    return p
def dumpster():
    p = Piece(); p.cham('accent2', -0.95, 0.95, 0.15, 1.2, -0.6, 0.6, 0.03)
    for s in (-1, 1): p.cham('dark', *(sorted((0.0, s * 0.96))), 1.2, 1.24, -0.62, 0.62, 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1): p.cyl('rubber', 0.07, 0.0, 0.15, sx * 0.8, sz * 0.45, 12)
    for x in (-0.6, 0.0, 0.6): p.box('accent2', x - 0.05, x + 0.05, 0.25, 1.15, 0.6, 0.64)
    return p

# ============================================================================ cobertura
def ac_unit():
    """Condensadora de telhado: base de concreto, caixa de chapa com venezianas, grade redonda do ventilador e tubos de cobre."""
    p = Piece(); p.box('concrete', -0.55, 0.55, 0.03, 0.12, -0.45, 0.45)
    p.cham('enamel', -0.45, 0.45, 0.12, 0.95, -0.38, 0.38, 0.015)
    for s in (-1, 1):
        for k in range(14): y = 0.2 + k * 0.05; p.box('steel', -0.4, 0.4, y, y + 0.02, *sorted((s * 0.38, s * 0.39)))
    ring_y(p, 'steel_d', 0.28, 0.31, 0.95, 0.97, 0, 0, 24)
    for k in range(8): a = k * math.pi / 8; seg_cyl(p, 'steel_d', (0.3 * math.cos(a), 0.965, 0.3 * math.sin(a)), (-0.3 * math.cos(a), 0.965, -0.3 * math.sin(a)), 0.004, 4)
    p.cyl('dark', 0.27, 0.948, 0.952, 0, 0, 24); p.cyl('steel_d', 0.06, 0.95, 0.97, 0, 0, 12)
    for (dz, r) in ((-0.1, 0.012), (0.05, 0.02)):
        seg_cyl(p, 'brass', (0.45, 0.3, dz), (0.6, 0.3, dz), r, 8); seg_cyl(p, 'brass', (0.6, 0.3, dz), (0.6, 0.03, dz), r, 8)
    return p
def vent_stack():
    p = Piece(); seg_cyl(p, 'paint_w', (0, 0.0, 0), (0, 0.55, 0), 0.05, 12); lathe(p, 'membrane', [(0.16, 0.012), (0.06, 0.12), (0.055, 0.14)], sec=12); p.cyl('galv', 0.07, 0.55, 0.6, 0, 0, 12)
    return p
def tv_antenna():
    """Antena de TV de varetas (anos 60): mastro, base, 3 estais e elementos horizontais."""
    p = Piece(); h = 2.8
    p.box('galv', -0.12, 0.12, 0.03, 0.05, -0.12, 0.12); seg_cyl(p, 'galv', (0, 0.05, 0), (0, h, 0), 0.02, 8)
    for k in range(3): a = 2 * math.pi * k / 3; seg_cyl(p, 'steel', (0, h * 0.6, 0), (1.4 * math.cos(a), 0.04, 1.4 * math.sin(a)), 0.004, 4); p.box('galv', 1.4 * math.cos(a) - 0.04, 1.4 * math.cos(a) + 0.04, 0.03, 0.05, 1.4 * math.sin(a) - 0.04, 1.4 * math.sin(a) + 0.04)
    seg_cyl(p, 'galv', (0, h - 0.1, -0.9), (0, h - 0.1, 0.9), 0.012, 6)
    for (k, L_) in enumerate((1.4, 1.25, 1.1, 0.95, 0.8, 0.65, 0.5)):
        z = -0.85 + k * 0.28; seg_cyl(p, 'galv', (-L_ / 2, h - 0.1, z), (L_ / 2, h - 0.1, z), 0.006, 4)
    seg_cyl(p, 'galv', (0, h - 0.5, -0.5), (0, h - 0.5, 0.5), 0.01, 6)
    for (k, L_) in enumerate((0.9, 0.75, 0.6)): z = -0.4 + k * 0.4; seg_cyl(p, 'galv', (-L_ / 2, h - 0.5, z), (L_ / 2, h - 0.5, z), 0.005, 4)
    seg_cyl(p, 'dark', (0, h - 0.6, 0.02), (0.0, 0.05, 0.3), 0.005, 4)
    return p

# ============================================================================ terreno, calcada e rua (pivo: origem, y = 0)
GATE = (-0.7, 0.7); RGATE = (2.0, 3.0)
BEDS = [(-1.75, 7.0), (1.75, 7.0)]                                 # canteiros com as palmeiras
def site():
    """Terreno: gramado nos recuos, patio de concreto com juntas, calcada de placas, guia com rebaixo da garagem, rua de asfalto
    com faixa amarela tracejada, beco de servico nos fundos e acessos de concreto."""
    p = Piece()
    bld = unary_union([wing_box('w'), wing_box('e')])
    pool_fp = sbox(PX0, PZ0, PX1, PZ1).buffer(0.32, join_style=2)
    beds = unary_union([sbox(x - 0.85, z - 1.8, x + 0.85, z + 1.8) for (x, z) in BEDS])
    court = sbox(WX[1], -ZE + 0.2, -WX[1], ZE - 0.2).difference(pool_fp).difference(beds)
    q = paving(court, YD, 1.5, 'concrete'); p.merge(q)
    # faixa sob as muretas (frente e fundos) e gramado/acessos da frente
    walls = unary_union([sbox(WX[1], ZE - 0.2, -WX[1], ZE), sbox(WX[1], -ZE, -WX[1], -ZE + 0.2)])
    ext_y(p, 'concrete', walls, GY, YD)
    drive = sbox(IXW[0], ZE, IXW[1], SWZ0); walk = sbox(GATE[0], ZE, GATE[1], SWZ0)
    front = sbox(SX0, ZE, SX1, SWZ0).difference(drive).difference(walk)
    ext_y(p, 'grass', front.difference(bld), GY, YD - 0.03)
    p.merge(paving(drive, YD, 1.2, 'concrete')); p.merge(paving(walk, YD, 0.7, 'concrete'))
    # calcada, guia (rebaixada na garagem), rua e faixa
    p.merge(paving(sbox(SX0, SWZ0, SX1, SWZ1), YD, 1.0, 'concrete'))
    cut = (IXW[0], IXW[1])
    for (a, b) in segs_excl([cut], SX0, SX1): ext_y(p, 'curb', sbox(a, SWZ1, b, CZ), GY, YD)
    p.hull('curb', [(x, y, z) for x in (cut[0], cut[1]) for (y, z) in ((GY, SWZ1), (GY, CZ), (YD, SWZ1), (0.02, CZ))])
    ext_y(p, 'asphalt', sbox(SX0, CZ, SX1, SZ1S), GY, 0.0)
    for x in np.arange(SX0 + 0.5, SX1 - 1.0, 3.0): ext_y(p, 'line_y', sbox(x, 15.35, x + 1.5, 15.47), 0.0, 0.003)
    # recuos laterais (gramado) e fundos (cascalho, acesso ao portao e beco)
    sides = unary_union([sbox(SX0, -ZE, WX[0], ZE), sbox(-WX[0], -ZE, SX1, ZE)])
    ext_y(p, 'grass', sides, GY, YD - 0.03)
    rear = sbox(SX0, -11.0, SX1, -ZE).difference(bld); rwalk = sbox(RGATE[0] - 0.1, -11.0, RGATE[1] + 0.1, -ZE)
    ext_y(p, 'gravel', rear.difference(rwalk), GY, YD - 0.02); p.merge(paving(rwalk, YD, 0.7, 'concrete'))
    ext_y(p, 'asphalt', sbox(SX0, SZ0S, SX1, -11.0), GY, 0.0)
    return p
def side_wall(L1=21.0):
    """Muro de divisa de blocos de concreto aparente em amarracao, com capa (pivo: centro, chao; corre em Z)."""
    p = Piece(); z = L1 / 2; g = 0.006
    for j in range(6):
        off_ = 0.2 if j % 2 else 0.0; y0 = j * 0.2 + (g if j else 0.0); y1 = (j + 1) * 0.2 - g
        for k in range(int(L1 / 0.4) + 2):
            a = max(-z, -z - off_ + k * 0.4 + g); b = min(z, -z - off_ + (k + 1) * 0.4 - g)
            if b - a > 0.02: p.box('block', -0.1, 0.1, y0, y1, a, b)
    p.box('grout', -0.095, 0.095, 0.0, 1.2, -z + 0.005, z - 0.005); p.box('coping', -0.13, 0.13, 1.2, 1.26, -z, z)
    return p

# ============================================================================ portao
def gate(w=1.38, h=1.2, t=0.04):
    """Portao de tubo de aco pintado: quadro, barras verticais, 2 aros decorativos e trinco (pivo: dobradica, embaixo)."""
    p = Piece(); m = 'steel_d'
    for x in (0.02, w - 0.02): seg_cyl(p, m, (x, 0.05, 0), (x, h, 0), 0.02, 8)
    for y in (0.08, h - 0.03): seg_cyl(p, m, (0.02, y, 0), (w - 0.02, y, 0), 0.016, 8)
    for x in np.arange(0.12, w - 0.08, 0.1):
        cut = any(abs(x - cx) < 0.18 for cx in (w * 0.3, w * 0.7))
        if cut: seg_cyl(p, m, (x, 0.08, 0), (x, 0.42, 0), 0.008, 6); seg_cyl(p, m, (x, 0.78, 0), (x, h - 0.03, 0), 0.008, 6)
        else: seg_cyl(p, m, (x, 0.08, 0), (x, h - 0.03, 0), 0.008, 6)
    for cx in (w * 0.3, w * 0.7):
        pts = [(cx + 0.18 * math.cos(a), 0.6 + 0.18 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 17)]
        for (u, v) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'accent', (u[0], u[1], 0), (v[0], v[1], 0), 0.012, 6)
        p.sphere('accent', 0.04, cx, 0.6, 0, 1)
    p.box('chrome', w - 0.1, w - 0.03, 0.9, 0.96, -0.04, 0.04)
    for y in (0.2, h - 0.2): p.cyl('steel_d', 0.03, y - 0.04, y + 0.04, 0.0, 0.0, 10)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def put_u(n, wing, k, zc, x, y, u, ry=0, tags=(), door=None):
    """Peca do apartamento: (x do mundo, u = z - centro) da ala oeste; na leste gira 180 graus em volta do eixo do patio."""
    if wing == 'w': put(n, x, LV[k] + y, zc + u, ry, tags, door)
    else: put(n, -x, LV[k] + y, zc - u, ry + 180, tags, door)
pieces = {
    'site': site(), 'ground_slab': ground_slab(), 'slab_1': slab_1(), 'roof': roof(),
    'envelope_w_ground': envelope('w', 'g'), 'envelope_w_upper': envelope('w', 't'), 'envelope_e_ground': envelope('e', 'g'), 'envelope_e_upper': envelope('e', 't'),
    'gallery': gallery(), 'stair_ext': stair_ext(), 'carport': carport(), 'carport_screen': carport_screen(), 'court_walls': court_walls(),
    'unit_shell': unit_shell(), 'kitchen': kitchen60(), 'bathroom': bath60(),
    'sofa_o': sofa60('fabric_o'), 'sofa_t': sofa60('fabric_t'), 'coffee_table': coffee_kidney(), 'armchair_t': armchair60('fabric_t'), 'armchair_m': armchair60('fabric_m'),
    'tv_console': tv_console(), 'floor_lamp': tripod_lamp(), 'rug_y': rug_round(0.95, 'fabric_y'), 'rug_m': rug_round(0.95, 'fabric_m'), 'dinette': dinette(),
    'bed_p': bed60('bed_p'), 'bed_g': bed60('bed_g'), 'nightstand': nightstand60(), 'dresser': dresser60(), 'plant': plant60(), 'wall_art': wall_art(),
    'door_unit': door_unit('door'), 'door_unit_t': door_unit('door_t'), 'door_int': door_flush(0.74, IDH - 0.012), 'door_office': door_glass(0.98, 2.17, 0.05),
    'gate': gate(1.38, 1.2), 'gate_rear': gate(0.98, 1.75),
    'office_room': office_room(), 'office_desk': office_desk(), 'office_chair': office_chair('vinyl_r'), 'guest_chair': guest_chair('vinyl_r'),
    'water_cooler': water_cooler(), 'file_cabinet': file_cab60(), 'bench_office': bench60(1.4), 'washer': washer(), 'dryer': dryer(),
    'folding_table': folding_table(), 'utility_sink': utility_sink(),
    'pool': pool(), 'lounger': lounger(), 'umbrella_table': umbrella_table(), 'picnic_t': picnic('pic_t'), 'picnic_m': picnic('pic_m'), 'bbq': bbq(),
    'palm': palm(8.0), 'bed_planting': bed_edge(1.7, 3.6), 'planter': planter60(), 'mailboxes': mailboxes(), 'garden_lamp': globe_lamp(),
    'street_lamp': cobra_lamp(7.0), 'hydrant': hydrant(), 'trash_can': trash_can(), 'dumpster': dumpster(), 'side_wall': side_wall(21.0),
    'ac_unit': ac_unit(), 'vent_stack': vent_stack(), 'tv_antenna': tv_antenna(),
    'car_wagon_t': car('car_t', 'wagon'), 'car_sedan_p': car('car_p', 'sedan'), 'car_coupe_y': car('car_y', 'coupe'),
    'player_scale_ref': player_ref()}

# ============================================================================ montagem
G = ['predio']; J = ['rua']; R = G + ['roof']
def fl(k): return G + [f'floor{k}']
put('site', 0, 0, 0, 0, J); put('ground_slab', 0, Y0, 0, 0, fl(0)); put('slab_1', 0, LV[1], 0, 0, fl(1)); put('roof', 0, LV[2], 0, 0, R)
for wing in ('w', 'e'):
    put(f'envelope_{wing}_ground', 0, Y0, 0, 0, fl(0) + ['ext']); put(f'envelope_{wing}_upper', 0, LV[1], 0, 0, fl(1) + ['ext'])
for ry in (0, 180): put('gallery', 0, LV[1], 0, ry, fl(1) + ['ext']); put('stair_ext', 0, 0, 0, ry, J)
put('carport', 0, Y0, 0, 0, fl(0)); put('carport_screen', 0, Y0, 0, 0, fl(0) + ['ext']); put('court_walls', 0, Y0, 0, 0, J)
# apartamentos
n_ = 0
for wing in ('w', 'e'):
    for k in (0, 1):
        for zc in UZ:
            if k == 0 and zc > 3.0: continue                       # frente do terreo: garagem (oeste) e escritorio (leste)
            t = fl(k); alt = n_ % 2; n_ += 1
            put_u('unit_shell', wing, k, zc, 0, 0, 0, 0, t); put_u('kitchen', wing, k, zc, 0, 0, 0, 0, t); put_u('bathroom', wing, k, zc, 0, 0, 0, 0, t)
            put_u('sofa_t' if alt else 'sofa_o', wing, k, zc, -6.95, 0.012, -0.42, 180, t)
            put_u('coffee_table', wing, k, zc, -6.95, 0.012, -1.35, 0, t); put_u('rug_m' if alt else 'rug_y', wing, k, zc, -7.0, 0.0, -1.4, 0, t)
            put_u('armchair_m' if alt else 'armchair_t', wing, k, zc, -7.7, 0.012, -1.0, 90, t)
            put_u('tv_console', wing, k, zc, -6.95, 0.012, -HU + 0.012, 0, t); put_u('floor_lamp', wing, k, zc, -8.22, 0.012, 0.62, 0, t)
            put_u('wall_art', wing, k, zc, P1X[1], 1.6, -1.0, 90, t); put_u('plant', wing, k, zc, -5.62, 0.012, 0.45, 0, t)
            put_u('dinette', wing, k, zc, -6.8, 0.012, 1.45, 0, t)
            put_u('bed_g' if alt else 'bed_p', wing, k, zc, -10.2, 0.012, P2U[0] - 0.012, 180, t)
            put_u('nightstand', wing, k, zc, -11.3, 0.012, P2U[0] - 0.012, 180, t); put_u('dresser', wing, k, zc, P1X[0] - 0.012, 0.012, -1.0, -90, t)
            put_u('door_unit_t' if alt else 'door_unit', wing, k, zc, WX[1] - 0.13, 0.013, DOOR_U[0] + 0.04, -90, t, door=-90)
            put_u('door_int', wing, k, zc, (P1X[0] + P1X[1]) / 2, 0.012, BDOOR_U[0] + 0.03, -90, t, door=-90)
            put_u('door_int', wing, k, zc, (P1X[0] + P1X[1]) / 2, 0.012, WDOOR_U[0] + 0.03, -90, t, door=-90)
# escritorio e lavanderia (frente do terreo da ala leste)
t = fl(0); y = Y0 + 0.012
put('office_room', 0, Y0, 0, 0, t); put('office_desk', 9.4, y, 7.8, 0, t); put('office_chair', 9.4, y, 6.75, 0, t)
for x in (9.0, 9.8): put('guest_chair', x, y, 8.45, 180, t)
put('water_cooler', 5.62, y, 8.9, 90, t); put('file_cabinet', OXB, y, 7.3, -90, t); put('file_cabinet', OXB, y, 7.8, -90, t)
put('bench_office', 5.27, y, 7.4, 90, t); put('plant', 11.3, y, 9.1, 0, t)
put('door_office', 8.01, y, ZE - 0.11, 0, t, door=90); put('door_int', 10.03, y, OFZ, 0, t, door=90)
put('door_unit_t', -WX[1] + 0.13, Y0 + 0.013, 3.74, -90, t, door=90)
for z in (3.75, 4.45, 5.15): put('washer', OXB - 0.012, y, z, -90, t)
for x in (6.5, 7.2, 7.9): put('dryer', x, y, OFZ - 0.062, 180, t)
put('folding_table', 8.7, y, 4.4, 0, t); put('utility_sink', 6.4, y, PWZ[0] + PW / 2 + 0.012, 0, t)
# garagem
put('car_wagon_t', -10.1, Y0, 6.6, 180, fl(0))
# patio
C = J + ['patio']
put('pool', 0, YD, 0, 0, C)
for (x, z) in BEDS: put('bed_planting', x, YD, z, 0 if x < 0 else 180, C); put('palm', x, YD + 0.02, z, 0 if x < 0 else 180, C + ['roof'])
put('gate', GATE[0] + 0.01, YD, ZE - 0.1, 0, C, door=90); put('gate_rear', RGATE[0] + 0.01, YD, -ZE + 0.1, 0, C, door=-90)
for z in (-4.3, -6.2): put('lounger', -2.6, YD, z, 0, C)
for z in (-5.2, -7.1): put('lounger', 2.6, YD, z, 0, C)
put('umbrella_table', 2.9, YD, 4.3, 0, C + ['roof']); put('picnic_t', -2.6, YD, -8.4, 0, C); put('picnic_m', 0.4, YD, -8.4, 0, C); put('bbq', 3.1, YD, -8.9, 0, C)
for (x, z) in ((-2.2, 4.6), (-4.3, -9.0), (4.3, -9.0)): put('planter', x, YD, z, 0, C)
put('mailboxes', 3.4, YD, 9.23, 180, C); put('garden_lamp', -3.3, YD, 8.9, 0, C)
for x in (-1.2, 1.2): put('garden_lamp', x, YD, -7.3, 0, C)
# rua, beco e divisas
for x in (-9.0, 9.0): put('street_lamp', x, YD, 12.2, 0, J + ['roof'])
put('hydrant', 4.5, YD, 12.1, 0, J); put('trash_can', -6.5, 0.0, -11.6, 0, J); put('trash_can', -5.8, 0.0, -11.6, 0, J); put('dumpster', 6.5, 0.0, -12.0, 0, J)
put('car_sedan_p', -3.0, 0.0, 13.9, 90, J); put('car_coupe_y', 6.0, 0.0, 13.9, -90, J)
for x in (-15.8, 15.8): put('side_wall', x, YD - 0.03, -0.2, 0, J)
# cobertura
for wing in ('w', 'e'):
    s = 1 if wing == 'w' else -1
    for zc in UZ:
        put('ac_unit', s * -10.3, LV[2] + 0.03, s * (zc + 1.2), 0 if s > 0 else 180, R)
        put('vent_stack', s * -10.0, LV[2], s * (zc + 2.0), 0, R); put('vent_stack', s * -6.4, LV[2], s * (zc + 2.8), 0, R)
    put('tv_antenna', s * -7.6, LV[2], s * -1.6, 0, R)
put('player_scale_ref', -13.0, YD, 11.4, 0, J); put('player_scale_ref', -6.2, LV[1], 0.8, 0, fl(1))

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'ground_floor': Y0, 'storey_height': H, 'levels': LV, 'slab': ST, 'courtyard_floor': YD,
                       'wings': {'west': {'x': list(WX), 'z': [-ZE, ZE]}, 'east': {'x': [-WX[1], -WX[0]], 'z': [-ZE, ZE]}}, 'wall': T,
                       'units': {'centers_z': list(UZ), 'inner_width': UW, 'east_wing': 'west pieces rotated 180 degrees about the origin'},
                       'gallery': {'x': list(GX)}, 'pool': {'x': [PX0, PX1], 'z': [PZ0, PZ1], 'depth': list(PD)},
                       'site': {'x': [SX0, SX1], 'z': [SZ0S, SZ1S]}, 'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
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
