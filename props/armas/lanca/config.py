"""O que a fábrica (../m4a1/fabrica.py) precisa saber da lança improvisada."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
DESCRICAO = 'Cabo de vassoura com uma faca de cozinha enfiada na ponta serrada, presa com prego, abraçadeiras, fita prata e arame. Mantém o zumbi a 1,5 m, mas a faca pode prender no alvo e a fita afrouxa com o uso. Feita na hora, sem bancada; o cabo pode vir de vassoura, rodo ou enxada. Modelo detalhado, com texturas assadas (tinta lascada, fita e pano enrolados, abraçadeiras).'
CFG = dict(
    nome='lanca', montar=montar, gerador='lanca/jogo.py', tris_leve=4000,
    origem=(-250, 0, 0),             # a mão de trás na origem, como na lança antiga
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    nos={None: ['cabo'], 'amarracao': ['amarracao'], 'faca': ['faca']},
    variantes={
        '': ('lanca_improvisada',
             DESCRICAO),
    })
