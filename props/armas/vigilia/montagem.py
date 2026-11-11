"""Fuzil Vigília 5,56 no nível de detalhe da M4A1, montado com as peças da própria M4A1
(../m4a1/modelo.py e ../m4a1/acessorios.py): receptores, ferrolho, alavanca, controles, punho,
cano, guarda-mão longo vazado com trilho contínuo e carregador de polímero. Sem alça de
transporte, sem massa fixa e sem coronha: miras rebatíveis, boca e coronha são acessórios nos
encaixes, como no Vigília antigo (arma05_fuzil.py).

VARIANTE=bicolor pinta de caramelo o guarda-mão, o punho e o carregador.

As peças nascem nas coordenadas da M4A1 e são levadas 145 mm para a frente: assim o punho, o
gatilho, o poço do carregador e o eixo do cano caem nos mesmos pontos do Vigília antigo.
`coronha()` monta a coronha retrátil da M4A1 como acessório (coronha_retratil_ar).
"""
import sys, os
import bpy
from lib import *
import modelo as m4          # ../m4a1/modelo.py (este arquivo não se chama modelo.py para não o esconder)
import acessorios as m4ac

DU = 145.0
VARIANTE = os.environ.get('VARIANTE', '')
GRUPO = {'receptor_superior': 'A', 'impulsor_ferrolho': 'A', 'tampa_janela': 'A', 'ferrolho': 'A', 'alavanca_manejo': 'A',
         'trava_alavanca': 'A', 'receptor_inferior': 'A', 'gatilho': 'A', 'guarda_mato': 'A', 'seletor': 'A', 'retem_ferrolho': 'A',
         'retem_carregador': 'A', 'pino_pivo': 'A', 'pino_desmontagem': 'A', 'pino_gatilho': 'A', 'pino_cao': 'A',
         'pino_armadilha': 'A', 'punho': 'A', 'cano': 'B', 'guarda_mao_longo': 'B', 'porca_cano': 'B', 'bloco_gas': 'B',
         'carregador_polimero': 'B'}
CARAMELO = {'guarda_mao_longo': {'anod': 'areia_anod'}, 'punho': {'polim': 'tan', 'polim_grip': 'tan_grip'},
            'carregador_polimero': {'polim': 'tan'}, 'coronha': {'polim': 'tan'}, 'trava_coronha': {'polim': 'tan'}}


def _filho(o, pai):
    o.parent = pai
    bpy.context.view_layer.update()
    o.matrix_parent_inverse = pai.matrix_world.inverted()


def _tirar(nomes):
    for o in [o for o in PARTES if o.name in nomes]:
        PARTES.remove(o)
        bpy.data.objects.remove(o)


def _trocar(o, mapa):
    for i, m in enumerate(o.data.materials):
        if m and m.name in mapa:
            o.data.materials[i] = M(mapa[m.name])


def _fechar(grupos, du):
    for o in PARTES:
        if o.parent is None:
            o.location += P(du, 0, 0)
        o['grupo'] = grupos if isinstance(grupos, str) else grupos[o.name]
        if VARIANTE in ('bicolor', 'tan') and o.name in CARAMELO:
            _trocar(o, CARAMELO[o.name])
    bpy.context.view_layer.update()


def _gravacao(s, *a, **k):
    """As gravações do receptor da M4A1, com o nome deste fuzil."""
    return texto({'FUZIL M4A1': 'FUZIL VIGÍLIA', 'RC 104517': 'RC 556208'}.get(s, s), *a, **k)


def montar():
    m4.texto = _gravacao
    sup = m4.receptor_superior()
    for f in (m4.impulsor, m4.tampa_janela, m4.ferrolho, m4.alavanca_manejo):
        _filho(f(), sup)
    inf = m4.receptor_inferior()
    m4.controles(inf)
    m4.punho(inf)
    m4.cano()
    m4ac.guarda_mao_longo()
    m4ac.carregador_polimero()
    _tirar(('trilho_baixo', 'trilho_esquerdo'))
    _fechar(GRUPO, DU)


def coronha():
    """Coronha retrátil (tubo, placa, porca e corpo que corre) com o começo do tubo no encaixe."""
    m4.coronha()
    _fechar('C', 197.0)
