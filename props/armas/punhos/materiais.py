"""Classes de material dos punhos (somadas às da M4A1). VARIANTE=tan faz os caramelo."""
import os
import texturas
from texturas import _n, _math, _smooth, _noise

TAN = os.environ.get('VARIANTE', '') == 'tan'
_P = ((0.300, 0.205, 0.105), (0.440, 0.335, 0.205)) if TAN else ((0.021, 0.022, 0.022), (0.060, 0.060, 0.058))
_B = ((0.250, 0.170, 0.090), (0.380, 0.290, 0.180)) if TAN else ((0.014, 0.014, 0.014), (0.046, 0.046, 0.045))
# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'polim':         (_P[0], 0.60, 0.0, _P[1], 0.40, 0.0, 0.80, 1.00, 1.2),
    'polim_grip':    (_P[0], 0.60, 0.0, _P[1], 0.40, 0.0, 0.80, 1.00, 1.2),
    'polim_pontos':  (_P[0], 0.64, 0.0, _P[1], 0.42, 0.0, 0.80, 1.00, 1.5),
    'polim_fundo':   (tuple(c * 0.8 for c in _P[0]), 0.66, 0.0, _P[1], 0.44, 0.0, 0.60, 1.00, 1.6),
    'borracha_grip': (_B[0], 0.84, 0.0, _B[1], 0.66, 0.0, 0.70, 1.00, 1.7),
})


def pontos(nt, pos, geo):
    """Pontilhado fino: calotas de 1,1 mm em colmeia nos painéis dos lados."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    y, z = p.outputs['Y'], p.outputs['Z']
    passo = 0.0011
    lin = _math(nt, 'DIVIDE', z, passo * 0.866)
    par = _math(nt, 'MULTIPLY', _math(nt, 'FLOOR', _math(nt, 'MULTIPLY', _math(nt, 'FRACT', _math(nt, 'MULTIPLY', _math(nt, 'FLOOR', lin), 0.5)), 2.0)), 0.5)
    fx = _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'ADD', _math(nt, 'DIVIDE', y, passo), par)), 0.5)
    fy = _math(nt, 'SUBTRACT', _math(nt, 'FRACT', lin), 0.5)
    d = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', fx, fx), _math(nt, 'MULTIPLY', fy, fy)))
    cal = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, d, 0.12, 0.44))
    h = _math(nt, 'MULTIPLY', cal, 0.00045)
    return h, _math(nt, 'MULTIPLY', _smooth(nt, cal, 0.7, 0.95), 0.8), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, cal, 0.0, 0.3))


def pedrinhas(nt, pos, geo):
    """Borracha moldada com grão de pedrinhas (relevo arredondado e irregular de ~1 mm) em toda a volta."""
    g = _noise(nt, pos, 1500.0, 1.0, 0.4)
    ped = _smooth(nt, g, 0.38, 0.66)
    h = _math(nt, 'MULTIPLY', ped, 0.00042)
    return h, _math(nt, 'MULTIPLY', _smooth(nt, g, 0.60, 0.72), 0.55), _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, g, 0.30, 0.42)), 0.7)


texturas.RELEVO['polim_pontos'] = pontos
texturas.RELEVO['borracha_grip'] = pedrinhas
