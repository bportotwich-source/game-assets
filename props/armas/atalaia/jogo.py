"""Versão de jogo do Atalaia .308 feito com as peças da M4A1, no lugar do fuzil_308_precisao antigo e do curto.

Grava props/armas/armas/fuzil_308_precisao[_curto].glb com os nós do antigo (punho, gatilho, seletor,
ferrolho, alavanca, tampa_janela, retem_ferrolho, carregador, encaixes, boca_fogo, saida_estojo,
mira_ferro) e as mesmas animações, lidos de esqueleto[_curto].json, mais a versão leve de cada um.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=curto python3 jogo.py saida_curto
     python3 jogo.py saida_coronha coronha          (acessorios/coronha_precisao_ar.glb; VARIANTE=preta para a preta)
"""
import sys
from config import CFG, CFG_CORONHA
import fabrica

if __name__ == '__main__':
    if sys.argv[2:3] == ['coronha']:
        fabrica.acessorio(CFG_CORONHA, sys.argv[1])
    else:
        fabrica.jogo(CFG, *sys.argv[1:3])
