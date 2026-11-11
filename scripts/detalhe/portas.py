"""Troca folhas de porta lisas (uma caixa) por folhas com almofadas em relevo, direto no GLB.

    python3 scripts/detalhe/portas.py kits/diner/pieces/door_leaf_front.glb [...]

Mantém a largura, a altura, o pivô (dobradiça em x = 0, embaixo), os nomes dos nós e os materiais que a
folha já tinha. Folha com material `glass` ganha vidro com baguetes no alto; sem vidro, três almofadas
(cinco se o material for `frame`, de porta interna). Rodar de novo não muda nada: folha com mais de
200 triângulos é pulada.
"""
import os, sys
import numpy as np, trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detalhe as D

PRINCIPAIS = ('door', 'door_service', 'frame', 'door_int')


def refazer(arq):
    velha = trimesh.load(arq)
    if sum(len(g.faces) for g in velha.geometry.values()) > 200:
        print('pulada (já tem relevo):', arq); return False
    nome = os.path.splitext(os.path.basename(arq))[0]
    mats = {g.visual.material.name: g.visual.material for g in velha.geometry.values()}
    mat = next((m for m in PRINCIPAIS if m in mats), None)
    if mat is None:
        print('pulada (sem material de porta):', arq, list(mats)); return False
    ferragem = 'brass' if 'brass' in mats else 'metal' if 'metal' in mats else mat
    vidro = 'glass' in mats
    (x0, y0, _), (x1, y1, _) = velha.bounds
    w, h, t = float(x1 - x0), float(y1 - y0), 0.05
    p = D.Piece(); slab = D.tbox(0, w, 0, h, -t / 2, t / 2); cut = []
    m = 0.12 * (w / 0.94); y_top = h - 0.13
    if vidro:
        gy0 = h * 0.62; cut.append(D.tbox(m, w - m, gy0, y_top, -t, t))
        paineis = [(0.18, gy0 - 0.14)]
    else:
        n = 5 if mat in ('frame', 'door_int') else 3
        passo = (h - 0.32) / n
        paineis = [(0.16 + i * passo + 0.02, 0.16 + (i + 1) * passo - 0.02) for i in range(n)]
    for (a, b) in paineis:
        for z in (t / 2, -t / 2): cut.append(D.tbox(m, w - m, a, b, z - 0.01, z + 0.01))
    p.add(mat, D.bl_detail(slab, cut, bevel=0.004, segments=2 if vidro else 1))
    if vidro:
        p.box('glass', m - 0.004, w - m + 0.004, gy0 - 0.004, y_top + 0.004, -0.004, 0.004)
        p.cham(mat, w / 2 - 0.013, w / 2 + 0.013, gy0, y_top, -0.013, 0.013, 0.004)
        p.cham(mat, m, w - m, (gy0 + y_top) / 2 - 0.013, (gy0 + y_top) / 2 + 0.013, -0.013, 0.013, 0.004)
    for z in (1, -1):   # espelho, maçaneta e haste
        p.cham(ferragem, w - 0.12, w - 0.07, 0.9, 1.1, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
        p.sphere(ferragem, 0.028, w - 0.095, 1.0, z * (t / 2 + 0.05))
        p.seg(ferragem, (w - 0.095, 1.0, z * t / 2), (w - 0.095, 1.0, z * (t / 2 + 0.04)), 0.015)
    for yy in (0.25, h - 0.35): p.cyl(ferragem, 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)   # dobradiças
    cena = trimesh.Scene()
    for k, ms in p.parts.items():
        ms = [x for x in ms if x is not None and len(x.faces)]
        if not ms: continue
        g = trimesh.util.concatenate([trimesh.Trimesh(x.vertices, x.faces, process=False) for x in ms])
        g.visual = trimesh.visual.TextureVisuals(material=mats[k])
        cena.add_geometry(g, node_name=f'{nome}_{k}', geom_name=f'{nome}_{k}')
    cena.export(arq)
    nova = trimesh.load(arq)
    print(f'{arq}: {sum(len(g.faces) for g in nova.geometry.values())} triângulos, caixa {nova.bounds.round(3).tolist()}')
    return True


if __name__ == '__main__':
    for a in sys.argv[1:]: refazer(a)
