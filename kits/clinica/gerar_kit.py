"""Kit 33: clinica de bairro de tijolo, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Predio de 24 x 10 m e 2 andares de tijolo vermelho com faixas de concreto aparente nas linhas de peitoril, de verga e de laje,
embasamento de concreto, janelas de aluminio bronze (vidro fixo embaixo, basculante em cima), platibanda com cachorrada de
tijolo e rufo de aluminio. Entrada central com vitrines e porta dupla de vidro, marquise de concreto sobre 2 pilares de tijolo
(com luminarias embutidas no forro), calcada no nivel do piso com rebaixo de guia, pista de embarque, ilha e postes de luz.
Telhado plano com manta, condensadoras, exaustores, respiros, ralos, alcapao e buzinotes com condutores nos fundos.
Dentro: recepcao com balcao e piso de granilite, corredor central, consultorios dos dois lados, banheiros, escada em U de
concreto com corrimao de tubo e saidas de emergencia nas pontas do corredor.
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
configurar(cores={'brick': (148, 62, 46), 'precast': (214, 206, 190), 'alu': (70, 60, 50), 'plaster': (238, 236, 230), 'concrete': (178, 174, 166),
                  'vct': (214, 212, 200), 'vct2': (190, 194, 182), 'terrazzo': (222, 214, 200), 'tile': (232, 236, 236), 'dark': (40, 40, 42),
                  'membrane': (112, 114, 116), 'seam': (88, 90, 92), 'asphalt': (70, 72, 74), 'stripe': (236, 232, 214), 'grass': (100, 146, 72),
                  'hedge': (66, 104, 54), 'leaf': (82, 128, 64), 'leaf2': (150, 120, 50), 'bark': (92, 70, 52), 'wood': (150, 108, 72),
                  'laminate': (236, 232, 222), 'steel': (128, 132, 136), 'grate': (60, 62, 64), 'trim': (240, 238, 232), 'frame': (232, 230, 222),
                  'door_int': (214, 196, 166), 'yellow': (226, 182, 40), 'mulch': (96, 70, 50)},
           texturas={'brick': 'brick', 'precast': 'render', 'plaster': 'plaster', 'concrete': 'render', 'vct': 'plaster', 'vct2': 'plaster',
                     'terrazzo': 'render', 'membrane': 'render', 'asphalt': 'render', 'wood': 'planks'},
           out=OUT)
D.METAL.update({'alu'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.3; H = 3.4; SLAB = 0.25; RAISE = 0.15
H0 = H - SLAB
def lvl(fl): return RAISE + fl * H
YR = lvl(2)                                     # cota da cobertura
PAR = 0.95                                      # topo da platibanda acima da cobertura
HX = 12.0; HZ = 5.0                             # predio: x de -12 a 12, z de -5 a 5
SILL = (0.72, 0.9); HEAD = (2.42, 2.6); SLABB = (-SLAB, 0.0); PLT = 0.35
CZ = 1.0; IT = 0.12                             # corredor de z = -1 a 1, paredes internas de 12 cm
XI = HX - T; ZI = HZ - T                        # faces internas das paredes externas
# escada em U de 2 lances (na ponta oeste, atras do corredor)
NR2 = 10; RS_ = H / (2 * NR2); TR = 0.26; RUN = (NR2 - 1) * TR; SW_ = 1.14
LA = (-XI, -XI + SW_); LB = (-9.36 - SW_, -9.36); ZF = -1.4; ZL = ZF - RUN; YL = NR2 * RS_
HOLE = (-XI, -ZI, -9.36, ZF)                    # vao na laje do 1o andar (x0, z0, x1, z1)

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
    q = Piece(); prof_z(q, mat, 0.0, D_, [(z, y) for (z, y) in prof]); p.add(mat, slice_keep(q.parts[mat][0], [0, 0, 0], np.array([1, 0, -1]) / math.sqrt(2)))

# ============================================================================ fachada
SILL_P = [(0.0, SILL[0]), (0.035, SILL[0]), (0.035, SILL[1] - 0.02), (0.0, SILL[1])]                # faixa de peitoril com pingadeira
HEAD_P = [(0.0, HEAD[0]), (0.022, HEAD[0]), (0.022, HEAD[1] - 0.006), (0.016, HEAD[1]), (0.0, HEAD[1])]
SLAB_P = [(0.0, SLABB[0]), (0.022, SLABB[0] + 0.006), (0.022, SLABB[1] - 0.006), (0.016, SLABB[1]), (0.0, SLABB[1])]
PLINTH_P = lambda y0: [(0.0, y0), (0.03, y0), (0.03, PLT - 0.025), (0.005, PLT), (0.0, PLT)]
def band_segs(holes, y0, y1, x0=-W / 2, x1=W / 2):
    segs = [(x0, x1)]
    for (a, b, c, d) in holes:
        if c < y1 - 1e-6 and d > y0 + 1e-6: segs = [s for (e, f) in segs for s in ((e, min(f, a)), (max(e, b), f)) if s[1] - s[0] > 1e-3]
    return segs
def wall_core(p, y0, top, holes):
    """Parede estanque: tijolo por fora, gesso por dentro (2 cm, ate 5 mm abaixo do topo)."""
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, top - 0.005, top] + [max(y0, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return None if ys[j] >= top - 0.0051 else 'plaster'
        return 'brick'
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
def alu_window(p, ow, oy0, oy1, hopper_y=None):
    """Janela de aluminio bronze no vao (face externa em z = 0): marco de 5 cm recuado 6 cm, montante central, travessa,
    vidro fixo embaixo e basculante em cima; rufo de peitoril e peitoril interno."""
    x = ow / 2; f = 0.05; z0, z1 = -0.14, -0.06
    p.box('alu', -x, -x + f, oy0, oy1, z0, z1); p.box('alu', x - f, x, oy0, oy1, z0, z1)
    p.box('alu', -x + f, x - f, oy1 - f, oy1, z0, z1); p.box('alu', -x + f, x - f, oy0, oy0 + f, z0, z1)
    two = ow > 1.2
    if two: p.box('alu', -0.025, 0.025, oy0 + f, oy1 - f, z0, z1)
    ht = hopper_y if hopper_y is not None else oy0 + f
    if hopper_y is not None: p.box('alu', -x + f, x - f, ht - 0.025, ht + 0.025, z0, z1)
    cols = [(-x + f, -0.025), (0.025, x - f)] if two else [(-x + f, x - f)]
    for (a, b) in cols:
        if hopper_y is not None: p.box('glass', a, b, oy0 + f, ht - 0.025, -0.104, -0.096)
        # basculante: caixilho de 3,5 cm saliente 1 cm, vidro, alavanca
        ya, yb = (ht + 0.025, oy1 - f) if hopper_y is not None else (oy0 + f, oy1 - f)
        s = 0.035
        for (aa, bb, cc, dd) in ((a, a + s, ya, yb), (b - s, b, ya, yb), (a + s, b - s, ya, ya + s), (a + s, b - s, yb - s, yb)):
            p.box('alu', aa + 0.003, bb - 0.003, cc + 0.003, dd - 0.003, z1, z1 + 0.012)
        p.box('glass', a + s, b - s, ya + s, yb - s, -0.074, -0.066)
        p.box('alu', (a + b) / 2 - 0.05, (a + b) / 2 + 0.05, ya + 0.004, ya + 0.02, z0 - 0.025, z0)
    p.box('alu', -x, x, oy0 - 0.0, oy0 + 0.012, z1, 0.045)                                         # rufo de peitoril
    p.box('trim', -x - 0.02, x + 0.02, oy0 - 0.02, oy0 + 0.02, -T - 0.03, z0)                     # peitoril interno
def storefront(p, x0, x1, top, kick=0.35, tb=2.15, mull=()):
    """Vitrine de aluminio de x0 a x1 (vao do chao ate 'top'): rodape de chapa, vidro, travessa, bandeira e montantes."""
    f = 0.05; z0, z1 = -0.16, -0.06
    p.box('alu', x0, x0 + f, 0.0, top, z0, z1); p.box('alu', x1 - f, x1, 0.0, top, z0, z1)
    p.box('alu', x0 + f, x1 - f, top - f, top, z0, z1); p.box('alu', x0 + f, x1 - f, tb - 0.025, tb + 0.025, z0, z1)
    p.box('alu', x0 + f, x1 - f, 0.0, kick, z0 + 0.01, z1 - 0.01); p.box('alu', x0 + f, x1 - f, kick, kick + 0.04, z0, z1)
    xs = [x0 + f] + [v for m in mull for v in (m - 0.025, m + 0.025)] + [x1 - f]
    for m in mull: p.box('alu', m - 0.025, m + 0.025, kick + 0.04, top - f, z0, z1)
    for i in range(0, len(xs), 2):
        a, b = xs[i], xs[i + 1]
        p.box('glass', a, b, kick + 0.04, tb - 0.025, -0.114, -0.106); p.box('glass', a, b, tb + 0.025, top - f, -0.114, -0.106)
def threshold(p, x0, x1, y0):
    p.box('precast', x0, x1, y0, 0.005, -0.165, 0.04)
WINS = {'win': (-0.8, 0.8, SILL[1], HEAD[0]), 'wc': (-0.5, 0.5, 1.62, HEAD[0]), 'store': (-0.9, 0.9, 0.0, HEAD[1]),
        'door': (-0.55, 0.55, 0.0, HEAD[1]), 'entry': (-0.05, 1.0, 0.0, HEAD[1])}
def wall(kind='plain', fl=0):
    """Modulo de 2 m de parede externa (pivo: face externa, cota do piso). kind: plain, win, wc (janela alta de banheiro),
    store (vitrine), door (porta de saida), entry (meia porta dupla da entrada; a outra metade e a peca espelhada entry_r)."""
    p = Piece(); y0 = -RAISE if fl == 0 else -SLAB; top = H0
    holes = [WINS[kind]] if kind in WINS else []
    if kind == 'entry_r': holes = [(-1.0, 0.05, 0.0, HEAD[1])]
    wall_core(p, y0, top, holes)
    if kind == 'win': alu_window(p, 1.6, SILL[1], HEAD[0], hopper_y=1.86)
    if kind == 'wc': alu_window(p, 1.0, 1.62, HEAD[0])
    if kind == 'store': storefront(p, -0.9, 0.9, HEAD[1], mull=(0.0,)); threshold(p, -0.9, 0.9, y0)
    if kind in ('entry', 'entry_r'):
        s = 1 if kind == 'entry' else -1; f = 0.05; z0, z1 = -0.16, -0.06
        xa, xb = sorted((s * -0.05, s * 0.0)); p.box('alu', xa, xb, 0.0, HEAD[1], z0, z1)                     # batente
        xa, xb = sorted((s * 0.97, s * 1.0)); p.box('alu', xa, xb, 0.0, HEAD[1], z0, z1)                      # meio montante central
        xa, xb = sorted((s * 0.0, s * 0.97)); p.box('alu', xa, xb, HEAD[1] - f, HEAD[1], z0, z1); p.box('alu', xa, xb, 2.17, 2.22, z0, z1)
        p.box('glass', xa, xb, 2.22, HEAD[1] - f, -0.114, -0.106)
        xa, xb = sorted((s * -0.05, s * 0.999)); threshold(p, xa, xb, y0)
    if kind == 'door':
        f = 0.05; z0, z1 = -0.16, -0.06
        p.box('alu', -0.55, -0.5, 0.0, HEAD[1], z0, z1); p.box('alu', 0.5, 0.55, 0.0, HEAD[1], z0, z1)
        p.box('alu', -0.5, 0.5, HEAD[1] - f, HEAD[1], z0, z1); p.box('alu', -0.5, 0.5, 2.17, 2.22, z0, z1)
        p.box('glass', -0.5, 0.5, 2.22, HEAD[1] - f, -0.114, -0.106); threshold(p, -0.55, 0.55, y0)
        # luminaria de parede sobre a porta
        p.cham('alu', -0.14, 0.14, 2.72, 2.92, 0.0, 0.16, 0.01); p.box('lamp_glass', -0.11, 0.11, 2.7, 2.722, 0.02, 0.14)
    # faixas de concreto
    for (y_a, y_b, pr) in ((SILL[0], SILL[1], SILL_P), (HEAD[0], HEAD[1], HEAD_P)):
        for (a, b) in band_segs(holes, y_a, y_b): prof_x(p, 'precast', a, b, pr)
    if fl == 1:
        for (a, b) in band_segs(holes, *SLABB): prof_x(p, 'precast', a, b, SLAB_P)
    if fl == 0:
        for (a, b) in band_segs(holes, y0, PLT): prof_x(p, 'precast', a, b, PLINTH_P(y0))
    return p
def corner(fl):
    """Quina externa (pivo: quina externa, cota do piso; paredes em -X e -Z): nucleo de tijolo e cantos das faixas em meia-esquadria."""
    p = Piece(); e = 0.004; y0 = -RAISE if fl == 0 else -SLAB
    p.box('brick', -T + 0.004, e, y0 + 0.003, H0 - 0.004, -T + 0.004, e)
    for pr in ([SILL_P, HEAD_P] + ([SLAB_P] if fl == 1 else []) + ([PLINTH_P(y0)] if fl == 0 else [])): mitre_pair(p, 'precast', pr)
    return p
COPE_Y = PAR - 0.05
def parapet():
    """Platibanda de 2 m (pivo: face externa, cota da cobertura): faixa da laje, tijolo dos dois lados, cachorrada de tijolos
    salientes, rufo de aluminio com pingadeiras e cobre-junta; manta subindo 30 cm com perfil de arremate do lado de dentro."""
    p = Piece()
    xs = [-W / 2, W / 2]; ys = [-SLAB - 0.005, -SLAB, COPE_Y]
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], lambda i, j, k: 'brick' if (j == 1 or k == 0) else None).items(): p.add(m, mesh)
    prof_x(p, 'precast', -W / 2, W / 2, SLAB_P)
    for i in range(8):                                     # cachorrada: tijolos de topo salientes a cada 25 cm
        xc = -W / 2 + 0.125 + i * 0.25
        p.box('brick', xc - 0.05, xc + 0.05, COPE_Y - 0.3, COPE_Y - 0.235, 0.0, 0.035)
    p.box('brick', -W / 2, W / 2, COPE_Y - 0.36, COPE_Y - 0.3, 0.0, 0.018)
    p.box('alu', -W / 2, W / 2, COPE_Y, PAR, -T - 0.03, 0.035)
    p.box('alu', -W / 2, W / 2, COPE_Y - 0.08, COPE_Y, 0.025, 0.035); p.box('alu', -W / 2 + 0.001, W / 2 - 0.001, COPE_Y - 0.08, COPE_Y, -T - 0.03, -T - 0.02)
    for (a, b) in ((-W / 2, -W / 2 + 0.04), (W / 2 - 0.04, W / 2)): p.box('alu', a, b, PAR, PAR + 0.006, -T - 0.035, 0.04)
    p.box('membrane', -W / 2 + 0.001, W / 2 - 0.001, 0.0, 0.3, -T - 0.01, -T)
    p.box('alu', -W / 2 + 0.002, W / 2 - 0.002, 0.28, 0.31, -T - 0.016, -T)
    return p
def corner_p():
    p = Piece(); e = 0.004
    p.box('brick', -T + 0.004, e, -SLAB + 0.003, COPE_Y - 0.002, -T + 0.004, e)
    mitre_pair(p, 'precast', SLAB_P)
    p.box('brick', -0.06, 0.035, COPE_Y - 0.3, COPE_Y - 0.235, -0.06, 0.035)
    p.box('brick', -0.06, 0.018, COPE_Y - 0.36, COPE_Y - 0.3, -0.06, 0.018) if False else mitre_pair(p, 'brick', [(0.0, COPE_Y - 0.36), (0.018, COPE_Y - 0.36), (0.018, COPE_Y - 0.3), (0.0, COPE_Y - 0.3)])
    p.box('alu', -T - 0.03, 0.035, COPE_Y, PAR, -T - 0.03, 0.035)
    p.box('alu', -T - 0.03, 0.035, COPE_Y - 0.08, COPE_Y, 0.025, 0.035); p.box('alu', 0.025, 0.035, COPE_Y - 0.08, COPE_Y, -T - 0.03, 0.025)
    p.box('alu', -T - 0.035, 0.04, PAR, PAR + 0.006, -T - 0.035, 0.04)
    return p
def inner_corner_p():
    """Arremate da manta no canto interno da platibanda (pivo: canto interno na cota da cobertura; platibandas em -X e -Z... do lado de dentro)."""
    p = Piece(); p.box('membrane', -0.01, 0.0, 0.0, 0.3, -0.01, 0.0); return p

# ============================================================================ marquise da entrada (porte-cochere)
CW = 3.3; CD = 5.3; CY = 3.0; CF = 0.5                 # meia-largura, balanco, face de baixo e altura da testeira
PIER_Z = 4.9; PIER_X = 2.75
def canopy():
    """Marquise de concreto (pivo: face da fachada no eixo da entrada, no chao): laje com testeira de concreto, forro de gesso com
    6 luminarias embutidas, manta e rufo em cima, 2 pilares de tijolo com base e capitel de concreto, buzinote e condutor embutido."""
    p = Piece()
    p.box('plaster', -CW + 0.12, CW - 0.12, CY, CY + 0.25, 0.0, CD - 0.12)                          # laje (forro por baixo)
    for s in (-1, 1):                                                                                # testeiras laterais
        a, b = sorted((s * (CW - 0.12), s * CW))
        prof_z(p, 'precast', 0.0, CD - 0.12, [(a, CY - 0.1), (b, CY - 0.1), (b, CY + CF - 0.1), (a, CY + CF - 0.1)]) if False else p.box('precast', a, b, CY - 0.1, CY + CF - 0.1, 0.0, CD - 0.12)
    p.box('precast', -CW, CW, CY - 0.1, CY + CF - 0.1, CD - 0.12, CD)                               # testeira da frente
    p.box('precast', -CW + 0.12, CW - 0.12, CY - 0.1, CY, CD - 0.18, CD - 0.12) if False else None
    ext_y(p, 'membrane', sbox(-CW + 0.12, 0.0, CW - 0.12, CD - 0.12), CY + 0.25, CY + 0.27)
    for (a, b, c, d) in ((-CW - 0.02, CW + 0.02, CD - 0.14, CD + 0.02), (-CW - 0.02, -CW + 0.14, 0.0, CD - 0.14), (CW - 0.14, CW + 0.02, 0.0, CD - 0.14)):
        p.box('alu', a, b, CY + CF - 0.1, CY + CF - 0.06, c, d)
    for (x0_, x1_, z0_, z1_) in ((-CW - 0.02, CW + 0.02, CD + 0.012, CD + 0.02), (-CW - 0.02, -CW - 0.012, 0.0, CD + 0.012), (CW + 0.012, CW + 0.02, 0.0, CD + 0.012)):
        p.box('alu', x0_, x1_, CY + CF - 0.16, CY + CF - 0.1, z0_, z1_)
    # pingadeira (friso) na face de baixo da testeira
    for (a, b, c, d) in ((-CW + 0.02, CW - 0.02, CD - 0.03, CD - 0.02), (-CW + 0.02, -CW + 0.03, 0.02, CD - 0.03), (CW - 0.03, CW - 0.02, 0.02, CD - 0.03)):
        p.box('dark', a, b, CY - 0.104, CY - 0.1, c, d)
    for i, z in enumerate((1.2, 2.6, 4.0)):
        for x in (-1.6, 1.6):
            p.cyl('alu', 0.13, CY - 0.012, CY + 0.001, x, z, 20); p.cyl('lamp_glass', 0.1, CY - 0.016, CY - 0.011, x, z, 20)
    for s in (-1, 1):
        x = s * PIER_X; a = 0.25
        p.box('brick', x - a, x + a, 0.3, CY - 0.15, PIER_Z - a, PIER_Z + a)
        p.cham('precast', x - a - 0.04, x + a + 0.04, 0.0, 0.3, PIER_Z - a - 0.04, PIER_Z + a + 0.04, 0.012)
        p.box('precast', x - a - 0.03, x + a + 0.03, CY - 0.15, CY, PIER_Z - a - 0.03, PIER_Z + a + 0.03)
        for k in range(3):     # frisos de tijolo em sombra no pilar
            y = 0.8 + k * 0.6
            for (xa, xb, za, zb) in ((x - a - 0.01, x + a + 0.01, PIER_Z + a, PIER_Z + a + 0.01), (x - a - 0.01, x + a + 0.01, PIER_Z - a - 0.01, PIER_Z - a)):
                p.box('brick', xa, xb, y, y + 0.065, za, zb)
            for (xa, xb) in ((x - a - 0.01, x - a), (x + a, x + a + 0.01)): p.box('brick', xa, xb, y, y + 0.065, PIER_Z - a, PIER_Z + a)
    # buzinote e condutor descendo pela face de tras de um pilar
    x = PIER_X; zb_ = PIER_Z - 0.25
    p.box('alu', x - 0.06, x + 0.06, CY + 0.26, CY + 0.34, CD - 0.18, CD + 0.12) if False else None
    seg_cyl(p, 'alu', (x, CY - 0.27, zb_ - 0.05), (x, 0.35, zb_ - 0.05), 0.045, 10)
    p.box('alu', x - 0.06, x + 0.06, CY - 0.4, CY - 0.15, zb_ - 0.13, zb_ - 0.03)
    for y in (1.1, 2.25): p.box('alu', x - 0.06, x + 0.06, y, y + 0.03, zb_ - 0.1, zb_)
    return p

# ============================================================================ escada em U de concreto
def flight():
    """Lance reto de 10 espelhos (pivo: canto do 1o degrau do lado x = 0, cota do piso; sobe para -Z, largura SW_): degraus de
    granilite com faixa antiderrapante, espelhos e laje inclinada de concreto com forro de gesso por baixo."""
    p = Piece(); w = SW_
    for i in range(NR2 - 1):
        y = (i + 1) * RS_; z0 = -i * TR
        p.box('terrazzo', 0.0, w, y - 0.03, y, z0 - TR, z0 + 0.02)
        p.box('dark', 0.03, w - 0.03, y, y + 0.002, z0 - 0.04, z0 + 0.01)
        p.box('precast', 0.0, w, y - RS_ - (0.002 if i else 0.0), y - 0.03, z0 - 0.02, z0)
    p.box('precast', 0.0, w, YL - RS_ - 0.002, YL - 0.03, -RUN - 0.02, -RUN)
    # laje inclinada: face de baixo paralela a linha dos degraus, 18 cm abaixo
    k = RS_ / TR
    p.hull('plaster', [(x, y, z) for x in (0.003, w - 0.003) for (z, y) in ((-0.021, 0.0), (-0.3, 0.0), (-RUN, YL - RS_ - 0.2), (-RUN, YL - RS_ - 0.03), (-0.021, RS_ - 0.03))])
    return p
def landing():
    """Patamar de meia altura (pivo: canto x0, z0 da parede, na cota do patamar): laje de granilite com forro, de LA[0] a LB[1]."""
    p = Piece(); x1 = LB[1] - LA[0]; d = ZL - (-ZI)
    p.box('terrazzo', 0.0, x1, -0.03, 0.0, 0.0, d + 0.0)
    p.box('plaster', 0.0, x1, -0.2, -0.03, 0.0, d - 0.002)
    p.box('dark', 0.03, x1 - 0.03, 0.0, 0.002, d - 0.05, d - 0.01)
    return p
def pipe_rail(Ln, rise=0.0, h=0.9, posts=(True, True), wall=False):
    """Corrimao de tubo de aco (pivo: inicio, na cota do piso; vai para +X, sobe 'rise'): tubo, montantes e 2 tubos intermediarios
    (wall=True: corrimao de parede com suportes)."""
    p = Piece(); r = 0.022
    if wall:
        seg_cyl(p, 'steel', (0.0, h, 0.0), (Ln, h + rise, 0.0), r, 10)
        for t in (0.15, Ln / 2, Ln - 0.15):
            y = h + rise * t / Ln; seg_cyl(p, 'steel', (t, y, 0.0), (t, y - 0.07, 0.0), 0.008, 6); seg_cyl(p, 'steel', (t, y - 0.07, 0.0), (t, y - 0.07, -0.07), 0.008, 6)
            p.box('steel', t - 0.03, t + 0.03, y - 0.1, y - 0.04, -0.076, -0.07)
        return p
    seg_cyl(p, 'steel', (0.0, h, 0.0), (Ln, h + rise, 0.0), r, 10)
    for yy in (0.35, 0.62): seg_cyl(p, 'steel', (0.04, yy + rise * 0.04 / max(Ln, 1e-6), 0.0), (Ln - 0.04, yy + rise * (Ln - 0.04) / max(Ln, 1e-6), 0.0), 0.012, 8)
    n = max(1, int(round(Ln / 1.2)))
    for i in range(n + 1):
        t = i * Ln / n
        if (i == 0 and not posts[0]) or (i == n and not posts[1]): continue
        y = rise * t / Ln; seg_cyl(p, 'steel', (t, y, 0.0), (t, y + h, 0.0), 0.02, 10); p.cyl('steel', 0.045, y, y + 0.012, t, 0.0, 12)
    return p
def stair_closure():
    """Fechamentos de gesso da escada (pivo na origem do mundo, cota do terreo): divisoria entre os lances, ate a face de baixo
    do lance de cima e do patamar, e tampa da ponta do lance de cima (lado do corredor)."""
    p = Piece(); k = RS_ / TR
    ub = lambda z: YL + (z - ZL) * k - 0.2                          # face de baixo do lance B (sobe para +Z a partir do patamar)
    xa, xb = LA[1] + 0.003, LB[0] - 0.003
    p.hull('plaster', [(x, y, z) for x in (xa, xb) for (z, y) in ((ZF - 0.003, 0.0), (ZL, 0.0), (ZL, ub(ZL)), (ZF - 0.003, ub(ZF - 0.003)))])
    p.box('plaster', xa, xb, 0.0, YL - 0.2, -ZI, ZL)
    p.hull('plaster', [(x, y, z) for x in (LB[0], LB[1]) for (z, y) in ((ZF, 0.0), (ZF - 0.04, 0.0), (ZF - 0.04, ub(ZF - 0.04)), (ZF, ub(ZF)))])
    return p

# ============================================================================ interior
def run_wall(Ln, h, door_at=None, ow=0.86, t=IT, end_gap=(0.016, 0.016)):
    """Parede interna de comprimento livre (pivo: inicio, eixo; vai para +X), com porta opcional centrada em door_at."""
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
def counter():
    """Balcao da recepcao em L (pivo: centro da frente, no chao; frente para +Z): corpo de madeira com frisos, tampo de laminado,
    prateleira alta de atendimento e mesa baixa por dentro."""
    p = Piece(); L1 = 2.4; dd = 0.7
    p.box('wood', -L1 / 2, L1 / 2, 0.0, 1.02, -dd, 0.0)
    for i in range(1, 8):
        x = -L1 / 2 + i * L1 / 8; p.box('dark', x - 0.004, x + 0.004, 0.08, 0.98, 0.0, 0.004)
    p.box('dark', -L1 / 2 + 0.006, L1 / 2 - 0.006, 0.0, 0.08, -dd + 0.02, 0.008)
    p.cham('laminate', -L1 / 2 - 0.03, L1 / 2 + 0.03, 1.02, 1.06, -0.3, 0.06, 0.008)
    p.cham('laminate', -L1 / 2 + 0.006, L1 / 2 - 0.006, 0.74, 0.77, -dd - 0.05, -0.3, 0.006)
    p.box('wood', -L1 / 2, -L1 / 2 + 0.7, 0.0, 1.02, -dd - 1.0, -dd)
    p.cham('laminate', -L1 / 2 - 0.03, -L1 / 2 + 0.7, 1.02, 1.06, -dd - 1.0, -dd, 0.008)
    for i in range(1, 4):
        z = -dd - i * 0.25; p.box('dark', -L1 / 2 - 0.004, -L1 / 2, 0.08, 0.98, z - 0.004, z + 0.004)
    return p
def floor_tile(kind, lv, holes=(), trim=(0, 0, 0, 0)):
    """Piso de 2 x 2 m: placas vinilicas de 50 cm em 2 tons ('vct'), granilite com juntas de latao ('terrazzo'), ladrilho de
    banheiro ('wc') ou manta da cobertura ('membrane'). lv 'g' = terreo, 'u' = andar, 'r' = cobertura. trim = recuo (x-, x+, z-, z+)."""
    p = Piece(); x0, x1, z0, z1 = -1 + trim[0], 1 - trim[1], -1 + trim[2], 1 - trim[3]
    sq = sbox(x0, z0, x1, z1)
    for (a, b, c, d) in holes: sq = sq.difference(sbox(a, b, c, d))
    if kind == 'vct':
        s = 0.5
        for i in range(4):
            for j in range(4):
                q = sbox(-1 + i * s, -1 + j * s, -1 + (i + 1) * s, -1 + (j + 1) * s).intersection(sq)
                ext_y(p, 'vct' if (i + j) % 2 == 0 else 'vct2', q, -0.03, 0.0)
    elif kind == 'terrazzo':
        ext_y(p, 'terrazzo', sq, -0.03, 0.0)
        for v in (-0.5, 0.5):
            for g in (sbox(v - 0.004, -1, v + 0.004, 1), sbox(-1, v - 0.004, 1, v + 0.004)):
                ext_y(p, 'alu' if False else 'steel', g.intersection(sq.buffer(-0.01)), 0.0, 0.0015)
    elif kind == 'wc':
        ext_y(p, 'dark', sq, -0.027, -0.004); n = 10; s = W / n
        for i in range(n):
            for j in range(n):
                q = sbox(-1 + i * s + 0.004, -1 + j * s + 0.004, -1 + (i + 1) * s - 0.004, -1 + (j + 1) * s - 0.004).intersection(sq.buffer(-0.004))
                ext_y(p, 'tile', q, -0.03, 0.0)
    elif kind == 'membrane':
        ext_y(p, 'membrane', sq, -0.03, 0.0)
        for g in (sbox(-0.02, z0 + 0.02, 0.02, z1 - 0.02), sbox(x0 + 0.02, -0.02, x1 - 0.02, 0.02)):
            q = g
            for (a, b, c, d) in holes: q = q.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
            ext_y(p, 'seam', q, 0.0, 0.004)
    sqi = sbox(x0 + 0.02 * (trim[0] == 0), z0 + 0.02 * (trim[2] == 0), x1 - 0.02 * (trim[1] == 0), z1 - 0.02 * (trim[3] == 0))
    for (a, b, c, d) in holes: sqi = sqi.difference(sbox(a - 0.02, b - 0.02, c + 0.02, d + 0.02))
    if lv == 'g': ext_y(p, 'concrete', sqi, -RAISE + 0.02, -0.03)
    else: ext_y(p, 'plaster', sqi, -SLAB - 0.005, -0.03)
    return p

# ============================================================================ cobertura
def rtu():
    """Equipamento de ar-condicionado de cobertura (pivo: centro, cota da cobertura): base de chapa, gabinete com paineis e
    venezianas, 2 grades de ventilador no topo, dutos descendo para a laje."""
    p = Piece(); a, b, h = 1.2, 0.75, 1.15
    p.box('alu', -a - 0.05, a + 0.05, 0.0, 0.3, -b - 0.05, b + 0.05)
    p.cham('steel', -a, a, 0.3, h, -b, b, 0.012)
    for i in range(16):
        y = 0.4 + i * 0.04
        p.box('grate', -a + 0.1, -0.1, y, y + 0.018, b, b + 0.008)
    for xx in (-a + 0.6, a - 0.4):
        for zz in (b, -b):
            for yy in (0.36, h - 0.06):
                p.box('dark', xx - 0.003, xx + 0.003, 0.36, h - 0.06, zz - (0.004 if zz < 0 else 0), zz + (0.004 if zz > 0 else 0)) if yy == 0.36 else None
    R = 0.34
    for xx in (-0.55, 0.55):
        ext_y(p, 'grate', Point(xx, 0).buffer(R + 0.03, 24).difference(Point(xx, 0).buffer(R, 24)), h, h + 0.04)
        for k in range(6):
            q = Piece(); q.box('grate', -R, R, h + 0.02, h + 0.035, -0.006, 0.006)
            M = trimesh.transformations.rotation_matrix(k * math.pi / 6, [0, 1, 0]); M[:3, 3] = [xx, 0, 0]; p.merge(q, M)
        p.cyl('dark', 0.08, h, h + 0.03, xx, 0.0, 12)
    for (xx, w_) in ((-0.3, 0.5), (0.4, 0.4)):
        p.box('alu', xx - w_ / 2, xx + w_ / 2, 0.0, 0.32, -b - 0.45, -b - 0.05)
    return p
def exhaust():
    p = Piece(); p.cham('alu', -0.3, 0.3, 0.0, 0.25, -0.3, 0.3, 0.01)
    lathe(p, 'steel', [(0.18, 0.25), (0.18, 0.45), (0.32, 0.5), (0.32, 0.56), (0.05, 0.7)], sec=16)
    return p
def vent():
    p = Piece(); p.cham('membrane', -0.18, 0.18, 0.0, 0.06, -0.18, 0.18, 0.02); p.cyl('steel', 0.06, 0.06, 0.55, 0.0, 0.0, 12)
    p.cyl('steel', 0.13, 0.55, 0.6, 0.0, 0.0, 14); p.hull('steel', [(0.13 * math.cos(a), 0.6, 0.13 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)] + [(0, 0.68, 0)])
    return p
def drain():
    p = Piece(); p.cyl('seam', 0.16, 0.0, 0.012, 0.0, 0.0, 16); p.hull('grate', [(0.1 * math.cos(a), 0.012, 0.1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)] + [(0, 0.09, 0)])
    return p
def hatch():
    """Alcapao de cobertura (pivo: centro, cota da cobertura): base de chapa, tampa com reforcos, alca e 2 barras de seguranca."""
    p = Piece(); a = 0.55
    p.box('alu', -a, a, 0.0, 0.32, -a, a)
    p.cham('steel', -a - 0.04, a + 0.04, 0.32, 0.4, -a - 0.04, a + 0.04, 0.01)
    for z in (-0.25, 0.25): p.box('steel', -a, a, 0.4, 0.42, z - 0.02, z + 0.02)
    seg_cyl(p, 'yellow', (-0.12, 0.42, 0.0), (0.12, 0.42, 0.0), 0.015, 8)
    for s in (-1, 1):
        x = s * (a + 0.12)
        seg_cyl(p, 'yellow', (x, 0.0, -0.3), (x, 1.05, -0.3), 0.022, 10); seg_cyl(p, 'yellow', (x, 0.0, 0.3), (x, 1.05, 0.3), 0.022, 10)
        seg_cyl(p, 'yellow', (x, 1.05, -0.3), (x, 1.05, 0.3), 0.022, 10)
    return p
def downspout_piece():
    """Buzinote, caixa coletora e condutor de aluminio (pivo: face da fachada no eixo, no chao; sai para +Z): abracadeiras e bica."""
    p = Piece(); y = YR + 0.04; zc = 0.12
    p.box('alu', -0.12, 0.12, y, y + 0.1, -0.1, 0.16)
    p.hull('alu', [(x, yy, z) for x in (-0.16, 0.16) for (z, yy) in ((0.04, YR - 0.1), (0.3, YR - 0.1), (0.3, YR + 0.12), (0.04, YR + 0.12))] + [(x, YR - 0.35, z) for x in (-0.06, 0.06) for z in (0.07, 0.17)])
    seg_cyl(p, 'alu', (0.0, YR - 0.33, zc), (0.0, 0.3, zc), 0.05, 12)
    seg_cyl(p, 'alu', (0.0, 0.3, zc), (0.0, 0.08, zc + 0.22), 0.05, 12)
    for yy in (1.4, 3.1, 4.9):
        p.box('alu', -0.065, 0.065, yy, yy + 0.04, zc - 0.06, zc + 0.06) if False else None
        for (a, b) in ((-0.065, -0.05), (0.05, 0.065)): p.box('alu', a, b, yy, yy + 0.04, 0.0, zc + 0.02)
        p.box('alu', -0.065, 0.065, yy, yy + 0.04, zc + 0.05, zc + 0.065)
    p.cham('concrete', -0.15, 0.15, 0.03, 0.08, 0.2, 0.75, 0.01)
    return p

# ============================================================================ terreno
def lawn(x0, x1, z0, z1, holes=()):
    p = Piece(); g = sbox(x0, z0, x1, z1)
    for h in holes: g = g.difference(h)
    ext_y(p, 'grass', g, 0.002, 0.03); return p
def sidewalk(poly, y1=RAISE, joint=1.5):
    """Calcada de concreto (pivo: origem do terreno) com juntas a cada 1,5 m."""
    p = Piece(); b = poly.bounds
    xs = np.arange(b[0], b[2] + 1e-6, joint)
    for x in xs:
        q = sbox(x + 0.005, b[1], x + joint - 0.005, b[3]).intersection(poly)
        ext_y(p, 'concrete', q, 0.0, y1)
    ext_y(p, 'dark', poly.buffer(-0.003), 0.0, y1 - 0.008)
    return p
def curb_ramp():
    """Rebaixo de guia na frente da entrada (pivo: eixo, inicio da rampa no lado da calcada): rampa de 1,2 m e abas laterais."""
    p = Piece(); w = 1.0; d = 0.9; y0 = RAISE; y1 = 0.02
    p.hull('concrete', [(x, 0.0, z) for x in (-w, w) for z in (0.0, d)] + [(x, y0, 0.0) for x in (-w, w)] + [(x, y1, d) for x in (-w, w)])
    for s in (-1, 1):
        p.hull('concrete', [(s * w, 0.0, 0.0), (s * w, 0.0, d), (s * w, y0, 0.0), (s * w, y1, d), (s * (w + 0.6), 0.0, d), (s * (w + 0.6), y0, d - 0.004), (s * (w + 0.6), 0.0, 0.0), (s * (w + 0.6), y0, 0.0)])
    for i in range(12):     # piso tatil (domos)
        for j in range(5):
            x = -0.55 + i * 0.1; z = 0.55 + j * 0.07; y = y0 + (y1 - y0) * z / d
            p.cyl('yellow', 0.018, y - 0.01, y + 0.006, x, z, 8)
    return p
def drive(poly):
    p = Piece(); ext_y(p, 'asphalt', poly, 0.0, 0.02)
    return p
def island(poly):
    p = Piece(); ext_y(p, 'concrete', poly, 0.0, RAISE); return p
def tree(h=4.6, r=1.5, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.13, 0.0), (0.1, 0.5), (0.08, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)):
        seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.045, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(7):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65)
        p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    ext_y(p, 'mulch', Point(0, 0).buffer(0.75, 20), 0.0, 0.05)
    return p
def bush(r=0.45):
    p = Piece(); rng = np.random.default_rng(3)
    p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def hedge(Ln=2.0, h=0.8, d=0.6):
    p = Piece(); p.cham('hedge', 0.0, Ln, 0.0, h, -d / 2, d / 2, 0.12)
    rng = np.random.default_rng(int(Ln * 10))
    for _ in range(int(Ln * 6)):
        x = rng.uniform(0.15, Ln - 0.15); y = rng.uniform(0.25, h - 0.05); s = rng.choice([-1, 1])
        p.sphere('hedge', rng.uniform(0.09, 0.14), x, y, s * (d / 2 - 0.06), 1)
    return p
def bollard():
    p = Piece(); lathe(p, 'steel', [(0.1, 0.0), (0.1, 0.95), (0.06, 1.0), (0.0, 1.02)], sec=16)
    for y in (0.75, 0.83): p.cyl('yellow', 0.102, y, y + 0.04, 0.0, 0.0, 16)
    return p
def pole_light(h=5.0):
    """Poste de luz do estacionamento (pivo: centro, no chao): base de concreto, poste de aco, braco e luminaria tipo caixa."""
    p = Piece(); lathe(p, 'concrete', [(0.25, 0.0), (0.25, 0.5), (0.2, 0.55)], sec=12)
    p.cyl('steel', 0.07, 0.55, h, 0.0, 0.0, 10)
    p.box('steel', -0.04, 0.04, h - 0.1, h - 0.03, 0.0, 0.7)
    p.cham('alu', -0.22, 0.22, h - 0.2, h - 0.05, 0.6, 1.2, 0.01); p.box('lamp_glass', -0.18, 0.18, h - 0.205, h - 0.195, 0.65, 1.15)
    return p
def bench():
    """Banco de concreto e madeira (pivo: centro, no chao)."""
    p = Piece(); L1 = 1.8
    for s in (-1, 1): p.cham('concrete', s * 0.75 - 0.08, s * 0.75 + 0.08, 0.0, 0.42, -0.22, 0.22, 0.01)
    for i in range(4): z = -0.2 + i * 0.105; p.cham('wood', -L1 / 2, L1 / 2, 0.42, 0.46, z, z + 0.09, 0.006)
    return p
def sign():
    """Placa de identificacao em pedestal (pivo: centro, no chao), sem texto: base de tijolo, painel de aluminio e capa de concreto."""
    p = Piece()
    p.box('brick', -1.2, 1.2, 0.0, 0.5, -0.2, 0.2); p.cham('precast', -1.25, 1.25, 0.5, 0.56, -0.25, 0.25, 0.01)
    p.box('alu', -1.0, 1.0, 0.56, 1.4, -0.06, 0.06); p.box('stripe', -0.9, 0.9, 0.66, 1.3, 0.06, 0.064); p.box('stripe', -0.9, 0.9, 0.66, 1.3, -0.064, -0.06)
    p.cham('precast', -1.08, 1.08, 1.4, 1.46, -0.1, 0.1, 0.008)
    ext_y(p, 'mulch', sbox(-1.6, -0.6, 1.6, 0.6).difference(sbox(-1.2, -0.2, 1.2, 0.2)), 0.0, 0.05)
    return p
def exit_pad():
    """Patamar de concreto da porta de saida (pivo: face da parede no eixo, no chao; sai para +Z)."""
    p = Piece(); p.cham('concrete', -0.9, 0.9, 0.0, RAISE, 0.0, 1.4, 0.008); return p

# ============================================================================ pecas
pieces = {
    'canopy': canopy(), 'parapet': parapet(), 'corner_p': corner_p(), 'flight': flight(), 'landing': landing(), 'stair_closure': stair_closure(),
    'counter': counter(), 'rtu': rtu(), 'exhaust': exhaust(), 'vent': vent(), 'drain': drain(), 'hatch': hatch(), 'downspout': downspout_piece(),
    'door_leaf_interior': door_interior(0.82, 2.06), 'curb_ramp': curb_ramp(), 'tree': tree(), 'tree_b': tree(5.2, 1.7, 'leaf2', 5), 'bush': bush(),
    'hedge': hedge(), 'bollard': bollard(), 'pole_light': pole_light(), 'bench': bench(), 'sign': sign(), 'exit_pad': exit_pad(),
    'player_scale_ref': player_ref()}
for fl, nm in ((0, 'g'), (1, 'u')):
    for k in ('plain', 'win', 'wc', 'store', 'door', 'entry', 'entry_r'):
        if fl == 1 and k in ('store', 'door', 'entry', 'entry_r'): continue
        pieces[f'w_{nm}_{k}'] = wall(k, fl)
    pieces[f'corner_{nm}'] = corner(fl)

def door_leaf_glass(w=0.96, h=2.15, t=0.045):
    """Folha de vidro com quadro de aluminio (pivo: dobradica, embaixo; vai para +X): montantes largos, rodape alto,
    barra antipanico horizontal e puxador vertical."""
    p = Piece(); s = 0.09
    p.box('alu', 0.0, s, 0.0, h, -t / 2, t / 2); p.box('alu', w - s, w, 0.0, h, -t / 2, t / 2)
    p.box('alu', s, w - s, h - s, h, -t / 2, t / 2); p.box('alu', s, w - s, 0.0, 0.25, -t / 2, t / 2)
    p.box('glass', s, w - s, 0.25, h - s, -0.004, 0.004)
    for z in (1, -1):
        seg_cyl(p, 'steel', (0.12, 1.0, z * (t / 2 + 0.06)), (w - 0.12, 1.0, z * (t / 2 + 0.06)), 0.018, 10) if z < 0 else None
        if z < 0:
            for x in (0.12, w - 0.12): seg_cyl(p, 'steel', (x, 1.0, -t / 2), (x, 1.0, -t / 2 - 0.06), 0.012, 8)
        else:
            x = w - 0.06; seg_cyl(p, 'steel', (x, 0.75, t / 2 + 0.06), (x, 1.35, t / 2 + 0.06), 0.016, 10)
            for y in (0.8, 1.3): seg_cyl(p, 'steel', (x, y, t / 2), (x, y, t / 2 + 0.06), 0.01, 8)
    p.box('alu', 0.0, 0.04, h - 0.02, h, -t / 2 - 0.03, t / 2) if False else None
    return p
def door_leaf_steel(w=0.98, h=2.15, t=0.045):
    """Folha da porta de saida (pivo: dobradica, embaixo): chapa pintada com visor estreito, barra antipanico e mola."""
    p = Piece()
    p.add('alu', bl_detail(tbox(0, w, 0, h, -t / 2, t / 2), [tbox(w - 0.3, w - 0.18, 1.2, 1.9, -t, t)], bevel=0.004, segments=1))
    p.box('glass', w - 0.304, w - 0.176, 1.196, 1.904, -0.004, 0.004)
    seg_cyl(p, 'steel', (0.1, 1.0, -t / 2 - 0.06), (w - 0.1, 1.0, -t / 2 - 0.06), 0.018, 10)
    for x in (0.1, w - 0.1): p.box('steel', x - 0.03, x + 0.03, 0.96, 1.04, -t / 2 - 0.06, -t / 2)
    p.box('steel', 0.05, 0.35, h - 0.08, h - 0.03, -t / 2 - 0.06, -t / 2)
    x = w - 0.07; p.sphere('steel', 0.025, x, 1.0, t / 2 + 0.04); seg_cyl(p, 'steel', (x, 1.0, t / 2), (x, 1.0, t / 2 + 0.03), 0.01, 8)
    return p
pieces['door_leaf_glass'] = door_leaf_glass(); pieces['door_leaf_exit'] = door_leaf_steel()

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
def ftag(fl): return f'floor{fl}'
XM = list(range(-11, 12, 2)); ZM = [-4, -2, 0, 2, 4]
# ---------- fachadas (front +Z, x do mundo) ----------
FRONT = {0: {-11: 'win', -9: 'win', -7: 'win', -5: 'win', -3: 'store', -1: 'entry', 1: 'entry_r', 3: 'store', 5: 'win', 7: 'win', 9: 'win', 11: 'win'},
         1: {x: 'win' for x in XM}}
BACK = {0: {-11: 'plain', -9: 'plain', -7: 'wc', -5: 'win', -3: 'win', -1: 'win', 1: 'win', 3: 'win', 5: 'win', 7: 'win', 9: 'win', 11: 'win'},
        1: {-11: 'win', -9: 'plain', -7: 'wc', -5: 'win', -3: 'win', -1: 'win', 1: 'win', 3: 'win', 5: 'win', 7: 'win', 9: 'win', 11: 'win'}}
LEFT = {0: {-4: 'plain', -2: 'plain', 0: 'door', 2: 'win', 4: 'win'}, 1: {z: 'win' for z in ZM}}
RIGHT = {0: {-4: 'win', -2: 'win', 0: 'door', 2: 'win', 4: 'win'}, 1: {z: 'win' for z in ZM}}
for fl, nm in ((0, 'g'), (1, 'u')):
    y = lvl(fl); tg = ftag(fl)
    for x in XM:
        put(f'w_{nm}_{FRONT[fl][x]}', x, y, HZ, 0, ['front', 'ext', tg]); put(f'w_{nm}_{BACK[fl][x]}', x, y, -HZ, 180, ['back', 'ext', tg])
    for z in ZM:
        put(f'w_{nm}_{LEFT[fl][z]}', -HX, y, z, -90, ['left', 'ext', tg]); put(f'w_{nm}_{RIGHT[fl][z]}', HX, y, z, 90, ['right', 'ext', tg])
    for (x, z, ry) in ((HX, HZ, 0), (HX, -HZ, 90), (-HX, -HZ, 180), (-HX, HZ, -90)): put(f'corner_{nm}', x, y, z, ry, ['ext', tg])
for x in XM:
    put('parapet', x, YR, HZ, 0, ['roof']); put('parapet', x, YR, -HZ, 180, ['roof'])
for z in ZM:
    put('parapet', -HX, YR, z, -90, ['roof']); put('parapet', HX, YR, z, 90, ['roof'])
for (x, z, ry) in ((HX, HZ, 0), (HX, -HZ, 90), (-HX, -HZ, 180), (-HX, HZ, -90)): put('corner_p', x, YR, z, ry, ['roof'])
# portas externas
Y0 = lvl(0)
hx, hz = hinge(-1.0, HZ, 0, 0.0, -0.11); put('door_leaf_glass', hx, Y0 + 0.006, hz, 0, ['front', 'ext', ftag(0)], door=90)
hx, hz = hinge(1.0, HZ, 0, 0.0, -0.11); put('door_leaf_glass', hx, Y0 + 0.006, hz, 180, ['front', 'ext', ftag(0)], door=-90)
hx, hz = hinge(-HX, 0.0, -90, -0.5, -0.11); put('door_leaf_exit', hx, Y0 + 0.006, hz, -90, ['left', 'ext', ftag(0)], door=-90)
hx, hz = hinge(HX, 0.0, 90, -0.5, -0.11); put('door_leaf_exit', hx, Y0 + 0.006, hz, 90, ['right', 'ext', ftag(0)], door=-90)
put('canopy', 0.0, 0.0, HZ, 0, ['front', 'ext'])
for x in (-6.0, 0.0, 6.0): put('downspout', x, 0.0, -HZ, 180, ['back', 'ext'])
# ---------- interior ----------
HI = H0 - 0.005
def corridor(fl, side, rooms):
    """Paredes do corredor: um trecho por sala [(x0, x1, porta?)]; side = +1 (frente, z = 1) ou -1 (fundos, z = -1)."""
    z = side * CZ
    for (a, b, dr) in rooms:
        Ln = round(b - a, 3); c = round(Ln / 2, 3) if dr else None
        nm = f'cw_{int(round(Ln * 100))}' + ('_d' if dr else '')
        if nm not in pieces: pieces[nm] = run_wall(Ln, HI, door_at=c)
        put(nm, a, lvl(fl), z, 0, [ftag(fl)])
        if dr:
            hx, hz = hinge(a + c, z, 0, -0.41, 0); put('door_leaf_interior', hx, lvl(fl) + 0.01, hz, 0, [ftag(fl)], door=-90 * side)
def partitions(fl, side, xs):
    Ln = round(ZI - CZ - IT / 2, 3); nm = f'pw_{int(round(Ln * 100))}'
    if nm not in pieces: pieces[nm] = run_wall(Ln, HI)
    for x in xs:
        if side > 0: put(nm, x, lvl(fl), ZI, 90, [ftag(fl)])
        else: put(nm, x, lvl(fl), -CZ - IT / 2, 90, [ftag(fl)])
for fl in (0, 1):
    if fl == 0: front = [(-XI, -8.0, True), (-8.0, -3.94, True), (3.94, 8.0, True), (8.0, XI, True)]
    else: front = [(-XI, -8.0, True), (-8.0, -4.0, True), (-4.0, 0.0, True), (0.0, 4.0, True), (4.0, 8.0, True), (8.0, XI, True)]
    back = [(-9.36, -6.0, True), (-6.0, -2.0, True), (-2.0, 2.0, True), (2.0, 6.0, True), (6.0, XI, True)]
    corridor(fl, 1, front); corridor(fl, -1, back)
    partitions(fl, 1, [-8.0, -4.0, 4.0, 8.0] if fl == 0 else [-8.0, -4.0, 0.0, 4.0, 8.0])
    partitions(fl, -1, [-9.3, -6.0, -2.0, 2.0, 6.0])
put('counter', -2.2, Y0, 3.0, 0, [ftag(0)])
# escada
put('flight', LA[0], Y0, ZF, 0, [ftag(0)])
put('landing', LA[0], Y0 + YL, -ZI, 0, [ftag(0)])
put('flight', LB[1], Y0 + YL, ZL, 180, [ftag(0)])
put('stair_closure', 0, Y0, 0, 0, [ftag(0)])
pieces['rail_a'] = pipe_rail(LB[0] + 0.03 - LA[0], posts=(False, True)); put('rail_a', LA[0], lvl(1), ZF + 0.03, 0, [ftag(1)])
pieces['hrail'] = pipe_rail(RUN, YL - RS_, h=0.9, wall=True)
put('hrail', LA[0] + 0.0, Y0 + RS_, ZF - 0.0, 90, [ftag(0)]) if False else None
pieces['hrail_wall'] = pipe_rail(RUN, YL - RS_, wall=True)
put('hrail_wall', -XI + 0.076, Y0, ZF, 90, [ftag(0)]); put('hrail_wall', LB[1] - 0.076, Y0 + YL, ZL, -90, [ftag(0)])
pieces['hrail_mid'] = pipe_rail(RUN, YL - RS_, posts=(True, True))
put('hrail_mid', LA[1] - 0.06, Y0 + RS_ * 0.13 / TR, ZF - 0.13, 90, [ftag(0)])
put('hrail_mid', LB[0] + 0.06, Y0 + YL + RS_ * 0.13 / TR, ZL + 0.13, -90, [ftag(0)])
# pisos e cobertura
def kind_at(fl, x, z):
    if fl == 2: return 'membrane'
    if x == -7 and z in (-4, -2): return 'wc'
    if x in (-11, -9) and z in (-4, -2): return 'terrazzo'
    if fl == 0 and -4 < x < 4 and z in (2, 4): return 'terrazzo'
    return 'vct'
TILE_N = {}
def tile_piece(kind, lv, holes, trim):
    key = (kind, lv, tuple(holes), trim)
    if key not in TILE_N:
        nm = f'floor_{kind}_{lv}' + ('_e' + '_'.join(str(int(round(t * 100))) for t in trim) if any(trim) else ''); base = nm; i = 2
        while nm in pieces: nm = f'{base}_h{i}'; i += 1
        pieces[nm] = floor_tile(kind, lv, holes, trim); TILE_N[key] = nm
    return TILE_N[key]
for fl in (0, 1, 2):
    lv = 'g' if fl == 0 else ('r' if fl == 2 else 'u')
    for x in XM:
        for z in ZM:
            tr = (T if x == XM[0] else 0.0, T if x == XM[-1] else 0.0, T if z == ZM[0] else 0.0, T if z == ZM[-1] else 0.0)
            hs = []
            if fl == 1:
                r_ = sbox(x - 1, z - 1, x + 1, z + 1).intersection(sbox(*HOLE))
                if r_.area > 1e-6: bb = r_.bounds; hs.append((round(bb[0] - x, 3), round(bb[1] - z, 3), round(bb[2] - x, 3), round(bb[3] - z, 3)))
            tn = tile_piece(kind_at(fl, x, z), lv, hs, tuple(round(t, 3) for t in tr))
            if pieces[tn].tris() == 0: del pieces[tn]; TILE_N.pop((kind_at(fl, x, z), lv, tuple(hs), tuple(round(t, 3) for t in tr))); continue   # todo dentro do vao da escada
            put(tn, x, lvl(fl), z, 0, [ftag(fl) if fl < 2 else 'roof'])
# cobertura: equipamentos
for (x, z) in ((-4.0, -1.0), (5.0, -1.2)): put('rtu', x, YR, z, 0, ['roof'])
for (x, z) in ((-7.5, 2.5), (8.5, 2.6)): put('exhaust', x, YR, z, 0, ['roof'])
for (x, z) in ((-7.0, -3.0), (1.0, 3.0), (9.6, -3.4)): put('vent', x, YR, z, 0, ['roof'])
for (x, z) in ((-6.0, -4.2), (0.0, -4.2), (6.0, -4.2), (0.0, 1.6)): put('drain', x, YR, z, 0, ['roof'])
put('hatch', -10.5, YR, -3.0, 0, ['roof'])
# ---------- terreno ----------
SW = sbox(-HX - 2.0, HZ, HX + 2.0, HZ + 1.6)
RAMP = (-1.0, HZ + 0.7)
pieces['sidewalk'] = sidewalk(SW.difference(sbox(-1.6, HZ + 0.7, 1.6, HZ + 1.6)))
pieces['drive'] = drive(sbox(-HX - 4.0, HZ + 1.6, HX + 4.0, HZ + 4.6))
pieces['island'] = sidewalk(sbox(-HX - 4.0, HZ + 4.6, HX + 4.0, HZ + 5.4), joint=2.0)
FRONT_LAWN = lawn(-HX - 4.0, HX + 4.0, HZ + 5.4, HZ + 11.0)
pieces['lawn_front'] = FRONT_LAWN
pieces['lawn_back'] = lawn(-HX - 4.0, HX + 4.0, -HZ - 6.0, -HZ)
pieces['lawn_left'] = lawn(-HX - 4.0, -HX, -HZ, HZ, [sbox(-HX - 1.4, -0.9, -HX, 0.9)])
pieces['lawn_right'] = lawn(HX, HX + 4.0, -HZ, HZ, [sbox(HX, -0.9, HX + 1.4, 0.9)])
pieces['lawn_corner_l'] = lawn(-HX - 4.0, -HX - 2.0, HZ, HZ + 1.6); pieces['lawn_corner_r'] = lawn(HX + 2.0, HX + 4.0, HZ, HZ + 1.6)
for nm in ('sidewalk', 'drive', 'island', 'lawn_front', 'lawn_back', 'lawn_left', 'lawn_right', 'lawn_corner_l', 'lawn_corner_r'): put(nm, 0, 0, 0, 0, ['site'])
put('curb_ramp', 0.0, 0.0, HZ + 0.7, 0, ['site'])
put('exit_pad', -HX, 0.0, 0.0, -90, ['site']); put('exit_pad', HX, 0.0, 0.0, 90, ['site'])
for x in (-8.0, 8.0): put('pole_light', x, 0.0, HZ + 5.0, 180, ['site'])
for x in (-1.6, 1.6): put('bollard', x, RAISE, HZ + 1.3, 0, ['site'])
put('bench', -6.0, RAISE, HZ + 1.0, 180, ['site']); put('bench', 6.0, RAISE, HZ + 1.0, 180, ['site'])
put('sign', -7.0, 0.0, HZ + 8.5, 0, ['site'])
for (x, z, nm) in ((-12.5, HZ + 8.0, 'tree'), (4.0, HZ + 8.3, 'tree_b'), (13.0, HZ + 8.0, 'tree'), (-14.0, -3.0, 'tree_b'), (14.5, -6.5, 'tree'), (-6.0, -HZ - 3.5, 'tree'), (6.0, -HZ - 3.8, 'tree_b')):
    put(nm, x, 0.0, z, 0, ['site'])
for (x, z) in ((-13.0, 3.5), (-13.0, 2.0), (13.0, 3.6), (13.0, 2.2), (-13.0, -2.2), (13.0, -2.6), (-10.0, HZ + 9.6), (10.0, HZ + 9.6), (-3.0, HZ + 9.4)):
    put('bush', x, 0.03, z, 0, ['site'])
for x0 in np.arange(-HX - 3.5, HX + 3.0, 2.0): put('hedge', float(x0), 0.03, -HZ - 5.6, 0, ['site'])
put('player_scale_ref', -4.0, RAISE, HZ + 1.0); put('player_scale_ref', 1.5, Y0, 2.0, 0, [ftag(0)])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE,
                       'building': {'x': [-HX, HX], 'z': [-HZ, HZ], 'floors': 2, 'roof_level': YR, 'parapet_top': YR + PAR},
                       'stair_holes': {'1': [list(HOLE)]}, 'roof': 'flat membrane roof behind a brick parapet with aluminium coping',
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
# folha da janela em no proprio, para o jogo abrir (scripts/detalhe/folhas.py, grava janelas.json)
import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe')); import folhas as _folhas
_folhas.kit(OUT)
