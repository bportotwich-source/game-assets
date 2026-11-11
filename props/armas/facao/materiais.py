"""Classes de material do facão (somadas às da M4A1, do Brasa e dos arcos)."""
import os, importlib.util
import texturas

_M = {}
for _nome, _pasta in (('materiais_recurvo_f', 'recurvo'), ('materiais_brasa_f', 'brasa')):
    _spec = importlib.util.spec_from_file_location(_nome, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', _pasta, 'materiais.py'))
    _M[_pasta] = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_M[_pasta])
recurvo = _M['recurvo']
from texturas import _n, _math, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'aco_facao':     ((0.040, 0.040, 0.042), 0.50, 0.80, (0.36, 0.35, 0.34), 0.34, 1.0, 0.0, 0.40, 1.6),     # aço carbono escurecido (sem desgaste de quina: a lâmina é fina demais para o bake)
    'madeira_facao': ((0.085, 0.036, 0.015), 0.50, 0.0, (0.200, 0.105, 0.050), 0.48, 0.0, 0.30, 1.00, 1.6),
    'couro_escuro':  ((0.030, 0.017, 0.010), 0.60, 0.0, (0.090, 0.055, 0.030), 0.55, 0.0, 0.0, 1.00, 0.0),
})


def cor_veio(nt, pos, cor):
    """Talas de madeira: veio comprido correndo ao longo do cabo."""
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    v = _n(nt, 'ShaderNodeCombineXYZ')
    nt.links.new(_math(nt, 'MULTIPLY', p.outputs['X'], 9.0), v.inputs[0])
    nt.links.new(_math(nt, 'MULTIPLY', p.outputs['Y'], 0.45), v.inputs[1])
    nt.links.new(_math(nt, 'MULTIPLY', p.outputs['Z'], 9.0), v.inputs[2])
    risco = _smooth(nt, _noise(nt, v.outputs[0], 200.0, 4.0, 0.6), 0.30, 0.72)
    tom = _math(nt, 'ADD', 0.55, _math(nt, 'MULTIPLY', risco, 0.85))
    escala = _n(nt, 'ShaderNodeCombineColor')
    for i in range(3):
        nt.links.new(tom, escala.inputs[i])
    return recurvo._mult(nt, cor, escala.outputs[0])


recurvo.COR['madeira_facao'] = cor_veio
