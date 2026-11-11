"""O que a fábrica (../m4a1/fabrica.py) precisa saber da machadinha tática."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
DESCRICAO = ('Cabeça e espiga numa peça só de aço escurecido: fio curvo com barba de um lado e ponta do outro para arrombar portas e '
             'janelas. Cabo com talas e cordão enrolado (dá para desenrolar e usar o cordão). Bate mais forte que o facão, mas alcança '
             'menos. Modelo detalhado, com texturas assadas (aço gasto nas quinas, fio polido, voltas do cordão).')
CFG = dict(
    nome='machadinha', montar=montar, gerador='machadinha/jogo.py', tris_leve=4000,
    origem=(0, 90, 0),               # a mão na origem, como na machadinha antiga
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    nos={None: ['cabeca', 'cabo']},
    variantes={
        '': ('machadinha_tatica',
             DESCRICAO),
    })
