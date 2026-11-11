"""O que a fábrica (../m4a1/fabrica.py) precisa saber do arco recurvo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
CFG = dict(
    nome='recurvo', montar=montar, gerador='recurvo/jogo.py', tris_leve=6000,
    origem=(-8, -22, 0),             # centro da empunhadura na origem, como no arco antigo
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['punho'], 'braco_cima': ['braco_cima'], 'braco_baixo': ['braco_baixo'], 'corda_cima': ['corda_cima'],
         'corda_baixo': ['corda_baixo'], 'flecha': ['flecha']},
    variantes={
        '': ('arco_recurvo',
             'Arco desmontável de punho de madeira laminada e braços recurvos de fibra com miolo de bordo (40 lb). Quase não faz barulho, '
             'a flecha pode ser recuperada (70%) e mata zumbi com um tiro na cabeça. Puxar e segurar cansa: não dá para manter mirado '
             'muito tempo. Modelo detalhado, com texturas assadas (laminado do punho, corda torcida, gravações).'),
    })
