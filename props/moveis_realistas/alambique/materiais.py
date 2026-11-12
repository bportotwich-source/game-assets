"""Classes de material do alambique de panela (somadas às da M4A1 e às das outras estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_filtro_barril', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'filtro_barril', 'materiais.py'))
filtro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(filtro)
forja = filtro.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'tambor_frio':  texturas.CLASSES['tambor_agua'],                                                           # o tambor da água fria, no chão
    'panela_alu':   ((0.420, 0.420, 0.420), 0.42, 1.0, (0.620, 0.620, 0.620), 0.30, 1.0, 0.60, 0.50, 1.8),    # panelão de alumínio tisnado
    'cobre_velho':  ((0.420, 0.170, 0.070), 0.36, 1.0, (0.620, 0.330, 0.170), 0.28, 1.0, 0.50, 0.40, 1.4),    # cano de cobre com azinhavre
    'agua_tambor':  ((0.020, 0.034, 0.032), 0.06, 0.0, (0.020, 0.034, 0.032), 0.06, 0.0, 0.0, 0.10, 0.3),
    'vidro_verde':  ((0.050, 0.130, 0.060), 0.08, 0.0, (0.050, 0.130, 0.060), 0.08, 0.0, 0.0, 0.20, 1.0),
    'pinga':        ((0.200, 0.190, 0.110), 0.06, 0.0, (0.200, 0.190, 0.110), 0.06, 0.0, 0.0, 0.10, 0.3),     # o destilado no vidro
    'rolha':        ((0.360, 0.240, 0.130), 0.85, 0.0, (0.460, 0.340, 0.210), 0.85, 0.0, 0.40, 1.60, 1.0),
    'cinza_fogo':   ((0.110, 0.105, 0.100), 0.96, 0.0, (0.110, 0.105, 0.100), 0.96, 0.0, 0.0, 2.40, 0.6),
    'mostrador':    ((0.560, 0.550, 0.500), 0.30, 0.0, (0.560, 0.550, 0.500), 0.30, 0.0, 0.0, 0.20, 1.0),
    'ponteiro':     ((0.300, 0.020, 0.015), 0.40, 0.0, None, 0, 0, 0, 0, 0),
})


def _panela(nt, pos, S, nome):
    """Alumínio de panela velha: fuligem lambendo de baixo para cima e amassados foscos."""
    x, y, z = forja._xyz(nt, pos)
    sobe = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.25), 14.0, 3.0, 0.6)
    f = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'SUBTRACT', z, _math(nt, 'MULTIPLY', sobe, 0.16)), 0.235, 0.335))
    f = _math(nt, 'MAXIMUM', _math(nt, 'MULTIPLY', f, 0.94), _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 20.0, 3.0, 0.6), 0.50, 0.75), 0.45))
    S['cor'] = _mix(nt, f, S['cor'], (0.020, 0.018, 0.016))
    S['rug'] = _mixf(nt, f, S['rug'], 0.88)
    S['met'] = _mixf(nt, f, S['met'], 0.15)
    fosco = _smooth(nt, _noise(nt, pos, 9.0, 3.0, 0.6), 0.45, 0.70)
    S['rug'] = _mixf(nt, _math(nt, 'MULTIPLY', fosco, 0.5), S['rug'], 0.62)


def _cobre(nt, pos, S, nome):
    """Cobre de cano velho: escurecido em manchas, azinhavre verde nas emendas e onde junta água."""
    escuro = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 26.0, 4.0, 0.62), 0.38, 0.66), 0.70)
    S['cor'] = _mix(nt, escuro, S['cor'], (0.090, 0.040, 0.022))
    S['rug'] = _mixf(nt, escuro, S['rug'], 0.55)
    verde = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 60.0, 4.0, 0.65), 0.58, 0.68), 0.85)
    S['cor'] = _mix(nt, verde, S['cor'], (0.120, 0.330, 0.250))
    S['rug'] = _mixf(nt, verde, S['rug'], 0.90)
    S['met'] = _mixf(nt, verde, S['met'], 0.0)


def _vidro(nt, pos, S, nome):
    po = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 30.0, 3.0, 0.6), 0.45, 0.75), 0.30)
    S['cor'] = _mix(nt, po, S['cor'], (0.200, 0.200, 0.160))
    S['rug'] = _mixf(nt, po, S['rug'], 0.50)


forja.VELHO.update(tambor_frio=filtro.tambor_velho(0.0), panela_alu=_panela, cobre_velho=_cobre, vidro_verde=_vidro)
