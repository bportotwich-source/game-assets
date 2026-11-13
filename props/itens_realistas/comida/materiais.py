"""Classes de material da comida embalada (somadas às da M4A1, às das estações e às das ferramentas)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_ferramentas', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ferramentas', 'materiais.py'))
ferramentas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ferramentas)
forja = ferramentas.forja


def _estampa(cor, rug=0.55, gasto=0.30, sujeira=1.2):
    """Tinta de embalagem: gasta nas quinas até o papel claro."""
    return (cor, rug, 0.0, (0.600, 0.560, 0.480), 0.75, 0.0, gasto, 0.30, sujeira)


# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'rot_vermelho': _estampa((0.430, 0.030, 0.022)),
    'rot_marrom':   _estampa((0.210, 0.075, 0.030)),
    'rot_creme':    _estampa((0.640, 0.540, 0.360)),
    'rot_verde':    _estampa((0.050, 0.240, 0.060)),
    'rot_amarelo':  _estampa((0.720, 0.480, 0.030)),
    'rot_azul':     _estampa((0.030, 0.110, 0.380)),
    'rot_laranja':  _estampa((0.700, 0.230, 0.020)),
    'rot_branco':   _estampa((0.700, 0.700, 0.680)),
    'letra_amarela': ((0.800, 0.600, 0.050), 0.55, 0.0, (0.800, 0.600, 0.050), 0.55, 0.0, 0.0, 0.30, 0.8),
    'letra_azul':    ((0.030, 0.100, 0.380), 0.55, 0.0, (0.030, 0.100, 0.380), 0.55, 0.0, 0.0, 0.30, 0.8),
    'letra_vermelha': ((0.450, 0.030, 0.022), 0.55, 0.0, (0.450, 0.030, 0.022), 0.55, 0.0, 0.0, 0.30, 0.8),
    # sacos plásticos: lisos, com brilho, sem desgaste de quina
    'saco_branco':  ((0.720, 0.720, 0.700), 0.32, 0.0, (0.720, 0.720, 0.700), 0.32, 0.0, 0.0, 0.15, 0.9),
    'saco_azul':    ((0.030, 0.110, 0.400), 0.30, 0.0, (0.030, 0.110, 0.400), 0.30, 0.0, 0.0, 0.15, 0.9),
    'saco_laranja': ((0.720, 0.250, 0.020), 0.26, 0.0, (0.720, 0.250, 0.020), 0.26, 0.0, 0.0, 0.15, 0.9),
    'saco_vermelho': ((0.450, 0.030, 0.022), 0.26, 0.0, (0.450, 0.030, 0.022), 0.26, 0.0, 0.0, 0.15, 0.9),
    'folha_aluminio': ((0.620, 0.620, 0.630), 0.30, 1.0, (0.620, 0.620, 0.630), 0.30, 1.0, 0.0, 0.50, 0.6),
    'chocolate':    ((0.085, 0.036, 0.016), 0.42, 0.0, (0.150, 0.075, 0.040), 0.50, 0.0, 0.35, 0.20, 0.5),
    'arroz':        ((0.760, 0.740, 0.660), 0.72, 0.0, (0.760, 0.740, 0.660), 0.72, 0.0, 0.0, 1.60, 0.3),
    'flocos':       ((0.700, 0.420, 0.080), 0.70, 0.0, (0.700, 0.420, 0.080), 0.70, 0.0, 0.0, 1.20, 0.4),
})
