"""O que a fábrica (../m4a1/fabrica.py) precisa saber da faca de combate."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
CFG = dict(
    nome='faca', montar=montar, gerador='faca/jogo.py', tris_leve=3000,
    origem=(-65, -3, 0),             # meio do cabo na origem, como na faca antiga
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    nos={None: ['lamina', 'cabo']},
    variantes={
        '': ('faca_combate',
             'Lâmina de 18 cm de aço escurecido com ponta recortada, fio liso e serrilha perto do cabo para cortar corda. Cabo pontilhado '
             'com cavas e pomo com quebra-vidro. Não faz barulho e não gasta munição, mas é preciso chegar muito perto. Modelo detalhado, '
             'com texturas assadas (desbaste, fio polido, sulco, gravações).'),
    })
