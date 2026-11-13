"""Classes de material dos móveis de banheiro (somadas às da cozinha: tinta creme, esmalte, plástico)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_cozinha', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cozinha', 'materiais.py'))
cozinha = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cozinha)
forja = cozinha.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'louca':     ((0.660, 0.660, 0.630), 0.12, 0.0, (0.350, 0.300, 0.220), 0.60, 0.0, 0.25, 0.20, 2.0),   # louça branca vitrificada
    'agua_vaso': ((0.030, 0.050, 0.040), 0.05, 0.0, (0.030, 0.050, 0.040), 0.05, 0.0, 0.0, 0.20, 1.0),
    'espelho':   ((0.780, 0.800, 0.810), 0.05, 1.0, (0.090, 0.080, 0.070), 0.55, 0.2, 0.0, 0.10, 1.0),
    'vidro_fosco': ((0.620, 0.620, 0.580), 0.55, 0.0, (0.620, 0.620, 0.580), 0.55, 0.0, 0.0, 0.20, 1.4),
})


def _louca(nt, pos, S, nome):
    """Louça de banheiro abandonado: encardida em manchas, escorridos de ferrugem e calcário, poeira em cima."""
    cozinha._tinta(nt, pos, S, nome, forca=0.30)


def _espelho(nt, pos, S, nome):
    """Espelho velho: manchas pretas onde a prata descascou e um véu de poeira que tira o brilho."""
    m = _smooth(nt, _noise(nt, pos, 22.0, 4.0, 0.65), 0.66, 0.74)
    S['cor'] = _mix(nt, m, S['cor'], (0.050, 0.045, 0.040))
    S['rug'] = _mixf(nt, m, S['rug'], 0.55)
    v = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 5.0, 3.0, 0.6), 0.35, 0.75), 0.22)
    S['rug'] = _mixf(nt, v, S['rug'], 0.60)


forja.VELHO.update(louca=_louca, espelho=_espelho, vidro_fosco=cozinha._esmalte)
