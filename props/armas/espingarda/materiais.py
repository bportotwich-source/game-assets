"""Classes de material da Mutirão 12 (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas
from texturas import _n, _math, _smooth

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'polim_esp_grip': ((0.021, 0.022, 0.022), 0.64, 0.0, (0.060, 0.060, 0.058), 0.42, 0.0, 0.85, 1.00, 1.6),
    'aco_cano':       ((0.040, 0.041, 0.044), 0.40, 0.90, (0.36, 0.36, 0.37), 0.28, 1.0, 1.00, 0.35, 0.8),    # aço oxidado do cano e do tubo
    'aco_polido':     ((0.300, 0.300, 0.295), 0.36, 1.00, (0.55, 0.55, 0.55), 0.28, 1.0, 0.50, 0.30, 1.0),    # ferrolho, visto pela janela
    'tinta_branca':   ((0.80, 0.80, 0.76), 0.50, 0.0, None, 0, 0, 0, 0, 0),                                  # ponto da massa de mira
    'tinta_vermelha': ((0.52, 0.030, 0.022), 0.50, 0.0, None, 0, 0, 0, 0, 0),
})


def pontilhado(nt, pos, geo):
    """Pontilhado do punho: pirâmides quadradas de 1,3 mm nos lados, na frente e nas costas,
    num painel de borda lisa (some perto do pé do punho e do receptor)."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    z = p.outputs['Z']
    masc = _math(nt, 'MULTIPLY', _smooth(nt, z, -0.1470, -0.1445), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, -0.0625, -0.0600)))
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


texturas.RELEVO['polim_esp_grip'] = pontilhado
