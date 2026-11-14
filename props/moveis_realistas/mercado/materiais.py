"""Classes de material da geladeira de bebidas e do carrinho de compras (somadas às de casa)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_casa', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'casa', 'materiais.py'))
casa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(casa)
forja = casa.forja
quarto = casa.quarto

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'chapa_vermelha': ((0.420, 0.030, 0.030), 0.40, 0.0, (0.300, 0.250, 0.220), 0.60, 0.0, 0.40, 0.25, 1.6),   # geladeira pintada
    'luminoso':       ((0.900, 0.880, 0.820), 0.30, 0.0, (0.700, 0.680, 0.600), 0.50, 0.0, 0.20, 0.20, 1.4),   # acrílico do letreiro
    'lata_azul':      ((0.050, 0.150, 0.450), 0.30, 1.0, (0.600, 0.600, 0.620), 0.30, 1.0, 0.30, 0.20, 1.0),
    'lata_laranja':   ((0.700, 0.250, 0.030), 0.30, 1.0, (0.600, 0.600, 0.620), 0.30, 1.0, 0.30, 0.20, 1.0),
    'pet_verde':      ((0.050, 0.250, 0.080), 0.10, 0.0, (0.050, 0.250, 0.080), 0.20, 0.0, 0.10, 0.10, 1.0),
    'refri_escuro':   ((0.060, 0.020, 0.010), 0.10, 0.0, (0.060, 0.020, 0.010), 0.20, 0.0, 0.10, 0.10, 1.0),
    'arame_cromo':    ((0.650, 0.650, 0.660), 0.25, 1.0, (0.350, 0.250, 0.180), 0.70, 0.6, 0.55, 0.35, 1.5),
    'plastico_vermelho': ((0.450, 0.030, 0.020), 0.45, 0.0, (0.350, 0.100, 0.080), 0.60, 0.0, 0.30, 0.30, 1.4),
})
