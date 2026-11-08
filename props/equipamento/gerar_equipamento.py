"""Gerador dos EQUIPAMENTOS VESTIVEIS do Recomeco: capacetes, coletes e coletes taticos (arte original, por script).

Uso:  python props/equipamento/gerar_equipamento.py                  (gera tudo)
      python props/equipamento/gerar_equipamento.py capacete_obra    (so os ids pedidos)

Saida: props/equipamento/<id>.glb, catalogo.json e CATALOGO.md.
Reaproveita as primitivas e os materiais de props/gerar_props.py (lotes 1 a 17) e o padrao de alto detalhe de scripts/detalhe.

Convencoes (ver README.md):
  Y para cima, 1 unidade = 1 m, frente do equipamento para +Z (como quem veste olha para +Z).
  Capacetes ficam em pe, apoiados na borda (como achados numa prateleira); pivo no centro da base.
  Coletes ficam DEITADOS DE COSTAS no chao (frente para cima, gola para -Z): a foto de cima (icone) mostra a frente com as bolsas.
  "vestir" no catalogo diz como por no personagem: girar_graus (XYZ, graus) e o ponto do corpo (cabeca ou peito) no GLB.
  Viseiras sao nos separados com origem no eixo, descritos em "partes" (tipo gira, eixo, abre_graus), como as portas das mobilias.
"""
import os, sys, math, json
AQUI = os.path.dirname(os.path.abspath(__file__))
PROPS = os.path.dirname(AQUI)
sys.path.insert(0, PROPS)
import gerar_props as G
from gerar_props import *                     # P, torno, anel, fofo, varrer, circ, cyl_eixo, trimesh, np, Polygon, GT...
from scipy.interpolate import CubicSpline
AQUI = os.path.dirname(os.path.abspath(__file__))   # (o import * acima traz o AQUI de props/)
import shapely
from shapely.geometry import Polygon as SPoly, box as sbox, Point as SPoint
TF = trimesh.transformations


def lin(c):
    """Cor sRGB (0-255) -> valor linear (0-255) para materiais sem textura (baseColorFactor e linear)."""
    return tuple(int(round(255 * (v / 255) ** 2.2)) for v in c)


# ============================================================================ materiais
# Com textura (cor em sRGB, vai para a imagem): tecidos (cordura), malha, camuflado, tinta granulada dos cascos.
CORES_TEX = {
    'cordura_coiote': (150, 124, 88), 'cordura_verde': (84, 90, 68), 'cordura_preta': (46, 46, 48), 'cordura_marinho': (40, 46, 64),
    'cordura_caqui': (176, 160, 122), 'camo_mata': (118, 112, 82), 'malha_preta': (40, 40, 42), 'malha_caqui': (150, 138, 104),
    'malha_coiote': (140, 116, 82), 'velcro_coiote': (138, 114, 80), 'velcro_preto': (40, 40, 42), 'velcro_marinho': (36, 42, 58),
    'velcro_verde': (78, 84, 62), 'forro_preto': (34, 34, 36), 'forro_cinza': (78, 80, 84), 'espuma_cinza': (96, 98, 100),
    'tinta_casco_coiote': (138, 118, 88), 'tinta_casco_verde': (80, 86, 66), 'tinta_casco_preta': (38, 40, 42),
    'elastico_preto': (30, 30, 32), 'fita_cinza': (110, 112, 114),
}
TIPO_TEX = {k: 'tecido' for k in CORES_TEX}
TIPO_TEX.update({'camo_mata': 'camo', 'malha_preta': 'malha', 'malha_caqui': 'malha', 'malha_coiote': 'malha',
                 'velcro_coiote': 'velcro', 'velcro_preto': 'velcro', 'velcro_marinho': 'velcro', 'velcro_verde': 'velcro',
                 'espuma_cinza': 'espuma', 'tinta_casco_coiote': 'granulado', 'tinta_casco_verde': 'granulado',
                 'tinta_casco_preta': 'granulado', 'elastico_preto': 'elastico'})
LADRILHO = {'tecido': (0.25, 1024), 'camo': (0.4, 768), 'malha': (0.12, 1536), 'velcro': (0.1, 1024), 'espuma': (0.2, 768),
            'granulado': (0.25, 1024), 'elastico': (0.08, 1024)}
CAMO = {'camo_mata': [(70, 84, 52), (140, 118, 84), (44, 42, 34)]}

# Sem textura (cor ja em linear): plasticos dos cascos, viseiras, ferragens.
CORES_LISAS = {
    'abs_amarelo': lin((236, 184, 22)), 'abs_branco': lin((236, 236, 230)), 'abs_laranja': lin((232, 104, 24)),
    'pc_vermelho': lin((168, 22, 20)), 'pc_preto': lin((26, 26, 28)), 'pc_grafite': lin((70, 72, 76)), 'pc_azul': lin((26, 60, 140)),
    'eps': lin((196, 196, 190)), 'eps_preto': lin((40, 40, 42)), 'nylon_preto': lin((34, 34, 36)), 'nylon_coiote': lin((128, 106, 76)),
    'nylon_verde': lin((70, 76, 58)), 'aluminio_escuro': lin((60, 62, 66)), 'refletivo': lin((200, 204, 206)),
    'borracha_viseira': lin((22, 22, 24)), 'costura_escura': lin((30, 28, 24)), 'costura_clara': lin((200, 190, 160)),
    'ceramica_placa': lin((60, 62, 60)), 'cromado': lin((210, 212, 216)), 'adesivo_branco': lin((236, 236, 232)),
    'polimero_mag': lin((36, 36, 38)), 'polimero_mag_coiote': lin((150, 124, 86)), 'latao_ilhos': lin((170, 140, 70)),
    'lente_vermelha': lin((160, 10, 8)), 'marcador_vermelho': lin((140, 20, 18)),
}
METAL_EQ = {'aluminio_escuro': (0.8, 0.4), 'refletivo': (0.6, 0.28), 'cromado': (0.95, 0.12), 'latao_ilhos': (0.85, 0.35)}
RUGOSO_EQ = {'abs_amarelo': 0.38, 'abs_branco': 0.38, 'abs_laranja': 0.4, 'pc_vermelho': 0.22, 'pc_preto': 0.25, 'pc_grafite': 0.5,
             'pc_azul': 0.24, 'eps': 0.85, 'eps_preto': 0.8, 'nylon_preto': 0.6, 'nylon_coiote': 0.62, 'nylon_verde': 0.62,
             'borracha_viseira': 0.8, 'costura_escura': 0.9, 'costura_clara': 0.9, 'ceramica_placa': 0.7, 'adesivo_branco': 0.5,
             'polimero_mag': 0.55, 'polimero_mag_coiote': 0.6, 'lente_vermelha': 0.3, 'marcador_vermelho': 0.6}
TRANSP_EQ = {'viseira_clara': ((214, 226, 232), 0.22, 0.04), 'viseira_fume': ((34, 40, 48), 0.72, 0.05),
             'viseira_ambar': ((200, 130, 40), 0.4, 0.06)}


def _tex_eq(col, seed, px, tile, kind):
    """Texturas dos equipamentos (mesmo formato de gerar_props._ruido_tex)."""
    n = int(tile * px); c = GT.rgb(col)[None, None]
    yy, xx = np.mgrid[0:n, 0:n] / px
    f = GT.fbm(n, n, 0.03 * px, 3, seed + 1); g = GT.noise(n, n, 0.0015 * px, 0.0015 * px, seed + 2)
    trama = lambda per: 0.5 + 0.5 * np.sin(xx * 2 * np.pi / per) * np.sin(yy * 2 * np.pi / per)
    if kind == 'tecido':                       # cordura 500D: trama cruzada fina + manchas suaves
        w = trama(0.0011)
        alb = c * (0.9 + 0.08 * w[..., None] + 0.04 * g[..., None] + 0.025 * f[..., None])
        return alb, 0.00012 * w + 0.0002 * f, 0.88 + 0.06 * f, 0.9, 0.0005
    if kind == 'camo':                         # manchas organicas em 3 cores sobre a base, com a trama por cima
        alb = c * np.ones((n, n, 1))
        for i, cc in enumerate(CAMO_ATUAL):
            m = GT.smooth(0.44, 0.5, GT.fbm(n, n, (0.03 - 0.005 * i) * px, 4, seed + 11 * (i + 1)) * 0.25 + 0.5)
            alb = GT.lerp(alb, GT.rgb(cc)[None, None] * np.ones((n, n, 1)), m[..., None])
        w = trama(0.0011)
        alb = alb * (0.92 + 0.07 * w[..., None] + 0.03 * g[..., None])
        return alb, 0.00012 * w + 0.0002 * f, 0.9 + 0.05 * f, 0.9, 0.0005
    if kind == 'malha':                        # tela de malha (furos hexagonais em fileiras desencontradas)
        per = 0.006; lin_ = np.floor(yy / (per * 0.87)); ox = (lin_ % 2) * per / 2
        dx = ((xx + ox) % per) / per - 0.5; dy = (yy % (per * 0.87)) / (per * 0.87) - 0.5
        furo = GT.smooth(0.3, 0.2, np.sqrt(dx * dx + dy * dy))
        alb = c * (0.95 + 0.05 * g[..., None]) * (1 - 0.75 * furo[..., None])
        return alb, -0.0006 * furo + 0.0001 * g, 0.9 - 0.1 * furo, 1.2, 0.0012
    if kind == 'velcro':                       # felpa do velcro (painel de remendos): ruido fino e fosco
        h = GT.noise(n, n, 0.0006 * px, 0.0006 * px, seed + 4)
        alb = c * (0.88 + 0.12 * h[..., None])
        return alb, 0.00025 * h, 0.97 + 0.02 * h, 1.0, 0.0008
    if kind == 'espuma':                       # espuma de alta densidade (almofadas internas)
        h = GT.noise(n, n, 0.0012 * px, 0.0012 * px, seed + 6)
        alb = c * (0.9 + 0.1 * h[..., None])
        return alb, 0.0003 * h, 0.95 + 0 * h, 0.8, 0.0008
    if kind == 'granulado':                    # tinta tatica de casco (textura de areia)
        h = GT.noise(n, n, 0.0009 * px, 0.0009 * px, seed + 8)
        alb = c * (0.93 + 0.06 * h[..., None] + 0.02 * f[..., None])
        return alb, 0.00008 * h + 0.00004 * f, 0.72 + 0.08 * h, 0.7, 0.0004
    if kind == 'elastico':                     # cordao elastico / fita trancada
        w = 0.5 + 0.5 * np.sin((xx + yy) * 2 * np.pi / 0.002)
        alb = c * (0.85 + 0.15 * w[..., None])
        return alb, 0.0002 * w, 0.8 + 0.1 * w, 1.0, 0.0005
    raise ValueError(kind)


CAMO_ATUAL = []


def materiais_eq():
    G.CORES.update(CORES_LISAS); G.CORES.update(CORES_TEX)
    G.METALICOS.update(METAL_EQ); G.FOSCOS.update(RUGOSO_EQ); G.TRANSP.update(TRANSP_EQ)
    G.materiais()
    for i, (k, kind) in enumerate(TIPO_TEX.items()):
        tile, px = LADRILHO[kind]
        CAMO_ATUAL[:] = CAMO.get(k, [])
        a, nm, o = tex_set(*_tex_eq(CORES_TEX[k], 311 + 13 * i, px, tile, kind), px)
        TEX[k] = (a, nm, o); G.UV_ESCALA[k] = tile
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)
    for k in TRANSP_EQ: MATS[k].doubleSided = True


# ============================================================================ geometria base
def sp(w, e): return np.sign(w) * np.abs(w) ** e


def nrm(v):
    v = np.asarray(v, float); return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def malha(v, f, fix=True):
    m = trimesh.Trimesh(np.asarray(v, float), np.asarray(f, np.int64), process=True)
    if fix:
        trimesh.repair.fix_winding(m); trimesh.repair.fix_normals(m)
    return m


def grade_faces(nu, nv, fecha_u=False, base=0):
    """Faces de uma grade nu x nv (indice = base + i*nv + j); fecha_u liga a ultima coluna na primeira."""
    F = []
    iu = nu if fecha_u else nu - 1
    for i in range(iu):
        i2 = (i + 1) % nu
        for j in range(nv - 1):
            a = base + i * nv + j; b = base + i2 * nv + j; c = base + i2 * nv + j + 1; d = base + i * nv + j + 1
            F += [(a, b, c), (a, c, d)]
    return F


def laje(fn, U, V, k0, k1):
    """Placa curva fechada: fn(u, v, k) -> pontos (N,3) da superficie com afastamento k. Grade U x V, espessura de k0 a k1."""
    U = np.asarray(U, float); V = np.asarray(V, float); nu, nv = len(U), len(V)
    uu, vv = np.meshgrid(U, V, indexing='ij'); uu = uu.ravel(); vv = vv.ravel()
    k0a = np.broadcast_to(np.asarray(k0, float), (nu, nv)).ravel() if np.ndim(k0) else np.full(nu * nv, float(k0))
    k1a = np.broadcast_to(np.asarray(k1, float), (nu, nv)).ravel() if np.ndim(k1) else np.full(nu * nv, float(k1))
    top = fn(uu, vv, k1a); bot = fn(uu, vv, k0a)
    v = np.concatenate([top, bot]); n = nu * nv
    F = grade_faces(nu, nv) + [(c, b, a) for a, b, c in grade_faces(nu, nv, base=n)]
    idx = lambda i, j, L: L * n + i * nv + j
    borda = [(i, 0) for i in range(nu)] + [(nu - 1, j) for j in range(1, nv)] + [(i, nv - 1) for i in range(nu - 2, -1, -1)] + [(0, j) for j in range(nv - 2, 0, -1)]
    for q in range(len(borda)):
        (i, j), (i2, j2) = borda[q], borda[(q + 1) % len(borda)]
        a, b, c, d = idx(i, j, 0), idx(i2, j2, 0), idx(i2, j2, 1), idx(i, j, 1)
        F += [(a, c, b), (a, d, c)]
    return malha(v, F)


def fita(pts, normais, w, t, canto=0.35, lat=None, fechada=False):
    """Fita de secao retangular arredondada ao longo de pts; espessura para o lado de normais (base em pts).
    lat: direcao da largura (opcional; senao = T x N). fechada: liga o fim ao comeco (aro)."""
    P_ = np.asarray(pts, float); N = nrm(normais)
    if fechada: T = nrm(np.roll(P_, -1, 0) - np.roll(P_, 1, 0))
    else: T = nrm(np.gradient(P_, axis=0))
    L = nrm(np.cross(T, N)) if lat is None else nrm(lat)
    N = nrm(np.cross(L, T)) * np.sign(np.sum(np.cross(L, T) * N, axis=1, keepdims=True) + 1e-9)
    c = min(w, t) * canto
    sec = [(w / 2, c), (w / 2, t - c), (w / 2 - c, t), (-w / 2 + c, t), (-w / 2, t - c), (-w / 2, c), (-w / 2 + c, 0), (w / 2 - c, 0)]
    ns = len(sec); m = len(P_)
    v = np.concatenate([P_ + l * L + d * N for l, d in sec], axis=0)       # bloco por ponto da secao
    v = v.reshape(ns, m, 3).transpose(1, 0, 2).reshape(-1, 3)               # indice = i*ns + s
    F = []
    rng = m if fechada else m - 1
    for i in range(rng):
        i2 = (i + 1) % m
        for s in range(ns):
            s2 = (s + 1) % ns
            a, b, cc, d = i * ns + s, i * ns + s2, i2 * ns + s2, i2 * ns + s
            F += [(a, b, cc), (a, cc, d)]
    if not fechada:
        v = np.concatenate([v, [P_[0] + N[0] * t / 2], [P_[-1] + N[-1] * t / 2]])
        c0, c1 = len(v) - 2, len(v) - 1
        for s in range(ns):
            s2 = (s + 1) % ns
            F += [(c0, s2, s), (c1, (m - 1) * ns + s, (m - 1) * ns + s2)]
    return malha(v, F)


def tubo(pts, r, sec=10, fechada=False):
    """Cordao (secao redonda) ao longo de pts."""
    P_ = np.asarray(pts, float)
    T = nrm((np.roll(P_, -1, 0) - np.roll(P_, 1, 0)) if fechada else np.gradient(P_, axis=0))
    ref = np.where(np.abs(T[:, [1]]) < 0.9, [[0, 1, 0]], [[1, 0, 0]])
    A = nrm(np.cross(T, ref)); B = np.cross(T, A)
    ang = np.linspace(0, 2 * np.pi, sec, endpoint=False)
    v = np.concatenate([P_ + r * (math.cos(a) * A + math.sin(a) * B) for a in ang]).reshape(sec, -1, 3).transpose(1, 0, 2).reshape(-1, 3)
    m = len(P_); F = []
    for i in range(m if fechada else m - 1):
        i2 = (i + 1) % m
        for s in range(sec):
            s2 = (s + 1) % sec; F += [(i * sec + s, i * sec + s2, i2 * sec + s2), (i * sec + s, i2 * sec + s2, i2 * sec + s)]
    if not fechada:
        v = np.concatenate([v, [P_[0]], [P_[-1]]]); c0, c1 = len(v) - 2, len(v) - 1
        for s in range(sec):
            s2 = (s + 1) % sec; F += [(c0, s2, s), (c1, (m - 1) * sec + s, (m - 1) * sec + s2)]
    return malha(v, F)


def curva(pts, n=40):
    """Spline suave (Catmull-Rom via CubicSpline por comprimento) passando pelos pontos."""
    P_ = np.asarray(pts, float); d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P_, axis=0), axis=1))])
    cs = CubicSpline(d, P_, axis=0, bc_type='natural'); return cs(np.linspace(0, d[-1], n))


def quadro(o, z, y=(0, 1, 0)):
    """Matriz 4x4: origem o, eixo z = normal, y o mais perto possivel de y pedido."""
    z = nrm(z); x = nrm(np.cross(y, z)); y = np.cross(z, x)
    M4 = np.eye(4); M4[:3, 0] = x; M4[:3, 1] = y; M4[:3, 2] = z; M4[:3, 3] = o; return M4


def _limpa(m):
    m.update_faces(m.nondegenerate_faces(height=1e-7)); m.remove_unreferenced_vertices(); return m


def menos(a, *bs):
    return _limpa(trimesh.boolean.difference([a] + list(bs), engine='manifold'))


def inter(a, b):
    return _limpa(trimesh.boolean.intersection([a, b], engine='manifold'))


def elipsoide(c, a, b, cc, e1=1.0, e2=1.0, n=(24, 32)):
    q = P(); fofo(q, 'x', c[0], c[1], c[2], a, b, cc, e1, e2, n); return q.parts['x'][0]


# ---------------------------------------------------------------------------- casco (capacetes)
class Casco:
    """Superelipsoide do casco: semi-eixos a (x), b (y, para cima), c (z), centro (0, y0, z0); e < 1 = mais quadrado.
    pt(th, al, k): th = azimute (0 = frente +Z, +pi/2 = lado +X), al = elevacao (pi/2 = topo), k = afastamento para fora."""
    def __init__(s, a, b, c, y0=0.0, z0=0.0, e=0.9, e2=1.0):
        s.a, s.b, s.c, s.y0, s.z0, s.e, s.e2 = a, b, c, y0, z0, e, e2
    def pt(s, th, al, k=0.0):
        th, al, k = np.broadcast_arrays(np.asarray(th, float), np.asarray(al, float), np.asarray(k, float))
        C = sp(np.cos(al), s.e); S = sp(np.sin(al), s.e)
        x = (s.a + k) * C * sp(np.sin(th), s.e2); y = s.y0 + (s.b + k) * S; z = s.z0 + (s.c + k) * C * sp(np.cos(th), s.e2)
        return np.stack([x, y, z], -1)
    def normal(s, th, al):
        d = 1e-3; p0 = s.pt(th, al, 0.0); return nrm(s.pt(th, al, d) - p0)
    def quadro(s, th, al, k=0.0):
        """Frame no casco: z = normal, y = subindo pela superficie."""
        o = s.pt(th, al, k); n = s.normal(th, al); up = nrm(s.pt(th, al + 0.01, k) - s.pt(th, al - 0.01, k))
        return quadro(o, n, up)
    def casca(s, borda, t, nth=144, nal=34, k=0.0):
        """Casca fechada (borda -> topo) com espessura t para dentro. borda(th) = elevacao da borda (rad)."""
        th = np.linspace(0, 2 * np.pi, nth, endpoint=False); ab = np.asarray(borda(th), float)
        fr = np.linspace(0, 1, nal + 1)[:-1]; fr = 1 - (1 - fr) ** 1.25                 # mais aneis perto da borda
        al = ab[:, None] + (np.pi / 2 - ab[:, None]) * fr[None, :]
        O = s.pt(th[:, None], al, k).reshape(-1, 3); I = s.pt(th[:, None], al, k - t).reshape(-1, 3)
        n = nth * nal; v = np.concatenate([O, I, s.pt(0, np.pi / 2, k)[None], s.pt(0, np.pi / 2, k - t)[None]])
        F = grade_faces(nth, nal, fecha_u=True) + [(c, b, a) for a, b, c in grade_faces(nth, nal, fecha_u=True, base=n)]
        for i in range(nth):
            i2 = (i + 1) % nth
            F += [(i * nal, n + i * nal, n + i2 * nal), (i * nal, n + i2 * nal, i2 * nal)]                 # borda
            F += [(i * nal + nal - 1, i2 * nal + nal - 1, 2 * n), (n + i * nal + nal - 1, 2 * n + 1, n + i2 * nal + nal - 1)]   # topo
        return malha(v, F)
    def aro(s, borda, w, t, k=0.0, th0=0.0, th1=2 * np.pi, n=160, fechada=True):
        """Pontos e normais ao longo da borda (para frisos de borracha)."""
        th = np.linspace(th0, th1, n, endpoint=not fechada); al = np.asarray(borda(th), float)
        return s.pt(th, al, k), s.normal(th, al)


def superficie(s, k=0.0, nth=720, nal=360):
    """Grade densa de pontos do casco (para achar onde uma linha reta encontra a superficie)."""
    th, al = np.meshgrid(np.linspace(-np.pi, np.pi, nth), np.linspace(-1.2, np.pi / 2, nal), indexing='ij')
    return th.ravel(), al.ravel(), s.pt(th.ravel(), al.ravel(), k)


def no_casco(s, alvo, eixos=(0, 2), k=0.0, lado_max=1, cache={}):
    """Para cada ponto alvo (so as coordenadas 'eixos' contam), o (th, al) do casco mais perto, pegando o lado de maior coordenada restante."""
    chave = (id(s), k)
    if chave not in cache: cache[chave] = superficie(s, k)
    th, al, P_ = cache[chave]; from scipy.spatial import cKDTree
    livre = [i for i in range(3) if i not in eixos][0]
    out = []
    for a in np.atleast_2d(alvo):
        d = np.hypot(P_[:, eixos[0]] - a[0], P_[:, eixos[1]] - a[1]); idx = np.argsort(d)[:40]
        j = idx[np.argmax(lado_max * P_[idx, livre])]; out.append((th[j], al[j]))
    return np.array(out)


def borda_suave(pontos):
    """Elevacao da borda por azimute a partir de [(th, al), ...] de 0 a pi (espelhado para o outro lado), periodica."""
    th = [p[0] for p in pontos]; al = [p[1] for p in pontos]
    TH = np.array([-x for x in th[::-1][:-1]] + th[:-1]); AL = np.array(al[::-1][:-1] + al[:-1])   # de -pi ate antes de +pi
    TH = np.concatenate([TH, [TH[0] + 2 * np.pi]]); AL = np.concatenate([AL, [AL[0]]])
    cs = CubicSpline(TH, AL, bc_type='periodic')
    return lambda t: cs(((np.asarray(t) + np.pi) % (2 * np.pi)) - np.pi)


# ---------------------------------------------------------------------------- tronco (coletes)
class Tronco:
    """Secao do tronco em superelipse (meia largura A em x, meia profundidade B em z, expoente n), y = 0 na barra do colete.
    u = comprimento de arco a partir do centro da frente (positivo para +X), pt(u, y, k) com k para fora (pela normal)."""
    def __init__(s, A=0.168, B=0.118, n=2.7, afina=0.07, y_cheio=0.3):
        s.A, s.B, s.n, s.afina, s.yc = A, B, n, afina, y_cheio
        phi = np.linspace(-np.pi, np.pi, 1441)
        x = A * sp(np.sin(phi), 2 / n); z = B * sp(np.cos(phi), 2 / n)
        d = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(z)))])
        s.Ptot = d[-1]; d = d - np.interp(0, phi, d)
        tx, tz = np.gradient(x), np.gradient(z); nn = nrm(np.stack([-tz, tx], 1))
        if nn[720, 1] < 0: nn = -nn
        s._u, s._x, s._z, s._nx, s._nz = d, x, z, nn[:, 0], nn[:, 1]
    def esc(s, y): return 1 - s.afina * (1 - np.clip(np.asarray(y, float) / s.yc, 0, 1))
    def pt(s, u, y, k=0.0):
        u, y, k = np.broadcast_arrays(np.asarray(u, float), np.asarray(y, float), np.asarray(k, float))
        uu = ((u - s._u[0]) % s.Ptot) + s._u[0]
        x = np.interp(uu, s._u, s._x); z = np.interp(uu, s._u, s._z); nx = np.interp(uu, s._u, s._nx); nz = np.interp(uu, s._u, s._nz)
        e = s.esc(y); return np.stack([x * e + nx * k, y, z * e + nz * k], -1)
    def normal(s, u):
        uu = ((np.asarray(u, float) - s._u[0]) % s.Ptot) + s._u[0]
        return nrm(np.stack([np.interp(uu, s._u, s._nx), np.zeros_like(uu), np.interp(uu, s._u, s._nz)], -1))
    def quadro(s, u, y, k=0.0):
        return quadro(s.pt(u, y, k), s.normal(u))
    def costas(s): return s.Ptot / 2       # u do centro das costas


def painel(corpo, poly, k0, t, infla=0.0, raio=0.035, passo=0.012, ini=None):
    """Painel acolchoado curvo: poligono shapely em (u, y) com espessura de k0 a k0+t sobre o corpo (Tronco ou funcao).
    infla: quanto a face de fora estufa no meio (almofada); raio: distancia da borda ate estufar tudo.
    Malha: pontos em grade dentro do poligono + borda reamostrada, Delaunay; paredes laterais pela borda."""
    from scipy.spatial import Delaunay
    poly = poly if poly.geom_type == 'Polygon' else max(poly.geoms, key=lambda g: g.area)
    anel_ = poly.exterior; L = anel_.length; nb = max(12, int(L / (passo * 0.7)))
    bd = np.array([anel_.interpolate(x).coords[0] for x in np.linspace(0, L, nb, endpoint=False)])
    x0, y0, x1, y1 = poly.bounds
    gx, gy = np.meshgrid(np.arange(x0, x1, passo) + passo / 2, np.arange(y0, y1, passo * 0.866) + passo / 2)
    gx = gx + (np.arange(gx.shape[0])[:, None] % 2) * passo / 2
    gp = np.stack([gx.ravel(), gy.ravel()], 1)
    dentro = shapely.contains(poly.buffer(-passo * 0.45), shapely.points(gp)); gp = gp[dentro]
    pts2 = np.concatenate([bd, gp]); tri = Delaunay(pts2).simplices
    cen = pts2[tri].mean(1); tri = tri[shapely.contains(poly, shapely.points(cen))]
    n = len(pts2); fn = corpo.pt if hasattr(corpo, 'pt') else corpo
    alt = np.full(n, float(t))
    if infla > 0: alt += infla * GT.smooth(0, raio, shapely.distance(anel_, shapely.points(pts2)))
    top = fn(pts2[:, 0], pts2[:, 1], k0 + alt); bot = fn(pts2[:, 0], pts2[:, 1], np.full(n, float(k0)))
    F = [tuple(f) for f in tri] + [(c + n, b + n, a + n) for a, b, c in tri]
    for q in range(nb):
        a, b = q, (q + 1) % nb; F += [(a, b + n, b), (a, a + n, b + n)]
    return malha(np.concatenate([top, bot]), F)


def ret_arred(u0, u1, y0, y1, r=0.02, n=6):
    """Retangulo de cantos arredondados (shapely)."""
    r = min(r, (u1 - u0) / 2.01, (y1 - y0) / 2.01)
    return sbox(u0 + r, y0 + r, u1 - r, y1 - r).buffer(r, quad_segs=n)


# ---------------------------------------------------------------------------- bolsas (pouches) no quadro local
# Quadro local da bolsa: origem no meio de baixo da face de tras (encostada no painel), x para o lado, y para cima, z para fora.
def bolsa_corpo(q, mat, w, h, d, e=0.2):
    fofo(q, mat, 0.0, h / 2, d / 2, w / 2, h / 2, d / 2, e, e, (14, 20))


def costura_contorno(q, w, h, d, mat='costura_escura'):
    """Pesponto na frente da bolsa (linha fina de pontos)."""
    for y in (0.012, h - 0.012):
        for x in np.arange(-w / 2 + 0.012, w / 2 - 0.008, 0.008): q.box(mat, x, x + 0.004, y - 0.0006, y + 0.0006, d - 0.0012, d + 0.0004)


def bolsa_carregador(q, tec, w=0.085, h=0.12, d=0.04, mags=1, mag='polimero_mag', tampa=False, elastico=True):
    """Porta-carregador de fuzil: aberto em cima com o carregador aparecendo e cordao elastico com puxador (ou tampa de velcro)."""
    bolsa_corpo(q, tec, w, h, d)
    mw = (w - 0.016) / mags
    for i in range(mags):
        cx = -w / 2 + 0.008 + mw * (i + 0.5)
        q.cham(mag, cx - mw / 2 + 0.003, cx + mw / 2 - 0.003, h * 0.55, h + 0.045, d / 2 - 0.012, d / 2 + 0.012, 0.004)
        for y in np.arange(h + 0.004, h + 0.04, 0.006): q.box(mag, cx - mw / 2 + 0.0035, cx + mw / 2 - 0.0035, y, y + 0.0025, d / 2 - 0.0128, d / 2 + 0.0128)
        q.cham(mag, cx - mw / 2 + 0.002, cx + mw / 2 - 0.002, h + 0.04, h + 0.052, d / 2 - 0.014, d / 2 + 0.014, 0.003)   # base do carregador
    if tampa:
        q.hull(tec, [(sx * (w / 2 + 0.002), y, z) for sx in (-1, 1) for (y, z) in ((h + 0.058, d / 2 - 0.02), (h + 0.06, d / 2 + 0.018), (h * 0.7, d + 0.004), (h * 0.7, d))])
        q.cham('velcro_preto' if 'preta' in tec else tec, -0.022, 0.022, h * 0.7 + 0.004, h * 0.7 + 0.03, d + 0.002, d + 0.0055, 0.0015)
        q.cham(tec, -0.012, 0.012, h * 0.62, h * 0.72, d + 0.003, d + 0.007, 0.002)                                  # puxador
    elif elastico:
        cam = [(-w / 2 - 0.002, h * 0.75, d * 0.6), (-w / 2 + 0.004, h + 0.054, d / 2), (0.0, h + 0.056, d / 2 + 0.004),
               (w / 2 - 0.004, h + 0.054, d / 2), (w / 2 + 0.002, h * 0.75, d * 0.6)]
        q.add('elastico_preto', tubo(curva(cam, 24), 0.0024, 8))
        q.cham('nylon_preto', -0.01, 0.01, h + 0.05, h + 0.062, d / 2 + 0.008, d / 2 + 0.016, 0.003)               # puxador
    costura_contorno(q, w, h, d)
    q.box(tec, -w / 2 + 0.004, w / 2 - 0.004, h * 0.18, h * 0.18 + 0.025, d - 0.002, d + 0.0025)                    # fita MOLLE na frente


def bolsa_tampa(q, tec, w, h, d, velcro=None, ziper=False, fivela=False, cruz=False):
    """Bolsa utilitaria fechada com tampa (velcro ou fivela), opcional ziper na frente."""
    bolsa_corpo(q, tec, w, h, d)
    q.hull(tec, [(sx * (w / 2 + 0.003), y, z) for sx in (-1, 1) for (y, z) in ((h + 0.004, 0.002), (h + 0.008, d * 0.6), (h * 0.62, d + 0.005), (h * 0.62, d - 0.002))])
    if fivela:
        q.box('nylon_preto', -0.011, 0.011, h * 0.25, h * 0.66, d + 0.0045, d + 0.0065)
        q.cham('nylon_preto', -0.014, 0.014, h * 0.3, h * 0.42, d + 0.004, d + 0.011, 0.002)
    else:
        q.cham(velcro or tec, -w * 0.3, w * 0.3, h * 0.66, h * 0.74, d + 0.004, d + 0.0065, 0.001)
        q.cham(tec, -0.012, 0.012, h * 0.56, h * 0.64, d + 0.004, d + 0.008, 0.002)
    if ziper:
        q.box('nylon_preto', -w / 2 + 0.01, w / 2 - 0.01, h * 0.3, h * 0.3 + 0.006, d - 0.001, d + 0.003)
        q.cham('aluminio_escuro', w / 2 - 0.022, w / 2 - 0.012, h * 0.3 - 0.012, h * 0.3 + 0.004, d + 0.002, d + 0.005, 0.0012)
    if cruz:                                                                                       # marca de primeiros socorros (cruz branca, sem simbolo oficial)
        q.box('adesivo_branco', -0.006, 0.006, h * 0.18, h * 0.46, d - 0.0005, d + 0.0025)
        q.box('adesivo_branco', -0.02, 0.02, h * 0.26, h * 0.38, d - 0.0005, d + 0.0025)
    costura_contorno(q, w, h, d)


def bolsa_pistola(q, tec, w=0.05, h=0.1, d=0.032):
    bolsa_corpo(q, tec, w, h, d)
    q.cham('polimero_mag', -w / 2 + 0.01, w / 2 - 0.01, h * 0.6, h + 0.03, d / 2 - 0.008, d / 2 + 0.008, 0.003)
    q.cham('polimero_mag', -w / 2 + 0.008, w / 2 - 0.008, h + 0.026, h + 0.036, d / 2 - 0.01, d / 2 + 0.01, 0.0025)
    cam = [(-w / 2, h * 0.8, d * 0.6), (0.0, h + 0.04, d / 2 + 0.003), (w / 2, h * 0.8, d * 0.6)]
    q.add('elastico_preto', tubo(curva(cam, 16), 0.002, 8))
    costura_contorno(q, w, h, d)


def fivela(q, c, w=0.025, eixo_x=True, mat='nylon_preto'):
    """Fivela de engate rapido (macho e femea) deitada no plano xy, centrada em c."""
    x, y, z = c
    if eixo_x:
        q.cham(mat, x - 0.03, x + 0.002, y - w / 2 - 0.003, y + w / 2 + 0.003, z, z + 0.009, 0.0025)
        q.cham(mat, x, x + 0.024, y - w / 2, y + w / 2, z + 0.001, z + 0.008, 0.002)
        for s in (-1, 1): q.cham(mat, x + 0.002, x + 0.012, y + s * (w / 2 + 0.001) - 0.003, y + s * (w / 2 + 0.001) + 0.003, z + 0.0015, z + 0.0095, 0.0012)
    else:
        q.cham(mat, x - w / 2 - 0.003, x + w / 2 + 0.003, y - 0.002, y + 0.03, z, z + 0.009, 0.0025)
        q.cham(mat, x - w / 2, x + w / 2, y - 0.024, y, z + 0.001, z + 0.008, 0.002)


def poe(p, q, M4):
    p.merge(q, M4)


# ============================================================================ registro e exportacao
ITENS_EQ = {}
def equip(id, nome, equipa, **dados):
    def deco(fn):
        ITENS_EQ[id] = dict(id=id, nome=nome, grupo='equipamento', categoria=equipa, equipa=equipa, recurso='equipamento',
                            empilha=1, fn=fn, **dados); return fn
    return deco


class Montagem:
    def __init__(s): s.base = P(); s.partes = []; s.pose = np.eye(4); s.ref = None; s.ref_nome = None; s.vestir = None
    def parte(s, nome, origem, tipo, **info):
        q = P(); s.partes.append(dict(no=nome, origem=list(origem), tipo=tipo, peca=q, **info)); return q


DEITAR = TF.rotation_matrix(-math.pi / 2, [1, 0, 0])      # colete vestido (frente +Z) -> deitado de costas (frente +Y)


def suavizar(m, graus=38.0):
    """Normais suaves por vertice (com quina acima de 'graus'), na malha ja desfeita (3 vertices por face)."""
    fn = m.face_normals; area = m.area_faces
    v = m.vertices; key = np.round(v * 2e4).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.ravel()
    fv = np.repeat(fn, 3, axis=0); wv = np.repeat(area, 3)[:, None]
    ordem = np.argsort(inv, kind='stable'); inv_s = inv[ordem]
    cortes = np.flatnonzero(np.diff(inv_s)) + 1
    out = fv.copy(); cs = math.cos(math.radians(graus))
    for g in np.split(ordem, cortes):
        if len(g) < 2: continue
        n = fv[g]; ww = wv[g]
        sim = (n @ n.T) > cs
        acc = sim @ (n * ww)
        out[g] = nrm(acc)
    ruim = np.linalg.norm(out, axis=1) < 0.5; out[ruim] = [0.0, 1.0, 0.0]
    m.vertex_normals = out


def exportar(it, raiz=AQUI):
    M = Montagem(); it['fn'](M)
    nome = it['id']; F = M.pose.copy()
    # pivo no centro da base (depois de deitar)
    tudo = [mm for ms in M.base.parts.values() for mm in ms] + [mm for pt in M.partes for ms in pt['peca'].parts.values() for mm in ms]
    vs = np.concatenate([trimesh.transform_points(mm.vertices, F) for mm in tudo])
    lo, hi = vs.min(0), vs.max(0); F = TF.translation_matrix([-(lo[0] + hi[0]) / 2, -lo[1], -(lo[2] + hi[2]) / 2]) @ F
    sc = trimesh.Scene()
    def por(piece, prefixo, pai, T):
        q = P(); q.uv = {}
        for k, ms in piece.parts.items():
            for m in ms: mm = m.copy(); mm.apply_transform(T); q.add(k, mm)
        Ti = np.linalg.inv(T)
        for k, f in piece.uv.items(): q.uv[k] = (lambda f, Ti: (lambda v, n: f(trimesh.transform_points(v, Ti), (Ti[:3, :3] @ n.T).T)))(f, Ti)
        for gname, g in q.scene(prefixo).geometry.items():
            suavizar(g); sc.add_geometry(g, node_name=gname, geom_name=gname, parent_node_name=pai)
    por(M.base, nome, None, F)
    partes = []
    for pt in M.partes:
        ow = trimesh.transform_points([pt['origem']], F)[0]
        sc.graph.update(frame_from=sc.graph.base_frame, frame_to=pt['no'], matrix=TF.translation_matrix(ow))
        por(pt['peca'], f"{nome}_{pt['no']}", pt['no'], TF.translation_matrix(-ow) @ F)
        info = {k: v for k, v in pt.items() if k not in ('peca', 'origem')}
        if 'eixo' in info: info['eixo'] = [round(float(c), 4) for c in F[:3, :3] @ np.array(info['eixo'], float)]
        info['origem_m'] = [round(float(c), 4) for c in ow]
        partes.append(info)
    arq = os.path.join(raiz, f'{nome}.glb'); sc.export(arq); glb_jpeg(arq)
    b = sc.bounds; tris = sum(len(g.faces) for g in sc.geometry.values())
    reg = {k: v for k, v in it.items() if k != 'fn'}
    reg.update(arquivo=f"equipamento/{nome}.glb", tamanho_m=[round(float(x), 3) for x in (b[1] - b[0])], triangulos=int(tris),
               kb=round(os.path.getsize(arq) / 1024, 1))
    if M.vestir:
        ref = trimesh.transform_points([M.vestir['ponto']], F)[0]
        reg['vestir'] = {'girar_graus': M.vestir['girar_graus'], M.vestir['nome']: [round(float(c), 4) for c in ref],
                         'nota': M.vestir['nota']}
    if partes: reg['partes'] = partes
    return reg


for _f in ('capacetes.py', 'coletes.py', 'taticos.py'):
    _c = os.path.join(AQUI, _f)
    if os.path.exists(_c): exec(compile(open(_c, encoding='utf-8').read(), _c, 'exec'), globals())


CABECALHO = {
    'escala': '1 unidade = 1 m, Y para cima, frente do equipamento para +Z. Capacetes em pé apoiados na borda; coletes deitados de costas '
              '(frente para cima, gola para -Z). Pivô no centro da base.',
    'campos_jogo': {
        'equipa': 'espaço do inventário onde veste: capacete, colete ou colete_tatico',
        'celulas': '[largura, altura] do item na grade do inventário',
        'grade': '[largura, altura] da grade que o colete tático abre quando vestido',
        'bolsos': 'como a grade se divide nas bolsas do modelo (só informação; a soma bate com a grade)',
        'protecao': 'pontos de proteção contra mordida e golpe na parte do corpo (protege)',
        'balistico': 'até que tiro segura: nenhum, pistola ou fuzil',
        'durabilidade': 'golpes/mordidas até precisar de reparo na bancada de costura',
        'penalidade': 'multiplicadores enquanto vestido (cansaco_correr, ruido_passos, audicao, visao)',
        'vestir': 'como pôr no personagem: girar_graus e o ponto do corpo (cabeca_m ou peito_m) em metros no GLB',
        'partes': 'nós móveis (viseiras): tipo gira em torno de eixo a partir de origem_m, até abre_graus',
        'onde': 'prédios onde aparece no saque', 'raridade': 'comum, incomum, raro', 'valor_troca': 'preço na troca entre comunidades'},
}


def catalogo_md(regs):
    nomes = {'capacete': 'Capacetes', 'colete': 'Coletes', 'colete_tatico': 'Coletes táticos'}
    L = ['# Catálogo de equipamentos', '', 'Gerado por `props/equipamento/gerar_equipamento.py`. Medidas em metros (largura × altura × profundidade) na pose de repouso.', '']
    for eq, titulo in nomes.items():
        L += [f'## {titulo}', '', '| Item | Células | Grade | Proteção | Balístico | Peso | Raridade | Efeito | Aparece em | Triângulos |', '|---|---|---|---|---|---|---|---|---|---|']
        for r in regs:
            if r['equipa'] != eq: continue
            g = '×'.join(map(str, r['grade'])) if r.get('grade') else '-'
            L.append(f"| {r['nome']} (`{r['id']}`) | {'×'.join(map(str, r['celulas']))} | {g} | {r.get('protecao', 0)} | {r.get('balistico', 'nenhum')} | "
                     f"{r['peso_kg']} kg | {r['raridade']} | {r['efeito']} | {', '.join(r['onde'])} | {r['triangulos']} |")
        L.append('')
    import re
    open(os.path.join(AQUI, 'CATALOGO.md'), 'w', encoding='utf-8').write(re.sub(r'(\d)\.(\d)', r'\1,\2', '\n'.join(L)))


def main(ids):
    materiais_eq(); regs = []
    f = os.path.join(AQUI, 'catalogo.json')
    if ids and os.path.exists(f): regs = [r for r in json.load(open(f, encoding='utf-8'))['itens'] if r['id'] not in ids]
    for id_, it in ITENS_EQ.items():
        if ids and id_ not in ids: continue
        r = exportar(it); regs.append(r)
        print(f"{id_:26s} {r['triangulos']:7d} tris {r['kb']:7.1f} KB  {r['tamanho_m']}")
    ordem = list(ITENS_EQ); regs.sort(key=lambda r: ordem.index(r['id']) if r['id'] in ordem else 999)
    json.dump(dict(CABECALHO, itens=regs), open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    catalogo_md(regs)


if __name__ == '__main__':
    main(sys.argv[1:])
