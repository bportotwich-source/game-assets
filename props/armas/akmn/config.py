"""AKMN 7,62 e peças táticas: modelos de terceiros com licença CC BY 4.0 (autor: suspensy).

Fontes (baixadas do Sketchfab pelo Bruno; os FBX e as texturas originais ficam fora do repositório):
  AKMN          https://sketchfab.com/3d-models/akmn-8a32337fe2eb4d528f82021d44e13bc8
  AKMN Zenitco  https://sketchfab.com/3d-models/akmn-zenitco-da587952abc9430fb2a2ae731c28daac
  Autor: suspensy (https://www.artstation.com/artwork/P463rB), licença https://creativecommons.org/licenses/by/4.0/
  O que mudou: peças separadas em partes móveis e acessórios, escala, orientação e origem do jogo,
  texturas reempacotadas (ORM, normal OpenGL), animações e encaixes do fuzil Brasa.

Este arquivo diz que malha do FBX vai para que peça, os ids, nomes e descrições.
"""
import os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [p for p in (AQUI, os.path.join(ARMAS, 'm4a1'), ARMAS) if p not in sys.path]

CREDITO = ('Modelo "AKMN" e "AKMN Zenitco" de suspensy (sketchfab.com/suspensy, artstation.com/artwork/P463rB), '
           'licença CC BY 4.0; adaptado para o Recomeço.')

# malhas do FBX (nome sem o sufixo .00N) -> peça. O que não está aqui é corpo da arma.
PECAS_AKMN = {
    'akmDc': 'tampa', 'akmMag': 'carregador', 'barrel.002': 'ferrolho', 'receiver.006': 'gatilho',
    'receiver.017': 'seletor', 'bGrip': 'punho', 'wStock': 'coronha', 'wHg': 'guarda_mao',
    'barrel.004': 'guarda_mao', 'barrel.006': 'guarda_mao', 'comp': 'freio',
}
# do FBX tático só saem os acessórios (o resto é igual ao AKMN)
PECAS_ZEN = {
    'pt1': 'coronha_tatica', 'lider': 'guarda_mao_longo', 'npn2': 'guarda_mao_longo', 'gripB': 'punho_tatico',
    'uspalm': 'carregador_polimero', 'b13': 'trilho_lateral', 'rl1': 'batente',
}

_FIM = ' ' + 'Modelo de suspensy (CC BY 4.0).'
ARMA = dict(nome='akmn', gerador='akmn/jogo.py', tris_leve=6000, id='fuzil_akmn',
            nos={None: ['corpo'], 'tampa': ['tampa'], 'gatilho': ['gatilho'], 'seletor': ['seletor'],
                 'ferrolho': ['ferrolho'], 'carregador': ['carregador']},
            descricao='Fuzil 7,62 de receptor estampado, a versão modernizada com trilho lateral para mira: coronha e guarda-mão '
                      'de madeira, punho de baquelite e freio de boca inclinado. Robusto e de coice forte. Aceita os acessórios do '
                      'Brasa 7,62 de cano, carregador, trilho lateral e trilhos, e as peças táticas próprias.' + _FIM)
TATICO = dict(id='fuzil_akmn_tatico',
              descricao='O mesmo AKMN montado com peças táticas: coronha rebatível de alumínio, guarda-mão longo com trilhos e '
                        'batente, punho ergonômico, carregador de polímero e trilho superior de montagem lateral para mira.' + _FIM)

# acessórios: peça -> (id, nome, encaixe, nó do encaixe na arma, categoria, peso, raridade, valor, modificadores, onde, descrição)
ACESSORIOS = {
    'coronha': dict(id='coronha_madeira_akmn', nome='Coronha de madeira (AKMN)', encaixe='coronha_ak', no='encaixe_coronha',
                    categoria='coronha', peso_kg=0.6, raridade='comum', valor_troca=14, modificadores={'recuo': 0.65, 'precisao': 1.3},
                    onde=['quartel', 'fabrica', 'armazem'],
                    descricao='Coronha fixa de madeira com soleira de aço e zarelho. Vem no AKMN.'),
    'guarda_mao': dict(id='guarda_mao_madeira_akmn', nome='Guarda-mão de madeira (AKMN)', encaixe='guarda_mao_ak', no='encaixe_guarda_mao',
                       categoria='guarda_mao', peso_kg=0.3, raridade='comum', valor_troca=8, modificadores={},
                       onde=['quartel', 'fabrica'],
                       descricao='Guarda-mão e capa do tubo de gás de madeira, com a trava e a vareta de limpeza. Vem no AKMN.'),
    'punho': dict(id='punho_akmn', nome='Punho de baquelite (AKMN)', encaixe='punho_ak', no='encaixe_punho',
                  categoria='punho', peso_kg=0.08, raridade='comum', valor_troca=5, modificadores={},
                  onde=['quartel', 'fabrica'], descricao='Punho de baquelite vermelho-escuro com quadriculado. Vem no AKMN.'),
    'freio': dict(id='freio_akmn', nome='Freio de boca inclinado (AKMN)', encaixe='boca_762', no='encaixe_boca',
                  categoria='boca', peso_kg=0.03, raridade='comum', valor_troca=6, modificadores={'recuo': 0.85},
                  onde=['quartel'], descricao='Bocal cortado em diagonal que segura a subida do cano. Vem no AKMN.'),
    'coronha_tatica': dict(id='coronha_rebativel_akmn', nome='Coronha rebatível de alumínio (AKMN)', encaixe='coronha_ak',
                           no='encaixe_coronha', categoria='coronha', peso_kg=0.55, raridade='raro', valor_troca=40,
                           modificadores={'recuo': 0.6, 'precisao': 1.35}, onde=['quartel'],
                           descricao='Coronha tática de alumínio com adaptador, apoio de rosto e soleira serrilhada.'),
    'guarda_mao_longo': dict(id='guarda_mao_longo_akmn', nome='Guarda-mão longo com trilhos (AKMN)', encaixe='guarda_mao_ak',
                             no='encaixe_guarda_mao', categoria='guarda_mao', peso_kg=0.45, raridade='raro', valor_troca=45,
                             modificadores={'precisao': 1.05}, onde=['quartel'],
                             descricao='Guarda-mão de alumínio que vai até a massa, com trilhos em cima e fendas dos lados e embaixo: '
                                       'libera empunhadura, lanterna e laser.'),
    'punho_tatico': dict(id='punho_tatico_akmn', nome='Punho ergonômico de polímero (AKMN)', encaixe='punho_ak', no='encaixe_punho',
                         categoria='punho', peso_kg=0.09, raridade='incomum', valor_troca=15, modificadores={'recuo': 0.97},
                         onde=['quartel', 'delegacia'], descricao='Punho de polímero com apoio para a palma e cavas para os dedos.'),
    'carregador_polimero': dict(id='carregador_762_30_polimero', nome='Carregador 7,62 de polímero (30)', encaixe='carregador_762',
                                no='encaixe_carregador', categoria='carregador', peso_kg=0.25, raridade='incomum', valor_troca=14,
                                modificadores={}, capacidade=30, municao='municao_762', onde=['quartel', 'delegacia'],
                                descricao='Carregador de polímero preto com grade em relevo, mais leve que o de aço.'),
    'trilho_lateral': dict(id='trilho_lateral_akmn', nome='Trilho superior de montagem lateral (AKMN)', encaixe='trilho_lateral_ak',
                           no='encaixe_mira', categoria='trilho', peso_kg=0.2, raridade='raro', valor_troca=30, modificadores={},
                           onde=['quartel'], descricao='Montagem que prende no trilho do lado esquerdo e põe um trilho por cima da '
                                                         'tampa para mira holográfica, de ponto ou luneta (encaixe_mira_trilho).'),
    'batente': dict(id='batente_akmn', nome='Batente de mão curto (AKMN)', encaixe='mlok_baixo', no='encaixe_empunhadura',
                    categoria='empunhadura', peso_kg=0.03, raridade='incomum', valor_troca=10,
                    modificadores={'recuo': 0.93, 'tempo_mirar': 0.92}, onde=['quartel'],
                    descricao='Batente inclinado embaixo do guarda-mão: a mão encosta e não escorrega.'),
}
PADRAO = {'encaixe_coronha': 'coronha_madeira_akmn', 'encaixe_guarda_mao': 'guarda_mao_madeira_akmn', 'encaixe_punho': 'punho_akmn',
          'encaixe_boca': 'freio_akmn'}
PADRAO_TATICO = {'encaixe_coronha': 'coronha_rebativel_akmn', 'encaixe_guarda_mao': 'guarda_mao_longo_akmn',
                 'encaixe_punho': 'punho_tatico_akmn', 'encaixe_boca': 'freio_akmn', 'encaixe_mira': 'trilho_lateral_akmn',
                 'encaixe_empunhadura': 'batente_akmn', 'encaixe_carregador': 'carregador_762_30_polimero'}


def ler(nome):
    return json.load(open(os.path.join(AQUI, nome), encoding='utf-8'))
