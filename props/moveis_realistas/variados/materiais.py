"""Classes de material do carrinho de emergência, do porta-pallet, da prateleira de pães e do beliche (somadas às de publico)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_publico', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'publico', 'materiais.py'))
publico = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(publico)
forja = publico.forja
quarto = publico.quarto

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'longarina':      ((0.600, 0.200, 0.020), 0.45, 0.0, (0.250, 0.150, 0.100), 0.75, 0.4, 0.60, 0.30, 1.8),   # laranja de porta-pallet
    'coluna_azul':    ((0.030, 0.090, 0.250), 0.45, 0.0, (0.250, 0.200, 0.150), 0.75, 0.4, 0.60, 0.30, 1.8),
    'pao':            ((0.480, 0.250, 0.080), 0.70, 0.0, (0.300, 0.250, 0.200), 0.85, 0.0, 0.40, 0.60, 1.3),
    'pao_claro':      ((0.620, 0.420, 0.200), 0.70, 0.0, (0.420, 0.380, 0.300), 0.85, 0.0, 0.40, 0.60, 1.3),
    'vermelho_carro': ((0.450, 0.030, 0.030), 0.40, 0.0, (0.300, 0.200, 0.180), 0.65, 0.0, 0.40, 0.25, 1.6),   # carrinho de emergência
    'aco_beliche':    ((0.150, 0.180, 0.160), 0.45, 0.0, (0.220, 0.120, 0.060), 0.80, 0.4, 0.70, 0.35, 1.8),
})
