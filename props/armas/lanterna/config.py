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

_FIM = ' Modelo detalhado, com texturas assadas.'
LASER = fabrica.aceso('laser_vermelho', (0.95, 0.06, 0.03))
#   id: (peças soltas de material liso, descrição)
NOVAS = {
    'lanterna_pistola': (('led', 'vidro'), 'Lanterna de 600 lm para o trilho curto das pistolas e do revólver: caixa de alumínio com a pilha '
                         'atravessada, cabeça com coroa dentada e teclas de borracha dos dois lados, ao alcance do dedo.'),
    'laser_pistola': (('emissor',), 'Mira laser vermelha para o trilho curto: caixinha de polímero com ajustes de latão de deriva e elevação, '
                      'botão dos dois lados e pilha de moeda.'),
    'combo_lanterna_laser': (('led', 'vidro', 'emissor'), 'Lanterna de 500 lm com o módulo do laser pendurado embaixo e chave de três posições '
                             'atrás (lanterna, laser ou os dois).'),
    'lanterna_cano_12': (('led', 'vidro'), 'Abraçadeira de duas voltas, no cano e no tubo da espingarda, com a lanterna de 800 lm do lado '
                         'direito e botão de pressão na tampa de trás.'),
    'lanterna_fuzil': (('led', 'vidro'), 'Lanterna de 1000 lm de duas pilhas: corpo comprido recartilhado, pescoço com aletas, cabeça larga e '
                       'suporte de dois anéis aparafusado nas fendas do guarda-mão.'),
    'laser_fuzil': (('led', 'vidro', 'emissor'), 'Caixa de alumínio do lado esquerdo do guarda-mão com mira laser e farolete: seletor de modo e '
                    'botão em cima, ajustes de latão, pilha atrás e tomada para botão remoto.'),
}


def _nova(q):
    soltas, desc = NOVAS[q]
    def montar():
        modelo.GASTO = False
        return getattr(modelo, q)()
    lisos = {}
    if 'vidro' in soltas:
        lisos['vidro'] = fabrica.VIDRO
    if 'led' in soltas:
        lisos['led'] = fabrica.aceso('led_lanterna', (0.95, 0.92, 0.7))
    if 'emissor' in soltas:
        lisos['emissor'] = LASER
    return dict(nome=q, montar=montar, gerador='lanterna/jogo.py', id=q, origem=(0, 0, 0), descricao=desc + _FIM,
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{q}.json'), encoding='utf-8')),
                nos={None: ['corpo'] + list(soltas)}, lisos=lisos)


ACESSORIOS.update({q: _nova(q) for q in NOVAS})
