"""Gerador de texturas PBR para os kits (estilos novos, mais ricos que as texturas lisas originais).

Para cada material e cada estilo gera 3 imagens que se repetem sem emenda:
  <material>_albedo.png  cor (sRGB)
  <material>_normal.png  relevo (normal map, convencao OpenGL/glTF: verde = para cima), igual ao Godot
  <material>_orm.png     R = oclusao (AO), G = rugosidade, B = metalico (0)

Estilos:
  detalhado    realista e limpo: variacao por peca, bordas chanfradas, juntas fundas, granulado
  pintado      pintado a mao, combina com o visual toon + contorno: tons em faixas, luz pintada no topo
  envelhecido  realista + desgaste: lascas, rachaduras, sujeira nas juntas, manchas, musgo

Tamanho do ladrilho: 2 m (dobro do original de 1 m) para a repeticao aparecer menos.
Nos kits as UVs estao em metros / tamanho do ladrilho original, entao no motor use uv_scale = original / novo
(ex.: tijolo original 1 m, novo 2 m -> uv1_scale = 0.5). A tabela TILE abaixo guarda os dois tamanhos.

Uso:  python3 gerar_texturas.py [--px-por-m 256] [--saida out] [--cores cores.json]
So depende de numpy e Pillow.
"""
import numpy as np, os, json, argparse
from PIL import Image

# ----------------------------------------------------------------------------- utilidades periodicas
def _freq(h, w):
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    return fy, fx

def noise(h, w, sx, sy=None, seed=0):
    """Ruido gaussiano periodico (sem emenda). sx/sy = tamanho do detalhe em pixels. Media 0, desvio 1."""
    sy = sx if sy is None else sy
    r = np.random.RandomState(seed).standard_normal((h, w))
    fy, fx = _freq(h, w)
    F = np.fft.fft2(r) * np.exp(-2 * np.pi**2 * ((fx * sx)**2 + (fy * sy)**2))
    a = np.real(np.fft.ifft2(F)); return (a - a.mean()) / (a.std() + 1e-9)

def fbm(h, w, s, octaves=4, seed=0, sy_ratio=1.0, gain=0.5):
    a = np.zeros((h, w)); amp = 1.0; tot = 0
    for o in range(octaves):
        a += amp * noise(h, w, s, s * sy_ratio, seed + o * 17); tot += amp; amp *= gain; s = max(0.6, s / 2)
    return a / tot

def blur(a, s):
    h, w = a.shape; fy, fx = _freq(h, w)
    return np.real(np.fft.ifft2(np.fft.fft2(a) * np.exp(-2 * np.pi**2 * (fx**2 + fy**2) * s * s)))

def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def hash01(*k):
    v = 1469598103934665603
    for x in k:
        v = ((v ^ (int(x) & 0xffffffff)) * 1099511628211) & 0xffffffffffffffff
    return float((v >> 11) % 1000003) / 1000003.0

# ----------------------------------------------------------------------------- layout de pecas (tijolo, pedra, telha...)
def bond(h, w, rows, row_cuts, mortar, px):
    """rows: altura de cada fiada em m (soma = altura do ladrilho). row_cuts[r]: posicoes x (m) das juntas verticais
    da fiada r, periodicas na largura. Devolve id da peca, distancia ate a borda (m, <0 na junta), u,v locais (0..1)."""
    W_m = w / px
    ys = (np.arange(h) + 0.5) / px; xs = (np.arange(w) + 0.5) / px
    uid = np.zeros((h, w), np.int32); dist = np.zeros((h, w)); U = np.zeros((h, w)); V = np.zeros((h, w))
    y0 = 0.0
    for r, rh in enumerate(rows):
        sel = (ys >= y0) & (ys < y0 + rh)
        cuts = np.sort(np.asarray(row_cuts[r]) % W_m)
        ext = np.concatenate([cuts - W_m, cuts, cuts + W_m])
        k = np.searchsorted(ext, xs, side='right') - 1
        left = ext[k]; right = ext[k + 1]
        dx = np.minimum(xs - left, right - xs)
        yy = ys[sel][:, None]
        dy = np.minimum(yy - y0, y0 + rh - yy)
        dist[sel] = np.minimum(dx[None, :], dy) - mortar / 2
        uid[sel] = (r * 1000 + (k % len(cuts)))[None, :]
        U[sel] = ((xs - left) / (right - left))[None, :]
        V[sel] = (yy - y0) / rh
        y0 += rh
    return uid, dist, U, V

def per_unit(uid, seed):
    """Valor aleatorio 0..1 por peca, espalhado por pixel."""
    ids, inv = np.unique(uid, return_inverse=True)
    vals = np.array([hash01(i, seed) for i in ids])
    return vals[inv].reshape(uid.shape)

# ----------------------------------------------------------------------------- saida
def to_img(a):
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))

def normal_from_height(hm, px, strength=1.0):
    """hm em metros. Imagem com topo = para cima no mundo (UV v cresce para baixo, como nos kits)."""
    gx = (np.roll(hm, -1, 1) - np.roll(hm, 1, 1)) * 0.5 * px * strength
    gy = (np.roll(hm, -1, 0) - np.roll(hm, 1, 0)) * 0.5 * px * strength   # d/d(linha) = -d/d(cima)
    n = np.stack([-gx, gy, np.ones_like(hm)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n * 0.5 + 0.5

def cavity_ao(hm, px, depth, strength=1.0):
    c = blur(hm, 0.03 * px) - hm
    return np.clip(1 - strength * np.clip(c / depth, 0, 1) * 0.8, 0, 1)

def save_set(out, name, alb, hm, rough, px, nstr=1.0, ao_depth=0.01, ao_str=1.0):
    os.makedirs(out, exist_ok=True)
    ao = cavity_ao(hm, px, ao_depth, ao_str)
    to_img(np.clip(alb, 0, 1)).save(os.path.join(out, name + '_albedo.png'))
    to_img(normal_from_height(hm, px, nstr)).save(os.path.join(out, name + '_normal.png'))
    orm = np.stack([ao, np.clip(rough, 0.05, 1), np.zeros_like(ao)], -1)
    to_img(orm).save(os.path.join(out, name + '_orm.png'))

def rgb(c): return np.array(c, np.float64) / 255.0

def lerp(a, b, t): return a + (b - a) * t

def posterize(x, levels):  # para o estilo pintado: tons em faixas suaves
    q = np.floor(x * levels) / levels; f = x * levels - np.floor(x * levels)
    return q + smooth(0.75, 1.0, f) / levels

# ----------------------------------------------------------------------------- estilos comuns
STYLES = ('detalhado', 'pintado', 'envelhecido')

def weathering(h, w, px, seed, alb, hm, rough, mortar_mask, dirt_col=(70, 60, 50), moss=True, amount=1.0):
    """Manchas grandes, sujeira nas juntas, musgo nos baixos, rachaduras finas."""
    stain = smooth(0.2, 1.6, fbm(h, w, 0.35 * px, 4, seed + 300))
    streak = smooth(0.5, 2.0, noise(h, w, 0.03 * px, 0.6 * px, seed + 310))      # escorridos verticais
    d = np.clip(0.35 * stain + 0.35 * streak, 0, 1) * amount
    alb = lerp(alb, alb * rgb(dirt_col)[None, None] * 2.4, d[..., None] * 0.55)
    alb = lerp(alb, alb * 0.55, (mortar_mask * 0.6 * amount)[..., None])
    if moss:
        m = smooth(0.6, 1.8, fbm(h, w, 0.12 * px, 4, seed + 320)) * np.clip(mortar_mask + 0.25, 0, 1) * amount
        alb = lerp(alb, rgb((86, 104, 58))[None, None] * (0.8 + 0.3 * noise(h, w, 2, seed=seed + 321))[..., None], m[..., None] * 0.7)
        rough = rough + 0.08 * m
    crack = np.abs(noise(h, w, 0.12 * px, seed=seed + 330) + 0.15 * noise(h, w, 0.01 * px, seed=seed + 332))
    cm = (1 - smooth(0.0, 0.03, crack)) * smooth(1.0, 1.8, fbm(h, w, 0.4 * px, 2, seed + 331)) * amount
    alb = alb * (1 - 0.55 * cm[..., None]); hm = hm - 0.004 * cm
    return alb, hm, np.clip(rough + 0.06 * d, 0, 1)

# ----------------------------------------------------------------------------- materiais
def masonry(style, px, size, rows, cuts, mortar, palette, mortar_col, seed, bevel, irregular=0.0, recess=0.01,
            ao_depth=0.008):
    W, H = int(size[0] * px), int(size[1] * px)
    uid, dist, U, V = bond(H, W, rows, cuts, mortar, px)
    if irregular:  # bordas irregulares (pedra rustica / tijolo velho)
        dist = dist + irregular * fbm(H, W, 0.02 * px, 3, seed + 5)
    r1 = per_unit(uid, seed); r2 = per_unit(uid, seed + 1); r3 = per_unit(uid, seed + 2)
    pal = np.array([rgb(c) for c in palette])
    base = pal[np.minimum((r1 * len(pal)).astype(int), len(pal) - 1)]
    unit = smooth(0, 0.0015, dist)                  # 1 = peca, 0 = junta
    edge = smooth(0, bevel, dist)                   # perfil chanfrado
    grain = fbm(H, W, 0.012 * px, 3, seed + 10)
    big = fbm(H, W, 0.1 * px, 3, seed + 11)
    tilt = (U - 0.5) * (r2 - 0.5) * 0.004 + (V - 0.5) * (r3 - 0.5) * 0.003
    mort = rgb(mortar_col)[None, None] * (1 + 0.06 * grain[..., None])
    if style == 'pintado':
        shade = 0.92 + 0.08 * posterize(np.clip(0.5 + 0.25 * big, 0, 1), 3)
        alb = base * shade[..., None]
        top = smooth(0.12, 0.0, V) * edge * unit        # luz pintada no topo da peca
        bot = smooth(0.8, 1.0, V) * unit
        alb = alb * (1 + 0.22 * top[..., None]) * (1 - 0.18 * bot[..., None])
        stroke = noise(H, W, 0.025 * px, 0.006 * px, seed + 12)  # pinceladas horizontais
        alb = alb * (1 + 0.025 * stroke[..., None])
        alb = lerp(mort, alb, unit[..., None])
        hm = recess * edge + 0.00015 * stroke * unit
        rough = 0.72 + 0.04 * grain
        nstr = 0.7
    else:
        jitter = (np.stack([per_unit(uid, seed + 20 + i) for i in range(3)], -1) - 0.5) * 0.06
        alb = base * (1 + jitter) * (1 + 0.07 * big[..., None]) * (1 + 0.05 * grain[..., None])
        speck = (noise(H, W, 0.6, seed=seed + 13) > 2.3)
        alb = alb * (1 - 0.25 * speck[..., None]) * (1 - 0.12 * (1 - edge)[..., None] * unit[..., None])
        alb = lerp(mort, alb, unit[..., None])
        hm = recess * edge + tilt + 0.0012 * grain * unit + 0.0006 * fbm(H, W, 0.003 * px, 2, seed + 14)
        rough = 0.86 + 0.06 * grain - 0.05 * unit * r2
        nstr = 1.0
    if style == 'envelhecido':
        chips = smooth(0.9, 1.6, fbm(H, W, 0.015 * px, 3, seed + 40)) * smooth(0.02, 0.0, dist) * unit
        hm = hm - recess * 0.8 * chips
        alb = alb * (1 - 0.25 * chips[..., None])
        alb, hm, rough = weathering(H, W, px, seed, alb, hm, rough, 1 - unit)
    return alb, hm, rough, nstr, ao_depth

def running(size_x, n_rows, unit_w, offset=0.5):
    return [[i * unit_w + (offset * unit_w if r % 2 else 0) for i in range(int(round(size_x / unit_w)))] for r in range(n_rows)]

def random_cuts(size_x, n_rows, wmin, wmax, seed):
    rs = np.random.RandomState(seed); out = []
    for r in range(n_rows):
        x = rs.uniform(0, wmax); start = x; c = []
        while x < start + size_x - wmin:
            c.append(x); x += rs.uniform(wmin, wmax)
        out.append(c)
    return out

def stucco(style, px, size, col, seed, coarse=1.0):
    W, H = int(size[0] * px), int(size[1] * px)
    c = rgb(col)[None, None]
    blot = fbm(H, W, 0.25 * px, 4, seed); grain = fbm(H, W, 0.006 * px, 3, seed + 1)
    trowel = noise(H, W, 0.15 * px, 0.05 * px, seed + 2)
    if style == 'pintado':
        alb = c * (0.95 + 0.05 * posterize(np.clip(0.5 + 0.3 * blot, 0, 1), 3))[..., None]
        alb = alb * (1 + 0.03 * noise(H, W, 0.06 * px, 0.006 * px, seed + 3)[..., None])
        hm = 0.0008 * trowel + 0.0003 * grain; rough = 0.8 + 0 * grain; nstr = 0.8
    else:
        alb = c * (1 + 0.045 * blot[..., None] + 0.03 * grain[..., None])
        pits = smooth(1.8, 2.6, noise(H, W, 0.8, seed=seed + 4))
        hm = (0.0012 * trowel + 0.0007 * grain - 0.0012 * pits) * coarse
        alb = alb * (1 - 0.12 * pits[..., None]); rough = 0.9 + 0.04 * grain; nstr = 1.0
    if style == 'envelhecido':
        alb, hm, rough = weathering(H, W, px, seed, alb, hm, rough, np.zeros((H, W)), moss=False, amount=0.8)
        # reboco descascado: placas onde aparece o tijolo/base por baixo
        peel = smooth(1.3, 1.45, fbm(H, W, 0.12 * px, 4, seed + 50))
        alb = lerp(alb, rgb((150, 104, 84))[None, None] * (1 + 0.1 * grain[..., None]), peel[..., None])
        hm = hm - 0.003 * peel; rough = rough + 0.05 * peel
    return alb, hm, rough, nstr, 0.002

def clay_tiles(style, px, size, col, seed):
    W, H = int(size[0] * px), int(size[1] * px)
    rows = [0.25] * int(round(size[1] / 0.25))
    uid, dist, U, V = bond(H, W, rows, running(size[0], len(rows), 0.2), 0.008, px)
    r1 = per_unit(uid, seed); r2 = per_unit(uid, seed + 1)
    barrel = np.sin(np.clip(U, 0, 1) * np.pi)                    # telha curva
    over = smooth(0.62, 0.78, V)                                  # sombra da fiada de cima (como no original)
    hm = 0.012 * barrel * smooth(0, 0.004, dist) - 0.006 * over + 0.004 * V
    c = rgb(col)[None, None] * (0.9 + 0.2 * r1[..., None])
    grain = fbm(H, W, 0.01 * px, 3, seed + 3)
    if style == 'pintado':
        alb = c * (1 + 0.18 * smooth(0.6, 1.0, barrel)[..., None] * (1 - over[..., None]))
        alb = alb * (1 - 0.35 * over[..., None]); rough = 0.65 + 0 * V; nstr = 0.8
    else:
        alb = c * (1 + 0.06 * grain[..., None] + 0.08 * fbm(H, W, 0.08 * px, 2, seed + 4)[..., None])
        alb = alb * (1 - 0.3 * over[..., None]); rough = 0.75 + 0.08 * grain - 0.06 * r2; nstr = 1.0
    alb = lerp(alb * 0.35, alb, smooth(0, 0.004, dist)[..., None])
    if style == 'envelhecido':
        lichen = smooth(1.0, 1.9, fbm(H, W, 0.03 * px, 4, seed + 60))
        alb = lerp(alb, rgb((176, 170, 120))[None, None], lichen[..., None] * 0.6)
        alb, hm, rough = weathering(H, W, px, seed, alb, hm, rough, over, dirt_col=(60, 56, 48))
    return alb, hm, rough, nstr, 0.01

def shingles(style, px, size, col, seed):
    W, H = int(size[0] * px), int(size[1] * px)
    rows = [0.2] * int(round(size[1] / 0.2))
    cuts = [[x + (0.15 if r % 2 else 0) + np.random.RandomState(seed + r).uniform(-0.04, 0.04) for x in np.arange(0, size[0], 0.333333)] for r in range(len(rows))]
    uid, dist, U, V = bond(H, W, rows, cuts, 0.012, px)
    r1 = per_unit(uid, seed); grain = fbm(H, W, 0.004 * px, 3, seed + 2)
    c = rgb(col)[None, None] * (0.85 + 0.3 * r1[..., None])
    over = smooth(0.0, 0.25, V)        # borda inferior da fiada de cima projeta sombra no topo
    hm = 0.004 * V + 0.003 * smooth(0, 0.002, dist) + 0.0006 * grain
    if style == 'pintado':
        alb = c * (0.75 + 0.25 * over[..., None]) * (1 + 0.12 * smooth(0.9, 1.0, V)[..., None]); rough = 0.7 + 0 * V; nstr = 0.8
    else:
        sand = noise(H, W, 0.7, seed=seed + 3)                    # granulos minerais
        alb = c * (1 + 0.12 * sand[..., None]) * (0.72 + 0.28 * over[..., None]); rough = 0.92 + 0.03 * sand; nstr = 1.0
    alb = lerp(alb * 0.4, alb, smooth(0, 0.002, dist)[..., None])
    if style == 'envelhecido':
        alb, hm, rough = weathering(H, W, px, seed, alb, hm, rough, 1 - smooth(0, 0.002, dist), dirt_col=(50, 50, 40))
    return alb, hm, rough, nstr, 0.004

def siding(style, px, size, col, seed):
    W, H = int(size[0] * px), int(size[1] * px)
    board = 0.2; ys = ((np.arange(H) + 0.5) / px)[:, None] * np.ones((1, W))
    v = (ys % board) / board                                       # 0 topo da tabua, 1 base
    row = (ys // board).astype(int)
    hm = 0.012 * v - 0.012 * smooth(0.93, 1.0, v)                  # tabua inclinada sobreposta
    woodg = noise(H, W, 0.5 * px, 0.002 * px, seed + 1)            # veio da madeira (alongado em x)
    c = rgb(col)[None, None]
    if style == 'pintado':
        alb = c * (0.82 + 0.22 * v[..., None]) * (1 + 0.04 * woodg[..., None])
        rough = 0.6 + 0 * v; nstr = 0.8
        alb = alb * (1 + 0.15 * smooth(0.9, 0.97, v)[..., None])
    else:
        rv = np.vectorize(lambda r: hash01(r, seed))(row)
        alb = c * (0.95 + 0.07 * rv[..., None]) * (1 + 0.035 * woodg[..., None]) * (0.86 + 0.14 * v[..., None])
        hm = hm + 0.0004 * woodg; rough = 0.55 + 0.1 * fbm(H, W, 0.05 * px, 2, seed + 2); nstr = 1.0
    alb = alb * (1 - 0.45 * smooth(0.0, 0.05, 0.05 - v)[..., None])          # sombra embaixo da tabua de cima
    if style == 'envelhecido':
        peel = smooth(1.1, 1.3, fbm(H, W, 0.04 * px, 4, seed + 70, sy_ratio=0.5))
        alb = lerp(alb, rgb((150, 130, 104))[None, None] * (1 + 0.1 * woodg[..., None]), peel[..., None])
        hm = hm - 0.0008 * peel; rough = rough + 0.3 * peel
        alb, hm, rough = weathering(H, W, px, seed, alb, hm, rough, smooth(0.9, 1.0, v), moss=False)
    return alb, hm, rough, nstr, 0.006

# ----------------------------------------------------------------------------- catalogo
# nome: (funcao, tamanho novo do ladrilho em m, tamanho original em m)
CORES = {   # cores base (podem ser trocadas por kit com --cores)
    'brick': [(178, 80, 58), (166, 72, 52), (188, 90, 64), (156, 66, 50), (194, 100, 72), (150, 76, 58)],
    'brick_mortar': (206, 192, 168),
    'stone': [(206, 197, 180), (196, 187, 170), (214, 206, 190), (200, 190, 172)], 'stone_mortar': (160, 150, 136),
    'stone2': [(214, 190, 150), (200, 176, 138), (222, 200, 162), (190, 170, 136)], 'stone2_mortar': (150, 130, 104),
    'plaster': (238, 230, 214), 'render': (206, 112, 78), 'roof_tiles': (128, 72, 50),
    'shingles': (62, 64, 72), 'siding': (124, 148, 106),
}

def materials(cores):
    return {
        'brick': (lambda s, px: masonry(s, px, (2, 2), [0.125] * 16, running(2, 16, 0.25), 0.012, cores['brick'], cores['brick_mortar'], 7,
                                        0.008, irregular=0.0015 if s != 'pintado' else 0.0), (2, 2), (1, 1)),
        'stone': (lambda s, px: masonry(s, px, (2, 1.6), [0.4] * 4, running(2, 4, 1.0), 0.014, cores['stone'], cores['stone_mortar'], 3,
                                        0.012, irregular=0.002 if s == 'envelhecido' else 0.0), (2, 1.6), (1, 0.8)),
        'stone2': (lambda s, px: masonry(s, px, (2, 1.2), [0.2] * 6, random_cuts(2, 6, 0.35, 0.7, 31), 0.016, cores['stone2'], cores['stone2_mortar'], 9,
                                         0.02, irregular=0.006 if s != 'pintado' else 0.002, recess=0.014), (2, 1.2), (1, 0.6)),
        'plaster': (lambda s, px: stucco(s, px, (2, 2), cores['plaster'], 5, coarse=0.6), (2, 2), (1, 1)),
        'render': (lambda s, px: stucco(s, px, (2, 2), cores['render'], 21), (2, 2), (1, 1)),
        'roof_tiles': (lambda s, px: clay_tiles(s, px, (2, 2), cores['roof_tiles'], 23), (2, 2), (1, 1)),
        'shingles': (lambda s, px: shingles(s, px, (2, 2), cores['shingles'], 41), (2, 2), (1, 1)),
        'siding': (lambda s, px: siding(s, px, (2, 2), cores['siding'], 51), (2, 2), (1, 1)),
    }

def gerar(out, px, cores=CORES, so=None, estilos=STYLES):
    info = {}
    for name, (fn, tile, orig) in materials(cores).items():
        if so and name not in so: continue
        for s in estilos:
            alb, hm, rough, nstr, aod = fn(s, px)
            save_set(os.path.join(out, s), name, alb, hm, rough, px, nstr, aod)
        info[name] = {'ladrilho_m': tile, 'original_m': orig, 'uv_scale': [orig[0] / tile[0], orig[1] / tile[1]]}
    json.dump(info, open(os.path.join(out, 'texturas.json'), 'w'), indent=1)
    return info

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--px-por-m', type=int, default=256)
    ap.add_argument('--saida', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'))
    ap.add_argument('--cores', help='json com cores para sobrescrever CORES')
    ap.add_argument('--so', nargs='*')
    a = ap.parse_args()
    cores = dict(CORES)
    if a.cores: cores.update({k: (tuple(v) if not isinstance(v[0], list) else [tuple(x) for x in v]) for k, v in json.load(open(a.cores)).items()})
    print(json.dumps(gerar(a.saida, a.px_por_m, cores, a.so), indent=1))
