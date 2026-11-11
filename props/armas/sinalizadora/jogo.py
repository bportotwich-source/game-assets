"""Versão de jogo da pistola sinalizadora detalhada, no lugar da pistola_sinalizadora antiga.

Grava props/armas/armas/pistola_sinalizadora.glb com os mesmos nós do antigo (cano, cartucho, cão,
gatilho, trava) e as mesmas animações, mais a versão leve e a entrada do catálogo.
O trabalho é de ../m4a1/fabrica.py; o que é da sinalizadora está em config.py.

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
