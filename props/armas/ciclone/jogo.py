"""Versão de jogo da Ciclone detalhada, no lugar da smg_ciclone_9mm antiga e da areia.

Grava props/armas/armas/smg_ciclone_9mm[_tan].glb com os mesmos nós da antiga (gatilho, seletor,
ferrolho, alavanca, coronha, carregador, encaixes, boca_fogo, saida_estojo, mira_ferro) e as
mesmas animações, lidos de esqueleto.json, mais a versão leve de cada uma. O trabalho é de
../m4a1/fabrica.py; o que é da Ciclone está em config.py.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=tan python3 jogo.py saida_tan         (rodar o gerar.py com a mesma variável)
"""
import sys
from config import CFG
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFG, *sys.argv[1:3])
