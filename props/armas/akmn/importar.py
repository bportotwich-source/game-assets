"""Importa o AKMN e o AKMN tático (FBX de suspensy, CC BY 4.0) e prepara tudo para ../m4a1/fabrica.py:
<saida>/akmn.blend (corpo com as partes móveis), <saida>/<id>.blend de cada acessório, as texturas em
<saida>/tex (cor, ORM e normal OpenGL) e, aqui na pasta, esqueleto.json (nós e animações do Brasa
7,62 levados para as medidas do AKMN) e os esqueletos dos acessórios.

uso: python3 importar.py <akm.fbx> <akm_zntc2.fbx> <saida>
(os FBX vêm de source/akm_2026.zip e source/akm.zip dos downloads do Sketchfab; as texturas ficam em
 textures/ ao lado de cada FBX)
"""
import sys, os, json, math
import numpy as np
from config import AQUI, ARMAS, PECAS_AKMN, PECAS_ZEN, ACESSORIOS, ler
import bpy, bmesh
from mathutils import Matrix, Vector
from PIL import Image
import fabrica

MATS_AKMN = ['receiver', 'barrel', 'akmDc', 'akmMag', 'wHg', 'wStock']
MATS_ZEN = ['pt1', 'liderhg', 'zenitcoacs1', 'rk3a', 'uspalmMag', 'b13']


def texturas(pasta_src, mats, saida):
    os.makedirs(saida, exist_ok=True)
    for m in mats:
        f = lambda s: os.path.join(pasta_src, f'{m}_{s}.png')
        cor = Image.open(f('BaseColor')).convert('RGB')
        cor.save(os.path.join(saida, f'akmn_{m}_cor.png'))
        cinza = lambda s: np.asarray(Image.open(f(s)).convert('L').resize(cor.size, Image.LANCZOS))
        orm = np.stack([cinza('AO'), cinza('Roughness'), cinza('Metallic')], -1)
        Image.fromarray(orm).save(os.path.join(saida, f'akmn_{m}_orm.png'))
        n = np.asarray(Image.open(f('Normal_DirectX')).convert('RGB').resize(cor.size, Image.LANCZOS)).copy()
        n[..., 1] = 255 - n[..., 1]                         # DirectX -> OpenGL (glTF)
        Image.fromarray(n).save(os.path.join(saida, f'akmn_{m}_normal.png'))
        print('textura', m, cor.size, flush=True)


def base(nome):
    """'receiver.024_low.001BAKE.004' -> 'receiver.024'; 'akmMag.001_low.003' -> 'akmMag'; 'npn2_low.010' -> 'npn2'."""
    n = nome.split('_low')[0]
    for k in ('barrel.002', 'barrel.004', 'barrel.006', 'receiver.006', 'receiver.017'):
        if n == k:
            return k
    return n.split('.')[0] if not n.startswith(('barrel.', 'receiver.')) else n


def importar(fbx):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx)
    objs = [o for o in bpy.data.objects if o.type == 'MESH']
    for o in objs:                                     # tudo no mundo, sem pais nem escala
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    for o in [o for o in bpy.data.objects if o.type != 'MESH']:
        bpy.data.objects.remove(o)
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return objs


def verts(objs):
    return np.concatenate([np.array([o.matrix_world @ v.co for v in o.data.vertices]) for o in objs])


def origem(punho):
    """Origem do jogo no sistema do FBX: centro do punho na altura do dedo médio, 84 mm abaixo do eixo do cano
    (a mesma altura do Brasa). Cano para -Y no FBX."""
    oz = 0.0855 - 0.084
    ys = []
    for o in punho:                                    # corte das arestas do punho no plano z = oz
        for e in o.data.edges:
            a, b = (o.matrix_world @ o.data.vertices[i].co for i in e.vertices)
            if (a.z - oz) * (b.z - oz) < 0:
                ys.append(a.y + (oz - a.z) / (b.z - a.z) * (b.y - a.y))
    return Vector((0.0, 0.5 * (min(ys) + max(ys)), oz))


def para_jogo(objs, O):
    """FBX (cano -Y) -> Blender do jogo (cano +Y, direito +X, origem no punho)."""
    M = Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Translation(-O)
    for o in objs:
        o.data.transform(M)
        o.matrix_world = Matrix.Identity(4)


DECIMAR = {'receiver.015': 0.25, 'lider': 0.4, 'b13': 0.6, 'pt1': 0.6}   # mola por dentro da tampa e peças táticas muito densas


def decimar(o):
    r = DECIMAR.get(base(o.name))
    if not r:
        return
    d = o.modifiers.new('d', 'DECIMATE')
    d.ratio = r
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier='d')


def juntar(objs, nome):
    for o in objs:
        decimar(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = o.data.name = nome
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for uv in list(o.data.uv_layers)[1:]:              # só o primeiro UV (a coronha tática traz dois)
        o.data.uv_layers.remove(uv)
    at = o.data.attributes.new('gravacao', 'INT', 'FACE')
    at.data.foreach_set('value', [0] * len(o.data.polygons))
    return o


def materiais(objs, tex):
    feitos = {}
    for o in objs:
        for i, m in enumerate(o.data.materials):
            nome = m.name.split('.')[0]
            if nome not in feitos:
                feitos[nome] = fabrica.material_final('akmn', nome, tex)
            o.data.materials[i] = feitos[nome]


def salvar(pecas, raiz_nome, deslocar, arq):
    """Cena só com as peças dadas, filhas de um vazio na origem; deslocar = ponto do encaixe (Blender do jogo)."""
    for o in list(bpy.data.objects):
        if o not in pecas:
            bpy.data.objects.remove(o)
    raiz = bpy.data.objects.new(raiz_nome, None)
    bpy.context.scene.collection.objects.link(raiz)
    for o in pecas:
        o.data.transform(Matrix.Translation(-Vector(deslocar)))
        o.parent = raiz
    bpy.ops.wm.save_as_mainfile(filepath=arq)


REASSAR = {'punho': 512, 'freio': 256, 'guarda_mao': 1024}     # acessórios que usam o conjunto do receptor/cano: textura própria


def reassar(o, res, tex):
    """Desdobra a peça de novo e assa cor, ORM e normal das texturas originais num conjunto só dela
    (akmn_<peça>_*.png), para o acessório não carregar o conjunto 2048 do corpo."""
    from fabrica import _emissor, _bsdf
    import texturas as tx
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.duplicate()
    b = bpy.context.view_layer.objects.active
    b.name = o.name + '_novo'
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin=0.006)
    bpy.ops.object.mode_set(mode='OBJECT')
    ml = bpy.data.materials.new('alvo')
    ml.use_nodes = True
    no = ml.node_tree.nodes.new('ShaderNodeTexImage')
    img = bpy.data.images.new('alvo', res, res, alpha=False, float_buffer=True)
    img.colorspace_settings.name = 'Non-Color'
    no.image = img
    ml.node_tree.nodes.active = no
    b.data.materials.clear()
    b.data.materials.append(ml)
    for p in b.data.polygons:
        p.material_index = 0
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 4; sc.cycles.use_denoising = False
    bk = sc.render.bake
    bk.margin = 6; bk.use_clear = True; bk.use_selected_to_active = True; bk.cage_extrusion = 0.0008; bk.max_ray_distance = 0.002
    o.select_set(True); b.select_set(True)
    bpy.context.view_layer.objects.active = b
    mats = [m for m in o.data.materials if m]
    passes = {}
    for nome, suf in (('cor', '_cor'), ('orm', '_orm'), ('normal', None)):
        for m in mats:
            _emissor(m, suf) if suf else _bsdf(m)
        bpy.ops.object.bake(type='EMIT' if suf else 'NORMAL')
        a = np.empty(res * res * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        passes[nome] = a.reshape(res, res, 4)[::-1, :, :3].copy()
    for m in mats:
        _bsdf(m)
    u8 = lambda x: (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
    g = o.name
    Image.fromarray(u8(tx.srgb(passes['cor']))).save(os.path.join(tex, f'akmn_{g}_cor.png'))
    Image.fromarray(u8(passes['orm'])).save(os.path.join(tex, f'akmn_{g}_orm.png'))
    Image.fromarray(u8(passes['normal'])).save(os.path.join(tex, f'akmn_{g}_normal.png'))
    b.data.materials.clear()
    b.data.materials.append(fabrica.material_final('akmn', g, tex))
    bpy.data.objects.remove(o)
    b.name = b.data.name = g
    print('reassado', g, res, flush=True)
    return b


G = lambda p: [round(float(p[0]), 4), round(float(p[2]), 4), round(float(-p[1]), 4)]    # Blender -> glTF


def medir(P):
    """Pivôs e encaixes medidos na malha (Blender do jogo: X direita, Y frente, Z cima)."""
    v = {k: verts([o]) for k, o in P.items()}
    corpo = v['corpo']
    M = {}
    # tampa: frente embaixo; gatilho: perto do topo da tecla; seletor: ponta de trás da alavanca
    t = v['tampa']; M['tampa'] = (0, t[:, 1].max(), t[:, 2].min())
    g = v['gatilho']; M['gatilho'] = (0, 0.5 * (g[:, 1].min() + g[:, 1].max()), g[:, 2].max() - 0.006)
    s = v['seletor']; fs = s[s[:, 1] < s[:, 1].min() + 0.012]
    M['seletor'] = (0.0, s[:, 1].min() + 0.006, 0.5 * (fs[:, 2].min() + fs[:, 2].max()))
    c = v['carregador']; topo = c[c[:, 2] > c[:, 2].max() - 0.012]
    M['carregador'] = (0, topo[:, 1].max(), c[:, 2].max() - 0.02)        # gancho da frente, perto do topo
    M['encaixe_carregador'] = M['carregador']
    # cano: boca sem o freio; freio vai até a boca de fogo
    cano = corpo[(np.abs(corpo[:, 0]) < 0.012) & (np.abs(corpo[:, 2] - 0.084) < 0.012)]
    fr = v['freio']
    M['encaixe_boca'] = (0, fr[:, 1].min() + 0.0005, 0.084)
    M['boca_fogo'] = (0, fr[:, 1].max(), 0.084)
    # coronha: fim de trás do receptor (sem o rabo que entra na coronha), na altura do eixo
    M['encaixe_coronha'] = (0, t[:, 1].min(), 0.085)     # fim de trás da tampa = fim do receptor
    # guarda-mão: fim de trás do guarda-mão de madeira, na altura do eixo
    gm = v['guarda_mao']
    M['encaixe_guarda_mao'] = (0, gm[:, 1].min(), 0.084)
    gl = v['guarda_mao_longo']
    zl = gl[:, 1].min() + 0.6 * (gl[:, 1].max() - gl[:, 1].min()) / 2
    bt = v['batente']
    M['encaixe_empunhadura'] = (0, 0.5 * (bt[:, 1].min() + bt[:, 1].max()), gl[:, 2].min())
    M['encaixe_lanterna'] = (gl[:, 0].max(), zl, 0.0855)
    M['encaixe_laser'] = (gl[:, 0].min(), zl, 0.0855)
    M['encaixe_enfeite'] = (0, 0.5 * (gm[:, 1].min() + gm[:, 1].max()), 0.0865)
    # trilho lateral (cauda de andorinha) do lado esquerdo: face do receptor, no meio do trilho
    lado = corpo[(corpo[:, 0] < -0.021) & (corpo[:, 2] > 0.045) & (corpo[:, 2] < 0.095)]
    M['encaixe_mira'] = (-0.0165, 0.5 * (lado[:, 1].min() + lado[:, 1].max()), 0.5 * (lado[:, 2].min() + lado[:, 2].max()))
    b13 = v['trilho_lateral']
    M['encaixe_mira_trilho'] = (0, 0.5 * (b13[:, 1].min() + b13[:, 1].max()), b13[:, 2].max())
    M['encaixe_mira_tampa'] = (0, M['tampa'][1] - 0.113, M['tampa'][2] + 0.0255)   # como no Brasa: em cima da tampa com trilho
    M['encaixe_tampa'] = M['tampa']
    M['encaixe_punho'] = (0, 0.0, 0.0)
    bo = M['encaixe_boca']
    M['encaixe_baioneta'] = (0, bo[1] - 0.061, 0.0745)
    M['encaixe_bandoleira'] = (-0.0098, bo[1] - 0.061, 0.0745)
    # saída do estojo: janela do lado direito, embaixo da tampa
    M['saida_estojo'] = (0.0138, M['tampa'][1] - 0.033, 0.1)
    # mira de ferro: fundo do entalhe da alça (peça de trás do bloco da alça) na altura do topo da massa
    massa = corpo[(np.abs(corpo[:, 0]) < 0.004) & (corpo[:, 1] > fr[:, 1].min() - 0.05) & (corpo[:, 2] > 0.12)]
    alca = corpo[(np.abs(corpo[:, 0]) < 0.016) & (corpo[:, 2] > 0.124) & (corpo[:, 1] > M['tampa'][1]) & (corpo[:, 1] < M['tampa'][1] + 0.03)]
    M['mira_ferro'] = (0, alca[:, 1].min(), massa[:, 2].max() - 0.0005)
    return {k: G(p) for k, p in M.items()}


def esqueleto(M):
    """Nós e animações do Brasa (brasa/esqueleto.json) com as posições do AKMN; as faixas de translação de cada nó
    andam junto com ele (as animações gravam posições absolutas)."""
    br = json.load(open(os.path.join(ARMAS, 'brasa', 'esqueleto.json'), encoding='utf-8'))
    nos, delta = [], {}
    for n in br['nos']:
        p = n['posicao'] if n['pai'] else M.get(n['no'], n['posicao'])
        if n['no'] == 'ferrolho':
            p = n['posicao']
        delta[n['no']] = [a - b for a, b in zip(p, n['posicao'])]
        nos.append({'no': n['no'], 'pai': n['pai'], 'posicao': p})
        if n['no'] == 'encaixe_mira_tampa':
            nos.append({'no': 'encaixe_mira_trilho', 'pai': None, 'posicao': M['encaixe_mira_trilho']})
    nos.append({'no': 'encaixe_punho', 'pai': None, 'posicao': [0.0, 0.0, 0.0]})
    anims = []
    for a in br['animacoes']:
        fx = []
        for f in a['faixas']:
            f = dict(f)
            if f['caminho'] == 'translation' and f['no']:
                d = delta[f['no']]
                f['v'] = [[round(x + dx, 6) for x, dx in zip(k, d)] for k in f['v']]
            fx.append(f)
        anims.append({'nome': a['nome'], 'faixas': fx})
    return {'origem': 'brasa/esqueleto.json + medidas do AKMN', 'nos': nos, 'animacoes': anims}


def main(fbx_akmn, fbx_zen, saida):
    tex = os.path.join(saida, 'tex')
    texturas(os.path.join(os.path.dirname(fbx_akmn), 'textures'), MATS_AKMN, tex)
    texturas(os.path.join(os.path.dirname(fbx_zen), 'textures'), MATS_ZEN, tex)

    def carregar(fbx, tabela, so_tabela):
        objs = importar(fbx)
        grupos = {}
        for o in objs:
            k = tabela.get(base(o.name), None if so_tabela else 'corpo')
            if k:
                grupos.setdefault(k, []).append(o)
            else:
                bpy.data.objects.remove(o)
        return grupos

    # 1) mede tudo numa cena com o AKMN e as peças táticas juntas
    medidas = {}
    for passo in ('medir', 'akmn', 'zen'):
        if passo in ('medir', 'akmn'):
            gr = carregar(fbx_akmn, PECAS_AKMN, False)
            O = origem(gr['punho'])
            todos = [o for l in gr.values() for o in l]
            para_jogo(todos, O)
            P = {k: juntar(l, k) for k, l in gr.items()}
        if passo == 'medir':
            bpy.ops.import_scene.fbx(filepath=fbx_zen)
            zen = {}
            for o in [o for o in bpy.data.objects if o.type == 'MESH' and o.name not in P]:
                k = PECAS_ZEN.get(base(o.name))
                if k:
                    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
                    zen.setdefault(k, []).append(o)
            for l in zen.values():
                bpy.ops.object.select_all(action='DESELECT')
                for o in l:
                    o.select_set(True)
                bpy.context.view_layer.objects.active = l[0]
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            para_jogo([o for l in zen.values() for o in l], O)
            P.update({k: juntar(l, k) for k, l in zen.items()})
            medidas = medir(P)
            json.dump(medidas, open(os.path.join(AQUI, 'medidas.json'), 'w'), indent=1)
            json.dump(esqueleto(medidas), open(os.path.join(AQUI, 'esqueleto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            print('origem no FBX', tuple(round(x, 4) for x in O))
            for k, p in medidas.items():
                print(f'  {k:22s} {p}')
            continue
        if passo == 'zen':
            gr = carregar(fbx_zen, PECAS_ZEN, True)
            todos = [o for l in gr.values() for o in l]
            for l in gr.values():
                bpy.ops.object.select_all(action='DESELECT')
                for o in l:
                    o.select_set(True)
                bpy.context.view_layer.objects.active = l[0]
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            para_jogo(todos, O)
            P = {k: juntar(l, k) for k, l in gr.items()}
        materiais(list(P.values()), tex)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(saida, f'_{passo}_tudo.blend'))
        # acessórios: cada um num .blend, com a origem no encaixe
        for k, o in P.items():
            if k not in ACESSORIOS:
                continue
            a = ACESSORIOS[k]
            bpy.ops.wm.open_mainfile(filepath=os.path.join(saida, f'_{passo}_tudo.blend'))
            o = bpy.data.objects[k]
            if k in REASSAR:
                o = reassar(o, REASSAR[k], tex)
            pg = medidas[a['no']]
            pb = (pg[0], -pg[2], pg[1])                    # glTF -> Blender
            salvar([o], a['id'], pb, os.path.join(saida, f"{a['id']}.blend"))
            v = verts([o])
            nos = []
            if a['categoria'] == 'coronha':                # ponto da soleira (como a coronha do Brasa)
                zmax = v[:, 1].min(); f = v[v[:, 1] < zmax + 0.006]
                nos.append({'no': 'ombro', 'pai': None, 'posicao': G((0, zmax, 0.5 * (f[:, 2].min() + f[:, 2].max())))})
            json.dump({'origem': 'akmn', 'nos': nos, 'animacoes': []},
                      open(os.path.join(AQUI, f"esqueleto_{a['id']}.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        if passo == 'akmn':
            bpy.ops.wm.open_mainfile(filepath=os.path.join(saida, '_akmn_tudo.blend'))
            salvar([bpy.data.objects[k] for k in ('corpo', 'tampa', 'gatilho', 'seletor', 'ferrolho', 'carregador')],
                   'akmn', (0, 0, 0), os.path.join(saida, 'akmn.blend'))
    print('pronto')


if __name__ == '__main__':
    main(*sys.argv[1:4])
