"""Kit 40: observatorio neoclassico, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Pavilhao central de 10 x 12 m e 2 alas de 6 x 8 m, de pedra calcaria, sobre um terraco de 1,8 m com muro de arrimo, balaustrada e
escadaria; terreo com embasamento rusticado, janelas altas com moldura de pedra, frontao reto e peitoril; cunhais nas quinas;
entablamento com arquitrave, friso, denticulos e cornija; balaustrada na cobertura. Portico de 4 colunas com forro em caixotoes e um
atico liso com medalhao (planeta com anel e estrela, sem texto). Na cobertura, tambor de 16 faces com a cupula grande de cobre
(fenda aberta, portinhola amarela recolhida) e, sobre as alas, 2 tambores de 12 faces com cupulas menores (fenda fechada).
Dentro: saguao com piso xadrez de marmore, escadaria de pedra que sobe direto para a sala da cupula, planetario mecanico, vitrines,
globo celeste, paineis de mapa estelar sem texto; biblioteca na ala oeste; sala de instrumentos na ala leste. Na cupula grande, o
telescopio refrator na coluna de ferro; nas pequenas, lunetas menores.
Fora: terraco de lajotas com urnas e postes, gramado com caminho, relogio de sol com esfera armilar, canteiros, arvores e bancos.
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
configurar(cores={'stone': (224, 216, 198), 'stone_r': (204, 196, 178), 'trim': (234, 228, 212), 'copper': (92, 152, 126), 'copper_d': (70, 122, 102),
                  'shutter': (216, 172, 70), 'iron': (40, 46, 46), 'brass': (198, 162, 84), 'gold': (222, 182, 72), 'sash': (58, 74, 64), 'frame': (58, 74, 64),
                  'door': (88, 54, 36), 'dkwood': (94, 60, 40), 'oak': (162, 114, 70), 'plaster': (238, 232, 218), 'ceil': (246, 242, 232),
                  'marble_w': (236, 232, 224), 'marble_k': (62, 66, 74), 'marble_r': (150, 70, 60), 'base': (92, 60, 42), 'paver': (198, 190, 172),
                  'concrete': (184, 180, 172), 'membrane': (120, 120, 118), 'grass': (100, 148, 70), 'gravel': (200, 190, 168), 'soil': (96, 70, 50),
                  'leaf': (84, 130, 62), 'leaf2': (110, 146, 70), 'hedge': (60, 100, 52), 'bark': (96, 72, 52), 'flower': (210, 72, 96), 'flower_y': (236, 196, 60),
                  'flower_b': (120, 110, 210), 'velvet_g': (52, 96, 72), 'leather': (120, 62, 40), 'book_r': (140, 42, 38), 'book_g': (46, 90, 62),
                  'book_b': (44, 62, 112), 'linen': (242, 238, 226), 'chart': (28, 42, 82), 'chalk': (232, 232, 224), 'board': (38, 52, 46), 'cream': (232, 224, 196),
                  'paint_w': (240, 240, 236), 'dome_in': (228, 224, 212), 'lamp_glass': (255, 236, 190), 'rock': (70, 62, 58), 'felt': (40, 90, 60),
                  'dark': (30, 30, 32)},
           texturas={'stone': 'stone', 'stone_r': 'stone', 'paver': 'stone', 'plaster': 'plaster', 'oak': 'planks', 'dkwood': 'planks',
                     'grass': 'render', 'gravel': 'render', 'concrete': 'render', 'membrane': 'render'},
           out=OUT)
D.METAL.update({'iron', 'brass', 'gold', 'copper', 'copper_d'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.4; t_ = 0.14                                # modulo, parede externa de pedra, parede interna
TY = 1.8; Y0 = TY + 0.15                                   # topo do terraco (12 degraus de 15 cm) e piso do predio
CEIL = 4.05; HW = 4.5; HC = 4.45                           # forro, topo da laje da cobertura, topo do nucleo das paredes (sobre o piso)
UY = Y0 + HW                                               # piso da cobertura e das cupulas
PL = 0.84                                                  # topo do embasamento rusticado
WIN = (-0.55, 0.55, 1.2, 3.2)                              # vao das janelas (x0, x1, peitoril, verga)
EA = 3.70                                                  # base da arquitrave
CX, CZ = 5.0, 6.0                                          # pavilhao central: x de -5 a 5, z de -6 a 6
WX, WZ = 11.0, 4.0                                         # alas: x de 5 a 11 (e -11 a -5), z de -4 a 4
PX, PZ = 3.6, 8.4                                          # portico: x de -3,6 a 3,6, z de 6 a 8,4
PCOL = [-3.1, -1.05, 1.05, 3.1]; PCZ = 7.95                # colunas do portico
QL = (0.24, 0.14)                                          # comprimento dos cunhais (longo, curto)
NS = 25; RS = HW / NS; GS = 0.28                           # escadaria: espelhos de 18 cm, pisos de 28 cm
XS0, XS1 = 0.9, 2.1                                        # largura da escadaria
ZT = 1.62; ZB = ZT - (NS - 1) * GS                         # chegada (na sala da cupula) e inicio (no saguao)
HOLE = (XS0, -2.3, XS1, ZT)                                # vao na laje
MAIN = dict(c=(0.0, 0.0), n=16, R=3.6, td=0.35, dh=3.0, door=4, wins=(0, 2, 6, 8, 10, 12, 14), slit=True, sw=1.1)
WING = dict(c=(8.0, 0.0), n=12, R=2.2, td=0.3, dh=2.6, door=3, wins=(0, 6, 9), slit=False, sw=0.7)

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

def orient_cw(poly):
    from shapely.geometry.polygon import orient
    return orient(poly, sign=-1.0)
def edges_of(poly):
    """Arestas (x0, z0, x1, z1) do contorno externo, no sentido horario (normal local +Z para fora em along())."""
    c = list(orient_cw(poly).exterior.coords); return [(a[0], a[1], b[0], b[1]) for a, b in zip(c[:-1], c[1:]) if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-6]
def off(poly, d): return poly.buffer(d, join_style=2, mitre_limit=10)
def ring(p, mat, poly, d_out, d_in, y0, y1, cut=None):
    r = off(poly, d_out).difference(off(poly, d_in))
    if cut is not None: r = r.difference(cut)
    ext_y(p, mat, r, y0, y1)
def rot_poly(poly, deg):
    from shapely import affinity
    return affinity.rotate(poly, deg, origin=(0, 0))

WALL_OUT = unary_union([sbox(-CX, -CZ, CX, CZ), sbox(-WX, -WZ, WX, WZ)]).buffer(0)
PORT = sbox(-PX, CZ, PX, PZ)
ROOF_OUT = unary_union([WALL_OUT, sbox(-PX, CZ - 0.01, PX, PZ)]).buffer(0)
INNER = off(WALL_OUT, -T)
HALL = sbox(-CX + T, -CZ + T, CX - T, CZ - T)
WINGS = [sbox(-WX + T, -WZ + T, -CX, WZ - T), sbox(CX, -WZ + T, WX - T, WZ - T)]
DOOR_GAPS = unary_union([sbox(-1.07, CZ - 0.6, 1.07, CZ + 0.6), sbox(-0.62, -CZ - 0.6, 0.62, -CZ + 0.6)])
ATTIC = sbox(-PX, PZ - 0.45, PX, PZ)

# ============================================================================ fachadas (pivo: face externa, cota do piso; parede em -Z)
def wall_core(p, holes, xs0=(-W / 2, W / 2), h=HC, y_bot=-0.15, layers=(-T, -0.2, 0.0)):
    xs = sorted(set(list(xs0) + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y_bot, 0.0, CEIL, h] + [v for hh in holes for v in hh[2:]]))
    ys = [v for v in ys if y_bot <= v <= h]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return 'stone' if cy < 0 else ('plaster' if cy < CEIL else 'concrete')
        return 'stone'
    for m, mesh in grid_solid(xs, ys, list(layers), cell).items(): p.add(m, mesh)
COURSES = [-0.15, 0.18, 0.51, PL]
def rustic(p, gaps=(), x0=-W / 2, x1=W / 2):
    """Embasamento rusticado: 3 fiadas de blocos chanfrados salientes 4 cm, juntas desencontradas."""
    for j, (ya, yb) in enumerate(zip(COURSES[:-1], COURSES[1:])):
        js = [x0, 0.0, x1] if j % 2 == 0 else [x0, -0.5, 0.5, x1]
        for (a, b) in zip(js[:-1], js[1:]):
            for (c, d) in segs_excl(gaps, a, b):
                if d - c > 0.05: p.cham('stone_r', c, d, ya, yb, 0.0, 0.04, 0.012)
BASE_IN = [(-T, 0.0), (-T - 0.018, 0.0), (-T - 0.018, 0.14), (-T - 0.009, 0.155), (-T, 0.158)]
def win_detail(p, a=WIN[0], b=WIN[1], y0=WIN[2], y1=WIN[3]):
    """Janela alta de pedra: moldura com orelhas, friso e cornija na verga, peitoril com mensulas; por dentro, caixilho com 2 folhas
    de guilhotina e bandeira fixa, peitoril de madeira, guarnicao e avental."""
    # por fora
    for s in (-1, 1):
        xa, xb = sorted((s * abs(a), s * (abs(a) + 0.12))); p.box('trim', xa, xb, y0, y1 + 0.12, 0.0, 0.05)
    p.box('trim', a - 0.16, b + 0.16, y1, y1 + 0.14, 0.0, 0.05)                                     # verga com orelhas
    p.box('trim', a - 0.12, b + 0.12, y1 + 0.14, y1 + 0.27, 0.0, 0.03)                              # friso
    prof_x(p, 'trim', a - 0.18, b + 0.18, [(0.0, y1 + 0.27), (0.07, y1 + 0.27), (0.09, y1 + 0.3), (0.12, y1 + 0.33), (0.12, y1 + 0.37), (0.0, y1 + 0.39)])
    prof_x(p, 'trim', a - 0.16, b + 0.16, [(0.0, y0 - 0.1), (0.075, y0 - 0.1), (0.09, y0 - 0.085), (0.09, y0 - 0.025), (0.05, y0), (0.0, y0)])   # peitoril
    p.box('trim', a, b, PL + 0.14, y0 - 0.1, 0.0, 0.022)                                            # avental
    for s in (-1, 1):
        xc = s * (abs(a) + 0.07); p.hull('trim', [(xc + dx, y, z) for dx in (-0.04, 0.04) for (y, z) in ((y0 - 0.1, 0.0), (y0 - 0.1, 0.07), (PL + 0.14, 0.0), (PL + 0.14, 0.03))])
    # caixilho
    z0, z1 = -0.25, -0.14; f = 0.06; yt = y1 - 0.58
    p.box('frame', a, a + f, y0, y1, z0, z1); p.box('frame', b - f, b, y0, y1, z0, z1)
    p.box('frame', a + f, b - f, y1 - f, y1, z0, z1); p.box('frame', a + f, b - f, y0, y0 + 0.05, z0, z1)
    p.box('frame', a + f, b - f, yt, yt + 0.05, z0, z1)
    ym = (y0 + 0.05 + yt) / 2
    sash(p, a + f, b - f, y0 + 0.05, ym + 0.02, -0.215, -0.185, 2, 0.07)
    sash(p, a + f, b - f, ym - 0.02, yt, -0.18, -0.15, 2, 0.05)
    p.box('glass', a + f, b - f, yt + 0.05, y1 - f, -0.198, -0.192)
    for x in (a + (b - a) / 3, a + 2 * (b - a) / 3): p.box('frame', x - 0.012, x + 0.012, yt + 0.05, y1 - f, -0.205, -0.185)
    # por dentro
    p.cham('oak', a, b, y0 - 0.03, y0 + 0.004, -T - 0.04, -0.25, 0.005)
    for s in (-1, 1):
        xa, xb = sorted((s * abs(a), s * (abs(a) + 0.1))); prof_y(p, 'trim', y0 + 0.004, y1 + 0.1, crect(xa, xb, -T - 0.022, -T, 0.005, (1, 1, 0, 0)))
    p.box('trim', a - 0.1, b + 0.1, y1, y1 + 0.1, -T - 0.022, -T)
    p.box('trim', a - 0.05, b + 0.05, y0 - 0.22, y0 - 0.03, -T - 0.016, -T)
def door_frame(p, a, b, h, z0=-0.3, z1=-0.1, f=0.07, mat='dkwood'):
    p.box(mat, a, a + f, 0.0, h, z0, z1); p.box(mat, b - f, b, 0.0, h, z0, z1); p.box(mat, a + f, b - f, h - f, h, z0, z1)
def wall(kind='win'):
    """Modulo de 2 m: win (janela alta), door (porta principal de 2 folhas com bandeira em leque), bdoor (porta dos fundos), plain."""
    p = Piece(); holes = []; gaps = []
    if kind == 'win': holes = [WIN]
    if kind == 'door': holes = [(-0.95, 0.95, 0.0, 3.0)]; gaps = [(-1.07, 1.07)]
    if kind == 'bdoor': holes = [(-0.5, 0.5, 0.0, 2.3)]; gaps = [(-0.62, 0.62)]
    wall_core(p, holes); rustic(p, gaps)
    if kind == 'win': win_detail(p)
    if kind == 'door':
        a, b, h = -0.95, 0.95, 3.0
        for s in (-1, 1):
            xa, xb = sorted((s * 0.95, s * 1.07)); p.box('trim', xa, xb, 0.0, h + 0.12, 0.0, 0.06)
            xa, xb = sorted((s * 0.95, s * 1.07)); prof_y(p, 'trim', 0.0, h + 0.1, crect(xa, xb, -T - 0.022, -T, 0.005, (1, 1, 0, 0)))
            xc = s * 1.13; p.hull('trim', [(xc + dx, y, z) for dx in (-0.05, 0.05) for (y, z) in ((h + 0.3, 0.0), (h + 0.3, 0.16), (h - 0.25, 0.0), (h - 0.25, 0.05))])
        p.box('trim', -1.1, 1.1, h, h + 0.14, 0.0, 0.06); p.box('trim', -1.07, 1.07, h + 0.14, h + 0.3, 0.0, 0.035)
        prof_x(p, 'trim', -1.2, 1.2, [(0.0, h + 0.3), (0.16, h + 0.3), (0.18, h + 0.33), (0.21, h + 0.37), (0.21, h + 0.42), (0.0, h + 0.45)])
        p.box('trim', -1.07, 1.07, h, h + 0.1, -T - 0.022, -T)
        door_frame(p, a, b, h)
        p.box('dkwood', a + 0.07, b - 0.07, 2.36, 2.44, -0.3, -0.1)
        p.box('glass', a + 0.07, b - 0.07, 2.44, h - 0.07, -0.203, -0.197)
        for k in range(7):
            ang = math.pi * (k + 1) / 8; ex, ey = 0.5 * math.cos(ang) * 1.8, 0.5 * math.sin(ang)
            ex = max(a + 0.08, min(b - 0.08, ex)); ey = min(h - 0.07 - 2.44, ey)
            p.seg('dkwood', (0.0, 2.44, -0.2), (ex, 2.44 + ey, -0.2), 0.022, 0.02)
        hub = trimesh.creation.cylinder(radius=0.12, height=0.03, sections=16, transform=None); hub.apply_translation([0, 2.44, -0.2])
        hub = slice_keep(hub, [0, 2.44, 0], [0, 1, 0]); p.add('dkwood', hub)
        p.cham('trim', a, b, -0.03, 0.006, -T + 0.004, 0.12, 0.005)
    if kind == 'bdoor':
        h = 2.3
        for s in (-1, 1):
            xa, xb = sorted((s * 0.5, s * 0.62)); p.box('trim', xa, xb, 0.0, h + 0.12, 0.0, 0.05)
            prof_y(p, 'trim', 0.0, h + 0.1, crect(xa, xb, -T - 0.022, -T, 0.005, (1, 1, 0, 0)))
        p.box('trim', -0.66, 0.66, h, h + 0.13, 0.0, 0.05)
        prof_x(p, 'trim', -0.76, 0.76, [(0.0, h + 0.13), (0.1, h + 0.13), (0.12, h + 0.16), (0.15, h + 0.2), (0.15, h + 0.24), (0.0, h + 0.26)])
        p.box('trim', -0.62, 0.62, h, h + 0.1, -T - 0.022, -T)
        door_frame(p, -0.5, 0.5, h)
        p.cham('trim', -0.5, 0.5, -0.03, 0.006, -T + 0.004, 0.14, 0.005)
        for s in (-1, 1): p.merge(wall_lantern(), tr(s * 0.86, 1.95, 0.0))
    for (a, b) in segs_excl(gaps, -W / 2, W / 2): prof_x(p, 'base', a, b, BASE_IN)
    return p
def corner():
    """Quina externa (pivo: quina, cota do piso; paredes em -X e -Z): nucleo saliente, blocos rusticados em L e cunhais alternados."""
    p = Piece(); e = 0.004
    p.box('stone', -T + e, e, -0.15, HC, -T + e, e)
    for j, (ya, yb) in enumerate(zip(COURSES[:-1], COURSES[1:])):
        lf, ls = (0.55, 0.35) if j % 2 == 0 else (0.35, 0.55)
        p.cham('stone_r', -lf, 0.045, ya - 0.003, yb + 0.003, -0.03, 0.045, 0.014); p.cham('stone_r', -0.03, 0.045, ya - 0.003, yb + 0.003, -ls, 0.045, 0.014)
    ys = np.linspace(PL + 0.14, EA, 9)
    for j, (ya, yb) in enumerate(zip(ys[:-1], ys[1:])):
        lf, ls = (QL[0], QL[1]) if j % 2 == 0 else (QL[1], QL[0])
        p.cham('stone', -lf, 0.03, ya, yb, -0.02, 0.03, 0.012); p.cham('stone', -0.02, 0.03, ya, yb, -ls, 0.03, 0.012)
    return p

# ============================================================================ frisos continuos, cornija e balaustrada (pivo: origem, cota do piso)
def baluster(p, x, z, y0, h, mat='trim'):
    lathe(p, mat, [(0.07, y0), (0.07, y0 + 0.05), (0.045, y0 + 0.09), (0.075, y0 + h * 0.4), (0.04, y0 + h * 0.78), (0.055, y0 + h * 0.9), (0.06, y0 + h)], x, z, 0.0, 8)
def balustrade_line(p, x0, z0, x1, z1, y0, h=0.86, sp=0.27, die=0.34, dmax=2.6, ends=(True, True), mat='trim', die_h=None):
    """Balaustrada de pedra entre 2 pontos (eixo): pedestais nas pontas e a cada 2,6 m, balaustres torneados; sem plinto/corrimao
    (vem dos aneis). Devolve as posicoes dos pedestais."""
    Ln = math.hypot(x1 - x0, z1 - z0); ux, uz = (x1 - x0) / Ln, (z1 - z0) / Ln
    nseg = max(1, int(math.ceil((Ln - die) / dmax))); dies = [i * Ln / nseg for i in range(nseg + 1)]
    out = []
    for i, t in enumerate(dies):
        if (i == 0 and not ends[0]) or (i == nseg and not ends[1]): continue
        cx, cz = x0 + ux * t, z0 + uz * t; out.append((cx, cz))
        hd = h if die_h is None else die_h
        p.cham(mat, cx - die / 2, cx + die / 2, y0, y0 + hd, cz - die / 2, cz + die / 2, 0.01)
        if die_h is not None: p.cham(mat, cx - die / 2 - 0.03, cx + die / 2 + 0.03, y0 + hd, y0 + hd + 0.06, cz - die / 2 - 0.03, cz + die / 2 + 0.03, 0.01)
    for ta, tb in zip(dies[:-1], dies[1:]):
        a = ta + (die / 2 if (ta > 0 or ends[0]) else 0.0); b = tb - (die / 2 if (tb < Ln or ends[1]) else 0.0)
        n = max(1, int(round((b - a) / sp)))
        for k in range(n):
            t = a + (k + 0.5) * (b - a) / n; baluster(p, x0 + ux * t, z0 + uz * t, y0, h, mat)
    return out
def trims():
    """Capa do embasamento, arquitrave, friso com denticulos, cornija, plinto, pedestais, balaustres e corrimao da cobertura, atico."""
    p = Piece()
    for (y0, y1, d) in ((PL, PL + 0.06, 0.075), (PL + 0.06, PL + 0.12, 0.05), (PL + 0.12, PL + 0.14, 0.03)):
        ring(p, 'trim', WALL_OUT, d, -0.02, y0, y1, DOOR_GAPS)
    for (y0, y1, d, di) in ((EA, EA + 0.12, 0.05, -0.02), (EA + 0.12, EA + 0.25, 0.07, -0.02), (EA + 0.25, 4.30, 0.04, -0.02), (4.30, 4.36, 0.11, -0.02),
                            (4.36, 4.52, 0.32, -T), (4.52, 4.58, 0.35, -T), (4.58, 4.62, 0.37, -T)):
        ring(p, 'trim', ROOF_OUT, d, di, y0, y1)
    for (x0, z0, x1, z1) in edges_of(ROOF_OUT):
        Ln = math.hypot(x1 - x0, z1 - z0); q = Piece(); n = int((Ln - 0.3) / 0.2)
        for k in range(n):
            x = 0.15 + (k + 0.5) * (Ln - 0.3) / n; q.box('trim', x - 0.05, x + 0.05, 4.18, 4.30, 0.04, 0.1)
        along(p, q, x0, z0, x1, z1)
    # balaustrada da cobertura
    cut = sbox(-PX - 1, PZ - 0.45, PX + 1, PZ + 1)
    ring(p, 'trim', ROOF_OUT, -0.03, -0.31, 4.62, 4.74, cut); ring(p, 'trim', ROOF_OUT, -0.05, -0.29, 4.74, 4.78, cut)
    ring(p, 'trim', ROOF_OUT, -0.07, -0.27, 5.36, 5.4, cut); ring(p, 'trim', ROOF_OUT, -0.02, -0.32, 5.4, 5.52, cut)
    cl = off(ROOF_OUT, -0.17)
    for (x0, z0, x1, z1) in edges_of(cl):
        if abs(z0 - (PZ - 0.17)) < 1e-6 and abs(z1 - z0) < 1e-6: continue                       # a frente do portico leva o atico
        e0 = (True, True)
        if abs(x0 - x1) < 1e-6 and abs(abs(x0) - (PX - 0.17)) < 1e-6:                          # laterais do portico: param no atico
            zz = [z0, z1]; zz = [min(z, PZ - 0.45 - 0.17) for z in zz]; z0, z1 = zz
        balustrade_line(p, x0, z0, x1, z1, 4.78, 0.58, ends=e0, die_h=0.8)
    # atico sobre o portico, com medalhao (planeta com anel e estrelas, sem texto)
    za, zb = PZ - 0.45, PZ
    p.box('stone', -PX, PX, HW, 5.9, za, zb)
    p.cham('trim', -PX - 0.04, PX + 0.04, 4.62, 4.8, za - 0.04, zb + 0.04, 0.01)
    p.cham('trim', -PX - 0.05, PX + 0.05, 5.78, 5.9, za - 0.05, zb + 0.05, 0.01); p.cham('trim', -PX - 0.1, PX + 0.1, 5.9, 6.02, za - 0.1, zb + 0.1, 0.012)
    p.cham('trim', -PX - 0.06, PX + 0.06, 6.02, 6.07, za - 0.06, zb + 0.06, 0.008)
    for (xa, xb, ya, yb) in ((-2.9, 2.9, 4.95, 5.03), (-2.9, 2.9, 5.55, 5.63), (-2.9, -2.82, 5.03, 5.55), (2.82, 2.9, 5.03, 5.55)):
        p.box('trim', xa, xb, ya, yb, zb, zb + 0.03)
    yc = 5.29; zf = zb + 0.002
    for (r, z0, z1, m) in ((0.24, zf, zf + 0.02, 'gold'), (0.1, zf + 0.02, zf + 0.045, 'trim')):
        c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=28); c.apply_translation([0, yc, (z0 + z1) / 2]); p.add(m, c)
    rg = trimesh.creation.annulus(r_min=0.13, r_max=0.19, height=0.02, sections=32); rg.apply_scale([1.0, 0.32, 1.0]); rg.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-14), [0, 0, 1]))
    rg.apply_translation([0, yc, zf + 0.04]); p.add('trim', rg)
    for s in (-1, 1):
        for (xs, sc) in ((1.5, 1.0), (2.2, 0.6), (0.9, 0.5)):
            x = s * xs; r1, r0 = 0.12 * sc, 0.025 * sc
            p.hull('gold', [(x + dx, yc + dy, z) for (dx, dy) in ((r1, 0), (-r1, 0), (0, r0), (0, -r0)) for z in (zf, zf + 0.02)])
            p.hull('gold', [(x + dx, yc + dy, z) for (dx, dy) in ((0, r1), (0, -r1), (r0, 0), (-r0, 0)) for z in (zf, zf + 0.02)])
    return p

# ============================================================================ portico (pivo: origem, cota do piso)
def column(p, x, z, h=EA):
    """Coluna jonica de pedra: plinto, base atica, fuste de 20 faces com entase, capitel com volutas e abaco."""
    p.cham('trim', x - 0.3, x + 0.3, 0.0, 0.1, z - 0.3, z + 0.3, 0.008)
    lathe(p, 'trim', [(0.28, 0.1), (0.28, 0.15), (0.25, 0.18), (0.25, 0.2), (0.27, 0.23), (0.27, 0.26), (0.23, 0.29)], x, z, 0.0, 24)
    lathe(p, 'stone', [(0.23, 0.29), (0.235, 1.2), (0.225, 2.2), (0.205, h - 0.36), (0.22, h - 0.34)], x, z, 0.0, 20)
    lathe(p, 'trim', [(0.22, h - 0.34), (0.24, h - 0.3), (0.26, h - 0.22), (0.26, h - 0.16), (0.0, h - 0.16)], x, z, 0.0, 20)
    for s in (-1, 1):
        for (r, z0, z1, m) in ((0.1, -0.26, 0.26, 'trim'), (0.04, -0.27, 0.27, 'trim')):
            c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=18); c.apply_translation([x + s * 0.24, h - 0.2, z]); p.add(m, c)
    p.box('trim', x - 0.24, x + 0.24, h - 0.3, h - 0.1, z - 0.24, z + 0.24)
    p.cham('trim', x - 0.32, x + 0.32, h - 0.1, h, z - 0.32, z + 0.32, 0.008)
def portico():
    """Portico: piso de lajotas com 1 degrau, 4 colunas jonicas, 2 pilastras na fachada, viga do entablamento, forro em caixotoes
    com rosaceas."""
    p = Piece()
    tiles(p, PORT, -0.18, 0.0, 0.6, 'paver', 0.004, 'concrete')
    for x in PCOL: column(p, x, PCZ)
    for x in (PCOL[0], PCOL[-1]):
        p.cham('trim', x - 0.26, x + 0.26, 0.0, 0.29, CZ, CZ + 0.1, 0.008); p.box('stone', x - 0.21, x + 0.21, 0.29, EA - 0.3, CZ, CZ + 0.07)
        p.cham('trim', x - 0.26, x + 0.26, EA - 0.3, EA, CZ, CZ + 0.1, 0.008)
    beam = PORT.difference(sbox(-PX + 0.6, CZ - 1.0, PX - 0.6, PZ - 0.6))
    ext_y(p, 'trim', beam, EA, CEIL - 0.01)
    x0, x1, z0, z1 = -PX + 0.6, PX - 0.6, CZ, PZ - 0.6; yb = CEIL - 0.24
    nx, nz = 5, 3; xs = np.linspace(x0, x1, nx + 1); zs = np.linspace(z0, z1, nz + 1)
    for x in xs[1:-1]: p.box('trim', x - 0.06, x + 0.06, yb, CEIL - 0.01, z0, z1)
    for z in zs[1:-1]: p.box('trim', x0, x1, yb + 0.003, CEIL - 0.01, z - 0.06, z + 0.06)
    p.box('trim', x0, x1, yb, CEIL - 0.01, z0, z0 + 0.1)
    for (a, b) in zip(xs[:-1], xs[1:]):
        for (c, d) in zip(zs[:-1], zs[1:]):
            xc, zc = (a + b) / 2, (c + d) / 2
            p.cham('trim', a + 0.1, b - 0.1, CEIL - 0.1, CEIL - 0.01, max(c + 0.1, z0 + 0.16), d - 0.1, 0.01)
            p.cyl('gold', 0.09, CEIL - 0.13, CEIL - 0.1, xc, zc, 12); p.sphere('gold', 0.035, xc, CEIL - 0.14, zc, 1)
    return p

# ============================================================================ pisos, forro e paredes internas
def tiles(p, poly, y0, y1, step, mat, gap=0.005, fill='concrete', ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step + gap, oz + j * step + gap, ox + (i + 1) * step - gap, oz + (j + 1) * step - gap).intersection(poly)
            if q.area > 1e-6: ext_y(p, mat, q, y0, y1)
    ext_y(p, fill, poly.buffer(-0.001, join_style=2), y0, y1 - 0.003)
def checker(p, poly, y0, y1, step, ma, mb, ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step, oz + j * step, ox + (i + 1) * step, oz + (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
def floor_piece():
    """Piso (pivo: origem, cota do piso): marmore xadrez com faixa vermelha no saguao, tabuado de carvalho nas alas, soleiras de marmore
    nos arcos; forro com sancas em todas as salas e medalhoes sob os lustres."""
    p = Piece(); ext_y(p, 'concrete', INNER, -0.15, -0.012)
    inner = HALL.buffer(-0.3, join_style=2)
    ext_y(p, 'marble_r', HALL.difference(inner), -0.012, 0.0); ext_y(p, 'marble_w', HALL.difference(HALL.buffer(-0.08, join_style=2)), -0.0119, 0.0001) if False else None
    checker(p, inner, -0.012, 0.0, 0.6, 'marble_w', 'marble_k', 0.0, 0.0)
    for w in WINGS: ext_y(p, 'oak', w, -0.012, 0.0)
    for s in (-1, 1):
        xa, xb = sorted((s * (CX - T), s * CX)); ext_y(p, 'marble_w', sbox(xa, -1.2, xb, 1.2), -0.012, 0.004)
    # sancas (forro)
    for r in [HALL] + WINGS:
        ext_y(p, 'trim', r.difference(r.buffer(-0.06, join_style=2)), CEIL - 0.26, CEIL - 0.01)
        ext_y(p, 'trim', r.difference(r.buffer(-0.14, join_style=2)), CEIL - 0.12, CEIL - 0.01)
        ext_y(p, 'trim', r.difference(r.buffer(-0.2, join_style=2)), CEIL - 0.05, CEIL - 0.01)
    for (x, z) in CHANDELIERS:
        p.cyl('trim', 0.4, CEIL - 0.03, CEIL - 0.01, x, z, 24); p.cyl('trim', 0.25, CEIL - 0.05, CEIL - 0.03, x, z, 20)
    return p
CHANDELIERS = [(-2.2, 2.6), (-2.2, -2.6), (3.4, 3.0), (-8.0, 0.0), (8.0, 0.0)]
def run_wall(Ln, h, cuts=(), t=t_, trim_side=0, trim=0.0):
    """Parede interna (pivo: inicio, eixo; vai para +X). cuts = (centro, largura, y0, y1, tipo): arch (arco largo com moldura de pedra
    e fecho) ou door."""
    p = Piece(); cs = [(c - w / 2, c + w / 2, y0, y1, k) for (c, w, y0, y1, k) in cuts]
    xs = sorted(set([0.0, Ln] + [v for c in cs for v in c[:2]])); ys = sorted(set([0.0, h] + [v for c in cs for v in c[2:4]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        return None if any(a < cx < b and y0 < cy < y1 for (a, b, y0, y1, _) in cs) else 'plaster'
    for m, mesh in grid_solid(xs, ys, [-t / 2, t / 2], cell).items(): p.add(m, mesh)
    for (a, b, y0, y1, k) in cs:
        if k == 'door': q = Piece(); door_casing(q, b - a, t, y1); p.merge(q, tr((a + b) / 2, 0, 0))
        if k == 'arch':
            for z in (1, -1):
                z0, z1 = sorted((z * t / 2, z * (t / 2 + 0.03)))
                for (xa, xb) in ((a - 0.15, a), (b, b + 0.15)):
                    p.box('trim', xa, xb, 0.0, y1 + 0.15, z0, z1); p.cham('trim', xa - 0.02, xb + 0.02, 0.0, 0.2, *sorted((z * t / 2, z * (t / 2 + 0.045))), 0.006)
                p.box('trim', a - 0.15, b + 0.15, y1, y1 + 0.15, z0, z1)
                zk0, zk1 = sorted((z * t / 2, z * (t / 2 + 0.06)))
                xc = (a + b) / 2; p.hull('trim', [(xc + dx, y, zz) for (dx, y) in ((-0.13, y1 - 0.08), (0.13, y1 - 0.08), (-0.17, y1 + 0.22), (0.17, y1 + 0.22)) for zz in (zk0, zk1)])
                p.box('trim', a - 0.2, b + 0.2, y1 + 0.15, y1 + 0.2, *sorted((z * t / 2, z * (t / 2 + 0.06))))
    for side in (1, -1):
        gaps = [(a - (0.17 if k == 'arch' else 0.09), b + (0.17 if k == 'arch' else 0.09)) for (a, b, y0, y1, k) in cs if y0 < 0.01]
        e = trim if side == trim_side else 0.0
        for (a, b) in segs_excl(gaps, e, Ln - e):
            if b - a > 0.02: prof_x(p, 'base', a, b, D.BASE_PROF(t) if side > 0 else [(-z, y) for (z, y) in D.BASE_PROF(t)][::-1])
    return p
def plan():
    """Paredes internas (pivo: origem, cota do piso): 2 paredes de pedra rebocada entre o saguao e as alas, com arco largo."""
    p = Piece()
    for s in (-1, 1):
        q = run_wall(2 * WZ, CEIL - 0.01, [(WZ, 2.4, 0.0, 3.3, 'arch')], T, -s, T)
        p.merge(q, rot_y(-90, (s * (CX - T / 2), 0, -WZ)))
        for zs in (-1, 1):
            xa, xb = sorted((s * (CX - T), s * CX)); za, zb = sorted((zs * (WZ - T), zs * WZ)); p.box('stone', xa, xb, -0.15, 0.0, za, zb)
    return p

# ============================================================================ escadaria do saguao (pivo: origem, cota do piso)
def stair():
    """Escadaria de pedra macica, em lance reto do saguao ate a sala da cupula: 24 pisos de marmore com bocel, 2 guarda-corpos de
    pedra com capa em rampa (ate o forro), pedestais com bola no arranque."""
    p = Piece(); x0, x1 = XS0, XS1
    yl = lambda z: (z - ZB) / GS * RS
    for i in range(1, NS):
        y = i * RS; z0, z1 = ZB + (i - 1) * GS, ZB + i * GS
        p.box('stone', x0, x1, 0.0, y - 0.03, z0, z1)
        p.cham('marble_w', x0, x1, y - 0.03, y, z0 - 0.03, z1, 0.008)
    top = lambda z: min(yl(z) + 0.98, CEIL - 0.01)
    zc = ZB + (CEIL - 0.01 - 0.98) / RS * GS
    zs = sorted(set([ZB - 0.3] + [ZB + i * GS for i in range(NS)] + ([zc] if ZB < zc < ZT else [])))
    for (xa, xb) in ((x0 - 0.14, x0 - 0.002), (x1 + 0.002, x1 + 0.14)):
        for za, zb in zip(zs[:-1], zs[1:]):
            ta, tb = top(max(za, ZB)), top(max(zb, ZB))
            if za < ZB: ta = tb = 0.98
            p.hull('stone', [(x, y, z) for x in (xa, xb) for (z, y) in ((za, 0.0), (zb, 0.0), (zb, tb - 0.06), (za, ta - 0.06))])
            zb2 = zb - 0.008 if zb >= ZT - 1e-6 else zb
            p.hull('marble_w', [(x, y, z) for x in (xa - 0.02, xb + 0.02) for (z, y) in ((za, ta - 0.06), (zb2, tb - 0.06), (zb2, tb), (za, ta))])
        xc = (xa + xb) / 2
        p.cham('stone', xc - 0.15, xc + 0.15, 0.0, 1.12, ZB - 0.62, ZB - 0.3, 0.01); p.cham('marble_w', xc - 0.18, xc + 0.18, 1.12, 1.18, ZB - 0.65, ZB - 0.27, 0.008)
        p.sphere('marble_w', 0.11, xc, 1.3, ZB - 0.46, 2)
    return p

# ============================================================================ cobertura (pivo: origem, cota do piso)
def drum_poly(cfg, r=None):
    n = cfg['n']; HA = math.pi / n; return poly_ngon(cfg['c'][0], cfg['c'][1], cfg['R'] if r is None else r, n, HA)
def roof():
    """Laje com forro, lajotas da cobertura com juntas e caimento para ralos, manta sob os tambores, vao da escadaria."""
    p = Piece(); hole = sbox(*HOLE)
    SL = off(ROOF_OUT, -T).difference(hole)
    ext_y(p, 'ceil', SL, CEIL - 0.01, CEIL); ext_y(p, 'concrete', SL, CEIL, HW - 0.012)
    drums = unary_union([drum_poly(MAIN), drum_poly(WING), rot_poly(drum_poly(WING), 180)])
    tiles(p, SL.difference(drums).difference(ATTIC.buffer(0.02, join_style=2)), HW - 0.012, HW, 0.8, 'paver', 0.005, 'concrete')
    ext_y(p, 'membrane', SL.intersection(drums), HW - 0.012, HW)
    ext_y(p, 'membrane', SL.intersection(ATTIC.buffer(0.02, join_style=2)), HW - 0.012, HW)
    for (x, z) in ((-4.3, -5.3), (4.3, -5.3), (-10.3, -3.3), (10.3, -3.3), (-10.3, 3.3), (10.3, 3.3), (-4.3, 5.3), (4.3, 5.3)): p.cyl('iron', 0.09, HW, HW + 0.02, x, z, 12)
    p.box('trim', XS0 - 0.03, XS1 + 0.03, CEIL - 0.14, CEIL - 0.01, HOLE[1] - 0.03, HOLE[1]) if False else None
    return p

# ============================================================================ tambores e cupulas
def drum(cfg):
    """Tambor de pedra (pivo: centro, piso da cobertura): faces com janelinhas de moldura, porta para a cobertura, pilastras nas quinas,
    plinto, cornija com denticulos, trilho de ferro da cupula; dentro, assoalho de carvalho e rodape."""
    p = Piece(); n = cfg['n']; R = cfg['R']; td = cfg['td']; dh = cfg['dh']; HA = math.pi / n; AP = R * math.cos(HA); FW = 2 * R * math.sin(HA)
    main = cfg['slit']; dw = 0.45 if main else 0.4; dhh = 2.15 if main else 2.08
    ww = 0.25 if main else 0.21; wy = (1.05, 1.95) if main else (0.95, 1.7)
    for k in range(n):
        q = Piece(); w2 = FW / 2 + 0.12; door = (k == cfg['door']); win = k in cfg['wins']
        holes = [(-dw, dw, 0.0, dhh)] if door else ([(-ww, ww, wy[0], wy[1])] if win else [])
        xs = sorted(set([-w2, w2] + [v for hh in holes for v in hh[:2]])); ys = sorted(set([0.0, dh - 0.04] + [v for hh in holes for v in hh[2:]]))
        def cell(i, j, kk, xs=xs, ys=ys, holes=holes):
            cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
            for (a, b, c, d) in holes:
                if a < cx < b and c < cy < d: return None
            return 'plaster' if kk == 0 else 'stone'
        for m, mesh in grid_solid(xs, ys, [-td, -td / 2, 0.0], cell).items(): q.add(m, mesh)
        if door:
            for s in (-1, 1):
                xa, xb = sorted((s * dw, s * (dw + 0.08))); q.box('trim', xa, xb, 0.0, dhh + 0.08, 0.0, 0.04)
                prof_y(q, 'trim', 0.0, dhh + 0.06, crect(xa, xb, -td - 0.02, -td, 0.004, (1, 1, 0, 0)))
            q.box('trim', -dw - 0.08, dw + 0.08, dhh, dhh + 0.08, 0.0, 0.04); q.box('trim', -dw - 0.08, dw + 0.08, dhh, dhh + 0.06, -td - 0.02, -td)
            door_frame(q, -dw, dw, dhh, -td + 0.08, -td + 0.2, 0.05)
            q.cham('trim', -dw, dw, -0.02, 0.03, -td + 0.004, 0.1, 0.005)
        if win:
            a, b = -ww, ww; y0, y1 = wy
            for s in (-1, 1):
                xa, xb = sorted((s * ww, s * (ww + 0.08))); q.box('trim', xa, xb, y0, y1 + 0.08, 0.0, 0.04)
                prof_y(q, 'trim', y0, y1 + 0.06, crect(xa, xb, -td - 0.02, -td, 0.004, (1, 1, 0, 0)))
            q.box('trim', a - 0.1, b + 0.1, y1, y1 + 0.1, 0.0, 0.045); q.box('trim', a - 0.1, b + 0.1, y1, y1 + 0.06, -td - 0.02, -td)
            prof_x(q, 'trim', a - 0.12, b + 0.12, [(0.0, y0 - 0.08), (0.07, y0 - 0.08), (0.08, y0 - 0.06), (0.08, y0 - 0.02), (0.04, y0), (0.0, y0)])
            q.box('frame', a, a + 0.04, y0, y1, -0.2, -0.12); q.box('frame', b - 0.04, b, y0, y1, -0.2, -0.12)
            q.box('frame', a + 0.04, b - 0.04, y1 - 0.04, y1, -0.2, -0.12); q.box('frame', a + 0.04, b - 0.04, y0, y0 + 0.04, -0.2, -0.12)
            q.box('frame', a + 0.04, b - 0.04, (y0 + y1) / 2 - 0.015, (y0 + y1) / 2 + 0.015, -0.18, -0.14); q.box('frame', -0.012, 0.012, y0 + 0.04, y1 - 0.04, -0.18, -0.14)
            q.box('glass', a + 0.04, b - 0.04, y0 + 0.04, y1 - 0.04, -0.163, -0.157)
            q.cham('oak', a - 0.04, b + 0.04, y0 - 0.03, y0 + 0.004, -td - 0.04, -0.2, 0.004)
        th = k * 2 * HA; c, s_ = math.cos(HA), math.sin(HA); o = (0.0, 0.0, -AP)
        q = clipped(q, [(o, (c, 0, s_)), (o, (-c, 0, s_))])
        p.merge(q, rot_y(90 - math.degrees(th), (AP * math.cos(th), 0.0, AP * math.sin(th))))
    DP = poly_ngon(0, 0, R, n, HA); DI = poly_ngon(0, 0, (AP - td) / math.cos(HA), n, HA)
    thd = cfg['door'] * 2 * HA
    gap = rot_poly(sbox(-dw - 0.08, AP - 1.0, dw + 0.08, AP + 1.0), math.degrees(thd) - 90)
    for (y0, y1, d) in ((0.0, 0.16, 0.06), (0.16, 0.24, 0.04)): ext_y(p, 'trim', off(DP, d).difference(off(DP, -0.02)).difference(gap), y0, y1)
    for (y0, y1, d, di) in ((dh - 0.36, dh - 0.26, 0.05, -0.02), (dh - 0.26, dh - 0.2, 0.1, -0.02), (dh - 0.2, dh - 0.1, 0.2, -td - 0.003), (dh - 0.1, dh, 0.24, -td - 0.003)):
        ext_y(p, 'trim', off(DP, d).difference(off(DP, di)), y0, y1)
    for k in range(n):                                                     # denticulos e pilastras nas quinas
        th = k * 2 * HA; q = Piece(); nd = max(3, int(FW / 0.16))
        for i in range(nd):
            x = -FW / 2 + 0.1 + (i + 0.5) * (FW - 0.2) / nd; q.box('trim', x - 0.035, x + 0.035, dh - 0.34, dh - 0.26, 0.05, 0.1)
        p.merge(q, rot_y(90 - math.degrees(th), (AP * math.cos(th), 0.0, AP * math.sin(th))))
        ph = th + HA; pw = 0.12 if main else 0.07
        q = Piece(); q.box('stone', -pw, pw, 0.26, dh - 0.44, -0.12, 0.045); q.cham('trim', -pw - 0.025, pw + 0.025, 0.24, 0.34, -0.12, 0.07, 0.006)
        q.cham('trim', -pw - 0.025, pw + 0.025, dh - 0.48, dh - 0.36, -0.12, 0.07, 0.006)
        p.merge(q, rot_y(90 - math.degrees(ph), (R * math.cos(ph), 0.0, R * math.sin(ph))))
    seat = Point(0, 0).buffer(R + 0.07, 64).difference(off(DI, -0.08))
    ext_y(p, 'iron', seat, dh, dh + 0.12)
    for k in range(2 * n):
        a = (k + 0.5) * math.pi / n; rr = (AP - td) - 0.04; p.cyl('iron', 0.05, dh - 0.08, dh, rr * math.cos(a), rr * math.sin(a), 10)
    hole = sbox(*HOLE) if main else Polygon()
    ext_y(p, 'oak', DI.difference(hole), 0.0, 0.03)
    ext_y(p, 'base', DI.difference(off(DI, -0.02)).difference(gap), 0.03, 0.16)
    return p
def dome(cfg):
    """Cupula de cobre (pivo: centro da base, sobre o trilho): casca de chapa com nervuras de junta, forro interno com costelas de
    madeira; fenda do observatorio (aberta na grande, com ombreiras de ferro; fechada nas pequenas) e portinhola amarela."""
    p = Piece(); R = cfg['R'] + 0.05; sw = cfg['sw']; main = cfg['slit']
    def sph(r): return trimesh.creation.uv_sphere(radius=r, count=[28, 56])
    def bx(x0, x1, y0, y1, z0, z1): return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])
    B = lambda ms, op: getattr(trimesh.boolean, op)(ms, engine='manifold')
    half = bx(-R - 1, R + 1, 0.0, R + 1, -R - 1, R + 1)
    slit = bx(-sw / 2, sw / 2, 0.32, R + 1, -R - 1, 0.35)
    cop = B([B([sph(R), sph(R - 0.045)], 'difference'), half], 'intersection')
    inn = B([B([sph(R - 0.045), sph(R - 0.14)], 'difference'), half], 'intersection')
    if main: cop = B([cop, slit], 'difference'); inn = B([inn, slit], 'difference')
    p.add('copper', cop); p.add('dome_in', inn)
    band = B([sph(R + 0.09), sph(R + 0.012)], 'difference')
    sh_box = bx(-sw / 2 - 0.1, sw / 2 + 0.1, R * math.sin(math.radians(28)), R + 1, 0.25, R + 1) if main else bx(-sw / 2 - 0.1, sw / 2 + 0.1, 0.22, R + 1, -R - 1, R + 1)
    p.add('shutter', B([band, sh_box], 'intersection'))
    if main:
        sh = B([sph(R + 0.05), sph(R - 0.2)], 'difference')
        for s in (-1, 1):
            xa, xb = sorted((s * (sw / 2 - 0.01), s * (sw / 2 + 0.06)))
            p.add('iron', B([sh, bx(xa, xb, 0.31, R + 1, -R - 1, 0.36)], 'intersection'))
        p.add('iron', B([sh, bx(-sw / 2 - 0.06, sw / 2 + 0.06, 0.31, 0.4, -R - 1, 0.0)], 'intersection'))
    for m in range(28):                                                    # nervuras externas (juntas em pe)
        lam = 2 * math.pi * m / 28
        pts = [((R + 0.006) * math.cos(f) * math.cos(lam), (R + 0.006) * math.sin(f), (R + 0.006) * math.cos(f) * math.sin(lam)) for f in np.radians(np.linspace(1.5, 78, 9))]
        for a, b in zip(pts[:-1], pts[1:]):
            mx = (a[0] + b[0]) / 2
            if abs(mx) < sw / 2 + 0.16: continue
            seg_cyl(p, 'copper_d', a, b, 0.018, 6)
    for m in range(12):                                                    # costelas internas
        lam = 2 * math.pi * (m + 0.5) / 12; r = R - 0.19
        pts = [(r * math.cos(f) * math.cos(lam), r * math.sin(f), r * math.cos(f) * math.sin(lam)) for f in np.radians(np.linspace(2, 74, 8))]
        for a, b in zip(pts[:-1], pts[1:]):
            mx, mz = (a[0] + b[0]) / 2, (a[2] + b[2]) / 2
            if main and abs(mx) < sw / 2 + 0.12 and mz < 0.45: continue
            seg_cyl(p, 'dkwood', a, b, 0.035, 6)
    sk = Point(0, 0).buffer(R + 0.03, 72).difference(Point(0, 0).buffer(R - 0.05, 72))
    ext_y(p, 'copper_d', sk, 0.0, 0.1)
    return p

# ============================================================================ telescopios e moveis da cupula (pivo: chao)
def unit(v): v = np.array(v, float); return v / np.linalg.norm(v)
def telescope_main():
    """Refrator grande na coluna de ferro fundido (pivo: centro da base, piso da cupula): base com degrau, coluna com aneis de latao,
    montagem equatorial (eixo polar a 40 graus, eixo de declinacao), tubo creme com faixas de latao e para-orvalho, focalizador e
    ocular, buscador com suportes, barra e contrapeso, mecanismo de relogio na coluna."""
    p = Piece()
    p.cham('iron', -0.62, 0.62, 0.0, 0.1, -0.62, 0.62, 0.02)
    lathe(p, 'iron', [(0.5, 0.1), (0.46, 0.18), (0.38, 0.3), (0.32, 0.45), (0.29, 1.5), (0.31, 1.62), (0.36, 1.75), (0.36, 1.85), (0.27, 1.92)], sec=20)
    for y in (0.46, 1.6): lathe(p, 'brass', [(0.335, y), (0.345, y + 0.02), (0.345, y + 0.05), (0.335, y + 0.07)], sec=20)
    for k in range(8):
        a = k * math.pi / 4; p.hull('iron', [(r * math.cos(a + da), y, r * math.sin(a + da)) for (r, y) in ((0.3, 0.5), (0.3, 1.45), (0.32, 0.5), (0.32, 1.45)) for da in (-0.05, 0.05)])
    p.cham('iron', 0.25, 0.45, 1.0, 1.3, -0.12, 0.12, 0.01); p.cyl('brass', 0.06, 1.12, 1.18, 0.45, 0.0, 12) if False else None
    m = trimesh.creation.cylinder(radius=0.07, height=0.02, sections=16); m.apply_transform(rot_y(90)); m.apply_translation([0.46, 1.15, 0.0]); p.add('brass', m)
    P = np.array([0.0, 2.15, 0.0]); seg_cyl(p, 'iron', (0, 1.85, 0), P, 0.2, 16)
    ap = unit((0, math.sin(math.radians(40)), -math.cos(math.radians(40)))); d = np.array([1.0, 0, 0])
    seg_cyl(p, 'iron', P - 0.3 * ap, P + 0.55 * ap, 0.16, 16); seg_cyl(p, 'brass', P - 0.32 * ap, P - 0.28 * ap, 0.2, 20)
    D0 = P + 0.62 * ap
    seg_cyl(p, 'iron', D0 - 0.42 * d, D0 + 0.42 * d, 0.11, 14)
    u = unit((0, math.sin(math.radians(50)), -math.cos(math.radians(50)))); C = D0 - 0.62 * d
    seg_cyl(p, 'iron', D0 - 0.42 * d, C + 0.0 * d - 0.0 * u, 0.08, 10)
    seg_cyl(p, 'cream', C - 1.3 * u, C + 2.5 * u, 0.2, 24); seg_cyl(p, 'cream', C + 2.5 * u, C + 2.9 * u, 0.225, 24)
    for t in (-1.25, -0.25, 0.25, 1.4, 2.45, 2.88): seg_cyl(p, 'brass', C + (t - 0.025) * u, C + (t + 0.025) * u, 0.215 if t < 2.5 else 0.24, 24)
    for t in (-0.25, 0.25): seg_cyl(p, 'iron', C + (t - 0.05) * u, C + (t + 0.05) * u, 0.23, 24)
    seg_cyl(p, 'brass', C - 1.3 * u, C - 1.5 * u, 0.08, 14); seg_cyl(p, 'brass', C - 1.5 * u, C - 1.62 * u, 0.05, 12)
    E = C - 1.62 * u; seg_cyl(p, 'dark', E, E - 0.12 * u, 0.025, 10)
    m = trimesh.creation.cylinder(radius=0.03, height=0.1, sections=12); m.apply_transform(rot_y(90)); m.apply_translation(C - 1.42 * u + np.array([0.11, 0, 0])); p.add('brass', m)
    nrm = unit(np.cross(d, u)); F = C + 0.34 * nrm
    seg_cyl(p, 'brass', F - 0.2 * u, F + 0.75 * u, 0.045, 12)
    for t in (0.0, 0.55): seg_cyl(p, 'brass', C + t * u + 0.2 * nrm, F + t * u, 0.012, 6)
    seg_cyl(p, 'iron', D0 + 0.42 * d, D0 + 1.05 * d, 0.03, 8); seg_cyl(p, 'iron', D0 + 0.7 * d, D0 + 0.92 * d, 0.17, 20); seg_cyl(p, 'iron', D0 + 0.94 * d, D0 + 1.0 * d, 0.1, 16)
    seg_cyl(p, 'brass', P + 0.2 * ap + np.array([0, 0, 0]), P + 0.2 * ap + 0.28 * d, 0.015, 6); p.sphere('brass', 0.035, *(P + 0.2 * ap + 0.3 * d), 1)
    return p
def telescope_small():
    """Luneta menor (pivo: base, piso da cupula): coluna de ferro, cabeca de garfo, tubo de latao com para-orvalho e ocular."""
    p = Piece(); p.cham('iron', -0.32, 0.32, 0.0, 0.06, -0.32, 0.32, 0.01)
    lathe(p, 'iron', [(0.26, 0.06), (0.2, 0.14), (0.14, 0.24), (0.12, 1.05), (0.15, 1.12), (0.15, 1.18)], sec=16)
    lathe(p, 'brass', [(0.125, 0.6), (0.135, 0.62), (0.135, 0.64), (0.125, 0.66)], sec=16)
    P = np.array([0.0, 1.32, 0.0]); seg_cyl(p, 'iron', (0, 1.18, 0), P, 0.09, 12)
    for s in (-1, 1): p.box('iron', s * 0.14 - 0.02, s * 0.14 + 0.02, P[1] - 0.05, P[1] + 0.12, -0.04, 0.04)
    seg_cyl(p, 'iron', P + (-0.16, 0.1, 0), P + (0.16, 0.1, 0), 0.025, 8)
    u = unit((0, math.sin(math.radians(45)), -math.cos(math.radians(45)))); C = P + np.array([0, 0.1, 0])
    seg_cyl(p, 'brass', C - 0.6 * u, C + 0.95 * u, 0.09, 18); seg_cyl(p, 'brass', C + 0.95 * u, C + 1.15 * u, 0.105, 18)
    for t in (-0.1, 0.1): seg_cyl(p, 'iron', C + (t - 0.03) * u, C + (t + 0.03) * u, 0.1, 18)
    seg_cyl(p, 'dark', C - 0.6 * u, C - 0.78 * u, 0.03, 10)
    seg_cyl(p, 'brass', C + 0.15 * u + (0, 0.13, 0.05), C + 0.55 * u + (0, 0.13, 0.05), 0.025, 8)
    return p
def hole_rail():
    """Gradil de ferro com corrimao de latao em volta do vao da escadaria (pivo: origem, piso da cupula)."""
    p = Piece(); x0, z0, x1, z1 = HOLE; e = 0.05
    pts = [(x0 - e, z1), (x0 - e, z0 - e), (x1 + e, z0 - e), (x1 + e, z1)]
    for (a, b) in zip(pts[:-1], pts[1:]):
        Ln = math.hypot(b[0] - a[0], b[1] - a[1]); n = int(Ln / 0.12)
        for k in range(1, n): t = k / n; x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t; p.cyl('iron', 0.012, 0.0, 0.95, x, z, 6)
        seg_cyl(p, 'brass', (a[0], 0.98, a[1]), (b[0], 0.98, b[1]), 0.03, 10); seg_cyl(p, 'iron', (a[0], 0.12, a[1]), (b[0], 0.12, b[1]), 0.015, 6)
    for (x, z) in pts:
        p.cham('iron', x - 0.04, x + 0.04, 0.0, 1.02, z - 0.04, z + 0.04, 0.006); p.sphere('brass', 0.05, x, 1.06, z, 1)
    return p
def chair(mat='leather'):
    """Cadeira de madeira com assento e encosto estofados (pivo: centro, piso; frente +Z)."""
    p = Piece()
    for (x, z) in ((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)): p.cham('dkwood', x - 0.022, x + 0.022, 0.0, 0.45, z - 0.022, z + 0.022, 0.005)
    p.cham('dkwood', -0.23, 0.23, 0.43, 0.47, -0.23, 0.23, 0.008); p.cham(mat, -0.21, 0.21, 0.47, 0.52, -0.2, 0.21, 0.02)
    for x in (-0.2, 0.2): p.cham('dkwood', x - 0.022, x + 0.022, 0.45, 0.95, -0.235, -0.19, 0.005)
    p.cham('dkwood', -0.22, 0.22, 0.86, 0.95, -0.24, -0.2, 0.008); p.cham(mat, -0.17, 0.17, 0.55, 0.84, -0.23, -0.19, 0.015)
    return p
def observer_chair():
    """Cadeira de observacao de degraus com assento regulavel (pivo: centro, piso; frente +Z)."""
    p = Piece()
    for (x, z) in ((-0.3, -0.35), (0.3, -0.35)): seg_cyl(p, 'oak', (x, 0.0, z), (x, 1.5, z + 0.2), 0.03, 8)
    for (x, z) in ((-0.3, 0.35), (0.3, 0.35)): seg_cyl(p, 'oak', (x, 0.0, z), (x, 1.5, z - 0.1), 0.03, 8)
    for i in range(4):
        y = 0.3 + i * 0.3; zf = 0.35 - (y / 1.5) * 0.45; p.cham('oak', -0.3, 0.3, y, y + 0.03, zf - 0.14, zf + 0.02, 0.006)
    p.cham('leather', -0.25, 0.25, 1.1, 1.16, -0.25, 0.05, 0.02); seg_cyl(p, 'iron', (-0.3, 1.13, -0.1), (0.3, 1.13, -0.1), 0.015, 6)
    return p
def chart_desk():
    """Mesa de cartas (pivo: centro de tras, piso; frente +Z): tampo inclinado com mapa celeste, gavetas, lampada e caderno."""
    p = Piece(); x = 0.75
    p.box('dkwood', -x, x, 0.0, 0.72, 0.0, 0.62)
    for i in range(3):
        y = 0.08 + i * 0.2
        for s in (-1, 1): p.cham('oak', *sorted((s * 0.05, s * (x - 0.05))), y, y + 0.17, 0.62, 0.64, 0.005); p.sphere('brass', 0.015, s * x * 0.5, y + 0.085, 0.65, 1)
    p.hull('dkwood', [(xx, y, z) for xx in (-x - 0.02, x + 0.02) for (y, z) in ((0.72, 0.0), (0.72, 0.68), (0.84, 0.0), (0.78, 0.68))])
    p.hull('chart', [(xx, y + 0.004, z) for xx in (-0.55, 0.55) for (y, z) in ((0.836, 0.06), (0.784, 0.62), (0.832, 0.06), (0.78, 0.62))])
    rng = np.random.default_rng(7)
    for _ in range(40):
        xx = rng.uniform(-0.52, 0.52); zz = rng.uniform(0.1, 0.6); y = 0.84 - (zz / 0.68) * 0.06 + 0.002; p.box('chalk', xx - 0.006, xx + 0.006, y, y + 0.002, zz - 0.006, zz + 0.006)
    p.box('dkwood', -x, x, 0.84, 1.15, 0.0, 0.04); p.cham('dkwood', -x, x, 1.15, 1.18, 0.0, 0.2, 0.005)
    lathe(p, 'brass', [(0.06, 1.18), (0.015, 1.2), (0.015, 1.45)], -0.55, 0.12, 0.0, 10); lathe(p, 'felt', [(0.12, 1.42), (0.05, 1.5)], -0.55, 0.12, 0.0, 14)
    p.box('book_r', 0.3, 0.55, 1.18, 1.22, 0.04, 0.18)
    return p
def flat_file():
    """Arquivo de mapas de gavetas rasas (pivo: centro de tras, piso)."""
    p = Piece(); x = 0.6; p.box('oak', -x, x, 0.05, 0.95, 0.0, 0.8); p.box('dkwood', -x + 0.02, x - 0.02, 0.0, 0.05, 0.02, 0.76)
    p.cham('dkwood', -x - 0.02, x + 0.02, 0.95, 0.99, 0.0, 0.82, 0.006)
    for i in range(6):
        y = 0.08 + i * 0.145; p.cham('oak', -x + 0.03, x - 0.03, y, y + 0.13, 0.8, 0.815, 0.004); p.box('brass', -0.12, 0.12, y + 0.05, y + 0.07, 0.815, 0.835)
    return p
def reg_clock():
    """Relogio regulador de parede com pendulo (pivo: face da parede, centro embaixo)."""
    p = Piece(); p.cham('dkwood', -0.24, 0.24, 0.0, 1.2, 0.0, 0.18, 0.01); p.cham('dkwood', -0.28, 0.28, 1.2, 1.28, 0.0, 0.22, 0.01)
    p.cham('dkwood', -0.2, 0.2, -0.12, 0.0, 0.0, 0.16, 0.01); p.box('glass', -0.19, 0.19, 0.05, 1.15, 0.18, 0.186)
    c = trimesh.creation.cylinder(radius=0.17, height=0.01, sections=28); c.apply_translation([0, 0.95, 0.177]); p.add('cream', c)
    for k in range(12): a = k * math.pi / 6; p.box('dark', 0.15 * math.cos(a) - 0.008, 0.15 * math.cos(a) + 0.008, 0.95 + 0.15 * math.sin(a) - 0.008, 0.95 + 0.15 * math.sin(a) + 0.008, 0.182, 0.185)
    p.box('dark', -0.006, 0.006, 0.95, 1.07, 0.183, 0.188); p.box('dark', -0.006, 0.08, 0.947, 0.953, 0.183, 0.188)
    seg_cyl(p, 'brass', (0, 0.75, 0.09), (0, 0.25, 0.09), 0.008, 6); c = trimesh.creation.cylinder(radius=0.07, height=0.02, sections=20); c.apply_translation([0, 0.22, 0.09]); p.add('brass', c)
    return p
def star_panel(w=1.2, h=1.4, seed=3):
    """Quadro de mapa estelar sem texto (pivo: face da parede, centro embaixo): moldura de madeira, fundo azul, estrelas, constelacoes
    ligadas por linhas e circulos de coordenadas."""
    p = Piece(); x = w / 2; rng = np.random.default_rng(seed)
    p.cham('dkwood', -x - 0.05, x + 0.05, -0.05, h + 0.05, 0.0, 0.04, 0.008); p.box('chart', -x, x, 0.0, h, 0.04, 0.046)
    for r in (0.5, 0.35):
        c = trimesh.creation.annulus(r_min=r - 0.006, r_max=r, height=0.003, sections=48); c.apply_translation([0, h / 2, 0.0475]); p.add('chalk', c)
    p.box('chalk', -x + 0.04, x - 0.04, h / 2 - 0.003, h / 2 + 0.003, 0.046, 0.049); p.box('chalk', -0.003, 0.003, 0.04, h - 0.04, 0.046, 0.049)
    stars = [(rng.uniform(-x + 0.06, x - 0.06), rng.uniform(0.06, h - 0.06)) for _ in range(60)]
    for (sx, sy) in stars:
        r = rng.choice([0.006, 0.009, 0.014]); p.box('gold' if r > 0.01 else 'chalk', sx - r, sx + r, sy - r, sy + r, 0.046, 0.052 if r > 0.01 else 0.05)
    for i in range(0, 12, 3):
        for a, b in zip(stars[i:i + 3], stars[i + 1:i + 4]): p.seg('chalk', (a[0], a[1], 0.049), (b[0], b[1], 0.049), 0.004, 0.002)
    return p

# ============================================================================ moveis do saguao e das alas (pivo: centro de tras, piso)
def orrery():
    """Planetario mecanico (pivo: centro, piso): pedestal de marmore, base de latao com engrenagens, sol dourado, 6 bracos com planetas,
    um com anel e lua."""
    p = Piece()
    p.cham('marble_k', -0.45, 0.45, 0.0, 0.1, -0.45, 0.45, 0.01); lathe(p, 'marble_w', [(0.36, 0.1), (0.3, 0.2), (0.24, 0.3), (0.22, 0.85), (0.3, 0.92), (0.36, 0.98), (0.36, 1.02)], sec=24)
    lathe(p, 'brass', [(0.32, 1.02), (0.32, 1.06), (0.26, 1.1), (0.1, 1.14), (0.04, 1.2), (0.03, 1.5)], sec=24)
    for k in range(12): a = k * math.pi / 6; p.box('brass', 0.3 * math.cos(a) - 0.02, 0.3 * math.cos(a) + 0.02, 1.02, 1.07, 0.3 * math.sin(a) - 0.02, 0.3 * math.sin(a) + 0.02)
    p.sphere('gold', 0.12, 0, 1.6, 0, 2)
    cols = ['marble_r', 'cream', 'book_b', 'marble_r', 'leather', 'cream']
    for i, (r, col) in enumerate(zip((0.22, 0.32, 0.43, 0.55, 0.7, 0.85), cols)):
        a = i * 1.1 + 0.3; y = 1.32 + i * 0.03; x, z = r * math.cos(a), r * math.sin(a)
        seg_cyl(p, 'brass', (0, y, 0), (x, y, z), 0.006, 6); seg_cyl(p, 'brass', (x, y, z), (x, 1.6, z), 0.005, 6)
        rr = (0.025, 0.035, 0.04, 0.03, 0.07, 0.06)[i]; p.sphere(col, rr, x, 1.6, z, 2)
        if i == 4:
            c = trimesh.creation.annulus(r_min=0.09, r_max=0.12, height=0.006, sections=24); c.apply_transform(trimesh.transformations.rotation_matrix(math.radians(70), [1, 0, 0])); c.apply_translation([x, 1.6, z]); p.add('brass', c)
        if i == 2: p.sphere('chalk', 0.015, x + 0.08, 1.62, z, 1); seg_cyl(p, 'brass', (x, 1.6, z), (x + 0.08, 1.62, z), 0.003, 4)
    return p
def display_case(L1=1.6, d=0.7, seed=1):
    """Vitrine (pivo: centro, piso; ao longo de X): movel de madeira com almofadas, caixa de vidro com cantoneiras de latao e pecas
    expostas (sextante, lunetas pequenas, rochas)."""
    p = Piece(); x, z = L1 / 2, d / 2; rng = np.random.default_rng(seed)
    p.box('dkwood', -x, x, 0.0, 0.08, -z + 0.03, z - 0.03); p.cham('dkwood', -x, x, 0.08, 0.85, -z, z, 0.01)
    for s in (-1, 1):
        for i in range(2): xa = -x + 0.08 + i * (L1 - 0.16) / 2; p.cham('oak', xa + 0.03, xa + (L1 - 0.16) / 2 - 0.03, 0.18, 0.75, *sorted((s * z, s * (z + 0.012))), 0.004)
    p.cham('dkwood', -x - 0.02, x + 0.02, 0.85, 0.89, -z - 0.02, z + 0.02, 0.006); p.box('velvet_g', -x + 0.04, x - 0.04, 0.89, 0.9, -z + 0.04, z - 0.04)
    yt = 1.3
    for (a, b, c_, e) in ((-x, x, -z, -z + 0.006), (-x, x, z - 0.006, z), (-x, -x + 0.006, -z, z), (x - 0.006, x, -z, z)): p.box('glass', a, b, 0.89, yt, c_, e)
    p.box('glass', -x, x, yt - 0.006, yt, -z, z)
    for (xx, zz) in ((-x, -z), (x, -z), (-x, z), (x, z)): p.box('brass', xx - 0.012, xx + 0.012, 0.89, yt + 0.006, zz - 0.012, zz + 0.012)
    for zz in (-z, z): p.box('brass', -x, x, yt - 0.006, yt + 0.006, zz - 0.012, zz + 0.012)
    for xx in (-x, x): p.box('brass', xx - 0.012, xx + 0.012, yt - 0.006, yt + 0.006, -z, z)
    c = trimesh.creation.annulus(r_min=0.12, r_max=0.15, height=0.01, sections=24); c = slice_keep(c, [0, 0, 0], [0, 1, 0]); c.apply_translation([-x * 0.5, 0.92, 0]); p.add('brass', c)
    seg_cyl(p, 'brass', (-x * 0.5, 0.92, 0), (-x * 0.5 + 0.1, 1.05, 0), 0.006, 4)
    seg_cyl(p, 'brass', (0.05, 0.94, -0.1), (0.45, 0.98, 0.08), 0.03, 12); seg_cyl(p, 'dark', (0.45, 0.98, 0.08), (0.5, 0.985, 0.1), 0.035, 12)
    for i in range(3):
        rx = x * 0.7 + rng.uniform(-0.05, 0.05); m = trimesh.creation.icosphere(subdivisions=1, radius=0.06); m.vertices *= rng.uniform(0.7, 1.3, 3); m.apply_translation([rx - i * 0.12, 0.95, rng.uniform(-0.2, 0.2)]); p.add('rock', m)
    return p
def celestial_globe():
    """Globo celeste (pivo: centro, piso): trepe de madeira, anel do horizonte, meridiano de latao, esfera azul com estrelas douradas."""
    p = Piece()
    for k in range(3): a = k * 2 * math.pi / 3; seg_cyl(p, 'dkwood', (0.42 * math.cos(a), 0.0, 0.42 * math.sin(a)), (0.3 * math.cos(a), 0.75, 0.3 * math.sin(a)), 0.03, 8)
    ext_y(p, 'dkwood', Point(0, 0).buffer(0.5, 48).difference(Point(0, 0).buffer(0.44, 48)), 0.75, 0.8)
    yc = 0.98; p.sphere('chart', 0.4, 0, yc, 0, 3)
    rng = np.random.default_rng(5)
    for _ in range(60):
        v = unit(rng.normal(size=3)); p.sphere('gold', 0.008, *(np.array([0, yc, 0]) + 0.402 * v), 0)
    c = trimesh.creation.annulus(r_min=0.42, r_max=0.45, height=0.02, sections=48); c.apply_transform(rot_y(30) @ trimesh.transformations.rotation_matrix(math.radians(23), [1, 0, 0]) @ np.diag([1, 1, 1, 1.0])); c.apply_translation([0, yc, 0]); p.add('brass', c)
    seg_cyl(p, 'brass', (0, yc - 0.5, 0), (0, 0.75, 0), 0.02, 8)
    return p
def bookcase(L1=2.0, h=2.4, seed=0):
    """Estante de livros com cornija (pivo: centro de tras, piso; frente +Z)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(int(L1 * 10) + seed)
    p.box('dkwood', -x, x, 0.0, h, 0.0, 0.03); p.box('dkwood', -x, x, 0.0, 0.1, 0.03, 0.36)
    for s in (-1, 1): p.box('dkwood', *sorted((s * x, s * (x - 0.04))), 0.0, h, 0.03, 0.38)
    nb = max(1, int(round(L1 / 1.0)))
    for i in range(1, nb): xx = -x + i * L1 / nb; p.box('dkwood', xx - 0.02, xx + 0.02, 0.1, h, 0.03, 0.36)
    p.cham('dkwood', -x - 0.04, x + 0.04, h, h + 0.08, 0.0, 0.42, 0.01)
    ns = max(2, int(round((h - 0.15) / 0.38))); ys = np.linspace(0.1, h - 0.03, ns + 1)
    for y in ys[1:-1]: p.box('dkwood', -x + 0.04, x - 0.04, y - 0.025, y, 0.03, 0.36)
    for (ya, yb) in zip(ys[:-1], ys[1:]):
        xx = -x + 0.05
        while xx < x - 0.1:
            w = rng.uniform(0.025, 0.05); hh = rng.uniform(0.6, 0.92) * (yb - ya - 0.04)
            if any(abs(xx - (-x + i * L1 / nb)) < 0.05 for i in range(1, nb)): xx += 0.06; continue
            p.box(['book_r', 'book_g', 'book_b', 'leather'][rng.integers(4)], xx, xx + w - 0.003, ya, ya + hh, 0.05, rng.uniform(0.24, 0.3)); xx += w
            if rng.random() < 0.04: xx += 0.12
    return p
def reading_table(L1=3.0):
    """Mesa de leitura longa (pivo: centro, piso; ao longo de X): pes torneados, tampo com feltro verde, 2 abajures de banqueiro,
    livros abertos."""
    p = Piece(); x = L1 / 2; z = 0.45
    for xx in (-x + 0.1, 0.0, x - 0.1):
        for zz in (-z + 0.08, z - 0.08): lathe(p, 'dkwood', [(0.045, 0.0), (0.06, 0.05), (0.035, 0.12), (0.045, 0.45), (0.035, 0.6), (0.045, 0.68)], xx, zz, 0.0, 10)
    p.box('dkwood', -x + 0.06, x - 0.06, 0.6, 0.72, -z + 0.06, z - 0.06); p.cham('dkwood', -x, x, 0.72, 0.77, -z, z, 0.01)
    p.box('felt', -x + 0.06, x - 0.06, 0.77, 0.773, -z + 0.06, z - 0.06)
    for xx in (-x * 0.5, x * 0.5):
        lathe(p, 'brass', [(0.07, 0.773), (0.06, 0.79), (0.012, 0.8), (0.012, 1.08)], xx, 0.0, 0.0, 10)
        q = Piece(); q.hull('felt', [(a, y, zz) for a in (-0.17, 0.17) for (y, zz) in ((1.05, -0.07), (1.05, 0.07), (1.14, -0.02), (1.14, 0.02))]); p.merge(q, tr(xx, 0, 0))
        p.box('lamp_glass', xx - 0.15, xx + 0.15, 1.048, 1.052, -0.06, 0.06)
    for (xx, zz) in ((-x * 0.75, 0.2), (x * 0.2, -0.2), (x * 0.75, 0.22)):
        p.box('linen', xx - 0.2, xx + 0.2, 0.773, 0.79, zz - 0.13, zz + 0.13); p.box('leather', xx - 0.21, xx + 0.21, 0.773, 0.78, zz - 0.14, zz + 0.14)
    return p
def hall_bench(L1=2.0):
    """Banco de saguao de carvalho com assento de couro e pes torneados (pivo: centro, piso; ao longo de X)."""
    p = Piece(); x = L1 / 2
    for xx in (-x + 0.08, x - 0.08):
        for zz in (-0.18, 0.18): lathe(p, 'dkwood', [(0.035, 0.0), (0.045, 0.06), (0.03, 0.2), (0.04, 0.38)], xx, zz, 0.0, 10)
    p.cham('dkwood', -x, x, 0.38, 0.43, -0.24, 0.24, 0.01); p.cham('leather', -x + 0.04, x - 0.04, 0.43, 0.48, -0.21, 0.21, 0.02)
    for k in range(int(L1 / 0.25)): xx = -x + 0.12 + k * 0.25; p.sphere('brass', 0.008, xx, 0.48, 0.21, 0)
    return p
def reception():
    """Balcao de recepcao de carvalho com almofadas e tampo de marmore, livro de visitas e campainha (pivo: centro de tras, piso)."""
    p = Piece(); x = 1.0
    p.box('dkwood', -x, x, 0.0, 1.0, 0.0, 0.55); p.cham('marble_w', -x - 0.04, x + 0.04, 1.0, 1.05, -0.02, 0.6, 0.008)
    for i in range(4): xa = -x + 0.06 + i * (2 * x - 0.12) / 4; p.cham('oak', xa + 0.03, xa + (2 * x - 0.12) / 4 - 0.03, 0.12, 0.88, 0.55, 0.565, 0.005)
    p.box('dkwood', -x, x, 0.0, 0.1, 0.5, 0.58)
    p.box('leather', -0.3, 0.1, 1.05, 1.08, 0.15, 0.45); p.box('linen', -0.28, 0.08, 1.08, 1.085, 0.17, 0.43)
    lathe(p, 'brass', [(0.04, 1.05), (0.04, 1.06), (0.03, 1.08), (0.0, 1.1)], 0.6, 0.3, 0.0, 12)
    return p
def meteorite():
    """Meteorito sobre pedestal de marmore com placa de latao lisa (pivo: centro, piso)."""
    p = Piece(); p.cham('marble_k', -0.35, 0.35, 0.0, 0.9, -0.35, 0.35, 0.012); p.cham('marble_w', -0.4, 0.4, 0.9, 0.95, -0.4, 0.4, 0.008)
    p.box('brass', -0.12, 0.12, 0.6, 0.7, 0.35, 0.355)
    m = trimesh.creation.icosphere(subdivisions=2, radius=0.3); rng = np.random.default_rng(11); m.vertices *= (1 + rng.uniform(-0.18, 0.12, (len(m.vertices), 1))) * np.array([1.1, 0.8, 0.95]); m.apply_translation([0, 1.18, 0]); p.add('rock', m)
    return p
def armillary(stand='stone'):
    """Esfera armilar (pivo: centro, piso): pedestal, aneis de latao (meridiano, equador, ecliptica, tropicos), eixo inclinado e esfera."""
    p = Piece()
    if stand == 'stone':
        p.cham('trim', -0.4, 0.4, 0.0, 0.12, -0.4, 0.4, 0.01); lathe(p, 'stone', [(0.3, 0.12), (0.24, 0.2), (0.18, 0.3), (0.16, 0.95), (0.22, 1.0), (0.28, 1.05), (0.28, 1.1)], sec=20)
        y0 = 1.1
    else:
        for k in range(3): a = k * 2 * math.pi / 3; seg_cyl(p, 'dkwood', (0.3 * math.cos(a), 0.0, 0.3 * math.sin(a)), (0.05 * math.cos(a), 0.8, 0.05 * math.sin(a)), 0.025, 8)
        y0 = 0.8
    yc = y0 + 0.55; R = 0.45
    seg_cyl(p, 'brass', (0, y0, 0), (0, yc - R, 0), 0.025, 10)
    tilt = trimesh.transformations.rotation_matrix(math.radians(40), [1, 0, 0])
    def ring_(r, w, M):
        c = trimesh.creation.annulus(r_min=r - w, r_max=r, height=0.012, sections=48); c.apply_transform(M); c.apply_translation([0, yc, 0]); p.add('brass', c)
    ring_(R, 0.03, trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    ring_(R - 0.04, 0.025, tilt @ trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    ring_(R - 0.04, 0.025, tilt @ trimesh.transformations.rotation_matrix(math.radians(90 + 23.4), [1, 0, 0]))
    ax = tilt @ np.array([0, 0, 1.0, 0]); ax = unit(ax[:3]); ax = np.array([0, ax[1], ax[2]])
    seg_cyl(p, 'iron', np.array([0, yc, 0]) - 0.52 * unit(ax), np.array([0, yc, 0]) + 0.52 * unit(ax), 0.01, 6)
    p.sphere('gold', 0.06, 0, yc, 0, 2)
    return p
def easel_chart():
    """Cavalete com quadro-negro de orbitas desenhadas a giz, sem texto (pivo: centro, piso; frente +Z)."""
    p = Piece()
    for x in (-0.45, 0.45): seg_cyl(p, 'oak', (x, 0.0, 0.25), (x * 0.8, 2.0, 0.0), 0.025, 8)
    seg_cyl(p, 'oak', (0, 0.0, -0.45), (0, 1.9, -0.02), 0.025, 8)
    p.cham('oak', -0.55, 0.55, 0.72, 0.76, 0.06, 0.2, 0.006)
    q = Piece(); q.cham('dkwood', -0.55, 0.55, 0.0, 1.0, -0.02, 0.02, 0.006); q.box('board', -0.5, 0.5, 0.05, 0.95, 0.02, 0.024)
    for (r, ry) in ((0.12, 0.08), (0.22, 0.14), (0.34, 0.2), (0.44, 0.27)):
        c = trimesh.creation.annulus(r_min=r - 0.006, r_max=r, height=0.002, sections=48); c.apply_scale([1.0, ry / r, 1.0]); c.apply_translation([0, 0.5, 0.025]); q.add('chalk', c)
    q.box('gold', -0.04, 0.04, 0.46, 0.54, 0.024, 0.028)
    for (ang, r, ry) in ((0.6, 0.22, 0.14), (2.4, 0.34, 0.2), (4.0, 0.44, 0.27)): q.box('chalk', r * math.cos(ang) - 0.02, r * math.cos(ang) + 0.02, 0.5 + ry * math.sin(ang) - 0.02, 0.5 + ry * math.sin(ang) + 0.02, 0.024, 0.028)
    p.merge(q, rot_y(0) @ trimesh.transformations.rotation_matrix(math.radians(-10), [1, 0, 0]) @ tr(0, 0, 0) if False else tr(0, 0.78, 0.13))
    return p
def chandelier(r=0.5, arms=8):
    """Lustre de latao (pivo: ponto no forro): canopla, haste, aro de bracos com velas acesas, pingentes e globo de vidro."""
    p = Piece(); p.cyl('brass', 0.07, -0.03, 0.0, 0, 0, 12)
    seg_cyl(p, 'brass', (0, -0.03, 0), (0, -0.6, 0), 0.012, 6)
    lathe(p, 'brass', [(0.02, -0.6), (0.09, -0.68), (0.11, -0.8), (0.06, -0.9), (0.02, -1.0)], sec=14)
    for k in range(arms):
        a = 2 * math.pi * k / arms; x, z = r * math.cos(a), r * math.sin(a)
        seg_cyl(p, 'brass', (0, -0.82, 0), (x, -0.82, z), 0.012, 6); seg_cyl(p, 'brass', (x, -0.82, z), (x, -0.72, z), 0.012, 6)
        p.cyl('brass', 0.045, -0.73, -0.71, x, z, 10); p.cyl('linen', 0.013, -0.71, -0.6, x, z, 6); p.sphere('lamp_glass', 0.028, x, -0.57, z, 1)
        p.sphere('lamp_glass', 0.015, x * 0.6, -0.9, z * 0.6, 0) if k % 2 == 0 else None
    p.sphere('lamp_glass', 0.08, 0, -1.04, 0, 2)
    return p

# ============================================================================ terreno (pivo: origem)
SX0, SX1, SZ0, SZ1 = -22.0, 22.0, -17.0, 26.0
GY = -0.2
TERR = sbox(-15.0, -10.0, 15.0, 11.0)
FST = (2.5, 11.0, 12, 0.32); BST = (1.2, -10.0, 12, 0.32)               # escadarias: meia largura, borda, degraus, piso
PLAZA_C = (0.0, 20.0); PLAZA_R = 2.8
BEDS = [sbox(sx * 3.6, z0, sx * 8.6, z1) if sx > 0 else sbox(sx * 8.6, z0, sx * 3.6, z1) for sx in (-1, 1) for (z0, z1) in ((15.8, 18.6), (21.4, 24.2))]
def steps(p, x0, x1, z0, n, rise, run, dirz=1, y_top=TY):
    for i in range(1, n + 1):
        y = y_top - i * rise
        if y <= 0.001: break
        za, zb = sorted((z0 + dirz * (i - 1) * run, z0 + dirz * i * run))
        p.box('stone', x0, x1, 0.0, y - 0.03, za, zb); p.cham('trim', x0, x1, y - 0.03, y, za - (0.03 if dirz > 0 else 0.0), zb + (0.03 if dirz < 0 else 0.0), 0.006)
def urn():
    """Urna de pedra com folhas (pivo: centro, base)."""
    p = Piece(); lathe(p, 'trim', [(0.14, 0.0), (0.14, 0.05), (0.07, 0.1), (0.06, 0.2), (0.16, 0.28), (0.22, 0.42), (0.22, 0.5), (0.25, 0.54), (0.25, 0.57), (0.18, 0.57)], sec=18)
    p.sphere('hedge', 0.2, 0, 0.66, 0, 2)
    for k in range(5): a = k * 2 * math.pi / 5; p.sphere('flower', 0.05, 0.16 * math.cos(a), 0.72, 0.16 * math.sin(a), 1)
    return p
def site():
    """Terreno: gramado, terraco de 1,8 m com muro de arrimo de pedra rusticada, capa, lajotas e balaustrada; escadarias da frente e
    dos fundos com muretas em rampa e pedestais; caminho de cascalho com meio-fio, praca redonda do relogio de sol, canteiros de flores
    com bordas de buxo."""
    p = Piece(); rng = np.random.default_rng(21)
    fw, fz, fn, fr = FST; bw, bz, bn, br = BST
    flen, blen = (fn - 1) * fr, (bn - 1) * fr
    fst = sbox(-fw - 0.4, fz, fw + 0.4, fz + flen); bst = sbox(-bw - 0.4, bz - blen, bw + 0.4, bz)
    plaza = Point(*PLAZA_C).buffer(PLAZA_R, 48)
    path = sbox(-1.5, fz + flen, 1.5, SZ1)
    bpath = sbox(-1.0, SZ0, 1.0, bz - blen)
    beds = unary_union(BEDS)
    ground = sbox(SX0, SZ0, SX1, SZ1).difference(unary_union([TERR, fst, bst, plaza, path, bpath, beds]))
    ext_y(p, 'grass', ground, GY, 0.0)
    ext_y(p, 'gravel', unary_union([sbox(-1.4, fz + flen, 1.4, SZ1), bpath]).difference(plaza).difference(fst).difference(bst), GY, 0.02)
    for xs in (-1.5, 1.4):
        for (a, b) in ((fz + flen, PLAZA_C[1] - math.sqrt(PLAZA_R ** 2 - 1.5 ** 2)), (PLAZA_C[1] + math.sqrt(PLAZA_R ** 2 - 1.5 ** 2), SZ1)):
            p.box('trim', xs, xs + 0.1, GY, 0.06, a, b)
    ext_y(p, 'paver', plaza.difference(Point(*PLAZA_C).buffer(0.9, 32)).difference(plaza.difference(plaza.buffer(-0.15))), GY, 0.03)
    ext_y(p, 'trim', plaza.difference(plaza.buffer(-0.15)), GY, 0.07); ext_y(p, 'trim', Point(*PLAZA_C).buffer(0.9, 32), GY, 0.06)
    for k in range(8):
        a = k * math.pi / 4; r0, r1 = 0.95, PLAZA_R - 0.2
        p.seg('trim', (PLAZA_C[0] + r0 * math.cos(a), 0.035, PLAZA_C[1] + r0 * math.sin(a)), (PLAZA_C[0] + r1 * math.cos(a), 0.035, PLAZA_C[1] + r1 * math.sin(a)), 0.06, 0.012)
    for b in BEDS:
        ext_y(p, 'soil', b.buffer(-0.2, join_style=2), GY, 0.08); ext_y(p, 'hedge', b.difference(b.buffer(-0.2, join_style=2)), GY, 0.32)
        x0, z0, x1, z1 = b.buffer(-0.3, join_style=2).bounds
        for x in np.arange(x0, x1, 0.32):
            for z in np.arange(z0, z1, 0.32):
                col = ['flower', 'flower_y', 'flower_b'][int((x - x0) / 1.2) % 3]
                p.sphere('leaf2', 0.13, x + rng.uniform(-0.04, 0.04), 0.14, z + rng.uniform(-0.04, 0.04), 1); p.sphere(col, 0.06, x, 0.27, z, 0)
    # terraco
    gaps = unary_union([sbox(-fw - 0.01, fz - 1, fw + 0.01, fz + 1), sbox(-bw - 0.01, bz - 1, bw + 0.01, bz + 1)])
    ext_y(p, 'stone_r', TERR, GY, TY - 0.03)
    ring(p, 'stone_r', TERR, 0.08, -0.02, GY, 0.32); ring(p, 'trim', TERR, 0.1, 0.06, 0.32, 0.4)
    cop = off(TERR, 0.06).difference(off(TERR, -0.34)).difference(gaps)
    ext_y(p, 'trim', cop, TY - 0.12, TY + 0.1)
    tiles(p, off(TERR, -0.34).difference(WALL_OUT).difference(PORT), TY - 0.03, TY, 1.0, 'paver', 0.006, 'concrete', 0.25, 0.25)
    ext_y(p, 'concrete', WALL_OUT.difference(INNER), TY - 0.03, TY)
    ext_y(p, 'paver', off(TERR, -0.34).difference(off(TERR, -0.36)).difference(INNER), TY - 0.03, TY) if False else None
    for (y0, y1, a, b) in ((TY + 0.9, TY + 1.02, -0.02, -0.3), (TY + 0.86, TY + 0.9, -0.05, -0.27)):
        ext_y(p, 'trim', off(TERR, a).difference(off(TERR, b)).difference(unary_union([sbox(-fw - 0.03, fz - 1, fw + 0.03, fz + 1), sbox(-bw - 0.03, bz - 1, bw + 0.03, bz + 1)])), y0, y1)
    c = 0.14; X, Zf, Zb = 15.0 - c, 11.0 - c, -10.0 + c; dz = fw + 0.2; db = bw + 0.2
    lines = [(-X, Zb, -X, Zf), (-X, Zf, -dz, Zf), (dz, Zf, X, Zf), (X, Zf, X, Zb), (X, Zb, db, Zb), (-db, Zb, -X, Zb)]
    for (x0, z0, x1, z1) in lines: balustrade_line(p, x0, z0, x1, z1, TY + 0.1, 0.76, die_h=1.0)
    # escadarias com muretas
    steps(p, -fw, fw, fz, fn, 0.15, fr, 1); steps(p, -bw, bw, bz, bn, 0.15, br, -1)
    for (w, z0, ln, s) in ((fw, fz, flen, 1), (bw, bz, blen, -1)):
        z1 = z0 + s * ln
        for sx in (-1, 1):
            xa, xb = sorted((sx * w, sx * (w + 0.4)))
            p.hull('stone_r', [(x, y, z) for x in (xa, xb) for (z, y) in ((z0, GY), (z0, TY + 0.9), (z1, 0.9), (z1, GY))])
            p.hull('trim', [(x, y, z) for x in (xa - 0.03, xb + 0.03) for (z, y) in ((z0, TY + 0.9), (z0, TY + 1.02), (z1, 1.02), (z1, 0.9))])
            xc = (xa + xb) / 2; za, zb = sorted((z1 - s * 0.02, z1 + s * 0.5))
            p.cham('stone_r', xc - 0.25, xc + 0.25, GY, 1.1, za, zb, 0.01); p.cham('trim', xc - 0.29, xc + 0.29, 1.1, 1.18, za - 0.04, zb + 0.04, 0.01)
            p.cham('trim', xc - 0.27, xc + 0.27, 0.0, 0.14, za - 0.02, zb + 0.02, 0.01)
    return p
def lamp_post(h=3.4):
    """Poste de ferro fundido com globo (pivo: centro, base): base canelada, fuste com aneis, capitel, braco de escada e globo leitoso."""
    p = Piece()
    lathe(p, 'iron', [(0.2, 0.0), (0.2, 0.1), (0.16, 0.2), (0.11, 0.35), (0.12, 0.8), (0.08, 0.9), (0.06, h - 0.3), (0.09, h - 0.22), (0.07, h - 0.12), (0.05, h - 0.05)], sec=16)
    for k in range(8): a = k * math.pi / 4; p.box('iron', 0.11 * math.cos(a) - 0.015, 0.11 * math.cos(a) + 0.015, 0.36, 0.8, 0.11 * math.sin(a) - 0.015, 0.11 * math.sin(a) + 0.015)
    seg_cyl(p, 'iron', (-0.3, h - 0.55, 0), (0.3, h - 0.55, 0), 0.015, 6)
    lathe(p, 'iron', [(0.08, h - 0.05), (0.1, h)], sec=16); p.sphere('lamp_glass', 0.22, 0, h + 0.2, 0, 2); lathe(p, 'iron', [(0.06, h + 0.4), (0.02, h + 0.5)], sec=12)
    return p
def coin_telescope():
    """Luneta publica do terraco (pivo: centro, piso): coluna, forquilha e tubo de latao voltado para fora (+Z)."""
    p = Piece(); lathe(p, 'iron', [(0.22, 0.0), (0.2, 0.06), (0.08, 0.15), (0.06, 1.05), (0.09, 1.1)], sec=14)
    for s in (-1, 1): p.box('iron', s * 0.14 - 0.02, s * 0.14 + 0.02, 1.05, 1.3, -0.04, 0.04)
    seg_cyl(p, 'brass', (0, 1.25, -0.35), (0, 1.38, 0.4), 0.1, 16); seg_cyl(p, 'brass', (0, 1.38, 0.4), (0, 1.4, 0.5), 0.12, 16)
    for z in (-0.35,): seg_cyl(p, 'dark', (0, 1.25, z), (0, 1.24, z - 0.1), 0.05, 10)
    seg_cyl(p, 'iron', (0, 1.32, 0.0), (0.3, 1.32, -0.25), 0.015, 6)
    return p
def tree(h=6.5, r=2.0, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.2, 0.0), (0.14, 0.5), (0.1, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(9):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    ext_y(p, 'soil', Point(0, 0).buffer(0.8, 20), 0.0, 0.02)
    return p
def cypress(h=5.0, seed=2):
    p = Piece(); lathe(p, 'bark', [(0.12, 0.0), (0.08, 0.6)], sec=8)
    lathe(p, 'hedge', [(0.0, 0.4), (0.55, 0.9), (0.7, 1.8), (0.6, 3.0), (0.35, h - 0.6), (0.0, h)], sec=14)
    return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
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

# ============================================================================ portas (pivo: dobradica, embaixo)
def door_panel(w=0.875, h=2.35, t=0.05, glass=False):
    """Porta de madeira escura de almofadas (4 almofadas, ou 2 em cima com vidro), puxador e espelho de latao, dobradicas."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2); cut = []; e = 0.13
    rows = [(0.18, h * 0.42), (h * 0.47, h - 0.15)]
    for (y0, y1) in rows:
        if glass and y0 > 0.5: cut.append(tbox(e, w - e, y0, y1, -t, t)); continue
        for z in (t / 2, -t / 2): cut.append(tbox(e, w - e, y0, y1, z - 0.01, z + 0.01))
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    if glass: p.box('glass', e - 0.004, w - e + 0.004, rows[1][0] - 0.004, rows[1][1] + 0.004, -0.004, 0.004)
    else:
        for (y0, y1) in rows:
            for z in (1, -1): p.cham('door', e + 0.04, w - e - 0.04, y0 + 0.04, y1 - 0.04, *sorted((z * (t / 2 - 0.01), z * (t / 2 + 0.002))), 0.006)
    for z in (1, -1):
        p.cham('brass', w - 0.12, w - 0.06, 0.9, 1.15, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.sphere('brass', 0.03, w - 0.09, 1.04, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.09, 1.04, z * t / 2), (w - 0.09, 1.04, z * (t / 2 + 0.04)), 0.016)
    for yy in (0.25, h / 2, h - 0.35): p.cyl('brass', 0.009, yy, yy + 0.11, 0.0, t / 2 + 0.002, 8)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)

pieces = {f'w_{k}': wall(k) for k in ('win', 'door', 'bdoor', 'plain')}
pieces.update({
    'corner': corner(), 'trims': trims(), 'portico': portico(), 'floor': floor_piece(), 'plan': plan(), 'stair': stair(), 'roof': roof(),
    'drum_main': drum(MAIN), 'drum_wing': drum(WING), 'dome_main': dome(MAIN), 'dome_wing': dome(WING),
    'telescope': telescope_main(), 'telescope_s': telescope_small(), 'hole_rail': hole_rail(),
    'chair': chair(), 'observer_chair': observer_chair(), 'chart_desk': chart_desk(), 'flat_file': flat_file(), 'reg_clock': reg_clock(),
    'star_panel': star_panel(), 'star_panel_s': star_panel(0.8, 1.0, 9),
    'orrery': orrery(), 'display_case': display_case(), 'display_case_l': display_case(2.4, 0.8, 4), 'celestial_globe': celestial_globe(),
    'bookcase': bookcase(1.6, 2.7), 'bookcase_low': bookcase(5.5, 0.85, 2), 'reading_table': reading_table(), 'hall_bench': hall_bench(),
    'reception': reception(), 'meteorite': meteorite(), 'armillary': armillary(), 'armillary_s': armillary('wood'), 'easel_chart': easel_chart(),
    'chandelier': chandelier(), 'porch_lantern': porch_lantern(),
    'site': site(), 'urn': urn(), 'lamp_post': lamp_post(), 'coin_telescope': coin_telescope(), 'garden_bench': garden_bench(),
    'tree': tree(), 'tree_b': tree(5.2, 1.6, 'leaf2', 4), 'cypress': cypress(), 'bush': bush(), 'bush_s': bush(0.35, 7),
    'door_leaf_front': door_panel(0.875, 2.355), 'door_leaf_back': door_back(0.86, 2.225), 'door_leaf_drum': door_panel(0.795, 2.09, 0.045, True),
    'door_leaf_drum_s': door_panel(0.695, 2.02, 0.045, True), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
tg = ['floor0', 'ext']
for x in (-4, -2, 2, 4): put('w_win', x, Y0, CZ, 0, tg + ['front']); put('w_win', x, Y0, -CZ, 180, tg + ['back'])
put('w_door', 0, Y0, CZ, 0, tg + ['front']); put('w_bdoor', 0, Y0, -CZ, 180, tg + ['back'])
for z in (5, -5): put('w_win', -CX, Y0, z, -90, tg + ['left']); put('w_win', CX, Y0, z, 90, tg + ['right'])
for s in (-1, 1):
    for x in (6, 8, 10): put('w_win', s * x, Y0, WZ, 0, tg + ['front']); put('w_win', s * x, Y0, -WZ, 180, tg + ['back'])
for z in (-3, -1, 1, 3): put('w_win', -WX, Y0, z, -90, tg + ['left']); put('w_win', WX, Y0, z, 90, tg + ['right'])
for (x, z, ry) in ((CX, CZ, 0), (-CX, CZ, -90), (-CX, -CZ, 180), (CX, -CZ, 90), (WX, WZ, 0), (-WX, WZ, -90), (-WX, -WZ, 180), (WX, -WZ, 90)):
    put('corner', x, Y0, z, ry, tg)
put('trims', 0, Y0, 0, 0, ['ext', 'roof']); put('portico', 0, Y0, 0, 0, ['ext', 'front'])
put('floor', 0, Y0, 0, 0, ['floor0']); put('plan', 0, Y0, 0, 0, ['floor0']); put('stair', 0, Y0, 0, 0, ['floor0'])
put('roof', 0, Y0, 0, 0, ['roof'])
for (cfg, nm) in ((MAIN, 'main'), (WING, 'wing')):
    for sx in ((1,) if nm == 'main' else (-1, 1)):
        cx, cz = sx * cfg['c'][0], cfg['c'][1]
        put(f'drum_{nm}', cx, UY, cz, 0, ['roof', 'dome']); put(f'dome_{nm}', cx, UY + cfg['dh'] + 0.12, cz, 0, ['roof', 'dome'])
        n = cfg['n']; HA = math.pi / n; AP = cfg['R'] * math.cos(HA); dw = (0.45 if nm == 'main' else 0.4) - 0.05
        put('door_leaf_drum' if nm == 'main' else 'door_leaf_drum_s', cx - dw, UY + 0.032, cz + AP - cfg['td'] / 2, 0, ['roof', 'dome'], door=90)
put('telescope', 0, UY + 0.03, 0, 0, ['roof', 'dome']); put('hole_rail', 0, UY + 0.03, 0, 0, ['roof', 'dome'])
for sx in (-1, 1):
    put('telescope_s', sx * 8.0, UY + 0.03, 0, 0, ['roof', 'dome']); put('chair', sx * 8.0 + 0.8, UY + 0.03, -0.7, 200, ['roof', 'dome'])
def polar(th, r, c=(0, 0)): return c[0] + r * math.cos(math.radians(th)), c[1] + r * math.sin(math.radians(th))
def facing_in(th): return math.degrees(math.atan2(-math.cos(math.radians(th)), -math.sin(math.radians(th))))
yd = UY + 0.03
x, z = polar(202.5, 3.17); put('chart_desk', x, yd, z, facing_in(202.5), ['roof', 'dome'])
x, z = polar(202.5, 2.3); put('chair', x, yd, z, facing_in(202.5) + 180, ['roof', 'dome'])
x, z = polar(247.5, 3.17); put('flat_file', x, yd, z, facing_in(247.5), ['roof', 'dome'])
x, z = polar(157.5, 3.17); put('reg_clock', x, yd + 1.0, z, facing_in(157.5), ['roof', 'dome'])
x, z = polar(112.5, 3.17); put('star_panel_s', x, yd + 1.1, z, facing_in(112.5), ['roof', 'dome'])
put('observer_chair', -0.95, yd, 1.3, 180, ['roof', 'dome'])
# portas
yf = Y0 + 0.008
put('door_leaf_front', -0.88, yf, CZ - 0.2, 0, ['floor0', 'front', 'ext'], door=90); put('door_leaf_front', 0.88, yf, CZ - 0.2, 180, ['floor0', 'front', 'ext'], door=-90)
hx, hz = hinge(0.0, -CZ, 180, -0.43, -0.2); put('door_leaf_back', hx, yf, hz, 180, ['floor0', 'back', 'ext'], door=90)
# saguao
g = ['floor0']; y = Y0
put('orrery', -2.4, y, 3.0, 0, g)
put('display_case', -3.75, y, -3.2, 90, g); put('display_case', 3.75, y, -3.2, 90, g)
put('celestial_globe', 3.5, y, 1.75, 0, g); put('reception', 3.4, y, 4.9, 180, g); put('hall_bench', -2.2, y, -1.35, 0, g)
for z in (3.0, -3.0): put('star_panel', -CX + T, y + 1.5, z, 90, g); put('star_panel', CX - T, y + 1.5, z, -90, g)
put('reg_clock', -3.0, y + 1.2, -CZ + T, 0, g)
for (x, z) in CHANDELIERS: put('chandelier', x, y + CEIL - 0.05, z, 0, g)
# biblioteca (oeste) e sala de instrumentos (leste)
for s in (-1, 1):
    xc = s * 7.8
    put('bookcase_low', xc, y, WZ - T, 180, g); put('bookcase_low', xc, y, -WZ + T, 0, g)
    for z in (2.3, -2.3): put('bookcase', s * CX, y, z, 90 * s, g)
xs_ = [-9.2, -8.0, -6.8]
for zt in (1.8, -1.8):
    put('reading_table', -8.0, y, zt, 0, g)
    for x in xs_:
        put('chair', x, y, zt - math.copysign(0.68, zt), 0 if zt > 0 else 180, g); put('chair', x, y, zt + math.copysign(0.68, zt), 180 if zt > 0 else 0, g)
put('armillary_s', -10.0, y, 0.0, 0, g)
for zt in (1.8, -1.8): put('display_case_l', 8.0, y, zt, 0, g)
put('meteorite', 10.0, y, 0.0, 0, g); put('easel_chart', 6.3, y, 2.9, 200, g); put('armillary_s', 6.3, y, -2.9, 0, g)
# portico
for x in (-2.4, 2.4): put('porch_lantern', x, Y0 + CEIL - 0.14, 6.9, 0, ['ext'])
# terreno
put('site', 0, 0, 0, 0, ['site'])
st = ['site']
for (x, z) in ((-2.7, 10.86), (2.7, 10.86), (-14.86, 10.86), (14.86, 10.86), (-14.86, -9.86), (14.86, -9.86), (-1.4, -9.86), (1.4, -9.86)): put('urn', x, TY + 1.16, z, 0, st)
for sx in (-1, 1):
    put('urn', sx * 2.7, 1.18, 11.0 + 11 * 0.32 + 0.25, 0, st)
    put('lamp_post', sx * 3.4, TY, 10.2, 0, st); put('lamp_post', sx * 14.2, TY, 10.2, 0, st); put('lamp_post', sx * 14.2, TY, -9.2, 0, st)
    put('lamp_post', sx * 2.1, 0.0, 16.0, 0, st); put('lamp_post', sx * 2.1, 0.0, 24.6, 0, st)
    put('garden_bench', sx * 8.0, TY, 9.9, 0, st); put('garden_bench', sx * 3.5, 0.0, 20.0, -90 * sx, st)
    put('coin_telescope', sx * 11.0, TY, 10.0, 0, st)
    put('urn', sx * 4.4, TY, 9.4, 0, st)
    for (x, z) in ((12.0, 17.5), (17.0, 22.0), (12.5, -13.5), (18.5, -2.0), (18.5, 8.0)): put('tree' if (x + z) % 2 < 1 else 'tree_b', sx * x, 0.0, z, 0, st)
    for z in (-6.0, -2.0, 2.0, 6.0): put('cypress', sx * 16.0, 0.0, z, 0, st)
    for x in np.arange(4.2, 14.5, 1.6): put('bush' if int(x) % 2 == 0 else 'bush_s', sx * x, 0.0, 11.75, 0, st)
put('armillary', PLAZA_C[0], 0.06, PLAZA_C[1], 0, st)
put('player_scale_ref', 0.0, 0.0, 15.5); put('player_scale_ref', -1.0, Y0, 2.0, 0, ['floor0'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_level': Y0, 'terrace_level': TY,
                       'building': {'center_pavilion': {'x': [-CX, CX], 'z': [-CZ, CZ]}, 'wings': {'x': [CX, WX], 'z': [-WZ, WZ]},
                                    'portico': {'x': [-PX, PX], 'z': [CZ, PZ]}, 'floors': 1, 'ceiling': CEIL, 'roof_level': UY},
                       'domes': {'main': {'center': list(MAIN['c']), 'radius': MAIN['R'], 'facets': MAIN['n'], 'slit': 'open'},
                                 'wings': {'center': [[-8.0, 0.0], [8.0, 0.0]], 'radius': WING['R'], 'facets': WING['n'], 'slit': 'closed'}},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1], 'terrace': list(TERR.bounds)},
                       'roof': 'flat stone-paved roof terrace with balustrade; stone drums with copper observatory domes',
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
