"""Classes de material da pistola sinalizadora (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas
from texturas import _n, _math, _smooth

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'laranja_sinal':    ((0.640, 0.105, 0.016), 0.40, 0.55, (0.50, 0.50, 0.51), 0.30, 1.0, 1.10, 0.25, 1.2),   # alumínio anodizado laranja
    'polim_sinal_grip': ((0.021, 0.022, 0.022), 0.60, 0.0, (0.060, 0.060, 0.058), 0.40, 0.0, 0.80, 1.00, 1.5),
    'casco_vermelho':   ((0.420, 0.020, 0.016), 0.45, 0.0, (0.55, 0.10, 0.08), 0.40, 0.0, 0.40, 0.60, 0.8),
    'tinta_branca':     ((0.80, 0.80, 0.76), 0.60, 0.0, None, 0, 0, 0, 0, 0),
    'tinta_preta':      ((0.015, 0.015, 0.015), 0.55, 0.0, None, 0, 0, 0, 0, 0),
})


def quadriculado(nt, pos, geo):
    """Quadriculado das talas: pirâmides de 1,7 mm em losango na face de fora (a borda abaulada fica lisa)."""
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    masc = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.90, 0.985)
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    passo = 0.0017
    a = _math(nt, 'MULTIPLY', p.outputs['Y'], 0.62)          # losango mais alto que largo
    x = _math(nt, 'DIVIDE', _math(nt, 'ADD', a, p.outputs['Z']), passo)
    y = _math(nt, 'DIVIDE', _math(nt, 'SUBTRACT', a, p.outputs['Z']), passo)
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', x), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', y), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0010)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


texturas.RELEVO['polim_sinal_grip'] = quadriculado
