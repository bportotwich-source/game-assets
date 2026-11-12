"""Renders de conferência da forma das lunetas (Cycles CPU, cores chapadas, sem texturas).
uso: python3 ver.py <id> [prefixo de saída]"""
import sys, os, math
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import bpy
from mathutils import Vector

CORES = {'anod': (0.12, 0.12, 0.13), 'anod_tubo': (0.2, 0.2, 0.21), 'serr': (0.3, 0.3, 0.32), 'fosf': (0.07, 0.07, 0.07), 'inox': (0.5, 0.5, 0.5),
         'borracha': (0.05, 0.05, 0.05), 'lente': (0.1, 0.2, 0.6), 'tinta': (0.85, 0.85, 0.85)}

if __name__ == '__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import modelo
    from lib import PARTES
    modelo.luneta(sys.argv[1])
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
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/luneta'
    for k, pos, esc in (('dir', (2, 0, 0.0), 0.46), ('esq', (-2, 0, 0), 0.46), ('34', (1.2, -1.6, 0.9), 0.40), ('frente', (-0.8, 1.8, 0.6), 0.30)):
        cd.ortho_scale = esc
        cam.location = Vector(pos) + Vector((0, 0, 0.03))
        cam.rotation_euler = (-Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.resolution_x, sc.render.resolution_y = 1500, 620
        sc.render.filepath = f'{out}_{k}.png'
        bpy.ops.render.render(write_still=True)
