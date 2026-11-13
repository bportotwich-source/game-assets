"""Classes de material dos móveis de quarto (somadas às da M4A1 e às das estações).

Móvel de casa é madeira envernizada, não tábua crua: `nogueira_*` (o sufixo diz para que lado corre o veio,
como nas outras madeiras) tem o verniz gasto nas quinas, riscos, manchas foscas onde o verniz morreu e
poeira assentada nas faces viradas para cima."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_bancada_municao', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bancada_municao', 'materiais.py'))
municao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(municao)
forja = municao.forja
madeira = forja.madeira
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
NOGUEIRA = ((0.150, 0.062, 0.023), 0.28, 0.0, (0.360, 0.220, 0.100), 0.62, 0.0, 0.50, 0.50, 1.5)
FORRO = ((0.520, 0.400, 0.235), 0.78, 0.0, (0.580, 0.460, 0.290), 0.80, 0.0, 0.25, 1.10, 1.2)      # madeira clara sem verniz: dentro das gavetas e do guarda-roupa
texturas.CLASSES.update({
    'latao_puxador': ((0.420, 0.270, 0.080), 0.42, 1.0, (0.800, 0.580, 0.240), 0.26, 1.0, 1.20, 0.30, 1.6),   # latão escurecido, brilhando onde a mão pega
    'cabide_arame':  ((0.330, 0.330, 0.340), 0.42, 1.0, (0.560, 0.560, 0.570), 0.30, 1.0, 0.0, 0.30, 1.0),
})
for _e in 'xyz':
    texturas.CLASSES['nogueira_' + _e] = NOGUEIRA
    texturas.CLASSES['forro_' + _e] = FORRO


def _cor_nogueira(nome):
    eixo = madeira.EIXO[nome[-1]]

    def f(nt, pos, cor):
        fino = _smooth(nt, _noise(nt, madeira._veio_vec(nt, pos, eixo, 0.030, 1.0), 300.0, 4.0, 0.6), 0.28, 0.74)      # poros do veio
        aneis = _noise(nt, madeira._veio_vec(nt, pos, eixo, 0.045, 1.0), 44.0, 3.0, 0.55)                              # catedrais largas
        larga = _noise(nt, madeira._veio_vec(nt, pos, eixo, 0.05, 1.0), 9.0, 2.0, 0.5)
        t = _math(nt, 'ADD', 0.62, _math(nt, 'MULTIPLY', fino, 0.55))
        t = _math(nt, 'MULTIPLY', t, _math(nt, 'ADD', 0.45, _math(nt, 'MULTIPLY', aneis, 1.10)))
        t = _math(nt, 'MULTIPLY', t, _math(nt, 'ADD', 0.80, _math(nt, 'MULTIPLY', larga, 0.40)))
        return madeira._tom(nt, cor, t)
    return f


def _cor_forro(nome):
    eixo = madeira.EIXO[nome[-1]]

    def f(nt, pos, cor):
        fino = _smooth(nt, _noise(nt, madeira._veio_vec(nt, pos, eixo, 0.035, 1.0), 240.0, 4.0, 0.6), 0.30, 0.72)
        aneis = _noise(nt, madeira._veio_vec(nt, pos, eixo, 0.04, 1.0), 30.0, 2.0, 0.5)
        t = _math(nt, 'ADD', 0.78, _math(nt, 'MULTIPLY', fino, 0.30))
        t = _math(nt, 'MULTIPLY', t, _math(nt, 'ADD', 0.80, _math(nt, 'MULTIPLY', aneis, 0.40)))
        return madeira._tom(nt, cor, t)
    return f


def _cima(nt):
    """1 nas faces viradas para cima, 0 nas outras."""
    geo = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeNewGeometry')
    s = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Normal'], s.inputs[0])
    return _smooth(nt, s.outputs['Z'], 0.55, 0.95)


def _verniz(nt, pos, S, nome):
    """Verniz velho: manchas foscas e desbotadas, e poeira nas faces de cima (mais grossa longe das bordas não dá
    para saber aqui, então vem em nuvens)."""
    morto = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 3.2, 4.0, 0.62), 0.58, 0.72), 0.40)
    S['cor'] = _mix(nt, morto, S['cor'], (0.270, 0.160, 0.080))
    S['rug'] = _mixf(nt, morto, S['rug'], 0.62)
    cima = _cima(nt)
    po = _math(nt, 'MULTIPLY', cima, _math(nt, 'ADD', 0.22, _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 6.0, 4.0, 0.6), 0.30, 0.75), 0.36)))
    S['cor'] = _mix(nt, po, S['cor'], (0.330, 0.300, 0.260))
    S['rug'] = _mixf(nt, po, S['rug'], 0.88)


def _forro(nt, pos, S, nome):
    cima = _cima(nt)
    po = _math(nt, 'MULTIPLY', cima, 0.30)
    S['cor'] = _mix(nt, po, S['cor'], (0.300, 0.270, 0.230))
    mancha = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 5.0, 4.0, 0.6), 0.55, 0.72), 0.35)
    S['cor'] = _mix(nt, mancha, S['cor'], (0.230, 0.160, 0.090))


for _e in 'xyz':
    for _p, _c, _v in (('nogueira_', _cor_nogueira, _verniz), ('forro_', _cor_forro, _forro)):
        madeira.COR[_p + _e] = _c(_p + _e)
        texturas.RELEVO[_p + _e] = madeira.relevo_madeira(_p + _e)
        forja.VELHO[_p + _e] = _v
