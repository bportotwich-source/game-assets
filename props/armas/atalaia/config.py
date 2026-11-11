"""O que a fábrica (../m4a1/fabrica.py) precisa saber do fuzil Atalaia .308 de precisão.
VARIANTE=curto é o de cano e guarda-mão curtos."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
VARIANTE = os.environ.get('VARIANTE', '')
CURTO = VARIANTE == 'curto'


def montar():
    import materiais, montagem
    montagem.montar()


def montar_coronha():
    import materiais, montagem
    montagem.coronha()


def _jogo(u, v, w=0.0):
    """Ponto do fuzil pronto (mm; u frente, v cima, w direita) nas coordenadas do jogo (m), com a origem no punho."""
    return [round(w / 1000, 4), round((v + 100) / 1000, 4), round(-(u + 40) / 1000, 4)]


def _m4(u, v, w=0.0):
    """Ponto de uma peça da M4A1 depois de aumentada e levada para a frente."""
    return _jogo(1.1 * u + 158, 1.1 * v, 1.1 * w)


def _esqueleto():
    """Nós e animações do Atalaia antigo; os nós das peças que giram e dos encaixes de cima e de
    trás vão para o lugar das peças novas (trilho 6,5 mm mais alto, receptor mais comprido atrás)."""
    e = json.load(open(os.path.join(AQUI, 'esqueleto_curto.json' if CURTO else 'esqueleto.json'), encoding='utf-8'))
    novo = {'gatilho': _m4(-108, -40), 'seletor': _m4(-140, -31), 'tampa_janela': _m4(-67, -12.3, 12.6),
            'retem_ferrolho': _m4(-74, -21, -13.4), 'carregador': _m4(-40, -16),
            'encaixe_mira': _jogo(90, 33), 'encaixe_alca': _jogo(-45, 33), 'mira_ferro': _jogo(-45, 52.5),
            'encaixe_massa': _jogo((430 if CURTO else 560) - 16, 33), 'encaixe_coronha': _m4(-205, 0),
            'saida_estojo': _jogo(85, 0, 16.5)}
    for n in e['nos']:
        if n['no'] in novo and n['pai'] is None:
            n['posicao'] = novo[n['no']]
    return e


_FIM = ' Modelo detalhado, feito com as peças da M4A1 aumentadas e texturas assadas.'
CFG = dict(
    nome='atalaia_curto' if CURTO else 'atalaia', montar=montar, gerador='atalaia/jogo.py', tris_leve=6000,
    origem=(-40, -100, 0),           # ponto do punho na origem, como no Atalaia antigo
    esqueleto=_esqueleto(),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['receptor_superior', 'impulsor_ferrolho', 'receptor_inferior', 'guarda_mato', 'retem_carregador', 'pino_pivo',
                'pino_desmontagem', 'pino_gatilho', 'pino_cao', 'pino_armadilha', 'cano', 'guarda_mao_oct', 'porca_cano', 'bloco_gas'],
         'punho': ['punho'], 'gatilho': ['gatilho'], 'seletor': ['seletor'], 'ferrolho': ['ferrolho'],
         'alavanca': ['alavanca_manejo', 'trava_alavanca'], 'tampa_janela': ['tampa_janela'], 'retem_ferrolho': ['retem_ferrolho'],
         'carregador': ['carregador_308']},
    variantes={
        '': ('fuzil_308_precisao',
             'Fuzil semiautomático .308 de cano longo e pesado, verde-oliva, com guarda-mão octogonal, coronha de precisão e '
             'luneta 5-25×. Acerta zumbi a 200 m e dá tiros seguidos sem mexer no ferrolho. Pesado e muito barulhento sem supressor.' + _FIM),
        'curto': ('fuzil_308_precisao_curto',
                  'O mesmo fuzil com cano e guarda-mão curtos: mais fácil de virar dentro de casa, um pouco menos preciso de longe.' + _FIM),
    })

# coronha de precisão (acessórios coronha_precisao_ar e coronha_precisao_ar_preta)
_PRETA = VARIANTE == 'preta'
CFG_CORONHA = dict(
    nome='coronha_atalaia_preta' if _PRETA else 'coronha_atalaia', montar=montar_coronha, gerador='atalaia/jogo.py',
    id='coronha_precisao_ar_preta' if _PRETA else 'coronha_precisao_ar',
    origem=(0, 0, 0),                # encaixe_coronha
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto_coronha.json'), encoding='utf-8')),
    nos={None: ['corpo_coronha', 'soleira_coronha', 'monope_coronha'], 'apoio_face': ['apoio_rosto']},
    descricao=('A mesma coronha de precisão, em polímero preto. ' if _PRETA else
               'Coronha fixa alta, verde-oliva, com apoio de rosto que sobe e monopé de rosca: deixa o fuzil quieto deitado. '
               'Serve no tubo de qualquer fuzil. ') + 'Modelo detalhado, com texturas assadas.')
