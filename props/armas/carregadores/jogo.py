"""Versão de jogo de um carregador avulso, no lugar da antiga (props/armas/acessorios/<id>.glb), com os
nós e as animações da antiga (esqueleto_<id>.json) e o registro no catálogo. O trabalho é de
../m4a1/fabrica.py; o que é das carregadores está em config.py.

uso: python3 gerar.py <id> 1024 saida && python3 jogo.py <id> saida
"""
import sys
from config import ACESSORIOS
import fabrica

if __name__ == '__main__':
    fabrica.acessorio(ACESSORIOS[sys.argv[1]], sys.argv[2])
