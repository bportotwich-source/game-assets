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
letreiro, _deitado, _ret_arred, _anel = R_.letreiro, R_._deitado, R_._ret_arred, R_._anel


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


FORMAS = {'estojo_diversos': estojo_diversos}
