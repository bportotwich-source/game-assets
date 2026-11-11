"""Renders de conferência do modelo texturizado.
uso: [FOTO_MONTAR=a.blend,b.blend] python3 foto.py saida/recurvo.blend prefixo vistas..."""
import sys, math, bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
# FOTO_MONTAR=a.blend,b.blend: acessórios (saídas do gerar.py) postos nos encaixes; o encaixe sai do nome do arquivo
import os
_POS = {}
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
    ld = bpy.data.lights.new(f'a{i}', 'AREA'); ld.energy = e * 1.3; ld.size = s * 2
    lo = bpy.data.objects.new(f'a{i}', ld); sc.collection.objects.link(lo)
    lo.location = p; lo.rotation_euler = (Vector((0, 0, 0)) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = 'ORTHO'
sc.view_settings.view_transform = 'Standard'
C = Vector((0, -0.03, 0.02))    # centro aproximado depois da origem no punho
R = (1300, 1700)
D = (1500, 1100)
V = {'esq': ((-3, 0, 0), (0, 0, 0), 1.55, R), 'dir': ((3, 0, 0), (0, 0, 0), 1.55, R),
     'punho': ((-3, 0.4, 0.2), (0, 0, 0), 0.62, R), 'punho_d': ((3, 0.4, 0.2), (0, 0, 0), 0.62, R),
     'punho_t': ((-1.6, -2.4, 0.5), (0, 0, 0), 0.62, R),
     'janela': ((-2.2, -2.0, 0.9), (0, 0.04, 0.06), 0.26, D), 'ponta': ((-2, -1.5, 0.3), (0, -0.11, 0.67), 0.20, D),
     'pe': ((-1.6, 2.2, 0.6), (0, 0.06, 0.26), 0.24, D), 'flecha': ((-2, -1, 1.2), (0, -0.10, 0.03), 0.20, D),
     'ponta_flecha': ((-2, 1, 1.2), (0, 0.55, 0.03), 0.16, D)}
for k in sys.argv[3:]:
    p, a, s, r = V[k]
    cam.location = Vector(p) + C + Vector(a); cd.ortho_scale = s
    cam.rotation_euler = (-Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = r
    sc.render.filepath = f'{sys.argv[2]}_{k}.png'
    bpy.ops.render.render(write_still=True)
