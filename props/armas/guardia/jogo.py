"""Versão de jogo da Guardiã detalhada, no lugar da pistola_guardia_9mm antiga.

Parte do guardia.blend que o gerar.py salva e grava props/armas/armas/pistola_guardia_9mm.glb
com os mesmos nós da antiga (talas, gatilho, cao, cano, ferrolho, trava, retem, carregador,
encaixes, boca_fogo, saida_estojo, mira_ferro) e as mesmas animações, lidos de esqueleto.json:
o jogo, os acessórios e as animações continuam valendo sem mudar nada. Os pontos ref_* são
medidos de novo (pontos_ref.py). Grava também a versão leve (uma malha só, 1 conjunto de
textura 1024) em armas/pistola_guardia_9mm_leve.glb, para a arma vista de longe ou no chão.
No catalogo.json a arma fica com "gerador": "guardia/jogo.py" (o gerar_armas.py não a refaz).
O trabalho é de ../m4a1/fabrica.py; o que é da Guardiã está em config.py.

uso: python3 jogo.py saida [webp|jpg]      (saida = pasta do gerar.py, com guardia.blend e tex/)
     VARIANTE=preta python3 jogo.py saida_preta      (a Guardiã preta: rodar o gerar.py com a mesma variável)
"""
import sys
from config import CFG
import fabrica

if __name__ == '__main__':
    fabrica.jogo(CFG, *sys.argv[1:3])
