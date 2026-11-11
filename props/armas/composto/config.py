"""O que a fábrica (../m4a1/fabrica.py) precisa saber do arco composto."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
_PARES = ('braco', 'polia', 'corda', 'cabo')
CFG = dict(
    nome='composto', montar=montar, gerador='composto/jogo.py', tris_leve=6000,
    origem=(-14, -30, 0),            # centro da pega na origem, como no arco antigo
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['punho', 'pega'], 'laco_d': ['laco_d'], 'visor_corda': ['visor_corda'], 'apoio': ['apoio'], 'flecha': ['flecha'],
         **{f'{p}_{l}': [f'{p}_{l}'] for p in _PARES for l in ('cima', 'baixo')}},
    variantes={
        '': ('arco_composto',
             'Arco de punho de alumínio usinado com polias excêntricas (60 lb, alívio de 80%): a flecha sai mais rápida e reta que no '
             'recurvo, e segurar puxado quase não cansa. Mira de pinos e visor na corda. Polias e cabos precisam de cuidado: corda '
             'gasta arrebenta. Modelo detalhado, com texturas assadas (treliça usinada, corda e cabos torcidos, gravações).'),
    })
