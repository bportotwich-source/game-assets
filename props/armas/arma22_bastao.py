# Arma 21: bastao de madeira melhorado na bancada (a partir do taco do loot): com pregos ou com arame farpado.
# Executado por gerar_armas.py depois de arma21_lanca.py (usa _tubo3d). Desenho proprio, sem marca.
# Plano de lado: x frente (do pomo para a ponta grossa), y cima, z direita. Pivo na mao de baixo (perto do pomo).
CORES.update({'madeira_taco': (172, 128, 82), 'aco_prego': (96, 94, 90), 'arame_farpado': (104, 100, 94)})
METAL.update({'madeira_taco': (0.0, 0.55), 'aco_prego': (0.8, 0.5), 'arame_farpado': (0.75, 0.55)})

TACO_L = 0.84


def _tex_taco(seed, px=1024, tile=0.25):
    """Freixo claro gasto: veio comprido, aneis mais escuros, encardido e riscos de uso."""
    n = int(tile * px); veio = GT.noise(n, n, 0.05 * px, 0.0012 * px, seed); f = GT.fbm(n, n, 0.03 * px, 4, seed + 1)
    anel = GT.smooth(0.55, 0.8, GT.noise(n, n, 0.08 * px, 0.004 * px, seed + 3))
    risco = GT.smooth(0.93, 1.0, GT.noise(n, n, 0.002 * px, 0.03 * px, seed + 4))
    c = GT.rgb(CORES['madeira_taco'])[None, None]
    alb = c * (0.86 + 0.08 * veio[..., None] + 0.07 * f[..., None] - 0.05 * anel[..., None] + 0.06 * risco[..., None])
    hm = 0.00005 * veio - 0.00008 * risco
    return alb, hm, 0.55 + 0.1 * f, 0.6, 0.0002, tile, px


_materiais_antes_22 = materiais
def materiais():
    _materiais_antes_22()
    alb, hm, rough, nstr, aod, tile, px = _tex_taco(2201)
    a, nm, o = tex_set(alb, hm, rough, nstr, aod, px)
    TEX['madeira_taco'] = (a, nm, o); gp.UV_ESCALA['madeira_taco'] = tile
    MATS['madeira_taco'] = PBRMaterial(name='madeira_taco', baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                                       baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)


def _r_taco(x):
    """raio do taco em x (0 = pomo, TACO_L = ponta)."""
    if x < 0.014: return 0.022
    if x < 0.03: return 0.022 - (0.022 - 0.0128) * (x - 0.014) / 0.016
    if x < 0.30: return 0.0128 + 0.0012 * (x - 0.03) / 0.27
    if x < 0.62: s = (x - 0.30) / 0.32; return 0.014 + (0.0335 - 0.014) * (3 * s * s - 2 * s ** 3)
    return 0.0335


def _taco(q, rng, fita=True):
    prof = [(0.0, 0.0), (0.017, 0.0), (0.021, 0.003), (0.022, 0.009), (0.0205, 0.014)]
    prof += [(_r_taco(x), x) for x in np.linspace(0.03, TACO_L - 0.012, 80)]
    prof += [(0.032, TACO_L - 0.006), (0.0285, TACO_L - 0.002), (0.018, TACO_L), (0.0, TACO_L + 0.001)]
    corpo = torno_x(prof, 36)
    # amassados e lascas de uso no barril
    mossas = []
    for _ in range(14):
        x = rng.uniform(0.5, 0.82); a = rng.uniform(0, 2 * math.pi); r = _r_taco(x)
        s = trimesh.creation.icosphere(1, radius=rng.uniform(0.003, 0.006)); s.apply_scale([rng.uniform(1.0, 2.2), 1, 1])
        s.apply_translation([x, (r + 0.0035) * math.cos(a), (r + 0.0035) * math.sin(a)]); mossas.append(s)
    q.add('madeira_taco', menos(corpo, *mossas))
    if fita:                                                             # pega de fita isolante preta, enrolada em espiral
        for k, x in enumerate(np.arange(0.03, 0.27, 0.014)):
            r = _r_taco(x + 0.01)
            _anel_fita(x, x + 0.02, r + 0.00005 + 0.00025 * (k % 2), 'borracha_grip', q, (rng.uniform(-2, 2), 6.0))
        q.add('borracha_grip', solido(arred([(0.268, 0.012), (0.29, 0.011), (0.292, 0.0138), (0.27, 0.0142)], 0.001), -0.006, 0.006, 0.0002))


def _anims_bastao(A, prende):
    A.anim('golpear', 0.7, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.22, 50), (0.4, -60), (0.7, 0)])), (None, 'r', (0, 1, 0), pose([(0, 0), (0.22, -30), (0.4, 35), (0.7, 0)])),
                            (None, 't', pose([(0, (0, 0, 0)), (0.22, (-0.06, 0.08, 0.04)), (0.4, (0.06, -0.05, -0.04)), (0.7, (0, 0, 0))]))],
           desc='golpe na diagonal com as duas mãos: acerto entre 0,3 e 0,42 s no encaixe barril')
    A.anim('golpe_forte', 1.1, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.5, 100), (0.58, 100), (0.76, -70), (1.1, 0)])),
                                (None, 't', pose([(0, (0, 0, 0)), (0.5, (-0.12, 0.16, 0)), (0.58, (-0.12, 0.16, 0)), (0.76, (0.1, -0.12, 0)), (1.1, (0, 0, 0))]))],
           desc='levanta por cima da cabeça e desce com tudo: acerto entre 0,64 e 0,78 s (derruba)')
    A.anim('estocar', 0.5, [(None, 't', pose([(0, (0, 0, 0)), (0.12, (-0.06, 0, 0)), (0.24, (0.2, 0, 0)), (0.32, (0.2, 0, 0)), (0.5, (0, 0, 0))]))],
           desc='cutucada com a ponta para afastar (empurra, pouco dano)')
    if prende:
        A.anim('puxar', 0.9, [(None, 't', pose([(0, (0, 0, 0)), (0.3, (0.0, 0.0, 0)), (0.45, (-0.08, 0.02, 0)), (0.9, (0, 0, 0))])),
                              (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, -6), (0.35, 6), (0.45, 10), (0.9, 0)]))],
               desc=f'quando {prende} prende no alvo: sacode e arranca (toque depois de um acerto que prendeu)')
    A.anim('inspecionar', 2.4, [(None, 't', pose([(0, (0, 0, 0)), (0.5, (-0.25, 0.06, 0)), (1.9, (-0.25, 0.06, 0)), (2.4, (0, 0, 0))])),
                                (None, 'r', (1, 0, 0), pose([(0, 0), (0.5, 0), (1.2, 180), (1.9, 360), (2.4, 360)])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.5, 55), (1.9, 55), (2.4, 0)]))],
           desc='levanta o bastão perto do rosto e gira olhando a ponta')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 1.0), (3.0, 0)])), (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.002, 0)), (3.0, (0, 0, 0))]))],
           laco=True, desc='respiração leve parado')


def _encaixes_bastao(A):
    A.pivo = (0.06, 0.0, 0.0)
    A.encaixe('mao_cima', (0.2, 0.0, 0.0), 'mao', descricao='mão de cima (a de baixo fica no pivô, junto do pomo)')
    A.encaixe('barril', (0.72, 0.0, 0.0), 'efeito', descricao='parte grossa: onde o golpe pesa (teste de acerto)')
    A.encaixe('ponta', (TACO_L, 0.0, 0.0), 'efeito', descricao='ponta do bastão (cutucada)')


# ---------------------------------------------------------------------------- com pregos
def _bastao_pregos(A):
    rng = np.random.default_rng(31); q = A.base
    _taco(q, rng)
    n = 0
    for i, x in enumerate(np.linspace(0.6, 0.81, 6)):                    # 6 aneis de 3 a 4 pregos, girados entre si
        k = 3 if i % 2 else 4
        for j in range(k):
            a = 2 * math.pi * j / k + i * 0.7 + rng.uniform(-0.25, 0.25)
            r = _r_taco(x); fora = rng.uniform(0.022, 0.04)
            d = np.array([rng.uniform(-0.25, 0.25), math.cos(a), math.sin(a)]); d /= np.linalg.norm(d)
            p0 = np.array([x, 0, 0]) + np.array([0, math.cos(a), math.sin(a)]) * (r - 0.018)
            p1 = np.array([x, 0, 0]) + np.array([0, math.cos(a), math.sin(a)]) * r + d * fora
            if n % 5 == 3:                                               # alguns entortados de bater
                meio = (p0 + p1) / 2 + d * 0.004
                dobra = np.cross(d, [1, 0, 0]); dobra /= np.linalg.norm(dobra)
                pts = [p0, meio, meio + d * 0.006 + dobra * 0.004, meio + d * 0.008 + dobra * 0.012]
                q.add('aco_prego', _tubo3d(pts, 0.0014, 8)); p1 = pts[-1]; d = (pts[-1] - pts[-2]) / np.linalg.norm(pts[-1] - pts[-2])
            else:
                q.add('aco_prego', trimesh.creation.cylinder(radius=0.0014, segment=[p0, p1], sections=8))
            cab = trimesh.creation.cylinder(radius=0.0036, segment=[p1 - d * 0.0004, p1 + d * 0.0008], sections=14)
            q.add('aco_oxidado' if n % 3 == 0 else 'aco_prego', cab)
            n += 1
    _encaixes_bastao(A)
    _anims_bastao(A, 'um prego')


# ---------------------------------------------------------------------------- com arame farpado
def _bastao_arame(A):
    rng = np.random.default_rng(37); q = A.base
    _taco(q, rng)
    x0, x1, voltas = 0.5, 0.815, 7.5
    t = np.linspace(0, 1, 900); X = x0 + (x1 - x0) * t; ang = 2 * math.pi * voltas * t
    R = np.array([_r_taco(x) + 0.0022 for x in X])
    C = np.stack([X, R * np.cos(ang), R * np.sin(ang)], 1)
    Nr = np.stack([np.zeros_like(X), np.cos(ang), np.sin(ang)], 1)
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; B = np.cross(T, Nr)
    for s in (0, math.pi):                                               # dois fios torcidos
        tor = 2 * math.pi * 70 * t + s
        fio = C + 0.0011 * (np.cos(tor)[:, None] * Nr + np.sin(tor)[:, None] * B)
        q.add('arame_farpado', _tubo3d(fio, 0.00085, 6))
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    for sb in np.arange(0.02, L[-1] - 0.01, 0.038):                       # farpas: dois arames cruzados com 4 pontas
        i = int(np.searchsorted(L, sb)); p = C[i]; n_, b_ = Nr[i], B[i]; tt = T[i]
        for k, (u, v) in enumerate(((0.75, 0.66), (0.75, -0.66))):
            d = u * n_ + v * b_ + 0.25 * tt * (1 if k else -1); d /= np.linalg.norm(d)
            p0 = p + tt * (0.0014 if k else -0.0014)
            q.add('arame_farpado', trimesh.creation.cylinder(radius=0.0007, segment=[p0 - d * 0.0005, p0 + d * 0.0085], sections=6))
            q.add('arame_farpado', trimesh.creation.cylinder(radius=0.0007, segment=[p0 + n_ * 0.0005, p0 - d * 0.0085 + n_ * 0.006], sections=6))
            q.add('arame_farpado', trimesh.creation.cone(0.0007, 0.0025, sections=6).apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d))
                  .apply_translation(p0 + d * 0.0085))
        q.add('arame_farpado', tubo_x(0.0016, 0.0024, -0.002, 0.002, sec=8).apply_transform(trimesh.geometry.align_vectors([1, 0, 0], tt)).apply_translation(p))
    for xa, sgn in ((x0, -1), (x1, 1)):                                  # pontas amarradas: voltas apertadas e rabicho torcido
        r = _r_taco(xa) + 0.0018
        for k in range(3):
            _anel_fita(xa + sgn * (0.004 + k * 0.0032) - 0.0011, xa + sgn * (0.004 + k * 0.0032) + 0.0011, r - 0.0006, 'arame_farpado', q, (0, 0), esp=0.0016)
        a0 = 2 * math.pi * voltas if sgn > 0 else 0.0
        base = np.array([xa, r * math.cos(a0), r * math.sin(a0)]); ra = np.array([0, math.cos(a0), math.sin(a0)])
        for s in (0, math.pi):
            uu = np.linspace(0, 1, 24)
            q.add('arame_farpado', _tubo3d([base + ra * 0.016 * u + 0.001 * np.array([math.cos(8 * math.pi * u + s), 0, math.sin(8 * math.pi * u + s)]) + np.array([sgn * 0.006 * u, 0, 0])
                                             for u in uu], 0.0007, 6))
    _encaixes_bastao(A)
    _anims_bastao(A, 'o arame')


_ONDE_BASTAO = ['casas', 'garagem', 'escolinha', 'abrigo']


@arma('bastao_pregos', 'Bastão com pregos', 'armas', 'bastao', classe='corpo_a_corpo', calibre='impacto', capacidade='-', dano=52, dano_golpe_forte=85,
      alcance_m=0.95, tiros_por_s=1.2, precisao=1.0, ruido_m=4, durabilidade=1400, peso_kg=1.05, raridade='comum', valor_troca=10, duas_maos=True,
      prende_no_alvo=0.15, derruba=0.3, receita={'taco_madeira': 1, 'caixa_pregos': 1}, bancada=True, reparo={'caixa_pregos': 1}, onde=_ONDE_BASTAO,
      descricao='Taco de madeira com uns vinte pregos batidos na parte grossa, alguns entortados, e pega de fita isolante. '
                'Bate bem mais que o taco e rasga, mas às vezes prende no alvo e precisa ser arrancado. Feito na bancada com uma caixa de pregos.')
def bastao_pregos(A): _bastao_pregos(A)


@arma('bastao_arame', 'Bastão com arame farpado', 'armas', 'bastao', classe='corpo_a_corpo', calibre='impacto', capacidade='-', dano=58, dano_golpe_forte=90,
      alcance_m=0.95, tiros_por_s=1.2, precisao=1.0, ruido_m=4, durabilidade=1100, peso_kg=1.15, raridade='incomum', valor_troca=12, duas_maos=True,
      prende_no_alvo=0.1, sangramento=True, derruba=0.3, receita={'taco_madeira': 1, 'arame_farpado': 1}, bancada=True, reparo={'arame_farpado': 1},
      onde=_ONDE_BASTAO,
      descricao='Taco de madeira com arame farpado enrolado na parte grossa, pontas amarradas e torcidas, e pega de fita isolante. '
                'Rasga e faz sangrar; prende menos que o de pregos, mas o arame afrouxa e quebra antes. Feito na bancada com um rolo de arame farpado.')
def bastao_arame(A): _bastao_arame(A)
