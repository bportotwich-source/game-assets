"""Classes de material do fuzil Brasa 7,62 (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas
from texturas import _n, _math, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_brasa':      ((0.030, 0.031, 0.034), 0.46, 0.85, (0.34, 0.34, 0.35), 0.30, 1.0, 1.30, 0.30, 1.3),     # aço oxidado preto, gasto nas quinas
    'aco_cano':       ((0.040, 0.041, 0.044), 0.40, 0.90, (0.36, 0.36, 0.37), 0.28, 1.0, 1.00, 0.35, 0.8),
    'aco_polido':     ((0.300, 0.300, 0.295), 0.36, 1.00, (0.55, 0.55, 0.55), 0.28, 1.0, 0.50, 0.30, 1.0),     # transportador do ferrolho
    'madeira_brasa':  ((0.070, 0.020, 0.007), 0.40, 0.0, (0.360, 0.130, 0.042), 0.36, 0.0, 0.55, 0.80, 1.5),   # laminado envernizado (a cor cheia vem do relevo)
    'baquelite_grip': ((0.085, 0.022, 0.012), 0.34, 0.0, (0.260, 0.085, 0.035), 0.30, 0.0, 0.60, 0.50, 1.4),
    'laca_verde':     ((0.070, 0.085, 0.040), 0.42, 0.60, (0.30, 0.30, 0.29), 0.30, 1.0, 0.50, 0.30, 0.8),     # estojo de aço laqueado
    'aco_brasa_gasto': ((0.036, 0.034, 0.034), 0.52, 0.80, (0.33, 0.32, 0.31), 0.34, 1.0, 2.00, 0.45, 1.9),    # o mesmo aço, bem usado
    'polim_gasto':     ((0.024, 0.024, 0.024), 0.62, 0.0, (0.085, 0.083, 0.078), 0.44, 0.0, 1.50, 1.00, 1.9),
    'anod_gasto':      ((0.036, 0.038, 0.036), 0.50, 0.75, (0.32, 0.33, 0.34), 0.32, 1.0, 1.80, 0.30, 1.6),
    'polim_brasa_grip': ((0.022, 0.022, 0.022), 0.62, 0.0, (0.075, 0.074, 0.070), 0.42, 0.0, 1.20, 1.00, 1.8),
    'tinta_branca':   ((0.80, 0.80, 0.76), 0.60, 0.0, None, 0, 0, 0, 0, 0),
})
DV_CABO = 0.0265


def quadriculado(nt, pos, geo):
    """Quadriculado do punho de baquelite: pirâmides de 1,5 mm nos dois lados, em painel de borda lisa."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    z = p.outputs['Z']
    masc = _math(nt, 'MULTIPLY', _smooth(nt, z, -0.1440 + DV_CABO, -0.1415 + DV_CABO),
                 _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, -0.0680 + DV_CABO, -0.0655 + DV_CABO)))
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    masc = _math(nt, 'MULTIPLY', masc, _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.62, 0.80))
    passo = 0.0015
    a = _math(nt, 'MULTIPLY', p.outputs['Y'], 1.0)
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'ADD', a, z), passo)), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'SUBTRACT', a, z), passo)), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0008)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    # baquelite: manchas largas mais claras fora do quadriculado
    mancha = _smooth(nt, _noise(nt, pos, 95.0, 3.0, 0.6), 0.40, 0.72)
    topo = _math(nt, 'MAXIMUM', topo, _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', mancha, 0.75), _math(nt, 'SUBTRACT', 1.0, masc)))
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


def laminado(nt, pos, geo):
    """Madeira laminada: folhas em pé de 1,7 mm (paralelas aos lados da arma), então as linhas de
    cola aparecem como curvas de nível onde a peça arredonda, e veio comprido ao longo da arma.
    A cor cheia fica entre a base escura (cola, poros) e a cor gasta; onde o verniz saiu, clareia."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    x, y, z = p.outputs['X'], p.outputs['Y'], p.outputs['Z']
    onda = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', _noise(nt, pos, 14.0, 2.0, 0.5), 0.5), 0.007)            # folhas levemente onduladas
    c = _math(nt, 'DIVIDE', _math(nt, 'ADD', _math(nt, 'ADD', x, onda), _math(nt, 'MULTIPLY', z, 0.04)), 0.0017)
    f = _math(nt, 'FRACT', c)
    cola = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', f, 0.5)), 0.38, 0.48))   # 1 na folha, 0 na linha de cola
    veio = _n(nt, 'ShaderNodeCombineXYZ')
    nt.links.new(_math(nt, 'MULTIPLY', x, 9.0), veio.inputs[0])
    nt.links.new(_math(nt, 'MULTIPLY', y, 0.35), veio.inputs[1])
    nt.links.new(_math(nt, 'MULTIPLY', z, 9.0), veio.inputs[2])
    g = _noise(nt, veio.outputs[0], 240.0, 4.0, 0.6)
    tom = _math(nt, 'ADD', 0.66, _math(nt, 'MULTIPLY', _smooth(nt, g, 0.30, 0.70), 0.34))
    cam = _n(nt, 'ShaderNodeCombineXYZ')                                                                         # cada folha com o seu tom
    nt.links.new(_math(nt, 'FLOOR', c), cam.inputs[0])
    folha = _math(nt, 'ADD', 0.58, _math(nt, 'MULTIPLY', _noise(nt, cam.outputs[0], 3.7, 1.0, 0.5), 0.56))
    topo = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', _math(nt, 'ADD', 0.70, _math(nt, 'MULTIPLY', cola, 0.30)), tom), folha, clamp=True)
    h = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', cola, 1.0), 0.00004)
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, cola), 0.3)
    return h, topo, fundo


texturas.RELEVO['baquelite_grip'] = quadriculado
texturas.RELEVO['polim_brasa_grip'] = quadriculado
texturas.RELEVO['madeira_brasa'] = laminado
