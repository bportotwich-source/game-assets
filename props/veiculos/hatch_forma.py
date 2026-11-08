"""Forma do hatch Brisa: a mesma frente, entre-eixos e portas dianteiras do sedã Rumo (família Rumo), com a traseira curta,
o teto que vai até o fim e a tampa traseira com o vidro.

Medidas (m): comprimento da carroceria 4,10 (4,22 com para-choques), largura 1,68, altura 1,39, entre-eixos 2,55.
Carrega as funções de sedan_forma.py neste módulo e troca só o que muda na traseira.
"""
import os

exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sedan_forma.py'), encoding='utf-8').read(), 'sedan_forma.py', 'exec'))

TIPO = 'hatch'
Z_PISO_TRAS = -1.40
ZR = -2.00                    # traseira da carroceria
ZBL = -1.86                   # base do vidro traseiro (na tampa)
Z_BOCAL = -1.735
Z_VIDRO_TRAS = -1.42
REC_VIDRO_TRAS = 0.115
Z_CALHA = -1.47
Z_FORRO_TRAS = -1.40
Z_PC_TRAS = -1.71
LANTERNA = (0.632, 0.772, 0.640, 0.945)   # lanternas em pé nas quinas, fora da tampa
X_TAMPA = 0.62                            # meia largura da tampa traseira
TAMPA = (-1.335, 80)
ITEM_TAMPA = 'tampa_traseira_hatch'
SUFIXO_TRAS = '_hatch'                    # portas traseiras próprias (a janela de trás é mais alta)
VIDRO_TRAS = ((0, 1.17, -1.62), (58, 0, 0), 'vidro_traseiro_hatch')
ESTEPE = (0.36, -1.685)


def yt(z):  # linha de cintura até a traseira; na frente é igual ao sedã
    return _i(z, [(-2.00, 0.895), (-1.985, 0.94), (-1.95, 0.966), (-1.88, 0.976), (-1.7, 0.978), (-1.2, 0.968), (-0.4, 0.952),
                  (0.3, 0.935), (0.64, 0.925), (0.8, 0.905), (1.2, 0.86), (1.6, 0.81), (1.85, 0.78), (2.0, 0.755), (2.07, 0.73), (2.10, 0.70)])


def yb(z):
    return _i(z, [(-2.00, 0.37), (-1.985, 0.31), (-1.94, 0.255), (-1.84, 0.228), (-1.6, 0.225), (1.65, 0.225), (1.85, 0.25), (2.0, 0.29), (2.10, 0.33)])


def ytop(z):  # teto reto até atrás e o vidro traseiro em pé
    return _i(z, [(-1.86, 0.986), (-1.83, 1.04), (-1.77, 1.13), (-1.68, 1.225), (-1.58, 1.295), (-1.48, 1.343), (-1.36, 1.372),
                  (-1.15, 1.385), (-0.8, 1.383), (-0.5, 1.39), (-0.32, 1.383), (-0.22, 1.365), (-0.08, 1.31), (0.12, 1.225),
                  (0.34, 1.12), (0.52, 1.02), (0.64, 0.93)])


def janela_terceira(borda=0.0):
    """Vidro fixo atrás da porta traseira (termina antes da tampa)."""
    z0 = -1.325 + borda; z1 = -1.585 - borda
    top = [(z, min(Y_TETO_CORTE - 0.035, ytop(z + 0.06) - 0.07) + borda) for z in np.linspace(z0, z1, 30)]
    bot = [(z, yt(z) + 0.012 - borda) for z in np.linspace(z1, z0, 8)]
    return Polygon(top + bot).buffer(0)


def regiao_tampa(g=0.0):
    """Tampa traseira: o teto atrás da dobradiça, a moldura do vidro e a face de trás até acima do para-choque."""
    zh = TAMPA[0]
    pg = Polygon([(zh, 2.2), (zh, 1.26), (-1.78, 0.62), (-2.6, 0.62), (-2.6, 2.2)])
    if g: pg = pg.buffer(g, join_style=2)
    return prisma_zy(pg, -X_TAMPA - g, X_TAMPA + g)
