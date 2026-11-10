"""Geometria da amostra: 4 m de fachada do bangalô (janela + porta), canto de sala, cômoda e dois itens.
Mesmas medidas e pivôs das peças atuais do kit 7 (módulo de 2 m, parede de 0,3 m, piso a 0,45 m do chão)."""
import math, random
from lib import *

rnd = random.Random(7)
H = 3.03; T = 0.3; RAISE = 0.45; WT = 0.12; FRIEZE = 2.72


def prof_x(pts, x0, x1, mat):
    return extr(pts, x0, x1, mat, 'zy')


def tb(x0, x1, y0, y1, z0, z1, mat, eixo):
    return veio(box(x0, x1, y0, y1, z0, z1, mat), eixo)


# ------------------------------------------------------------------ fachada
def tabuas(x0, x1, furo=None):
    """13 fiadas de tábuas sobrepostas (cunha), cada fiada emendada num ponto diferente."""
    out = []
    expo = (FRIEZE - WT) / 13
    for i in range(13):
        yb = WT + i * expo; yt = yb + expo + 0.03
        xj = rnd.uniform(x0 + 0.35, x1 - 0.35)
        for (a, b) in ((x0, xj - 0.0012), (xj + 0.0012, x1)):
            dz = rnd.uniform(-0.0012, 0.0012) if (a > x0 and b < x1) else 0.0
            dz = rnd.uniform(0.0, 0.0015) if a > x0 + 0.01 else 0.0
            o = prof_x([(0.0, yb), (0.024 + dz, yb), (0.0245 + dz, yb + 0.004), (0.008, yt), (0.0, yt)], a, b, 'tabua')
            if furo and not (furo[1] <= a or furo[0] >= b or furo[3] <= yb or furo[2] >= yt):
                if furo[0] <= a and furo[1] >= b and furo[2] <= yb and furo[3] >= yt:
                    bpy.data.objects.remove(o); continue
                cut(o, box(furo[0], furo[1], furo[2], furo[3], -0.05, 0.1, 'tabua'))
            out.append(veio(o, 'x'))
    return out


def rodape_ext(x0, x1):
    return veio(prof_x([(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)], x0, x1, 'guarn'), 'x')


def friso(x0, x1):
    return [veio(prof_x([(0.0, FRIEZE), (0.034, FRIEZE), (0.034, 3.0), (0.0, 3.0)], x0, x1, 'guarn'), 'x'),
            veio(prof_x([(0.0, FRIEZE - 0.05), (0.03, FRIEZE - 0.035), (0.042, FRIEZE - 0.012), (0.042, FRIEZE + 0.02), (0.0, FRIEZE + 0.02)], x0, x1, 'guarn'), 'x')]


def rodape_int(x0, x1):
    zi = -T
    return [veio(prof_x([(zi, 0.0), (zi - 0.018, 0.0), (zi - 0.018, 0.105), (zi - 0.014, 0.122), (zi - 0.008, 0.130), (zi - 0.008, 0.138), (zi, 0.142)], x0, x1, 'rodape'), 'x'),
            veio(prof_x([(zi - 0.018, 0.0), (zi - 0.032, 0.0), (zi - 0.032, 0.006), (zi - 0.027, 0.015), (zi - 0.018, 0.02)], x0, x1, 'rodape'), 'x')]


def nucleo(x0, x1, furo):
    core = box(x0, x1, 0.0, H, -T, 0.0, 'reboco')
    cut(core, box(furo[0], furo[1], furo[2], furo[3], -0.5, 0.2, 'reboco'))
    apagar(core, lambda c, n: n[2] > 0.9)
    base = box(x0, x1, -RAISE, 0.0, -T, 0.0, 'tijolo')
    apagar(base, lambda c, n: n[1] > 0.9 or n[2] < -0.9)
    return [core, base]


def caixilho(x0, x1, y0, y1, z0, z1, barras=0, trav_baixo=0.07, trav_cima=0.05):
    """Folha de guilhotina: montantes inteiros, travessas entre eles, vidro e baguetes."""
    s = 0.05
    L = [tb(x0, x0 + s, y0, y1, z0, z1, 'guarn', 'y'), tb(x1 - s, x1, y0, y1, z0, z1, 'guarn', 'y'),
         tb(x0 + s, x1 - s, y0, y0 + trav_baixo, z0, z1, 'guarn', 'x'), tb(x0 + s, x1 - s, y1 - trav_cima, y1, z0, z1, 'guarn', 'x')]
    zm = (z0 + z1) / 2
    for i in range(barras):
        xb = x0 + s + (x1 - x0 - 2 * s) * (i + 1) / (barras + 1)
        L.append(tb(xb - 0.011, xb + 0.011, y0 + trav_baixo, y1 - trav_cima, z0 + 0.005, z1 - 0.005, 'guarn', 'y'))
    L.append(box(x0 + s - 0.004, x1 - s + 0.004, y0 + trav_baixo - 0.004, y1 - trav_cima + 0.004, zm - 0.002, zm + 0.002, 'vidro'))
    return L


def parede_janela(ox):
    x0, x1 = ox - 1, ox + 1
    a0, a1, y0, y1 = ox - 0.55, ox + 0.55, 0.8, 2.3
    L = nucleo(x0, x1, (a0, a1, y0, y1))
    L += tabuas(x0, x1, (a0 - 0.115, a1 + 0.115, y0 - 0.1, y1 + 0.16))
    L += [rodape_ext(x0, x1)] + friso(x0, x1) + rodape_int(x0, x1)
    g = 'guarn'
    # marco: ombreiras, verga e peitoril inclinado com nariz e pingadeira
    L += [tb(a0, a0 + 0.035, y0 + 0.02, y1, -0.16, 0.0, g, 'y'), tb(a1 - 0.035, a1, y0 + 0.02, y1, -0.16, 0.0, g, 'y'),
          tb(a0 + 0.035, a1 - 0.035, y1 - 0.035, y1, -0.16, 0.0, g, 'x')]
    L.append(veio(prof_x([(-0.16, y0 + 0.045), (0.0, y0 + 0.029), (0.0, y0), (-0.16, y0)], a0, a1, g), 'x'))
    L.append(veio(prof_x([(0.0, y0 + 0.029), (0.072, y0 + 0.021), (0.072, y0 - 0.012), (0.05, y0 - 0.012), (0.046, y0 - 0.004), (0.0, y0 - 0.004)], a0 - 0.135, a1 + 0.135, g), 'x'))
    # guarnição externa: laterais, avental, verga larga com capa (craftsman)
    L += [tb(a0 - 0.115, a0 + 0.008, y0 + 0.022, y1 + 0.02, 0.0, 0.03, g, 'y'), tb(a1 - 0.008, a1 + 0.115, y0 + 0.022, y1 + 0.02, 0.0, 0.03, g, 'y'),
          tb(a0 - 0.1, a1 + 0.1, y0 - 0.1, y0 - 0.004, 0.0, 0.026, g, 'x'),
          tb(a0 - 0.135, a1 + 0.135, y1 + 0.02, y1 + 0.145, 0.0, 0.036, g, 'x')]
    L.append(veio(prof_x([(0.0, y1 + 0.145), (0.06, y1 + 0.145), (0.06, y1 + 0.157), (0.045, y1 + 0.174), (0.0, y1 + 0.186)], a0 - 0.155, a1 + 0.155, g), 'x'))
    # batentes: externo, de separação e interno
    for (za, zb, pr) in ((-0.015, 0.0, 0.016), (-0.055, -0.05, 0.012), (-0.108, -0.09, 0.014)):
        L += [tb(a0 + 0.035, a0 + 0.035 + pr, y0 + 0.04, y1 - 0.035, za, zb, g, 'y'), tb(a1 - 0.035 - pr, a1 - 0.035, y0 + 0.04, y1 - 0.035, za, zb, g, 'y')]
    L.append(tb(a0 + 0.035, a1 - 0.035, y1 - 0.05, y1 - 0.035, -0.015, 0.0, g, 'x'))
    s0, s1 = a0 + 0.037, a1 - 0.037
    # folha de cima (fixa, por fora), 3 vidros
    L += caixilho(s0, s1, 1.535, y1 - 0.037, -0.05, -0.015, barras=2, trav_baixo=0.04)
    # guarnição interna: forro do vão, peitoril interno com orelhas, avental, guarnições
    r = 'rodape'; zi = -T
    L += [tb(a0, a0 + 0.018, y0 + 0.03, y1, zi, -0.16, r, 'y'), tb(a1 - 0.018, a1, y0 + 0.03, y1, zi, -0.16, r, 'y'), tb(a0 + 0.018, a1 - 0.018, y1 - 0.018, y1, zi, -0.16, r, 'x')]
    st = tb(a0 - 0.125, a1 + 0.125, y0 + 0.012, y0 + 0.045, zi - 0.05, zi, r, 'x'); bevel(st, 0.008, 3, 60)
    L += [st, tb(a0 + 0.018, a1 - 0.018, y0 + 0.012, y0 + 0.045, zi, -0.108, r, 'x'),
          tb(a0 - 0.095, a1 + 0.095, y0 - 0.085, y0 + 0.012, zi - 0.016, zi, r, 'x'),
          tb(a0 - 0.095, a0 + 0.006, y0 + 0.045, y1 - 0.006, zi - 0.02, zi, r, 'y'), tb(a1 - 0.006, a1 + 0.095, y0 + 0.045, y1 - 0.006, zi - 0.02, zi, r, 'y'),
          tb(a0 - 0.115, a1 + 0.115, y1 - 0.006, y1 + 0.115, zi - 0.024, zi, r, 'x')]
    L.append(veio(prof_x([(zi, y1 + 0.115), (zi - 0.04, y1 + 0.115), (zi - 0.04, y1 + 0.125), (zi - 0.03, y1 + 0.138), (zi, y1 + 0.145)], a0 - 0.13, a1 + 0.13, r), 'x'))
    p = parte('parede_janela', L, origem=(ox, 0, 0), grupo='A')
    # folha de baixo (sobe), fecho e puxadores
    F = caixilho(s0, s1, y0 + 0.045, 1.575, -0.09, -0.055, barras=0, trav_baixo=0.075, trav_cima=0.04)
    ym = 1.575
    F += [box(ox - 0.03, ox + 0.03, ym, ym + 0.004, -0.088, -0.058, 'latao'), cyl((ox, ym + 0.004, -0.073), (ox, ym + 0.013, -0.073), 0.011, 'latao', n=20),
          box(ox - 0.006, ox + 0.034, ym + 0.013, ym + 0.017, -0.079, -0.067, 'latao'), cyl((ox + 0.034, ym + 0.013, -0.073), (ox + 0.034, ym + 0.024, -0.073), 0.006, 'latao', n=14)]
    for xs in (-0.3, 0.3):
        F += [box(ox + xs - 0.035, ox + xs + 0.035, y0 + 0.065, y0 + 0.095, -0.0925, -0.09, 'latao'),
              prof_x([(-0.0925, y0 + 0.07), (-0.106, y0 + 0.07), (-0.108, y0 + 0.078), (-0.0925, y0 + 0.084)], ox + xs - 0.022, ox + xs + 0.022, 'latao')]
    parte('janela_folha', F, origem=(ox, y0 + 0.045, -0.0725), pai=p, grupo='C', extra={'desliza_y': 0.66})
    return p


def porta_frente(ox, pai):
    d0, d1, y0, y1, z0, z1 = ox - 0.457, ox + 0.457, 0.022, 2.255, -0.2, -0.155
    st = 0.115; mu = 0.058
    lw = (d1 - d0 - 2 * st - 2 * mu) / 3
    pw = (d1 - d0 - 2 * st - mu) / 2
    a, b = d0 + st, d1 - st
    p_ = 'porta'
    # montantes inteiros e travessas entre eles, como numa porta de verdade (as emendas aparecem na tinta)
    L = [tb(d0, a, y0, y1, z0, z1, p_, 'y'), tb(b, d1, y0, y1, z0, z1, p_, 'y'),
         tb(a, b, y0, 0.24, z0, z1, p_, 'x'), tb(a, b, 0.95, 1.09, z0, z1, p_, 'x'), tb(a, b, 1.50, 1.62, z0, z1, p_, 'x'), tb(a, b, 2.12, y1, z0, z1, p_, 'x'),
         tb(a + pw, b - pw, 0.24, 0.95, z0, z1, p_, 'y')]
    for i in range(2):
        xm = a + lw + i * (lw + mu)
        L.append(tb(xm, xm + mu, 1.62, 2.12, z0, z1, p_, 'y'))
    zm = (z0 + z1) / 2
    for (pa, pb, pc, pe) in ((a, a + pw, 0.24, 0.95), (b - pw, b, 0.24, 0.95), (a, b, 1.09, 1.50)):
        L.append(tb(pa - 0.006, pb + 0.006, pc - 0.006, pe + 0.006, zm - 0.0105, zm + 0.0105, p_, 'y'))      # almofada
        for (za, zb) in ((z0 + 0.004, zm - 0.0105), (zm + 0.0105, z1 - 0.004)):
            c = box(pa + 0.035, pb - 0.035, pc + 0.035, pe - 0.035, za, zb, p_); bevel(c, 0.006, 1, 40); L.append(veio(c, 'y'))
        for (za, zb) in ((z0 + 0.001, z0 + 0.012), (z1 - 0.012, z1 - 0.001)):                                   # moldura da almofada
            L += [tb(pa, pb, pc, pc + 0.009, za, zb, p_, 'x'), tb(pa, pb, pe - 0.009, pe, za, zb, p_, 'x'),
                  tb(pa, pa + 0.009, pc + 0.009, pe - 0.009, za, zb, p_, 'y'), tb(pb - 0.009, pb, pc + 0.009, pe - 0.009, za, zb, p_, 'y')]
    for i in range(3):
        xa = a + i * (lw + mu)
        L.append(box(xa - 0.004, xa + lw + 0.004, 1.616, 2.124, -0.1795, -0.1755, 'vidro'))
        for (za, zb) in ((z0 + 0.006, zm - 0.004), (zm + 0.004, z1 - 0.006)):                                   # baguetes do vidro
            L += [tb(xa, xa + lw, 1.62, 1.628, za, zb, p_, 'x'), tb(xa, xa + lw, 2.112, 2.12, za, zb, p_, 'x'),
                  tb(xa, xa + 0.008, 1.628, 2.112, za, zb, p_, 'y'), tb(xa + lw - 0.008, xa + lw, 1.628, 2.112, za, zb, p_, 'y')]
    # prateleira com dentículos sob os vidros (lado de fora)
    L.append(veio(prof_x([(z1, 1.555), (z1 + 0.03, 1.555), (z1 + 0.03, 1.567), (z1 + 0.022, 1.58), (z1, 1.585)], d0 + st - 0.03, d1 - st + 0.03, 'porta'), 'x'))
    n = 11
    for i in range(n):
        xc = d0 + st + (d1 - d0 - 2 * st) * (i + 0.5) / n
        L.append(veio(box(xc - 0.014, xc + 0.014, 1.53, 1.555, z1, z1 + 0.018, 'porta'), 'y'))
    # maçaneta dos dois lados, tambor da fechadura, caixa de cartas, dobradiças
    kx, ky = d1 - 0.07, 1.0
    for s, zf in ((1, z1), (-1, z0)):
        L.append(lathe([(0, 0.0), (0.0, 0.031), (0.003, 0.031), (0.006, 0.027), (0.006, 0.011), (0.03, 0.010), (0.034, 0.016), (0.040, 0.026), (0.050, 0.029), (0.058, 0.026), (0.063, 0.016), (0.065, 0.0)],
                       'latao', n=28, c0=(kx, ky, zf), eixo=(0, 0, s)))
        L.append(lathe([(0, 0.0), (0.0, 0.024), (0.004, 0.024), (0.007, 0.020), (0.012, 0.019), (0.014, 0.016), (0.014, 0.0)], 'latao', n=24, c0=(kx, ky + 0.16, zf), eixo=(0, 0, s)))
    L.append(box(kx - 0.0015, kx + 0.0015, ky + 0.151, ky + 0.169, z1 + 0.0138, z1 + 0.0146, 'ferro'))
    L += [box(kx - 0.012, kx + 0.012, ky + 0.156, ky + 0.164, z0 - 0.024, z0 - 0.014, 'latao')]
    cx = (d0 + d1) / 2
    pl = extr(ret_arred(cx - 0.135, cx + 0.135, 0.985, 1.055, 0.006), z1, z1 + 0.003, 'latao')
    fl = extr(ret_arred(cx - 0.115, cx + 0.115, 0.998, 1.042, 0.003), z1 + 0.003, z1 + 0.0055, 'latao')
    L += [pl, fl, cyl((cx - 0.118, 1.044, z1 + 0.0045), (cx + 0.118, 1.044, z1 + 0.0045), 0.0035, 'latao', n=12),
          texto('CARTAS', 0.017, (cx, 1.008, z1 + 0.0058), mat='tinta_escura')]
    for sx in (-0.125, 0.125):
        L.append(lathe([(0, 0.0), (0, 0.004), (0.0012, 0.0035), (0.0018, 0.0)], 'latao', n=10, c0=(cx + sx, 1.02, z1 + 0.003), eixo=(0, 0, 1)))
    for hy in (0.25, 1.15, 2.0):
        L += [box(d0, d0 + 0.032, hy - 0.045, hy + 0.045, z0 - 0.0015, z0, 'ferro'),
              cyl((d0 - 0.002, hy - 0.048, z0 - 0.006), (d0 - 0.002, hy + 0.048, z0 - 0.006), 0.0065, 'ferro', n=14),
              cyl((d0 - 0.002, hy + 0.048, z0 - 0.006), (d0 - 0.002, hy + 0.056, z0 - 0.006), 0.0045, 'ferro', n=10, r1=0.002)]
        for sy in (-0.03, 0.0, 0.03):
            L.append(cyl((d0 + 0.018, hy + sy, z0 - 0.0015), (d0 + 0.018, hy + sy, z0 - 0.0028), 0.004, 'ferro', n=10))
    L.append(box(d1 - 0.0005, d1 + 0.001, ky - 0.05, ky + 0.2, z0 + 0.01, z1 - 0.01, 'latao'))
    return parte('porta_frente', L, origem=(d0, y0, z0), pai=pai, grupo='C', extra={'gira_y': 95})


def parede_porta(ox):
    x0, x1 = ox - 1, ox + 1
    a0, a1, y1 = ox - 0.5, ox + 0.5, 2.3
    L = nucleo(x0, x1, (a0, a1, -0.01, y1))
    L += tabuas(x0, x1, (a0 - 0.125, a1 + 0.125, -1.0, y1 + 0.2))
    L += friso(x0, x1)
    g = 'guarn'; r = 'rodape'; zi = -T
    L += [rodape_ext(x0, a0 - 0.125), rodape_ext(a1 + 0.125, x1)] + rodape_int(x0, a0 - 0.095) + rodape_int(a1 + 0.095, x1)
    # marco da porta e batente de encosto
    L += [tb(a0, a0 + 0.04, 0.015, y1, zi, 0.0, g, 'y'), tb(a1 - 0.04, a1, 0.015, y1, zi, 0.0, g, 'y'), tb(a0 + 0.04, a1 - 0.04, y1 - 0.04, y1, zi, 0.0, g, 'x'),
          tb(a0 + 0.04, a0 + 0.053, 0.015, y1 - 0.04, -0.155, -0.12, g, 'y'), tb(a1 - 0.053, a1 - 0.04, 0.015, y1 - 0.04, -0.155, -0.12, g, 'y'),
          tb(a0 + 0.053, a1 - 0.053, y1 - 0.053, y1 - 0.04, -0.155, -0.12, g, 'x')]
    # soleira de pedra com nariz
    L.append(prof_x([(zi, 0.0), (zi, 0.015), (0.03, 0.015), (0.05, 0.004), (0.05, -0.03), (0.0, -0.03), (0.0, 0.0)], a0, a1, 'pedra'))
    # guarnição externa com plintos, verga larga, dentículos e capa
    for s in (-1, 1):
        a, b = sorted((ox + s * 0.495, ox + s * 0.62))
        L.append(tb(a, b, 0.16, y1 + 0.025, 0.0, 0.036, g, 'y'))
        a, b = sorted((ox + s * 0.49, ox + s * 0.628))
        pl = tb(a, b, -0.03, 0.16, 0.0, 0.05, g, 'y'); bevel(pl, 0.006, 1, 40); veio(pl, 'y'); L.append(pl)
    L.append(tb(a0 - 0.14, a1 + 0.14, y1 + 0.025, y1 + 0.19, 0.0, 0.04, g, 'x'))
    for i in range(21):
        xc = a0 - 0.13 + (a1 - a0 + 0.26) * (i + 0.5) / 21
        L.append(veio(box(xc - 0.02, xc + 0.02, y1 + 0.165, y1 + 0.19, 0.04, 0.062, g), 'y'))
    L.append(veio(prof_x([(0.0, y1 + 0.19), (0.078, y1 + 0.19), (0.078, y1 + 0.208), (0.055, y1 + 0.232), (0.0, y1 + 0.245)], a0 - 0.17, a1 + 0.17, g), 'x'))
    L.append(texto('27', 0.085, (ox, y1 + 0.062, 0.0412), mat='latao'))
    # guarnição interna
    L += [tb(a0 - 0.095, a0 + 0.006, 0.0, y1 - 0.006, zi - 0.02, zi, r, 'y'), tb(a1 - 0.006, a1 + 0.095, 0.0, y1 - 0.006, zi - 0.02, zi, r, 'y'),
          tb(a0 - 0.115, a1 + 0.115, y1 - 0.006, y1 + 0.115, zi - 0.024, zi, r, 'x')]
    L.append(veio(prof_x([(zi, y1 + 0.115), (zi - 0.04, y1 + 0.115), (zi - 0.04, y1 + 0.125), (zi - 0.03, y1 + 0.138), (zi, y1 + 0.145)], a0 - 0.13, a1 + 0.13, r), 'x'))
    p = parte('parede_porta', L, origem=(ox, 0, 0), grupo='B')
    porta_frente(ox, p)
    return p


# ------------------------------------------------------------------ interior
def pisos():
    out = []
    for i, (cx, cz) in enumerate(((-1, -1.3), (1, -1.3), (-1, -3.3), (1, -3.3))):
        o = box(cx - 1, cx + 1, -0.2, 0.0, cz - 1, cz + 1, 'cimento')
        pintar(o, 'assoalho', lambda c, n: n[1] > 0.9)
        out.append(parte(f'piso_{i + 1}', o, origem=(cx, 0, cz), grupo='D'))
    return out


def parede_interna():
    out = []
    xa, xb = -2.0, -1.88
    for i, cz in enumerate((-1.3, -3.3)):
        L = [box(xa, xb, 0.0, 2.8, cz - 1, cz + 1, 'reboco')]
        L.append(veio(extr([(xb, 0.0), (xb + 0.018, 0.0), (xb + 0.018, 0.105), (xb + 0.014, 0.122), (xb + 0.008, 0.130), (xb + 0.008, 0.138), (xb, 0.142)], cz - 1, cz + 1, 'rodape'), 'z'))
        L.append(veio(extr([(xb + 0.018, 0.0), (xb + 0.032, 0.0), (xb + 0.032, 0.006), (xb + 0.027, 0.015), (xb + 0.018, 0.02)], cz - 1, cz + 1, 'rodape'), 'z'))
        out.append(parte(f'parede_interna_{i + 1}', L, origem=(-1.94, 0, cz), grupo='E'))
    return out


# ------------------------------------------------------------------ cômoda
def puxador(x, y, zf):
    L = [extr(ret_arred(x - 0.046, x + 0.046, y - 0.017, y + 0.017, 0.008), zf, zf + 0.0018, 'latao')]
    for s in (-1, 1):
        L.append(lathe([(0, 0.0), (0.0, 0.0075), (0.003, 0.0075), (0.005, 0.0045), (0.012, 0.0045), (0.014, 0.0065), (0.017, 0.0065), (0.019, 0.004), (0.019, 0.0)],
                       'latao', n=14, c0=(x + s * 0.032, y + 0.004, zf + 0.0018), eixo=(0, 0, 1)))
    zc = zf + 0.0165
    pts = caminho_arred([(x - 0.032, y + 0.004, zc), (x - 0.036, y - 0.028, zc + 0.006), (x + 0.036, y - 0.028, zc + 0.006), (x + 0.032, y + 0.004, zc)], 0.012, 5)
    L.append(fio(pts, 0.0028, 'latao', res=3))
    return L


def comoda(pos, rot):
    X, Z0, Z1 = 0.45, -0.22, 0.20
    v = 'verniz'
    L = [tb(-X, -X + 0.02, 0.10, 0.82, Z0, Z1, v, 'y'), tb(X - 0.02, X, 0.10, 0.82, Z0, Z1, v, 'y'),
         tb(-X + 0.02, X - 0.02, 0.10, 0.82, Z0 + 0.004, Z0 + 0.010, 'pinho', 'y'),
         tb(-X + 0.02, X - 0.02, 0.10, 0.118, Z0 + 0.01, Z1 - 0.022, 'pinho', 'x')]
    top = box(-X - 0.022, X + 0.022, 0.822, 0.848, Z0 - 0.004, Z1 + 0.034, v); bevel(top, 0.007, 3, 40); veio(top, 'x'); L.append(top)
    L.append(veio(prof_x([(Z1, 0.80), (Z1 + 0.018, 0.822), (Z1, 0.822)], -X, X, v), 'x'))
    for xs in (-1, 1):
        L.append(veio(extr([(xs * X, 0.80), (xs * (X + 0.012), 0.822), (xs * X, 0.822)][::xs], Z0, Z1 + 0.012, v), 'z'))
    ys = (0.125, 0.345, 0.363, 0.585, 0.603, 0.80)
    for (a, b) in ((0.10, 0.125), (0.345, 0.363), (0.585, 0.603), (0.80, 0.82)):
        L.append(tb(-X + 0.02, X - 0.02, a, b, Z1 - 0.045, Z1, v, 'x'))
        if b < 0.8:
            for xs in (-1, 1):       # corrediças de madeira
                xa, xb = sorted((xs * (X - 0.02), xs * (X - 0.045)))
                L.append(tb(xa, xb, b - 0.012, b, Z0 + 0.01, Z1 - 0.045, 'pinho', 'z'))
    # base com pés recortados e moldura
    cur = [(-X - 0.006, 0.0), (-X + 0.085, 0.0)] + arco(-X + 0.145, 0.0, 0.06, 180, 90, 6)[1:] + arco(X - 0.145, 0.0, 0.06, 90, 0, 6)[:-1] + [(X - 0.085, 0.0), (X + 0.006, 0.0), (X + 0.006, 0.10), (-X - 0.006, 0.10)]
    L.append(veio(extr(cur, Z1 - 0.014, Z1 + 0.006, v), 'x'))
    for xs in (-1, 1):
        c2 = [(Z0, 0.0), (Z0 + 0.07, 0.0)] + arco(Z0 + 0.12, 0.0, 0.05, 180, 90, 5)[1:] + arco(Z1 - 0.12, 0.0, 0.05, 90, 0, 5)[:-1] + [(Z1 - 0.07, 0.0), (Z1 + 0.006, 0.0), (Z1 + 0.006, 0.10), (Z0, 0.10)]
        xa, xb = sorted((xs * (X + 0.006), xs * (X - 0.014)))
        L.append(veio(prof_x(c2, xa, xb, v), 'z'))
    L.append(veio(prof_x([(Z1 + 0.006, 0.085), (Z1 + 0.016, 0.088), (Z1 + 0.016, 0.096), (Z1 + 0.006, 0.108)], -X - 0.016, X + 0.016, v), 'x'))
    for xs in (-1, 1):
        pf = [(xs * (X + 0.006), 0.085), (xs * (X + 0.016), 0.088), (xs * (X + 0.016), 0.096), (xs * (X + 0.006), 0.108)]
        L.append(veio(extr(pf[::xs], Z0, Z1 + 0.016, v), 'z'))
    c = parte('comoda', L, origem=(0, 0, 0), grupo='F')
    for i in range(3):
        y0, y1 = ys[2 * i] + 0.002, ys[2 * i + 1] - 0.002
        xa, xb = -X + 0.022, X - 0.022
        G = [tb(xa, xb, y0, y1, Z1 - 0.02, Z1, v, 'x')]
        # filete aplicado na frente
        for (a, b, c0, d) in ((xa + 0.03, xb - 0.03, y0 + 0.028, y0 + 0.035), (xa + 0.03, xb - 0.03, y1 - 0.035, y1 - 0.028)):
            G.append(tb(a, b, c0, d, Z1, Z1 + 0.004, v, 'x'))
        for (a, b) in ((xa + 0.03, xa + 0.037), (xb - 0.037, xb - 0.03)):
            G.append(tb(a, b, y0 + 0.035, y1 - 0.035, Z1, Z1 + 0.004, v, 'y'))
        # caixa da gaveta em pinho
        G += [tb(xa + 0.004, xa + 0.016, y0 + 0.012, y1 - 0.03, Z0 + 0.03, Z1 - 0.02, 'pinho', 'z'), tb(xb - 0.016, xb - 0.004, y0 + 0.012, y1 - 0.03, Z0 + 0.03, Z1 - 0.02, 'pinho', 'z'),
              tb(xa + 0.016, xb - 0.016, y0 + 0.012, y1 - 0.04, Z0 + 0.03, Z0 + 0.042, 'pinho', 'x'),
              tb(xa + 0.016, xb - 0.016, y0 + 0.02, y0 + 0.026, Z0 + 0.042, Z1 - 0.02, 'pinho', 'x')]
        ym = (y0 + y1) / 2
        for px in (-0.24, 0.24):
            G += puxador(px, ym, Z1 + 0.004 if False else Z1)
        G.append(extr([(q[0], q[1]) for q in arco(0.0, ym, 0.012, 0, 360, 16)[:-1]], Z1, Z1 + 0.0015, 'latao'))
        G.append(extr([(-0.0022, ym - 0.007), (0.0022, ym - 0.007), (0.0012, ym)] + arco(0.0, ym + 0.002, 0.003, -30, 210, 8), Z1 + 0.0015, Z1 + 0.0019, 'ferro'))
        parte(f'gaveta_{i + 1}', G, origem=(0, 0, 0), pai=c, grupo='F', extra={'desliza_z': 0.30})
    c.location = P(*pos); c.rotation_euler = (0, 0, math.radians(rot))
    return c


# ------------------------------------------------------------------ itens
def lata(pos, rot):
    R, Hh = 0.0370, 0.108
    corpo = lathe([(0.0, 0.0), (0.0, 0.031), (0.0015, 0.031), (0.0015, 0.0355), (0.0, 0.0362), (0.0, R + 0.0008), (0.003, R + 0.0008), (0.0036, R), (0.012, R), (0.014, R - 0.0008), (0.016, R),
                   (0.021, R), (0.023, R - 0.0008), (0.025, R), (Hh - 0.025, R), (Hh - 0.023, R - 0.0008), (Hh - 0.021, R), (Hh - 0.016, R), (Hh - 0.014, R - 0.0008), (Hh - 0.012, R),
                   (Hh - 0.0036, R), (Hh - 0.003, R + 0.0008), (Hh, R + 0.0008), (Hh, 0.0362), (Hh - 0.003, 0.0355), (Hh - 0.003, 0.030), (Hh - 0.0022, 0.028), (Hh - 0.003, 0.026),
                   (Hh - 0.003, 0.018), (Hh - 0.0022, 0.016), (Hh - 0.003, 0.014), (Hh - 0.003, 0.0)], 'lata', n=48)
    rot_ = lathe([(0.006, R + 0.0003), (Hh - 0.006, R + 0.0003)], 'rotulo', n=48)
    faixa = lathe([(0.030, R + 0.0006), (0.078, R + 0.0006)], 'rotulo_creme', n=48)
    rr = R + 0.0009
    L = [corpo, rot_, faixa,
         texto('FEIJÃO', 0.022, (0.0, 0.052, 0), mat='tinta_vinho', raio=rr, eixo_c=(0, 0)),
         texto('CARIOCA COZIDO', 0.0062, (0.0, 0.040, 0), mat='tinta_vinho', raio=rr, eixo_c=(0, 0)),
         texto('Sítio Bom', 0.0105, (0.0, 0.085, 0), mat='tinta_creme', raio=rr - 0.0003, eixo_c=(0, 0)),
         texto('Peso líquido 400 g', 0.0052, (0.0, 0.016, 0), mat='tinta_creme', raio=rr - 0.0003, eixo_c=(0, 0)),
         texto('INGREDIENTES', 0.0055, (math.pi, 0.066, 0), mat='tinta_vinho', raio=rr, eixo_c=(0, 0)),
         texto('feijão carioca, água e sal.', 0.0045, (math.pi, 0.057, 0), mat='tinta_vinho', raio=rr, eixo_c=(0, 0)),
         texto('Depois de aberto, guarde', 0.0045, (math.pi, 0.046, 0), mat='tinta_vinho', raio=rr, eixo_c=(0, 0)),
         texto('na geladeira por até 3 dias.', 0.0045, (math.pi, 0.039, 0), mat='tinta_vinho', raio=rr, eixo_c=(0, 0))]
    o = parte('lata_feijao', L, origem=(0, 0, 0), grupo='G', suave=40)
    o.location = P(*pos); o.rotation_euler = (0, 0, math.radians(rot))
    return o


def lampiao(pos, rot):
    e = 'esmalte'
    L = [lathe([(0.0, 0.0), (0.0, 0.058), (0.003, 0.063), (0.010, 0.066), (0.036, 0.066), (0.044, 0.063), (0.052, 0.052), (0.057, 0.036), (0.059, 0.027), (0.059, 0.0)], e, n=40),
         lathe([(0.059, 0.0), (0.059, 0.029), (0.064, 0.029), (0.066, 0.034), (0.074, 0.034), (0.076, 0.031), (0.080, 0.031), (0.080, 0.0)], 'lata', n=32),
         lathe([(0.080, 0.022), (0.080, 0.030), (0.082, 0.033), (0.084, 0.033)], 'lata', n=32),
         box(-0.006, 0.006, 0.080, 0.094, -0.0012, 0.0012, 'pavio')]
    # manivela do pavio
    L += [cyl((0.0, 0.069, 0.0), (0.0, 0.069, 0.058), 0.0016, 'arame', n=8),
          lathe([(0.0, 0.0), (0.0, 0.009), (0.004, 0.009), (0.004, 0.0)], 'lata', n=16, c0=(0, 0.069, 0.058), eixo=(0, 0, 1), lobes=0.12)]
    # globo de vidro
    L.append(lathe([(0.084, 0.031), (0.094, 0.040), (0.110, 0.048), (0.128, 0.051), (0.146, 0.048), (0.162, 0.041), (0.176, 0.034), (0.186, 0.031)], 'vidro', n=36))
    # coroa e chaminé
    L.append(lathe([(0.186, 0.030), (0.186, 0.036), (0.190, 0.037), (0.194, 0.033), (0.204, 0.029), (0.222, 0.027), (0.224, 0.034), (0.228, 0.036), (0.236, 0.030), (0.240, 0.018), (0.240, 0.0)], e, n=32))
    # tampa do tanque
    L.append(lathe([(0.0, 0.0), (0.0, 0.010), (0.007, 0.010), (0.008, 0.008), (0.008, 0.0)], 'lata', n=18, c0=(0.034, 0.050, -0.034), eixo=(0.3, 1, -0.3), lobes=0.10))
    # tubos laterais
    for s in (-1, 1):
        pts = caminho_arred([(s * 0.050, 0.046, 0.0), (s * 0.074, 0.060, 0.0), (s * 0.074, 0.200, 0.0), (s * 0.050, 0.228, 0.0), (s * 0.026, 0.228, 0.0)], 0.014, 5)
        L.append(fio(pts, 0.0062, e, res=4))
    # alça e arames de proteção do globo
    L.append(fio([(0.079 * math.cos(math.radians(a)), 0.205 + 0.092 * math.sin(math.radians(a)), -0.03 * math.sin(math.radians(a))) for a in range(0, 181, 12)], 0.0017, 'arame'))
    for yy, rr in ((0.108, 0.0505), (0.150, 0.0495)):
        L.append(fio([(rr * math.cos(math.radians(a)), yy, rr * math.sin(math.radians(a))) for a in range(0, 360, 15)], 0.0012, 'arame', fechado=True))
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        L.append(fio([(r_ * ca, y_, r_ * sa) for (y_, r_) in ((0.086, 0.036), (0.098, 0.046), (0.112, 0.0515), (0.128, 0.0535), (0.146, 0.051), (0.162, 0.044), (0.184, 0.038))], 0.0012, 'arame'))
    L.append(texto('LUZEIRO  Nº 2', 0.0085, (0.0, 0.019, 0), mat='tinta_creme', raio=0.0664, eixo_c=(0, 0)))
    o = parte('lampiao', L, origem=(0, 0, 0), grupo='G', suave=40)
    o.location = P(*pos); o.rotation_euler = (0, 0, math.radians(rot))
    return o


def construir():
    parede_janela(-1.0)
    parede_porta(1.0)
    pisos()
    parede_interna()
    comoda((-1.88 + 0.228, 0.0, -1.7), 90)
    lampiao((-1.66, 0.848, -1.45), 20)
    lata((-1.60, 0.848, -1.92), -55)
    return PARTES
