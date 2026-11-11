"""Versão de jogo da Mutirão 12 detalhada, no lugar da espingarda_12 antiga e da curta.

Grava props/armas/armas/espingarda_12[_curta].glb com os mesmos nós da antiga (gatilho, telha,
ferrolho, elevador, tampa_tubo, encaixes, boca_fogo, saida_estojo, mira_ferro) e as mesmas
animações, lidos de esqueleto.json (esqueleto_curta.json na curta), mais a versão leve de cada
uma. O trabalho é de ../m4a1/fabrica.py; o que é da Mutirão está em config.py.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=curta python3 jogo.py saida_curta     (rodar o gerar.py com a mesma variável)
     python3 jogo.py saida_coronha coronha          (acessórios/coronha_retratil_12.glb)
"""
import sys
from config import CFG, CFG_CORONHA
import fabrica

if __name__ == '__main__':
    if sys.argv[2:3] == ['coronha']:
        fabrica.acessorio(CFG_CORONHA, sys.argv[1])
    else:
        fabrica.jogo(CFG, *sys.argv[1:3])
