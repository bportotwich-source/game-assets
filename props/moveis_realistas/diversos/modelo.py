"""Lixeira de rua com rodas, mala de viagem, aquecedor a óleo e desenho de criança no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós
que abrem (tampa) são os dos móveis antigos de props/mobilias; o desenho tem a parede em z = 0."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

_spec = importlib.util.spec_from_file_location('modelo_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'modelo.py'))
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
_torno, _fio, _malha, _travesseiro = q._torno, q._fio, q._malha, q._travesseiro
PV = 'plastico_verde'


def _roda(x, y, z, r, larg, eixo_x=True):
    """Roda de borracha com cubo, eixo ao longo de x."""
    s = 1 if x >= 0 else -1
    return [_torno([(0, 0), (r - 6, 0), (r, 6), (r, larg - 6), (r - 6, larg), (0, larg)], 'borracha', x, y, z, n=18, eixo=(s, 0, 0)),
            _torno([(0, -1), (r * 0.55, -1), (r * 0.55, larg + 1), (0, larg + 1)], 'plastico_preto', x, y, z, n=12, eixo=(s, 0, 0))]


def lixeira():
    W0, W1, D0, D1, H = 255, 295, 330, 370, 1000                            # meia-largura e meia-profundidade embaixo e em cima
    zc = 0
    def secao(y, w, d, r=40):
        pts = []
        for cx, cz, a0 in ((w - r, d - r, 0), (-w + r, d - r, 90), (-w + r, -d + r, 180), (w - r, -d + r, 270)):
            pts += [(cx + r * math.cos(math.radians(a0 + k * 30)), cz + r * math.sin(math.radians(a0 + k * 30))) for k in range(4)]
        return [(x, y, z) for x, z in pts]
    import bmesh
    bm = bmesh.new()
    aneis = []
    for y, w, d in ((70, W0, D0), (H - 60, W1, D1), (H - 60, W1 + 12, D1 + 12), (H - 20, W1 + 12, D1 + 12), (H - 20, W1 - 4, D1 - 4), (95, W0 - 14, D0 - 14)):
        aneis.append([bm.verts.new(lib.P(*G(*p))) for p in secao(y, w, d)])
    for a, b in zip(aneis, aneis[1:]):
        n = len(a)
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(aneis[0][::-1])
    bm.faces.new(aneis[-1])
    p = [lib._obj('lixeira', bm, PV)]
    for k in range(4):                                                      # nervuras verticais na frente e nos lados
        x = -150 + k * 100
        p.append(perfil([(D0 - 2, 80), (D1 - 2, H - 70), (D1 + 10, H - 70), (D0 + 6, 80)], x - 9, x + 9, PV, 2.0))
    p.append(perfil([(-D0 - 40, 0), (-D0 + 60, 0), (-D0 + 60, 210), (-D0 - 40, 210)], -W0 + 70, W0 - 70, PV, 8.0))   # caixa do eixo atrás
    p.append(cil((-245, 100, -D0 - 10), (245, 100, -D0 - 10), 11, 'zincado', n=10))
    p += _roda(-245, 100, -D0 - 10, 100, 55) + _roda(245, 100, -D0 - 10, 100, 55)
    p.append(cil((-W1 + 20, H - 40, -D1 - 45), (W1 - 20, H - 40, -D1 - 45), 16, PV, n=12))   # alça de puxar
    for s in (-1, 1):
        p.append(caixa(s * (W1 - 40) - 15, s * (W1 - 40) + 15, H - 90, H - 30, -D1 - 50, -D1 + 5, PV, 4.0))
    for s in (-1, 1):                                                       # pés da frente
        p.append(caixa(s * 190 - 30, s * 190 + 30, 0, 75, D0 - 70, D0 - 10, PV, 6.0))
    # saco de lixo saindo pela borda
    p.append(_travesseiro(0, H - 140, 10, 240, 260, 120, mat='saco_lixo', semente=3.0, n=14))
    parte('corpo', p, origem=G(0, 0, 0), grupo='A')
    t = [bevel(caixa(-W1 - 16, W1 + 16, H, H + 40, -D1 - 10, D1 + 60, PV), 10.0, seg=2)]
    cut(t[0], caixa(-W1 - 4, W1 + 4, H - 5, H + 28, -D1 + 2, D1 + 48, PV))
    t.append(caixa(-W1 + 10, W1 - 10, H + 39, H + 44, -D1 + 40, D1 - 20, PV, 2.0))     # tampo com nervura
    t.append(caixa(-140, 140, H + 10, H + 40, D1 + 50, D1 + 72, PV, 5.0))              # pega da frente
    for s in (-1, 1):
        t.append(cil((s * 180, H + 20, -D1 - 10), (s * 80, H + 20, -D1 - 10), 14, PV, n=10))   # dobradiças
    parte('tampa', t, origem=G(0, 1000, -360), grupo='B')


def mala_viagem():
    X, Z, HB, HT = 360, 230, 120, 126
    r = 30
    def casco(y0, y1, aberto_em_cima):
        o = bevel(caixa(-X, X, y0, y1, -Z, Z, 'mala_azul'), r, seg=4)
        cut(o, caixa(-X + 8, X - 8, y0 + 8 if aberto_em_cima else y0 - 1, y1 + 1 if aberto_em_cima else y1 - 8, -Z + 8, Z - 8, 'forro_mala'))
        return o
    p = [casco(0, HB, True), caixa(-X + 8, X - 8, 7, 9, -Z + 8, Z - 8, 'forro_mala')]
    for s in (-1, 1):                                                       # vivo de plástico e rodinhas
        xa, xb = sorted((s * (X - 2), s * (X + 4)))
        p.append(caixa(xa, xb, 2, HB - 2, -Z + 30, Z - 30, 'plastico_preto', 2.0))
    p.append(cil((X, 40, 0), (X + 22, 40, 0), 14, 'plastico_preto', n=12))  # alça lateral
    p.append(_fio([(X, 40, -70), (X + 24, 40, -60), (X + 30, 40, 0), (X + 24, 40, 60), (X, 40, 70)], 8, 'plastico_preto', res=1))
    # roupas dobradas dentro
    rnd = random.Random(2)
    for k, (x0, x1, mat) in enumerate(((-330, -120, 'jeans'), (-110, 100, 'roupa_cinza'), (110, 330, 'roupa_vermelha'))):
        for c in range(2 + k % 2):
            y = 10 + c * 30
            p.append(caixa(x0 + rnd.uniform(0, 8), x1 - rnd.uniform(0, 8), y, y + 28, -195 + rnd.uniform(0, 10), 195 - rnd.uniform(0, 10), mat, 12.0))
    parte('mala', p, origem=G(0, 0, 0), grupo='A')
    t = [casco(HB, HB + HT, False)]
    t.append(caixa(-X + 8, X - 8, HB + HT - 9, HB + HT - 7, -Z + 8, Z - 8, 'forro_mala'))
    t.append(bevel(caixa(-130, 130, HB + HT - 2, HB + HT + 6, -40, 40, 'plastico_preto'), 3.0, seg=1))      # alça de cima
    t.append(_fio([(-110, HB + HT + 4, 0), (-100, HB + HT + 36, 0), (100, HB + HT + 36, 0), (110, HB + HT + 4, 0)], 9, 'plastico_preto', fechado=False, res=1))
    for s in (-1, 1):                                                       # fechos de latão na frente
        t.append(caixa(s * 200 - 22, s * 200 + 22, HB - 20, HB + 24, Z - 1, Z + 8, 'latao', 2.0))
    t.append(caixa(-X + 20, X - 20, HB - 1, HB + 2, Z - 2, Z + 0.8, 'plastico_preto'))  # zíper na junção da frente
    parte('tampa', t, origem=G(0, HB, -Z), grupo='B')


def aquecedor():
    E = 'esmalte_branco'
    p = []
    n = 9
    for k in range(n):                                                      # elementos de óleo
        x = -176 + k * 44
        p.append(perfil([(-115, 130), (-120, 160), (-120, 560), (-110, 595), (0, 600), (110, 595), (120, 560), (120, 160), (115, 130)], x - 17, x + 17, E, 5.0))
        p.append(perfil([(-60, 160), (-62, 560), (62, 560), (60, 160)], x - 20, x + 20, E, 3.0))     # alma do elemento
    p.append(cil((-200, 150, 0), (200, 150, 0), 18, E, n=12))               # tubos de ligação
    p.append(cil((-200, 570, 0), (200, 570, 0), 14, E, n=12))
    p.append(caixa(200, 290, 220, 460, -70, 70, 'plastico_bege', 8.0))      # caixa de comando
    for y, mat in ((410, 'baquelite'), (300, 'baquelite')):
        p.append(_torno([(0, 0), (22, 0), (22, 3), (19, 16), (0, 18)], mat, 290, y, 0, n=16, eixo=(1, 0, 0)))
        p.append(caixa(296, 310, y - 3, y + 3, -15, 15, 'inox'))
    p.append(cil((290, 350, 40), (293, 350, 40), 5, 'ponteiro', n=8))       # luz piloto
    p.append(_fio([(290, 240, -50), (330, 200, -80), (360, 20, -120), (420, 4, -200)], 3.5, 'plastico_preto', fechado=False, res=1))   # fio
    for s in (-1, 1):                                                       # pés em cruz com rodinhas
        p.append(caixa(-150, 150, 60, 110, s * 115 - 18, s * 115 + 18, 'zincado', 4.0))
        for sx in (-1, 1):
            p.append(_torno([(0, 0), (25, 0), (28, 8), (28, 34), (25, 42), (0, 42)], 'plastico_preto', sx * 135, 30, s * 115, n=14, eixo=(1, 0, 0)))
    p.append(cil((0, 110, -100), (0, 140, -100), 14, 'zincado', n=8))
    p.append(cil((0, 110, 100), (0, 140, 100), 14, 'zincado', n=8))
    parte('aquecedor', p, origem=G(0, 0, 0), grupo='A')


def _traco(pts, mat, w=2.2, z=0.25):
    """Risco de giz de cera: fita plana ao longo dos pontos (x, y)."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l * w / 2, dx / l * w / 2
        out.append(frente([(x0 - nx, y0 - ny), (x1 - nx, y1 - ny), (x1 + nx, y1 + ny), (x0 + nx, y0 + ny)], 0.6 + z, 0.8 + z, mat))
    return out


def desenho_crianca():
    p = [frente([(-150, 0), (150, 3), (148, 220), (-149, 218)], 0, 0.6, 'folha_sulfite')]
    for x in (-125, 120):                                                   # fita crepe nos cantos de cima
        p.append(frente([(x - 26, 200), (x + 26, 208), (x + 24, 234), (x - 28, 226)], 0.6, 0.9, 'fita_crepe'))
    p.append(frente([(-150, 0), (150, 3), (150, 30), (-150, 28)], 0.65, 0.75, 'giz_verde'))      # grama
    p += _traco([(-150, 30), (-110, 34), (-60, 29), (0, 33), (60, 28), (110, 34), (150, 30)], 'giz_verde', 3.0)
    p.append(frente([(-125, 30), (-35, 30), (-35, 105), (-125, 105)], 0.65, 0.75, 'giz_amarelo'))   # casa
    p += _traco([(-125, 30), (-125, 105), (-35, 105), (-35, 30)], 'giz_marrom', 2.6)
    p.append(frente([(-135, 105), (-80, 150), (-25, 105)], 0.75, 0.85, 'giz_vermelho'))
    p.append(frente([(-92, 30), (-68, 30), (-68, 68), (-92, 68)], 0.85, 0.95, 'giz_marrom'))
    p += _traco([(-117, 75), (-100, 75), (-100, 92), (-117, 92), (-117, 75)], 'giz_azul', 2.0, 0.3)
    p.append(frente([(95 + 22 * math.cos(k * math.pi / 8), 180 + 22 * math.sin(k * math.pi / 8)) for k in range(16)], 0.65, 0.75, 'giz_amarelo'))   # sol
    for k in range(8):
        a = k * math.pi / 4 + 0.2
        p += _traco([(95 + 28 * math.cos(a), 180 + 28 * math.sin(a)), (95 + 42 * math.cos(a), 180 + 42 * math.sin(a))], 'giz_amarelo', 2.4)
    for (x, h, cor) in ((0, 1.0, 'giz_azul'), (45, 0.95, 'giz_vermelho'), (85, 0.6, 'giz_verde')):     # família de palitos
        cy = 30 + 95 * h
        p.append(frente([(x + 10 * math.cos(k * math.pi / 6), cy + 11 * math.sin(k * math.pi / 6)) for k in range(12)], 0.65, 0.75, 'giz_amarelo'))
        p += _traco([(x + 10 * math.cos(k * math.pi / 6), cy + 11 * math.sin(k * math.pi / 6)) for k in range(13)], 'giz_marrom', 1.6, 0.1)
        p += _traco([(x, cy - 11), (x, cy - 11 - 45 * h)], cor, 3.0)
        p += _traco([(x - 22 * h, cy - 22 * h), (x, cy - 18 * h), (x + 22 * h, cy - 22 * h)], cor, 2.4)
        p += _traco([(x - 14 * h, 34), (x, cy - 11 - 45 * h), (x + 14 * h, 34)], cor, 2.4)
    p += _traco([(-20, 175), (-10, 182), (0, 175)], 'tinta_preta', 1.4)      # passarinhos
    p += _traco([(20, 195), (30, 202), (40, 195)], 'tinta_preta', 1.4)
    parte('desenho', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'lixeira': lixeira, 'mala_viagem': mala_viagem, 'aquecedor': aquecedor, 'desenho_crianca': desenho_crianca}
