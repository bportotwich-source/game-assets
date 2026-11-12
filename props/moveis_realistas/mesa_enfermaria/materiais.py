"""Classes de material da mesa de enfermaria (somadas às da M4A1 e às das outras bancadas)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_bancada_costura', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bancada_costura', 'materiais.py'))
costura = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(costura)
forja = costura.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'colchao':        costura._pano_cls((0.480, 0.440, 0.360)),
    'lencol':         costura._pano_cls((0.560, 0.550, 0.510)),
    'cobertor':       costura._pano_cls((0.115, 0.125, 0.120)),
    'fronha':         costura._pano_cls((0.520, 0.510, 0.460)),
    'esmalte_branco': ((0.620, 0.620, 0.590), 0.26, 0.0, (0.030, 0.030, 0.032), 0.50, 0.6, 0.45, 0.30, 1.6),   # ágata: lasca preta nas bordas
    'cruz_branca':    ((0.560, 0.560, 0.530), 0.60, 0.0, (0.560, 0.560, 0.530), 0.60, 0.0, 0.0, 0.40, 1.2),   # tinta a pincel
    'cruz_vermelha':  ((0.400, 0.030, 0.022), 0.60, 0.0, (0.400, 0.030, 0.022), 0.60, 0.0, 0.0, 0.40, 1.2),
    'vidro_ambar':    ((0.160, 0.060, 0.012), 0.10, 0.0, (0.160, 0.060, 0.012), 0.10, 0.0, 0.0, 0.20, 1.0),
    'vidro_soro':     ((0.420, 0.470, 0.450), 0.08, 0.0, (0.420, 0.470, 0.450), 0.08, 0.0, 0.0, 0.20, 0.8),
    'borracha_soro':  ((0.380, 0.250, 0.110), 0.55, 0.0, (0.380, 0.250, 0.110), 0.55, 0.0, 0.0, 0.40, 1.2),
})


def _colchao(nt, pos, S, nome):
    """Colchão de listras azuis ao comprido, encardido."""
    costura._pano(nt, pos, S, nome)
    x, y, z = forja._xyz(nt, pos)
    f = _math(nt, 'FRACT', _math(nt, 'DIVIDE', _math(nt, 'ADD', y, 10.0), 0.085))
    lista = _math(nt, 'SUBTRACT', _smooth(nt, f, 0.30, 0.33), _smooth(nt, f, 0.55, 0.58))
    fina = _math(nt, 'SUBTRACT', _smooth(nt, f, 0.72, 0.74), _smooth(nt, f, 0.78, 0.80))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', _math(nt, 'MAXIMUM', lista, fina), 0.85), S['cor'], (0.070, 0.110, 0.200))
    encardido = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 5.0, 3.0, 0.6), 0.45, 0.70), 0.45)
    S['cor'] = _mix(nt, encardido, S['cor'], (0.200, 0.140, 0.070))


def _lencol(nt, pos, S, nome):
    """Lençol lavado muitas vezes: amarelado em manchas e umas marcas velhas, castanhas."""
    costura._pano(nt, pos, S, nome)
    amarelo = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 4.0, 3.0, 0.6), 0.40, 0.70), 0.35)
    S['cor'] = _mix(nt, amarelo, S['cor'], (0.420, 0.340, 0.180))
    marca = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 7.5, 3.0, 0.55), 0.66, 0.70), 0.55)
    S['cor'] = _mix(nt, marca, S['cor'], (0.170, 0.070, 0.045))


def _cobertor(nt, pos, S, nome):
    """Cobertor de lã cinza: felpudo, com duas listras claras perto da barra."""
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _noise(nt, pos, 900.0, 2.0, 0.6), 0.0006))
    dobra = _smooth(nt, _noise(nt, pos, 7.0, 3.0, 0.6), 0.35, 0.70)
    S['cor'] = forja.madeira._tom(nt, S['cor'], _math(nt, 'ADD', 0.65, _math(nt, 'MULTIPLY', dobra, 0.65)))
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', dobra, 0.004))
    x, y, z = forja._xyz(nt, pos)
    l1 = _math(nt, 'SUBTRACT', _smooth(nt, x, 0.70, 0.705), _smooth(nt, x, 0.74, 0.745))
    l2 = _math(nt, 'SUBTRACT', _smooth(nt, x, 0.77, 0.775), _smooth(nt, x, 0.79, 0.795))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', _math(nt, 'MAXIMUM', l1, l2), 0.8), S['cor'], (0.330, 0.300, 0.240))


forja.VELHO.update(colchao=_colchao, lencol=_lencol, fronha=_lencol, cobertor=_cobertor)
