"""Renders de conferência da forma da faca de combate (Cycles CPU, cores chapadas, sem texturas).
uso: python3 ver.py [prefixo de saída] [vistas...]"""
import sys, os, math, time
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import bpy
from mathutils import Vector

CORES = {'polim_oliva': (0.3, 0.34, 0.18), 'anod_cabeca': (0.14, 0.14, 0.15), 'fita_deslize': (0.03, 0.03, 0.03), 'corda_besta': (0.25, 0.32, 0.15), 'laranja_trava': (0.9, 0.3, 0.04), 'pena_vermelha': (0.8, 0.06, 0.04), 'anod_arco': (0.3, 0.31, 0.3), 'anod_laranja': (0.85, 0.3, 0.04), 'polim_arco_grip': (0.1, 0.1, 0.11), 'fibra_faixa': (0.16, 0.18, 0.22), 'cabo': (0.25, 0.32, 0.15), 'cordel': (0.85, 0.35, 0.05), 'pena_verde': (0.4, 0.75, 0.1), 'nock_vermelho': (0.85, 0.08, 0.05), 'madeira_arco': (0.3, 0.14, 0.06), 'fibra_arco': (0.06, 0.06, 0.07), 'lamina_bordo': (0.6, 0.45, 0.25), 'fenolico': (0.7, 0.66, 0.55), 'corda': (0.12, 0.1, 0.08), 'corda_reforco': (0.03, 0.03, 0.03), 'feltro': (0.1, 0.09, 0.08), 'couro_arco': (0.25, 0.13, 0.06), 'carbono': (0.05, 0.05, 0.05), 'envoltorio': (0.85, 0.85, 0.8), 'pena_laranja': (0.9, 0.3, 0.03), 'pena_branca': (0.9, 0.9, 0.85), 'nock': (0.9, 0.3, 0.03), 'aluminio_flecha': (0.6, 0.6, 0.6), 'aco_lamina': (0.55, 0.55, 0.55), 'tinta_ouro': (0.8, 0.6, 0.2), 'laranja_sinal': (0.75, 0.25, 0.05), 'polim_sinal_grip': (0.15, 0.15, 0.16), 'casco_vermelho': (0.6, 0.05, 0.04), 'nogueira_pardal': (0.38, 0.19, 0.08), 'polim_pardal': (0.2, 0.2, 0.21), 'aco_brasa_gasto': (0.1, 0.1, 0.1), 'polim_gasto': (0.16, 0.16, 0.17), 'anod_gasto': (0.2, 0.2, 0.22), 'polim_brasa_grip': (0.22, 0.22, 0.22), 'aco_brasa': (0.09, 0.09, 0.1), 'madeira_brasa': (0.45, 0.2, 0.07), 'baquelite_grip': (0.3, 0.1, 0.05), 'laca_verde': (0.2, 0.25, 0.12), 'aco_polido': (0.45, 0.45, 0.45), 'polim_car_grip': (0.26, 0.26, 0.27), 'areia': (0.5, 0.4, 0.25), 'nogueira_car': (0.35, 0.18, 0.08), 'azulado': (0.1, 0.11, 0.14), 'tinta_vermelha': (0.7, 0.05, 0.05), 'fosf': (0.07, 0.07, 0.07),
         'anod': (0.12, 0.12, 0.13), 'anod_tubo': (0.2, 0.2, 0.21), 'fosf_escuro': (0.16, 0.16, 0.16), 'borracha': (0.05, 0.05, 0.05), 'polim_claro': (0.3, 0.4, 0.25),
         'aco_cano': (0.3, 0.3, 0.3), 'polim': (0.13, 0.13, 0.13), 'inox': (0.5, 0.5, 0.5), 'latao': (0.8, 0.6, 0.2), 'cobre': (0.7, 0.35, 0.2),
         'tinta': (0.85, 0.85, 0.85), 'tinta_branca': (0.9, 0.9, 0.9), 'tinta_preta': (0.02, 0.02, 0.02)}
C = Vector((0, 0, 0))
VISTAS = {'esq': ((-3, 0, 0), 0.36, (1800, 600), (0, 0.02, -0.003)), 'dir': ((3, 0, 0), 0.36, (1800, 600), (0, 0.02, -0.003)),
          'cima': ((0, 0, 3), 0.36, (1800, 500), (0, 0.02, 0)),
          '34': ((-2, 2.4, 1.6), 0.34, (1600, 1100), (0, 0.02, 0)), '34t': ((2.0, -2.4, 1.3), 0.34, (1600, 1100), (0, 0.02, 0)),
          'cabo': ((-3, -0.8, 0.8), 0.19, (1600, 1000), (0, -0.07, -0.003)), 'ponta': ((-2.4, 1.6, 1.0), 0.16, (1600, 1000), (0, 0.11, 0))}


def render(path, pos, ortho, res, des=(0, 0, 0), samples=24):
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
    cam.location = Vector(pos) + C + Vector(des)
    cam.rotation_euler = (-Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    t = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import modelo
    from lib import PARTES
    for f in os.environ.get('MONTAR', 'montar').split(','):
        getattr(modelo, f)()
    for o in PARTES:
        print(f"{o.name:22s} {sum(len(p.vertices) - 2 for p in o.data.polygons):6d}")
    print('peças', len(PARTES), 'tris', sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in PARTES), f'{time.time() - t:.0f}s')
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get('Principled BSDF')
        if b and m.name in CORES:
            b.inputs['Base Color'].default_value = (*CORES[m.name], 1)
            b.inputs['Roughness'].default_value = 0.55
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/faca'
    if os.environ.get('VISTA_EXTRA'):                                # VISTA_EXTRA="nome:((x,y,z), escala, (larg, alt), (dx,dy,dz))"
        k, v = os.environ['VISTA_EXTRA'].split(':', 1); VISTAS[k] = eval(v)
    for k in (sys.argv[2:] or ['esq', 'dir', '34', 'cima']):
        render(f'{out}_{k}.png', *VISTAS[k])
