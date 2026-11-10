"""Materiais procedurais e bake (Cycles) das texturas PBR da amostra de casa.
Mesmo método da M4A1 (props/armas/m4a1/texturas.py): tudo é calculado na posição 3D da peça
(desgaste nas arestas, sujeira nas reentrâncias, veio da madeira) e depois assado em cor + normal + ORM."""
import math, os
import bpy
import numpy as np

# classe: (família, parâmetros)
CLASSES = {
    'tabua':    ('pintura', dict(cor=(0.36, 0.47, 0.45), descasca=0.55, rug=0.62, suj=1.0, ext=True, bisel=0.002)),
    'guarn':    ('pintura', dict(cor=(0.78, 0.75, 0.66), descasca=0.42, rug=0.55, suj=1.0, ext=True, bisel=0.0022)),
    'porta':    ('pintura', dict(cor=(0.30, 0.038, 0.030), giz=0.05, descasca=0.36, rug=0.42, suj=0.8, ext=True, bisel=0.002)),
    'rodape':   ('pintura', dict(cor=(0.80, 0.78, 0.72), descasca=0.14, rug=0.38, suj=0.7, ext=False, bisel=0.002)),
    'tijolo':   ('tijolo', dict(bisel=0.0)),
    'reboco':   ('reboco', dict(cor=(0.62, 0.66, 0.55), bisel=0.003)),
    'assoalho': ('assoalho', dict(c1=(0.105, 0.050, 0.024), c2=(0.26, 0.145, 0.070), bisel=0.0)),
    'verniz':   ('verniz', dict(c1=(0.050, 0.020, 0.010), c2=(0.150, 0.062, 0.026), cru=(0.36, 0.22, 0.11), rug=0.22, kd=0.85, po=0.8, bisel=0.0012)),
    'pinho':    ('verniz', dict(c1=(0.42, 0.28, 0.13), c2=(0.62, 0.47, 0.26), cru=(0.66, 0.52, 0.32), rug=0.72, kd=0.3, po=0.6, bisel=0.0008)),
    'vidro':    ('vidro', dict()),
    # genéricos: cor, rug, metal, cor gasta, rug gasta, metal gasto, desgaste, grão, sujeira, escala
    'latao':    ('gen', dict(p=((0.62, 0.40, 0.12), 0.34, 1.0, (0.88, 0.68, 0.30), 0.22, 1.0, 0.9, 0.3, 1.3), mancha=(0.10, 0.075, 0.04), bisel=0.0006)),
    'ferro':    ('gen', dict(p=((0.030, 0.030, 0.032), 0.55, 0.85, (0.32, 0.31, 0.30), 0.35, 1.0, 1.0, 0.5, 1.0), mancha=(0.20, 0.08, 0.03), bisel=0.0005)),
    'pedra':    ('gen', dict(p=((0.44, 0.43, 0.40), 0.82, 0.0, (0.58, 0.57, 0.54), 0.6, 0.0, 0.6, 2.5, 1.2), mancha=(0.20, 0.19, 0.15), bisel=0.004, esc=0.12)),
    'cimento':  ('gen', dict(p=((0.36, 0.35, 0.33), 0.9, 0.0, (0.5, 0.5, 0.48), 0.8, 0.0, 0.3, 2.0, 0.6), mancha=(0.2, 0.19, 0.16), bisel=0.0, esc=0.12)),
    'lata':     ('gen', dict(p=((0.58, 0.58, 0.56), 0.30, 1.0, (0.70, 0.70, 0.70), 0.22, 1.0, 0.5, 0.3, 1.0), mancha=(0.24, 0.10, 0.035), bisel=0.0004)),
    'esmalte':  ('gen', dict(p=((0.045, 0.13, 0.30), 0.30, 0.0, (0.20, 0.085, 0.035), 0.82, 0.25, 1.5, 0.3, 1.2), mancha=(0.13, 0.06, 0.03), bisel=0.0006)),
    'arame':    ('gen', dict(p=((0.30, 0.30, 0.29), 0.42, 1.0, (0.5, 0.5, 0.5), 0.3, 1.0, 0.4, 0.3, 1.0), mancha=(0.2, 0.09, 0.03), bisel=0.0, fino=True)),
    'rotulo':   ('gen', dict(p=((0.48, 0.050, 0.030), 0.55, 0.0, (0.78, 0.74, 0.66), 0.7, 0.0, 0.7, 0.4, 0.9), mancha=(0.22, 0.12, 0.05), bisel=0.0, fino=True)),
    'rotulo_creme': ('gen', dict(p=((0.80, 0.72, 0.50), 0.55, 0.0, (0.85, 0.82, 0.75), 0.7, 0.0, 0.5, 0.4, 0.9), mancha=(0.3, 0.2, 0.1), bisel=0.0, fino=True)),
    'pavio':    ('liso', dict(cor=(0.70, 0.64, 0.50), rug=0.95)),
    'tinta_escura': ('liso', dict(cor=(0.035, 0.028, 0.02), rug=0.6)),
    'tinta_creme':  ('liso', dict(cor=(0.84, 0.78, 0.58), rug=0.55)),
    'tinta_vinho':  ('liso', dict(cor=(0.30, 0.03, 0.025), rug=0.55)),
}
ESCALA_UV = {'tinta': 2.6, 'reboco': 0.62, 'cimento': 0.3, 'latao': 1.6, 'ferro': 1.4, 'vidro': 0.7, 'pinho': 0.7}


def _n(nt, tipo, **props):
    n = nt.nodes.new(tipo)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def _math(nt, op, a, b=None, clamp=False):
    n = _n(nt, 'ShaderNodeMath', operation=op, use_clamp=clamp)
    for i, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    return n.outputs[0]


def _mix(nt, f, a, b):
    n = _n(nt, 'ShaderNodeMix', data_type='RGBA')
    for sock, x in ((n.inputs[0], f), (n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(x, (int, float)):
            sock.default_value = x
        elif isinstance(x, tuple):
            sock.default_value = (*x, 1)
        else:
            nt.links.new(x, sock)
    return n.outputs[2]


def _mixf(nt, f, a, b):
    n = _n(nt, 'ShaderNodeMix', data_type='FLOAT')
    for sock, x in ((n.inputs[0], f), (n.inputs[2], a), (n.inputs[3], b)):
        if isinstance(x, (int, float)):
            sock.default_value = x
        else:
            nt.links.new(x, sock)
    return n.outputs[0]


def _smooth(nt, x, lo, hi):
    n = _n(nt, 'ShaderNodeMapRange', interpolation_type='SMOOTHSTEP')
    nt.links.new(x, n.inputs[0])
    n.inputs[1].default_value, n.inputs[2].default_value = lo, hi
    return n.outputs[0]


def _noise(nt, vec, scale, detail=3.0, rough=0.55):
    n = _n(nt, 'ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail
    n.inputs['Roughness'].default_value = rough
    nt.links.new(vec, n.inputs['Vector'])
    return n.outputs[0]


def _vm(nt, op, a, b=None, escala=None):
    n = _n(nt, 'ShaderNodeVectorMath', operation=op)
    for i, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, tuple):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    if escala is not None:
        if isinstance(escala, (int, float)):
            n.inputs['Scale'].default_value = escala
        else:
            nt.links.new(escala, n.inputs['Scale'])
    return n.outputs[0]


def _escala_cor(nt, cor, f):
    return _vm(nt, 'SCALE', cor, escala=f)


def _xyz(nt, v):
    s = _n(nt, 'ShaderNodeSeparateXYZ')
    nt.links.new(v, s.inputs[0])
    return s.outputs


def _comb(nt, x, y, z):
    c = _n(nt, 'ShaderNodeCombineXYZ')
    for i, q in enumerate((x, y, z)):
        if isinstance(q, (int, float)):
            c.inputs[i].default_value = q
        else:
            nt.links.new(q, c.inputs[i])
    return c.outputs[0]


def _ao(nt, dist, dentro=False, amostras=12):
    a = _n(nt, 'ShaderNodeAmbientOcclusion', inside=dentro, only_local=True, samples=amostras)
    a.inputs['Distance'].default_value = dist
    return a.outputs['AO']


def _veio(nt, pos, S, s):
    """Vetor esticado ao longo do veio (atributo 'veio': eixo em RGB, semente em A)."""
    at = _n(nt, 'ShaderNodeAttribute', attribute_name='veio', attribute_type='GEOMETRY')
    k = _vm(nt, 'ADD', _vm(nt, 'SCALE', at.outputs['Color'], escala=s - S), (S, S, S))
    v = _vm(nt, 'MULTIPLY', pos, k)
    sd = at.outputs['Alpha']
    off = _comb(nt, _math(nt, 'MULTIPLY', sd, 31.7), _math(nt, 'MULTIPLY', sd, 17.3), _math(nt, 'MULTIPLY', sd, 23.9))
    return _vm(nt, 'ADD', v, off), sd


def _riscos(nt, pos, esc=(60, 1.6, 26), rot=(0.3, 0.2, 0.5), lo=0.70, hi=0.76):
    mp = _n(nt, 'ShaderNodeMapping')
    mp.inputs['Scale'].default_value = esc
    mp.inputs['Rotation'].default_value = rot
    nt.links.new(pos, mp.inputs[0])
    return _smooth(nt, _noise(nt, mp.outputs[0], 1.0, 1.0), lo, hi)


# ------------------------------------------------------------------ famílias
def f_liso(nt, pos, geo, p):
    return dict(cor=p['cor'], rug=p['rug'], met=0.0, alt=None, ao=1.0)


def f_gen(nt, pos, geo, p):
    base, rug, met, cg, rg, mg, kd, grao, suj = p['p']
    e = p.get('esc', 1.0)                       # 1 = objeto pequeno (ferragem); 0.12 = peça de construção
    fino = p.get('fino', False)
    v1 = _noise(nt, pos, 22.0 * e, 3.0)
    v2 = _noise(nt, pos, 140.0 * e, 4.0)
    g = _noise(nt, pos, 1500.0 if e == 1.0 else 420.0, 2.0, 0.6)
    aresta = 0.0 if fino else _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.0012 / e ** 0.5, True))
    cav = _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.008 / e ** 0.5))
    if fino:
        mod = _math(nt, 'MULTIPLY', _smooth(nt, v2, 0.5, 0.8), _smooth(nt, v1, 0.45, 0.7))
        gasto = _math(nt, 'MULTIPLY', mod, 0.8 * min(1.0, kd), clamp=True)
    else:
        mod = _math(nt, 'MULTIPLY', aresta, _math(nt, 'ADD', _math(nt, 'MULTIPLY', v2, 1.5), 0.15))
        mod = _math(nt, 'MULTIPLY', mod, _math(nt, 'ADD', _math(nt, 'MULTIPLY', v1, 1.2), 0.4))
        mod = _math(nt, 'MULTIPLY', mod, _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 55.0 * e, 2.0), 0.38, 0.62), 1.3 * max(1.0, kd)))
        gasto = _math(nt, 'MULTIPLY', _smooth(nt, mod, 0.26, 0.68), 0.9 * min(1.0, kd), clamp=True)
        if kd > 1.2:    # lascas largas (esmalte): manchas soltas além das arestas
            lasca = _smooth(nt, _math(nt, 'MULTIPLY', _noise(nt, pos, 38.0 * e, 3.0), _math(nt, 'ADD', v1, 0.35)), 0.50, 0.54)
            gasto = _math(nt, 'MAXIMUM', gasto, lasca)
        gasto = _math(nt, 'MULTIPLY', gasto, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, cav, 0.25, 0.6)), clamp=True)
    risco = _riscos(nt, pos, (900 * e, 25 * e, 400 * e))
    risco = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', risco, _smooth(nt, v1, 0.45, 0.7)), 0.35 * min(kd, 1.0))
    gasto2 = _math(nt, 'MAXIMUM', gasto, risco)
    manchas = _smooth(nt, v1, 0.55, 0.8)
    sujo = _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'MULTIPLY', cav, _math(nt, 'ADD', v2, 0.55)), 0.22, 0.75), min(1.0, 0.75 * suj), clamp=True)
    # oxidação / manchas largas
    oxi = _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'MULTIPLY', v1, _math(nt, 'ADD', v2, 0.5)), 0.42, 0.62), 0.55 * min(1.0, suj))
    sujo = _math(nt, 'MAXIMUM', sujo, oxi)
    tom = _math(nt, 'ADD', 0.80, _math(nt, 'MULTIPLY', v1, 0.40))
    cor = _mix(nt, gasto2, _escala_cor(nt, base, tom), cg)
    cor = _mix(nt, sujo, cor, p.get('mancha', (0.085, 0.078, 0.064)))
    r = _math(nt, 'ADD', rug, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', v2, 0.5), 0.22))
    r = _math(nt, 'SUBTRACT', r, _math(nt, 'MULTIPLY', manchas, 0.10))
    r = _mixf(nt, gasto2, r, rg)
    r = _mixf(nt, sujo, r, 0.85)
    r = _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', g, 0.5), 0.10 * min(grao, 1.0)), clamp=True)
    mt = _mixf(nt, gasto2, met, mg)
    mt = _math(nt, 'MULTIPLY', mt, _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', sujo, 0.8)))
    alt = _math(nt, 'MULTIPLY', g, 0.00006 * grao / e ** 0.5)
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', gasto, 0.00012 if kd > 1.2 else 0.0))
    return dict(cor=cor, rug=r, met=mt, alt=alt, ao=_ao(nt, 0.03 / e ** 0.5, False, 16))


def f_pintura(nt, pos, geo, p):
    k = p['descasca']
    v1 = _noise(nt, pos, 2.6, 3.0)
    v2 = _noise(nt, pos, 21.0, 4.0)
    fib_v, sd = _veio(nt, pos, 260.0, 7.0)
    fib = _noise(nt, fib_v, 1.0, 3.0, 0.6)
    lg_v, _ = _veio(nt, pos, 34.0, 2.2)
    lg = _noise(nt, lg_v, 1.0, 3.0, 0.6)
    aresta = _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.005, True))
    cav = _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.035))
    # tinta descascando: começa nas arestas e segue o veio
    e = _math(nt, 'MULTIPLY', aresta, _math(nt, 'ADD', _math(nt, 'MULTIPLY', v2, 1.3), 0.25))
    e = _math(nt, 'ADD', e, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', lg, 0.5), 1.25))
    e = _math(nt, 'ADD', e, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', v1, 0.5), 0.9))
    e = _math(nt, 'ADD', e, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', sd, 0.5), 0.22))
    e = _math(nt, 'ADD', e, k - 0.12)
    solta = _smooth(nt, e, 0.60, 0.64)
    solta = _math(nt, 'MULTIPLY', solta, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, cav, 0.45, 0.8)))
    quase = _smooth(nt, e, 0.36, 0.60)
    vo = _n(nt, 'ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE')
    cv, _ = _veio(nt, pos, 85.0, 16.0)
    nt.links.new(cv, vo.inputs['Vector']); vo.inputs['Scale'].default_value = 1.0
    trinca = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, vo.outputs['Distance'], 0.0, 0.045)), quase)
    trinca = _math(nt, 'MULTIPLY', trinca, _math(nt, 'SUBTRACT', 1.0, solta))
    # sujeira: reentrâncias; por fora, escorridos verticais e respingo perto do chão
    sujo = _smooth(nt, _math(nt, 'MULTIPLY', cav, _math(nt, 'ADD', v2, 0.55)), 0.2, 0.8)
    if p['ext']:
        mp = _n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (26, 26, 1.1); nt.links.new(pos, mp.inputs[0])
        esc = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, mp.outputs[0], 1.0, 2.0), 0.52, 0.78), _math(nt, 'ADD', v1, 0.2))
        z = _xyz(nt, pos)[2]
        chao = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, z, 0.0, 0.55)), _math(nt, 'ADD', v2, 0.3))
        sujo = _math(nt, 'MAXIMUM', sujo, _math(nt, 'MULTIPLY', esc, 0.55))
        sujo = _math(nt, 'MAXIMUM', sujo, _math(nt, 'MULTIPLY', chao, 0.7))
    sujo = _math(nt, 'MULTIPLY', sujo, min(1.0, 0.7 * p['suj']), clamp=True)
    tom = _math(nt, 'ADD', 0.86, _math(nt, 'MULTIPLY', v1, 0.22))
    tom = _math(nt, 'ADD', tom, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', sd, 0.5), 0.10))
    tinta = _escala_cor(nt, p['cor'], tom)
    tinta = _mix(nt, _math(nt, 'MULTIPLY', v2, p.get('giz', 0.12)), tinta, (0.75, 0.75, 0.72))          # giz / desbotado
    mad = _escala_cor(nt, (0.36, 0.33, 0.29), _math(nt, 'ADD', 0.45, _math(nt, 'MULTIPLY', fib, 1.0)))
    mad = _mix(nt, _smooth(nt, lg, 0.45, 0.7), mad, (0.20, 0.15, 0.10))
    cor = _mix(nt, solta, tinta, mad)
    cor = _mix(nt, _math(nt, 'MULTIPLY', trinca, 0.75), cor, (0.10, 0.09, 0.075))
    cor = _mix(nt, sujo, cor, (0.115, 0.10, 0.07))
    r = _math(nt, 'ADD', p['rug'], _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', v2, 0.5), 0.18))
    r = _mixf(nt, solta, r, 0.90)
    r = _mixf(nt, sujo, r, 0.92)
    pinc_v, _ = _veio(nt, pos, 520.0, 22.0)
    pinc = _noise(nt, pinc_v, 1.0, 2.0)
    alt = _mixf(nt, solta, _math(nt, 'ADD', 0.00045, _math(nt, 'MULTIPLY', pinc, 0.00007)), _math(nt, 'MULTIPLY', fib, 0.00055))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', trinca, 0.00035))
    alt = _math(nt, 'ADD', alt, _math(nt, 'MULTIPLY', quase, 0.00012))
    return dict(cor=cor, rug=r, met=0.0, alt=alt, ao=_ao(nt, 0.10, False, 16))


def f_tijolo(nt, pos, geo, p):
    v1 = _noise(nt, pos, 2.2, 3.0)
    v2 = _noise(nt, pos, 19.0, 4.0)
    g = _noise(nt, pos, 260.0, 3.0, 0.65)
    px, py, pz = _xyz(nt, pos)
    nx = _xyz(nt, geo.outputs['True Normal'])[0]
    lado = _smooth(nt, _math(nt, 'ABSOLUTE', nx), 0.45, 0.55)
    u = _mixf(nt, lado, px, _math(nt, 'ADD', py, 0.1125))
    w1 = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', _noise(nt, pos, 55.0, 2.0), 0.5), 0.007)
    vec = _comb(nt, _math(nt, 'ADD', u, w1), _math(nt, 'ADD', _math(nt, 'ADD', pz, 0.45), w1), 0.0)
    def tij(c1, c2):
        b = _n(nt, 'ShaderNodeTexBrick', offset=0.5)
        nt.links.new(vec, b.inputs['Vector'])
        b.inputs['Color1'].default_value = c1; b.inputs['Color2'].default_value = c2
        b.inputs['Scale'].default_value = 1.0; b.inputs['Mortar Size'].default_value = 0.0055; b.inputs['Mortar Smooth'].default_value = 0.35
        b.inputs['Bias'].default_value = 0.0; b.inputs['Brick Width'].default_value = 0.225; b.inputs['Row Height'].default_value = 0.075
        return b
    b = tij((0, 0, 0, 1), (1, 1, 1, 1))
    t = _xyz(nt, b.outputs['Color'])[0]
    junta = b.outputs['Fac']
    cb = _mix(nt, t, (0.36, 0.115, 0.07), (0.21, 0.075, 0.055))
    cb = _mix(nt, _smooth(nt, t, 0.80, 0.86), cb, (0.085, 0.06, 0.055))            # tijolos requeimados
    cb = _mix(nt, _smooth(nt, t, 0.05, 0.0), cb, (0.44, 0.20, 0.11))
    cb = _escala_cor(nt, cb, _math(nt, 'ADD', 0.72, _math(nt, 'MULTIPLY', v2, 0.56)))
    poro = _smooth(nt, _noise(nt, pos, 95.0, 2.0), 0.63, 0.74)
    cb = _mix(nt, _math(nt, 'MULTIPLY', poro, 0.6), cb, (0.07, 0.045, 0.035))
    cm = _escala_cor(nt, (0.42, 0.40, 0.36), _math(nt, 'ADD', 0.7, _math(nt, 'MULTIPLY', g, 0.6)))
    cor = _mix(nt, junta, cb, cm)
    baixo = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pz, -0.42, -0.12))
    musgo = _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'MULTIPLY', baixo, _math(nt, 'ADD', v2, 0.45)), 0.35, 0.75), 0.75)
    musgo = _math(nt, 'MULTIPLY', musgo, _math(nt, 'ADD', 0.55, _math(nt, 'MULTIPLY', junta, 0.45)))
    cor = _mix(nt, musgo, cor, (0.055, 0.065, 0.030))
    sal = _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'MULTIPLY', v1, v2), 0.30, 0.42), 0.38)
    sal = _math(nt, 'MULTIPLY', sal, _math(nt, 'SUBTRACT', 1.0, junta))
    cor = _mix(nt, sal, cor, (0.62, 0.60, 0.55))
    alt = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, junta), 0.0045)
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', poro, 0.0012))
    alt = _math(nt, 'ADD', alt, _math(nt, 'MULTIPLY', g, 0.0009))
    alt = _math(nt, 'ADD', alt, _math(nt, 'MULTIPLY', t, 0.0012))
    ao = _math(nt, 'MULTIPLY', _ao(nt, 0.2, False, 16), _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', junta, 0.45)))
    return dict(cor=cor, rug=_math(nt, 'ADD', 0.86, _math(nt, 'MULTIPLY', g, 0.1)), met=0.0, alt=alt, ao=ao)


def f_reboco(nt, pos, geo, p):
    v1 = _noise(nt, pos, 1.7, 3.0)
    v2 = _noise(nt, pos, 16.0, 4.0)
    g = _noise(nt, pos, 420.0, 2.0, 0.6)
    cav = _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.05))
    pz = _xyz(nt, pos)[2]
    cor = _escala_cor(nt, p['cor'], _math(nt, 'ADD', 0.88, _math(nt, 'MULTIPLY', v1, 0.24)))
    cor = _mix(nt, _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 0.8, 2.0), 0.52, 0.56), 0.10), cor, (0.70, 0.70, 0.62))     # remendo de pintura
    # trincas finas
    wv = _vm(nt, 'ADD', pos, _vm(nt, 'SCALE', _n(nt, 'ShaderNodeTexNoise').outputs['Color'], escala=0.0))
    nz = _n(nt, 'ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nt.links.new(pos, nz.inputs['Vector'])
    wv = _vm(nt, 'ADD', pos, _vm(nt, 'SCALE', nz.outputs['Color'], escala=0.22))
    vo = _n(nt, 'ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE'); vo.inputs['Scale'].default_value = 2.1
    nt.links.new(wv, vo.inputs['Vector'])
    zona = _smooth(nt, _noise(nt, pos, 0.9, 2.0), 0.50, 0.60)
    trinca = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, vo.outputs['Distance'], 0.0, 0.0035)), zona)
    trinca = _math(nt, 'MULTIPLY', trinca, _smooth(nt, _noise(nt, pos, 7.0, 2.0), 0.35, 0.5))
    # mancha de infiltração (contorno + miolo amarelado)
    w = _noise(nt, _vm(nt, 'ADD', pos, (3.1, 1.7, 0.4)), 1.25, 3.0)
    alto = _smooth(nt, pz, 1.2, 2.6)
    miolo = _math(nt, 'MULTIPLY', _smooth(nt, w, 0.675, 0.70), alto)
    borda = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', _smooth(nt, w, 0.665, 0.678), _math(nt, 'SUBTRACT', 1.0, _smooth(nt, w, 0.682, 0.70))), alto)
    cor = _mix(nt, _math(nt, 'MULTIPLY', miolo, 0.28), cor, (0.50, 0.40, 0.20))
    cor = _mix(nt, _math(nt, 'MULTIPLY', borda, 0.5), cor, (0.30, 0.22, 0.10))
    # encardido: reentrâncias, faixa de mãos/móveis e perto do piso
    perto = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pz, 0.14, 0.75)), _math(nt, 'ADD', v2, 0.25))
    sujo = _math(nt, 'MAXIMUM', _smooth(nt, _math(nt, 'MULTIPLY', cav, _math(nt, 'ADD', v2, 0.5)), 0.2, 0.8), _math(nt, 'MULTIPLY', perto, 0.5))
    mp = _n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (20, 20, 0.9); nt.links.new(pos, mp.inputs[0])
    esc = _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, mp.outputs[0], 1.0, 2.0), 0.60, 0.82), 0.22)
    sujo = _math(nt, 'MULTIPLY', _math(nt, 'MAXIMUM', sujo, esc), 0.55, clamp=True)
    cor = _mix(nt, sujo, cor, (0.20, 0.18, 0.13))
    cor = _mix(nt, _math(nt, 'MULTIPLY', trinca, 0.8), cor, (0.10, 0.09, 0.08))
    alt = _math(nt, 'ADD', _math(nt, 'MULTIPLY', g, 0.00022), _math(nt, 'MULTIPLY', _noise(nt, pos, 9.0, 2.0), 0.0012))
    alt = _math(nt, 'ADD', alt, _math(nt, 'MULTIPLY', _riscos(nt, pos, (38, 4, 38), (0.1, 0.5, 0.2), 0.55, 0.8), 0.00012))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', trinca, 0.0007))
    alt = _math(nt, 'ADD', alt, _math(nt, 'MULTIPLY', borda, 0.00025))
    r = _math(nt, 'ADD', 0.80, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', v2, 0.5), 0.16))
    return dict(cor=cor, rug=r, met=0.0, alt=alt, ao=_ao(nt, 0.25, False, 16))


def f_assoalho(nt, pos, geo, p):
    LARG, COMP = 0.095, 1.9
    v1 = _noise(nt, pos, 1.6, 3.0)
    v2 = _noise(nt, pos, 18.0, 4.0)
    px, py, pz = _xyz(nt, pos)
    fx = _math(nt, 'DIVIDE', _math(nt, 'ADD', px, 20.0), LARG)
    fila = _math(nt, 'FLOOR', fx)
    wn = _n(nt, 'ShaderNodeTexWhiteNoise', noise_dimensions='1D'); nt.links.new(fila, wn.inputs['W'])
    yy = _math(nt, 'DIVIDE', _math(nt, 'ADD', _math(nt, 'ADD', py, 20.0), _math(nt, 'MULTIPLY', wn.outputs['Value'], COMP)), COMP)
    idp = _math(nt, 'FLOOR', yy)
    w2 = _n(nt, 'ShaderNodeTexWhiteNoise', noise_dimensions='2D'); nt.links.new(_comb(nt, fila, idp, 0.0), w2.inputs['Vector'])
    rnd = w2.outputs['Value']
    r2 = _xyz(nt, w2.outputs['Color'])[1]
    dx = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 0.5, _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', fx), 0.5))), LARG)
    dy = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 0.5, _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', yy), 0.5))), COMP)
    d = _math(nt, 'MINIMUM', dx, dy)
    fresta = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, d, 0.0004, 0.0016))
    beira = _math(nt, 'SUBTRACT', 1.0, _smooth(nt, d, 0.0015, 0.012))
    gv = _comb(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', px, 30.0), _math(nt, 'MULTIPLY', rnd, 57.0)),
               _math(nt, 'ADD', _math(nt, 'MULTIPLY', py, 1.5), _math(nt, 'MULTIPLY', r2, 91.0)), _math(nt, 'MULTIPLY', rnd, 13.0))
    n1 = _noise(nt, gv, 1.0, 3.0, 0.55)
    aneis = _math(nt, 'MULTIPLY', _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'MULTIPLY', n1, 9.0)), 0.5)), 2.0)
    aneis = _smooth(nt, aneis, 0.15, 0.85)
    poros = _noise(nt, _comb(nt, _math(nt, 'MULTIPLY', px, 520.0), _math(nt, 'MULTIPLY', py, 16.0), rnd), 1.0, 2.0, 0.6)
    cor = _mix(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', aneis, 0.55), _math(nt, 'MULTIPLY', n1, 0.35)), p['c1'], p['c2'])
    cor = _escala_cor(nt, cor, _math(nt, 'ADD', 0.62, _math(nt, 'MULTIPLY', rnd, 0.60)))
    cor = _mix(nt, _math(nt, 'MULTIPLY', _smooth(nt, poros, 0.55, 0.75), 0.35), cor, (0.06, 0.03, 0.015))
    # verniz gasto nos caminhos e nas beiras das tábuas
    gasto = _math(nt, 'ADD', _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'ADD', v1, _math(nt, 'MULTIPLY', v2, 0.25)), 0.54, 0.80), 0.7), _math(nt, 'MULTIPLY', beira, _math(nt, 'MULTIPLY', v2, 0.9)))
    gasto = _math(nt, 'MINIMUM', gasto, 1.0)
    cinza = _escala_cor(nt, (0.30, 0.255, 0.20), _math(nt, 'ADD', 0.6, _math(nt, 'MULTIPLY', poros, 0.7)))
    cor = _mix(nt, _math(nt, 'MULTIPLY', gasto, 0.78), cor, cinza)
    risco = _math(nt, 'MULTIPLY', _riscos(nt, pos, (70, 2.2, 30), (0.0, 0.0, 0.9), 0.68, 0.74), _smooth(nt, v1, 0.35, 0.6))
    cor = _mix(nt, _math(nt, 'MULTIPLY', risco, 0.35), cor, (0.55, 0.47, 0.36))
    po = _math(nt, 'MULTIPLY', _smooth(nt, v2, 0.45, 0.8), 0.22)
    cor = _mix(nt, po, cor, (0.30, 0.27, 0.22))
    cor = _mix(nt, fresta, cor, (0.018, 0.014, 0.010))
    r = _mixf(nt, gasto, 0.30, 0.72)
    r = _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', v2, 0.5), 0.2))
    r = _math(nt, 'MAXIMUM', r, _math(nt, 'MULTIPLY', risco, 0.7))
    r = _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', po, 1.2))
    r = _mixf(nt, fresta, r, 0.95)
    alt = _math(nt, 'ADD', _math(nt, 'MULTIPLY', rnd, 0.0006), _math(nt, 'MULTIPLY', aneis, 0.00010))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', beira, 0.0005))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', fresta, 0.003))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', _smooth(nt, poros, 0.55, 0.75), 0.00008))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', risco, 0.00012))
    ao = _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', fresta, 0.7))
    return dict(cor=cor, rug=r, met=0.0, alt=alt, ao=ao)


def f_verniz(nt, pos, geo, p):
    v1 = _noise(nt, pos, 9.0, 3.0)
    v2 = _noise(nt, pos, 70.0, 4.0)
    gv, sd = _veio(nt, pos, 46.0, 2.4)
    n1 = _noise(nt, gv, 1.0, 3.0, 0.55)
    aneis = _math(nt, 'MULTIPLY', _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', _math(nt, 'MULTIPLY', n1, 8.0)), 0.5)), 2.0)
    aneis = _smooth(nt, aneis, 0.1, 0.9)
    pv, _ = _veio(nt, pos, 900.0, 28.0)
    poros = _smooth(nt, _noise(nt, pv, 1.0, 2.0, 0.6), 0.52, 0.72)
    aresta = _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.0035, True))
    cav = _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.02))
    cor = _mix(nt, _math(nt, 'ADD', _math(nt, 'MULTIPLY', aneis, 0.6), _math(nt, 'MULTIPLY', n1, 0.3)), p['c1'], p['c2'])
    cor = _escala_cor(nt, cor, _math(nt, 'ADD', 0.80, _math(nt, 'MULTIPLY', sd, 0.40)))
    cor = _mix(nt, _math(nt, 'MULTIPLY', poros, 0.45), cor, _escala_cor(nt, p['c1'], 0.35))
    mod = _math(nt, 'MULTIPLY', aresta, _math(nt, 'ADD', _math(nt, 'MULTIPLY', v2, 1.4), 0.2))
    mod = _math(nt, 'MULTIPLY', mod, _math(nt, 'ADD', _math(nt, 'MULTIPLY', v1, 1.3), 0.45))
    gasto = _math(nt, 'MULTIPLY', _smooth(nt, mod, 0.24, 0.62), 0.92 * min(1.0, p['kd']), clamp=True)
    gasto = _math(nt, 'MAXIMUM', gasto, _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'MULTIPLY', v1, _math(nt, 'ADD', v2, 0.4)), 0.56, 0.70), 0.16 * p['kd']))
    cru = _escala_cor(nt, p['cru'], _math(nt, 'ADD', 0.65, _math(nt, 'MULTIPLY', aneis, 0.5)))
    cor = _mix(nt, gasto, cor, cru)
    risco = _math(nt, 'MULTIPLY', _riscos(nt, pos, (260, 7, 120), (0.2, 0.3, 0.6), 0.70, 0.75), _math(nt, 'MULTIPLY', _smooth(nt, v1, 0.4, 0.65), p['kd']))
    cor = _mix(nt, _math(nt, 'MULTIPLY', risco, 0.4), cor, p['cru'])
    nz = _xyz(nt, geo.outputs['True Normal'])[2]
    cima = _smooth(nt, nz, 0.6, 0.9)
    po = _math(nt, 'MULTIPLY', _math(nt, 'MAXIMUM', _math(nt, 'MULTIPLY', cima, _math(nt, 'ADD', 0.35, _math(nt, 'MULTIPLY', v2, 0.5))),
                                     _smooth(nt, _math(nt, 'MULTIPLY', cav, _math(nt, 'ADD', v2, 0.5)), 0.2, 0.75)), 0.5 * p['po'], clamp=True)
    cor = _mix(nt, po, cor, (0.33, 0.30, 0.25))
    r = _math(nt, 'ADD', p['rug'], _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', v2, 0.5), 0.14))
    r = _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', poros, 0.12))
    r = _mixf(nt, gasto, r, 0.68)
    r = _math(nt, 'MAXIMUM', r, _math(nt, 'MULTIPLY', risco, 0.6))
    r = _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', po, 0.9), clamp=True)
    alt = _math(nt, 'SUBTRACT', _math(nt, 'MULTIPLY', aneis, 0.00003), _math(nt, 'MULTIPLY', poros, 0.00006))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', gasto, 0.00008))
    alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', risco, 0.00006))
    return dict(cor=cor, rug=r, met=0.0, alt=alt, ao=_ao(nt, 0.06, False, 16))


def f_vidro(nt, pos, geo, p):
    v1 = _noise(nt, pos, 5.0, 3.0)
    v2 = _noise(nt, pos, 45.0, 4.0)
    cav = _math(nt, 'SUBTRACT', 1.0, _ao(nt, 0.035))
    mp = _n(nt, 'ShaderNodeMapping'); mp.inputs['Scale'].default_value = (40, 40, 2.0); nt.links.new(pos, mp.inputs[0])
    esc = _smooth(nt, _noise(nt, mp.outputs[0], 1.0, 2.0), 0.55, 0.8)
    suj = _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'MULTIPLY', cav, _math(nt, 'ADD', v2, 0.6)), 0.12, 0.8), 0.85)
    suj = _math(nt, 'ADD', suj, _math(nt, 'MULTIPLY', _smooth(nt, v1, 0.5, 0.85), 0.14))
    suj = _math(nt, 'ADD', suj, _math(nt, 'MULTIPLY', esc, 0.16), clamp=True)
    cor = _mix(nt, v2, (0.30, 0.28, 0.23), (0.48, 0.46, 0.40))
    alfa = _math(nt, 'ADD', 0.05, _math(nt, 'MULTIPLY', suj, 0.50), clamp=True)
    r = _math(nt, 'ADD', 0.04, _math(nt, 'MULTIPLY', suj, 0.6), clamp=True)
    return dict(cor=cor, rug=r, met=0.0, alt=None, ao=1.0, alfa=alfa)


FAMILIAS = dict(liso=f_liso, gen=f_gen, pintura=f_pintura, tijolo=f_tijolo, reboco=f_reboco, assoalho=f_assoalho, verniz=f_verniz, vidro=f_vidro)


def montar_material(m, nome):
    fam, prm = CLASSES[nome]
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links
    geo = _n(nt, 'ShaderNodeNewGeometry')
    out = _n(nt, 'ShaderNodeOutputMaterial')
    if fam in ('verniz', 'gen', 'liso', 'vidro_obj'):
        pos = _n(nt, 'ShaderNodeTexCoord').outputs['Object']
    else:
        pos = geo.outputs['Position']
    S = FAMILIAS[fam](nt, pos, geo, prm)
    S.setdefault('alfa', 1.0)
    em = _n(nt, 'ShaderNodeEmission')
    bs = _n(nt, 'ShaderNodeBsdfPrincipled')
    bz = prm.get('bisel', 0.0)
    nor = None
    if bz > 0:
        bev = _n(nt, 'ShaderNodeBevel', samples=6)
        bev.inputs['Radius'].default_value = bz
        nor = bev.outputs[0]
    if S['alt'] is not None:
        bmp = _n(nt, 'ShaderNodeBump')
        bmp.inputs['Strength'].default_value = 1.0
        bmp.inputs['Distance'].default_value = 1.0
        L.new(S['alt'], bmp.inputs['Height'])
        if nor is not None:
            L.new(nor, bmp.inputs['Normal'])
        nor = bmp.outputs[0]
    if nor is not None:
        L.new(nor, bs.inputs['Normal'])
    img = _n(nt, 'ShaderNodeTexImage')
    return S, em, bs, out, img


_INFO = {}


def preparar_materiais():
    _INFO.clear()
    for m in bpy.data.materials:
        if m.name in CLASSES:
            _INFO[m.name] = montar_material(m, m.name)


def passe(nome):
    for mn, (S, em, bs, out, img) in _INFO.items():
        nt = bpy.data.materials[mn].node_tree
        for l in list(out.inputs[0].links):
            nt.links.remove(l)
        for l in list(em.inputs[0].links):
            nt.links.remove(l)
        if nome == 'normal':
            nt.links.new(bs.outputs[0], out.inputs[0])
            continue
        x = S[nome]
        if isinstance(x, tuple):
            em.inputs[0].default_value = (*x, 1)
        elif isinstance(x, (int, float)):
            em.inputs[0].default_value = (x, x, x, 1)
        else:
            nt.links.new(x, em.inputs[0])
        nt.links.new(em.outputs[0], out.inputs[0])


def previa():
    """Liga os materiais direto no BSDF, para renders de conferência sem bake."""
    for mn, (S, em, bs, out, img) in _INFO.items():
        nt = bpy.data.materials[mn].node_tree
        for nome, sock in (('cor', 'Base Color'), ('rug', 'Roughness'), ('met', 'Metallic'), ('alfa', 'Alpha')):
            x = S[nome]
            if isinstance(x, tuple):
                bs.inputs[sock].default_value = (*x, 1)
            elif isinstance(x, (int, float)):
                bs.inputs[sock].default_value = x
            else:
                nt.links.new(x, bs.inputs[sock])
        nt.links.new(bs.outputs[0], out.inputs[0])
        bpy.data.materials[mn]['pronto'] = 1


def desdobrar(objs, margem=0.004):
    import bmesh
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
        if not o.data.uv_layers:
            o.data.uv_layers.new(name='UVMap')
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(62), island_margin=0.0, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    for o in objs:
        esc = {}
        for i, m in enumerate(o.data.materials):
            for pre, k in ESCALA_UV.items():
                if m and m.name.startswith(pre):
                    esc[i] = k
        if not esc:
            continue
        bm = bmesh.from_edit_mesh(o.data)
        uv = bm.loops.layers.uv.verify()
        vistos = set()
        for f in bm.faces:
            if f.material_index not in esc or f in vistos:
                continue
            mi = f.material_index
            ilha, pilha = [], [f]
            vistos.add(f)
            while pilha:
                a = pilha.pop()
                ilha.append(a)
                for e in a.edges:
                    for b in e.link_faces:
                        if b not in vistos and b.material_index == mi:
                            vistos.add(b)
                            pilha.append(b)
            ls = [l for a in ilha for l in a.loops]
            cx = sum(l[uv].uv.x for l in ls) / len(ls)
            cy = sum(l[uv].uv.y for l in ls) / len(ls)
            for l in ls:
                l[uv].uv.x = cx + (l[uv].uv.x - cx) * esc[mi]
                l[uv].uv.y = cy + (l[uv].uv.y - cy) * esc[mi]
        bmesh.update_edit_mesh(o.data)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin=margem)
    bpy.ops.object.mode_set(mode='OBJECT')


def assar(objs, res, amostras=6):
    """Devolve dict passe -> array float (res, res, 3) linear."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = amostras
    sc.cycles.use_denoising = False
    sc.render.bake.margin = max(3, res // 512)
    sc.render.bake.use_clear = True
    sc.render.bake.use_selected_to_active = False
    img = bpy.data.images.new('alvo', res, res, alpha=False, float_buffer=True)
    img.colorspace_settings.name = 'Non-Color'
    for mn, (S, em, bs, out, node) in _INFO.items():
        node.image = img
        nt = bpy.data.materials[mn].node_tree
        for n in nt.nodes:
            n.select = False
        node.select = True
        nt.nodes.active = node
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    tem_vidro = any(m and m.name == 'vidro' for o in objs for m in o.data.materials)
    saida = {}
    for p in ('cor', 'rug', 'met', 'ao', 'normal') + (('alfa',) if tem_vidro else ()):
        passe(p)
        bpy.ops.object.bake(type='NORMAL' if p == 'normal' else 'EMIT')
        a = np.empty(res * res * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        saida[p] = a.reshape(res, res, 4)[::-1, :, :3].copy()
    bpy.data.images.remove(img)
    return saida


def srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def salvar(passes, prefixo):
    from PIL import Image
    os.makedirs(os.path.dirname(prefixo), exist_ok=True)
    u8 = lambda x: (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
    cor = u8(srgb(passes['cor']))
    if 'alfa' in passes:
        cor = np.dstack([cor, u8(passes['alfa'][..., 0])])
    Image.fromarray(cor).save(prefixo + '_cor.png')
    orm = np.stack([passes['ao'][..., 0], passes['rug'][..., 0], passes['met'][..., 0]], axis=-1)
    Image.fromarray(u8(orm)).save(prefixo + '_orm.png')
    Image.fromarray(u8(passes['normal'])).save(prefixo + '_normal.png')
