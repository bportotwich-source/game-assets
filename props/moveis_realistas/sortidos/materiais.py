"""Classes de material do painel de ferramentas, da balança médica, do fichário de catálogo e da jukebox
(somadas às de utilidades)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_utilidades', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'utilidades', 'materiais.py'))
utilidades = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(utilidades)
forja = utilidades.forja

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'esmalte_balanca': ((0.620, 0.630, 0.600), 0.40, 0.0, (0.300, 0.270, 0.230), 0.70, 0.6, 0.55, 0.40, 1.6),   # ferro fundido esmaltado de cinza-claro
    'tinta_sombra':    ((0.030, 0.030, 0.030), 0.80, 0.0, (0.120, 0.100, 0.080), 0.85, 0.0, 0.40, 0.60, 1.0),   # silhueta pintada da ferramenta que sumiu
    'rotulo_disco':    ((0.420, 0.050, 0.040), 0.50, 0.0, (0.400, 0.300, 0.250), 0.70, 0.0, 0.30, 0.40, 1.0),
    'luz_tubo':        ((0.900, 0.480, 0.150), 0.30, 0.0, (0.900, 0.480, 0.150), 0.30, 0.0, 0.00, 0.20, 0.3),   # trocado pelo material aceso
    'ficha':           ((0.780, 0.740, 0.620), 0.85, 0.0, (0.600, 0.520, 0.400), 0.90, 0.0, 0.50, 0.80, 1.4),
})
