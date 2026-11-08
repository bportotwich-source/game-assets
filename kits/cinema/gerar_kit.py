"""Kit 30: cinema de rua dos anos 1920, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Bloco da frente de 14 x 8 m e 3 andares com fachada de terracota creme: pilares verticais que sobem ate pinaculos acima da
platibanda, janelas em arco pleno com moldura de pingadeira e bandeira com rendilhado, faixas entre os andares, arcada cega
na platibanda. Terreo com portas de bronze e vidro, vitrine da loja, porta do escritorio e quadro de cartazes (sem texto).
Marquise com quadros de letreiro em branco e lampadas, letreiro vertical vermelho com lampadas (sem letras), bilheteria
redonda de vidro na calcada e postes de luz. Atras, a sala de projecao de 14 x 18 m de tijolo, com plateia em degraus e
poltronas, corredores, palco com boca de cena em arco dourado, cortinas, tela, arandelas, lustre e saidas laterais.
Escada de 2 lances para os escritorios e a cabine de projecao no 1o andar. Y para cima, 1 unidade = 1 m.
Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'terra': (232, 214, 178), 'terra2': (214, 192, 150), 'brick': (146, 62, 46), 'brick2': (110, 44, 34), 'trim': (226, 218, 198),
                  'plinth': (70, 68, 72), 'coping': (210, 198, 170), 'plaster': (238, 232, 220), 'aplaster': (196, 150, 112), 'floor': (150, 106, 70),
                  'concrete': (170, 166, 158), 'marble': (232, 228, 218), 'slate': (64, 66, 68), 'membrane': (92, 94, 96), 'seam': (78, 80, 82),
                  'frame': (238, 236, 228), 'sash': (238, 236, 228), 'bronze': (120, 88, 52), 'gold': (200, 160, 80), 'steel': (110, 114, 118),
                  'iron': (30, 32, 34), 'door': (112, 34, 32), 'door_int': (222, 216, 200), 'carpet': (128, 30, 34), 'seat': (150, 30, 36),
                  'curtain': (140, 24, 30), 'screen': (240, 240, 236), 'marquee': (236, 226, 200), 'board': (248, 246, 238), 'sign': (172, 34, 30),
                  'poster': (60, 90, 120), 'wood': (96, 60, 38), 'grate': (60, 62, 64), 'stagefl': (120, 84, 52), 'wframe': (70, 58, 44), 'dark': (30, 30, 30), 'tile': (214, 224, 228)},
           texturas={'terra': 'stone2', 'terra2': 'render', 'brick': 'brick', 'brick2': 'brick', 'trim': 'render', 'plinth': 'stone',
                     'plaster': 'plaster', 'aplaster': 'plaster', 'floor': 'planks', 'concrete': 'render', 'membrane': 'render', 'marble': 'plaster',
                     'carpet': 'render', 'wood': 'planks', 'stagefl': 'planks'},
           out=OUT)
D.METAL.update({'bronze', 'gold'}); MATS = D.MATS; TEX = D.TEX
for k in ('bronze', 'gold'): MATS[k].metallicFactor = 0.7; MATS[k].roughnessFactor = 0.35

W = 2.0; T = 0.3; H = 3.4; SLAB = 0.25; RAISE = 0.15
H0 = H - SLAB
def lvl(fl): return RAISE + fl * H
YR = lvl(3); PAR = 1.2; PL = 0.45; PLH = 0.5
FX = 7.0; FZ0 = -2.0; FZ1 = 6.0              # bloco da frente
AZ0 = -20.0; AY = 9.0; ATOP = AY + 0.8; AB = -2.2   # sala: fundo, laje (do piso 0), topo da platibanda, base das paredes
PW = 0.18
NR = 18; RS_ = H / NR; TR = 0.26; SW_ = 1.1; RUN = (NR - 1) * TR
LA = (-6.7, -5.6); LB = (-5.3, -4.2); ZA = 4.7; ZB = ZA - RUN

# ============================================================================ ferramentas comuns
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

COPE = lambda yt: [(-T - 0.05, yt), (0.15, yt), (0.15, yt + 0.03), (0.12, yt + 0.06), (-T - 0.02, yt + 0.06), (-T - 0.05, yt + 0.03)]
def corbel(p, xa, xb, yt):
    """Cachorrada de tijolo sob a capa: 2 fiadas escalonadas, denticulos e friso, de xa a xb (pivo: face da parede)."""
    prof_x(p, 'brick2', xa, xb, crect(0.0, 0.035, yt - 0.62, yt - 0.54, 0.006, (0, 1, 1, 0)))
    n = int((xb - xa) / 0.125)
    for i in range(n): xx = xa + (i + 0.5) * (xb - xa) / n; p.box('brick2', xx - 0.03, xx + 0.03, yt - 0.54, yt - 0.44, -0.01, 0.06)
    prof_x(p, 'brick2', xa, xb, crect(0.0, 0.075, yt - 0.44, yt - 0.36, 0.006, (0, 1, 1, 0)))
    prof_x(p, 'brick', xa, xb, [(0.0, yt - 0.36), (0.1, yt - 0.36), (0.1, yt), (0.0, yt)])
def stone_sill(p, ow, oy0, ext_=0.1, mat='trim'):
    x = ow / 2 + ext_
    prof_x(p, mat, -x, x, [(-0.06, oy0 - 0.08), (0.06, oy0 - 0.08), (0.075, oy0 - 0.065), (0.075, oy0 - 0.025), (0.065, oy0 - 0.01), (-0.06, oy0 + 0.02)])
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
def steps(w=0.8, d=0.8, n=2):
    """Patamar e degraus de pedra (pivo: face da parede, eixo, cota do piso; descem para +Z ate o chao)."""
    p = Piece(); r = RAISE / n
    p.box('trim', -w, w, -0.04, 0.0, 0.0, d); p.box('plinth', -w + 0.005, w - 0.005, -RAISE + 0.002, -0.04, 0.0, d - 0.005)
    for i in range(n - 1, 0, -1):
        y = -RAISE + i * r; z0 = d + (n - 1 - i) * 0.3
        prof_x(p, 'trim', -w, w, [(z0, y - r - 0.0 + 0.002), (z0 + 0.3, y - r + 0.002), (z0 + 0.3, y - 0.03), (z0 + 0.32, y - 0.012), (z0 + 0.32, y), (z0, y)])
    return p
def vent():
    p = Piece(); p.cham('membrane', -0.18, 0.18, 0.0, 0.06, -0.18, 0.18, 0.02); p.cyl('steel', 0.06, 0.06, 0.55, 0.0, 0.0, 12)
    p.cyl('steel', 0.13, 0.55, 0.6, 0.0, 0.0, 14); p.hull('steel', [(0.13 * math.cos(a), 0.6, 0.13 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)] + [(0, 0.68, 0)])
    return p
def drain():
    p = Piece(); p.cyl('seam', 0.16, 0.0, 0.012, 0.0, 0.0, 16); p.hull('grate', [(0.1 * math.cos(a), 0.012, 0.1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)] + [(0, 0.09, 0)])
    return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p

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
OWIN = (1.0, 0.9, 2.2, 0.22); ODOOR = (1.1, 0.0, 2.4, 0.2)
BELT = [(0.0, -0.25), (0.05, -0.25), (0.05, -0.2), (0.065, -0.185), (0.065, -0.05), (0.08, -0.04), (0.09, -0.01), (0.09, 0.03), (0.07, 0.05), (0.0, 0.08)]
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

# ============================================================================ fachada de terracota
PX = 0.78; PD = 0.12                         # face interna dos meio-pilares e saliencia
FWIN = (1.0, 0.9, 2.3, 0.5)                  # janela em arco pleno dos andares
def f_wall(kind='window', fl=1):
    """Modulo de 2 m da fachada (pivo: face externa, cota do piso): terracota com meio-pilar em cada ponta, gesso por dentro.
    Terreo: 'doors' (2 folhas de bronze e bandeira), 'vitrine', 'door' (porta simples com bandeira) ou 'poster' (quadro de cartaz).
    Andares: janela de guilhotina em arco pleno com bandeira de rendilhado, pingadeira, peitoril e almofada embaixo."""
    p = Piece(); y0 = -RAISE if fl == 0 else -SLAB; op = None
    if kind == 'window': op = opening(*FWIN)
    if kind == 'doors': op = sbox(-0.7, 0.0, 0.7, 3.0)
    if kind == 'vitrine': op = sbox(-0.7, 0.6, 0.7, 2.9)
    if kind == 'door': op = sbox(-0.55, 0.0, 0.55, 2.9)
    out = sbox(-W / 2, y0, W / 2, H0); inn = sbox(-W / 2, y0, W / 2, H0 - 0.005)
    ext(p, 'terra', out.difference(op) if op else out, -T + 0.02, 0.0); ext(p, 'plaster', inn.difference(op) if op else inn, -T, -T + 0.02)
    yb = 0.6 if fl == 0 else y0
    for (a, b) in ((-1.0, -PX), (PX, 1.0)): p.box('terra', a, b, yb, H0, -0.01, PD)
    if fl == 0:
        for (a, b) in ((-1.0, -PX + 0.03), (PX - 0.03, 1.0)): p.box('plinth', a, b, -RAISE, 0.6, 0.0, PD + 0.03)
        gx = {'doors': (-0.7, 0.7), 'door': (-0.55, 0.55)}.get(kind)
        segs = [(-PX, gx[0]), (gx[1], PX)] if gx else [(-PX, PX)]
        for (a, b) in segs:
            if b - a > 0.01: prof_x(p, 'plinth', a, b, crect(0.0, 0.03, -RAISE, 0.6, 0.008, (0, 0, 1, 0)))
        prof_x(p, 'terra2', -PX, PX, crect(0.0, 0.05, 3.02, 3.15, 0.008, (0, 1, 0, 0)))          # faixa do letreiro (lisa)
    if kind == 'doors':
        x = 0.7
        p.box('bronze', -x, -x + 0.06, 0.0, 3.0, -0.22, -0.1); p.box('bronze', x - 0.06, x, 0.0, 3.0, -0.22, -0.1)
        p.box('bronze', -x + 0.06, x - 0.06, 2.4, 2.48, -0.22, -0.1); p.box('bronze', -x + 0.06, x - 0.06, 2.94, 3.0, -0.22, -0.1)
        p.box('glass', -x + 0.06, x - 0.06, 2.48, 2.94, -0.162, -0.158)
        for xx in np.linspace(-x + 0.06, x - 0.06, 6)[1:-1]: p.box('bronze', xx - 0.012, xx + 0.012, 2.48, 2.94, -0.175, -0.145)
        p.box('bronze', -x, x, -0.03, 0.012, -0.296, 0.04)
    if kind == 'door':
        x = 0.55
        p.box('bronze', -x, -x + 0.06, 0.0, 2.9, -0.22, -0.1); p.box('bronze', x - 0.06, x, 0.0, 2.9, -0.22, -0.1)
        p.box('bronze', -x + 0.06, x - 0.06, 2.3, 2.36, -0.22, -0.1); p.box('bronze', -x + 0.06, x - 0.06, 2.84, 2.9, -0.22, -0.1)
        p.box('glass', -x + 0.06, x - 0.06, 2.36, 2.84, -0.162, -0.158)
        p.box('bronze', -x, x, -0.03, 0.012, -0.296, 0.04)
    if kind == 'vitrine':
        inner = op.buffer(-0.05, join_style=2); ext(p, 'bronze', op.difference(inner), -0.12, -0.05)
        p.box('bronze', -0.65, 0.65, 2.28, 2.34, -0.11, -0.06); p.box('glass', -0.65, 0.65, 0.65, 2.85, -0.092, -0.088)
        p.box('wood', -0.7, 0.7, 0.6, 0.62, -T - 0.25, -0.12)
    if kind == 'poster':
        p.box('bronze', -0.55, -0.5, 0.8, 2.6, 0.0, 0.09); p.box('bronze', 0.5, 0.55, 0.8, 2.6, 0.0, 0.09)
        p.box('bronze', -0.5, 0.5, 0.8, 0.85, 0.0, 0.09); p.box('bronze', -0.5, 0.5, 2.55, 2.6, 0.0, 0.09)
        p.box('poster', -0.5, 0.5, 0.85, 2.55, 0.0, 0.03); p.box('glass', -0.5, 0.5, 0.85, 2.55, 0.075, 0.078)
        p.box('bronze', -0.45, 0.45, 2.64, 2.7, 0.0, 0.16); p.box('lamp_glass', -0.4, 0.4, 2.62, 2.64, 0.04, 0.14)
    if kind == 'window':
        w_, s_, ys, r_ = FWIN; sash_window(p, w_, s_, ys)
        seg = op.intersection(sbox(-w_ / 2, ys, w_ / 2, ys + 1)); inner = seg.buffer(-0.05, join_style=2)
        ext(p, 'frame', seg.difference(inner), -0.2, -0.04); ext(p, 'glass', inner, -0.122, -0.118)
        tr = unary_union([sbox(-0.02, ys, 0.02, ys + r_), Point(0, ys + 0.25).buffer(0.15, 24).difference(Point(0, ys + 0.25).buffer(0.12, 24))]).intersection(inner)
        ext(p, 'frame', tr, -0.14, -0.1)
        voussoirs(p, 'terra2', w_, ys, r_, d=0.1, z1=0.05, bw=0.1)
        for s in (-1, 1):
            a, b = sorted((s * w_ / 2, s * (w_ / 2 + 0.18))); p.box('terra2', a, b, ys - 0.12, ys, 0.0, 0.05)
        stone_sill(p, w_, s_, mat='terra2')
        p.box('terra2', -0.45, 0.45, 0.2, 0.7, 0.0, 0.02)
        p.hull('terra2', [(0.0, 0.3, 0.02), (0.0, 0.6, 0.02), (-0.25, 0.45, 0.02), (0.25, 0.45, 0.02), (0.0, 0.45, 0.045)])
        if fl == 1: prof_x(p, 'terra', -PX, PX, BELT)
        if fl == 2:
            prof_x(p, 'terra2', -PX, PX, crect(0.0, 0.08, H0 - 0.3, H0 - 0.12, 0.01, (0, 1, 1, 0)))
            for (a, b) in ((-0.997, -PX + 0.02), (PX - 0.02, 0.997)): p.box('terra2', a, b, H0 - 0.32, H0 - 0.1, -0.01, PD + 0.025)
    return p
def f_parapet():
    """Platibanda da fachada (pivo: face externa, cota do terraco): arcada cega de 3 arcos, capa e meio-pinaculos nas pontas."""
    p = Piece(); top = PAR - 0.06
    ext(p, 'terra', sbox(-W / 2, -SLAB, W / 2, top), -T + 0.02, 0.0)
    ext(p, 'plaster', sbox(-W / 2, -SLAB, W / 2, -0.03), -T, -T + 0.02); ext(p, 'terra', sbox(-W / 2, -0.03, W / 2, top), -T, -T + 0.02)
    for xc in (-0.47, 0.0, 0.47):
        fr = opening(0.4, 0.2, 0.62, 0.2, xc).difference(opening(0.3, 0.25, 0.62, 0.15, xc)); ext(p, 'terra2', fr, 0.0, 0.025)
    prof_x(p, 'terra2', -PX, PX, crect(0.0, 0.05, 0.05, 0.15, 0.008, (0, 1, 1, 0)))
    prof_x(p, 'coping', -PX, PX, COPE(top))
    for s in (-1, 1):
        a, b = sorted((s * 1.0, s * PX))
        p.box('terra', a, b, -SLAB, 0.0, -0.01, PD); p.box('terra', a, b, 0.0, PAR + 0.6, -T - 0.08, 0.16)
        a2, b2 = sorted((s * 1.0, s * (PX - 0.02))); p.box('terra2', a2, b2, PAR + 0.6, PAR + 0.68, -T - 0.1, 0.18)
        p.hull('terra2', [(s * xx, PAR + 0.68, zz) for xx in (1.0, PX - 0.02) for zz in (-T - 0.1, 0.18)] + [(s * 1.0, PAR + 1.3, -0.06)])
        a3, b3 = sorted((s * 0.997, s * PX)); p.box('terra2', a3, b3, PAR - 0.3, PAR - 0.22, -T - 0.1, 0.18)
    return p
def f_corner(fl):
    """Quina da fachada (pivo: quina externa, cota do piso; paredes em -X e -Z): pilar de terracota em L que vira pinaculo inteiro."""
    p = Piece(); e = 0.004; y0 = -RAISE if fl == 0 else -SLAB
    if fl < 3:
        p.box('plaster', -T + 0.004, e, y0 + 0.003, H0 - 0.004, -T + 0.004, e)
        yb = 0.6 if fl == 0 else y0
        p.box('terra', -0.4, 0.16, yb, H0, -0.01, 0.16); p.box('terra', -0.01, 0.16, yb, H0, -0.4, -0.01)
        if fl == 0: p.box('plinth', -0.43, 0.19, -RAISE + 0.004, 0.62, -0.01, 0.19); p.box('plinth', -0.01, 0.19, -RAISE + 0.004, 0.62, -0.43, -0.01)
        if fl == 2:
            p.box('terra2', -0.42, 0.185, H0 - 0.32, H0 - 0.1, -0.01, 0.185); p.box('terra2', -0.01, 0.185, H0 - 0.32, H0 - 0.1, -0.42, -0.01)
    else:
        p.box('terra', -T + 0.004, e, -SLAB + 0.003, 0.0, -T + 0.004, e)
        p.box('terra', -0.4, 0.16, -SLAB, 0.0, -0.01, 0.16); p.box('terra', -0.01, 0.16, -SLAB, 0.0, -0.4, -0.01)
        p.box('terra', -0.42, 0.17, 0.0, PAR + 0.8, -0.42, 0.17)
        p.box('terra2', -0.45, 0.2, PAR - 0.3, PAR - 0.22, -0.45, 0.2); p.box('terra2', -0.46, 0.21, PAR + 0.8, PAR + 0.9, -0.46, 0.21)
        p.hull('terra2', [(x, PAR + 0.9, z) for x in (-0.46, 0.21) for z in (-0.46, 0.21)] + [(-0.125, PAR + 1.65, -0.125)])
        p.sphere('terra2', 0.06, -0.125, PAR + 1.68, -0.125, 1)
    return p
def entry_leaf(w=0.66, h=2.38, t=0.045):
    """Folha de bronze e vidro (pivo: dobradica, embaixo): montantes, travessa baixa com chapa, vidro inteiro e barra."""
    p = Piece(); s = 0.08
    p.box('bronze', 0.0, s, 0.0, h, -t / 2, t / 2); p.box('bronze', w - s, w, 0.0, h, -t / 2, t / 2)
    p.box('bronze', s, w - s, 0.0, 0.28, -t / 2, t / 2); p.box('bronze', s, w - s, h - 0.1, h, -t / 2, t / 2)
    p.box('glass', s, w - s, 0.28, h - 0.1, -0.003, 0.003)
    for z in (1, -1):
        seg_cyl(p, 'gold', (s + 0.02, 1.05, z * (t / 2 + 0.05)), (w - s - 0.02, 1.05, z * (t / 2 + 0.05)), 0.014, 8)
        for xx in (s + 0.04, w - s - 0.04): p.seg('gold', (xx, 1.05, z * t / 2), (xx, 1.05, z * (t / 2 + 0.05)), 0.016)
    for yy in (0.25, 1.2, 2.1): p.cyl('gold', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def b_wall(kind='plain', fl=0, ycut=99.0):
    """Parede entre o bloco da frente e a sala (pivo: face voltada para a sala, z = -2, girada 180): gesso colorido do lado da sala
    ate ycut e tijolo acima; gesso do lado do bloco. 'door' = porta para a sala, 'port' = visores da cabine de projecao."""
    p = Piece(); y0 = -RAISE if fl == 0 else -SLAB; top = H0 if fl < 3 else PAR - 0.06; ops = []
    if kind == 'door': ops = [sbox(-0.5, 0.0, 0.5, 2.2)]
    if kind == 'port': ops = [sbox(-0.18, 1.15, 0.18, 1.45), sbox(0.45, 1.25, 0.7, 1.45)]
    hole = unary_union(ops) if ops else None
    def cut(g): return g.difference(hole) if hole else g
    ext(p, 'brick', cut(sbox(-W / 2, y0, W / 2, top)), -T + 0.02, -0.02)
    if ycut > y0: ext(p, 'aplaster', cut(sbox(-W / 2, y0, W / 2, min(ycut, top))), -0.02, 0.0)
    if ycut < top: ext(p, 'brick', cut(sbox(-W / 2, max(ycut, y0), W / 2, top)), -0.02, 0.0)
    if fl < 3: ext(p, 'plaster', cut(sbox(-W / 2, y0, W / 2, H0 - 0.005)), -T, -T + 0.02)
    else:
        ext(p, 'plaster', sbox(-W / 2, -SLAB, W / 2, -0.03), -T, -T + 0.02); ext(p, 'brick', sbox(-W / 2, -0.03, W / 2, top), -T, -T + 0.02)
        corbel(p, -W / 2, W / 2, top); prof_x(p, 'coping', -W / 2, W / 2, COPE(top))
    if kind == 'door':
        for (a, b) in ((-0.5, -0.44), (0.44, 0.5)): p.box('wood', a, b, 0.0, 2.2, -T, 0.0)
        p.box('wood', -0.44, 0.44, 2.14, 2.2, -T, 0.0); p.box('trim', -0.5, 0.5, -0.03, 0.012, -T + 0.004, -0.004)
        for (z0, z1) in ((0.0, 0.025), (-T - 0.025, -T)):
            for s in (-1, 1): a, b = sorted((s * 0.5, s * 0.6)); p.box('wood', a, b, 0.012, 2.3, z0, z1)
            p.box('wood', -0.6, 0.6, 2.2, 2.3, z0, z1)
    if kind == 'port':
        for o in ops:
            x0, y0_, x1, y1 = o.bounds; p.box('glass', x0, x1, y0_, y1, -0.152, -0.148)
            p.box('steel', x0 - 0.05, x1 + 0.05, y0_ - 0.05, y1 + 0.05, -T - 0.01, -T)
    return p

# ============================================================================ sala de projecao: paredes de tijolo
ADOOR = (1.1, 0.0, 2.45, 0.25)
def a_wall(kind='plain'):
    """Modulo de 2 m da sala (pivo: face externa, cota do piso do saguao; vai de AB, abaixo do chao, ate a platibanda):
    tijolo com meias pilastras, embasamento, fiada de tijolo escuro, cachorrada e capa; gesso colorido por dentro.
    'door' = saida de emergencia com verga em arco e bandeira."""
    p = Piece(); x0, x1 = -W / 2, W / 2; top = ATOP - 0.06
    op = opening(*ADOOR) if kind == 'door' else None
    def cut(g): return g.difference(op) if op else g
    ext(p, 'brick', cut(sbox(x0, AB, x1, top)), -T + 0.02, 0.0)
    ext(p, 'aplaster', cut(sbox(x0, AB, x1, AY - 0.26)), -T, -T + 0.02); ext(p, 'brick', sbox(x0, AY - 0.26, x1, top), -T, -T + 0.02)
    for (a, b) in ((x0, x0 + PW), (x1 - PW, x1)): p.box('brick', a, b, PLH, top, -0.01, 0.1)
    if kind == 'door': segs = [(x0 + PW, -0.55), (0.55, x1 - PW)]
    else: segs = [(x0 + PW, x1 - PW)]
    for (a, b) in segs: prof_x(p, 'plinth', a, b, crect(0.0, 0.04, -RAISE, PLH, 0.012, (0, 0, 1, 0)))
    for (a, b) in ((x0, x0 + PW + 0.02), (x1 - PW - 0.02, x1)): prof_x(p, 'plinth', a, b, crect(0.0, 0.13, -RAISE, PLH, 0.015, (0, 0, 1, 0)))
    prof_x(p, 'brick2', x0 + PW, x1 - PW, crect(0.0, 0.03, 3.4, 3.62, 0.006, (0, 1, 1, 0)))
    corbel(p, x0 + PW, x1 - PW, top); prof_x(p, 'coping', x0, x1, COPE(top))
    if kind == 'door':
        w_, s_, ys, r_ = ADOOR; x = w_ / 2
        voussoirs(p, 'brick2', w_, ys, r_, key='trim')
        prof_x(p, 'trim', -x, x, [(-0.295, 0.012), (0.04, 0.012), (0.06, 0.0), (0.06, -0.045), (-0.295, -0.045)])
        p.box('steel', -x, -x + 0.06, 0.0, ys, -0.2, -0.1); p.box('steel', x - 0.06, x, 0.0, ys, -0.2, -0.1); p.box('steel', -x + 0.06, x - 0.06, 2.37, ys, -0.2, -0.1)
        steel_window(p, op.intersection(sbox(-x, ys, x, ys + 1)), zf=-0.1, dx=0.28, mat='steel')
    return p
def a_pier(top):
    """Pilar de canto da sala (pivo: quina externa; paredes em -X e -Z)."""
    p = Piece(); a, b = -0.38, 0.17
    p.box('brick', a, b, AB + 0.003, top - 0.3, a, b)
    p.cham('plinth', a - 0.03, b + 0.03, -RAISE + 0.004, PLH + 0.04, a - 0.03, b + 0.03, 0.015)
    p.cham('brick2', a - 0.03, b + 0.03, top - 0.3, top - 0.08, a - 0.03, b + 0.03, 0.01)
    p.cham('coping', a - 0.06, b + 0.06, top - 0.08, top, a - 0.06, b + 0.06, 0.012)
    return p

# ============================================================================ sala: plateia em degraus, poltronas, palco
AX = FX - T                      # face interna das paredes laterais
CZ = -3.5; TD = 0.9; NT = 12; TRS = H / (NT + 1)     # plateia em estadio: sobe da orquestra ate o corredor do 1o andar
def tier_top(k): return H - TRS * (k + 1)
def tier_z(k): return CZ - TD * k, CZ - TD * (k + 1)
ZO0 = CZ - TD * NT; YO = 0.0              # orquestra (piso plano na frente do palco)
ZS = -16.5; YS = YO + 1.0; ZBK = AZ0 + T; PSPR = YS + 4.8; VALY = PSPR + 1.6; ZEX = -15          # frente e cota do palco, face interna do fundo
def floor_slab(z0, z1, top, mat='carpet', nosing=True):
    """Faixa de piso da sala de parede a parede (pivo: eixo, cota do saguao): corpo ate AB e acabamento de 3 cm;
    borda de latao na frente do degrau."""
    p = Piece()
    p.box('trim', -AX, AX, AB + 0.05, top - 0.03, z1, z0); p.box(mat, -AX, AX, top - 0.03, top, z1, z0)
    if nosing: p.box('gold', -AX + 0.003, AX - 0.003, top - 0.035, top + 0.004, z1 - 0.005, z1 + 0.03)
    return p
def seat_row():
    """Fileira de 4 poltronas de 50 cm (pivo: borda da frente do degrau, centro, no piso; olham para -Z): pes de ferro fundido
    com bracos de madeira, assento rebatido e encosto de veludo com casca de madeira."""
    p = Piece()
    for xs in (-1.0, -0.5, 0.0, 0.5, 1.0):
        p.hull('iron', [(xs + dx, y, z) for dx in (-0.02, 0.02) for (z, y) in ((0.42, 0.0), (0.78, 0.0), (0.78, 0.06), (0.7, 0.62), (0.4, 0.62), (0.5, 0.06))])
        p.box('wood', max(xs - 0.03, -0.997), min(xs + 0.03, 0.997), 0.62, 0.67, 0.3, 0.8)
    for i in range(4):
        xc = -0.75 + 0.5 * i
        p.cham('seat', xc - 0.215, xc + 0.215, 0.4, 0.49, 0.3, 0.72, 0.02)
        p.hull('seat', [(xc + dx, y, z) for dx in (-0.21, 0.21) for (z, y) in ((0.72, 0.48), (0.8, 0.48), (0.86, 0.98), (0.79, 0.98))])
        p.hull('wood', [(xc + dx, y, z) for dx in (-0.215, 0.215) for (z, y) in ((0.8, 0.46), (0.83, 0.46), (0.9, 1.0), (0.87, 1.0))])
    return p
def stage():
    """Palco (pivo: eixo, cota do saguao): corpo, tablado de madeira, frisos dourados na frente e calha da ribalta."""
    p = Piece()
    p.box('trim', -AX, AX, AB + 0.05, YS - 0.03, ZBK, ZS); p.box('stagefl', -AX, AX, YS - 0.03, YS, ZBK, ZS)
    for (ya, yb) in ((YO + 0.12, YO + 0.2), (YS - 0.16, YS - 0.06)): p.box('gold', -AX, AX, ya, yb, ZS, ZS + 0.03)
    for xx in np.arange(-AX + 0.6, AX - 0.4, 1.2): p.box('gold', xx - 0.3, xx + 0.3, YO + 0.32, YS - 0.28, ZS, ZS + 0.015)
    p.box('dark', -4.0, 4.0, YS, YS + 0.08, ZS + 0.02, ZS + 0.16); p.box('lamp_glass', -3.9, 3.9, YS + 0.01, YS + 0.05, ZS + 0.05, ZS + 0.13)
    return p
def stage_steps():
    """Escada lateral do palco (pivo: centro, na frente do palco, cota da orquestra): 5 degraus de madeira."""
    p = Piece(); n = 5; r = (YS - YO) / n
    for j in range(1, n):
        z1 = 0.3 * (n - j); p.box('stagefl', -0.5, 0.5, 0.0, j * r, 0.0, z1)
    for s in (-1, 1): p.box('gold', s * 0.5 - 0.02, s * 0.5 + 0.02, 0.0, 0.95, 0.004, 0.3 * n - 0.32)
    return p
def proscenium():
    """Boca de cena (pivo: eixo, face da frente, cota do saguao): parede de gesso com arco abatido, aduelas e fecho dourados,
    pilastras douradas com base e capitel e moldura em volta."""
    p = Piece(); w_ = 10.0; ys = PSPR; r_ = 1.4; t = 0.3
    op = opening(w_, YS, ys, r_)
    ext(p, 'aplaster', sbox(-AX, YS, AX, AY - 0.26).difference(op), -t, 0.0)
    voussoirs(p, 'gold', w_, ys, r_, d=0.32, z1=0.06, bw=0.4, key='gold')
    for s in (-1, 1):
        a, b = sorted((s * (w_ / 2), s * (w_ / 2 + 0.45)))
        p.box('gold', a, b, YS, ys - 0.25, 0.0, 0.08); p.box('gold', a - 0.04, b + 0.04, YS, YS + 0.3, 0.0, 0.11)
        p.box('gold', a - 0.05, b + 0.05, ys - 0.25, ys, 0.0, 0.12)
        for k in range(3): xx = a + (k + 0.5) * (b - a) / 3; p.box('aplaster', xx - 0.04, xx + 0.04, YS + 0.4, ys - 0.4, 0.08, 0.1)
    R, cy = arch_geom(w_, ys, r_)
    p.hull('gold', [(sx * 0.35, y, z) for sx in (-1, 1) for y in (ys + r_ + 0.25, ys + r_ + 0.75) for z in (0.0, 0.14)] + [(0.0, ys + r_ + 0.9, 0.07)])
    return p
def curtain_side(w=1.7, h=None):
    """Cortina de veludo puxada para o lado (pivo: borda de fora, embaixo, no meio da espessura): pregas verticais e abracadeira."""
    p = Piece(); h = h or (VALY - 0.05 - YS); n = 9
    for i in range(n):
        x = i * w / n; z = 0.06 if i % 2 else -0.06
        lathe(p, 'curtain', [(0.1, 0.0), (0.1, h)], x=x + w / n / 2, z=z, sec=8)
    p.box('gold', -0.02, w + 0.02, 1.4, 1.48, -0.18, 0.18)
    return p
def valance(w=10.4):
    """Bambinela no alto da boca de cena (pivo: centro, base das pregas)."""
    p = Piece(); n = 26
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n; L = 0.9 + 0.35 * abs(math.sin(math.pi * (i + 0.5) / n * 4))
        lathe(p, 'curtain', [(0.11, -L), (0.11, -0.005)], x=x, z=0.06 if i % 2 else -0.06, sec=8)
    p.box('gold', -w / 2, w / 2, -0.08, 0.005, -0.2, 0.2)
    return p
def screen():
    p = Piece(); p.box('dark', -4.8, 4.8, YS + 0.6, YS + 5.4, -0.04, 0.0); p.box('screen', -4.4, 4.4, YS + 0.85, YS + 5.15, 0.0, 0.01)
    return p
def chandelier():
    """Lustre de latao (pivo: no forro): canopla, haste, 2 aneis de bracos com lampadas e pingentes, gota embaixo."""
    p = Piece(); p.cyl('gold', 0.18, -0.05, 0.0, 0.0, 0.0, 16); p.cyl('gold', 0.02, -1.2, -0.05, 0.0, 0.0, 8)
    for (r, y, n) in ((0.75, -1.5, 12), (0.45, -1.2, 8)):
        lathe(p, 'gold', [(r, y - 0.03), (r, y + 0.03)], sec=24); lathe(p, 'gold', [(r - 0.04, y - 0.03), (r - 0.04, y + 0.03)], sec=24) if False else None
        for k in range(n):
            a = 2 * math.pi * k / n; x, z = r * math.cos(a), r * math.sin(a)
            p.cyl('gold', 0.03, y, y + 0.08, x, z, 8); p.sphere('lamp_glass', 0.05, x, y + 0.13, z, 1)
            p.sphere('lamp_glass', 0.02, x, y - 0.12, z, 0)
        seg_cyl(p, 'gold', (0.0, -1.25, 0.0), (r, y, 0.0), 0.012, 6); seg_cyl(p, 'gold', (0.0, -1.25, 0.0), (-r, y, 0.0), 0.012, 6)
    lathe(p, 'gold', [(0.0, -1.85), (0.12, -1.7), (0.16, -1.55), (0.05, -1.22)], sec=14)
    return p
def sconce():
    """Arandela em leque (pivo: face da parede, centro)."""
    p = Piece(); p.cham('gold', -0.12, 0.12, -0.25, 0.1, 0.0, 0.03, 0.008)
    q = Point(0, -0.05).buffer(0.32, 24).intersection(sbox(-0.4, -0.05, 0.4, 0.4)).difference(Point(0, -0.05).buffer(0.06, 12))
    ext(p, 'gold', q, 0.03, 0.05)
    for k in range(5):
        a = math.pi * (k + 0.5) / 5; ext(p, 'aplaster', Polygon([(0.08 * math.cos(a - 0.12), -0.05 + 0.08 * math.sin(a - 0.12)), (0.3 * math.cos(a - 0.2), -0.05 + 0.3 * math.sin(a - 0.2)), (0.3 * math.cos(a + 0.2), -0.05 + 0.3 * math.sin(a + 0.2)), (0.08 * math.cos(a + 0.12), -0.05 + 0.08 * math.sin(a + 0.12))]), 0.05, 0.056)
    p.sphere('lamp_glass', 0.07, 0.0, 0.02, 0.12, 1)
    return p

# ============================================================================ marquise, letreiro, bilheteria, calcada, cabine
MQ = (3.7, 3.25, 4.25, 3.2)        # meia largura, base, topo, ponta
def marquee():
    """Marquise (pivo: eixo da fachada, cota do piso, face da parede): caixa de chapa creme, quadros de letreiro em branco
    na frente e nos lados com molduras douradas e fileiras de lampadas, forro com grade de lampadas, crista e tirantes."""
    p = Piece(); X, y0, y1, Z = MQ; z0 = PD + 0.02
    p.box('marquee', -X, X, y0, y1, z0, Z)
    p.box('board', -X + 0.2, X - 0.2, y0 + 0.25, y1 - 0.15, Z, Z + 0.02)
    for s in (-1, 1):
        a, b = sorted((s * X, s * (X + 0.02))); p.box('board', a, b, y0 + 0.25, y1 - 0.15, z0 + 0.4, Z - 0.2)
    for (ya, yb) in ((y0 + 0.18, y0 + 0.25), (y1 - 0.15, y1 - 0.08)):
        p.box('gold', -X + 0.1, X - 0.1, ya, yb, Z, Z + 0.04)
        for s in (-1, 1): a, b = sorted((s * X, s * (X + 0.04))); p.box('gold', a, b, ya, yb, z0 + 0.3, Z - 0.1)
    for xx in np.arange(-X + 0.2, X - 0.1, 0.25):
        for yy in (y0 + 0.1, y1 - 0.03): p.sphere('lamp_glass', 0.035, xx, yy, Z + 0.03, 0)
    for xx in np.arange(-X + 0.3, X - 0.2, 0.4):
        for zz in np.arange(z0 + 0.4, Z - 0.2, 0.4): p.sphere('lamp_glass', 0.04, xx, y0 - 0.02, zz, 0)
    for i in range(int(2 * X / 0.4)):
        xx = -X + 0.2 + i * 0.4; p.hull('gold', [(xx + dx, y1, z) for dx in (-0.15, 0.15) for z in (Z - 0.06, Z)] + [(xx, y1 + 0.18, Z - 0.03)])
    p.box('gold', -X, X, y1, y1 + 0.04, z0, Z)
    for xx in (-3.4, -1.2, 1.2, 3.4):
        seg_cyl(p, 'iron', (xx, 7.0, PD), (xx, y1 + 0.02, Z - 0.2), 0.02, 8)
        p.cham('iron', xx - 0.06, xx + 0.06, 6.92, 7.08, 0.0, 0.03, 0.005) if abs(xx) > 3 or True else None
    return p
def blade(y0=4.8, y1=None):
    """Letreiro vertical vermelho (pivo: face do pilar, cota do piso; sai para +Z): caixa com chanfro, molduras douradas,
    medalhoes em branco (sem letras), lampadas nas bordas, coroa com pinha e maos-francesas de ferro ate a fachada."""
    p = Piece(); y1 = y1 or (YR - lvl(0) + PAR + 1.0); a, b = 0.45, 1.95; t = 0.2
    p.cham('sign', -t, t, y0, y1, a, b, 0.03)
    for s in (-1, 1):
        f0, f1 = sorted((s * t, s * (t + 0.02)))
        for (za, zb) in ((a + 0.06, a + 0.12), (b - 0.12, b - 0.06)): p.box('gold', f0, f1, y0 + 0.1, y1 - 0.1, za, zb)
        for (ya, yb) in ((y0 + 0.1, y0 + 0.16), (y1 - 0.16, y1 - 0.1)): p.box('gold', f0, f1, ya, yb, a + 0.06, b - 0.06)
        for k in range(6):
            yc = y0 + 0.75 + k * (y1 - y0 - 1.3) / 5; q = Piece()
            q.add('board', trimesh.creation.cylinder(radius=0.38, height=0.02, sections=20)); q.add('gold', trimesh.creation.annulus(r_min=0.38, r_max=0.43, height=0.03, sections=20))
            M = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]); M[:3, 3] = [s * (t + 0.01), yc, (a + b) / 2]; p.merge(q, M)
        for yy in np.arange(y0 + 0.3, y1 - 0.2, 0.3):
            for zz in (a + 0.09, b - 0.09): p.sphere('lamp_glass', 0.03, s * (t + 0.025), yy, zz, 0)
    p.box('gold', -t - 0.04, t + 0.04, y1, y1 + 0.12, a - 0.04, b + 0.04)
    p.hull('gold', [(x, y1 + 0.12, z) for x in (-t, t) for z in (a + 0.2, b - 0.2)] + [(0.0, y1 + 0.55, (a + b) / 2)])
    p.sphere('gold', 0.08, 0.0, y1 + 0.62, (a + b) / 2, 1)
    for yy in (y0 + 0.5, (y0 + y1) / 2, y1 - 0.6):
        seg_cyl(p, 'iron', (0.0, yy, 0.0), (0.0, yy, a), 0.025, 8); seg_cyl(p, 'iron', (0.0, yy - 0.6, 0.0), (0.0, yy, a), 0.015, 6)
        p.cham('iron', -0.08, 0.08, yy - 0.68, yy + 0.08, 0.0, 0.03, 0.005)
    return p
def booth():
    """Bilheteria redonda (pivo: centro, na calcada): tambor de granito, vidro curvo com montantes de bronze, balcao,
    cornija dourada, cupula com pinha."""
    p = Piece(); sec = 24
    lathe(p, 'plinth', [(0.86, 0.0), (0.86, 0.9)], sec=sec); lathe(p, 'gold', [(0.9, 0.9), (0.9, 0.97)], sec=sec)
    lathe(p, 'glass', [(0.8, 0.97), (0.8, 2.1)], sec=sec)
    for k in range(8):
        a = 2 * math.pi * k / 8; p.cyl('bronze', 0.025, 0.97, 2.1, 0.81 * math.cos(a), 0.81 * math.sin(a), 8)
    lathe(p, 'gold', [(0.86, 2.1), (0.92, 2.2), (0.92, 2.28)], sec=sec)
    lathe(p, 'marquee', [(0.86, 2.28), (0.7, 2.55), (0.4, 2.75), (0.0, 2.82)], sec=sec)
    p.sphere('gold', 0.07, 0.0, 2.9, 0.0, 1); p.cyl('dark', 0.05, 1.35, 1.36, 0.0, 0.0, 12) if False else None
    p.cham('bronze', -0.25, 0.25, 1.0, 1.04, 0.78, 0.96, 0.006)
    return p
def sidewalk(d=3.6):
    """Calcada de 2 m (pivo: eixo, na face do predio, no chao): placas de concreto com juntas e meio-fio de granito."""
    p = Piece(); n = 3
    for i in range(n):
        z0 = i * (d - 0.2) / n + 0.006; z1 = (i + 1) * (d - 0.2) / n - 0.006
        for k in range(2): p.cham('concrete', -1.0 + k + 0.006, k - 0.006, -0.05, 0.03, z0, z1, 0.006)
    p.box('plinth', -1.0, 1.0, -0.18, 0.035, d - 0.2, d)
    return p
def projector():
    """Projetor de cinema (pivo: centro, piso da cabine; aponta para -Z): pedestal, caixa da lampada com chamine, cabeca
    com objetiva e 2 bobinas."""
    p = Piece()
    p.cham('iron', -0.25, 0.25, 0.0, 0.08, -0.35, 0.35, 0.01); p.box('iron', -0.08, 0.08, 0.08, 0.9, -0.08, 0.08)
    p.cham('steel', -0.2, 0.2, 0.9, 1.3, 0.0, 0.5, 0.02); p.cyl('steel', 0.06, 1.3, 1.6, 0.0, 0.25, 10)
    p.cham('dark', -0.12, 0.12, 0.95, 1.35, -0.3, 0.0, 0.015)
    seg_cyl(p, 'steel', (0.0, 1.3, -0.3), (0.0, 1.3, -0.55), 0.05, 12)
    for (y, z) in ((1.75, -0.15), (0.55, -0.15)):
        q = Piece(); q.add('steel', trimesh.creation.cylinder(radius=0.3, height=0.04, sections=20))
        M = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]); M[:3, 3] = [0.16, y, z]; p.merge(q, M)
    return p
def door_padded(w=0.94, h=2.12, t=0.05):
    """Porta da sala estofada (pivo: dobradica, embaixo): couro vermelho com tachas de latao, visor redondo, chapa de chute."""
    p = Piece(); p.cham('door', 0.0, w, 0.0, h, -t / 2, t / 2, 0.01)
    for z in (1, -1):
        zz = z * (t / 2 + 0.004)
        for i in range(5):
            for j in range(7):
                if (i + j) % 2: continue
                x = 0.12 + i * (w - 0.24) / 4; y = 0.35 + j * 0.16
                p.box('gold', x - 0.008, x + 0.008, y - 0.008, y + 0.008, zz - 0.006, zz + 0.006)
        a, b = sorted((z * t / 2, z * (t / 2 + 0.003))); p.box('gold', 0.05, w - 0.05, 0.03, 0.22, a, b)
        q = Piece(); q.add('gold', trimesh.creation.annulus(r_min=0.12, r_max=0.15, height=t + 0.02, sections=20))
        p.merge(q, trimesh.transformations.translation_matrix([w / 2, 1.65, 0.0]))
        p.seg('gold', (w - 0.1, 1.0, z * t / 2), (w - 0.1, 1.0, z * (t / 2 + 0.06)), 0.02); p.cham('gold', w - 0.16, w - 0.04, 0.95, 1.05, z * (t / 2 + 0.05) - 0.01, z * (t / 2 + 0.05) + 0.01, 0.004)
    q = Piece(); q.add('glass', trimesh.creation.cylinder(radius=0.125, height=0.006, sections=20)); p.merge(q, trimesh.transformations.translation_matrix([w / 2, 1.65, 0.0]))
    for yy in (0.25, 1.1, 1.9): p.cyl('gold', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def counter():
    """Balcao da bomboniere (pivo: centro, piso): corpo de madeira com almofadas, tampo de vidro com moldura de bronze."""
    p = Piece(); a, b, d = 1.5, 0.95, 0.3
    p.cham('wood', -d, d, 0.0, b, -a, a, 0.01); p.box('dark', -d - 0.02, d + 0.02, 0.0, 0.1, -a - 0.02, a + 0.02)
    for k in range(4): zc = -a + (k + 0.5) * 2 * a / 4; p.box('bronze', -d - 0.012, -d, 0.2, 0.8, zc - 0.3, zc + 0.3)
    p.box('bronze', -d - 0.02, d + 0.02, b, b + 0.03, -a - 0.02, a + 0.02); p.box('glass', -d, d, b + 0.03, b + 0.3, -a, a)
    p.box('bronze', -d - 0.01, d + 0.01, b + 0.3, b + 0.33, -a - 0.01, a + 0.01)
    return p

# ============================================================================ pecas
pieces = {
    'f_g_poster': f_wall('poster', 0), 'f_g_door': f_wall('door', 0), 'f_g_doors': f_wall('doors', 0), 'f_g_vitrine': f_wall('vitrine', 0),
    'f_u1_window': f_wall('window', 1), 'f_u2_window': f_wall('window', 2), 'f_parapet': f_parapet(),
    'f_corner_g': f_corner(0), 'f_corner_u1': f_corner(1), 'f_corner_u2': f_corner(2), 'f_corner_p': f_corner(3),
    's_g_window': o_wall('window', 0), 's_u1_window': o_wall('window', 1), 's_u2_window': o_wall('window', 2), 's_parapet': o_parapet(),
    'back_corner_u': o_corner(2, False), 'back_corner_g': o_corner(0, False), 'back_corner_p': o_corner(3, False),
    'b_g_plain': b_wall('plain', 0), 'b_u1_plain': b_wall('plain', 1), 'b_u1_door': b_wall('door', 1),
    'b_u2_plain': b_wall('plain', 2, ycut=round(RAISE + AY - 0.255 - lvl(2), 4)), 'b_u2_port': b_wall('port', 2, ycut=round(RAISE + AY - 0.255 - lvl(2), 4)), 'b_parapet': b_wall('plain', 3, ycut=-99.0),
    'a_wall_plain': a_wall('plain'), 'a_wall_door': a_wall('door'), 'a_pier': a_pier(ATOP + 0.12),
    'aisle_floor': floor_slab(FZ0, CZ, H, nosing=False), 'orchestra_floor': floor_slab(ZO0, ZS, YO), 'stage': stage(), 'stage_steps': stage_steps(),
    'seat_row': seat_row(), 'proscenium': proscenium(), 'curtain_side': curtain_side(), 'valance': valance(), 'screen': screen(),
    'chandelier': chandelier(), 'sconce': sconce(), 'marquee': marquee(), 'blade_sign': blade(), 'booth': booth(), 'sidewalk': sidewalk(),
    'street_lamp': globe_lamp(), 'projector': projector(), 'counter': counter(),
    'door_leaf_entry': entry_leaf(), 'door_leaf_street': entry_leaf(0.96, 2.28), 'door_leaf_aud': door_padded(), 'door_leaf_exit': door_back(0.96, 2.36),
    'door_leaf_interior': door_interior(), 'exit_step': steps(0.8, 0.9, 1), 'wall_lantern': wall_lantern(), 'stair': stair(), 'stair_both': stair(True),
    'hvac': hvac(), 'vent': vent(), 'roof_drain': drain(),
    'iw_plain': interior_wall(False, H0 - 0.005), 'iw_doorway': interior_wall(True, H0 - 0.005), 'iw_end_plain': interior_wall(False, H0 - 0.005, end=True),
    'iw_end_doorway': interior_wall(True, H0 - 0.005, end=True), 'player_scale_ref': player_ref()}
for k in range(NT): pieces[f'tier_{k:02d}'] = floor_slab(*tier_z(k), tier_top(k))

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
TILE_N = {}
def tile_piece(kind, lv, rect, holes, trim):
    key = (kind, lv, rect, tuple(holes), trim)
    if key not in TILE_N:
        nm = f'floor_{kind}_{lv}' + ('_e' + ''.join(map(str, trim)) if any(trim) else ''); base = nm; i = 2
        while nm in pieces: nm = f'{base}_h{i}'; i += 1
        pieces[nm] = floor_tile(kind, lv, rect, holes, trim); TILE_N[key] = nm
    return TILE_N[key]
FM = list(range(-6, 7, 2)); FS = list(range(-1, 6, 2)); AS = list(range(-19, -2, 2))
OX0, OX1, OZ0, OZ1 = -FX, FX, FZ0, FZ1
# ---------- bloco da frente ----------
G0 = {-6: 'poster', -4: 'door', -2: 'doors', 0: 'doors', 2: 'doors', 4: 'vitrine', 6: 'door'}
for x in FM:
    put(f'f_g_{G0[x]}', x, lvl(0), FZ1, 0, ['front', 'ext', ftag(0)])
    put('f_u1_window', x, lvl(1), FZ1, 0, ['front', 'ext', ftag(1)]); put('f_u2_window', x, lvl(2), FZ1, 0, ['front', 'ext', ftag(2)])
    put('f_parapet', x, YR, FZ1, 0, ['front', 'roof'])
    put('b_g_plain', x, lvl(0), FZ0, 180, ['back', ftag(0)])
    put('b_u1_door' if x in (-2, 2) else 'b_u1_plain', x, lvl(1), FZ0, 180, ['back', ftag(1)]); put('b_u2_port' if x == 0 else 'b_u2_plain', x, lvl(2), FZ0, 180, ['back', ftag(2)])
    put('b_parapet', x, YR, FZ0, 180, ['back', 'roof'])
for z in FS:
    for (x, ry, tg) in ((-FX, -90, 'left'), (FX, 90, 'right')):
        put('s_g_window', x, lvl(0), z, ry, [tg, 'ext', ftag(0)]); put('s_u1_window', x, lvl(1), z, ry, [tg, 'ext', ftag(1)])
        put('s_u2_window', x, lvl(2), z, ry, [tg, 'ext', ftag(2)]); put('s_parapet', x, YR, z, ry, [tg, 'roof'])
for (x, ry, tg) in ((FX, 0, ('front', 'right')), (-FX, -90, ('left', 'front'))):
    for nm, fl in (('g', 0), ('u1', 1), ('u2', 2)): put(f'f_corner_{nm}', x, lvl(fl), FZ1, ry, list(tg) + ['ext', ftag(fl)])
    put('f_corner_p', x, YR, FZ1, ry, list(tg) + ['roof'])
for (x, ry, tg) in ((FX, 90, 'right'), (-FX, 180, 'left')):
    put('back_corner_g', x, lvl(0), FZ0, ry, [tg, ftag(0)]); put('back_corner_u', x, lvl(1), FZ0, ry, [tg, ftag(1)])
    put('back_corner_u', x, lvl(2), FZ0, ry, [tg, ftag(2)]); put('back_corner_p', x, YR, FZ0, ry, [tg, 'roof'])
# portas da frente
for x in (-2, 0, 2):
    hx, hz = hinge(x, FZ1, 0, -0.68, -0.16); put('door_leaf_entry', hx, Y0 + 0.013, hz, 0, ['front', 'ext', ftag(0)], door=85)
    hx, hz = hinge(x, FZ1, 0, 0.68, -0.16); put('door_leaf_entry', hx, Y0 + 0.013, hz, 180, ['front', 'ext', ftag(0)], door=-85)
for x in (-4, 6):
    hx, hz = hinge(x, FZ1, 0, -0.48, -0.16); put('door_leaf_street', hx, Y0 + 0.013, hz, 0, ['front', 'ext', ftag(0)], door=85)
for x in (-2, 2):
    hx, hz = hinge(x, FZ0, 180, -0.47, -0.15); put('door_leaf_aud', hx, lvl(1) + 0.013, hz, 180, [ftag(1)], door=-85)
put('marquee', 0, Y0, FZ1, 0, ['front', 'ext']); put('blade_sign', 3, Y0, FZ1, 0, ['front', 'ext'])
put('booth', 0, 0.03, FZ1 + 1.9, 0, ['front', 'street'])
for x in (-6.5, 6.5): put('street_lamp', x, 0.03, FZ1 + 3.0, 0, ['front', 'street'])
for x in range(-7, 8, 2): put('sidewalk', x, 0.0, FZ1, 0, ['street'])
put('counter', 2.4, Y0, 2.0, 0, [ftag(0)]); put('projector', 0.0, lvl(2), FZ0 + 1.0, 0, [ftag(2)])
# ---------- sala ----------
for z in AS:
    for (x, ry, tg) in ((-FX, -90, 'left'), (FX, 90, 'right')): put('a_wall_door' if z == ZEX else 'a_wall_plain', x, Y0, z, ry, [tg, 'ext', 'aud', ftag(0)])
for x in FM: put('a_wall_plain', x, Y0, AZ0, 180, ['back', 'ext', 'aud', ftag(0)])
put('a_pier', FX, Y0, AZ0, 90, ['back', 'right', 'aud', ftag(0)]); put('a_pier', -FX, Y0, AZ0, 180, ['back', 'left', 'aud', ftag(0)])
for (x, ry) in ((FX, 90), (-FX, -90)):
    hx, hz = hinge(x, ZEX, ry, -0.48, -0.15); put('door_leaf_exit', hx, Y0 + 0.013, hz, ry, ['aud', 'ext', ftag(0)], door=85)
    put('exit_step', x, Y0, ZEX, ry, ['ext']); put('wall_lantern', x, Y0 + 3.15, ZEX, ry, ['ext', 'aud'])
put('aisle_floor', 0, Y0, 0, 0, ['aud', ftag(0)]); put('orchestra_floor', 0, Y0, 0, 0, ['aud', ftag(0)]); put('stage', 0, Y0, 0, 0, ['aud', ftag(0)])
for k in range(NT):
    put(f'tier_{k:02d}', 0, Y0, 0, 0, ['aud', ftag(0)])
    for x in (-5, -3, 0, 3, 5): put('seat_row', x, Y0 + tier_top(k), tier_z(k)[1], 0, ['aud', ftag(0)])
for x in (-5, -3, 0, 3): put('seat_row', x, Y0 + YO, ZO0 - TD, 0, ['aud', ftag(0)])
for s in (-1, 1): put('stage_steps', s * 5.6, Y0 + YO, ZS, 0, ['aud', ftag(0)])
put('proscenium', 0, Y0, ZS - 0.5, 0, ['aud', ftag(0)])
put('curtain_side', -AX, Y0 + YS, ZS - 0.95, 0, ['aud', ftag(0)]); put('curtain_side', AX, Y0 + YS, ZS - 0.95, 180, ['aud', ftag(0)])
put('valance', 0, Y0 + VALY, ZS - 0.95, 0, ['aud', ftag(0)]); put('screen', 0, Y0, ZBK + 0.3, 0, ['aud', ftag(0)])
put('chandelier', 0, Y0 + AY - 0.255, -9.0, 0, ['aud', 'roof'])
for z in (-6.0, -10.0, -14.0):
    put('sconce', -AX, Y0 + 5.2, z, 90, ['aud', ftag(0)]); put('sconce', AX, Y0 + 5.2, z, -90, ['aud', ftag(0)])
# ---------- terracos ----------
for (x, z) in ((-3.0, -8.0), (0.0, -12.0), (3.0, -8.0)): put('hvac', x, Y0 + AY, z, 0, ['roof', 'aud'])
for (x, z, y) in ((-4.0, 2.0, YR), (-5.0, -16.0, Y0 + AY)): put('vent', x, y, z, 0, ['roof'])
for (x, z, y) in ((5.5, -18.5, Y0 + AY), (-5.5, -18.5, Y0 + AY), (5.5, -4.0, Y0 + AY), (-5.5, -4.0, Y0 + AY), (5.8, -0.8, YR)): put('roof_drain', x, y, z, 0, ['roof'])
# ---------- pisos ----------
HOLES = {1: [(LA[0], ZB, LA[1], ZA - 1.5)], 2: [(LB[0], ZB + 1.5, LB[1], ZA)]}
for fl in (0, 1, 2, 3):
    lv = 'g' if fl == 0 else ('r' if fl == 3 else 'u')
    for a in FM:
        for b in FS:
            tr = (int(a == FM[0]), int(a == FM[-1]), int(b == FS[0]), int(b == FS[-1])); hs = []
            for (x0, z0, x1, z1) in HOLES.get(fl, []):
                r = sbox(a - 1, b - 1, a + 1, b + 1).intersection(sbox(x0, z0, x1, z1))
                if r.area > 1e-6: bb = r.bounds; hs.append((round(bb[0] - a, 3), round(bb[1] - b, 3), round(bb[2] - a, 3), round(bb[3] - b, 3)))
            kind = 'membrane' if fl == 3 else ('marble' if fl == 0 and a <= 2 else 'floor')
            put(tile_piece(kind, lv, (-1, 1, -1, 1), hs, tr), a, lvl(fl), b, 0, [ftag(fl) if fl < 3 else 'roof'])
for a in FM:
    for b in AS:
        put(tile_piece('membrane', 'r', (-1, 1, -1, 1), [], (int(a == FM[0]), int(a == FM[-1]), int(b == AS[0]), 0)), a, Y0 + AY, b, 0, ['roof', 'aud'])
# ---------- escada, guarda-corpos, paredes internas ----------
put('stair', LA[0], lvl(0), ZA, 0, [ftag(0)]); put('stair_both', LB[1], lvl(1), ZB, 180, [ftag(1)])
def put_rail(fl, x0, z0, x1, z1, posts=(True, True)):
    Lr = round(abs(x1 - x0) + abs(z1 - z0), 3); nm = f'rail_{int(round(Lr * 100))}' + ('' if all(posts) else '_' + ''.join('1' if q else '0' for q in posts))
    if nm not in pieces: pieces[nm] = rail(Lr, posts)
    if abs(z1 - z0) < 1e-6: put(nm, min(x0, x1), lvl(fl), z0, 0, [ftag(fl)])
    else: put(nm, x0, lvl(fl), max(z0, z1), 90, [ftag(fl)])
XG = (LA[1] + LB[0]) / 2; XR = LB[1] + 0.1
put_rail(1, XG, ZB, XG, ZA - 1.5); put_rail(1, LA[0] + 0.05, ZA - 1.5, XG - 0.04, ZA - 1.5, (True, False))
put_rail(2, XG, ZB + 1.5, XG, ZA); put_rail(2, XR, ZB + 1.5, XR, ZA); put_rail(2, XG + 0.04, ZB + 1.5, XR - 0.04, ZB + 1.5, (False, False))
def wl(fl, x0, z0, x1, z1, doors=(), side=-1):
    """Paredes internas em modulos de 2 m; pontas que encostam nas paredes externas usam a versao 'end'.
    side: lado para onde as portas abrem (-1 = -Z/-X, 1 = +Z/+X)."""
    y = lvl(fl)
    if z0 == z1:
        for c in range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2):
            end = (c - 1 == OX0) or (c + 1 == OX1); d = c in doors; ry = 0 if (c + 1 == OX1 or not end) else 180
            put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), c, y, z0, ry, [ftag(fl)])
            if d:
                dr = 0 if side < 0 else 180; hx, hz = hinge(c, z0, dr, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, dr, [ftag(fl)], door=75)
    else:
        for c in range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2):
            end = (c - 1 == OZ0) or (c + 1 == OZ1); d = c in doors; ry = (90 if c - 1 == OZ0 else -90) if end else 90
            put('iw_' + ('end_' if end else '') + ('doorway' if d else 'plain'), x0, y, c, ry, [ftag(fl)])
            if d:
                hry = 90 if side < 0 else -90; hx, hz = hinge(x0, c, hry, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, hry, [ftag(fl)], door=90)
for fl, dl, dr in ((0, (1,), None), (1, (1,), (3,)), (2, (5,), (3,))):
    wl(fl, -3.0, OZ0, -3.0, OZ1, doors=dl, side=1)
    wl(fl, 3.0, OZ0, 3.0, OZ1, doors=dr or (), side=1)
put('player_scale_ref', 1.5, 0.03, 8.4); put('player_scale_ref', -1.0, Y0, 1.0, 0, [ftag(0)]); put('player_scale_ref', 1.5, Y0 + tier_top(5), tier_z(5)[1] + 0.2, 0, ['aud', ftag(0)])
if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    json.dump({'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE,
                        'front_block': {'x': [-FX, FX], 'z': [FZ0, FZ1], 'floors': 3, 'roof_level': YR},
                        'auditorium': {'x': [-FX, FX], 'z': [AZ0, FZ0], 'roof_level': RAISE + AY, 'tiers': NT, 'tier_depth': TD, 'tier_rise': TRS, 'stage_front_z': ZS},
                        'stair_holes': HOLES, 'roof': 'flat membrane roofs behind parapets', 'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
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
