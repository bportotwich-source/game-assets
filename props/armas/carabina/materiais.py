"""Classes de material da carabina Paciência .308 (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas
from texturas import _n, _math, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'areia':          ((0.300, 0.225, 0.130), 0.55, 0.0, (0.40, 0.40, 0.41), 0.32, 1.0, 0.90, 0.45, 1.3),     # pintura cerâmica areia sobre alumínio
    'polim_car_grip': ((0.021, 0.022, 0.022), 0.64, 0.0, (0.060, 0.060, 0.058), 0.42, 0.0, 0.85, 1.00, 1.6),
    'aco_cano':       ((0.040, 0.041, 0.044), 0.40, 0.90, (0.36, 0.36, 0.37), 0.28, 1.0, 1.00, 0.35, 0.8),
    'aco_polido':     ((0.300, 0.300, 0.295), 0.36, 1.00, (0.55, 0.55, 0.55), 0.28, 1.0, 0.50, 0.30, 1.0),    # ferrolho
    'azulado':        ((0.026, 0.030, 0.040), 0.36, 0.90, (0.30, 0.30, 0.31), 0.28, 1.0, 0.85, 0.20, 1.0),    # aço azulado da de caça
    'nogueira_car':   ((0.085, 0.034, 0.014), 0.42, 0.0, (0.210, 0.100, 0.048), 0.40, 0.0, 0.55, 1.00, 1.4),
    'tinta_vermelha': ((0.52, 0.030, 0.022), 0.50, 0.0, None, 0, 0, 0, 0, 0),
})
DV_CABO = 0.0095


def pontilhado(nt, pos, geo):
    """Pontilhado do punho: pirâmides quadradas de 1,3 mm nos lados, na frente e nas costas,
    num painel de borda lisa (some perto do pé do punho e do chassi)."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    z = p.outputs['Z']
    masc = _math(nt, 'MULTIPLY', _smooth(nt, z, -0.1470 + DV_CABO, -0.1445 + DV_CABO),
                 _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, -0.0625 + DV_CABO, -0.0600 + DV_CABO)))
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    masc = _math(nt, 'MULTIPLY', masc, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['Z']), 0.25, 0.45)))
    passo = 0.0013
    lado = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.55, 0.75)
    a = _math(nt, 'ADD', _math(nt, 'MULTIPLY', p.outputs['Y'], lado), _math(nt, 'MULTIPLY', p.outputs['X'], _math(nt, 'SUBTRACT', 1.0, lado)))
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', a, passo)), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', z, passo)), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0008)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


def _faixa(nt, x, a, b, borda=0.002):
    return _math(nt, 'MULTIPLY', _smooth(nt, x, a, a + borda), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, x, b - borda, b)))


def quadriculado(nt, pos, geo):
    """Nogueira da coronha de caça: quadriculado de losangos de 1,6 mm nos lados do punho e da telha
    (painéis de borda lisa) e veio comprido, ao longo da arma, no resto."""
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    lado = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.55, 0.80)
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    y, z = p.outputs['Y'], p.outputs['Z']
    telha = _math(nt, 'MULTIPLY', _faixa(nt, y, 0.172, 0.308), _faixa(nt, z, -0.031, -0.011))
    s = _math(nt, 'ADD', y, _math(nt, 'MULTIPLY', _math(nt, 'ADD', z, 0.055), 0.45))               # o punho é inclinado
    punho = _math(nt, 'MULTIPLY', _faixa(nt, s, -0.101, -0.066), _faixa(nt, z, -0.080, -0.036))
    masc = _math(nt, 'MULTIPLY', lado, _math(nt, 'MAXIMUM', telha, punho))
    passo = 0.0016
    a = _math(nt, 'MULTIPLY', y, 0.62)
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'ADD', a, z), passo)), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'SUBTRACT', a, z), passo)), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0009)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    veio = _n(nt, 'ShaderNodeCombineXYZ')
    nt.links.new(_math(nt, 'MULTIPLY', p.outputs['X'], 7.0), veio.inputs[0])
    nt.links.new(_math(nt, 'MULTIPLY', y, 0.4), veio.inputs[1])
    nt.links.new(_math(nt, 'MULTIPLY', _math(nt, 'ADD', z, _math(nt, 'MULTIPLY', y, 0.06)), 7.0), veio.inputs[2])
    risco = _smooth(nt, _noise(nt, veio.outputs[0], 260.0, 4.0, 0.6), 0.42, 0.66)
    topo = _math(nt, 'MAXIMUM', topo, _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', risco, 0.8), _math(nt, 'SUBTRACT', 1.0, masc)))
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


texturas.RELEVO['polim_car_grip'] = pontilhado
texturas.RELEVO['nogueira_car'] = quadriculado
