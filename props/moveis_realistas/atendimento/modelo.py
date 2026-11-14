"""Mural de desaparecidos, suporte de soro, banco de praça e balcão de recepção no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora são as dos
móveis antigos de props/mobilias (nenhum deles tem nó que abre). O mural é de parede: costas em z = 0."""
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
_mover = _carregar('modelo_sala', 'sala')._mover


def _girar_z(objs, cx, cy, a):
    """Gira no plano da parede (em volta de z) e leva o centro para (cx, cy)."""
    c, s = math.cos(a), math.sin(a)
    for o in objs:
        _mover(o, lambda x, y, z: (cx + x * c - y * s, cy + x * s + y * c, z))
    return objs


def _disco(x, y, z0, z1, r, mat, n=16, sy=1.0):
    """Disco de frente (eixo z), achatado em y por sy."""
    o = cil((x, 0, z0), (x, 0, z1), r, mat, n=n)
    _mover(o, lambda a, b, c: (a, y + b * sy, c))
    return o


# ---------------------------------------------------------------------------- MURAL DE DESAPARECIDOS
_FUNDOS = ('foto_azul', 'foto_verde', 'foto_bege', 'foto_meio')
_NOMES = ('ANA', 'JOÃO', 'LÍVIA', 'RAUL', 'TETÊ', 'CAIO', 'DONA LU', 'BETO', 'MAYARA', 'SEU ZÉ', 'NINA', 'PEDRO')


def _foto(rnd, k, z):
    """Foto 3x4 ampliada (95 x 125) colada numa folha com o nome escrito à mão, centrada na origem."""
    W, H = 60, 80
    p = [caixa(-W, W, -H - 40, H, z, z + 0.4, 'folha_sulfite')]
    p.append(caixa(-W + 8, W - 8, -H + 22, H - 8, z + 0.4, z + 0.8, 'foto_papel'))
    f = _FUNDOS[k % 4]
    p.append(caixa(-W + 13, W - 13, -H + 27, H - 13, z + 0.8, z + 1.1, f))
    cab = 'foto_loiro' if k % 5 == 2 else 'foto_cabelo'
    p.append(_disco(0, 22, z + 1.1, z + 1.4, 25, cab, n=18, sy=1.05))            # cabelo atrás da cabeça
    p.append(_disco(0, 16, z + 1.4, z + 1.7, 19, 'foto_pele', n=18, sy=1.2))      # rosto
    for ex in (-7, 7):                                                           # olhos e boca, para ler como rosto
        p.append(_disco(ex, 20, z + 1.7, z + 1.9, 2.6, 'foto_cabelo', n=8))
    p.append(caixa(-6, 6, 4, 6, z + 1.7, z + 1.9, 'foto_roupa'))
    p.append(_disco(0, 38, z + 1.7, z + 1.9, 17, cab, n=14, sy=0.45))           # franja por cima da testa
    o = _disco(0, -48, z + 1.1, z + 1.5, 36, 'foto_roupa' if k % 3 else 'foto_sombra', n=18, sy=0.8)   # ombros
    p.append(o)
    cut(o, caixa(-60, 60, -H + 26 - 60, -H + 27, z, z + 3, 'foto_roupa'))         # corta os ombros na borda da foto
    p.append(letreiro(_NOMES[k % len(_NOMES)], 15, 0, -H - 2, z + 0.5, 'caneta_azul'))
    for j in range(rnd.randint(1, 2)):                                           # "visto em..." em linhas de caneta
        w = rnd.uniform(50, 95)
        p.append(caixa(-w / 2, w / 2, -H - 20 - j * 10, -H - 17 - j * 10, z + 0.4, z + 0.6, 'caneta_azul'))
    return p


def _recado(rnd, z, w=130, h=95):
    p = [caixa(-w / 2, w / 2, -h / 2, h / 2, z, z + 0.4, 'recado')]
    for j in range(5):
        l = rnd.uniform(0.45, 0.85) * w
        y = h / 2 - 18 - j * 15
        p.append(caixa(-w / 2 + 10, -w / 2 + 10 + l, y, y + 3, z + 0.4, z + 0.6, 'caneta_azul'))
    return p


def _pino(x, y, z, mat):
    return _torno([(0, 0), (3, 0), (3, 3), (6, 4), (6, 10), (4, 12), (0, 12)], mat, x, y, z, n=10, eixo=(0, 0, 1))


def mural_desaparecidos():
    X, H, Zc = 600, 900, 26                                                     # meia largura, altura, face da cortiça
    N = 'nogueira_'
    p = [caixa(-X + 40, X - 40, 40, H - 40, 0, Zc, 'cortica')]
    p.append(caixa(-X, X, 0, 40, 0, 38, N + 'x', 4.0))                           # moldura
    p.append(caixa(-X, X, H - 40, H, 0, 38, N + 'x', 4.0))
    p.append(caixa(-X, -X + 40, 40, H - 40, 0, 38, N + 'y', 4.0))
    p.append(caixa(X - 40, X, 40, H - 40, 0, 38, N + 'y', 4.0))
    p.append(caixa(-300, 300, H - 125, H - 55, Zc, Zc + 0.5, 'folha_sulfite'))    # cabeçalho escrito à mão
    p.append(letreiro('DESAPARECIDOS', 44, 0, H - 108, Zc + 0.7, 'pino_vermelho'))
    p.append(caixa(-310, -250, H - 70, H - 50, Zc + 0.5, Zc + 0.8, 'fita_crepe'))
    p.append(caixa(250, 310, H - 70, H - 50, Zc + 0.5, Zc + 0.8, 'fita_crepe'))
    rnd = random.Random(23)
    LUG = [(-470, 600), (-330, 615), (-185, 590), (-40, 610), (110, 600), (255, 620), (400, 595),
           (-400, 330), (-250, 345), (-100, 325), (60, 340), (390, 330)]
    for k, (x, y) in enumerate(LUG):                                              # fotos sobrepostas em camadas
        z = Zc + 0.3 + (k % 3) * 2.2
        f = _girar_z(_foto(rnd, k, z), x, y, rnd.uniform(-0.10, 0.10))
        p += f
        p.append(_pino(x + rnd.uniform(-10, 10), y + 72, z + 2.0, 'pino_vermelho' if k % 3 else 'pino_azul'))
    for x, y, a in ((235, 330, 0.06), (-480, 120, -0.05), (-210, 120, 0.04), (90, 125, -0.07), (420, 110, 0.03)):
        z = Zc + 7.0
        p += _girar_z(_recado(rnd, z), x, y, a)
        p.append(_pino(x, y + 38, z + 0.5, 'pino_azul'))
    for x, y in ((-520, 450), (520, 470), (-60, 460), (300, 200), (-350, 210), (520, 220)):   # furos de tachinhas antigas e uma solta
        p.append(_pino(x, y, Zc, 'tacha') if rnd.random() < 0.6 else caixa(x - 1.5, x + 1.5, y - 1.5, y + 1.5, Zc - 0.3, Zc + 0.05, 'foto_sombra'))
    parte('mural', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- SUPORTE DE SORO
def suporte_soro():
    A = 'inox'
    p = []
    p.append(_torno([(0, 60), (38, 60), (42, 72), (42, 118), (30, 132), (0, 132)], 'plastico_preto', 0, 0, 30, n=20))   # cubo da base
    for k in range(5):                                                         # cinco pés com rodízio
        a = 2 * math.pi * k / 5 + 0.3
        c, s = math.cos(a), math.sin(a)
        ex, ez = 270 * c, 30 + 270 * s
        p.append(cil((32 * c, 100, 30 + 32 * s), (ex, 70, ez), 14, A, n=10, r1=10))
        p.append(cil((ex, 70, ez), (ex, 52, ez), 9, A, n=8))
        p.append(caixa(ex - 14, ex + 14, 40, 54, ez - 14, ez + 14, 'plastico_preto', 3.0))
        for sx in (-1, 1):                                                      # rodinha dupla
            p.append(_torno([(0, -5), (18, -5), (22, -2), (22, 2), (18, 5), (0, 5)], 'borracha', ex + sx * 9 * s, 22, ez - sx * 9 * c, n=14, eixo=(s, 0, -c)))
    p.append(cil((0, 125, 30), (0, 1250, 30), 13, A, n=14))                      # tubo de baixo
    p.append(_torno([(0, -30), (17, -30), (19, -20), (19, 20), (17, 30), (0, 30)], 'plastico_preto', 0, 1255, 30, n=16))   # trava da altura
    p.append(cil((0, 1255, 49), (0, 1255, 75), 5, A, n=8))
    p.append(_torno([(0, 0), (14, 0), (16, 6), (14, 14), (0, 14)], 'plastico_preto', 0, 1255, 75, n=12, eixo=(0, 0, 1)))
    p.append(cil((0, 1260, 30), (0, 1880, 30), 9, A, n=12))                      # tubo de cima
    p.append(_torno([(0, 0), (16, 0), (18, 10), (16, 22), (0, 24)], 'plastico_preto', 0, 1870, 30, n=14))
    for k in range(4):                                                         # quatro ganchos de cima
        a = math.pi / 2 * k
        c, s = math.cos(a), math.sin(a)
        p.append(_fio([(0, 1885, 30), (70 * c, 1905, 30 + 70 * s), (120 * c, 1915, 30 + 120 * s), (130 * c, 1940, 30 + 130 * s)], 3.5, A, res=2))
        p.append(_torno([(0, -6), (6, -3), (6, 3), (0, 6)], 'plastico_preto', 130 * c, 1944, 30 + 130 * s, n=8))
    # bolsa de soro de 500 ml pendurada no gancho da direita (o do +x)
    bx, bz = 120, 30
    p.append(caixa(bx - 6, bx + 6, 1845, 1915, bz - 2, bz + 2, 'bolsa_soro', 1.0))                     # aba com o furo
    b = _torno([(0, 0), (20, 0), (42, 25), (52, 120), (50, 210), (40, 240), (0, 245)], 'bolsa_soro', bx, 1600, bz, n=16)
    _mover(b, lambda x, y, z: (bx + (x - bx), 1600 + 1845 - y, bz + (z - bz) * 0.35))                  # de cabeça para baixo, achatada
    p.append(b)
    p.append(caixa(bx - 32, bx + 32, 1660, 1780, bz + 17.5, bz + 18, 'folha_sulfite'))                 # rótulo
    p.append(letreiro('SORO 0,9%', 9, bx, 1755, bz + 18.2, 'tinta_preta'))
    for j in range(5):
        p.append(caixa(bx - 26, bx + 26 - 8 * j, 1730 - j * 12, 1733 - j * 12, bz + 18, bz + 18.3, 'tinta_preta'))
    p.append(_torno([(0, 0), (5, 0), (5, -25), (0, -25)], 'pvc_branco', bx, 1600, bz, n=8))             # ponta e câmara de gotas
    p.append(_torno([(0, 0), (9, -4), (10, -55), (7, -62), (0, -64)], 'vidro_soro', bx, 1575, bz, n=12))
    p.append(_fio([(bx, 1511, bz), (bx + 10, 1350, bz + 20), (bx - 10, 1100, bz + 30), (40, 950, bz + 20), (14, 900, bz)], 2.2, 'borracha_soro', res=3))
    p.append(caixa(bx - 8, bx + 8, 1290, 1330, bz + 10, bz + 30, 'plastico_azul', 2.0))                # pinça de rolete
    p.append(caixa(8, 22, 880, 920, bz - 14, bz + 14, 'fita_crepe', 1.0))                               # equipo preso no tubo com esparadrapo
    p.append(_fio([(14, 880, bz), (60, 800, bz + 60), (110, 700, bz + 110), (170, 650, bz + 160)], 2.2, 'borracha_soro', res=3))
    parte('suporte', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- BANCO DE PRAÇA
def _barra(pts, w, x0, x1, mat):
    """Barra de ferro fundido seguindo a linha [(z, y)], com juntas arredondadas."""
    p = []
    for (za, ya), (zb, yb) in zip(pts, pts[1:]):
        dz, dy = zb - za, yb - ya
        L = math.hypot(dz, dy)
        nz, ny = -dy / L * w / 2, dz / L * w / 2
        p.append(perfil([(za + nz, ya + ny), (zb + nz, yb + ny), (zb - nz, yb - ny), (za - nz, ya - ny)], x0, x1, mat, 3.0))
    for z, y in pts[1:-1]:
        p.append(cil((x0 - 1.5, y, z), (x1 + 1.5, y, z), w / 2, mat, n=12))     # tampa um pouco para fora: não coincide com a face da barra
    return p


def _lado_banco(x):
    F = 'ferro_banco'
    x0, x1 = x - 18, x + 18
    p = []
    p += _barra([(250, 0), (235, 200), (215, 420)], 46, x0, x1, F)                      # pé da frente
    p += _barra([(-260, 0), (-225, 200), (-200, 420), (-250, 600), (-300, 760), (-330, 880)], 46, x0, x1, F)   # pé de trás que sobe no encosto
    p += _barra([(230, 410), (0, 418), (-205, 410)], 40, x0 + 3, x1 - 3, F)                     # braço do assento
    p += _barra([(-235, 520), (-120, 590), (60, 630), (200, 640), (255, 610), (262, 560), (240, 520)], 34, x0 - 4, x1 + 4, F)   # braço de apoio com voluta
    p.append(cil((x0 - 6, 520, 240), (x1 + 6, 520, 240), 22, F, n=12))
    p += _barra([(235, 200), (0, 230), (-225, 200)], 30, x0 + 3, x1 - 3, F)                     # travessa de baixo
    p.append(caixa(x0 - 6, x1 + 6, 0, 14, 210, 290, F, 3.0))                            # sapatas aparafusadas no chão
    p.append(caixa(x0 - 6, x1 + 6, 0, 14, -300, -220, F, 3.0))
    for z in (250, -260):
        p.append(_torno([(0, 0), (8, 0), (6, 6), (0, 7)], 'ferrugem', x, 14, z, n=8))
    return p


def banco_praca():
    L = 900
    W = 'praca_x'
    rnd = random.Random(9)
    p = _lado_banco(-750) + _lado_banco(750)
    for k in range(5):                                                         # ripas do assento
        zc = 165 - k * 90
        y0 = 422 + rnd.uniform(-1.5, 1.5)
        p.append(caixa(-L, L, y0, y0 + 32, zc - 38, zc + 38, W, 5.0))
        for x in (-750, 750):                                                   # cabeças dos parafusos
            p.append(_torno([(0, 0), (8, 0), (6, 3), (0, 4)], 'ferrugem', x, y0 + 32, zc, n=8))
    for k in range(3):                                                         # ripas do encosto, inclinadas
        y = 560 + k * 110
        z = -232 - k * 37
        o = caixa(-L, L, -45, 45, -16, 16, W, 5.0)
        a = math.radians(17)
        _mover(o, lambda xx, yy, zz: (xx, y + yy * math.cos(a), z + zz - yy * math.sin(a)))
        p.append(o)
        for x in (-750, 750):
            p.append(_torno([(0, 0), (8, 0), (6, 3), (0, 4)], 'ferrugem', x, y, z + 16, n=8, eixo=(0, -math.sin(a), math.cos(a))))
    # jornal velho esquecido no assento
    j = [caixa(-170, 170, 0, 4, -120, 120, 'jornal', 1.0), caixa(-160, 160, 4, 5, -110, 110, 'jornal')]
    for i in range(6):
        j.append(caixa(-140 + (i % 2) * 150, -20 + (i % 2) * 150, 5, 5.3, 80 - (i // 2) * 60, 95 - (i // 2) * 60, 'tinta_preta'))
    j.append(caixa(-150, 140, 5, 5.3, 100, 108, 'tinta_preta'))
    for o in j:
        _mover(o, lambda xx, yy, zz: (420 + xx * 0.94 - zz * 0.34, 455 + yy, 20 + xx * 0.34 + zz * 0.94))
    p += j
    parte('banco', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- BALCÃO DE RECEPÇÃO
def _painel(x0, x1, y0, y1, z, mat):
    """Painel almofadado: moldura em volta e almofada saltada no meio (sempre à frente da face)."""
    p = [caixa(x0, x1, y0, y0 + 50, z, z + 14, mat, 3.0), caixa(x0, x1, y1 - 50, y1, z, z + 14, mat, 3.0),
         caixa(x0, x0 + 50, y0 + 50, y1 - 50, z, z + 14, mat, 3.0), caixa(x1 - 50, x1, y0 + 50, y1 - 50, z, z + 14, mat, 3.0)]
    p.append(caixa(x0 + 70, x1 - 70, y0 + 70, y1 - 70, z, z + 10, mat, 6.0))
    return p


def _campainha(x, y, z):
    return [_torno([(0, 0), (40, 0), (42, 6), (40, 14), (0, 14)], 'ferro_preto', x, y, z, n=20),
            _torno([(0, 14), (36, 14), (34, 30), (26, 44), (12, 52), (0, 54)], 'cromo', x, y, z, n=20),
            _torno([(0, 54), (4, 54), (4, 62), (7, 66), (0, 68)], 'cromo', x, y, z, n=8)]


def balcao_recepcao():
    X, ZF, ZB = 1000, 500, 100                                                 # meia largura, frente e costas do balcão alto
    N = 'nogueira_'
    rnd = random.Random(13)
    p = [caixa(-X, X, 60, 1100, ZB, ZF, N + 'y', 4.0)]                          # corpo do balcão alto
    p.append(caixa(-X + 20, X - 20, 0, 60, ZB + 20, ZF - 30, 'ferro_preto', 2.0))   # rodapé recuado
    for i in range(4):                                                         # quatro painéis na frente
        x0 = -X + 30 + i * (2 * X - 60) / 4
        p += _painel(x0 + 10, x0 + (2 * X - 60) / 4 - 10, 110, 1030, ZF, N + 'y')
    for s in (-1, 1):                                                          # cantos com pilastra
        xa, xb = sorted((s * X, s * (X - 40)))
        p.append(caixa(xa, xb, 60, 1080, ZF, ZF + 22, N + 'y', 4.0))
    p.append(caixa(-X - 10, X + 10, 1060, 1100, ZB, ZF + 30, N + 'x', 6.0))    # cimalha
    p.append(caixa(-X - 30, X + 30, 1100, 1140, ZB - 20, ZF + 50, 'granito', 6.0))   # tampo de granito
    # mesa de trabalho do lado de dentro (mais baixa) com duas gavetas viradas para a parede
    p.append(caixa(-X, X, 0, 730, -250, ZB, N + 'y', 4.0))
    p.append(caixa(-X - 10, X + 10, 730, 760, -270, ZB, 'tampo_balcao', 4.0))
    for x in (-600, 600):
        p.append(caixa(x - 230, x + 230, 520, 700, -262, -250, N + 'x', 3.0))
        p.append(caixa(x - 50, x + 50, 600, 612, -272, -262, 'latao', 2.0))
    p.append(caixa(-350, 350, 0, 690, -251, -249.5, 'foto_sombra'))            # vão das pernas (sombra)
    # em cima da mesa de dentro: telefone, monitor velho, teclado e fichas
    p.append(caixa(-820, -620, 760, 820, -180, 0, 'bege_monitor', 8.0))
    p.append(caixa(-800, -640, 820, 880, -150, -30, 'bege_monitor', 12.0))
    tel = [caixa(-200, 0, 760, 830, -150, -10, 'plastico_preto', 10.0), caixa(-195, -5, 830, 870, -120, -40, 'plastico_preto', 14.0)]
    for i in range(12):                                                        # teclado do telefone, na rampa da frente
        x = -150 + (i % 3) * 40
        z = -100 + (i // 3) * 22
        tel.append(caixa(x, x + 30, 830, 833, z, z + 16, 'tecla', 1.0))
    tel[1] = caixa(-195, -5, 830, 870, -150, -110, 'plastico_preto', 14.0)      # fone deitado no gancho, atrás das teclas
    p += tel
    p.append(_fio([(-100, 790, -10), (-60, 770, 60), (20, 762, 40), (60, 800, -60)], 4, 'plastico_preto', res=3))   # fio enrolado do fone
    p.append(caixa(150, 600, 760, 1100 - 20, -240, 40, 'bege_monitor', 14.0))   # monitor de tubo
    cut(p[-1], caixa(190, 560, 820, 1060, 30, 60, 'bege_monitor'))
    p.append(caixa(195, 555, 825, 1055, 25, 30, 'vidro_escuro', 6.0))
    p.append(caixa(150, 600, 760, 775, 60, 90, 'bege_monitor', 3.0))           # fio do monitor esquecido
    for k in range(4):
        x = -500 + k * 70
        p.append(caixa(x, x + 60, 760 + k * 0.6, 760.5 + k * 0.6, -200 + rnd.uniform(-10, 10), -110, 'folha_sulfite'))
    # em cima do granito: campainha, livro de registro aberto, caneta presa na corrente, placa
    p += _campainha(520, 1140, 330)
    p.append(caixa(-560, -40, 1140, 1146, 220, 460, 'couro', 2.0))            # capa do livro
    for s in (-1, 1):
        xa, xb = (-300 + s * 4, -300 + s * 250) if s > 0 else (-300 - 250, -300 - 4)
        p.append(caixa(xa, xb, 1146, 1152 + (s + 1) * 1.5, 230, 450, 'papel_livro', 1.5))
        for j in range(9):                                                      # linhas de hóspedes
            w = rnd.uniform(120, 220)
            p.append(caixa(xa + 15, xa + 15 + w, 1152.3 + (s + 1) * 1.5, 1152.6 + (s + 1) * 1.5, 420 - j * 20, 423 - j * 20, 'caneta_azul'))
    p.append(cil((-20, 1160, 380), (-20, 1160, 260), 5, 'plastico_preto', n=8))
    p.append(_fio([(-20, 1160, 390), (-10, 1142, 430), (10, 1142, 470), (40, 1141, 500)], 1.2, 'latao', res=2))
    p.append(caixa(150, 410, 1140, 1145, 380, 470, 'latao', 1.0))              # placa de mesa
    p.append(caixa(160, 400, 1145, 1210, 445, 455, 'latao', 1.0))
    p.append(letreiro('RECEPÇÃO', 32, 280, 1165, 455.3, 'tinta_preta'))
    parte('balcao', p, origem=G(0, 0, 0), grupo='A')
    # quadro de chaves na parede de trás
    W, y0, ZQ = 600, 1200, -650
    k = [caixa(-W, W, y0, y0 + 785, ZQ, ZQ + 26, N + 'y', 5.0)]
    k.append(caixa(-W - 15, W + 15, y0 + 770, y0 + 800, ZQ, ZQ + 40, N + 'x', 6.0))
    k.append(letreiro('CHAVES', 40, 0, y0 + 735, ZQ + 26.3, 'latao'))
    for j in range(3):
        for i in range(8):
            x = -W + 75 + i * 150
            y = y0 + 640 - j * 230
            k.append(cil((x, y, ZQ + 26), (x, y, ZQ + 46), 3, 'latao', n=6))     # gancho
            k.append(letreiro(str(101 + j * 100 + i), 18, x, y + 15, ZQ + 26.3, 'latao'))
            if rnd.random() < 0.7:                                              # chave com chaveiro de madeira
                k.append(_fio([(x, y + 2, ZQ + 44), (x, y - 12, ZQ + 46)], 1.3, 'latao', res=1))
                k.append(caixa(x - 5, x + 5, y - 65, y - 14, ZQ + 44, ZQ + 46, 'latao', 0.8))
                k.append(caixa(x - 18, x + 18, y - 160, y - 65, ZQ + 40, ZQ + 54, N + 'y', 5.0))
                k.append(letreiro(str(101 + j * 100 + i), 13, x, y - 120, ZQ + 54.3, 'letra_branca'))
    parte('quadro_chaves', k, origem=G(0, 0, 0), grupo='B')


FORMAS = {'mural_desaparecidos': mural_desaparecidos, 'suporte_soro': suporte_soro, 'banco_praca': banco_praca, 'balcao_recepcao': balcao_recepcao}
