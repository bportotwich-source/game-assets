"""Classes de material das caixas de itens (somadas às dos remédios e, por eles, às da comida, das ferramentas e das estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_remedios', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'remedios', 'materiais.py'))
remedios = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(remedios)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    # plástico rígido moldado: fosco, quinas esbranquiçadas de arrastar, pó nos rebaixos
    'caixa_grafite': ((0.060, 0.066, 0.072), 0.58, 0.0, (0.230, 0.240, 0.250), 0.66, 0.0, 0.55, 0.90, 2.0),
    'caixa_verde':   ((0.060, 0.082, 0.050), 0.60, 0.0, (0.240, 0.260, 0.200), 0.68, 0.0, 0.55, 0.90, 2.0),
    'caixa_oliva':   ((0.105, 0.110, 0.070), 0.60, 0.0, (0.300, 0.300, 0.230), 0.68, 0.0, 0.55, 0.90, 2.0),
    'caixa_branca':  ((0.620, 0.620, 0.590), 0.50, 0.0, (0.420, 0.410, 0.380), 0.62, 0.0, 0.35, 0.70, 2.2),
    'fecho_metal':   ((0.360, 0.365, 0.370), 0.40, 1.0, (0.600, 0.600, 0.600), 0.30, 1.0, 0.50, 0.40, 1.6),
    'ziper':         ((0.020, 0.020, 0.022), 0.50, 0.0, (0.300, 0.300, 0.300), 0.40, 1.0, 0.40, 0.60, 1.4),
})
