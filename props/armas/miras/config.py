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


def _olho(x, y, z):
    return {'nos': [{'no': 'olho', 'pai': None, 'posicao': [x, y, z]}], 'animacoes': []}


def _ponto(qual, f, optica, olho, vidro=('lente',), areia=False):
    def m():
        modelo.GASTO = False
        modelo.AREIA = areia
        return f()
    return dict(nome=qual, montar=m, gerador='miras/jogo.py', id=qual, origem=(0, 0, 0), esqueleto=_olho(*olho),
                nos={None: ['mira'] + list(vidro)}, optica=optica, vidro=list(vidro))


def _polimero(qual, f, tan):
    def m():
        modelo.GASTO = False
        modelo.POLIM = 'tan' if tan else 'polim'
        return f()
    return dict(nome=qual, montar=m, gerador='miras/jogo.py', id=qual, origem=(0, 0, 0),
                esqueleto=_esq(qual.replace('_tan', '')), nos={None: ['base'], 'lamina': ['lamina']})


def _tubo():
    q = 'mira_ponto_vermelho_tubo'
    d = _ponto(q, modelo.mira_tubo, modelo.optica_tubo(), (0, 0, 0), vidro=('lente', 'vidro'))
    d.update(esqueleto=_esq(q), nos={None: ['mira', 'lente', 'vidro'], 'tampa_frente': ['tampa_frente'], 'tampa_tras': ['tampa_tras']})
    return d


def _lateral(qual, f, optica, olho, corpo='mira', vidro=('lente', 'vidro')):
    d = _ponto(qual, f, optica, olho, vidro=vidro)
    d.update(nos={None: [corpo, 'lente'] + [v for v in vidro if v != 'lente']})
    return d


def _pinos_arco():
    q = 'mira_pinos_arco'
    cores = {'verde': (0.2, 1.0, 0.3), 'amarelo': (1.0, 0.5, 0.05), 'vermelho': (1.0, 0.1, 0.05)}
    return dict(nome=q, montar=modelo.mira_pinos_arco, gerador='miras/jogo.py', id=q, origem=(0, 0, 0),
                esqueleto=_olho(-0.0176, -0.01, 0.632), nos={None: ['mira'] + ['fibra_' + c for c in cores]},
                lisos={'fibra_' + c: fabrica.aceso('fibra_arco_' + c, rgb) for c, rgb in cores.items()})


_PONTE = (modelo.optica_micro(modelo.PU, modelo.PV0), (0.0, 0.0627, -0.0015))

ACESSORIOS = {
    'mira_ponto_vermelho_compacta': _ponto('mira_ponto_vermelho_compacta', modelo.mira_compacta, modelo.optica_micro(), (0.0, 0.0145, 0.0)),
    'ponte_mira_pistola': _ponto('ponte_mira_pistola', modelo.ponte_mira, *_PONTE),
    'ponte_mira_pistola_tan': _ponto('ponte_mira_pistola_tan', modelo.ponte_mira, *_PONTE, areia=True),
    'mira_ponto_vermelho_revolver': _ponto('mira_ponto_vermelho_revolver', modelo.mira_tubo_revolver, modelo.optica_tubo_revolver(),
                                           (0.0, 0.0215, 0.03), vidro=('lente', 'vidro')),
    'mira_holografica': _ponto('mira_holografica', modelo.mira_holografica, modelo.optica_holografica(), (0.0, 0.0288, 0.012),
                               vidro=('lente', 'vidro')),
    'mira_ponto_vermelho_tubo': _tubo(),
    'alca_polimero': _polimero('alca_polimero', modelo.alca_polimero, False),
    'alca_polimero_tan': _polimero('alca_polimero_tan', modelo.alca_polimero, True),
    'massa_polimero': _polimero('massa_polimero', modelo.massa_polimero, False),
    'massa_polimero_tan': _polimero('massa_polimero_tan', modelo.massa_polimero, True),
    'mira_lateral_ak': _lateral('mira_lateral_ak', modelo.mira_lateral, modelo.optica_lateral(), (0.0163, 0.058, 0.035)),
    'luneta_lateral_ak': _lateral('luneta_lateral_ak', modelo.luneta_lateral, modelo.optica_luneta_lateral(), (0.0163, 0.061, 0.092),
                                  corpo='luneta', vidro=()),
    'mira_pinos_arco': _pinos_arco(),
    'mira_pinos_luz': _pinos(),
    'mira_reflexa': _reflexa('mira_reflexa', False),
    'mira_reflexa_gasto': _reflexa('mira_reflexa_gasto', True),
    'alca_rebativel': _ferro('alca_rebativel', modelo.alca_rebativel),
    'massa_rebativel': _ferro('massa_rebativel', modelo.massa_rebativel),
}
