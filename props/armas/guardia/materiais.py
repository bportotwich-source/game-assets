"""Classes de material da Guardiã (somadas às da M4A1 em m4a1/texturas.py).
VARIANTE=preta troca a pintura areia por alumínio anodizado, aço oxidado e polímero pretos."""
import os
import texturas
from texturas import _n, _math, _smooth

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
texturas.CLASSES.update({
    'areia_al':         ((0.200, 0.155, 0.095), 0.52, 0.25, (0.26, 0.26, 0.27), 0.34, 1.0, 1.50, 0.30, 1.5),   # pintura areia sobre alumínio
    'areia_aco':        ((0.185, 0.145, 0.090), 0.50, 0.30, (0.13, 0.13, 0.135), 0.36, 1.0, 1.70, 0.30, 1.5),  # pintura areia sobre aço
    'polim_areia':      ((0.150, 0.115, 0.070), 0.62, 0.0, (0.24, 0.19, 0.12), 0.42, 0.0, 0.90, 1.00, 1.5),
    'polim_areia_grip': ((0.150, 0.115, 0.070), 0.62, 0.0, (0.24, 0.19, 0.12), 0.42, 0.0, 0.90, 1.00, 1.6),
    'aco_cano':         ((0.060, 0.060, 0.062), 0.42, 0.90, (0.38, 0.38, 0.38), 0.28, 1.0, 0.90, 0.35, 0.7),
    'tinta_branca':     ((0.80, 0.80, 0.76), 0.60, 0.0, None, 0, 0, 0, 0, 0),
    'tinta_vermelha':   ((0.60, 0.02, 0.02), 0.50, 0.0, None, 0, 0, 0, 0, 0),
})

if os.environ.get('VARIANTE') == 'preta':
    texturas.CLASSES.update({
        'areia_al':         ((0.030, 0.032, 0.031), 0.48, 0.75, (0.30, 0.31, 0.32), 0.32, 1.0, 1.30, 0.25, 1.3),   # alumínio anodizado preto
        'areia_aco':        ((0.036, 0.037, 0.036), 0.58, 0.65, (0.27, 0.27, 0.26), 0.34, 1.0, 1.50, 0.45, 1.3),   # aço oxidado preto
        'polim_areia':      ((0.021, 0.022, 0.022), 0.60, 0.0, (0.060, 0.060, 0.058), 0.40, 0.0, 0.80, 1.00, 1.4),
        'polim_areia_grip': ((0.021, 0.022, 0.022), 0.60, 0.0, (0.060, 0.060, 0.058), 0.40, 0.0, 0.80, 1.00, 1.5),
    })

def quadriculado(nt, pos, geo):
    """Quadriculado das talas: pirâmides de 1,7 mm em losango na face de fora (a borda abaulada fica lisa)."""
    sep = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
    masc = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.90, 0.985)
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    passo = 0.0017
    a = _math(nt, 'MULTIPLY', p.outputs['Y'], 0.62)          # losango mais alto que largo
    x = _math(nt, 'DIVIDE', _math(nt, 'ADD', a, p.outputs['Z']), passo)
    y = _math(nt, 'DIVIDE', _math(nt, 'SUBTRACT', a, p.outputs['Z']), passo)
    fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', x), 0.5))
    fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', y), 0.5))
    pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
    h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0010)
    topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
    fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
    return h, topo, fundo


texturas.RELEVO['polim_areia_grip'] = quadriculado
