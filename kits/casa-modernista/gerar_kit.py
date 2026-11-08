"""Kit 27: casa modernista dos anos 50 (mid-century), terrea, de 14 x 10 m, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Estrutura de pilar e viga: vigas de madeira laminada aparentes que atravessam as paredes e saem em balanco sob o beiral de 1 m,
forro de tabuas continuo de dentro para fora, telhado plano com cascalho, testeira escura com rufo, domos de iluminacao,
paredes de vidro do piso ao forro, janelas altas em fita, tabuas verticais com junta em V, reboco branco, porta amarela com
visor lateral, muro de cobogo, garagem coberta (carport) com pilares de aco, lareira e chamine de pedra, corrente de chuva.
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
configurar(cores={'boards': (152, 94, 60), 'render': (238, 234, 224), 'metal': (58, 54, 50), 'roofdeck': (168, 164, 156), 'ceiling': (200, 160, 116),
                  'fascia': (74, 52, 40), 'concrete': (184, 180, 172), 'breeze': (240, 236, 228), 'stone2': (170, 150, 128), 'floor': (176, 128, 84),
                  'door': (222, 166, 44), 'plaster': (244, 241, 234), 'beam': (128, 84, 54), 'trim': (240, 236, 228), 'frame': (240, 236, 228),
                  'glass': (150, 186, 200), 'iron': (40, 40, 42), 'dome': (226, 234, 236), 'tile': (120, 172, 168), 'door_int': (196, 150, 104), 'gutter': (70, 64, 58)},
           texturas={'boards': 'planks', 'render': 'render', 'roofdeck': 'stone2', 'ceiling': 'planks', 'fascia': 'paint', 'concrete': 'render',
                     'breeze': 'render', 'stone2': 'stone2', 'floor': 'planks', 'plaster': 'plaster', 'beam': 'planks', 'door': 'paint'},
           out=OUT)
D.METAL.add('metal'); MATS = D.MATS
MATS['metal'].metallicFactor = 0.7; MATS['metal'].roughnessFactor = 0.4
MATS['dome'].roughnessFactor = 0.2; MATS['dome'].metallicFactor = 0.1

W = 2.0; T = 0.3; H = 2.9; RAISE = 0.2; SX = 7.0; SZ = 5.0; OV = 1.0
DK = 0.22             # espessura do telhado (forro + estrutura + manta)
def lvl(): return RAISE

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
def seg_cyl(p, mat, p0, p1, r, sec=10):
    p0, p1 = np.array(p0, float), np.array(p1, float); v = p1 - p0; L = np.linalg.norm(v)
    c = trimesh.creation.cylinder(radius=r, height=L, sections=sec); z = np.array([0, 0, 1.0]); v = v / L
    ax = np.cross(z, v); ang = math.acos(np.clip(np.dot(z, v), -1, 1))
    if np.linalg.norm(ax) > 1e-6: c.apply_transform(trimesh.transformations.rotation_matrix(ang, ax))
    elif v[2] < 0: c.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    c.apply_translation((p0 + p1) / 2); return p.add(mat, c)
def wall_core(p, holes, h, outer, inner='plaster', zo=-0.025):
    """Nucleo estanque com buracos [(x0, x1, y0, y1)], de -RAISE a h. Camada interna de gesso (2 cm) acima do piso, que para 5 mm abaixo do topo."""
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([-RAISE, 0.0, h - 0.005, h] + [max(-RAISE, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0:
            if ys[j] >= h - 0.0051: return None
            return inner if cy > 0 else 'concrete'
        return outer if cy > 0 else 'concrete'
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, zo], cell).items(): p.add(m, mesh)
def bands(holes, y0, y1, x0=-W / 2, x1=W / 2):
    cuts = sorted(set([y0, y1] + [y for h in holes for y in (h[2], h[3]) if y0 < y < y1])); out = []
    for ya, yb in zip(cuts[:-1], cuts[1:]):
        xs = [(x0, x1)]
        for (hx0, hx1, hy0, hy1) in holes:
            if ya >= hy0 - 1e-9 and yb <= hy1 + 1e-9: xs = [s for a, b in xs for s in ((a, min(b, hx0)), (max(a, hx1), b)) if s[1] - s[0] > 1e-4]
        out += [(a, b, ya, yb) for a, b in xs]
    return out
NB = 13; BWID = W / NB
def boards(p, holes, y0=0.06, y1=H):
    """Tabuas verticais de 15 cm com junta em V (chanfro de 8 mm nas 2 bordas), 2,5 cm de espessura, recortadas nos vaos."""
    for k in range(NB):
        a0 = -W / 2 + k * BWID; a1 = a0 + BWID
        for (a, b, ya, yb) in bands(holes, y0, y1, a0, a1):
            c = 0.008
            pts = [(a, -0.025), (b, -0.025)] + ([(b, -c), (b - c, 0.0)] if abs(b - a1) < 1e-6 else [(b, 0.0)]) + ([(a + c, 0.0), (a, -c)] if abs(a - a0) < 1e-6 else [(a, 0.0)])
            prof_y(p, 'boards', ya, yb, [(x, z) for (x, z) in pts])
def render_skin(p, holes, y0=0.06, y1=H):
    """Reboco branco liso (2,5 cm) de y0 a y1, com buracos."""
    for (a, b, ya, yb) in bands(holes, y0, y1):
        prof_x(p, 'render', a, b, [(-0.025, ya), (0.0, ya), (0.0, yb), (-0.025, yb)])
def base(p, gaps=()):
    """Embasamento de concreto recuado 3 cm (a casa parece flutuar) de -RAISE a 0,06, com pingadeira de aluminio."""
    xs = [-W / 2] + [v for g in gaps for v in g] + [W / 2]
    for i in range(0, len(xs) - 1, 2):
        a, b = xs[i], xs[i + 1]
        if b - a < 0.01: continue
        prof_x(p, 'metal', a, b, [(-0.025, 0.04), (0.012, 0.04), (0.012, 0.03), (0.018, 0.024), (0.022, 0.03), (0.022, 0.06), (-0.025, 0.06)])

# ---------- vidros e esquadrias de aluminio anodizado ----------
def mullion(p, x, y0, y1, w=0.1, z0=-0.17, z1=-0.07):
    p.cham('metal', x - w / 2, x + w / 2, y0, y1, z0, z1, 0.005)
def glass_pane(p, x0, x1, y0, y1, z=-0.12):
    p.box('glass', x0, x1, y0, y1, z - 0.004, z + 0.004)
    for (a, b) in ((x0 - 0.002, x0 + 0.02), (x1 - 0.02, x1 + 0.002)):   # baguetes de vedacao
        for zz in (z - 0.012, z + 0.006): p.box('dark', a, b, y0 - 0.002, y1 + 0.002, zz, zz + 0.006)
def ribbon(p, x0, x1, y0, y1, n=2):
    """Faixa de vidro de x0 a x1 com n vaos, montantes de 10 cm (o do centro recebe a viga), travessas em cima e embaixo."""
    p.cham('metal', x0, x1, y0, y0 + 0.06, -0.2, -0.04, 0.005); p.cham('metal', x0, x1, y1 - 0.06, y1, -0.2, -0.04, 0.005)
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    for i, x in enumerate(xs):
        w = 0.1 if 0 < i < n else 0.06
        xc = x if 0 < i < n else (x + 0.03 if i == 0 else x - 0.03)
        mullion(p, xc, y0 + 0.06, y1 - 0.06, w, -0.2, -0.04)
    for a, b in zip(xs[:-1], xs[1:]):
        ia = a + (0.045 if a > x0 + 1e-6 else 0.055); ib = b - (0.045 if b < x1 - 1e-6 else 0.055)
        glass_pane(p, ia, ib, y0 + 0.058, y1 - 0.058)
# ---------- modulos de parede ----------
CL = 2.15   # peitoril das janelas altas (fita sob o forro)
def wall(kind='boards'):
    """Modulo de 2 m (pivo: face externa, cota do piso). kind: boards, render, glass, glass_door, clerestory, window, entry, side_door, fire."""
    p = Piece(); holes = []
    if kind in ('glass', 'glass_door'): holes = [(-W / 2 + 0.0, W / 2 - 0.0, 0.0, H)]
    if kind == 'clerestory': holes = [(-W / 2, W / 2, CL, H)]
    if kind == 'window': holes = [(-0.8, 0.8, 1.0, 2.15)]
    if kind == 'entry': holes = [(-0.85, 0.85, 0.0, 2.35)]
    if kind == 'side_door': holes = [(-0.47, 0.47, 0.0, 2.2)]
    full = kind in ('glass', 'glass_door')
    if full:      # parede de vidro: so o embasamento e a soleira; vidro do piso ao forro
        prof_x(p, 'concrete', -W / 2, W / 2, [(-T, -RAISE), (-0.025, -RAISE), (-0.025, -0.031), (-T, -0.031)])
        p.box('metal', -W / 2, W / 2, 0.0, 0.08, -0.2, -0.04)
        p.box('metal', -W / 2, W / 2, H - 0.07, H, -0.22, -0.02)
        if kind == 'glass':
            mullion(p, 0.0, 0.08, H - 0.07, 0.1, -0.2, -0.04)
            for (a, b) in ((-W / 2 + 0.03, -0.045), (0.045, W / 2 - 0.03)): glass_pane(p, a + 0.002, b - 0.002, 0.078, H - 0.068)
            for x in (-W / 2, W / 2): mullion(p, x + (0.025 if x < 0 else -0.025), 0.08, H - 0.07, 0.05, -0.2, -0.04)
        else:     # metade esquerda e porta de vidro (folha separada), metade direita fixa; bandeira em cima da porta
            for x in (-W / 2 + 0.025, 0.0, W / 2 - 0.025): mullion(p, x, 0.08, H - 0.07, 0.1 if x == 0 else 0.05, -0.2, -0.04)
            glass_pane(p, 0.047, W / 2 - 0.052, 0.078, H - 0.068)
            p.cham('metal', -W / 2 + 0.05, -0.05, 2.4, 2.47, -0.2, -0.04, 0.005); glass_pane(p, -W / 2 + 0.052, -0.047, 2.468, H - 0.068)
        return p
    wall_core(p, holes, H, 'render' if kind in ('render', 'entry', 'fire') else 'boards')
    if kind in ('render', 'entry', 'fire'): render_skin(p, holes)
    else: boards(p, holes)
    base(p, [h[:2] for h in holes if h[2] <= 0.0])
    if kind == 'clerestory': ribbon(p, -W / 2, W / 2, CL, H, 2)
    if kind == 'window':     # janela horizontal de 3 folhas basculantes com peitoril de aluminio
        ribbon(p, -0.8, 0.8, 1.0, 2.15, 3)
        prof_x(p, 'metal', -0.82, 0.82, [(-0.2, 0.985), (0.035, 0.985), (0.045, 0.975), (0.045, 0.955), (0.0, 0.94), (0.0, 0.97), (-0.2, 0.97)])
        for xx in (-0.8 + 1.6 / 6, 0.0, 0.8 - 1.6 / 6):   # alavancas das basculantes
            p.box('metal', xx - 0.04, xx + 0.04, 1.08, 1.1, -0.16, -0.135)
    if kind == 'entry':      # porta de abrir (folha separada) a esquerda e visor do piso ao alto a direita
        p.box('metal', -0.85, -0.79, 0.0, 2.35, -0.2, -0.05); p.box('metal', -0.85, 0.85, 2.29, 2.35, -0.2, -0.05); p.box('metal', 0.79, 0.85, 0.0, 2.35, -0.2, -0.05)
        mullion(p, 0.17, 0.0, 2.29, 0.08, -0.2, -0.05)
        glass_pane(p, 0.21, 0.79, 0.06, 2.29); p.box('metal', 0.21, 0.79, 0.0, 0.06, -0.2, -0.05)
        prof_x(p, 'concrete', -0.848, 0.848, [(-0.3, 0.012), (0.05, 0.012), (0.07, 0.0), (0.07, -0.05), (-0.3, -0.05)])
    if kind == 'side_door':
        x = 0.47
        p.box('metal', -x, -x + 0.05, 0.0, 2.2, -0.2, -0.05); p.box('metal', x - 0.05, x, 0.0, 2.2, -0.2, -0.05); p.box('metal', -x, x, 2.15, 2.2, -0.2, -0.05)
        prof_x(p, 'concrete', -x + 0.002, x - 0.002, [(-0.3, 0.012), (0.05, 0.012), (0.07, 0.0), (0.07, -0.05), (-0.3, -0.05)])
    return p
def corner():
    """Quina: pilar de aco de 30 x 30 cm que envolve as pontas das paredes, do embasamento ao forro."""
    p = Piece(); e = 0.03
    p.cham('metal', -T - 0.01, e, -0.032, H, -T - 0.01, e, 0.006)
    p.box('concrete', -T - 0.01, -0.03, -RAISE, -0.03, -T - 0.01, -0.03)
    return p
def fireplace():
    """Lareira de pedra encostada na parede de dentro (pivo: face interna da parede, centro, cota do piso; a sala fica em +Z):
    lareira elevada com banco de pedra em balanco, boca com verga de aco, consolo de madeira e pedra ate o forro."""
    p = Piece(); w = 1.8; d = 0.45
    ext_y(p, 'stone2', sbox(-w / 2, 0.0, w / 2, d).difference(sbox(-0.45, 0.002, 0.45, d + 1)), 0.0, H)
    p.box('stone2', -0.45, 0.45, 1.25, H, 0.0, d)
    p.box('dark', -0.45, 0.45, 0.45, 1.25, -0.002, 0.06)
    p.box('stone2', -0.45, 0.45, 0.0, 0.4, 0.06, d)
    p.box('metal', -0.47, 0.47, 1.2, 1.25, d - 0.01, d + 0.012)
    p.cham('concrete', -1.6, 1.6, 0.4, 0.45, 0.003, d + 0.25, 0.01)            # banco em balanco
    p.cham('beam', -1.1, 1.1, 1.5, 1.58, 0.003, d + 0.12, 0.01)                # consolo
    return p
def chimney():
    """Chamine de pedra do lado de fora da parede da lareira (pivo: face externa da parede, centro, cota do piso), atravessa o beiral."""
    p = Piece(); w = 1.0
    p.box('stone2', -w / 2, w / 2, -RAISE, H + DK + 1.0, 0.0, 0.8)
    p.cham('concrete', -w / 2 - 0.05, w / 2 + 0.05, H + DK + 1.0, H + DK + 1.1, -0.05, 0.85, 0.01)
    p.box('metal', -0.2, 0.2, H + DK + 1.1, H + DK + 1.35, 0.2, 0.6); p.box('metal', -0.26, 0.26, H + DK + 1.35, H + DK + 1.38, 0.14, 0.66)
    return p

# ============================================================================ telhado plano: placas de 2 x 2 m, vigas aparentes, testeira
def deck(edges=(0, 0, 0, 0), sky=False, vent=False):
    """Placa de telhado de 2 x 2 m (pivo: centro, cota do piso): forro de tabuas por baixo (face em y = H), estrutura,
    manta com cascalho. edges = (x-, x+, z-, z+): testeira de 5 cm que desce 12 cm abaixo do forro, rufo e batente do cascalho."""
    p = Piece(); x0, x1, z0, z1 = -W / 2, W / 2, -W / 2, W / 2
    p.box('ceiling', x0, x1, H, H + 0.025, z0, z1)
    p.box('fascia', x0, x1, H + 0.025, H + DK - 0.012, z0, z1)
    p.box('roofdeck', x0, x1, H + DK - 0.012, H + DK, z0, z1)
    fb, ft = H - 0.12, H + DK + 0.06
    def fas(prof_fun, a, b, axis):
        pts = [(0.0, fb), (0.05, fb), (0.05, ft - 0.01), (0.045, ft), (0.0, ft)]
        cap = [(-0.04, ft), (0.065, ft), (0.065, ft - 0.03), (0.07, ft - 0.035), (0.075, ft - 0.03), (0.075, ft + 0.012), (-0.04, ft + 0.012)]
        return pts, cap
    zs = (z0 - 0.05 * edges[2], z1 + 0.05 * edges[3])
    for side, on in enumerate(edges):
        if not on: continue
        pts, cap = fas(None, 0, 0, 0)
        if side in (2, 3):    # ao longo de X, em z0 ou z1
            s = 1 if side == 3 else -1; zb = z1 if s > 0 else z0
            a, b = x0, x1
            prof_x(p, 'fascia', a + 0.0005 * (not edges[0]), b - 0.0005 * (not edges[1]), [(zb + s * zz, y) for (zz, y) in pts])
            prof_x(p, 'metal', a - 0.075 * edges[0] + 0.0005 * (not edges[0]), b + 0.075 * edges[1] - 0.0005 * (not edges[1]), [(zb + s * zz, y) for (zz, y) in cap])
        else:                 # ao longo de Z, em x0 ou x1 (cobre as pontas das testeiras de X)
            s = 1 if side == 1 else -1; xb = x1 if s > 0 else x0
            ext(p, 'fascia', Polygon([(xb + s * xx, y) for (xx, y) in pts]), zs[0] + 0.0005 * (not edges[2]), zs[1] - 0.0005 * (not edges[3]))
            ext(p, 'metal', Polygon([(xb + s * xx, y + 0.0005) for (xx, y) in cap]), z0 - 0.07 * edges[2] + 0.0005 * (not edges[2]), z1 + 0.07 * edges[3] - 0.0005 * (not edges[3]))
    if sky:   # domo de acrilico sobre um colar de 15 cm
        p.box('fascia', -0.45, 0.45, H + DK, H + DK + 0.15, -0.45, 0.45); p.box('metal', -0.47, 0.47, H + DK + 0.15, H + DK + 0.17, -0.47, 0.47)
        dm = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
        dm.vertices[:, 1] = np.maximum(dm.vertices[:, 1], 0.0) * 0.28; dm.vertices[:, 0] *= 0.42; dm.vertices[:, 2] *= 0.42
        dm.apply_translation([0, H + DK + 0.17, 0]); p.add('dome', dm)
    if vent:
        for (x, z) in ((0.5, -0.4), (-0.4, 0.5)):
            p.cyl('metal', 0.06, H + DK, H + DK + 0.35, x, z, 12); p.cyl('metal', 0.12, H + DK + 0.35, H + DK + 0.38, x, z, 14); p.cyl('metal', 0.03, H + DK + 0.38, H + DK + 0.46, x, z, 8)
            p.hull('metal', [(x + 0.13 * math.cos(a), H + DK + 0.46, z + 0.13 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)] + [(x, H + DK + 0.53, z)])
    return p
BL = 2 * SZ + 2 * OV - 0.06
def beam(L=BL, h=0.28, w=0.12):
    """Viga de madeira laminada de 12 x 28 cm (pivo: centro, topo encostado no forro, ao longo de Z), pontas chanfradas em bisel."""
    p = Piece(); a = L / 2
    p.hull('beam', [(x, y, z) for x in (-w / 2, w / 2) for (z, y) in ((-a, H), (a, H), (a, H - 0.12), (a - 0.25, H - h), (-a + 0.25, H - h), (-a, H - 0.12))])
    return p
def rain_chain(h):
    """Bocal de aco na testeira e corrente de chuva ate uma bacia de seixos (pivo: ponto sob o bocal, no chao)."""
    p = Piece()
    p.box('metal', -0.06, 0.06, h - 0.05, h + 0.06, -0.06, 0.16)
    n = int((h - 0.25) / 0.09)
    for i in range(n):
        y = h - 0.08 - i * 0.09
        if i % 2: p.box('metal', -0.004, 0.004, y - 0.05, y + 0.05, -0.03, 0.03)
        else: p.box('metal', -0.03, 0.03, y - 0.05, y + 0.05, -0.004, 0.004)
    p.cyl('concrete', 0.32, 0.0, 0.1, 0.0, 0.0, 20); p.cyl('stone2', 0.27, 0.1, 0.12, 0.0, 0.0, 18)
    for i in range(9):
        a = i * 2.4; r = 0.08 + 0.02 * (i % 3); p.sphere('concrete', 0.045, 0.16 * math.cos(a), 0.13, 0.16 * math.sin(a), 1)
    return p

# ============================================================================ carport, cobogo, jardim
CPX0, CPX1, CPZ0, CPZ1 = SX, SX + 6.0, -4.0, 2.0
CH = H - 0.45           # forro do carport (abaixo do beiral da casa)
def cp_deck(edges):
    p = deck(edges); M = trimesh.transformations.translation_matrix([0, CH - H, 0])
    q = Piece(); q.merge(p, M); return q
def cp_post(h=CH - 0.28):
    """Pilar de aco tubular de 15 cm com chapa de base e chapa de topo (pivo: centro, chao)."""
    p = Piece(); p.box('metal', -0.15, 0.15, 0.05, 0.065, -0.15, 0.15); p.cyl('metal', 0.075, 0.065, h - 0.015, 0, 0, 16)
    for (x, z) in ((-0.11, -0.11), (0.11, -0.11), (0.11, 0.11), (-0.11, 0.11)): p.cyl('metal', 0.012, 0.065, 0.085, x, z, 6)
    p.box('metal', -0.1, 0.1, h - 0.015, h, -0.1, 0.1); return p
def cp_beam(L=CPX1 - CPX0 - 0.06):
    """Viga do carport ao longo de X (pivo: ponta na parede da casa, topo no forro do carport)."""
    p = Piece(); h, w = 0.28, 0.12
    p.hull('beam', [(x, y, z) for z in (-w / 2, w / 2) for (x, y) in ((0.0, CH), (L, CH), (L, CH - 0.12), (L - 0.25, CH - h), (0.0, CH - h))])
    p.box('metal', -0.004, 0.2, CH - h + 0.04, CH - 0.04, -w / 2 - 0.008, -w / 2 - 0.002); p.box('metal', -0.004, 0.2, CH - h + 0.04, CH - 0.04, w / 2 + 0.002, w / 2 + 0.008)
    return p
def slab(L=2.0, w=2.0):
    """Placa de concreto de 2 x 2 m com junta de dilatacao em volta (pivo: centro, chao)."""
    p = Piece(); p.cham('concrete', -L / 2 + 0.006, L / 2 - 0.006, 0.0, 0.06, -w / 2 + 0.006, w / 2 - 0.006, 0.006)
    p.box('dark', -L / 2, L / 2, 0.0, 0.045, -w / 2, w / 2); return p
BB = 0.4
def breeze_block():
    """Bloco de cobogo de 40 x 40 x 10 cm: moldura e 4 petalas vazadas em volta de um circulo (pivo: centro da base)."""
    p = Piece(); sq = sbox(-BB / 2 + 0.003, 0.003, BB / 2 - 0.003, BB - 0.003)
    holes = []
    for (dx, dy) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        holes.append(Point(dx * 0.085, BB / 2 + dy * 0.085).buffer(0.07, 10).difference(Point(0, BB / 2).buffer(0.06, 12)))
    shape = sq.difference(unary_union(holes))
    ext(p, 'breeze', shape, -0.05, 0.05); return p
BW_N = 8; BW_M = 5
def breeze_wall():
    """Muro de cobogo de 3,2 x 2,0 m sobre sapata de concreto, com capa (pivo: centro da base)."""
    p = Piece(); L = BW_N * BB
    p.cham('concrete', -L / 2 - 0.05, L / 2 + 0.05, 0.0, 0.2, -0.1, 0.1, 0.008)
    blk = breeze_block()
    for i in range(BW_N):
        for j in range(BW_M):
            M = trimesh.transformations.translation_matrix([-L / 2 + (i + 0.5) * BB, 0.2 + j * BB, 0.0]); p.merge(blk, M)
    p.cham('concrete', -L / 2 - 0.05, L / 2 + 0.05, 0.2 + BW_M * BB, 0.28 + BW_M * BB, -0.09, 0.09, 0.008)
    return p
def planter(L=3.0, w=0.8, h=0.55):
    """Floreira de pedra em L baixo, com cascalho (pivo: canto, chao)."""
    p = Piece(); t = 0.18
    ring = sbox(0, 0, L, w).difference(sbox(t, t, L - t, w - t))
    ext_y(p, 'stone2', ring, 0.0, h - 0.05); ext_y(p, 'concrete', sbox(-0.03, -0.03, L + 0.03, w + 0.03).difference(sbox(t - 0.02, t - 0.02, L - t + 0.02, w - t + 0.02)), h - 0.05, h)
    p.box('roofdeck', t, L - t, 0.0, h - 0.15, t, w - t)
    return p
def lamp_post(h=1.6):
    """Poste de jardim 'atomico': haste de aco e 3 globos leitosos em bracos (pivo: chao)."""
    p = Piece(); p.cyl('concrete', 0.18, 0.0, 0.12, 0, 0, 16); p.cyl('metal', 0.03, 0.12, h, 0, 0, 10)
    for k in range(3):
        a = k * 2 * math.pi / 3; x, z = 0.22 * math.cos(a), 0.22 * math.sin(a); y = h - 0.1 - 0.12 * k
        seg_cyl(p, 'metal', (0, y, 0), (x, y + 0.05, z), 0.012, 6); p.sphere('lamp_glass', 0.08, x, y + 0.12, z, 2)
    p.sphere('metal', 0.04, 0, h, 0, 1); return p
def wall_light():
    """Arandela cilindrica de aco (luz para cima e para baixo). Pivo: face da parede."""
    p = Piece(); p.box('metal', -0.05, 0.05, -0.15, 0.15, 0.0, 0.02)
    p.box('metal', -0.015, 0.015, -0.02, 0.02, 0.02, 0.08); p.cyl('metal', 0.06, -0.18, 0.18, 0.0, 0.13, 16); p.cyl('lamp_glass', 0.05, -0.185, -0.178, 0.0, 0.13, 14)
    p.cyl('lamp_glass', 0.05, 0.178, 0.185, 0.0, 0.13, 14); return p

# ============================================================================ portas e interior
def door_entry(w=0.92, h=2.27, t=0.05):
    """Porta de entrada lisa amarela com 3 visores quadrados em escada e puxador vertical (pivo: dobradica, embaixo)."""
    p = Piece(); slab_ = tbox(0, w, 0, h, -t / 2, t / 2); cut = []
    lites = [(0.22, 0.36, 1.0, 1.14), (0.36, 0.5, 1.3, 1.44), (0.5, 0.64, 1.6, 1.74)]
    for (a, b, c, d) in lites: cut.append(tbox(a, b, c, d, -t, t))
    p.add('door', bl_detail(slab_, cut, bevel=0.004, segments=2))
    for (a, b, c, d) in lites: p.box('glass', a - 0.003, b + 0.003, c - 0.003, d + 0.003, -0.004, 0.004)
    for z in (1, -1):
        p.box('metal', w - 0.14, w - 0.12, 0.7, 1.5, z * (t / 2 + 0.04) - 0.01, z * (t / 2 + 0.04) + 0.01)
        for yy in (0.75, 1.45): p.box('metal', w - 0.14, w - 0.12, yy - 0.01, yy + 0.01, *sorted((z * t / 2, z * (t / 2 + 0.045))))
    for yy in (0.25, 1.1, 1.95): p.cyl('metal', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def door_glass(w=0.87, h=2.3, t=0.05):
    """Porta de vidro de quadro de aluminio estreito, puxador de barra (pivo: dobradica, embaixo)."""
    p = Piece(); s = 0.06
    p.cham('metal', 0, s, 0, h, -t / 2, t / 2, 0.004); p.cham('metal', w - s, w, 0, h, -t / 2, t / 2, 0.004)
    p.cham('metal', s - 0.002, w - s + 0.002, 0, 0.12, -t / 2, t / 2, 0.004); p.cham('metal', s - 0.002, w - s + 0.002, h - s, h, -t / 2, t / 2, 0.004)
    p.box('glass', s - 0.004, w - s + 0.004, 0.116, h - s + 0.004, -0.004, 0.004)
    for z in (1, -1): seg_cyl(p, 'metal', (w - 0.12, 0.85, z * (t / 2 + 0.04)), (w - 0.12, 1.35, z * (t / 2 + 0.04)), 0.015, 8)
    return p
def door_flush(w=0.83, h=2.14, t=0.045):
    """Porta de servico lisa de madeira com visor alto estreito."""
    p = Piece(); p.add('boards', bl_detail(tbox(0, w, 0, h, -t / 2, t / 2), [tbox(0.12, 0.24, 1.1, 1.9, -t, t)], bevel=0.004, segments=2))
    p.box('glass', 0.117, 0.243, 1.097, 1.903, -0.004, 0.004)
    for z in (1, -1): p.sphere('metal', 0.028, w - 0.08, 1.0, z * (t / 2 + 0.05)); p.seg('metal', (w - 0.08, 1.0, z * t / 2), (w - 0.08, 1.0, z * (t / 2 + 0.04)), 0.014)
    return p
def door_int(w=0.84, h=2.08, t=0.04):
    """Porta interna lisa de madeira (folheada) com puxador de barra curta."""
    p = Piece(); p.add('door_int', bl_detail(tbox(0, w, 0, h, -t / 2, t / 2), bevel=0.004, segments=2))
    for z in (1, -1): p.box('metal', w - 0.1, w - 0.08, 0.9, 1.1, z * (t / 2 + 0.03) - 0.008, z * (t / 2 + 0.03) + 0.008); p.box('metal', w - 0.1, w - 0.08, 0.99, 1.01, *sorted((z * t / 2, z * (t / 2 + 0.03))))
    return p
def floor_tile(bath=False):
    p = Piece()
    if bath:
        p.box('dark', -W / 2, W / 2, -0.027, -0.004, -W / 2, W / 2); n = 20; s = W / n
        for i in range(n):
            for j in range(n):
                x0 = -W / 2 + i * s + 0.003; z0 = -W / 2 + j * s + 0.003; p.box('tile', x0, x0 + s - 0.006, -0.03, 0.0, z0, z0 + s - 0.006)
    else: p.box('floor', -W / 2, W / 2, -0.03, 0.0, -W / 2, W / 2)
    p.box('concrete', -W / 2 + 0.02, W / 2 - 0.02, -RAISE + 0.02, -0.03, -W / 2 + 0.02, W / 2 - 0.02); return p
def interior_wall(doorway, h=H, ow=0.9, end=False):
    p = Piece(); t = 0.12; x1 = W / 2 - (T if end else 0.0)
    xs = [-W / 2] + ([-ow / 2, ow / 2] if doorway else []) + [x1]; ys = [0.0, 2.1, h] if doorway else [0.0, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (doorway and i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    if doorway:
        door_casing(p, ow, t)
        for a, b in ((-W / 2, -ow / 2 - 0.09), (ow / 2 + 0.09, x1)): baseboard(p, a, b, t)
    else: baseboard(p, -W / 2, x1, t)
    return p
def step_pad(w=1.8, d=0.9):
    """Degrau de concreto 'flutuante' (pivo: face da parede, centro, cota do piso; avanca para +Z)."""
    p = Piece(); p.cham('concrete', -w / 2, w / 2, -0.1, -0.012, 0.004, d, 0.008); p.box('dark', -w / 2 + 0.05, w / 2 - 0.05, -RAISE + 0.005, -0.1, 0.004, d - 0.08); return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p

# ============================================================================ pecas
FB = [-6, -4, -2, 0, 2, 4, 6]; SB = [-4, -2, 0, 2, 4]
pieces = {f'wall_{k}': wall(k) for k in ('boards', 'render', 'glass', 'glass_door', 'clerestory', 'window', 'entry', 'side_door')}
pieces.update({'corner': corner(), 'fireplace': fireplace(), 'chimney': chimney(), 'beam': beam(), 'cp_post': cp_post(), 'cp_beam': cp_beam(),
               'rain_chain': rain_chain(RAISE + H - 0.12), 'slab': slab(), 'breeze_wall': breeze_wall(), 'planter': planter(), 'lamp_post': lamp_post(),
               'wall_light': wall_light(), 'door_leaf_entry': door_entry(), 'door_leaf_glass': door_glass(), 'door_leaf_service': door_flush(),
               'door_leaf_interior': door_int(), 'floor_tile': floor_tile(), 'floor_tile_bath': floor_tile(True), 'step_pad': step_pad(),
               'interior_wall_plain': interior_wall(False), 'interior_wall_doorway': interior_wall(True), 'interior_wall_end_plain': interior_wall(False, end=True),
               'interior_wall_end_doorway': interior_wall(True, end=True), 'player_scale_ref': player_ref()})
def deck_name(e, pre='deck', extra=''):
    return pre + ('_e' + ''.join(str(int(b)) for b in e) if any(e) else '') + extra
# placas: casa x -8..8, z -6..6 (centros impares); carport x 7..13 (centros 8, 10, 12), z -4..2
HX = [-7, -5, -3, -1, 1, 3, 5, 7]; HZ = [-5, -3, -1, 1, 3, 5]
SKY = {(-3, -1), (3, 1)}; VENT = {(1, 3), (-5, 3)}
for x in HX:
    for z in HZ:
        e = (x == HX[0], x == HX[-1], z == HZ[0], z == HZ[-1])
        n = deck_name(e, extra='_sky' if (x, z) in SKY else '_vent' if (x, z) in VENT else '')
        if n not in pieces: pieces[n] = deck(e, sky=(x, z) in SKY, vent=(x, z) in VENT)
CPXS = [8, 10, 12]; CPZS = [-3, -1, 1]
for x in CPXS:
    for z in CPZS:
        e = (False, x == CPXS[-1], z == CPZS[0], z == CPZS[-1]); n = deck_name(e, 'cp_deck')
        if n not in pieces: pieces[n] = cp_deck(e)

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
Y0 = RAISE
faces = [(0, FB, lambda u: (u, SZ), 'front'), (90, SB, lambda u: (SX, -u), 'right'), (180, FB, lambda u: (-u, -SZ), 'back'), (-90, SB, lambda u: (-SX, u), 'left')]
G = {'front': {-6: 'clerestory', -4: 'window', -2: 'render', 0: 'entry', 2: 'clerestory', 4: 'window', 6: 'boards'},
     'back': {-6: 'glass', -4: 'glass_door', -2: 'glass', 0: 'clerestory', 2: 'clerestory', 4: 'glass_door', 6: 'window'},
     'right': {4: 'clerestory', 2: 'window', 0: 'side_door', -2: 'window', -4: 'boards'},
     'left': {4: 'window', 2: 'boards', 0: 'render', -2: 'fire', -4: 'clerestory'}}
G['front'][6] = 'window'
for ry, bays, f, tag in faces:
    for u in bays:
        x, z = f(u); wk = x if tag in ('front', 'back') else z
        k = G[tag][wk]; put('wall_' + ('render' if k == 'fire' else k), x, Y0, z, ry, [tag, 'ext'])
for ry, x, z, tg in [(0, SX, SZ, ('front', 'right')), (90, SX, -SZ, ('right', 'back')), (180, -SX, -SZ, ('back', 'left')), (-90, -SX, SZ, ('left', 'front'))]:
    put('corner', x, Y0, z, ry, tg + ('ext',))
for x in HX:
    for z in HZ:
        e = (x == HX[0], x == HX[-1], z == HZ[0], z == HZ[-1])
        put(deck_name(e, extra='_sky' if (x, z) in SKY else '_vent' if (x, z) in VENT else ''), x, Y0, z, 0, ['roof'])
for x in FB: put('beam', x, Y0, 0.0, 0, ['roof'])
# lareira (parede esquerda, z = 2 no sentido da face: x=-7, z=-2) e chamine de pedra
put('fireplace', -SX + T, Y0, -2.0, 90, ['left']); put('chimney', -SX, Y0, -2.0, -90, ['left', 'ext'])
# carport: piso, pilares, vigas, placas
for x in CPXS:
    for z in CPZS: put('slab', x, 0.0, z, 0, ['carport'])
for z in (-3.0 - 0.94, -1.0, 1.0 + 0.94): put('cp_post', CPX1 - 0.25, 0.0, z, 0, ['carport'])
for z in (-3.94, -1.0, 1.94): put('cp_beam', CPX0, Y0 + 0.0, z, 0, ['carport', 'roof'])
for x in CPXS:
    for z in CPZS:
        e = (False, x == CPXS[-1], z == CPZS[0], z == CPZS[-1]); put(deck_name(e, 'cp_deck'), x, Y0, z, 0, ['carport', 'roof'])
# portas externas
hx, hz = hinge(0, SZ, 0, -0.79, -0.13); put('door_leaf_entry', hx, Y0 + 0.013, hz, 0, ['front', 'ext'], door=85)
for xx in (-4.0, 4.0):
    hx, hz = hinge(xx, -SZ, 180, -0.95, -0.13); put('door_leaf_glass', hx, Y0 + 0.081, hz, 180, ['back', 'ext'], door=85)
hx, hz = hinge(SX, 0, 90, -0.42, -0.13); put('door_leaf_service', hx, Y0 + 0.013, hz, 90, ['right', 'ext'], door=85)
put('step_pad', 0.0, Y0, SZ, 0, ['front']); put('step_pad', -4.0, Y0, -SZ, 180, ['back']); put('step_pad', SX, Y0, 0.0, 90, ['right'])
put('wall_light', -1.15, Y0 + 1.9, SZ, 0, ['front', 'ext']); put('wall_light', SX, Y0 + 1.9, 0.75, 90, ['right', 'ext'])
put('rain_chain', -SX - OV + 0.15, 0.0, SZ + OV - 0.15, 0, ['front', 'ext'])
put('breeze_wall', 2.6, 0.0, SZ + 1.9, 0, ['front', 'garden'])
put('planter', -5.6, 0.0, SZ + 1.4, 0, ['front', 'garden'])
put('lamp_post', -2.2, 0.0, SZ + 3.2, 0, ['garden'])
for z in (SZ + 2.0, SZ + 4.0): put('slab', 0.0, 0.0, z, 0, ['garden'])
for x in (-6, -4, -2, 0):
    for z in (-SZ - 1.0, -SZ - 3.0): put('slab', x, 0.0, z, 0, ['garden', 'back'])
# piso de dentro e paredes internas
BATH = {(2, -4), (2, -2), (2, 2), (2, 4)}
for a in FB:
    for b in SB: put('floor_tile_bath' if (a, b) in BATH else 'floor_tile', a, Y0, b, 0, ['floor0'])
MX0, MX1, MZ0, MZ1 = -SX, SX, -SZ, SZ
def wl(x0, z0, x1, z1, doors=()):
    y = Y0
    if z0 == z1:
        cs = list(range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2))
        for c in cs:
            end = c in (cs[0], cs[-1]) and (c - 1 == MX0 or c + 1 == MX1); d = c in doors
            ry = 0 if c + 1 == MX1 or not end else 180
            put('interior_wall_' + ('end_' if end else '') + ('doorway' if d else 'plain'), c, y, z0, ry, ['floor0'])
            if d:
                dr = 180 if z0 > 0 and min(x0, x1) >= 0 else 0  # quartos da frente abrem para dentro; a da cozinha abre para a sala
                hx, hz = hinge(c, z0, dr, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, dr, ['floor0'], door=75)
    else:
        cs = list(range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2))
        for c in cs:
            end = (c - 1 == MZ0) or (c + 1 == MZ1); d = c in doors
            ry = (90 if c - 1 == MZ0 else -90) if end else 90
            put('interior_wall_' + ('end_' if end else '') + ('doorway' if d else 'plain'), x0, y, c, ry, ['floor0'])
            if d: hx, hz = hinge(x0, c, ry if end else 90, -0.43, 0); put('door_leaf_interior', hx, y + 0.01, hz, ry if end else 90, ['floor0'], door=75)
wl(1.0, -1.0, 7.0, -1.0, doors=(2, 4)); wl(1.0, 1.0, 7.0, 1.0, doors=(2, 4))
wl(3.0, MZ0, 3.0, -1.0); wl(3.0, 1.0, 3.0, MZ1); wl(1.0, MZ0, 1.0, -1.0); wl(1.0, 1.0, 1.0, MZ1)
wl(MX0, 1.0, -3.0, 1.0, doors=(-4,)); wl(-3.0, 1.0, -3.0, MZ1, doors=(2,))
put('player_scale_ref', 0.6, 0, SZ + 2.6); put('player_scale_ref', -2.5, Y0, -2.0, 0, ['floor0']); put('player_scale_ref', 10.5, 0.06, 0.0, 0, ['carport'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    json.dump({'grid': {'module_width': W, 'wall_height': H, 'wall_thickness': T, 'floor_raise': RAISE, 'footprint': [2 * SX, 2 * SZ], 'overhang': OV,
                        'carport': {'x': [CPX0, CPX1], 'z': [CPZ0, CPZ1], 'ceiling': CH},
                        'roof': 'flat gravel roof, 2x2 m deck tiles centred on odd coordinates (x -8..8, z -6..6), exposed glulam beams along Z at even x',
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
