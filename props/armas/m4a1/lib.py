"""Primitivas de modelagem (Blender/bpy) para a M4A1.

Coordenadas de projeto em milímetros: u = para a frente (boca do cano),
v = para cima, w = para a direita da arma. Eixo do cano em v = 0, w = 0;
u = 0 na face da frente do receptor superior.
No Blender: x = w, y = u, z = v (o exportador glTF vira Y para cima, cano em -Z).
"""
import math
import bpy
import bmesh
from mathutils import Vector

MM = 0.001


def P(u, v, w=0.0):
    return Vector((w * MM, u * MM, v * MM))


_MATS = {}


def M(nome):
    if nome not in _MATS:
        m = bpy.data.materials.new(nome)
        m.use_nodes = True
        _MATS[nome] = m
    return _MATS[nome]


def _obj(nome, bm, mat):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nome, me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(M(mat))
    return o


def _mk(plane, p, t):
    if plane == 'uv':
        return P(p[0], p[1], t)
    if plane == 'uw':
        return P(p[0], t, p[1])
    return P(t, p[1], p[0])          # 'wv': pontos (w, v), extrusão em u


def extr(pts, a, b, mat, plane='uv'):
    """Polígono 2D extrudado de a até b no terceiro eixo."""
    bm = bmesh.new()
    va = [bm.verts.new(_mk(plane, p, a)) for p in pts]
    vb = [bm.verts.new(_mk(plane, p, b)) for p in pts]
    bm.faces.new(va)
    bm.faces.new(vb[::-1])
    n = len(pts)
    for i in range(n):
        bm.faces.new((va[i], vb[i], vb[(i + 1) % n], va[(i + 1) % n]))
    return _obj('e', bm, mat)


def box(u0, u1, v0, v1, w0, w1, mat):
    return extr([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], w0, w1, mat)


def _frame(a):
    a = a.normalized()
    h = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    x = a.cross(h).normalized()
    y = a.cross(x).normalized()
    return x, y


def cyl(c0, c1, r, mat, n=24, r1=None, lobes=0.0):
    """Cilindro/cone entre dois pontos de projeto (u, v, w). lobes>0: serrilhado."""
    a, b = P(*c0), P(*c1)
    x, y = _frame(b - a)
    r1 = r if r1 is None else r1
    bm = bmesh.new()
    ra, rb = [], []
    for i in range(n):
        t = 2 * math.pi * i / n
        k = (1 - lobes) if (lobes and i % 2) else 1.0
        d = x * math.cos(t) + y * math.sin(t)
        ra.append(bm.verts.new(a + d * r * k * MM))
        rb.append(bm.verts.new(b + d * r1 * k * MM))
    bm.faces.new(ra)
    bm.faces.new(rb[::-1])
    for i in range(n):
        bm.faces.new((ra[i], rb[i], rb[(i + 1) % n], ra[(i + 1) % n]))
    return _obj('c', bm, mat)


def pin(u, v, r, w0, w1, mat, n=16, lobes=0.0):
    return cyl((u, v, w0), (u, v, w1), r, mat, n=n, lobes=lobes)


def lathe(prof, mat, n=32, c0=(0, 0, 0), eixo=(1, 0, 0), lobes=0.0, lobe_min=0.0, anel=False):
    """Revolução: prof = [(t, r)] ao longo do eixo a partir de c0."""
    o = P(*c0)
    ax = P(*eixo).normalized()
    x, y = _frame(ax)
    bm = bmesh.new()
    rings = []
    for (t, r) in prof:
        c = o + ax * t * MM
        if r < 1e-6:
            rings.append([bm.verts.new(c)])
        else:
            ring = []
            for i in range(n):
                a = 2 * math.pi * i / n
                k = (1 - lobes) if (lobes and i % 2 and r >= lobe_min) else 1.0
                ring.append(bm.verts.new(c + (x * math.cos(a) + y * math.sin(a)) * r * k * MM))
            rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            if len(ra) == 1 and len(rb) == 1:
                continue
            if len(ra) == 1:
                bm.faces.new((ra[0], rb[i], rb[j]))
            elif len(rb) == 1:
                bm.faces.new((ra[i], rb[0], ra[j]))
            else:
                bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
    if anel:
        ra, rb = rings[-1], rings[0]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
    else:
        if len(rings[0]) > 1:
            bm.faces.new(rings[0])
        if len(rings[-1]) > 1:
            bm.faces.new(rings[-1][::-1])
    return _obj('l', bm, mat)


def loft(rings, mat, cap=True):
    """rings: listas de Vector (coordenadas Blender), mesmo número de pontos."""
    bm = bmesh.new()
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    for ra, rb in zip(vr, vr[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
    if cap:
        bm.faces.new(vr[0])
        bm.faces.new(vr[-1][::-1])
    return _obj('f', bm, mat)


def superelipse(rx, ry, n=28, e=2.6, cx=0.0, cy=0.0):
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        out.append((cx + rx * math.copysign(abs(c) ** (2 / e), c),
                    cy + ry * math.copysign(abs(s) ** (2 / e), s)))
    return out


def ret_arred(x0, x1, y0, y1, r, n=4):
    """Retângulo de cantos arredondados (lista de pontos 2D, anti-horário)."""
    out = []
    for (cx, cy, a0) in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90),
                         (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def arco(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _ativo(o, outros=()):
    return bpy.context.temp_override(active_object=o, object=o,
                                     selected_objects=[o, *outros],
                                     selected_editable_objects=[o, *outros])


def join(objs, nome='j'):
    objs = [o for o in objs if o is not None]
    o = objs[0]
    if len(objs) > 1:
        with _ativo(o, objs[1:]):
            bpy.ops.object.join()
    o.name = nome
    return o


def cut(o, cortes, op='DIFFERENCE'):
    cortes = list(cortes) if isinstance(cortes, (list, tuple)) else [cortes]
    col = bpy.data.collections.new('cortes')
    for c in cortes:
        for uc in list(c.users_collection):
            uc.objects.unlink(c)
        col.objects.link(c)
    m = o.modifiers.new('b', 'BOOLEAN')
    m.operation = op
    m.solver = 'EXACT'
    m.operand_type = 'COLLECTION'
    m.collection = col
    n0 = len(o.data.polygons)
    with _ativo(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    if len(o.data.polygons) < 4:
        raise RuntimeError(f'corte destruiu a peça ({n0} faces)')
    for c in cortes:
        bpy.data.objects.remove(c)
    bpy.data.collections.remove(col)
    return o


def bevel(o, w, seg=2, ang=30):
    m = o.modifiers.new('bv', 'BEVEL')
    m.width = w * MM
    m.segments = seg
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(ang)
    m.harden_normals = False
    with _ativo(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def fio(pts, r, mat, fechado=True, res=3):
    """Arame redondo ao longo de pontos de projeto (u, v, w)."""
    cu = bpy.data.curves.new('fio', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r * MM
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (*P(*q), 1.0)
    sp.use_cyclic_u = fechado
    tmp = bpy.data.objects.new('fio', cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    o = bpy.data.objects.new('fio', me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.clear()
    me.materials.append(M(mat))
    return o


def caminho_arred(pts, r, n=5, fechado=True):
    """Arredonda os cantos de uma poligonal 3D (pontos de projeto)."""
    V = [Vector(p) for p in pts]
    out = []
    m = len(V)
    for i in range(m):
        if not fechado and i in (0, m - 1):
            out.append(tuple(V[i]))
            continue
        a, b, c = V[i - 1], V[i], V[(i + 1) % m]
        d0 = (a - b).normalized()
        d1 = (c - b).normalized()
        p0, p1 = b + d0 * r, b + d1 * r
        for k in range(n + 1):
            t = k / n
            q = p0.lerp(b, t).lerp(b.lerp(p1, t), t)
            out.append(tuple(q))
    return out


def texto(s, tam, u, v, w, mat='tinta', lado=-1, alinhar='CENTER'):
    """Gravação plana no lado esquerdo (lado=-1) ou direito (+1) da arma."""
    cu = bpy.data.curves.new('t', 'FONT')
    cu.body = s
    cu.size = tam * MM
    cu.align_x = alinhar
    cu.resolution_u = 2
    tmp = bpy.data.objects.new('t', cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    for vv in me.vertices:
        x, y = vv.co.x, vv.co.y
        vv.co = P(u + lado * x / MM, v + y / MM, w)
    o = bpy.data.objects.new('t', me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.clear()
    me.materials.append(M(mat))
    return o


def pintar(o, mat, teste):
    """Troca o material das faces em que teste(centro_mm(u,v,w), normal(u,v,w)) é verdadeiro."""
    me = o.data
    me.materials.append(M(mat))
    idx = len(me.materials) - 1
    for p in me.polygons:
        c = p.center / MM
        n = p.normal
        if teste((c.y, c.z, c.x), (n.y, n.z, n.x)):
            p.material_index = idx
    return o


PARTES = []


def parte(nome, objs, origem=None, pai=None, grupo='A', suave=32):
    o = join(objs if isinstance(objs, (list, tuple)) else [objs], nome)
    me = o.data
    me.name = nome
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(suave))
    if origem is None:
        cs = [o.matrix_world @ v.co for v in me.vertices]
        mn = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
        mx = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
        org = (mn + mx) / 2
    else:
        org = P(*origem)
    for v in me.vertices:
        v.co -= org
    o.location = org
    o['grupo'] = grupo
    if pai is not None:
        bpy.context.view_layer.update()
        o.parent = pai
        o.matrix_parent_inverse = pai.matrix_world.inverted()
    PARTES.append(o)
    return o
