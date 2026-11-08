# Lote 2: casa completa. Executado por gerar_props.py (usa as mesmas funcoes e materiais).
CORES.update({'tecido_mochila': (66, 82, 48), 'tecido_azul': (58, 86, 136), 'tecido_cinza': (128, 128, 126), 'tecido_vermelho': (148, 48, 42),
              'tecido_poltrona': (122, 84, 56), 'papel': (238, 232, 214), 'cera': (242, 238, 224), 'plastico_azul': (40, 90, 170),
              'livro_1': (120, 36, 36), 'livro_2': (36, 70, 110), 'livro_3': (46, 96, 60), 'livro_4': (190, 150, 60), 'livro_5': (70, 50, 40),
              'livro_6': (200, 196, 184), 'cortica': (176, 130, 84)})
FOSCOS.update({'papel': 0.85, 'cera': 0.6, 'plastico_azul': 0.45, 'cortica': 0.9, **{f'livro_{i}': 0.7 for i in range(1, 7)}})
TRANSP.update({'vidro_verde': ((60, 120, 60), 0.7, 0.08)})
TEX_PROPRIAS += [('tecido_mochila', 'tecido', 0.5, 768), ('tecido_azul', 'tecido', 0.5, 768), ('tecido_cinza', 'tecido', 0.5, 768),
                 ('tecido_vermelho', 'tecido', 0.5, 768), ('tecido_poltrona', 'tecido', 0.5, 768)]


def _bacia(p, mat, cx, cy, cz, rx, rz, prof, sec=32):
    """Bacia oca (pia, vaso) com a borda em cy: casca de revolucao achatada em x/z (semi-eixos rx, rz)."""
    fora = [(0.0, -prof)] + [(math.sin(a), -prof * math.cos(a)) for a in np.linspace(0.15, math.pi / 2, 8)]
    dentro = [(r * 0.93, y * 0.9) for r, y in fora]
    m = trimesh.creation.revolve(np.array(fora + dentro[::-1], float), sections=sec); m = _fix(m)
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    m.vertices[:, 0] *= rx; m.vertices[:, 2] *= rz; m.apply_translation([cx, cy, cz]); return p.add(mat, m)


def _torneira(p, x, y, z, alcance=0.12, altura=0.12):
    torno(p, 'inox', [(0.022, y), (0.02, y + 0.012), (0.012, y + 0.03), (0.011, y + altura)], 20, 'y', (x, 0, z))
    arco = [(x, y + altura + 0.04 * math.sin(a), z + 0.04 * (1 - math.cos(a))) for a in np.linspace(0, math.pi / 2, 7)]
    varrer(p, 'inox', circ(0.009, 12), [(x, y + altura - 0.005, z)] + arco[1:] + [(x, y + altura + 0.04, z + alcance)])
    p.cyl('aco_polido', 0.008, y + altura + 0.025, y + altura + 0.034, x=x, z=z + alcance, sec=12)
    for xs in (-1, 1):
        p.cyl('inox', 0.012, y, y + 0.025, x=x + xs * 0.07, z=z, sec=16)
        torno(p, 'aco_polido', [(0.016, y + 0.025), (0.014, y + 0.04), (0.0, y + 0.045)], 16, 'y', (x + xs * 0.07, 0, z))


# ---------------------------------------------------------------------------- MOBILIAS
@item('armario_aereo', 'Armário aéreo de cozinha', 'mobilias', 'cozinha', montagem='wall', conteiner=True, saque=['comida', 'utensilios'],
      slots=6, comodos=['cozinha'], altura_sugerida_m=1.5)
def armario_aereo(M):
    p = M.base; X, H, D, mat = 0.4, 0.6, 0.33, 'madeira_branca'
    carcaca(p, mat, -X, X, 0.0, H, 0.0, D - 0.02, t=0.018)
    p.box(mat, -X + 0.018, X - 0.018, 0.29, 0.306, 0.008, D - 0.04)
    p.cham(mat, -X - 0.01, X + 0.01, H, H + 0.03, 0.0, D + 0.01, 0.004)
    prof_x(p, mat, -X - 0.004, X + 0.004, [(D - 0.02, -0.012), (D + 0.004, -0.012), (D + 0.004, 0.0), (D - 0.02, 0.0)])
    for nome, hx0, sgn in (('porta_esq', -X, -1), ('porta_dir', X, 1)):
        q = M.parte(nome, (hx0, 0, D), 'porta', eixo='y', abre_graus=100 * sgn)
        a0, a1 = sorted((hx0 - sgn * 0.002, -sgn * 0.0015))
        almofadada(q, mat, a0, a1, 0.003, H - 0.003, D - 0.02, D, borda=0.06, n=1)
        puxador_barra(q, 'inox', 0.06, -sgn * 0.04 - 0.05, -sgn * 0.04 + 0.05, D, eixo='x')


@item('pia_banheiro', 'Pia de coluna', 'mobilias', 'banheiro', comodos=['banheiro'])
def pia_banheiro(M):
    p = M.base; Zb = -0.22
    torno(p, 'esmalte', [(0.11, 0.0), (0.105, 0.02), (0.075, 0.06), (0.07, 0.5), (0.09, 0.62), (0.14, 0.7)], 32, 'y', (0, 0, Zb + 0.12))
    cont = Point(0, 0).buffer(1.0, 24); cont = affinity.scale(cont, 0.27, 0.21)
    cont = cont.union(sbox(-0.27, 0.0, 0.27, 0.21)); furo = affinity.scale(Point(0, 0).buffer(1.0, 24), 0.19, 0.14)
    furo = affinity.translate(furo, 0, -0.02)
    tampo = cont.difference(furo)
    extrudar_xz(p, 'esmalte', affinity.translate(tampo, 0, 0), 0.84, 0.865)
    _bacia(p, 'esmalte', 0.0, 0.865, 0.02, 0.2, 0.15, 0.13)
    p.cham('esmalte', -0.27, 0.27, 0.72, 0.845, Zb + 0.0, Zb + 0.06, 0.01)
    p.hull('esmalte', [(x, y, z) for x in (-0.24, 0.24) for y in (0.72, 0.84) for z in (Zb + 0.05,)] + [(x, 0.84, z) for x in (-0.2, 0.2) for z in (0.12,)])
    anel(p, 'inox', 0.0, 0.02, 0.735, 0.738, 20, 'y', (0, 0, 0.02))
    _torneira(p, 0, 0.865, Zb + 0.04, alcance=0.1, altura=0.09)


@item('vaso_sanitario', 'Vaso sanitário com caixa', 'mobilias', 'banheiro', comodos=['banheiro'], conteiner=True, saque=['remedios', 'moedas'],
      slots=1, esconderijo='tampa da caixa: saque escondido')
def vaso_sanitario(M):
    p = M.base; Zb = -0.33
    m = trimesh.creation.revolve(np.array([(0, 0.0), (0.11, 0.0), (0.1, 0.03), (0.09, 0.15), (0.12, 0.25), (0.0, 0.25)]), sections=32)
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m = _fix(m)
    m.vertices[:, 2] *= 1.35; m.apply_translation([0, 0, 0.07]); p.add('esmalte', m)
    _bacia(p, 'esmalte', 0.0, 0.38, 0.06, 0.18, 0.235, 0.16)
    extrudar_xz(p, 'agua', affinity.translate(affinity.scale(Point(0, 0).buffer(1, 24), 0.08, 0.1), 0, -0.06), 0.27, 0.275)
    p.cham('esmalte', -0.12, 0.12, 0.38, 0.4, Zb, Zb + 0.16, 0.01)
    p.cham('esmalte', -0.19, 0.19, 0.4, 0.78, Zb, Zb + 0.17, 0.015)
    p.cham('inox', -0.03, 0.03, 0.79, 0.795, Zb + 0.06, Zb + 0.11, 0.003)
    for xs in (-1, 1): p.cyl('aco_polido', 0.008, 0.38, 0.41, x=xs * 0.09, z=Zb + 0.18, sec=10)
    aro = affinity.scale(Point(0, 0).buffer(1, 32), 0.18, 0.235).difference(affinity.scale(Point(0, 0).buffer(1, 32), 0.11, 0.15))
    q = M.parte('assento', (0, 0.4, -0.15), 'tampa', eixo='x', abre_graus=-95)
    extrudar_xz(q, 'plastico_branco', affinity.translate(aro, 0, -0.06), 0.385, 0.405)
    q2 = M.parte('tampa_caixa', (0, 0.78, 0), 'gaveta', desliza=[0, 0.12, 0.04])
    q2.cham('esmalte', -0.2, 0.2, 0.78, 0.81, Zb - 0.005, Zb + 0.18, 0.01)


@item('banheira', 'Banheira', 'mobilias', 'banheiro', comodos=['banheiro'], estacao='reservatorio de agua (enche com chuva)')
def banheira(M):
    p = M.base; X, Z, H = 0.8, 0.37, 0.55; t = 0.08
    for (a0, a1, b0, b1) in ((-X, X, -Z, -Z + 0.03), (-X, X, Z - 0.03, Z), (-X, -X + 0.03, -Z, Z), (X - 0.03, X, -Z, Z)):
        p.cham('esmalte', a0, a1, 0.0, H - 0.04, b0, b1, 0.01)                         # saias
    for (a0, a1, b0, b1) in ((-X, X, -Z, -Z + t), (-X, X, Z - t, Z), (-X, -X + t, -Z, Z), (X - t, X, -Z, Z)):
        p.cham('esmalte', a0, a1, H - 0.05, H, b0, b1, 0.012)
    # interior: fundo e paredes inclinadas
    bac = trimesh.convex.convex_hull(np.array([(x, H - 0.045, z) for x in (-X + t, X - t) for z in (-Z + t, Z - t)] +
                                              [(x, 0.08, z) for x in (-X + t + 0.12, X - t - 0.04) for z in (-Z + t + 0.05, Z - t - 0.05)]))
    bac.update_faces(bac.face_normals[:, 1] < 0.9); bac.remove_unreferenced_vertices(); bac.invert(); p.add('esmalte', bac)   # bacia (sem tampa, normais para dentro)
    anel(p, 'inox', 0.0, 0.025, 0.081, 0.084, 20, 'y', (X - t - 0.1, 0, 0))
    torno(p, 'inox', [(0.02, H), (0.018, H + 0.03), (0.012, H + 0.06)], 16, 'y', (X - 0.04, 0, 0))
    varrer(p, 'inox', circ(0.012, 12), [(X - 0.04, H + 0.055, 0), (X - 0.12, H + 0.06, 0), (X - 0.16, H + 0.04, 0)])
    for zs in (-1, 1):
        p.cyl('inox', 0.012, H, H + 0.03, x=X - 0.04, z=zs * 0.1, sec=16); torno(p, 'aco_polido', [(0.018, H + 0.03), (0.0, H + 0.045)], 16, 'y', (X - 0.04, 0, zs * 0.1))


@item('estante_livros', 'Estante de livros', 'mobilias', 'sala', conteiner=True, saque=['livros'], slots=8, barricada=True,
      comodos=['sala', 'escritorio', 'biblioteca'])
def estante_livros(M):
    p = M.base; X, H, Z0, Z1, mat = 0.45, 1.8, -0.16, 0.16, 'madeira_escura'
    carcaca(p, mat, -X, X, 0.06, H, Z0, Z1, t=0.022)
    p.box(mat, -X + 0.02, X - 0.02, 0.0, 0.06, Z0 + 0.01, Z1 - 0.02)
    p.cham(mat, -X - 0.015, X + 0.015, H, H + 0.03, Z0 - 0.005, Z1 + 0.02, 0.006)
    rng = np.random.default_rng(11); niveis = [0.082, 0.43, 0.78, 1.13, 1.47]
    for y in niveis[1:]: p.box(mat, -X + 0.022, X - 0.022, y - 0.022, y, Z0 + 0.008, Z1)
    for i, y in enumerate(niveis):
        x = -X + 0.03; fim = X - 0.03 - (0.16 if i == 2 else 0)
        while x < fim - 0.03:
            w = rng.uniform(0.018, 0.045); h = rng.uniform(0.18, 0.29); d = rng.uniform(0.15, 0.22)
            if x + w > fim: break
            mat_l = f'livro_{rng.integers(1, 7)}'
            if rng.random() < 0.07 and x + h < fim:   # livro deitado
                p.cham(mat_l, x, x + h, y, y + w, Z1 - 0.01 - d, Z1 - 0.01, 0.003); x += h + 0.005; continue
            p.cham(mat_l, x, x + w, y, y + h, Z1 - 0.012 - d, Z1 - 0.012, 0.003)
            for yy in (y + 0.02, y + h - 0.03): p.box('livro_4', x + 0.002, x + w - 0.002, yy, yy + 0.006, Z1 - 0.0125, Z1 - 0.0115)
            x += w + 0.001
        if i == 2:
            torno(p, 'cortica', [(0.05, y), (0.055, y + 0.01), (0.045, y + 0.12), (0.035, y + 0.14), (0.04, y + 0.16)], 20, 'y', (X - 0.1, 0, 0.0))


@item('rack_tv', 'Rack com TV', 'mobilias', 'sala', conteiner=True, saque=['pilhas', 'eletronicos'], slots=3, comodos=['sala'])
def rack_tv(M):
    p = M.base; X, H, Z0, Z1, mat = 0.7, 0.5, -0.21, 0.2, 'madeira'
    carcaca(p, mat, -X, X, 0.08, H, Z0, Z1, t=0.02)
    p.box(mat, -0.02, 0.0, 0.1, H - 0.02, Z0 + 0.008, Z1); p.box(mat, 0.0, X - 0.02, 0.28, 0.296, Z0 + 0.008, Z1)
    for xs in (-1, 1):
        for zz in (Z0 + 0.03, Z1 - 0.03): torno(p, 'aco', [(0.015, 0.0), (0.012, 0.08)], 12, 'y', (xs * (X - 0.04), 0, zz))
    for nome, hx0, sgn in (('porta_esq', -X, -1),):
        q = M.parte(nome, (hx0, 0, Z1 + 0.02), 'porta', eixo='y', abre_graus=-100)
        almofadada(q, mat, -X + 0.002, -0.022, 0.082, H - 0.004, Z1, Z1 + 0.02, borda=0.05, n=1)
        pegador(q, 'aco', -0.06, 0.3, Z1 + 0.02)
    p.cham('plastico_preto', 0.05, 0.3, 0.3, 0.36, -0.1, 0.12, 0.006)                      # aparelho
    p.box('lamp_glass', 0.26, 0.28, 0.33, 0.335, 0.12, 0.122)
    # TV de tela plana sobre pe
    p.cham('plastico_preto', -0.18, 0.18, H, H + 0.015, -0.12, 0.04, 0.006)
    p.cham('plastico_preto', -0.03, 0.03, H + 0.015, H + 0.12, -0.07, -0.04, 0.005)
    p.cham('plastico_preto', -0.5, 0.5, H + 0.08, H + 0.68, -0.05, -0.015, 0.008)
    p.box('vidro_escuro', -0.48, 0.48, H + 0.1, H + 0.66, -0.0152, -0.012)
    p.box('aco_polido', -0.03, 0.03, H + 0.085, H + 0.095, -0.0148, -0.012)


@item('poltrona', 'Poltrona', 'mobilias', 'sala', sentar=True, comodos=['sala', 'quarto'], conteiner=True, saque=['moedas'], slots=1)
def poltrona(M):
    p = M.base; X, Z0, Z1, mat = 0.42, -0.42, 0.42, 'tecido_poltrona'
    p.cham(mat, -X + 0.14, X - 0.14, 0.13, 0.4, Z0 + 0.04, Z1 - 0.02, 0.02)
    p.cham(mat, -X + 0.04, X - 0.04, 0.13, 0.95, Z0, Z0 + 0.2, 0.04)
    fofo(p, mat, 0, 0.93, Z0 + 0.1, X - 0.04, 0.05, 0.1, 0.4, 0.3, (12, 24))
    for xs in (-1, 1):
        cx = xs * (X - 0.07)
        p.cham(mat, cx - 0.07, cx + 0.07, 0.13, 0.6, Z0 + 0.02, Z1, 0.03)
        fofo(p, mat, cx, 0.62, (Z0 + Z1) / 2 + 0.01, 0.085, 0.06, (Z1 - Z0) / 2, 0.35, 0.25, (12, 24))
        for zz in (Z0 + 0.06, Z1 - 0.06): torno(p, 'madeira_escura', [(0.022, 0.0), (0.028, 0.10), (0.03, 0.13)], 12, 'y', (cx, 0, zz))
    fofo(p, mat, 0, 0.47, 0.06, X - 0.15, 0.075, (Z1 - 0.2 - Z0) / 2 + 0.02, 0.22, 0.18, (14, 28))
    fofo(p, mat, 0, 0.7, Z0 + 0.27, X - 0.16, 0.22, 0.08, 0.25, 0.3, (16, 24), rot_x=-0.18)
    for x in (-0.12, 0.0, 0.12):
        for y in (0.6, 0.78): cyl_eixo(p, 'tecido_poltrona', 0.008, Z0 + 0.34 + (y - 0.6) * 0.18, Z0 + 0.36 + (y - 0.6) * 0.18, 'z', (x, y, 0), 10)


@item('escrivaninha', 'Escrivaninha com luminária', 'mobilias', 'escritorio', conteiner=True, saque=['livros', 'pilhas', 'remedios'], slots=4,
      comodos=['quarto', 'escritorio', 'escolinha'])
def escrivaninha(M):
    p = M.base; X, Z0, Z1, mat = 0.6, -0.3, 0.3, 'madeira'
    p.cham(mat, -X, X, 0.73, 0.76, Z0, Z1, 0.006)
    carcaca(p, mat, 0.18, X - 0.01, 0.0, 0.73, Z0 + 0.01, Z1 - 0.02, t=0.018, topo=False)
    p.cham(mat, -X + 0.02, -X + 0.05, 0.0, 0.73, Z0 + 0.01, Z1 - 0.02, 0.004); p.box(mat, -X + 0.05, 0.18, 0.4, 0.72, Z0 + 0.01, Z0 + 0.03)
    for i, (y0, y1) in enumerate(((0.02, 0.27), (0.275, 0.5), (0.505, 0.725))):
        g = M.parte(f'gaveta_{i + 1}', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.35])
        almofadada(g, mat, 0.185, X - 0.012, y0, y1, Z1 - 0.02, Z1, borda=0.035, n=1, c=0.003)
        carcaca(g, mat, 0.2, X - 0.03, y0 + 0.01, y1 - 0.03, Z0 + 0.03, Z1 - 0.02, t=0.01, topo=False)
        pegador(g, 'cobre', (0.185 + X) / 2, (y0 + y1) / 2, Z1)
    g = M.parte('gaveta_centro', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.3])
    g.cham(mat, -X + 0.06, 0.17, 0.66, 0.725, Z1 - 0.02, Z1, 0.003); carcaca(g, mat, -X + 0.07, 0.16, 0.665, 0.715, Z0 + 0.05, Z1 - 0.02, t=0.008, topo=False)
    pegador(g, 'cobre', -0.2, 0.693, Z1)
    torno(p, 'aco_pintado', [(0.07, 0.76), (0.07, 0.775), (0.02, 0.785)], 24, 'y', (-0.42, 0, -0.15))
    a = (-0.42, 0.78, -0.15); b = (-0.38, 1.12, -0.1); c = (-0.2, 1.18, 0.02)
    p.seg('aco_pintado', a, b, 0.012); p.seg('aco_pintado', b, c, 0.012)
    cone = trimesh.creation.revolve(np.array([(0.0, 0.0), (0.03, 0.0), (0.075, -0.12), (0.07, -0.12), (0.025, -0.006), (0.0, -0.006)]), sections=24)
    cone.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); cone = _fix(cone); cone.apply_translation(c); p.add('aco_pintado', cone)
    p.sphere('lamp_glass', 0.03, c[0], c[1] - 0.06, c[2], 1)


@item('berco', 'Berço', 'mobilias', 'quarto', comodos=['quarto'], conteiner=True, saque=['roupas', 'remedios'], slots=2)
def berco(M):
    p = M.base; X, Z, mat = 0.64, 0.36, 'madeira_branca'
    for xs in (-1, 1):
        for zs in (-1, 1):
            cx, cz = xs * (X - 0.025), zs * (Z - 0.025)
            p.cham(mat, cx - 0.025, cx + 0.025, 0.0, 0.92, cz - 0.025, cz + 0.025, 0.006)
            torno(p, mat, [(0.026, 0.92), (0.022, 0.94), (0.012, 0.955)], 12, 'y', (cx, 0, cz))
    for zs in (-1, 1):
        for y in (0.3, 0.86): p.cham(mat, -X + 0.05, X - 0.05, y - 0.02, y + 0.02, *sorted((zs * (Z - 0.04), zs * (Z - 0.01))), 0.004)
        for x in np.arange(-X + 0.11, X - 0.08, 0.075): cyl_eixo(p, mat, 0.01, 0.32, 0.84, 'y', (x, 0, zs * (Z - 0.025)), 10)
    for xs in (-1, 1):
        p.cham(mat, *sorted((xs * (X - 0.04), xs * (X - 0.01))), 0.3, 0.86, -Z + 0.05, Z - 0.05, 0.006)
    p.box('madeira_crua', -X + 0.05, X - 0.05, 0.3, 0.32, -Z + 0.05, Z - 0.05)
    fofo(p, 'colchao', 0, 0.37, 0, X - 0.06, 0.05, Z - 0.06, 0.15, 0.12, (12, 28))
    fofo(p, 'cobertor', 0.1, 0.43, 0.0, 0.3, 0.025, Z - 0.08, 0.2, 0.15, (10, 24))
    fofo(p, 'travesseiro', -X + 0.2, 0.44, 0, 0.1, 0.03, 0.15, 0.35, 0.4, (12, 20))


@item('maquina_lavar', 'Máquina de lavar', 'mobilias', 'lavanderia', comodos=['lavanderia', 'cozinha'], conteiner=True, saque=['roupas', 'limpeza'],
      slots=3, barricada=True)
def maquina_lavar(M):
    p = M.base; X, H, Z0, Z1 = 0.3, 0.85, -0.29, 0.27
    p.cham('esmalte', -X, X, 0.02, H, Z0, Z1, 0.015)
    p.box('borracha', -X + 0.03, X - 0.03, 0.0, 0.02, Z0 + 0.03, Z1 - 0.04)
    p.cham('esmalte', -X + 0.005, X - 0.005, H - 0.13, H - 0.004, Z1 - 0.004, Z1 + 0.012, 0.006)
    p.box('vidro_escuro', 0.02, 0.16, H - 0.09, H - 0.05, Z1 + 0.011, Z1 + 0.014)
    torno(p, 'plastico_cinza', [(0.03, 0), (0.03, 0.012), (0.024, 0.03), (0, 0.032)], 24, 'z', (0.21, H - 0.07, Z1 + 0.012))
    for x in (0.05, 0.09, 0.13): cyl_eixo(p, 'plastico_cinza', 0.007, Z1 + 0.012, Z1 + 0.02, 'z', (x, H - 0.115, 0), 10)
    anel(p, 'borracha', 0.15, 0.175, Z1 - 0.01, Z1 + 0.004, 40, 'z', (0, 0.4, 0))
    anel(p, 'inox', 0.14, 0.15, Z1 - 0.25, Z1 - 0.005, 40, 'z', (0, 0.4, 0))
    cyl_eixo(p, 'inox', 0.14, Z1 - 0.26, Z1 - 0.25, 'z', (0, 0.4, 0), 40)
    for i in range(3):
        a = i * 2 * math.pi / 3; p.seg('plastico_cinza', (0.12 * math.cos(a), 0.4 + 0.12 * math.sin(a), Z1 - 0.25), (0.12 * math.cos(a), 0.4 + 0.12 * math.sin(a), Z1 - 0.1), 0.02, 0.02)
    g = M.parte('gaveta_sabao', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.18])
    g.cham('plastico_branco', -X + 0.02, -0.06, H - 0.11, H - 0.03, Z1 + 0.004, Z1 + 0.02, 0.004)
    carcaca(g, 'plastico_branco', -X + 0.03, -0.07, H - 0.105, H - 0.04, Z1 - 0.2, Z1 + 0.004, t=0.004, topo=False)
    q = M.parte('porta', (-0.18, 0.4, Z1 + 0.03), 'porta', eixo='y', abre_graus=-110)
    anel(q, 'plastico_branco', 0.13, 0.19, Z1 + 0.005, Z1 + 0.04, 40, 'z', (0, 0.4, 0), chanfro=0.01)
    anel(q, 'aco_polido', 0.175, 0.185, Z1 + 0.04, Z1 + 0.044, 40, 'z', (0, 0.4, 0))
    torno(q, 'plastico_transp', [(0.135, -0.02), (0.12, 0.0), (0.06, 0.012), (0.0, 0.014)], 32, 'z', (0, 0.4, Z1 + 0.03))
    q.cham('plastico_cinza', 0.17, 0.2, 0.36, 0.44, Z1 + 0.035, Z1 + 0.05, 0.004)


@item('aquecedor', 'Aquecedor a óleo', 'mobilias', 'quarto', comodos=['quarto', 'sala'], estacao='calor (gasta energia)')
def aquecedor(M):
    p = M.base; n = 7
    for i in range(n):
        x = (i - (n - 1) / 2) * 0.055
        fofo(p, 'esmalte', x, 0.36, 0.0, 0.012, 0.24, 0.12, 0.25, 0.4, (14, 16))
        for zz in (-0.06, 0.06): cyl_eixo(p, 'esmalte', 0.012, x - 0.03, x + 0.03, 'x', (0, 0.14, zz), 10)
    p.cham('plastico_cinza', 0.2, 0.3, 0.22, 0.46, -0.07, 0.07, 0.01)
    torno(p, 'plastico_preto', [(0.02, 0), (0.02, 0.012), (0.0, 0.015)], 16, 'x', (0.3, 0.4, 0.0))
    p.box('lamp_glass', 0.3, 0.302, 0.34, 0.35, -0.01, 0.01)
    for x in (-0.15, 0.15):
        p.seg('aco', (x, 0.12, 0), (x, 0.05, 0), 0.012, 0.012); cyl_eixo(p, 'aco', 0.008, -0.13, 0.13, 'z', (x, 0.05, 0), 8)
        for zz in (-0.12, 0.12): cyl_eixo(p, 'borracha', 0.025, x - 0.01, x + 0.01, 'x', (0, 0.025, zz), 16)


# ---------------------------------------------------------------------------- LOOT
@item('mochila', 'Mochila', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=0.9, empilha=1, onde=['casas', 'escolinha', 'motel', 'estacao'],
      efeito='+8 espaços no inventário', pega=[0, 0.42, -0.05])
def mochila(M):
    p = M.base; m = 'tecido_mochila'
    fofo(p, m, 0, 0.23, 0, 0.15, 0.23, 0.085, 0.4, 0.45, (20, 28))
    fofo(p, m, 0, 0.14, 0.075, 0.11, 0.1, 0.04, 0.4, 0.4, (14, 20))
    fofo(p, m, 0, 0.42, 0.02, 0.14, 0.05, 0.09, 0.4, 0.4, (12, 20), rot_x=0.15)
    for x0, x1 in ((-0.1, 0.1),): p.box('plastico_preto', x0, x1, 0.21, 0.214, 0.112, 0.116)
    p.box('aco_polido', 0.06, 0.07, 0.2, 0.215, 0.114, 0.12)
    for xs in (-1, 1):
        cam = [(xs * 0.07, 0.4, -0.075), (xs * 0.09, 0.38, -0.12), (xs * 0.1, 0.25, -0.13), (xs * 0.1, 0.1, -0.11), (xs * 0.09, 0.04, -0.08)]
        varrer(p, 'tecido_cinza', Polygon([(-0.025, -0.006), (0.025, -0.006), (0.025, 0.006), (-0.025, 0.006)]), cam)
        fofo(p, m, xs * 0.14, 0.17, 0.0, 0.03, 0.08, 0.05, 0.4, 0.4, (10, 16))
    varrer(p, 'tecido_cinza', circ(0.006, 8), [(-0.03, 0.44, -0.04), (-0.025, 0.47, -0.04), (0.025, 0.47, -0.04), (0.03, 0.44, -0.04)])


@item('roupas', 'Pilha de roupas dobradas', 'loot', 'roupas', recurso='tecido', valor=2, peso_kg=1.2, empilha=3,
      onde=['casas', 'motel', 'galeria'], efeito='aquece à noite; vira atadura ou tecido para receitas')
def roupas(M):
    p = M.base; y = 0.0
    for i, (m, h) in enumerate((('tecido_azul', 0.05), ('tecido_cinza', 0.035), ('tecido_vermelho', 0.04), ('tecido_azul', 0.03))):
        dx = 0.006 * (-1) ** i; c = h / 2
        fofo(p, m, dx, y + c, 0.005 * i, 0.15, c, 0.12, 0.18, 0.15, (12, 24)); y += h - 0.002
    fofo(p, 'tecido_cinza', 0.0, y + 0.012, -0.05, 0.14, 0.012, 0.03, 0.4, 0.2, (8, 20))


@item('sabao', 'Sabonete embrulhado', 'loot', 'higiene', recurso='higiene', valor=1, peso_kg=0.09, empilha=10, onde=['casas', 'motel', 'supermercado'],
      efeito='evita doença na base (saneamento)')
def sabao(M):
    p = M.base; X, H, Z = 0.045, 0.03, 0.03
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(200, 230, 214)); d.ellipse([20, h * 0.25, w - 20, h * 0.75], fill=(255, 255, 255))
        texto_c(d, (w / 2, h / 2 - 20), 'BRISA', 50, (40, 120, 90)); texto_c(d, (w / 2, h / 2 + 30), 'erva-doce', 26, (60, 90, 70), False)
    lado = lambda d, w, h: d.rectangle([0, 0, w, h], fill=(200, 230, 214))
    mat_imagem('rotulo_sabao', rotulo_caixa([frente, lado, lado, lado]), 0.6)
    p.cham('rotulo_sabao', -X, X, 0, H, -Z, Z, 0.006); p.uv['rotulo_sabao'] = uv_atlas(-X, X, 0, H, -Z, Z, frente='y')


@item('livro', 'Livro técnico', 'loot', 'utensilios', recurso='conhecimento', valor=1, peso_kg=0.6, empilha=5,
      onde=['biblioteca', 'escolinha', 'casas', 'correios'], efeito='pesquisa: desbloqueia projetos')
def livro(M):
    p = M.base; X, Z, e = 0.08, 0.115, 0.03
    def capa(d, w, h):
        d.rectangle([0, 0, w, h], fill=(46, 96, 60)); d.rectangle([14, 14, w - 14, h - 14], outline=(220, 200, 120), width=4)
        texto_c(d, (w / 2, h * 0.3), 'MANUAL', 40, (240, 230, 190)); texto_c(d, (w / 2, h * 0.4), 'DO HORTELÃO', 30, (240, 230, 190), larg=w - 30)
        d.ellipse([w / 2 - 50, h * 0.55, w / 2 + 50, h * 0.55 + 100], outline=(220, 200, 120), width=5); d.line([(w / 2, h * 0.6), (w / 2, h * 0.55 + 95)], fill=(220, 200, 120), width=5)
    contra = lambda d, w, h: d.rectangle([0, 0, w, h], fill=(46, 96, 60))
    mat_imagem('capa_livro', rotulo_caixa([capa, contra, contra, contra]), 0.6)
    for y0 in (0.0, e - 0.003):
        p.cham('capa_livro', -X, X, y0, y0 + 0.003, -Z, Z, 0.001)
    p.uv['capa_livro'] = uv_atlas(-X, X, 0, e, -Z, Z, frente='y')
    p.box('papel', -X + 0.008, X - 0.003, 0.003, e - 0.003, -Z + 0.003, Z - 0.003)
    cyl_eixo(p, 'livro_3', e / 2, -Z, Z, 'z', (-X + 0.004, e / 2, 0), 16)


@item('radio_portatil', 'Rádio portátil', 'loot', 'eletronicos', recurso='equipamento', valor=1, peso_kg=0.9, empilha=1, usa='pilhas',
      onde=['casas', 'correios', 'quartel', 'posto'], efeito='ouve chamados de sobreviventes')
def radio_portatil(M):
    p = M.base; X, H, Z = 0.13, 0.15, 0.045
    p.cham('plastico_cinza', -X, X, 0, H, -Z, Z, 0.012)
    p.cham('plastico_preto', -X + 0.01, -0.005, 0.015, H - 0.03, Z - 0.002, Z + 0.003, 0.004)
    for i in range(9):
        for j in range(8):
            cyl_eixo(p, 'borracha', 0.0035, Z + 0.002, Z + 0.0035, 'z', (-X + 0.02 + i * 0.012, 0.025 + j * 0.012, 0), 8)
    p.box('papel', 0.01, X - 0.015, H - 0.07, H - 0.035, Z - 0.001, Z + 0.002)
    for i in range(10): p.box('plastico_preto', 0.015 + i * 0.01, 0.016 + i * 0.01, H - 0.065, H - 0.045, Z + 0.002, Z + 0.0025)
    p.box('plastico_vermelho', 0.06, 0.062, H - 0.07, H - 0.035, Z + 0.002, Z + 0.003)
    for x in (0.04, 0.095): torno(p, 'plastico_preto', [(0.012, 0), (0.012, 0.01), (0.0, 0.012)], 16, 'z', (x, 0.04, Z))
    varrer(p, 'plastico_preto', Polygon([(-0.008, -0.006), (0.008, -0.006), (0.008, 0.006), (-0.008, 0.006)]),
           [(-X + 0.02, H - 0.005, 0), (-X + 0.03, H + 0.035, 0), (X - 0.03, H + 0.035, 0), (X - 0.02, H - 0.005, 0)])
    p.seg('aco_polido', (X - 0.015, H - 0.01, -0.02), (X + 0.05, H + 0.3, -0.03), 0.004, 0.004)
    p.sphere('aco_polido', 0.004, X + 0.05, H + 0.3, -0.03)


@item('vela_fosforos', 'Vela e caixa de fósforos', 'loot', 'eletronicos', recurso='luz', valor=1, peso_kg=0.15, empilha=6,
      onde=['casas', 'igreja', 'supermercado', 'motel'], efeito='luz sem pilha por 4 horas; acende fogueira')
def vela_fosforos(M):
    p = M.base
    torno(p, 'cera', [(0.011, 0.0), (0.011, 0.14), (0.009, 0.143), (0.004, 0.141)], 20, 'y', (-0.03, 0, 0))
    p.cyl('fita_preta', 0.0012, 0.138, 0.152, x=-0.03, z=0, sec=6)
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(220, 50, 40)); texto_c(d, (w / 2, h * 0.35), 'FAÍSCA', 40, (255, 230, 120))
        d.polygon([(w / 2, h * 0.5), (w / 2 + 30, h * 0.75), (w / 2, h * 0.9), (w / 2 - 30, h * 0.75)], fill=(255, 200, 60))
    lado = lambda d, w, h: d.rectangle([0, 0, w, h], fill=(80, 50, 40))
    mat_imagem('rotulo_fosforo', rotulo_caixa([frente, frente, lado, lado]), 0.7)
    p.cham('rotulo_fosforo', 0.0, 0.052, 0, 0.015, -0.018, 0.018, 0.0015); p.uv['rotulo_fosforo'] = uv_atlas(0.0, 0.052, 0, 0.015, -0.018, 0.018, frente='y')
    for i in range(2): p.seg('madeira_crua', (0.06 + i * 0.006, 0.0012, -0.02), (0.065 + i * 0.008, 0.0012, 0.02), 0.0022, 0.0022); p.sphere('plastico_vermelho', 0.0024, 0.065 + i * 0.008, 0.0016, 0.021, 1)


@item('isqueiro', 'Isqueiro', 'loot', 'eletronicos', recurso='ferramenta', valor=1, peso_kg=0.02, empilha=10,
      onde=['casas', 'posto', 'diner', 'motel'], efeito='acende fogueira e molotov (muitos usos)')
def isqueiro(M):
    p = M.base; y = 0.0125
    TRANSP['isq'] = ((40, 150, 90), 0.75, 0.15)
    MATS['isq'] = PBRMaterial(name='isq', baseColorFactor=[40 / 255, 150 / 255, 90 / 255, 0.75], alphaMode='BLEND', roughnessFactor=0.15)
    p.cham('isq', -0.035, 0.025, 0.0, 0.025, -0.0055, 0.0055, 0.004)
    p.cham('aco_polido', 0.025, 0.045, 0.0015, 0.0235, -0.0058, 0.0058, 0.002)
    cyl_eixo(p, 'aco', 0.0045, -0.003, 0.003, 'z', (0.039, y + 0.005, 0), 12)
    p.cham('plastico_preto', 0.028, 0.04, 0.003, 0.009, -0.004, 0.004, 0.001)


@item('garrafa_vidro', 'Garrafa de vidro vazia', 'loot', 'utensilios', recurso='sucata', valor=1, peso_kg=0.4, empilha=4,
      onde=['casas', 'diner', 'galeria', 'supermercado'], efeito='guarda água fervida; ingrediente do molotov')
def garrafa_vidro(M):
    p = M.base; r = 0.035
    torno(p, 'vidro_verde', [(r - 0.003, 0.0), (r, 0.004), (r, 0.19), (0.03, 0.21), (0.014, 0.245), (0.012, 0.28), (0.014, 0.283), (0.014, 0.29), (0.011, 0.292)], 32)
    img = Image.new('RGB', (1024, 256), (236, 226, 196)); d = ImageDraw.Draw(img)
    for cx in (256, 768): texto_c(d, (cx, 100), 'SERRA ALTA', 52, (120, 40, 30)); texto_c(d, (cx, 160), 'suco de uva', 30, (70, 50, 40), False)
    mat_imagem('rotulo_vidro', img, 0.6)
    anel(p, 'rotulo_vidro', r - 0.0005, r + 0.0006, 0.06, 0.13, 32); p.uv['rotulo_vidro'] = uv_cilindro(0.06, 0.13)


@item('panela', 'Panela com tampa', 'loot', 'utensilios', recurso='ferramenta', valor=2, peso_kg=1.1, empilha=1,
      onde=['casas', 'diner', 'padaria', 'motel'], efeito='cozinhar na fogueira; ferver água')
def panela(M):
    p = M.base; r, h, t = 0.11, 0.12, 0.003
    torno(p, 'aco_polido', [(0.0, 0.0), (r - 0.01, 0.0), (r, 0.01), (r, h), (r + 0.004, h + 0.003), (r - t, h + 0.003), (r - t, t + 0.01), (r - 0.012, t), (0.0, t)], 40)
    for xs in (-1, 1):
        p.cham('plastico_preto', *sorted((xs * (r + 0.005), xs * (r + 0.05))), h - 0.03, h - 0.012, -0.018, 0.018, 0.005)
        cyl_eixo(p, 'aco', 0.004, *sorted((xs * (r - 0.002), xs * (r + 0.008))), 'x', (0, h - 0.02, 0), 8)
    torno(p, 'aco_polido', [(r + 0.004, h + 0.002), (r - 0.002, h + 0.006), (r * 0.6, h + 0.022), (0.0, h + 0.026)], 40)
    torno(p, 'plastico_preto', [(0.012, h + 0.025), (0.01, h + 0.035), (0.02, h + 0.045), (0.0, h + 0.05)], 16)


@item('faca_cozinha', 'Faca de cozinha', 'loot', 'armas', recurso='arma', valor=2, peso_kg=0.15, empilha=1, arma=True, dano=18,
      onde=['casas', 'diner', 'padaria'], efeito='arma rápida e silenciosa; corta comida e tecido', pega=[-0.08, 0.009, 0])
def faca_cozinha(M):
    p = M.base
    lam = Polygon([(-0.01, -0.012), (0.17, -0.012), (0.2, -0.002), (0.19, 0.004), (0.12, 0.018), (-0.01, 0.022)])
    extrudar_xz(p, 'aco_polido', lam, 0.008, 0.0105)
    extrudar_xz(p, 'aco', Polygon([(0.0, -0.012), (0.17, -0.012), (0.2, -0.002), (0.19, -0.0)]).buffer(0.0005), 0.0085, 0.0099)
    p.cham('plastico_preto', -0.13, -0.008, 0.0, 0.018, -0.011, 0.015, 0.005)
    for x in (-0.1, -0.065, -0.03): p.cyl('aco_polido', 0.0035, 0.0175, 0.019, x=x, z=0.002, sec=10)
