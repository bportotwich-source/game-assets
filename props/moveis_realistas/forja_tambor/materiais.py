"""Classes de material da forja de tambor (somadas às da M4A1 e às madeiras da bancada de carpintaria)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_bancada_carpintaria',
                                               os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bancada_carpintaria', 'materiais.py'))
madeira = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(madeira)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'tambor':          ((0.030, 0.070, 0.150), 0.52, 0.0, (0.200, 0.085, 0.036), 0.85, 0.3, 1.60, 0.60, 2.2),    # tinta azul, ferrugem nas quinas
    'tambor_queimado': ((0.036, 0.030, 0.027), 0.82, 0.2, (0.220, 0.095, 0.045), 0.88, 0.3, 1.60, 1.20, 2.2),    # a boca, queimada pelo fogo
    'barro':           ((0.300, 0.185, 0.110), 0.95, 0.0, (0.430, 0.310, 0.210), 0.95, 0.0, 0.40, 2.20, 1.6),
    'carvao':          ((0.012, 0.012, 0.013), 0.72, 0.0, (0.012, 0.012, 0.013), 0.72, 0.0, 0.0, 1.80, 0.3),
    'tijolo':          ((0.330, 0.095, 0.050), 0.88, 0.0, (0.480, 0.240, 0.150), 0.88, 0.0, 0.60, 1.80, 2.0),
    'ferrugem':        ((0.150, 0.062, 0.030), 0.86, 0.3, (0.300, 0.280, 0.270), 0.50, 1.0, 0.50, 1.60, 1.6),
    'couro':           ((0.100, 0.046, 0.022), 0.70, 0.0, (0.250, 0.140, 0.080), 0.60, 0.0, 0.80, 1.20, 1.6),
    'casca':           ((0.070, 0.047, 0.032), 0.95, 0.0, (0.200, 0.140, 0.090), 0.90, 0.0, 0.60, 2.60, 1.3),
    'trilho':          ((0.085, 0.055, 0.038), 0.70, 0.7, (0.450, 0.440, 0.430), 0.32, 1.0, 1.30, 1.00, 1.6),
    'trilho_batido':   ((0.380, 0.380, 0.390), 0.30, 1.0, (0.600, 0.600, 0.610), 0.24, 1.0, 0.60, 0.40, 0.8),    # a mesa da bigorna, polida de pancada
})

# ---------------------------------------------------------------- envelhecimento próprio de cada classe
from texturas import _n, _math, _mix, _mixf, _smooth, _noise


def _xyz(nt, pos):
    s = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, s.inputs[0])
    return s.outputs['X'], s.outputs['Y'], s.outputs['Z']


def _vec(nt, x, y, z, fx=1.0, fy=1.0, fz=1.0):
    v = _n(nt, 'ShaderNodeCombineXYZ')
    for i, (a, f) in enumerate(((x, fx), (y, fy), (z, fz))):
        nt.links.new(_math(nt, 'MULTIPLY', a, f), v.inputs[i])
    return v.outputs[0]


def _tambor(nt, pos, S, nome):
    """Tinta de tambor velho: ferrugem em manchas e escorrida de cima para baixo, pé comido de ferrugem
    e fuligem perto da boca."""
    x, y, z = _xyz(nt, pos)
    escorrido = _noise(nt, _vec(nt, x, y, z, 1.0, 1.0, 0.07), 16.0, 3.0, 0.6)
    mancha = _noise(nt, pos, 5.5, 4.0, 0.62)
    f = _smooth(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', mancha, 0.62), _math(nt, 'MULTIPLY', escorrido, 0.42)), 0.50, 0.60)
    pe = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, 0.13, 0.30)), _smooth(nt, _noise(nt, pos, 24.0, 3.0, 0.6), 0.30, 0.55))
    f = _math(nt, 'MAXIMUM', _math(nt, 'MULTIPLY', f, 0.92), pe)
    ferr = _mix(nt, _smooth(nt, _noise(nt, pos, 70.0, 3.0, 0.6), 0.3, 0.7), (0.200, 0.075, 0.028), (0.085, 0.036, 0.018))
    S['cor'] = _mix(nt, f, S['cor'], ferr)
    S['rug'] = _mixf(nt, f, S['rug'], 0.90)
    S['met'] = _mixf(nt, f, S['met'], 0.15)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', f, _noise(nt, pos, 500.0, 2.0, 0.6)), 0.0006))
    fuligem = _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'ADD', z, _math(nt, 'MULTIPLY', escorrido, 0.10)), 0.56, 0.76), 0.85)
    S['cor'] = _mix(nt, fuligem, S['cor'], (0.014, 0.013, 0.012))
    S['rug'] = _mixf(nt, fuligem, S['rug'], 0.95)


def _tijolo(nt, pos, S, nome):
    tom = _math(nt, 'ADD', 0.55, _math(nt, 'MULTIPLY', _noise(nt, pos, 4.5, 2.0, 0.5), 0.95))
    S['cor'] = madeira._tom(nt, S['cor'], tom)
    poros = _smooth(nt, _noise(nt, pos, 420.0, 3.0, 0.6), 0.55, 0.75)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', poros, 0.5), S['cor'], (0.090, 0.035, 0.022))
    S['alt'] = _math(nt, 'SUBTRACT', S['alt'], _math(nt, 'MULTIPLY', poros, 0.0012))
    fuligem = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 9.0, 3.0, 0.6), 0.45, 0.65), 0.7)
    S['cor'] = _mix(nt, fuligem, S['cor'], (0.030, 0.026, 0.024))


def _casca(nt, pos, S, nome):
    """Casca de tora: sulcos fundos correndo de cima a baixo."""
    x, y, z = _xyz(nt, pos)
    sulco = _noise(nt, _vec(nt, x, y, z, 1.0, 1.0, 0.10), 55.0, 4.0, 0.65)
    fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, sulco, 0.38, 0.56))
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _smooth(nt, sulco, 0.30, 0.70), 0.0075))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', fundo, 0.80), S['cor'], (0.016, 0.011, 0.008))
    topo = _math(nt, 'MULTIPLY', _smooth(nt, sulco, 0.60, 0.75), _smooth(nt, _noise(nt, pos, 30.0, 3.0, 0.6), 0.4, 0.7))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', topo, 0.55), S['cor'], (0.200, 0.160, 0.115))
    S['ao'] = _math(nt, 'MULTIPLY', S['ao'], _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', fundo, 0.5)))


def _couro(nt, pos, S, nome):
    x, y, z = _xyz(nt, pos)
    ruga = _noise(nt, _vec(nt, x, y, z, 0.25, 1.0, 1.0), 85.0, 4.0, 0.65)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _smooth(nt, ruga, 0.30, 0.70), 0.0022))
    fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, ruga, 0.36, 0.52))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', fundo, 0.65), S['cor'], (0.022, 0.011, 0.006))
    gasto = _math(nt, 'MULTIPLY', _smooth(nt, ruga, 0.62, 0.78), 0.5)
    S['cor'] = _mix(nt, gasto, S['cor'], (0.260, 0.150, 0.085))
    S['rug'] = _mixf(nt, gasto, S['rug'], 0.50)


def _barro(nt, pos, S, nome):
    """Barro cozido da boca da forja: rachaduras e fuligem para o lado do fogo."""
    v = _n(nt, 'ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE')
    v.inputs['Scale'].default_value = 26.0
    nt.links.new(pos, v.inputs['Vector'])
    racha = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, v.outputs['Distance'], 0.0, 0.05))
    racha = _math(nt, 'MULTIPLY', racha, _smooth(nt, _noise(nt, pos, 12.0, 2.0, 0.5), 0.35, 0.6))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', racha, 0.85), S['cor'], (0.030, 0.022, 0.016))
    S['alt'] = _math(nt, 'SUBTRACT', S['alt'], _math(nt, 'MULTIPLY', racha, 0.0030))
    x, y, z = _xyz(nt, pos)
    r = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', x, x), _math(nt, 'MULTIPLY', y, y)))
    fuligem = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', _noise(nt, pos, 18.0, 3.0, 0.6), 0.08)), 0.17, 0.31))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', fuligem, 0.85), S['cor'], (0.016, 0.014, 0.013))


def _trilho(nt, pos, S, nome):
    f = _smooth(nt, _noise(nt, pos, 38.0, 4.0, 0.65), 0.42, 0.62)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', f, 0.8), S['cor'], (0.170, 0.065, 0.026))
    S['rug'] = _mixf(nt, f, S['rug'], 0.9)
    S['met'] = _mixf(nt, f, S['met'], 0.2)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', f, _noise(nt, pos, 600.0, 2.0, 0.6)), 0.0005))


VELHO = {'tambor': _tambor, 'tambor_queimado': _tambor, 'tijolo': _tijolo, 'casca': _casca, 'couro': _couro, 'barro': _barro,
         'trilho': _trilho, 'ferrugem': _trilho}
_montar = texturas.montar_material


def montar_material(m, nome):
    S, em, bs, out, img = _montar(m, nome)
    if nome in VELHO:
        nt = m.node_tree
        geo = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeNewGeometry')
        VELHO[nome](nt, geo.outputs['Position'], S, nome)
        if S['alt'] is not None:                                   # o relevo novo entra no bump que a base já ligou
            bmp = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBump')
            nt.links.new(S['alt'], bmp.inputs['Height'])
    return S, em, bs, out, img


texturas.montar_material = montar_material
