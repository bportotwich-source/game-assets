"""O que a fábrica (../m4a1/fabrica.py) precisa saber da Guardiã."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(os.path.dirname(AQUI), 'm4a1')]


def montar():
    import materiais, modelo
    modelo.montar()


_FIM = ' Modelo detalhado, com texturas assadas (desgaste nas arestas, quadriculado nas talas, gravações).'
CFG = dict(
    nome='guardia', montar=montar, gerador='guardia/jogo.py', tris_leve=6000,
    origem=(4, -68, 0),              # ponto do punho na origem, como nas outras armas
    esqueleto=json.load(open(os.path.join(AQUI, 'esqueleto.json'), encoding='utf-8')),
    # peças de cada nó (None = direto na raiz)
    nos={None: ['armacao', 'pinos', 'alavanca_desmontagem', 'botao_desmontagem', 'retem_carregador'],
         'talas': ['tala_esquerda', 'tala_direita', 'parafusos_talas'],
         'gatilho': ['gatilho'], 'cao': ['cao'], 'cano': ['cano'],
         'ferrolho': ['ferrolho', 'alca_mira', 'massa_mira', 'extrator', 'percussor'],
         'trava': ['trava'], 'retem': ['retem'], 'carregador': ['carregador']},
    # VARIANTE='' é a areia; 'preta' é o mesmo modelo com outro bake (materiais.py)
    variantes={
        '': ('pistola_guardia_9mm',
             'Pistola de serviço de armação de alumínio cor de areia: ferrolho aberto em cima, cão externo, alavanca que desarma o cão, '
             'trilho para lanterna e cano com rosca. Mais pesada que a Sentinela, coice mais manso e 17 tiros.' + _FIM),
        'preta': ('pistola_guardia_9mm_preta',
                  'A mesma Guardiã toda preta (alumínio anodizado, ferrolho oxidado e talas pretas). Aceita os mesmos acessórios.' + _FIM),
    })
