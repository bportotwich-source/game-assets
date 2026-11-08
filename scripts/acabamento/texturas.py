"""Texturas dos acabamentos internos (papel de parede, azulejo, lambri, pisos...), 1 x 1 m, sem emenda.

Grava acabamentos/<nome>_albedo.png, _normal.png e _orm.png (R oclusao, G rugosidade, B metalico), todas do
mesmo tamanho, porque o Godot junta tudo num Texture2DArray (uma camada por acabamento, na ordem de CAMADAS).
A imagem tem o topo para cima (nas paredes) e o norte (-Z) para cima (nos pisos).

Uso: python3 scripts/acabamento/texturas.py [--px 512]
So depende de numpy e Pillow (usa as funcoes de scripts/texturas/gerar_texturas.py).
"""
import argparse, json, math, os, sys
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'scripts', 'texturas'))
from gerar_texturas import noise, fbm, blur, smooth, save_set, rgb, lerp, hash01, bond, per_unit

SAIDA = os.path.join(RAIZ, 'acabamentos')


def grade(px):
    y, x = np.mgrid[0:px, 0:px]
    return (x + 0.5) / px, (y + 0.5) / px          # metros (0..1), y para baixo


def grao(px, s, amt, seed):
    return 1 + amt * fbm(px, px, s, 3, seed)


# ---------------------------------------------------------------------------------------------- paredes
def pintura(px):
    """Tinta acrilica sobre reboco: branco texturizado, o Godot tinge com a cor do comodo."""
    x, y = grade(px)
    hm = 0.0006 * fbm(px, px, 0.006 * px, 4, 1) + 0.0003 * noise(px, px, 1.2, seed=2)
    alb = np.ones((px, px, 3)) * 0.93 * grao(px, 0.05 * px, 0.025, 3)[..., None]
    return alb, hm, 0.82 + 0.05 * noise(px, px, 3, seed=4)


def _papel(px, base, fundo_grao=0.03):
    alb = np.ones((px, px, 3)) * rgb(base)[None, None]
    alb *= grao(px, 0.01 * px, fundo_grao, 7)[..., None]
    hm = 0.00015 * noise(px, px, 1.5, seed=8)
    return alb, hm


def papel_listrado(px):
    x, y = grade(px)
    alb, hm = _papel(px, (150, 168, 140))
    f = (x * 5.0) % 1.0                                     # 5 listras por metro (0,2 m)
    larga = smooth(0.08, 0.10, f) * (1 - smooth(0.36, 0.38, f))
    fina = smooth(0.52, 0.53, f) * (1 - smooth(0.56, 0.57, f)) + smooth(0.62, 0.63, f) * (1 - smooth(0.66, 0.67, f))
    alb = lerp(alb, rgb((222, 214, 186))[None, None], larga[..., None])
    alb = lerp(alb, rgb((116, 136, 108))[None, None], fina[..., None])
    # losango pequeno no meio da listra larga
    cx = (np.floor(x * 5.0) + 0.23) / 5.0; cy = (np.round(y * 4.0 + 0.5 * (np.floor(x * 5.0) % 2)) - 0.5 * (np.floor(x * 5.0) % 2)) / 4.0
    d = np.abs(x - cx) / 0.022 + np.abs(y - cy) / 0.032
    alb = lerp(alb, rgb((196, 186, 150))[None, None], (1 - smooth(0.85, 1.0, d))[..., None])
    hm = hm - 0.0002 * (1 - smooth(0.85, 1.0, d))
    return alb, hm, 0.7


def papel_floral(px):
    """Raminhos miudos espalhados sobre rosa antigo."""
    x, y = grade(px)
    alb, hm = _papel(px, (206, 170, 160))
    rng = np.random.RandomState(11)
    for i in range(6):
        for j in range(6):
            cx = (i + 0.5 + (j % 2) * 0.5) / 6 + rng.uniform(-0.02, 0.02); cy = (j + 0.5) / 6 + rng.uniform(-0.02, 0.02)
            for k in range(5):
                a = k / 5 * 2 * math.pi + rng.uniform(0, 0.4)
                px_ = cx + 0.022 * math.cos(a); py_ = cy + 0.022 * math.sin(a)
                dx = (x - px_ + 0.5) % 1 - 0.5; dy = (y - py_ + 0.5) % 1 - 0.5
                m = 1 - smooth(0.009, 0.013, np.sqrt(dx * dx + dy * dy))
                alb = lerp(alb, rgb((176, 92, 96))[None, None], m[..., None])
            dx = (x - cx + 0.5) % 1 - 0.5; dy = (y - cy + 0.5) % 1 - 0.5
            alb = lerp(alb, rgb((232, 206, 120))[None, None], (1 - smooth(0.006, 0.009, np.sqrt(dx * dx + dy * dy)))[..., None])
            for s in (-1, 1):                               # folhinhas
                lx = (x - (cx + s * 0.04) + 0.5) % 1 - 0.5; ly = (y - (cy + 0.035) + 0.5) % 1 - 0.5
                m = 1 - smooth(0.8, 1.0, np.sqrt((lx / 0.016) ** 2 + (ly / 0.008) ** 2))
                alb = lerp(alb, rgb((108, 132, 96))[None, None], m[..., None])
    return alb, hm, 0.72


def papel_damasco(px):
    """Medalhao simetrico em azul sobre azul (efeito acetinado)."""
    x, y = grade(px)
    alb, hm = _papel(px, (78, 98, 128))
    u = (x * 2.0) % 1.0 - 0.5; v = (y * 2.0) % 1.0 - 0.5
    u2 = ((x * 2.0 + 0.5) % 1.0) - 0.5; v2 = ((y * 2.0 + 0.5) % 1.0) - 0.5
    def medalhao(u, v):
        r = np.sqrt((np.abs(u) * 1.3) ** 2 + v ** 2); a = np.arctan2(v, np.abs(u))
        petala = 0.17 + 0.07 * np.cos(4 * a) + 0.03 * np.cos(9 * a)
        borda = np.abs(r - petala) < 0.012
        miolo = r < 0.05
        folha = (np.abs(np.abs(u) - 0.09 - 0.25 * v * v) < 0.01) & (np.abs(v) < 0.3) & (r > petala)
        return (borda | miolo | folha).astype(float)
    m = np.clip(medalhao(u, v) + 0.6 * medalhao(u2 * 1.6, v2 * 1.6), 0, 1)
    m = blur(m, 0.8)
    alb = lerp(alb, rgb((124, 144, 172))[None, None], np.clip(m * 1.4, 0, 1)[..., None])
    return alb, hm + 0.0002 * m, 0.55 - 0.15 * m


def papel_losango(px):
    x, y = grade(px)
    alb, hm = _papel(px, (196, 160, 86))
    u = (x * 6.0) % 1.0 - 0.5; v = (y * 4.0) % 1.0 - 0.5
    d = np.abs(u) + np.abs(v) * 1.0
    linha = 1 - smooth(0.0, 0.03, np.abs(d - 0.42))
    centro = 1 - smooth(0.06, 0.08, d)
    alb = lerp(alb, rgb((236, 222, 186))[None, None], linha[..., None])
    alb = lerp(alb, rgb((120, 70, 44))[None, None], centro[..., None])
    return alb, hm, 0.72


def papel_infantil(px):
    """Bolinhas e estrelas coloridas sobre azul claro."""
    x, y = grade(px)
    alb, hm = _papel(px, (176, 208, 222))
    cores = [(240, 200, 80), (226, 120, 110), (130, 190, 130), (250, 250, 240)]
    rng = np.random.RandomState(5)
    for i in range(5):
        for j in range(5):
            cx = (i + 0.5) / 5 + rng.uniform(-0.04, 0.04); cy = (j + 0.5) / 5 + rng.uniform(-0.04, 0.04)
            dx = (x - cx + 0.5) % 1 - 0.5; dy = (y - cy + 0.5) % 1 - 0.5
            c = rgb(cores[(i + 2 * j) % 4])
            if (i + j) % 2 == 0:
                r = np.sqrt(dx * dx + dy * dy); a = np.arctan2(dy, dx)
                m = 1 - smooth(0.0, 0.004, r - (0.022 + 0.012 * np.cos(5 * a + 1.57)))
            else:
                m = 1 - smooth(0.012, 0.015, np.sqrt(dx * dx + dy * dy))
            alb = lerp(alb, c[None, None], m[..., None])
    return alb, hm, 0.7


def _azulejo(px, n_x, n_y, cor, junta=0.003, var=0.035, cor_junta=(206, 204, 196), rows_offset=0.0, seed=21, vidrado=0.12):
    W = 1.0
    rows = [W / n_y] * n_y
    cuts = [[(k + (r % 2) * rows_offset) * W / n_x for k in range(n_x)] for r in range(n_y)]
    uid, dist, U, V = bond(px, px, rows, cuts, junta, px)
    pu = per_unit(uid, seed)
    alb = rgb(cor)[None, None] * (1 + var * (pu - 0.5) * 2)[..., None]
    borda = smooth(-0.0005, 0.004, dist)
    alb = lerp(rgb(cor_junta)[None, None] * np.ones_like(alb), alb, borda[..., None])
    alb *= grao(px, 0.02 * px, 0.012, seed + 1)[..., None]
    hm = 0.003 * borda + 0.0003 * noise(px, px, 0.2 * px, seed=seed + 2) * borda
    rough = lerp(0.9, vidrado, borda)
    return alb, hm, rough


def azulejo_branco(px):  return _azulejo(px, 7, 7, (236, 236, 230))                         # ~15 x 15 cm
def azulejo_metro(px):   return _azulejo(px, 7, 13, (232, 234, 230), rows_offset=0.5, seed=23)  # 15 x 7,5 cm desencontrado
def azulejo_verde(px):   return _azulejo(px, 7, 7, (150, 196, 184), var=0.06, seed=25)


def lambri_madeira(px):
    """Lambri de madeira com almofadas (0,5 m por painel); fica so na parte de baixo da parede."""
    x, y = grade(px)
    veio = fbm(px, px, 0.004 * px, 3, 31, sy_ratio=12.0)
    base = rgb((116, 76, 48))[None, None] * (1 + 0.10 * veio)[..., None] * grao(px, 0.2 * px, 0.06, 32)[..., None]
    u = (x * 2.0) % 1.0; v = y
    moldura = np.minimum(np.minimum(u, 1 - u) * 0.5, np.minimum(v, 1 - v))      # distancia ate a borda do painel (m)
    alm = smooth(0.05, 0.07, moldura)                                           # almofada
    canal = 1 - smooth(0.0, 0.012, np.abs(moldura - 0.06))
    hm = 0.006 * alm - 0.003 * canal
    alb = base * (1 - 0.18 * canal)[..., None] * (1 + 0.05 * alm)[..., None]
    return alb, hm, 0.5


def lambri_tabuado(px):
    """Tabuado vertical pintado (meia-parede de cozinha e corredor): tabuas de 10 cm com friso."""
    x, y = grade(px)
    f = (x * 10.0) % 1.0
    friso = 1 - smooth(0.0, 0.06, np.minimum(f, 1 - f))
    alb = np.ones((px, px, 3)) * rgb((232, 228, 214))[None, None] * grao(px, 0.03 * px, 0.02, 41)[..., None]
    alb *= (1 - 0.3 * friso)[..., None]
    return alb, -0.002 * friso, 0.45


# ---------------------------------------------------------------------------------------------- pisos
def taco(px):
    x, y = grade(px)
    L, Wt = 0.25, 0.0625                                    # taco de 25 x 6,25 cm em espinha de peixe
    a = (x + y) / math.sqrt(2); b = (y - x) / math.sqrt(2)
    s = L / math.sqrt(2) * 2                                # periodo de 1 m precisa de passo que divida 1: ajusta pelo 4x4
    col = np.floor((x * 4.0)) ; rowi = np.floor((y * 16.0))
    lado = ((col + rowi) % 2)
    ux = (x * 4.0) % 1.0; uy = (y * 16.0) % 1.0
    uid = (col * 100 + rowi).astype(np.int64)
    pu = per_unit(uid.astype(np.int32), 51)
    veio = fbm(px, px, 0.003 * px, 3, 52, sy_ratio=0.12)
    veio2 = fbm(px, px, 0.003 * px, 3, 53, sy_ratio=8.0)
    v = np.where(lado > 0, veio, veio2)
    cor = rgb((140, 92, 56))[None, None] * (0.82 + 0.36 * pu)[..., None] * (1 + 0.1 * v)[..., None]
    junta = np.minimum(np.minimum(ux, 1 - ux) * 0.25, np.minimum(uy, 1 - uy) * 0.0625)
    borda = smooth(0.0, 0.0025, junta)
    alb = cor * (0.55 + 0.45 * borda)[..., None]
    return alb, 0.001 * borda, 0.55 - 0.1 * borda


def tabua_corrida(px):
    rows = [1.0 / 7] * 7                                    # tabuas de ~14 cm (no piso: ao longo de X)
    cuts = [[hash01(r, 1) * 0.9 + 0.05, (hash01(r, 1) * 0.9 + 0.55) % 1.0] for r in range(7)]
    uid, dist, U, V = bond(px, px, rows, cuts, 0.002, px)
    pu = per_unit(uid, 61)
    veio = fbm(px, px, 0.004 * px, 4, 62, sy_ratio=0.08)
    alb = rgb((150, 104, 66))[None, None] * (0.8 + 0.4 * pu)[..., None] * (1 + 0.12 * veio)[..., None]
    borda = smooth(-0.0005, 0.002, dist)
    alb *= (0.5 + 0.5 * borda)[..., None]
    return alb, 0.001 * borda, 0.5


def ladrilho_xadrez(px):
    x, y = grade(px)
    n = 5
    c = ((np.floor(x * n) + np.floor(y * n)) % 2)
    u = (x * n) % 1; v = (y * n) % 1
    junta = smooth(0.0, 0.015, np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v)))
    alb = lerp(rgb((236, 232, 222))[None, None] * np.ones((px, px, 3)), rgb((40, 40, 42))[None, None] * np.ones((px, px, 3)), c[..., None])
    alb *= grao(px, 0.02 * px, 0.03, 71)[..., None]
    alb = lerp(rgb((150, 146, 138))[None, None] * np.ones_like(alb), alb, junta[..., None])
    return alb, 0.0015 * junta, lerp(0.8, 0.25, junta)


def ceramica_bege(px):  return _azulejo(px, 3, 3, (204, 186, 156), junta=0.005, var=0.05, cor_junta=(160, 150, 136), seed=81, vidrado=0.35)
def vinilico(px):       return _azulejo(px, 3, 3, (196, 194, 184), junta=0.0015, var=0.07, cor_junta=(170, 168, 160), seed=91, vidrado=0.5)


def cimento_queimado(px):
    alb = np.ones((px, px, 3)) * rgb((150, 148, 142))[None, None]
    m = fbm(px, px, 0.15 * px, 5, 101)
    alb *= (1 + 0.08 * m + 0.03 * noise(px, px, 2, seed=102))[..., None]
    return alb, 0.0003 * noise(px, px, 3, seed=103), 0.45 + 0.15 * smooth(-1, 1, m)


# Ordem = camada do Texture2DArray. Nao mude a ordem sem regenerar os acabamento.json dos kits.
CAMADAS = [('pintura', pintura), ('papel_listrado', papel_listrado), ('papel_floral', papel_floral), ('papel_damasco', papel_damasco),
           ('papel_losango', papel_losango), ('papel_infantil', papel_infantil), ('azulejo_branco', azulejo_branco), ('azulejo_metro', azulejo_metro),
           ('azulejo_verde', azulejo_verde), ('lambri_madeira', lambri_madeira), ('lambri_tabuado', lambri_tabuado), ('taco', taco),
           ('tabua_corrida', tabua_corrida), ('ladrilho_xadrez', ladrilho_xadrez), ('ceramica_bege', ceramica_bege), ('vinilico', vinilico),
           ('cimento_queimado', cimento_queimado)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--px', type=int, default=512); a = ap.parse_args()
    os.makedirs(SAIDA, exist_ok=True)
    for nome, f in CAMADAS:
        alb, hm, rough = f(a.px)
        if np.isscalar(rough): rough = np.full(hm.shape, rough)
        save_set(SAIDA, nome, np.clip(alb, 0, 1), hm, rough, a.px, nstr=1.0, ao_depth=0.003)
        print(nome, flush=True)
    json.dump(dict(camadas=[n for n, _ in CAMADAS], tamanho_m=1.0, px=a.px), open(os.path.join(SAIDA, 'camadas.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
