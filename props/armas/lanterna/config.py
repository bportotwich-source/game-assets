"""O que a fábrica (../m4a1/fabrica.py) precisa saber da lanterna: uma entrada por id do catálogo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import materiais, modelo, fabrica


def _cfg(q, gasto):
    def montar():
        modelo.GASTO = gasto
        return modelo.lanterna()
    return dict(nome=q, montar=montar, gerador='lanterna/jogo.py', id=q, origem=(0, 0, 0),
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{q}.json'), encoding='utf-8')),
                nos={None: ['lanterna', 'led', 'vidro']},
                lisos=dict(vidro=fabrica.VIDRO, led=fabrica.aceso('led_lanterna', (0.95, 0.92, 0.7))))


ACESSORIOS = {'lanterna_compacta': _cfg('lanterna_compacta', False), 'lanterna_compacta_gasto': _cfg('lanterna_compacta_gasto', True)}
