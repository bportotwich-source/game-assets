"""Classes de material do armário de armas (somadas às da M4A1 em armas/m4a1/texturas.py)."""
import texturas

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'chapa_verde':   ((0.034, 0.050, 0.041), 0.46, 0.0, (0.30, 0.30, 0.31), 0.36, 1.0, 1.50, 0.35, 1.3),   # esmalte verde-acinzentado sobre aço
    'chapa_escura':  ((0.030, 0.034, 0.034), 0.50, 0.0, (0.28, 0.28, 0.29), 0.38, 1.0, 1.40, 0.35, 1.5),   # rodapé e reforços
    'chapa_clara':   ((0.115, 0.120, 0.112), 0.50, 0.0, (0.33, 0.33, 0.34), 0.36, 1.0, 1.10, 0.35, 1.4),   # pintura de dentro
    'chapa_veneziana': ((0.034, 0.050, 0.041), 0.46, 0.0, (0.30, 0.30, 0.31), 0.36, 1.0, 0.45, 0.35, 1.6),  # mesma tinta, estampado fino gasta menos
    'feltro':        ((0.022, 0.060, 0.034), 0.96, 0.0, (0.050, 0.090, 0.055), 0.96, 0.0, 0.50, 1.60, 1.0),
    'zincado':       ((0.46, 0.47, 0.47), 0.42, 1.0, (0.62, 0.62, 0.62), 0.30, 1.0, 0.60, 0.40, 1.3),
    'tinta_branca':  ((0.72, 0.72, 0.66), 0.62, 0.0, None, 0, 0, 0, 0, 0),
    'tinta_amarela': ((0.70, 0.52, 0.05), 0.60, 0.0, None, 0, 0, 0, 0, 0),
})
