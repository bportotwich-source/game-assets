"""Classes de material do baú de aço (somadas às da M4A1 e às dos outros móveis realistas:
madeiras da carpintaria, envelhecimento da forja, esmaltes das bancadas)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_bancada_trabalho', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bancada_trabalho', 'materiais.py'))
bancada = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bancada)
forja = bancada.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_ocre':  ((0.400, 0.235, 0.022), 0.50, 0.0, (0.200, 0.085, 0.036), 0.85, 0.3, 1.60, 0.60, 2.2),    # cantoneira pintada de amarelo de obra
    'zinco':     ((0.300, 0.315, 0.320), 0.46, 0.9, (0.480, 0.490, 0.500), 0.36, 1.0, 0.50, 0.50, 2.0),    # chapa ondulada galvanizada
    'cadeado':   ((0.560, 0.400, 0.130), 0.38, 1.0, (0.700, 0.540, 0.240), 0.30, 1.0, 0.80, 0.30, 1.6),    # corpo de latão do cadeado
})


def _zinco(nt, pos, S, nome):
    """Chapa galvanizada velha: flor do zinco apagada, ferrugem escorrida de cima para baixo e pé comido."""
    x, y, z = forja._xyz(nt, pos)
    flor = _noise(nt, pos, 60.0, 2.0, 0.5)
    S['cor'] = forja.madeira._tom(nt, S['cor'], _math(nt, 'ADD', 0.72, _math(nt, 'MULTIPLY', flor, 0.56)))
    escorrido = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.06), 15.0, 3.0, 0.6)
    mancha = _noise(nt, pos, 4.5, 4.0, 0.62)
    f = _smooth(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', mancha, 0.55), _math(nt, 'MULTIPLY', escorrido, 0.50)), 0.52, 0.63)
    pe = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, 0.10, 0.26)), _smooth(nt, _noise(nt, pos, 24.0, 3.0, 0.6), 0.30, 0.55))
    f = _math(nt, 'MAXIMUM', _math(nt, 'MULTIPLY', f, 0.85), pe)
    ferr = _mix(nt, _smooth(nt, _noise(nt, pos, 70.0, 3.0, 0.6), 0.3, 0.7), (0.210, 0.080, 0.030), (0.090, 0.038, 0.018))
    S['cor'] = _mix(nt, f, S['cor'], ferr)
    S['rug'] = _mixf(nt, f, S['rug'], 0.90)
    S['met'] = _mixf(nt, f, S['met'], 0.15)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', f, _noise(nt, pos, 500.0, 2.0, 0.6)), 0.0006))


forja.VELHO.update(aco_ocre=bancada._lascado, zinco=_zinco)
