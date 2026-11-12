"""Classes de material da lanterna de arma (somadas às da M4A1)."""
import texturas

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'anod_gasto':  ((0.036, 0.038, 0.036), 0.50, 0.75, (0.32, 0.33, 0.34), 0.32, 1.0, 1.80, 0.30, 1.6),
    'fosf_gasto':  ((0.042, 0.042, 0.040), 0.62, 0.65, (0.30, 0.29, 0.28), 0.36, 1.0, 1.80, 0.50, 1.8),
    'serr_gasto':  ((0.040, 0.041, 0.038), 0.60, 0.65, (0.32, 0.31, 0.30), 0.34, 1.0, 2.00, 0.50, 1.8),
    'refletor':    ((0.80, 0.80, 0.78), 0.12, 1.0, (0.80, 0.80, 0.78), 0.12, 1.0, 0.0, 0.0, 0.2),
    'led_frio':    ((0.95, 0.92, 0.70), 0.30, 0.0, (0.95, 0.92, 0.70), 0.30, 0.0, 0.0, 0.0, 0.0),
})
