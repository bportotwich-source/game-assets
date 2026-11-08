"""Gerador das MOBILIAS e dos ITENS DE LOOT originais (lote 1), no padrao de alto detalhe dos kits.

Uso:  python props/gerar_props.py            (gera tudo)
      python props/gerar_props.py geladeira  (so os ids pedidos)

Saida:
  props/mobilias/<id>.glb   props/mobilias/catalogo.json
  props/loot/<id>.glb       props/loot/catalogo.json

Convencoes (iguais as de props/decoracao, PR #48, e do PADRAO_METRICAS.md):
  Y para cima, 1 unidade = 1 m, frente para +Z.
  montagem "floor": pivo no centro da base.  "wall": pivo no centro de baixo da face de tras (encosta na parede).
  Itens de loot ficam deitados na pose de repouso (como achados numa prateleira ou no chao), pivo no centro da base.
  Portas, gavetas e tampas sao NOS separados no GLB, com a origem na dobradica (ou no ponto de deslize),
  descritos em "partes" no catalogo: o jogo so precisa girar ou deslizar o no.
Dependencias: as de scripts/detalhe (trimesh shapely numpy pillow scipy manifold3d mapbox_earcut).
"""
import os, sys, math, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', 'scripts', 'detalhe'))
from detalhe import *
from detalhe import Piece, PBRMaterial, TextureVisuals, Polygon, GT, tex_set, _fix
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Point, box as sbox, LineString
from shapely import affinity

# ============================================================================ materiais
CORES = {
    'madeira': (150, 102, 62), 'madeira_escura': (92, 60, 40), 'madeira_crua': (184, 150, 106), 'madeira_branca': (236, 232, 222),
    'esmalte': (238, 238, 232), 'esmalte_escuro': (34, 34, 36), 'liner': (244, 246, 246), 'inox': (188, 190, 194),
    'aco': (150, 154, 160), 'aco_pintado': (88, 104, 118), 'aco_polido': (210, 212, 216), 'lata': (200, 202, 206),
    'borracha': (28, 28, 30), 'plastico_branco': (240, 240, 236), 'plastico_cinza': (128, 132, 136), 'plastico_preto': (40, 40, 42),
    'plastico_vermelho': (120, 6, 5), 'tinta_vermelha': (112, 6, 4), 'tinta_amarela': (226, 176, 30),
    'granito': (70, 68, 66), 'espelho': (220, 226, 230), 'vidro_escuro': (30, 34, 38),
    'tecido_sofa': (92, 112, 128), 'tecido_almofada': (178, 120, 70), 'tecido_cadeira': (140, 70, 56),
    'colchao': (232, 228, 214), 'lencol': (240, 240, 236), 'cobertor': (120, 52, 52), 'travesseiro': (246, 244, 238),
    'atadura': (246, 244, 236), 'papelao': (176, 136, 92), 'ferrugem': (128, 70, 40), 'fita_prata': (176, 178, 180),
    'fita_preta': (30, 30, 30), 'cartela': (40, 96, 170), 'pilha_corpo': (30, 30, 34), 'cobre': (184, 110, 64),
}
TEXTURAS = {'madeira': 'paint', 'madeira_escura': 'paint', 'madeira_crua': 'paint'}
METALICOS = {'inox': (0.85, 0.28), 'aco': (0.8, 0.4), 'aco_polido': (0.9, 0.18), 'lata': (0.9, 0.26), 'espelho': (1.0, 0.03),
             'fita_prata': (0.5, 0.35), 'aco_pintado': (0.35, 0.45), 'tinta_vermelha': (0.1, 0.58), 'cobre': (0.9, 0.3),
             'tinta_amarela': (0.2, 0.45), 'esmalte': (0.05, 0.25), 'esmalte_escuro': (0.1, 0.3)}
FOSCOS = {'borracha': 0.92, 'tecido_sofa': 0.95, 'tecido_almofada': 0.95, 'tecido_cadeira': 0.95, 'colchao': 0.9, 'lencol': 0.9,
          'cobertor': 0.95, 'travesseiro': 0.9, 'atadura': 0.95, 'papelao': 0.92, 'ferrugem': 0.88, 'granito': 0.35,
          'plastico_branco': 0.45, 'plastico_cinza': 0.5, 'plastico_preto': 0.5, 'plastico_vermelho': 0.58, 'liner': 0.4,
          'fita_preta': 0.85, 'cartela': 0.6, 'pilha_corpo': 0.35, 'madeira_branca': 0.5}
TRANSP = {'vidro_prateleira': ((200, 226, 230), 0.35, 0.05), 'pet': ((200, 228, 240), 0.32, 0.08), 'agua': ((150, 200, 230), 0.45, 0.02),
          'plastico_transp': ((230, 236, 240), 0.4, 0.15), 'ambar': ((168, 84, 20), 0.82, 0.2), 'galao_azul': ((90, 150, 210), 0.6, 0.25)}
EMISSIVOS = {}          # material -> emissiveFactor (brasa da fogueira)
UV_ESCALA = {}          # material -> tamanho do ladrilho em metros (projecao em caixa)
TEX_PROPRIAS = [        # (material, tipo, ladrilho m, px/m): texturas de _ruido_tex; os lotes acrescentam as suas
    ('tecido_sofa', 'tecido', 0.5, 768), ('tecido_almofada', 'tecido', 0.5, 768), ('tecido_cadeira', 'tecido', 0.5, 768),
    ('colchao', 'tecido', 0.5, 768), ('lencol', 'tecido', 0.5, 768), ('cobertor', 'tecido', 0.5, 768),
    ('travesseiro', 'tecido', 0.5, 768), ('atadura', 'tecido', 0.25, 1024), ('papelao', 'papelao', 0.5, 512),
    ('ferrugem', 'ferrugem', 1.0, 384), ('granito', 'granito', 1.0, 512)]


def _ruido_tex(col, seed, px, tile, kind):
    """Texturas proprias dos props: tecido (trama), papelao, ferrugem e granito. tile em metros, px pixels por metro."""
    n = int(tile * px); g = GT.noise(n, n, 0.05 * px, 0.05 * px, seed); f = GT.fbm(n, n, 0.02 * px, 3, seed + 1)
    c = GT.rgb(col)[None, None]
    if kind == 'tecido':
        yy, xx = np.mgrid[0:n, 0:n] / px
        w = 0.5 + 0.5 * np.sin(xx * 2 * np.pi / 0.0024) * np.sin(yy * 2 * np.pi / 0.0024)
        alb = c * (0.9 + 0.08 * w[..., None] + 0.05 * g[..., None]); hm = 0.0002 * w + 0.0003 * f
        return alb, hm, 0.9 + 0.05 * f, 0.8, 0.0008
    if kind == 'papelao':
        yy = np.mgrid[0:n, 0:n][0] / px
        alb = c * (0.92 + 0.07 * g[..., None] + 0.05 * f[..., None]); hm = 0.0003 * np.sin(yy * 2 * np.pi / 0.008) + 0.0002 * f
        return alb, hm, 0.9 + 0.05 * f, 0.6, 0.0008
    if kind == 'ferrugem':
        sp = GT.smooth(0.2, 0.9, GT.fbm(n, n, 0.08 * px, 4, seed + 5))
        alb = GT.lerp(c * (0.85 + 0.2 * f[..., None]), GT.rgb((70, 64, 60))[None, None] * (0.9 + 0.2 * g[..., None]), (sp * 0.5)[..., None])
        hm = 0.0008 * f + 0.0005 * sp
        return alb, hm, 0.75 + 0.2 * f, 1.0, 0.002
    if kind == 'granito':
        sp = GT.smooth(0.62, 0.72, GT.noise(n, n, 0.0025 * px, 0.0025 * px, seed + 7)); sp2 = GT.smooth(0.62, 0.74, GT.noise(n, n, 0.002 * px, 0.002 * px, seed + 9))
        alb = c * (0.9 + 0.12 * f[..., None]); alb = GT.lerp(alb, GT.rgb((150, 140, 132))[None, None], (sp * 0.45)[..., None])
        alb = GT.lerp(alb, GT.rgb((24, 22, 22))[None, None], (sp2 * 0.5)[..., None]); hm = 0.00005 * f
        return alb, hm, 0.25 + 0.1 * sp, 0.3, 0.0003
    raise ValueError(kind)


def materiais():
    configurar(cores=CORES, texturas=TEXTURAS)
    for k, (met, rough) in METALICOS.items():
        MATS[k].metallicFactor = met; MATS[k].roughnessFactor = rough
    for k, r in FOSCOS.items(): MATS[k].roughnessFactor = r
    for i, (k, kind, tile, px) in enumerate(TEX_PROPRIAS):
        a, nm, o = tex_set(*_ruido_tex(CORES[k], 101 + 7 * i, px, tile, kind), px)
        TEX[k] = (a, nm, o); UV_ESCALA[k] = tile
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=0.15 if kind == 'ferrugem' else 0.0, roughnessFactor=1.0)
    for k, (c, alpha, rough) in TRANSP.items():
        MATS[k] = PBRMaterial(name=k, baseColorFactor=[c[0] / 255, c[1] / 255, c[2] / 255, alpha], alphaMode='BLEND',
                              metallicFactor=0.0, roughnessFactor=rough, doubleSided=False)
    for k, e in EMISSIVOS.items(): MATS[k].emissiveFactor = e
    MATS['espelho'].roughnessFactor = 0.03


def mat_imagem(nome, img, rough=0.45, metal=0.0):
    """Material com imagem impressa (rotulos). A UV vem de uma funcao da peca (uv_cilindro / uv_atlas / uv_plano)."""
    TEX[nome] = (img, None, None)
    MATS[nome] = PBRMaterial(name=nome, baseColorTexture=img, baseColorFactor=[255, 255, 255, 255], metallicFactor=metal, roughnessFactor=rough)


class P(Piece):
    """Piece com ladrilho por material (tecidos 0,5 m etc.)."""
    vertical = False
    def scene(s, name):
        for k in s.parts:
            if s.vertical and KIND.get(k) == 'paint' and k not in s.uv: s.uv[k] = uv_veio_vertical
            if k in UV_ESCALA and k not in s.uv: s.uv[k] = uv_caixa(UV_ESCALA[k])
        return Piece.scene(s, name)


def uv_veio_vertical(v, n):
    """Madeira dos moveis: veio na vertical nas faces em pe (portas, laterais) e ao longo de x nos tampos."""
    uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1)
    uv[ax == 0] = v[ax == 0][:, [1, 2]]; uv[ax == 2] = v[ax == 2][:, [1, 0]]; uv[ax == 1] = v[ax == 1][:, [0, 2]]
    return uv / TILE


def uv_caixa(tile):
    def f(v, n):
        uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1)
        uv[ax == 0] = v[ax == 0][:, [2, 1]]; uv[ax == 2] = v[ax == 2][:, [0, 1]]; uv[ax == 1] = v[ax == 1][:, [0, 2]]
        return uv / tile
    return f


def _sem_costura(u):
    """u por triangulo (vertices em trios apos unmerge): tira o salto 0,99 -> 0,01 na costura do cilindro."""
    t = u.reshape(-1, 3)
    for _ in range(2):
        big = (t.max(1) - t.min(1)) > 0.5
        t[big] = np.where(t[big] < 0.5, t[big] + 1, t[big])
    return t.reshape(-1)


def uv_cilindro(y0, y1, eixo='y', centro=(0, 0, 0), u0=0.0):
    """Rotulo enrolado num cilindro: u = angulo, v = altura ao longo do eixo."""
    def f(v, n):
        c = v - np.array(centro)
        if eixo == 'y': a, b, h = c[:, 0], c[:, 2], c[:, 1]
        elif eixo == 'x': a, b, h = c[:, 2], c[:, 1], c[:, 0]
        else: a, b, h = c[:, 0], c[:, 1], c[:, 2]
        u = (0.5 - np.arctan2(b, a) / (2 * np.pi) + u0) % 1.0
        return np.stack([_sem_costura(u), (h - y0) / (y1 - y0)], 1)
    return f


def uv_atlas(x0, x1, y0, y1, z0, z1, frente='z'):
    """Atlas de 4 colunas [frente | tras | lado | topo] para caixas impressas.
    frente='z': frente e a face +Z (caixa em pe). frente='y': frente e a face de cima (pacote deitado)."""
    def f(v, n):
        uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1); sg = np.sign(n[np.arange(len(n)), ax])
        X = (v[:, 0] - x0) / (x1 - x0); Y = (v[:, 1] - y0) / (y1 - y0); Z = (v[:, 2] - z0) / (z1 - z0)
        if frente == 'z':
            m = (ax == 2) & (sg > 0); uv[m] = np.stack([X[m] * 0.25, Y[m]], 1)
            m = (ax == 2) & (sg < 0); uv[m] = np.stack([0.25 + (1 - X[m]) * 0.25, Y[m]], 1)
            m = ax == 0; uv[m] = np.stack([0.5 + np.where(sg[m] > 0, 1 - Z[m], Z[m]) * 0.25, Y[m]], 1)
            m = ax == 1; uv[m] = np.stack([0.75 + X[m] * 0.25, Z[m]], 1)
        else:
            m = (ax == 1) & (sg > 0); uv[m] = np.stack([X[m] * 0.25, 1 - Z[m]], 1)
            m = (ax == 1) & (sg < 0); uv[m] = np.stack([0.25 + X[m] * 0.25, Z[m]], 1)
            m = ax == 0; uv[m] = np.stack([0.5 + Z[m] * 0.25, Y[m]], 1)
            m = ax == 2; uv[m] = np.stack([0.75 + X[m] * 0.25, Y[m]], 1)
        return uv
    return f


def uv_plano(x0, x1, z0, z1):
    """Imagem deitada no plano XZ (tampa da lata de sardinha, cartela de pilhas)."""
    def f(v, n): return np.stack([(v[:, 0] - x0) / (x1 - x0), 1 - (v[:, 2] - z0) / (z1 - z0)], 1)
    return f


# ============================================================================ rotulos (artes originais, marcas inventadas)
def fonte(tam, negrito=True):
    for f in (('DejaVuSans-Bold.ttf' if negrito else 'DejaVuSans.ttf'), ('arialbd.ttf' if negrito else 'arial.ttf'),
              '/usr/share/fonts/truetype/dejavu/' + ('DejaVuSans-Bold.ttf' if negrito else 'DejaVuSans.ttf')):
        try: return ImageFont.truetype(f, tam)
        except OSError: pass
    return ImageFont.load_default(size=tam)


def texto_c(d, xy, txt, tam, cor, negrito=True, larg=None):
    f = fonte(tam, negrito)
    while larg and d.textlength(txt, font=f) > larg and tam > 8: tam -= 2; f = fonte(tam, negrito)
    d.text(xy, txt, font=f, fill=cor, anchor='mm')


def rotulo_lata(nome, marca, fundo, faixa, desenho):
    im = Image.new('RGB', (1024, 384), fundo); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1024, 60], fill=faixa); d.rectangle([0, 324, 1024, 384], fill=faixa)
    for cx in (256, 768):
        d.ellipse([cx - 150, 80, cx + 150, 304], fill=(250, 244, 226), outline=faixa, width=8)
        texto_c(d, (cx, 150), marca, 40, faixa, larg=260); texto_c(d, (cx, 220), nome, 64, (40, 30, 26), larg=270)
        texto_c(d, (cx, 280), 'PESO LIQ. 420 g', 22, (70, 60, 50), False)
    desenho(d)
    return im


def graos(cor):
    def f(d):
        for x0 in (40, 512 + 40):
            for i in range(14):
                x = x0 + (i * 37) % 70; y = 90 + (i * 53) % 200
                d.ellipse([x, y, x + 34, y + 22], fill=cor, outline=(40, 20, 16))
    return f


def rotulo_caixa(colunas, tam=(1024, 512)):
    """colunas: 4 funcoes desenho(d, w, h) para [frente, tras, lado, topo]."""
    im = Image.new('RGB', tam, (255, 255, 255)); cw = tam[0] // 4
    for i, fn in enumerate(colunas):
        sub = Image.new('RGB', (cw, tam[1]), (255, 255, 255)); fn(ImageDraw.Draw(sub), cw, tam[1]); im.paste(sub, (i * cw, 0))
    return im


# ============================================================================ primitivas extras
def cyl_eixo(p, mat, r, a0, a1, eixo='x', c=(0, 0, 0), sec=16):
    """Cilindro ao longo de x ou z, de a0 a a1, centrado em c nas outras duas coordenadas."""
    m = trimesh.creation.cylinder(radius=r, height=a1 - a0, sections=sec)
    if eixo == 'x': m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([(a0 + a1) / 2, c[1], c[2]])
    elif eixo == 'z': m.apply_translation([c[0], c[1], (a0 + a1) / 2])
    else: m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_translation([c[0], (a0 + a1) / 2, c[2]])
    return p.add(mat, m)


def torno(p, mat, perfil, sec=32, eixo='y', c=(0, 0, 0), fechar=True):
    """Solido de revolucao. perfil = [(raio, altura), ...] de baixo para cima; fechar poe raio 0 nas pontas."""
    pts = list(perfil)
    if fechar:
        if pts[0][0] > 0: pts = [(0.0, pts[0][1])] + pts
        if pts[-1][0] > 0: pts = pts + [(0.0, pts[-1][1])]
    m = trimesh.creation.revolve(np.array(pts, float), sections=sec)
    if m.volume < 0: m.invert()
    if eixo == 'y': m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    elif eixo == 'x': m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    m.apply_translation(c); return p.add(mat, m)


def anel(p, mat, r0, r1, h0, h1, sec=32, eixo='y', c=(0, 0, 0), chanfro=0.0):
    """Tubo (anel) de r0 a r1, de h0 a h1."""
    ch = min(chanfro, (r1 - r0) / 3, (h1 - h0) / 3)
    pts = [(r0, h0), (r1 - ch, h0), (r1, h0 + ch), (r1, h1 - ch), (r1 - ch, h1), (r0, h1)]
    m = trimesh.creation.revolve(np.array(pts + [pts[0]], float), sections=sec)
    if m.volume < 0: m.invert()
    if eixo == 'y': m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    elif eixo == 'x': m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    m.apply_translation(c); return p.add(mat, m)


def fofo(p, mat, cx, cy, cz, a, b, c, e1=0.25, e2=0.25, n=(20, 28), rot_x=0.0):
    """Superelipsoide (almofadas, colchao, travesseiro, pacote): semi-eixos a,b,c; e pequeno = mais quadrado."""
    s = trimesh.creation.uv_sphere(radius=1.0, count=list(n)); v = s.vertices
    lat = np.arcsin(np.clip(v[:, 1], -1, 1)); lon = np.arctan2(v[:, 2], v[:, 0])
    sp = lambda w, e: np.sign(w) * np.abs(w) ** e
    x = a * sp(np.cos(lat), e1) * sp(np.cos(lon), e2); y = b * sp(np.sin(lat), e1); z = c * sp(np.cos(lat), e1) * sp(np.sin(lon), e2)
    m = trimesh.Trimesh(np.stack([x, y, z], 1), s.faces, process=True)
    if m.volume < 0: m.invert()
    if rot_x: m.apply_transform(trimesh.transformations.rotation_matrix(rot_x, [1, 0, 0]))
    m.apply_translation([cx, cy, cz]); return p.add(mat, m)


def varrer(p, mat, perfil, caminho, cap=True):
    """Perfil 2D (Polygon) varrido ao longo de um caminho 3D (cabos, pe de cabra, alca)."""
    m = trimesh.creation.sweep_polygon(perfil, np.array(caminho, float), cap=cap)
    if m.volume < 0: m.invert()
    return p.add(mat, m)


def circ(r, n=12): return Polygon([(r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)])


def extrudar_xz(p, mat, poly, y0, y1):
    """Poligono no plano XZ (shapely em x,z) extrudado de y0 a y1 (pecas deitadas: chave inglesa, tampa oval)."""
    m = trimesh.creation.extrude_polygon(poly, y1 - y0)
    m.vertices = np.stack([m.vertices[:, 0], y0 + m.vertices[:, 2], -m.vertices[:, 1]], 1)
    if m.volume < 0: m.invert()
    return p.add(mat, m)


def carcaca(p, mat, x0, x1, y0, y1, z0, z1, t=0.018, fundo=True, topo=True, base=True):
    """Caixa oca aberta na frente (+Z): laterais, topo, base e fundo."""
    p.box(mat, x0, x0 + t, y0, y1, z0, z1); p.box(mat, x1 - t, x1, y0, y1, z0, z1)
    if topo: p.box(mat, x0 + t, x1 - t, y1 - t, y1, z0, z1)
    if base: p.box(mat, x0 + t, x1 - t, y0, y0 + t, z0, z1)
    if fundo: p.box(mat, x0 + t, x1 - t, y0 + t, y1 - t, z0, z0 + 0.008)


def almofadada(p, mat, x0, x1, y0, y1, z0, z1, borda=0.06, n=1, c=0.004):
    """Folha de porta com quadro (montantes e travessas) e n almofadas levantadas, na frente (+Z)."""
    e = z1 - z0; p.cham(mat, x0, x0 + borda, y0, y1, z0, z1, c); p.cham(mat, x1 - borda, x1, y0, y1, z0, z1, c)
    hs = (y1 - y0 - borda * (n + 1)) / n
    for i in range(n + 1):
        yb = y0 + i * (hs + borda); p.cham(mat, x0 + borda - 0.001, x1 - borda + 0.001, yb, yb + borda, z0, z1, c)
    for i in range(n):
        ya = y0 + borda + i * (hs + borda)
        p.cham(mat, x0 + borda, x1 - borda, ya - 0.001, ya + hs + 0.001, z0 + 0.002, z1 - e * 0.35, c)          # fundo rebaixado
        p.cham(mat, x0 + borda + 0.02, x1 - borda - 0.02, ya + 0.02, ya + hs - 0.02, z1 - e * 0.4, z1 - 0.003, 0.008)   # almofada


def puxador_barra(p, mat, x, y0, y1, z, afast=0.03, r=0.007, eixo='y'):
    """Puxador em barra com dois pes. eixo y: vertical em x; eixo x: horizontal em y (y0..y1 viram x0..x1, x vira y)."""
    if eixo == 'y':
        for yy in (y0 + 0.012, y1 - 0.012): cyl_eixo(p, mat, r * 0.8, z, z + afast, 'z', (x, yy, 0), 10)
        p.cyl(mat, r, y0, y1, x=x, z=z + afast, sec=12)
    else:
        for xx in (y0 + 0.012, y1 - 0.012): cyl_eixo(p, mat, r * 0.8, z, z + afast, 'z', (xx, x, 0), 10)
        cyl_eixo(p, mat, r, y0, y1, 'x', (0, x, z + afast), 12)


def pegador(p, mat, x, y, z, r=0.014):
    """Puxador redondo (botao) na frente."""
    torno(p, mat, [(r * 0.45, 0), (r * 0.5, 0.008), (r * 0.9, 0.014), (r, 0.019), (r * 0.7, 0.024)], 16, 'z', (x, y, z))


def pe_torneado(p, mat, x, z, y0, y1, r=0.025, sec=16):
    h = y1 - y0
    perf = [(r * 0.6, 0), (r * 0.75, 0.02 * h), (r * 0.7, 0.06 * h), (r * 0.55, 0.3 * h), (r * 0.9, 0.55 * h), (r * 0.6, 0.62 * h),
            (r * 0.6, 0.68 * h), (r, 0.72 * h), (r, 1.0 * h)]
    torno(p, mat, [(a, b + y0) for a, b in perf], sec, 'y', (x, 0, z))


# ============================================================================ itens
ITENS = {}; LOTE = [1]
def item(id, nome, grupo, categoria, montagem='floor', **dados):
    def deco(fn): ITENS[id] = dict(id=id, nome=nome, grupo=grupo, categoria=categoria, montagem=montagem, lote=LOTE[0], fn=fn, **dados); return fn
    return deco


class Montagem:
    """Peca fixa + partes moveis (cada parte vira um no com origem na dobradica)."""
    def __init__(s): s.base = P(); s.partes = []
    def parte(s, nome, origem, tipo, **info):
        q = P(); s.partes.append(dict(no=nome, origem=list(origem), tipo=tipo, peca=q, **info)); return q


# ---------------------------------------------------------------------------- MOBILIAS
@item('geladeira', 'Geladeira duplex', 'mobilias', 'cozinha', conteiner=True, saque=['comida', 'agua', 'remedios'], slots=12,
      barricada=True, comodos=['cozinha'])
def geladeira(M):
    p = M.base; W, H = 0.70, 1.75; X = W / 2; zf = 0.26
    carcaca(p, 'esmalte', -X, X, 0.06, H, -0.33, zf, t=0.04)
    p.box('liner', -X + 0.04, X - 0.04, 0.10, H - 0.04, -0.29, -0.282)
    for xs in (-1, 1): p.box('liner', xs * (X - 0.04) - (0.004 if xs > 0 else -0.004), xs * (X - 0.04), 0.10, H - 0.04, -0.29, zf)
    p.box('esmalte', -X + 0.04, X - 0.04, 1.22, 1.27, -0.29, zf)                        # divisoria freezer
    p.box('liner', -X + 0.04, X - 0.04, 0.10, 0.104, -0.29, zf)
    for y in (0.45, 0.75, 1.0):                                                       # prateleiras de vidro com friso
        p.box('vidro_prateleira', -X + 0.045, X - 0.045, y, y + 0.006, -0.28, zf - 0.03)
        p.box('plastico_cinza', -X + 0.045, X - 0.045, y - 0.01, y + 0.012, zf - 0.045, zf - 0.03)
        for xs in (-1, 1): p.box('plastico_cinza', xs * (X - 0.045) - xs * 0.012, xs * (X - 0.045), y - 0.008, y, -0.28, zf - 0.03)
    p.box('vidro_prateleira', -X + 0.045, X - 0.045, 1.48, 1.486, -0.28, zf - 0.03)
    for x0, x1 in ((-X + 0.05, -0.005), (0.005, X - 0.05)):                           # gavetas de legumes
        p.box('plastico_transp', x0, x1, 0.106, 0.12, -0.27, zf - 0.03)
        p.box('plastico_transp', x0, x1, 0.12, 0.30, zf - 0.04, zf - 0.03)
        for xx in (x0, x1 - 0.004): p.box('plastico_transp', xx, xx + 0.004, 0.12, 0.28, -0.27, zf - 0.04)
        p.box('plastico_cinza', x0 + 0.08, x1 - 0.08, 0.27, 0.285, zf - 0.03, zf - 0.02)
    p.box('liner', -X + 0.04, X - 0.04, 0.33, 0.336, -0.28, zf - 0.03)
    p.box('esmalte_escuro', -X + 0.03, X - 0.03, 0.0, 0.06, zf - 0.03, zf - 0.025)     # grelha do rodape
    for i in range(14): p.box('borracha', -X + 0.05 + i * 0.043, -X + 0.07 + i * 0.043, 0.012, 0.048, zf - 0.026, zf - 0.02)
    for xs in (-1, 1):
        for zz in (-0.29, zf - 0.06): p.cyl('borracha', 0.02, 0.0, 0.06, x=xs * (X - 0.05), z=zz)
    for i in range(9):                                                                # serpentina atras
        y = 0.25 + i * 0.16; cyl_eixo(p, 'esmalte_escuro', 0.004, -X + 0.08, X - 0.08, 'x', (0, y, -0.355), 8)
    for x in np.linspace(-X + 0.09, X - 0.09, 12): p.box('esmalte_escuro', x - 0.0015, x + 0.0015, 0.2, 1.6, -0.36, -0.35)
    for xs in (-1, 1): p.box('esmalte_escuro', xs * (X - 0.08) - 0.006, xs * (X - 0.08) + 0.006, 0.2, 1.6, -0.35, -0.33)
    p.cham('esmalte', X - 0.06, X, H - 0.002, H + 0.012, zf + 0.004, zf + 0.06, 0.004)  # tampa da dobradica
    def porta(nome, y0, y1, cestos):
        q = M.parte(nome, (X, 0, zf + 0.065), 'porta', eixo='y', abre_graus=110)
        q.cham('esmalte', -X, X, y0, y1, zf + 0.002, zf + 0.065, 0.012)
        for (a0, a1, b0, b1) in ((-X + 0.02, X - 0.02, y0 + 0.02, y0 + 0.04), (-X + 0.02, X - 0.02, y1 - 0.04, y1 - 0.02),
                                 (-X + 0.02, -X + 0.04, y0 + 0.02, y1 - 0.02), (X - 0.04, X - 0.02, y0 + 0.02, y1 - 0.02)):
            q.box('borracha', a0, a1, b0, b1, zf - 0.006, zf + 0.002)                     # borracha de vedacao
        q.box('liner', -X + 0.045, X - 0.045, y0 + 0.045, y1 - 0.045, zf - 0.014, zf)
        for yb in cestos:
            q.box('plastico_transp', -X + 0.06, X - 0.06, yb, yb + 0.006, zf - 0.09, zf - 0.014)
            q.box('plastico_transp', -X + 0.06, X - 0.06, yb, yb + 0.07, zf - 0.094, zf - 0.088)
            for xs in (-1, 1): q.box('plastico_transp', xs * (X - 0.06) - (0.004 if xs > 0 else 0), xs * (X - 0.06) + (0 if xs > 0 else 0.004), yb, yb + 0.07, zf - 0.09, zf - 0.014)
        q.cham('plastico_cinza', -X + 0.02, -X + 0.05, y0 + (0.1 if y1 - y0 > 0.6 else 0.03), y0 + (0.5 if y1 - y0 > 0.6 else 0.2), zf + 0.065, zf + 0.09, 0.008)
        return q
    q = porta('porta_geladeira', 0.065, 1.262, (0.25, 0.55, 0.85))
    porta('porta_freezer', 1.268, H - 0.003, (1.40,)).box('inox', -X + 0.06, -X + 0.18, H - 0.07, H - 0.05, zf + 0.065, zf + 0.067)


@item('fogao', 'Fogão 4 bocas', 'mobilias', 'cozinha', conteiner=True, saque=['comida', 'utensilios'], slots=4, comodos=['cozinha'])
def fogao(M):
    p = M.base; X = 0.28; zf = 0.27; zb = -0.30
    p.box('esmalte', -X, -X + 0.02, 0.02, 0.80, zb, zf + 0.03); p.box('esmalte', X - 0.02, X, 0.02, 0.80, zb, zf + 0.03)
    p.box('esmalte', -X + 0.02, X - 0.02, 0.02, 0.80, zb, zb + 0.015)
    p.box('esmalte', -X + 0.02, X - 0.02, 0.02, 0.17, zb, zf + 0.03)                    # base e gaveta
    p.box('esmalte', -X + 0.02, X - 0.02, 0.645, 0.80, zf - 0.04, zf + 0.03)            # painel dos botoes
    p.box('esmalte', -X + 0.02, -0.22, 0.17, 0.645, zf - 0.01, zf + 0.03); p.box('esmalte', 0.22, X - 0.02, 0.17, 0.645, zf - 0.01, zf + 0.03)
    carcaca(p, 'esmalte_escuro', -0.22, 0.22, 0.17, 0.645, -0.27, zf - 0.01, t=0.01)    # forno
    for y in (0.30, 0.44):                                                            # grades do forno
        for x in np.linspace(-0.2, 0.2, 9): cyl_eixo(p, 'aco', 0.0025, -0.25, zf - 0.03, 'z', (x, y, 0), 6)
        for z in (-0.25, zf - 0.03): cyl_eixo(p, 'aco', 0.003, -0.21, 0.21, 'x', (0, y, z), 6)
    p.box('lamp_glass', -0.03, 0.03, 0.62, 0.635, -0.27, -0.25)
    p.box('inox', -X, X, 0.80, 0.815, zb, zf + 0.03)                                   # mesa inox
    for (bx, bz, r) in ((-0.13, -0.13, 0.05), (0.13, -0.13, 0.04), (-0.13, 0.13, 0.04), (0.13, 0.13, 0.055)):
        torno(p, 'esmalte_escuro', [(r + 0.02, 0.815), (r + 0.015, 0.825), (r, 0.83)], 24, 'y', (bx, 0, bz))
        torno(p, 'aco', [(r * 0.9, 0.83), (r * 0.9, 0.842), (r * 0.6, 0.846)], 24, 'y', (bx, 0, bz))
        p.cyl('esmalte_escuro', r * 0.55, 0.846, 0.852, x=bx, z=bz, sec=20)
        for a in range(4):                                                            # trempe de ferro
            ang = a * math.pi / 2 + math.pi / 4; dx, dz = math.cos(ang), math.sin(ang)
            p.seg('esmalte_escuro', (bx + dx * (r * 0.75), 0.862, bz + dz * (r * 0.75)), (bx + dx * 0.11, 0.862, bz + dz * 0.11), 0.009, 0.012)
            p.seg('esmalte_escuro', (bx + dx * 0.105, 0.815, bz + dz * 0.105), (bx + dx * 0.105, 0.868, bz + dz * 0.105), 0.01, 0.01)
    for x0, x1, z0, z1 in ((-0.255, 0.255, -0.258, -0.245), (-0.255, 0.255, 0.245, 0.258), (-0.258, -0.245, -0.255, 0.255),
                           (0.245, 0.258, -0.255, 0.255), (-0.006, 0.006, -0.255, 0.255), (-0.255, 0.255, -0.006, 0.006)):
        p.box('esmalte_escuro', x0, x1, 0.856, 0.868, z0, z1)
    p.cham('esmalte', -X, X, 0.815, 0.98, zb, zb + 0.025, 0.004)                        # espelho traseiro
    for i, x in enumerate((-0.2, -0.1, 0.0, 0.1, 0.2)):                               # botoes
        torno(p, 'plastico_preto', [(0.022, 0), (0.022, 0.006), (0.018, 0.024), (0.0, 0.026)], 20, 'z', (x, 0.725, zf + 0.03))
        p.box('aco_polido', x - 0.003, x + 0.003, 0.71, 0.74, zf + 0.05, zf + 0.058)
        anel(p, 'inox', 0.023, 0.028, 0.0, 0.002, 20, 'z', (x, 0.725, zf + 0.03))
    p.box('esmalte_escuro', -0.25, 0.25, 0.775, 0.79, zf + 0.03, zf + 0.032)
    for xs in (-1, 1):
        for zz in (zb + 0.04, zf - 0.02): torno(p, 'borracha', [(0.018, 0), (0.014, 0.02)], 12, 'y', (xs * (X - 0.04), 0, zz))
    g = M.parte('gaveta', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.35])
    g.cham('esmalte', -X + 0.022, X - 0.022, 0.025, 0.165, zf + 0.004, zf + 0.03, 0.006)
    carcaca(g, 'esmalte_escuro', -X + 0.04, X - 0.04, 0.03, 0.14, -0.26, zf + 0.004, t=0.008, topo=False)
    puxador_barra(g, 'inox', 0.12, -0.15, 0.15, zf + 0.03, eixo='x')
    q = M.parte('porta_forno', (0, 0.17, zf + 0.03), 'porta', eixo='x', abre_graus=85)
    q.cham('esmalte', -X + 0.022, X - 0.022, 0.172, 0.642, zf - 0.006, zf + 0.03, 0.008)
    q.box('vidro_escuro', -0.18, 0.18, 0.28, 0.56, zf + 0.026, zf + 0.032)
    for (a0, a1, b0, b1) in ((-0.19, 0.19, 0.27, 0.28), (-0.19, 0.19, 0.56, 0.57), (-0.19, -0.18, 0.27, 0.57), (0.18, 0.19, 0.27, 0.57)):
        q.box('inox', a0, a1, b0, b1, zf + 0.026, zf + 0.034)
    puxador_barra(q, 'inox', 0.61, -0.22, 0.22, zf + 0.03, eixo='x')


@item('balcao_pia', 'Balcão com pia', 'mobilias', 'cozinha', conteiner=True, saque=['utensilios', 'limpeza', 'ferramentas'], slots=6,
      comodos=['cozinha'])
def balcao_pia(M):
    p = M.base; X = 0.60; zf = 0.27; zb = -0.30
    p.box('madeira_branca', -X, -X + 0.018, 0.0, 0.86, zb, zf); p.box('madeira_branca', X - 0.018, X, 0.0, 0.86, zb, zf)
    p.box('madeira_branca', -X + 0.018, X - 0.018, 0.10, 0.118, zb, zf); p.box('madeira_branca', -X + 0.018, X - 0.018, 0.118, 0.86, zb, zb + 0.008)
    p.box('madeira_branca', -X + 0.018, X - 0.018, 0.40, 0.416, zb + 0.008, zf - 0.04)    # prateleira
    p.box('plastico_preto', -X + 0.018, X - 0.018, 0.0, 0.10, zf - 0.06, zf - 0.045)        # rodape recuado
    p.cham('madeira_branca', -X + 0.002, X - 0.002, 0.705, 0.858, zf, zf + 0.019, 0.003)   # frente falsa
    p.box('madeira_branca', -0.0008, 0.0008, 0.70, 0.86, zf + 0.012, zf + 0.0195)
    # tampo de granito com recorte da cuba
    T0, T1 = 0.86, 0.90; hx, hz0, hz1 = 0.24, -0.20, 0.13
    for (a0, a1, b0, b1) in ((-X - 0.01, -hx, zb, zf + 0.035), (hx, X + 0.01, zb, zf + 0.035), (-hx, hx, zb, hz0), (-hx, hx, hz1, zf + 0.035)):
        p.cham('granito', a0, a1, T0, T1, b0, b1, 0.002)
    p.box('granito', -X - 0.01, X + 0.01, T1, T1 + 0.08, zb, zb + 0.015)                # rodabanca
    p.box('inox', -hx - 0.02, hx + 0.02, T1, T1 + 0.004, hz0 - 0.02, hz0 + 0.002); p.box('inox', -hx - 0.02, hx + 0.02, T1, T1 + 0.004, hz1 - 0.002, hz1 + 0.02)
    p.box('inox', -hx - 0.02, -hx + 0.002, T1, T1 + 0.004, hz0, hz1); p.box('inox', hx - 0.002, hx + 0.02, T1, T1 + 0.004, hz0, hz1)
    cb = 0.69
    for (a0, a1, b0, b1) in ((-hx, hx, hz0, hz0 + 0.003), (-hx, hx, hz1 - 0.003, hz1), (-hx, -hx + 0.003, hz0, hz1), (hx - 0.003, hx, hz0, hz1)):
        p.box('inox', a0, a1, cb, T1, b0, b1)
    p.box('inox', -hx, hx, cb, cb + 0.003, hz0, hz1)
    anel(p, 'inox', 0.012, 0.03, cb + 0.003, cb + 0.006, 24); p.cyl('esmalte_escuro', 0.012, cb + 0.001, cb + 0.004, sec=16)
    p.cyl('plastico_cinza', 0.02, 0.42, cb, x=0, z=0.0, sec=16)                         # sifao
    cyl_eixo(p, 'plastico_cinza', 0.02, zb, 0.0, 'z', (0, 0.44, 0), 16)
    torno(p, 'inox', [(0.026, T1), (0.024, T1 + 0.01), (0.014, T1 + 0.03), (0.012, T1 + 0.24)], 24, 'y', (0, 0, -0.245))
    arco = [(0, T1 + 0.24 + 0.08 * math.sin(a), -0.245 + 0.08 * (1 - math.cos(a))) for a in np.linspace(0, math.pi, 14)]
    varrer(p, 'inox', circ(0.011, 14), [(0, T1 + 0.235, -0.245)] + arco[1:] + [(0, T1 + 0.17, -0.085)])
    p.cyl('aco_polido', 0.009, T1 + 0.155, T1 + 0.17, x=0, z=-0.085, sec=14)
    for xs in (-1, 1):
        p.cyl('inox', 0.012, T1, T1 + 0.03, x=xs * 0.07, z=-0.25, sec=16)
        p.seg('inox', (xs * 0.07, T1 + 0.03, -0.25), (xs * 0.07, T1 + 0.04, -0.19), 0.01, 0.008)
    for nome, hx0, sgn in (('porta_esq', -X, -1), ('porta_dir', X, 1)):
        q = M.parte(nome, (hx0, 0, zf + 0.019), 'porta', eixo='y', abre_graus=100 * sgn)
        a0, a1 = sorted((hx0 - sgn * 0.002, -sgn * 0.0015))
        almofadada(q, 'madeira_branca', a0, a1, 0.105, 0.70, zf, zf + 0.019, borda=0.07, n=1)
        xh = -sgn * 0.035
        puxador_barra(q, 'inox', xh, 0.50, 0.66, zf + 0.019)


@item('estante_metal', 'Estante de aço (5 prateleiras)', 'mobilias', 'deposito', conteiner=True, saque=['ferramentas', 'materiais', 'comida'],
      slots=10, comodos=['deposito', 'garagem', 'loja'])
def estante_metal(M):
    p = M.base; X, Z, H = 0.5, 0.2, 1.9; a, t = 0.035, 0.0025
    for xs in (-1, 1):
        for zs in (-1, 1):
            cx, cz = xs * X, zs * Z
            L = [(cx, cz), (cx - xs * a, cz), (cx - xs * a, cz - zs * t), (cx - xs * t, cz - zs * t), (cx - xs * t, cz - zs * a), (cx, cz - zs * a)]
            L = [(px, -pz) for px, pz in L]
            m = trimesh.creation.extrude_polygon(Polygon(L).buffer(0), H - 0.012); m.vertices = np.stack([m.vertices[:, 0], 0.012 + m.vertices[:, 2], -m.vertices[:, 1]], 1)
            p.add('aco_pintado', _fix(m))
            for y in np.arange(0.06, H - 0.04, 0.05):                                 # furos oblongos (escuros) nas duas abas
                p.box('esmalte_escuro', cx - xs * 0.02, cx - xs * 0.012, y, y + 0.022, cz + zs * 0.0002, cz + zs * 0.0006) if zs > 0 else \
                    p.box('esmalte_escuro', cx - xs * 0.02, cx - xs * 0.012, y, y + 0.022, cz - 0.0006, cz - 0.0002)
                xa, xb = sorted((cx + xs * 0.0002, cx + xs * 0.0006)); p.box('esmalte_escuro', xa, xb, y, y + 0.022, *sorted((cz - zs * 0.02, cz - zs * 0.012)))
            torno(p, 'plastico_preto', [(0.022, 0), (0.022, 0.012)], 4, 'y', (cx - xs * 0.012, 0, cz - zs * 0.012))
    for i, y in enumerate((0.08, 0.50, 0.92, 1.34, 1.76)):
        p.box('aco_pintado', -X + 0.003, X - 0.003, y + 0.03 - 0.0012, y + 0.03, -Z + 0.003, Z - 0.003)
        for zs in (-1, 1): p.box('aco_pintado', -X + 0.003, X - 0.003, y, y + 0.03, *sorted((zs * (Z - 0.003), zs * (Z - 0.0045))))
        for xs in (-1, 1): p.box('aco_pintado', *sorted((xs * (X - 0.003), xs * (X - 0.0045))), y, y + 0.03, -Z + 0.003, Z - 0.003)
        p.box('aco_pintado', -X + 0.01, X - 0.01, y + 0.012, y + 0.03 - 0.0012, -0.012, 0.012)   # reforco
        for xs in (-1, 1):
            for zs in (-1, 1):
                for yy in (y + 0.009, y + 0.021):                                     # parafusos
                    cyl_eixo(p, 'aco', 0.005, zs * Z, zs * (Z + 0.004), 'z', (xs * (X - 0.02), yy, 0), 8) if zs > 0 else \
                        cyl_eixo(p, 'aco', 0.005, -Z - 0.004, -Z, 'z', (xs * (X - 0.02), yy, 0), 8)
    # travamento em X atras
    p.seg('aco_pintado', (-X + 0.02, 0.12, -Z - 0.0015), (X - 0.02, 0.88, -Z - 0.0015), 0.014, 0.002)
    p.seg('aco_pintado', (X - 0.02, 0.12, -Z - 0.0035), (-X + 0.02, 0.88, -Z - 0.0035), 0.014, 0.002)


def _guarda_carcaca(p, mat, X, H, Z0, Z1):
    carcaca(p, mat, -X, X, 0.08, H - 0.08, Z0, Z1, t=0.02)
    p.box(mat, -X + 0.03, X - 0.03, 0.0, 0.08, Z0 + 0.02, Z1 - 0.02)
    prof_x(p, mat, -X - 0.012, X + 0.012, crect(Z1 - 0.03, Z1 + 0.012, 0.0, 0.06, 0.004))
    for xs in (-1, 1):
        a, b = sorted((xs * X, xs * (X + 0.012))); prof_z(p, mat, Z0, Z1 + 0.012, crect(a, b, 0.0, 0.06, 0.004))
    prof_x(p, mat, -X - 0.025, X + 0.025, [(Z1 - 0.02, H - 0.08), (Z1 + 0.01, H - 0.08), (Z1 + 0.01, H - 0.06), (Z1 + 0.025, H - 0.045),
                                            (Z1 + 0.025, H - 0.02), (Z1 + 0.035, H - 0.01), (Z1 + 0.035, H), (Z1 - 0.02, H)])
    p.box(mat, -X - 0.025, X + 0.025, H - 0.08, H, Z0, Z1 - 0.02)
    for xs in (-1, 1):
        pts = [(Z0, H - 0.08), (Z1 + 0.01, H - 0.08), (Z1 + 0.01, H - 0.06), (Z1 + 0.025, H - 0.045), (Z1 + 0.025, H - 0.02), (Z1 + 0.035, H - 0.01), (Z1 + 0.035, H), (Z0, H)]
        m = trimesh.creation.extrude_polygon(Polygon([(z, y) for z, y in pts]).buffer(0), 0.025)
        m.vertices = np.stack([xs * X + (m.vertices[:, 2] if xs > 0 else -m.vertices[:, 2]), m.vertices[:, 1], m.vertices[:, 0]], 1)
        if m.volume < 0: m.invert()
        p.add(mat, m)


@item('guarda_roupa', 'Guarda-roupa 2 portas', 'mobilias', 'quarto', conteiner=True, saque=['roupas', 'tecido', 'mochila'], slots=10,
      barricada=True, comodos=['quarto'])
def guarda_roupa(M):
    p = M.base; X, H, Z0, Z1 = 0.5, 2.0, -0.29, 0.27; mat = 'madeira_escura'
    _guarda_carcaca(p, mat, X, H, Z0, Z1)
    p.box(mat, -X + 0.02, X - 0.02, 0.40, 0.42, Z0 + 0.008, Z1)                          # travessa sobre a gaveta
    p.box(mat, -X + 0.02, X - 0.02, 1.70, 1.718, Z0 + 0.008, Z1 - 0.02)                  # maleiro
    cyl_eixo(p, 'inox', 0.012, -X + 0.02, X - 0.02, 'x', (0, 1.64, -0.01), 16)
    for x in (-0.25, -0.05, 0.2):                                                     # cabides
        p.cyl('aco', 0.002, 1.60, 1.645, x=x, z=-0.01, sec=6)
        cyl_eixo(p, 'aco', 0.0025, -0.006, 0.006, 'z', (x, 1.645, -0.01), 6)
        for s in (-1, 1): p.seg('madeira', (x, 1.60, -0.01), (x + s * 0.2, 1.52, -0.01), 0.012, 0.008)
        cyl_eixo(p, 'madeira', 0.006, x - 0.2, x + 0.2, 'x', (0, 1.52, -0.01), 8)
    for nome, hx0, sgn in (('porta_esq', -X, -1), ('porta_dir', X, 1)):
        q = M.parte(nome, (hx0, 0, Z1 + 0.022), 'porta', eixo='y', abre_graus=105 * sgn)
        a0, a1 = sorted((hx0 - sgn * 0.003, -sgn * 0.0015))
        almofadada(q, mat, a0, a1, 0.425, H - 0.085, Z1, Z1 + 0.022, borda=0.075, n=2)
        pegador(q, 'cobre', -sgn * 0.04, 1.05, Z1 + 0.022)
        for yy in (0.52, 1.75): q.box('cobre', *sorted((hx0 - sgn * 0.001, hx0 + sgn * 0.004)), yy, yy + 0.06, Z1 + 0.004, Z1 + 0.016)
    g = M.parte('gaveta', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.4])
    almofadada(g, mat, -X + 0.003, X - 0.003, 0.085, 0.395, Z1, Z1 + 0.022, borda=0.06, n=1)
    carcaca(g, mat, -X + 0.03, X - 0.03, 0.09, 0.36, Z0 + 0.03, Z1, t=0.012, topo=False)
    for x in (-0.25, 0.25): pegador(g, 'cobre', x, 0.24, Z1 + 0.022)


@item('comoda', 'Cômoda 3 gavetas', 'mobilias', 'quarto', conteiner=True, saque=['roupas', 'remedios', 'pilhas'], slots=6, comodos=['quarto'])
def comoda(M):
    p = M.base; X, Z0, Z1, mat = 0.45, -0.22, 0.20, 'madeira'
    carcaca(p, mat, -X, X, 0.10, 0.82, Z0, Z1, t=0.018)
    p.cham(mat, -X - 0.015, X + 0.015, 0.82, 0.85, Z0 - 0.005, Z1 + 0.04, 0.006)
    prof_x(p, mat, -X - 0.008, X + 0.008, [(Z1, 0.10), (Z1 + 0.026, 0.10), (Z1 + 0.026, 0.115), (Z1 + 0.018, 0.13), (Z1, 0.13)])
    for xs in (-1, 1):
        for zz in (Z0 + 0.03, Z1 - 0.01):
            cx = xs * (X - 0.035); p.hull(mat, [(cx + dx, 0.10, zz + dz) for dx in (-0.025, 0.025) for dz in (-0.025, 0.025)] +
                                         [(cx + dx, 0.0, zz + dz) for dx in (-0.014, 0.014) for dz in (-0.014, 0.014)])
    for i, (y0, y1) in enumerate(((0.13, 0.35), (0.355, 0.575), (0.58, 0.815))):
        for y in (y0 - 0.004, ):
            p.box(mat, -X + 0.018, X - 0.018, y - 0.001, y + 0.003, Z0 + 0.008, Z1)
        g = M.parte(f'gaveta_{i + 1}', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.3])
        almofadada(g, mat, -X + 0.02, X - 0.02, y0, y1, Z1, Z1 + 0.024, borda=0.04, n=1, c=0.003)
        carcaca(g, mat, -X + 0.03, X - 0.03, y0 + 0.01, y1 - 0.03, Z0 + 0.02, Z1, t=0.012, topo=False)
        for x in (-0.22, 0.22): pegador(g, 'cobre', x, (y0 + y1) / 2, Z1 + 0.024)


@item('criado_mudo', 'Criado-mudo', 'mobilias', 'quarto', conteiner=True, saque=['remedios', 'pilhas', 'livros'], slots=3, comodos=['quarto'])
def criado_mudo(M):
    p = M.base; X, Z0, Z1, mat = 0.225, -0.19, 0.18, 'madeira'
    carcaca(p, mat, -X, X, 0.12, 0.53, Z0, Z1, t=0.016)
    p.cham(mat, -X - 0.012, X + 0.012, 0.53, 0.555, Z0 - 0.004, Z1 + 0.03, 0.005)
    p.box(mat, -X + 0.016, X - 0.016, 0.33, 0.345, Z0 + 0.008, Z1)
    for xs in (-1, 1):
        for zz in (Z0 + 0.02, Z1 - 0.02): pe_torneado(p, mat, xs * (X - 0.02), zz, 0.0, 0.125, r=0.017)
    g = M.parte('gaveta', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.26])
    almofadada(g, mat, -X + 0.004, X - 0.004, 0.35, 0.525, Z1, Z1 + 0.02, borda=0.035, n=1, c=0.003)
    carcaca(g, mat, -X + 0.02, X - 0.02, 0.355, 0.5, Z0 + 0.02, Z1, t=0.01, topo=False)
    pegador(g, 'cobre', 0, 0.44, Z1 + 0.02)


def _cama(M, wc, lc):
    """Cama com cabeceira em -Z: colchao wc x lc (m)."""
    p = M.base; mat = 'madeira'; X = wc / 2 + 0.04; Zh, Zp = -lc / 2 - 0.04, lc / 2 + 0.04
    for xs in (-1, 1):
        for (zc, h) in ((Zh + 0.03, 1.0), (Zp - 0.03, 0.6)):
            cx = xs * (X - 0.03); p.cham(mat, cx - 0.035, cx + 0.035, 0.0, h, zc - 0.035, zc + 0.035, 0.006)
            torno(p, mat, [(0.038, h), (0.042, h + 0.012), (0.03, h + 0.03), (0.012, h + 0.05)], 16, 'y', (cx, 0, zc))
        p.cham(mat, xs * (X - 0.06) - 0.02, xs * (X - 0.06) + 0.02, 0.18, 0.33, Zh + 0.06, Zp - 0.06, 0.005)   # lateral
    for (zc, y0, y1) in ((Zh + 0.03, 0.40, 0.92), (Zp - 0.03, 0.40, 0.52)):           # cabeceira e peseira
        p.cham(mat, -X + 0.065, X - 0.065, y1 - 0.06, y1, zc - 0.025, zc + 0.025, 0.006)
        p.cham(mat, -X + 0.065, X - 0.065, 0.20, 0.40 if y1 > 0.6 else 0.30, zc - 0.022, zc + 0.022, 0.006)
        if y1 > 0.6:
            n = int(wc / 0.12)
            for x in np.linspace(-X + 0.12, X - 0.12, n): p.cham(mat, x - 0.02, x + 0.02, 0.40, y1 - 0.06, zc - 0.012, zc + 0.012, 0.004)
    for z in np.linspace(Zh + 0.1, Zp - 0.1, 9): p.box('madeira_crua', -X + 0.08, X - 0.08, 0.30, 0.32, z - 0.04, z + 0.04)   # estrado
    fofo(p, 'colchao', 0, 0.42, 0, wc / 2, 0.10, lc / 2, 0.15, 0.12, (16, 36))
    fofo(p, 'lencol', 0, 0.428, -0.02, wc / 2 + 0.006, 0.098, lc / 2 - 0.01, 0.15, 0.12, (16, 36))
    zc0 = -lc / 2 + 0.55                                                                 # cobertor da dobra para os pes
    fofo(p, 'cobertor', 0, 0.44, (zc0 + lc / 2 + 0.03) / 2, wc / 2 + 0.025, 0.095, (lc / 2 + 0.03 - zc0) / 2, 0.12, 0.1, (16, 36))
    fofo(p, 'lencol', 0, 0.527, zc0 + 0.02, wc / 2 + 0.02, 0.016, 0.07, 0.4, 0.2, (12, 24))
    for xs in (-1, 1): p.cham('cobertor', *sorted((xs * (wc / 2 + 0.01), xs * (wc / 2 + 0.03))), 0.24, 0.45, zc0 + 0.06, lc / 2 + 0.01, 0.01)
    p.cham('cobertor', -wc / 2 - 0.02, wc / 2 + 0.02, 0.24, 0.45, lc / 2 + 0.0, lc / 2 + 0.03, 0.01)
    n = 2 if wc > 1.2 else 1
    for i in range(n):
        x = (i - (n - 1) / 2) * (wc / n)
        fofo(p, 'travesseiro', x, 0.565, -lc / 2 + 0.24, min(0.32, wc / n / 2 - 0.04), 0.065, 0.2, 0.35, 0.45, (16, 28), rot_x=-0.15)


@item('cama_casal', 'Cama de casal', 'mobilias', 'quarto', conteiner=False, deitar=True, comodos=['quarto'], estacao='cama')
def cama_casal(M): _cama(M, 1.38, 1.88)


@item('cama_solteiro', 'Cama de solteiro', 'mobilias', 'quarto', conteiner=False, deitar=True, comodos=['quarto'], estacao='cama')
def cama_solteiro(M): _cama(M, 0.88, 1.88)


@item('mesa_jantar', 'Mesa de jantar', 'mobilias', 'sala', barricada=True, comodos=['sala', 'cozinha'])
def mesa_jantar(M):
    p = M.base; X, Z, mat = 0.70, 0.40, 'madeira'
    p.cham(mat, -X, X, 0.725, 0.76, -Z, Z, 0.008)
    prof_x(p, mat, -X + 0.01, X - 0.01, [(Z - 0.004, 0.725), (Z - 0.004, 0.718), (Z - 0.012, 0.712), (Z - 0.03, 0.712), (Z - 0.03, 0.725)])
    for zs in (-1, 1): p.cham(mat, -X + 0.08, X - 0.08, 0.62, 0.725, *sorted((zs * (Z - 0.07), zs * (Z - 0.09))), 0.004)
    for xs in (-1, 1): p.cham(mat, *sorted((xs * (X - 0.07), xs * (X - 0.09))), 0.62, 0.725, -Z + 0.08, Z - 0.08, 0.004)
    for xs in (-1, 1):
        for zs in (-1, 1):
            cx, cz = xs * (X - 0.08), zs * (Z - 0.08)
            p.cham(mat, cx - 0.032, cx + 0.032, 0.60, 0.725, cz - 0.032, cz + 0.032, 0.004)
            torno(p, mat, [(0.02, 0.0), (0.024, 0.012), (0.019, 0.04), (0.017, 0.2), (0.026, 0.33), (0.03, 0.4), (0.022, 0.46), (0.032, 0.52),
                           (0.032, 0.56), (0.026, 0.58), (0.03, 0.60)], 16, 'y', (cx, 0, cz))


@item('cadeira', 'Cadeira de madeira', 'mobilias', 'sala', comodos=['sala', 'cozinha'], sentar=True)
def cadeira(M):
    p = M.base; X, Z0, Z1, mat = 0.21, -0.2, 0.21, 'madeira'; ys = 0.44
    for xs in (-1, 1):
        cx = xs * (X - 0.02)
        torno(p, mat, [(0.014, 0.0), (0.017, 0.01), (0.015, 0.1), (0.019, 0.2), (0.016, 0.3), (0.019, 0.4), (0.02, ys)], 14, 'y', (cx, 0, Z1 - 0.02))
        p.hull(mat, [(cx + dx, 0, Z0 + 0.02 + dz) for dx in (-0.015, 0.015) for dz in (-0.015, 0.015)] +
               [(cx + dx, 0.92, Z0 - 0.03 + dz) for dx in (-0.016, 0.016) for dz in (-0.014, 0.014)])
        cyl_eixo(p, mat, 0.009, Z0 + 0.02, Z1 - 0.02, 'z', (cx, 0.16, 0), 10)
        torno(p, mat, [(0.017, 0.92), (0.02, 0.93), (0.012, 0.95), (0.0, 0.955)], 12, 'y', (cx, 0, Z0 - 0.03))
    cyl_eixo(p, mat, 0.009, -X + 0.02, X - 0.02, 'x', (0, 0.2, Z1 - 0.02), 10); cyl_eixo(p, mat, 0.009, -X + 0.02, X - 0.02, 'x', (0, 0.2, Z0 + 0.02), 10)
    p.cham(mat, -X, X, ys - 0.03, ys, Z0 - 0.005, Z1 + 0.01, 0.006)
    for (y, h) in ((0.86, 0.06), (0.58, 0.035)):
        zc = Z0 - 0.02 - (y - ys) / (0.92 - ys) * 0.03
        p.cham(mat, -X + 0.01, X - 0.01, y - h / 2, y + h / 2, zc - 0.012, zc + 0.012, 0.004)
    for x in (-0.08, 0.0, 0.08): p.seg(mat, (x, 0.6, Z0 - 0.018), (x, 0.83, Z0 - 0.025), 0.022, 0.014)
    fofo(p, 'tecido_cadeira', 0, ys + 0.022, 0.005, X - 0.015, 0.022, (Z1 - Z0) / 2 - 0.01, 0.3, 0.2, (12, 24))
    for xs in (-1, 1): p.seg('tecido_cadeira', (xs * 0.07, ys + 0.03, Z0 + 0.005), (xs * 0.09, ys + 0.002, Z0 - 0.025), 0.008, 0.003)


@item('sofa', 'Sofá 3 lugares', 'mobilias', 'sala', barricada=True, sentar=True, deitar=True, comodos=['sala'], conteiner=True,
      saque=['moedas', 'pilhas'], slots=2)
def sofa(M):
    p = M.base; X, Z0, Z1, mat = 0.95, -0.44, 0.42, 'tecido_sofa'
    p.cham(mat, -X + 0.16, X - 0.16, 0.13, 0.40, Z0 + 0.02, Z1 - 0.02, 0.02)
    p.cham(mat, -X + 0.06, X - 0.06, 0.13, 0.86, Z0, Z0 + 0.2, 0.04)
    fofo(p, mat, 0, 0.84, Z0 + 0.1, X - 0.06, 0.04, 0.1, 0.4, 0.3, (12, 28))
    for xs in (-1, 1):
        cx = xs * (X - 0.08)
        p.cham(mat, cx - 0.08, cx + 0.08, 0.13, 0.58, Z0 + 0.02, Z1, 0.03)
        fofo(p, mat, cx, 0.6, (Z0 + Z1) / 2 + 0.01, 0.095, 0.06, (Z1 - Z0) / 2, 0.35, 0.25, (12, 24))
        for zz in (Z0 + 0.06, Z1 - 0.06):
            torno(p, 'madeira_escura', [(0.022, 0.0), (0.028, 0.10), (0.03, 0.13)], 12, 'y', (xs * (X - 0.08), 0, zz))
    wc = (2 * X - 0.32) / 3
    for i in range(3):
        cx = -X + 0.16 + wc * (i + 0.5)
        fofo(p, 'tecido_sofa', cx, 0.465, 0.04, wc / 2 - 0.006, 0.07, (Z1 - 0.2 - Z0) / 2 + 0.03, 0.22, 0.18, (14, 28))
        fofo(p, 'tecido_sofa', cx, 0.66, Z0 + 0.27, wc / 2 - 0.008, 0.19, 0.075, 0.25, 0.3, (16, 24), rot_x=-0.18)
    fofo(p, 'tecido_almofada', -X + 0.32, 0.62, Z0 + 0.38, 0.2, 0.2, 0.06, 0.3, 0.3, (14, 22), rot_x=-0.35)


@item('armario_banheiro', 'Armário de banheiro com espelho', 'mobilias', 'banheiro', montagem='wall', conteiner=True,
      saque=['remedios', 'higiene'], slots=4, comodos=['banheiro'], altura_sugerida_m=1.2)
def armario_banheiro(M):
    p = M.base; X, H, D, mat = 0.25, 0.65, 0.14, 'madeira_branca'
    carcaca(p, mat, -X, X, 0.0, H, 0.0, D, t=0.016)
    for y in (0.22, 0.43):
        p.box('vidro_prateleira', -X + 0.016, X - 0.016, y, y + 0.006, 0.01, D - 0.02)
        for xs in (-1, 1): p.cyl('aco_polido', 0.003, y - 0.006, y, x=xs * (X - 0.024), z=D - 0.03, sec=6)
    p.cham(mat, -X - 0.01, X + 0.01, H, H + 0.05, -0.0, D + 0.02, 0.004)
    p.box('lamp_glass', -X + 0.04, X - 0.04, H + 0.004, H + 0.02, D + 0.018, D + 0.022)
    p.box('inox', -X + 0.03, X - 0.03, H + 0.002, H + 0.022, D + 0.016, D + 0.018)
    q = M.parte('porta_espelho', (-X, 0, D + 0.02), 'porta', eixo='y', abre_graus=-100)
    q.cham(mat, -X, X, 0.002, H - 0.002, D, D + 0.02, 0.005)
    q.box('espelho', -X + 0.03, X - 0.03, 0.03, H - 0.03, D + 0.019, D + 0.022)
    q.cham('aco_polido', X - 0.03, X - 0.012, 0.25, 0.4, D + 0.02, D + 0.03, 0.003)


@item('caixa_madeira', 'Caixote de madeira', 'mobilias', 'deposito', conteiner=True, saque=['comida', 'materiais', 'ferramentas', 'armas'],
      slots=8, comodos=['deposito', 'garagem', 'estacao'], barricada=True)
def caixa_madeira(M):
    p = M.base; X, Z, H, mat = 0.40, 0.28, 0.52, 'madeira_crua'; e = 0.02
    for fz in (-1, 1):                                                                # tabuas das faces +-Z e +-X com frestas
        for i in range(3):
            y0 = 0.01 + i * 0.17; z0, z1 = sorted((fz * Z, fz * (Z - e)))
            p.cham(mat, -X + e, X - e, y0, y0 + 0.16, z0, z1, 0.003)
            x0, x1 = sorted((fz * X, fz * (X - e))); p.cham(mat, x0, x1, y0, y0 + 0.16, -Z + e, Z - e, 0.003)
    for i in range(4): p.box(mat, -X + e, X - e, 0.0, 0.02, -Z + e + i * 0.13, -Z + e + i * 0.13 + 0.11)
    for xs in (-1, 1):                                                                # cantoneiras e travessas
        for zs in (-1, 1):
            x0, x1 = sorted((xs * X, xs * (X + 0.022))); p.cham(mat, x0, x1, 0.0, H, *sorted((zs * (Z - 0.06), zs * (Z + 0.0))), 0.003)
            z0, z1 = sorted((zs * Z, zs * (Z + 0.022))); p.cham(mat, *sorted((xs * (X - 0.06), xs * X)), 0.0, H, z0, z1, 0.003)
        for zs in (-1, 1):
            z0, z1 = sorted((zs * Z, zs * (Z + 0.022)))
            for yb in (0.0, H - 0.06): p.cham(mat, -X + 0.06, X - 0.06, yb, yb + 0.06, z0, z1, 0.003)
            p.seg(mat, (-X + 0.07, 0.07, zs * (Z + 0.011)), (X - 0.07, H - 0.07, zs * (Z + 0.011)), 0.06, 0.02)
    for xs in (-1, 1):
        for zs in (-1, 1):
            for y in (0.03, H - 0.03):
                cyl_eixo(p, 'aco', 0.004, *sorted((zs * (Z + 0.022), zs * (Z + 0.024))), 'z', (xs * (X - 0.03), y, 0), 6)
    q = M.parte('tampa', (0, H, -Z - 0.022), 'tampa', eixo='x', abre_graus=-105)
    for i in range(4):
        z0 = -Z - 0.02 + i * 0.15; q.cham(mat, -X - 0.02, X + 0.02, H, H + 0.02, z0, z0 + 0.145, 0.003)
    for x in (-X + 0.04, 0.0, X - 0.04): q.cham(mat, x - 0.03, x + 0.03, H + 0.02, H + 0.04, -Z, Z, 0.003)
    for x in (-X + 0.04, 0.0, X - 0.04):
        for z in (-Z + 0.05, Z - 0.05): q.cyl('aco', 0.004, H + 0.04, H + 0.042, x=x, z=z, sec=6)


# ---------------------------------------------------------------------------- LOOT
@item('lata_feijao', 'Lata de feijão', 'loot', 'comida', recurso='comida', valor=1, peso_kg=0.45, empilha=10,
      onde=['supermercado', 'casas', 'galeria', 'diner', 'armazem'], efeito='fome -25')
def lata_feijao(M):
    p = M.base; r, h = 0.0375, 0.11
    perf = [(r - 0.003, 0.0), (r, 0.002), (r, 0.006), (r - 0.001, 0.008), (r - 0.001, 0.012)]
    for i in range(6): y = 0.016 + i * 0.015; perf += [(r - 0.001, y), (r - 0.0004, y + 0.004), (r - 0.001, y + 0.008)]
    perf += [(r - 0.001, h - 0.008), (r, h - 0.006), (r + 0.0005, h - 0.002), (r - 0.001, h), (r - 0.004, h - 0.002), (r - 0.012, h - 0.003),
             (r - 0.013, h - 0.0015), (r - 0.02, h - 0.0025), (0, h - 0.0025)]
    torno(p, 'lata', perf, 40)
    mat_imagem('rotulo_feijao', rotulo_lata('FEIJÃO', 'VALE VERDE', (126, 50, 32), (196, 156, 50), graos((96, 40, 30))))
    anel(p, 'rotulo_feijao', r - 0.0012, r + 0.0006, 0.014, 0.098, 40); p.uv['rotulo_feijao'] = uv_cilindro(0.014, 0.098)


@item('lata_sardinha', 'Lata de sardinha', 'loot', 'comida', recurso='comida', valor=1, peso_kg=0.13, empilha=12,
      onde=['supermercado', 'casas', 'diner'], efeito='fome -15')
def lata_sardinha(M):
    p = M.base; a, b, h = 0.053, 0.037, 0.024
    pol = lambda d: Polygon([(np.sign(math.cos(t)) * abs(math.cos(t)) ** 0.5 * (a - d), np.sign(math.sin(t)) * abs(math.sin(t)) ** 0.5 * (b - d))
                             for t in np.linspace(0, 2 * math.pi, 64, endpoint=False)])
    extrudar_xz(p, 'lata', pol(0.001), 0.0, h - 0.002); extrudar_xz(p, 'lata', pol(0.0), h - 0.003, h)
    img = Image.new('RGB', (512, 360), (26, 76, 140)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([30, 40, 482, 320], 40, fill=(236, 230, 210), outline=(210, 170, 60), width=8)
    texto_c(d, (256, 120), 'MAR AZUL', 46, (26, 76, 140)); texto_c(d, (256, 200), 'SARDINHAS', 58, (160, 40, 30)); texto_c(d, (256, 270), 'em óleo · 125 g', 28, (60, 60, 60), False)
    for x in (90, 380): d.ellipse([x - 50, 160, x + 50, 190], fill=(150, 160, 170))
    mat_imagem('rotulo_sardinha', img, 0.35, 0.3)
    extrudar_xz(p, 'rotulo_sardinha', pol(0.006), h, h + 0.0006); p.uv['rotulo_sardinha'] = uv_plano(-a, a, -b, b)
    anel(p, 'aco_polido', 0.008, 0.0105, h + 0.0006, h + 0.0022, 20, 'y', (a - 0.02, 0, 0))
    p.box('aco_polido', a - 0.032, a - 0.018, h + 0.0006, h + 0.0016, -0.003, 0.003)


@item('pacote_arroz', 'Pacote de arroz 1 kg', 'loot', 'comida', recurso='comida', valor=2, peso_kg=1.0, empilha=5,
      onde=['supermercado', 'casas', 'armazem', 'padaria'], efeito='precisa cozinhar: rende 4 refeições')
def pacote_arroz(M):
    p = M.base; a, b, c = 0.085, 0.032, 0.125
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(240, 236, 226)); d.rectangle([0, 0, w, 60], fill=(200, 40, 40)); d.rectangle([0, h - 70, w, h], fill=(200, 40, 40))
        texto_c(d, (w / 2, 30), 'BOM PRATO', 34, (255, 230, 120)); texto_c(d, (w / 2, 200), 'ARROZ', 66, (180, 30, 30), larg=w - 20)
        texto_c(d, (w / 2, 260), 'TIPO 1', 32, (40, 40, 40)); texto_c(d, (w / 2, h - 35), '1 kg', 40, (255, 255, 255))
        for i in range(30): x = 30 + (i * 47) % (w - 60); y = 300 + (i * 29) % 110; d.ellipse([x, y, x + 16, y + 7], fill=(250, 248, 240), outline=(200, 190, 170))
    def tras(d, w, h):
        d.rectangle([0, 0, w, h], fill=(240, 236, 226)); d.rectangle([0, 0, w, 60], fill=(200, 40, 40))
        for i in range(8): d.rectangle([30, 100 + i * 34, w - 30, 112 + i * 34], fill=(150, 140, 130))
    lado = lambda d, w, h: d.rectangle([0, 0, w, h], fill=(200, 40, 40))
    mat_imagem('rotulo_arroz', rotulo_caixa([frente, tras, lado, lado]), 0.5)
    fofo(p, 'rotulo_arroz', 0, b, 0, a, b, c, 0.18, 0.12, (14, 28)); p.uv['rotulo_arroz'] = uv_atlas(-a, a, 0, 2 * b, -c, c, frente='y')
    for zs in (-1, 1): p.cham('plastico_vermelho', -a + 0.006, a - 0.006, b - 0.012, b + 0.012, *sorted((zs * (c - 0.004), zs * (c + 0.01))), 0.003)


@item('caixa_cereal', 'Caixa de flocos de milho', 'loot', 'comida', recurso='comida', valor=1, peso_kg=0.3, empilha=4,
      onde=['supermercado', 'casas', 'escolinha'], efeito='fome -20')
def caixa_cereal(M):
    p = M.base; X, H, Z = 0.095, 0.28, 0.035
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(240, 160, 30)); d.ellipse([-40, h * 0.42, w + 40, h * 0.95], fill=(250, 240, 220))
        texto_c(d, (w / 2, 60), 'SOL DA', 34, (150, 40, 20), larg=w - 110); texto_c(d, (w / 2, 120), 'MANHÃ', 56, (150, 40, 20), larg=w - 20)
        texto_c(d, (w / 2, 180), 'flocos de milho', 24, (90, 40, 20), False)
        for i in range(24): x = 40 + (i * 53) % (w - 80); y = int(h * 0.5) + (i * 37) % int(h * 0.38); d.polygon([(x, y), (x + 24, y + 6), (x + 18, y + 22), (x - 2, y + 16)], fill=(230, 170, 60))
        d.ellipse([w - 90, 10, w - 10, 90], fill=(255, 220, 60))
    def tras(d, w, h):
        d.rectangle([0, 0, w, h], fill=(240, 160, 30)); d.rectangle([20, 40, w - 20, h - 40], fill=(255, 250, 235))
        for i in range(10): d.rectangle([40, 70 + i * 36, w - 40, 80 + i * 36], fill=(180, 160, 140))
    def lado(d, w, h):
        d.rectangle([0, 0, w, h], fill=(240, 160, 30)); texto_c(d, (w / 2, h / 2), 'SOL', 40, (150, 40, 20))
    mat_imagem('rotulo_cereal', rotulo_caixa([frente, tras, lado, lado]), 0.6)
    p.cham('rotulo_cereal', -X, X, 0, H, -Z, Z, 0.0015); p.uv['rotulo_cereal'] = uv_atlas(-X, X, 0, H, -Z, Z)
    p.box('papelao', -X + 0.002, X - 0.002, H - 0.0005, H + 0.0015, -0.002, Z - 0.002)


def _garrafa_perfil(r, h):
    pts = [(r * 0.7, 0.0), (r * 0.95, 0.004), (r, 0.015)]
    for i in range(7): y = 0.03 + i * 0.022; pts += [(r, y), (r * 0.94, y + 0.006), (r, y + 0.012)]
    return pts + [(r, h * 0.62), (r * 0.9, h * 0.72), (r * 0.6, h * 0.82), (r * 0.36, h * 0.9), (r * 0.33, h * 0.93)]


@item('garrafa_agua', 'Garrafa de água 1,5 L', 'loot', 'agua', recurso='agua', valor=1, peso_kg=1.55, empilha=6,
      onde=['supermercado', 'casas', 'posto', 'diner', 'galeria'], efeito='sede -40')
def garrafa_agua(M):
    p = M.base; r, h = 0.045, 0.32
    perf = _garrafa_perfil(r, h); torno(p, 'pet', perf, 36)
    agua = [(max(a - 0.0015, 0.001), y) for a, y in perf if y < h * 0.7]
    agua = [(a, max(y, 0.003)) for a, y in agua] + [(agua[-1][0], h * 0.66)]
    torno(p, 'agua', agua, 36)
    anel(p, 'pet', r * 0.31, r * 0.4, h * 0.93, h * 0.935, 24)
    torno(p, 'plastico_branco', [(r * 0.38, h * 0.935), (r * 0.38, h * 0.995), (r * 0.34, h)], 24)
    img = Image.new('RGB', (1024, 256), (30, 110, 190)); d = ImageDraw.Draw(img)
    for i in range(0, 1024, 64): d.arc([i - 40, 150, i + 40, 230], 180, 360, fill=(140, 200, 240), width=6)
    for cx in (256, 768): texto_c(d, (cx, 80), 'FONTE CLARA', 50, (255, 255, 255)); texto_c(d, (cx, 135), 'água mineral · 1,5 L', 28, (210, 235, 250), False)
    mat_imagem('rotulo_agua', img, 0.35)
    anel(p, 'rotulo_agua', r - 0.0005, r + 0.0005, 0.105, 0.17, 40); p.uv['rotulo_agua'] = uv_cilindro(0.105, 0.17)


@item('galao_agua', 'Galão de água 5 L', 'loot', 'agua', recurso='agua', valor=4, peso_kg=5.2, empilha=1,
      onde=['supermercado', 'posto', 'quartel', 'galeria'], efeito='sede -40 por uso, 5 usos')
def galao_agua(M):
    p = M.base; X, Z, H = 0.095, 0.075, 0.27
    p.cham('galao_azul', -X, X, 0, H, -Z, Z, 0.022)
    p.cham('agua', -X + 0.004, X - 0.004, 0.004, H * 0.8, -Z + 0.004, Z - 0.004, 0.018)
    torno(p, 'galao_azul', [(0.03, H - 0.01), (0.03, H + 0.012), (0.024, H + 0.02), (0.02, H + 0.024)], 24, 'y', (-0.04, 0, 0))
    torno(p, 'plastico_branco', [(0.022, H + 0.024), (0.022, H + 0.045), (0.019, H + 0.048)], 24, 'y', (-0.04, 0, 0))
    varrer(p, 'galao_azul', Polygon([(-0.008, -0.012), (0.008, -0.012), (0.008, 0.012), (-0.008, 0.012)]),
           [(0.0, H - 0.005, 0), (0.005, H + 0.03, 0), (0.035, H + 0.05, 0), (0.07, H + 0.03, 0), (0.08, H - 0.005, 0)])
    for i in range(5): p.box('galao_azul', -X - 0.0015, -X, 0.04 + i * 0.04, 0.045 + i * 0.04, -Z + 0.02, Z - 0.02)


@item('kit_medico', 'Kit de primeiros socorros', 'loot', 'remedios', recurso='remedios', valor=6, peso_kg=0.8, empilha=1,
      onde=['quartel', 'escolinha', 'casas', 'motel', 'galeria'], efeito='cura 60 e para sangramento')
def kit_medico(M):
    p = M.base; X, Z, H = 0.13, 0.085, 0.09
    p.cham('plastico_vermelho', -X, X, 0, H * 0.55, -Z, Z, 0.012); p.cham('plastico_vermelho', -X, X, H * 0.55 + 0.002, H, -Z, Z, 0.014)
    p.box('plastico_preto', -X + 0.003, X - 0.003, H * 0.55 - 0.001, H * 0.55 + 0.003, -Z + 0.003, Z - 0.003)
    p.cham('plastico_branco', -0.012, 0.012, H - 0.001, H + 0.004, -0.045, 0.045, 0.002); p.cham('plastico_branco', -0.045, 0.045, H - 0.001, H + 0.004, -0.012, 0.012, 0.002)
    for x in (-0.08, 0.08): p.cham('plastico_branco', x - 0.012, x + 0.012, H * 0.4, H * 0.7, Z - 0.001, Z + 0.008, 0.002)
    varrer(p, 'plastico_preto', Polygon([(-0.006, -0.004), (0.006, -0.004), (0.006, 0.004), (-0.006, 0.004)]),
           [(-0.05, H * 0.5, Z), (-0.045, H * 0.5, Z + 0.025), (0.045, H * 0.5, Z + 0.025), (0.05, H * 0.5, Z)])
    for x in (-0.05, 0.05): p.box('plastico_preto', x - 0.008, x + 0.008, H * 0.42, H * 0.58, Z - 0.002, Z + 0.004)


@item('frasco_remedio', 'Frasco de comprimidos', 'loot', 'remedios', recurso='remedios', valor=3, peso_kg=0.08, empilha=10,
      onde=['casas', 'motel', 'quartel', 'galeria'], efeito='cura doença / alivia dor')
def frasco_remedio(M):
    p = M.base; r, h = 0.021, 0.07
    torno(p, 'ambar', [(r - 0.003, 0), (r, 0.003), (r, h - 0.01), (r - 0.002, h - 0.006), (r - 0.003, h)], 28)
    torno(p, 'plastico_branco', [(r + 0.0008, h - 0.008), (r + 0.0008, h + 0.012), (r - 0.002, h + 0.014)], 28)
    for i in range(20):
        a = i * 2 * math.pi / 20; p.seg('plastico_branco', (math.cos(a) * (r + 0.0012), h - 0.006, math.sin(a) * (r + 0.0012)),
                                         (math.cos(a) * (r + 0.0012), h + 0.01, math.sin(a) * (r + 0.0012)), 0.0016, 0.0012)
    img = Image.new('RGB', (1024, 256), (250, 250, 248)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1024, 50], fill=(40, 140, 90)); d.rectangle([0, 206, 1024, 256], fill=(40, 140, 90))
    for cx in (256, 768): texto_c(d, (cx, 110), 'ANALGÉSICO', 52, (30, 30, 30)); texto_c(d, (cx, 165), '500 mg · 20 comprimidos', 26, (80, 80, 80), False)
    mat_imagem('rotulo_remedio', img, 0.4)
    anel(p, 'rotulo_remedio', r - 0.0004, r + 0.0005, 0.012, 0.05, 32); p.uv['rotulo_remedio'] = uv_cilindro(0.012, 0.05)


@item('atadura', 'Rolo de atadura', 'loot', 'remedios', recurso='remedios', valor=1, peso_kg=0.03, empilha=10,
      onde=['casas', 'quartel', 'escolinha', 'motel'], efeito='para sangramento')
def atadura(M):
    p = M.base; r, w = 0.03, 0.08
    anel(p, 'atadura', 0.009, r, -w / 2, w / 2, 32, 'x', (0, r, 0), chanfro=0.003)
    anel(p, 'papelao', 0.0075, 0.009, -w / 2 + 0.001, w / 2 - 0.001, 24, 'x', (0, r, 0))
    anel(p, 'atadura', r - 0.0002, r + 0.0004, -w / 2 + 0.002, w / 2 - 0.002, 32, 'x', (0, r, 0))           # ultima volta
    p.hull('atadura', [(x, y, z) for x in (-w / 2 + 0.002, w / 2 - 0.002) for (y, z) in ((0.0, 0.004), (0.0012, 0.004), (0.0, 0.045), (0.0010, 0.045))])   # ponta solta


@item('martelo', 'Martelo de unha', 'loot', 'ferramentas', recurso='ferramenta', valor=4, peso_kg=0.6, empilha=1, arma=True, dano=20,
      onde=['casas', 'garagem', 'armazem', 'quartel'], efeito='constrói e repara; arma corpo a corpo leve', pega=[-0.1, 0.017, 0])
def martelo(M):
    p = M.base; L = 0.31
    m = trimesh.creation.revolve(np.array([(0, 0), (0.014, 0.0), (0.016, 0.01), (0.015, 0.08), (0.013, 0.16), (0.011, 0.25), (0.012, L - 0.02), (0, L - 0.02)]), sections=20)
    if m.volume < 0: m.invert()
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])); m.vertices[:, 1] *= 0.75
    m.apply_translation([-L / 2, 0.017, 0]); p.add('madeira', m)
    p.cham('borracha', -L / 2 - 0.001, -L / 2 + 0.11, 0.004, 0.03, -0.017, 0.017, 0.008)
    hx = L / 2 - 0.03; yc = 0.017
    p.cham('aco', hx - 0.014, hx + 0.014, yc - 0.012, yc + 0.012, -0.03, 0.035, 0.003)
    torno(p, 'aco_polido', [(0.014, 0.0), (0.015, 0.018), (0.013, 0.024), (0.0, 0.025)], 20, 'z', (hx, yc, 0.035))
    for s in (-1, 1):
        p.hull('aco', [(hx + s * 0.003 + dx, yc + dy, z) for dx in (-0.004, 0.004) for dy in (-0.01, 0.01) for z in (-0.03,)] +
               [(hx + s * 0.012 + dx, yc + dy, -0.1) for dx in (-0.002, 0.002) for dy in (-0.004, 0.004)])


@item('pe_de_cabra', 'Pé de cabra', 'loot', 'armas', recurso='ferramenta', valor=5, peso_kg=1.2, empilha=1, arma=True, dano=30,
      onde=['garagem', 'quartel', 'estacao', 'armazem'], efeito='abre portas trancadas e caixotes; arma corpo a corpo', pega=[-0.15, 0.012, 0])
def pe_de_cabra(M):
    p = M.base; L = 0.6; r = 0.011; y = r
    hexa = circ(r, 6); cam = [(-L / 2 + 0.04, y, 0)] + [(L / 2 - 0.08, y, 0)]
    gancho = [(L / 2 - 0.08 + 0.06 * math.sin(a), y, 0.06 * (1 - math.cos(a))) for a in np.linspace(0.15, math.pi * 0.95, 10)]
    varrer(p, 'tinta_vermelha', hexa, cam + gancho)
    ponta = [(-L / 2 + 0.04 - 0.035 * math.sin(a), y, -0.035 * (1 - math.cos(a))) for a in np.linspace(0, 0.5, 4)]
    varrer(p, 'tinta_vermelha', hexa, [(-L / 2 + 0.045, y, 0)] + ponta)
    end = np.array(gancho[-1]); prev = np.array(gancho[-2]); d = (end - prev) / np.linalg.norm(end - prev)
    for s in (-1, 1): p.hull('aco', [end + d * 0.002 + np.array([0, dy, 0]) + np.array([-d[2], 0, d[0]]) * s * 0.004 for dy in (-0.008, 0.008)] +
                             [end + d * 0.03 + np.array([0, dy, 0]) + np.array([-d[2], 0, d[0]]) * s * 0.006 for dy in (-0.006, 0.006)])
    e2 = np.array(ponta[-1]); d2 = (e2 - np.array(ponta[-2])); d2 /= np.linalg.norm(d2)
    p.hull('aco', [e2 + np.array([0, dy, dz]) for dy in (-r, r) for dz in (-r * 0.8, r * 0.8)] + [e2 + d2 * 0.035 + np.array([0, dy, dz]) for dy in (-0.002, 0.002) for dz in (-0.012, 0.012)])


@item('machado', 'Machado', 'loot', 'armas', recurso='ferramenta', valor=8, peso_kg=1.6, empilha=1, arma=True, dano=45,
      onde=['quartel', 'armazem', 'casa_de_campo', 'garagem'], efeito='corta lenha e arromba; arma corpo a corpo forte', pega=[-0.25, 0.018, 0])
def machado(M):
    p = M.base; L = 0.72; y = 0.018
    cam = [(-L / 2 + 0.03 * i / 10 + (L - 0.03) * i / 10, y, 0.012 * math.sin(i / 10 * math.pi)) for i in range(11)]
    sec = Polygon([(0.016 * math.cos(a), 0.011 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)])
    p.add('madeira', _fix(trimesh.creation.sweep_polygon(sec, np.array(cam))))
    torno(p, 'madeira', [(0.0, 0), (0.019, 0), (0.02, 0.012), (0.014, 0.022)], 16, 'x', (-L / 2 - 0.005, y, 0))
    hx = L / 2 - 0.06
    p.hull('aco', [(hx + dx, y + dy, dz) for dx in (-0.03, 0.03) for dy in (-0.017, 0.017) for dz in (-0.03, 0.02)] +
           [(hx + dx, y + dy, 0.13) for dx in (-0.075, 0.075) for dy in (-0.002, 0.002)] + [(hx + dx, y + dy, 0.09) for dx in (-0.045, 0.045) for dy in (-0.012, 0.012)])
    p.hull('aco_polido', [(hx + dx, y + dy, 0.128) for dx in (-0.074, 0.074) for dy in (-0.0028, 0.0028)] + [(hx + dx, y + dy, 0.105) for dx in (-0.06, 0.06) for dy in (-0.007, 0.007)])
    p.cham('aco', hx - 0.024, hx + 0.024, y - 0.016, y + 0.016, -0.06, -0.025, 0.006)


@item('chave_inglesa', 'Chave inglesa', 'loot', 'ferramentas', recurso='ferramenta', valor=3, peso_kg=0.45, empilha=1, arma=True, dano=15,
      onde=['garagem', 'posto', 'quartel', 'casas'], efeito='desmonta sucata e repara geradores', pega=[-0.07, 0.006, 0])
def chave_inglesa(M):
    p = M.base; t = 0.012
    cabo = Point(-0.1, 0).buffer(0.013, 8).union(sbox(-0.1, -0.011, 0.05, 0.011)).union(Point(-0.1, 0).buffer(0.008, 8))
    cabo = cabo.difference(Point(-0.1, 0).buffer(0.006, 12))
    cabeca = Point(0.07, 0).buffer(0.03, 16).union(sbox(0.04, -0.016, 0.1, 0.024)).difference(sbox(0.075, -0.009, 0.12, 0.012))
    extrudar_xz(p, 'aco_polido', cabo.union(cabeca), 0.0, t)
    extrudar_xz(p, 'aco', sbox(0.075, -0.009, 0.104, -0.003).union(sbox(0.09, -0.016, 0.104, -0.003)), 0.001, t - 0.001)
    cyl_eixo(p, 'aco', 0.0075, 0.04, 0.072, 'x', (0, t / 2, -0.015), 14)
    for x in np.linspace(0.042, 0.07, 8): anel(p, 'aco', 0.0074, 0.0082, x, x + 0.0015, 14, 'x', (0, t / 2, -0.015))
    extrudar_xz(p, 'aco', sbox(-0.08, -0.004, 0.02, 0.004), t, t + 0.0005)


@item('lanterna', 'Lanterna', 'loot', 'ferramentas', recurso='ferramenta', valor=4, peso_kg=0.3, empilha=1, usa='pilhas',
      onde=['casas', 'quartel', 'posto', 'correios'], efeito='luz na mão (gasta pilhas)', pega=[-0.03, 0.024, 0])
def lanterna(M):
    p = M.base; y = 0.032
    torno(p, 'aco_pintado', [(0.0, -0.12), (0.016, -0.12), (0.019, -0.115), (0.019, 0.04), (0.022, 0.05), (0.032, 0.09), (0.032, 0.11)], 32, 'x', (0, y, 0))
    for x in np.linspace(-0.1, -0.02, 9): anel(p, 'borracha', 0.0185, 0.0205, x, x + 0.004, 28, 'x', (0, y, 0))
    anel(p, 'aco_polido', 0.026, 0.0335, 0.105, 0.118, 32, 'x', (0, y, 0))
    torno(p, 'aco_polido', [(0.008, 0.07), (0.026, 0.106)], 32, 'x', (0, y, 0), fechar=True)
    cyl_eixo(p, 'lamp_glass', 0.026, 0.106, 0.112, 'x', (0, y, 0), 32)
    p.cham('borracha', 0.0, 0.02, y + 0.017, y + 0.024, -0.007, 0.007, 0.002)
    m = trimesh.creation.torus(0.012, 0.0022, major_sections=20, minor_sections=6)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])); m.apply_translation([-0.132, y, 0]); p.add('aco', m)
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4; p.seg('aco_pintado', (0.06, y + 0.026 * math.cos(a), 0.026 * math.sin(a)), (0.09, y + 0.031 * math.cos(a), 0.031 * math.sin(a)), 0.004, 0.003)


@item('taco_madeira', 'Taco de madeira', 'loot', 'armas', recurso='arma', valor=3, peso_kg=0.9, empilha=1, arma=True, dano=25,
      onde=['casas', 'escolinha', 'garagem'], efeito='arma corpo a corpo de alcance médio', pega=[-0.3, 0.035, 0])
def taco_madeira(M):
    p = M.base; L = 0.84; y = 0.034
    perf = [(0.0, -L / 2), (0.022, -L / 2), (0.024, -L / 2 + 0.006), (0.016, -L / 2 + 0.018), (0.013, -L / 2 + 0.03), (0.014, -L / 2 + 0.25),
            (0.018, -L / 2 + 0.4), (0.026, -L / 2 + 0.55), (0.032, -L / 2 + 0.68), (0.034, L / 2 - 0.04), (0.031, L / 2 - 0.01), (0.022, L / 2)]
    torno(p, 'madeira_crua', perf, 28, 'x', (0, y, 0))
    for i in range(10):
        x0 = -L / 2 + 0.035 + i * 0.019; anel(p, 'fita_preta', 0.0133, 0.0148, x0, x0 + 0.017, 24, 'x', (0, y, 0))


@item('tabua', 'Tábua de madeira', 'loot', 'materiais', recurso='madeira', valor=1, peso_kg=2.0, empilha=10,
      onde=['armazem', 'casas', 'estacao', 'quartel', 'deposito'], efeito='barricadas e construção (1 madeira)')
def tabua(M):
    p = M.base; L = 1.5
    p.cham('madeira_crua', -L / 2, L / 2, 0, 0.025, -0.075, 0.075, 0.003)
    for x in (-0.48, 0.21, 0.55):
        torno(p, 'madeira_escura', [(0.009, 0.0), (0.012, 0.0005)], 12, 'y', (x, 0.025, 0.02 * math.sin(x * 9)), fechar=True)
    for xs in (-1, 1):
        for z in (-0.045, 0.045): p.cyl('aco', 0.0025, 0.022, 0.0262, x=xs * (L / 2 - 0.03), z=z, sec=8)


@item('caixa_pregos', 'Caixa de pregos', 'loot', 'materiais', recurso='sucata', valor=2, peso_kg=0.5, empilha=5,
      onde=['armazem', 'garagem', 'casas', 'deposito'], efeito='construção: 20 pregos')
def caixa_pregos(M):
    p = M.base; X, H, Z = 0.055, 0.065, 0.035
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(250, 200, 40)); d.rectangle([0, h * 0.62, w, h], fill=(30, 30, 30))
        texto_c(d, (w / 2, h * 0.25), 'FORTE', 50, (30, 30, 30)); texto_c(d, (w / 2, h * 0.45), 'PREGOS 18x27', 30, (30, 30, 30), larg=w - 20)
        for i in range(5): d.line([(30 + i * 45, h * 0.7), (30 + i * 45, h * 0.95)], fill=(200, 200, 200), width=6); d.line([(18 + i * 45, h * 0.7), (42 + i * 45, h * 0.7)], fill=(200, 200, 200), width=8)
    lado = lambda d, w, h: (d.rectangle([0, 0, w, h], fill=(250, 200, 40)), d.rectangle([0, h * 0.62, w, h], fill=(30, 30, 30)))
    mat_imagem('rotulo_pregos', rotulo_caixa([frente, frente, lado, lambda d, w, h: d.rectangle([0, 0, w, h], fill=(250, 200, 40))]), 0.6)
    p.cham('rotulo_pregos', -X, X, 0, H, -Z, Z, 0.0012); p.uv['rotulo_pregos'] = uv_atlas(-X, X, 0, H, -Z, Z)
    for i, (x, z, a) in enumerate(((-0.02, 0.0, 0.3), (0.0, 0.01, -0.5), (0.025, -0.012, 1.1))):
        c, s = math.cos(a), math.sin(a)
        p.seg('aco', (x - c * 0.024, H + 0.0015, z - s * 0.024), (x + c * 0.024, H + 0.0015, z + s * 0.024), 0.0024, 0.0024)
        p.cyl('aco', 0.0042, H + 0.0003, H + 0.0015 + 0.0012, x=x - c * 0.025, z=z - s * 0.025, sec=10)


@item('fita_adesiva', 'Fita adesiva prata', 'loot', 'materiais', recurso='sucata', valor=2, peso_kg=0.2, empilha=5,
      onde=['casas', 'garagem', 'galeria', 'correios'], efeito='repara armas e barricadas; ingrediente de receitas')
def fita_adesiva(M):
    p = M.base
    anel(p, 'fita_prata', 0.038, 0.055, 0.0, 0.048, 40, chanfro=0.0015)
    anel(p, 'papelao', 0.035, 0.038, 0.0005, 0.0475, 32)
    p.hull('fita_prata', [(x, y, z) for x in (0.054, 0.0555) for y in (0.001, 0.047) for z in (0.0,)] + [(0.057, y, z) for y in (0.002, 0.046) for z in (0.016, 0.0)])


@item('chapa_metal', 'Chapa de metal ondulada', 'loot', 'materiais', recurso='sucata', valor=2, peso_kg=4.0, empilha=4,
      onde=['armazem', 'posto', 'estacao', 'quartel'], efeito='construção: 2 sucata (muros e telhados)')
def chapa_metal(M):
    p = M.base; L, Wd, t, a = 0.9, 0.6, 0.0015, 0.009
    xs = np.linspace(-Wd / 2, Wd / 2, 61); top = [(x, a + a * math.cos(x * 2 * math.pi / 0.076)) for x in xs]
    pts = top + [(x, y - t) for x, y in top[::-1]]
    m = trimesh.creation.extrude_polygon(Polygon(pts).buffer(0), L); m.vertices = np.stack([m.vertices[:, 2] - L / 2, m.vertices[:, 1] + t, m.vertices[:, 0]], 1)
    if m.volume < 0: m.invert()
    v = m.vertices; v[:, 1] += 0.06 * (v[:, 0] / (L / 2)) ** 2 * (v[:, 0] > 0.15) + 0.015 * np.maximum(0, -v[:, 2] / (Wd / 2)) ** 2
    p.add('ferrugem', m)
    for x in (-0.38, 0.0):
        for z in np.arange(-0.266, 0.28, 0.152): p.cyl('aco', 0.004, 2 * a + 0.0005, 2 * a + 0.003, x=x, z=z, sec=8)


@item('cano_metal', 'Cano de ferro', 'loot', 'armas', recurso='sucata', valor=2, peso_kg=1.4, empilha=4, arma=True, dano=22,
      onde=['garagem', 'armazem', 'estacao', 'posto'], efeito='1 sucata ou arma corpo a corpo', pega=[-0.25, 0.017, 0])
def cano_metal(M):
    p = M.base; L = 0.75; r = 0.0168
    anel(p, 'ferrugem', 0.0125, r, -L / 2, L / 2 - 0.04, 24, 'x', (0, r, 0))
    for x0 in (-L / 2, L / 2 - 0.045):
        anel(p, 'aco', 0.0125, r + 0.0012, x0, x0 + 0.004, 24, 'x', (0, r, 0)) if x0 < 0 else None
    anel(p, 'aco', 0.0168, 0.021, L / 2 - 0.05, L / 2, 8, 'x', (0, r, 0), chanfro=0.002)
    for x in np.linspace(L / 2 - 0.09, L / 2 - 0.05, 8): anel(p, 'aco', r - 0.0004, r + 0.0005, x, x + 0.002, 24, 'x', (0, r, 0))


@item('galao_gasolina', 'Galão de gasolina 20 L', 'loot', 'combustivel', recurso='combustivel', valor=10, peso_kg=16.0, empilha=1,
      onde=['posto', 'garagem', 'quartel', 'armazem'], efeito='abastece gerador (8 horas)')
def galao_gasolina(M):
    p = M.base; X, Z, H = 0.17, 0.0825, 0.47
    p.cham('tinta_vermelha', -X, X, 0.004, H - 0.04, -Z, Z, 0.018)
    prof_x(p, 'tinta_vermelha', -X - 0.003, X + 0.003, crect(-0.004, 0.004, 0.004, H - 0.045, 0.002))
    for xs in (-1, 1): prof_y(p, 'tinta_vermelha', 0.01, H - 0.045, crect(*sorted((xs * X, xs * (X + 0.003))), -0.004, 0.004, 0.0015))
    for zs in (-1, 1):
        z0 = zs * Z; zz = zs * (Z + 0.004)
        for (a, b) in (((-X + 0.04, 0.05), (X - 0.04, H - 0.1)), ((X - 0.04, 0.05), (-X + 0.04, H - 0.1))):
            p.seg('tinta_vermelha', (a[0], a[1], (z0 + zz) / 2 - zs * 0.004), (b[0], b[1], (z0 + zz) / 2 - zs * 0.004), 0.022, 0.012)
    p.cham('tinta_vermelha', -X + 0.01, X - 0.01, H - 0.05, H - 0.035, -Z + 0.01, Z - 0.01, 0.006)
    for x in (-0.09, 0.0, 0.09):
        p.cham('tinta_vermelha', x - 0.012, x + 0.012, H - 0.04, H - 0.004, -0.009, 0.009, 0.004)
    cyl_eixo(p, 'tinta_vermelha', 0.011, -0.11, 0.11, 'x', (0, H - 0.006, 0), 14)
    torno(p, 'tinta_vermelha', [(0.022, 0.0), (0.022, 0.03), (0.026, 0.034)], 20, 'y', (X - 0.045, H - 0.045, 0))
    p.cham('tinta_amarela', X - 0.072, X - 0.018, H - 0.012, H + 0.005, -0.028, 0.028, 0.004)
    p.seg('aco', (X - 0.03, H - 0.006, 0.015), (X - 0.02, H - 0.03, 0.03), 0.004, 0.004)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('tinta_vermelha', xs * (X - 0.03) - 0.02, xs * (X - 0.03) + 0.02, 0.0, 0.012, zs * (Z - 0.02) - 0.015, zs * (Z - 0.02) + 0.015, 0.003)


@item('pilhas', 'Cartela de pilhas AA', 'loot', 'energia', recurso='energia', valor=3, peso_kg=0.1, empilha=10,
      onde=['casas', 'correios', 'galeria', 'posto', 'supermercado'], efeito='4 cargas para lanterna e rádio')
def pilhas(M):
    p = M.base; X, Z = 0.055, 0.08
    img = Image.new('RGB', (440, 640), (40, 96, 170)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 440, 120], fill=(250, 200, 40)); texto_c(d, (220, 60), 'VOLTA', 70, (30, 30, 30))
    texto_c(d, (220, 560), 'ALCALINA AA · 4', 34, (255, 255, 255)); d.ellipse([200, 30, 240, 70], fill=(40, 96, 170))
    mat_imagem('cartela_img', img, 0.6)
    p.box('cartela_img', -X, X, 0, 0.0015, -Z, Z); p.uv['cartela_img'] = uv_plano(-X, X, -Z, Z)
    p.cham('plastico_transp', -X + 0.006, X - 0.006, 0.0015, 0.018, -Z + 0.025, Z - 0.022, 0.005)
    for i in range(4):
        x = -0.0315 + i * 0.021; c = (x, 0.0085, 0.0)
        torno(p, 'pilha_corpo', [(0.007, -0.025), (0.0072, -0.024), (0.0072, 0.022), (0.007, 0.0235)], 20, 'z', c)
        anel(p, 'cobre', 0.0068, 0.00735, 0.005, 0.0225, 20, 'z', c)
        torno(p, 'aco_polido', [(0.0068, 0.0235), (0.0068, 0.0245), (0.0025, 0.0245), (0.0025, 0.0258)], 16, 'z', c)
        torno(p, 'aco_polido', [(0.0065, -0.0255), (0.0065, -0.025)], 16, 'z', c)


# ============================================================================ lotes seguintes (props/lote2.py, lote3.py, ...)
for _n in range(2, 20):
    _f = os.path.join(AQUI, f'lote{_n}.py')
    if os.path.exists(_f): LOTE[0] = _n; exec(compile(open(_f, encoding='utf-8').read(), _f, 'exec'), globals())


# ============================================================================ exportacao
def exportar(it, raiz):
    M = Montagem(); it['fn'](M)
    sc = trimesh.Scene(); nome = it['id']
    def por(piece, prefixo, parent, T):
        piece2 = P(); piece2.uv = {}; piece2.vertical = it['grupo'] == 'mobilias'
        for k, ms in piece.parts.items():
            for m in ms: mm = m.copy(); mm.apply_transform(T); piece2.add(k, mm)
        for k, f in piece.uv.items():
            piece2.uv[k] = (lambda f, T: (lambda v, n: f(v + T[:3, 3] * -1, n)))(f, T)   # UV calculada nas coordenadas originais
        sub = piece2.scene(prefixo)
        for gname, g in sub.geometry.items():
            sc.add_geometry(g, node_name=gname, geom_name=gname, parent_node_name=parent)
    por(M.base, nome, None, np.eye(4))
    partes = []
    for pt in M.partes:
        T = trimesh.transformations.translation_matrix(pt['origem'])
        sc.graph.update(frame_from=sc.graph.base_frame, frame_to=pt['no'], matrix=T)
        por(pt['peca'], f"{nome}_{pt['no']}", pt['no'], np.linalg.inv(T))
        partes.append({k: v for k, v in pt.items() if k != 'peca'})
    pasta = os.path.join(raiz, it['grupo']); os.makedirs(pasta, exist_ok=True)
    arq = os.path.join(pasta, f'{nome}.glb'); sc.export(arq); glb_jpeg(arq)
    b = sc.bounds; tris = sum(len(g.faces) for g in sc.dump(concatenate=False)) if hasattr(sc, 'dump') else 0
    reg = {k: v for k, v in it.items() if k not in ('fn',)}
    reg.update(arquivo=f"{it['grupo']}/{nome}.glb", tamanho_m=[round(float(x), 3) for x in (b[1] - b[0])], triangulos=int(tris),
               kb=round(os.path.getsize(arq) / 1024, 1))
    if partes: reg['partes'] = partes
    return reg


CABECALHO = {
    'mobilias': {'escala': '1 unidade = 1 m, Y para cima, frente para +Z',
                 'montagem': {'floor': 'pivô no centro da base', 'wall': 'pivô no centro de baixo da face de trás (encosta na parede)'},
                 'partes': 'portas, gavetas e tampas são nós do GLB com origem na dobradiça: tipo porta/tampa gira abre_graus em torno do eixo; '
                           'tipo gaveta desliza o vetor desliza (m)',
                 'campos_jogo': {'conteiner': 'pode ser revistado', 'saque': 'grupos da tabela de saque', 'slots': 'capacidade',
                                 'barricada': 'pode ser empurrado para bloquear porta', 'comodos': 'onde aparece', 'estacao': 'estação de base'}},
    'loot': {'escala': '1 unidade = 1 m, Y para cima; item deitado na pose de repouso, pivô no centro da base',
             'recursos_mvp': ['comida', 'agua', 'madeira', 'sucata', 'remedios', 'combustivel'],
             'campos_jogo': {'recurso': 'recurso do MVP ou tipo de item', 'valor': 'quantidade do recurso que rende', 'peso_kg': 'peso real',
                             'empilha': 'máximo por espaço da mochila', 'onde': 'prédios onde aparece', 'arma/dano': 'arma corpo a corpo',
                             'pega': 'ponto da mão (m) para segurar'}},
}


NOMES = {'cozinha': 'Cozinha', 'quarto': 'Quarto', 'sala': 'Sala', 'banheiro': 'Banheiro', 'deposito': 'Depósito',
         'comida': 'Comida', 'agua': 'Água', 'remedios': 'Remédios', 'ferramentas': 'Ferramentas', 'armas': 'Armas improvisadas',
         'materiais': 'Materiais de construção', 'combustivel': 'Combustível', 'energia': 'Energia',
         'lavanderia': 'Lavanderia', 'escritorio': 'Escritório', 'loja': 'Loja', 'saude': 'Saúde', 'oficina': 'Oficina', 'abrigo': 'Abrigo',
         'roupas': 'Roupas e equipamento', 'utensilios': 'Utensílios', 'eletronicos': 'Luz e eletrônicos', 'higiene': 'Higiene',
         'agricultura': 'Agricultura', 'barricadas': 'Barricadas e alarmes', 'rua': 'Rua e quintal', 'pistas': 'Chaves e pistas', 'sinais': 'Sinais do fim do mundo', 'lembrancas': 'Vida de antes', 'igreja': 'Igreja', 'biblioteca': 'Biblioteca', 'escolinha': 'Escola', 'correios': 'Correios', 'delegacia': 'Delegacia', 'banco': 'Banco', 'quartel': 'Quartel de bombeiros', 'diner': 'Diner e lanchonete', 'padaria': 'Padaria', 'posto': 'Posto', 'cinema': 'Cinema', 'hotel': 'Hotel e motel', 'estacao': 'Estação e rodoviária', 'fabrica': 'Fábrica', 'serraria': 'Serraria', 'fazenda': 'Fazenda', 'armazem': 'Armazém', 'ferrovelho': 'Ferro-velho', 'concessionaria': 'Concessionária', 'barcos': 'Casa de barcos', 'observatorio': 'Observatório', 'piscina': 'Piscina', 'skate': 'Pista de skate', 'minigolfe': 'Minigolfe', 'concha': 'Concha acústica', 'drivein': 'Drive-in'}


def catalogo_md(regs):
    """props/CATALOGO.md: tabelas em portugues geradas a partir dos catalogos."""
    L = ['# Catálogo de mobílias e loot', '', 'Gerado por `props/gerar_props.py` a partir de `mobilias/catalogo.json` e `loot/catalogo.json`. Medidas em metros (largura × altura × profundidade).', '']
    L += ['## Mobílias', '', '| Item | Lote | Cômodo | Medidas | Revistar | Partes móveis | Uso no jogo | Triângulos |', '|---|---|---|---|---|---|---|---|']
    for r in regs['mobilias']:
        usos = [u for u, k in (('barricada', 'barricada'), ('dormir', 'deitar'), ('sentar', 'sentar')) if r.get(k)]
        rev = f"{r['slots']} espaços: {', '.join(r['saque'])}" if r.get('conteiner') else '-'
        pt = ', '.join(p['no'] for p in r.get('partes', [])) or '-'
        L.append(f"| {r['nome']} (`{r['id']}`) | {r['lote']} | {NOMES[r['categoria']]} | {' × '.join(f'{x:.2f}' for x in r['tamanho_m'])} | {rev} | {pt} | {', '.join(usos) or '-'} | {r['triangulos']} |")
    L += ['', '## Loot', '', '| Item | Lote | Categoria | Recurso | Rende | Peso | Empilha | Efeito | Aparece em |', '|---|---|---|---|---|---|---|---|---|']
    for r in regs['loot']:
        L.append(f"| {r['nome']} (`{r['id']}`) | {r['lote']} | {NOMES[r['categoria']]} | {r['recurso']} | {r['valor']} | {r['peso_kg']} kg | {r['empilha']} | {r['efeito']}"
                 f"{' (dano ' + str(r['dano']) + ')' if r.get('arma') else ''} | {', '.join(r['onde'])} |")
    import re
    open(os.path.join(AQUI, 'CATALOGO.md'), 'w', encoding='utf-8').write(re.sub(r'(\d)\.(\d)', r'\1,\2', '\n'.join(L)) + '\n')


def main(ids):
    materiais(); raiz = AQUI; regs = {'mobilias': [], 'loot': []}
    cats = {}
    for g in regs:
        f = os.path.join(raiz, g, 'catalogo.json')
        if ids and os.path.exists(f): regs[g] = [r for r in json.load(open(f, encoding='utf-8'))['itens'] if r['id'] not in ids]
    for id_, it in ITENS.items():
        if ids and id_ not in ids: continue
        r = exportar(it, raiz); regs[it['grupo']].append(r)
        print(f"{id_:18s} {r['triangulos']:7d} tris {r['kb']:7.1f} KB  {r['tamanho_m']}")
    ordem = list(ITENS)
    for g, lista in regs.items():
        lista.sort(key=lambda r: ordem.index(r['id']) if r['id'] in ordem else 999)
        os.makedirs(os.path.join(raiz, g), exist_ok=True)
        json.dump(dict(CABECALHO[g], itens=lista), open(os.path.join(raiz, g, 'catalogo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    catalogo_md(regs)


if __name__ == '__main__':
    main(sys.argv[1:])
