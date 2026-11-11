"""UVs, materiais procedurais e bake (Cycles) das texturas PBR da M4A1."""
import math, os
import bpy
import numpy as np

# classe: cor base, rugosidade, metal, cor gasta, rug. gasta, metal gasto, quanto desgaste, grão, sujeira
CLASSES = {
    'anod':        ((0.034, 0.037, 0.033), 0.50, 0.75, (0.30, 0.31, 0.32), 0.32, 1.0, 1.00, 0.25, 1.0),
    'anod_tubo':   ((0.050, 0.052, 0.050), 0.46, 0.80, (0.32, 0.33, 0.34), 0.32, 1.0, 1.10, 0.20, 0.8),
    'fosf':        ((0.040, 0.042, 0.038), 0.68, 0.60, (0.25, 0.25, 0.24), 0.38, 1.0, 1.00, 0.55, 1.0),
    'fosf_escuro': ((0.085, 0.085, 0.082), 0.50, 0.90, (0.40, 0.40, 0.39), 0.30, 1.0, 0.80, 0.40, 0.6),
    'serr':        ((0.038, 0.040, 0.037), 0.62, 0.65, (0.30, 0.29, 0.28), 0.34, 1.0, 1.50, 0.50, 1.2),
    'inox':        ((0.42, 0.42, 0.41), 0.38, 1.0, (0.60, 0.60, 0.60), 0.28, 1.0, 0.50, 0.30, 1.2),
    'polim':       ((0.021, 0.022, 0.022), 0.60, 0.0, (0.060, 0.060, 0.058), 0.40, 0.0, 0.80, 1.00, 1.2),
    'polim_grip':  ((0.021, 0.022, 0.022), 0.60, 0.0, (0.060, 0.060, 0.058), 0.40, 0.0, 0.80, 1.00, 1.2),
    'polim_claro': ((0.060, 0.095, 0.050), 0.55, 0.0, (0.10, 0.14, 0.09), 0.40, 0.0, 0.50, 0.60, 0.8),
    'magal':       ((0.060, 0.062, 0.062), 0.56, 0.65, (0.40, 0.41, 0.42), 0.32, 1.0, 1.60, 0.35, 1.0),
    'latao':       ((0.80, 0.56, 0.22), 0.30, 1.0, (0.85, 0.62, 0.28), 0.25, 1.0, 0.30, 0.15, 0.6),
    'cobre':       ((0.72, 0.36, 0.20), 0.30, 1.0, (0.78, 0.42, 0.25), 0.25, 1.0, 0.30, 0.15, 0.6),
    'tinta':       ((0.42, 0.42, 0.39), 0.65, 0.0, None, 0, 0, 0, 0, 0),
    'tinta_preta': ((0.015, 0.015, 0.015), 0.60, 0.0, None, 0, 0, 0, 0, 0),
    'tan':         ((0.36, 0.25, 0.135), 0.58, 0.0, (0.50, 0.39, 0.25), 0.42, 0.0, 0.70, 0.60, 1.3),
    'vermelho':    ((0.42, 0.018, 0.016), 0.36, 0.85, (0.55, 0.36, 0.34), 0.30, 1.0, 0.35, 0.20, 0.8),
    'lente':       ((0.07, 0.11, 0.30), 0.05, 1.0, (0.07, 0.11, 0.30), 0.05, 1.0, 0.0, 0.0, 0.2),
    'lente_clara': ((0.62, 0.62, 0.58), 0.08, 1.0, (0.62, 0.62, 0.58), 0.08, 1.0, 0.0, 0.0, 0.2),
    'borracha':    ((0.014, 0.014, 0.014), 0.86, 0.0, (0.040, 0.040, 0.040), 0.70, 0.0, 0.50, 1.00, 1.5),
    'rotulo':      ((0.72, 0.50, 0.03), 0.50, 0.0, (0.62, 0.50, 0.20), 0.50, 0.0, 0.30, 0.20, 0.8),
}
RELEVO = {}                      # classe -> função(nt, posição, geometria) -> (altura, topo, fundo)
GRIP = dict(T=(-0.160, -0.056), B=(-0.207, -0.146))        # eixo do punho (u, v) em metros


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


def montar_material(m, nome):
    base, rug, met, cg, rg, mg, kd, grao, suj = CLASSES[nome]
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links
    geo = _n(nt, 'ShaderNodeNewGeometry')
    pos = geo.outputs['Position']
    out = _n(nt, 'ShaderNodeOutputMaterial')
    out.name = 'saida'
    S = {}
    if cg is None:                       # tinta das gravações
        S = dict(cor=base, rug=rug, met=met, alt=None, ao=1.0)
    else:
        v1 = _noise(nt, pos, 22.0, 3.0)
        v2 = _noise(nt, pos, 140.0, 4.0)
        g = _noise(nt, pos, 2600.0 if 'polim' in nome else 1700.0, 2.0, 0.6)
        ao_in = _n(nt, 'ShaderNodeAmbientOcclusion', inside=True, only_local=True, samples=12)
        ao_in.inputs['Distance'].default_value = 0.0014
        ao_ex = _n(nt, 'ShaderNodeAmbientOcclusion', inside=False, only_local=True, samples=12)
        ao_ex.inputs['Distance'].default_value = 0.010
        aresta = _math(nt, 'SUBTRACT', 1.0, ao_in.outputs['AO'])
        cav = _math(nt, 'SUBTRACT', 1.0, ao_ex.outputs['AO'])
        # desgaste nas arestas, quebrado por ruído
        mod = _math(nt, 'MULTIPLY', aresta, _math(nt, 'ADD', _math(nt, 'MULTIPLY', v2, 1.5), 0.15))
        mod = _math(nt, 'MULTIPLY', mod, _math(nt, 'ADD', _math(nt, 'MULTIPLY', v1, 1.2), 0.4))
        mod = _math(nt, 'MULTIPLY', mod, _math(nt, 'MULTIPLY', _smooth(nt, _noise(nt, pos, 55.0, 2.0), 0.38, 0.62), 1.3 * max(1.0, kd)))
        gasto = _math(nt, 'MULTIPLY', _smooth(nt, mod, 0.26, 0.68), 0.9 * min(1.0, kd), clamp=True)
        gasto = _math(nt, 'MULTIPLY', gasto, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, cav, 0.25, 0.6)), clamp=True)
        # riscos finos
        mp = _n(nt, 'ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (900, 25, 400)
        mp.inputs['Rotation'].default_value = (0.3, 0.2, 0.5)
        L.new(pos, mp.inputs[0])
        risco = _smooth(nt, _noise(nt, mp.outputs[0], 1.0, 1.0), 0.70, 0.76)
        risco = _math(nt, 'MULTIPLY', risco, _smooth(nt, v1, 0.45, 0.7))
        risco = _math(nt, 'MULTIPLY', risco, 0.35 * kd)
        gasto2 = _math(nt, 'MAXIMUM', gasto, risco)
        # polimento em áreas de manuseio (manchas largas mais lisas)
        manchas = _smooth(nt, v1, 0.55, 0.8)
        sujo = _math(nt, 'MULTIPLY', _smooth(nt, _math(nt, 'MULTIPLY', cav, _math(nt, 'ADD', v2, 0.55)), 0.22, 0.75),
                     min(1.0, 0.75 * suj), clamp=True)
        tom = _math(nt, 'ADD', 0.80, _math(nt, 'MULTIPLY', v1, 0.40))
        cb = _n(nt, 'ShaderNodeVectorMath', operation='SCALE')
        cb.inputs[0].default_value = base
        L.new(tom, cb.inputs['Scale'])
        cor = _mix(nt, gasto2, cb.outputs[0], cg)
        cor = _mix(nt, sujo, cor, (0.085, 0.078, 0.064))
        r = _math(nt, 'ADD', rug, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', v2, 0.5), 0.22))
        r = _math(nt, 'SUBTRACT', r, _math(nt, 'MULTIPLY', manchas, 0.10))
        r = _mixf(nt, gasto2, r, rg)
        r = _mixf(nt, sujo, r, 0.88)
        r = _math(nt, 'ADD', r, _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', g, 0.5), 0.10 * grao), clamp=True)
        mt = _mixf(nt, gasto2, met, mg)
        mt = _math(nt, 'MULTIPLY', mt, _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', sujo, 0.8)))
        alt = _math(nt, 'MULTIPLY', g, 0.00006 * grao)
        alt = _math(nt, 'SUBTRACT', alt, _math(nt, 'MULTIPLY', risco, 0.00008))
        if nome in ('polim_grip', 'tan_grip', 'verde_grip'):
            T, B = GRIP['T'], GRIP['B']
            Lg = math.hypot(B[0] - T[0], B[1] - T[1])
            a = ((B[0] - T[0]) / Lg, (B[1] - T[1]) / Lg)
            e = (-a[1], a[0]) if -a[1] > 0 else (a[1], -a[0])
            sep = _n(nt, 'ShaderNodeSeparateXYZ')
            L.new(pos, sep.inputs[0])
            du = _math(nt, 'SUBTRACT', sep.outputs['Y'], T[0])
            dv = _math(nt, 'SUBTRACT', sep.outputs['Z'], T[1])
            t = _math(nt, 'DIVIDE', _math(nt, 'ADD', _math(nt, 'MULTIPLY', du, a[0]), _math(nt, 'MULTIPLY', dv, a[1])), Lg)
            s = _math(nt, 'ADD', _math(nt, 'MULTIPLY', du, e[0]), _math(nt, 'MULTIPLY', dv, e[1]))
            sepn = _n(nt, 'ShaderNodeSeparateXYZ')
            L.new(geo.outputs['True Normal'], sepn.inputs[0])
            masc = _smooth(nt, _math(nt, 'ABSOLUTE', sepn.outputs['X']), 0.55, 0.75)
            masc = _math(nt, 'MULTIPLY', masc, _smooth(nt, t, 0.13, 0.16))
            masc = _math(nt, 'MULTIPLY', masc, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, t, 0.90, 0.93)))
            masc = _math(nt, 'MULTIPLY', masc, _smooth(nt, s, -0.0125, -0.0105))
            masc = _math(nt, 'MULTIPLY', masc, _math(nt, 'SUBTRACT', 1.0, _smooth(nt, s, 0.0115, 0.0135)))
            P_ = 0.0021
            x = _math(nt, 'DIVIDE', _math(nt, 'ADD', _math(nt, 'MULTIPLY', t, Lg), s), P_)
            y = _math(nt, 'DIVIDE', _math(nt, 'SUBTRACT', _math(nt, 'MULTIPLY', t, Lg), s), P_)
            fx = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', x), 0.5))
            fy = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', _math(nt, 'FRACT', y), 0.5))
            pir = _math(nt, 'SUBTRACT', 0.5, _math(nt, 'MAXIMUM', fx, fy))
            alt = _math(nt, 'ADD', alt, _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', pir, masc), 0.0011))
            topo = _math(nt, 'MULTIPLY', _smooth(nt, pir, 0.30, 0.45), masc)
            cor = _mix(nt, _math(nt, 'MULTIPLY', topo, 0.5), cor, cg)
            r = _mixf(nt, _math(nt, 'MULTIPLY', topo, 0.6), r, rg)
            fundo = _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, _smooth(nt, pir, 0.0, 0.2)), masc)
            S['ao_extra'] = _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', fundo, 0.45))
        if nome in RELEVO:               # relevo próprio da classe (outras armas): altura (m), topo e fundo (0..1)
            h, topo, fundo = RELEVO[nome](nt, pos, geo)
            alt = _math(nt, 'ADD', alt, h)
            cor = _mix(nt, _math(nt, 'MULTIPLY', topo, 0.5), cor, cg)
            r = _mixf(nt, _math(nt, 'MULTIPLY', topo, 0.6), r, rg)
            S['ao_extra'] = _math(nt, 'SUBTRACT', 1.0, _math(nt, 'MULTIPLY', fundo, 0.45))
        ao2 = _n(nt, 'ShaderNodeAmbientOcclusion', inside=False, only_local=True, samples=16)
        ao2.inputs['Distance'].default_value = 0.03
        ao = ao2.outputs['AO']
        if 'ao_extra' in S:
            ao = _math(nt, 'MULTIPLY', ao, S['ao_extra'])
        S.update(cor=cor, rug=r, met=mt, alt=alt, ao=ao)
    # nós de saída por passe
    em = _n(nt, 'ShaderNodeEmission')
    em.name = 'emissao'
    bs = _n(nt, 'ShaderNodeBsdfPrincipled')
    bs.name = 'bsdf'
    bev = _n(nt, 'ShaderNodeBevel', samples=6)
    bev.inputs['Radius'].default_value = 0.00045
    if S['alt'] is not None:
        bmp = _n(nt, 'ShaderNodeBump')
        bmp.inputs['Strength'].default_value = 1.0
        bmp.inputs['Distance'].default_value = 1.0
        L.new(S['alt'], bmp.inputs['Height'])
        L.new(bev.outputs[0], bmp.inputs['Normal'])
        L.new(bmp.outputs[0], bs.inputs['Normal'])
    else:
        L.new(bev.outputs[0], bs.inputs['Normal'])
    img = _n(nt, 'ShaderNodeTexImage')
    img.name = 'alvo'
    return S, em, bs, out, img


_INFO = {}


def preparar_materiais():
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


def desdobrar(objs, margem=0.003):
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
    import bmesh
    for o in objs:
        idx = [i for i, m in enumerate(o.data.materials) if m and m.name.startswith('tinta')]
        if not idx:
            continue
        bm = bmesh.from_edit_mesh(o.data)
        uv = bm.loops.layers.uv.verify()
        vistos = set()
        for f in bm.faces:
            if f.material_index not in idx or f in vistos:
                continue
            ilha, pilha = [], [f]
            vistos.add(f)
            while pilha:
                a = pilha.pop()
                ilha.append(a)
                for e in a.edges:
                    for b in e.link_faces:
                        if b not in vistos and b.material_index in idx:
                            vistos.add(b)
                            pilha.append(b)
            ls = [l for a in ilha for l in a.loops]
            cx = sum(l[uv].uv.x for l in ls) / len(ls)
            cy = sum(l[uv].uv.y for l in ls) / len(ls)
            for l in ls:
                l[uv].uv.x = cx + (l[uv].uv.x - cx) * 3.5
                l[uv].uv.y = cy + (l[uv].uv.y - cy) * 3.5
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
    sc.render.bake.margin = 6
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
    saida = {}
    for p in ('cor', 'rug', 'met', 'ao', 'normal'):
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
    Image.fromarray(u8(srgb(passes['cor']))).save(prefixo + '_cor.png')
    orm = np.stack([passes['ao'][..., 0], passes['rug'][..., 0], passes['met'][..., 0]], axis=-1)
    Image.fromarray(u8(orm)).save(prefixo + '_orm.png')
    Image.fromarray(u8(passes['normal'])).save(prefixo + '_normal.png')
