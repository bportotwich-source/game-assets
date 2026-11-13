"""Foto rápida de um móvel sem texturas (cores das classes), para conferir as formas.
uso: python3 ver.py saida.png forma [aberto]"""
import sys, os, math
sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
import base, bpy
import materiais, modelo, texturas
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
forma = sys.argv[2]
modelo.FORMAS[forma]()
for m in bpy.data.materials:
    c = texturas.CLASSES.get(m.name)
    if c:
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*c[0], 1)
        b.inputs['Roughness'].default_value = c[1]
        b.inputs['Metallic'].default_value = c[2]
if len(sys.argv) > 3:
    for o in bpy.data.objects:
        if o.name.startswith('gaveta'):
            o.location.y -= 0.28
        elif o.name.startswith('porta'):
            o.rotation_euler = (0, 0, math.radians(-105 if o.name.endswith('esq') else 105) * (-1 if o.name[-1].isdigit() else 1))
print('triângulos', sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == 'MESH' for p in o.data.polygons))
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
meio, d = (mn + mx) / 2, (mx - mn).length
sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.location = meio + Vector((0.75 * d, -1.35 * d, 0.55 * d))
cam.rotation_euler = (meio - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 50
sc.camera = cam
for off, e in (((1, -1.2, 1.6), 60), ((-1.3, -0.6, 0.9), 30), ((0, -1.2, 0.2), 20)):
    l = bpy.data.objects.new('l', bpy.data.lights.new('l', 'AREA'))
    l.data.energy = e * d * d
    l.data.size = d
    l.location = meio + Vector(off) * d
    l.rotation_euler = (meio - l.location).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(l)
sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.25, 0.25, 0.27, 1)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 24
sc.render.resolution_x, sc.render.resolution_y = 1100, 1100
sc.render.filepath = sys.argv[1]
bpy.ops.render.render(write_still=True)
