"""Renders de conferência da forma dos arremessáveis (Cycles CPU, cores chapadas, sem texturas).
uso: python3 ver.py <função de modelo.py> [prefixo de saída] [escala]"""
import sys, os, math
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import bpy
from mathutils import Vector

CORES = {'vidro_garrafa': (0.2, 0.5, 0.2), 'combustivel': (0.6, 0.45, 0.1), 'papel_rotulo': (0.75, 0.65, 0.45), 'pano_sujo': (0.6, 0.5, 0.35), 'pano_queimado': (0.05, 0.05, 0.05),
         'barbante': (0.5, 0.4, 0.25), 'lata': (0.55, 0.55, 0.57), 'prego_velho': (0.25, 0.2, 0.17), 'fita_cinza': (0.4, 0.4, 0.42), 'pavio_verde': (0.1, 0.4, 0.12),
         'esmalte_relogio': (0.5, 0.05, 0.04), 'cromado': (0.7, 0.7, 0.72), 'mostrador': (0.85, 0.83, 0.72), 'ponteiro': (0.02, 0.02, 0.02), 'ponteiro_alarme': (0.7, 0.05, 0.03), 'tinta_preta': (0.02, 0.02, 0.02),
         'anod': (0.12, 0.12, 0.13), 'serr': (0.3, 0.3, 0.32), 'fosf': (0.07, 0.07, 0.07), 'inox': (0.5, 0.5, 0.5),
         'lente_clara': (0.5, 0.7, 0.9), 'tinta': (0.85, 0.85, 0.85), 'led': (0.8, 0.05, 0.05),
         'anod_laranja': (0.7, 0.2, 0.03), 'tinta_viva': (0.8, 0.86, 0.3), 'fibra_verde': (0.2, 1, 0.3), 'fibra_amarelo': (1, 0.85, 0.05),
         'fibra_vermelho': (1, 0.1, 0.05), 'luz_fria': (0.75, 0.9, 1)}

if __name__ == '__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import modelo
    from lib import PARTES
    import materiais; getattr(modelo, sys.argv[1])()
    print('tris', sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in PARTES))
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get('Principled BSDF')
        if b and m.name in CORES:
            b.inputs['Base Color'].default_value = (*CORES[m.name], 1)
            b.inputs['Roughness'].default_value = 0.55
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.cycles.use_denoising = True
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.7
    for i, (p, e) in enumerate((((1.2, 0.3, 1.5), 4), ((-1.5, -0.4, 1.0), 3))):
        ld = bpy.data.lights.new(f's{i}', 'SUN'); ld.energy = e; ld.angle = 0.3
        lo = bpy.data.objects.new(f's{i}', ld); sc.collection.objects.link(lo)
        lo.rotation_euler = (-Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    cd.type = 'ORTHO'
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/mira'
    esc = float(sys.argv[3]) if len(sys.argv) > 3 else 0.11
    for k, pos in (('dir', (2, 0, 0.0)), ('34', (1.2, -1.6, 0.9)), ('frente', (-0.8, 1.8, 0.6)), ('tras', (0.0, -2.0, 0.3))):
        cd.ortho_scale = esc
        cam.location = Vector(pos) + Vector((float(sys.argv[4]) if len(sys.argv) > 4 else 0, 0, float(sys.argv[5]) if len(sys.argv) > 5 else 0.022))
        cam.rotation_euler = (-Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.resolution_x, sc.render.resolution_y = 900, 700
        sc.render.filepath = f'{out}_{k}.png'
        bpy.ops.render.render(write_still=True)
