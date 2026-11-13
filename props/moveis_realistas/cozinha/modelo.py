"""Móveis de cozinha no nível realista: balcão com pia e armário aéreo.

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


FORMAS = {'balcao_pia': balcao_pia, 'armario_aereo': armario_aereo}
