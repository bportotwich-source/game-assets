"""O que a fábrica (../m4a1/fabrica.py) precisa saber dos apetrechos: uma entrada por id do catálogo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import materiais, modelo

PECA = {'estribo_besta': 'estribo', 'soltador_pulso': 'soltador', 'elastico_ak': 'elastico'}


def _cfg(q):
    return dict(nome=q, montar=getattr(modelo, q), gerador='apetrechos/jogo.py', id=q, origem=(0, 0, 0),
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{q}.json'), encoding='utf-8')), nos={None: [PECA[q]]})


ACESSORIOS = {q: _cfg(q) for q in PECA}
