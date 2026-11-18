"""O que a fábrica (../m4a1/fabrica.py) precisa saber dos punhos: uma entrada por id do catálogo.
VARIANTE=tan faz os caramelo (punho_ar_tan, punho_cavas_tan, punho_reto_tan)."""
import sys, os
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]
import materiais, modelo

TAN = os.environ.get('VARIANTE', '') == 'tan'
_FIM = ' Modelo detalhado, com texturas assadas.'
DESCRICAO = {
    'punho_ar': 'O punho que vem no fuzil: polímero com quadriculado dos lados, ressalto para o dedo médio e a base oca com o parafuso.',
    'punho_cavas': 'Borracha moldada com grão de pedrinhas em toda a volta, ressalto para o dedo médio, três cavas para os dedos, palma '
                   'cheia e sapata larga na base. Não escorrega com a mão suada ou molhada.',
    'punho_reto': 'Punho mais em pé, com rabo de castor que protege a mão, painéis de pontilhado fino dos lados, nervuras na frente e '
                  'nas costas e compartimento com tampa no fundo (cabe pilha ou bilhete).',
    'adaptador_punho_762': 'Bloco de aço que aparafusa embaixo do receptor de alumínio e dá a face plana onde assentam os punhos de '
                           '7,62 (baquelite e ergonômico). O jogo põe sozinho quando um punho de 7,62 entra num fuzil 5,56 ou .308.',
}
PECA = {'adaptador_punho_762': 'adaptador'}


def _cfg(q):
    base = q[:-4] if q.endswith('_tan') else q
    desc = DESCRICAO[base] + (' Em caramelo.' if q.endswith('_tan') else '') + _FIM
    return dict(nome=q, montar=getattr(modelo, base), gerador='punhos/jogo.py', id=q, origem=(*modelo.ENCAIXE, 0),
                esqueleto={'nos': [], 'animacoes': []}, nos={None: [PECA.get(base, 'punho')]}, descricao=desc)


IDS = ['punho_ar_tan', 'punho_cavas_tan', 'punho_reto_tan'] if TAN else ['punho_ar', 'punho_cavas', 'punho_reto', 'adaptador_punho_762']
ACESSORIOS = {q: _cfg(q) for q in IDS}
