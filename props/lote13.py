# Lote 13: materiais de craft (o que o jogador junta para fabricar ferramentas, estacoes e construcoes).
# Executado por gerar_props.py (usa as mesmas funcoes e materiais dos lotes anteriores).
# Campos novos: celulas [largura, altura] na grade do inventario (jogo/sistemas/grade.gd do Recomeco le direto)
#               obtem_de: de onde o material sai quando nao e achado pronto ({'desmontar': id, 'qtd': n})
#               fase: fase do jogo em que o item comeca a importar (1 Sozinho ... 5 Cidade nova)
# Cores sem textura vao direto para baseColorFactor (linear): valores ja convertidos (sRGB^2,2).
CORES.update({'lona_azul': (24, 60, 120), 'trapo_xadrez': (120, 40, 36), 'trapo_bege': (190, 170, 130), 'couro': (98, 58, 30),
              'nylon_branco': (200, 196, 186), 'pvc': (196, 196, 190), 'fio_azul': (2, 12, 80), 'fio_vermelho': (80, 2, 2),
              'carvao': (5, 5, 6), 'saco_rafia': (176, 150, 112), 'tijolo': (156, 70, 44), 'cimento_saco': (200, 196, 186),
              'linha_verde': (10, 68, 26), 'galvanizado': (104, 108, 110), 'pedra_rio': (130, 124, 112), 'esmeril': (38, 36, 33),
              'trapo_cinza': (96, 98, 104), 'pedra_escura': (88, 84, 78)})
METALICOS.update({'galvanizado': (0.85, 0.42), 'esmeril': (0.0, 0.85)})
FOSCOS.update({'pvc': 0.4, 'fio_azul': 0.45, 'fio_vermelho': 0.45, 'carvao': 0.95, 'nylon_branco': 0.5})
TEX_PROPRIAS += [('lona_azul', 'tecido', 0.5, 768), ('trapo_xadrez', 'xadrez', 0.25, 1024), ('trapo_bege', 'tecido', 0.25, 1024),
                 ('trapo_cinza', 'tecido', 0.25, 1024), ('saco_rafia', 'papelao', 0.5, 512), ('cimento_saco', 'papelao', 0.5, 512),
                 ('tijolo', 'barro', 0.5, 512), ('couro', 'couro', 0.25, 1024), ('pedra_rio', 'couro', 0.5, 512), ('pedra_escura', 'couro', 0.5, 512)]

_ruido_tex_antes = _ruido_tex
def _ruido_tex(col, seed, px, tile, kind):
    """Acrescenta texturas: barro (tijolo), couro (granulado) e xadrez (pano de camisa)."""
    n = int(tile * px); c = GT.rgb(col)[None, None]
    if kind == 'barro':
        f = GT.fbm(n, n, 0.03 * px, 4, seed + 1); g = GT.noise(n, n, 0.004 * px, 0.004 * px, seed + 2)
        pit = GT.smooth(0.7, 0.8, GT.noise(n, n, 0.003 * px, 0.003 * px, seed + 3))
        alb = c * (0.9 + 0.14 * f[..., None] + 0.04 * g[..., None]) * (1 - 0.2 * pit[..., None])
        return alb, 0.0006 * f - 0.0006 * pit, 0.85 + 0.1 * f, 0.9, 0.0015
    if kind == 'couro':
        g = GT.noise(n, n, 0.0018 * px, 0.0018 * px, seed + 2); f = GT.fbm(n, n, 0.04 * px, 3, seed + 1)
        alb = c * (0.9 + 0.12 * f[..., None] + 0.04 * g[..., None])
        return alb, 0.0002 * g + 0.0003 * f, 0.55 + 0.2 * f, 0.6, 0.0008
    if kind == 'xadrez':
        yy, xx = np.mgrid[0:n, 0:n] / px; per = tile / 6
        a = ((xx % per) < per * 0.45).astype(float); b = ((yy % per) < per * 0.45).astype(float)
        alb, hm, r, ns, ao = _ruido_tex_antes(col, seed, px, tile, 'tecido')
        alb = alb * (1 - 0.35 * a[..., None]) * (1 - 0.35 * b[..., None]) + 0.25 * (a * b)[..., None] * GT.rgb((230, 220, 200))[None, None]
        return alb, hm, r, ns, ao
    return _ruido_tex_antes(col, seed, px, tile, kind)


def _amassar(p, mat, amp=0.004, freq=40.0, seed=0, sub=1):
    """Amassa a ultima malha do material (pano, saco): subdivide e empurra os vertices pela normal com ruido suave."""
    m = p.parts[mat][-1]
    for _ in range(sub): m = m.subdivide()
    rng = np.random.default_rng(seed); k = rng.normal(size=(6, 3)) * freq; ph = rng.uniform(0, 6.3, 6)
    v = m.vertices; d = sum(np.sin(v @ k[i] + ph[i]) for i in range(6)) / 6
    m.vertices = v + m.vertex_normals * (amp * d)[:, None]
    p.parts[mat][-1] = m


def _rot(ang, eixo, c=(0, 0, 0)): return trimesh.transformations.rotation_matrix(ang, eixo, point=c)


def _parafuso(p, c, L=0.04, r=0.004, eixo='x', mat='aco'):
    """Parafuso sextavado deitado: cabeca + corpo com rosca (aneis)."""
    x, y, z = c
    if eixo == 'x':
        torno(p, mat, [(r * 1.8, 0), (r * 1.8, r * 1.4)], 6, 'x', (x, y, z))
        cyl_eixo(p, mat, r, x + r * 1.4, x + L, 'x', (0, y, z), 10)
        for xx in np.linspace(x + L * 0.45, x + L - 0.002, 6): anel(p, mat, r * 0.9, r * 1.12, xx, xx + 0.0012, 10, 'x', (0, y, z))
    else:
        torno(p, mat, [(r * 1.8, 0), (r * 1.8, r * 1.4)], 6, 'z', (x, y, z))
        cyl_eixo(p, mat, r, z + r * 1.4, z + L, 'z', (x, y, 0), 10)
        for zz in np.linspace(z + L * 0.45, z + L - 0.002, 6): anel(p, mat, r * 0.9, r * 1.12, zz, zz + 0.0012, 10, 'z', (x, y, 0))


def _porca(p, c, r=0.007, h=0.0055, mat='aco'):
    anel(p, mat, r * 0.5, r, c[1], c[1] + h, 6, 'y', (c[0], 0, c[2]), chanfro=0.0008)


def _mola(p, c, r=0.009, L=0.05, voltas=8, fio=0.0012, mat='aco_polido', eixo='x'):
    t = np.linspace(0, 2 * math.pi * voltas, voltas * 14)
    if eixo == 'x': pts = np.stack([c[0] + t / t[-1] * L, c[1] + r * np.cos(t), c[2] + r * np.sin(t)], 1)
    else: pts = np.stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t), c[2] + t / t[-1] * L], 1)
    varrer(p, mat, circ(fio, 6), pts)


def _engrenagem(p, c, r, dentes, esp, mat='aco', furo=0.3):
    """Engrenagem deitada (eixo y): disco com dentes trapezoidais e furo."""
    pts = []
    for k in range(dentes):
        a = k * 2 * math.pi / dentes; da = math.pi / dentes
        for aa, rr in ((a - da * 0.95, r * 0.86), (a - da * 0.45, r), (a + da * 0.45, r), (a + da * 0.95, r * 0.86)):
            pts.append((rr * math.cos(aa), rr * math.sin(aa)))
    poly = Polygon(pts).buffer(0).difference(Point(0, 0).buffer(r * furo, 16))
    m = trimesh.creation.extrude_polygon(poly, esp); m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2], -m.vertices[:, 1]], 1)
    m.apply_translation(c); p.add(mat, m)


def _rolo_fio(p, mat, R, r0, largura, fio, voltas=6, camadas=3, c=(0, 0, 0), eixo='y'):
    """Rolo de fio/arame: espiras sobrepostas (camadas) num anel de raio R."""
    cx, cy, cz = c
    for k in range(camadas):
        rr = R + k * fio * 1.8
        t = np.linspace(0, 2 * math.pi * voltas, voltas * 30)
        h = (t / t[-1]) * largura if k % 2 == 0 else (1 - t / t[-1]) * largura
        tt = t + k * 0.7
        if eixo == 'y': pts = np.stack([cx + rr * np.cos(tt), cy + r0 + h, cz + rr * np.sin(tt)], 1)
        else: pts = np.stack([cx + rr * np.cos(tt), cy + rr * np.sin(tt), cz + r0 + h], 1)
        varrer(p, mat, circ(fio, 6), pts)


# ---------------------------------------------------------------------------- METAL E PECAS
@item('sucata_metal', 'Punhado de sucata', 'loot', 'materiais', recurso='sucata', valor=1, peso_kg=1.2, empilha=10, celulas=[2, 1], fase=1,
      onde=['ferrovelho', 'garagem', 'posto', 'fabrica', 'rua'], efeito='1 sucata: base de quase toda receita de metal',
      obtem_de=[{'desmontar': 'carcaca_carro', 'qtd': 12}, {'desmontar': 'pilha_sucata', 'qtd': 8}, {'desmontar': 'carrinho_compras', 'qtd': 3},
                {'desmontar': 'arquivo_aco', 'qtd': 4}, {'desmontar': 'estante_metal', 'qtd': 4}])
def sucata_metal(M):
    p = M.base; rng = np.random.default_rng(13)
    # retalho de chapa dobrado e enferrujado
    pts = [(-0.11, -0.04), (0.02, -0.06), (0.07, -0.02), (0.05, 0.05), (-0.06, 0.06), (-0.12, 0.02)]
    m = trimesh.creation.extrude_polygon(Polygon(pts), 0.0018); m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2], -m.vertices[:, 1]], 1)
    v = m.vertices; v[:, 1] += 0.022 * np.clip((v[:, 0] + 0.02) / 0.09, 0, 1) ** 2 + 0.004
    p.add('ferrugem', m)
    # cantoneira cortada
    prof_x(p, 'aco_pintado', -0.02, 0.13, [(0.0, 0.0), (0.03, 0.0), (0.03, 0.003), (0.003, 0.003), (0.003, 0.03), (0.0, 0.03)])
    p.parts['aco_pintado'][-1].apply_translation([0, 0.0, 0.035])
    for x in (0.02, 0.08): cyl_eixo(p, 'ferrugem', 0.0035, 0.0, 0.0035, 'y', (x, 0.0, 0.05), 10)
    _parafuso(p, (-0.04, 0.033, -0.02), 0.05, 0.0042)
    _parafuso(p, (0.04, 0.03, -0.05), 0.035, 0.0035, 'z')
    for c in ((-0.09, 0.0, 0.045), (0.1, 0.0, -0.03), (0.065, 0.0, 0.0)): _porca(p, c)
    _mola(p, (-0.13, 0.012, -0.03), 0.008, 0.045, 7)
    p.seg('aco', (0.09, 0.004, 0.06), (0.15, 0.006, 0.02), 0.004, 0.004)           # vergalhao curto
    for xx in np.linspace(0.092, 0.148, 8):
        k = (xx - 0.09) / 0.06; c = np.array([0.09, 0.004, 0.06]) + k * np.array([0.06, 0.002, -0.04])
        p.seg('aco', c - [0.0, 0.0025, 0.0015], c + [0.0, 0.0025, 0.0015], 0.0012, 0.0012)


@item('pote_parafusos', 'Pote de parafusos e porcas', 'loot', 'materiais', recurso='sucata', valor=2, peso_kg=0.9, empilha=4, celulas=[1, 1], fase=1,
      onde=['garagem', 'casas', 'fabrica', 'serraria'], efeito='fixa peças: armas, bancadas, portas reforçadas')
def pote_parafusos(M):
    p = M.base; R, H = 0.042, 0.11
    anel(p, 'vidro_prateleira', R - 0.0025, R, 0.003, H - 0.012, 32)
    torno(p, 'vidro_prateleira', [(R - 0.006, 0.0), (R, 0.004), (R - 0.003, 0.004)], 32)
    anel(p, 'vidro_prateleira', R - 0.006, R - 0.003, H - 0.014, H - 0.006, 32)
    torno(p, 'tinta_vermelha', [(R - 0.001, H - 0.016), (R + 0.001, H - 0.015), (R + 0.001, H), (R - 0.004, H + 0.002)], 32)
    for y in np.linspace(H - 0.014, H - 0.003, 6): anel(p, 'tinta_vermelha', R + 0.0009, R + 0.0016, y, y + 0.0009, 32)
    rng = np.random.default_rng(3)
    for i in range(26):                                                    # recheio ate 60 %
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0, R - 0.012); y = rng.uniform(0.008, 0.062)
        c = (r * math.cos(a), y, r * math.sin(a))
        if i % 3 == 0: _porca(p, c, 0.0055, 0.004)
        elif i % 3 == 1:
            m = P(); _parafuso(m, (0, 0, 0), 0.025, 0.0028)
            T = trimesh.transformations.translation_matrix(c) @ _rot(rng.uniform(0, 6), [0, 1, 0]) @ _rot(rng.uniform(-0.6, 0.6), [0, 0, 1])
            p.merge(m, T)
        else: anel(p, 'aco_polido', 0.0025, 0.0055, y, y + 0.001, 12, 'y', (c[0], 0, c[2]))     # arruela
    img = Image.new('RGB', (512, 128), (240, 236, 220)); d = ImageDraw.Draw(img)
    texto_c(d, (256, 64), 'PARAFUSOS 1/4"', 48, (40, 30, 26)); mat_imagem('etiqueta_pote', img, 0.7)
    anel(p, 'etiqueta_pote', R, R + 0.0006, 0.035, 0.062, 32); p.uv['etiqueta_pote'] = uv_cilindro(0.035, 0.062)


@item('engrenagens', 'Molas e engrenagens', 'loot', 'materiais', recurso='pecas', valor=1, peso_kg=0.6, empilha=6, celulas=[1, 1], fase=2,
      onde=['fabrica', 'garagem', 'relojoaria', 'casas'], efeito='mecanismos: armadilhas, besta, bomba d\'água, cata-vento',
      obtem_de=[{'desmontar': 'relogio_parede', 'qtd': 2}, {'desmontar': 'maquina_lavar', 'qtd': 3}, {'desmontar': 'vitrola', 'qtd': 2}])
def engrenagens(M):
    p = M.base
    _engrenagem(p, (-0.025, 0.0, 0.0), 0.042, 24, 0.006, 'aco')
    _engrenagem(p, (0.04, 0.006, 0.018), 0.026, 16, 0.006, 'cobre', 0.25)
    _engrenagem(p, (0.03, 0.0, -0.035), 0.018, 12, 0.008, 'aco_polido', 0.35)
    cyl_eixo(p, 'aco_polido', 0.004, 0.006, 0.03, 'y', (-0.025, 0, 0), 12)
    _mola(p, (-0.06, 0.012, 0.05), 0.009, 0.06, 9)
    _mola(p, (0.0, 0.007, -0.07), 0.005, 0.045, 12, 0.0008, 'aco')


@item('placa_circuito', 'Placa de circuito', 'loot', 'eletronicos', recurso='pecas', valor=1, peso_kg=0.2, empilha=6, celulas=[1, 1], fase=3,
      onde=['casas', 'escritorio', 'cinema', 'delegacia', 'correios'], efeito='eletrônica: rádio, holofote, painel solar',
      obtem_de=[{'desmontar': 'rack_tv', 'qtd': 2}, {'desmontar': 'tv_tubo', 'qtd': 2}, {'desmontar': 'radio_portatil', 'qtd': 1}])
def placa_circuito(M):
    p = M.base; X, Z, t = 0.07, 0.05, 0.0016
    img = Image.new('RGB', (560, 400), (14, 70, 30)); d = ImageDraw.Draw(img); rng = np.random.default_rng(9)
    for i in range(70):                                                     # trilhas
        x, y = rng.integers(10, 550), rng.integers(10, 390); dx = rng.choice([-1, 1]) * rng.integers(30, 160)
        d.line([(x, y), (x + dx, y), (x + dx, y + rng.integers(-60, 60))], fill=(150, 130, 60), width=3)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(200, 190, 160))
    texto_c(d, (440, 370), 'RX-204 REV B', 22, (230, 230, 220))
    mat_imagem('pcb', img, 0.4); p.box('pcb', -X, X, 0, t, -Z, Z); p.uv['pcb'] = uv_plano(-X, X, -Z, Z)
    p.cham('plastico_preto', -0.03, 0.01, t, t + 0.004, -0.012, 0.012, 0.0008)                  # chip
    for i in range(8):
        for zs in (-1, 1): p.box('aco_polido', -0.028 + i * 0.005, -0.026 + i * 0.005, t, t + 0.002, zs * 0.012, zs * 0.0145)
    for (x, z, r, h, mat) in ((0.035, 0.025, 0.0055, 0.014, 'fio_azul'), (0.05, -0.02, 0.004, 0.01, 'plastico_preto'), (-0.05, 0.03, 0.0035, 0.008, 'fio_azul')):
        torno(p, mat, [(r, t), (r, t + h), (r * 0.9, t + h + 0.0006)], 16, 'y', (x, 0, z))             # capacitores
        torno(p, 'aco_polido', [(r * 0.8, t + h + 0.0006), (r * 0.8, t + h + 0.0009)], 16, 'y', (x, 0, z))
    for i in range(5):
        x = 0.0 + i * 0.008; p.cham('tijolo', x, x + 0.0055, t, t + 0.0022, -0.035, -0.027, 0.0006)  # resistores
    p.cham('plastico_branco', 0.045, 0.068, t, t + 0.009, 0.008, 0.035, 0.001)                  # conector
    p.box('aco', -X + 0.004, -X + 0.03, t, t + 0.012, -0.045, -0.02)                             # dissipador
    for i in range(5): p.box('aco', -X + 0.004 + i * 0.0055, -X + 0.0065 + i * 0.0055, t + 0.012, t + 0.02, -0.045, -0.02)
    for xs in (-1, 1):
        for zs in (-1, 1): anel(p, 'aco_polido', 0.0016, 0.0028, -0.0002, t + 0.0003, 12, 'y', (xs * (X - 0.005), 0, zs * (Z - 0.005)))


@item('motor_eletrico', 'Motor elétrico pequeno', 'loot', 'eletronicos', recurso='pecas', valor=2, peso_kg=1.6, empilha=1, celulas=[2, 1], fase=3,
      onde=['casas', 'fabrica', 'garagem', 'lavanderia'], efeito='gera energia girando (cata-vento, bicicleta-gerador) ou move bomba d\'água',
      obtem_de=[{'desmontar': 'maquina_lavar', 'qtd': 1}, {'desmontar': 'aquecedor', 'qtd': 1}, {'desmontar': 'compressor_ar', 'qtd': 1}])
def motor_eletrico(M):
    p = M.base; R = 0.048; L = 0.11; y = R + 0.012
    anel(p, 'aco_pintado', R - 0.004, R, -L / 2, L / 2, 32, 'x', (0, y, 0), chanfro=0.002)
    for x in np.linspace(-L / 2 + 0.01, L / 2 - 0.01, 9): p.box('aco_pintado', x - 0.002, x + 0.002, y + R - 0.002, y + R + 0.008, -0.012, 0.012)  # aletas
    for s in (-1, 1):
        torno(p, 'aco', [(R - 0.002, 0), (R - 0.001, 0.008), (R * 0.6, 0.016), (0.012, 0.018)], 32, 'x', (s * L / 2, y, 0)) if s > 0 else \
            torno(p, 'aco', [(0.012, -0.018), (R * 0.6, -0.016), (R - 0.001, -0.008), (R - 0.002, 0)], 32, 'x', (s * L / 2, y, 0))
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            cyl_eixo(p, 'aco_polido', 0.0025, -L / 2 - 0.004, L / 2 + 0.004, 'x', (0, y + (R - 0.006) * math.sin(a), (R - 0.006) * math.cos(a)), 8)
    cyl_eixo(p, 'aco_polido', 0.006, L / 2 + 0.018, L / 2 + 0.05, 'x', (0, y, 0), 16)            # eixo com chaveta
    p.box('aco', L / 2 + 0.025, L / 2 + 0.05, y + 0.005, y + 0.0075, -0.0015, 0.0015)
    p.cham('aco_pintado', -L / 2 + 0.005, L / 2 - 0.005, 0.0, 0.006, -0.05, 0.05, 0.002)             # pe
    for zs in (-1, 1): p.hull('aco_pintado', [(x, 0.006, zs * 0.03) for x in (-0.04, 0.04)] + [(x, y - R * 0.6, zs * 0.025) for x in (-0.04, 0.04)] + [(x, 0.006, zs * 0.045) for x in (-0.04, 0.04)])
    p.cham('aco_pintado', -0.02, 0.02, y - 0.01, y + 0.028, R - 0.004, R + 0.02, 0.003)              # caixa de ligacao
    for i, mat in enumerate(('fio_azul', 'fio_vermelho')):
        varrer(p, mat, circ(0.0022, 8), [(-0.008 + i * 0.016, y + 0.005, R + 0.02), (-0.01 + i * 0.02, y - 0.01, R + 0.05), (-0.03 + i * 0.05, 0.004, R + 0.07)])


@item('fio_eletrico', 'Rolo de fio elétrico', 'loot', 'eletronicos', recurso='pecas', valor=1, peso_kg=0.8, empilha=3, celulas=[1, 1], fase=2,
      onde=['casas', 'fabrica', 'garagem', 'cinema', 'hotel'], efeito='ligar luzes, alarmes, gerador e painel solar (10 m)',
      obtem_de=[{'desmontar': 'cordao_luzes', 'qtd': 1}, {'desmontar': 'abajur', 'qtd': 1}])
def fio_eletrico(M):
    p = M.base
    _rolo_fio(p, 'fio_vermelho', 0.05, 0.0, 0.03, 0.0028, voltas=5, camadas=3)
    varrer(p, 'fio_vermelho', circ(0.0028, 6), [(0.058, 0.03, 0.0), (0.085, 0.02, 0.025), (0.11, 0.004, 0.02), (0.13, 0.0035, -0.01)])
    cyl_eixo(p, 'cobre', 0.0012, 0.13, 0.145, 'x', (0, 0.0035, -0.01), 8)
    for a in (0.3, 2.5, 4.3):
        p.seg('plastico_preto', (0.05 * math.cos(a) - 0.002, 0.0, 0.05 * math.sin(a)), (0.065 * math.cos(a), 0.034, 0.065 * math.sin(a)), 0.012, 0.0015)


@item('arame_liso', 'Rolo de arame liso', 'loot', 'materiais', recurso='sucata', valor=1, peso_kg=1.0, empilha=3, celulas=[1, 1], fase=1,
      onde=['armazem', 'fazenda', 'serraria', 'garagem', 'casa_de_campo'], efeito='amarrar: armadilhas, cercas, lanças e reparos (20 m)')
def arame_liso(M):
    p = M.base
    _rolo_fio(p, 'galvanizado', 0.065, 0.0, 0.025, 0.0012, voltas=9, camadas=4)
    for a in (0.0, 2.1, 4.2):                                                               # amarras
        c = (0.07 * math.cos(a), 0.012, 0.07 * math.sin(a))
        varrer(p, 'galvanizado', circ(0.0012, 6), [(c[0] * 0.88, -0.001, c[2] * 0.88), (c[0] * 1.14, -0.001, c[2] * 1.14), (c[0] * 1.14, 0.03, c[2] * 1.14), (c[0] * 0.88, 0.03, c[2] * 0.88)])
    varrer(p, 'galvanizado', circ(0.0012, 6), [(0.072, 0.02, 0.0), (0.1, 0.03, 0.03), (0.12, 0.012, 0.06)])


@item('corrente_cadeado', 'Corrente com cadeado', 'loot', 'materiais', recurso='sucata', valor=2, peso_kg=2.2, empilha=1, celulas=[2, 1], fase=2,
      onde=['garagem', 'armazem', 'delegacia', 'estacao', 'parque_trailers'], efeito='tranca portão ou armário (zumbi não abre, saqueador precisa de alicate)')
def corrente_cadeado(M):
    p = M.base; rng = np.random.default_rng(4)
    cam = [(-0.2 + 0.022 * i, 0.0, 0.06 * math.sin(i * 0.3)) for i in range(16)]
    for i, (x, _, z) in enumerate(cam):
        T = trimesh.transformations.translation_matrix([x, 0.004 if i % 2 == 0 else 0.016, z])
        R = _rot(-math.atan2(0.06 * 0.3 * math.cos(i * 0.3), 0.022), [0, 1, 0])
        m = trimesh.creation.torus(0.0115, 0.0036, major_sections=18, minor_sections=8)
        m.vertices[:, 0] *= 1.45
        if i % 2: m.apply_transform(_rot(math.pi / 2, [1, 0, 0]))
        m.apply_transform(T @ R); p.add('galvanizado', m)
    # cadeado no fim da corrente
    x0 = cam[-1][0] + 0.035; z0 = cam[-1][2]
    p.cham('latao', x0 - 0.022, x0 + 0.022, 0.0, 0.016, z0 - 0.026, z0 + 0.012, 0.004)
    varrer(p, 'aco_polido', circ(0.0035, 10), [(x0 - 0.013, 0.008, z0 + 0.012), (x0 - 0.013, 0.008, z0 + 0.03), (x0 - 0.006, 0.008, z0 + 0.04),
                                               (x0 + 0.006, 0.008, z0 + 0.04), (x0 + 0.013, 0.008, z0 + 0.03), (x0 + 0.013, 0.008, z0 + 0.012)])
    cyl_eixo(p, 'aco', 0.004, 0.0158, 0.0165, 'y', (x0, 0, z0 - 0.012), 16)
    p.box('plastico_preto', x0 - 0.0006, x0 + 0.0006, 0.0164, 0.0166, z0 - 0.0145, z0 - 0.0095)


@item('dobradicas', 'Par de dobradiças', 'loot', 'materiais', recurso='sucata', valor=1, peso_kg=0.4, empilha=6, celulas=[1, 1], fase=2,
      onde=['casas', 'garagem', 'serraria', 'armazem'], efeito='portões, alçapões, tampas de caixote e armários',
      obtem_de=[{'desmontar': 'guarda_roupa', 'qtd': 2}, {'desmontar': 'armario_aereo', 'qtd': 2}])
def dobradicas(M):
    p = M.base
    for k, (dx, dz, a) in enumerate(((-0.03, 0.0, 0.2), (0.035, 0.01, -0.5))):
        q = P(); W, H, t = 0.035, 0.075, 0.0018
        for s in (-1, 1):
            q.cham('galvanizado', min(0, s * W), max(0, s * W) - (0.003 if s < 0 else -0.003), 0, t, -H / 2, H / 2, 0.0006)
            for zz in (-0.022, 0.0, 0.022):
                torno(q, 'aco', [(0.0034, t), (0.0028, t + 0.0012)], 10, 'y', (s * W * 0.55, 0, zz))
        cyl_eixo(q, 'galvanizado', 0.0042, -H / 2, H / 2, 'z', (0, 0.004, 0), 14)
        for zz in np.linspace(-H / 2 + H / 5, H / 2 - H / 5, 4): anel(q, 'aco', 0.0041, 0.0045, zz - 0.0003, zz + 0.0003, 14, 'z', (0, 0.004, 0))
        p.merge(q, trimesh.transformations.translation_matrix([dx, 0, dz]) @ _rot(a, [0, 1, 0]))


@item('abracadeiras', 'Pacote de abraçadeiras de nylon', 'loot', 'materiais', recurso='material', valor=1, peso_kg=0.1, empilha=10, celulas=[1, 1], fase=1,
      onde=['garagem', 'casas', 'fabrica', 'cinema', 'supermercado'], efeito='amarra rápido: armadilhas, lanternas na arma, reparos')
def abracadeiras(M):
    p = M.base; X, Z = 0.05, 0.11
    img = Image.new('RGB', (400, 880), (250, 250, 250)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 400, 180], fill=(230, 120, 20)); texto_c(d, (200, 70), 'AMARRA', 70, (255, 255, 255)); texto_c(d, (200, 140), '100 un · 20 cm', 34, (255, 255, 255))
    mat_imagem('saco_abrac', img, 0.6)
    p.cham('plastico_transp', -X, X, 0.0, 0.016, -Z, Z, 0.006)
    p.box('saco_abrac', -X + 0.002, X - 0.002, 0.016, 0.0165, Z - 0.05, Z - 0.002); p.uv['saco_abrac'] = uv_plano(-X, X, Z - 0.05 - 0.17, Z - 0.002)
    p.cham('plastico_transp', -X + 0.004, X - 0.004, 0.0, 0.004, Z - 0.004, Z + 0.004, 0.0015)          # solda do saco
    for i in range(11):                                                        # abracadeiras dentro
        x = -X + 0.008 + i * 0.0076; p.box('nylon_branco', x, x + 0.004, 0.003 + (i % 3) * 0.003, 0.0042 + (i % 3) * 0.003, -Z + 0.015, Z - 0.03)
        p.cham('nylon_branco', x - 0.001, x + 0.005, 0.002 + (i % 3) * 0.003, 0.006 + (i % 3) * 0.003, -Z + 0.008, -Z + 0.016, 0.0008)
    # duas soltas: uma aberta, uma fechada em laco
    p.box('nylon_branco', X + 0.01, X + 0.014, 0.0, 0.0012, -0.08, 0.1)
    p.cham('nylon_branco', X + 0.008, X + 0.016, 0.0, 0.004, -0.088, -0.08, 0.0008)
    t = np.linspace(0, 2 * math.pi, 28); pts = np.stack([X + 0.045 + 0.022 * np.cos(t), np.full_like(t, 0.002), 0.03 + 0.022 * np.sin(t)], 1)
    for a, b in zip(pts[:-1], pts[1:]): p.seg('nylon_branco', a, b, 0.004, 0.0012)
    p.cham('nylon_branco', X + 0.063, X + 0.071, 0.0, 0.005, 0.026, 0.034, 0.0008)
    p.box('nylon_branco', X + 0.07, X + 0.11, 0.0, 0.0012, 0.028, 0.032)


@item('cola_contato', 'Lata de cola de contato', 'loot', 'materiais', recurso='material', valor=1, peso_kg=0.3, empilha=4, celulas=[1, 1], fase=2,
      onde=['casas', 'garagem', 'serraria', 'escolinha'], efeito='cola couro, borracha e madeira: proteções, reparo de botas e mochila')
def cola_contato(M):
    p = M.base; R, H = 0.036, 0.085
    def desenho(d):
        for cx in (256, 768):
            d.rectangle([cx - 230, 120, cx + 230, 264], fill=(250, 210, 30))
            texto_c(d, (cx, 160), 'COLA FORTE', 56, (20, 20, 20), larg=440); texto_c(d, (cx, 225), 'CONTATO · 200 g', 30, (20, 20, 20))
    img = Image.new('RGB', (1024, 384), (20, 20, 20)); desenho(ImageDraw.Draw(img)); mat_imagem('rot_cola', img, 0.5)
    anel(p, 'rot_cola', R - 0.001, R, 0.004, H - 0.006, 40); p.uv['rot_cola'] = uv_cilindro(0.004, H - 0.006)
    torno(p, 'lata', [(R - 0.002, 0.0), (R + 0.0008, 0.002), (R + 0.0008, 0.005), (R - 0.001, 0.005)], 40)
    torno(p, 'lata', [(R - 0.001, H - 0.006), (R + 0.0008, H - 0.004), (R + 0.0008, H), (R - 0.004, H), (R - 0.004, H - 0.002), (0.0, H - 0.003)], 40)
    torno(p, 'lata', [(0.022, H - 0.003), (0.022, H + 0.004), (0.02, H + 0.005)], 32)
    torno(p, 'plastico_preto', [(0.0235, H + 0.002), (0.0235, H + 0.016), (0.021, H + 0.018)], 32)
    for k in range(24):
        a = k * 2 * math.pi / 24; p.box('plastico_preto', 0.0232 * math.cos(a) - 0.0008, 0.0232 * math.cos(a) + 0.0008, H + 0.003, H + 0.015, 0.0232 * math.sin(a) - 0.0008, 0.0232 * math.sin(a) + 0.0008)
    p.seg('tinta_amarela', (R - 0.001, H - 0.004, 0.0), (R + 0.001, H - 0.03, 0.004), 0.006, 0.0015)


@item('garrafa_pet', 'Garrafa PET vazia 2 L', 'loot', 'utensilios', recurso='material', valor=1, peso_kg=0.05, empilha=4, celulas=[1, 2], fase=1,
      onde=['casas', 'rua', 'supermercado', 'diner', 'posto'], efeito='filtro de água, coletor, armadilha de garrafa e isca')
def garrafa_pet(M):
    p = M.base; r = 0.054; H = 0.32
    # garrafa deitada (eixo x), amassada de leve
    perfil = [(r * 0.7, 0.0), (r * 0.95, 0.006), (r, 0.03), (r, 0.18), (r * 0.98, 0.2), (r * 0.6, 0.27), (0.017, 0.295), (0.015, 0.3)]
    q = P(); torno(q, 'pet', perfil, 28)
    for y in (0.07, 0.1, 0.13, 0.16): anel(q, 'pet', r - 0.001, r + 0.0012, y, y + 0.004, 28)
    for k in range(5):                                                          # pes petaloides
        a = k * 2 * math.pi / 5; fofo(q, 'pet', 0.03 * math.cos(a), 0.008, 0.03 * math.sin(a), 0.018, 0.008, 0.018, 0.5, 0.5, (8, 10))
    torno(q, 'pet', [(0.021, 0.298), (0.021, 0.301)], 24)
    torno(q, 'plastico_cinza', [(0.0155, 0.3), (0.0155, 0.322), (0.013, 0.324)], 24)
    for k in range(20):
        a = k * 2 * math.pi / 20; q.box('plastico_cinza', 0.0154 * math.cos(a) - 0.0006, 0.0154 * math.cos(a) + 0.0006, 0.302, 0.32, 0.0154 * math.sin(a) - 0.0006, 0.0154 * math.sin(a) + 0.0006)
    for m in q.parts['pet']:
        v = m.vertices; v[:, 0] = np.where(v[:, 0] > 0, v[:, 0] * (1 - 0.18 * np.exp(-((v[:, 1] - 0.15) / 0.05) ** 2)), v[:, 0])
    T = trimesh.transformations.translation_matrix([-H / 2, r * 0.97, 0]) @ _rot(-math.pi / 2, [0, 0, 1])
    p.merge(q, T)


@item('lata_vazia', 'Lata vazia', 'loot', 'utensilios', recurso='sucata', valor=1, peso_kg=0.06, empilha=8, celulas=[1, 1], fase=1,
      onde=['casas', 'rua', 'supermercado', 'diner', 'abrigo'], efeito='alarme de latas, lamparina, fogareiro e caneca de ferver água',
      obtem_de=[{'consumir': 'lata_feijao', 'qtd': 1}, {'consumir': 'lata_milho', 'qtd': 1}])
def lata_vazia(M):
    p = M.base; R, H = 0.038, 0.11
    anel(p, 'lata', R - 0.0006, R, 0.004, H - 0.004, 36)
    torno(p, 'lata', [(R - 0.003, 0.0), (R + 0.0008, 0.002), (R + 0.0008, 0.005), (R - 0.002, 0.005), (0.0, 0.004)], 36)
    anel(p, 'lata', R - 0.0006, R + 0.001, H - 0.005, H, 36)
    for y in np.linspace(0.02, H - 0.02, 9): anel(p, 'lata', R - 0.0004, R + 0.0007, y, y + 0.0025, 36)
    # tampa meio aberta presa na borda (dente serrilhado)
    q = P(); pts = [(R * 0.94 * math.cos(a), R * 0.94 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
    m = trimesh.creation.extrude_polygon(Polygon(pts), 0.0005); m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2], -m.vertices[:, 1]], 1)
    q.add('lata', m); anel(q, 'lata', R * 0.75, R * 0.8, 0.0, 0.001, 36)
    p.merge(q, trimesh.transformations.translation_matrix([R * 0.94, H - 0.002, 0]) @ _rot(-1.9, [0, 0, 1]) @ trimesh.transformations.translation_matrix([-R * 0.94, 0, 0]))
    for k in range(30):                                                           # borda cortada
        a = k * 2 * math.pi / 30
        if abs(math.atan2(math.sin(a), math.cos(a))) < 0.5: continue
        p.hull('lata', [(R * 0.96 * math.cos(a), H - 0.0005, R * 0.96 * math.sin(a)), (R * 0.96 * math.cos(a + 0.1), H - 0.0005, R * 0.96 * math.sin(a + 0.1)),
                        (R * 0.95 * math.cos(a + 0.05), H + 0.002, R * 0.95 * math.sin(a + 0.05)), (R * 0.94 * math.cos(a + 0.05), H - 0.0005, R * 0.94 * math.sin(a + 0.05))])
    anel(p, 'ferrugem', R - 0.0003, R + 0.0003, 0.004, 0.02, 36)


@item('tubo_pvc', 'Cano de PVC', 'loot', 'materiais', recurso='material', valor=1, peso_kg=0.6, empilha=4, celulas=[4, 1], fase=2,
      onde=['casas', 'armazem', 'fabrica', 'piscina', 'fazenda'], efeito='calhas, coletor de chuva, irrigação da horta e filtros')
def tubo_pvc(M):
    p = M.base; L = 1.0; R = 0.025
    anel(p, 'pvc', R - 0.0022, R, -L / 2, L / 2 - 0.05, 28, 'x', (0, R, 0))
    anel(p, 'pvc', R - 0.0006, R + 0.0026, L / 2 - 0.06, L / 2, 28, 'x', (0, R, 0), chanfro=0.0008)      # bolsa
    img = Image.new('RGB', (1024, 64), (226, 226, 220)); d = ImageDraw.Draw(img)
    for x in (100, 600): d.text((x, 20), 'ÁGUA FRIA  25 mm  PN 7,5  NBR', fill=(30, 40, 120), font=fonte(26))
    mat_imagem('marca_pvc', img, 0.4)
    anel(p, 'marca_pvc', R, R + 0.0003, -0.3, 0.3, 28, 'x', (0, R, 0)); p.uv['marca_pvc'] = (lambda f: (lambda v, n: f(v, n)[:, ::-1] * [1, 1]))(uv_cilindro(-0.3, 0.3, 'x', (0, R, 0)))
    # conexoes soltas ao lado: cotovelo e T
    q = P(); varrer(q, 'pvc', circ(R + 0.003, 20), [(0, 0, 0), (0.04, 0, 0), (0.055, 0, 0.015), (0.06, 0, 0.04), (0.06, 0, 0.08)])
    p.merge(q, trimesh.transformations.translation_matrix([-0.2, R + 0.003, 0.13]))
    q = P(); anel(q, 'pvc', R, R + 0.003, -0.04, 0.04, 20, 'x'); anel(q, 'pvc', R, R + 0.003, 0.0, 0.045, 20, 'z')
    p.merge(q, trimesh.transformations.translation_matrix([0.15, R + 0.003, 0.11]))


@item('lona', 'Lona dobrada', 'loot', 'materiais', recurso='material', valor=2, peso_kg=2.5, empilha=2, celulas=[2, 2], fase=1,
      onde=['armazem', 'fazenda', 'garagem', 'parque_trailers', 'posto'], efeito='cobre telhado quebrado, barraca, estufa e coletor de chuva (4 × 3 m)')
def lona(M):
    p = M.base; X, Z = 0.21, 0.16
    for k in range(5):                                                            # camadas dobradas, com borda abaulada
        y = 0.012 + k * 0.012; dx = 0.004 * (k % 2)
        fofo(p, 'lona_azul', dx, y, 0.0, X - k * 0.002, 0.007, Z - 0.002 * (k % 3), 0.15, 0.08, (12, 28))
    for xs in (-1, 1): fofo(p, 'lona_azul', xs * (X - 0.004), 0.036, 0.0, 0.012, 0.03, Z, 0.4, 0.1, (12, 20))  # dobras dos lados
    for zz in (-Z + 0.025, Z - 0.025):                                             # ilhoses de aluminio na borda de cima
        for x in (-X + 0.03, X - 0.03):
            anel(p, 'aco_polido', 0.005, 0.009, 0.068, 0.0705, 16, 'y', (x, 0, zz))
    for zz in (-0.06, 0.06):                                                       # cordinha amarrando
        _torcido(p, 'corda', [(-X - 0.01, 0.0, zz), (-X - 0.012, 0.04, zz), (-X + 0.02, 0.074, zz), (X - 0.02, 0.074, zz), (X + 0.012, 0.04, zz), (X + 0.01, 0.0, zz)], 0.003)


@item('trapos', 'Trapos amarrados', 'loot', 'materiais', recurso='material', valor=1, peso_kg=0.3, empilha=10, celulas=[1, 1], fase=1,
      onde=['casas', 'lavanderia', 'hotel', 'motel', 'garagem'], efeito='curativo, tocha, filtro, remendo e pavio de molotov',
      obtem_de=[{'desmontar': 'roupas', 'qtd': 3}, {'desmontar': 'cama_solteiro', 'qtd': 2}, {'desmontar': 'cama_casal', 'qtd': 3}])
def trapos(M):
    p = M.base
    # tres panos dobrados e amassados (camisa xadrez, lencol bege, flanela cinza), amarrados com uma tira
    for mat, (cx, cy, cz, a, b, c, rx), sd in (('trapo_xadrez', (0.0, 0.022, 0.0, 0.085, 0.022, 0.065, 0.05), 1),
                                              ('trapo_bege', (0.012, 0.05, 0.006, 0.072, 0.016, 0.056, -0.08), 2),
                                              ('trapo_cinza', (-0.012, 0.071, -0.004, 0.06, 0.011, 0.048, 0.1), 3)):
        fofo(p, mat, cx, cy, cz, a, b, c, 0.35, 0.22, (16, 24), rot_x=rx); _amassar(p, mat, 0.0035, 70.0, sd)
    for xs in (-1, 1):                                                               # pontas que escapam da dobra
        p.hull('trapo_xadrez', [(xs * 0.08, 0.01, 0.02), (xs * 0.125, 0.0, 0.035), (xs * 0.13, 0.002, 0.07), (xs * 0.085, 0.016, 0.06), (xs * 0.1, 0.004, 0.05)])
    p.hull('trapo_cinza', [(-0.02, 0.07, 0.04), (0.02, 0.065, 0.05), (0.01, 0.02, 0.09), (-0.03, 0.03, 0.085), (0.0, 0.05, 0.075)])
    t = np.linspace(0, 2 * math.pi, 30)
    for x in (-0.035,):
        pts = np.stack([np.full_like(t, x) + 0.004 * np.sin(3 * t), 0.042 + 0.046 * np.sin(t), 0.07 * np.cos(t)], 1)
        varrer(p, 'trapo_bege', Polygon([(-0.007, -0.0013), (0.007, -0.0013), (0.007, 0.0013), (-0.007, 0.0013)]), pts)
    fofo(p, 'trapo_bege', -0.035, 0.09, 0.0, 0.013, 0.009, 0.012, 0.5, 0.5, (8, 10))                     # no
    for zs in (-1, 1): p.hull('trapo_bege', [(-0.035, 0.09, 0.0), (-0.03, 0.092, zs * 0.03), (-0.04, 0.086, zs * 0.045), (-0.033, 0.088, zs * 0.01)])


@item('couro', 'Retalho de couro', 'loot', 'materiais', recurso='material', valor=1, peso_kg=0.5, empilha=6, celulas=[2, 1], fase=2,
      onde=['casas', 'fazenda', 'mansao', 'concessionaria', 'cinema'], efeito='protetor de braço anti-mordida, coldre, alças e botas',
      obtem_de=[{'desmontar': 'poltrona', 'qtd': 2}, {'desmontar': 'sofa', 'qtd': 3}, {'desmontar': 'mesa_booth', 'qtd': 2}])
def couro(M):
    p = M.base
    pts = [(-0.14, -0.06), (-0.08, -0.08), (0.02, -0.07), (0.12, -0.09), (0.15, -0.02), (0.13, 0.06), (0.05, 0.08), (-0.06, 0.07), (-0.13, 0.04)]
    m = trimesh.creation.extrude_polygon(Polygon(pts), 0.003); m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2], -m.vertices[:, 1]], 1)
    m = m.subdivide().subdivide(); v = m.vertices; v[:, 1] += 0.012 * np.sin(v[:, 0] * 20) * np.clip(v[:, 2] / 0.08, 0, 1) + 0.002
    p.add('couro', m)
    # segunda tira enrolada
    t = np.linspace(0, 3 * 2 * math.pi, 60); r = 0.012 + 0.0011 * t
    pts = np.stack([0.05 + np.zeros_like(t), 0.03 + r * np.sin(t), -0.04 + r * np.cos(t)], 1)
    for a, b in zip(pts[:-1], pts[1:]): p.seg('couro', a, b, 0.04, 0.0025)


@item('carvao', 'Saco de carvão', 'loot', 'combustivel', recurso='combustivel', valor=3, peso_kg=3.0, empilha=1, celulas=[2, 2], fase=2,
      onde=['supermercado', 'posto', 'casas', 'diner', 'armazem'], efeito='combustível da forja e do defumador; carvão moído vai no filtro de água',
      obtem_de=[{'fazer': 'fogueira', 'qtd': 1}])
def carvao(M):
    p = M.base; X, Z = 0.17, 0.11
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(200, 194, 170)); d.rectangle([0, h * 0.06, w, h * 0.32], fill=(20, 20, 20))
        texto_c(d, (w / 2, h * 0.19), 'BRASA BOA', 46, (240, 120, 20), larg=w - 20); texto_c(d, (w / 2, h * 0.45), 'CARVÃO VEGETAL', 30, (20, 20, 20), larg=w - 20)
        texto_c(d, (w / 2, h * 0.58), '3 kg', 54, (20, 20, 20))
        for i in range(6): d.polygon([(30 + i * 36, h * 0.85), (50 + i * 36, h * 0.75), (66 + i * 36, h * 0.86), (44 + i * 36, h * 0.93)], fill=(30, 30, 30))
    mat_imagem('rot_carvao', rotulo_caixa([frente, frente, lambda d, w, h: d.rectangle([0, 0, w, h], fill=(200, 194, 170)), lambda d, w, h: d.rectangle([0, 0, w, h], fill=(200, 194, 170))]), 0.85)
    fofo(p, 'rot_carvao', 0.0, 0.06, 0.0, X, 0.06, Z, 0.25, 0.15, (16, 28)); _amassar(p, 'rot_carvao', 0.003, 50.0, 4)
    p.uv['rot_carvao'] = uv_atlas(-X, X, 0.0, 0.12, -Z, Z, frente='y')
    p.hull('saco_rafia', [(X - 0.01, 0.01, -Z + 0.01), (X - 0.01, 0.01, Z - 0.01), (X - 0.01, 0.1, -Z + 0.02), (X - 0.01, 0.1, Z - 0.02),
                          (X + 0.06, 0.004, -Z + 0.02), (X + 0.06, 0.004, Z - 0.02), (X + 0.06, 0.012, -Z + 0.02), (X + 0.06, 0.012, Z - 0.02)])   # boca dobrada
    for z in np.linspace(-Z + 0.03, Z - 0.03, 7): p.seg('aco_polido', (X + 0.002, 0.03, z), (X + 0.002, 0.09, z), 0.0012, 0.003)        # grampos
    rng = np.random.default_rng(8)
    for i in range(6):                                                              # pedras que cairam
        c = (X + 0.08 + rng.uniform(0, 0.06), 0.012, rng.uniform(-0.08, 0.08))
        p.hull('carvao', c + rng.uniform(-0.016, 0.016, (8, 3)) * [1, 0.6, 1] + [0, 0.004, 0])


@item('pedras', 'Punhado de pedras', 'loot', 'materiais', recurso='material', valor=1, peso_kg=2.0, empilha=10, celulas=[1, 1], fase=1,
      onde=['rua', 'parque', 'fazenda', 'casa_barcos', 'serraria'], efeito='fogueira, forno de barro, peso de armadilha e muro de pedra')
def pedras(M):
    p = M.base; rng = np.random.default_rng(21)
    for i, (x, z, s) in enumerate(((-0.03, 0.0, 1.0), (0.035, 0.015, 0.8), (0.0, -0.04, 0.7), (0.01, 0.04, 0.6), (-0.05, 0.045, 0.5))):
        fofo(p, 'pedra_rio' if i % 2 else 'pedra_escura', x, 0.025 * s, z, 0.038 * s, 0.026 * s, 0.03 * s, 0.6, 0.7, (12, 16))


@item('tijolo', 'Tijolos', 'loot', 'materiais', recurso='material', valor=1, peso_kg=2.4, empilha=6, celulas=[1, 1], fase=2,
      onde=['fabrica', 'ruinas', 'casas', 'armazem'], efeito='fogão de tijolo, forno comunitário, forja e muros',
      obtem_de=[{'desmontar': 'ruina', 'qtd': 6}])
def tijolo(M):
    p = M.base
    for k, (x, y, a) in enumerate(((0.0, 0.0, 0.0), (0.0, 0.057, 0.12))):
        q = P(); X, H, Z = 0.095, 0.057, 0.045
        q.cham('tijolo', -X, X, 0.0, H, -Z, Z, 0.004)
        for cx in (-0.05, 0.0, 0.05): cyl_eixo(q, 'carvao', 0.011, H - 0.0005, H + 0.0004, 'y', (cx, 0, 0), 12)  # furos
        q.hull('cimento_saco', [(-X - 0.001, 0.0, -Z), (-X - 0.001, 0.0, Z), (-X + 0.03, 0.0, Z + 0.001), (-X - 0.001, 0.012, 0.0)])   # argamassa velha
        p.merge(q, trimesh.transformations.translation_matrix([x, y, 0]) @ _rot(a, [0, 1, 0]))
    # meio tijolo quebrado ao lado
    p.hull('tijolo', [(0.12, 0.0, -0.04), (0.17, 0.0, -0.04), (0.18, 0.0, 0.03), (0.12, 0.0, 0.045), (0.12, 0.05, -0.04), (0.16, 0.055, -0.035), (0.15, 0.05, 0.04), (0.12, 0.055, 0.045)])


def _mat_cimento():
    if 'rot_cimento' in MATS: return
    X = 0.3
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(200, 196, 186)); d.rectangle([0, h * 0.1, w, h * 0.42], fill=(170, 20, 20))
        texto_c(d, (w / 2, h * 0.2), 'ROCHEDO', 52, (255, 255, 255), larg=w - 20); texto_c(d, (w / 2, h * 0.34), 'CIMENTO CP II', 28, (255, 255, 255), larg=w - 20)
        texto_c(d, (w / 2, h * 0.6), '25 kg', 64, (30, 30, 30)); texto_c(d, (w / 2, h * 0.8), 'USO GERAL', 26, (30, 30, 30))
    mat_imagem('rot_cimento', rotulo_caixa([frente, frente, lambda d, w, h: d.rectangle([0, 0, w, h], fill=(200, 196, 186)), lambda d, w, h: d.rectangle([0, 0, w, h], fill=(200, 196, 186))]), 0.9)


@item('cimento', 'Saco de cimento 25 kg', 'loot', 'materiais', recurso='material', valor=3, peso_kg=25.0, empilha=1, celulas=[3, 2], fase=4,
      onde=['armazem', 'fabrica', 'garagem_vertical', 'ruinas'], efeito='muralha de concreto, cisterna, reforma de prédios (fase 4)')
def cimento(M):
    p = M.base; X, Z = 0.3, 0.2; _mat_cimento()
    fofo(p, 'rot_cimento', 0.0, 0.055, 0.0, X, 0.055, Z, 0.2, 0.08, (16, 28)); _amassar(p, 'rot_cimento', 0.0025, 30.0, 5); p.uv['rot_cimento'] = uv_atlas(-X, X, 0.0, 0.11, -Z, Z, frente='y')
    p.hull('cimento_saco', [(-X + 0.02, 0.1, Z - 0.06), (-X + 0.07, 0.1, Z - 0.03), (-X + 0.04, 0.112, Z - 0.04), (-X + 0.06, 0.105, Z - 0.07)])   # valvula


@item('linha_pesca', 'Carretel de linha e anzóis', 'loot', 'utensilios', recurso='material', valor=1, peso_kg=0.1, empilha=6, celulas=[1, 1], fase=1,
      onde=['casa_barcos', 'casas', 'supermercado', 'parque_trailers'], efeito='vara de pesca, armadilha de linha e costura de ferimento')
def linha_pesca(M):
    p = M.base; R = 0.035
    torno(p, 'plastico_preto', [(R, 0.0), (R, 0.003), (0.014, 0.003), (0.014, 0.02), (R, 0.02), (R, 0.023), (0.008, 0.023), (0.008, 0.0)], 32)
    anel(p, 'linha_verde', 0.014, 0.03, 0.003, 0.02, 32)
    for y in np.linspace(0.004, 0.019, 8): anel(p, 'linha_verde', 0.0299, 0.0303, y, y + 0.0008, 32)
    varrer(p, 'linha_verde', circ(0.0004, 5), [(0.03, 0.012, 0.0), (0.05, 0.004, 0.02), (0.07, 0.0006, 0.03)])
    # cartela com 3 anzois
    p.box('papelao', 0.045, 0.085, 0.0, 0.001, -0.06, -0.015)
    for k in range(3):
        z = -0.052 + k * 0.014
        pts = [(0.05, 0.0015, z), (0.072, 0.0015, z), (0.078, 0.0015, z + 0.004), (0.075, 0.0015, z + 0.008), (0.07, 0.0015, z + 0.006)]
        varrer(p, 'aco_polido', circ(0.0005, 5), pts)
    torno(p, 'plastico_vermelho', [(0.0, 0.0), (0.006, 0.002), (0.008, 0.006), (0.006, 0.01), (0.0, 0.012)], 16, 'y', (-0.05, 0, 0.03))    # boia
    torno(p, 'plastico_branco', [(0.0, 0.012), (0.006, 0.014), (0.0, 0.02)], 16, 'y', (-0.05, -0.0, 0.03))


@item('alcool', 'Garrafa de álcool 70 %', 'loot', 'remedios', recurso='remedios', valor=1, peso_kg=1.0, empilha=2, celulas=[1, 2], fase=1,
      onde=['supermercado', 'clinica', 'casas', 'posto'], efeito='desinfeta ferimento, acende fogo, combustível da lamparina e do molotov')
def alcool(M):
    p = M.base; X, Z, H = 0.045, 0.03, 0.22
    img = Image.new('RGB', (512, 512), (240, 240, 236)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 512, 110], fill=(20, 80, 170)); texto_c(d, (256, 55), 'LIMPOMAX', 62, (255, 255, 255))
    texto_c(d, (256, 230), 'ÁLCOOL 70°', 84, (20, 80, 170)); texto_c(d, (256, 340), 'ETÍLICO HIDRATADO', 32, (30, 30, 30))
    texto_c(d, (256, 440), '1 LITRO · INFLAMÁVEL', 30, (180, 20, 20)); mat_imagem('rot_alcool', img, 0.5)
    q = p; q.cham('plastico_transp', -X, X, 0.0, H * 0.75, -Z, Z, 0.012)
    q.hull('plastico_transp', [(x, H * 0.75 - 0.01, z) for x in (-X + 0.004, X - 0.004) for z in (-Z + 0.004, Z - 0.004)] + [(x, H * 0.9, z) for x in (-0.014, 0.014) for z in (-0.014, 0.014)])
    torno(q, 'plastico_transp', [(0.0125, H * 0.9 - 0.004), (0.0125, H * 0.93)], 20)
    torno(q, 'tinta_vermelha', [(0.0145, H * 0.92), (0.0145, H * 0.97), (0.012, H * 0.975)], 20)
    q.cham('agua', -X + 0.002, X - 0.002, 0.002, H * 0.55, -Z + 0.002, Z - 0.002, 0.01)
    q.box('rot_alcool', -X + 0.004, X - 0.004, 0.03, 0.14, Z, Z + 0.0005)
    q.uv['rot_alcool'] = lambda v, n: np.stack([(v[:, 0] + X) / (2 * X), (v[:, 1] - 0.03) / 0.11], 1)


@item('pedra_amolar', 'Pedra de amolar', 'loot', 'ferramentas', recurso='ferramenta', valor=2, peso_kg=0.4, empilha=1, celulas=[1, 1], fase=1,
      onde=['casas', 'fazenda', 'serraria', 'casa_de_campo'], efeito='recupera o fio de facas, facão, machado e lança (sem bancada)')
def pedra_amolar(M):
    p = M.base; X, Z = 0.1, 0.025
    p.cham('madeira_escura', -X - 0.015, X + 0.015, 0.0, 0.018, -Z - 0.01, Z + 0.01, 0.004)                  # base de madeira
    p.cham('esmeril', -X, X, 0.012, 0.032, -Z, Z, 0.002)
    p.cham('pedra', -X, X, 0.032, 0.042, -Z, Z, 0.0015)                                                       # lado fino
    for xs in (-1, 1): p.cham('borracha', xs * X - 0.012, xs * X + 0.012, -0.002, 0.004, -Z, Z, 0.002)
