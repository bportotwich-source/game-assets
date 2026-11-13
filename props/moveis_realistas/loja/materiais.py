"""Classes de material da gôndola, do balcão de caixa, do armário de vestiário e da banqueta (somadas às de diversos)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_diversos', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'diversos', 'materiais.py'))
diversos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(diversos)
forja = diversos.forja
quarto = diversos.escritorio.cozinha.quarto
from texturas import _n, _math, _mix, _mixf, _smooth, _noise


def _liso(cor, rug=0.45, suj=1.2):
    return (cor, rug, 0.0, cor, rug, 0.0, 0.0, 0.3, suj)


# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'gondola_branca':    ((0.600, 0.605, 0.580), 0.34, 0.0, (0.200, 0.095, 0.040), 0.80, 0.3, 0.70, 0.30, 2.0),   # chapa pintada, ferrugem nas quinas
    'etiqueta_amarela':  ((0.700, 0.520, 0.020), 0.40, 0.0, (0.600, 0.500, 0.250), 0.50, 0.0, 0.40, 0.30, 1.6),
    'furo':              _liso((0.006, 0.006, 0.006), 0.9, 0.5),
    'rotulo_verde':      _liso((0.050, 0.250, 0.060)),
    'rotulo_vermelho':   _liso((0.450, 0.040, 0.030)),
    'caixa_cereal':      ((0.500, 0.120, 0.030), 0.60, 0.0, (0.400, 0.300, 0.200), 0.70, 0.0, 0.50, 0.40, 1.6),
    'caixa_azul_pac':    ((0.050, 0.150, 0.420), 0.60, 0.0, (0.400, 0.350, 0.250), 0.70, 0.0, 0.50, 0.40, 1.6),
    'pet':               ((0.300, 0.420, 0.420), 0.12, 0.0, (0.300, 0.420, 0.420), 0.20, 0.0, 0.0, 0.20, 1.4),
    'laminado_branco':   ((0.560, 0.555, 0.530), 0.40, 0.0, (0.300, 0.250, 0.180), 0.70, 0.0, 0.60, 0.30, 2.0),   # fórmica branca, lascada na quina
    'granito':           ((0.090, 0.088, 0.090), 0.22, 0.0, (0.130, 0.130, 0.130), 0.40, 0.0, 0.30, 0.30, 1.4),
    'plastico_cinza':    ((0.200, 0.205, 0.210), 0.50, 0.0, (0.320, 0.320, 0.320), 0.45, 0.0, 0.60, 0.60, 1.8),
    'vidro_leitor':      ((0.120, 0.010, 0.008), 0.08, 0.0, (0.120, 0.010, 0.008), 0.10, 0.0, 0.0, 0.10, 0.8),
    'vidro_visor':       ((0.010, 0.040, 0.030), 0.10, 0.0, (0.010, 0.040, 0.030), 0.12, 0.0, 0.0, 0.10, 0.8),
    'sacola':            ((0.560, 0.560, 0.540), 0.35, 0.0, (0.560, 0.560, 0.540), 0.40, 0.0, 0.0, 0.30, 1.3),
    'tecla_vermelha':    ((0.400, 0.050, 0.030), 0.50, 0.0, (0.450, 0.200, 0.150), 0.45, 0.0, 0.50, 0.50, 2.0),
    'cedula_verde':      _liso((0.200, 0.300, 0.200), 0.8),
    'cedula_azul':       _liso((0.180, 0.240, 0.380), 0.8),
    'cedula_rosa':       _liso((0.420, 0.230, 0.260), 0.8),
    'armario_verde':     ((0.140, 0.195, 0.160), 0.40, 0.0, (0.330, 0.330, 0.340), 0.36, 1.0, 1.10, 0.40, 1.9),   # esmalte cinza-verde de vestiário
    'aco_polido':        ((0.550, 0.550, 0.550), 0.22, 1.0, (0.600, 0.600, 0.600), 0.18, 1.0, 0.40, 0.30, 1.4),
    'cromo':             ((0.620, 0.620, 0.620), 0.12, 1.0, (0.250, 0.150, 0.100), 0.55, 0.5, 0.50, 0.25, 1.4),   # cromado com pontos de ferrugem
    'vinil_vermelho':    ((0.300, 0.018, 0.018), 0.32, 0.0, (0.330, 0.200, 0.170), 0.60, 0.0, 0.60, 0.50, 1.6),
    'vinil_costura':     _liso((0.180, 0.010, 0.010), 0.6),
})


def _granito(nt, pos, S, nome):
    """Granito preto polido: pintas claras e grãos médios."""
    pinta = _smooth(nt, _noise(nt, pos, 260.0, 2.0, 0.5), 0.66, 0.70)
    S['cor'] = _mix(nt, pinta, S['cor'], (0.420, 0.400, 0.380))
    meio = _smooth(nt, _noise(nt, pos, 90.0, 3.0, 0.6), 0.55, 0.62)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', meio, 0.6), S['cor'], (0.190, 0.170, 0.160))


def _cromo(nt, pos, S, nome):
    """Cromado: pontinhos de ferrugem espalhados."""
    m = _smooth(nt, _noise(nt, pos, 140.0, 2.0, 0.6), 0.70, 0.76)
    S['cor'] = _mix(nt, m, S['cor'], (0.180, 0.090, 0.040))
    S['rug'] = _mixf(nt, m, S['rug'], 0.8)


def _po(nt, pos, S, nome):
    """Poeira nas faces de cima."""
    po = _math(nt, 'MULTIPLY', quarto._cima(nt), 0.4)
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))
    S['rug'] = _mixf(nt, po, S['rug'], 0.85)


forja.VELHO.update(gondola_branca=_po, armario_verde=_po, laminado_branco=_po, granito=_granito, cromo=_cromo, sacola=forja.VELHO['pano_cru'])
