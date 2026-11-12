"""Lunetas do jogo no nível de detalhe da M4A1: tubo de alumínio anodizado com ocular, anel de
aumento (nas de aumento variável), sela com torres de ajuste, sino da objetiva, dois anéis de
suporte e a base que abraça o trilho. Desenho próprio, sem marcas.

Uma função só (luneta) faz as seis, a partir das medidas de SPECS: cada uma mantém o comprimento,
a altura do eixo e a posição das lentes da luneta antiga, então o ponto `olho` e o encaixe no trilho
continuam valendo.

As duas lentes são uma peça separada (`lente`), planas e recuadas dentro do tubo: é por elas que o
jogo desenha o zoom (ver `optica` no catálogo).

Coordenadas em mm (lib.py da M4A1): u = para a frente, v = para cima, w = direita.
u = 0 no meio do suporte, v = 0 no topo do trilho.
"""
import math
from lib import *

REC = 6.0          # quanto cada lente fica recuada dentro do tubo
D = -30.25         # o perfil da base é o da M4A1, que tem o topo do trilho em v = 30,25

# uR/uF: pontas de trás e da frente; VC: altura do eixo; rt: raio do tubo; r_oc/r_ob: raio das lentes;
# oc: comprimento da ocular; sino: comprimento do sino da objetiva (0 = tubo reto);
# var: tem anel de aumento; torres: 'caca' (com tampa), 'tatica' (altas, expostas) ou 'baixa';
# lado: botão do lado esquerdo (paralaxe ou luz do retículo); aneis: onde ficam os dois anéis;
# base: 'mono' (uma base comprida) ou 'aneis' (cada anel com a sua); texto: gravação na base
SPECS = {
    'luneta_1_6':   dict(uR=-135, uF=130, VC=28, rt=15.0, r_oc=17.1, r_ob=12.4, oc=60, sino=0, var=True, torres='tatica', lado=True,
                         aneis=(-36, 36), base='mono', texto='1-6x24'),
    'luneta_3_9':   dict(uR=-175, uF=175, VC=34, rt=15.0, r_oc=17.1, r_ob=21.1, oc=62, sino=72, var=True, torres='caca', lado=True,
                         aneis=(-38, 38), base='aneis', texto='3-9x44'),
    'luneta_4x':    dict(uR=-140, uF=140, VC=28, rt=12.7, r_oc=14.6, r_ob=16.1, oc=52, sino=56, var=False, torres='caca', lado=False,
                         aneis=(-30, 30), base='aneis', texto='4x32'),
    'luneta_4x_22': dict(uR=-118, uF=118, VC=28, rt=9.6, r_oc=13.1, r_ob=11.8, oc=46, sino=44, var=False, torres='baixa', lado=False,
                         aneis=(-29, 29), base='aneis', texto='4x20'),
    'luneta_5_25':  dict(uR=-205, uF=205, VC=34, rt=17.0, r_oc=18.1, r_ob=22.8, oc=70, sino=90, var=True, torres='tatica', lado=True,
                         aneis=(-38, 38), base='mono', texto='5-25x56'),
    'luneta_besta': dict(uR=-105, uF=105, VC=28, rt=12.7, r_oc=13.1, r_ob=13.6, oc=42, sino=36, var=False, torres='baixa', lado=True,
                         aneis=(-28, 28), base='mono', texto='3x32'),
}


def _base(u0, u1, topo, porcas=2):
    """Base que abraça o trilho, com a barra de aperto e as porcas do lado esquerdo."""
    b = extr([(-14.2, 22.6 + D), (-14.2, topo), (14.2, topo), (14.2, 22.6 + D), (11.0, 22.6 + D), (11.0, 0.0), (-11.0, 0.0),
              (-11.0, 22.6 + D)], u0, u1, 'anod', plane='wv')
    bevel(b, 0.8, 1)
    o = [b, bevel(box(u0 + 3, u1 - 3, 22.4 + D, 29.6 + D, -16.4, -14.0, 'anod'), 0.5, 1)]
    for i in range(porcas):
        u = u0 + (u1 - u0) * (i + 0.5) / porcas
        o.append(pin(u, 27.5 + D, 5.4, -21.5, -16.3, 'fosf', n=6))
        o.append(pin(u, 27.5 + D, 2.4, -23, -21.4, 'inox', n=10))
    return o


def _anel(u, vc, r_in, topo, larg=14.0):
    """Anel de suporte em duas metades, com quatro parafusos, e o pé que desce até a base."""
    o = [bevel(lathe([(u - larg / 2, r_in), (u - larg / 2, r_in + 4.2), (u + larg / 2, r_in + 4.2), (u + larg / 2, r_in)],
                     'anod', n=48, c0=(0, vc, 0), anel=True), 0.6, 1)]
    for s in (-1, 1):
        o.append(bevel(box(u - larg / 2, u + larg / 2, vc - 2.2, vc + 2.2, s * (r_in + 3), s * (r_in + 8.5), 'anod'), 0.6, 1))
        for du in (-3.5, 3.5):
            o.append(cyl((u + du, vc + 2.2, s * (r_in + 6)), (u + du, vc + 4.4, s * (r_in + 6)), 1.9, 'fosf', n=6))
    o.append(bevel(extr([(u - 7, topo - 0.5), (u + 7, topo - 0.5), (u + 6, vc - r_in - 2.5), (u - 6, vc - r_in - 2.5)], -8.5, 8.5, 'anod'), 0.8, 1))
    return o


def _torre(u, vc, eixo, r0, tipo):
    """Torre de ajuste saindo da sela na direção eixo = (dv, dw)."""
    dv, dw = eixo
    p = lambda d: (u, vc + dv * d, dw * d)
    if tipo == 'tatica':        # alta e exposta, com o tambor recartilhado
        return [cyl(p(r0 - 1), p(r0 + 4.5), 11.5, 'anod', n=28),
                cyl(p(r0 + 4.5), p(r0 + 6), 12.3, 'anod', n=28),
                cyl(p(r0 + 6), p(r0 + 17), 11.4, 'serr', n=40, lobes=0.055),
                cyl(p(r0 + 17), p(r0 + 18.4), 9.6, 'anod', n=24),
                cyl(p(r0 + 18.4), p(r0 + 19.0), 3.4, 'fosf', n=6)]
    if tipo == 'caca':          # baixa, com tampa de rosca
        return [cyl(p(r0 - 1), p(r0 + 3.5), 10.2, 'anod', n=28),
                cyl(p(r0 + 3.5), p(r0 + 11), 9.6, 'serr', n=36, lobes=0.045),
                cyl(p(r0 + 11), p(r0 + 12.2), 8.2, 'anod', n=24)]
    return [cyl(p(r0 - 1), p(r0 + 2.5), 8.2, 'anod', n=24),           # 'baixa': só o botão com fenda de moeda
            cyl(p(r0 + 2.5), p(r0 + 6.5), 7.4, 'serr', n=28, lobes=0.05),
            cyl(p(r0 + 6.5), p(r0 + 7.2), 5.6, 'fosf', n=20)]


def luneta(qual):
    s = SPECS[qual]
    uR, uF, VC, rt = s['uR'], s['uF'], s['VC'], s['rt']
    Roc = s['r_oc'] + 2.8                                   # raio de fora da ocular
    Rob = max(s['r_ob'] + 3.0, rt + (1.6 if s['sino'] == 0 else 0))
    u_oc = uR + s['oc']                                     # fim da ocular
    u_tubo = u_oc + (22 if s['var'] else 10)                # onde começa o tubo liso
    SELA = 13.0
    rs = rt + 3.6
    # corpo: de trás para a frente
    # (debaixo da borracha e dos anéis recartilhados o corpo é mais fino: uma superfície a menos de 1,4 mm
    # de outra por baixo assa manchada)
    prof = [(uR + REC, 0.0), (uR + REC, s['r_oc']), (uR, s['r_oc']), (uR, Roc - 1.8), (uR + 8.0, Roc - 1.8), (uR + 8.0, Roc),
            (uR + 9, Roc), (uR + 9.6, Roc - 1.1), (uR + 11.2, Roc - 1.1), (uR + 11.8, Roc),      # canal do anel de foco
            (u_oc - 23, Roc), (u_oc - 23, Roc - 2.2), (u_oc - 7, Roc - 2.2), (u_oc - 7, Roc), (u_oc - 5, Roc), (u_oc, Roc - 2.2)]
    if s['var']:
        prof += [(u_oc + 1.5, rt + 2.4), (u_oc + 16, rt + 2.4), (u_tubo - 1.5, rt + 2.2), (u_tubo, rt)]
    else:
        prof += [(u_tubo - 2, rt + 1.2), (u_tubo, rt)]
    prof += [(-SELA - 3, rt), (-SELA, rs), (SELA, rs), (SELA + 3, rt)]
    if s['sino']:
        ub = uF - s['sino']
        prof += [(ub, rt), (ub + s['sino'] * 0.42, Rob), (uF - 9, Rob), (uF - 8.4, Rob - 0.9), (uF - 7.2, Rob - 0.9), (uF - 6.6, Rob)]
    else:
        prof += [(uF - 44, rt), (uF - 42, Rob), (uF - 9, Rob), (uF - 8.4, Rob - 0.9), (uF - 7.2, Rob - 0.9), (uF - 6.6, Rob)]
    prof += [(uF - 0.8, Rob), (uF, Rob - 0.8), (uF, s['r_ob']), (uF - REC, s['r_ob']), (uF - REC, 0.0)]
    o = [lathe(prof, 'anod_tubo', n=64, c0=(0, VC, 0))]
    # borracha na borda da ocular e anel de foco rápido
    o.append(lathe([(uR - 0.6, s['r_oc'] + 0.6), (uR - 0.6, Roc + 0.3), (uR + 0.6, Roc + 1.0), (uR + 7.0, Roc + 1.0), (uR + 7.9, Roc + 0.1),
                    (uR + 7.9, s['r_oc'] + 0.6)], 'borracha', n=64, c0=(0, VC, 0), anel=True))
    o.append(lathe([(u_oc - 22, Roc - 2.0), (u_oc - 22, Roc + 1.0), (u_oc - 8, Roc + 1.0), (u_oc - 8, Roc - 2.0)], 'serr', n=64, c0=(0, VC, 0),
                   lobes=0.035, anel=True))
    if s['var']:                                            # anel de aumento, com a aleta
        o.append(lathe([(u_oc + 2.5, rt + 2.6), (u_oc + 2.5, rt + 5.4), (u_oc + 13.5, rt + 5.4), (u_oc + 13.5, rt + 2.6)], 'serr', n=64,
                       c0=(0, VC, 0), lobes=0.045, anel=True))
        o.append(bevel(box(u_oc + 4.5, u_oc + 11.5, VC + rt + 4.8, VC + rt + 11.5, -2.6, 2.6, 'anod'), 0.9, 1))
    # torres: elevação em cima, deriva à direita e, quando tem, o botão do lado esquerdo
    o += _torre(0, VC, (1, 0), rs, s['torres'])
    o += _torre(0, VC, (0, 1), rs, s['torres'])
    if s['lado']:
        o += _torre(0, VC, (0, -1), rs, 'tatica' if s['torres'] == 'tatica' else 'baixa')
    # suporte
    topo = 6.0
    a0, a1 = s['aneis']
    if s['base'] == 'mono':
        o += _base(a0 - 12, a1 + 12, topo, 3)
        ub = (a0 + a1) / 2
    else:
        for a in (a0, a1):
            o += _base(a - 10, a + 10, topo, 1)
        ub = a1
    for a in (a0, a1):
        o += _anel(a, VC, rt + 0.1, topo)
    o.append(texto(s['texto'], 2.8, ub, -3.6, 14.26, mat='tinta', lado=1))
    corpo = parte('luneta', o, origem=(0, 0, 0), grupo='A')
    # lentes: planas, no fundo do rebaixo de cada ponta
    lentes = [cyl((uR + REC + 0.5, VC, 0), (uR + REC - 0.3, VC, 0), s['r_oc'] - 0.05, 'lente', n=64),
              cyl((uF - REC - 0.5, VC, 0), (uF - REC + 0.3, VC, 0), s['r_ob'] - 0.05, 'lente', n=64)]
    parte('lente', lentes, origem=(0, 0, 0), grupo='A')
    return corpo


def optica(qual, aumento, reticulo='cruz', iluminado=False):
    """Campo "optica" do catálogo (metros, cano para -Z): onde ficam as lentes e o aumento."""
    s = SPECS[qual]
    return {'tipo': 'luneta', 'aumento': list(aumento), 'ocular_m': [0.0, s['VC'] / 1000, round(-(s['uR'] + REC - 0.3) / 1000, 4)],
            'raio_ocular_m': round((s['r_oc'] - 0.05) / 1000, 4), 'objetiva_m': [0.0, s['VC'] / 1000, round(-(s['uF'] - REC + 0.3) / 1000, 4)],
            'reticulo': reticulo, 'iluminado': iluminado}
