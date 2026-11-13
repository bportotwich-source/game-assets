"""Classes de material da lixeira, da mala, do aquecedor e do desenho de criança (somadas às do escritório)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_escritorio', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'escritorio', 'materiais.py'))
escritorio = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(escritorio)
forja = escritorio.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise


def _pano(cor):
    claro = tuple(min(1.0, c * 1.5 + 0.03) for c in cor)
    return (cor, 0.92, 0.0, claro, 0.90, 0.0, 0.50, 1.20, 1.6)


# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'plastico_verde': ((0.035, 0.120, 0.050), 0.55, 0.0, (0.120, 0.180, 0.120), 0.70, 0.0, 0.80, 0.70, 2.4),   # PEAD de lixeira, riscado
    'saco_lixo':      ((0.010, 0.010, 0.012), 0.22, 0.0, (0.010, 0.010, 0.012), 0.30, 0.0, 0.0, 0.30, 1.6),
    'mala_azul':      _pano((0.030, 0.060, 0.140)),                                                          # náilon da mala
    'forro_mala':     _pano((0.180, 0.150, 0.110)),
    'roupa_vermelha': _pano((0.250, 0.040, 0.035)),
    'roupa_cinza':    _pano((0.200, 0.200, 0.190)),
    'jeans':          _pano((0.050, 0.080, 0.150)),
    'giz_vermelho':   ((0.550, 0.070, 0.050), 0.85, 0.0, (0.550, 0.070, 0.050), 0.85, 0.0, 0.0, 0.70, 1.0),
    'giz_azul':       ((0.050, 0.150, 0.500), 0.85, 0.0, (0.050, 0.150, 0.500), 0.85, 0.0, 0.0, 0.70, 1.0),
    'giz_verde':      ((0.080, 0.330, 0.060), 0.85, 0.0, (0.080, 0.330, 0.060), 0.85, 0.0, 0.0, 0.70, 1.0),
    'giz_amarelo':    ((0.750, 0.560, 0.040), 0.85, 0.0, (0.750, 0.560, 0.040), 0.85, 0.0, 0.0, 0.70, 1.0),
    'giz_marrom':     ((0.200, 0.100, 0.040), 0.85, 0.0, (0.200, 0.100, 0.040), 0.85, 0.0, 0.0, 0.70, 1.0),
    'folha_sulfite':  ((0.640, 0.630, 0.580), 0.85, 0.0, (0.640, 0.630, 0.580), 0.85, 0.0, 0.0, 0.40, 1.5),
    'fita_crepe':     ((0.520, 0.450, 0.300), 0.70, 0.0, (0.520, 0.450, 0.300), 0.70, 0.0, 0.0, 0.40, 1.3),
})


def _plastico_rua(nt, pos, S, nome):
    """Lixeira de rua: escorridos escuros de cima para baixo e o verde desbotado pelo sol nas faces de cima."""
    m = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 6.0, 4.0, 0.6), 0.45, 0.80), 0.55)
    S['cor'] = _mix(nt, m, S['cor'], (0.030, 0.035, 0.025))
    sol = _math(nt, 'MULTIPLY', escritorio.cozinha.quarto._cima(nt), 0.45)
    S['cor'] = _mix(nt, sol, S['cor'], (0.140, 0.200, 0.140))


forja.VELHO.update(plastico_verde=_plastico_rua, folha_sulfite=escritorio.decoracao._foto,
                   **{k: forja.VELHO['pano_cru'] for k in ('mala_azul', 'forro_mala', 'roupa_vermelha', 'roupa_cinza', 'jeans')})
