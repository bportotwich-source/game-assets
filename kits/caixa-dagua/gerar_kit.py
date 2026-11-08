"""Kit 41: caixa-d'agua de aco sobre torre (anos 1930), em ALTO DETALHE (scripts/detalhe/detalhe.py).
Reservatorio cilindrico de chapas rebitadas (4 anéis com juntas sobrepostas e costuras desencontradas), fundo em bacia, teto conico
com nervuras, respiro, alcapao com guarda-corpo e pinaculo com para-raios. Passarela de grade em volta da base do reservatorio, com
guarda-corpo e consolos. Torre de 4 pernas inclinadas de perfil composto com treliça, vigas treliçadas em 3 niveis, contraventamento
em X com esticadores, anel de apoio; tubo de subida central com flanges. Escada de marinheiro com gaiola na perna da frente e no
costado do reservatorio. Casa de bombas de tijolo com janelas de caixilho de aco, porta de chapa e platibanda; dentro, o tubo de
subida desce ate o registro e as 2 bombas com motores, quadro eletrico, bancada e estante.
Fora: patio de brita cercado por tela com arame farpado, portao de carros de 2 folhas e portao de pedestres, caminho de concreto,
blocos de fundacao das pernas, poste de luz, placa sem texto (pictograma de gota), armario eletrico, tampa de inspecao, gramado,
rua de acesso, arvores e arbustos.
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
configurar(cores={'brick': (152, 70, 52), 'concrete': (186, 182, 174), 'coping': (200, 196, 188), 'plaster': (230, 226, 214), 'ceil': (238, 236, 228),
                  'paint': (232, 226, 206), 'paint_d': (204, 198, 178), 'roofp': (150, 156, 160), 'steel': (70, 76, 80), 'steel_d': (52, 56, 60),
                  'galv': (176, 180, 182), 'mesh': (150, 154, 156), 'iron': (40, 42, 44), 'brass': (196, 160, 82), 'copper': (176, 104, 62),
                  'frame': (66, 92, 82), 'door': (78, 104, 92), 'pump': (46, 92, 140), 'motor': (60, 110, 150), 'redp': (180, 50, 40),
                  'yellowp': (230, 190, 50), 'sign_b': (40, 90, 160), 'paint_w': (240, 240, 236), 'rubber': (30, 30, 30), 'dark': (30, 30, 32),
                  'wood': (150, 104, 62), 'dkwood': (96, 62, 42), 'gravel': (170, 164, 152), 'asphalt': (72, 74, 76), 'grass': (100, 146, 70),
                  'soil': (96, 72, 52), 'leaf': (84, 130, 62), 'leaf2': (110, 146, 70), 'hedge': (62, 102, 52), 'bark': (96, 72, 52),
                  'lamp_glass': (255, 236, 190), 'membrane': (110, 110, 108), 'glass_w': (180, 200, 206), 'chalk': (232, 232, 224), 'cream': (236, 228, 204),
                  'gauge': (240, 240, 232)},
           texturas={'brick': 'brick', 'concrete': 'render', 'plaster': 'plaster', 'gravel': 'render', 'asphalt': 'render', 'grass': 'render',
                     'membrane': 'render', 'wood': 'planks', 'dkwood': 'planks'},
           out=OUT)
D.METAL.update({'steel', 'steel_d', 'galv', 'mesh', 'iron', 'brass', 'copper', 'roofp', 'paint', 'paint_d'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.25; t_ = 0.12                               # modulo, parede de tijolo, parede interna
Y0 = 0.15                                                  # piso da casa de bombas (patio de brita em 0)
HX, HZ = 3.0, 2.0                                          # casa: x de -3 a 3, z de -2 a 2, frente para +Z
CEIL = 3.0; HW = 3.25; HP = 3.6                            # forro, topo da laje, topo da platibanda (sobre o piso)
LB = 5.6; LT = 2.85; YB = 0.94; YT = 23.4                  # pernas: meio-vao na base e no topo, cota da placa de base e do anel
LEVELS = [YB, 6.6, 12.3, 18.0, YT]                         # nos das pernas (vigas nos 3 do meio)
TB = 24.0; TR = 4.0; CH = 1.75; NC = 4                     # reservatorio: base do costado, raio, altura de cada anel, anéis
TTOP = TB + CH * NC; TAPEX = TTOP + 2.6                    # topo do costado e apice do teto
BR0, BR1 = TR, TR + 1.1                                    # passarela: raio interno e externo
RISER = 0.55                                               # raio do tubo de subida
FX, FZ = 10.0, 10.0                                        # cerca: x de -10 a 10, z de -10 a 10
PG = (-2.6, -1.4); VG = (1.0, 5.0)                         # portao de pedestres e portao de carros (na frente, z = 10)
DOOR_X = -2.0                                              # porta da casa de bombas
def leg_xz(y): t = (y - YB) / (YT - YB); return LB + (LT - LB) * t

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

def unit(v): v = np.array(v, float); return v / np.linalg.norm(v)
def ring_y(p, mat, r0, r1, y0, y1, x=0.0, z=0.0, sec=96):
    m = trimesh.creation.annulus(r_min=r0, r_max=r1, height=y1 - y0, sections=sec)
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([x, (y0 + y1) / 2, z]); return p.add(mat, m)
def disc_x(p, mat, r, x0, x1, y, z, sec=20):
    m = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=sec); m.apply_transform(rot_y(90)); m.apply_translation([(x0 + x1) / 2, y, z]); return p.add(mat, m)
def disc_z(p, mat, r, z0, z1, x, y, sec=20):
    m = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sec); m.apply_translation([x, y, (z0 + z1) / 2]); return p.add(mat, m)
OUTL = sbox(-HX, -HZ, HX, HZ)
def off(poly, d): return poly.buffer(d, join_style=2, mitre_limit=10)

# ============================================================================ casa de bombas (pivo: face externa, cota do piso; parede em -Z)
def wall_core(p, holes, xs0=(-W / 2, W / 2), h=HP):
    xs = sorted(set(list(xs0) + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([-Y0, 0.0, CEIL, h] + [v for hh in holes for v in hh[2:]]))
    ys = [v for v in ys if -Y0 <= v <= h]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return 'concrete' if (cy < 0 or cy > CEIL) else 'plaster'
        return 'concrete' if cy < 0 else 'brick'
    for m, mesh in grid_solid(xs, ys, [-T, -0.12, 0.0], cell).items(): p.add(m, mesh)
WIN = (-0.6, 0.6, 0.9, 2.3)
def steel_window(p, a, b, y0, y1):
    """Caixilho de aco de 3 x 4 vidros com basculante no meio, peitoril de concreto inclinado, verga de concreto e peitoril interno."""
    z0, z1 = -0.16, -0.1; f = 0.045
    p.box('frame', a, a + f, y0, y1, z0, z1); p.box('frame', b - f, b, y0, y1, z0, z1); p.box('frame', a + f, b - f, y1 - f, y1, z0, z1); p.box('frame', a + f, b - f, y0, y0 + f, z0, z1)
    p.box('glass', a + f, b - f, y0 + f, y1 - f, -0.133, -0.127)
    for k in (1, 2): x = a + (b - a) * k / 3; p.box('frame', x - 0.012, x + 0.012, y0 + f, y1 - f, -0.145, -0.115)
    for k in (1, 2, 3): y = y0 + (y1 - y0) * k / 4; p.box('frame', a + f, b - f, y - 0.012, y + 0.012, -0.145, -0.115)
    ym0, ym1 = y0 + (y1 - y0) / 2, y0 + 3 * (y1 - y0) / 4
    q = Piece(); q.box('frame', a + f + 0.01, b - f - 0.01, 0.0, 0.03, -0.01, 0.01); q.box('frame', a + f + 0.01, b - f - 0.01, ym1 - ym0 - 0.03, ym1 - ym0, -0.01, 0.01)
    q.box('glass', a + f + 0.02, b - f - 0.02, 0.03, ym1 - ym0 - 0.03, -0.003, 0.003)
    for k in (1, 2): x = a + (b - a) * k / 3; q.box('frame', x - 0.012, x + 0.012, 0.03, ym1 - ym0 - 0.03, -0.012, 0.012)
    p.merge(q, tr(0, ym0, -0.09) @ trimesh.transformations.rotation_matrix(math.radians(-18), [1, 0, 0]))
    prof_x(p, 'concrete', a - 0.08, b + 0.08, [(-0.1, y0 - 0.06), (0.06, y0 - 0.07), (0.06, y0 - 0.04), (-0.1, y0 + 0.0)])
    p.box('concrete', a - 0.12, b + 0.12, y1, y1 + 0.2, 0.0, 0.012)
    p.cham('concrete', a - 0.03, b + 0.03, y0 - 0.04, y0 + 0.004, -T - 0.04, -0.16, 0.004)
def wall(kind='plain', trim=0):
    """Modulo de 2 m da casa de bombas: win (caixilho de aco), door (porta de chapa com veneziana e arandela), plain.
    trim -1/+1 encurta a ponta -x/+x em T (paredes laterais encostam por dentro das paredes de frente e fundos)."""
    p = Piece(); holes = []; xs0 = (-W / 2 + T * (trim < 0), W / 2 - T * (trim > 0))
    if kind == 'win': holes = [WIN]
    if kind == 'door': holes = [(-0.5, 0.5, 0.0, 2.2)]
    wall_core(p, holes, xs0)
    if kind == 'win': steel_window(p, *WIN)
    if kind == 'door':
        p.box('steel', -0.5, -0.45, 0.0, 2.2, -0.2, -0.06); p.box('steel', 0.45, 0.5, 0.0, 2.2, -0.2, -0.06); p.box('steel', -0.45, 0.45, 2.15, 2.2, -0.2, -0.06)
        p.box('concrete', -0.65, 0.65, 2.2, 2.42, 0.0, 0.012)
        p.cham('concrete', -0.8, 0.8, -Y0, 0.0, -T + 0.004, 0.9, 0.012); p.cham('concrete', -0.5, 0.5, -0.02, 0.008, -T + 0.004, 0.02, 0.004)
        p.merge(wall_lantern(), tr(0.0, 2.62, 0.0))
    return p
def corner():
    p = Piece(); e = 0.004
    p.box('concrete', -T + e, e, -Y0, 0.0, -T + e, e); p.box('brick', -T + e, e, 0.0, HP, -T + e, e)
    return p

# ============================================================================ cobertura, piso e interior da casa de bombas (pivo: origem, cota do piso)
def ph_roof():
    """Laje com forro, manta, rodape de manta na platibanda, rufo de concreto, faixa de concreto, furo do tubo de subida com luva e
    canopla, ralo com buzinote e condutor."""
    p = Piece(); IN = off(OUTL, -T); hole = Point(0, 0).buffer(RISER + 0.05, 48)
    ext_y(p, 'ceil', IN.difference(hole), CEIL - 0.01, CEIL); ext_y(p, 'concrete', IN.difference(hole), CEIL, HW - 0.012); ext_y(p, 'membrane', IN.difference(hole), HW - 0.012, HW)
    ext_y(p, 'membrane', IN.difference(off(OUTL, -T - 0.03)), HW, HW + 0.15)
    ext_y(p, 'coping', off(OUTL, 0.04).difference(off(OUTL, -T - 0.03)), HP, HP + 0.07)
    ext_y(p, 'concrete', off(OUTL, 0.02).difference(off(OUTL, -0.01)), CEIL + 0.05, CEIL + 0.22)
    ring_y(p, 'galv', RISER + 0.002, RISER + 0.16, HW, HW + 0.32, sec=48); ring_y(p, 'iron', RISER + 0.002, RISER + 0.05, HW + 0.32, HW + 0.4, sec=48)
    ring_y(p, 'galv', RISER + 0.002, RISER + 0.14, CEIL - 0.04, CEIL - 0.01, sec=48)
    p.box('galv', HX - 1.2, HX - 0.8, HW + 0.02, HW + 0.12, -HZ - 0.25, -HZ + T); p.box('galv', HX - 1.15, HX - 0.85, HW + 0.02, HW + 0.1, -HZ - 0.32, -HZ - 0.25) if False else None
    seg_cyl(p, 'galv', (HX - 1.0, HW + 0.07, -HZ - 0.25), (HX - 1.0, -Y0 + 0.2, -HZ - 0.08), 0.05, 10) if False else None
    for y in np.arange(0.4, HW, 1.0): p.box('galv', HX - 1.06, HX - 0.94, y, y + 0.03, -HZ, -HZ - 0.02) if False else None
    return p
def downspout_piece():
    """Buzinote na platibanda e condutor (pivo: face dos fundos, na cota do piso)."""
    p = Piece(); x = 0.0
    p.box('galv', x - 0.15, x + 0.15, HW + 0.02, HW + 0.12, -0.02, 0.25)
    lathe(p, 'galv', [(0.12, HW - 0.12), (0.12, HW + 0.0), (0.06, HW - 0.25)], x, 0.22, 0.0, 12)
    seg_cyl(p, 'galv', (x, HW - 0.2, 0.22), (x, 0.25, 0.22), 0.05, 12); seg_cyl(p, 'galv', (x, 0.25, 0.22), (x, 0.05, 0.5), 0.05, 12)
    for y in (0.8, 1.8, 2.8): p.box('galv', x - 0.06, x + 0.06, y, y + 0.03, 0.0, 0.2)
    return p
def ph_floor():
    """Piso de concreto com juntas e ralo; bases de concreto das bombas."""
    p = Piece(); IN = off(OUTL, -T)
    ext_y(p, 'concrete', IN, -Y0, 0.0)
    for x in (-1.0, 1.0): p.box('dark', x - 0.004, x + 0.004, 0.0, 0.002, -HZ + T, HZ - T)
    p.box('iron', -1.85, -1.55, 0.0, 0.006, 0.55, 0.85)
    for k in range(5): x = -1.82 + k * 0.06; p.box('dark', x, x + 0.02, 0.006, 0.007, 0.58, 0.82)
    return p
def pumpset():
    """Bomba centrifuga em base de concreto (pivo: centro da base, piso; eixo ao longo de Z): voluta azul com flanges, motor com aletas,
    acoplamento com protecao, saida para cima com valvula de retencao."""
    p = Piece(); p.cham('concrete', -0.35, 0.35, 0.0, 0.15, -0.35, 0.95, 0.01); p.box('steel_d', -0.3, 0.3, 0.15, 0.2, -0.3, 0.9)
    disc_z(p, 'pump', 0.25, -0.15, 0.1, 0.0, 0.45, 24); disc_z(p, 'pump', 0.12, 0.1, 0.25, 0.0, 0.45, 16)
    lathe(p, 'pump', [(0.1, 0.62), (0.1, 0.7)], 0.0, 0.0, 0.0, 16); ring_y(p, 'pump', 0.0, 0.16, 0.66, 0.7, sec=20)
    disc_z(p, 'galv', 0.11, 0.25, 0.42, 0.0, 0.45, 16)
    disc_z(p, 'motor', 0.2, 0.42, 0.82, 0.0, 0.42, 24); disc_z(p, 'motor', 0.16, 0.82, 0.88, 0.0, 0.42, 20)
    for k in range(12):
        a = k * math.pi / 6; x, y = 0.2 * math.cos(a), 0.42 + 0.2 * math.sin(a)
        if y > 0.25: p.box('motor', x - 0.012, x + 0.012, y - 0.012, y + 0.012, 0.44, 0.8) if False else seg_cyl(p, 'motor', (x * 1.08, y + 0.016 * math.sin(a), 0.44), (x * 1.08, y + 0.016 * math.sin(a), 0.8), 0.012, 4)
    p.box('motor', -0.17, 0.17, 0.2, 0.25, 0.48, 0.78); p.box('steel_d', -0.08, 0.08, 0.6, 0.72, 0.55, 0.7)
    return p
def valve_set():
    """Registro de gaveta no pe do tubo de subida (volante e castelo), curva, coletor ate as bombas, valvulas de retencao e manometros
    (pivo: origem, piso)."""
    p = Piece(); r = 0.3
    ring_y(p, 'steel_d', 0.0, RISER + 0.12, 1.78, 1.84, sec=32); seg_cyl(p, 'steel_d', (0, 1.78, 0), (0, 1.62, 0), r, 24)
    p.cyl('steel_d', 0.42, 1.25, 1.62, 0, 0, 24)
    for y in (1.25, 1.62): ring_y(p, 'steel_d', 0.0, 0.48, y - 0.02, y + 0.02, sec=32)
    seg_cyl(p, 'steel_d', (0.3, 1.43, 0), (0.95, 1.43, 0), 0.16, 16); seg_cyl(p, 'brass', (0.95, 1.43, 0), (1.25, 1.43, 0), 0.03, 8)
    m = trimesh.creation.annulus(r_min=0.24, r_max=0.28, height=0.04, sections=32); m.apply_transform(rot_y(90)); m.apply_translation([1.2, 1.43, 0]); p.add('redp', m)
    for k in range(4): a = k * math.pi / 2; seg_cyl(p, 'redp', (1.2, 1.43, 0), (1.2, 1.43 + 0.25 * math.sin(a), 0.25 * math.cos(a)), 0.015, 6)
    pts = [(0, 1.25, 0), (0, 1.05, -0.05), (0, 0.97, -0.25), (0, 0.95, -0.45)]
    for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'pump', a, b, r, 24); p.sphere('pump', r, *b, 2)
    seg_cyl(p, 'pump', (0, 0.95, -0.45), (0, 0.95, -1.15), 0.25, 24); p.sphere('pump', 0.25, 0, 0.95, -1.15, 2)
    seg_cyl(p, 'pump', (0, 0.95, -1.15), (2.3, 0.95, -1.15), 0.2, 24); disc_x(p, 'pump', 0.26, 2.3, 2.34, 0.95, -1.15, 24)
    for x in (0.6, 1.4, 2.0): disc_x(p, 'pump', 0.27, x - 0.02, x + 0.02, 0.95, -1.15, 24)
    for xp in (0.9, 1.9):
        seg_cyl(p, 'pump', (xp, 0.7, -1.15), (xp, 0.78, -1.15), 0.1, 16); p.cyl('steel_d', 0.13, 0.78, 0.86, xp, -1.15, 16)
        p.box('steel_d', xp - 0.02, xp + 0.02, 0.82, 0.86, -1.05, -0.9); seg_cyl(p, 'steel_d', (xp, 0.84, -0.9), (xp, 0.84, -0.72), 0.01, 4); p.sphere('redp', 0.03, xp, 0.84, -0.7, 1)
    for x in (0.4, 1.6):
        seg_cyl(p, 'brass', (x, 1.15, -1.15), (x, 1.32, -1.15), 0.012, 6)
        disc_z(p, 'brass', 0.07, -1.17, -1.13, x, 1.38, 20); disc_z(p, 'gauge', 0.06, -1.13, -1.125, x, 1.38, 20); p.box('dark', x - 0.002, x + 0.045, 1.379, 1.383, -1.125, -1.122)
    return p
def el_panel():
    """Quadro eletrico de chapa (pivo: face da parede, centro embaixo; frente +Z): porta com puxador, 3 chaves de faca, luzes, eletroduto."""
    p = Piece(); p.cham('frame', -0.45, 0.45, 0.6, 2.0, 0.0, 0.3, 0.01); p.box('frame', -0.44, 0.44, 0.62, 1.98, 0.3, 0.31)
    p.box('steel_d', 0.34, 0.37, 1.2, 1.4, 0.31, 0.34)
    for x in (-0.25, 0.0, 0.25):
        p.box('dark', x - 0.06, x + 0.06, 1.55, 1.75, 0.31, 0.33); seg_cyl(p, 'redp', (x, 1.6, 0.33), (x, 1.72, 0.42), 0.012, 6)
        p.sphere('lamp_glass' if x != 0 else 'redp', 0.02, x, 1.85, 0.32, 1)
    seg_cyl(p, 'galv', (0.3, 2.0, 0.08), (0.3, CEIL, 0.08), 0.025, 8); seg_cyl(p, 'galv', (-0.3, 2.0, 0.08), (-0.3, CEIL, 0.08), 0.025, 8)
    p.box('yellowp', -0.12, 0.12, 1.12, 1.24, 0.31, 0.313); p.hull('dark', [(x, y, 0.3135) for (x, y) in ((0.0, 1.22), (-0.04, 1.17), (0.01, 1.17), (-0.01, 1.14), (0.04, 1.19), (-0.01, 1.19))] + [(0.0, 1.22, 0.315)])
    return p
def workbench(L1=1.4):
    """Bancada de madeira com morsa, ferramentas e prateleira de baixo (pivo: centro de tras, piso)."""
    p = Piece(); x = L1 / 2
    for xx in (-x + 0.05, x - 0.05):
        for zz in (0.05, 0.55): p.box('dkwood', xx - 0.04, xx + 0.04, 0.0, 0.86, zz - 0.04, zz + 0.04)
    p.cham('wood', -x, x, 0.86, 0.92, 0.0, 0.6, 0.006); p.box('wood', -x + 0.05, x - 0.05, 0.2, 0.24, 0.02, 0.58)
    p.box('dkwood', -x, x, 0.92, 1.6, 0.0, 0.02)
    for (xx, w, h) in ((-0.4, 0.04, 0.28), (-0.3, 0.03, 0.22), (-0.15, 0.05, 0.3), (0.05, 0.03, 0.25)): p.box('steel_d', xx, xx + w, 1.15, 1.15 + h, 0.02, 0.035)
    p.box('iron', 0.35, 0.55, 0.92, 1.02, 0.45, 0.62); p.box('iron', 0.35, 0.55, 1.02, 1.1, 0.5, 0.62); seg_cyl(p, 'galv', (0.45, 0.97, 0.62), (0.45, 0.97, 0.72), 0.012, 6)
    p.box('redp', -0.5, -0.2, 0.92, 1.05, 0.25, 0.45); p.box('steel_d', -0.15, 0.1, 0.24, 0.4, 0.1, 0.45)
    return p
def extinguisher():
    p = Piece(); p.box('steel_d', -0.06, 0.06, 1.0, 1.08, 0.0, 0.02); lathe(p, 'redp', [(0.08, 0.5), (0.08, 0.95), (0.05, 1.0), (0.02, 1.03)], 0.0, 0.1, 0.0, 14)
    seg_cyl(p, 'dark', (0.02, 1.0, 0.1), (0.1, 0.8, 0.16), 0.01, 6); p.box('dark', -0.04, 0.04, 1.03, 1.06, 0.06, 0.14)
    return p
def pendant_lamp():
    """Luminaria industrial pendente (pivo: ponto no forro)."""
    p = Piece(); p.cyl('galv', 0.05, -0.03, 0.0, 0, 0, 10); seg_cyl(p, 'galv', (0, -0.03, 0), (0, -0.55, 0), 0.008, 6)
    lathe(p, 'frame', [(0.03, -0.55), (0.06, -0.6), (0.24, -0.75), (0.25, -0.77)], sec=20); p.sphere('lamp_glass', 0.06, 0, -0.72, 0, 1)
    return p

# ============================================================================ torre (pivo: origem, chao)
LEG_A = unit((LT - LB, YT - YB, LT - LB))
U1 = unit((1.0, 0.0, -1.0)); U2 = unit(np.cross(LEG_A, U1))
def leg_c(y): return np.array([leg_xz(y), y, leg_xz(y)])
def leg():
    """Perna (quina +X +Z): bloco de fundacao com chanfro, placa de base com chumbadores, perfil composto de 4 cantoneiras com treliça nas
    4 faces e chapas de ligacao, chapas de no nos niveis das vigas, chapa de topo sob o anel."""
    p = Piece(); c0 = np.array([LB, 0.0, LB])
    p.cham('concrete', LB - 0.75, LB + 0.75, -0.2, 0.75, LB - 0.75, LB + 0.75, 0.04); p.cham('concrete', LB - 0.62, LB + 0.62, 0.75, 0.9, LB - 0.62, LB + 0.62, 0.05)
    p.box('galv', LB - 0.45, LB + 0.45, 0.9, YB, LB - 0.45, LB + 0.45)
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = LB + sx * 0.35, LB + sz * 0.35; p.cyl('galv', 0.025, YB, YB + 0.1, x, z, 8); p.cyl('galv', 0.045, YB, YB + 0.04, x, z, 6)
    h = 0.2; ch = 0.045
    def pt(y, s1, s2): return leg_c(y) + LEG_A * 0.0 + U1 * s1 + U2 * s2
    y0, y1 = YB, YT
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            pts = [leg_c(y) + U1 * s1 * h + U2 * s2 * h + U1 * a * ch + U2 * b * ch for y in (y0, y1) for a in (-1, 1) for b in (-1, 1)]
            p.hull('steel', pts)
    step = 0.34
    for (fu, fs) in ((U1, 1), (U1, -1), (U2, 1), (U2, -1)):
        other = U2 if fu is U1 else U1
        n = int((y1 - y0) / step)
        prev = None
        for k in range(n + 1):
            y = y0 + k * step; side = 1 if k % 2 == 0 else -1
            q = leg_c(y) + fu * fs * (h + 0.05) + other * side * (h - 0.02)
            if prev is not None: p.seg('steel_d', prev, q, 0.05, 0.012)
            prev = q
    for y in [y0 + 0.08, y1 - 0.08] + LEVELS[1:-1]:
        for (fu, fs) in ((U1, 1), (U1, -1), (U2, 1), (U2, -1)):
            other = U2 if fu is U1 else U1; c = leg_c(y) + fu * fs * (h + 0.06)
            p.hull('steel', [c + other * a * (h + 0.04) + LEG_A * b * 0.14 + fu * fs * d for a in (-1, 1) for b in (-1, 1) for d in (0.0, 0.012)])
    for y in LEVELS[1:-1]:
        for (dx, dz) in ((-1, 0), (0, -1)):
            c = leg_c(y); d = np.array([dx, 0, dz], float)
            p.hull('steel', [c + d * (h + 0.0) + np.array([0, b, 0]) * 0.32 + np.array([dz, 0, dx]) * e * 0.008 + d * f * 0.38 for b in (-1, 1) for e in (-1, 1) for f in (0, 1)])
    p.hull('steel', [leg_c(y1) + U1 * a * 0.3 + U2 * b * 0.3 + np.array([0, d, 0]) for a in (-1, 1) for b in (-1, 1) for d in (0.0, 0.025)])
    return p
def strut(y):
    """Viga treliçada horizontal na face +Z, no nivel y (pivo: origem): banzos, diagonais, chapas de ponta."""
    p = Piece(); r = leg_xz(y); a, b = -r + 0.26, r - 0.26; hh = 0.24
    for yy in (y - hh, y + hh): p.box('steel', a, b, yy - 0.05, yy + 0.05, r - 0.06, r + 0.06)
    n = max(2, int((b - a) / 0.5)); xs = np.linspace(a, b, n + 1)
    for k, (xa, xb) in enumerate(zip(xs[:-1], xs[1:])):
        ya, yb = (y - hh + 0.05, y + hh - 0.05) if k % 2 == 0 else (y + hh - 0.05, y - hh + 0.05)
        p.seg('steel_d', (xa, ya, r), (xb, yb, r), 0.05, 0.016)
    for x in xs[1:-1]: p.box('steel_d', x - 0.02, x + 0.02, y - hh + 0.05, y + hh - 0.05, r - 0.04, r + 0.04)
    return p
def brace(i):
    """Contraventamento em X da face +Z entre os niveis i e i+1 (pivo: origem): tirantes redondos com esticadores e anel no cruzamento."""
    p = Piece(); ya, yb = LEVELS[i] + (0.3 if i > 0 else 0.6), LEVELS[i + 1] - 0.3
    ra, rb = leg_xz(ya) - 0.28, leg_xz(yb) - 0.28; za, zb = leg_xz(ya), leg_xz(yb)
    for s in (-1, 1):
        A = np.array([s * ra, ya, za]); B = np.array([-s * rb, yb, zb]); seg_cyl(p, 'steel', A, B, 0.026, 8)
        for t in (0.22, 0.78):
            C = A + (B - A) * t; u = unit(B - A); seg_cyl(p, 'steel_d', C - u * 0.18, C + u * 0.18, 0.045, 8)
        for E in (A, B): p.hull('steel_d', [E + np.array([dx, dy, 0]) for dx in (-0.08, 0.08) for dy in (-0.08, 0.08)] + [E + np.array([0, 0, 0.012])])
    ym = (ya + yb) / 2; zm = leg_xz(ym); m = trimesh.creation.cylinder(radius=0.09, height=0.03, sections=16); m.apply_translation([0, ym, zm]); p.add('steel_d', m)
    return p
def ring_girder():
    """Anel de apoio do reservatorio (pivo: centro, cota do topo das pernas): viga circular de chapa com abas e enrijecedores."""
    p = Piece(); ring_y(p, 'steel', 3.86, 4.12, 0.0, 0.55, sec=96)
    ring_y(p, 'steel', 3.8, 4.2, 0.0, 0.03, sec=96); ring_y(p, 'steel', 3.8, 4.2, 0.52, 0.55, sec=96)
    for k in range(32):
        a = k * math.pi / 16; c, s = math.cos(a), math.sin(a)
        p.hull('steel_d', [(r * c + t * -s, y, r * s + t * c) for r in (4.12, 4.19) for y in (0.03, 0.52) for t in (-0.006, 0.006)])
    return p
def riser():
    """Tubo de subida de chapa (pivo: origem, chao): do pe dentro da casa de bombas ate o fundo do reservatorio, flanges aparafusadas."""
    p = Piece(); y0, y1 = Y0 + 1.84, TB - 1.95
    p.cyl('paint_d', RISER, y0, y1, 0, 0, 40)
    for y in np.arange(Y0 + HW + 1.2, y1 - 0.5, 3.0):
        ring_y(p, 'paint_d', RISER - 0.01, RISER + 0.08, y - 0.025, y + 0.025, sec=40)
        for k in range(16): a = k * math.pi / 8; p.cyl('steel_d', 0.018, y + 0.025, y + 0.05, (RISER + 0.045) * math.cos(a), (RISER + 0.045) * math.sin(a), 6)
    return p

# ============================================================================ reservatorio (pivo: centro, base de cada peca)
SEAMS = 12
def tank_course(k, top=True):
    """Anel do costado: chapa curva, junta sobreposta em cima com 2 fileiras de rebites, 12 costuras verticais com rebites
    (desencontradas nos anéis pares e impares)."""
    p = Piece(); ring_y(p, 'paint', TR - 0.015, TR, 0.0, CH, sec=96)
    if top:
        ring_y(p, 'paint', TR, TR + 0.012, CH - 0.08, CH, sec=96)
        n = int(2 * math.pi * TR / 0.14)
        for j in range(n):
            a = 2 * math.pi * j / n; c, s = math.cos(a), math.sin(a)
            for y in (CH - 0.06, CH - 0.025): p.add('paint', trimesh.creation.cylinder(radius=0.013, height=0.016, sections=6, transform=rot_y(90 - math.degrees(a), ((TR + 0.012) * c, y, (TR + 0.012) * s))))
    off_a = (math.pi / SEAMS) * (k % 2)
    for m in range(SEAMS):
        a = off_a + 2 * math.pi * m / SEAMS; c, s = math.cos(a), math.sin(a)
        q = Piece(); q.box('paint', -0.045, 0.045, 0.0, CH - (0.08 if top else 0.0), 0.0, 0.01)
        for y in np.arange(0.08, CH - 0.1, 0.14):
            for x in (-0.025, 0.025): q.add('paint', trimesh.creation.cylinder(radius=0.012, height=0.014, sections=6, transform=tr(x, y, 0.012)))
        p.merge(q, rot_y(90 - math.degrees(a), (TR * c, 0.0, TR * s)))
    return p
def tank_bottom():
    """Fundo em bacia (pivo: centro, cota da base do costado): chapa de duplo raio, anel de juntas, bocal do tubo de subida."""
    p = Piece()
    prof = [(TR, 0.0)] + [(TR - 0.4 * (1 - math.cos(t)), -0.4 * math.sin(t)) for t in np.linspace(0.2, math.pi / 2, 5)]
    prof += [(r, -0.4 - 1.5 * (1 - (r / (TR - 0.4)) ** 2)) for r in np.linspace(TR - 0.6, RISER + 0.15, 7)]
    prof = [(r, y) for (r, y) in prof]; prof.append((0.0, prof[-1][1]))
    lathe(p, 'paint', [(r, y) for (r, y) in prof], sec=48)
    yb = prof[-2][1]; seg_cyl(p, 'paint_d', (0, yb + 0.1, 0), (0, yb - 0.12, 0), RISER + 0.08, 40)
    for k in range(3):
        rr = TR - 0.6 - k * 1.0; yy = -0.4 - 1.5 * (1 - (rr / (TR - 0.4)) ** 2)
        ring_y(p, 'paint_d', rr - 0.02, rr + 0.03, yy - 0.04, yy + 0.02, sec=64) if False else None
    return p
def tank_roof():
    """Teto conico (pivo: centro, cota do topo do costado): beiral com testeira, 24 nervuras, respiro de cogumelo, alcapao com
    guarda-corpo, pinaculo com bola e para-raios de cobre."""
    p = Piece(); RE = TR + 0.15; H = TAPEX - TTOP
    lathe(p, 'roofp', [(RE, 0.0), (RE, 0.04), (0.3, H - 0.1), (0.0, H)], sec=64)
    ring_y(p, 'roofp', RE - 0.001, RE + 0.018, -0.12, 0.05, sec=96)
    for k in range(24):
        a = 2 * math.pi * k / 24; c, s = math.cos(a), math.sin(a)
        A = np.array([(RE - 0.05) * c, 0.04 + 0.004, (RE - 0.05) * s]); B = np.array([0.45 * c, 0.04 + (RE - 0.45) / (RE - 0.3) * (H - 0.14) + 0.004, 0.45 * s])
        seg_cyl(p, 'roofp', A, B, 0.016, 6)
    lathe(p, 'roofp', [(0.32, H - 0.12), (0.3, H + 0.05), (0.12, H + 0.25), (0.05, H + 0.6)], sec=20)
    p.sphere('roofp', 0.14, 0, H + 0.72, 0, 2); seg_cyl(p, 'copper', (0, H + 0.8, 0), (0, H + 2.0, 0), 0.015, 8); p.sphere('copper', 0.03, 0, H + 2.02, 0, 1)
    ys = lambda r: 0.04 + (RE - r) / (RE - 0.3) * (H - 0.14)
    rv = 1.4; xv, zv = rv * math.cos(2.3), rv * math.sin(2.3)
    lathe(p, 'roofp', [(0.15, ys(rv) - 0.1), (0.15, ys(rv) + 0.5), (0.4, ys(rv) + 0.55), (0.36, ys(rv) + 0.7), (0.0, ys(rv) + 0.78)], xv, zv, 0.0, 20)
    ah = math.radians(60); rh = 2.3; xh, zh = rh * math.cos(ah), rh * math.sin(ah); yh = ys(rh)
    q = Piece(); q.box('roofp', -0.4, 0.4, -0.4, 0.3, -0.4, 0.4); q.box('roofp', -0.44, 0.44, 0.3, 0.35, -0.44, 0.44); q.box('steel_d', 0.38, 0.45, 0.1, 0.18, -0.06, 0.06)
    for (x, z) in ((-0.55, -0.55), (0.55, -0.55), (-0.55, 0.55)): q.cyl('galv', 0.02, -0.3, 1.0, x, z, 6)
    for y in (0.5, 1.0): seg_cyl(q, 'galv', (-0.55, y, 0.55), (-0.55, y, -0.55), 0.02, 6); seg_cyl(q, 'galv', (-0.55, y, -0.55), (0.55, y, -0.55), 0.02, 6)
    p.merge(q, rot_y(-math.degrees(ah) + 90, (xh, yh, zh)))
    return p
def balcony():
    """Passarela de grade em volta da base do costado (pivo: centro, cota do piso da passarela): chapa de grade com vao da escada,
    rodape, guarda-corpo de 2 tubos com 24 montantes, consolos diagonais ate o anel de apoio."""
    p = Piece(); deck = Point(0, 0).buffer(BR1, 96).difference(Point(0, 0).buffer(BR0, 96))
    lc = LADDER_TOP; hole = sbox(lc[0] - 0.4, lc[2] - 0.4, lc[0] + 0.4, lc[2] + 0.4)
    hole = rot_hole(hole, lc)
    ext_y(p, 'mesh', deck.difference(hole), -0.05, 0.0)
    for k in range(48):
        a = 2 * math.pi * k / 48; c, s = math.cos(a), math.sin(a)
        if Point((BR0 + BR1) / 2 * c, (BR0 + BR1) / 2 * s).distance(hole) < 0.15: continue
        p.seg('galv', (BR0 * c, -0.05, BR0 * s), ((BR1 - 0.01) * c, -0.05, (BR1 - 0.01) * s), 0.02, 0.05) if False else None
    ring_y(p, 'galv', BR1 - 0.012, BR1, 0.0, 0.1, sec=96); ring_y(p, 'galv', BR1 - 0.06, BR1, -0.12, -0.05, sec=96)
    for (y, r) in ((1.07, 0.024), (0.55, 0.018)):
        rr = BR1 - 0.04; ext_y(p, 'galv', Point(0, 0).buffer(rr + r, 96).difference(Point(0, 0).buffer(rr - r, 96)), y - r, y + r)
    for k in range(24):
        a = 2 * math.pi * k / 24; c, s = math.cos(a), math.sin(a); rr = BR1 - 0.04
        p.cyl('galv', 0.022, 0.0, 1.07, rr * c, rr * s, 8)
    for k in range(16):
        a = 2 * math.pi * (k + 0.5) / 16; c, s = math.cos(a), math.sin(a)
        seg_cyl(p, 'steel', (4.16 * c, YT + 0.2 - TB, 4.16 * s), ((BR1 - 0.08) * c, -0.08, (BR1 - 0.08) * s), 0.04, 8)
        p.hull('steel', [(r * c + t * -s, y, r * s + t * c) for r in (BR0, BR1 - 0.06) for y in (-0.12, -0.05) for t in (-0.04, 0.04)])
    return p
def rot_hole(poly, lc):
    from shapely import affinity
    return affinity.rotate(poly, 45, origin=(lc[0], lc[2]))
LAD_OFF = 0.62
def ladder_axis(y): return leg_c(y) + unit((1.0, 0.0, 1.0)) * LAD_OFF
LADDER_TOP = ladder_axis(TB)
def ladder(points, w=0.21, cage_from=None, cage_to=None, out=None):
    """Escada de marinheiro entre os pontos A e B do eixo: 2 montantes chatos, degraus redondos a cada 30 cm, gaiola de aros com 5
    barras; 'out' e a direcao para fora (a gaiola fica desse lado)."""
    p = Piece(); A, B = np.array(points[0], float), np.array(points[1], float); ax = unit(B - A); out = unit(out)
    side = unit(np.cross(ax, out)); Ln = np.linalg.norm(B - A)
    for s in (-1, 1): p.seg('galv', A + side * s * w, B + side * s * w, 0.06, 0.014)
    for t in np.arange(0.3, Ln - 0.05, 0.3): C = A + ax * t; seg_cyl(p, 'galv', C - side * w, C + side * w, 0.014, 6)
    for t in np.arange(0.2, Ln, 2.0):
        C = A + ax * t
        for s in (-1, 1): p.seg('galv', C + side * s * w, C + side * s * w - out * LAD_OFF * 0.75, 0.04, 0.012)
    if cage_from is not None:
        R = 0.36; c0 = cage_from; c1 = min(cage_to, Ln)
        hoops = list(np.arange(c0, c1, 0.9)) + [c1]
        for t in hoops:
            C = A + ax * t + out * 0.12; pts = [C + side * R * math.cos(th) + out * R * math.sin(th) for th in np.linspace(0, math.pi, 9)]
            for a, b in zip(pts[:-1], pts[1:]): p.seg('galv', a, b, 0.045, 0.01)
        for th in np.linspace(0.25, math.pi - 0.25, 5):
            o = side * R * math.cos(th) + out * R * math.sin(th) + out * 0.12
            p.seg('galv', A + ax * c0 + o, A + ax * c1 + o, 0.035, 0.01)
    return p
def ladder_leg():
    A = ladder_axis(2.4); B = ladder_axis(TB + 1.1)
    return ladder((A, B), cage_from=2.2, cage_to=np.linalg.norm(B - A) - 1.15, out=(1.0, 0.0, 1.0))
TL_A = math.radians(60)
def ladder_tank():
    c, s = math.cos(TL_A), math.sin(TL_A); r = TR + 0.24
    A = (r * c, TB + 0.0, r * s); B = (r * c, TTOP + 1.0, r * s)
    return ladder((A, B), w=0.21, cage_from=2.2, cage_to=CH * NC - 0.2, out=(c, 0.0, s))
def roof_ladder():
    """Escada de telhado do beiral ate o alcapao (pivo: centro, cota do topo do costado)."""
    p = Piece(); c, s = math.cos(TL_A), math.sin(TL_A); RE = TR + 0.15; H = TAPEX - TTOP
    ys = lambda r: 0.04 + (RE - r) / (RE - 0.3) * (H - 0.14)
    A = np.array([(RE - 0.05) * c, ys(RE - 0.05) + 0.08, (RE - 0.05) * s]); B = np.array([2.75 * c, ys(2.75) + 0.08, 2.75 * s])
    side = unit(np.cross(unit(B - A), (c, 0, s))) if False else np.array([-s, 0.0, c])
    for k in (-1, 1): p.seg('galv', A + side * k * 0.21, B + side * k * 0.21, 0.05, 0.012)
    Ln = np.linalg.norm(B - A)
    for t in np.arange(0.2, Ln, 0.3): C = A + unit(B - A) * t; seg_cyl(p, 'galv', C - side * 0.21, C + side * 0.21, 0.014, 6)
    for t in (0.1, Ln - 0.1):
        C = A + unit(B - A) * t
        for k in (-1, 1): seg_cyl(p, 'galv', C + side * k * 0.21, C + side * k * 0.21 - np.array([0, 0.08, 0]), 0.012, 4)
    return p

# ============================================================================ cerca e terreno (pivo: chao)
def fence_panel(L1):
    """Trecho de tela de arame (pivo: inicio, chao; ao longo de +X, lado de fora em +Z): tubo de cima, arame de baixo, malha em losango,
    3 fios de arame farpado nos bracos."""
    p = Piece(); h = 1.95; s = 0.16
    seg_cyl(p, 'galv', (0.04, h, 0), (L1 - 0.04, h, 0), 0.021, 8); seg_cyl(p, 'galv', (0.04, 0.06, 0), (L1 - 0.04, 0.06, 0), 0.006, 4)
    for k in range(-int(h / s), int(L1 / s) + 1):
        x0 = k * s
        for d in (1, -1):
            xa, ya = (x0, 0.06) if d > 0 else (x0, h - 0.03)
            xb, yb = xa + (h - 0.09), (h - 0.03 if d > 0 else 0.06)
            t0 = max(0.0, (0.04 - xa) / (xb - xa)); t1 = min(1.0, (L1 - 0.04 - xa) / (xb - xa))
            if t1 - t0 < 0.02: continue
            A = (xa + (xb - xa) * t0, ya + (yb - ya) * t0, 0.0); B = (xa + (xb - xa) * t1, ya + (yb - ya) * t1, 0.0)
            p.seg('mesh', A, B, 0.006, 0.006)
    for (dz, dy) in ((0.12, 2.06), (0.24, 2.18), (0.36, 2.3)):
        p.seg('galv', (0.0, dy, dz), (L1, dy, dz), 0.005, 0.005)
        for x in np.arange(0.1, L1, 0.15): p.seg('galv', (x - 0.02, dy - 0.02, dz), (x + 0.02, dy + 0.02, dz), 0.004, 0.004)
    return p
def fence_post(term=False):
    """Mourao de tubo galvanizado com tampa e braco de arame farpado a 45 graus para fora (+Z); terminal mais grosso."""
    p = Piece(); r = 0.045 if term else 0.032; h = 2.0
    p.cyl('concrete', 0.15, -0.2, 0.03, 0, 0, 12); p.cyl('galv', r, 0.03, h, 0, 0, 12); lathe(p, 'galv', [(r + 0.008, h), (r + 0.008, h + 0.03), (0.0, h + 0.06)], sec=12)
    seg_cyl(p, 'galv', (0, h - 0.05, 0), (0, h + 0.3, 0.38), 0.016, 6)
    if term:
        for y in (0.4, 1.0, 1.6): p.box('galv', -0.05, 0.05, y, y + 0.06, -0.05, 0.05)
    return p
def gate_leaf(w=1.95, h=1.9):
    """Folha de portao de tubo e tela (pivo: dobradica, embaixo; ao longo de +X): quadro, travessa do meio, diagonal, tela, ferrolho."""
    p = Piece(); r = 0.022
    for (a, b) in (((0.05, 0.05), (0.05, h)), ((w - 0.03, 0.05), (w - 0.03, h)), ((0.05, 0.05), (w - 0.03, 0.05)), ((0.05, h), (w - 0.03, h)), ((0.05, h / 2), (w - 0.03, h / 2)), ((0.05, 0.05), (w - 0.03, h))):
        seg_cyl(p, 'galv', (a[0], a[1], 0), (b[0], b[1], 0), r, 8)
    q = fence_panel(w - 0.1)
    for ms in q.parts.get('mesh', []): mm = ms.copy(); mm.apply_translation([0.05, 0, 0]); mm.apply_scale([1, (h - 0.05) / 1.95, 1]) if False else None; p.add('mesh', mm)
    for y in (0.3, 1.5): p.cyl('galv', 0.03, y, y + 0.1, 0.0, 0.0, 8)
    p.box('steel_d', w - 0.12, w - 0.02, 1.0, 1.12, -0.04, 0.04)
    return p
def light_pole():
    """Poste de aco com braco e luminaria (pivo: chao)."""
    p = Piece(); p.cyl('concrete', 0.3, -0.2, 0.3, 0, 0, 12); lathe(p, 'galv', [(0.12, 0.3), (0.1, 0.4), (0.07, 6.0)], sec=12)
    seg_cyl(p, 'galv', (0, 5.8, 0), (1.4, 6.1, 0), 0.04, 8); p.cham('galv', 1.2, 1.9, 5.98, 6.14, -0.18, 0.18, 0.03); p.box('lamp_glass', 1.25, 1.85, 5.96, 5.98, -0.14, 0.14)
    p.box('galv', -0.1, 0.1, 1.2, 1.6, 0.07, 0.15)
    return p
def sign_plate():
    """Placa azul sem texto com pictograma de gota (pivo: centro, na cerca; frente +Z)."""
    p = Piece(); p.cham('sign_b', -0.35, 0.35, 0.0, 0.5, 0.0, 0.012, 0.004)
    pts = [(0.0, 0.42)] + [(0.13 * math.cos(a), 0.2 + 0.13 * math.sin(a)) for a in np.linspace(-0.3, math.pi + 0.3, 10)]
    p.hull('paint_w', [(x, y, z) for (x, y) in pts for z in (0.012, 0.016)])
    for x in (-0.3, 0.3):
        for y in (0.05, 0.45): p.cyl('galv', 0.01, 0.012, 0.02, x, y, 6) if False else p.add('galv', trimesh.creation.cylinder(radius=0.01, height=0.01, sections=6, transform=tr(x, y, 0.016)))
    return p
def el_cabinet():
    """Armario eletrico verde em base de concreto (pivo: centro, chao)."""
    p = Piece(); p.cham('concrete', -0.6, 0.6, -0.2, 0.15, -0.4, 0.4, 0.02); p.cham('frame', -0.5, 0.5, 0.15, 1.5, -0.3, 0.3, 0.02)
    p.cham('frame', -0.55, 0.55, 1.5, 1.56, -0.35, 0.35, 0.01)
    for x in (-0.25, 0.25): p.box('frame', x - 0.22, x + 0.22, 0.22, 1.42, 0.3, 0.31)
    for x in (-0.06, 0.06): p.box('steel_d', x - 0.015, x + 0.015, 0.75, 0.95, 0.31, 0.33)
    p.box('yellowp', -0.1, 0.1, 1.2, 1.3, 0.31, 0.312)
    return p
def manhole():
    p = Piece(); ring_y(p, 'concrete', 0.0, 0.55, -0.2, 0.04, sec=32); p.cyl('iron', 0.38, 0.04, 0.06, 0, 0, 32)
    for k in range(-3, 4): p.box('dark', k * 0.1 - 0.015, k * 0.1 + 0.015, 0.06, 0.065, -math.sqrt(max(0.0, 0.33 ** 2 - (k * 0.1) ** 2)), math.sqrt(max(0.0, 0.33 ** 2 - (k * 0.1) ** 2)))
    return p
def tree(h=6.0, r=1.9, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.18, 0.0), (0.13, 0.5), (0.09, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    return p
def bush(r=0.5, seed=3):
    p = Piece(); rng = np.random.default_rng(seed); p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
SX0, SX1, SZ0, SZ1 = -16.0, 16.0, -14.0, 22.0
GY = -0.2
def site():
    """Terreno: patio de brita dentro da cerca, gramado fora, caminho de concreto com juntas do portao ate a casa, calcada com juntas e
    meio-fio, rua com faixa amarela, entrada de carros de asfalto com rebaixo na calcada."""
    p = Piece(); yard = sbox(-FX, -FZ, FX, FZ)
    path = sbox(PG[0] - 0.1, HZ + 0.9, PG[1] + 0.1, 14.0); drive = sbox(VG[0], FZ, VG[1], 16.0)
    walk = sbox(SX0, 14.0, SX1, 16.0).difference(drive); street = sbox(SX0, 16.15, SX1, SZ1)
    ext_y(p, 'gravel', yard.difference(path).difference(OUTL.buffer(0.9, join_style=2)), GY, 0.0)
    ext_y(p, 'concrete', OUTL.buffer(0.9, join_style=2).difference(OUTL).difference(sbox(DOOR_X - 0.8, HZ, DOOR_X + 0.8, HZ + 0.9)), GY, 0.03)
    ext_y(p, 'grass', sbox(SX0, SZ0, SX1, 14.0).difference(yard).difference(path).difference(drive), GY, 0.0)
    for (z0, z1) in zip(np.arange(HZ + 0.9, 14.0, 1.2)[:-1], np.arange(HZ + 0.9, 14.0, 1.2)[1:]):
        ext_y(p, 'concrete', path.intersection(sbox(-20, z0 + 0.005, 20, z1 - 0.005)), GY, 0.06)
    last = np.arange(HZ + 0.9, 14.0, 1.2)[-1]; ext_y(p, 'concrete', path.intersection(sbox(-20, last + 0.005, 20, 14.0)), GY, 0.06)
    ext_y(p, 'dark', path.buffer(-0.004, join_style=2), GY, 0.05)
    for x0 in np.arange(SX0, SX1, 1.5):
        q = sbox(x0 + 0.005, 14.0, x0 + 1.5 - 0.005, 16.0).intersection(walk)
        if q.area > 1e-6: ext_y(p, 'concrete', q, GY, 0.12)
    ext_y(p, 'dark', walk.buffer(-0.004, join_style=2), GY, 0.11)
    ext_y(p, 'concrete', sbox(SX0, 16.0, SX1, 16.15).difference(drive), GY, 0.15)
    ext_y(p, 'asphalt', drive, GY, 0.0); ext_y(p, 'asphalt', street, GY, 0.0)
    for x in np.arange(SX0 + 0.5, SX1, 3.0): p.box('yellowp', x, x + 1.5, 0.0, 0.004, 19.0, 19.12)
    return p

# ============================================================================ portas
def door_steel(w=0.9, h=2.14, t=0.045):
    """Porta de chapa de aco com veneziana embaixo, visor com tela e barra (pivo: dobradica, embaixo)."""
    p = Piece(); p.cham('door', 0.0, w, 0.0, h, -t / 2, t / 2, 0.004)
    for z in (1, -1):
        zz = sorted((z * t / 2, z * (t / 2 + 0.006)))
        for k in range(8): y = 0.15 + k * 0.06; p.box('steel_d', 0.15, w - 0.15, y, y + 0.025, *zz)
        p.box('steel_d', 0.2, w - 0.2, 1.45, 1.49, *zz); p.box('steel_d', 0.2, w - 0.2, 1.85, 1.89, *zz)
        p.box('steel_d', 0.2, 0.24, 1.45, 1.89, *zz); p.box('steel_d', w - 0.24, w - 0.2, 1.45, 1.89, *zz)
    p.box('glass_w', 0.24, w - 0.24, 1.49, 1.85, -0.004, 0.004)
    for z in (1, -1):
        p.cham('galv', w - 0.12, w - 0.06, 0.95, 1.15, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.seg('galv', (w - 0.09, 1.05, z * t / 2), (w - 0.09, 1.05, z * (t / 2 + 0.05)), 0.016); p.seg('galv', (w - 0.09, 1.05, z * (t / 2 + 0.05)), (w - 0.22, 1.05, z * (t / 2 + 0.05)), 0.02)
    for yy in (0.25, 1.1, 1.85): p.cyl('galv', 0.01, yy, yy + 0.12, 0.0, t / 2 + 0.002, 8)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': round(float(ry), 3), 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': e['rotY'], 'open': round(float(ry + door), 3)}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)

pieces = {'w_win': wall('win'), 'w_door': wall('door'), 'w_plain': wall('plain'), 'w_win_r': wall('win', 1), 'w_plain_l': wall('plain', -1)}
pieces.update({
    'ph_roof': ph_roof(), 'downspout': downspout_piece(), 'ph_floor': ph_floor(), 'pumpset': pumpset(), 'valve_set': valve_set(),
    'el_panel': el_panel(), 'workbench': workbench(), 'extinguisher': extinguisher(), 'pendant_lamp': pendant_lamp(),
    'leg': leg(), 'ring_girder': ring_girder(), 'riser': riser(),
    'tank_course_a': tank_course(0), 'tank_course_b': tank_course(1), 'tank_course_top': tank_course(3, False),
    'tank_bottom': tank_bottom(), 'tank_roof': tank_roof(), 'balcony': balcony(),
    'ladder_leg': ladder_leg(), 'ladder_tank': ladder_tank(), 'roof_ladder': roof_ladder(),
    'fence_panel': fence_panel(2.5), 'fence_panel_s': fence_panel(7.4 / 3), 'fence_panel_m': fence_panel(2.4),
    'fence_post': fence_post(), 'fence_post_t': fence_post(True), 'gate_leaf': gate_leaf(1.95), 'gate_leaf_p': gate_leaf(1.1),
    'light_pole': light_pole(), 'sign_plate': sign_plate(), 'el_cabinet': el_cabinet(), 'manhole': manhole(),
    'site': site(), 'tree': tree(), 'tree_b': tree(5.0, 1.6, 'leaf2', 4), 'bush': bush(), 'bush_s': bush(0.35, 7),
    'door_leaf_steel': door_steel(0.9, 2.13), 'player_scale_ref': player_ref()})
for i in (1, 2, 3): pieces[f'strut_{i}'] = strut(LEVELS[i])
for i in range(4): pieces[f'brace_{i}'] = brace(i)

# ============================================================================ montagem
tg = ['house', 'ext']
put('w_door', DOOR_X, Y0, HZ, 0, tg + ['front']); put('w_win', 0, Y0, HZ, 0, tg + ['front']); put('w_win', 2, Y0, HZ, 0, tg + ['front'])
put('w_plain', -2, Y0, -HZ, 180, tg + ['back']); put('w_win', 0, Y0, -HZ, 180, tg + ['back']); put('w_plain', 2, Y0, -HZ, 180, tg + ['back'])
put('w_plain_l', -HX, Y0, -1, -90, tg + ['left']); put('w_win_r', -HX, Y0, 1, -90, tg + ['left'])
put('w_win_r', HX, Y0, -1, 90, tg + ['right']); put('w_plain_l', HX, Y0, 1, 90, tg + ['right'])
put('ph_roof', 0, Y0, 0, 0, ['house', 'roof']); put('downspout', HX - 1.0, Y0, -HZ, 180, ['house', 'ext'])
put('ph_floor', 0, Y0, 0, 0, ['house'])
g = ['house']
put('valve_set', 0, Y0, 0, 0, g)
for xp in (0.9, 1.9): put('pumpset', xp, Y0, -1.15, 0, g)
put('el_panel', -HX + T, Y0, -0.3, 90, g); put('workbench', -2.0, Y0, -HZ + T, 0, g); put('extinguisher', -1.05, Y0, HZ - T, 180, g)
for (x, z) in ((-1.5, 0.3), (1.3, 0.5)): put('pendant_lamp', x, Y0 + CEIL - 0.01, z, 0, g)
hx, hz = hinge(DOOR_X, HZ, 0, -0.45, -0.13); put('door_leaf_steel', hx, Y0 + 0.012, hz, 0, ['house', 'front', 'ext'], door=90)
# torre e reservatorio
tw = ['tower']
for r in (0, 90, 180, 270):
    put('leg', 0, 0, 0, r, tw)
    for i in (1, 2, 3): put(f'strut_{i}', 0, 0, 0, r, tw)
    for i in range(4): put(f'brace_{i}', 0, 0, 0, r, tw)
put('ring_girder', 0, YT, 0, 0, tw); put('riser', 0, 0, 0, 0, tw)
tk = ['tank']
for k in range(NC): put('tank_course_top' if k == NC - 1 else ('tank_course_a' if k % 2 == 0 else 'tank_course_b'), 0, TB + k * CH, 0, 0, tk)
put('tank_bottom', 0, TB, 0, 0, tk); put('balcony', 0, TB, 0, 0, tk); put('tank_roof', 0, TTOP, 0, 0, tk + ['roof']); put('roof_ladder', 0, TTOP, 0, 0, tk + ['roof'])
put('ladder_leg', 0, 0, 0, 0, tw); put('ladder_tank', 0, 0, 0, 0, tk)
# cerca
st = ['site']
def fence_run(x0, z0, ry, lens, posts=True):
    r = math.radians(ry); d = np.array([math.cos(r), -math.sin(r)]); p0 = np.array([x0, z0], float); s = 0.0
    for (n, l) in lens:
        q = p0 + d * s; put(n, q[0], 0, q[1], ry, st); s += l
        if posts: q = p0 + d * s; put('fence_post', q[0], 0, q[1], ry, st)
    return L
fence_run(-FX, FZ, 0, [('fence_panel_s', 7.4 / 3)] * 3); L.pop()
fence_run(PG[1], FZ, 0, [('fence_panel_m', 2.4)]); L.pop()
fence_run(VG[1], FZ, 0, [('fence_panel', 2.5)] * 2); L.pop()
fence_run(FX, -FZ, 180, [('fence_panel', 2.5)] * 8); L.pop()
fence_run(FX, FZ, 90, [('fence_panel', 2.5)] * 8); L.pop()
fence_run(-FX, -FZ, -90, [('fence_panel', 2.5)] * 8); L.pop()
for (x, z, ry) in ((-FX, FZ, 0), (FX, FZ, 0), (FX, -FZ, 180), (-FX, -FZ, 180), (PG[0], FZ, 0), (PG[1], FZ, 0), (VG[0], FZ, 0), (VG[1], FZ, 0)):
    put('fence_post_t', x, 0, z, ry, st)
put('gate_leaf_p', PG[0] + 0.05, 0.06, FZ, 0, st, door=90)
put('gate_leaf', VG[0] + 0.05, 0.0, FZ, 0, st, door=90); put('gate_leaf', VG[1] - 0.05, 0.0, FZ, 180, st, door=-90)
# terreno
put('site', 0, 0, 0, 0, st)
put('light_pole', -7.0, 0, 7.0, 0, st); put('sign_plate', -5.0, 1.15, FZ + 0.03, 0, st); put('el_cabinet', 7.5, 0, -1.0, 90, st); put('manhole', 3.0, 0, -4.0, 0, st)
for (x, z, n) in ((-13.0, -8.0, 'tree'), (13.0, -6.0, 'tree_b'), (-13.0, 5.0, 'tree_b'), (13.5, 7.0, 'tree'), (-6.0, -12.3, 'tree_b'), (6.5, -12.3, 'tree'), (-12.5, 12.5, 'tree'), (12.5, 12.5, 'tree_b')):
    put(n, x, 0, z, 0, st)
for k, x in enumerate(list(np.arange(-9.2, -3.4, 1.15)) + list(np.arange(6.2, 9.6, 1.15))): put('bush' if k % 2 == 0 else 'bush_s', x, 0, 11.4, 0, st)
put('player_scale_ref', 0.0, 0.0, 12.5); put('player_scale_ref', -1.2, Y0, 1.2, 0, ['house'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'floor_level': Y0,
                       'pump_house': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 1, 'ceiling': CEIL, 'roof_level': HW, 'parapet': HP},
                       'tower': {'legs': 4, 'half_span_base': LB, 'half_span_top': LT, 'levels': LEVELS},
                       'tank': {'radius': TR, 'shell_base': TB, 'shell_top': TTOP, 'apex': TAPEX, 'courses': NC, 'balcony': [BR0, BR1]},
                       'fence': {'x': [-FX, FX], 'z': [-FZ, FZ], 'pedestrian_gate': list(PG), 'vehicle_gate': list(VG)},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1]},
                       'roof': 'pump house: flat slab with membrane and parapet; tank: conical steel roof with ribs, vent, hatch and finial',
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
