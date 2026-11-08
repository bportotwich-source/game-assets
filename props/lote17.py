# Lote 17: defesa da base (fases 2 e 3): o que segura a horda dos 7 dias.
# Executado por gerar_props.py (usa as mesmas funcoes e materiais dos lotes anteriores).
# Campos: vida (dano que aguenta antes de cair), modulo_m (encaixa lado a lado no grid de 2 m), bloqueia ('passagem' ou 'passagem e visao'),
#         dano_zumbi (armadilhas: dano por segundo ou por pisada), prende_s (segura o zumbi parado), vao_m (pecas de porta e janela,
#         como nas barricadas do lote 5), luz_m, ruido_m, atirar_por_cima (moradores atiram por tras sem levar mordida).
CORES.update({'pneu': (14, 14, 15), 'terra': (70, 50, 32), 'galho': (80, 60, 40), 'botijao': (120, 10, 8), 'vidro_holofote': (230, 236, 240),
              'andaime': (110, 112, 112), 'concreto_bloco': (150, 148, 140), 'folha_mato': (16, 28, 7)})
METALICOS.update({'botijao': (0.3, 0.45), 'andaime': (0.85, 0.45)})
FOSCOS.update({'pneu': 0.85, 'terra': 0.95, 'folha_mato': 0.8})
TEX_PROPRIAS += [('terra', 'barro', 0.5, 512), ('galho', 'couro', 0.5, 512), ('concreto_bloco', 'barro', 0.5, 512)]
EMISSIVOS.update({'vidro_holofote': [1.0, 0.95, 0.8]})


def _estaca(p, a, b, r=0.04, ponta=0.18, mat='madeira_lenha'):
    """Tronco apontado de a para b (ponta em b), com o topo da ponta mais claro (madeira cortada)."""
    a, b = np.array(a, float), np.array(b, float); d = (b - a) / np.linalg.norm(b - a); c = b - d * ponta
    p.add(mat, trimesh.creation.cylinder(radius=r, segment=[a, c], sections=10))
    p.add('madeira_crua', trimesh.creation.cone(radius=r, height=ponta, sections=10, transform=_alinha(c, d)))


def _alinha(origem, d):
    z = np.array([0, 0, 1.0]); d = d / np.linalg.norm(d); ax = np.cross(z, d); s = np.linalg.norm(ax)
    T = np.eye(4) if s < 1e-8 else trimesh.transformations.rotation_matrix(math.atan2(s, np.dot(z, d)), ax / s)
    T[:3, 3] = origem; return T


def _pneu(p, c, R=0.32, r=0.1, deitado=True, terra=True):
    m = trimesh.creation.torus(R, r, major_sections=32, minor_sections=12)
    m.vertices[:, 2] *= 0.75                                                                     # pneu achatado (banda larga)
    if deitado: m.apply_transform(_rot(math.pi / 2, [1, 0, 0]))                                 # torus nasce com eixo em z
    m.apply_translation(c); p.add('pneu', m)
    for k in range(24):                                                                           # sulcos da banda
        a = k * 2 * math.pi / 24; rr = R + r * 0.86
        if deitado: p.box('pneu', c[0] + rr * math.cos(a) - 0.008, c[0] + rr * math.cos(a) + 0.008, c[1] - r * 0.55, c[1] + r * 0.55, c[2] + rr * math.sin(a) - 0.008, c[2] + rr * math.sin(a) + 0.008)
    if terra and deitado: torno(p, 'terra', [(R - r * 0.3, c[1] + r * 0.5), (R * 0.5, c[1] + r * 0.65), (0.0, c[1] + r * 0.7)], 24, 'y', (c[0], 0, c[2]))


# ---------------------------------------------------------------------------- BARREIRAS
@item('cavalo_frisa', 'Cavalo de frisa de estacas', 'mobilias', 'defesa', comodos=['abrigo', 'rua'], constroi={'lenha': 6, 'arame_liso': 1},
      ferramenta='machado', fase=2, vida=300, modulo_m=2, bloqueia='passagem', dano_zumbi=4, empurrar=True,
      estacao='barreira (zumbi que encosta se fere e empaca; dá para arrastar e fechar a rua)')
def cavalo_frisa(M):
    p = M.base; L = 1.9
    p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.07, segment=[(-L / 2, 0.45, 0), (L / 2, 0.45, 0)], sections=12))
    for s in (-1, 1): torno(p, 'madeira_crua', [(0.065, 0.0), (0.065, 0.004)], 12, 'x', (s * L / 2 - (0.004 if s > 0 else 0), 0.45, 0))
    for i, x in enumerate(np.linspace(-L / 2 + 0.15, L / 2 - 0.15, 5)):                               # pares de estacas cruzadas
        a = math.pi / 4 + (0.08 if i % 2 else -0.06)
        for s in (-1, 1):
            d = np.array([0, math.sin(a), s * math.cos(a)]); _estaca(p, np.array([x, 0.45, 0]) - d * 0.62, np.array([x, 0.45, 0]) + d * 0.62, 0.035, 0.16)
        for k in range(6):                                                                               # amarracao de arame
            t = k / 6 * 2 * math.pi; p.seg('galvanizado', (x - 0.03, 0.45 + 0.07 * math.sin(t), 0.07 * math.cos(t)), (x + 0.03, 0.45 + 0.07 * math.sin(t + 1), 0.07 * math.cos(t + 1)), 0.003, 0.003)


@item('cerca_arame', 'Cerca de arame farpado', 'mobilias', 'defesa', comodos=['abrigo', 'fazenda', 'rua'], constroi={'arame_farpado': 1, 'lenha': 3},
      ferramenta='martelo', fase=2, vida=150, modulo_m=2, bloqueia='passagem', dano_zumbi=2, prende_s=3,
      estacao='cerca (segura zumbis comuns 3 s e fere; não para o pesado)')
def cerca_arame(M):
    p = M.base; rng = np.random.default_rng(4)
    for x in (-1.0, 0.0, 1.0):                                                                           # moiroes (as pontas casam com o modulo vizinho)
        r = 0.05 if x != 0 else 0.045
        torno(p, 'madeira_lenha', [(r, 0.0), (r * 0.95, 1.2), (r * 0.7, 1.24)], 12, 'y', (x + rng.uniform(-0.02, 0.02) * (x == 0), 0, 0))
    for k, y in enumerate((0.25, 0.55, 0.85, 1.12)):
        sag = 0.03 + 0.01 * k
        cam = [(x, y - sag * (1 - (2 * (x % 1.0) - 1) ** 2) * (abs(x) < 1), 0.055) for x in np.linspace(-1.0, 1.0, 25)]
        for a, b in zip(cam[:-1], cam[1:]):
            p.seg('ferrugem', a, b, 0.0035, 0.0035)
        for x, yy, z in cam[1:-1:2]:                                                                     # farpas
            for dd in ((0.012, 0.012), (-0.012, 0.012)): p.seg('aco', (x, yy, z), (x + dd[0], yy + dd[1] * 0.8, z + 0.008), 0.0016, 0.0016)
        for x in (-1.0, 0.0, 1.0): torno(p, 'aco', [(0.004, 0.0), (0.004, 0.02)], 6, 'z', (x, y, 0.035))   # grampos
    p.seg('madeira_lenha', (-0.95, 0.1, 0.0), (-0.05, 1.05, 0.0), 0.05, 0.05)                           # escora em diagonal


@item('parede_sacos', 'Parede de sacos de areia', 'mobilias', 'defesa', comodos=['abrigo', 'quartel', 'rua'], constroi={'saco_areia': 12},
      ferramenta='pa', fase=2, vida=900, modulo_m=2, bloqueia='passagem', atirar_por_cima=True,
      estacao='trincheira (1,1 m de altura; moradores atiram por cima sem levar mordida; à prova de bala)')
def parede_sacos(M):
    p = M.base; rng = np.random.default_rng(12)
    for k in range(5):                                                                                   # 5 fiadas, juntas desencontradas
        n = 4 if k % 2 == 0 else 3; w = 2.0 / n
        for i in range(n + (k % 2)):
            x = -1.0 + w / 2 + i * w - (w / 2 if k % 2 else 0)
            if abs(x) > 1.0: continue
            s = P(); fofo(s, 'lona', 0.0, 0.0, 0.0, w / 2 - 0.01, 0.11, 0.2, 0.35, 0.2, (10, 18)); _amassar(s, 'lona', 0.008, 18.0, 31 * k + i, sub=0)
            fofo(s, 'lona', w / 2 - 0.02, -0.01, 0.0, 0.03, 0.05, 0.12, 0.5, 0.4, (6, 8))
            ang = rng.uniform(-0.05, 0.05) + (math.pi if (i + k) % 2 else 0)
            p.merge(s, trimesh.transformations.translation_matrix([max(-1 + w / 2 - 0.01, min(1 - w / 2 + 0.01, x)), 0.11 + k * 0.2, 0.08 * (k == 4) * 0]) @ _rot(ang, [0, 1, 0]))


@item('barreira_pneus', 'Barreira de pneus com terra', 'mobilias', 'defesa', comodos=['abrigo', 'posto', 'ferrovelho', 'rua'], constroi={'terra': 6, 'pilha_pneus': 1},
      ferramenta='pa', fase=2, vida=700, modulo_m=2, bloqueia='passagem', estacao='barreira (pneus velhos cheios de terra; carro não passa)')
def barreira_pneus(M):
    p = M.base
    for k in range(3):
        for i in range(3 if k < 2 else 2):
            x = -0.66 + i * 0.66 + (0.33 if k == 2 else 0)
            _pneu(p, (x, 0.072 + k * 0.143, 0.0 + (0.02 if (i + k) % 2 else -0.02)), 0.24, 0.095, True, k == 2)
    fofo(p, 'terra', 0.0, 0.03, 0.4, 0.8, 0.04, 0.12, 0.6, 0.6, (8, 16))


@item('tabua_pregos', 'Tábua de pregos', 'mobilias', 'defesa', comodos=['abrigo', 'rua'], constroi={'tabua': 1, 'caixa_pregos': 1},
      ferramenta='martelo', fase=1, vida=60, dano_zumbi=25, prende_s=2, colisao='nenhuma',
      estacao='armadilha (escondida no mato ou atrás da porta: fere e trava o zumbi que pisa; o jogador também se fere)')
def tabua_pregos(M):
    p = M.base; L = 1.0
    p.cham('madeira_crua', -L / 2, L / 2, 0.0, 0.025, -0.1, 0.1, 0.003)
    rng = np.random.default_rng(8)
    for x in np.linspace(-L / 2 + 0.05, L / 2 - 0.05, 12):
        for z in (-0.06, 0.0, 0.06):
            xx, zz = x + rng.uniform(-0.012, 0.012), z + rng.uniform(-0.01, 0.01)
            tilt = rng.uniform(-0.25, 0.25)
            a = np.array([xx, 0.02, zz]); b = a + np.array([math.sin(tilt) * 0.06, 0.06, 0.0])
            p.add('aco', trimesh.creation.cylinder(radius=0.0018, segment=[a, b], sections=6))
            p.add('ferrugem' if (int(x * 37) + int(z * 50)) % 3 == 0 else 'aco', trimesh.creation.cone(radius=0.0018, height=0.008, sections=6, transform=_alinha(b, b - a)))
    for i in range(3): fofo(p, 'galho', -0.3 + i * 0.3, 0.04, 0.12 + i * 0.03, 0.18, 0.012, 0.03, 0.5, 0.5, (6, 10))     # galhos e folhas tapando
    for i in range(8): fofo(p, 'folha_mato', rng.uniform(-0.45, 0.45), 0.075, rng.uniform(-0.08, 0.1), 0.04, 0.005, 0.025, 0.6, 0.6, (5, 6))


@item('fosso_estacas', 'Fosso com estacas', 'mobilias', 'defesa', comodos=['abrigo', 'rua', 'fazenda'], constroi={'lenha': 4},
      ferramenta='pa', fase=3, vida=400, modulo_m=2, dano_zumbi=60, prende_s=999, colisao='buraco',
      estacao='armadilha (cavado na frente do muro; zumbi que cai fica preso até alguém acabar com ele)')
def fosso_estacas(M):
    p = M.base; X, Z, D = 0.95, 0.6, 0.9; rng = np.random.default_rng(5)
    for xs in (-1, 1):                                                                                  # paredes do buraco e borda de terra
        p.box('terra', xs * X - 0.05 * (xs > 0), xs * X + 0.05 * (xs < 0), -D, 0.0, -Z, Z)
        fofo(p, 'terra', xs * (X + 0.15), 0.03, 0.0, 0.18, 0.07, Z + 0.1, 0.6, 0.6, (8, 14))
    for zs in (-1, 1): p.box('terra', -X, X, -D, 0.0, zs * Z - 0.05 * (zs > 0), zs * Z + 0.05 * (zs < 0))
    p.box('terra', -X, X, -D - 0.05, -D, -Z, Z)
    for i in range(14):                                                                                  # estacas no fundo
        x, z = rng.uniform(-X + 0.15, X - 0.15), rng.uniform(-Z + 0.15, Z - 0.15)
        _estaca(p, (x, -D, z), (x + rng.uniform(-0.1, 0.1), -D + rng.uniform(0.5, 0.7), z + rng.uniform(-0.1, 0.1)), 0.03, 0.14)
    for i in range(6):                                                                                   # galhos cobrindo parte do buraco
        z = rng.uniform(-Z, Z); p.seg('galho', (-X - 0.1, 0.01, z), (X * rng.uniform(-0.2, 0.9), 0.02, z + rng.uniform(-0.2, 0.2)), 0.03, 0.03)
    for i in range(16): fofo(p, 'folha_mato', rng.uniform(-X, X * 0.3), 0.035, rng.uniform(-Z, Z), 0.07, 0.008, 0.05, 0.6, 0.6, (5, 6))


# ---------------------------------------------------------------------------- PORTAS E JANELAS
@item('porta_reforcada', 'Porta reforçada com chapa', 'mobilias', 'defesa', montagem='wall', comodos=['abrigo', 'casas', 'quartel'],
      vao='porta 0,9 × 2,1 m (troca a porta do kit)', vao_m=[0.9, 2.1, 0.0], constroi={'chapa_metal': 2, 'tabua': 3, 'pote_parafusos': 1, 'corrente_cadeado': 1},
      ferramenta='chave_inglesa', estacao_obra='bancada_carpintaria', fase=2, vida=600, trancado=True, tranca='tranca de barra por dentro',
      estacao='porta (abre e fecha; aguenta 3× uma barricada de tábuas)')
def porta_reforcada(M):
    p = M.base; W, H = 0.9, 2.1
    for xs in (-1, 1): p.cham('madeira_escura', xs * (W / 2 + 0.04) - 0.04, xs * (W / 2 + 0.04) + 0.04, 0.0, H + 0.08, -0.02, 0.06, 0.004)   # batente reforcado
    p.cham('madeira_escura', -W / 2 - 0.08, W / 2 + 0.08, H, H + 0.08, -0.02, 0.06, 0.004)
    for xs in (-1, 1):                                                                                    # suportes da tranca (por dentro)
        p.cham('aco', xs * (W / 2 + 0.02) - 0.03, xs * (W / 2 + 0.02) + 0.03, 1.0, 1.12, -0.07, -0.02, 0.004)
    q = M.parte('porta', (-W / 2, 0, 0.0), 'porta', eixo='y', abre_graus=100)
    q.cham('madeira', -W / 2 + 0.005, W / 2 - 0.005, 0.005, H - 0.005, -0.015, 0.03, 0.004)
    L, Wd, a = H - 0.06, W - 0.06, 0.008; xs_ = np.linspace(-Wd / 2, Wd / 2, 41)
    top = [(x, a + a * math.cos(x * 2 * math.pi / 0.076)) for x in xs_]
    m = trimesh.creation.extrude_polygon(Polygon(top + [(x, y - 0.0015) for x, y in top[::-1]]).buffer(0), L)
    m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2] + 0.03, m.vertices[:, 1] + 0.03], 1)
    if m.volume < 0: m.invert()
    q.add('galvanizado', m)
    for y in (0.12, 1.05, H - 0.12):                                                                      # cantoneiras parafusadas
        q.cham('aco_pintado', -W / 2 + 0.02, W / 2 - 0.02, y - 0.03, y + 0.03, 0.045, 0.052, 0.002)
        for x in np.linspace(-W / 2 + 0.06, W / 2 - 0.06, 6): torno(q, 'aco', [(0.008, 0.0), (0.007, 0.004)], 6, 'z', (x, y, 0.052))
    q.seg('aco_pintado', (-W / 2 + 0.04, 0.15, 0.054), (W / 2 - 0.04, 1.0, 0.054), 0.05, 0.006)
    for y in (0.35, 1.75):                                                                                # dobradicas grandes
        q.cham('aco', -W / 2 - 0.01, -W / 2 + 0.18, y - 0.04, y + 0.04, 0.03, 0.036, 0.002)
    varrer(q, 'aco_polido', circ(0.01, 10), [(W / 2 - 0.1, 0.9, 0.055), (W / 2 - 0.1, 0.9, 0.1), (W / 2 - 0.1, 1.15, 0.1), (W / 2 - 0.1, 1.15, 0.055)])   # puxador
    q.cham('aco', W / 2 - 0.2, W / 2 - 0.08, 1.33, 1.37, 0.05, 0.058, 0.002)                                # visor de correr
    q.box('vidro_escuro', W / 2 - 0.19, W / 2 - 0.09, 1.38, 1.42, 0.05, 0.051)
    for xs in (-1, 1): q.cham('aco', xs * 0.15 - 0.03, xs * 0.15 + 0.03, 1.02, 1.1, -0.04, -0.015, 0.003)    # suportes da barra na folha
    p.cham('madeira_escura', -W / 2 - 0.05, W / 2 + 0.05, 1.02, 1.1, -0.1, -0.045, 0.006)   # barra de tranca


@item('grade_janela', 'Grade de janela de vergalhão', 'mobilias', 'defesa', montagem='wall', altura_sugerida_m=0.78, comodos=['abrigo', 'casas', 'galeria'],
      vao='janela 0,9 × 1,45 m', vao_m=[0.9, 1.45, 0.07], constroi={'cano_metal': 3, 'sucata_metal': 4, 'pote_parafusos': 1},
      ferramenta='chave_inglesa', estacao_obra='forja_tambor', fase=2, vida=500, bloqueia='passagem',
      estacao='grade (deixa ver e atirar pela janela; zumbi enfia o braço mas não passa)')
def grade_janela(M):
    p = M.base; W, H = 1.05, 1.56
    p.cham('ferrugem', -W / 2, W / 2, 0.0, 0.04, 0.0, 0.03, 0.003); p.cham('ferrugem', -W / 2, W / 2, H - 0.04, H, 0.0, 0.03, 0.003)
    for xs in (-1, 1): p.cham('ferrugem', xs * W / 2 - 0.04 * (xs > 0), xs * W / 2 + 0.04 * (xs < 0), 0.0, H, 0.0, 0.03, 0.003)
    for x in np.linspace(-W / 2 + 0.11, W / 2 - 0.11, 6):
        p.add('ferrugem', trimesh.creation.cylinder(radius=0.009, segment=[(x, 0.04, 0.015), (x, H - 0.04, 0.015)], sections=10))
        for y in np.arange(0.1, H - 0.05, 0.06): anel(p, 'ferrugem', 0.0088, 0.0098, y, y + 0.004, 10, 'y', (x, 0, 0.015))   # nervura do vergalhao
    for y in (0.52, 1.04): p.cham('aco_pintado', -W / 2 + 0.04, W / 2 - 0.04, y - 0.018, y + 0.018, 0.02, 0.028, 0.002)
    for (x, y) in ((-W / 2 + 0.02, 0.2), (W / 2 - 0.02, 0.2), (-W / 2 + 0.02, H - 0.2), (W / 2 - 0.02, H - 0.2)):
        torno(p, 'aco', [(0.012, 0.0), (0.012, 0.004), (0.007, 0.008)], 6, 'z', (x, y, 0.03))
    for k in range(5):                                                                                     # pontos de solda
        x = -W / 2 + 0.11 + k * 0.166; fofo(p, 'aco', x, 0.52, 0.03, 0.014, 0.022, 0.008, 0.6, 0.6, (6, 8))


@item('seteira', 'Chapa de seteira para janela', 'mobilias', 'defesa', montagem='wall', altura_sugerida_m=0.78, comodos=['abrigo', 'quartel'],
      vao='janela 0,9 × 1,45 m', vao_m=[0.9, 1.45, 0.07], constroi={'chapa_metal': 2, 'tabua': 2, 'pote_parafusos': 1}, ferramenta='chave_inglesa',
      fase=2, vida=450, bloqueia='passagem e visao', atirar_por_cima=False,
      estacao='seteira (fecha a janela e deixa uma fenda para atirar; quem está dentro não é visto de longe)')
def seteira(M):
    p = M.base; W, H = 1.05, 1.56
    for xs in (-1, 1): p.cham('madeira_escura', xs * 0.45 - 0.05, xs * 0.45 + 0.05, -0.04, H + 0.04, -0.005, 0.025, 0.003)
    L, a = W - 0.04, 0.009
    for (y0, y1) in ((0.02, 0.62), (0.76, H - 0.02)):
        xs_ = np.linspace(-L / 2, L / 2, 41); top = [(x, a + a * math.cos(x * 2 * math.pi / 0.076)) for x in xs_]
        m = trimesh.creation.extrude_polygon(Polygon(top + [(x, y - 0.0015) for x, y in top[::-1]]).buffer(0), y1 - y0)
        m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2] + y0, m.vertices[:, 1] + 0.025], 1)
        if m.volume < 0: m.invert()
        p.add('chapa_pintada', m)
    for y in (0.62, 0.76):                                                                                  # moldura da fenda com cantoneira
        p.cham('aco_pintado', -L / 2, L / 2, y - 0.012 * (y > 0.7), y + 0.012 * (y < 0.7), 0.025, 0.06, 0.002)
    q = M.parte('tampa_fenda', (0.0, 0.76, 0.06), 'tampa', eixo='x', abre_graus=-80)                          # tampa basculante da fenda
    q.cham('aco_pintado', -0.3, 0.3, 0.62, 0.76, 0.06, 0.066, 0.002); q.cham('aco_polido', -0.03, 0.03, 0.63, 0.66, 0.066, 0.09, 0.004)
    for x in np.linspace(-L / 2 + 0.05, L / 2 - 0.05, 7):
        for y in (0.1, 0.5, 0.9, 1.4): torno(p, 'aco', [(0.008, 0.0), (0.007, 0.004)], 6, 'z', (x, y, 0.034))
    img = Image.new('RGB', (512, 160), (128, 70, 40)); d = ImageDraw.Draw(img); texto_c(d, (256, 80), 'VIVOS AQUI', 72, (236, 230, 220)); mat_imagem('picha_seteira', img, 0.9)
    p.box('picha_seteira', -0.4, 0.4, 1.0, 1.25, 0.0355, 0.036); p.uv['picha_seteira'] = lambda v, n: np.stack([(v[:, 0] + 0.4) / 0.8, (v[:, 1] - 1.0) / 0.25], 1)


# ---------------------------------------------------------------------------- VIGIA, LUZ E ALARME
@item('holofote', 'Holofote em poste com bateria', 'mobilias', 'defesa', comodos=['abrigo', 'rua', 'quartel'],
      constroi={'cano_metal': 2, 'fio_eletrico': 2, 'bateria_carro': 1, 'placa_circuito': 1, 'lanterna': 1}, ferramenta='chave_inglesa',
      estacao_obra='bancada_eletronica', fase=3, luz_m=25, usa='energia', vida=120,
      estacao='holofote (ilumina 25 m no muro: moradores acertam mais de noite, mas a luz atrai zumbis de longe)')
def holofote(M):
    p = M.base; H = 2.6
    for k in range(3):                                                                                     # tripe de cano
        a = k * 2 * math.pi / 3; p.add('ferrugem', trimesh.creation.cylinder(radius=0.02, segment=[(0.5 * math.cos(a), 0.0, 0.5 * math.sin(a)), (0, 1.2, 0)], sections=10))
    anel(p, 'aco', 0.022, 0.028, 0.0, H, 14)
    p.cham('aco_pintado', -0.03, 0.03, H, H + 0.06, -0.03, 0.03, 0.004)
    q = M.parte('cabeca', (0.0, H + 0.12, 0.0), 'porta', eixo='y', abre_graus=360, gira_livre=True)
    for s in (-1, 1): q.cham('aco_pintado', s * 0.17 - 0.012, s * 0.17 + 0.012, H + 0.03, H + 0.18, -0.02, 0.02, 0.003)
    q.cham('aco_pintado', -0.18, 0.18, H + 0.02, H + 0.05, -0.02, 0.02, 0.004)
    torno(q, 'aco_pintado', [(0.13, -0.12), (0.15, -0.02), (0.15, 0.1), (0.155, 0.11)], 28, 'z', (0.0, H + 0.12, 0.0))
    torno(q, 'vidro_holofote', [(0.14, 0.098), (0.14, 0.104)], 28, 'z', (0.0, H + 0.12, 0.0))
    for k in range(4): q.cham('aco_pintado', -0.15, 0.15, H + 0.12 - 0.09 + k * 0.06, H + 0.12 - 0.084 + k * 0.06, 0.104, 0.11, 0.001)  # grade de protecao
    for k in range(10):
        a = k * 2 * math.pi / 10; q.cham('aco_pintado', 0.13 * math.cos(a) - 0.003, 0.13 * math.cos(a) + 0.003, H + 0.12 + 0.13 * math.sin(a) - 0.003, H + 0.12 + 0.13 * math.sin(a) + 0.003, -0.11, -0.04, 0.001)
    q2 = P(); q2.cham('plastico_preto', -0.13, 0.13, 0.0, 0.18, -0.09, 0.09, 0.008); q2.cham('plastico_cinza', -0.13, 0.13, 0.18, 0.2, -0.09, 0.09, 0.004)
    p.merge(q2, trimesh.transformations.translation_matrix([0.45, 0.0, 0.25]))                               # bateria no pe
    varrer(p, 'fio_vermelho', circ(0.004, 6), [(0.38, 0.22, 0.27), (0.15, 0.3, 0.1), (0.03, 0.6, 0.0), (0.03, H, 0.0)])
    p.cham('plastico_preto', 0.0, 0.08, 1.1, 1.22, 0.02, 0.07, 0.006)                                       # interruptor


@item('sino_alarme', 'Sino de alarme de botijão', 'mobilias', 'defesa', comodos=['abrigo', 'rua'], constroi={'tabua': 3, 'corrente_cadeado': 1, 'cano_metal': 1},
      ferramenta='serrote', fase=2, ruido_m=120,
      estacao='alarme (quem vê a horda bate o sino: todos os moradores correm para os postos; a horda também ouve)')
def sino_alarme(M):
    p = M.base; H = 2.2; X = 0.55
    for xs in (-1, 1):                                                                                      # portico de tabua
        p.cham('madeira_escura', xs * X - 0.045, xs * X + 0.045, 0.0, H, -0.045, 0.045, 0.004)
        p.seg('madeira_escura', (xs * X, 0.0, -0.4), (xs * X, 1.2, -0.03), 0.06, 0.04); p.seg('madeira_escura', (xs * X, 0.0, 0.4), (xs * X, 1.2, 0.03), 0.06, 0.04)
    p.cham('madeira_escura', -X - 0.1, X + 0.1, H, H + 0.09, -0.05, 0.05, 0.004)
    for x in (-0.03, 0.03): p.seg('galvanizado', (x, H, 0.0), (0.0, H - 0.25, 0.0), 0.008, 0.008)              # corrente curta
    q = P()                                                                                                    # botijao cortado (vira sino)
    torno(q, 'botijao', [(0.12, 0.0), (0.155, 0.05), (0.155, 0.3), (0.14, 0.34), (0.08, 0.38), (0.04, 0.39)], 32)
    torno(q, 'tambor_preto', [(0.146, 0.004), (0.146, 0.008)], 32)
    anel(q, 'aco', 0.04, 0.05, 0.38, 0.42, 14)
    for y in (0.08, 0.27): anel(q, 'botijao', 0.155, 0.158, y, y + 0.012, 32)
    anel(q, 'ferrugem', 0.1555, 0.157, 0.12, 0.16, 32)
    p.merge(q, trimesh.transformations.translation_matrix([0, H - 0.67, 0]))
    p.add('aco', trimesh.creation.cylinder(radius=0.005, segment=[(0, H - 0.3, 0), (0, H - 0.6, 0)], sections=8)); p.sphere('aco', 0.03, 0, H - 0.6, 0, sub=2)   # badalo
    _torcido(p, 'corda', [(0.0, H - 0.62, 0.0), (0.05, H - 0.8, 0.05), (0.1, 1.0, 0.1), (0.12, 0.9, 0.12)], 0.006)
    q = P(); cyl_eixo(q, 'madeira', 0.014, 0.0, 0.45, 'x', (0, 0, 0), 10); q.cham('aco', 0.42, 0.48, -0.03, 0.03, -0.022, 0.022, 0.005)   # marreta pendurada
    p.merge(q, trimesh.transformations.translation_matrix([X + 0.05, 1.0, 0.06]) @ _rot(-math.pi / 2, [0, 0, 1]))


@item('plataforma_tiro', 'Plataforma de tiro de andaime', 'mobilias', 'defesa', comodos=['abrigo', 'quartel', 'rua'],
      constroi={'cano_metal': 6, 'tabua': 6, 'pote_parafusos': 1, 'saco_areia': 4}, ferramenta='chave_inglesa', fase=3, vida=500, modulo_m=2,
      vagas=2, atirar_por_cima=True, estacao='posto de tiro (2 moradores atiram por cima do muro de 2 m; sobe pela escada)')
def plataforma_tiro(M):
    p = M.base; X, Z, H = 1.0, 0.5, 1.5
    for xs in (-1, 1):
        for zs in (-1, 1):
            x, z = xs * (X - 0.03), zs * (Z - 0.03); anel(p, 'andaime', 0.019, 0.024, 0.0, H + 1.0, 14, 'y', (x, 0, z))
            p.cham('andaime', x - 0.06, x + 0.06, 0.0, 0.008, z - 0.06, z + 0.06, 0.002)
            for y in (0.3, H - 0.05, H + 0.95): p.cham('aco', x - 0.035, x + 0.035, y - 0.03, y + 0.03, z - 0.035, z + 0.035, 0.006)   # bracadeiras
    for y in (0.3, H - 0.05, H + 0.95):
        for zs in (-1, 1): anel(p, 'andaime', 0.019, 0.024, -X + 0.03, X - 0.03, 14, 'x', (0, y, zs * (Z - 0.03)))
        for xs in (-1, 1): anel(p, 'andaime', 0.019, 0.024, -Z + 0.03, Z - 0.03, 14, 'z', (xs * (X - 0.03), y, 0))
    for zs in (-1, 1):                                                                                      # diagonais
        p.add('andaime', trimesh.creation.cylinder(radius=0.022, segment=[(-X + 0.03, 0.3, zs * (Z - 0.03)), (X - 0.03, H - 0.05, zs * (Z - 0.03))], sections=12))
    for z in np.linspace(-Z + 0.1, Z - 0.1, 4): _tab_h(p, -X, X, H, H + 0.03, z - 0.11, z + 0.11)
    for k in range(2):                                                                                       # parapeito de sacos na frente
        for i in range(4):
            s = P(); fofo(s, 'lona', 0, 0, 0, 0.24, 0.09, 0.16, 0.35, 0.2, (10, 16)); _amassar(s, 'lona', 0.006, 20.0, 7 * k + i, sub=0)
            p.merge(s, trimesh.transformations.translation_matrix([-0.75 + i * 0.5 + 0.25 * (k % 2) * (i < 3), H + 0.12 + k * 0.17, Z - 0.17]))
    for y in np.arange(0.25, H, 0.3): anel(p, 'andaime', 0.016, 0.02, -0.2, 0.2, 12, 'z', (X + 0.04, y, 0))   # degraus
    for zs in (-1, 1): anel(p, 'andaime', 0.019, 0.024, 0.0, H + 0.9, 14, 'y', (X + 0.04, 0, zs * 0.2))
