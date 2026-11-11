"""O que a fábrica (../m4a1/fabrica.py) precisa saber da Faísca."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, pontilhado no punho, gravações).'
CFG = dict(
    nome='faisca', montar=montar, gerador='smg/jogo.py', tris_leve=6000,
    origem=(20, -80, 0),             # ponto do punho na origem, como nas outras armas
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['corpo', 'trilhos', 'cano', 'pinos'],
         'gatilho': ['gatilho'], 'seletor': ['seletor'], 'ferrolho': ['ferrolho'], 'alavanca': ['alavanca'],
         'coronha': ['varetas', 'soleira'], 'carregador': ['carregador']},
    # VARIANTE='' é a preta; a caramelo é o mesmo modelo com outro bake do grupo A (materiais.py)
    variantes={
        '': ('smg_9mm',
             'Arma curta de polímero com o carregador dentro do punho e coronha de varetas que encolhe. Cabe numa mochila, '
             'atira rápido e usa a mesma munição da pistola: ótima para limpar corredores.' + _FIM),
        'tan': ('smg_9mm_tan',
                'A mesma submetralhadora com corpo, punho e coronha caramelo; carregador e trilhos pretos.' + _FIM),
    })
