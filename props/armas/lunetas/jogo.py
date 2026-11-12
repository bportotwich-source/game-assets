"""Versão de jogo de uma luneta detalhada, no lugar da antiga.

Grava props/armas/acessorios/<id>.glb com o mesmo ponto `olho` da antiga, a malha `<id>_lente`
separada e, no catálogo, o campo "optica" (onde ficam as lentes e o aumento).
O trabalho é de ../m4a1/fabrica.py; o que é das lunetas está em config.py.

uso: python3 gerar.py <id> 1024 saida && python3 jogo.py <id> saida
"""
import sys
from config import ACESSORIOS
import fabrica

if __name__ == '__main__':
    fabrica.acessorio(ACESSORIOS[sys.argv[1]], sys.argv[2])
