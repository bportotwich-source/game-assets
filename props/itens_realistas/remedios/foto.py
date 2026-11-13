"""Foto dos GLBs do jogo lado a lado (com as texturas).
uso: python3 foto.py saida.png ../../loot/garrafa_pet.glb ../../loot/garrafa_pet_agua_suja.glb ..."""
import sys, bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
out=sys.argv[1]; arqs=sys.argv[2:]
x=0
for a in arqs:
    antes=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=a)
    novos=[o for o in bpy.data.objects if o not in antes]
    for o in novos:
        if o.parent is None: o.location.x+=x
    x+=0.36
n=len(arqs); cx=(n-1)*0.18
sc=bpy.context.scene
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
d=0.5+0.5*n
cam.location=(cx+0.25*d,-d,0.4*d+0.1); cam.rotation_euler=(Vector((cx,0,0.13))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=85; sc.camera=cam
for pos,e in (((cx+1.5,-2,2.5),70),((cx-2,-1.5,1.5),30),((cx,-2,0.3),10),((cx,2,1.5),35)):
    l=bpy.data.objects.new('l',bpy.data.lights.new('l','AREA')); l.data.energy=e; l.data.size=1.5; l.location=pos
    l.rotation_euler=(Vector((cx,0,0.1))-Vector(pos)).to_track_quat('-Z','Y').to_euler(); sc.collection.objects.link(l)
bpy.ops.mesh.primitive_plane_add(size=6,location=(cx,0,0))
m=bpy.data.materials.new('chao'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.12,0.10,0.08,1); bpy.context.object.data.materials.append(m)
sc.world=bpy.data.worlds.new('w'); sc.world.use_nodes=True; sc.world.node_tree.nodes['Background'].inputs[0].default_value=(0.2,0.2,0.22,1)
sc.render.engine='CYCLES'; sc.cycles.samples=48; sc.render.resolution_x,sc.render.resolution_y=1500,800
sc.render.filepath=out; bpy.ops.render.render(write_still=True)
