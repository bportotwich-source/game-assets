"""Foto dos GLBs do jogo lado a lado (com as texturas), enquadrados pelo tamanho deles.
uso: python3 foto.py saida.png ../../loot/estojo_municao.glb ../../loot/estojo_armas.glb ..."""
import sys, bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
out = sys.argv[1]; arqs = sys.argv[2:]
x = 0.0
for a in arqs:
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=a)
    novos = [o for o in bpy.data.objects if o not in antes]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in novos if o.type == 'MESH' for c in o.bound_box]
    larg = max(p.x for p in pts) - min(p.x for p in pts)
    for o in novos:
        if o.parent is None:
            o.location.x += x + larg / 2
    x += larg + 0.18
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
meio = (mn + mx) / 2; d = (mx - mn).length
sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
cam.location = meio + Vector((0.18 * d, -1.05 * d, 0.55 * d)); cam.rotation_euler = (meio - cam.location).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = 36; sc.camera = cam
for off, e in (((0.6, -0.9, 1.2), 90), ((-0.9, -0.6, 0.6), 35), ((0, -0.9, 0.1), 12), ((0, 0.9, 0.7), 40)):
    l = bpy.data.objects.new('l', bpy.data.lights.new('l', 'AREA')); l.data.energy = e * d * d * 0.3; l.data.size = d; l.location = meio + Vector(off) * d
    l.rotation_euler = (meio - l.location).to_track_quat('-Z', 'Y').to_euler(); sc.collection.objects.link(l)
bpy.ops.mesh.primitive_plane_add(size=20 * d, location=(meio.x, meio.y, 0))
m = bpy.data.materials.new('chao'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.12, 0.10, 0.08, 1); bpy.context.object.data.materials.append(m)
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.2, 0.2, 0.22, 1)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.render.resolution_x, sc.render.resolution_y = 1600, 800
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
