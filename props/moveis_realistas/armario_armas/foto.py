"""Foto do GLB do jogo (com as texturas), de portas fechadas ou abertas.
uso: python3 foto.py saida.png [aberto]"""
import sys, os, math
import bpy
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, '..', '..', 'mobilias', 'armario_armas.glb'))
if len(sys.argv) > 2:
    for n, a in (('porta_esq', -110), ('porta_dir', 110)):
        o = bpy.data.objects[n]
        o.rotation_mode = 'XYZ'
        o.rotation_euler = (0, 0, math.radians(a))
sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.location = (1.5, -3.3, 1.5)
cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 50
sc.camera = cam
for pos, e in (((2, -3, 3), 500), ((-3, -2, 2), 200), ((0, -3, 0.5), 80)):
    l = bpy.data.objects.new('l', bpy.data.lights.new('l', 'AREA'))
    l.data.energy = e
    l.data.size = 2
    l.location = pos
    l.rotation_euler = (Vector((0, 0, 1)) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(l)
sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.12, 0.12, 0.13, 1)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.render.resolution_x, sc.render.resolution_y = 900, 1100
sc.render.filepath = sys.argv[1]
bpy.ops.render.render(write_still=True)
