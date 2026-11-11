"""O que a fábrica (../m4a1/fabrica.py) precisa saber do rifle Pardal .22.
VARIANTE=sintetico troca a madeira da coronha por polímero (materiais.py) e usa os nós do sintético antigo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
SINT = os.environ.get('VARIANTE', '') == 'sintetico'


def montar():
    import materiais, modelo
    modelo.montar()


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, gravações).'
CFG = dict(
    nome='pardal_sintetico' if SINT else 'pardal', montar=montar, gerador='pardal/jogo.py', tris_leve=6000,
    origem=(-78, -62, 0),            # ponto do punho na origem, como no rifle antigo
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto_sintetico.json' if SINT else 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['receptor', 'cano', 'coronha', 'ferragem', 'placas'], 'gatilho': ['gatilho'], 'ferrolho': ['ferrolho'],
         'carregador': ['carregador']},
    variantes={
        '': ('rifle_22',
             'Rifle leve de ferrolho na coronha de nogueira, com luneta 4× pequena. Para caça pequena (coelho, pombo): barulho baixo '
             'e munição barata e fácil de achar. Mata zumbi só com tiro na cabeça. Com o supressor quase não se ouve.' + _FIM),
        'sintetico': ('rifle_22_sintetico',
                      'O mesmo rifle numa coronha preta de polímero que não liga para chuva. Vem só com as miras de ferro.' + _FIM),
    })


def _ac(qual):
    def f():
        import materiais, modelo
        getattr(modelo, qual)()
    return f


def _ler(nome):
    return json.load(open(os.path.join(AQUI, nome), encoding='utf-8'))


# acessórios que vêm montados no rifle: função de modelo.py, id, ponto do encaixe e peças de cada nó
ACESSORIOS = {
    'alca': dict(
        nome='alca_pardal', montar=_ac('alca_cano'), gerador='pardal/jogo.py', id='alca_cano_22',
        origem=(180, 10.4, 0), esqueleto=_ler('esqueleto_alca_cano_22.json'), nos={None: ['base'], 'lamina': ['lamina']},
        descricao='Alça de lâmina com entalhe em U, presa no cano por uma sela. Deita para trás quando há luneta. Vem no rifle .22. '
                  'Modelo detalhado, do Pardal .22 refeito.'),
    'protetor': dict(
        nome='protetor_pardal', montar=_ac('protetor_rosca'), gerador='pardal/jogo.py', id='protetor_rosca_22',
        origem=(568, 0, 0), esqueleto=_ler('esqueleto_protetor_rosca_22.json'), nos={None: ['protetor']},
        descricao='Capinha recartilhada que protege a rosca da boca. Vem no rifle. Modelo detalhado, do Pardal .22 refeito.'),
}
