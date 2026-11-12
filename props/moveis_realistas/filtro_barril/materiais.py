"""Classes de material do filtro de água em barril (somadas às da M4A1 e às das outras estações)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_mesa_enfermaria', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mesa_enfermaria', 'materiais.py'))
enfermaria = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enfermaria)
forja = enfermaria.forja
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'tambor_agua':  ((0.030, 0.075, 0.160), 0.50, 0.0, (0.200, 0.085, 0.036), 0.85, 0.3, 1.50, 0.60, 2.0),    # tambor azul sem fuligem
    'bloco':        ((0.300, 0.295, 0.280), 0.94, 0.0, (0.420, 0.415, 0.400), 0.92, 0.0, 0.50, 2.40, 2.2),    # bloco de concreto
    'pvc':          ((0.170, 0.085, 0.045), 0.38, 0.0, (0.300, 0.190, 0.120), 0.55, 0.0, 0.50, 0.40, 1.6),    # cano marrom de água
    'pvc_branco':   ((0.520, 0.510, 0.470), 0.40, 0.0, (0.600, 0.590, 0.560), 0.55, 0.0, 0.40, 0.40, 2.0),
    'galao':        ((0.200, 0.330, 0.430), 0.22, 0.0, (0.300, 0.420, 0.500), 0.40, 0.0, 0.30, 0.30, 1.2),    # galão de 5 L cheio
    'tampa_azul':   ((0.020, 0.080, 0.300), 0.40, 0.0, (0.100, 0.200, 0.450), 0.50, 0.0, 0.50, 0.40, 1.0),
    'mangueira':    ((0.400, 0.440, 0.360), 0.25, 0.0, (0.400, 0.440, 0.360), 0.25, 0.0, 0.0, 0.30, 1.6),     # mangueira de nível, esverdeada de limo
    'sisal':        ((0.400, 0.300, 0.150), 0.90, 0.0, (0.520, 0.420, 0.250), 0.90, 0.0, 0.40, 1.40, 1.6),
    'pano_filtro':  enfermaria.costura._pano_cls((0.470, 0.430, 0.340)),
    'letra_branca': ((0.560, 0.560, 0.530), 0.60, 0.0, (0.560, 0.560, 0.530), 0.60, 0.0, 0.0, 0.40, 1.0),     # tinta a pincel
})

def tambor_velho(pe):
    """Tambor que guarda água: ferrugem em manchas e escorrida, pé comido (pe = altura do fundo, em metros)
    e calcário branco escorrendo da boca."""
    def f(nt, pos, S, nome):
        x, y, z = forja._xyz(nt, pos)
        escorrido = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.07), 16.0, 3.0, 0.6)
        mancha = _noise(nt, pos, 5.5, 4.0, 0.62)
        f = _smooth(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', mancha, 0.62), _math(nt, 'MULTIPLY', escorrido, 0.42)), 0.54, 0.64)
        comido = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, pe + 0.02, pe + 0.20)), _smooth(nt, _noise(nt, pos, 24.0, 3.0, 0.6), 0.30, 0.55))
        f = _math(nt, 'MAXIMUM', _math(nt, 'MULTIPLY', f, 0.9), comido)
        ferr = _mix(nt, _smooth(nt, _noise(nt, pos, 70.0, 3.0, 0.6), 0.3, 0.7), (0.200, 0.075, 0.028), (0.085, 0.036, 0.018))
        S['cor'] = _mix(nt, f, S['cor'], ferr)
        S['rug'] = _mixf(nt, f, S['rug'], 0.90)
        S['met'] = _mixf(nt, f, S['met'], 0.15)
        S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', f, _noise(nt, pos, 500.0, 2.0, 0.6)), 0.0006))
        fino = _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.05), 34.0, 3.0, 0.6)
        cal = _math(nt, 'MULTIPLY', _smooth(nt, fino, 0.56, 0.70), _smooth(nt, _math(nt, 'ADD', z, _math(nt, 'MULTIPLY', escorrido, 0.25)), pe + 0.33, pe + 0.83))
        S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', cal, 0.55), S['cor'], (0.420, 0.430, 0.400))
        S['rug'] = _mixf(nt, cal, S['rug'], 0.85)
    return f


def _bloco(nt, pos, S, nome):
    tom = _math(nt, 'ADD', 0.62, _math(nt, 'MULTIPLY', _noise(nt, pos, 6.0, 3.0, 0.6), 0.75))
    S['cor'] = forja.madeira._tom(nt, S['cor'], tom)
    poros = _smooth(nt, _noise(nt, pos, 300.0, 3.0, 0.6), 0.52, 0.72)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', poros, 0.55), S['cor'], (0.090, 0.088, 0.080))
    S['alt'] = _math(nt, 'SUBTRACT', S['alt'], _math(nt, 'MULTIPLY', poros, 0.0016))
    x, y, z = forja._xyz(nt, pos)
    umido = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ADD', z, _math(nt, 'MULTIPLY', _noise(nt, pos, 14.0, 3.0, 0.6), 0.10)), 0.04, 0.16)), 0.75)
    S['cor'] = _mix(nt, umido, S['cor'], (0.060, 0.075, 0.040))          # limo no pé


def _pano_molhado(nt, pos, S, nome):
    """Pano do filtro: trama, e o meio escuro e encardido de tanto passar água suja."""
    enfermaria.costura._pano(nt, pos, S, nome)
    x, y, z = forja._xyz(nt, pos)
    r = _math(nt, 'SQRT', _math(nt, 'ADD', _math(nt, 'MULTIPLY', x, x), _math(nt, 'MULTIPLY', y, y)))
    meio = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', _noise(nt, pos, 13.0, 3.0, 0.6), 0.12)), 0.16, 0.30))
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', meio, 0.72), S['cor'], (0.120, 0.095, 0.055))
    S['rug'] = _mixf(nt, _math(nt, 'MULTIPLY', meio, 0.8), S['rug'], 0.45)
    borra = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 48.0, 3.0, 0.6), 0.60, 0.72), meio)
    S['cor'] = _mix(nt, _math(nt, 'MULTIPLY', borra, 0.8), S['cor'], (0.040, 0.034, 0.020))
    escorre = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, forja._vec(nt, x, y, z, 1.0, 1.0, 0.08), 22.0, 3.0, 0.6), 0.52, 0.68), 0.5)
    S['cor'] = _mix(nt, escorre, S['cor'], (0.200, 0.160, 0.090))


def _sisal(nt, pos, S, nome):
    x, y, z = forja._xyz(nt, pos)
    w = _n(nt, 'ShaderNodeTexWave', wave_type='BANDS')
    w.inputs['Scale'].default_value = 260.0
    w.inputs['Distortion'].default_value = 1.0
    nt.links.new(forja._vec(nt, _math(nt, 'ADD', _math(nt, 'ADD', x, y), z), z, z, 1.0, 0.0, 0.0), w.inputs['Vector'])
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', w.outputs['Fac'], 0.0012))
    S['cor'] = forja.madeira._tom(nt, S['cor'], _math(nt, 'ADD', 0.60, _math(nt, 'MULTIPLY', w.outputs['Fac'], 0.60)))


def _limo(nt, pos, S, nome):
    f = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 40.0, 3.0, 0.6), 0.40, 0.70), 0.6)
    S['cor'] = _mix(nt, f, S['cor'], (0.090, 0.130, 0.050))


forja.VELHO.update(tambor_agua=tambor_velho(0.225), bloco=_bloco, pano_filtro=_pano_molhado, sisal=_sisal, mangueira=_limo)
