"""Classes de material da mesa de recarga de munição (somadas às da M4A1 e às das outras estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_alambique', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'alambique', 'materiais.py'))
alambique = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(alambique)
forja = alambique.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'papelao':      ((0.330, 0.230, 0.130), 0.88, 0.0, (0.460, 0.360, 0.240), 0.88, 0.0, 0.50, 1.40, 1.6),
    'caixa_verde':  ((0.050, 0.110, 0.060), 0.80, 0.0, (0.400, 0.330, 0.220), 0.88, 0.0, 0.90, 1.00, 1.4),    # caixinha de munição
    'caixa_azul':   ((0.040, 0.070, 0.180), 0.80, 0.0, (0.400, 0.330, 0.220), 0.88, 0.0, 0.90, 1.00, 1.4),
    'papel':        ((0.520, 0.490, 0.400), 0.85, 0.0, (0.520, 0.490, 0.400), 0.85, 0.0, 0.0, 0.60, 1.4),     # tabela de cargas escrita à mão
    'cartucho':     ((0.330, 0.025, 0.018), 0.45, 0.0, (0.450, 0.100, 0.070), 0.55, 0.0, 0.50, 0.40, 1.2),    # cartucho de espingarda
    'letra_preta':  ((0.020, 0.020, 0.022), 0.60, 0.0, (0.020, 0.020, 0.022), 0.60, 0.0, 0.0, 0.40, 1.0),     # estêncil
    'latao_fosco':  ((0.420, 0.300, 0.110), 0.42, 1.0, (0.600, 0.450, 0.190), 0.30, 1.0, 0.50, 0.40, 1.6),    # cápsulas usadas
})


def _papel(nt, pos, S, nome):
    """Folha pautada com colunas de números a lápis (riscos miúdos), amarelada e com marca de dedo."""
    x, y, z = forja._xyz(nt, pos)
    linha = _math(nt, 'FRACT', _math(nt, 'DIVIDE', z, 0.011))
    pauta = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', linha, 0.1)), 0.02, 0.06))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', pauta, 0.35), S['cor'], (0.150, 0.220, 0.330))
    escrita = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.35), 520.0, 2.0, 0.7), 0.56, 0.62),
                    _math(nt, 'MULTIPLY', _smooth(nt, linha, 0.25, 0.35), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, linha, 0.80, 0.90))))
    coluna = _smooth(nt, _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.0), 42.0, 1.0, 0.5), 0.40, 0.46)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', escrita, coluna), 0.85), S['cor'], (0.050, 0.050, 0.060))
    velho = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 9.0, 3.0, 0.6), 0.45, 0.72), 0.45)
    S['cor'] = _mix(nt, velho, S['cor'], (0.330, 0.250, 0.130))


def _papelao(nt, pos, S, nome):
    tom = _math(nt, 'ADD', 0.72, _math(nt, 'MULTIPLY', _noise(nt, pos, 11.0, 3.0, 0.6), 0.55))
    S['cor'] = forja.madeira._tom(nt, S['cor'], tom)
    oleo = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 17.0, 3.0, 0.6), 0.58, 0.72), 0.5)
    S['cor'] = _mix(nt, oleo, S['cor'], (0.090, 0.060, 0.030))


def _latao(nt, pos, S, nome):
    """Latão de cápsula deflagrada: manchas escuras de pólvora e de dedo."""
    f = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 120.0, 3.0, 0.6), 0.45, 0.70), 0.65)
    S['cor'] = _mix(nt, f, S['cor'], (0.090, 0.060, 0.025))
    S['rug'] = _mixf(nt, f, S['rug'], 0.60)


forja.VELHO.update(papel=_papel, papelao=_papelao, caixa_verde=_papelao, caixa_azul=_papelao, latao_fosco=_latao)
