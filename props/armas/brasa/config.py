"""O que a fábrica (../m4a1/fabrica.py) precisa saber do fuzil Brasa 7,62 e dos acessórios que vêm
montados nele (coronha e guarda-mão de madeira, freio de boca)."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def _ler(nome):
    return json.load(open(os.path.join(AQUI, nome), encoding='utf-8'))


def _montar(qual):
    def f():
        import materiais, modelo
        getattr(modelo, qual)()
    return f


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, gravações).'
CFG = dict(
    nome='brasa', montar=_montar('montar'), gerador='brasa/jogo.py', tris_leve=6000,
    origem=(-18, -84, 0),            # ponto do punho na origem, como no Brasa antigo
    esqueleto=_ler('esqueleto.json'),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['receptor', 'punho', 'cano'], 'tampa': ['tampa'], 'gatilho': ['gatilho'], 'seletor': ['seletor'],
         'ferrolho': ['ferrolho'], 'carregador': ['carregador']},
    variantes={
        '': ('fuzil_762',
             'Fuzil de receptor estampado e rebitado, guarda-mão e coronha de madeira laminada, tubo de gás por cima do cano. '
             'Aguenta sujeira e falta de manutenção como nenhum outro, mas coice forte e mira de ferro grosseira.' + _FIM),
    })

# acessórios que vêm montados no fuzil: nome da função de modelo.py, id, ponto do encaixe e peças
_FIM_AC = ' Modelo detalhado, do Brasa 7,62 refeito.'
ACESSORIOS = {
    'coronha': dict(
        nome='coronha_brasa', montar=_montar('coronha_madeira'), gerador='brasa/jogo.py', id='coronha_madeira_ak',
        origem=(-81, 1, 0), esqueleto=_ler('esqueleto_coronha_madeira_ak.json'), nos={None: ['coronha']},
        descricao='Coronha fixa de madeira laminada com soleira de aço, tampa do estojo de limpeza e zarelho da bandoleira. Vem no fuzil.' + _FIM_AC),
    'guarda_mao': dict(
        nome='guarda_mao_brasa', montar=_montar('guarda_mao_madeira'), gerador='brasa/jogo.py', id='guarda_mao_madeira_ak',
        origem=(190, 0, 0), esqueleto=_ler('esqueleto_guarda_mao_madeira_ak.json'), nos={None: ['guarda_mao']},
        descricao='Guarda-mão de madeira laminada envernizada, com sulco para os dedos e capa em volta do tubo de gás. Vem no fuzil.' + _FIM_AC),
    'freio': dict(
        nome='freio_brasa', montar=_montar('freio'), gerador='brasa/jogo.py', id='freio_ak',
        origem=(570, 0, 0), esqueleto=_ler('esqueleto_freio_ak.json'), nos={None: ['freio']},
        descricao='Bocal cortado em diagonal que empurra o gás para cima e segura a subida do cano. Vem no fuzil.' + _FIM_AC),
}
