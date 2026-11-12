"""Gera um bastão: modelo, UVs e bake das texturas (bastao_<qual>.blend e tex/ na pasta de saída).
uso: python3 gerar.py pregos|arame [resolução] [saída]"""
import sys, os
from config import CFGS, AQUI
import fabrica

if __name__ == '__main__':
    qual = sys.argv[1]
    fabrica.gerar(CFGS[qual], int(sys.argv[2]) if len(sys.argv) > 2 else 2048, sys.argv[3] if len(sys.argv) > 3 else os.path.join(AQUI, 'saida_' + qual))
