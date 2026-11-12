"""Classes de material da fogueira (somadas às da M4A1, às madeiras da bancada e ao envelhecimento da forja)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_forja_tambor', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'forja_tambor', 'materiais.py'))
forja = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(forja)
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'pedra':          ((0.120, 0.112, 0.098), 0.90, 0.0, (0.360, 0.350, 0.320), 0.86, 0.0, 0.35, 2.20, 1.4),
    'casca_lenha':    texturas.CLASSES['casca'],
    'cinza':          ((0.300, 0.295, 0.285), 0.96, 0.0, (0.300, 0.295, 0.285), 0.96, 0.0, 0.0, 2.40, 0.6),
    'tora_queimada':  ((0.016, 0.015, 0.015), 0.80, 0.0, (0.016, 0.015, 0.015), 0.80, 0.0, 0.0, 2.00, 0.2),
})


def _pedra(nt, pos, S, nome):
    """Pedra de rio: cada uma de um tom, veios, e fuligem do lado virado para o fogo."""
    tom = _math(nt, 'ADD', 0.50, _math(nt, 'MULTIPLY', _noise(nt, pos, 5.0, 2.0, 0.5), 1.05))
    S['cor'] = forja.madeira._tom(nt, S['cor'], tom)
    quente = _smooth(nt, _noise(nt, pos, 11.0, 2.0, 0.5), 0.40, 0.65)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', quente, 0.35), S['cor'], (0.260, 0.190, 0.130))
    furo = _smooth(nt, _noise(nt, pos, 260.0, 3.0, 0.6), 0.58, 0.74)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', furo, 0.55), S['cor'], (0.050, 0.047, 0.042))
    S['alt'] = _math(nt, 'SUBTRACT', _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _noise(nt, pos, 60.0, 4.0, 0.6), 0.004)), _math(nt, 'MULTIPLY', furo, 0.0015))
    x, y, z = forja._xyz(nt, pos)
    r = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', x, x), _math(nt, 'MULTIPLY', y, y)))
    fuligem = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', _noise(nt, pos, 25.0, 3.0, 0.6), 0.5), 0.12)), 0.37, 0.47))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', fuligem, 0.92), S['cor'], (0.014, 0.013, 0.012))


def _cinza(nt, pos, S, nome):
    m = _smooth(nt, _noise(nt, pos, 30.0, 4.0, 0.65), 0.35, 0.65)
    S['cor'] = _mix(nt, m, (0.060, 0.058, 0.056), S['cor'])
    c = _smooth(nt, _noise(nt, pos, 140.0, 2.0, 0.5), 0.62, 0.72)
    S['cor'] = _mix(nt, c, S['cor'], (0.012, 0.012, 0.012))
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _noise(nt, pos, 90.0, 4.0, 0.6), 0.004))


def _queimada(nt, pos, S, nome):
    """Lenha virada carvão: quadriculado de rachaduras, com cinza clara nas quinas."""
    v = _n(nt, 'ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE')
    v.inputs['Scale'].default_value = 75.0
    nt.links.new(pos, v.inputs['Vector'])
    racha = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, v.outputs['Distance'], 0.0, 0.08))
    S['alt'] = _math(nt, 'SUBTRACT', S['alt'], _math(nt, 'MULTIPLY', racha, 0.0030))
    topo = _math(nt, 'MULTIPLY', _smooth(nt, v.outputs['Distance'], 0.25, 0.45), _smooth(nt, _noise(nt, pos, 22.0, 3.0, 0.6), 0.45, 0.7))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', topo, 0.6), S['cor'], (0.230, 0.225, 0.215))
    S['rug'] = _mixf(nt, racha, 0.55, 0.9)


def _lenha(nt, pos, S, nome):
    """Casca de lenha fina, com o pé da acha já tisnado pelo fogo."""
    x, y, z = forja._xyz(nt, pos)
    sulco = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.22), 150.0, 4.0, 0.65)
    fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, sulco, 0.38, 0.56))
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _smooth(nt, sulco, 0.30, 0.70), 0.0030))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', fundo, 0.70), S['cor'], (0.018, 0.012, 0.009))
    topo = _smooth(nt, sulco, 0.62, 0.78)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', topo, 0.40), S['cor'], (0.190, 0.150, 0.110))
    queimado = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ADD', z, _math(nt, 'MULTIPLY', _noise(nt, pos, 28.0, 3.0, 0.6), 0.10)), 0.10, 0.24))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', queimado, 0.95), S['cor'], (0.012, 0.011, 0.011))


forja.VELHO.update(pedra=_pedra, cinza=_cinza, tora_queimada=_queimada, casca_lenha=_lenha)
