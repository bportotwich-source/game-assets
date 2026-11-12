"""O que a fábrica (../m4a1/fabrica.py) precisa saber das lunetas: uma entrada por id do catálogo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import modelo

# id: (aumento, retículo, retículo iluminado). A descrição do catálogo fica a que já estava.
_DADOS = {
    'luneta_1_6':   ((1, 6), 'cruz', True),
    'luneta_3_9':   ((3, 9), 'cruz', True),
    'luneta_4x':    ((4, 4), 'cruz', False),
    'luneta_4x_22': ((4, 4), 'cruz', False),
    'luneta_5_25':  ((5, 25), 'cruz', True),
    'luneta_besta': ((3, 3), 'besta', True),
}


def _cfg(qual):
    aumento, reticulo, luz = _DADOS[qual]
    return dict(
        nome=qual, montar=lambda: modelo.luneta(qual), gerador='lunetas/jogo.py', id=qual, origem=(0, 0, 0),
        esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{qual}.json'), encoding='utf-8')),
        nos={None: ['luneta', 'lente']},
        optica=modelo.optica(qual, aumento, reticulo, luz))


ACESSORIOS = {q: _cfg(q) for q in _DADOS}
