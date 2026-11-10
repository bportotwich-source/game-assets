"""Renders de conferência: python3 foto.py <arquivo.blend> <prefixo> [res] [amostras]"""
import sys, math, bpy
from mathutils import Vector
src, pref = sys.argv[1], sys.argv[2]
res = int(sys.argv[3]) if len(sys.argv) > 3 else 900
amo = int(sys.argv[4]) if len(sys.argv) > 4 else 24
quais = sys.argv[5].split(',') if len(sys.argv) > 5 else None
bpy.ops.wm.open_mainfile(filepath=src)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = amo; sc.cycles.use_denoising = True
sc.render.resolution_x = res; sc.render.resolution_y = int(res * 0.75)
sc.view_settings.view_transform = 'AgX'
CORES = {'reboco': (0.75, 0.72, 0.62), 'tijolo': (0.45, 0.2, 0.14), 'tabua': (0.42, 0.52, 0.5), 'guarn': (0.8, 0.78, 0.7), 'rodape': (0.85, 0.84, 0.8), 'porta': (0.3, 0.06, 0.05),
         'vidro': (0.6, 0.7, 0.75), 'latao': (0.8, 0.6, 0.25), 'ferro': (0.05, 0.05, 0.05), 'pedra': (0.5, 0.5, 0.48), 'cimento': (0.4, 0.4, 0.4), 'assoalho': (0.45, 0.28, 0.15),
         'verniz': (0.25, 0.12, 0.06), 'pinho': (0.7, 0.55, 0.35), 'lata': (0.6, 0.6, 0.6), 'rotulo': (0.5, 0.07, 0.05), 'rotulo_creme': (0.85, 0.8, 0.6), 'esmalte': (0.1, 0.2, 0.45), 'arame': (0.3, 0.3, 0.3)}
for m in bpy.data.materials:
    bs = m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
    if bs and m.name in CORES and not m.get('pronto'):
        bs.inputs['Base Color'].default_value = (*CORES[m.name], 1)
        if m.name == 'vidro':
            bs.inputs['Alpha'].default_value = 0.25
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.75, 0.82, 0.95, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.45
sun = bpy.data.objects.new('sol', bpy.data.lights.new('sol', 'SUN')); sun.data.energy = 2.6; sun.data.angle = 0.03
sun.rotation_euler = (math.radians(50), 0, math.radians(35)); sc.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.45))
def P(x, y, z): return Vector((x, -z, y))
CAMS = {'fachada': ((0.6, 1.3, 5.2), (0.0, 1.25, 0), 30), 'porta': ((1.9, 1.4, 1.9), (1.0, 1.25, 0), 35), 'janela': ((-1.9, 1.6, 1.6), (-1.0, 1.5, 0), 35),
        'macaneta': ((1.15, 1.15, 0.42), (1.38, 1.05, -0.15), 50), 'interior': ((1.6, 1.6, -3.9), (-0.9, 1.0, -0.6), 24), 'comoda': ((-0.3, 1.15, -2.9), (-1.7, 0.5, -1.7), 35),
        'itens': ((-1.25, 1.12, -1.95), (-1.63, 0.93, -1.68), 50), 'puxador': ((-1.3, 0.75, -1.55), (-1.66, 0.5, -1.7), 60), 'jan_int': ((-0.2, 1.5, -2.2), (-1.0, 1.4, -0.3), 35),
        'tabuas': ((-0.6, 0.6, 0.9), (-1.5, 0.35, 0), 50)}
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
for nome, (pos, alvo, lente) in CAMS.items():
    if quais and nome not in quais: continue
    cam.location = P(*pos); d = P(*alvo) - P(*pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = lente; cam.data.clip_start = 0.01
    sc.render.filepath = f'{pref}_{nome}.png'
    bpy.ops.render.render(write_still=True)
