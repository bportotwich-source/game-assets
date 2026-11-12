"""Classes de material dos itens de água (somadas às da M4A1 e às das estações de craft)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_municao', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'moveis_realistas', 'bancada_municao', 'materiais.py'))
municao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(municao)
forja = municao.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
# 'pet' e 'agua' só marcam as malhas: no GLB elas ganham material liso (gerar.py)
texturas.CLASSES.update({
    'pet':            ((0.700, 0.800, 0.850), 0.10, 0.0, (0.700, 0.800, 0.850), 0.10, 0.0, 0.0, 0.00, 0.0),
    'agua':           ((0.450, 0.650, 0.750), 0.08, 0.0, (0.450, 0.650, 0.750), 0.08, 0.0, 0.0, 0.00, 0.0),
    'tampa_vermelha': ((0.420, 0.030, 0.025), 0.45, 0.0, (0.580, 0.200, 0.150), 0.60, 0.0, 0.30, 0.30, 1.2),
    'rotulo_agua':    ((0.780, 0.800, 0.800), 0.50, 0.0, (0.780, 0.800, 0.800), 0.50, 0.0, 0.0, 0.30, 0.6),
    'rotulo_velho':   ((0.620, 0.520, 0.330), 0.75, 0.0, (0.700, 0.620, 0.450), 0.75, 0.0, 0.60, 0.80, 1.6),
    'cantil_verde':   ((0.110, 0.135, 0.065), 0.55, 0.0, (0.560, 0.570, 0.580), 0.34, 1.0, 1.40, 0.40, 1.4),   # tinta verde gasta até o alumínio
    'aluminio':       ((0.560, 0.570, 0.580), 0.34, 1.0, (0.400, 0.400, 0.410), 0.45, 1.0, 0.40, 0.30, 1.2),
    'lata_fuligem':   ((0.520, 0.530, 0.540), 0.34, 1.0, (0.300, 0.180, 0.100), 0.60, 0.6, 1.00, 0.40, 1.6),
    'arame':          ((0.230, 0.180, 0.140), 0.55, 0.5, (0.400, 0.360, 0.330), 0.40, 0.6, 0.0, 0.60, 1.2),
})


def _rotulo_agua(nt, pos, S, nome):
    """Rótulo de água mineral sem marca: faixa azul em cima e embaixo e um filete no meio."""
    x, y, z = forja._xyz(nt, pos)
    faixa = _math(nt, 'MAXIMUM', _smooth(nt, z, 0.172, 0.174), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, 0.136, 0.138)))
    filete = _math(nt, 'MULTIPLY', _smooth(nt, z, 0.151, 0.152), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, 0.158, 0.159)))
    S['cor'] = _mix(nt, faixa, S['cor'], (0.030, 0.130, 0.420))
    S['cor'] = _mix(nt, filete, S['cor'], (0.100, 0.380, 0.650))


def _rotulo_velho(nt, pos, S, nome):
    """Papel de rótulo desbotado, com manchas de água e uma faixa escura que sobrou da estampa."""
    x, y, z = forja._xyz(nt, pos)
    estampa = _math(nt, 'MULTIPLY', _smooth(nt, z, 0.092, 0.094), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, 0.108, 0.110)))
    falha = _smooth(nt, _noise(nt, pos, 60.0, 3.0, 0.6), 0.42, 0.55)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', estampa, falha), 0.8), S['cor'], (0.250, 0.060, 0.040))
    mancha = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 22.0, 3.0, 0.6), 0.50, 0.70), 0.55)
    S['cor'] = _mix(nt, mancha, S['cor'], (0.300, 0.220, 0.110))


def _fuligem(nt, pos, S, nome):
    """Lata que vai ao fogo: fundo e metade de baixo pretos de fuligem, subindo em línguas."""
    x, y, z = forja._xyz(nt, pos)
    lingua = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.15), 55.0, 3.0, 0.6)
    f = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'SUBTRACT', z, _math(nt, 'MULTIPLY', lingua, 0.035)), 0.012, 0.040))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', f, 0.94), S['cor'], (0.012, 0.011, 0.010))
    S['rug'] = _mixf(nt, f, S['rug'], 0.92)
    S['met'] = _mixf(nt, f, S['met'], 0.10)


forja.VELHO.update(rotulo_agua=_rotulo_agua, rotulo_velho=_rotulo_velho, lata_fuligem=_fuligem)
