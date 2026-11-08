"""Kit 39: rodoviaria streamline (anos 40), em ALTO DETALHE (scripts/detalhe/detalhe.py).
Predio terreo de 20 x 12 m e 5 m de pe-direito, reboco creme com rodape de azulejo verde, 3 frisos horizontais ("linhas de
velocidade") no alto, janelas em fita de aluminio, paineis de bloco de vidro, platibanda com rufo. Esquina da frente arredondada
(raio 4 m) com vitrines, portas de vidro e marquise curva com frisos de luz; totem vertical sem texto com disco e pictograma de
onibus. Plataforma coberta no lado oeste, com marquise de concreto, pilares, bancos e postes das baias (discos coloridos).
Dentro: salao com piso de granilite e filetes de latao, bancos, guarda-volumes, banca de jornal, quadro de partidas sem texto,
relogio, bilheteria com 2 guiches gradeados, despacho de bagagem, cafe com balcao e banquetas, banheiros com cabines.
Fora: patio dos onibus com faixas e batentes, calcadas com juntas, ponto de taxi, rua, postes, lixeiras, arvores em canteiros.
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
configurar(cores={'render': (236, 226, 200), 'tile_g': (40, 110, 92), 'trim_g': (34, 96, 80), 'coping': (200, 204, 206), 'metal': (196, 200, 204),
                  'frame': (190, 194, 198), 'gblock': (196, 226, 230), 'mortar': (226, 222, 210), 'plaster': (240, 234, 220), 'ceil': (246, 244, 236),
                  'terrazzo': (214, 206, 190), 'terrazzo_g': (70, 120, 104), 'brass': (200, 164, 84), 'lino': (164, 120, 92), 'tile': (234, 234, 228),
                  'tile_k': (52, 98, 86), 'concrete': (186, 182, 174), 'asphalt': (70, 72, 74), 'paint_w': (236, 236, 230), 'paint_y': (232, 190, 50),
                  'membrane': (118, 118, 116), 'wood': (150, 102, 60), 'dkwood': (92, 58, 40), 'vinyl_r': (170, 50, 46), 'vinyl_g': (46, 104, 84),
                  'steel': (150, 156, 162), 'chrome': (214, 218, 222), 'porcelain': (244, 244, 240), 'dark': (40, 40, 42), 'board': (34, 40, 44),
                  'led_y': (250, 210, 90), 'led_g': (110, 220, 160), 'sign_b': (40, 90, 150), 'sign_r': (196, 60, 50), 'sign_y': (234, 190, 50),
                  'grass': (98, 144, 70), 'leaf': (86, 132, 64), 'leaf2': (112, 148, 72), 'bark': (98, 74, 54), 'mulch': (90, 66, 48), 'curb': (196, 192, 184),
                  'paper': (236, 232, 220), 'news_r': (190, 70, 60), 'news_b': (60, 90, 140), 'cream': (240, 232, 210), 'rubber': (30, 30, 30),
                  'lamp_glass': (255, 238, 196), 'neon': (150, 240, 210), 'stall': (120, 160, 150), 'mirror': (200, 214, 220), 'clay': (170, 96, 66)},
           texturas={'render': 'render', 'plaster': 'plaster', 'concrete': 'render', 'asphalt': 'render', 'terrazzo': 'render', 'wood': 'planks',
                     'dkwood': 'planks', 'grass': 'render', 'membrane': 'render', 'lino': 'render', 'curb': 'render'},
           out=OUT)
D.METAL.update({'metal', 'frame', 'coping', 'brass', 'steel', 'chrome'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.3; t_ = 0.14                               # modulo, parede externa, parede interna
Y0 = 0.15                                                  # piso do salao (nivel das calcadas)
CEIL = 4.5; HW = 5.0; HP = 5.9                             # forro, topo da laje de cobertura, topo da platibanda (sobre o piso)
HX, HZ = 10.0, 6.0; XI, ZI = HX - T, HZ - T                # predio: x de -10 a 10, z de -6 a 6, frente para +Z
AC = (6.0, 2.0); AR = 4.0; NA = 6; AH = math.pi / 4 / NA * 1.0   # esquina redonda: centro, raio externo, 6 faces de 15 graus
AH = math.radians(7.5); AAP = AR * math.cos(AH)
BASE = 0.9                                                 # topo do rodape de azulejo (sobre o piso)
SPEED = (5.08, 5.28, 5.48)                                 # frisos horizontais
ZP = -1.5                                                  # parede da bilheteria / servicos (salao para +Z)
RIB = (1.0, 2.6)                                           # janela em fita: peitoril e verga

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


# ============================================================================ fachadas (pivo: face externa, cota do piso; parede em -Z)
WALL_LAYERS = [-T, -0.18, 0.0]
def wall_core(p, holes, xs0=(-W / 2, W / 2), h=HP):
    xs = sorted(set(list(xs0) + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([-Y0, 0.0, BASE, CEIL, HW, h] + [v for hh in holes for v in hh[2:]]))
    ys = [v for v in ys if -Y0 <= v <= h]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return 'concrete' if cy < 0 else ('plaster' if cy < HW else 'render')
        return 'tile_g' if cy < BASE else 'render'
    for m, mesh in grid_solid(xs, ys, WALL_LAYERS, cell).items(): p.add(m, mesh)
COPING = [(-T - 0.03, HP), (0.05, HP), (0.05, HP + 0.03), (0.035, HP + 0.06), (-T - 0.03, HP + 0.06)]
def band_prof(y):
    return [(0.0, y), (0.045, y), (0.06, y + 0.015), (0.06, y + 0.065), (0.045, y + 0.08), (0.0, y + 0.08)]
TILE_CAP = [(0.0, BASE - 0.02), (0.012, BASE - 0.02), (0.022, BASE - 0.008), (0.022, BASE + 0.02), (0.0, BASE + 0.03)]
PARA_IN = [(-T, HW), (-T - 0.04, HW), (-T - 0.04, HW + 0.12), (-T, HW + 0.12)]     # rodape de manta por dentro da platibanda
BASE_IN = [(-T, 0.001), (-T - 0.016, 0.001), (-T - 0.016, 0.12), (-T, 0.13)]
def trims(p, x0, x1, gaps=(), base_gaps=()):
    """Faixas que correm ao longo do modulo: rufo, 3 frisos verdes, capa do azulejo, rodape de manta e rodape interno."""
    for y in SPEED: prof_x(p, 'trim_g', x0, x1, band_prof(y))
    for (a, b) in segs_excl(list(gaps), x0, x1): prof_x(p, 'tile_g', a, b, TILE_CAP)
    for (a, b) in segs_excl(list(base_gaps), x0 + 0.001, x1 - 0.001, 0.0): prof_x(p, 'dkwood', a, b, BASE_IN)
def alu_frame(p, a, b, y0, y1, f=0.05, z0=-0.2, z1=-0.1, mulls=(), trans=()):
    p.box('frame', a, a + f, y0, y1, z0, z1); p.box('frame', b - f, b, y0, y1, z0, z1)
    p.box('frame', a + f, b - f, y1 - f, y1, z0, z1); p.box('frame', a + f, b - f, y0, y0 + f, z0, z1)
    for x in mulls: p.box('frame', x - f / 2, x + f / 2, y0 + f, y1 - f, z0, z1)
    for y in trans: p.box('frame', a + f, b - f, y - f / 2, y + f / 2, z0, z1)
def glass_block(p, a, b, y0, y1, zc=-0.15, s=0.2):
    """Painel de blocos de vidro (a, b, y0, y1) no plano z = zc: lamina translucida com rejuntes nas 2 faces."""
    p.box('gblock', a, b, y0, y1, zc - 0.04, zc + 0.04)
    nx = max(1, int(round((b - a) / s))); ny = max(1, int(round((y1 - y0) / s)))
    for i in range(1, nx):
        x = a + i * (b - a) / nx
        for z in (zc - 0.045, zc + 0.04): p.box('mortar', x - 0.008, x + 0.008, y0, y1, z, z + 0.005)
    for j in range(1, ny):
        y = y0 + j * (y1 - y0) / ny
        for z in (zc - 0.045, zc + 0.04): p.box('mortar', a, b, y - 0.008, y + 0.008, z, z + 0.005)
def sill_out(p, a, b, y):
    prof_x(p, 'coping', a, b, [(-0.1, y - 0.04), (0.06, y - 0.04), (0.07, y - 0.025), (0.07, y - 0.012), (-0.1, y + 0.005)])
def stool_in(p, a, b, y):
    p.cham('wood', a, b, y - 0.03, y + 0.004, -T - 0.04, -0.18, 0.005)
def wall(kind='plain'):
    """Modulo de 2 m: rib (janela em fita de ponta a ponta), gb (bloco de vidro alto), high (janela alta de bloco de vidro),
    door2 (porta dupla de vidro com bandeira), svc (porta de servico), dock (porta de enrolar aberta), plain."""
    p = Piece(); holes = []; gaps = []
    if kind == 'rib': holes = [(-1.0, 1.0, RIB[0], RIB[1])]
    if kind == 'gb': holes = [(-0.45, 0.45, 0.6, 4.2)]
    if kind == 'high': holes = [(-0.6, 0.6, 2.3, 2.9)]
    if kind == 'door2': holes = [(-0.95, 0.95, 0.0, 2.9)]; gaps = [(-0.95, 0.95)]
    if kind == 'svc': holes = [(-0.5, 0.5, 0.0, 2.2)]; gaps = [(-0.5, 0.5)]
    if kind == 'dock': holes = [(-0.95, 0.95, 0.0, 2.7)]; gaps = [(-0.95, 0.95)]
    wall_core(p, holes)
    if kind == 'rib':
        a, b = -1.0, 1.0; y0, y1 = RIB
        p.box('frame', a + 0.001, a + 0.03, y0, y1, -0.2, -0.1); p.box('frame', b - 0.03, b - 0.001, y0, y1, -0.2, -0.1)
        p.box('frame', a + 0.03, b - 0.03, y1 - 0.05, y1, -0.2, -0.1); p.box('frame', a + 0.03, b - 0.03, y0, y0 + 0.05, -0.2, -0.1)
        p.box('frame', -0.025, 0.025, y0 + 0.05, y1 - 0.05, -0.2, -0.1); p.box('frame', a + 0.03, b - 0.03, 2.0, 2.04, -0.19, -0.11)
        for (c, d) in ((a + 0.03, -0.025), (0.025, b - 0.03)):
            p.box('glass', c, d, y0 + 0.05, 2.0, -0.153, -0.147); p.box('glass', c, d, 2.04, y1 - 0.05, -0.153, -0.147)
        p.box('frame', 0.35, 0.65, 2.04, 2.07, -0.1, -0.09)                       # puxador da basculante
        sill_out(p, a + 0.001, b - 0.001, y0); stool_in(p, a + 0.002, b - 0.002, y0)
    if kind == 'gb':
        glass_block(p, -0.45, 0.45, 0.6, 4.2); sill_out(p, -0.5, 0.5, 0.6)
        prof_y(p, 'render', 0.6, 4.2, [(-0.45, -0.18), (-0.45, -0.001), (-0.46, -0.001), (-0.46, -0.18)]) if False else None
    if kind == 'high':
        glass_block(p, -0.6, 0.6, 2.3, 2.9, s=0.2); sill_out(p, -0.65, 0.65, 2.3)
    if kind == 'door2':
        alu_frame(p, -0.95, 0.95, 0.0, 2.9, mulls=(), trans=(2.42,))
        p.box('frame', -0.025, 0.025, 2.445, 2.85, -0.2, -0.1); p.box('glass', -0.9, -0.025, 2.445, 2.85, -0.153, -0.147); p.box('glass', 0.025, 0.9, 2.445, 2.85, -0.153, -0.147)
        p.cham('concrete', -0.99, 0.99, -0.03, 0.006, -T + 0.004, 0.2, 0.005)
    if kind == 'svc':
        alu_frame(p, -0.5, 0.5, 0.0, 2.2, f=0.05)
        p.cham('concrete', -0.54, 0.54, -0.03, 0.006, -T + 0.004, 0.12, 0.005)
        p.box('metal', -0.7, 0.7, 2.45, 2.5, 0.0, 0.5); p.box('metal', -0.7, 0.7, 2.5, 2.55, 0.0, 0.03) if False else None
        q = wall_lamp(); p.merge(q, tr(0.0, 2.75, 0.0))
    if kind == 'dock':
        for x in (-0.95, 0.95): p.box('steel', x - 0.06 * (x > 0), x + 0.06 * (x < 0), 0.0, 2.7, -0.2, -0.12)
        p.cyl('steel', 0.2, 0, 0, 0, 0) if False else seg_cyl(p, 'steel', (-1.0, 2.95, -T - 0.25), (1.0, 2.95, -T - 0.25), 0.2, 16)
        p.box('steel', -1.0, 1.0, 2.7, 3.2, -T - 0.05, -T); p.box('steel', -0.95, 0.95, 2.62, 2.7, -0.2, -0.12)
        p.cham('concrete', -0.99, 0.99, -0.03, 0.006, -T + 0.004, 0.2, 0.005)
        for x in (-1.1, 1.1): p.cyl('paint_y', 0.1, -Y0, 1.0, x, 0.25, 12)
    trims(p, -W / 2, W / 2, gaps, gaps if kind != 'dock' else gaps)
    return p
def wall_lamp():
    """Arandela redonda de chapa (pivo: face da parede, centro)."""
    p = Piece(); p.cyl('metal', 0.12, -0.12, 0.0, 0, 0, 16) if False else None
    m = trimesh.creation.cylinder(radius=0.13, height=0.05, sections=20); m.apply_translation([0, 0, 0.025]); p.add('metal', m)
    m = trimesh.creation.cylinder(radius=0.1, height=0.05, sections=20); m.apply_translation([0, 0, 0.074]); p.add('lamp_glass', m)
    p.box('metal', -0.14, 0.14, 0.13, 0.15, 0.0, 0.12)
    return p
def corner():
    """Quina (pivo: quina externa, cota do piso; paredes em -X e -Z): nucleo arredondado por fora, rufo, frisos e capa em meia-esquadria."""
    p = Piece(); e = 0.003
    p.box('tile_g', -T + e, e, -Y0, BASE, -T + e, e); p.box('render', -T + e, e, BASE, HP + 0.002, -T + e, e)
    for prof, mat in [(band_prof(y), 'trim_g') for y in SPEED] + [(TILE_CAP, 'tile_g')]:
        mitre_pair(p, mat, [(z, y) for (z, y) in prof if True])
    return p

# ============================================================================ esquina redonda (pivo: centro do arco, cota do piso)
def facet_xf(k, y=0.0):
    th = (k + 0.5) * 2 * AH; return rot_y(90 - math.degrees(th), (AAP * math.cos(th), y, AAP * math.sin(th)))
def facet_clip(q, ap=AAP):
    c, s = math.cos(AH), math.sin(AH); o = (0.0, 0.0, -ap)
    return clipped(q, [(o, (c, 0, s)), (o, (-c, 0, s))])
AFW = 2 * AR * math.sin(AH)
DOOR_FACETS = (2, 3)
def arc_wall():
    """Esquina de 6 faces de 15 graus: vitrines com bloco de vidro em cima e, nas 2 faces do meio, portas de vidro com bandeira;
    rodape de azulejo, 3 frisos e rodape interno cortados em meia-esquadria."""
    p = Piece()
    for k in range(NA):
        q = Piece(); w2 = AFW / 2 + 0.1; door = k in DOOR_FACETS
        holes = [(-0.46, 0.46, 0.0, 2.9)] if door else [(-0.42, 0.42, 0.75, 2.6), (-0.36, 0.36, 3.0, 4.2)]
        wall_core(q, holes, (-w2, w2))
        if door:
            alu_frame(q, -0.46, 0.46, 0.0, 2.9, f=0.04, trans=(2.42,)); q.box('glass', -0.42, 0.42, 2.445, 2.86, -0.153, -0.147)
            q.cham('concrete', -0.5, 0.5, -0.03, 0.006, -T + 0.004, 0.2, 0.005)
        else:
            alu_frame(q, -0.42, 0.42, 0.75, 2.6, f=0.04); q.box('glass', -0.38, 0.38, 0.79, 2.56, -0.153, -0.147)
            sill_out(q, -0.46, 0.46, 0.75); stool_in(q, -0.44, 0.44, 0.75)
            glass_block(q, -0.36, 0.36, 3.0, 4.2)
        for y in SPEED: prof_x(q, 'trim_g', -w2, w2, band_prof(y))
        for (a, b) in segs_excl([(-0.46, 0.46)] if door else [], -w2, w2): prof_x(q, 'tile_g', a, b, TILE_CAP)
        for (a, b) in segs_excl([(-0.46, 0.46)] if door else [], -w2, w2): prof_x(q, 'dkwood', a, b, BASE_IN)
        p.merge(facet_clip(q), facet_xf(k))
    return p
def marquee():
    """Marquise curva sobre as portas da esquina (pivo: centro do arco, cota do piso): laje em leque com bordo arredondado, faixa
    verde com 3 filetes de neon, forro com luzes embutidas, 2 tirantes ate a parede."""
    p = Piece(); r0 = AR - 0.01; r1 = AR + 2.4; y0, y1 = 2.95, 3.35
    a0, a1 = math.radians(14), math.radians(76)
    sector = Polygon([(0, 0)] + [(9 * math.cos(a), 9 * math.sin(a)) for a in np.linspace(a0, a1, 24)])
    slab = Point(0, 0).buffer(r1, 64).intersection(sector).difference(Point(0, 0).buffer(r0, 64)).buffer(0.4, 16).buffer(-0.4, 16).difference(Point(0, 0).buffer(r0, 64))
    ext_y(p, 'ceil', slab, y0, y0 + 0.01); ext_y(p, 'concrete', slab, y0 + 0.01, y1 - 0.02); ext_y(p, 'membrane', slab.buffer(-0.06), y1 - 0.02, y1)
    rim = slab.difference(slab.buffer(-0.08, 16))
    ext_y(p, 'trim_g', rim.difference(Point(0, 0).buffer(r0 + 0.08, 64)), y0 - 0.12, y1 + 0.1)
    out = slab.buffer(0.012, 16).difference(slab.buffer(-0.001, 16)).difference(Point(0, 0).buffer(r0 + 0.08, 64))
    for y in (y0 + 0.02, y0 + 0.18, y0 + 0.34): ext_y(p, 'neon', out, y - 0.015, y + 0.015)
    for a in np.linspace(a0 + 0.12, a1 - 0.12, 6):
        for r in (r0 + 0.9, r0 + 1.8): p.cyl('lamp_glass', 0.09, y0 - 0.004, y0, r * math.cos(a), r * math.sin(a), 12)
    for a in (math.radians(25), math.radians(65)):
        seg_cyl(p, 'steel', ((r1 - 0.3) * math.cos(a), y1 + 0.05, (r1 - 0.3) * math.sin(a)), ((AR - 0.01) * math.cos(a), y1 + 1.7, (AR - 0.01) * math.sin(a)), 0.025, 8)
    return p
def pylon():
    """Totem sem texto (pivo: base no teto, centro; plano da lamina ao longo de X): lamina de reboco com nervuras, bordas
    arredondadas de chapa verde com neon, disco com pictograma de onibus e coroamento com 3 aneis."""
    p = Piece(); w, t, h = 1.5, 0.45, 9.0
    ext_y(p, 'render', sbox(-w / 2 + 0.2, -t / 2, w / 2 - 0.2, t / 2), 0.0, h)
    for s in (-1, 1):
        ext_y(p, 'trim_g', Point(s * (w / 2 - 0.2), 0).buffer(t / 2, 16).difference(sbox(-w / 2 + 0.2, -1, w / 2 - 0.2, 1)), 0.0, h)
        p.box('neon', s * (w / 2 + 0.042) - 0.012, s * (w / 2 + 0.042) + 0.012, 0.3, h - 0.3, -0.012, 0.012)
    for y in np.arange(0.6, h - 2.6, 0.5):
        for z in (-1, 1): p.box('trim_g', -w / 2 + 0.25, w / 2 - 0.25, y, y + 0.08, *sorted((z * t / 2, z * (t / 2 + 0.03))))
    yc = h - 1.5
    for z in (-1, 1):
        m = trimesh.creation.cylinder(radius=0.85, height=0.08, sections=40); m.apply_translation([0, yc, z * (t / 2 + 0.04)]); p.add('trim_g', m)
        m = trimesh.creation.cylinder(radius=0.72, height=0.02, sections=40); m.apply_translation([0, yc, z * (t / 2 + 0.09)]); p.add('cream', m)
        zz = z * (t / 2 + 0.1); d = z * 0.012
        p.box('sign_b', -0.42, 0.42, yc - 0.12, yc + 0.22, *sorted((zz, zz + d)))
        for x in np.linspace(-0.32, 0.22, 4): p.box('cream', x, x + 0.1, yc + 0.04, yc + 0.17, *sorted((zz + d, zz + 2 * d)))
        p.box('cream', 0.27, 0.36, yc - 0.06, yc + 0.17, *sorted((zz + d, zz + 2 * d)))
        for x in (-0.25, 0.25):
            m = trimesh.creation.cylinder(radius=0.09, height=abs(d) * 1.8, sections=16); m.apply_translation([x, yc - 0.13, zz + d]); p.add('dark', m)
        for (yy, w2) in ((yc - 0.32, 0.5), (yc - 0.4, 0.36)): p.box('sign_y', -w2, w2, yy - 0.025, yy + 0.025, *sorted((zz, zz + d)))
    for i, r in enumerate((0.55, 0.42, 0.3)):
        y = h + i * 0.22; Rx = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]); m = trimesh.creation.annulus(r_min=r - 0.04, r_max=r, height=0.06, sections=32); m.apply_transform(Rx); m.apply_translation([0, y + 0.1, 0]); p.add('trim_g', m)
        m2 = trimesh.creation.annulus(r_min=r - 0.06, r_max=r + 0.01, height=0.02, sections=32); m2.apply_transform(Rx); m2.apply_translation([0, y + 0.14, 0]); p.add('neon', m2)
    for a in range(4): seg_cyl(p, 'steel', (0.0, h, 0.0), (0.5 * math.cos(a * math.pi / 2 + 0.785), h + 0.5, 0.5 * math.sin(a * math.pi / 2 + 0.785)), 0.02, 6)
    seg_cyl(p, 'steel', (0, h, 0), (0, h + 1.2, 0), 0.03, 8); p.sphere('sign_r', 0.07, 0, h + 1.25, 0, 1)
    p.cham('render', -w / 2 - 0.1, w / 2 + 0.1, -0.2, 0.25, -t / 2 - 0.1, t / 2 + 0.1, 0.02)
    return p

# ============================================================================ cobertura (pivo: origem, cota do piso)
def outline(off=0.0):
    """Contorno do predio (retangulo com a quina da frente/leste arredondada), afastado 'off' para fora (negativo = para dentro)."""
    rect = sbox(-HX - off, -HZ - off, HX + off, HZ + off).difference(sbox(AC[0], AC[1], 20, 20))
    return rect.union(Point(*AC).buffer(AR + off, 96).intersection(sbox(AC[0], AC[1], 20, 20))).union(sbox(-HX - off, -HZ - off, AC[0] + 0.001, HZ + off)).union(sbox(-HX - off, -HZ - off, HX + off, AC[1] + 0.001)).buffer(0)
def roof():
    """Laje, manta, rufo da platibanda (anel continuo, inclusive no arco), claraboia de lanternim sobre o salao, 2 condensadoras,
    exaustores, alcapao, ralos e passarela."""
    p = Piece(); inner = outline(-T)
    ext_y(p, 'ceil', inner, CEIL - 0.01, CEIL); ext_y(p, 'concrete', inner, CEIL, HW - 0.012)
    sky = sbox(-6.0, 1.0, 2.0, 4.5)
    ext_y(p, 'membrane', inner.difference(sky.buffer(0.3, join_style=2)), HW - 0.012, HW)
    ring = outline(0.05).difference(outline(-T - 0.03))
    ext_y(p, 'coping', ring, HP, HP + 0.06)
    ext_y(p, 'membrane', inner.difference(outline(-T - 0.04)), HW, HW + 0.12)
    # lanternim: muretas de 0,4 m, caixilho de vidro inclinado de 2 aguas
    curb = sky.buffer(0.3, join_style=2).difference(sky)
    ext_y(p, 'render', curb, HW - 0.012, HW + 0.4); ext_y(p, 'coping', curb.buffer(0.03, join_style=2).difference(sky.buffer(-0.01, join_style=2)), HW + 0.4, HW + 0.44)
    x0, z0, x1, z1 = sky.bounds; zm = (z0 + z1) / 2; yr = HW + 1.25; ye = HW + 0.44
    for s in (-1, 1):
        za = z0 if s < 0 else z1
        p.hull('glass', [(x, y, z) for x in (x0, x1) for (z, y) in ((za, ye), (zm, yr))])
        for x in np.linspace(x0, x1, 9): seg_cyl(p, 'frame', (x, ye + 0.01, za), (x, yr + 0.01, zm), 0.025, 4)
    seg_cyl(p, 'frame', (x0, yr + 0.03, zm), (x1, yr + 0.03, zm), 0.04, 6)
    for s in (-1, 1): p.hull('frame', [(x, y, z) for x in ((x0, x0 + 0.05) if s < 0 else (x1 - 0.05, x1)) for (z, y) in ((z0, ye), (z1, ye), (zm, yr + 0.02))])
    ext_y(p, 'glass', sky, CEIL - 0.02, CEIL - 0.01)                             # vidro de forro do lanternim
    for x in np.linspace(x0, x1, 5)[1:-1]: p.box('frame', x - 0.03, x + 0.03, CEIL - 0.03, CEIL - 0.01, z0 + 0.001, z1 - 0.001)
    for (cx, cz) in ((5.0, -3.6), (2.0, -3.6)):
        p.cham('metal', cx - 0.65, cx + 0.65, HW, HW + 0.12, cz - 0.55, cz + 0.55, 0.01); p.cham('cream', cx - 0.6, cx + 0.6, HW + 0.12, HW + 1.0, cz - 0.5, cz + 0.5, 0.02)
        p.cyl('dark', 0.38, HW + 1.0, HW + 1.03, cx, cz, 24); p.cyl('metal', 0.08, HW + 1.03, HW + 1.08, cx, cz, 10)
        for k in range(4):
            a = k * math.pi / 2 + 0.4; p.hull('metal', [(cx + r * math.cos(aa), yy, cz + r * math.sin(aa)) for (r, aa) in ((0.06, a), (0.34, a), (0.34, a + 0.5)) for yy in (HW + 1.0, HW + 1.015)])
        for z in np.arange(cz - 0.42, cz + 0.42, 0.06): p.box('metal', cx - 0.605, cx - 0.6, HW + 0.2, HW + 0.9, z, z + 0.03)
        seg_cyl(p, 'steel', (cx - 0.6, HW + 0.3, cz), (cx - 0.6, HW + 0.3, cz - 1.6), 0.03, 6) if False else None
    for (cx, cz) in ((-8.0, -4.0), (-5.0, -4.2), (-2.0, -3.0)):
        lathe(p, 'metal', [(0.18, HW), (0.18, HW + 0.25), (0.06, HW + 0.3), (0.06, HW + 0.6), (0.24, HW + 0.62), (0.2, HW + 0.78), (0.0, HW + 0.82)], cx, cz, 0.0, 16)
    p.cham('metal', 6.5, 7.5, HW, HW + 0.3, -4.5, -3.5, 0.01); p.box('dark', 6.55, 7.45, HW + 0.3, HW + 0.32, -4.45, -3.55)
    for (cx, cz) in ((-7.5, 2.5), (6.0, 0.5), (-1.0, -4.6)): p.cyl('dark', 0.1, HW, HW + 0.03, cx, cz, 12)
    for i in range(10): p.box('rubber', -8.5 + i * 0.5, -8.05 + i * 0.5, HW, HW + 0.03, -4.2, -3.6) if False else None
    return p

# ============================================================================ pisos e paredes internas
INNER = outline(-T)
HALL_P = INNER.intersection(sbox(-20, ZP + t_ / 2, 20, 20))
ROOMS_X = [-XI, -6.5, -3.2, 1.0, 5.5, XI]                 # banheiro masc., banheiro fem., bagagem, bilheteria, cafe
def tiles(p, poly, y0, y1, step, mat, gap=0.005, fill='brass', ox=0.0, oz=0.0):
    b = poly.bounds
    for i in range(int(math.floor((b[0] - ox) / step)), int(math.ceil((b[2] - ox) / step))):
        for j in range(int(math.floor((b[1] - oz) / step)), int(math.ceil((b[3] - oz) / step))):
            q = sbox(ox + i * step + gap, oz + j * step + gap, ox + (i + 1) * step - gap, oz + (j + 1) * step - gap).intersection(poly)
            if q.area > 1e-6: ext_y(p, mat, q, y0, y1)
    ext_y(p, fill, poly.buffer(-0.001, join_style=2), y0, y1 - 0.003)
def checker(p, poly, y0, y1, step, ma, mb):
    b = poly.bounds
    for i in range(int(math.floor(b[0] / step)), int(math.ceil(b[2] / step))):
        for j in range(int(math.floor(b[1] / step)), int(math.ceil(b[3] / step))):
            q = sbox(i * step, j * step, (i + 1) * step, (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
def floor_piece():
    """Piso (pivo: origem, cota do piso): granilite com faixa verde e filetes de latao no salao, ladrilho nos banheiros e no cafe,
    piso vinilico na bagagem e na bilheteria."""
    p = Piece(); ext_y(p, 'concrete', INNER, -Y0 + 0.02, -0.012)
    border = HALL_P.difference(HALL_P.buffer(-0.45, join_style=2))
    ext_y(p, 'terrazzo_g', border, -0.012, 0.0)
    tiles(p, HALL_P.buffer(-0.45, join_style=2), -0.012, 0.0, 1.5, 'terrazzo', 0.004, 'brass', -0.75, 0.0)
    for i, (x0, x1) in enumerate(zip(ROOMS_X[:-1], ROOMS_X[1:])):
        r = INNER.intersection(sbox(x0, -ZI, x1, ZP - t_ / 2))
        if i < 2: checker(p, r, -0.012, 0.0, 0.3, 'tile', 'tile_k')
        elif i == 4: checker(p, r, -0.012, 0.0, 0.3, 'tile', 'vinyl_r')
        else: ext_y(p, 'lino', r, -0.012, 0.0)
    return p
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
def stalls(x0, x1, n=3):
    """Cabines de divisoria (pivo: origem): paineis com pes cromados, pilastras, portas entreabertas, travessa de cima."""
    p = Piece(); xs = np.linspace(x0, x1, n + 1)
    for x in xs[1:-1]:
        p.box('stall', x - 0.012, x + 0.012, 0.15, 2.0, -ZI, ZST); p.cyl('chrome', 0.02, 0.0, 0.15, x, ZST - 0.08, 8)
    for a, b in zip(xs[:-1], xs[1:]):
        p.box('stall', a + 0.012 * (a > x0), a + 0.11, 0.0, 2.0, ZST - 0.025, ZST); p.box('stall', b - 0.11, b - 0.012 * (b < x1), 0.0, 2.0, ZST - 0.025, ZST)
        q = Piece(); w = b - a - 0.24; q.box('stall', 0.0, w, 0.15, 1.95, -0.012, 0.012); q.box('chrome', w - 0.1, w - 0.04, 1.0, 1.06, 0.012, 0.03)
        p.merge(q, rot_y(25, (a + 0.115, 0, ZST - 0.0125)))
        p.merge(wc(), rot_y(0, ((a + b) / 2, 0, -ZI)))
    p.box('chrome', x0 + 0.002, x1 - 0.002, 2.0, 2.03, ZST - 0.03, ZST + 0.005)
    return p
def plan():
    """Paredes internas (pivo: origem, cota do piso): parede da bilheteria com portas, balcao de bagagem, 2 guiches e o vao do cafe;
    divisorias dos fundos; cabines dos banheiros."""
    p = Piece(); cuts = [(c + XI, w, y0, y1, k) for (c, w, y0, y1, k) in PART]
    p.merge(run_wall(2 * XI, CEIL, cuts), tr(-XI, 0, ZP))
    for x in ROOMS_X[1:-1]: p.merge(run_wall((ZP - t_ / 2) + ZI, CEIL), rot_y(-90, (x, 0, -ZI)))
    p.merge(stalls(-XI, -6.57)); p.merge(stalls(-6.43, -3.27))
    return p

# ============================================================================ moveis (pivo: centro de tras, piso; frente para +Z)
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
def bench_double(L1=3.0):
    """Banco duplo de costas (pivo: centro, piso; ao longo de X): assentos e encostos de ripas, pes e bracos cromados."""
    p = Piece(); x = L1 / 2
    for s in (-1, 1):
        for i in range(4):
            z = s * (0.12 + i * 0.1); p.cham('wood', -x, x, 0.44, 0.47, *sorted((z, z + s * 0.085)), 0.006)
        for i in range(3):
            y = 0.6 + i * 0.13; z = s * (0.07 + (y - 0.5) * 0.12); p.cham('wood', -x, x, y, y + 0.1, *sorted((z, z + s * 0.025)), 0.006)
    for xx in np.linspace(-x + 0.1, x - 0.1, 4):
        for s in (-1, 1): seg_cyl(p, 'chrome', (xx, 0.0, s * 0.42), (xx, 0.44, s * 0.32), 0.02, 8)
        seg_cyl(p, 'chrome', (xx, 0.44, -0.5), (xx, 0.44, 0.5), 0.02, 8); seg_cyl(p, 'chrome', (xx, 0.44, 0.0), (xx, 1.0, 0.0), 0.02, 8)
    for xx in (-x - 0.02, 0.0, x + 0.02):
        for s in (-1, 1): seg_cyl(p, 'chrome', (xx, 0.47, s * 0.08), (xx, 0.68, s * 0.45), 0.018, 8); seg_cyl(p, 'chrome', (xx, 0.68, s * 0.45), (xx, 0.47, s * 0.5), 0.018, 8)
    return p
def bench_wall(L1=1.8):
    """Banco simples com encosto (pivo: centro de tras, piso)."""
    p = Piece(); x = L1 / 2
    for i in range(4): z = 0.12 + i * 0.1; p.cham('wood', -x, x, 0.44, 0.47, z, z + 0.085, 0.006)
    for i in range(3): y = 0.6 + i * 0.13; p.cham('wood', -x, x, y, y + 0.1, 0.04, 0.065, 0.006)
    for xx in (-x + 0.12, x - 0.12):
        seg_cyl(p, 'chrome', (xx, 0.0, 0.5), (xx, 0.44, 0.45), 0.02, 8); seg_cyl(p, 'chrome', (xx, 0.0, 0.05), (xx, 0.95, 0.03), 0.02, 8)
        seg_cyl(p, 'chrome', (xx, 0.44, 0.05), (xx, 0.44, 0.5), 0.02, 8)
    return p
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
def kiosk():
    """Banca de jornais (pivo: centro de tras, piso): balcao com revistas em degraus, prateleiras, toldo listrado e caixa."""
    p = Piece(); x = 0.9; rng = np.random.default_rng(4)
    p.box('dkwood', -x, x, 0.0, 0.95, 0.0, 0.7); p.cham('wood', -x - 0.03, x + 0.03, 0.95, 0.99, 0.0, 0.75, 0.006)
    for s in (-1, 1): p.box('dkwood', *sorted((s * x, s * (x - 0.06))), 0.99, 2.3, 0.0, 0.7)
    p.box('dkwood', -x, x, 0.99, 2.3, 0.0, 0.04)
    for i, y in enumerate((1.15, 1.45, 1.75, 2.05)):
        p.box('wood', -x + 0.06, x - 0.06, y - 0.02, y, 0.04, 0.3)
        for xx in np.arange(-x + 0.1, x - 0.2, 0.22):
            p.hull(['news_r', 'news_b', 'paper', 'sign_y'][rng.integers(4)], [(xx + dx, y + dy, 0.08 + dz) for dx in (0.0, 0.18) for (dy, dz) in ((0.0, 0.1), (0.25, 0.04))] + [(xx + dx, y, 0.12) for dx in (0.0, 0.18)])
    for k in range(3):
        z = 0.15 + k * 0.18
        for xx in np.arange(-x + 0.1, x - 0.6, 0.3): p.box(['paper', 'news_r', 'news_b'][rng.integers(3)], xx, xx + 0.26, 0.99 + k * 0.012, 1.0 + k * 0.012, z, z + 0.16)
    for i in range(8):
        a, b = -x - 0.1 + i * (2 * x + 0.2) / 8, -x - 0.1 + (i + 1) * (2 * x + 0.2) / 8
        p.hull('sign_r' if i % 2 == 0 else 'cream', [(xx, y, z) for xx in (a, b) for (y, z) in ((2.3, 0.0), (2.36, 0.0), (2.05, 1.05), (2.1, 1.05))])
    p.cham('metal', 0.4, 0.75, 0.99, 1.2, 0.45, 0.68, 0.01); p.box('dark', 0.44, 0.71, 1.12, 1.19, 0.68, 0.69)
    return p
def depart_board():
    """Quadro de partidas sem texto (pivo: face da parede, centro embaixo): moldura de aco, fundo escuro, 6 linhas com faixas coloridas
    (destino), pontos (plataforma) e barras de horario."""
    p = Piece(); w, h = 3.0, 1.1
    p.cham('metal', -w / 2 - 0.06, w / 2 + 0.06, -0.06, h + 0.06, 0.0, 0.1, 0.01); p.box('board', -w / 2, w / 2, 0.0, h, 0.1, 0.11)
    cols = ['sign_r', 'sign_b', 'sign_y', 'led_g', 'sign_b', 'sign_r']
    for i in range(6):
        y = h - 0.12 - i * 0.165
        p.box(cols[i], -w / 2 + 0.1, -w / 2 + 0.3, y - 0.05, y + 0.05, 0.11, 0.116)
        for k in range(4): p.box('led_y', -w / 2 + 0.4 + k * 0.17, -w / 2 + 0.55 + k * 0.17, y - 0.03, y + 0.03, 0.11, 0.115)
        for k in range(1 + i % 4): p.sphere('led_g', 0.025, 0.6 + k * 0.08, y, 0.12, 0)
        p.box('led_y', 1.0, 1.35, y - 0.03, y + 0.03, 0.11, 0.115)
    for x in (-1.2, 1.2): seg_cyl(p, 'steel', (x, h + 0.06, 0.05), (x, h + 0.6, 0.05), 0.012, 6)
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
def pendant_globe(drop=1.4):
    """Luminaria pendente de globo leitoso com canopla e haste (pivo: ponto no forro)."""
    p = Piece(); p.cyl('chrome', 0.08, -0.03, 0.0, 0, 0, 14); seg_cyl(p, 'chrome', (0, -0.03, 0), (0, -drop, 0), 0.01, 6)
    lathe(p, 'chrome', [(0.02, -drop), (0.09, -drop - 0.04), (0.1, -drop - 0.06)], sec=14); p.sphere('lamp_glass', 0.24, 0, -drop - 0.26, 0, 2)
    return p
def water_fountain():
    p = Piece(); p.cham('steel', -0.25, 0.25, 0.65, 0.95, 0.0, 0.4, 0.02); p.box('dark', -0.18, 0.18, 0.945, 0.952, 0.08, 0.32)
    p.box('steel', -0.08, 0.08, 0.0, 0.65, 0.0, 0.12); seg_cyl(p, 'chrome', (0.0, 0.95, 0.15), (0.0, 1.02, 0.2), 0.012, 6); p.box('chrome', 0.12, 0.2, 0.9, 0.94, 0.4, 0.42)
    return p
def trash_bin():
    p = Piece(); lathe(p, 'steel', [(0.2, 0.0), (0.2, 0.82), (0.22, 0.84), (0.22, 0.86), (0.08, 0.95), (0.0, 0.98)], sec=16); p.box('dark', -0.08, 0.08, 0.78, 0.86, 0.2, 0.225); return p
def planter(r=0.4):
    p = Piece(); lathe(p, 'terrazzo_g', [(r, 0.0), (r, 0.6), (r + 0.04, 0.62), (r + 0.04, 0.66), (r - 0.04, 0.66)], sec=20); p.cyl('mulch', r - 0.04, 0.6, 0.64, 0, 0, 20)
    rng = np.random.default_rng(int(r * 100))
    for _ in range(9): a = rng.uniform(0, 6.28); d = rng.uniform(0, r * 0.5); p.sphere('leaf', rng.uniform(0.14, 0.22), d * math.cos(a), 0.8 + rng.uniform(0, 0.4), d * math.sin(a), 1)
    return p
def stool():
    p = Piece(); p.cyl('chrome', 0.2, 0.0, 0.02, 0, 0, 16); seg_cyl(p, 'chrome', (0, 0.02, 0), (0, 0.66, 0), 0.03, 8)
    m = trimesh.creation.annulus(r_min=0.15, r_max=0.17, height=0.015, sections=20); m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0.3, 0]); p.add('chrome', m) if False else p.cyl('chrome', 0.17, 0.3, 0.315, 0, 0, 20)
    lathe(p, 'vinyl_r', [(0.18, 0.66), (0.19, 0.7), (0.18, 0.76), (0.0, 0.77)], sec=20); return p
def cafe_counter(L1=2.6):
    """Balcao do cafe (pivo: centro de tras, piso; frente para +Z): frente de chapa com frisos, tampo de granilite, rodape com apoio
    de pes, cuba de bolos com tampa de vidro, caixa registradora, cafeteira de 2 bules, porta-guardanapos."""
    p = Piece(); x = L1 / 2
    p.box('cream', -x, x, 0.1, 1.0, 0.0, 0.62); p.box('dark', -x + 0.03, x - 0.03, 0.0, 0.1, 0.0, 0.56)
    for y in (0.35, 0.55, 0.75): p.box('chrome', -x, x, y, y + 0.025, 0.62, 0.635)
    p.cham('terrazzo', -x - 0.03, x + 0.03, 1.0, 1.05, 0.0, 0.72, 0.008); seg_cyl(p, 'chrome', (-x, 0.2, 0.75), (x, 0.2, 0.75), 0.02, 8)
    for xx in np.linspace(-x + 0.2, x - 0.2, 5): seg_cyl(p, 'chrome', (xx, 0.2, 0.62), (xx, 0.2, 0.75), 0.012, 6)
    p.cyl('chrome', 0.2, 1.05, 1.08, -0.6, 0.35, 20); p.sphere('glass', 0.18, -0.6, 1.08, 0.35, 2); lathe(p, 'cream', [(0.15, 1.08), (0.15, 1.15)], -0.6, 0.35, 0.0, 16)
    p.cham('metal', 0.3, 0.7, 1.05, 1.3, 0.1, 0.45, 0.02); p.box('dark', 0.34, 0.66, 1.22, 1.29, 0.45, 0.46)
    for xx in (0.9, 1.1): lathe(p, 'chrome', [(0.08, 1.05), (0.08, 1.3), (0.05, 1.35)], xx, 0.15, 0.0, 12)
    p.box('chrome', -0.12, 0.0, 1.05, 1.18, 0.3, 0.38)
    return p
def back_kitchen(L1=3.6):
    """Cozinha do cafe (pivo: centro de tras, piso): bancada de inox com chapa, coifa, geladeira e prateleira de louca."""
    p = Piece(); x = L1 / 2
    p.box('steel', -x, x - 0.8, 0.1, 0.9, 0.0, 0.65); p.box('dark', -x + 0.03, x - 0.83, 0.0, 0.1, 0.0, 0.6); p.cham('chrome', -x, x - 0.8, 0.9, 0.94, 0.0, 0.67, 0.006)
    p.box('dark', -x + 0.1, -x + 0.9, 0.94, 0.96, 0.08, 0.6); p.cham('steel', -x, -x + 1.0, 1.9, 2.4, 0.0, 0.7, 0.02)
    p.cham('chrome', x - 0.78, x, 0.0, 1.9, 0.0, 0.68, 0.02); p.box('dark', x - 0.4, x - 0.38, 0.0, 1.9, 0.68, 0.69)
    for y in (0.9, 1.5): p.box('chrome', x - 0.1, x - 0.07, y, y + 0.25, 0.68, 0.72)
    p.box('wood', -x + 1.2, x - 0.9, 1.5, 1.53, 0.0, 0.3)
    for xx in np.arange(-x + 1.3, x - 1.0, 0.18): p.cyl('porcelain', 0.06, 1.53, 1.62, xx, 0.15, 12)
    return p
def bag_shelf(L1=3.0):
    """Estante de aco com malas (pivo: centro de tras, piso)."""
    p = Piece(); x = L1 / 2; rng = np.random.default_rng(9)
    for xx in (-x, 0.0, x):
        for z in (0.03, 0.57): p.box('steel', xx - 0.025, xx + 0.025, 0.0, 2.2, z - 0.025, z + 0.025)
    for y in (0.1, 0.8, 1.5, 2.15):
        p.box('steel', -x, x, y, y + 0.03, 0.0, 0.6)
        xx = -x + 0.05
        while y < 2.0 and xx < x - 0.4:
            w = rng.uniform(0.35, 0.6); h = rng.uniform(0.3, 0.55)
            p.cham(['vinyl_r', 'news_b', 'dkwood', 'vinyl_g', 'lino'][rng.integers(5)], xx, xx + w, y + 0.03, y + 0.03 + h, 0.08, 0.5, 0.02)
            p.box('dark', xx + w / 2 - 0.08, xx + w / 2 + 0.08, y + 0.03 + h, y + 0.06 + h, 0.27, 0.31); xx += w + 0.05
    return p
def bag_cart():
    """Carrinho de bagagem de 4 rodas com 2 malas (pivo: centro, piso; puxador para +Z)."""
    p = Piece(); p.cham('wood', -0.5, 0.5, 0.25, 0.3, -0.8, 0.8, 0.01)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        c = trimesh.creation.cylinder(radius=0.12, height=0.06, sections=16); c.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])); c.apply_translation([sx * 0.45, 0.12, sz * 0.6]); p.add('rubber', c)
        p.box('steel', sx * 0.45 - 0.02, sx * 0.45 + 0.02, 0.12, 0.25, sz * 0.6 - 0.02, sz * 0.6 + 0.02)
    for s in (-1, 1): seg_cyl(p, 'steel', (s * 0.45, 0.3, 0.8), (s * 0.3, 0.9, 1.1), 0.015, 6)
    seg_cyl(p, 'steel', (-0.3, 0.9, 1.1), (0.3, 0.9, 1.1), 0.02, 6)
    p.cham('vinyl_r', -0.4, 0.3, 0.3, 0.75, -0.7, -0.1, 0.03); p.cham('news_b', -0.3, 0.4, 0.3, 0.6, 0.0, 0.6, 0.03)
    return p
def office_desk():
    """Mesa de guiche com tampo de madeira, gaveteiro, banqueta alta e luminaria (pivo: centro de tras, piso)."""
    p = Piece(); p.cham('wood', -0.5, 0.5, 0.95, 1.0, 0.0, 0.6, 0.008); p.box('dkwood', 0.1, 0.5, 0.0, 0.95, 0.02, 0.58)
    for y in (0.3, 0.6): p.box('chrome', 0.25, 0.35, y, y + 0.02, 0.58, 0.6)
    p.box('dkwood', -0.48, -0.44, 0.0, 0.95, 0.02, 0.58)
    p.merge(stool(), tr(-0.1, 0.0, 0.95) @ np.diag([1.0, 1.0, 1.0, 1.0]))
    lathe(p, 'sign_y' if False else 'trim_g', [(0.08, 1.0), (0.015, 1.03), (0.015, 1.3), (0.12, 1.35), (0.05, 1.45)], 0.35, 0.15, 0.0, 12)
    p.box('paper', -0.35, -0.05, 1.0, 1.005, 0.2, 0.42); p.cham('metal', -0.1, 0.15, 1.0, 1.12, 0.1, 0.3, 0.01)
    return p
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
def canopy_poly(off=0.0):
    return sbox(-5.6, -3.0, 5.6, 5.3).buffer(1.2 + off, 24).intersection(sbox(-20, 0.0, 20, 20))
def canopy():
    """Marquise da plataforma: laje de concreto com cantos arredondados, faixa verde com 3 filetes brancos, forro com luminarias,
    4 pilares de aco com base e capitel, condutores, manta e rufo."""
    p = Piece(); slab = canopy_poly()
    ext_y(p, 'ceil', slab, CAN_Y0, CAN_Y0 + 0.01); ext_y(p, 'concrete', slab, CAN_Y0 + 0.01, CAN_Y1 - 0.02); ext_y(p, 'membrane', canopy_poly(-0.15), CAN_Y1 - 0.02, CAN_Y1)
    rim = canopy_poly(0.02).difference(canopy_poly(-0.12)).difference(sbox(-20, -1, 20, 0.12))
    ext_y(p, 'trim_g', rim, CAN_Y0 - 0.2, CAN_Y1 + 0.15)
    lines = canopy_poly(0.032).difference(canopy_poly(0.019)).difference(sbox(-20, -1, 20, 0.12))
    for y in (CAN_Y0 - 0.12, CAN_Y0 + 0.05, CAN_Y0 + 0.22): ext_y(p, 'paint_w', lines, y, y + 0.04)
    for x in np.arange(-5.5, 5.6, 1.1):
        for z in (1.6, 4.0): p.box('lamp_glass', x - 0.35, x + 0.35, CAN_Y0 - 0.004, CAN_Y0, z - 0.06, z + 0.06)
    for x in CAN_COLS:
        lathe(p, 'steel', [(0.28, Y0), (0.28, Y0 + 0.06), (0.2, Y0 + 0.1), (0.14, Y0 + 0.16), (0.14, CAN_Y0 - 0.35), (0.2, CAN_Y0 - 0.2), (0.26, CAN_Y0 - 0.1), (0.26, CAN_Y0)], x, CAN_ZC, 0.0, 20)
        for y in (1.1, 1.18): lathe(p, 'trim_g', [(0.145, Y0 + y), (0.16, Y0 + y + 0.02), (0.16, Y0 + y + 0.05), (0.145, Y0 + y + 0.07)], x, CAN_ZC, 0.0, 20)
    for x in (-5.0, 5.0): seg_cyl(p, 'steel', (x + 0.2, CAN_Y0 - 0.05, CAN_ZC), (x + 0.2, Y0 + 0.2, CAN_ZC), 0.05, 10)
    return p
def bay_pole(mat='sign_r', n=1):
    """Poste de baia (pivo: chao): coluna de aco, disco colorido nas 2 faces com n pontos brancos (sem numeros), luz em cima."""
    p = Piece(); lathe(p, 'steel', [(0.1, 0.0), (0.1, 0.05), (0.04, 0.1), (0.035, 2.95)], sec=12)
    R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    for (r, z0, z1, m) in ((0.32, -0.025, 0.025, 'chrome'), (0.29, -0.03, 0.03, mat)):
        c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=32); c.apply_translation([0, 2.4, 0]); p.add(m, c)
    for z in (-1, 1):
        xs = np.linspace(-0.09 * (n - 1), 0.09 * (n - 1), n)
        for x in xs: p.sphere('paint_w', 0.05, x, 2.4, z * 0.03, 1)
    p.sphere('lamp_glass', 0.08, 0, 3.0, 0, 1)
    return p

# ============================================================================ terreno (pivo: origem)
SX0, SX1, SZ0, SZ1 = -28.0, 14.0, -12.0, 14.0
GY = -0.2
WALK = unary_union([sbox(-16.5, 6.0, 11.6, 9.0), sbox(10.0, -7.4, 11.6, 6.0), sbox(-10.0, -7.4, 10.0, -6.0), sbox(-16.5, -7.4, -10.0, 6.0)]).difference(outline(0.0))
PITS = [sbox(x - 0.6, 7.6, x + 0.6, 8.8) for x in (-13.5, -7.0, -1.0, 4.0)]
LAWN = sbox(11.6, SZ0, SX1, -7.4)
def paving(poly, y1, joints=1.5, mat='concrete', gap=0.006):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + gap, z + gap, x + joints - gap, z + joints - gap).intersection(poly); ext_y(p, mat, q, GY, y1)
    ext_y(p, 'dark', poly.buffer(-0.002, join_style=2), GY, y1 - 0.008)
    return p
def site():
    """Terreno: rua com faixas e travessia, patio dos onibus com baias pintadas e batentes, patio de servico, faixa de taxi,
    calcadas com juntas (plataforma com faixa amarela), covas de arvore com grade, gramado com guia."""
    p = Piece(); box_ = sbox(SX0, SZ0, SX1, SZ1)
    walk = WALK.difference(unary_union(PITS))
    asph = box_.difference(unary_union([WALK, LAWN, outline(0.0)]))
    ext_y(p, 'asphalt', asph, GY, 0.0)
    p.merge(paving(walk, Y0))
    for b in PITS:
        ext_y(p, 'mulch', b.buffer(-0.002, join_style=2), GY, Y0 - 0.06)
        for k in range(9):
            x0 = b.bounds[0] + 0.05 + k * 0.122; p.box('dark', x0, x0 + 0.03, Y0 - 0.04, Y0 - 0.005, b.bounds[1] + 0.02, b.bounds[3] - 0.02)
        p.box('dark', b.bounds[0] + 0.02, b.bounds[2] - 0.02, Y0 - 0.06, Y0 - 0.04, b.bounds[1] + 0.02, b.bounds[1] + 0.06)
        p.box('dark', b.bounds[0] + 0.02, b.bounds[2] - 0.02, Y0 - 0.06, Y0 - 0.04, b.bounds[3] - 0.06, b.bounds[3] - 0.02)
    inner = LAWN.buffer(-0.15, join_style=2); ext_y(p, 'grass', inner, GY, 0.12); ext_y(p, 'curb', LAWN.difference(inner), GY, Y0)
    p.box('paint_y', -16.45, -16.15, Y0, Y0 + 0.004, -7.3, 5.95)
    for z in (-6.0, -3.0, 0.0, 3.0, 6.0): p.box('paint_w', -26.0, -16.5, 0.0, 0.004, z - 0.06, z + 0.06)
    p.box('paint_w', -26.12, -26.0, 0.0, 0.004, -6.06, 6.06)
    for x in np.arange(SX0 + 1.0, SX1 - 1.0, 4.0):
        for (a, b) in segs_excl([(-2.7, 2.7)], x, x + 2.0): p.box('paint_y', a, b, 0.0, 0.004, 11.45, 11.55)
    for x in np.arange(-2.25, 2.3, 0.9): p.box('paint_w', x - 0.25, x + 0.25, 0.0, 0.004, 9.3, 13.7)
    for z in (9.2, 13.8): p.box('paint_w', -2.5, 2.5, 0.0, 0.004, z - 0.05, z + 0.05) if False else None
    for z in np.arange(-6.5, 8.5, 1.2): p.box('paint_y', 12.0, 12.12, 0.0, 0.004, z, z + 0.6)
    for (x0, x1, z) in ((-16.5, -10.0, -10.0),): pass
    return p
def wheel_stop():
    p = Piece(); p.cham('concrete', -0.9, 0.9, 0.0, 0.12, -0.1, 0.1, 0.02)
    for x in (-0.6, 0.6): p.box('paint_y', x - 0.15, x + 0.15, 0.12, 0.123, -0.08, 0.08)
    return p
def lamp_post(h=5.5):
    """Poste streamline (pivo: chao): base conica, fuste com 3 aneis verdes, braco curvo e lanterna cilindrica."""
    p = Piece(); lathe(p, 'steel', [(0.2, GY), (0.2, 0.2), (0.12, 0.45), (0.08, 0.6), (0.06, h)], sec=16)
    for y in (2.0, 2.12, 2.24): lathe(p, 'trim_g', [(0.065, y), (0.085, y + 0.02), (0.085, y + 0.06), (0.065, y + 0.08)], sec=16)
    pts = [(0.06 * 0 + 0.0 + 0.6 * (1 - math.cos(a)), h + 0.6 * math.sin(a), 0.0) for a in np.linspace(0, math.pi / 2, 6)]
    for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'steel', a, b, 0.04, 8)
    x = pts[-1][0]; y = pts[-1][1]
    lathe(p, 'steel', [(0.05, y), (0.22, y - 0.1), (0.24, y - 0.14)], x + 0.0, 0.0, 0.0, 16); lathe(p, 'lamp_glass', [(0.2, y - 0.14), (0.2, y - 0.4), (0.12, y - 0.48)], x, 0.0, 0.0, 16)
    return p
def bollard():
    p = Piece(); lathe(p, 'steel', [(0.12, GY), (0.12, 0.85), (0.1, 0.9), (0.0, 0.93)], sec=14); lathe(p, 'trim_g', [(0.122, 0.6), (0.122, 0.7)], sec=14); return p
def taxi_sign():
    """Placa do ponto de taxi sem texto: poste com disco amarelo e faixa de quadriculado preto (pivo: chao)."""
    p = Piece(); lathe(p, 'steel', [(0.08, GY), (0.04, 0.1), (0.035, 2.6)], sec=12)
    R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    c = trimesh.creation.cylinder(radius=0.32, height=0.04, sections=32); c.apply_translation([0, 2.3, 0]); p.add('sign_y', c)
    for z in (-1, 1):
        for i in range(6):
            for j in range(2):
                if (i + j) % 2 == 0: p.box('dark', -0.27 + i * 0.09, -0.18 + i * 0.09, 2.21 + j * 0.09, 2.3 + j * 0.09, *sorted((z * 0.02, z * 0.025)))
    return p
def bike_rack():
    p = Piece()
    for k in range(4):
        x = -0.9 + k * 0.6; pts = [(x, GY + 0.2, -0.35)] + [(x, 0.15 + 0.55 + 0.25 * math.sin(t), -0.35 * math.cos(t)) for t in np.linspace(0, math.pi, 9)] + [(x, GY + 0.2, 0.35)]
        for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'steel', a, b, 0.025, 8)
    return p
def tree(h=6.0, r=1.8, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.16, -0.06), (0.12, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    return p

# ============================================================================ portas
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
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)

pieces = {f'w_{k}': wall(k) for k in ('rib', 'gb', 'high', 'door2', 'svc', 'dock', 'plain')}
pieces.update({
    'corner': corner(), 'arc_wall': arc_wall(), 'marquee': marquee(), 'pylon': pylon(), 'roof': roof(), 'canopy': canopy(),
    'floor': floor_piece(), 'plan': plan(), 'sink_bank': sink_bank(), 'urinal': urinal(),
    'bench_double': bench_double(), 'bench_wall': bench_wall(), 'lockers': lockers(1.6), 'kiosk': kiosk(), 'depart_board': depart_board(),
    'wall_clock': wall_clock(), 'pendant_globe': pendant_globe(), 'water_fountain': water_fountain(), 'trash_bin': trash_bin(), 'planter': planter(0.42),
    'stool': stool(), 'cafe_counter': cafe_counter(2.6), 'back_kitchen': back_kitchen(3.6), 'bag_shelf': bag_shelf(3.0), 'bag_cart': bag_cart(),
    'office_desk': office_desk(), 'safe': safe_box(), 'file_cab': file_cab(),
    'site': site(), 'wheel_stop': wheel_stop(), 'lamp_post': lamp_post(), 'bollard': bollard(), 'taxi_sign': taxi_sign(), 'bike_rack': bike_rack(),
    'tree': tree(), 'tree_b': tree(4.8, 1.5, 'leaf2', 4),
    'door_leaf_glass': door_glass(0.89, 2.36), 'door_leaf_arc': door_glass(0.83, 2.36), 'door_leaf_metal': door_metal(0.89, 2.13),
    'door_leaf_interior': door_interior(0.86, 2.08), 'player_scale_ref': player_ref()})
for i, (m, n) in enumerate((('sign_r', 1), ('sign_b', 2), ('sign_y', 3), ('led_g', 4))): pieces[f'bay_pole_{i + 1}'] = bay_pole(m, n)

# ============================================================================ montagem
FRONT = {-9: 'rib', -7: 'rib', -5: 'plain', -3: 'rib', -1: 'rib', 1: 'gb', 3: 'rib', 5: 'gb'}
BACK = {-9: 'high', -7: 'high', -5: 'high', -3: 'high', -1: 'dock', 1: 'plain', 3: 'svc', 5: 'high', 7: 'high', 9: 'high'}
WEST = {-5: 'high', -3: 'plain', -1: 'plain', 1: 'door2', 3: 'door2', 5: 'plain'}
EAST = {-5: 'high', -3: 'svc', -1: 'plain', 1: 'rib'}
tg = ['floor0', 'ext']
for x, k in FRONT.items(): put(f'w_{k}', x, Y0, HZ, 0, tg + ['front'])
for x, k in BACK.items(): put(f'w_{k}', x, Y0, -HZ, 180, tg + ['back'])
for z, k in WEST.items(): put(f'w_{k}', -HX, Y0, z, -90, tg + ['left'])
for z, k in EAST.items(): put(f'w_{k}', HX, Y0, z, 90, tg + ['right'])
for (x, z, ry) in ((-HX, HZ, -90), (-HX, -HZ, 180), (HX, -HZ, 90)): put('corner', x, Y0, z, ry, tg)
put('arc_wall', AC[0], Y0, AC[1], 0, tg + ['front']); put('marquee', AC[0], Y0, AC[1], 0, ['ext', 'front'])
put('roof', 0, Y0, 0, 0, ['roof']); put('pylon', AC[0] + 2.0, Y0 + HW, AC[1] + 2.0, 45, ['roof'])
put('canopy', -HX, 0, 0, -90, ['ext'])
put('floor', 0, Y0, 0, 0, ['floor0']); put('plan', 0, Y0, 0, 0, ['floor0'])
# portas
yd = Y0 + 0.006
for (k, lx, extra, d) in ((2, 0.4175, 180, -90), (3, -0.4175, 0, 90)):
    M = facet_xf(k); hp = M @ np.array([lx, 0.0, -0.15, 1.0]); R = 90 - math.degrees((k + 0.5) * 2 * AH)
    put('door_leaf_arc', AC[0] + hp[0], yd, AC[1] + hp[2], R + extra, ['floor0', 'front', 'ext'], door=d)
for zc in (1.0, 3.0):
    hx, hz = hinge(-HX, zc, -90, -0.9, -0.15); put('door_leaf_glass', hx, yd, hz, -90, ['floor0', 'left', 'ext'], door=90)
    hx, hz = hinge(-HX, zc, -90, 0.9, -0.15); put('door_leaf_glass', hx, yd, hz, 90, ['floor0', 'left', 'ext'], door=-90)
hx, hz = hinge(3.0, -HZ, 180, -0.45, -0.15); put('door_leaf_metal', hx, yd, hz, 180, ['floor0', 'back', 'ext'], door=90)
hx, hz = hinge(HX, -3.0, 90, -0.45, -0.15); put('door_leaf_metal', hx, yd, hz, 90, ['floor0', 'right', 'ext'], door=90)
for c in (-8.2, -4.85, -0.9, 5.0): put('door_leaf_interior', c - 0.43, Y0 + 0.01, ZP, 0, ['floor0'], door=90)
# salao
g = ['floor0']; y = Y0
for x in (-6.5, -2.5, 1.5): put('bench_double', x, y, 1.4, 0, g)
put('lockers', -XI, y, 4.85, 90, g); put('kiosk', -5.0, y, ZI, 180, g)
put('depart_board', 3.05, y + 2.5, ZP + t_ / 2, 0, g); put('wall_clock', -2.3, y + 3.1, ZP + t_ / 2, 0, g); put('water_fountain', -6.5, y, ZP + t_ / 2, 0, g)
for (x, z) in ((-9.3, 0.3), (5.6, 5.3), (-1.7, -1.1)): put('trash_bin', x, y, z, 0, g)
for (x, z) in ((4.6, 5.1), (-9.0, -0.7)): put('planter', x, y, z, 0, g)
for (x, z) in ((-8.5, 0.0), (-8.5, 5.0), (3.5, 0.4), (3.5, 5.0), (-3.0, 5.1), (0.5, 5.1)): put('pendant_globe', x, y + CEIL, z, 0, g)
# cafe, bilheteria, bagagem, banheiros
put('cafe_counter', 7.4, y, ZP - t_ / 2 - 0.72, 0, g); put('back_kitchen', 7.6, y, -ZI, 0, g)
for x in (6.4, 7.0, 7.6, 8.2): put('stool', x, y, -1.0, 0, g)
for x in (2.3, 3.8): put('office_desk', x, y, ZP - t_ / 2, 180, g)
put('safe', 1.6, y, -ZI, 0, g); put('file_cab', 4.6, y, -ZI, 0, g); put('file_cab', 5.1, y, -ZI, 0, g)
put('bag_shelf', -3.13, y, -3.6, 90, g); put('bag_cart', 0.2, y, -3.5, 0, g)
put('sink_bank', -XI, y, -2.7, 90, g); put('sink_bank', -3.27, y, -2.7, -90, g)
# plataforma e terreno
put('site', 0, 0, 0, 0, ['site'])
for z in (-3.0, -5.0): put('bench_wall', -HX, Y0, z, -90, ['site'])
for i, z in enumerate((-4.5, -1.5, 1.5, 4.5)): put(f'bay_pole_{i + 1}', -15.9, Y0, z, 90, ['site']); put('wheel_stop', -17.3, 0.0, z, 90, ['site'])
put('trash_bin', -12.0, Y0, -0.2, 0, ['site']); put('bike_rack', -15.0, Y0, 7.6, 0, ['site'])
for (x, z) in ((-10.2, 8.5), (1.5, 8.5), (9.0, 8.5)): put('lamp_post', x, Y0, z, 90, ['site'])
for (x, z) in ((-22.0, -9.6), (-22.0, 8.0)): put('lamp_post', x, 0.0, z, 0, ['site'])
for (i, x) in enumerate((-13.5, -7.0, -1.0, 4.0)): put('tree' if i % 2 == 0 else 'tree_b', x, Y0 - 0.06, 8.2, 0, ['site'])
for (x, z) in ((7.5, 8.75), (8.6, 8.75), (11.35, 3.0), (11.35, 4.5)): put('bollard', x, Y0, z, 0, ['site'])
put('taxi_sign', 11.35, Y0, 0.0, 90, ['site']); put('bench_wall', -4.0, Y0, HZ + 0.05, 0, ['site']); put('bench_wall', 0.0, Y0, HZ + 0.05, 0, ['site'])
put('tree_b', 12.8, 0.12, -9.8, 0, ['site'])
put('player_scale_ref', -13.0, Y0, 2.0); put('player_scale_ref', -4.0, Y0, 3.4, 0, ['floor0'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_raise': Y0,
                       'building': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 1, 'ceiling': CEIL, 'roof_slab': HW, 'parapet': HP,
                                    'round_corner': {'center': list(AC), 'radius': AR, 'facets': NA}},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1], 'walk_level': Y0},
                       'roof': 'flat membrane roof with a continuous coping, glazed roof monitor over the hall, 2 condensers, vents and a blank pylon sign',
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
