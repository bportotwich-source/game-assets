"""Classes de material do freezer horizontal, da mesa com máquina de escrever, do armário de remédios e da maca
(somadas às de mercado); também do globo, da cesta de compras, da cadeira de rodas e do biombo."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_mercado', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mercado', 'materiais.py'))
mercado = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mercado)
forja = mercado.forja
quarto = mercado.quarto

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'gelo':           ((0.700, 0.760, 0.800), 0.30, 0.0, (0.700, 0.760, 0.800), 0.30, 0.0, 0.0, 0.50, 0.6),
    'pote_sorvete':   ((0.600, 0.420, 0.250), 0.40, 0.0, (0.600, 0.420, 0.250), 0.40, 0.0, 0.10, 0.30, 1.0),
    'pacote_azul':    ((0.080, 0.200, 0.500), 0.35, 0.0, (0.080, 0.200, 0.500), 0.40, 0.0, 0.10, 0.30, 1.0),
    'vinil_maca':     ((0.060, 0.200, 0.220), 0.50, 0.0, (0.200, 0.250, 0.240), 0.70, 0.0, 0.40, 0.30, 1.5),
    'cinza_maquina':  ((0.180, 0.200, 0.190), 0.40, 0.0, (0.300, 0.280, 0.250), 0.60, 0.3, 0.50, 0.30, 1.5),   # máquina de escrever pintada
    'tecla_maquina':  ((0.030, 0.030, 0.030), 0.30, 0.0, (0.150, 0.150, 0.150), 0.40, 0.0, 0.30, 0.20, 1.0),
    'globo_mar':      ((0.220, 0.380, 0.480), 0.55, 0.0, (0.450, 0.420, 0.320), 0.70, 0.0, 0.50, 0.40, 1.6),   # papel envernizado amarelado
    'globo_terra':    ((0.520, 0.430, 0.220), 0.55, 0.0, (0.500, 0.420, 0.260), 0.70, 0.0, 0.40, 0.40, 1.6),
    'cortina_verde':  quarto._pano_cls((0.300, 0.420, 0.360)),
    'cinza_mesa':     ((0.250, 0.270, 0.270), 0.45, 0.0, (0.200, 0.150, 0.100), 0.80, 0.4, 0.80, 0.40, 1.8),   # mesa de aço de repartição
})
forja.VELHO.update(cortina_verde=forja.VELHO['pano_cru'])
