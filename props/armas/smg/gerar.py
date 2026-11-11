"""Gera a Faísca 9 mm: modelo, UVs e bake das texturas (faisca.blend e tex/ na pasta de saída).
uso: python3 gerar.py [resolução] [saída]          (VARIANTE=tan para a caramelo)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo
(o desdobramento é determinístico); REASSAR=A,B força os grupos listados."""
import sys, os
from config import CFG, AQUI
import fabrica

if __name__ == '__main__':
    fabrica.gerar(CFG, int(sys.argv[1]) if len(sys.argv) > 1 else 2048, sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, 'saida'))
