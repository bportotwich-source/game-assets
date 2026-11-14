"""Classes de material da máquina de refrigerante, da masseira, da fritadeira e da chapa de lanchonete
(somadas às de sortidos)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_sortidos', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sortidos', 'materiais.py'))
sortidos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sortidos)
forja = sortidos.forja

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'oleo_velho':   ((0.120, 0.060, 0.010), 0.15, 0.0, (0.060, 0.040, 0.020), 0.30, 0.0, 0.30, 0.40, 1.0),   # óleo de fritura escurecido
    'botijao':      ((0.080, 0.170, 0.330), 0.45, 0.0, (0.300, 0.180, 0.110), 0.80, 0.5, 0.70, 0.40, 2.0),   # botijão de gás azul, ralado
    'gordura':      ((0.050, 0.040, 0.030), 0.35, 0.0, (0.100, 0.080, 0.060), 0.60, 0.0, 0.40, 0.80, 1.0),   # crosta queimada da chapa
    'copo_papel':   ((0.800, 0.770, 0.700), 0.80, 0.0, (0.600, 0.550, 0.450), 0.90, 0.0, 0.40, 0.60, 1.4),
})
