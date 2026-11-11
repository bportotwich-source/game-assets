"""O que a fábrica (../m4a1/fabrica.py) precisa saber dos bastões (com pregos e com arame farpado)."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def _montar(qual):
    def f():
        import materiais, modelo
        getattr(modelo, 'montar_' + qual)()
    return f


def _cfg(qual, descricao):
    return dict(
        nome='bastao_' + qual, montar=_montar(qual), gerador='bastao/jogo.py', tris_leve=4000,
        origem=(60, 0, 0),               # a mão de baixo na origem, como nos bastões antigos
        esqueleto=json.load(open(os.path.join(AQUI, f'esqueleto_{qual}.json'), encoding='utf-8')),
        nos={None: ['taco']},
        variantes={'': ('bastao_' + qual, descricao)})


CFGS = {
    'pregos': _cfg('pregos', 'Taco de madeira com uns vinte pregos batidos na parte grossa, alguns entortados, e pega de fita isolante. '
                             'Bate bem mais que o taco e rasga, mas às vezes prende no alvo e precisa ser arrancado. Feito na bancada com uma '
                             'caixa de pregos. Modelo detalhado, com texturas assadas (veio, mossas, fita enrolada).'),
    'arame': _cfg('arame', 'Taco de madeira com arame farpado enrolado na parte grossa, pontas amarradas e torcidas, e pega de fita isolante. '
                           'Rasga e faz sangrar; prende menos que o de pregos, mas o arame afrouxa e quebra antes. Feito na bancada com um rolo '
                           'de arame farpado. Modelo detalhado, com texturas assadas (veio, mossas, fita enrolada).'),
}
