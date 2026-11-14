"""M4A1 de peças trocáveis: a arma base (receptores, cano, controles, punho e carregador de metal)
com os encaixes do fuzil Vigília, e as peças próprias da M4A1 como acessórios soltos.

As peças nascem nas coordenadas da M4A1 (modelo.py e acessorios.py, em mm: u para a frente,
v para cima, w para a direita); a origem de cada acessório é o ponto do encaixe dele na arma.
O Vigília (../vigilia) é feito das mesmas peças, levadas 145 mm para a frente com a origem no
mesmo ponto do punho; por isso os encaixes dele valem aqui como estão, e as coronhas, punhos,
miras, bocas, carregadores e empunhaduras do Vigília servem na M4A1 (e vice-versa).

Configurações para ../m4a1/fabrica.py:
  BASE         arma base (fuzil_m4a1; as montagens _luneta e _tatico são cópias dela com outras peças de fábrica)
  ACESSORIOS   id -> cfg de cada acessório
Uso: ver gerar_troca.py.
"""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [p for p in (AQUI, ARMAS) if p not in sys.path]

ORIGEM = (-182, -93, 0)                   # centro do punho, como na M4A1 antiga e no Vigília


def _ler(nome):
    return json.load(open(os.path.join(AQUI, '..', 'vigilia', nome), encoding='utf-8'))


def enc(x, y, z):
    """Ponto de encaixe (m, espaço da arma: y para cima, cano para -Z) -> mm do projeto."""
    return (ORIGEM[0] - z * 1000.0, ORIGEM[1] + y * 1000.0, x * 1000.0)


# encaixes novos da M4A1 (os outros são os do Vigília, lidos do esqueleto dele)
NOVOS = {
    'encaixe_guarda_mao': (None, [0.0, 0.093, -0.182]),       # frente do receptor, no eixo do cano
    'encaixe_alavanca': ('alavanca', [0.0, 0.0, 0.0]),        # dentro do nó da alavanca (anda com ela)
    'encaixe_mira_45': (None, [0.0, 0.123, -0.239]),          # trilho de cima do guarda-mão longo, perto do receptor
}
POS = {'encaixe_mira': (0.0, 0.123, -0.117), 'encaixe_punho': (0.0, 0.048, -0.017), 'alavanca': (0.0, 0.093, -0.037),
       'encaixe_coronha': (0.0, 0.093, 0.015), 'encaixe_guarda_mao': (0.0, 0.093, -0.182), 'encaixe_mira_45': (0.0, 0.123, -0.239)}


def esqueleto_base():
    e = _ler('esqueleto.json')
    e = dict(e, origem='fuzil_m4a1.glb', nos=[dict(n) for n in e['nos']])
    for no, (pai, p) in NOVOS.items():
        e['nos'].append({'no': no, 'pai': pai, 'posicao': p})
    return e


def _so(*nomes_olho):
    nos = [{'no': n, 'pai': None, 'posicao': p} for n, p in nomes_olho]
    return {'nos': nos, 'animacoes': []}


# ------------------------------------------------------------------ montagem (Blender)
def _bl():
    import bpy
    import lib, modelo as m4, acessorios as ac
    return bpy, lib, m4, ac


def _solto(o):
    """Tira o pai sem mexer a peça no mundo."""
    import bpy
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = mw
    bpy.context.view_layer.update()


def _tirar(nomes):
    bpy, lib, m4, ac = _bl()
    alvo = [o for o in lib.PARTES if o.name in nomes]
    for o in alvo:
        for c in [c for c in bpy.data.objects if c.parent == o and c.name not in nomes]:
            _solto(c)
    for o in alvo:
        lib.PARTES.remove(o)
        bpy.data.objects.remove(o)


def _grupo(g, nomes=None):
    bpy, lib, m4, ac = _bl()
    for o in lib.PARTES:
        o['grupo'] = g if nomes is None else ('A' if o.name in nomes else 'B')


def _filho(o, pai):
    import bpy
    o.parent = pai
    bpy.context.view_layer.update()
    o.matrix_parent_inverse = pai.matrix_world.inverted()


def montar_base():
    bpy, lib, m4, ac = _bl()
    sup = m4.receptor_superior()
    for f in (m4.impulsor, m4.tampa_janela, m4.ferrolho, m4.alavanca_manejo):
        _filho(f(), sup)
    inf = m4.receptor_inferior()
    m4.controles(inf)
    m4.punho(inf)
    c = m4.cano()
    m4.base_massa(c)                       # cria a base da massa e o tubo de gás; a base vai com o guarda-mão clássico
    _tirar(('base_massa', 'pino_base_massa_1', 'pino_base_massa_2', 'pino_massa', 'zarelho_frontal'))
    m4.carregador()
    # A: receptores e controles; B: cano, tubo de gás, punho e carregador
    _grupo(None, {'receptor_superior', 'impulsor_ferrolho', 'tampa_janela', 'ferrolho', 'alavanca_manejo', 'trava_alavanca',
                  'receptor_inferior', 'gatilho', 'guarda_mato', 'seletor', 'retem_ferrolho', 'retem_carregador', 'pino_pivo',
                  'pino_desmontagem', 'pino_gatilho', 'pino_cao', 'pino_armadilha'})


def montar_classico():
    bpy, lib, m4, ac = _bl()
    c = m4.cano()
    m4.base_massa(c)
    m4.guarda_mao(c)
    _tirar(('cano', 'tubo_gas'))
    _grupo('A')


def montar_longo():
    bpy, lib, m4, ac = _bl()
    ac.guarda_mao_longo()
    _tirar(('trilho_baixo', 'trilho_esquerdo'))
    _grupo('A')


def montar_alca():
    bpy, lib, m4, ac = _bl()
    m4.alca_transporte()
    _grupo('A')


def montar_luneta():
    bpy, lib, m4, ac = _bl()
    ac.luneta()
    _grupo('A')


def montar_prismatica():
    bpy, lib, m4, ac = _bl()
    ac.mira_prismatica()
    _grupo('A')


def montar_reflex():
    bpy, lib, m4, ac = _bl()
    ac.mira_reflex()
    _grupo('A')


def montar_punho():
    bpy, lib, m4, ac = _bl()
    ac.punho_vazado()
    _grupo('A')


def montar_alavanca():
    bpy, lib, m4, ac = _bl()
    ac.alavanca_ambi()
    _grupo('A')


def montar_coronha():
    bpy, lib, m4, ac = _bl()
    m4.coronha()                           # tira daqui só a placa e a porca do tubo
    _tirar(('tubo_coronha', 'coronha', 'trava_coronha', 'zarelho_traseiro'))
    ac.tubo_vermelho()
    ac.coronha_moderna()
    _grupo('A')


# ------------------------------------------------------------------ configurações
_FIM = ' Modelo detalhado, peça da M4A1, com texturas assadas.'
BASE = dict(nome='m4a1_base', montar=montar_base, gerador='m4a1/gerar_troca.py', tris_leve=6000, origem=ORIGEM,
            esqueleto=esqueleto_base(),
            nos={None: ['receptor_superior', 'impulsor_ferrolho', 'receptor_inferior', 'guarda_mato', 'retem_carregador', 'pino_pivo',
                        'pino_desmontagem', 'pino_gatilho', 'pino_cao', 'pino_armadilha', 'cano', 'tubo_gas'],
                 'punho': ['punho'], 'gatilho': ['gatilho'], 'seletor': ['seletor'], 'ferrolho': ['ferrolho'],
                 'alavanca': ['alavanca_manejo', 'trava_alavanca'], 'tampa_janela': ['tampa_janela'],
                 'retem_ferrolho': ['retem_ferrolho'], 'carregador': ['carregador', 'transportador', 'cartucho_1', 'cartucho_2']},
            variantes={'': ('fuzil_m4a1',
                            'Fuzil 5,56 clássico, de peças trocáveis como o Vigília: guarda-mão, alça de transporte, boca, '
                            'coronha, punho, alavanca de manejo e carregador saem e entram pela tela da arma. Vem com o '
                            'guarda-mão de trilho quádruplo, a alça de transporte, o quebra-chamas e a coronha retrátil. '
                            'Modelo detalhado, com texturas assadas.')})


def _cfg(id_, montar, origem, nos, descricao, esqueleto=None):
    return dict(id=id_, nome=id_, montar=montar, gerador='m4a1/gerar_troca.py', origem=enc(*origem),
                esqueleto=esqueleto or {'nos': [], 'animacoes': []}, nos=nos, descricao=descricao + _FIM)


def _olho(origem, y, z):
    """Nó "olho" (linha de visada) no espaço do acessório, a partir de um ponto no espaço da arma."""
    return _so(('olho', [0.0, round(y - origem[1], 4), round(z - origem[2], 4)]))


M = POS['encaixe_mira']
ACESSORIOS = {
    'guarda_mao_classico_m4': _cfg(
        'guarda_mao_classico_m4', montar_classico, POS['encaixe_guarda_mao'],
        {None: ['guarda_mao_superior', 'guarda_mao_inferior', 'anel_delta', 'tampa_guarda_mao', 'base_massa',
                'pino_base_massa_1', 'pino_base_massa_2', 'pino_massa', 'zarelho_frontal']},
        'Guarda-mão de trilho quádruplo com anel delta e a base de massa fixa no cano: a massa de mira e o zarelho da '
        'frente vêm com ele. Não tem trilho livre para empunhadura, lanterna ou laser.'),
    'guarda_mao_longo_m4': _cfg(
        'guarda_mao_longo_m4', montar_longo, POS['encaixe_guarda_mao'],
        {None: ['guarda_mao_longo', 'porca_cano', 'bloco_gas']},
        'Guarda-mão longo vazado com trilho contínuo em cima e fendas dos lados e embaixo: recebe empunhadura, '
        'lanterna, laser, bipé, massa rebatível e a mira a 45°. Bloco de gás baixo, sem massa fixa.'),
    'alca_transporte_m4': _cfg(
        'alca_transporte_m4', montar_alca, M,
        {None: ['alca_transporte', 'alca_mira', 'botao_deriva', 'tambor_elevacao', 'porca_alca_1', 'porca_alca_2']},
        'Alça de transporte com a mira de furo, tambor de elevação e botão de deriva. Mira junto com a massa fixa do '
        'guarda-mão clássico.', _olho(M, 0.1556, 0.0)),
    'luneta_m4': _cfg(
        'luneta_m4', montar_luneta, M, {None: ['luneta', 'suporte_luneta']},
        'Luneta de 2 a 8× em suporte de peça única com dois anéis, torres recartilhadas e alavanca de aumento.',
        _olho(M, 0.161, 0.02)),
    'mira_prismatica_m4': _cfg(
        'mira_prismatica_m4', montar_prismatica, M,
        {None: ['mira_prismatica', 'tampa_lente_frente', 'tampa_lente_tras', 'suporte_prismatica']},
        'Mira prismática de 3× com retículo iluminado, tampas de lente basculantes e suporte alto.', _olho(M, 0.167, -0.033)),
    'mira_45_m4': _cfg(
        'mira_45_m4', montar_reflex, POS['encaixe_mira_45'], {None: ['mira_reflex', 'suporte_45']},
        'Mira reflex pequena num suporte inclinado a 45° no trilho de cima do guarda-mão longo, para usar ao lado da '
        'luneta ou da prismática.'),
    'punho_vazado_m4': _cfg(
        'punho_vazado_m4', montar_punho, POS['encaixe_punho'], {None: ['punho_vazado']},
        'Punho de alumínio vazado, mais em pé, com ressalto para o dedo médio.'),
    'alavanca_ambi_m4': _cfg(
        'alavanca_ambi_m4', montar_alavanca, POS['alavanca'], {None: ['alavanca_ambi']},
        'Alavanca de manejo com asas dos dois lados (caramelo): dá para puxar com qualquer mão.'),
    'coronha_moderna_ar': _cfg(
        'coronha_moderna_ar', montar_coronha, POS['encaixe_coronha'],
        {None: ['tubo_coronha_vermelho', 'placa_traseira', 'porca_castelo', 'coronha_moderna', 'trava_coronha_moderna']},
        'Coronha moderna de polímero com apoio de rosto e soleira de borracha, num tubo octogonal vermelho.'),
}
