"""Forma da van Jornada: a frente, o entre-eixos e as portas dianteiras do sedã Rumo (família Rumo), com o baú de teto alto e duas portas atrás.

Medidas (m): comprimento da carroceria 4,50 (4,62 com para-choques), largura 1,68, altura 1,80, entre-eixos 2,55.
Baú de 1,60 m de comprimento por 1,40 m de largura entre as forrações, 1,28 m de altura do assoalho ao teto.
Carrega sedan_forma.py e troca o que muda.
"""
import os
from forma import prisma_xy

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sedan_forma.py'), encoding='utf-8').read(), 'sedan_forma.py', 'exec'))

TIPO = 'van'
PORTAS = 'd'                  # portas dianteiras do sedã; as de trás são as duas do baú (regioes_extra)
ZR = -2.40
ZBL = ZR + 0.001              # o teto alto vai até a traseira
TAMPA = None                  # sem tampa: o baú abre pelas portas de trás
VIDRO_TRAS = None             # os vidros de trás ficam nas portas
Z_BOCAL = -1.95
Z_CALHA = -0.38
Z_FORRO_TRAS = -0.72
Z_PISO_TRAS = -0.78
Z_MIOLO = -0.79
Z_PC_TRAS = -1.75
Z_DIVISORIA = -0.80           # grade entre a cabine e o baú
Y_PISO = 0.50                 # assoalho de compensado do baú
X_FORRO = 0.70                # forração lateral do baú (compensado)
Y_PORTA = (0.55, 1.73)        # portas de trás: de baixo até em cima
X_PORTA = 0.62                # dobradiça das portas de trás (as quinas, com as lanternas, são colunas da carroceria)
LANTERNA = (0.632, 0.772, 0.640, 0.945)   # a mesma lanterna em pé do hatch
LANTERNA_FUNDO = 0.045
ESTEPE = (0.36, -1.93)        # deitado debaixo do assoalho, no poço
JANELAS = None                # definido depois das funções


def fx(z):  # a frente igual à do sedã; atrás quase reta (quinas do baú)
    d = z / ZF if z > 0 else z / ZR
    d = min(abs(d), 1.0); n = 9 if z > 0 else 20
    return max((1 - d ** n) ** (1 / n), 0.02)


def yt(z):  # linha de cintura reta até atrás (a mesma da picape)
    return _i(z, [(-2.40, 0.935), (-2.392, 0.958), (-2.37, 0.971), (-2.30, 0.977), (-1.7, 0.978), (-1.2, 0.968), (-0.4, 0.952),
                  (0.3, 0.935), (0.64, 0.925), (0.8, 0.905), (1.2, 0.86), (1.6, 0.81), (1.85, 0.78), (2.0, 0.755), (2.07, 0.73), (2.10, 0.70)])


def yb(z):
    return _i(z, [(-2.40, 0.40), (-2.385, 0.33), (-2.34, 0.27), (-2.22, 0.235), (-1.6, 0.225), (1.65, 0.225), (1.85, 0.25), (2.0, 0.29), (2.10, 0.33)])


def ytop(z):  # o teto da cabine é o do sedã até a coluna do meio; atrás sobe para o teto alto do baú
    return _i(z, [(ZR, 1.772), (ZR + 0.008, 1.788), (ZR + 0.025, 1.798), (ZR + 0.06, 1.80), (-1.0, 1.805), (-0.88, 1.80), (-0.79, 1.782),
                  (-0.70, 1.735), (-0.61, 1.64), (-0.53, 1.52), (-0.47, 1.43), (-0.42, 1.396), (-0.38, 1.388),
                  (-0.32, 1.383), (-0.22, 1.365), (-0.08, 1.31), (0.12, 1.225), (0.34, 1.12), (0.52, 1.02), (0.64, 0.93)])


def _tumble(z):
    """Quanto a lateral da cabine entra até o teto: 0,13 como no sedã nas portas, 0,035 no baú (parede quase em pé)."""
    t = min(max((-0.45 - z) / 0.40, 0.0), 1.0); t = t * t * (3 - 2 * t)
    return 0.13 + (0.035 - 0.13) * t


def meio_cabine(z, enc=0.0, desce=0.0):
    yb_ = yt(z) - 0.03 - (0.06 if enc else 0.0) - desce
    yt_ = max(ytop(z) - enc, yt(z) + 0.004)
    h = yt_ - (yt(z) - 0.03)
    wb = larg_cintura(z) - enc
    wt = wb - _tumble(z) * min(h, 0.46) / 0.46
    return [(0, yb_), (wb, yb_)] + ([(wb, yt(z) - 0.03)] if enc else []) + [(wb - 0.006, yt(z) + 0.02), (wt + 0.035, yt_ - 0.055), (wt + 0.012, yt_ - 0.02),
            (wt - 0.03, yt_ - 0.004), (wt - 0.2, yt_), (0, yt_ + 0.004)]


def quina_cabine(z):
    h = ytop(z) - (yt(z) - 0.03); wb = larg_cintura(z); wt = wb - _tumble(z) * min(h, 0.46) / 0.46
    return wt + 0.02, ytop(z) - 0.04


JANELAS = (janela_dianteira,)


# ---------------------------------------------------------------------------- portas de trás
def _vidros_tras_pg(borda=0.0):
    """Os dois vidros das portas de trás (plano x, y)."""
    pgs = []
    for s in (1, -1):
        x0, x1 = sorted((s * 0.09, s * 0.53))
        pgs.append(sbox(x0 - borda, 1.20 - borda, x1 + borda, 1.62 + borda).buffer(0.04, join_style=1).buffer(-0.04, join_style=1))
    return unary_union(pgs)


def _prismas(pg, z0, z1):
    return unary_union_m([prisma_xy(g, z0, z1) for g in getattr(pg, 'geoms', [pg])])


def unary_union_m(ms):
    return uniao(ms) if len(ms) > 1 else ms[0]


def vidro_tras_vao(borda=0.0):
    return _prismas(_vidros_tras_pg(-borda), ZR - 0.05, ZR + 0.10)


def vidro_tras_vidro():
    return _prismas(_vidros_tras_pg(-0.012), ZR + 0.011, ZR + 0.017)


def regiao_porta_tras(lado=1, g=0.0):
    y0, y1 = Y_PORTA
    m = caixa(0.002 - g, X_PORTA + g, y0 - g, y1 + g, ZR - 0.2, ZR + 0.06 + g)
    return m if lado > 0 else espelhar_x(m)


def regioes_extra():
    return [('porta_te', regiao_porta_tras(1), regiao_porta_tras(1, FOLGA)), ('porta_td', regiao_porta_tras(-1), regiao_porta_tras(-1, FOLGA))]
