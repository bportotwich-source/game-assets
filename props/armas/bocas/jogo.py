"""Versão de jogo de uma boca de cano detalhada, no lugar da antiga (props/armas/acessorios/<id>.glb).
O trabalho é de ../m4a1/fabrica.py; o que é das bocas está em config.py.

uso: python3 gerar.py <id> 512 saida && python3 jogo.py <id> saida
"""
import sys
from config import ACESSORIOS
import fabrica

if __name__ == '__main__':
    fabrica.acessorio(ACESSORIOS[sys.argv[1]], sys.argv[2])
