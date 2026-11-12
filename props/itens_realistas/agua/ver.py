"""Foto rápida das formas sem texturas (cores das classes; plástico e vidro meio transparentes).
uso: python3 ver.py saida.png [forma ...]"""
import sys, os
sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'moveis_realistas')]
import base, bpy
import materiais, modelo, texturas
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
formas = sys.argv[2:] or list(modelo.FORMAS)
for k, f in enumerate(formas):
    raiz = modelo.FORMAS[f]()
    raiz.location.x += 0.26 * k
    print(f, sum(len(p.vertices) - 2 for o in [raiz] + list(raiz.children_recursive) for p in o.data.polygons), 'triângulos')
for m in bpy.data.materials:
    c = texturas.CLASSES.get(m.name)
    if c:
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*c[0], 1)
        b.inputs['Roughness'].default_value = c[1]
        b.inputs['Metallic'].default_value = c[2]
        if m.name in ('pet', 'vidro_verde'):
            b.inputs['Alpha'].default_value = 0.3
n = len(formas)
cx = 0.13 * (n - 1)
d = 0.5 + 0.4 * n
sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.location = (cx + 0.25 * d, -d, 0.5 * d + 0.1)
cam.rotation_euler = (Vector((cx, 0, 0.13)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 60
sc.camera = cam
for pos, e in (((cx + 1.5, -2, 2.5), 300), ((cx - 2, -1.5, 1.5), 120), ((cx, -2, 0.3), 40), ((cx, 2, 1.5), 150)):
    l = bpy.data.objects.new('l', bpy.data.lights.new('l', 'AREA'))
    l.data.energy = e
    l.data.size = 1.5
    l.location = pos
    l.rotation_euler = (Vector((cx, 0, 0.1)) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(l)
bpy.ops.mesh.primitive_plane_add(size=6, location=(cx, 0, 0))
ch = bpy.data.materials.new('chao')
ch.use_nodes = True
ch.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.33, 0.27, 0.2, 1)
bpy.context.object.data.materials.append(ch)
sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.2, 0.2, 0.22, 1)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 40
sc.render.resolution_x, sc.render.resolution_y = 1600, 800
sc.render.filepath = sys.argv[1]
bpy.ops.render.render(write_still=True)
