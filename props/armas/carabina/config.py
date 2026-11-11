"""O que a fábrica (../m4a1/fabrica.py) precisa saber da carabina Paciência .308.
VARIANTE=caca troca a montagem (modelo.py) e usa os nós da carabina de caça antiga."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
CACA = os.environ.get('VARIANTE', '') == 'caca'


def montar():
    import materiais, modelo
    modelo.montar()


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, gravações).'
_ACAO = {'gatilho': ['gatilho'], 'ferrolho': ['ferrolho'], 'carregador': ['carregador']}
CFG = dict(
    nome='paciencia_caca' if CACA else 'paciencia', montar=montar, gerador='carabina/jogo.py', tris_leve=6000,
    origem=(-80, -68, 0) if CACA else (-93, -80, 0),            # ponto do punho na origem, como nas armas antigas
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto_caca.json' if CACA else 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos=({None: ['receptor', 'cano', 'coronha', 'ferragem', 'placas'], **_ACAO} if CACA else
         {None: ['receptor', 'cano', 'chassi', 'punho', 'guarda_mao', 'coronha'], 'apoio_face': ['apoio_face'], **_ACAO}),
    variantes={
        '': ('carabina_308',
             'Carabina de precisão em chassi de alumínio areia: cano pesado estriado, guarda-mão com fendas, coronha com apoio de rosto. '
             'Derruba um zumbi a 150 m com um tiro na cabeça, mas o estampido se ouve a 220 m.' + _FIM),
        'caca': ('carabina_308_caca',
                 'A mesma ação na coronha de nogueira quadriculada, com luneta 4×. Mais leve e fácil de achar em sítios e casas de campo.' + _FIM),
    })
