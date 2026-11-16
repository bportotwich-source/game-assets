"""GLBs do jogo do AKMN (fuzil_akmn e a montagem tática fuzil_akmn_tatico) e dos acessórios, com o
registro no catálogo. Usa a saída de importar.py e o trabalho comum de ../m4a1/fabrica.py.

uso: python3 jogo.py catalogo                     entradas no catalogo.json (arma, montagem, acessórios)
     python3 jogo.py acessorio <id> <saida>       um acessório (acessorios/<id>.glb)
     python3 jogo.py arma <saida>                 o fuzil (armas/fuzil_akmn.glb), a montagem tática e as versões leves
     python3 jogo.py tudo <saida>                 os três passos, um processo do Blender por GLB
"""
import sys, os, json, copy, subprocess
from config import AQUI, ARMAS, ARMA, TATICO, ACESSORIOS, PADRAO, PADRAO_TATICO, CREDITO, ler

CAT = os.path.join(ARMAS, 'catalogo.json')
GERADOR = 'akmn/jogo.py'
ACS = {a['id']: a for a in ACESSORIOS.values()}


def _cfg_arma():
    return dict(nome=ARMA['nome'], gerador=GERADOR, tris_leve=ARMA['tris_leve'], esqueleto=ler('esqueleto.json'), nos=ARMA['nos'],
                variantes={'': (ARMA['id'], ARMA['descricao'])})


def _cfg_ac(id_):
    a = ACS[id_]
    return dict(nome=id_, gerador=GERADOR, id=id_, esqueleto=ler(f'esqueleto_{id_}.json'), nos={None: [k for k, v in ACESSORIOS.items() if v['id'] == id_]},
                descricao=a['descricao'] + ' ' + CREDITO)


# ------------------------------------------------------------------ catálogo
def catalogo():
    cat = json.load(open(CAT, encoding='utf-8'))
    brasa = next(x for x in cat['armas'] if x['id'] == 'fuzil_762')
    pos = {n['no']: n['posicao'] for n in ler('esqueleto.json')['nos'] if n['pai'] is None}
    pos_filho = {n['no']: n['posicao'] for n in ler('esqueleto.json')['nos']}
    enc_b = {e['no']: e for e in brasa['encaixes']}
    trilhos = ['guarda_mao_longo_akmn']
    E = []
    def enc(no, tipo, aceita, padrao=None, pai=None, **k):
        e = dict(no=no, tipo=tipo, pai=pai or ARMA['id'], posicao_m=pos_filho[no] if pai else pos[no])
        e.update(k)
        if aceita is not None:
            e['aceita'] = aceita
        if padrao:
            e['padrao'] = padrao
        ex = enc_b.get(no, {}).get('explodir_m')
        if ex:
            e['explodir_m'] = ex
        E.append(e)
    enc('encaixe_mira', 'trilho_lateral_ak', ['trilho_lateral_akmn', 'mira_lateral_ak', 'luneta_lateral_ak'],
        descricao='trilho de cauda de andorinha do lado esquerdo')
    enc('encaixe_mira_trilho', 'trilho_mira', enc_b['encaixe_mira_tampa']['aceita'], requer={'encaixe_mira': 'trilho_lateral_akmn'},
        descricao='só existe com o trilho superior de montagem lateral', explodir_m=[0.0, 0.07, 0.0])
    enc('encaixe_boca', 'boca_762', ['freio_akmn', 'freio_ak', 'compensador_ak', 'supressor_762'], 'freio_akmn')
    enc('encaixe_carregador', 'carregador_762', enc_b['encaixe_carregador']['aceita'] + ['carregador_762_30_polimero'],
        pai='carregador', substitui='carregador', descricao='filho do nó carregador; ao pôr um carregador aqui, esconda o original')
    enc('encaixe_coronha', 'coronha_ak', ['coronha_madeira_akmn', 'coronha_rebativel_akmn'], 'coronha_madeira_akmn')
    enc('encaixe_punho', 'punho_ak', ['punho_akmn', 'punho_tatico_akmn'], 'punho_akmn', explodir_m=[0.0, -0.06, 0.03])
    enc('encaixe_guarda_mao', 'guarda_mao_ak', ['guarda_mao_madeira_akmn', 'guarda_mao_longo_akmn'], 'guarda_mao_madeira_akmn')
    enc('encaixe_empunhadura', 'mlok_baixo', enc_b['encaixe_empunhadura']['aceita'] + ['batente_akmn'], requer={'encaixe_guarda_mao': trilhos},
        descricao='fendas de baixo do guarda-mão longo')
    enc('encaixe_lanterna', 'mlok_lado', enc_b['encaixe_lanterna']['aceita'], requer={'encaixe_guarda_mao': trilhos},
        descricao='fendas da direita do guarda-mão longo')
    enc('encaixe_laser', 'mlok_esq', enc_b['encaixe_laser']['aceita'], requer={'encaixe_guarda_mao': trilhos},
        descricao='fendas da esquerda do guarda-mão longo')
    enc('encaixe_enfeite', 'guarda_mao_enfeite', ['elastico_ak'], requer={'encaixe_guarda_mao': ['guarda_mao_madeira_akmn']},
        descricao='tiras de borracha em volta do guarda-mão')
    enc('encaixe_baioneta', 'baioneta_ak', ['baioneta_ak'])
    enc('encaixe_bandoleira', 'bandoleira', ['bandoleira'])
    for no in ('boca_fogo', 'saida_estojo', 'mira_ferro'):
        enc(no, 'efeito' if no != 'mira_ferro' else 'mira', None, descricao=enc_b[no]['descricao'])
    partes = copy.deepcopy(brasa['partes'])
    for p in partes:
        p['pai'] = ARMA['id']
        if p['no'] == 'tampa':
            p['descricao'] = 'tampa do receptor com nervuras (sai para limpar)'
    r = {k: copy.deepcopy(v) for k, v in brasa.items() if k not in ('pontos_ref', 'triangulos', 'kb', 'tamanho_m', 'triangulos_leve', 'kb_leve')}
    r.update(id=ARMA['id'], nome='Fuzil AKMN 7,62', descricao=ARMA['descricao'], arquivo=f"armas/{ARMA['id']}.glb", gerador=GERADOR,
             encaixes=E, partes=partes, peso_kg=3.3, raridade='raro', valor_troca=170, credito=CREDITO,
             onde=['quartel', 'delegacia', 'fabrica'])
    t = copy.deepcopy(r)
    for e in t['encaixes']:
        e['pai'] = TATICO['id'] if e['pai'] == ARMA['id'] else e['pai']
        e.pop('padrao', None)
        if e['no'] in PADRAO_TATICO:
            e['padrao'] = PADRAO_TATICO[e['no']]
    for p in t['partes']:
        p['pai'] = TATICO['id']
    t.update(id=TATICO['id'], nome='Fuzil AKMN tático 7,62', descricao=TATICO['descricao'], arquivo=f"armas/{TATICO['id']}.glb",
             peso_kg=3.6, raridade='muito raro', valor_troca=260, onde=['quartel'])
    for novo in (r, t):
        velho = next((x for x in cat['armas'] if x['id'] == novo['id']), None)
        if velho:                                      # guarda as medidas já feitas
            for k in ('pontos_ref', 'triangulos', 'kb', 'tamanho_m', 'triangulos_leve', 'kb_leve', 'arquivo_leve'):
                if k in velho:
                    novo[k] = velho[k]
            cat['armas'][cat['armas'].index(velho)] = novo
        else:
            i = cat['armas'].index(next(x for x in cat['armas'] if x['id'] == 'fuzil_762_tatico'))
            cat['armas'].insert(i + 1 + (novo is t), novo)
    for a in ACESSORIOS.values():
        x = dict(id=a['id'], nome=a['nome'], grupo='acessorios', categoria=a['categoria'], encaixe=a['encaixe'], peso_kg=a['peso_kg'],
                 raridade=a['raridade'], valor_troca=a['valor_troca'], modificadores=a['modificadores'], onde=a['onde'],
                 descricao=a['descricao'] + ' ' + CREDITO, arquivo=f"acessorios/{a['id']}.glb", gerador=GERADOR, credito=CREDITO)
        for k in ('capacidade', 'municao'):
            if k in a:
                x[k] = a[k]
        velho = next((y for y in cat['acessorios'] if y['id'] == a['id']), None)
        if velho:
            for k in ('pontos_ref', 'triangulos', 'kb', 'tamanho_m', 'encaixes'):
                if k in velho:
                    x[k] = velho[k]
            cat['acessorios'][cat['acessorios'].index(velho)] = x
        else:
            cat['acessorios'].append(x)
    # o carregador de polímero também serve no Brasa 7,62
    for w in cat['armas']:
        if w['id'] in ('fuzil_762', 'fuzil_762_tatico'):
            for e in w['encaixes']:
                if e['no'] == 'encaixe_carregador' and 'carregador_762_30_polimero' not in e['aceita']:
                    e['aceita'].append('carregador_762_30_polimero')
    json.dump(cat, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('catálogo: 2 armas,', len(ACESSORIOS), 'acessórios')


# ------------------------------------------------------------------ versões leves (com os acessórios montados)
def _leve(ID, pecas, saida):
    """Versão leve da arma montada: o corpo e as peças dadas (nomes do _akmn_tudo/_zen_tudo.blend) numa malha só."""
    import bpy
    import fabrica, empacotar
    from mathutils import Matrix
    bpy.ops.wm.open_mainfile(filepath=os.path.join(saida, '_akmn_tudo.blend'))
    zen = [p for p in pecas if p not in bpy.data.objects]
    if zen:
        with bpy.data.libraries.load(os.path.join(saida, '_zen_tudo.blend')) as (de, para):
            para.objects = [n for n in de.objects if n in zen]
        for o in para.objects:
            bpy.context.scene.collection.objects.link(o)
    manter = set(pecas) | {'corpo', 'tampa', 'gatilho', 'seletor', 'ferrolho'} | ({'carregador'} if 'carregador_polimero' not in pecas else set())
    for o in list(bpy.data.objects):
        if o.name not in manter:
            bpy.data.objects.remove(o)
    raiz = bpy.data.objects.new(ARMA['nome'], None)
    bpy.context.scene.collection.objects.link(raiz)
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            o.parent = raiz
    blend = os.path.join(saida, f'{ID}_leve.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    fabrica.leve(_cfg_arma(), ID, blend, os.path.join(saida, 'tex'))
    tmp = os.path.join(saida, f'{ID}_leve_sem_tex.glb')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=tmp, **fabrica.EXPORTAR)
    arq_l = os.path.join(ARMAS, 'armas', f'{ID}_leve.glb')
    empacotar.main(tmp, os.path.join(saida, 'tex'), arq_l, 'webp')
    cat = json.load(open(CAT, encoding='utf-8'))
    r = next(x for x in cat['armas'] if x['id'] == ID)
    tam, tris = fabrica.medir(arq_l)
    r.update(arquivo_leve=f'armas/{ID}_leve.glb', triangulos_leve=tris, kb_leve=round(os.path.getsize(arq_l) / 1024, 1))
    json.dump(cat, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(ID, 'leve', tris, 'tris', r['kb_leve'], 'KB', tam)


def _copiar_glb(de, para, ID, velho):
    import empacotar
    j, b = empacotar.ler_glb(de)
    for n in j['nodes']:
        nm = str(n.get('name', ''))
        if nm == velho or nm.startswith(velho + '_'):
            n['name'] = ID + nm[len(velho):]
    for m in j.get('meshes', []):
        nm = str(m.get('name', ''))
        if nm.startswith(velho + '_'):
            m['name'] = ID + nm[len(velho):]
    empacotar.gravar_glb(para, j, b)


def arma(saida):
    import fabrica, pontos_ref
    fabrica.jogo(_cfg_arma(), saida)                   # GLB do jogo, leve sem acessórios (refeita abaixo) e catálogo
    base = os.path.join(ARMAS, 'armas', f"{ARMA['id']}.glb")
    _copiar_glb(base, os.path.join(ARMAS, 'armas', f"{TATICO['id']}.glb"), TATICO['id'], ARMA['id'])
    cat = json.load(open(CAT, encoding='utf-8'))
    ac = {x['id']: x for x in cat['acessorios']}
    r = next(x for x in cat['armas'] if x['id'] == TATICO['id'])
    r['tamanho_m'], r['triangulos'] = fabrica.medir(os.path.join(ARMAS, r['arquivo']))
    pontos_ref.aplicar_item(r, 'armas', ac)
    r['kb'] = round(os.path.getsize(os.path.join(ARMAS, r['arquivo'])) / 1024, 1)
    json.dump(cat, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def tudo(saida):
    py = sys.executable
    subprocess.run([py, __file__, 'catalogo'], check=True)
    for id_ in ACS:
        subprocess.run([py, __file__, 'acessorio', id_, saida], check=True)
    subprocess.run([py, __file__, 'arma', saida], check=True)
    subprocess.run([py, __file__, 'leve', ARMA['id'], saida, 'coronha,guarda_mao,punho,freio'], check=True)
    subprocess.run([py, __file__, 'leve', TATICO['id'], saida,
                    'coronha_tatica,guarda_mao_longo,punho_tatico,freio,carregador_polimero,trilho_lateral,batente'], check=True)
    subprocess.run([py, __file__, 'md'], check=True)


if __name__ == '__main__':
    q = sys.argv[1]
    if q == 'catalogo':
        catalogo()
    elif q == 'acessorio':
        import fabrica
        fabrica.acessorio(_cfg_ac(sys.argv[2]), sys.argv[3])
    elif q == 'arma':
        arma(sys.argv[2])
    elif q == 'leve':
        pecas = sys.argv[4].split(',')
        if 'freio' in pecas:                           # o freio está no _akmn_tudo.blend
            pass
        _leve(sys.argv[2], pecas, sys.argv[3])
    elif q == 'md':
        sys.path.insert(0, ARMAS)
        import gerar_armas
        gerar_armas.catalogo_md(json.load(open(CAT, encoding='utf-8')))
    elif q == 'tudo':
        tudo(sys.argv[2])
