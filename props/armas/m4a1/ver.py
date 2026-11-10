"""Renders de conferência (Cycles CPU)."""
import sys, math, bpy
sys.path.insert(0, '.')
from mathutils import Vector
def cena_limpa():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def render(path, pos, alvo, ortho=0.95, res=(1600, 800), samples=24):
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
    cam.location = pos
    cam.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
if __name__ == '__main__':
    import time; t = time.time()
    cena_limpa()
    import modelo
    partes = modelo.montar()
    print('partes', len(partes), 'tris', sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in partes), time.time() - t)
    cores = {'anod': (0.05, 0.052, 0.055), 'anod_tubo': (0.06, 0.06, 0.06), 'fosf': (0.09, 0.09, 0.085), 'fosf_escuro': (0.12, 0.12, 0.12),
             'polim': (0.03, 0.03, 0.03), 'polim_grip': (0.05, 0.03, 0.03), 'magal': (0.1, 0.1, 0.1), 'serr': (0.12, 0.1, 0.08),
             'inox': (0.5, 0.5, 0.5), 'latao': (0.8, 0.6, 0.2), 'cobre': (0.7, 0.35, 0.2), 'tinta': (0.8, 0.8, 0.8), 'polim_claro': (0.2, 0.2, 0.15)}
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get('Principled BSDF')
        if b and m.name in cores:
            c = cores[m.name]; k = 3.0
            b.inputs['Base Color'].default_value = (min(1, c[0] * k), min(1, c[1] * k), min(1, c[2] * k), 1)
            b.inputs['Roughness'].default_value = 0.55
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/m4'
    c = (0, -0.02, -0.04)
    render(out + '_esq.png', (-2, -0.02, -0.04), c)
    render(out + '_dir.png', (2, -0.02, -0.04), c)
    render(out + '_34.png', (-1.2, 1.4, 0.7), (0, 0.0, -0.03), ortho=0.8)
    render(out + '_cima.png', (0, -0.02, 2), (0, -0.02, 0), ortho=0.95, res=(1600, 400))
    bpy.ops.wm.save_as_mainfile(filepath='/tmp/m4_modelo.blend')
