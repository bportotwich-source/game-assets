"""Primitivas para móveis no método da M4A1 (Blender/bpy, texturas assadas).

Reaproveita props/armas/m4a1/lib.py e texturas.py. Aqui as medidas são em milímetros
nas coordenadas do jogo: x = largura (direita de quem olha o móvel de frente),
y = altura a partir do chão, z = profundidade (+z é a frente, de onde se abre).
O pivô do móvel é o centro da base, como em props/mobilias."""
import sys, os, math
AQUI = os.path.dirname(os.path.abspath(__file__))
M4 = os.path.join(os.path.dirname(AQUI), 'armas', 'm4a1')
sys.path[:0] = [p for p in (AQUI,) if p not in sys.path]
sys.path += [p for p in (M4, os.path.dirname(M4)) if p not in sys.path]     # no fim: o modelo.py do móvel vem antes do da M4A1
import bpy
import lib
from lib import MM, M, P, bevel, cut, join, parte, PARTES


def G(x, y, z):
    """Ponto do jogo (mm) -> coordenadas de projeto da lib (u para trás do móvel, v para cima, w para a direita)."""
    return (-z, y, x)


def caixa(x0, x1, y0, y1, z0, z1, mat, chanfro=0.0):
    o = lib.box(-z1, -z0, y0, y1, x0, x1, mat)
    return bevel(o, chanfro, seg=2) if chanfro else o


def cil(a, b, r, mat, n=20, r1=None):
    return lib.cyl(G(*a), G(*b), r, mat, n=n, r1=r1)


def planta(pts_xz, y0, y1, mat, chanfro=0.0):
    """Contorno visto de cima [(x, z)] levantado de y0 a y1."""
    o = lib.extr([(-z, x) for x, z in pts_xz], y0, y1, mat, plane='uw')
    return bevel(o, chanfro, seg=2) if chanfro else o


def perfil(pts_zy, x0, x1, mat, chanfro=0.0):
    """Perfil visto de lado [(z, y)] esticado de x0 a x1."""
    o = lib.extr([(-z, y) for z, y in pts_zy], x0, x1, mat, plane='uv')
    return bevel(o, chanfro, seg=2) if chanfro else o


def frente(pts_xy, z0, z1, mat, chanfro=0.0):
    """Contorno visto de frente [(x, y)] com espessura de z0 a z1."""
    o = lib.extr(pts_xy, -z1, -z0, mat, plane='wv')
    return bevel(o, chanfro, seg=2) if chanfro else o


def letreiro(s, tam, x, y, z, mat='tinta_branca', alinhar='CENTER'):
    """Texto pintado numa face virada para a frente (+z), centrado em x, linha de base em y."""
    cu = bpy.data.curves.new('t', 'FONT')
    cu.body = s
    cu.size = tam * MM
    cu.align_x = alinhar
    cu.resolution_u = 2
    tmp = bpy.data.objects.new('t', cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    for v in me.vertices:
        a, b = v.co.x / MM, v.co.y / MM
        v.co = P(*G(x + a, y + b, z))
    o = bpy.data.objects.new('t', me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.clear()
    me.materials.append(M(mat))
    return o
