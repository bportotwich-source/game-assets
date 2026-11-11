"""Classes de material dos bastões (somadas às da M4A1; o veio da madeira é o do facão)."""
import os, math, importlib.util
import texturas
from texturas import _n, _math, _smooth

_spec = importlib.util.spec_from_file_location('materiais_facao_b', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'facao', 'materiais.py'))
facao = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(facao)

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'madeira_taco':   ((0.380, 0.235, 0.115), 0.55, 0.0, (0.300, 0.200, 0.110), 0.62, 0.0, 0.35, 1.00, 2.2),    # freixo claro, encardido
    'madeira_lasca':  ((0.480, 0.340, 0.190), 0.70, 0.0, (0.480, 0.340, 0.190), 0.70, 0.0, 0.0, 1.00, 1.2),     # madeira crua nas mossas
    'fita_isolante':  ((0.016, 0.016, 0.017), 0.42, 0.0, (0.050, 0.050, 0.050), 0.55, 0.0, 0.25, 0.30, 1.0),
    'aco_prego':      ((0.240, 0.230, 0.220), 0.48, 0.9, (0.300, 0.290, 0.280), 0.40, 1.0, 0.0, 0.50, 0.0),
    'prego_ferrugem': ((0.200, 0.095, 0.045), 0.75, 0.3, (0.200, 0.095, 0.045), 0.75, 0.3, 0.0, 1.00, 0.0),
    'arame_farpado':  ((0.230, 0.215, 0.195), 0.52, 0.85, (0.280, 0.200, 0.130), 0.60, 0.6, 0.0, 0.80, 0.0),
})
facao.recurvo.COR['madeira_taco'] = facao.cor_veio
facao.recurvo.COR['madeira_lasca'] = facao.cor_veio


def enfaixado(nt, pos, geo):
    """Fita isolante enrolada em espiral: cada volta (14 mm) sobe um degrau sobre a anterior."""
    n = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], n.inputs[0])
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    ang = _math(nt, 'DIVIDE', _math(nt, 'ARCTAN2', n.outputs['Z'], n.outputs['X']), 2 * math.pi)
    s = _math(nt, 'FRACT', _math(nt, 'ADD', _math(nt, 'DIVIDE', p.outputs['Y'], 0.014), ang))
    h = _math(nt, 'MULTIPLY', s, 0.0005)
    topo = _smooth(nt, s, 0.86, 0.98)
    fundo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, s, 0.0, 0.08))
    return h, topo, fundo


texturas.RELEVO['fita_isolante'] = enfaixado
