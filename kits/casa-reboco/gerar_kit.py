"""Kit 32: sobrado europeu de reboco com garagem, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Casa de 8 x 10 m e 2 andares de reboco creme com embasamento de tijolo, vergas de tijolo em espelho, peitoris de pedra, janelas
de batente brancas com bandeira, porta com vidro lateral e chapeu de 2 aguas sobre misulas, telhado de 40 graus de telha de barro
com cumeeira de telha capa, testeiras brancas, calhas e condutores, chamine de tijolo com vasos no frontao dos fundos.
Garagem de 4 x 8 m encostada na lateral, com frontao, portao de 2 folhas de tabuas, janela e porta lateral, rufo junto da casa.
Dentro: hall com escada, sala, cozinha com jantar, area de servico com porta para a garagem; 3 quartos e banheiro em cima.
Jardim com gramado, entrada de carro, caminho de lajotas, cerca de estacas, cerca-viva e cerca de tabuas nos fundos.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'render': (232, 222, 196), 'brick': (150, 70, 52), 'cill': (206, 200, 186), 'trim': (246, 246, 242), 'frame': (246, 246, 242),
                  'sash': (250, 250, 248), 'shingles': (176, 82, 56), 'ridge': (160, 70, 48), 'door': (40, 70, 60), 'gdoor': (226, 220, 206),
                  'floor': (168, 124, 84), 'plaster': (240, 236, 226), 'tile': (230, 232, 228), 'slate': (84, 88, 92), 'concrete': (176, 172, 164),
                  'paving': (190, 180, 160), 'grass': (100, 146, 72), 'hedge': (66, 104, 54), 'fencew': (150, 112, 76), 'picket': (244, 242, 236),
                  'attic': (150, 120, 86), 'gutter': (240, 240, 236), 'dark': (30, 30, 32), 'iron': (36, 38, 40), 'pot': (178, 90, 60), 'flash': (150, 154, 156)},
           texturas={'render': 'render', 'brick': 'brick', 'cill': 'stone2', 'shingles': 'roof_tiles', 'floor': 'planks', 'plaster': 'plaster',
                     'concrete': 'render', 'paving': 'stone', 'fencew': 'planks', 'attic': 'planks', 'gdoor': 'paint'},
           out=OUT)
D.METAL.update({'flash'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.3; H = 3.0; SLAB = 0.2; RAISE = 0.3
H0 = H - SLAB
def lvl(fl): return RAISE + fl * H
Y0 = lvl(0); YE = lvl(2)
HX = 4.0; HZ = 5.0                                 # casa: x de -4 a 4, z de -5 a 5
GX0, GX1, GZ0, GZ1 = 4.0, 8.0, -3.0, 5.0          # garagem
GY = 0.05; GH = 2.7; GYE = GY + GH                 # piso e beiral da garagem
ANG = 40.0; KR = math.tan(math.radians(ANG)); CS = math.cos(math.radians(ANG))
SX = HX; RIDGE = SX * KR; GSX = (GX1 - GX0) / 2; GRIDGE = GSX * KR
OVE = 0.35; OVF = 0.3; OVG = 0.25
TV = 0.07; BUMP = 0.02
configurar_telhado(TV, BUMP, ANG)
NR = 16; RS_ = H / NR; TR = 0.26; SW_ = 1.05; RUN = (NR - 1) * TR
SX0 = 2.6; SZ0 = 3.3; SZ1 = SZ0 - RUN               # escada: lado aberto em x = 2,6, pe na frente, sobe para -Z
XW = 0.0                                           # parede do hall (eixo)

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

# ============================================================================ paredes de reboco
def wall_core(p, y0, top, holes, base=True):
    """Parede estanque: reboco por fora (embasamento de tijolo no pe, de y0 ate 0,15), gesso por dentro (para 5 mm abaixo do topo)."""
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    yb = 0.15 if base else None
    ys = sorted(set([y0, top - 0.005, top] + ([yb] if base else []) + [max(y0, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return None if ys[j] >= top - 0.0051 else 'plaster'
        return 'brick' if (base and cy < yb) else 'render'
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
def plinth(p, segs, y0, yb=0.15):
    """Embasamento de tijolo 2 cm saliente, com capa chanfrada de tijolo em pe."""
    for (a, b) in segs:
        if b - a < 0.01: continue
        prof_x(p, 'brick', a, b, [(0.0, y0), (0.02, y0), (0.02, yb), (0.0, yb + 0.02)])
def casement(p, ow, oy0, oy1, lites=2, transom=True):
    """Janela de batente branca no vao (face externa em z = 0, recuada 12 cm): marco, montantes, bandeira, folhas com vidro,
    peitoril de pedra com pingadeira e verga de tijolo em espelho."""
    x = ow / 2; f = 0.06; zf0, zf1 = -0.2, -0.1
    p.box('frame', -x, -x + f, oy0, oy1, zf0, zf1); p.box('frame', x - f, x, oy0, oy1, zf0, zf1)
    p.box('frame', -x + f, x - f, oy1 - f, oy1, zf0, zf1); p.box('frame', -x + f, x - f, oy0, oy0 + f, zf0, zf1)
    yt = oy1 - 0.42 if transom else oy1 - f
    if transom: p.box('frame', -x + f, x - f, yt - 0.03, yt + 0.03, zf0, zf1)
    xs = [-x + f + (ow - 2 * f) * i / lites for i in range(lites + 1)]
    for xm in xs[1:-1]: p.box('frame', xm - 0.03, xm + 0.03, oy0 + f, oy1 - f, zf0, zf1)
    def leaf(a, b, c, d):
        s = 0.05
        p.cham('sash', a, a + s, c, d, zf1 - 0.0, zf1 + 0.03, 0.006); p.cham('sash', b - s, b, c, d, zf1, zf1 + 0.03, 0.006)
        p.cham('sash', a + s - 0.002, b - s + 0.002, d - s, d, zf1, zf1 + 0.03, 0.006); p.cham('sash', a + s - 0.002, b - s + 0.002, c, c + s, zf1, zf1 + 0.03, 0.006)
        p.box('glass', a + s - 0.004, b - s + 0.004, c + s - 0.004, d - s + 0.004, zf1 + 0.012, zf1 + 0.018)
    for i in range(lites):
        a = xs[i] + (0.03 if i else 0.0); b = xs[i + 1] - (0.03 if i < lites - 1 else 0.0)
        leaf(a + 0.005, b - 0.005, oy0 + f + 0.005, (yt - 0.03 if transom else oy1 - f) - 0.005)
        if transom: p.box('glass', a, b, yt + 0.03, oy1 - f, zf0 + 0.045, zf0 + 0.055)
        if i == 0 or i == lites - 1:
            hx_ = (b - 0.06) if i == 0 and lites > 1 else (a + 0.06)
            p.box('iron', hx_ - 0.008, hx_ + 0.008, oy0 + 0.35, oy0 + 0.5, zf1 + 0.03, zf1 + 0.05)
    # peitoril de pedra, verga de tijolo em espelho e reboco do vao
    prof_x(p, 'cill', -x - 0.08, x + 0.08, [(zf0 + 0.005, oy0 - 0.06), (0.06, oy0 - 0.06), (0.07, oy0 - 0.05), (0.07, oy0 - 0.03), (0.0, oy0 + 0.005), (zf0 + 0.005, oy0 + 0.005)])
    n = max(3, int(round((ow + 0.2) / 0.075)))
    for i in range(n):
        xa = -x - 0.1 + i * (ow + 0.2) / n + 0.004; xb = -x - 0.1 + (i + 1) * (ow + 0.2) / n - 0.004
        p.box('brick', xa, xb, oy1 + 0.006, oy1 + 0.215, -0.02, 0.012)
    p.box('cill', -x - 0.1, x + 0.1, oy1 + 0.002, oy1 + 0.006, -0.02, 0.01)
    return (-x - 0.1, x + 0.1)
WINS = {'win': (1.2, 0.9, 2.2, 2), 'wide': (1.7, 0.6, 2.2, 3), 'small': (0.6, 1.4, 2.2, 1), 'gwin': (1.0, 1.1, 2.0, 2)}
def wall(kind='plain', fl=0, top=None, y0=None, base=None):
    """Modulo de 2 m de parede de reboco (pivo: face externa, cota do piso). kind: plain, win, wide (3 folhas), small (banheiro),
    door (porta da frente), bdoor (porta dos fundos/lateral), din (porta interna da casa para a garagem, so vao com batente)."""
    p = Piece(); top = top if top is not None else (H0 if fl == 0 else H); y0 = y0 if y0 is not None else (-RAISE if fl == 0 else -SLAB)
    base = (fl == 0) if base is None else base
    holes = []; gaps = []
    if kind in WINS:
        ow, oy0, oy1, n = WINS[kind]; holes = [(-ow / 2, ow / 2, oy0, oy1)]
    if kind == 'door': holes = [(-0.65, 0.65, 0.0, 2.25)]; gaps = [(-0.8, 0.8)]
    if kind in ('bdoor', 'din'): holes = [(-0.5, 0.5, 0.0, 2.15)]; gaps = [(-0.62, 0.62)]
    wall_core(p, y0, top, holes, base)
    if kind in WINS:
        ow, oy0, oy1, n = WINS[kind]; casement(p, ow, oy0, oy1, n, transom=(kind != 'small'))
        if kind == 'small': p.box('glass', -ow / 2 + 0.1, ow / 2 - 0.1, oy0 + 0.1, oy1 - 0.1, -0.087, -0.083) if False else None
    if kind == 'door':
        x = 0.65; yt = 2.25
        p.box('frame', -x, -x + 0.07, 0.0, yt, -0.22, -0.08); p.box('frame', x - 0.07, x, 0.0, yt, -0.22, -0.08); p.box('frame', -x + 0.07, x - 0.07, yt - 0.07, yt, -0.22, -0.08)
        p.box('frame', 0.2, 0.26, 0.0, yt - 0.07, -0.22, -0.08)                                   # montante do vidro lateral
        p.box('frame', 0.26, x - 0.07, 0.0, 0.6, -0.2, -0.1); p.box('glass', 0.26, x - 0.07, 0.6, yt - 0.07, -0.153, -0.147)
        for yy in (1.1, 1.6): p.box('frame', 0.26, x - 0.07, yy - 0.012, yy + 0.012, -0.16, -0.14)
        p.box('frame', -x + 0.07, -x + 0.085, 0.015, yt - 0.07, -0.13, -0.11)
        prof_x(p, 'cill', -x, x, [(-T + 0.004, -0.03), (0.06, -0.03), (0.07, -0.02), (0.07, 0.012), (-T + 0.004, 0.012)])
        n = 18
        for i in range(n):
            xa = -x - 0.1 + i * (2 * x + 0.2) / n + 0.004; xb = -x - 0.1 + (i + 1) * (2 * x + 0.2) / n - 0.004
            p.box('brick', xa, xb, yt + 0.006, yt + 0.215, -0.02, 0.012)
        p.box('cill', -x - 0.1, x + 0.1, yt + 0.002, yt + 0.006, -0.02, 0.01)
    if kind in ('bdoor', 'din'):
        x = 0.5; yt = 2.15
        p.box('frame', -x, -x + 0.06, 0.0, yt, -0.2, -0.08); p.box('frame', x - 0.06, x, 0.0, yt, -0.2, -0.08); p.box('frame', -x + 0.06, x - 0.06, yt - 0.06, yt, -0.2, -0.08)
        p.box('frame', -x + 0.06, -x + 0.075, 0.015, yt - 0.06, -0.13, -0.11)
        prof_x(p, 'cill', -x, x, [(-T + 0.004, -0.03), (0.04, -0.03), (0.05, -0.02), (0.05, 0.012), (-T + 0.004, 0.012)])
        if kind == 'bdoor':
            for i in range(14):
                xa = -x - 0.1 + i * 1.2 / 14 + 0.004; xb = -x - 0.1 + (i + 1) * 1.2 / 14 - 0.004
                p.box('brick', xa, xb, yt + 0.006, yt + 0.215, -0.02, 0.012)
            p.box('cill', -x - 0.1, x + 0.1, yt + 0.002, yt + 0.006, -0.02, 0.01)
    if base:
        segs = [(-W / 2, W / 2)]
        for (a, b) in gaps: segs = [s for (c, d) in segs for s in ((c, min(d, a)), (max(c, b), d)) if s[1] - s[0] > 1e-3]
        plinth(p, segs, y0)
    return p
def corner(y0, top, base=True):
    """Quina externa (pivo: quina externa, cota do piso; paredes em -X e -Z): nucleo de reboco e quina do embasamento."""
    p = Piece(); e = 0.004
    p.box('render', -T + 0.004, e, y0 + 0.003, top - 0.004, -T + 0.004, e)
    if base:
        p.box('brick', -0.2, 0.022, y0 + 0.004, 0.15, -0.2, 0.022)
        p.hull('brick', [(x, 0.15, z) for (x, z) in ((-0.2, -0.2), (0.022, -0.2), (0.022, 0.022), (-0.2, 0.022))] + [(x, 0.17, z) for (x, z) in ((-0.2, -0.2), (0.0, -0.2), (0.0, 0.0), (-0.2, 0.0))])
    return p

# ============================================================================ frontoes e chamine
def gable(span, rise, vent=True, win=False):
    """Frontao de reboco (pivo: face da parede no eixo, cota do beiral): miolo triangular; respiro de tijolo ou janela do sotao."""
    p = Piece(); A = rise - 0.02
    core = Polygon([(-span, 0.0), (span, 0.0), (0.0, A)])
    if win:
        ow, oy0, oy1 = 0.7, 0.6, 1.5; hole = sbox(-ow / 2, oy0, ow / 2, oy1)
        ext(p, 'render', core.difference(hole), -T + 0.02, 0.0); ext(p, 'plaster', core.buffer(-0.01).difference(hole), -T, -T + 0.02)
        casement(p, ow, oy0, oy1, 1, transom=False); p.box('dark', -ow / 2, ow / 2, oy0, oy1, -T + 0.01, -T + 0.02)
    else:
        ext(p, 'render', core, -T, 0.0)
    if vent:
        vy = A * 0.45
        for k in range(4):
            yy = vy + k * 0.09
            for i in range(5):
                xa = -0.22 + i * 0.09 + (0.045 if k % 2 else 0.0)
                if xa + 0.08 > 0.25: continue
                p.box('brick', xa, xa + 0.07, yy, yy + 0.07, -0.01, 0.015)
        p.box('cill', -0.3, 0.3, vy - 0.05, vy - 0.01, -0.01, 0.04); p.box('cill', -0.3, 0.3, vy + 0.36, vy + 0.4, -0.01, 0.04)
    return p
def chimney(y0, y1):
    """Chamine de tijolo no frontao dos fundos (pivo: centro do pe, no topo da parede): fuste, 2 fiadas salientes, capa e 2 vasos."""
    p = Piece(); a, b = 0.42, 0.3
    p.box('brick', -a, a, y0, y1, -b, b)
    for (ya, d) in ((y1 - 0.45, 0.03), (y1 - 0.38, 0.05)): p.box('brick', -a - d, a + d, ya, ya + 0.07, -b - d, b + d)
    p.cham('cill', -a - 0.06, a + 0.06, y1, y1 + 0.06, -b - 0.06, b + 0.06, 0.01)
    p.box('cill', -a + 0.03, a - 0.03, y1 + 0.06, y1 + 0.12, -b + 0.03, b - 0.03)
    for xx in (-0.2, 0.2):
        lathe(p, 'pot', [(0.11, y1 + 0.1), (0.1, y1 + 0.3), (0.085, y1 + 0.42), (0.1, y1 + 0.46), (0.1, y1 + 0.5)], xx, 0.0, 0.0, 14)
        p.cyl('dark', 0.07, y1 + 0.48, y1 + 0.501, xx, 0.0, 12)
    # rufo de chumbo na passagem pelo telhado
    return p

# ============================================================================ telhado de telha de barro a 40 graus
def roof_strip(x0=-W / 2, x1=W / 2, rake=0, over=0.0, sx=SX):
    """Faixa de 2 m de uma agua (pivo: plano da parede, cota do beiral; beiral em z = over, sobe para -Z ate a cumeeira em z = -sx).
    over > 0: testeira, calha e cachorros; over = 0: encosta numa parede (rufo). rake = -1/+1: testeira inclinada na ponta x0/x1."""
    p = Piece(); f = lambda a, b: -KR * b
    poly = sbox(x0, -sx, x1, over)
    sheared(p, 'plaster', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: over - b, lambda d0, d1: sbox(-50, over - d1, 50, over - d0), over + sx + 0.01,
                    lambda v, n: np.stack([v[:, 0] / TILE, (over - v[:, 2]) / CS / TILE], 1))
    if over > 0:
        yb = -KR * over
        a = x0 + (-0.03 if rake < 0 else 0.001); b = x1 + (0.03 if rake > 0 else -0.001)
        prof_x(p, 'trim', a, b, crect(over - 0.02, over + 0.03, yb - 0.17, yb + 0.05, 0.006, (0, 1, 1, 0)))
        prof_x(p, 'trim', a, b, [(0.0, yb - 0.17), (over - 0.02, yb - 0.17), (over - 0.02, yb - 0.15), (0.0, yb - 0.15)])
        gutter_run(p, x0 - (0.03 if rake < 0 else 0), x1 + (0.03 if rake > 0 else 0), over + 0.03, yb + 0.02, caps=(rake < 0, rake > 0))
    if rake:
        xr = x0 if rake < 0 else x1; xa, xb = sorted((xr, xr + rake * 0.035))
        z0 = over + (0.03 if over > 0 else 0.0)
        tp = lambda z: -KR * z + TV + BUMP + 0.03
        prof_x(p, 'trim', xa, xb, [(z0, tp(z0)), (-sx, tp(-sx)), (-sx, KR * sx - 0.2), (z0, -KR * z0 - 0.2)])
    return p
def ridge_cap(z0, z1, rise):
    """Cumeeira de telhas capa (meia-cana) com argamassa (pivo: eixo, cota do beiral)."""
    p = Piece(); y = TV + BUMP + rise - 0.03; n = int((z1 - z0) / 0.33)
    for i in range(n):
        za = z0 + i * (z1 - z0) / n; zb = za + (z1 - z0) / n + 0.02
        q = trimesh.creation.cylinder(radius=0.13, height=zb - za, sections=14)
        q.apply_translation([0, 0, (za + zb) / 2]); q = slice_keep(q, [0, 0, 0], [0, 1, 0])
        q.apply_translation([0, y, 0]); p.add('ridge', q)
    p.hull('render', [(x, yy, z) for z in (z0 + 0.01, z1 - 0.01) for (x, yy) in ((-0.15, y - 0.13 * KR + 0.005), (0.15, y - 0.13 * KR + 0.005), (0.0, y + 0.03))])
    return p
def abutment(z0, z1):
    """Rufo de chapa onde uma agua encosta numa parede (pivo: face da parede, cota do beiral): aba sobre as telhas e aba na parede."""
    p = Piece(); y = TV + BUMP
    p.hull('flash', [(x, -KR * x + y + dy, z) for x in (0.0, 0.18) for z in (z0, z1) for dy in (0.004, 0.012)]) if False else None
    p.hull('flash', [(x, KR * x + y + dy, z) for x in (0.0, 0.18) for z in (z0, z1) for dy in (0.004, 0.012)])
    p.box('flash', 0.0, 0.012, y, y + 0.16, z0, z1)
    return p

# ============================================================================ porta e garagem
def front_door_leaf(w=0.86, h=2.13, t=0.05):
    """Folha da porta da frente: vidro alto em cima, 3 almofadas em baixo, puxador, olho magico e caixa de correio."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.14, w - 0.14, 1.3, h - 0.16, -t, t)] + [tbox(0.14, w - 0.14, y0, y1, z - 0.01, z + 0.01) for (y0, y1) in ((0.16, 0.5), (0.6, 0.86), (0.96, 1.2)) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', 0.136, w - 0.136, 1.296, h - 0.156, -0.004, 0.004)
    for z in (1, -1):
        p.cham('brass', w - 0.11, w - 0.07, 0.85, 1.25, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.seg('brass', (w - 0.09, 1.08, z * t / 2), (w - 0.09, 1.08, z * (t / 2 + 0.05)), 0.016)
    p.cham('brass', w / 2 - 0.15, w / 2 + 0.15, 1.22, 1.27, t / 2, t / 2 + 0.01, 0.003)
    for yy in (0.25, 1.05, 1.85): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def back_door_leaf(w=0.86, h=2.06, t=0.045):
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.12, w - 0.12, 1.0, h - 0.12, -t, t)] + [tbox(0.12, w - 0.12, 0.14, 0.88, z - 0.01, z + 0.01) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', 0.116, w - 0.116, 0.996, h - 0.116, -0.004, 0.004)
    for z in (1, -1):
        p.sphere('brass', 0.028, w - 0.085, 1.0, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.085, 1.0, z * t / 2), (w - 0.085, 1.0, z * (t / 2 + 0.04)), 0.015)
    for yy in (0.25, 1.05, 1.75): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def canopy():
    """Chapeu da porta (pivo: face da parede no eixo da porta, cota do piso): 2 misulas, testeira, telhado de 2 aguas de telha e cumeeira."""
    p = Piece(); y = 2.55; d = 0.75; w = 0.9; k = 0.75
    for s in (-1, 1):
        x = s * (w - 0.08)
        p.hull('trim', [(x + dx, yy, zz) for dx in (-0.04, 0.04) for (zz, yy) in ((-0.01, y - 0.55), (-0.01, y), (d - 0.05, y), (d - 0.08, y - 0.08), (0.12, y - 0.45))])
    p.cham('trim', -w, w, y - 0.02, y + 0.05, -0.01, d, 0.01)
    for s in (-1, 1):
        a, b = sorted((0.0, s * (w + 0.06)))
        f = lambda x: y + 0.05 + (w + 0.06 - abs(x)) * k
        p.hull('trim', [(x, f(x) + dy, z) for x in (a, b) for z in (-0.01, d + 0.04) for dy in (-0.02, 0.0)])
        for i in range(7):
            xa = s * (0.02 + i * 0.14); xb = s * (0.02 + (i + 1) * 0.14)
            xa, xb = sorted((xa, xb))
            if abs(xb) > w + 0.08: continue
            p.hull('shingles', [(x, f(x) + dy, z) for x in (xa, xb) for z in (-0.01, d + 0.06) for dy in (0.0, 0.035)])
    p.hull('trim', [(x, y + 0.05, z) for x in (-w - 0.06, w + 0.06) for z in (d, d + 0.04)] + [(0.0, y + 0.05 + (w + 0.06) * k, d), (0.0, y + 0.05 + (w + 0.06) * k, d + 0.04)])
    p.hull('ridge', [(x, y + 0.05 + (w + 0.06) * k + 0.03 + dy, z) for x in (-0.06, 0.06) for dy in (0.0, 0.06) for z in (-0.01, d + 0.07)])
    p.box('lamp_glass', -0.08, 0.08, y - 0.12, y - 0.02, d * 0.5 - 0.08, d * 0.5 + 0.08); p.box('iron', -0.1, 0.1, y - 0.14, y - 0.12, d * 0.5 - 0.1, d * 0.5 + 0.1)
    return p
def steps(w=0.8, n=2, d=0.9, h=RAISE):
    """Patamar e degraus de pedra (pivo: face da parede no eixo, cota do piso; descem para +Z ate o chao)."""
    p = Piece(); r = h / n
    p.box('cill', -w, w, -0.04, 0.0, 0.003, d); p.box('brick', -w + 0.01, w - 0.01, -h + 0.003, -0.04, 0.003, d - 0.01)
    for i in range(1, n):
        y = -i * r; z0 = d + (i - 1) * 0.3
        p.box('cill', -w, w, y - 0.04, y, z0 - 0.01, z0 + 0.3); p.box('brick', -w + 0.01, w - 0.01, -h + 0.003, y - 0.04, z0 - 0.01, z0 + 0.29)
    return p
def garage_front():
    """Frontao e vao da garagem (pivo: face da frente no eixo da garagem, cota do chao): reboco, embasamento, vao de 2,6 x 2,2 m
    com verga de tijolo, marco e soleira, frontao com respiro."""
    p = Piece(); ow = 2.6; oh = 2.2; x = ow / 2; top = GH
    xs = [-GSX, -x, x, GSX]; ys = [-GY, 0.15, oh, top - 0.005, top]
    def cell(i, j, k):
        if i == 1 and ys[j] >= 0.0 and ys[j + 1] <= oh + 1e-9 and j >= 0 and (ys[j] >= -1e-9 or True) and ys[j + 1] <= oh: return None
        if k == 0: return None if ys[j] >= top - 0.0051 else 'plaster'
        return 'brick' if ys[j + 1] <= 0.15 + 1e-9 else 'render'
    ys = [-GY, 0.0, 0.15, oh, top - 0.005, top]
    def cell(i, j, k):
        cy = (ys[j] + ys[j + 1]) / 2
        if i == 1 and cy < oh: return None
        if k == 0: return None if ys[j] >= top - 0.0051 else 'plaster'
        return 'brick' if cy < 0.15 else 'render'
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
    p.box('frame', -x, -x + 0.08, 0.0, oh, -0.2, -0.06); p.box('frame', x - 0.08, x, 0.0, oh, -0.2, -0.06); p.box('frame', -x + 0.08, x - 0.08, oh - 0.08, oh, -0.2, -0.06)
    p.box('concrete', -x, x, -GY + 0.003, 0.0, -T + 0.001, 0.06)
    n = 34
    for i in range(n):
        xa = -x - 0.12 + i * (ow + 0.24) / n + 0.004; xb = -x - 0.12 + (i + 1) * (ow + 0.24) / n - 0.004
        p.box('brick', xa, xb, oh + 0.006, oh + 0.215, -0.02, 0.012)
    p.box('cill', -x - 0.12, x + 0.12, oh + 0.002, oh + 0.006, -0.02, 0.01)
    plinth(p, [(-GSX, -x - 0.15), (x + 0.15, GSX)], -GY)
    q = gable(GSX, GRIDGE, vent=True); p.merge(q, trimesh.transformations.translation_matrix([0, top, 0]))
    return p
def garage_leaf(w=1.22, h=2.11, t=0.05):
    """Folha do portao da garagem: tabuas verticais em V, travessas e mao-francesa por dentro, 3 vidros no alto, dobradicas e puxador."""
    p = Piece(); n = 9
    for i in range(n):
        a = i * w / n + 0.003; b = (i + 1) * w / n - 0.003
        p.cham('gdoor', a, b, 0.0, h, -t / 2, t / 2, 0.006)
    for (ya, yb) in ((0.15, 0.3), (1.0, 1.15), (h - 0.3, h - 0.15)): p.box('gdoor', 0.06, w - 0.06, ya, yb, -t / 2 - 0.035, -t / 2)
    ln = LineString([(0.12, 0.3), (w - 0.12, 1.0)]).buffer(0.06, cap_style=2); ext(p, 'gdoor', ln.intersection(sbox(0.06, 0.3, w - 0.06, 1.0)), -t / 2 - 0.035, -t / 2)
    for i in range(3):
        a = 0.12 + i * (w - 0.24) / 3 + 0.02; b = 0.12 + (i + 1) * (w - 0.24) / 3 - 0.02
        p.box('dark', a - 0.012, b + 0.012, h - 0.55, h - 0.33, t / 2, t / 2 + 0.012); p.box('glass', a, b, h - 0.538, h - 0.342, t / 2 + 0.012, t / 2 + 0.016)
    for yy in (0.25, 1.05, h - 0.3):
        p.box('iron', 0.0, 0.45, yy - 0.025, yy + 0.025, t / 2, t / 2 + 0.008); p.cyl('iron', 0.012, yy - 0.06, yy + 0.06, 0.0, t / 2 + 0.01, 8)
    p.seg('iron', (w - 0.09, 1.05, t / 2), (w - 0.09, 1.05, t / 2 + 0.05), 0.018)
    p.box('iron', w - 0.14, w - 0.04, 0.95, 1.15, t / 2, t / 2 + 0.008)
    return p

# ============================================================================ interior
def interior_wall(doorway, h, ow=0.9, end=False):
    p = Piece(); t = 0.12; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2] + ([-ow / 2, ow / 2] if doorway else []) + [x1]; ys = [0.0, 2.1, h] if doorway else [0.0, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (doorway and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    if doorway:
        door_casing(p, ow, t)
        for a, b in ((-W / 2, -ow / 2 - 0.09), (ow / 2 + 0.09, x1)): baseboard(p, a, b, t)
    else: baseboard(p, -W / 2, x1, t)
    return p
def run_wall(L, h, door_at=None, ow=0.86, t=0.12, end_gap=(0.0, 0.0)):
    """Parede interna de comprimento livre (pivo: inicio, eixo; vai para +X), com porta opcional centrada em door_at."""
    p = Piece(); xs = [0.0, L]; c = door_at
    if c is not None: xs = [0.0, c - ow / 2, c + ow / 2, L]
    for m, mesh in grid_solid(xs, [0.0, 2.1, h], [-t / 2, t / 2], lambda i, j, k: None if (c is not None and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    segs = [(end_gap[0], L - end_gap[1])]
    if c is not None:
        q = Piece(); door_casing(q, ow, t); p.merge(q, trimesh.transformations.translation_matrix([c, 0, 0]))
        segs = [(end_gap[0], c - ow / 2 - 0.09), (c + ow / 2 + 0.09, L - end_gap[1])]
    for a, b in segs:
        if b - a > 0.02: baseboard(p, a, b, t)
    return p
def floor_tile(kind, lv, holes=(), trim=(0, 0, 0, 0)):
    """Piso de 2 x 2 m: tacos ('wood'), ladrilho xadrez ('tile', cozinha e banheiro), concreto ('garage') ou forro do sotao (lv 'c').
    lv 'g' = terreo (corpo ate o chao), 'u' = andar. trim = recuo em metros (x-, x+, z-, z+)."""
    p = Piece(); rect = (-1, 1, -1, 1); x0, x1, z0, z1 = rect[0] + trim[0], rect[1] - trim[1], rect[2] + trim[2], rect[3] - trim[3]
    sq = sbox(x0, z0, x1, z1)
    for (a, b, c, d) in holes: sq = sq.difference(sbox(a, b, c, d))
    if kind == 'tile':
        s = 0.25
        for i in range(8):
            for j in range(8):
                q = sbox(-1 + i * s, -1 + j * s, -1 + (i + 1) * s, -1 + (j + 1) * s).intersection(sq)
                ext_y(p, 'tile' if (i + j) % 2 == 0 else 'slate', q, -0.02, 0.0)
        if lv == 'g': ext_y(p, 'concrete', sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0)), -RAISE + 0.02, -0.02)
        else:
            sqi = sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0))
            for (a, b, c, d) in holes: sqi = sqi.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
            ext_y(p, 'plaster', sqi, -SLAB - 0.005, -0.02)
        return p
    if kind == 'garage':
        ext_y(p, 'concrete', sq, -GY + 0.002, 0.0)
        return p
    ext_y(p, 'attic' if lv == 'c' else 'floor', sq, -0.03, 0.0)
    if lv == 'g':
        ext_y(p, 'concrete', sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0)), -RAISE + 0.02, -0.03)
    else:
        sqi = sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0))
        for (a, b, c, d) in holes: sqi = sqi.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
        ext_y(p, 'plaster', sqi, -SLAB - 0.005, -0.03)
    return p
def stair():
    """Lance reto (pivo: canto do primeiro degrau do lado da parede, cota do piso; sobe para -Z e o lado aberto fica em x = -w):
    pisos com bocel, espelhos, banzos, corrimao com balaustres torneados, pilarete no pe e armario fechado embaixo."""
    p = Piece(); w = SW_
    for i in range(NR - 1):
        y = (i + 1) * RS_; z0 = -i * TR
        p.box('floor', -w, 0.0, y - 0.035, y, z0 - TR, z0 + 0.03)
        p.box('trim', -w, 0.0, y - RS_ - 0.002 if i else 0.0, y - 0.035, z0 - 0.02, z0)
    p.box('trim', -w, 0.0, H - RS_ - 0.002, H - 0.035, -RUN - 0.02, -RUN)
    for (a, b) in ((-w - 0.05, -w - 0.002), (0.002, 0.03)):
        p.hull('trim', [(x, y, z) for x in (a, b) for (z, y) in ((0.03, 0.0), (0.28, 0.0), (-RUN + 0.02, H - RS_ - 0.25), (-RUN + 0.02, H + 0.08), (0.03, RS_ + 0.08))])
    k = RS_ / TR; hr = lambda z: 0.9 + k * (-z); xr = -w - 0.025
    seg_cyl(p, 'floor', (xr, hr(0.0) + 0.05, 0.0), (xr, hr(-RUN) + 0.05, -RUN), 0.03, 10)
    for i in range(NR - 1):
        z = -i * TR - TR / 2; y = (i + 1) * RS_
        lathe(p, 'trim', [(0.014, y), (0.022, y + 0.1), (0.012, y + 0.25), (0.012, hr(z) - 0.1), (0.018, hr(z) - 0.05), (0.012, hr(z) + 0.03)], xr, z, 0.0, 6)
    p.cham('floor', xr - 0.06, xr + 0.06, 0.0, 1.0, -0.1, 0.03, 0.01); lathe(p, 'floor', [(0.05, 1.0), (0.06, 1.05), (0.035, 1.1), (0.0, 1.14)], xr, -0.035, 0.0, 12)
    ly = lambda z: (0.28 - z) / (0.28 + RUN - 0.02) * (H - RS_ - 0.25) - 0.05
    za = -1.2
    p.hull('plaster', [(x, y, z) for x in (-w + 0.03, -w + 0.07) for (z, y) in ((za, 0.0), (-RUN + 0.08, 0.0), (-RUN + 0.08, ly(-RUN + 0.08)), (za, ly(za)))])
    p.box('plaster', -w + 0.07, -0.004, 0.0, H - RS_ - 0.32, -RUN + 0.02, -RUN + 0.08)
    # porta do armario embaixo da escada
    p.box('door_int', -w + 0.02, -w + 0.03, 0.05, 1.6, -2.6, -1.9)
    p.sphere('brass', 0.02, -w + 0.0, 0.95, -2.5)
    return p
def rail(Ln, posts=(True, True)):
    p = Piece()
    p.box('trim', 0.0, Ln, 0.003, 0.08, -0.03, 0.03); p.box('floor', 0.0, Ln, 0.92, 0.98, -0.04, 0.04)
    n = int(Ln / 0.12)
    for i in range(1, n):
        x = i * Ln / n; lathe(p, 'trim', [(0.014, 0.08), (0.022, 0.2), (0.012, 0.35), (0.012, 0.82), (0.018, 0.87), (0.012, 0.92)], x, 0.0, 0.0, 6)
    for x, ok in zip((0.0, Ln), posts):
        if ok: p.cham('floor', x - 0.045, x + 0.045, 0.0015, 1.06, -0.045, 0.045, 0.008)
    return p

# ============================================================================ jardim
def lawn(x0, x1, z0, z1, holes=()):
    p = Piece(); g = sbox(x0, z0, x1, z1)
    for h in holes: g = g.difference(h)
    ext_y(p, 'grass', g, 0.002, 0.03); return p
def paving(poly, y1=0.05, joints=0.6):
    """Lajotas de concreto sobre o chao (pivo: origem do terreno): placas de 60 cm com juntas."""
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + 0.006, z + 0.006, x + joints - 0.006, z + joints - 0.006).intersection(poly)
            ext_y(p, 'paving', q, 0.0, y1)
    ext_y(p, 'dark', poly.buffer(-0.002), 0.0, y1 - 0.01)
    return p
def drive(poly):
    p = Piece(); ext_y(p, 'concrete', poly, 0.0, 0.04)
    b = poly.bounds
    for z in np.arange(b[1] + 2.0, b[3] - 0.5, 2.0): ext_y(p, 'dark', sbox(b[0] + 0.01, z - 0.004, b[2] - 0.01, z + 0.004), 0.04, 0.041)
    return p
def picket(L=2.0):
    """Cerca de estacas branca de L m (pivo: inicio, no chao; vai para +X): mourao, 2 travessas e estacas com ponta."""
    p = Piece()
    p.cham('picket', -0.05, 0.05, 0.0, 1.0, -0.05, 0.05, 0.008); p.hull('picket', [(x, 1.0, z) for x in (-0.05, 0.05) for z in (-0.05, 0.05)] + [(0, 1.08, 0)])
    for yy in (0.22, 0.72): p.box('picket', 0.05, L - 0.05, yy, yy + 0.06, 0.05, 0.075)
    for x in np.arange(0.12, L - 0.06, 0.12):
        p.box('picket', x - 0.035, x + 0.035, 0.05, 0.86, 0.075, 0.095)
        p.hull('picket', [(x + dx, 0.86, z) for dx in (-0.035, 0.035) for z in (0.075, 0.095)] + [(x, 0.92, 0.075), (x, 0.92, 0.095)])
    return p
def board_fence(L=2.0):
    """Cerca de tabuas dos fundos de L m (pivo: inicio, no chao): mourao de concreto, base e painel de tabuas sobrepostas."""
    p = Piece()
    p.box('concrete', -0.05, 0.05, 0.0, 1.8, -0.05, 0.05)
    p.box('concrete', 0.05, L - 0.05, 0.0, 0.15, -0.02, 0.02)
    for i in range(int((L - 0.1) / 0.1)):
        x = 0.05 + i * 0.1; z = 0.02 if i % 2 else 0.035
        p.box('fencew', x, x + 0.11, 0.15, 1.75, z, z + 0.015)
    for yy in (0.4, 1.45): p.box('fencew', 0.05, L - 0.05, yy, yy + 0.08, -0.02, 0.02)
    p.box('fencew', 0.05, L - 0.05, 1.75, 1.8, -0.03, 0.06)
    return p
def hedge(L=2.0, h=0.9, d=0.6):
    """Cerca-viva aparada de L m (pivo: inicio, eixo, no chao): bloco com quinas arredondadas e tufos."""
    p = Piece(); p.cham('hedge', 0.0, L, 0.0, h, -d / 2, d / 2, 0.12)
    rng = np.random.default_rng(int(L * 10))
    for _ in range(int(L * 6)):
        x = rng.uniform(0.15, L - 0.15); y = rng.uniform(0.25, h - 0.05); s = rng.choice([-1, 1])
        p.sphere('hedge', rng.uniform(0.09, 0.14), x, y, s * (d / 2 - 0.06), 1)
    return p
def bush(r=0.45):
    p = Piece(); rng = np.random.default_rng(3)
    p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def bin_():
    """Lixeira com rodas (pivo: centro, no chao)."""
    p = Piece(); p.hull('dark', [(x, 0.05, z) for x in (-0.25, 0.25) for z in (-0.3, 0.3)] + [(x, 1.0, z) for x in (-0.29, 0.29) for z in (-0.35, 0.35)])
    p.cham('slate', -0.31, 0.31, 1.0, 1.05, -0.38, 0.37, 0.01)
    for s in (-1, 1): p.cyl('iron', 0.1, 0.0, 0.0, 0.0, 0.0, 12) if False else seg_cyl(p, 'iron', (s * 0.31, 0.1, -0.32), (s * 0.25, 0.1, -0.32), 0.1, 12)
    return p
def downspout_piece(top):
    return downspout(top + 0.02 - KR * OVE, OVE + 0.03 + 0.065)

# ============================================================================ pecas
pieces = {
    'chimney': chimney(RIDGE - 0.6, RIDGE + 1.0), 'canopy': canopy(), 'front_steps': steps(0.85, 2, 1.0), 'back_steps': steps(0.65, 2, 0.8),
    'garage_steps': steps(0.6, 2, 0.6, h=RAISE - GY),
    'garage_front': garage_front(), 'garage_back': gable(GSX, GRIDGE, vent=False), 'gable_front': gable(HX, RIDGE, vent=False, win=True), 'gable_back': gable(HX, RIDGE, vent=False),
    'roof_eave': roof_strip(over=OVE), 'roof_eave_a': roof_strip(x0=-W / 2 - OVF, rake=-1, over=OVE), 'roof_eave_b': roof_strip(x1=W / 2 + OVF, rake=1, over=OVE),
    'groof_eave': roof_strip(over=OVE, sx=GSX), 'groof_eave_a': roof_strip(x0=-W / 2 - OVG, rake=-1, over=OVE, sx=GSX), 'groof_eave_b': roof_strip(x1=W / 2 + OVG, rake=1, over=OVE, sx=GSX),
    'groof_wall': roof_strip(sx=GSX), 'groof_wall_a': roof_strip(x0=-W / 2 - OVG, rake=-1, sx=GSX), 'groof_wall_b': roof_strip(x1=W / 2 + OVG, rake=1, sx=GSX),
    'ridge': ridge_cap(-HZ - OVF, HZ + OVF, RIDGE), 'gridge': ridge_cap(GZ0 - OVG, GZ1 + OVG, GRIDGE), 'abutment': abutment(GZ0 - OVG, GZ1 + OVG),
    'downspout': downspout_piece(YE), 'gdownspout': downspout(GYE + 0.02 - KR * OVE, OVE + 0.03 + 0.065),
    'iw_plain': interior_wall(False, H0 - 0.005), 'iw_doorway': interior_wall(True, H0 - 0.005), 'iw_end_plain': interior_wall(False, H0 - 0.005, end=True),
    'iw_end_doorway': interior_wall(True, H0 - 0.005, end=True),
    'stair': stair(), 'door_leaf_front': front_door_leaf(), 'door_leaf_back': back_door_leaf(), 'door_leaf_interior': door_interior(0.82, 2.06), 'garage_leaf': garage_leaf(),
    'picket': picket(), 'board_fence': board_fence(), 'hedge': hedge(), 'bush': bush(), 'bin': bin_(), 'player_scale_ref': player_ref()}
for fl, nm in ((0, 'g'), (1, 'u')):
    for k in ('plain', 'win', 'wide', 'small', 'door', 'bdoor', 'din'):
        if fl == 1 and k in ('door', 'bdoor', 'din', 'wide'): continue
        pieces[f'w_{nm}_{k}'] = wall(k, fl)
    pieces[f'corner_{nm}'] = corner(-RAISE if fl == 0 else -SLAB, H0 if fl == 0 else H, base=(fl == 0))
for k in ('plain', 'gwin', 'bdoor'):
    pieces[f'gw_{k}'] = wall(k, 0, top=GH, y0=-GY)
pieces['gcorner'] = corner(-GY, GH)

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
def ftag(fl): return f'floor{fl}'
TILE_N = {}
def tile_piece(kind, lv, holes, trim):
    key = (kind, lv, tuple(holes), trim)
    if key not in TILE_N:
        nm = f'floor_{kind}_{lv}' + ('_e' + '_'.join(str(int(round(t * 100))) for t in trim) if any(trim) else ''); base = nm; i = 2
        while nm in pieces: nm = f'{base}_h{i}'; i += 1
        pieces[nm] = floor_tile(kind, lv, holes, trim); TILE_N[key] = nm
    return TILE_N[key]
XM = [-3, -1, 1, 3]; ZM = [-4, -2, 0, 2, 4]
# ---------- casa: paredes ----------
FRONT = {0: {-3: 'wide', -1: 'win', 1: 'door', 3: 'small'}, 1: {-3: 'win', -1: 'win', 1: 'small', 3: 'win'}}
BACK = {0: {-3: 'win', -1: 'wide', 1: 'bdoor', 3: 'win'}, 1: {-3: 'win', -1: 'win', 1: 'small', 3: 'win'}}   # x do mundo
LEFT = {0: {-4: 'win', -2: 'plain', 0: 'plain', 2: 'win', 4: 'plain'}, 1: {-4: 'win', -2: 'plain', 0: 'win', 2: 'plain', 4: 'win'}}
RIGHT = {0: {-4: 'win', -2: 'din', 0: 'plain', 2: 'plain', 4: 'plain'}, 1: {-4: 'win', -2: 'small', 0: 'win', 2: 'plain', 4: 'win'}}
for fl, nm in ((0, 'g'), (1, 'u')):
    y = lvl(fl); tg = ftag(fl)
    for x in XM: put(f'w_{nm}_{FRONT[fl][x]}', x, y, HZ, 0, ['front', 'ext', tg]); put(f'w_{nm}_{BACK[fl][x]}', x, y, -HZ, 180, ['back', 'ext', tg])
    for z in ZM:
        put(f'w_{nm}_{LEFT[fl][z]}', -HX, y, z, -90, ['left', 'ext', tg])
        put(f'w_{nm}_{RIGHT[fl][z]}', HX, y, z, 90, ['right', 'ext', tg])
    for (x, z, ry) in ((HX, HZ, 0), (-HX, HZ, -90), (HX, -HZ, 90), (-HX, -HZ, 180)): put(f'corner_{nm}', x, y, z, ry, ['ext', tg])
put('gable_front', 0, YE, HZ, 0, ['front', 'roof']); put('gable_back', 0, YE, -HZ, 180, ['back', 'roof'])
put('chimney', 0, YE, -HZ + 0.15, 0, ['roof'])
put('canopy', 1, Y0, HZ, 0, ['front', 'ext']); put('front_steps', 1, Y0, HZ, 0, ['front', 'ext']); put('back_steps', 1, Y0, -HZ, 180, ['back', 'ext'])
hx, hz = hinge(0.65 - 0.06 - 0.33, HZ, 0, -0.55 + 0.2, -0.15)
hx, hz = hinge(1.0, HZ, 0, -0.58, -0.15); put('door_leaf_front', hx, Y0 + 0.013, hz, 0, ['front', 'ext', ftag(0)], door=85)
hx, hz = hinge(1.0, -HZ, 180, -0.44, -0.15); put('door_leaf_back', hx, Y0 + 0.013, hz, 180, ['back', 'ext', ftag(0)], door=-85)
hx, hz = hinge(HX, -2.0, 90, -0.44, -0.15); put('door_leaf_back', hx, Y0 + 0.013, hz, 90, ['right', ftag(0)], door=-85)
# ---------- casa: telhado ----------
for (side, ry) in ((1, 90), (-1, -90)):
    for z in ZM:
        if z == 4: nm = 'roof_eave' + ('_a' if side > 0 else '_b')
        elif z == -4: nm = 'roof_eave' + ('_b' if side > 0 else '_a')
        else: nm = 'roof_eave'
        put(nm, side * HX, YE, z, ry, ['roof'])
put('ridge', 0, YE, 0, 0, ['roof'])
for (x, z, ry) in ((-HX, HZ - 0.5, -90), (-HX, -HZ + 0.5, -90), (HX, -HZ + 0.5, 90)): put('downspout', x, 0.0, z, ry, ['ext'])
# ---------- garagem ----------
GXC = (GX0 + GX1) / 2
put('garage_front', GXC, GY, GZ1, 0, ['garage', 'front', 'ext']); put('garage_back', GXC, GYE, GZ0, 180, ['garage', 'back', 'roof'])
for x in (GX0 + 1, GX1 - 1): put('gw_plain', x, GY, GZ0, 180, ['garage', 'back', 'ext'])
for z, k in ((-2, 'plain'), (0, 'gwin'), (2, 'bdoor'), (4, 'plain')): put(f'gw_{k}', GX1, GY, z, 90, ['garage', 'right', 'ext'])
for (x, z, ry) in ((GX1, GZ1, 0), (GX1, GZ0, 90)): put('gcorner', x, GY, z, ry, ['garage', 'ext'])
for (s, x) in ((-1, GXC - 1.3), (1, GXC + 1.3)):
    if s < 0: put('garage_leaf', GXC - 1.3 + 0.02, GY + 0.04, GZ1 - 0.15, 0, ['garage', 'front', 'ext'], door=95)
    else: put('garage_leaf', GXC + 1.3 - 0.02, GY + 0.04, GZ1 - 0.15, 180, ['garage', 'front', 'ext'], door=-95)
hx, hz = hinge(GX1, 2.0, 90, -0.44, -0.15); put('door_leaf_back', hx, GY + 0.013, hz, 90, ['garage', 'right', 'ext'], door=-85)
for z in (-2, 0, 2, 4):
    zn = 'groof_eave' + ('_a' if z == 4 else '_b' if z == -2 else ''); put(zn, GX1, GYE, z, 90, ['garage', 'roof'])
    zn = 'groof_wall' + ('_b' if z == 4 else '_a' if z == -2 else ''); put(zn, GX0, GYE, z, -90, ['garage', 'roof'])
put('gridge', GXC, GYE, 0, 0, ['garage', 'roof']); put('abutment', GX0, GYE, 0, 0, ['garage', 'roof'])
put('gdownspout', GX1, 0.0, GZ1 - 0.4, 90, ['garage', 'ext'])
put('garage_steps', HX, Y0, -2.0, 90, ['garage'])
# ---------- interior ----------
def wl(fl, x0, z0, x1, z1, doors=()):
    y = lvl(fl)
    for c in range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2):
        end = (c - 1 == -HZ) or (c + 1 == HZ); d = c in doors; ry = (90 if c - 1 == -HZ else -90) if end else 90
        put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), x0, y, c, ry, [ftag(fl)])
        if d: hx, hz = hinge(x0, c, 90, -0.41, 0); put('door_leaf_interior', hx, y + 0.01, hz, 90, [ftag(fl)], door=90)
# a parede do hall (x = 0) usa modulos centrados em z impar, de -5 a 5
for fl in (0, 1):
    y = lvl(fl)
    for c in (-4, -2, 0, 2, 4):
        end = abs(c) == 4
        d = (fl == 0 and c in (2, -2)) or (fl == 1 and c in (2, -2))
        if end:
            ry = 90 if c < 0 else -90
            put('iw_end_' + ('doorway' if d else 'plain'), XW, y, c, ry, [ftag(fl)])
        else: put('iw_' + ('doorway' if d else 'plain'), XW, y, c, 90, [ftag(fl)])
        if d: hx, hz = hinge(XW, c, 90, -0.41, 0); put('door_leaf_interior', hx, y + 0.01, hz, 90, [ftag(fl)], door=90)
# paredes de comprimento livre
FX0 = -HX + T; FX1 = HX - T; IFACE = 0.06
for nm, fl, x0, z, L_, door in (('rw_bed', 1, FX0, 0.0, -IFACE - FX0, -FX0 - 2.0), ('rw_bath', 1, IFACE, -2.4, FX1 - IFACE, 1.0),
                                 ('rw_util', 0, IFACE, -2.6 - 0.06, SX0 - 0.1 - IFACE, None)):
    if nm not in pieces: pieces[nm] = run_wall(L_, H0 - 0.005, door_at=door)
    put(nm, x0, lvl(fl), z, 0, [ftag(fl)])
    if door is not None:
        hx, hz = hinge(x0 + door, z, 0, -0.41, 0); put('door_leaf_interior', hx, lvl(fl) + 0.01, hz, 0, [ftag(fl)], door=-90)
put('stair', FX1, Y0, SZ0, 0, [ftag(0)])
HOLE = (FX1 - SW_ - 0.06, SZ1, FX1, SZ0 - 1.3)
for nm, x0, z0, x1, z1, posts in (('rail_side', HOLE[0], HOLE[3], HOLE[0], HOLE[1], (True, False)), ('rail_end', HOLE[0], HOLE[3], FX1, HOLE[3], (False, False))):
    Lr = round(abs(x1 - x0) + abs(z1 - z0), 3); rn = f'rail_{int(round(Lr * 100))}'
    if rn not in pieces: pieces[rn] = rail(Lr, posts)
    if abs(z1 - z0) < 1e-6: put(rn, x0, lvl(1), z0, 0, [ftag(1)])
    else: put(rn, x0, lvl(1), z0, 90, [ftag(1)])
for fl in (0, 1, 2):
    lv = 'g' if fl == 0 else ('c' if fl == 2 else 'u')
    for x in XM:
        for z in ZM:
            tr = (T if x == -3 else 0.0, T if x == 3 else 0.0, T if z == -4 else 0.0, T if z == 4 else 0.0)
            hs = []
            if fl == 1:
                r_ = sbox(x - 1, z - 1, x + 1, z + 1).intersection(sbox(*HOLE))
                if r_.area > 1e-6: bb = r_.bounds; hs.append((round(bb[0] - x, 3), round(bb[1] - z, 3), round(bb[2] - x, 3), round(bb[3] - z, 3)))
            kind = 'wood'
            if fl == 0 and x in (-3, -1) and z == -4: kind = 'tile'
            if fl == 1 and x == 3 and z == -4: kind = 'tile'
            put(tile_piece(kind, lv, hs, tuple(round(t, 3) for t in tr)), x, lvl(fl), z, 0, [ftag(fl) if fl < 2 else 'roof'])
for x in (GX0 + 1, GX1 - 1):
    for z in ZM[1:]:
        tr = (T if x == GX0 + 1 else 0.0, T if x == GX1 - 1 else 0.0, T if z == -2 else 0.0, T if z == 4 else 0.0)
        if z == -2: tr = (tr[0], tr[1], 1.0 + T - 0.0 if False else T - 0.0 + 0.0, tr[3])
        put(tile_piece('garage', 'g', [], tuple(round(t, 3) for t in tr)), x, GY, z if z != -2 else -2.0, 0, ['garage'])
# ---------- jardim ----------
DRIVE = sbox(GX0 + 0.4, GZ1 + 0.06, GX1 - 0.4, GZ1 + 6.0)
PATH = sbox(0.4, HZ + 1.62, 1.6, HZ + 6.0)
pieces['lawn_front'] = lawn(-HX - 1.0, GX1 + 0.6, HZ, HZ + 6.0, [DRIVE.buffer(0.001), PATH.buffer(0.001), sbox(-0.05, HZ, 2.05, HZ + 1.62)])
pieces['lawn_back'] = lawn(-HX - 1.0, GX1 + 0.6, -HZ - 8.0, -HZ, [sbox(0.25, -HZ - 1.4, 1.75, -HZ)])
pieces['lawn_side'] = lawn(-HX - 1.0, -HX, -HZ, HZ)
pieces['path'] = paving(PATH); pieces['drive'] = drive(DRIVE)
for nm in ('lawn_front', 'lawn_back', 'lawn_side', 'path', 'drive'): put(nm, 0, 0, 0, 0, ['garden'])
for x0 in (-HX - 1.0, -HX + 1.0, -HX + 3.0): put('picket', x0, 0.03, HZ + 5.95, 0, ['garden'])
put('picket', GX1 - 2.0 + 0.6, 0.03, HZ + 5.95, 0, ['garden'])
for x0 in np.arange(-HX - 1.0, GX1 + 0.5, 2.0): put('board_fence', float(x0), 0.03, -HZ - 8.0, 0, ['garden'])
for z0 in np.arange(-HZ - 8.0, HZ + 5.9, 2.0):
    put('hedge', -HX - 0.7, 0.03, float(z0) + 2.0, 90, ['garden']) if z0 + 2.0 <= HZ + 6.0 else None
for (x, z) in ((-2.6, HZ + 1.1), (-1.0, HZ + 1.0), (2.8, HZ + 1.0), (-3.0, HZ + 4.5)): put('bush', x, 0.03, z, 0, ['garden'])
for x in (GX1 + 0.3, GX1 + 0.3): pass
put('bin', GX1 + 0.4, 0.03, 1.0, 90, ['garden']); put('bin', GX1 + 0.4, 0.03, 0.2, 90, ['garden'])
put('player_scale_ref', -2.0, 0.03, HZ + 3.0); put('player_scale_ref', -1.5, Y0, 2.0, 0, [ftag(0)])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE,
                       'house': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 2, 'eave_level': YE, 'ridge_level': YE + RIDGE, 'roof_pitch_deg': ANG},
                       'garage': {'x': [GX0, GX1], 'z': [GZ0, GZ1], 'floor': GY, 'eave_level': GYE, 'ridge_level': GYE + GRIDGE},
                       'stair_holes': {'1': [list(HOLE)]}, 'roof': 'clay plain tile gable roofs at 40 deg',
                       'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
              'placements': L}
    json.dump(layout, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc2 = trimesh.Scene(); tot = 0
    for e in L:
        T_ = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T_[:3, 3] = e['pos']
        sc = pieces[e['piece']].scene(e['piece'])
        for nm, g in sc.geometry.items(): g2 = g.copy(); g2.apply_transform(T_); sc2.add_geometry(g2); tot += len(g2.faces)
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:10]: print(f'  {n:30s} {p.tris():6d} tri')
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
