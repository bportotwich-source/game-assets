"""Classes de material das bocas de cano (somadas às da M4A1)."""
import texturas

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_boca':       ((0.030, 0.031, 0.034), 0.46, 0.85, (0.30, 0.30, 0.31), 0.32, 1.0, 0.70, 0.40, 1.0),
    'aco_boca_gasto': ((0.050, 0.050, 0.048), 0.55, 0.80, (0.34, 0.32, 0.30), 0.36, 1.0, 2.00, 0.55, 2.0),
    'ceramica_tan':   ((0.290, 0.200, 0.100), 0.62, 0.20, (0.10, 0.10, 0.10), 0.40, 0.9, 0.90, 0.30, 1.2),
    'fuligem':        ((0.012, 0.012, 0.012), 0.85, 0.30, (0.012, 0.012, 0.012), 0.85, 0.30, 0.0, 0.5, 1.5),
})
