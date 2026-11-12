"""Classes de material do caixote grande (somadas às da M4A1, às madeiras da bancada de carpintaria
e ao envelhecimento da forja)."""
import os, importlib.util
import texturas

_spec = importlib.util.spec_from_file_location('materiais_forja_tambor', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'forja_tambor', 'materiais.py'))
forja = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(forja)
from texturas import _n, _math, _mix, _mixf, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
madeira = forja.madeira
texturas.CLASSES.update({
    'crua_z': madeira.CRUA,
    'tinta_branca': ((0.62, 0.62, 0.56), 0.70, 0.0, None, 0, 0, 0, 0, 0),                            # letreiro pintado à mão
    'corda': ((0.330, 0.250, 0.140), 0.92, 0.0, (0.450, 0.370, 0.240), 0.92, 0.0, 0.40, 1.60, 1.8),     # sisal encardido
})


def _corda(nt, pos, S, nome):
    """Sisal torcido: riscos finos atravessados e sujeira de mão."""
    fio = _noise(nt, pos, 900.0, 2.0, 0.6)
    S['alt'] = _math(nt, 'ADD', S['alt'], _math(nt, 'MULTIPLY', fio, 0.0012))
    suj = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 40.0, 3.0, 0.6), 0.45, 0.70), 0.6)
    S['cor'] = _mix(nt, suj, S['cor'], (0.070, 0.050, 0.034))


madeira.COR['crua_z'] = madeira.cor_madeira('crua_z')
texturas.RELEVO['crua_z'] = madeira.relevo_madeira('crua_z')
forja.VELHO.update(corda=_corda)
