"""Versão de jogo dos bastões detalhados, no lugar dos antigos bastao_pregos e bastao_arame.

Grava props/armas/armas/bastao_<qual>.glb com os mesmos pontos (mao_cima, barril, ponta) e as
mesmas animações do antigo, mais a versão leve e a entrada do catálogo.
O trabalho é de ../m4a1/fabrica.py; o que é dos bastões está em config.py.

uso: python3 gerar.py pregos 2048 saida_pregos && python3 jogo.py pregos saida_pregos
"""
import sys
from config import CFGS
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFGS[sys.argv[1]], sys.argv[2])
