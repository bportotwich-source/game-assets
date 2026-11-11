"""Classes de material do arco composto (somadas às da M4A1 e às do arco recurvo)."""
import os, importlib.util
import texturas
from texturas import _n, _math, _smooth

_spec = importlib.util.spec_from_file_location('materiais_recurvo', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recurvo', 'materiais.py'))
recurvo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(recurvo)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'anod_arco':       ((0.105, 0.110, 0.100), 0.42, 0.85, (0.50, 0.50, 0.51), 0.30, 1.0, 0.90, 0.25, 0.9),    # alumínio anodizado grafite
    'anod_laranja':    ((0.620, 0.150, 0.014), 0.36, 0.85, (0.60, 0.50, 0.46), 0.30, 1.0, 0.45, 0.20, 0.8),
    'polim_arco_grip': ((0.021, 0.022, 0.022), 0.62, 0.0, (0.060, 0.060, 0.058), 0.42, 0.0, 0.80, 1.00, 1.4),
    'fibra_faixa':     ((0.030, 0.034, 0.040), 0.30, 0.25, (0.080, 0.080, 0.085), 0.40, 0.0, 0.20, 0.30, 0.5),  # faixa de carbono no braço
    'cabo':            ((0.050, 0.070, 0.030), 0.82, 0.0, (0.130, 0.160, 0.090), 0.80, 0.0, 0.0, 1.00, 0.0),
    'cordel':          ((0.620, 0.170, 0.020), 0.80, 0.0, (0.700, 0.300, 0.080), 0.80, 0.0, 0.0, 1.00, 0.0),    # laço D
    'pena_verde':      ((0.220, 0.560, 0.030), 0.48, 0.0, (0.220, 0.560, 0.030), 0.48, 0.0, 0.0, 0.30, 0.0),
    'nock_vermelho':   ((0.750, 0.030, 0.020), 0.30, 0.0, (0.750, 0.030, 0.020), 0.30, 0.0, 0.0, 0.20, 0.0),
})


def pontilhado(nt, pos, geo):
    """Pega: pirâmides de 1,4 mm dos dois lados."""
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    masc = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.62, 0.85)
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    passo = 0.0014
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', p.outputs['Y'], passo)), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', p.outputs['Z'], passo)), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0008)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


texturas.RELEVO['polim_arco_grip'] = pontilhado
texturas.RELEVO['cabo'] = recurvo.torcida
texturas.RELEVO['cordel'] = recurvo.torcida
