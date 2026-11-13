"""Classes de material dos móveis de sala (somadas às dos móveis de quarto: nogueira envernizada, forro, latão)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'materiais.py'))
quarto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(quarto)
forja = quarto.forja
madeira = quarto.madeira
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

CAPAS = [(0.230, 0.030, 0.028), (0.030, 0.075, 0.150), (0.040, 0.110, 0.060), (0.290, 0.190, 0.090), (0.060, 0.050, 0.045), (0.300, 0.250, 0.170)]
# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'estofado_verde': quarto._pano_cls((0.070, 0.115, 0.075)),
    'papel_livro':    ((0.560, 0.500, 0.370), 0.86, 0.0, (0.560, 0.500, 0.370), 0.86, 0.0, 0.0, 0.60, 1.4),
    'tacha':          ((0.380, 0.250, 0.080), 0.40, 1.0, (0.700, 0.520, 0.220), 0.28, 1.0, 0.80, 0.30, 1.2),
})
for _i, _c in enumerate(CAPAS):
    texturas.CLASSES[f'capa_{_i + 1}'] = (_c, 0.62, 0.0, tuple(min(1.0, v * 2.2 + 0.08) for v in _c), 0.80, 0.0, 1.10, 0.80, 1.6)


def _estofado(nt, pos, S, nome):
    """Assento de tecido: trama, e o meio gasto e desbotado de tanto sentar."""
    forja.VELHO['pano_cru'](nt, pos, S, nome)
    x, y, z = forja._xyz(nt, pos)
    r = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', x, x), _math(nt, 'MULTIPLY', y, y)))
    gasto = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', _noise(nt, pos, 14.0, 3.0, 0.6), 0.10)), 0.08, 0.22)), 0.45)
    S['cor'] = _mix(nt, gasto, S['cor'], (0.200, 0.220, 0.160))
    po = _math(nt, 'MULTIPLY', quarto._cima(nt), 0.22)
    S['cor'] = _mix(nt, po, S['cor'], (0.300, 0.270, 0.230))


def _capa(nt, pos, S, nome):
    """Capa de livro velho: desbotada em manchas e com poeira em cima."""
    f = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 18.0, 3.0, 0.6), 0.45, 0.75), 0.35)
    S['cor'] = _mix(nt, f, S['cor'], (0.300, 0.260, 0.200))
    po = _math(nt, 'MULTIPLY', quarto._cima(nt), 0.55)
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))
    S['rug'] = _mixf(nt, po, S['rug'], 0.92)


def _papel(nt, pos, S, nome):
    """Miolo do livro: as folhas (riscas finas ao longo da espessura), amarelado nas bordas e com poeira em cima."""
    x, y, z = forja._xyz(nt, pos)
    w = _n(nt, 'ShaderNodeTexWave', wave_type='BANDS')
    w.inputs['Scale'].default_value = 900.0
    w.inputs['Distortion'].default_value = 1.5
    nt.links.new(forja._vec(nt, x, x, x, 1.0, 0.0, 0.0), w.inputs['Vector'])
    S['cor'] = madeira._tom(nt, S['cor'], _math(nt, 'ADD', 0.78, _math(nt, 'MULTIPLY', w.outputs['Fac'], 0.30)))
    amarelo = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 30.0, 3.0, 0.6), 0.40, 0.70), 0.40)
    S['cor'] = _mix(nt, amarelo, S['cor'], (0.330, 0.240, 0.120))
    po = _math(nt, 'MULTIPLY', quarto._cima(nt), 0.50)
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))


forja.VELHO.update(estofado_verde=_estofado, papel_livro=_papel, **{f'capa_{i + 1}': _capa for i in range(len(CAPAS))})
