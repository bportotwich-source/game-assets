"""Versão de jogo de um arremessável detalhado, no lugar do antigo.

Grava props/armas/armas/<id>.glb com os mesmos nós e as mesmas animações do antigo, mais a versão
leve e a entrada do catálogo. O trabalho é de ../m4a1/fabrica.py; o que é de cada um está em config.py.

uso: python3 gerar.py <id> 1024 saida/<id> && python3 jogo.py <id> saida/<id>
"""
import sys
from config import CFGS
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFGS[sys.argv[1]], sys.argv[2])
