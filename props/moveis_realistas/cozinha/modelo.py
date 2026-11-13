"""Móveis de cozinha no nível realista: balcão com pia, armário aéreo, geladeira duplex e fogão de 4 bocas.

Armários de madeira pintada de creme, de porta de moldura com almofada rebaixada, tampo de granito escuro com cuba de
inox e torneira de bica alta. Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente.
As medidas de fora, os nós e as dobradiças das portas são os dos móveis antigos de props/mobilias."""
import math, os, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
_torno, _fio = q._torno, q._fio
T = 'tinta_creme'


def _porta(xa, xb, y0, y1, z0, pux_x, esp=20, mont=62):
    """Porta de moldura com almofada rebaixada, puxador de alça em pé e duas dobradiças aparentes do lado oposto ao puxador."""
    p = [caixa(xa, xa + mont, y0, y1, z0, z0 + esp, T, 1.6), caixa(xb - mont, xb, y0, y1, z0, z0 + esp, T, 1.6),
         caixa(xa + mont, xb - mont, y0, y0 + mont, z0, z0 + esp, T, 1.6), caixa(xa + mont, xb - mont, y1 - mont, y1, z0, z0 + esp, T, 1.6),
         caixa(xa + mont - 4, xb - mont + 4, y0 + mont - 4, y1 - mont + 4, z0 + 3, z0 + 10, T)]
    ym = (y0 + y1) / 2
    zf = z0 + esp
    p.append(cil((pux_x, ym - 55, zf + 20), (pux_x, ym + 55, zf + 20), 5.0, 'inox', n=12))                  # alça
    for d in (-42, 42):
        p.append(cil((pux_x, ym + d, zf), (pux_x, ym + d, zf + 20), 4.0, 'inox', n=10))
        p.append(_torno([(0, 0), (8, 0), (7, 2), (0, 2.5)], 'inox', pux_x, ym + d, zf, n=12, eixo=(0, 0, 1)))
    xd = xa if abs(pux_x - xa) > abs(pux_x - xb) else xb                                                    # lado da dobradiça
    for y in (y0 + 90, y1 - 90):
        p.append(cil((xd, y - 26, zf), (xd, y + 26, zf), 4.5, 'zincado', n=10))
    return p


def _carcaca(X, y0, y1, z0, z1, prat=(), e=18):
    """Caixa do armário aberta na frente, com as prateleiras e o montante do meio."""
    c = caixa(-X, X, y0, y1, z0, z1, T)
    cut(c, caixa(-X + e, X - e, y0 + e, y1 - e, z0 + 6, z1 + 5, T))
    p = [bevel(c, 1.2)]
    for y in prat:
        p.append(caixa(-X + e, X - e, y - e / 2, y + e / 2, z0 + 6, z1 - 30, T, 1.0))
    p.append(caixa(-22, 22, y0 + e, y1 - e, z1 - 20, z1, T, 1.0))
    return p


def balcao_pia():
    X, Z0, ZC, YR, YT = 600, -300, 269, 100, 850          # meia largura, fundo, face da carcaça, topo do rodapé, topo da carcaça
    p = _carcaca(X, YR, YT, Z0, ZC, prat=(470,))
    p.append(caixa(-X + 10, X - 10, 0, YR, Z0 + 10, ZC - 55, T, 1.5))                                     # rodapé recuado
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    # tampo de granito com a cuba de inox encaixada e o frontão atrás
    CX0, CX1, CZ0, CZ1 = 90, 520, -190, 215
    t = caixa(-X - 10, X + 10, YT, YT + 40, Z0, ZC + 57, 'pedra_pia')
    cut(t, caixa(CX0, CX1, YT - 5, YT + 45, CZ0, CZ1, 'pedra_pia'))
    tp = [bevel(t, 3.0), caixa(-X - 10, X + 10, YT + 40, YT + 110, Z0, Z0 + 22, 'pedra_pia', 3.0)]
    cuba = caixa(CX0 - 4, CX1 + 4, YT - 150, YT + 42, CZ0 - 4, CZ1 + 4, 'inox')
    cut(cuba, bevel(caixa(CX0 + 2, CX1 - 2, YT - 148, YT + 60, CZ0 + 2, CZ1 - 2, 'inox'), 28.0, seg=4, ang=80))
    tp.append(cuba)
    aba = caixa(CX0 - 14, CX1 + 14, YT + 40, YT + 43, CZ0 - 14, CZ1 + 14, 'inox')                           # aba da cuba sobre a pedra
    cut(aba, caixa(CX0 + 2, CX1 - 2, YT + 30, YT + 50, CZ0 + 2, CZ1 - 2, 'inox'))
    tp.append(aba)
    cx, cz = (CX0 + CX1) / 2, (CZ0 + CZ1) / 2
    tp.append(_torno([(0, 0), (38, 0), (38, 2), (30, 3.5), (0, 3.5)], 'inox', cx, YT - 148, cz, n=18))      # válvula do ralo
    tp.append(_torno([(0, 0), (24, 0), (24, 1.2), (0, 1.2)], 'ralo', cx, YT - 144.5, cz, n=14))
    parte('tampo', tp, origem=G(0, 0, 0), grupo='A')
    # torneira de bica alta e os dois registros
    tx, tz, yb = cx, Z0 + 62, YT + 40
    tn = [_torno([(0, 0), (26, 0), (26, 4), (18, 8), (15, 30), (13, 34), (0, 34)], 'inox', tx, yb, tz, n=18)]
    arco = [(tx, yb + 30, tz), (tx, yb + 230, tz)]
    for k in range(1, 10):
        a = math.radians(180 - k * 20)
        arco.append((tx, yb + 230 + 58 * math.sin(a) * 1.0, tz + 70 + 70 * math.cos(a)))
    arco.append((tx, yb + 195, tz + 140))
    tn.append(_fio(arco, 11.0, 'inox', res=3))
    tn.append(_torno([(0, 0), (13, 0), (13, 14), (11, 16), (0, 16)], 'inox', tx, yb + 181, tz + 140, n=14))  # arejador
    for s in (-1, 1):
        x = tx + s * 95
        tn.append(_torno([(0, 0), (20, 0), (20, 4), (13, 8), (12, 40), (16, 44), (16, 52), (0, 52)], 'inox', x, yb, tz, n=16))
        for g in (0, 90):
            dx, dz = 26 * math.cos(math.radians(g + 20 * s)), 26 * math.sin(math.radians(g + 20 * s))
            tn.append(cil((x - dx, yb + 58, tz - dz), (x + dx, yb + 58, tz + dz), 5.0, 'inox', n=10))
        tn.append(_torno([(0, 0), (9, 0), (7, 5), (0, 6)], 'inox', x, yb + 60, tz, n=12))
    parte('torneira', tn, origem=G(0, 0, 0), grupo='A')
    for nome, lado in (('porta_esq', -1), ('porta_dir', 1)):
        xa, xb = sorted((lado * (X - 2), lado * 2))
        parte(nome, _porta(xa, xb, YR + 6, YT - 6, ZC, lado * 40), origem=G(lado * X, 0, ZC + 20), grupo='B')


def armario_aereo():
    X, Z0, ZC, H = 400, -20, 310, 630
    p = _carcaca(X, 0, H - 6, Z0, ZC, prat=(315,))
    p.append(caixa(-X - 10, X + 10, H - 30, H, Z0, ZC + 24, T, 4.0))                                       # cimalha
    p.append(caixa(-X + 6, X - 6, -12, 4, ZC - 30, ZC - 8, T, 2.0))                                        # régua de baixo
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    for nome, lado in (('porta_esq', -1), ('porta_dir', 1)):
        xa, xb = sorted((lado * (X - 2), lado * 2))
        parte(nome, _porta(xa, xb, 4, H - 34, ZC, lado * 38, mont=56), origem=G(lado * X, 0, ZC + 20), grupo='B')


# ------------------------------------------------------------------ geladeira e fogão
E = 'esmalte_cozinha'


def _grade(x0, x1, y, z0, z1, n=9, mat='zincado', r=3.0):
    """Prateleira de arame: moldura e varetas da frente para o fundo."""
    p = [cil((x0, y, z0), (x1, y, z0), r * 1.3, mat, n=6), cil((x0, y, z1), (x1, y, z1), r * 1.3, mat, n=6),
         cil((x0, y, z0), (x0, y, z1), r * 1.3, mat, n=6), cil((x1, y, z0), (x1, y, z1), r * 1.3, mat, n=6)]
    for k in range(1, n + 1):
        x = x0 + (x1 - x0) * k / (n + 1)
        p.append(cil((x, y, z0), (x, y, z1), r, mat, n=5))
    return p


def _dentro(c, mat, X, z0, zf, borda):
    """Pinta com `mat` as faces de dentro de um vão aberto na frente."""
    lib.pintar(c, mat, lambda q, n: abs(q[2]) < X - borda + 1 and -zf + 1 < q[0] < -z0 - 1)
    return c


def _porta_gel(X, y0, y1, zf, pux, prat):
    """Porta de geladeira: casca esmaltada de quina redonda, forro de plástico com prateleiras, borracha e puxador em pé."""
    p = [bevel(caixa(-X, X, y0, y1, zf, zf + 45, E), 14.0, seg=3)]
    p.append(caixa(-X + 44, X - 44, y0 + 34, y1 - 34, zf - 16, zf, 'liner', 3.0))
    for xa, xb, ya, yb in ((-X + 12, X - 12, y0 + 10, y0 + 30), (-X + 12, X - 12, y1 - 30, y1 - 10), (-X + 12, -X + 32, y0 + 30, y1 - 30), (X - 32, X - 12, y0 + 30, y1 - 30)):
        p.append(caixa(xa, xb, ya, yb, zf - 5, zf, 'borracha', 1.5))                                       # borracha de vedação
    for y in prat:                                                                                          # prateleiras da porta
        p.append(caixa(-X + 50, X - 50, y, y + 5, zf - 78, zf - 16, 'liner'))
        p.append(caixa(-X + 50, X - 50, y, y + 52, zf - 78, zf - 74, 'liner', 1.0))
        for s in (-1, 1):
            p.append(caixa(min(s * (X - 50), s * (X - 54)), max(s * (X - 50), s * (X - 54)), y, y + 52, zf - 78, zf - 16, 'liner'))
    ya, yb = pux
    x = -X + 46
    p.append(cil((x, ya, zf + 62), (x, yb, zf + 62), 8.0, 'inox', n=12))
    for y in (ya + 26, yb - 26):
        p.append(cil((x, y, zf + 43), (x, y, zf + 62), 6.0, 'inox', n=10))
    return p


def geladeira():
    X, Z0, ZF, H = 350, -318, 325, 1762
    YD = 1290                                              # divisão entre a geladeira e o freezer
    c = bevel(caixa(-X, X, 30, H, Z0, ZF, E), 18.0, seg=3)
    cut(c, caixa(-X + 40, X - 40, 80, YD - 40, Z0 + 50, ZF + 5, E))
    cut(c, caixa(-X + 40, X - 40, YD + 30, H - 40, Z0 + 50, ZF + 5, E))
    p = [_dentro(c, 'liner', X, Z0 + 50, ZF, 40)]
    for s in (-1, 1):
        for z in (Z0 + 60, ZF - 60):
            p.append(_torno([(0, 0), (20, 0), (22, 6), (22, 32), (0, 32)], 'borracha', s * (X - 50), 0, z, n=12))
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    d = []
    for y in (560, 790, 1020):
        d += _grade(-X + 44, X - 44, y, Z0 + 56, ZF - 96, n=11)
    d += _grade(-X + 44, X - 44, YD + 190, Z0 + 56, ZF - 96, n=11)
    d.append(caixa(-X + 42, X - 42, 322, 328, Z0 + 54, ZF - 92, 'liner'))                                  # tampa da gaveta de legumes
    g = caixa(-X + 50, X - 50, 90, 316, Z0 + 70, ZF - 96, 'liner')
    cut(g, caixa(-X + 54, X - 54, 94, 330, Z0 + 74, ZF - 100, 'liner'))
    d.append(g)
    d.append(caixa(-70, 70, 250, 268, ZF - 96, ZF - 84, 'liner', 3.0))                                     # pega da gaveta
    d.append(caixa(X - 130, X - 42, YD - 110, YD - 44, Z0 + 120, Z0 + 260, 'liner', 4.0))                  # caixa do termostato e da lâmpada
    d.append(_torno([(0, 0), (16, 0), (16, 6), (12, 9), (0, 9)], 'baquelite', X - 86, YD - 77, Z0 + 260, n=12, eixo=(0, 0, 1)))
    parte('dentro', d, origem=G(0, 0, 0), grupo='A')
    pg = _porta_gel(X, 40, YD - 6, ZF, (820, 1180), (150, 480, 800))
    parte('porta_geladeira', pg, origem=G(X, 0, ZF), grupo='B')
    pf = _porta_gel(X, YD + 4, H - 4, ZF, (YD + 40, YD + 260), (YD + 120,))
    pf.append(caixa(X - 190, X - 70, H - 90, H - 66, ZF + 45, ZF + 47.5, 'inox', 0.8))                     # plaqueta da marca
    parte('porta_freezer', pf, origem=G(X, 0, ZF), grupo='B')


def fogao():
    X, Z0, ZF, YT = 280, -290, 300, 850
    c = bevel(caixa(-X, X, 35, YT, Z0, ZF, E), 4.0, seg=2)
    cut(c, caixa(-X + 35, X - 35, 190, 680, Z0 + 40, ZF + 5, E))
    cut(c, caixa(-X + 20, X - 20, 50, 168, Z0 + 30, ZF + 5, E))
    p = [_dentro(c, 'esmalte_forno', X, Z0 + 30, ZF, 20)]
    p.append(bevel(caixa(-X, X, YT, 980, Z0, Z0 + 26, E), 5.0, seg=2))                                     # espelho de trás
    for s in (-1, 1):
        for z in (Z0 + 50, ZF - 50):
            p.append(_torno([(0, 0), (18, 0), (20, 5), (20, 37), (0, 37)], 'borracha', s * (X - 45), 0, z, n=12))
    for k in range(5):                                                                                      # botões: 4 bocas e o forno
        x = -200 + 100 * k
        p.append(_torno([(0, 0), (23, 0), (23, 4), (17, 8), (15, 24), (11, 27), (0, 27)], 'baquelite', x, 752, ZF, n=16, eixo=(0, 0, 1)))
        p.append(caixa(x - 2.5, x + 2.5, 752, 772, ZF + 24, ZF + 30, 'baquelite', 1.0))
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    # mesa de inox com as quatro bocas e as grades de ferro
    m = [bevel(caixa(-X, X, YT, YT + 16, Z0 + 26, ZF + 8, 'inox'), 3.0, seg=2)]
    yb = YT + 16
    for cx in (-135, 135):
        for cz, r in ((-140, 1.0), (130, 0.82)):
            m.append(_torno([(0, 0), (62 * r, 0), (60 * r, 3), (46 * r, 3), (44 * r, 9), (0, 9)], 'esmalte_forno', cx, yb, cz, n=20))       # bacia
            m.append(_torno([(0, 9), (36 * r, 9), (38 * r, 13), (38 * r, 18), (30 * r, 21), (0, 21)], 'ferro_grade', cx, yb, cz, n=20))    # queimador e tampa
            a = 96
            for s in (-1, 1):                                                                               # grade: moldura e quatro dedos
                m.append(caixa(cx - a, cx + a, yb + 22, yb + 30, cz + s * a - 4, cz + s * a + 4, 'ferro_grade', 1.2))
                m.append(caixa(cx + s * a - 4, cx + s * a + 4, yb + 22, yb + 30, cz - a, cz + a, 'ferro_grade', 1.2))
                m.append(caixa(min(cx + s * a, cx + s * 30), max(cx + s * a, cx + s * 30), yb + 22, yb + 30, cz - 4, cz + 4, 'ferro_grade', 1.2))
                m.append(caixa(cx - 4, cx + 4, yb + 22, yb + 30, min(cz + s * a, cz + s * 30), max(cz + s * a, cz + s * 30), 'ferro_grade', 1.2))
                for t in (-1, 1):
                    m.append(caixa(cx + s * a - 5, cx + s * a + 5, yb, yb + 22, cz + t * a - 5, cz + t * a + 5, 'ferro_grade'))
    parte('mesa', m, origem=G(0, 0, 0), grupo='A')
    f = _grade(-X + 38, X - 38, 420, Z0 + 46, ZF - 12, n=13)
    f.append(caixa(-X + 60, X - 60, 196, 204, Z0 + 70, ZF - 40, 'esmalte_forno', 2.0))                     # chapa do fundo do forno
    parte('forno', f, origem=G(0, 0, 0), grupo='A')
    # porta do forno: abre para baixo, com visor de vidro escuro
    d = [bevel(caixa(-X + 6, X - 6, 176, 692, ZF, ZF + 28, E), 5.0, seg=2),
         caixa(-X + 40, X - 40, 196, 674, ZF - 6, ZF, 'esmalte_forno', 1.5),
         caixa(-178, 178, 292, 572, ZF + 27, ZF + 30, 'inox', 1.0),
         caixa(-166, 166, 304, 560, ZF + 29, ZF + 31.5, 'vidro_forno', 0.8),
         cil((-200, 640, ZF + 56), (200, 640, ZF + 56), 8.0, 'inox', n=12)]
    for s in (-1, 1):
        d.append(cil((s * 175, 640, ZF + 28), (s * 175, 640, ZF + 56), 6.0, 'inox', n=10))
    parte('porta_forno', d, origem=G(0, 170, ZF), grupo='B')
    # gaveta de panelas embaixo
    g = [bevel(caixa(-X + 6, X - 6, 44, 170, ZF, ZF + 24, E), 4.0, seg=2),
         caixa(-X + 26, X - 26, 56, 60, Z0 + 50, ZF, 'zincado'),
         caixa(-X + 26, X - 26, 60, 150, Z0 + 50, Z0 + 53, 'zincado'),
         cil((-150, 138, ZF + 44), (150, 138, ZF + 44), 6.0, 'inox', n=10)]
    for s in (-1, 1):
        g.append(caixa(min(s * (X - 26), s * (X - 29)), max(s * (X - 26), s * (X - 29)), 60, 150, Z0 + 50, ZF, 'zincado'))
        g.append(cil((s * 130, 138, ZF + 24), (s * 130, 138, ZF + 44), 4.5, 'inox', n=8))
    parte('gaveta', g, origem=G(0, 0, 0), grupo='B')


FORMAS = {'balcao_pia': balcao_pia, 'armario_aereo': armario_aereo, 'geladeira': geladeira, 'fogao': fogao}
