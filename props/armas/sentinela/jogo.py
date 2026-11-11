"""Versão de jogo da Sentinela detalhada, no lugar da pistola_9mm antiga e das três cores.

Grava props/armas/armas/pistola_9mm[_tan|_verde|_cinza].glb com os mesmos nós da antiga
(gatilho, cano, ferrolho, carregador, encaixes, boca_fogo, saida_estojo, mira_ferro) e as
mesmas animações, lidos de esqueleto.json, mais a versão leve de cada uma. O trabalho é de
../m4a1/fabrica.py; o que é da Sentinela está em config.py.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=tan python3 jogo.py saida_tan         (rodar o gerar.py com a mesma variável)
"""
import sys
from config import CFG
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFG, *sys.argv[1:3])
