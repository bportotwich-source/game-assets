"""O que é igual para toda arma refeita no método da M4A1 (ver guardia/ e sentinela/):
gerar() monta, desdobra e assa; jogo() grava o GLB do jogo com os nós e as animações da
arma antiga, a versão leve (uma malha, 1 conjunto 1024) e o registro no catálogo.

cfg = dict(nome='guardia',                 # prefixo dos arquivos (guardia.blend, guardia_A_cor.png)
           montar=modelo.montar,           # cria as peças (lib.parte)
           origem=(4, -68, 0),             # ponto do projeto (mm) que vira a origem da arma (o punho)
           esqueleto=json de tirar_esqueleto.py,
           nos={None: [peças na raiz], 'ferrolho': [...]},     # peças de cada nó
           variantes={'': (id, descrição), 'preta': (id, descrição)},
           gerador='guardia/jogo.py', tris_leve=6000)
"""
import sys, os, json, math, time
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [p for p in (AQUI, ARMAS) if p not in sys.path]
import bpy
import numpy as np
from mathutils import Matrix, Vector
import empacotar
import pontos_ref


# ------------------------------------------------------------------ modelo e bake
def material_final(nome, g, pasta):
    m = bpy.data.materials.new(f'{nome}_{g}')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    def tex(suf, cs):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(os.path.join(pasta, f'{nome}_{g}_{suf}.png'))
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


def gerar(cfg, res=2048, saida='saida'):
    """Monta (cfg['montar']), desdobra, assa cada grupo de textura e salva <nome>.blend em saida."""
    import texturas
    from lib import PARTES, P
    nome = cfg['nome']
    reassar = [g for g in os.environ.get('REASSAR', '').split(',') if g]
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cfg['montar']()
    partes = list(PARTES)
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in partes)
    print(f'{len(partes)} peças, {tris} triângulos, {time.time() - t0:.0f}s', flush=True)
    grupos = {}
    for o in partes:
        grupos.setdefault(o['grupo'], []).append(o)
    texturas.preparar_materiais()
    pasta = os.path.join(saida, 'tex')
    for g, objs in sorted(grupos.items()):
        texturas.desdobrar(objs)
        if os.path.exists(os.path.join(pasta, f'{nome}_{g}_cor.png')) and g not in reassar:
            print(f'grupo {g}: texturas reaproveitadas', flush=True)
            continue
        passes = texturas.assar(objs, res)
        texturas.salvar(passes, os.path.join(pasta, f'{nome}_{g}'))
        print(f'grupo {g}: {len(objs)} peças assadas, {time.time() - t0:.0f}s', flush=True)
    for g, objs in grupos.items():
        m = material_final(nome, g, pasta)
        for o in objs:
            # marca as gravações e os pontos pintados (a versão leve tira essas faces: lá elas vêm só pela textura)
            at = o.data.attributes.new('gravacao', 'INT', 'FACE')
            tinta = [i for i, x in enumerate(o.data.materials) if x and x.name.startswith('tinta')]
            at.data.foreach_set('value', [int(p.material_index in tinta) for p in o.data.polygons])
            o.data.materials.clear()
            o.data.materials.append(m)
            for p in o.data.polygons:
                p.material_index = 0
    raiz = bpy.data.objects.new(nome, None)
    bpy.context.scene.collection.objects.link(raiz)
    raiz.location = P(*cfg['origem'])
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(saida, f'{nome}.blend'))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(saida, f'{nome}_sem_tex.glb'), export_format='GLB',
                              export_image_format='NONE', export_tangents=True, export_yup=True,
                              export_apply=True, export_extras=False, export_animations=False)
    print(f'pronto em {time.time() - t0:.0f}s')


# ------------------------------------------------------------------ versão de jogo
EXPORTAR = dict(export_format='GLB', export_image_format='NONE', export_tangents=True, export_yup=True, export_apply=True,
                export_extras=False, export_animations=False)


def montar_cena(cfg, ID, blend):
    bpy.ops.wm.open_mainfile(filepath=blend)
    raiz = bpy.data.objects[cfg['nome']]
    raiz.name = ID
    bpy.context.view_layer.update()
    pecas = {o.name: o for o in bpy.data.objects if o.type == 'MESH'}
    mundo = {n: o.matrix_world.copy() for n, o in pecas.items()}
    for n, o in pecas.items():                         # libera os nomes para os nós (gatilho, cano, ferrolho...)
        o.name = o.data.name = f'{ID}_{n}'
    nos = {None: raiz}
    for n in cfg['esqueleto']['nos']:                       # pais vêm antes dos filhos na lista
        e = bpy.data.objects.new(n['no'], None)
        bpy.context.scene.collection.objects.link(e)
        e.parent = nos[n['pai']]
        e.matrix_parent_inverse = Matrix.Identity(4)
        x, y, z = n['posicao']
        e.location = (x, -z, y)                        # glTF (y para cima) -> Blender (z para cima)
        nos[n['no']] = e
    bpy.context.view_layer.update()
    usadas = set()
    for no, nomes in cfg['nos'].items():
        for nome in nomes:
            o = pecas[nome]
            o.parent = nos[no]
            o.matrix_parent_inverse = Matrix.Identity(4)
            o.matrix_world = mundo[nome]
            usadas.add(nome)
    assert usadas == set(pecas), set(pecas) - usadas
    bpy.context.view_layer.update()


def animar(cfg, ID, arq):
    j, bin_ = empacotar.ler_glb(arq)
    idx = {n.get('name'): i for i, n in enumerate(j['nodes'])}
    j['animations'] = []

    def put(arr, tipo):
        while len(bin_) % 4:
            bin_.append(0)
        a = np.asarray(arr, np.float32)
        j['bufferViews'].append({'buffer': 0, 'byteOffset': len(bin_), 'byteLength': a.nbytes})
        bin_.extend(a.tobytes())
        acc = {'bufferView': len(j['bufferViews']) - 1, 'componentType': 5126, 'count': int(a.shape[0]), 'type': tipo}
        if tipo == 'SCALAR':
            acc['min'], acc['max'] = [float(a.min())], [float(a.max())]
        j['accessors'].append(acc)
        return len(j['accessors']) - 1

    esq = cfg['esqueleto']
    for n in esq['nos']:                               # as animações gravam posições absolutas: os nós têm de estar no lugar de antes
        t = j['nodes'][idx[n['no']]].get('translation', [0, 0, 0])
        assert max(abs(a - b) for a, b in zip(t, n['posicao'])) < 1e-5, (n['no'], t)
        assert 'rotation' not in j['nodes'][idx[n['no']]], n['no']
    for a in esq['animacoes']:
        an = {'name': a['nome'], 'samplers': [], 'channels': []}
        for f in a['faixas']:
            tipo = 'VEC3' if f['caminho'] == 'translation' else 'VEC4'
            an['samplers'].append({'input': put(f['t'], 'SCALAR'), 'output': put(f['v'], tipo), 'interpolation': f['interp']})
            an['channels'].append({'sampler': len(an['samplers']) - 1, 'target': {'node': idx[f['no'] or ID], 'path': f['caminho']}})
        j['animations'].append(an)
    empacotar.gravar_glb(arq, j, bin_)


VIDRO = {'name': 'vidro', 'alphaMode': 'BLEND', 'doubleSided': True,
         'pbrMetallicRoughness': {'baseColorFactor': [0.667, 0.804, 0.765, 0.102], 'metallicFactor': 0.0, 'roughnessFactor': 0.05}}


def aceso(nome, cor):
    """Material liso que brilha sozinho (fibra óptica, lâmpada)."""
    return {'name': nome, 'emissiveFactor': list(cor), 'pbrMetallicRoughness': {'baseColorFactor': [*cor, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.3}}


def materiais_lisos(arq, malhas):
    """Troca o material assado das malhas dadas ({malha: material glTF}) por um liso: vidro transparente
    (lente de mira de ponto, vê-se através) ou peça acesa."""
    j, bin_ = empacotar.ler_glb(arq)
    achadas = set()
    for m in j['meshes']:
        if m.get('name') in malhas:
            j['materials'].append(dict(malhas[m['name']]))
            for p in m['primitives']:
                p['material'] = len(j['materials']) - 1
                p['attributes'] = {k: v for k, v in p['attributes'].items() if not k.startswith('TEXCOORD') and k != 'TANGENT'}
            achadas.add(m['name'])
    assert achadas == set(malhas), (set(malhas) - achadas, [m.get('name') for m in j['meshes']])
    empacotar.gravar_glb(arq, j, bin_)


# ------------------------------------------------------------------ versão leve
def _emissor(m, sufixo):
    """Liga a textura <sufixo> do material ao emissor (para assar cor e ORM da malha detalhada na leve)."""
    nt = m.node_tree
    img = next(n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name.split('.')[0].endswith(sufixo))
    em = nt.nodes.get('emissor') or nt.nodes.new('ShaderNodeEmission')
    em.name = 'emissor'
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    nt.links.new(img.outputs[0], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])


def _bsdf(m):
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    nt.links.new(nt.nodes['Principled BSDF'].outputs[0], out.inputs[0])


def leve(cfg, ID, blend, pasta_tex, res=1024):
    """Uma malha só com cerca de cfg['tris_leve'] triângulos e as texturas da detalhada assadas num conjunto."""
    import bmesh
    from PIL import Image
    bpy.ops.wm.open_mainfile(filepath=blend)
    raiz = bpy.data.objects[cfg['nome']]
    malhas = [o for o in bpy.data.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in malhas:
        o.select_set(True)
    bpy.context.view_layer.objects.active = malhas[0]
    bpy.ops.object.duplicate()
    copias = list(bpy.context.selected_objects)
    bpy.context.view_layer.objects.active = copias[0]
    bpy.ops.object.join()
    alta = bpy.context.view_layer.objects.active
    alta.name = 'alta'
    mw = alta.matrix_world.copy()
    alta.parent = None
    alta.matrix_world = mw
    for o in malhas:
        bpy.data.objects.remove(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # leve: cópia sem as gravações (entram pela textura), soldada e decimada
    bpy.ops.object.duplicate()
    bx = bpy.context.view_layer.objects.active
    bx.name = bx.data.name = f'{ID}_leve'
    bm = bmesh.new()
    bm.from_mesh(bx.data)
    marca = bm.faces.layers.int['gravacao']
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[marca]], context='FACES')
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-5)
    bm.to_mesh(bx.data)
    bm.free()
    tris = sum(len(p.vertices) - 2 for p in bx.data.polygons)
    d = bx.modifiers.new('d', 'DECIMATE')
    d.ratio = cfg.get('tris_leve', 6000) / tris
    bpy.ops.object.modifier_apply(modifier='d')
    for p in bx.data.polygons:
        p.use_smooth = True
    bx.data.set_sharp_from_angle(angle=math.radians(40))
    bpy.ops.object.select_all(action='DESELECT')
    bx.select_set(True)
    bpy.context.view_layer.objects.active = bx
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(62), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin=0.004)
    bpy.ops.object.mode_set(mode='OBJECT')
    ml = bpy.data.materials.new(f"{cfg['nome']}_L")
    ml.use_nodes = True
    alvo = ml.node_tree.nodes.new('ShaderNodeTexImage')
    img = bpy.data.images.new('alvo', res, res, alpha=False, float_buffer=True)
    img.colorspace_settings.name = 'Non-Color'
    alvo.image = img
    ml.node_tree.nodes.active = alvo
    bx.data.materials.clear()
    bx.data.materials.append(ml)
    for p in bx.data.polygons:
        p.material_index = 0
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 4
    sc.cycles.use_denoising = False
    bk = sc.render.bake
    bk.margin = 6
    bk.use_clear = True
    bk.use_selected_to_active = True
    bk.cage_extrusion = 0.0012
    bk.max_ray_distance = 0.004
    alta.select_set(True)
    bx.select_set(True)
    bpy.context.view_layer.objects.active = bx
    mats = [m for m in alta.data.materials if m]
    passes = {}
    for nome, suf in (('cor', '_cor'), ('orm', '_orm'), ('normal', None)):
        for m in mats:
            _emissor(m, suf) if suf else _bsdf(m)
        bpy.ops.object.bake(type='EMIT' if suf else 'NORMAL')
        a = np.empty(res * res * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        passes[nome] = a.reshape(res, res, 4)[::-1, :, :3].copy()
    import texturas
    u8 = lambda x: (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(u8(texturas.srgb(passes['cor']))).save(os.path.join(pasta_tex, f"{cfg['nome']}_L_cor.png"))
    Image.fromarray(u8(passes['orm'])).save(os.path.join(pasta_tex, f"{cfg['nome']}_L_orm.png"))
    Image.fromarray(u8(passes['normal'])).save(os.path.join(pasta_tex, f"{cfg['nome']}_L_normal.png"))
    bpy.data.objects.remove(alta)
    raiz.name = f'{ID}_leve'
    bx.parent = raiz
    bx.matrix_parent_inverse = Matrix.Identity(4)
    bm = bmesh.new()
    bm.from_mesh(bx.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(bx.data)
    bm.free()
    bpy.context.view_layer.update()


# ------------------------------------------------------------------ catálogo
def medir(arq):
    g = pontos_ref.Glb(arq)
    T = g.malha_tudo()
    v = T.reshape(-1, 3)
    return [round(float(x), 3) for x in (v.max(0) - v.min(0))], int(len(T))


def jogo(cfg, saida, fmt='webp'):
    """GLB do jogo (nós e animações de cfg['esqueleto']), versão leve e registro no catálogo.
    VARIANTE escolhe a entrada de cfg['variantes'] (id e descrição); o modelo é o mesmo, muda o bake."""
    var = os.environ.get('VARIANTE', '')
    ID, descricao = cfg['variantes'][var]
    blend = os.path.join(saida, f"{cfg['nome']}.blend")
    tex = os.path.join(saida, 'tex')
    montar_cena(cfg, ID, blend)
    tmp = os.path.join(saida, f'{ID}_sem_tex.glb')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=tmp, **EXPORTAR)
    arq = os.path.join(ARMAS, 'armas', f'{ID}.glb')
    empacotar.main(tmp, tex, arq, fmt)
    animar(cfg, ID, arq)
    leve(cfg, ID, blend, tex)
    tmp = os.path.join(saida, f'{ID}_leve_sem_tex.glb')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=tmp, **EXPORTAR)
    arq_l = os.path.join(ARMAS, 'armas', f'{ID}_leve.glb')
    empacotar.main(tmp, tex, arq_l, fmt)
    arq_cat = os.path.join(ARMAS, 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    r = next(x for x in cat['armas'] if x['id'] == ID)
    r['tamanho_m'], r['triangulos'] = medir(arq)
    tam_l, tris_l = medir(arq_l)
    r.update(gerador=cfg['gerador'], arquivo_leve=f'armas/{ID}_leve.glb', triangulos_leve=tris_l,
             kb_leve=round(os.path.getsize(arq_l) / 1024, 1), descricao=descricao)
    s = pontos_ref.aplicar_item(r, 'armas', {x['id']: x for x in cat['acessorios']})
    r['kb'] = round(os.path.getsize(arq) / 1024, 1)
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{ID} {r['triangulos']} tris {r['kb']} KB {r['tamanho_m']}  leve {tris_l} tris {r['kb_leve']} KB {tam_l}")
    print('  '.join(f"{p['no'][4:]}{p['posicao_m']}" for p in s))


def acessorio(cfg, saida, fmt='webp'):
    """GLB de um acessório refeito (cfg['id'] em acessorios/), com os nós e as animações do antigo
    (cfg['esqueleto']) e o registro no catálogo. Sem versão leve."""
    ID = cfg['id']
    G = cfg.get('grupo', 'acessorios')                 # 'municao' para flechas e virotes soltos
    montar_cena(cfg, ID, os.path.join(saida, f"{cfg['nome']}.blend"))
    tmp = os.path.join(saida, f'{ID}_sem_tex.glb')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=tmp, **EXPORTAR)
    arq = os.path.join(ARMAS, G, f'{ID}.glb')
    empacotar.main(tmp, os.path.join(saida, 'tex'), arq, fmt)
    animar(cfg, ID, arq)
    lisos = {p: VIDRO for p in cfg.get('vidro', [])}
    lisos.update(cfg.get('lisos', {}))                 # peças de material liso, sem textura: vidro, fibra acesa
    if lisos:
        materiais_lisos(arq, {f'{ID}_{p}': m for p, m in lisos.items()})
    arq_cat = os.path.join(ARMAS, 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    r = next(x for x in cat[G] if x['id'] == ID)
    r['tamanho_m'], r['triangulos'] = medir(arq)
    r.update(gerador=cfg['gerador'], descricao=cfg.get('descricao', r['descricao']))
    if cfg.get('optica'):                              # miras e lunetas: onde ficam as lentes (o jogo desenha o zoom por elas)
        r['optica'] = cfg['optica']
    pos = {n['no']: n['posicao'] for n in cfg['esqueleto']['nos']}
    for e in r.get('encaixes', []):                    # os encaixes do acessório seguem os nós novos
        if e['no'] in pos:
            e['posicao_m'] = pos[e['no']]
    s = pontos_ref.aplicar_item(r, G, {x['id']: x for x in cat[G]}) if G == 'acessorios' else None
    r['kb'] = round(os.path.getsize(arq) / 1024, 1)
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{ID} {r['triangulos']} tris {r['kb']} KB {r['tamanho_m']}")
    if s:
        print('  '.join(f"{p['no'][4:]}{p['posicao_m']}" for p in s))
