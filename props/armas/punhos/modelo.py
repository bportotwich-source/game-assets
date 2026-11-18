"""Punhos de pistola trocáveis dos fuzis (encaixe_punho) no nível de detalhe da M4A1: o original
quadriculado, o emborrachado com cavas para os dedos e o reto com rabo de castor e compartimento.
Mais o adaptador que deixa os punhos de 7,62 (AKMN) entrarem nos fuzis de receptor de alumínio.
Desenho próprio, sem marcas.

Coordenadas da M4A1 em mm (lib.py): u = para a frente, v = para cima, w = direita. O punho é
montado em volta do eixo T -> B (do alto, embaixo do receptor, até a base) e recortado pela linha
de baixo do receptor inferior da M4A1, por isso assenta nela sem folga. A origem é o encaixe_punho.
"""
import math
from mathutils import Vector
from lib import *

LINHA_BAIXO = [(-134, -50), (-136, -55), (-172, -55), (-178, -51), (-196, -35), (-213, -29)]    # a de m4a1/modelo.py

ENCAIXE = (-165.0, -45.0)                                   # nó encaixe_punho nas coordenadas da M4A1 (origem dela em -182, -93)
LIM = [(-110, -55)] + LINHA_BAIXO[2:] + [(-240, -29), (-240, 10), (-110, 10)]     # tudo que é do receptor


class Eixo:
    def __init__(self, T, B):
        self.T, self.B = Vector(T), Vector(B)
        self.L = (self.B - self.T).length
        self.a = (self.B - self.T) / self.L
        e = Vector((-self.a.y, self.a.x))
        self.e = e if e.x > 0 else -e                        # perpendicular apontando para a frente

    def p(self, t, s=0.0, w=0.0):
        q = self.T + self.a * self.L * t + self.e * s
        return (q.x, q.y, w)

    def anel(self, t, df, dr, hw, n=36, exp=2.7):
        c = self.T + self.a * self.L * t
        cx, rx = (df - dr) / 2, (df + dr) / 2
        out = []
        for (x, y) in superelipse(rx, hw, n=n, e=exp, cx=cx):
            q = c + self.e * x
            out.append(P(q.x, q.y, y))
        return out


def _corpo(E, ts, df, dr, hw, mat, exp=2.7, n=36):
    g = loft([E.anel(t, df(t), dr(t), hw(t), n=n, exp=exp(t) if callable(exp) else exp) for t in ts], mat)
    return cut(g, extr(LIM, -30, 30, mat))


def _ts(t0, t1, passo, fim=(0.955, 0.985, 1.0)):
    out, t = [], t0
    while t < 0.94:
        out.append(round(t, 4)); t += passo
    return out + list(fim)


def _fecho(t):
    """Quanto a base afina nos últimos anéis (mm)."""
    return 0.0 if t < 0.95 else (1.1 if t < 0.98 else (2.6 if t < 0.999 else 6.0))


def _tang(t, k0=0.22, k1=0.30):
    k = max(0.0, min(1.0, (k0 - t) / k1))
    return k * k * (3 - 2 * k)


# ------------------------------------------------------------------ o original
def punho_ar():
    E = Eixo((-160.0, -56.0), (-207.0, -146.0))
    df = lambda t: 18 + 4.4 * math.exp(-((t - 0.34) / 0.07) ** 2) - 1.5 * max(0, t - 0.5) - _fecho(t)
    dr = lambda t: 17.5 + 24 * _tang(t) + 3.0 * max(0, t - 0.75) / 0.25 - _fecho(t)
    hw = lambda t: 14.6 - 1.3 * max(0, t) - 3.0 * _tang(t) - _fecho(t) * 0.8
    o = [_corpo(E, _ts(-0.30, 1.0, 0.03), df, dr, hw, 'polim_grip')]
    # base: boca oca com a arruela e o parafuso que prende o punho ao receptor
    o.append(extr([E.p(1.0, 11.5)[:2], E.p(1.0, -15.5)[:2], E.p(0.975, -15.5)[:2], E.p(0.975, 11.5)[:2]], -8.4, 8.4, 'polim_fundo'))
    c = E.p(0.985, -2.0)
    o.append(cyl(c, E.p(1.004, -2.0), 6.2, 'fosf', n=20))
    o.append(cyl(E.p(1.004, -2.0), E.p(1.02, -2.0), 4.0, 'fosf', n=6))
    return parte('punho', o, origem=(*ENCAIXE, 0), grupo='A', suave=45)


# ------------------------------------------------------------------ emborrachado com cavas
def punho_cavas():
    E = Eixo((-160.0, -56.0), (-205.0, -150.0))
    def df(t):
        d = 18.4 + 4.6 * math.exp(-((t - 0.335) / 0.06) ** 2)                 # ressalto do dedo médio, embaixo do guarda-mato
        if 0.40 < t < 0.95:
            d += 1.9 * math.cos(2 * math.pi * (t - 0.515) / 0.18) * min(1.0, (t - 0.40) / 0.05, (0.95 - t) / 0.05)   # três cavas
        return d - 0.8 * max(0, t - 0.5) - _fecho(t)
    dr = lambda t: 18.5 + 25 * _tang(t) + 3.2 * math.exp(-((t - 0.52) / 0.22) ** 2) + 2.5 * max(0, t - 0.8) / 0.2 - _fecho(t)   # palma cheia
    hw = lambda t: 15.4 - 1.0 * max(0, t) - 3.6 * _tang(t) + 1.2 * math.exp(-((t - 0.55) / 0.2) ** 2) - _fecho(t) * 0.8
    o = [_corpo(E, _ts(-0.30, 1.0, 0.02), df, dr, hw, 'borracha_grip', exp=2.35, n=40)]
    # colar liso de polímero no alto (onde encosta no receptor)
    pintar(o[0], 'polim', lambda c, n: ((c[0] - E.T.x) * E.a.x + (c[1] - E.T.y) * E.a.y) / E.L < 0.13)
    # sapata larga na base, que apoia o mindinho, com a tampa do compartimento e a fenda de moeda
    b0, b1 = E.p(0.985, 0), E.p(1.045, 0)
    sap = loft([E.anel(t, f, r, h, n=40, exp=2.6) for (t, f, r, h) in ((0.975, 15.0, 19.5, 12.8), (0.99, 19.5, 23.5, 15.2), (1.03, 20.0, 24.0, 15.6), (1.045, 18.6, 22.6, 14.4))], 'polim')
    o.append(sap)
    o.append(cyl(E.p(1.04, -2.0), E.p(1.052, -2.0), 9.0, 'polim_fundo', n=28))
    o.append(bevel(box(-3.2, 3.2, -0.5, 0.5, -0.6, 0.6, 'fosf'), 0.1, 1))
    o[-1].data.transform(__import__('mathutils').Matrix.Translation(P(*E.p(1.052, -2.0))))
    return parte('punho', o, origem=(*ENCAIXE, 0), grupo='A', suave=50)


# ------------------------------------------------------------------ reto, com rabo de castor
def punho_reto():
    E = Eixo((-160.0, -56.0), (-190.0, -152.0))
    df = lambda t: 17.2 + 2.2 * math.exp(-((t - 0.30) / 0.05) ** 2) - 0.6 * max(0, t - 0.4) - _fecho(t)
    def dr(t):
        d = 18.0 + 27 * _tang(t, 0.20, 0.26) + 2.0 * max(0, t - 0.7) / 0.3
        d += 7.5 * math.exp(-((t - 0.105) / 0.035) ** 2)                      # rabo de castor
        return d - _fecho(t)
    hw = lambda t: 13.6 - 0.6 * max(0, t) - 2.4 * _tang(t) - _fecho(t) * 0.8
    g = _corpo(E, _ts(-0.30, 1.0, 0.02), df, dr, hw, 'polim', exp=lambda t: 3.6 if t > 0.2 else 2.8, n=40)
    # painéis de pontilhado fino dos lados e faixas nervuradas na frente e nas costas
    def painel(c, n):
        u, v = c[0], c[1]
        t = ((u - E.T.x) * E.a.x + (v - E.T.y) * E.a.y) / E.L
        s = (u - E.T.x) * E.e.x + (v - E.T.y) * E.e.y
        return abs(n[2]) > 0.8 and 0.30 < t < 0.90 and -13.5 < s < 12.0
    pintar(g, 'polim_pontos', painel)
    o = [g]
    for k in range(9):                                                         # nervuras da frente
        t = 0.40 + k * 0.06
        o.append(bevel(extr([E.p(t, 15.6 - 0.6 * max(0, t - 0.4))[:2], E.p(t, 17.9 - 0.6 * max(0, t - 0.4))[:2],
                             E.p(t + 0.022, 17.9 - 0.6 * max(0, t - 0.4))[:2], E.p(t + 0.022, 15.6 - 0.6 * max(0, t - 0.4))[:2]], -7.4, 7.4, 'polim'), 0.45, 1))
    for k in range(8):                                                         # nervuras das costas
        t = 0.36 + k * 0.07
        d = 18.0 + 2.0 * max(0, t - 0.7) / 0.3
        o.append(bevel(extr([E.p(t, -d + 2.2)[:2], E.p(t, -d - 0.75)[:2], E.p(t + 0.026, -d - 0.75)[:2], E.p(t + 0.026, -d + 2.2)[:2]], -6.8, 6.8, 'polim'), 0.45, 1))
    # tampa do compartimento na base, com a trava de aço e o rebaixo de puxar
    o.append(bevel(extr([E.p(0.99, 13.4)[:2], E.p(0.99, -16.6)[:2], E.p(1.022, -15.6)[:2], E.p(1.022, 12.4)[:2]], -9.6, 9.6, 'polim_fundo'), 0.8, 2))
    o.append(bevel(extr([E.p(1.01, 12.0)[:2], E.p(1.01, 16.2)[:2], E.p(1.03, 16.2)[:2], E.p(1.03, 12.0)[:2]], -4.2, 4.2, 'fosf'), 0.4, 1))
    o.append(pin(E.p(0.955, -12)[0], E.p(0.955, -12)[1], 1.5, -13.2, 13.2, 'inox', n=10))        # pino da tampa
    return parte('punho', o, origem=(*ENCAIXE, 0), grupo='A', suave=45)


# ------------------------------------------------------------------ adaptador dos punhos de 7,62
ADAPT_GRAUS = 10.0        # quanto o punho de 7,62 gira para trás para ficar no ângulo da mão destes fuzis
ADAPT_CENTRO = (-182.0, -93.0)        # origem da arma (centro do punho) nas coordenadas da M4A1: aí fica o centro do punho de 7,62
ADAPT_TOPO = 47.8         # altura do topo plano do punho de 7,62 acima do centro dele


def _girado(z, y):
    """Ponto do punho de 7,62 (z para trás, y para cima, mm, no sistema dele) -> (u, v) da M4A1."""
    a = math.radians(ADAPT_GRAUS)
    zz = z * math.cos(a) - y * math.sin(a)
    yy = z * math.sin(a) + y * math.cos(a)
    return (ADAPT_CENTRO[0] - zz, ADAPT_CENTRO[1] + yy)


def adaptador_punho_762():
    """Sapata de aço que aparafusa embaixo do receptor de alumínio e abraça o alto do punho de 7,62."""
    y = ADAPT_TOPO - 8.5
    a, b = _girado(-39.6, y), _girado(21.6, y)
    g = extr([a, b, (b[0] - 6.0, 10), (a[0] + 2.0, 10)], -13.9, 13.9, 'fosf')
    cut(g, extr(LIM, -30, 30, 'fosf'))
    bevel(g, 1.0, 2, 30)
    o = [g]
    for z in (-26.0, 8.0):                                                     # cabeças dos parafusos que apertam o punho, dos dois lados
        u, v = _girado(z, y + 4.6)
        o.append(pin(u, v, 2.4, -14.5, 14.5, 'inox', n=6))
    return parte('adaptador', o, origem=(*ENCAIXE, 0), grupo='A', suave=40)
