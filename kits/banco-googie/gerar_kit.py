"""Kit 42: banco googie (anos 50), em ALTO DETALHE (scripts/detalhe/detalhe.py).
Agencia bancaria terrea de 18 x 12 m sob uma cobertura de cascas onduladas (9 abobadas de 3 m, inclinada para a frente) que se
estende sobre o drive-thru. Fachada da frente toda de vidro com caixilhos dourados e porta dupla, colunas em V amarelas sob o beiral,
paredes laterais de pedra rustica, fundos de tijolo, faixa de vidro (clerestorio) entre as paredes e a casca, testeira turquesa
com nervuras e luzes embutidas no forro. Totem turquesa sem texto com estrela atomica e pictograma de moedas.
Dentro: saguao de granilite com estrela de latao, balcao de caixas com 4 guiches de vidro, grade baixa com portinhola, mesas de
preencher, sofa, poltronas tulipa, mesa de centro, luminarias sputnik e relogio-estrela na parede de pedra; caixa-forte com porta
redonda e cofres de aluguel, sala do gerente, copa dos funcionarios e cabine do drive-thru com tubo pneumatico.
Fora: 2 faixas de drive-thru com ilha e terminal de tubo, estacionamento com vagas e batentes, gramado com canteiros de pedras e
iucas, palmeiras, luminarias de cogumelo, calcada e rua.
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
configurar(cores={'fstone': (176, 160, 140), 'brick': (196, 150, 112), 'concrete': (190, 186, 178), 'plaster': (238, 234, 222), 'ceil': (240, 240, 234),
                  'soffit': (232, 236, 228), 'roofw': (238, 236, 226), 'teal': (40, 140, 140), 'teal_d': (28, 104, 106), 'paint_y': (232, 180, 60),
                  'frame': (198, 166, 96), 'gold': (206, 172, 92), 'chrome': (214, 218, 222), 'metal': (186, 190, 194), 'steel': (150, 156, 162),
                  'brass': (204, 166, 84), 'terrazzo': (222, 214, 198), 'terrazzo_t': (88, 160, 156), 'lino': (196, 186, 164), 'marble': (234, 230, 222),
                  'walnut': (116, 76, 50), 'wood': (160, 110, 66), 'dkwood': (94, 60, 40), 'trim': (110, 72, 48), 'vinyl_o': (222, 120, 60),
                  'vinyl_t': (60, 150, 146), 'vinyl_g': (90, 128, 110), 'fabric': (210, 196, 160), 'cream': (240, 232, 210), 'paper': (238, 234, 222),
                  'dark': (40, 40, 42), 'rubber': (30, 30, 30), 'red': (196, 60, 50), 'paint_w': (238, 238, 232), 'sign_w': (244, 242, 232),
                  'asphalt': (70, 72, 74), 'grass': (100, 148, 70), 'mulch': (104, 76, 54), 'leaf': (86, 132, 64), 'leaf2': (112, 150, 72),
                  'palm': (92, 140, 70), 'bark': (124, 98, 72), 'boulder': (150, 140, 128), 'yucca': (104, 140, 90), 'curb': (196, 192, 184),
                  'lamp_glass': (255, 238, 196), 'vault': (130, 136, 140), 'porcelain': (244, 244, 240), 'vinyl_r': (196, 70, 54), 'door_int': (150, 104, 66)},
           texturas={'fstone': 'stone2', 'brick': 'brick', 'plaster': 'plaster', 'concrete': 'render', 'asphalt': 'render', 'terrazzo': 'render',
                     'grass': 'render', 'lino': 'render', 'walnut': 'planks', 'wood': 'planks', 'curb': 'render', 'roofw': 'render'},
           out=OUT)
D.METAL.update({'frame', 'gold', 'chrome', 'metal', 'steel', 'brass', 'vault'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.12; GT_ = 0.12                   # modulo, parede externa, parede interna, fachada de vidro
Y0 = 0.15                                                  # piso (nivel da calcada coberta)
X0, X1, HZ = -10.0, 8.0, 6.0                               # predio: x de -10 a 8, z de -6 a 6, frente para +Z
HWALL = 3.6                                                # topo das paredes (sobre o piso); acima, clerestorio ate a casca
RX0, RX1, RZ0, RZ1 = -11.0, 16.0, -7.2, 8.6                # cobertura (inclui o drive-thru)
VW = 3.0; RH0 = 4.25; RS = 0.05; RA = 0.32; RT = 0.16      # largura das abobadas, altura atras, inclinacao, flecha, espessura
ZP = -2.5                                                  # parede da caixa-forte / gerencia / copa
ZC = -0.8                                                  # linha do balcao de caixas e da grade
XB = 5.0                                                   # parede da cabine do drive-thru
def ytop(x, z):
    u = ((x - RX0) / VW) % 1.0; return RH0 + RS * (z - RZ0) + RA * math.sin(math.pi * u)
def ybot(x, z): return ytop(x, z) - RT
VALLEYS = [RX0 + VW * k for k in range(1, 9)]; CRESTS = [RX0 + VW * (k + 0.5) for k in range(9)]
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
def hf_solid(xs, zs, fb, ft):
    """Solido entre 2 superficies y = fb(x, z) e y = ft(x, z) sobre a grade xs x zs (estanque)."""
    nx, nz = len(xs), len(zs); V = []
    for f in (ft, fb):
        for x in xs:
            for z in zs: V.append((x, f(x, z), z))
    N = nx * nz; idx = lambda i, j, b=0: b * N + i * nz + j; F = []
    for i in range(nx - 1):
        for j in range(nz - 1):
            a, b_, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            F += [[a, c, b_], [a, d, c]]
            a, b_, c, d = idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j + 1, 1), idx(i, j + 1, 1)
            F += [[a, b_, c], [a, c, d]]
    ring = [(i, 0) for i in range(nx)] + [(nx - 1, j) for j in range(1, nz)] + [(i, nz - 1) for i in range(nx - 2, -1, -1)] + [(0, j) for j in range(nz - 2, 0, -1)]
    for k in range(len(ring)):
        (i0, j0), (i1, j1) = ring[k], ring[(k + 1) % len(ring)]
        a, b_ = idx(i0, j0), idx(i1, j1); c, d = idx(i1, j1, 1), idx(i0, j0, 1)
        F += [[a, b_, c], [a, c, d]]
    m = trimesh.Trimesh(np.array(V, float), np.array(F), process=True); m.fix_normals(); return D._fix(m)
def roof_xs(a, b, n=16):
    xs = [a, b] + [RX0 + VW * k / n for k in range(int((a - RX0) / VW * n) - 1, int((b - RX0) / VW * n) + 2)]
    return sorted(set(round(x, 6) for x in xs if a <= x <= b))

# ============================================================================ fachadas (pivo: face externa, cota do piso; parede em -Z)
def wall_core(p, holes, xs0, outer):
    xs = sorted(set(list(xs0) + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([-Y0, 0.0, HWALL] + [v for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if cy < 0: return 'concrete'
        return 'plaster' if k == 0 else outer
    for m, mesh in grid_solid(xs, ys, [-T, -0.1, 0.0], cell).items(): p.add(m, mesh)
BASE_IN = [(-T, 0.001), (-T - 0.016, 0.001), (-T - 0.016, 0.12), (-T, 0.13)]
def sill_out(p, a, b, y):
    prof_x(p, 'concrete', a, b, [(-0.1, y - 0.04), (0.06, y - 0.04), (0.07, y - 0.025), (0.07, y - 0.012), (-0.1, y + 0.005)])
def stool_in(p, a, b, y, d=0.04):
    p.cham('walnut', a, b, y - 0.03, y + 0.004, -T - d, -0.15, 0.005)
def wall(kind='plain', outer='fstone', trim=0, tamt=T):
    """Modulo de 2 m: plain, teller (janela do drive-thru com gaveta, aba e alto-falante), win (janela alta em fita), door (porta de
    servico com aba e arandela). trim -1/+1 encurta a ponta -x/+x em tamt (paredes laterais encostam por dentro)."""
    p = Piece(); xs0 = (-W / 2 + tamt * (trim < 0), W / 2 - tamt * (trim > 0)); holes = []; gaps = []
    if kind == 'teller': holes = [(-0.7, 0.7, 0.95, 2.15)]
    if kind == 'win': holes = [(-0.8, 0.8, 2.0, 3.1)]
    if kind == 'door': holes = [(-0.5, 0.5, 0.0, 2.2)]; gaps = [(-0.5, 0.5)]
    wall_core(p, holes, xs0, outer)
    if kind == 'teller':
        alu_frame(p, -0.7, 0.7, 0.95, 2.15, f=0.05, z0=-0.17, z1=-0.08, mulls=(0.0,)) if False else None
        for (a, b) in ((-0.7, -0.65), (0.65, 0.7), (-0.025, 0.025)): p.box('gold', a, b, 0.95, 2.15, -0.17, -0.06)
        p.box('gold', -0.65, 0.65, 2.1, 2.15, -0.17, -0.06); p.box('gold', -0.65, 0.65, 0.95, 1.0, -0.17, -0.06)
        p.box('glass', -0.65, -0.025, 1.0, 2.1, -0.143, -0.137); p.box('glass', 0.025, 0.65, 1.0, 2.1, -0.093, -0.087)
        p.cham('concrete', -0.85, 0.85, 0.85, 0.96, -0.06, 0.32, 0.008)
        p.box('steel', -0.3, 0.3, 0.95, 0.99, -0.08, 0.36); p.box('steel', -0.3, 0.3, 0.99, 1.08, 0.33, 0.36); p.box('steel', -0.3, -0.27, 0.99, 1.08, -0.08, 0.33); p.box('steel', 0.27, 0.3, 0.99, 1.08, -0.08, 0.33)
        p.box('dark', -0.08, 0.08, 1.02, 1.05, 0.36, 0.38)
        p.cham('teal', -0.9, 0.9, 2.25, 2.33, 0.0, 0.5, 0.01); p.box('lamp_glass', -0.7, 0.7, 2.245, 2.25, 0.15, 0.35)
        for x in (-0.85, 0.85): seg_cyl(p, 'teal', (x, 2.3, 0.48), (x, 2.75, 0.0), 0.015, 6)
        disc_z(p, 'chrome', 0.12, 0.0, 0.05, 0.92, 1.45, 24); disc_z(p, 'dark', 0.1, 0.05, 0.055, 0.92, 1.45, 24)
        for k in range(-3, 4): p.box('chrome', 0.92 - 0.09, 0.92 + 0.09, 1.45 + k * 0.025 - 0.004, 1.45 + k * 0.025 + 0.004, 0.055, 0.06)
        disc_z(p, 'red', 0.025, 0.0, 0.03, 0.92, 1.25, 12)
        stool_in(p, -0.75, 0.75, 0.95, 0.3)
    if kind == 'win':
        for (a, b) in ((-0.8, -0.75), (0.75, 0.8), (-0.02, 0.02)): p.box('gold', a, b, 2.0, 3.1, -0.17, -0.08)
        p.box('gold', -0.75, 0.75, 3.05, 3.1, -0.17, -0.08); p.box('gold', -0.75, 0.75, 2.0, 2.05, -0.17, -0.08)
        p.box('glass', -0.75, 0.75, 2.05, 3.05, -0.128, -0.122)
        sill_out(p, -0.84, 0.84, 2.0); stool_in(p, -0.82, 0.82, 2.0)
    if kind == 'door':
        p.box('steel', -0.5, -0.45, 0.0, 2.2, -0.18, -0.06); p.box('steel', 0.45, 0.5, 0.0, 2.2, -0.18, -0.06); p.box('steel', -0.45, 0.45, 2.15, 2.2, -0.18, -0.06)
        p.cham('concrete', -0.5, 0.5, -0.02, 0.008, -T + 0.004, 0.02, 0.004)
        p.cham('teal', -0.75, 0.75, 2.4, 2.48, 0.0, 0.7, 0.01)
        for x in (-0.7, 0.7): seg_cyl(p, 'teal', (x, 2.46, 0.66), (x, 3.0, 0.0), 0.015, 6)
        p.merge(wall_lamp(), tr(0.0, 2.75, 0.0) if False else tr(0.75 + 0.2, 1.95, 0.0))
    for (a, b) in segs_excl(gaps, xs0[0] + 0.001, xs0[1] - 0.001, 0.0): prof_x(p, 'trim', a, b, BASE_IN)
    return p
def glass_mod(kind='win'):
    """Modulo da fachada de vidro (pivo: face externa, cota do piso; 12 cm de fundo): montantes dourados com aletas, painel turquesa
    embaixo, travessa da bandeira, ou vao para a porta dupla de vidro com soleira de latao."""
    p = Piece(); e = 0.975; hd = HWALL
    p.box('concrete', -1.0, 1.0, -Y0, 0.0, -GT_, 0.0)
    for s in (-1, 1):
        a, b = sorted((s * e, s * 1.0)); p.box('gold', a, b, 0.0, hd, -GT_, 0.0)
        a, b = sorted((s * 0.985, s * 1.0)); p.box('gold', a, b, 0.0, hd, 0.0, 0.07)
    p.box('gold', -e, e, hd - 0.05, hd, -GT_ + 0.01, -0.01); p.box('gold', -e, e, 2.45, 2.5, -GT_ + 0.01, -0.01)
    p.box('glass', -e, e, 2.5, hd - 0.05, -0.063, -0.057)
    if kind == 'win':
        p.box('gold', -e, e, 0.0, 0.05, -GT_ + 0.01, -0.01); p.box('teal', -e, e, 0.05, 0.35, -0.09, -0.03); p.box('gold', -e, e, 0.35, 0.4, -GT_ + 0.01, -0.01)
        p.box('glass', -e, e, 0.4, 2.45, -0.063, -0.057)
    else:
        for s in (-1, 1): a, b = sorted((s * 0.9, s * e)); p.box('gold', a, b, 0.0, 2.45, -GT_, 0.0)
        p.box('brass', -0.9, 0.9, -0.01, 0.006, -GT_ + 0.004, 0.03)
    return p

# ============================================================================ clerestorio (pivo: origem, cota do piso)
def clerestory():
    """Faixa de vidro entre o topo das paredes e a casca, nas 4 fachadas: peitoril dourado, montantes a cada 1 m, postes nas quinas."""
    p = Piece(); ys = HWALL + 0.05
    LINES = [('x', -HZ, -HZ + T), ('x', HZ - GT_, HZ)]; SIDES = [(X0, X0 + T), (X1 - T, X1)]
    for (_, z0, z1) in LINES:
        p.box('gold', X0, X1, HWALL, ys, z0, z1); zc = (z0 + z1) / 2
        xs = roof_xs(X0 + 0.1, X1 - 0.1); pts = [(X0 + 0.1, ys), (X1 - 0.1, ys)] + [(x, ybot(x, zc) + 0.015) for x in xs[::-1]]
        prof_z(p, 'glass', zc - 0.006, zc + 0.006, pts)
        for x in np.arange(X0 + 1.0, X1 - 0.5, 1.0):
            p.hull('gold', [(x + a, y, z) for a in (-0.02, 0.02) for z in (zc - 0.04, zc + 0.04) for y in (ys, ybot(x + a, z) + 0.02)])
    for (x0, x1) in SIDES:
        p.box('gold', x0, x1, HWALL, ys, -HZ + T, HZ - GT_); xc = (x0 + x1) / 2
        prof_x(p, 'glass', xc - 0.006, xc + 0.006, [(-HZ + 0.15, ys), (HZ - 0.05, ys), (HZ - 0.05, ybot(xc, HZ - 0.05) + 0.015), (-HZ + 0.15, ybot(xc, -HZ + 0.15) + 0.015)])
        for z in np.arange(-HZ + 1.0, HZ - 0.5, 1.0):
            p.hull('gold', [(x, y, z + a) for a in (-0.02, 0.02) for x in (xc - 0.04, xc + 0.04) for y in (ys, ybot(x, z + a) + 0.02)])
    for (x0, x1) in SIDES:
        for (z0, z1) in ((-HZ, -HZ + T), (HZ - GT_, HZ)):
            p.hull('gold', [(x, y, z) for x in (x0, x1) for z in (z0, z1) for y in (ys, ybot(x, z) + 0.02)])
    return p

# ============================================================================ cobertura (pivo: origem, cota do piso)
def roof():
    """Cobertura de 9 cascas abobadadas de 3 m, inclinada para a frente: casca com forro, capa branca, nervuras turquesa nos vales,
    testeira turquesa com filete dourado, gargulas nos vales dos fundos e luzes redondas embutidas no forro."""
    p = Piece()
    p.add('soffit', hf_solid(roof_xs(RX0, RX1), [RZ0, RZ1], ybot, ytop))
    p.add('roofw', hf_solid(roof_xs(RX0 + 0.05, RX1 - 0.05), [RZ0 + 0.05, RZ1 - 0.05], ytop, lambda x, z: ytop(x, z) + 0.02))
    xf = roof_xs(RX0 - 0.04, RX1 + 0.04)
    for (z0, z1) in ((RZ1 - 0.05, RZ1 + 0.03), (RZ0 - 0.03, RZ0 + 0.05)):
        p.add('teal', hf_solid(xf, [z0, z1], lambda x, z: ybot(x, z) - 0.1, lambda x, z: ytop(x, z) + 0.07))
    for zz in (RZ1 + 0.03, RZ0 - 0.03):
        z0, z1 = sorted((zz, zz + (0.006 if zz > 0 else -0.006)))
        p.add('gold', hf_solid(xf, [z0, z1], lambda x, z: ybot(x, z) - 0.06, lambda x, z: ybot(x, z) - 0.03))
    for x0 in (RX0, RX1):
        a, b = (RX0 - 0.04, RX0 + 0.05) if x0 == RX0 else (RX1 - 0.05, RX1 + 0.04)
        za, zb = RZ0 + 0.05, RZ1 - 0.05
        prof_x(p, 'teal', a, b, [(za, ybot(x0, za) - 0.1), (zb, ybot(x0, zb) - 0.1), (zb, ytop(x0, zb) + 0.07), (za, ytop(x0, za) + 0.07)])
        s = 1 if x0 == RX1 else -1; xg = x0 + s * 0.04 + s * 0.003
        prof_x(p, 'gold', *sorted((xg - s * 0.003, xg + s * 0.003)), [(za, ybot(x0, za) - 0.06), (zb, ybot(x0, zb) - 0.06), (zb, ybot(x0, zb) - 0.03), (za, ybot(x0, za) - 0.03)]) if False else None
    for v in VALLEYS:
        p.add('teal_d', hf_solid([v - 0.07, v - 0.035, v, v + 0.035, v + 0.07], [RZ0 + 0.05, RZ1 - 0.05], lambda x, z: ytop(x, z) - 0.005, lambda x, z: ytop(x, z) + 0.06))
        y = ytop(v, RZ0); p.cham('teal', v - 0.09, v + 0.09, y - 0.05, y + 0.07, RZ0 - 0.45, RZ0 + 0.0, 0.01)
    for x in CRESTS:
        for z in np.arange(-6.6, 8.2, 1.6):
            if abs(z + HZ - T / 2) < 0.45 or abs(z - HZ + GT_ / 2) < 0.45 or abs(x - X0 - T / 2) < 0.45 or abs(x - X1 + T / 2) < 0.45: continue
            y = ybot(x, z); p.cyl('lamp_glass', 0.11, y - 0.012, y + 0.04, x, z, 20); ring_y(p, 'gold', 0.11, 0.15, y - 0.008, y + 0.04, x, z, 20)
    return p
def vcol(zv):
    """Coluna em V amarela (pivo: pe, no chao; abre ao longo de X): 2 escoras afiladas do pe ate os vales da casca, chapas de topo,
    sapata de aco e base de concreto."""
    p = Piece(); yt = Y0 + RH0 + RS * (zv - RZ0) - RT
    p.cyl('concrete', 0.26, 0.0, 0.3, 0, 0, 20); p.cham('paint_y', -0.14, 0.14, 0.3, 0.42, -0.16, 0.16, 0.01)
    for s in (-1, 1):
        x1 = s * VW / 2
        p.hull('paint_y', [(a, 0.36, c) for a in (-0.07, 0.07) for c in (-0.1, 0.1)] + [(x1 + a, yt + 0.04, c) for a in (-0.13, 0.13) for c in (-0.14, 0.14)])
        p.cham('paint_y', x1 - 0.22, x1 + 0.22, yt - 0.03, yt + 0.06, -0.2, 0.2, 0.008)
    return p

# ============================================================================ piso, forro da area de servico e paredes internas
XI0, XI1, ZI0, ZI1 = X0 + T, X1 - T, -HZ + T, HZ - GT_
INNER = sbox(XI0, ZI0, XI1, ZI1)
BACK = INNER.intersection(sbox(-30, -30, XB + t_ / 2, ZP + t_ / 2))
STAR_C = (-3.0, 2.6)
def checker(p, poly, y0, y1, step, ma, mb):
    b = poly.bounds
    for i in range(int(math.floor(b[0] / step)), int(math.ceil(b[2] / step))):
        for j in range(int(math.floor(b[1] / step)), int(math.ceil(b[3] / step))):
            q = sbox(i * step, j * step, (i + 1) * step, (j + 1) * step).intersection(poly)
            if q.area > 1e-6: ext_y(p, ma if (i + j) % 2 == 0 else mb, q, y0, y1)
def floor_piece():
    """Piso (pivo: origem, cota do piso): granilite em placas de 1 m com filetes de latao e estrela de 8 pontas no saguao,
    piso vinilico xadrez na gerencia e na copa, concreto polido na caixa-forte."""
    p = Piece(); ext_y(p, 'concrete', INNER, -Y0 + 0.02, -0.012)
    tiles(p, INNER.difference(BACK), -0.012, 0.0, 1.0, 'terrazzo', 0.004, 'brass', 0.5, 0.5)
    vault = BACK.intersection(sbox(-30, -30, -5.0, 30)); rest = BACK.difference(vault)
    ext_y(p, 'concrete', vault, -0.012, 0.0); checker(p, rest, -0.012, 0.0, 0.3, 'lino', 'cream')
    cx, cz = STAR_C; p.cyl('brass', 0.34, -0.006, 0.003, cx, cz, 32); p.cyl('terrazzo_t', 0.3, 0.0, 0.005, cx, cz, 32)
    for k in range(16):
        a = k * math.pi / 8; L1 = 1.3 if k % 2 == 0 else 0.75; c, s = math.cos(a), math.sin(a); w = 0.05 if k % 2 == 0 else 0.03
        p.hull('brass', [(cx + c * r + -s * q, y, cz + s * r + c * q) for (r, q) in ((0.25, -w), (0.25, w), (L1, 0.0)) for y in (-0.006, 0.001)])
    return p
def core_ceil():
    """Forro da area de servico (pivo: origem, cota do piso): laje de forro a 3 m com luminarias e filete dourado na borda."""
    p = Piece(); ext_y(p, 'ceil', BACK, 3.0, 3.01); ext_y(p, 'plaster', BACK, 3.01, 3.12)
    edge = unary_union([sbox(XI0, ZP + t_ / 2, XB + t_ / 2 + 0.02, ZP + t_ / 2 + 0.02), sbox(XB + t_ / 2, ZI0, XB + t_ / 2 + 0.02, ZP + t_ / 2 + 0.02)])
    ext_y(p, 'gold', edge, 2.96, 3.15)
    for (x, z) in ((-7.4, -4.1), (-3.0, -4.1), (2.0, -4.1)): p.box('lamp_glass', x - 0.6, x + 0.6, 2.994, 3.0, z - 0.3, z + 0.3); p.box('gold', x - 0.63, x + 0.63, 2.99, 2.994, z - 0.33, z + 0.33)
    return p
VAULT_X = -7.4; VAULT_R = 0.98; VAULT_Y = 1.08
OFFICE_DOOR = -1.6; STAFF_DOOR = 1.2
def plan():
    """Paredes internas (pivo: origem, cota do piso): parede da caixa-forte, gerencia (com visor de vidro) e copa; divisorias; cabine do
    drive-thru com visor."""
    p = Piece(); Ln = XB + t_ / 2 - XI0
    cuts = [(VAULT_X - XI0, 2.1, 0.0, 2.3, 'pass'), (-3.425 - XI0, 2.35, 0.9, 2.5, 'glaze'), (OFFICE_DOOR - XI0, 0.9, 0.0, 2.1, 'door'), (STAFF_DOOR - XI0, 0.9, 0.0, 2.1, 'door')]
    p.merge(run_wall(Ln, 3.0, cuts), tr(XI0, 0, ZP))
    for x in (-5.0, -1.0, XB): p.merge(run_wall(ZP - t_ / 2 - ZI0, 3.0), rot_y(-90, (x, 0, ZI0)))
    p.merge(run_wall(3.0 + t_ / 2 - (ZC + 0.3), 3.0, [(1.75, 2.0, 1.0, 2.4, 'glaze')]), rot_y(-90, (XB, 0, ZC + 0.3)))
    p.merge(run_wall(XI1 - XB - t_ / 2, 3.0), tr(XB + t_ / 2, 0, 3.0))
    return p

# ============================================================================ balcao, grade e caixa-forte (pivo: origem, cota do piso)
SC = [1.0, 2.15, 3.3, 4.4]
def rail_low():
    """Grade baixa de nogueira que separa o saguao da area dos funcionarios (a porta da caixa-forte fica a vista): painel com filetes dourados, capa, rodape e 2 postes."""
    p = Piece(); a, b = -6.1, -0.6
    p.box('walnut', a - 0.1, a, 0.0, 1.05, ZC - 0.07, ZC + 0.07); p.sphere('gold', 0.06, a - 0.05, 1.1, ZC, 2)
    p.box('dark', a, b, 0.0, 0.06, ZC - 0.03, ZC + 0.03); p.box('walnut', a, b, 0.06, 0.9, ZC - 0.035, ZC + 0.035)
    p.cham('gold', a - 0.05, -0.55, 0.9, 0.95, ZC - 0.06, ZC + 0.06, 0.008)
    for x in np.arange(a + 0.3, b - 0.1, 0.6):
        for z in (1, -1): p.box('gold', x - 0.01, x + 0.01, 0.12, 0.84, *sorted((ZC + z * 0.035, ZC + z * 0.04)))
    p.box('walnut', -0.6, -0.5, 0.0, 1.05, ZC - 0.07, ZC + 0.07); p.sphere('gold', 0.06, -0.55, 1.1, ZC, 2)
    return p
def gate_c(w=0.88):
    """Portinhola da grade (pivo: dobradica, embaixo)."""
    p = Piece(); p.box('walnut', 0.02, w, 0.1, 0.88, -0.03, 0.03); p.cham('gold', 0.0, w, 0.88, 0.92, -0.05, 0.05, 0.006)
    for z in (1, -1): p.box('gold', w / 2 - 0.01, w / 2 + 0.01, 0.16, 0.82, *sorted((z * 0.03, z * 0.036)))
    for y in (0.25, 0.7): p.cyl('gold', 0.012, y, y + 0.08, 0.0, 0.0, 8)
    return p
def teller_counter():
    """Balcao de 4 caixas: frente de nogueira com filetes dourados, tampo de marmore, vidro com passa-documentos em cada guiche,
    porta-canetas, apoio de pes cromado; atras, bancada de trabalho com gavetas de dinheiro, somadoras e luminarias."""
    p = Piece(); a, b = 0.4, XB - t_ / 2; zf, zb = ZC + 0.3, ZC - 0.3
    p.box('walnut', a, b, 0.1, 1.0, zb, zf); p.box('dark', a + 0.03, b, 0.0, 0.1, zb, zf - 0.06)
    for x in np.arange(a + 0.15, b - 0.05, 0.3): p.box('gold', x - 0.0125, x + 0.0125, 0.15, 0.95, zf, zf + 0.006)
    p.cham('marble', a - 0.02, b, 1.0, 1.05, zb - 0.05, zf + 0.06, 0.008)
    posts = [a + 0.02] + [(u + v) / 2 for u, v in zip(SC[:-1], SC[1:])] + [b - 0.02]
    for x in posts: p.box('gold', x - 0.02, x + 0.02, 1.05, 1.88, ZC - 0.02, ZC + 0.02)
    p.box('gold', a, b, 1.88, 1.92, ZC - 0.03, ZC + 0.03)
    for u, v in zip(posts[:-1], posts[1:]):
        p.box('glass', u + 0.02, v - 0.02, 1.2, 1.88, ZC - 0.003, ZC + 0.003); p.box('gold', u + 0.02, v - 0.02, 1.18, 1.2, ZC - 0.015, ZC + 0.015)
    for (u, v), c in zip(zip(posts[:-1], posts[1:]), SC):
        for (q0, q1) in ((u + 0.02, c - 0.18), (c + 0.18, v - 0.02)): p.box('glass', q0, q1, 1.05, 1.18, ZC - 0.003, ZC + 0.003)
        p.cyl('brass', 0.03, 1.05, 1.08, c + 0.35, zf - 0.05, 12); seg_cyl(p, 'chrome', (c + 0.35, 1.08, zf - 0.05), (c + 0.33, 1.2, zf - 0.03), 0.006, 6)
        p.cham('walnut', c - 0.25, c + 0.25, 0.55, 0.75, zb - 0.02, zb, 0.004); p.box('chrome', c - 0.06, c + 0.06, 0.64, 0.66, zb - 0.04, zb - 0.02)
        p.hull('dark', [(c - 0.3 + dx, 0.82, zb - 0.38 + dz) for dx in (0, 0.25) for dz in (0, 0.25)] + [(c - 0.3 + dx, 0.92, zb - 0.32 + dz) for dx in (0, 0.25) for dz in (0, 0.12)])
        lathe(p, 'teal', [(0.07, 0.82), (0.07, 0.84), (0.012, 0.86), (0.012, 1.15), (0.1, 1.18), (0.04, 1.28)], c + 0.25, zb - 0.3, 0.0, 12)
    p.cham('walnut', a, b, 0.78, 0.82, zb - 0.45, zb, 0.006)
    seg_cyl(p, 'chrome', (a + 0.1, 0.15, zf + 0.12), (b - 0.1, 0.15, zf + 0.12), 0.02, 8)
    for x in np.linspace(a + 0.2, b - 0.2, 5): seg_cyl(p, 'chrome', (x, 0.15, zf), (x, 0.15, zf + 0.12), 0.012, 6)
    return p
def vault_frame():
    """Marco da caixa-forte (pivo: centro do vao na parede, piso): chapa de aco com vao redondo, colar polido com parafusos dos 2 lados."""
    p = Piece(); hole = Point(0, VAULT_Y).buffer(VAULT_R, 32)
    ext(p, 'vault', sbox(-1.2, 0.0, 1.2, 2.5).difference(hole), -0.12, 0.12)
    for z in (1, -1):
        m = trimesh.creation.annulus(r_min=VAULT_R, r_max=1.18, height=0.08, sections=64); m.apply_translation([0, VAULT_Y, z * 0.16]); p.add('chrome', m)
        for k in range(24):
            a = 2 * math.pi * k / 24; x, y = 1.09 * math.cos(a), VAULT_Y + 1.09 * math.sin(a); disc_z(p, 'vault', 0.022, *sorted((z * 0.2, z * 0.215)), x, y, 8)
    return p
def vault_leaf():
    """Porta redonda da caixa-forte (pivo: dobradica, piso): disco de aco de 44 cm com face polida, volante de 4 raios, trincos,
    bracos e eixo da dobradica."""
    p = Piece(); cx, cz = 1.03, -0.3; y = VAULT_Y
    disc_z(p, 'vault', 0.94, cz - 0.22, cz + 0.22, cx, y, 64); disc_z(p, 'chrome', 0.86, cz + 0.22, cz + 0.24, cx, y, 64)
    for k in range(12):
        a = 2 * math.pi * k / 12; disc_z(p, 'chrome', 0.05, cz + 0.24, cz + 0.27, cx + 0.7 * math.cos(a), y + 0.7 * math.sin(a), 12)
    disc_z(p, 'brass', 0.1, cz + 0.24, cz + 0.36, cx, y, 20)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; seg_cyl(p, 'brass', (cx, y, cz + 0.33), (cx + 0.42 * math.cos(a), y + 0.42 * math.sin(a), cz + 0.33), 0.02, 8)
    pts = [(cx + 0.42 * math.cos(a), y + 0.42 * math.sin(a), cz + 0.33) for a in np.linspace(0, 2 * math.pi, 25)]
    for u, v in zip(pts[:-1], pts[1:]): seg_cyl(p, 'brass', u, v, 0.025, 8)
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8; c, s = math.cos(a), math.sin(a)
        seg_cyl(p, 'chrome', (cx + 0.85 * c, y + 0.85 * s, cz - 0.1), (cx + 1.0 * c, y + 1.0 * s, cz - 0.1), 0.035, 10) if False else None
    for yy in (y - 0.5, y + 0.5): p.cham('vault', -0.04, cx - 0.6, yy - 0.1, yy + 0.1, -0.08, 0.06, 0.01); p.cham('vault', cx - 0.62, cx - 0.4, yy - 0.1, yy + 0.1, cz + 0.2, 0.06, 0.01)
    p.cyl('vault', 0.08, y - 0.8, y + 0.8, 0.0, 0.0, 16)
    return p
def deposit_boxes(L1=3.2, h=2.3):
    """Cofres de aluguel (pivo: centro de tras, piso; frente +Z): estante de aco com portinhas de latao, fechaduras duplas e dobradicas."""
    p = Piece(); x = L1 / 2; p.box('vault', -x, x, 0.0, h, 0.0, 0.45); p.box('dark', -x + 0.02, x - 0.02, 0.0, 0.12, 0.45, 0.46) if False else None
    nx = int(round(L1 / 0.27)); ny = 13
    for i in range(nx):
        for j in range(ny):
            a = -x + 0.02 + i * (L1 - 0.04) / nx + 0.008; b = -x + 0.02 + (i + 1) * (L1 - 0.04) / nx - 0.008
            y0 = 0.15 + j * (h - 0.2) / ny + 0.008; y1 = 0.15 + (j + 1) * (h - 0.2) / ny - 0.008
            p.box('brass', a, b, y0, y1, 0.45, 0.46)
            for xx in ((a + b) / 2 - 0.04, (a + b) / 2 + 0.04): p.box('dark', xx - 0.008, xx + 0.008, (y0 + y1) / 2 - 0.015, (y0 + y1) / 2 + 0.015, 0.46, 0.464)
    return p
def cash_cart():
    p = Piece(); p.cham('steel', -0.45, 0.45, 0.25, 0.3, -0.3, 0.3, 0.01); p.cham('steel', -0.45, 0.45, 0.75, 0.8, -0.3, 0.3, 0.01)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        p.box('steel', sx * 0.42 - 0.02, sx * 0.42 + 0.02, 0.12, 0.85, sz * 0.27 - 0.02, sz * 0.27 + 0.02)
        c = trimesh.creation.cylinder(radius=0.06, height=0.04, sections=12); c.apply_transform(rot_y(90)); c.apply_translation([sx * 0.42, 0.06, sz * 0.27]); p.add('rubber', c)
    seg_cyl(p, 'chrome', (-0.45, 0.95, -0.3), (-0.45, 0.95, 0.3), 0.015, 6)
    for (x, z) in ((-0.42, -0.27), (-0.42, 0.27)): seg_cyl(p, 'chrome', (x, 0.85, z), (-0.45, 0.95, z), 0.012, 6)
    rng = np.random.default_rng(5)
    for (x, z, y) in ((-0.2, -0.1, 0.3), (0.15, 0.1, 0.3), (0.0, 0.0, 0.8), (0.25, -0.12, 0.8)):
        pts = [(x + rng.uniform(-0.16, 0.16), y + rng.uniform(0.0, 0.32), z + rng.uniform(-0.13, 0.13)) for _ in range(24)]
        p.hull('fabric', pts); p.cyl('dark', 0.03, max(q[1] for q in pts) - 0.03, max(q[1] for q in pts) + 0.03, x, z, 8)
    return p
def safe_box():
    p = Piece(); p.cham('dark', -0.35, 0.35, 0.0, 0.9, 0.0, 0.6, 0.02); p.box('steel', -0.3, 0.3, 0.1, 0.8, 0.6, 0.61)
    c = trimesh.creation.cylinder(radius=0.08, height=0.03, sections=16); c.apply_translation([0, 0.5, 0.625]); p.add('chrome', c)
    p.box('chrome', 0.15, 0.2, 0.3, 0.55, 0.61, 0.64); return p

# ============================================================================ moveis (pivo: centro de tras ou centro, piso; frente +Z)
def hairpin(p, x, z, y0, y1, d=0.06, mat='chrome'):
    seg_cyl(p, mat, (x - d, y0, z), (x, y1, z), 0.008, 6); seg_cyl(p, mat, (x + d, y0, z), (x, y1, z), 0.008, 6)
def check_desk():
    """Mesa de preencher em bumerangue (pivo: centro, piso): tampo de formica creme com borda dourada, 2 pedestais turquesa afilados
    com base cromada, bandeja de formularios em branco e 4 canetas em suportes de latao."""
    p = Piece(); line = LineString([(-0.8, 0.12), (-0.4, -0.06), (0.0, -0.12), (0.4, -0.06), (0.8, 0.12)]); top = line.buffer(0.27, 24)
    ext_y(p, 'cream', top, 1.0, 1.04); ext_y(p, 'gold', top.buffer(0.015, 24).difference(top), 0.995, 1.045); ext_y(p, 'walnut', top.buffer(-0.08, 24), 0.96, 1.0)
    for x in (-0.5, 0.5):
        z = -0.06 if abs(x) < 0.6 else 0.12
        p.hull('teal', [(x + a, 0.04, -0.08 + c) for a in (-0.18, 0.18) for c in (-0.1, 0.1)] + [(x + a, 0.96, -0.08 + c) for a in (-0.07, 0.07) for c in (-0.05, 0.05)])
        p.cham('chrome', x - 0.22, x + 0.22, 0.0, 0.04, -0.21, 0.05, 0.01)
    p.box('gold', -0.25, 0.25, 1.04, 1.07, -0.25, -0.05); p.box('paper', -0.23, 0.23, 1.05, 1.072, -0.23, -0.07)
    for x in (-0.65, -0.35, 0.35, 0.65):
        z = 0.12 if abs(x) > 0.5 else -0.02
        p.cyl('brass', 0.03, 1.04, 1.07, x, z + 0.08, 12); seg_cyl(p, 'chrome', (x, 1.07, z + 0.08), (x + 0.05, 1.2, z + 0.1), 0.006, 6)
    return p
def sofa(L1=2.2):
    """Sofa baixo (pivo: centro de tras, piso): estrutura de nogueira, pes afilados, 3 almofadas de assento e de encosto turquesa."""
    p = Piece(); x = L1 / 2
    p.cham('walnut', -x, x, 0.18, 0.28, 0.0, 0.8, 0.01)
    for (xx, zz) in ((-x + 0.1, 0.1), (x - 0.1, 0.1), (-x + 0.1, 0.7), (x - 0.1, 0.7)): seg_cyl(p, 'walnut', (xx * 1.03, 0.0, zz + (0.04 if zz > 0.5 else -0.04)), (xx, 0.18, zz), 0.02, 8)
    n = 3; w = (L1 - 0.3) / n
    for i in range(n):
        a = -x + 0.15 + i * w
        p.cham('vinyl_t', a + 0.005, a + w - 0.005, 0.28, 0.43, 0.15, 0.78, 0.04); p.cham('vinyl_t', a + 0.005, a + w - 0.005, 0.32, 0.78, 0.02, 0.17, 0.04)
        for k in (0.35, 0.65): p.sphere('teal_d', 0.012, a + w * k, 0.6, 0.172, 0)
    for s in (-1, 1): p.cham('walnut', *sorted((s * x, s * (x - 0.15))), 0.28, 0.6, 0.0, 0.8, 0.01)
    return p
def tulip_chair():
    """Poltrona tulipa (pivo: centro, piso; frente +Z): pe de taca branco, concha laranja com almofada."""
    p = Piece(); lathe(p, 'paint_w', [(0.26, 0.0), (0.26, 0.02), (0.06, 0.1), (0.035, 0.3), (0.06, 0.4), (0.18, 0.45)], sec=24)
    pts = []
    for k in range(24):
        a = 2 * math.pi * k / 24; c, s = math.cos(a), math.sin(a); back = max(0.0, -s)
        for (r, y) in ((0.24, 0.45), (0.34, 0.6 + 0.35 * back ** 1.5)): pts.append((r * c, y, r * s * 0.95))
    p.hull('vinyl_o', pts); p.cham('vinyl_t', -0.24, 0.24, 0.58, 0.66, -0.2, 0.24, 0.04)
    return p
def coffee_table():
    """Mesa de centro em rim (pivo: centro, piso): tampo de nogueira com borda, pes de grampo cromados, cinzeiro e revistas."""
    p = Piece(); top = LineString([(-0.5, -0.1), (0.0, 0.05), (0.5, -0.1)]).buffer(0.3, 24)
    ext_y(p, 'walnut', top, 0.38, 0.42); ext_y(p, 'dkwood', top.buffer(0.012, 24).difference(top), 0.38, 0.42)
    for (x, z) in ((-0.55, -0.1), (0.55, -0.1), (0.0, 0.25)): hairpin(p, x, z, 0.0, 0.38)
    lathe(p, 'glass', [(0.0, 0.42), (0.09, 0.42), (0.1, 0.46), (0.07, 0.445), (0.0, 0.44)], -0.25, 0.0, 0.0, 16)
    p.box('paper', 0.1, 0.38, 0.42, 0.43, -0.12, 0.08); p.box('red', 0.12, 0.4, 0.43, 0.437, -0.1, 0.1)
    return p
def sputnik(drop=1.2):
    """Lustre sputnik (pivo: ponto no forro): canopla e haste dourada, bola de latao com 16 bracos e lampadas."""
    p = Piece(); p.cyl('gold', 0.08, -0.03, 0.02, 0, 0, 16); seg_cyl(p, 'gold', (0, 0.0, 0), (0, -drop, 0), 0.01, 6)
    yc = -drop - 0.12; p.sphere('brass', 0.12, 0, yc, 0, 2)
    for k in range(16):
        g = math.acos(1 - 2 * (k + 0.5) / 16); a = k * 2.39996; d = np.array([math.sin(g) * math.cos(a), math.cos(g), math.sin(g) * math.sin(a)])
        q0 = np.array([0, yc, 0]) + d * 0.1; q1 = np.array([0, yc, 0]) + d * 0.55
        seg_cyl(p, 'gold', q0, q1, 0.007, 5); p.sphere('lamp_glass', 0.035, *q1, 1)
    return p
def star_clock(r=0.55):
    """Relogio-estrela de parede sem numeros (pivo: face da parede, centro): 12 raios dourados, aro de nogueira, mostrador e ponteiros."""
    p = Piece()
    for k in range(12):
        a = k * math.pi / 6; L1 = r if k % 3 == 0 else r * 0.72; c, s = math.cos(a), math.sin(a); w = 0.025
        p.hull('gold', [(c * rr - s * q, s * rr + c * q, z) for (rr, q) in ((0.14, -w), (0.14, w), (L1, 0.0)) for z in (0.003, 0.033)])
        p.sphere('brass', 0.025, c * L1, s * L1, 0.03, 1)
    disc_z(p, 'walnut', 0.17, 0.0, 0.05, 0, 0, 32); disc_z(p, 'cream', 0.14, 0.05, 0.055, 0, 0, 32)
    for (a, l) in ((math.radians(300), 0.08), (math.radians(60), 0.12)): seg_cyl(p, 'dark', (0, 0, 0.06), (l * math.sin(a), l * math.cos(a), 0.06), 0.006, 4)
    return p
def planter_bowl():
    """Vaso de cuia turquesa sobre 3 pes de grampo, com espadas-de-sao-jorge (pivo: centro, piso)."""
    p = Piece(); lathe(p, 'teal', [(0.12, 0.35), (0.36, 0.5), (0.4, 0.65), (0.38, 0.66), (0.0, 0.66)], sec=24)
    for k in range(3):
        a = k * 2 * math.pi / 3; seg_cyl(p, 'dark', (0.32 * math.cos(a), 0.0, 0.32 * math.sin(a)), (0.2 * math.cos(a), 0.45, 0.2 * math.sin(a)), 0.012, 6)
    p.cyl('mulch', 0.36, 0.64, 0.67, 0, 0, 24); rng = np.random.default_rng(4)
    for _ in range(11):
        a = rng.uniform(0, 6.28); d = rng.uniform(0, 0.2); x, z = d * math.cos(a), d * math.sin(a); h = rng.uniform(0.5, 0.9); t = rng.uniform(0, 6.28)
        lean = rng.uniform(0.0, 0.12); ux, uz = math.cos(t), math.sin(t)
        p.hull('leaf', [(x - uz * 0.04, 0.66, z + ux * 0.04), (x + uz * 0.04, 0.66, z - ux * 0.04), (x + ux * lean, 0.66 + h, z + uz * lean), (x + ux * 0.01, 0.66, z + uz * 0.01)])
    return p
def queue_posts(L1=3.0):
    """Organizador de fila (pivo: inicio, piso; ao longo de +X): 4 pedestais cromados com base pesada e cordao vermelho."""
    p = Piece(); xs = np.linspace(0, L1, 4)
    for x in xs:
        p.cyl('chrome', 0.16, 0.0, 0.03, x, 0, 20); p.cyl('chrome', 0.03, 0.03, 0.92, x, 0, 10); p.sphere('chrome', 0.045, x, 0.95, 0, 1)
    for u, v in zip(xs[:-1], xs[1:]):
        pts = [(u + (v - u) * t, 0.88 - 0.16 * math.sin(math.pi * t), 0.0) for t in np.linspace(0.02, 0.98, 9)]
        for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'red', a, b, 0.018, 6)
    return p
def brochure_rack():
    p = Piece(); p.cyl('chrome', 0.2, 0.0, 0.02, 0, 0, 16); seg_cyl(p, 'chrome', (0, 0.02, 0), (0, 1.4, 0), 0.015, 6)
    for (y, m) in ((0.8, 'red'), (1.0, 'sign_w'), (1.2, 'teal')):
        p.box('chrome', -0.22, 0.22, y - 0.01, y, -0.05, 0.08); p.box(m, -0.2, 0.2, y, y + 0.18, 0.0, 0.03)
        seg_cyl(p, 'chrome', (-0.22, y + 0.05, 0.08), (0.22, y + 0.05, 0.08), 0.004, 4)
    return p
def exec_desk():
    """Mesa do gerente (pivo: centro de tras, piso; frente +Z): tampo de nogueira com borda, gaveteiro, pes de grampo, luminaria
    atomica, mata-borrao, telefone e porta-canetas."""
    p = Piece(); p.cham('walnut', -0.85, 0.85, 0.72, 0.77, 0.0, 0.85, 0.01)
    p.box('walnut', 0.35, 0.8, 0.1, 0.72, 0.05, 0.8)
    for y in (0.15, 0.35, 0.55): p.box('dkwood', 0.37, 0.78, y, y + 0.16, 0.8, 0.81); p.box('gold', 0.52, 0.63, y + 0.07, y + 0.09, 0.81, 0.825)
    for (x, z) in ((-0.78, 0.08), (-0.78, 0.77)): hairpin(p, x, z, 0.0, 0.72, mat='dark')
    p.box('dkwood', -0.82, 0.33, 0.45, 0.72, 0.0, 0.02)
    p.box('vinyl_g', -0.3, 0.3, 0.77, 0.775, 0.35, 0.75); p.hull('dark', [(-0.7 + dx, 0.77, 0.25 + dz) for dx in (0, 0.22) for dz in (0, 0.2)] + [(-0.68 + dx, 0.86, 0.29 + dz) for dx in (0, 0.18) for dz in (0, 0.1)])
    lathe(p, 'teal', [(0.08, 0.77), (0.015, 0.8), (0.015, 1.15), (0.14, 1.12), (0.18, 1.06), (0.0, 1.2)], 0.6, 0.2, 0.0, 14)
    p.cyl('brass', 0.04, 0.77, 0.87, 0.35, 0.6, 12)
    return p
def office_chair():
    """Cadeira giratoria (pivo: centro, piso; frente +Z): base de 5 pes cromada, assento e encosto turquesa."""
    p = Piece()
    for k in range(5):
        a = k * 2 * math.pi / 5; seg_cyl(p, 'chrome', (0, 0.08, 0), (0.3 * math.cos(a), 0.05, 0.3 * math.sin(a)), 0.018, 6); p.sphere('rubber', 0.03, 0.3 * math.cos(a), 0.03, 0.3 * math.sin(a), 1)
    seg_cyl(p, 'chrome', (0, 0.06, 0), (0, 0.44, 0), 0.025, 8)
    p.cham('vinyl_t', -0.24, 0.24, 0.44, 0.52, -0.22, 0.24, 0.03); p.cham('vinyl_t', -0.22, 0.22, 0.6, 0.95, -0.26, -0.2, 0.03)
    seg_cyl(p, 'chrome', (0, 0.45, -0.18), (0, 0.65, -0.23), 0.015, 6)
    return p
def shell_chair():
    """Cadeira de concha moldada laranja sobre pes de arame (pivo: centro, piso; frente +Z)."""
    p = Piece(); pts = []
    for k in range(20):
        a = 2 * math.pi * k / 20; c, s = math.cos(a), math.sin(a); back = max(0.0, -s)
        for (r, y) in ((0.18, 0.43), (0.24, 0.47 + 0.4 * back ** 1.3)): pts.append((r * c, y, r * s))
    p.hull('vinyl_o', pts)
    for (x, z) in ((-0.18, -0.16), (0.18, -0.16), (-0.18, 0.16), (0.18, 0.16)): seg_cyl(p, 'dark', (x, 0.0, z), (x * 0.4, 0.43, z * 0.4), 0.008, 5)
    seg_cyl(p, 'dark', (-0.18, 0.12, -0.16), (0.18, 0.12, 0.16), 0.005, 4); seg_cyl(p, 'dark', (0.18, 0.12, -0.16), (-0.18, 0.12, 0.16), 0.005, 4)
    return p
def table_round(r=0.5):
    p = Piece(); p.cyl('chrome', 0.25, 0.0, 0.03, 0, 0, 20); seg_cyl(p, 'chrome', (0, 0.03, 0), (0, 0.72, 0), 0.04, 10)
    p.cyl('cream', r, 0.72, 0.75, 0, 0, 32); ring_y(p, 'chrome', r, r + 0.012, 0.715, 0.755, 0, 0, 32)
    return p
def kitchenette(L1=2.4):
    """Copa (pivo: centro de tras, piso; frente +Z): armarios de nogueira, tampo creme com pia cromada, cafeteira, canecas, armario
    alto e geladeira arredondada branca."""
    p = Piece(); x = L1 / 2
    p.box('walnut', -x, x - 0.8, 0.1, 0.88, 0.0, 0.58); p.box('dark', -x + 0.03, x - 0.83, 0.0, 0.1, 0.0, 0.52); p.cham('cream', -x, x - 0.78, 0.88, 0.92, 0.0, 0.62, 0.006)
    for i in range(3):
        a = -x + 0.02 + i * (L1 - 0.82) / 3; b = a + (L1 - 0.82) / 3 - 0.02; p.box('dkwood', a, b, 0.14, 0.84, 0.58, 0.59); p.box('gold', (a + b) / 2 - 0.05, (a + b) / 2 + 0.05, 0.75, 0.77, 0.59, 0.6)
    p.box('chrome', -0.5, -0.1, 0.9, 0.922, 0.12, 0.48); seg_cyl(p, 'chrome', (-0.3, 0.92, 0.08), (-0.3, 1.15, 0.08), 0.012, 6); seg_cyl(p, 'chrome', (-0.3, 1.15, 0.08), (-0.3, 1.13, 0.24), 0.012, 6)
    lathe(p, 'chrome', [(0.08, 0.92), (0.08, 1.18), (0.05, 1.22), (0.02, 1.26)], 0.15, 0.3, 0.0, 14)
    for xx in (0.32, 0.42): p.cyl('porcelain', 0.035, 0.92, 1.01, xx, 0.42, 10)
    p.box('walnut', -x, x - 0.8, 1.5, 2.2, 0.0, 0.35)
    lathe(p, 'paint_w', [(0.0, 0.0), (0.36, 0.0), (0.37, 0.05), (0.37, 1.55), (0.33, 1.7), (0.0, 1.72)], x - 0.39, 0.37, 0.0, 28)
    p.box('chrome', x - 0.12, x - 0.09, 0.9, 1.3, 0.72, 0.76)
    return p
def booth_desk():
    """Bancada do caixa do drive-thru (pivo: centro de tras, piso; frente +Z): tampo de nogueira, gavetas de dinheiro, microfone,
    terminal do tubo pneumatico e somadora."""
    p = Piece(); p.cham('walnut', -0.8, 0.8, 0.86, 0.9, 0.3, 0.9, 0.008); p.box('walnut', -0.8, -0.45, 0.1, 0.86, 0.32, 0.88); p.box('walnut', 0.45, 0.8, 0.1, 0.86, 0.32, 0.88)
    for xx in (-0.8, 0.45):
        for y in (0.2, 0.5): p.box('dkwood', xx + 0.02, xx + 0.33, y, y + 0.26, 0.88, 0.89)
    p.cyl('chrome', 0.06, 0.9, 0.92, -0.2, 0.5, 12); seg_cyl(p, 'chrome', (-0.2, 0.92, 0.5), (-0.2, 1.15, 0.45), 0.006, 6); p.sphere('dark', 0.03, -0.2, 1.17, 0.44, 1)
    p.cham('teal', 0.15, 0.55, 0.9, 1.2, 0.3, 0.62, 0.02); p.cyl('chrome', 0.07, 1.2, 1.45, 0.35, 0.46, 16)
    p.hull('dark', [(-0.6 + dx, 0.9, 0.5 + dz) for dx in (0, 0.25) for dz in (0, 0.25)] + [(-0.6 + dx, 1.0, 0.56 + dz) for dx in (0, 0.25) for dz in (0, 0.12)])
    return p
def lockers(L1=1.8, rows=3):
    p = Piece(); x = L1 / 2; h = 1.95; n = int(round(L1 / 0.45))
    p.box('steel', -x, x, 0.1, h, 0.0, 0.48); p.box('dark', -x + 0.02, x - 0.02, 0.0, 0.1, 0.0, 0.44); p.cham('steel', -x - 0.01, x + 0.01, h, h + 0.04, 0.0, 0.5, 0.005)
    for i in range(n):
        for j in range(rows):
            a = -x + i * L1 / n + 0.012; b = -x + (i + 1) * L1 / n - 0.012; y0 = 0.12 + j * (h - 0.14) / rows + 0.01; y1 = 0.12 + (j + 1) * (h - 0.14) / rows - 0.01
            p.box('vinyl_t', a, b, y0, y1, 0.48, 0.49)
            for k in range(4): yy = y1 - 0.08 - k * 0.035; p.box('dark', a + 0.08, b - 0.08, yy, yy + 0.012, 0.49, 0.494)
            p.box('chrome', b - 0.07, b - 0.04, (y0 + y1) / 2 - 0.05, (y0 + y1) / 2 + 0.05, 0.49, 0.51)
    return p

# ============================================================================ drive-thru e fora (pivo: chao, salvo indicacao)
def vcol(xp, zp, along='x'):
    """Coluna em V amarela (pivo: pe, no chao): 2 escoras afiladas do pe ate a casca (vales quando abre em X), chapas de topo
    inclinadas como o forro, sapata de aco e base de concreto."""
    p = Piece(); p.cyl('concrete', 0.26, 0.0, 0.3, 0, 0, 20); p.cham('paint_y', -0.14, 0.14, 0.3, 0.42, -0.16, 0.16, 0.01)
    for s in (-1, 1):
        dx, dz = (s * VW / 2, 0.0) if along == 'x' else (0.0, s * VW / 2)
        yt = lambda a, c: Y0 + ybot(xp + dx + a, zp + dz + c)
        p.hull('paint_y', [(a, 0.36, c) for a in (-0.07, 0.07) for c in (-0.1, 0.1)] + [(dx + a, yt(a, c) + 0.04, dz + c) for a in (-0.13, 0.13) for c in (-0.14, 0.14)])
        p.hull('paint_y', [(dx + a, yt(a, c) + d, dz + c) for a in (-0.22, 0.22) for c in (-0.2, 0.2) for d in (-0.035, 0.06)])
    return p
def tube_kiosk():
    """Terminal do tubo pneumatico na ilha (pivo: chao; frente +Z): pedestal turquesa afilado, cabeca com porta do cartucho, alto-falante,
    botao, aba com luz e o tubo que sobe para a cobertura."""
    p = Piece(); p.cham('concrete', -0.35, 0.35, 0.0, 0.08, -0.3, 0.3, 0.01)
    p.hull('teal', [(a, 0.08, c) for a in (-0.25, 0.25) for c in (-0.2, 0.2)] + [(a, 1.0, c) for a in (-0.18, 0.18) for c in (-0.15, 0.15)])
    p.cham('teal', -0.3, 0.3, 1.0, 1.6, -0.22, 0.3, 0.02); p.cham('teal_d', -0.36, 0.36, 1.6, 1.68, -0.26, 0.5, 0.01); p.box('lamp_glass', -0.3, 0.3, 1.596, 1.6, 0.32, 0.46)
    disc_z(p, 'chrome', 0.13, 0.3, 0.33, 0.0, 1.28, 24); disc_z(p, 'dark', 0.1, 0.33, 0.335, 0.0, 1.28, 24); p.box('chrome', -0.05, 0.05, 1.12, 1.15, 0.33, 0.36)
    for k in range(-3, 4): p.box('chrome', -0.22, -0.12, 1.46 + k * 0.018 - 0.004, 1.46 + k * 0.018 + 0.004, 0.3, 0.31)
    disc_z(p, 'red', 0.025, 0.3, 0.33, 0.17, 1.46, 12)
    p.cyl('chrome', 0.06, 1.68, 1.75, 0.0, 0.0, 14)
    return p
TUBE_Z = 1.35; KIOSK = (12.1, TUBE_Z); TERM = (7.29, TUBE_Z); TUBE_Y = 3.3
def tube_run():
    """Tubo pneumatico (pivo: origem, cota do piso): sobe do terminal da ilha, corre sob a casca com tirantes, atravessa a parede de
    pedra e desce ate a bancada do caixa."""
    p = Piece(); r = 0.05
    pts = [(KIOSK[0], 1.75, KIOSK[1]), (KIOSK[0], TUBE_Y, KIOSK[1]), (TERM[0], TUBE_Y, TERM[1]), (TERM[0], 1.45, TERM[1])]
    for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', a, b, r, 14)
    for q in pts[1:3]: p.sphere('chrome', r, *q, 2)
    for x in np.arange(TERM[0] + 1.6, KIOSK[0] - 0.3, 1.5):
        if abs(x - X1) < 0.4: continue
        seg_cyl(p, 'steel', (x, TUBE_Y, TUBE_Z), (x, ybot(x, TUBE_Z) + 0.03, TUBE_Z), 0.008, 5); ring_y(p, 'steel', r, r + 0.012, TUBE_Y - 0.03, TUBE_Y + 0.03, x, TUBE_Z, 14) if False else None
    for x in (X1 + 0.02, X1 - T - 0.02): p.add('steel', trimesh.creation.annulus(r_min=r, r_max=r + 0.03, height=0.02, sections=16, transform=rot_y(90, (x, TUBE_Y, TUBE_Z))))
    return p
def bollard_y():
    p = Piece(); lathe(p, 'paint_y', [(0.11, -0.2), (0.11, 0.95), (0.08, 1.02), (0.0, 1.05)], sec=16)
    for y in (0.7, 0.8): lathe(p, 'dark', [(0.112, y), (0.112, y + 0.05)], sec=16)
    return p
def totem():
    """Totem da agencia sem texto (pivo: chao): canteiro de pedra, lamina turquesa afilada, caixa luminosa com pictograma de moedas e
    estrela, aleta em bumerangue amarela e estrela atomica no topo com 3 orbitas."""
    p = Piece(); p.box('fstone', -0.8, 0.8, 0.0, 0.5, -0.4, 0.4); p.cham('concrete', -0.85, 0.85, 0.5, 0.56, -0.45, 0.45, 0.01); p.box('mulch', -0.75, 0.75, 0.5, 0.58, -0.35, 0.35)
    p.hull('teal', [(a, 0.56, c) for a in (-0.45, 0.45) for c in (-0.18, 0.18)] + [(a, 6.6, c) for a in (-0.25, 0.25) for c in (-0.12, 0.12)])
    p.cham('gold', -1.0, 1.0, 3.0, 4.3, -0.24, 0.24, 0.02); p.cham('sign_w', -0.94, 0.94, 3.06, 4.24, -0.25, 0.25, 0.015)
    for z in (1, -1):
        zz = sorted((z * 0.25, z * 0.262))
        for k in range(3):
            p.box('paint_y', -0.67, -0.03, 3.3 + k * 0.17, 3.44 + k * 0.17, *zz); p.box('gold', -0.672, -0.028, 3.42 + k * 0.17, 3.445 + k * 0.17, zz[0] - 0.002 * (z < 0), zz[1] + 0.002 * (z > 0))
        for k in range(10):
            a = math.pi / 2 + k * math.pi / 5; rr = 0.3 if k % 2 == 0 else 0.13
            b_ = math.pi / 2 + (k + 1) * math.pi / 5; r2 = 0.3 if (k + 1) % 2 == 0 else 0.13
            p.hull('teal', [(0.5, 3.65, z * 0.256), (0.5 + rr * math.cos(a), 3.65 + rr * math.sin(a), z * 0.256), (0.5 + r2 * math.cos(b_), 3.65 + r2 * math.sin(b_), z * 0.256), (0.5, 3.65, z * 0.262)])
    for x in (-0.97, 0.97): p.box('lamp_glass', x - 0.015, x + 0.015, 3.06, 4.24, -0.2, 0.2)
    p.hull('paint_y', [(-1.4, 5.2, c) for c in (-0.04, 0.04)] + [(1.3, 5.9, c) for c in (-0.04, 0.04)] + [(0.2, 5.0, c) for c in (-0.04, 0.04)] + [(0.0, 5.75, c) for c in (-0.04, 0.04)])
    yc = 7.25; seg_cyl(p, 'gold', (0, 6.6, 0), (0, yc, 0), 0.04, 10); p.sphere('brass', 0.16, 0, yc, 0, 2)
    for k in range(12):
        g = math.acos(1 - 2 * (k + 0.5) / 12); a = k * 2.39996; d = np.array([math.sin(g) * math.cos(a), math.cos(g), math.sin(g) * math.sin(a)])
        q1 = np.array([0, yc, 0]) + d * 0.75; seg_cyl(p, 'gold', np.array([0, yc, 0]) + d * 0.14, q1, 0.012, 5); p.sphere('paint_y', 0.05, *q1, 1)
    for (ax, ang) in (((1, 0, 0), 0.0), ((1, 0, 0), 60.0), ((1, 0, 0), -60.0)):
        R = trimesh.transformations.rotation_matrix(math.radians(ang), [0, 1, 0]) @ trimesh.transformations.rotation_matrix(math.radians(70), [1, 0, 0])
        pts = [(R @ np.array([0.45 * math.cos(t), 0.45 * math.sin(t) * 0.45, 0.0, 1.0]))[:3] + np.array([0, yc, 0]) for t in np.linspace(0, 2 * math.pi, 25)]
        for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'chrome', a, b, 0.012, 5)
    return p
def disc_lamp():
    """Luminaria de cogumelo (pivo: chao): haste turquesa e disco com luz embaixo."""
    p = Piece(); lathe(p, 'teal', [(0.12, -0.2), (0.12, 0.1), (0.05, 0.2), (0.035, 2.4)], sec=14)
    lathe(p, 'teal', [(0.04, 2.4), (0.45, 2.48), (0.46, 2.52), (0.2, 2.58), (0.0, 2.6)], sec=28); p.cyl('lamp_glass', 0.3, 2.43, 2.46, 0, 0, 24)
    return p
def palm(h=6.5, seed=1, lean=(0.6, 0.2)):
    """Palmeira (pivo: chao): tronco curvo em aneis, 10 folhas arqueadas e cocos."""
    p = Piece(); rng = np.random.default_rng(seed); n = 14
    P = [np.array([lean[0] * (t ** 1.6), h * t, lean[1] * (t ** 1.6)]) for t in np.linspace(0, 1, n + 1)]
    for k, (a, b) in enumerate(zip(P[:-1], P[1:])):
        r0 = 0.2 - 0.07 * k / n; r1 = 0.2 - 0.07 * (k + 1) / n
        p.hull('bark', [a + np.array([r0 * math.cos(t), -0.2 if k == 0 else 0.0, r0 * math.sin(t)]) for t in np.linspace(0, 6.28, 10, endpoint=False)] +
               [b + np.array([(r1 + 0.02) * math.cos(t), -0.03, (r1 + 0.02) * math.sin(t)]) for t in np.linspace(0, 6.28, 10, endpoint=False)])
    top = P[-1]
    for k in range(10):
        a = k * 2 * math.pi / 10 + rng.uniform(-0.2, 0.2); d = np.array([math.cos(a), 0.0, math.sin(a)]); side = np.array([-d[2], 0.0, d[0]])
        L1 = rng.uniform(2.2, 2.8); pts = [top + d * L1 * t + np.array([0, 0.6 * math.sin(math.pi * t * 0.8) - 1.2 * t * t, 0]) for t in np.linspace(0, 1, 7)]
        for i, (u, v) in enumerate(zip(pts[:-1], pts[1:])):
            w0 = 0.3 * math.sin(math.pi * (i + 0.3) / 7) + 0.03; w1 = 0.3 * math.sin(math.pi * (i + 1.3) / 7) + 0.03
            p.hull('palm', [u - side * w0, u + side * w0, v - side * w1, v + side * w1, (u + v) / 2 + np.array([0, 0.03, 0])])
    for k in range(4): a = k * 1.6; p.sphere('dkwood', 0.09, top[0] + 0.15 * math.cos(a), top[1] - 0.15, top[2] + 0.15 * math.sin(a), 1)
    return p
def yucca(seed=2, h=0.9):
    p = Piece(); rng = np.random.default_rng(seed)
    for _ in range(22):
        a = rng.uniform(0, 6.28); e = rng.uniform(0.3, 1.3); L1 = h * rng.uniform(0.7, 1.0); d = np.array([math.cos(a) * math.cos(e), math.sin(e), math.sin(a) * math.cos(e)])
        side = np.array([-math.sin(a), 0, math.cos(a)]) * 0.03; b = d * L1
        p.hull('yucca', [side, -side, b, np.array([0, -0.02, 0])])
    return p
def boulder(r=0.45, seed=3):
    p = Piece(); rng = np.random.default_rng(seed)
    pts = [(r * rng.uniform(0.6, 1.0) * math.cos(a) * math.cos(e), r * 0.7 * rng.uniform(0.6, 1.0) * math.sin(e) + r * 0.25, r * rng.uniform(0.6, 1.0) * math.sin(a) * math.cos(e))
           for a in np.linspace(0, 6.28, 9, endpoint=False) for e in (-0.3, 0.4, 1.1)]
    p.hull('boulder', pts); return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('leaf', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('leaf2', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def tree(h=6.0, r=1.9, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.18, -0.2), (0.13, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    return p
def night_drop():
    """Cofre noturno na parede de pedra (pivo: face da parede, centro embaixo; frente +Z): moldura turquesa, gaveta basculante de aco."""
    p = Piece(); p.cham('teal', -0.35, 0.35, 0.9, 1.6, 0.0, 0.06, 0.01); p.cham('chrome', -0.25, 0.25, 1.05, 1.35, 0.06, 0.1, 0.01)
    p.box('dark', -0.2, 0.2, 1.3, 1.32, 0.1, 0.104); seg_cyl(p, 'chrome', (-0.12, 1.15, 0.1), (0.12, 1.15, 0.1), 0.012, 6) if False else p.box('chrome', -0.12, 0.12, 1.12, 1.16, 0.1, 0.14)
    disc_z(p, 'brass', 0.03, 0.06, 0.09, 0.0, 1.48, 12)
    return p
def planter_box(L1=1.4):
    p = Piece(); x = L1 / 2; p.cham('concrete', -x, x, 0.0, 0.55, -0.35, 0.35, 0.02); p.box('mulch', -x + 0.06, x - 0.06, 0.5, 0.56, -0.29, 0.29)
    rng = np.random.default_rng(int(L1 * 10))
    for _ in range(7): p.sphere('leaf2', rng.uniform(0.15, 0.25), rng.uniform(-x + 0.2, x - 0.2), 0.62 + rng.uniform(0, 0.15), rng.uniform(-0.15, 0.15), 1)
    return p
def trash_bin():
    p = Piece(); lathe(p, 'teal', [(0.2, 0.0), (0.24, 0.85), (0.25, 0.88), (0.08, 0.98), (0.0, 1.0)], sec=16); p.box('dark', -0.1, 0.1, 0.8, 0.9, 0.22, 0.25); return p

# ============================================================================ terreno (pivo: origem)
SX0, SX1, SZ0, SZ1 = -26.0, 20.0, -16.0, 18.0
GY = -0.2
OUTL = sbox(X0, -HZ, X1, HZ)
APRON = unary_union([sbox(-12.0, -7.4, 8.6, 8.6), sbox(-2.6, 8.6, 0.6, 12.0)]).difference(OUTL)
ISLAND = sbox(11.6, -3.0, 12.6, 4.0); LANES = (8.6, 15.0)
LAWN_F = sbox(-12.0, 8.6, 8.6, 12.0).difference(sbox(-2.6, 8.6, 0.6, 12.0))
SIDEWALK = sbox(SX0, 12.0, SX1, 14.0).difference(unary_union([sbox(-24.0, 12.0, -18.0, 14.0), sbox(LANES[0], 12.0, LANES[1], 14.0)]))
EAST_LAWN = sbox(LANES[1], -7.4, SX1, 12.0); BACK_LAWN = sbox(SX0, SZ0, SX1, -12.0)
BED1 = LineString([(-8.6, 10.0), (-6.4, 10.6), (-4.2, 10.0)]).buffer(0.9, 24); BED2 = LineString([(2.0, 10.2), (4.5, 10.7), (7.0, 10.2)]).buffer(0.8, 24)
def site():
    """Terreno: calcada coberta de placas em volta do predio e caminho ate a calcada, gramado com 2 canteiros em rim com borda,
    estacionamento com vagas pintadas, 2 faixas de drive-thru com setas e ilha, viela dos fundos, calcada com juntas e rua."""
    p = Piece(); box_ = sbox(SX0, SZ0, SX1, SZ1)
    p.merge(paving(APRON, Y0)); p.merge(paving(SIDEWALK, Y0))
    ext_y(p, 'curb', ISLAND, GY, Y0); ext_y(p, 'concrete', ISLAND.buffer(-0.15, join_style=2), Y0, Y0 + 0.004)
    beds = unary_union([BED1, BED2]); edge = beds.buffer(0.08, 24)
    for g in (LAWN_F.difference(edge), EAST_LAWN, BACK_LAWN): ext_y(p, 'grass', g, GY, 0.08)
    ext_y(p, 'mulch', beds, GY, 0.1); ext_y(p, 'curb', edge.difference(beds), GY, 0.14)
    asph = box_.difference(unary_union([APRON, OUTL, ISLAND, LAWN_F, SIDEWALK, EAST_LAWN, BACK_LAWN]))
    ext_y(p, 'asphalt', asph, GY, 0.0)
    for z in np.arange(-6.0, 11.5, 2.6):
        for (a, b) in ((-25.5, -20.5), (-17.5, -12.5)): p.box('paint_w', a, b, 0.0, 0.004, z - 0.05, z + 0.05)
    for x in (10.1, (12.6 + LANES[1]) / 2):
        for z in (-5.5, 7.0):
            p.hull('paint_w', [(x - 0.08, 0.0, z - 0.9), (x + 0.08, 0.0, z - 0.9), (x - 0.08, 0.0, z), (x + 0.08, 0.0, z)] + [(x - 0.08, 0.004, z - 0.9), (x + 0.08, 0.004, z - 0.9), (x - 0.08, 0.004, z), (x + 0.08, 0.004, z)])
            p.hull('paint_w', [(x + dx, y, z + dz) for (dx, dz) in ((-0.35, 0.0), (0.35, 0.0), (0.0, 0.6)) for y in (0.0, 0.004)])
    for x in np.arange(SX0 + 0.5, SX1 - 1.0, 3.0): p.box('paint_y', x, x + 1.5, 0.0, 0.004, 15.95, 16.07)
    p.box('paint_w', LANES[0] + 0.1, LANES[1] - 0.1, 0.0, 0.004, -7.0, -6.9)
    return p
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

# ============================================================================ portas
def door_glass_g(w=0.89, h=2.43, t=0.05):
    """Porta de vidro de quadro dourado com barra de empurrar cromada e chute alto (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.06
    p.cham('gold', 0, s, 0, h, -t / 2, t / 2, 0.004); p.cham('gold', w - s, w, 0, h, -t / 2, t / 2, 0.004)
    p.cham('gold', s - 0.002, w - s + 0.002, 0, 0.3, -t / 2, t / 2, 0.004); p.cham('gold', s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.004)
    p.box('glass', s - 0.004, w - s + 0.004, 0.296, h - s + 0.004, -0.004, 0.004)
    for z in (1, -1):
        seg_cyl(p, 'chrome', (s, 1.05, z * (t / 2 + 0.05)), (w - s, 1.05, z * (t / 2 + 0.05)), 0.018, 8)
        for x in (s + 0.04, w - s - 0.04): seg_cyl(p, 'chrome', (x, 1.05, z * t / 2), (x, 1.05, z * (t / 2 + 0.05)), 0.01, 6)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
SPUT = [(-7.5, 3.2), (-3.0, 2.6), (2.5, 2.2), (6.4, 4.4), (-0.5, 4.2)]
pieces = {'g_win': glass_mod('win'), 'g_door': glass_mod('door'),
          'b_plain': wall('plain', 'brick'), 'b_win': wall('win', 'brick'), 'b_door': wall('door', 'brick'),
          's_plain': wall('plain'), 's_teller': wall('teller'), 's_plain_fa': wall('plain', 'fstone', 1, GT_), 's_plain_fb': wall('plain', 'fstone', -1, GT_),
          's_plain_ba': wall('plain', 'fstone', -1, T), 's_plain_bb': wall('plain', 'fstone', 1, T)}
pieces.update({
    'clerestory': clerestory(), 'roof': roof(), 'vcol_f': vcol(-6.5, 7.6), 'vcol_i': vcol(12.1, -1.2, 'z'), 'vcol_e1': vcol(15.6, -3.5, 'z'), 'vcol_e2': vcol(15.6, 3.5, 'z'),
    'floor': floor_piece(), 'core_ceil': core_ceil(), 'plan': plan(), 'rail_low': rail_low(), 'teller_counter': teller_counter(),
    'vault_frame': vault_frame(), 'deposit_boxes': deposit_boxes(3.2), 'deposit_boxes_s': deposit_boxes(2.4), 'cash_cart': cash_cart(), 'safe_box': safe_box(),
    'check_desk': check_desk(), 'sofa': sofa(), 'tulip_chair': tulip_chair(), 'coffee_table': coffee_table(), 'sputnik': sputnik(1.3), 'star_clock': star_clock(),
    'planter_bowl': planter_bowl(), 'queue_posts': queue_posts(), 'brochure_rack': brochure_rack(), 'exec_desk': exec_desk(), 'office_chair': office_chair(),
    'shell_chair': shell_chair(), 'table_round': table_round(), 'kitchenette': kitchenette(), 'lockers': lockers(), 'file_cab': file_cab(), 'stool': stool(),
    'booth_desk': booth_desk(), 'tube_kiosk': tube_kiosk(), 'tube_run': tube_run(), 'bollard_y': bollard_y(), 'totem': totem(), 'disc_lamp': disc_lamp(),
    'palm': palm(), 'palm_b': palm(5.6, 3, (-0.4, 0.5)), 'yucca': yucca(), 'yucca_s': yucca(5, 0.6), 'boulder': boulder(), 'boulder_s': boulder(0.3, 8),
    'bush': bush(), 'tree': tree(), 'tree_b': tree(5.0, 1.6, 'leaf2', 4), 'night_drop': night_drop(), 'planter_box': planter_box(), 'trash_bin': trash_bin(),
    'wheel_stop': wheel_stop(), 'site': site(),
    'door_leaf_glass': door_glass_g(), 'door_leaf_office': door_glass_g(0.86, 2.07, 0.04), 'door_leaf_back': door_metal(0.88, 2.13), 'door_leaf_int': door_interior(0.86, 2.08),
    'vault_leaf': vault_leaf(), 'gate_c': gate_c(), 'player_scale_ref': player_ref()})

# ============================================================================ montagem
tg = ['house', 'ext']
for x in range(-9, 8, 2): put('g_door' if x == -1 else 'g_win', x, Y0, HZ, 0, tg + ['front'])
BACKK = {-9: 'b_plain', -7: 'b_plain', -5: 'b_plain', -3: 'b_win', -1: 'b_win', 1: 'b_win', 3: 'b_door', 5: 'b_plain', 7: 'b_win'}
for x, k in BACKK.items(): put(k, x, Y0, -HZ, 180, tg + ['back'])
for z in range(-5, 6, 2):
    put({5: 's_plain_fa', -5: 's_plain_ba'}.get(z, 's_plain'), X0, Y0, z, -90, tg + ['left'])
    put({5: 's_plain_fb', -5: 's_plain_bb', 1: 's_teller'}.get(z, 's_plain'), X1, Y0, z, 90, tg + ['right'])
put('clerestory', 0, Y0, 0, 0, ['house', 'ext', 'roof']); put('roof', 0, Y0, 0, 0, ['roof'])
for x in (-6.5, -3.5, 2.5, 5.5): put('vcol_f', x, 0, 7.6, 0, ['site', 'front'])
put('vcol_i', 12.1, 0, -1.2, 0, ['site']); put('vcol_e1', 15.6, 0, -3.5, 0, ['site']); put('vcol_e2', 15.6, 0, 3.5, 0, ['site'])
g = ['house']; y = Y0
for n in ('floor', 'plan', 'rail_low', 'teller_counter'): put(n, 0, y, 0, 0, g)
put('core_ceil', 0, y, 0, 0, g + ['roof'])
put('gate_c', -0.495, y, ZC, 0, g, door=90)
put('vault_frame', VAULT_X, y, ZP, 0, g); put('vault_leaf', VAULT_X - 1.03, y, ZP + 0.3, 0, g, door=-95)
yf = y + 0.008
put('door_leaf_glass', -1 - 0.895, yf, HZ - 0.06, 0, tg + ['front'], door=90); put('door_leaf_glass', -1 + 0.895, yf, HZ - 0.06, 180, tg + ['front'], door=-90)
hx, hz = hinge(3, -HZ, 180, -0.45, -0.12); put('door_leaf_back', hx, yf, hz, 180, tg + ['back'], door=90)
put('door_leaf_office', OFFICE_DOOR - 0.43, y + 0.005, ZP, 0, g, door=-90); put('door_leaf_int', STAFF_DOOR - 0.43, y + 0.005, ZP, 0, g, door=90)
# caixas, caixa-forte, gerencia, copa, cabine
for c in SC: put('stool', c, y, ZC - 0.95, 0, g)
put('safe_box', 0.0, y, ZP + t_ / 2, 0, g)
put('deposit_boxes', VAULT_X, y, ZI0, 0, g); put('deposit_boxes_s', XI0, y, -4.15, 90, g); put('cash_cart', -6.0, y, -4.4, 0, g)
put('exec_desk', -3.0, y, -3.4, 180, g); put('office_chair', -3.0, y, -4.7, 0, g)
for x in (-3.5, -2.4): put('shell_chair', x, y, -3.0, 180, g)
put('file_cab', -4.6, y, ZI0, 0, g); put('planter_bowl', -1.5, y, -5.2, 0, g)
put('table_round', 2.2, y, -4.3, 0, g); put('shell_chair', 1.5, y, -4.3, 90, g); put('shell_chair', 2.9, y, -4.3, -90, g); put('shell_chair', 2.2, y, -3.6, 180, g)
put('kitchenette', XB - t_ / 2, y, -4.2, -90, g); put('lockers', -1.0 + t_ / 2, y, -4.2, 90, g)
put('booth_desk', XI1, y, 1.0, -90, g); put('office_chair', 6.7, y, 1.0, 90, g)
# saguao
put('sofa', XI0, y, 3.2, 90, g); put('coffee_table', -8.3, y, 3.2, 90, g)
for z in (2.6, 3.8): put('tulip_chair', -7.3, y, z, -90, g)
put('star_clock', XI0, y + 2.2, 3.2, 90, g)
for (x, z) in ((-9.2, 5.2), (-9.2, 1.0), (0.6, 5.2)): put('planter_bowl', x, y, z, 0, g)
put('check_desk', -5.2, y, 1.5, 0, g); put('check_desk', 3.6, y, 3.8, 180, g)
put('queue_posts', 1.0, y, 0.9, 0, g); put('brochure_rack', 7.2, y, 4.9, 0, g)
for (x, z) in SPUT: put('sputnik', x, Y0 + ybot(x, z), z, 0, g)
# drive-thru e terreno
st = ['site']
put('tube_kiosk', KIOSK[0], Y0, KIOSK[1], 90, st); put('tube_run', 0, Y0, 0, 0, st)
for (x, z) in ((12.1, -2.75), (12.1, 3.75), (8.3, -0.6), (8.3, 2.6)): put('bollard_y', x, Y0, z, 0, st)
put('site', 0, 0, 0, 0, st); put('totem', -10.6, 0, 11.0, 0, st); put('night_drop', X0, Y0, 4.4, -90, st)
for (x, z) in ((-3.2, 9.6), (1.2, 9.6), (-3.2, 11.4), (1.2, 11.4)): put('disc_lamp', x, 0, z, 0, st)
for (x, z, n) in ((18.2, -6.5, 'palm'), (7.9, 11.4, 'palm_b'), (18.2, 9.0, 'palm'), (18.2, -3.0, 'palm_b'), (18.2, 3.0, 'palm')): put(n, x, 0, z, 0, st)
for (x, z, n) in ((-8.0, 10.3, 'yucca'), (-6.4, 10.6, 'yucca_s'), (-5.0, 10.2, 'yucca'), (3.0, 10.5, 'yucca'), (5.6, 10.6, 'yucca_s')): put(n, x, 0.1, z, 0, st)
for (x, z, n) in ((-7.2, 10.1, 'boulder'), (-5.7, 10.75, 'boulder_s'), (4.2, 10.35, 'boulder'), (6.5, 10.4, 'boulder_s')): put(n, x, 0.06, z, 0, st)
for x in (-8.5, 4.0): put('planter_box', x, Y0, 7.7, 0, st)
put('trash_bin', 1.3, Y0, 8.2, 0, st)
for k in range(6):
    z = -6.0 + 1.3 + 2.6 * k; put('wheel_stop', -25.0, 0, z, 90, st); put('wheel_stop', -13.0, 0, z, 90, st)
for k, x in enumerate((-20.0, -9.0, 2.0, 13.0)): put('tree' if k % 2 == 0 else 'tree_b', x, 0, -14.2 + 0.1 * k, 0, st)
for z in (-6.0, -0.5, 0.8, 6.0, 8.5): put('bush', 15.7, 0, z, 0, st)
put('player_scale_ref', -1.0, Y0, 13.0); put('player_scale_ref', -6.0, Y0, 1.0, 0, ['house'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_level': Y0,
                       'building': {'x': [X0, X1], 'z': [-HZ, HZ], 'floors': 1, 'wall_top': HWALL, 'service_ceiling': 3.0},
                       'roof': {'x': [RX0, RX1], 'z': [RZ0, RZ1], 'vaults': 9, 'vault_width': VW, 'height_back': RH0, 'slope': RS, 'rise': RA,
                                'note': 'roof underside y = Y0 + RH0 + RS*(z-RZ0) + RA*sin(pi*u) - RT, u = frac((x-RX0)/VW)'},
                       'drive_thru': {'lanes_x': [LANES[0], 11.6, 12.6, LANES[1]], 'island': list(ISLAND.bounds)},
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
