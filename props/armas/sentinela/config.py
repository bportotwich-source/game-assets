"""O que a fábrica (../m4a1/fabrica.py) precisa saber da Sentinela."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, pontilhado no punho, gravações).'
_COR = lambda nome: (f'A mesma Sentinela com armação {nome}, ferrolho preto e cano dourado. Aceita os mesmos acessórios.' + _FIM)
CFG = dict(
    nome='sentinela', montar=montar, gerador='sentinela/jogo.py', tris_leve=6000,
    origem=(6, -68, 0),              # ponto do punho na origem, como nas outras armas
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['armacao', 'pinos', 'retem_ferrolho', 'alavanca_desmontagem', 'retem_carregador'],
         'gatilho': ['gatilho'], 'cano': ['cano'],
         'ferrolho': ['ferrolho', 'tampa_mira', 'alca_mira', 'massa_mira', 'extrator', 'placa_traseira'],
         'carregador': ['carregador']},
    # VARIANTE='' é a preta; as cores são o mesmo modelo com outro bake (materiais.py)
    variantes={
        '': ('pistola_9mm',
             'Pistola de polímero com ferrolho de aço quadrado e punho com cavas e pontilhado, 15 tiros. Leve e confiável, '
             'mas o tiro chama zumbis num raio de 60 m.' + _FIM),
        'tan': ('pistola_9mm_tan', _COR('areia')),
        'verde': ('pistola_9mm_verde', _COR('verde-oliva')),
        'cinza': ('pistola_9mm_cinza', _COR('cinza')),
    })
