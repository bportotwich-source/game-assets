"""Classes de material da mesa de costura (somadas às da M4A1, às madeiras, ao envelhecimento da forja e aos
plásticos e metais das outras bancadas)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_bancada_trabalho', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bancada_trabalho', 'materiais.py'))
trabalho = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(trabalho)
forja = trabalho.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise


def _pano_cls(cor):
    claro = tuple(min(1.0, c * 1.5 + 0.03) for c in cor)
    return (cor, 0.92, 0.0, claro, 0.90, 0.0, 0.50, 1.20, 1.6)


# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'esmalte_preto': ((0.010, 0.010, 0.011), 0.22, 0.0, (0.300, 0.300, 0.310), 0.36, 1.0, 1.10, 0.30, 1.4),   # ferro esmaltado da máquina
    'dourado':       ((0.560, 0.380, 0.090), 0.38, 1.0, (0.560, 0.380, 0.090), 0.38, 1.0, 0.0, 0.30, 1.0),
    'pano_cru':      _pano_cls((0.450, 0.400, 0.300)),
    'pano_azul':     _pano_cls((0.040, 0.090, 0.220)),
    'pano_vermelho': _pano_cls((0.330, 0.035, 0.030)),
    'pano_verde':    _pano_cls((0.070, 0.150, 0.070)),
    'pano_cinza':    _pano_cls((0.130, 0.130, 0.140)),
    'pano_amarelo':  _pano_cls((0.520, 0.330, 0.040)),
    'vime':          ((0.330, 0.210, 0.090), 0.70, 0.0, (0.450, 0.330, 0.180), 0.65, 0.0, 0.70, 1.40, 1.8),
})

# madeiras com o veio no eixo que faltava (pinos do quadro, laterais de caixote)
for _n_, _base in (('faia_z', forja.madeira.FAIA), ('crua_z', forja.madeira.CRUA), ('tampo_z', forja.madeira.TAMPO)):
    texturas.CLASSES[_n_] = _base
    forja.madeira.COR[_n_] = forja.madeira.cor_madeira(_n_)
    texturas.RELEVO[_n_] = forja.madeira.relevo_madeira(_n_)


def _pano(nt, pos, S, nome):
    """Trama do tecido (fios cruzados miúdos) e dobras largas mais escuras."""
    x, y, z = forja._xyz(nt, pos)
    t = None
    for a in (x, y, z):
        w = _n(nt, 'ShaderNodeTexWave', wave_type='BANDS')
        w.inputs['Scale'].default_value = 520.0
        w.inputs['Distortion'].default_value = 0.6
        v = forja._vec(nt, a, a, a, 1.0, 0.0, 0.0)
        nt.links.new(v, w.inputs['Vector'])
        t = w.outputs['Fac'] if t is None else _math(nt, 'ADD', t, w.outputs['Fac'])
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', t, 0.00025))
    dobra = _smooth(nt, _noise(nt, pos, 9.0, 3.0, 0.6), 0.40, 0.70)
    S['cor'] = forja.madeira._tom(nt, S['cor'], _math(nt, 'ADD', 0.70, _math(nt, 'MULTIPLY', dobra, 0.50)))


def _vime(nt, pos, S, nome):
    """Cesto trançado: faixas deitadas alternando com as de pé."""
    x, y, z = forja._xyz(nt, pos)
    faixa = _math(nt, 'FRACT', _math(nt, 'DIVIDE', z, 0.024))
    onda = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', faixa, 0.5))
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 0.5, onda), 0.006))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', _smooth(nt, onda, 0.36, 0.5), 0.8), S['cor'], (0.070, 0.040, 0.018))
    S['cor'] = forja.madeira._tom(nt, S['cor'], _math(nt, 'ADD', 0.75, _math(nt, 'MULTIPLY', _noise(nt, pos, 60.0, 2.0, 0.5), 0.5)))


def _esmalte(nt, pos, S, nome):
    """Esmalte preto antigo: lascas mostrando o ferro e pó nas partes de cima."""
    f = _smooth(nt, _noise(nt, pos, 46.0, 4.0, 0.65), 0.63, 0.70)
    S['cor'] = _mix(nt, f, S['cor'], (0.160, 0.110, 0.080))
    S['rug'] = _mixf(nt, f, S['rug'], 0.75)
    S['met'] = _mixf(nt, f, S['met'], 0.6)
    po = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 14.0, 3.0, 0.6), 0.45, 0.75), 0.14)
    S['cor'] = _mix(nt, po, S['cor'], (0.160, 0.140, 0.120))
    S['rug'] = _mixf(nt, po, S['rug'], 0.70)


forja.VELHO.update(esmalte_preto=_esmalte, vime=_vime, **{k: _pano for k in ('pano_cru', 'pano_azul', 'pano_vermelho', 'pano_verde', 'pano_cinza', 'pano_amarelo')})
