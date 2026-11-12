"""Classes de material das ferramentas e materiais de craft (somadas às da M4A1 e às das estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_municao', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'moveis_realistas', 'bancada_municao', 'materiais.py'))
municao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(municao)
forja = municao.forja

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'prego':    ((0.330, 0.330, 0.340), 0.42, 1.0, (0.330, 0.330, 0.340), 0.42, 1.0, 0.0, 0.40, 0.8),     # miúdo: sem desgaste de quina
    'etiqueta': ((0.640, 0.600, 0.480), 0.80, 0.0, (0.640, 0.600, 0.480), 0.80, 0.0, 0.0, 0.30, 0.4),
})
