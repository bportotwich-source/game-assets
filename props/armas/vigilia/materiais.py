"""Classes de material do Vigília 5,56 bicolor (somadas às da M4A1 em m4a1/texturas.py)."""
import texturas

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'areia_anod': ((0.300, 0.215, 0.115), 0.52, 0.0, (0.40, 0.40, 0.41), 0.32, 1.0, 0.90, 0.40, 1.2),     # pintura caramelo sobre alumínio
    'tan_grip':   texturas.CLASSES['tan'],                                                                 # punho caramelo, com o quadriculado do polim_grip
})
# o quadriculado do punho é medido na posição da peça, e o punho foi levado 145 mm para a frente
texturas.GRIP = dict(T=(-0.160 + 0.145, -0.056), B=(-0.207 + 0.145, -0.146))
