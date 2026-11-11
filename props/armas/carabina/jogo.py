"""Versão de jogo da carabina Paciência detalhada, no lugar da carabina_308 antiga e da de caça.

Grava props/armas/armas/carabina_308[_caca].glb com os mesmos nós da antiga (apoio_face, gatilho,
ferrolho, carregador, encaixes, boca_fogo, saida_estojo) e as mesmas animações, lidos de
esqueleto.json (esqueleto_caca.json na de caça), mais a versão leve de cada uma. O trabalho é de
../m4a1/fabrica.py; o que é da carabina está em config.py.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=caca python3 jogo.py saida_caca       (rodar o gerar.py com a mesma variável)
"""
import sys
from config import CFG
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFG, *sys.argv[1:3])
