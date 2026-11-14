"""Classes de material da vitrine de tortas, do carrinho de assadeiras, da bicicleta e do carrinho de mão
(somadas às de abrigo)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_abrigo', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'abrigo', 'materiais.py'))
abrigo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(abrigo)
forja = abrigo.forja
quarto = abrigo.quarto

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'massa_assada':  ((0.500, 0.270, 0.090), 0.70, 0.0, (0.330, 0.250, 0.180), 0.85, 0.0, 0.40, 0.60, 1.3),   # massa de torta e pão (passada: escurece)
    'massa_clara':   ((0.640, 0.450, 0.220), 0.70, 0.0, (0.430, 0.380, 0.300), 0.85, 0.0, 0.40, 0.60, 1.3),
    'recheio_morango': ((0.300, 0.030, 0.040), 0.35, 0.0, (0.200, 0.080, 0.060), 0.60, 0.0, 0.30, 0.40, 1.0),
    'recheio_creme': ((0.700, 0.620, 0.420), 0.40, 0.0, (0.500, 0.450, 0.350), 0.60, 0.0, 0.30, 0.40, 1.0),
    'mofo':          ((0.300, 0.330, 0.250), 0.95, 0.0, (0.200, 0.220, 0.180), 0.95, 0.0, 0.20, 2.00, 0.8),   # bolor verde-acinzentado
    'assadeira':     ((0.260, 0.240, 0.220), 0.50, 0.8, (0.420, 0.410, 0.400), 0.40, 1.0, 0.70, 0.40, 2.2),   # alumínio queimado de forno
    'quadro_bici':   ((0.350, 0.035, 0.030), 0.35, 0.0, (0.300, 0.200, 0.180), 0.70, 0.5, 0.80, 0.30, 1.8),   # quadro vermelho pintado
    'banco_bici':    ((0.030, 0.030, 0.030), 0.55, 0.0, (0.150, 0.140, 0.130), 0.70, 0.0, 0.50, 0.60, 1.4),
    'cacamba_verde': ((0.060, 0.180, 0.080), 0.50, 0.0, (0.250, 0.130, 0.060), 0.85, 0.4, 1.00, 0.50, 2.4),   # caçamba pintada e enferrujada
    'cabo_madeira_x': ((0.400, 0.260, 0.130), 0.60, 0.0, (0.550, 0.420, 0.280), 0.70, 0.0, 0.60, 1.00, 2.0),
    'areia':         ((0.400, 0.330, 0.220), 0.95, 0.0, (0.350, 0.300, 0.220), 0.95, 0.0, 0.10, 2.40, 1.2),
})
forja.madeira.COR['cabo_madeira_x'] = forja.madeira.cor_madeira('cabo_madeira_x')
texturas.RELEVO['cabo_madeira_x'] = forja.madeira.relevo_madeira('cabo_madeira_x')
