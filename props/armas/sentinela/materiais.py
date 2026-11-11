"""Classes de material da Sentinela (somadas às da M4A1 em m4a1/texturas.py).
VARIANTE=tan, verde ou cinza troca a cor do polímero da armação e põe o cano dourado."""
import os
import texturas
from texturas import _n, _math, _smooth

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
POLIMERO = {
    '':      ((0.021, 0.022, 0.022), (0.060, 0.060, 0.058)),
    'tan':   ((0.300, 0.205, 0.105), (0.420, 0.320, 0.200)),
    'verde': ((0.062, 0.072, 0.036), (0.120, 0.135, 0.080)),
    'cinza': ((0.105, 0.110, 0.115), (0.200, 0.205, 0.210)),
}
VARIANTE = os.environ.get('VARIANTE', '')
_cor, _gasta = POLIMERO[VARIANTE]
texturas.CLASSES.update({
    'aco_sent':      ((0.034, 0.035, 0.035), 0.56, 0.70, (0.27, 0.27, 0.26), 0.34, 1.0, 1.40, 0.45, 1.2),   # aço nitretado preto
    'pol_sent':      (_cor, 0.62, 0.0, _gasta, 0.42, 0.0, 0.85, 1.00, 1.4),
    'pol_sent_grip': (_cor, 0.64, 0.0, _gasta, 0.42, 0.0, 0.85, 1.00, 1.6),
    'aco_cano':      ((0.060, 0.060, 0.062), 0.42, 0.90, (0.38, 0.38, 0.38), 0.28, 1.0, 0.90, 0.35, 0.7),
    'tinta_branca':  ((0.80, 0.80, 0.76), 0.60, 0.0, None, 0, 0, 0, 0, 0),
})
if VARIANTE:
    texturas.CLASSES['aco_cano'] = ((0.62, 0.42, 0.13), 0.34, 1.0, (0.70, 0.56, 0.30), 0.28, 1.0, 0.60, 0.25, 0.7)    # cano dourado


def pontilhado(nt, pos, geo):
    """Pontilhado do punho: pirâmides quadradas de 1,3 mm nos lados, na frente e nas costas,
    num painel de borda lisa (some perto do pé do punho, da armação e do apoio do polegar)."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    z = p.outputs['Z']
    masc = _math(nt, 'MULTIPLY', _smooth(nt, z, -0.1150, -0.1125), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, -0.0500, -0.0475)))
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    masc = _math(nt, 'MULTIPLY', masc, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['Z']), 0.25, 0.45)))
    passo = 0.0013
    # nos lados o padrão corre em Y e Z; na frente e nas costas, em X e Z
    lado = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.55, 0.75)
    a = _math(nt, 'ADD', _math(nt, 'MULTIPLY', p.outputs['Y'], lado), _math(nt, 'MULTIPLY', p.outputs['X'], _math(nt, 'SUBTRACT', 1.0, lado)))
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', a, passo)), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', z, passo)), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0008)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


texturas.RELEVO['pol_sent_grip'] = pontilhado
