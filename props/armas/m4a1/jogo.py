"""Versões de jogo da M4A1, no padrão das outras armas de props/armas.

Parte do m4a1.blend que o gerar.py salva (todas as peças e acessórios, já com as
texturas) e grava um GLB por montagem em props/armas/armas/, com:
  - só as peças daquela montagem, cada uma no seu nó;
  - as peças móveis nos nós de nome padrão (gatilho, seletor, ferrolho, alavanca,
    tampa_janela, retem_ferrolho, carregador, punho);
  - os nós boca_fogo, saida_estojo, mira_ferro, encaixe_empunhadura e ombro;
  - as animações embutidas (atirar, atirar_ultimo, vazia, recarregar,
    recarregar_vazia, trocar_modo, ocioso);
  - os pontos ref_* das mãos, do ombro e do olho (pontos_ref.py).
Também põe as montagens no catalogo.json (campo "gerador": "m4a1/jogo.py", que o
gerar_armas.py preserva ao regerar tudo).

uso: python3 jogo.py saida [webp|jpg]      (saida = pasta do gerar.py, com m4a1.blend e tex/)
"""
import sys, os, json, math, struct
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [AQUI, ARMAS]
import bpy
import numpy as np
from mathutils import Matrix, Vector
import empacotar
import pontos_ref

MM = 0.001
ORIGEM = (-182, -93, 0)


def W(u, v, w=0.0):
    """Ponto de projeto (mm) -> coordenadas do Blender com a origem no punho."""
    return Vector((w * MM, (u - ORIGEM[0]) * MM, (v - ORIGEM[1]) * MM))


# peças de cada encaixe; o que não aparece aqui entra em todas as montagens
SLOTS = {
    'gm': {'classico': ['guarda_mao_superior', 'guarda_mao_inferior', 'anel_delta', 'tampa_guarda_mao', 'base_massa',
                        'pino_base_massa_1', 'pino_base_massa_2', 'pino_massa', 'zarelho_frontal'],
           'longo': ['guarda_mao_longo', 'porca_cano', 'bloco_gas']},
    'boca': {'quebra': ['quebra_chamas', 'arruela_boca'], 'supressor': ['supressor']},
    'mira': {'alca': ['alca_transporte', 'alca_mira', 'botao_deriva', 'tambor_elevacao', 'porca_alca_1', 'porca_alca_2'],
             'luneta': ['luneta', 'suporte_luneta'],
             'prisma': ['mira_prismatica', 'tampa_lente_frente', 'tampa_lente_tras', 'suporte_prismatica']},
    'reflex': {'sem': [], 'com': ['mira_reflex', 'suporte_45']},
    'laser': {'sem': [], 'com': ['modulo_laser']},
    'lanterna': {'sem': [], 'com': ['lanterna', 'trilho_esquerdo']},
    'emp': {'sem': [], 'angulada': ['empunhadura_angulada', 'trilho_baixo'], 'vertical': ['empunhadura_vertical', 'trilho_baixo']},
    'carr': {'metal': ['carregador', 'transportador', 'cartucho_1', 'cartucho_2'], 'polimero': ['carregador_polimero'],
             'tambor': ['carregador_tambor']},
    'punho': {'padrao': ['punho'], 'vazado': ['punho_vazado']},
    'alav': {'padrao': ['alavanca_manejo', 'trava_alavanca'], 'ambi': ['alavanca_ambi']},
    'tubo': {'preto': ['tubo_coronha'], 'vermelho': ['tubo_coronha_vermelho']},
    'cor': {'retratil': ['coronha', 'trava_coronha', 'zarelho_traseiro'], 'moderna': ['coronha_moderna', 'trava_coronha_moderna'],
            'fixa': ['coronha_fixa']},
}
RENOMEAR = {'alavanca_manejo': 'alavanca', 'alavanca_ambi': 'alavanca', 'carregador_polimero': 'carregador',
            'carregador_tambor': 'carregador', 'punho_vazado': 'punho', 'coronha_moderna': 'coronha', 'coronha_fixa': 'coronha',
            'trava_coronha_moderna': 'trava_coronha', 'tubo_coronha_vermelho': 'tubo_coronha'}
MOVEIS = ['punho', 'gatilho', 'seletor', 'ferrolho', 'alavanca', 'tampa_janela', 'retem_ferrolho', 'carregador']
JUNTO = {'trava_alavanca': 'alavanca', 'transportador': 'carregador', 'cartucho_1': 'carregador', 'cartucho_2': 'carregador'}

COMUM = dict(grupo='armas', categoria='fuzil', classe='fogo', calibre='5,56', municao='municao_556', dano=42, alcance_max_m=400,
             modo='semiautomático e automático (seletor)', tiros_por_s=11, recuo=0.35, durabilidade=3000, estojo_s=0.02)
MONTAGENS = {
    'fuzil_m4a1': dict(
        escolha=dict(gm='classico', boca='quebra', mira='alca', reflex='sem', laser='sem', lanterna='sem', emp='sem', carr='metal',
                     punho='padrao', alav='padrao', tubo='preto', cor='retratil'),
        mira=(-182, 56.3),
        dados=dict(nome='Fuzil M4A1', capacidade=30, alcance_m=80, recarga_s=2.2, recarga_vazia_s=2.6, precisao=0.8, ruido_m=160,
                   peso_kg=3.4, raridade='raro', valor_troca=180, onde=['quartel', 'delegacia'],
                   descricao='Fuzil 5,56 clássico e bem detalhado: alça de transporte com mira, guarda-mão de trilho quádruplo, '
                             'coronha retrátil e carregador de metal de 30. Cada peça é um nó próprio do modelo.')),
    'fuzil_m4a1_luneta': dict(
        escolha=dict(gm='longo', boca='supressor', mira='luneta', reflex='sem', laser='sem', lanterna='sem', emp='angulada',
                     carr='polimero', punho='padrao', alav='padrao', tubo='preto', cor='fixa'),
        mira=(-210, 68),
        dados=dict(nome='Fuzil M4A1 com luneta', variante_de='fuzil_m4a1', capacidade=30, alcance_m=140, recarga_s=2.2,
                   recarga_vazia_s=2.6, precisao=0.92, ruido_m=60, peso_kg=4.3, raridade='muito raro', valor_troca=260,
                   onde=['quartel', 'delegacia'],
                   descricao='A M4A1 montada para tiro de longe: guarda-mão longo vazado, supressor, luneta em suporte de peça única, '
                             'empunhadura angulada, carregador de polímero e coronha fixa. O supressor baixa o ruído para 60 m.')),
    'fuzil_m4a1_tatico': dict(
        escolha=dict(gm='longo', boca='supressor', mira='prisma', reflex='com', laser='com', lanterna='com', emp='vertical',
                     carr='tambor', punho='vazado', alav='ambi', tubo='vermelho', cor='moderna'),
        mira=(-154, 74),
        dados=dict(nome='Fuzil M4A1 tático', variante_de='fuzil_m4a1', apoio_vertical=True, capacidade=60, alcance_m=100, recarga_s=2.8,
                   recarga_vazia_s=3.2, precisao=0.85, ruido_m=60, peso_kg=5.2, raridade='muito raro', valor_troca=300,
                   onde=['quartel', 'delegacia'],
                   descricao='A M4A1 com tudo: guarda-mão longo, supressor, mira prismática com tampas, reflex a 45°, módulo laser, '
                             'lanterna, empunhadura vertical vazada, carregador de tambor de 60, punho vazado, alavanca ambidestra, '
                             'tubo vermelho e coronha moderna. Pesada, mas silenciosa e com muita munição.')),
}
PARTES = [
    dict(no='punho', tipo='troca', descricao='punho de pistola'),
    dict(no='gatilho', tipo='gira', eixo='x', curso_graus=-12, descricao='puxa para trás'),
    dict(no='seletor', tipo='gira', eixo='x', curso_graus=90, descricao='seguro / semi (90°) / auto (180°)'),
    dict(no='ferrolho', tipo='desliza', curso_m=-0.08, descricao='transportador: recua 80 mm a cada tiro; fica atrás com o carregador vazio'),
    dict(no='alavanca', tipo='desliza', curso_m=-0.065, descricao='alavanca de manejo (puxa e solta)'),
    dict(no='tampa_janela', tipo='gira', eixo='z', curso_graus=-110, descricao='abre no primeiro tiro e fica aberta'),
    dict(no='retem_ferrolho', tipo='gira', eixo='z', curso_graus=-8, descricao='retém do ferrolho (esquerda)'),
    dict(no='carregador', tipo='remove', direcao=[0, -1, 0], descricao='sai para baixo'),
]


# ------------------------------------------------------------------ cena
def _verts(o):
    return [o.matrix_world @ v.co for v in o.data.vertices]


def _vazio(nome, pos, pai):
    e = bpy.data.objects.new(nome, None)
    bpy.context.scene.collection.objects.link(e)
    e.parent = pai
    e.matrix_parent_inverse = Matrix.Identity(4)
    e.location = pos
    return e


def montar_cena(blend, id_, m):
    bpy.ops.wm.open_mainfile(filepath=blend)
    esc = m['escolha']
    fora = {n for s, ops in SLOTS.items() for k, ns in ops.items() if k != esc[s] for n in ns}
    raiz = bpy.data.objects['m4a1']
    bpy.context.view_layer.update()
    pecas = {}
    for o in list(bpy.data.objects):
        if o.type != 'MESH':
            continue
        if o.name in fora:
            mw = [(c, c.matrix_world.copy()) for c in o.children]
            for c, x in mw:                       # filhos de peça retirada sobem para a raiz
                c.parent = raiz
                c.matrix_parent_inverse = Matrix.Identity(4)
                c.matrix_world = x
            bpy.data.objects.remove(o)
        else:
            pecas[o.name] = o
    bpy.context.view_layer.update()
    for o in pecas.values():                      # tudo direto na raiz
        mw = o.matrix_world.copy()
        o.parent = raiz
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_world = mw
    raiz.name = id_
    bpy.context.view_layer.update()
    for velho, novo in RENOMEAR.items():
        if velho in pecas:
            pecas[novo] = pecas.pop(velho)
            pecas[novo].name = novo
    nos = {}
    for nome in MOVEIS:                           # nó vazio de nome padrão com a malha dentro
        o = pecas[nome]
        pos = o.location.copy()
        o.name = o.data.name = f'{id_}_{nome}'
        nos[nome] = e = _vazio(nome, pos, raiz)
        o.parent = e
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.location = (0, 0, 0)
    bpy.context.view_layer.update()
    for nome, pai in JUNTO.items():
        if nome in pecas:
            o = pecas[nome]
            mw = o.matrix_world.copy()
            o.parent = nos[pai]
            o.matrix_parent_inverse = Matrix.Identity(4)
            o.matrix_world = mw
    for nome, o in pecas.items():
        if nome not in MOVEIS:
            o.name = o.data.name = f'{id_}_{nome}'
    bpy.context.view_layer.update()
    # pontos do padrão
    boca = pecas['supressor' if esc['boca'] == 'supressor' else 'quebra_chamas']
    _vazio('boca_fogo', Vector((0, max(v.y for v in _verts(boca)), W(0, 0).z)), raiz)
    _vazio('saida_estojo', W(-67, 2, 15), raiz)
    _vazio('mira_ferro', W(*m['mira']), raiz)
    vs = _verts(pecas['coronha'])
    y0 = min(v.y for v in vs)
    zs = [v.z for v in vs if v.y < y0 + 0.006]
    _vazio('ombro', Vector((0, y0, 0.5 * (min(zs) + max(zs)))), raiz)
    if esc['emp'] == 'vertical':                  # a mão fecha no meio da empunhadura
        vs = _verts(pecas['empunhadura_vertical'])
        zm = 0.5 * (min(v.z for v in vs) + max(v.z for v in vs)) - 0.008
        ys = [v.y for v in vs if abs(v.z - zm) < 0.006]
        apoio = Vector((0, 0.5 * (min(ys) + max(ys)), zm))
    else:                                         # palma embaixo do guarda-mão ou da empunhadura angulada
        vs = _verts(pecas['empunhadura_angulada' if esc['emp'] == 'angulada' else 'guarda_mao_inferior'])
        ys = [v.y for v in vs]
        yc = 0.5 * (min(ys) + max(ys))
        apoio = Vector((0, yc, min(v.z for v in vs if abs(v.y - yc) < 0.02)))
    _vazio('encaixe_empunhadura', apoio, raiz)
    bpy.context.view_layer.update()


# ------------------------------------------------------------------ animações (pós-processa o GLB)
def _q(eixo, graus):
    h = math.radians(graus) / 2
    return [eixo[0] * math.sin(h), eixo[1] * math.sin(h), eixo[2] * math.sin(h), math.cos(h)]


X, Z = (1, 0, 0), (0, 0, 1)
ABERTA = -110          # tampa da janela aberta (graus em Z)


def animacoes(d):
    """nome -> (duração, laço, descrição, faixas). Faixa: (nó ou None para a raiz, 't' | 'r', eixo, [(tempo, valor)])."""
    cai = [(0, (0, 0, 0)), (0.35, (0, 0, 0)), (0.6, (0, -0.26, 0.03)), (1.3 * d, (0, -0.26, 0.03)), (1.72 * d, (0, 0, 0))]
    vira = [(0, 0), (0.25, 14), (1.8 * d, 14), (2.1 * d, 0)]
    tampa = ('tampa_janela', 'r', Z, [(0, ABERTA), (0.1, ABERTA)])
    return {
        'atirar': (0.09, False, 'um tiro (repita em rajada a 11 por segundo): transportador recua 80 mm, coice leve; a tampa da janela abre', [
            ('ferrolho', 't', None, [(0, (0, 0, 0)), (0.03, (0, 0, 0.08)), (0.09, (0, 0, 0))]),
            ('gatilho', 'r', X, [(0, 0), (0.015, -12), (0.09, 0)]),
            ('tampa_janela', 'r', Z, [(0, 0), (0.03, ABERTA), (0.09, ABERTA)]),
            (None, 't', None, [(0, (0, 0, 0)), (0.025, (0, 0.001, 0.006)), (0.09, (0, 0, 0))]),
            (None, 'r', X, [(0, 0), (0.03, 0.9), (0.09, 0)])]),
        'atirar_ultimo': (0.1, False, 'último tiro: o ferrolho fica preso atrás', [
            ('ferrolho', 't', None, [(0, (0, 0, 0)), (0.03, (0, 0, 0.08)), (0.1, (0, 0, 0.08))]),
            ('gatilho', 'r', X, [(0, 0), (0.015, -12), (0.1, 0)]),
            ('tampa_janela', 'r', Z, [(0, 0), (0.03, ABERTA), (0.1, ABERTA)]),
            (None, 't', None, [(0, (0, 0, 0)), (0.025, (0, 0.001, 0.006)), (0.1, (0, 0, 0))]),
            (None, 'r', X, [(0, 0), (0.03, 0.9), (0.1, 0)])]),
        'vazia': (0.1, True, 'pose parada: ferrolho atrás', [
            ('ferrolho', 't', None, [(0, (0, 0, 0.08)), (0.1, (0, 0, 0.08))]), tampa]),
        'recarregar': (2.2 * d, False, f'carregador cai (0,35 s) e o novo entra ({1.72 * d:.2f} s)'.replace('.', ','), [
            ('carregador', 't', None, cai), (None, 'r', Z, vira),
            ('ferrolho', 't', None, [(0, (0, 0, 0)), (0.1, (0, 0, 0))])]),
        'recarregar_vazia': (2.6 * d, False, f'troca o carregador e bate no retém: o ferrolho fecha ({2.0 * d:.1f} s)'.replace('.', ','), [
            ('carregador', 't', None, cai), (None, 'r', Z, vira),
            ('retem_ferrolho', 'r', Z, [(0, 0), (2.0 * d - 0.05, 0), (2.0 * d, -8), (2.0 * d + 0.15, 0)]),
            ('ferrolho', 't', None, [(0, (0, 0, 0.08)), (2.0 * d, (0, 0, 0.08)), (2.0 * d + 0.06, (0, 0, 0))])]),
        'trocar_modo': (0.5, False, 'seletor: seguro -> semi -> auto (no jogo, pare na posição escolhida)', [
            ('seletor', 'r', X, [(0, 0), (0.25, 90), (0.5, 180)])]),
        'ocioso': (3.0, True, 'respiração leve parado', [
            (None, 't', None, [(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]),
            ('ferrolho', 't', None, [(0, (0, 0, 0)), (3.0, (0, 0, 0))])]),
    }


def animar(arq, id_, d):
    j, bin_ = empacotar.ler_glb(arq)
    idx = {n.get('name'): i for i, n in enumerate(j['nodes'])}
    j['animations'] = []
    resumo = {}

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

    for nome, (dur, laco, desc, faixas) in animacoes(d).items():
        an = {'name': nome, 'samplers': [], 'channels': []}
        for no, tipo, eixo, chaves in faixas:
            i = idx[no or id_]
            n = j['nodes'][i]
            assert 'rotation' not in n and 'matrix' not in n, no
            base = np.array(n.get('translation', [0, 0, 0]), float)
            t = [k[0] for k in chaves]
            if tipo == 't':
                val, vt, caminho = [list(base + np.array(k[1], float)) for k in chaves], 'VEC3', 'translation'
            else:
                val, vt, caminho = [_q(eixo, k[1]) for k in chaves], 'VEC4', 'rotation'
            an['samplers'].append({'input': put(t, 'SCALAR'), 'output': put(val, vt), 'interpolation': 'LINEAR'})
            an['channels'].append({'sampler': len(an['samplers']) - 1, 'target': {'node': i, 'path': caminho}})
        j['animations'].append(an)
        resumo[nome] = {'duracao_s': round(dur, 2), 'laco': laco, 'descricao': desc}
    empacotar.gravar_glb(arq, j, bin_)
    return resumo


# ------------------------------------------------------------------ catálogo
def registro(id_, m, arq, anims):
    g = pontos_ref.Glb(arq)
    T = g.malha_tudo()
    v = T.reshape(-1, 3)
    r = dict(id=id_)
    d = dict(m['dados'])
    r['nome'] = d.pop('nome')
    r.update(COMUM)
    r.update(d)
    r.update(arquivo=f'armas/{id_}.glb', tamanho_m=[round(float(x), 3) for x in (v.max(0) - v.min(0))], triangulos=int(len(T)),
             kb=round(os.path.getsize(arq) / 1024, 1), gerador='m4a1/jogo.py',
             partes=[dict(p, pai=id_) for p in PARTES], animacoes=anims)
    return r


def linha_md(r):
    v = lambda x: str(x).replace('.', ',')
    return (f"| {r['nome']} (`{r['id']}`) | {r['calibre']} | {r['capacidade']} | {r['dano']} | {r['alcance_m']} m | {v(r['tiros_por_s'])}/s | "
            f"{r['ruido_m']} m | {r['durabilidade']} | {v(r['peso_kg'])} kg |  | {', '.join(r['animacoes'])} |")


def main(saida, fmt='webp'):
    regs = []
    for id_, m in MONTAGENS.items():
        montar_cena(os.path.join(saida, 'm4a1.blend'), id_, m)
        tmp = os.path.join(saida, f'{id_}_sem_tex.glb')
        bpy.ops.export_scene.gltf(filepath=tmp, export_format='GLB', export_image_format='NONE', export_tangents=True,
                                  export_yup=True, export_apply=True, export_extras=False, export_animations=False)
        arq = os.path.join(ARMAS, 'armas', f'{id_}.glb')
        empacotar.main(tmp, os.path.join(saida, 'tex'), arq, fmt)
        d = m['dados']['recarga_s'] / 2.2
        regs.append(registro(id_, m, arq, animar(arq, id_, d)))
    arq_cat = os.path.join(ARMAS, 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    cat['armas'] = [r for r in cat['armas'] if r['id'] not in MONTAGENS] + regs
    cat_ac = {r['id']: r for r in cat['acessorios']}
    for r in regs:
        s = pontos_ref.aplicar_item(r, 'armas', cat_ac)
        r['kb'] = round(os.path.getsize(os.path.join(ARMAS, r['arquivo'])) / 1024, 1)
        print(f"{r['id']:20s} {r['triangulos']} tris {r['kb']} KB {r['tamanho_m']}  " +
              '  '.join(f"{p['no'][4:]}{p['posicao_m']}" for p in s))
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # tabela de armas do CATALOGO.md
    arq_md = os.path.join(ARMAS, 'CATALOGO.md')
    L = [l for l in open(arq_md, encoding='utf-8').read().split('\n') if not any(f'(`{i}`)' in l for i in MONTAGENS)]
    fim = max(i for i, l in enumerate(L[:L.index('## Acessórios')]) if l.startswith('| '))
    L[fim + 1:fim + 1] = [linha_md(r) for r in regs]
    open(arq_md, 'w', encoding='utf-8').write('\n'.join(L))


if __name__ == '__main__':
    main(*sys.argv[1:3])
