"""Gera a lanterna: modelo, UVs e bake das texturas (<id>.blend e tex/ na pasta de saída).
uso: python3 gerar.py <id> [resolução] [saída]         (ids em config.py; 1024 basta)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo;
REASSAR=A força. Depois de mudar o modelo, apague a saída."""
import sys, os
from config import ACESSORIOS, AQUI
import fabrica

if __name__ == '__main__':
    q = sys.argv[1]
    fabrica.gerar(ACESSORIOS[q], int(sys.argv[2]) if len(sys.argv) > 2 else 1024, sys.argv[3] if len(sys.argv) > 3 else os.path.join(AQUI, 'saida_' + q))
