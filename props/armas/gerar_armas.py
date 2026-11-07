"""Gerador das ARMAS originais do Recomeco: armas em partes, encaixes de acessorios e animacoes glTF embutidas.

Uso:  python props/armas/gerar_armas.py               (gera tudo)
      python props/armas/gerar_armas.py pistola_9mm   (so os ids pedidos)

Saida:
  props/armas/armas/<id>.glb        a arma, com partes moveis, encaixes e animacoes
  props/armas/acessorios/<id>.glb   acessorios (pivo = ponto de encaixe)
  props/armas/municao/<id>.glb      municao, estojos e caixas
  props/armas/efeitos/<id>.glb      clarao de boca etc.
  props/armas/catalogo.json         dados de jogo de tudo     props/armas/CATALOGO.md (tabelas em portugues)

Convencoes (ver README.md):
  Y para cima, 1 unidade = 1 m. Arma em posicao de tiro: o cano aponta para -Z (a frente da camera no Godot), o lado direito e +X.
  Pivo (origem) = ponto da empunhadura, onde a mao fecha (centro do punho, na altura do dedo medio).
  Cada parte movel e um no com a origem no eixo/ponto de deslize; os encaixes sao nos vazios "encaixe_<tipo>" com a mesma orientacao
  da arma: um acessorio entra como filho do no de encaixe, com transformacao identidade.
  As animacoes (atirar, recarregar, ...) mexem so os nos da arma; maos e bracos ficam para os personagens.

Por dentro o modelo e desenhado num plano "de lado": x = para a frente (cano), y = para cima, z = para a direita da arma
(na exportacao gira 90 graus em Y: x -> -Z, z -> +X).
"""
import os, sys, math, json, struct, re
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..'))
import gerar_props as gp
from gerar_props import (P, torno, anel, cyl_eixo, varrer, circ, fofo, fonte, texto_c, mat_imagem, uv_cilindro, uv_atlas, uv_plano)
from detalhe import MATS, TEX, KIND, GT, tex_set, PBRMaterial, glb_jpeg, _fix
import numpy as np, trimesh
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union
from shapely import affinity

TF = trimesh.transformations

# ============================================================================ materiais das armas
CORES = {
    'aco_oxidado': (40, 42, 46), 'aco_fosfatado': (58, 60, 60), 'aco_inox': (178, 180, 184), 'aco_cano': (44, 46, 50),
    'polimero': (44, 44, 46), 'polimero_grip': (40, 40, 42), 'polimero_tan': (128, 104, 72),
    'aluminio_preto': (26, 26, 28), 'latao': (150, 112, 46), 'cobre_bala': (150, 76, 40), 'chumbo': (90, 92, 96),
    'tinta_branca': (230, 230, 224), 'tinta_laranja': (200, 80, 10), 'mola': (120, 122, 126),
    'borracha_grip': (28, 28, 28), 'borracha': (30, 30, 32), 'plastico_branco': (232, 232, 226), 'pet_azul': (90, 140, 180), 'fita_cinza': (150, 150, 146),
}
METAL = {'aco_oxidado': (0.75, 0.32), 'aco_fosfatado': (0.55, 0.62), 'aco_inox': (0.9, 0.22), 'aco_cano': (0.8, 0.3),
         'aluminio_preto': (0.55, 0.38), 'latao': (0.95, 0.28), 'cobre_bala': (0.95, 0.3), 'chumbo': (0.7, 0.5), 'mola': (0.9, 0.35),
         'polimero': (0.0, 0.55), 'polimero_tan': (0.0, 0.6), 'tinta_branca': (0.0, 0.4), 'tinta_laranja': (0.0, 0.45),
         'borracha_grip': (0.0, 0.9), 'fita_cinza': (0.3, 0.5), 'borracha': (0.0, 0.85), 'plastico_branco': (0.0, 0.5)}
TRANSP = {'lente': ((120, 160, 150), 0.35, 0.03), 'lente_laser': ((200, 30, 20), 0.6, 0.05), 'pet_garrafa': ((150, 190, 215), 0.22, 0.06)}
EMISSIVOS = {'ponto_vermelho': (1.0, 0.05, 0.02), 'led_lanterna': (1.0, 0.97, 0.88), 'led_laser': (1.0, 0.08, 0.04),
             'clarao': (1.0, 0.62, 0.22), 'clarao_nucleo': (1.0, 0.92, 0.7)}


def _tex_grip(seed, px=1024, tile=0.05):
    """Pontilhado do punho de polimero: picotes pequenos e irregulares (normal + rugosidade)."""
    n = int(tile * px); g = GT.noise(n, n, 0.0006 * px, 0.0006 * px, seed); f = GT.fbm(n, n, 0.003 * px, 3, seed + 3)
    pic = GT.smooth(0.3, 1.4, g)
    c = GT.rgb(CORES['polimero_grip'])[None, None]
    alb = c * (0.95 + 0.12 * pic[..., None] + 0.03 * f[..., None]); hm = 0.00025 * pic + 0.00005 * f
    return alb, hm, 0.75 + 0.15 * pic, 1.2, 0.0004, tile, px


def _tex_serrilha(seed, px=1024, tile=0.03):
    """Recartilhado em diamante (botoes, aneis de luneta, supressor)."""
    n = int(tile * px); yy, xx = np.mgrid[0:n, 0:n] / px; p = 0.0012
    d = np.minimum(np.abs(((xx + yy) / p) % 1 - 0.5), np.abs(((xx - yy) / p) % 1 - 0.5))
    hm = 0.00015 * GT.smooth(0.05, 0.3, d)
    alb = GT.rgb(CORES['aco_oxidado'])[None, None] * (0.9 + 0.2 * GT.smooth(0.05, 0.3, d)[..., None])
    return alb, hm, 0.4 + 0.2 * (1 - GT.smooth(0.05, 0.3, d)), 1.0, 0.0003, tile, px


def materiais():
    gp.CORES.update(CORES)
    gp.materiais()
    lin = lambda c: ((c / 255) / 12.92) if c <= 10 else (((c / 255) + 0.055) / 1.055) ** 2.4      # cores em sRGB -> fator linear do glTF
    for k, c in CORES.items(): MATS[k].baseColorFactor = [lin(x) for x in c] + [1.0]
    for k, (met, rough) in METAL.items(): MATS[k].metallicFactor = met; MATS[k].roughnessFactor = rough
    for i, (k, fn) in enumerate((('polimero_grip', _tex_grip), ('recartilhado', _tex_serrilha))):
        alb, hm, rough, nstr, aod, tile, px = fn(301 + i)
        a, nm, o = tex_set(alb, hm, rough, nstr, aod, px)
        TEX[k] = (a, nm, o); gp.UV_ESCALA[k] = tile
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0 if k == 'polimero_grip' else 0.7, roughnessFactor=1.0)
    for k, (c, alpha, rough) in TRANSP.items():
        MATS[k] = PBRMaterial(name=k, baseColorFactor=[c[0] / 255, c[1] / 255, c[2] / 255, alpha], alphaMode='BLEND',
                              metallicFactor=0.0, roughnessFactor=rough)
    for k, e in EMISSIVOS.items():
        MATS[k] = PBRMaterial(name=k, baseColorFactor=list(e) + [1.0], emissiveFactor=list(e), metallicFactor=0.0, roughnessFactor=0.4,
                              alphaMode='BLEND' if k.startswith('clarao') else None, doubleSided=k.startswith('clarao'))
        if k.startswith('clarao'): MATS[k].baseColorFactor = list(e) + [0.85]


# ============================================================================ geometria (plano de lado: x frente, y cima, z direita)
def ext(poly, z0, z1, ch=0.0):
    """Perfil lateral (x,y) extrudado em z de z0 a z1. ch > 0: arestas com chanfro (miolo encolhido em toda a espessura +
    perfil cheio recuado ch nas faces): le como bisel na luz e nao tem faces sobrepostas."""
    def pr(pl, a, b):
        ms = []
        for g in (pl.geoms if hasattr(pl, 'geoms') else [pl]):
            if g.area < 1e-9: continue
            m = trimesh.creation.extrude_polygon(g, b - a); m.apply_translation([0, 0, a]); ms.append(_fix(m))
        return ms
    if ch <= 0: return pr(poly, z0, z1)
    ch = min(ch, (z1 - z0) / 3)
    return pr(poly.buffer(-ch, join_style=2), z0, z1) + pr(poly, z0 + ch, z1 - ch)


def solido(poly, z0, z1, ch=0.0):
    """Igual a ext, mas devolve UM solido estanque (para booleanos)."""
    ms = ext(poly, z0, z1, ch)
    return ms[0] if len(ms) == 1 else trimesh.boolean.union(ms, engine='manifold')


def ext_x(poly_zy, x0, x1):
    """Secao (z,y) extrudada ao longo de x (trilhos, cortes de secao)."""
    m = trimesh.creation.extrude_polygon(poly_zy, x1 - x0)
    v = m.vertices.copy(); m.vertices = np.stack([x0 + v[:, 2], v[:, 1], v[:, 0]], 1)
    return _fix(m)


def ext_y(poly_xz, y0, y1):
    """Planta (x,z) extrudada em y."""
    m = trimesh.creation.extrude_polygon(poly_xz, y1 - y0)
    v = m.vertices.copy(); m.vertices = np.stack([v[:, 0], y0 + v[:, 2], v[:, 1]], 1)
    return _fix(m)


def caixa(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0]); b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return b


def cil_x(r, x0, x1, y=0.0, z=0.0, sec=24):
    m = trimesh.creation.cylinder(radius=r, height=x1 - x0, sections=sec)
    m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([(x0 + x1) / 2, y, z]); return m


def cil_z(r, z0, z1, x=0.0, y=0.0, sec=16):
    m = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sec); m.apply_translation([x, y, (z0 + z1) / 2]); return m


def menos(a, *bs):
    bs = [b for b in bs if b is not None]
    return trimesh.boolean.difference([a] + bs, engine='manifold') if bs else a


def uniao(ms): return trimesh.boolean.union(ms, engine='manifold')


def inter(ms): return trimesh.boolean.intersection(ms, engine='manifold')


def arred(pts, r=0.002, n=4):
    """Poligono com cantos arredondados (buffer para fora e para dentro)."""
    return Polygon(pts).buffer(-r, join_style=1, resolution=n).buffer(r, join_style=1, resolution=n)


def torno_x(perfil, sec=32, y=0.0, z=0.0, x0=0.0):
    """Solido de revolucao ao longo de x: perfil [(raio, x), ...]."""
    pts = list(perfil)
    if pts[0][0] > 0: pts = [(0.0, pts[0][1])] + pts
    if pts[-1][0] > 0: pts = pts + [(0.0, pts[-1][1])]
    m = trimesh.creation.revolve(np.array(pts, float), sections=sec)
    if m.volume < 0: m.invert()
    m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([x0, y, z]); return m


def tubo_x(r0, r1, x0, x1, y=0.0, z=0.0, sec=32, ch=0.0):
    ch = min(ch, (r1 - r0) / 3, (x1 - x0) / 3)
    pts = [(r0, x0), (r1 - ch, x0), (r1, x0 + ch), (r1, x1 - ch), (r1 - ch, x1), (r0, x1)]
    m = trimesh.creation.revolve(np.array(pts + [pts[0]], float), sections=sec)
    if m.volume < 0: m.invert()
    m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([0, y, z]); return m


def rosca_x(p, mat, r, x0, x1, passo=0.001, y=0.0, z=0.0):
    """Rosca: aneis triangulares em serie (le como fio de rosca)."""
    x = x0
    while x + passo <= x1 + 1e-9:
        p.add(mat, torno_x([(r * 0.9, x), (r, x + passo / 2), (r * 0.9, x + passo)], 24, y, z)); x += passo


def parafuso_z(p, mat, x, y, z, r=0.0018, lado=1, fenda=True):
    """Cabeca de pino/parafuso na face lateral (lado +1 direita, -1 esquerda)."""
    m = trimesh.creation.cylinder(radius=r, height=0.0008, sections=12); m.apply_translation([x, y, z + lado * 0.0004]); p.add(mat, m)


def trilho(p, mat, x0, x1, y_base, para_baixo=True, larg=0.021, passo=0.01):
    """Trilho padrao do Recomeco (21 mm, fendas a cada 10 mm), ao longo de x. para_baixo: trilho embaixo do guarda-mao."""
    s = -1 if para_baixo else 1; h1 = 0.003; h2 = 0.0055; w2 = larg / 2; w1 = w2 - 0.003
    sec = Polygon([(-w1, 0), (w1, 0), (w1, h1 * 0.5), (w2, h1), (w2, h2 - 0.001), (w2 - 0.001, h2), (-w2 + 0.001, h2), (-w2, h2 - 0.001),
                   (-w2, h1), (-w1, h1 * 0.5)])
    if s < 0: sec = affinity.scale(sec, 1, -1, origin=(0, 0))
    sec = affinity.translate(sec, 0, y_base)
    corpo = ext_x(sec, x0, x1)
    cortes = []
    n = int((x1 - x0 - 0.004) / passo)
    xa = (x0 + x1) / 2 - (n - 1) * passo / 2
    for i in range(n):
        xc = xa + i * passo
        cortes.append(caixa(xc - 0.00265, xc + 0.00265, y_base + s * 0.0028 - 0.004, y_base + s * 0.0028 + 0.004, -0.02, 0.02)
                      if True else None)
    cortes = [inter([c, caixa(x0 - 1, x1 + 1, min(y_base + s * 0.0029, y_base + s * 0.007), max(y_base + s * 0.0029, y_base + s * 0.007), -1, 1)]) for c in cortes]
    p.add(mat, menos(corpo, *cortes))
    return n


# ============================================================================ registro
REG = {}
def arma(id, nome, grupo, categoria, **dados):
    def deco(fn): REG[id] = dict(id=id, nome=nome, grupo=grupo, categoria=categoria, fn=fn, **dados); return fn
    return deco


class Arma:
    """Base fixa + partes moveis + encaixes + animacoes, tudo no plano de lado. pivo = ponto da empunhadura."""
    def __init__(s):
        s.base = P(); s.partes = []; s.encaixes = []; s.anims = {}; s.pivo = (0, 0, 0)
    def parte(s, no, origem, pai=None, **info):
        q = P(); s.partes.append(dict(no=no, origem=list(origem), pai=pai, peca=q, **info)); return q
    def encaixe(s, no, pos, tipo, pai=None, **info):
        s.encaixes.append(dict(no=no, pos=list(pos), tipo=tipo, pai=pai, **info))
    def anim(s, nome, dur, faixas, laco=False, desc=''):
        """faixas: (no, 't', [(tempo, (dx,dy,dz)), ...]) deslocamento no plano de lado;
                   (no, 'r', eixo, [(tempo, graus), ...]) giro em torno do eixo (plano de lado);  no = None -> raiz."""
        s.anims[nome] = dict(dur=dur, faixas=faixas, laco=laco, desc=desc)


R_LADO = TF.rotation_matrix(math.pi / 2, [0, 1, 0])      # plano de lado -> arma: x -> -Z, z -> +X
def rot(v): return (R_LADO[:3, :3] @ np.array(v, float))


def exportar(it, raiz):
    A = Arma(); it['fn'](A)
    nome = it['id']; pv = np.array(A.pivo, float)
    F = TF.translation_matrix(-rot(pv)) @ R_LADO          # plano de lado -> coordenadas finais da arma
    sc = trimesh.Scene(); base = sc.graph.base_frame
    sc.graph.update(frame_from=base, frame_to=nome, matrix=np.eye(4))
    pos_w = {nome: np.zeros(3)}

    def coloca(piece, prefixo, pai, origem_w):
        T = TF.translation_matrix(-origem_w) @ F
        q = P(); q.uv = {}
        for k, ms in piece.parts.items():
            for m in ms: mm = m.copy(); mm.apply_transform(T); q.add(k, mm)
        for k, f in piece.uv.items(): q.uv[k] = (lambda f, Ti: (lambda v, n: f(trimesh.transform_points(v, Ti), (Ti[:3, :3] @ n.T).T)))(f, np.linalg.inv(T))
        for gname, g in q.scene(prefixo).geometry.items():
            sc.add_geometry(g, node_name=gname, geom_name=gname, parent_node_name=pai)

    coloca(A.base, nome, nome, np.zeros(3))
    for pt in A.partes:                                          # pais antes dos filhos (ordem de declaracao)
        pai = pt['pai'] or nome; ow = trimesh.transform_points([pt['origem']], F)[0]
        sc.graph.update(frame_from=pai, frame_to=pt['no'], matrix=TF.translation_matrix(ow - pos_w[pai])); pos_w[pt['no']] = ow
        coloca(pt['peca'], f"{nome}_{pt['no']}", pt['no'], ow)
    for e in A.encaixes:
        pai = e['pai'] or nome; ow = trimesh.transform_points([e['pos']], F)[0]
        sc.graph.update(frame_from=pai, frame_to=e['no'], matrix=TF.translation_matrix(ow - pos_w[pai])); pos_w[e['no']] = ow
    pasta = os.path.join(raiz, it['grupo']); os.makedirs(pasta, exist_ok=True)
    arq = os.path.join(pasta, f'{nome}.glb'); sc.export(arq)
    anims = animar(arq, A, nome, pos_w); glb_jpeg(arq)
    b = sc.bounds; tris = sum(len(g.faces) for g in sc.geometry.values())
    reg = {k: v for k, v in it.items() if k != 'fn'}
    reg.update(arquivo=f"{it['grupo']}/{nome}.glb", tamanho_m=[round(float(x), 3) for x in (b[1] - b[0])], triangulos=int(tris),
               kb=round(os.path.getsize(arq) / 1024, 1))
    if A.partes: reg['partes'] = [{k: (v if k != 'origem' else None) for k, v in p.items() if k not in ('peca', 'origem', 'pai')} | {'pai': p['pai'] or nome} for p in A.partes]
    if A.encaixes:
        reg['encaixes'] = [{'no': e['no'], 'tipo': e['tipo'], 'pai': e['pai'] or nome, 'posicao_m': [round(float(c), 4) for c in pos_w[e['no']]],
                            **{k: v for k, v in e.items() if k not in ('no', 'tipo', 'pai', 'pos')}} for e in A.encaixes]
    if anims: reg['animacoes'] = anims
    return reg


# ---------------------------------------------------------------------------- animacoes glTF (pos-processa o GLB do trimesh)
def _qeixo(eixo, graus):
    a = rot(eixo); a = a / np.linalg.norm(a); h = math.radians(graus) / 2
    return [float(a[0] * math.sin(h)), float(a[1] * math.sin(h)), float(a[2] * math.sin(h)), float(math.cos(h))]


def animar(arq, A, nome, pos_w):
    """Converte as matrizes dos nos em TRS e grava as animacoes de A (canais translation/rotation)."""
    data = open(arq, 'rb').read(); off = 12; ch = []
    while off < len(data):
        ln, ty = struct.unpack('<II', data[off:off + 8]); ch.append([ty, data[off + 8:off + 8 + ln]]); off += 8 + ln
    js = json.loads(ch[0][1]); binb = bytearray(ch[1][1])
    for n in js['nodes']:
        if 'matrix' in n:
            M = np.array(n.pop('matrix')).reshape(4, 4).T
            t = M[:3, 3]
            if np.linalg.norm(t) > 0: n['translation'] = [float(c) for c in t]
            if not np.allclose(M[:3, :3], np.eye(3)): raise ValueError('no com rotacao inesperada')
    idx = {n.get('name'): i for i, n in enumerate(js['nodes'])}
    rest = {k: np.array(js['nodes'][i].get('translation', [0, 0, 0]), float) for k, i in idx.items()}
    js.setdefault('animations', []); acc = js['accessors']; bvs = js['bufferViews']; resumo = {}

    def put(arr, tipo):
        nonlocal binb
        while len(binb) % 4: binb.append(0)
        a = np.asarray(arr, np.float32); o = len(binb); binb += a.tobytes()
        bvs.append({'buffer': 0, 'byteOffset': o, 'byteLength': a.nbytes})
        d = {'bufferView': len(bvs) - 1, 'componentType': 5126, 'count': int(a.shape[0]), 'type': tipo}
        if tipo == 'SCALAR': d['min'] = [float(a.min())]; d['max'] = [float(a.max())]
        acc.append(d); return len(acc) - 1

    def qmul(a, b):
        x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
        return [w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2, w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2, w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2]

    for an, spec in A.anims.items():
        samplers = []; channels = []; grupos = {}
        for f in spec['faixas']:                                   # junta as faixas do mesmo no e do mesmo canal
            grupos.setdefault((f[0] or nome, f[1]), []).append(f)
        for (no, tp), fs in grupos.items():
            ts = sorted({k[0] for f in fs for k in (f[2] if tp == 't' else f[3])})
            if tp == 't':
                vals = []
                for t in ts:
                    v = np.zeros(3)
                    for f in fs: ks = f[2]; v += np.array([np.interp(t, [k[0] for k in ks], [k[1][i] for k in ks]) for i in range(3)])
                    vals.append(rest[no] + rot(v))
                path = 'translation'; tipo = 'VEC3'
            else:
                vals = []
                for t in ts:
                    q = [0, 0, 0, 1]
                    for f in fs: ks = f[3]; q = qmul(q, _qeixo(f[2], float(np.interp(t, [k[0] for k in ks], [k[1] for k in ks]))))
                    vals.append(q)
                path = 'rotation'; tipo = 'VEC4'
            tin = put(ts, 'SCALAR'); tout = put(vals, tipo)
            samplers.append({'input': tin, 'output': tout, 'interpolation': 'LINEAR'})
            channels.append({'sampler': len(samplers) - 1, 'target': {'node': idx[no], 'path': path}})
        js['animations'].append({'name': an, 'samplers': samplers, 'channels': channels})
        resumo[an] = {'duracao_s': spec['dur'], 'laco': spec['laco'], 'descricao': spec['desc']}
    if not js['animations']: js.pop('animations')
    js['buffers'] = [{'byteLength': len(binb)}]
    while len(binb) % 4: binb.append(0)
    js['buffers'][0]['byteLength'] = len(binb)
    j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((-len(j)) % 4)
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(binb)) + struct.pack('<II', len(j), 0x4E4F534A) + j + struct.pack('<II', len(binb), 0x004E4942) + bytes(binb)
    open(arq, 'wb').write(out)
    return resumo


def pose(ks):
    """Atalho: lista de (tempo, valor) a partir de pares."""
    return [(float(t), v) for t, v in ks]


# ============================================================================ ARMAS
# ---------------------------------------------------------------------------- pistola 9 mm
SL_Y0, SL_Y1, SL_W = -0.0135, 0.0175, 0.0125     # ferrolho: base, topo, meia largura
SL_L = 0.186
MAG_D = np.array([-math.sin(math.radians(17)), -math.cos(math.radians(17)), 0.0])   # eixo do carregador (desce e vai para tras)


def _ferrolho_pistola(q):
    lado = Polygon([(0, SL_Y0), (SL_L, SL_Y0), (SL_L, SL_Y1 - 0.007), (SL_L - 0.009, SL_Y1), (0.003, SL_Y1), (0, SL_Y1 - 0.003)])
    # planta com serrilhas atras (e na frente) e ponta afinada
    planta = Polygon([(0, -SL_W), (SL_L - 0.025, -SL_W), (SL_L, -SL_W + 0.0015), (SL_L, SL_W - 0.0015), (SL_L - 0.025, SL_W), (0, SL_W)])
    secao = Polygon([(-SL_W, SL_Y0), (SL_W, SL_Y0), (SL_W, SL_Y1 - 0.0045), (SL_W - 0.0035, SL_Y1), (-SL_W + 0.0035, SL_Y1), (-SL_W, SL_Y1 - 0.0045)])
    corpo = inter([solido(lado, -SL_W, SL_W), ext_y(planta, SL_Y0 - 0.01, SL_Y1 + 0.01), ext_x(secao, -0.01, SL_L + 0.01)])
    cortes = []
    for xs, n in ((0.012, 9), (0.142, 6)):                      # serrilhas: ranhuras inclinadas nas duas faces
        for i in range(n):
            x = xs + i * 0.0032
            for zs in (-1, 1):
                g = caixa(-0.0006, 0.0006, -0.02, 0.02, -0.001, 0.001)
                g.apply_transform(TF.rotation_matrix(math.radians(-8), [0, 0, 1])); g.apply_translation([x, SL_Y0 + 0.003 + 0.02, zs * SL_W])
                cortes.append(inter([g, caixa(x - 0.01, x + 0.01, SL_Y0 + 0.003, SL_Y1 - 0.0045, -1, 1)]))
    cortes.append(caixa(0.072, 0.112, -0.002, 0.03, 0.0, 0.03))  # janela de ejecao (lado direito)
    cortes.append(cil_x(0.0068, SL_L - 0.004, SL_L + 0.01))      # boca do ferrolho (o cano aparece)
    cortes.append(caixa(0.026, 0.058, SL_Y1 - 0.0022, SL_Y1 + 0.01, -0.0105, 0.0105))   # rebaixo para mira de ferrolho
    cortes.append(caixa(-0.01, 0.006, -0.004, 0.004, -0.003, 0.003))  # furo do percussor (traseira)
    q.add('aco_oxidado', menos(corpo, *cortes))
    q.cham('aco_oxidado', 0.0275, 0.0565, SL_Y1 - 0.0021, SL_Y1 - 0.0004, -0.0098, 0.0098, 0.0005)  # tampa do rebaixo
    for x in (0.031, 0.053): q.add('aco_inox', cil_z(0.0009, -0.0001, 0.0001, x, SL_Y1 - 0.0004).apply_transform(np.eye(4)))
    for x in (0.031, 0.053):
        m = trimesh.creation.cylinder(radius=0.0011, height=0.0006, sections=10); m.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0]))
        m.apply_translation([x, SL_Y1 - 0.0001, 0]); q.add('aco_inox', m)            # parafusos da tampa
    # mira traseira (cauda de andorinha) com dois pontos brancos
    alca = arred([(0.004, SL_Y1 - 0.001), (0.018, SL_Y1 - 0.001), (0.018, SL_Y1 + 0.0055), (0.008, SL_Y1 + 0.0062), (0.004, SL_Y1 + 0.004)], 0.0008)
    m = solido(alca, -0.0105, 0.0105, 0.0008); m = menos(m, caixa(0.0, 0.03, SL_Y1 + 0.002, SL_Y1 + 0.01, -0.0016, 0.0016))
    q.add('aco_oxidado', m)
    for z in (-0.0042, 0.0042):
        d = trimesh.creation.cylinder(radius=0.0011, height=0.0006, sections=12); d.apply_transform(TF.rotation_matrix(-math.pi / 2, [0, 1, 0]))
        d.apply_translation([0.0178, SL_Y1 + 0.0037, z]); q.add('tinta_branca', d)
    # massa de mira frontal com ponto
    mas = arred([(0.168, SL_Y1 - 0.001), (0.18, SL_Y1 - 0.001), (0.179, SL_Y1 + 0.0058), (0.171, SL_Y1 + 0.0058)], 0.0006)
    q.add('aco_oxidado', solido(mas, -0.0016, 0.0016, 0.0004))
    d = trimesh.creation.cylinder(radius=0.0011, height=0.0006, sections=12); d.apply_transform(TF.rotation_matrix(-math.pi / 2, [0, 1, 0]))
    d.apply_translation([0.1681, SL_Y1 + 0.0037, 0]); q.add('tinta_branca', d)
    # extrator (lado direito) e marcacoes
    q.add('aco_inox', solido(arred([(0.06, 0.004), (0.071, 0.004), (0.071, 0.0085), (0.06, 0.0085)], 0.0006), SL_W - 0.0003, SL_W + 0.0004, 0.0002))
    q.add('aco_inox', torno_x([(0.0024, -0.0004), (0.0024, 0.0002), (0.0018, 0.0008)], 16, 0.0, 0.0, -0.0004))   # tampa do percussor


def _armacao_pistola(p):
    # perfil lateral da armacao (polimero): trilho do guarda-po, guarda-mato, punho inclinado com apoio do polegar
    out = [(-0.003, SL_Y0 + 0.0005), (-0.016, -0.0175), (-0.019, -0.024), (-0.012, -0.031), (-0.018, -0.05), (-0.027, -0.085),
           (-0.033, -0.112), (-0.034, -0.119), (-0.028, -0.123), (0.019, -0.123), (0.024, -0.118), (0.025, -0.11), (0.03, -0.1),
           (0.029, -0.093), (0.034, -0.083), (0.033, -0.076), (0.039, -0.066), (0.038, -0.058), (0.044, -0.047), (0.047, -0.043),
           (0.062, -0.049), (0.086, -0.0505), (0.094, -0.047), (0.097, -0.04), (0.097, -0.032), (0.102, -0.03), (0.18, -0.03),
           (0.183, -0.027), (0.183, SL_Y0 + 0.0005)]
    perfil = arred(out, 0.0016)
    guarda = arred([(0.05, -0.043), (0.086, -0.0455), (0.092, -0.041), (0.092, -0.031), (0.088, -0.026), (0.052, -0.026), (0.046, -0.034)], 0.003)
    perfil = perfil.difference(guarda)
    punho = perfil.intersection(sbox(-0.05, -0.13, 0.06, -0.029))
    alto = perfil.difference(sbox(-0.05, -0.13, 0.06, -0.0295)).union(perfil.intersection(sbox(0.045, -0.06, 0.2, 0)))
    m_alto = solido(alto, -0.0112, 0.0112, 0.0012)
    m_punho = solido(punho.buffer(0), -0.0148, 0.0148, 0.0042)
    corpo = uniao([m_alto, m_punho])
    # poco do carregador: prisma inclinado vazado por baixo (folga de 0,8 mm do carregador)
    poco = _perfil_carregador(0.0008)
    corpo = menos(corpo, solido(poco, -0.0096, 0.0096))
    corpo = menos(corpo, caixa(0.06, 0.082, -0.03, -0.012, -0.0045, 0.0045))   # fenda do gatilho
    p.add('polimero', corpo)
    # paineis pontilhados (laterais, frente e costas do punho), 0,4 mm salientes
    painel = arred([(-0.012, -0.04), (0.036, -0.054), (0.03, -0.074), (0.026, -0.1), (0.019, -0.114), (-0.026, -0.114),
                    (-0.024, -0.092), (-0.017, -0.06)], 0.004)
    for zs in (-1, 1):
        z0 = zs * 0.0148; p.add('polimero_grip', solido(painel, min(z0, z0 + zs * 0.0005), max(z0, z0 + zs * 0.0005), 0.0002))
    # trilho padrao embaixo do guarda-po
    trilho(p, 'polimero', 0.105, 0.177, -0.03, True, 0.019)
    # alavanca do retem do ferrolho (esquerda), botao do retem do carregador, alavanca de desmontagem, pinos
    ret = arred([(0.03, -0.014), (0.07, -0.014), (0.074, -0.0115), (0.07, -0.009), (0.046, -0.009), (0.038, -0.006), (0.03, -0.007)], 0.0008)
    p.add('aco_oxidado', solido(ret, -0.0124, -0.0112, 0.0004))
    for x in np.linspace(0.033, 0.041, 4):
        p.add('aco_oxidado', caixa(x - 0.0004, x + 0.0004, -0.0085, -0.0058, -0.0126, -0.0122))
    p.add('recartilhado', torno_x([(0.0038, 0), (0.0039, 0.0008), (0.0036, 0.0016)], 20).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])).apply_translation([0.046, -0.037, -0.0113]))
    lev = arred([(0.083, -0.021), (0.095, -0.021), (0.095, -0.017), (0.083, -0.017)], 0.0012)
    for zs in (-1, 1): p.add('aco_oxidado', solido(lev, min(zs * 0.0112, zs * 0.0122), max(zs * 0.0112, zs * 0.0122), 0.0003))
    for (x, y) in ((0.072, -0.022), (0.052, -0.02), (-0.006, -0.022)):
        for zs in (-1, 1): p.add('aco_inox', cil_z(0.0014, min(zs * 0.0111, zs * 0.0118), max(zs * 0.0111, zs * 0.0118), x, y, 12))
    # pega do cordao na base e numero de serie gravado (placa)
    p.add('aco_oxidado', caixa(0.12, 0.135, -0.0262, -0.0255, 0.0111, 0.0114))


def _perfil_carregador(folga=0.0):
    """Perfil lateral do corpo do carregador (inclinado como o punho), do topo (y = -0.016) ate a base."""
    d = MAG_D[:2]; topo = np.array([0.0215, -0.016]); L = 0.106
    n = np.array([-d[1], d[0]])                                   # normal (frente)
    a = topo - n * 0.0145; b = topo + n * 0.0145
    pts = [a, b, b + d * L, a + d * L]
    return Polygon([tuple(x) for x in pts]).buffer(folga, join_style=2)


def _carregador(q, cap=15, extra=0.0, nome_base='polimero'):
    """Carregador de pistola: corpo de aco com furos de contagem, base de polimero, cartucho no topo. extra = alongamento."""
    d = MAG_D[:2]; perfil = _perfil_carregador()
    if extra: perfil = perfil.union(affinity.translate(perfil, *(d * extra)))
    hw = 0.0088
    corpo = solido(perfil, -hw, hw, 0.0012)
    furos = []
    topo = np.array([0.0215, -0.016]); n = np.array([-d[1], d[0]])
    for i in range(int(cap / 3) + 1):                               # furos de contagem atras
        c = topo - n * 0.0118 + d * (0.02 + i * 0.012)
        furos.append(cil_z(0.0012, -0.02, 0.0, c[0], c[1], 10))
    corpo = menos(corpo, *furos)
    q.add('aco_oxidado', corpo)
    for i in range(int(cap / 3) + 1):                               # numeros: sulcos pequenos marcados com tinta branca
        c = topo - n * 0.0118 + d * (0.02 + i * 0.012) + n * 0.004
        q.add('tinta_branca', caixa(c[0] - 0.0012, c[0] + 0.0012, c[1] - 0.0004, c[1] + 0.0004, -hw - 0.00015, -hw + 0.0001))
    # base (polimero) com apoio para extracao
    L = 0.106 + extra; b0 = topo + d * L
    base = arred([tuple(b0 - n * 0.0168 - d * 0.001), tuple(b0 + n * 0.0185 - d * 0.001), tuple(b0 + n * 0.0192 + d * 0.0055),
                  tuple(b0 + n * 0.0185 + d * 0.0085), tuple(b0 - n * 0.0172 + d * 0.0085)], 0.0015)
    q.add(nome_base, solido(base, -0.0128, 0.0128, 0.0025))
    # labios e cartucho de cima
    xc = topo[0] + 0.002; yc = topo[1] + 0.0022
    cart = _cartucho_9mm_malha()
    q.merge(cart, TF.translation_matrix([xc - 0.009, yc + 0.0028, 0]) @ TF.rotation_matrix(math.radians(-3), [0, 0, 1]))
    for zs in (-1, 1): q.add('aco_oxidado', caixa(topo[0] - 0.012, topo[0] + 0.006, topo[1] - 0.001, topo[1] + 0.0034, zs * 0.0045 - 0.0012, zs * 0.0045 + 0.0012))


def _cartucho_9mm_malha(sec=28):
    """Cartucho 9 mm deitado ao longo de x (base em x=0): estojo de latao com virola + projetil de cobre."""
    q = P()
    q.add('latao', torno_x([(0.0, 0.0), (0.0049, 0.0), (0.005, 0.0012), (0.0042, 0.0016), (0.0042, 0.0024), (0.00495, 0.003),
                             (0.00482, 0.019), (0.0, 0.019)], sec))
    q.add('cobre_bala', torno_x([(0.0045, 0.0185), (0.00452, 0.022), (0.0042, 0.025), (0.0031, 0.0278), (0.0014, 0.0292), (0.0, 0.0294)], sec))
    q.add('aco_inox', torno_x([(0.0, -0.00005), (0.0021, -0.00005), (0.0021, 0.0004)], max(8, sec // 2)))     # espoleta
    return q


def _gatilho_pistola(q):
    """Gatilho curvo com tecla de seguranca, origem no pino (0.071, -0.0215)."""
    cam = [(0.071 + 0.004 * math.sin(a) - 0.006 * (1 - math.cos(a)) * 0, -0.0215 - 0.019 * a / 1.1, 0) for a in np.linspace(0, 1.1, 2)]
    lam = arred([(0.0655, -0.022), (0.0705, -0.022), (0.0718, -0.028), (0.0705, -0.036), (0.068, -0.041), (0.0655, -0.0425),
                 (0.0638, -0.041), (0.0652, -0.036), (0.066, -0.029)], 0.0007)
    q.add('polimero', solido(lam, -0.0035, 0.0035, 0.0008))
    q.add('aco_oxidado', solido(arred([(0.0668, -0.027), (0.0706, -0.027), (0.0695, -0.037), (0.0668, -0.0385), (0.0662, -0.033)], 0.0005), -0.0009, 0.0009))


@arma('pistola_9mm', 'Pistola Sentinela 9 mm', 'armas', 'pistola', classe='fogo', calibre='9 mm', municao='municao_9mm',
      capacidade=15, dano=34, alcance_m=25, alcance_max_m=50, modo='semiautomático', tiros_por_s=4.0, recarga_s=1.6, recarga_vazia_s=2.1,
      precisao=0.72, recuo=0.3, ruido_m=60, durabilidade=600, peso_kg=0.78, raridade='incomum', valor_troca=40,
      onde=['quartel', 'correios', 'motel', 'posto', 'casas'],
      descricao='Pistola de polímero com ferrolho de aço, 15 tiros. Leve e confiável, mas o tiro chama zumbis num raio de 60 m.')
def pistola_9mm(A):
    A.pivo = (0.006, -0.068, 0.0)            # centro do punho, na altura do dedo medio
    _armacao_pistola(A.base)
    gat = A.parte('gatilho', (0.071, -0.0215, 0), tipo='gira', eixo='x', curso_graus=-14, descricao='puxa para tras ao atirar')
    _gatilho_pistola(gat)
    cano = A.parte('cano', (0.0, 0.0, 0.0), tipo='desliza', curso_m=0.004, descricao='recua 4 mm com o ferrolho')
    cano.add('aco_cano', menos(uniao([cil_x(0.0068, 0.04, SL_L + 0.0002, sec=32), caixa(0.07, 0.112, -0.0068, 0.0098, -0.0085, 0.0085)]),
                                cil_x(0.0045, 0.03, SL_L + 0.01, sec=24)))
    rosca_x(cano, 'aco_cano', 0.0068, SL_L + 0.0002, SL_L + 0.0122, 0.001)
    cano.add('aco_cano', tubo_x(0.0045, 0.0064, SL_L + 0.0122, SL_L + 0.0132, sec=32))
    cano.add('aco_oxidado', solido(arred([(0.072, 0.0099), (0.11, 0.0099), (0.11, 0.0102), (0.072, 0.0102)], 0.0001), -0.008, 0.008))
    for i, ch in enumerate('9MM'):
        cano.add('aco_inox', caixa(0.08 + i * 0.006, 0.084 + i * 0.006, 0.0099, 0.0104, 0.0086, 0.00875))
    cano.add('latao', torno_x([(0.0045, 0.06), (0.0045, 0.0715)], 24))      # culote do cartucho na camara (aparece pela janela)
    fer = A.parte('ferrolho', (0.0, 0.0, 0.0), tipo='desliza', curso_m=0.032, descricao='recua 32 mm ao atirar; fica travado atrás com o carregador vazio')
    _ferrolho_pistola(fer)
    car = A.parte('carregador', (0.0215, -0.016, 0.0), tipo='remove', direcao=[round(float(c), 3) for c in rot(MAG_D)],
                  municao='municao_9mm', capacidade=15, descricao='sai pelo fundo do punho ao recarregar')
    _carregador(car, 15)
    A.encaixe('encaixe_mira', (0.042, SL_Y1 - 0.0004, 0), 'mira_ferrolho', pai='ferrolho', aceita=['mira_ponto_vermelho_compacta'])
    A.encaixe('encaixe_boca', (SL_L + 0.0122, 0, 0), 'boca_rosca_9mm', pai='cano',
              aceita=['protetor_rosca_9mm', 'supressor_9mm', 'compensador_9mm', 'supressor_garrafa'], padrao='protetor_rosca_9mm')
    A.encaixe('encaixe_trilho', (0.141, -0.0355, 0), 'trilho_curto', aceita=['lanterna_pistola', 'laser_pistola', 'combo_lanterna_laser'])
    A.encaixe('encaixe_carregador', (0.0215, -0.016, 0), 'carregador_9mm', pai='carregador', substitui='carregador',
              aceita=['carregador_9mm', 'carregador_9mm_estendido'],
              descricao='filho do nó carregador (anda com a recarga); ao pôr um carregador aqui, esconda as malhas próprias do nó carregador')
    A.encaixe('saida_estojo', (0.092, 0.012, 0.012), 'efeito', descricao='onde nasce o estojo ejetado (vai para +X e para cima)')
    A.encaixe('boca_fogo', (SL_L + 0.0132, 0, 0), 'efeito', pai='cano', descricao='clarão de boca e origem do disparo (raycast para -Z)')
    A.encaixe('mira_ferro', (0.011, SL_Y1 + 0.004, 0), 'mira', pai='ferrolho', descricao='linha de visada: alça -> massa')
    # animacoes (tempos em s, deslocamentos no plano de lado: x = frente)
    A.anim('atirar', 0.14, [
        ('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.02, -14), (0.06, -14), (0.12, 0)])),
        ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.02, (0, 0, 0)), (0.045, (-0.032, 0, 0)), (0.1, (0, 0, 0))])),
        ('cano', 't', pose([(0, (0, 0, 0)), (0.02, (0, 0, 0)), (0.03, (-0.004, -0.0005, 0)), (0.09, (-0.004, -0.0005, 0)), (0.1, (0, 0, 0))])),
        ('cano', 'r', (0, 0, 1), pose([(0, 0), (0.03, 0), (0.045, 1.2), (0.085, 1.2), (0.1, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.025, 0), (0.05, 7), (0.14, 0)])),
        (None, 't', pose([(0, (0, 0, 0)), (0.025, (0, 0, 0)), (0.05, (-0.012, 0.004, 0)), (0.14, (0, 0, 0))]))],
        desc='um disparo: gatilho, recuo do ferrolho e do cano, coice da arma (soltar estojo em saida_estojo aos 0,04 s)')
    A.anim('atirar_ultimo', 0.14, [
        ('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.02, -14), (0.06, -14), (0.12, 0)])),
        ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.02, (0, 0, 0)), (0.045, (-0.032, 0, 0)), (0.07, (-0.029, 0, 0)), (0.14, (-0.029, 0, 0))])),
        ('cano', 't', pose([(0, (0, 0, 0)), (0.03, (-0.004, -0.0005, 0)), (0.14, (-0.004, -0.0005, 0))])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.025, 0), (0.05, 7), (0.14, 0)]))],
        desc='último tiro: o ferrolho fica travado atrás')
    A.anim('vazia', 0.1, [('ferrolho', 't', pose([(0, (-0.029, 0, 0)), (0.1, (-0.029, 0, 0))])),
                          ('cano', 't', pose([(0, (-0.004, -0.0005, 0)), (0.1, (-0.004, -0.0005, 0))]))], laco=True,
           desc='pose parada: ferrolho travado atrás, carregador vazio')
    dm = MAG_D * 0.17
    A.anim('recarregar', 1.6, [
        ('carregador', 't', pose([(0, (0, 0, 0)), (0.15, (0, 0, 0)), (0.3, tuple(MAG_D * 0.02)), (0.5, tuple(dm)), (0.9, tuple(dm)),
                                  (1.15, tuple(MAG_D * 0.01)), (1.22, (0, 0, 0))])),
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, -18), (1.3, -18), (1.6, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 10), (1.3, 10), (1.6, 0)]))],
        desc='troca tática: solta o carregador (0,3 s), carregador novo entra (1,2 s); trocar o nó carregador entre 0,5 e 0,9 s')
    A.anim('recarregar_vazia', 2.1, [
        ('ferrolho', 't', pose([(0, (-0.029, 0, 0)), (1.45, (-0.029, 0, 0)), (1.5, (-0.032, 0, 0)), (1.58, (0, 0, 0))])),
        ('cano', 't', pose([(0, (-0.004, -0.0005, 0)), (1.5, (-0.004, -0.0005, 0)), (1.58, (0, 0, 0))])),
        ('carregador', 't', pose([(0, (0, 0, 0)), (0.15, (0, 0, 0)), (0.3, tuple(MAG_D * 0.02)), (0.5, tuple(dm)), (0.9, tuple(dm)),
                                  (1.15, tuple(MAG_D * 0.01)), (1.22, (0, 0, 0))])),
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, -18), (1.3, -18), (1.5, -8), (1.7, -8), (2.1, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 10), (1.3, 10), (1.5, 4), (1.7, 4), (2.1, 0)]))],
        desc='recarga com a arma vazia: troca o carregador e solta o ferrolho (1,5 s)')
    A.anim('inspecionar', 2.6, [
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -55), (1.1, -55), (1.5, 30), (2.0, 30), (2.6, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 12), (1.1, 12), (1.5, 8), (2.0, 8), (2.6, 0)])),
        ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.65, (-0.012, 0, 0)), (0.95, (-0.012, 0, 0)), (1.05, (0, 0, 0))]))],
        desc='gira a arma, puxa o ferrolho até ver o cartucho na câmara e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.8), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True,
           desc='respiração leve parado')


# ============================================================================ ACESSORIOS (pivo = ponto de encaixe; mesma orientacao da arma)
def _acessorio(id, nome, categoria, encaixe, **dados):
    return arma(id, nome, 'acessorios', categoria, encaixe=encaixe, **dados)


@_acessorio('protetor_rosca_9mm', 'Protetor de rosca 9 mm', 'boca', 'boca_rosca_9mm', modificadores={}, peso_kg=0.01, raridade='comum',
            descricao='Capa que protege a rosca do cano. Vem na pistola.')
def protetor_rosca_9mm(A):
    q = A.base
    q.add('aco_oxidado', menos(torno_x([(0.0084, -0.0122), (0.0086, -0.0112), (0.0086, 0.0008), (0.0078, 0.0016)], 32),
                               cil_x(0.0046, -0.02, 0.01), cil_x(0.0069, -0.013, -0.0004)))
    for i in range(16):
        a = i * 2 * math.pi / 16; m = caixa(-0.0108, -0.0012, -0.0004, 0.0004, 0.0083, 0.0090)
        m.apply_transform(TF.rotation_matrix(a, [1, 0, 0])); q.add('aco_oxidado', m)
    A.pivo = (-0.0122, 0, 0)


@_acessorio('supressor_9mm', 'Supressor 9 mm', 'boca', 'boca_rosca_9mm', peso_kg=0.2, durabilidade=1200, raridade='raro', valor_troca=60,
            modificadores={'ruido_m': 0.3, 'dano': 0.95, 'alcance_m': 1.05, 'recuo': 0.85}, onde=['quartel', 'motel'],
            descricao='Tubo de alumínio com defletores. O tiro só é ouvido a 18 m: essencial para não chamar a horda.')
def supressor_9mm(A):
    q = A.base; L = 0.16; R = 0.0175
    tubo = torno_x([(0.0, 0.0), (R - 0.003, 0.0), (R, 0.003), (R, L - 0.003), (R - 0.003, L), (0.0, L)], 48)
    tubo = menos(tubo, cil_x(0.0055, -0.01, L + 0.01, sec=24), cil_x(0.0069, -0.001, 0.012, sec=32))
    q.add('aluminio_preto', tubo)
    for x in (0.004, L - 0.012):                                   # tampas recartilhadas
        q.add('recartilhado', tubo_x(R - 0.0001, R + 0.0006, x, x + 0.008, sec=48))
    for i in range(6):                                             # aneis de anodizado (marcas dos defletores)
        x = 0.03 + i * 0.018; q.add('aco_oxidado', tubo_x(R - 0.0002, R + 0.0002, x, x + 0.0012, sec=48))
    q.add('aco_cano', tubo_x(0.0055, 0.0075, L - 0.0002, L + 0.0008, sec=32))
    for i in range(3):
        a = i * 2 * math.pi / 3; m = cil_z(0.0018, -0.0012, 0.0012, 0, 0, 10)
        m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([L + 0.0005, 0.011 * math.cos(a), 0.011 * math.sin(a)])
        q.add('aco_oxidado', m)                                    # furos da chave na tampa da frente
    A.pivo = (0, 0, 0)


@_acessorio('compensador_9mm', 'Compensador 9 mm', 'boca', 'boca_rosca_9mm', peso_kg=0.04, raridade='incomum', valor_troca=15,
            modificadores={'recuo': 0.7, 'ruido_m': 1.15}, onde=['quartel', 'galeria'],
            descricao='Joga os gases para cima e segura o cano: menos coice, mas um pouco mais de barulho.')
def compensador_9mm(A):
    q = A.base; L = 0.03; R = 0.0098
    c = solido(arred([(0, -R), (L, -R), (L, R - 0.002), (L - 0.004, R), (0, R)], 0.0012), -R, R, 0.0015)
    cortes = [cil_x(0.0055, -0.01, L + 0.01), cil_x(0.0069, -0.001, 0.008)]
    for x in (0.012, 0.019, 0.026):
        cortes.append(caixa(x - 0.0022, x + 0.0022, 0.0, 0.02, -0.0045, 0.0045))       # janelas de cima
    for zs in (-1, 1): cortes.append(caixa(0.013, 0.027, -0.0035, 0.0035, zs * 0.006 - 0.01, zs * 0.006 + 0.01) if False else caixa(0.016, 0.026, -0.003, 0.003, -0.02 if zs < 0 else 0.007, -0.007 if zs < 0 else 0.02))
    q.add('aco_oxidado', menos(c, *cortes))
    q.add('aco_inox', cil_z(0.0012, R - 0.0002, R + 0.0003, 0.004, 0.0, 10))            # parafuso de trava
    A.pivo = (0, 0, 0)


@_acessorio('supressor_garrafa', 'Supressor improvisado (garrafa PET)', 'boca', 'boca_rosca_9mm', peso_kg=0.08, durabilidade=12, raridade='comum',
            modificadores={'ruido_m': 0.55, 'precisao': 0.8}, receita={'garrafa_agua': 1, 'fita_adesiva': 1, 'sucata': 1},
            descricao='Garrafa PET com palha de aço, presa com fita e um adaptador de cano. Abafa bem, mas rasga em uns 12 tiros.')
def supressor_garrafa(A):
    q = A.base
    q.add('aco_fosfatado', menos(torno_x([(0.0095, 0.0), (0.0095, 0.022), (0.011, 0.024), (0.011, 0.03)], 24), cil_x(0.0046, -0.01, 0.04), cil_x(0.0069, -0.001, 0.012)))
    perf = [(0.012, 0.028), (0.0125, 0.034), (0.018, 0.04), (0.03, 0.055), (0.0435, 0.075), (0.0445, 0.09), (0.0435, 0.1), (0.0445, 0.12),
            (0.0435, 0.14), (0.0445, 0.16), (0.0445, 0.24), (0.042, 0.255), (0.035, 0.262), (0.02, 0.266), (0.0, 0.267)]
    q.add('pet_garrafa', torno_x(perf, 40))
    q.add('palha_aco', torno_x([(0.0, 0.07), (0.038, 0.075), (0.039, 0.23), (0.0, 0.235)], 20))                # palha de aco dentro
    q.add('fita_cinza', tubo_x(0.0118, 0.0135, 0.022, 0.05, sec=32))                                       # fita no gargalo
    for x in (0.1, 0.17):
        q.add('fita_cinza', tubo_x(0.0444, 0.0458, x, x + 0.024, sec=48))
    q.add('cobre_bala', cil_x(0.0028, 0.264, 0.268, sec=16))     # furo de saida chamuscado
    A.pivo = (0, 0, 0)


def _corpo_rail(q, mat, x0, x1, w=0.016, h=0.012):
    """Base de acessorio de trilho (embaixo do trilho; pivo = centro do topo da braçadeira): garras, parafuso de aperto."""
    sec = Polygon([(-w / 2 - 0.002, 0), (w / 2 + 0.002, 0), (w / 2 + 0.002, -0.008), (-w / 2 - 0.002, -0.008)])
    q.add(mat, ext_x(arred(list(sec.exterior.coords)[:-1], 0.0012), x0, x1))
    for zs in (-1, 1):
        q.add(mat, caixa(x0 + 0.004, x1 - 0.004, -0.001, 0.0015, zs * (w / 2 + 0.0005), zs * (w / 2 + 0.0022)) if zs > 0 else caixa(x0 + 0.004, x1 - 0.004, -0.001, 0.0015, -w / 2 - 0.0022, -w / 2 - 0.0005))
    q.add('aco_inox', cil_z(0.0016, w / 2 + 0.002, w / 2 + 0.004, (x0 + x1) / 2, -0.004, 12))
    q.add('aco_oxidado', caixa((x0 + x1) / 2 - 0.0028, (x0 + x1) / 2 + 0.0028, -0.0002, 0.0018, -w / 2, w / 2))     # trava na fenda


@_acessorio('lanterna_pistola', 'Lanterna tática de trilho', 'trilho', 'trilho_curto', peso_kg=0.11, raridade='incomum', valor_troca=25,
            usa='pilhas', autonomia_min=90, luz={'alcance_m': 35, 'angulo_graus': 22, 'lumens': 600},
            modificadores={}, onde=['quartel', 'posto', 'galeria'],
            descricao='Lanterna de 600 lm presa no trilho. Ilumina sem ocupar a mão, mas a luz atrai zumbis que estão de frente.',
            liga_desliga='no "luz": ligue um SpotLight3D no encaixe "feixe" (aponta para -Z)')
def lanterna_pistola(A):
    q = A.base; L = 0.072
    _corpo_rail(q, 'aluminio_preto', -0.036, 0.0)
    corpo = torno_x([(0.0, -0.048), (0.0115, -0.048), (0.013, -0.046), (0.013, 0.012), (0.0155, 0.018), (0.0155, 0.028), (0.0, 0.028)], 40, -0.017)
    q.add('aluminio_preto', corpo)
    for x in np.linspace(-0.036, -0.004, 9): q.add('aluminio_preto', tubo_x(0.0128, 0.0138, x, x + 0.0018, -0.017, sec=40))   # aletas
    q.add('recartilhado', tubo_x(0.0154, 0.0160, 0.018, 0.027, -0.017, sec=40))
    q.add('aco_inox', tubo_x(0.011, 0.0156, 0.0272, 0.0285, -0.017, sec=40))
    q.add('refletor', torno_x([(0.004, 0.019), (0.011, 0.0272)], 32, -0.017))
    q.add('led_lanterna', cil_x(0.0035, 0.0188, 0.0196, -0.017, 0, 16))
    q.add('lente', cil_x(0.011, 0.0268, 0.0274, -0.017, 0, 40))
    q.add('borracha', caixa(-0.052, -0.044, -0.024, -0.008, -0.009, 0.009))                      # interruptor ambidestro
    for zs in (-1, 1): q.add('borracha', caixa(-0.052, -0.04, -0.03, -0.024, zs * 0.009 - 0.002, zs * 0.009 + 0.002))
    A.encaixe('feixe', (0.028, -0.017, 0), 'efeito', descricao='SpotLight3D aqui, apontando para -Z')
    A.pivo = (0, 0, 0)


@_acessorio('laser_pistola', 'Mira laser de trilho', 'trilho', 'trilho_curto', peso_kg=0.06, raridade='raro', valor_troca=30, usa='pilhas',
            autonomia_min=240, modificadores={'precisao_sem_mirar': 1.35}, onde=['quartel', 'galeria'],
            descricao='Ponto vermelho projetado: acerta melhor atirando sem mirar pela alça.',
            liga_desliga='raio laser a partir do encaixe "laser" (para -Z), ponto onde bater')
def laser_pistola(A):
    q = A.base
    _corpo_rail(q, 'polimero', -0.03, 0.0)
    q.add('polimero', solido(arred([(-0.034, -0.008), (0.006, -0.008), (0.01, -0.012), (0.01, -0.026), (-0.03, -0.026), (-0.036, -0.02)], 0.003),
                             -0.0125, 0.0125, 0.002))
    q.add('aco_inox', tubo_x(0.003, 0.0045, 0.009, 0.0115, -0.0175, 0.0, 24))
    q.add('lente_laser', cil_x(0.003, 0.0098, 0.011, -0.0175, 0, 16))
    for zs in (-1, 1):
        q.add('recartilhado', cil_z(0.0032, min(zs * 0.0125, zs * 0.0145), max(zs * 0.0125, zs * 0.0145), -0.012, -0.018, 20))   # ajustes
    q.add('borracha', caixa(-0.04, -0.035, -0.024, -0.012, -0.007, 0.007))
    A.encaixe('laser', (0.011, -0.0175, 0), 'efeito', descricao='origem do raio laser (-Z)')
    A.pivo = (0, 0, 0)


@_acessorio('combo_lanterna_laser', 'Lanterna com laser', 'trilho', 'trilho_curto', peso_kg=0.15, raridade='muito raro', valor_troca=55,
            usa='pilhas', autonomia_min=75, luz={'alcance_m': 30, 'angulo_graus': 24, 'lumens': 500},
            modificadores={'precisao_sem_mirar': 1.35}, onde=['quartel'],
            descricao='Lanterna e laser num corpo só, com chave de três posições.')
def combo_lanterna_laser(A):
    q = A.base
    _corpo_rail(q, 'aluminio_preto', -0.04, 0.0)
    q.add('aluminio_preto', solido(arred([(-0.05, -0.008), (0.012, -0.008), (0.016, -0.012), (0.016, -0.036), (-0.046, -0.036), (-0.052, -0.026)], 0.004),
                                   -0.0145, 0.0145, 0.0025))
    q.add('aco_inox', tubo_x(0.0085, 0.0105, 0.0158, 0.018, -0.024, 0.004, 32))
    q.add('refletor', torno_x([(0.003, 0.0105), (0.0086, 0.0176)], 24, -0.024, 0.004))
    q.add('led_lanterna', cil_x(0.0028, 0.0103, 0.011, -0.024, 0.004, 16))
    q.add('lente', cil_x(0.0086, 0.0172, 0.0177, -0.024, 0.004, 32))
    q.add('aco_inox', tubo_x(0.002, 0.0032, 0.0158, 0.018, -0.0145, -0.0075, 20))
    q.add('lente_laser', cil_x(0.002, 0.016, 0.0176, -0.0145, -0.0075, 12))
    q.add('borracha', caixa(-0.058, -0.05, -0.032, -0.012, -0.01, 0.01))
    q.add('aco_oxidado', caixa(-0.03, -0.022, -0.0365, -0.034, -0.004, 0.004))                         # chave seletora
    A.encaixe('feixe', (0.018, -0.024, 0.004), 'efeito', descricao='SpotLight3D aqui (-Z)')
    A.encaixe('laser', (0.018, -0.0145, -0.0075), 'efeito', descricao='origem do laser (-Z)')
    A.pivo = (0, 0, 0)


@_acessorio('mira_ponto_vermelho_compacta', 'Mira de ponto vermelho compacta', 'mira', 'mira_ferrolho', peso_kg=0.03, raridade='raro',
            valor_troca=45, usa='pilhas', autonomia_min=3000, modificadores={'precisao_mirando': 1.25, 'tempo_mirar': 0.85},
            onde=['quartel', 'galeria'], linha_de_visada='encaixe "olho": centro da lente, a câmera mira por ali',
            descricao='Mira refletora pequena para o ferrolho da pistola: ponto vermelho, mira mais rápido.')
def mira_ponto_vermelho_compacta(A):
    q = A.base; L0, L1 = -0.014, 0.014
    base = arred([(L0, 0), (L1, 0), (L1, 0.006), (L0, 0.006)], 0.001)
    q.add('aluminio_preto', solido(base, -0.0105, 0.0105, 0.0012))
    jan = arred([(L0 + 0.001, 0.005), (L1 - 0.003, 0.005), (L1 - 0.001, 0.022), (L1 - 0.004, 0.026), (L0 + 0.005, 0.026), (L0 + 0.001, 0.02)], 0.003)
    capuz = menos(solido(jan, -0.0115, 0.0115, 0.002), solido(Polygon([(L0 - 0.01, 0.0075), (L1 + 0.01, 0.0075), (L1 + 0.01, 0.0235), (L0 - 0.01, 0.0235)]).buffer(0), -0.0085, 0.0085))
    q.add('aluminio_preto', capuz)
    q.add('lente', caixa(0.0085, 0.0095, 0.0075, 0.0235, -0.0085, 0.0085))
    q.add('ponto_vermelho', caixa(0.0089, 0.0091, 0.0149, 0.0151, -0.0001, 0.0001))
    q.add('aluminio_preto', caixa(L0, L0 + 0.009, 0.0055, 0.008, -0.0098, 0.0098))                        # tampa da pilha
    for zs in (-1, 1): q.add('borracha', caixa(-0.006, 0.0, 0.009, 0.014, zs * 0.0116 - 0.0008, zs * 0.0116 + 0.0008))   # botoes
    q.add('recartilhado', cil_z(0.0025, 0.0115, 0.0128, 0.002, 0.018, 16))                                       # ajuste lateral
    A.encaixe('olho', (0.009, 0.015, 0), 'mira', descricao='centro da lente: linha de visada')
    A.pivo = (0, 0, 0)


def _carregador_acessorio(A, cap, extra):
    _carregador(A.base, cap, extra)
    A.pivo = (0.0215, -0.016, 0)


@_acessorio('carregador_9mm', 'Carregador 9 mm (15)', 'carregador', 'carregador_9mm', capacidade=15, municao='municao_9mm',
            peso_kg=0.09, raridade='comum', valor_troca=8, modificadores={}, descricao='Carregador padrão da pistola, 15 tiros.')
def carregador_9mm(A): _carregador_acessorio(A, 15, 0.0)


@_acessorio('carregador_9mm_estendido', 'Carregador 9 mm estendido (24)', 'carregador', 'carregador_9mm', capacidade=24, municao='municao_9mm',
            peso_kg=0.13, raridade='raro', valor_troca=20, modificadores={'recarga_s': 1.1}, onde=['quartel', 'galeria'],
            descricao='Mais 9 tiros, mas sai pelo fundo do punho e deixa a recarga um pouco mais lenta.')
def carregador_9mm_estendido(A): _carregador_acessorio(A, 24, 0.04)


# ============================================================================ MUNICAO e EFEITOS
@arma('municao_9mm', 'Cartucho 9 mm', 'municao', 'municao', calibre='9 mm', peso_kg=0.012, empilha=100, raridade='comum',
      onde=['quartel', 'correios', 'motel', 'casas', 'galeria'], descricao='Um cartucho (deitado, pivô no centro). No inventário conta por unidade.')
def municao_9mm(A):
    q = _cartucho_9mm_malha()
    A.base.merge(q, TF.translation_matrix([-0.0147, 0.005, 0]))
    A.pivo = (0, 0, 0)


@arma('estojo_9mm', 'Estojo 9 mm (vazio)', 'municao', 'estojo', calibre='9 mm', peso_kg=0.004,
      descricao='Estojo ejetado: o jogo cria um em saida_estojo a cada tiro (corpo rígido pequeno, some depois de uns segundos).')
def estojo_9mm(A):
    q = A.base
    q.add('latao', menos(torno_x([(0.0, 0.0), (0.0049, 0.0), (0.005, 0.0012), (0.0042, 0.0016), (0.0042, 0.0024), (0.00495, 0.003), (0.00482, 0.019), (0.0, 0.019)], 28),
                         cil_x(0.0043, 0.004, 0.03, sec=24)))
    q.add('aco_inox', torno_x([(0.0, -0.00005), (0.0021, -0.00005), (0.0021, 0.0004)], 16))
    A.pivo = (0.0095, 0, 0)


PXM = 4096                                     # atlas da caixa: 1024 px = 0,25 m
CX = dict(x0=-0.058, x1=0.058, y0=0.0, y1=0.034, z0=-0.044, z1=0.044)
ATLAS = {'topo': (0, 0), 'lado+': (0, 380), 'lado-': (0, 520), 'ponta+': (500, 380), 'ponta-': (500, 520)}


def _arte_caixa_9mm():
    im = Image.new('RGB', (1024, 1024), (236, 230, 212)); d = ImageDraw.Draw(im)
    L = int((CX['x1'] - CX['x0']) * PXM); P_ = int((CX['z1'] - CX['z0']) * PXM); H = int((CX['y1'] - CX['y0']) * PXM)
    x, y = ATLAS['topo']                                                 # tampa: arte principal
    d.rectangle([x, y, x + L, y + P_], fill=(236, 230, 212)); d.rectangle([x, y, x + 120, y + P_], fill=(150, 30, 20))
    texto_c(d, (x + 60, y + P_ // 2), '9', 90, (250, 240, 220))
    texto_c(d, (x + 120 + (L - 120) // 2, y + 80), 'GUARDIÃO', 58, (150, 30, 20), larg=L - 150)
    texto_c(d, (x + 120 + (L - 120) // 2, y + 160), '9 mm', 86, (40, 30, 26))
    texto_c(d, (x + 120 + (L - 120) // 2, y + 240), '50 CARTUCHOS', 36, (40, 30, 26), larg=L - 150)
    texto_c(d, (x + 120 + (L - 120) // 2, y + 290), 'PONTA OGIVAL 124 gr', 24, (90, 70, 60), False, larg=L - 150)
    d.rectangle([x + 130, y + P_ - 30, x + L - 10, y + P_ - 14], fill=(40, 40, 44))
    for k in ('lado+', 'lado-'):
        x, y = ATLAS[k]; d.rectangle([x, y, x + L, y + H], fill=(150, 30, 20))
        texto_c(d, (x + L // 2, y + 82), 'GUARDIÃO  9 mm', 34, (250, 240, 220), larg=L - 40)
        texto_c(d, (x + L // 2, y + 116), 'MANTENHA LONGE DE CRIANÇAS' if k == 'lado+' else 'LOTE 0815 · 50 UN', 17, (240, 220, 200), False, larg=L - 40)
    for k in ('ponta+', 'ponta-'):
        x, y = ATLAS[k]; d.rectangle([x, y, x + P_, y + H], fill=(236, 230, 212)); d.rectangle([x, y, x + P_, y + 22], fill=(150, 30, 20))
        texto_c(d, (x + P_ // 2, y + 96), '9 mm · 50', 34, (40, 30, 26), larg=P_ - 30)
    return im


def _uv_caixa_9mm(v, n):
    """Cada face vai para o seu retangulo do atlas, na mesma densidade (texto nao estica)."""
    uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1); sg = np.sign(n[np.arange(len(n)), ax])
    X = v[:, 0] - CX['x0']; Y = CX['y1'] - v[:, 1]; Z = v[:, 2] - CX['z0']
    def put(m, chave, a, b):
        x, y = ATLAS[chave]; uv[m] = np.stack([(x + a[m] * PXM) / 1024, (y + b[m] * PXM) / 1024], 1)
    put((ax == 1) & (sg > 0), 'topo', X, Z); put((ax == 1) & (sg < 0), 'topo', X, Z)
    put((ax == 2) & (sg > 0), 'lado+', X, Y); put((ax == 2) & (sg < 0), 'lado-', (CX['x1'] - CX['x0']) - X, Y)
    put((ax == 0) & (sg > 0), 'ponta+', (CX['z1'] - CX['z0']) - Z, Y); put((ax == 0) & (sg < 0), 'ponta-', Z, Y)
    uv[:, 1] = 1 - uv[:, 1]
    return uv


@arma('caixa_municao_9mm', 'Caixa de munição 9 mm (50)', 'municao', 'caixa', calibre='9 mm', municao='municao_9mm', quantidade=50,
      peso_kg=0.62, empilha=4, raridade='incomum', onde=['quartel', 'correios', 'motel', 'casas', 'posto'],
      descricao='Caixa de papelão com bandeja de 50 cartuchos. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_9mm(A):
    mat_imagem('rotulo_9mm', _arte_caixa_9mm(), 0.7)
    x0, x1, y0, y1, z0, z1 = (CX[k] for k in ('x0', 'x1', 'y0', 'y1', 'z0', 'z1')); t = 0.0012; yt = y1 - 0.006
    q = A.base
    q.add('rotulo_9mm', menos(caixa(x0, x1, y0, yt, z0, z1), caixa(x0 + t, x1 - t, y0 + t, yt + 0.01, z0 + t, z1 - t)))
    q.uv['rotulo_9mm'] = _uv_caixa_9mm
    q.add('papelao', caixa(x0 + t, x1 - t, y0 + t, y0 + t + 0.0008, z0 + t, z1 - t))
    q.add('plastico_branco', caixa(x0 + t, x1 - t, yt - 0.012, yt - 0.0105, z0 + t, z1 - t))     # bandeja
    cart = _cartucho_9mm_malha(12); Rv = TF.rotation_matrix(math.pi / 2, [0, 0, 1])
    for i in range(10):
        for j in range(5):
            if (i * 5 + j) in (7, 23, 24): continue                                                # 3 ja usados
            x = x0 + 0.0078 + i * 0.01116; z = z0 + 0.0098 + j * 0.0171
            q.merge(cart, TF.translation_matrix([x, y0 + t + 0.0008 + 0.0005, z]) @ Rv)
    tampa = A.parte('tampa', (x0 - 0.0008, yt, 0), tipo='tampa', eixo='z', abre_graus=115, descricao='gira em torno da ponta de trás')
    e = 0.0008; hs = 0.012
    tampa.add('rotulo_9mm', caixa(x0 - e, x1 + e, y1 - 0.0006, y1 + 0.0002, z0 - e, z1 + e)); tampa.uv['rotulo_9mm'] = _uv_caixa_9mm
    tampa.add('papelao', menos(caixa(x0 - e, x1 + e, y1 - hs, y1 - 0.0006, z0 - e, z1 + e), caixa(x0, x1, y1 - hs - 0.01, y1 - 0.0014, z0, z1)))
    A.anim('abrir', 0.6, [('tampa', 'r', (0, 0, 1), pose([(0, 0), (0.6, 115)]))], desc='abre a tampa')
    A.anim('fechar', 0.6, [('tampa', 'r', (0, 0, 1), pose([(0, 115), (0.6, 0)]))], desc='fecha a tampa')
    A.pivo = (0, 0, 0)


@arma('clarao_boca', 'Clarão de boca', 'efeitos', 'efeito', descricao='Mostrar por 1 ou 2 quadros no encaixe boca_fogo a cada tiro; '
      'girar ao acaso em -Z e variar a escala (0,8 a 1,2). Material emissivo com transparência.')
def clarao_boca(A):
    q = A.base
    for i in range(3):                                     # 3 placas cruzadas em estrela + nucleo
        a = i * math.pi / 3
        pts = [(0, 0)]
        for k in range(9):
            t = k / 8; r = 0.012 + 0.016 * (k % 2)
            pts.append((0.004 + 0.075 * t, (r if k % 2 else r * 0.4) * (1 - t * 0.7)))
        pts += [(0.004 + 0.075 * (1 - k / 8), -(0.012 + 0.016 * ((8 - k) % 2)) * (k / 8 * 0.7 + 0.3) * 0.8) for k in range(9)]
        m = solido(Polygon(pts).buffer(0), -0.0002, 0.0002)
        m.apply_transform(TF.rotation_matrix(a, [1, 0, 0])); q.add('clarao', m)
    q.add('clarao_nucleo', torno_x([(0.0, 0.0), (0.01, 0.004), (0.012, 0.012), (0.006, 0.03), (0.0, 0.036)], 16))
    for i in range(5):                                      # fagulhas laterais
        a = i * 2 * math.pi / 5 + 0.3; m = caixa(0.0, 0.022, -0.0006, 0.0006, -0.0002, 0.0002)
        m.apply_transform(TF.rotation_matrix(math.radians(38), [0, 0, 1])); m.apply_transform(TF.rotation_matrix(a, [1, 0, 0]))
        m.apply_translation([0.004, 0, 0]); q.add('clarao', m)
    A.pivo = (0, 0, 0)


# ============================================================================ catalogo e main
CAB = {
    'escala': '1 unidade = 1 m, Y para cima. Armas em posição de tiro: cano para -Z, lado direito +X, pivô na empunhadura.',
    'encaixes': 'nós vazios "encaixe_<tipo>" com a orientação da arma; o acessório entra como filho do nó, transformação identidade. '
                'O "tipo" do encaixe tem que bater com o "encaixe" do acessório. Os acessórios têm o pivô no ponto de encaixe.',
    'partes': 'partes móveis são nós do GLB: tipo desliza (curso_m ao longo do cano), gira (eixo, curso_graus), remove (direcao).',
    'animacoes': 'animações glTF embutidas, só das peças da arma (sem mãos); o nó raiz também se mexe (coice, recarga, inspeção).',
    'campos_jogo': {'dano': 'por tiro (zumbi comum tem 100 de vida, cabeça x2,5)', 'alcance_m': 'alcance efetivo; depois disso o dano cai',
                    'alcance_max_m': 'alcance máximo', 'tiros_por_s': 'cadência máxima', 'precisao': '0 a 1', 'recuo': '0 a 1',
                    'ruido_m': 'raio em que os zumbis ouvem o tiro', 'durabilidade': 'tiros até precisar de reparo',
                    'modificadores': 'multiplicadores aplicados à arma pelo acessório', 'valor_troca': 'preço na troca entre comunidades'},
}
NOMES = {'pistola': 'Pistolas', 'boca': 'Boca do cano', 'trilho': 'Trilho', 'mira': 'Miras', 'carregador': 'Carregadores',
         'municao': 'Munição', 'estojo': 'Estojos', 'caixa': 'Caixas de munição', 'efeito': 'Efeitos'}


def catalogo_md(cat):
    v = lambda x: re.sub(r'(\d)\.(\d)', r'\1,\2', str(x))
    L = ['# Catálogo de armas, acessórios e munição', '', 'Gerado por `props/armas/gerar_armas.py` a partir de `catalogo.json`. '
         'Medidas em metros (largura × altura × comprimento).', '']
    L += ['## Armas', '', '| Arma | Calibre | Tiros | Dano | Alcance | Cadência | Ruído | Durab. | Peso | Encaixes | Animações |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in cat['armas']:
        enc = ', '.join(e['no'].replace('encaixe_', '') for e in r.get('encaixes', []) if e['tipo'] not in ('efeito', 'mira') or e['no'].startswith('encaixe'))
        L.append(f"| {r['nome']} (`{r['id']}`) | {r['calibre']} | {r['capacidade']} | {r['dano']} | {r['alcance_m']} m | {v(r['tiros_por_s'])}/s | "
                 f"{r['ruido_m']} m | {r['durabilidade']} | {v(r['peso_kg'])} kg | {enc} | {', '.join(r.get('animacoes', {}))} |")
    L += ['', '## Acessórios', '', '| Acessório | Tipo | Encaixe | Efeito no jogo | Peso | Raridade | Triângulos |', '|---|---|---|---|---|---|---|']
    for r in cat['acessorios']:
        mod = ', '.join(f"{k} ×{v(x)}" for k, x in r.get('modificadores', {}).items()) or '-'
        L.append(f"| {r['nome']} (`{r['id']}`) | {NOMES[r['categoria']]} | `{r['encaixe']}` | {mod} | {v(r['peso_kg'])} kg | {r['raridade']} | {r['triangulos']} |")
    L += ['', '## Munição e efeitos', '', '| Item | Tipo | Descrição | Triângulos |', '|---|---|---|---|']
    for g in ('municao', 'efeitos'):
        for r in cat[g]: L.append(f"| {r['nome']} (`{r['id']}`) | {NOMES[r['categoria']]} | {r['descricao']} | {r['triangulos']} |")
    L += ['', '## Compatibilidade', '']
    for r in cat['armas']:
        for e in r.get('encaixes', []):
            if 'aceita' in e: L.append(f"- **{r['nome']}**, `{e['no']}`: {', '.join(e['aceita'])}")
    open(os.path.join(AQUI, 'CATALOGO.md'), 'w', encoding='utf-8').write(v('\n'.join(L)).replace('×', '×') + '\n')


def main(ids):
    materiais(); MATS['palha_aco'] = PBRMaterial(name='palha_aco', baseColorFactor=[0.07, 0.07, 0.075, 1], metallicFactor=0.8, roughnessFactor=0.7)
    MATS['refletor'] = PBRMaterial(name='refletor', baseColorFactor=[0.9, 0.9, 0.92, 1], metallicFactor=1.0, roughnessFactor=0.08)
    arq = os.path.join(AQUI, 'catalogo.json'); grupos = ('armas', 'acessorios', 'municao', 'efeitos')
    cat = {g: [] for g in grupos}
    if ids and os.path.exists(arq):
        velho = json.load(open(arq, encoding='utf-8')); cat = {g: [r for r in velho.get(g, []) if r['id'] not in ids] for g in grupos}
    for id_, it in REG.items():
        if ids and id_ not in ids: continue
        r = exportar(it, AQUI); cat[it['grupo']].append(r)
        print(f"{id_:30s} {r['triangulos']:7d} tris {r['kb']:7.1f} KB  {r['tamanho_m']}")
    ordem = list(REG)
    for g in grupos: cat[g].sort(key=lambda r: ordem.index(r['id']) if r['id'] in ordem else 999)
    json.dump(dict(CAB, **cat), open(arq, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    catalogo_md(cat)


if __name__ == '__main__':
    main(sys.argv[1:])
