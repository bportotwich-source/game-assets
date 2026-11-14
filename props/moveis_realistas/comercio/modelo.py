"""Freezer de sorvete com tampa de vidro, expositor de óleo de motor, relógio de ponto com cartões e empilhadeira no
nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós que
abrem (tampa_1 e tampa_2 do freezer, que correm de lado) são os dos móveis antigos de props/mobilias. O relógio de ponto
é de parede: costas em z = 0 e o pivô na altura de pendurar (vai de y = -250 a 550). Os vidros das tampas são malhas
filhas vidro_tampa_*, trocadas pelo vidro transparente no gerar.py. As marcas são inventadas."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro


def _carregar(nome, pasta):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', pasta, 'modelo.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


q = _carregar('modelo_quarto', 'quarto')
_torno, _fio = q._torno, q._fio
sala = _carregar('modelo_sala', 'sala')
_mover, _fofo = sala._mover, sala._fofo


def _anel(prof, mat, x=0, y=0, z=0, n=20, eixo=(0, 1, 0)):
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), anel=True)


def _redondo(x0, x1, y0, y1, r, n=4):
    """Contorno de retângulo de cantos redondos [(x, y)]."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
        pts += [(cx + r * math.cos(math.radians(a0 + 90 * k / n)), cy + r * math.sin(math.radians(a0 + 90 * k / n))) for k in range(n + 1)]
    return pts


# ---------------------------------------------------------------------------- FREEZER DE SORVETE
def _picole(x, y, z, cor, a=0.0, deitado=True):
    """Picolé com palito: deitado no fundo (de cima) ou estampado de pé na frente."""
    if deitado:
        o = planta(_redondo(-26, 26, -60, 50, 22), 0, 18, cor, 3.0)
        p = [o, caixa(-5, 5, 3, 7, -110, -55, 'faia_z')]
        for k in p:
            _mover(k, lambda xx, yy, zz: (x + xx * math.cos(a) - zz * math.sin(a), y + yy, z + xx * math.sin(a) + zz * math.cos(a)))
        return p
    return [frente(_redondo(x - 30, x + 30, y, y + 120, 26), z, z + 1.0, cor), caixa(x - 6, x + 6, y - 50, y + 2, z, z + 0.8, 'faia_y')]


def freezer_sorvete():
    X, Z0, Z1, H = 600, -330, 330, 820
    rnd = random.Random(12)
    c = caixa(-X, X, 60, H, Z0, Z1, 'esmalte_branco', 8.0)
    cut(c, caixa(-X + 45, X - 45, 170, H + 10, Z0 + 45, Z1 - 45, 'esmalte_branco'))
    p = [c]
    l = caixa(-X + 45, X - 45, 170, H - 2, Z0 + 45, Z1 - 45, 'liner_branco')
    cut(l, caixa(-X + 51, X - 51, 176, H + 10, Z0 + 51, Z1 - 51, 'liner_branco'))
    p.append(l)
    p.append(caixa(-X + 20, X - 20, 12, 60, Z0 + 20, Z1 - 30, 'plastico_preto', 3.0))
    for x in (-X + 60, X - 60):
        for z in (Z0 + 60, Z1 - 70):
            p.append(_torno([(0, 0), (18, 0), (18, 12), (0, 12)], 'plastico_preto', x, 0, z, n=12))
    p.append(caixa(-X - 4, X + 4, H, H + 30, Z0 - 2, Z1 + 2, 'plastico_azul', 5.0))                 # aro azul com os trilhos
    cut(p[-1], caixa(-X + 40, X - 40, H - 10, H + 40, Z0 + 40, Z1 - 40, 'plastico_azul'))
    # frente estampada
    p.append(caixa(-X + 20, X - 20, 200, 750, Z1, Z1 + 1.2, 'azul_vending'))
    p.append(letreiro('PICOLÉS', 70, 0, 640, Z1 + 1.4, 'letra_branca'))
    p.append(letreiro('e sorvetes de massa', 28, 0, 590, Z1 + 1.4, 'plastico_amarelo'))
    for k, cor in enumerate(('recheio_morango', 'plastico_amarelo', 'chocolate', 'plastico_verde', 'recheio_creme')):
        p += _picole(-400 + k * 200, 380, Z1 + 1.3, cor, deitado=False)
    p.append(caixa(-X + 20, X - 20, 250, 262, Z1 + 1.2, Z1 + 1.6, 'plastico_amarelo'))
    for k in range(14):                                                                              # grade do motor na lateral
        p.append(caixa(X - 0.5, X + 2.5, 80 + k * 8, 84 + k * 8, Z0 + 70, Z0 + 240, 'plastico_preto'))
    # dentro: água do que derreteu, caixas de picolé e potes
    p.append(caixa(-X + 52, X - 52, 176, 180, Z0 + 52, Z1 - 52, 'agua_vaso'))
    for k in range(5):
        x = -440 + k * 190 + rnd.uniform(-20, 20)
        o = caixa(-80, 80, 0, 70, -110, 110, ('pacote_azul', 'caixa_cereal', 'sacola')[k % 3], 6.0)
        a = rnd.uniform(-0.3, 0.3)
        _mover(o, lambda xx, yy, zz, x=x, a=a: (x + xx * math.cos(a) - zz * math.sin(a), 180 + yy, -40 + xx * math.sin(a) + zz * math.cos(a)))
        p.append(o)
    for k in range(9):
        p += _picole(rnd.uniform(-480, 480), 252 + rnd.uniform(0, 6), rnd.uniform(-200, 220), rnd.choice(('recheio_morango', 'plastico_amarelo', 'chocolate', 'plastico_verde')),
                     rnd.uniform(0, 6.28))
    for x in (-300, 330):
        p.append(_torno([(0, 0), (80, 0), (90, 110), (93, 118), (0, 118)], 'pote_sorvete', x, 180, 180, n=16))
    parte('freezer', p, origem=G(0, 0, 0), grupo='A')
    for nome, x0, x1, y in (('tampa_1', -X + 30, 15, H + 30), ('tampa_2', -15, X - 30, H + 44)):
        zf = Z1 - 8 if nome == 'tampa_2' else Z1 - 30                                             # a de cima sai mais à frente
        t = caixa(x0, x1, y, y + 13, Z0 + 24, zf, 'plastico_azul', 3.0)
        cut(t, caixa(x0 + 28, x1 - 28, y - 5, y + 20, Z0 + 52, Z1 - 52, 'plastico_azul'))
        px = (x1 - 70, x1 - 20) if nome == 'tampa_1' else (x0 + 20, x0 + 70)
        pux = caixa(px[0], px[1], y + 13, y + 16, -150, 150, 'plastico_preto', 1.0)
        tampa = parte(nome, [t, pux], origem=G(0, 0, 0), grupo='B')
        parte('vidro_' + nome, [caixa(x0 + 28, x1 - 28, y + 4, y + 8, Z0 + 52, Z1 - 52, 'vidro_visor')], origem=G(0, 0, 0), pai=tampa, grupo='B')


# ---------------------------------------------------------------------------- EXPOSITOR DE ÓLEO
def _frasco(x, y, z, mat, a=0.0, deitado=False):
    """Frasco de óleo de 1 litro: corpo de cantos redondos, bico de lado com tampa e rótulo na frente."""
    o = [planta(_redondo(-45, 45, -30, 30, 14, 2), 0, 170, mat),
         planta(_redondo(-45, 45, -30, 30, 14, 2), 170, 186, mat),
         cil((22, 186, 0), (22, 214, 0), 13, mat, n=8),
         cil((22, 214, 0), (22, 234, 0), 15, 'plastico_preto' if mat != 'frasco_oleo_3' else 'plastico_vermelho', n=8),
         caixa(-40, 40, 40, 140, 30, 31, 'rotulo')]
    for k in o:
        if deitado:
            _mover(k, lambda xx, yy, zz: (x + yy - 60, y + 30 + zz, z - xx))
        else:
            _mover(k, lambda xx, yy, zz: (x + xx * math.cos(a) - zz * math.sin(a), y + yy, z + xx * math.sin(a) + zz * math.cos(a)))
    return o


def expositor_oleo():
    V = 'esmalte_vermelho'
    rnd = random.Random(21)
    p = []
    for x in (-445, 445):
        for z in (-215, 215):
            p.append(caixa(x - 15, x + 15, 0, 1320, z - 15, z + 15, V, 2.0))
            p.append(caixa(x - 18, x + 18, 0, 10, z - 18, z + 18, 'plastico_preto'))
    for s in (-1, 1):                                                                                # travessas X nas laterais
        p.append(cil((s * 450, 60, -200), (s * 450, 1250, 200), 5, V, n=8))
        p.append(cil((s * 450, 60, 200), (s * 450, 1250, -200), 5, V, n=8))
    for k, y in enumerate((70, 380, 690, 1000)):
        p.append(caixa(-430, 430, y, y + 14, -215, 215, V, 2.0))
        p.append(caixa(-430, 430, y + 14, y + 60, 211, 219, V, 2.0))                                 # beirada da frente
        p.append(caixa(-300, 300, y + 22, y + 52, 219, 220, 'rotulo'))
        p.append(letreiro(('20W50', '15W40', '10W30', 'GALÃO 4 L')[3 - k], 22, 0, y + 28, 220.2, 'tinta_preta'))
    for k, y in enumerate((384, 694, 1004)):
        mat = ('frasco_oleo_1', 'frasco_oleo_2', 'frasco_oleo_3')[k]
        for fila, z in enumerate((-120, 100)):
            for j in range(8):
                if (k * 8 + j + fila * 3) % 11 == 5 or (fila == 1 and (j + k) % 5 == 0):            # vagas de frascos levados
                    continue
                p += _frasco(-370 + j * 105 + rnd.uniform(-4, 4), y, z + rnd.uniform(-6, 6), mat, rnd.uniform(-0.12, 0.12))
    p += _frasco(250, 1004, 150, 'frasco_oleo_4', deitado=True)
    for j in range(4):                                                                               # galões de 4 L embaixo
        if j == 2:
            continue
        x = -300 + j * 200
        g = planta(_redondo(-85, 85, -60, 60, 20, 2), 84, 360, 'frasco_oleo_4' if j % 2 else 'frasco_oleo_1')
        _mover(g, lambda xx, yy, zz, x=x: (x + xx, yy, 60 + zz))
        p += [g, cil((x + 45, 360, 60), (x + 45, 395, 60), 20, 'plastico_preto', n=10),
              caixa(x - 70, x - 20, 360, 372, 40, 80, 'plastico_preto', 3.0), caixa(x - 78, x + 78, 160, 300, 120, 121, 'rotulo')]
    p.append(_torno([(0, 0), (12, 0), (75, 110), (80, 116), (0, 116)], 'plastico_amarelo', -330, 84, -120, n=16))   # funil
    p.append(caixa(-465, 465, 1320, 1500, -12, 12, 'chapa_vermelha', 3.0))                           # placa do alto
    for zf, s in ((12, 1), (-12, -1)):
        p.append(caixa(-440, 440, 1335, 1485, zf, zf + s * 0.8, 'letra_branca'))
        p.append(caixa(-430, 430, 1345, 1475, zf + s * 0.8, zf + s * 1.2, 'chapa_vermelha'))
    p.append(letreiro('ÓLEO DE MOTOR', 62, 0, 1385, 13.3, 'letra_branca'))
    p.append(letreiro('TROCA RÁPIDA', 30, 0, 1350, 13.3, 'plastico_amarelo'))
    parte('expositor', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- RELÓGIO DE PONTO
def _porta_cartoes(x0, x1, rnd):
    p = [caixa(x0, x1, -250, 550, 0, 14, 'chapa_cinza', 3.0)]
    for k in range(10):
        y = -230 + k * 76
        p.append(perfil([(14, y), (60, y), (60, y + 34), (52, y + 34), (52, y + 8), (14, y + 8)], x0 + 12, x1 - 12, 'chapa_cinza', 1.0))   # bolso
        p.append(caixa((x0 + x1) / 2 - 22, (x0 + x1) / 2 + 22, y + 12, y + 26, 60, 60.6, 'letra_branca'))
        if rnd.random() < 0.78:                                                                      # cartão no bolso
            xc = (x0 + x1) / 2 + rnd.uniform(-20, 20)
            h = rnd.uniform(110, 140)
            c = caixa(xc - 42, xc + 42, y + 8, y + h, 34, 35.2, 'cartao_ponto')
            p.append(c)
            for j in range(3):
                p.append(caixa(xc - 34, xc + 34 - j * 12, y + h - 18 - j * 12, y + h - 16 - j * 12, 35.2, 35.6, 'tinta_cartaz'))
    return p


def relogio_ponto():
    rnd = random.Random(31)
    p = _porta_cartoes(-480, -190, rnd) + _porta_cartoes(190, 480, rnd)
    for x in (-470, -200, 200, 470):
        for y in (-240, 540):
            p.append(_torno([(0, 0), (6, 0), (5, 2), (0, 3)], 'aco_ferramenta', x, y, 14, n=8, eixo=(0, 0, 1)))
    # a máquina
    corpo = perfil([(0, -150), (150, -150), (175, -110), (175, 230), (150, 270), (0, 270)], -150, 150, 'bege_monitor', 6.0)
    cut(corpo, caixa(-70, 70, 150, 290, 60, 110, 'tinta_preta'))                                      # fenda do cartão em cima
    p.append(corpo)
    p.append(_anel([(108, 0), (118, 0), (118, 10), (108, 10)], 'cromo', 0, 70, 175, n=36, eixo=(0, 0, 1)))
    p.append(cil((0, 70, 174), (0, 70, 176), 108, 'mostrador', n=36))
    for k in range(12):
        a = math.radians(90 - k * 30)
        r0 = 84 if k % 3 else 76
        p.append(cil((r0 * math.cos(a), 70 + r0 * math.sin(a), 176), (96 * math.cos(a), 70 + 96 * math.sin(a), 176.5), 2.6 if k % 3 else 3.6, 'tinta_preta', n=6))
    for comp, ang, larg in ((55, 300, 4.5), (82, 162, 3.0)):                                          # ponteiros parados nas 5h50
        a = math.radians(90 - ang)
        p.append(caixa(-larg, larg, -8, comp, 177, 178.5, 'ponteiro'))
        _mover(p[-1], lambda xx, yy, zz, a=a: (xx * math.sin(a) + yy * math.cos(a), 70 - xx * math.cos(a) + yy * math.sin(a), zz))
    p.append(cil((0, 70, 176), (0, 70, 181), 7, 'tinta_preta', n=12))
    p.append(_anel([(108, 0), (110, 0), (110, 2), (108, 2)], 'vidro_visor', 0, 70, 186, n=36, eixo=(0, 0, 1)))
    p.append(caixa(-110, 110, -120, -40, 175, 178, 'tinta_preta', 2.0))                              # janela da data
    p.append(caixa(-100, 100, -110, -50, 178, 178.6, 'mostrador'))
    p.append(letreiro('SEX 14', 30, 0, -95, 178.8, 'tinta_preta'))
    p.append(caixa(-150, 150, 255, 262, 60, 110, 'cromo'))
    c = caixa(-40, 40, 150, 330, 82, 83.2, 'cartao_ponto')                                            # cartão enfiado na fenda
    p.append(c)
    for j in range(4):
        p.append(caixa(-34, 34 - j * 8, 300 - j * 10, 302 - j * 10, 83.2, 83.6, 'tinta_cartaz'))
    p.append(_torno([(0, 0), (12, 0), (12, 26), (18, 32), (0, 36)], 'plastico_vermelho', 130, -130, 160, n=12, eixo=(0, 0, 1)))   # chave
    p.append(caixa(-120, -60, -148, -140, 165, 175, 'chapa_cinza'))
    parte('relogio', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- EMPILHADEIRA
def _roda(x0, x1, y, z, R, aro):
    s = 1 if x1 > x0 else -1
    w = abs(x1 - x0)
    p = [_torno([(0, 0), (R - 20, 0), (R - 4, 6), (R, 20), (R, w - 20), (R - 4, w - 6), (R - 20, w), (0, w)], 'borracha', x0, y, z, n=32, eixo=(s, 0, 0))]
    for k in range(16):                                                                              # gomos do pneu
        a = 2 * math.pi * k / 16
        p.append(cil((x0 + s * 18, y + R * math.cos(a), z + R * math.sin(a)), (x0 + s * (w - 18), y + R * math.cos(a), z + R * math.sin(a)), 9, 'borracha', n=6))
    p.append(_torno([(0, 0), (aro, 0), (aro, 4), (aro * 0.6, 14), (0, 18)], 'amarelo_maquina', x1, y, z, n=20, eixo=(s, 0, 0)))
    for k in range(6):
        a = 2 * math.pi * k / 6
        p.append(cil((x1 + s * 10, y + aro * 0.5 * math.cos(a), z + aro * 0.5 * math.sin(a)), (x1 + s * 22, y + aro * 0.5 * math.cos(a), z + aro * 0.5 * math.sin(a)), 9, 'aco_polido', n=6))
    return p


def empilhadeira():
    A, F = 'amarelo_maquina', 'ferro_preto'
    p = []
    p += _roda(450, 600, 300, 640, 300, 190) + _roda(-450, -600, 300, 640, 300, 190)
    p += _roda(450, 580, 240, -800, 240, 150) + _roda(-450, -580, 240, -800, 240, 150)
    p.append(caixa(-450, 450, 130, 680, -1000, 900, A, 20.0))                                        # chassi
    p.append(planta([(-450, -720), (450, -720), (450, -1060), (380, -1140), (-380, -1140), (-450, -1060)], 130, 1050, F, 25.0))   # contrapeso
    for s in (-1, 1):
        p.append(caixa(s * 420 - 30, s * 420 + 30, 140, 700, 380, 900, A, 10.0))                      # para-lamas da frente
    p.append(caixa(-440, 440, 680, 860, -720, 260, A, 30.0))                                          # capô
    p.append(caixa(-300, 300, 860, 870, -560, -100, 'plastico_preto', 3.0))
    p.append(_fofo(-260, 260, 870, 960, -580, -150, 'banco_bici', 30, 12, 'y', 5, 1.0))               # banco
    p.append(_fofo(-250, 250, 940, 1340, -660, -580, 'banco_bici', 30, 12, 'z', 5, 2.0))
    p.append(caixa(-440, 440, 680, 1060, 260, 620, A, 25.0))                                          # painel
    p.append(caixa(-400, 400, 560, 580, 620, 900, 'chapa_cinza'))                                     # piso de pisar
    for k in range(10):
        p.append(caixa(-380, 380, 580, 584, 640 + k * 26, 650 + k * 26, 'chapa_cinza'))
    p.append(cil((0, 1000, 420), (0, 1220, 220), 22, F, n=12))                                        # coluna do volante
    ang = math.radians(40)
    vol = [(190 * math.cos(t), 1225 + 190 * math.sin(t) * math.sin(ang), 215 - 190 * math.sin(t) * math.cos(ang)) for t in [i * math.pi / 12 for i in range(24)]]
    p.append(_fio(vol, 16, 'plastico_preto', fechado=True, res=1))
    for t in (0, 2.1, 4.2):
        p.append(cil((0, 1225, 215), (180 * math.cos(t), 1225 + 180 * math.sin(t) * math.sin(ang), 215 - 180 * math.sin(t) * math.cos(ang)), 8, 'plastico_preto', n=8))
    for k in range(3):                                                                                # alavancas dos garfos
        p.append(cil((150 + k * 50, 1060, 330), (150 + k * 50, 1260, 390), 7, F, n=8))
        p.append(_torno([(0, 0), (16, 0), (18, 10), (16, 26), (0, 30)], 'plastico_preto', 150 + k * 50, 1255, 388, n=10))
    # proteção de cima
    for s in (-1, 1):
        p.append(cil((s * 410, 1040, -680), (s * 410, 2150, -620), 30, F, n=12))
        p.append(cil((s * 410, 1060, 560), (s * 410, 2150, 380), 30, F, n=12))
    p.append(_fio([(-410, 2160, -640), (410, 2160, -640), (410, 2160, 400), (-410, 2160, 400)], 32, F, fechado=True, res=0))
    for k in range(7):
        z = -520 + k * 140
        p.append(caixa(-400, 400, 2150, 2172, z - 20, z + 20, F, 3.0))
    p.append(_torno([(0, 0), (60, 0), (60, 20), (50, 30), (50, 90), (30, 110), (0, 115)], 'lata_laranja', -300, 2190, -560, n=16))   # giroflex
    for s in (-1, 1):
        p.append(_torno([(0, 0), (42, 0), (42, 50), (30, 56), (0, 56)], 'cromo', s * 410, 1960, 440, n=16, eixo=(0, 0, 1)))       # faróis
        p.append(cil((s * 410, 1960, 497), (s * 410, 1960, 499), 34, 'vidro_lampada', n=16))
    # botijão de gás deitado atrás
    p.append(_torno([(0, 0), (130, 0), (165, 40), (175, 100), (175, 700), (165, 760), (130, 800), (0, 800)], 'botijao', -400, 1240, -880, n=24, eixo=(1, 0, 0)))
    p.append(cil((400, 1240, -880), (440, 1240, -880), 20, 'latao', n=10))
    p.append(_fio([(440, 1240, -880), (470, 1140, -820), (430, 900, -700)], 9, 'mangueira', res=0))
    for x in (-250, 250):
        p.append(_anel([(178, 0), (186, 0), (186, 40), (178, 40)], F, x - 20, 1240, -880, n=24, eixo=(1, 0, 0)))
        p.append(caixa(x - 20, x + 20, 1050, 1080, -1000, -760, F))
    # torre (mastro) e garfos
    for s in (-1, 1):
        p.append(caixa(s * 300 - 40, s * 300 + 40, 100, 2500, 930, 1010, F, 3.0))
        p.append(caixa(s * 240 - 30, s * 240 + 30, 160, 2420, 945, 1000, F, 3.0))
        p.append(cil((s * 200, 900, 700), (s * 270, 1000, 940), 30, 'aco_polido', n=12))               # cilindros de inclinação
        p.append(cil((s * 200, 900, 700), (s * 200, 900, 620), 40, F, n=12))
        p.append(_fio([(s * 140, 2380, 1010), (s * 140, 2420, 990), (s * 140, 2400, 960), (s * 140, 500, 970)], 9, 'ferrugem', res=0))   # correntes
    for y in (180, 1300, 2460):
        p.append(caixa(-340, 340, y, y + 60, 940, 1000, F, 3.0))
    p.append(cil((0, 200, 970), (0, 1900, 970), 45, 'aco_polido', n=16))
    p.append(cil((0, 200, 970), (0, 1100, 970), 55, F, n=16))
    p.append(caixa(-520, 520, 80, 460, 1010, 1060, F, 4.0))                                           # carro dos garfos
    for x in range(-500, 501, 100):                                                                    # grade de encosto
        p.append(cil((x, 460, 1035), (x, 1250, 1035), 12, F, n=8))
    p.append(caixa(-520, 520, 1220, 1260, 1015, 1055, F, 3.0))
    for s in (-1, 1):
        p.append(caixa(s * 520 - 20, s * 520, 460, 1260, 1015, 1055, F, 3.0))
        x = s * 260
        p.append(caixa(x - 50, x + 50, 60, 520, 1060, 1100, F, 4.0))                                  # garfo: canela
        p.append(perfil([(1060, 30), (1850, 30), (1850, 40), (1100, 80), (1060, 80)], x - 50, x + 50, F, 3.0))
    parte('empilhadeira', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'freezer_sorvete': freezer_sorvete, 'expositor_oleo': expositor_oleo, 'relogio_ponto': relogio_ponto, 'empilhadeira': empilhadeira}
