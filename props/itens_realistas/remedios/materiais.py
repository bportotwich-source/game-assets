"""Classes de material dos remédios (somadas às da comida e, por ela, às das ferramentas e das estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_comida', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'comida', 'materiais.py'))
comida = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comida)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'plastico_verm':  ((0.480, 0.028, 0.022), 0.42, 0.0, (0.560, 0.120, 0.100), 0.50, 0.0, 0.06, 0.30, 1.2),
    'plastico_branco': ((0.700, 0.700, 0.680), 0.40, 0.0, (0.700, 0.700, 0.680), 0.40, 0.0, 0.0, 0.30, 1.0),
    'frasco_laranja': ((0.620, 0.210, 0.020), 0.18, 0.0, (0.620, 0.210, 0.020), 0.18, 0.0, 0.0, 0.10, 0.5),
    'frasco_claro':   ((0.560, 0.640, 0.700), 0.22, 0.0, (0.560, 0.640, 0.700), 0.22, 0.0, 0.0, 0.10, 0.6),
    'seringa_corpo':  ((0.680, 0.720, 0.740), 0.14, 0.0, (0.680, 0.720, 0.740), 0.14, 0.0, 0.0, 0.10, 0.4),
    'remedio_liq':    ((0.560, 0.400, 0.090), 0.12, 0.0, (0.560, 0.400, 0.090), 0.12, 0.0, 0.0, 0.10, 0.2),
    'gaze':           ((0.720, 0.700, 0.640), 0.92, 0.0, (0.720, 0.700, 0.640), 0.92, 0.0, 0.0, 1.40, 0.9),
    'linha_verm':     ((0.480, 0.030, 0.030), 0.75, 0.0, (0.480, 0.030, 0.030), 0.75, 0.0, 0.0, 1.20, 0.4),
    'linha_preta':    ((0.030, 0.030, 0.035), 0.75, 0.0, (0.030, 0.030, 0.035), 0.75, 0.0, 0.0, 1.20, 0.4),
    'cha_verde':      ((0.090, 0.150, 0.030), 0.14, 0.0, (0.090, 0.150, 0.030), 0.14, 0.0, 0.0, 0.10, 0.3),
})
texturas.RELEVO['gaze'] = comida._manchas(900.0, 0.0004)
