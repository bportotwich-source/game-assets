"""Classes de material dos móveis de depósito e escritório (somadas às dos móveis de quarto e das estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_quarto', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'quarto', 'materiais.py'))
quarto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(quarto)
forja = quarto.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_arquivo': ((0.200, 0.235, 0.215), 0.42, 0.0, (0.320, 0.320, 0.330), 0.36, 1.0, 1.20, 0.40, 1.7),   # esmalte cinza-esverdeado de escritório
    'aco_estante': ((0.400, 0.410, 0.420), 0.44, 1.0, (0.200, 0.100, 0.050), 0.80, 0.3, 0.60, 0.50, 1.8),   # cantoneira galvanizada, ferrugem nas quinas
    'fita_parda':  ((0.300, 0.190, 0.085), 0.25, 0.0, (0.300, 0.190, 0.085), 0.30, 0.0, 0.0, 0.20, 1.2),
})


def _po(nt, pos, S, nome):
    """Poeira de depósito nas faces de cima."""
    po = _math(nt, 'MULTIPLY', quarto._cima(nt), 0.45)
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))
    S['rug'] = _mixf(nt, po, S['rug'], 0.85)


forja.VELHO.update(aco_arquivo=_po, aco_estante=_po)
