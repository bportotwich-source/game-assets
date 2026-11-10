"""Gera a M4A1 e os acessórios: modelo, UVs, bake das texturas e GLB final.
uso: python3 gerar.py [resolução] [saída]
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo
(o desdobramento é determinístico); REASSAR=A,B força os grupos listados."""
import sys, os, json, struct, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import modelo, acessorios, texturas
from lib import PARTES
from lib import P

RES = int(sys.argv[1]) if len(sys.argv) > 1 else 2048
SAIDA = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saida')
REASSAR = [g for g in os.environ.get('REASSAR', '').split(',') if g]
ORIGEM = (-182, -93, 0)          # ponto do punho na origem, como nas outras armas


def material_final(g, pasta):
    m = bpy.data.materials.new(f'm4a1_{g}')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    def tex(suf, cs):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(os.path.join(pasta, f'm4a1_{g}_{suf}.png'))
        n.image.colorspace_settings.name = cs
        return n
    nt.links.new(tex('cor', 'sRGB').outputs[0], b.inputs['Base Color'])
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    nt.links.new(tex('orm', 'Non-Color').outputs[0], sep.inputs[0])
    nt.links.new(sep.outputs[1], b.inputs['Roughness'])
    nt.links.new(sep.outputs[2], b.inputs['Metallic'])
    nm = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(tex('normal', 'Non-Color').outputs[0], nm.inputs['Color'])
    nt.links.new(nm.outputs[0], b.inputs['Normal'])
    return m


def main():
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    modelo.montar()
    acessorios.montar()
    partes = list(PARTES)
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in partes)
    print(f'{len(partes)} peças, {tris} triângulos, {time.time() - t0:.0f}s', flush=True)
    grupos = {}
    for o in partes:
        grupos.setdefault(o['grupo'], []).append(o)
    texturas.preparar_materiais()
    pasta = os.path.join(SAIDA, 'tex')
    for g, objs in sorted(grupos.items()):
        texturas.desdobrar(objs)
        if os.path.exists(os.path.join(pasta, f'm4a1_{g}_cor.png')) and g not in REASSAR:
            print(f'grupo {g}: texturas reaproveitadas', flush=True)
            continue
        passes = texturas.assar(objs, RES)
        texturas.salvar(passes, os.path.join(pasta, f'm4a1_{g}'))
        print(f'grupo {g}: {len(objs)} peças assadas, {time.time() - t0:.0f}s', flush=True)
    for g, objs in grupos.items():
        m = material_final(g, pasta)
        for o in objs:
            o.data.materials.clear()
            o.data.materials.append(m)
            for p in o.data.polygons:
                p.material_index = 0
    raiz = bpy.data.objects.new('m4a1', None)
    bpy.context.scene.collection.objects.link(raiz)
    raiz.location = P(*ORIGEM)
    bpy.context.view_layer.update()
    for o in partes:
        if o.parent is None:
            o.parent = raiz
            o.matrix_parent_inverse = raiz.matrix_world.inverted()
    raiz.location = (0, 0, 0)
    bpy.context.view_layer.update()
    import bmesh
    for o in partes:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(o.data)
        bm.free()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, 'm4a1.blend'))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(SAIDA, 'm4a1_sem_tex.glb'), export_format='GLB',
                              export_image_format='NONE', export_tangents=True, export_yup=True,
                              export_apply=True, export_extras=False, export_animations=False)
    print(f'pronto em {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
