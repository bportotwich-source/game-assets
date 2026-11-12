"""Classes de material do fogão de tambor (somadas às da M4A1 e às das outras estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_mesa_enfermaria', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mesa_enfermaria', 'materiais.py'))
enfermaria = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enfermaria)
forja = enfermaria.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'chamine':       ((0.150, 0.150, 0.150), 0.55, 0.8, (0.220, 0.095, 0.045), 0.88, 0.3, 1.20, 0.80, 2.0),   # cano galvanizado tisnado
    'aluminio':      ((0.560, 0.560, 0.560), 0.36, 1.0, (0.700, 0.700, 0.700), 0.28, 1.0, 0.60, 0.40, 1.8),
    'chapa_fogao':   ((0.060, 0.052, 0.048), 0.62, 0.8, (0.300, 0.290, 0.280), 0.40, 1.0, 1.00, 0.80, 1.6),   # chapa de cozinhar, preta de uso
})


def _chamine(nt, pos, S, nome):
    """Cano de chaminé: fuligem escorrida das emendas e ferrugem em manchas."""
    x, y, z = forja._xyz(nt, pos)
    escorrido = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.06), 18.0, 3.0, 0.6)
    f = _smooth(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', _noise(nt, pos, 6.0, 4.0, 0.62), 0.6), _math(nt, 'MULTIPLY', escorrido, 0.45)), 0.50, 0.60)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', f, 0.85), S['cor'], (0.170, 0.070, 0.028))
    S['rug'] = _mixf(nt, f, S['rug'], 0.9)
    S['met'] = _mixf(nt, f, S['met'], 0.15)
    fuligem = _math(nt, 'MULTIPLY', _smooth(nt, escorrido, 0.45, 0.75), 0.6)
    S['cor'] = _mix(nt, fuligem, S['cor'], (0.014, 0.013, 0.012))
    S['rug'] = _mixf(nt, fuligem, S['rug'], 0.95)


def _panela(nt, pos, S, nome):
    """Alumínio de panela velha: fundo e lados tisnados do fogo."""
    x, y, z = forja._xyz(nt, pos)
    f = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 20.0, 3.0, 0.6), 0.35, 0.70), 0.75)
    S['cor'] = _mix(nt, f, S['cor'], (0.030, 0.026, 0.022))
    S['rug'] = _mixf(nt, f, S['rug'], 0.80)
    S['met'] = _mixf(nt, f, S['met'], 0.3)


def _chapa(nt, pos, S, nome):
    f = _smooth(nt, _noise(nt, pos, 30.0, 4.0, 0.65), 0.50, 0.66)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', f, 0.7), S['cor'], (0.170, 0.065, 0.026))
    S['rug'] = _mixf(nt, f, S['rug'], 0.9)
    gordura = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 11.0, 3.0, 0.6), 0.50, 0.70), 0.6)
    S['rug'] = _mixf(nt, gordura, S['rug'], 0.25)


forja.VELHO.update(chamine=_chamine, aluminio=_panela, chapa_fogao=_chapa)
