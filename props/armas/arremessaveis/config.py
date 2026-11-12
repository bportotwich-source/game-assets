"""O que a fábrica (../m4a1/fabrica.py) precisa saber dos arremessáveis (um CFG por arma)."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import fabrica

FIM = ' Modelo detalhado, com texturas assadas.'
VIDRO_GARRAFA = {'name': 'vidro_garrafa', 'alphaMode': 'BLEND', 'doubleSided': True,
                 'pbrMetallicRoughness': {'baseColorFactor': [0.16, 0.36, 0.14, 0.42], 'metallicFactor': 0.0, 'roughnessFactor': 0.06}}


def _montar(qual):
    def montar():
        import materiais, modelo
        getattr(modelo, qual)()
    return montar


def _cfg(qual, nos, descricao, tris_leve, **mais):
    return dict(nome=qual, montar=_montar(qual), gerador='arremessaveis/jogo.py', tris_leve=tris_leve,
                esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{qual}.json'), encoding='utf-8')),
                nos=nos, origem=(0, 0, 0), variantes={'': (qual, descricao + FIM)}, **mais)


CFGS = {
    'coquetel_molotov': _cfg(
        'coquetel_molotov', {None: ['rotulo', 'vidro', 'combustivel'], 'pavio': ['pavio']},
        'Garrafa de vidro com combustível e um pano enfiado no gargalo, amarrado com barbante. Acenda o pano e jogue: quebra ao bater e deixa uma poça de fogo por alguns segundos. Ilumina a noite, mas chama atenção.',
        1800, lisos={'vidro': VIDRO_GARRAFA}),       # vidro verde transparente: vê-se o combustível dentro
    'bomba_pregos': _cfg(
        'bomba_pregos', {None: ['lata'], 'pavio': ['pavio']},
        'Lata vazia fechada com fita, cheia de pregos por dentro e por fora, com um pavio verde na tampa. Acenda, jogue e corra: estoura 4 s depois e derruba um grupo, mas o estrondo atrai tudo num raio grande.',
        2400),
    'isca_sonora': _cfg(
        'isca_sonora', {None: ['caixa', 'vidro'], 'ponteiro_horas': ['ponteiro_horas'], 'ponteiro_minutos': ['ponteiro_minutos'],
                        'ponteiro_alarme': ['ponteiro_alarme'], 'martelo': ['martelo']},
        'Despertador de corda com duas campainhas. Dê corda, jogue longe e ele toca por uns 20 s: os zumbis vão atrás do barulho. Dá para pegar de volta e usar de novo, se ninguém pisar nele.',
        2400, lisos={'vidro': fabrica.VIDRO}, fora_leve=['vidro']),
}
