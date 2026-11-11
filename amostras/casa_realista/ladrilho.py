"""Materiais realistas que se repetem a cada 2 m, para as peças atuais dos kits (UV em metros / 2).
Assa um painel de 2,25 m e funde a sobra de 0,25 m com o começo, para a emenda sumir.
uso: python3 ladrilho.py [saída] [px por metro]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
import texturas
from lib import *

SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saida', 'ladrilho')
PPM = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
SO = [g for g in os.environ.get('SO', '').split(',') if g]
PLANOS = {'shingles': 'telha_l', 'cap': 'pedra_l', 'tinta': 'tinta_l', 'render': 'reboco_ext_l', 'rooftile': 'telha_barro_l',
          'ashlar': 'cantaria_l', 'block': 'bloco_l', 'concrete': 'concreto_l'}
T, S = 2.0, 0.25                    # ladrilho e sobra
D = T + S


def uv_plano(o, f):
    """UV = f(ponto de projeto) nas faces viradas para a frente; o resto colapsa num canto."""
    me = o.data
    uv = me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li in p.loop_indices:
            c = me.vertices[me.loops[li].vertex_index].co
            q = f((c.x, c.z, -c.y), (p.normal.x, p.normal.z, -p.normal.y))
            uv.data[li].uv = q if q else (0.0, 0.0)


def painel(nome):
    if nome in ('siding', 'siding_w'):        # tábuas em cunha como as do kit: fiadas de 0,2 m a partir de 0,12 m
        L = []
        for k in range(-1, 12):
            yb = 0.12 + k * 0.2; yt = yb + 0.23
            L.append(veio(extr([(0.0, yb), (0.024, yb), (0.0245, yb + 0.004), (0.008, yt), (0.0, yt)], -0.2, D + 0.2, 'tabua_l' if nome == 'siding' else 'tabua_branca_l', 'zy'), 'x'))
        o = join(L, nome)
        uv_plano(o, lambda c, n: (c[0] / D, c[1] / D) if n[2] > 0.5 else None)
    elif nome == 'brick':
        o = box(-0.2, D + 0.2, -0.2, D + 0.2, -0.1, 0.0, 'tijolo_l')
        uv_plano(o, lambda c, n: (c[0] / D, c[1] / D) if n[2] > 0.5 else None)
    elif nome == 'plaster':
        o = box(-0.2, D + 0.2, -0.2, D + 0.2, -0.1, 0.0, 'reboco_l')
        uv_plano(o, lambda c, n: (c[0] / D, c[1] / D) if n[2] > 0.5 else None)
    elif nome in PLANOS:
        o = box(-0.2, D + 0.2, -0.2, D + 0.2, -0.1, 0.0, PLANOS[nome])
        uv_plano(o, lambda c, n: (c[0] / D, c[1] / D) if n[2] > 0.5 else None)
    else:                       # floor e deck: plano horizontal, tábuas ao longo de U como nas texturas do kit
        o = box(-0.2, D + 0.2, -0.1, 0.0, -D - 0.2, 0.2, 'assoalho_l' if nome == 'floor' else 'deck_l')
        uv_plano(o, lambda c, n: (-c[2] / D, c[0] / D) if n[1] > 0.5 else None)
    for p in o.data.polygons:
        p.use_smooth = False
    return o


def fundir(a):
    """a: (N, N, c) cobrindo D metros, linha 0 = topo. Devolve o ladrilho de T metros."""
    n = a.shape[0]; t = int(round(n * T / D)); s = n - t
    w = (np.arange(s) / s).reshape(1, s, 1)
    x = a[:, :t].copy()
    x[:, :s] = w * a[:, :s] + (1 - w) * a[:, t:t + s]
    y = x[::-1]                                  # linha 0 = base (v = 0)
    out = y[:t].copy()
    wv = w.reshape(s, 1, 1)
    out[:s] = wv * y[:s] + (1 - wv) * y[t:t + s]
    return out[::-1]


def main():
    for nome in ('siding', 'brick', 'plaster', 'floor', 'deck', 'shingles', 'cap', 'tinta', 'siding_w', 'render', 'rooftile', 'ashlar', 'block', 'concrete'):
        if SO and nome not in SO:
            continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        import lib; lib._MATS.clear()
        o = painel(nome)
        texturas.preparar_materiais()
        passes = texturas.assar([o], int(round(D * PPM)))
        passes = {k: fundir(v) for k, v in passes.items()}
        nn = passes['normal'] * 2 - 1
        passes['normal'] = nn / np.maximum(np.linalg.norm(nn, axis=2, keepdims=True), 1e-6) * 0.5 + 0.5
        texturas.salvar(passes, os.path.join(SAIDA, nome))
        print(nome, 'pronto', flush=True)


if __name__ == '__main__':
    main()
