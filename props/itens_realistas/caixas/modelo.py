"""Caixas de itens do jogo (ocupam pouco na mochila e têm uma grade maior por dentro): caixas rígidas de
plástico moldado, de desenho próprio, sem marcas.

Coordenadas do jogo em mm (base.py dos móveis): x = largura, y = para cima, z = frente.
"""
import os, math, importlib.util
import lib
from lib import bevel, parte, pintar, MM
from base import G, caixa, cil, planta, perfil, frente

_spec = importlib.util.spec_from_file_location('modelo_remedios', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'remedios', 'modelo.py'))
R_ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R_)
letreiro, _deitado, _ret_arred, _anel, _cruz = R_.letreiro, R_._deitado, R_._ret_arred, R_._anel, R_._cruz


def _casco(HX, HZ, R, H, HT, mat, junta='plastico_preto', aba=5.0):
    """Corpo e tampa de caixa rígida: fundo recuado, parede com leve saída, aba grossa em volta da boca, junta
    de borracha e tampa com ombro. H = altura do corpo até a junta, HT = altura da tampa."""
    r = lambda d: _ret_arred(HX - d, HZ - d, max(2.0, R - d))
    a = [_anel(r(9), 0), _anel(r(6), 2), _anel(r(5), 8), _anel(r(3), H - 22),
         _anel(r(3), H - 20), _anel(r(-aba), H - 18), _anel(r(-aba), H - 2),               # aba da boca
         _anel(r(1.5), H - 1), _anel(r(1.5), H + 3),                                         # junta
         _anel(r(-aba), H + 4), _anel(r(-aba), H + 18), _anel(r(2), H + 20),               # aba da tampa
         _anel(r(3), H + HT - 12), _anel(r(7), H + HT - 3), _anel(r(14), H + HT)]
    cx = lib.loft(a, mat)
    pintar(cx, junta, lambda c, n: H - 1.2 < c[1] < H + 3.2)
    return cx


def _fecho(x, y, z, larg=44.0, alt=58.0, mat='caixa_grafite'):
    """Fecho de alavanca na frente (face em +z): base presa à tampa, alavanca que desce e morde a aba do corpo."""
    return [bevel(caixa(x - larg / 2, x + larg / 2, y - alt * 0.45, y + alt * 0.55, z, z + 7, mat), 2.0, 2),
            bevel(caixa(x - larg / 2 + 5, x + larg / 2 - 5, y - alt * 0.38, y + alt * 0.30, z + 7, z + 12, mat), 2.0, 2),
            caixa(x - larg / 2 + 9, x + larg / 2 - 9, y - alt * 0.30, y - alt * 0.12, z + 12, z + 13.2, 'plastico_preto'),
            cil((x - larg / 2 - 1, y + alt * 0.42, z + 6), (x + larg / 2 + 1, y + alt * 0.42, z + 6), 3.2, 'fecho_metal', n=10)]


def _alca_lateral(lado, HX, y, larg=120.0, mat='plastico_preto'):
    """Alça dobrável na lateral (lado = -1 esquerda, +1 direita): dois olhais e a barra caída."""
    x = lado * HX
    s = lado
    p = []
    for z in (-larg / 2, larg / 2):
        p.append(bevel(caixa(min(x, x + s * 14), max(x, x + s * 14), y - 2, y + 20, z - 9, z + 9, mat), 2.0, 2))
        p.append(cil((x + s * 9, y + 8, z), (x + s * 9, y - 34, z), 5.0, mat, n=10))
    p.append(cil((x + s * 9, y - 34, -larg / 2 - 4), (x + s * 9, y - 34, larg / 2 + 4), 7.5, mat, n=12))
    return p


# ------------------------------------------------------------------ caixa de itens diversos
def estojo_diversos():
    """Caixa rígida de tampa nervurada, do tamanho de uma caixa de ferramentas grande."""
    HX, HZ, R, H, HT = 250.0, 170.0, 30.0, 215.0, 70.0
    TOPO = H + HT
    cx = _casco(HX, HZ, R, H, HT, 'caixa_grafite')
    reforco = []
    for z, s, xs in ((HZ - 4, 1, (-196, 196)), (-HZ + 4, -1, (-150, 0, 150))):          # nervuras em pé: duas na frente (a etiqueta fica no meio), três atrás
        for x in xs:
            z0, z1 = (z, z + 9) if s > 0 else (z - 9, z)
            reforco.append(bevel(caixa(x - 16, x + 16, 10, H - 20, z0, z1, 'caixa_grafite'), 3.0, 2))
    for z in (-90, 90):                                                                  # e nas laterais
        for x, s in ((HX - 4, 1), (-HX + 4, -1)):
            x0, x1 = (x, x + 9) if s > 0 else (x - 9, x)
            reforco.append(bevel(caixa(x0, x1, 10, H - 78, z - 14, z + 14, 'caixa_grafite'), 3.0, 2))
    for sx in (-1, 1):                                                                   # cantoneiras de borracha nos quatro cantos da tampa
        for sz in (-1, 1):
            reforco.append(bevel(caixa(min(sx * (HX - 46), sx * (HX + 6)), max(sx * (HX - 46), sx * (HX + 6)), H + 6, H + 30,
                                       min(sz * (HZ - 46), sz * (HZ + 6)), max(sz * (HZ - 46), sz * (HZ + 6)), 'plastico_preto'), 7.0, 3))
    tampa = []
    for x in (-160, 0, 160):                                                             # três almofadas em relevo na tampa (empilhar)
        tampa.append(bevel(caixa(x - 62, x + 62, TOPO - 0.5, TOPO + 6, -HZ + 34, HZ - 34, 'caixa_grafite'), 2.5, 2))
        for z in (-70, 0, 70):
            tampa.append(caixa(x - 50, x + 50, TOPO + 6, TOPO + 7.4, z - 5, z + 5, 'plastico_preto'))   # frisos antiderrapantes
    fer = _fecho(-130, H + 2, HZ + 5) + _fecho(130, H + 2, HZ + 5)
    fer += _alca_lateral(-1, HX + 5, H - 30) + _alca_lateral(1, HX + 5, H - 30)
    for x in (-150, 150):                                                                # dobradiças atrás
        fer += [cil((x - 40, H + 1, -HZ - 8), (x + 40, H + 1, -HZ - 8), 6.0, 'caixa_grafite', n=12),
                cil((x - 46, H + 1, -HZ - 8), (x + 46, H + 1, -HZ - 8), 2.6, 'fecho_metal', n=8)]
    # alça de cima embutida, entre os fechos
    fer += [bevel(caixa(-62, 62, H + 22, H + 44, HZ + 2, HZ + 12, 'plastico_preto'), 4.0, 3),
            caixa(-46, 46, H + 28, H + 38, HZ + 1, HZ + 13, 'caixa_grafite')]
    # etiqueta de papel na frente, com o conteúdo escrito
    et = [caixa(-58, 58, 96, 150, HZ - 3.2, HZ - 2.2, 'etiqueta')]
    txt = [letreiro('DIVERSOS', 17, 0, 124, HZ - 2.0, mat='letra_preta'), letreiro('peças  ·  miudezas  ·  sobras', 6.2, 0, 107, HZ - 2.0, mat='letra_preta')]
    raiz = parte('caixa', [cx], origem=G(0, 0, 0), grupo='A', suave=45)
    parte('reforcos', reforco, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('tampa', tampa, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('ferragens', fer, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('etiqueta', et, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


def _dobradicas(xs, H, HZ, mat, larg=40.0):
    p = []
    for x in xs:
        p += [cil((x - larg, H + 1, -HZ - 8), (x + larg, H + 1, -HZ - 8), 6.0, mat, n=12),
              cil((x - larg - 6, H + 1, -HZ - 8), (x + larg + 6, H + 1, -HZ - 8), 2.6, 'fecho_metal', n=8)]
    return p


def _cruz_frente(x, y, z, t, mat, esp=0.5):
    """Cruz em pé numa face virada para a frente (+z), braço t."""
    a, b = t, t / 3.0
    return frente([(x - b, y - a), (x + b, y - a), (x + b, y - b), (x + a, y - b), (x + a, y + b), (x + b, y + b), (x + b, y + a), (x - b, y + a),
                   (x - b, y + b), (x - a, y + b), (x - a, y - b), (x - b, y - b)], z, z + esp, mat)


# ------------------------------------------------------------------ caixa de munição
def estojo_municao():
    """Caixa estreita e alta, verde oliva, com alça dobrável em cima e um fecho grande na ponta da frente."""
    HX, HZ, R, H, HT = 150.0, 88.0, 16.0, 168.0, 30.0
    TOPO = H + HT
    cx = _casco(HX, HZ, R, H, HT, 'caixa_oliva', aba=4.0)
    ref = []
    for z, s, xs in ((HZ - 4, 1, (-118, 118)), (-HZ + 4, -1, (-95, 0, 95))):             # nervuras nos lados compridos (na frente, só nas pontas: a etiqueta fica no meio)
        for x in xs:
            z0, z1 = (z, z + 7) if s > 0 else (z - 7, z)
            ref.append(bevel(caixa(x - 11, x + 11, 8, H - 20, z0, z1, 'caixa_oliva'), 2.5, 2))
    ref.append(bevel(caixa(-118, 118, TOPO - 0.5, TOPO + 4, -HZ + 22, HZ - 22, 'caixa_oliva'), 2.0, 2))   # almofada da tampa
    fer = _fecho(-80, H + 2, HZ + 4, larg=40, alt=54, mat='caixa_oliva') + _fecho(80, H + 2, HZ + 4, larg=40, alt=54, mat='caixa_oliva')
    fer += _dobradicas((-80, 80), H, HZ - 3, 'caixa_oliva', larg=30)
    for x in (-70, 70):                                                                  # alça de arame dobrada sobre a tampa
        fer += [bevel(caixa(x - 9, x + 9, TOPO + 4, TOPO + 15, -9, 9, 'fecho_metal'), 1.5, 2)]
    fer += [cil((-70, TOPO + 10, 0), (-70, TOPO + 10, 46), 3.2, 'fecho_metal', n=8), cil((70, TOPO + 10, 0), (70, TOPO + 10, 46), 3.2, 'fecho_metal', n=8),
            cil((-74, TOPO + 10, 46), (74, TOPO + 10, 46), 7.0, 'plastico_preto', n=12)]
    et = [caixa(-56, 56, 78, 128, HZ - 3.2, HZ - 2.2, 'rot_amarelo')]
    txt = [letreiro('MUNIÇÃO', 15, 0, 104, HZ - 2.0, mat='letra_preta'), letreiro('manter seco  ·  longe do fogo', 5.0, 0, 88, HZ - 2.0, mat='letra_preta')]
    raiz = parte('caixa', [cx], origem=G(0, 0, 0), grupo='A', suave=45)
    parte('reforcos', ref, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('ferragens', fer, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('etiqueta', et, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ caixa de armas
def estojo_armas():
    """Estojo comprido e baixo para arma longa: tampa com cinco réguas em relevo, quatro fechos e alça na frente."""
    HX, HZ, R, H, HT = 620.0, 190.0, 34.0, 78.0, 62.0
    TOPO = H + HT
    cx = _casco(HX, HZ, R, H, HT, 'caixa_verde', aba=6.0)
    ref = []
    for k in range(5):                                                                   # réguas de empilhar na tampa
        x = -480 + k * 240
        ref.append(bevel(caixa(x - 86, x + 86, TOPO - 0.5, TOPO + 7, -22, 22, 'caixa_verde'), 2.5, 2))
        ref.append(bevel(caixa(x - 86, x + 86, TOPO - 0.5, TOPO + 7, -HZ + 40, -HZ + 76, 'caixa_verde'), 2.5, 2))
        ref.append(bevel(caixa(x - 86, x + 86, TOPO - 0.5, TOPO + 7, HZ - 76, HZ - 40, 'caixa_verde'), 2.5, 2))
    for sx in (-1, 1):                                                                   # cantoneiras grossas nas quatro quinas, corpo e tampa
        for sz in (-1, 1):
            x0, x1 = sorted((sx * (HX - 70), sx * (HX + 8)))
            z0, z1 = sorted((sz * (HZ - 70), sz * (HZ + 8)))
            ref.append(bevel(caixa(x0, x1, 4, TOPO - 6, z0, z1, 'caixa_verde'), 12.0, 3))
    fer = []
    for x in (-470, -190, 190, 470):
        fer += _fecho(x, H + 2, HZ + 7, larg=48, alt=56, mat='caixa_verde')
    fer += _dobradicas((-420, 0, 420), H, HZ - 1, 'caixa_verde', larg=46)
    fer += [bevel(caixa(-78, 78, H - 34, H - 12, HZ + 6, HZ + 30, 'plastico_preto'), 6.0, 3),          # alça na frente, entre os fechos do meio
            bevel(caixa(-92, -70, H - 30, H - 4, HZ + 4, HZ + 16, 'caixa_verde'), 2.0, 2), bevel(caixa(70, 92, H - 30, H - 4, HZ + 4, HZ + 16, 'caixa_verde'), 2.0, 2)]
    for x in (-330, 330):                                                                # olhais de cadeado
        fer.append(bevel(caixa(x - 14, x + 14, H - 14, H + 16, HZ + 6, HZ + 12, 'fecho_metal'), 1.5, 2))
        fer.append(cil((x, H + 1, HZ + 5), (x, H + 1, HZ + 13), 5.0, 'plastico_preto', n=10))
    alto = lambda x, z: TOPO + 0.4
    txt = [_deitado('ARMAS', 30, 0, 118, alto, 'letra_branca')]
    raiz = parte('caixa', [cx], origem=G(0, 0, 0), grupo='A', suave=45)
    parte('reforcos', ref, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('ferragens', fer, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ maleta de remédios
def estojo_remedios():
    """Maleta rígida branca de socorro: cruz vermelha na tampa e na frente, três fechos e alça na frente."""
    HX, HZ, R, H, HT = 200.0, 160.0, 30.0, 100.0, 62.0
    TOPO = H + HT
    cx = _casco(HX, HZ, R, H, HT, 'caixa_branca', aba=5.0)
    ref = []
    for z in (-96, 96):                                                                  # duas réguas na tampa
        ref.append(bevel(caixa(-120, 120, TOPO - 0.5, TOPO + 6, z - 16, z + 16, 'caixa_branca'), 2.5, 2))
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, x1 = sorted((sx * (HX - 46), sx * (HX + 5)))
            z0, z1 = sorted((sz * (HZ - 46), sz * (HZ + 5)))
            ref.append(bevel(caixa(x0, x1, 4, TOPO - 5, z0, z1, 'caixa_branca'), 9.0, 3))
    est = [_cruz(0, TOPO + 0.2, 0, 52, 'letra_vermelha', esp=0.5), _cruz_frente(-128, 52, HZ - 2.6, 24, 'letra_vermelha')]
    fer = []
    for x in (-130, 0, 130):
        fer += _fecho(x, H + 2, HZ + 6, larg=36, alt=50, mat='fecho_metal')
    fer += _dobradicas((-110, 110), H, HZ - 2, 'caixa_branca', larg=34)
    fer += [bevel(caixa(-58, 58, 30, 50, HZ + 10, HZ + 30, 'plastico_preto'), 6.0, 3),
            bevel(caixa(-70, -52, 26, 56, HZ - 3, HZ + 16, 'fecho_metal'), 2.0, 2), bevel(caixa(52, 70, 26, 56, HZ - 3, HZ + 16, 'fecho_metal'), 2.0, 2)]
    et = [caixa(60, 170, 30, 74, HZ - 3.2, HZ - 2.2, 'lata')]                             # plaquinha de identificação
    txt = [letreiro('SOCORRO', 11, 115, 52, HZ - 2.0, mat='letra_preta'), letreiro('remédios  ·  curativos', 4.6, 115, 39, HZ - 2.0, mat='letra_preta')]
    raiz = parte('caixa', [cx], origem=G(0, 0, 0), grupo='A', suave=45)
    parte('reforcos', ref, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('estampa', est, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('ferragens', fer, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('etiqueta', et, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ bolsa térmica de comida
def estojo_comida():
    """Bolsa térmica de pano: corpo acolchoado, tampa com zíper em volta, bolso na frente, dois bolsos de garrafa
    nos lados e alça de ombro passada por cima."""
    HX, HZ, R, H = 190.0, 130.0, 34.0, 270.0
    r = lambda d: _ret_arred(HX - d, HZ - d, max(4.0, R - d))
    a = [_anel(r(12), 0), _anel(r(3), 6), _anel(r(-3), 60), _anel(r(-4), 150), _anel(r(-2), 214),      # corpo um pouco estufado
         _anel(r(0), 218), _anel(r(2.5), 219), _anel(r(2.5), 225), _anel(r(0), 226),                  # zíper da tampa
         _anel(r(-1), 250), _anel(r(4), H - 6), _anel(r(16), H)]
    cx = lib.loft(a, 'pano_azul')
    pintar(cx, 'ziper', lambda c, n: 218.6 < c[1] < 225.4)
    p = [bevel(caixa(-112, 112, 30, 168, HZ + 1, HZ + 30, 'pano_azul'), 12.0, 3),                      # bolso da frente
         caixa(-96, 96, 150, 156, HZ + 28, HZ + 31.5, 'ziper')]
    for sx in (-1, 1):                                                                   # bolsos de garrafa nos lados
        x0, x1 = sorted((sx * (HX + 1), sx * (HX + 30)))
        p.append(bevel(caixa(x0, x1, 20, 150, -70, 70, 'pano_cinza'), 12.0, 3))
    alca = []
    for sx in (-1, 1):                                                                   # alça de ombro: sobe pelos lados e deita na tampa
        x0, x1 = sorted((sx * (HX + 3), sx * (HX + 7)))
        alca.append(caixa(x0, x1, 150, 248, -22, 22, 'pano_cinza'))
        alca.append(bevel(caixa(sx * (HX + 2) - 9, sx * (HX + 2) + 9, 232, 258, -28, 28, 'fecho_metal'), 2.0, 2))   # argola
    alca.append(bevel(caixa(-HX - 4, HX + 4, H - 1, H + 5, -22, 22, 'pano_cinza'), 1.5, 2))
    alca.append(bevel(caixa(-70, 70, H + 4, H + 13, -30, 30, 'plastico_preto'), 4.0, 3))                # ombreira
    alca += [bevel(caixa(-60, 60, 232, 246, HZ - 2, HZ + 14, 'pano_cinza'), 4.0, 2)]                    # pegador da tampa
    et = [caixa(-52, 52, 70, 118, HZ + 30, HZ + 30.8, 'rot_branco')]
    txt = [letreiro('COMIDA', 15, 0, 94, HZ + 31.0, mat='letra_azul'), letreiro('mantém frio por 12 horas', 4.6, 0, 80, HZ + 31.0, mat='letra_azul')]
    raiz = parte('bolsa', [cx], origem=G(0, 0, 0), grupo='A', suave=50)
    parte('bolsos', p, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=45)
    parte('alca', alca, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=40)
    parte('etiqueta', et, origem=G(0, 0, 0), pai=raiz, grupo='A')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='A')
    return raiz


# ------------------------------------------------------------------ caixote enorme de madeira
def caixote_enorme():
    """Caixote de transporte de tábuas: sarrafos em pé, travessas em X entre eles, tampa de tábuas com
    réguas, dois fechos de alavanca de ferro e patins embaixo."""
    X, Z, E, Y0, Y1 = 560.0, 330.0, 20.0, 50.0, 500.0
    N = 5
    alt = (Y1 - Y0) / N
    p = []
    for k in range(N):                                                                   # tábuas deitadas nos quatro lados
        y0, y1 = Y0 + k * alt + 1.2, Y0 + (k + 1) * alt - 1.2
        for sz in (-1, 1):
            z0, z1 = sorted((sz * (Z - E), sz * Z))
            p.append(caixa(-X, X, y0, y1, z0, z1, 'pinho_x', 2.0))
        for sx in (-1, 1):
            x0, x1 = sorted((sx * (X - E), sx * X))
            p.append(caixa(x0, x1, y0, y1, -Z + E + 0.5, Z - E - 0.5, 'pinho_z', 2.0))
    p.append(caixa(-X + E, X - E, Y0, Y0 + E, -Z + E, Z - E, 'pinho_x'))                    # fundo
    sar = []
    for x in (-X + 40, -190, 190, X - 40):                                               # sarrafos em pé na frente e atrás
        for sz in (-1, 1):
            z0, z1 = sorted((sz * Z, sz * (Z + E)))
            sar.append(caixa(x - 40, x + 40, Y0 - 6, Y1 + 2, z0, z1, 'tampo_y', 2.5))
    for sx in (-1, 1):                                                                   # e nos lados
        x0, x1 = sorted((sx * X, sx * (X + E)))
        for z in (-Z + 40, Z - 40):
            sar.append(caixa(x0, x1, Y0 - 6, Y1 + 2, z - 40, z + 40, 'tampo_y', 2.5))
    for (xa, xb) in ((-X + 80, -230), (230, X - 80)):                                    # travessas inclinadas nos vãos de fora (frente e trás)
        for sz in (-1, 1):
            z0, z1 = sorted((sz * Z, sz * (Z + E - 2)))
            sobe = sz > 0
            ya, yb = (Y0 + 20, Y1 - 20) if (xa < 0) == sobe else (Y1 - 20, Y0 + 20)
            sar.append(frente([(xa, ya - 34), (xa, ya + 34), (xb, yb + 34), (xb, yb - 34)] if ya < yb else [(xa, ya + 34), (xb, yb + 34), (xb, yb - 34), (xa, ya - 34)][::-1],
                              z0, z1, 'pinho_x', 2.0))
    for x in (-X + 130, 0, X - 130):                                                     # patins
        sar.append(caixa(x - 50, x + 50, 0, Y0, -Z - 4, Z + 4, 'pinho_z', 4.0))
    YT = Y1 + 24
    tp = []
    for k in range(5):                                                                   # tampa: cinco tábuas ao comprido
        z0 = -Z - 12 + k * 136.8
        tp.append(caixa(-X - 14, X + 14, Y1 + 2, YT, z0, z0 + 134, 'tampo_x', 2.5))
    for x in (-X + 40, -190, 190, X - 40):                                               # réguas em cima da tampa, alinhadas com os sarrafos
        tp.append(caixa(x - 40, x + 40, YT, YT + E, -Z - 14, Z + 14, 'pinho_z', 2.5))
    fer = []
    for x in (-190, 190):                                                                # fechos de alavanca de ferro na frente
        fer += [caixa(x - 26, x + 26, YT + E, YT + E + 5, Z - 70, Z + E + 6, 'ferro_preto', 0.8),
                caixa(x - 26, x + 26, Y1 - 40, YT + E + 5, Z + E + 2, Z + E + 7, 'ferro_preto', 0.8),
                bevel(caixa(x - 20, x + 20, Y1 - 130, Y1 - 36, Z + E + 2, Z + E + 14, 'ferro_preto'), 2.0, 2),
                cil((x - 30, Y1 - 38, Z + E + 10), (x + 30, Y1 - 38, Z + E + 10), 6.0, 'ferro_preto', n=10)]
        for sz_ in (Z - 40, Z):
            fer.append(cil((x, YT + E + 5, sz_ - 10), (x, YT + E + 7, sz_ - 10), 6.0, 'ferro_preto', n=8, r1=4.0))
    for x in (-X + 40, X - 40):                                                          # dobradiças de cinta atrás
        fer += [caixa(x - 22, x + 22, YT + E, YT + E + 4, -Z - E - 6, -Z + 90, 'ferro_preto', 0.8),
                caixa(x - 22, x + 22, Y1 - 60, YT + E + 4, -Z - E - 6, -Z - E - 2, 'ferro_preto', 0.8),
                cil((x - 26, Y1 + 2, -Z - E - 6), (x + 26, Y1 + 2, -Z - E - 6), 7.0, 'ferro_preto', n=12)]
    for x in (-X + 40, -190, 190, X - 40):
        for y in (Y0 + 40, Y0 + 40 + alt, Y0 + 40 + 2 * alt, Y0 + 40 + 3 * alt, Y0 + 40 + 4 * alt):
            for dx in (-18, 18):
                fer.append(cil((x + dx, y, Z + E), (x + dx, y, Z + E + 1.8), 4.2, 'ferro_preto', n=8, r1=3.0))
    et = [caixa(X - 250, X - 110, Y1 - 130, Y1 - 40, Z + 0.2, Z + 1.2, 'etiqueta')]         # etiqueta de transporte
    txt = [letreiro('FRÁGIL', 20, X - 180, Y1 - 82, Z + 1.4, mat='letra_preta'), letreiro('este lado para cima', 9, X - 180, Y1 - 110, Z + 1.4, mat='letra_preta')]
    raiz = parte('caixote', p, origem=G(0, 0, 0), grupo='A', suave=35)
    parte('sarrafos', sar, origem=G(0, 0, 0), pai=raiz, grupo='A', suave=35)
    parte('tampa', tp, origem=G(0, 0, 0), pai=raiz, grupo='B', suave=35)
    parte('ferragens', fer, origem=G(0, 0, 0), pai=raiz, grupo='B', suave=40)
    parte('etiqueta', et, origem=G(0, 0, 0), pai=raiz, grupo='B')
    parte('letras', txt, origem=G(0, 0, 0), pai=raiz, grupo='B')
    return raiz


FORMAS = {'estojo_diversos': estojo_diversos, 'estojo_municao': estojo_municao, 'estojo_armas': estojo_armas,
          'estojo_remedios': estojo_remedios, 'estojo_comida': estojo_comida, 'caixote_enorme': caixote_enorme}
