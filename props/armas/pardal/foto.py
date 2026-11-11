"""Renders de conferência do modelo texturizado.
uso: [FOTO_MONTAR=a.blend,b.blend] python3 foto.py saida/pardal.blend prefixo vistas..."""
import sys, math, bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
# FOTO_MONTAR=a.blend,b.blend: acessórios (saídas do gerar.py) postos nos encaixes; o encaixe sai do nome do arquivo
import os
_POS = {'alca': (0, 0.258, 0.0724), 'protetor': (0, 0.646, 0.062)}
for b in [b for b in os.environ.get('FOTO_MONTAR', '').split(',') if b]:
    raiz = os.path.basename(b)[:-6]
    with bpy.data.libraries.load(b) as (de, para):
        para.objects = list(de.objects)
    for o in para.objects:
        bpy.context.scene.collection.objects.link(o)
    bpy.data.objects[raiz].location = next(v for k, v in _POS.items() if raiz.startswith(k))
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
for i, (p, e, s) in enumerate((((-0.5, 0.3, 0.8), 28, 0.6), ((0.7, -0.3, 0.5), 14, 0.8), ((-0.2, -0.7, 0.2), 9, 0.5), ((0.3, 0.6, -0.3), 6, 0.5))):
    ld = bpy.data.lights.new(f'a{i}', 'AREA'); ld.energy = e; ld.size = s
    lo = bpy.data.objects.new(f'a{i}', ld); sc.collection.objects.link(lo)
    lo.location = p; lo.rotation_euler = (Vector((0, 0.09, 0.02)) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = 'ORTHO'
sc.view_settings.view_transform = 'Standard'
C = Vector((0, 0.19, 0.03))     # centro aproximado depois da origem no punho
R = (1600, 1100)
V = {'esq': ((-2, 0, 0), (0, 0, 0), 1.0, (1800, 620)), 'dir': ((2, 0, 0), (0, 0, 0), 1.0, (1800, 620)),
     'rec': ((2, -0.17, 0.02), (0, -0.17, 0.02), 0.36, (1800, 1000)), 'rece': ((-2, -0.17, 0.02), (0, -0.17, 0.02), 0.36, (1800, 1000)),
     'acao': ((1.2, -0.9, 1.2), (0, -0.19, 0.03), 0.30, (1800, 1000)), 'coronha': ((-1.6, -1.2, 0.5), (0, -0.36, -0.03), 0.5, (1800, 1000)),
     'telha': ((1.5, 1.0, 0.5), (0, 0.06, 0.0), 0.36, (1800, 1000)), 'massa': ((-1.4, 1.2, 0.7), (0, 0.42, 0.045), 0.16, (1600, 1000)),
     '34': ((-1.2, 1.4, 0.7), (0, 0, 0), 1.0, R)}
for k in sys.argv[3:]:
    p, a, s, r = V[k]
    cam.location = Vector(p) + C; cd.ortho_scale = s
    cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = r
    sc.render.filepath = f'{sys.argv[2]}_{k}.png'
    bpy.ops.render.render(write_still=True)
