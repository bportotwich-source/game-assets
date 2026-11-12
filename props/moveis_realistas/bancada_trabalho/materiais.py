"""Classes de material da bancada de trabalho (somadas às da M4A1, às madeiras da bancada de carpintaria,
ao envelhecimento da forja e aos plásticos da bancada de eletrônica)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_bancada_eletronica', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bancada_eletronica', 'materiais.py'))
eletronica = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eletronica)
forja = eletronica.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_verde':    ((0.060, 0.105, 0.080), 0.50, 0.0, (0.200, 0.085, 0.036), 0.85, 0.3, 1.60, 0.60, 2.2),   # cantoneira pintada, ferrugem nas quinas
    'esmalte_azul': ((0.016, 0.060, 0.190), 0.42, 0.0, (0.300, 0.300, 0.310), 0.40, 1.0, 1.40, 0.50, 1.8),   # ferro fundido da morsa
    'eucatex':      ((0.190, 0.108, 0.058), 0.62, 0.0, (0.330, 0.220, 0.130), 0.70, 0.0, 0.60, 0.80, 2.0),   # painel perfurado
})


def _lascado(nt, pos, S, nome):
    """Tinta de oficina: lascas e manchas de ferrugem, pé comido e graxa escura em manchas largas."""
    x, y, z = forja._xyz(nt, pos)
    f = _smooth(nt, _noise(nt, pos, 11.0, 4.0, 0.65), 0.56, 0.64)
    pe = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, 0.03, 0.16)), _smooth(nt, _noise(nt, pos, 30.0, 3.0, 0.6), 0.30, 0.55))
    f = _math(nt, 'MAXIMUM', _math(nt, 'MULTIPLY', f, 0.9), pe)
    ferr = _mix(nt, _smooth(nt, _noise(nt, pos, 70.0, 3.0, 0.6), 0.3, 0.7), (0.200, 0.075, 0.028), (0.085, 0.036, 0.018))
    S['cor'] = _mix(nt, f, S['cor'], ferr)
    S['rug'] = _mixf(nt, f, S['rug'], 0.90)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', f, _noise(nt, pos, 500.0, 2.0, 0.6)), 0.0006))
    graxa = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 6.0, 3.0, 0.6), 0.50, 0.70), 0.55)
    S['cor'] = _mix(nt, graxa, S['cor'], (0.014, 0.013, 0.012))
    S['rug'] = _mixf(nt, graxa, S['rug'], 0.35)


def _fundido(nt, pos, S, nome):
    """Ferro fundido pintado: casca de laranja da fundição e graxa nos cantos."""
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _noise(nt, pos, 260.0, 2.0, 0.5), 0.0007))
    graxa = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 22.0, 4.0, 0.62), 0.48, 0.66), 0.7)
    S['cor'] = _mix(nt, graxa, S['cor'], (0.012, 0.014, 0.020))
    S['rug'] = _mixf(nt, graxa, S['rug'], 0.30)


def _furos(nt, pos, S, nome):
    """Painel perfurado: furos a cada polegada, e a chapa desbotada em manchas."""
    x, y, z = forja._xyz(nt, pos)
    a = _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'ADD', x, 10.0), 0.0254)), 0.5)
    b = _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', z, 0.0254)), 0.5)
    d = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', a, a), _math(nt, 'MULTIPLY', b, b)))
    furo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, d, 0.11, 0.15))
    tom = _math(nt, 'ADD', 0.75, _math(nt, 'MULTIPLY', _noise(nt, pos, 3.5, 3.0, 0.6), 0.5))
    S['cor'] = forja.madeira._tom(nt, S['cor'], tom)
    S['cor'] = _mix(nt, furo, S['cor'], (0.008, 0.007, 0.006))
    S['rug'] = _mixf(nt, furo, S['rug'], 1.0)
    S['alt'] = _math(nt, 'SUBTRACT', S['alt'], _math(nt, 'MULTIPLY', furo, 0.0015))
    S['ao'] = _math(nt, 'MULTIPLY', S['ao'], _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', furo, 0.6)))


forja.VELHO.update(aco_verde=_lascado, esmalte_azul=_fundido, eucatex=_furos, esmalte_vermelho=_lascado)
