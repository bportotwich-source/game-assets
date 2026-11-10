"""Renders de conferência do modelo texturizado."""
import sys, math, bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes['Background']
sky = nt.nodes.new('ShaderNodeTexGradient'); tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
mp.inputs['Rotation'].default_value = (0, math.radians(90), 0)
nt.links.new(tc.outputs['Generated'], mp.inputs[0]); nt.links.new(mp.outputs[0], sky.inputs[0])
ramp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sky.outputs[0], ramp.inputs[0])
ramp.color_ramp.elements[0].color = (0.25, 0.25, 0.27, 1); ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
nt.links.new(ramp.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.45
for i, (p, e, s) in enumerate((((-1.0, 0.6, 1.6), 130, 1.2), ((1.5, -0.6, 0.8), 60, 1.5), ((-0.3, -1.5, 0.4), 40, 1.0), ((0.5, 1.2, -0.5), 25, 1.0))):
    ld = bpy.data.lights.new(f'a{i}', 'AREA'); ld.energy = e; ld.size = s
    lo = bpy.data.objects.new(f'a{i}', ld); sc.collection.objects.link(lo)
    lo.location = p; lo.rotation_euler = (Vector((0, 0.05, 0.05)) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = 'ORTHO'
sc.view_settings.view_transform = 'Standard'
C = Vector((0, 0.13, 0.06))     # centro aproximado depois da origem no punho
V = {'esq': ((-2, 0, 0), (0, 0, 0), 0.95, (1800, 900)), 'dir': ((2, 0, 0), (0, 0, 0), 0.95, (1800, 900)),
     'rec_esq': ((-2, -0.08, 0.02), (0, -0.08, 0.02), 0.36, (1500, 950)), 'rec_dir': ((2, -0.08, 0.02), (0, -0.08, 0.02), 0.36, (1500, 950)),
     'frente': ((-0.8, 1.1, 0.5), (0, 0.17, 0.02), 0.40, (1500, 950)), 'coronha': ((-1.0, -1.3, 0.4), (0, -0.33, -0.01), 0.36, (1500, 950)),
     '34': ((-1.2, 1.4, 0.7), (0, 0.0, -0.01), 0.82, (1800, 900)), '34d': ((1.2, -1.3, 0.8), (0, 0.0, -0.01), 0.82, (1800, 900))}
for k in sys.argv[3:]:
    p, a, s, r = V[k]
    cam.location = Vector(p) + C; cd.ortho_scale = s
    cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = r
    sc.render.filepath = f'{sys.argv[2]}_{k}.png'
    bpy.ops.render.render(write_still=True)
