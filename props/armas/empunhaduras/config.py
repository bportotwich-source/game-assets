"""O que a fábrica (../m4a1/fabrica.py) precisa saber das empunhaduras: uma entrada por id do catálogo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import materiais, modelo

NOS = {'empunhadura_reta': {None: ['punho']}, 'empunhadura_curta_tan': {None: ['punho']},
       'empunhadura_dobravel': {None: ['base'], 'haste': ['haste']}}


def _cfg(q):
    return dict(nome=q, montar=getattr(modelo, q), gerador='empunhaduras/jogo.py', id=q, origem=(0, 0, 0),
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{q}.json'), encoding='utf-8')), nos=NOS[q])


ACESSORIOS = {q: _cfg(q) for q in NOS}
