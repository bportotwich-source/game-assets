"""Versão de jogo do arco composto detalhado, no lugar do arco_composto antigo.

Grava props/armas/armas/arco_composto.glb com os mesmos nós do antigo (braços, metades da
corda, polias, cabos, laço D, visor, apoio, flecha e encaixes) e as mesmas animações, mais
a versão leve e a entrada do catálogo.
O trabalho é de ../m4a1/fabrica.py; o que é do arco está em config.py.

uso: python3 gerar.py 2048 saida && python3 jogo.py saida
"""
import sys
from config import CFG, ACESSORIOS
import fabrica

if __name__ == '__main__':
    if sys.argv[2:3] and sys.argv[2] in ACESSORIOS:
        fabrica.acessorio(ACESSORIOS[sys.argv[2]], sys.argv[1])
    else:
        fabrica.jogo(CFG, *sys.argv[1:3])
