"""Versão de jogo do rifle Pardal .22 detalhado, no lugar do rifle_22 antigo e do sintético.

Grava props/armas/armas/rifle_22[_sintetico].glb com os mesmos nós do antigo (gatilho, ferrolho,
carregador, encaixes, boca_fogo, saida_estojo, mira_ferro) e as mesmas animações, lidos de
esqueleto.json (esqueleto_sintetico.json no sintético), mais a versão leve de cada um. Os
acessórios que vêm montados (alca_cano_22, protetor_rosca_22) saem em props/armas/acessorios/.
O trabalho é de ../m4a1/fabrica.py; o que é do Pardal está em config.py.

uso: python3 jogo.py saida [webp|jpg]               (saida = pasta do gerar.py)
     VARIANTE=sintetico python3 jogo.py saida_sint  (rodar o gerar.py com a mesma variável)
     python3 jogo.py saida_alca alca                (acessórios: alca ou protetor)
"""
import sys
from config import CFG, ACESSORIOS
import fabrica

if __name__ == '__main__':
    if sys.argv[2:3] and sys.argv[2] in ACESSORIOS:
        fabrica.acessorio(ACESSORIOS[sys.argv[2]], sys.argv[1])
    else:
        fabrica.jogo(CFG, *sys.argv[1:3])
