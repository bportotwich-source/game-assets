"""Classes de material dos sinais de saque, da pilha de livros e do tambor (somadas às de servicos)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_servicos', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'servicos', 'materiais.py'))
servicos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(servicos)
forja = servicos.forja
quarto = servicos.quarto

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'estofado_verde': quarto._pano_cls((0.070, 0.115, 0.075)),
    'tacha':          ((0.380, 0.250, 0.080), 0.40, 1.0, (0.700, 0.520, 0.220), 0.28, 1.0, 0.80, 0.30, 1.2),
    'lasca':          ((0.300, 0.220, 0.140), 0.80, 0.0, (0.300, 0.220, 0.140), 0.80, 0.0, 0.0, 0.50, 1.2),   # madeira clara da quebra
    'pasta_parda':    ((0.420, 0.300, 0.150), 0.80, 0.0, (0.420, 0.300, 0.150), 0.80, 0.0, 0.30, 0.40, 1.5),
    'carimbo_azul':   ((0.050, 0.080, 0.300), 0.80, 0.0, (0.050, 0.080, 0.300), 0.80, 0.0, 0.0, 0.40, 1.0),
})
forja.VELHO.update(estofado_verde=forja.VELHO['pano_cru'])
