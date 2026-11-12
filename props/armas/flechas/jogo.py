"""Versão de jogo de uma flecha ou virote solto, no lugar do antigo (props/armas/municao/<id>.glb).
O trabalho é de ../m4a1/fabrica.py; o que é das flechas está em config.py.

uso: python3 gerar.py <id> 512 saida && python3 jogo.py <id> saida
"""
import sys
from config import ACESSORIOS
import fabrica

if __name__ == '__main__':
    fabrica.acessorio(ACESSORIOS[sys.argv[1]], sys.argv[2])
