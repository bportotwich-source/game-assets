"""O que a fábrica (../m4a1/fabrica.py) precisa saber da pistola sinalizadora."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


ACESSORIOS = {}
CFG = dict(
    nome='sinalizadora', montar=montar, gerador='sinalizadora/jogo.py', tris_leve=4000,
    origem=(-58, -60, 0),            # ponto do punho na origem, como na pistola antiga
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['armacao', 'tala_esquerda', 'tala_direita', 'parafusos_talas'], 'cano': ['cano'], 'cartucho': ['cartucho'],
         'cao': ['cao'], 'gatilho': ['gatilho'], 'trava': ['trava']},
    variantes={
        '': ('pistola_sinalizadora',
             'Pistola de sinal de alumínio laranja, um tiro por vez. Não é arma: o sinal sobe uns 80 m e brilha 7 s. Vermelho pede socorro; '
             'verde chama sobreviventes para a sua posição, mas os zumbis também veem. De perto, o cartucho queima o alvo. '
             'Modelo detalhado, com texturas assadas (desgaste nas arestas, quadriculado nas talas, gravações).'),
    })
