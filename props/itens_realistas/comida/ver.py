"""Foto rápida das formas sem texturas (cores das classes), uma ao lado da outra em z.
uso: python3 ver.py saida.png [forma ...]"""
import sys, os
sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'moveis_realistas')]
import base, bpy
import materiais, modelo, texturas
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
formas = sys.argv[2:] or list(modelo.FORMAS)
y = 0.0
for f in formas:
    raiz = modelo.FORMAS[f]()
    raiz.location.y = y
    y += float(os.environ.get('PASSO', 0.3))
    print(f, sum(len(p.vertices) - 2 for o in [raiz] + list(raiz.children_recursive) for p in o.data.polygons), 'triângulos')
for m in bpy.data.materials:
    c = texturas.CLASSES.get(m.name)
    if c:
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*c[0], 1)
        b.inputs['Roughness'].default_value = c[1]
        b.inputs['Metallic'].default_value = c[2]
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
meio, d = (mn + mx) / 2, max((mx - mn).length, 0.2)
sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.location = meio + Vector((0.25 * d, -0.9 * d, 1.1 * d))
cam.rotation_euler = (meio - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 60
sc.camera = cam
for off, e in (((1, -1.2, 1.6), 60), ((-1.3, -0.6, 0.9), 25), ((0, 1.2, 1.0), 25)):
    l = bpy.data.objects.new('l', bpy.data.lights.new('l', 'AREA'))
    l.data.energy = e * d * d
    l.data.size = d
    l.location = meio + Vector(off) * d
    l.rotation_euler = (meio - l.location).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(l)
bpy.ops.mesh.primitive_plane_add(size=20, location=(meio.x, meio.y, 0))
ch = bpy.data.materials.new('chao')
ch.use_nodes = True
ch.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.12, 0.10, 0.08, 1)
bpy.context.object.data.materials.append(ch)
sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.2, 0.2, 0.22, 1)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 40
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.render.filepath = sys.argv[1]
bpy.ops.render.render(write_still=True)
