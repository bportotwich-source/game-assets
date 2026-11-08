"""Kit 34: banco neoclassico de colunas, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Templo de 12 x 12 m em cantaria de calcario sobre embasamento de granito, com portico de 4 colunas jonicas (base atica, fuste
com 24 caneluras e entase, capitel com volutas e ovulos), antas nas quinas, entablamento completo (arquitrave de 3 faixas,
friso, cornija com denticulos) contornando o predio, frontao com timpano, medalhao liso e acroterios, telhado de cobre
patinado com juntas em pe e antefixas. Janelas em arco com moldura, impostas e chave; porta dupla de bronze com bandeira
gradeada e moldura com orelhas e cornija sobre misulas. Escadaria de granito em toda a frente, com pedestais e lanternas.
Dentro: salao de atendimento com piso xadrez de marmore, teto em caixotoes com pendentes, balcao dos caixas com grades de
latao, cofre com porta blindada e parede de cofres de aluguel, escritorio do gerente e corredor ate a porta dos fundos.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'stone': (226, 218, 200), 'carve': (232, 226, 210), 'granite': (150, 146, 140), 'patina': (96, 150, 126), 'bronze': (104, 80, 50),
                  'plaster': (240, 236, 226), 'marble': (236, 232, 224), 'marble2': (112, 104, 98), 'wood': (122, 76, 46), 'concrete': (184, 180, 172),
                  'steel': (150, 154, 158), 'grass': (100, 146, 72), 'hedge': (66, 104, 54), 'iron': (34, 36, 38), 'dark': (36, 36, 38),
                  'door': (96, 62, 40), 'clock': (246, 242, 230), 'soil': (90, 66, 48), 'door_int': (150, 100, 64), 'frame': (224, 218, 204), 'trim': (232, 226, 210)},
           texturas={'stone': 'stone', 'carve': 'plaster', 'granite': 'stone2', 'plaster': 'plaster', 'marble': 'plaster', 'marble2': 'plaster',
                     'wood': 'planks', 'concrete': 'render'},
           out=OUT)
D.METAL.update({'bronze'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.3; RAISE = 1.2; H = 6.3; YE = RAISE + H
HX = 6.0; ZB = -7.5; ZF = 4.5; ZP = 8.0           # corpo: x de -6 a 6, z de -7,5 a 4,5; portico ate z = 8
EH = 1.25; YC = YE + EH                            # entablamento e beiral
CPJ = 0.58                                          # projecao da cornija
ANG = 22.0; KR = math.tan(math.radians(ANG)); RISE = (HX + CPJ) * KR
COLX = (-5.6, -1.867, 1.867, 5.6); COLZ = 7.6; CR = 0.36; CH = H
XI = HX - T; ZBI = ZB + T; ZFI = ZF - T
ZPART = -2.5; YBC = 4.9                             # parede do fundo do salao e forro baixo da area de tras
NST = 8; RS = RAISE / NST; TRD = 0.32; ZST = 8.15   # escadaria da frente

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
def mitre_pair(p, mat, prof):
    """Canto externo de um perfil (z, y) que corre nas duas fachadas (pivo na quina, paredes em -X e -Z): 2 cunhas em meia-esquadria."""
    D_ = max(z for z, y in prof) + 0.001
    q = Piece(); prof_x(q, mat, 0.0, D_, prof); p.add(mat, slice_keep(q.parts[mat][0], [0, 0, 0], np.array([-1, 0, 1]) / math.sqrt(2)))
    q = Piece(); prof_z(q, mat, 0.0, D_, prof); p.add(mat, slice_keep(q.parts[mat][0], [0, 0, 0], np.array([1, 0, -1]) / math.sqrt(2)))
def arch_poly(w, y0, ys, grow=0.0):
    """Vao em arco pleno: retangulo de largura w de y0 ate a imposta ys, semicirculo em cima; grow = afastamento."""
    r = w / 2 + grow
    return unary_union([sbox(-r, y0 - grow, r, ys), Point(0, ys).buffer(r, 32)])
def as_xy(poly):   # poligono (x, y) para extrudar em z
    return poly

# ============================================================================ perfis do entablamento (z para fora, y a partir de YE)
ENT_PROF = [(0.0, 0.0), (0.03, 0.0), (0.03, 0.14), (0.05, 0.14), (0.05, 0.3), (0.07, 0.3), (0.07, 0.4), (0.1, 0.42), (0.1, 0.45),
            (0.03, 0.45), (0.03, 0.85), (0.08, 0.86), (0.12, 0.9), (0.12, 1.03), (0.5, 1.03), (0.5, 1.15), (0.53, 1.16), (CPJ, 1.22),
            (CPJ, EH), (0.0, EH)]
ARCH_IN = [(0.0, 0.0), (0.03, 0.0), (0.03, 0.14), (0.05, 0.14), (0.05, 0.3), (0.07, 0.3), (0.07, 0.4), (0.1, 0.42), (0.1, 0.45), (0.0, 0.45)]
def dentils(p, x0, x1, z=0.12, y0=0.93, y1=1.03, step=0.125, w=0.075, d=0.08):
    n = int(round((x1 - x0) / step))
    for i in range(n):
        xc = x0 + (i + 0.5) * (x1 - x0) / n; p.box('carve', xc - w / 2, xc + w / 2, y0, y1, z, z + d)
def ent_module():
    """Entablamento de 2 m (pivo: face externa da parede, cota YE): arquitrave de 3 faixas, friso liso, cornija com denticulos,
    corona e cimalha; corpo macico ate a face interna."""
    p = Piece()
    prof_x(p, 'carve', -W / 2, W / 2, [(-T + 0.02, 0.0)] + ENT_PROF + [(-T + 0.02, EH)])
    dentils(p, -W / 2, W / 2)
    return p
def ent_corner():
    p = Piece(); e = 0.004
    p.box('carve', -T + 0.004, e, 0.003, EH - 0.003, -T + 0.004, e)
    mitre_pair(p, 'carve', ENT_PROF)
    p.box('carve', -0.02, 0.2, 0.93, 1.03, 0.12, 0.2); p.box('carve', 0.12, 0.2, 0.93, 1.03, -0.02, 0.12)
    return p

# ============================================================================ paredes
STONE_Y = (0.0, H)                                  # cantaria do piso ao entablamento
PL_TOP = 0.55
PLINTH = lambda y0: [(0.0, y0), (0.05, y0), (0.05, PL_TOP - 0.1), (0.07, PL_TOP - 0.08), (0.07, PL_TOP - 0.04), (0.04, PL_TOP), (0.0, PL_TOP + 0.02)]
SILL_C = [(0.0, 0.86), (0.04, 0.86), (0.04, 0.96), (0.06, 0.98), (0.06, 1.0), (0.0, 1.0)]
def layered(p, holes_poly, y0, top):
    """Parede de 2 m em 2 camadas (cantaria por fora, gesso por dentro) com vaos (poligono em x, y) recortados no Blender."""
    cut = []
    for g in getattr(holes_poly, 'geoms', [holes_poly]) if holes_poly is not None else []:
        if g.area < 1e-6: continue
        m = trimesh.creation.extrude_polygon(g, 1.0); m.apply_translation([0, 0, -0.6]); cut.append(m)
    so = tbox(-W / 2, W / 2, y0, top, -T + 0.02, 0.0); pl = tbox(-W / 2, W / 2, y0, top - 0.005, -T, -T + 0.02)
    if cut:
        p.add('stone', bl_detail(so, cut, bevel=0.0)); p.add('plaster', bl_detail(pl, cut, bevel=0.0))
    else: p.add('stone', so); p.add('plaster', pl)
AW, AY0, AYS = 1.4, 1.0, 4.0                         # janela em arco: largura, peitoril, imposta
def arch_window(p):
    """Caixilho de madeira bronzeada no vao em arco (face externa em z = 0): aro, pinazios (retos e radiais), vidro, peitoril
    de pedra com misulas, moldura com impostas e chave."""
    outer = arch_poly(AW, AY0, AYS); inner = arch_poly(AW - 0.12, AY0 + 0.06, AYS)
    ext(p, 'bronze', outer.difference(inner), -0.2, -0.12)
    ext(p, 'glass', inner.buffer(0.004), -0.164, -0.156)
    r = AW / 2 - 0.06
    for x in (0.0,): p.box('bronze', x - 0.02, x + 0.02, AY0 + 0.06, AYS, -0.18, -0.14)
    for y in (2.0, 3.0, AYS): p.box('bronze', -r, r, y - 0.02, y + 0.02, -0.18, -0.14)
    for a in (math.radians(45), math.radians(135)):
        q = Piece(); q.box('bronze', 0.0, r, -0.02, 0.02, -0.18, -0.14)
        M = trimesh.transformations.rotation_matrix(a, [0, 0, 1]); M[:3, 3] = [0, AYS, 0]; p.merge(q, M)
    p.box('bronze', -0.02, 0.02, AYS, AYS + r, -0.18, -0.14)
    ext(p, 'bronze', Point(0, AYS).buffer(0.22, 20).difference(Point(0, AYS).buffer(0.18, 20)).intersection(sbox(-1, AYS, 1, AYS + 1)), -0.18, -0.14)
    # moldura, impostas, chave, peitoril
    band = arch_poly(AW, AY0, AYS, 0.16).difference(arch_poly(AW, AY0, AYS)).intersection(sbox(-2, AY0, 2, 9))
    ext(p, 'carve', band, 0.0, 0.04)
    for s in (-1, 1):
        a, b = sorted((s * (AW / 2 - 0.0), s * (AW / 2 + 0.22))); p.cham('carve', a, b, AYS - 0.14, AYS, 0.0, 0.06, 0.008)
    kt = Polygon([(-0.11, AYS + AW / 2 - 0.04), (0.11, AYS + AW / 2 - 0.04), (0.15, AYS + AW / 2 + 0.3), (-0.15, AYS + AW / 2 + 0.3)])
    ext(p, 'carve', kt, 0.0, 0.08)
    p.cham('carve', -AW / 2 - 0.2, AW / 2 + 0.2, AY0 - 0.1, AY0 + 0.004, -0.005, 0.1, 0.01)
    for s in (-1, 1):
        x = s * (AW / 2 + 0.08); p.hull('carve', [(x + dx, y, z) for dx in (-0.06, 0.06) for (z, y) in ((0.0, AY0 - 0.1), (0.08, AY0 - 0.1), (0.0, AY0 - 0.32))])
    p.box('wood', -AW / 2 - 0.03, AW / 2 + 0.03, AY0 - 0.03, AY0 + 0.02, -T - 0.04, -0.2)
RW, RY0, RY1 = 1.4, 1.0, 4.6                         # janela retangular da frente
def rect_window(p):
    """Janela retangular sob o portico: caixilho de guilhotina com pinazios, moldura com orelhas e cornija sobre misulas."""
    x = RW / 2; f = 0.06
    for (a, b, c, d) in ((-x, -x + f, RY0, RY1), (x - f, x, RY0, RY1), (-x + f, x - f, RY1 - f, RY1), (-x + f, x - f, RY0, RY0 + f), (-x + f, x - f, 2.76, 2.84)):
        p.box('bronze', a, b, c, d, -0.2, -0.12)
    for y in (1.6, 2.2, 3.4, 4.0): p.box('bronze', -x + f, x - f, y - 0.015, y + 0.015, -0.18, -0.15)
    for xx in (-0.21, 0.21): p.box('bronze', xx - 0.015, xx + 0.015, RY0 + f, RY1 - f, -0.18, -0.15)
    p.box('glass', -x + f, x - f, RY0 + f, RY1 - f, -0.164, -0.156)
    ring = sbox(-x - 0.16, RY0, x + 0.16, RY1 + 0.16).difference(sbox(-x, RY0, x, RY1))
    ears = unary_union([sbox(-x - 0.22, RY1 - 0.12, -x - 0.15, RY1 + 0.16), sbox(x + 0.15, RY1 - 0.12, x + 0.22, RY1 + 0.16)])
    ext(p, 'carve', unary_union([ring, ears]), 0.0, 0.04)
    p.box('carve', -x - 0.22, x + 0.22, RY1 + 0.16, RY1 + 0.42, 0.0, 0.03)
    prof_x(p, 'carve', -x - 0.34, x + 0.34, [(0.0, RY1 + 0.42), (0.1, RY1 + 0.42), (0.14, RY1 + 0.48), (0.14, RY1 + 0.56), (0.18, RY1 + 0.6), (0.18, RY1 + 0.64), (0.0, RY1 + 0.64)])
    for s in (-1, 1):
        xx = s * (x + 0.26); p.hull('carve', [(xx + dx, y, z) for dx in (-0.05, 0.05) for (z, y) in ((0.0, RY1 + 0.42), (0.12, RY1 + 0.42), (0.0, RY1 + 0.0), (0.04, RY1 + 0.02))])
    p.cham('carve', -x - 0.12, x + 0.12, RY0 - 0.08, RY0 + 0.004, -0.005, 0.08, 0.008)
    p.box('wood', -x - 0.03, x + 0.03, RY0 - 0.03, RY0 + 0.02, -T - 0.04, -0.2)
DW, DH = 1.1, 4.4                                   # meia largura do vao da porta principal e altura
def wall(kind='plain', side='s'):
    """Modulo de 2 m de parede (pivo: face externa, cota do piso). side 's' (laterais e fundos, embasamento de granito desde o
    chao) ou 'f' (frente, sob o portico, sobre o estilobato). kind: plain, arch, rect, door_l / door_r (metades da porta
    principal), bdoor (porta dos fundos)."""
    p = Piece(); y0 = -RAISE if side == 's' else 0.0; top = H
    hp = None; gaps = []
    if kind == 'arch': hp = arch_poly(AW, AY0, AYS)
    if kind == 'rect': hp = sbox(-RW / 2, RY0, RW / 2, RY1)
    if kind in ('door_l', 'door_r'):
        s = 1 if kind == 'door_l' else -1; a, b = sorted((s * (1.0 - DW), s * 1.0)); hp = sbox(a, 0.0, b, DH); gaps = [(a, b)]
    if kind == 'bdoor': hp = sbox(-0.55, 0.0, 0.55, 2.6); gaps = [(-0.68, 0.68)]
    layered(p, hp, y0, top)
    if kind == 'arch': arch_window(p)
    if kind == 'rect': rect_window(p)
    if kind in ('door_l', 'door_r'):
        s = 1 if kind == 'door_l' else -1
        X = lambda v: s * v
        def bx(mat, xa, xb, *r):
            a, b = sorted((X(xa), X(xb))); p.box(mat, a, b, *r)
        bx('bronze', 1.0 - DW, 1.0 - DW + 0.08, 0.0, DH, -0.24, -0.12)                      # batente
        bx('bronze', 1.0 - DW + 0.08, 1.0, DH - 0.08, DH, -0.24, -0.12)                     # verga
        bx('bronze', 1.0 - DW + 0.08, 1.0, 3.22, 3.32, -0.24, -0.12)                        # travessa da bandeira
        bx('glass', 1.0 - DW + 0.08, 1.0, 3.32, DH - 0.08, -0.184, -0.176)
        for k in range(4):                                                                  # grade da bandeira
            xx = 1.0 - DW + 0.08 + (k + 0.5) * (DW - 0.08) / 4; bx('bronze', xx - 0.012, xx + 0.012, 3.32, DH - 0.08, -0.17, -0.15)
        bx('bronze', 1.0 - DW + 0.08, 1.0, 3.84, 3.86, -0.17, -0.15)
        q = Piece(); q.cyl('bronze', 0.09, -0.01, 0.01, 0, 0, 16)
        # moldura com orelhas e cornija
        ring = sbox(X(1.0 - DW - 0.22), 0.0, X(1.0), DH + 0.22) if s > 0 else sbox(X(1.0), 0.0, X(1.0 - DW - 0.22), DH + 0.22)
        hole = sbox(*sorted((X(1.0 - DW), X(1.0))), 0.0, DH) if False else sbox(min(X(1.0 - DW), X(1.0)), 0.0, max(X(1.0 - DW), X(1.0)), DH)
        ring = ring.difference(hole)
        ear = sbox(*sorted((X(1.0 - DW - 0.3), X(1.0 - DW - 0.2))), DH - 0.16, DH + 0.22) if False else sbox(min(X(1.0 - DW - 0.3), X(1.0 - DW - 0.2)), DH - 0.16, max(X(1.0 - DW - 0.3), X(1.0 - DW - 0.2)), DH + 0.22)
        ext(p, 'carve', unary_union([ring, ear]), 0.0, 0.05)
        a, b = sorted((X(1.0 - DW - 0.3), X(1.0))); p.box('carve', a, b, DH + 0.22, DH + 0.5, 0.0, 0.035)
        a, b = sorted((X(1.0 - DW - 0.44), X(1.0))); prof_x(p, 'carve', a, b, [(0.0, DH + 0.5), (0.12, DH + 0.5), (0.16, DH + 0.56), (0.16, DH + 0.66), (0.21, DH + 0.71), (0.21, DH + 0.76), (0.0, DH + 0.76)])
        xx = X(1.0 - DW - 0.36); p.hull('carve', [(xx + dx, y, z) for dx in (-0.06, 0.06) for (z, y) in ((0.0, DH + 0.5), (0.14, DH + 0.5), (0.0, DH - 0.1), (0.05, DH - 0.08))])
        a, b = sorted((X(1.0 - DW), X(1.0))); p.box('granite', a, b, -0.004 if False else 0.0 - 0.0, 0.006, -T, 0.04) if False else p.box('granite', a, b, -0.06, 0.006, -T + 0.004, 0.04)
    if kind == 'bdoor':
        p.box('bronze', -0.55, -0.49, 0.0, 2.6, -0.2, -0.1); p.box('bronze', 0.49, 0.55, 0.0, 2.6, -0.2, -0.1); p.box('bronze', -0.49, 0.49, 2.54, 2.6, -0.2, -0.1)
        p.box('bronze', -0.49, 0.49, 2.24, 2.3, -0.2, -0.1); p.box('glass', -0.49, 0.49, 2.3, 2.54, -0.154, -0.146)
        ext(p, 'carve', sbox(-0.7, 0.0, 0.7, 2.75).difference(sbox(-0.55, 0.0, 0.55, 2.6)), 0.0, 0.04)
        prof_x(p, 'carve', -0.82, 0.82, [(0.0, 2.75), (0.1, 2.75), (0.14, 2.8), (0.14, 2.86), (0.0, 2.86)])
        p.box('granite', -0.55, 0.55, -0.06, 0.006, -T + 0.004, 0.04)
    if side == 's':
        segs = [(-W / 2, W / 2)]
        for (a, b) in gaps: segs = [s_ for (c, d) in segs for s_ in ((c, min(d, a)), (max(c, b), d)) if s_[1] - s_[0] > 1e-3]
        for (a, b) in segs: prof_x(p, 'granite', a, b, PLINTH(y0))
        if kind not in ('bdoor',): prof_x(p, 'carve', -W / 2, W / 2, SILL_C) if kind != 'arch' else [prof_x(p, 'carve', a, b, SILL_C) for (a, b) in ((-W / 2, -AW / 2 - 0.2), (AW / 2 + 0.2, W / 2))]
        else:
            for (a, b) in ((-W / 2, -0.7), (0.7, W / 2)): prof_x(p, 'carve', a, b, SILL_C)
    else:
        base = [(0.0, 0.0), (0.05, 0.0), (0.05, 0.25), (0.03, 0.3), (0.0, 0.3)]
        segs = [(-W / 2, W / 2)]
        if kind in ('door_l', 'door_r'):
            s = 1 if kind == 'door_l' else -1; a, b = sorted((s * -1.0, s * (1.0 - DW - 0.22))); segs = [(a, b)]
        for (a, b) in segs:
            if b - a > 0.01: prof_x(p, 'granite', a, b, base)
    return p
def corner():
    """Quina dos fundos (pivo: quina externa, cota do piso; paredes em -X e -Z): nucleo, embasamento e faixa de peitoril."""
    p = Piece(); e = 0.004
    p.box('stone', -T + 0.004, e, -RAISE + 0.003, H - 0.004, -T + 0.004, e)
    mitre_pair(p, 'granite', PLINTH(-RAISE)); mitre_pair(p, 'carve', SILL_C)
    return p
AN = 0.7; AP = 0.1                                  # largura e saliencia da anta
def anta():
    """Anta (pilastra de quina do portico; pivo: quina externa na cota do piso, paredes em -X e -Z): fuste em L saliente 10 cm,
    base atica e capitel com cimalha e abaco, ambos em meia-esquadria; embasamento de granito por baixo da base."""
    p = Piece()
    shaft = unary_union([sbox(-AN, -T + 0.004, AP, AP), sbox(-T + 0.004, -AN, AP, AP)])
    ext_y(p, 'stone', Polygon([(x, z) for (x, z) in shaft.exterior.coords]) if False else shaft, 0.003, H - 0.003)
    for (prof, mat) in (([(AP, 0.0), (AP + 0.06, 0.0), (AP + 0.06, 0.1), (AP + 0.04, 0.14), (AP + 0.04, 0.2), (AP, 0.24)], 'carve'),
                        ([(AP, H - 0.42), (AP + 0.03, H - 0.4), (AP + 0.05, H - 0.32), (AP + 0.05, H - 0.26), (AP + 0.08, H - 0.2), (AP + 0.08, H - 0.003), (AP, H - 0.003)], 'carve')):
        q = Piece(); prof_x(q, mat, -AN, AP + 0.1, prof); p.add(mat, slice_keep(q.parts[mat][0], [AP, 0, AP], np.array([-1, 0, 1]) / math.sqrt(2)))
        q = Piece(); prof_z(q, mat, -AN, AP + 0.1, prof); p.add(mat, slice_keep(q.parts[mat][0], [AP, 0, AP], np.array([1, 0, -1]) / math.sqrt(2)))
    return p

# ============================================================================ coluna jonica
def column():
    """Coluna jonica (pivo: centro, no estilobato): plinto, base atica (toro, escocia, toro), fuste com 24 caneluras e entase,
    astragalo, equino com ovulos, almofada com volutas na frente e atras, abaco."""
    p = Piece(); r0 = CR; r1 = CR * 0.84; h = CH
    p.cham('carve', -0.46, 0.46, 0.0, 0.12, -0.46, 0.46, 0.008)
    lathe(p, 'carve', [(0.44, 0.12), (0.45, 0.16), (0.43, 0.2), (0.4, 0.21), (0.38, 0.24), (0.4, 0.27), (0.41, 0.3), (0.39, 0.33), (0.37, 0.34)], sec=28)
    # fuste canelado: secao com 24 caneluras, extrudada e afinada (entase)
    n = 24; pts = []
    for i in range(n):
        a0 = 2 * math.pi * i / n; a1 = 2 * math.pi * (i + 1) / n
        for t in np.linspace(0, 1, 5)[:-1]:
            a = a0 + (a1 - a0) * t; rr = 1.0 - 0.06 * math.sin(math.pi * min(1, max(0, (t - 0.12) / 0.76)))
            pts.append((rr * math.cos(a), rr * math.sin(a)))
    sec = Polygon(pts); ys0, ys1 = 0.34, h - 0.62
    m = trimesh.creation.extrude_polygon(sec, ys1 - ys0, engine='earcut') if False else trimesh.creation.extrude_polygon(sec, ys1 - ys0)
    v = m.vertices.copy(); t = v[:, 2] / (ys1 - ys0)
    rad = r0 * (1 - 0.16 * t ** 1.6)
    m.vertices = np.stack([v[:, 0] * rad, ys0 + v[:, 2], v[:, 1] * rad], 1); m.invert(); p.add('carve', D._fix(m))
    lathe(p, 'carve', [(r1 + 0.03, h - 0.62), (r1 + 0.035, h - 0.6), (r1 + 0.03, h - 0.58), (r1 + 0.005, h - 0.57)], sec=28)
    # equino com ovulos
    lathe(p, 'carve', [(r1 + 0.005, h - 0.57), (r1 + 0.06, h - 0.5), (r1 + 0.07, h - 0.44), (r1 + 0.04, h - 0.4), (0.0, h - 0.4)], sec=28)
    for k in range(16):
        a = 2 * math.pi * k / 16; rr = r1 + 0.06
        p.sphere('carve', 0.04, rr * math.cos(a), h - 0.48, rr * math.sin(a), 1)
    # almofada (pulvino) e volutas: espirais de gomos decrescentes nas faces z = +-
    L = 0.5; p.box('carve', -L, L, h - 0.4, h - 0.24, -0.3, 0.3)
    for s in (-1, 1):
        x = s * (L - 0.04); seg_cyl(p, 'carve', (x, h - 0.42, -0.31), (x, h - 0.42, 0.31), 0.13, 16)
        for zf in (-0.31, 0.31):
            for k in range(14):
                a = k * 0.62; rr = 0.17 * (1 - k / 16)
                xx = x + s * 0.0 + rr * math.cos(a) * 0.9; yy = h - 0.42 + rr * math.sin(a) * 0.9
                p.sphere('carve', 0.028 + 0.01 * (1 - k / 14), xx, yy, zf + (0.012 if zf > 0 else -0.012), 1)
            p.cyl('carve', 0.035, 0, 0, 0, 0) if False else None
            p.sphere('carve', 0.045, x, h - 0.42, zf + (0.02 if zf > 0 else -0.02), 1)
    # abaco
    p.cham('carve', -0.48, 0.48, h - 0.24, h - 0.16, -0.42, 0.42, 0.01)
    prof_x(p, 'carve', -0.5, 0.5, [(-0.44, h - 0.16), (0.44, h - 0.16), (0.46, h - 0.1), (0.46, h), (-0.46, h), (-0.46, h - 0.1)]) if False else p.cham('carve', -0.5, 0.5, h - 0.16, h - 0.003, -0.46, 0.46, 0.02)
    return p

# ============================================================================ entablamento do portico, frontao, telhado
def portico_ent():
    """Entablamento do portico (pivo: face da fachada da frente no eixo, cota YE): viga da frente e vigas laterais com o perfil
    completo por fora (quinas em meia-esquadria), arquitrave por dentro, faixa na parede do fundo e forro de caixotoes."""
    p = Piece(); D_ = ZP - ZF; bw = 0.8
    def cut(m, c, nrm): return slice_keep(m, c, np.array(nrm, float) / np.linalg.norm(nrm))
    # viga da frente: perfil completo em z = D_ (para fora), corpo ate D_ - bw
    q = Piece(); prof_x(q, 'carve', -HX - CPJ - 0.01, HX + CPJ + 0.01, [(z + D_, y) for (z, y) in ENT_PROF] + [(D_ - bw, EH), (D_ - bw, 0.0)])
    m = q.parts['carve'][0]; m = cut(m, [HX, 0, D_], [-1, 0, 1]); m = cut(m, [-HX, 0, D_], [1, 0, 1]); p.add('carve', m)
    dentils(p, -HX + 0.1, HX - 0.1, z=D_ + 0.12)
    for s in (-1, 1):
        q = Piece(); prof_z(q, 'carve', 0.0, D_ + CPJ + 0.01, [(s * (HX + z) if True else 0, y) for (z, y) in ENT_PROF] + [(s * (HX - bw), EH), (s * (HX - bw), 0.0)])
        m = q.parts['carve'][0]; m = cut(m, [s * HX, 0, D_], [s * 1, 0, -1]); p.add('carve', m)
        dentils_z = Piece(); dentils(dentils_z, 0.1, D_ - 0.1)
        M = trimesh.transformations.rotation_matrix(-s * math.pi / 2, [0, 1, 0]); M[:3, 3] = [s * HX, 0, 0]; p.merge(dentils_z, M)
        p.box('carve', s * HX - 0.2 if s > 0 else -HX + 0.12, s * HX - 0.12 if s > 0 else -HX + 0.2, 0.93, 1.03, D_ + 0.12, D_ + 0.2) if False else None
        a, b = sorted((s * (HX + 0.12), s * (HX + 0.2))); p.box('carve', a, b, 0.93, 1.03, D_ + 0.12, D_ + 0.2)
    # arquitrave por dentro (viga da frente e vigas laterais) e faixa na parede do fundo
    prof_x(p, 'carve', -HX + bw, HX - bw, [(D_ - bw - z, y) for (z, y) in ARCH_IN][::-1])
    for s in (-1, 1):
        prof_z(p, 'carve', 0.0, D_ - bw, [(s * (HX - bw - z), y) for (z, y) in ARCH_IN][::(-1 if s > 0 else 1)])
    prof_x(p, 'carve', -HX + bw, HX - bw, ARCH_IN)
    # forro: laje e caixotoes (3 x 5)
    x0, x1, z0, z1 = -HX + bw, HX - bw, 0.0, D_ - bw
    p.box('carve', x0, x1, 0.45, 0.6, z0, z1)
    nx, nz = 5, 2
    for i in range(nx + 1):
        x = x0 + i * (x1 - x0) / nx
        if 0 < i < nx: p.box('carve', x - 0.1, x + 0.1, 0.25, 0.45, z0 + 0.1, z1 - 0.1)
    for j in range(nz + 1):
        z = z0 + j * (z1 - z0) / nz
        if 0 < j < nz: p.box('carve', x0 + 0.1, x1 - 0.1, 0.25, 0.45, z - 0.1, z + 0.1)
    for i in range(nx):
        for j in range(nz):
            a = x0 + i * (x1 - x0) / nx + 0.1; b = x0 + (i + 1) * (x1 - x0) / nx - 0.1; c = z0 + j * (z1 - z0) / nz + 0.1; d = z0 + (j + 1) * (z1 - z0) / nz - 0.1
            if i == 0: a = x0 + 0.1
            ext_y(p, 'carve', sbox(a + 0.04, c + 0.04, b - 0.04, d - 0.04).difference(sbox(a + 0.1, c + 0.1, b - 0.1, d - 0.1)), 0.39, 0.45)
            p.cyl('carve', 0.06, 0.4, 0.45, (a + b) / 2, (c + d) / 2, 12)
    p.box('carve', x0, x0 + 0.1, 0.25, 0.45, z0, z1); p.box('carve', x1 - 0.1, x1, 0.25, 0.45, z0, z1)
    p.box('carve', x0, x1, 0.25, 0.45, z1 - 0.1, z1); p.box('carve', x0, x1, 0.25, 0.45, z0 + 0.07, z0 + 0.1)
    return p
PK = KR
def pediment(recess=0.15, front=True):
    """Frontao (pivo: plano da face do entablamento, eixo, cota YC): timpano recuado, cornija inclinada (corona e cimalha) sobre
    o telhado, medalhao liso no timpano, acroterios de palmeta no topo e nas pontas."""
    p = Piece(); R = HX + CPJ
    tri = Polygon([(-HX, 0.0), (HX, 0.0), (0.0, HX * PK)])
    ext(p, 'stone', tri, -T - 0.6, -recess)
    if front:
        ext(p, 'carve', Point(0, HX * PK * 0.4).buffer(0.62, 32).difference(Point(0, HX * PK * 0.4).buffer(0.5, 32)), -recess, -recess + 0.06)
        ext(p, 'carve', Point(0, HX * PK * 0.4).buffer(0.5, 32), -recess, -recess + 0.025)
        for s in (-1, 1):   # ramos (guirlanda) dos lados do medalhao
            for k in range(6):
                a = math.radians(200 + k * 14) if s < 0 else math.radians(-20 - k * 14)
                xx = s * 0.0 + 0.8 * math.cos(a) * (1 if s > 0 else 1); yy = HX * PK * 0.4 + 0.5 * math.sin(a)
                p.sphere('carve', 0.07, xx, yy, -recess + 0.03, 1)
    # cornija inclinada: perfil perpendicular a agua, varrido de cada ponta ao topo
    cp = [(0.0, 0.0), (0.0, 0.3), (CPJ - 0.1, 0.3), (CPJ - 0.06, 0.34), (CPJ, 0.4), (CPJ, 0.44), (-0.6, 0.44), (-0.6, 0.0)]
    for s in (-1, 1):
        a0 = (s * (R - 0.004), -0.0); a1 = (0.0, R * PK)
        pts = []
        for (x, y) in (a0, a1):
            for (dz, dy) in cp: pts.append((x, y + dy - 0.02, dz))
        p.hull('carve', pts)
    # acroterios
    for (x, y) in ((0.0, R * PK + 0.4), (-R + 0.25, 0.42), (R - 0.25, 0.42)):
        p.cham('carve', x - 0.22, x + 0.22, y, y + 0.2, -0.15, 0.25, 0.01)
        pal = unary_union([Point(x + 0.16 * math.cos(a), y + 0.2 + 0.28 + 0.16 * math.sin(a)).buffer(0.08, 10) for a in np.linspace(math.radians(20), math.radians(160), 5)] + [sbox(x - 0.07, y + 0.2, x + 0.07, y + 0.5)])
        ext(p, 'carve', pal, 0.02, 0.08)
    return p
def palmette():
    """Antefixa de palmeta (pivo: base, no beiral): folhas em leque sobre base com voluta."""
    p = Piece()
    pal = unary_union([Point(0.13 * math.cos(a), 0.1 + 0.13 * math.sin(a)).buffer(0.055, 8) for a in np.linspace(math.radians(15), math.radians(165), 7)] + [sbox(-0.06, 0.0, 0.06, 0.12)])
    ext(p, 'carve', pal, -0.02, 0.02)
    return p
SPAN = HX + CPJ
def roof_strip():
    """Faixa de 2 m de telhado de cobre (pivo: face da parede, cota YC; beiral em z = CPJ, sobe para -Z ate a cumeeira em z = -HX):
    chapa, 4 juntas em pe, friso de beiral e 2 antefixas."""
    p = Piece(); f = lambda a, b: KR * (CPJ - b)
    poly = sbox(-W / 2, -HX, W / 2, CPJ)
    sheared(p, 'patina', poly, 0.0, 0.035, f)
    for xc in (-0.75, -0.25, 0.25, 0.75):
        p.hull('patina', [(x, f(0, z) + dy, z) for x in (xc - 0.012, xc + 0.012) for z in (CPJ, -HX) for dy in (0.03, 0.075)])
    seg_cyl(p, 'patina', (-W / 2, 0.02, CPJ + 0.005), (W / 2, 0.02, CPJ + 0.005), 0.025, 10)
    q = palmette()
    for x in (-0.5, 0.5):
        M = trimesh.transformations.translation_matrix([x, 0.05, CPJ - 0.05]); p.merge(q, M)
    return p
def ridge():
    p = Piece(); y = RISE + 0.035
    seg_cyl(p, 'patina', (0.0, y + 0.02, ZB - 0.5), (0.0, y + 0.02, ZP), 0.08, 14)
    for z in np.arange(ZB - 0.5 + 0.5, ZP, 1.0):
        q = palmette(); M = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]); M[:3, 3] = [0.0, y + 0.08, z]; p.merge(q, M)
    return p

# ============================================================================ estilobato, escadarias
def podium():
    """Estilobato e escadaria de granito (pivo: origem do mundo): plataforma do portico com piso de marmore, 8 degraus em toda a
    largura, cimalha na borda, pedestais nas pontas da escadaria."""
    p = Piece(); x0, x1 = -HX - 0.3, HX + 0.3
    p.box('granite', x0, x1, 0.0, RAISE - 0.03, ZF, ZST)
    for i in range(int((ZST - ZF) / 0.6) + 1):
        for j in range(int((x1 - x0) / 0.6)):
            a, b = x0 + 0.15 + j * 0.6, x0 + 0.15 + (j + 1) * 0.6; c, d = ZF + i * 0.6, ZF + (i + 1) * 0.6
            q = sbox(a + 0.003, c + 0.003, b - 0.003, d - 0.003).intersection(sbox(x0 + 0.15, ZF, x1 - 0.15, ZST - 0.15))
            ext_y(p, 'marble' if (i + j) % 2 == 0 else 'marble2', q, RAISE - 0.03, RAISE)
    ext_y(p, 'granite', sbox(x0, ZF, x1, ZST).difference(sbox(x0 + 0.15, ZF, x1 - 0.15, ZST - 0.15)), RAISE - 0.03, RAISE)
    ext_y(p, 'dark', sbox(x0 + 0.15, ZF, x1 - 0.15, ZST - 0.15), RAISE - 0.03, RAISE - 0.006)
    for s in (-1, 1):
        a, b = sorted((s * (HX + 0.3), s * (HX + 0.36))); p.box('granite', a, b, RAISE - 0.12, RAISE - 0.02, ZF, ZST)
    for k in range(1, NST):
        y = RAISE - k * RS; z0 = ZST + (k - 1) * TRD
        p.box('granite', x0, x1, 0.0, y, z0, z0 + TRD + 0.02)
        p.box('granite', x0, x1, y - 0.02, y, z0 + TRD, z0 + TRD + 0.03) if False else None
    for s in (-1, 1):
        a, b = sorted((s * (HX + 0.3), s * (HX + 1.0))); zc0, zc1 = ZST + (NST - 2) * TRD - 0.4, ZST + (NST - 1) * TRD
        p.box('granite', a, b, 0.0, 0.85, zc0, zc1)
        p.cham('granite', a - 0.04, b + 0.04, 0.85, 0.95, zc0 - 0.04, zc1 + 0.04, 0.01)
        p.hull('granite', [(x, y, z) for x in (a, b) for (z, y) in ((ZF, 0.0), (ZF, RAISE - 0.12), (zc0, 0.95), (zc0, 0.0))]) if False else p.box('granite', a, b, 0.0, RAISE - 0.12, ZF + 0.6, zc0)
    return p
def back_steps():
    """Patamar e 8 degraus de granito na porta dos fundos (pivo: face da parede, eixo, no chao; descem para +Z) com corrimaos de ferro."""
    p = Piece(); w = 0.85; d = 1.3
    p.box('granite', -w, w, 0.0, RAISE, 0.0, d)
    for k in range(1, NST):
        y = RAISE - k * RS; z0 = d + (k - 1) * 0.3
        p.box('granite', -w, w, 0.0, y, z0 - 0.002, z0 + 0.3)
    zend = d + (NST - 1) * 0.3
    for s in (-1, 1):
        x = s * (w - 0.06)
        seg_cyl(p, 'iron', (x, RAISE + 0.95, 0.1), (x, RAISE + 0.95, d), 0.022, 8)
        seg_cyl(p, 'iron', (x, RAISE + 0.95, d), (x, 0.95 + RS, zend - 0.2), 0.022, 8)
        for z in np.arange(0.2, d, 0.15): seg_cyl(p, 'iron', (x, RAISE, z), (x, RAISE + 0.95, z), 0.009, 6)
        for k in range(1, NST):
            z = d + (k - 0.5) * 0.3; y = RAISE - k * RS; yt = RAISE + 0.95 - (z - d) * RS / 0.3
            if z < zend - 0.2: seg_cyl(p, 'iron', (x, y, z), (x, yt, z), 0.009, 6)
        seg_cyl(p, 'iron', (x, 0.0 + RS, zend - 0.2), (x, 0.95 + RS, zend - 0.2), 0.025, 10); p.sphere('iron', 0.04, x, 0.95 + RS + 0.03, zend - 0.2, 1)
    return p

# ============================================================================ interior
def run_wall(Ln, h, door_at=None, ow=0.86, t=0.15, end_gap=(0.016, 0.016)):
    p = Piece(); xs = [0.0, Ln]; c = door_at
    if c is not None: xs = [0.0, c - ow / 2, c + ow / 2, Ln]
    for m, mesh in grid_solid(xs, [0.0, 2.1, h], [-t / 2, t / 2], lambda i, j, k: None if (c is not None and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    segs = [(end_gap[0], Ln - end_gap[1])]
    if c is not None:
        q = Piece(); door_casing(q, ow, t); p.merge(q, trimesh.transformations.translation_matrix([c, 0, 0]))
        segs = [(end_gap[0], c - ow / 2 - 0.09), (c + ow / 2 + 0.09, Ln - end_gap[1])]
    for a, b in segs:
        if b - a > 0.02: baseboard(p, a, b, t)
    return p
def floor_tile(kind, trim=(0, 0, 0, 0)):
    """Piso de 2 x 2 m: xadrez de marmore de 50 cm ('marble'), tabuas ('wood') ou concreto ('vault')."""
    p = Piece(); x0, x1, z0, z1 = -1 + trim[0], 1 - trim[1], -1 + trim[2], 1 - trim[3]
    sq = sbox(x0, z0, x1, z1)
    if kind == 'marble':
        s = 0.5
        for i in range(4):
            for j in range(4):
                q = sbox(-1 + i * s, -1 + j * s, -1 + (i + 1) * s, -1 + (j + 1) * s).intersection(sq)
                ext_y(p, 'marble' if (i + j) % 2 == 0 else 'marble2', q, -0.03, 0.0)
    elif kind == 'wood': ext_y(p, 'wood', sq, -0.03, 0.0)
    else: ext_y(p, 'concrete', sq, -0.03, 0.0)
    ext_y(p, 'granite', sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0)), -RAISE + 0.02, -0.03)
    return p
def coffers():
    """Teto de caixotoes do salao (pivo: origem, cota do piso; teto em H): laje de gesso, vigas em grelha de 4 x 4 com molduras
    e roseta em cada caixotao."""
    p = Piece(); x0, x1, z0, z1 = -XI, XI, ZPART + 0.075, ZFI
    p.box('plaster', x0, x1, H, H + 0.15, z0, z1)
    nx, nz = 6, 4
    xs = [x0 + i * (x1 - x0) / nx for i in range(nx + 1)]; zs = [z0 + j * (z1 - z0) / nz for j in range(nz + 1)]
    for x in xs[1:-1]: p.box('plaster', x - 0.14, x + 0.14, H - 0.4, H, z0, z1)
    for z in zs[1:-1]: p.box('plaster', x0, x1, H - 0.4, H, z - 0.14, z + 0.14)
    for i in range(nx):
        for j in range(nz):
            a, b, c, d = xs[i] + (0.14 if i else 0.0), xs[i + 1] - (0.14 if i < nx - 1 else 0.0), zs[j] + (0.14 if j else 0.0), zs[j + 1] - (0.14 if j < nz - 1 else 0.0)
            ext_y(p, 'trim', sbox(a, c, b, d).difference(sbox(a + 0.08, c + 0.08, b - 0.08, d - 0.08)), H - 0.08, H)
            p.cyl('trim', 0.14, H - 0.04, H, (a + b) / 2, (c + d) / 2, 16)
    return p
def pendant(drop=2.4):
    p = Piece(); p.cyl('bronze', 0.12, -0.04, 0.0, 0, 0, 14)
    seg_cyl(p, 'bronze', (0, -0.04, 0), (0, -drop + 0.4, 0), 0.012, 6)
    lathe(p, 'bronze', [(0.04, -drop + 0.4), (0.12, -drop + 0.33), (0.12, -drop + 0.3)], sec=14)
    p.sphere('lamp_glass', 0.24, 0.0, -drop + 0.08, 0.0, 2)
    return p
def teller(Ln=9.3):
    """Balcao dos caixas (pivo: ponta x0, frente para +Z, no piso): base de marmore com rodape escuro, tampo de madeira, grades de
    latao com guiches a cada 1,55 m e prateleira por dentro."""
    p = Piece(); d = 0.6
    p.box('marble', 0.0, Ln, 0.1, 1.05, -d, 0.0); p.box('marble2', 0.0, Ln, 0.0, 0.1, -d + 0.02, 0.02)
    for i in range(int(Ln / 0.775)):
        x = (i + 0.5) * Ln / int(Ln / 0.775); p.box('marble2', x - 0.25, x + 0.25, 0.3, 0.85, 0.0, 0.012)
    p.cham('wood', -0.03, Ln + 0.03, 1.05, 1.1, -d - 0.05, 0.06, 0.01)
    n = int(Ln / 1.55)
    for i in range(n + 1):
        x = i * Ln / n; p.box('bronze', x - 0.03, x + 0.03, 1.1, 2.3, -0.3, -0.24)
    p.box('bronze', 0.0, Ln, 2.27, 2.33, -0.3, -0.24)
    for i in range(n):
        a = i * Ln / n + 0.03; b = (i + 1) * Ln / n - 0.03; c = (a + b) / 2
        for xx in np.arange(a + 0.06, b - 0.03, 0.06):
            if abs(xx - c) > 0.24: p.cyl('bronze', 0.006, 1.1, 2.27, xx, -0.27, 6)
        p.box('bronze', c - 0.25, c + 0.25, 1.48, 1.52, -0.3, -0.24); p.box('bronze', c - 0.25, c - 0.22, 1.1, 1.52, -0.3, -0.24); p.box('bronze', c + 0.22, c + 0.25, 1.1, 1.52, -0.3, -0.24)
        for xx in np.arange(c - 0.2, c + 0.21, 0.06): p.cyl('bronze', 0.006, 1.52, 2.27, xx, -0.27, 6)
    p.box('wood', 0.0, Ln, 0.8, 0.84, -d - 0.4, -d)
    return p
def vault_door():
    """Porta do cofre (pivo: dobradica, embaixo; vai para +X): chapa de aco espessa, aneis, volante de 4 bracos, segredo e trincos."""
    p = Piece(); w = 1.0; h = 2.05; t = 0.22
    p.cham('steel', 0.0, w, 0.0, h, -t / 2, t / 2, 0.02)
    c = (w / 2, 1.05)
    for r in (0.42, 0.3): ext(p, 'steel', Point(c).buffer(r + 0.03, 32).difference(Point(c).buffer(r, 32)), t / 2, t / 2 + 0.02)
    p.cyl('steel', 0.05, 0, 0, 0, 0) if False else None
    for k in range(4):
        q = Piece(); q.box('bronze', -0.24, 0.24, -0.015, 0.015, t / 2 + 0.06, t / 2 + 0.08)
        M = trimesh.transformations.rotation_matrix(k * math.pi / 4, [0, 0, 1]); M[:3, 3] = [c[0], c[1], 0]; p.merge(q, M)
    seg_cyl(p, 'bronze', (c[0], c[1], t / 2), (c[0], c[1], t / 2 + 0.09), 0.04, 12)
    seg_cyl(p, 'dark', (c[0], c[1] + 0.55, t / 2), (c[0], c[1] + 0.55, t / 2 + 0.03), 0.08, 16)
    for y in (0.3, 1.0, 1.75): p.cyl('steel', 0.05, y, y + 0.22, 0.0, 0.0, 12)
    return p
def deposit_boxes(Ln=2.0, h=2.4):
    """Parede de cofres de aluguel (pivo: inicio, encostada na parede, no piso; frente para +Z): gabinete de aco com portinholas
    numeradas por plaquinhas lisas e fechaduras."""
    p = Piece(); d = 0.45
    p.box('steel', 0.0, Ln, 0.0, h, 0.0, d)
    nx, ny = int(Ln / 0.3), int((h - 0.2) / 0.2)
    for i in range(nx):
        for j in range(ny):
            a = 0.05 + i * (Ln - 0.1) / nx; b = a + (Ln - 0.1) / nx - 0.012; c = 0.15 + j * 0.2; e = c + 0.188
            p.box('steel', a, b, c, e, d, d + 0.008)
            p.box('bronze', (a + b) / 2 - 0.03, (a + b) / 2 + 0.03, c + 0.14, c + 0.165, d + 0.008, d + 0.011)
            p.cyl('dark', 0.009, 0, 0, 0, 0) if False else p.box('dark', (a + b) / 2 - 0.008, (a + b) / 2 + 0.008, c + 0.06, c + 0.08, d + 0.008, d + 0.012)
    return p
def back_ceiling():
    """Forro baixo da area de tras (pivo: origem, cota do piso)."""
    p = Piece(); p.box('plaster', -XI, XI, YBC, YBC + 0.2, ZBI, ZPART - 0.075); return p

# ============================================================================ terreno
def lawn(x0, x1, z0, z1, holes=()):
    p = Piece(); g = sbox(x0, z0, x1, z1)
    for hh in holes: g = g.difference(hh)
    ext_y(p, 'grass', g, 0.002, 0.03); return p
def sidewalk(poly, y1=0.06, joint=1.5):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2] + 1e-6, joint):
        q = sbox(x + 0.005, b[1], x + joint - 0.005, b[3]).intersection(poly); ext_y(p, 'concrete', q, 0.0, y1)
    ext_y(p, 'dark', poly.buffer(-0.003), 0.0, y1 - 0.008)
    return p
def lantern_post(h=1.5):
    """Poste de bronze com lanterna (pivo: base, sobre o pedestal): base, fuste canelado, lanterna de 4 vidros e pinha."""
    p = Piece(); lathe(p, 'bronze', [(0.12, 0.0), (0.12, 0.08), (0.06, 0.16), (0.045, 0.3), (0.035, h - 0.1), (0.07, h)], sec=12)
    p.box('bronze', -0.14, 0.14, h, h + 0.04, -0.14, 0.14)
    for (x, z) in ((-0.12, -0.12), (0.12, -0.12), (-0.12, 0.12), (0.12, 0.12)): p.box('bronze', x - 0.015, x + 0.015, h + 0.04, h + 0.5, z - 0.015, z + 0.015)
    p.box('lamp_glass', -0.11, 0.11, h + 0.06, h + 0.48, -0.11, 0.11)
    p.hull('bronze', [(x, h + 0.5, z) for x in (-0.17, 0.17) for z in (-0.17, 0.17)] + [(0, h + 0.68, 0)])
    p.sphere('bronze', 0.04, 0, h + 0.71, 0, 1)
    return p
def street_clock(h=3.6):
    """Relogio de rua (pivo: base, no chao): pedestal, coluna de ferro, caixa com 2 mostradores (marcas e ponteiros, sem numeros)."""
    p = Piece(); lathe(p, 'iron', [(0.28, 0.0), (0.28, 0.2), (0.2, 0.3), (0.12, 0.5), (0.1, h - 0.6), (0.16, h - 0.5)], sec=14)
    c = h; R = 0.4
    seg_cyl(p, 'iron', (0, c, -0.12), (0, c, 0.12), R + 0.06, 24)
    for s in (-1, 1):
        z = s * 0.125; seg_cyl(p, 'clock', (0, c, z), (0, c, z + s * 0.01), R, 24)
        for k in range(12):
            a = k * math.pi / 6; r0 = R - (0.1 if k % 3 == 0 else 0.06)
            q = Piece(); q.box('dark', r0, R - 0.03, -0.012, 0.012, -0.004, 0.004)
            M = trimesh.transformations.rotation_matrix(a, [0, 0, 1]); M[:3, 3] = [0, c, z + s * 0.014]; p.merge(q, M)
        for (a, L, w) in ((math.radians(120), 0.2, 0.02), (math.radians(30), 0.3, 0.014)):
            q = Piece(); q.box('dark', -0.03, L, -w, w, -0.004, 0.004)
            M = trimesh.transformations.rotation_matrix(a, [0, 0, 1]); M[:3, 3] = [0, c, z + s * 0.02]; p.merge(q, M)
    p.sphere('iron', 0.12, 0, c + R + 0.1, 0, 1)
    return p
def bench():
    p = Piece(); L1 = 1.8
    for s in (-1, 1):
        x = s * 0.75; p.box('iron', x - 0.03, x + 0.03, 0.0, 0.42, -0.25, 0.25); p.box('iron', x - 0.03, x + 0.03, 0.42, 0.85, -0.25, -0.2)
    for i in range(4): z = -0.2 + i * 0.105; p.cham('wood', -L1 / 2, L1 / 2, 0.42, 0.46, z, z + 0.09, 0.006)
    for y in (0.58, 0.72): p.cham('wood', -L1 / 2, L1 / 2, y, y + 0.1, -0.245, -0.205, 0.006)
    return p
def urn():
    """Vaso de pedra com arbusto (pivo: base, no chao)."""
    p = Piece(); lathe(p, 'carve', [(0.3, 0.0), (0.3, 0.1), (0.14, 0.18), (0.12, 0.35), (0.38, 0.55), (0.42, 0.8), (0.44, 0.86), (0.36, 0.86)], sec=20)
    p.cyl('soil', 0.37, 0.8, 0.84, 0, 0, 20)
    p.sphere('hedge', 0.38, 0, 1.15, 0, 2)
    for k in range(5): a = k * 1.25; p.sphere('hedge', 0.22, 0.25 * math.cos(a), 1.0 + 0.15 * (k % 2), 0.25 * math.sin(a), 1)
    return p
def bush(r=0.5):
    p = Piece(); rng = np.random.default_rng(3)
    p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def street_lamp(h=4.2):
    p = Piece(); lathe(p, 'iron', [(0.2, 0.0), (0.2, 0.3), (0.1, 0.45), (0.07, h - 0.3), (0.12, h - 0.2)], sec=12)
    p.sphere('lamp_glass', 0.24, 0, h + 0.1, 0, 2); p.cyl('iron', 0.08, h + 0.32, h + 0.38, 0, 0, 10)
    return p

# ============================================================================ pecas
pieces = {
    'ent': ent_module(), 'ent_corner': ent_corner(), 'portico_ent': portico_ent(), 'pediment_front': pediment(0.15, True), 'pediment_back': pediment(0.0, False),
    'roof_strip': roof_strip(), 'ridge': ridge(), 'column': column(), 'anta': anta(), 'corner': corner(), 'podium': podium(), 'back_steps': back_steps(),
    'coffers': coffers(), 'pendant': pendant(), 'teller': teller(), 'vault_door': vault_door(), 'deposit_boxes': deposit_boxes(), 'back_ceiling': back_ceiling(),
    'door_leaf_interior': door_interior(0.82, 2.06), 'door_leaf_back': D.door_back(1.0, 2.22), 'lantern_post': lantern_post(), 'street_clock': street_clock(),
    'bench': bench(), 'urn': urn(), 'bush': bush(), 'street_lamp': street_lamp(), 'player_scale_ref': player_ref()}
for k in ('plain', 'arch', 'bdoor'): pieces[f's_{k}'] = wall(k, 's')
for k in ('plain', 'rect', 'door_l', 'door_r'): pieces[f'f_{k}'] = wall(k, 'f')
def bronze_leaf(w=1.03, h=3.2, t=0.07):
    """Folha da porta principal de bronze (pivo: dobradica, embaixo; vai para +X): 3 almofadas com molduras e rosetas, vidro com
    grade no alto, puxador vertical e espelho de fechadura."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.16, w - 0.16, 2.0, h - 0.18, -t, t)] + [tbox(0.16, w - 0.16, y0, y1, z - 0.012, z + 0.012) for (y0, y1) in ((0.2, 0.9), (1.05, 1.85)) for z in (t / 2, -t / 2)]
    p.add('bronze', bl_detail(slab, cut, bevel=0.006, segments=2))
    p.box('glass', 0.156, w - 0.156, 1.996, h - 0.176, -0.004, 0.004)
    for xx in np.arange(0.24, w - 0.16, 0.1): p.cyl('bronze', 0.008, 2.0, h - 0.18, xx, 0.0, 6)
    for (y0, y1) in ((0.2, 0.9), (1.05, 1.85)):
        for z in (1, -1): p.cyl('bronze', 0.05, 0, 0, 0, 0) if False else seg_cyl(p, 'bronze', ((w) / 2, (y0 + y1) / 2, z * (t / 2 - 0.012)), (w / 2, (y0 + y1) / 2, z * (t / 2 + 0.01)), 0.07, 12)
    for z in (1, -1):
        x = w - 0.1; seg_cyl(p, 'bronze', (x, 0.9, z * (t / 2 + 0.07)), (x, 1.7, z * (t / 2 + 0.07)), 0.022, 10)
        for y in (0.95, 1.65): seg_cyl(p, 'bronze', (x, y, z * t / 2), (x, y, z * (t / 2 + 0.07)), 0.012, 8)
    return p
pieces['door_leaf_bronze'] = bronze_leaf()

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
Y0 = RAISE
SIDE = {-6.5: 'plain', -4.5: 'arch', -2.5: 'plain', -0.5: 'plain', 1.5: 'arch', 3.5: 'plain'}
BACK = {-5: 'plain', -3: 'arch', -1: 'plain', 1: 'bdoor', 3: 'arch', 5: 'plain'}
FRONT = {-5: 'plain', -3: 'rect', -1: 'door_l', 1: 'door_r', 3: 'rect', 5: 'plain'}
for z, k in SIDE.items():
    put(f's_{k}', -HX, Y0, z, -90, ['left', 'ext']); put(f's_{k}', HX, Y0, z, 90, ['right', 'ext'])
for x, k in BACK.items(): put(f's_{k}', x, Y0, ZB, 180, ['back', 'ext'])
for x, k in FRONT.items(): put(f'f_{k}', x, Y0, ZF, 0, ['front', 'ext'])
put('corner', HX, Y0, ZB, 90, ['ext']); put('corner', -HX, Y0, ZB, 180, ['ext'])
put('anta', HX, Y0, ZF, 0, ['front', 'ext']); put('anta', -HX, Y0, ZF, -90, ['front', 'ext'])
for x in COLX: put('column', x, Y0, COLZ, 0, ['front', 'ext'])
# entablamento
for z in SIDE:
    put('ent', -HX, YE, z, -90, ['roof']); put('ent', HX, YE, z, 90, ['roof'])
for x in BACK: put('ent', x, YE, ZB, 180, ['roof'])
put('ent_corner', HX, YE, ZB, 90, ['roof']); put('ent_corner', -HX, YE, ZB, 180, ['roof'])
put('portico_ent', 0.0, YE, ZF, 0, ['front', 'roof'])
put('pediment_front', 0.0, YC, ZP, 0, ['front', 'roof']); put('pediment_back', 0.0, YC, ZB, 180, ['roof'])
for z in np.arange(ZB - 0.5 + 1.0, ZP, 2.0):
    put('roof_strip', HX, YC, float(z), 90, ['roof']); put('roof_strip', -HX, YC, float(z), -90, ['roof'])
put('ridge', 0.0, YC, 0.0, 0, ['roof'])
# portas
hx, hz = hinge(-DW + 0.0 - 0.0, ZF, 0, 0.0 - 0.0, -0.18); put('door_leaf_bronze', -DW + 0.08, Y0 + 0.006, hz, 0, ['front', 'ext'], door=90)
put('door_leaf_bronze', DW - 0.08, Y0 + 0.006, hz, 180, ['front', 'ext'], door=-90)
hx, hz = hinge(1.0, ZB, 180, -0.49, -0.15); put('door_leaf_back', hx, Y0 + 0.006, hz, 180, ['back', 'ext'], door=-90)
put('podium', 0, 0, 0, 0, ['site']); put('back_steps', 1.0, 0.0, ZB, 180, ['site'])
# interior
HI = H - 0.005
def tile(kind, trim):
    nm = f'floor_{kind}' + ('_e' + '_'.join(str(int(round(t * 100))) for t in trim) if any(trim) else '')
    if nm not in pieces: pieces[nm] = floor_tile(kind, trim)
    return nm
XM = [-5, -3, -1, 1, 3, 5]; ZM = [-6.5, -4.5, -2.5, -0.5, 1.5, 3.5]
for x in XM:
    for z in ZM:
        tr = (T if x == XM[0] else 0.0, T if x == XM[-1] else 0.0, T if z == ZM[0] else 0.0, T if z == ZM[-1] else 0.0)
        kind = 'marble'
        if z <= -4.5: kind = 'vault' if x < 0 else ('marble' if x == 1 else 'wood')
        put(tile(kind, tuple(round(t, 3) for t in tr)), x, Y0, z, 0, ['floor0'])
# parede do fundo do salao (z = ZPART) e divisorias da area de tras
segs = [(-XI, 0.0, -XI / 2 - 0.0, 1.2), (0.0, 2.0, 1.0, 0.86), (2.0, XI, (2.0 + XI) / 2, 0.86)]
for (a, b, c, ow) in segs:
    Ln = round(b - a, 3); nm = f'pw_{int(round(Ln * 100))}_{int(round((c - a) * 100))}_{int(ow * 100)}'
    if nm not in pieces: pieces[nm] = run_wall(Ln, HI, door_at=round(c - a, 3), ow=ow)
    put(nm, a, Y0, ZPART, 0, ['floor0'])
hx, hz = hinge(1.0, ZPART, 0, -0.41, 0); put('door_leaf_interior', hx, Y0 + 0.01, hz, 0, ['floor0'], door=90)
hx, hz = hinge((2.0 + XI) / 2, ZPART, 0, -0.41, 0); put('door_leaf_interior', hx, Y0 + 0.01, hz, 0, ['floor0'], door=90)
put('vault_door', -XI / 2 - 0.5, Y0 + 0.004, ZPART + 0.075 + 0.11, 0, ['floor0'], door=-100)
LP = round(ZPART - 0.075 - ZBI, 3); nm = f'pz_{int(round(LP * 100))}'
pieces[nm] = run_wall(LP, YBC)
for x in (0.0, 2.0): put(nm, x, Y0, ZPART - 0.075, 90, ['floor0'])
put('back_ceiling', 0, Y0, 0, 0, ['floor0', 'roof'])
put('coffers', 0, Y0, 0, 0, ['floor0', 'roof'])
for (x, z) in ((-3.0, 2.2), (3.0, 2.2), (-3.0, -0.6), (3.0, -0.6)): put('pendant', x, Y0 + H - 0.4, z, 0, ['floor0'])
put('teller', -XI, Y0, 0.5, 0, ['floor0'])
put('deposit_boxes', -3.6, Y0, ZPART - 0.075, 180, ['floor0'])
# terreno
ZS0 = ZST + (NST - 1) * TRD
pieces['sidewalk'] = sidewalk(sbox(-11.0, ZS0, 11.0, ZS0 + 3.0))
pieces['lawn_l'] = lawn(-11.0, -HX - 0.3, ZB - 4.0, ZS0, [sbox(-HX - 1.0, ZS0 - 2.4, -HX - 0.3, ZS0)])
pieces['lawn_r'] = lawn(HX + 0.3, 11.0, ZB - 4.0, ZS0, [sbox(HX + 0.3, ZS0 - 2.4, HX + 1.0, ZS0)])
pieces['lawn_b'] = lawn(-HX - 0.3, HX + 0.3, ZB - 4.0, ZB, [sbox(1.0 - 0.85, ZB - 1.3 - (NST - 1) * 0.3, 1.0 + 0.85, ZB)])
pieces['lawn_m'] = lawn(-HX - 0.3, HX + 0.3, ZB, ZF, [sbox(-HX, ZB, HX, ZF)])
for nm in ('sidewalk', 'lawn_l', 'lawn_r', 'lawn_b', 'lawn_m'): put(nm, 0, 0, 0, 0, ['site'])
for s in (-1, 1): put('lantern_post', s * (HX + 0.65), 0.95, ZST + (NST - 2) * TRD - 0.4 + (ZS0 - (ZST + (NST - 2) * TRD - 0.4)) / 2, 0, ['site'])
put('street_clock', -4.5, 0.06, ZS0 + 1.6, 0, ['site'])
for x in (-8.5, 8.5): put('street_lamp', x, 0.06, ZS0 + 2.4, 0, ['site'])
put('bench', 4.0, 0.06, ZS0 + 2.2, 180, ['site']); put('bench', -8.0, 0.06, ZS0 + 1.2, 180, ['site'])
for s in (-1, 1): put('urn', s * 8.0, 0.03, ZS0 - 1.2, 0, ['site'])
for z in (-6.0, -3.0, 0.0, 3.0):
    put('bush', -HX - 0.8, 0.03, z, 0, ['site']); put('bush', HX + 0.8, 0.03, z, 0, ['site'])
put('player_scale_ref', -3.0, 0.06, ZS0 + 1.0); put('player_scale_ref', 2.0, Y0, 2.0, 0, ['floor0'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_height': H, 'wall_thickness': T, 'floor_raise': RAISE,
                       'building': {'x': [-HX, HX], 'z': [ZB, ZF], 'portico_front': ZP, 'entablature_level': YE, 'eave_level': YC, 'ridge_level': YC + RISE, 'roof_pitch_deg': ANG},
                       'roof': 'patinated copper standing seam, 22 deg gable with pediments',
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
