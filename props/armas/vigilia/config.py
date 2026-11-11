"""O que a fábrica (../m4a1/fabrica.py) precisa saber do fuzil Vigília 5,56 e da coronha retrátil dos fuzis.
VARIANTE=bicolor (fuzil) ou VARIANTE=tan (coronha) troca as cores em montagem.py."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
VARIANTE = os.environ.get('VARIANTE', '')


def _ler(nome):
    return json.load(open(os.path.join(AQUI, nome), encoding='utf-8'))


def montar():
    import materiais, montagem
    montagem.montar()


def montar_coronha():
    import materiais, montagem
    montagem.coronha()


_FIM = ' Modelo detalhado, feito com as peças da M4A1 e texturas assadas.'
CFG = dict(
    nome='vigilia_bicolor' if VARIANTE == 'bicolor' else 'vigilia', montar=montar, gerador='vigilia/jogo.py', tris_leve=6000,
    origem=(-37, -93, 0),            # ponto do punho na origem, como no Vigília antigo
    esqueleto=_ler('esqueleto.json'),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['receptor_superior', 'impulsor_ferrolho', 'receptor_inferior', 'guarda_mato', 'retem_carregador', 'pino_pivo',
                'pino_desmontagem', 'pino_gatilho', 'pino_cao', 'pino_armadilha', 'cano', 'guarda_mao_longo', 'porca_cano', 'bloco_gas'],
         'punho': ['punho'], 'gatilho': ['gatilho'], 'seletor': ['seletor'], 'ferrolho': ['ferrolho'],
         'alavanca': ['alavanca_manejo', 'trava_alavanca'], 'tampa_janela': ['tampa_janela'], 'retem_ferrolho': ['retem_ferrolho'],
         'carregador': ['carregador_polimero']},
    variantes={
        '': ('fuzil_556',
             'Fuzil de receptor de alumínio, guarda-mão longo vazado e trilho contínuo em cima. Seletor de tiro automático, '
             'muitos encaixes. Rajadas gastam munição rápido e chamam a horda a 160 m.' + _FIM),
        'bicolor': ('fuzil_556_bicolor',
                    'O mesmo fuzil com guarda-mão, punho, carregador e coronha caramelo e receptor preto. Vem montado com '
                    'luneta 1-6×, supressor, lanterna compacta e empunhadura curta.' + _FIM),
    })

# coronha retrátil dos fuzis (acessórios coronha_retratil_ar e coronha_retratil_ar_tan)
_TAN = VARIANTE == 'tan'
CFG_CORONHA = dict(
    nome='coronha_vigilia_tan' if _TAN else 'coronha_vigilia', montar=montar_coronha, gerador='vigilia/jogo.py',
    id='coronha_retratil_ar_tan' if _TAN else 'coronha_retratil_ar',
    origem=(0, 0, 0),                # começo do tubo no encaixe_coronha
    esqueleto=_ler('esqueleto_coronha.json'),
    nos={None: ['tubo_coronha', 'placa_traseira', 'porca_castelo'], 'soleira': ['coronha', 'trava_coronha', 'zarelho_traseiro']},
    descricao=('Coronha retrátil de 5 posições em polímero caramelo. ' if _TAN else
               'Tubo com coronha de polímero de 5 posições. Nó "soleira", animações estender/recolher. ')
              + 'Modelo detalhado, a coronha da M4A1.')
