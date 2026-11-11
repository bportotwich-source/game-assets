"""O que a fábrica (../m4a1/fabrica.py) precisa saber do revólver Vigia."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


CFG = dict(
    nome='revolver', montar=montar, gerador='revolver/jogo.py', tris_leve=6000,
    origem=(-36, -70, 0),            # ponto do punho na origem, como nas outras armas
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['armacao'], 'punho': ['talas'], 'cao': ['cao'], 'gatilho': ['gatilho'], 'trava': ['trava'],
         'braco': ['braco'], 'tambor': ['tambor'], 'extrator': ['extrator']},
    variantes={
        '': ('revolver_38',
             'Revólver de 6 tiros com tambor que abre de lado. Não engasga nunca e é fácil de achar em casas, mas recarrega devagar '
             'sem o carregador rápido. Modelo detalhado, com texturas assadas (aço azulado gasto nas arestas, talas de nogueira '
             'quadriculadas, gravações).'),
    })
