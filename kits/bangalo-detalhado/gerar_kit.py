"""Kit piloto de ALTO DETALHE: o mesmo bangalo do kit 7 (14 x 12 m, mesma planta e montagem), refeito com:
  - tabuas de fachada em geometria (cada fiada e uma cunha sobreposta), telhas em fiadas com degrau real;
  - janelas de guilhotina com duas folhas, travessas, peitoril com pingadeira, avental e verga craftsman;
  - calhas K com cantos em meia-esquadria, condutores com cotovelos, abracadeiras e bloco de respingo;
  - cachorros (pontas de caibro) sob o beiral, maos-francesas e tercas aparentes no frontao da varanda;
  - degraus com bocel arredondado e muretas laterais, pilares com cimalha de tijolo e capa chanfrada;
  - portas com almofadas rebaixadas e chanfradas feitas no Blender (booleano + bevel), macaneta e dobradicas;
  - lanterna pendente na varanda e arandela na porta dos fundos;
  - texturas PBR (cor + normal + ORM) geradas por scripts/texturas/gerar_texturas.py, estilo 'detalhado'.
Y para cima, 1 unidade = 1 m. Mesmo padrao de medidas (PADRAO_METRICAS.md) e mesmas regras contra flicker.
Dependencias: trimesh shapely numpy pillow scipy mapbox_earcut  (+ bpy, o Blender como modulo Python: pip install bpy)
"""
import numpy as np, trimesh, json, os, math, sys, io, struct
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
from PIL import Image
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT + '/pieces', exist_ok=True)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'texturas'))
import gerar_texturas as GT

# ============================================================================ materiais
COL = {'siding': (118, 146, 104), 'shingles': (64, 66, 74), 'ridge': (58, 60, 66), 'trim': (240, 234, 218), 'frame': (240, 234, 218),
       'sash': (250, 246, 236), 'door': (138, 54, 42), 'door_int': (236, 228, 210), 'deck': (150, 104, 70), 'floor': (176, 128, 86),
       'brick': (166, 80, 60), 'cap': (196, 190, 178), 'iron': (40, 40, 44), 'brass': (196, 160, 84), 'ceiling': (206, 226, 224),
       'glass': (150, 186, 204), 'gutter': (92, 76, 62), 'dark': (36, 34, 34), 'plaster': (238, 230, 214), 'tile': (214, 224, 228),
       'lamp_glass': (255, 214, 140), 'concrete': (176, 172, 164), 'player': (90, 140, 220), 'clay': (172, 96, 62)}
PX_M = 192          # pixels por metro das texturas (ladrilho de 2 m = 384 px)
TILE = 2.0          # todas as texturas repetem a cada 2 m (divide o modulo)

def wood_paint(px, size, col, seed, rough=0.5):
    """Madeira pintada SEM linhas de tabua (as tabuas sao geometria): veio alongado em x, pinceladas, poros."""
    W_, H_ = int(size[0] * px), int(size[1] * px)
    g = GT.noise(H_, W_, 0.6 * px, 0.003 * px, seed); g2 = GT.noise(H_, W_, 0.08 * px, 0.0015 * px, seed + 1)
    brush = GT.noise(H_, W_, 0.05 * px, 0.004 * px, seed + 2)
    alb = GT.rgb(col)[None, None] * (1 + 0.03 * g[..., None] + 0.02 * brush[..., None])
    hm = 0.00035 * g + 0.0002 * g2 + 0.0001 * brush
    return alb, hm, rough + 0.06 * GT.fbm(H_, W_, 0.05 * px, 2, seed + 3), 1.0, 0.002

def planks(px, size, col, seed, w=0.14, rough=0.62):
    """Tabuas de assoalho ao longo de x (larguras de 0,14 m, emendas desencontradas), veio e verniz."""
    W_, H_ = int(size[0] * px), int(size[1] * px)
    n = int(round(size[1] / w)); rows = [size[1] / n] * n
    cuts = [[(GT.hash01(r, seed) * 2.0 + k * 1.0) % size[0] for k in range(2)] for r in range(n)]
    uid, dist, U, V = GT.bond(H_, W_, rows, cuts, 0.004, px)
    r1 = GT.per_unit(uid, seed); g = GT.noise(H_, W_, 0.4 * px, 0.002 * px, seed + 1)
    knots = GT.smooth(2.3, 3.0, GT.noise(H_, W_, 0.012 * px, 0.008 * px, seed + 2))
    alb = GT.rgb(col)[None, None] * (0.86 + 0.24 * r1[..., None]) * (1 + 0.08 * g[..., None]) * (1 - 0.35 * knots[..., None])
    unit = GT.smooth(0, 0.0012, dist); alb = GT.lerp(alb * 0.35, alb, unit[..., None])
    hm = 0.0015 * GT.smooth(0, 0.002, dist) + 0.0003 * g
    return alb, hm, rough + 0.12 * (1 - unit) + 0.05 * g, 1.0, 0.003

def tex_set(alb, hm, rough, nstr, aod, px):
    ao = GT.cavity_ao(hm, px, aod)
    orm = np.stack([ao, np.clip(rough, 0.05, 1), np.zeros_like(ao)], -1)
    return GT.to_img(np.clip(alb, 0, 1)), GT.to_img(GT.normal_from_height(hm, px, nstr)), GT.to_img(orm)

C = GT.CORES
C['siding'] = COL['siding']; C['shingles'] = COL['shingles']
TEXDEF = {
    'siding': (lambda r: (r[0], r[1], r[2] + 0.25, r[3], r[4]))(GT.siding('detalhado', PX_M, (TILE, TILE), COL['siding'], 51)),   # fiadas de 0,2 m alinhadas com as tabuas de geometria
    'brick': GT.masonry('detalhado', PX_M, (TILE, TILE), [0.125] * 16, GT.running(2, 16, 0.25), 0.012, C['brick'], C['brick_mortar'], 7, 0.008, irregular=0.0015),
    'shingles': GT.shingles('detalhado', PX_M, (TILE, TILE), COL['shingles'], 41),
    'plaster': GT.stucco('detalhado', PX_M, (TILE, TILE), C['plaster'], 5, coarse=0.6),
    'deck': planks(PX_M, (TILE, TILE), COL['deck'], 61, w=0.2),        # tabuas do deck sao geometria: so o veio importa
    'floor': planks(PX_M, (TILE, TILE), COL['floor'], 63),
    'cap': GT.stucco('detalhado', PX_M, (TILE, TILE), COL['cap'], 9, coarse=1.0),
}
TEX = {k: tex_set(*v, PX_M) for k, v in TEXDEF.items()}
for k, (a, n, o) in TEX.items():
    a.save(f'{OUT}/{k}_albedo.png'); n.save(f'{OUT}/{k}_normal.png'); o.save(f'{OUT}/{k}_orm.png')
MATS = {k: PBRMaterial(name=k, baseColorFactor=[c / 255 for c in v] + [1.0], metallicFactor=0.0, roughnessFactor=0.6) for k, v in COL.items()}
for k in ('iron', 'brass', 'gutter'): MATS[k].metallicFactor = 0.6; MATS[k].roughnessFactor = 0.45
for k in ('ridge', 'concrete', 'dark', 'clay'): MATS[k].roughnessFactor = 0.9
MATS['glass'].roughnessFactor = 0.08; MATS['glass'].metallicFactor = 0.2
MATS['lamp_glass'] = PBRMaterial(name='lamp_glass', baseColorFactor=[1, 0.86, 0.6, 1], emissiveFactor=[1.0, 0.72, 0.36], metallicFactor=0, roughnessFactor=0.3)
for k, (a, n, o) in TEX.items():
    MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=n, occlusionTexture=o, metallicRoughnessTexture=o,
                          baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)

# ============================================================================ peca + utilitarios de geometria
class Piece:
    def __init__(s): s.parts = {}; s.uv = {}       # uv[mat] = funcao(vertices, normais) -> uv (sobrescreve a projecao em caixa)
    def add(s, mat, m): s.parts.setdefault(mat, []).append(m); return s
    def box(s, mat, x0, x1, y0, y1, z0, z1):
        b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0]); b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return s.add(mat, b)
    def cham(s, mat, x0, x1, y0, y1, z0, z1, c=0.01):
        """Caixa chanfrada (todas as arestas com chanfro c): fica bonita na luz e no contorno."""
        c = min(c, (x1 - x0) / 2.2, (y1 - y0) / 2.2, (z1 - z0) / 2.2)
        pts = []
        for (a, b, d) in ((c, c, 0), (c, 0, c), (0, c, c)):
            for X in (x0 + a, x1 - a):
                for Y in (y0 + b, y1 - b):
                    for Z in (z0 + d, z1 - d): pts.append((X, Y, Z))
        return s.add(mat, trimesh.convex.convex_hull(np.array(pts)))
    def cyl(s, mat, r, y0, y1, x=0, z=0, sec=12):
        c = trimesh.creation.cylinder(radius=r, height=y1 - y0, sections=sec); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([x, (y0 + y1) / 2, z]); return s.add(mat, c)
    def sphere(s, mat, r, x, y, z, sub=1):
        c = trimesh.creation.icosphere(subdivisions=sub, radius=r); c.apply_translation([x, y, z]); return s.add(mat, c)
    def hull(s, mat, pts): return s.add(mat, trimesh.convex.convex_hull(np.array(pts, float)))
    def seg(s, mat, p0, p1, w, d=None):
        d = w if d is None else d
        p0, p1 = np.array(p0, float), np.array(p1, float); v = p1 - p0; L = np.linalg.norm(v)
        b = trimesh.creation.box(extents=[w, d, L]); z = np.array([0, 0, 1.0]); v = v / L
        ax = np.cross(z, v); ang = math.acos(np.clip(np.dot(z, v), -1, 1))
        if np.linalg.norm(ax) > 1e-6: b.apply_transform(trimesh.transformations.rotation_matrix(ang, ax))
        b.apply_translation((p0 + p1) / 2); return s.add(mat, b)
    def merge(s, other, T=np.eye(4)):
        for k, ms in other.parts.items():
            for m in ms: mm = m.copy(); mm.apply_transform(T); s.add(k, mm)
        return s
    def tris(s): return sum(len(m.faces) for ms in s.parts.values() for m in ms)
    def scene(s, name):
        sc = trimesh.Scene()
        for k, ms in s.parts.items():
            m = trimesh.util.concatenate(ms); m.unmerge_vertices()
            if k in TEX:
                v = m.vertices; n = np.repeat(m.face_normals, 3, axis=0)
                if k in s.uv: uv = s.uv[k](v, n)
                else:
                    uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1)
                    uv[ax == 0] = v[ax == 0][:, [2, 1]]; uv[ax == 2] = v[ax == 2][:, [0, 1]]; uv[ax == 1] = v[ax == 1][:, [0, 2]]
                    uv /= TILE
                    if k == 'plaster': uv[ax == 1] = 0.37
                    if k == 'siding': uv[ax == 1] = 0.37
                    if k == 'siding': uv[ax != 1, 1] = (v[ax != 1, 1] - WT) / TILE   # fase: a borda de baixo de cada tabua cai na sombra pintada   # tetos e topos de parede: cor lisa (sobreposicoes iguais)
                m.visual = TextureVisuals(uv=uv, material=MATS[k])
            else: m.visual = TextureVisuals(material=MATS[k])
            sc.add_geometry(m, node_name=f'{name}_{k}', geom_name=f'{name}_{k}')
        return sc

def _fix(m):
    if m.volume < 0: m.invert()
    return m
def prof_x(p, mat, x0, x1, pts):
    """Perfil 2D em (z, y) extrudado ao longo de X, de x0 a x1. Pontas retas: modulos vizinhos encostam sem emenda."""
    m = trimesh.creation.extrude_polygon(Polygon(pts).buffer(0), x1 - x0); v = m.vertices
    m.vertices = np.stack([x0 + v[:, 2], v[:, 1], v[:, 0]], 1); return p.add(mat, _fix(m))
def prof_y(p, mat, y0, y1, pts):
    """Perfil 2D em (x, z) extrudado ao longo de Y."""
    m = trimesh.creation.extrude_polygon(Polygon(pts).buffer(0), y1 - y0); v = m.vertices
    m.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1); return p.add(mat, _fix(m))
def prof_z(p, mat, z0, z1, pts):
    """Perfil 2D em (x, y) extrudado ao longo de Z."""
    m = trimesh.creation.extrude_polygon(Polygon(pts).buffer(0), z1 - z0); m.apply_translation([0, 0, z0]); return p.add(mat, _fix(m))
def crect(a0, a1, b0, b1, c=0.008, corners=(1, 1, 1, 1)):
    """Retangulo com cantos chanfrados (para perfis). corners = (a0b0, a1b0, a1b1, a0b1)."""
    q = []
    for (a, b, sa, sb), on in zip(((a0, b0, 1, 1), (a1, b0, -1, 1), (a1, b1, -1, -1), (a0, b1, 1, -1)), corners):
        if on: q += [(a, b + sb * c), (a + sa * c, b)] if sa * sb > 0 else [(a + sa * c, b), (a, b + sb * c)]
        else: q.append((a, b))
    return q
def arc(cx, cy, r, a0, a1, n=6): return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(a0, a1, n)]
def slice_keep(m, origin, normal):
    """Mantem o lado de m para onde normal aponta (corte com tampa)."""
    return trimesh.intersections.slice_mesh_plane(m, plane_normal=normal, plane_origin=origin, cap=True)

# ============================================================================ Blender (bpy) headless: booleanos e bevel
_bpy = None
def blender():
    global _bpy
    if _bpy is None:
        import bpy; _bpy = bpy
        bpy.ops.wm.read_factory_settings(use_empty=True)
    return _bpy
def bl_obj(tm, name='o'):
    bpy = blender(); me = bpy.data.meshes.new(name)
    me.from_pydata(tm.vertices.tolist(), [], tm.faces.tolist()); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); return ob
def bl_get(ob):
    bpy = blender(); dg = bpy.context.evaluated_depsgraph_get(); ev = ob.evaluated_get(dg); me = ev.to_mesh()
    me.calc_loop_triangles()
    v = np.array([x.co[:] for x in me.vertices]); f = np.array([t.vertices[:] for t in me.loop_triangles])
    ev.to_mesh_clear(); m = trimesh.Trimesh(v, f, process=True)
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    return m
def bl_detail(base, cutters=(), bevel=0.006, segments=2, angle=35):
    """base: trimesh; cutters: trimeshes subtraidos (booleano EXACT). Depois bevel nas arestas vivas (limite por angulo)."""
    bpy = blender(); ob = bl_obj(base, 'base')
    if cutters:
        cu = bl_obj(trimesh.util.concatenate(list(cutters)), 'cut'); cu.hide_set(True)
        mo = ob.modifiers.new('bool', 'BOOLEAN'); mo.operation = 'DIFFERENCE'; mo.solver = 'EXACT'; mo.object = cu
    if bevel:
        mo = ob.modifiers.new('bev', 'BEVEL'); mo.width = bevel; mo.segments = segments
        mo.limit_method = 'ANGLE'; mo.angle_limit = math.radians(angle); mo.harden_normals = False
    return bl_get(ob)
def tbox(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0]); b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return b

# ============================================================================ grade, paredes (mesma base do kit 7)
W = 2.0; T = 0.3; H = 3.0; SLAB = 0.2; RAISE = 0.45
def lvl(fl): return RAISE + fl * H
def grid_solid(xs, ys, zs, cell):
    """Malha estanque numa grade retilinea (sem juncoes em T): modulos vizinhos parecem uma superficie so."""
    out = {}; nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1
    def get(i, j, k): return cell(i, j, k) if (0 <= i < nx and 0 <= j < ny and 0 <= k < nz) else None
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                m = get(i, j, k)
                if m is None: continue
                x0, x1, y0, y1, z0, z1 = xs[i], xs[i + 1], ys[j], ys[j + 1], zs[k], zs[k + 1]; q = []
                if get(i - 1, j, k) is None: q.append([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)])
                if get(i + 1, j, k) is None: q.append([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)])
                if get(i, j - 1, k) is None: q.append([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)])
                if get(i, j + 1, k) is None: q.append([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)])
                if get(i, j, k - 1) is None: q.append([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)])
                if get(i, j, k + 1) is None: q.append([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
                out.setdefault(m, []).extend(q)
    res = {}
    for m, qs in out.items():
        v = []; f = []
        for q in qs: b = len(v); v += q; f += [[b, b + 1, b + 2], [b, b + 2, b + 3]]
        mm = trimesh.Trimesh(np.array(v, float), np.array(f), process=False); mm.merge_vertices(); res[m] = mm
    return res
def wall_with_opening(p, mat, ow, oy0, oy1, h, inner='plaster', t=T, centered=False, y0=0.0):
    x = ow / 2; z0 = -t / 2 if centered else -t; zs = [z0, z0 + 0.02, z0 + t]
    if ow > 0:
        xs = [-W / 2, -x, x, W / 2]; ys = sorted(set([y0, max(oy0, y0), oy1, h - 0.005, h]))
        def cell(i, j, k):
            if i == 1 and ys[j] >= max(oy0, y0) - 1e-9 and ys[j + 1] <= oy1 + 1e-9: return None
            if k == 0 and ys[j] >= h - 0.0051 and not centered: return None   # topo: a camada interna para 5 mm abaixo (cantos sem faces coplanares)
            return inner if k == 0 else mat
    else:
        xs = [-W / 2, W / 2]; ys = [y0, h - 0.005, h]
        def cell(i, j, k):
            if k == 0 and j == 1 and not centered: return None
            return inner if k == 0 else mat
    for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)

# ---------- tabuas sobrepostas (lap siding) em geometria ----------
FRIEZE = 2.72; HW = H + 0.03; FT = H; WT = 0.12      # topo da testeira do rodape (water table)
NC = 13; EXPO = (FRIEZE - WT) / NC; LAP = 0.03; TB = 0.024; TT = 0.007   # fiadas, exposicao, sobreposicao, espessura em baixo/em cima
def board(p, x0, x1, k, ya=None, yb=None):
    """Cunha da fiada k entre ya e yb (padrao: a tabua inteira). A face da frente e inclinada: a borda de baixo faz sombra."""
    b0 = WT + k * EXPO; b1 = b0 + EXPO + (LAP if k < NC - 1 else 0.0)
    ya = b0 if ya is None else max(ya, b0); yb = b1 if yb is None else min(yb, b1)
    if yb - ya < 1e-4 or x1 - x0 < 1e-4: return
    th = lambda y: TB - (TB - TT) * (y - b0) / (b1 - b0)
    p.hull('siding', [(x, y, z) for x in (x0, x1) for y in (ya, yb) for z in (0.0, th(y))])
def siding_field(p, holes=(), x0=-W / 2 + 0.0012, x1=W / 2 - 0.0012):
    """Preenche o modulo com tabuas, deixando buracos [(hx0, hx1, hy0, hy1)] para janelas/portas (cobertos pelas guarnicoes)."""
    for k in range(NC):
        b0 = WT + k * EXPO; b1 = b0 + EXPO + LAP
        cuts = sorted(set([b0, b1] + [y for h in holes for y in (h[2], h[3]) if b0 < y < b1]))
        for ya, yb in zip(cuts[:-1], cuts[1:]):
            xs = [(x0, x1)]
            for (hx0, hx1, hy0, hy1) in holes:
                if ya >= hy0 - 1e-9 and yb <= hy1 + 1e-9:
                    xs = [s for a, b in xs for s in ((a, min(b, hx0)), (max(a, hx1), b)) if s[1] - s[0] > 1e-4]
            for a, b in xs: board(p, a, b, k, ya, yb)

# ---------- testeira do rodape, friso sob o beiral ----------
def water_table(p, x0=-W / 2, x1=W / 2):
    p.box('brick', x0, x1, -RAISE, 0.0, -T, 0.0)
    # tabua com pingadeira chanfrada em cima: esconde a borda da laje e joga a agua para fora
    prof_x(p, 'trim', x0, x1, [(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)])
def frieze(p, x0=-W / 2, x1=W / 2):
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE), (0.034, FRIEZE), (0.034, FT), (0.0, FT)])
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE - 0.05), (0.03, FRIEZE - 0.035), (0.042, FRIEZE - 0.012), (0.042, FRIEZE + 0.02), (0.0, FRIEZE + 0.02)])  # cimalha

# ---------- janela de guilhotina craftsman ----------
def sash(p, x0, x1, y0, y1, z0, z1, lites=1, bot=0.07):
    """Folha de guilhotina: montantes e travessas chanfrados, vidro e (opcional) baguetes verticais."""
    s = 0.05
    p.cham('sash', x0, x0 + s, y0, y1, z0, z1, 0.008); p.cham('sash', x1 - s, x1, y0, y1, z0, z1, 0.008)
    p.cham('sash', x0 + s - 0.002, x1 - s + 0.002, y1 - s, y1, z0, z1, 0.008); p.cham('sash', x0 + s - 0.002, x1 - s + 0.002, y0, y0 + bot, z0, z1, 0.008)
    zc = (z0 + z1) / 2; p.box('glass', x0 + s - 0.004, x1 - s + 0.004, y0 + bot - 0.004, y1 - s + 0.004, zc - 0.003, zc + 0.003)
    for i in range(1, lites):
        xm = x0 + s + (x1 - x0 - 2 * s) * i / lites; p.cham('sash', xm - 0.013, xm + 0.013, y0 + bot, y1 - s, zc - 0.012, zc + 0.012, 0.005)
def window(p, ow, oy0, oy1, lites=3):
    """Janela no vao (ow x oy0..oy1) de parede com face externa em z=0: caixilho, 2 folhas, peitoril, avental, guarnicao e verga."""
    x = ow / 2; f = 0.05
    p.box('frame', -x, -x + f, oy0, oy1, -0.2, -0.04); p.box('frame', x - f, x, oy0, oy1, -0.2, -0.04)     # caixilho (batentes)
    p.box('frame', -x, x, oy1 - f, oy1, -0.2, -0.04)
    p.box('frame', -x + f, -x + f + 0.012, oy0 + 0.02, oy1 - f, -0.105, -0.095); p.box('frame', x - f - 0.012, x - f, oy0 + 0.02, oy1 - f, -0.105, -0.095)  # batente entre folhas
    mid = oy0 + 0.02 + (oy1 - f - oy0 - 0.02) * 0.5
    sash(p, -x + f, x - f, oy0 + 0.025, mid + 0.02, -0.15, -0.11, 1, 0.075)               # folha de baixo (por dentro)
    sash(p, -x + f + 0.012, x - f - 0.012, mid - 0.02, oy1 - f, -0.09, -0.05, lites, 0.05)  # folha de cima (por fora), com baguetes
    st = oy0 + 0.015   # peitoril sempre acima do piso do vao
    prof_x(p, 'trim', -x + f, x - f, [(-0.2, st - 0.03), (-0.04, st - 0.03), (-0.04, st), (-0.2, st)])           # base interna do peitoril
    prof_x(p, 'trim', -x - 0.13, x + 0.13, [(-0.04, st - 0.03), (0.07, st - 0.05), (0.082, st - 0.058), (0.082, st - 0.078),
                                           (0.07, st - 0.082), (0.055, st - 0.068), (0.0, st - 0.06), (0.0, st - 0.03)] if False else
           [(-0.0, st - 0.075), (0.06, st - 0.075), (0.075, st - 0.068), (0.082, st - 0.055), (0.07, st - 0.04), (0.0, st - 0.015)])  # nariz com pingadeira
    p.box('trim', -x + f, x - f, st - 0.03, st, -0.04, 0.0)
    prof_x(p, 'trim', -x - 0.06, x + 0.06, [(0.0, st - 0.2), (0.03, st - 0.2), (0.036, st - 0.19), (0.036, st - 0.075), (0.0, st - 0.075)])  # avental
    for s in (-1, 1):   # guarnicoes laterais (tabua lisa larga com quina chanfrada)
        a, b = sorted((s * x, s * (x + 0.11)))
        prof_y(p, 'trim', st - 0.04, oy1 + 0.025, crect(a, b, 0.0, 0.036, 0.006, (0, 0, 1, 1)))
    prof_x(p, 'trim', -x - 0.13, x + 0.13, crect(0.0, 0.04, oy1 + 0.025, oy1 + 0.2, 0.006, (0, 1, 1, 0)))           # verga larga
    prof_x(p, 'trim', -x - 0.16, x + 0.16, [(0.0, oy1 + 0.2), (0.07, oy1 + 0.2), (0.07, oy1 + 0.225), (0.05, oy1 + 0.245), (0.0, oy1 + 0.255)])  # capa com pingadeira
    return (-x - 0.03, x + 0.03, oy0, oy1 + 0.05)   # buraco nas tabuas (coberto pela guarnicao)

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
def sheared_courses(p, poly, f, d_of, strip_of, dmax, uvf):
    """Telhas em fiadas: poly no plano (a, b); f(a, b) = altura da face de baixo do telhado; d_of(a, b) = distancia do beiral;
    strip_of(d0, d1) = poligono da faixa entre d0 e d1. Cada fiada e uma placa cujo topo desce em cunha ate a fiada de cima."""
    k = 0
    while k * SHX < dmax:
        d0, d1 = k * SHX, (k + 1) * SHX
        band = poly.intersection(strip_of(d0, d1)); k += 1
        for g in getattr(band, 'geoms', [band]):
            if g.geom_type != 'Polygon' or g.area < 1e-6: continue
            m = trimesh.creation.extrude_polygon(g, 1.0); v = m.vertices.copy(); a, b, t = v[:, 0], v[:, 1], v[:, 2]
            d = d_of(a, b); top = TV + BUMP * (1 - np.clip((d - d0) / SHX, 0, 1))
            m.vertices = np.stack([a, f(a, b) + 0.02 + t * (top - 0.02), b], 1); m.invert(); p.add('shingles', _fix(m))
    p.uv['shingles'] = uvf
def sheared(p, mat, poly, t0, t1, f):
    for g in getattr(poly, 'geoms', [poly]):
        if g.geom_type != 'Polygon' or g.area < 1e-6: continue
        m = trimesh.creation.extrude_polygon(g, t1 - t0); v = m.vertices.copy(); a, b, c = v[:, 0].copy(), v[:, 1].copy(), v[:, 2] + t0
        m.vertices = np.stack([a, f(a, b) + c, b], 1); m.invert(); p.add(mat, _fix(m))
def gutter_profile(z0, ytop):
    """Calha K (ogee simplificada), parede de 1 cm, encostada na testeira em z0; topo em ytop."""
    z1 = z0 + 0.13; y0 = ytop - 0.12; t = 0.01
    return [(z0, ytop), (z0, y0), (z1 - 0.035, y0), (z1 - 0.01, y0 + 0.03), (z1, y0 + 0.07), (z1, ytop), (z1 - 0.025, ytop),
            (z1 - 0.025, ytop - 0.012), (z1 - t, ytop - 0.012), (z1 - t, y0 + 0.072), (z1 - 0.02, y0 + 0.036), (z1 - 0.04, y0 + t), (z0 + t, y0 + t), (z0 + t, ytop)]
def gutter_run(p, x0, x1, z0, ytop, mitre=(), caps=(False, False)):
    """Calha de x0 a x1 (eixo X da peca). mitre = cantos (xc, lado) cortados a 45 graus no canto externo do beiral (xc, z0-0.03).
    caps = tampas nas pontas (x0, x1) onde a calha termina sem canto."""
    g = Piece(); prof_x(g, 'gutter', x0, x1, gutter_profile(z0, ytop)); m = g.parts['gutter'][0]
    for (xc, s) in mitre:   # lado s=+1: corta onde (x - xc) > (z - zc)
        zc = z0 - 0.03; m = slice_keep(m, [xc, 0, zc], [-s / math.sqrt(2), 0, 1 / math.sqrt(2)])
    p.add('gutter', m)
    pr = gutter_profile(z0, ytop); fill = Polygon(pr[:6]).convex_hull.exterior.coords[:-1]
    for xe, on, d in ((x0, caps[0], 1), (x1, caps[1], -1)):
        if on: prof_x(p, 'gutter', *sorted((xe, xe + d * 0.008)), [(z + 0.001, y) for z, y in fill] if False else list(fill))
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
def downspout(drop, gz):
    """Condutor: bocal na calha (a gz da parede, topo a 'drop' do chao), cotovelo ate a parede, descida com abracadeiras,
    cotovelo de saida e bloco de respingo. Pivo: face da parede no chao, condutor para +Z."""
    p = Piece(); a, b = 0.035, 0.045; zw = 0.1
    y_top = drop - 0.1
    p.box('gutter', -a, a, y_top - 0.06, y_top + 0.02, gz - b, gz + b)
    p.seg('gutter', (0, y_top - 0.04, gz), (0, y_top - 0.04 - (gz - zw) * 0.9, zw), 2 * a, 2 * b)
    yv = y_top - 0.04 - (gz - zw) * 0.9
    p.box('gutter', -a, a, 0.32, yv + 0.04, zw - b, zw + b)
    p.seg('gutter', (0, 0.36, zw), (0, 0.14, zw + 0.22), 2 * a, 2 * b)
    p.box('gutter', -a - 0.004, a + 0.004, 0.08, 0.16, zw + 0.18, zw + 0.34)
    for yy in np.arange(0.8, yv - 0.2, 1.2):
        p.box('gutter', -a - 0.006, a + 0.006, yy, yy + 0.03, zw - b - 0.006, zw + b + 0.006); p.box('gutter', -0.012, 0.012, yy, yy + 0.03, 0.0, zw - b)
    p.hull('concrete', [(x, y, z) for x in (-0.16, 0.16) for (z, y) in ((zw + 0.1, 0.0), (zw + 0.1, 0.06), (zw + 0.65, 0.0), (zw + 0.65, 0.03))])
    return p

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
def porch_lantern():
    """Lanterna pendente: canopla no forro, corrente, gaiola de ferro com vidro aceso e chapeu piramidal. Pivo: ponto no forro."""
    p = Piece()
    p.cyl('iron', 0.07, -0.03, 0.0, sec=12)
    for i in range(6): p.cham('iron', -0.008, 0.008, -0.08 - i * 0.06, -0.035 - i * 0.06, -0.008, 0.008, 0.003)
    yb = -0.75; yt = -0.42
    p.hull('iron', [(sx * 0.13, yt, sz * 0.13) for sx in (-1, 1) for sz in (-1, 1)] + [(0, yt + 0.12, 0)])
    p.box('iron', -0.11, 0.11, yt - 0.02, yt, -0.11, 0.11); p.box('iron', -0.1, 0.1, yb, yb + 0.03, -0.1, 0.1)
    p.box('lamp_glass', -0.085, 0.085, yb + 0.03, yt - 0.02, -0.085, 0.085)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('iron', sx * 0.1 - 0.012, sx * 0.1 + 0.012, yb, yt, sz * 0.1 - 0.012, sz * 0.1 + 0.012)
    p.sphere('iron', 0.025, 0, yb - 0.02, 0)
    return p
def wall_lantern():
    """Arandela de parede ao lado da porta. Pivo: face da parede, centro da base de fixacao."""
    p = Piece(); p.cham('iron', -0.06, 0.06, -0.1, 0.1, 0.0, 0.025, 0.006)
    p.box('iron', -0.015, 0.015, -0.02, 0.02, 0.025, 0.11)
    yb, yt = -0.12, 0.14; zc = 0.17
    p.box('iron', -0.08, 0.08, yb, yb + 0.025, zc - 0.08, zc + 0.08)
    p.box('lamp_glass', -0.065, 0.065, yb + 0.025, yt, zc - 0.065, zc + 0.065)
    for sx in (-1, 1):
        for sz in (-1, 1): p.box('iron', sx * 0.07 - 0.01, sx * 0.07 + 0.01, yb, yt, zc + sz * 0.07 - 0.01, zc + sz * 0.07 + 0.01)
    p.hull('iron', [(sx * 0.1, yt, zc + sz * 0.1) for sx in (-1, 1) for sz in (-1, 1)] + [(0, yt + 0.1, zc)])
    return p

# ============================================================================ portas (Blender: almofadas rebaixadas + bevel)
def door_front(w=0.94, h=2.26, t=0.045):
    """Porta craftsman: 3 vidros escalonados no alto, prateleira com denticulos, 2 almofadas verticais. Pivo: dobradica, embaixo."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2); cut = []
    lites = [(0.12, 0.33, 1.62, 2.1), (0.37, 0.57, 1.62, 2.14), (0.61, 0.82, 1.62, 2.1)]
    for (a, b, c, d) in lites: cut.append(tbox(a, b, c, d, -t, t))
    for (a, b) in ((0.12, 0.45), (0.49, 0.82)):
        for z in (t / 2, -t / 2): cut.append(tbox(a, b, 0.22, 1.36, z - 0.01, z + 0.01))
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    for (a, b, c, d) in lites:
        p.box('glass', a - 0.004, b + 0.004, c - 0.004, d + 0.004, -0.004, 0.004)
    p.add('door', bl_detail(tbox(0.06, w - 0.06, 1.44, 1.49, -t / 2 - 0.035, t / 2 + 0.035), bevel=0.006, segments=2))   # prateleira
    for i in range(9):
        xx = 0.1 + i * (w - 0.2) / 8; p.box('door', xx - 0.018, xx + 0.018, 1.4, 1.44, t / 2, t / 2 + 0.02); p.box('door', xx - 0.018, xx + 0.018, 1.4, 1.44, -t / 2 - 0.02, -t / 2)
    for z in (1, -1):   # macaneta e espelho
        p.cham('brass', w - 0.11, w - 0.06, 0.88, 1.1, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.sphere('brass', 0.03, w - 0.085, 1.0, z * (t / 2 + 0.05)); p.cyl('brass', 0.008, 0.99, 1.01, w - 0.085, z * (t / 2 + 0.025)) if False else None
        p.seg('brass', (w - 0.085, 1.0, z * t / 2), (w - 0.085, 1.0, z * (t / 2 + 0.04)), 0.016)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)   # dobradicas (pinos)
    return p
def door_back(w=0.94, h=2.26, t=0.045):
    """Porta dos fundos: meio vidro com cruzeta, 2 almofadas embaixo."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2)
    cut = [tbox(0.14, w - 0.14, 1.25, 2.1, -t, t)] + [tbox(0.14, w - 0.14, y0, y1, z - 0.01, z + 0.01) for (y0, y1) in ((0.18, 0.62), (0.72, 1.12)) for z in (t / 2, -t / 2)]
    p.add('door', bl_detail(slab, cut, bevel=0.005, segments=2))
    p.box('glass', 0.136, w - 0.136, 1.246, 2.104, -0.004, 0.004)
    p.cham('door', w / 2 - 0.015, w / 2 + 0.015, 1.25, 2.1, -0.014, 0.014, 0.004); p.cham('door', 0.14, w - 0.14, 1.66, 1.69, -0.014, 0.014, 0.004)
    for z in (1, -1):
        p.cham('brass', w - 0.11, w - 0.06, 0.88, 1.1, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.sphere('brass', 0.03, w - 0.085, 1.0, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.085, 1.0, z * t / 2), (w - 0.085, 1.0, z * (t / 2 + 0.04)), 0.016)
    for yy in (0.25, 1.1, 1.95): p.cyl('brass', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
    return p
def door_interior(w=0.86, h=2.08, t=0.04):
    """Porta interna de 5 almofadas horizontais (estilo shaker)."""
    p = Piece(); slab = tbox(0, w, 0, h, -t / 2, t / 2); cut = []
    for i in range(5):
        y0 = 0.14 + i * (h - 0.28) / 5 + 0.03; y1 = 0.14 + (i + 1) * (h - 0.28) / 5 - 0.03
        for z in (t / 2, -t / 2): cut.append(tbox(0.13, w - 0.13, y0, y1, z - 0.009, z + 0.009))
    p.add('door_int', bl_detail(slab, cut, bevel=0.004, segments=2))
    for z in (1, -1):
        p.sphere('brass', 0.028, w - 0.08, 1.0, z * (t / 2 + 0.05)); p.seg('brass', (w - 0.08, 1.0, z * t / 2), (w - 0.08, 1.0, z * (t / 2 + 0.04)), 0.014)
        p.cyl('brass', 0.03, 0.995, 1.005, w - 0.08, z * (t / 2 + 0.004), 12) if False else p.cham('brass', w - 0.11, w - 0.05, 0.97, 1.03, z * t / 2 - 0.004 * (z < 0), z * t / 2 + 0.004 * (z > 0), 0.003)
    for yy in (0.25, 1.75): p.cyl('brass', 0.007, yy, yy + 0.09, 0.0, t / 2 + 0.002, 8)
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
BASE_PROF = lambda t: [(t / 2, 0.0), (t / 2 + 0.016, 0.0), (t / 2 + 0.016, 0.1), (t / 2 + 0.008, 0.115), (t / 2, 0.118)]
def baseboard(p, a, b, t):
    prof_x(p, 'trim', a, b, BASE_PROF(t)); prof_x(p, 'trim', a, b, [(-z, y) for (z, y) in BASE_PROF(t)][::-1])
def door_casing(p, ow, t, oh=2.1):
    """Batente e guarnicoes de porta interna: guarnicao de 7 cm com quina chanfrada dos dois lados, verga com capa."""
    for xx in (-ow / 2, ow / 2):
        a, b = sorted((xx, xx - 0.03 * np.sign(xx)))
        p.box('frame', a, b, 0, oh, -t / 2 - 0.002, t / 2 + 0.002)
    p.box('frame', -ow / 2, ow / 2, oh - 0.03, oh, -t / 2 - 0.002, t / 2 + 0.002)
    for z in (1, -1):
        z0, z1 = sorted((z * t / 2, z * (t / 2 + 0.02)))
        for s in (-1, 1):
            a, b = sorted((s * ow / 2, s * (ow / 2 + 0.08)))
            prof_y(p, 'frame', 0, oh + 0.02, crect(a, b, z0, z1, 0.005, (0, 0, 1, 1) if z > 0 else (1, 1, 0, 0)))
        prof_x(p, 'frame', -ow / 2 - 0.09, ow / 2 + 0.09, crect(z0, z1, oh + 0.02, oh + 0.13, 0.005, (0, 1, 1, 0) if z > 0 else (1, 0, 0, 1)))
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

def glb_jpeg(path, q=88):
    """Troca as imagens PNG embutidas no GLB por JPEG (cor e ORM q88, normal q92): arquivos ~4x menores."""
    data = open(path, 'rb').read(); _, _, _ = struct.unpack('<III', data[:12]); off = 12; chunks = []
    while off < len(data):
        ln, ty = struct.unpack('<II', data[off:off + 8]); chunks.append((ty, data[off + 8:off + 8 + ln])); off += 8 + ln
    js = json.loads(chunks[0][1]); binb = chunks[1][1] if len(chunks) > 1 else b''
    if not js.get('images'): return
    normals = {js['materials'][i]['normalTexture']['index'] for i in range(len(js.get('materials', []))) if 'normalTexture' in js['materials'][i]}
    norm_imgs = {js['textures'][t]['source'] for t in normals}
    views = js['bufferViews']; blobs = []
    for i, v in enumerate(views): blobs.append(binb[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']])
    for ii, im in enumerate(js['images']):
        bv = im['bufferView']; pim = Image.open(io.BytesIO(blobs[bv])).convert('RGB'); bio = io.BytesIO()
        pim.save(bio, 'JPEG', quality=92 if ii in norm_imgs else q, optimize=True); blobs[bv] = bio.getvalue(); im['mimeType'] = 'image/jpeg'
    out = b''
    for i, v in enumerate(views):
        v['byteOffset'] = len(out); v['byteLength'] = len(blobs[i]); out += blobs[i] + b'\0' * ((-len(blobs[i])) % 4)
    js['buffers'] = [{'byteLength': len(out)}]
    j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((-len(j)) % 4)
    res = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(out)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(out), 0x004E4942) + out
    open(path, 'wb').write(res)

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
