# Lote 8: abrigo vivo e construcoes da base. Executado por gerar_props.py (mesmas funcoes e materiais).
CORES.update({'lousa': (22, 34, 28), 'giz': (236, 236, 230), 'folha_verde': (30, 80, 24), 'tomate': (130, 14, 6), 'terra': (54, 38, 26),
              'lona_azul': (14, 40, 90), 'chapa_pintada': (60, 80, 70), 'lampada_cordao': (255, 214, 140)})
METALICOS.update({'chapa_pintada': (0.4, 0.55)})
FOSCOS.update({'lousa': 0.85, 'folha_verde': 0.6, 'tomate': 0.35, 'lona_azul': 0.6})
TEX_PROPRIAS += [('terra', 'papelao', 0.5, 512), ('lona_azul', 'tecido', 0.5, 768)]
EMISSIVOS.update({'lampada_cordao': [1.0, 0.75, 0.4]})
BASE = dict(comodos=['abrigo', 'quartel', 'igreja', 'casas'], ambiente=True)


@item('lampiao', 'Lampião a querosene', 'mobilias', 'abrigo', comodos=['abrigo', 'casas', 'fazenda', 'igreja'], ambiente=True, colisao='nenhuma',
      portatil=True, peso_kg=1.2, luz_m=6, usa='combustivel', estacao='luz da base (gasta 1 combustível a cada 2 dias)')
def lampiao(M):
    p = M.base
    torno(p, 'tinta_vermelha', [(0.07, 0.0), (0.075, 0.01), (0.075, 0.05), (0.06, 0.07), (0.035, 0.08)], 32)
    for k in range(4): a = k / 4 * 2 * math.pi + 0.4; p.seg('tinta_vermelha', (0.04 * math.cos(a), 0.08, 0.04 * math.sin(a)), (0.05 * math.cos(a), 0.23, 0.05 * math.sin(a)), 0.006)
    torno(p, 'vidro_prateleira', [(0.03, 0.08), (0.055, 0.13), (0.055, 0.17), (0.03, 0.23)], 28, fechar=False)
    torno(p, 'lamp_glass', [(0.0, 0.1), (0.008, 0.11), (0.004, 0.13), (0.0, 0.135)], 10)
    torno(p, 'tinta_vermelha', [(0.04, 0.23), (0.06, 0.245), (0.03, 0.27), (0.01, 0.28)], 28)
    varrer(p, 'aco', circ(0.002, 6), [(-0.075, 0.03, 0)] + [(0.09 * math.cos(a), 0.18 + 0.15 * math.sin(a), 0) for a in np.linspace(math.pi, 0, 14)] + [(0.075, 0.03, 0)])
    cyl_eixo(p, 'aco', 0.01, 0.075, 0.095, 'x', (0, 0.035, 0), 10)


@item('cordao_luzes', 'Cordão de luzes', 'mobilias', 'abrigo', montagem='wall', altura_sugerida_m=2.2, comodos=['abrigo', 'igreja', 'quartel', 'concha'],
      ambiente=True, colisao='nenhuma', usa='energia', luz_m=4, efeito='moral +5 à noite; a luz atrai zumbis de longe')
def cordao_luzes(M):
    p = M.base; X = 1.5
    pts = [(x, -0.25 * (1 - (x / X) ** 2), 0.08) for x in np.linspace(-X, X, 31)]
    varrer(p, 'plastico_preto', circ(0.003, 6), pts)
    for xs in (-1, 1): cyl_eixo(p, 'aco', 0.003, 0.0, 0.085, 'z', (xs * X, 0, 0), 8)
    for k, (x, y, z) in enumerate(pts[1:-1:2]):
        torno(p, 'plastico_preto', [(0.008, -0.01), (0.008, -0.025)], 10, 'y', (x, y, z))
        torno(p, 'lampada_cordao', [(0.008, -0.025), (0.016, -0.04), (0.015, -0.055), (0.0, -0.065)], 14, 'y', (x, y, z))


@item('mapa_alfinetes', 'Mapa da cidade com alfinetes', 'mobilias', 'abrigo', montagem='wall', altura_sugerida_m=1.2,
      comodos=['abrigo', 'quartel', 'delegacia', 'correios'], ambiente=True, colisao='nenhuma', interacao='abre o mapa do jogo (prédios saqueados ficam marcados)')
def mapa_alfinetes(M):
    p = M.base; W, H = 1.2, 0.85; rng = np.random.default_rng(9)
    img = Image.new('RGB', (1200, 850), (232, 226, 200)); d = ImageDraw.Draw(img)
    d.polygon([(0, 600), (300, 560), (520, 640), (900, 600), (1200, 650), (1200, 720), (900, 670), (520, 710), (300, 630), (0, 670)], fill=(150, 196, 220))
    for i in range(9): y = 40 + i * 95; d.line([(0, y), (1200, y + rng.integers(-30, 30))], fill=(255, 255, 250), width=12 if i % 3 else 22)
    for i in range(12): x = 30 + i * 100; d.line([(x, 0), (x + rng.integers(-40, 40), 850)], fill=(255, 255, 250), width=12 if i % 2 else 20)
    for _ in range(80): x, y = rng.integers(10, 1180), rng.integers(10, 830); d.rectangle([x, y, x + 28, y + 20], fill=(210, 192, 166))
    for _ in range(9): x, y = rng.integers(60, 1140), rng.integers(60, 800); d.line([(x - 22, y - 22), (x + 22, y + 22)], fill=(30, 30, 30), width=7); d.line([(x - 22, y + 22), (x + 22, y - 22)], fill=(30, 30, 30), width=7)
    d.ellipse([500, 300, 600, 400], outline=(200, 20, 20), width=8); texto_c(d, (550, 280), 'BASE', 36, (200, 20, 20))
    mat_imagem('mapa_parede', img, 0.85)
    p.cham('cortica', -W / 2 - 0.03, W / 2 + 0.03, -0.03, H + 0.03, 0.0, 0.02, 0.004)
    p.box('mapa_parede', -W / 2, W / 2, 0, H, 0.02, 0.0215); p.uv['mapa_parede'] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)
    for k in range(14):
        x, y = rng.uniform(-W / 2 + 0.05, W / 2 - 0.05), rng.uniform(0.05, H - 0.05); c = ['plastico_vermelho', 'plastico_azul', 'tinta_amarela', 'tinta_verde'][k % 4]
        cyl_eixo(p, 'aco_polido', 0.0012, 0.02, 0.035, 'z', (x, y, 0), 6); p.sphere(c, 0.008, x, y, 0.04, 1)
    for a, b in ((0, 3), (3, 7), (7, 2)):
        pass
    varrer(p, 'corda', circ(0.0012, 5), [(-0.3, 0.6, 0.03), (0.0, 0.42, 0.03), (0.25, 0.25, 0.03), (0.4, 0.55, 0.03)])


@item('quadro_tarefas', 'Quadro de tarefas da comunidade', 'mobilias', 'abrigo', montagem='wall', altura_sugerida_m=1.0,
      comodos=['abrigo', 'quartel', 'igreja'], ambiente=True, colisao='nenhuma', interacao='abre a tela de tarefas dos sobreviventes')
def quadro_tarefas(M):
    p = M.base; W, H = 1.1, 0.75
    img = Image.new('RGB', (1100, 750), (30, 46, 38)); d = ImageDraw.Draw(img); g = (236, 236, 226)
    texto_c(d, (550, 60), 'TAREFAS · DIA 34', 54, g, False)
    d.line([(60, 110), (1040, 110)], fill=g, width=4); d.line([(400, 130), (400, 700)], fill=g, width=3)
    for i, (nm, tf) in enumerate((('MARTA', 'horta'), ('JOÃO', 'vigia (noite)'), ('LÍVIA', 'cozinha'), ('RAUL', 'buscar água'), ('VOCÊ', 'saque: posto'))):
        y = 170 + i * 105; d.text((80, y), nm, font=fonte(44, False), fill=g); d.text((440, y), tf, font=fonte(44, False), fill=g)
        if i in (0, 2): d.line([(430, y + 30), (800, y + 26)], fill=g, width=4)
    for _ in range(300): x, y = np.random.default_rng(_).integers(0, 1100, 2); d.point((int(x), int(y % 750)), fill=(70, 80, 74))
    mat_imagem('lousa_tarefas', img, 0.85)
    for (x0, x1, y0, y1) in ((-W / 2 - 0.04, W / 2 + 0.04, -0.04, 0.0), (-W / 2 - 0.04, W / 2 + 0.04, H, H + 0.04), (-W / 2 - 0.04, -W / 2, 0, H), (W / 2, W / 2 + 0.04, 0, H)):
        p.cham('madeira_crua', x0, x1, y0, y1, 0.0, 0.03, 0.005)
    p.box('lousa_tarefas', -W / 2, W / 2, 0, H, 0.0, 0.015); p.uv['lousa_tarefas'] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)
    p.cham('madeira_crua', -W / 2, W / 2, -0.06, -0.04, 0.0, 0.07, 0.004)
    for k in range(3): cyl_eixo(p, 'giz', 0.005, -0.4 + k * 0.05, -0.36 + k * 0.05, 'x', (0, -0.035, 0.04), 8)


@item('estoque_latas', 'Estoque de latas empilhadas', 'mobilias', 'abrigo', comodos=['abrigo', 'quartel', 'deposito'], ambiente=True, colisao='caixa',
      conteiner=True, slots=8, saque=['comida'], mostra='visual cresce com a comida guardada na base')
def estoque_latas(M):
    p = M.base; r, h = 0.038, 0.11; n = 5
    for lvl in range(4):
        for i in range(n - lvl):
            for j in range(2):
                x = (i - (n - lvl - 1) / 2) * (2 * r + 0.002); z = (j - 0.5) * (2 * r + 0.004); y = lvl * h
                anel(p, 'lata', r - 0.001, r, y, y + h, 14, 'y', (x, 0, z))
                torno(p, 'lata', [(r, y + h - 0.002), (r, y + h)], 14, 'y', (x, 0, z))
                anel(p, ['rotulo_feijao', 'tinta_vermelha', 'tinta_verde', 'tinta_amarela'][(i + j + lvl) % 4] if False else ['tinta_vermelha', 'tinta_verde', 'tinta_amarela', 'papel'][(i + 2 * j + lvl) % 4],
                     r, r + 0.0006, y + 0.015, y + h - 0.015, 14, 'y', (x, 0, z))


@item('galoes_fila', 'Galões de água enfileirados', 'mobilias', 'abrigo', comodos=['abrigo', 'quartel'], ambiente=True, colisao='caixa', conteiner=True,
      slots=4, saque=['agua'], mostra='quantos estão cheios = água guardada na base')
def galoes_fila(M):
    p = M.base
    for k in range(4):
        x = -0.45 + k * 0.3; cheio = k < 3
        t = P(); galao_agua(type('M', (), {'base': t})()) if 'galao_agua' in globals() else None
        p.merge(t, trimesh.transformations.translation_matrix([x, 0, 0]))
    p.cham('madeira_crua', -0.62, 0.62, -0.02, 0.0, -0.18, 0.18, 0.003)


@item('canteiro_horta', 'Canteiro de horta', 'mobilias', 'abrigo', comodos=['quintal', 'abrigo', 'fazenda', 'igreja'], ambiente=True, colisao='caixa',
      modulo_m=2.0, estacao='horta (planta 1 saco de sementes; colhe 6 comida em 5 dias)', constroi={'tabua': 4, 'terra': 2}, estagios=['vazio', 'brotos', 'pronto'])
def canteiro_horta(M):
    p = M.base; X, Z, H = 0.95, 0.45, 0.3; rng = np.random.default_rng(3)
    for k in range(2):
        y = k * 0.15
        p.cham('madeira_crua', -X, X, y, y + 0.15, -Z, -Z + 0.04, 0.004); p.cham('madeira_crua', -X, X, y, y + 0.15, Z - 0.04, Z, 0.004)
        p.cham('madeira_crua', -X, -X + 0.04, y, y + 0.15, -Z, Z, 0.004); p.cham('madeira_crua', X - 0.04, X, y, y + 0.15, -Z, Z, 0.004)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_crua', xs * (X - 0.04) - 0.03, xs * (X - 0.04) + 0.03, 0.0, H + 0.05, zs * (Z - 0.04) - 0.03, zs * (Z - 0.04) + 0.03, 0.004)
    p.box('terra', -X + 0.04, X - 0.04, 0.0, H - 0.04, -Z + 0.04, Z - 0.04)
    for i in range(6):                                                                        # alfaces
        for j in range(2):
            x = -X + 0.2 + i * 0.3; z = (j - 0.5) * 0.4
            for k in range(5):
                a = k / 5 * 2 * math.pi; fofo(p, 'folha_verde', x + 0.04 * math.cos(a), H + 0.01, z + 0.04 * math.sin(a), 0.06, 0.015, 0.035, 0.7, 0.6, (6, 8))
            fofo(p, 'folha_verde', x, H + 0.02, z, 0.04, 0.04, 0.04, 0.8, 0.8, (6, 8))
    for x in np.linspace(-X + 0.15, X - 0.15, 4): p.seg('madeira_crua', (x, H - 0.04, -Z + 0.03), (x, H + 0.45, -Z + 0.03), 0.012)
    varrer(p, 'corda', circ(0.002, 5), [(-X + 0.15, H + 0.4, -Z + 0.03), (X - 0.15, H + 0.4, -Z + 0.03)])


@item('vaso_tomate', 'Balde com pé de tomate', 'mobilias', 'abrigo', comodos=['abrigo', 'quintal', 'casas', 'igreja'], ambiente=True, colisao='caixa', portatil=True,
      peso_kg=10.0, estacao='horta pequena (2 comida a cada 4 dias)')
def vaso_tomate(M):
    p = M.base; rng = np.random.default_rng(5)
    torno(p, 'plastico_branco', [(0.13, 0.0), (0.155, 0.32), (0.16, 0.33), (0.15, 0.33)], 32, fechar=False); torno(p, 'plastico_branco', [(0.0, 0.0), (0.13, 0.0)], 32)
    varrer(p, 'aco', circ(0.002, 6), [(-0.16, 0.3, 0), (-0.1, 0.42, 0), (0.1, 0.42, 0), (0.16, 0.3, 0)])
    torno(p, 'terra', [(0.0, 0.29), (0.15, 0.29)], 32)
    p.seg('madeira_crua', (0.03, 0.29, 0.0), (0.03, 1.0, 0.0), 0.014)
    for k in range(14):
        y = 0.35 + k * 0.045; a = k * 2.3; L = rng.uniform(0.08, 0.16)
        p.seg('folha_verde', (0, y, 0), (L * math.cos(a), y + 0.05, L * math.sin(a)), 0.006)
        fofo(p, 'folha_verde', L * math.cos(a), y + 0.05, L * math.sin(a), 0.04, 0.006, 0.025, 0.6, 0.6, (6, 8))
        if k % 3 == 1: p.sphere('tomate', 0.025, L * 0.7 * math.cos(a + 0.6), y, L * 0.7 * math.sin(a + 0.6), 2)
    p.seg('folha_verde', (0, 0.29, 0), (0.0, 0.95, 0.0), 0.012)


@item('coletor_chuva', 'Coletor de água da chuva', 'mobilias', 'abrigo', comodos=['abrigo', 'quintal', 'fazenda', 'quartel'], ambiente=True, colisao='caixa',
      estacao='coletor (rende 3 água por dia de chuva; precisa ferver)', constroi={'tambor_200l': 1, 'lona': 1, 'tabua': 3})
def coletor_chuva(M):
    p = M.base; R = 0.3
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_crua', xs * 0.36 - 0.03, xs * 0.36 + 0.03, 0.0, 1.55, zs * 0.36 - 0.03, zs * 0.36 + 0.03, 0.004)
    for y in (0.15, 1.5):
        for zs in (-1, 1): p.cham('madeira_crua', -0.4, 0.4, y, y + 0.05, zs * 0.36 - 0.025, zs * 0.36 + 0.025, 0.004)
    anel(p, 'tinta_azul', R - 0.004, R, 0.2, 1.05, 36); torno(p, 'tinta_azul', [(0.0, 0.2), (R, 0.2)], 36)
    for y in (0.45, 0.8): anel(p, 'tinta_azul', R, R + 0.01, y - 0.015, y + 0.015, 36)
    torno(p, 'agua', [(0.0, 0.95), (R - 0.006, 0.95)], 36)
    pts = [(R * 1.9 * math.cos(a), 1.5 + 0.0, R * 1.9 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)]
    m = trimesh.Trimesh(np.array([(0, 1.12, 0)] + pts[:-1], float), [[0, i % 8 + 1, i + 1] for i in range(8)]) if False else None
    funil = [(0.04, 1.1), (0.5, 1.48), (0.52, 1.5)]
    torno(p, 'lona_azul', funil, 8, fechar=False)
    inner = list(p.parts['lona_azul'])[-1].copy(); inner.invert(); p.add('lona_azul', inner)
    torno(p, 'aco', [(0.035, 1.02), (0.035, 1.12)], 14, fechar=False)
    torno(p, 'aco_polido', [(0.012, 0.0), (0.012, 0.06)], 12, 'x', (R, 0.3, 0))
    cyl_eixo(p, 'plastico_vermelho', 0.012, R + 0.06, R + 0.08, 'x', (0, 0.3, 0), 10)


def _chapa_ondulada(t, L, W, mat, onda=0.076, a=0.009):
    xs = np.linspace(-W / 2, W / 2, int(W / onda * 8) + 1); top = [(x, a + a * math.cos(x * 2 * math.pi / onda)) for x in xs]
    m = trimesh.creation.extrude_polygon(Polygon(top + [(x_, y - 0.0015) for x_, y in top[::-1]]).buffer(0), L)
    m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2], m.vertices[:, 1]], 1)       # chapa em pe: x largura, y altura, z espessura
    if m.volume < 0: m.invert()
    t.add(mat, m)


@item('muro_sucata', 'Muro de sucata', 'mobilias', 'abrigo', comodos=['abrigo', 'quintal', 'rua'], ambiente=True, colisao='caixa', modulo_m=2.0,
      constroi={'chapa_metal': 3, 'tabua': 2, 'caixa_pregos': 1}, vida=400, estacao='defesa (zumbis batem antes de pular)')
def muro_sucata(M):
    p = M.base; rng = np.random.default_rng(13)
    for xs in (-1, 1): p.cham('madeira_escura', xs * 0.96 - 0.05, xs * 0.96 + 0.05, 0.0, 2.1, -0.06, 0.04, 0.006)
    for y in (0.4, 1.6): p.cham('madeira_escura', -1.0, 1.0, y, y + 0.08, -0.06, -0.01, 0.006)
    for k, (x, w, y0, mat, ang) in enumerate(((-0.62, 0.8, 0.0, 'ferrugem', 0.02), (0.18, 0.85, 0.02, 'chapa_pintada', -0.015), (0.7, 0.62, 0.0, 'ferrugem', 0.03),
                                               (-0.3, 0.9, 0.95, 'chapa_pintada', -0.03), (0.5, 0.95, 1.0, 'ferrugem', 0.02))):
        t = P(); _chapa_ondulada(t, 1.15 if y0 < 0.5 else 1.1, w, mat)
        p.merge(t, trimesh.transformations.translation_matrix([x, y0, 0.0 + 0.012 * (k % 2)]) @ _rz(ang))
    for k in range(18):
        x, y = rng.uniform(-0.95, 0.95), rng.choice([0.44, 1.64]); torno(p, 'aco', [(0.006, 0.0), (0.006, 0.003)], 8, 'z', (x, y, 0.03))
    p.cham('tinta_amarela', -0.15, 0.25, 1.25, 1.55, 0.03, 0.035, 0.002)                        # placa velha reaproveitada
    varrer(p, 'aco', circ(0.002, 5), [(x, 2.08 + 0.02 * math.sin(x * 20), 0.0) for x in np.linspace(-0.95, 0.95, 40)])   # arame no topo


@item('portao_sucata', 'Portão de sucata', 'mobilias', 'abrigo', comodos=['abrigo', 'quintal', 'rua'], ambiente=True, colisao='caixa', modulo_m=2.0,
      constroi={'chapa_metal': 2, 'tabua': 4, 'caixa_pregos': 1}, vida=300)
def portao_sucata(M):
    p = M.base
    for xs in (-1, 1): p.cham('madeira_escura', xs * 0.96 - 0.06, xs * 0.96 + 0.06, 0.0, 2.2, -0.06, 0.06, 0.006)
    p.cham('madeira_escura', -1.02, 1.02, 2.1, 2.2, -0.06, 0.06, 0.006)
    for sgn, nm in ((-1, 'folha_esq'), (1, 'folha_dir')):
        hx = sgn * 0.9
        q = M.parte(nm, (hx, 0, 0.07), 'porta', eixo='y', abre_graus=95 * sgn)
        x0, x1 = sorted((hx, sgn * 0.02))
        for y in (0.1, 0.95, 1.8): q.cham('madeira_crua', x0, x1, y, y + 0.12, 0.06, 0.1, 0.005)
        q.seg('madeira_crua', (x0 + 0.05, 0.2, 0.08), (x1 - 0.05, 1.85, 0.08), 0.1, 0.035) if sgn < 0 else q.seg('madeira_crua', (x1 - 0.05, 0.2, 0.08), (x0 + 0.05, 1.85, 0.08), 0.1, 0.035)
        t = P(); _chapa_ondulada(t, 1.9, x1 - x0 - 0.04, 'ferrugem' if sgn < 0 else 'chapa_pintada')
        q.merge(t, trimesh.transformations.translation_matrix([(x0 + x1) / 2, 0.08, 0.1]))
        for y in (0.4, 1.6): cyl_eixo(q, 'aco', 0.02, -0.05, 0.05, 'y', (hx, y, 0.07), 10) if False else q.cyl('aco', 0.02, y - 0.05, y + 0.05, x=hx, z=0.07, sec=10)
    p.cham('aco', -0.06, 0.06, 1.0, 1.04, 0.1, 0.16, 0.004)                                    # trava
    p.cham('madeira_crua', -0.3, 0.3, 1.0, 1.08, 0.16, 0.2, 0.004)


@item('torre_vigia', 'Torre de vigia', 'mobilias', 'abrigo', comodos=['abrigo', 'quintal', 'fazenda'], ambiente=True, colisao='caixa',
      constroi={'tabua': 16, 'caixa_pregos': 2, 'lona': 1}, estacao='vigia (avisa hordas mais cedo; 1 sobrevivente de vigia)', subir=True)
def torre_vigia(M):
    p = M.base; X, H = 1.0, 3.0
    for xs in (-1, 1):
        for zs in (-1, 1):
            p.seg('madeira_escura', (xs * X, 0.0, zs * X), (xs * (X - 0.15), H + 1.2, zs * (X - 0.15)), 0.12)
    for y in (0.9, 2.0):
        for zs in (-1, 1): p.seg('madeira_crua', (-X + 0.05, y, zs * (X - 0.05)), (X - 0.05, y + 0.6, zs * (X - 0.05)), 0.1, 0.04)
        for xs in (-1, 1): p.seg('madeira_crua', (xs * (X - 0.05), y, -X + 0.05), (xs * (X - 0.05), y + 0.6, X - 0.05), 0.04, 0.1)
    for k in range(10): p.cham('madeira_crua', -X + 0.05, X - 0.05, H, H + 0.05, -X + 0.08 + k * 0.188, -X + 0.08 + k * 0.188 + 0.18, 0.004)
    for zs in (-1, 1):
        for y in (H + 0.5, H + 1.0): p.cham('madeira_crua', -X + 0.1, X - 0.1, y, y + 0.1, zs * (X - 0.13) - 0.02, zs * (X - 0.13) + 0.02, 0.004)
    p.cham('madeira_crua', -X + 0.1, X - 0.1, H + 0.5, H + 0.6, -X + 0.11, -X + 0.15, 0.004)
    for y in np.arange(0.25, H, 0.3): p.cham('madeira_crua', 0.25, 0.65, y, y + 0.04, X + 0.02, X + 0.08, 0.004)   # escada
    for x in (0.25, 0.65): p.seg('madeira_crua', (x, 0.0, X + 0.25), (x, H + 0.05, X - 0.05), 0.05, 0.05)
    p.hull('lona_azul', [(x, H + 1.65, z) for x in (-X + 0.05, X - 0.05) for z in (-X + 0.05, X - 0.05)] + [(0, H + 1.95, 0)])   # cobertura de lona
    for xs in (-1, 1):
        for zs in (-1, 1): p.seg('madeira_crua', (xs * (X - 0.15), H + 1.15, zs * (X - 0.15)), (xs * (X - 0.12), H + 1.68, zs * (X - 0.12)), 0.06)
    t = P(); _chapa_ondulada(t, 0.9, 1.6, 'ferrugem')
    p.merge(t, trimesh.transformations.translation_matrix([0, H + 0.05, X - 0.1]))
    torno(p, 'cobre', [(0.06, 0.0), (0.11, 0.15), (0.12, 0.18), (0.0, 0.18)], 20, 'y', (0.55, H + 1.25, -0.55))      # sino de alarme
    p.seg('aco', (0.55, H + 1.43, -0.55), (0.55, H + 1.62, -0.55), 0.01)
