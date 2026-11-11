"""Renders de conferência da forma (Cycles CPU, cores chapadas, sem texturas).
uso: python3 ver.py [prefixo de saída] [vistas...]"""
import sys, os, math, time
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import bpy
from mathutils import Vector

CORES = {'aco_polido': (0.45, 0.45, 0.45), 'polim_esp_grip': (0.26, 0.26, 0.27), 'tinta_vermelha': (0.7, 0.05, 0.05), 'fosf': (0.07, 0.07, 0.07),
         'anod': (0.12, 0.12, 0.13), 'anod_tubo': (0.2, 0.2, 0.21), 'fosf_escuro': (0.16, 0.16, 0.16), 'borracha': (0.05, 0.05, 0.05), 'polim_claro': (0.3, 0.4, 0.25),
         'aco_cano': (0.3, 0.3, 0.3), 'polim': (0.13, 0.13, 0.13), 'inox': (0.5, 0.5, 0.5), 'latao': (0.8, 0.6, 0.2), 'cobre': (0.7, 0.35, 0.2),
         'tinta': (0.85, 0.85, 0.85), 'tinta_branca': (0.9, 0.9, 0.9), 'tinta_preta': (0.02, 0.02, 0.02)}
C = Vector((0, 0.33, -0.065))
VISTAS = {'esq': ((-2, 0, 0), 0.86, (1600, 1100)), 'dir': ((2, 0, 0), 0.86, (1600, 1100)), '34': ((-1.2, 1.4, 0.7), 0.86, (1600, 1100)),
          '34d': ((1.3, -1.2, 0.8), 0.86, (1600, 1100)), 'cima': ((0, 0, 2), 0.86, (1600, 500)), 'frente': ((0.5, 2, 0.3), 0.22, (1200, 1100)),
          'tras': ((-0.5, -2, 0.5), 0.22, (1200, 1100)), 'baixo': ((-0.6, 0.3, -2), 0.86, (1600, 1000))}


def render(path, pos, ortho, res, samples=24):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    cam = bpy.data.objects.get('cam')
    if not cam:
        cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam)
        sc.camera = cam
        w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
        w.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
        w.node_tree.nodes['Background'].inputs[1].default_value = 0.7
        for i, (p, e) in enumerate((((1.2, 0.3, 1.5), 4), ((-1.5, -0.4, 1.0), 3))):
            ld = bpy.data.lights.new(f's{i}', 'SUN'); ld.energy = e; ld.angle = 0.3
            lo = bpy.data.objects.new(f's{i}', ld); sc.collection.objects.link(lo)
            lo.rotation_euler = (Vector((0, 0, 0)) - Vector(p)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    cam.location = Vector(pos) + C
    cam.rotation_euler = (-Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    t = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import modelo
    from lib import PARTES
    modelo.montar()
    if os.environ.get('CORONHA'):
        import coronha
        coronha.montar()
    for o in PARTES:
        print(f"{o.name:22s} {sum(len(p.vertices) - 2 for p in o.data.polygons):6d}")
    print('peças', len(PARTES), 'tris', sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in PARTES), f'{time.time() - t:.0f}s')
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get('Principled BSDF')
        if b and m.name in CORES:
            b.inputs['Base Color'].default_value = (*CORES[m.name], 1)
            b.inputs['Roughness'].default_value = 0.55
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/espingarda'
    for k in (sys.argv[2:] or ['esq', 'dir', '34', 'cima']):
        render(f'{out}_{k}.png', *VISTAS[k])
