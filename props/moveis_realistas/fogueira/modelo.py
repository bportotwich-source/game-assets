"""Fogueira de pedras: roda de pedras de rio tisnadas por dentro, cama de cinza, lenha em tenda no meio,
tocos já queimados caídos na cinza e a brasa (malha própria, que o jogo só mostra com o fogo aceso).
Medidas em mm, coordenadas do jogo (ver ../base.py)."""
import math, random
import bmesh
from mathutils import Vector, noise
import lib
from lib import MM, P, M, pintar
from base import G, cil, parte

FOGO_Y = 120
RAIO = 360


def pedra(x, y, z, sx, sy, sz, semente, mat='pedra'):
    """Pedra arredondada: esfera amassada por ruído, de base achatada. Meias medidas em mm."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3 if mat == "pedra" else 2, radius=1.0)
    rnd = random.Random(semente)
    desl = Vector((rnd.uniform(0, 50), rnd.uniform(0, 50), rnd.uniform(0, 50)))
    giro = rnd.uniform(0, math.pi)
    c, s = math.cos(giro), math.sin(giro)
    for v in bm.verts:
        n = noise.noise(v.co * 1.3 + desl) * 0.22 + noise.noise(v.co * 3.1 + desl) * 0.07
        p = v.co * (1.0 + n)
        px, py, pz = p.x * sx, max(p.z, -0.55) * sy, p.y * sz          # px, pz no chão; py para cima
        v.co = P(*G(x + px * c - pz * s, y + py, z + px * s + pz * c))
    o = lib._obj('pedra', bm, mat)
    return o


def tora(a, b, r, mat='casca_lenha', topo='crua_y', n=12):
    o = cil(a, b, r, mat, n=n, r1=r * 0.9)
    eixo = (Vector(P(*G(*b))) - Vector(P(*G(*a)))).normalized()
    ex = (eixo.y, eixo.z, eixo.x)                                      # nas coordenadas (u, v, w) do pintar
    pintar(o, topo, lambda c, nn: abs(nn[0] * ex[0] + nn[1] * ex[1] + nn[2] * ex[2]) > 0.9)
    return o


def _pedras():
    rnd = random.Random(5)
    p = []
    for i in range(11):
        a = i / 11 * 2 * math.pi + rnd.uniform(-0.08, 0.08)
        r = RAIO + rnd.uniform(-18, 18)
        e = rnd.uniform(0.8, 1.2)
        p.append(pedra(r * math.cos(a), 52 * e * 0.55, r * math.sin(a), 92 * e, 62 * e, 74 * e, 20 + i))
    for i in range(5):                                                # pedrinhas calçando
        a = rnd.uniform(0, 2 * math.pi)
        p.append(pedra((RAIO + 95) * math.cos(a), 12, (RAIO + 95) * math.sin(a), 32, 22, 26, 60 + i))
    return p


def _cinzas():
    return [lib.lathe([(0, 0), (0, 318), (10, 300), (22, 190), (30, 90), (32, 0)], 'cinza', n=32, c0=G(0, 0, 0), eixo=G(0, 1, 0)),
            lib.lathe([(26, 0), (26, 150), (36, 100), (40, 0)], 'tora_queimada', n=20, c0=G(0, 0, 0), eixo=G(0, 1, 0))]      # miolo de carvão


def _lenha():
    p = []
    for i in range(6):                                                # tenda
        a = i / 6 * 2 * math.pi + 0.3
        r = 30 + 5 * (i % 3)
        topo = (38 * math.cos(a + 2.6), 400 + 12 * (i % 2), 38 * math.sin(a + 2.6))
        p.append(tora((250 * math.cos(a), 26, 250 * math.sin(a)), topo, r))
    for i in range(3):                                                # tocos queimados na cinza
        a = i * 2.1 + 0.8
        p.append(tora((60 * math.cos(a), 50, 60 * math.sin(a)), (275 * math.cos(a + 0.35), 44, 275 * math.sin(a + 0.35)), 27, 'tora_queimada', 'tora_queimada', n=10))
    return p


def _brasa():
    rnd = random.Random(9)
    p = []
    for i in range(22):
        a, r = rnd.uniform(0, 2 * math.pi), 150 * math.sqrt(rnd.random())
        p.append(pedra(r * math.cos(a), 44 - r * 0.07, r * math.sin(a), rnd.uniform(12, 22), rnd.uniform(9, 14), rnd.uniform(12, 20), 100 + i, 'tora_queimada'))
    return p


def montar():
    parte('pedras', _pedras(), origem=G(0, 0, 0), grupo='A')
    parte('cinzas', _cinzas(), origem=G(0, 0, 0), grupo='A')
    parte('lenha', _lenha(), origem=G(0, 0, 0), grupo='B')
    parte('brasa', _brasa(), origem=G(0, 0, 0), grupo='B')
