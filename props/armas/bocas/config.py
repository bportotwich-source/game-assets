"""O que a fábrica (../m4a1/fabrica.py) precisa saber das bocas de cano: uma entrada por id do catálogo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import materiais, modelo

IDS = ['supressor_556_tan', 'supressor_762_gasto', 'quebra_chamas_556', 'freio_boca_308', 'freio_rompimento_12',
       'protetor_rosca_308', 'protetor_rosca_9mm']


def _cfg(q):
    return dict(nome=q, montar=getattr(modelo, q), gerador='bocas/jogo.py', id=q, origem=(0, 0, 0),
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{q}.json'), encoding='utf-8')), nos={None: ['boca']})


ACESSORIOS = {q: _cfg(q) for q in IDS}
