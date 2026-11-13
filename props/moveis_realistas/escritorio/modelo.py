"""Mesa de escritório, rack com TV, TV de tubo e calendário de parede no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós
que abrem (gaveta; porta_esq) são os dos móveis antigos de props/mobilias."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
_torno, _fio = q._torno, q._fio
AC, PB, PP, TELA = 'aco_mesa', 'plastico_bege', 'plastico_preto', 'vidro_escuro'


def _girado(cx, cz, w, d, graus):
    """Retângulo w x d visto de cima, girado em volta do centro."""
    a = math.radians(graus)
    return [(cx + x * math.cos(a) - z * math.sin(a), cz + x * math.sin(a) + z * math.cos(a)) for x, z in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]


def mesa_escritorio():
    X, Z, T = 700, 350, 720
    p = [caixa(-X, X, T, T + 25, -Z, Z, 'formica', 2.5)]
    for s in (-1, 1):                                                       # pés de painel de aço
        xa, xb = sorted((s * 640, s * 665))
        p.append(caixa(xa, xb, 8, T, -330, 330, AC, 3.0))
        p.append(caixa(xa - 4, xb + 4, 0, 8, -335, -275, 'borracha'))
        p.append(caixa(xa - 4, xb + 4, 0, 8, 275, 335, 'borracha'))
    p.append(caixa(-640, 640, 300, T - 10, -332, -318, AC, 2.0))             # saia de trás
    c = caixa(140, 560, 515, T, -300, 335, AC, 2.0)                          # caixa da gaveta, pendurada no tampo
    cut(c, caixa(152, 548, 525, 716, -290, 345, AC))
    p.append(c)
    # monitor de tubo
    mx = -250
    p.append(_torno([(0, 0), (115, 0), (118, 6), (112, 14), (60, 22), (48, 30), (48, 52), (0, 52)], PB, mx, T + 25, -150, n=20))
    m = bevel(caixa(mx - 215, mx + 215, 795, 1140, -72, -40, PB), 8.0, seg=2)
    cut(m, caixa(mx - 180, mx + 180, 850, 1118, -52, -30, PB))
    p += [m, bevel(caixa(mx - 182, mx + 182, 848, 1120, -56, -50, TELA), 2.0, seg=1)]
    p.append(perfil([(-72, 800), (-72, 1135), (-250, 1085), (-340, 1010), (-340, 900), (-250, 815)], mx - 195, mx + 195, PB, 4.0))
    p.append(cil((mx + 150, 822, -40), (mx + 150, 822, -37), 9, PB, n=12))  # botão de ligar
    p.append(caixa(mx - 170, mx - 110, 815, 829, -40.5, -39.3, 'tecla'))     # etiqueta da marca (lisa)
    # teclado
    kx0, kx1, kz0, kz1 = -480, -40, 110, 270
    p.append(perfil([(kz0, T + 25), (kz1, T + 25), (kz1, T + 37), (kz0, T + 55)], kx0, kx1, PB, 2.0))
    for r in range(5):
        z0 = kz0 + 14 + r * 27
        y = T + 55 - (z0 - kz0 + 11) * 18 / (kz1 - kz0)
        nk = 14
        for k in range(nk):
            if r == 4 and 3 <= k <= 9:
                if k == 3:
                    p.append(caixa(kx0 + 14 + 3 * 29.5, kx0 + 14 + 9 * 29.5 + 25, y - 4, y + 5, z0, z0 + 22, 'tecla', 1.5))     # barra de espaço
                continue
            x0 = kx0 + 14 + k * 29.5
            p.append(caixa(x0, x0 + 25, y - 4, y + 5, z0, z0 + 22, 'tecla', 1.5))
    p.append(_fio([(-260, T + 30, 110), (-250, T + 28, 60), (-200, T + 28, 10), (-230, T + 28, -90)], 2.5, PB, res=1))
    # mouse e papéis
    p.append(q._mover(_torno([(0, 0), (30, 0), (32, 10), (26, 24), (12, 31), (0, 33)], PB, 0, 0, 0, n=12), lambda x, y, z: (30 + x, T + 25 + y, 200 + z * 1.7)) if hasattr(q, '_mover') else caixa(0, 60, T + 25, T + 55, 150, 250, PB, 8.0))
    rnd = random.Random(4)
    for k in range(4):
        p.append(planta(_girado(330 + rnd.uniform(-25, 25), 30 + rnd.uniform(-30, 30), 210, 297, rnd.uniform(-18, 18)), T + 25 + k * 0.8, T + 25.6 + k * 0.8, 'papel'))
    p.append(cil((520, T + 25, -200), (520, T + 120, -200), 38, 'latao_fosco', n=16))       # porta-lápis
    for k in range(4):
        a = k * 1.7
        p.append(cil((520 + 12 * math.cos(a), T + 60, -200 + 12 * math.sin(a)), (520 + 26 * math.cos(a), T + 185 + k * 8, -200 + 26 * math.sin(a)), 3.6, ('lapis', 'plastico_azul', 'lapis', 'tinta_preta')[k], n=6))
    parte('mesa', p, origem=G(0, 0, 0), grupo='A')
    g = [bevel(caixa(147, 553, 520, 718, 335, 353, AC), 3.0, seg=2)]         # gaveta
    for s in (-1, 1):
        xa, xb = sorted((350 + s * 194, 350 + s * 191.5))
        g.append(caixa(xa, xb, 536, 690, -280, 335, 'zincado'))
    g += [caixa(158.5, 541.5, 533, 536, -280, 335, 'zincado'), caixa(158.5, 541.5, 536, 690, -280, -277.5, 'zincado')]
    g.append(cil((290, 628, 366), (410, 628, 366), 6.0, 'inox', n=10))
    for s in (-1, 1):
        g.append(cil((350 + s * 50, 628, 353), (350 + s * 50, 628, 366), 4.5, 'inox', n=8))
    g.append(planta(_girado(330, 40, 210, 297, 8), 536, 548, 'papel'))        # resma, grampeador e pilhas
    g.append(caixa(190, 225, 536, 566, 150, 290, 'esmalte_vermelho', 4.0))
    for k in range(3):
        g.append(cil((470 + k * 17, 543.5, 200), (470 + k * 17, 543.5, 250), 7.2, 'cobre', n=8))
    parte('gaveta', g, origem=G(0, 0, 0), grupo='B')


def rack_tv():
    X, Z0, Z1 = 700, -210, 200
    N = 'nogueira_'
    c = bevel(caixa(-X, X, 80, 500, Z0, Z1, N + 'x'), 3.0, seg=2)
    cut(c, caixa(-680, -12, 100, 478, Z0 + 15, Z1 + 5, N + 'x'))
    cut(c, caixa(12, 680, 100, 478, Z0 + 15, Z1 + 5, N + 'x'))
    p = [c, caixa(12, 680, 282, 298, Z0 + 15, Z1 - 4, N + 'x', 1.0),          # prateleira do lado aberto
         caixa(-680, -12, 282, 298, Z0 + 15, Z1 - 30, N + 'x', 1.0)]
    for sx in (-1, 1):
        for sz in (-1, 1):                                                  # pés palito
            p.append(_torno([(0, 0), (13, 0), (14, 3), (22, 78), (26, 80), (0, 80)], N + 'y', sx * 620, 0, (Z1 - 50) if sz > 0 else (Z0 + 50), n=12))
    # aparelho de vídeo e fitas no lado aberto
    v = bevel(caixa(60, 480, 298, 388, -150, 160, PP), 3.0, seg=1)
    p += [v, caixa(90, 330, 340, 366, 160, 161.2, 'tinta_preta'), caixa(360, 450, 318, 334, 160, 161.2, 'vidro_escuro'),
          cil((270, 322, 160), (270, 322, 162), 3.0, 'ponteiro', n=8)]
    for k in range(3):
        p.append(cil((372 + k * 30, 356, 160), (372 + k * 30, 356, 164), 7, 'inox', n=10))
    rnd = random.Random(8)
    x = 40
    for k in range(9):                                                      # fitas em pé
        w = 26
        p.append(caixa(x, x + w, 100, 100 + 190 + rnd.uniform(-2, 2), -60 + rnd.uniform(-10, 10), 50, ('tinta_preta', 'cal_faixa', 'plastico_azul', 'papel')[rnd.randrange(4)], 1.5))
        x += w + rnd.uniform(1, 4)
    p.append(caixa(330, 520, 100, 126, -80, 110, 'papelao', 1.5))
    parte('rack', p, origem=G(0, 0, 0), grupo='A')
    # TV de tela plana em cima
    t = bevel(caixa(-500, 500, 585, 1180, -32, 16, PP), 6.0, seg=2)
    cut(t, caixa(-478, 478, 612, 1160, 8, 30, PP))
    tv = [t, caixa(-480, 480, 610, 1162, 4, 10, TELA), bevel(caixa(-330, 330, 660, 1080, -75, -32, PP), 12.0, seg=2),
          caixa(-45, 45, 512, 600, -40, -8, PP, 3.0), bevel(caixa(-220, 220, 500, 513, -115, 110, PP), 4.0, seg=2),
          cil((440, 598, 16), (440, 598, 17.2), 3.0, 'ponteiro', n=8)]
    parte('tv', tv, origem=G(0, 0, 0), grupo='B')
    d = bevel(caixa(-698, -22, 82, 496, Z1, Z1 + 20, N + 'x'), 4.0, seg=2)   # porta
    cut(d, q._anel(-698 + 45, -22 - 45, 82 + 45, 496 - 45, 6, Z1 + 17.5, Z1 + 24))
    parte('porta_esq', [d] + q._botao(-62, 290, Z1 + 20), origem=G(-700, 0, 220), grupo='B')


def tv_tubo():
    N = 'nogueira_'
    c = bevel(caixa(-330, 330, 40, 500, -200, 200, N + 'x'), 6.0, seg=2)
    cut(c, caixa(-306, 306, 64, 476, 186, 210, N + 'x'))
    p = [c]
    for sx in (-1, 1):
        for sz in (-1, 1):
            p.append(_torno([(0, 0), (14, 0), (15, 3), (22, 40), (0, 40)], N + 'y', sx * 280, 0, sz * 150, n=10))
    p.append(caixa(-304, 304, 66, 474, 184, 190, PP))                         # fundo do rebaixo
    m = bevel(caixa(-296, 146, 74, 466, 188, 204, PP), 5.0, seg=2)            # moldura da tela
    cut(m, caixa(-270, 120, 100, 440, 196, 210, PP))
    p += [m, bevel(caixa(-272, 122, 98, 442, 192, 201, TELA), 4.0, seg=2)]
    # trincas saindo do ponto da pancada
    rnd = random.Random(21)
    cx, cy = -95, 300
    p.append(frente([(cx + 11 * math.cos(a * 1.05), cy + 9 * math.sin(a * 1.05)) for a in range(6)], 201, 201.5, 'tinta_preta'))
    for k in range(9):
        a = k * 0.70 + rnd.uniform(-0.15, 0.15)
        x0, y0, w = cx + 9 * math.cos(a), cy + 8 * math.sin(a), 2.6
        for s in range(3):
            l = rnd.uniform(35, 70)
            a2 = a + rnd.uniform(-0.35, 0.35)
            x1, y1 = x0 + l * math.cos(a2), y0 + l * math.sin(a2)
            if not (-262 < x1 < 112 and 108 < y1 < 432):
                break
            nx, ny = -math.sin(a2), math.cos(a2)
            w1 = w * 0.6
            p.append(frente([(x0 - nx * w / 2, y0 - ny * w / 2), (x1 - nx * w1 / 2, y1 - ny * w1 / 2), (x1 + nx * w1 / 2, y1 + ny * w1 / 2), (x0 + nx * w / 2, y0 + ny * w / 2)], 201, 201.4, 'vidro_caco'))
            x0, y0, w = x1, y1, w1
    # painel de comando
    for y in (400, 315):
        p.append(_torno([(0, 0), (30, 0), (30, 3), (0, 3)], 'inox', 225, y, 190, n=20, eixo=(0, 0, 1)))
        p.append(_torno([(0, 0), (24, 0), (24, 3), (21, 16), (18, 20), (0, 20)], 'baquelite', 225, y, 193, n=16, eixo=(0, 0, 1)))
        p.append(caixa(223, 227, y + 4, y + 20, 212.5, 214.5, 'inox'))
    for k in range(9):                                                      # grade do alto-falante
        p.append(caixa(170, 280, 90 + k * 16, 98 + k * 16, 190, 191.5, 'tinta_preta'))
    p.append(cil((190, 255, 190), (190, 255, 197), 8, 'baquelite', n=10))
    p.append(cil((260, 255, 190), (260, 255, 197), 8, 'baquelite', n=10))
    p.append(perfil([(-200, 70), (-200, 450), (-330, 400), (-420, 330), (-420, 160), (-330, 100)], -260, 240, PP, 5.0))    # costas do tubo
    # antena
    p.append(_torno([(0, 0), (48, 0), (50, 5), (40, 22), (14, 28), (0, 28)], PP, 0, 500, 20, n=16))
    for sx, tip in ((-1, (-250, 848, -110)), (1, (258, 848, 215))):
        b = (sx * 10, 524, 20)
        p.append(cil(b, tip, 2.6, 'inox', n=6))
        p.append(_torno([(0, 0), (4.5, 1), (5.5, 5), (4.5, 9), (0, 10)], 'inox', tip[0], tip[1] - 5, tip[2], n=8))
    parte('tv', p, origem=G(0, 0, 0), grupo='A')


def calendario_parede():
    p = [caixa(-150, 150, 0, 414, 0, 2.6, 'cal_papel'),
         cil((-126, 409, 5), (126, 409, 5), 4.2, 'inox', n=8), caixa(-128, 128, 403, 415, 0, 5, 'inox'),
         cil((0, 450, 0), (0, 450, 20), 3.0, 'inox', n=8),
         _fio([(-60, 412, 6), (0, 449, 12), (60, 412, 6)], 0.9, 'inox', res=1)]
    z = 2.6
    p.append(caixa(-138, 138, 214, 394, z, z + 0.3, 'cal_ceu'))               # a foto do mês
    p.append(frente([(60 + 22 * math.cos(k * math.pi / 6), 345 + 22 * math.sin(k * math.pi / 6)) for k in range(12)], z + 0.3, z + 0.5, 'cal_sol'))
    p.append(frente([(-138, 214), (138, 214), (138, 265), (95, 300), (40, 272), (-10, 318), (-70, 280), (-138, 305)], z + 0.5, z + 0.7, 'cal_morro'))
    p.append(frente([(-138, 214), (138, 214), (138, 240), (70, 262), (0, 240), (-60, 258), (-138, 235)], z + 0.7, z + 0.9, 'cal_morro2'))
    p.append(caixa(-138, 138, 180, 208, z, z + 0.3, 'cal_faixa'))             # faixa do mês
    p.append(letreiro('OUTUBRO', 17, 0, 187, z + 0.4, 'cal_letra'))
    for k, d in enumerate('DSTQQSS'):
        p.append(letreiro(d, 10, -114 + k * 38, 160, z + 0.1, 'cal_faixa' if k == 0 else 'letra_preta'))
    for dia in range(1, 32):
        k = dia + 2                                                         # o dia 1 cai numa quarta
        col, lin = k % 7, k // 7
        p.append(letreiro(str(dia), 12, -114 + col * 38, 132 - lin * 27, z + 0.1, 'cal_faixa' if col == 0 else 'letra_preta'))
    k = 17 + 2
    cx, cy = -114 + (k % 7) * 38, 132 - (k // 7) * 27 + 5
    p.append(_fio([(cx + 14 * math.cos(a * math.pi / 8), cy + 12 * math.sin(a * math.pi / 8), z + 0.9) for a in range(16)], 0.9, 'ponteiro', fechado=True, res=1))
    for k in range(1, 17):                                                  # dias riscados antes do surto
        kk = k + 2
        x, y = -114 + (kk % 7) * 38, 132 - (kk // 7) * 27 + 5
        p.append(frente([(x - 10, y - 8), (x - 8.6, y - 9), (x + 10, y + 8), (x + 8.6, y + 9)], z + 0.5, z + 0.7, 'ponteiro'))
    parte('calendario', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'mesa_escritorio': mesa_escritorio, 'rack_tv': rack_tv, 'tv_tubo': tv_tubo, 'calendario_parede': calendario_parede}
