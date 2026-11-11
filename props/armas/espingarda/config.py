"""O que a fábrica (../m4a1/fabrica.py) precisa saber da Mutirão 12.
VARIANTE=curta muda a geometria (modelo.py) e usa os nós da curta antiga."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
CURTA = os.environ.get('VARIANTE', '') == 'curta'


def montar():
    import materiais, modelo
    modelo.montar()


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, pontilhado no punho, gravações).'
CFG = dict(
    nome='mutirao_curta' if CURTA else 'mutirao', montar=montar, gerador='espingarda/jogo.py', tris_leve=6000,
    origem=(-33, -90, 0),            # ponto do punho na origem, como nas outras armas
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto_curta.json' if CURTA else 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['receptor', 'pinos', 'cano', 'protetor'],
         'gatilho': ['gatilho'], 'telha': ['telha'], 'ferrolho': ['ferrolho'], 'elevador': ['elevador'], 'tampa_tubo': ['tampa_tubo']},
    variantes={
        '': ('espingarda_12',
             'Espingarda de bombeamento com coronha retrátil, punho de pistola, protetor de calor e trilho. 5 no tubo; '
             'a curta distância derruba qualquer zumbi, mas o estrondo chama tudo num raio de 110 m. Recarrega um cartucho por vez.' + _FIM),
        'curta': ('espingarda_12_curta',
                  'Versão de cano curto e só punho, com freio dentado na boca: boa para arrombar portas e lutar dentro de casa. '
                  'Espalha mais os bagos e coice forte; aceita coronha.' + _FIM),
    })


def montar_coronha():
    import materiais, coronha
    coronha.montar()


# a coronha retrátil que vem na Mutirão (acessório coronha_retratil_12): python3 gerar.py 1024 saida_coronha coronha
CFG_CORONHA = dict(
    nome='coronha_mutirao', montar=montar_coronha, gerador='espingarda/jogo.py', id='coronha_retratil_12',
    origem=(-35, -4, 0),             # encaixe_coronha
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto_coronha.json'), encoding='utf-8')),
    nos={None: ['tubo_coronha'], 'soleira': ['coronha_corpo', 'trava_coronha', 'zarelho_traseiro']},
    descricao='Tubo com coronha de polímero que corre em 5 posições (nó "soleira", animações estender/recolher). '
              'Segura o coice no ombro. Modelo detalhado, com texturas assadas.')
