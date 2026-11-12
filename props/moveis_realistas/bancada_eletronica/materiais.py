"""Classes de material da bancada de eletrônica (somadas às da M4A1, às madeiras da bancada de carpintaria
e ao envelhecimento da forja)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_forja_tambor', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'forja_tambor', 'materiais.py'))
forja = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(forja)
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'plastico_preto':   ((0.018, 0.018, 0.020), 0.46, 0.0, (0.090, 0.090, 0.095), 0.38, 0.0, 0.90, 0.80, 1.8),
    'plastico_amarelo': ((0.520, 0.300, 0.020), 0.48, 0.0, (0.600, 0.450, 0.200), 0.40, 0.0, 0.80, 0.80, 2.0),
    'plastico_azul':    ((0.020, 0.090, 0.280), 0.42, 0.0, (0.150, 0.250, 0.450), 0.38, 0.0, 0.70, 0.60, 1.6),
    'plastico_bege':    ((0.420, 0.370, 0.270), 0.50, 0.0, (0.520, 0.480, 0.400), 0.42, 0.0, 0.70, 0.80, 2.2),
    'isolante_vermelho': ((0.420, 0.020, 0.015), 0.50, 0.0, (0.420, 0.020, 0.015), 0.50, 0.0, 0.0, 0.60, 1.2),
    'isolante_preto':   ((0.016, 0.016, 0.018), 0.50, 0.0, (0.016, 0.016, 0.018), 0.50, 0.0, 0.0, 0.60, 1.0),
    'placa_verde':      ((0.012, 0.130, 0.050), 0.36, 0.0, (0.380, 0.220, 0.080), 0.40, 0.6, 0.50, 0.40, 1.2),
    'chapa_cinza':      ((0.170, 0.180, 0.185), 0.48, 0.0, (0.330, 0.330, 0.340), 0.36, 1.0, 1.40, 0.40, 1.7),   # esmalte martelado sobre aço
    'chapa_creme':      ((0.480, 0.430, 0.310), 0.50, 0.0, (0.330, 0.330, 0.340), 0.36, 1.0, 1.30, 0.40, 1.9),
    'chumbo':           ((0.200, 0.200, 0.210), 0.55, 1.0, (0.420, 0.420, 0.430), 0.40, 1.0, 0.60, 0.80, 1.4),
    'vidro_escuro':     ((0.012, 0.016, 0.014), 0.12, 0.0, (0.012, 0.016, 0.014), 0.12, 0.0, 0.0, 0.20, 0.8),
    'compensado':       forja.madeira.CRUA,
})
forja.madeira.COR['compensado'] = forja.madeira.cor_madeira('crua_x')


def _placa(nt, pos, S, nome):
    """Placa de circuito: trilhas de cobre em ângulo reto por baixo do verniz e ilhas de solda."""
    x, y, z = forja._xyz(nt, pos)
    t = None
    for a, b, passo in ((x, y, 0.0062), (y, x, 0.0085)):
        faixa = _math(nt, 'FLOOR', _math(nt, 'DIVIDE', b, passo * 3.1))
        n = _n(nt, 'ShaderNodeTexWhiteNoise', noise_dimensions='1D')
        nt.links.new(faixa, n.inputs['W'])
        linha = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', a, passo)), 0.5))
        m = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, linha, 0.10, 0.16)), _smooth(nt, n.outputs['Value'], 0.45, 0.55))
        t = m if t is None else _math(nt, 'MAXIMUM', t, m)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', t, 0.75), S['cor'], (0.030, 0.230, 0.085))
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', t, 0.00012))


def _martelado(nt, pos, S, nome):
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _noise(nt, pos, 330.0, 1.0, 0.5), 0.0005))
    f = _smooth(nt, _noise(nt, pos, 14.0, 4.0, 0.62), 0.60, 0.70)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', f, 0.8), S['cor'], (0.150, 0.060, 0.026))
    S['rug'] = _mixf(nt, f, S['rug'], 0.88)


def _plastico(nt, pos, S, nome):
    """Plástico velho: amarelado e encardido em manchas largas."""
    f = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 16.0, 4.0, 0.6), 0.42, 0.68), 0.45)
    S['cor'] = _mix(nt, f, S['cor'], (0.090, 0.070, 0.045))
    S['rug'] = _mixf(nt, f, S['rug'], 0.75)


forja.VELHO.update(placa_verde=_placa, chapa_cinza=_martelado, chapa_creme=_martelado,
                   plastico_bege=_plastico, plastico_amarelo=_plastico, plastico_preto=_plastico, plastico_azul=_plastico)
