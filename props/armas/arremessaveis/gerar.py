"""Gera um arremessável: modelo, UVs e bake das texturas (<id>.blend e tex/ na pasta de saída).
uso: python3 gerar.py <id> [resolução] [saída]      (ids em config.CFGS)"""
import sys, os
from config import CFGS, AQUI
import fabrica

if __name__ == '__main__':
    fabrica.gerar(CFGS[sys.argv[1]], int(sys.argv[2]) if len(sys.argv) > 2 else 1024,
                  sys.argv[3] if len(sys.argv) > 3 else os.path.join(AQUI, 'saida', sys.argv[1]))
