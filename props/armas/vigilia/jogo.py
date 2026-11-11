"""Versão de jogo do Vigília 5,56 feito com as peças da M4A1, no lugar do fuzil_556 antigo e do bicolor.

Grava props/armas/armas/fuzil_556[_bicolor].glb com os nós do antigo (punho, gatilho, seletor,
ferrolho, alavanca, tampa_janela, retem_ferrolho, carregador, encaixes, boca_fogo, saida_estojo,
mira_ferro) e as mesmas animações, lidos de esqueleto.json, mais a versão leve de cada um.
Os nós das peças que giram e alguns encaixes foram levados para o lugar das peças novas
(trilho 6,5 mm mais alto, boca e coronha nos pontos da M4A1).

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=bicolor python3 jogo.py saida_bicolor
     python3 jogo.py saida_coronha coronha          (acessorios/coronha_retratil_ar.glb; VARIANTE=tan para a caramelo)
"""
import sys
from config import CFG, CFG_CORONHA
import fabrica

if __name__ == '__main__':
    if sys.argv[2:3] == ['coronha']:
        fabrica.acessorio(CFG_CORONHA, sys.argv[1])
    else:
        fabrica.jogo(CFG, *sys.argv[1:3])
