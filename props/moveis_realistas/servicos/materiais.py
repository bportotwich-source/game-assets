"""Classes de material do pallet, do banco de espera, da estante de biblioteca e do frigobar (somadas às da loja)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_loja', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'loja', 'materiais.py'))
loja = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(loja)
forja = loja.forja
quarto = loja.quarto
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

CAPAS = [(0.230, 0.030, 0.028), (0.030, 0.075, 0.150), (0.040, 0.110, 0.060), (0.290, 0.190, 0.090), (0.060, 0.050, 0.045), (0.300, 0.250, 0.170)]
# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'papel_livro':    ((0.560, 0.500, 0.370), 0.86, 0.0, (0.560, 0.500, 0.370), 0.86, 0.0, 0.0, 0.60, 1.4),
    'assento_azul':   ((0.020, 0.080, 0.230), 0.45, 0.0, (0.120, 0.180, 0.300), 0.60, 0.0, 0.70, 0.40, 2.0),   # polipropileno de banco de espera
    'aco_banco':      ((0.090, 0.090, 0.095), 0.45, 0.0, (0.330, 0.330, 0.340), 0.36, 1.0, 1.00, 0.40, 1.8),   # tubo pintado de grafite
    'liner_branco':   ((0.600, 0.600, 0.580), 0.30, 0.0, (0.400, 0.380, 0.330), 0.50, 0.0, 0.30, 0.20, 2.0),
    'chocolate':      ((0.250, 0.040, 0.050), 0.40, 0.0, (0.250, 0.040, 0.050), 0.40, 0.0, 0.0, 0.30, 1.2),
})
for _i, _c in enumerate(CAPAS):
    texturas.CLASSES[f'capa_{_i + 1}'] = (_c, 0.62, 0.0, tuple(min(1.0, v * 2.2 + 0.08) for v in _c), 0.80, 0.0, 1.10, 0.80, 1.6)


def _capa(nt, pos, S, nome):
    """Capa de livro velho: desbotada em manchas e com poeira em cima."""
    f = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 18.0, 3.0, 0.6), 0.45, 0.75), 0.35)
    S['cor'] = _mix(nt, f, S['cor'], (0.300, 0.260, 0.200))
    po = _math(nt, 'MULTIPLY', quarto._cima(nt), 0.55)
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))


forja.VELHO.update(aco_banco=loja._po, liner_branco=loja._po, **{f'capa_{i + 1}': _capa for i in range(len(CAPAS))})
