"""Forma da picape Lida: desenho próprio (frente quadrada e alta, capô reto, para-brisa mais em pé, teto mais alto), cabine simples e
caçamba aberta. O entre-eixos, o motor, as rodas e o interior são os do sedã Rumo.

Medidas (m): comprimento da carroceria 4,50 (4,62 com para-choques), largura 1,68, altura 1,46, entre-eixos 2,55.
Caçamba de 1,48 m de comprimento por 1,46 m de largura, 0,53 m de fundo. Carrega sedan_forma.py e troca o que muda.
"""
import os
from forma import prisma_xy

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sedan_forma.py'), encoding='utf-8').read(), 'sedan_forma.py', 'exec'))

TIPO = 'picape'
PORTAS = 'd'                  # só as portas dianteiras (as mesmas do sedã)
ZR = -2.40
ZBL = -0.80                   # fim da cabine (parede de trás)
Z_CAB = -0.88                 # frente da caçamba
Y_FUNDO = 0.50                # assoalho da caçamba
REC_CACAMBA = 0.085           # largura da borda (chapa de fora até a parede de dentro)
Z_BOCAL = -1.95
Z_CALHA = -0.70
Z_FORRO_TRAS = -0.72
Z_PISO_TRAS = -0.78
Z_MIOLO = -0.79
Z_PC_TRAS = -1.75
LANTERNA = (0.632, 0.772, 0.640, 0.945)   # a mesma lanterna em pé do hatch
X_TAMPA = 0.62
LANTERNA_FUNDO = 0.045                     # rasa, para não furar a parede da caçamba
TAMPA = (ZR + 0.02, -90, Y_FUNDO + 0.06)  # tampa da caçamba: dobradiça embaixo, cai para trás
ITEM_TAMPA = 'tampa_cacamba'
VIDRO_TRAS = ((0, 1.20, -0.79), (90, 0, 0), 'vidro_traseiro_cabine', None)
ESTEPE = (Y_FUNDO + 0.095, -1.22)
JANELAS = None                # definido depois das funções

# frente própria
SUFIXO_FRENTE = '_picape'
DY_CINTURA = 0.065            # cintura 6,5 cm mais alta que a do sedã
Y_TETO_CORTE = 1.37
Z_TOPO_PARABRISA = 0.03
FAROL = (0.42, 0.79, 0.645, 0.805)        # dois faróis quadrados de cada lado
FAROL_PISCA = 0.06
GRADE = (0.405, 0.630, 0.830)
GRADE_ESTILO = 'barras'
CAPO_Y0 = 0.885
MAT_PARA_CHOQUE = 'cromado'   # para-choques de aço cromado


def fx(z):  # frente quase reta (quinas vivas), traseira como a da caçamba
    d = z / ZF if z > 0 else z / ZR
    d = min(abs(d), 1.0); n = 14 if z > 0 else 9
    return max((1 - d ** n) ** (1 / n), 0.02)


def hw(z):  # a frente tem a mesma largura do resto (caixote)
    return HW - 0.008 * max(0.0, z / ZF) ** 2 - 0.012 * max(0.0, z / ZR) ** 2


def _tumble(z):
    return 0.09


def meio_cabine(z, enc=0.0, desce=0.0):
    yb_ = yt(z) - 0.03 - (0.06 if enc else 0.0) - desce
    yt_ = max(ytop(z) - enc, yt(z) + 0.004)
    h = yt_ - (yt(z) - 0.03)
    wb = larg_cintura(z) - enc
    wt = wb - _tumble(z) * min(h, 0.46) / 0.46
    return [(0, yb_), (wb, yb_)] + ([(wb, yt(z) - 0.03)] if enc else []) + [(wb - 0.006, yt(z) + 0.02), (wt + 0.03, yt_ - 0.045), (wt + 0.01, yt_ - 0.015),
            (wt - 0.025, yt_ - 0.003), (wt - 0.2, yt_), (0, yt_ + 0.002)]


def quina_cabine(z):
    h = ytop(z) - (yt(z) - 0.03); wb = larg_cintura(z); wt = wb - _tumble(z) * min(h, 0.46) / 0.46
    return wt + 0.02, ytop(z) - 0.04


def yt(z):  # cintura alta e reta até atrás; capô alto e reto que dobra em quina na frente
    return _i(z, [(-2.40, 0.995), (-2.392, 1.018), (-2.37, 1.031), (-2.30, 1.037), (-1.7, 1.038), (-1.2, 1.030), (-0.4, 1.017),
                  (0.3, 1.005), (0.64, 0.998), (0.8, 0.992), (1.2, 0.982), (1.6, 0.970), (1.9, 0.958), (2.0, 0.950), (2.05, 0.935),
                  (2.08, 0.912), (2.10, 0.875)])


def yb(z):
    return _i(z, [(-2.40, 0.40), (-2.385, 0.33), (-2.34, 0.27), (-2.22, 0.235), (-1.6, 0.225), (1.65, 0.225), (1.85, 0.24), (2.0, 0.27), (2.10, 0.31)])


def ytop(z):  # cabine simples mais alta: para-brisa mais em pé, teto reto até a parede de trás
    return _i(z, [(-0.80, 1.02), (-0.797, 1.26), (-0.792, 1.36), (-0.775, 1.415), (-0.74, 1.442), (-0.66, 1.453),
                  (-0.4, 1.457), (-0.1, 1.454), (0.0, 1.447), (0.06, 1.428), (0.20, 1.330), (0.40, 1.180), (0.56, 1.060), (0.64, 1.000)])


def janela_terceira(borda=0.0):
    """Vidro fixo pequeno atrás da porta, até a parede da cabine."""
    z0 = -0.445 + borda; z1 = -0.705 - borda
    top = [(z, min(Y_TETO_CORTE - 0.035, ytop(z + 0.02) - 0.07) + borda) for z in np.linspace(z0, z1, 20)]
    bot = [(z, yt(z) + 0.012 - borda) for z in np.linspace(z1, z0, 8)]
    return Polygon(top + bot).buffer(0)


JANELAS = (janela_dianteira, janela_terceira)


def _vidro_tras_pg(borda=0.0):
    return sbox(-0.50 - borda, 1.10 - borda, 0.50 + borda, 1.32 + borda).buffer(0.05, join_style=1).buffer(-0.05, join_style=1)


def vidro_tras_vao(borda=0.0):
    """Vão do vidro de trás da cabine (atravessa a parede de trás)."""
    return prisma_xy(_vidro_tras_pg(-borda), -0.86, -0.74)


def vidro_tras_vidro():
    return prisma_xy(_vidro_tras_pg(-0.012), -0.792, -0.786)


def planta_cacamba(rec, z0=None, z1=None):
    """Contorno da caçamba em planta, rec m para dentro da chapa de fora."""
    return _planta(Z_CAB if z0 is None else z0, ZR + 0.035 if z1 is None else z1, rec, 0.6, n=40)


Z_POSTE = ZR + 0.13           # atrás disto só a abertura da tampa: as quinas (onde ficam as lanternas) são colunas cheias
X_ABERTURA = 0.60


def vazios():
    """O que a caçamba tira da casca: tudo acima do assoalho, por dentro das bordas, até as colunas das quinas."""
    return [uniao([prisma_xz(planta_cacamba(REC_CACAMBA, z1=Z_POSTE), Y_FUNDO, 2.0),
                   caixa(-X_ABERTURA, X_ABERTURA, Y_FUNDO, 2.0, ZR + 0.035, Z_POSTE + 0.01)])]


def regiao_tampa(g=0.0):
    """Tampa da caçamba: a parede de trás entre as lanternas, do assoalho à borda."""
    pg = Polygon([(ZR + 0.10, Y_FUNDO + 0.055), (ZR + 0.10, 2.0), (-2.7, 2.0), (-2.7, Y_FUNDO + 0.055)])
    if g: pg = pg.buffer(g, join_style=2)
    return prisma_zy(pg, -X_TAMPA - g, X_TAMPA + g)
