"""Classes de material do rifle Pardal .22 (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas
from texturas import _n, _math, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_cano':        ((0.040, 0.041, 0.044), 0.40, 0.90, (0.36, 0.36, 0.37), 0.28, 1.0, 1.00, 0.35, 0.8),
    'aco_polido':      ((0.300, 0.300, 0.295), 0.36, 1.00, (0.55, 0.55, 0.55), 0.28, 1.0, 0.50, 0.30, 1.0),    # ferrolho
    'azulado':         ((0.026, 0.030, 0.040), 0.36, 0.90, (0.30, 0.30, 0.31), 0.28, 1.0, 0.85, 0.20, 1.0),    # aço azulado
    'nogueira_pardal': ((0.078, 0.030, 0.012), 0.40, 0.0, (0.200, 0.095, 0.044), 0.40, 0.0, 0.55, 1.00, 1.4),
    'polim_pardal':    ((0.021, 0.022, 0.022), 0.64, 0.0, (0.060, 0.060, 0.058), 0.42, 0.0, 0.85, 1.00, 1.6),
    'tinta_vermelha':  ((0.52, 0.030, 0.022), 0.50, 0.0, None, 0, 0, 0, 0, 0),
})


def _faixa(nt, x, a, b, borda=0.002):
    return _math(nt, 'MULTIPLY', _smooth(nt, x, a, a + borda), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, x, b - borda, b)))


def _paineis(nt, pos, geo):
    """Máscara dos painéis de pega: lados da telha (atrás das placas) e lados do punho (inclinado)."""
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    lado = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.55, 0.80)
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    y, z = p.outputs['Y'], p.outputs['Z']
    telha = _math(nt, 'MULTIPLY', _faixa(nt, y, 0.118, 0.234), _faixa(nt, z, -0.0275, -0.0085))
    s = _math(nt, 'SUBTRACT', y, _math(nt, 'MULTIPLY', _math(nt, 'ADD', z, 0.062), 0.62))          # o punho é inclinado
    punho = _math(nt, 'MULTIPLY', _faixa(nt, s, -0.108, -0.073), _faixa(nt, z, -0.086, -0.036))
    return _math(nt, 'MULTIPLY', lado, _math(nt, 'MAXIMUM', telha, punho)), p


def quadriculado(nt, pos, geo):
    """Nogueira: quadriculado de losangos de 1,6 mm nos painéis e veio comprido, ao longo da arma, no resto."""
    masc, p = _paineis(nt, pos, geo)
    y, z = p.outputs['Y'], p.outputs['Z']
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


def pontilhado(nt, pos, geo):
    """Polímero: pirâmides quadradas de 1,3 mm nos mesmos painéis."""
    masc, p = _paineis(nt, pos, geo)
    y, z = p.outputs['Y'], p.outputs['Z']
    passo = 0.0013
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', y, passo)), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', z, passo)), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0008)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


texturas.RELEVO['nogueira_pardal'] = quadriculado
texturas.RELEVO['polim_pardal'] = pontilhado
