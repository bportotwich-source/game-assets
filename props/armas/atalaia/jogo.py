"""Versão de jogo do Atalaia .308 feito com as peças da M4A1, no lugar do fuzil_308_precisao antigo e do curto.

Grava props/armas/armas/fuzil_308_precisao[_curto].glb com os nós do antigo (punho, gatilho, seletor,
ferrolho, alavanca, tampa_janela, retem_ferrolho, carregador, encaixes, boca_fogo, saida_estojo,
mira_ferro) e as mesmas animações, lidos de esqueleto[_curto].json, mais a versão leve de cada um.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=curto python3 jogo.py saida_curto
"""
import sys
from config import CFG
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFG, *sys.argv[1:3])
