"""Kit 46: torre residencial art deco de 18 andares, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Embasamento de granito e saguao de pedra clara com janelas altas de bronze e portal de bronze com bandeira em raios de sol sob
marquise; 1o andar de pedra com cornija. Fuste de tijolo escuro com pilares de pedra salientes, janelas de caixilho de aco e
paineis de terracota com chevrons. Recuo no 12o andar com terraco cercado de platibanda, pilares com pinaculos escalonados;
fuste superior coroado por faixa de terracota com caneluras, pinaculos de canto e casa de maquinas com telhado em piramide e
mastro. Dentro: saguao com piso de granilite em raios de sol, lambri de marmore, recepcao curva, caixas de correio, lustres e
sofas; salao social com sinuca, biblioteca e lavanderia no 1o andar; andares baixos com 4 apartamentos (2 de frente com quarto
separado, 2 de fundos com quarto ao longo da fachada), andares altos com 2 estudios, lavanderia e deposito; escada em U e
elevador com portas de bronze. Fora: calcada com arvores em grelhas, postes, bancos, hidrante, bicicletario e rua.
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
from trimesh.visual.material import PBRMaterial
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'stone': (222, 214, 196), 'brick_d': (112, 66, 52), 'terra': (196, 112, 72), 'terra2': (168, 88, 58), 'granite': (96, 88, 90),
                  'bronze': (140, 102, 60), 'frame': (52, 60, 56), 'plaster': (238, 232, 220), 'ceil': (244, 242, 236), 'trim': (232, 226, 212),
                  'terrazzo': (214, 206, 188), 'terr_a': (176, 150, 112), 'terr_b': (96, 112, 110), 'marble': (232, 228, 220), 'marble_d': (60, 70, 72),
                  'parquet': (162, 112, 70), 'carpet': (120, 50, 52), 'carpet2': (160, 146, 122), 'tile': (226, 230, 226), 'tile_k': (180, 210, 200),
                  'porcelain': (244, 244, 238), 'chrome': (212, 214, 216), 'gold': (210, 170, 84), 'metal': (120, 126, 130), 'steel': (92, 96, 100),
                  'dkwood': (90, 58, 40), 'wood': (166, 120, 76), 'door': (96, 62, 42), 'door_int': (232, 224, 206), 'fabric': (70, 98, 92),
                  'fabric2': (176, 120, 60), 'fabric3': (120, 64, 74), 'leather': (110, 60, 40), 'linen': (242, 240, 232), 'rug': (128, 52, 46),
                  'rug2': (60, 84, 110), 'felt': (40, 110, 70), 'dark': (34, 34, 36), 'concrete': (184, 180, 172), 'asphalt': (70, 70, 72),
                  'curb': (190, 186, 178), 'grass': (100, 146, 70), 'leaf': (82, 128, 60), 'leaf2': (112, 148, 70), 'hedge': (64, 104, 52),
                  'bark': (96, 72, 52), 'mulch': (88, 64, 46), 'paint_w': (240, 240, 234), 'paint_y': (230, 190, 52), 'membrane': (150, 150, 148),
                  'paver': (190, 180, 164), 'roof_d': (58, 62, 70), 'cream': (240, 232, 214), 'appliance': (236, 236, 230), 'book_a': (140, 52, 44),
                  'book_b': (44, 72, 110), 'book_c': (70, 110, 70), 'book_d': (200, 170, 100), 'box_c': (176, 140, 96), 'red': (180, 40, 36),
                  'plant': (70, 120, 56), 'clay': (176, 98, 66), 'mirror': (196, 210, 216), 'cloth': (210, 200, 180)},
           texturas={'stone': 'stone2', 'brick_d': 'brick', 'terra': 'render', 'granite': 'stone', 'plaster': 'plaster', 'terrazzo': 'render',
                     'marble': 'render', 'parquet': 'planks', 'carpet': 'render', 'carpet2': 'render', 'concrete': 'render', 'asphalt': 'render',
                     'curb': 'render', 'grass': 'render', 'membrane': 'render', 'paver': 'stone', 'roof_d': 'shingles', 'dkwood': 'planks', 'wood': 'planks'},
           out=OUT)
D.METAL.update({'bronze', 'frame', 'chrome', 'gold', 'metal', 'steel'}); MATS = D.MATS; TEX = D.TEX
for k in ('chrome', 'mirror'): MATS[k].roughnessFactor = 0.15; MATS[k].metallicFactor = 0.9
MATS['bronze'].roughnessFactor = 0.35
configurar_telhado(0.07, 0.02, 50)

# ============================================================================ medidas
W = 2.0; T = 0.3; t_ = 0.12; SLAB = 0.25                   # modulo, parede externa, divisoria, laje
Y0 = 0.15; H0 = 4.2; H1 = 3.3; HF = 3.1                    # piso do saguao, saguao, 1o andar, andares tipo
NF = 18; NS = 12                                           # andares (0 a 17) e andar do recuo (terraco)
def lvl(k): return Y0 if k == 0 else (Y0 + H0 if k == 1 else Y0 + H0 + H1 + (k - 2) * HF)
YS = lvl(NS); YR = lvl(NF)                                 # terraco do recuo e cobertura
LX = 7.0; UX = 5.0                                         # meia largura do fuste baixo (andares 0 a 11) e do alto (12 a 17)
LI = LX - T; UI = UX - T
ZF = 0.8; ZB = -0.7                                        # eixos das paredes do corredor
XS = 0.3; SD = -1.4; ZL = ZB - 1.06                        # parede escada / elevador, porta da escada, borda do patamar
ZC = -4.7                                                  # fundo da escada nos andares tipo (face da parede do nucleo / fachada)
ZCW = ZC - t_ / 2                                          # eixo da parede atras do nucleo (andares baixos)
PAR = 1.1                                                  # platibanda do terraco
CEIL = HF - SLAB
PIER = 0.15; PW = 0.2                                      # saliencia e meia largura dos pilares
GY = -0.2                                                  # base das calcadas
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

# ============================================================================ paredes externas
BASE_IN = [(-T, 0.0), (-T - 0.016, 0.0), (-T - 0.016, 0.1), (-T - 0.008, 0.115), (-T, 0.118)]
def wall_core(p, holes, h, y0=0.0, out='brick_d', inner_top=None, par=None, inner=None):
    """Parede de 2 m: material externo, gesso (ou 'inner') por dentro ate inner_top."""
    it = (h - 0.005) if inner_top is None else inner_top; top = h + (par or 0.0)
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, 0.0, it, top] + ([h] if par else []) + [v for hh in holes for v in hh[2:]]))
    ys = [v for v in ys if y0 <= v <= top]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return (inner or 'plaster') if 0 < cy < it else (out if cy > h or cy < 0 else None)
        return out
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
def chevron_panel(p, x0, x1, y0, y1, z0=0.0, n=3, mat='terra', relief='terra2'):
    """Painel de terracota (face em z0, para +Z): moldura, fundo e 2 chevrons em relevo."""
    rect = sbox(x0, y0, x1, y1); inner = sbox(x0 + 0.035, y0 + 0.035, x1 - 0.035, y1 - 0.035)
    ext(p, mat, rect, z0, z0 + 0.022); ext(p, mat, rect.difference(inner), z0 + 0.022, z0 + 0.04)
    hy = (y1 - y0 - 0.07) / 2
    for k, yy in enumerate((y0 + 0.035 + hy * 0.45, y0 + 0.035 + hy * 1.25)):
        pts = []
        for i in range(2 * n + 1):
            x = x0 + 0.035 + i * (x1 - x0 - 0.07) / (2 * n); pts.append((x, yy + (0.16 if i % 2 else 0.0) * (hy / 0.25) * 0.5))
        ln = LineString(pts).buffer(0.022, cap_style=2, join_style=2, mitre_limit=4).intersection(inner)
        ext(p, relief, ln, z0 + 0.022, z0 + 0.034)
def steel_win(p, a, b, y0, y1, mat='frame', inner_sill='trim'):
    """Janela de caixilho de aco (face externa em z = 0): marco, 2 montantes e travessas finas, basculante no alto, vidro,
    peitoril de pedra com pingadeira e peitoril interno."""
    z0, z1 = -0.14, -0.08; f = 0.045; zg = -0.11
    p.box(mat, a, a + f, y0, y1, z0, z1); p.box(mat, b - f, b, y0, y1, z0, z1)
    p.box(mat, a + f, b - f, y1 - f, y1, z0, z1); p.box(mat, a + f, b - f, y0, y0 + f, z0, z1)
    p.box('glass', a + f, b - f, y0 + f, y1 - f, zg - 0.003, zg + 0.003)
    yt = y0 + (y1 - y0) * 0.72
    p.box(mat, a + f, b - f, yt - 0.02, yt + 0.02, z0 + 0.005, z1 - 0.005)
    for k in (1, 2):
        x = a + (b - a) * k / 3; p.box(mat, x - 0.014, x + 0.014, y0 + f, y1 - f, zg - 0.014, zg + 0.014)
    for k in (1, 2):
        y = y0 + f + (yt - 0.02 - y0 - f) * k / 3; p.box(mat, a + f, b - f, y - 0.01, y + 0.01, zg - 0.012, zg + 0.012)
    p.box(mat, a + f + 0.01, b - f - 0.01, yt + 0.02, yt + 0.045, z0 - 0.012, z0)
    p.box('dark', a + f + 0.02, b - f - 0.02, y1 - f - 0.03, y1 - f - 0.005, z0 - 0.01, z0)
    for x in (a + (b - a) / 3 - 0.05, a + 2 * (b - a) / 3 + 0.05): p.box('bronze', x - 0.01, x + 0.01, y0 + 0.5, y0 + 0.62, z0 - 0.03, z0)
    prof_x(p, 'stone', a - 0.06, b + 0.06, [(0.0, y0 - 0.075), (0.07, y0 - 0.075), (0.07, y0 - 0.035), (0.0, y0)])
    p.box(inner_sill, a - 0.03, b + 0.03, y0 - 0.02, y0 + 0.012, -T - 0.035, z0)
def piers(p, y0, y1, mat='stone', d=PIER):
    for s in (-1, 1): p.box(mat, *sorted((s * (1.0 - PW), s * 1.0)), y0, y1, 0.0, d)
def fmod(kind='win'):
    """Modulo do fuste (pivo: face externa, cota do piso do andar; para +Z): win (janela com painel de chevrons embaixo),
    plain (vao cego com faixa de terracota canelada), door (porta de vidro para o terraco). Meios pilares de pedra nas pontas."""
    p = Piece(); h = HF; holes = []
    if kind == 'win': holes = [(-0.6, 0.6, 0.8, 2.4)]
    if kind == 'door': holes = [(-0.5, 0.5, 0.0, 2.45)]
    wall_core(p, holes, h, 0.0, 'brick_d', inner_top=h)
    piers(p, 0.0, h)
    gaps = []
    if kind == 'win':
        steel_win(p, -0.6, 0.6, 0.8, 2.4); chevron_panel(p, -0.72, 0.72, 0.08, 0.66)
    if kind == 'plain':
        p.box('terra', -0.3, 0.3, 0.0, h, 0.0, 0.025)
        for x in (-0.2, 0.0, 0.2): p.box('terra2', x - 0.035, x + 0.035, 0.0, h, 0.025, 0.05)
    if kind == 'door':
        z0, z1 = -0.16, -0.06
        p.box('frame', -0.5, -0.45, 0.0, 2.45, z0, z1); p.box('frame', 0.45, 0.5, 0.0, 2.45, z0, z1); p.box('frame', -0.45, 0.45, 2.39, 2.45, z0, z1)
        p.box('stone', -0.5, 0.5, -0.025, 0.008, -T + 0.004, 0.06); gaps = [(-0.5, 0.5)]
        prof_x(p, 'stone', -0.58, 0.58, [(0.0, 2.45), (0.05, 2.45), (0.05, 2.6), (0.0, 2.64)])
    for (a, b) in segs_excl(gaps, -0.999, 0.999, 0.0): prof_x(p, 'trim', a, b, BASE_IN)
    return p

PORTAL_H = 3.1
def gmod(kind='win'):
    """Modulo do saguao (pivo: face externa, cota do piso; de -Y0 a H0): embasamento de granito (para nas portas), pedra clara,
    meios pilares; win (janela alta de bronze com bandeira gradeada e verga esculpida), door (portal de bronze: porta dupla,
    bandeira com raios de sol, molduras escalonadas, arandelas), svc (porta de servico), plain. Lambri de marmore por dentro."""
    p = Piece(); holes = []; gaps = []
    if kind == 'win': holes = [(-0.65, 0.65, 1.0, 3.6)]
    if kind == 'door': holes = [(-0.85, 0.85, 0.0, PORTAL_H)]; gaps = [(-1.0, 1.0)]
    if kind == 'svc': holes = [(-0.5, 0.5, 0.0, 2.2)]; gaps = [(-0.5, 0.5)]
    wall_core(p, holes, H0, -Y0, 'stone', inner_top=H0)
    GR = [(0.0, -Y0), (0.05, -Y0), (0.05, 0.8), (0.03, 0.86), (0.0, 0.9)]
    if kind != 'door':
        for s in (-1, 1):
            p.box('granite', *sorted((s * (1.0 - PW), s * 1.0)), -Y0, 0.9, 0.0, PIER + 0.04)
            p.box('stone', *sorted((s * (1.0 - PW), s * 1.0)), 0.9, H0, 0.0, PIER)
    pad = 0.09 if kind == 'svc' else 0.0
    for (a, b) in segs_excl(gaps, -1.0, 1.0, pad): prof_x(p, 'granite', a, b, GR)
    if kind == 'win':
        a, b, y0, y1 = -0.65, 0.65, 1.0, 3.6; z0, z1 = -0.17, -0.07; f = 0.06; yt = 2.95
        p.box('bronze', a, a + f, y0, y1, z0, z1); p.box('bronze', b - f, b, y0, y1, z0, z1)
        p.box('bronze', a + f, b - f, y1 - f, y1, z0, z1); p.box('bronze', a + f, b - f, y0, y0 + f, z0, z1)
        p.box('bronze', a + f, b - f, yt - 0.035, yt + 0.035, z0, z1); p.box('bronze', -0.025, 0.025, y0 + f, yt - 0.035, z0 + 0.01, z1 - 0.01)
        p.box('glass', a + f, b - f, y0 + f, y1 - f, -0.123, -0.117)
        for x in np.arange(a + f + 0.1, b - f - 0.05, 0.1): p.box('bronze', x - 0.008, x + 0.008, yt + 0.035, y1 - f, -0.1, -0.085)
        for k in range(9):
            ang = math.pi * (k + 1) / 10; xx = 0.42 * math.cos(ang); yy = yt + 0.035 + 0.5 * math.sin(ang)
            p.seg('bronze', (0.0, yt + 0.035, -0.08), (xx, min(yy, y1 - f - 0.01), -0.08), 0.014, 0.014)
        prof_x(p, 'stone', a - 0.07, b + 0.07, [(0.0, y0 - 0.08), (0.08, y0 - 0.08), (0.08, y0 - 0.04), (0.0, y0)])
        p.box('marble', a - 0.01, b + 0.01, y0 - 0.02, y0 + 0.012, -T - 0.03, z0)
        for (xa, xb, ya, yb) in ((-0.34, 0.34, 3.64, 3.86), (-0.22, 0.22, 3.86, 4.0), (-0.1, 0.1, 4.0, 4.1)): p.box('stone', xa, xb, ya, yb, 0.0, 0.03)
    if kind == 'door':
        a, b, y1 = -0.85, 0.85, PORTAL_H; z0, z1 = -0.2, -0.08; yd = 2.42
        p.box('bronze', a, a + 0.05, 0.0, y1, z0, z1); p.box('bronze', b - 0.05, b, 0.0, y1, z0, z1); p.box('bronze', a, b, y1 - 0.05, y1, z0, z1)
        p.box('bronze', a + 0.05, b - 0.05, yd, yd + 0.07, z0, z1)
        p.box('glass', a + 0.05, b - 0.05, yd + 0.07, y1 - 0.05, -0.143, -0.137)
        cx, cy = 0.0, yd + 0.07; R = y1 - 0.05 - cy
        for k in range(11):
            ang = math.pi * (k + 1) / 12; p.seg('bronze', (cx, cy, -0.12), (cx + 0.78 * math.cos(ang) if abs(math.cos(ang)) > 0.01 else cx, cy + min(R - 0.01, 0.78 * math.sin(ang)), -0.12), 0.016, 0.016)
        disc_z(p, 'bronze', 0.16, -0.13, -0.11, cx, cy, 20)
        for (xa, xb) in ((-1.0, -0.85), (0.85, 1.0)):
            p.box('granite', xa, xb, -Y0, 0.9, 0.0, 0.34); p.box('stone', xa, xb, 0.9, y1, 0.0, 0.3)
            p.box('stone', xa + (0.05 if xa < 0 else 0.0), xb - (0.0 if xa < 0 else 0.05), 0.9, y1, 0.3, 0.36)
        p.box('stone', -1.0, 1.0, y1, H0, 0.0, 0.3); p.box('stone', -0.95, 0.95, y1, y1 + 0.5, 0.3, 0.36)
        for (w_, y_) in ((0.7, 4.05), (0.45, 4.2)): pass
        fan = [Polygon([(0.0, y1 + 0.04)] + [(0.42 * math.cos(t), y1 + 0.04 + 0.42 * math.sin(t)) for t in np.linspace(math.pi * k / 7, math.pi * (k + 0.6) / 7, 4)]) for k in range(7)]
        for f_ in fan: ext(p, 'stone', f_, 0.36, 0.385)
        p.box('stone', -0.62, 0.62, y1 + 0.5, y1 + 0.58, 0.3, 0.38)
        p.box('granite', a, b, -Y0, 0.006, -T + 0.004, 0.34)
        for s in (-1, 1):
            q = Piece(); q.cham('bronze', -0.07, 0.07, -0.18, 0.18, 0.0, 0.03, 0.006)
            for (r, y) in ((0.06, -0.05), (0.1, 0.05), (0.07, 0.25)): pass
            q.hull('lamp_glass', [(x, y, z) for x in (-0.07, 0.07) for y in (-0.15, 0.2) for z in (0.06, 0.16)])
            for (yy, ww) in ((-0.17, 0.09), (0.2, 0.09), (0.25, 0.06), (0.29, 0.03)): q.box('bronze', -ww, ww, yy, yy + 0.04, 0.04, 0.18)
            q.box('bronze', -0.015, 0.015, -0.12, 0.1, 0.03, 0.06)
            p.merge(q, tr(s * 0.925, 2.1, 0.36))
    if kind == 'svc':
        q = Piece(); door_casing(q, 1.0, T, 2.2); p.merge(q, tr(0, 0, -T / 2))
        q = wall_lantern(); p.merge(q, tr(0, 2.6, 0.0))
        p.box('granite', -0.5, 0.5, -0.03, 0.006, -T + 0.004, 0.06)
    if kind == 'plain':
        for (xa, xb, ya, yb) in ((-0.5, 0.5, 1.4, 3.4),): ext(p, 'stone', sbox(xa, ya, xb, yb).difference(sbox(xa + 0.06, ya + 0.06, xb - 0.06, yb - 0.06)), 0.0, 0.03)
    # lambri de marmore por dentro (para nas portas)
    wg = [(-0.86, 0.86)] if kind == 'door' else ([(-0.59, 0.59)] if kind == 'svc' else [])
    for (a, b) in segs_excl(wg, -0.999, 0.999):
        p.box('marble', a, b, 0.0, 0.9, -T - 0.02, -T); p.box('marble_d', a, b, 0.9, 0.95, -T - 0.03, -T)
        p.box('marble_d', a + 0.001, b - 0.001, 0.0, 0.14, -T - 0.035, -T - 0.019)
    return p

CORN = lambda h: [(0.0, h - 0.42), (0.05, h - 0.42), (0.05, h - 0.36), (0.12, h - 0.3), (0.12, h - 0.24), (0.2, h - 0.2), (0.3, h - 0.1), (0.3, h - 0.004), (0.0, h - 0.004)]
def cmod(kind='win'):
    """Modulo do 1o andar (pivo: face externa, cota do piso): pedra clara, janela de aco, painel canelado embaixo, cornija."""
    p = Piece(); h = H1; holes = [(-0.6, 0.6, 0.8, 2.4)] if kind == 'win' else []
    wall_core(p, holes, h, 0.0, 'stone', inner_top=h)
    piers(p, 0.0, h - 0.05)
    if kind == 'win':
        steel_win(p, -0.6, 0.6, 0.8, 2.4)
        ext(p, 'stone', sbox(-0.6, 0.12, 0.6, 0.66).difference(sbox(-0.55, 0.17, 0.55, 0.61)), 0.0, 0.03)
        for x in np.linspace(-0.45, 0.45, 7): p.box('stone', x - 0.02, x + 0.02, 0.17, 0.61, 0.0, 0.02)
    prof_x(p, 'stone', -1.0, 1.0, CORN(h))
    for (a, b) in segs_excl([], -0.999, 0.999): prof_x(p, 'trim', a, b, BASE_IN)
    return p
def pmod():
    """Platibanda do terraco do recuo (pivo: face externa, cota do terraco): tijolo, friso de chevrons, capa de pedra,
    pilares que sobem em pinaculos escalonados."""
    p = Piece()
    p.box('brick_d', -1.0, 1.0, 0.0, PAR, -T, 0.0)
    chevron_panel(p, -0.72, 0.72, 0.15, 0.8)
    p.cham('stone', -1.0, 1.0, PAR, PAR + 0.08, -T - 0.04, 0.04, 0.008)
    for s in (-1, 1):
        a, b = sorted((s * (1.0 - PW), s * 1.0)); p.box('stone', a, b, 0.0, PAR + 0.45, 0.0, PIER)
        a, b = sorted((s * (1.0 - PW + 0.06), s * 1.0)); p.box('stone', a, b, PAR + 0.45, PAR + 0.72, 0.0, PIER - 0.05)
    return p
def kmod():
    """Coroa do fuste alto (pivo: face externa, cota da cobertura): faixa de terracota com caneluras e friso de chevrons, base e
    capa de pedra, pilares com pinaculos escalonados."""
    p = Piece(); h = 2.0
    p.box('terra', -1.0, 1.0, 0.0, h, -T, 0.0)
    prof_x(p, 'stone', -1.0, 1.0, [(0.0, 0.0), (0.07, 0.0), (0.07, 0.18), (0.0, 0.25)])
    for x in (-0.6, -0.3, 0.0, 0.3, 0.6): p.cham('terra2', x - 0.06, x + 0.06, 0.4, 1.45, 0.0, 0.05, 0.012)
    ln = LineString([(-0.8 + i * 0.2, 1.62 + (0.2 if i % 2 else 0.0)) for i in range(9)]).buffer(0.035, cap_style=2, join_style=2, mitre_limit=4).intersection(sbox(-0.8, 1.5, 0.8, 1.92))
    ext(p, 'terra2', ln, 0.0, 0.04)
    p.cham('stone', -1.0, 1.0, h, h + 0.1, -T - 0.04, 0.06, 0.008)
    for s in (-1, 1):
        a, b = sorted((s * (1.0 - PW), s * 1.0)); p.box('stone', a, b, 0.0, h + 0.55, 0.0, PIER)
        a, b = sorted((s * (1.0 - PW + 0.06), s * 1.0)); p.box('stone', a, b, h + 0.55, h + 0.9, 0.0, PIER - 0.05)
    return p
def kcorner(kind='typ'):
    """Quina (pivo: quina externa; paredes em -X e -Z): pilar de canto de pedra, 4 mm saliente sobre as pontas dos modulos.
    typ / c (com cornija em meia-esquadria) / g (granito embaixo) / par e crown (macicos, com pinaculos escalonados)."""
    p = Piece(); e = 0.004; a = 0.38; P = 0.2; d = -0.002
    def Lb(mat, y0, y1, a=a, P=P, full=False):
        if full: p.box(mat, -a, P, y0, y1, -a, P); return
        p.box(mat, -a, P, y0, y1, -T + e, P); p.box(mat, -T + e, P, y0, y1, -a, -T + e)
    if kind == 'typ': Lb('stone', d, HF + d)
    if kind == 'c':
        Lb('stone', d, H1 + d); q = Piece(); mitre_pair(q, 'stone', CORN(H1)); p.merge(q)
    if kind == 'g':
        Lb('granite', -Y0 + d, 0.92, a + 0.03, P + 0.04); Lb('stone', 0.92, H0 + d)
    if kind == 'par':
        Lb('stone', d, PAR + 0.6, full=True); Lb('stone', PAR + 0.6, PAR + 0.95, 0.3, 0.13, True); Lb('stone', PAR + 0.95, PAR + 1.15, 0.22, 0.06, True)
    if kind == 'crown':
        Lb('stone', d, 2.75, full=True); Lb('stone', 2.75, 3.25, 0.3, 0.13, True); Lb('stone', 3.25, 3.6, 0.22, 0.06, True)
        p.hull('stone', [(x, 3.6, z) for x in (-0.18, 0.02) for z in (-0.18, 0.02)] + [(-0.08, 3.95, -0.08)])
    return p

def mirror_z(z0=0.0):
    M = np.eye(4); M[2, 2] = -1; M[2, 3] = 2 * z0; return M

# ============================================================================ paredes internas, escada, elevador
def iwall(Ln, h, cuts=(), t=t_, tp=(0.016, 0.016), tm=(0.016, 0.016), base=(1, 1)):
    """Parede interna (pivo: inicio, eixo; vai para +X). cuts = (centro, largura, y0, y1, tipo): door (com batente e guarnicao)
    ou pass (vao livre). tp / tm: quanto o rodape do lado +Z / -Z para antes do inicio e do fim (encontro com outra parede)."""
    p = Piece(); cs = [(c - w / 2, c + w / 2, y0, y1, k) for (c, w, y0, y1, k) in cuts]
    xs = sorted(set([0.0, Ln] + [v for c in cs for v in c[:2]])); ys = sorted(set([0.0, h] + [v for c in cs for v in c[2:4]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        return None if any(a < cx < b and y0 < cy < y1 for (a, b, y0, y1, _) in cs) else 'plaster'
    for m, mesh in grid_solid(xs, ys, [-t / 2, t / 2], cell).items(): p.add(m, mesh)
    for (a, b, y0, y1, k) in cs:
        if k == 'door': q = Piece(); door_casing(q, b - a, t, y1); p.merge(q, tr((a + b) / 2, 0, 0))
    gaps = [(a - (0.08 if k == 'door' else 0.0), b + (0.08 if k == 'door' else 0.0)) for (a, b, y0, y1, k) in cs if y0 < 0.01]
    for side, (s0, s1), on in ((1, tp, base[0]), (-1, tm, base[1])):
        if not on: continue
        for (a, b) in segs_excl(gaps, s0, Ln - s1):
            if b - a > 0.02: prof_x(p, 'trim', a, b, D.BASE_PROF(t) if side > 0 else [(-z, y) for (z, y) in D.BASE_PROF(t)][::-1])
    return p
def wall_z(p, x, z0, z1, h, cuts=(), **kw):
    """Parede ao longo de +Z (de z0 a z1) no eixo x; lado +Z local da iwall = -X do mundo. cuts com centro em z do mundo."""
    q = iwall(z1 - z0, h, [(c - z0, w, a, b, k) for (c, w, a, b, k) in cuts], **kw); p.merge(q, rot_y(-90, (x, 0, z0)))
def wall_x(p, z, x0, x1, h, cuts=(), **kw):
    q = iwall(x1 - x0, h, [(c - x0, w, a, b, k) for (c, w, a, b, k) in cuts], **kw); p.merge(q, tr(x0, 0, z))
DR = lambda c, w=0.9: (c, w, 0.0, 2.1, 'door')
def stair_u(H, n, zback=ZC, g=0.26, mat='concrete', nose='metal'):
    """Escada em U do nucleo (pivo: origem do predio, cota do piso do andar): lance que sobe de ZL para os fundos, patamar e lance
    que volta ate ZL no andar de cima; degraus macicos com bocel, corrimaos nas paredes e guarda-corpo central de barras."""
    p = Piece(); r = H / (2 * n); xa0, xa1 = -1.94, -0.89; xb0, xb1 = -0.81, 0.24
    zl = ZL - (n - 1) * g
    for i in range(1, n):
        z0, z1 = ZL - i * g, ZL - (i - 1) * g; y = i * r
        p.box(mat, xa0, xa1, max(0.0, y - r - 0.16), y, z0, z1); p.box(nose, xa0, xa1, y, y + 0.004, z1 - 0.04, z1)
    p.box(mat, xa0, xb1, H / 2 - 0.2, H / 2, zback, zl)
    for i in range(1, n):
        z0, z1 = zl + (i - 1) * g, zl + i * g; y = H / 2 + i * r
        p.box(mat, xb0, xb1, y - r - 0.16, y, z0, z1); p.box(nose, xb0, xb1, y, y + 0.004, z0, z0 + 0.04)
    p.box(mat, xa1, xb0, 0.0, H / 2, zl, ZL)
    for (x, za, zb, ya, yb) in ((-1.9, ZL, zl, 0.9, H / 2 + 0.9), (0.2, zl, ZL, H / 2 + 0.9, H + 0.9)):
        seg_cyl(p, 'bronze', (x, ya, za), (x, yb, zb), 0.02, 8)
        for z in np.linspace(za, zb, 4): seg_cyl(p, 'bronze', (x, ya + (yb - ya) * (z - za) / (zb - za), z), (x + (0.04 if x < 0 else -0.04), ya + (yb - ya) * (z - za) / (zb - za), z), 0.008, 6)
    for (za, zb, ya, yb) in ((ZL, zl, 0.0, H / 2), (zl, ZL, H / 2, H)):
        top = lambda z: ya + (yb - ya) * (z - za) / (zb - za) + 0.95
        seg_cyl(p, 'bronze', (-0.85, top(za), za), (-0.85, top(zb), zb), 0.024, 8)
        for z in np.arange(min(za, zb) + 0.12, max(za, zb) - 0.05, 0.12):
            yy = ya + (yb - ya) * (z - za) / (zb - za); p.box('iron', -0.86, -0.84, yy + r, top(z), z - 0.008, z + 0.008)
    return p
def elevator(p, zc):
    """Portas de bronze do elevador com leque em relevo, batente, indicador de ponteiro sem numeros e botoeira (face em zc)."""
    for (a, b) in ((0.7, 1.15), (1.15, 1.6)):
        p.box('bronze', a, b, 0.0, 2.1, zc - 0.07, zc - 0.05)
        cx = 1.15; fan = [Polygon([(cx, 1.15)] + [(cx + 0.4 * math.cos(t), 1.15 + 0.4 * math.sin(t)) for t in np.linspace(math.pi * k / 6, math.pi * (k + 0.55) / 6, 4)]) for k in range(6)]
        for f_ in fan:
            g_ = f_.intersection(sbox(a + 0.03, 0.2, b - 0.03, 2.0))
            if g_.area > 1e-5: ext(p, 'gold', g_, zc - 0.05, zc - 0.044)
        p.box('gold', a + 0.03, b - 0.03, 0.12, 0.16, zc - 0.05, zc - 0.045)
    p.box('dark', 1.148, 1.152, 0.0, 2.1, zc - 0.05, zc - 0.046)
    for (a, b) in ((0.62, 0.71), (1.59, 1.68)): p.box('bronze', a, b, 0.0, 2.2, ZB - t_ / 2 - 0.02, zc + 0.02)
    p.box('bronze', 0.62, 1.68, 2.09, 2.2, ZB - t_ / 2 - 0.02, zc + 0.02)
    p.box('bronze', 0.85, 1.45, 2.26, 2.3, zc, zc + 0.03)
    pts = [(1.15 + 0.28 * math.cos(t), 2.3 + 0.28 * math.sin(t)) for t in np.linspace(0, math.pi, 13)]
    ext(p, 'bronze', Polygon(pts), zc, zc + 0.02); ext(p, 'cream', Polygon([(1.15 + 0.23 * math.cos(t), 2.32 + 0.21 * math.sin(t)) for t in np.linspace(0, math.pi, 13)]), zc + 0.02, zc + 0.024)
    p.seg('dark', (1.15, 2.33, zc + 0.03), (1.15 + 0.15, 2.33 + 0.12, zc + 0.03), 0.012, 0.006)
    p.cham('bronze', 1.8, 1.9, 1.0, 1.25, zc, zc + 0.012, 0.003)
    for y in (1.07, 1.17): disc_z(p, 'lamp_glass', 0.018, zc + 0.012, zc + 0.018, 1.85, y, 10)

def deco_light(p, x, y, z, r=0.22):
    """Luminaria de teto deco: canopla, haste, prato de vidro fosco escalonado (pivo: forro em y)."""
    p.cyl('bronze', 0.06, y - 0.03, y, x, z, 14); p.cyl('bronze', 0.012, y - 0.3, y - 0.03, x, z, 8)
    lathe(p, 'lamp_glass', [(0.0, y - 0.42), (r * 0.6, y - 0.4), (r, y - 0.32), (r * 0.95, y - 0.305), (0.0, y - 0.305)], x, z, 0.0, 20)
    lathe(p, 'bronze', [(r + 0.01, y - 0.33), (r + 0.01, y - 0.3), (r * 0.9, y - 0.3)], x, z, 0.0, 20)

# ============================================================================ lajes
HOLE_T = sbox(-1.939, ZC, 0.24, ZL)
def slab(kind='l'):
    """Laje / piso (pivo: origem, cota do piso). l: andares baixos, u: altos, 1: 1o andar (abertura da escada do saguao ate o fundo),
    0: piso do saguao (granilite com leque), roof: cobertura com manta e alcapao. Forro por baixo, acabamentos por ambiente."""
    p = Piece(); xi = UI if kind in ('u', 'roof') else LI
    inner = sbox(-xi, -xi, xi, xi)
    hole = {'l': HOLE_T, 'u': HOLE_T, '1': sbox(-1.939, -LI, 0.24, ZL), '0': None, 'roof': sbox(-0.7, -1.5, -0.1, -0.9)}[kind]
    if hole is not None: inner = inner.difference(hole)
    if kind == '0':
        ext_y(p, 'concrete', inner, -Y0 + 0.02, -0.012)
    else:
        ext_y(p, 'ceil', inner, -SLAB, -SLAB + 0.01); ext_y(p, 'concrete', inner, -SLAB + 0.01, -0.012)
    if kind == 'roof':
        ext_y(p, 'membrane', inner, -0.012, 0.0)
        for (a, b, c, d) in ((-0.76, -0.04, -1.56, -1.5), (-0.76, -0.04, -0.9, -0.84), (-0.76, -0.7, -1.5, -0.9), (-0.1, -0.04, -1.5, -0.9)):
            p.box('metal', a, b, 0.0, 0.25, c, d)
        p.box('metal', -0.78, -0.02, 0.25, 0.29, -1.58, -0.82); p.box('metal', -0.4, -0.3, 0.29, 0.31, -0.84, -0.8)
        return p
    land = sbox(-1.94, ZL, 0.24, ZB); corr = sbox(-xi, ZB, xi, ZF)
    if kind in ('l', 'u'):
        baths = []
        for s in (-1, 1):
            if kind == 'l': bb = [sbox(-2.3, ZF, 0.0, 3.0), sbox(-LI, -2.8, -4.6, ZB)]
            else: bb = [sbox(-UI, ZF, -2.6, 2.9), sbox(-UI, -UI, -2.0, ZB)] if s < 0 else [sbox(-UI, ZF, -2.6, 2.9)]
            for b in bb: baths.append(b if s < 0 else Polygon([(-x, z) for (x, z) in b.exterior.coords]))
        shaft = sbox(0.3, ZC if kind == 'u' else ZC, 2.0, ZB)
        store = sbox(2.0, -UI, UI, ZB) if kind == 'u' else Polygon()
        ext_y(p, 'carpet', corr.difference(land), -0.012, 0.0); ext_y(p, 'stone', land, -0.012, 0.0)
        for b in baths: ext_y(p, 'tile', b.intersection(inner), -0.012, 0.0)
        ext_y(p, 'dark', shaft, -0.012, 0.0)
        if kind == 'u': ext_y(p, 'concrete', store, -0.0119, 0.0)
        rest = inner.difference(unary_union([corr, land, shaft, store] + baths))
        ext_y(p, 'parquet', rest, -0.012, 0.0)
        return p
    if kind == '1':
        club = sbox(-xi, ZB, xi, xi); ext_y(p, 'parquet', club, -0.012, 0.0)
        ext_y(p, 'stone', land, -0.012, 0.0); ext_y(p, 'dark', sbox(0.3, -LI, 2.0, ZB), -0.012, 0.0)
        ext_y(p, 'carpet2', inner.difference(unary_union([club, land, sbox(0.3, -LI, 2.0, ZB)])), -0.012, 0.0)
        return p
    # saguao: granilite com leque de raios a partir da porta, faixas e filetes de latao
    C = (0.0, LI); R0, R1 = 4.2, 4.5
    fanr = Point(C).buffer(R0, 64).intersection(inner)
    lobby = sbox(-xi, ZB, xi, xi)
    for k in range(12):
        t0, t1 = math.pi + math.pi * k / 12, math.pi + math.pi * (k + 1) / 12
        w_ = Polygon([C] + [(C[0] + 9 * math.cos(t), C[1] + 9 * math.sin(t)) for t in np.linspace(t0, t1, 4)]).intersection(fanr)
        ext_y(p, 'terr_a' if k % 2 == 0 else 'terrazzo', w_, -0.012, 0.0)
    ring = Point(C).buffer(R1, 64).difference(Point(C).buffer(R0, 64)).intersection(inner); ext_y(p, 'terr_b', ring, -0.012, 0.0)
    border = lobby.difference(off(lobby, -0.3)); rest = lobby.difference(Point(C).buffer(R1, 64)).difference(border)
    ext_y(p, 'terrazzo', rest, -0.012, 0.0); ext_y(p, 'terr_b', border.difference(Point(C).buffer(R1, 64)), -0.012, 0.0)
    for k in range(13):
        t = math.pi + math.pi * k / 12
        if 0 < k < 12: p.seg('gold', (C[0], 0.0, C[1]), (C[0] + R1 * math.cos(t), 0.0, C[1] + R1 * math.sin(t)), 0.012, 0.004)
    ext_y(p, 'terrazzo', inner.difference(lobby).difference(land), -0.012, 0.0); ext_y(p, 'stone', land, -0.012, 0.0)
    return p

# ============================================================================ plantas
def plan_low():
    """Paredes internas dos andares baixos (pivo: origem, cota do piso): corredor, nucleo (escada, elevador), parede atras do
    nucleo com as portas dos quartos dos fundos, divisorias, banheiros, luzes do corredor e portas do elevador."""
    p = Piece(); h = CEIL; xi = LI
    wall_x(p, ZF, -xi, xi, h, [DR(-3.0), DR(3.0)])
    wall_x(p, ZB, -xi, xi, h, [DR(-3.4), DR(SD), DR(3.4), (1.15, 0.9, 0.0, 2.1, 'pass')])
    wall_x(p, ZCW, -xi, xi, h, [DR(-3.0), DR(3.0)])
    wall_z(p, XS, ZC, ZB - t_ / 2, h, base=(0, 0))
    wall_z(p, 0.0, ZF + t_ / 2, xi, h); wall_z(p, 0.0, -xi, ZCW - t_ / 2, h)
    half = Piece()
    wall_z(half, -2.0, ZC, ZB - t_ / 2, h, base=(1, 0))
    wall_z(half, -3.7, ZF + t_ / 2, 2.94, h, [(2.0, 0.8, 0.0, 2.1, 'door')], tp=(0.016, 0.016), tm=(0.016, 0.0))
    wall_z(half, -2.3, ZF + t_ / 2, 2.94, h, [(1.9, 0.76, 0.0, 2.06, 'door')], tp=(0.016, 0.0), tm=(0.016, 0.016))
    wall_x(half, 3.0, -xi, -3.64, h, tp=(0.016, 0.0), tm=(0.016, 0.136))
    wall_x(half, 3.0, -2.36, -0.06, h, tp=(0.0, 0.016), tm=(0.136, 0.016))
    wall_z(half, -4.6, -2.74, ZB - t_ / 2, h, [(-1.6, 0.76, 0.0, 2.06, 'door')], tp=(0.016, 0.016), tm=(0.0, 0.016))
    wall_x(half, -2.8, -xi, -4.54, h, tp=(0.016, 0.136), tm=(0.016, 0.0))
    p.merge(half); p.merge(half, mirror_x())
    elevator(p, ZB + t_ / 2)
    for x in (-5.0, -1.5, 1.5, 5.0): deco_light(p, x, h, (ZB + ZF) / 2, 0.16)
    return p
def plan_up():
    """Paredes internas dos andares altos: corredor, nucleo, estudios de frente, lavanderia e deposito nos fundos."""
    p = Piece(); h = CEIL; xi = UI
    wall_x(p, ZF, -xi, xi, h, [DR(-1.2), DR(1.2)])
    wall_x(p, ZB, -xi, xi, h, [DR(-3.4), DR(SD), DR(3.4), (1.15, 0.9, 0.0, 2.1, 'pass')])
    wall_z(p, XS, ZC, ZB - t_ / 2, h, base=(0, 0), tp=(0.0, 0.0), tm=(0.0, 0.0))
    wall_z(p, 0.0, ZF + t_ / 2, xi, h)
    half = Piece()
    wall_z(half, -2.0, ZC, ZB - t_ / 2, h, base=(1, 0))
    wall_z(half, -2.6, ZF + t_ / 2, 2.84, h, [(1.9, 0.76, 0.0, 2.06, 'door')], tp=(0.016, 0.016), tm=(0.016, 0.0))
    wall_x(half, 2.9, -xi, -2.54, h, tp=(0.016, 0.0), tm=(0.016, 0.136))
    p.merge(half); p.merge(half, mirror_x())
    elevator(p, ZB + t_ / 2)
    for x in (-3.5, -0.5, 2.5): deco_light(p, x, h, (ZB + ZF) / 2, 0.16)
    return p
def plan_base(level=0):
    """Paredes internas do saguao (0) e do 1o andar (1): parede dos fundos com portas para a sala de correio / biblioteca e o
    corredor de servico / lavanderia, escada e elevador; nucleo ate a fachada dos fundos."""
    p = Piece(); h = (H0 if level == 0 else H1) - SLAB; xi = LI
    wall_x(p, ZB, -xi, xi, h, [DR(-3.4), DR(SD), DR(3.4), (1.15, 0.9, 0.0, 2.1, 'pass')])
    wall_z(p, -2.0, -xi, ZB - t_ / 2, h, base=(1, 0))
    wall_z(p, XS, -xi, ZB - t_ / 2, h, base=(0, 0))
    wall_z(p, 2.0, -xi, ZB - t_ / 2, h, base=(0, 1))
    if level == 1:
        wall_x(p, ZCW, -1.94, 0.24, h, base=(0, 0)); p.box('ceil', -1.94, 0.24, -SLAB, 0.0, ZCW - t_ / 2, ZCW + t_ / 2)
    elevator(p, ZB + t_ / 2)
    return p

# ============================================================================ moveis dos apartamentos
def toilet():
    p = Piece()
    lathe(p, 'porcelain', [(0.12, 0.0), (0.14, 0.1), (0.13, 0.25), (0.19, 0.38), (0.2, 0.4), (0.0, 0.4)], 0.0, 0.0, 0.0, 16)
    p.hull('porcelain', [(x * 0.19, y, z) for x in (-1, 1) for z in (0.0, 0.3) for y in (0.38, 0.4)] + [(0, 0.38, 0.42), (0, 0.4, 0.42)])
    p.cham('porcelain', -0.2, 0.2, 0.42, 0.44, -0.02, 0.44, 0.02)
    p.cham('porcelain', -0.22, 0.22, 0.42, 0.8, -0.22, -0.04, 0.02); p.cham('porcelain', -0.23, 0.23, 0.8, 0.84, -0.23, -0.03, 0.01)
    p.box('chrome', 0.12, 0.18, 0.72, 0.74, -0.04, -0.01)
    return p
def bath_fix():
    """Banheiro (local: parede do corredor em z = 0, parede lateral em x = 0, banheiro em +X e +Z): banheira com saia de azulejo,
    chuveiro e cortina, vaso, pia de coluna, espelho com prateleira."""
    p = Piece()
    p.cham('porcelain', 0.002, 0.75, 0.0, 0.52, 0.002, 1.6, 0.03)
    p.box('dark', 0.08, 0.67, 0.5, 0.521, 0.08, 1.52)
    seg_cyl(p, 'chrome', (0.375, 1.85, 0.0), (0.375, 1.85, 0.1), 0.012, 6); disc_z(p, 'chrome', 0.06, 0.1, 0.12, 0.375, 1.83, 14)
    for x in (0.25, 0.5): seg_cyl(p, 'chrome', (x, 0.75, 0.0), (x, 0.75, 0.06), 0.014, 8)
    seg_cyl(p, 'chrome', (0.375, 0.62, 0.0), (0.375, 0.6, 0.12), 0.012, 6)
    seg_cyl(p, 'chrome', (0.76, 2.0, 0.002), (0.76, 2.0, 1.6), 0.01, 6)
    for k in range(9): z = 0.05 + k * 0.17; p.box('cloth', 0.755, 0.765, 0.7, 1.98, z, z + 0.15)
    q = toilet(); p.merge(q, rot_y(-90, (1.75 - 0.2, 0.0, 1.7)))
    lathe(p, 'porcelain', [(0.07, 0.0), (0.06, 0.1), (0.05, 0.6), (0.1, 0.74), (0.26, 0.8), (0.27, 0.86), (0.0, 0.86)], 1.25, 0.28, 0.0, 18)
    p.cyl('chrome', 0.014, 0.86, 1.0, 1.25, 0.08, 8); seg_cyl(p, 'chrome', (1.25, 0.99, 0.08), (1.25, 0.99, 0.17), 0.01, 6)
    p.box('chrome', 0.98, 1.52, 1.12, 1.82, 0.0, 0.012); p.box('mirror', 1.0, 1.5, 1.14, 1.8, 0.012, 0.016)
    p.box('porcelain', 0.98, 1.52, 1.06, 1.08, 0.0, 0.12)
    return p
def bed(Lb=2.0, wb=1.4, cov='fabric3'):
    """Cama de casal (pivo: centro da cabeceira, no piso; para +Z): cabeceira deco em degraus, base, colchao, colcha, travesseiros."""
    p = Piece(); x = wb / 2
    p.cham('dkwood', -x - 0.06, x + 0.06, 0.0, 0.95, 0.0, 0.06, 0.01); p.cham('dkwood', -x * 0.6, x * 0.6, 0.95, 1.1, 0.0, 0.06, 0.01)
    p.cham('dkwood', -x * 0.25, x * 0.25, 1.1, 1.18, 0.0, 0.06, 0.01)
    p.box('dkwood', -x, x, 0.08, 0.3, 0.06, Lb); p.cham('linen', -x + 0.02, x - 0.02, 0.3, 0.5, 0.07, Lb - 0.02, 0.04)
    p.cham(cov, -x - 0.01, x + 0.01, 0.4, 0.54, 0.65, Lb, 0.03)
    for s in (-1, 1): p.cham('linen', s * x / 2 - 0.28, s * x / 2 + 0.28, 0.5, 0.64, 0.12, 0.46, 0.06)
    for (sx, sz) in ((-1, 0.1), (1, 0.1), (-1, Lb - 0.05), (1, Lb - 0.05)): p.cyl('dkwood', 0.03, 0.0, 0.08, sx * (x - 0.05), sz, 8)
    return p
def nightstand(w=0.44):
    p = Piece(); p.cham('dkwood', -w / 2, w / 2, 0.05, 0.55, 0.0, 0.38, 0.01); p.box('wood', -w / 2 + 0.03, w / 2 - 0.03, 0.3, 0.5, 0.38, 0.39)
    p.box('gold', -0.04, 0.04, 0.38, 0.41, 0.39, 0.405)
    for sx in (-1, 1): p.box('dkwood', sx * (w / 2 - 0.03) - 0.02, sx * (w / 2 - 0.03) + 0.02, 0.0, 0.05, 0.02, 0.36)
    lathe(p, 'bronze', [(0.07, 0.55), (0.07, 0.57), (0.02, 0.6), (0.02, 0.78)], 0.0, 0.19, 0.0, 10); lathe(p, 'cream', [(0.12, 0.76), (0.08, 0.95)], 0.0, 0.19, 0.0, 14)
    return p
def wardrobe(w=1.0):
    """Guarda-roupa (pivo: canto de tras a esquerda, no piso; frente +Z, vai para +X): 2 portas com friso, puxadores de latao."""
    p = Piece(); p.cham('dkwood', 0.0, w, 0.08, 2.1, 0.0, 0.6, 0.01); p.box('dark', 0.03, w - 0.03, 0.0, 0.08, 0.02, 0.56)
    p.box('dark', w / 2 - 0.002, w / 2 + 0.002, 0.12, 2.06, 0.6, 0.602)
    for (a, b) in ((0.05, w / 2 - 0.03), (w / 2 + 0.03, w - 0.05)): ext(p, 'wood', sbox(a, 0.2, b, 1.96).difference(sbox(a + 0.04, 0.24, b - 0.04, 1.92)), 0.6, 0.61)
    for x in (w / 2 - 0.06, w / 2 + 0.06): p.box('gold', x - 0.008, x + 0.008, 0.95, 1.25, 0.61, 0.63)
    return p
def sofa(L1=2.0, mat='fabric'):
    """Sofa deco de bracos arredondados (pivo: centro de tras, no piso; frente +Z)."""
    p = Piece(); x = L1 / 2
    p.cham(mat, -x + 0.12, x - 0.12, 0.12, 0.42, 0.0, 0.85, 0.04); p.cham(mat, -x + 0.12, x - 0.12, 0.42, 0.86, 0.0, 0.2, 0.05)
    for s in (-1, 1):
        xc = s * (x - 0.12)
        p.cham(mat, *sorted((xc, xc + s * 0.14)), 0.12, 0.62, 0.0, 0.85, 0.05)
        seg_cyl(p, mat, (xc + s * 0.07, 0.62, 0.02), (xc + s * 0.07, 0.62, 0.84), 0.075, 12)
    n = max(1, int(L1 / 0.7))
    for k in range(n):
        a = -x + 0.12 + k * (L1 - 0.24) / n + 0.01; b = -x + 0.12 + (k + 1) * (L1 - 0.24) / n - 0.01; p.cham(mat, a, b, 0.42, 0.55, 0.2, 0.82, 0.04)
    for (sx, sz) in ((-1, 0.05), (1, 0.05), (-1, 0.8), (1, 0.8)): lathe(p, 'dkwood', [(0.03, 0.0), (0.04, 0.12)], sx * (x - 0.08), sz, 0.0, 8)
    return p
def armchair(mat='fabric2'):
    p = Piece(); p.cham(mat, -0.32, 0.32, 0.12, 0.42, 0.0, 0.75, 0.04); p.cham(mat, -0.32, 0.32, 0.42, 0.95, 0.0, 0.18, 0.05)
    for s in (-1, 1): p.cham(mat, *sorted((s * 0.32, s * 0.42)), 0.12, 0.62, 0.0, 0.75, 0.04); seg_cyl(p, mat, (s * 0.37, 0.62, 0.02), (s * 0.37, 0.62, 0.74), 0.05, 10)
    p.cham(mat, -0.31, 0.31, 0.42, 0.54, 0.18, 0.73, 0.04)
    for (sx, sz) in ((-1, 0.05), (1, 0.05), (-1, 0.7), (1, 0.7)): lathe(p, 'dkwood', [(0.03, 0.0), (0.04, 0.12)], sx * 0.37, sz, 0.0, 8)
    return p
def coffee_table(w=1.0, d=0.55):
    p = Piece(); p.cham('dkwood', -w / 2, w / 2, 0.36, 0.42, -d / 2, d / 2, 0.012); p.box('mirror', -w / 2 + 0.05, w / 2 - 0.05, 0.42, 0.424, -d / 2 + 0.05, d / 2 - 0.05)
    for s in (-1, 1): p.cham('dkwood', *sorted((s * w / 2 * 0.7, s * (w / 2 * 0.7 - 0.06))), 0.0, 0.36, -d / 2 + 0.06, d / 2 - 0.06, 0.008)
    return p
def floor_lamp():
    p = Piece(); p.cyl('bronze', 0.15, 0.0, 0.03, 0, 0, 16); p.cyl('bronze', 0.014, 0.03, 1.55, 0, 0, 8)
    lathe(p, 'cream', [(0.12, 1.45), (0.24, 1.7), (0.22, 1.72), (0.1, 1.5)], 0.0, 0.0, 0.0, 18); return p
def radio():
    """Radio-vitrola de pe (pivo: centro de tras, no piso; frente +Z): caixa de madeira com topo arredondado, tela com frisos
    verticais, mostrador redondo sem numeros e 3 botoes."""
    p = Piece(); w = 0.62
    p.cham('dkwood', -w / 2, w / 2, 0.06, 0.9, 0.0, 0.36, 0.015)
    pts = [(w / 2 * math.cos(t), 0.9 + 0.12 * math.sin(t)) for t in np.linspace(0, math.pi, 13)]
    q = Piece(); prof_z(q, 'dkwood', 0.0, 0.36, pts); p.merge(q)
    p.box('cloth', -0.22, 0.22, 0.12, 0.6, 0.36, 0.365)
    for x in np.linspace(-0.18, 0.18, 7): p.box('wood', x - 0.012, x + 0.012, 0.12, 0.6, 0.365, 0.38)
    disc_z(p, 'cream', 0.08, 0.36, 0.37, 0.0, 0.76, 24); disc_z(p, 'bronze', 0.09, 0.355, 0.365, 0.0, 0.76, 24); p.seg('dark', (0, 0.76, 0.372), (0.05, 0.8, 0.372), 0.006, 0.004)
    for x in (-0.18, 0.0, 0.18): disc_z(p, 'bronze', 0.025, 0.36, 0.39, x, 0.66 if x else 0.66, 12) if x else None
    for x in (-0.18, 0.18): disc_z(p, 'bronze', 0.025, 0.36, 0.39, x, 0.76, 12)
    for sx in (-1, 1): p.box('dkwood', sx * (w / 2 - 0.05) - 0.03, sx * (w / 2 - 0.05) + 0.03, 0.0, 0.06, 0.03, 0.33)
    return p
def kitchen(L1=2.4, fridge=True):
    """Cozinha linear (pivo: inicio, na parede; frente +Z, vai para +X): armarios baixos, tampo, pia com torneira, fogao de 4 bocas
    com forno, armarios altos, coifa, geladeira de cantos arredondados no fim e azulejo entre os armarios."""
    p = Piece(); d = 0.6
    p.box('dark', 0.0, L1, 0.0, 0.1, 0.0, d - 0.06); p.box('cream', 0.0, L1, 0.1, 0.86, 0.0, d - 0.02)
    n = int(round(L1 / 0.6))
    for k in range(n):
        a = k * L1 / n + 0.008; b = (k + 1) * L1 / n - 0.008
        if k == 1:
            p.box('appliance', a, b, 0.1, 0.86, d - 0.02, d); p.box('dark', a + 0.06, b - 0.06, 0.25, 0.6, d, d + 0.005)
            seg_cyl(p, 'chrome', (a + 0.06, 0.68, d + 0.04), (b - 0.06, 0.68, d + 0.04), 0.01, 6)
            for x in (a + 0.12, b - 0.12):
                for z in (0.15, 0.4): p.cyl('dark', 0.09, 0.95, 0.96, x, z, 14)
            for x in np.linspace(a + 0.08, b - 0.08, 4): disc_z(p, 'cream', 0.018, d, d + 0.03, x, 0.78, 10)
            continue
        p.box('cream', a, b, 0.12, 0.84, d - 0.02, d); p.box('chrome', (a + b) / 2 - 0.05, (a + b) / 2 + 0.05, 0.75, 0.77, d, d + 0.02)
    p.cham('tile_k', -0.0, L1, 0.86, 0.9, 0.0, d + 0.02, 0.006)
    a, b = 1 * L1 / n, 2 * L1 / n
    p.box('steel', a + 0.02, b - 0.02, 0.9, 0.95, 0.012, d - 0.02)
    xs = 0.3 if n > 1 else 0.3
    for (x0, x1) in ((xs - 0.22, xs + 0.22),): p.box('chrome', x0, x1, 0.895, 0.902, 0.1, 0.5); p.box('dark', x0 + 0.02, x1 - 0.02, 0.9, 0.904, 0.12, 0.48)
    p.cyl('chrome', 0.015, 0.9, 1.15, xs, 0.06, 8); seg_cyl(p, 'chrome', (xs, 1.13, 0.06), (xs, 1.13, 0.25), 0.012, 6)
    p.box('tile_k', 0.0, L1, 0.9, 1.45, 0.0, 0.01)
    for k in range(n):
        a = k * L1 / n + 0.008; b = (k + 1) * L1 / n - 0.008
        if k == 1: p.hull('steel', [(x, y, z) for x in (a + 0.02, b - 0.02) for (y, z) in ((1.5, 0.0), (1.5, 0.5), (1.62, 0.0), (1.62, 0.4))]); continue
        p.box('cream', a, b, 1.45, 2.15, 0.0, 0.33); p.box('cream', a + 0.02, b - 0.02, 1.47, 2.13, 0.33, 0.345); p.box('chrome', (a + b) / 2 - 0.04, (a + b) / 2 + 0.04, 1.5, 1.52, 0.345, 0.36)
    if fridge:
        x0 = L1 + 0.03; p.cham('appliance', x0, x0 + 0.7, 0.0, 1.7, 0.0, 0.66, 0.06)
        p.box('dark', x0 + 0.04, x0 + 0.66, 1.14, 1.16, 0.65, 0.665)
        p.box('chrome', x0 + 0.58, x0 + 0.62, 1.2, 1.45, 0.665, 0.7); p.box('chrome', x0 + 0.58, x0 + 0.62, 0.8, 1.05, 0.665, 0.7)
    return p
def table_set(n=4, r=0.45, top='dkwood', chair='fabric3'):
    """Mesa redonda de pe central com n cadeiras de encosto alto voltadas para o centro (pivo: centro, no piso)."""
    p = Piece()
    lathe(p, 'dkwood', [(0.26, 0.0), (0.26, 0.03), (0.08, 0.08), (0.06, 0.7)], sec=14); p.cyl(top, r, 0.71, 0.75, 0, 0, 28)
    for k in range(n):
        a = 2 * math.pi * k / n; d = r + 0.3; q = Piece()
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): q.box('dkwood', sx * 0.18 - 0.018, sx * 0.18 + 0.018, 0.0, 0.45, sz * 0.18 - 0.018, sz * 0.18 + 0.018)
        q.cham(chair, -0.21, 0.21, 0.45, 0.52, -0.21, 0.21, 0.015); q.cham('dkwood', -0.2, 0.2, 0.52, 1.0, 0.17, 0.21, 0.012)
        q.cham(chair, -0.16, 0.16, 0.6, 0.95, 0.165, 0.17, 0.006)
        p.merge(q, rot_y(90 - math.degrees(a), (d * math.cos(a), 0, d * math.sin(a))))
    return p
def rug(x0, x1, z0, z1, mat='rug', p=None):
    p = p or Piece(); p.box(mat, x0, x1, 0.0, 0.008, z0, z1); p.box('cream', x0 + 0.08, x1 - 0.08, 0.008, 0.01, z0 + 0.08, z0 + 0.12); p.box('cream', x0 + 0.08, x1 - 0.08, 0.008, 0.01, z1 - 0.12, z1 - 0.08)
    return p
def ceil_lamp(p, x, z, h=CEIL):
    p.cyl('bronze', 0.2, h - 0.03, h, x, z, 20); lathe(p, 'lamp_glass', [(0.18, h - 0.03), (0.15, h - 0.1), (0.0, h - 0.12)], x, z, 0.0, 20)
    p.cyl('bronze', 0.025, h - 0.135, h - 0.115, x, z, 10)
def desk():
    p = Piece(); p.cham('dkwood', -0.55, 0.55, 0.72, 0.76, 0.0, 0.55, 0.008)
    for s in (-1, 1): p.box('dkwood', *sorted((s * 0.55, s * 0.5)), 0.0, 0.72, 0.02, 0.53)
    p.box('dkwood', 0.05, 0.5, 0.45, 0.72, 0.02, 0.53); p.box('gold', 0.24, 0.31, 0.6, 0.615, 0.53, 0.545)
    lathe(p, 'bronze', [(0.08, 0.76), (0.08, 0.78), (0.015, 0.8), (0.015, 1.15)], -0.35, 0.15, 0.0, 10); lathe(p, 'felt', [(0.05, 1.08), (0.14, 1.2), (0.13, 1.21), (0.04, 1.1)], -0.35, 0.22, 0.0, 14)
    q = Piece(); q.cham('fabric3', -0.21, 0.21, 0.45, 0.52, -0.21, 0.21, 0.015); q.cham('dkwood', -0.2, 0.2, 0.52, 0.95, 0.17, 0.21, 0.012)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): q.box('dkwood', sx * 0.18 - 0.018, sx * 0.18 + 0.018, 0.0, 0.45, sz * 0.18 - 0.018, sz * 0.18 + 0.018)
    p.merge(q, rot_y(180, (0.0, 0, 0.85)))
    return p
def apt_front():
    """Moveis do apartamento de frente (esquerda; o da direita e o espelho): banheiro, quarto (cama, criados, tapete), sala com
    cozinha linear e geladeira, mesa de jantar, sofa, mesa de centro, poltrona, radio-vitrola, guarda-roupa e luminarias."""
    p = Piece()
    p.merge(bath_fix(), tr(-0.06, 0, ZF + t_ / 2) @ mirror_x())
    p.merge(bed(), tr(-5.3, 0, ZF + t_ / 2))
    for x in (-6.3, -4.3): p.merge(nightstand(0.42), tr(x, 0, ZF + t_ / 2 + 0.02))
    rug(-6.1, -4.5, 2.0, 2.85, 'rug2', p)
    p.merge(kitchen(2.4), rot_y(-90, (-0.06, 0, 3.4)))
    p.merge(table_set(4, 0.45), tr(-1.95, 0, 4.7))
    p.merge(sofa(2.0), rot_y(90, (-LI + 0.02, 0, 4.95)))
    p.merge(coffee_table(), rot_y(90, (-5.35, 0, 4.95))); rug(-6.0, -3.8, 3.8, 6.1, 'rug', p)
    p.merge(armchair(), rot_y(-90, (-3.9, 0, 4.95)))
    p.merge(radio(), tr(-1.2, 0, 3.062))
    p.merge(wardrobe(1.0), tr(-6.5, 0, 3.062))
    p.merge(floor_lamp(), tr(-6.35, 0, 6.35))
    for (x, z) in ((-5.2, 1.9), (-3.0, 4.8), (-3.0, 2.0)): ceil_lamp(p, x, z)
    return p
def apt_back():
    """Moveis do apartamento de fundos (esquerda): banheiro, sala com cozinha no nucleo, mesa, sofa, poltrona e radio; quarto ao
    longo da fachada dos fundos com cama, criado, escrivaninha e guarda-roupa no nicho atras do nucleo."""
    p = Piece()
    p.merge(bath_fix(), tr(-LI, 0, ZB - t_ / 2) @ mirror_z())
    p.merge(kitchen(1.6), rot_y(-90, (-2.06, 0, -4.62)))
    p.merge(table_set(2, 0.38), rot_y(90, (-4.2, 0, -2.25)))
    p.merge(sofa(1.6), rot_y(90, (-LI + 0.02, 0, -3.8)))
    p.merge(coffee_table(0.8, 0.5), rot_y(90, (-5.55, 0, -3.8))); rug(-6.2, -4.7, -4.6, -3.0, 'rug2', p)
    p.merge(armchair(), rot_y(-90, (-4.6, 0, -3.8)))
    p.merge(bed(), rot_y(90, (-LI + 0.02, 0, -5.94)))
    p.merge(nightstand(0.32), rot_y(90, (-LI + 0.02, 0, -5.05)))
    p.merge(desk(), tr(-3.85, 0, -LI + 0.01))
    p.merge(wardrobe(1.0), rot_y(-90, (-0.06, 0, -6.62)))
    for (x, z) in ((-5.5, -5.76), (-1.2, -5.76), (-4.0, -2.2), (-5.6, -1.8)): ceil_lamp(p, x, z)
    return p
def studio():
    """Moveis do estudio (esquerda, andares altos): banheiro, cama de casal, cozinha no muro de divisa, mesinha com 2 cadeiras,
    sofa de 2 lugares, abajur de pe e luminarias."""
    p = Piece()
    p.merge(bath_fix(), tr(-UI, 0, ZF + t_ / 2))
    p.merge(bed(), rot_y(90, (-UI + 0.02, 0, 3.95)))
    p.merge(kitchen(1.8), rot_y(-90, (-0.06, 0, 2.0)))
    p.merge(table_set(2, 0.36), rot_y(90, (-1.9, 0, 3.4)))
    p.merge(sofa(1.3), rot_y(90, (-2.5, 0, 1.75)))
    p.merge(floor_lamp(), tr(-2.3, 0, 3.12))
    for (x, z) in ((-3.5, 3.9), (-1.4, 2.4)): ceil_lamp(p, x, z)
    return p
def washer(dryer=False):
    p = Piece(); p.cham('appliance', -0.3, 0.3, 0.0, 0.9, 0.0, 0.62, 0.02)
    disc_z(p, 'chrome', 0.21, 0.62, 0.64, 0.0, 0.45, 28); disc_z(p, 'glass' if not dryer else 'dark', 0.17, 0.64, 0.645, 0.0, 0.45, 28)
    p.box('chrome', -0.28, 0.28, 0.78, 0.88, 0.6, 0.63)
    for x in (-0.15, 0.0, 0.15): disc_z(p, 'dark', 0.025, 0.62, 0.635, x, 0.83, 12)
    return p
def laundry():
    """Lavanderia (fundos a esquerda, andares altos): 2 lavadoras e 2 secadoras, mesa de dobrar, tanque, cesto e varal de teto."""
    p = Piece()
    for k, z in enumerate((-4.3, -3.65, -3.0, -2.35)): p.merge(washer(k >= 2), rot_y(-90, (-2.06, 0, z)))
    p.cham('wood', -4.6, -3.2, 0.75, 0.8, -UI + 0.02, -4.0, 0.01)
    for (x, z) in ((-4.55, -4.65), (-3.25, -4.65), (-4.55, -4.05), (-3.25, -4.05)): p.box('steel', x - 0.02, x + 0.02, 0.0, 0.75, z - 0.02, z + 0.02)
    p.cham('porcelain', -4.62, -4.0, 0.6, 0.92, -1.36, -0.8, 0.02)
    for (x, z) in ((-4.58, -1.32), (-4.04, -1.32), (-4.58, -0.84), (-4.04, -0.84)): p.box('steel', x - 0.02, x + 0.02, 0.0, 0.6, z - 0.02, z + 0.02)
    p.cyl('chrome', 0.014, 0.92, 1.15, -4.31, -0.84, 8)
    lathe(p, 'cloth', [(0.2, 0.0), (0.23, 0.45), (0.21, 0.45), (0.18, 0.02)], -3.6, -3.5, 0.0, 16)
    for z in (-1.8, -2.4, -3.0): seg_cyl(p, 'chrome', (-4.5, CEIL - 0.3, z), (-2.7, CEIL - 0.3, z), 0.01, 6)
    for x in (-4.5, -2.7): seg_cyl(p, 'chrome', (x, CEIL - 0.3, -3.0), (x, CEIL, -3.0), 0.008, 5)
    for (x, z) in ((-3.6, -2.4),): ceil_lamp(p, x, z)
    return p
def storage():
    """Deposito (fundos a direita, andares altos): estantes de aco com caixas, cadeiras empilhadas, bicicleta e escada."""
    p = Piece()
    for (z0, z1) in ((-4.62, -4.2),):
        for x0 in (2.2, 3.3):
            x1 = x0 + 1.0
            for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)): p.box('steel', x - 0.02, x + 0.02, 0.0, 2.0, z - 0.02, z + 0.02)
            for y in (0.1, 0.6, 1.1, 1.6, 1.98): p.box('steel', x0, x1, y, y + 0.02, z0, z1)
            rng = np.random.default_rng(int(x0 * 10))
            for y in (0.12, 0.62, 1.12, 1.62):
                x = x0 + 0.04
                while x < x1 - 0.25:
                    w_ = rng.uniform(0.2, 0.34); h_ = rng.uniform(0.18, 0.38); p.cham('box_c', x, x + w_, y, y + h_, z0 + 0.03, z1 - 0.03, 0.006); x += w_ + 0.03
    for k in range(4):
        q = Piece(); y = k * 0.06
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): q.box('steel', sx * 0.2 - 0.012, sx * 0.2 + 0.012, y, 0.45 + y, sz * 0.2 - 0.012, sz * 0.2 + 0.012)
        q.box('wood', -0.22, 0.22, 0.45 + y, 0.48 + y, -0.22, 0.22); q.box('wood', -0.22, 0.22, 0.48 + y, 0.85 + y, 0.18, 0.22); p.merge(q, tr(4.2, 0, -1.4))
    q = Piece()
    for s in (-1, 1): ring_y(q, 'dark', 0.3, 0.33, -0.02, 0.02, 0.0, 0.0, 28)
    rr = Piece(); ring_y(rr, 'dark', 0.29, 0.33, -0.02, 0.02, 0, 0, 28); rr2 = Piece(); rr2.merge(rr, trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]))
    bike = Piece(); bike.merge(rr2, tr(-0.5, 0.33, 0.0)); bike.merge(rr2, tr(0.5, 0.33, 0.0))
    for (a, b) in (((-0.5, 0.33), (0.0, 0.75)), ((0.0, 0.75), (0.5, 0.33)), ((-0.5, 0.33), (0.05, 0.33)), ((0.05, 0.33), (0.0, 0.75)), ((0.05, 0.33), (0.45, 0.8))):
        seg_cyl(bike, 'red', (a[0], a[1], 0.0), (b[0], b[1], 0.0), 0.016, 6)
    bike.cham('dark', -0.12, 0.08, 0.78, 0.82, -0.06, 0.06, 0.01); seg_cyl(bike, 'chrome', (0.45, 0.8, -0.25), (0.45, 0.8, 0.25), 0.012, 6)
    p.merge(bike, rot_y(90, (UI - 0.25, 0, -2.6)))
    for (x, z) in ((3.4, -2.6),): ceil_lamp(p, x, z)
    return p

# ============================================================================ saguao, 1o andar
def chandelier(h, n=3):
    """Lustre deco de 3 aneis escalonados de vidro fosco com aros de bronze (pivo: forro em y = h)."""
    p = Piece(); p.cyl('bronze', 0.12, h - 0.04, h, 0, 0, 16); p.cyl('bronze', 0.015, h - 0.7, h - 0.04, 0, 0, 8)
    for k in range(n):
        r = 0.55 - k * 0.15; y = h - 0.7 - k * 0.22
        lathe(p, 'lamp_glass', [(r - 0.08, y - 0.18), (r, y - 0.02), (r, y), (r - 0.08, y), (r - 0.12, y - 0.16)], 0, 0, 0.0, 28)
        ring_y(p, 'bronze', r - 0.005, r + 0.01, y - 0.005, y + 0.01, 0, 0, 28)
        for a in np.linspace(0, 2 * math.pi, 4, endpoint=False): seg_cyl(p, 'bronze', (0, h - 0.7, 0), (r * math.cos(a), y, r * math.sin(a)), 0.006, 4)
    p.sphere('lamp_glass', 0.09, 0, h - 0.7 - n * 0.22 - 0.05, 0, 1)
    return p
def reception():
    """Recepcao curva (pivo: centro do arco, no piso; frente para +Z): frente de madeira com frisos de bronze verticais, tampo
    de marmore escuro, faixa de bronze, painel de chaves, sineta e luminaria de mesa."""
    p = Piece(); R0, R1 = 1.2, 1.75; a0, a1 = math.radians(20), math.radians(160)
    ts = np.linspace(a0, a1, 15)
    for t0, t1 in zip(ts[:-1], ts[1:]):
        pts = [(r * math.cos(t), y, r * math.sin(t)) for r in (R0, R1) for t in (t0, t1) for y in (0.06, 1.05)]
        p.hull('dkwood', pts); p.hull('dark', [(r * math.cos(t), y, r * math.sin(t)) for r in (R0 + 0.04, R1 - 0.04) for t in (t0, t1) for y in (0.0, 0.06)])
        p.hull('marble_d', [(r * math.cos(t), y, r * math.sin(t)) for r in (R0 - 0.04, R1 + 0.05) for t in (t0, t1) for y in (1.05, 1.1)])
        p.hull('bronze', [(r * math.cos(t), y, r * math.sin(t)) for r in (R1, R1 + 0.012) for t in (t0, t1) for y in (0.9, 0.95)])
    for t in ts[1:-1:2]: p.hull('bronze', [((R1 + dr) * math.cos(t + da), y, (R1 + dr) * math.sin(t + da)) for dr in (0.0, 0.012) for da in (-0.012, 0.012) for y in (0.12, 0.85)])
    for t in (a0, a1):
        p.hull('dkwood', [(r * math.cos(t), y, r * math.sin(t)) for r in (R0, R1) for y in (0.06, 1.05)] + [(r * math.cos(t) + 0.04 * math.sin(t) * (1 if t < 1.5 else -1), y, r * math.sin(t) - 0.04 * math.cos(t) * (1 if t < 1.5 else -1)) for r in (R0, R1) for y in (0.06, 1.05)])
    lathe(p, 'gold', [(0.05, 1.1), (0.05, 1.12), (0.04, 1.16), (0.0, 1.17)], 0.2, 1.45, 0.0, 12)
    lathe(p, 'bronze', [(0.08, 1.1), (0.08, 1.12), (0.015, 1.15), (0.015, 1.45)], -0.7, 1.4, 0.0, 10); lathe(p, 'felt', [(0.05, 1.38), (0.15, 1.5), (0.14, 1.51), (0.04, 1.4)], -0.7, 1.48, 0.0, 14)
    p.cham('dkwood', -0.9, 0.9, 0.0, 0.72, -0.6, -0.1, 0.01); p.cham('marble_d', -0.92, 0.92, 0.72, 0.76, -0.62, -0.08, 0.006)
    return p
def mailboxes(w=2.2):
    """Caixas de correio de latao (pivo: inicio, na face da parede; frente +Z, vai para +X): moldura, portinholas com visor e
    fenda, sem numeros; escaninho de encomendas embaixo."""
    p = Piece(); y0, y1 = 0.45, 1.85; nc = int(w / 0.3); nr = 5
    p.cham('bronze', 0.0, w, y0 - 0.05, y1 + 0.05, 0.0, 0.18, 0.008)
    for i in range(nc):
        for j in range(nr):
            a = 0.04 + i * (w - 0.08) / nc + 0.006; b = 0.04 + (i + 1) * (w - 0.08) / nc - 0.006
            c = y0 + j * (y1 - y0) / nr + 0.006; d = y0 + (j + 1) * (y1 - y0) / nr - 0.006
            p.box('gold', a, b, c, d, 0.18, 0.19); p.box('dark', a + 0.03, b - 0.03, d - 0.06, d - 0.045, 0.19, 0.193)
            p.box('glass', a + 0.06, b - 0.06, c + 0.05, c + 0.12, 0.19, 0.192)
    p.cham('dkwood', 0.0, w, 0.0, 0.4, 0.0, 0.4, 0.01)
    for k in range(3): a = 0.05 + k * (w - 0.1) / 3; p.box('wood', a + 0.01, a + (w - 0.1) / 3 - 0.01, 0.05, 0.36, 0.4, 0.41)
    return p
def wainscot_back(p, zf, h=0.9, cuts=()):
    """Lambri de marmore na face (zf, para +Z) de uma parede, de -LI a LI, parando nos vaos."""
    for (a, b) in segs_excl(cuts, -LI + 0.03, LI - 0.03):
        if b - a < 0.02: continue
        p.box('marble', a, b, 0.0, h, zf, zf + 0.02); p.box('marble_d', a, b, h, h + 0.05, zf, zf + 0.03)
        p.box('marble_d', a + 0.001, b - 0.001, 0.0, 0.14, zf + 0.019, zf + 0.035)
def planter(h=2.0, r=0.36):
    p = Piece(); lathe(p, 'bronze', [(r * 0.8, 0.0), (r, 0.05), (r, 0.12), (r * 0.9, 0.16), (r * 1.02, 0.62), (r * 1.06, 0.66), (0.0, 0.66)], sec=20)
    p.cyl('mulch', r * 0.98, 0.66, 0.67, 0, 0, 20); lathe(p, 'bark', [(0.035, 0.66), (0.025, h - 0.6)], sec=8)
    for (dx, dy, dz, rr) in ((0, h - 0.4, 0, 0.42), (0.22, h - 0.62, 0.1, 0.28), (-0.2, h - 0.6, -0.08, 0.26)): p.sphere('plant', rr, dx, dy, dz, 2)
    return p
def palm_pot():
    p = Piece(); lathe(p, 'cream', [(0.18, 0.0), (0.26, 0.5), (0.28, 0.52), (0.0, 0.52)], sec=18); p.cyl('mulch', 0.25, 0.5, 0.51, 0, 0, 18)
    for k in range(9):
        a = 2 * math.pi * k / 9; L = 0.7 + 0.15 * (k % 3)
        tip = (L * math.cos(a), 0.5 + 0.6 + 0.2 * (k % 2), L * math.sin(a))
        p.hull('plant', [(0, 0.55, 0), (0, 0.6, 0), (tip[0] * 0.5 - 0.08 * math.sin(a), 1.25, tip[2] * 0.5 + 0.08 * math.cos(a)), (tip[0] * 0.5 + 0.08 * math.sin(a), 1.25, tip[2] * 0.5 - 0.08 * math.cos(a)), tip])
    return p
def lobby_set():
    """Moveis do saguao (pivo: origem, cota do piso): recepcao, caixas de correio, lambri de marmore na parede dos fundos, 2 sofas,
    2 poltronas, mesa de centro, tapete, lustres, vasos com plantas e relogio de parede sem numeros."""
    p = Piece(); zf = ZB + t_ / 2
    wainscot_back(p, zf, 0.9, [(-3.4 - 0.55, -3.4 + 0.55), (SD - 0.55, SD + 0.55), (3.4 - 0.55, 3.4 + 0.55), (0.6, 1.7), (1.78, 1.92)])
    p.merge(mailboxes(2.3), tr(-6.45, 0, zf + 0.035))
    p.merge(reception(), tr(-4.4, 0, 1.0))
    p.merge(sofa(2.2, 'leather'), tr(4.3, 0, 1.4)); p.merge(sofa(2.2, 'leather'), rot_y(180, (4.3, 0, 5.0)))
    for s in (-1, 1): p.merge(armchair('fabric'), rot_y(-90 * s, (4.3 + s * 1.75, 0, 3.2)))
    p.merge(coffee_table(1.2, 0.6), tr(4.3, 0, 3.2)); rug(2.6, 6.0, 1.3, 5.1, 'rug', p)
    for (x, z) in ((-2.3, 6.25), (2.3, 6.25), (6.25, 6.25), (-6.25, 6.25)): p.merge(planter(2.1), tr(x, 0, z))
    p.merge(wall_clock(0.45), tr(-1.4, 3.15, zf + 0.002))
    return p
def billiard():
    """Mesa de sinuca (pivo: centro, no piso): pes torneados, caixa com friso, pano verde, tabelas, cacapas, bolas e 2 tacos."""
    p = Piece(); x, z = 1.3, 0.72
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1)):
        lathe(p, 'dkwood', [(0.08, 0.0), (0.1, 0.06), (0.07, 0.2), (0.09, 0.4), (0.06, 0.62)], sx * (x - 0.15), sz * (z - 0.15), 0.0, 10)
    p.cham('dkwood', -x, x, 0.6, 0.8, -z, z, 0.02); p.box('gold', -x - 0.002, x + 0.002, 0.66, 0.68, -z - 0.002, z + 0.002)
    p.box('felt', -x + 0.12, x - 0.12, 0.8, 0.82, -z + 0.12, z - 0.12)
    for (a, b, c, d) in ((-x, x, -z, -z + 0.12), (-x, x, z - 0.12, z), (-x, -x + 0.12, -z + 0.12, z - 0.12), (x - 0.12, x, -z + 0.12, z - 0.12)): p.cham('dkwood', a, b, 0.8, 0.86, c, d, 0.008)
    for (a, b, c, d) in ((-x + 0.12, x - 0.12, -z + 0.12, -z + 0.16), (-x + 0.12, x - 0.12, z - 0.16, z - 0.12), (-x + 0.12, -x + 0.16, -z + 0.16, z - 0.16), (x - 0.16, x - 0.12, -z + 0.16, z - 0.16)): p.box('felt', a, b, 0.82, 0.85, c, d)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1)): p.cyl('dark', 0.06, 0.82, 0.865, sx * (x - 0.1), sz * (z - 0.1), 12)
    cols = ['cream', 'red', 'book_b', 'paint_y', 'dark', 'felt', 'fabric2']
    for k, (bx, bz) in enumerate(((0.5, 0.0), (0.56, -0.04), (0.56, 0.04), (0.62, -0.08), (0.62, 0.0), (0.62, 0.08), (-0.6, 0.0))): p.sphere(cols[k % len(cols)], 0.028, bx, 0.848, bz, 1)
    for s in (-1, 1): seg_cyl(p, 'wood', (-0.9, 0.86, s * 0.3), (0.3, 0.88, s * 0.32), 0.012, 6)
    return p
def bookcase(w=1.6, h=2.2, d=0.35):
    """Estante (pivo: canto de tras a esquerda, no piso; frente +Z, vai para +X) com livros de lombadas lisas."""
    p = Piece(); p.box('dkwood', 0.0, w, 0.0, h, 0.0, 0.02)
    for x in (0.0, w - 0.03): p.box('dkwood', x, x + 0.03, 0.0, h, 0.02, d)
    shelves = np.linspace(0.08, h - 0.03, 6); rng = np.random.default_rng(int(w * 100))
    for y in shelves: p.box('dkwood', 0.03, w - 0.03, y, y + 0.03, 0.02, d)
    p.box('dark', 0.03, w - 0.03, 0.0, 0.08, 0.04, d - 0.02); p.cham('dkwood', -0.02, w + 0.02, h, h + 0.05, 0.0, d + 0.03, 0.006)
    mats = ['book_a', 'book_b', 'book_c', 'book_d', 'leather', 'cream']
    for y0, y1 in zip(shelves[:-1], shelves[1:]):
        x = 0.05
        while x < w - 0.1:
            t = rng.uniform(0.025, 0.05); hh = rng.uniform(0.6, 0.92) * (y1 - y0 - 0.03)
            if rng.random() < 0.06: x += 0.08; continue
            p.box(mats[rng.integers(len(mats))], x, x + t, y0 + 0.03, y0 + 0.03 + hh, 0.06, d - rng.uniform(0.02, 0.06)); x += t + 0.003
    return p
def piano():
    p = Piece(); w = 1.5
    p.cham('dark', -w / 2, w / 2, 0.0, 1.25, 0.0, 0.32, 0.01); p.cham('dark', -w / 2, w / 2, 0.62, 0.78, 0.32, 0.62, 0.008)
    p.box('cream', -w / 2 + 0.06, w / 2 - 0.06, 0.74, 0.76, 0.42, 0.6)
    for x in np.arange(-w / 2 + 0.08, w / 2 - 0.08, 0.035):
        if int((x + 1) / 0.035) % 7 not in (2, 6): p.box('dark', x - 0.007, x + 0.007, 0.76, 0.78, 0.42, 0.52)
    for s in (-1, 1): p.box('dark', s * (w / 2 - 0.05) - 0.04, s * (w / 2 - 0.05) + 0.04, 0.0, 0.62, 0.5, 0.6)
    p.cham('dark', -0.45, 0.45, 0.0, 0.5, 0.9, 1.25, 0.01); p.box('gold', -0.6, 0.6, 1.0, 1.02, 0.32, 0.33)
    return p
def club_set():
    """Salao social do 1o andar (pivo: origem, cota do piso): sinuca, piano, estantes na parede dos fundos, sofa e poltronas com
    mesa de centro, mesa de jogos com 4 cadeiras, carrinho de bar, tapetes, vasos e lambri de madeira."""
    p = Piece(); zf = ZB + t_ / 2
    p.merge(bookcase(1.3), tr(-6.6, 0, zf + 0.002)); p.merge(bookcase(1.3), tr(4.1, 0, zf + 0.002)); p.merge(bookcase(1.1), tr(5.5, 0, zf + 0.002))
    p.merge(billiard(), tr(-3.6, 0, 3.3)); rug(-5.4, -1.8, 2.0, 4.6, 'rug2', p)
    p.merge(sofa(2.2, 'leather'), rot_y(180, (3.6, 0, 6.1)))
    for s in (-1, 1): p.merge(armchair('leather'), rot_y(-90 * s, (3.6 + s * 1.6, 0, 4.7)))
    p.merge(coffee_table(1.1, 0.6), tr(3.6, 0, 4.7)); rug(2.0, 5.2, 3.6, 6.4, 'rug', p)
    p.merge(table_set(4, 0.48, 'felt', 'leather'), tr(3.4, 0, 1.6))
    q = Piece(); q.box('bronze', -0.35, 0.35, 0.3, 0.32, -0.22, 0.22); q.box('bronze', -0.35, 0.35, 0.8, 0.82, -0.22, 0.22)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): q.cyl('bronze', 0.012, 0.06, 0.95, sx * 0.34, sz * 0.21, 6)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): seg_cyl(q, 'dark', (sx * 0.34, 0.05, sz * 0.21 - 0.015), (sx * 0.34, 0.05, sz * 0.21 + 0.015), 0.05, 10)
    for k, x in enumerate((-0.25, -0.12, 0.0, 0.14, 0.26)): lathe(q, 'mirror' if k % 2 else 'book_c', [(0.035, 0.82), (0.035, 1.02), (0.012, 1.08), (0.012, 1.12)], x, 0.05 * (k % 2), 0.0, 8)
    p.merge(q, tr(6.2, 0, 3.0))
    for (x, z) in ((-6.25, 6.25), (6.25, 6.25), (0.0, 6.25)): p.merge(palm_pot(), tr(x, 0, z))
    return p
def library():
    """Biblioteca (fundos a esquerda do 1o andar): estantes nas paredes, poltronas de leitura com abajur e mesa de estudo."""
    p = Piece()
    p.merge(bookcase(1.5), rot_y(-90, (-2.062, 0, -6.6)))
    p.merge(bookcase(1.5), rot_y(-90, (-2.062, 0, -4.95)))
    p.merge(bookcase(1.2), rot_y(180, (-3.3, 0, -0.762)))
    for (x, z, r) in ((-5.6, -1.6, 180), (-4.4, -1.6, 180)): p.merge(armchair('leather'), rot_y(r, (x, 0, z)))
    p.merge(floor_lamp(), tr(-5.0, 0, -1.2)); rug(-6.3, -3.7, -3.4, -1.0, 'rug', p)
    p.cham('dkwood', -5.3, -3.7, 0.74, 0.78, -5.6, -4.6, 0.01)
    for (x, z) in ((-5.25, -5.55), (-3.75, -5.55), (-5.25, -4.65), (-3.75, -4.65)): p.box('dkwood', x - 0.03, x + 0.03, 0.0, 0.74, z - 0.03, z + 0.03)
    for (x, z, r) in ((-4.9, -4.2, 0), (-4.1, -4.2, 0), (-4.5, -6.0, 180)):
        q = Piece(); q.cham('leather', -0.21, 0.21, 0.45, 0.52, -0.21, 0.21, 0.015); q.cham('dkwood', -0.2, 0.2, 0.52, 0.95, 0.17, 0.21, 0.012)
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): q.box('dkwood', sx * 0.18 - 0.018, sx * 0.18 + 0.018, 0.0, 0.45, sz * 0.18 - 0.018, sz * 0.18 + 0.018)
        p.merge(q, rot_y(r, (x, 0, z)))
    lathe(p, 'bronze', [(0.08, 0.78), (0.08, 0.8), (0.015, 0.82), (0.015, 1.15)], -4.5, -5.1, 0.0, 10); lathe(p, 'felt', [(0.05, 1.08), (0.14, 1.2), (0.13, 1.21), (0.04, 1.1)], -4.5, -5.02, 0.0, 14)
    for (x, z) in ((-4.4, -3.0), (-4.4, -5.2)): ceil_lamp(p, x, z, H1 - SLAB)
    return p
def mailroom():
    """Sala de correio e encomendas (fundos a esquerda do saguao): prateleiras de aco com caixas, mesa com balanca e carrinho."""
    p = Piece()
    for x0 in (-6.6, -5.4):
        x1 = x0 + 1.1; z0, z1 = -6.64, -6.2
        for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)): p.box('steel', x - 0.02, x + 0.02, 0.0, 2.0, z - 0.02, z + 0.02)
        for y in (0.1, 0.6, 1.1, 1.6, 1.98): p.box('steel', x0, x1, y, y + 0.02, z0, z1)
        rng = np.random.default_rng(int(-x0 * 7))
        for y in (0.12, 0.62, 1.12, 1.62):
            x = x0 + 0.04
            while x < x1 - 0.22:
                w_ = rng.uniform(0.18, 0.34); h_ = rng.uniform(0.12, 0.36); p.cham('box_c', x, x + w_, y, y + h_, z0 + 0.03, z1 - 0.03, 0.006); x += w_ + 0.03
    p.cham('dkwood', -3.9, -2.3, 0.0, 0.9, -6.64, -6.0, 0.01); p.cham('marble_d', -3.92, -2.28, 0.9, 0.94, -6.66, -5.98, 0.006)
    p.box('chrome', -3.6, -3.2, 0.94, 1.0, -6.4, -6.1); p.box('cream', -3.55, -3.25, 1.0, 1.02, -6.35, -6.15)
    q = Piece(); q.cham('steel', -0.3, 0.3, 0.15, 0.2, -0.45, 0.45, 0.01)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): seg_cyl(q, 'dark', (sx * 0.25 - 0.02, 0.07, sz * 0.38), (sx * 0.25 + 0.02, 0.07, sz * 0.38), 0.07, 10)
    for sx in (-1, 1): seg_cyl(q, 'steel', (sx * 0.28, 0.2, 0.45), (sx * 0.28, 1.0, 0.5), 0.015, 6)
    seg_cyl(q, 'steel', (-0.28, 1.0, 0.5), (0.28, 1.0, 0.5), 0.015, 6); q.cham('box_c', -0.22, 0.2, 0.2, 0.5, -0.35, 0.1, 0.006)
    p.merge(q, tr(-4.2, 0, -3.0))
    for (x, z) in ((-4.4, -3.6),): ceil_lamp(p, x, z, H0 - SLAB)
    return p
def service():
    """Corredor de servico (fundos a direita do saguao): conteineres de lixo com rodas, tanque de servico, bicicletario de parede."""
    p = Piece()
    for (x, z) in ((5.9, -5.2), (5.9, -3.9)):
        q = Piece(); q.cham('felt', -0.4, 0.4, 0.12, 1.05, -0.55, 0.55, 0.02); q.cham('dark', -0.43, 0.43, 1.05, 1.1, -0.58, 0.58, 0.01)
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): seg_cyl(q, 'dark', (sx * 0.3 - 0.02, 0.06, sz * 0.45), (sx * 0.3 + 0.02, 0.06, sz * 0.45), 0.06, 10)
        p.merge(q, tr(x, 0, z))
    p.cham('porcelain', 2.12, 2.7, 0.0, 0.5, -1.4, -0.82, 0.02); p.cyl('chrome', 0.014, 0.5, 0.9, 2.2, -1.1, 8); seg_cyl(p, 'chrome', (2.2, 0.88, -1.1), (2.35, 0.88, -1.1), 0.01, 6)
    for z in (-2.2, -2.9, -3.6):
        seg_cyl(p, 'steel', (2.06, 1.6, z), (2.35, 1.6, z), 0.012, 6)
    for (x, z) in ((4.5, -3.6),): ceil_lamp(p, x, z, H0 - SLAB)
    return p

# ============================================================================ terraco, coroa, marquise
def terrace():
    """Terraco do recuo (pivo: origem, cota do terraco): laje com forro por baixo, piso de placas com juntas fora do fuste alto,
    floreiras junto da platibanda, vasos com arvores nos cantos, bancos, mesinhas de pedra, balizadores de luz."""
    p = Piece()
    ring = sbox(-LI, -LI, LI, LI).difference(sbox(-UI, -UI, UI, UI)); up = sbox(-UX, -UX, UX, UX)
    ext_y(p, 'ceil', ring, -SLAB, -SLAB + 0.01); ext_y(p, 'concrete', ring, -SLAB + 0.01, -0.05)
    ext_y(p, 'concrete', ring.intersection(up), -0.05, 0.0)
    out = ring.difference(up); J = 0.6
    for x in np.arange(-LI, LI, J):
        for z in np.arange(-LI, LI, J):
            q = sbox(x + 0.004, z + 0.004, x + J - 0.004, z + J - 0.004).intersection(out)
            if q.area > 1e-5: ext_y(p, 'paver', q, -0.03, 0.0)
    ext_y(p, 'dark', out.buffer(-0.001, join_style=2), -0.05, -0.03)
    for s in (-1, 1):
        for (x0, x1) in ((-3.8, -1.2), (1.2, 3.8)):
            z0, z1 = s * (LI - 0.02), s * (LI - 0.45); z0, z1 = sorted((z0, z1))
            p.cham('concrete', x0, x1, 0.0, 0.55, z0, z1, 0.02); p.box('mulch', x0 + 0.05, x1 - 0.05, 0.55, 0.562, z0 + 0.05, z1 - 0.05)
            for k in range(6): p.sphere('hedge', 0.2, x0 + 0.25 + k * (x1 - x0 - 0.5) / 5, 0.65, (z0 + z1) / 2, 1)
    for (x, z) in ((-5.85, -5.85), (5.85, -5.85), (-5.85, 5.85), (5.85, 5.85)):
        p.merge(planter(2.6, 0.42), tr(x, 0, z))
    for s in (-1, 1):
        for z in (-2.8, 2.8):
            q = Piece()
            for xx in (-0.6, 0.6): q.cham('stone', xx - 0.08, xx + 0.08, 0.0, 0.42, -0.2, 0.2, 0.01)
            for i in range(4): zz = -0.2 + i * 0.105; q.cham('wood', -0.8, 0.8, 0.42, 0.46, zz, zz + 0.09, 0.006)
            p.merge(q, rot_y(90 * s, (s * (LI - 0.3), 0, z)))
    for (x, z) in ((-5.85, 4.3), (5.85, 4.3), (-5.85, -4.3), (5.85, -4.3)):
        p.cyl('stone', 0.3, 0.7, 0.74, x, z, 20); lathe(p, 'iron', [(0.22, 0.0), (0.22, 0.02), (0.03, 0.05), (0.025, 0.7)], x, z, 0.0, 12)
    for (x, z) in ((-5.85, 1.3), (5.85, 1.3), (-5.85, -1.3), (5.85, -1.3), (-1.0, 5.85), (1.0, 5.85), (-1.0, -5.85), (1.0, -5.85)):
        p.cyl('bronze', 0.07, 0.0, 0.6, x, z, 10); lathe(p, 'lamp_glass', [(0.065, 0.45), (0.065, 0.58)], x, z, 0.0, 10)
        p.cyl('bronze', 0.09, 0.6, 0.63, x, z, 10)
    return p
def roof_ladder():
    """Escada de marinheiro do ultimo patamar ate o alcapao da cobertura (pivo: origem, cota do ultimo andar)."""
    p = Piece(); z0, z1 = -0.95, -1.2; h = HF
    for x in (-0.65, -0.15): seg_cyl(p, 'steel', (x, 0.0, z0), (x, h + 0.25, z1), 0.02, 8)
    for k in range(1, 11):
        y = k * 0.28; z = z0 + (z1 - z0) * y / (h + 0.25)
        if y < h - 0.3: seg_cyl(p, 'steel', (-0.65, y, z), (-0.15, y, z), 0.014, 6)
    return p
def crown_top():
    """Casa de maquinas da coroa (pivo: origem, cota da cobertura): paredes de pedra com aletas de terracota e venezianas, porta,
    pilares de canto escalonados, cornija, telhado em piramide de ardosia com rufos de bronze, mastro com aneis, esferas e farol
    vermelho; dentro, maquina do elevador, quadro de comando, luminaria e respiros na laje."""
    p = Piece(); A = 3.0; tw_ = 0.3; H = 4.0
    holes = {'front': [(-0.45, 0.45, 0.0, 2.1)], 'back': [], 'left': [(-1.2, 1.2, 1.6, 2.8)], 'right': [(-1.2, 1.2, 1.6, 2.8)]}
    for (side, ry) in (('front', 0), ('back', 180), ('left', -90), ('right', 90)):
        q = Piece(); hs = holes[side]
        xs = sorted(set([-A, A] + [v for hh in hs for v in hh[:2]])); ys = sorted(set([0.0, H] + [v for hh in hs for v in hh[2:]]))
        def cell(i, j, k, hs=hs, xs=xs, ys=ys):
            cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
            return None if any(a < cx < b and c < cy < d for (a, b, c, d) in hs) else 'stone'
        for m, mesh in grid_solid(xs, ys, [-tw_, 0.0], cell).items(): q.add(m, mesh)
        for x in (-2.0, -1.0, 0.0, 1.0, 2.0) if side != 'front' else (-2.0, -1.0, 1.0, 2.0):
            if side in ('left', 'right') and abs(x) <= 1.0: continue
            q.cham('terra', x - 0.1, x + 0.1, 0.3, H - 0.5, 0.0, 0.12, 0.012)
        for (a, b, c, d) in hs:
            if side == 'front':
                q2 = Piece(); door_casing(q2, b - a, tw_, d); q.merge(q2, tr(0, 0, -tw_ / 2))
                q.merge(wall_lantern(), tr(0.0, 2.45, 0.0))
            else:
                for (xa, xb) in ((a, a + 0.06), (b - 0.06, b)): q.box('bronze', xa, xb, c, d, -0.2, -0.1)
                q.box('bronze', a, b, c, c + 0.06, -0.2, -0.1); q.box('bronze', a, b, d - 0.06, d, -0.2, -0.1)
                for y in np.arange(c + 0.12, d - 0.06, 0.1): q.hull('bronze', [(x, y + dy, z) for x in (a + 0.06, b - 0.06) for (dy, z) in ((0.0, -0.18), (0.0, -0.17), (0.07, -0.1), (0.07, -0.11))])
        prof_x(q, 'stone', -A, A, [(0.0, H - 0.3), (0.06, H - 0.3), (0.12, H - 0.18), (0.18, H - 0.1), (0.18, H), (0.0, H)])
        prof_x(q, 'stone', -A, A, [(0.0, 0.0), (0.06, 0.0), (0.06, 0.25), (0.0, 0.3)])
        p.merge(q, rot_y(ry, (0, 0, 0)) @ tr(0, 0, A))
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        for (a, b, c, d) in ((A - 0.25, A + 0.25, -0.0, H + 0.6), (A - 0.18, A + 0.18, H + 0.6, H + 1.0), (A - 0.1, A + 0.1, H + 1.0, H + 1.3)):
            p.box('stone', *sorted((sx * a, sx * b)), c, d, *sorted((sz * a, sz * b)))
        p.hull('stone', [(sx * A + dx, H + 1.3, sz * A + dz) for dx in (-0.1, 0.1) for dz in (-0.1, 0.1)] + [(sx * A, H + 1.55, sz * A)])
    R = A + 0.25; yb = H; yt = H + 3.6
    p.hull('roof_d', [(sx * R, yb, sz * R) for sx in (-1, 1) for sz in (-1, 1)] + [(0, yt, 0)])
    p.box('ceil', -A + tw_, A - tw_, H - 0.02, H, -A + tw_, A - tw_)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): seg_cyl(p, 'bronze', (sx * R, yb + 0.03, sz * R), (0, yt + 0.03, 0), 0.04, 6)
    lathe(p, 'bronze', [(0.3, yt - 0.3), (0.32, yt - 0.1), (0.22, yt + 0.1), (0.12, yt + 0.2), (0.12, yt + 0.5), (0.18, yt + 0.55), (0.18, yt + 0.6), (0.08, yt + 0.7),
                        (0.06, yt + 2.2), (0.12, yt + 2.25), (0.12, yt + 2.3), (0.045, yt + 2.35), (0.035, yt + 4.2), (0.0, yt + 4.4)], 0, 0, 0.0, 14)
    p.sphere('gold', 0.2, 0, yt + 1.2, 0, 2); p.sphere('gold', 0.12, 0, yt + 3.1, 0, 2)
    for y in (yt + 1.6, yt + 2.7): ring_y(p, 'bronze', 0.045, 0.16, y, y + 0.03, 0, 0, 16)
    p.sphere('red', 0.07, 0, yt + 4.45, 0, 1)
    # dentro: maquina do elevador, quadro, luminaria
    p.cham('steel', 0.4, 1.9, 0.0, 0.25, -2.4, -1.0, 0.01); p.cham('felt', 0.5, 1.2, 0.25, 0.85, -2.2, -1.2, 0.02)
    disc_x(p, 'steel', 0.35, 1.25, 1.4, 0.65, -1.7, 24); disc_x(p, 'dark', 0.3, 1.4, 1.6, 0.65, -1.7, 20)
    p.cham('dark', 1.55, 1.85, 0.25, 0.75, -2.0, -1.4, 0.01)
    p.cham('metal', -2.6, -1.9, 0.6, 2.0, -2.68, -2.38, 0.01); p.box('dark', -2.55, -1.95, 0.7, 1.9, -2.38, -2.37)
    p.cyl('bronze', 0.15, H - 0.06, H - 0.02, 0, 0, 14); p.cyl('lamp_glass', 0.12, H - 0.1, H - 0.06, 0, 0, 14)
    # respiros e para-raios na laje fora da casa de maquinas
    for (x, z) in ((-3.9, 3.9), (3.9, 3.9), (3.9, -3.9)):
        p.cyl('metal', 0.12, -0.0, 0.6, x, z, 14); lathe(p, 'metal', [(0.25, 0.6), (0.25, 0.64), (0.2, 0.7), (0.0, 0.74)], x, z, 0.0, 16)
    return p
def marquee():
    """Marquise sobre o portal (pivo: face da fachada, x = 0, cota do piso do saguao; para +Z): laje de bronze com testeira de
    degraus, leque dourado na frente, forro com luzes embutidas e tirantes ate a fachada."""
    p = Piece(); x0, x1, d = -2.4, 2.4, 2.2; yb, yt = 3.65, 3.95
    p.box('ceil', x0 + 0.06, x1 - 0.06, yb, yb + 0.02, 0.0, d - 0.06)
    p.box('membrane', x0 + 0.06, x1 - 0.06, yt - 0.04, yt, 0.0, d - 0.06); p.box('concrete', x0 + 0.06, x1 - 0.06, yb + 0.02, yt - 0.04, 0.0, d - 0.06)
    for (a, b, c, e) in ((x0, x1, d - 0.06, d), (x0, x0 + 0.06, 0.0, d - 0.06), (x1 - 0.06, x1, 0.0, d - 0.06)): p.box('bronze', a, b, yb - 0.08, yt + 0.06, c, e)
    for (w_, y0, y1) in ((1.6, yt + 0.06, yt + 0.2), (1.0, yt + 0.2, yt + 0.34), (0.45, yt + 0.34, yt + 0.46)): p.box('bronze', -w_, w_, y0, y1, d - 0.06, d)
    for k in range(9):
        t0 = math.pi * k / 9 + 0.03; t1 = math.pi * (k + 1) / 9 - 0.03
        f_ = Polygon([(0.0, yb + 0.02)] + [(0.95 * math.cos(t), yb + 0.02 + 0.95 * math.sin(t)) for t in np.linspace(t0, t1, 3)]).intersection(sbox(-1.6, yb - 0.06, 1.6, yt + 0.44))
        if k % 2 == 0: ext(p, 'gold', f_, d, d + 0.012)
    for x in np.arange(x0 + 0.2, x1 - 0.1, 0.25): p.box('gold', x - 0.01, x + 0.01, yb - 0.06, yb - 0.02, d, d + 0.01)
    for (x, z) in ((-1.6, 0.8), (-0.55, 0.8), (0.55, 0.8), (1.6, 0.8), (-1.6, 1.6), (-0.55, 1.6), (0.55, 1.6), (1.6, 1.6)):
        p.cyl('bronze', 0.09, yb - 0.006, yb, x, z, 14); p.cyl('lamp_glass', 0.07, yb - 0.01, yb - 0.006, x, z, 14)
    for s in (-1, 1):
        seg_cyl(p, 'bronze', (s * 1.0, 5.6, 0.16), (s * 2.1, yt + 0.06, d - 0.15), 0.025, 8)
        p.cham('bronze', s * 1.0 - 0.08, s * 1.0 + 0.08, 5.5, 5.7, 0.15, 0.19, 0.005)
    return p

# ============================================================================ portas
def door_bronze(w=0.84, h=2.42, t=0.05):
    """Folha da porta do portal (pivo: dobradica, embaixo): quadro de bronze, vidro, 3 travessas, rodape com leque e puxador."""
    p = Piece(); s = 0.09
    p.cham('bronze', 0.0, s, 0.0, h, -t / 2, t / 2, 0.004); p.cham('bronze', w - s, w, 0.0, h, -t / 2, t / 2, 0.004)
    p.cham('bronze', s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.004); p.cham('bronze', s - 0.002, w - s + 0.002, 0.0, 0.42, -t / 2, t / 2, 0.004)
    p.box('glass', s - 0.004, w - s + 0.004, 0.42, h - s + 0.004, -0.004, 0.004)
    for y in (1.2, 1.25): p.box('bronze', s, w - s, y, y + 0.025, -0.012, 0.012)
    for k in range(5):
        t0 = math.pi * k / 5 + 0.05; t1 = math.pi * (k + 1) / 5 - 0.05
        f_ = Polygon([(w / 2, 0.06)] + [(w / 2 + 0.3 * math.cos(tt), 0.06 + 0.3 * math.sin(tt)) for tt in np.linspace(t0, t1, 3)])
        for z in (1, -1): ext(p, 'gold', f_, *sorted((z * t / 2, z * (t / 2 + 0.006))))
    for z in (1, -1): seg_cyl(p, 'gold', (w - 0.16, 0.85, z * (t / 2 + 0.05)), (w - 0.16, 1.65, z * (t / 2 + 0.05)), 0.018, 10)
    for z in (1, -1):
        for y in (0.9, 1.6): seg_cyl(p, 'gold', (w - 0.16, y, z * t / 2), (w - 0.16, y, z * (t / 2 + 0.05)), 0.01, 6)
    for yy in (0.2, 2.1): p.cyl('bronze', 0.012, yy, yy + 0.1, 0.0, t / 2 + 0.003, 8)
    return p
def recolor(p, m):
    q = Piece()
    for k, ms in p.parts.items():
        for mm in ms: q.add(m.get(k, k), mm)
    return q

# ============================================================================ terreno
SX0, SX1, SZ0, SZ1 = -12.0, 12.0, -11.0, 16.0
WALK = sbox(-11.0, -10.0, 11.0, 10.6); STREET = sbox(SX0, 10.8, SX1, SZ1); CURB = sbox(SX0, 10.6, SX1, 10.8)
TREES = [(-5.5, 9.3), (5.5, 9.3), (-9.6, 9.3), (9.6, 9.3), (-9.3, 3.5), (9.3, 3.5), (-9.3, -3.5), (9.3, -3.5), (-6.4, -8.6), (6.4, -8.6)]
GRATE = 0.6
def site():
    """Terreno (pivo: origem): calcada de placas em volta da torre com grelhas para as arvores, guia, rua de asfalto com faixa
    amarela tracejada e gramado nas bordas."""
    p = Piece()
    grates = unary_union([sbox(x - GRATE, z - GRATE, x + GRATE, z + GRATE) for (x, z) in TREES])
    walk = WALK.difference(sbox(-LX, -LX, LX, LX)).difference(grates)
    p.merge(paving(walk, Y0, 1.0, 'concrete'))
    ext_y(p, 'curb', CURB, GY, Y0); ext_y(p, 'asphalt', STREET, GY, 0.02)
    for x in np.arange(SX0 + 0.5, SX1, 3.0): p.box('paint_y', x, x + 1.5, 0.02, 0.024, 13.35, 13.45)
    grass = sbox(SX0, SZ0, SX1, SZ1).difference(unary_union([WALK, STREET, CURB]))
    ext_y(p, 'grass', grass, GY, 0.1)
    return p
def tree_grate():
    """Grelha de ferro da arvore (pivo: centro, cota da calcada): moldura, barras radiais e terra por baixo."""
    p = Piece(); g = GRATE
    ext_y(p, 'mulch', sbox(-g, -g, g, g), GY - Y0, -0.06)
    ext_y(p, 'iron', sbox(-g, -g, g, g).difference(sbox(-g + 0.05, -g + 0.05, g - 0.05, g - 0.05)), -0.06, 0.0)
    ext_y(p, 'iron', Point(0, 0).buffer(0.3, 24).difference(Point(0, 0).buffer(0.25, 24)), -0.06, 0.0)
    for k in range(16):
        a = 2 * math.pi * k / 16; r1 = (g - 0.05) / max(abs(math.cos(a)), abs(math.sin(a)))
        p.seg('iron', (0.28 * math.cos(a), -0.03, 0.28 * math.sin(a)), (r1 * math.cos(a), -0.03, r1 * math.sin(a)), 0.025, 0.06)
    return p
def tree(h=6.0, r=1.7, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.13, -0.06), (0.11, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    return p
def lamp_post():
    """Poste deco (pivo: base, cota da calcada): base escalonada, fuste canelado, lanterna de vidro com chapeu em degraus."""
    p = Piece()
    for (r, y0, y1) in ((0.24, 0.0, 0.12), (0.19, 0.12, 0.3), (0.14, 0.3, 0.45)): p.cyl('dark', r, y0, y1, 0, 0, 16)
    p.cyl('dark', 0.08, 0.45, 3.6, 0, 0, 12)
    for k in range(8): a = 2 * math.pi * k / 8; p.box('dark', 0.075 * math.cos(a) - 0.015, 0.075 * math.cos(a) + 0.015, 0.5, 3.4, 0.075 * math.sin(a) - 0.015, 0.075 * math.sin(a) + 0.015)
    p.cyl('dark', 0.12, 3.6, 3.7, 0, 0, 14)
    lathe(p, 'lamp_glass', [(0.12, 3.7), (0.2, 3.9), (0.2, 4.3), (0.14, 4.4)], 0, 0, 0.0, 16)
    for k in range(4): a = 2 * math.pi * k / 4 + math.pi / 4; seg_cyl(p, 'dark', (0.17 * math.cos(a), 3.72, 0.17 * math.sin(a)), (0.2 * math.cos(a), 4.38, 0.2 * math.sin(a)), 0.012, 4)
    for (r, y0, y1) in ((0.26, 4.4, 4.46), (0.18, 4.46, 4.54), (0.1, 4.54, 4.62)): p.cyl('dark', r, y0, y1, 0, 0, 16)
    p.sphere('dark', 0.05, 0, 4.66, 0, 1)
    return p
def bench():
    p = Piece()
    for s in (-1, 1):
        p.cham('iron', s * 0.75 - 0.04, s * 0.75 + 0.04, 0.0, 0.42, -0.25, 0.22, 0.01)
        p.hull('iron', [(s * 0.75 + dx, y, z) for dx in (-0.03, 0.03) for (y, z) in ((0.42, -0.25), (0.42, -0.2), (0.85, -0.32), (0.85, -0.28))])
    for i in range(5): z = -0.24 + i * 0.095; p.cham('wood', -0.95, 0.95, 0.42, 0.46, z, z + 0.08, 0.006)
    for i in range(3): y = 0.52 + i * 0.11; p.hull('wood', [(x, y + dy, -0.27 - (y + dy - 0.42) * 0.12) for x in (-0.95, 0.95) for dy in (0.0, 0.08)] + [(x, y + dy, -0.3 - (y + dy - 0.42) * 0.12) for x in (-0.95, 0.95) for dy in (0.0, 0.08)])
    return p
def hydrant():
    p = Piece(); lathe(p, 'red', [(0.16, 0.0), (0.16, 0.05), (0.12, 0.08), (0.12, 0.6), (0.15, 0.62), (0.15, 0.66), (0.1, 0.72), (0.05, 0.8), (0.02, 0.84), (0.0, 0.86)], sec=16)
    for s in (-1, 1): disc_x(p, 'red', 0.05, *sorted((s * 0.12, s * 0.22)), 0.45, 0.0, 12); disc_x(p, 'red', 0.06, *sorted((s * 0.2, s * 0.24)), 0.45, 0.0, 12)
    disc_z(p, 'red', 0.07, 0.1, 0.22, 0.0, 0.45, 12)
    return p
def bike_rack():
    p = Piece()
    for k in range(4):
        x = -0.9 + k * 0.6; pts = [(x, 0.0, -0.35)] + [(x, 0.55 + 0.3 * math.sin(t), -0.35 * math.cos(t)) for t in np.linspace(0, math.pi, 9)] + [(x, 0.0, 0.35)]
        for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', a, b, 0.025, 8)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def door_x(n, c, zw, into, hinge, y, tg, w):
    if hinge == 'lo': put(n, c - w / 2, y, zw, 0, tg, door=-90 if into > 0 else 90)
    else: put(n, c + w / 2, y, zw, 180, tg, door=90 if into > 0 else -90)
def door_z(n, c, xw, into, hinge, y, tg, w):
    if hinge == 'lo': put(n, xw, y, c - w / 2, -90, tg, door=90 if into > 0 else -90)
    else: put(n, xw, y, c + w / 2, 90, tg, door=-90 if into > 0 else 90)
def doors(specs, y, tg):
    """specs (lado esquerdo): ('x' ou 'z', peca, centro, eixo, para onde abre, dobradica, largura, espelhar)."""
    for (ax, n, c, wv, into, hinge, w, mir) in specs:
        for s in ((1, -1) if mir else (1,)):
            if ax == 'x': door_x(n, s * c, wv, into, hinge if s > 0 else {'lo': 'hi', 'hi': 'lo'}[hinge], y, tg, w)
            else: door_z(n, c, s * wv, s * into, hinge, y, tg, w)

pieces = {
    'f_win': fmod('win'), 'f_plain': fmod('plain'), 'f_door': fmod('door'),
    'g_win': gmod('win'), 'g_door': gmod('door'), 'g_svc': gmod('svc'), 'g_plain': gmod('plain'),
    'c_win': cmod('win'), 'c_plain': cmod('plain'), 'parapet': pmod(), 'crown': kmod(),
    'corner': kcorner('typ'), 'corner_g': kcorner('g'), 'corner_c': kcorner('c'), 'corner_par': kcorner('par'), 'corner_crown': kcorner('crown'),
    'floor_0': slab('0'), 'slab_1': slab('1'), 'slab_low': slab('l'), 'slab_up': slab('u'), 'slab_roof': slab('roof'),
    'plan_0': plan_base(0), 'plan_1': plan_base(1), 'plan_low': plan_low(), 'plan_up': plan_up(),
    'stair_0': stair_u(H0, 12, -LI, 0.26, 'stone', 'gold'), 'stair_1': stair_u(H1, 9, ZC, 0.24), 'stair': stair_u(HF, 8, ZC, 0.26), 'roof_ladder': roof_ladder(),
    'apt_front': apt_front(), 'apt_back': apt_back(), 'studio': studio(), 'laundry': laundry(), 'storage': storage(),
    'lobby': lobby_set(), 'mailroom': mailroom(), 'service': service(), 'club': club_set(), 'library': library(),
    'chandelier': chandelier(H0 - SLAB, 3), 'chandelier_s': chandelier(H1 - SLAB, 2),
    'terrace': terrace(), 'crown_top': crown_top(), 'marquee': marquee(),
    'door_portal': door_bronze(0.84, 2.42), 'door_entry': recolor(door_interior(0.82, 2.06), {'door_int': 'door'}),
    'door_room': door_interior(0.72, 2.06), 'door_bath': door_interior(0.68, 2.0), 'door_stair': door_metal(0.82, 2.06),
    'door_svc': door_metal(0.92, 2.16), 'door_terrace': door_glass(0.88, 2.36), 'door_roof': door_metal(0.82, 2.04),
    'site': site(), 'tree_grate': tree_grate(), 'tree': tree(5.6, 1.25), 'tree_b': tree(4.8, 1.05, 'leaf2', 4), 'lamp_post': lamp_post(),
    'bench': bench(), 'hydrant': hydrant(), 'bike_rack': bike_rack(), 'player_scale_ref': player_ref()}
for k in ('apt_front', 'apt_back', 'studio'): pieces[k + '_r'] = mirrored(pieces[k], mirror_x())
pieces['laundry_r'] = mirrored(pieces['laundry'], mirror_x())

# ============================================================================ montagem
M7 = [-6, -4, -2, 0, 2, 4, 6]; M5 = [-4, -2, 0, 2, 4]
def ring(kinds, y, X, ms, tg, corner=None):
    """kinds: funcao (lado, coordenada) -> peca. Lados: front (+Z), back (-Z), left (-X), right (+X)."""
    for m in ms:
        put(kinds('front', m), m, y, X, 0, tg + ['front', 'ext']); put(kinds('back', m), m, y, -X, 180, tg + ['back', 'ext'])
        put(kinds('left', m), -X, y, m, -90, tg + ['left', 'ext']); put(kinds('right', m), X, y, m, 90, tg + ['right', 'ext'])
    if corner:
        for (x, z, ry, sd) in ((X, X, 0, 'front'), (-X, X, -90, 'front'), (X, -X, 90, 'back'), (-X, -X, 180, 'back')): put(corner, x, y, z, ry, tg + ['ext', sd])
# saguao
y = lvl(0); tg = ['floor0']
ring(lambda s, m: {('front', 0): 'g_door', ('back', 4): 'g_svc', ('back', -2): 'g_plain', ('back', 0): 'g_plain', ('back', 2): 'g_plain',
                   ('left', 0): 'g_plain', ('right', 0): 'g_plain'}.get((s, m), 'g_win'), y, LX, M7, tg, 'corner_g')
put('floor_0', 0, y, 0, 0, tg); put('plan_0', 0, y, 0, 0, tg); put('stair_0', 0, y, 0, 0, tg)
put('lobby', 0, y, 0, 0, tg); put('mailroom', 0, y, 0, 0, tg); put('service', 0, y, 0, 0, tg)
for (x, z) in ((0.0, 3.0), (-4.4, 4.2), (4.3, 3.2)): put('chandelier', x, y, z, 0, tg)
for (s, ry, d) in ((-1, 0, 90), (1, 180, -90)): put('door_portal', s * 0.85, y + 0.01, LX - 0.14, ry, tg + ['front', 'ext'], door=d)
door_x('door_svc', 4.0, -LX + T / 2, 1, 'hi', y + 0.012, tg + ['back', 'ext'], 0.92)
doors([('x', 'door_entry', -3.4, ZB, -1, 'hi', 0.82, True), ('x', 'door_stair', SD, ZB, -1, 'lo', 0.82, False)], y + 0.01, tg)
put('marquee', 0, y, LX, 0, ['site', 'front'])
# 1o andar
y = lvl(1); tg = ['floor1']
ring(lambda s, m: 'c_plain' if (s == 'back' and m in (-2, 0, 2)) else 'c_win', y, LX, M7, tg, 'corner_c')
put('slab_1', 0, y, 0, 0, tg); put('plan_1', 0, y, 0, 0, tg); put('stair_1', 0, y, 0, 0, tg)
put('club', 0, y, 0, 0, tg); put('library', 0, y, 0, 0, tg); put('laundry_r', 0, y, 0, 0, tg)
for (x, z) in ((-3.6, 3.3), (3.6, 4.4)): put('chandelier_s', x, y, z, 0, tg)
doors([('x', 'door_entry', -3.4, ZB, -1, 'hi', 0.82, True), ('x', 'door_stair', SD, ZB, -1, 'lo', 0.82, False)], y + 0.01, tg)
# andares baixos
LOW_DOORS = [('x', 'door_entry', -3.0, ZF, 1, 'lo', 0.82, True), ('x', 'door_entry', -3.4, ZB, -1, 'hi', 0.82, True), ('x', 'door_stair', SD, ZB, -1, 'lo', 0.82, False),
             ('z', 'door_room', 2.0, -3.7, -1, 'hi', 0.72, True), ('z', 'door_bath', 1.9, -2.3, 1, 'lo', 0.68, True),
             ('z', 'door_bath', -1.6, -4.6, -1, 'lo', 0.68, True), ('x', 'door_room', -3.0, ZCW, -1, 'lo', 0.72, True)]
for k in range(2, NS):
    y = lvl(k); tg = [f'floor{k}']
    ring(lambda s, m: 'f_plain' if (s in ('front', 'back') and m == 0) else 'f_win', y, LX, M7, tg, 'corner')
    for n in ('slab_low', 'plan_low', 'stair', 'apt_front', 'apt_front_r', 'apt_back', 'apt_back_r'): put(n, 0, y, 0, 0, tg)
    doors(LOW_DOORS, y + 0.01, tg)
# terraco do recuo e andares altos
y = lvl(NS); put('terrace', 0, y, 0, 0, ['terrace'])
ring(lambda s, m: 'parapet', y, LX, M7, ['terrace'], 'corner_par')
UP_DOORS = [('x', 'door_entry', -1.2, ZF, 1, 'hi', 0.82, True), ('x', 'door_entry', -3.4, ZB, -1, 'hi', 0.82, True), ('x', 'door_stair', SD, ZB, -1, 'lo', 0.82, False),
            ('z', 'door_bath', 1.9, -2.6, -1, 'lo', 0.68, True)]
for k in range(NS, NF):
    y = lvl(k); tg = [f'floor{k}']
    def up_kind(s, m, k=k):
        if s == 'front': return 'f_plain' if m == 0 else 'f_win'
        if s == 'back': return 'f_plain' if m in (-2, 0, 2) else 'f_win'
        return 'f_door' if (m == 0 and k == NS) else 'f_win'
    ring(up_kind, y, UX, M5, tg, 'corner')
    for n in ('slab_up', 'plan_up', 'studio', 'studio_r', 'laundry', 'storage'): put(n, 0, y, 0, 0, tg)
    put('stair', 0, y, 0, 0, tg) if k < NF - 1 else put('roof_ladder', 0, y, 0, 0, tg)
    doors(UP_DOORS, y + 0.01, tg)
    if k == NS:
        for s in (-1, 1): door_z('door_terrace', 0.0, s * (UX - 0.11), -s, 'lo', y + 0.01, tg + ['ext'], 0.88)
# cobertura
y = YR; put('slab_roof', 0, y, 0, 0, ['roof']); put('crown_top', 0, y, 0, 0, ['roof'])
ring(lambda s, m: 'crown', y, UX, M5, ['roof'], 'corner_crown')
door_x('door_roof', 0.0, 3.0 - 0.15, 1, 'lo', y + 0.01, ['roof'], 0.82)
# terreno
st = ['site']; put('site', 0, 0, 0, 0, st)
for k, (x, z) in enumerate(TREES): put('tree_grate', x, Y0, z, 0, st); put('tree' if k % 2 == 0 else 'tree_b', x, Y0 - 0.06, z, 0, st)
for (x, z) in ((-3.2, 10.15), (3.2, 10.15), (-8.0, 10.15), (8.0, 10.15), (-10.4, 0.0), (10.4, 0.0), (-10.4, -7.0), (10.4, -7.0), (0.0, -9.5)): put('lamp_post', x, Y0, z, 0, st)
for x in (-3.6, 3.6): put('bench', x, Y0, 8.5, 0, st)
for z in (-1.0, 6.0): put('bench', -10.2, Y0, z, 90, st); put('bench', 10.2, Y0, z, -90, st)
put('hydrant', 10.2, Y0, 10.1, 0, st); put('bike_rack', -9.9, Y0, -5.5, 90, st)
put('player_scale_ref', 1.5, Y0, 9.0, 0, st); put('player_scale_ref', 1.0, lvl(0), 3.0, 0, ['floor0']); put('player_scale_ref', -6.0, YS, 0.5, 0, ['terrace'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': Y0,
                       'levels': {f'floor{k}': round(lvl(k), 3) for k in range(NF)}, 'roof': round(YR, 3), 'setback_terrace': round(YS, 3),
                       'lower_shaft': {'x': [-LX, LX], 'z': [-LX, LX], 'floors': [0, NS - 1], 'heights': {'lobby': H0, 'floor1': H1, 'typical': HF}},
                       'upper_shaft': {'x': [-UX, UX], 'z': [-UX, UX], 'floors': [NS, NF - 1], 'height': HF},
                       'core': {'stair_x': [-1.94, 0.24], 'elevator_x': [0.36, 1.94], 'corridor_walls_z': [ZB, ZF], 'landing_edge_z': ZL},
                       'crown': 'terracotta band with stepped pinnacles, machine room 6 x 6 m with slate pyramid and spire (about 13 m above the roof)',
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1], 'walk_level': Y0},
                       'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
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
