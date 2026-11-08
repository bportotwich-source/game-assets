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
    'polimero_verde': (70, 76, 54), 'polimero_cinza': (128, 130, 130), 'cano_dourado': (176, 132, 62),
    'etiqueta_amarela': (214, 176, 40), 'cerakote_verde': (74, 82, 58), 'cerakote_cinza': (124, 126, 128), 'cerakote_areia': (136, 112, 82),
    'aluminio_preto': (26, 26, 28), 'latao': (150, 112, 46), 'cobre_bala': (150, 76, 40), 'chumbo': (90, 92, 96),
    'tinta_branca': (230, 230, 224), 'tinta_laranja': (200, 80, 10), 'mola': (120, 122, 126),
    'borracha_grip': (28, 28, 28), 'borracha': (30, 30, 32), 'plastico_branco': (232, 232, 226), 'pet_azul': (90, 140, 180), 'fita_cinza': (150, 150, 146),
}
METAL = {'aco_oxidado': (0.75, 0.32), 'aco_fosfatado': (0.55, 0.62), 'aco_inox': (0.9, 0.22), 'aco_cano': (0.8, 0.3),
         'aluminio_preto': (0.55, 0.38), 'latao': (0.95, 0.28), 'cobre_bala': (0.95, 0.3), 'chumbo': (0.7, 0.5), 'mola': (0.9, 0.35),
         'polimero': (0.0, 0.55), 'polimero_tan': (0.0, 0.6), 'polimero_verde': (0.0, 0.6), 'polimero_cinza': (0.0, 0.6), 'cano_dourado': (0.9, 0.3), 'etiqueta_amarela': (0.0, 0.5),
         'cerakote_verde': (0.2, 0.55), 'cerakote_cinza': (0.2, 0.55), 'cerakote_areia': (0.2, 0.55), 'tinta_branca': (0.0, 0.4), 'tinta_laranja': (0.0, 0.45),
         'borracha_grip': (0.0, 0.9), 'fita_cinza': (0.3, 0.5), 'borracha': (0.0, 0.85), 'plastico_branco': (0.0, 0.5)}
TEX_EXTRA = []   # (material, funcao de textura, metallic): texturas que os arquivos armaNN acrescentam (ex.: desgaste)
TRANSP = {'lente': ((120, 160, 150), 0.35, 0.03), 'lente_clara': ((170, 205, 195), 0.1, 0.02), 'lente_laser': ((200, 30, 20), 0.6, 0.05), 'pet_garrafa': ((150, 190, 215), 0.22, 0.06)}
EMISSIVOS = {'ponto_vermelho': (1.0, 0.05, 0.02), 'led_lanterna': (1.0, 0.97, 0.88), 'led_laser': (1.0, 0.08, 0.04),
             'clarao': (1.0, 0.62, 0.22), 'clarao_nucleo': (1.0, 0.92, 0.7)}


def _tex_grip(seed, px=1024, tile=0.05, cor='polimero_grip'):
    """Pontilhado do punho de polimero: picotes pequenos e irregulares (normal + rugosidade)."""
    n = int(tile * px); g = GT.noise(n, n, 0.0006 * px, 0.0006 * px, seed); f = GT.fbm(n, n, 0.003 * px, 3, seed + 3)
    pic = GT.smooth(0.3, 1.4, g)
    c = GT.rgb(CORES[cor])[None, None]
    alb = c * (0.72 + 0.1 * pic[..., None] + 0.03 * f[..., None]); hm = 0.00025 * pic + 0.00005 * f
    return alb, hm, 0.75 + 0.15 * pic, 1.2, 0.0004, tile, px


def _tex_pontos(seed, cor='polimero', px=8000, tile=0.032, passo=0.0016):
    """Pontilhado quadriculado do punho: pontas quadradas em relevo em grade regular (le como textura moldada de fabrica)."""
    n = int(round(tile * px)); yy, xx = np.mgrid[0:n, 0:n] / px
    fx = np.abs((xx / passo) % 1 - 0.5) * 2; fy = np.abs((yy / passo) % 1 - 0.5) * 2
    pir = np.clip(1.0 - np.maximum(fx, fy) / 0.62, 0, 1)                     # piramide quadrada truncada
    pir = np.minimum(pir * 1.8, 1.0)
    f = GT.fbm(n, n, 0.004 * px, 3, seed)
    c = GT.rgb(CORES[cor])[None, None]
    alb = c * (0.86 + 0.12 * pir[..., None] + 0.03 * f[..., None]); hm = 0.0003 * pir + 0.00002 * f
    return alb, hm, 0.8 - 0.1 * pir, 1.4, 0.0004, tile, px


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
    for i, (k, fn) in enumerate((('polimero_grip', _tex_grip), ('recartilhado', _tex_serrilha),
                                  ('polimero_grip_tan', lambda s: _tex_grip(s, cor='polimero_tan')),
                                  ('polimero_pontos', _tex_pontos), ('polimero_pontos_tan', lambda s: _tex_pontos(s, 'polimero_tan')),
                                  ('polimero_pontos_verde', lambda s: _tex_pontos(s, 'polimero_verde')),
                                  ('polimero_pontos_cinza', lambda s: _tex_pontos(s, 'polimero_cinza')))):
        alb, hm, rough, nstr, aod, tile, px = fn(301 + i)
        a, nm, o = tex_set(alb, hm, rough, nstr, aod, px)
        TEX[k] = (a, nm, o); gp.UV_ESCALA[k] = tile
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0 if k.startswith('polimero') else 0.7, roughnessFactor=1.0)
    for k, fn, met in TEX_EXTRA:
        alb, hm, rough, nstr, aod, tile, px = fn(); a, nm, o = tex_set(alb, hm, rough, nstr, aod, px)
        TEX[k] = (a, nm, o); gp.UV_ESCALA[k] = tile
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=met, roughnessFactor=1.0)
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


def punho_redondo(perfil, y_topo, y_base, meia_larg, n=2.6, fatias=70, voltas=40, raio_base=0.006, raio_topo=0.0):
    """Cabo com secao ARREDONDADA (superelipse) seguindo o perfil lateral: em cada altura y pega a extensao do perfil em x
    (frente e costas do cabo) e faz uma secao de largura 2 * meia_larg(y). n ~ 2 = oval, maior = mais quadrado.
    raio_base arredonda a borda de baixo (e raio_topo a de cima). Devolve um solido estanque (serve para booleanos)."""
    ys = np.linspace(y_topo, y_base, fatias)
    ang = np.linspace(0, 2 * math.pi, voltas, endpoint=False); c, s_ = np.cos(ang), np.sin(ang)
    ex = lambda w: np.sign(w) * np.abs(w) ** (2.0 / n)
    aneis = []
    for y in ys:
        g = perfil.intersection(LineString([(-1, y), (1, y)]))
        segs = [g] if g.geom_type == 'LineString' else [h for h in getattr(g, 'geoms', []) if h.geom_type == 'LineString']
        if not segs or g.is_empty: continue
        sg = min(segs, key=lambda h: h.bounds[0]); xa, xb = sg.bounds[0], sg.bounds[2]
        a = (xb - xa) / 2; b = meia_larg(y); k = 0.0
        if raio_base and y < y_base + raio_base:
            t = (y_base + raio_base - y) / raio_base; k = raio_base * (1 - math.sqrt(max(0.0, 1 - t * t)))
        if raio_topo and y > y_topo - raio_topo:
            t = (y - (y_topo - raio_topo)) / raio_topo; k = max(k, raio_topo * (1 - math.sqrt(max(0.0, 1 - t * t))))
        a = max(a - k, 0.0008); b = max(b - k, 0.0008)
        aneis.append(np.stack([(xa + xb) / 2 + a * ex(c), np.full(voltas, y), b * ex(s_)], 1))
    V = np.concatenate(aneis + [aneis[0].mean(0, keepdims=True), aneis[-1].mean(0, keepdims=True)]); N = len(aneis); F = []
    for i in range(N - 1):
        for j in range(voltas):
            a0 = i * voltas + j; a1 = i * voltas + (j + 1) % voltas; b0 = a0 + voltas; b1 = a1 + voltas
            F += [[a0, b0, a1], [a1, b0, b1]]
    ct, cb = N * voltas, N * voltas + 1
    for j in range(voltas):
        F.append([ct, j, (j + 1) % voltas]); F.append([cb, (N - 1) * voltas + (j + 1) % voltas, (N - 1) * voltas + j])
    m = trimesh.Trimesh(V, np.array(F), process=True); trimesh.repair.fix_normals(m)
    return _fix(m)


def suave(pts, it=4):
    """Contorno fechado suavizado (Chaikin): cantos viram curvas, sem facetas."""
    P_ = np.array(pts, float)
    for _ in range(it):
        Q = np.roll(P_, -1, 0); P_ = np.stack([0.75 * P_ + 0.25 * Q, 0.25 * P_ + 0.75 * Q], 1).reshape(-1, 2)
    return Polygon(P_).buffer(0)


def _fatia(contorno, y):
    g = contorno.intersection(LineString([(-1, y), (1, y)]))
    segs = [g] if g.geom_type == 'LineString' else [h for h in getattr(g, 'geoms', []) if h.geom_type == 'LineString']
    sg = min(segs, key=lambda h: h.bounds[0]); return sg.bounds[0], sg.bounds[2]


def z_superficie(contorno, x, y, meia_larg, n):
    """Altura z da superficie do punho_redondo no ponto (x, y) do lado direito."""
    xa, xb = _fatia(contorno, y); a = (xb - xa) / 2; u = min(abs(x - (xa + xb) / 2) / a, 0.999)
    return meia_larg(y) * (1 - u ** n) ** (1 / n)


def cabo_com_talas(q, contorno, y_topo, y_base, larg_nucleo, larg_tala, mat_nucleo, mat_tala, mat_xadrez=None, borda=0.0016,
                   borda_xadrez=0.0035, n=2.3, raio_base=0.006, medalhao=None, parafuso=None, nucleo=True):
    """Cabo de verdade: nucleo arredondado da armacao (aparece nas costas e na frente) + talas que seguem a curva do cabo,
    com borda lisa e area quadriculada levantada, medalhao e parafuso da tala. contorno = Polygon suave do cabo (vista de lado)."""
    if nucleo: q.add(mat_nucleo, punho_redondo(contorno, y_topo, y_base, larg_nucleo, n=n, fatias=110, voltas=56, raio_base=raio_base))
    prisma = lambda pl: solido(pl, -0.05, 0.05)
    tala = punho_redondo(contorno, y_topo, y_base, larg_tala, n=n, fatias=110, voltas=56, raio_base=raio_base)
    q.add(mat_tala, inter([tala, prisma(contorno.buffer(-borda, join_style=1))]))
    if mat_xadrez:
        lx = lambda y: larg_tala(y) + 0.0005
        xz = punho_redondo(contorno, y_topo, y_base, lx, n=n, fatias=110, voltas=56, raio_base=raio_base)
        area = contorno.buffer(-borda - borda_xadrez, join_style=1).intersection(sbox(-1, y_base + raio_base + 0.002, 1, y_topo - 0.004))
        q.add(mat_xadrez, inter([xz, prisma(area)]))
        if medalhao:                                                  # medalhao liso no meio do quadriculado
            mx, my, mr, mm = medalhao
            for zs in (-1, 1):
                zc = z_superficie(contorno, mx, my, lx, n)
                d = torno_x([(0.0, -0.0006), (mr, -0.0006), (mr, 0.0002), (mr * 0.85, 0.0007), (0.0, 0.0008)], 32)
                d.apply_transform(TF.rotation_matrix(-zs * math.pi / 2, [0, 1, 0])); d.apply_translation([mx, my, zs * zc]); q.add(mm, d)
                sol = torno_x([(0.0, 0.0), (mr * 0.5, 0.0), (mr * 0.5, 0.0003), (0.0, 0.0003)], 24)       # sol nascente (marca do Recomeco)
                sol.apply_transform(TF.rotation_matrix(-zs * math.pi / 2, [0, 1, 0])); sol.apply_translation([mx, my, zs * (zc + 0.0008)]); q.add('aco_oxidado', sol)
    if parafuso:
        px, py = parafuso; zc = z_superficie(contorno, px, py, larg_tala, n)
        for zs in (-1, 1):
            m = torno_x([(0.0, -0.0004), (0.0021, -0.0004), (0.0021, 0.0002), (0.0015, 0.0007), (0.0, 0.0008)], 20)
            m.apply_transform(TF.rotation_matrix(-zs * math.pi / 2, [0, 1, 0])); m.apply_translation([px, py, zs * zc]); q.add('aco_inox', m)
            f = caixa(px - 0.0016, px + 0.0016, py - 0.00025, py + 0.00025, zs * (zc + 0.0005) - 0.0003, zs * (zc + 0.0005) + 0.0003)
            q.add('aco_oxidado', f)


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


# listas de acessorios para os encaixes de lanterna, laser e empunhadura que toda arma longa ganha
ACEITA_LANTERNA = ['lanterna_fuzil', 'lanterna_compacta']
ACEITA_LASER = ['laser_fuzil', 'modulo_laser', 'modulo_laser_tan']
ACEITA_EMPUNHADURA = ['empunhadura_vertical', 'empunhadura_angulada', 'empunhadura_curta', 'empunhadura_curta_tan', 'empunhadura_quadrada',
                      'empunhadura_cilindrica', 'empunhadura_reta', 'empunhadura_reta_tan', 'batente_mao']


def placa_mlok(p, mat, x0, x1, yc, zf, lado=1, alt=0.016, esp=0.0035, mat_paraf='aco_inox'):
    """Placa curta de M-LOK aparafusada no lado da coronha ou do guarda-mao (para lanterna ou laser). zf = face de fora
    (lado +1 = direita, -1 = esquerda); a placa entra esp para dentro da peca. Fendas oblongas rasas e dois parafusos."""
    z0, z1 = sorted((zf, zf - lado * esp))
    pl = solido(arred([(x0, yc - alt / 2), (x1, yc - alt / 2), (x1, yc + alt / 2), (x0, yc + alt / 2)], 0.003), z0, z1, 0.0008)
    n = max(1, int((x1 - x0 - 0.012) / 0.02)); xa = (x0 + x1) / 2 - (n - 1) * 0.01
    zc0, zc1 = sorted((zf - lado * 0.0012, zf + lado * 0.001))
    fendas = [solido(LineString([(xa + i * 0.02 - 0.0045, yc), (xa + i * 0.02 + 0.0045, yc)]).buffer(0.0028, 10), zc0, zc1) for i in range(n)]
    p.add(mat, menos(pl, *fendas))
    for x in (x0 + 0.0045, x1 - 0.0045):
        a, b = sorted((zf, zf + lado * 0.0006)); p.add(mat_paraf, cil_z(0.0018, a, b, x, yc, 12))


def placa_mlok_baixo(p, mat, x0, x1, yf, meia=0.008, esp=0.004, mat_paraf='aco_inox'):
    """Placa de M-LOK embaixo (para empunhadura): yf = face de baixo; a placa sobe esp para dentro da peca."""
    pl = solido(arred([(x0, yf), (x1, yf), (x1, yf + esp), (x0, yf + esp)], 0.0012), -meia, meia, 0.0008)
    n = max(1, int((x1 - x0 - 0.012) / 0.02)); xa = (x0 + x1) / 2 - (n - 1) * 0.01
    fendas = [ext_y(LineString([(xa + i * 0.02 - 0.0045, 0.0), (xa + i * 0.02 + 0.0045, 0.0)]).buffer(0.0028, 10), yf - 0.001, yf + 0.0012) for i in range(n)]
    p.add(mat, menos(pl, *fendas))
    for x in (x0 + 0.0045, x1 - 0.0045):
        p.add(mat_paraf, trimesh.creation.cylinder(radius=0.0018, segment=[[x, yf, 0], [x, yf - 0.0006, 0]], sections=12))


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
    if A.partes:
        reg['partes'] = [{k: v for k, v in p.items() if k not in ('peca', 'origem', 'pai', 'explodir')} | {'pai': p['pai'] or nome}
                         | ({'explodir_m': [round(float(c), 4) for c in rot(p['explodir'])]} if 'explodir' in p else {}) for p in A.partes]
    if A.encaixes:
        reg['encaixes'] = [{'no': e['no'], 'tipo': e['tipo'], 'pai': e['pai'] or nome, 'posicao_m': [round(float(c), 4) for c in pos_w[e['no']]],
                            **{k: v for k, v in e.items() if k not in ('no', 'tipo', 'pai', 'pos', 'explodir')},
                            **({'explodir_m': [round(float(c), 4) for c in rot(e['explodir'])]} if 'explodir' in e else {})} for e in A.encaixes]
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


def _ferrolho_pistola(q, mat='aco_oxidado'):
    """Ferrolho quadrado com chanfros largos em cima, nariz chanfrado embaixo, serrilhas inclinadas atras e na frente
    (cortam tambem o chanfro de cima), janela de ejecao, rebaixo de mira com tampa, placa traseira e miras de ferro."""
    CH = 0.0042                                                  # chanfro de cima
    lado = Polygon([(0, SL_Y0), (SL_L - 0.004, SL_Y0), (SL_L, SL_Y0 + 0.004), (SL_L, SL_Y1 - 0.006), (SL_L - 0.007, SL_Y1),
                    (0.002, SL_Y1), (0, SL_Y1 - 0.002)])
    planta = Polygon([(0, -SL_W), (SL_L - 0.022, -SL_W), (SL_L, -SL_W + 0.0018), (SL_L, SL_W - 0.0018), (SL_L - 0.022, SL_W), (0, SL_W)])
    sec = lambda f: Polygon([(-SL_W + f, SL_Y0 + 0.0006), (-SL_W + f + 0.0006, SL_Y0), (SL_W - f - 0.0006, SL_Y0), (SL_W - f, SL_Y0 + 0.0006),
                             (SL_W - f, SL_Y1 - CH - f * 0.4), (SL_W - CH - f * 0.4, SL_Y1 - f), (-SL_W + CH + f * 0.4, SL_Y1 - f),
                             (-SL_W + f, SL_Y1 - CH - f * 0.4)])
    corpo = inter([solido(lado, -SL_W, SL_W), ext_y(planta, SL_Y0 - 0.01, SL_Y1 + 0.01), ext_x(sec(0.0), -0.01, SL_L + 0.01)])
    miolo = ext_x(sec(0.0009), -0.02, SL_L + 0.02)               # serrilha = 0,9 mm de fundo em qualquer face
    cortes = []
    for xs, n, ang in ((0.006, 10, 4), (0.136, 7, -24)):          # atras quase em pe; na frente bem inclinadas
        for i in range(n):
            x = xs + i * 0.0031
            g = caixa(-0.00065, 0.00065, -0.03, 0.03, -0.03, 0.03)
            g.apply_transform(TF.rotation_matrix(math.radians(ang), [0, 0, 1])); g.apply_translation([x, SL_Y0 + 0.016, 0])
            cortes.append(inter([g, caixa(x - 0.012, x + 0.012, SL_Y0 + 0.0035, SL_Y1 + 0.01, -1, 1)]))
    serr = menos(uniao(cortes), miolo)
    cortes = [serr]
    cortes.append(caixa(0.07, 0.112, 0.003, 0.03, -0.0035, 0.03))  # janela de ejecao (topo e lado direito)
    cortes.append(cil_x(0.0068, SL_L - 0.004, SL_L + 0.01))      # boca do ferrolho (o cano aparece)
    cortes.append(cil_x(0.0062, SL_L - 0.004, SL_L + 0.01, -0.0115))   # guia da mola por baixo
    cortes.append(caixa(0.024, 0.06, SL_Y1 - 0.0022, SL_Y1 + 0.01, -0.0105, 0.0105))   # rebaixo para mira de ferrolho
    cortes.append(caixa(-0.01, 0.0012, -0.0085, 0.0075, -0.0062, 0.0062))              # rebaixo da placa traseira
    q.add(mat, menos(corpo, *cortes))
    q.add('aco_oxidado', solido(arred([(-0.0003, -0.0082), (0.0013, -0.0082), (0.0013, 0.0072), (-0.0003, 0.0072)], 0.0004), -0.006, 0.006, 0.0003))  # placa traseira
    q.add('polimero', cil_x(0.0016, -0.0006, 0.0, 0.0, 0.0, 16))                                                      # ponta do percussor
    q.cham(mat, 0.0255, 0.0585, SL_Y1 - 0.0021, SL_Y1 - 0.0004, -0.0098, 0.0098, 0.0005)  # tampa do rebaixo
    for x in (0.031, 0.053):
        m = trimesh.creation.cylinder(radius=0.0011, height=0.0006, sections=10); m.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0]))
        m.apply_translation([x, SL_Y1 - 0.0001, 0]); q.add('aco_inox', m)            # parafusos da tampa
    # alca de mira (bloco com entalhe em U e contorno branco)
    alca = arred([(0.004, SL_Y1 - 0.001), (0.016, SL_Y1 - 0.001), (0.0165, SL_Y1 + 0.0058), (0.0055, SL_Y1 + 0.0064), (0.004, SL_Y1 + 0.006)], 0.0006)
    entalhe = ext_x(Polygon([(-0.0016, SL_Y1 + 0.0028)] + [(0.0016 * math.cos(a), SL_Y1 + 0.0028 + 0.0016 * math.sin(a)) for a in np.linspace(0, -math.pi, 9)][::-1] +
                            [(0.0016, SL_Y1 + 0.0028), (0.0016, SL_Y1 + 0.009), (-0.0016, SL_Y1 + 0.009)]).buffer(0), 0.0, 0.03)
    q.add(mat, menos(solido(alca, -0.0072, 0.0072, 0.0008), entalhe))
    u = LineString([(-0.0034, SL_Y1 + 0.0055), (-0.0034, SL_Y1 + 0.0026)] + [(0.0034 * math.cos(a), SL_Y1 + 0.0026 + 0.0034 * math.sin(a)) for a in np.linspace(-math.pi, 0, 13)][1:-1] +
                   [(0.0034, SL_Y1 + 0.0026), (0.0034, SL_Y1 + 0.0055)]).buffer(0.0005, cap_style=2)
    m = ext_x(u, 0.0035, 0.0041); q.add('tinta_branca', m)
    # massa de mira frontal com ponto branco
    mas = arred([(0.166, SL_Y1 - 0.001), (0.178, SL_Y1 - 0.001), (0.1765, SL_Y1 + 0.0058), (0.1695, SL_Y1 + 0.0058)], 0.0006)
    q.add(mat, solido(mas, -0.0016, 0.0016, 0.0004))
    d = trimesh.creation.cylinder(radius=0.0011, height=0.0006, sections=12); d.apply_transform(TF.rotation_matrix(-math.pi / 2, [0, 1, 0]))
    d.apply_translation([0.1661, SL_Y1 + 0.0037, 0]); q.add('tinta_branca', d)
    # extrator (lado direito), indicador de camara e furos de pino
    q.add('aco_inox', solido(arred([(0.058, 0.0035), (0.07, 0.0035), (0.07, 0.008), (0.058, 0.008)], 0.0006), SL_W - 0.0003, SL_W + 0.0004, 0.0002))
    q.add('aco_oxidado', cil_z(0.0012, SL_W - 0.0002, SL_W + 0.0005, 0.061, 0.0058, 10))


def _armacao_pistola(p):
    # perfil lateral da armacao (polimero): rabo de castor, guarda-mato de frente reta com gancho, guarda-po com trilho
    out = [(-0.003, SL_Y0 + 0.0005), (-0.016, -0.0172), (-0.0225, -0.0215), (-0.0222, -0.0252), (-0.0135, -0.031), (-0.018, -0.05), (-0.027, -0.085),
           (-0.033, -0.112), (-0.034, -0.119), (-0.028, -0.123), (0.019, -0.123), (0.024, -0.118), (0.025, -0.11), (0.03, -0.1),
           (0.029, -0.093), (0.034, -0.083), (0.033, -0.076), (0.039, -0.066), (0.038, -0.058), (0.044, -0.047), (0.048, -0.0445),
           (0.06, -0.0505), (0.094, -0.0515), (0.0985, -0.0495), (0.0992, -0.046), (0.0975, -0.034), (0.1025, -0.03), (0.18, -0.03),
           (0.183, -0.027), (0.183, SL_Y0 + 0.0005)]
    perfil = arred(out, 0.0014)
    guarda = arred([(0.051, -0.0435), (0.062, -0.0465), (0.09, -0.047), (0.0935, -0.0445), (0.0935, -0.0335), (0.089, -0.0265), (0.053, -0.0265), (0.047, -0.034)], 0.0028)
    perfil = perfil.difference(guarda)
    alto = perfil.difference(sbox(-0.05, -0.13, 0.06, -0.0295)).union(perfil.intersection(sbox(0.045, -0.06, 0.2, 0)))
    m_alto = solido(alto, -0.0112, 0.0112, 0.0012)
    CABO9 = suave([(-0.0125, -0.0262), (-0.0168, -0.044), (-0.0235, -0.068), (-0.0305, -0.094), (-0.0345, -0.114), (-0.0338, -0.1225),
                   (-0.0272, -0.1255), (0.0182, -0.1255), (0.0238, -0.1218), (0.0258, -0.112), (0.0306, -0.101), (0.0308, -0.093), (0.0352, -0.084),
                   (0.0354, -0.076), (0.0398, -0.067), (0.0402, -0.059), (0.0452, -0.047), (0.0478, -0.031), (0.04, -0.0262)])
    palma = lambda y: 0.0012 * math.exp(-((y + 0.075) / 0.02) ** 2)                 # apoio da palma (incha no meio)
    larg = lambda y: 0.0105 + 0.0038 * GT.smooth(-0.0285, -0.05, y) + palma(y) + 0.0006 * GT.smooth(-0.112, -0.122, y)   # boca do poco abre embaixo
    m_punho = punho_redondo(CABO9, -0.0285, -0.1255, larg, n=2.4, fatias=110, voltas=56, raio_base=0.0035)
    poco = _perfil_carregador(0.0008)
    fenda = caixa(0.06, 0.082, -0.03, -0.012, -0.0045, 0.0045)
    polegar = []                                                   # rebaixo do polegar dos dois lados, acima do punho
    for zs in (-1, 1):
        e = trimesh.creation.icosphere(3, radius=1.0); e.apply_scale([0.017, 0.0075, 0.0055]); e.apply_translation([0.02, -0.0385, zs * 0.0178]); polegar.append(e)
    p.add('polimero', menos(m_alto, solido(poco, -0.0096, 0.0096), fenda, *polegar))
    p.add('polimero', menos(m_punho, solido(poco, -0.0096, 0.0096), fenda, *polegar))
    # pontilhado quadriculado em painel com borda lisa (frente com as cavas dos dedos tambem pontilhada)
    lp = lambda y: larg(y) + 0.00035
    pont = punho_redondo(CABO9, -0.0285, -0.1255, lp, n=2.4, fatias=110, voltas=56, raio_base=0.0035)
    area = CABO9.buffer(-0.0016, join_style=1).intersection(sbox(-1, -0.118, 1, -0.049))
    p.add('polimero_pontos', menos(inter([pont, solido(area, -0.05, 0.05)]), solido(poco, -0.0096, 0.0096)))
    # trilho embaixo do guarda-po (uma fenda larga) e frente do guarda-po com degrau
    trilho(p, 'polimero', 0.105, 0.177, -0.03, True, 0.019, 0.026)
    # alavanca do retem do ferrolho (esquerda), retem do carregador quadriculado (dos dois lados), alavanca de desmontagem, pinos
    ret = arred([(0.03, -0.014), (0.07, -0.014), (0.074, -0.0115), (0.07, -0.009), (0.046, -0.009), (0.038, -0.006), (0.03, -0.007)], 0.0008)
    p.add('aco_oxidado', solido(ret, -0.0124, -0.0112, 0.0004))
    for x in np.linspace(0.033, 0.041, 4):
        p.add('aco_oxidado', caixa(x - 0.0004, x + 0.0004, -0.0085, -0.0058, -0.0126, -0.0122))
    bot = arred([(0.0405, -0.0415), (0.0505, -0.0415), (0.0505, -0.0325), (0.0405, -0.0325)], 0.0012)
    for zs in (-1, 1):
        p.add('polimero', solido(bot, min(zs * 0.0108, zs * 0.0122), max(zs * 0.0108, zs * 0.0122), 0.0004))
        p.add('polimero_pontos', solido(bot.buffer(-0.0012), min(zs * 0.0121, zs * 0.0124), max(zs * 0.0121, zs * 0.0124)))
    lev = arred([(0.083, -0.021), (0.095, -0.021), (0.095, -0.017), (0.083, -0.017)], 0.0012)
    for zs in (-1, 1):
        p.add('aco_oxidado', solido(lev, min(zs * 0.0112, zs * 0.0122), max(zs * 0.0112, zs * 0.0122), 0.0003))
        for x in np.linspace(0.085, 0.093, 4):
            p.add('aco_oxidado', caixa(x - 0.0003, x + 0.0003, -0.0205, -0.0175, min(zs * 0.0121, zs * 0.0124), max(zs * 0.0121, zs * 0.0124)))
    for (x, y) in ((0.072, -0.022), (0.052, -0.02), (-0.006, -0.022)):
        for zs in (-1, 1): p.add('aco_inox', cil_z(0.0014, min(zs * 0.0111, zs * 0.0118), max(zs * 0.0111, zs * 0.0118), x, y, 12))
    # placa lisa de identificacao (sem marcas) nos dois lados do guarda-po e pega do cordao no fundo do punho
    for zs in (-1, 1):
        p.add('polimero', solido(arred([(0.112, -0.0262), (0.15, -0.0262), (0.15, -0.0215), (0.112, -0.0215)], 0.0012),
                                 min(zs * 0.0111, zs * 0.0116), max(zs * 0.0111, zs * 0.0116), 0.0003))
    p.add('polimero', menos(solido(arred([(-0.03, -0.1275), (-0.018, -0.1275), (-0.018, -0.1235), (-0.03, -0.1235)], 0.0012), -0.004, 0.004, 0.0005),
                            cil_z(0.0012, -0.01, 0.01, -0.024, -0.126, 12)))


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
    """Gatilho curvo (ponta para a FRENTE) com tecla de seguranca no meio; origem no pino (0.071, -0.0215)."""
    lam = LineString([(0.0712, -0.0235), (0.0692, -0.0295), (0.0686, -0.0355), (0.0698, -0.0398), (0.0728, -0.0425)]).buffer(0.0017, cap_style=1, join_style=1)
    q.add('polimero', menos(solido(lam, -0.0035, 0.0035, 0.0008), caixa(0.06, 0.08, -0.04, -0.028, -0.0011, 0.0011)))
    tec = LineString([(0.0688, -0.029), (0.0682, -0.0355), (0.0694, -0.0392)]).buffer(0.0011, cap_style=1, join_style=1)
    q.add('aco_oxidado', solido(tec, -0.0009, 0.0009))


@arma('pistola_9mm', 'Pistola Sentinela 9 mm', 'armas', 'pistola', classe='fogo', calibre='9 mm', municao='municao_9mm',
      capacidade=15, dano=34, alcance_m=25, alcance_max_m=50, modo='semiautomático', tiros_por_s=4.0, recarga_s=1.6, recarga_vazia_s=2.1,
      precisao=0.72, recuo=0.3, ruido_m=60, durabilidade=600, peso_kg=0.78, raridade='incomum', valor_troca=40,
      onde=['quartel', 'correios', 'motel', 'posto', 'casas'],
      descricao='Pistola de polímero com ferrolho de aço quadrado e punho com cavas e pontilhado, 15 tiros. Leve e confiável, mas o tiro chama zumbis num raio de 60 m.')
def pistola_9mm(A):
    A.pivo = (0.006, -0.068, 0.0)            # centro do punho, na altura do dedo medio
    _armacao_pistola(A.base)
    gat = A.parte('gatilho', (0.071, -0.0215, 0), explodir=(0.05, -0.03, 0), tipo='gira', eixo='x', curso_graus=-14, descricao='puxa para tras ao atirar')
    _gatilho_pistola(gat)
    cano = A.parte('cano', (0.0, 0.0, 0.0), explodir=(0.06, 0.07, 0), tipo='desliza', curso_m=0.004, descricao='recua 4 mm com o ferrolho')
    cano.add('aco_cano', menos(uniao([cil_x(0.0068, 0.04, SL_L + 0.0002, sec=32), caixa(0.07, 0.112, -0.0068, 0.0161, -0.0085, 0.0085)]),
                                cil_x(0.0045, 0.03, SL_L + 0.01, sec=24)))
    rosca_x(cano, 'aco_cano', 0.0068, SL_L + 0.0002, SL_L + 0.0122, 0.001)
    cano.add('aco_cano', tubo_x(0.0045, 0.0064, SL_L + 0.0122, SL_L + 0.0132, sec=32))
    cano.add('aco_oxidado', solido(arred([(0.072, 0.0161), (0.11, 0.0161), (0.11, 0.0164), (0.072, 0.0164)], 0.0001), -0.008, 0.008))
    for i, ch in enumerate('9MM'):
        cano.add('aco_inox', caixa(0.08 + i * 0.006, 0.084 + i * 0.006, 0.0161, 0.0166, -0.002, 0.0))
    cano.add('latao', torno_x([(0.0045, 0.06), (0.0045, 0.0715)], 24))      # culote do cartucho na camara (aparece pela janela)
    fer = A.parte('ferrolho', (0.0, 0.0, 0.0), explodir=(-0.04, 0.035, 0), tipo='desliza', curso_m=0.032, descricao='recua 32 mm ao atirar; fica travado atrás com o carregador vazio')
    _ferrolho_pistola(fer)
    car = A.parte('carregador', (0.0215, -0.016, 0.0), explodir=(-0.02, -0.07, 0), tipo='remove', direcao=[round(float(c), 3) for c in rot(MAG_D)],
                  municao='municao_9mm', capacidade=15, descricao='sai pelo fundo do punho ao recarregar')
    _carregador(car, 15)
    A.encaixe('encaixe_mira', (0.042, SL_Y1 - 0.0004, 0), 'mira_ferrolho', pai='ferrolho', explodir=(0, 0.04, 0), aceita=['mira_ponto_vermelho_compacta'],
              exclui=['encaixe_ponte'], descricao='mira no rebaixo do ferrolho (anda com ele); tira a ponte de mira se houver')
    A.encaixe('encaixe_ponte', (0.14, -0.022, 0), 'ponte_pistola', explodir=(0, 0.06, 0), aceita=['ponte_mira_pistola', 'ponte_mira_pistola_tan'],
              exclui=['encaixe_mira'], descricao='ponte presa na armação que passa por cima do ferrolho com a mira de ponto (não anda com o ferrolho)')
    A.encaixe('encaixe_boca', (SL_L + 0.0122, 0, 0), 'boca_rosca_9mm', pai='cano', explodir=(0.06, 0, 0),
              aceita=['protetor_rosca_9mm', 'supressor_9mm', 'supressor_9mm_tan', 'supressor_9mm_verde', 'supressor_9mm_cinza', 'compensador_9mm', 'supressor_garrafa'], padrao='protetor_rosca_9mm')
    A.encaixe('encaixe_trilho', (0.141, -0.0355, 0), 'trilho_curto', explodir=(0.02, -0.05, 0), aceita=['lanterna_pistola', 'laser_pistola', 'combo_lanterna_laser'])
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
            descricao='Tubo longo de alumínio com defletores e reforço com conchas atrás (ajuda a pistola a funcionar com o peso). '
                      'O tiro só é ouvido a 18 m: essencial para não chamar a horda.')
def supressor_9mm(A, mat='aluminio_preto'):
    """Supressor com reforco (pistao) atras: carcaca com recortes em concha e anel recartilhado, tubo longo e tampa da frente
    levemente maior. Atras aparece o colar de latao do pistao."""
    q = A.base; L = 0.168; R = 0.0168; XB = 0.042
    tubo = torno_x([(0.0, XB), (R, XB), (R, L - 0.022), (R + 0.0006, L - 0.021), (R + 0.0006, L - 0.003), (R - 0.0024, L), (0.0, L)], 64)
    q.add(mat, menos(tubo, cil_x(0.0055, XB - 0.01, L + 0.01, sec=24)))
    q.add('aco_oxidado', tubo_x(R - 0.0004, R + 0.0002, L - 0.0215, L - 0.0205, sec=64))                        # junta da tampa
    # reforco: carcaca com 8 conchas, anel recartilhado atras e chanfro
    RB = 0.0175
    reforco = torno_x([(0.0074, 0.0), (RB - 0.0025, 0.0), (RB, 0.0025), (RB, XB - 0.002), (R - 0.001, XB)], 64)
    conchas = []
    for i in range(8):
        a = i * 2 * math.pi / 8
        e = trimesh.creation.icosphere(2, radius=1.0); e.apply_scale([0.0095, 0.0042, 0.0042])
        e.apply_translation([0.026, (RB + 0.0012) * math.cos(a), (RB + 0.0012) * math.sin(a)]); conchas.append(e)
    q.add(mat, menos(reforco, cil_x(0.0069, -0.001, 0.014, sec=32), cil_x(0.0055, -0.01, XB + 0.01, sec=24), *conchas))
    q.add('recartilhado', tubo_x(RB - 0.0003, RB + 0.0005, 0.004, 0.013, sec=64))
    q.add('latao', tubo_x(0.0069, 0.0086, -0.0035, 0.0005, sec=32, ch=0.0004))                                # colar do pistao
    q.add('aco_cano', tubo_x(0.0055, 0.0075, L - 0.0002, L + 0.0008, sec=32))
    for i in range(3):
        a = i * 2 * math.pi / 3; m = cil_z(0.0018, -0.0012, 0.0012, 0, 0, 10)
        m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([L + 0.0005, 0.0105 * math.cos(a), 0.0105 * math.sin(a)])
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
    q = A.base; yl = -0.021; zl = 0.0
    _corpo_rail(q, 'aluminio_preto', -0.042, -0.002)
    # corpo: caixa chanfrada com degrau embaixo (onde fica o laser) e tampa da pilha
    lado = arred([(-0.054, -0.008), (0.004, -0.008), (0.008, -0.011), (0.008, -0.031), (0.002, -0.031), (0.0, -0.039), (-0.03, -0.039),
                  (-0.036, -0.034), (-0.054, -0.034)], 0.0025)
    q.add('aluminio_preto', solido(lado, -0.0138, 0.0138, 0.002))
    q.add('aluminio_preto', solido(arred([(-0.05, -0.012), (-0.012, -0.012), (-0.012, -0.03), (-0.05, -0.03)], 0.002), -0.0146, 0.0146, 0.0006))  # tampas laterais
    for zs in (-1, 1):
        for x in (-0.046, -0.016):
            q.add('aco_inox', cil_z(0.0011, min(zs * 0.0145, zs * 0.0151), max(zs * 0.0145, zs * 0.0151), x, -0.0275, 8))
    # cabeca da lanterna: anel recartilhado, aro e lente
    q.add('aluminio_preto', torno_x([(0.0, 0.006), (0.0118, 0.006), (0.0118, 0.009), (0.0126, 0.011), (0.0126, 0.026), (0.0, 0.026)], 48, yl, zl))
    q.add('recartilhado', tubo_x(0.0124, 0.013, 0.013, 0.024, yl, zl, sec=48))
    q.add('aco_inox', tubo_x(0.0098, 0.0128, 0.0262, 0.0275, yl, zl, sec=48))
    q.add('refletor', torno_x([(0.003, 0.016), (0.0098, 0.026)], 32, yl, zl))
    q.add('led_lanterna', cil_x(0.0028, 0.0158, 0.0166, yl, zl, 16))
    q.add('lente', cil_x(0.0098, 0.0258, 0.0264, yl, zl, 40))
    # laser no degrau de baixo, com etiqueta amarela de aviso dos dois lados
    q.add('aco_inox', tubo_x(0.0018, 0.003, -0.002, 0.0015, -0.035, 0.0, 20)); q.add('lente_laser', cil_x(0.0018, 0.0, 0.0014, -0.035, 0.0, 12))
    for zs in (-1, 1):
        q.add('etiqueta_amarela', caixa(-0.028, -0.018, -0.0375, -0.032, min(zs * 0.0138, zs * 0.0141), max(zs * 0.0138, zs * 0.0141)))
        q.add('aco_oxidado', caixa(-0.0255, -0.0205, -0.0365, -0.0332, min(zs * 0.0141, zs * 0.0142), max(zs * 0.0141, zs * 0.0142)))
        # alavancas ambidestras atras
        q.add('borracha', solido(arred([(-0.062, -0.012), (-0.052, -0.012), (-0.05, -0.026), (-0.06, -0.03)], 0.0015),
                                 min(zs * 0.0105, zs * 0.0148), max(zs * 0.0105, zs * 0.0148), 0.0008))
    q.add('aluminio_preto', cil_z(0.0024, -0.0141, -0.0128, -0.04, -0.016, 16))                                   # parafuso do ajuste
    A.encaixe('feixe', (0.0275, yl, zl), 'efeito', descricao='SpotLight3D aqui (-Z)')
    A.encaixe('laser', (0.0015, -0.035, 0.0), 'efeito', descricao='origem do laser (-Z)')
    A.pivo = (0, 0, 0)


@_acessorio('mira_ponto_vermelho_compacta', 'Mira de ponto vermelho compacta', 'mira', 'mira_ferrolho', peso_kg=0.03, raridade='raro',
            valor_troca=45, usa='pilhas', autonomia_min=3000, modificadores={'precisao_mirando': 1.25, 'tempo_mirar': 0.85},
            onde=['quartel', 'galeria'], linha_de_visada='encaixe "olho": centro da lente, a câmera mira por ali',
            descricao='Mira refletora pequena para o ferrolho da pistola: ponto vermelho, mira mais rápido.')
def mira_ponto_vermelho_compacta(A):
    _mini_ponto(A.base); A.encaixe('olho', (0.0, 0.0145, 0), 'mira', descricao='centro da lente: linha de visada'); A.pivo = (0, 0, 0)


def _mini_ponto(q, mat='aluminio_preto', dx=0.0, dy=0.0):
    """Mira de ponto vermelho pequena: corpo trapezio com capuz de orelhas inclinadas, janela que afina em cima, botao de altura
    em cima e de lado, tampa da pilha embaixo. Origem no centro da base."""
    T = TF.translation_matrix([dx, dy, 0])
    L0, L1 = -0.0175, 0.0165
    lado = arred([(L0, 0.0), (L1, 0.0), (L1, 0.006), (L1 - 0.003, 0.0085), (L1 - 0.009, 0.0245), (L0 + 0.009, 0.0245), (L0 + 0.002, 0.012),
                  (L0, 0.0065)], 0.0012)
    planta = arred([(L0, -0.0105), (L1, -0.0105), (L1, 0.0105), (L0, 0.0105)], 0.002)
    corpo = inter([solido(lado, -0.0112, 0.0112), ext_y(planta, -0.01, 0.04)])
    jan = Polygon([(-0.0085, 0.0072), (0.0085, 0.0072), (0.0062, 0.0212), (-0.0062, 0.0212)]).buffer(0.0012, join_style=1).buffer(-0.0006)
    cortes = [ext_x(jan, -0.003, 0.03), caixa(-0.004, 0.0035, 0.0072, 0.0215, -0.0081, 0.0081)]
    q.add(mat, menos(corpo, *cortes).apply_transform(T))
    lente = ext_x(jan.buffer(0.0003), 0.0, 0.0008); lente.apply_transform(TF.rotation_matrix(math.radians(-8), [0, 0, 1], point=[0, 0.014, 0]))
    q.add('lente', lente.apply_transform(T))
    q.add('ponto_vermelho', caixa(-0.0001, 0.0001, 0.0144, 0.0146, -0.0001, 0.0001).apply_transform(T))
    q.add('recartilhado', menos(_cil_vert(0.0034, 0.0245, 0.0262, -0.0105), caixa(-0.0115, -0.0095, 0.025, 0.03, -0.0006, 0.0006)).apply_transform(T))   # altura
    q.add('recartilhado', menos(cil_z(0.0032, 0.0112, 0.0127, -0.011, 0.014, 20), caixa(-0.0117, -0.0103, 0.012, 0.016, 0.012, 0.014)).apply_transform(T))  # lado
    q.add('borracha', caixa(0.004, 0.012, 0.0022, 0.006, 0.0112, 0.0121).apply_transform(T))                   # botoes de brilho
    q.add('borracha', caixa(0.004, 0.012, 0.0022, 0.006, -0.0121, -0.0112).apply_transform(T))
    q.add('aco_inox', cil_z(0.0012, -0.0113, -0.0108, L0 + 0.004, 0.003, 8).apply_transform(T))


def _cil_vert(r, y0, y1, x=0.0, z=0.0, sec=24):
    m = trimesh.creation.cylinder(radius=r, height=y1 - y0, sections=sec); m.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0]))
    m.apply_translation([x, (y0 + y1) / 2, z]); return m


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


PXM = 4096                                     # atlas das caixas: 1024 px = 0,25 m
ATLAS = {'topo': (0, 0), 'lado+': (0, 380), 'lado-': (0, 520), 'ponta+': (500, 380), 'ponta-': (500, 520)}


def _arte_caixa(CX, cal, linha2, linha3, cor=(150, 30, 20), marca='GUARDIÃO', tampa=0.012, atlas=None):
    """Arte original da caixa (marca inventada). Cada face tem o seu retangulo no atlas, na mesma densidade."""
    ATLAS = atlas or globals()['ATLAS']
    im = Image.new('RGB', (1024, 1024), (236, 230, 212)); d = ImageDraw.Draw(im)
    L = int((CX['x1'] - CX['x0']) * PXM); P_ = int((CX['z1'] - CX['z0']) * PXM); H = int((CX['y1'] - CX['y0']) * PXM)
    tp = int(tampa * PXM); vis = (tp + H) // 2                            # centro da parte do lado que a tampa nao cobre
    x, y = ATLAS['topo']
    d.rectangle([x, y, x + 120, y + P_], fill=cor)
    texto_c(d, (x + 60, y + P_ // 2), cal.split()[0], 64, (250, 240, 220), larg=104)
    cx = x + 120 + (L - 120) // 2
    texto_c(d, (cx, y + 80), marca, 58, cor, larg=L - 150); texto_c(d, (cx, y + 160), cal, 80, (40, 30, 26), larg=L - 150)
    texto_c(d, (cx, y + 240), linha2, 36, (40, 30, 26), larg=L - 150); texto_c(d, (cx, y + 290), linha3, 24, (90, 70, 60), False, larg=L - 150)
    d.rectangle([x + 130, y + P_ - 30, x + L - 10, y + P_ - 14], fill=(40, 40, 44))
    for k in ('lado+', 'lado-'):
        x, y = ATLAS[k]; d.rectangle([x, y, x + L, y + H], fill=cor)
        texto_c(d, (x + L // 2, y + vis - 14), f'{marca}  {cal}', 34, (250, 240, 220), larg=L - 40)
        texto_c(d, (x + L // 2, y + vis + 20), 'MANTENHA LONGE DE CRIANÇAS' if k == 'lado+' else 'LOTE 0815 · ' + linha2, 17, (240, 220, 200), False, larg=L - 40)
    for k in ('ponta+', 'ponta-'):
        x, y = ATLAS[k]; d.rectangle([x, y, x + P_, y + H], fill=(236, 230, 212)); d.rectangle([x, y, x + P_, y + 22], fill=cor)
        texto_c(d, (x + P_ // 2, y + vis), cal, 34, (40, 30, 26), larg=P_ - 30)
    return im


def _uv_caixa(CX, atlas=None):
    ATLAS = atlas or globals()['ATLAS']
    def f(v, n):
        uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1); sg = np.sign(n[np.arange(len(n)), ax])
        X = v[:, 0] - CX['x0']; Y = CX['y1'] - v[:, 1]; Z = v[:, 2] - CX['z0']
        def put(m, chave, a, b):
            x, y = ATLAS[chave]; uv[m] = np.stack([(x + a[m] * PXM) / 1024, (y + b[m] * PXM) / 1024], 1)
        put(ax == 1, 'topo', X, Z)
        put((ax == 2) & (sg > 0), 'lado+', X, Y); put((ax == 2) & (sg < 0), 'lado-', (CX['x1'] - CX['x0']) - X, Y)
        put((ax == 0) & (sg > 0), 'ponta+', (CX['z1'] - CX['z0']) - Z, Y); put((ax == 0) & (sg < 0), 'ponta-', Z, Y)
        uv[:, 1] = 1 - uv[:, 1]
        return uv
    return f


def caixa_municao(A, mat, CX, arte, cart, nx, nz, passo_x, passo_z, faltam=(7, 23, 24), bandeja=0.012, atlas=None):
    """Caixa de papelao aberta em cima, bandeja com nx x nz cartuchos de pe (cart = Piece deitada em x, base em x=0) e tampa animada."""
    mat_imagem(mat, arte, 0.7)
    x0, x1, y0, y1, z0, z1 = (CX[k] for k in ('x0', 'x1', 'y0', 'y1', 'z0', 'z1')); t = 0.0012; yt = y1 - 0.006
    q = A.base; uvf = _uv_caixa(CX, atlas)
    q.add(mat, menos(caixa(x0, x1, y0, yt, z0, z1), caixa(x0 + t, x1 - t, y0 + t, yt + 0.01, z0 + t, z1 - t))); q.uv[mat] = uvf
    q.add('papelao', caixa(x0 + t, x1 - t, y0 + t, y0 + t + 0.0008, z0 + t, z1 - t))
    q.add('plastico_branco', caixa(x0 + t, x1 - t, yt - bandeja, yt - bandeja + 0.0015, z0 + t, z1 - t))       # bandeja
    Rv = TF.rotation_matrix(math.pi / 2, [0, 0, 1])
    ax0 = (x0 + x1) / 2 - (nx - 1) * passo_x / 2; az0 = (z0 + z1) / 2 - (nz - 1) * passo_z / 2
    for i in range(nx):
        for j in range(nz):
            if (i * nz + j) in faltam: continue                                                         # alguns ja usados
            q.merge(cart, TF.translation_matrix([ax0 + i * passo_x, y0 + t + 0.0013, az0 + j * passo_z]) @ Rv)
    tampa = A.parte('tampa', (x0 - 0.0008, yt, 0), explodir=(0, 0.05, 0), tipo='tampa', eixo='z', abre_graus=115, descricao='gira em torno da ponta de trás')
    e = 0.0008; hs = 0.012
    tampa.add(mat, caixa(x0 - e, x1 + e, y1 - 0.0006, y1 + 0.0002, z0 - e, z1 + e)); tampa.uv[mat] = uvf
    tampa.add('papelao', menos(caixa(x0 - e, x1 + e, y1 - hs, y1 - 0.0006, z0 - e, z1 + e), caixa(x0, x1, y1 - hs - 0.01, y1 - 0.0014, z0, z1)))
    A.anim('abrir', 0.6, [('tampa', 'r', (0, 0, 1), pose([(0, 0), (0.6, 115)]))], desc='abre a tampa')
    A.anim('fechar', 0.6, [('tampa', 'r', (0, 0, 1), pose([(0, 115), (0.6, 0)]))], desc='fecha a tampa')
    A.pivo = (0, 0, 0)


CX9 = dict(x0=-0.058, x1=0.058, y0=0.0, y1=0.034, z0=-0.044, z1=0.044)


@arma('caixa_municao_9mm', 'Caixa de munição 9 mm (50)', 'municao', 'caixa', calibre='9 mm', municao='municao_9mm', quantidade=50,
      peso_kg=0.62, empilha=4, raridade='incomum', onde=['quartel', 'correios', 'motel', 'casas', 'posto'],
      descricao='Caixa de papelão com bandeja de 50 cartuchos. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_9mm(A):
    caixa_municao(A, 'rotulo_9mm', CX9, _arte_caixa(CX9, '9 mm', '50 CARTUCHOS', 'PONTA OGIVAL 124 gr'), _cartucho_9mm_malha(12),
                  10, 5, 0.01116, 0.0171)


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


# ============================================================================ armas seguintes (props/armas/arma02_*.py ...)
import glob as _glob
for _f in sorted(_glob.glob(os.path.join(AQUI, 'arma[0-9][0-9]_*.py'))):
    exec(compile(open(_f, encoding='utf-8').read(), _f, 'exec'), globals())


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
NOMES = {'rifle': 'Rifles', 'arco': 'Arcos', 'estabilizador': 'Estabilizadores', 'aljava': 'Aljavas', 'soltador': 'Soltadores', 'punho': 'Punhos', 'enfeite': 'Enfeites', 'guarda_mao': 'Guarda-mãos', 'tampa': 'Tampas', 'baioneta': 'Baionetas', 'fuzil': 'Fuzis', 'laser': 'Lasers', 'carabina': 'Carabinas', 'bipe': 'Bipés', 'espingarda': 'Espingardas', 'coronha': 'Coronhas', 'tubo': 'Tubo do carregador', 'lanterna': 'Lanternas', 'porta_cartuchos': 'Porta-cartuchos', 'bandoleira': 'Bandoleiras', 'revolver': 'Revólveres', 'recarga': 'Recarga rápida', 'empunhadura': 'Empunhaduras', 'coldre': 'Coldres', 'pistola': 'Pistolas', 'boca': 'Boca do cano', 'trilho': 'Trilho', 'mira': 'Miras', 'carregador': 'Carregadores',
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
