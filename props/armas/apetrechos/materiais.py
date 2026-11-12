"""Classes de material dos apetrechos (estribo da besta, soltador de pulso, elástico do guarda-mão)."""
import texturas

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'camara_pneu':  ((0.050, 0.036, 0.030), 0.78, 0.0, (0.10, 0.085, 0.075), 0.65, 0.0, 0.9, 0.8, 1.8),
    'aco_estribo':  ((0.030, 0.031, 0.034), 0.48, 0.85, (0.30, 0.30, 0.31), 0.32, 1.0, 1.10, 0.40, 1.2),
    'fita_nylon':   ((0.030, 0.030, 0.032), 0.85, 0.0, (0.07, 0.07, 0.07), 0.75, 0.0, 0.5, 1.6, 1.2),
    'anod_laranja': ((0.62, 0.14, 0.02), 0.42, 0.85, (0.55, 0.50, 0.46), 0.30, 1.0, 0.70, 0.25, 0.8),
})
