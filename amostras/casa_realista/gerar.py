"""Gera a amostra: modelo, UVs, bake das texturas e GLB (sem imagens; empacotar.py coloca as texturas).
uso: python3 gerar.py [saída] [escala de resolução]
Um grupo que já tem as texturas na pasta de saída não é assado de novo; REASSAR=A,B força os grupos listados."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import modelo, texturas, lib

SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saida')
ESC = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
REASSAR = [g for g in os.environ.get('REASSAR', '').split(',') if g]
SO = [g for g in os.environ.get('SO', '').split(',') if g]
# grupo de textura: resolução. A/B paredes da fachada, C folhas (porta, janela), D piso, E parede interna, F cômoda, G itens
RES = dict(A=4096, B=4096, C=2048, D=4096, E=2048, F=2048, G=2048)


def material_final(g, pasta, vidro=False):
    m = bpy.data.materials.new(f'casa_{g}' + ('_vidro' if vidro else ''))
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    def tex(suf, cs):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(os.path.join(pasta, f'casa_{g}_{suf}.png'))
        n.image.colorspace_settings.name = cs
        return n
    c = tex('cor', 'sRGB')
    nt.links.new(c.outputs[0], b.inputs['Base Color'])
    if vidro:
        nt.links.new(c.outputs[1], b.inputs['Alpha'])
        m.blend_method = 'BLEND'
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
    partes = list(modelo.construir())
    info = {o.name: dict(tris=lib.tris(o), grupo=o['grupo']) for o in partes}
    print(f'{len(partes)} peças, {sum(i["tris"] for i in info.values())} triângulos', flush=True)
    grupos = {}
    for o in partes:
        grupos.setdefault(o['grupo'], []).append(o)
    texturas.preparar_materiais()
    pasta = os.path.join(SAIDA, 'tex')
    for g, objs in sorted(grupos.items()):
        texturas.desdobrar(objs)
        res = max(256, int(RES[g] * ESC))
        if SO and g not in SO:
            continue
        if os.path.exists(os.path.join(pasta, f'casa_{g}_cor.png')) and g not in REASSAR:
            print(f'grupo {g}: texturas reaproveitadas', flush=True)
            continue
        passes = texturas.assar(objs, res)
        texturas.salvar(passes, os.path.join(pasta, f'casa_{g}'))
        print(f'grupo {g}: {len(objs)} peças assadas a {res} px, {time.time() - t0:.0f}s', flush=True)
    if SO:
        return
    for g, objs in grupos.items():
        m, mv = material_final(g, pasta), None
        for o in objs:
            vid = [i for i, mm in enumerate(o.data.materials) if mm and mm.name == 'vidro']
            ev = [p.material_index in vid for p in o.data.polygons]
            o.data.materials.clear()
            o.data.materials.append(m)
            if any(ev):
                mv = mv or material_final(g, pasta, True)
                o.data.materials.append(mv)
            for p, v in zip(o.data.polygons, ev):
                p.material_index = 1 if v else 0
    for o in partes:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(o.data)
        bm.free()
        if 'veio' in o.data.color_attributes:
            o.data.color_attributes.remove(o.data.color_attributes['veio'])
    os.makedirs(SAIDA, exist_ok=True)
    json.dump(info, open(os.path.join(SAIDA, 'pecas.json'), 'w'), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, 'casa.blend'))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(SAIDA, 'casa_sem_tex.glb'), export_format='GLB',
                              export_image_format='NONE', export_tangents=True, export_yup=True,
                              export_apply=True, export_extras=True, export_animations=False)
    print(f'pronto em {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
