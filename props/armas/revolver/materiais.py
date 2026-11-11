"""Classes de material do revólver Vigia (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas
from texturas import _n, _math, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'azulado':       ((0.026, 0.030, 0.040), 0.36, 0.90, (0.30, 0.30, 0.31), 0.28, 1.0, 0.85, 0.20, 1.0),   # aço azulado, brilhante
    'nogueira':      ((0.070, 0.028, 0.012), 0.50, 0.0, (0.200, 0.095, 0.045), 0.42, 0.0, 0.60, 1.00, 1.6),
    'chumbo':        ((0.200, 0.200, 0.210), 0.55, 0.9, (0.34, 0.34, 0.35), 0.45, 1.0, 0.30, 0.50, 0.8),
    'tinta_laranja': ((0.90, 0.22, 0.02), 0.50, 0.0, None, 0, 0, 0, 0, 0),
})


def quadriculado(nt, pos, geo):
    """Quadriculado das talas de madeira: losangos de 1,6 mm na face de fora, com borda lisa
    e uma ilha lisa em volta do medalhão."""
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    masc = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.80, 0.95)
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    y, z = p.outputs['Y'], p.outputs['Z']
    masc = _math(nt, 'MULTIPLY', masc, _math(nt, 'MULTIPLY', _smooth(nt, z, -0.1090, -0.1065), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, -0.0460, -0.0435))))
    dy, dz = _math(nt, 'ADD', y, 0.0385), _math(nt, 'ADD', z, 0.058)
    dist = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', dy, dy), _math(nt, 'MULTIPLY', dz, dz)))
    masc = _math(nt, 'MULTIPLY', masc, _smooth(nt, dist, 0.0066, 0.0080))          # ilha lisa do medalhão
    passo = 0.0016
    a = _math(nt, 'MULTIPLY', z, 0.62)
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'ADD', a, y), passo)), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'SUBTRACT', a, y), passo)), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0009)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    # veio da madeira (riscos claros ao longo do cabo) onde não há quadriculado
    veio = _n(nt, 'ShaderNodeCombineXYZ')
    nt.links.new(_math(nt, 'MULTIPLY', p.outputs['X'], 7.0), veio.inputs[0])
    nt.links.new(_math(nt, 'MULTIPLY', _math(nt, 'ADD', y, _math(nt, 'MULTIPLY', z, 0.3)), 7.0), veio.inputs[1])
    nt.links.new(_math(nt, 'MULTIPLY', z, 0.5), veio.inputs[2])
    risco = _smooth(nt, _noise(nt, veio.outputs[0], 260.0, 4.0, 0.6), 0.42, 0.66)
    topo = _math(nt, 'MAXIMUM', topo, _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', risco, 0.8), _math(nt, 'SUBTRACT', 1.0, masc)))
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


texturas.RELEVO['nogueira'] = quadriculado
