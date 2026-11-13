"""O que a fábrica (../m4a1/fabrica.py) precisa saber das coronhas de troca: uma entrada por id do
catálogo. VARIANTE=tan faz as caramelo (coronha_leve_ar_tan, coronha_leve_ak_tan)."""
import sys, os, json, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [AQUI, os.path.join(ARMAS, 'm4a1')]
VARIANTE = os.environ.get('VARIANTE', '')


def _ler(nome):
    return json.load(open(os.path.join(AQUI, nome), encoding='utf-8'))


def _montar(qual):
    def f():
        import texturas
        spec = importlib.util.spec_from_file_location('brasa_materiais', os.path.join(ARMAS, 'brasa', 'materiais.py'))
        spec.loader.exec_module(importlib.util.module_from_spec(spec))      # aço oxidado do 7,62
        import montagem
        getattr(montagem, qual)()
    return f


_FIM = ' Modelo detalhado, com texturas assadas.'
TUBO = ['tubo_coronha', 'placa_traseira', 'porca_castelo']
CORPO = ['coronha', 'trava_coronha']
#        id: (função, nome do bake, origem = encaixe_coronha, nós, descrição)
_T = {
    'coronha_fixa_ar': ('montar_fixa', 'coronha_fixa', (-197, 0, 0), {None: ['coronha']},
                        'Coronha fixa inteiriça de polímero, comprida e firme, com painéis rebaixados dos lados, porta do '
                        'compartimento e soleira de borracha nervurada. Mais pesada que a retrátil.'),
    'coronha_fixa_12': ('montar_fixa', 'coronha_fixa', (-197, 0, 0), {None: ['coronha']},
                        'Coronha fixa inteiriça de polímero para a espingarda, com soleira de borracha nervurada e zarelho da '
                        'bandoleira. Mais pesada e firme que a retrátil.'),
    'coronha_leve_ar': ('montar_leve', 'coronha_leve', (-197, 0, 0), {None: TUBO, 'soleira': CORPO},
                        'Coronha leve de polímero com o quadro de baixo vazado e soleira de borracha; corre no tubo em 5 posições '
                        '(nó "soleira", animações estender/recolher).'),
    'coronha_leve_ak': ('montar_leve_ak', 'coronha_leve_ak', (-165, 0, 0), {None: ['adaptador'] + TUBO, 'soleira': CORPO},
                        'Adaptador de aço que recebe o tubo de 5 posições, com a coronha leve vazada (nó "soleira").'),
    'coronha_retratil_ak': ('montar_retratil_ak', 'coronha_retratil_ak', (-165, 0, 0),
                            {None: ['adaptador'] + TUBO, 'soleira': ['coronha', 'trava_coronha', 'zarelho_traseiro']},
                            'Adaptador de aço que recebe o tubo e a coronha retrátil de 5 posições (a mesma do fuzil 5,56). '
                            'Nó "soleira", animações estender/recolher.'),
    'coronha_polimero_ak': ('montar_polimero_ak', 'coronha_polimero_ak', (-165, 0, 0), {None: ['coronha']},
                            'Coronha fixa de polímero preto no desenho da de madeira, com painel rebaixado dos lados (mais leve) '
                            'e soleira de borracha.'),
    'coronha_rebativel_ak': ('montar_rebativel_ak', 'coronha_rebativel_ak', (-165, 0, 0), {None: ['base'], 'dobra': ['coronha']},
                             'Coronha de tubos de aço soldados com soleira de borracha, que dobra para a esquerda na dobradiça '
                             '(nó "dobra", animações dobrar/abrir).'),
}
_T['coronha_leve_ar_tan'] = _T['coronha_leve_ar'][:4] + ('A mesma coronha leve vazada, em polímero caramelo; corre no tubo em 5 posições.',)
_T['coronha_leve_ak_tan'] = _T['coronha_leve_ak'][:4] + ('Adaptador de aço com a coronha leve vazada em caramelo (nó "soleira").',)


def _cfg(q):
    f, nome, org, nos, desc = _T[q]
    return dict(nome=nome + ('_tan' if q.endswith('_tan') else ''), montar=_montar(f), gerador='coronhas/jogo.py', id=q, origem=org,
                esqueleto=_ler(f'esqueleto_{q}.json'), nos=nos, descricao=desc + _FIM)


ACESSORIOS = {q: _cfg(q) for q in _T}
