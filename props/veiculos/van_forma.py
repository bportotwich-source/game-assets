"""Forma da van Jornada: desenho próprio (bico curto e redondo, para-brisa grande e deitado, teto alto contínuo desde o para-brisa),
baú de carga e duas portas atrás. O entre-eixos, o motor, as rodas e o interior da cabine são os do sedã Rumo.

Medidas (m): comprimento da carroceria 4,50 (4,62 com para-choques), largura 1,68, altura 1,80, entre-eixos 2,55.
Baú de 1,60 m de comprimento por 1,40 m de largura entre as forrações, 1,28 m de altura do assoalho ao teto.
Carrega sedan_forma.py e troca o que muda.
"""
import os
from forma import prisma_xy

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sedan_forma.py'), encoding='utf-8').read(), 'sedan_forma.py', 'exec'))

TIPO = 'van'
PORTAS = 'd'                  # portas dianteiras; as de trás são as duas do baú (regioes_extra)
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

# frente própria
SUFIXO_FRENTE = '_van'
ZWS = 0.72                    # base do para-brisa mais para a frente
Z_CAPO = 0.78
DY_CINTURA = 0.04             # cintura 4 cm mais alta que a do sedã
CAPO_Y0 = 0.70
Y_PARALAMA = 0.99             # o para-lama não sobe na coluna do para-brisa
Y_TETO_CORTE = 1.56           # janelas das portas bem altas
Z_TOPO_PARABRISA = -0.10
FAROL = (0.40, 0.80, 0.600, 0.700)        # faróis largos e baixos
FAROL_PISCA = 0.075
GRADE = (0.36, 0.612, 0.688)
GRADE_ESTILO = 'fenda'


def fx(z):  # frente arredondada; atrás quase reta (quinas do baú)
    d = z / ZF if z > 0 else z / ZR
    d = min(abs(d), 1.0); n = 6 if z > 0 else 20     # bico redondo, traseira de baú
    return max((1 - d ** n) ** (1 / n), 0.02)


def yt(z):  # cintura reta até atrás; capô curto que cai continuando a linha do para-brisa
    return _i(z, [(-2.40, 0.955), (-2.392, 0.978), (-2.37, 0.991), (-2.30, 0.997), (-1.7, 0.998), (-1.2, 0.992), (-0.4, 0.985),
                  (0.3, 0.976), (0.72, 0.966), (0.85, 0.950), (1.0, 0.928), (1.4, 0.874), (1.75, 0.822), (1.95, 0.784), (2.05, 0.748), (2.10, 0.70)])


def hw(z):  # a frente afina mais que a do sedã (bico redondo)
    return HW - 0.05 * max(0.0, z / ZF) ** 2 - 0.012 * max(0.0, z / ZR) ** 2


def yb(z):
    return _i(z, [(-2.40, 0.40), (-2.385, 0.33), (-2.34, 0.27), (-2.22, 0.235), (-1.6, 0.225), (1.65, 0.225), (1.85, 0.25), (2.0, 0.29), (2.10, 0.33)])


def ytop(z):  # para-brisa grande e deitado que sobe direto para o teto alto, reto até atrás
    return _i(z, [(ZR, 1.772), (ZR + 0.008, 1.788), (ZR + 0.025, 1.798), (ZR + 0.06, 1.80), (-1.0, 1.805), (-0.40, 1.80), (-0.24, 1.787),
                  (-0.14, 1.756), (-0.06, 1.700), (0.03, 1.610), (0.15, 1.485), (0.30, 1.340), (0.45, 1.200), (0.60, 1.068), (0.72, 0.970)])


def _tumble(z):
    """Lateral quase em pé em toda a cabine e no baú."""
    return 0.05


def janela_dianteira(borda=0.0, _orig=janela_dianteira):
    """A da família, cortada na frente: a coluna do para-brisa fica na carroceria, não na porta."""
    return _orig(borda).intersection(sbox(-3, 0, 0.565 + borda, 3))


def meio_cabine(z, enc=0.0, desce=0.0):
    yb_ = yt(z) - 0.03 - (0.06 if enc else 0.0) - desce
    yt_ = max(ytop(z) - enc, yt(z) + 0.004)
    h = yt_ - (yt(z) - 0.03)
    wb = larg_cintura(z) - enc
    wt = wb - _tumble(z) * min(h, 0.46) / 0.46
    return [(0, yb_), (wb, yb_)] + ([(wb, yt(z) - 0.03)] if enc else []) + [(wb - 0.006, yt(z) + 0.02), (wt + 0.045, yt_ - 0.075), (wt + 0.018, yt_ - 0.028),
            (wt - 0.03, yt_ - 0.005), (wt - 0.2, yt_), (0, yt_ + 0.006)]


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
