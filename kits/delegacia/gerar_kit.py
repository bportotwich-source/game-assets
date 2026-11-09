"""Kit 28: delegacia de policia de 18 x 12 m e 3 andares, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Terreo de pedra rusticada com grades de ferro nas janelas, andares de tijolo com cunhais de pedra, faixa entre os andares,
peitoril corrido no ultimo andar, cornija com denticulos e modilhoes, platibanda com capa de pedra. Pavilhao central de
cantaria que avanca 1 m, com porta dupla, pilastras, entablamento, frontoes nas janelas e atico com relogio e mastro.
Terraco plano com casa de maquinas da escada, condensadoras, ralos, respiros e torre de radio. Dentro: escada de 3 lances
em U (do terreo ao terraco), saguao com piso xadrez, corredor, salas, banheiros e 3 celas com grades.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'rust': (222, 212, 190), 'ashlar': (214, 204, 182), 'trim': (230, 222, 202), 'plinth': (120, 118, 112), 'brick': (140, 60, 46),
                  'floor': (150, 106, 70), 'plaster': (240, 236, 226), 'membrane': (96, 98, 100), 'concrete': (170, 166, 158), 'stone2': (196, 188, 172),
                  'marble': (234, 230, 220), 'slate': (58, 60, 62), 'frame': (236, 234, 226), 'sash': (236, 234, 226), 'door': (34, 54, 44),
                  'iron': (28, 30, 32), 'steel': (120, 124, 128), 'door_int': (222, 216, 200), 'coping': (206, 198, 178), 'seam': (84, 86, 88),
                  'clock': (246, 244, 236), 'wood': (96, 60, 38), 'grate': (60, 62, 64)},
           texturas={'rust': 'render', 'ashlar': 'render', 'trim': 'plaster', 'plinth': 'stone', 'brick': 'brick', 'floor': 'planks', 'plaster': 'plaster',
                     'membrane': 'render', 'concrete': 'render', 'stone2': 'stone2', 'marble': 'plaster', 'wood': 'planks'},
           out=OUT)
MATS = D.MATS; TEX = D.TEX

W = 2.0; T = 0.3; H = 3.2; SLAB = 0.25; RAISE = 0.6; SX = 9.0; SZ = 6.0
H0 = H - SLAB            # altura das paredes de cada andar (o de cima comeca na face de baixo da laje)
PL = 0.45                # topo do embasamento de granito
def lvl(fl): return RAISE + fl * H
YR = lvl(3)              # cota do terraco
PXH = 3.0; PZ = 1.0; ZP = SZ + PZ    # pavilhao central: x de -3 a 3, frente em z = 7
PAR = 1.05; PAVH = 2.3   # platibanda e atico do pavilhao (acima do terraco)

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
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1 - p0; L = np.linalg.norm(v)
    c = trimesh.creation.cylinder(radius=r, height=L, sections=sec); z = np.array([0, 0, 1.0]); v = v / L
    ax = np.cross(z, v); ang = math.acos(np.clip(np.dot(z, v), -1, 1))
    if np.linalg.norm(ax) > 1e-6: c.apply_transform(trimesh.transformations.rotation_matrix(ang, ax))
    elif v[2] < 0: c.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    c.apply_translation((p0 + p1) / 2); return p.add(mat, c)
def lathe(p, mat, prof, x=0.0, z=0.0, y0=0.0, sec=14):
    for (r0, ya), (r1, yb) in zip(prof[:-1], prof[1:]):
        if abs(yb - ya) < 1e-6: continue
        pts = [(x + r * math.cos(a), y0 + y, z + r * math.sin(a)) for (r, y) in ((r0, ya), (r1, yb)) for a in np.linspace(0, 2 * math.pi, sec, endpoint=False)]
        p.hull(mat, pts)
def mitre_cut(m, keep_x_le_z=True):
    n = [-1, 0, 1] if keep_x_le_z else [1, 0, -1]; n = np.array(n) / math.sqrt(2)
    return slice_keep(m, [0, 0, 0], n)
def mitred(p, mat, prof, L=0.5):
    """Perfil (z, y) que dobra a quina externa (pivo na quina, paredes em -X e -Z): duas metades cortadas em meia-esquadria."""
    for keep in (True, False):
        q = Piece()
        if keep: prof_x(q, mat, 0.0, L, prof)
        else: prof_z(q, mat, 0.0, L, prof)
        p.add(mat, mitre_cut(q.parts[mat][0], keep))

# ---------- paredes ----------
def wall_core(p, holes, y0, h, outer_mat, inner='plaster', zo=-0.03, x0=-W / 2, x1=W / 2):
    """Nucleo estanque com buracos [(x0, x1, y0, y1)]: camada interna (2 cm, de y=0 ate 5 mm abaixo do topo) e corpo ate z=zo."""
    xs = sorted(set([x0, x1] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, 0.0, h - 0.005, h] + [max(y0, v) for hh in holes for v in hh[2:]]))
    ys = [v for v in ys if y0 - 1e-9 <= v <= h + 1e-9]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0:
            if ys[j] >= h - 0.0051: return None
            return inner             # gesso tambem na altura da laje (aparece no vao da escada)
        return outer_mat
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, zo], cell).items(): p.add(m, mesh)
def bands(holes, y0, y1, x0=-W / 2, x1=W / 2):
    cuts = sorted(set([y0, y1] + [y for h in holes for y in (h[2], h[3]) if y0 < y < y1])); out = []
    for ya, yb in zip(cuts[:-1], cuts[1:]):
        xs = [(x0, x1)]
        for (hx0, hx1, hy0, hy1) in holes:
            if ya >= hy0 - 1e-9 and yb <= hy1 + 1e-9: xs = [s for a, b in xs for s in ((a, min(b, hx0)), (max(a, hx1), b)) if s[1] - s[0] > 1e-4]
        out += [(a, b, ya, yb) for a, b in xs]
    return out
COURSE = (H0 - PL) / 6
def rustication(p, holes, mat='rust', x0=-W / 2, x1=W / 2, d=0.03, c=0.015, y0=PL, y1=H0, n=6):
    """Fiadas rusticadas (faixas com chanfro em cima e embaixo, d de espessura) de y0 a y1."""
    k_h = (y1 - y0) / n
    for k in range(n):
        b0 = y0 + k * k_h; b1 = b0 + k_h
        for (a, b, ya, yb) in bands(holes, b0, b1, x0, x1):
            prof_x(p, mat, a, b, crect(-d, 0.0, ya, yb, c, (0, 1 if abs(ya - b0) < 1e-6 else 0, 1 if abs(yb - b1) < 1e-6 else 0, 0)))
def base_course(p, gaps=(), x0=-W / 2, x1=W / 2):
    """Embasamento de granito (de -RAISE a PL), 1 cm saliente, com chanfro em cima; para nos vaos de porta."""
    xs = [x0] + [v for g in gaps for v in g] + [x1]
    for i in range(0, len(xs) - 1, 2):
        if xs[i + 1] - xs[i] > 0.01: prof_x(p, 'plinth', xs[i], xs[i + 1], crect(-0.03, 0.01, -RAISE, PL, 0.012, (0, 0, 1, 0)))
BELT = [(0.0, -0.25), (0.05, -0.25), (0.05, -0.2), (0.065, -0.185), (0.065, -0.05), (0.08, -0.04), (0.09, -0.01), (0.09, 0.03), (0.07, 0.05), (0.0, 0.08)]
def sill_course(y):    # peitoril corrido do ultimo andar (topo em y)
    return [(0.0, y - 0.11), (0.05, y - 0.11), (0.06, y - 0.1), (0.075, y - 0.08), (0.075, y - 0.03), (0.065, y - 0.01), (0.0, y + 0.004)]

# ---------- janelas de guilhotina, verga em arco abatido de aduelas, peitoril, grade ----------
def sash_window(p, ow, oy0, oy1, zf=-0.04, lites=2):
    """Caixilho branco recuado (frente em zf), 2 folhas de guilhotina (a de cima com baguete), batente e peitoril interno."""
    x = ow / 2; f = 0.06; y0 = oy0 + 0.032
    p.box('frame', -x, -x + f, y0, oy1, zf - 0.16, zf); p.box('frame', x - f, x, y0, oy1, zf - 0.16, zf)
    p.box('frame', -x + f, x - f, oy1 - f, oy1, zf - 0.16, zf); p.box('frame', -x + f, x - f, y0, y0 + 0.04, zf - 0.16, zf)
    p.box('frame', -x + f, -x + f + 0.012, y0 + 0.04, oy1 - f, zf - 0.065, zf - 0.055); p.box('frame', x - f - 0.012, x - f, y0 + 0.04, oy1 - f, zf - 0.065, zf - 0.055)
    mid = (y0 + 0.04 + oy1 - f) / 2
    sash(p, -x + f, x - f, y0 + 0.04, mid + 0.02, zf - 0.11, zf - 0.07, 1, 0.075)
    sash(p, -x + f + 0.012, x - f - 0.012, mid - 0.02, oy1 - f, zf - 0.05, zf - 0.01, lites, 0.05)
    p.box('trim', -x - 0.05, x + 0.05, oy0, oy0 + 0.022, -T - 0.04, zf - 0.16)               # peitoril interno
def stone_sill(p, ow, oy0, ext_=0.1):
    x = ow / 2 + ext_
    prof_x(p, 'trim', -x, x, [(-0.2, oy0 - 0.07), (0.06, oy0 - 0.07), (0.075, oy0 - 0.055), (0.075, oy0 - 0.015), (0.065, oy0 - 0.0), (-0.2, oy0 + 0.03)])
def jack_arch(p, ow, oy1, h=0.32, n=7, d=0.03, mat='trim'):
    """Verga em arco abatido: aduelas radiais com junta de 6 mm e fecho (keystone) mais alto e saliente."""
    x = ow / 2 + 0.03; cy = oy1 - 1.4; xb = np.linspace(-x, x, n + 1); yt = oy1 + h
    for i in range(n):
        a, b = xb[i] + 0.003, xb[i + 1] - 0.003; key = i == n // 2
        ta = a * (yt + (0.08 if key else 0) - cy) / (oy1 - cy); tb = b * (yt + (0.08 if key else 0) - cy) / (oy1 - cy)
        top = yt + (0.08 if key else 0.0); dd = d + (0.025 if key else 0.0)
        p.hull(mat, [(xx, yy, z) for (xx, yy) in ((a, oy1), (b, oy1), (tb, top), (ta, top)) for z in (0.0, dd)])
def grille(p, ow, oy0, oy1, z=-0.02):
    """Grade de ferro no vao: barras redondas a cada 12 cm atravessando 2 chatas; as pontas entram na pedra."""
    x = ow / 2; n = int(ow / 0.12)
    for i in range(n):
        xx = -x + (i + 0.5) * ow / n; seg_cyl(p, 'iron', (xx, oy0 + 0.0, z), (xx, oy1 + 0.03, z), 0.011, 8)
    for yy in (oy0 + 0.32, oy1 - 0.28): p.box('iron', -x - 0.01, x + 0.01, yy - 0.025, yy + 0.025, z - 0.009, z + 0.009)
def surround(p, ow, oy0, oy1, w=0.12, d=0.035, keystone=False, hood=None, mat='trim'):
    """Moldura de pedra em volta do vao, com filete; fecho (keystone), cornija reta (hood='flat') ou frontao (hood='pediment')."""
    x = ow / 2
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x + w)))
        prof_y(p, mat, oy0 - 0.06, oy1 + w, crect(a, b, 0.0, d, 0.008, (0, 0, 1, 1)))
        a2, b2 = sorted((s * (x + w - 0.03), s * (x + w)))
        prof_y(p, mat, oy0 - 0.02, oy1 + w - 0.03, crect(a2, b2, d, d + 0.012, 0.004, (0, 0, 1, 1)))
    prof_x(p, mat, -x, x, crect(0.0, d, oy1, oy1 + w, 0.008, (0, 1, 1, 0)))
    prof_x(p, mat, -x - w + 0.03, x + w - 0.03, crect(d, d + 0.012, oy1 + w - 0.03, oy1 + w - 0.001, 0.004, (0, 1, 1, 0)))
    if keystone: p.hull(mat, [(sx * ww, y, z) for (ww, y) in ((0.07, oy1 - 0.05), (0.11, oy1 + w + 0.06)) for sx in (-1, 1) for z in (0.0, d + 0.03)])
    yh = oy1 + w
    if hood == 'flat':
        p.hull(mat, [(sx * (x + w + 0.02), y, z) for sx in (-1, 1) for (z, y) in ((0.0, yh), (0.0, yh + 0.06), (0.05, yh), (0.05, yh + 0.06))])
        prof_x(p, mat, -x - w - 0.08, x + w + 0.08, [(0.0, yh + 0.06), (0.09, yh + 0.06), (0.11, yh + 0.09), (0.12, yh + 0.14), (0.12, yh + 0.17), (0.0, yh + 0.21)])
        for s in (-1, 1): p.hull(mat, [(s * (x + w - dx), y, z) for dx in (0.0, 0.07) for (z, y) in ((0.0, yh - 0.28), (0.0, yh + 0.06), (0.09, yh + 0.06), (0.04, yh - 0.2))])
    if hood == 'pediment':
        prof_x(p, mat, -x - w - 0.08, x + w + 0.08, [(0.0, yh), (0.1, yh), (0.12, yh + 0.03), (0.12, yh + 0.08), (0.0, yh + 0.08)])
        X = x + w + 0.1; Hp = 0.36
        for s in (-1, 1):
            pts = []
            for (xx, yy) in ((s * X, yh + 0.08), (0.0, yh + 0.08 + Hp)):
                for (dz, dy) in ((0.0, 0.0), (0.0, 0.1), (0.12, 0.1), (0.13, 0.06), (0.1, 0.0)): pts.append((xx, yy + dy, dz))
            p.hull(mat, pts)
        ext(p, mat, Polygon([(-X + 0.15, yh + 0.08), (X - 0.15, yh + 0.08), (0.0, yh + 0.08 + Hp - 0.06)]), 0.0, 0.03)
        for s in (-1, 1): p.hull(mat, [(s * (x + w - dx), y, z) for dx in (0.0, 0.08) for (z, y) in ((0.0, yh - 0.3), (0.0, yh), (0.11, yh), (0.05, yh - 0.22))])

# ---------- modulos de parede externos ----------
GW_ = (1.0, 0.95, 2.45); UW_ = (1.0, 0.85, 2.45); CW_ = (0.7, 1.95, 2.45)
def g_wall(kind='window', mat='rust', grid=True):
    """Modulo de 2 m do terreo: embasamento de granito, 6 fiadas rusticadas, gesso por dentro. Pivo: face externa, cota do piso."""
    p = Piece(); holes = []
    if kind in ('window', 'cell'): ow, a, b = GW_ if kind == 'window' else CW_; holes = [(-ow / 2, ow / 2, a, b)]
    if kind == 'back_door': holes = [(-0.55, 0.55, 0.0, 2.3)]
    if kind == 'door': holes = [(-0.85, 0.85, 0.0, 2.6)]
    wall_core(p, holes, -RAISE, H0, mat)
    rustication(p, holes, mat, d=0.03 if mat == 'rust' else 0.04, c=0.015 if mat == 'rust' else 0.02)
    base_course(p, [(h[0] - 0.14, h[1] + 0.14) for h in holes if h[2] <= 0.0])
    if kind in ('window', 'cell'):
        sash_window(p, ow, a, b, lites=1 if kind == 'cell' else 2); stone_sill(p, ow, a)
        if grid: grille(p, ow, a, b)
        if mat == 'rust': jack_arch(p, ow, b, h=0.3 if kind == 'window' else 0.24, n=7 if kind == 'window' else 5)
        else: surround(p, ow, a, b, keystone=True)
    if kind == 'back_door':
        x = 0.55
        prof_x(p, 'stone2', -x, x, [(-0.295, 0.012), (0.04, 0.012), (0.06, 0.0), (0.06, -0.045), (-0.295, -0.045)])
        p.box('steel', -x, -x + 0.07, 0.0, 2.3, -0.2, -0.1); p.box('steel', x - 0.07, x, 0.0, 2.3, -0.2, -0.1); p.box('steel', -x + 0.07, x - 0.07, 2.23, 2.3, -0.2, -0.1)
        jack_arch(p, 1.1, 2.3, h=0.3, n=7)
    if kind == 'door':     # porta principal: soleira, caixilho com bandeira, pilastras e entablamento com placa lisa
        x = 0.85
        prof_x(p, 'stone2', -x, x, [(-0.295, 0.012), (0.08, 0.012), (0.1, 0.0), (0.1, -0.045), (-0.295, -0.045)])
        p.box('frame', -x, -x + 0.08, 0.0, 2.6, -0.2, -0.1); p.box('frame', x - 0.08, x, 0.0, 2.6, -0.2, -0.1)
        p.cham('frame', -x + 0.08, x - 0.08, 2.24, 2.32, -0.21, -0.09, 0.008); p.box('frame', -x + 0.08, x - 0.08, 2.52, 2.6, -0.2, -0.1)
        ext(p, 'glass', sbox(-x + 0.08, 2.32, x - 0.08, 2.52), -0.153, -0.147)
        for xx in np.linspace(-x + 0.08, x - 0.08, 6)[1:-1]: p.cham('frame', xx - 0.018, xx + 0.018, 2.32, 2.52, -0.165, -0.135, 0.005)
        for s in (-1, 1):     # pilastras com base e capitel
            a, b = sorted((s * (x + 0.02), s * (x + 0.3)))
            p.cham('ashlar', a, b, 0.0, 2.65, -0.01, 0.07, 0.01)
            p.cham('trim', a - 0.03, b + 0.03, 0.0, 0.22, -0.006, 0.1, 0.012)
            p.cham('trim', a - 0.03, b + 0.03, 2.52, 2.65, -0.006, 0.1, 0.012)
        E0 = x + 0.36
        prof_x(p, 'trim', -E0, E0, crect(-0.01, 0.1, 2.65, 2.77, 0.01, (0, 1, 1, 0)))          # arquitrave
        prof_x(p, 'trim', -E0 + 0.04, E0 - 0.04, crect(-0.01, 0.07, 2.77, 2.93, 0.008, (0, 1, 1, 0)))  # friso
        prof_x(p, 'trim', -E0 - 0.06, E0 + 0.06, [(-0.01, 2.93), (0.16, 2.93), (0.19, 2.96), (0.21, 3.0), (0.21, 3.04), (-0.01, 3.08)])  # cornija
        p.cham('trim', -0.7, 0.7, 2.8, 2.9, 0.07, 0.1, 0.008)                                  # placa lisa (sem letreiro)
    return p
def u_wall(kind='window', fl=1, mat='brick', zo=0.0, hood=None, grid_lines=0):
    """Modulo de 2 m de andar (de -SLAB a H0): tijolo (ou cantaria), faixa no 1o andar, peitoril corrido no 2o, gesso por dentro."""
    p = Piece(); holes = []
    if kind == 'window': ow, a, b = UW_; holes = [(-ow / 2, ow / 2, a, b)]
    wall_core(p, holes, -SLAB, H0, mat, zo=zo)
    if grid_lines: rustication(p, holes, mat, d=-zo, c=0.006, y0=-SLAB, y1=H0, n=grid_lines)
    if fl == 1: prof_x(p, 'trim', -W / 2, W / 2, BELT)
    if fl == 2: prof_x(p, 'trim', -W / 2, W / 2, sill_course(UW_[1]))
    if kind == 'window':
        ow, a, b = UW_; sash_window(p, ow, a, b)
        if fl == 1: stone_sill(p, ow, a)
        else: prof_x(p, 'trim', -ow / 2, ow / 2, [(-0.2, a - 0.07), (0.0, a - 0.07), (0.0, a + 0.004), (-0.2, a + 0.03)])
        if hood: surround(p, ow, a, b, keystone=hood == 'key', hood=hood if hood != 'key' else None, mat='trim')
        else: jack_arch(p, ow, b)
    return p

# ---------- cornija, platibanda e atico ----------
CORONA = [(0.0, 0.08), (0.14, 0.08), (0.14, 0.12), (0.38, 0.12), (0.4, 0.14), (0.4, 0.24), (0.42, 0.26), (0.42, 0.3), (0.0, 0.3)]
ARCH_ = [(0.0, -0.25), (0.05, -0.25), (0.05, -0.17), (0.065, -0.155), (0.065, -0.12), (0.0, -0.12)]
FRIEZE = [(0.0, -0.12), (0.025, -0.12), (0.025, 0.0), (0.0, 0.0)]
BED = [(0.0, 0.0), (0.02, 0.0), (0.02, 0.08), (0.0, 0.08)]
def cornice(p, x0=-W / 2, x1=W / 2, mat='trim'):
    """Cornija na base da platibanda (pivo: cota do terraco): arquitrave, friso, denticulos, modilhoes e coroa."""
    for pr in (ARCH_, FRIEZE, BED, CORONA): prof_x(p, mat, x0, x1, pr)
    for xx in np.arange(x0 + 0.05, x1 - 0.02, 0.1): p.box(mat, xx - 0.025, xx + 0.025, 0.005, 0.08, 0.02, 0.08)
    for xx in np.arange(x0 + 0.25, x1 - 0.1, 0.5):
        p.hull(mat, [(xx + dx, yy, z) for dx in (-0.04, 0.04) for (z, yy) in ((0.1, 0.12), (0.1, 0.06), (0.16, 0.02), (0.22, 0.02), (0.34, 0.09), (0.34, 0.12))])
COPE = lambda y: [(-T - 0.05, y - 0.08), (0.05, y - 0.08), (0.05, y - 0.03), (0.0, y), (-T, y), (-T - 0.05, y - 0.03)]
def parapet(mat='brick', top=PAR, inner='brick', zo=0.0, panel=False, clock=False, grid_lines=0):
    """Platibanda de 2 m (pivo: face externa, cota do terraco), de -SLAB ate 'top': cornija, tijolo dos dois lados e capa de pedra."""
    p = Piece()
    wall_core(p, [], -SLAB, top - 0.08, mat, inner=inner, zo=zo)
    if grid_lines: rustication(p, [], mat, d=-zo, c=0.006, y0=-SLAB, y1=top - 0.08, n=grid_lines)
    cornice(p)
    prof_x(p, 'coping', -W / 2, W / 2, COPE(top))
    if panel:     # atico: painel rebaixado com moldura
        prof_y(p, 'trim', 0.55, top - 0.35, crect(-0.75, -0.65, 0.0, 0.03, 0.006, (0, 0, 1, 1))); prof_y(p, 'trim', 0.55, top - 0.35, crect(0.65, 0.75, 0.0, 0.03, 0.006, (0, 0, 1, 1)))
        prof_x(p, 'trim', -0.75, 0.75, crect(0.0, 0.03, 0.45, 0.55, 0.006, (0, 1, 1, 0))); prof_x(p, 'trim', -0.75, 0.75, crect(0.0, 0.03, top - 0.35, top - 0.25, 0.006, (0, 1, 1, 0)))
    if clock:     # relogio no eixo do atico
        yc = 1.25; R = 0.5
        ext(p, 'trim', Point(0, yc).buffer(R + 0.12, 32).difference(Point(0, yc).buffer(R, 32)), 0.0, 0.07)
        ext(p, 'clock', Point(0, yc).buffer(R + 0.002, 32), 0.003, 0.04)
        for k in range(12):
            a = k * math.pi / 6; r0, r1 = (R - 0.1, R - 0.03) if k % 3 else (R - 0.14, R - 0.03)
            q = Piece(); q.box('iron', r0, r1, -0.012 if k % 3 else -0.02, 0.012 if k % 3 else 0.02, 0.04, 0.046)
            M = trimesh.transformations.rotation_matrix(a, [0, 0, 1]); M[:3, 3] = [0, yc, 0]; p.merge(q, M)
        for (a, L, w) in ((math.radians(60), 0.26, 0.025), (math.radians(-30), 0.38, 0.016)):
            q = Piece(); q.hull('iron', [(-0.04, -w, 0.05), (-0.04, w, 0.05), (L, 0.0, 0.05), (-0.04, -w, 0.058), (-0.04, w, 0.058), (L, 0.0, 0.058)])
            M = trimesh.transformations.rotation_matrix(a, [0, 0, 1]); M[:3, 3] = [0, yc, 0]; p.merge(q, M)
        p.cyl('iron', 0.03, 0.04, 0.07, 0.0, 0.0, 12) if False else p.sphere('iron', 0.03, 0.0, yc, 0.06)
        p.hull('trim', [(sx * 0.2, y, z) for sx in (-1, 1) for (z, y) in ((0.0, yc - R - 0.1), (0.0, yc - R - 0.3), (0.08, yc - R - 0.12))])
    return p

# ---------- quina interna com o pavilhao (perfis em meia-esquadria) ----------
def imitre(p, origin, normal, mats=('trim',)):
    for mt in mats:
        if mt not in p.parts: continue
        n = np.array(normal, float) / np.linalg.norm(normal); out = []
        for m in p.parts[mt]:
            d = (m.vertices - np.array(origin, float)) @ n
            if d.min() >= -1e-9: out.append(m)
            elif d.max() > 1e-9: out.append(slice_keep(m, origin, n))
        p.parts[mt] = out
    return p
def wall_side(p, sgn):    # modulo da frente ao lado do pavilhao: quina interna em x = -sgn (local)
    return imitre(p, [-sgn * W / 2, 0, 0], [sgn, 0, -1])
def ps_side(p, sgn):      # parede lateral do pavilhao: quina interna na ponta de tras (x = sgn * 0,5)
    return imitre(p, [sgn * 0.5, 0, 0], [-sgn, 0, -1])

# ---------- quinas ----------
QH = 0.32
def corner_g(mat='rust'):
    """Quina do terreo: nucleo, embasamento e fiadas rusticadas que dobram a quina. Pivo: quina externa, cota do piso; paredes em -X e -Z."""
    p = Piece(); e = 0.004; d = 0.03 if mat == 'rust' else 0.04; c = 0.015 if mat == 'rust' else 0.02
    p.box(mat, -T + 0.004, e, -RAISE, H0 - 0.004, -T + 0.004, e)
    p.cham('plinth', -T + 0.006, 0.025, -RAISE, PL, -T + 0.006, 0.025, 0.012)
    for k in range(6):
        b0 = PL + k * COURSE; b1 = b0 + COURSE
        mitred(p, mat, [(-d, b0), (0.035 - c, b0), (0.035, b0 + c), (0.035, b1 - c), (0.035 - c, b1), (-d, b1)], 0.4)
    return p
def corner_u(fl, pav=False):
    """Quina de andar (pivo na cota do piso): nucleo de tijolo, cunhais de pedra alternados (ou pilastra no pavilhao),
    faixa (1o andar) ou peitoril corrido (2o) dobrando a quina."""
    p = Piece(); e = 0.004
    p.box('ashlar' if pav else 'brick', -T + 0.004, e, -SLAB - 0.003, H0 - 0.004, -T + 0.004, e)
    if pav:     # pilastra que dobra a quina, com capitel no ultimo andar
        PW = 0.26
        p.cham('ashlar', -PW, 0.06, -SLAB + 0.006, H0 - 0.006, -0.05, 0.06, 0.008); p.cham('ashlar', -0.05, 0.06, -SLAB + 0.006, H0 - 0.006, -PW, -0.05, 0.008)
        if fl == 2:
            a, b = H0 - 0.3, H0 - 0.002
            p.cham('trim', -PW - 0.03, 0.1, a, b, -0.06, 0.1, 0.01); p.cham('trim', -0.06, 0.1, a, b, -PW - 0.03, -0.06, 0.01)
    else:
        for k in range(10):
            ya, yb = -SLAB + k * QH + 0.007, -SLAB + (k + 1) * QH - 0.009; L1, L2 = (0.33, 0.22) if k % 2 == 0 else (0.22, 0.33)
            p.cham('trim', -L1, 0.03, ya, yb, -0.05, 0.03, 0.008)
            p.cham('trim', -0.05, 0.03, ya, yb, -L2, -0.05, 0.008)
    mitred(p, 'trim', BELT if fl == 1 else sill_course(UW_[1]))
    return p
def corner_p(top=PAR, mat='brick', zo=0.0):
    """Quina da platibanda: nucleo, cornija em meia-esquadria, canto da capa e um denticulo no canto."""
    p = Piece(); e = 0.004
    p.box(mat, -T + 0.002, e, -SLAB - 0.003, top - 0.077, -T + 0.002, e)
    for pr in (ARCH_, FRIEZE, BED, CORONA): mitred(p, 'trim', pr)
    p.box('trim', 0.0, 0.08, 0.005, 0.08, 0.0, 0.08)
    p.hull('trim', [(x, yy, z) for (x, z) in ((0.1, 0.1), (0.34, 0.34)) for yy in (0.02, 0.12)] + [(0.04, 0.12, 0.16), (0.16, 0.12, 0.04), (0.04, 0.06, 0.1), (0.1, 0.06, 0.04)])
    prof_x(p, 'coping', 0.0, 0.05, COPE(top))
    return p

# ============================================================================ escada em U de 3 lances, guarda-corpos
NR = 18; RS_ = H / NR; TR = 0.28; SW_ = 1.1; RUN = (NR - 1) * TR
LA = (-8.7, -7.6); LB = (-7.3, -6.2); ZA = 0.9; ZB = ZA - RUN        # faixas A e B e as pontas
def stair(both=False):
    """Lance reto de madeira (pivo: canto do primeiro degrau, cota do piso), sobe para -Z: pisos com bocel, espelhos brancos,
    banzos, corrimao com balaustres no lado aberto (nos dois lados se both) e pilarete torneado no pe."""
    p = Piece(); w = SW_
    for i in range(NR - 1):
        y = (i + 1) * RS_; z0 = -i * TR
        p.box('floor', 0.0, w, y - 0.035, y, z0 - TR, z0 + 0.03)
        p.box('trim', 0.0, w, y - RS_ - 0.002 if i else 0.0, y - 0.035, z0 - 0.02, z0)
    p.box('trim', 0.0, w, H - RS_ - 0.002, H - 0.035, -RUN - 0.02, -RUN)
    for (a, b) in ((w + 0.002, w + 0.05), (-0.03, -0.002)):
        p.hull('trim', [(x, y, z) for x in (a, b) for (z, y) in ((0.03, 0.0), (0.28, 0.0), (-RUN + 0.02, H - RS_ - 0.25), (-RUN + 0.02, H + 0.08), (0.03, RS_ + 0.08))])
    k = RS_ / TR; hr = lambda z: 0.9 + k * (-z)
    for xr in ((w + 0.025, -0.025) if both else (w + 0.025,)):
        seg_cyl(p, 'wood', (xr, hr(0.0) + 0.05, 0.0), (xr, hr(-RUN) + 0.05, -RUN), 0.03, 10)
        for i in range(NR - 1):
            z = -i * TR - TR / 2; y = (i + 1) * RS_
            p.box('trim', xr - 0.012, xr + 0.012, y, hr(z) + 0.03, z - 0.012, z + 0.012)
        p.cham('wood', xr - 0.07, xr + 0.07, 0.0, 1.0, -0.1, 0.04, 0.01); lathe(p, 'wood', [(0.06, 1.0), (0.07, 1.06), (0.04, 1.12), (0.0, 1.16)], xr, -0.03, 0.0, 12)
    return p
def rail(L, posts=(True, True)):
    """Guarda-corpo reto ao longo de +X (0..L), pivo no chao: rodape, balaustres, corrimao e pilaretes nas pontas."""
    p = Piece()
    p.box('trim', 0.0, L, 0.003, 0.08, -0.03, 0.03); p.box('wood', 0.0, L, 0.92, 0.98, -0.04, 0.04)
    n = int(L / 0.12)
    for i in range(1, n):
        x = i * L / n; p.box('trim', x - 0.012, x + 0.012, 0.08, 0.92, -0.012, 0.012)
    for x, ok in zip((0.0, L), posts):
        if ok: p.cham('wood', x - 0.04, x + 0.04, 0.0015, 1.06, -0.04, 0.04, 0.008)
    return p

# ============================================================================ interior
def interior_wall(doorway, h, ow=0.9, end=False):
    p = Piece(); t = 0.14; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2] + ([-ow / 2, ow / 2] if doorway else []) + [x1]; ys = [0.0, 2.1, h] if doorway else [0.0, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (doorway and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    if doorway:
        door_casing(p, ow, t)
        for a, b in ((-W / 2, -ow / 2 - 0.09), (ow / 2 + 0.09, x1)): baseboard(p, a, b, t)
    else: baseboard(p, -W / 2, x1, t)
    return p
def cell_front(end=False, h=H0 - 0.009):
    """Grade de cela de 2 m (pivo: centro, cota do piso): quadro de aco, barras redondas a cada 13 cm, travessas e vao de porta."""
    p = Piece(); x0, x1 = -W / 2, W / 2 - (T if end else 0.0); dw = 0.82
    p.box('steel', x0, x1, 0.0, 0.06, -0.04, 0.04); p.box('steel', x0, x1, h - 0.08, h, -0.04, 0.04)
    p.box('steel', -dw / 2 - 0.05, -dw / 2, 0.06, h - 0.08, -0.04, 0.04); p.box('steel', dw / 2, dw / 2 + 0.05, 0.06, h - 0.08, -0.04, 0.04)
    p.box('steel', -dw / 2, dw / 2, 2.12, 2.2, -0.04, 0.04)
    for (a, b) in ((x0, -dw / 2 - 0.05), (dw / 2 + 0.05, x1)):
        n = max(1, int((b - a) / 0.13))
        for i in range(n): xx = a + (i + 0.5) * (b - a) / n; seg_cyl(p, 'steel', (xx, 0.06, 0.0), (xx, h - 0.08, 0.0), 0.014, 8)
        for yy in (1.05, 2.16): p.box('steel', a, b, yy - 0.03, yy + 0.03, -0.012, 0.012)
    for i in range(6): xx = -dw / 2 + (i + 0.5) * dw / 6; seg_cyl(p, 'steel', (xx, 2.2, 0.0), (xx, h - 0.08, 0.0), 0.014, 8)
    return p
def door_cell(w=0.8, h=2.1):
    """Porta de grade da cela (pivo: dobradica, embaixo): quadro, barras, travessa com fechadura."""
    p = Piece(); s = 0.04
    p.box('steel', 0.0, s, 0.0, h, -0.02, 0.02); p.box('steel', w - s, w, 0.0, h, -0.02, 0.02)
    for (a, b) in ((0.0, 0.05), (1.0, 1.06), (h - 0.05, h)): p.box('steel', s, w - s, a, b, -0.02, 0.02)
    for i in range(5): xx = s + (i + 0.5) * (w - 2 * s) / 5; seg_cyl(p, 'steel', (xx, 0.05, 0.0), (xx, h - 0.05, 0.0), 0.013, 8)
    p.box('iron', w - 0.2, w - s, 0.9, 1.16, -0.035, 0.035)
    for yy in (0.25, 1.75): p.cyl('steel', 0.016, yy, yy + 0.12, 0.0, 0.0, 8)
    return p
def floor_tile(kind, lv, rect=(-1, 1, -1, 1), holes=(), trim=(0, 0, 0, 0)):
    """Piso: tacos, xadrez de marmore, pastilhas, concreto ou manta (terraco). lv 'g' = terreo (embasamento ate o chao),
    'u' = andar e 'r' = terraco (laje com forro de gesso por baixo). trim: para na face interna das paredes externas."""
    p = Piece(); x0, x1, z0, z1 = rect[0] + T * trim[0], rect[1] - T * trim[1], rect[2] + T * trim[2], rect[3] - T * trim[3]
    sq = sbox(x0, z0, x1, z1)
    for (a, b, c, d) in holes: sq = sq.difference(sbox(a, b, c, d))
    if kind == 'bath':
        ext_y(p, 'dark', sq, -0.027, -0.004); n = 10; s = W / n
        for i in range(n):
            for j in range(int(round((rect[3] - rect[2]) / s))):
                a0 = rect[0] + i * s + 0.004; c0 = rect[2] + j * s + 0.004; a1, c1 = a0 + s - 0.008, c0 + s - 0.008
                a0, a1, c0, c1 = max(a0, x0 + 0.004), min(a1, x1 - 0.004), max(c0, z0 + 0.004), min(c1, z1 - 0.004)
                if a1 - a0 > 0.01 and c1 - c0 > 0.01:
                    q = sbox(a0, c0, a1, c1)
                    for (a, b, c, d) in holes: q = q.difference(sbox(a, b, c, d))
                    ext_y(p, 'tile', q, -0.03, 0.0)
    elif kind == 'marble':
        s = 0.5
        for i in range(4):
            for j in range(int(round((rect[3] - rect[2]) / s))):
                q = sbox(rect[0] + i * s, rect[2] + j * s, rect[0] + (i + 1) * s, rect[2] + (j + 1) * s).intersection(sq)
                ext_y(p, 'marble' if (i + j) % 2 == 0 else 'slate', q, -0.03, 0.0)
    elif kind == 'membrane':
        ext_y(p, 'membrane', sq, -0.03, 0.0)
        for (a, b, c, d) in ((-0.02, rect[2] + 0.02, 0.02, rect[3] - 0.02), (rect[0] + 0.02, -0.02, rect[1] - 0.02, 0.02)):
            q = sbox(a, b, c, d).intersection(sbox(x0 + 0.01, z0 + 0.01, x1 - 0.01, z1 - 0.01))
            for (aa, bb, cc, dd) in holes: q = q.difference(sbox(aa - 0.01, bb - 0.01, cc + 0.01, dd + 0.01))
            ext_y(p, 'seam', q, 0.0, 0.004)
    else: ext_y(p, 'concrete' if kind == 'concrete' else 'floor', sq, -0.03, 0.0)
    if lv == 'g':
        q = sbox(rect[0] + 0.02, rect[2] + 0.02, rect[1] - 0.02, rect[3] - 0.02); ext_y(p, 'plinth', q, -RAISE + 0.02, -0.03)
    else:
        sqi = sbox(x0 + 0.02 * (1 - trim[0]), z0 + 0.02 * (1 - trim[2]), x1 - 0.02 * (1 - trim[1]), z1 - 0.02 * (1 - trim[3]))
        for (a, b, c, d) in holes: sqi = sqi.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
        ext_y(p, 'plaster', sqi, -SLAB - 0.005, -0.03)
    return p

# ============================================================================ portas
def door_double(w=0.77, h=2.22, t=0.055):
    """Folha da porta dupla principal: vidro alto com grade de ferro, 2 almofadas embaixo, puxador de latao. Pivo: dobradica, embaixo."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2); a, b = 0.12, w - 0.12
    cut = [tbox(a, b, 1.25, h - 0.14, -t, t)] + [tbox(a, b, y0, y1, z - 0.01, z + 0.01) for (y0, y1) in ((0.16, 0.55), (0.66, 1.1)) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', a - 0.004, b + 0.004, 1.246, h - 0.136, -0.004, 0.004)
    for sz in (1, -1):    # grade de ferro dos dois lados do vidro
        z0, z1 = sorted((sz * (t / 2 - 0.01), sz * (t / 2 + 0.004)))
        for i in range(1, 3): xx = a + (b - a) * i / 3; p.box('iron', xx - 0.008, xx + 0.008, 1.25, h - 0.14, z0, z1)
        yy = 1.25 + (h - 1.39) / 2; p.box('iron', a, b, yy - 0.008, yy + 0.008, z0, z1)
    p.add('door', bl_detail(tbox(0.05, w - 0.05, 1.16, 1.21, -t / 2 - 0.02, t / 2 + 0.02), bevel=0.006, segments=2))
    for z in (1, -1):
        p.cyl('brass', 0.012, 0.85, 1.35, w - 0.09, z * (t / 2 + 0.05), 10)
        for yy in (0.88, 1.32): p.seg('brass', (w - 0.09, yy, z * t / 2), (w - 0.09, yy, z * (t / 2 + 0.05)), 0.01)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p

# ============================================================================ pavilhao: parede lateral e enchimento da quina interna
def ps_piece(fl):
    """Parede lateral do pavilhao (1 m, pivo no centro da face externa): mesma estrutura dos modulos de cantaria do andar."""
    p = Piece(); x0, x1 = -0.5, 0.5
    if fl == 0:
        wall_core(p, [], -RAISE, H0, 'ashlar', x0=x0, x1=x1); rustication(p, [], 'ashlar', x0, x1, d=0.04, c=0.02); base_course(p, (), x0, x1)
    elif fl in (1, 2):
        wall_core(p, [], -SLAB, H0, 'ashlar', zo=-0.012, x0=x0, x1=x1); rustication(p, [], 'ashlar', x0, x1, d=0.012, c=0.006, y0=-SLAB, y1=H0, n=8)
        prof_x(p, 'trim', x0, x1, BELT if fl == 1 else sill_course(UW_[1]))
    else:
        wall_core(p, [], -SLAB, PAVH - 0.08, 'ashlar', inner='ashlar', zo=-0.012, x0=x0, x1=x1)
        rustication(p, [], 'ashlar', x0, x1, d=0.012, c=0.006, y0=-SLAB, y1=PAVH - 0.08, n=5)
        cornice(p, x0, x1); prof_x(p, 'coping', x0, x1, COPE(PAVH))
    return p
def filler(part):
    """Enchimento da quina interna entre a parede da frente e o pavilhao (0,3 x 0,3 m), um por andar: gesso por dentro,
    cantaria no atico (acima do terraco). Pivo: a quina, na cota do piso do andar."""
    p = Piece()
    if part == 'g': p.box('plaster', -T, 0.0, -RAISE, H0, -T, 0.0)
    elif part == 'u': p.box('plaster', -T, 0.0, -SLAB, H0, -T, 0.0)
    else: p.box('ashlar', -T, 0.0, -SLAB, PAVH - 0.08, -T, 0.0)
    return p

# ============================================================================ escadaria da frente, fundos, luzes
PDW = 2.6; PDL = 1.2; NST = 4; RST = RAISE / NST
def podium():
    """Patamar de granito na porta principal (pivo: face do pavilhao, eixo, cota do piso), 4 degraus de 0,15 x 0,3 m,
    muretas laterais com pedestais para os postes de luz."""
    p = Piece(); x0, x1 = -PDW, PDW
    p.box('stone2', x0 + 0.3, x1 - 0.3, -0.04, 0.0, 0.0, PDL); p.box('plinth', x0 + 0.305, x1 - 0.305, -RAISE, -0.04, 0.003, PDL - 0.005)
    for i in range(NST):
        y = -RAISE + (i + 1) * RST; z0 = PDL + (NST - 1 - i) * 0.3
        prof_x(p, 'stone2', x0 + 0.3, x1 - 0.3, [(z0, y - RST - 0.01), (z0 + 0.3, y - RST - 0.01), (z0 + 0.3, y - 0.03), (z0 + 0.32, y - 0.012), (z0 + 0.32, y), (z0, y)])
    ZE = PDL + NST * 0.3
    for s in (-1, 1):
        a, b = sorted((s * (PDW - 0.3), s * PDW))
        p.box('ashlar', a, b, -RAISE, 0.35, 0.0, ZE - 0.35)
        p.cham('trim', a - 0.03, b + 0.03, 0.35, 0.42, 0.0, ZE - 0.35, 0.01)
        p.cham('ashlar', a - 0.05, b + 0.05, -RAISE, 0.55, ZE - 0.45, ZE + 0.05, 0.01)
        p.cham('trim', a - 0.08, b + 0.08, 0.55, 0.64, ZE - 0.48, ZE + 0.08, 0.012)
    return p
def globe_lamp():
    """Poste de ferro com globo (pivo: topo do pedestal): base, fuste canelado, bracos com 2 globos e pinha."""
    p = Piece()
    lathe(p, 'iron', [(0.14, 0.0), (0.14, 0.05), (0.1, 0.1), (0.07, 0.25), (0.05, 0.35)], sec=12)
    p.cyl('iron', 0.04, 0.35, 1.9, 0.0, 0.0, 10)
    for yy in (0.6, 1.2, 1.75): p.cyl('iron', 0.05, yy, yy + 0.04, 0.0, 0.0, 10)
    for s in (-1, 1):
        seg_cyl(p, 'iron', (0.0, 1.85, 0.0), (s * 0.32, 1.95, 0.0), 0.02, 8)
        p.cyl('iron', 0.06, 1.93, 1.98, s * 0.32, 0.0, 10)
        p.sphere('lamp_glass', 0.15, s * 0.32, 2.12, 0.0)
        p.cyl('iron', 0.04, 2.25, 2.3, s * 0.32, 0.0, 10)
    p.cyl('iron', 0.04, 1.9, 2.3, 0.0, 0.0, 10); p.sphere('lamp_glass', 0.17, 0.0, 2.44, 0.0); p.cyl('iron', 0.05, 2.59, 2.64, 0.0, 0.0, 10)
    lathe(p, 'iron', [(0.04, 2.64), (0.03, 2.7), (0.0, 2.76)], sec=10)
    return p
def back_steps(w=0.8, d=1.0):
    """4 degraus de granito e patamar na porta dos fundos (pivo: face da parede, eixo, cota do piso)."""
    p = Piece()
    p.box('stone2', -w, w, -0.04, 0.0, 0.0, d); p.box('plinth', -w + 0.005, w - 0.005, -RAISE, -0.04, 0.0, d - 0.005)
    for i in range(NST):
        y = -RAISE + (i + 1) * RST; z0 = d + (NST - 1 - i) * 0.3
        prof_x(p, 'stone2', -w, w, [(z0, y - RST - 0.01), (z0 + 0.3, y - RST - 0.01), (z0 + 0.3, y - 0.03), (z0 + 0.32, y - 0.012), (z0 + 0.32, y), (z0, y)])
    return p
def canopy(w=1.8, d=1.1):
    """Cobertura metalica sobre a porta dos fundos (pivo: face da parede, eixo, na cota da fixacao): chapa com rufo e 2 maos-francesas."""
    p = Piece()
    p.hull('steel', [(x, y, z) for x in (-w / 2, w / 2) for (z, y) in ((0.0, 0.0), (0.0, 0.08), (d, -0.1), (d, -0.04))])
    p.box('steel', -w / 2, w / 2, -0.18, -0.04, d - 0.03, d + 0.01)
    for s in (-1, 1):
        seg_cyl(p, 'iron', (s * (w / 2 - 0.15), -0.7, 0.01), (s * (w / 2 - 0.15), -0.05, d - 0.1), 0.02, 8)
        p.box('iron', s * (w / 2 - 0.15) - 0.05, s * (w / 2 - 0.15) + 0.05, -0.78, -0.62, 0.0, 0.02)
    return p

# ============================================================================ terraco: casa de maquinas, condensadoras, torre de radio
PH0 = (-8.7, -5.7); PHX = 2.5; PHZ = 6.0; PHH = 2.75; PHT = 0.2
PDZ = 1.1     # centro da porta, medido a partir de z0
def penthouse():
    """Casa de maquinas da escada no terraco (pivo: canto interno x0, z0, cota do terraco): tijolo, gesso por dentro, porta de aco
    para o terraco, laje com capa e pingadeira, arandela."""
    p = Piece(); X, Z, Hh, t = PHX, PHZ, PHH, PHT
    def wall(x0, x1, z0, z1, holes=()):
        xs = sorted(set([x0, x1] + [h[0] for h in holes] + [h[1] for h in holes])); ys = sorted(set([0.0, Hh] + [h[3] for h in holes]))
        zs = [z0, z1]
        def cell(i, j, k):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            for (a, b, c, d) in holes:
                if a < cx < b and c < cy < d: return None
            return 'brick'
        for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)
    wall(0.0, t, 0.0, Z)                                     # lado do predio (x0): encosta na platibanda
    wall(t, X - t, 0.0, t); wall(t, X - t, Z - t, Z)         # fundo e frente
    q = Piece()
    xs = [0.0, t]; zs = sorted([0.0, PDZ - 0.5, PDZ + 0.5, Z])
    for m, mesh in grid_solid([X - t, X], [0.0, 2.2, Hh], zs, lambda i, j, k: None if (j == 0 and k == 1) else 'brick').items(): p.add(m, mesh)
    # gesso por dentro (paineis finos), forro
    for (a, b, c, d) in ((t, t + 0.015, t, Z - t), (X - t - 0.015, X - t, t, PDZ - 0.5), (X - t - 0.015, X - t, PDZ + 0.5, Z - t)):
        p.box('plaster', a, b, 0.0, Hh - 0.005, c, d)
    for (c, d) in ((t, t + 0.015), (Z - t - 0.015, Z - t)): p.box('plaster', t + 0.015, X - t - 0.015, 0.0, Hh - 0.005, c, d)
    p.box('plaster', t, X - t, Hh - 0.02, Hh, t, Z - t)
    p.box('concrete', -0.003, X + 0.08, Hh, Hh + 0.16, -0.003, Z + 0.08)
    p.box('coping', -0.002, X + 0.12, Hh + 0.16, Hh + 0.22, -0.002, Z + 0.12)
    ext_y(p, 'membrane', sbox(0.0, 0.0, X + 0.1, Z + 0.1), Hh + 0.22, Hh + 0.24)
    # batente de aco e soleira da porta
    a, b = PDZ - 0.5, PDZ + 0.5
    p.box('steel', X - t, X - t + 0.06, 0.0, 2.2, a, a + 0.06); p.box('steel', X - t, X - t + 0.06, 0.0, 2.2, b - 0.06, b); p.box('steel', X - t, X - t + 0.06, 2.14, 2.2, a + 0.06, b - 0.06)
    p.box('stone2', X - t - 0.003, X + 0.06, 0.0, 0.02, a - 0.04, b + 0.04)
    return p
def hvac():
    """Condensadora (pivo: centro, cota do terraco): base de perfis, gabinete com aletas, grade do ventilador no topo e tubos."""
    p = Piece(); a, b, h = 0.6, 0.45, 0.95
    for s in (-1, 1): p.box('iron', s * a - 0.05, s * a + 0.05, 0.0, 0.12, -b - 0.05, b + 0.05)
    p.cham('steel', -a, a, 0.12, h, -b, b, 0.015)
    for i in range(14):
        y = 0.22 + i * 0.05
        for z in (b, -b): p.box('grate', -a + 0.06, a - 0.06, y, y + 0.02, z - 0.004 * (z < 0) - 0.0 * (z > 0) - (0.0 if z > 0 else 0.0), z + 0.004 * (z > 0)) if True else None
    R = 0.36
    ext_y(p, 'grate', Point(0, 0).buffer(R + 0.03, 24).difference(Point(0, 0).buffer(R, 24)), h, h + 0.04)
    for k in range(8):
        q = Piece(); q.box('grate', -R, R, h + 0.02, h + 0.035, -0.006, 0.006)
        M = trimesh.transformations.rotation_matrix(k * math.pi / 8, [0, 1, 0]); p.merge(q, M)
    for r in (0.12, 0.24): ext_y(p, 'grate', Point(0, 0).buffer(r + 0.008, 20).difference(Point(0, 0).buffer(r, 20)), h + 0.02, h + 0.035)
    p.cyl('dark', 0.08, h + 0.0, h + 0.03, 0.0, 0.0, 12)
    for (z, r) in ((0.12, 0.02), (0.24, 0.014)):
        seg_cyl(p, 'steel', (a, 0.3, z), (a + 0.3, 0.3, z), r); seg_cyl(p, 'steel', (a + 0.3, 0.3, z), (a + 0.3, 0.003, z), r)
    return p
def mast(h=6.0):
    """Torre de radio trelicada de 3 montantes (pivo: centro, cota do terraco), com chapa de base, antenas e uma parabolica."""
    p = Piece(); r = 0.25; pts = [(r * math.cos(a), r * math.sin(a)) for a in (math.pi / 2, math.pi / 2 + 2 * math.pi / 3, math.pi / 2 + 4 * math.pi / 3)]
    p.cham('steel', -0.45, 0.45, 0.0, 0.03, -0.45, 0.45, 0.008)
    for (x, z) in pts: seg_cyl(p, 'steel', (x, 0.03, z), (x, h, z), 0.022, 8)
    n = int(h / 0.6)
    for i in range(n):
        y0, y1 = 0.03 + i * 0.6, 0.03 + (i + 1) * 0.6
        for j in range(3):
            (xa, za), (xb, zb) = pts[j], pts[(j + 1) % 3]
            seg_cyl(p, 'steel', (xa, y0, za), (xb, y1, zb), 0.009, 6); seg_cyl(p, 'steel', (xa, y1, za), (xb, y1, zb), 0.009, 6)
    for (x, z) in pts: p.cyl('steel', 0.012, h, h + 1.6, x, z, 6)
    p.box('steel', -0.3, 0.3, h - 0.02, h + 0.02, -0.3, 0.3)
    for k, y in enumerate((h - 1.0, h - 2.2)):
        a = k * 2.1
        for s in (-1, 1): seg_cyl(p, 'steel', (0.0, y, 0.0), (s * 0.7 * math.cos(a), y + 0.02, s * 0.7 * math.sin(a)), 0.012, 6)
    q = Piece(); prof = [(0.0, 0.0), (0.2, 0.025), (0.32, 0.07), (0.34, 0.075)]
    for (r0, y0), (r1, y1) in zip(prof[:-1], prof[1:]):
        q.hull('clock', [(r * math.cos(a), y, r * math.sin(a)) for (r, y) in ((r0, y0), (r1, y1)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
    M = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]); M[:3, 3] = [0.0, h - 1.6, 0.3]; p.merge(q, M)
    seg_cyl(p, 'steel', (0.0, h - 1.6, 0.0), (0.0, h - 1.6, 0.3), 0.02, 8)
    return p
def vent():
    p = Piece(); p.cham('membrane', -0.18, 0.18, 0.0, 0.06, -0.18, 0.18, 0.02); p.cyl('steel', 0.06, 0.06, 0.55, 0.0, 0.0, 12)
    p.cyl('steel', 0.13, 0.55, 0.6, 0.0, 0.0, 14); p.hull('steel', [(0.13 * math.cos(a), 0.6, 0.13 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)] + [(0, 0.68, 0)])
    return p
def drain():
    p = Piece(); p.cyl('seam', 0.16, 0.0, 0.012, 0.0, 0.0, 16); p.hull('grate', [(0.1 * math.cos(a), 0.012, 0.1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)] + [(0, 0.09, 0)])
    return p
def flagpole(h=4.0):
    p = Piece(); p.cham('trim', -0.2, 0.2, 0.0, 0.12, -0.2, 0.2, 0.012)
    lathe(p, 'steel', [(0.05, 0.12), (0.035, h * 0.5), (0.025, h)], sec=10); p.sphere('brass', 0.07, 0.0, h + 0.06, 0.0)
    p.cham('steel', 0.03, 0.06, 1.0, 1.15, -0.012, 0.012, 0.003)
    return p
def path_slab(L, w=3.4):
    p = Piece(); n = int(round(L / 0.6))
    for i in range(n):
        z0 = -L / 2 + i * L / n + 0.006
        for k in range(2): p.cham('concrete', -w / 2 + k * w / 2 + 0.006, -w / 2 + (k + 1) * w / 2 - 0.006, -0.02, 0.03, z0, z0 + L / n - 0.012, 0.008)
    return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p

# ============================================================================ pecas
FB = list(range(-8, 9, 2)); SB = list(range(-5, 6, 2)); PB = (-2, 0, 2)
pieces = {
    'g_wall_window': g_wall('window'), 'g_wall_plain': g_wall('plain'), 'g_wall_cell': g_wall('cell'), 'g_wall_back_door': g_wall('back_door'),
    'u1_wall_window': u_wall('window', 1), 'u1_wall_plain': u_wall('plain', 1), 'u2_wall_window': u_wall('window', 2), 'u2_wall_plain': u_wall('plain', 2),
    'parapet': parapet(),
    'pv_g_window': g_wall('window', 'ashlar'), 'pv_g_door': g_wall('door', 'ashlar'),
    'pv_u1_window': u_wall('window', 1, 'ashlar', zo=-0.012, hood='flat', grid_lines=8), 'pv_u1_window_ped': u_wall('window', 1, 'ashlar', zo=-0.012, hood='pediment', grid_lines=8),
    'pv_u2_window': u_wall('window', 2, 'ashlar', zo=-0.012, hood='key', grid_lines=8),
    'pv_attic': parapet('ashlar', PAVH, 'ashlar', zo=-0.012, panel=True, grid_lines=5), 'pv_attic_clock': parapet('ashlar', PAVH, 'ashlar', zo=-0.012, clock=True, grid_lines=5),
    'pv_side_g': ps_piece(0), 'pv_filler_g': filler('g'), 'pv_filler_u': filler('u'), 'pv_filler_attic': filler('a'),
    'corner_g': corner_g(), 'corner_u1': corner_u(1), 'corner_u2': corner_u(2), 'corner_parapet': corner_p(),
    'corner_pv_g': corner_g('ashlar'), 'corner_pv_u1': corner_u(1, True), 'corner_pv_u2': corner_u(2, True), 'corner_pv_attic': corner_p(PAVH, 'ashlar'),
    'stair': stair(), 'stair_both': stair(True), 'podium': podium(), 'globe_lamp': globe_lamp(), 'back_steps': back_steps(), 'canopy': canopy(),
    'wall_lantern': wall_lantern(), 'penthouse': penthouse(), 'hvac': hvac(), 'radio_mast': mast(), 'vent': vent(), 'roof_drain': drain(), 'flagpole': flagpole(),
    'door_leaf_front': door_double(), 'door_leaf_back': door_back(0.96, 2.22), 'door_leaf_roof': door_back(0.86, 2.13), 'door_leaf_interior': door_interior(),
    'door_leaf_cell': door_cell(), 'cell_front': cell_front(), 'cell_front_end': cell_front(True),
    'iw_plain': interior_wall(False, H0 - 0.005), 'iw_doorway': interior_wall(True, H0 - 0.005), 'iw_end_plain': interior_wall(False, H0 - 0.005, end=True),
    'iw_end_doorway': interior_wall(True, H0 - 0.005, end=True), 'player_scale_ref': player_ref()}

for sg, nm in ((1, 'r'), (-1, 'l')):
    for k, f in (('u1', lambda: u_wall('window', 1)), ('u2', lambda: u_wall('window', 2)), ('parapet', lambda: parapet())):
        pieces[(f'{k}_wall_window' if k != 'parapet' else 'parapet') + '_pv' + nm] = wall_side(f(), sg)
    for fl, k in ((1, 'u1'), (2, 'u2'), (3, 'attic')): pieces[f'pv_side_{k}_{nm}'] = ps_side(ps_piece(fl), sg)

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
def ftag(fl): return f'floor{fl}'
faces = [(0, FB, lambda u: (u, SZ), 'front'), (90, SB, lambda u: (SX, -u), 'right'), (180, FB, lambda u: (-u, -SZ), 'back'), (-90, SB, lambda u: (-SX, u), 'left')]
def kind_of(tag, wk, fl):
    if tag == 'front': return 'window'
    if tag == 'back': return ('cell' if wk in (4, 6, 8) else 'window') if fl == 0 else 'window'
    if tag == 'right': return {-5: 'cell', -3: 'cell', -1: 'back_door'}.get(wk, 'window') if fl == 0 else 'window'
    if tag == 'left': return 'plain' if wk in (-3, -1, 1) else 'window'
for ry, bays, f, tag in faces:
    for u in bays:
        x, z = f(u); wk = x if tag in ('front', 'back') else z
        if tag == 'front' and wk in PB: continue
        k0, k1, k2 = kind_of(tag, wk, 0), kind_of(tag, wk, 1), kind_of(tag, wk, 2)
        sf = ('_pvr' if wk == 4 else '_pvl' if wk == -4 else '') if tag == 'front' else ''
        put(f'g_wall_{k0}', x, lvl(0), z, ry, [tag, 'ext', ftag(0)])
        put(f'u1_wall_{k1}' + sf, x, lvl(1), z, ry, [tag, 'ext', ftag(1)])
        put(f'u2_wall_{k2}' + sf, x, lvl(2), z, ry, [tag, 'ext', ftag(2)])
        put('parapet' + sf, x, YR, z, ry, [tag, 'roof'])
for ry, x, z, tg in [(0, SX, SZ, ('front', 'right')), (90, SX, -SZ, ('right', 'back')), (180, -SX, -SZ, ('back', 'left')), (-90, -SX, SZ, ('left', 'front'))]:
    put('corner_g', x, lvl(0), z, ry, tg + ('ext', ftag(0))); put('corner_u1', x, lvl(1), z, ry, tg + ('ext', ftag(1)))
    put('corner_u2', x, lvl(2), z, ry, tg + ('ext', ftag(2))); put('corner_parapet', x, YR, z, ry, tg + ('roof',))
# pavilhao central
for x in PB:
    put('pv_g_door' if x == 0 else 'pv_g_window', x, lvl(0), ZP, 0, ['front', 'pavilion', ftag(0)])
    put('pv_u1_window_ped' if x == 0 else 'pv_u1_window', x, lvl(1), ZP, 0, ['front', 'pavilion', ftag(1)])
    put('pv_u2_window', x, lvl(2), ZP, 0, ['front', 'pavilion', ftag(2)])
    put('pv_attic_clock' if x == 0 else 'pv_attic', x, YR, ZP, 0, ['front', 'pavilion', 'roof'])
for s, ry in ((1, 90), (-1, -90)):
    sn = 'r' if s > 0 else 'l'
    for nm, y, tg in (('pv_side_g', lvl(0), ftag(0)), (f'pv_side_u1_{sn}', lvl(1), ftag(1)), (f'pv_side_u2_{sn}', lvl(2), ftag(2)), (f'pv_side_attic_{sn}', YR, 'roof')):
        put(nm, s * PXH, y, SZ + 0.5, ry, ['pavilion', 'ext', tg])
    for nm, y, tg in (('pv_filler_g', lvl(0), ftag(0)), ('pv_filler_u', lvl(1), ftag(1)), ('pv_filler_u', lvl(2), ftag(2)), ('pv_filler_attic', YR, 'roof')):
        put(nm, s * PXH, y, SZ, 0 if s > 0 else -90, ['pavilion', tg])
for ry, x in ((0, PXH), (-90, -PXH)):
    for nm, y, tg in (('corner_pv_g', lvl(0), ftag(0)), ('corner_pv_u1', lvl(1), ftag(1)), ('corner_pv_u2', lvl(2), ftag(2)), ('corner_pv_attic', YR, 'roof')): put(nm, x, y, ZP, ry, ['pavilion', 'ext', 'front', tg])
put('flagpole', 0.0, YR + PAVH, ZP - T / 2 - 0.02, 0, ['pavilion', 'roof'])
# escadaria, postes, fundos
put('podium', 0, lvl(0), ZP, 0, ['front', 'porch'])
ZE = ZP + PDL + NST * 0.3
for s in (-1, 1): put('globe_lamp', s * (PDW - 0.15), lvl(0) + 0.64, ZE - 0.2, 0, ['front', 'porch'])
put('back_steps', SX, lvl(0), -1.0, 90, ['right', 'ext']); put('canopy', SX, lvl(0) + 2.75, -1.0, 90, ['right', 'ext'])
for dz in (-0.85, 0.85): put('wall_lantern', SX + 0.0, lvl(0) + 1.95, -1.0 + dz, 90, ['right', 'ext'])
# portas externas
hx, hz = hinge(0, ZP, 0, -0.77, -0.15); put('door_leaf_front', hx, lvl(0) + 0.013, hz, 0, ['front', 'ext', ftag(0)], door=85)
hx, hz = hinge(0, ZP, 0, 0.77, -0.15); put('door_leaf_front', hx, lvl(0) + 0.013, hz, 180, ['front', 'ext', ftag(0)], door=-85)
hx, hz = hinge(SX, -1.0, 90, -0.48, -0.15); put('door_leaf_back', hx, lvl(0) + 0.013, hz, 90, ['right', 'ext', ftag(0)], door=85)
# terraco
put('penthouse', PH0[0], YR, PH0[1], 0, ['roof'])
hx, hz = PH0[0] + PHX - PHT / 2, PH0[1] + PDZ - 0.43
put('door_leaf_roof', hx, YR + 0.02, hz, -90, ['roof'], door=85)
put('wall_lantern', PH0[0] + PHX, YR + 2.4, PH0[1] + PDZ + 0.75, -90 + 180, ['roof'])
for (x, z) in ((1.0, -3.6), (3.6, -3.6)): put('hvac', x, YR, z, 0, ['roof'])
put('radio_mast', 6.0, YR, 2.6, 0, ['roof'])
for (x, z) in ((-3.0, 2.5), (-1.0, -4.5), (5.5, -1.5)): put('vent', x, YR, z, 0, ['roof'])
for (x, z) in ((-4.5, -4.5), (4.5, -4.5), (-4.5, 4.0), (4.5, 4.0)): put('roof_drain', x, YR, z, 0, ['roof'])

# ---------- pisos, escada, buracos ----------
HOLES = {1: [(LA[0], ZB, LA[1], ZA - 1.5)], 2: [(LB[0], ZB + 1.5, LB[1], ZA)], 3: [(LA[0], ZB, LA[1], ZA - 1.5)]}
def fkind(fl, a, b):
    if fl == 3: return 'membrane'
    if a in (-8, -6) and b <= 1: return 'marble'                  # hall da escada
    if b == 1 and a >= -4: return 'marble'                        # corredor
    if fl == 0 and a in PB and b >= 3: return 'marble'            # saguao
    if a in (-4, -2) and b < 0: return 'bath'
    if fl == 0 and a >= 4 and b < 0: return 'concrete'            # celas
    return 'floor'
TILE_N = {}
def tile_piece(kind, lv, rect, holes, trim):
    key = (kind, lv, rect, tuple(holes), trim)
    if key not in TILE_N:
        nm = f'floor_{kind}_{lv}' + ('_half' if rect[3] - rect[2] < 1.5 else '') + ('_e' + ''.join(map(str, trim)) if any(trim) else '')
        i = 2
        base = nm
        while nm in pieces: nm = f'{base}_h{i}'; i += 1
        pieces[nm] = floor_tile(kind, lv, rect, holes, trim); TILE_N[key] = nm
    return TILE_N[key]
for fl in (0, 1, 2, 3):
    lv = 'g' if fl == 0 else ('r' if fl == 3 else 'u')
    cells = [(a, b, (-1, 1, -1, 1)) for a in FB for b in SB] + [(a, SZ + 0.5, (-1, 1, -0.5, 0.5)) for a in PB]
    for (a, b, rect) in cells:
        half = rect[3] < 1
        tr = (int(a == FB[0] or (half and a == -2)), int(a == FB[-1] or (half and a == 2)), int(b == SB[0] and not half), int(half or (b == SB[-1] and a not in PB)))
        hs = []
        for (x0, z0, x1, z1) in HOLES.get(fl, []):
            r = sbox(a + rect[0], b + rect[2], a + rect[1], b + rect[3]).intersection(sbox(x0, z0, x1, z1))
            if r.area > 1e-6: bb = r.bounds; hs.append((round(bb[0] - a, 3), round(bb[1] - b, 3), round(bb[2] - a, 3), round(bb[3] - b, 3)))
        kind = fkind(fl, a, b) if not half else ('membrane' if fl == 3 else 'marble' if fl == 0 else 'floor')
        put(tile_piece(kind, lv, rect, hs, tr), a, lvl(fl), b, 0, [ftag(fl) if fl < 3 else 'roof'])
put('stair', LA[0], lvl(0), ZA, 0, [ftag(0)]); put('stair_both', LB[1], lvl(1), ZB, 180, [ftag(1)]); put('stair', LA[0], lvl(2), ZA, 0, [ftag(2)])
def put_rail(fl, x0, z0, x1, z1, posts=(True, True)):
    Lr = round(abs(x1 - x0) + abs(z1 - z0), 3); nm = f'rail_{int(round(Lr * 100))}' + ('' if all(posts) else '_' + ''.join('1' if q else '0' for q in posts))
    if nm not in pieces: pieces[nm] = rail(Lr, posts)
    if abs(z1 - z0) < 1e-6: put(nm, min(x0, x1), lvl(fl), z0, 0, [ftag(fl) if fl < 3 else 'roof'])
    else: put(nm, x0, lvl(fl), max(z0, z1), 90, [ftag(fl) if fl < 3 else 'roof'])
XG = (LA[1] + LB[0]) / 2
XR = LB[1] + 0.1     # os lances de travessa param na face dos pilaretes dos guarda-corpos laterais
put_rail(1, XG, ZB, XG, ZA - 1.5); put_rail(1, LA[0], ZA - 1.5, XG - 0.04, ZA - 1.5, (True, False))
put_rail(2, XG, ZB + 1.5, XG, ZA); put_rail(2, XR, ZB + 1.5, XR, ZA); put_rail(2, XG + 0.04, ZB + 1.5, XR - 0.04, ZB + 1.5, (False, False))
put_rail(3, XG, ZB, XG, ZA - 1.5); put_rail(3, LA[0] + PHT + 0.015, ZA - 1.5, XG - 0.04, ZA - 1.5, (True, False))
# ---------- paredes internas ----------
MX0, MX1, MZ0, MZ1 = -SX, SX, -SZ, SZ
def swing_z(z0, room_side):     # porta numa parede ao longo de X: abre para o lado do comodo (-1 = -Z, 1 = +Z)
    return 0 if room_side < 0 else 180
def wl(fl, x0, z0, x1, z1, doors=(), side=-1, cells=False):
    """Paredes internas: modulos de 2 m na linha; pontas que encostam nas paredes externas usam a versao 'end'.
    side: lado para onde as portas abrem (-1 = -Z/-X, 1 = +Z/+X)."""
    y = lvl(fl)
    if z0 == z1:
        cs = list(range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2))
        for c in cs:
            end = (c - 1 == MX0) or (c + 1 == MX1); d = c in doors
            ry = 0 if (c + 1 == MX1 or not end) else 180
            if cells: put('cell_front_end' if end else 'cell_front', c, y, z0, ry, [ftag(fl)])
            else: put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), c, y, z0, ry, [ftag(fl)])
            if d or cells:
                dr = 0 if side < 0 else 180
                hx, hz = hinge(c, z0, dr, -0.41 if cells else -0.43, 0); put('door_leaf_cell' if cells else 'door_leaf_interior', hx, y + 0.01, hz, dr, [ftag(fl)], door=90 if cells else 75)
    else:
        cs = list(range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2))
        for c in cs:
            end = (c - 1 == MZ0) or (c + 1 == MZ1); d = c in doors
            ry = (90 if c - 1 == MZ0 else -90) if end else 90
            put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), x0, y, c, ry, [ftag(fl)])
            if d:
                hry = 90 if side < 0 else -90
                hx, hz = hinge(x0, c, hry, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, hry, [ftag(fl)], door=90)
for fl in (0, 1, 2):
    wl(fl, -5.0, MZ0, -5.0, 2.0, doors=(1,), side=1)                       # hall da escada (abre para o corredor)
    wl(fl, -5.0, 0.0, MX1, 0.0, doors=(-2, 2, 4), side=-1)                 # fundo do corredor
    wl(fl, -1.0, MZ0, -1.0, 0.0); wl(fl, 3.0, MZ0, 3.0, 0.0)
    wl(fl, -3.0, 2.0, -3.0, MZ1); wl(fl, 3.0, 2.0, 3.0, MZ1)
    wl(fl, MX0, 2.0, -3.0, 2.0, doors=(-4,), side=1); wl(fl, 3.0, 2.0, MX1, 2.0, doors=(4,), side=1)
    if fl > 0: wl(fl, -3.0, 2.0, 3.0, 2.0, doors=(0,), side=1)
wl(0, 5.0, MZ0, 5.0, -2.0); wl(0, 7.0, MZ0, 7.0, -2.0)
wl(0, 3.0, -2.0, MX1, -2.0, side=-1, cells=True)
# calcada da frente
ZW0 = ZE + 0.02; ZW1 = ZW0 + 3.6
pieces['path_slab'] = path_slab(ZW1 - ZW0)
put('path_slab', 0.0, 0.0, (ZW0 + ZW1) / 2, 0, ['garden'])
put('player_scale_ref', 3.2, 0, ZE + 0.6); put('player_scale_ref', 0.8, lvl(0), ZP + 0.6, 0, ['porch']); put('player_scale_ref', 1.2, lvl(0), 4.0, 0, [ftag(0)])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    json.dump({'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE, 'floors': 3, 'footprint': [2 * SX, 2 * SZ],
                        'pavilion': {'x': [-PXH, PXH], 'z': [SZ, ZP]}, 'roof_level': YR, 'parapet': PAR, 'stair_holes': HOLES,
                        'roof': 'flat membrane roof behind a brick parapet; stair penthouse, condensers, radio mast',
                        'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
               'placements': L}, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc = trimesh.Scene()
    for i, e in enumerate(L):
        if e['piece'] == 'player_scale_ref': continue
        Tm = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); Tm[:3, 3] = e['pos']
        s = pieces[e['piece']].scene(e['piece'])
        for nm, g in s.geometry.items():
            g = g.copy(); g.apply_transform(Tm); sc.add_geometry(g, node_name=f'{i}_{nm}', geom_name=f'{i}_{nm}')
    bym = {}
    for g in sc.geometry.values(): bym.setdefault(g.visual.material.name, []).append(g)
    sc2 = trimesh.Scene()
    for k, gs in bym.items():
        m = trimesh.util.concatenate(gs); m.visual.material = MATS[k]; sc2.add_geometry(m, node_name=f'building_{k}', geom_name=f'building_{k}')
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    tot = sum(len(g.faces) for g in sc2.geometry.values())
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:12]: print(f'  {n:28s} {p.tris():6d} tri')
# folha da janela em no proprio, para o jogo abrir (scripts/detalhe/folhas.py, grava janelas.json)
import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe')); import folhas as _folhas
_folhas.kit(OUT)
