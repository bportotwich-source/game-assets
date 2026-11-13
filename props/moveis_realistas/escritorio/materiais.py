"""Classes de material da mesa de escritório, do rack, da TV de tubo e do calendário (somadas às da decoração)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_decoracao', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'decoracao', 'materiais.py'))
decoracao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(decoracao)
cozinha = decoracao.cozinha
forja = decoracao.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_mesa':   ((0.230, 0.240, 0.235), 0.42, 0.0, (0.320, 0.320, 0.330), 0.36, 1.0, 1.10, 0.40, 1.7),   # esmalte cinza de escritório
    'formica':    ((0.520, 0.470, 0.380), 0.35, 0.0, (0.300, 0.230, 0.150), 0.70, 0.0, 0.35, 0.30, 1.8),   # laminado bege, quina lascada
    'tecla':      ((0.330, 0.300, 0.240), 0.55, 0.0, (0.420, 0.390, 0.330), 0.40, 0.0, 0.50, 0.50, 2.0),
    'vidro_caco': ((0.550, 0.580, 0.570), 0.30, 0.0, (0.550, 0.580, 0.570), 0.30, 0.0, 0.0, 0.10, 1.0),    # risco de trinca
    'cal_papel':  ((0.600, 0.580, 0.500), 0.80, 0.0, (0.600, 0.580, 0.500), 0.80, 0.0, 0.0, 0.40, 1.5),
    'cal_ceu':    ((0.300, 0.450, 0.560), 0.60, 0.0, (0.300, 0.450, 0.560), 0.60, 0.0, 0.0, 0.30, 1.3),
    'cal_morro':  ((0.130, 0.250, 0.110), 0.60, 0.0, (0.130, 0.250, 0.110), 0.60, 0.0, 0.0, 0.30, 1.3),
    'cal_morro2': ((0.200, 0.330, 0.180), 0.60, 0.0, (0.200, 0.330, 0.180), 0.60, 0.0, 0.0, 0.30, 1.3),
    'cal_sol':    ((0.800, 0.620, 0.200), 0.60, 0.0, (0.800, 0.620, 0.200), 0.60, 0.0, 0.0, 0.30, 1.3),
    'cal_faixa':  ((0.400, 0.060, 0.045), 0.60, 0.0, (0.400, 0.060, 0.045), 0.60, 0.0, 0.0, 0.30, 1.3),
    'cal_letra':  ((0.550, 0.550, 0.500), 0.70, 0.0, (0.550, 0.550, 0.500), 0.70, 0.0, 0.0, 0.20, 1.0),
})


def _po(nt, pos, S, nome):
    """Poeira nas faces de cima."""
    po = _math(nt, 'MULTIPLY', cozinha.quarto._cima(nt), 0.40)
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))
    S['rug'] = _mixf(nt, po, S['rug'], 0.85)


forja.VELHO.update(aco_mesa=_po, formica=_po, cal_papel=decoracao._foto, cal_ceu=decoracao._foto, cal_morro=decoracao._foto, cal_morro2=decoracao._foto)
