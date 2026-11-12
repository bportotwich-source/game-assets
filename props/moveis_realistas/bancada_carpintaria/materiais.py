"""Classes de material da bancada de carpintaria (somadas às da M4A1 em armas/m4a1/texturas.py).

Madeira: o sufixo da classe diz para que lado corre o veio nas coordenadas do jogo
(_x ao comprido da bancada, _y em pé, _z no sentido da profundidade)."""
import texturas
from texturas import _n, _math, _mix, _smooth, _noise

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
PINHO = ((0.340, 0.220, 0.108), 0.74, 0.0, (0.520, 0.380, 0.220), 0.78, 0.0, 0.55, 1.20, 2.4)     # caibro de pinho encardido
TAMPO = ((0.285, 0.175, 0.082), 0.66, 0.0, (0.470, 0.330, 0.180), 0.72, 0.0, 0.70, 1.20, 2.4)     # tábuas do tampo, batidas e manchadas
FAIA = ((0.330, 0.170, 0.060), 0.46, 0.0, (0.480, 0.300, 0.150), 0.55, 0.0, 0.60, 0.90, 1.3)      # ferramentas de madeira, lisas da mão
CRUA = ((0.560, 0.420, 0.230), 0.80, 0.0, (0.600, 0.470, 0.280), 0.80, 0.0, 0.20, 1.20, 0.6)      # tábua nova, recém-serrada
texturas.CLASSES.update({
    'pinho_x': PINHO, 'pinho_y': PINHO, 'pinho_z': PINHO,
    'tampo_x': TAMPO, 'tampo_y': TAMPO,
    'faia_x': FAIA, 'faia_y': FAIA,
    'crua_y': CRUA, 'crua_x': CRUA,
    'aco_ferramenta': ((0.300, 0.300, 0.310), 0.40, 1.0, (0.560, 0.560, 0.570), 0.28, 1.0, 0.60, 0.40, 1.5),
    'aco_lamina':     ((0.330, 0.330, 0.340), 0.36, 1.0, (0.560, 0.560, 0.570), 0.28, 1.0, 0.0, 0.40, 1.2),    # chapa fina: sem desgaste de quina
    'ferro_preto':    ((0.040, 0.038, 0.036), 0.58, 0.5, (0.300, 0.290, 0.280), 0.40, 1.0, 1.10, 0.60, 1.6),
    'esmalte_vermelho': ((0.300, 0.022, 0.014), 0.42, 0.0, (0.280, 0.270, 0.270), 0.38, 1.0, 1.30, 0.40, 1.5),
    'lata':           ((0.420, 0.430, 0.430), 0.44, 1.0, (0.600, 0.600, 0.600), 0.32, 1.0, 0.60, 0.40, 1.8),
    'lapis':          ((0.560, 0.330, 0.020), 0.50, 0.0, (0.560, 0.420, 0.230), 0.70, 0.0, 0.50, 0.40, 0.8),
    'grafite':        ((0.020, 0.020, 0.022), 0.45, 0.0, None, 0, 0, 0, 0, 0),
})

# No Blender: X = x do jogo, Y = -z do jogo, Z = y do jogo.
EIXO = {'x': 'X', 'y': 'Z', 'z': 'Y'}


def _veio_vec(nt, pos, eixo, ao_comprido, atravessado):
    p = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(pos, p.inputs[0])
    v = _n(nt, 'ShaderNodeCombineXYZ')
    for i, k in enumerate('XYZ'):
        nt.links.new(_math(nt, 'MULTIPLY', p.outputs[k], ao_comprido if k == eixo else atravessado), v.inputs[i])
    return v.outputs[0]


def _tom(nt, cor, f):
    c = _n(nt, 'ShaderNodeCombineColor')
    for i in range(3):
        nt.links.new(f, c.inputs[i])
    m = _n(nt, 'ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY')
    m.inputs[0].default_value = 1.0
    nt.links.new(cor, m.inputs[6])
    nt.links.new(c.outputs[0], m.inputs[7])
    return m.outputs[2]


def cor_madeira(nome):
    eixo = EIXO[nome[-1]]

    def f(nt, pos, cor):
        fino = _smooth(nt, _noise(nt, _veio_vec(nt, pos, eixo, 0.035, 1.0), 260.0, 4.0, 0.6), 0.30, 0.72)       # riscos do veio
        aneis = _noise(nt, _veio_vec(nt, pos, eixo, 0.03, 1.0), 38.0, 2.0, 0.5)                                # faixas largas
        tabua = _noise(nt, _veio_vec(nt, pos, eixo, 0.02, 1.0), 7.0, 1.0, 0.5)                                 # cada tábua de um tom
        t = _math(nt, 'ADD', 0.62, _math(nt, 'MULTIPLY', fino, 0.60))
        t = _math(nt, 'MULTIPLY', t, _math(nt, 'ADD', 0.78, _math(nt, 'MULTIPLY', aneis, 0.44)))
        t = _math(nt, 'MULTIPLY', t, _math(nt, 'ADD', 0.52, _math(nt, 'MULTIPLY', tabua, 0.96)))
        cor = _tom(nt, cor, t)
        if nome.startswith('tampo'):                                                                         # manchas de óleo, cola e uso
            m1 = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 7.0, 4.0, 0.6), 0.47, 0.66), 0.70)
            cor = _mix(nt, m1, cor, (0.050, 0.036, 0.024))
            m2 = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 19.0, 3.0, 0.5), 0.66, 0.74), 0.35)
            cor = _mix(nt, m2, cor, (0.520, 0.480, 0.400))
        if nome.startswith('pinho'):                                                                         # pé da bancada encardido do chão
            sp = _n(nt, 'ShaderNodeSeparateXYZ')
            nt.links.new(pos, sp.inputs[0])
            baixo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, _math(nt, 'ADD', sp.outputs['Z'], _math(nt, 'MULTIPLY', _noise(nt, pos, 30.0, 3.0, 0.6), 0.08)), 0.03, 0.20))
            cor = _mix(nt, _math(nt, 'MULTIPLY', baixo, 0.65), cor, (0.060, 0.050, 0.040))
        return cor
    return f


def relevo_madeira(nome):
    eixo = EIXO[nome[-1]]

    def f(nt, pos, geo):
        fino = _smooth(nt, _noise(nt, _veio_vec(nt, pos, eixo, 0.035, 1.0), 260.0, 4.0, 0.6), 0.30, 0.72)
        return _math(nt, 'MULTIPLY', fino, 0.00035), 0.0, 0.0
    return f


COR = {}
for _c in texturas.CLASSES:
    if _c.split('_')[0] in ('pinho', 'tampo', 'faia', 'crua'):
        COR[_c] = cor_madeira(_c)
        texturas.RELEVO[_c] = relevo_madeira(_c)
_montar = texturas.montar_material


def montar_material(m, nome):
    S, em, bs, out, img = _montar(m, nome)
    if nome in COR:
        nt = m.node_tree
        geo = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeNewGeometry')
        S['cor'] = COR[nome](nt, geo.outputs['Position'], S['cor'])
    return S, em, bs, out, img


texturas.montar_material = montar_material
