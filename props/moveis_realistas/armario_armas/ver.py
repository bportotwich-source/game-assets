"""Foto rápida do modelo sem texturas (cores das classes), para conferir as formas.
uso: python3 ver.py saida.png [aberto]"""
import sys, os, math
sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
import base, bpy
import materiais, modelo, texturas
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
modelo.montar()
for m in bpy.data.materials:
    c = texturas.CLASSES.get(m.name)
    if c:
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*c[0], 1)
        b.inputs['Roughness'].default_value = c[1]
        b.inputs['Metallic'].default_value = c[2]
if len(sys.argv) > 2:
    for n, a in (('porta_esq', -110), ('porta_dir', 110)):
        bpy.data.objects[n].rotation_euler = (0, 0, math.radians(a))
tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == 'MESH' for p in o.data.polygons)
print('triângulos', tris)
sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.location = (1.6, -3.4, 1.5)
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 50
sc.camera = cam
for pos, e in (((2, -3, 3), 900), ((-3, -2, 2), 400), ((0, -3, 0.5), 200)):
    l = bpy.data.objects.new('l', bpy.data.lights.new('l', 'AREA'))
    l.data.energy = e
    l.data.size = 2
    l.location = pos
    l.rotation_euler = (Vector((0, 0, 1)) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(l)
sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.25, 0.25, 0.27, 1)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 24
sc.render.resolution_x, sc.render.resolution_y = 900, 1100
sc.render.filepath = sys.argv[1]
bpy.ops.render.render(write_still=True)
