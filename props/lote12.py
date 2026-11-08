# Lote 12: itens unicos de lazer (parque e casa de barcos, observatorio, piscina, pista de skate, minigolfe, concha acustica, drive-in).
# Executado por gerar_props.py (mesmas funcoes e materiais).
CORES.update({'casco_canoa': (110, 24, 8), 'laranja_boia': (190, 50, 4), 'azul_piscina': (20, 80, 130), 'agua_piscina': (40, 110, 110),
              'lona_listrada': (200, 196, 186), 'branco_tel': (230, 232, 230), 'lixa_skate': (24, 24, 26), 'verde_golfe': (14, 70, 22),
              'vermelho_flag': (150, 8, 6), 'preto_palco': (22, 22, 24), 'tela_som': (36, 36, 38), 'vinil_azul': (12, 44, 90), 'carta_ceu': (10, 14, 40)})
METALICOS.update({'branco_tel': (0.3, 0.35), 'preto_palco': (0.4, 0.45)})
FOSCOS.update({'laranja_boia': 0.5, 'lona_listrada': 0.85, 'lixa_skate': 0.98, 'verde_golfe': 0.9, 'tela_som': 0.95, 'vinil_azul': 0.4})
TEX_PROPRIAS += [('tela_som', 'tecido', 0.15, 512), ('lixa_skate', 'tecido', 0.1, 256)]

_rx12 = lambda ang, c=(0, 0, 0): trimesh.transformations.rotation_matrix(ang, [1, 0, 0], point=c)
_ry12 = lambda ang, c=(0, 0, 0): trimesh.transformations.rotation_matrix(ang, [0, 1, 0], point=c)
_rz12 = lambda ang, c=(0, 0, 0): trimesh.transformations.rotation_matrix(ang, [0, 0, 1], point=c)
_tr12 = lambda x, y, z: trimesh.transformations.translation_matrix([x, y, z])


def _listras(nome, cores, n=8, tam=(512, 512), vertical=True):
    img = Image.new('RGB', tam, cores[0]); d = ImageDraw.Draw(img); w = (tam[0] if vertical else tam[1]) / n
    for k in range(n):
        if k % 2: d.rectangle([k * w, 0, (k + 1) * w, tam[1]] if vertical else [0, k * w, tam[0], (k + 1) * w], fill=cores[1])
    mat_imagem(nome, img, 0.8)


# ---------------------------------------------------------------------------- CASA DE BARCOS / PARQUE
@item('canoa', 'Canoa no cavalete', 'mobilias', 'barcos', comodos=['casa_de_barcos', 'parque', 'quintal', 'garagem'], ambiente=True, colisao='caixa',
      interacao='atravessa o lago em silêncio (rota de fuga do parque)', desmonta={'madeira': 3})
def canoa(M):
    p = M.base; L, W, D = 2.4, 0.42, 0.34; y0 = 0.62
    secs = []
    for u in np.linspace(-1, 1, 25):
        s = math.sqrt(max(0.0, 1 - u ** 2)) ** 0.75; w = W * max(s, 0.02); d = D * (0.7 + 0.3 * s); x = u * L
        ring = [(x, y0 + d - d * math.sin(a) * 1.0 + (0.08 * u ** 4), w * math.cos(a)) for a in np.linspace(0, math.pi, 13)]
        secs.append(ring)
    V = np.array([pt for r in secs for pt in r]); n = 13; F = []
    for i in range(len(secs) - 1):
        for j in range(n - 1):
            a, b, c, d_ = i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j
            F += [[a, d_, c], [a, c, b]]
    casco = trimesh.Trimesh(V, F, process=True)
    inner = casco.copy(); inner.vertices = inner.vertices + 0.0; inner.vertices[:, 1] += 0.012; inner.vertices[:, 2] *= 0.96; inner.invert()
    p.add('casco_canoa', casco); p.add('madeira_crua', inner)
    for u in (-0.95, 0.95):
        x = u * L; s = 0.55; p.box('madeira', x - 0.02, x + 0.02, y0 + D * 0.8, y0 + D, -W * 0.25, W * 0.25) if False else None
    for zs in (-1, 1):                                                                     # amurada
        pts = [(u * L, y0 + D + 0.08 * u ** 4 + 0.005, zs * W * max(math.sqrt(max(0.0, 1 - u ** 2)) ** 0.75, 0.02)) for u in np.linspace(-0.98, 0.98, 21)]
        for a, b in zip(pts[:-1], pts[1:]): p.seg('madeira', a, b, 0.03, 0.02)
    for x in (-0.7, 0.0, 0.7):                                                              # bancos
        s = math.sqrt(1 - (x / L) ** 2) ** 0.75; p.cham('madeira', x - 0.1, x + 0.1, y0 + D - 0.06, y0 + D - 0.03, -W * s, W * s, 0.005)
    for x in (-1.1, 1.1):                                                                   # cavaletes
        for zs in (-1, 1): p.seg('madeira_escura', (x, 0.0, zs * 0.4), (x, y0 + 0.02, zs * 0.12), 0.06, 0.05)
        p.cham('madeira_escura', x - 0.04, x + 0.04, y0 - 0.02, y0 + 0.03, -0.3, 0.3, 0.006)
    p.seg('madeira', (-0.4, y0 + D - 0.02, -0.15), (1.1, y0 + D + 0.05, 0.12), 0.035, 0.025)          # remo deitado
    p.hull('madeira', [(1.1, y0 + D + 0.05, 0.05), (1.1, y0 + D + 0.05, 0.19), (1.5, y0 + D + 0.08, 0.06), (1.5, y0 + D + 0.08, 0.2), (1.1, y0 + D + 0.065, 0.05), (1.5, y0 + D + 0.095, 0.2)])


@item('remo', 'Remo de madeira', 'loot', 'armas', recurso='arma', valor=2, peso_kg=1.4, empilha=1, arma=True, dano=14, alcance_m=1.6,
      onde=['casa_de_barcos', 'parque', 'garagem'], efeito='arma corpo a corpo longa (empurra zumbis); rema a canoa', pega=[-0.4, 0.02, 0])
def remo(M):
    p = M.base
    cyl_eixo(p, 'madeira', 0.017, -0.75, 0.3, 'x', (0, 0.02, 0), 12)
    p.hull('madeira', [(-0.78, 0.0, -0.05), (-0.78, 0.04, -0.05), (-0.78, 0.0, 0.05), (-0.78, 0.04, 0.05), (-0.73, 0.0, -0.05), (-0.73, 0.04, 0.05)])
    pa = Polygon([(0.3, -0.03), (0.45, -0.085), (0.75, -0.09), (0.82, -0.06), (0.82, 0.06), (0.75, 0.09), (0.45, 0.085), (0.3, 0.03)])
    m = trimesh.creation.extrude_polygon(pa, 0.014); m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2] + 0.013, m.vertices[:, 1]], 1)
    if m.volume < 0: m.invert()
    p.add('madeira', m); p.box('vermelho_flag', 0.7, 0.82, 0.0125, 0.0285, -0.09, 0.09) if False else p.hull('vermelho_flag', [(0.74, 0.0124, -0.088), (0.74, 0.0124, 0.088), (0.82, 0.0124, -0.06), (0.82, 0.0124, 0.06), (0.74, 0.0286, -0.088), (0.74, 0.0286, 0.088), (0.82, 0.0286, -0.06), (0.82, 0.0286, 0.06)])


@item('boia_salva_vidas', 'Boia salva-vidas na parede', 'mobilias', 'barcos', montagem='wall', altura_sugerida_m=1.5, comodos=['casa_de_barcos', 'piscina', 'parque'],
      ambiente=True, colisao='nenhuma', coleta={'recurso': 'material', 'total': 1, 'ferramenta': 'nenhuma', 'segundos_por_unidade': 2}, observacao='corda: 10 m')
def boia_salva_vidas(M):
    p = M.base; R, r = 0.3, 0.07
    t = trimesh.creation.torus(major_radius=R, minor_radius=r, major_sections=40, minor_sections=16)
    # faixas brancas em 4 setores
    for k in range(8):
        a0 = k / 8 * 2 * math.pi; part = t.slice_plane([0, 0, 0], [-math.sin(a0), math.cos(a0), 0]) if False else None
    v = t.vertices; ang = np.arctan2(v[:, 1], v[:, 0]); sector = ((ang + math.pi) / (math.pi / 4)).astype(int) % 8
    for mat, cond in (('laranja_boia', 0), ('plastico_branco', 1)):
        f = t.faces[(sector[t.faces].max(1) % 2 == cond) & (sector[t.faces].min(1) == sector[t.faces].max(1))]
        if len(f): m = trimesh.Trimesh(v, f, process=True); m.remove_unreferenced_vertices(); m.apply_translation([0, 0, r + 0.02]); m.apply_translation([0, R + r, 0]); p.add(mat, m)
    for k in range(4):
        a = k / 4 * 2 * math.pi + math.pi / 8; c = (0, R + r, r + 0.02)
        p.seg('corda' if 'corda' in CORES else 'lona', (R * math.cos(a), R + r + R * math.sin(a), 2 * r + 0.02), ((R) * math.cos(a + math.pi / 4), R + r + R * math.sin(a + math.pi / 4), 2 * r + 0.02), 0.012) if False else None
    for k in range(16):
        a = k / 16 * 2 * math.pi; b = (k + 1) / 16 * 2 * math.pi; RR = R + r + 0.005
        p.seg('lona', (RR * math.cos(a), R + r + RR * math.sin(a), r + 0.02), (RR * math.cos(b), R + r + RR * math.sin(b), r + 0.02), 0.012)
    p.cyl('aco', 0.012, 2 * R + 0.1, 2 * R + 2 * r + 0.06, x=0, z=0.03, sec=8) if False else p.seg('aco', (0, 2 * R + 2 * r - 0.02, 0.0), (0, 2 * R + 2 * r - 0.02, 0.12), 0.02)


@item('colete_salva_vidas', 'Colete salva-vidas', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=0.8, empilha=1, onde=['casa_de_barcos', 'piscina', 'parque'],
      efeito='flutua (atravessa o lago); +5 de proteção leve', pega=[0, 0.08, 0])
def colete_salva_vidas(M):
    p = M.base
    for xs in (-1, 1):
        fofo(p, 'laranja_boia', xs * 0.12, 0.04, 0.0, 0.1, 0.04, 0.24, e1=0.3, e2=0.35)
        p.box('plastico_preto', xs * 0.12 - 0.08, xs * 0.12 + 0.08, 0.078, 0.082, -0.06, -0.04)
    fofo(p, 'laranja_boia', 0.0, 0.03, -0.32, 0.18, 0.03, 0.08, e1=0.3, e2=0.35)
    for z in (-0.1, 0.05, 0.18): p.box('plastico_preto', -0.24, 0.24, 0.074, 0.079, z - 0.015, z + 0.015); p.cham('plastico_preto', -0.02, 0.02, 0.07, 0.09, z - 0.025, z + 0.025, 0.004)
    p.box('lona', -0.22, 0.22, 0.0, 0.006, 0.25, 0.27)


@item('balanco', 'Balanço de parquinho', 'mobilias', 'barcos', comodos=['parque', 'escolinha', 'quintal'], ambiente=True, colisao='caixa', modulo_m=2.0,
      observacao='range com o vento à noite (som de ambiente)', desmonta={'sucata': 3, 'corda': 1})
def balanco(M):
    p = M.base; X, H = 1.3, 2.2
    for xs in (-1, 1):
        for zs in (-1, 1): p.seg('tinta_azul', (xs * X, 0.0, zs * 0.7), (xs * X, H, 0.0), 0.06)
    cyl_eixo(p, 'tinta_azul', 0.04, -X - 0.05, X + 0.05, 'x', (0, H, 0), 14)
    for k, x in enumerate((-0.55, 0.55)):
        ang = 0.0 if k == 0 else 0.18
        for dx in (-0.2, 0.2):
            topo = (x + dx, H - 0.03, 0.0); fim = (x + dx, H - 1.75 * math.cos(ang), 1.75 * math.sin(ang))
            for t in np.linspace(0, 1, 18)[:-1]:
                a = np.array(topo) + (np.array(fim) - np.array(topo)) * t; b = np.array(topo) + (np.array(fim) - np.array(topo)) * (t + 1 / 17)
                p.seg('aco', tuple(a), tuple(b), 0.008, 0.015)
            anel(p, 'aco', 0.015, 0.022, -0.005, 0.005, 10, 'x', (x + dx, H - 0.035, 0))
        s = P(); s.cham('borracha', -0.24, 0.24, -0.015, 0.0, -0.1, 0.1, 0.01); s.cham('borracha', -0.26, 0.26, -0.03, -0.015, -0.11, 0.11, 0.006)
        p.merge(s, _tr12(x, H - 1.75 * math.cos(ang), 1.75 * math.sin(ang)) @ _rx12(ang))
    for k in range(10): p.box('terra' if 'terra' in CORES else 'papelao', -0.8 + (k % 5) * 0.08, -0.74 + (k % 5) * 0.08, 0.0, 0.003, -0.25 + (k // 5) * 0.12, -0.15 + (k // 5) * 0.12)


@item('barraca_camping', 'Barraca de camping abandonada', 'mobilias', 'barcos', comodos=['parque', 'quintal', 'rua', 'abrigo'], ambiente=True, colisao='caixa',
      conteiner=True, slots=3, saque=['roupas', 'comida', 'remedios'], deitar=True, observacao='alguém acampou aqui fugindo da cidade')
def barraca_camping(M):
    p = M.base; X, Z, H = 1.0, 0.75, 1.1
    for zs in (-1, 1):
        h = trimesh.convex.convex_hull(np.array([(-X, 0.0, zs * Z), (X, 0.0, zs * Z), (-X + 0.05, H, 0.0), (X - 0.05, H, 0.0), (-X, 0.0, zs * (Z - 0.012)), (X, 0.0, zs * (Z - 0.012)), (-X + 0.05, H - 0.015, 0.0), (X - 0.05, H - 0.015, 0.0)]))
        p.add('tecido_verde' if 'tecido_verde' in CORES else 'lona', h)
    fundo = trimesh.convex.convex_hull(np.array([(-X, 0, -Z), (-X, 0, Z), (-X + 0.05, H, 0), (-X + 0.01, 0, -Z), (-X + 0.01, 0, Z), (-X + 0.06, H, 0)]))
    p.add('lona', fundo)
    for zs in (-1, 1):                                                                     # porta enrolada aberta na frente
        p.hull('lona', [(X - 0.02, 0.0, zs * Z), (X, 0.0, zs * Z * 0.25), (X - 0.05, H - 0.02, 0.0), (X - 0.02, 0.0, zs * Z * 0.97), (X - 0.01, 0.0, zs * Z * 0.25)])
    cyl_eixo(p, 'lona', 0.045, -0.22, 0.22, 'z', (X - 0.02, H * 0.72, 0), 12) if False else None
    for x in (-X + 0.05, X - 0.05): p.cyl('aco', 0.01, 0.0, H + 0.08, x=x, z=0.0, sec=8)
    for x in (-X - 0.3, X + 0.35):
        for zs in (-1, 1): p.seg('corda' if 'corda' in CORES else 'aco', (x * 0.0 + (X - 0.05 if x > 0 else -X + 0.05), H + 0.06, 0.0), (x, 0.0, zs * 0.35), 0.006)
    fofo(p, 'tecido_vermelho' if 'tecido_vermelho' in CORES else 'cobertor', -0.2, 0.06, 0.1, 0.7, 0.06, 0.3, e1=0.4, e2=0.4)   # saco de dormir aberto
    fofo(p, 'tecido_mochila' if 'tecido_mochila' in CORES else 'lona', 0.55, 0.18, -0.4, 0.15, 0.18, 0.1, e1=0.5, e2=0.5)
    for k in range(3): torno(p, 'lata', [(0.035, 0.0), (0.035, 0.1), (0.033, 0.105)], 14, 'y', (1.25 + k * 0.08, 0, 0.3 - k * 0.05))


@item('guarda_sol', 'Guarda-sol fechado com base', 'mobilias', 'piscina', comodos=['piscina', 'parque', 'quintal', 'diner'], ambiente=True, colisao='caixa',
      desmonta={'tecido': 2, 'sucata': 1})
def guarda_sol(M):
    p = M.base
    torno(p, 'plastico_branco', [(0.0, 0.0), (0.25, 0.0), (0.25, 0.06), (0.06, 0.12), (0.04, 0.14), (0.0, 0.14)], 24)
    p.cyl('aco_polido', 0.02, 0.1, 2.3, sec=12)
    _listras('lona_sol', [(220, 216, 206), (20, 90, 150)], n=12)
    perf = [(0.0, 1.0), (0.12, 1.15), (0.14, 1.6), (0.1, 2.05), (0.04, 2.18), (0.0, 2.22)]
    m = P(); torno(m, 'lona_sol', perf, 12); p.merge(m)
    p.uv['lona_sol'] = lambda v, n: np.stack([(np.arctan2(v[:, 2], v[:, 0]) / (2 * math.pi) + 0.5), v[:, 1] / 2.3], 1)
    for k in range(12): a = k / 12 * 2 * math.pi; p.seg('aco', (0.02 * math.cos(a), 2.18, 0.02 * math.sin(a)), (0.13 * math.cos(a), 1.6, 0.13 * math.sin(a)), 0.006)
    p.cyl('plastico_branco', 0.025, 2.22, 2.3, sec=12); p.sphere('plastico_branco', 0.03, 0, 2.31, 0)
    p.box('lona', -0.05, 0.05, 1.5, 1.53, 0.12, 0.16)


# ---------------------------------------------------------------------------- OBSERVATORIO
@item('telescopio', 'Telescópio refrator no tripé', 'mobilias', 'observatorio', comodos=['observatorio', 'mansao', 'torre_vigia', 'abrigo'], ambiente=True, colisao='caixa',
      estacao='vigia de longe (vê hordas e fumaça de outros sobreviventes a 1 km)', interacao='olhar pela ocular (zoom 8x)')
def telescopio(M):
    p = M.base
    for k in range(3):
        a = k / 3 * 2 * math.pi; p.seg('madeira', (0.0, 1.05, 0.0), (0.55 * math.cos(a), 0.0, 0.55 * math.sin(a)), 0.045, 0.03)
        p.cham('borracha', 0.55 * math.cos(a) - 0.03, 0.55 * math.cos(a) + 0.03, 0.0, 0.02, 0.55 * math.sin(a) - 0.03, 0.55 * math.sin(a) + 0.03, 0.006)
        p.seg('aco', (0.0, 0.45, 0.0), (0.3 * math.cos(a), 0.45, 0.3 * math.sin(a)), 0.012)
    torno(p, 'aco_pintado', [(0.0, 0.42), (0.18, 0.42), (0.19, 0.44), (0.0, 0.44)], 6)
    torno(p, 'branco_tel', [(0.0, 1.0), (0.09, 1.02), (0.08, 1.12), (0.0, 1.14)], 20)
    t = P(); ang = 0.55
    torno(t, 'branco_tel', [(0.0, -0.6), (0.06, -0.6), (0.06, 0.55), (0.075, 0.56), (0.075, 0.72), (0.07, 0.72), (0.06, 0.6)], 28, 'x', (0, 0, 0), fechar=False)
    torno(t, 'vidro_escuro', [(0.0, 0.6), (0.06, 0.6)], 28, 'x', (0, 0, 0))
    torno(t, 'esmalte_escuro', [(0.0, -0.7), (0.025, -0.7), (0.025, -0.6), (0.0, -0.6)], 16, 'x', (0, 0, 0))
    torno(t, 'esmalte_escuro', [(0.0, -0.78), (0.016, -0.78), (0.018, -0.7), (0.0, -0.7)], 12, 'x', (0, 0, 0))
    for x in (-0.15, 0.25): anel(t, 'aco_pintado', 0.06, 0.072, x - 0.02, x + 0.02, 24, 'x', (0, 0, 0))
    torno(t, 'branco_tel', [(0.0, -0.1), (0.018, -0.1), (0.018, 0.25), (0.0, 0.25)], 12, 'x', (0, 0.1, 0))   # buscador
    t.seg('aco_pintado', (-0.05, 0.06, 0), (-0.05, 0.1, 0), 0.015); t.seg('aco_pintado', (0.2, 0.06, 0), (0.2, 0.1, 0), 0.015)
    cyl_eixo(t, 'esmalte_escuro', 0.012, -0.1, 0.12, 'z', (-0.45, -0.07, 0), 8); torno(t, 'esmalte_escuro', [(0.025, 0.12), (0.025, 0.14)], 14, 'z', (-0.45, -0.07, 0))
    p.merge(t, _tr12(0.0, 1.22, 0.0) @ _rz12(ang))
    p.cham('aco_pintado', -0.06, 0.06, 1.12, 1.2, -0.07, 0.07, 0.01)
    p.seg('aco', (0.0, 1.16, 0.0), (-0.3, 0.9, 0.15), 0.012)


@item('mapa_estrelas', 'Carta celeste na parede', 'mobilias', 'observatorio', montagem='wall', altura_sugerida_m=1.3, comodos=['observatorio', 'escolinha', 'biblioteca'],
      ambiente=True, colisao='nenhuma', observacao='as constelações servem de bússola à noite (sem GPS)')
def mapa_estrelas(M):
    p = M.base; W, H = 1.2, 0.85; rng = np.random.default_rng(81)
    img = Image.new('RGB', (1024, 724), (10, 16, 46)); d = ImageDraw.Draw(img)
    d.ellipse([60, 20, 964, 704], outline=(120, 140, 200), width=4); d.ellipse([200, 140, 824, 584], outline=(60, 80, 140), width=2)
    for k in range(9): a = k / 9 * math.pi; d.line([(512 - 452 * math.cos(a), 362 - 342 * math.sin(a)), (512 + 452 * math.cos(a), 362 + 342 * math.sin(a))], fill=(40, 56, 110), width=2)
    pts = [(rng.uniform(80, 944), rng.uniform(40, 684)) for _ in range(260)]
    for x, y in pts: r = rng.choice([1, 1, 2, 3]); d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 246, 220))
    for c in range(7):
        cx, cy = rng.uniform(200, 820), rng.uniform(140, 580); cs = [(cx + rng.uniform(-80, 80), cy + rng.uniform(-60, 60)) for _ in range(5)]
        d.line(cs, fill=(200, 180, 90), width=2)
        for x, y in cs: d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 240, 180))
    texto_c(d, (512, 700), 'CÉU DO HEMISFÉRIO SUL', 30, (200, 200, 230))
    mat_imagem('carta_ceu_arte', img, 0.6)
    p.cham('madeira_escura', -W / 2 - 0.03, W / 2 + 0.03, -0.03, H + 0.03, 0.0, 0.025, 0.006)
    p.box('carta_ceu_arte', -W / 2, W / 2, 0.0, H, 0.025, 0.027); p.uv['carta_ceu_arte'] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)
    p.box('vidro_prateleira' if 'vidro_prateleira' in CORES else 'vidro_escuro', -W / 2, W / 2, 0.0, H, 0.03, 0.032) if False else None


# ---------------------------------------------------------------------------- PISCINA
@item('espreguicadeira', 'Espreguiçadeira', 'mobilias', 'piscina', comodos=['piscina', 'quintal', 'hotel', 'motel'], deitar=True, colisao='caixa',
      barricada=True, desmonta={'sucata': 2})
def espreguicadeira(M):
    p = M.base; X, L = 0.32, 0.95; y = 0.32
    for xs in (-1, 1):
        p.seg('aco_polido', (xs * X, y, -L), (xs * X, y, 0.35), 0.022)
        p.seg('aco_polido', (xs * X, y, 0.35), (xs * X, y + 0.55, 0.85), 0.022)
        for z in (-L + 0.05, 0.25): p.seg('aco_polido', (xs * X, y, z), (xs * X, 0.0, z + (0.05 if z > 0 else -0.03)), 0.022)
        p.cyl('borracha', 0.016, 0.0, 0.02, x=xs * X, z=0.3, sec=8)
    for k in range(18):
        z = -L + 0.05 + k * 0.075; p.cham('vinil_azul', -X + 0.01, X - 0.01, y - 0.008, y + 0.008, z, z + 0.05, 0.006)
    for k in range(7):
        t = (k + 0.5) / 7; z = 0.35 + 0.5 * t; yy = y + 0.55 * t; p.seg('vinil_azul', (-X + 0.01, yy, z), (X - 0.01, yy, z), 0.05, 0.016)
    p.box('lona_listrada', -0.2, 0.2, y + 0.008, y + 0.012, -0.6, 0.2)                     # toalha esquecida


@item('cadeira_salva_vidas', 'Cadeira alta de salva-vidas', 'mobilias', 'piscina', comodos=['piscina', 'parque'], ambiente=True, colisao='caixa', sentar=True,
      estacao='vigia (vê 30 m em volta da piscina)', desmonta={'madeira': 4})
def cadeira_salva_vidas(M):
    p = M.base; H = 1.7
    for xs in (-1, 1):
        for zs in (-1, 1): p.seg('madeira_branca', (xs * 0.45, 0.0, zs * 0.5), (xs * 0.33, H, zs * 0.25), 0.07, 0.07)
    for k in range(6):
        y = 0.25 + k * 0.25; z = 0.5 - (y / H) * 0.25 + 0.02; xx = 0.45 - (y / H) * 0.12
        p.cham('madeira_branca', -xx, xx, y - 0.02, y + 0.02, z - 0.03, z + 0.03, 0.004)
    p.cham('madeira_branca', -0.38, 0.38, H, H + 0.05, -0.3, 0.3, 0.008)
    p.cham('madeira_branca', -0.38, 0.38, H + 0.05, H + 0.6, -0.3, -0.26, 0.008)
    for xs in (-1, 1): p.cham('madeira_branca', xs * 0.38 - 0.03, xs * 0.38 + 0.03, H + 0.05, H + 0.3, -0.3, 0.2, 0.006)
    for xs in (-1, 1): p.seg('madeira_branca', (xs * 0.45, 0.0, -0.5), (xs * 0.4, 0.5, 0.0), 0.05, 0.05)
    p.cyl('aco_polido', 0.02, H + 0.05, H + 1.2, x=0.33, z=-0.28, sec=8)
    _listras('lona_sv', [(200, 20, 16), (240, 240, 236)], n=8)
    torno(p, 'lona_sv', [(0.0, H + 1.0), (0.5, H + 1.0), (0.48, H + 1.05), (0.25, H + 1.15), (0.0, H + 1.2)], 16, 'y', (0.33, 0, -0.28))
    p.uv['lona_sv'] = lambda v, n: np.stack([(np.arctan2(v[:, 2] + 0.28, v[:, 0] - 0.33) / (2 * math.pi) + 0.5), (v[:, 1] - H - 1.0) * 4], 1)
    fofo(p, 'laranja_boia', 0.42, H + 0.25, 0.1, 0.03, 0.2, 0.08, e1=0.3, e2=0.3) if False else torno(p, 'laranja_boia', [(0.08, 0.0), (0.1, 0.0), (0.1, 0.03), (0.08, 0.03)], 20, 'x', (0.42, H + 0.25, 0.05))


@item('escada_piscina', 'Escada de piscina', 'mobilias', 'piscina', comodos=['piscina'], ambiente=True, colisao='nenhuma', pivo='borda da piscina (y=0 no chão)',
      desmonta={'sucata': 2})
def escada_piscina(M):
    p = M.base
    for xs in (-1, 1):
        x = xs * 0.25; pts = [(x, -1.2, 0.12), (x, 0.0, 0.12)] + [(x, 0.55 + 0.25 * math.sin(a), 0.12 - 0.35 * (1 - math.cos(a)) * 0.0 - 0.25 * (1 - math.cos(a))) for a in np.linspace(0, math.pi, 10)] + [(x, 0.55 - 0.1, -0.38)]
        pts = [(x, -1.2, 0.12), (x, 0.55, 0.12)] + [(x, 0.55 + 0.22 * math.sin(a), 0.12 - 0.22 * (1 - math.cos(a))) for a in np.linspace(0.15, math.pi, 10)] + [(x, 0.0, -0.32)]
        for a, b in zip(pts[:-1], pts[1:]): p.seg('aco_polido', a, b, 0.04)
        torno(p, 'aco_polido', [(0.0, 0.0), (0.045, 0.0), (0.035, 0.012)], 16, 'y', (x, 0, -0.32))
    for k in range(4):
        y = -0.25 - k * 0.27; p.cham('aco_polido', -0.24, 0.24, y - 0.015, y + 0.015, 0.05, 0.19, 0.005); p.box('plastico_preto', -0.2, 0.2, y + 0.015, y + 0.018, 0.07, 0.17)


@item('boia_piscina', 'Boia de piscina murcha', 'mobilias', 'piscina', comodos=['piscina', 'quintal', 'casas'], ambiente=True, colisao='nenhuma', **({'observacao': 'lembrança do último verão'}))
def boia_piscina(M):
    p = M.base
    t = trimesh.creation.torus(major_radius=0.35, minor_radius=0.12, major_sections=36, minor_sections=14)
    v = t.vertices.copy(); ang = np.arctan2(v[:, 1], v[:, 0])
    v[:, 2] *= (0.35 + 0.65 * (0.5 + 0.5 * np.cos(ang - 1.0)))                                # murcha de um lado
    t.vertices = np.stack([v[:, 0], v[:, 2], v[:, 1]], 1); t.apply_translation([0, -t.vertices[:, 1].min(), 0])
    if t.volume < 0: t.invert()
    a2 = np.arctan2(t.vertices[:, 2], t.vertices[:, 0]); sec = ((a2 + math.pi) / (math.pi / 3)).astype(int) % 6
    for mat, cond in (('tinta_amarela', 0), ('laranja_boia', 1)):
        f = t.faces[(sec[t.faces].min(1) == sec[t.faces].max(1)) & (sec[t.faces][:, 0] % 2 == cond)]
        f2 = t.faces[(sec[t.faces].min(1) != sec[t.faces].max(1))] if cond == 0 else np.zeros((0, 3), int)
        ff = np.vstack([f, f2]) if len(f2) else f
        m = trimesh.Trimesh(t.vertices, ff, process=True); m.remove_unreferenced_vertices(); p.add(mat, m)


@item('placa_regras_piscina', 'Placa de regras da piscina', 'mobilias', 'piscina', montagem='wall', altura_sugerida_m=1.6, comodos=['piscina'], ambiente=True,
      colisao='nenhuma', pista='alguém riscou e escreveu: "água limpa no reservatório do subsolo"')
def placa_regras_piscina(M):
    p = M.base
    img = Image.new('RGB', (512, 640), (246, 246, 240)); d = ImageDraw.Draw(img); d.rectangle([0, 0, 512, 120], fill=(20, 80, 150))
    texto_c(d, (256, 60), 'PISCINA', 70, (255, 255, 255))
    for k, t in enumerate(['NÃO CORRA', 'NÃO MERGULHE', 'DUCHA ANTES', 'SÓ COM SALVA-VIDAS']): texto_c(d, (256, 180 + k * 70), f'{k + 1}. {t}', 36, (30, 30, 30))
    d.line([(60, 460), (450, 420)], fill=(160, 20, 20), width=8); texto_c(d, (256, 520), 'ÁGUA LIMPA', 44, (150, 20, 20)); texto_c(d, (256, 580), 'NO SUBSOLO', 44, (150, 20, 20))
    mat_imagem('placa_piscina', img, 0.5)
    p.cham('aco_pintado', -0.27, 0.27, -0.02, 0.69, 0.0, 0.02, 0.006)
    p.box('placa_piscina', -0.25, 0.25, 0.0, 0.67, 0.02, 0.022); p.uv['placa_piscina'] = lambda v, n: np.stack([(v[:, 0] + 0.25) / 0.5, v[:, 1] / 0.67], 1)
    for x, y in ((-0.23, 0.02), (0.23, 0.02), (-0.23, 0.65), (0.23, 0.65)): torno(p, 'aco_polido', [(0.008, 0.0), (0.008, 0.004)], 8, 'z', (x, y, 0.022))


# ---------------------------------------------------------------------------- SKATE / MINIGOLFE
@item('skate', 'Skate', 'loot', 'utensilios', recurso='equipamento', valor=2, peso_kg=2.2, empilha=1, arma=True, dano=10,
      onde=['pista_skate', 'casas', 'escolinha', 'rua'], efeito='anda 40% mais rápido no asfalto (rodinhas fazem barulho); arma leve', pega=[0, 0.1, 0])
def skate(M):
    p = M.base; L, W = 0.4, 0.105
    perf = [(-L, 0.105), (-L + 0.04, 0.085)] + [(x, 0.08) for x in np.linspace(-L + 0.1, L - 0.1, 6)] + [(L - 0.04, 0.085), (L, 0.105)]
    pts = []
    for x, y in perf: pts.append((x, y))
    deck = P()
    for (x0, y0), (x1, y1) in zip(perf[:-1], perf[1:]):
        w0 = W * (0.85 if abs(x0) > L - 0.05 else 1.0); w1 = W * (0.85 if abs(x1) > L - 0.05 else 1.0)
        deck.hull('madeira', [(x0, y0, -w0), (x0, y0, w0), (x1, y1, -w1), (x1, y1, w1), (x0, y0 + 0.012, -w0), (x0, y0 + 0.012, w0), (x1, y1 + 0.012, -w1), (x1, y1 + 0.012, w1)])
        deck.hull('lixa_skate', [(x0, y0 + 0.012, -w0 + 0.003), (x0, y0 + 0.012, w0 - 0.003), (x1, y1 + 0.012, -w1 + 0.003), (x1, y1 + 0.012, w1 - 0.003), (x0, y0 + 0.0135, -w0 + 0.003), (x0, y0 + 0.0135, w0 - 0.003), (x1, y1 + 0.0135, -w1 + 0.003), (x1, y1 + 0.0135, w1 - 0.003)])
    for xs in (-1, 1): torno(deck, 'madeira', [(0.0, 0.0), (W * 0.85, 0.0), (W * 0.85, 0.012), (0.0, 0.012)], 16, 'y', (xs * L, perf[0][1], 0)) if False else None
    p.merge(deck)
    for xs in (-1, 1):
        x = xs * (L - 0.1)
        p.cham('aco_polido', x - 0.03, x + 0.03, 0.065, 0.08, -0.04, 0.04, 0.004); p.hull('aco_polido', [(x - 0.02, 0.065, -0.02), (x + 0.02, 0.065, -0.02), (x - 0.02, 0.065, 0.02), (x + 0.02, 0.065, 0.02), (x, 0.04, -0.08), (x, 0.04, 0.08), (x, 0.03, -0.08), (x, 0.03, 0.08)])
        for zs in (-1, 1): torno(p, 'plastico_branco', [(0.006, -0.0), (0.027, -0.0), (0.028, 0.02), (0.027, 0.04), (0.006, 0.04)], 16, 'z', (x, 0.028, zs * 0.08 + (0 if zs > 0 else -0.04)))
    p.box('tinta_vermelha', -0.05, 0.05, 0.079, 0.08, -0.08, 0.08) if False else None


@item('taco_golfe', 'Taco de minigolfe', 'loot', 'armas', recurso='arma', valor=2, peso_kg=0.5, empilha=1, arma=True, dano=12,
      onde=['minigolfe', 'mansao', 'casas'], efeito='arma corpo a corpo leve (quebra fácil)', pega=[-0.35, 0.012, 0])
def taco_golfe(M):
    p = M.base
    cyl_eixo(p, 'aco_polido', 0.007, -0.2, 0.4, 'x', (0, 0.012, 0), 10)
    cyl_eixo(p, 'borracha', 0.013, -0.45, -0.2, 'x', (0, 0.013, 0), 12)
    for k in range(10): anel(p, 'borracha', 0.013, 0.0145, -0.44 + k * 0.025, -0.432 + k * 0.025, 12, 'x', (0, 0.013, 0))
    p.cham('aco_pintado', 0.39, 0.42, 0.0, 0.03, -0.02, 0.09, 0.004); p.cham('vermelho_flag', 0.42, 0.425, 0.004, 0.026, -0.015, 0.085, 0.002)


@item('bandeira_buraco', 'Bandeirinha de buraco do minigolfe', 'mobilias', 'minigolfe', comodos=['minigolfe', 'quintal', 'parque'], ambiente=True, colisao='nenhuma',
      observacao='bom marcador de caminho (vermelho se vê de longe)')
def bandeira_buraco(M):
    p = M.base
    torno(p, 'verde_golfe', [(0.0, 0.0), (0.3, 0.0), (0.3, 0.02), (0.06, 0.02), (0.06, 0.005), (0.0, 0.005)], 28)
    anel(p, 'plastico_branco', 0.055, 0.06, 0.005, 0.02, 24)
    p.cyl('plastico_branco', 0.008, 0.005, 0.75, x=0.0, z=0.0, sec=8)
    p.hull('vermelho_flag', [(0.0, 0.74, 0.0), (0.0, 0.56, 0.0), (0.24, 0.66, 0.02), (0.0, 0.74, 0.003), (0.0, 0.56, 0.003), (0.24, 0.66, 0.023)])
    torno(p, 'plastico_branco', [(0.0, 0.02), (0.021, 0.02), (0.021, 0.05), (0.0, 0.062)], 16, 'y', (0.18, 0, 0.1)) if False else p.sphere('plastico_branco', 0.021, 0.18, 0.041, 0.1)


# ---------------------------------------------------------------------------- CONCHA ACUSTICA / DRIVE-IN
@item('estante_partitura', 'Estante de partitura', 'mobilias', 'concha', comodos=['concha_acustica', 'igreja', 'escolinha'], ambiente=True, colisao='nenhuma')
def estante_partitura(M):
    p = M.base
    for k in range(3): a = k / 3 * 2 * math.pi; p.seg('preto_palco', (0, 0.25, 0), (0.28 * math.cos(a), 0.0, 0.28 * math.sin(a)), 0.012)
    p.cyl('preto_palco', 0.012, 0.0, 1.05, sec=10); p.cyl('aco_polido', 0.008, 0.8, 1.15, sec=8)
    s = P(); s.cham('preto_palco', -0.25, 0.25, 0.0, 0.33, -0.006, 0.006, 0.003); s.cham('preto_palco', -0.25, 0.25, -0.03, 0.0, -0.006, 0.05, 0.003)
    img = Image.new('RGB', (512, 360), (244, 240, 226)); d = ImageDraw.Draw(img)
    for j in range(5):
        for i in range(5): d.line([(30, 40 + j * 65 + i * 7), (482, 40 + j * 65 + i * 7)], fill=(40, 40, 40), width=1)
        for k in range(14): x = 60 + k * 30; y = 40 + j * 65 + (k * 5 % 28); d.ellipse([x - 5, y - 4, x + 5, y + 4], fill=(20, 20, 20)); d.line([(x + 5, y), (x + 5, y - 22)], fill=(20, 20, 20), width=2)
    mat_imagem('partitura', img, 0.8)
    s.box('partitura', -0.22, 0.22, 0.0, 0.3, 0.006, 0.008); s.uv['partitura'] = lambda v, n: np.stack([(v[:, 0] + 0.22) / 0.44, v[:, 1] / 0.3], 1)
    p.merge(s, _tr12(0, 1.15, 0) @ _rx12(-0.3))


@item('caixa_som', 'Caixa de som de palco', 'mobilias', 'concha', comodos=['concha_acustica', 'igreja', 'cinema', 'escolinha', 'drive_in'], colisao='caixa', barricada=True,
      usa='energia', barulho='muito alto', interacao='isca: ligada no gerador, atrai a horda para longe da base', desmonta={'sucata': 2, 'pecas': 1})
def caixa_som(M):
    p = M.base; X, Z, H = 0.32, 0.3, 0.95
    p.cham('preto_palco', -X, X, 0.0, H, -Z, Z, 0.015)
    p.cham('tela_som', -X + 0.02, X - 0.02, 0.02, H - 0.02, Z - 0.005, Z + 0.004, 0.006)
    for y, r in ((0.32, 0.2), (0.74, 0.08)):
        anel(p, 'esmalte_escuro', r, r + 0.02, Z + 0.004, Z + 0.008, 32, 'z', (0, y, 0))
    for xs in (-1, 1):
        for y in (0.04, H - 0.04): p.cham('aco_polido', xs * X - 0.05 * xs - 0.03, xs * X - 0.05 * xs + 0.03, y - 0.03, y + 0.03, Z - 0.03, Z + 0.012, 0.01) if False else p.sphere('aco_polido', 0.025, xs * (X - 0.01), y, Z - 0.01)
        p.cham('aco', xs * X - 0.006, xs * X + 0.006, 0.5, 0.6, -0.08, 0.08, 0.004)
    p.seg('borracha', (0.1, 0.1, -Z), (0.5, 0.005, -Z - 0.4), 0.015); p.seg('borracha', (0.5, 0.005, -Z - 0.4), (1.0, 0.005, -Z - 0.3), 0.015)


@item('microfone_pedestal', 'Microfone no pedestal', 'mobilias', 'concha', comodos=['concha_acustica', 'igreja', 'escolinha', 'delegacia'], ambiente=True, colisao='nenhuma',
      observacao='com caixa de som e gerador: chamar sobreviventes (atrai zumbis também)')
def microfone_pedestal(M):
    p = M.base
    torno(p, 'preto_palco', [(0.0, 0.0), (0.15, 0.0), (0.15, 0.015), (0.03, 0.03), (0.0, 0.03)], 28)
    p.cyl('preto_palco', 0.012, 0.03, 1.0, sec=10); p.cyl('aco_polido', 0.009, 1.0, 1.45, sec=8); anel(p, 'preto_palco', 0.012, 0.02, 0.98, 1.02, 12)
    p.seg('preto_palco', (0.0, 1.45, 0.0), (0.0, 1.5, 0.2), 0.012)
    m = P(); torno(m, 'preto_palco', [(0.0, 0.0), (0.013, 0.0), (0.02, 0.13), (0.0, 0.13)], 16, 'z', (0, 0, 0))
    torno(m, 'tela_som', [(0.02, 0.13), (0.026, 0.15), (0.024, 0.18), (0.0, 0.19)], 16, 'z', (0, 0, 0))
    p.merge(m, _tr12(0.0, 1.5, 0.2) @ _rx12(0.35))
    pts = [(0.0, 1.47, 0.2), (0.05, 1.2, 0.05), (0.02, 0.6, 0.02), (0.15, 0.005, 0.1), (0.6, 0.005, 0.3)]
    for a, b in zip(pts[:-1], pts[1:]): p.seg('borracha', a, b, 0.008)


@item('cadeira_dobravel', 'Cadeira dobrável de plateia', 'mobilias', 'concha', comodos=['concha_acustica', 'igreja', 'escolinha', 'quartel', 'abrigo'], sentar=True,
      colisao='caixa', desmonta={'sucata': 1})
def cadeira_dobravel(M):
    p = M.base; X = 0.21
    for xs in (-1, 1):
        x = xs * X; p.seg('aco_pintado', (x, 0.0, 0.2), (x, 0.85, -0.2), 0.022, 0.016); p.seg('aco_pintado', (x, 0.0, -0.22), (x, 0.45, 0.18), 0.022, 0.016)
        for z in (0.2, -0.22): p.cham('borracha', x - 0.012, x + 0.012, 0.0, 0.012, z - 0.015, z + 0.015, 0.003)
    p.cham('aco_pintado', -X, X, 0.44, 0.46, -0.18, 0.2, 0.008)
    s = P(); s.cham('aco_pintado', -X + 0.01, X - 0.01, -0.12, 0.12, -0.008, 0.008, 0.006); p.merge(s, _tr12(0, 0.7, -0.1) @ _rx12(-0.44))
    p.seg('aco_pintado', (-X, 0.45, 0.18), (X, 0.45, 0.18), 0.018); p.seg('aco_pintado', (-X, 0.18, -0.1), (X, 0.18, -0.1), 0.014)


@item('poste_som_drivein', 'Poste de alto-falante do drive-in', 'mobilias', 'drivein', comodos=['drive_in', 'cinema_drive_in', 'estacionamento'], ambiente=True,
      colisao='caixa', desmonta={'sucata': 1, 'pecas': 1}, observacao='dois alto-falantes de janela: um caiu no chão')
def poste_som_drivein(M):
    p = M.base
    torno(p, 'pedra' if 'pedra' in CORES else 'granito', [(0.0, 0.0), (0.2, 0.0), (0.2, 0.1), (0.16, 0.14), (0.0, 0.14)], 20)
    p.cyl('aco_pintado', 0.04, 0.14, 1.2, sec=14); torno(p, 'aco_pintado', [(0.0, 1.2), (0.06, 1.2), (0.06, 1.24), (0.0, 1.26)], 14)
    def falante(t):
        t.cham('aco_pintado', -0.12, 0.12, -0.08, 0.08, -0.05, 0.05, 0.02); t.cham('tela_som', -0.1, 0.1, -0.06, 0.06, 0.045, 0.053, 0.006)
        for k in range(7): t.box('aco', -0.1, 0.1, -0.055 + k * 0.018, -0.05 + k * 0.018, 0.053, 0.056)
        t.cham('aco', -0.08, 0.08, 0.08, 0.1, -0.05, -0.02, 0.004); t.cham('esmalte_escuro', 0.09, 0.11, -0.02, 0.02, 0.05, 0.065, 0.003)
    a = P(); falante(a); p.merge(a, _tr12(-0.18, 1.05, 0.0) @ _ry12(-math.pi / 2))
    p.cham('aco_pintado', -0.12, -0.04, 1.08, 1.12, -0.02, 0.02, 0.003); p.cham('aco_pintado', 0.04, 0.12, 1.08, 1.12, -0.02, 0.02, 0.003)
    b = P(); falante(b); p.merge(b, _tr12(0.35, 0.05, 0.2) @ _ry12(0.6) @ _rx12(-math.pi / 2 + 0.1))
    pts = [(0.15, 1.1, 0.0), (0.25, 0.7, 0.06), (0.3, 0.2, 0.15), (0.35, 0.08, 0.18)]
    for u, v in zip(pts[:-1], pts[1:]): p.seg('plastico_preto', u, v, 0.01)
