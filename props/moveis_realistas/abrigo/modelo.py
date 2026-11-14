"""Máquina de lanches, colchão no chão, quadro de procurados e riscos de contagem de dias no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora são as dos
móveis antigos de props/mobilias (nenhum tem nó que abre). O quadro e os riscos são de parede: costas em z = 0.
O vidro da máquina é a malha vidro_frente, trocada pelo vidro transparente no gerar.py."""
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
at = _carregar('modelo_atendimento', 'atendimento')
_girar_z, _disco, _pino, _recado = at._girar_z, at._disco, at._pino, at._recado


# ---------------------------------------------------------------------------- MÁQUINA DE LANCHES
_PACOTES = ('salgadinho_1', 'salgadinho_2', 'salgadinho_3', 'chocolate_emb')


def _mola(x, y, z0, z1, r=28, voltas=7):
    pts = []
    for i in range(voltas * 6 + 1):
        a = 2 * math.pi * i / 6
        pts.append((x + r * math.cos(a), y + r + r * math.sin(a), z0 + (z1 - z0) * i / (voltas * 6)))
    return _fio(pts, 2.4, 'cromo', res=0)              # arame de seção baixa: são 25 molas


def maquina_lanches():
    X, Z0, Z1, H = 450, -400, 400, 1800
    V = 'azul_vending'
    rnd = random.Random(67)
    c = caixa(-X, X, 0, H, Z0, Z1, V, 8.0)
    cut(c, caixa(-X + 40, 210, 330, H - 60, Z0 + 60, Z1 + 10, V))            # vão da vitrine
    cut(c, caixa(-X + 60, 180, 90, 270, Z1 - 120, Z1 + 10, V))                # boca de retirada
    p = [c]
    p.append(caixa(-X + 40, 210, 330, H - 60, Z0 + 58, Z0 + 62, 'esmalte_preto'))   # fundo da vitrine
    for s in (-1, 1):
        xa, xb = (-X + 40, -X + 44) if s < 0 else (206, 210)
        p.append(caixa(xa, xb, 330, H - 60, Z0 + 60, Z1 - 10, 'esmalte_preto'))
    p.append(caixa(-X + 60, 180, 90, 94, Z1 - 120, Z1 - 10, 'esmalte_preto'))      # fundo da boca
    p.append(caixa(-X + 60, 180, 94, 104, Z1 - 100, Z1 - 30, 'salgadinho_2', 3.0))  # pacote que caiu e ficou
    p.append(caixa(-X + 50, 190, 175, 270, Z1 - 4, Z1 + 2, 'plastico_preto', 3.0))   # aba de empurrar
    for k in range(5):                                                         # prateleiras com molas e pacotes
        y = 380 + k * 270
        p.append(caixa(-X + 44, 206, y - 10, y, Z0 + 62, Z1 - 30, 'inox', 1.5))
        p.append(caixa(-X + 44, 206, y - 30, y, Z1 - 36, Z1 - 30, 'plastico_preto'))     # testeira com as etiquetas
        for i in range(5):
            x = -X + 85 + i * 120
            p.append(caixa(x - 18, x + 18, y - 26, y - 6, Z1 - 29.5, Z1 - 29, 'folha_sulfite'))
            p.append(letreiro(f'{chr(65 + k)}{i + 1}', 12, x, y - 22, Z1 - 28.8, 'tinta_preta'))
            p.append(_mola(x, y, Z0 + 80, Z1 - 50))
            sobra = rnd.random()
            if sobra < 0.3:                                                     # mola vazia: já saquearam
                continue
            m = rnd.choice(_PACOTES)
            n = 1 + int(sobra * 4)
            for j in range(n):
                z = Z1 - 90 - j * 75
                if m == 'chocolate_emb':
                    p.append(caixa(x - 45, x + 45, y + 4, y + 26, z - 25, z + 25, m, 3.0))
                else:
                    o = caixa(x - 48, x + 48, y + 4, y + 175, z - 22, z + 22, m, 16.0)
                    _mover(o, lambda a, b, cc: (a, b, z + (cc - z) * (1.0 - 0.6 * abs(b - y - 90) / 90)))   # pacote estufado no meio
                    p.append(o)
    # painel da direita: visor, teclado, moedeiro, devolução de troco
    p.append(caixa(220, X - 30, 330, H - 60, Z1 - 8, Z1 + 2, 'esmalte_preto', 3.0))
    p.append(caixa(250, X - 60, 1420, 1500, Z1 + 2, Z1 + 6, 'vidro_visor', 2.0))
    p.append(letreiro('SEM ENERGIA', 14, (250 + X - 60) / 2, 1452, Z1 + 6.2, 'tinta_preta'))
    for i in range(4):
        for j in range(3):
            x = 270 + j * 50
            y = 1340 - i * 50
            p.append(caixa(x, x + 36, y, y + 36, Z1 + 2, Z1 + 12, 'cromo', 3.0))
            p.append(letreiro('ABCD123456*#'[i * 3 + j], 14, x + 18, y + 11, Z1 + 12.2, 'tinta_preta'))
    p.append(caixa(300, 390, 1060, 1160, Z1 + 2, Z1 + 14, 'cromo', 4.0))     # moedeiro
    p.append(caixa(338, 352, 1080, 1140, Z1 + 14, Z1 + 15, 'esmalte_preto'))
    p.append(caixa(250, X - 60, 980, 1030, Z1 + 2, Z1 + 10, 'cromo', 3.0))    # aceitador de notas
    p.append(caixa(270, X - 80, 1000, 1008, Z1 + 10, Z1 + 11, 'esmalte_preto'))
    p.append(caixa(290, 400, 600, 680, Z1 + 2, Z1 + 30, 'cromo', 5.0))       # devolução do troco
    cut(p[-1], caixa(305, 385, 610, 665, Z1 + 10, Z1 + 40, 'cromo'))
    p.append(caixa(-X + 10, X - 10, H - 50, H - 10, Z1, Z1 + 3, 'luminoso', 1.0))  # faixa de cima
    p.append(letreiro('LANCHES', 34, 0, H - 44, Z1 + 3.2, 'tinta_preta'))
    p.append(caixa(-X + 30, X - 30, 0, 40, Z1 - 20, Z1 + 1, 'esmalte_preto', 2.0))  # rodapé
    for s in (-1, 1):                                                         # niveladores
        for z in (Z0 + 40, Z1 - 40):
            p.append(cil((s * (X - 40), 0, z), (s * (X - 40), 6, z), 20, 'borracha', n=10))
    # aro da vitrine e trincas do vidro (o vidro quebrado foi o caminho do saque)
    p.append(caixa(-X + 30, 220, 320, 340, Z1 - 2, Z1 + 12, V, 3.0))
    p.append(caixa(-X + 30, 220, H - 70, H - 50, Z1 - 2, Z1 + 12, V, 3.0))
    p.append(caixa(-X + 30, -X + 50, 340, H - 70, Z1 - 2, Z1 + 12, V, 3.0))
    p.append(caixa(200, 220, 340, H - 70, Z1 - 2, Z1 + 12, V, 3.0))
    cx, cy = -100, 1150
    for k in range(9):
        a = 2 * math.pi * k / 9 + rnd.uniform(-0.2, 0.2)
        L = rnd.uniform(140, 330)
        pts = [(cx, cy, Z1 + 6.5)]
        for t in (0.35, 0.7, 1.0):
            pts.append((cx + L * t * math.cos(a) + rnd.uniform(-12, 12), cy + L * t * math.sin(a) + rnd.uniform(-12, 12), Z1 + 6.5))
        pts = [(max(-X + 52, min(198, x)), max(345, min(H - 75, y)), z) for x, y, z in pts]
        p.append(_fio(pts, 0.9, 'vidro_caco', res=1))
    parte('maquina', p, origem=G(0, 0, 0), grupo='A')
    parte('vidro_frente', [caixa(-X + 50, 200, 340, H - 70, Z1 + 4, Z1 + 6, 'vidro_visor')], origem=G(0, 0, 0), grupo='B')


# ---------------------------------------------------------------------------- COLCHÃO NO CHÃO
def colchao_chao():
    rnd = random.Random(5)
    p = []
    for i, (x, z, a) in enumerate(((-200, -450, 0.04), (250, 500, -0.06), (50, 100, 0.1))):   # papelão aberto por baixo
        o = caixa(-450, 450, i * 2.5, i * 2.5 + 3, -600, 600, 'papelao', 1.0)
        _mover(o, lambda xx, yy, zz: (x + xx * math.cos(a) - zz * math.sin(a), yy, z + xx * math.sin(a) + zz * math.cos(a)))
        p.append(o)
        p.append(caixa(-30, 30, i * 2.5 + 3, i * 2.5 + 3.3, -500, 500, 'fita_crepe'))
        _mover(p[-1], lambda xx, yy, zz: (x + 300 * math.cos(a) + xx * math.cos(a) - zz * math.sin(a), yy, z + 300 * math.sin(a) + xx * math.sin(a) + zz * math.cos(a)))
    p.append(_fofo(-440, 440, 9, 165, -940, 940, 'colchao_chao', r=45.0, bojo=10.0, semente=2.0))   # colchão de solteiro velho
    p.append(q._coberta(-430, 430, -250, 820, 180, 130, 'cobertor_cinza', amp=14.0, semente=1.3, queda_pe=90))   # cobertor jogado por cima
    t = q._travesseiro(0, 0, 0, 290, 170, 55)
    for o in (t if isinstance(t, list) else [t]):
        _mover(o, lambda xx, yy, zz: (xx, 172 + yy, -700 + zz))
        p.append(o)
    # vela num pires e garrafa d'água ao lado da cabeceira
    p.append(_torno([(0, 0), (60, 0), (64, 6), (60, 10), (0, 8)], 'louca', 590, 0, -820, n=18))
    p.append(_torno([(0, 8), (20, 8), (20, 60), (14, 70), (0, 66)], 'vela', 590, 0, -820, n=12))
    p.append(_torno([(0, 8), (32, 8), (38, 12), (30, 13), (0, 13)], 'vela', 590, 0, -820, n=12))    # cera escorrida
    p.append(_fio([(590, 66, -820), (591, 78, -820)], 1.0, 'carvao', res=1))
    p.append(_torno([(0, 0), (36, 0), (38, 10), (38, 200), (30, 230), (14, 250), (14, 270), (0, 270)], 'pet', 630, 0, -560, n=14))
    p.append(_torno([(0, 270), (16, 270), (16, 285), (0, 285)], 'tampa_azul', 630, 0, -560, n=10))
    parte('colchao', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- QUADRO DE PROCURADOS
def _cartaz(rnd, k, z):
    """Cartaz de 240 x 330 centrado na origem: PROCURADO com rosto ou AVISO só de texto."""
    p = [caixa(-120, 120, -165, 165, z, z + 0.4, 'cartaz_velho')]
    zt = z + 0.6
    if k % 3:
        p.append(letreiro('PROCURADO', 26, 0, 120, zt, 'tinta_cartaz'))
        p.append(caixa(-70, 70, -50, 100, z + 0.4, z + 0.7, 'foto_meio'))
        p.append(_disco(0, 45, z + 0.7, z + 1.0, 26, 'foto_cabelo', n=16, sy=1.1))
        p.append(_disco(0, 38, z + 1.0, z + 1.3, 20, 'foto_pele', n=16, sy=1.2))
        for ex in (-7, 7):
            p.append(_disco(ex, 42, z + 1.3, z + 1.5, 2.6, 'foto_cabelo', n=8))
        o = _disco(0, -20, z + 0.7, z + 1.1, 46, 'foto_sombra', n=16, sy=0.7)
        cut(o, caixa(-80, 80, -110, -50, z, z + 3, 'foto_sombra'))
        p.append(o)
        p.append(letreiro(('SAQUE', 'ROUBO', 'FUGA', 'AGRESSÃO')[k % 4], 18, 0, -82, zt, 'vermelho_cartaz'))
        for j in range(3):
            w = rnd.uniform(140, 200)
            p.append(caixa(-w / 2, w / 2, -110 - j * 16, -106 - j * 16, z + 0.4, z + 0.6, 'tinta_cartaz'))
    else:
        p.append(letreiro('AVISO', 34, 0, 110, zt, 'vermelho_cartaz'))
        for i, l in enumerate(('TOQUE DE', 'RECOLHER', '20h', 'ATÉ NOVA', 'ORDEM')):
            p.append(letreiro(l, 22, 0, 60 - i * 36, zt, 'tinta_cartaz'))
        p.append(caixa(-90, 90, -130, -126, z + 0.4, z + 0.6, 'tinta_cartaz'))
        p.append(letreiro('DELEGACIA MUNICIPAL', 11, 0, -150, zt, 'tinta_cartaz'))
    return p


def quadro_procurados():
    X, H, Zc = 600, 900, 26
    N = 'nogueira_'
    rnd = random.Random(37)
    p = [caixa(-X + 30, X - 30, 30, H - 30, 0, Zc, 'cortica')]
    p.append(caixa(-X, X, 0, 30, 0, 38, N + 'x', 4.0))
    p.append(caixa(-X, X, H - 30, H, 0, 38, N + 'x', 4.0))
    p.append(caixa(-X, -X + 30, 30, H - 30, 0, 38, N + 'y', 4.0))
    p.append(caixa(X - 30, X, 30, H - 30, 0, 38, N + 'y', 4.0))
    for k in range(6):
        x = -400 + (k % 3) * 400 + rnd.uniform(-25, 25)
        y = 650 if k < 3 else 250
        z = Zc + 0.3 + (k % 2) * 1.8
        p += _girar_z(_cartaz(rnd, k, z), x, y, rnd.uniform(-0.05, 0.05))
        for dx in (-100, 100):                                              # tachinha em cada canto de cima
            p.append(_pino(x + dx, y + 150, z + 1.6, 'pino_vermelho'))
    p += _girar_z(_recado(rnd, Zc + 4.5, 120, 90), 470, 460, 0.08)         # recado colado por cima
    p.append(_pino(470, 495, Zc + 5.0, 'pino_azul'))
    p.append(caixa(-560, -440, 445, 465, Zc + 0.2, Zc + 0.5, 'fita_crepe'))  # restos de cartaz arrancado
    p.append(caixa(-555, -470, 420, 445, Zc + 0.2, Zc + 0.5, 'cartaz_velho'))
    parte('quadro', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- RISCOS DE CONTAGEM DE DIAS
def _risco(a, b, larg=6.0, z0=0.3, z1=1.2):
    """Traço de carvão da parede: tira fina que afina nas pontas."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * larg / 2, (x1 - x0) / L * larg / 2
    pts = [(x0 + nx * 0.4, y0 + ny * 0.4), (x0 + (x1 - x0) * 0.15 + nx, y0 + (y1 - y0) * 0.15 + ny), (x1 - (x1 - x0) * 0.15 + nx, y1 - (y1 - y0) * 0.15 + ny),
           (x1, y1), (x1 - (x1 - x0) * 0.15 - nx, y1 - (y1 - y0) * 0.15 - ny), (x0 + (x1 - x0) * 0.15 - nx, y0 + (y1 - y0) * 0.15 - ny), (x0 - nx * 0.4, y0 - ny * 0.4)]
    return frente(pts, z0, z1, 'risco_carvao')


def contagem_dias():
    rnd = random.Random(6)
    p = []
    for g in range(7):                                                      # sete grupos de cinco (o último incompleto): 33 dias
        x0 = -470 + (g % 4) * 240 + rnd.uniform(-8, 8)
        y0 = 300 if g < 4 else 100
        n = 4 if g < 6 else 3
        for k in range(n):
            x = x0 + k * 34 + rnd.uniform(-4, 4)
            p.append(_risco((x, y0 + rnd.uniform(-5, 5)), (x + rnd.uniform(-9, 9), y0 + 130 + rnd.uniform(-6, 6)), rnd.uniform(5, 8)))
        if g < 6:
            p.append(_risco((x0 - 18, y0 + 100 + rnd.uniform(-8, 8)), (x0 + 125, y0 + 25 + rnd.uniform(-8, 8)), 7, 1.4, 2.2))   # o corte passa por cima dos quatro
    p.append(letreiro('DIA 33', 50, 330, 30, 0.6, 'risco_carvao'))
    parte('riscos', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'maquina_lanches': maquina_lanches, 'colchao_chao': colchao_chao, 'quadro_procurados': quadro_procurados, 'contagem_dias': contagem_dias}
