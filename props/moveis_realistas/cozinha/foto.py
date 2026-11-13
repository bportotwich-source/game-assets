"""Foto do GLB do jogo (com as texturas), fechado ou com as gavetas e portas abertas.
uso: python3 foto.py saida.png forma [aberto]"""
import sys, os, math, json
import bpy
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
forma = sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(AQUI, '..', '..', 'mobilias', forma + '.glb'))
if len(sys.argv) > 3:
    cat = json.load(open(os.path.join(AQUI, '..', '..', 'mobilias', 'catalogo.json'), encoding='utf-8'))
    for p in next(x for x in cat['itens'] if x['id'] == forma)['partes']:
        o = bpy.data.objects[p['no']]
        if p['tipo'] == 'gaveta':
            o.location.y -= p['desliza'][2] * (0.6 + 0.4 * (p['no'][-1] in '3a'))
        else:
            o.rotation_mode = 'XYZ'
            o.rotation_euler = (0, 0, math.radians(p['abre_graus'] * 0.85))
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
meio, d = (mn + mx) / 2, (mx - mn).length
sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.location = meio + Vector((0.75 * d, -1.35 * d, 0.45 * d))
cam.rotation_euler = (meio - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 50
sc.camera = cam
for off, e in (((1, -1.2, 1.6), 45), ((-1.3, -0.6, 0.9), 18), ((0, -1.2, 0.2), 8)):
    l = bpy.data.objects.new('l', bpy.data.lights.new('l', 'AREA'))
    l.data.energy = e * d * d
    l.data.size = d
    l.location = meio + Vector(off) * d
    l.rotation_euler = (meio - l.location).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(l)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ch = bpy.data.materials.new('chao')
ch.use_nodes = True
ch.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.16, 0.13, 0.10, 1)
bpy.context.object.data.materials.append(ch)
sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.14, 0.14, 0.15, 1)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.render.resolution_x, sc.render.resolution_y = 1200, 1200
sc.render.filepath = sys.argv[1]
bpy.ops.render.render(write_still=True)
