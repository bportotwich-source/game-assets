"""O que a fábrica (../m4a1/fabrica.py) precisa saber da Ciclone."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, pontilhado no punho e no painel, gravações).'
CFG = dict(
    nome='ciclone', montar=montar, gerador='ciclone/jogo.py', tris_leve=6000,
    origem=(-58, -80, 0),            # ponto do punho na origem, como nas outras armas
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['corpo', 'trilhos', 'cano', 'chassi', 'pinos'],
         'gatilho': ['gatilho'], 'seletor': ['seletor'], 'ferrolho': ['ferrolho'], 'alavanca': ['alavanca'],
         'coronha': ['coronha'], 'carregador': ['carregador']},
    # VARIANTE='' é a preta; a areia é o mesmo modelo com outro bake do grupo A (materiais.py)
    variantes={
        '': ('smg_ciclone_9mm',
             'Submetralhadora de cano alto, na linha do ombro: o coice vai reto para trás e quase não levanta. Atira muito rápido, '
             'aceita carregador de pistola longo e o tambor de 50. A coronha dobra para o lado.' + _FIM),
        'tan': ('smg_ciclone_9mm_tan',
                'A mesma Ciclone com chassi, punho e coronha cor de areia; corpo de cima e carregador pretos.' + _FIM),
    })
