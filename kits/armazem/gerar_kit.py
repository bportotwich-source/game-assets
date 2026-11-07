"""Kit 24: armazem de secos e molhados com celeiro, em ALTO DETALHE (scripts/detalhe/detalhe.py).
Loja de tabuas sobrepostas 10 x 14 m com fachada falsa e letreiro, varanda de 2,6 m com telhado de chapa, telhado de duas aguas
de telhas atras da fachada; celeiro vermelho 12 x 12 m de tabua e mata-junta com telhado holandes (gambrel) de chapa com
nervuras, portao de 2 folhas, porta do palheiro e capuz da talha. Corredor de carga de 2,4 m entre os dois.
Y para cima, 1 unidade = 1 m. Padrao de medidas: PADRAO_METRICAS.md.
Dependencias: trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'detalhe'))
from detalhe import *
import detalhe as D
from PIL import ImageDraw, ImageFont, ImageFilter
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT + '/pieces', exist_ok=True)
configurar(cores={'siding': (138, 158, 174), 'shingles': (86, 88, 96), 'deck': (146, 108, 74), 'floor': (168, 122, 82), 'stone': (150, 144, 134),
                  'barn': (150, 44, 38), 'planks': (160, 126, 90), 'metal': (96, 100, 108), 'ceiling': (226, 230, 222), 'gutter': (196, 198, 196),
                  'signbk': (36, 74, 54), 'concrete': (170, 166, 158)},
           texturas={'siding': 'siding', 'shingles': 'shingles', 'plaster': 'plaster', 'deck': 'deck', 'floor': 'planks', 'stone': 'stone2',
                     'barn': 'paint', 'planks': 'planks', 'cap': 'plaster'},
           out=OUT)

# ---------- letreiro: textura pintada (texto original), cor + normal + ORM ----------
def sign_texture(wpx=1536, hpx=512):
    im = Image.new('RGB', (wpx, hpx), (34, 72, 52)); d = ImageDraw.Draw(im)
    rng = np.random.default_rng(5); g = rng.normal(0, 1, (hpx // 8, wpx // 2)); g = np.kron(g, np.ones((8, 2)))
    arr = np.array(im).astype(float) * (1 + 0.035 * g[..., None]); im = Image.fromarray(np.clip(arr, 0, 255).astype('uint8')); d = ImageDraw.Draw(im)
    cream = (236, 222, 180); gold = (206, 168, 92)
    d.rectangle([22, 22, wpx - 23, hpx - 23], outline=cream, width=10); d.rectangle([46, 46, wpx - 47, hpx - 47], outline=gold, width=4)
    for (cx, cy) in ((70, 70), (wpx - 70, 70), (70, hpx - 70), (wpx - 70, hpx - 70)): d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=gold)
    fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 210)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 62)
    def ctext(y, s, f, col, shadow=True):
        b = d.textbbox((0, 0), s, font=f); x = (wpx - (b[2] - b[0])) / 2 - b[0]
        if shadow: d.text((x + 6, y + 6), s, font=f, fill=(16, 34, 24))
        d.text((x, y), s, font=f, fill=col)
    ctext(70, 'ARMAZÉM', fb, cream); ctext(330, 'SECOS  &  MOLHADOS', fs, gold)
    d.line([(300, 312), (wpx - 300, 312)], fill=gold, width=4)
    ctext(410, '— FUNDADO EM 1908 —', ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 34), cream, False)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    nrm = Image.new('RGB', (wpx, hpx), (128, 128, 255)); orm = Image.new('RGB', (wpx, hpx), (255, 150, 0))
    return im, nrm, orm
_sa, _sn, _so = sign_texture()
_sa.save(f'{OUT}/sign_albedo.png'); _sn.save(f'{OUT}/sign_normal.png'); _so.save(f'{OUT}/sign_orm.png')
D.TEX['sign'] = (_sa, _sn, _so)
D.MATS['sign'] = trimesh.visual.material.PBRMaterial(name='sign', baseColorTexture=_sa, normalTexture=_sn, occlusionTexture=_so, metallicRoughnessTexture=_so,
                                                     baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)
TEX = D.TEX; MATS = D.MATS

# ============================================================================ medidas da loja
W = 2.0; T = 0.3; H = 3.6; SLAB = 0.2; RAISE = 0.45
FRIEZE = 3.32; FT = H; HW = H + 0.03; YE = H - 0.03; WT = 0.12
FFT = 7.12                     # topo das tabuas da fachada falsa (35 fiadas); a cornija vai ate 7,36
SX, SZ = 5.0, 7.0              # meia largura e meia profundidade da loja (coordenadas da loja: x de -5 a 5)
CX = -5.0                      # centro da loja no mundo
configurar_tabuas(WT, FRIEZE, 0.2)

def water_table(p, x0=-W / 2, x1=W / 2):
    p.box('stone', x0, x1, -RAISE, 0.0, -T, 0.0)
    prof_x(p, 'trim', x0, x1, [(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)])
def frieze(p, x0=-W / 2, x1=W / 2):
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE), (0.034, FRIEZE), (0.034, FT), (0.0, FT)])
    prof_x(p, 'trim', x0, x1, [(0.0, FRIEZE - 0.05), (0.03, FRIEZE - 0.035), (0.042, FRIEZE - 0.012), (0.042, FRIEZE + 0.02), (0.0, FRIEZE + 0.02)])

# ---------- paredes laterais e dos fundos (16 fiadas) ----------
def wall_window():
    p = Piece(); wall_with_opening(p, 'siding', 1.0, 0.9, 2.6, HW); hole = window(p, 1.0, 0.9, 2.6, 2)
    siding_field(p, [hole]); water_table(p); frieze(p); return p
def wall_small_window():
    p = Piece(); wall_with_opening(p, 'siding', 0.6, 1.7, 2.6, HW); hole = window(p, 0.6, 1.7, 2.6, 1)
    siding_field(p, [hole]); water_table(p); frieze(p); return p
def wall_plain():
    p = Piece(); wall_with_opening(p, 'siding', 0, 0, 0, HW); siding_field(p); water_table(p); frieze(p); return p
def door_surround(p, ow, oy1, depth=0.24):
    x = ow / 2
    p.box('frame', -x, -x + 0.07, 0.015, oy1, -depth, 0.0); p.box('frame', x - 0.07, x, 0.015, oy1, -depth, 0.0); p.box('frame', -x, x, oy1 - 0.07, oy1, -depth, 0.0)
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x + 0.12)))
        prof_y(p, 'trim', -0.03, oy1 + 0.025, crect(a, b, 0.0, 0.036, 0.006, (0, 0, 1, 1)))
        a, b = sorted((s * (x + 0.005), s * (x + 0.125)))
        p.cham('trim', a, b, -0.06, 0.16, 0.0, 0.05, 0.008)
    prof_x(p, 'trim', -x - 0.14, x + 0.14, crect(0.0, 0.04, oy1 + 0.025, oy1 + 0.2, 0.006, (0, 1, 1, 0)))
    prof_x(p, 'trim', -x - 0.17, x + 0.17, [(0.0, oy1 + 0.2), (0.075, oy1 + 0.2), (0.075, oy1 + 0.225), (0.05, oy1 + 0.245), (0.0, oy1 + 0.255)])
def door_sill(p, ow, depth=0.24):
    x = ow / 2
    prof_x(p, 'cap', -x + 0.07, x - 0.07, [(-depth, 0.012), (0.03, 0.012), (0.05, 0.0), (0.05, -0.03), (-depth, -0.03)])
    p.box('stone', -W / 2, W / 2, -RAISE, -0.03, -T, 0.0); p.box('stone', -W / 2, -x, -0.03, 0.0, -T, 0.0); p.box('stone', x, W / 2, -0.03, 0.0, -T, 0.0)
    for (a, b) in ((-W / 2, -x - 0.12), (x + 0.12, W / 2)):
        prof_x(p, 'trim', a, b, [(0.0, -0.1), (0.05, -0.1), (0.05, 0.09), (0.062, 0.094), (0.062, 0.104), (0.0, 0.118)])
def wall_door():
    p = Piece(); ow = 1.0; x = ow / 2; oy1 = 2.3
    wall_with_opening(p, 'siding', ow, 0.015, oy1, HW)
    door_surround(p, ow, oy1)
    p.box('frame', -x + 0.07, -x + 0.085, 0.015, oy1 - 0.07, -0.2, -0.16); p.box('frame', x - 0.085, x - 0.07, 0.015, oy1 - 0.07, -0.2, -0.16)
    door_sill(p, ow); siding_field(p, [(-x - 0.03, x + 0.03, -1.0, oy1 + 0.05)]); frieze(p); return p
def corner_siding(top=FT):
    p = Piece(); e = 0.045
    prof_y(p, 'trim', 0.0, top, [(-T - 0.01, -T - 0.01), (e, -T - 0.01), (e, e - 0.006), (e - 0.006, e), (-T - 0.01, e)])
    p.box('stone', -T - 0.01, 0.01, -RAISE, 0, -T - 0.01, 0.01)
    prof_y(p, 'trim', -0.1, 0.092, [(-T, -T), (e + 0.062, -T), (e + 0.062, e + 0.062), (-T, e + 0.062)])
    p.hull('trim', [(x, y, z) for (x, z) in ((-T, -T), (e + 0.062, -T), (e + 0.062, e + 0.062), (-T, e + 0.062)) for y in (0.092, 0.104)] +
           [(x, 0.118, z) for (x, z) in ((-T, -T), (e, -T), (e, e), (-T, e))])
    if top <= FT + 0.01: prof_y(p, 'trim', FRIEZE - 0.05, FRIEZE + 0.02, [(-T, -T), (e + 0.012, -T), (e + 0.012, e + 0.012), (-T, e + 0.012)])
    return p

# ---------- fachada falsa: vitrines, porta dupla, tabuas ate 7,12 m e cornija com misulas ----------
def cornice(p, x0=-W / 2, x1=W / 2, brackets=(-0.5, 0.5)):
    y = FFT
    prof_x(p, 'trim', x0, x1, [(0.0, y - 0.03), (0.04, y - 0.03), (0.04, y + 0.06), (0.0, y + 0.06)])                      # friso
    prof_x(p, 'trim', x0, x1, [(0.0, y + 0.06), (0.09, y + 0.06), (0.11, y + 0.08), (0.13, y + 0.12), (0.26, y + 0.17), (0.3, y + 0.2), (0.0, y + 0.2)])  # coroa
    prof_x(p, 'trim', x0, x1, crect(-T - 0.03, 0.33, y + 0.2, y + 0.24, 0.008))                                            # capa
    for bx in brackets:   # misulas sob a coroa
        p.hull('trim', [(bx + dx, yy, zz) for dx in (-0.04, 0.04) for (zz, yy) in ((0.04, y - 0.28), (0.04, y + 0.06), (0.11, y + 0.06), (0.1, y - 0.06), (0.06, y - 0.24))])
def front_field(p, holes):
    configurar_tabuas(WT, FFT, 0.2); siding_field(p, holes); configurar_tabuas(WT, FRIEZE, 0.2)
def display_window(p, ow=1.5, oy0=0.6, oy1=2.9):
    """Vitrine: vidro grande com montante, bandeira de 4 vidros, peitoril com pingadeira, guarnicao larga e verga com capa."""
    x = ow / 2; f = 0.06
    p.box('frame', -x, -x + f, oy0, oy1, -0.2, -0.03); p.box('frame', x - f, x, oy0, oy1, -0.2, -0.03); p.box('frame', -x, x, oy1 - f, oy1, -0.2, -0.03)
    st = oy0 + 0.015
    p.box('frame', -x + f, x - f, oy0, st + 0.06, -0.2, -0.03)                                   # travessa de baixo
    yt = oy1 - 0.55
    p.cham('frame', -x + f - 0.002, x - f + 0.002, yt - 0.03, yt + 0.03, -0.16, -0.06, 0.008)      # travessa da bandeira
    p.cham('frame', -0.025, 0.025, st + 0.06, yt - 0.03, -0.15, -0.07, 0.006)                      # montante
    p.box('glass', -x + f - 0.004, x - f + 0.004, st + 0.056, yt - 0.026, -0.113, -0.107)
    p.box('glass', -x + f - 0.004, x - f + 0.004, yt + 0.026, oy1 - f + 0.004, -0.113, -0.107)
    for i in range(1, 4):
        xm = -x + f + (ow - 2 * f) * i / 4; p.cham('frame', xm - 0.015, xm + 0.015, yt + 0.03, oy1 - f, -0.13, -0.09, 0.005)
    prof_x(p, 'trim', -x - 0.13, x + 0.13, [(0.0, st - 0.075), (0.07, st - 0.075), (0.085, st - 0.068), (0.092, st - 0.055), (0.08, st - 0.04), (0.0, st - 0.015)])
    p.box('trim', -x + f, x - f, st - 0.03, st + 0.06, -0.03, 0.0)
    for s in (-1, 1):
        a, b = sorted((s * x, s * (x + 0.11)))
        prof_y(p, 'trim', st - 0.04, oy1 + 0.025, crect(a, b, 0.0, 0.036, 0.006, (0, 0, 1, 1)))
    prof_x(p, 'trim', -x - 0.13, x + 0.13, crect(0.0, 0.04, oy1 + 0.025, oy1 + 0.2, 0.006, (0, 1, 1, 0)))
    prof_x(p, 'trim', -x - 0.16, x + 0.16, [(0.0, oy1 + 0.2), (0.07, oy1 + 0.2), (0.07, oy1 + 0.225), (0.05, oy1 + 0.245), (0.0, oy1 + 0.255)])
    # almofada abaixo da vitrine
    p.cham('trim', -x + 0.08, x - 0.08, 0.16, st - 0.12, 0.0, 0.03, 0.008); p.cham('trim', -x + 0.16, x - 0.16, 0.24, st - 0.2, 0.03, 0.045, 0.006)
    return (-x - 0.03, x + 0.03, 0.0, oy1 + 0.05)
def wall_grid(p, mat, inner, xa, xb, h, holes=(), y0=0.0):
    """Parede estanque de xa a xb com buracos [(x0, x1, y0, y1)]; camada interna para 5 mm abaixo do topo."""
    xs = sorted(set([xa, xb] + [v for hh in holes for v in hh[:2]])); ys = sorted(set([y0, h - 0.005, h] + [max(y0, v) for hh in holes for v in hh[2:]]))
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0 and ys[j] >= h - 0.0051: return None
        return inner if k == 0 else mat
    for m, mesh in grid_solid(xs, ys, [-T, -T + 0.02, 0.0], cell).items(): p.add(m, mesh)
DSW = 1.3
def front_display(dx=0.0):
    """Modulo de vitrine; dx desloca a vitrine para o centro nos modulos de ponta (a cantoneira alta ocupa 0,35 m da quina)."""
    p = Piece(); wall_grid(p, 'siding', 'plaster', -W / 2, W / 2, FFT + 0.2, [(dx - DSW / 2, dx + DSW / 2, 0.6, 2.9)])
    q = Piece(); hole = display_window(q, DSW); p.merge(q, trimesh.transformations.translation_matrix([dx, 0, 0]))
    front_field(p, [(hole[0] + dx, hole[1] + dx, hole[2], hole[3])]); water_table(p); cornice(p); return p
def front_plain():
    p = Piece(); wall_with_opening(p, 'siding', 0, 0, 0, FFT + 0.2); front_field(p, []); water_table(p); cornice(p); return p
DOW = 1.7; DOY = 2.9; LEAF_W = 0.78; LEAF_H = 2.38
def front_door():
    """Porta dupla de 1,7 m com bandeira de vidro."""
    p = Piece(); x = DOW / 2
    wall_with_opening(p, 'siding', DOW, 0.015, DOY, FFT + 0.2)
    door_surround(p, DOW, DOY)
    p.cham('frame', -x + 0.07, x - 0.07, 2.4, 2.47, -0.2, -0.04, 0.008)                    # travessa da bandeira
    p.box('glass', -x + 0.066, x - 0.066, 2.466, DOY - 0.066, -0.123, -0.117)
    for i in (1, 2): xm = -x + 0.07 + (DOW - 0.14) * i / 3; p.cham('frame', xm - 0.015, xm + 0.015, 2.47, DOY - 0.07, -0.14, -0.1, 0.005)
    p.box('frame', -x + 0.07, -x + 0.085, 0.015, 2.4, -0.145, -0.12); p.box('frame', x - 0.085, x - 0.07, 0.015, 2.4, -0.145, -0.12)   # batentes de encosto (por fora da folha)
    door_sill(p, DOW); front_field(p, [(-x - 0.03, x + 0.03, -1.0, DOY + 0.05)]); cornice(p); return p
def corner_tall():
    p = corner_siding(FFT + 0.2); return p
def cornice_end(swap=False):
    """Retorno da cornija na ponta da fachada falsa (vai na quina, sobre a cantoneira alta): capa, coroa da frente prolongada
    ate a quina e coroa de retorno na lateral. swap=True: versao da quina esquerda (troca x e z)."""
    p = Piece(); e = 0.045; y = FFT
    p.cham('trim', -T - 0.04, e + 0.31, y + 0.205, y + 0.25, -T - 0.04, 0.34, 0.008)
    prof_x(p, 'trim', 0.0, e + 0.3, [(0.0, y + 0.06), (0.09, y + 0.06), (0.11, y + 0.08), (0.13, y + 0.12), (0.26, y + 0.17), (0.3, y + 0.2), (0.0, y + 0.2)])
    prof_x(p, 'trim', 0.0, e + 0.3, [(0.0, y - 0.03), (0.04 + e, y - 0.03), (0.04 + e, y + 0.06), (0.0, y + 0.06)])
    prof_z(p, 'trim', -T - 0.035, 0.0, [(e - 0.01, y + 0.06), (e + 0.08, y + 0.06), (e + 0.1, y + 0.08), (e + 0.12, y + 0.12), (e + 0.25, y + 0.17), (e + 0.29, y + 0.2), (e - 0.01, y + 0.2)])
    prof_z(p, 'trim', -T - 0.035, 0.0, [(e - 0.01, y - 0.03), (e + 0.04, y - 0.03), (e + 0.04, y + 0.06), (e - 0.01, y + 0.06)])
    if swap:
        M = np.array([[0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
        for ms in p.parts.values():
            for m in ms: m.apply_transform(M)
    return p
SIGN = (-2.9, 2.9, 4.35, 6.35)
def sign_board():
    """Letreiro de 5,8 x 2 m pintado (textura propria), com moldura de 3 filetes. Pivo: face da fachada, centro, cota do piso."""
    p = Piece(); x0, x1, y0, y1 = SIGN
    p.box('signbk', x0, x1, y0, y1, 0.03, 0.065)
    p.box('sign', x0 + 0.06, x1 - 0.06, y0 + 0.06, y1 - 0.06, 0.065, 0.068)
    for (a, b, c, d) in ((x0 - 0.08, x1 + 0.08, y1, y1 + 0.08), (x0 - 0.08, x1 + 0.08, y0 - 0.08, y0), (x0 - 0.08, x0, y0, y1), (x1, x1 + 0.08, y0, y1)):
        p.cham('trim', a, b, c, d, 0.03, 0.095, 0.012)
    p.cham('trim', x0 - 0.16, x1 + 0.16, y1 + 0.08, y1 + 0.12, 0.03, 0.14, 0.01)               # capa
    w, h = (x1 - x0 - 0.12), (y1 - y0 - 0.12)
    p.uv['sign'] = lambda v, n: np.stack([(v[:, 0] - x0 - 0.06) / w, (v[:, 1] - y0 - 0.06) / h], 1)
    return p

# ---------- frontao dos fundos: tabuas recortadas pelo triangulo, veneziana ----------
KR = math.tan(math.radians(30)); CS = math.cos(math.radians(30)); TV = 0.08; OVER = 0.45; BUMP = 0.022; RAKE = 0.4
configurar_telhado(TV, BUMP, 30)
def under_y(d):   # face de baixo do telhado a d metros da parede lateral, para dentro
    return YE + KR * d
YR = under_y(SX)
def gable_boards(p, poly, holes=(), z=0.0):
    """Tabuas sobrepostas recortadas por poly (x, y), na fase das paredes. holes = [(x0, x1, y0, y1)]."""
    k0 = int(math.floor((poly.bounds[1] - WT) / 0.2)); k1 = int(math.ceil((poly.bounds[3] - WT) / 0.2))
    for k in range(k0, k1):
        b0 = WT + k * 0.2; b1 = b0 + 0.2 + D.LAP
        cuts = sorted(set([b0, b1] + [y for hh in holes for y in hh[2:] if b0 < y < b1]))
        for ya, yb in zip(cuts[:-1], cuts[1:]):
            xs = [(-50, 50)]
            for (hx0, hx1, hy0, hy1) in holes:
                if ya >= hy0 - 1e-9 and yb <= hy1 + 1e-9: xs = [s for a, b in xs for s in ((a, min(b, hx0)), (max(a, hx1), b)) if s[1] - s[0] > 1e-4]
            for a, b in xs:
                g = poly.intersection(sbox(a, ya, b, yb))
                for gg in getattr(g, 'geoms', [g]):
                    if gg.geom_type != 'Polygon' or gg.area < 1e-5: continue
                    th = lambda y: D.TB - (D.TB - D.TT) * (y - b0) / (b1 - b0)
                    pts = list(gg.exterior.coords)[:-1]
                    p.hull('siding', [(px, py, z) for px, py in pts] + [(px, py, z + th(py)) for px, py in pts])
def store_gable_back():
    p = Piece(); xg = SX - (HW - YE - 0.01) / KR
    core = Polygon([(-xg, HW), (xg, HW), (0, YR + 0.01)])
    prof_z(p, 'siding', -T, 0.0, list(core.exterior.coords)[:-1])
    vy = 4.55; hole = (-0.45, 0.45, vy - 0.05, vy + 0.78)
    xb_ = SX - (FT - YE + 0.02) / KR; bpoly = Polygon([(-xb_, FT), (xb_, FT), (0, YR - 0.02)])
    gable_boards(p, bpoly, [hole])
    p.cham('trim', -0.45, 0.45, vy - 0.05, vy + 0.73, 0.0, 0.045, 0.008); p.box('dark', -0.36, 0.36, vy + 0.04, vy + 0.62, 0.045, 0.05)
    for i in range(6):
        yy = vy + 0.08 + i * 0.09
        p.hull('trim', [(x, y, z) for x in (-0.36, 0.36) for (y, z) in ((yy, 0.05), (yy + 0.012, 0.05), (yy - 0.03, 0.1), (yy - 0.018, 0.1))])
    p.hull('trim', [(x, y, z) for x in (-0.5, 0.5) for (y, z) in ((vy + 0.73, 0.0), (vy + 0.73, 0.075), (vy + 0.76, 0.0), (vy + 0.755, 0.075))])
    return p

# ============================================================================ telhado da loja: duas aguas a 30 graus, cumeeira ao longo de Z
def rafter_tails(p, xs, yfun, z0=0.01, z1=OVER - 0.022):
    for xx in xs: p.hull('trim', [(xx + dx, yfun(z) + dy, z) for dx in (-0.025, 0.025) for z in (z0, z1) for dy in (0.0, -0.12)])
def roof_store(x0=-W / 2, x1=W / 2, rake=0, u=0):
    """Faixa de 2 m de uma agua. Pivo: face da parede lateral, cota do piso; beiral em z=OVER, sobe para -Z ate a cumeeira (z=-SX).
    rake = -1/+1: ponta com beirada inclinada (testeira) do lado x0/x1."""
    p = Piece(); f = lambda a, b: YE - KR * b
    poly = sbox(x0, -SX, x1, OVER)
    sheared(p, 'plaster', poly, 0.0, 0.02, f)
    sheared_courses(p, poly, f, lambda a, b: OVER - b, lambda d0, d1: sbox(-50, OVER - d1, 50, OVER - d0), OVER + SX + 0.01,
                    lambda v, n: np.stack([(v[:, 0] + u) / TILE, (OVER - v[:, 2]) / CS / TILE], 1))
    yb = YE - KR * OVER
    a = x0 + (-0.03 if rake < 0 else 0.001); b = x1 + (0.03 if rake > 0 else -0.001)
    prof_x(p, 'trim', a, b, crect(OVER - 0.02, OVER + 0.03, yb - 0.15, yb + 0.05, 0.006, (0, 1, 1, 0)))
    gutter_run(p, x0 - (0.03 if rake < 0 else 0), x1 + (0.03 if rake > 0 else 0), OVER + 0.03, yb + 0.02, caps=(rake < 0 or x0 > -W / 2 + 1e-6, rake > 0 or x1 < W / 2 - 1e-6))
    xs = [xx for xx in (-0.75, -0.25, 0.25, 0.75) if x0 + 0.05 < xx < x1 - 0.05]
    rafter_tails(p, xs, lambda z: YE - KR * z)
    if rake:   # testeira inclinada cobrindo a ponta das telhas
        xr = x0 if rake < 0 else x1; xa, xb = sorted((xr, xr + rake * 0.04))
        top = lambda z: YE - KR * z + TV + BUMP + 0.03
        prof_x(p, 'trim', xa, xb, [(OVER + 0.03, top(OVER + 0.03)), (-SX, top(-SX)), (-SX, YE + KR * SX - 0.16), (OVER + 0.03, YE - KR * (OVER + 0.03) - 0.16)])
        xa, xb = sorted((xr - rake * 0.06, xr + rake * 0.04))
        prof_x(p, 'trim', xa, xb, [(-SX, YE + KR * SX - 0.16), (OVER + 0.03, YE - KR * (OVER + 0.03) - 0.16), (OVER + 0.03, YE - KR * (OVER + 0.03) - 0.22), (-SX, YE + KR * SX - 0.22)])
    return p
def ridge_store(z0, z1):
    """Cumeeira continua (uma peca so), ao longo de X local. Pivo: centro da loja, cota do piso."""
    p = Piece(); y = YE + TV + BUMP + KR * SX; d = 0.17
    p.hull('ridge', [(x, yy, z) for x in (z0, z1) for (yy, z) in ((y - d * KR - 0.04, d), (y - d * KR - 0.04, -d), (y + 0.075, 0.0), (y + 0.06, 0.06), (y + 0.06, -0.06), (y - 0.12, 0.0))])
    return p
STOVE_D = 2.8
def stovepipe():
    """Chamine de chapa do fogao a lenha: cano com abracadeira, rufo inclinado e chapeu. Pivo: eixo do cano, cota do piso."""
    p = Piece(); yb = 4.8; yt = 7.6; rs = lambda x: YE + KR * (STOVE_D + x) + TV + BUMP
    p.cyl('iron', 0.1, yb, yt, sec=16)
    p.hull('iron', [(x, rs(x) + dy, z) for x in (-0.3, 0.3) for z in (-0.3, 0.3) for dy in (0.012, 0.03)])
    p.cyl('iron', 0.12, rs(0.0) - 0.05, rs(0.0) + 0.25, sec=16)
    p.cyl('iron', 0.13, yt - 0.9, yt - 0.85, sec=16)
    p.cyl('iron', 0.012, yt, yt + 0.12, 0.09, 0); p.cyl('iron', 0.012, yt, yt + 0.12, -0.09, 0)
    p.hull('iron', [(0.24 * math.cos(a), yt + 0.12, 0.24 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 13)[:-1]] + [(0, yt + 0.3, 0)])
    return p

# ============================================================================ varanda com telhado de chapa (agua unica)
PD = 2.6; PB = 2.95; PY0 = 3.8; PS = 0.25; PZB = 2.4; PZE = 2.85; RT = 0.03
def porch_under(z): return PY0 - PS * z
def porch_deck():
    p = Piece(); L = PD
    p.box('dark', -W / 2, W / 2, -0.07, -0.03, 0.0, L)
    n = 14; bw = W / n
    for i in range(n):
        a = -W / 2 + i * bw + 0.003; b = a + bw - 0.006
        prof_z(p, 'deck', 0.0, L, crect(a, b, -0.03, 0.0, 0.004, (0, 0, 1, 1)))
    return p
def porch_skirt(L=W):
    """Testeira do deck e saia de ripas verticais ate o chao. Pivo: borda do deck, centro, cota do piso."""
    p = Piece(); a, b = -L / 2, L / 2
    prof_x(p, 'trim', a + 0.001, b - 0.001, crect(0.0, 0.035, -0.22, -0.004, 0.006, (0, 1, 1, 0)))
    p.box('dark', a, b, -RAISE, -0.22, 0.0, 0.012)
    n = int(round(L / 0.1))
    for i in range(n):
        xx = a + (i + 0.5) * L / n; p.box('trim', xx - 0.025, xx + 0.025, -RAISE + 0.02, -0.22, 0.012, 0.03)
    p.box('trim', a + 0.002, b - 0.002, -RAISE + 0.02, -RAISE + 0.1, 0.03, 0.047)
    return p
def porch_steps(w=3.0, n=3, rise=0.15, run=0.3):
    """Escada de madeira: pisos de 2 tabuas com bocel, espelhos e banzos. Pivo: borda do deck, centro, cota do piso; desce para +Z."""
    p = Piece(); z0 = 0.035
    for i in range(n):
        top = -(i + 1) * rise; za = z0 + i * run; zb = za + run
        for j in range(2):
            c0 = za - 0.03 + j * (run + 0.03) / 2 + 0.003; c1 = za - 0.03 + (j + 1) * (run + 0.03) / 2 - 0.003
            prof_x(p, 'deck', -w / 2 + 0.06, w / 2 - 0.06, crect(c0, c1 + (0.02 if j == 1 else 0.0), top - 0.035, top, 0.006, (0, 1, 1, 1)))
        p.box('trim', -w / 2 + 0.06, w / 2 - 0.06, top, top + rise - 0.035 if i else top + rise - 0.004, za - 0.025, za - 0.005)
    for s in (-1, 1):
        a, b = sorted((s * (w / 2), s * (w / 2 - 0.06)))
        L = n * run; ztop = z0 - 0.03
        p.hull('trim', [(x, y, z) for x in (a, b) for (z, y) in ((ztop, 0.0), (ztop, -0.25), (ztop + L + 0.03, -n * rise - 0.04), (ztop + L + 0.03, -RAISE), (ztop + L - 0.25, -RAISE))])
    return p
def porch_post(brackets=(-1, 1)):
    """Pilar de 15 cm com chanfros, base e capitel, maos-francesas recortadas para a viga. Pivo: eixo, cota do piso."""
    p = Piece(); a = 0.075
    p.add('trim', bl_detail(tbox(-a, a, 0.25, PB - 0.2, -a, a), bevel=0.012, segments=1))
    p.add('trim', bl_detail(tbox(-0.1, 0.1, 0.0, 0.25, -0.1, 0.1), bevel=0.01, segments=2))
    p.add('trim', bl_detail(tbox(-0.095, 0.095, PB - 0.2, PB, -0.095, 0.095), bevel=0.01, segments=2))
    for s in brackets:   # mao-francesa com borda curva (recorte em arco de elipse)
        arcp = [(0.6 + 0.505 * math.cos(t_), PB - 0.55 + 0.53 * math.sin(t_)) for t_ in np.linspace(math.pi / 2, math.pi, 9)]
        poly = [(0.07, PB), (0.6, PB), (0.6, PB - 0.02)] + arcp[1:] + [(0.07, PB - 0.55)]
        prof_z(p, 'trim', -0.03, 0.03, [(s * x, y) for x, y in poly][::(1 if s > 0 else -1)])
    return p
def porch_beam(x0=-W / 2, x1=W / 2):
    p = Piece(); prof_x(p, 'trim', x0, x1, crect(PZB - 0.1, PZB + 0.1, PB, PB + 0.25, 0.012)); return p
def porch_rail(L):
    """Guarda-corpo entre pilares, ao longo de X local de -L/2 a L/2: corrimao, travessa de baixo e balaustres torneados (bevel)."""
    p = Piece(); a, b = -L / 2, L / 2
    p.cham('trim', a, b, 0.9, 0.96, -0.045, 0.045, 0.01); p.cham('trim', a, b, 0.12, 0.18, -0.035, 0.035, 0.008)
    n = int(L / 0.13)
    bal = bl_detail(trimesh.util.concatenate([tbox(-0.022, 0.022, 0.18, 0.9, -0.022, 0.022)]), bevel=0.008, segments=1)
    for i in range(n):
        xx = a + (i + 0.5) * L / n; m = bal.copy(); m.apply_translation([xx, 0, 0]); p.add('trim', m)
    return p
def porch_roof(x0=-W / 2, x1=W / 2, end=0):
    """Modulo de 2 m do telhado da varanda: chapa com nervuras, forro de frisos, caibros, testeira, calha e rufo na parede.
    Pivo: face da parede da frente, cota do piso; avanca para +Z. end = -1/+1: ponta com beirada lateral."""
    p = Piece(); ue = porch_under(PZE)
    prof_x(p, 'metal', x0, x1, [(0.0, PY0), (PZE, ue), (PZE, ue + RT), (0.0, PY0 + RT)])
    for i in range(5):
        xx = -0.8 + 0.4 * i
        if True: prof_x(p, 'metal', xx - 0.012, xx + 0.012, [(0.0, PY0 + RT), (PZE, ue + RT), (PZE, ue + RT + 0.035), (0.0, PY0 + RT + 0.035)])
    if end:
        for xx in ((1.2,) if end > 0 else (-1.2,)): prof_x(p, 'metal', xx - 0.012, xx + 0.012, [(0.0, PY0 + RT), (PZE, ue + RT), (PZE, ue + RT + 0.035), (0.0, PY0 + RT + 0.035)])
    cz = lambda z: porch_under(z) - 0.02
    ca = x0 + (0.05 if end < 0 else 0.0); cb = x1 - (0.05 if end > 0 else 0.0)
    prof_x(p, 'ceiling', ca, cb, [(0.0, PY0 - 0.02), (PZE - 0.03, porch_under(PZE - 0.03) - 0.02), (PZE - 0.03, porch_under(PZE - 0.03)), (0.0, PY0)])
    for i in range(1, int((cb - ca) / 0.1)):
        xx = ca + i * (cb - ca) / int((cb - ca) / 0.1)
        prof_x(p, 'dark', xx - 0.004, xx + 0.004, [(0.005, cz(0.005) - 0.003), (PZE - 0.035, cz(PZE - 0.035) - 0.003), (PZE - 0.035, cz(PZE - 0.035) + 0.001), (0.005, cz(0.005) + 0.001)])
    for xx in (-0.5, 0.5):   # caibros aparentes
        prof_x(p, 'trim', xx - 0.025, xx + 0.025, [(0.0, cz(0.0)), (PZE - 0.04, cz(PZE - 0.04)), (PZE - 0.04, cz(PZE - 0.04) - 0.14), (0.0, cz(0.0) - 0.14)])
    fa = x0 - (0.03 if end < 0 else 0.0); fb = x1 + (0.03 if end > 0 else 0.0)
    prof_x(p, 'trim', fa + 0.001 * (end >= 0), fb - 0.001 * (end <= 0), crect(PZE, PZE + 0.03, ue - 0.14, ue + 0.02, 0.006, (0, 1, 1, 0)))
    gutter_run(p, fa, fb, PZE + 0.03, ue + 0.0, caps=(end < 0, end > 0))
    p.box('frame', x0 + 0.001 * (end >= 0), x1 - 0.001 * (end <= 0), PY0 - 0.2, PY0 - 0.02, 0.026, 0.05)                    # ripa de apoio na parede
    prof_x(p, 'metal', x0 + 0.0005, x1 - 0.0005, [(0.026, PY0 + RT + 0.035), (0.09, porch_under(0.09) + RT + 0.035), (0.09, porch_under(0.09) + RT + 0.045), (0.036, PY0 + RT + 0.17), (0.026, PY0 + RT + 0.17)])  # rufo
    if end:   # beirada lateral: testeira ao longo de Z
        xs = sorted((x1 if end > 0 else x0, (x1 if end > 0 else x0) + end * 0.03))
        prof_x(p, 'trim', *xs, [(0.0, PY0 + RT + 0.02), (PZE + 0.03, ue + RT + 0.02), (PZE + 0.03, ue - 0.14), (0.0, PY0 - 0.16)])
    return p

# ============================================================================ interior da loja
def floor_tile():
    p = Piece(); p.box('floor', -W / 2, W / 2, -0.03, 0, -W / 2, W / 2); p.box('plaster', -W / 2 + 0.02, W / 2 - 0.02, -SLAB, -0.03, -W / 2 + 0.02, W / 2 - 0.02); return p
def floor_tile_bath():
    p = Piece(); p.box('dark', -W / 2, W / 2, -0.027, -0.004, -W / 2, W / 2); n = 10; s = W / n
    for i in range(n):
        for j in range(n):
            x0 = -W / 2 + i * s + 0.004; z0 = -W / 2 + j * s + 0.004; p.box('tile', x0, x0 + s - 0.008, -0.03, 0.0, z0, z0 + s - 0.008)
    p.box('plaster', -W / 2 + 0.02, W / 2 - 0.02, -SLAB, -0.03, -W / 2 + 0.02, W / 2 - 0.02); return p
def ceiling_tile(z1=W / 2):
    """Forro de chapa estampada (tin ceiling): placa com quadros de 0,5 m em relevo. z1 < 1: fileira da frente, para dentro da fachada."""
    p = Piece(); p.box('plaster', -W / 2, W / 2, -SLAB, 0, -W / 2, z1)
    for i in range(4):
        for j in range(4):
            a = -W / 2 + i * 0.5; c = -W / 2 + j * 0.5
            p.cham('plaster', a + 0.06, a + 0.44, -SLAB - 0.012, -SLAB + 0.001, c + 0.06, c + 0.44, 0.006)
    return p
IH = H - SLAB
def interior_wall(doorway, h=IH, ow=0.9):
    p = Piece(); t = 0.12; ow = ow if doorway else 0
    wall_with_opening(p, 'plaster', ow, 0, 2.1, h, inner='plaster', t=t, centered=True)
    if doorway: door_casing(p, ow, t)
    for a, b in ([(-W / 2, -ow / 2 - 0.08), (ow / 2 + 0.08, W / 2)] if doorway else [(-W / 2, W / 2)]): baseboard(p, a, b, t)
    return p
def interior_wall_end(h=IH):
    p = Piece(); t = 0.12; L = W - T
    m = trimesh.creation.box(extents=[L, h, t]); m.apply_translation([-W / 2 + L / 2, h / 2, 0]); p.add('plaster', m)
    baseboard(p, -W / 2, -W / 2 + L, t); return p
def interior_wall_end_doorway(h=IH):
    p = Piece(); t = 0.12; e = W / 2 - T
    xs = [-W / 2, -0.45, 0.45, e]; ys = [0.0, 2.1, h]; zs = [-t / 2, t / 2]
    for m, mesh in grid_solid(xs, ys, zs, lambda i, j, k: None if (i == 1 and j == 0) else 'plaster').items(): p.add(m, mesh)
    door_casing(p, 0.9, t)
    for (a, b) in ((-W / 2, -0.53), (0.53, e)): baseboard(p, a, b, t)
    return p
def player_ref():
    p = Piece(); c = trimesh.creation.capsule(height=1.8 - 0.6, radius=0.3, count=[8, 8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); c.apply_translation([0, 0.9, 0]); p.add('player', c)
    p.box('dark', -0.15, 0.15, 1.5, 1.6, 0.22, 0.32); return p
def brick_steps(w=1.36, rise=0.15, run=0.28, n=3):
    """Degraus de pedra com bocel e muretas laterais (porta lateral para o corredor). Pivo: borda de cima, centro; desce para +Z."""
    p = Piece()
    for i in range(n):
        top = -(i + 1) * rise; z0, z1 = i * run, (i + 1) * run
        p.box('stone', -w / 2, w / 2, -RAISE, top - 0.04, z0, z1 - 0.02)
        prof_x(p, 'cap', -w / 2 + 0.002, w / 2 - 0.002, [(z0, top - 0.04)] + arc(z1 + 0.012, top - 0.02, 0.02, -math.pi / 2, math.pi / 2, 6) + [(z0, top)])
    L = n * run + 0.05
    for s in (-1, 1):
        a, b = sorted((s * (w / 2), s * (w / 2 + 0.2)))
        p.box('stone', a, b, -RAISE, -0.05, 0.0, L)
        p.hull('cap', [(xx, y, z) for xx in (a - 0.02 * (s < 0), b + 0.02 * (s > 0)) for (z, y) in ((0.0, -0.05), (0.0, 0.0), (L + 0.03, -0.05), (L + 0.03, -0.035))])
    return p

# ============================================================================ celeiro: tabua e mata-junta, telhado holandes de chapa
BW = 6.0; BD = 6.0; RB = 0.15; YEB = 3.6; OVB = 0.3; OVR = 0.3; R1 = 1.8
T1 = math.tan(math.radians(60)); T2 = math.tan(math.radians(22))
YK = YEB + R1 * T1; YRB = YK + (BW - R1) * T2
BX, BZ = 8.4, -1.0                     # centro do celeiro no mundo (paredes de x 2,4 a 14,4 e z -7 a 5)
GU = [(-BW - OVB, YEB - OVB * T1), (-BW + R1, YK), (0.0, YRB), (BW - R1, YK), (BW + OVB, YEB - OVB * T1)]
def gy(x):   # face de baixo do telhado (forro de tabuas) no ponto x
    xs = [q[0] for q in GU]; ys = [q[1] for q in GU]; return float(np.interp(x, xs, ys))
def offset_line(pts, d, vertical_ends=True):
    P = np.array(pts, float); N = []
    for i in range(len(P) - 1):
        v = P[i + 1] - P[i]; v /= np.linalg.norm(v); N.append(np.array([-v[1], v[0]]))
    out = []
    for i in range(len(P)):
        if i == 0 or i == len(P) - 1:
            j = 0 if i == 0 else len(N) - 1; q = P[i] + d * N[j]
            if vertical_ends:
                v = P[j + 1] - P[j]; v /= np.linalg.norm(v); t = (P[i][0] - q[0]) / v[0]; q = q + t * v
            out.append(q)
        else:
            m = N[i - 1] + N[i]; m /= np.linalg.norm(m); out.append(P[i] + m * d / np.dot(m, N[i]))
    return [tuple(q) for q in out]
def band(pts, d0, d1): return offset_line(pts, d0) + offset_line(pts, d1)[::-1]
def clip_line(x0, x1):
    pts = [(x0, gy(x0))] + [q for q in GU if x0 < q[0] < x1] + [(x1, gy(x1))]; return pts
DK = 0.025; MS = 0.02     # forro de tabuas e chapa
def ytop(x): return gy(x) + (DK + MS) / math.cos(math.atan(T1 if abs(x) > BW - R1 else T2))
def barn_roof(z0=-1.0, z1=1.0, rake=False):
    """Faixa de 2 m (ao longo de Z) do telhado holandes inteiro: forro de tabuas, chapa, nervuras a cada 0,4 m, cumeeira,
    testeiras, calhas dos 2 beirais, caibros e tirante por dentro. Pivo: eixo do celeiro, cota do piso do celeiro."""
    p = Piece()
    prof_z(p, 'planks', z0, z1, band(GU, 0.0, DK)); prof_z(p, 'metal', z0, z1, band(GU, DK, DK + MS))
    zs = [z for z in np.arange(-0.8, (1.21 if rake else 0.81), 0.4)]
    for zc in zs: prof_z(p, 'metal', zc - 0.012, zc + 0.012, band(GU, DK + MS, DK + MS + 0.032))
    zc0, zc1 = z0 - 0.0, z1 + (0.04 if rake else 0.0)
    yt = ytop(0.3)
    prof_z(p, 'metal', zc0, zc1, [(-0.32, ytop(-0.32) - 0.006), (-0.32, ytop(-0.32) + 0.045), (0.0, ytop(0.0) + 0.1), (0.32, ytop(0.32) + 0.045), (0.32, ytop(0.32) - 0.006), (0.0, ytop(0.0) + 0.02)])
    ye = GU[0][1]
    for s in (-1, 1):
        xa, xb = sorted((s * (BW + OVB), s * (BW + OVB + 0.03)))
        prof_z(p, 'trim', z0 + 0.001 * (not rake and False), z1 + (0.03 if rake else 0.0), crect(xa, xb, ye - 0.16, ye + 0.05, 0.006))
        g = Piece(); gutter_run(g, *((-(z1 + (0.03 if rake else 0.0)), -z0) if s > 0 else (z0, z1 + (0.03 if rake else 0.0))), 0.0, ye + 0.02, caps=(rake and s > 0, rake and s < 0))
        R = trimesh.transformations.rotation_matrix(s * math.pi / 2, [0, 1, 0])
        for m in g.parts['gutter']: m.apply_transform(R); m.apply_translation([s * (BW + OVB + 0.03), 0, 0]); p.add('gutter', m)
    # caibros e tirante (por dentro), no meio da faixa
    zr = 0.0 if not rake else -0.4
    prof_z(p, 'planks', zr - 0.03, zr + 0.03, band(clip_line(-BW + T, BW - T), -0.16, -0.0001))
    p.box('planks', -(BW - R1) - 0.05, (BW - R1) + 0.05, YK - 0.36, YK - 0.2, zr + 0.03, zr + 0.08)
    if rake:   # testeira ao longo do perfil holandes, na ponta
        prof_z(p, 'trim', z1, z1 + 0.03, band(GU, -0.16, DK + MS + 0.045))
    return p
def battens(p, xa, xb, y0, y1, holes=(), z=0.0):
    n = int(round((xb - xa) / 0.2857))
    for i in range(n):
        xx = xa + (i + 0.5) * (xb - xa) / n; segs = [(y0, y1)]
        for (a, b, c, d) in holes:
            if a - 0.03 < xx < b + 0.03: segs = [s for (u, v) in segs for s in ((u, min(v, c)), (max(u, d), v)) if s[1] - s[0] > 0.02]
        for (u, v) in segs: p.cham('barn', xx - 0.03, xx + 0.03, u, v, z, z + 0.022, 0.006)
def planks_uv(v, n):
    """Projecao em caixa, mas faces horizontais com cor lisa (como o reboco): os topos das camadas internas se cruzam nas quinas."""
    uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1)
    uv[ax == 0] = v[ax == 0][:, [2, 1]]; uv[ax == 2] = v[ax == 2][:, [0, 1]]; uv /= TILE; uv[ax == 1] = 0.37; return uv
def barn_wall_grid(p, xa, xb, h, holes=(), y0=0.1):
    xs = sorted(set([xa, xb] + [v for hh in holes for v in hh[:2]])); ys = sorted(set([y0, h - 0.005, h] + [max(y0, v) for hh in holes for v in hh[2:]]))
    zs = [-T, -T + 0.02, 0.0]
    def cell(i, j, k):
        cx = (xs[i] + xs[i + 1]) / 2; cy = (ys[j] + ys[j + 1]) / 2
        for (a, b, c, d) in holes:
            if a < cx < b and c < cy < d: return None
        if k == 0 and ys[j] >= h - 0.0051: return None
        return 'planks' if k == 0 else 'barn'
    for m, mesh in grid_solid(xs, ys, zs, cell).items(): p.add(m, mesh)
    p.uv['planks'] = planks_uv
def barn_base(p, xa, xb, gaps=()):
    xs = [xa] + [v for g in gaps for v in g] + [xb]
    for i in range(0, len(xs) - 1):
        top = 0.006 if i % 2 == 1 else 0.1
        p.box('concrete', xs[i], xs[i + 1], -RB, top, -T, 0.03)
    for i in range(0, len(xs) - 1, 2):   # testeira de baixo sobre o baldrame
        if xs[i + 1] - xs[i] > 0.01: prof_x(p, 'trim', xs[i] + 0.001, xs[i + 1] - 0.001, crect(0.0, 0.03, 0.1, 0.24, 0.006, (0, 1, 1, 0)))
def barn_top(p, xa, xb): prof_x(p, 'trim', xa + 0.001, xb - 0.001, crect(0.0, 0.03, YEB - 0.26, YEB, 0.006, (0, 1, 1, 0)))
def barn_window_frame(p, ow=0.9, oy0=1.5, oy1=2.5):
    x = ow / 2; f = 0.05
    p.box('frame', -x, -x + f, oy0, oy1, -0.285, -0.03); p.box('frame', x - f, x, oy0, oy1, -0.285, -0.03)   # batentes na espessura toda da parede
    p.box('frame', -x + f, x - f, oy1 - f, oy1, -0.285, -0.03); p.box('frame', -x + f, x - f, oy0, oy0 + f, -0.285, -0.03)
    p.box('glass', -x + f - 0.004, x - f + 0.004, oy0 + f - 0.004, oy1 - f + 0.004, -0.123, -0.117)
    p.cham('frame', -0.016, 0.016, oy0 + f, oy1 - f, -0.14, -0.1, 0.005); p.cham('frame', -x + f, x - f, (oy0 + oy1) / 2 - 0.016, (oy0 + oy1) / 2 + 0.016, -0.14, -0.1, 0.005)
    for (a, b, c, d) in ((-x - 0.1, -x, oy0 - 0.02, oy1 + 0.1), (x, x + 0.1, oy0 - 0.02, oy1 + 0.1), (-x - 0.1, x + 0.1, oy1, oy1 + 0.1)):
        p.cham('trim', a, b, c, d, 0.0, 0.035, 0.006)
    prof_x(p, 'trim', -x - 0.14, x + 0.14, [(-0.03, oy0 - 0.06), (0.06, oy0 - 0.06), (0.075, oy0 - 0.045), (0.06, oy0 - 0.02), (-0.03, oy0 - 0.02)])
    p.box('trim', -x + f, x - f, oy0 - 0.02, oy0 + 0.012, -0.19, 0.02)
    return (-x - 0.1, x + 0.1, oy0 - 0.06, oy1 + 0.1)
def barn_wall_plain():
    p = Piece(); barn_wall_grid(p, -W / 2, W / 2, YEB); barn_base(p, -W / 2, W / 2); barn_top(p, -W / 2, W / 2); battens(p, -W / 2, W / 2, 0.24, YEB - 0.26); return p
def barn_wall_window():
    p = Piece(); hole = (-0.45, 0.45, 1.5, 2.5); barn_wall_grid(p, -W / 2, W / 2, YEB, [hole]); barn_base(p, -W / 2, W / 2); barn_top(p, -W / 2, W / 2)
    h = barn_window_frame(p); battens(p, -W / 2, W / 2, 0.24, YEB - 0.26, [h]); return p
def barn_wall_door():
    p = Piece(); x = 0.5; oy1 = 2.25
    barn_wall_grid(p, -W / 2, W / 2, YEB, [(-x, x, 0.0, oy1)]); barn_base(p, -W / 2, W / 2, [(-x, x)]); barn_top(p, -W / 2, W / 2)
    p.box('frame', -x, -x + 0.06, 0.0, oy1, -0.2, -0.03); p.box('frame', x - 0.06, x, 0.0, oy1, -0.2, -0.03); p.box('frame', -x, x, oy1 - 0.06, oy1, -0.2, -0.03)
    for (a, b, c, d) in ((-x - 0.12, -x, 0.1, oy1 + 0.12), (x, x + 0.12, 0.1, oy1 + 0.12), (-x - 0.12, x + 0.12, oy1, oy1 + 0.12)): p.cham('trim', a, b, c, d, 0.0, 0.035, 0.006)
    p.box('frame', -x + 0.06, x - 0.06, -0.02, 0.012, -0.2, -0.03)
    battens(p, -W / 2, W / 2, 0.24, YEB - 0.26, [(-x - 0.12, x + 0.12, -1, oy1 + 0.12)]); return p
BDW = 3.6; BDH = 3.3
def barn_wall_bigdoor():
    """Modulo de 4 m com o portao de 3,6 x 3,3 m: batentes, verga, guarnicoes e ferragens do trinco."""
    p = Piece(); x = BDW / 2; L = 2.0
    barn_wall_grid(p, -L, L, YEB, [(-x, x, 0.0, BDH)]); barn_base(p, -L, L, [(-x, x)]); barn_top(p, -L, L)
    p.box('frame', -x, -x + 0.08, 0.0, BDH, -0.24, -0.03); p.box('frame', x - 0.08, x, 0.0, BDH, -0.24, -0.03); p.box('frame', -x, x, BDH - 0.08, BDH, -0.24, -0.03)
    for (a, b, c, d) in ((-x - 0.15, -x, 0.1, BDH + 0.15), (x, x + 0.15, 0.1, BDH + 0.15), (-x - 0.15, x + 0.15, BDH, BDH + 0.15)): p.cham('trim', a, b, c, d, 0.0, 0.04, 0.008)
    p.box('frame', -x + 0.08, x - 0.08, -0.02, 0.012, -0.24, -0.03)
    battens(p, -L, L, 0.24, YEB - 0.26, [(-x - 0.15, x + 0.15, -1, BDH + 0.15)]); return p
def barn_corner():
    p = Piece(); e = 0.045
    prof_y(p, 'trim', -RB, YEB - 0.1, [(-T - 0.01, -T - 0.01), (e, -T - 0.01), (e, e - 0.006), (e - 0.006, e), (-T - 0.01, e)]); return p
def barn_floor():
    p = Piece(); p.box('concrete', -W / 2 + 0.004, W / 2 - 0.004, -RB, 0.0, -W / 2 + 0.004, W / 2 - 0.004); p.box('dark', -W / 2, W / 2, -RB, -0.004, -W / 2, W / 2); return p
def barn_ramp(w=4.2, L=1.2):
    p = Piece(); p.hull('concrete', [(x, y, z) for x in (-w / 2, w / 2) for (z, y) in ((0.03, 0.0), (0.03, -RB), (L, -RB), (L, -RB + 0.01))]); return p
def barn_gable(front=True):
    """Oitao holandes acima do beiral: tabua e mata-junta, faixa de arremate sob o telhado, porta do palheiro e, na frente,
    capuz da talha com viga e gancho. Pivo: face da parede, eixo, cota do piso do celeiro."""
    p = Piece()
    pts = [(-BW, YEB)] + [(q[0], q[1] + 0.01) for q in GU[1:-1]] + [(BW, YEB)]
    prof_z(p, 'barn', -T + 0.02, 0.0, pts); prof_z(p, 'planks', -T, -T + 0.02, [(x, y - (0.005 if y > YEB else 0)) for x, y in pts])
    prof_z(p, 'trim', 0.0, 0.03, band(clip_line(-BW, BW), -0.2, 0.0))
    ld = (-0.8, 0.8, 4.7, 6.5) if front else (-0.5, 0.5, 5.2, 6.2)
    n = int(round(2 * BW / 0.2857))
    for i in range(n):
        xx = -BW + (i + 0.5) * 2 * BW / n; y1 = min(gy(xx - 0.03), gy(xx + 0.03)) - 0.2 - 0.04
        segs = [(YEB, y1)]
        a, b, c, d = ld
        if a - 0.13 < xx < b + 0.13: segs = [s for (u, v) in segs for s in ((u, min(v, c - 0.13)), (max(u, d + 0.13), v)) if s[1] - s[0] > 0.02]
        for (u, v) in segs:
            if v - u > 0.02: p.cham('barn', xx - 0.03, xx + 0.03, u, v, 0.0, 0.022, 0.006)
    a, b, c, d = ld
    p.box('barn', a, b, c, d, 0.0, 0.03)
    for i in range(1, int((b - a) / 0.16)): xx = a + i * (b - a) / int((b - a) / 0.16); p.box('dark', xx - 0.004, xx + 0.004, c + 0.01, d - 0.01, 0.03, 0.032)
    for (u0, u1, v0, v1) in ((a - 0.12, a, c - 0.12, d + 0.12), (b, b + 0.12, c - 0.12, d + 0.12), (a, b, d, d + 0.12), (a, b, c - 0.12, c)): p.cham('trim', u0, u1, v0, v1, 0.0, 0.045, 0.008)
    for (P0, P1) in (((a + 0.05, c + 0.05), (b - 0.05, d - 0.05)), ((a + 0.05, d - 0.05), (b - 0.05, c + 0.05))):
        p.seg('trim', (P0[0], P0[1], 0.045), (P1[0], P1[1], 0.045), 0.1, 0.03)
    if front:   # capuz da talha
        yr = YRB - 0.12; ye = YRB - 0.62; hw = 0.95; L = 1.2
        for s in (-1, 1):
            p.hull('metal', [(x, y + dy, z) for (x, y) in ((0.0, yr), (s * hw, ye)) for z in (0.0, L) for dy in (0.0, 0.025)])
            p.hull('trim', [(x, y + dy, z) for (x, y) in ((0.0, yr), (s * hw, ye)) for z in (L - 0.03, L) for dy in (-0.16, -0.001)])
        p.box('trim', -0.07, 0.07, ye - 0.3, ye - 0.14, -0.1, L - 0.03)
        p.box('iron', -0.012, 0.012, ye - 0.7, ye - 0.3, L - 0.2, L - 0.176); p.cyl('iron', 0.05, ye - 0.33, ye - 0.29, 0, L - 0.19, 12)
        p.box('iron', -0.04, 0.04, ye - 0.74, ye - 0.7, L - 0.22, L - 0.16)
    return p
def barn_door_leaf(w=1.71, h=3.2, t=0.05):
    """Folha do portao: tabuas verticais com frestas, quadro e X brancos, dobradicas de ferro em faixa. Pivo: dobradica, embaixo."""
    p = Piece(); n = int(round(w / 0.18))
    for i in range(n):
        a = i * w / n + 0.003; b = (i + 1) * w / n - 0.003; p.cham('barn', a, b, 0.0, h, -t / 2, t / 2 - 0.01, 0.004)
    p.box('dark', 0.01, w - 0.01, 0.01, h - 0.01, -t / 2 + 0.01, t / 2 - 0.015)
    for sz in (1, -1):   # quadro e X nas 2 faces (a folha da direita vai girada 180 graus)
        z0, z1 = sorted((sz * (t / 2 - 0.01), sz * (t / 2 + 0.02)))
        if sz < 0: z0, z1 = sorted((-t / 2 - 0.02, -t / 2 + 0.001))
        for (a, b, c, d) in ((0.0, 0.14, 0.0, h), (w - 0.14, w, 0.0, h), (0.14, w - 0.14, h - 0.14, h), (0.14, w - 0.14, 0.0, 0.14), (0.14, w - 0.14, h / 2 - 0.07, h / 2 + 0.07)):
            p.cham('trim', a, b, c, d, z0, z1, 0.006)
        zc = sz * (t / 2 + 0.005)
        for (y0, y1) in ((0.14, h / 2 - 0.07), (h / 2 + 0.07, h - 0.14)):
            p.seg('trim', (0.2, y0 + 0.06, zc), (w - 0.2, y1 - 0.06, zc), 0.12, 0.028)
            p.seg('trim', (0.2, y1 - 0.06, zc + sz * 0.001), (w - 0.2, y0 + 0.06, zc + sz * 0.001), 0.12, 0.026)
    for yy in (0.45, h - 0.45):
        p.box('iron', 0.0, 0.7, yy - 0.04, yy + 0.04, t / 2 + 0.02, t / 2 + 0.028); p.cyl('iron', 0.022, yy - 0.06, yy + 0.06, 0.0, t / 2 + 0.01, 10)
    p.box('iron', w - 0.11, w - 0.07, 1.0, 1.4, t / 2 + 0.02, t / 2 + 0.03); p.seg('iron', (w - 0.09, 1.05, t / 2 + 0.03), (w - 0.09, 1.05, t / 2 + 0.08), 0.02)
    p.seg('iron', (w - 0.09, 1.35, t / 2 + 0.03), (w - 0.09, 1.35, t / 2 + 0.08), 0.02); p.box('iron', w - 0.105, w - 0.075, 1.04, 1.36, t / 2 + 0.07, t / 2 + 0.09)
    return p
def barn_small_leaf(w=0.88, h=2.17, t=0.045):
    """Porta de servico do celeiro: tabuas com frestas e Z de travessas, dobradicas em T, trinco."""
    p = Piece(); n = 5
    for i in range(n): a = i * w / n + 0.003; b = (i + 1) * w / n - 0.003; p.cham('barn', a, b, 0.0, h, -t / 2, t / 2, 0.004)
    p.box('dark', 0.01, w - 0.01, 0.01, h - 0.01, -t / 2 + 0.005, t / 2 - 0.005)
    for yy in (0.25, h - 0.25):
        p.cham('trim', 0.04, w - 0.04, yy - 0.07, yy + 0.07, t / 2, t / 2 + 0.025, 0.006); p.cham('trim', 0.04, w - 0.04, yy - 0.07, yy + 0.07, -t / 2 - 0.025, -t / 2, 0.006)
        p.box('iron', 0.0, 0.45, yy - 0.025, yy + 0.025, t / 2 + 0.025, t / 2 + 0.032)
    p.seg('trim', (0.1, 0.3, t / 2 + 0.012), (w - 0.1, h - 0.3, t / 2 + 0.012), 0.12, 0.025)
    p.box('iron', w - 0.1, w - 0.07, 0.95, 1.15, t / 2, t / 2 + 0.012); p.seg('iron', (w - 0.085, 1.0, t / 2), (w - 0.085, 1.0, t / 2 + 0.06), 0.018)
    p.seg('iron', (w - 0.085, 1.0, -t / 2), (w - 0.085, 1.0, -t / 2 - 0.06), 0.018)
    return p

# ============================================================================ pecas
GUT_Y = YE - KR * OVER + 0.02 - 0.12
pieces = {'floor_tile': floor_tile(), 'floor_tile_bath': floor_tile_bath(), 'ceiling_tin': ceiling_tile(), 'ceiling_tin_front': ceiling_tile(W / 2 - 0.15),
          'door_leaf_store': door_back(LEAF_W, LEAF_H), 'door_leaf_back': door_back(), 'door_leaf_interior': door_interior(),
          'interior_wall_plain': interior_wall(False), 'interior_wall_doorway': interior_wall(True), 'interior_wall_end': interior_wall_end(), 'interior_wall_end_doorway': interior_wall_end_doorway(),
          'wall_siding_window': wall_window(), 'wall_siding_small_window': wall_small_window(), 'wall_siding_plain': wall_plain(), 'wall_siding_door': wall_door(),
          'corner_siding': corner_siding(), 'corner_tall': corner_tall(), 'cornice_end': cornice_end(), 'cornice_end_l': cornice_end(True),
          'front_display': front_display(), 'front_display_l': front_display(0.15), 'front_display_r': front_display(-0.15), 'front_plain': front_plain(), 'front_door': front_door(), 'sign_board': sign_board(),
          'store_gable_back': store_gable_back(), 'stovepipe': stovepipe(), 'stone_steps': brick_steps(),
          'roof_store': roof_store(), 'roof_store_front': roof_store(-1.0, 0.7), 'roof_store_front_r': roof_store(-0.7, 1.0),
          'roof_store_back': roof_store(-1.0 - RAKE, 1.0, rake=-1), 'roof_store_back_r': roof_store(-1.0, 1.0 + RAKE, rake=1),
          'ridge_store': ridge_store(-SZ - RAKE - 0.03, SZ - T),
          'downspout': downspout(RAISE + GUT_Y, OVER + 0.095),
          'porch_deck': porch_deck(), 'porch_skirt': porch_skirt(), 'porch_skirt_side': porch_skirt(PD), 'porch_steps': porch_steps(),
          'porch_post': porch_post(), 'porch_post_end_l': porch_post((1,)), 'porch_post_end_r': porch_post((-1,)),
          'porch_beam': porch_beam(), 'porch_beam_end_l': porch_beam(-W / 2 - 0.12, W / 2), 'porch_beam_end_r': porch_beam(-W / 2, W / 2 + 0.12),
          'porch_rail': porch_rail(3.2 - 0.15), 'porch_rail_side': porch_rail(PZB - 0.075 - 0.07),
          'porch_roof': porch_roof(), 'porch_roof_end_l': porch_roof(-W / 2 - 0.3, W / 2, -1), 'porch_roof_end_r': porch_roof(-W / 2, W / 2 + 0.3, 1),
          'downspout_porch': downspout(RAISE + porch_under(PZE) - 0.12, PZE + 0.095 - PD - 0.045),
          'porch_lantern': porch_lantern(), 'wall_lantern': wall_lantern(),
          'barn_wall_plain': barn_wall_plain(), 'barn_wall_window': barn_wall_window(), 'barn_wall_door': barn_wall_door(), 'barn_wall_bigdoor': barn_wall_bigdoor(),
          'barn_corner': barn_corner(), 'barn_floor': barn_floor(), 'barn_ramp': barn_ramp(), 'barn_ramp_small': barn_ramp(1.3, 0.7),
          'barn_gable_front': barn_gable(True), 'barn_gable_back': barn_gable(False), 'barn_roof': barn_roof(), 'barn_roof_end': barn_roof(z1=1.0 + OVR, rake=True),
          'barn_door_leaf': barn_door_leaf(), 'barn_door_small': barn_small_leaf(),
          'downspout_barn': downspout(RB + GU[0][1] + 0.02 - 0.12, OVB + 0.095),
          'player_scale_ref': player_ref()}

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    import shutil; shutil.rmtree(f'{OUT}/pieces', ignore_errors=True); os.makedirs(f'{OUT}/pieces')
    for n, p in pieces.items():
        fn = f'{OUT}/pieces/{n}.glb'; p.scene(n).export(fn, include_normals=True); glb_jpeg(fn)

# ============================================================================ montagem
L = []
def put(n, x, y, z, ry=0, tags=(), door=None):
    e = {'piece': n, 'pos': [round(x, 3), round(y, 3), round(z, 3)], 'rotY': ry, 'tags': list(tags)}
    if door is not None: e['door'] = {'closed': ry, 'open': ry + door}; e['tags'].append('door')
    L.append(e)
def hinge(x, z, ry, lx, lz):
    r = math.radians(ry); return x + lx * math.cos(r) + lz * math.sin(r), z - lx * math.sin(r) + lz * math.cos(r)
Y0 = RAISE
# ---------- loja (coordenadas da loja + CX) ----------
XB = [-4, -2, 0, 2, 4]; ZB = [-6, -4, -2, 0, 2, 4, 6]
SW, SS, SP, SD = 'wall_siding_window', 'wall_siding_small_window', 'wall_siding_plain', 'wall_siding_door'
G = {'front': {-4: 'front_display_l', -2: 'front_display', 0: 'front_door', 2: 'front_display', 4: 'front_display_r'},
     'back': {-4: SS, -2: SP, 0: SW, 2: SP, 4: SW},
     'left': {6: SP, 4: SW, 2: SW, 0: SW, -2: SW, -4: SP, -6: SS},
     'right': {6: SP, 4: SW, 2: SP, 0: SW, -2: SW, -4: SD, -6: SP}}
faces = [(0, XB, lambda u: (u, SZ), 'front'), (90, ZB, lambda u: (SX, -u), 'right'), (180, XB, lambda u: (-u, -SZ), 'back'), (-90, ZB, lambda u: (-SX, u), 'left')]
for ry, bays, f, tag in faces:
    for u in bays:
        x, z = f(u); wk = x if tag in ('front', 'back') else z
        put(G[tag][wk], CX + x, Y0, z, ry, ['store', tag, 'ext'])
for ry, x, z, n in [(0, SX, SZ, 'corner_tall'), (90, SX, -SZ, 'corner_siding'), (180, -SX, -SZ, 'corner_siding'), (-90, -SX, SZ, 'corner_tall')]:
    put(n, CX + x, Y0, z, ry, ['store', 'ext'])
put('cornice_end', CX + SX, Y0, SZ, 0, ['store', 'front']); put('cornice_end_l', CX - SX, Y0, SZ, -90, ['store', 'front'])
put('sign_board', CX, Y0, SZ, 0, ['store', 'front'])
put('store_gable_back', CX, Y0, -SZ, 180, ['store', 'back'])
# telhado: faixas nas 2 aguas (esquerda ry=-90 em x=-SX, direita ry=90 em x=+SX)
for u in ZB:
    nl = 'roof_store_front' if u == 6 else 'roof_store_back' if u == -6 else 'roof_store'
    put(nl, CX - SX, Y0, u, -90, ['store', 'roof'])
    nr = 'roof_store_front_r' if u == 6 else 'roof_store_back_r' if u == -6 else 'roof_store'
    put(nr, CX + SX, Y0, u, 90, ['store', 'roof'])
put('ridge_store', CX, Y0, 0, -90, ['store', 'roof'])
put('stovepipe', CX - SX + STOVE_D, Y0, -3.0, 0, ['store', 'roof'])
for x, z, ry in ((CX - SX, 6.35, -90), (CX - SX, -6.62, -90), (CX + SX, 6.35, 90), (CX + SX, -6.62, 90)):
    put('downspout', x, 0, z, ry, ['store', 'ext'])
# interior da loja
TILEB = {(-4, -6), (-2, -6)}
for a in XB:
    for b in ZB:
        put('floor_tile_bath' if (a, b) in TILEB else 'floor_tile', CX + a, Y0, b, 0, ['store', 'floor0'])
        put('ceiling_tin_front' if b == 6 else 'ceiling_tin', CX + a, Y0 + H - 0.01, b, 0, ['store', 'roof', 'ceiling'])
def wl(x0, z0, x1, z1, doors=()):
    y = Y0
    if z0 == z1:
        for c in range(int(min(x0, x1)) + 1, int(max(x0, x1)), 2):
            end = abs(c) + 1 >= SX; d = c in doors
            put(('interior_wall_end' if end else 'interior_wall_' + ('doorway' if d else 'plain')) + ('_doorway' if end and d else ''), CX + c, y, z0, (0 if c > 0 else 180) if end else 0, ['store', 'floor0'])
            if d: hx, hz = hinge(c, z0, 0, -0.43, 0); put('door_leaf_interior', CX + hx, y, hz, 0, ['store', 'floor0'], door=70)
    else:
        for c in range(int(min(z0, z1)) + 1, int(max(z0, z1)), 2):
            end = abs(c) + 1 >= SZ; d = c in doors
            put(('interior_wall_end' if end else 'interior_wall_' + ('doorway' if d else 'plain')) + ('_doorway' if end and d else ''), CX + x0, y, c, (-90 if c > 0 else 90) if end else 90, ['store', 'floor0'])
            if d: hx, hz = hinge(x0, c, 90, -0.43, 0); put('door_leaf_interior', CX + hx, y, hz, 90, ['store', 'floor0'], door=70)
wl(-5, -1, 5, -1, doors=(-2, 2)); wl(-1, -7, -1, -1, doors=(-6,)); wl(-5, -5, -1, -5)
# portas externas da loja
for s, ry, op in ((-1, 0, 85), (1, 180, -85)):
    put('door_leaf_store', CX + s * (DOW / 2 - 0.07), Y0 + 0.015, SZ - 0.17, ry, ['store', 'front', 'ext'], door=op)
hx, hz = hinge(SX, -4.0, 90, -0.47, -0.18); put('door_leaf_back', CX + hx, Y0 + 0.015, hz, 90, ['store', 'right', 'ext'], door=85)
put('stone_steps', CX + SX, Y0, -4.0, 90, ['store', 'right', 'ext'])
# varanda
for x in XB:
    put('porch_deck', CX + x, Y0, SZ, 0, ['porch'])
    put('porch_skirt', CX + x, Y0, SZ + PD, 0, ['porch'])
    put('porch_roof_end_l' if x == -4 else 'porch_roof_end_r' if x == 4 else 'porch_roof', CX + x, Y0, SZ, 0, ['porch', 'roof'])
    put('porch_beam_end_l' if x == -4 else 'porch_beam_end_r' if x == 4 else 'porch_beam', CX + x, Y0, SZ, 0, ['porch'])
put('porch_skirt_side', CX - SX, Y0, SZ + PD / 2, -90, ['porch']); put('porch_skirt_side', CX + SX, Y0, SZ + PD / 2, 90, ['porch'])
PXS = [-4.8, -1.6, 1.6, 4.8]
for x in PXS: put('porch_post_end_l' if x == -4.8 else 'porch_post_end_r' if x == 4.8 else 'porch_post', CX + x, Y0, SZ + PZB, 0, ['porch'])
for xa, xb in ((-4.8, -1.6), (1.6, 4.8)): put('porch_rail', CX + (xa + xb) / 2, Y0, SZ + PZB, 0, ['porch'])
for x in (-4.8, 4.8): put('porch_rail_side', CX + x, Y0, SZ + (0.07 + PZB - 0.075) / 2, 90, ['porch'])
put('porch_steps', CX, Y0, SZ + PD, 0, ['porch'])
put('porch_lantern', CX, Y0 + porch_under(1.2) - 0.02, SZ + 1.2, 0, ['porch'])
put('downspout_porch', CX - 4.8, 0, SZ + PD + 0.045, 0, ['porch']); put('downspout_porch', CX + 4.8, 0, SZ + PD + 0.045, 0, ['porch'])
# ---------- celeiro ----------
YB = RB
BXB = [-5, -3, 3, 5]; BZB = [-5, -3, -1, 1, 3, 5]
BWN, BWW, BWD = 'barn_wall_plain', 'barn_wall_window', 'barn_wall_door'
GB = {'front': {-5: BWW, -3: BWN, 3: BWN, 5: BWW}, 'back': {-5: BWW, -3: BWN, -1: BWD, 1: BWN, 3: BWN, 5: BWW},
      'left': {5: BWW, 3: BWN, 1: BWW, -1: BWN, -3: BWD, -5: BWW}, 'right': {5: BWW, 3: BWN, 1: BWW, -1: BWW, -3: BWN, -5: BWW}}
bfaces = [(0, BXB, lambda u: (u, BD), 'front'), (90, BZB, lambda u: (BW, -u), 'right'), (180, [-5, -3, -1, 1, 3, 5], lambda u: (-u, -BD), 'back'), (-90, BZB, lambda u: (-BW, u), 'left')]
for ry, bays, f, tag in bfaces:
    for u in bays:
        x, z = f(u); wk = x if tag in ('front', 'back') else z
        put(GB[tag][wk], BX + x, YB, BZ + z, ry, ['barn', tag, 'ext'])
put('barn_wall_bigdoor', BX, YB, BZ + BD, 0, ['barn', 'front', 'ext'])
for ry, x, z in ((0, BW, BD), (90, BW, -BD), (180, -BW, -BD), (-90, -BW, BD)): put('barn_corner', BX + x, YB, BZ + z, ry, ['barn', 'ext'])
put('barn_gable_front', BX, YB, BZ + BD, 0, ['barn', 'front']); put('barn_gable_back', BX, YB, BZ - BD, 180, ['barn', 'back'])
for u in BZB:
    if abs(u) == 5: put('barn_roof_end', BX, YB, BZ + u, 0 if u > 0 else 180, ['barn', 'roof'])
    else: put('barn_roof', BX, YB, BZ + u, 0, ['barn', 'roof'])
for a in [-5, -3, -1, 1, 3, 5]:
    for b in BZB: put('barn_floor', BX + a, YB, BZ + b, 0, ['barn', 'floor0'])
put('barn_ramp', BX, YB, BZ + BD, 0, ['barn', 'front'])
put('barn_ramp_small', BX - BW, YB, BZ - 3, -90, ['barn', 'left']); put('barn_ramp_small', BX - 1, YB, BZ - BD, 180, ['barn', 'back'])
for s, ry, op in ((-1, 0, 85), (1, 180, -85)): put('barn_door_leaf', BX + s * (BDW / 2 - 0.08), YB + 0.005, BZ + BD - 0.15, ry, ['barn', 'front', 'ext'], door=op)
hx, hz = hinge(-BW, -3.0, -90, -0.44, -0.14); put('barn_door_small', BX + hx, YB + 0.005, BZ + hz, -90, ['barn', 'left', 'ext'], door=85)
hx, hz = hinge(-1.0, -BD, 180, -0.44, -0.14); put('barn_door_small', BX + hx, YB + 0.005, BZ + hz, 180, ['barn', 'back', 'ext'], door=85)
for x, z, ry in ((-BW, 5.65, -90), (-BW, -5.65, -90), (BW, 5.65, 90), (BW, -5.65, 90)): put('downspout_barn', BX + x, 0, BZ + z, ry, ['barn', 'ext'])
put('wall_lantern', BX + 2.35, YB + 2.9, BZ + BD + 0.04, 0, ['barn', 'front'])
put('player_scale_ref', CX + 1.2, 0, SZ + PD + 1.6); put('player_scale_ref', CX - 2, Y0, 3, 0, ['store']); put('player_scale_ref', BX, YB, BZ, 0, ['barn'])

if __name__ == '__main__' or os.environ.get('EXPORTAR'):
    json.dump({'grid': {'module_width': W, 'floor_height': H, 'wall_thickness': T, 'slab': SLAB, 'floor_raise': RAISE,
                        'store': {'x': [CX - SX, CX + SX], 'z': [-SZ, SZ], 'false_front_top': FFT + 0.24},
                        'porch': {'x': [CX - SX, CX + SX], 'z': [SZ, SZ + PD]},
                        'barn': {'x': [BX - BW, BX + BW], 'z': [BZ - BD, BZ + BD], 'floor': RB, 'eave': YEB, 'ridge': round(YRB, 3)},
                        'roof': 'store: gable 30 deg, ridge along Z at x=-5 behind a false front; barn: gambrel 60/22 deg, ridge along Z',
                        'textures': 'PBR (albedo + normal + ORM), 2 m tiles, UV in metres / 2; sign has its own 0-1 UV'},
               'placements': L}, open(f'{OUT}/building_layout.json', 'w'), indent=1)
    sc = trimesh.Scene()
    for i, e in enumerate(L):
        if e['piece'] == 'player_scale_ref': continue
        Tm = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); Tm[:3, 3] = e['pos']
        s = pieces[e['piece']].scene(e['piece'])
        for nm, g in s.geometry.items():
            g = g.copy(); g.apply_transform(Tm); sc.add_geometry(g, node_name=f'{i}_{nm}', geom_name=f'{i}_{nm}')
    bym = {}
    for g in sc.geometry.values(): bym.setdefault(g.visual.material.name, []).append(g)
    sc2 = trimesh.Scene()
    for k, gs in bym.items():
        m = trimesh.util.concatenate(gs); m.visual.material = MATS[k]; sc2.add_geometry(m, node_name=f'building_{k}', geom_name=f'building_{k}')
    sc2.export(f'{OUT}/building_assembled.glb', include_normals=True); glb_jpeg(f'{OUT}/building_assembled.glb')
    tot = sum(len(g.faces) for g in sc2.geometry.values())
    print(len(pieces), 'pecas', len(L), 'posicoes', sum(1 for e in L if 'door' in e), 'portas', tot, 'triangulos no montado')
    for n, p in sorted(pieces.items(), key=lambda kv: -kv[1].tris())[:12]: print(f'  {n:28s} {p.tris():6d} tri')
