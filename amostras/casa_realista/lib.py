"""Primitivas de modelagem (Blender/bpy) da amostra de casa realista.

Coordenadas de projeto em metros, as mesmas do pacote: x = direita, y = para cima,
z = para fora da fachada. No Blender: (x, -z, y); o exportador glTF devolve Y para cima.
"""
import math, random
import bpy
import bmesh
from mathutils import Vector


def P(x, y, z=0.0):
    return Vector((x, -z, y))


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
    if plane == 'xy':
        return P(p[0], p[1], t)
    if plane == 'xz':
        return P(p[0], t, p[1])
    return P(t, p[1], p[0])          # 'zy': pontos (z, y), extrusão em x


def extr(pts, a, b, mat, plane='xy'):
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


def box(x0, x1, y0, y1, z0, z1, mat):
    return extr([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mat)


def _frame(a):
    a = a.normalized()
    h = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    x = a.cross(h).normalized()
    y = a.cross(x).normalized()
    return x, y


def cyl(c0, c1, r, mat, n=24, r1=None):
    a, b = P(*c0), P(*c1)
    x, y = _frame(b - a)
    r1 = r if r1 is None else r1
    bm = bmesh.new()
    ra, rb = [], []
    for i in range(n):
        t = 2 * math.pi * i / n
        d = x * math.cos(t) + y * math.sin(t)
        ra.append(bm.verts.new(a + d * r))
        rb.append(bm.verts.new(b + d * r1))
    bm.faces.new(ra)
    bm.faces.new(rb[::-1])
    for i in range(n):
        bm.faces.new((ra[i], rb[i], rb[(i + 1) % n], ra[(i + 1) % n]))
    return _obj('c', bm, mat)


def lathe(prof, mat, n=32, c0=(0, 0, 0), eixo=(0, 1, 0), anel=False, lobes=0.0, lobe_min=0.0):
    """Revolução: prof = [(t, r)] ao longo do eixo a partir de c0."""
    o = P(*c0)
    ax = P(*eixo).normalized()
    x, y = _frame(ax)
    bm = bmesh.new()
    rings = []
    for (t, r) in prof:
        c = o + ax * t
        if r < 1e-7:
            rings.append([bm.verts.new(c)])
        else:
            ring = []
            for i in range(n):
                a = 2 * math.pi * i / n
                k = (1 - lobes) if (lobes and i % 2 and r >= lobe_min) else 1.0
                ring.append(bm.verts.new(c + (x * math.cos(a) + y * math.sin(a)) * r * k))
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


def ret_arred(x0, x1, y0, y1, r, n=4):
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
    m.width = w
    m.segments = seg
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(ang)
    m.harden_normals = False
    with _ativo(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def fio(pts, r, mat, fechado=False, res=3):
    """Arame redondo ao longo de pontos de projeto."""
    cu = bpy.data.curves.new('fio', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r
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


def caminho_arred(pts, r, n=5, fechado=False):
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


def texto(s, tam, org, dx=(1, 0, 0), dy=(0, 1, 0), mat='tinta', alinhar='CENTER', raio=None, eixo_c=None):
    """Texto plano: org = ponto de projeto, dx/dy = direções de projeto da escrita.
    raio + eixo_c: enrola em volta de um cilindro vertical de centro eixo_c=(x, z)."""
    cu = bpy.data.curves.new('t', 'FONT')
    cu.body = s
    cu.size = tam
    cu.align_x = alinhar
    cu.resolution_u = 2
    tmp = bpy.data.objects.new('t', cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    if raio:
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if e.calc_length() > tam * 0.25], cuts=2)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
    O, DX, DY = Vector(org), Vector(dx), Vector(dy)
    for vv in me.vertices:
        x, y = vv.co.x, vv.co.y
        if raio:
            a0 = org[0]                      # ângulo central (rad)
            a = a0 + x / raio
            vv.co = P(eixo_c[0] + raio * math.sin(a), org[1] + y, eixo_c[1] + raio * math.cos(a))
        else:
            q = O + DX * x + DY * y
            vv.co = P(*q)
    o = bpy.data.objects.new('t', me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.clear()
    me.materials.append(M(mat))
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    return o


_SEED = [0]


def veio(o, eixo='x', seed=None):
    """Marca a direção do veio da madeira (eixo de projeto) e uma semente por tábua."""
    if isinstance(o, (list, tuple)):
        for q in o:
            veio(q, eixo, seed)
        return o
    me = o.data
    at = me.color_attributes.get('veio') or me.color_attributes.new('veio', 'FLOAT_COLOR', 'POINT')
    if seed is None:
        _SEED[0] += 1
        seed = (_SEED[0] * 0.6180339) % 1.0
    ax = {'x': (1, 0, 0), 'y': (0, 0, 1), 'z': (0, 1, 0)}[eixo]      # em eixos do Blender
    for d in at.data:
        d.color = (*ax, seed)
    return o


def pintar(o, mat, teste):
    """Troca o material das faces em que teste(centro(x,y,z), normal(x,y,z)) é verdadeiro (coordenadas de projeto)."""
    me = o.data
    me.materials.append(M(mat))
    idx = len(me.materials) - 1
    for p in me.polygons:
        c, n = p.center, p.normal
        if teste((c.x, c.z, -c.y), (n.x, n.z, -n.y)):
            p.material_index = idx
    return o


def apagar(o, teste):
    """Remove faces escondidas: teste(centro, normal) em coordenadas de projeto."""
    bm = bmesh.new(); bm.from_mesh(o.data)
    fs = [f for f in bm.faces if teste((f.calc_center_median().x, f.calc_center_median().z, -f.calc_center_median().y),
                                       (f.normal.x, f.normal.z, -f.normal.y))]
    bmesh.ops.delete(bm, geom=fs, context='FACES')
    bm.to_mesh(o.data); bm.free()
    return o


def mover(o, dx=0, dy=0, dz=0):
    d = P(dx, dy, dz)
    for v in o.data.vertices:
        v.co += d
    return o


def girar(o, graus, eixo='y', centro=(0, 0, 0)):
    """Gira os vértices em torno de um eixo de projeto que passa por centro."""
    from mathutils import Matrix
    ax = {'x': (1, 0, 0), 'y': (0, 0, 1), 'z': (0, -1, 0)}[eixo]
    R = Matrix.Rotation(math.radians(graus), 4, Vector(ax))
    c = P(*centro)
    for v in o.data.vertices:
        v.co = (R @ (v.co - c)) + c
    return o


PARTES = []


def parte(nome, objs, origem=None, pai=None, grupo='A', suave=32, extra=None):
    o = join(objs if isinstance(objs, (list, tuple)) else [objs], nome)
    me = o.data
    me.name = nome
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(suave))
    org = P(*origem) if origem is not None else Vector((0, 0, 0))
    for v in me.vertices:
        v.co -= org
    o.location = org
    o['grupo'] = grupo
    for k, v in (extra or {}).items():
        o[k] = v
    if pai is not None:
        bpy.context.view_layer.update()
        o.parent = pai
        o.matrix_parent_inverse = pai.matrix_world.inverted()
    PARTES.append(o)
    return o


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)
