"""Classes de material da besta recurva (somadas às da M4A1, do arco recurvo e do composto)."""
import os, math, importlib.util
import texturas
from texturas import _n, _math, _smooth

_spec = importlib.util.spec_from_file_location('materiais_composto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'composto', 'materiais.py'))
composto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(composto)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'polim_oliva':    ((0.070, 0.082, 0.040), 0.60, 0.0, (0.150, 0.165, 0.100), 0.45, 0.0, 0.70, 0.90, 1.3),   # polímero verde-oliva
    'anod_cabeca':    ((0.030, 0.031, 0.033), 0.40, 0.85, (0.50, 0.50, 0.51), 0.30, 1.0, 0.80, 0.25, 0.9),    # alumínio anodizado preto
    'fita_deslize':   ((0.012, 0.012, 0.012), 0.18, 0.0, (0.060, 0.060, 0.060), 0.30, 0.0, 0.0, 0.20, 0.3),
    'corda_besta':    ((0.050, 0.070, 0.030), 0.82, 0.0, (0.130, 0.160, 0.090), 0.80, 0.0, 0.0, 1.00, 0.0),
    'laranja_trava':  ((0.700, 0.160, 0.014), 0.45, 0.0, (0.700, 0.160, 0.014), 0.45, 0.0, 0.0, 0.30, 0.3),
    'pena_vermelha':  ((0.650, 0.030, 0.020), 0.48, 0.0, (0.650, 0.030, 0.020), 0.48, 0.0, 0.0, 0.30, 0.0),
    'tinta_vermelha': ((0.520, 0.030, 0.022), 0.50, 0.0, None, 0, 0, 0, 0, 0),
})


def torcida_deitada(nt, pos, geo):
    """Corda torcida da besta, que corre deitada (em x e y do Blender): frisos enviesados de 3,5 mm."""
    n = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], n.inputs[0])
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    ao_longo = _math(nt, 'ADD', _math(nt, 'MULTIPLY', _math(nt, 'ABSOLUTE', p.outputs['X']), 0.652), _math(nt, 'MULTIPLY', p.outputs['Y'], -0.758))
    ang = _math(nt, 'MULTIPLY', n.outputs['Z'], 0.5)
    fase = _math(nt, 'ADD', _math(nt, 'DIVIDE', ao_longo, 0.0035), ang)
    s = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', fase), 0.5))
    h = _math(nt, 'MULTIPLY', s, 0.0009)
    topo = _smooth(nt, s, 0.25, 0.45)
    fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, s, 0.0, 0.15))
    return h, topo, fundo


texturas.RELEVO['corda_besta'] = torcida_deitada
