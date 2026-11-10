"""M4A1 (carabina 5,56 com guarda-mão de quatro trilhos, alça de transporte
removível e coronha retrátil). Desenho próprio, sem marcas de fabricante.
Cada peça é um objeto separado; medidas em mm (ver lib.py)."""
import math
from mathutils import Vector
from lib import *

# materiais: anod (alumínio anodizado), fosf (aço fosfatado), polim (polímero),
# polim_grip (polímero quadriculado), magal (carregador), serr (aço serrilhado),
# inox, latao, cobre, tinta (gravações)

PIC = [(-7.85, 0), (7.85, 0), (10.6, -2.75), (7.9, -5.5)]      # meio perfil do trilho (x, y do topo)


def fendas_trilho(u0, n, v_topo, passo=10.008):
    return [box(u0 - i * passo - 5.23, u0 - i * passo, v_topo - 3.0, v_topo + 1, -12, 12, 'anod')
            for i in range(n)]


# ------------------------------------------------------------------ receptor superior
def receptor_superior():
    sec = [(12.5, -19), (12.5, -10.77)]
    sec += arco(0, 0, 16.5, -40.7, 54, 10)[1:]
    sec += [(9.6, 20.6), (9.6, 21.6), (7.9, 22.6), (7.9, 24.5), (10.6, 27.25), (7.85, 30)]
    sec = sec + [(-w, v) for (w, v) in reversed(sec)]
    corpo = extr(sec, -198, 0, 'anod', plane='wv')
    cortes = [cyl((-205, 0, 0), (5, 0, 0), 12.9, 'anod', n=32),
              box(-95, -38, -9, 7, 5, 30, 'anod'),                       # janela de ejeção
              box(-205, -168, 12.5, 19.5, -6.7, 6.7, 'anod'),            # canal da alavanca
              box(-76, -8, -25, -11, -9, 9, 'anod')]                     # passagem do carregador
    cortes += fendas_trilho(-8, 19, 30)
    cut(corpo, cortes)
    bevel(corpo, 0.5, 1, 40)
    o = [corpo]
    o.append(lathe([(0, 15.2), (11, 15.2), (11, 12.6), (0, 12.6)], 'anod', n=32))      # rosca da porca do cano
    # olhais dos pinos
    for (u0, u1) in ((-11, 1), (-193, -179)):
        l = extr(ret_arred(u0, u1, -33, -18, 4, 3), -6, 6, 'anod')
        cut(l, pin((u0 + u1) / 2, -27, 3.3, -9, 9, 'anod'))
        o.append(l)
    # defletor de estojos
    d = extr([(-98, 14), (-105, 25.5), (-119, 25.5), (-127, 14)], -8, 13, 'anod', plane='uw')
    o.append(bevel(d, 2.0, 2, 30))
    # alojamento do impulsor
    o.append(cyl((-126, 3, 12), (-166, 3, 20.5), 8.6, 'anod', n=20))
    o.append(cyl((-166, 3, 20.5), (-168, 3, 20.9), 9.6, 'anod', n=20))
    # reforço do lado esquerdo (came do ferrolho)
    r = extr(ret_arred(-92, -52, 0, 13, 3, 3), -17.4, -10, 'anod')
    o.append(bevel(r, 0.8, 1))
    # ressalto da frente (apoio do tubo de gás)
    o.append(bevel(box(-14, 0, 14, 22, -9, 9, 'anod'), 1.0, 1))
    return parte('receptor_superior', o, origem=(-100, 0, 0))


def impulsor():
    o = [cyl((-166, 3, 20.5), (-175, 3, 22.4), 5.2, 'fosf', n=16),
         cyl((-175, 3, 22.4), (-180, 3, 23.5), 7.6, 'serr', n=24, lobes=0.08)]
    return parte('impulsor_ferrolho', o, origem=(-166, 3, 20.5))


def tampa_janela():
    def faixa(r0, r1, a0, a1, u0, u1):
        p = arco(0, 0, r0, a0, a1, 6) + arco(0, 0, r1, a1, a0, 6)
        return extr(p, u0, u1, 'fosf', plane='wv')
    o = [faixa(14.6, 18.0, -44, 32, -101, -33)]
    for (u0, u1) in ((-98, -79), (-76, -58), (-55, -36)):
        o.append(bevel(faixa(15.2, 18.8, -30, 20, u0, u1), 0.4, 1))
    o.append(cyl((-104, -12.3, 12.6), (-30, -12.3, 12.6), 2.0, 'fosf', n=12))        # dobradiça
    o.append(cyl((-67, 13.5, 13.6), (-67, 12.5, 16.5), 1.6, 'fosf', n=10))           # trava
    return parte('tampa_janela', o, origem=(-67, -12.3, 12.6))


def ferrolho():
    o = [lathe([(-14, 0), (-14, 5.6), (-21, 5.6), (-21, 9.3), (-30, 9.3), (-30, 12.6),
                (-188, 12.6), (-190, 11), (-190, 0)], 'fosf_escuro', n=28)]
    cut(o[0], [box(-100, -40, -6, 20, 6, 20, 'fosf_escuro')])
    return parte('ferrolho', o, origem=(-100, 0, 0), grupo='D')


def alavanca_manejo():
    T = [(-170, 6.5), (-199, 6.5), (-201, 25), (-209, 25), (-211, 9), (-211, -9), (-209, -25),
         (-201, -25), (-199, -6.5), (-170, -6.5)]
    a = bevel(extr(T, 13.2, 19.2, 'anod', plane='uw'), 0.9, 2)
    t = bevel(extr([(-196, -9), (-197, -27.5), (-209, -27.5), (-210, -24), (-203, -22), (-203, -9)],
                   14.2, 18.2, 'fosf', plane='uw'), 0.6, 1)
    o = parte('alavanca_manejo', [a], origem=(-198, 16, 0), grupo='D')
    parte('trava_alavanca', [t, cyl((-200, 13.4, -12), (-200, 19.0, -12), 1.3, 'inox', n=10)],
          origem=(-200, 16, -12), pai=o, grupo='D')
    return o


# ------------------------------------------------------------------ receptor inferior
LINHA_BAIXO = [(-134, -50), (-136, -55), (-172, -55), (-178, -51), (-196, -35), (-213, -29)]


def receptor_inferior():
    perfil = [(4, -19), (4, -29), (1, -33), (-3, -36), (-5, -84), (-70, -74), (-73, -52), (-78, -50)]
    perfil += LINHA_BAIXO + [(-213, -12), (-198, -12), (-198, -19)]
    corpo = extr(perfil, -11.5, 11.5, 'anod')
    cortes = [box(-70, -9.5, -95, -10, -11.4, 11.4, 'anod'),                 # poço do carregador
              box(-174, -76, -47, -10, -8, 8, 'anod'),                       # caixa do mecanismo
              box(-196, -170, -30, -10, -8, 8, 'anod'),
              box(-12, 2, -34, -10, -6.3, 6.3, 'anod'),                      # olhal do pino pivô
              box(-116, -100, -60, -40, -3.6, 3.6, 'anod')]                  # fenda do gatilho
    for (u, v, r) in ((-5, -27, 3.25), (-186, -27, 3.25), (-108, -40, 2.0), (-87, -32, 2.0),
                      (-140, -31, 4.8), (-147, -22.5, 1.6)):
        cortes.append(pin(u, v, r, -20, 20, 'anod'))
    cut(corpo, cortes)
    bevel(corpo, 0.7, 1, 40)
    o = [corpo]
    # poço do carregador mais largo, com boca chanfrada
    poco = extr([(4.6, -19.4), (4.6, -29), (1.8, -33.4), (-2.2, -36.4), (-4.2, -85), (-70.6, -74.8), (-74, -52), (-78, -46),
                 (-78, -31), (-70, -19.4)], -14, 14, 'anod')
    cut(poco, [box(-70, -9.5, -95, -10, -11.4, 11.4, 'anod'),
               box(-12, 2, -34, -10, -6.3, 6.3, 'anod'),
               pin(-5, -27, 3.25, -20, 20, 'anod'),
               box(-86, -54, -43.6, -35.4, -20, -12.6, 'anod')])              # rebaixo do retém
    o.append(bevel(poco, 1.6, 2, 40))
    # anel do tubo da coronha
    anel = lathe([(-213, 14.7), (-213, 18.6), (-198, 18.6), (-198, 14.7)], 'anod', n=36, anel=True)
    o.append(bevel(anel, 0.8, 1))
    # orelhas do guarda-mato e cerca do botão do retém
    o.append(bevel(extr([(-133, -50), (-142, -50), (-142, -76), (-136, -76)], -6.5, 6.5, 'anod'), 0.8, 1))
    cerca = extr(ret_arred(-90, -71, -47, -32, 3, 3), 11, 14.2, 'anod')
    cut(cerca, extr(ret_arred(-87.5, -73.5, -44.5, -34.5, 2, 3), 9, 16, 'anod'))
    o.append(bevel(cerca, 0.5, 1))
    # batentes do seletor e ressalto do retém do ferrolho
    o.append(bevel(box(-84, -64, -31, -19, -13.6, -11, 'anod'), 0.8, 1))
    # gravações (lado esquerdo)
    o.append(texto('SEGURO', 2.6, -112, -32.2, -11.56, alinhar='RIGHT'))
    o.append(texto('SEMI', 2.6, -140, -24.6, -11.56))
    o.append(texto('AUTO', 2.6, -152, -32.2, -11.56, alinhar='LEFT'))
    for i, s in enumerate(('FUZIL M4A1', 'CAL. 5,56 MM', 'RC 104517')):
        o.append(texto(s, 3.4, -38, -52 - i * 5.2, -14.06))
    o.append(texto('SEGURO', 2.2, -122, -32, 11.56, lado=1, alinhar='LEFT'))
    o.append(texto('AUTO', 2.2, -158, -32, 11.56, lado=1, alinhar='RIGHT'))
    return parte('receptor_inferior', o, origem=(-100, -40, 0))


def controles(pai):
    # gatilho (curva côncava para a frente)
    g = [(-99, -38), (-104, -52)]
    g += [(-104 - 5.5 * math.sin(math.radians(a)), -61 + 9 * math.cos(math.radians(a)))
          for a in range(0, 181, 30)][1:-1]
    g += [(-103, -71.5), (-106.5, -72)]
    g += [(-107.5 - 6.5 * math.sin(math.radians(a)), -61 + 10 * math.cos(math.radians(a)))
          for a in range(180, -1, -30)][1:-1]
    g += [(-110.5, -50), (-113, -38)]
    parte('gatilho', bevel(extr(g, -3.2, 3.2, 'fosf'), 0.9, 2), origem=(-108, -40, 0), pai=pai)
    # guarda-mato
    gm = bevel(extr([(-70.5, -73.3), (-141, -71), (-141, -74.2), (-70.5, -76.6)], -5.6, 5.6, 'anod'), 0.5, 1)
    parte('guarda_mato', [gm, pin(-138.5, -72.6, 1.5, -6.9, 6.9, 'fosf', n=10),
                          pin(-73, -74.5, 1.5, -5.8, 5.8, 'fosf', n=10)], pai=pai)
    # seletor de tiro (apontado para SEGURO)
    al = bevel(extr([(-140, -26.6), (-122, -28.4), (-118.5, -31), (-122, -33.6), (-140, -35.4),
                     (-145, -33.5), (-145, -28.5)], -16.4, -13.2, 'fosf'), 0.7, 2)
    s = [al, pin(-140, -31, 4.7, -13.4, 11.5, 'fosf', n=20),
         pin(-140, -31, 5.6, 11.4, 12.7, 'fosf', n=20),
         bevel(box(-143, -129.5, -31.7, -30.3, 12.6, 13.2, 'fosf'), 0.2, 1)]
    parte('seletor', s, origem=(-140, -31, 0), pai=pai)
    # retém do ferrolho
    pa = bevel(extr([(-65, -5), (-81, -5), (-82, -17), (-65, -17)], -17.6, -12.4, 'fosf'), 1.0, 2)
    cut(pa, [box(-90, -60, -7.6 - i * 2.6, -6.6 - i * 2.6, -19, -17.0, 'fosf') for i in range(4)])
    ha = bevel(extr([(-69, -16), (-78, -16), (-77.5, -30.5), (-70.5, -30.5)], -15.2, -11.6, 'fosf'), 0.7, 1)
    parte('retem_ferrolho', [pa, ha, cyl((-80, -21, -13.4), (-66, -21, -13.4), 1.3, 'inox', n=10)],
          origem=(-74, -21, -13.4), pai=pai)
    # retém do carregador: barra à esquerda, botão à direita
    b = bevel(box(-85.5, -54.5, -43.2, -35.8, -14.3, -12.8, 'fosf'), 0.5, 1)
    bt = bevel(extr(ret_arred(-86.5, -74.5, -43.8, -35.2, 2.2, 3), 11.6, 15.0, 'serr'), 0.4, 1)
    cut(bt, [box(-88, -73, -42.6 + i * 1.7, -41.9 + i * 1.7, 14.5, 16, 'serr') for i in range(5)])
    parte('retem_carregador', [b, bt, pin(-80.5, -39.5, 2.4, -12.8, 11.6, 'fosf', n=12)],
          origem=(-80.5, -39.5, 0), pai=pai)
    # pinos
    def pino(nome, u, v, r, cabeca):
        o = [pin(u, v, r, -12.0, 12.0, 'fosf', n=16)]
        if cabeca:
            o.append(pin(u, v, r + 1.3, 11.9, 13.3, 'fosf', n=18))
            o.append(pin(u, v, r - 1.3, -12.5, -11.9, 'inox', n=10))
        parte(nome, o, origem=(u, v, 0), pai=pai)
    pino('pino_pivo', -5, -27, 3.15, True)
    pino('pino_desmontagem', -186, -27, 3.15, True)
    pino('pino_gatilho', -108, -40, 1.95, False)
    pino('pino_cao', -87, -32, 1.95, False)
    pino('pino_armadilha', -147, -22.5, 1.55, False)


def punho(pai):
    T = Vector((-160.0, -56.0))
    B = Vector((-207.0, -146.0))
    L = (B - T).length
    a = (B - T) / L
    e = Vector((-a.y, a.x)) * -1           # perpendicular apontando para a frente
    if e.x < 0:
        e = -e
    rings = []
    ts = [-0.30, -0.24, -0.18, -0.12, -0.08, -0.04, 0.0, 0.035, 0.07, 0.105, 0.14, 0.18, 0.22, 0.26, 0.30, 0.36, 0.42, 0.50, 0.60, 0.72, 0.84, 0.94, 0.985, 1.0]
    for t in ts:
        c = T + a * L * t
        df = 18 + 4.2 * math.exp(-((t - 0.34) / 0.075) ** 2) - 1.5 * max(0, t - 0.5)
        k = max(0.0, min(1.0, (0.22 - t) / 0.30))
        dr = 17.5 + 24 * k * k * (3 - 2 * k) + 3.0 * max(0, t - 0.75) / 0.25
        hw = 14.6 - 1.3 * max(0, t) - 3.0 * k
        if t >= 0.985:
            df, dr, hw = df - 1.2 * (t - 0.97) * 40, dr - 1.2 * (t - 0.97) * 40, hw - 1.2 * (t - 0.97) * 40
        cx, rx = (df - dr) / 2, (df + dr) / 2
        ring = []
        for (x, y) in superelipse(rx, hw, n=28, e=2.7, cx=cx):
            q = c + e * x
            ring.append(P(q.x, q.y, y))
        rings.append(ring)
    g = loft(rings, 'polim_grip')
    lim = [(-110, -55)] + LINHA_BAIXO[2:] + [(-240, -29), (-240, 10), (-110, 10)]
    cut(g, extr(lim, -30, 30, 'polim'))
    o = parte('punho', [g], origem=(-160, -56, 0), pai=pai, suave=45, grupo='D')
    return o


# ------------------------------------------------------------------ cano e frente
def cano():
    prof = [(-16, 0), (-16, 11.0), (-14, 12.6), (-1, 12.6), (-1, 14.6), (2.5, 14.6), (2.5, 12.3),
            (38, 12.3), (40, 11.4), (58, 11.4), (62, 8.7), (203, 8.7), (204, 9.52), (243, 9.52),
            (244.5, 8.0), (300, 8.0), (302, 9.15), (358, 9.15), (359, 6.3), (372, 6.3),
            (372, 2.85), (330, 2.85), (330, 0)]
    c = lathe(prof, 'fosf', n=32)
    return parte('cano', [c], origem=(180, 0, 0), grupo='B')


def quebra_chamas(pai):
    q = lathe([(357.5, 6.4), (357.5, 9.6), (358.5, 11.0), (369, 11.0), (370, 10.2), (372, 10.2),
               (373, 11.0), (397.5, 10.8), (399, 9.6), (399, 6.6), (371, 6.6), (371, 6.4)], 'fosf', n=30)
    cortes = []
    for ang in (-120, -60, 0, 60, 120):
        r = math.radians(ang)
        p0 = (384.5, 4 * math.cos(r), 4 * math.sin(r))
        p1 = (384.5, 14 * math.cos(r), 14 * math.sin(r))
        cb = cyl(p0, p1, 1.75, 'fosf', n=10)
        for v in cb.data.vertices:
            v.co.y = (v.co.y - 0.3845) * 5.4 + 0.3845
        cortes.append(cb)
    for s in (-1, 1):
        cortes.append(box(359.5, 368, -14, 14, s * 9.6, s * 14, 'fosf'))            # faces de chave
    cut(q, cortes)
    parte('quebra_chamas', [q], origem=(378, 0, 0), pai=pai, grupo='B')
    parte('arruela_boca', lathe([(355.2, 6.4), (355.2, 9.6), (356.3, 10.6), (357.4, 9.6), (357.4, 6.4)],
                                'inox', n=24), pai=pai, grupo='B')


def base_massa(pai):
    o = []
    for (u0, u1) in ((205, 217), (229, 243)):
        o.append(bevel(lathe([(u0, 9.5), (u0, 13.6), (u1, 13.6), (u1, 9.5)], 'fosf', n=28), 0.6, 1))
    q = extr([(205, 8), (206.5, 16), (222, 51.5), (243, 51.5), (243, 8)], -4.6, 4.6, 'fosf')
    cut(q, [extr([(212.5, 15), (238, 15), (238, 44), (227, 44)], -10, 10, 'fosf')])
    o.append(bevel(q, 0.9, 1))
    topo = extr([(221.5, 49), (220.5, 60.5), (223, 64.5), (238, 64.5), (241, 61), (243, 49)], -8.2, 8.2, 'fosf')
    cut(topo, [box(210, 250, 52.5, 70, -4.6, 4.6, 'fosf')])
    o.append(bevel(topo, 0.8, 1))
    o.append(bevel(box(205, 243, -13.5, -8, -5.5, 5.5, 'fosf'), 0.8, 1))
    # ressalto de baioneta e suporte do zarelho
    o.append(bevel(extr([(-3.2, -12), (3.2, -12), (3.2, -17.5), (5.6, -17.5), (5.6, -21.5), (-5.6, -21.5),
                         (-5.6, -17.5), (-3.2, -17.5)], 229.5, 243, 'fosf', plane='wv'), 0.5, 1))
    o.append(bevel(extr(ret_arred(205.5, 216.5, -22, -12, 3, 3), -3.4, 3.4, 'fosf'), 0.5, 1))
    b = parte('base_massa', o, origem=(224, 0, 0), pai=pai, grupo='B')
    for i, u in enumerate((210.5, 236)):
        parte(f'pino_base_massa_{i + 1}', pin(u, -10.6, 1.6, -9.6, 9.6, 'inox', n=10), pai=b, grupo='B')
    parte('pino_massa', [cyl((232, 51, 0), (232, 54, 0), 4.0, 'fosf', n=16, lobes=0.12),
                         cyl((232, 54, 0), (232, 62.6, 0), 1.05, 'fosf', n=10)],
          origem=(232, 51.5, 0), pai=b, grupo='B')
    laco = caminho_arred([(211, -17.5, -16.5), (207, -38, -16.5), (207, -38, 16.5), (211, -17.5, 16.5)], 4, 5)
    parte('zarelho_frontal', [fio(laco, 1.7, 'fosf'), pin(211, -17.5, 2.3, -5.2, 5.2, 'fosf', n=12)],
          origem=(211, -17.5, 0), pai=b, grupo='B')
    parte('tubo_gas', [cyl((-8, 14.5, 0), (214, 14.5, 0), 2.4, 'inox', n=12),
                       pin(210, 14.5, 1.0, -5.2, 5.2, 'inox', n=8)], pai=pai, grupo='B')


CG = (0.0, -2.0)           # centro do guarda-mão (w, v)


def guarda_mao(pai):
    def pol(k, t, r):
        a = math.radians(90 * k)
        return (CG[0] + r * math.cos(a) - t * math.sin(a), CG[1] + r * math.sin(a) + t * math.cos(a))
    sec = []
    for k in range(4):
        for (t, r) in ((-11, 19.6), (-7.9, 19.6), (-7.9, 23.5), (-10.6, 26.25), (-7.85, 29),
                       (7.85, 29), (10.6, 26.25), (7.9, 23.5), (7.9, 19.6), (11, 19.6)):
            sec.append(pol(k, t, r))
    U0, U1 = 25, 191
    g = extr(sec, U0, U1, 'anod', plane='wv')
    cortes = [cyl((U0 - 5, CG[1], 0), (U1 + 5, CG[1], 0), 17.0, 'anod', n=32)]
    for k in range(4):
        a = math.radians(90 * k)
        cs, sn = math.cos(a), math.sin(a)
        for i in range(16):
            u = 31 + i * 10.008
            c = box(u, u + 5.23, -1, 4, -12, 12, 'anod')          # caixa local: v = radial 26..30
            for vv in c.data.vertices:
                t, r = -vv.co.x / MM, 26 + vv.co.z / MM
                vv.co.x = (CG[0] + r * cs - t * sn) * MM
                vv.co.z = (CG[1] + r * sn + t * cs) * MM
            cortes.append(c)
        ad = a + math.pi / 4
        for i in range(7):
            u = 42 + i * 22.0
            for du in (-4, 4):
                cortes.append(cyl((u + du, CG[1] + 13 * math.sin(ad), CG[0] + 13 * math.cos(ad)),
                                  (u + du, CG[1] + 27 * math.sin(ad), CG[0] + 27 * math.cos(ad)), 3.3, 'anod', n=12))
            c = box(u - 4, u + 4, 0, 14, -3.3, 3.3, 'anod')
            for vv in c.data.vertices:
                t, r = -vv.co.x / MM, 13 + vv.co.z / MM
                vv.co.x = (CG[0] + r * math.cos(ad) - t * math.sin(ad)) * MM
                vv.co.z = (CG[1] + r * math.sin(ad) + t * math.cos(ad)) * MM
            cortes.append(c)
    cut(g, cortes)
    import bpy
    baixo = g.copy()
    baixo.data = g.data.copy()
    bpy.context.scene.collection.objects.link(baixo)
    VS = CG[1] - 11.4
    cut(g, [box(U0 - 10, U1 + 10, -60, VS, -40, 40, 'anod')])
    cut(baixo, [box(U0 - 10, U1 + 10, VS + 0.25, 60, -40, 40, 'anod')])
    bevel(g, 0.35, 1, 40)
    bevel(baixo, 0.35, 1, 40)
    # presilha de mola do guarda-mão inferior
    s = parte('guarda_mao_superior', [g], origem=(108, CG[1], 0), pai=pai, grupo='B')
    parte('guarda_mao_inferior', [baixo, bevel(box(176, 190, -35.2, -31, -5, 5, 'fosf'), 0.5, 1)],
          origem=(108, CG[1] - 20, 0), pai=pai, grupo='B')
    # anel delta (estriado) e tampa da frente
    d = lathe([(3, 15.4), (3, 21), (5, 24.4), (8.5, 26.6), (21.5, 24.2), (24.8, 22.6), (24.8, 15.4)],
              'anod', n=44, lobes=0.035, lobe_min=24, anel=True)
    parte('anel_delta', bevel(d, 0.4, 1, 50), pai=pai, grupo='B')
    t = lathe([(191.2, 9.2), (191.2, 24.5), (193, 25.5), (194.6, 24.5), (194.6, 9.2)], 'fosf', n=32, c0=(0, CG[1], 0), anel=True)
    t2 = lathe([(191.2, 9.2), (191.2, 12.5), (198, 12.5), (198, 9.2)], 'fosf', n=24)
    parte('tampa_guarda_mao', [t, t2], pai=pai, grupo='B')


# ------------------------------------------------------------------ alça de transporte
def alca_transporte():
    base = extr([(-14.2, 22.6), (-14.2, 38), (14.2, 38), (14.2, 22.6), (11.0, 22.6), (11.0, 30.25),
                 (-11.0, 30.25), (-11.0, 22.6)], -196, -8, 'anod', plane='wv')
    bevel(base, 0.7, 1)
    arc = extr([(-6, 37.5), (-6, 51.5), (-8.5, 56.5), (-14, 59), (-150, 59), (-150, 37.5)], -7, 7, 'anod')
    cut(arc, [extr(ret_arred(-142, -23, 30, 50.5, 5, 4), -10, 10, 'anod'),
              box(-151, -30, 56.2, 61, -3.4, 3.4, 'anod')])
    bevel(arc, 1.3, 2)
    cx = extr([(-144, 37.5), (-144, 59), (-157, 68.5), (-190, 68.5), (-196, 60), (-196, 37.5)], -11.6, 11.6, 'anod')
    cut(cx, [box(-205, -171, 55, 80, -7.6, 7.6, 'anod'),
             box(-181.5, -150.5, 40.2, 46.2, -20, 20, 'anod'),
             pin(-182, 62, 2.6, -20, 20, 'anod')])
    bevel(cx, 0.9, 1)
    barra = bevel(box(-172, -30, 22.4, 29.6, -16.6, -14.0, 'anod'), 0.6, 1)
    a = parte('alca_transporte', [base, arc, cx, barra], origem=(-100, 30.25, 0), grupo='D')
    # abertura da alça de mira (folha rebatível em L)
    f = extr(ret_arred(-5.6, 5.6, 55.2, 69.5, 2.0, 3), -183.2, -180.8, 'fosf', plane='wv')
    cut(f, [cyl((-190, 62.6, 0), (-175, 62.6, 0), 1.7, 'fosf', n=14)])
    f2 = box(-180.9, -171.5, 55.2, 57.4, -5.6, 5.6, 'fosf')
    cut(f2, [cyl((-176, 50, 0), (-176, 60, 0), 2.7, 'fosf', n=14)])
    parte('alca_mira', [f, f2, pin(-182, 56.3, 1.2, -7.6, 7.6, 'inox', n=8)], origem=(-182, 56.3, 0), pai=a, grupo='D')
    parte('botao_deriva', [pin(-182, 62, 2.4, 7.6, 12, 'fosf', n=12),
                           pin(-182, 62, 8.6, 11.7, 18.5, 'serr', n=28, lobes=0.07),
                           pin(-182, 62, 5.5, 18.4, 19.4, 'fosf', n=16)], origem=(-182, 62, 11.7), pai=a, grupo='D')
    parte('tambor_elevacao', [cyl((-166, 40.5, 0), (-166, 45.9, 0), 14.4, 'serr', n=36, lobes=0.06),
                              cyl((-166, 38, 0), (-166, 40.5, 0), 6, 'fosf', n=16)],
          origem=(-166, 43.2, 0), pai=a, grupo='D')
    for i, u in enumerate((-48, -152)):
        parte(f'porca_alca_{i + 1}', [pin(u, 28, 9.6, -24, -16.6, 'serr', n=28, lobes=0.09),
                                      pin(u, 28, 6.5, -25.2, -23.9, 'fosf', n=16),
                                      pin(u, 28, 2.6, -16.7, -9, 'fosf', n=10)],
              origem=(u, 28, -16.6), pai=a, grupo='D')
    return a


# ------------------------------------------------------------------ carregador
def carregador():
    R, S0, LT = 300.0, 72.0, 178.0
    def quadro(s):
        if s <= S0:
            return Vector((-40.0, -22.0 - s)), Vector((1.0, 0.0))
        f = (s - S0) / R
        cu, cv = -40.0 + R, -22.0 - S0
        return Vector((cu - R * math.cos(f), cv - R * math.sin(f))), Vector((math.cos(f), math.sin(f)))
    meia = [(30.5, 0.0), (30.5, 2.2), (29.9, 3.0), (29.9, 8.6), (27.4, 11.2),
            (19.5, 11.2), (18.6, 10.3), (12.4, 10.3), (11.5, 11.2), (3.5, 11.2), (2.6, 10.3),
            (-5.4, 10.3), (-6.3, 11.2), (-14.5, 11.2), (-15.4, 10.3), (-19.6, 10.3), (-20.5, 11.2),
            (-27.4, 11.2), (-29.9, 8.6), (-29.9, 2.6), (-30.9, 2.0), (-30.9, 0.0)]
    sec = meia + [(x, -y) for (x, y) in reversed(meia[1:-1])]
    def anel(s, esc=0.0):
        c, e = quadro(s)
        out = []
        for (x, y) in sec:
            x2 = x + math.copysign(esc, x)
            y2 = y + (math.copysign(esc, y) if abs(y) > 0.01 else 0)
            q = c + e * x2
            out.append(P(q.x, q.y, y2))
        return out
    ss = [0, 2] + [S0 * i / 3 for i in range(1, 4)] + [S0 + (LT - S0) * i / 12 for i in range(1, 13)]
    corpo = loft([anel(s) for s in ss], 'magal')
    cut(corpo, [box(-67.5, -12.5, -40, -10, -9.6, 9.6, 'magal'),               # boca
                box(-92, -64, -44.5, -36.5, -12, -9.9, 'magal')])               # entalhe do retém
    fundo = loft([anel(LT - 0.2, 0.0), anel(LT, 1.3), anel(LT + 2.2, 1.3), anel(LT + 3.0, 0.4)], 'magal')
    m = parte('carregador', [corpo, fundo], origem=(-40, -22, 0), grupo='C')
    tr = bevel(extr([(-66.5, -40), (-66.5, -27.5), (-40, -26), (-13.5, -28), (-13.5, -40)], -9.4, 9.4, 'polim_claro'), 1.0, 1)
    parte('transportador', [tr], pai=m, grupo='C')
    for i, (w, v) in enumerate(((2.3, -21.6), (-2.6, -25.6))):
        cst = lathe([(0, 0), (0, 4.1), (0.6, 4.75), (1.6, 4.75), (2.0, 4.2), (2.9, 4.2), (3.4, 4.78),
                     (36.6, 4.5), (39.6, 3.2), (44.7, 3.2)], 'latao', n=16, c0=(-66.0, v, w))
        bal = lathe([(44.7, 2.85), (49.5, 2.85), (54.0, 1.9), (56.6, 0.9), (57.3, 0)], 'cobre', n=16, c0=(-66.0, v, w))
        parte(f'cartucho_{i + 1}', [cst, bal], pai=m, grupo='C')
    return m


# ------------------------------------------------------------------ coronha
def coronha():
    tubo = lathe([(-197, 0), (-197, 14.6), (-391, 14.6), (-393, 13.4), (-393, 0)], 'anod_tubo', n=32)
    trilho = bevel(box(-391, -232, -21.5, -12, -4.8, 4.8, 'anod_tubo'), 0.6, 1)
    cut(trilho, [cyl((u, -25, 0), (u, -17, 0), 3.2, 'anod_tubo', n=12) for u in (-262, -290, -318, -346, -374)])
    t = parte('tubo_coronha', [tubo, trilho], origem=(-198, 0, 0), grupo='C')
    placa = extr(superelipse(16.5, 24.5, n=28, e=3.2, cy=-6), -216.6, -213.1, 'fosf', plane='wv')
    cut(placa, [cyl((-220, 0, 0), (-210, 0, 0), 14.7, 'fosf', n=28)])
    parte('placa_traseira', bevel(placa, 0.6, 1), pai=t, grupo='C')
    porca = lathe([(-229, 14.7), (-229, 18.2), (-224, 18.2), (-223.5, 19.8), (-216.7, 19.8), (-216.7, 14.7)],
                  'fosf', n=36, lobes=0.085, lobe_min=19, anel=True)
    parte('porca_castelo', porca, pai=t, grupo='C')

    # corpo da coronha (estendida)
    sec = arco(0, 0, 19.6, 0, 180, 12) + [(-19.6, -6), (-17.5, -30), (-14, -36.5), (14, -36.5), (17.5, -30), (19.6, -6)]
    U0, U1 = -270, -436
    luva = extr(sec, U1, U0, 'polim', plane='wv')
    cortes = [cyl((-405, 0, 0), (-260, 0, 0), 15.1, 'polim', n=28),
              box(-405, -260, -22.5, -8, -5.4, 5.4, 'polim')]
    for i in range(4):
        u = -283 - i * 26.5
        for s in (-1, 1):
            cortes.append(box(u - 22, u, -29, -10, s * 16.6, s * 26, 'polim'))
    for s in (-1, 1):
        cortes.append(box(-434, -396, 6, 12.5, s * 17.2, s * 26, 'polim'))
    cut(luva, cortes)
    bevel(luva, 1.1, 2, 35)
    alma = extr([(-300, -35), (-438, -35), (-440, -108), (-428, -108)], -4.2, 4.2, 'polim')
    cut(alma, [extr(ret_arred(-431, -401, -47, -41, 2.5, 3), -10, 10, 'polim')])        # passador da bandoleira
    bevel(alma, 0.6, 1)
    viga = bevel(extr([(-291, -35), (-312, -35), (-437, -101.5), (-437, -114.5), (-427, -114.5)], -8, 8, 'polim'), 1.6, 2)
    sol = extr([(-434, 19.6), (-446.5, 17), (-449.5, -114.5), (-434, -114.5)], -17.5, 17.5, 'polim')
    bevel(sol, 2.2, 2, 35)
    cut(sol, [box(-455, -445.5 + 0.0228 * (v - 17), v - 2.2, v, -14.5, 14.5, 'polim') for v in range(10, -108, -5)])
    bloco = bevel(box(-336, -296, -44, -35, -9, 9, 'polim'), 1.0, 1)
    c = parte('coronha', [luva, alma, viga, sol, bloco], origem=(-270, 0, 0), pai=t, grupo='C', suave=40)
    tr = bevel(extr([(-299, -44), (-344, -44), (-346, -47), (-333, -49.5), (-303, -52.5), (-298, -50)], -7.2, 7.2, 'polim'), 1.2, 2)
    parte('trava_coronha', [tr, cyl((-318, -52, 0), (-318, -25, 0), 3.0, 'fosf', n=12),
                            pin(-306, -46, 1.4, -9.3, 9.3, 'inox', n=8)], origem=(-306, -46, 0), pai=c, grupo='C')
    laco = caminho_arred([(-437, -112, -6), (-437, -112, -15), (-446, -133, -15), (-446, -133, 15),
                          (-437, -112, 15), (-437, -112, 6)], 3.5, 5)
    parte('zarelho_traseiro', [fio(laco, 1.7, 'fosf'), pin(-437, -112, 2.6, -9.4, 9.4, 'fosf', n=12)],
          origem=(-437, -112, 0), pai=c, grupo='C')
    return t


def montar():
    sup = receptor_superior()
    for f in (impulsor, tampa_janela, ferrolho, alavanca_manejo):
        o = f()
        o.parent = sup
        import bpy
        bpy.context.view_layer.update()
        o.matrix_parent_inverse = sup.matrix_world.inverted()
    inf = receptor_inferior()
    controles(inf)
    punho(inf)
    c = cano()
    quebra_chamas(c)
    base_massa(c)
    guarda_mao(c)
    alca_transporte()
    carregador()
    coronha()
    return PARTES
