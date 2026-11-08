"""Kit 38: mansao de tijolo com torreao (estilo rainha Ana), em ALTO DETALHE (scripts/detalhe/detalhe.py).
Casa de 14 x 12 m e 2 andares sobre embasamento de pedra, tijolo vermelho com cunhais de pedra, faixa entre andares, janelas de
guilhotina com peitoril e verga de pedra com fecho, cornija com modilhoes, telhado de 4 aguas de ardosia com rincoes, mirante plano
com gradil de ferro, 5 trapeiras e 3 chamines altas com coroamento. Torreao de 12 faces na quina da frente, com 3 niveis e
telhado conico com pinaculo de cobre. Varanda da frente com colunas, balaustrada e escada; porte-cochere lateral sobre a entrada
de carros; os dois tetos sao sacadas do 2o andar.
Dentro: hall central com piso xadrez de marmore e escadaria com balaustres torneados; sala de estar, sala de jantar e cozinha com
fogao a lenha, biblioteca com o torreao; no 2o andar, 3 quartos com cama de dossel e um banheiro com banheira de pes. Lareiras.
Fora: jardim com chafariz de 2 bacias, caminhos de tijolo, gradil de ferro com pilares de tijolo e lanternas, portoes, entrada de
cascalho, cerca viva, um galpao de jardim no fundo.
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
configurar(cores={'brick': (150, 62, 48), 'stone_t': (212, 200, 176), 'trim': (240, 234, 220), 'sash': (246, 242, 232), 'frame': (240, 234, 220),
                  'shingles': (78, 84, 92), 'ridge': (58, 62, 68), 'plaster': (236, 226, 204), 'ceil': (244, 240, 230), 'oak': (156, 108, 64),
                  'dkwood': (96, 56, 38), 'marble_w': (236, 232, 224), 'marble_k': (44, 42, 44), 'tile': (230, 230, 224), 'tile_k': (60, 70, 66),
                  'iron': (36, 36, 38), 'brass': (196, 160, 82), 'copper': (96, 156, 132), 'velvet': (130, 34, 44), 'velvet_g': (52, 92, 70),
                  'linen': (242, 238, 226), 'porcelain': (244, 244, 240), 'door': (70, 44, 34), 'door_int': (226, 212, 184), 'gutter': (232, 224, 204),
                  'gravel': (196, 186, 166), 'grass': (100, 146, 70), 'hedge': (60, 100, 50), 'leaf': (86, 130, 62), 'leaf2': (110, 146, 70),
                  'bark': (96, 72, 52), 'mulch': (88, 64, 46), 'water': (86, 140, 170), 'concrete': (184, 180, 172), 'paver': (164, 84, 62),
                  'membrane': (120, 120, 118), 'deck': (150, 140, 126), 'rug': (128, 46, 44), 'rug2': (56, 70, 110), 'book_r': (140, 40, 36),
                  'book_g': (46, 90, 62), 'book_b': (44, 60, 110), 'flower': (210, 70, 90), 'flower_y': (236, 196, 60), 'siding': (196, 182, 150),
                  'stove': (30, 30, 32), 'cream': (240, 232, 210), 'clay': (170, 90, 60), 'lamp_glass': (255, 236, 190)},
           texturas={'brick': 'brick', 'stone_t': 'stone', 'shingles': 'shingles', 'plaster': 'plaster', 'oak': 'planks', 'dkwood': 'planks',
                     'gravel': 'render', 'grass': 'render', 'paver': 'brick', 'concrete': 'render', 'membrane': 'render', 'deck': 'planks',
                     'siding': 'planks'},
           out=OUT)
D.METAL.update({'iron', 'brass', 'copper'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.3; SLAB = 0.3; t_ = 0.14                    # modulo, parede externa (alvenaria), laje, parede interna
Y0 = 0.75; HF = 3.3; Y1 = Y0 + HF; YE = Y1 + HF            # piso do terreo (5 degraus), piso do 2o andar, topo das paredes
HX, HZ = 7.0, 6.0; XI, ZI = HX - T, HZ - T                 # casa: x de -7 a 7, z de -6 a 6, frente para +Z
CEIL = HF - SLAB                                           # pe-direito livre
WT = 0.1                                                   # topo do embasamento de pedra (acima do piso)
ANG = 45.0; K = 1.0                                        # telhado de 4 aguas a 45 graus
MF, MB = 0.45, -4.0                                        # beiral (alem da face da parede) e borda do mirante (recuo)
RISE = K * (MF - MB)                                       # altura do mirante sobre o topo das paredes
TV = 0.06; BUMP = 0.018; configurar_telhado(TV, BUMP, ANG); CS = math.cos(math.radians(ANG))
TC = (HX, HZ); TR = 2.0                                    # torreao: centro na quina da frente/leste, raio externo (12 faces)
NSIDE = 12; HA = math.pi / NSIDE; TAP = TR * math.cos(HA)  # meio angulo e apotema externo
TTOP = 2.7                                                 # altura do 3o nivel do torreao acima de YE
WIN0 = (-0.5, 0.5, 0.75, 2.55)                             # vao das janelas de guilhotina do terreo (x0, x1, peitoril, verga)
WIN1 = (-0.5, 0.5, 0.65, 2.4)                              # 2o andar (a verga fica abaixo do friso da cornija)
WIN = WIN0
HALL = 2.0                                                 # paredes do hall central em x = -2 e 2
ZS0, NS = 1.2, 17; RS = HF / NS; GS = 0.27                 # escadaria: inicio, degraus, espelho e piso
ZS1 = ZS0 - (NS - 1) * GS                                  # chegada no 2o andar
XS0, XS1 = 0.63, HALL - t_ / 2                             # largura da escadaria (encostada na parede leste do hall)
STAIR_HOLE = sbox(XS0, ZS1, XS1 - 0.001, ZS0)

# ============================================================================ ferramentas
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
def poly_ngon(cx, cz, r, n=NSIDE, a0=0.0):
    return Polygon([(cx + r * math.cos(a0 + 2 * math.pi * k / n), cz + r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)])

# ============================================================================ janelas e portas de fachada
STONE_SILL = lambda y0: [(-0.06, y0 - 0.1), (0.07, y0 - 0.1), (0.085, y0 - 0.085), (0.085, y0 - 0.03), (-0.06, y0 + 0.01)]
def stone_head(p, a, b, y1, h=0.32, key=True):
    """Verga de pedra (arco plano) com fecho saliente, sobre o vao (a, b) com topo do vao em y1."""
    p.cham('stone_t', a - 0.14, b + 0.14, y1, y1 + h, 0.0, 0.025, 0.006)
    for x in np.linspace(a - 0.14, b + 0.14, 6)[1:-1]: p.box('dark', x - 0.004, x + 0.004, y1 + 0.02, y1 + h - 0.02, 0.025, 0.027)
    if key:
        xm = (a + b) / 2
        p.hull('stone_t', [(xm + s * w, y, z) for (w, y) in ((0.09, y1 - 0.02), (0.13, y1 + h + 0.05)) for s in (-1, 1) for z in (0.0, 0.05)])
def sash_window(p, a, b, y0, y1, inner=True, lites=2):
    """Janela de guilhotina (2 sobre 2) no vao (a, b, y0, y1) de parede com face externa em z = 0: caixilho de madeira recuado,
    folhas com montante central, trilho de encontro, puxador, peitoril de pedra, verga com fecho e, por dentro, peitoril de madeira e guarnicao."""
    f = 0.06; z0, z1 = -0.2, -0.06
    p.box('frame', a, a + f, y0, y1, z0, z1); p.box('frame', b - f, b, y0, y1, z0, z1); p.box('frame', a + f, b - f, y1 - f, y1, z0, z1)
    p.box('frame', a + f, b - f, y0, y0 + 0.04, z0, z1)
    mid = (y0 + 0.04 + y1 - f) / 2
    sash(p, a + f, b - f, y0 + 0.04, mid + 0.02, -0.17, -0.13, lites, 0.07)
    sash(p, a + f + 0.004, b - f - 0.004, mid - 0.02, y1 - f, -0.12, -0.08, lites, 0.05)
    p.box('brass', (a + b) / 2 - 0.04, (a + b) / 2 + 0.04, mid + 0.0, mid + 0.02, -0.13, -0.12)
    prof_x(p, 'stone_t', a - 0.08, b + 0.08, STONE_SILL(y0))
    stone_head(p, a, b, y1)
    if inner:
        p.cham('oak', a - 0.06, b + 0.06, y0 - 0.03, y0 + 0.004, -T - 0.05, -0.2, 0.006)
        for x in (a, b):
            s = -1 if x == a else 1; c, d = sorted((x - s * 0.004, x + s * 0.09))
            prof_y(p, 'trim', y0 - 0.15, y1 + 0.09, crect(c, d, -T - 0.022, -T + 0.001, 0.005, (1, 1, 0, 0)))
        prof_x(p, 'trim', a - 0.09, b + 0.09, crect(-T - 0.022, -T + 0.001, y1 - 0.004, y1 + 0.09, 0.005, (1, 0, 0, 1)))
        p.box('trim', a - 0.04, b + 0.04, y0 - 0.15, y0 - 0.03, -T - 0.016, -T)
def front_door_frame(p, a, b, h):
    """Porta da frente com 2 janelas laterais (bandeiras de baixo com almofada) e bandeira em cima: caixilhos e vidros."""
    z0, z1 = -0.2, -0.06; f = 0.06
    for (x0, x1) in ((a, a + f), (-0.51, -0.47), (0.47, 0.51), (b - f, b)): p.box('frame', x0, x1, 0.0, h, z0, z1)
    p.box('frame', a + f, b - f, h - f, h, z0, z1); p.box('frame', a, b, 2.32, 2.38, z0, z1)
    for (c, d) in ((a + f, -0.51), (0.51, b - f)):
        p.box('frame', c, d, 0.0, 0.8, z0 + 0.02, z1 - 0.02); p.box('trim', c + 0.05, d - 0.05, 0.12, 0.7, z1 - 0.02, z1 - 0.01)
        p.box('glass', c, d, 0.8, 2.32, -0.133, -0.127)
        for y in (1.3, 1.82): p.box('frame', c, d, y - 0.012, y + 0.012, -0.14, -0.12)
    p.box('glass', a + f, b - f, 2.38, h - f, -0.133, -0.127)
    for x in np.linspace(a + f, b - f, 6)[1:-1]: p.box('frame', x - 0.012, x + 0.012, 2.38, h - f, -0.14, -0.12)
WALL_LAYERS = [-T, -0.16, 0.0]
def wall_core(p, holes, h, y0=0.0, inner_top=None, out='brick'):
    """Parede de 2 m em 2 camadas (gesso por dentro, de -T a -0,16, e tijolo por fora); abaixo de WT, por fora, pedra do embasamento."""
    it = h if inner_top is None else inner_top
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, 0.0, WT, it, h] + [v for hh in holes for v in hh[2:]]))
    ys = [v for v in ys if y0 <= v <= h]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return 'plaster' if 0 < cy < it else ('stone_t' if cy < 0 else None)
        return 'stone_t' if cy < WT else out
    for m, mesh in grid_solid(xs, ys, WALL_LAYERS, cell).items(): p.add(m, mesh)
WATER = [(0.0, WT - 0.12), (0.05, WT - 0.12), (0.05, WT - 0.06), (0.0, WT)]                  # capa chanfrada do embasamento
BELT = [(0.0, -SLAB - 0.08), (0.045, -SLAB - 0.08), (0.06, -SLAB - 0.06), (0.06, 0.02), (0.045, 0.05), (0.0, 0.05)]   # faixa de pedra entre andares
BASE_IN = [(-T, 0.0), (-T - 0.018, 0.0), (-T - 0.018, 0.16), (-T - 0.008, 0.18), (-T, 0.185)]
def wall(kind='win', fl=0):
    """Modulo de fachada (pivo: face externa, cota do piso do andar; parede em -Z): win, plain, door (porta da frente com bandeiras),
    bdoor / sdoor (portas de servico e lateral), bal (porta-balcao para a sacada), chim (liso, atras da chamine).
    fl = 0: terreo com embasamento de pedra e respiros; fl = 1: 2o andar com a faixa de pedra na base."""
    p = Piece(); holes = []; gaps = []
    WW = WIN0 if fl == 0 else WIN1
    if kind == 'win': holes = [WW]
    if kind == 'door': holes = [(-0.95, 0.95, 0.0, 2.6)]; gaps = [(-0.95, 0.95)]
    if kind in ('bdoor', 'sdoor'): holes = [(-0.5, 0.5, 0.0, 2.3)]; gaps = [(-0.5, 0.5)]
    if kind == 'bal': holes = [(-0.6, 0.6, 0.0, 2.35)]; gaps = [(-0.6, 0.6)]
    wall_core(p, holes, HF, -Y0 if fl == 0 else 0.0)
    if kind == 'win': sash_window(p, *WW)
    if kind == 'door':
        front_door_frame(p, -0.95, 0.95, 2.6); stone_head(p, -0.95, 0.95, 2.6, 0.3)
        p.cham('stone_t', -0.995, 0.995, -0.04, 0.012, -T + 0.004, 0.12, 0.006)
    if kind in ('bdoor', 'sdoor', 'bal'):
        a, b = gaps[0]; hh = holes[0][3]; z0, z1 = -0.2, -0.06
        p.box('frame', a, a + 0.06, 0.0, hh, z0, z1); p.box('frame', b - 0.06, b, 0.0, hh, z0, z1); p.box('frame', a, b, hh - 0.06, hh, z0, z1)
        stone_head(p, a, b, hh); p.cham('stone_t', a - 0.03, b + 0.03, -0.04, 0.012, -T + 0.004, 0.08, 0.006)
        if kind == 'sdoor': q = wall_lantern(); p.merge(q, tr(b + 0.35, 1.75, 0.0))
    if fl == 0:
        for (a, b) in segs_excl([], -1.0, 1.0): prof_x(p, 'stone_t', a, b, WATER)
        if kind in ('plain', 'chim'):
            for xx in ((-0.25, 0.25),):
                p.box('dark', xx[0], xx[1], -0.55, -0.3, -0.05, -0.04)
                for x in np.linspace(xx[0] + 0.04, xx[1] - 0.04, 5): p.box('iron', x - 0.008, x + 0.008, -0.55, -0.3, -0.04, -0.025)
    else:
        for (a, b) in segs_excl(gaps if kind == 'bal' else [], -1.0, 1.0): prof_x(p, 'stone_t', a, b, BELT)
    for (a, b) in segs_excl(gaps, -0.999, 0.999, 0.09 if gaps else 0.0): prof_x(p, 'trim', a, b, BASE_IN)
    return p
def corner(fl=0):
    """Quina (pivo: quina externa, cota do piso do andar; paredes em -X e -Z): nucleo, cunhais de pedra alternados nas 2 faces,
    capa do embasamento (terreo) ou faixa (2o andar) em meia-esquadria."""
    p = Piece(); e = 0.004; y0 = -Y0 if fl == 0 else 0.0
    p.box('brick', -T + e, e, WT if fl == 0 else 0.0, HF + (0.0 if fl == 0 else 0.006), -T + e, e); p.box('stone_t', -T + e, e, y0, WT, -T + e, e) if fl == 0 else None
    yq = WT + 0.02 if fl == 0 else 0.13; k = 0
    while yq + 0.3 < HF - 0.04:
        L1, L2 = (0.5, 0.3) if k % 2 == 0 else (0.3, 0.5)
        p.cham('stone_t', -L1, 0.012, yq, yq + 0.29, 0.0, 0.012, 0.004); p.cham('stone_t', 0.0, 0.012, yq, yq + 0.29, -L2, 0.0, 0.004)
        yq += 0.3; k += 1
    if fl == 0: mitre_pair(p, 'stone_t', WATER)
    else: mitre_pair(p, 'stone_t', BELT)
    return p

# ============================================================================ torreao de 12 faces (pivo: centro do torreao, cota do piso)
def facet_xf(k, y=0.0):
    """Transformacao da face k (centro no angulo (k + 0,5) * 30 graus) para o sistema do torreao; local: face em z = 0, parede em -Z."""
    th = (k + 0.5) * 2 * HA; return rot_y(90 - math.degrees(th), (TAP * math.cos(th), y, TAP * math.sin(th)))
def facet_clip(q):
    """Corta a peca local de uma face pelos 2 planos radiais (meia-esquadria automatica de faixas, cornijas e calhas)."""
    c, s = math.cos(HA), math.sin(HA); o = (0.0, 0.0, -TAP)
    return clipped(q, [(o, (c, 0, s)), (o, (-c, 0, s))])
FW = 2 * TR * math.sin(HA)                                    # largura externa da face
def turret_ring(level):
    """Anel do torreao: level 0 (terreo, com embasamento), 1 (2o andar) - 9 faces do lado de fora e pilaretes junto das paredes da casa;
    level 2 (3o nivel, acima do beiral) - 12 faces, cornija com modilhoes e calha. Janelas nas faces 1, 3, 5 e 7 (e 10 no 3o nivel)."""
    p = Piece(); faces = range(NSIDE) if level == 2 else [k for k in range(NSIDE) if k not in (6, 7, 8)]
    wins = {0, 2, 4, 10}
    h = HF if level < 2 else TTOP; y0 = -Y0 if level == 0 else 0.0
    for k in faces:
        q = Piece(); w2 = FW / 2 + 0.12
        WW = WIN0 if level == 0 else WIN1
        holes = [(-0.31, 0.31, WW[2], WW[3]) if level < 2 else (-0.31, 0.31, 0.7, 2.0)] if k in wins else []
        xs = sorted(set([-w2, w2] + [v for hh in holes for v in hh[:2]])); ys = sorted(set([y0, 0.0, WT, h] + [v for hh in holes for v in hh[2:]]))
        ys = [v for v in ys if y0 <= v <= h]
        def cell(i, j, kk, holes=holes, xs=xs, ys=ys):
            cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
            for (a, b, c, d) in holes:
                if a < cx < b and c < cy < d: return None
            if kk == 0: return ('plaster' if 0 < cy < h else 'stone_t') if level < 2 else 'plaster'
            return 'stone_t' if (cy < WT and level == 0) else 'brick'
        for m, mesh in grid_solid(xs, ys, WALL_LAYERS, cell).items(): q.add(m, mesh)
        if holes:
            a, b, c, d = holes[0]; sash_window(q, a, b, c, d, inner=(level < 2), lites=1)
        if level == 0: prof_x(q, 'stone_t', -w2, w2, WATER)
        if level == 1: prof_x(q, 'stone_t', -w2, w2, BELT)
        if level == 2:
            prof_x(q, 'stone_t', -w2, w2, [(0.0, -0.02), (0.05, -0.02), (0.05, 0.12), (0.0, 0.14)])
            prof_x(q, 'trim', -w2, w2, [(z * 0.8, h + y * 0.8) for (z, y) in CORN])
            for xm in (-0.25, 0.25): q.hull('trim', [(xm + dx, h + y, z) for dx in (-0.03, 0.03) for (z, y) in ((0.04, -0.27), (0.17, -0.27), (0.04, -0.21), (0.17, -0.17))])
            prof_x(q, 'gutter', -w2, w2, gutter_profile(0.36, h + 0.03))
        if level < 2: prof_x(q, 'trim', -w2, w2, BASE_IN)
        p.merge(facet_clip(q), facet_xf(k))
    if level < 2:   # pilaretes onde o anel encontra as paredes da casa (o quarto de circulo de dentro fica aberto para o comodo)
        ri = TR - T / math.cos(HA)
        p.box('brick', -TR, -ri, max(y0, WT), h, -T, 0.0); p.box('brick', -T, 0.0, max(y0, WT), h, -TR, -ri)
        if level == 0: p.box('stone_t', -TR, -ri, y0, WT, -T, 0.0); p.box('stone_t', -T, 0.0, y0, WT, -TR, -ri)
        p = clipped(p, [((-TR, 0, 0), (1, 0, 0)), ((0, 0, -TR), (0, 0, 1))])
    return p
def turret_floor(kind='floor'):
    """Piso do torreao (pivo: centro, cota do piso): o dodecagono interno menos o canto coberto pelo piso da casa (x e z < -T).
    'floor' (assoalho sobre o embasamento), 'slab' (laje com forro por baixo), 'top' (forro do 2o andar, piso e forro do 3o nivel)."""
    p = Piece(); ri = TR - T / math.cos(HA)
    full = poly_ngon(0, 0, ri); inner = full.difference(sbox(-5, -5, -T, -T)).buffer(0)
    if kind == 'floor':
        ext_y(p, 'oak', inner, -0.012, 0.0); ext_y(p, 'concrete', inner, -Y0 + 0.02, -0.012)
    else:
        ext_y(p, 'ceil', inner, -SLAB, -SLAB + 0.01); ext_y(p, 'concrete', inner, -SLAB + 0.01, -0.012)
        ext_y(p, 'oak' if kind == 'slab' else 'deck', inner, -0.012, 0.0)
        if kind == 'top': ext_y(p, 'ceil', full, TTOP - 0.26, TTOP - 0.24)
    return p
def turret_roof():
    """Telhado conico de 12 faces (pivo: centro, cota do topo do anel): fiadas de ardosia em anel, beiral sobre a calha,
    espigoes de chapa, pinaculo de cobre com bola e haste."""
    p = Piece(); H = 5.0; r0 = TR + 0.42; n = 26
    for i in range(n):
        ra = r0 * (1 - i / n); rb = r0 * (1 - (i + 1.25) / n); ya = H * i / n; yb = H * (i + 1.25) / n
        if rb < 0.03: rb = 0.03
        for k in range(NSIDE):
            a0, a1 = 2 * HA * k, 2 * HA * (k + 1)
            pts = []
            for (r, y) in ((ra, ya), (rb, yb)):
                for a in (a0, a1): pts += [(r * math.cos(a), y, r * math.sin(a)), ((r - 0.04) * math.cos(a), y + 0.035, (r - 0.04) * math.sin(a))]
            p.hull('shingles', pts)
    for k in range(NSIDE):
        a = 2 * HA * k; seg_cyl(p, 'copper', (r0 * math.cos(a), 0.04, r0 * math.sin(a)), (0.06 * math.cos(a), H - 0.15, 0.06 * math.sin(a)), 0.025, 6)
    lathe(p, 'copper', [(0.16, H - 0.25), (0.16, H - 0.1), (0.1, H), (0.06, H + 0.3), (0.12, H + 0.45), (0.12, H + 0.55), (0.04, H + 0.65), (0.03, H + 1.4), (0.0, H + 1.45)], sec=16)
    p.sphere('copper', 0.12, 0.0, H + 0.85, 0.0, 2)
    return p

# ============================================================================ telhado de 4 aguas (pivo: face da parede, cota do topo das paredes)
CORN = [(0.0, -0.4), (0.05, -0.4), (0.05, -0.34), (0.09, -0.32), (0.38, -0.25), (0.45, -0.25), (0.45, 0.0), (0.0, 0.0)]
FRIEZE = [(0.0, -0.78), (0.03, -0.78), (0.03, -0.42), (0.0, -0.42)]
def roof_strip(lxL=-99.0, lxR=99.0):
    """Faixa de 2 m do telhado (local: parede em z = 0, beiral em +Z): forro, fiadas de ardosia a 45 graus, cornija com modilhoes,
    friso de pedra, calha K e meio-fio do mirante. lxL / lxR: posicao local das quinas da casa a esquerda / direita (rincao a 45 graus)."""
    p = Piece(); x0 = max(-1.0, lxL - MF - 0.02); x1 = min(1.0, lxR + MF + 0.02)
    f = lambda a, b: K * (MF - b)
    sheared(p, 'dark', sbox(x0, MB, x1, MF), 0.0, 0.02, f)
    sheared_courses(p, sbox(x0, MB + 0.1, x1, MF), f, lambda a, b: MF - b, lambda d0, d1: sbox(-50, MF - d1, 50, MF - d0), MF - MB - 0.1,
                    lambda v, n: np.stack([v[:, 0] / TILE, (MF - v[:, 2]) / CS / TILE], 1))
    prof_x(p, 'trim', x0, x1, CORN); prof_x(p, 'stone_t', x0, x1, FRIEZE)
    for xm in np.arange(-1.2, 1.21, 0.4):
        if x0 + 0.05 < xm < x1 - 0.05:
            p.hull('trim', [(xm + dx, y, z) for dx in (-0.035, 0.035) for (z, y) in ((0.05, -0.4), (0.33, -0.33), (0.05, -0.25), (0.38, -0.25))])
    for xm in np.arange(-0.9, 0.91, 0.2):
        if x0 + 0.03 < xm < x1 - 0.03: p.box('trim', xm - 0.03, xm + 0.03, -0.45, -0.4, 0.003, 0.04)                 # denticulos
    gutter_run(p, x0, x1, MF, 0.03)
    p.cham('trim', x0 + 0.001, x1 - 0.001, RISE - 0.04, RISE + 0.12, MB - 0.1, MB + 0.1, 0.01)
    planes = []
    if lxL > -1.0 - (MF - MB) - 0.5: planes.append(((lxL, 0, 0), (1, 0, 1)))
    if lxR < 1.0 + (MF - MB) + 0.5: planes.append(((lxR, 0, 0), (-1, 0, 1)))
    return clipped(p, planes) if planes else p
def hip():
    """Capa do rincao (pivo: quina externa, cota do topo das paredes; paredes em -X e -Z)."""
    p = Piece(); yo = TV + BUMP + 0.004; pts = []
    for h in (MF + 0.03, MB + 0.06):
        y = K * (MF - h) + yo
        pts += [(h, y + 0.05, h), (h - 0.1, y, h), (h, y, h - 0.1), (h - 0.08, y - 0.02, h), (h, y - 0.02, h - 0.08)]
    p.hull('ridge', pts)
    return p
def roof_deck():
    """Mirante plano no topo (pivo: centro, cota do topo das paredes): manta, alcapao, gradil de ferro com pinhas nos cantos."""
    p = Piece(); y = RISE + 0.02; xa, za = HX + MB, HZ + MB
    p.box('membrane', -xa + 0.05, xa - 0.05, RISE - 0.12, y, -za + 0.05, za - 0.05)
    p.cham('trim', -0.6, 0.4, y, y + 0.3, -1.3, -0.5, 0.01); p.cham('dark', -0.65, 0.45, y + 0.3, y + 0.36, -1.35, -0.45, 0.01)
    yb = RISE + 0.12
    for (x0, z0, x1, z1) in ((-xa, za, xa, za), (-xa, -za, xa, -za), (-xa, -za, -xa, za), (xa, -za, xa, za)):
        Ln = math.hypot(x1 - x0, z1 - z0); q = Piece()
        q.box('iron', 0.0, Ln, yb + 0.05, yb + 0.08, -0.015, 0.015); q.box('iron', 0.0, Ln, yb + 0.52, yb + 0.55, -0.015, 0.015)
        for t in np.arange(0.12, Ln - 0.05, 0.12):
            q.box('iron', t - 0.008, t + 0.008, yb, yb + 0.62, -0.008, 0.008); q.hull('iron', [(t + dx, yb + 0.62 + dy, dz) for (dx, dy) in ((-0.025, 0), (0.025, 0), (0, 0.07)) for dz in (-0.008, 0.008)])
        for t in np.arange(0.36, Ln - 0.2, 0.72):
            for k in range(8): a = k * math.pi / 4; seg_cyl(q, 'iron', (t + 0.1 * math.cos(a), yb + 0.3 + 0.1 * math.sin(a), 0), (t + 0.1 * math.cos(a + math.pi / 4), yb + 0.3 + 0.1 * math.sin(a + math.pi / 4), 0), 0.006, 4)
        along(p, q, x0, z0, x1, z1)
    for (x, z) in ((-xa, -za), (-xa, za), (xa, -za), (xa, za)):
        p.box('iron', x - 0.03, x + 0.03, yb, yb + 0.7, z - 0.03, z + 0.03); lathe(p, 'iron', [(0.04, yb + 0.7), (0.06, yb + 0.78), (0.0, yb + 0.92)], x, z, 0.0, 10)
    return p
def roof_turret_corner():
    """Canto do telhado junto do torreao (pivo: quina da casa / centro do torreao, cota do topo das paredes): faixas da frente e do
    lado leste e o rincao, cortados pelo prisma do torreao."""
    p = Piece()
    p.merge(roof_strip(-99.0, 1.0), tr(-1.0, 0, 0))
    p.merge(roof_strip(-1.0, 99.0), rot_y(90, (0, 0, -1.0)))
    p.merge(hip())
    return subtract_prism(p, poly_ngon(0, 0, TR + 0.006), -1.5, RISE + 1.0)
def dormer():
    """Trapeira (local como a faixa do telhado; pivo na face da parede, no eixo, cota do topo das paredes): frente de madeira com
    pilastras e frontao, janela de guilhotina, ilhargas, telhado de 2 aguas de ardosia com cumeeira, enterrado no telhado atras."""
    p = Piece(); zf = -1.0; zb = -3.5; x = 0.72; ye = 2.75; yr = 3.45; y0 = 0.9
    xs = [-x, -0.38, 0.38, x]; ys = [y0, 1.62, 2.52, ye]
    for m, mesh in grid_solid(xs, ys, [zf - 0.12, zf], lambda i, j, k: None if (i == 1 and j == 1) else 'trim').items(): p.add(m, mesh)
    f = 0.05
    p.box('frame', -0.38, -0.38 + f, 1.62, 2.52, zf - 0.1, zf - 0.03); p.box('frame', 0.38 - f, 0.38, 1.62, 2.52, zf - 0.1, zf - 0.03)
    p.box('frame', -0.38 + f, 0.38 - f, 2.47, 2.52, zf - 0.1, zf - 0.03); p.box('frame', -0.38 + f, 0.38 - f, 1.62, 1.66, zf - 0.1, zf - 0.03)
    sash(p, -0.33, 0.33, 1.66, 2.1, zf - 0.09, zf - 0.065, 2, 0.06); sash(p, -0.33, 0.33, 2.06, 2.47, zf - 0.06, zf - 0.035, 2, 0.05)
    prof_x(p, 'trim', -0.46, 0.46, [(zf, 1.55), (zf + 0.07, 1.55), (zf + 0.07, 1.6), (zf, 1.63)])
    for s in (-1, 1): p.cham('trim', *sorted((s * x, s * (x - 0.12))), y0, ye, zf, zf + 0.03, 0.006)
    for s in (-1, 1): p.box('shingles', *sorted((s * x, s * (x - 0.06))), y0, ye, zb, zf - 0.12)
    tri = Polygon([(-x - 0.08, ye), (x + 0.08, ye), (0.0, yr + 0.06)])
    ext(p, 'trim', tri.buffer(0), zf - 0.12, zf + 0.04)
    ext(p, 'dark', Polygon([(-x + 0.08, ye + 0.06), (x - 0.08, ye + 0.06), (0.0, yr - 0.08)]), zf + 0.04, zf + 0.05)
    for s in (-1, 1):
        a = (s * (x + 0.14), ye - 0.06); b = (0.0, yr + 0.02)
        p.hull('shingles', [(a[0], a[1], z) for z in (zf + 0.08, zb - 0.4)] + [(a[0], a[1] + 0.07, z) for z in (zf + 0.08, zb - 0.4)] +
               [(b[0], b[1], z) for z in (zf + 0.08, zb - 0.4)] + [(b[0], b[1] + 0.07, z) for z in (zf + 0.08, zb - 0.4)])
    p.hull('ridge', [(dx, yr + 0.09 + dy, z) for dx in (-0.06, 0.06) for dy in (0.0, 0.04) for z in (zf + 0.09, zb - 0.4)])
    return p
def chimney(kind='ext'):
    """Chamine de tijolo. 'ext': encostada na fachada (pivo: face da parede no chao; para +Z), base de pedra, ombros com rampa de
    pedra no 2o andar, sobe pelo beiral. 'roof': nasce do sotao (pivo: centro, cota do topo das paredes). Coroamento com 3 fiadas
    salientes, capa de pedra e 2 potes de barro."""
    p = Piece()
    if kind == 'ext':
        top = YE + 3.7; ya = Y1 + 1.2
        p.box('stone_t', -0.66, 0.66, 0.0, Y0 + WT, 0.0, 0.72); p.cham('stone_t', -0.7, 0.7, Y0 + WT - 0.1, Y0 + WT, 0.0, 0.76, 0.01)
        p.box('brick', -0.62, 0.62, Y0 + WT, ya, 0.0, 0.68)
        p.hull('stone_t', [(x, y, z) for x in (-0.64, 0.64) for (z, y) in ((0.003, ya), (0.7, ya), (0.003, ya + 0.45), (0.55, ya + 0.45))] + [(x, ya + 0.45, 0.003) for x in (-0.5, 0.5)])
        x, z1 = 0.48, 0.55; yb = ya + 0.4
    else:
        top = RISE + 2.4; x, z1 = 0.46, 0.36; yb = 0.0
    zc = 0.0 if kind == 'ext' else -z1
    p.box('brick', -x, x, yb, top - 0.5, zc, z1)
    for i, d in enumerate((0.04, 0.08, 0.05)):
        yy = top - 0.5 + i * 0.1; p.box('brick', -x - d, x + d, yy, yy + 0.1, zc - (d if kind == 'roof' else 0.0), z1 + d)
    p.box('brick', -x, x, top - 0.2, top - 0.1, zc, z1)
    p.cham('stone_t', -x - 0.07, x + 0.07, top - 0.1, top, zc - (0.07 if kind == 'roof' else 0.0), z1 + 0.07, 0.01)
    zm = (zc + z1) / 2
    for xx in (-x / 2, x / 2): lathe(p, 'clay', [(0.13, top), (0.11, top + 0.35), (0.14, top + 0.4), (0.14, top + 0.46), (0.1, top + 0.47)], xx, zm, 0.0, 12)
    return p
def downspout_piece(fl_drop):
    return downspout(fl_drop, MF + 0.065)

# ============================================================================ varanda, porte-cochere e escadas (pivo: face da parede, chao)
def baluster(p, x, z, y0, h):
    lathe(p, 'trim', [(0.05, y0), (0.05, y0 + 0.06), (0.032, y0 + 0.1), (0.045, y0 + h * 0.35), (0.028, y0 + h * 0.6), (0.022, y0 + h * 0.85),
                      (0.035, y0 + h * 0.9), (0.035, y0 + h)], x, z, 0.0, 8)
def balustrade(p, x0, z0, x1, z1, y0, h=0.9, sp=0.16, base=True):
    """Balaustrada de madeira pintada de (x0, z0) a (x1, z1): rodape, balaustres torneados e corrimao."""
    Ln = math.hypot(x1 - x0, z1 - z0); q = Piece()
    if base: q.cham('trim', 0.0, Ln, y0, y0 + 0.08, -0.06, 0.06, 0.008)
    q.cham('trim', 0.0, Ln, y0 + h, y0 + h + 0.06, -0.07, 0.07, 0.012); q.cham('trim', 0.0, Ln, y0 + h - 0.04, y0 + h, -0.045, 0.045, 0.006)
    n = max(1, int(round((Ln - 0.1) / sp)))
    for i in range(n): baluster(q, 0.05 + (i + 0.5) * (Ln - 0.1) / n, 0.0, y0 + (0.08 if base else 0.0), h - 0.04 - (0.08 if base else 0.0))
    along(p, q, x0, z0, x1, z1)
def column(p, x, z, y0, h):
    """Coluna toscana de pedra: plinto, toro, fuste com entase, capitel com abaco."""
    p.cham('stone_t', x - 0.2, x + 0.2, y0, y0 + 0.08, z - 0.2, z + 0.2, 0.006)
    lathe(p, 'stone_t', [(0.18, y0 + 0.08), (0.18, y0 + 0.12), (0.155, y0 + 0.16), (0.15, y0 + 0.2), (0.14, y0 + h * 0.6), (0.12, y0 + h - 0.22),
                         (0.135, y0 + h - 0.2), (0.135, y0 + h - 0.17), (0.12, y0 + h - 0.16), (0.16, y0 + h - 0.08)], x, z, 0.0, 16)
    p.cham('stone_t', x - 0.19, x + 0.19, y0 + h - 0.08, y0 + h, z - 0.19, z + 0.19, 0.006)
def steps(p, x0, x1, z0, n, rise, run, dirz=1, mat='stone_t', y_top=Y0):
    """Degraus macicos de (x0, x1), comecando em z0 e descendo no sentido dirz: n degraus de espelho 'rise' e piso 'run'."""
    for i in range(1, n + 1):
        y = y_top - i * rise
        if y <= 0.001: break
        za, zb = sorted((z0 + dirz * (i - 1) * run, z0 + dirz * i * run))
        p.box(mat, x0, x1, 0.0, y - 0.03, za, zb); p.cham(mat, x0 - 0.02, x1 + 0.02, y - 0.03, y, za - (0.03 if dirz > 0 else 0.0), zb + (0.03 if dirz < 0 else 0.0), 0.006)
def porch():
    """Varanda da frente (pivo: face da parede no eixo da porta, chao; para +Z): embasamento de tijolo com capa, piso de tabuas,
    4 colunas toscanas, balaustradas, arquitrave, forro de lambri com lanterna, teto que e sacada do 2o andar com balaustrada,
    escada de 4 degraus de pedra com muretas e urnas."""
    p = Piece(); x = 3.3; d = 3.0; yt = HF + Y0 - 0.02; yb = 3.5; yc = 3.75
    for (a, b, c, e) in ((-x, -1.45, d - 0.25, d), (1.45, x, d - 0.25, d), (-x, -x + 0.25, 0.0, d - 0.25), (x - 0.25, x, 0.0, d - 0.25)):
        p.box('brick', a, b, 0.0, Y0 - 0.1, c, e); p.cham('stone_t', a - 0.02, b + 0.02, Y0 - 0.1, Y0 - 0.05, c - 0.02, e + 0.02, 0.006)
    for xx in np.arange(-x + 0.6, x - 0.4, 0.75):
        if abs(xx) > 1.6: p.box('dark', xx - 0.15, xx + 0.15, 0.15, 0.4, d, d + 0.004)
    p.box('concrete', -x + 0.25, x - 0.25, 0.0, Y0 - 0.12, 0.0, d - 0.25)
    for i in range(int((2 * x) / 0.14)):
        xa = -x + i * 0.14; p.box('deck', xa + 0.003, min(x, xa + 0.137), Y0 - 0.05, Y0 - 0.005, 0.0, d + 0.03)
    for (cx, cz) in ((-3.0, d - 0.25), (-1.45, d - 0.25), (1.45, d - 0.25), (3.0, d - 0.25)): column(p, cx, cz, Y0 - 0.005, yb - Y0 + 0.005)
    for (a, b, c, e) in ((-x + 0.003, x - 0.003, d - 0.45, d - 0.053), (-x + 0.003, -x + 0.4, 0.003, d - 0.45), (x - 0.4, x - 0.003, 0.003, d - 0.45)):
        p.cham('trim', a, b, yb, yc + 0.1, c, e, 0.008)
    prof_x(p, 'trim', -x - 0.08, x + 0.08, [(d - 0.05, yc + 0.1), (d + 0.06, yc + 0.1), (d + 0.08, yc + 0.14), (d + 0.08, yt - 0.04), (d - 0.05, yt - 0.04)])
    for s in (-1, 1): prof_z(p, 'trim', 0.0, d - 0.05, [(s * x, yc + 0.1), (s * (x + 0.08), yc + 0.1), (s * (x + 0.08), yt - 0.04), (s * x, yt - 0.04)] if s > 0 else [(-x - 0.08, yc + 0.1), (-x, yc + 0.1), (-x, yt - 0.04), (-x - 0.08, yt - 0.04)])
    for i in range(int((2 * x - 0.8) / 0.1)):
        xa = -x + 0.4 + i * 0.1; p.box('trim', xa + 0.003, xa + 0.097, yc - 0.012, yc, 0.0, d - 0.45)
    p.box('concrete', -x, x, yc, yt - 0.03, 0.0, d - 0.05); p.box('membrane', -x + 0.02, x - 0.02, yt - 0.03, yt, 0.0, d - 0.06)
    q = porch_lantern(); p.merge(q, tr(0.0, yc - 0.012, 1.3))
    for (a, b) in ((-3.0, -1.45), (1.45, 3.0)): balustrade(p, a + 0.2, d - 0.25, b - 0.2, d - 0.25, Y0 - 0.005)
    for s in (-1, 1): balustrade(p, s * 3.0, 0.25, s * 3.0, d - 0.45, Y0 - 0.005)
    for (x0, z0, x1, z1) in ((-x + 0.08, d - 0.13, x - 0.08, d - 0.13), (-x + 0.08, 0.06, -x + 0.08, d - 0.13), (x - 0.08, 0.06, x - 0.08, d - 0.13)):
        balustrade(p, x0, z0, x1, z1, yt)
    for (xx, zz) in ((-x + 0.08, d - 0.13), (x - 0.08, d - 0.13)): p.cham('trim', xx - 0.1, xx + 0.1, yt, yt + 1.05, zz - 0.1, zz + 0.1, 0.01)
    steps(p, -1.2, 1.2, d + 0.03, 4, 0.15, 0.3, 1)
    for s in (-1, 1):
        a, b = sorted((s * 1.22, s * 1.5))
        p.hull('brick', [(xx, y, z) for xx in (a, b) for (z, y) in ((d, 0.0), (d + 1.23, 0.0), (d, Y0 + 0.05), (d + 0.35, Y0 + 0.05), (d + 1.23, 0.35))])
        p.hull('stone_t', [(xx, y, z) for xx in (a - 0.03, b + 0.03) for (z, y) in ((d, Y0 + 0.05), (d + 0.35, Y0 + 0.05), (d + 1.26, 0.35), (d + 1.26, 0.41), (d + 0.35, Y0 + 0.11), (d, Y0 + 0.11))])
        p.cham('stone_t', a - 0.04, b + 0.04, 0.35, 0.41, d + 1.1, d + 1.32, 0.006) if False else None
        lathe(p, 'stone_t', [(0.1, Y0 + 0.11), (0.12, Y0 + 0.16), (0.06, Y0 + 0.2), (0.17, Y0 + 0.36), (0.2, Y0 + 0.5), (0.16, Y0 + 0.54)], s * 1.36, d + 0.17, 0.0, 14)
        p.sphere('hedge', 0.17, s * 1.36, Y0 + 0.62, d + 0.17, 1)
    return p
def porte_cochere():
    """Porte-cochere lateral (pivo: face da parede oeste no meio, chao; local +Z para fora, +X para o fundo... ver montagem):
    2 pilares de tijolo com base e capitel de pedra, vigas, forro de lambri com lanterna, teto que e sacada com balaustrada,
    patamar de pedra junto da porta lateral com escada e corrimao de ferro."""
    p = Piece(); x = 2.9; d = 4.6; yb = 3.5; yc = 3.75; yt = HF + Y0 - 0.02
    for s in (-1, 1):
        a, b = sorted((s * 2.3, s * 2.9))
        p.cham('stone_t', a - 0.05, b + 0.05, 0.0, 0.45, d - 0.65, d + 0.05, 0.01); p.box('brick', a, b, 0.45, yb - 0.25, d - 0.6, d)
        for yy in np.arange(0.9, yb - 0.4, 0.6): p.box('stone_t', a - 0.012, b + 0.012, yy, yy + 0.1, d - 0.612, d + 0.012)
        p.cham('stone_t', a - 0.06, b + 0.06, yb - 0.25, yb, d - 0.66, d + 0.06, 0.008)
        p.cham('trim', a + 0.003 * (s < 0), b - 0.003 * (s > 0), yb, yc + 0.1, 0.003, d - 0.6, 0.008)
    p.cham('trim', -x + 0.003, x - 0.003, yb, yc + 0.1, d - 0.6, d - 0.003, 0.008)
    prof_x(p, 'trim', -x - 0.08, x + 0.08, [(d, yc + 0.1), (d + 0.08, yc + 0.1), (d + 0.08, yt - 0.04), (d, yt - 0.04)])
    prof_z(p, 'trim', 0.0, d + 0.08, [(-x - 0.08, yc + 0.1), (-x, yc + 0.1), (-x, yt - 0.04), (-x - 0.08, yt - 0.04)])
    prof_z(p, 'trim', 0.0, d + 0.08, [(x, yc + 0.1), (x + 0.08, yc + 0.1), (x + 0.08, yt - 0.04), (x, yt - 0.04)])
    for i in range(int((2 * 2.3) / 0.1)):
        xa = -2.3 + i * 0.1; p.box('trim', xa + 0.003, xa + 0.097, yc - 0.012, yc, 0.0, d - 0.6)
    p.box('concrete', -x, x, yc, yt - 0.03, 0.0, d); p.box('membrane', -x + 0.02, x - 0.02, yt - 0.03, yt, 0.0, d - 0.01)
    q = porch_lantern(); p.merge(q, tr(0.0, yc - 0.012, 2.2))
    for (x0, z0, x1, z1) in ((-x + 0.08, d - 0.08, x - 0.08, d - 0.08), (-x + 0.08, 0.06, -x + 0.08, d - 0.08), (x - 0.08, 0.06, x - 0.08, d - 0.08)):
        balustrade(p, x0, z0, x1, z1, yt)
    for (xx, zz) in ((-x + 0.08, d - 0.08), (x - 0.08, d - 0.08)): p.cham('trim', xx - 0.1, xx + 0.1, yt, yt + 1.05, zz - 0.1, zz + 0.1, 0.01)
    # patamar e escada da porta lateral (porta em local x de 1,0 a 2,0)
    p.box('brick', 0.7, 2.3, 0.0, Y0 - 0.04, 0.0, 1.2); p.cham('stone_t', 0.68, 2.32, Y0 - 0.04, Y0, 0.0, 1.22, 0.006)
    for i in range(1, 5):
        y = Y0 - i * 0.15; xa, xb = 0.7 - i * 0.3, 0.7 - (i - 1) * 0.3
        p.box('stone_t', xa, xb, 0.0, y - 0.03, 0.0, 1.2); p.cham('stone_t', xa - 0.03, xb, y - 0.03, y, 0.0, 1.22, 0.006)
    rail = [(-0.5 + 0.05, 0.9 + 0.15), (0.7, Y0 + 0.9), (2.25, Y0 + 0.9)]
    for (xa, ya), (xb, yb_) in zip(rail[:-1], rail[1:]): seg_cyl(p, 'iron', (xa, ya, 1.12), (xb, yb_, 1.12), 0.02, 8)
    for (xx, yy) in ((-0.42, 0.15), (0.1, 0.45), (0.7, Y0), (1.5, Y0), (2.25, Y0)): seg_cyl(p, 'iron', (xx, yy, 1.12), (xx, yy + 0.9 + (0.0 if xx >= 0.7 else (Y0 - yy) * 0.0), 1.12), 0.012, 6)
    return p
def back_stoop():
    """Patamar e escada da porta da cozinha (pivo: face da parede no eixo da porta, chao; para +Z), com corrimaos de ferro."""
    p = Piece()
    p.box('brick', -0.8, 0.8, 0.0, Y0 - 0.04, 0.0, 1.3); p.cham('stone_t', -0.82, 0.82, Y0 - 0.04, Y0, 0.0, 1.32, 0.006)
    steps(p, -0.8, 0.8, 1.32, 4, 0.15, 0.3, 1)
    for s in (-1, 1):
        xx = s * 0.74
        for (za, ya, zb, yb_) in ((0.05, Y0 + 0.9, 1.3, Y0 + 0.9), (1.3, Y0 + 0.9, 2.5, 0.9 + 0.15)): seg_cyl(p, 'iron', (xx, ya, za), (xx, yb_, zb), 0.02, 8)
        for (zz, yy) in ((0.1, Y0), (1.25, Y0), (1.95, 0.3), (2.45, 0.15)): seg_cyl(p, 'iron', (xx, yy, zz), (xx, yy + 0.9, zz), 0.012, 6)
    return p

# ============================================================================ pisos, forros, paredes internas, escadaria
def checker(p, poly, y0, y1, step, ma, mb, ox=0.0, oz=0.0, gap=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step + gap, oz + j * step + gap, ox + (i + 1) * step - gap, oz + (j + 1) * step - gap).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
INNER = sbox(-XI, -ZI, XI, ZI)
HALL_R = sbox(-HALL, -ZI, HALL, ZI); NE = sbox(HALL, -ZI, XI, 0.0)
def crown(p, segs, y):
    """Sanca de gesso (cimalha) ao longo dos segmentos (x0, z0, x1, z1, lado): lado = vetor (dx, dz) que aponta para dentro do comodo."""
    for (x0, z0, x1, z1, (dx, dz)) in segs:
        pts = []
        for (x, z) in ((x0, z0), (x1, z1)):
            for (o, yy) in ((0.0, y - 0.13), (0.0, y), (0.13, y), (0.03, y - 0.1)):
                pts.append((x + dx * o, yy, z + dz * o))
        p.hull('trim', pts)
def medallion(p, x, z, y):
    lathe(p, 'trim', [(0.32, y), (0.3, y - 0.02), (0.22, y - 0.035), (0.1, y - 0.05), (0.0, y - 0.055)], x, z, 0.0, 20)
ROOMS_G = {'parlor': (-XI, 0.07, -2.07, ZI), 'dining': (-XI, -ZI, -2.07, -0.07), 'library': (2.07, 0.07, XI, ZI), 'kitchen': (2.07, -ZI, XI, -0.07)}
def room_crown(p, r, y, skip=()):
    x0, z0, x1, z1 = r; segs = [(x0, z0, x1, z0, (0, 1)), (x0, z1, x1, z1, (0, -1)), (x0, z0, x0, z1, (1, 0)), (x1, z0, x1, z1, (-1, 0))]
    crown(p, [s for i, s in enumerate(segs) if i not in skip], y)
def floor_piece(level):
    """Piso / laje de um andar (pivo: origem, cota do piso). 'g': terreo sobre o embasamento (marmore xadrez no hall, ladrilho na
    cozinha, tabuas de carvalho nos comodos). '1': laje do 2o andar (forro, sancas e medalhoes do terreo por baixo, abertura da
    escadaria, ladrilho no banheiro). 'e': forro do 2o andar e piso do sotao."""
    p = Piece()
    if level == 'g':
        ext_y(p, 'concrete', INNER, -Y0 + 0.02, -0.012)
        checker(p, HALL_R.intersection(INNER), -0.012, 0.0, 0.5, 'marble_w', 'marble_k', 0.0, 0.0)
        checker(p, NE.intersection(INNER), -0.012, 0.0, 0.25, 'tile', 'tile_k', 0.0, 0.0)
        ext_y(p, 'oak', INNER.difference(HALL_R).difference(NE), -0.012, 0.0)
        return p
    inner = INNER.difference(STAIR_HOLE) if level == '1' else INNER
    ext_y(p, 'ceil', inner, -SLAB, -SLAB + 0.01); ext_y(p, 'concrete', inner, -SLAB + 0.01, -0.012)
    yc = -SLAB
    if level == '1':
        checker(p, NE.intersection(INNER), -0.012, 0.0, 0.25, 'tile', 'tile_k', 0.0, 0.0)
        ext_y(p, 'oak', inner.difference(NE), -0.012, 0.0)
        for k, r in ROOMS_G.items():
            if k == 'library': room_crown(p, r, yc, skip=(1, 3))
            elif k != 'kitchen': room_crown(p, r, yc)
        crown(p, [(-1.93, -ZI, -1.93, ZI, (1, 0)), (-1.93, ZI, 1.93, ZI, (0, -1)), (-1.93, -ZI, 1.93, -ZI, (0, 1))], yc)
        for (x, z) in ((-4.4, 2.6), (-4.4, -2.9), (4.4, 2.6), (0.0, 3.4)): medallion(p, x, z, yc)
    else:
        ext_y(p, 'deck', inner, -0.012, 0.0) if False else None
        for r in (ROOMS_G['parlor'], ROOMS_G['dining']): room_crown(p, r, yc)
        room_crown(p, ROOMS_G['library'], yc, skip=(1, 3))
        crown(p, [(-1.93, -ZI, -1.93, ZI, (1, 0)), (1.93, -ZI, 1.93, ZI, (-1, 0)), (-1.93, ZI, 1.93, ZI, (0, -1)), (-1.93, -ZI, 1.93, -ZI, (0, 1))], yc)
        for (x, z) in ((-4.6, 3.3), (-4.4, -2.9), (4.4, 2.6), (0.0, 3.4), (4.4, -2.9)): medallion(p, x, z, yc)
    return p
def run_wall(Ln, h, cuts=(), t=t_, skip_base=((), ())):
    """Parede interna (pivo: inicio, eixo; vai para +X). cuts = (centro, largura, altura, com_folha): portas e passagens com batente e
    guarnicao. skip_base = trechos (a, b) sem rodape do lado +Z local e do lado -Z local (ex.: sob a escadaria)."""
    p = Piece(); cs = [(c - w / 2, c + w / 2, hh) for (c, w, hh, _) in cuts]
    xs = sorted(set([0.0, Ln] + [v for (a, b, _) in cs for v in (a, b)])); ys = sorted(set([0.0, h] + [hh for (_, _, hh) in cs]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        return None if any(a < cx < b and cy < hh for (a, b, hh) in cs) else 'plaster'
    for m, mesh in grid_solid(xs, ys, [-t / 2, t / 2], cell).items(): p.add(m, mesh)
    for (c, w, hh, _) in cuts:
        q = Piece(); door_casing(q, w, t, hh); p.merge(q, tr(c, 0, 0))
    for side, skip in ((1, skip_base[0]), (-1, skip_base[1])):
        segs = segs_excl([(a - 0.09, b + 0.09) for (a, b, _) in cs] + list(skip), 0.0, Ln)
        for (a, b) in segs:
            if b - a > 0.02: prof_x(p, 'trim', a, b, D.BASE_PROF(t) if side > 0 else [(-z, y) for (z, y) in D.BASE_PROF(t)][::-1])
    return p
def plan(level):
    """Paredes internas de um andar (pivo: origem, cota do piso): hall central com passagens e portas, divisorias em z = 0."""
    p = Piece(); h = CEIL
    if level == 'g':
        west = [(3.0 + ZI, 1.4, 2.5, False), (-3.0 + ZI, 0.9, 2.1, True)]; east = [(3.0 + ZI, 1.4, 2.5, False), (-4.6 + ZI, 0.9, 2.1, True)]
        sk = (ZS1 + ZI - 0.1, ZS0 + ZI + 0.05)
    else:
        west = [(4.6 + ZI, 0.9, 2.1, True), (-3.0 + ZI, 0.9, 2.1, True)]; east = [(3.0 + ZI, 0.9, 2.1, True), (-4.6 + ZI, 0.9, 2.1, True)]
        sk = (ZS1 + ZI - 0.1, ZS0 + ZI + 0.05)
    p.merge(run_wall(2 * ZI, h, west), rot_y(-90, (-HALL, 0, -ZI)))
    p.merge(run_wall(2 * ZI, h, east, skip_base=((sk,), ())), rot_y(-90, (HALL, 0, -ZI)))
    for (x0, x1) in ((-XI, -HALL - t_ / 2), (HALL + t_ / 2, XI)): p.merge(run_wall(x1 - x0, h), tr(x0, 0, 0))
    return p
def stair():
    """Escadaria do hall (pivo: origem, cota do piso do terreo): 16 pisos de carvalho com bocel e 17 espelhos brancos, longarina
    aberta com consolos recortados, balaustres torneados (2 por degrau), corrimao, pilares de arranque e de chegada com pinha,
    corrimao de parede com suportes, painel sob a escada."""
    p = Piece(); x0, x1 = XS0, XS1
    yl = lambda z: (ZS0 - z) / GS * RS
    for i in range(1, NS):
        y = i * RS; z0, z1 = ZS0 - i * GS, ZS0 - (i - 1) * GS
        p.box('trim', x0, x1, max(0.0, y - RS - 0.2), y - 0.03, z0, z1)
        p.cham('oak', x0 - 0.03, x1, y - 0.03, y, z0, z1 + 0.035, 0.008)
        p.hull('trim', [(x0 - 0.012, yy, zz) for (zz, yy) in ((z0 + 0.03, y - 0.05), (z1 - 0.03, y - 0.05), (z1 - 0.06, y - 0.17))] + [(x0, yy, zz) for (zz, yy) in ((z0 + 0.03, y - 0.05), (z1 - 0.03, y - 0.05), (z1 - 0.06, y - 0.17))])
        for k in (0.25, 0.75):
            zz = z0 + k * GS; baluster(p, x0 + 0.05, zz, y, yl(zz) + 0.9 - y)
    za, zb = ZS0 + 0.1, ZS1 + 0.05
    seg_cyl(p, 'oak', (x0 + 0.05, yl(za) + 0.95, za), (x0 + 0.05, yl(zb) + 0.95, zb), 0.035, 10)
    seg_cyl(p, 'oak', (x1 - 0.08, yl(za) + 0.9, za - 0.2), (x1 - 0.08, yl(zb) + 0.9, zb + 0.1), 0.025, 8)
    for zz in np.linspace(za - 0.4, zb + 0.3, 5): seg_cyl(p, 'brass', (x1 - 0.08, yl(zz) + 0.9, zz), (x1, yl(zz) + 0.9, zz), 0.008, 6)
    for (zz, yb, yt) in ((ZS0 + 0.12, 0.0, 1.2), (ZS1 - 0.08, HF - 0.33, HF + 1.1)):
        p.cham('oak', x0 - 0.04, x0 + 0.14, yb, yt, zz - 0.09, zz + 0.09, 0.012)
        p.cham('oak', x0 - 0.07, x0 + 0.17, yt - 0.06, yt, zz - 0.12, zz + 0.12, 0.01); p.sphere('oak', 0.08, x0 + 0.05, yt + 0.06, zz, 1)
    # painel de lambri sob a escada (fecha o vao baixo; o fundo fica aberto sob o patamar)
    zc0, zc1 = ZS0 - 1.6, ZS1 + 0.1
    p.hull('plaster', [(xx, y, z) for xx in (x0 + 0.003, x0 + 0.06) for (z, y) in ((zc0, 0.0), (zc1, 0.0), (zc1, yl(zc1) - 0.3), (zc0, yl(zc0) - 0.3))])
    return p
def stair_rail_1():
    """Balaustrada do 2o andar em volta do vao da escadaria (pivo: origem, cota do piso do 2o andar)."""
    p = Piece()
    balustrade(p, XS0 + 0.05, ZS1 - 0.08, XS0 + 0.05, ZS0 + 0.05, 0.0)
    balustrade(p, XS0 + 0.05, ZS0 + 0.05, XS1, ZS0 + 0.05, 0.0)
    p.cham('oak', XS0 - 0.04, XS0 + 0.14, -0.05, 1.1, ZS0 - 0.04, ZS0 + 0.14, 0.012); p.sphere('oak', 0.08, XS0 + 0.05, 1.16, ZS0 + 0.05, 1)
    p.box('trim', XS0 - 0.02, XS0 + 0.0, -SLAB - 0.05, 0.0, ZS1, ZS0) if False else None
    return p

# ============================================================================ moveis (pivo: centro da parte de tras, no piso; frente para +Z)
def fireplace():
    """Lareira de marmore e madeira (pivo: face da parede, no eixo, piso; para +Z): soleira de pedra, pilastras, friso, prateleira,
    fornalha escura com grelha e lenha, guarda-fogo de latao e espelho com moldura dourada em cima."""
    p = Piece()
    p.cham('marble_w', -0.85, 0.85, 0.0, 0.03, 0.0, 0.55, 0.006)
    for s in (-1, 1):
        a, b = sorted((s * 0.78, s * 0.56)); p.cham('dkwood', a, b, 0.03, 1.12, 0.0, 0.26, 0.008)
        p.cham('dkwood', a - 0.02 * (s < 0), b + 0.02 * (s > 0), 0.03, 0.15, 0.0, 0.28, 0.008)
    p.cham('dkwood', -0.56, 0.56, 0.86, 1.12, 0.0, 0.24, 0.008); p.cham('marble_w', -0.56, 0.56, 0.03, 0.86, 0.0, 0.02, 0.004)
    p.box('dark', -0.38, 0.38, 0.03, 0.7, 0.02, 0.03)
    p.cham('dkwood', -0.88, 0.88, 1.12, 1.18, 0.0, 0.32, 0.01)
    for x in (-0.25, 0.25): seg_cyl(p, 'iron', (x, 0.08, 0.06), (x, 0.08, 0.2), 0.015, 6)
    seg_cyl(p, 'iron', (-0.3, 0.12, 0.12), (0.3, 0.12, 0.12), 0.012, 6)
    for (dz, dy) in ((0.08, 0.17), (0.16, 0.17), (0.12, 0.24)): seg_cyl(p, 'bark', (-0.25, dy, dz), (0.25, dy, dz), 0.045, 8)
    p.box('brass', -0.7, 0.7, 0.03, 0.12, 0.5, 0.52); p.box('brass', -0.7, -0.68, 0.03, 0.12, 0.3, 0.5); p.box('brass', 0.68, 0.7, 0.03, 0.12, 0.3, 0.5)
    p.cham('brass', -0.6, 0.6, 1.3, 2.3, 0.0, 0.05, 0.01); p.box('glass', -0.52, 0.52, 1.38, 2.22, 0.05, 0.055)
    for x in (-0.6, 0.6): lathe(p, 'brass', [(0.05, 1.18), (0.03, 1.22), (0.015, 1.4), (0.03, 1.42)], x, 0.12, 0.0, 10)
    return p
def sofa_v(L1=2.0, mat='velvet'):
    """Sofa de encosto ondulado com pes torneados e almofadas."""
    p = Piece(); x = L1 / 2
    p.cham('dkwood', -x, x, 0.12, 0.2, 0.0, 0.8, 0.01); p.cham(mat, -x + 0.04, x - 0.04, 0.2, 0.45, 0.02, 0.8, 0.04)
    p.hull(mat, [(xx, y, z) for xx in (-x + 0.04, x - 0.04) for (z, y) in ((0.0, 0.2), (0.18, 0.2), (0.0, 0.85), (0.12, 0.85))] + [(0.0, 1.0, 0.0), (0.0, 1.0, 0.1)])
    for s in (-1, 1): p.cham(mat, *sorted((s * x, s * (x - 0.16))), 0.2, 0.68, 0.0, 0.82, 0.05)
    for (sx, sz) in ((-1, 0.06), (1, 0.06), (-1, 0.74), (1, 0.74)): lathe(p, 'dkwood', [(0.03, 0.0), (0.04, 0.06), (0.025, 0.12)], sx * (x - 0.06), sz, 0.0, 8)
    return p
def armchair(mat='velvet'):
    p = Piece()
    p.cham('dkwood', -0.4, 0.4, 0.12, 0.2, 0.0, 0.75, 0.01); p.cham(mat, -0.36, 0.36, 0.2, 0.46, 0.04, 0.75, 0.04)
    p.hull(mat, [(xx, y, z) for xx in (-0.38, 0.38) for (z, y) in ((0.0, 0.2), (0.18, 0.2), (0.0, 1.0), (0.12, 1.0))])
    for s in (-1, 1): p.cham(mat, *sorted((s * 0.4, s * 0.28)), 0.2, 0.68, 0.0, 0.76, 0.04)
    for (sx, sz) in ((-1, 0.06), (1, 0.06), (-1, 0.7), (1, 0.7)): lathe(p, 'dkwood', [(0.025, 0.0), (0.035, 0.06), (0.025, 0.12)], sx * 0.33, sz, 0.0, 8)
    return p
def tea_table(r=0.45, h=0.5):
    p = Piece(); p.cyl('dkwood', r, h - 0.04, h, 0, 0, 24); lathe(p, 'dkwood', [(0.05, 0.08), (0.04, h * 0.5), (0.06, h * 0.7), (0.05, h - 0.04)], sec=10)
    for k in range(3): a = 2 * math.pi * k / 3; seg_cyl(p, 'dkwood', (0, 0.1, 0), (0.3 * math.cos(a), 0.0, 0.3 * math.sin(a)), 0.02, 6)
    return p
def rug(p, x0, x1, z0, z1, mat='rug', border='rug2'):
    p.box(border, x0, x1, 0.0, 0.006, z0, z1); p.box(mat, x0 + 0.18, x1 - 0.18, 0.006, 0.008, z0 + 0.18, z1 - 0.18)
def piano():
    p = Piece()
    p.box('dkwood', -0.75, 0.75, 0.0, 1.3, 0.0, 0.32); p.box('dkwood', -0.75, 0.75, 0.62, 0.76, 0.32, 0.62)
    p.box('porcelain', -0.68, 0.68, 0.76, 0.78, 0.36, 0.56)
    for k in range(36):
        x = -0.66 + k * 0.0375
        if k % 7 not in (2, 6): p.box('dark', x + 0.012, x + 0.03, 0.78, 0.8, 0.44, 0.56)
    for s in (-1, 1): p.box('dkwood', s * 0.7 - 0.05, s * 0.7 + 0.05, 0.0, 0.62, 0.5, 0.6)
    p.cham('dkwood', -0.4, 0.4, 0.0, 0.48, 0.75, 1.1, 0.01)
    p.box('dkwood', -0.5, 0.5, 0.95, 1.2, 0.3, 0.34)
    return p
def parlor_set():
    """Sala de estar (pivo: centro do tapete): tapete, sofa e 2 poltronas em volta da mesa de cha, abajur de pe."""
    p = Piece(); rug(p, -1.7, 1.7, -1.3, 1.3)
    p.merge(sofa_v(2.0), rot_y(180, (0, 0, 1.25)))
    for s in (-1, 1): p.merge(armchair(), rot_y(-90 * s, (s * 1.55, 0, -0.2)))
    p.merge(tea_table(0.4, 0.48), tr(0, 0, -0.1))
    lathe(p, 'brass', [(0.18, 0.0), (0.18, 0.03), (0.03, 0.06), (0.02, 1.5)], 1.7, 1.2, 0.0, 12); lathe(p, 'velvet', [(0.26, 1.42), (0.14, 1.72)], 1.7, 1.2, 0.0, 16)
    return p
def chair_d(mat='velvet'):
    """Cadeira de jantar estofada com encosto alto (pivo: centro, frente +Z)."""
    p = Piece()
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): p.box('dkwood', sx * 0.2 - 0.022, sx * 0.2 + 0.022, 0.0, 0.46, sz * 0.2 - 0.022, sz * 0.2 + 0.022)
    p.cham(mat, -0.23, 0.23, 0.46, 0.53, -0.23, 0.23, 0.02)
    for s in (-1, 1): p.box('dkwood', s * 0.2 - 0.022, s * 0.2 + 0.022, 0.46, 1.1, -0.24, -0.2)
    p.cham('dkwood', -0.23, 0.23, 1.02, 1.12, -0.25, -0.19, 0.01); p.cham(mat, -0.17, 0.17, 0.6, 1.0, -0.235, -0.2, 0.01)
    return p
def dining_set():
    """Mesa de jantar de 2,2 m com toalha e 6 cadeiras, candelabros e pratos (pivo: centro da mesa; mesa ao longo de Z)."""
    p = Piece(); x, z = 0.5, 1.1
    p.cham('dkwood', -x, x, 0.72, 0.77, -z, z, 0.01)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): lathe(p, 'dkwood', [(0.04, 0.0), (0.05, 0.1), (0.03, 0.3), (0.045, 0.5), (0.035, 0.72)], sx * (x - 0.08), sz * (z - 0.1), 0.0, 10)
    p.box('linen', -x + 0.05, x - 0.05, 0.77, 0.775, -z + 0.15, z - 0.15)
    for (cx, cz, ry) in ((-0.75, -0.6, 90), (-0.75, 0.0, 90), (-0.75, 0.6, 90), (0.75, -0.6, -90), (0.75, 0.0, -90), (0.75, 0.6, -90)):
        p.merge(chair_d(), rot_y(ry, (cx, 0, cz)))
        px = cx * 0.48; p.cyl('porcelain', 0.12, 0.775, 0.785, px, cz, 16)
    for cz in (-0.45, 0.45): lathe(p, 'brass', [(0.07, 0.775), (0.02, 0.8), (0.015, 1.05), (0.04, 1.07), (0.012, 1.08), (0.012, 1.18)], 0.0, cz, 0.0, 10)
    return p
def sideboard(L1=1.6):
    p = Piece(); x = L1 / 2
    p.box('dkwood', -x, x, 0.12, 0.9, 0.0, 0.5); p.cham('dkwood', -x - 0.02, x + 0.02, 0.9, 0.94, 0.0, 0.53, 0.008)
    for xx in np.linspace(-x + 0.05, x - 0.05, 4)[:-1]: p.box('oak', xx + 0.02, xx + (L1 - 0.1) / 3 - 0.02, 0.2, 0.82, 0.5, 0.51)
    for (sx, sz) in ((-1, 0.05), (1, 0.05), (-1, 0.45), (1, 0.45)): p.box('dkwood', sx * (x - 0.05) - 0.03, sx * (x - 0.05) + 0.03, 0.0, 0.12, sz - 0.03, sz + 0.03)
    for xx in (-0.4, 0.0, 0.4): lathe(p, 'porcelain', [(0.08, 0.94), (0.11, 1.05), (0.06, 1.2), (0.08, 1.25)], xx, 0.25, 0.0, 12)
    return p
def chandelier(r=0.45, arms=6):
    """Lustre de latao (pivo: ponto no forro): corrente, haste, aro de bracos com velas de luz e pingentes."""
    p = Piece(); p.cyl('brass', 0.06, -0.03, 0.0, 0, 0, 12)
    seg_cyl(p, 'brass', (0, -0.03, 0), (0, -0.55, 0), 0.01, 6)
    lathe(p, 'brass', [(0.02, -0.55), (0.08, -0.62), (0.1, -0.75), (0.05, -0.85), (0.02, -0.95)], sec=12)
    for k in range(arms):
        a = 2 * math.pi * k / arms; x, z = r * math.cos(a), r * math.sin(a)
        seg_cyl(p, 'brass', (0, -0.78, 0), (x, -0.78, z), 0.012, 6); seg_cyl(p, 'brass', (x, -0.78, z), (x, -0.68, z), 0.012, 6)
        p.cyl('brass', 0.04, -0.69, -0.67, x, z, 10); p.cyl('linen', 0.012, -0.67, -0.55, x, z, 6); p.sphere('lamp_glass', 0.025, x, -0.53, z, 1)
    return p
def bookcase(L1=2.0, h=2.4):
    """Estante de livros com cornija (pivo: centro de tras, piso; frente +Z): 5 prateleiras com livros coloridos."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(int(L1 * 10))
    p.box('dkwood', -x, x, 0.0, h, 0.0, 0.03); p.box('dkwood', -x, x, 0.0, 0.1, 0.03, 0.36)
    for s in (-1, 1): p.box('dkwood', *sorted((s * x, s * (x - 0.04))), 0.0, h, 0.03, 0.38)
    p.cham('dkwood', -x - 0.04, x + 0.04, h, h + 0.08, 0.0, 0.42, 0.01)
    ys = np.linspace(0.1, h - 0.05, 6)
    for y in ys[1:-1]: p.box('dkwood', -x + 0.04, x - 0.04, y - 0.025, y, 0.03, 0.36)
    for (ya, yb) in zip(ys[:-1], ys[1:]):
        xx = -x + 0.05
        while xx < x - 0.1:
            w = rng.uniform(0.025, 0.05); hh = rng.uniform(0.6, 0.92) * (yb - ya - 0.04)
            p.box(['book_r', 'book_g', 'book_b', 'dkwood'][rng.integers(4)], xx, xx + w - 0.003, ya, ya + hh, 0.05, rng.uniform(0.24, 0.3)); xx += w
            if rng.random() < 0.04: xx += 0.12
    return p
def desk():
    p = Piece()
    p.cham('dkwood', -0.75, 0.75, 0.72, 0.77, -0.4, 0.4, 0.01)
    for s in (-1, 1): p.box('dkwood', *sorted((s * 0.75, s * 0.33)), 0.0, 0.72, -0.38, 0.38)
    for y in (0.15, 0.35, 0.55):
        for s in (-1, 1): p.box('brass', s * 0.54 - 0.04, s * 0.54 + 0.04, y + 0.06, y + 0.08, 0.38, 0.4)
    p.box('velvet_g', -0.6, 0.6, 0.77, 0.775, -0.3, 0.3)
    lathe(p, 'brass', [(0.08, 0.775), (0.015, 0.8), (0.015, 1.15)], 0.5, -0.2, 0.0, 10); lathe(p, 'velvet_g', [(0.16, 1.1), (0.08, 1.22)], 0.5, -0.2, 0.0, 14)
    p.box('book_r', -0.3, 0.0, 0.775, 0.81, -0.1, 0.12); p.box('linen', 0.05, 0.3, 0.775, 0.78, -0.05, 0.15)
    return p
def globe():
    p = Piece(); lathe(p, 'dkwood', [(0.22, 0.0), (0.22, 0.03), (0.04, 0.08), (0.03, 0.7), (0.06, 0.72)], sec=12)
    p.sphere('rug2', 0.22, 0, 0.95, 0, 2); m = trimesh.creation.annulus(r_min=0.24, r_max=0.26, height=0.02, sections=24); m.apply_transform(rot_y(0) @ trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.95, 0]); p.add('brass', m)
    return p
def bed4(L1=2.1, w=1.6):
    """Cama de casal com dossel (pivo: centro da cabeceira; cama para +Z): 4 colunas torneadas, cabeceira entalhada, colchao,
    colcha, travesseiros, armacao do dossel com sanefa."""
    p = Piece(); x = w / 2; ht = 2.3
    for (sx, sz) in ((-1, 0.06), (1, 0.06), (-1, L1 - 0.06), (1, L1 - 0.06)):
        lathe(p, 'dkwood', [(0.06, 0.0), (0.06, 0.4), (0.04, 0.5), (0.05, 0.9), (0.03, 1.3), (0.035, ht)], sx * (x + 0.02), sz, 0.0, 10)
    p.cham('dkwood', -x, x, 0.3, 1.3, 0.02, 0.1, 0.01); p.cham('dkwood', -x, x, 0.3, 0.7, L1 - 0.1, L1 - 0.02, 0.01)
    p.box('dkwood', -x, x, 0.25, 0.4, 0.1, L1 - 0.1); p.cham('linen', -x + 0.03, x - 0.03, 0.4, 0.62, 0.12, L1 - 0.12, 0.04)
    p.cham('velvet', -x - 0.02, x + 0.02, 0.5, 0.66, 0.7, L1 - 0.08, 0.03)
    for s in (-1, 1): p.cham('linen', s * 0.38 - 0.32, s * 0.38 + 0.32, 0.62, 0.78, 0.15, 0.5, 0.06)
    for (a, b, c, d) in ((-x - 0.04, x + 0.04, 0.02, 0.1), (-x - 0.04, x + 0.04, L1 - 0.1, L1 - 0.02), (-x - 0.04, -x + 0.04, 0.02, L1 - 0.02), (x - 0.04, x + 0.04, 0.02, L1 - 0.02)):
        p.box('dkwood', a, b, ht - 0.08, ht, c, d); p.box('velvet', a - 0.01 * (b - a < 0.1), b + 0.01 * (b - a < 0.1), ht - 0.32, ht - 0.08, c, d) if (b - a) < 0.1 or True else None
    return p
def wardrobe(L1=1.1):
    p = Piece(); x = L1 / 2
    p.box('dkwood', -x, x, 0.1, 2.15, 0.0, 0.6); p.cham('dkwood', -x - 0.04, x + 0.04, 2.15, 2.25, 0.0, 0.64, 0.01)
    p.cham('dkwood', -x - 0.02, x + 0.02, 0.0, 0.12, 0.0, 0.62, 0.01)
    for s in (-1, 1): p.box('oak', *sorted((s * 0.03, s * (x - 0.05))), 0.25, 2.0, 0.6, 0.61); p.box('brass', s * 0.07 - 0.01, s * 0.07 + 0.01, 1.05, 1.2, 0.61, 0.63)
    return p
def dresser():
    p = Piece(); p.box('dkwood', -0.5, 0.5, 0.1, 0.85, 0.0, 0.5); p.cham('marble_w', -0.52, 0.52, 0.85, 0.88, 0.0, 0.52, 0.006)
    for k in range(3):
        y = 0.15 + k * 0.23; p.box('oak', -0.46, 0.46, y, y + 0.2, 0.5, 0.51)
        for s in (-1, 1): p.box('brass', s * 0.25 - 0.04, s * 0.25 + 0.04, y + 0.09, y + 0.11, 0.51, 0.53)
    for s in (-1, 1): p.box('dkwood', s * 0.44 - 0.03, s * 0.44 + 0.03, 0.88, 1.75, 0.04, 0.1)
    p.cham('dkwood', -0.42, 0.42, 1.0, 1.75, 0.04, 0.08, 0.01); p.box('glass', -0.36, 0.36, 1.06, 1.69, 0.08, 0.085)
    return p
def nightstand():
    p = Piece(); p.box('dkwood', -0.22, 0.22, 0.1, 0.62, 0.0, 0.4); p.cham('dkwood', -0.24, 0.24, 0.62, 0.65, 0.0, 0.42, 0.006)
    p.box('oak', -0.18, 0.18, 0.4, 0.56, 0.4, 0.41); p.box('brass', -0.03, 0.03, 0.47, 0.49, 0.41, 0.43)
    lathe(p, 'porcelain', [(0.08, 0.65), (0.1, 0.75), (0.04, 0.85), (0.015, 0.95)], 0.0, 0.2, 0.0, 12); lathe(p, 'linen', [(0.15, 0.92), (0.09, 1.1)], 0.0, 0.2, 0.0, 14)
    return p
def bedroom_set(fire=True):
    """Moveis do quarto (pivo: centro da cabeceira encostada na parede; cama para +Z): cama de dossel, 2 criados-mudos e tapete."""
    p = Piece(); p.merge(bed4())
    rug(p, -1.3, 1.3, 0.9, 3.0, 'rug2', 'rug')
    for s in (-1, 1): p.merge(nightstand(), tr(s * 1.1, 0, 0.0))
    return p
def clawfoot_tub():
    p = Piece()
    pts = [(0.36 * math.cos(a) * (1.0 if math.cos(a) > 0 else 1.0), 0.0, 0.8 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
    for (ya, yb, sc) in ((0.15, 0.62, 1.0),):
        p.hull('porcelain', [(x * 0.92, ya, z * 0.95) for (x, _, z) in pts] + [(x, yb, z) for (x, _, z) in pts])
    p.hull('dark', [(x * 0.85, 0.62, z * 0.9) for (x, _, z) in pts] + [(x * 0.85, 0.625, z * 0.9) for (x, _, z) in pts]) if False else None
    p.hull('water', [(x * 0.86, 0.5, z * 0.9) for (x, _, z) in pts] + [(x * 0.86, 0.605, z * 0.9) for (x, _, z) in pts])
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        p.hull('brass', [(sx * 0.26 + dx, y, sz * 0.58 + dz) for dx in (-0.04, 0.04) for dz in (-0.04, 0.04) for y in (0.2,)] + [(sx * 0.3, 0.0, sz * 0.64)]); p.sphere('brass', 0.035, sx * 0.3, 0.03, sz * 0.64, 1)
    seg_cyl(p, 'brass', (0.0, 0.62, -0.78), (0.0, 0.95, -0.82), 0.015, 6); seg_cyl(p, 'brass', (0.0, 0.95, -0.82), (0.0, 0.85, -0.68), 0.012, 6)
    return p
def toilet_tank():
    """Vaso com caixa alta de madeira, cano e corrente (pivo: face da parede, piso; frente +Z)."""
    p = Piece()
    lathe(p, 'porcelain', [(0.12, 0.0), (0.14, 0.1), (0.13, 0.25), (0.19, 0.38), (0.2, 0.4), (0.0, 0.4)], 0.0, 0.38, 0.0, 16)
    p.hull('porcelain', [(x * 0.17, y, z) for x in (-1, 1) for z in (0.12, 0.38) for y in (0.0, 0.4)])
    p.cham('oak', -0.21, 0.21, 0.42, 0.46, 0.14, 0.6, 0.02)
    p.cham('oak', -0.25, 0.25, 1.75, 2.05, 0.0, 0.22, 0.01); seg_cyl(p, 'brass', (0.0, 1.75, 0.08), (0.0, 0.42, 0.24), 0.02, 8)
    seg_cyl(p, 'brass', (0.18, 1.75, 0.18), (0.18, 1.3, 0.2), 0.004, 4); p.sphere('porcelain', 0.025, 0.18, 1.28, 0.2, 1)
    return p
def pedestal_sink():
    p = Piece(); lathe(p, 'porcelain', [(0.16, 0.0), (0.12, 0.08), (0.09, 0.6), (0.18, 0.78)], 0.0, 0.25, 0.0, 16)
    p.cham('porcelain', -0.3, 0.3, 0.78, 0.86, 0.0, 0.48, 0.03); p.box('water', -0.2, 0.2, 0.84, 0.865, 0.12, 0.4) if False else None
    for s in (-1, 1): seg_cyl(p, 'brass', (s * 0.12, 0.86, 0.06), (s * 0.12, 0.96, 0.06), 0.012, 6); p.sphere('porcelain', 0.025, s * 0.12, 0.98, 0.06, 1)
    seg_cyl(p, 'brass', (0, 0.86, 0.04), (0, 0.98, 0.04), 0.014, 6); seg_cyl(p, 'brass', (0, 0.98, 0.04), (0, 0.96, 0.16), 0.012, 6)
    p.cham('brass', -0.3, 0.3, 1.15, 1.95, 0.0, 0.03, 0.01); p.box('glass', -0.25, 0.25, 1.2, 1.9, 0.03, 0.035)
    return p
def radiator(n=10):
    """Radiador de ferro fundido com colunas (pivo: centro de tras, piso)."""
    p = Piece(); x = n * 0.065 / 2
    for i in range(n):
        xx = -x + (i + 0.5) * 0.065; p.cham('iron', xx - 0.028, xx + 0.028, 0.12, 0.72, 0.06, 0.2, 0.012)
    for y in (0.16, 0.68): seg_cyl(p, 'iron', (-x, y, 0.13), (x, y, 0.13), 0.025, 8)
    for s in (-1, 1): p.box('iron', s * (x - 0.03) - 0.02, s * (x - 0.03) + 0.02, 0.0, 0.12, 0.1, 0.16)
    return p
def kitchen_range():
    """Fogao a lenha de ferro (pivo: face da parede, piso; frente +Z): corpo, 6 bocas, forno, prateleira de aquecer, cano para a chamine."""
    p = Piece()
    p.cham('stove', -0.65, 0.65, 0.12, 0.82, 0.12, 0.8, 0.02)
    for (sx, sz) in ((-1, 0.18), (1, 0.18), (-1, 0.74), (1, 0.74)): lathe(p, 'stove', [(0.04, 0.0), (0.05, 0.06), (0.03, 0.12)], sx * 0.6, sz, 0.0, 8)
    p.box('stove', -0.68, 0.68, 0.82, 0.85, 0.1, 0.84)
    for (x, z) in ((-0.42, 0.3), (0.0, 0.3), (0.42, 0.3), (-0.42, 0.62), (0.0, 0.62), (0.42, 0.62)): p.cyl('dark', 0.13, 0.85, 0.86, x, z, 16); p.cyl('stove', 0.03, 0.86, 0.875, x, z, 8)
    for x in (-0.33, 0.33): p.cham('stove', x - 0.27, x + 0.27, 0.22, 0.7, 0.8, 0.82, 0.006); p.box('steel' if False else 'brass', x - 0.12, x + 0.12, 0.62, 0.64, 0.82, 0.85)
    p.box('stove', -0.65, 0.65, 1.3, 1.34, 0.12, 0.42); seg_cyl(p, 'stove', (-0.6, 0.85, 0.14), (-0.6, 1.3, 0.14), 0.015, 6); seg_cyl(p, 'stove', (0.6, 0.85, 0.14), (0.6, 1.3, 0.14), 0.015, 6)
    p.cyl('stove', 0.1, 0.85, 1.9, 0.0, 0.25, 14); seg_cyl(p, 'stove', (0.0, 1.9, 0.25), (0.0, 1.95, 0.0), 0.1, 14)
    seg_cyl(p, 'brass', (-0.6, 0.78, 0.84), (0.6, 0.78, 0.84), 0.012, 6)
    return p
def counter(L1=1.6, sink=False):
    """Bancada de cozinha com armarios almofadados e tampo de marmore (pivo: centro de tras, piso; frente +Z); com pia de louca e torneira."""
    p = Piece(); x = L1 / 2
    p.box('cream', -x, x, 0.1, 0.86, 0.0, 0.58); p.box('dkwood', -x + 0.02, x - 0.02, 0.0, 0.1, 0.0, 0.52)
    n = max(1, int(L1 / 0.5))
    for i in range(n):
        xa = -x + i * L1 / n; p.box('cream', xa + 0.04, xa + L1 / n - 0.04, 0.16, 0.8, 0.58, 0.6); p.box('brass', xa + L1 / n / 2 - 0.04, xa + L1 / n / 2 + 0.04, 0.72, 0.74, 0.6, 0.62)
    p.cham('marble_w', -x - 0.02, x + 0.02, 0.86, 0.9, 0.0, 0.62, 0.006)
    if sink:
        p.box('porcelain', -0.35, 0.35, 0.9, 1.0, 0.08, 0.55); p.box('dark', -0.3, 0.3, 0.995, 1.003, 0.12, 0.5)
        seg_cyl(p, 'brass', (0, 0.9, 0.05), (0, 1.25, 0.05), 0.014, 6); seg_cyl(p, 'brass', (0, 1.25, 0.05), (0, 1.15, 0.28), 0.012, 6)
    return p
def icebox():
    p = Piece(); p.box('oak', -0.4, 0.4, 0.1, 1.5, 0.0, 0.6)
    for (y0, y1) in ((0.2, 0.75), (0.85, 1.4)):
        for s in (-1, 1): p.cham('oak', *sorted((s * 0.02, s * 0.36)), y0, y1, 0.6, 0.62, 0.006)
        p.box('brass', 0.25, 0.32, (y0 + y1) / 2 - 0.02, (y0 + y1) / 2 + 0.02, 0.62, 0.65)
    for (sx, sz) in ((-1, 0.05), (1, 0.05), (-1, 0.55), (1, 0.55)): p.box('dkwood', sx * 0.35 - 0.03, sx * 0.35 + 0.03, 0.0, 0.1, sz - 0.03, sz + 0.03)
    return p
def work_table():
    p = Piece(); p.cham('oak', -0.8, 0.8, 0.82, 0.88, -0.45, 0.45, 0.01)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): p.box('oak', sx * 0.72 - 0.035, sx * 0.72 + 0.035, 0.0, 0.82, sz * 0.38 - 0.035, sz * 0.38 + 0.035)
    p.box('oak', -0.7, 0.7, 0.15, 0.18, -0.36, 0.36)
    for (x, z) in ((-0.4, 0.1), (0.2, -0.1)): lathe(p, 'cream', [(0.12, 0.88), (0.16, 0.98), (0.17, 1.0)], x, z, 0.0, 14)
    return p
def pantry_shelf(L1=2.4):
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(7)
    for s in (-1, 1): p.box('oak', *sorted((s * x, s * (x - 0.04))), 0.0, 2.0, 0.0, 0.4)
    for y in (0.3, 0.75, 1.2, 1.65, 2.0):
        p.box('oak', -x, x, y - 0.03, y, 0.0, 0.4)
        if y < 1.9:
            for xx in np.arange(-x + 0.12, x - 0.1, 0.18): lathe(p, ['cream', 'clay', 'porcelain'][rng.integers(3)], [(0.06, y), (0.065, y + 0.18), (0.04, y + 0.22), (0.045, y + 0.25)], xx, 0.2, 0.0, 10)
    return p
def console():
    p = Piece(); p.cham('marble_w', -0.6, 0.6, 0.8, 0.84, 0.0, 0.4, 0.006)
    for s in (-1, 1): lathe(p, 'dkwood', [(0.04, 0.0), (0.05, 0.1), (0.03, 0.4), (0.045, 0.6), (0.035, 0.8)], s * 0.52, 0.3, 0.0, 10)
    p.box('dkwood', -0.58, 0.58, 0.68, 0.8, 0.0, 0.38); p.box('dkwood', -0.55, 0.55, 0.0, 0.03, 0.0, 0.3)
    p.cham('brass', -0.45, 0.45, 1.05, 2.05, 0.0, 0.04, 0.01); p.box('glass', -0.39, 0.39, 1.11, 1.99, 0.04, 0.045)
    lathe(p, 'porcelain', [(0.07, 0.84), (0.12, 1.0), (0.06, 1.2), (0.08, 1.25)], 0.3, 0.2, 0.0, 12); p.sphere('flower', 0.12, 0.3, 1.33, 0.2, 1)
    return p
def grandfather_clock():
    p = Piece(); p.box('dkwood', -0.26, 0.26, 0.0, 0.3, 0.0, 0.32); p.box('dkwood', -0.2, 0.2, 0.3, 1.5, 0.0, 0.26)
    p.box('dkwood', -0.26, 0.26, 1.5, 2.1, 0.0, 0.32); p.cham('dkwood', -0.3, 0.3, 2.1, 2.2, 0.0, 0.36, 0.01)
    p.cyl('cream', 0.17, 1.8, 1.8, 0, 0.32, 20) if False else p.box('cream', -0.17, 0.17, 1.62, 1.98, 0.32, 0.325)
    p.box('glass', -0.14, 0.14, 0.45, 1.4, 0.26, 0.265); seg_cyl(p, 'brass', (0, 1.38, 0.2), (0, 0.75, 0.2), 0.006, 4); p.cyl('brass', 0.07, 0.72, 0.73, 0, 0.2, 14) if False else p.sphere('brass', 0.07, 0, 0.72, 0.2, 1)
    for a in (0.3, 1.9): seg_cyl(p, 'dark', (0, 1.8, 0.326), (0.12 * math.sin(a), 1.8 + 0.12 * math.cos(a), 0.326), 0.006, 4)
    return p
def window_seat():
    """Banco estofado em volta das janelas do torreao (pivo: centro do torreao, cota do piso)."""
    p = Piece(); ri = TR - T / math.cos(HA) - 0.02
    for k in [k for k in range(NSIDE) if k not in (6, 7, 8)]:
        q = Piece(); w = 2 * ri * math.sin(HA) + 0.3
        q.box('dkwood', -w / 2, w / 2, 0.0, 0.38, -0.45, 0.0); q.cham('velvet_g', -w / 2, w / 2, 0.38, 0.46, -0.44, 0.0, 0.02)
        q = clipped(q, [((0, 0, -ri * math.cos(HA)), (math.cos(HA), 0, math.sin(HA))), ((0, 0, -ri * math.cos(HA)), (-math.cos(HA), 0, math.sin(HA)))])
        th = (k + 0.5) * 2 * HA; p.merge(q, rot_y(90 - math.degrees(th), (ri * math.cos(HA) * math.cos(th), 0, ri * math.cos(HA) * math.sin(th))))
    return p

# ============================================================================ terreno, jardim, gradil e galpao
SX0, SX1, SZ0, SZ1 = -15.0, 12.0, -12.0, 19.0
GY = -0.2                                                  # fundo do terreno (as pecas do chao nascem dentro dele)
FC = (0.0, 13.6)                                           # chafariz
DRIVE = sbox(-10.9, -11.0, -8.25, 17.3)
STREETW = sbox(SX0, 17.3, SX1, SZ1)
WALKS = unary_union([sbox(-0.8, 10.1, 0.8, 17.3), Point(*FC).buffer(3.0, 48).difference(Point(*FC).buffer(2.0, 48)),
                     sbox(-8.25, 10.6, -0.8, 11.4), sbox(-8.25, -9.6, 4.8, -8.5), sbox(-11.5, -10.8, -10.9, -9.9)]).difference(Point(*FC).buffer(2.0, 48))
BEDS = [sbox(-7.0, 6.0, -3.32, 6.8), sbox(3.32, 6.0, 4.9, 6.8)]
FOOT = unary_union([sbox(-HX, -HZ, HX, HZ), poly_ngon(TC[0], TC[1], TR + 0.01), sbox(-3.32, 6.0, 3.32, 9.05), sbox(-1.53, 9.0, 1.53, 10.26),
                    sbox(3.18, -8.55, 4.82, -6.0), sbox(-8.25, 0.85, -7.0, 3.75), sbox(-14.55, -11.65, -11.45, -9.05)])
def paving(poly, y1, joints=1.5, mat='concrete', gap=0.006):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + gap, z + gap, x + joints - gap, z + joints - gap).intersection(poly); ext_y(p, mat, q, GY, y1)
    ext_y(p, 'dark', poly.buffer(-0.002), GY, y1 - 0.008)
    return p
def site():
    """Terreno (pivo: origem): gramado, entrada de cascalho, caminhos de tijolo, anel em volta do chafariz, calcada da rua com juntas,
    canteiros de flores junto da casa."""
    p = Piece(); box_ = sbox(SX0, SZ0, SX1, SZ1)
    ext_y(p, 'gravel', DRIVE.intersection(box_).difference(FOOT), GY, 0.03)
    ext_y(p, 'paver', WALKS.difference(DRIVE).difference(FOOT), GY, 0.05)
    p.merge(paving(STREETW, 0.08))
    p.box('concrete', SX0, SX1, GY, 0.12, SZ1 - 0.15, SZ1)
    lawn = box_.difference(unary_union([DRIVE, WALKS, STREETW, FOOT, Point(*FC).buffer(2.0, 48)] + BEDS))
    ext_y(p, 'grass', lawn, GY, 0.06)
    rng = np.random.default_rng(11)
    for b in BEDS:
        ext_y(p, 'mulch', b, GY, 0.1); x0, z0, x1, z1 = b.bounds
        for x in np.arange(x0 + 0.25, x1 - 0.2, 0.42):
            for z in (z0 + 0.25, z0 + 0.58):
                p.sphere('leaf', 0.17, x + rng.uniform(-0.05, 0.05), 0.2, z, 1)
                for _ in range(3): p.sphere(['flower', 'flower_y'][rng.integers(2)], 0.05, x + rng.uniform(-0.12, 0.12), 0.33, z + rng.uniform(-0.1, 0.1), 0)
    return p
def fountain():
    """Chafariz de 2 bacias (pivo: centro, chao): tanque redondo de pedra com capa, espelho d'agua, pedestal torneado, bacia de baixo
    com cortina d'agua, bacia de cima e pinaculo."""
    p = Piece(); P0 = Point(0, 0)
    ext_y(p, 'stone_t', P0.buffer(2.0, 48).difference(P0.buffer(1.72, 48)), GY, 0.45)
    ext_y(p, 'stone_t', P0.buffer(2.07, 48).difference(P0.buffer(1.66, 48)), 0.45, 0.53)
    ext_y(p, 'water', P0.buffer(1.72, 48), GY, 0.36)
    lathe(p, 'stone_t', [(0.42, 0.36), (0.36, 0.46), (0.2, 0.56), (0.15, 0.75), (0.13, 0.85), (0.2, 0.95)], sec=20)
    lathe(p, 'stone_t', [(0.2, 0.95), (0.96, 1.12), (0.96, 1.2)], sec=28)
    m = trimesh.creation.annulus(r_min=0.86, r_max=0.96, height=0.06, sections=28); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 1.23, 0]); p.add('stone_t', m)
    p.cyl('water', 0.865, 1.2, 1.235, 0, 0, 28)
    m = trimesh.creation.annulus(r_min=0.968, r_max=0.978, height=0.82, sections=28); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.77, 0]); p.add('water', m)
    lathe(p, 'stone_t', [(0.14, 1.2), (0.09, 1.4), (0.07, 1.6), (0.11, 1.72)], sec=16)
    lathe(p, 'stone_t', [(0.11, 1.72), (0.5, 1.86), (0.5, 1.9)], sec=24)
    m = trimesh.creation.annulus(r_min=0.44, r_max=0.5, height=0.04, sections=24); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 1.92, 0]); p.add('stone_t', m)
    p.cyl('water', 0.445, 1.9, 1.925, 0, 0, 24)
    lathe(p, 'stone_t', [(0.08, 1.925), (0.06, 2.05), (0.11, 2.15), (0.07, 2.3), (0.0, 2.42)], sec=14)
    for k in range(8):
        a = 2 * math.pi * k / 8; seg_cyl(p, 'water', (0.12 * math.cos(a), 2.2, 0.12 * math.sin(a)), (0.4 * math.cos(a), 1.93, 0.4 * math.sin(a)), 0.012, 4)
    return p
def post_lantern(p, y):
    """Lanterna de ferro sobre pilar (base em y): pe, gaiola com vidro aceso, chapeu e pinaculo."""
    p.cham('iron', -0.12, 0.12, y, y + 0.05, -0.12, 0.12, 0.01); lathe(p, 'iron', [(0.05, y + 0.05), (0.035, y + 0.25)], sec=10)
    yb, yt = y + 0.25, y + 0.6
    p.box('iron', -0.13, 0.13, yb, yb + 0.03, -0.13, 0.13); p.box('lamp_glass', -0.11, 0.11, yb + 0.03, yt, -0.11, 0.11)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('iron', sx * 0.12 - 0.012, sx * 0.12 + 0.012, yb, yt, sz * 0.12 - 0.012, sz * 0.12 + 0.012)
    p.hull('iron', [(sx * 0.16, yt, sz * 0.16) for sx in (-1, 1) for sz in (-1, 1)] + [(0, yt + 0.16, 0)]); p.sphere('iron', 0.03, 0, yt + 0.19, 0, 1)
def fence_pier(lamp=False):
    """Pilar de tijolo do gradil (pivo: centro, chao): base de pedra, fiadas, capa com cornija e bola de pedra ou lanterna."""
    p = Piece(); h = 1.75
    p.cham('stone_t', -0.29, 0.29, GY, 0.32, -0.29, 0.29, 0.01); p.box('brick', -0.25, 0.25, 0.32, h, -0.25, 0.25)
    p.cham('stone_t', -0.32, 0.32, h, h + 0.07, -0.32, 0.32, 0.008); p.cham('stone_t', -0.28, 0.28, h + 0.07, h + 0.14, -0.28, 0.28, 0.008)
    if lamp: post_lantern(p, h + 0.14)
    else: p.cham('stone_t', -0.12, 0.12, h + 0.14, h + 0.2, -0.12, 0.12, 0.006); p.sphere('stone_t', 0.15, 0, h + 0.34, 0, 2)
    return p
def fence_panel(L1):
    """Trecho do gradil entre 2 pilares (pivo: centro, chao; ao longo de X): mureta de tijolo com capa de pedra, 2 travessas e
    barras de ferro com ponta de lanca, arcos no alto."""
    p = Piece(); x = L1 / 2
    p.box('brick', -x, x, GY, 0.42, -0.15, 0.15); p.cham('stone_t', -x, x, 0.42, 0.5, -0.19, 0.19, 0.008)
    for y in (0.62, 1.38): p.box('iron', -x, x, y, y + 0.035, -0.015, 0.015)
    n = max(2, int(round((L1 - 0.06) / 0.12)))
    for i in range(n):
        xx = -x + 0.03 + (i + 0.5) * (L1 - 0.06) / n
        p.box('iron', xx - 0.009, xx + 0.009, 0.5, 1.56, -0.009, 0.009)
        p.hull('iron', [(xx + dx, 1.56, dz) for dx in (-0.022, 0.022) for dz in (-0.012, 0.012)] + [(xx, 1.66, 0.0)])
        if i < n - 1:
            xm = xx + (L1 - 0.06) / n / 2
            for k in range(6):
                a0, a1 = math.pi * k / 6, math.pi * (k + 1) / 6
                seg_cyl(p, 'iron', (xm + 0.06 * math.cos(a0), 1.3 - 0.06 * math.sin(a0) * 0 + 0.06 * math.sin(a0), 0), (xm + 0.06 * math.cos(a1), 1.3 + 0.06 * math.sin(a1), 0), 0.005, 4) if False else None
    for xm in np.arange(-x + 0.25, x - 0.2, 0.5):
        for k in range(8): a = k * math.pi / 4; seg_cyl(p, 'iron', (xm + 0.09 * math.cos(a), 1.0 + 0.09 * math.sin(a), 0), (xm + 0.09 * math.cos(a + math.pi / 4), 1.0 + 0.09 * math.sin(a + math.pi / 4), 0), 0.006, 4)
    return p
def gate_leaf(w=1.49, h=1.7):
    """Folha de portao de ferro (pivo: dobradica, embaixo; para +X): quadro, barras com lanca, travessa com circulos, arco no topo."""
    p = Piece(); t = 0.02
    p.box('iron', 0.0, 0.04, 0.05, h, -t, t); p.box('iron', w - 0.04, w, 0.05, h, -t, t)
    for y in (0.05, 0.55, 1.2): p.box('iron', 0.04, w - 0.04, y, y + 0.04, -t, t)
    n = max(3, int(w / 0.12))
    for i in range(1, n):
        xx = i * w / n; top = h + 0.18 * math.sin(math.pi * xx / w)
        p.box('iron', xx - 0.009, xx + 0.009, 0.09, top, -0.01, 0.01)
        p.hull('iron', [(xx + dx, top, dz) for dx in (-0.022, 0.022) for dz in (-0.012, 0.012)] + [(xx, top + 0.1, 0.0)])
    pts = [(xx, h + 0.18 * math.sin(math.pi * xx / w)) for xx in np.linspace(0.02, w - 0.02, 12)]
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'iron', (xa, ya, 0), (xb, yb, 0), 0.016, 6)
    for xm in np.arange(0.18, w - 0.1, 0.3):
        for k in range(8): a = k * math.pi / 4; seg_cyl(p, 'iron', (xm + 0.1 * math.cos(a), 0.88 + 0.1 * math.sin(a), 0), (xm + 0.1 * math.cos(a + math.pi / 4), 0.88 + 0.1 * math.sin(a + math.pi / 4), 0), 0.007, 4)
    p.sphere('brass', 0.03, w - 0.1, 1.0, 0.03, 1)
    return p
def shed():
    """Galpao de jardim (pivo: centro, chao): base de concreto, paredes de tabuas com tabeiras, janela de guilhotina na face +Z,
    porta na face +X com degrau, telhado de 2 aguas de ardosia com cumeeira e beirais, prateleira de vasos por dentro."""
    p = Piece(); X, Z, H, R = 1.5, 1.25, 2.4, 3.2
    xs = [-X, -X + 0.1, -0.4, 0.4, X - 0.1, X]; zs = [-Z, -Z + 0.1, -0.45, 0.45, Z - 0.1, Z]; ys = [0.0, 0.15, 1.2, 1.9, 2.2, H]
    def cell(i, j, k):
        if not (i in (0, 4) or k in (0, 4)): return None
        if i == 4 and k == 2 and 1 <= j <= 3: return None
        if k == 4 and i == 2 and j == 2: return None
        return 'concrete' if j == 0 else 'siding'
    for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)
    p.box('deck', -X + 0.1, X - 0.1, 0.0, 0.15, -Z + 0.1, Z - 0.1)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('trim', *sorted((sx * (X + 0.03), sx * (X - 0.07))), 0.15, H, *sorted((sz * (Z + 0.03), sz * (Z - 0.07))))
    for zz in (-0.55, 0.45): p.box('trim', X, X + 0.03, 0.15, 2.3, zz, zz + 0.1)
    p.box('trim', X, X + 0.03, 2.2, 2.3, -0.55, 0.55); p.cham('stone_t', X, X + 0.4, GY, 0.075, -0.5, 0.5, 0.006)
    for xx in (-0.5, 0.4): p.box('trim', xx, xx + 0.1, 1.2, 1.9, Z, Z + 0.03)
    p.box('trim', -0.5, 0.5, 1.9, 2.0, Z, Z + 0.03); p.cham('trim', -0.5, 0.5, 1.14, 1.204, Z - 0.02, Z + 0.08, 0.005)
    p.box('frame', -0.4, 0.4, 1.2, 1.9, Z - 0.07, Z - 0.05) if False else None
    sash(p, -0.4, 0.4, 1.2, 1.57, Z - 0.075, Z - 0.045, 2, 0.05); sash(p, -0.4, 0.4, 1.53, 1.9, Z - 0.04, Z - 0.01, 2, 0.04)
    slope = (R - H) / Z; ov = 0.3
    for s in (-1, 1):
        ye = H - ov * slope
        for c in range(7):
            f0, f1 = c / 7, (c + 1.3) / 7
            za, zb = s * (Z + ov) * (1 - f0), s * (Z + ov) * (1 - min(1.0, f1))
            ya, yb = ye + (R - ye) * f0, ye + (R - ye) * min(1.0, f1)
            p.hull('shingles', [(x, y + dy, z) for x in (-X - 0.25, X + 0.25) for (z, y) in ((za, ya), (zb, yb)) for dy in (0.0, 0.04)])
        p.hull('trim', [(x, y, z) for x in (-X - 0.25, X + 0.25) for (z, y) in ((s * (Z + ov), ye - 0.18), (s * (Z + ov - 0.03), ye - 0.18), (s * (Z + ov), ye), (s * (Z + ov - 0.03), ye))])
    for x in (-X, X - 0.1): p.hull('siding', [(xx, y, z) for xx in (x, x + 0.1) for (z, y) in ((-Z, H), (Z, H), (0.0, R))])
    for sx in (-1, 1):
        for s in (-1, 1):
            xa, xb = sorted((sx * (X + 0.27), sx * (X + 0.22)))
            p.hull('trim', [(xx, y + dy, z) for xx in (xa, xb) for (z, y) in ((s * (Z + ov), H - ov * slope), (0.0, R + 0.04)) for dy in (-0.16, 0.0)])
    p.hull('ridge', [(x, R + 0.05 + dy, dz) for x in (-X - 0.25, X + 0.25) for dy in (0.0, 0.06) for dz in (-0.08, 0.08)])
    p.merge(pantry_shelf(2.0), rot_y(90, (-X + 0.1, 0.15, 0.0)))
    for (x, z, sc) in ((0.6, -0.8, 0.3), (0.95, -0.85, 0.22)): p.cham('oak', x - sc, x + sc, 0.15, 0.15 + sc * 1.4, z - sc, z + sc, 0.01)
    return p
def door_leaf_shed(w=0.86, h=2.02, t=0.04):
    """Porta de tabuas com travessas em Z (pivo: dobradica, embaixo)."""
    p = Piece(); n = 6
    for i in range(n): p.cham('siding', i * w / n + 0.002, (i + 1) * w / n - 0.002, 0.0, h, -t / 2, t / 2, 0.004)
    for y in (0.25, h - 0.35): p.box('trim', 0.05, w - 0.05, y, y + 0.12, t / 2, t / 2 + 0.025)
    p.hull('trim', [(x, y, z) for (x, y) in ((0.05, 0.37), (0.17, 0.37), (w - 0.17, h - 0.35), (w - 0.05, h - 0.35)) for z in (t / 2, t / 2 + 0.025)])
    for y in (0.3, h - 0.3): p.box('iron', -0.02, 0.3, y - 0.02, y + 0.02, t / 2 + 0.025, t / 2 + 0.035)
    p.box('iron', w - 0.12, w - 0.08, 1.0, 1.15, t / 2 + 0.025, t / 2 + 0.05)
    return p
def tree(h=6.5, r=2.0, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.2, 0.0), (0.14, 0.5), (0.1, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(9):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    ext_y(p, 'mulch', Point(0, 0).buffer(0.8, 20), 0.0, 0.02)
    return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def topiary():
    """Buxinho podado em 3 bolas num vaso de barro (pivo: centro, chao)."""
    p = Piece(); lathe(p, 'clay', [(0.24, 0.0), (0.3, 0.45), (0.34, 0.5), (0.34, 0.56), (0.3, 0.56)], sec=16)
    p.cyl('mulch', 0.29, 0.5, 0.55, 0, 0, 16); seg_cyl(p, 'bark', (0, 0.55, 0), (0, 1.5, 0), 0.03, 6)
    for (y, r) in ((0.85, 0.3), (1.32, 0.22), (1.68, 0.15)): p.sphere('hedge', r, 0, y, 0, 2)
    return p
def hedge(L1=4.0, seed=5):
    """Cerca viva podada (pivo: centro, chao; ao longo de X)."""
    p = Piece(); rng = np.random.default_rng(seed); x = L1 / 2
    p.cham('hedge', -x, x, GY, 1.35, -0.38, 0.38, 0.1)
    for xx in np.arange(-x + 0.35, x - 0.3, 0.55):
        for (y, z) in ((1.3, 0.0), (0.8, 0.33), (0.8, -0.33)): p.sphere('hedge', rng.uniform(0.2, 0.26), xx + rng.uniform(-0.1, 0.1), y, z, 1)
    return p
def lamp_post():
    """Poste de ferro fundido com lanterna (pivo: centro, chao): base canelada, fuste, travessa de escada e lanterna."""
    p = Piece()
    lathe(p, 'iron', [(0.18, GY), (0.18, 0.1), (0.15, 0.2), (0.1, 0.3), (0.11, 0.7), (0.07, 0.8), (0.05, 2.6), (0.07, 2.7)], sec=16)
    for a in (0, math.pi): seg_cyl(p, 'iron', (0, 2.5, 0), (0.28 * math.cos(a), 2.5, 0.28 * math.sin(a)), 0.012, 6)
    post_lantern(p, 2.7)
    return p
def garden_bench():
    """Banco de jardim com laterais de ferro e ripas de madeira (pivo: centro, chao; frente +Z)."""
    p = Piece(); L1 = 1.6
    for s in (-1, 1):
        x = s * 0.72; pts = [(x, 0.0, 0.25), (x, 0.42, 0.22), (x, 0.42, -0.18), (x, 0.0, -0.22), (x, 0.42, -0.18), (x, 0.9, -0.3)]
        for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'iron', a, b, 0.022, 6)
        seg_cyl(p, 'iron', (x, 0.42, 0.22), (x, 0.62, 0.2), 0.02, 6); seg_cyl(p, 'iron', (x, 0.62, 0.2), (x, 0.62, -0.05), 0.02, 6)
    for i in range(5): z = -0.17 + i * 0.08; p.cham('oak', -L1 / 2, L1 / 2, 0.42, 0.45, z, z + 0.065, 0.005)
    for i in range(3):
        y = 0.55 + i * 0.12; z = -0.2 - (y - 0.45) * 0.22
        p.cham('oak', -L1 / 2, L1 / 2, y, y + 0.08, z - 0.015, z + 0.015, 0.005)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)

pieces = {}
for fl in (0, 1):
    for k in ('win', 'plain', 'chim') + (('door', 'bdoor', 'sdoor') if fl == 0 else ('bal',)): pieces[f'w{fl}_{k}'] = wall(k, fl)
    pieces[f'corner{fl}'] = corner(fl); pieces[f'turret{fl}'] = turret_ring(fl)
pieces.update({
    'turret2': turret_ring(2), 'turret_floor': turret_floor('floor'), 'turret_slab': turret_floor('slab'), 'turret_top': turret_floor('top'),
    'turret_roof': turret_roof(), 'hip': hip(),
    'roof_deck': roof_deck(), 'roof_turret': roof_turret_corner(), 'dormer': dormer(), 'chimney': chimney('ext'), 'chimney_roof': chimney('roof'),
    'downspout': downspout_piece(YE + 0.02), 'porch': porch(), 'porte_cochere': porte_cochere(), 'back_stoop': back_stoop(),
    'floor_ground': floor_piece('g'), 'floor_upper': floor_piece('1'), 'ceiling_attic': floor_piece('e'), 'plan_ground': plan('g'), 'plan_upper': plan('1'),
    'stair': stair(), 'stair_rail': stair_rail_1(),
    'fireplace': fireplace(), 'parlor_set': parlor_set(), 'piano': piano(), 'dining_set': dining_set(), 'sideboard': sideboard(),
    'chandelier': chandelier(), 'chandelier_s': chandelier(0.32, 5), 'bookcase': bookcase(), 'desk': desk(), 'globe': globe(),
    'bedroom_set': bedroom_set(), 'wardrobe': wardrobe(), 'dresser': dresser(), 'clawfoot_tub': clawfoot_tub(), 'toilet': toilet_tank(),
    'pedestal_sink': pedestal_sink(), 'radiator': radiator(), 'kitchen_range': kitchen_range(), 'counter_sink': counter(1.3, True),
    'icebox': icebox(), 'work_table': work_table(), 'pantry': pantry_shelf(2.4), 'console': console(), 'grandfather_clock': grandfather_clock(),
    'window_seat': window_seat(),
    'site': site(), 'fountain': fountain(), 'fence_pier': fence_pier(), 'fence_pier_lamp': fence_pier(True),
    'gate_leaf': gate_leaf(1.49), 'gate_leaf_s': gate_leaf(0.79, 1.4), 'shed': shed(), 'door_leaf_shed': door_leaf_shed(),
    'tree': tree(), 'tree_b': tree(5.2, 1.6, 'leaf2', 4), 'bush': bush(), 'topiary': topiary(), 'hedge': hedge(), 'lamp_post': lamp_post(),
    'garden_bench': garden_bench(),
    'door_leaf_front': door_front(0.93, 2.3), 'door_leaf_back': door_back(0.87, 2.2), 'door_leaf_french': door_back(0.535, 2.27),
    'door_leaf_interior': door_interior(0.86, 2.08), 'player_scale_ref': player_ref()})
FENCE_L = {}
def panel_name(Ln):
    k = f'fence_{int(round(Ln * 100))}'
    if k not in pieces: pieces[k] = fence_panel(Ln)
    return k

# ============================================================================ montagem
FRONT = [{-6: 'win', -4: 'win', -2: 'plain', 0: 'door', 2: 'plain', 4: 'win'}, {-6: 'win', -4: 'win', -2: 'plain', 0: 'bal', 2: 'plain', 4: 'win'}]
BACK = [{-6: 'win', -4: 'win', -2: 'plain', 0: 'win', 2: 'plain', 4: 'bdoor', 6: 'win'}, {-6: 'win', -4: 'win', -2: 'plain', 0: 'win', 2: 'plain', 4: 'win', 6: 'win'}]
WEST = [{-5: 'win', -3: 'chim', -1: 'plain', 1: 'win', 3: 'sdoor', 5: 'win'}, {-5: 'win', -3: 'chim', -1: 'win', 1: 'bal', 3: 'win', 5: 'win'}]
EAST = [{-5: 'win', -3: 'chim', -1: 'win', 1: 'win', 3: 'win'}] * 2
for fl, y in ((0, Y0), (1, Y1)):
    tg = [f'floor{fl}', 'ext']
    for x, k in FRONT[fl].items(): put(f'w{fl}_{k}', x, y, HZ, 0, tg + ['front'])
    for x, k in BACK[fl].items(): put(f'w{fl}_{k}', x, y, -HZ, 180, tg + ['back'])
    for z, k in WEST[fl].items(): put(f'w{fl}_{k}', -HX, y, z, -90, tg + ['left'])
    for z, k in EAST[fl].items(): put(f'w{fl}_{k}', HX, y, z, 90, tg + ['right'])
    for (x, z, ry) in ((-HX, HZ, -90), (HX, -HZ, 90), (-HX, -HZ, 180)): put(f'corner{fl}', x, y, z, ry, tg)
    put(f'turret{fl}', TC[0], y, TC[1], 0, tg + ['front'])
    put('window_seat', TC[0], y, TC[1], 0, [f'floor{fl}'])
put('turret2', TC[0], YE, TC[1], 0, ['roof', 'ext']); put('turret_roof', TC[0], YE + TTOP, TC[1], 0, ['roof', 'ext'])
put('turret_floor', TC[0], Y0, TC[1], 0, ['floor0']); put('turret_slab', TC[0], Y1, TC[1], 0, ['floor1']); put('turret_top', TC[0], YE, TC[1], 0, ['roof'])
# portas de fachada
put('door_leaf_front', -0.465, Y0 + 0.014, HZ - 0.13, 0, ['floor0', 'front', 'ext'], door=90)
hx, hz = hinge(4.0, -HZ, 180, -0.437, -0.13); put('door_leaf_back', hx, Y0 + 0.014, hz, 180, ['floor0', 'back', 'ext'], door=90)
hx, hz = hinge(-HX, 3.0, -90, -0.437, -0.13); put('door_leaf_back', hx, Y0 + 0.014, hz, -90, ['floor0', 'left', 'ext'], door=90)
for (cx, cz, ry, tg) in ((0.0, HZ, 0, 'front'), (-HX, 1.0, -90, 'left')):
    hx, hz = hinge(cx, cz, ry, -0.539, -0.13); put('door_leaf_french', hx, Y1 + 0.014, hz, ry, ['floor1', tg, 'ext'], door=90)
    hx, hz = hinge(cx, cz, ry, 0.539, -0.13); put('door_leaf_french', hx, Y1 + 0.014, hz, ry + 180, ['floor1', tg, 'ext'], door=-90)
# telhado
def strip_name(a, b):
    """Faixa do telhado com os rincoes nas posicoes locais a (esquerda) e b (direita) das quinas da casa; longe demais = sem corte."""
    a = a if a > -5.95 else -99; b = b if b < 5.95 else 99
    k = 'roof' + ('' if a == -99 else f'_l{-a:g}') + ('' if b == 99 else f'_r{b:g}')
    if k not in pieces: pieces[k] = roof_strip(float(a), float(b))
    return k
for c in (-6, -4, -2, 0, 2, 4): put(strip_name(-HX - c, HX - c), c, YE, HZ, 0, ['roof'])
for c in (-6, -4, -2, 0, 2, 4, 6): put(strip_name(c - HX, c + HX), c, YE, -HZ, 180, ['roof'])
for c in (-5, -3, -1, 1, 3, 5): put(strip_name(-HZ - c, HZ - c), -HX, YE, c, -90, ['roof'])
for c in (-5, -3, -1, 1, 3): put(strip_name(c - HZ, c + HZ), HX, YE, c, 90, ['roof'])
for (x, z, ry) in ((-HX, HZ, -90), (HX, -HZ, 90), (-HX, -HZ, 180)): put('hip', x, YE, z, ry, ['roof'])
put('roof_turret', HX, YE, HZ, 0, ['roof']); put('roof_deck', 0, YE, 0, 0, ['roof'])
for (x, z, ry) in ((-4, HZ, 0), (-4, -HZ, 180), (4, -HZ, 180), (-HX, 1, -90), (HX, -1, 90)): put('dormer', x, YE, z, ry, ['roof'])
put('chimney', -HX, 0, -3, -90, ['ext', 'left']); put('chimney', HX, 0, -3, 90, ['ext', 'right']); put('chimney_roof', -4.5, YE, -0.8, 0, ['roof'])
for (x, z, ry) in ((-6.7, HZ, 0), (6.7, -HZ, 180), (-6.7, -HZ, 180), (HX, -5.7, 90)): put('downspout', x, 0, z, ry, ['ext'])
put('ceiling_attic', 0, YE, 0, 0, ['roof'])
# varanda, porte-cochere, escadinha
put('porch', 0, 0, HZ, 0, ['front', 'ext']); put('porte_cochere', -HX, 0, 1.4, -90, ['left', 'ext']); put('back_stoop', 4.0, 0, -HZ, 180, ['back', 'ext'])
# pisos, paredes, escadaria, portas internas
put('floor_ground', 0, Y0, 0, 0, ['floor0']); put('floor_upper', 0, Y1, 0, 0, ['floor1'])
put('plan_ground', 0, Y0, 0, 0, ['floor0']); put('plan_upper', 0, Y1, 0, 0, ['floor1'])
put('stair', 0, Y0, 0, 0, ['floor0']); put('stair_rail', 0, Y1, 0, 0, ['floor1'])
DOORS = [(Y0, 'floor0', -3.0, -1), (Y0, 'floor0', -4.6, 1), (Y1, 'floor1', 4.6, -1), (Y1, 'floor1', -3.0, -1), (Y1, 'floor1', 3.0, 1), (Y1, 'floor1', -4.6, 1)]
for (y, tg, c, s) in DOORS: put('door_leaf_interior', s * HALL, y + 0.01, c - 0.43, -90, [tg], door=90 * s)
# terreo
g = ['floor0']; y = Y0
put('fireplace', -4.4, y, 0.07, 0, g); put('parlor_set', -4.4, y, 2.6, 0, g); put('piano', -2.07, y, 4.9, -90, g); put('radiator', -6.0, y, ZI, 180, g)
put('dining_set', -4.4, y, -2.9, 0, g); put('fireplace', -XI, y, -3.0, 90, g); put('sideboard', -4.4, y, -0.07, 180, g); put('radiator', -6.0, y, -ZI, 0, g)
put('bookcase', 4.4, y, 0.07, 0, g); put('bookcase', 2.07, y, 1.15, 90, g); put('desk', 4.2, y, 3.0, 0, g); put('globe', 3.0, y, 4.8, 0, g); put('radiator', XI, y, 3.0, -90, g)
put('kitchen_range', XI, y, -3.0, -90, g); put('counter_sink', 6.0, y, -ZI, 0, g); put('icebox', 3.0, y, -0.07, 180, g); put('work_table', 4.6, y, -2.6, 0, g)
put('pantry', 2.07, y, -2.4, 90, g)
put('console', -1.93, y, -1.2, 90, g); put('grandfather_clock', -1.93, y, -4.8, 90, g)
for (x, z) in ((-4.4, 2.6), (-4.4, -2.9), (4.4, 2.6), (0.0, 3.4)): put('chandelier', x, y + CEIL, z, 0, g)
# 2o andar
g = ['floor1']; y = Y1
put('bedroom_set', -2.07, y, 2.0, -90, g); put('fireplace', -4.4, y, 0.07, 0, g); put('wardrobe', -2.65, y, ZI, 180, g)
put('bedroom_set', -4.0, y, -0.07, 180, g); put('fireplace', -XI, y, -3.0, 90, g); put('wardrobe', -2.65, y, -ZI, 0, g)
put('bedroom_set', 4.4, y, 0.07, 0, g); put('wardrobe', 2.07, y, 4.4, 90, g); put('dresser', 2.75, y, ZI, 180, g); put('radiator', XI, y, 1.0, -90, g)
put('clawfoot_tub', XI - 0.42, y, -1.65, 0, g); put('toilet', 5.0, y, -ZI, 0, g); put('pedestal_sink', 3.2, y, -0.07, 180, g); put('radiator', 6.0, y, -ZI, 0, g)
put('console', -1.93, y, 0.0, 90, g)
for (x, z) in ((-4.6, 3.3), (-4.4, -2.9), (4.4, 2.6), (4.4, -2.9)): put('chandelier_s', x, y + CEIL, z, 0, g)
put('chandelier', 0.0, y + CEIL, 3.4, 0, g)
# terreno
put('site', 0, 0, 0, 0, ['site']); put('fountain', FC[0], 0, FC[1], 0, ['site'])
PIERS = [-14.75, -13.05, -11.35, -7.85, -5.6, -3.3, -1.05, 1.05, 3.3, 5.6, 7.85, 10.1, 11.75]
GATES = {(-11.35, -7.85), (-1.05, 1.05)}
for x in PIERS: put('fence_pier_lamp' if x in (-11.35, -7.85, -1.05, 1.05) else 'fence_pier', x, 0, 17.0, 0, ['site'])
for a, b in zip(PIERS[:-1], PIERS[1:]):
    if (a, b) in GATES: continue
    put(panel_name(round(b - a - 0.5, 3)), (a + b) / 2, 0, 17.0, 0, ['site'])
for (x, ry, d, k) in ((-11.095, 0, 90, 'gate_leaf'), (-8.105, 180, -90, 'gate_leaf'), (-0.795, 0, 90, 'gate_leaf_s'), (0.795, 180, -90, 'gate_leaf_s')):
    put(k, x, 0.0, 17.0, ry, ['site'], door=d)
put('shed', -13.0, 0, -10.35, 0, ['site'])
put('door_leaf_shed', -13.0 + 1.45, 0.152, -10.35 - 0.43, -90, ['site'], door=90)
for z in np.arange(-6.5, 15.6, 4.0): put('hedge', -14.6, 0, z, 90, ['site'])
for z in np.arange(-9.5, 14.6, 4.0): put('hedge', 11.6, 0, z, 90, ['site'])
for x in np.arange(-6.9, 9.2, 4.0): put('hedge', x, 0, -11.6, 0, ['site'])
for (x, z, k) in ((-12.6, 12.0, 'tree'), (-12.6, 4.0, 'tree_b'), (-12.6, -4.0, 'tree'), (9.8, -3.0, 'tree_b'), (9.7, 11.5, 'tree'),
                  (-5.5, 14.4, 'tree_b'), (6.0, 14.4, 'tree_b'), (-3.0, -10.3, 'tree'), (8.0, -9.8, 'tree_b')): put(k, x, 0.06, z, 0, ['site'])
for (x, z) in ((-2.2, 9.6), (2.2, 9.6), (-2.55, 11.05), (2.55, 11.05), (-2.55, 16.15), (2.55, 16.15)): put('topiary', x, 0.06, z, 0, ['site'])
for (x, z) in ((-7.65, -5.2), (-7.65, 5.3), (7.6, -5.0), (7.6, -1.3), (-4.0, -6.6), (-1.0, -6.6), (1.6, -6.6)): put('bush', x, 0.06, z, 0, ['site'])
for (x, z) in ((-11.5, 8.0), (-11.5, -6.0), (-1.3, 10.45), (1.3, 10.45)): put('lamp_post', x, 0.0, z, 0, ['site'])
put('garden_bench', -3.6, 0.06, FC[1], 90, ['site']); put('garden_bench', 3.6, 0.06, FC[1], -90, ['site'])
put('player_scale_ref', 0.0, 0.05, 11.0); put('player_scale_ref', 0.0, Y0, 1.0, 0, ['floor0'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': Y0,
                       'house': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 2, 'floor_height': HF, 'levels': [Y0, Y1], 'wall_top': YE},
                       'turret': {'center': list(TC), 'radius': TR, 'sides': NSIDE, 'top_level': TTOP},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
                       'roof': 'hip roof at 45 degrees with slate courses, flat deck with iron cresting, 5 dormers, 3 chimneys, conical turret roof',
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
