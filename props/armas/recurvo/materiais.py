"""Classes de material do arco recurvo (somadas às da M4A1 em m4a1/texturas.py)."""
import math
import texturas
from texturas import _n, _math, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'madeira_arco':    ((0.105, 0.040, 0.016), 0.30, 0.0, (0.260, 0.130, 0.060), 0.42, 0.0, 0.35, 0.50, 0.8),   # laminado envernizado
    'fibra_arco':      ((0.012, 0.012, 0.013), 0.22, 0.0, (0.060, 0.060, 0.060), 0.40, 0.0, 0.35, 0.25, 0.6),   # fibra de vidro preta
    'lamina_bordo':    ((0.340, 0.205, 0.090), 0.38, 0.0, (0.520, 0.360, 0.190), 0.45, 0.0, 0.0, 0.50, 0.5),    # miolo de bordo, à vista no canto
    'fenolico':        ((0.560, 0.520, 0.420), 0.42, 0.0, (0.600, 0.570, 0.480), 0.45, 0.0, 0.0, 0.40, 0.9),    # reforço da ponta
    'corda':           ((0.030, 0.026, 0.022), 0.82, 0.0, (0.110, 0.100, 0.085), 0.80, 0.0, 0.0, 1.00, 0.0),
    'corda_reforco':   ((0.012, 0.012, 0.012), 0.70, 0.0, (0.050, 0.050, 0.050), 0.70, 0.0, 0.0, 1.00, 0.0),
    'feltro':          ((0.030, 0.026, 0.022), 0.96, 0.0, (0.060, 0.055, 0.050), 0.96, 0.0, 0.0, 1.00, 0.0),
    'couro_arco':      ((0.070, 0.036, 0.018), 0.62, 0.0, (0.150, 0.090, 0.050), 0.55, 0.0, 0.0, 1.00, 0.0),
    'carbono':         ((0.016, 0.016, 0.017), 0.36, 0.0, (0.060, 0.060, 0.060), 0.40, 0.0, 0.0, 0.40, 0.0),
    'envoltorio':      ((0.780, 0.780, 0.740), 0.40, 0.0, (0.800, 0.800, 0.760), 0.40, 0.0, 0.0, 0.20, 0.0),
    'pena_laranja':    ((0.800, 0.170, 0.012), 0.48, 0.0, (0.800, 0.170, 0.012), 0.48, 0.0, 0.0, 0.30, 0.0),
    'pena_branca':     ((0.800, 0.800, 0.760), 0.48, 0.0, (0.800, 0.800, 0.760), 0.48, 0.0, 0.0, 0.30, 0.0),
    'nock':            ((0.800, 0.170, 0.012), 0.35, 0.0, (0.800, 0.170, 0.012), 0.35, 0.0, 0.0, 0.20, 0.0),
    'aluminio_flecha': ((0.550, 0.550, 0.560), 0.34, 1.0, (0.650, 0.650, 0.650), 0.30, 1.0, 0.0, 0.30, 0.0),
    'aco_lamina':      ((0.480, 0.480, 0.480), 0.26, 1.0, (0.650, 0.650, 0.650), 0.22, 1.0, 0.0, 0.30, 0.0),
    'tinta_ouro':      ((0.700, 0.500, 0.180), 0.40, 1.0, None, 0, 0, 0, 0, 0),
})


def _mult(nt, a, b):
    n = _n(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY')
    n.inputs[0].default_value = 1.0
    nt.links.new(a, n.inputs[6])
    nt.links.new(b, n.inputs[7])
    return n.outputs[2]


def _escala(nt, f, cor):
    """Cor = branco onde f = 0 e `cor` onde f = 1 (para multiplicar a cor base)."""
    n = _n(nt, 'ShaderNodeMix', data_type='RGBA')
    nt.links.new(f, n.inputs[0])
    n.inputs[6].default_value = (1, 1, 1, 1)
    n.inputs[7].default_value = (*cor, 1)
    return n.outputs[2]


def _faixa(nt, x, a, b, borda=0.0004):
    return _math(nt, 'MULTIPLY', _smooth(nt, x, a - borda, a + borda), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, x, b - borda, b + borda)))


def cor_laminado(nt, pos, cor):
    """Punho laminado: folhas empilhadas de frente para trás, com uma faixa clara de bordo entre
    dois filetes pretos e o veio correndo de cima a baixo."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    u, v = p.outputs['Y'], p.outputs['Z']
    x = _math(nt, 'SUBTRACT', u, _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', v, v), 0.16))      # as folhas acompanham a curva do punho
    x = _math(nt, 'ADD', x, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', _noise(nt, pos, 9.0, 2.0), 0.5), 0.0016))
    clara = _faixa(nt, x, 0.0050, 0.0125)
    filete = _math(nt, 'MAXIMUM', _faixa(nt, x, 0.0034, 0.0050), _faixa(nt, x, 0.0125, 0.0141))
    filete = _math(nt, 'MAXIMUM', filete, _faixa(nt, x, -0.0092, -0.0080))
    # folhas finas (2 mm), umas mais escuras que as outras
    folha = _math(nt, 'FRACT', _math(nt, 'DIVIDE', x, 0.0021))
    tom = _math(nt, 'ADD', 0.86, _math(nt, 'MULTIPLY', _smooth(nt, folha, 0.35, 0.65), 0.28))
    # veio: riscos compridos no sentido da altura
    veio = _n(nt, 'ShaderNodeCombineXYZ')
    nt.links.new(_math(nt, 'MULTIPLY', p.outputs['X'], 9.0), veio.inputs[0])
    nt.links.new(_math(nt, 'MULTIPLY', u, 9.0), veio.inputs[1])
    nt.links.new(_math(nt, 'MULTIPLY', v, 0.35), veio.inputs[2])
    risco = _smooth(nt, _noise(nt, veio.outputs[0], 240.0, 4.0, 0.6), 0.35, 0.70)
    tom = _math(nt, 'MULTIPLY', tom, _math(nt, 'ADD', 0.72, _math(nt, 'MULTIPLY', risco, 0.50)))
    escala = _n(nt, 'ShaderNodeCombineColor')
    for i in range(3):
        nt.links.new(tom, escala.inputs[i])
    cor = _mult(nt, cor, escala.outputs[0])
    cor = _mult(nt, cor, _escala(nt, clara, (3.0, 4.3, 4.6)))
    cor = _mult(nt, cor, _escala(nt, filete, (0.16, 0.22, 0.40)))
    return cor


def cor_bordo(nt, pos, cor):
    """Miolo de bordo no canto do braço: veio fino."""
    g = _smooth(nt, _noise(nt, pos, 900.0, 3.0, 0.6), 0.3, 0.7)
    escala = _n(nt, 'ShaderNodeCombineColor')
    tom = _math(nt, 'ADD', 0.78, _math(nt, 'MULTIPLY', g, 0.40))
    for i in range(3):
        nt.links.new(tom, escala.inputs[i])
    return _mult(nt, cor, escala.outputs[0])


COR = {'madeira_arco': cor_laminado, 'lamina_bordo': cor_bordo}
_montar = texturas.montar_material


def montar_material(m, nome):
    S, em, bs, out, img = _montar(m, nome)
    if nome in COR:
        nt = m.node_tree
        geo = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeNewGeometry')
        S['cor'] = COR[nome](nt, geo.outputs['Position'], S['cor'])
    return S, em, bs, out, img


texturas.montar_material = montar_material


def torcida(nt, pos, geo):
    """Corda torcida: dois cabos enrolados em hélice (passo de 7 mm), em relevo."""
    n = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], n.inputs[0])
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    ang = _math(nt, 'DIVIDE', _math(nt, 'ARCTAN2', n.outputs['Y'], n.outputs['X']), math.pi)          # -1..1 em volta
    fase = _math(nt, 'ADD', _math(nt, 'DIVIDE', p.outputs['Z'], 0.0035), ang)
    s = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', fase), 0.5))                   # 0 no vale, 0,5 na crista
    h = _math(nt, 'MULTIPLY', s, 0.0009)
    topo = _smooth(nt, s, 0.25, 0.45)
    fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, s, 0.0, 0.15))
    return h, topo, fundo


texturas.RELEVO['corda'] = torcida
