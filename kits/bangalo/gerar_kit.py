"""Kit 7: bangalo terreo de 14 x 12 m em ALTO DETALHE (refeito no padrao do piloto, com scripts/detalhe/detalhe.py).
Tabuas e telhas em geometria, janelas de guilhotina, calhas e condutores, portas de almofada (Blender), lanternas e texturas PBR.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'siding': (118, 146, 104), 'shingles': (64, 66, 74), 'deck': (150, 104, 70), 'floor': (176, 128, 86), 'brick': (166, 80, 60),
                  'ceiling': (206, 226, 224)},
           texturas={'siding': 'siding', 'brick': 'brick', 'shingles': 'shingles', 'plaster': 'plaster', 'deck': 'deck', 'floor': 'planks', 'cap': 'plaster'},
           out=OUT)

# ============================================================================ grade, paredes
W = 2.0; T = 0.3; H = 3.0; SLAB = 0.2; RAISE = 0.45
def lvl(fl): return RAISE + fl * H
FRIEZE = 2.72; HW = H + 0.03; FT = H; WT = 0.12      # topo da testeira do rodape (water table)
NC = 13; EXPO = (FRIEZE - WT) / NC; LAP = 0.03; TB = 0.024; TT = 0.007   # fiadas, exposicao, sobreposicao, espessura em baixo/em cima
configurar_tabuas(WT, FRIEZE, 0.2)
# ---------- testeira do rodape, friso sob o beiral ----------
def water_table(p, x0=-W / 2, x1=W / 2):
    p.box('brick', x0, x1, -RAISE, 0.0, -T, 0.0)
    # tabua com pingadeira chanfrada em cima: esconde a borda da laje e joga a agua para fora
    prof_x(p, 'trim', x0, x1, [(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)])
def frieze(p, x0=-W / 2, x1=W / 2):
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE), (0.034, FRIEZE), (0.034, FT), (0.0, FT)])
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE - 0.05), (0.03, FRIEZE - 0.035), (0.042, FRIEZE - 0.012), (0.042, FRIEZE + 0.02), (0.0, FRIEZE + 0.02)])  # cimalha

# ---------- janela de guilhotina craftsman ----------
def wall_siding_window():
    p = Piece(); wall_with_opening(p, 'siding', 1.1, 0.8, 2.3, HW); hole = window(p, 1.1, 0.8, 2.3, 3)
    siding_field(p, [hole]); water_table(p); frieze(p); return p
def wall_siding_small_window():
    p = Piece(); wall_with_opening(p, 'siding', 0.6, 1.5, 2.3, HW); hole = window(p, 0.6, 1.5, 2.3, 2)
    siding_field(p, [hole]); water_table(p); frieze(p); return p
def wall_siding_plain():
    p = Piece(); wall_with_opening(p, 'siding', 0, 0, 0, HW); siding_field(p); water_table(p); frieze(p); return p
def wall_siding_window_hood():
    """Janela com cobertura de telhas sobre maos-francesas (fachada lateral)."""
    p = wall_siding_window(); x = 0.85; y0 = 2.66; y1 = 2.38; d = 0.7; kk = (y0 - y1) / d
    p.box('trim', -x, x, y0 - 0.03, y0 + 0.02, 0.04, 0.09)                                 # sarrafo de apoio na parede
    hull_pts = lambda yb, yt: [(xx, y, z) for xx in (-x, x) for (z, y) in ((0.05, y0 + yb), (0.05, y0 + yt), (d, y1 + yb), (d, y1 + yt))]
    p.hull('plaster', [(xx * 0.994, y, z) for (xx, y, z) in hull_pts(0.0, 0.02)])
    for i in range(4):   # 4 fiadas de telha com degrau
        za = 0.05 + i * (d - 0.05) / 4; zb = za + (d - 0.05) / 4 + 0.02
        ya = lambda z: y0 - kk * (z - 0.05)
        p.hull('shingles', [(xx, ya(z) + dy, z) for xx in (-x - 0.02, x + 0.02) for (z, dy) in ((za, 0.02), (za, 0.04), (min(zb, d), 0.02), (min(zb, d), 0.04 + 0.02 * (zb > d)))])
    p.cham('trim', -x - 0.02, x + 0.02, y1 - 0.13, y1 + 0.02, d - 0.03, d + 0.02, 0.006)   # testeira
    for s in (-1, 1):   # mao-francesa: braco, escora diagonal e ponta recortada
        xa, xb = sorted((s * (x - 0.13), s * (x - 0.05)))
        p.cham('trim', xa, xb, 1.98, y0 - 0.03, 0.036, 0.1, 0.008)
        p.cham('trim', xa, xb, y1 - 0.14, y1 - 0.02, 0.1, d - 0.03, 0.008)
        p.seg('trim', ((xa + xb) / 2, 2.08, 0.1), ((xa + xb) / 2, y1 - 0.12, d - 0.16), 0.06, 0.07)
    return p
def wall_siding_door():
    p = Piece(); ow = 1.0; x = ow / 2; oy0 = 0.015; oy1 = 2.3
    wall_with_opening(p, 'siding', ow, oy0, oy1, HW)
    p.box('frame', -x, -x + 0.07, oy0, oy1, -0.24, 0.0); p.box('frame', x - 0.07, x, oy0, oy1, -0.24, 0.0); p.box('frame', -x, x, oy1 - 0.07, oy1, -0.24, 0.0)
    p.box('frame', -x + 0.07, -x + 0.085, oy0, oy1 - 0.07, -0.2, -0.16); p.box('frame', x - 0.085, x - 0.07, oy0, oy1 - 0.07, -0.2, -0.16)   # batente de encosto
    prof_x(p, 'cap', -x + 0.07, x - 0.07, [(-0.24, 0.012), (0.03, 0.012), (0.05, 0.0), (0.05, -0.03), (-0.24, -0.03)])   # soleira de pedra com nariz
    p.box('brick', -W / 2, W / 2, -RAISE, -0.03, -T, 0.0); p.box('brick', -W / 2, -x, -0.03, 0.0, -T, 0.0); p.box('brick', x, W / 2, -0.03, 0.0, -T, 0.0)
    for (a, b) in ((-W / 2, -x - 0.12), (x + 0.12, W / 2)):
        prof_x(p, 'trim', a, b, [(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)])
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x + 0.12)))
        prof_y(p, 'trim', -0.03, oy1 + 0.025, crect(a, b, 0.0, 0.036, 0.006, (0, 0, 1, 1)))
        a, b = sorted((s * (x + 0.005), s * (x + 0.125)))
        p.cham('trim', a, b, -0.06, 0.16, 0.0, 0.05, 0.008)          # pe da guarnicao (plinto)
    prof_x(p, 'trim', -x - 0.14, x + 0.14, crect(0.0, 0.04, oy1 + 0.025, oy1 + 0.2, 0.006, (0, 1, 1, 0)))
    prof_x(p, 'trim', -x - 0.17, x + 0.17, [(0.0, oy1 + 0.2), (0.075, oy1 + 0.2), (0.075, oy1 + 0.225), (0.05, oy1 + 0.245), (0.0, oy1 + 0.255)])
    siding_field(p, [(-x - 0.03, x + 0.03, -1.0, oy1 + 0.05)]); frieze(p); return p
def corner_siding():
    """Cantoneira dupla (duas tabuas que se cruzam no canto, quinas chanfradas) + canto do rodape de tijolo."""
    p = Piece(); e = 0.045
    prof_y(p, 'trim', 0.0, FT, [(-T - 0.01, -T - 0.01), (e, -T - 0.01), (e, e - 0.006), (e - 0.006, e), (-T - 0.01, e)])
    p.box('brick', -T - 0.01, 0.01, -RAISE, 0, -T - 0.01, 0.01)
    prof_y(p, 'trim', -0.1, 0.092, [(-T, -T), (e + 0.062, -T), (e + 0.062, e + 0.062), (-T, e + 0.062)])
    p.hull('trim', [(x, y, z) for (x, z) in ((-T, -T), (e + 0.062, -T), (e + 0.062, e + 0.062), (-T, e + 0.062)) for y in (0.092, 0.104)] +
           [(x, 0.118, z) for (x, z) in ((-T, -T), (e, -T), (e, e), (-T, e))])
    prof_y(p, 'trim', FRIEZE - 0.05, FRIEZE + 0.02, [(-T, -T), (e + 0.012, -T), (e + 0.012, e + 0.012), (-T, e + 0.012)])
    return p
def ceiling_tile():
    p = Piece(); p.box('plaster', -W / 2, W / 2, -SLAB, 0, -W / 2, W / 2); return p

# ---------- degraus de tijolo com bocel ----------
def brick_steps(w=1.36, rise=0.15, run=0.3, n=2, cheeks=True):
    """Degraus de tijolo com pisos de pedra de bocel arredondado e muretas laterais. Pivo: borda de cima, centro; desce para +Z."""
    p = Piece()
    for i in range(n):
        top = -(i + 1) * rise; z0, z1 = i * run, (i + 1) * run
        p.box('brick', -w / 2, w / 2, -RAISE, top - 0.04, z0, z1 - 0.02)
        nose = arc(z1 + 0.012, top - 0.02, 0.02, -math.pi / 2, math.pi / 2, 6)
        prof_x(p, 'cap', -w / 2 + 0.002, w / 2 - 0.002, [(z0, top - 0.04)] + nose + [(z0, top)])
    if cheeks:
        L = n * run + 0.05
        for s in (-1, 1):
            a, b = sorted((s * (w / 2), s * (w / 2 + 0.22)))
            p.box('brick', a, b, -RAISE, -0.05, 0.0, L)
            p.hull('cap', [(xx, y, z) for xx in (a - 0.02 * (s < 0), b + 0.02 * (s > 0)) for (z, y) in ((0.0, -0.05), (0.0, 0.0), (L + 0.03, -0.05), (L + 0.03, -0.035))])
    return p

# ---------- lareira, chamine ----------
def fireplace():
    p = Piece(); w = 0.8; d = 0.5
    p.box('brick', -w, w, 0, 1.2, 0, d)
    prof_x(p, 'trim', -w - 0.12, w + 0.12, [(0.0, 1.2), (d + 0.1, 1.2), (d + 0.12, 1.215), (d + 0.12, 1.26), (d + 0.09, 1.28), (0.0, 1.28)])  # cornija
    for s in (-1, 1):
        a, b = sorted((s * (w - 0.02), s * (w - 0.12)))
        p.hull('trim', [(x, y, z) for x in (a, b) for (z, y) in ((d, 1.2), (d + 0.09, 1.2), (d, 1.0))])        # misulas
    p.box('dark', -0.45, 0.45, 0.12, 0.8, d - 0.12, d + 0.001)
    p.box('brick', -0.55, 0.55, 0.8, 0.86, d - 0.12, d)                                       # verga de tijolo do vao
    p.box('brick', -0.55, -0.45, 0.12, 0.8, d - 0.12, d); p.box('brick', 0.45, 0.55, 0.12, 0.8, d - 0.12, d)
    p.box('dark', -0.45, 0.45, 0.12, 0.8, d - 0.13, d - 0.12)
    prof_x(p, 'cap', -w - 0.1, w + 0.1, crect(d, d + 0.45, 0.0, 0.08, 0.012, (0, 1, 1, 0)))         # lareira (base de pedra)
    p.box('brick', -0.5, 0.5, 1.28, H - SLAB, 0, 0.4); return p
def chimney(h):
    """Chamine externa: base larga, ombros inclinados com pingadeira, corpo, cimalha em 2 fiadas, capa de concreto e 2 manilhas."""
    p = Piece(); d0 = 0.7; w0 = 0.8; ws = 0.36; ys = RAISE + 1.4
    p.box('brick', -w0, w0, 0, ys, 0.0, d0)
    p.hull('brick', [(x, y, z) for (x, y) in ((-w0, ys), (w0, ys), (-ws, ys + 0.8), (ws, ys + 0.8)) for z in (0.0, d0)])
    p.hull('cap', [(x, y, z) for (x, y) in ((-w0 - 0.03, ys - 0.02), (w0 + 0.03, ys - 0.02), (-w0 - 0.03, ys + 0.02), (w0 + 0.03, ys + 0.02)) for z in (0.006, d0 + 0.03)])
    p.box('brick', -ws, ws, ys + 0.8, h - 0.25, 0.04, 0.66)
    p.box('brick', -ws - 0.03, ws + 0.03, h - 0.25, h - 0.125, 0.01, 0.69); p.box('brick', -ws - 0.06, ws + 0.06, h - 0.125, h, -0.02, 0.72)
    p.hull('cap', [(x, y, z) for (x, z) in ((-ws - 0.09, -0.05), (ws + 0.09, -0.05), (ws + 0.09, 0.75), (-ws - 0.09, 0.75)) for y in (h, h + 0.06)] +
           [(x, h + 0.12, z) for (x, z) in ((-ws, 0.06), (ws, 0.06), (ws, 0.64), (-ws, 0.64))])
    for xx in (-0.15, 0.15):
        p.cyl('clay', 0.085, h + 0.08, h + 0.42, xx, 0.35, 12); p.cyl('dark', 0.065, h + 0.42 - 0.02, h + 0.425, xx, 0.35, 12)
        p.cyl('clay', 0.1, h + 0.36, h + 0.42, xx, 0.35, 12)
    return p

# ============================================================================ telhado de quatro aguas a 30 graus
KR = math.tan(math.radians(30)); CS = math.cos(math.radians(30)); TV = 0.08; OVER = 0.5; YE = H - 0.03
AXR, AZR = 7.0 + OVER, 6.0 + OVER
SHX = 0.2 * CS; BUMP = 0.022      # fiada de telha: 0,2 m medidos na agua; degrau de 2,2 cm na borda de baixo
configurar_telhado(TV, BUMP, 30)
def rafter_tails(p, xs, yfun, z0=0.01, z1=OVER - 0.022):
    """Pontas de caibro aparentes sob o beiral (0,05 x 0,12 m)."""
    for xx in xs:
        p.hull('trim', [(xx + dx, yfun(z) + dy, z) for dx in (-0.025, 0.025) for z in (z0, z1) for dy in (0.0, -0.12)])
def roof_strip(E, P, u, x0=-W / 2, x1=W / 2, fascia_ext=0.0, gutter=(None, None), tails=True, gaps=()):
    """Faixa de 2 m de uma agua do telhado de quatro aguas. Beiral ao longo de X local em z=OVER (pivo: face da parede, cota do piso),
    sobe para -Z. E = meia largura do beiral (externo), P = distancia do beiral a cumeeira, u = centro do modulo ao longo do beiral.
    gutter = (gx0, gx1): trecho da calha em x local (None = ate o fim da faixa)."""
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
    prof_x(p, 'trim', a, b, crect(OVER - 0.02, OVER + 0.03, yb - 0.15, yb + 0.05, 0.006, (0, 1, 1, 0)))   # testeira com quina chanfrada
    if gutter is not False:
        gx0 = gutter[0] if gutter[0] is not None else x0 - (0.2 if x0 < -W / 2 else 0)
        gx1 = gutter[1] if gutter[1] is not None else x1 + (0.2 if x1 > W / 2 else 0)
        mit = []
        if x1 > W / 2 + 1e-6: mit.append((x1, 1))
        if x0 < -W / 2 - 1e-6: mit.append((x0, -1))
        runs = [[gx0, gx1, gutter[0] is not None, gutter[1] is not None]]
        for (ga, gb) in gaps:      # interrompe a calha (ex.: chamine atravessando o beiral), com tampas
            r = runs.pop(); runs += [[r[0], ga, r[2], True], [gb, r[1], True, r[3]]]
        for (ra, rb, ca, cb) in runs:
            gutter_run(p, ra, rb, OVER + 0.03, yb + 0.02, [(xc, s) for xc, s in mit if (s > 0 and rb >= xc) or (s < 0 and ra <= xc)], caps=(ca, cb))
    if tails:
        lim = E - OVER - 0.25
        xs = [xx for xx in (-0.75, -0.25, 0.25, 0.75) if abs(u + xx) < lim]
        rafter_tails(p, xs, lambda z: YE - KR * z)
    return p
def hip_cap():
    p = Piece(); t0, t1 = OVER + 0.02, -(AZR - OVER); yt = lambda t: YE + TV + BUMP - KR * t; pts = []
    for t in (t0, t1):
        c = np.array([t, 0, t]); n = np.array([1, 0, -1]) / math.sqrt(2)
        for (off, dy) in ((0, 0.075), (0.06, 0.06), (-0.06, 0.06), (0.14, -0.04), (-0.14, -0.04), (0, -0.12)):
            q = c + n * off; pts.append((q[0], yt(t) + dy, q[2]))
    p.hull('ridge', pts); return p
def ridge_cap(x0=-1.0, x1=1.0):
    p = Piece(); y = YE + TV + BUMP + KR * (AZR - OVER); d = 0.17
    p.hull('ridge', [(x, yy, z) for x in (x0 - 0.05, x1 + 0.05) for (yy, z) in ((y - d * KR - 0.04, d), (y - d * KR - 0.04, -d), (y + 0.075, 0.0), (y + 0.06, 0.06), (y + 0.06, -0.06), (y - 0.12, 0.0))]); return p
# ============================================================================ varanda
PD = 2.5; LW = 0.9; PB = 2.35; PBT = 2.65; PX = 5.15; PXO = 5.45
def porch_deck():
    """Modulo de 2 m do deck, da parede (z=0) ate a mureta (z=PD-0.25): tabuas de 0,14 m com frestas, sobre barrote."""
    p = Piece(); L = PD - 0.25
    p.box('dark', -W / 2, W / 2, -0.07, -0.03, 0.0, L)
    n = 14; bw = W / n
    for i in range(n):
        a = -W / 2 + i * bw + 0.003; b = a + bw - 0.006
        prof_z(p, 'deck', 0.0, L, crect(a, b, -0.03, 0.0, 0.004, (0, 0, 1, 1)))
    return p
def porch_front_wall():
    p = Piece(); t = 0.25
    p.box('brick', -W / 2, W / 2, -RAISE, -0.05, -t, 0)
    for k in range(5):     # tabuas da mureta
        y0 = -0.05 + k * (LW - 0.05 + 0.05) / 5; y1 = y0 + (LW) / 5 + 0.02
        p.hull('siding', [(x, y, z) for x in (-W / 2, W / 2) for (y, z) in ((y0, 0.0), (y0, 0.02), (min(y1, LW), 0.0), (min(y1, LW), 0.02 - 0.014 * min(1, (min(y1, LW) - y0) / (y1 - y0))))])
    p.box('siding', -W / 2, W / 2, -0.05, LW, -t, 0.0)
    prof_x(p, 'cap', -W / 2, W / 2, [(-t - 0.045, LW), (0.045, LW), (0.045, LW + 0.04), (0.02, LW + 0.07), (-t - 0.02, LW + 0.07), (-t - 0.045, LW + 0.04)])
    return p
def porch_base_steps():
    p = Piece(); t = 0.25
    p.box('brick', -W / 2, W / 2, -RAISE, -0.05, -t, 0)
    for i in range(7):
        a = -W / 2 + i * W / 7 + 0.003; b = a + W / 7 - 0.006
        prof_z(p, 'deck', -t, 0.02, crect(a, b, -0.05, 0.0, 0.004, (0, 0, 1, 1)))
    prof_x(p, 'trim', -W / 2, W / 2, crect(0.02, 0.045, -0.2, -0.005, 0.005, (0, 1, 1, 0))); return p
def porch_side_wall(L=PD - 0.125):
    p = Piece(); t = 0.25
    p.box('brick', 0, L, -RAISE, -0.05, -t / 2, t / 2); p.box('siding', 0, L, -0.05, LW, -t / 2, t / 2)
    q = Piece(); prof_x(q, 'cap', 0.05, L, [(-t / 2 - 0.045, LW), (t / 2 + 0.045, LW), (t / 2 + 0.045, LW + 0.04), (t / 2 + 0.02, LW + 0.07), (-t / 2 - 0.02, LW + 0.07), (-t / 2 - 0.045, LW + 0.04)])
    p.merge(q); return p
def porch_pier():
    """Pilar de tijolo com cimalha em 2 fiadas e capa de pedra chanfrada; coluna conica com base e capitel (bevel no Blender)."""
    p = Piece(); a = 0.3
    p.box('brick', -a, a, -RAISE, LW - 0.1, -a, a)
    p.box('brick', -a - 0.025, a + 0.025, LW - 0.1, LW - 0.025, -a - 0.025, a + 0.025)
    p.box('brick', -a - 0.05, a + 0.05, LW - 0.025, LW + 0.05, -a - 0.05, a + 0.05)
    p.hull('cap', [(sx * c, y, sz * c) for (c, y) in ((a + 0.09, LW + 0.05), (a + 0.09, LW + 0.1), (a + 0.04, LW + 0.15)) for sx in (-1, 1) for sz in (-1, 1)])
    y0, y1 = LW + 0.15, PB - 0.1; b0, b1 = 0.2, 0.14
    shaft = trimesh.convex.convex_hull(np.array([(sx * b, y, sz * b) for (b, y) in ((b0, y0 + 0.16), (b1, y1 - 0.14)) for sx in (-1, 1) for sz in (-1, 1)]))
    base = [tbox(-0.26, 0.26, y0, y0 + 0.1, -0.26, 0.26), tbox(-0.23, 0.23, y0 + 0.1, y0 + 0.16, -0.23, 0.23)]
    capt = [tbox(-0.16, 0.16, y1 - 0.14, y1 - 0.1, -0.16, 0.16), tbox(-0.19, 0.19, y1 - 0.1, y1 - 0.05, -0.19, 0.19), tbox(-0.22, 0.22, y1 - 0.05, PB, -0.22, 0.22)]
    for m in [shaft] + base + capt: p.add('trim', bl_detail(m, bevel=0.008, segments=2))
    return p
def porch_beam_side(L=PD - 0.275):
    p = Piece(); prof_x(p, 'trim', 0, L, crect(-0.15, 0.15, PB, PBT, 0.01)); return p
def porch_ceiling():
    """Forro de tabuas macho-femea (frisos) pintado, entre as vigas."""
    p = Piece(); x0, x1 = -PX + 0.3, PX - 0.3; L = PD - 0.275
    p.box('ceiling', x0, x1, PBT - 0.03, PBT, 0, L)
    n = int((x1 - x0) / 0.1)
    for i in range(1, n):
        xx = x0 + i * (x1 - x0) / n; p.box('dark', xx - 0.004, xx + 0.004, PBT - 0.032, PBT - 0.029, 0.005, L - 0.005)
    return p
ZF = PD + 0.45
def porch_y(x): return PBT + KR * (PX - np.abs(x))
def porch_gable():
    """Viga da frente, frontao de tabuas em geometria com veneziana, testeiras, tercas aparentes e maos-francesas."""
    p = Piece(); zc = PD - 0.125
    prof_x(p, 'trim', -PX, PX, crect(zc - 0.15, zc + 0.15, PB, PBT, 0.01))
    yp = float(porch_y(0)) + 0.02
    tri = Polygon([(-PX, PBT), (PX, PBT), (0, yp)])
    ext = lambda mat, poly, z0, z1: [p.add(mat, _fix((lambda m: (m.apply_translation([0, 0, z0]), m)[1])(trimesh.creation.extrude_polygon(g, z1 - z0))))
                                     for g in getattr(poly, 'geoms', [poly]) if g.geom_type == 'Polygon' and g.area > 1e-6]
    ext('siding', tri, PD - 0.1, PD + 0.05)
    # tabuas do frontao (mesma exposicao das paredes), recortadas pelo triangulo; a veneziana fica num buraco
    vy = PBT + 1.25; hole = (-0.53, 0.53, vy - 0.05, vy + 0.795)
    GB0 = WT + 13 * EXPO; kG = int((yp - GB0) / EXPO) + 1   # tabuas do frontao na mesma fase das paredes
    for k in range(kG):
        b0 = GB0 + k * EXPO; b1 = b0 + EXPO + LAP
        for (ya, yb) in [(b0, b1)]:
            wa = PX * (1 - (ya - PBT) / (yp - PBT)); wb = PX * (1 - (yb - PBT) / (yp - PBT))
            if wb <= 0.02: wb = 0.02
            th = lambda y: TB - (TB - TT) * (y - b0) / (b1 - b0)
            segs = [(-1, 1)]
            if ya >= hole[2] - 1e-9 and yb <= hole[3] + 1e-9: segs = [(-1, hole[0]), (hole[1], 1)]
            elif ya < hole[3] and yb > hole[2]:
                for y_lo, y_hi, sg in ((ya, hole[2], [(-1, 1)]), (hole[2], min(yb, hole[3]), [(-1, hole[0]), (hole[1], 1)]), (hole[3], yb, [(-1, 1)])):
                    if y_hi - y_lo < 1e-4: continue
                    wl = PX * (1 - (y_lo - PBT) / (yp - PBT)); wh = max(0.02, PX * (1 - (y_hi - PBT) / (yp - PBT)))
                    for sa, sb in sg:
                        xa_l, xb_l = max(-wl, sa if sa > -1 else -wl), min(wl, sb if sb < 1 else wl)
                        xa_h, xb_h = max(-wh, sa if sa > -1 else -wh), min(wh, sb if sb < 1 else wh)
                        if xb_l - xa_l < 1e-3: continue
                        p.hull('siding', [(xa_l, y_lo, PD + 0.05), (xb_l, y_lo, PD + 0.05), (xa_l, y_lo, PD + 0.05 + th(y_lo)), (xb_l, y_lo, PD + 0.05 + th(y_lo)),
                                          (xa_h, y_hi, PD + 0.05), (max(xa_h + 1e-3, xb_h), y_hi, PD + 0.05), (xa_h, y_hi, PD + 0.05 + th(y_hi)), (max(xa_h + 1e-3, xb_h), y_hi, PD + 0.05 + th(y_hi))])
                continue
            for sa, sb in segs:
                xa_l, xb_l = max(-wa, sa if sa > -1 else -wa), min(wa, sb if sb < 1 else wa)
                xa_h, xb_h = max(-wb, sa if sa > -1 else -wb), min(wb, sb if sb < 1 else wb)
                if xb_l - xa_l < 1e-3: continue
                xb_h = max(xa_h + 1e-3, xb_h)
                p.hull('siding', [(xa_l, ya, PD + 0.05), (xb_l, ya, PD + 0.05), (xa_l, ya, PD + 0.05 + th(ya)), (xb_l, ya, PD + 0.05 + th(ya)),
                                  (xa_h, yb, PD + 0.05), (xb_h, yb, PD + 0.05), (xa_h, yb, PD + 0.05 + th(yb)), (xb_h, yb, PD + 0.05 + th(yb))])
    prof_x(p, 'trim', -PX, PX, crect(PD + 0.05, PD + 0.09, PBT, PBT + 0.16, 0.006, (0, 1, 1, 0)))
    # veneziana com moldura, laminas inclinadas
    p.cham('trim', -0.53, 0.53, vy - 0.05, vy + 0.78, PD + 0.05, PD + 0.095, 0.008)
    p.box('dark', -0.43, 0.43, vy + 0.05, vy + 0.68, PD + 0.095, PD + 0.1)
    for i in range(6):
        yy = vy + 0.09 + i * 0.1
        p.hull('trim', [(x, y, z) for x in (-0.43, 0.43) for (y, z) in ((yy, PD + 0.1), (yy + 0.012, PD + 0.1), (yy - 0.03, PD + 0.15), (yy - 0.018, PD + 0.15))])
    p.hull('trim', [(x, y, z) for x in (-0.55, 0.55) for (y, z) in ((vy + 0.78, PD + 0.05), (vy + 0.78, PD + 0.12), (vy + 0.81, PD + 0.05), (vy + 0.8, PD + 0.12))])
    # testeiras inclinadas (rake) por cima das tabuas
    for s in (-1, 1):
        a = np.array([s * PX, PBT]); b = np.array([0, float(porch_y(0))]); d = b - a; n = np.array([-d[1], d[0]]) / np.linalg.norm(d) * 0.12
        q = Polygon([a + n, b + n, b - n, a - n]).intersection(tri.buffer(0)); ext('trim', q, PD + 0.05, PD + 0.09)
    # tercas aparentes e maos-francesas sob a beirada inclinada
    for s in (-1, 1):
        for xx in (1.6, 3.4):
            yy = float(porch_y(xx)) - 0.02; X = s * xx
            p.cham('trim', X - 0.06, X + 0.06, yy - 0.2, yy, PD - 0.09, ZF - 0.04, 0.012)
            p.hull('trim', [(X + dx, y, z) for dx in (-0.06, 0.06) for (y, z) in ((yy - 0.2, ZF - 0.04), (yy - 0.26, ZF - 0.1), (yy - 0.2, ZF - 0.12))])
        X = s * 4.6; yy = float(porch_y(4.6)) - 0.02
        p.cham('trim', X - 0.05, X + 0.05, yy - 0.75, yy - 0.12, PD + 0.09, PD + 0.17, 0.01)
        p.seg('trim', (X, yy - 0.68, PD + 0.13), (X - s * 0.0, yy - 0.15, ZF - 0.12), 0.08, 0.08)
    yy = yp - 0.02; p.cham('trim', -0.08, 0.08, yy - 0.3, yy - 0.04, PD - 0.09, ZF + 0.02, 0.012)   # ponta da cumeeira
    return p
def porch_roof():
    """Telhado de duas aguas da varanda, com fiadas de telha; atras morre no telhado principal em dois rincoes. Calhas nos beirais laterais."""
    p = Piece(); zv = (YE + TV - PBT - TV) / KR
    zb = lambda ax: min(ax - PX + zv, OVER + 0.05)
    f = lambda a, b: PBT + KR * (PX - np.abs(a))
    for s in (-1, 1):
        xs = np.linspace(0, PX, 12); pts = [(s * x, zb(x)) for x in xs] + [(s * PX, OVER + 0.05), (s * PXO, OVER + 0.05), (s * PXO, ZF), (0, ZF)]
        poly = Polygon(pts).buffer(0)
        sheared(p, 'plaster', poly, 0.0, 0.02, f)
        sheared_courses(p, poly, f, lambda a, b: PXO - np.abs(a),
                        (lambda s_: (lambda d0, d1: (lambda xa, xb: sbox(xa, -50, xb, 50))(*sorted((s_ * (PXO - d1), s_ * (PXO - d0))))))(s),
                        PXO + 0.01, lambda v, n: np.stack([v[:, 2] / TILE, (PXO - np.abs(v[:, 0])) / CS / TILE], 1))
        ye = float(porch_y(PXO))
        prof_z(p, 'trim', OVER + 0.06, ZF + 0.03, crect(*sorted((s * (PXO - 0.02), s * (PXO + 0.03))), ye - 0.15, ye + 0.05, 0.006))
        g = Piece(); gx = s * (PXO + 0.03)     # calha: X local -> Z do mundo, Z local -> para fora (s * X)
        za, zb_ = OVER + 0.04, ZF + 0.16
        gutter_run(g, *((-zb_, -za) if s > 0 else (za, zb_)), 0.0, ye + 0.02, caps=(True, True))
        R = trimesh.transformations.rotation_matrix(s * math.pi / 2, [0, 1, 0])
        for m in g.parts['gutter']: m.apply_transform(R); m.apply_translation([gx, 0, 0]); p.add('gutter', m)
        a = (s * (PXO + 0.03), float(porch_y(PXO))); b = (0, float(porch_y(0)))
        p.hull('trim', [(x, y + dy, z) for (x, y) in (a, b) for dy in (-0.15, 0.05) for z in (ZF - 0.02, ZF + 0.03)])
    y = float(porch_y(0)) + TV + BUMP; d = 0.17; z0 = zb(0.0)
    p.hull('ridge', [(x, yy, z) for z in (z0, ZF + 0.05) for (yy, x) in ((y - d * KR - 0.04, d), (y - d * KR - 0.04, -d), (y + 0.075, 0.0), (y + 0.06, 0.06), (y + 0.06, -0.06), (y - 0.12, 0.0))])
    return p
# ============================================================================ interior
def floor_tile():
    p = Piece(); p.box('floor', -W / 2, W / 2, -0.03, 0, -W / 2, W / 2); p.box('plaster', -W / 2 + 0.02, W / 2 - 0.02, -SLAB, -0.03, -W / 2 + 0.02, W / 2 - 0.02); return p
def floor_tile_bath():
    """Piso de banheiro: ladrilhos hexagonais/quadrados em relevo seria caro; aqui pastilhas de 0,1 m com rejunte em geometria."""
    p = Piece(); p.box('dark', -W / 2, W / 2, -0.027, -0.004, -W / 2, W / 2)
    n = 10; s = W / n
    for i in range(n):
        for j in range(n):
            x0 = -W / 2 + i * s + 0.004; z0 = -W / 2 + j * s + 0.004
            p.box('tile', x0, x0 + s - 0.008, -0.03, 0.0, z0, z0 + s - 0.008)
    p.box('plaster', -W / 2 + 0.02, W / 2 - 0.02, -SLAB, -0.03, -W / 2 + 0.02, W / 2 - 0.02); return p
def interior_wall(doorway, h=H - SLAB, ow=0.9):
    p = Piece(); t = 0.12; ow = ow if doorway else 0
    wall_with_opening(p, 'plaster', ow, 0, 2.1, h, inner='plaster', t=t, centered=True)
    if doorway: door_casing(p, ow, t)
    segs = [(-W / 2, -ow / 2 - 0.08), (ow / 2 + 0.08, W / 2)] if doorway else [(-W / 2, W / 2)]   # rodape para na porta
    for a, b in segs: baseboard(p, a, b, t)
    return p
def interior_wall_end(h=H - SLAB):
    p = Piece(); t = 0.12; L = W - T
    m = trimesh.creation.box(extents=[L, h, t]); m.apply_translation([-W / 2 + L / 2, h / 2, 0]); p.add('plaster', m)
    baseboard(p, -W / 2, -W / 2 + L, t); return p
def interior_wall_end_doorway(h=H - SLAB):
    p = Piece(); t = 0.12; e = W / 2 - T
    xs = [-W / 2, -0.45, 0.45, e]; ys = [0.0, 2.1, h]; zs = [-t / 2, t / 2]
    def cell(i, j, k): return None if (i == 1 and j == 0) else 'plaster'
    for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)
    door_casing(p, 0.9, t)
    for (a, b) in ((-W / 2, -0.53), (0.53, e)): baseboard(p, a, b, t)
    return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p

# ============================================================================ pecas
CHIM_H = round(RAISE + 5.1, 2)
FB = [-6, -4, -2, 0, 2, 4, 6]; SB = [-5, -3, -1, 1, 3, 5]
def roof_name(kind, u, suf=''): return f'roof_{kind}_{abs(u)}' + ('_l' if u < 0 else '') + suf
GUT_Y = YE - KR * OVER + 0.02 - 0.12   # fundo da calha, relativo ao piso
pieces = {'floor_tile': floor_tile(), 'floor_tile_bath': floor_tile_bath(), 'ceiling_tile': ceiling_tile(),
          'door_leaf_front': door_front(), 'door_leaf_back': door_back(), 'door_leaf_interior': door_interior(),
          'interior_wall_plain': interior_wall(False), 'interior_wall_doorway': interior_wall(True), 'interior_wall_end': interior_wall_end(), 'interior_wall_end_doorway': interior_wall_end_doorway(),
          'wall_siding_window': wall_siding_window(), 'wall_siding_small_window': wall_siding_small_window(), 'wall_siding_plain': wall_siding_plain(), 'wall_siding_door': wall_siding_door(),
          'wall_siding_window_hood': wall_siding_window_hood(), 'corner_siding': corner_siding(), 'fireplace': fireplace(), 'chimney': chimney(CHIM_H), 'brick_steps': brick_steps(),
          'hip_cap': hip_cap(), 'ridge_cap': ridge_cap(),
          'downspout': downspout(RAISE + GUT_Y, OVER + 0.095), 'downspout_porch': downspout(RAISE + float(porch_y(PXO)) + 0.02 - 0.12, 0.245),
          'porch_deck': porch_deck(), 'porch_front_wall': porch_front_wall(), 'porch_base_steps': porch_base_steps(), 'porch_side_wall': porch_side_wall(), 'porch_pier': porch_pier(),
          'porch_beam_side': porch_beam_side(), 'porch_ceiling': porch_ceiling(), 'porch_gable': porch_gable(), 'porch_roof': porch_roof(),
          'porch_lantern': porch_lantern(), 'wall_lantern': wall_lantern(),
          'player_scale_ref': player_ref()}
for u in FB:
    ext_ = 0.03 if u == 6 else -0.03 if u == -6 else 0
    x0, x1 = -W / 2 - (OVER if u == -6 else 0), W / 2 + (OVER if u == 6 else 0)
    pieces.setdefault(roof_name('main', u), roof_strip(AXR, AZR, u, x0, x1, fascia_ext=ext_))
    # frente: atras do telhado da varanda nao ha calha (ela fica escondida); na ponta a calha comeca depois da varanda
    if abs(u) <= 4: pieces.setdefault(roof_name('main', u, '_porch'), roof_strip(AXR, AZR, u, x0, x1, fascia_ext=ext_, gutter=False))
    else:
        g0 = (PXO + 0.16) - abs(u)
        pieces.setdefault(roof_name('main', u, '_porch'), roof_strip(AXR, AZR, u, x0, x1, fascia_ext=ext_, gutter=(g0, None) if u > 0 else (None, -g0)))
for u in SB:
    pieces.setdefault(roof_name('hip', u), roof_strip(AZR, AXR, u, -W / 2 - (OVER if u == -5 else 0), W / 2 + (OVER if u == 5 else 0)))
pieces['roof_hip_3_chimney'] = roof_strip(AZR, AXR, 3, -W / 2, W / 2, gaps=[(-0.45, 0.45)])   # lado esquerdo: a chamine corta a calha

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)

# ============================================================================ montagem: igual ao kit 7 + calhas, condutores e lanternas
SX, SZ = 7.0, 6.0
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
def ftag(fl): return f'floor{fl}'
faces = [(0, FB, lambda u: (u, SZ), 'front'), (90, SB, lambda u: (SX, -u), 'right'), (180, FB, lambda u: (-u, -SZ), 'back'), (-90, SB, lambda u: (-SX, u), 'left')]
SW, SS, SP, SD, SH = 'wall_siding_window', 'wall_siding_small_window', 'wall_siding_plain', 'wall_siding_door', 'wall_siding_window_hood'
G = {'front': {-6: SW, -4: SW, -2: SW, 0: SD, 2: SW, 4: SP, 6: SW},
     'back': {-6: SW, -4: SW, -2: SD, 0: SS, 2: SP, 4: SW, 6: SW},
     'left': {5: SW, 3: SP, 1: SW, -1: SW, -3: SW, -5: SP},
     'right': {5: SW, 3: SH, 1: SS, -1: SW, -3: SP, -5: SW}}
for ry, bays, f, tag in faces:
    for u in bays:
        x, z = f(u); wk = x if tag in ('front', 'back') else z
        put(G[tag][wk], x, lvl(0), z, ry, [tag, 'ext', ftag(0)])
        put(roof_name('main' if tag in ('front', 'back') else 'hip', u, '_porch' if tag == 'front' else '_chimney' if (tag, u) == ('left', 3) else ''), x, lvl(0), z, ry, [tag, 'roof'])
for ry, x, z, tg in [(0, SX, SZ, ('front', 'right')), (90, SX, -SZ, ('right', 'back')), (180, -SX, -SZ, ('back', 'left')), (-90, -SX, SZ, ('left', 'front'))]:
    put('corner_siding', x, lvl(0), z, ry, tg + ('ext', ftag(0))); put('hip_cap', x, lvl(0), z, ry, tg + ('roof',))
put('ridge_cap', 0, lvl(0), 0, 0, ['roof'])
# condutores nos 4 cantos (nas fachadas da frente e dos fundos, a 0,35 m do canto) e 2 na frente da varanda
for x, z, ry, tg in ((6.62, SZ, 0, 'front'), (-6.62, SZ, 0, 'front'), (6.62, -SZ, 180, 'back'), (-6.62, -SZ, 180, 'back')):
    put('downspout', x, 0, z, ry, [tg, 'ext'])
for s in (-1, 1): put('downspout_porch', s * 5.3, 0, SZ + 2.3, 90 * s, ['front', 'porch'])
put('chimney', -SX, 0, 3, -90, ['left', 'ext']); put('fireplace', -SX + T, lvl(0), 3, 90, [ftag(0)])
for x in (-4, -2, 0, 2, 4):
    put('porch_deck', x, lvl(0), SZ, 0, ['front', 'porch'])
    put('porch_base_steps' if x == 0 else 'porch_front_wall', x, lvl(0), SZ + PD, 0, ['front', 'porch'])
for x in (-5, -1, 1, 5): put('porch_pier', x, lvl(0), SZ + PD - 0.125, 0, ['front', 'porch'])
for x in (-5, 5): put('porch_side_wall', x, lvl(0), SZ, -90, ['front', 'porch']); put('porch_beam_side', x, lvl(0), SZ, -90, ['front', 'porch'])
put('porch_ceiling', 0, lvl(0), SZ, 0, ['front', 'porch']); put('porch_gable', 0, lvl(0), SZ, 0, ['front', 'porch'])
put('porch_roof', 0, lvl(0), SZ, 0, ['front', 'porch', 'roof'])
put('porch_lantern', 0, lvl(0) + PBT - 0.03, SZ + 1.15, 0, ['front', 'porch'])
put('wall_lantern', -3.0, lvl(0) + 1.85, -SZ - 0.04, 180, ['back', 'ext'])
put('brick_steps', 0, lvl(0), SZ + PD, 0, ['front', 'porch'])
put('brick_steps', -2, lvl(0), -SZ, 180, ['back', 'ext'])
TILEB = {(2, -3), (2, -1), (-2, -5), (-2, -3), (-2, -1), (0, -5), (0, -3), (0, -1), (2, -5)}
for a in FB:
    for b in SB:
        put('floor_tile_bath' if (a, b) in TILEB else 'floor_tile', a, lvl(0), b, 0, [ftag(0)])
        put('ceiling_tile', a, lvl(0) + H - 0.01, b, 0, ['roof', 'ceiling'])
def wl(fl, x0, z0, x1, z1, doors=()):
    y = lvl(fl)
    if z0 == z1:
        for c in range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2):
            end = abs(c) + 1 >= SX; d = c in doors
            put(('interior_wall_end' if end else 'interior_wall_' + ('doorway' if d else 'plain')) + ('_doorway' if end and d else ''), c, y, z0, (0 if c > 0 else 180) if end else 0, [ftag(fl)])
            if d: hx, hz = hinge(c, z0, 0, -0.43, 0); put('door_leaf_interior', hx, y, hz, 0, [ftag(fl)], door=70)
    else:
        for c in range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2):
            end = abs(c) + 1 >= SZ; d = c in doors
            put(('interior_wall_end' if end else 'interior_wall_' + ('doorway' if d else 'plain')) + ('_doorway' if end and d else ''), x0, y, c, (-90 if c > 0 else 90) if end else 90, [ftag(fl)])
            if d: hx, hz = hinge(x0, c, 90, -0.43, 0); put('door_leaf_interior', hx, y, hz, 90, [ftag(fl)], door=70)
wl(0, -7, 0, 1, 0, doors=(-4, 0)); wl(0, 1, -6, 1, 6, doors=(1, -5)); wl(0, 1, 0, 7, 0, doors=(2, 4)); wl(0, 1, 2, 7, 2, doors=(4,))
wl(0, 3, -6, 3, 0); wl(0, 1, -4, 3, -4); wl(0, -3, -6, -3, 0, doors=(-3,))
put('door_leaf_front', -0.47, lvl(0) + 0.015, SZ - 0.18, 0, ['front', 'ext', ftag(0)], door=85)
hx, hz = hinge(-2, -SZ, 180, -0.47, -0.18); put('door_leaf_back', hx, lvl(0) + 0.015, hz, 180, ['back', 'ext', ftag(0)], door=85)
put('player_scale_ref', 2.0, 0, SZ + PD + 1.4); put('player_scale_ref', -4, lvl(0), 3, 0, [ftag(0)]); put('player_scale_ref', 3, lvl(0), SZ + 1.2, 0, ['porch'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    json.dump({'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE, 'footprint': [2 * SX, 2 * SZ], 'porch': {'x': [-5, 5], 'z': [SZ, SZ + PD]},
                        'roof': 'hipped, 30 deg, ridge along X (x in [-1,1]) at z=0, eave overhang 0.5 m', 'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2'},
               'placements': L}, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    asm = Piece()
    for e in L:
        if e['piece'] == 'player_scale_ref': continue
        Tm = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); Tm[:3, 3] = e['pos']
        q = pieces[e['piece']]; asm.merge(q, Tm)
        # UVs especiais (telhas) sao calculadas por peca: no montado guardamos a malha ja com UV
    # o montado precisa das UVs de cada peca: exporta cada peca ja posicionada e junta as cenas
    sc = trimesh.Scene()
    for i, e in enumerate(L):
        if e['piece'] == 'player_scale_ref': continue
        Tm = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); Tm[:3, 3] = e['pos']
        s = pieces[e['piece']].scene(e['piece'])
        for nm, g in s.geometry.items():
            g = g.copy(); g.apply_transform(Tm); sc.add_geometry(g, node_name=f'{i}_{nm}', geom_name=f'{i}_{nm}')
    # junta por material para ficar leve
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
# vao da janela rebocado por dentro (scripts/detalhe/vao.py)
import vao as _vao, glob as _gl
for _f in _gl.glob(_o.path.join(OUT, 'pieces', '*win*.glb')): _vao.rebocar(_f)
