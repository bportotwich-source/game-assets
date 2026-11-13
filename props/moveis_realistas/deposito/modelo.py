"""Móveis de depósito e escritório no nível realista: estante de aço, caixote de madeira, caixa de papelão e arquivo de aço.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós
que abrem (tampa; aba_esq, aba_dir, aba_frente, aba_tras; gaveta_1..4) são os dos móveis antigos de props/mobilias."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
_torno = q._torno
M = 'forro_'              # madeira clara sem verniz (+ eixo do veio)
A = 'aco_estante'


def _caixa_fechada(x0, x1, y0, y1, z0, z1):
    """Caixa de papelão fechada com fita, para pôr na estante."""
    xm = (x0 + x1) / 2
    return [caixa(x0, x1, y0, y1, z0, z1, 'papelao', 1.5), caixa(xm - 25, xm + 25, y1 - 60, y1 + 0.8, z0 - 0.8, z1 + 0.8, 'fita_parda')]


def estante_metal():
    X, Z, H = 510, 210, 1900
    NIV = (150, 560, 970, 1380, 1790)
    p = []
    for sx in (-1, 1):
        for sz in (-1, 1):                                                  # montantes de cantoneira
            xa, xb = sorted((sx * X, sx * (X - 38)))
            za, zb = sorted((sz * Z, sz * (Z - 38)))
            xe = sorted((sx * X, sx * (X - 2.5)))
            ze = sorted((sz * Z, sz * (Z - 2.5)))
            p.append(caixa(xa, xb, 6, H, ze[0], ze[1], A))
            p.append(caixa(xe[0], xe[1], 6, H, za, zb, A))
            p.append(caixa(xa - 2 if sx < 0 else xa, xb if sx < 0 else xb + 2, 0, 6, za - 2 if sz < 0 else za, zb if sz < 0 else zb + 2, 'borracha'))
            for y in NIV:                                                   # parafusos de cabeça sextavada
                p.append(_torno([(0, 0), (6.5, 0), (6.5, 4), (0, 4.5)], 'zincado', sx * (X - 20), y - 15, sz * Z, n=6, eixo=(0, 0, sz)))
                p.append(_torno([(0, 0), (6.5, 0), (6.5, 4), (0, 4.5)], 'zincado', sx * X, y - 15, sz * (Z - 20), n=6, eixo=(sx, 0, 0)))
    for y in NIV:                                                           # bandejas de chapa dobrada
        p.append(caixa(-X + 3, X - 3, y - 2.5, y, -Z + 3, Z - 3, A))
        for s in (-1, 1):
            za, zb = sorted((s * (Z - 3), s * (Z - 5.5)))
            p.append(caixa(-X + 3, X - 3, y - 32, y, za, zb, A))
            xa, xb = sorted((s * (X - 3), s * (X - 5.5)))
            p.append(caixa(xa, xb, y - 32, y, -Z + 3, Z - 3, A))
    w = 26                                                                  # contraventamento em X atrás
    for s in (-1, 1):
        p.append(frente([(s * (X - 6), 180), (s * (X - 6), 180 + w * 1.3), (-s * (X - 6), 940 + w * 1.3), (-s * (X - 6), 940)][::s], -Z - 2.5 * (1 if s > 0 else 2), -Z - 2.5 * (0 if s > 0 else 1), A))
    parte('estante', p, origem=G(0, 0, 0), grupo='A')
    c = _caixa_fechada(-440, -90, 150, 420, -170, 160) + _caixa_fechada(60, 400, 970, 1200, -160, 150) + _caixa_fechada(-380, -120, 1380, 1560, -150, 120)
    c.append(_torno([(0, 0), (82, 0), (84, 4), (82, 8), (82, 180), (86, 184), (86, 190), (0, 190)], 'zincado', 250, 560, 10, n=20))          # lata de tinta
    c.append(_torno([(0, 0), (58, 0), (60, 4), (58, 8), (58, 120), (62, 124), (62, 128), (0, 128)], 'zincado', -280, 560, -30, n=18))
    parte('carga', c, origem=G(0, 0, 0), grupo='B')


def _tabuas(x0, x1, y0, y1, z0, z1, n, eixo, mat, folga=8, ch=2.0):
    """n tábuas lado a lado ao longo de `eixo` ('x', 'y' ou 'z'), com folga entre elas."""
    lim = {'x': (x0, x1), 'y': (y0, y1), 'z': (z0, z1)}
    a, b = lim[eixo]
    passo = (b - a + folga) / n
    p = []
    for k in range(n):
        lim[eixo] = (a + k * passo, a + (k + 1) * passo - folga)
        p.append(caixa(*lim['x'], *lim['y'], *lim['z'], mat, ch))
    return p


def caixa_madeira():
    X, Z0, Z1, YB, YT = 422, -322, 322, 45, 520
    E = 20                                                                  # espessura das tábuas
    p = []
    for s in (-1, 1):                                                       # sarrafos de baixo (patins)
        xa, xb = sorted((s * (X - 30), s * (X - 110)))
        p.append(caixa(xa, xb, 0, YB, Z0, Z1, M + 'z', 3.0))
    p += _tabuas(-X + 4, X - 4, YB, YB + E, Z0 + 4, Z1 - 4, 5, 'z', M + 'x')                       # fundo
    for s in (-1, 1):
        za, zb = sorted((s * Z1, s * (Z1 - E)))
        p += _tabuas(-X, X, YB + E + 4, YT, za, zb, 4, 'y', M + 'x')                               # frente e fundo
        xa, xb = sorted((s * X, s * (X - E)))
        p += _tabuas(xa, xb, YB + E + 4, YT, Z0 + E + 2, Z1 - E - 2, 4, 'y', M + 'z')              # lados
        for t in (-1, 1):                                                                          # cantoneiras por dentro
            xa, xb = sorted((s * (X - E), s * (X - E - 45)))
            za, zb = sorted((t * (Z1 - E), t * (Z1 - E - 45)))
            p.append(caixa(xa, xb, YB + E, YT - 6, za, zb, M + 'y', 2.0))
        for y in (YB + E + 60, YT - 60):                                                           # cintas de aço e pregos
            za, zb = sorted((s * Z1, s * (Z1 + 1.5)))
            p.append(caixa(-X - 1.5, X + 1.5, y - 14, y + 14, za, zb, 'aco_estante'))
            xa, xb = sorted((s * X, s * (X + 1.5)))
            p.append(caixa(xa, xb, y - 14, y + 14, Z0, Z1, 'aco_estante'))
        for a in (-1, 1):                                                                          # alças de corda
            pass
    parte('caixote', p, origem=G(0, 0, 0), grupo='A')
    t = _tabuas(-X, X, YT, YT + E, Z0, Z1, 5, 'z', M + 'x', folga=5)
    for x in (-X + 110, 0, X - 110):
        t.append(caixa(x - 45, x + 45, YT + E, YT + E + 22, Z0 + 10, Z1 - 10, M + 'z', 3.0))                # travessas da tampa
    for x in (-X + 110, X - 110):                                                                  # dobradiças de tira
        t.append(caixa(x - 16, x + 16, YT - 4, YT + E + 23.5, Z0 - 2, Z0, 'aco_estante'))
        t.append(cil((x - 18, YT, Z0 - 3), (x + 18, YT, Z0 - 3), 5.0, 'aco_estante', n=10))
    parte('tampa', t, origem=G(0, YT, Z0 + 20), grupo='B')


def caixa_papelao():
    X, Z, H, E = 250, 200, 360, 4
    c = caixa(-X, X, 0, H, -Z, Z, 'papelao')
    cut(c, caixa(-X + E, X - E, E, H + 5, -Z + E, Z - E, 'papelao'))
    p = [bevel(c, 1.0)]
    for s in (-1, 1):                                                       # fita que desce pelas pontas
        xa, xb = sorted((s * X, s * (X + 0.8)))
        p.append(caixa(xa, xb, H - 90, H, -24, 24, 'fita_parda'))
        za, zb = sorted((s * Z, s * (Z + 0.8)))
    p.append(caixa(-X + E, X - E, E, E + 3, -Z + E, Z - E, 'papelao'))
    parte('caixa', p, origem=G(0, 0, 0), grupo='A')
    for nome, s in (('aba_esq', -1), ('aba_dir', 1)):                       # abas curtas, por baixo
        xa, xb = sorted((s * X, s * (X - Z)))
        parte(nome, [caixa(xa, xb, H, H + 3, -Z + 1, Z - 1, 'papelao', 0.6)], origem=G(s * X, H, 0), grupo='A')
    for nome, s in (('aba_frente', 1), ('aba_tras', -1)):                   # abas compridas, por cima, com a fita cortada no meio
        za, zb = sorted((s * Z, s * 1.0))
        fa, fb = sorted((s * 1.0, s * 26))
        parte(nome, [caixa(-X + 1, X - 1, H + 3, H + 6, za, zb, 'papelao', 0.6), caixa(-X, X, H + 6, H + 6.8, fa, fb, 'fita_parda')],
              origem=G(0, H + 3, s * Z), grupo='A')


def arquivo_aco():
    X, Z0, ZF, H = 235, -310, 300, 1330
    AC = 'aco_arquivo'
    c = bevel(caixa(-X, X, 30, H, Z0, ZF, AC), 3.0, seg=2)
    vaos = [60 + k * 312 for k in range(4)][::-1]                           # gaveta_1 é a de cima
    for y0 in vaos:
        cut(c, caixa(-X + 18, X - 18, y0, y0 + 296, Z0 + 18, ZF + 5, AC))
    p = [c, caixa(-X + 6, X - 6, 0, 30, Z0 + 10, ZF - 30, 'borracha', 2.0)]
    p.append(_torno([(0, 0), (9, 0), (9, 3), (6, 5), (0, 5)], 'inox', X - 40, H - 22, ZF, n=12, eixo=(0, 0, 1)))                         # fechadura
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    rnd = random.Random(5)
    for k, y0 in enumerate(vaos):
        g = [bevel(caixa(-X + 5, X - 5, y0 - 5, y0 + 301, ZF, ZF + 20, AC), 3.0, seg=2),
             caixa(-X + 24, X - 24, y0 + 8, y0 + 11, Z0 + 40, ZF, 'zincado'),
             caixa(-X + 24, X - 24, y0 + 11, y0 + 220, Z0 + 40, Z0 + 42.5, 'zincado')]
        for s in (-1, 1):
            xa, xb = sorted((s * (X - 24), s * (X - 26.5)))
            g.append(caixa(xa, xb, y0 + 11, y0 + 220, Z0 + 40, ZF, 'zincado'))
        g.append(cil((-75, y0 + 215, ZF + 33), (75, y0 + 215, ZF + 33), 6.0, 'inox', n=10))                                                # puxador
        for s in (-1, 1):
            g.append(cil((s * 60, y0 + 215, ZF + 20), (s * 60, y0 + 215, ZF + 33), 4.5, 'inox', n=8))
        fr = caixa(-52, 52, y0 + 100, y0 + 150, ZF + 20, ZF + 22, 'inox')                                                                  # porta-etiqueta
        cut(fr, caixa(-46, 46, y0 + 106, y0 + 152, ZF + 20.6, ZF + 25, 'inox'))
        g += [fr, caixa(-45, 45, y0 + 107, y0 + 146, ZF + 20, ZF + 21, 'papel')]
        z = Z0 + 70                                                                                                                       # pastas suspensas
        while z < ZF - 60:
            h = rnd.uniform(215, 245)
            g.append(caixa(-X + 34, X - 34, y0 + 20, y0 + h, z, z + rnd.uniform(4, 14), 'papelao' if rnd.random() < 0.5 else 'papel'))
            tx = rnd.uniform(-150, 90)
            g.append(caixa(tx, tx + 60, y0 + h, y0 + h + 14, z, z + 1.5, 'papel'))
            z += rnd.uniform(28, 70)
        parte(f'gaveta_{k + 1}', g, origem=G(0, 0, 0), grupo='B')


FORMAS = {'estante_metal': estante_metal, 'caixa_madeira': caixa_madeira, 'caixa_papelao': caixa_papelao, 'arquivo_aco': arquivo_aco}
