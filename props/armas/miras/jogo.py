"""Versão de jogo de uma mira detalhada, no lugar da antiga.

Grava props/armas/acessorios/<id>.glb com os mesmos nós e animações da antiga (`olho` na reflexa,
`lamina` e a animação dobrar nas rebatíveis). Na reflexa a malha `<id>_lente` sai separada e de
vidro transparente, e o catálogo ganha o campo "optica" (o jogo acende o ponto nela).
O trabalho é de ../m4a1/fabrica.py; o que é das miras está em config.py.

uso: python3 gerar.py <id> 1024 saida && python3 jogo.py <id> saida
"""
import sys
from config import ACESSORIOS
import fabrica

if __name__ == '__main__':
    fabrica.acessorio(ACESSORIOS[sys.argv[1]], sys.argv[2])
