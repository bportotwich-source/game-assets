"""O que a fábrica (../m4a1/fabrica.py) precisa saber das flechas e virotes: uma entrada por id do catálogo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import materiais, modelo


def _cfg(q):
    return dict(nome=q, montar=lambda: modelo.flecha(q), gerador='flechas/jogo.py', id=q, grupo='municao', origem=(0, 0, 0),
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{q}.json'), encoding='utf-8')), nos={None: ['flecha']})


ACESSORIOS = {q: _cfg(q) for q in modelo.SPECS}
