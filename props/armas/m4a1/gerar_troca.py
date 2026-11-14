"""Gera a M4A1 de peças trocáveis (troca.py): a arma base, os acessórios próprios dela e as três
montagens do catálogo (fuzil_m4a1, fuzil_m4a1_luneta, fuzil_m4a1_tatico), que usam o mesmo modelo
base e mudam só as peças que vêm montadas de fábrica.

uso:
  python3 gerar_troca.py catalogo                     registros no catalogo.json (sem Blender)
  python3 gerar_troca.py base [res] [saida]           arma base: bake (2048) e GLB de jogo de fuzil_m4a1
  python3 gerar_troca.py <id_acessorio> [res] [saida] um acessório (1024): bake e GLB em acessorios/
  python3 gerar_troca.py montagens <saida_m4a1>       cópias da base para _luneta/_tatico e as versões leves
                                                      das três montagens (saida_m4a1 = pasta de `gerar.py 1024`)
"""
import sys, os, json, shutil, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [p for p in (AQUI, ARMAS) if p not in sys.path]
import troca

CAT = os.path.join(ARMAS, 'catalogo.json')
LONGO = ['guarda_mao_longo_m4']

# peças de fábrica de cada montagem ({encaixe: acessório}) e o que muda nos números
MONTAGENS = {
    'fuzil_m4a1': dict(
        padrao={'encaixe_guarda_mao': 'guarda_mao_classico_m4', 'encaixe_mira': 'alca_transporte_m4',
                'encaixe_boca': 'quebra_chamas_556', 'encaixe_coronha': 'coronha_retratil_ar'},
        dados=dict(nome='Fuzil M4A1', raridade='raro', valor_troca=180)),
    'fuzil_m4a1_luneta': dict(
        padrao={'encaixe_guarda_mao': 'guarda_mao_longo_m4', 'encaixe_mira': 'luneta_m4', 'encaixe_boca': 'supressor_556',
                'encaixe_empunhadura': 'empunhadura_angulada', 'encaixe_carregador': 'carregador_556_30',
                'encaixe_coronha': 'coronha_fixa_ar'},
        dados=dict(nome='Fuzil M4A1 com luneta', variante_de='fuzil_m4a1', raridade='muito raro', valor_troca=260,
                   descricao='A M4A1 montada para tiro de longe: guarda-mão longo vazado, supressor, luneta de 2 a 8×, '
                             'empunhadura angulada, carregador de polímero e coronha fixa. Todas as peças saem e entram pela '
                             'tela da arma. Modelo detalhado, com texturas assadas.')),
    'fuzil_m4a1_tatico': dict(
        padrao={'encaixe_guarda_mao': 'guarda_mao_longo_m4', 'encaixe_mira': 'mira_prismatica_m4', 'encaixe_mira_45': 'mira_45_m4',
                'encaixe_boca': 'supressor_556', 'encaixe_laser': 'modulo_laser', 'encaixe_lanterna': 'lanterna_compacta',
                'encaixe_empunhadura': 'empunhadura_vertical', 'encaixe_carregador': 'tambor_556_60_tatico',
                'encaixe_punho': 'punho_vazado_m4', 'encaixe_alavanca': 'alavanca_ambi_m4', 'encaixe_coronha': 'coronha_moderna_ar'},
        dados=dict(nome='Fuzil M4A1 tático', variante_de='fuzil_m4a1', raridade='muito raro', valor_troca=300,
                   descricao='A M4A1 com tudo: guarda-mão longo, supressor, mira prismática, reflex a 45°, módulo laser, '
                             'lanterna, empunhadura vertical, tambor de 60, punho vazado, alavanca ambidestra e coronha moderna. '
                             'Todas as peças saem e entram pela tela da arma. Modelo detalhado, com texturas assadas.')),
}

# registro de cada acessório novo (o resto: tamanho, triângulos, kb e descrição vem da fábrica)
ACESS = {
    'guarda_mao_classico_m4': dict(nome='Guarda-mão de trilho quádruplo (M4A1)', categoria='guarda_mao', encaixe='guarda_mao_m4',
                                   peso_kg=0.32, raridade='incomum', valor_troca=15, modificadores={}, onde=['quartel', 'delegacia']),
    'guarda_mao_longo_m4': dict(nome='Guarda-mão longo vazado (M4A1)', categoria='guarda_mao', encaixe='guarda_mao_m4',
                                peso_kg=0.36, raridade='raro', valor_troca=30, modificadores={'precisao': 1.05},
                                onde=['quartel', 'delegacia']),
    'alca_transporte_m4': dict(nome='Alça de transporte com mira (M4A1)', categoria='mira', encaixe='trilho_mira', ferro=True,
                               peso_kg=0.27, raridade='incomum', valor_troca=15, modificadores={},
                               onde=['quartel', 'delegacia'], linha_de_visada='encaixe "olho" (furo da alça)'),
    'luneta_m4': dict(nome='Luneta 2-8× (M4A1)', categoria='mira', encaixe='trilho_mira', aumento=[2, 8], peso_kg=0.62,
                      raridade='muito raro', valor_troca=120,
                      modificadores={'precisao_mirando': 1.5, 'tempo_mirar': 1.15, 'alcance_m': 1.75}, onde=['quartel'],
                      linha_de_visada='encaixe "olho"; zoom de 2× a 8×',
                      optica={'tipo': 'luneta', 'aumento': [2, 8], 'iluminado': True, 'ocular_m': [0.0, 0.161, 0.0142],
                              'raio_ocular_m': 0.0165, 'objetiva_m': [0.0, 0.161, -0.2478]}),
    'mira_prismatica_m4': dict(nome='Mira prismática 3× (M4A1)', categoria='mira', encaixe='trilho_mira', aumento=[3, 3],
                               peso_kg=0.45, raridade='muito raro', valor_troca=95,
                               modificadores={'precisao_mirando': 1.35, 'tempo_mirar': 0.95, 'alcance_m': 1.25},
                               onde=['quartel', 'delegacia'], linha_de_visada='encaixe "olho"; 3× fixo',
                               optica={'tipo': 'luneta', 'aumento': [3, 3], 'iluminado': True, 'ocular_m': [0.0, 0.167, -0.0388],
                                       'raio_ocular_m': 0.0145, 'objetiva_m': [0.0, 0.167, -0.1548]}),
    'mira_45_m4': dict(nome='Mira reflex a 45° (M4A1)', categoria='mira_45', encaixe='mira_45_m4', peso_kg=0.12,
                       raridade='raro', valor_troca=45, modificadores={'tempo_mirar': 0.9}, onde=['quartel']),
    'punho_vazado_m4': dict(nome='Punho vazado de alumínio', categoria='punho', encaixe='punho_ar', peso_kg=0.09,
                            raridade='incomum', valor_troca=10, modificadores={'recuo': 0.97}, onde=['quartel', 'delegacia']),
    'alavanca_ambi_m4': dict(nome='Alavanca de manejo ambidestra', categoria='alavanca', encaixe='alavanca_ar', peso_kg=0.05,
                             raridade='incomum', valor_troca=10, modificadores={'recarga_s': 0.95}, onde=['quartel', 'delegacia']),
    'coronha_moderna_ar': dict(nome='Coronha moderna (fuzil)', categoria='coronha', encaixe='coronha_ar', peso_kg=0.48,
                               raridade='raro', valor_troca=28, modificadores={'recuo': 0.6, 'precisao': 1.32},
                               onde=['quartel', 'delegacia']),
}
# acessórios novos que também servem em encaixes do mesmo tipo de outras armas (com a luneta 1-6 aceita lá)
EXTRA = {'punho_ar': ['punho_vazado_m4'], 'coronha_ar': ['coronha_moderna_ar'], 'trilho_mira': ['luneta_m4', 'mira_prismatica_m4']}


def _optica_local(o, pos):
    o = dict(o)
    for k in ('ocular_m', 'objetiva_m'):
        o[k] = [round(a - b, 4) for a, b in zip(o[k], pos)]
    return o


def encaixes_m4(ID, cat):
    """Encaixes da M4A1: os do Vigília (mesmos lugares), mais guarda-mão, alavanca e mira a 45°."""
    v = next(a for a in cat['armas'] if a['id'] == 'fuzil_556')
    pos = {n['no']: n for n in troca.esqueleto_base()['nos']}
    out = [dict(no='encaixe_guarda_mao', tipo='guarda_mao_m4', pai=ID, posicao_m=pos['encaixe_guarda_mao']['posicao'],
                aceita=['guarda_mao_classico_m4', 'guarda_mao_longo_m4'],
                descricao='guarda-mão: o clássico traz a massa fixa; o longo libera os trilhos de baixo e dos lados')]
    for e in v['encaixes']:
        e = json.loads(json.dumps(e))
        if e.get('pai') == 'fuzil_556':
            e['pai'] = ID
        if e['no'] in pos:
            e['posicao_m'] = [round(c, 4) for c in pos[e['no']]['posicao']]
        e.pop('padrao', None)
        if e['no'] == 'encaixe_mira':
            e['aceita'] = ['alca_transporte_m4'] + e['aceita']
        if e['no'] == 'encaixe_alca':
            e['proibe'] = {'encaixe_mira': ['alca_transporte_m4']}
            e['descricao'] = 'não cabe com a alça de transporte; ' + e['descricao']
        if e['no'] in ('encaixe_massa', 'encaixe_empunhadura', 'encaixe_lanterna', 'encaixe_laser', 'encaixe_bipe',
                       'encaixe_bandoleira'):
            e['requer'] = {'encaixe_guarda_mao': LONGO}
        out.append(e)
        if e['no'] == 'encaixe_punho':
            out.append(dict(no='encaixe_alavanca', tipo='alavanca_ar', pai='alavanca', posicao_m=[0.0, 0.0, 0.0],
                            substitui='alavanca', aceita=['alavanca_ambi_m4'],
                            descricao='filho do nó alavanca (anda com ela); ao pôr uma alavanca aqui, esconda as malhas do nó alavanca'))
        if e['no'] == 'encaixe_mira':
            out.append(dict(no='encaixe_mira_45', tipo='mira_45_m4', pai=ID, posicao_m=pos['encaixe_mira_45']['posicao'],
                            requer={'encaixe_guarda_mao': LONGO}, aceita=['mira_45_m4'],
                            descricao='trilho de cima do guarda-mão longo, na frente da mira principal'))
    return out


def catalogo():
    cat = json.load(open(CAT, encoding='utf-8'))
    ids_ac = {a['id'] for a in cat['acessorios']}
    for i, r in ACESS.items():
        a = next((x for x in cat['acessorios'] if x['id'] == i), None)
        if a is None:
            a = {'id': i}
            cat['acessorios'].append(a)
        a.update(grupo='acessorios', **json.loads(json.dumps(r)))
        a.setdefault('descricao', troca.ACESSORIOS[i]['descricao'])
        a['arquivo'] = f'acessorios/{i}.glb'
        a['gerador'] = 'm4a1/gerar_troca.py'
        if 'optica' in a:
            a['optica'] = _optica_local(a['optica'], troca.POS['encaixe_mira'])
        olho = troca.ACESSORIOS[i]['esqueleto']['nos']
        if olho:
            a['encaixes'] = [dict(no='olho', tipo='mira', pai=i, posicao_m=olho[0]['posicao'], descricao='linha de visada')]
    base = next(a for a in cat['armas'] if a['id'] == 'fuzil_m4a1')
    for ID, m in MONTAGENS.items():
        r = next(a for a in cat['armas'] if a['id'] == ID)
        r.pop('apoio_vertical', None)
        if ID != 'fuzil_m4a1':                                  # números da base; o que muda vem dos acessórios
            for k in ('capacidade', 'alcance_m', 'recarga_s', 'recarga_vazia_s', 'precisao', 'ruido_m', 'peso_kg', 'partes', 'animacoes'):
                if k in base:
                    r[k] = json.loads(json.dumps(base[k]))
        else:
            r.update(capacidade=30, alcance_m=80, recarga_s=2.2, recarga_vazia_s=2.6, precisao=0.8, ruido_m=160, peso_kg=3.1)
            v = next(a for a in cat['armas'] if a['id'] == 'fuzil_556')
            r['partes'] = [dict(p, pai=ID if p.get('pai') == 'fuzil_556' else p.get('pai')) for p in json.loads(json.dumps(v['partes']))]
            r['animacoes'] = json.loads(json.dumps(v['animacoes']))
        r.update(m['dados'])
        r['arquivo'] = f'armas/{ID}.glb'
        r['gerador'] = 'm4a1/gerar_troca.py'
        r['encaixes'] = encaixes_m4(ID, cat)
        for e in r['encaixes']:
            if e['no'] in m['padrao']:
                e['padrao'] = m['padrao'][e['no']]
        falta = set(m['padrao']) - {e['no'] for e in r['encaixes']}
        assert not falta, falta
    for i in [x for x in ACESS if x not in ids_ac]:
        print('novo acessório', i)
    # acessórios novos em encaixes do mesmo tipo das outras armas
    for a in cat['armas']:
        for e in a.get('encaixes', []):
            for novo in EXTRA.get(e.get('tipo'), []):
                if e['tipo'] == 'trilho_mira' and 'luneta_1_6' not in e.get('aceita', []):
                    continue
                if novo not in e.setdefault('aceita', []):
                    e['aceita'].append(novo)
    json.dump(cat, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def _copiar_glb(de, para, ID):
    """Cópia do GLB da base com a raiz renomeada (os nós pai dos encaixes têm o nome da arma)."""
    import empacotar
    j, b = empacotar.ler_glb(de)
    for n in j['nodes']:
        if n.get('name') == 'fuzil_m4a1':
            n['name'] = ID
        elif str(n.get('name', '')).startswith('fuzil_m4a1_'):
            n['name'] = ID + n['name'][len('fuzil_m4a1'):]
    for m in j.get('meshes', []):
        if str(m.get('name', '')).startswith('fuzil_m4a1_'):
            m['name'] = ID + m['name'][len('fuzil_m4a1'):]
    empacotar.gravar_glb(para, j, b)


# peças da M4A1 inteira (m4a1.blend de gerar.py) que entram na versão leve de cada montagem
SLOTS_LEVE = {
    'fuzil_m4a1': dict(gm='classico', boca='quebra', mira='alca', reflex='sem', laser='sem', lanterna='sem', emp='sem', carr='metal',
                       punho='padrao', alav='padrao', tubo='preto', cor='retratil'),
    'fuzil_m4a1_luneta': dict(gm='longo', boca='supressor', mira='luneta', reflex='sem', laser='sem', lanterna='sem', emp='angulada',
                              carr='polimero', punho='padrao', alav='padrao', tubo='preto', cor='fixa'),
    'fuzil_m4a1_tatico': dict(gm='longo', boca='supressor', mira='prisma', reflex='com', laser='com', lanterna='com', emp='vertical',
                              carr='tambor', punho='vazado', alav='ambi', tubo='vermelho', cor='moderna'),
}
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


def leve_montagem(ID, saida_m4):
    """Versão leve (uma malha, 1 conjunto 1024) da montagem de fábrica, a partir da M4A1 inteira."""
    import bpy
    import fabrica, empacotar
    esc = SLOTS_LEVE[ID]
    fora = {n for s, ops in SLOTS.items() for k, ns in ops.items() if k != esc[s] for n in ns}
    bpy.ops.wm.open_mainfile(filepath=os.path.join(saida_m4, 'm4a1.blend'))
    for o in [o for o in bpy.data.objects if o.type == 'MESH' and o.name in fora]:
        for c in [c for c in bpy.data.objects if c.parent == o]:
            mw = c.matrix_world.copy()
            c.parent = bpy.data.objects['m4a1']
            c.matrix_parent_inverse.identity()
            c.matrix_world = mw
        bpy.data.objects.remove(o)
    for o in bpy.data.objects:                          # a versão leve não tem gravações à parte
        if o.type == 'MESH' and 'gravacao' not in o.data.attributes:
            o.data.attributes.new('gravacao', 'INT', 'FACE')
    blend = os.path.join(saida_m4, f'{ID}_leve.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    fabrica.leve(dict(nome='m4a1', tris_leve=6000), ID, blend, os.path.join(saida_m4, 'tex'))
    tmp = os.path.join(saida_m4, f'{ID}_leve_sem_tex.glb')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=tmp, **fabrica.EXPORTAR)
    arq = os.path.join(ARMAS, 'armas', f'{ID}_leve.glb')
    empacotar.main(tmp, os.path.join(saida_m4, 'tex'), arq, 'webp')
    cat = json.load(open(CAT, encoding='utf-8'))
    r = next(x for x in cat['armas'] if x['id'] == ID)
    tam, tris = fabrica.medir(arq)
    # tamanho_m é o da arma montada de fábrica (a base sem coronha e sem guarda-mão é curta): o jogo tira dele o
    # espaço na mochila e a altura da arma deitada no chão (que é a versão leve)
    r.update(tamanho_m=tam, arquivo_leve=f'armas/{ID}_leve.glb', triangulos_leve=tris, kb_leve=round(os.path.getsize(arq) / 1024, 1))
    json.dump(cat, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(ID, 'leve', tris, 'tris', r['kb_leve'], 'KB', tam)


def montagens(saida_m4):
    import pontos_ref, fabrica
    base = os.path.join(ARMAS, 'armas', 'fuzil_m4a1.glb')
    for ID in MONTAGENS:
        if ID != 'fuzil_m4a1':
            _copiar_glb(base, os.path.join(ARMAS, 'armas', f'{ID}.glb'), ID)
    cat = json.load(open(CAT, encoding='utf-8'))
    ac = {x['id']: x for x in cat['acessorios']}
    for ID in MONTAGENS:
        r = next(x for x in cat['armas'] if x['id'] == ID)
        arq = os.path.join(ARMAS, 'armas', f'{ID}.glb')
        r['tamanho_m'], r['triangulos'] = fabrica.medir(arq)
        pontos_ref.aplicar_item(r, 'armas', ac)
        r['kb'] = round(os.path.getsize(arq) / 1024, 1)
    json.dump(cat, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for ID in MONTAGENS:                                 # um processo por montagem (o Blender abre outro arquivo a cada vez)
        subprocess.run([sys.executable, __file__, 'leve', ID, saida_m4], check=True)


if __name__ == '__main__':
    q = sys.argv[1]
    if q == 'catalogo':
        catalogo()
    elif q == 'montagens':
        montagens(sys.argv[2])
    elif q == 'leve':
        leve_montagem(sys.argv[2], sys.argv[3])
    else:
        import fabrica
        cfg = troca.BASE if q == 'base' else troca.ACESSORIOS[q]
        res = int(sys.argv[2]) if len(sys.argv) > 2 else (2048 if q == 'base' else 1024)
        saida = sys.argv[3] if len(sys.argv) > 3 else os.path.join(AQUI, 'saida_' + q)
        if not os.path.exists(os.path.join(saida, f"{cfg['nome']}.blend")):
            fabrica.gerar(cfg, res, saida)
        if q == 'base':
            fabrica.jogo(cfg, saida)
        else:
            fabrica.acessorio(cfg, saida)
