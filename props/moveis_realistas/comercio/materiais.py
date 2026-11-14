"""Classes de material do freezer de sorvete, do expositor de óleo, do relógio de ponto e da empilhadeira
(somadas às de lanchonete)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_lanchonete', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lanchonete', 'materiais.py'))
lanchonete = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lanchonete)
forja = lanchonete.forja

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'amarelo_maquina': ((0.550, 0.380, 0.020), 0.50, 0.0, (0.250, 0.180, 0.100), 0.85, 0.5, 0.90, 0.50, 2.4),   # empilhadeira pintada, ralada
    'cartao_ponto':    ((0.720, 0.680, 0.560), 0.85, 0.0, (0.550, 0.480, 0.380), 0.90, 0.0, 0.50, 0.80, 1.6),
    'frasco_oleo_1':   ((0.500, 0.380, 0.020), 0.45, 0.0, (0.350, 0.300, 0.200), 0.70, 0.0, 0.40, 0.40, 1.6),   # frascos de óleo de 1 L
    'frasco_oleo_2':   ((0.020, 0.090, 0.300), 0.45, 0.0, (0.150, 0.180, 0.250), 0.70, 0.0, 0.40, 0.40, 1.6),
    'frasco_oleo_3':   ((0.030, 0.030, 0.030), 0.45, 0.0, (0.150, 0.140, 0.130), 0.70, 0.0, 0.40, 0.40, 1.6),
    'frasco_oleo_4':   ((0.030, 0.220, 0.060), 0.45, 0.0, (0.180, 0.220, 0.150), 0.70, 0.0, 0.40, 0.40, 1.6),
})
