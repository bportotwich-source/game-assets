"""Móveis de sala no nível realista: cadeira de madeira, mesa de jantar e estante de livros.

O mesmo conjunto de nogueira envernizada dos móveis de quarto (../quarto/modelo.py, de onde vêm os ajudantes).
Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora são
as dos móveis antigos de props/mobilias."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
N, F, _torno = q.N, q.F, q._torno


def _xyz(v):
    """Vértice do Blender -> ponto do jogo (mm)."""
    return v.co.x / lib.MM, v.co.z / lib.MM, -v.co.y / lib.MM


def _mover(o, f):
    """Aplica f(x, y, z) -> (x, y, z), em mm do jogo, a todos os vértices."""
    for v in o.data.vertices:
        v.co = lib.P(*G(*f(*_xyz(v))))
    return o


def _inclinar(o, y0, k):
    """Deita para trás: cada mm acima de y0 recua k mm em z."""
    return _mover(o, lambda x, y, z: (x, y, z - k * (y - y0)))


# ------------------------------------------------------------------ cadeira
def cadeira():
    XF, XT = 210, 186                 # meia largura na frente e atrás
    ZF, ZT = 205, -180                # frente e fundo do assento
    YA = 430                          # topo da armação do assento
    K = 59 / 500.0                    # quanto o encosto deita
    p = []
    for s in (-1, 1):                 # pés da frente torneados
        p.append(caixa(s * (XF - 20) - 20, s * (XF - 20) + 20, YA - 90, YA, ZF - 44, ZF - 4, N + 'y', 2.0))
        p.append(_torno([(0, 0), (11, 0), (13, 6), (13, 16), (10, 24), (13, 70), (18, 200), (19, 300), (15, 318), (19, 330), (19, YA - 90), (0, YA - 90)],
                        N + 'y', s * (XF - 20), 0, ZF - 24, n=14))
        # pé de trás e montante do encosto numa peça só, deitado para trás acima do assento
        x = s * (XT - 18)
        pe = perfil([(ZT + 22, 0), (ZT + 50, 0), (ZT + 42, YA - 80), (ZT + 40, YA), (ZT + 36, 900), (ZT + 12, 900), (ZT + 2, YA), (ZT + 2, YA - 80)], x - 17, x + 17, N + 'y', 3.0)
        _mover(pe, lambda a, b, c: (a, b, c - K * max(0.0, b - YA)))
        p.append(pe)
        p.append(caixa(min(s * (XF - 28), s * (XF - 12)), max(s * (XF - 28), s * (XF - 12)), YA - 80, YA, ZT + 30, ZF - 40, N + 'z', 1.5))      # saia lateral
        p.append(cil((s * (XF - 22), 150, ZT + 30), (s * (XF - 22), 150, ZF - 24), 9, N + 'z', n=10))                                        # travessa lateral
    p.append(caixa(-XF + 36, XF - 36, YA - 80, YA, ZF - 26, ZF - 8, N + 'x', 1.5))                    # saia da frente
    p.append(caixa(-XT + 30, XT - 30, YA - 80, YA, ZT + 6, ZT + 24, N + 'x', 1.5))                    # saia de trás
    p.append(cil((-XF + 22, 150, 20), (XF - 22, 150, 20), 9, N + 'x', n=10))                          # travessa do meio
    # encosto: chapéu curvo, travessa de baixo e a tábua central recortada
    def arco(z0, esp, y0, y1, fl=14):
        pts = [(XT * math.sin(math.radians(t)), z0 - fl * math.cos(math.radians(t)) ** 2) for t in range(-90, 91, 15)]
        o = planta(pts + [(x, z + esp) for x, z in pts[::-1]], y0, y1, N + 'x', 3.0)
        return _inclinar(o, YA, K)
    p.append(arco(ZT + 10, 22, 840, 925))
    p.append(arco(ZT + 12, 18, 560, 600, fl=6))
    tab = frente([(-34, 596), (34, 596), (30, 640), (46, 700), (52, 760), (40, 815), (44, 845), (-44, 845), (-40, 815), (-52, 760), (-46, 700), (-30, 640)],
                 ZT + 12, ZT + 24, N + 'y', 2.0)
    p.append(_inclinar(tab, YA, K))
    parte('armacao', p, origem=G(0, 0, 0), grupo='A')
    # assento estofado, com as tachas na beirada
    a = planta([(-XF + 6, ZF - 2), (XF - 6, ZF - 2), (XT - 2, ZT + 30), (-XT + 2, ZT + 30)], YA, YA + 48, 'estofado_verde')
    bevel(a, 20.0, seg=4, ang=40)
    e = [a, planta([(-XF + 2, ZF + 2), (XF - 2, ZF + 2), (XT + 2, ZT + 26), (-XT - 2, ZT + 26)], YA - 6, YA + 6, N + 'x', 2.0)]
    for k in range(13):
        x = -XF + 16 + (2 * XF - 32) * k / 12
        e.append(_torno([(0, 0), (4.5, 0), (3.5, 2), (0, 3)], 'tacha', x, YA + 10, ZF + 1, n=8, eixo=(0, 0, 1)))
    parte('assento', e, origem=G(0, 0, 0), grupo='A')


# ------------------------------------------------------------------ mesa de jantar
def mesa_jantar():
    X, Z, H = 700, 400, 760
    p = []
    for k, d in enumerate((0, 3, -2, 2)):                                   # tampo de quatro tábuas, de quina boleada
        z0 = -Z + k * 200
        p.append(caixa(-X + (2 if d > 0 else 0), X - (2 if d < 0 else 0), H - 30, H, z0 + 0.6, z0 + 199.4, N + 'x', 5.0 if k in (0, 3) else 1.2))
    p.append(caixa(-X + 14, X - 14, H - 40, H - 28, -Z + 14, Z - 14, N + 'x', 3.0))    # filete embaixo do tampo
    for s in (-1, 1):
        p.append(caixa(-X + 110, X - 110, H - 140, H - 38, min(s * (Z - 70), s * (Z - 92)), max(s * (Z - 70), s * (Z - 92)), N + 'x', 2.0))    # saias
        p.append(caixa(-X + 110, X - 110, H - 140, H - 128, min(s * (Z - 66), s * (Z - 96)), max(s * (Z - 66), s * (Z - 96)), N + 'x', 3.0))   # cordão
        p.append(caixa(min(s * (X - 70), s * (X - 92)), max(s * (X - 70), s * (X - 92)), H - 140, H - 38, -Z + 110, Z - 110, N + 'z', 2.0))
        p.append(caixa(min(s * (X - 66), s * (X - 96)), max(s * (X - 66), s * (X - 96)), H - 140, H - 128, -Z + 110, Z - 110, N + 'z', 3.0))
        for t in (-1, 1):
            x, z = s * (X - 81), t * (Z - 81)
            p.append(caixa(x - 36, x + 36, H - 150, H - 30, z - 36, z + 36, N + 'y', 3.0))
            p.append(_torno([(0, 0), (20, 0), (24, 8), (24, 20), (18, 30), (17, 60), (20, 200), (27, 330), (32, 400), (32, 430), (22, 450), (22, 462), (33, 480),
                             (34, 520), (26, 545), (30, 560), (36, 580), (36, H - 150), (0, H - 150)], N + 'y', x, 0, z, n=18))
    parte('mesa', p, origem=G(0, 0, 0), grupo='A')


# ------------------------------------------------------------------ estante de livros
def _livro(w, h, d, capa, rnd):
    """Livro em pé com a lombada virada para +z: x de 0 a w (espessura), y de 0 a h, z de -d a 0."""
    c = 2.2
    pecas = [caixa(0, c, 0, h, -d, -1, capa), caixa(w - c, w, 0, h, -d, -1, capa)]            # as duas capas
    lomb = planta([(0, -6), (0, -2), (w * 0.2, 0), (w * 0.8, 0), (w, -2), (w, -6)], 0, h, capa)   # lombada arredondada
    pecas.append(lomb)
    pecas.append(caixa(c, w - c, 3, h - 3, -d + 4, -4, 'papel_livro'))
    if rnd.random() < 0.7:                                                                             # filetes dourados na lombada
        for yy in (h * 0.14, h * 0.82) + ((h * 0.70,) if rnd.random() < 0.5 else ()):
            pecas.append(caixa(0.6, w - 0.6, yy, yy + h * 0.022, -0.5, 0.35, 'dourado'))
    if rnd.random() < 0.5:                                                                             # etiqueta do título
        pecas.append(caixa(1.2, w - 1.2, h * 0.52, h * 0.66, -0.5, 0.3, 'capa_6' if capa != 'capa_6' else 'capa_5'))
    return lib.join(pecas, 'livro')


def _por(o, x, y, z, tomba=0.0, deitado=False):
    """Põe o livro no lugar. tomba = graus caído para a direita (apoiado no vizinho); deitado = de lado, lombada à frente."""
    a = math.radians(-90 if deitado else -tomba)
    ca, sa = math.cos(a), math.sin(a)
    return _mover(o, lambda px, py, pz: (x + px * ca - py * sa, y + px * sa + py * ca, z + pz))


def estante_livros():
    X, H, Z0, Z1 = 450, 1800, -160, 160
    NIVEIS = [82, 430, 780, 1130, 1470]                    # em cima de cada prateleira (o mesmo dos livros antigos)
    c = caixa(-X + 9, X - 9, 60, H, Z0, Z1, N + 'y')
    cut(c, caixa(-X + 26, X - 26, 82, H - 22, Z0 + 8, Z1 + 5, N + 'y'))
    p = [bevel(c, 1.5)]
    for y in NIVEIS[1:]:
        p.append(caixa(-X + 26, X - 26, y - 22, y, Z0 + 8, Z1 - 4, N + 'x', 1.5))
    for s in (-1, 1):
        p += q._almofada_lado(s, X, 8, 60, H, Z0, Z1, mont=60, trav=70, meio=(780,))
    p += q._saia(X + 4, 0, 64, Z0, Z1 + 12, pe=80)
    p.append(caixa(-X + 6, X - 6, 20, 60, Z0, Z0 + 12, N + 'x'))
    for dx, ya, yb, ch in ((6, H, H + 10, 2.0), (15, H + 10, H + 30, 6.0)):          # cornija baixa
        p.append(caixa(-X - dx, X + dx, ya, yb, Z0 - 5 if dx > 10 else Z0, Z1 + dx + 5, N + 'x', ch))
    parte('estante', p, origem=G(0, 0, 0), grupo='A')
    # livros: casa saqueada, então há vãos, livros tombados e pilhas deitadas
    rnd = random.Random(11)
    liv = []
    for i, y in enumerate(NIVEIS):
        x, fim = -X + 30.0, X - 30.0
        vao = rnd.uniform(-200, 150) if i != 1 else 999
        while x < fim - 25:
            if abs(x - vao) < 12:                                                    # um vão: os livros do lado tombam para dentro dele
                larg = rnd.uniform(110, 190)
                if rnd.random() < 0.6 and x + larg + 60 < fim:                       # pilha deitada no vão
                    yy = y
                    for _ in range(rnd.randint(1, 3)):
                        w, h, d = rnd.uniform(22, 42), rnd.uniform(190, 250), rnd.uniform(140, 200)
                        liv.append(_por(_livro(w, h, d, f'capa_{rnd.randint(1, 6)}', rnd), x + 8 + rnd.uniform(0, 8), yy + w, Z1 - 14 - rnd.uniform(0, 20), deitado=True))
                        yy += w
                    x += 270
                else:
                    x += larg
                continue
            w, h, d = rnd.uniform(18, 46), rnd.uniform(185, 285), rnd.uniform(140, 215)
            if x + w > fim:
                break
            tomba = 0.0
            if abs(x + w + 14 - vao) < 30 and x - 60 > -X + 30:
                tomba = -rnd.uniform(9, 16)                                           # o último antes do vão cai para a esquerda, sobre os outros
            capa = f'capa_{rnd.randint(1, 6)}'
            o = _livro(w, h, d, capa, rnd)
            if tomba:
                liv.append(_por(o, x + w + 6, y, Z1 - 12 - rnd.uniform(0, 14), tomba=0))
                _mover(o, lambda px, py, pz, x0=x + w + 6, y0=y, a=math.radians(-tomba): (x0 + (px - x0) * math.cos(a) - (py - y0) * math.sin(a), y0 + (px - x0) * math.sin(a) + (py - y0) * math.cos(a), pz))
                x += w + 6 + h * math.sin(math.radians(-tomba)) * 0.2
            else:
                liv.append(_por(o, x, y, Z1 - 12 - rnd.uniform(0, 14)))
                x += w + rnd.uniform(0.6, 1.8)
    parte('livros', liv, origem=G(0, 0, 0), grupo='B')


FORMAS = {'cadeira': cadeira, 'mesa_jantar': mesa_jantar, 'estante_livros': estante_livros}
