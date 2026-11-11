"""Classes de material da Ciclone (somadas às da M4A1 em m4a1/texturas.py).
VARIANTE=tan troca a cor do polímero do chassi, do punho e da coronha para areia."""
import os
import texturas
from texturas import _n, _math, _smooth

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
POLIMERO = {
    '':    ((0.021, 0.022, 0.022), (0.060, 0.060, 0.058)),
    'tan': ((0.300, 0.205, 0.105), (0.420, 0.320, 0.200)),
}
VARIANTE = os.environ.get('VARIANTE', '')
_cor, _gasta = POLIMERO[VARIANTE]
texturas.CLASSES.update({
    'pol_cic':      (_cor, 0.62, 0.0, _gasta, 0.42, 0.0, 0.85, 1.00, 1.4),
    'pol_cic_grip': (_cor, 0.64, 0.0, _gasta, 0.42, 0.0, 0.85, 1.00, 1.6),
    'pol_cic_painel': (_cor, 0.64, 0.0, _gasta, 0.42, 0.0, 0.85, 1.00, 1.6),
    'aco_cano':     ((0.060, 0.060, 0.062), 0.42, 0.90, (0.38, 0.38, 0.38), 0.28, 1.0, 0.90, 0.35, 0.7),
    'aco_polido':   ((0.300, 0.300, 0.295), 0.36, 1.00, (0.55, 0.55, 0.55), 0.28, 1.0, 0.50, 0.30, 1.0),   # ferrolho, visto pela janela
})


def _pontilhado(z0, z1):
    """Pontilhado de pirâmides quadradas de 1,3 mm entre as alturas z0 e z1 (m), com a borda lisa."""
    def f(nt, pos, geo):
        p = _n(nt, 'ShaderNodeSeparateXYZ')
        nt.links.new(pos, p.inputs[0])
        z = p.outputs['Z']
        masc = _math(nt, 'MULTIPLY', _smooth(nt, z, z0, z0 + 0.0025), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, z1 - 0.0025, z1)))
        sep = _n(nt, 'ShaderNodeSeparateXYZ')
        nt.links.new(geo.outputs['True Normal'], sep.inputs[0])
        masc = _math(nt, 'MULTIPLY', masc, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['Z']), 0.25, 0.45)))
        passo = 0.0013
        # nos lados o padrão corre em Y e Z; na frente e nas costas, em X e Z
        lado = _smooth(nt, _math(nt, 'ABSOLUTE', sep.outputs['X']), 0.55, 0.75)
        a = _math(nt, 'ADD', _math(nt, 'MULTIPLY', p.outputs['Y'], lado), _math(nt, 'MULTIPLY', p.outputs['X'], _math(nt, 'SUBTRACT', 1.0, lado)))
        fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', a, passo)), 0.5))
        fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'DIVIDE', z, passo)), 0.5))
        pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
        h = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0008)
        topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
        fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
        return h, topo, fundo
    return f


texturas.RELEVO['pol_cic_grip'] = _pontilhado(-0.131, -0.045)
texturas.RELEVO['pol_cic_painel'] = _pontilhado(-0.2, 0.0)
