"""Forma da picape Lida: a frente, o entre-eixos e as portas dianteiras do sedã Rumo (família Rumo), cabine simples e caçamba aberta.

Medidas (m): comprimento da carroceria 4,50 (4,62 com para-choques), largura 1,68, altura 1,39, entre-eixos 2,55.
Caçamba de 1,48 m de comprimento por 1,46 m de largura, 0,47 m de fundo. Carrega sedan_forma.py e troca o que muda.
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
LANTERNA = (0.632, 0.772, 0.640, 0.925)
X_TAMPA = 0.62
LANTERNA_FUNDO = 0.045                     # rasa, para não furar a parede da caçamba
TAMPA = (ZR + 0.02, -90, Y_FUNDO + 0.06)  # tampa da caçamba: dobradiça embaixo, cai para trás
ITEM_TAMPA = 'tampa_cacamba'
VIDRO_TRAS = ((0, 1.14, -0.79), (90, 0, 0), 'vidro_traseiro_cabine', None)
ESTEPE = (Y_FUNDO + 0.095, -1.22)
JANELAS = None                # definido depois das funções


def yt(z):  # borda da caçamba reta até atrás
    return _i(z, [(-2.40, 0.935), (-2.392, 0.958), (-2.37, 0.971), (-2.30, 0.977), (-1.7, 0.978), (-1.2, 0.968), (-0.4, 0.952),
                  (0.3, 0.935), (0.64, 0.925), (0.8, 0.905), (1.2, 0.86), (1.6, 0.81), (1.85, 0.78), (2.0, 0.755), (2.07, 0.73), (2.10, 0.70)])


def yb(z):
    return _i(z, [(-2.40, 0.40), (-2.385, 0.33), (-2.34, 0.27), (-2.22, 0.235), (-1.6, 0.225), (1.65, 0.225), (1.85, 0.25), (2.0, 0.29), (2.10, 0.33)])


def ytop(z):  # cabine simples: o teto vai até a parede de trás, quase em pé
    return _i(z, [(-0.80, 0.96), (-0.797, 1.20), (-0.792, 1.29), (-0.775, 1.345), (-0.74, 1.372), (-0.66, 1.386),
                  (-0.5, 1.39), (-0.32, 1.383), (-0.22, 1.365), (-0.08, 1.31), (0.12, 1.225), (0.34, 1.12), (0.52, 1.02), (0.64, 0.93)])


def janela_terceira(borda=0.0):
    """Vidro fixo pequeno atrás da porta, até a parede da cabine."""
    z0 = -0.445 + borda; z1 = -0.705 - borda
    top = [(z, min(Y_TETO_CORTE - 0.035, ytop(z + 0.02) - 0.07) + borda) for z in np.linspace(z0, z1, 20)]
    bot = [(z, yt(z) + 0.012 - borda) for z in np.linspace(z1, z0, 8)]
    return Polygon(top + bot).buffer(0)


JANELAS = (janela_dianteira, janela_terceira)


def _vidro_tras_pg(borda=0.0):
    return sbox(-0.50 - borda, 1.035 - borda, 0.50 + borda, 1.255 + borda).buffer(0.05, join_style=1).buffer(-0.05, join_style=1)


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
