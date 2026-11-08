"""Ferramentas de forma para carrocerias: secoes lofadas, cascas, booleanos e regioes de painel.

Tudo em trimesh com o motor 'manifold' (booleanos exatos e rapidos). Convencao dos veiculos: Y para cima, frente para +Z,
lado esquerdo do carro (motorista) em +X, 1 unidade = 1 m.
"""
import math
import numpy as np, trimesh
from shapely.geometry import Polygon, MultiPolygon, box as sbox
from shapely.ops import unary_union

TF = trimesh.transformations


def chaikin(pts, it=3, fechado=True, fixos=()):
    """Suaviza um poligono (corte de cantos). fixos = indices que ficam como cantos vivos (repetidos)."""
    p = [np.array(q, float) for q in pts]
    for _ in range(it):
        n = len(p); out = []
        rng = range(n) if fechado else range(n - 1)
        for i in rng:
            a, b = p[i], p[(i + 1) % n]
            out += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        if not fechado: out = [p[0]] + out + [p[-1]]
        p = out
    return np.array(p)


def anel_xy(meio, z):
    """Meio perfil (x >= 0) de baixo (x=0) para cima (x=0) -> anel fechado em z, sentido fixo."""
    meio = np.asarray(meio, float)
    esq = meio[-2:0:-1].copy(); esq[:, 0] *= -1
    r = np.vstack([meio, esq])
    return np.column_stack([r[:, 0], r[:, 1], np.full(len(r), z)])


def loft(aneis):
    """Malha fechada ligando aneis (mesmo numero de pontos) em sequencia, com tampas nas pontas."""
    A = np.asarray(aneis, float); S, N, _ = A.shape
    v = A.reshape(-1, 3); f = []
    for s in range(S - 1):
        a0, b0 = s * N, (s + 1) * N
        for i in range(N):
            j = (i + 1) % N
            f += [[a0 + i, a0 + j, b0 + j], [a0 + i, b0 + j, b0 + i]]
    c0 = len(v); c1 = c0 + 1
    v = np.vstack([v, A[0].mean(0), A[-1].mean(0)])
    for i in range(N):
        j = (i + 1) % N
        f += [[c0, j, i]]
        f += [[c1, (S - 1) * N + i, (S - 1) * N + j]]
    m = trimesh.Trimesh(v, np.array(f), process=True)
    if m.volume < 0: m.invert()
    return m


def menos(a, *bs):
    bs = [b for b in bs if b is not None and len(b.faces)]
    if not bs: return a
    return trimesh.boolean.difference([a] + bs, engine='manifold')


def uniao(ms):
    ms = [m for m in ms if m is not None and len(m.faces)]
    return ms[0] if len(ms) == 1 else trimesh.boolean.union(ms, engine='manifold')


def inter(a, b):
    r = trimesh.boolean.intersection([a, b], engine='manifold')
    return r


def prisma_zy(poly, x0, x1):
    """Poligono no plano (z, y) extrudado em x de x0 a x1."""
    if poly.is_empty: return None
    polys = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
    ms = []
    for pg in polys:
        m = trimesh.creation.extrude_polygon(pg, x1 - x0)       # (z, y, x)
        v = m.vertices; m.vertices = np.column_stack([v[:, 2] + x0, v[:, 1], v[:, 0]])
        if m.volume < 0: m.invert()
        ms.append(m)
    return trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]


def prisma_xz(poly, y0, y1):
    """Poligono no plano (x, z) extrudado em y de y0 a y1."""
    if poly.is_empty: return None
    polys = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
    ms = []
    for pg in polys:
        m = trimesh.creation.extrude_polygon(pg, y1 - y0)       # (x, z, y)
        v = m.vertices; m.vertices = np.column_stack([v[:, 0], v[:, 2] + y0, v[:, 1]])
        if m.volume < 0: m.invert()
        ms.append(m)
    return trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]


def prisma_xy(poly, z0, z1):
    """Poligono no plano (x, y) extrudado em z."""
    if poly.is_empty: return None
    m = trimesh.creation.extrude_polygon(poly, z1 - z0); m.apply_translation([0, 0, z0])
    if m.volume < 0: m.invert()
    return m


def caixa(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0]); b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return b


def cil_x(r, x0, x1, y, z, sec=48):
    c = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=sec)
    c.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); c.apply_translation([(x0 + x1) / 2, y, z]); return c


def espelhar_x(m):
    mm = m.copy(); mm.apply_transform(np.diag([-1, 1, 1, 1])); mm.invert() if mm.volume < 0 else None
    if mm.volume < 0: mm.invert()
    return mm


def varrer_caminho(perfil, caminho, normal_ref=(0, 1, 0), fechar=True):
    """Perfil (lista de (u, v)) varrido ao longo de um caminho 3D. u = lateral (perpendicular ao caminho e a normal_ref),
    v = ao longo de normal_ref. Tampas nas pontas."""
    P = np.asarray(caminho, float); n = len(P); up = np.asarray(normal_ref, float)
    aneis = []
    for i in range(n):
        t = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]; t /= np.linalg.norm(t)
        lado = np.cross(up, t); lado /= np.linalg.norm(lado); cima = np.cross(t, lado)
        aneis.append([P[i] + lado * u + cima * v for (u, v) in perfil])
    return loft(aneis)


def tubo(caminho, r, sec=12, normal_ref=(0, 1, 0)):
    perfil = [(r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, sec, endpoint=False)]
    P = np.asarray(caminho, float)
    t = P[-1] - P[0]; t /= np.linalg.norm(t)
    ref = np.asarray(normal_ref, float)
    if abs(np.dot(ref, t)) > 0.9: ref = np.array([1.0, 0, 0]) if abs(t[0]) < 0.9 else np.array([0, 0, 1.0])
    return varrer_caminho(perfil, P, ref)


def suavizar_caminho(pts, it=3):
    return chaikin(pts, it, fechado=False)
