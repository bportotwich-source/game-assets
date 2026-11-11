"""Versão de jogo do Brasa 7,62 detalhado, no lugar do fuzil_762 antigo.

Grava props/armas/armas/fuzil_762.glb com os mesmos nós do antigo (tampa, gatilho, seletor,
ferrolho, carregador, encaixes, boca_fogo, saida_estojo, mira_ferro) e as mesmas animações, lidos
de esqueleto.json, mais a versão leve. Os acessórios que vêm montados (coronha_madeira_ak,
guarda_mao_madeira_ak, freio_ak) saem em props/armas/acessorios/. O trabalho é de
../m4a1/fabrica.py; o que é do Brasa está em config.py.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     python3 jogo.py saida_coronha coronha          (acessórios: coronha, guarda_mao ou freio)
Gere os acessórios antes do fuzil (o ref_coronha do fuzil sai da coronha).
"""
import sys
from config import CFG, ACESSORIOS
import fabrica

if __name__ == '__main__':
    if sys.argv[2:3] and sys.argv[2] in ACESSORIOS:
        fabrica.acessorio(ACESSORIOS[sys.argv[2]], sys.argv[1])
    else:
        fabrica.jogo(CFG, *sys.argv[1:3])
