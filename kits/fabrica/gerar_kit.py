"""Kit 29: fabrica europeia de tijolo, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Galpao de 20 x 16 m com cobertura em dente de serra (4 dentes de 4 m, vidracas verticais voltadas para a frente, calhas de
zinco nos vales), estrutura de aco aparente (pilares, vigas de vale, tesouras inclinadas, tercas), paredes de tijolo com
pilastras, janelas altas em arco abatido com caixilho de aco de muitos vidros, cachorrada de tijolo e capa de pedra.
Portao de carga em arco pleno com 2 folhas de tabuas e bandeira em leque, portas de servico nas laterais e nos fundos.
Escritorio de 10 x 8 m e 3 andares na frente do galpao: tijolo, janelas de guilhotina com vergas de pedra e fecho,
faixa entre andares, platibanda com cachorrada, escada de 2 lances, salas, porta para o galpao, caixa d'agua de madeira
no terraco. Fora: 2 chamines redondas de 24 m, muro do patio com pilares e portao de ferro, luminarias pescoco de ganso.
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
configurar(cores={'brick': (150, 66, 50), 'brick2': (108, 44, 36), 'trim': (226, 218, 198), 'plinth': (124, 120, 112), 'coping': (202, 196, 182),
                  'plaster': (238, 232, 220), 'floor': (150, 106, 70), 'concrete': (164, 160, 152), 'marble': (232, 228, 218), 'slate': (64, 66, 68),
                  'membrane': (92, 94, 96), 'seam': (78, 80, 82), 'frame': (238, 236, 228), 'sash': (238, 236, 228), 'wframe': (46, 60, 56),
                  'steel': (88, 96, 100), 'iron': (30, 32, 34), 'roofsheet': (82, 86, 90), 'zinc': (146, 150, 152), 'door': (40, 62, 52),
                  'door_int': (222, 216, 200), 'gatewood': (122, 46, 38), 'wood': (96, 60, 38), 'tank': (118, 84, 56), 'enamel': (44, 74, 64),
                  'grate': (60, 62, 64)},
           texturas={'brick': 'brick', 'brick2': 'brick', 'trim': 'render', 'plinth': 'stone', 'plaster': 'plaster', 'floor': 'planks',
                     'concrete': 'render', 'membrane': 'render', 'marble': 'plaster', 'gatewood': 'planks', 'wood': 'planks', 'tank': 'planks'},
           out=OUT)
MATS = D.MATS; TEX = D.TEX

W = 2.0; T = 0.3; H = 3.2; SLAB = 0.25; RAISE = 0.3
H0 = H - SLAB
def lvl(fl): return RAISE + fl * H
YR = lvl(3); PAR = 1.0                         # terraco do escritorio e altura da platibanda
PL = 0.45                                      # topo do embasamento de pedra (escritorio)
PLH = 0.5                                      # topo do embasamento do galpao
# galpao: x de -10 a 10, z de -10 a 6; 4 dentes de serra de 4 m (sobem para +Z), vale a V do piso, crista a V + 2
HX = 10.0; HZ0 = -10.0; HZ1 = 6.0; V = 5.7; RISE = 2.0; TEETH = (-10.0, -6.0, -2.0, 2.0)
BT = V + 0.5; FT = V + RISE + 0.5              # topo da parede dos fundos e da frente (platibanda acima da cobertura)
PW = 0.18                                      # meia pilastra em cada ponta dos modulos do galpao
def yu(z): return V + z * RISE / 4.0           # face de baixo da telha, z medido a partir do vale do dente

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
def mitre_cut(m, keep_x_le_z=True):
    n = [-1, 0, 1] if keep_x_le_z else [1, 0, -1]; n = np.array(n) / math.sqrt(2)
    return slice_keep(m, [0, 0, 0], n)
def mitred(p, mat, prof, Ln=0.5):
    """Perfil (z, y) que dobra a quina externa (pivo na quina, paredes em -X e -Z): duas metades cortadas em meia-esquadria."""
    for keep in (True, False):
        q = Piece()
        if keep: prof_x(q, mat, 0.0, Ln, prof)
        else: prof_z(q, mat, 0.0, Ln, prof)
        p.add(mat, mitre_cut(q.parts[mat][0], keep))
def sloped(p, mat, xa, xb, za, zb, f, d0, d1):
    """Barra inclinada (convexa) de xa a xb e de za a zb, entre f(z) + d0 e f(z) + d1."""
    p.hull(mat, [(x, f(z) + d, z) for x in (xa, xb) for z in (za, zb) for d in (d0, d1)])

# ---------- arcos ----------
def arch_geom(w, ys, rise):
    R = (w * w / 4 + rise * rise) / (2 * rise); return R, ys + rise - R
def opening(w, sill, ys, rise, x=0.0):
    """Vao com verga em arco (abatido, ou pleno quando rise = w / 2): retangulo ate ys e segmento de circulo acima."""
    R, cy = arch_geom(w, ys, rise)
    top = Point(x, cy).buffer(R, 48).intersection(sbox(x - w / 2, ys - 0.001, x + w / 2, ys + rise + 0.01))
    return unary_union([sbox(x - w / 2, sill, x + w / 2, ys), top]).buffer(0)
def voussoirs(p, mat, w, ys, rise, d=0.22, x=0.0, z0=0.0, z1=0.02, key=None, gap=0.007, bw=0.12):
    """Aduelas radiais em volta do arco (junta de 7 mm); 'key' = material do fecho central, mais alto e saliente."""
    R, cy = arch_geom(w, ys, rise); a0 = math.atan2(ys - cy, w / 2); a1 = math.pi - a0
    n = max(5, int(round(R * (a1 - a0) / bw))); n += (n % 2 == 0); da = gap / 2 / R
    for i in range(n):
        aa = a0 + (a1 - a0) * i / n + (da if i else 0.0); bb = a0 + (a1 - a0) * (i + 1) / n - (da if i < n - 1 else 0.0)
        k = key is not None and i == n // 2
        Ro = R + d + (0.09 if k else 0.0)
        pts = [(x + R * math.cos(a), cy + R * math.sin(a)) for a in np.linspace(aa, bb, 3)] + [(x + Ro * math.cos(a), cy + Ro * math.sin(a)) for a in np.linspace(bb, aa, 3)]
        ext(p, key if k else mat, Polygon(pts), z0, z1 + (0.03 if k else 0.0))
def steel_window(p, op, zf=-0.1, dx=0.3, dy=0.3, fw=0.05, mat='wframe'):
    """Caixilho de aco de muitos vidros no vao 'op' (poligono): quadro, montantes e travessas finos e vidro no meio."""
    inner = op.buffer(-fw, join_style=2)
    ext(p, mat, op.difference(inner), zf - 0.06, zf)
    b0, b1, b2, b3 = inner.bounds; bars = []
    nx = max(1, int(round((b2 - b0) / dx))); ny = max(1, int(round((b3 - b1) / dy)))
    for i in range(1, nx): xx = b0 + (b2 - b0) * i / nx; bars.append(sbox(xx - 0.012, b1 - 0.01, xx + 0.012, b3 + 0.01))
    for j in range(1, ny): yy = b1 + (b3 - b1) * j / ny; bars.append(sbox(b0 - 0.01, yy - 0.012, b2 + 0.01, yy + 0.012))
    if bars: ext(p, mat, unary_union(bars).intersection(inner), zf - 0.045, zf - 0.015)
    ext(p, 'glass', inner, zf - 0.032, zf - 0.028)
def fan_window(p, cx, cy, R, zf=-0.1, n=7, mat='wframe'):
    """Bandeira em leque (meio circulo acima de cy): quadro em arco, raios e cubo."""
    half = Point(cx, cy).buffer(R, 48).intersection(sbox(cx - R, cy, cx + R, cy + R))
    inner = Point(cx, cy).buffer(R - 0.05, 48).intersection(sbox(cx - R, cy + 0.04, cx + R, cy + R))
    ext(p, mat, half.difference(inner), zf - 0.06, zf); bars = [Point(cx, cy).buffer(0.22, 24).difference(Point(cx, cy).buffer(0.18, 24))]
    for k in range(1, n):
        a = math.pi * k / n; c, s = math.cos(a), math.sin(a)
        bars.append(Polygon([(cx + 0.012 * s, cy - 0.012 * c), (cx + R * c + 0.012 * s, cy + R * s - 0.012 * c), (cx + R * c - 0.012 * s, cy + R * s + 0.012 * c), (cx - 0.012 * s, cy + 0.012 * c)]))
    ext(p, mat, unary_union(bars).intersection(inner), zf - 0.045, zf - 0.015)
    ext(p, 'glass', inner, zf - 0.032, zf - 0.028)

# ============================================================================ galpao: paredes de tijolo com pilastras
HWIN = (1.2, 1.2, 4.1, 0.35); CLERE = (1.0, 5.95, 6.95, 0.22); HDOOR = (1.1, 0.0, 2.45, 0.25); GATE = (3.2, 0.0, 3.2, 1.6)
COPE = lambda yt: [(-T - 0.05, yt), (0.15, yt), (0.15, yt + 0.03), (0.12, yt + 0.06), (-T - 0.02, yt + 0.06), (-T - 0.05, yt + 0.03)]
def corbel(p, xa, xb, yt):
    """Cachorrada de tijolo sob a capa: 2 fiadas escalonadas, denticulos e friso, de xa a xb (pivo: face da parede)."""
    prof_x(p, 'brick2', xa, xb, crect(0.0, 0.035, yt - 0.62, yt - 0.54, 0.006, (0, 1, 1, 0)))
    n = int((xb - xa) / 0.125)
    for i in range(n): xx = xa + (i + 0.5) * (xb - xa) / n; p.box('brick2', xx - 0.03, xx + 0.03, yt - 0.54, yt - 0.44, -0.01, 0.06)
    prof_x(p, 'brick2', xa, xb, crect(0.0, 0.075, yt - 0.44, yt - 0.36, 0.006, (0, 1, 1, 0)))
    prof_x(p, 'brick', xa, xb, [(0.0, yt - 0.36), (0.1, yt - 0.36), (0.1, yt), (0.0, yt)])
def stone_sill(p, ow, oy0, ext_=0.1):
    x = ow / 2 + ext_
    prof_x(p, 'trim', -x, x, [(-0.06, oy0 - 0.08), (0.06, oy0 - 0.08), (0.075, oy0 - 0.065), (0.075, oy0 - 0.025), (0.065, oy0 - 0.01), (-0.06, oy0 + 0.02)])
def hall_wall(kind='window', ya=BT, yb=BT, w=W, level=True, clere=False):
    """Modulo de parede do galpao (pivo: face externa no centro, cota do piso). level: topo reto com cachorrada e capa
    (frente e fundos); senao o topo segue a cobertura (ya na ponta -X, yb na ponta +X) com uma faixa inclinada de tijolo escuro."""
    p = Piece(); x0, x1 = -w / 2, w / 2
    ta, tb = (ya - 0.06, yb - 0.06) if level else (ya - 0.003, yb - 0.003)
    outline = Polygon([(x0, -RAISE), (x1, -RAISE), (x1, tb), (x0, ta)])
    ops = []; gaps = []
    if kind == 'window': ops.append(('w', opening(*HWIN)))
    if kind == 'door': ops.append(('d', opening(*HDOOR))); gaps.append((-0.55, 0.55))
    if kind == 'gate': ops.append(('g', opening(*GATE))); gaps.append((-1.6, 1.6))
    if clere:
        for xc in ((-1.0, 1.0) if w > 2.5 else (0.0,)): ops.append(('c', opening(CLERE[0], CLERE[1], CLERE[2], CLERE[3], xc)))
    hole = unary_union([o for _, o in ops]) if ops else None
    ext(p, 'brick', outline.difference(hole) if hole else outline, -T, 0.0)
    pil = unary_union([sbox(x0, PLH, x0 + PW, 99), sbox(x1 - PW, PLH, x1, 99)]).intersection(outline)
    ext(p, 'brick', pil, -0.01, 0.1)
    xs = [x0] + [v for g in gaps for v in g] + [x1]
    for i in range(0, len(xs) - 1, 2):
        if xs[i + 1] - xs[i] > 0.01: prof_x(p, 'plinth', xs[i], xs[i + 1], crect(0.0, 0.04, -RAISE, PLH, 0.012, (0, 0, 1, 0)))
    for (a, b) in ((x0, x0 + PW + 0.02), (x1 - PW - 0.02, x1)): prof_x(p, 'plinth', a, b, crect(0.0, 0.13, -RAISE, PLH, 0.015, (0, 0, 1, 0)))
    if level:
        corbel(p, x0 + PW, x1 - PW, ta); prof_x(p, 'coping', x0, x1, COPE(ta))
    else:
        xa, xb = x0 + PW, x1 - PW; f = lambda x: ta + (tb - ta) * (x - x0) / (x1 - x0)
        ext(p, 'brick2', Polygon([(xa, f(xa) - 0.32), (xb, f(xb) - 0.32), (xb, f(xb) - 0.06), (xa, f(xa) - 0.06)]), -0.01, 0.03)
    for k, op in ops:
        if k == 'w':
            w_, s_, ys, r_ = HWIN; voussoirs(p, 'brick2', w_, ys, r_, key='trim'); stone_sill(p, w_, s_); steel_window(p, op)
            p.box('brick2', -w_ / 2 - 0.02, w_ / 2 + 0.02, s_ - 0.02, s_ + 0.015, -T - 0.03, -T + 0.12)      # peitoril interno de tijolo
        if k == 'c':
            w_, s_, ys, r_ = CLERE; xc = op.centroid.x if w > 2.5 else 0.0
            voussoirs(p, 'brick2', w_, ys, r_, x=xc, d=0.2); steel_window(p, op, dx=0.34)
            prof_x(p, 'trim', xc - w_ / 2 - 0.08, xc + w_ / 2 + 0.08, [(-0.06, s_ - 0.07), (0.06, s_ - 0.07), (0.07, s_ - 0.055), (0.07, s_ - 0.02), (-0.06, s_ + 0.015)])
        if k == 'd':
            w_, s_, ys, r_ = HDOOR; x = w_ / 2
            voussoirs(p, 'brick2', w_, ys, r_, key='trim')
            prof_x(p, 'trim', -x, x, [(-0.295, 0.012), (0.04, 0.012), (0.06, 0.0), (0.06, -0.045), (-0.295, -0.045)])
            p.box('wframe', -x, -x + 0.06, 0.0, ys, -0.2, -0.1); p.box('wframe', x - 0.06, x, 0.0, ys, -0.2, -0.1)
            p.box('wframe', -x + 0.06, x - 0.06, 2.37, ys, -0.2, -0.1)
            steel_window(p, op.intersection(sbox(-x, ys, x, ys + 1)), zf=-0.1, dx=0.28)
        if k == 'g':
            w_, s_, ys, r_ = GATE; x = w_ / 2
            voussoirs(p, 'brick2', w_, ys, r_, d=0.2, bw=0.14)
            p.hull('trim', [(sx * 0.13, y, z) for sx in (-1, 1) for y in (ys + r_ - 0.03, ys + r_ + 0.32) for z in (0.0, 0.07)] + [(sx * 0.17, ys + r_ + 0.32, z) for sx in (-1, 1) for z in (0.0, 0.07)])
            for s in (-1, 1):
                a, b = sorted((s * x, s * (x + 0.2))); p.cham('trim', a, b, ys - 0.18, ys + 0.02, 0.0, 0.06, 0.008)    # impostas de pedra
            prof_x(p, 'trim', -x, x, [(-0.295, 0.012), (0.06, 0.012), (0.08, 0.0), (0.08, -0.045), (-0.295, -0.045)])
            p.box('wframe', -x, x, ys - 0.17, ys, -0.2, -0.08)                                     # verga de aco das folhas
            fan_window(p, 0.0, ys, x, zf=-0.1, n=9)
            for s in (-1, 1):
                for yy in (0.5, 1.6, 2.7): p.cyl('iron', 0.02, yy - 0.08, yy + 0.08, s * (x - 0.01), -0.19, 8)   # pinos das dobradicas
    return p

def pier(top):
    """Pilar de canto do galpao (pivo: quina externa, cota do piso; paredes em -X e -Z): tijolo, base de pedra, cimalha e capa."""
    p = Piece(); a, b = -0.38, 0.17
    p.box('brick', a, b, -RAISE + 0.003, top - 0.3, a, b)
    p.cham('plinth', a - 0.03, b + 0.03, -RAISE + 0.004, PLH + 0.04, a - 0.03, b + 0.03, 0.015)
    p.cham('brick2', a - 0.03, b + 0.03, top - 0.3, top - 0.08, a - 0.03, b + 0.03, 0.01)
    p.cham('coping', a - 0.06, b + 0.06, top - 0.08, top, a - 0.06, b + 0.06, 0.012)
    return p

# ============================================================================ galpao: cobertura em dente de serra e estrutura de aco
def roof_tooth(glaze=True):
    """Modulo de 2 m de um dente (pivo: eixo do modulo no vale, cota do piso): telha de aco com nervuras, tercas, calha de zinco
    no vale e, na crista, a vidraca vertical com montantes, travessas e rufo."""
    p = Piece(); z0, z1 = 0.15, 4.0
    p.hull('roofsheet', [(x, yu(z) + d, z) for x in (-1.0, 1.0) for z in (z0, z1) for d in (0.0, 0.025)])
    for i in range(8):
        xr = -0.875 + 0.25 * i
        p.hull('roofsheet', [(xr + s * hw, yu(z) + 0.02 + dy, z) for z in (z0, z1) for (hw, dy) in ((0.03, 0.0), (0.015, 0.035)) for s in (-1, 1)])
    for zc in (0.6, 1.4, 2.2, 3.0, 3.7): p.seg('steel', (-0.998, yu(zc) - 0.075, zc), (0.998, yu(zc) - 0.075, zc), 0.06, 0.15)
    p.box('zinc', -1.0, 1.0, V - 0.25, V - 0.23, 0.01, 0.42); p.box('zinc', -1.0, 1.0, V - 0.25, V + 0.02, 0.01, 0.03)
    p.box('zinc', -1.0, 1.0, V - 0.25, V + 0.08, 0.4, 0.42)
    if glaze:
        g0 = V + 0.06; g1 = V + RISE - 0.04
        p.box('wframe', -1.0, 1.0, V - 0.02, g0, 3.92, 3.995)
        for xm in (-0.5, 0.0, 0.5): p.box('wframe', xm - 0.02, xm + 0.02, g0, g1, 3.92, 3.995)
        for xm in (-1.0, 1.0): a, b = sorted((xm, xm - 0.02 * xm)); p.box('wframe', a, b, g0, g1, 3.92, 3.995)
        for yy in (V + 0.7, V + 1.35): p.box('wframe', -1.0, 1.0, yy - 0.015, yy + 0.015, 3.93, 3.99)
        p.box('glass', -0.98, 0.98, g0, g1, 3.955, 3.96)
        p.box('zinc', -1.0, 1.0, V + RISE + 0.06, V + RISE + 0.09, 3.82, 4.06); p.box('zinc', -1.0, 1.0, V + RISE - 0.1, V + RISE + 0.09, 4.0, 4.04)
    return p
def ibeam(p, mat, x0, x1, ytop, d, zc, bf=0.2):
    p.box(mat, x0, x1, ytop - 0.02, ytop, zc - bf / 2, zc + bf / 2); p.box(mat, x0, x1, ytop - d, ytop - d + 0.02, zc - bf / 2, zc + bf / 2)
    p.box(mat, x0, x1, ytop - d + 0.02, ytop - 0.02, zc - 0.008, zc + 0.008)
def girder():
    """Viga de vale de 20 m (pivo: centro, cota do piso), perfil I de 50 cm com enrijecedores a cada 2 m; pontas na parede."""
    p = Piece(); top = V - 0.26; d = 0.5
    ibeam(p, 'steel', -HX + 0.15, HX - 0.15, top, d, 0.0)
    for xx in np.arange(-HX + 1.0, HX - 0.5, 2.0): p.box('steel', xx - 0.006, xx + 0.006, top - d + 0.02, top - 0.02, -0.095, 0.095)
    return p
def column():
    """Pilar de aco (pivo: centro, piso): perfil H com chapa de base chumbada, capitel e maos-francesas sob a viga."""
    p = Piece(); top = V - 0.76
    p.box('steel', -0.1, 0.1, 0.02, top, -0.1, -0.08); p.box('steel', -0.1, 0.1, 0.02, top, 0.08, 0.1); p.box('steel', -0.008, 0.008, 0.02, top, -0.08, 0.08)
    p.cham('steel', -0.22, 0.22, 0.0, 0.025, -0.22, 0.22, 0.004)
    for sx in (-1, 1):
        for sz in (-1, 1): p.cyl('iron', 0.016, 0.025, 0.06, sx * 0.16, sz * 0.16, 6)
    p.box('steel', -0.14, 0.14, top - 0.02, top, -0.14, 0.14)
    for s in (-1, 1): p.hull('steel', [(s * x, y, z) for z in (-0.006, 0.006) for (x, y) in ((0.1, top - 0.8), (0.1, top - 0.02), (0.7, top - 0.02))])
    return p
def rafter(end=False):
    """Tesoura inclinada em perfil I sob as tercas (pivo: eixo no vale, piso); na crista, montante que segura a vidraca."""
    p = Piece(); f = lambda z: yu(z) - 0.15; za, zb = 0.45, (3.62 if end else 3.85)
    sloped(p, 'steel', -0.075, 0.075, za, zb, f, -0.02, 0.0); sloped(p, 'steel', -0.075, 0.075, za, zb, f, -0.3, -0.28)
    sloped(p, 'steel', -0.007, 0.007, za, zb, f, -0.28, -0.02)
    p.box('steel', -0.075, 0.075, f(za) - 0.3 - 0.0, f(za) + 0.0, za - 0.02, za)
    p.box('steel', -0.04, 0.04, V - 0.26, f(za) - 0.3, za - 0.05, za + 0.05)
    if not end:
        p.box('steel', -0.075, 0.075, V - 0.04, V + RISE - 0.002, 3.85, 3.9); p.box('steel', -0.008, 0.008, V - 0.04, V + RISE - 0.002, 3.9, 3.99)
    return p
def verge(s, glaze=True, outlet=True):
    """Arremate da lateral (x = s * 10, pivo no eixo do galpao no vale, piso): capa e testeira de zinco seguindo a agua,
    tampa da ponta da parede ao lado da vidraca, bocal da calha, funil e condutor ate o chao."""
    p = Piece(); a, b = sorted((s * 9.82, s * 10.2)); z0, z1 = 0.1, 4.0
    sloped(p, 'zinc', a, b, z0, z1 + 0.06, yu, 0.06, 0.085)
    c, d = sorted((s * 10.17, s * 10.2)); sloped(p, 'zinc', c, d, z0, z1 + 0.06, yu, -0.25, 0.085)
    if glaze:
        e, f = sorted((s * 9.69, s * 10.2)); p.box('zinc', e, f, V, V + RISE + 0.085, z1, z1 + 0.025)
    if outlet:
        e, f = sorted((s * 9.6, s * 10.16)); p.box('zinc', e, f, V - 0.25, V - 0.15, 0.14, 0.3)
        e, f = sorted((s * 10.12, s * 10.42)); p.box('zinc', e, f, V - 0.6, V - 0.1, 0.05, 0.45)
        p.box('dark', e + 0.02, f - 0.02, V - 0.1, V - 0.095, 0.07, 0.43)
        p.hull('zinc', [(s * xx, y, zz) for (xx, y) in ((10.14, V - 0.6), (10.4, V - 0.6), (10.2, V - 0.82), (10.3, V - 0.82)) for zz in (0.18, 0.32)])
        xp = s * 10.25; p.cyl('zinc', 0.05, -RAISE + 0.18, V - 0.8, xp, 0.25, 12)
        p.hull('zinc', [(xp + s * dx, y, 0.25 + dz) for (dx, y) in ((-0.05, -RAISE + 0.25), (0.05, -RAISE + 0.25), (0.05, -RAISE + 0.12), (0.25, -RAISE + 0.02), (0.25, -RAISE + 0.1)) for dz in (-0.05, 0.05)])
        for yy in np.arange(0.6, V - 1.2, 1.4):
            p.box('zinc', xp - 0.06, xp + 0.06, yy, yy + 0.04, 0.19, 0.31); e, f = sorted((s * 10.0, s * 10.2)); p.box('zinc', e, f, yy + 0.005, yy + 0.035, 0.24, 0.26)
    return p
def pendant():
    """Luminaria industrial pendurada na viga (pivo: face de baixo da viga): haste, cupula de esmalte e lampada."""
    p = Piece(); L1 = 1.6
    p.box('steel', -0.04, 0.04, -0.015, 0.0, -0.04, 0.04); p.cyl('iron', 0.008, -L1, -0.015, 0.0, 0.0, 6)
    p.cyl('enamel', 0.05, -L1 - 0.08, -L1, 0.0, 0.0, 12)
    lathe(p, 'enamel', [(0.05, -L1 - 0.08), (0.12, -L1 - 0.16), (0.24, -L1 - 0.3), (0.26, -L1 - 0.33)], sec=16)
    p.sphere('lamp_glass', 0.07, 0.0, -L1 - 0.2, 0.0)
    return p
def gooseneck(arm=0.55):
    """Luminaria pescoco de ganso (pivo: face da parede, base): espelho, braco curvo, cupula de esmalte e lampada."""
    p = Piece(); p.cham('iron', -0.07, 0.07, -0.1, 0.1, 0.0, 0.02, 0.005)
    pts = [(0.0, 0.03)] + [(0.3 * math.sin(a), 0.03 + 0.3 * (1 - math.cos(a))) for a in np.linspace(0, math.pi / 2, 6)[1:]] + [(0.3, arm)]
    for (ya, za), (yb, zb) in zip(pts[:-1], pts[1:]): seg_cyl(p, 'iron', (0.0, ya, za), (0.0, yb, zb), 0.016, 8)
    yb, zc = 0.3, arm
    lathe(p, 'enamel', [(0.03, yb + 0.04), (0.1, yb - 0.04), (0.2, yb - 0.13), (0.22, yb - 0.16)], z=zc, sec=16)
    p.sphere('lamp_glass', 0.06, 0.0, yb - 0.08, zc)
    return p

# ============================================================================ escritorio
OWIN = (1.0, 0.9, 2.2, 0.22); ODOOR = (1.1, 0.0, 2.4, 0.2)
BELT = [(0.0, -0.25), (0.05, -0.25), (0.05, -0.2), (0.065, -0.185), (0.065, -0.05), (0.08, -0.04), (0.09, -0.01), (0.09, 0.03), (0.07, 0.05), (0.0, 0.08)]
def sill_course(y):
    return [(0.0, y - 0.11), (0.05, y - 0.11), (0.06, y - 0.1), (0.075, y - 0.08), (0.075, y - 0.03), (0.065, y - 0.01), (0.0, y + 0.004)]
def sash_window(p, ow, oy0, oy1, zf=-0.04, lites=2):
    """Caixilho branco recuado, 2 folhas de guilhotina, batente e peitoril interno."""
    x = ow / 2; f = 0.06; y0 = oy0 + 0.032
    p.box('frame', -x, -x + f, y0, oy1, zf - 0.16, zf); p.box('frame', x - f, x, y0, oy1, zf - 0.16, zf)
    p.box('frame', -x + f, x - f, oy1 - f, oy1, zf - 0.16, zf); p.box('frame', -x + f, x - f, y0, y0 + 0.04, zf - 0.16, zf)
    p.box('frame', -x + f, -x + f + 0.012, y0 + 0.04, oy1 - f, zf - 0.065, zf - 0.055); p.box('frame', x - f - 0.012, x - f, y0 + 0.04, oy1 - f, zf - 0.065, zf - 0.055)
    mid = (y0 + 0.04 + oy1 - f) / 2
    sash(p, -x + f, x - f, y0 + 0.04, mid + 0.02, zf - 0.11, zf - 0.07, 1, 0.075)
    sash(p, -x + f + 0.012, x - f - 0.012, mid - 0.02, oy1 - f, zf - 0.05, zf - 0.01, lites, 0.05)
    p.box('trim', -x - 0.05, x + 0.05, oy0, oy0 + 0.022, -T - 0.04, zf - 0.16)
def o_wall(kind='window', fl=1):
    """Modulo de 2 m do escritorio (pivo: face externa, cota do piso): tijolo, gesso por dentro, janela de guilhotina com
    bandeira em arco, verga de aduelas de pedra com fecho e peitoril; embasamento no terreo, faixa no 1o andar e peitoril corrido no 2o."""
    p = Piece(); y0 = -RAISE if fl == 0 else -SLAB
    op = None
    if kind == 'window': op = opening(*OWIN)
    if kind == 'door': op = opening(*ODOOR)
    if kind == 'door_in': op = sbox(-0.5, 0.0, 0.5, 2.2)
    out = sbox(-W / 2, y0, W / 2, H0); inn = sbox(-W / 2, y0, W / 2, H0 - 0.005)
    ext(p, 'brick', out.difference(op) if op else out, -T + 0.02, 0.0)
    ext(p, 'plaster', inn.difference(op) if op else inn, -T, -T + 0.02)
    if fl == 0:
        gaps = [(-0.62, 0.62)] if kind in ('door', 'door_in') else []
        xs = [-W / 2] + [v for g in gaps for v in g] + [W / 2]
        for i in range(0, len(xs) - 1, 2): prof_x(p, 'plinth', xs[i], xs[i + 1], crect(0.0, 0.03, -RAISE, PL, 0.01, (0, 0, 1, 0)))
    if fl == 1: prof_x(p, 'trim', -W / 2, W / 2, BELT)
    if fl == 2: prof_x(p, 'trim', -W / 2, W / 2, sill_course(OWIN[1]))
    if kind == 'window':
        w_, s_, ys, r_ = OWIN; sash_window(p, w_, s_, ys)
        seg = op.intersection(sbox(-w_ / 2, ys, w_ / 2, ys + 1)); inner = seg.buffer(-0.05, join_style=2)
        ext(p, 'frame', seg.difference(inner), -0.2, -0.04); ext(p, 'glass', inner, -0.122, -0.118)
        voussoirs(p, 'trim', w_, ys, r_, d=0.2, key='trim', bw=0.13)
        if fl != 2: stone_sill(p, w_, s_)
        else: prof_x(p, 'trim', -w_ / 2, w_ / 2, [(-0.2, s_ - 0.07), (0.0, s_ - 0.07), (0.0, s_ + 0.004), (-0.2, s_ + 0.03)])
    if kind == 'door':
        w_, s_, ys, r_ = ODOOR; x = w_ / 2
        prof_x(p, 'trim', -x, x, [(-0.295, 0.012), (0.06, 0.012), (0.08, 0.0), (0.08, -0.045), (-0.295, -0.045)])
        p.box('frame', -x, -x + 0.07, 0.0, ys, -0.2, -0.1); p.box('frame', x - 0.07, x, 0.0, ys, -0.2, -0.1); p.box('frame', -x + 0.07, x - 0.07, 2.32, ys, -0.21, -0.09)
        seg = op.intersection(sbox(-x, ys, x, ys + 1)); inner = seg.buffer(-0.05, join_style=2)
        ext(p, 'frame', seg.difference(inner), -0.2, -0.1); ext(p, 'glass', inner, -0.152, -0.148)
        voussoirs(p, 'trim', w_, ys, r_, d=0.2, key='trim', bw=0.13)
        for s in (-1, 1):       # ombreiras de pedra em blocos alternados
            for k in range(5):
                ya, yb = PL + k * 0.4 + 0.004, PL + (k + 1) * 0.4 - 0.004; ww = 0.3 if k % 2 == 0 else 0.2
                a, b = sorted((s * x, s * (x + ww))); p.cham('trim', a, b, ya, yb, 0.0, 0.035, 0.006)
    if kind == 'door_in':
        prof_x(p, 'trim', -0.5, 0.5, [(-0.295, 0.012), (0.04, 0.012), (0.06, 0.0), (0.06, -0.045), (-0.295, -0.045)])
        p.box('wframe', -0.5, -0.44, 0.0, 2.2, -0.2, -0.1); p.box('wframe', 0.44, 0.5, 0.0, 2.2, -0.2, -0.1); p.box('wframe', -0.44, 0.44, 2.14, 2.2, -0.2, -0.1)
        p.cham('trim', -0.68, 0.68, 2.2, 2.45, 0.0, 0.04, 0.008)
    return p
def o_parapet():
    """Platibanda do escritorio (pivo: face externa, cota do terraco): faixa de pedra, tijolo, cachorrada e capa."""
    p = Piece(); top = PAR
    ext(p, 'brick', sbox(-W / 2, -SLAB, W / 2, top - 0.06), -T + 0.02, 0.0); ext(p, 'plaster', sbox(-W / 2, -SLAB, W / 2, -0.03), -T, -T + 0.02); ext(p, 'brick', sbox(-W / 2, -0.03, W / 2, top - 0.06), -T, -T + 0.02)
    prof_x(p, 'trim', -W / 2, W / 2, crect(0.0, 0.05, -0.06, 0.08, 0.008, (0, 1, 1, 0)))
    corbel(p, -W / 2, W / 2, top - 0.06); prof_x(p, 'coping', -W / 2, W / 2, COPE(top - 0.06))
    return p
def o_corner(fl, pil=True):
    """Quina do escritorio (pivo: quina externa, cota do piso; paredes em -X e -Z): nucleo, pilastra de tijolo em L e
    embasamento, faixa ou peitoril corrido dobrando a quina; fl = 3 e a platibanda."""
    p = Piece(); e = 0.004; y0 = -RAISE if fl == 0 else -SLAB; top = H0 if fl < 3 else PAR - 0.06
    p.box('brick', -T + 0.004, e, y0 + 0.003, top - 0.004, -T + 0.004, e)
    if pil:
        ya = PL if fl == 0 else y0 + 0.003; yb = top - (0.62 if fl == 3 else 0.004)
        p.cham('brick', -0.45, 0.06, ya, yb, -0.01, 0.06, 0.006); p.cham('brick', -0.01, 0.06, ya, yb, -0.45, -0.01, 0.006)
    if fl == 0 and pil:
        p.cham('plinth', -0.5, 0.08, -RAISE + 0.004, PL + 0.02, -0.01, 0.08, 0.01); p.cham('plinth', -0.01, 0.08, -RAISE + 0.004, PL + 0.02, -0.5, -0.01, 0.01)
    if fl == 1: mitred(p, 'trim', BELT)
    if fl == 2 and pil: mitred(p, 'trim', sill_course(OWIN[1]))
    if fl == 3:
        mitred(p, 'trim', crect(0.0, 0.05, -0.06, 0.08, 0.008, (0, 1, 1, 0)))
        yt = PAR - 0.06
        for pr in (crect(0.0, 0.035, yt - 0.62, yt - 0.54, 0.006, (0, 1, 1, 0)), crect(0.0, 0.075, yt - 0.44, yt - 0.36, 0.006, (0, 1, 1, 0)), [(0.0, yt - 0.36), (0.1, yt - 0.36), (0.1, yt), (0.0, yt)]):
            mitred(p, 'brick2' if pr[0][1] < yt - 0.37 else 'brick', pr)
        p.box('brick2', -0.03, 0.06, yt - 0.54, yt - 0.44, -0.03, 0.06)
        mitred(p, 'coping', COPE(yt))
    return p

# ============================================================================ escada, guarda-corpos, paredes internas, pisos, portas
NR = 18; RS_ = H / NR; TR = 0.28; SW_ = 1.1; RUN = (NR - 1) * TR
LA = (-9.7, -8.6); LB = (-8.3, -7.2); ZA = 12.7; ZB = ZA - RUN
def stair(both=False):
    """Lance reto de madeira (pivo: canto do primeiro degrau, cota do piso), sobe para -Z: pisos com bocel, espelhos,
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
def rail(Ln, posts=(True, True)):
    p = Piece()
    p.box('trim', 0.0, Ln, 0.003, 0.08, -0.03, 0.03); p.box('wood', 0.0, Ln, 0.92, 0.98, -0.04, 0.04)
    n = int(Ln / 0.12)
    for i in range(1, n):
        x = i * Ln / n; p.box('trim', x - 0.012, x + 0.012, 0.08, 0.92, -0.012, 0.012)
    for x, ok in zip((0.0, Ln), posts):
        if ok: p.cham('wood', x - 0.04, x + 0.04, 0.0015, 1.06, -0.04, 0.04, 0.008)
    return p
def interior_wall(doorway, h, ow=0.9, end=False):
    p = Piece(); t = 0.14; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2] + ([-ow / 2, ow / 2] if doorway else []) + [x1]; ys = [0.0, 2.1, h] if doorway else [0.0, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (doorway and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    if doorway:
        door_casing(p, ow, t)
        for a, b in ((-W / 2, -ow / 2 - 0.09), (ow / 2 + 0.09, x1)): baseboard(p, a, b, t)
    else: baseboard(p, -W / 2, x1, t)
    return p
def floor_tile(kind, lv, rect=(-1, 1, -1, 1), holes=(), trim=(0, 0, 0, 0)):
    """Piso: tacos, xadrez de marmore, concreto com juntas serradas (galpao) ou manta (terraco). lv 'g' = terreo (base ate
    o chao), 'u' = andar e 'r' = terraco (laje com forro de gesso por baixo). trim: para na face interna das paredes."""
    p = Piece(); x0, x1, z0, z1 = rect[0] + T * trim[0], rect[1] - T * trim[1], rect[2] + T * trim[2], rect[3] - T * trim[3]
    sq = sbox(x0, z0, x1, z1)
    for (a, b, c, d) in holes: sq = sq.difference(sbox(a, b, c, d))
    if kind == 'marble':
        s = 0.5
        for i in range(4):
            for j in range(4):
                q = sbox(rect[0] + i * s, rect[2] + j * s, rect[0] + (i + 1) * s, rect[2] + (j + 1) * s).intersection(sq)
                ext_y(p, 'marble' if (i + j) % 2 == 0 else 'slate', q, -0.03, 0.0)
    elif kind == 'membrane':
        ext_y(p, 'membrane', sq, -0.03, 0.0)
        for (a, b, c, d) in ((-0.02, rect[2] + 0.02, 0.02, rect[3] - 0.02), (rect[0] + 0.02, -0.02, rect[1] - 0.02, 0.02)):
            ext_y(p, 'seam', sbox(a, b, c, d).intersection(sbox(x0 + 0.01, z0 + 0.01, x1 - 0.01, z1 - 0.01)), 0.0, 0.004)
    elif kind == 'hall':
        ext_y(p, 'concrete', sq, -0.03, 0.0)
        for q in (sbox(rect[0], z0, rect[0] + 0.008, z1), sbox(x0, rect[2], x1, rect[2] + 0.008), sbox(-0.004, z0, 0.004, z1), sbox(x0, -0.004, x1, 0.004)):
            if not ((q.bounds[0] == rect[0] and trim[0]) or (q.bounds[1] == rect[2] and trim[2])): ext_y(p, 'seam', q.intersection(sq), 0.0, 0.002)
    else: ext_y(p, 'floor', sq, -0.03, 0.0)
    if lv == 'g':
        ext_y(p, 'plinth', sbox(rect[0] + 0.02, rect[2] + 0.02, rect[1] - 0.02, rect[3] - 0.02), -RAISE + 0.02, -0.03)
    else:
        sqi = sbox(x0 + 0.02 * (1 - trim[0]), z0 + 0.02 * (1 - trim[2]), x1 - 0.02 * (1 - trim[1]), z1 - 0.02 * (1 - trim[3]))
        for (a, b, c, d) in holes: sqi = sqi.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
        ext_y(p, 'plaster', sqi, -SLAB - 0.005, -0.03)
    return p
def door_double(w=0.94, h=2.3, t=0.055):
    """Folha da porta do escritorio: vidro alto com grade, 2 almofadas embaixo, puxador de latao. Pivo: dobradica, embaixo."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2); a, b = 0.12, w - 0.12
    cut = [tbox(a, b, 1.25, h - 0.14, -t, t)] + [tbox(a, b, y0, y1, z - 0.01, z + 0.01) for (y0, y1) in ((0.16, 0.55), (0.66, 1.1)) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', a - 0.004, b + 0.004, 1.246, h - 0.136, -0.004, 0.004)
    for sz in (1, -1):
        z0, z1 = sorted((sz * (t / 2 - 0.01), sz * (t / 2 + 0.004)))
        for i in range(1, 3): xx = a + (b - a) * i / 3; p.box('iron', xx - 0.008, xx + 0.008, 1.25, h - 0.14, z0, z1)
        yy = 1.25 + (h - 1.39) / 2; p.box('iron', a, b, yy - 0.008, yy + 0.008, z0, z1)
    p.add('door', bl_detail(tbox(0.05, w - 0.05, 1.16, 1.21, -t / 2 - 0.02, t / 2 + 0.02), bevel=0.006, segments=2))
    for z in (1, -1):
        p.cyl('brass', 0.012, 0.85, 1.35, w - 0.09, z * (t / 2 + 0.05), 10)
        for yy in (0.88, 1.32): p.seg('brass', (w - 0.09, yy, z * t / 2), (w - 0.09, yy, z * (t / 2 + 0.05)), 0.01)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def gate_leaf(w=1.59, h=3.02):
    """Folha do portao de carga (pivo: dobradica, embaixo): tabuas verticais com junta, forro, travessas e mao-francesa
    por dentro, ferragens de ferro (dobradicas compridas e argola) por fora."""
    p = Piece(); n = int(round(w / 0.16))
    p.box('gatewood', 0.0, w, 0.0, h, -0.04, 0.0)
    for i in range(n): p.box('gatewood', i * w / n + 0.003, (i + 1) * w / n - 0.003, 0.0, h, 0.0, 0.035)
    for yy in (0.15, h / 2, h - 0.25): p.box('gatewood', 0.05, w - 0.05, yy - 0.09, yy + 0.09, -0.075, -0.04)
    for (ya, yb) in ((0.24, h / 2 - 0.09), (h / 2 + 0.09, h - 0.34)):
        p.hull('gatewood', [(x, y, z) for (x, y) in ((0.12, ya), (0.24, ya), (w - 0.12, yb), (w - 0.24, yb)) for z in (-0.07, -0.04)])
    for yy in (0.5, 1.6, 2.7):
        p.box('iron', 0.0, 1.1, yy - 0.035, yy + 0.035, 0.035, 0.045); p.hull('iron', [(1.1, yy - 0.035, 0.035), (1.1, yy + 0.035, 0.035), (1.18, yy, 0.035), (1.1, yy - 0.035, 0.045), (1.1, yy + 0.035, 0.045), (1.18, yy, 0.045)])
        for xx in (0.15, 0.45, 0.8): p.sphere('iron', 0.016, xx, yy, 0.047)
        p.cyl('iron', 0.022, yy - 0.08, yy + 0.08, 0.0, -0.02, 8)
    p.cham('iron', w - 0.2, w - 0.1, 1.2, 1.32, 0.035, 0.05, 0.004)
    q = Piece(); lathe(q, 'iron', [(0.07, -0.006), (0.07, 0.006)], sec=14)
    M = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]); M[:3, 3] = [w - 0.15, 1.12, 0.07]; p.merge(q, M)
    return p
def iron_gate(w=1.73, h=1.75):
    """Folha do portao de ferro do patio (pivo: dobradica, embaixo): quadro, barras com lancas, travessas e voluta."""
    p = Piece()
    for (ya, yb) in ((0.08, 0.14), (0.85, 0.89), (h - 0.3, h - 0.25)): p.box('iron', 0.0, w, ya, yb, -0.02, 0.02)
    p.box('iron', 0.0, 0.05, 0.08, h - 0.15, -0.025, 0.025); p.box('iron', w - 0.04, w, 0.08, h - 0.25, -0.02, 0.02)
    n = int(w / 0.12)
    for i in range(1, n):
        xx = i * w / n; tip = h + (0.12 if i % 2 else 0.0)
        seg_cyl(p, 'iron', (xx, 0.14, 0.0), (xx, tip - 0.1, 0.0), 0.011, 8)
        p.hull('iron', [(xx + dx, tip - 0.1, dz) for dx in (-0.025, 0.025) for dz in (-0.012, 0.012)] + [(xx, tip, 0.0)])
    for k in range(3):
        cx = w * (k + 0.5) / 3; R = 0.12
        ring = Point(cx, 0.5).buffer(R, 24).difference(Point(cx, 0.5).buffer(R - 0.02, 24)); q = Piece(); ext(q, 'iron', ring, -0.01, 0.01); p.merge(q)
    p.cyl('iron', 0.03, 0.2, 0.3, 0.0, 0.0, 8); p.cyl('iron', 0.03, h - 0.5, h - 0.4, 0.0, 0.0, 8)
    return p

# ============================================================================ fora: degraus, rampa, chamine, muro, caixa d'agua
def steps(w=0.8, d=0.8, n=2):
    """Patamar e degraus de pedra (pivo: face da parede, eixo, cota do piso; descem para +Z ate o chao)."""
    p = Piece(); r = RAISE / n
    p.box('trim', -w, w, -0.04, 0.0, 0.0, d); p.box('plinth', -w + 0.005, w - 0.005, -RAISE + 0.002, -0.04, 0.0, d - 0.005)
    for i in range(n - 1, 0, -1):
        y = -RAISE + i * r; z0 = d + (n - 1 - i) * 0.3
        prof_x(p, 'trim', -w, w, [(z0, y - r - 0.0 + 0.002), (z0 + 0.3, y - r + 0.002), (z0 + 0.3, y - 0.03), (z0 + 0.32, y - 0.012), (z0 + 0.32, y), (z0, y)])
    return p
def ramp(w=1.9, d=2.2):
    """Rampa de concreto do portao (pivo: face da parede, eixo, cota do piso) com cantoneira de aco na borda."""
    p = Piece()
    p.hull('concrete', [(x, y, z) for x in (-w, w) for (z, y) in ((0.0, 0.0), (0.0, -RAISE + 0.002), (d, -RAISE + 0.002), (d, -RAISE + 0.02))])
    for s in (-1, 1): p.hull('steel', [(s * w + s * dx, y, z) for dx in (0.0, 0.006) for (z, y) in ((0.0, 0.0), (0.0, -0.05), (d, -RAISE + 0.002), (d, -RAISE + 0.02))])
    return p
def chimney(h=24.0):
    """Chamine redonda de tijolo (pivo: centro, chao): base quadrada com almofadas, cimalha de pedra, fuste conico com
    cintas de ferro, 2 aneis de pedra, coroa de tijolo em balanco, boca escura, escada de grampos e para-raios."""
    p = Piece(); B = 1.3; y1 = 4.0; r0, r1 = 1.0, 0.62; yc = h - 1.3
    rr = lambda y: r0 + (r1 - r0) * (y - y1) / (yc - y1)
    p.cham('plinth', -B - 0.06, B + 0.06, 0.003, 0.6, -B - 0.06, B + 0.06, 0.02)
    p.box('brick', -B, B, 0.6, y1 - 0.4, -B, B)
    for ry in range(4):
        q = Piece(); prof_y(q, 'brick2', 0.9, y1 - 0.75, crect(-0.8, 0.8, B - 0.01, B + 0.03, 0.006, (0, 0, 1, 1)))
        M = trimesh.transformations.rotation_matrix(math.radians(90 * ry), [0, 1, 0]); p.merge(q, M)
    p.cham('trim', -B - 0.12, B + 0.12, y1 - 0.4, y1 - 0.25, -B - 0.12, B + 0.12, 0.02); p.cham('trim', -B - 0.05, B + 0.05, y1 - 0.25, y1 - 0.05, -B - 0.05, B + 0.05, 0.015)
    lathe(p, 'brick', [(r0 + 0.05, y1 - 0.1), (r0, y1 + 0.1), (r1, yc)], sec=24)
    for (ya, yb) in ((12.0, 12.45), (18.0, 18.45)): lathe(p, 'trim', [(rr(ya) + 0.06, ya), (rr(yb) + 0.06, yb)], sec=24)
    for yy in np.arange(6.0, yc - 0.6, 2.5):
        if not any(a - 0.2 < yy < b + 0.2 for (a, b) in ((12.0, 12.45), (18.0, 18.45))): lathe(p, 'iron', [(rr(yy) + 0.012, yy), (rr(yy + 0.06) + 0.012, yy + 0.06)], sec=24)
    lathe(p, 'brick2', [(r1, yc - 0.01), (r1 + 0.08, yc + 0.25), (r1 + 0.15, yc + 0.5), (r1 + 0.15, h - 0.25), (r1 + 0.2, h - 0.15), (r1 + 0.2, h)], sec=24)
    lathe(p, 'iron', [(r1 + 0.21, h - 0.12), (r1 + 0.21, h + 0.02)], sec=24)
    p.cyl('dark', r1 - 0.08, h - 0.02, h + 0.006, 0.0, 0.0, 24)
    p.cyl('zinc', 0.012, h, h + 1.6, r1 + 0.05, 0.0, 6); p.sphere('zinc', 0.03, r1 + 0.05, h + 1.6, 0.0)
    for yy in np.arange(y1 + 0.4, yc - 0.3, 0.35):                      # grampos da escada no lado +X
        r = rr(yy)
        for dz in (-0.2, 0.2): seg_cyl(p, 'iron', (r - 0.02, yy, dz), (r + 0.14, yy, dz), 0.01, 6)
        seg_cyl(p, 'iron', (r + 0.14, yy, -0.2), (r + 0.14, yy, 0.2), 0.012, 6)
    return p
def yard_wall(y0=0.003):
    """Muro do patio (modulo de 2 m, pivo: centro, chao): embasamento de pedra, tijolo, friso escuro e capa de pedra."""
    p = Piece(); t = 0.15
    prof_x(p, 'plinth', -1.0, 1.0, [(-t - 0.03, y0), (t + 0.03, y0), (t + 0.03, 0.32), (t, 0.35), (-t, 0.35), (-t - 0.03, 0.32)])
    p.box('brick', -1.0, 1.0, 0.35, 1.3, -t, t)
    for s in (-1, 1): a, b = sorted((s * t, s * (t + 0.02))); p.box('brick2', -1.0, 1.0, 1.12, 1.2, a, b)
    prof_x(p, 'coping', -1.0, 1.0, [(-t - 0.05, 1.3), (t + 0.05, 1.3), (t + 0.05, 1.34), (0.0, 1.42), (-t - 0.05, 1.34)])
    return p
def yard_pier():
    p = Piece(); a = 0.25
    p.cham('plinth', -a - 0.04, a + 0.04, 0.006, 0.42, -a - 0.04, a + 0.04, 0.012)
    p.box('brick', -a, a, 0.42, 1.72, -a, a)
    p.cham('brick2', -a - 0.03, a + 0.03, 1.55, 1.72, -a - 0.03, a + 0.03, 0.008)
    p.cham('coping', -a - 0.06, a + 0.06, 1.72, 1.82, -a - 0.06, a + 0.06, 0.012)
    p.hull('coping', [(sx * 0.2, 1.82, sz * 0.2) for sx in (-1, 1) for sz in (-1, 1)] + [(0.0, 1.95, 0.0)])
    p.sphere('coping', 0.11, 0.0, 2.04, 0.0, 2)
    return p
def water_tank():
    """Caixa d'agua de madeira sobre torre de aco (pivo: centro, cota do terraco): pes, contraventamento, estrado,
    aduelas com cintas de ferro, tampa conica e escada."""
    p = Piece(); a = 0.85; Hp = 1.6; R = 1.1; ht = 2.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.cham('steel', sx * a - 0.12, sx * a + 0.12, 0.0, 0.02, sz * a - 0.12, sz * a + 0.12, 0.004)
            p.box('steel', sx * a - 0.05, sx * a + 0.05, 0.02, Hp, sz * a - 0.05, sz * a + 0.05)
    for s in (-1, 1):
        seg_cyl(p, 'steel', (-a, 0.2, s * a), (a, Hp - 0.2, s * a), 0.015, 6); seg_cyl(p, 'steel', (a, 0.2, s * a), (-a, Hp - 0.2, s * a), 0.015, 6)
        seg_cyl(p, 'steel', (s * a, 0.2, -a), (s * a, Hp - 0.2, a), 0.015, 6); seg_cyl(p, 'steel', (s * a, 0.2, a), (s * a, Hp - 0.2, -a), 0.015, 6)
    for s in (-1, 1): p.box('steel', -a - 0.1, a + 0.1, Hp, Hp + 0.12, s * a - 0.05, s * a + 0.05)
    for i in range(9): zz = -1.2 + i * 0.3 + 0.01; p.box('wood', -1.25, 1.25, Hp + 0.12, Hp + 0.16, zz, zz + 0.28)
    n = 26; y0 = Hp + 0.16
    for i in range(n):
        q = Piece(); ww = 2 * math.pi * R / n - 0.008; q.box('tank', R - 0.06, R, y0, y0 + ht, -ww / 2, ww / 2)
        p.merge(q, trimesh.transformations.rotation_matrix(2 * math.pi * i / n, [0, 1, 0]))
    p.cyl('tank', R - 0.055, y0, y0 + 0.08, 0.0, 0.0, 26)
    for yy in (0.25, 0.8, 1.35, 1.8): lathe(p, 'iron', [(R + 0.012, y0 + yy), (R + 0.012, y0 + yy + 0.05)], sec=26)
    lathe(p, 'roofsheet', [(R + 0.1, y0 + ht), (R + 0.1, y0 + ht + 0.05), (0.12, y0 + ht + 0.7), (0.0, y0 + ht + 0.72)], sec=26)
    p.cyl('zinc', 0.06, y0 + ht + 0.7, y0 + ht + 0.85, 0.0, 0.0, 10); p.sphere('zinc', 0.07, 0.0, y0 + ht + 0.9, 0.0)
    for dz in (-0.2, 0.2): p.box('steel', R + 0.16, R + 0.19, 0.0, y0 + ht + 0.3, dz - 0.02, dz + 0.02)
    for yy in np.arange(0.3, y0 + ht + 0.2, 0.3): seg_cyl(p, 'steel', (R + 0.175, yy, -0.2), (R + 0.175, yy, 0.2), 0.012, 6)
    for dz in (-0.2, 0.2): p.box('steel', R - 0.0, R + 0.16, y0 + 0.6, y0 + 0.64, dz - 0.015, dz + 0.015)
    return p
def vent():
    p = Piece(); p.cham('membrane', -0.18, 0.18, 0.0, 0.06, -0.18, 0.18, 0.02); p.cyl('steel', 0.06, 0.06, 0.55, 0.0, 0.0, 12)
    p.cyl('steel', 0.13, 0.55, 0.6, 0.0, 0.0, 14); p.hull('steel', [(0.13 * math.cos(a), 0.6, 0.13 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)] + [(0, 0.68, 0)])
    return p
def drain():
    p = Piece(); p.cyl('seam', 0.16, 0.0, 0.012, 0.0, 0.0, 16); p.hull('grate', [(0.1 * math.cos(a), 0.012, 0.1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)] + [(0, 0.09, 0)])
    return p
def path_slab(Lz, w=2.0):
    p = Piece(); n = max(1, int(round(Lz / 0.6)))
    for i in range(n):
        z0 = -Lz / 2 + i * Lz / n + 0.006
        for k in range(2): p.cham('concrete', -w / 2 + k * w / 2 + 0.006, -w / 2 + (k + 1) * w / 2 - 0.006, -0.02, 0.03, z0, z0 + Lz / n - 0.012, 0.008)
    return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p

# ============================================================================ pecas
pieces = {
    'h_back_window': hall_wall('window', BT, BT), 'h_back_door': hall_wall('door', BT, BT),
    'h_front_window': hall_wall('window', FT, FT, clere=True), 'h_front_gate': hall_wall('gate', FT, FT, w=4.0, clere=True),
    'h_pier_low': pier(BT + 0.12), 'h_pier_high': pier(FT + 0.12),
    'roof_tooth': roof_tooth(), 'roof_tooth_end': roof_tooth(False), 'rafter': rafter(), 'rafter_end': rafter(True),
    'girder': girder(), 'column': column(), 'pendant': pendant(), 'gooseneck': gooseneck(),
    'gate_leaf': gate_leaf(h=3.0), 'door_leaf_side': door_back(0.96, 2.36), 'hall_steps': steps(), 'gate_ramp': ramp(),
    'o_g_window': o_wall('window', 0), 'o_g_plain': o_wall('plain', 0), 'o_g_door': o_wall('door', 0), 'o_g_door_in': o_wall('door_in', 0),
    'o_u1_window': o_wall('window', 1), 'o_u1_plain': o_wall('plain', 1), 'o_u2_window': o_wall('window', 2), 'o_u2_plain': o_wall('plain', 2),
    'o_parapet': o_parapet(),
    'o_corner_g': o_corner(0), 'o_corner_u1': o_corner(1), 'o_corner_u2': o_corner(2), 'o_corner_p': o_corner(3),
    'o_corner_back_g': o_corner(0, False), 'o_corner_back_u1': o_corner(1, False), 'o_corner_back_u2': o_corner(2, False), 'o_corner_back_p': o_corner(3, False),
    'o_steps': steps(0.9, 0.9), 'door_leaf_front': door_double(), 'door_leaf_hall': door_back(0.94, 2.15), 'door_leaf_interior': door_interior(),
    'wall_lantern': wall_lantern(), 'stair': stair(), 'stair_both': stair(True), 'water_tank': water_tank(), 'vent': vent(), 'roof_drain': drain(),
    'iw_plain': interior_wall(False, H0 - 0.005), 'iw_doorway': interior_wall(True, H0 - 0.005), 'iw_end_plain': interior_wall(False, H0 - 0.005, end=True),
    'iw_end_doorway': interior_wall(True, H0 - 0.005, end=True),
    'chimney': chimney(), 'yard_wall': yard_wall(), 'yard_wall_b': yard_wall(0.005), 'yard_pier': yard_pier(), 'yard_gate_leaf': iron_gate(), 'player_scale_ref': player_ref()}
SLOPE = {'r0': (V + 1, V), 'r1': (V + 2, V + 1), 'l0': (V, V + 1), 'l1': (V + 1, V + 2)}
for nm, (ya, yb) in SLOPE.items(): pieces[f'h_side_window_{nm}'] = hall_wall('window', ya, yb, level=False)
pieces['h_side_door_r0'] = hall_wall('door', *SLOPE['r0'], level=False); pieces['h_side_door_l0'] = hall_wall('door', *SLOPE['l0'], level=False)
for s, nm in ((1, 'r'), (-1, 'l')):
    pieces[f'verge_{nm}_first'] = verge(s, True, False); pieces[f'verge_{nm}'] = verge(s); pieces[f'verge_{nm}_end'] = verge(s, False, True)

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
def ftag(fl): return f'floor{fl}'
Y0 = lvl(0)
# ---------- galpao ----------
HB = list(range(-9, 10, 2)); HS = list(range(-9, 6, 2))
for x in HB: put('h_back_door' if x == 5 else 'h_back_window', x, Y0, HZ0, 180, ['back', 'ext', 'hall', ftag(0)])
for x in (1, 7, 9): put('h_front_window', x, Y0, HZ1, 0, ['front', 'ext', 'hall', ftag(0)])
put('h_front_gate', 4, Y0, HZ1, 0, ['front', 'ext', 'hall', ftag(0)])
for c in HS:
    h = '0' if (c + 10) % 4 == 1 else '1'
    put('h_side_door_r0' if c == -1 else f'h_side_window_r{h}', HX, Y0, c, 90, ['right', 'ext', 'hall', ftag(0)])
    put('h_side_door_l0' if c == -5 else f'h_side_window_l{h}', -HX, Y0, c, -90, ['left', 'ext', 'hall', ftag(0)])
put('h_pier_low', HX, Y0, HZ0, 90, ['back', 'right', 'ext', 'hall', ftag(0)]); put('h_pier_low', -HX, Y0, HZ0, 180, ['back', 'left', 'ext', 'hall', ftag(0)])
put('h_pier_high', HX, Y0, HZ1, 0, ['front', 'right', 'ext', 'hall', ftag(0)])
for i, z0 in enumerate(TEETH):
    last = i == len(TEETH) - 1
    for x in HB: put('roof_tooth_end' if last else 'roof_tooth', x, Y0, z0, 0, ['roof', 'hall'])
    for x in (-4, 4): put('rafter_end' if last else 'rafter', x, Y0, z0, 0, ['roof', 'hall'])
    sf = '_first' if i == 0 else '_end' if last else ''
    for nm in ('r', 'l'): put(f'verge_{nm}{sf}', 0, Y0, z0, 0, ['roof', 'hall'])
for zv in TEETH[1:]:
    put('girder', 0, Y0, zv, 0, ['hall', ftag(0)])
    for x in (-4, 4): put('column', x, Y0, zv, 0, ['hall', ftag(0)])
    for x in (-6, -2, 2, 6): put('pendant', x, Y0 + V - 0.76, zv, 0, ['hall', ftag(0)])
# portao, portas de servico, rampa, degraus, luminarias
hx, hz = hinge(4, HZ1, 0, -1.6, -0.15); put('gate_leaf', hx, Y0 + 0.013, hz, 0, ['front', 'ext', 'hall', ftag(0)], door=88)
hx, hz = hinge(4, HZ1, 0, 1.6, -0.15); put('gate_leaf', hx, Y0 + 0.013, hz, 180, ['front', 'ext', 'hall', ftag(0)], door=-88)
put('gate_ramp', 4, Y0, HZ1, 0, ['front', 'ext']); put('gooseneck', 4, Y0 + 5.3, HZ1, 0, ['front', 'ext', 'hall'])
for (x, z, ry, tg) in ((HX, -1.0, 90, 'right'), (-HX, -5.0, -90, 'left'), (5.0, HZ0, 180, 'back')):
    hx, hz = hinge(x, z, ry, -0.48, -0.15); put('door_leaf_side', hx, Y0 + 0.013, hz, ry, [tg, 'ext', 'hall', ftag(0)], door=85)
    put('hall_steps', x, Y0, z, ry, [tg, 'ext']); put('gooseneck', x, Y0 + 3.15, z, ry, [tg, 'ext', 'hall'])
# ---------- escritorio ----------
OX0, OX1, OZ0, OZ1 = -10.0, 0.0, 6.0, 14.0
OF = list(range(-9, 0, 2)); OS = list(range(7, 14, 2))
for x in OF:
    put('o_g_door' if x == -5 else 'o_g_window', x, lvl(0), OZ1, 0, ['front', 'ext', 'office', ftag(0)])
    put('o_u1_window', x, lvl(1), OZ1, 0, ['front', 'ext', 'office', ftag(1)]); put('o_u2_window', x, lvl(2), OZ1, 0, ['front', 'ext', 'office', ftag(2)])
    put('o_parapet', x, YR, OZ1, 0, ['front', 'roof', 'office'])
    put('o_g_door_in' if x == -3 else 'o_g_plain', x, lvl(0), OZ0, 180, ['back', 'office', ftag(0)])
    put('o_u1_window' if x >= -5 else 'o_u1_plain', x, lvl(1), OZ0, 180, ['back', 'office', ftag(1)]); put('o_u2_plain', x, lvl(2), OZ0, 180, ['back', 'office', ftag(2)])
    put('o_parapet', x, YR, OZ0, 180, ['back', 'roof', 'office'])
for z in OS:
    for (x, ry, tg) in ((OX0, -90, 'left'), (OX1, 90, 'right')):
        put('o_g_window', x, lvl(0), z, ry, [tg, 'ext', 'office', ftag(0)]); put('o_u1_window', x, lvl(1), z, ry, [tg, 'ext', 'office', ftag(1)])
        put('o_u2_window', x, lvl(2), z, ry, [tg, 'ext', 'office', ftag(2)]); put('o_parapet', x, YR, z, ry, [tg, 'roof', 'office'])
for (x, z, ry, tg, b) in ((OX1, OZ1, 0, ('front', 'right'), ''), (OX0, OZ1, -90, ('left', 'front'), ''), (OX0, OZ0, 180, ('back', 'left'), '_back'), (OX1, OZ0, 90, ('right', 'back'), '_back')):
    for nm, fl in (('g', 0), ('u1', 1), ('u2', 2)): put(f'o_corner{b}_{nm}', x, lvl(fl), z, ry, list(tg) + ['ext', 'office', ftag(fl)])
    put(f'o_corner{b}_p', x, YR, z, ry, list(tg) + ['roof', 'office'])
hx, hz = hinge(-5, OZ1, 0, -0.47, -0.15); put('door_leaf_front', hx, lvl(0) + 0.013, hz, 0, ['front', 'ext', 'office', ftag(0)], door=85)
put('o_steps', -5, lvl(0), OZ1, 0, ['front', 'ext'])
for dx in (-0.95, 0.95): put('wall_lantern', -5 + dx, lvl(0) + 2.0, OZ1, 0, ['front', 'ext', 'office'])
hx, hz = hinge(-3, OZ0, 180, -0.47, -0.15); put('door_leaf_hall', hx, lvl(0) + 0.013, hz, 180, ['office', ftag(0)], door=85)
# terraco do escritorio
put('water_tank', -3.0, YR, 9.5, 0, ['roof', 'office'])
for (x, z) in ((-8.0, 8.0), (-6.5, 12.6)): put('vent', x, YR, z, 0, ['roof', 'office'])
for (x, z) in ((-8.8, 12.8), (-1.2, 7.2)): put('roof_drain', x, YR, z, 0, ['roof', 'office'])
# ---------- pisos ----------
HOLES = {1: [(LA[0], ZB, LA[1], ZA - 1.5)], 2: [(LB[0], ZB + 1.5, LB[1], ZA)]}
TILE_N = {}
def tile_piece(kind, lv, rect, holes, trim):
    key = (kind, lv, rect, tuple(holes), trim)
    if key not in TILE_N:
        nm = f'floor_{kind}_{lv}' + ('_e' + ''.join(map(str, trim)) if any(trim) else ''); base = nm; i = 2
        while nm in pieces: nm = f'{base}_h{i}'; i += 1
        pieces[nm] = floor_tile(kind, lv, rect, holes, trim); TILE_N[key] = nm
    return TILE_N[key]
for a in HB:
    for b in HS:
        tr = (int(a == HB[0]), int(a == HB[-1]), int(b == HS[0]), int(b == HS[-1] and a > 0))
        put(tile_piece('hall', 'g', (-1, 1, -1, 1), [], tr), a, Y0, b, 0, ['hall', ftag(0)])
for fl in (0, 1, 2, 3):
    lv = 'g' if fl == 0 else ('r' if fl == 3 else 'u')
    for a in OF:
        for b in OS:
            tr = (int(a == OF[0]), int(a == OF[-1]), int(b == OS[0]), int(b == OS[-1]))
            hs = []
            for (x0, z0, x1, z1) in HOLES.get(fl, []):
                r = sbox(a - 1, b - 1, a + 1, b + 1).intersection(sbox(x0, z0, x1, z1))
                if r.area > 1e-6: bb = r.bounds; hs.append((round(bb[0] - a, 3), round(bb[1] - b, 3), round(bb[2] - a, 3), round(bb[3] - b, 3)))
            kind = 'membrane' if fl == 3 else ('marble' if fl == 0 and (a < -6 or b > 10) else 'floor')
            put(tile_piece(kind, lv, (-1, 1, -1, 1), hs, tr), a, lvl(fl), b, 0, [ftag(fl) if fl < 3 else 'roof', 'office'])
# ---------- escada e guarda-corpos ----------
put('stair', LA[0], lvl(0), ZA, 0, [ftag(0), 'office']); put('stair_both', LB[1], lvl(1), ZB, 180, [ftag(1), 'office'])
def put_rail(fl, x0, z0, x1, z1, posts=(True, True)):
    Lr = round(abs(x1 - x0) + abs(z1 - z0), 3); nm = f'rail_{int(round(Lr * 100))}' + ('' if all(posts) else '_' + ''.join('1' if q else '0' for q in posts))
    if nm not in pieces: pieces[nm] = rail(Lr, posts)
    if abs(z1 - z0) < 1e-6: put(nm, min(x0, x1), lvl(fl), z0, 0, [ftag(fl), 'office'])
    else: put(nm, x0, lvl(fl), max(z0, z1), 90, [ftag(fl), 'office'])
XG = (LA[1] + LB[0]) / 2; XR = LB[1] + 0.1
put_rail(1, XG, ZB, XG, ZA - 1.5); put_rail(1, LA[0] + 0.05, ZA - 1.5, XG - 0.04, ZA - 1.5, (True, False))
put_rail(2, XG, ZB + 1.5, XG, ZA); put_rail(2, XR, ZB + 1.5, XR, ZA); put_rail(2, XG + 0.04, ZB + 1.5, XR - 0.04, ZB + 1.5, (False, False))
# ---------- paredes internas ----------
def wl(fl, x0, z0, x1, z1, doors=(), side=-1):
    """Paredes internas em modulos de 2 m; pontas que encostam nas paredes externas usam a versao 'end'.
    side: lado para onde as portas abrem (-1 = -Z/-X, 1 = +Z/+X)."""
    y = lvl(fl)
    if z0 == z1:
        for c in range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2):
            end = (c - 1 == OX0) or (c + 1 == OX1); d = c in doors; ry = 0 if (c + 1 == OX1 or not end) else 180
            put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), c, y, z0, ry, [ftag(fl), 'office'])
            if d:
                dr = 0 if side < 0 else 180; hx, hz = hinge(c, z0, dr, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, dr, [ftag(fl), 'office'], door=75)
    else:
        for c in range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2):
            end = (c - 1 == OZ0) or (c + 1 == OZ1); d = c in doors; ry = (90 if c - 1 == OZ0 else -90) if end else 90
            put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), x0, y, c, ry, [ftag(fl), 'office'])
            if d:
                hry = 90 if side < 0 else -90; hx, hz = hinge(x0, c, hry, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, hry, [ftag(fl), 'office'], door=90)
for fl in (0, 1, 2):
    wl(fl, -6.0, OZ0, -6.0, OZ1, doors=(7, 11), side=1)
    wl(fl, -6.0, 10.0, OX1, 10.0, doors=(-3,), side=-1)
# ---------- patio: chamines, muro, portao, caminhos ----------
for x in (-5.5, 1.5): put('chimney', x, 0.0, -12.5, 0, ['back', 'yard'])
for z in range(-11, 16, 2): put('yard_wall_b', 14.0, 0.0, z, 90, ['yard'])
for z in range(-12, 17, 4): put('yard_pier', 14.0, 0.0, z, 0, ['yard'])
for x in (7, 9, 11, 13): put('yard_wall', x, 0.0, 16.0, 0, ['yard', 'front'])
for x in (2, 6, 10): put('yard_pier', x, 0.0, 16.0, 0, ['yard', 'front'])
put('yard_gate_leaf', 2.25, 0.0, 16.0, 0, ['yard', 'front'], door=90); put('yard_gate_leaf', 5.75, 0.0, 16.0, 180, ['yard', 'front'], door=-90)
ZR = HZ1 + 2.25; pieces['path_gate'] = path_slab(16.0 - ZR, 3.4); put('path_gate', 4.0, 0.0, (ZR + 16.0) / 2, 0, ['yard'])
ZO = OZ1 + 1.25; pieces['path_office'] = path_slab(19.0 - ZO, 1.6); put('path_office', -5.0, 0.0, (ZO + 19.0) / 2, 0, ['yard'])
put('player_scale_ref', 4.0, 0, 9.0); put('player_scale_ref', 1.0, Y0, 0.0, 0, ['hall', ftag(0)]); put('player_scale_ref', -3.0, Y0, 12.0, 0, ['office', ftag(0)])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    json.dump({'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE,
                        'hall': {'x': [-HX, HX], 'z': [HZ0, HZ1], 'valley': V, 'ridge': V + RISE, 'teeth_z': TEETH},
                        'office': {'x': [OX0, OX1], 'z': [OZ0, OZ1], 'floors': 3, 'roof_level': YR}, 'stair_holes': HOLES,
                        'roof': 'sawtooth steel roof with vertical north-light glazing over the hall; flat membrane roof behind a parapet over the office',
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
