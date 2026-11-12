"""O que a fábrica (../m4a1/fabrica.py) precisa saber das miras: uma entrada por id do catálogo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import materiais, modelo, fabrica


def _esq(qual):
    return json.load(open(os.path.join(AQUI, f'esqueleto_{qual}.json'), encoding='utf-8'))


def _montar(f, gasto):
    def m():
        modelo.GASTO = gasto
        return f()
    return m


def _reflexa(qual, gasto):
    return dict(nome=qual, montar=_montar(modelo.mira_reflexa, gasto), gerador='miras/jogo.py', id=qual, origem=(0, 0, 0),
                esqueleto=_esq(qual), nos={None: ['mira', 'lente']}, optica=modelo.optica_reflexa(),
                vidro=['lente'])                       # a lente sai transparente (o jogo acende o ponto nela)


def _ferro(qual, f):
    return dict(nome=qual, montar=_montar(f, False), gerador='miras/jogo.py', id=qual, origem=(0, 0, 0),
                esqueleto=_esq(qual), nos={None: ['base'], 'lamina': ['lamina']})


def _pinos():
    q = 'mira_pinos_luz'
    cores = {'verde': (0.2, 1.0, 0.3), 'amarelo': (1.0, 0.85, 0.05), 'vermelho': (1.0, 0.1, 0.05)}
    lisos = {'fibra_' + c: fabrica.aceso('fibra_' + c, rgb) for c, rgb in cores.items()}
    lisos.update(vidro=fabrica.VIDRO, luz=fabrica.aceso('luz_mira', (0.75, 0.9, 1.0)))
    # o vidro do aro não se chama "lente" de propósito: o jogo acende um ponto vermelho em toda malha "_lente"
    return dict(nome=q, montar=modelo.mira_pinos, gerador='miras/jogo.py', id=q, origem=(0, 0, 0), esqueleto=_esq(q),
                nos={None: ['mira', 'vidro', 'luz'] + ['fibra_' + c for c in cores]}, lisos=lisos)


ACESSORIOS = {
    'mira_pinos_luz': _pinos(),
    'mira_reflexa': _reflexa('mira_reflexa', False),
    'mira_reflexa_gasto': _reflexa('mira_reflexa_gasto', True),
    'alca_rebativel': _ferro('alca_rebativel', modelo.alca_rebativel),
    'massa_rebativel': _ferro('massa_rebativel', modelo.massa_rebativel),
}
