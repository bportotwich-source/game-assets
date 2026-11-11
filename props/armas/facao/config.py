"""O que a fábrica (../m4a1/fabrica.py) precisa saber do facão."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
DESCRICAO = ('Lâmina de 34 cm de aço carbono escurecido que alarga na ponta para pesar no golpe. Talas de madeira com rebites de latão '
             'e fiel de couro. Alcança mais que a faca e abre caminho no mato, mas o golpe é mais lento. Modelo detalhado, com texturas '
             'assadas (aço gasto, fio polido, veio da madeira).')
CFG = dict(
    nome='facao', montar=montar, gerador='facao/jogo.py', tris_leve=3000,
    origem=(-65, 0, 0),             # meio do cabo na origem, como no facão antigo
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    nos={None: ['lamina', 'cabo']},
    variantes={
        '': ('facao',
             DESCRICAO),
    })
