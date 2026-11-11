"""Classes de material do Atalaia .308 (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'verde_anod':  ((0.105, 0.125, 0.062), 0.55, 0.0, (0.36, 0.37, 0.37), 0.32, 1.0, 0.85, 0.40, 1.2),    # pintura verde-oliva sobre alumínio
    'verde_polim': ((0.095, 0.115, 0.060), 0.60, 0.0, (0.16, 0.19, 0.11), 0.42, 0.0, 0.70, 0.60, 1.3),    # polímero verde-oliva
})
texturas.CLASSES['verde_grip'] = texturas.CLASSES['verde_polim']                                         # punho, com o quadriculado do polim_grip
# o quadriculado do punho é medido na posição da peça: o punho foi levado para o receptor aumentado e 158 mm para a frente
texturas.GRIP = dict(T=(-0.160 - 0.016 + 0.158, -0.056 - 0.0056), B=(-0.207 - 0.016 + 0.158, -0.146 - 0.0056))
