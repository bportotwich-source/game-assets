"""Biblioteca comum de ALTO DETALHE para os kits (nasceu do kit piloto kits/bangalo-detalhado).

Uso num gerar_kit.py:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe'))
    from detalhe import *
    configurar(cores={'siding': (118, 146, 104), ...}, texturas={'siding': 'siding', 'brick': 'brick', ...})

O que tem:
  materiais   configurar(cores, texturas): cores lisas + texturas PBR (cor + normal + ORM) do scripts/texturas/gerar_texturas.py,
              ladrilho de 2 m, UV em metros / 2 (projecao em caixa), metalicos e vidro com brilho, lamp_glass com emissao.
  Piece       box, cham (caixa chanfrada), cyl, sphere, hull, seg, merge, scene(nome) -> trimesh.Scene pronta para GLB.
  perfis      prof_x / prof_y / prof_z (perfil 2D extrudado, pontas retas: modulos vizinhos encostam sem emenda), crect, arc.
  paredes     grid_solid, wall_with_opening (malha estanque sem juncao em T; a camada interna para 5 mm abaixo do topo).
  tabuas      configurar_tabuas(base, topo, expo), board, siding_field (tabuas sobrepostas em geometria, com buracos).
  janelas     sash, window (guilhotina 2 folhas, peitoril com pingadeira, avental, guarnicao, verga com capa).
  telhado     configurar_telhado(tv, bump, graus), sheared, sheared_courses (fiadas de telha com degrau), gutter_profile,
              gutter_run (calha K com meia-esquadria e tampas), downspout (condutor com cotovelos).
  portas      door_front, door_back, door_interior (almofadas via Blender: bl_detail = booleano EXACT + bevel), tbox.
  interior    baseboard, door_casing.
  luz         porch_lantern, wall_lantern.
  arquivo     glb_jpeg(caminho): troca PNG embutido por JPEG (~4x menor).
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
"""
import numpy as np, trimesh, json, os, math, sys, io, struct
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
from PIL import Image
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'texturas'))
import gerar_texturas as GT

W = 2.0; T = 0.3          # modulo e parede externa do padrao
PX_M = 192; TILE = 2.0    # pixels por metro e tamanho do ladrilho das texturas

COL = {'trim': (240, 234, 218), 'frame': (240, 234, 218), 'sash': (250, 246, 236), 'door': (138, 54, 42), 'door_int': (236, 228, 210),
       'iron': (40, 40, 44), 'brass': (196, 160, 84), 'glass': (150, 186, 204), 'gutter': (92, 76, 62), 'dark': (36, 34, 34),
       'plaster': (238, 230, 214), 'tile': (214, 224, 228), 'lamp_glass': (255, 214, 140), 'concrete': (176, 172, 164),
       'player': (90, 140, 220), 'clay': (172, 96, 62), 'cap': (196, 190, 178), 'ridge': (58, 60, 66)}
METAL = {'iron', 'brass', 'gutter', 'steel', 'metal', 'zinc', 'copper'}
MATTE = {'ridge', 'concrete', 'dark', 'clay'}
MATS = {}; TEX = {}; KIND = {}

def _texdef(kind, col, seed):
    """Tipos de textura: siding, brick, stone, stone2, shingles, roof_tiles, plaster, render, planks, deck, paint (madeira pintada lisa)."""
    C = dict(GT.CORES)
    if kind == 'siding': r = GT.siding('detalhado', PX_M, (TILE, TILE), col, seed); return (r[0], r[1], r[2] + 0.25, r[3], r[4])
    if kind == 'brick':
        pal = C['brick'] if col is None else [tuple(int(max(0, min(255, c * f))) for c in col) for f in (1.0, 0.93, 1.06, 0.88, 1.1, 0.9)]
        return GT.masonry('detalhado', PX_M, (TILE, TILE), [0.125] * 16, GT.running(2, 16, 0.25), 0.012, pal, C['brick_mortar'], seed, 0.008, irregular=0.0015)
    if kind == 'stone':
        pal = C['stone'] if col is None else [tuple(int(max(0, min(255, c * f))) for c in col) for f in (1.0, 0.95, 1.04, 0.97)]
        return GT.masonry('detalhado', PX_M, (TILE, 1.6), [0.4] * 4, GT.running(2, 4, 1.0), 0.014, pal, C['stone_mortar'], seed, 0.012)
    if kind == 'stone2':
        pal = C['stone2'] if col is None else [tuple(int(max(0, min(255, c * f))) for c in col) for f in (1.0, 0.93, 1.04, 0.9)]
        return GT.masonry('detalhado', PX_M, (TILE, 1.2), [0.2] * 6, GT.random_cuts(2, 6, 0.35, 0.7, 31), 0.016, pal, C['stone2_mortar'], seed, 0.02, irregular=0.006, recess=0.014)
    if kind == 'shingles': return GT.shingles('detalhado', PX_M, (TILE, TILE), col or C['shingles'], seed)
    if kind == 'roof_tiles': return GT.clay_tiles('detalhado', PX_M, (TILE, TILE), col or C['roof_tiles'], seed)
    if kind in ('plaster', 'render'): return GT.stucco('detalhado', PX_M, (TILE, TILE), col or C[kind], seed, coarse=0.6 if kind == 'plaster' else 1.0)
    if kind == 'planks': return planks(PX_M, (TILE, TILE), col, seed)
    if kind == 'deck': return planks(PX_M, (TILE, TILE), col, seed, w=0.2)
    if kind == 'paint': return wood_paint(PX_M, (TILE, TILE), col, seed)
    raise ValueError(kind)

def configurar(cores=None, texturas=None, out=None):
    """cores: {material: (r,g,b)} somadas as padrao. texturas: {material: tipo} (veja _texdef). out: pasta para salvar os PNG.
    Os nomes dos materiais continuam livres (brick, siding, stone...), para trocar as cores depois na engine."""
    COL.update(cores or {}); MATS.clear(); TEX.clear(); KIND.clear(); KIND.update(texturas or {})
    for k, v in COL.items():
        m = PBRMaterial(name=k, baseColorFactor=[c / 255 for c in v] + [1.0], metallicFactor=0.0, roughnessFactor=0.6)
        if k in METAL: m.metallicFactor = 0.6; m.roughnessFactor = 0.45
        if k in MATTE: m.roughnessFactor = 0.9
        MATS[k] = m
    MATS['glass'].roughnessFactor = 0.08; MATS['glass'].metallicFactor = 0.2
    MATS['lamp_glass'] = PBRMaterial(name='lamp_glass', baseColorFactor=[1, 0.86, 0.6, 1], emissiveFactor=[1.0, 0.72, 0.36], metallicFactor=0, roughnessFactor=0.3)
    for i, (k, kind) in enumerate((texturas or {}).items()):
        a, n, o = tex_set(*_texdef(kind, COL.get(k), 7 + 11 * i), PX_M); TEX[k] = (a, n, o)
        if out: a.save(f'{out}/{k}_albedo.png'); n.save(f'{out}/{k}_normal.png'); o.save(f'{out}/{k}_orm.png')
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=n, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)
    for k in COL:
        if k not in MATS: MATS[k] = PBRMaterial(name=k, baseColorFactor=[c / 255 for c in COL[k]] + [1.0])
    return MATS

# tabuas sobrepostas: fiadas de EXPO a partir de WT; a fase casa com a textura 'siding' (sombra a cada 0,2 m a partir de WT)
WT = 0.12; NC = 13; EXPO = 0.2; LAP = 0.03; TB = 0.024; TT = 0.007
def configurar_tabuas(base=0.12, topo=2.72, expo=0.2):
    """Tabuas de 'base' a 'topo' (m, na peca). Use expo = 0,2 m (divide o ladrilho de 2 m) e (topo - base) multiplo de expo."""
    global WT, NC, EXPO
    WT = base; EXPO = expo; NC = int(round((topo - base) / expo))

# telhado: espessura TV, degrau BUMP, fiada de 0,2 m medida na agua
TV = 0.08; BUMP = 0.022; SHX = 0.2 * math.cos(math.radians(30))
def configurar_telhado(tv=0.08, bump=0.022, graus=30):
    global TV, BUMP, SHX
    TV = tv; BUMP = bump; SHX = 0.2 * math.cos(math.radians(graus))

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
                    if KIND.get(k) == 'siding': uv[ax == 1] = 0.37
                    if KIND.get(k) == 'siding': uv[ax != 1, 1] = (v[ax != 1, 1] - WT) / TILE   # fase: a borda de baixo de cada tabua cai na sombra pintada   # tetos e topos de parede: cor lisa (sobreposicoes iguais)
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

def board(p, x0, x1, k, ya=None, yb=None, mat='siding'):
    """Cunha da fiada k entre ya e yb (padrao: a tabua inteira). A face da frente e inclinada: a borda de baixo faz sombra."""
    b0 = WT + k * EXPO; b1 = b0 + EXPO + (LAP if k < NC - 1 else 0.0)
    ya = b0 if ya is None else max(ya, b0); yb = b1 if yb is None else min(yb, b1)
    if yb - ya < 1e-4 or x1 - x0 < 1e-4: return
    th = lambda y: TB - (TB - TT) * (y - b0) / (b1 - b0)
    p.hull(mat, [(x, y, z) for x in (x0, x1) for y in (ya, yb) for z in (0.0, th(y))])
def siding_field(p, holes=(), x0=-W / 2 + 0.0012, x1=W / 2 - 0.0012, mat="siding"):
    """Preenche o modulo com tabuas, deixando buracos [(hx0, hx1, hy0, hy1)] para janelas/portas (cobertos pelas guarnicoes)."""
    for k in range(NC):
        b0 = WT + k * EXPO; b1 = b0 + EXPO + LAP
        cuts = sorted(set([b0, b1] + [y for h in holes for y in (h[2], h[3]) if b0 < y < b1]))
        for ya, yb in zip(cuts[:-1], cuts[1:]):
            xs = [(x0, x1)]
            for (hx0, hx1, hy0, hy1) in holes:
                if ya >= hy0 - 1e-9 and yb <= hy1 + 1e-9:
                    xs = [s for a, b in xs for s in ((a, min(b, hx0)), (max(a, hx1), b)) if s[1] - s[0] > 1e-4]
            for a, b in xs: board(p, a, b, k, ya, yb, mat)


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
        bv = im['bufferView']; pim = Image.open(io.BytesIO(blobs[bv]))
        if pim.mode in ('RGBA', 'LA') and pim.getchannel('A').getextrema()[0] < 255: continue   # decalque com transparencia: fica PNG
        pim = pim.convert('RGB'); bio = io.BytesIO()
        pim.save(bio, 'JPEG', quality=92 if ii in norm_imgs else q, optimize=True); blobs[bv] = bio.getvalue(); im['mimeType'] = 'image/jpeg'
    out = b''
    for i, v in enumerate(views):
        v['byteOffset'] = len(out); v['byteLength'] = len(blobs[i]); out += blobs[i] + b'\0' * ((-len(blobs[i])) % 4)
    js['buffers'] = [{'byteLength': len(out)}]
    j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((-len(j)) % 4)
    res = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(out)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(out), 0x004E4942) + out
    open(path, 'wb').write(res)


__all__ = [n for n in list(globals()) if not n.startswith('__') and n not in ('np', 'trimesh', 'json', 'os', 'math', 'sys', 'io', 'struct')] + ['np', 'trimesh', 'json', 'math', 'os', 'sys']
