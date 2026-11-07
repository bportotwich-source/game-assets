"""Kit 26: vila urbana europeia (Stadtvilla) de 14 x 10 m e 2 andares, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Terreo rusticado em fiadas com chanfro, andar de cima rebocado com cunhais de pedra, faixa entre os andares e cornija com
modilhoes; telhado de quatro aguas em ardosia (fiadas em geometria) com frontao triangular sobre o eixo e 3 aguas-furtadas;
portico de 2 colunas toscanas carregando a sacada de balaustres; janelas de abrir com bandeira, molduras, venezianas;
escada interna de madeira com balaustrada; jardim com gradil de ferro, pilares e portao.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'rust': (230, 219, 196), 'render': (218, 172, 150), 'trim': (234, 228, 212), 'plinth': (150, 146, 138), 'shingles': (72, 78, 90),
                  'floor': (150, 102, 66), 'plaster': (243, 239, 229), 'shutter': (50, 82, 66), 'door': (54, 74, 64), 'brick': (150, 76, 60),
                  'wood': (92, 58, 38), 'stone2': (200, 192, 176), 'frame': (246, 244, 238), 'sash': (246, 244, 238), 'iron': (30, 32, 34),
                  'ridge': (70, 74, 80), 'gutter': (96, 100, 104), 'door_int': (240, 236, 226)},
           texturas={'rust': 'render', 'render': 'render', 'trim': 'plaster', 'plinth': 'stone', 'shingles': 'shingles', 'floor': 'planks',
                     'plaster': 'plaster', 'shutter': 'paint', 'brick': 'brick', 'stone2': 'stone2', 'wood': 'planks'},
           out=OUT)
MATS = D.MATS; TEX = D.TEX

W = 2.0; T = 0.3; H = 3.2; SLAB = 0.25; RAISE = 0.75; SX = 7.0; SZ = 5.0
H0 = H - SLAB            # altura das paredes do terreo (o andar de cima comeca na face de baixo da laje)
PL = 0.35                # topo do embasamento de pedra
YE = 2 * H               # topo das paredes = linha do beiral (relativo ao piso do terreo)
def lvl(fl): return RAISE + fl * H

# ============================================================================ ferramentas
def ext(p, mat, poly, z0, z1):
    """Poligono no plano (x, y) extrudado em Z."""
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type == 'Polygon' and g.area > 1e-6:
            m = trimesh.creation.extrude_polygon(g, z1 - z0); m.apply_translation([0, 0, z0]); p.add(mat, D._fix(m))
def ext_y(p, mat, poly, y0, y1):
    """Poligono no plano (x, z) extrudado em Y."""
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type == 'Polygon' and g.area > 1e-6:
            m = trimesh.creation.extrude_polygon(g, y1 - y0); v = m.vertices.copy()
            m.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1); m.invert(); p.add(mat, D._fix(m))
def seg_cyl(p, mat, p0, p1, r, sec=10):
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1 - p0; L = np.linalg.norm(v)
    c = trimesh.creation.cylinder(radius=r, height=L, sections=sec); z = np.array([0, 0, 1.0]); v = v / L
    ax = np.cross(z, v); ang = math.acos(np.clip(np.dot(z, v), -1, 1))
    if np.linalg.norm(ax) > 1e-6: c.apply_transform(trimesh.transformations.rotation_matrix(ang, ax))
    elif v[2] < 0: c.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    c.apply_translation((p0 + p1) / 2); return p.add(mat, c)
def lathe(p, mat, prof, x=0.0, z=0.0, y0=0.0, sec=14):
    """Peca torneada: prof = [(raio, y), ...] de baixo para cima (cascas convexas por trecho)."""
    for (r0, ya), (r1, yb) in zip(prof[:-1], prof[1:]):
        if abs(yb - ya) < 1e-6: continue
        pts = [(x + r * math.cos(a), y0 + y, z + r * math.sin(a)) for (r, y) in ((r0, ya), (r1, yb)) for a in np.linspace(0, 2 * math.pi, sec, endpoint=False)]
        p.hull(mat, pts)
def mitre_cut(m, keep_x_le_z=True):
    """Corta uma extrusao no plano x = z (quina externa em (0, 0)): mantem x <= z (ou z <= x)."""
    n = [-1, 0, 1] if keep_x_le_z else [1, 0, -1]; n = np.array(n) / math.sqrt(2)
    return slice_keep(m, [0, 0, 0], n)

# ---------- paredes externas ----------
COURSE = (H0 - PL) / 6      # 6 fiadas rusticadas no terreo
def wall_core(p, holes, y0, h, outer_mat, inner='plaster', zo=-0.03):
    """Nucleo estanque (grid_solid) com buracos [(x0, x1, y0, y1)]: camada interna de gesso (2 cm) e corpo ate z=zo.
    A camada interna para 5 mm abaixo do topo (cantos sem faces coplanares)."""
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, 0.0, h - 0.005, h] + [max(y0, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0:
            if cy < 0.0 or ys[j] >= h - 0.0051: return None if ys[j] >= h - 0.0051 else outer_mat
            return inner
        return outer_mat
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, zo], cell).items(): p.add(m, mesh)
def bands(holes, y0, y1, x0=-W / 2, x1=W / 2):
    """Pedacos [(a, b, ya, yb)] da faixa y0..y1 fora dos buracos."""
    cuts = sorted(set([y0, y1] + [y for h in holes for y in (h[2], h[3]) if y0 < y < y1])); out = []
    for ya, yb in zip(cuts[:-1], cuts[1:]):
        xs = [(x0, x1)]
        for (hx0, hx1, hy0, hy1) in holes:
            if ya >= hy0 - 1e-9 and yb <= hy1 + 1e-9: xs = [s for a, b in xs for s in ((a, min(b, hx0)), (max(a, hx1), b)) if s[1] - s[0] > 1e-4]
        out += [(a, b, ya, yb) for a, b in xs]
    return out
def rustication(p, holes, x0=-W / 2, x1=W / 2):
    """Fiadas rusticadas (reboco em faixas com chanfro de 1,5 cm em cima e embaixo, 3 cm de espessura) de PL a H0."""
    for k in range(6):
        b0 = PL + k * COURSE; b1 = b0 + COURSE
        for (a, b, ya, yb) in bands(holes, b0, b1, x0, x1):
            prof_x(p, 'rust', a, b, crect(-0.03, 0.0, ya, yb, 0.015, (0, 1 if abs(ya - b0) < 1e-6 else 0, 1 if abs(yb - b1) < 1e-6 else 0, 0)))
def base_course(p, gaps=(), x0=-W / 2, x1=W / 2):
    """Embasamento de pedra (de -RAISE a PL), 1 cm saliente, com chanfro em cima; para nos vaos de porta."""
    xs = [x0] + [v for g in gaps for v in g] + [x1]
    for i in range(0, len(xs) - 1, 2):
        if xs[i + 1] - xs[i] > 0.01: prof_x(p, 'plinth', xs[i], xs[i + 1], crect(-0.03, 0.01, -RAISE, PL, 0.012, (0, 0, 1, 0)))
BELT = [(0.0, -0.25), (0.05, -0.25), (0.05, -0.2), (0.065, -0.185), (0.065, -0.05), (0.08, -0.04), (0.09, -0.01), (0.09, 0.03), (0.07, 0.05), (0.0, 0.08)]
def belt(p, x0=-W / 2, x1=W / 2): prof_x(p, 'trim', x0, x1, BELT)
# cornija sob o beiral: arquitrave, friso, modilhoes e coroa; o topo segue a face de baixo do beiral (YE - KR*z)
KR = math.tan(math.radians(35)); CS = math.cos(math.radians(35)); OVER = 0.55
def cornice_prof(y):
    top = lambda z: y - KR * z - 0.004
    return [(0.0, y - 0.62), (0.04, y - 0.62), (0.04, y - 0.5), (0.055, y - 0.48), (0.055, y - 0.44), (0.0, y - 0.44)]
def cornice_crown(y):
    t = lambda z: y - KR * z - 0.004
    return [(0.0, y - 0.18), (0.1, y - 0.18), (0.12, y - 0.16), (0.3, y - 0.16), (0.33, y - 0.13), (0.35, y - 0.1), (0.35, t(0.35)), (0.0, t(0.0))]
def cornice(p, x0=-W / 2, x1=W / 2, y=H, modillions=True):
    prof_x(p, 'trim', x0, x1, cornice_prof(y)); prof_x(p, 'trim', x0, x1, cornice_crown(y))
    if modillions:
        for xx in np.arange(x0 + 0.25, x1 - 0.1, 0.5):
            p.hull('trim', [(xx + dx, yy, z) for dx in (-0.045, 0.045) for (z, yy) in ((0.0, y - 0.18), (0.0, y - 0.34), (0.06, y - 0.34), (0.1, y - 0.26), (0.26, y - 0.24), (0.26, y - 0.18))])

# ---------- janelas de abrir com bandeira ----------
def casement(p, ow, oy0, oy1, transom=0.42, z=-0.12, lites=3):
    """Caixilho de madeira recuado (face em z), 2 folhas de abrir com baguetes, travessa e bandeira com montante."""
    x = ow / 2; f = 0.07; zb, zf = z - 0.08, z
    p.box('frame', -x, -x + f, oy0, oy1, zb, zf); p.box('frame', x - f, x, oy0, oy1, zb, zf)
    p.box('frame', -x + f, x - f, oy1 - f, oy1, zb, zf); p.box('frame', -x + f, x - f, oy0, oy0 + 0.06, zb, zf)
    yt = oy1 - transom
    p.cham('frame', -x + f, x - f, yt - 0.035, yt + 0.035, zb, zf + 0.01, 0.008)
    zs0, zs1 = zb + 0.015, zf - 0.015
    for (a, b) in ((-x + f, -0.004), (0.004, x - f)):
        s = 0.055; ya, yb = oy0 + 0.06, yt - 0.035
        p.cham('sash', a, a + s, ya, yb, zs0, zs1, 0.006); p.cham('sash', b - s, b, ya, yb, zs0, zs1, 0.006)
        p.cham('sash', a + s - 0.002, b - s + 0.002, ya, ya + 0.07, zs0, zs1, 0.006); p.cham('sash', a + s - 0.002, b - s + 0.002, yb - s, yb, zs0, zs1, 0.006)
        zc = (zs0 + zs1) / 2; p.box('glass', a + s - 0.004, b - s + 0.004, ya + 0.066, yb - s + 0.004, zc - 0.003, zc + 0.003)
        for i in range(1, lites):
            yy = ya + 0.07 + (yb - s - ya - 0.07) * i / lites; p.cham('sash', a + s, b - s, yy - 0.012, yy + 0.012, zc - 0.012, zc + 0.012, 0.004)
    zc = (zb + zf) / 2
    p.box('glass', -x + f - 0.004, x - f + 0.004, yt + 0.031, oy1 - f + 0.004, zc - 0.003, zc + 0.003)
    p.cham('frame', -0.02, 0.02, yt + 0.035, oy1 - f, zc - 0.015, zc + 0.015, 0.005)
def surround(p, ow, oy0, oy1, w=0.12, d=0.035, keystone=False, hood=False, sill=True):
    """Moldura de pedra em volta do vao (faixa com filete), peitoril com pingadeira, aduela (keystone) ou cornija de coroamento."""
    x = ow / 2
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x + w)))
        prof_y(p, 'trim', oy0 - (0.0 if sill else 0.0), oy1 + w, crect(a, b, 0.0, d, 0.008, (0, 0, 1, 1)))
        a2, b2 = sorted((s * (x + w - 0.03), s * (x + w)))
        prof_y(p, 'trim', oy0 + 0.04, oy1 + w - 0.03, crect(a2, b2, d, d + 0.012, 0.004, (0, 0, 1, 1)))
    prof_x(p, 'trim', -x, x, crect(0.0, d, oy1, oy1 + w, 0.008, (0, 1, 1, 0)))
    prof_x(p, 'trim', -x - w + 0.03, x + w - 0.03, crect(d, d + 0.012, oy1 + w - 0.03, oy1 + w - 0.001, 0.004, (0, 1, 1, 0)))
    if sill:
        prof_x(p, 'trim', -x - w - 0.04, x + w + 0.04, [(-0.06, oy0 - 0.09), (0.07, oy0 - 0.09), (0.085, oy0 - 0.075), (0.085, oy0 - 0.03),
                                                       (0.06, oy0 + 0.004), (-0.06, oy0 + 0.004)])
        for s in (-1, 1): p.hull('trim', [(s * (x + dx), y, z) for dx in (0.0, 0.1) for (z, y) in ((0.0, oy0 - 0.09), (0.0, oy0 - 0.25), (0.05, oy0 - 0.09))])
    if keystone:
        p.hull('trim', [(sx * ww, y, z) for (ww, y) in ((0.07, oy1 - 0.05), (0.11, oy1 + w + 0.06)) for sx in (-1, 1) for z in (0.0, d + 0.03)])
    if hood:
        yh = oy1 + w
        p.hull('trim', [(sx * (x + w + 0.02), y, z) for sx in (-1, 1) for (z, y) in ((0.0, yh), (0.0, yh + 0.05), (0.05, yh), (0.05, yh + 0.05))])
        prof_x(p, 'trim', -x - w - 0.08, x + w + 0.08, [(0.0, yh + 0.05), (0.09, yh + 0.05), (0.11, yh + 0.08), (0.12, yh + 0.13), (0.12, yh + 0.16), (0.0, yh + 0.2)])
        for s in (-1, 1): p.hull('trim', [(s * (x + w - dx), y, z) for dx in (0.0, 0.07) for (z, y) in ((0.0, yh - 0.28), (0.0, yh + 0.05), (0.09, yh + 0.05), (0.04, yh - 0.2))])
def shutter(p, x0, x1, y0, y1, z0=0.04):
    """Veneziana aberta encostada na parede: quadro, travessa no meio e palhetas inclinadas em geometria."""
    t = 0.03; s = 0.05
    p.cham('shutter', x0, x0 + s, y0, y1, z0, z0 + t, 0.006); p.cham('shutter', x1 - s, x1, y0, y1, z0, z0 + t, 0.006)
    ym = (y0 + y1) / 2
    for (a, b) in ((y0, y0 + 0.08), (ym - 0.04, ym + 0.04), (y1 - 0.08, y1)): p.cham('shutter', x0 + s - 0.002, x1 - s + 0.002, a, b, z0, z0 + t, 0.006)
    for (ya, yb) in ((y0 + 0.08, ym - 0.04), (ym + 0.04, y1 - 0.08)):
        n = int((yb - ya) / 0.055)
        for i in range(n):
            yy = ya + (i + 0.5) * (yb - ya) / n
            p.hull('shutter', [(x, yy + dy, z) for x in (x0 + s - 0.002, x1 - s + 0.002) for (dy, z) in ((-0.026, z0 + t - 0.004), (-0.018, z0 + t - 0.0), (0.022, z0 + 0.004), (0.014, z0 + 0.0))])
    p.box('dark', x0 + s, x1 - s, y0 + 0.08, y1 - 0.08, z0 + 0.002, z0 + 0.006)
    for yy in (y0 + 0.25, y1 - 0.25): p.box('iron', x0 + 0.01, x0 + 0.16, yy - 0.015, yy + 0.015, z0 + t, z0 + t + 0.006)

# ---------- modulos de parede ----------
GW_ = (0.9, 1.0, 2.6)       # janela do terreo: largura, peitoril, topo
UW_ = (0.9, 0.9, 2.5)       # janela do andar de cima
def g_wall(kind='window'):
    """Modulo de 2 m do terreo: embasamento de pedra, 6 fiadas rusticadas, gesso por dentro. Pivo: face externa, cota do piso."""
    p = Piece(); holes = []
    if kind == 'window': ow, a, b = GW_; holes = [(-ow / 2, ow / 2, a, b)]
    if kind == 'door': holes = [(-0.65, 0.65, 0.0, 2.9)]
    if kind == 'back_door': holes = [(-0.5, 0.5, 0.0, 2.35)]
    wall_core(p, holes, -RAISE, H0, 'rust')
    rustication(p, holes); base_course(p, [(h[0] - (0.16 if kind == 'door' else 0.12), h[1] + (0.16 if kind == 'door' else 0.12)) for h in holes if h[2] <= 0.0])
    if kind == 'window':
        ow, a, b = GW_; casement(p, ow, a, b); surround(p, ow, a, b, keystone=True)
    if kind == 'door':     # porta principal: batentes de pedra, soleira e bandeira em leque (meia-lua) sobre a verga
        x = 0.65
        prof_x(p, 'stone2', -x, x, [(-0.295, 0.012), (0.04, 0.012), (0.06, 0.0), (0.06, -0.045), (-0.295, -0.045)])
        p.box('frame', -x, -x + 0.08, 0.0, 2.9, -0.2, -0.1); p.box('frame', x - 0.08, x, 0.0, 2.9, -0.2, -0.1)
        p.box('frame', -x + 0.08, x - 0.08, 2.32, 2.4, -0.2, -0.1)
        fan = Point(0, 2.4).buffer(0.57, 24).intersection(sbox(-1, 2.4, 1, 3)).intersection(sbox(-x + 0.08, 0, x - 0.08, 2.9 - 0.06))
        p.box('frame', -x + 0.08, x - 0.08, 2.84, 2.9, -0.2, -0.1)
        ext(p, 'glass', sbox(-x + 0.08, 2.4, x - 0.08, 2.84), -0.153, -0.147)
        for a in np.linspace(0.35, math.pi - 0.35, 5):
            q = Piece(); q.box('frame', 0.0, 0.5, -0.012, 0.012, -0.165, -0.135)
            R = trimesh.transformations.rotation_matrix(a, [0, 0, 1]); R[:3, 3] = [0, 2.4, 0]; p.merge(q, R)
        surround(p, 1.3, 0.0, 2.9, w=0.16, keystone=True, sill=False)
    if kind == 'back_door':
        x = 0.5
        prof_x(p, 'stone2', -x, x, [(-0.295, 0.012), (0.04, 0.012), (0.06, 0.0), (0.06, -0.045), (-0.295, -0.045)])
        p.box('frame', -x, -x + 0.07, 0.0, 2.35, -0.2, -0.1); p.box('frame', x - 0.07, x, 0.0, 2.35, -0.2, -0.1); p.box('frame', -x, x, 2.28, 2.35, -0.2, -0.1)
        surround(p, 1.0, 0.0, 2.35, keystone=True, sill=False)
    return p
def u_wall(kind='window', shutters=True):
    """Modulo de 2 m do andar de cima (de -SLAB a H): faixa entre andares, reboco, cornija com modilhoes no topo."""
    p = Piece(); holes = []
    if kind == 'window': ow, a, b = UW_; holes = [(-ow / 2, ow / 2, a, b)]
    if kind == 'balcony': holes = [(-0.65, 0.65, 0.0, 2.6)]
    wall_core(p, holes, -SLAB, H, 'render', zo=0.0)
    belt(p); cornice(p)
    if kind == 'window':
        ow, a, b = UW_; casement(p, ow, a, b); surround(p, ow, a, b, hood=True)
        if shutters:
            for s in (-1, 1):
                x0, x1 = sorted((s * (ow / 2 + 0.03), s * (ow / 2 + 0.03 + ow / 2)))
                shutter(p, x0, x1, a + 0.01, b - 0.01)
    if kind == 'balcony':
        x = 0.65
        prof_x(p, 'stone2', -x, x, [(-0.295, 0.012), (0.04, 0.012), (0.06, 0.0), (0.06, -0.045), (-0.295, -0.045)])
        p.box('frame', -x, -x + 0.07, 0.0, 2.6, -0.2, -0.1); p.box('frame', x - 0.07, x, 0.0, 2.6, -0.2, -0.1)
        p.box('frame', -x, x, 2.53, 2.6, -0.2, -0.1); p.cham('frame', -x + 0.07, x - 0.07, 2.18, 2.25, -0.2, -0.09, 0.008)
        ext(p, 'glass', sbox(-x + 0.07, 2.25, x - 0.07, 2.53), -0.153, -0.147); p.cham('frame', -0.02, 0.02, 2.25, 2.53, -0.165, -0.135, 0.005)
        surround(p, 1.3, 0.0, 2.6, w=0.14, hood=True, sill=False)
    return p
QH = 0.36
def corner_q(part):
    """Quina dos 2 andares: nucleo que cobre o encontro das paredes, fiadas rusticadas que dobram a quina no terreo,
    cunhais de pedra alternados (0,6 / 0,35 m) no andar de cima. Pivo: quina externa, cota do piso; paredes em -X e -Z."""
    p = Piece(); e = 0.004
    if part == 'upper':     # pivo na cota do piso de cima
        p.box('render', -T - 0.01, e, -SLAB, H - 0.006, -T - 0.01, e)
        return corner_upper(p)
    p.box('rust', -T - 0.01, e, -RAISE, H0, -T - 0.01, e)
    p.cham('plinth', -T - 0.005, 0.025, -RAISE, PL, -T - 0.005, 0.025, 0.012)
    for k in range(6):
        b0 = PL + k * COURSE; b1 = b0 + COURSE; c = 0.015
        for keep in (True, False):
            q = Piece()
            if keep: prof_x(q, 'rust', -T - 0.01, 0.035, crect(-0.03, 0.035, b0, b1, c, (0, 1, 1, 0)))
            else: prof_z(q, 'rust', -T - 0.01, 0.035, [(xx, yy) for (xx, yy) in [(-0.03, b0), (0.035 - c, b0), (0.035, b0 + c), (0.035, b1 - c), (0.035 - c, b1), (-0.03, b1)]])
            mm = q.parts['rust'][0]; mm = mitre_cut(mm, keep); p.add('rust', mm)
    return p
def corner_upper(p):
    y = 0.0
    for k in range(int((H - 0.62 - y - 0.05) / QH)):
        ya, yb = y + 0.05 + k * QH, y + 0.05 + (k + 1) * QH; L1, L2 = (0.6, 0.35) if k % 2 == 0 else (0.35, 0.6)
        p.cham('trim', -L1, 0.03, ya, yb, -T - 0.005, 0.03, 0.01)
        p.cham('trim', -T - 0.005, 0.03, ya, yb, -L2, -T - 0.004, 0.01)
    # faixa e cornija dobrando a quina (meia-esquadria)
    for keep in (True, False):
        for prof, y0 in ((BELT, 0.0), (cornice_prof(H), 0.0), (cornice_crown(H), 0.0)):
            q = Piece()
            pts = [(z, yy + y0) for (z, yy) in prof]
            if keep: prof_x(q, 'trim', 0.0, 0.4, pts)
            else: prof_z(q, 'trim', 0.0, 0.4, pts)
            mm = q.parts['trim'][0]; p.add('trim', mitre_cut(mm, keep))
    return p

# ============================================================================ telhado de quatro aguas em ardosia (35 graus)
TV = 0.07; BUMP = 0.02
configurar_telhado(TV, BUMP, 35)
AXR, AZR = SX + OVER, SZ + OVER
def roof_strip(E, P, u, x0=-W / 2, x1=W / 2, fascia_ext=0.0):
    """Faixa de 2 m de uma agua. Beiral ao longo de X local em z=OVER (pivo: face da parede, cota do piso do terreo), sobe para -Z.
    E = meia largura do beiral externo, P = distancia do beiral a cumeeira, u = centro do modulo ao longo do beiral."""
    p = Piece(); top = P if P < E else E
    slope = Polygon([(-E, 0), (E, 0), (E - top, top), (-(E - top), top)]) if P < E else Polygon([(-E, 0), (E, 0), (0, E)])
    s = sbox(u + x0, 0, u + x1, top + 1).intersection(slope)
    poly = Polygon([(x - u, OVER - d) for x, d in s.exterior.coords])
    f = lambda a, b: YE - KR * b
    sheared(p, 'plaster', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: OVER - b, lambda d0, d1: sbox(-50, OVER - d1, 50, OVER - d0), top + 0.01,
                    lambda v, n: np.stack([(v[:, 0] + u) / TILE, (OVER - v[:, 2]) / CS / TILE], 1))
    yb = YE - KR * OVER; a, b = x0, x1
    a = a + fascia_ext if fascia_ext < 0 else a + 0.001
    b = b + fascia_ext if fascia_ext > 0 else b - 0.001
    prof_x(p, 'trim', a, b, crect(OVER - 0.02, OVER + 0.03, yb - 0.17 - 0.003 * (fascia_ext != 0), yb + 0.05, 0.006, (0, 1, 1, 0)))
    mit = []
    if x1 > W / 2 + 1e-6: mit.append((x1, 1))
    if x0 < -W / 2 - 1e-6: mit.append((x0, -1))
    gx0 = x0 - (0.2 if x0 < -W / 2 else 0); gx1 = x1 + (0.2 if x1 > W / 2 else 0)
    gutter_run(p, gx0, gx1, OVER + 0.03, yb + 0.02, mit)
    return p
def hip_cap():
    p = Piece(); t0, t1 = OVER + 0.02, -(AZR - OVER); yt = lambda t: YE + TV + BUMP - KR * t; pts = []
    for t in (t0, t1):
        c = np.array([t, 0, t]); n = np.array([1, 0, -1]) / math.sqrt(2)
        for (off, dy) in ((0, 0.07), (0.055, 0.055), (-0.055, 0.055), (0.13, -0.04), (-0.13, -0.04), (0, -0.12)):
            q = c + n * off; pts.append((q[0], yt(t) + dy, q[2]))
    p.hull('ridge', pts); return p
def ridge_cap(x0, x1):
    p = Piece(); y = YE + TV + BUMP + KR * (AZR - OVER); d = 0.16
    p.hull('ridge', [(x, yy, z) for x in (x0 - 0.05, x1 + 0.05) for (yy, z) in ((y - d * KR - 0.04, d), (y - d * KR - 0.04, -d), (y + 0.07, 0.0), (y + 0.055, 0.055), (y + 0.055, -0.055), (y - 0.12, 0.0))])
    for xx in (x0 - 0.05, x1 + 0.05): p.cyl('ridge', 0.035, y + 0.06, y + 0.35, xx, 0.0, 8); p.sphere('ridge', 0.05, xx, y + 0.38, 0.0)
    return p
def roof_u(b): return YE - KR * b      # face de baixo do telhado na distancia b da face da parede (b < 0 = para dentro)

# ---------- frontao sobre o eixo, com telhadinho que morre no telhado principal ----------
PW = 1.95; PHT = 1.45; PK = PHT / PW; PRC = 0.22
def pediment():
    """Frontao triangular de 3,9 m sobre a cornija (pivo: face da parede da frente, eixo, cota do piso): timpano de reboco com
    oculo, cornija inclinada de pedra, acroterios, e um telhadinho de ardosia que entra no telhado principal."""
    p = Piece(); y0 = YE
    tri = Polygon([(-PW, y0), (PW, y0), (0, y0 + PHT)]); oc = Point(0, y0 + 0.62).buffer(0.26, 20)
    ext(p, 'render', tri.difference(oc), -T, 0.0)
    ext(p, 'trim', Point(0, y0 + 0.62).buffer(0.36, 20).difference(oc), 0.0, 0.04)
    ext(p, 'frame', Point(0, y0 + 0.62).buffer(0.26, 20).difference(Point(0, y0 + 0.62).buffer(0.2, 20)), -0.16, -0.1)
    ext(p, 'glass', Point(0, y0 + 0.62).buffer(0.205, 20), -0.133, -0.127); ext(p, 'dark', Point(0, y0 + 0.62).buffer(0.27, 20), -0.295, -0.275)
    for a in (0, 90):
        q = Piece(); q.box('frame', -0.2, 0.2, -0.012, 0.012, -0.14, -0.12); R = trimesh.transformations.rotation_matrix(math.radians(a), [0, 0, 1]); R[:3, 3] = [0, y0 + 0.62, 0]; p.merge(q, R)
    # cornija inclinada (2 lances) e base horizontal do frontao
    for s in (-1, 1):
        a0 = np.array([s * (PW + 0.12), y0 - 0.02]); a1 = np.array([0.0, y0 + PHT + 0.12 * PK])
        pts = []
        for (x, y) in (a0, a1):
            for (dz, dy) in ((0.0, 0.0), (0.0, PRC), (0.14, PRC), (0.16, PRC - 0.04), (0.16, 0.06), (0.1, 0.0)):
                pts.append((x, y + dy, dz))
        p.hull('trim', pts)
    prof_x(p, 'trim', -PW, PW, [(0.0, y0 - 0.005), (0.1, y0 - 0.005), (0.1, y0 + 0.07), (0.0, y0 + 0.1)])
    for x in (-PW - 0.05, PW + 0.05, 0.0):
        yb = y0 + (PHT + 0.12 * PK + PRC if x == 0 else PRC - 0.02)
        p.cham('trim', x - 0.12, x + 0.12, yb - 0.02, yb + 0.22, -0.12, 0.12, 0.01); lathe(p, 'trim', [(0.06, 0.0), (0.09, 0.08), (0.05, 0.18), (0.0, 0.2)], x, 0.0, yb + 0.2, 12)
    # telhadinho: aguas de PK a partir da cornija inclinada, ate 3,6 m para dentro (enterra no telhado principal)
    ER = PW + 0.18
    f = lambda a, b: y0 + PHT + PRC + 0.12 * PK - PK * np.abs(a)
    poly = sbox(-ER, -3.6, ER, 0.18)
    def strip(d0, d1): return unary_union([sbox(ER - d1, -50, ER - d0, 50), sbox(-(ER - d0), -50, -(ER - d1), 50)])
    cs = math.cos(math.atan(PK))
    sheared(p, 'plaster', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: ER - np.abs(a), strip, ER + 0.01, lambda v, n: np.stack([v[:, 2] / TILE, (ER - np.abs(v[:, 0])) / cs / TILE], 1))
    yr = y0 + PHT + PRC + 0.12 * PK + TV + BUMP
    p.hull('ridge', [(x, yy, z) for z in (0.17, -3.2) for (x, yy) in ((-0.13, yr - 0.1), (0.13, yr - 0.1), (0.0, yr + 0.07), (0.05, yr + 0.05), (-0.05, yr + 0.05))])
    return p

# ---------- agua-furtada ----------
DY0 = 0.95; DWW = 1.3; DH = 1.25; DK = 0.9
def dormer():
    """Agua-furtada com frontao: frente de reboco com janela de 2 folhas e moldura, ilhargas de ardosia lisa, telhado de 2 aguas
    em fiadas. Pivo: face da parede, centro, cota do piso do terreo; a frente fica 1 m para dentro (z = -1)."""
    p = Piece(); zf = -1.0; x = DWW / 2; yb = roof_u(zf) - 0.12; ye = yb + 0.12 + DH
    yr = ye + x * DK
    front = Polygon([(-x, yb), (x, yb), (x, ye), (0, yr), (-x, ye)])
    ow, oy0, oy1 = 0.7, roof_u(zf) + 0.2, ye - 0.12
    ext(p, 'render', front.difference(sbox(-ow / 2, oy0, ow / 2, oy1)), zf - 0.12, zf)
    p.box('dark', -ow / 2, ow / 2, oy0, oy1, zf - 0.613, zf - 0.587)
    q = Piece(); casement(q, ow, oy0, oy1, transom=0.0001, z=-0.06, lites=2); surround(q, ow, oy0, oy1, w=0.09, sill=True)
    for m, ms in q.parts.items():
        for mm in ms: mm = mm.copy(); mm.apply_translation([0, 0, zf]); p.add(m, mm)
    zb = zf - (ye + 0.3 - roof_u(zf)) / KR     # onde o telhado alcanca o beiral da agua-furtada
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x - 0.1)))
        p.hull('render', [(xx, y, z) for xx in (a, b) for (z, y) in ((zf, yb), (zf, ye), (zb - 0.2, ye))])
        a, b = sorted((s * x, s * (x + 0.012)))
        p.hull('shingles', [(xx, y, z) for xx in (a, b) for (z, y) in ((zf - 0.12, yb + 0.06), (zf - 0.12, ye - 0.02), (zb - 0.2, ye - 0.02))])
    # beirada do frontao
    for s in (-1, 1):
        pts = []
        for (xx, yy) in ((s * (x + 0.1), ye - 0.03), (0.0, yr + 0.06)):
            for (dz, dy) in ((0.0, 0.0), (0.0, 0.12), (0.07, 0.12), (0.07, 0.0)): pts.append((xx, yy + dy, zf + dz))
        p.hull('trim', pts)
    ER = x + 0.18
    f = lambda a, b: yr + 0.1 - DK * np.abs(a)
    poly = sbox(-ER, zb - 0.5, ER, zf + 0.08)
    def strip(d0, d1): return unary_union([sbox(ER - d1, -50, ER - d0, 50), sbox(-(ER - d0), -50, -(ER - d1), 50)])
    cs = math.cos(math.atan(DK))
    sheared(p, 'plaster', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: ER - np.abs(a), strip, ER + 0.01, lambda v, n: np.stack([v[:, 2] / TILE, (ER - np.abs(v[:, 0])) / cs / TILE], 1))
    y = yr + 0.1 + TV + BUMP
    p.hull('ridge', [(xx, yy, z) for z in (zf + 0.1, zb - 0.4) for (xx, yy) in ((-0.1, y - 0.08), (0.1, y - 0.08), (0.0, y + 0.06), (0.04, y + 0.045), (-0.04, y + 0.045))])
    return p
def chimney(h):
    """Chamine de tijolo que atravessa o telhado: corpo, faixa de 3 fiadas salientes, capa de pedra e 3 manilhas. Pivo: centro, cota do piso."""
    p = Piece(); a, b = 0.42, 0.3; y0 = YE - 0.2
    p.box('brick', -a, a, y0, h - 0.35, -b, b)
    p.box('brick', -a - 0.04, a + 0.04, h - 0.35, h - 0.27, -b - 0.04, b + 0.04); p.box('brick', -a - 0.02, a + 0.02, h - 0.27, h - 0.12, -b - 0.02, b + 0.02)
    p.box('brick', -a - 0.06, a + 0.06, h - 0.12, h - 0.04, -b - 0.06, b + 0.06)
    p.hull('trim', [(x, y, z) for x in (-a - 0.09, a + 0.09) for z in (-b - 0.09, b + 0.09) for y in (h - 0.04, h + 0.03)] + [(x, h + 0.08, z) for x in (-a, a) for z in (-b, b)])
    for xx in (-0.24, 0.0, 0.24):
        p.cyl('clay', 0.075, h + 0.05, h + 0.42, xx, 0.0, 12); p.cyl('clay', 0.09, h + 0.36, h + 0.42, xx, 0.0, 12); p.cyl('dark', 0.058, h + 0.4, h + 0.425, xx, 0.0, 12)
    return p

# ============================================================================ portico, sacada, escadas externas
PZ = 1.7; PXW = 1.55; COLX = 1.15; COLZ = 1.45
def column(h):
    """Coluna toscana: plinto, toro, fuste com entase (casca convexa), colarinho, equino e abaco."""
    p = Piece(); r = 0.17
    p.cham('stone2', -0.24, 0.24, 0.0, 0.1, -0.24, 0.24, 0.01)
    lathe(p, 'trim', [(0.22, 0.1), (0.225, 0.13), (0.2, 0.18), (r + 0.01, 0.2)])
    lathe(p, 'trim', [(r + 0.01, 0.2), (r, 0.3), (r - 0.025, h - 0.32)], sec=18)
    lathe(p, 'trim', [(r - 0.01, h - 0.32), (r + 0.005, h - 0.3), (r + 0.005, h - 0.27), (r - 0.02, h - 0.25), (r + 0.04, h - 0.14), (0.0, h - 0.14)], sec=18)
    p.cham('trim', -0.25, 0.25, h - 0.14, h, -0.25, 0.25, 0.01)
    return p
def balcony():
    """Sacada sobre o portico (pivo: face da parede, eixo, cota do piso de cima): laje com cornija, viga de pedra sobre as colunas,
    piso de lajota e balaustrada de balaustres torneados com corrimao e pedestais."""
    p = Piece(); x0, x1, z1 = -PXW, PXW, PZ
    yt = -0.03
    p.box('stone2', x0, x1, yt - 0.02, yt, 0.002, z1)
    p.box('trim', x0 + 0.004, x1 - 0.004, -0.42, yt - 0.02, 0.002, z1)
    prof_x(p, 'trim', x0 - 0.08, x1 + 0.08, [(z1, -0.42), (z1 + 0.04, -0.42), (z1 + 0.06, -0.38), (z1 + 0.06, -0.12), (z1 + 0.1, -0.08), (z1 + 0.1, yt - 0.02), (z1, yt - 0.02)])
    for s in (-1, 1):
        a, b = sorted((s * PXW, s * (PXW + 0.08)))
        prof_z(p, 'trim', 0.002, z1, [(a, -0.42), (b, -0.42), (b, yt - 0.02), (a, yt - 0.02)])
    prof_x(p, 'trim', x0 - 0.08, x1 + 0.08, crect(z1, z1 + 0.1, yt - 0.02, yt + 0.06, 0.01, (0, 1, 1, 0)))
    # balaustrada em U
    hb = 0.95
    posts = [(x0 + 0.13, z1 - 0.12), (x1 - 0.13, z1 - 0.12), (x0 + 0.13, 0.12), (x1 - 0.13, 0.12), (0.0, z1 - 0.12)]
    for (x, z) in posts: p.cham('trim', x - 0.12, x + 0.12, yt + 0.06, yt + hb, z - 0.12, z + 0.12, 0.01)
    runs = [((x0 + 0.25, z1 - 0.12), (-0.12, z1 - 0.12)), ((0.12, z1 - 0.12), (x1 - 0.25, z1 - 0.12)), ((x0 + 0.13, 0.24), (x0 + 0.13, z1 - 0.24)), ((x1 - 0.13, 0.24), (x1 - 0.13, z1 - 0.24))]
    for (a, b) in runs:
        a, b = np.array(a), np.array(b); L = np.linalg.norm(b - a); v = (b - a) / L; nx_ = 1 if abs(v[0]) > 0.5 else 0
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        p.box('trim', lo[0] - 0.08 * (1 - nx_), hi[0] + 0.08 * (1 - nx_), yt + 0.06, yt + 0.16, lo[1] - 0.08 * nx_, hi[1] + 0.08 * nx_)
        p.cham('trim', lo[0] - 0.1 * (1 - nx_), hi[0] + 0.1 * (1 - nx_), yt + hb - 0.1, yt + hb, lo[1] - 0.1 * nx_, hi[1] + 0.1 * nx_, 0.012)
        n = int(L / 0.16)
        for i in range(n):
            c = a + v * (i + 0.5) * L / n
            lathe(p, 'trim', [(0.045, 0.0), (0.04, 0.05), (0.065, 0.25), (0.05, 0.42), (0.03, 0.55), (0.04, 0.63), (0.045, hb - 0.26)], c[0], c[1], yt + 0.16, 10)
    return p
def podium():
    """Patamar de pedra sob o portico (pivo: face da parede, eixo, cota do piso), 5 degraus de 0,15 x 0,3 m e muretas laterais."""
    p = Piece(); x0, x1 = -PXW, PXW
    p.box('stone2', x0, x1, -0.04, 0.0, 0.0, PZ); p.box('plinth', x0 + 0.005, x1 - 0.005, -RAISE, -0.04, 0.003, PZ - 0.005)
    n = 5; rs = RAISE / n
    for i in range(n):
        y = -RAISE + (i + 1) * rs; z0 = PZ + (n - 1 - i) * 0.3
        prof_x(p, 'stone2', x0 + 0.3, x1 - 0.3, [(z0, y - rs - 0.01), (z0 + 0.3, y - rs - 0.01), (z0 + 0.3, y - 0.03), (z0 + 0.32, y - 0.012), (z0 + 0.32, y), (z0, y)])
    for s in (-1, 1):
        a, b = sorted((s * (PXW - 0.3), s * PXW))
        p.hull('stone2', [(x, y, z) for x in (a, b) for (z, y) in ((0.0, -RAISE), (0.0, 0.3), (PZ, 0.3), (PZ + 1.5, -RAISE + 0.15), (PZ + 1.5, -RAISE))])
        p.hull('trim', [(x, y, z) for x in (a - 0.02, b + 0.02) for (z, y) in ((0.0, 0.3), (0.0, 0.36), (PZ, 0.36), (PZ + 1.52, -RAISE + 0.21), (PZ + 1.52, -RAISE + 0.15), (PZ, 0.3))])
    return p
def back_steps():
    """5 degraus de pedra na porta dos fundos (pivo: face da parede, eixo, cota do piso)."""
    p = Piece(); n = 5; rs = RAISE / n; w = 0.8
    p.box('stone2', -w, w, -0.04, 0.0, 0.0, 0.9); p.box('plinth', -w + 0.005, w - 0.005, -RAISE, -0.04, 0.0, 0.895)
    for i in range(n):
        y = -RAISE + (i + 1) * rs; z0 = 0.9 + (n - 1 - i) * 0.3
        prof_x(p, 'stone2', -w, w, [(z0, y - rs - 0.01), (z0 + 0.3, y - rs - 0.01), (z0 + 0.3, y - 0.03), (z0 + 0.32, y - 0.012), (z0 + 0.32, y), (z0, y)])
    return p

# ============================================================================ interior
def floor_tile(fl, holes=(), bath=False, trim=(0, 0, 0, 0)):
    """Piso de 2 x 2 m: tacos (planks) ou ladrilho; no andar de cima, laje com forro de gesso por baixo. holes = retangulos (x0, z0, x1, z1)."""
    p = Piece(); x0, x1, z0, z1 = -W / 2 + T * trim[0], W / 2 - T * trim[1], -W / 2 + T * trim[2], W / 2 - T * trim[3]
    sq = sbox(x0, z0, x1, z1)
    for (a, b, c, d) in holes: sq = sq.difference(sbox(a, b, c, d))
    sqi = sbox(x0 + 0.02 * (1 - trim[0]), z0 + 0.02 * (1 - trim[2]), x1 - 0.02 * (1 - trim[1]), z1 - 0.02 * (1 - trim[3])) if fl > 0 else sbox(-W / 2 + 0.02, -W / 2 + 0.02, W / 2 - 0.02, W / 2 - 0.02)
    for (a, b, c, d) in holes: sqi = sqi.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
    if bath:
        ext_y(p, 'dark', sq, -0.027, -0.004); n = 10; s = W / n
        for i in range(n):
            for j in range(n):
                a0 = -W / 2 + i * s + 0.004; c0 = -W / 2 + j * s + 0.004; a1, c1 = a0 + s - 0.008, c0 + s - 0.008
                a0, a1, c0, c1 = max(a0, x0 + 0.004), min(a1, x1 - 0.004), max(c0, z0 + 0.004), min(c1, z1 - 0.004)
                if a1 - a0 > 0.01 and c1 - c0 > 0.01: p.box('tile', a0, a1, -0.03, 0.0, c0, c1)
    else: ext_y(p, 'floor', sq, -0.03, 0.0)
    if fl > 0: ext_y(p, 'plaster', sqi, -SLAB - 0.005, -0.03)
    else: ext_y(p, 'plinth', sqi, -RAISE + 0.02, -0.03)
    return p
def ceiling_tile():
    p = Piece(); p.box('plaster', -W / 2, W / 2, -0.06, -0.01, -W / 2, W / 2); return p
def interior_wall(doorway, h, ow=0.9, end=False):
    """Parede interna de 0,14 m com rodape (para na porta), guarnicoes e batente. end: termina 0,3 m antes (encontra parede externa)."""
    p = Piece(); t = 0.14; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2] + ([-ow / 2, ow / 2] if doorway else []) + [x1]; ys = [0.0, 2.1, h] if doorway else [0.0, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (doorway and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    if doorway:
        door_casing(p, ow, t)
        for a, b in ((-W / 2, -ow / 2 - 0.09), (ow / 2 + 0.09, x1)): baseboard(p, a, b, t)
    else: baseboard(p, -W / 2, x1, t)
    return p
# escada reta de madeira: 18 espelhos de H/18 e 17 pisos de 0,28 m, sobe para -Z
NR = 18; RS_ = H / NR; TR = 0.28; SW_ = 1.2
SZ0 = 2.4; STX0 = -SX + 4.0 + 0.07   # pe da escada (z) e lado da parede (x = face da parede do hall em x=-3)
def stair():
    """Escada de madeira (pivo: canto do primeiro degrau junto a parede, cota do piso): degraus com bocel, espelhos brancos,
    banzo aparente do lado aberto, corrimao, balaustres finos e pilarete torneado no pe."""
    p = Piece(); w = SW_
    for i in range(NR - 1):
        y = (i + 1) * RS_; z0 = -i * TR
        p.box('floor', 0.0, w, y - 0.035, y, z0 - TR - 0.0, z0 + 0.03)
        p.box('trim', 0.0, w, y - RS_ - 0.002 if i else 0.0, y - 0.035, z0 - 0.02, z0)
    top = (NR - 1) * TR
    p.box('trim', 0.0, w, H - RS_ - 0.002, H - 0.035, -top - 0.02, -top)
    # banzo aparente (lado aberto, x = w) e banzo de parede
    for (a, b) in ((w, w + 0.05), (-0.005, 0.025)):
        p.hull('trim', [(x, y, z) for x in (a, b) for (z, y) in ((0.03, -0.0), (0.03 + 0.25, -0.0), (-top + 0.02, H - RS_ - 0.25), (-top + 0.02, H + 0.08), (0.03, RS_ + 0.08))])
    # corrimao e balaustres do lado aberto
    xr = w + 0.025; k = RS_ / TR
    hr = lambda z: 0.9 + k * (-z)
    seg_cyl(p, 'wood', (xr, hr(0.0) + 0.05, 0.0), (xr, hr(-top) + 0.05, -top), 0.03, 10)
    for i in range(NR - 1):
        z = -i * TR - TR / 2; y = (i + 1) * RS_
        p.box('trim', xr - 0.012, xr + 0.012, y, hr(z) + 0.03, z - 0.012, z + 0.012)
    p.cham('wood', xr - 0.07, xr + 0.07, 0.0, 1.0, -0.1, 0.04, 0.01); lathe(p, 'wood', [(0.06, 1.0), (0.07, 1.06), (0.04, 1.12), (0.0, 1.16)], xr, -0.03, 0.0, 12)
    return p
HOLE = (-3.0, -2.45, -1.6, 1.0)    # buraco da escada na laje de cima (x0, z0, x1, z1), em coordenadas do predio
def stair_rail():
    """Guarda-corpo em volta do buraco da escada no andar de cima (pivo: canto x0, z1 do buraco, cota do piso)."""
    p = Piece(); x0, z0, x1, z1 = HOLE; L1 = z1 - z0; L2 = x1 - x0
    for (a, b, c, d) in ((L2 - 0.03, L2 + 0.03, -L1 + 0.0, 0.03), (0.07, L2 + 0.03, -0.03, 0.03)):
        p.box('wood', a - 0.01, b + 0.01, 0.92, 0.98, c, d)
        p.box('trim', a, b, 0.003, 0.08, c, d)
    for i in range(int(L1 / 0.12)):
        z = -L1 + 0.06 + i * 0.12
        if z < -0.05: p.box('trim', L2 - 0.012, L2 + 0.012, 0.08, 0.92, z - 0.012, z + 0.012)
    for i in range(int((L2 - 0.1) / 0.12)):
        x = 0.13 + i * 0.12
        if x < L2 - 0.06: p.box('trim', x - 0.012, x + 0.012, 0.08, 0.92, -0.012, 0.012)
    p.cham('wood', L2 - 0.05, L2 + 0.05, 0.0015, 1.06, -0.05, 0.05, 0.008)
    return p

# ============================================================================ jardim: gradil, pilares, portao, caminho
FH = 0.45
def fence(L=W):
    """Gradil de 2 m sobre mureta de pedra: barras quadradas a cada 12 cm com pontas de lanca, 2 travessas. Pivo: centro, chao."""
    p = Piece(); a, b = -L / 2, L / 2
    p.box('stone2', a, b, 0.0, FH - 0.06, -0.15, 0.15)
    prof_x(p, 'trim', a, b, crect(-0.18, 0.18, FH - 0.06, FH, 0.012, (1, 1, 1, 1)))
    for yy in (FH + 0.12, FH + 1.0): p.box('iron', a, b, yy - 0.02, yy + 0.02, -0.015, 0.015)
    n = int(round(L / 0.12))
    for i in range(n):
        x = a + (i + 0.5) * L / n
        p.box('iron', x - 0.01, x + 0.01, FH, FH + 1.12, -0.01, 0.01)
        p.hull('iron', [(x + dx, FH + 1.12, z) for dx in (-0.022, 0.022) for z in (-0.012, 0.012)] + [(x, FH + 1.24, 0.0)])
    return p
def pier(h=1.75):
    p = Piece(); a = 0.25
    p.cham('stone2', -a, a, 0.0, h, -a, a, 0.008)
    p.cham('trim', -a - 0.05, a + 0.05, h, h + 0.08, -a - 0.05, a + 0.05, 0.012); p.cham('trim', -a - 0.02, a + 0.02, h + 0.08, h + 0.13, -a - 0.02, a + 0.02, 0.01)
    lathe(p, 'trim', [(0.09, 0.0), (0.06, 0.06), (0.14, 0.18), (0.13, 0.26), (0.06, 0.34), (0.0, 0.37)], 0.0, 0.0, h + 0.13, 14)
    return p
GTW = 2.0
def gate_leaf(w=GTW / 2 - 0.03):
    """Folha do portao de ferro: quadro, barras com lancas, arco no alto e volutas simples. Pivo: dobradica, chao; fecha ao longo de +X."""
    p = Piece(); h0 = 0.1; h1 = 1.5
    for (a, b) in ((0.0, 0.04), (w - 0.04, w)): p.box('iron', a, b, h0, h1 + 0.1, -0.02, 0.02)
    for yy in (h0 + 0.02, 0.5, h1): p.box('iron', 0.04, w - 0.04, yy - 0.02, yy + 0.02, -0.018, 0.018)
    n = 7
    for i in range(n):
        x = 0.04 + (i + 0.5) * (w - 0.08) / n; top = h1 + 0.05 + 0.25 * (x / w)
        p.box('iron', x - 0.01, x + 0.01, h0, top, -0.01, 0.01)
        p.hull('iron', [(x + dx, top, z) for dx in (-0.022, 0.022) for z in (-0.012, 0.012)] + [(x, top + 0.12, 0.0)])
    for k in range(10):
        a0 = math.pi * k / 10; a1 = math.pi * (k + 1) / 10; r = 0.12
        for (cx, cy) in ((w * 0.3, 0.75), (w * 0.7, 0.75)):
            seg_cyl(p, 'iron', (cx + r * math.cos(a0), cy + r * math.sin(a0) * 1.2, 0.0), (cx + r * math.cos(a1), cy + r * math.sin(a1) * 1.2, 0.0), 0.01, 6)
    return p
def path_slab(L=W, w=1.6):
    p = Piece(); n = int(round(L / 0.5))
    for i in range(n):
        z0 = -L / 2 + i * L / n + 0.006; p.cham('stone2', -w / 2, w / 2, -0.02, 0.03, z0, z0 + L / n - 0.012, 0.008)
    return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p

# ============================================================================ pecas
FB = [-6, -4, -2, 0, 2, 4, 6]; SB = [-4, -2, 0, 2, 4]
def roof_name(kind, u): return f'roof_{kind}_{abs(u)}' + ('_l' if u < 0 else '')
GUT_Y = YE - KR * OVER + 0.02 - 0.12
CH_H = YE + KR * (AZR - OVER) + 0.4
pieces = {'g_wall_window': g_wall('window'), 'g_wall_plain': g_wall('plain'), 'g_wall_door': g_wall('door'), 'g_wall_back_door': g_wall('back_door'),
          'u_wall_window': u_wall('window'), 'u_wall_window_plain': u_wall('window', shutters=False), 'u_wall_plain': u_wall('plain'), 'u_wall_balcony': u_wall('balcony'),
          'corner_ground': corner_q('ground'), 'corner_upper': corner_q('upper'), 'hip_cap': hip_cap(), 'ridge_cap': ridge_cap(-2.0, 2.0), 'pediment': pediment(), 'dormer': dormer(), 'chimney': chimney(CH_H),
          'downspout': downspout(RAISE + GUT_Y, OVER + 0.095), 'column': column(H - 0.42 + 0.0), 'balcony': balcony(), 'podium': podium(), 'back_steps': back_steps(),
          'floor_tile': floor_tile(1), 'floor_tile_ground': floor_tile(0), 'floor_tile_bath': floor_tile(1, bath=True), 'ceiling_tile': ceiling_tile(),
          'stair': stair(), 'stair_rail': stair_rail(),
          'door_leaf_front': None, 'door_leaf_back': door_back(0.92, 2.3), 'door_leaf_interior': door_interior(),
          'door_leaf_balcony': None, 'fence': fence(), 'fence_pier': pier(), 'gate_leaf': gate_leaf(), 'path_slab': path_slab(), 'wall_lantern': wall_lantern(), 'porch_lantern': porch_lantern(),
          'player_scale_ref': player_ref()}
for fl in (0, 1):
    h = H0 - 0.005 if fl == 0 else H
    for nm, args in (('plain', (False,)), ('doorway', (True,))):
        pieces[f'iw{fl}_{nm}'] = interior_wall(args[0], h); pieces[f'iw{fl}_end_{nm}'] = interior_wall(args[0], h, end=True)
def door_panel(w=0.6, h=2.32, t=0.05):
    """Folha da porta principal: vidro alto com grade de ferro e 2 almofadas em baixo (Blender). Pivo: dobradica, embaixo."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2); a, b = 0.11, w - 0.11
    cut = [tbox(a, b, 1.42, h - 0.14, -t, t)] + [tbox(a, b, y0, y1, z - 0.01, z + 0.01) for (y0, y1) in ((0.16, 0.6), (0.72, 1.28)) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', a - 0.004, b + 0.004, 1.416, h - 0.136, -0.004, 0.004)
    for i in range(1, 4): xx = a + (b - a) * i / 4; p.box('iron', xx - 0.008, xx + 0.008, 1.42, h - 0.14, t / 2 - 0.01, t / 2 + 0.004)
    for yy in (1.42 + (h - 1.56) / 3, 1.42 + 2 * (h - 1.56) / 3): p.box('iron', a, b, yy - 0.008, yy + 0.008, t / 2 - 0.01, t / 2 + 0.004)
    p.add('door', bl_detail(tbox(0.05, w - 0.05, 1.32, 1.38, -t / 2 - 0.02, t / 2 + 0.02), bevel=0.006, segments=2))
    for z in (1, -1):
        p.cham('brass', w - 0.1, w - 0.05, 0.9, 1.12, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.sphere('brass', 0.03, w - 0.075, 1.02, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.075, 1.02, z * t / 2), (w - 0.075, 1.02, z * (t / 2 + 0.04)), 0.016)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
pieces['door_leaf_front'] = door_panel()
def door_glazed(w=0.6, h=2.15, t=0.045):
    """Folha envidracada da sacada: quadro, almofada embaixo, 3 vidros com baguetes. Pivo: dobradica, embaixo."""
    p = Piece(); s = 0.08
    p.cham('frame', 0.0, s, 0.0, h, -t / 2, t / 2, 0.006); p.cham('frame', w - s, w, 0.0, h, -t / 2, t / 2, 0.006)
    p.cham('frame', s - 0.002, w - s + 0.002, 0.0, 0.5, -t / 2, t / 2, 0.006); p.cham('frame', s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.006)
    p.cham('frame', s + 0.04, w - s - 0.04, 0.1, 0.4, -t / 2 - 0.008, t / 2 + 0.008, 0.008)
    p.box('glass', s - 0.004, w - s + 0.004, 0.496, h - s + 0.004, -0.003, 0.003)
    for i in (1, 2):
        yy = 0.5 + (h - s - 0.5) * i / 3; p.cham('frame', s, w - s, yy - 0.013, yy + 0.013, -0.012, 0.012, 0.004)
    for z in (1, -1): p.seg('brass', (w - 0.05, 1.05, z * t / 2), (w - 0.05, 1.05, z * (t / 2 + 0.04)), 0.014)
    return p
pieces['door_leaf_balcony'] = door_glazed()
for u in FB:
    ext_ = 0.035 if u == 6 else -0.035 if u == -6 else 0
    pieces.setdefault(roof_name('main', u), roof_strip(AXR, AZR, u, -W / 2 - (OVER if u == -6 else 0), W / 2 + (OVER if u == 6 else 0), fascia_ext=ext_))
for u in SB:
    ext_ = 0
    pieces.setdefault(roof_name('hip', u), roof_strip(AZR, AXR, u, -W / 2 - (OVER if u == -4 else 0), W / 2 + (OVER if u == 4 else 0), fascia_ext=ext_))
# pisos com o buraco da escada (andar de cima)
HOLE_T = {}
for cx in FB:
    for cz in SB:
        r = sbox(cx - 1, cz - 1, cx + 1, cz + 1).intersection(sbox(HOLE[0], HOLE[1], HOLE[2], HOLE[3]))
        if r.area > 1e-6:
            b = r.bounds; HOLE_T[(cx, cz)] = f'floor_tile_hole_{len(HOLE_T) + 1}'
            pieces[HOLE_T[(cx, cz)]] = floor_tile(1, [(b[0] - cx, b[1] - cz, b[2] - cx, b[3] - cz)])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)

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
GWn, GPn, GDn, GBn = 'g_wall_window', 'g_wall_plain', 'g_wall_door', 'g_wall_back_door'
UWn, UNn, UPn, UBn = 'u_wall_window', 'u_wall_window_plain', 'u_wall_plain', 'u_wall_balcony'
G0 = {'front': {-6: GWn, -4: GWn, -2: GWn, 0: GDn, 2: GWn, 4: GWn, 6: GWn},
      'back': {-6: GWn, -4: GWn, -2: GPn, 0: GBn, 2: GWn, 4: GWn, 6: GWn},
      'left': {4: GWn, 2: GWn, 0: GPn, -2: GWn, -4: GWn},
      'right': {4: GWn, 2: GWn, 0: GPn, -2: GWn, -4: GWn}}
G1 = {'front': {-6: UNn, -4: UWn, -2: UWn, 0: UBn, 2: UWn, 4: UWn, 6: UNn},
      'back': {-6: UNn, -4: UWn, -2: UWn, 0: UWn, 2: UWn, 4: UWn, 6: UNn},
      'left': {4: UNn, 2: UWn, 0: UPn, -2: UWn, -4: UNn},
      'right': {4: UNn, 2: UWn, 0: UPn, -2: UWn, -4: UNn}}
for ry, bays, f, tag in faces:
    for u in bays:
        x, z = f(u); wk = x if tag in ('front', 'back') else z
        put(G0[tag][wk], x, lvl(0), z, ry, [tag, 'ext', ftag(0)])
        put(G1[tag][wk], x, lvl(1), z, ry, [tag, 'ext', ftag(1)])
        put(roof_name('main' if tag in ('front', 'back') else 'hip', u), x, lvl(0), z, ry, [tag, 'roof'])
for ry, x, z, tg in [(0, SX, SZ, ('front', 'right')), (90, SX, -SZ, ('right', 'back')), (180, -SX, -SZ, ('back', 'left')), (-90, -SX, SZ, ('left', 'front'))]:
    put('corner_ground', x, lvl(0), z, ry, tg + ('ext', ftag(0))); put('corner_upper', x, lvl(1), z, ry, tg + ('ext', ftag(1))); put('hip_cap', x, lvl(0), z, ry, tg + ('roof',))
put('ridge_cap', 0, lvl(0), 0, 0, ['roof'])
put('pediment', 0, lvl(0), SZ, 0, ['front', 'roof'])
for x in (-4.0, 4.0): put('dormer', x, lvl(0), SZ, 0, ['front', 'roof'])
put('dormer', 0.0, lvl(0), -SZ, 180, ['back', 'roof'])
for x in (-4.5, 4.5): put('chimney', x, lvl(0), -1.6, 0, ['roof'])
for x, z, ry, tg in ((6.5, SZ, 0, 'front'), (-6.5, SZ, 0, 'front'), (6.5, -SZ, 180, 'back'), (-6.5, -SZ, 180, 'back')):
    put('downspout', x, 0, z, ry, [tg, 'ext'])
# portico e sacada
put('podium', 0, lvl(0), SZ, 0, ['front', 'porch'])
for s in (-1, 1): put('column', s * COLX, lvl(0), SZ + COLZ, 0, ['front', 'porch'])
put('balcony', 0, lvl(1), SZ, 0, ['front', 'porch', ftag(1)])
put('back_steps', 0, lvl(0), -SZ, 180, ['back', 'ext'])
put('porch_lantern', 0, lvl(1) - 0.42, SZ + 0.85, 0, ['front', 'porch'])
put('wall_lantern', 1.05, lvl(0) + 1.9, -SZ - 0.04, 180, ['back', 'ext'])
# portas externas (folha direita girada 180, abre com -85)
hx, hz = hinge(0, SZ, 0, -0.6, -0.15); put('door_leaf_front', hx, lvl(0) + 0.013, hz, 0, ['front', 'ext', ftag(0)], door=85)
hx, hz = hinge(0, SZ, 0, 0.6, -0.15); put('door_leaf_front', hx, lvl(0) + 0.013, hz, 180, ['front', 'ext', ftag(0)], door=-85)
hx, hz = hinge(0, -SZ, 180, -0.46, -0.15); put('door_leaf_back', hx, lvl(0) + 0.013, hz, 180, ['back', 'ext', ftag(0)], door=85)
hx, hz = hinge(0, SZ, 0, -0.58, -0.15); put('door_leaf_balcony', hx, lvl(1) + 0.013, hz, 0, ['front', 'ext', ftag(1)], door=85)
hx, hz = hinge(0, SZ, 0, 0.58, -0.15); put('door_leaf_balcony', hx, lvl(1) + 0.013, hz, 180, ['front', 'ext', ftag(1)], door=-85)
# pisos, forros, escada
BATH = {(4, -4), (6, -4), (4, -2), (6, -2)}; NEW_TILES = []
for a in FB:
    for b in SB:
        put('floor_tile_ground', a, lvl(0), b, 0, [ftag(0)])
        tr = (a == FB[0], a == FB[-1], b == SB[0], b == SB[-1]); nm = HOLE_T.get((a, b), 'floor_tile_bath' if (a, b) in BATH else 'floor_tile')
        if any(tr):
            nm2 = nm + '_e' + ''.join('1' if t else '0' for t in tr)
            if nm2 not in pieces:
                pieces[nm2] = floor_tile(1, bath=nm == 'floor_tile_bath', trim=tuple(int(t) for t in tr)); NEW_TILES.append(nm2)
            nm = nm2
        put(nm, a, lvl(1), b, 0, [ftag(1)])
        put('ceiling_tile', a, lvl(1) + H, b, 0, ['roof', 'ceiling'])
put('stair', STX0, lvl(0), SZ0, 0, [ftag(0)])
put('stair_rail', HOLE[0], lvl(1), HOLE[3], 0, [ftag(1)])
MX0, MX1, MZ0, MZ1 = -SX, SX, -SZ, SZ
def wl(fl, x0, z0, x1, z1, doors=()):
    """Paredes internas: modulos de 2 m na linha; as pontas que encostam nas paredes externas usam a versao 'end'."""
    y = lvl(fl); pre = f'iw{fl}_'
    if z0 == z1:
        cs = list(range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2))
        for c in cs:
            end = c in (cs[0], cs[-1]) and (c - 1 == MX0 or c + 1 == MX1); d = c in doors
            ry = 0 if c + 1 == MX1 or not end else 180
            put(pre + ('end_' if end else '') + ('doorway' if d else 'plain'), c, y, z0, ry, [ftag(fl)])
            if d: hx, hz = hinge(c, z0, 0, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, 0, [ftag(fl)], door=75)
    else:
        cs = list(range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2))
        for c in cs:
            end = (c - 1 == MZ0) or (c + 1 == MZ1); d = c in doors
            ry = (90 if c - 1 == MZ0 else -90) if end else 90
            put(pre + ('end_' if end else '') + ('doorway' if d else 'plain'), x0, y, c, ry, [ftag(fl)])
            if d:
                hry = ry if end else 90
                hx, hz = hinge(x0, c, hry, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, hry, [ftag(fl)], door=75)
for fl in (0, 1):
    wl(fl, -3.0, MZ0, -3.0, MZ1, doors=(4, -4)); wl(fl, 3.0, MZ0, 3.0, MZ1, doors=(2, -2))
    wl(fl, MX0, -1.0, -3.0, -1.0); wl(fl, 3.0, -1.0, MX1, -1.0)
# jardim: gradil em volta (x -9..9, z -8..10), portao no eixo da frente
GX, GZ0, GZ1 = 9.0, -8.0, 10.0
for x in (2, 4, 6, 8, -2, -4, -6, -8): put('fence', x, 0, GZ1, 0, ['garden', 'front'])
for x in range(-8, 9, 2): put('fence', x, 0, GZ0, 0, ['garden', 'back'])
for z in range(-7, 10, 2):
    put('fence', GX, 0, z, 90, ['garden', 'right']); put('fence', -GX, 0, z, 90, ['garden', 'left'])
for (x, z) in ((GX, GZ1), (-GX, GZ1), (GX, GZ0), (-GX, GZ0), (1.0 + 0.24, GZ1), (-1.0 - 0.24, GZ1)): put('fence_pier', x, 0, z, 0, ['garden'])
for s, ry, op in ((-1, 0, -80), (1, 180, 80)):
    put('gate_leaf', s * 1.0, 0.02, GZ1, ry, ['garden', 'front'], door=op)
ZP0 = SZ + PZ + 1.5      # fim dos degraus do portico
pieces['path_slab'] = path_slab(GZ1 - 0.18 - ZP0)
put('path_slab', 0.0, 0.0, ZP0 + (GZ1 - 0.18 - ZP0) / 2, 0, ['garden'])
put('player_scale_ref', 2.5, 0, 11.2); put('player_scale_ref', 0.6, lvl(0), SZ + 1.0, 0, ['porch']); put('player_scale_ref', 5, lvl(0), 2, 0, [ftag(0)])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    for n in ['path_slab'] + NEW_TILES: fn = f'{OUT}/pieces/{n}.glb'; pieces[n].scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    json.dump({'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE, 'footprint': [2 * SX, 2 * SZ],
                        'garden': {'x': [-GX, GX], 'z': [GZ0, GZ1]}, 'stair_hole': HOLE,
                        'roof': 'hipped, 35 deg, slate courses in geometry, ridge along X (x in [-2,2]) at z=0, eave overhang 0.55 m; pediment and dormers on top',
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
