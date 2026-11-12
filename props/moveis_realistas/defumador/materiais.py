"""Classes de material do defumador (somadas às da M4A1 e às das outras estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_fogao_tambor', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fogao_tambor', 'materiais.py'))
fogao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fogao)
forja = fogao.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'zinco':       ((0.330, 0.340, 0.340), 0.46, 1.0, (0.200, 0.085, 0.036), 0.85, 0.3, 1.00, 0.60, 2.0),   # telha ondulada
    'carne_seca':  ((0.130, 0.035, 0.022), 0.48, 0.0, (0.260, 0.110, 0.050), 0.55, 0.0, 0.50, 1.40, 1.0),
    'cinza_fogo':  ((0.110, 0.105, 0.100), 0.96, 0.0, (0.110, 0.105, 0.100), 0.96, 0.0, 0.0, 2.40, 0.6),
})

# tábuas do defumador: as do tampo (manchadas), mais a fuligem que sai pelas frestas e sobe
for _e in 'xyz':
    texturas.CLASSES['fumo_' + _e] = forja.madeira.TAMPO
    forja.madeira.COR['fumo_' + _e] = forja.madeira.cor_madeira('tampo_' + _e)
    texturas.RELEVO['fumo_' + _e] = forja.madeira.relevo_madeira('tampo_' + _e)


def _fumo(nt, pos, S, nome):
    x, y, z = forja._xyz(nt, pos)
    escorrido = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.10), 9.0, 3.0, 0.6)
    alto = _smooth(nt, _math(nt, 'ADD', z, _math(nt, 'MULTIPLY', escorrido, 0.9)), 0.75, 1.85)
    f = _math(nt, 'MULTIPLY', _math(nt, 'ADD', 0.25, _math(nt, 'MULTIPLY', alto, 0.70)), _smooth(nt, escorrido, 0.25, 0.70))
    S['cor'] = _mix(nt, f, S['cor'], (0.022, 0.018, 0.015))
    S['rug'] = _mixf(nt, f, S['rug'], 0.95)


def _zinco(nt, pos, S, nome):
    """Telha de zinco: ondas ao longo da água do telhado (relevo e sombra nos vales), ferrugem escorrida."""
    x, y, z = forja._xyz(nt, pos)
    f = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'ADD', x, 10.0), 0.076)), 0.5))
    onda = _smooth(nt, f, 0.0, 0.5)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', onda, 0.016))
    S['cor'] = forja.madeira._tom(nt, S['cor'], _math(nt, 'ADD', 0.55, _math(nt, 'MULTIPLY', onda, 0.60)))
    escorrido = _noise(nt, forja._vec(nt, x, y, z, 1.0, 0.08, 1.0), 16.0, 3.0, 0.6)
    fe = _smooth(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', _noise(nt, pos, 5.0, 4.0, 0.62), 0.6), _math(nt, 'MULTIPLY', escorrido, 0.45)), 0.56, 0.66)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', fe, 0.9), S['cor'], (0.180, 0.072, 0.028))
    S['rug'] = _mixf(nt, fe, S['rug'], 0.9)
    S['met'] = _mixf(nt, fe, S['met'], 0.15)


def _carne(nt, pos, S, nome):
    """Carne defumada: fibras ao comprido, gordura clara em veios e casca escura."""
    x, y, z = forja._xyz(nt, pos)
    fibra = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.12), 140.0, 3.0, 0.6)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', fibra, 0.0015))
    gordura = _math(nt, 'MULTIPLY', _smooth(nt, fibra, 0.62, 0.72), 0.6)
    S['cor'] = _mix(nt, gordura, S['cor'], (0.420, 0.300, 0.180))
    casca = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 30.0, 3.0, 0.6), 0.45, 0.70), 0.7)
    S['cor'] = _mix(nt, casca, S['cor'], (0.030, 0.014, 0.010))


forja.VELHO.update(zinco=_zinco, carne_seca=_carne, fumo_x=_fumo, fumo_y=_fumo, fumo_z=_fumo)
