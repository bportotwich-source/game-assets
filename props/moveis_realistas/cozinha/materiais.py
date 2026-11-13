"""Classes de material dos móveis de cozinha (somadas às dos móveis de quarto e das estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'materiais.py'))
quarto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(quarto)
forja = quarto.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'tinta_creme': ((0.560, 0.520, 0.400), 0.40, 0.0, (0.300, 0.190, 0.095), 0.70, 0.0, 0.70, 0.35, 1.8),   # madeira pintada, lascada nas quinas
    'pedra_pia':   ((0.060, 0.060, 0.065), 0.30, 0.0, (0.090, 0.090, 0.095), 0.50, 0.0, 0.20, 0.30, 1.2),   # granito escuro polido
    'ralo':        ((0.020, 0.020, 0.022), 0.60, 0.3, (0.020, 0.020, 0.022), 0.60, 0.3, 0.0, 0.30, 1.0),
})


def _tinta(nt, pos, S, nome):
    """Armário pintado de cozinha velha: amarelado de gordura em manchas, escorridos escuros e poeira nas faces de cima."""
    x, y, z = forja._xyz(nt, pos)
    gord = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 6.0, 3.0, 0.6), 0.40, 0.75), 0.45)
    S['cor'] = _mix(nt, gord, S['cor'], (0.420, 0.330, 0.170))
    esc = _noise(nt, forja._vec(nt, x, y, z, 60.0, 60.0, 4.0), 1.0, 3.0, 0.6)
    esc = _math(nt, 'MULTIPLY', _smooth(nt, esc, 0.60, 0.80), 0.30)
    S['cor'] = _mix(nt, esc, S['cor'], (0.200, 0.160, 0.100))
    S['rug'] = _mixf(nt, gord, S['rug'], 0.62)
    po = _math(nt, 'MULTIPLY', quarto._cima(nt), 0.35)
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))


def _pedra(nt, pos, S, nome):
    """Granito: pintas claras e cinzas miúdas, e marcas foscas de água."""
    a = _smooth(nt, _noise(nt, pos, 260.0, 2.0, 0.5), 0.60, 0.66)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', a, 0.85), S['cor'], (0.420, 0.410, 0.390))
    b = _smooth(nt, _noise(nt, pos, 140.0, 2.0, 0.5), 0.58, 0.64)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', b, 0.70), S['cor'], (0.170, 0.150, 0.140))
    fosco = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 9.0, 3.0, 0.6), 0.50, 0.75), 0.5)
    S['rug'] = _mixf(nt, fosco, S['rug'], 0.60)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', fosco, 0.25), S['cor'], (0.300, 0.290, 0.270))


forja.VELHO.update(tinta_creme=_tinta, pedra_pia=_pedra)
