"""Versão de jogo do revólver Vigia detalhado, no lugar do revolver_38 antigo: mesmos nós
(punho, cao, gatilho, trava, braco, tambor, extrator, encaixes) e mesmas animações, lidos de
esqueleto.json, mais a versão leve. O trabalho é de ../m4a1/fabrica.py; o que é do revólver
está em config.py.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
"""
import sys
from config import CFG
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFG, *sys.argv[1:3])
