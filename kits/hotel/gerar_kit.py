"""Kit 37: hotel de 12 andares, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Embasamento de 2 andares (16 x 16 m) de tijolo salmao com vitrines, porta dupla de vidro, faixas de concreto e platibanda com
capa; terraco no teto do embasamento com piso de placas, floreiras, arvores e espreguicadeiras. Torre de 10 andares (12 x 12 m)
de reboco creme com faixas de laje, janelas, portas de correr para sacadas com guarda-corpo de vidro verde e um pano de vidro
azul sobre o nucleo da escada. Cobertura com casa de maquinas, condensadoras, platibanda e letreiro sem texto (estrela).
Marquise na entrada com teto verde, claraboias redondas e luzes embutidas.
Dentro: saguao com recepcao, sala de estar, bar, pilares; salao de eventos no 2o andar; em cada andar da torre, corredor com
5 quartos (cama, criados-mudos, TV, guarda-roupa, poltrona, banheiro com chuveiro, vaso e bancada), escada em U e elevador.
Fora: rampa de embarque sob a marquise, pista em laco, calcadas, floreiras, mastros com bandeiras lisas, postes, bancos.
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
configurar(cores={'render': (234, 226, 208), 'brick': (182, 112, 88), 'band': (150, 152, 156), 'cill': (206, 200, 190), 'frame': (58, 62, 68),
                  'gglass': (120, 176, 160), 'bglass': (70, 112, 152), 'mull': (60, 70, 84), 'plaster': (240, 236, 226), 'ceil': (246, 244, 238),
                  'carpet': (96, 70, 84), 'carpet2': (176, 160, 136), 'tile': (222, 222, 216), 'stone_f': (214, 206, 190), 'wood': (150, 104, 66),
                  'paver': (176, 170, 160), 'concrete': (184, 180, 172), 'asphalt': (66, 66, 68), 'grass': (100, 146, 70), 'hedge': (64, 104, 52),
                  'leaf': (86, 130, 62), 'leaf2': (110, 146, 70), 'bark': (96, 72, 52), 'mulch': (88, 64, 46), 'steel': (196, 198, 200),
                  'gold': (204, 164, 76), 'fabric': (112, 126, 140), 'fabric2': (178, 92, 62), 'linen': (242, 240, 234), 'porcelain': (242, 242, 238),
                  'door': (110, 80, 56), 'door_int': (226, 214, 186), 'flag_r': (190, 52, 46), 'flag_b': (52, 86, 150), 'flag_w': (238, 236, 228),
                  'membrane': (180, 180, 176), 'unit': (176, 180, 178), 'paint_w': (234, 234, 228), 'paint_y': (230, 190, 52), 'curb': (196, 192, 184),
                  'sign': (34, 48, 78), 'rug': (150, 60, 52), 'dkwood': (92, 62, 44), 'gutter': (150, 152, 156), 'bottle': (90, 130, 90)},
           texturas={'render': 'render', 'brick': 'brick', 'plaster': 'plaster', 'stone_f': 'stone', 'wood': 'planks', 'paver': 'stone',
                     'concrete': 'render', 'asphalt': 'render', 'grass': 'render', 'membrane': 'render', 'carpet': 'render', 'carpet2': 'render',
                     'dkwood': 'planks'},
           out=OUT)
D.METAL.update({'steel', 'gold', 'unit', 'mull'}); MATS = D.MATS; TEX = D.TEX

# ============================================================================ medidas
W = 2.0; T = 0.25; SLAB = 0.25; t_ = 0.12                 # modulo, parede externa, laje, parede interna
Y0 = 0.15; HP = 3.6; Y1 = Y0 + HP; YT = Y1 + HP           # terreo, 2o andar e terraco (teto do embasamento)
HF = 3.0; NF = 10; YR = YT + NF * HF                      # andares da torre e cobertura
PX = 8.0; PZ0, PZ1 = -6.0, 10.0                           # embasamento: x de -8 a 8, z de -6 a 10
TX = 6.0; TZ0, TZ1 = -6.0, 6.0                            # torre: x de -6 a 6, z de -6 a 6
PAR = 1.1                                                 # platibandas
ZF = 0.09; ZB = -1.43                                     # eixos das paredes do corredor (frente e fundos)
XS = 0.3                                                  # parede entre a escada e o elevador
SD = -1.4                                                 # porta da escada (alinhada com o lance que sobe)
ZL = -2.49                                                # borda do patamar do andar (inicio dos lances)
ZBB = -3.30                                               # eixo da parede dos banheiros dos quartos dos fundos
ZBK = -5.88                                               # fim das paredes do nucleo na torre (face interna do pano de vidro)
CEIL = HF - SLAB                                          # pe-direito livre da torre

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
def rot_y(deg, t=(0, 0, 0)):
    M = trimesh.transformations.rotation_matrix(math.radians(deg), [0, 1, 0]); M[:3, 3] = t; return M
def mirror_x(x0=0.0):
    M = np.eye(4); M[0, 0] = -1; M[0, 3] = 2 * x0; return M
def mirror_z(z0=0.0):
    M = np.eye(4); M[2, 2] = -1; M[2, 3] = 2 * z0; return M
def tr(x=0.0, y=0.0, z=0.0): return trimesh.transformations.translation_matrix([x, y, z])
def along(p, q, x0, z0, x1, z1, y=0.0):
    ang = math.degrees(math.atan2(-(z1 - z0), x1 - x0)); p.merge(q, rot_y(ang, (x0, y, z0)))
def segs_excl(gaps, a0=-1.0, a1=1.0, pad=0.0):
    segs = [(a0, a1)]
    for (a, b) in gaps: segs = [s for (c, d) in segs for s in ((c, min(d, a - pad)), (max(c, b + pad), d)) if s[1] - s[0] > 1e-3]
    return segs
def trimmed(p, pt, n):
    """Copia de p cortada por um plano (fica o lado para onde n aponta)."""
    q = Piece()
    for m, ms in p.parts.items():
        for mesh in ms:
            b = mesh.bounds; d = np.dot(np.array(n, float), np.array(pt, float))
            lo = min(np.dot(n, [x, y, z]) for x in b[:, 0] for y in b[:, 1] for z in b[:, 2]); hi = max(np.dot(n, [x, y, z]) for x in b[:, 0] for y in b[:, 1] for z in b[:, 2])
            if lo >= d - 1e-9: q.add(m, mesh)
            elif hi > d + 1e-9: q.add(m, slice_keep(mesh, pt, n))
    return q
def mirrored(p, M):
    """Copia de p transformada por M (pode espelhar: o trimesh corrige o sentido das faces)."""
    q = Piece(); q.merge(p, M); return q

# ============================================================================ paredes externas
BAND_PROF = [(0.0, -SLAB - 0.02), (0.03, -SLAB - 0.02), (0.03, 0.03), (0.0, 0.03)]
PLINTH = [(0.0, -Y0), (0.03, -Y0), (0.03, 0.27), (0.015, 0.3), (0.0, 0.3)]
BASE_IN = [(-T, 0.0), (-T - 0.016, 0.0), (-T - 0.016, 0.1), (-T - 0.008, 0.115), (-T, 0.118)]
COPING = [(-T - 0.04, 0.0), (0.05, 0.0), (0.05, 0.05), (0.03, 0.07), (-T - 0.04, 0.08)]
def wall_core(p, holes, h, y0=0.0, out='render', inner_top=None, par=None):
    """Parede de 2 m: material externo, gesso por dentro ate inner_top (acima disso, e na platibanda, o material externo)."""
    it = (h - 0.005) if inner_top is None else inner_top; top = h + (par or 0.0)
    xs = sorted(set([-W / 2, W / 2] + [v for hh in holes for v in hh[:2]]))
    ys = sorted(set([y0, 0.0, it, top] + ([h] if par else []) + [v for hh in holes for v in hh[2:]]))
    ys = [v for v in ys if y0 <= v <= top]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0: return 'plaster' if 0 < cy < it else (out if cy > h or cy < 0 else None)
        return out
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
def casement(p, a, b, y0, y1, mat='frame', split=True):
    """Janela de aluminio no vao (face externa em z = 0): marco, folhas, vidro, peitoril de concreto e soleira interna."""
    z0, z1 = -0.16, -0.06; f = 0.05; zg = (z0 + z1) / 2
    p.box(mat, a, a + f, y0, y1, z0, z1); p.box(mat, b - f, b, y0, y1, z0, z1)
    p.box(mat, a + f, b - f, y1 - f, y1, z0, z1); p.box(mat, a + f, b - f, y0, y0 + f, z0, z1)
    p.box('glass', a + f, b - f, y0 + f, y1 - f, zg - 0.003, zg + 0.003)
    if split:
        xm = (a + b) / 2; p.box(mat, xm - 0.03, xm + 0.03, y0 + f, y1 - f, z0 + 0.01, z1 - 0.01)
        for s in (-1, 1): p.box('steel', xm + s * 0.06 - 0.008, xm + s * 0.06 + 0.008, (y0 + y1) / 2 - 0.08, (y0 + y1) / 2 + 0.08, z0 - 0.02, z0)
    prof_x(p, 'cill', a - 0.05, b + 0.05, [(0.0, y0 - 0.06), (0.05, y0 - 0.06), (0.05, y0 - 0.03), (0.0, y0)])
    p.box('cill', a - 0.02, b + 0.02, y0 - 0.02, y0 + 0.01, -T - 0.03, -0.16)
def slider(p, a, b, h):
    """Porta de correr de 2 folhas (uma fixa e uma aberta pela metade), trilho e soleira."""
    z0, z1 = -0.18, -0.04; f = 0.05
    p.box('frame', a, a + f, 0.0, h, z0, z1); p.box('frame', b - f, b, 0.0, h, z0, z1); p.box('frame', a + f, b - f, h - f, h, z0, z1)
    p.box('frame', a, b, -0.02, 0.012, z0 - 0.06, 0.04)
    xm = (a + b) / 2; w = (b - a - 2 * f) / 2
    for (xa, za, zb) in ((a + f, -0.09, -0.05), (a + f + w * 0.04, -0.15, -0.11)):
        xb = xa + w + 0.03
        p.box('frame', xa, xa + 0.06, 0.012, h - f, za, zb); p.box('frame', xb - 0.06, xb, 0.012, h - f, za, zb)
        p.box('frame', xa + 0.06, xb - 0.06, 0.012, 0.12, za, zb); p.box('frame', xa + 0.06, xb - 0.06, h - f - 0.06, h - f, za, zb)
        p.box('glass', xa + 0.06, xb - 0.06, 0.12, h - f - 0.06, (za + zb) / 2 - 0.003, (za + zb) / 2 + 0.003)
        p.box('steel', xb - 0.05, xb - 0.03, 0.9, 1.2, zb, zb + 0.02)
def tw(kind='plain'):
    """Modulo da torre (pivo: face externa, cota do piso do andar): win, bal (porta de correr da sacada), plain, curt (pano de vidro
    azul do nucleo). Faixa de concreto na laje, rodape interno."""
    p = Piece(); holes = []
    if kind == 'curt':
        for (xa, xb) in ((-1.0, -0.97), (-0.025, 0.025), (0.97, 1.0)): p.box('mull', xa, xb, -SLAB - 0.02, HF - SLAB - 0.02, -0.12, 0.06)
        p.box('mull', -1.0, 1.0, -SLAB - 0.02, 0.1, -0.12, 0.06)
        for y in (1.25,): p.box('mull', -0.97, 0.97, y - 0.025, y + 0.025, -0.1, 0.04)
        p.box('bglass', -0.97, 0.97, 0.1, HF - SLAB - 0.015, -0.033, -0.027)
        p.box('band', -1.0, 1.0, -SLAB - 0.02, 0.1, -T + 0.003, -0.12)
        return p
    if kind == 'win': holes = [(-0.6, 0.6, 0.9, 2.4)]
    if kind == 'bal': holes = [(-0.8, 0.8, 0.0, 2.3)]
    if kind == 'cwin_l': holes = [(-0.25, 0.75, 0.9, 2.4)]
    if kind == 'cwin_r': holes = [(-0.75, 0.25, 0.9, 2.4)]
    wall_core(p, holes, HF, 0.0, 'render', inner_top=HF)
    p.box('render', -1.0, 1.0, HF - SLAB, HF - SLAB - 0.02 + 0.02, -T, 0.0) if False else None
    prof_x(p, 'band', -1.0, 1.0, BAND_PROF)
    gaps = []
    if kind == 'win': casement(p, -0.6, 0.6, 0.9, 2.4)
    if kind in ('cwin_l', 'cwin_r'): a, b = holes[0][:2]; casement(p, a, b, 0.9, 2.4, split=False)
    if kind == 'bal': slider(p, -0.8, 0.8, 2.3); gaps = [(-0.8, 0.8)]
    for (a, b) in segs_excl(gaps, -0.999, 0.999, 0.0): prof_x(p, 'trim', a, b, BASE_IN)
    return p
def tcorner(h=HF, mat='render'):
    """Quina da torre (pivo: quina externa; paredes em -X e -Z): nucleo e faixa de laje em meia-esquadria."""
    p = Piece(); e = 0.004
    p.box(mat, -T + e, e, 0.0, h, -T + e, e); mitre_pair(p, 'band', BAND_PROF)
    return p

# ============================================================================ embasamento
GH = 3.0                                                  # verga das vitrines do terreo
def pod_ground(kind='plain'):
    """Modulo do terreo do embasamento (pivo: face externa, cota do piso): glass (vitrine com bandeira e rodape de aluminio),
    door_l / door_r (metades da porta dupla de vidro), svc (porta de servico), plain. Tijolo, embasamento de pedra, verga."""
    p = Piece(); holes = []; gaps = []
    if kind == 'glass': holes = [(-0.8, 0.8, 0.0, GH)]
    if kind == 'svc': holes = [(-0.5, 0.5, 0.0, 2.2)]; gaps = [(-0.5, 0.5)]
    if kind in ('door_l', 'door_r'):
        s = 1 if kind == 'door_l' else -1; a, b = sorted((s * 0.1, s * 1.0)); holes = [(a, b, 0.0, GH)]; gaps = [(a, b)] if True else []
    wall_core(p, holes, HP, -Y0, 'brick', inner_top=HP)
    p.box('brick', -1.0, 1.0, HP - SLAB, HP - SLAB + 0.0001, -T, 0.0) if False else None
    if kind == 'glass':
        a, b = -0.8, 0.8; z0, z1 = -0.18, -0.06
        p.box('frame', a, a + 0.06, 0.0, GH, z0, z1); p.box('frame', b - 0.06, b, 0.0, GH, z0, z1); p.box('frame', a + 0.06, b - 0.06, GH - 0.06, GH, z0, z1)
        p.box('frame', a + 0.06, b - 0.06, 0.0, 0.35, z0, z1); p.box('frame', a + 0.06, b - 0.06, 2.4, 2.46, z0, z1)
        p.box('glass', a + 0.06, b - 0.06, 0.35, GH - 0.06, -0.123, -0.117)
        p.box('cill', a, b, -0.02, 0.0, -T, 0.02) if False else None
        p.box('trim', a - 0.02, b + 0.02, 0.33, 0.36, -T - 0.03, -0.18)
    if kind in ('door_l', 'door_r'):
        s = 1 if kind == 'door_l' else -1; a, b = sorted((s * 0.1, s * 1.0)); z0, z1 = -0.18, -0.06
        jamb = sorted((s * 0.94, s * 1.0)) if s > 0 else sorted((s * 0.94, s * 1.0))
        p.box('frame', *sorted((s * 0.94, s * 1.0)) if False else sorted((s * 0.1, s * 0.16)), 0.0, GH, z0, z1)
        p.box('frame', a, b, GH - 0.06, GH, z0, z1); p.box('frame', a, b, 2.36, 2.42, z0, z1)
        p.box('glass', a + (0.06 if s > 0 else 0.0), b - (0.0 if s > 0 else 0.06), 2.42, GH - 0.06, -0.123, -0.117)
    if kind == 'svc':
        q = Piece(); door_casing(q, 1.0, T, 2.2); p.merge(q, tr(0, 0, -T / 2))
        q = wall_lantern(); p.merge(q, tr(0, 2.55, 0.0))
    for (a, b) in gaps: p.box('cill', a + (0.001 if abs(a + 1) < 1e-6 else 0.0), b - (0.001 if abs(b - 1) < 1e-6 else 0.0), -0.03, 0.006, -T + 0.004, 0.06)
    pad = 0.09 if kind == 'svc' else 0.0
    for (a, b) in segs_excl([(-0.8, 0.8)] if kind == 'glass' else gaps, pad=pad): prof_x(p, 'cill', a, b, PLINTH)
    for (a, b) in segs_excl([(-0.8, 0.8)] if kind == 'glass' else gaps, -0.999, 0.999, pad): prof_x(p, 'trim', a, b, BASE_IN)
    lint = [(-0.9, 0.9)] if kind == 'glass' else ([sorted((s_ * 0.0, s_ * 1.0)) for s_ in ([1] if kind == 'door_l' else [-1])] if kind in ('door_l', 'door_r') else [])
    for (a, b) in lint: p.cham('cill', a, b, GH, GH + 0.18, 0.0, 0.035, 0.006)
    return p
def pod_upper(kind='win', par=True):
    """Modulo do 2o andar do embasamento (pivo: face externa, cota do piso): faixa de laje, janela, platibanda com capa."""
    p = Piece(); holes = [(-0.7, 0.7, 0.9, 2.6)] if kind == 'win' else []
    wall_core(p, holes, HP, 0.0, 'brick', inner_top=HP, par=PAR if par else None)
    prof_x(p, 'band', -1.0, 1.0, BAND_PROF)
    if kind == 'win':
        casement(p, -0.7, 0.7, 0.9, 2.6); p.cham('cill', -0.8, 0.8, 2.6, 2.75, 0.0, 0.035, 0.006)
    if par:
        y = HP + PAR; prof_x(p, 'cill', -1.0, 1.0, [(z, y + yy) for (z, yy) in COPING])
        prof_x(p, 'band', -1.0, 1.0, [(0.0, HP - 0.02), (0.03, HP - 0.02), (0.03, HP + 0.3), (0.0, HP + 0.3)])
    for (a, b) in segs_excl([], -0.999, 0.999): prof_x(p, 'trim', a, b, BASE_IN)
    return p
def pcorner(par=True):
    """Quina do embasamento (pivo: quina externa, cota do piso do terreo; paredes em -X e -Z), 2 andares e platibanda."""
    p = Piece(); e = 0.004; top = 2 * HP + (PAR if par else -SLAB)
    p.box('brick', -T + e, e, -Y0, top, -T + e, e)
    mitre_pair(p, 'cill', PLINTH)
    q = Piece(); mitre_pair(q, 'band', BAND_PROF); p.merge(q, tr(0, HP, 0))
    if par:
        q = Piece(); mitre_pair(q, 'band', [(0.0, -0.02), (0.03, -0.02), (0.03, 0.3), (0.0, 0.3)]); p.merge(q, tr(0, 2 * HP, 0))
        q = Piece(); mitre_pair(q, 'cill', [(z + T + 0.04 - 0.0, y) for (z, y) in COPING] if False else [(0.0, 0.0), (0.05, 0.0), (0.05, 0.05), (0.03, 0.07), (0.0, 0.08)]); p.merge(q, tr(0, 2 * HP + PAR, 0))
        p.box('cill', -T - 0.04, 0.0, 2 * HP + PAR, 2 * HP + PAR + 0.08, -T - 0.04, 0.0)
    return p

# ============================================================================ lajes, escada, paredes internas
STAIR_HOLE = sbox(-1.939, -5.75, 0.24, ZL)
def slab_typ(kind='typ'):
    """Laje de um andar da torre (pivo: centro, cota do piso): carpete do corredor e dos quartos, piso dos banheiros, patamar,
    abertura da escada, forro liso por baixo. kind 'roof': manta impermeavel por cima."""
    p = Piece(); inner = sbox(-TX + T, TZ0 + T, TX - T, TZ1 - T).difference(STAIR_HOLE)
    ext_y(p, 'ceil', inner, -SLAB, -SLAB + 0.01); ext_y(p, 'concrete', inner, -SLAB + 0.01, -0.012)
    if kind == 'roof':
        ext_y(p, 'membrane', inner, -0.012, 0.0); return p
    corr = sbox(-TX + T, ZB, TX - T, ZF)
    baths = [sbox(xa, ZF, xa + 2.06, 1.96) for xa in (-5.75, -1.94)] + [sbox(5.75 - 2.06, ZF, 5.75, 1.96)] + [sbox(-5.75, ZBB, -5.75 + 2.06, ZB), sbox(5.75 - 2.06, ZBB, 5.75, ZB)]
    land = sbox(-1.94, ZL, 0.24, ZB)
    rest = inner.difference(unary_union([corr, land] + baths))
    ext_y(p, 'carpet', corr.difference(land), -0.012, 0.0); ext_y(p, 'stone_f', land, -0.012, 0.0)
    for b in baths: ext_y(p, 'tile', b.intersection(inner), -0.012, 0.0)
    ext_y(p, 'carpet2', rest, -0.012, 0.0)
    return p
def stair_u(H, n, zback=TZ0 + T):
    """Escada em U do nucleo (pivo: origem do predio, cota do piso do andar): lance que desce de ZL para os fundos, patamar e lance
    que volta ate ZL no andar de cima; degraus macicos de concreto com bocel, corrimaos nas paredes e guarda-corpo central."""
    p = Piece(); r = H / (2 * n); g = 0.26; xa0, xa1 = -1.94, -0.89; xb0, xb1 = -0.81, 0.24
    zl = ZL - (n - 1) * g
    for i in range(1, n):
        z0, z1 = ZL - i * g, ZL - (i - 1) * g; y = i * r
        p.box('concrete', xa0, xa1, max(0.0, y - r - 0.16), y, z0, z1); p.box('band', xa0, xa1, y - 0.03, y + 0.004, z0, z0 + 0.03) if False else p.box('band', xa0, xa1, y, y + 0.004, z1 - 0.04, z1)
    p.box('concrete', xa0, xb1, H / 2 - 0.2, H / 2, zback, zl)
    for i in range(1, n):
        z0, z1 = zl + (i - 1) * g, zl + i * g; y = H / 2 + i * r
        p.box('concrete', xb0, xb1, y - r - 0.16, y, z0, z1); p.box('band', xb0, xb1, y, y + 0.004, z0, z0 + 0.04)
    p.box('concrete', xa1, xb0, 0.0, H / 2, zl, ZL)
    # corrimaos
    for (x, za, zb, ya, yb) in ((-1.9, ZL, zl, 0.9, H / 2 + 0.9), (0.2, zl, ZL, H / 2 + 0.9, H + 0.9)):
        seg_cyl(p, 'steel', (x, ya, za), (x, yb, zb), 0.02, 8)
        for z in np.linspace(za, zb, 4): seg_cyl(p, 'steel', (x, ya + (yb - ya) * (z - za) / (zb - za), z), (x + (0.04 if x < 0 else -0.04), ya + (yb - ya) * (z - za) / (zb - za), z), 0.008, 6)
    for (za, zb, ya, yb) in ((ZL, zl, 0.0, H / 2), (zl, ZL, H / 2, H)):
        top = lambda z: ya + (yb - ya) * (z - za) / (zb - za) + 0.95
        seg_cyl(p, 'steel', (-0.85, top(za), za), (-0.85, top(zb), zb), 0.022, 8)
        for z in np.arange(min(za, zb) + 0.12, max(za, zb) - 0.05, 0.12):
            yy = ya + (yb - ya) * (z - za) / (zb - za); p.box('steel', -0.86, -0.84, yy + (r if ya == 0 else r), top(z), z - 0.008, z + 0.008)
    return p
def run_wall(Ln, h, doors=(), ow=0.86, t=t_, opens=(), base=True):
    """base: True (rodape dos 2 lados), '+' (so do lado +Z local) ou False."""
    """Parede interna (pivo: inicio, eixo; vai para +X): portas (com batente e guarnicao) e vaos sem porta (opens = (centro, largura))."""
    p = Piece(); cuts = [(c - ow / 2, c + ow / 2) for c in doors] + [(c - w / 2, c + w / 2) for (c, w) in opens]
    xs = sorted(set([0.0, Ln] + [v for c in cuts for v in c]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2
        return None if (j == 0 and any(a < cx < b for (a, b) in cuts)) else 'plaster'
    for m, mesh in grid_solid(xs, [0.0, 2.1, h], [-t / 2, t / 2], cell).items(): p.add(m, mesh)
    for c in doors:
        q = Piece(); door_casing(q, ow, t); p.merge(q, tr(c, 0, 0))
    if base:
        segs = [(0.0, Ln)]
        for (a, b) in cuts: segs = [s for (c, d) in segs for s in segs_excl([(a, b)], c, d, 0.09 if (a, b) in [(c_ - ow / 2, c_ + ow / 2) for c_ in doors] else 0.0)]
        for a, b in segs:
            if b - a > 0.02:
                if base == '+': prof_x(p, 'trim', a, b, D.BASE_PROF(t))
                else: baseboard(p, a, b, t)
    return p

# ============================================================================ banheiro, quarto e moveis
def toilet():
    p = Piece()
    lathe(p, 'porcelain', [(0.12, 0.0), (0.14, 0.1), (0.13, 0.25), (0.19, 0.38), (0.2, 0.4), (0.0, 0.4)], 0.0, 0.0, 0.0, 16)
    p.hull('porcelain', [(x * 0.19, y, z) for x in (-1, 1) for z in (0.0, 0.3) for y in (0.38, 0.4)] + [(0, 0.38, 0.42), (0, 0.4, 0.42)])
    p.cham('porcelain', -0.2, 0.2, 0.42, 0.44, -0.02, 0.44, 0.02)
    p.cham('porcelain', -0.22, 0.22, 0.42, 0.8, -0.22, -0.04, 0.02); p.cham('porcelain', -0.23, 0.23, 0.8, 0.84, -0.23, -0.03, 0.01)
    p.box('steel', 0.12, 0.18, 0.72, 0.74, -0.04, -0.01)
    return p
def bath_fix():
    """Banheiro (coordenadas locais: parede do corredor em z = 0, parede externa/lateral em x = 0, banheiro em +X e +Z, 2 x 1,75 m):
    box com bandeja e vidro, chuveiro, vaso, bancada com cuba, espelho, toalheiro, revestimento ate 1,2 m."""
    p = Piece()
    p.cham('porcelain', 0.002, 0.9, 0.0, 0.06, 0.002, 0.9, 0.01); p.box('glass', 0.9, 0.91, 0.06, 2.0, 0.0, 0.9)
    p.box('steel', 0.895, 0.915, 2.0, 2.02, 0.0, 0.9)
    p.cyl('steel', 0.015, 0.8, 1.9, 0.45, 0.02, 8); p.cyl('steel', 0.1, 1.9, 1.92, 0.45, 0.12, 14); seg_cyl(p, 'steel', (0.45, 1.9, 0.02), (0.45, 1.9, 0.12), 0.012, 6)
    q = toilet(); p.merge(q, rot_y(180, (0.45, 0.0, 1.75 - 0.24)))
    p.box('wood', 1.0, 1.7, 0.45, 0.85, 0.0, 0.48); p.cham('stone_f', 0.98, 1.72, 0.85, 0.89, 0.0, 0.5, 0.006)
    lathe(p, 'porcelain', [(0.0, 0.89), (0.2, 0.89), (0.2, 0.96), (0.0, 0.96)], 1.35, 0.25, 0.0, 16)
    p.cyl('steel', 0.015, 0.89, 1.05, 1.35, 0.06, 8); seg_cyl(p, 'steel', (1.35, 1.04, 0.06), (1.35, 1.04, 0.14), 0.01, 6)
    p.box('steel', 1.02, 1.68, 1.1, 1.9, 0.0, 0.015); p.box('glass', 1.04, 1.66, 1.12, 1.88, 0.015, 0.02)
    seg_cyl(p, 'steel', (1.8, 1.4, 0.06), (1.8, 1.4, 0.0), 0.008, 5) if False else None
    for (a, b, c, d) in ((0.0, 2.0, 0.0, 0.004), (0.0, 0.004, 0.0, 1.75)):
        p.box('tile', a + (0.004 if c == 0.0 and d == 0.004 else 0.0), b, 0.0, 1.2, c, d) if False else None
    return p
def bed(Lb=2.0, wb=1.6):
    """Cama de casal (pivo: centro da cabeceira, no piso; cama para +Z): cabeceira estofada, base, colchao, edredom, travesseiros."""
    p = Piece(); x = wb / 2
    p.cham('dkwood', -x - 0.1, x + 0.1, 0.0, 1.15, 0.0, 0.08, 0.01); p.cham('fabric', -x - 0.05, x + 0.05, 0.4, 1.1, 0.08, 0.13, 0.03)
    p.box('dkwood', -x, x, 0.05, 0.3, 0.13, Lb); p.cham('linen', -x + 0.02, x - 0.02, 0.3, 0.52, 0.14, Lb - 0.02, 0.04)
    p.cham('fabric2', -x - 0.01, x + 0.01, 0.42, 0.56, 0.7, Lb - 0.0, 0.03)
    for s in (-1, 1): p.cham('linen', s * 0.38 - 0.3, s * 0.38 + 0.3, 0.52, 0.66, 0.18, 0.5, 0.06)
    return p
def room_set(front=True):
    """Moveis do quarto (pivo: canto do lado do banheiro, na parede norte do banheiro; banheiro em -Z, quarto em +X e +Z):
    cama, 2 criados-mudos com abajur, TV na parede, aparador, guarda-roupa, poltrona, mesinha e cortina."""
    p = Piece()
    if front:
        q = bed(); p.merge(q, tr(1.3, 0, 0.06))
        for x in (0.22, 2.38):
            p.cham('dkwood', x - 0.22, x + 0.22, 0.0, 0.55, 0.08, 0.48, 0.01); p.box('brass', x - 0.12, x + 0.12, 0.38, 0.4, 0.07, 0.48) if False else None
            lathe(p, 'gold', [(0.07, 0.55), (0.07, 0.57), (0.02, 0.6), (0.02, 0.8)], x, 0.28, 0.0, 10); lathe(p, 'linen', [(0.13, 0.78), (0.09, 0.98)], x, 0.28, 0.0, 14)
        # poltrona e mesinha junto da janela
        p.cham('fabric', 0.2, 0.95, 0.0, 0.45, 2.9, 3.55, 0.04); p.cham('fabric', 0.2, 0.32, 0.45, 0.85, 2.9, 3.55, 0.03); p.cham('fabric', 0.2, 0.95, 0.45, 0.95, 3.45, 3.6, 0.03)
        p.cyl('dkwood', 0.25, 0.5, 0.53, 1.35, 3.25, 16); p.cyl('steel', 0.02, 0.0, 0.5, 1.35, 3.25, 8); p.cyl('steel', 0.18, 0.0, 0.02, 1.35, 3.25, 14)
    else:
        q = bed(2.0, 1.4); p.merge(q, rot_y(90, (0.06, 0.0, -1.35)))
        p.cham('dkwood', 0.08, 0.5, 0.0, 0.55, -0.52, -0.1, 0.01)
        lathe(p, 'gold', [(0.07, 0.55), (0.07, 0.57), (0.02, 0.6), (0.02, 0.8)], 0.29, -0.31, 0.0, 10); lathe(p, 'linen', [(0.13, 0.78), (0.09, 0.98)], 0.29, -0.31, 0.0, 14)
    return p
def tv_unit(Ln=1.4):
    """Aparador com TV na parede (pivo: centro, na face da parede; frente +Z)."""
    p = Piece()
    p.cham('dkwood', -Ln / 2, Ln / 2, 0.15, 0.6, 0.0, 0.38, 0.01); p.box('dark', -Ln / 2 + 0.04, Ln / 2 - 0.04, 0.0, 0.15, 0.03, 0.34)
    for x in (-Ln / 4, Ln / 4): p.box('steel', x - 0.1, x + 0.1, 0.4, 0.42, 0.38, 0.385)
    p.cham('dark', -0.55, 0.55, 1.05, 1.7, 0.0, 0.05, 0.006); p.box('menu' if False else 'sign', -0.52, 0.52, 1.08, 1.67, 0.05, 0.052)
    return p
def wardrobe():
    p = Piece(); p.box('dkwood', 0.0, 1.0, 0.0, 2.2, 0.0, 0.6); p.box('dark', 0.499, 0.501, 0.1, 2.15, 0.6, 0.602)
    for x in (0.45, 0.55): p.box('gold', x - 0.008, x + 0.008, 1.0, 1.3, 0.6, 0.62)
    return p
def room_furn(front=True, wid=3.69):
    """Moveis do quarto inteiro (pivo como room_set; wid = largura livre do quarto): TV, guarda-roupa no hall, escrivaninha."""
    p = room_set(front)
    if front:
        q = tv_unit(); p.merge(q, rot_y(-90, (wid, 0.0, 1.0)))         # TV na parede lateral, vira para a cama
        q = wardrobe(); p.merge(q, rot_y(-90, (wid, 0.0, -0.95)))       # guarda-roupa no hall de entrada
    else:
        x0, x1, z0, z1 = 2.2, 3.2, -2.36, -1.86
        p.cham('dkwood', x0, x1, 0.72, 0.76, z0, z1, 0.006)
        for xx in (x0 + 0.02, x1 - 0.06): p.box('dkwood', xx, xx + 0.04, 0.0, 0.72, z0 + 0.02, z1 - 0.02)
        q = Piece(); q.cham('fabric', -0.22, 0.22, 0.0, 0.47, -0.22, 0.22, 0.02); q.cham('fabric', -0.22, 0.22, 0.47, 0.9, 0.15, 0.22, 0.02); p.merge(q, tr(2.7, 0, -1.5))
        q = tv_unit(1.0); p.merge(q, rot_y(-90, (wid, 0.0, -1.0)))
        q = wardrobe(); p.merge(q, rot_y(-90, (wid, 0.0, -0.05)))
    return p

# ============================================================================ planta do andar tipo
FRONT_ROOMS = [(-5.75, -2.06, 'l'), (-1.94, 1.94, 'l'), (2.06, 5.75, 'r')]
BACK_ROOMS = [(-5.75, -2.06, 'l'), (2.06, 5.75, 'r')]
def entry_x(xa, xb, side): return (xa + 2.65) if side == 'l' else (xb - 2.65)      # porta do quarto junto do banheiro (o guarda-roupa fica no outro lado do hall)
def plan_typ(level='typ'):
    """Paredes internas de um andar da torre (pivo: centro, cota do piso): corredor, quartos, banheiros, nucleo com escada e
    elevador (portas de aco fechadas e botoeira), batentes, rodapes, banheiros equipados e luzes do corredor."""
    p = Piece(); h = CEIL if level == 'typ' else HP - SLAB
    xi = TX - T
    fd = [entry_x(a, b, s) for (a, b, s) in FRONT_ROOMS]
    q = run_wall(2 * xi, h, doors=[x + xi for x in fd]); p.merge(q, tr(-xi, 0, ZF))
    bd = [entry_x(a, b, s) for (a, b, s) in BACK_ROOMS]
    q = run_wall(2 * xi, h, doors=[x + xi for x in bd] + [SD + xi], opens=[(1.15 + xi, 0.9)]); p.merge(q, tr(-xi, 0, ZB))
    for x in (-2.0, 2.0):
        q = run_wall(TZ1 - T - (ZF + t_ / 2), h); p.merge(q, rot_y(-90, (x, 0, ZF + t_ / 2)))
        q = run_wall((ZB - t_ / 2) - ZBK, h, base='+' if x < 0 else True); p.merge(q, rot_y(-90, (x, 0, ZBK)))
    q = run_wall((ZB - t_ / 2) - ZBK, h, base=False); p.merge(q, rot_y(-90, (XS, 0, ZBK)))
    # banheiros
    for (xa, xb, s) in FRONT_ROOMS:
        xw = xa + 2.06 if s == 'l' else xb - 2.06
        q = run_wall(1.96 - (ZF + t_ / 2) + t_ / 2, h, doors=[1.0 - (ZF + t_ / 2)], ow=0.72); p.merge(q, rot_y(-90, (xw, 0, ZF + t_ / 2)))
        a, b = (xa, xw - t_ / 2) if s == 'l' else (xw + t_ / 2, xb)
        q = run_wall(b - a, h); p.merge(q, tr(a, 0, 1.96))
        M = tr(xa, 0, ZF + t_ / 2) if s == 'l' else tr(xb, 0, ZF + t_ / 2) @ mirror_x()
        p.merge(bath_fix(), M)
    for (xa, xb, s) in BACK_ROOMS:
        xw = xa + 2.06 if s == 'l' else xb - 2.06
        q = run_wall((ZB - t_ / 2) - (ZBB - t_ / 2), h, doors=[(ZB - t_ / 2) - (-2.4)], ow=0.72); p.merge(q, rot_y(90, (xw, 0, ZB - t_ / 2)))
        a, b = (xa, xw - t_ / 2) if s == 'l' else (xw + t_ / 2, xb)
        q = run_wall(b - a, h); p.merge(q, tr(a, 0, ZBB))
        M = (tr(xa, 0, ZB - t_ / 2) @ mirror_z()) if s == 'l' else (tr(xb, 0, ZB - t_ / 2) @ mirror_x() @ mirror_z())
        p.merge(bath_fix(), M)
    # elevador: portas de aco, batente e botoeira
    zc = ZB + t_ / 2
    p.box('steel', 0.7, 1.15, 0.0, 2.1, zc - 0.07, zc - 0.05); p.box('steel', 1.15, 1.6, 0.0, 2.1, zc - 0.07, zc - 0.05)
    p.box('dark', 1.148, 1.152, 0.0, 2.1, zc - 0.05, zc - 0.048)
    for (a, b) in ((0.62, 0.71), (1.59, 1.68)): p.box('steel', a, b, 0.0, 2.2, ZB - t_ / 2 - 0.02, zc + 0.02)
    p.box('steel', 0.62, 1.68, 2.09, 2.2, ZB - t_ / 2 - 0.02, zc + 0.02)
    p.cham('steel', 1.8, 1.9, 1.0, 1.25, zc, zc + 0.012, 0.003); p.cyl('lamp_glass', 0.012, 1.08, 1.1, 1.85, zc + 0.012, 8) if False else p.box('lamp_glass', 1.83, 1.87, 1.08, 1.12, zc + 0.012, zc + 0.016)
    p.box('dark', 0.7, 1.6, 0.0, 2.1, -1.9, -1.88) if False else None
    # luzes do corredor e sinalizacao de saida sem texto (seta verde)
    for x in (-4.5, -1.5, 1.5, 4.5): p.cyl('steel', 0.09, h - 0.012, h, x, (ZB + ZF) / 2, 14); p.cyl('lamp_glass', 0.07, h - 0.016, h - 0.012, x, (ZB + ZF) / 2, 14)
    return p

# ============================================================================ sacada, terraco, cobertura e marquise
def balcony(w=1.9, d=1.4):
    """Sacada (pivo: face da fachada no eixo da porta, cota do piso; para +Z): laje com pingadeira, piso de deck, guarda-corpo
    de vidro verde com montantes e corrimao de aco, divisorias laterais."""
    p = Piece(); x = w / 2
    p.box('band', -x, x, -0.2, -0.012, 0.0, d); p.box('band', -x - 0.02, x + 0.02, -0.24, -0.2, -0.0, d + 0.02)
    p.box('wood', -x + 0.02, x - 0.02, -0.012, 0.0, 0.004, d - 0.02)
    for (a, b, c, e) in ((-x, x, d - 0.04, d - 0.02), (-x, -x + 0.02, 0.004, d - 0.04), (x - 0.02, x, 0.004, d - 0.04)):
        p.box('gglass', a, b, 0.05, 1.0, c, e)
    p.box('steel', -x - 0.01, x + 0.01, 1.0, 1.05, d - 0.05, d - 0.01); p.box('steel', -x - 0.01, -x + 0.03, 1.0, 1.05, 0.004, d - 0.05); p.box('steel', x - 0.03, x + 0.01, 1.0, 1.05, 0.004, d - 0.05)
    for xx in (-x + 0.01, x - 0.01):
        p.box('steel', xx - 0.02, xx + 0.02, 0.0, 1.0, d - 0.065, d - 0.015)
    p.cham('steel', -x + 0.2, -x + 0.6, 0.0, 0.42, 0.25, 0.65, 0.01); p.cham('steel', -x + 0.95, -x + 1.45, 0.0, 0.42, 0.3, 0.8, 0.01)
    p.cham('wood', -x + 0.18, -x + 0.62, 0.42, 0.45, 0.23, 0.67, 0.006); p.cyl('steel', 0.22, 0.7, 0.72, -x + 1.2, 0.55, 16); p.cyl('steel', 0.02, 0.0, 0.7, -x + 1.2, 0.55, 8)
    return p
def terrace():
    """Terraco no teto do embasamento (pivo: origem, cota do terraco): laje com forro por baixo, piso de placas fora da torre,
    floreiras com arvores e arbustos, espreguicadeiras, ombrelone e luminarias de piso."""
    p = Piece()
    pod_in = sbox(-PX + T, PZ0 + T, PX - T, PZ1 - T); tw_in = sbox(-TX + T, TZ0 + T, TX - T, TZ1 - T); tw_out = sbox(-TX, TZ0, TX, TZ1)
    slab = pod_in.difference(tw_in)
    ext_y(p, 'ceil', slab, -SLAB, -SLAB + 0.01); ext_y(p, 'concrete', slab, -SLAB + 0.01, -0.05)
    ext_y(p, 'concrete', slab.intersection(tw_out), -0.05, 0.0)
    out = slab.difference(tw_out); b = out.bounds; J = 0.6
    for x in np.arange(b[0], b[2], J):
        for z in np.arange(b[1], b[3], J):
            q = sbox(x + 0.004, z + 0.004, x + J - 0.004, z + J - 0.004).intersection(out); ext_y(p, 'paver', q, -0.05 + 0.02, 0.0)
    ext_y(p, 'dark', out.buffer(-0.001), -0.05, -0.03)
    for (x0, x1, z0, z1) in ((-PX + T, -TX - 0.3, TZ1 + 0.4, PZ1 - T), (TX + 0.3, PX - T, TZ1 + 0.4, PZ1 - T)):
        pass
    for (x, z) in ((-7.1, 8.9), (7.1, 8.9), (-7.1, -4.5), (7.1, -4.5)):
        p.cham('concrete', x - 0.6, x + 0.6, 0.0, 0.6, z - 0.6, z + 0.6, 0.02); p.box('mulch', x - 0.54, x + 0.54, 0.6, 0.612, z - 0.54, z + 0.54)
        lathe(p, 'bark', [(0.07, 0.6), (0.05, 2.0)], x, z, 0.0, 8); p.sphere('leaf2', 0.75, x, 2.4, z, 2); p.sphere('leaf2', 0.45, x + 0.4, 2.1, z - 0.2, 1)
    for x in np.arange(-5.0, 5.01, 2.5):
        p.cham('concrete', x - 0.9, x + 0.9, 0.0, 0.5, PZ1 - T - 0.5, PZ1 - T - 0.02, 0.02); p.box('mulch', x - 0.85, x + 0.85, 0.5, 0.512, PZ1 - T - 0.46, PZ1 - T - 0.06)
        for k in range(4): p.sphere('hedge', 0.22, x - 0.6 + k * 0.4, 0.6, PZ1 - T - 0.26, 1)
    for x in (-3.4, -1.6, 1.6, 3.4):
        q = Piece()
        q.hull('steel', [(xx, y, z) for xx in (-0.32, 0.32) for (z, y) in ((0.0, 0.3), (1.3, 0.3), (0.0, 0.34), (1.3, 0.34))])
        q.hull('fabric2', [(xx, y, z) for xx in (-0.3, 0.3) for (z, y) in ((0.45, 0.34), (1.3, 0.34), (0.45, 0.4), (1.3, 0.4))])
        q.hull('fabric2', [(xx, y, z) for xx in (-0.3, 0.3) for (z, y) in ((0.0, 0.85), (0.08, 0.85), (0.45, 0.34), (0.5, 0.4))])
        for (xx, z) in ((-0.28, 0.1), (0.28, 0.1), (-0.28, 1.25), (0.28, 1.25)): p.box('steel', x + xx - 0.02, x + xx + 0.02, 0.0, 0.3, 7.4 + z - 0.02, 7.4 + z + 0.02)
        p.merge(q, tr(x, 0, 7.4))
    for (x, z) in ((-5.2, 7.0), (5.2, 7.0), (-7.0, 1.0), (7.0, 1.0), (-7.0, -2.5), (7.0, -2.5)):
        p.cyl('steel', 0.08, 0.0, 0.7, x, z, 10); p.cyl('lamp_glass', 0.07, 0.55, 0.68, x, z, 10); p.cyl('steel', 0.1, 0.7, 0.73, x, z, 10)
    return p
def roof_top():
    """Cobertura (pivo: origem, cota da laje de cobertura): platibanda de reboco com capa e faixa, casa de maquinas do nucleo com
    porta, condensadoras, exaustores, para-raios e letreiro sem texto (painel azul com estrela e moldura dourada)."""
    p = Piece(); ph = PAR
    for (x0, x1, z0, z1) in ((-TX, TX, TZ1 - T, TZ1), (-TX, TX, TZ0, TZ0 + T), (-TX, -TX + T, TZ0, TZ1), (TX - T, TX, TZ0, TZ1)):
        p.box('render', x0, x1, 0.0, ph, z0, z1)
    for (x0, x1, z0, z1) in ((-TX - 0.04, TX + 0.04, TZ1 - T - 0.04, TZ1 + 0.04), (-TX - 0.04, TX + 0.04, TZ0 - 0.04, TZ0 + T + 0.04), (-TX - 0.04, -TX + T + 0.04, TZ0 - 0.04, TZ1 + 0.04), (TX - T - 0.04, TX + 0.04, TZ0 - 0.04, TZ1 + 0.04)):
        p.cham('cill', x0, x1, ph, ph + 0.08, z0, z1, 0.008)
    for (x0, x1, z0, z1) in ((-TX - 0.03, TX + 0.03, TZ1, TZ1 + 0.03), (-TX - 0.03, TX + 0.03, TZ0 - 0.03, TZ0), (-TX - 0.03, -TX, TZ0 - 0.03, TZ1 + 0.03), (TX, TX + 0.03, TZ0 - 0.03, TZ1 + 0.03)):
        p.box('band', x0, x1, -SLAB - 0.02, 0.03, z0, z1)
    p.box('band', -2.0, 2.0, -SLAB - 0.02, 0.0, TZ0 - 0.06, TZ0 + T)       # fecha o topo do pano de vidro
    # casa de maquinas sobre o nucleo
    hx0, hx1, hz0, hz1, hh = -2.2, 2.2, TZ0 + T, -1.25, 4.0
    for (x0, x1, z0, z1) in ((hx0, hx1, hz1 - 0.2, hz1), (hx0, hx0 + 0.2, hz0, hz1), (hx1 - 0.2, hx1, hz0, hz1)):
        holes = []
        p.box('render', x0, x1, 0.0, hh, z0, z1) if not (z1 == hz1 and x1 - x0 > 1) else None
    # parede da frente da casa de maquinas com a porta da escada
    q = Piece()
    xs = [hx0, -1.45, -0.45, hx1]
    for m, mesh in grid_solid(xs, [0.0, 2.2, hh], [hz1 - 0.2, hz1], lambda i, j, k: None if (i == 1 and j == 0) else 'render').items(): q.add(m, mesh)
    p.merge(q)
    q = Piece(); door_casing(q, 1.0, 0.2, 2.2); p.merge(q, tr(-0.95, 0, hz1 - 0.1))
    p.cham('cill', hx0 - 0.05, hx1 + 0.05, hh, hh + 0.08, hz0, hz1 + 0.05, 0.008)
    p.box('membrane', hx0 + 0.2, hx1 - 0.2, hh - 0.2, hh - 0.01, hz0, hz1 - 0.2)
    p.box('ceil', hx0 + 0.2, hx1 - 0.2, hh - 0.21, hh - 0.2, hz0, hz1 - 0.2)
    q = wall_lantern(); p.merge(q, tr(-0.95, 2.5, hz1))
    # condensadoras e exaustores
    for (x, z) in ((-4.0, 2.0), (4.0, 2.0)):
        p.box('dark', x - 1.0, x + 1.0, 0.0, 0.12, z - 0.4, z - 0.3); p.box('dark', x - 1.0, x + 1.0, 0.0, 0.12, z + 0.3, z + 0.4)
        p.cham('unit', x - 0.9, x + 0.9, 0.12, 1.3, z - 0.6, z + 0.6, 0.015)
        for xx in (x - 0.45, x + 0.45):
            p.cyl('dark', 0.36, 1.3, 1.33, xx, z, 24); lathe(p, 'unit', [(0.4, 1.3), (0.4, 1.36), (0.36, 1.36), (0.36, 1.33)], xx, z, 0.0, 24)
            for k in range(4):
                a = k * math.pi / 4; seg_cyl(p, 'steel', (xx - 0.37 * math.cos(a), 1.36, z - 0.37 * math.sin(a)), (xx + 0.37 * math.cos(a), 1.36, z + 0.37 * math.sin(a)), 0.006, 4)
        for i in range(14):
            y = 0.25 + i * 0.07
            for s in (-1, 1): p.hull('unit', [(xx, yy, z + s * zz) for xx in (x - 0.85, x + 0.85) for (zz, yy) in ((0.6, y + 0.04), (0.6, y + 0.05), (0.63, y), (0.63, y + 0.01))])
    for (x, z) in ((-4.0, -3.5), (4.0, -3.5), (3.5, -1.0)):
        p.cham('unit', x - 0.35, x + 0.35, 0.0, 0.35, z - 0.35, z + 0.35, 0.01); p.cyl('unit', 0.24, 0.35, 0.6, x, z, 16)
        lathe(p, 'unit', [(0.48, 0.58), (0.48, 0.62), (0.42, 0.74), (0.25, 0.83), (0.0, 0.86)], x, z, 0.0, 20)
    seg_cyl(p, 'steel', (0.0, hh + 0.08, -3.5), (0.0, hh + 3.0, -3.5), 0.02, 6); p.sphere('steel', 0.04, 0.0, hh + 3.0, -3.5, 1)
    # letreiro (sem texto)
    sx, sy0, sy1, sz = 3.6, 1.8, 3.8, TZ1 - 1.2
    for x in (-2.8, 0.0, 2.8):
        p.box('steel', x - 0.06, x + 0.06, 0.0, sy0, sz - 0.06, sz + 0.06); seg_cyl(p, 'steel', (x, 0.0, sz - 1.0), (x, sy0 - 0.1, sz), 0.03, 6)
        p.box('steel', x - 0.15, x + 0.15, 0.0, 0.04, sz - 1.15, sz - 0.85)
    p.cham('gold', -sx, sx, sy0, sy1, sz - 0.12, sz + 0.12, 0.02); p.box('sign', -sx + 0.12, sx - 0.12, sy0 + 0.12, sy1 - 0.12, sz + 0.12, sz + 0.13)
    star = Polygon([(0.75 * (1 if k % 2 == 0 else 0.4) * math.cos(math.pi / 2 + k * math.pi / 5), (sy0 + sy1) / 2 + 0.75 * (1 if k % 2 == 0 else 0.4) * math.sin(math.pi / 2 + k * math.pi / 5)) for k in range(10)])
    ext(p, 'gold', star, sz + 0.13, sz + 0.15)
    for xx in (-2.4, -1.6, 1.6, 2.4): ext(p, 'gold', Point(xx, (sy0 + sy1) / 2).buffer(0.12, 12), sz + 0.13, sz + 0.145)
    for x in np.arange(-sx + 0.4, sx - 0.3, 0.8): p.box('lamp_glass', x - 0.05, x + 0.05, sy1 + 0.0, sy1 + 0.06, sz + 0.13, sz + 0.25); seg_cyl(p, 'steel', (x, sy1, sz + 0.05), (x, sy1 + 0.04, sz + 0.2), 0.012, 5)
    return p
def canopy():
    """Marquise da entrada (pivo: face da fachada, x = 0, no chao; para +Z): 4 pilares revestidos, laje com faixa e friso dourado,
    forro com luzes embutidas, teto verde com arbustos e 3 claraboias redondas."""
    p = Piece(); x0, x1, d = -4.0, 4.0, 4.6; yb, yt = 3.95, 4.55
    for (x, z) in ((-3.4, 0.6), (3.4, 0.6)):
        p.cham('cill', x - 0.25, x + 0.25, 0.0, 0.35, z - 0.25, z + 0.25, 0.01); p.cham('brick', x - 0.2, x + 0.2, 0.35, yb, z - 0.2, z + 0.2, 0.01)
        p.cham('cill', x - 0.24, x + 0.24, yb - 0.25, yb, z - 0.24, z + 0.24, 0.008)
    holes = [Point(x, 2.4).buffer(0.45, 24) for x in (-2.2, 0.0, 2.2)]
    roof = sbox(x0, 0.0, x1, d)
    ext_y(p, 'band', roof.difference(unary_union([h.buffer(0.06) for h in holes])), yb, yt)
    for h in holes:
        ext_y(p, 'band', h.buffer(0.06).difference(h), yb, yt + 0.1); lathe(p, 'glass', [(0.47, yt + 0.1), (0.4, yt + 0.25), (0.2, yt + 0.33), (0.0, yt + 0.35)], h.centroid.x, h.centroid.y, 0.0, 24)
    ext_y(p, 'ceil', roof.difference(unary_union([h.buffer(0.06) for h in holes])), yb - 0.01, yb)
    for (x, z) in ((-3.0, 1.0), (-1.0, 1.0), (1.0, 1.0), (3.0, 1.0), (-3.0, 4.0), (-1.0, 4.0), (1.0, 4.0), (3.0, 4.0)):
        p.cyl('lamp_glass', 0.08, yb - 0.015, yb - 0.01, x, z, 12); p.cyl('steel', 0.1, yb - 0.012, yb - 0.008, x, z, 12) if False else None
    for (a, b, c, e) in ((x0, x1, d, d + 0.06), (x0 - 0.06, x0, 0.0, d + 0.06), (x1, x1 + 0.06, 0.0, d + 0.06)):
        p.box('band', a, b, yb - 0.1, yt + 0.2, c, e); p.box('gold', a - (0.006 if a == x0 - 0.06 else 0.0), b + (0.006 if b == x1 + 0.06 else 0.0), yt - 0.05, yt + 0.02, c + (0.06 if c == d else 0.0), e + 0.006) if False else None
    p.box('gold', x0 - 0.06, x1 + 0.06, yt - 0.06, yt + 0.0, d + 0.06, d + 0.07)
    for x in (-3.4, -1.1, 1.1, 3.4):                                       # tirantes ate a fachada
        seg_cyl(p, 'steel', (x, 6.9, 0.04), (x, yt + 0.2, d - 0.3), 0.022, 8)
        p.cham('steel', x - 0.08, x + 0.08, 6.8, 7.0, 0.0, 0.03, 0.005); p.cham('steel', x - 0.06, x + 0.06, yt + 0.12, yt + 0.24, d - 0.4, d - 0.2, 0.005)
    for s in (-1, 1): p.box('gold', *sorted((s * (x1 + 0.06), s * (x1 + 0.07))), yt - 0.06, yt, 0.0, d + 0.07)
    green = roof.buffer(-0.06).difference(unary_union([h.buffer(0.1) for h in holes]))
    ext_y(p, 'grass', green, yt, yt + 0.12)
    rng = np.random.default_rng(2)
    for k in range(16):
        x = rng.uniform(x0 + 0.3, x1 - 0.3); z = rng.choice([rng.uniform(0.3, 1.6), rng.uniform(3.2, 4.3)])
        p.sphere('hedge', rng.uniform(0.18, 0.3), x, yt + 0.16, z, 1)
    return p

# ============================================================================ interior do embasamento
def column():
    """Pilar redondo revestido com base e capitel (pivo: centro, no piso)."""
    p = Piece(); h = HP - SLAB
    lathe(p, 'cill', [(0.32, 0.0), (0.32, 0.12), (0.26, 0.16)], sec=24); p.cyl('stone_f', 0.24, 0.12, h - 0.2, 0, 0, 24)
    lathe(p, 'cill', [(0.26, h - 0.2), (0.32, h - 0.12), (0.34, h)], sec=24)
    return p
def pod_floor(kind='g'):
    """Piso / laje do embasamento (pivo: origem, cota do piso). 'g': piso do terreo (pedra no saguao, carpete no fundo).
    'p': laje do 2o andar (assoalho no salao, forro do terreo por baixo, abertura da escada)."""
    p = Piece(); inner = sbox(-PX + T, PZ0 + T, PX - T, PZ1 - T)
    back = sbox(-PX + T, PZ0 + T, PX - T, ZB)
    if kind == 'g':
        ext_y(p, 'concrete', inner, -Y0 + 0.02, -0.012)
        ext_y(p, 'stone_f', inner.difference(back), -0.012, 0.0); ext_y(p, 'carpet2', back, -0.012, 0.0)
        return p
    inner = inner.difference(STAIR_HOLE)
    ext_y(p, 'ceil', inner, -SLAB, -SLAB + 0.01); ext_y(p, 'concrete', inner, -SLAB + 0.01, -0.012)
    ext_y(p, 'wood', inner.difference(back), -0.012, 0.0); ext_y(p, 'carpet2', back.difference(STAIR_HOLE), -0.012, 0.0)
    for (x, z) in ((-5.0, 2.0), (5.0, 2.0), (-5.0, 7.0), (0.0, 7.0), (5.0, 7.0)):
        p.cyl('steel', 0.3, -SLAB - 0.004, -SLAB, x, z, 20); p.cyl('lamp_glass', 0.26, -SLAB - 0.006, -SLAB - 0.004, x, z, 20)
    return p
def plan_pod(level='g'):
    """Paredes internas do embasamento (pivo: origem, cota do piso): parede dos fundos com portas para escritorio/deposito,
    escada e elevador; paredes do nucleo."""
    p = Piece(); h = HP - SLAB; xi = PX - T
    q = run_wall(2 * xi, h, doors=[-5.0 + xi, SD + xi, 5.0 + xi], opens=[(1.15 + xi, 0.9)]); p.merge(q, tr(-xi, 0, ZB))
    for x in (-2.0, 2.0):
        q = run_wall((ZB - t_ / 2) - (TZ0 + T), h, base='+' if x < 0 else True); p.merge(q, rot_y(-90, (x, 0, TZ0 + T)))
    q = run_wall((ZB - t_ / 2) - (TZ0 + T), h, base=False); p.merge(q, rot_y(-90, (XS, 0, TZ0 + T)))
    zc = ZB + t_ / 2
    p.box('steel', 0.7, 1.15, 0.0, 2.1, zc - 0.07, zc - 0.05); p.box('steel', 1.15, 1.6, 0.0, 2.1, zc - 0.07, zc - 0.05); p.box('dark', 1.148, 1.152, 0.0, 2.1, zc - 0.05, zc - 0.048)
    for (a, b) in ((0.62, 0.71), (1.59, 1.68)): p.box('gold', a, b, 0.0, 2.2, ZB - t_ / 2 - 0.02, zc + 0.02)
    p.box('gold', 0.62, 1.68, 2.09, 2.2, ZB - t_ / 2 - 0.02, zc + 0.02); p.box('gold', 1.83, 1.87, 1.0, 1.2, zc, zc + 0.012)
    if level == 'g':
        p.cham('dkwood', -7.4, -5.9, 0.0, 0.75, -5.4, -4.7, 0.01)                 # mesa do escritorio
        for k in range(3): p.box('dkwood', 5.9, 7.6, 0.4 + k * 0.6, 0.43 + k * 0.6, -5.7, -5.2)
        for x in (5.95, 7.55): p.box('dkwood', x - 0.02, x + 0.02, 0.0, 1.8, -5.7, -5.2)
        for (x, z, c) in ((6.3, -4.6, 'fabric2'), (6.9, -4.6, 'fabric'), (7.3, -3.8, 'fabric2')): p.cham(c, x - 0.22, x + 0.22, 0.0, 0.6, z - 0.15, z + 0.15, 0.02)
    return p
def reception():
    """Balcao da recepcao (pivo: centro da frente, no piso; frente +Z): frente de madeira com friso dourado, tampo de pedra,
    computadores, sineta, painel de parede com estrela dourada (sem texto)."""
    p = Piece(); L1 = 3.6; x = L1 / 2
    p.box('dkwood', -x, x, 0.0, 1.05, -0.7, 0.0); p.box('gold', -x, x, 0.85, 0.89, 0.0, 0.01)
    for k in range(6): xx = -x + (k + 0.5) * L1 / 6; p.box('wood', xx - 0.22, xx + 0.22, 0.12, 0.78, 0.0, 0.015)
    p.cham('stone_f', -x - 0.04, x + 0.04, 1.05, 1.1, -0.74, 0.08, 0.006); p.cham('stone_f', -x + 0.05, x - 0.05, 0.75, 0.78, -0.69, -0.35, 0.004)
    for xx in (-1.0, 1.0):
        p.box('dark', xx - 0.25, xx + 0.25, 0.78, 0.8, -0.65, -0.4); p.hull('dark', [(xx + dx, y, z) for dx in (-0.25, 0.25) for (y, z) in ((1.12, -0.58), (1.45, -0.62), (1.12, -0.55), (1.45, -0.59))])
    lathe(p, 'gold', [(0.05, 1.1), (0.05, 1.12), (0.04, 1.16), (0.0, 1.17)], 0.4, -0.2, 0.0, 12)
    return p
def lobby_wall_panel():
    p = Piece(); p.box('dkwood', -2.0, 2.0, 0.0, 3.0, 0.0, 0.04)
    for k in range(9): xx = -1.8 + k * 0.45; p.box('wood', xx - 0.2, xx + 0.2, 0.1, 2.9, 0.04, 0.05)
    star = Polygon([(0.45 * (1 if k % 2 == 0 else 0.4) * math.cos(math.pi / 2 + k * math.pi / 5), 1.8 + 0.45 * (1 if k % 2 == 0 else 0.4) * math.sin(math.pi / 2 + k * math.pi / 5)) for k in range(10)])
    ext(p, 'gold', star, 0.05, 0.07)
    return p
def sofa(L1=2.0):
    p = Piece(); x = L1 / 2
    p.cham('fabric', -x, x, 0.1, 0.42, 0.0, 0.85, 0.04); p.cham('fabric', -x, x, 0.42, 0.85, 0.0, 0.2, 0.05)
    for s in (-1, 1): p.cham('fabric', *sorted((s * x, s * (x - 0.18))), 0.42, 0.65, 0.0, 0.85, 0.04)
    for k in range(int(L1 / 0.6)): xx = -x + 0.18 + (k + 0.5) * (L1 - 0.36) / int(L1 / 0.6); p.cham('fabric', xx - (L1 - 0.36) / int(L1 / 0.6) / 2 + 0.01, xx + (L1 - 0.36) / int(L1 / 0.6) / 2 - 0.01, 0.42, 0.55, 0.2, 0.82, 0.04)
    for (sx, sz) in ((-1, 0.05), (1, 0.05), (-1, 0.8), (1, 0.8)): p.cyl('dkwood', 0.025, 0.0, 0.1, sx * (x - 0.08), sz, 8)
    return p
def lounge():
    """Sala de estar do saguao (pivo: centro do tapete, no piso): tapete, 2 sofas, 2 poltronas, mesa de centro, abajur de pe."""
    p = Piece()
    p.box('rug', -2.0, 2.0, 0.0, 0.008, -1.5, 1.5)
    q = sofa(2.2); p.merge(q, tr(0, 0, -1.4)); q = sofa(2.2); p.merge(q, rot_y(180, (0, 0, 1.4)))
    for s in (-1, 1): q = sofa(0.9); p.merge(q, rot_y(-90 * s, (s * 1.85, 0, 0.0)))
    p.cham('dkwood', -0.7, 0.7, 0.3, 0.38, -0.4, 0.4, 0.01); p.box('dkwood', -0.65, -0.6, 0.008, 0.3, -0.35, 0.35); p.box('dkwood', 0.6, 0.65, 0.008, 0.3, -0.35, 0.35)
    lathe(p, 'gold', [(0.15, 0.008), (0.15, 0.03), (0.02, 0.05), (0.02, 1.5)], 1.85, -1.3, 0.0, 12); lathe(p, 'linen', [(0.22, 1.45), (0.16, 1.75)], 1.85, -1.3, 0.0, 16)
    return p
def bar(L1=3.0):
    """Bar (pivo: inicio, encostado na parede, no piso; frente +Z, vai para +X): estante de garrafas com espelho, balcao de madeira
    com tampo de pedra e apoio de pes, 5 banquetas."""
    p = Piece()
    p.box('dkwood', 0.0, L1, 0.0, 0.9, 0.0, 0.45); p.cham('stone_f', 0.0, L1, 0.9, 0.94, 0.0, 0.5, 0.006)
    p.box('glass', 0.1, L1 - 0.1, 1.2, 2.4, 0.001, 0.011)
    for y in (1.3, 1.75, 2.2):
        p.box('dkwood', 0.05, L1 - 0.05, y - 0.03, y, 0.0, 0.25)
        for x in np.arange(0.2, L1 - 0.15, 0.16): lathe(p, 'bottle', [(0.035, y), (0.035, y + 0.2), (0.012, y + 0.27), (0.012, y + 0.32)], x, 0.12, 0.0, 8)
    z0 = 1.3
    p.box('dkwood', 0.2, L1 - 0.2, 0.0, 1.05, z0, z0 + 0.5); p.cham('stone_f', 0.15, L1 - 0.15, 1.05, 1.1, z0 - 0.05, z0 + 0.6, 0.008)
    p.box('gold', 0.2, L1 - 0.2, 0.75, 0.78, z0 + 0.5, z0 + 0.51)
    seg_cyl(p, 'gold', (0.25, 0.2, z0 + 0.62), (L1 - 0.25, 0.2, z0 + 0.62), 0.022, 10)
    for x in np.arange(0.6, L1 - 0.3, 0.7):
        lathe(p, 'gold', [(0.2, 0.0), (0.2, 0.02), (0.03, 0.05), (0.03, 0.72)], x, z0 + 1.05, 0.0, 12); p.cyl('fabric2', 0.19, 0.72, 0.8, x, z0 + 1.05, 16)
    return p
def table_set(n=4, r=0.45, chair_mat='fabric', top='linen'):
    p = Piece()
    lathe(p, 'steel', [(0.24, 0.0), (0.24, 0.02), (0.05, 0.06), (0.035, 0.72)], sec=12); p.cyl(top, r, 0.72, 0.76, 0, 0, 28)
    if top == 'linen': lathe(p, 'linen', [(r + 0.02, 0.76), (r + 0.06, 0.45), (r + 0.05, 0.44)], sec=28)
    for k in range(n):
        a = 2 * math.pi * k / n; d = r + 0.32; q = Piece()
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)): seg_cyl(q, 'gold', (sx * 0.18, 0.0, sz * 0.18), (sx * 0.17, 0.45, sz * 0.17), 0.012, 6)
        q.cham(chair_mat, -0.21, 0.21, 0.45, 0.5, -0.21, 0.21, 0.015); q.cham(chair_mat, -0.2, 0.2, 0.5, 0.95, -0.24, -0.19, 0.015)
        p.merge(q, rot_y(-math.degrees(a) - 90, (d * math.cos(a), 0, d * math.sin(a))))
    return p
def buffet(L1=2.6):
    p = Piece()
    p.box('linen', 0.0, L1, 0.0, 0.76, 0.0, 0.8); p.box('linen', -0.01, L1 + 0.01, 0.6, 0.78, -0.01, 0.81)
    for x in np.linspace(0.5, L1 - 0.5, 3):
        p.box('steel', x - 0.3, x + 0.3, 0.78, 0.86, 0.15, 0.65); p.hull('steel', [(x + dx, 0.86 + 0.15 * math.sin(t), 0.4 + 0.25 * math.cos(t)) for dx in (-0.3, 0.3) for t in np.linspace(0, math.pi, 7)])
    return p
def planter_tree(h=2.4):
    p = Piece(); lathe(p, 'dark', [(0.3, 0.0), (0.36, 0.6), (0.38, 0.62), (0.0, 0.62)], sec=20); p.cyl('mulch', 0.33, 0.6, 0.63, 0, 0, 20)
    lathe(p, 'bark', [(0.04, 0.6), (0.03, h - 0.5)], sec=8); p.sphere('leaf2', 0.55, 0, h - 0.3, 0, 2); p.sphere('leaf2', 0.35, 0.25, h - 0.6, 0.1, 1)
    return p
def luggage_cart():
    p = Piece()
    p.cham('dkwood', -0.5, 0.5, 0.2, 0.26, -0.3, 0.3, 0.01)
    for s in (-1, 1):
        for z in (-0.25, 0.25): p.cyl('dark', 0.07, 0.0, 0.14, s * 0.4, z, 10) if False else seg_cyl(p, 'dark', (s * 0.4, 0.08, z - 0.02), (s * 0.4, 0.08, z + 0.02), 0.08, 12)
        seg_cyl(p, 'gold', (s * 0.45, 0.26, 0.0), (s * 0.45, 1.75, 0.0), 0.022, 10)
    pts = [(0.45 * math.cos(t), 1.75 + 0.3 * math.sin(t), 0.0) for t in np.linspace(0, math.pi, 11)]
    for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'gold', a, b, 0.022, 10)
    seg_cyl(p, 'gold', (-0.45, 1.2, 0.0), (0.45, 1.2, 0.0), 0.015, 8)
    p.cham('fabric2', -0.35, 0.05, 0.26, 0.86, -0.2, 0.15, 0.03); p.cham('dark', 0.1, 0.42, 0.26, 0.68, -0.18, 0.12, 0.03)
    return p

# ============================================================================ terreno
SX0, SX1, SZ0, SZ1 = -13.0, 13.0, -9.0, 22.0
POD = sbox(-PX, PZ0, PX, PZ1)
DROP = sbox(-6.0, PZ1, 6.0, 11.0)                                   # calcada de embarque sob a marquise
ISL = Point(0.0, 16.5).buffer(2.6, 32).union(sbox(-5.0, 15.6, 5.0, 17.4))
STREET = sbox(SX0, 19.0, SX1, SZ1)
APRONS = [sbox(-11.0, 19.0, -7.0, SZ1), sbox(7.0, 19.0, 11.0, SZ1)]
LANE = LineString([(-9.0, SZ1), (-9.0, 15.0), (-6.0, 12.6), (6.0, 12.6), (9.0, 15.0), (9.0, SZ1)]).buffer(2.0, 8, join_style=1)
def paving(poly, y1, joints=1.5, mat='concrete', gap=0.006):
    p = Piece(); b = poly.bounds
    for x in np.arange(b[0], b[2], joints):
        for z in np.arange(b[1], b[3], joints):
            q = sbox(x + gap, z + gap, x + joints - gap, z + joints - gap).intersection(poly); ext_y(p, mat, q, 0.0, y1)
    ext_y(p, 'dark', poly.buffer(-0.002), 0.0, y1 - 0.008)
    return p
def site():
    """Terreno (pivo: origem): pista em laco ate a marquise, calcada de embarque e calcada da rua com juntas, ilha com grama,
    gramados com guia, faixa de pedestres e pintura."""
    p = Piece()
    lane = LANE.intersection(sbox(SX0, PZ1, SX1, SZ1)).difference(DROP).difference(ISL)
    walk = unary_union([DROP, STREET.difference(unary_union(APRONS)), sbox(SX0, PZ0 - 3.0, SX1, PZ0).difference(POD), sbox(-PX - 3.0, PZ0, -PX, PZ1), sbox(PX, PZ0, PX + 3.0, PZ1),
                        sbox(-PX - 3.0, PZ1, -6.0, 11.0), sbox(6.0, PZ1, PX + 3.0, 11.0)]).difference(POD).difference(lane)
    aspl = unary_union([lane] + [a.difference(lane) for a in APRONS]).intersection(sbox(SX0, SZ0, SX1, SZ1))
    ext_y(p, 'asphalt', aspl.buffer(-0.001, join_style=2), 0.0, 0.03)
    q = paving(walk.intersection(sbox(SX0, SZ0, SX1, SZ1)), Y0); p.merge(q)
    grass = sbox(SX0, SZ0, SX1, SZ1).difference(unary_union([walk, aspl, POD]))
    for g in getattr(grass, 'geoms', [grass]):
        if g.area < 0.05: continue
        inner = g.buffer(-0.15, join_style=2); ext_y(p, 'grass', inner, 0.0, 0.13); ext_y(p, 'curb', g.difference(inner).buffer(-0.001, join_style=2), 0.0, 0.16)
    for k in range(6): p.box('paint_w', -2.0 + k * 0.8, -1.6 + k * 0.8, 0.03, 0.034, 11.1, 12.0) if False else p.box('paint_w', -2.4 + k * 0.85, -2.0 + k * 0.85, 0.03, 0.034, 11.05, 11.9) if False else None
    for x in np.arange(-4.6, 4.7, 0.9): p.box('paint_w', x - 0.2, x + 0.2, 0.03, 0.034, 11.4, 12.1) if False else None
    p.box('paint_y', -6.0, 6.0, Y0, Y0 + 0.004, 10.95, 11.0)
    return p
def flagpole(mat='flag_r'):
    p = Piece(); p.cham('concrete', -0.3, 0.3, 0.0, 0.2, -0.3, 0.3, 0.01)
    lathe(p, 'steel', [(0.06, 0.2), (0.035, 9.0)], sec=10); p.sphere('gold', 0.07, 0, 9.05, 0, 1)
    rng = np.random.default_rng(5); pts = []
    for i in range(9):
        x = 0.04 + i * 0.18; dz = 0.06 * math.sin(i * 0.9)
        for y in (8.0, 8.9): pts.append((x, y, dz))
    for i in range(8):
        a, b = pts[2 * i:2 * i + 2], pts[2 * i + 2:2 * i + 4]
        p.hull(mat, [(x, y, z + dz) for (x, y, z) in a + b for dz in (-0.006, 0.006)])
    return p
def lamp_post():
    p = Piece(); p.cyl('concrete', 0.22, 0.0, 0.4, 0, 0, 14)
    lathe(p, 'dark', [(0.09, 0.4), (0.06, 4.2)], sec=12); seg_cyl(p, 'dark', (0, 4.1, 0), (0.6, 4.3, 0), 0.03, 8)
    p.cham('dark', 0.45, 0.95, 4.22, 4.36, -0.16, 0.16, 0.02); p.box('lamp_glass', 0.48, 0.92, 4.21, 4.22, -0.13, 0.13)
    return p
def bench():
    p = Piece(); L1 = 1.8
    for s in (-1, 1): p.cham('concrete', s * 0.7 - 0.12, s * 0.7 + 0.12, 0.0, 0.42, -0.25, 0.25, 0.01)
    for i in range(5): z = -0.24 + i * 0.1; p.cham('wood', -L1 / 2, L1 / 2, 0.42, 0.46, z, z + 0.085, 0.006)
    return p
def bollard():
    p = Piece(); p.cyl('steel', 0.09, 0.0, 0.9, 0, 0, 14); p.sphere('steel', 0.09, 0, 0.9, 0, 1); p.cyl('lamp_glass', 0.092, 0.75, 0.8, 0, 0, 14); return p
def bike_rack():
    p = Piece()
    for k in range(4):
        x = -0.9 + k * 0.6; pts = [(x, 0.0, -0.35)] + [(x, 0.55 + 0.3 * math.sin(t), -0.35 * math.cos(t)) for t in np.linspace(0, math.pi, 9)] + [(x, 0.0, 0.35)]
        for a, b in zip(pts[:-1], pts[1:]): seg_cyl(p, 'steel', a, b, 0.025, 8)
    return p
def tree(h=6.0, r=1.9, mat='leaf', seed=1):
    p = Piece(); rng = np.random.default_rng(seed)
    lathe(p, 'bark', [(0.18, 0.0), (0.13, 0.5), (0.1, h * 0.6)], sec=10)
    for (dx, dz, yy) in ((0.6, 0.0, h * 0.62), (-0.5, 0.4, h * 0.66), (0.0, -0.5, h * 0.7)): seg_cyl(p, 'bark', (0.0, h * 0.45, 0.0), (dx * 0.8, yy, dz * 0.8), 0.05, 6)
    p.sphere(mat, r, 0.0, h * 0.78, 0.0, 2)
    for _ in range(8):
        a = rng.uniform(0, 2 * math.pi); rr = r * rng.uniform(0.45, 0.65); p.sphere(mat, rr, math.cos(a) * r * 0.7, h * 0.78 + rng.uniform(-0.4, 0.5) * r, math.sin(a) * r * 0.7, 1)
    ext_y(p, 'mulch', Point(0, 0).buffer(0.8, 20), 0.0, 0.02)
    return p
def bush(r=0.5):
    p = Piece(); rng = np.random.default_rng(3); p.sphere('hedge', r, 0.0, r * 0.85, 0.0, 2)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi); p.sphere('hedge', r * 0.55, math.cos(a) * r * 0.6, r * rng.uniform(0.7, 1.2), math.sin(a) * r * 0.6, 1)
    return p
def door_leaf_glass(w=0.84, h=2.34, t=0.045):
    p = Piece(); s = 0.1
    p.box('frame', 0.0, s, 0.0, h, -t / 2, t / 2); p.box('frame', w - s, w, 0.0, h, -t / 2, t / 2)
    p.box('frame', s, w - s, h - s, h, -t / 2, t / 2); p.box('frame', s, w - s, 0.0, 0.2, -t / 2, t / 2)
    p.box('glass', s, w - s, 0.2, h - s, -0.004, 0.004)
    for z in (1, -1):
        seg_cyl(p, 'gold', (w - 0.17, 0.75, z * (t / 2 + 0.05)), (w - 0.17, 1.75, z * (t / 2 + 0.05)), 0.016, 8)
        for y in (0.8, 1.7): seg_cyl(p, 'gold', (w - 0.17, y, z * t / 2), (w - 0.17, y, z * (t / 2 + 0.05)), 0.01, 6)
    for yy in (0.2, 2.1): p.cyl('steel', 0.01, yy, yy + 0.08, 0.0, t / 2 + 0.002, 8)
    return p

# ============================================================================ pecas
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(float(x), 3), round(float(y), 3), round(float(z), 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)

pieces = {
    't_corner': tcorner(), 'p_corner': pcorner(True), 'slab_typ': slab_typ('typ'), 'slab_roof': slab_typ('roof'),
    'stair_tower': stair_u(HF, 8, ZBK), 'stair_podium': stair_u(HP, 10), 'plan_floor': plan_typ(),
    'room_front': room_furn(True, 3.69), 'room_front_c': room_furn(True, 3.88), 'room_back': room_furn(False, 3.69),
    'balcony': balcony(), 'terrace': terrace(), 'roof_top': roof_top(), 'canopy': canopy(),
    'column': column(), 'floor_ground': pod_floor('g'), 'floor_podium': pod_floor('p'), 'plan_ground': plan_pod('g'), 'plan_podium': plan_pod('p'),
    'reception': reception(), 'lobby_panel': lobby_wall_panel(), 'lounge': lounge(), 'bar': bar(3.0), 'table_set': table_set(4),
    'buffet': buffet(2.6), 'planter_tree': planter_tree(), 'luggage_cart': luggage_cart(),
    'site': site(), 'flagpole_r': flagpole('flag_r'), 'flagpole_w': flagpole('flag_w'), 'flagpole_b': flagpole('flag_b'),
    'lamp_post': lamp_post(), 'bench': bench(), 'bollard': bollard(), 'bike_rack': bike_rack(), 'tree': tree(), 'tree_b': tree(4.6, 1.5, 'leaf2', 4),
    'bush': bush(), 'door_leaf_glass': door_leaf_glass(), 'door_leaf_back': door_back(0.94, 2.16), 'door_leaf_interior': door_interior(0.82, 2.06),
    'door_leaf_bath': door_interior(0.68, 2.06), 'player_scale_ref': player_ref()}
pieces['room_front_r'] = mirrored(pieces['room_front'], mirror_x()); pieces['room_back_r'] = mirrored(pieces['room_back'], mirror_x())
for k in ('win', 'bal', 'plain', 'curt', 'cwin_l', 'cwin_r'): pieces[f't_{k}'] = tw(k)
for k in ('glass', 'door_l', 'door_r', 'svc', 'plain'): pieces[f'pg_{k}'] = pod_ground(k)
pieces['pu_win'] = pod_upper('win'); pieces['pu_plain'] = pod_upper('plain'); pieces['pu_plain_np'] = pod_upper('plain', False)
pieces['pu_plain_e'] = trimmed(pod_upper('plain'), [-0.999, 0, 0], [1, 0, 0])      # ponta junto da torre, 1 mm recuada

# ============================================================================ montagem
# torre
TXM = [-5, -3, -1, 1, 3, 5]
T_FRONT = {-5: 'win', -3: 'bal', -1: 'win', 1: 'bal', 3: 'bal', 5: 'win'}
T_BACK = {-5: 'win', -3: 'win', -1: 'curt', 1: 'curt', 3: 'win', 5: 'win'}          # x do mundo
T_WEST = {-5: 'win', -3: 'plain', -1: 'cwin_l', 1: 'plain', 3: 'win', 5: 'win'}
T_EAST = {-5: 'win', -3: 'plain', -1: 'cwin_r', 1: 'plain', 3: 'win', 5: 'win'}
for k in range(NF):
    y = YT + k * HF; tg = [f'floor{k + 2}']
    for x in TXM:
        put(f't_{T_FRONT[x]}', x, y, TZ1, 0, tg + ['front', 'ext']); put(f't_{T_BACK[x]}', x, y, TZ0, 180, tg + ['back', 'ext'])
    for z in TXM:
        put(f't_{T_WEST[z]}', -TX, y, z, -90, tg + ['left', 'ext']); put(f't_{T_EAST[z]}', TX, y, z, 90, tg + ['right', 'ext'])
    for (x, z, ry) in ((TX, TZ1, 0), (-TX, TZ1, -90), (TX, TZ0, 90), (-TX, TZ0, 180)): put('t_corner', x, y, z, ry, tg + ['ext'])
    put('slab_typ', 0, y, 0, 0, tg); put('plan_floor', 0, y, 0, 0, tg); put('stair_tower', 0, y, 0, 0, tg)
    if k >= 1:
        for x in (-3, 1, 3): put('balcony', x, y, TZ1, 0, tg + ['front', 'ext'])
    zf, zb = 1.96 + t_ / 2, ZBB - t_ / 2
    put('room_front', -5.75, y, zf, 0, tg); put('room_front_c', -1.94, y, zf, 0, tg); put('room_front_r', 5.75, y, zf, 0, tg)
    put('room_back', -5.75, y, zb, 0, tg); put('room_back_r', 5.75, y, zb, 0, tg)
    yd = y + 0.01
    for (xa, xb, s) in FRONT_ROOMS:
        c = entry_x(xa, xb, s); xw = xa + 2.06 if s == 'l' else xb - 2.06
        if s == 'l': put('door_leaf_interior', c + 0.41, yd, ZF, 180, tg, door=90)
        else: put('door_leaf_interior', c - 0.41, yd, ZF, 0, tg, door=-90)
        put('door_leaf_bath', xw, yd, 1.0 - 0.34, -90, tg, door=-90 if s == 'l' else 90)
    for (xa, xb, s) in BACK_ROOMS:
        c = entry_x(xa, xb, s); xw = xa + 2.06 if s == 'l' else xb - 2.06
        if s == 'l': put('door_leaf_interior', c + 0.41, yd, ZB, 180, tg, door=-90)
        else: put('door_leaf_interior', c - 0.41, yd, ZB, 0, tg, door=90)
        put('door_leaf_bath', xw, yd, -2.4 + 0.34, 90, tg, door=90 if s == 'l' else -90)
    put('door_leaf_interior', SD - 0.41, yd, ZB, 0, tg, door=90)
put('slab_roof', 0, YR, 0, 0, ['roof']); put('roof_top', 0, YR, 0, 0, ['roof'])
put('door_leaf_back', -0.95 - 0.47, YR + 0.012, -1.35, 0, ['roof'], door=-90)
# embasamento
PXM = [-7, -5, -3, -1, 1, 3, 5, 7]; PZM = [-5, -3, -1, 1, 3, 5, 7, 9]
for x in PXM:
    put({-1: 'pg_door_l', 1: 'pg_door_r'}.get(x, 'pg_glass'), x, Y0, PZ1, 0, ['floor0', 'front', 'ext']); put('pu_win', x, Y1, PZ1, 0, ['floor1', 'front', 'ext'])
    put('pg_svc' if x == -5 else 'pg_plain', x, Y0, PZ0, 180, ['floor0', 'back', 'ext']); put('pu_plain_e' if abs(x) == 7 else 'pu_plain_np', x, Y1, PZ0, 180, ['floor1', 'back', 'ext'])
for z in PZM:
    put('pg_plain' if z < 0 else 'pg_glass', -PX, Y0, z, -90, ['floor0', 'left', 'ext']); put('pg_plain' if z < 0 else 'pg_glass', PX, Y0, z, 90, ['floor0', 'right', 'ext'])
    put('pu_plain' if z < 0 else 'pu_win', -PX, Y1, z, -90, ['floor1', 'left', 'ext']); put('pu_plain' if (z < 0 or z in (3, 5)) else 'pu_win', PX, Y1, z, 90, ['floor1', 'right', 'ext'])
for (x, z, ry) in ((PX, PZ1, 0), (-PX, PZ1, -90), (PX, PZ0, 90), (-PX, PZ0, 180)): put('p_corner', x, Y0, z, ry, ['ext'])
put('door_leaf_glass', -0.84, Y0 + 0.01, PZ1 - 0.12, 0, ['floor0', 'front', 'ext'], door=-95)
put('door_leaf_glass', 0.84, Y0 + 0.01, PZ1 - 0.12, 180, ['floor0', 'front', 'ext'], door=95)
hx, hz = hinge(-5.0, PZ0, 180, -0.47, -T / 2); put('door_leaf_back', hx, Y0 + 0.012, hz, 180, ['floor0', 'back', 'ext'], door=90)
put('floor_ground', 0, Y0, 0, 0, ['floor0']); put('floor_podium', 0, Y1, 0, 0, ['floor1'])
put('plan_ground', 0, Y0, 0, 0, ['floor0']); put('plan_podium', 0, Y1, 0, 0, ['floor1'])
put('stair_podium', 0, Y0, 0, 0, ['floor0']); put('stair_podium', 0, Y1, 0, 0, ['floor1'])
for (y, tg) in ((Y0, ['floor0']), (Y1, ['floor1'])):
    for c in (-5.0, SD, 5.0): put('door_leaf_interior', c - 0.41, y + 0.01, ZB, 0, tg, door=90)
    for (x, z) in ((-6, 6), (-2, 6), (2, 6), (6, 6), (-6, 2), (6, 2)): put('column', x, y, z, 0, tg)
put('terrace', 0, YT, 0, 0, ['terrace']); put('slab_typ', 0, YT, 0, 0, ['floor2'])
# saguao e salao
put('reception', -4.5, Y0, 0.9, 0, ['floor0']); put('lobby_panel', -PX + T, Y0, 4.0, 90, ['floor0']); put('lounge', 4.0, Y0, 4.0, 0, ['floor0'])
put('luggage_cart', -1.6, Y0, 1.9, 20, ['floor0'])
for (x, z) in ((-2.8, 9.1), (2.8, 9.1), (-7.1, 9.1), (7.1, 9.1)): put('planter_tree', x, Y0, z, 0, ['floor0'])
put('bar', PX - T, Y1, 2.5, -90, ['floor1']); put('buffet', -4.2, Y1, ZB + t_ / 2, 0, ['floor1'])
for (x, z) in ((-4.0, 3.8), (-4.0, 8.2), (0.0, 3.8), (0.0, 8.2), (4.0, 8.2)): put('table_set', x, Y1, z, 0, ['floor1'])
for (x, z) in ((-7.1, 9.1), (7.1, 9.1)): put('planter_tree', x, Y1, z, 0, ['floor1'])
# marquise e terreno
put('canopy', 0, 0, PZ1, 0, ['site', 'front'])
put('site', 0, 0, 0, 0, ['site'])
for (x, k) in ((-1.5, 'flagpole_r'), (0.0, 'flagpole_w'), (1.5, 'flagpole_b')): put(k, x, 0.13, 16.5, 0, ['site'])
for (x, z, ry) in ((-10.5, -1.0, 0), (-10.5, 7.0, 0), (10.5, -1.0, 180), (10.5, 7.0, 180), (-4.5, 21.3, 90), (4.5, 21.3, 90)): put('lamp_post', x, Y0, z, ry, ['site'])
for x in (-5.0, 5.0): put('bench', x, Y0, 10.45, 0, ['site'])
for x in (-4.6, -2.0, 2.0, 4.6): put('bollard', x, Y0, 10.85, 0, ['site'])
put('bike_rack', -9.6, Y0, 3.0, 90, ['site'])
for (x, z, k) in ((-12.0, -4.4, 'tree'), (-12.0, 1.5, 'tree_b'), (-12.0, 9.0, 'tree'), (12.0, -4.4, 'tree_b'), (12.0, 1.5, 'tree'), (12.0, 9.0, 'tree_b')): put(k, x, 0.13, z, 0, ['site'])
for (x, z) in ((-12.0, 14.0), (12.0, 14.0), (-12.0, -2.2), (12.0, -2.2)): put('bush', x, 0.13, z, 0, ['site'])
put('player_scale_ref', 0.0, 0.03, 12.6); put('player_scale_ref', 1.0, Y0, 3.0, 0, ['floor0'])


if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)
    layout = {'grid': {'module_width': W, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': Y0,
                       'podium': {'x': [-PX, PX], 'z': [PZ0, PZ1], 'floors': 2, 'floor_height': HP, 'levels': [Y0, Y1], 'terrace': YT},
                       'tower': {'x': [-TX, TX], 'z': [TZ0, TZ1], 'floors': NF, 'floor_height': HF, 'first_floor': YT, 'roof': YR},
                       'site': {'x': [SX0, SX1], 'z': [SZ0, SZ1], 'walk_level': Y0},
                       'roof': 'flat membrane roofs with parapets: planted terrace on the podium, machine room, condensers and a blank sign on the tower',
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
