"""Gera o fuzil Vigília 5,56: modelo, UVs e bake das texturas (vigilia.blend e tex/ na pasta de saída).
uso: python3 gerar.py [resolução] [saída]          (VARIANTE=bicolor para o preto e caramelo)
     python3 gerar.py 1024 saida_coronha coronha   (a coronha retrátil dos fuzis; VARIANTE=tan para a caramelo)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo
(o desdobramento é determinístico); REASSAR=A,B força os grupos listados."""
import sys, os
from config import CFG, CFG_CORONHA, AQUI
import fabrica

if __name__ == '__main__':
    cfg = CFG_CORONHA if sys.argv[3:4] == ['coronha'] else CFG
    fabrica.gerar(cfg, int(sys.argv[1]) if len(sys.argv) > 1 else 2048, sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, 'saida'))
