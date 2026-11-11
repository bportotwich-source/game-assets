"""Classes de material da machadinha tática (somadas às da M4A1, do Brasa, dos arcos e da besta)."""
import os, importlib.util
import texturas
from texturas import _n, _math, _smooth

for _nome, _pasta in (('materiais_besta_m', 'besta'), ('materiais_brasa_m', 'brasa')):
    _spec = importlib.util.spec_from_file_location(_nome, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', _pasta, 'materiais.py'))
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_machado': ((0.055, 0.056, 0.060), 0.50, 0.40, (0.36, 0.36, 0.37), 0.32, 1.0, 0.60, 0.35, 1.4),     # aço escurecido
    'cordao':      ((0.200, 0.150, 0.070), 0.85, 0.0, (0.300, 0.240, 0.130), 0.85, 0.0, 0.0, 1.00, 0.8),     # cordão cor de areia
})


def enrolado(nt, pos, geo):
    """Cordão enrolado no cabo: voltas de 4,2 mm empilhadas na altura, em relevo."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    fase = _math(nt, 'ADD', _math(nt, 'DIVIDE', p.outputs['Z'], 0.0042), _math(nt, 'MULTIPLY', p.outputs['Y'], 9.0))     # voltas levemente inclinadas
    s = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', fase), 0.5)))        # 0 no vale, 0,5 na crista
    h = _math(nt, 'MULTIPLY', _math(nt, 'POWER', _math(nt, 'MULTIPLY', s, 2.0), 0.5), 0.0016)
    topo = _smooth(nt, s, 0.30, 0.48)
    fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, s, 0.0, 0.12))
    return h, topo, fundo


texturas.RELEVO['cordao'] = enrolado
