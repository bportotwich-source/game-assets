"""Renders de conferência do modelo texturizado.
uso: [FOTO_ACESSORIOS=pasta] python3 foto.py saida/brasa.blend prefixo vistas..."""
import sys, math, bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
# FOTO_ACESSORIOS=pasta com coronha/, guarda_mao/ e freio/ (saídas do gerar.py): monta os três nos encaixes
import os
_AC = os.environ.get('FOTO_ACESSORIOS')
if _AC:
    for nome, raiz, pos in (('coronha', 'coronha_brasa', (0, -0.063, 0.085)), ('guarda_mao', 'guarda_mao_brasa', (0, 0.208, 0.084)),
                            ('freio', 'freio_brasa', (0, 0.588, 0.084))):
        with bpy.data.libraries.load(os.path.join(_AC, nome, raiz + '.blend')) as (de, para):
            para.objects = list(de.objects)
        for o in para.objects:
            bpy.context.scene.collection.objects.link(o)
        bpy.data.objects[raiz].location = pos
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
C = Vector((0, 0.11, 0.06))     # centro aproximado depois da origem no punho
R = (1600, 1100)
V = {'esq': ((-2, 0, 0), (0, 0, 0), 1.08, (1800, 800)), 'dir': ((2, 0, 0), (0, 0, 0), 1.08, (1800, 800)),
     'rec': ((2, -0.06, 0.02), (0, -0.06, 0.02), 0.40, (1800, 1000)), 'rece': ((-2, -0.06, 0.02), (0, -0.06, 0.02), 0.40, (1800, 1000)),
     'frente': ((-1.6, 1.0, 0.6), (0, 0.33, 0.04), 0.46, (1800, 1000)), 'coronha': ((-1.6, -1.2, 0.5), (0, -0.33, -0.02), 0.55, (1800, 1000)),
     '34': ((-1.2, 1.4, 0.7), (0, 0, 0), 0.86, R), '34d': ((1.3, -1.2, 0.8), (0, 0, 0), 0.86, R),
     'cima': ((-0.3, 0, 2), (0, 0, 0.03), 0.86, (1600, 700)), 'perto': ((-1.5, -0.9, 0.7), (0, -0.27, 0.05), 0.30, R),
     'cabo': ((-2, 0.3, -0.2), (0, -0.02, 0.03), 0.34, R), 'boca': ((-0.9, 1.6, 0.4), (0, 0.28, 0.07), 0.30, R)}
for k in sys.argv[3:]:
    p, a, s, r = V[k]
    cam.location = Vector(p) + C; cd.ortho_scale = s
    cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = r
    sc.render.filepath = f'{sys.argv[2]}_{k}.png'
    bpy.ops.render.render(write_still=True)
