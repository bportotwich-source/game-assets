# Lote 3: comercio e servicos. Executado por gerar_props.py (usa as mesmas funcoes e materiais).
CORES.update({'gondola': (226, 228, 224), 'etiqueta': (250, 210, 40), 'vinil_maca': (70, 110, 130), 'armario_verde': (92, 120, 96),
              'aco_cinza': (150, 156, 160), 'saco_rafia': (226, 216, 190), 'juta': (168, 136, 92), 'plastico_amarelo': (230, 190, 40)})
METALICOS.update({'gondola': (0.3, 0.4), 'armario_verde': (0.3, 0.45), 'aco_cinza': (0.4, 0.4)})
FOSCOS.update({'etiqueta': 0.5, 'vinil_maca': 0.45, 'plastico_amarelo': 0.45})
TEX_PROPRIAS += [('saco_rafia', 'tecido', 0.5, 768), ('juta', 'tecido', 0.25, 1024)]


def _arame(p, mat, a, b, r=0.003): p.seg(mat, a, b, 2 * r, 2 * r)


# ---------------------------------------------------------------------------- MOBILIAS
@item('gondola', 'Gôndola de supermercado', 'mobilias', 'loja', conteiner=True, saque=['comida', 'agua', 'higiene', 'limpeza'], slots=16,
      comodos=['supermercado', 'galeria', 'posto'], modulo_m=1.0)
def gondola(M):
    """Modulo de 1 m dupla face: encaixa lado a lado (pontas retas) para formar corredores."""
    p = M.base; X, Z, H, mat = 0.5, 0.45, 1.6, 'gondola'
    p.box(mat, -X + 0.001, X - 0.001, 0.0, 0.12, -Z + 0.01, Z - 0.01)
    p.box('esmalte_escuro', -X + 0.001, X - 0.001, 0.0, 0.02, -Z + 0.03, Z - 0.03)
    for xs in (-1, 1): p.box(mat, *sorted((xs * X, xs * (X - 0.04))), 0.12, H, -0.03, 0.03)
    p.box(mat, -X + 0.04, X - 0.04, 0.12, H, -0.01, 0.01)
    for xs in (-1, 1):
        for y in np.arange(0.2, H - 0.05, 0.05): p.box('esmalte_escuro', xs * (X - 0.02) - 0.004, xs * (X - 0.02) + 0.004, y, y + 0.025, -0.0305, 0.0305)
    for zs in (-1, 1):
        for i, y in enumerate((0.12, 0.5, 0.85, 1.2)):
            d = Z - 0.03 if i == 0 else 0.38 - i * 0.03
            z0, z1 = sorted((zs * 0.03, zs * d))
            p.box(mat, -X + 0.002, X - 0.002, y, y + 0.02, z0, z1)
            p.box('etiqueta', -X + 0.002, X - 0.002, y - 0.02, y + 0.02, *sorted((zs * d, zs * (d + 0.004))))
            for x in np.arange(-X + 0.12, X - 0.05, 0.25): p.box('papel', x - 0.02, x + 0.02, y - 0.012, y + 0.012, *sorted((zs * (d + 0.004), zs * (d + 0.005))))
            if i > 0:
                for xs in (-1, 1):
                    _arame(p, 'aco', (xs * (X - 0.06), y, zs * 0.03), (xs * (X - 0.06), y - 0.1, zs * 0.03), 0.006)
                    p.hull(mat, [(xs * (X - 0.06) + dx, y, zs * z) for dx in (-0.003, 0.003) for z in (0.03, d - 0.02)] + [(xs * (X - 0.06) + dx, y - 0.08, zs * 0.03) for dx in (-0.003, 0.003)])
    p.cham(mat, -X, X, H, H + 0.05, -0.04, 0.04, 0.006)


@item('balcao_caixa', 'Balcão de caixa com registradora', 'mobilias', 'loja', conteiner=True, saque=['moedas', 'pilhas', 'remedios'], slots=4,
      barricada=True, comodos=['supermercado', 'galeria', 'posto', 'diner', 'padaria'])
def balcao_caixa(M):
    p = M.base; X, Z, H = 0.9, 0.3, 0.9
    p.cham('madeira_branca', -X, X, 0.08, H - 0.04, -Z, Z, 0.01)
    p.box('plastico_preto', -X + 0.02, X - 0.02, 0.0, 0.08, -Z + 0.02, Z - 0.04)
    p.cham('granito', -X - 0.02, X + 0.02, H - 0.04, H, -Z - 0.02, Z + 0.02, 0.004)
    p.box('borracha', -X + 0.05, 0.1, H, H + 0.006, -Z + 0.04, Z - 0.04)                  # esteira
    for x in (-X + 0.05, 0.1): cyl_eixo(p, 'aco', 0.012, -Z + 0.04, Z - 0.04, 'z', (x, H + 0.0, 0), 16)
    p.cham('aco_polido', 0.12, 0.24, H, H + 0.02, -0.1, 0.1, 0.003)                         # balanca
    p.cham('plastico_cinza', 0.4, 0.8, H, H + 0.09, -0.22, 0.12, 0.01)                      # registradora
    p.hull('plastico_cinza', [(x, H + 0.09, z) for x in (0.42, 0.78) for z in (-0.2, -0.02)] + [(x, H + 0.13, z) for x in (0.42, 0.78) for z in (-0.2, -0.12)])
    for i in range(4):
        for j in range(3): p.cham('plastico_preto', 0.46 + i * 0.05, 0.495 + i * 0.05, H + 0.098 + j * 0.01, H + 0.104 + j * 0.01, -0.06 + j * -0.04, -0.03 + j * -0.04, 0.002)
    p.cham('plastico_preto', 0.5, 0.7, H + 0.13, H + 0.25, -0.2, -0.18, 0.005)
    p.box('vidro_escuro', 0.51, 0.69, H + 0.14, H + 0.24, -0.1801, -0.179)
    p.cyl('plastico_cinza', 0.02, H + 0.13, H + 0.14, x=0.6, z=-0.19, sec=12)
    g = M.parte('gaveta_dinheiro', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.25])
    g.cham('plastico_cinza', 0.42, 0.78, H - 0.15, H - 0.045, -0.2, Z + 0.005, 0.005)
    for i in range(4): g.box('papel' if i < 3 else 'cobre', 0.44 + i * 0.085, 0.51 + i * 0.085, H - 0.06, H - 0.055, -0.15, Z - 0.03)


@item('freezer_horizontal', 'Freezer horizontal', 'mobilias', 'loja', conteiner=True, saque=['comida'], slots=10, comodos=['supermercado', 'posto', 'diner'])
def freezer_horizontal(M):
    p = M.base; X, Z, H = 0.75, 0.33, 0.85
    for (a0, a1, b0, b1) in ((-X, X, -Z, -Z + 0.05), (-X, X, Z - 0.05, Z), (-X, -X + 0.05, -Z, Z), (X - 0.05, X, -Z, Z)):
        p.cham('esmalte', a0, a1, 0.06, H, b0, b1, 0.01)
    p.box('esmalte', -X + 0.05, X - 0.05, 0.06, 0.12, -Z + 0.05, Z - 0.05)
    p.box('liner', -X + 0.05, X - 0.05, 0.12, 0.125, -Z + 0.05, Z - 0.05)
    p.box('esmalte_escuro', -X + 0.03, X - 0.03, 0.0, 0.06, -Z + 0.03, Z - 0.03)
    rng = np.random.default_rng(5)
    for i in range(14):                                                                 # pacotes congelados
        x = rng.uniform(-X + 0.12, X - 0.12); z = rng.uniform(-Z + 0.1, Z - 0.1); a = rng.uniform(0, 3)
        p.cham(['tecido_azul', 'plastico_vermelho', 'plastico_branco', 'plastico_amarelo'][i % 4], x - 0.08, x + 0.08, 0.125 + (i // 7) * 0.05, 0.17 + (i // 7) * 0.05, z - 0.06, z + 0.06, 0.008)
    p.box('etiqueta', -X, X, H - 0.12, H - 0.06, Z, Z + 0.003)
    for i, (nome, x0, x1, dz) in enumerate((('tampa_esq', -X + 0.03, 0.02, 0), ('tampa_dir', -0.02, X - 0.03, 0))):
        q = M.parte(nome, (0, 0, 0), 'gaveta', desliza=[0.55 if i == 0 else -0.55, 0, 0])
        yy = H + 0.004 + i * 0.012
        q.box('plastico_cinza', x0, x1, yy, yy + 0.012, -Z + 0.02, Z - 0.02)
        q.box('vidro_prateleira', x0 + 0.03, x1 - 0.03, yy + 0.012, yy + 0.014, -Z + 0.05, Z - 0.05)
        q.cham('plastico_preto', (x1 if i == 0 else x0) - 0.05, (x1 if i == 0 else x0) + 0.05, yy + 0.012, yy + 0.03, -0.08, 0.08, 0.004)


@item('prateleira_padaria', 'Prateleira de pães', 'mobilias', 'loja', conteiner=True, saque=['comida'], slots=6, comodos=['padaria', 'supermercado'])
def prateleira_padaria(M):
    p = M.base; X, Z, H, mat = 0.6, 0.25, 1.6, 'madeira'
    for xs in (-1, 1): p.cham(mat, *sorted((xs * X, xs * (X - 0.03))), 0.0, H, -Z, Z, 0.005)
    p.box(mat, -X + 0.03, X - 0.03, 0.04, H - 0.02, -Z, -Z + 0.015)
    p.cham(mat, -X - 0.01, X + 0.01, H, H + 0.03, -Z - 0.01, Z + 0.01, 0.005)
    for k, y in enumerate((0.1, 0.5, 0.9, 1.25)):
        yb = y; zf = Z - 0.02; zt = -Z + 0.03                                                # prateleira inclinada para a frente
        p.hull(mat, [(x, yb + 0.15 + dy, zt) for x in (-X + 0.03, X - 0.03) for dy in (0, 0.015)] + [(x, yb + dy, zf) for x in (-X + 0.03, X - 0.03) for dy in (0, 0.015)])
        p.cham(mat, -X + 0.03, X - 0.03, yb, yb + 0.06, zf, zf + 0.015, 0.003)
        for j in range(3):                                                               # cestos de vime com paes
            cx = -0.38 + j * 0.38; cy = yb + 0.08
            p.cham('juta', cx - 0.16, cx + 0.16, cy - 0.04, cy + 0.04, -0.08, 0.16, 0.012)
            for i in range(3):
                fofo(p, 'cortica', cx - 0.08 + i * 0.08, cy + 0.055, 0.05, 0.035, 0.03, 0.09, 0.35, 0.3, (8, 12))
                for t in (-0.05, 0.0, 0.05): p.seg('madeira_crua', (cx - 0.08 + i * 0.08 - 0.02, cy + 0.08, 0.05 + t), (cx - 0.08 + i * 0.08 + 0.02, cy + 0.08, 0.05 + t + 0.01), 0.004, 0.004)


@item('mesa_escritorio', 'Mesa de escritório', 'mobilias', 'escritorio', conteiner=True, saque=['pilhas', 'livros', 'moedas'], slots=3,
      comodos=['escritorio', 'correios', 'biblioteca', 'quartel'])
def mesa_escritorio(M):
    p = M.base; X, Z = 0.7, 0.35
    p.cham('madeira_branca', -X, X, 0.72, 0.745, -Z, Z, 0.004)
    p.box('plastico_preto', -X - 0.002, X + 0.002, 0.722, 0.743, Z - 0.0, Z + 0.002)
    for xs in (-1, 1):
        cx = xs * (X - 0.06)
        for zs in (-1, 1): p.cham('aco_cinza', cx - 0.02, cx + 0.02, 0.03, 0.72, zs * (Z - 0.05) - 0.02, zs * (Z - 0.05) + 0.02, 0.004)
        p.cham('aco_cinza', cx - 0.025, cx + 0.025, 0.0, 0.03, -Z + 0.01, Z - 0.01, 0.006)
        p.cham('aco_cinza', cx - 0.02, cx + 0.02, 0.68, 0.72, -Z + 0.03, Z - 0.03, 0.004)
    p.cham('aco_cinza', -X + 0.06, X - 0.06, 0.4, 0.68, -Z + 0.04, -Z + 0.055, 0.004)
    carcaca(p, 'aco_cinza', 0.15, 0.55, 0.52, 0.72, -Z + 0.06, Z - 0.03, t=0.012, topo=False)
    g = M.parte('gaveta', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.3])
    g.cham('aco_cinza', 0.152, 0.548, 0.525, 0.715, Z - 0.03, Z - 0.01, 0.003); carcaca(g, 'aco_cinza', 0.165, 0.535, 0.53, 0.69, -Z + 0.07, Z - 0.03, t=0.006, topo=False)
    puxador_barra(g, 'aco_polido', 0.62, 0.28, 0.42, Z - 0.01, eixo='x')
    p.cham('plastico_preto', -0.45, -0.05, 0.745, 0.76, -0.25, -0.12, 0.004)                # teclado e monitor
    p.cham('plastico_preto', -0.3, -0.2, 0.745, 0.76, -0.33, -0.27, 0.004); p.cham('plastico_preto', -0.27, -0.23, 0.76, 0.86, -0.31, -0.29, 0.004)
    p.cham('plastico_preto', -0.5, 0.0, 0.84, 1.14, -0.32, -0.29, 0.006); p.box('vidro_escuro', -0.485, -0.015, 0.855, 1.125, -0.2902, -0.288)
    p.cham('papel', 0.1, 0.32, 0.745, 0.765, -0.1, 0.2, 0.002)


@item('arquivo_aco', 'Arquivo de aço 4 gavetas', 'mobilias', 'escritorio', conteiner=True, saque=['livros', 'mapas', 'moedas'], slots=6, barricada=True,
      comodos=['escritorio', 'correios', 'quartel', 'escolinha'])
def arquivo_aco(M):
    p = M.base; X, Z0, Z1, H, mat = 0.235, -0.31, 0.3, 1.33, 'aco_cinza'
    carcaca(p, mat, -X, X, 0.04, H, Z0, Z1, t=0.01)
    p.box('borracha', -X + 0.02, X - 0.02, 0.0, 0.04, Z0 + 0.02, Z1 - 0.03)
    hs = (H - 0.06) / 4
    for i in range(4):
        y0 = 0.045 + i * hs; y1 = y0 + hs - 0.006
        g = M.parte(f'gaveta_{i + 1}', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.45])
        g.cham(mat, -X + 0.004, X - 0.004, y0, y1, Z1, Z1 + 0.02, 0.004)
        carcaca(g, mat, -X + 0.015, X - 0.015, y0 + 0.01, y1 - 0.04, Z0 + 0.02, Z1, t=0.006, topo=False)
        for k in range(6): g.box('papel', -X + 0.03, X - 0.03, y0 + 0.02, y1 - 0.06, Z0 + 0.06 + k * 0.08, Z0 + 0.065 + k * 0.08)
        yc = y1 - 0.08
        g.cham('aco_polido', -0.06, 0.06, yc - 0.012, yc + 0.012, Z1 + 0.02, Z1 + 0.035, 0.004)
        g.box('papel', -0.04, 0.04, yc + 0.03, yc + 0.06, Z1 + 0.02, Z1 + 0.023)
    cyl_eixo(p, 'aco_polido', 0.01, Z1, Z1 + 0.012, 'z', (0.18, H - 0.04, 0), 12)


@item('armario_vestiario', 'Armário de vestiário (3 portas)', 'mobilias', 'escritorio', conteiner=True, saque=['roupas', 'mochila', 'armas', 'remedios'],
      slots=9, barricada=True, comodos=['quartel', 'escolinha', 'estacao', 'galeria'])
def armario_vestiario(M):
    p = M.base; X, Z0, Z1, H, mat = 0.45, -0.25, 0.24, 1.85, 'armario_verde'
    carcaca(p, mat, -X, X, 0.1, H, Z0, Z1, t=0.012)
    for x in (-0.15, 0.15): p.box(mat, x - 0.006, x + 0.006, 0.1, H, Z0 + 0.008, Z1)
    p.box('esmalte_escuro', -X + 0.01, X - 0.01, 0.0, 0.1, Z0 + 0.02, Z1 - 0.02)
    for i in range(3):
        x0 = -X + i * 0.3 + 0.003; x1 = x0 + 0.3 - 0.006
        p.box(mat, x0 + 0.01, x1 - 0.01, 1.55, 1.56, Z0 + 0.008, Z1 - 0.01)
        cyl_eixo(p, 'aco_polido', 0.008, x0 + 0.01, x1 - 0.01, 'x', (0, 1.5, 0), 10)
        q = M.parte(f'porta_{i + 1}', (x0, 0, Z1 + 0.015), 'porta', eixo='y', abre_graus=-105)
        q.cham(mat, x0, x1, 0.103, H - 0.003, Z1, Z1 + 0.015, 0.003)
        for k in range(6): q.box('esmalte_escuro', x0 + 0.06, x1 - 0.06, 1.62 + k * 0.03, 1.632 + k * 0.03, Z1 + 0.014, Z1 + 0.016)
        for k in range(6): q.box('esmalte_escuro', x0 + 0.06, x1 - 0.06, 0.2 + k * 0.03, 0.212 + k * 0.03, Z1 + 0.014, Z1 + 0.016)
        q.cham('aco_polido', x1 - 0.06, x1 - 0.03, 0.95, 1.1, Z1 + 0.015, Z1 + 0.03, 0.004)
        q.box('papel', x0 + 0.08, x1 - 0.08, 1.38, 1.42, Z1 + 0.015, Z1 + 0.017)


@item('maca', 'Maca hospitalar', 'mobilias', 'saude', deitar=True, comodos=['quartel', 'escolinha', 'enfermaria'], estacao='enfermaria (cura mais rápido)')
def maca(M):
    p = M.base; X, Z, Y = 0.33, 0.95, 0.78
    for xs in (-1, 1):
        for zs in (-1, 1):
            cx, cz = xs * (X - 0.03), zs * (Z - 0.08)
            p.cyl('aco_polido', 0.014, 0.1, Y - 0.04, x=cx, z=cz, sec=12)
            p.cham('aco', cx - 0.015, cx + 0.015, 0.06, 0.1, cz - 0.02, cz + 0.02, 0.003)
            anel(p, 'borracha', 0.0, 0.04, -0.012, 0.012, 20, 'x', (cx, 0.04, cz))
        cyl_eixo(p, 'aco_polido', 0.012, -Z + 0.05, Z - 0.05, 'z', (xs * (X - 0.03), 0.25, 0), 12)
        cyl_eixo(p, 'aco_polido', 0.015, -Z, Z, 'z', (xs * (X - 0.01), Y - 0.04, 0), 12)
        cyl_eixo(p, 'aco_polido', 0.011, -Z + 0.3, Z - 0.3, 'z', (xs * (X + 0.02), Y + 0.12, 0), 12)
        for zz in (-Z + 0.3, 0.0, Z - 0.3): p.cyl('aco_polido', 0.01, Y - 0.04, Y + 0.12, x=xs * (X + 0.02), z=zz, sec=10)
    for zs in (-1, 1): cyl_eixo(p, 'aco_polido', 0.015, -X + 0.01, X - 0.01, 'x', (0, Y - 0.04, zs * Z), 12)
    p.box('aco', -X + 0.01, X - 0.01, Y - 0.04, Y - 0.025, -Z + 0.02, Z - 0.02)
    p.cham('vinil_maca', -X + 0.02, X - 0.02, Y - 0.025, Y + 0.05, -Z + 0.35, Z - 0.02, 0.025)
    p.hull('vinil_maca', [(x, Y - 0.025, z) for x in (-X + 0.02, X - 0.02) for z in (-Z + 0.35, -Z + 0.05)] +
           [(x, Y + 0.05, -Z + 0.35) for x in (-X + 0.02, X - 0.02)] + [(x, Y + 0.3, z) for x in (-X + 0.02, X - 0.02) for z in (-Z + 0.05, -Z + 0.1)])
    fofo(p, 'travesseiro', 0, Y + 0.2, -Z + 0.18, 0.22, 0.05, 0.12, 0.35, 0.4, (12, 20), rot_x=-0.55)
    p.cyl('aco_polido', 0.008, Y, 1.9, x=X - 0.03, z=-Z + 0.08, sec=10)
    cyl_eixo(p, 'aco_polido', 0.005, X - 0.12, X + 0.06, 'x', (0, 1.88, -Z + 0.08), 8)
    p.cham('plastico_transp', X - 0.12, X - 0.05, 1.62, 1.82, -Z + 0.06, -Z + 0.1, 0.01)


@item('carrinho_compras', 'Carrinho de compras', 'mobilias', 'loja', conteiner=True, saque=['comida'], slots=6, barricada=True,
      comodos=['supermercado', 'estacionamento'], empurrar=True)
def carrinho_compras(M):
    p = M.base; m = 'aco_polido'; yb, yt = 0.42, 0.92; X0, X1 = 0.26, 0.29
    zf, zt = 0.42, -0.42
    def contorno(y, xh, z0, z1): return [(-xh, y, z0), (xh, y, z0), (xh, y, z1), (-xh, y, z1)]
    for y, xh, z0, z1 in ((yb, 0.24, zf - 0.04, zt), (yt, 0.27, zf, zt - 0.02)):
        c = contorno(y, xh, z0, z1)
        for i in range(4): _arame(p, m, c[i], c[(i + 1) % 4], 0.005)
    for i, t in enumerate(np.linspace(0, 1, 9)):                                       # laterais (arames verticais)
        z_b = zf - 0.04 + (zt - zf + 0.04) * t; z_t = zf + (zt - 0.02 - zf) * t
        for xs in (-1, 1): _arame(p, m, (xs * 0.24, yb, z_b), (xs * 0.27, yt, z_t), 0.0028)
    for x in np.linspace(-0.24, 0.24, 9):
        _arame(p, m, (x, yb, zf - 0.04), (x * 1.12, yt, zf), 0.0028); _arame(p, m, (x, yb, zt), (x * 1.12, yt, zt - 0.02), 0.0028)
        _arame(p, m, (x, yb, zf - 0.04), (x, yb, zt), 0.0025)
    for y in np.linspace(yb + 0.1, yt - 0.1, 4):
        k = (y - yb) / (yt - yb); xh = 0.24 + 0.03 * k
        for xs in (-1, 1): _arame(p, m, (xs * xh, y, zf - 0.04 + 0.04 * k), (xs * xh, y, zt - 0.02 * k), 0.0025)
        _arame(p, m, (-xh, y, zf - 0.04 + 0.04 * k), (xh, y, zf - 0.04 + 0.04 * k), 0.0025); _arame(p, m, (-xh, y, zt - 0.02 * k), (xh, y, zt - 0.02 * k), 0.0025)
    for xs in (-1, 1):                                                                 # chassi
        _arame(p, m, (xs * 0.2, 0.1, zf - 0.05), (xs * 0.22, 0.1, zt - 0.05), 0.009)
        _arame(p, m, (xs * 0.22, 0.1, zt - 0.05), (xs * 0.26, yt + 0.08, zt - 0.14), 0.009)
        _arame(p, m, (xs * 0.2, 0.1, zf - 0.05), (xs * 0.22, yb, zf - 0.05), 0.008)
        for zz in (zf - 0.05, zt - 0.05):
            p.cham('plastico_preto', xs * 0.21 - 0.012, xs * 0.21 + 0.012, 0.06, 0.1, zz - 0.02, zz + 0.02, 0.004)
            anel(p, 'borracha', 0.0, 0.05, -0.012, 0.012, 20, 'x', (xs * 0.21, 0.05, zz))
    cyl_eixo(p, 'plastico_vermelho', 0.016, -0.28, 0.28, 'x', (0, yt + 0.08, zt - 0.14), 16)
    for x in np.linspace(-0.18, 0.18, 7): _arame(p, m, (x, 0.12, zf - 0.05), (x, 0.12, zt - 0.05), 0.0025)


# ---------------------------------------------------------------------------- LOOT
@item('caixa_leite', 'Caixa de leite longa vida', 'loot', 'comida', recurso='comida', valor=1, peso_kg=1.05, empilha=6,
      onde=['supermercado', 'casas', 'diner', 'padaria'], efeito='fome -10, sede -15')
def caixa_leite(M):
    p = M.base; X, H, Z = 0.048, 0.2, 0.031
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(250, 250, 246)); d.rectangle([0, h * 0.62, w, h], fill=(40, 110, 200))
        texto_c(d, (w / 2, h * 0.14), 'CAMPO BOM', 30, (40, 110, 200), larg=w - 20); texto_c(d, (w / 2, h * 0.3), 'LEITE', 62, (30, 60, 120))
        texto_c(d, (w / 2, h * 0.42), 'integral · 1 L', 26, (60, 60, 60), False)
        d.ellipse([w * 0.2, h * 0.68, w * 0.8, h * 0.92], fill=(250, 250, 246)); d.ellipse([w * 0.35, h * 0.74, w * 0.5, h * 0.8], fill=(40, 40, 40))
    lado = lambda d, w, h: (d.rectangle([0, 0, w, h], fill=(250, 250, 246)), d.rectangle([0, h * 0.62, w, h], fill=(40, 110, 200)))
    mat_imagem('rotulo_leite', rotulo_caixa([frente, frente, lado, lambda d, w, h: d.rectangle([0, 0, w, h], fill=(240, 240, 236))]), 0.5)
    p.cham('rotulo_leite', -X, X, 0, H, -Z, Z, 0.002); p.uv['rotulo_leite'] = uv_atlas(-X, X, 0, H, -Z, Z)
    torno(p, 'plastico_azul', [(0.012, H), (0.012, H + 0.012), (0.01, H + 0.014)], 20, 'y', (0.02, 0, 0.0))
    p.box('plastico_branco', -X + 0.004, X - 0.004, H, H + 0.004, -0.004, 0.004)


@item('saco_farinha', 'Saco de farinha 5 kg', 'loot', 'comida', recurso='comida', valor=8, peso_kg=5.0, empilha=1,
      onde=['padaria', 'supermercado', 'armazem'], efeito='padaria da base: rende 20 pães')
def saco_farinha(M):
    p = M.base; a, b, c = 0.15, 0.06, 0.23
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(236, 226, 200)); d.rectangle([0, h * 0.1, w, h * 0.3], fill=(170, 60, 40))
        texto_c(d, (w / 2, h * 0.2), 'MOINHO REAL', 34, (250, 240, 210), larg=w - 20); texto_c(d, (w / 2, h * 0.5), 'FARINHA', 56, (130, 50, 30), larg=w - 20)
        texto_c(d, (w / 2, h * 0.62), 'de trigo', 30, (90, 70, 50), False); texto_c(d, (w / 2, h * 0.85), '5 kg', 54, (130, 50, 30))
    lado = lambda d, w, h: d.rectangle([0, 0, w, h], fill=(236, 226, 200))
    mat_imagem('rotulo_farinha', rotulo_caixa([frente, lado, lado, lado]), 0.85)
    fofo(p, 'rotulo_farinha', 0, b, 0, a, b, c, 0.25, 0.15, (16, 28)); p.uv['rotulo_farinha'] = uv_atlas(-a, a, 0, 2 * b, -c, c, frente='y')
    for zs in (-1, 1): p.cham('saco_rafia', -a + 0.01, a - 0.01, b - 0.02, b + 0.02, *sorted((zs * (c - 0.01), zs * (c + 0.025))), 0.01)


@item('saco_sementes', 'Saco de sementes', 'loot', 'agricultura', recurso='sementes', valor=10, peso_kg=1.0, empilha=4,
      onde=['armazem', 'supermercado', 'casa_de_campo'], efeito='planta 1 canteiro da horta')
def saco_sementes(M):
    p = M.base
    m = trimesh.creation.revolve(np.array([(0, 0.0), (0.07, 0.0), (0.08, 0.02), (0.08, 0.13), (0.06, 0.17), (0.022, 0.19), (0.02, 0.21), (0.0, 0.215)]), sections=24)
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])); m = _fix(m)
    v = m.vertices; v[:, 0] *= 1.0 + 0.05 * np.sin(v[:, 1] * 40); v[:, 2] *= 0.85
    p.add('juta', m)
    anel(p, 'cortica', 0.019, 0.026, 0.185, 0.198, 16)
    p.seg('cortica', (0.024, 0.19, 0.0), (0.06, 0.16, 0.03), 0.004, 0.004)
    p.box('papel', -0.04, 0.04, 0.06, 0.11, 0.068, 0.07)
    for i, cor in enumerate(('livro_4', 'livro_3', 'cortica')):
        p.sphere(cor, 0.004, -0.01 + i * 0.01, 0.003, 0.09, 1)


@item('lata_milho', 'Lata de milho', 'loot', 'comida', recurso='comida', valor=1, peso_kg=0.3, empilha=10,
      onde=['supermercado', 'casas', 'diner', 'armazem'], efeito='fome -20')
def lata_milho(M):
    p = M.base; r, h = 0.037, 0.075
    perf = [(r - 0.003, 0.0), (r, 0.002), (r, 0.006), (r - 0.001, 0.008)]
    for i in range(4): y = 0.014 + i * 0.014; perf += [(r - 0.001, y), (r - 0.0004, y + 0.004), (r - 0.001, y + 0.008)]
    perf += [(r - 0.001, h - 0.006), (r + 0.0005, h - 0.002), (r - 0.001, h), (r - 0.004, h - 0.002), (r - 0.015, h - 0.0025), (0, h - 0.0025)]
    torno(p, 'lata', perf, 40)
    def graos_milho(d):
        for x0 in (40, 552):
            for i in range(18): x = x0 + (i * 23) % 60; y = 90 + (i * 31) % 190; d.ellipse([x, y, x + 20, y + 20], fill=(250, 200, 40), outline=(190, 140, 20))
    mat_imagem('rotulo_milho', rotulo_lata('MILHO', 'VALE VERDE', (40, 120, 60), (240, 200, 50), graos_milho))
    anel(p, 'rotulo_milho', r - 0.0012, r + 0.0006, 0.01, 0.066, 40); p.uv['rotulo_milho'] = uv_cilindro(0.01, 0.066)
    anel(p, 'aco_polido', 0.006, 0.009, h - 0.0025, h - 0.001, 16, 'y', (0.012, 0, 0))


@item('seringa', 'Seringa com antibiótico', 'loot', 'remedios', recurso='remedios', valor=5, peso_kg=0.02, empilha=10,
      onde=['quartel', 'enfermaria', 'casas'], efeito='cura infecção (raro)')
def seringa(M):
    p = M.base; y = 0.009
    anel(p, 'plastico_transp', 0.006, 0.0075, -0.04, 0.03, 20, 'x', (0, y, 0))
    cyl_eixo(p, 'agua', 0.0058, -0.005, 0.028, 'x', (0, y, 0), 16)
    torno(p, 'plastico_transp', [(0.0075, 0.03), (0.003, 0.036), (0.0015, 0.04)], 16, 'x', (0, y, 0))
    cyl_eixo(p, 'aco_polido', 0.0005, 0.04, 0.065, 'x', (0, y, 0), 6)
    torno(p, 'borracha', [(0.0058, -0.012), (0.0058, -0.005)], 16, 'x', (0, y, 0))
    p.box('plastico_branco', -0.07, -0.012, y - 0.0012, y + 0.0012, -0.004, 0.004); p.box('plastico_branco', -0.07, -0.012, y - 0.004, y + 0.004, -0.0012, 0.0012)
    p.cham('plastico_branco', -0.074, -0.07, y - 0.007, y + 0.007, -0.007, 0.007, 0.001)
    p.cham('plastico_transp', -0.045, -0.04, y - 0.009, y + 0.009, -0.012, 0.012, 0.001)
    for k in range(6): p.box('plastico_preto', -0.035 + k * 0.012, -0.0345 + k * 0.012, y + 0.0074, y + 0.0078, -0.002, 0.002)


@item('mascara', 'Máscara de proteção', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=0.05, empilha=10,
      onde=['quartel', 'casas', 'enfermaria', 'galeria'], efeito='reduz chance de doença ao limpar prédios')
def mascara(M):
    p = M.base
    m = trimesh.creation.uv_sphere(radius=1.0, count=[16, 24]); v = m.vertices
    m = trimesh.Trimesh(np.stack([v[:, 0] * 0.085, np.clip(v[:, 1], 0, 1) * 0.035, v[:, 2] * 0.06], 1), m.faces)
    m.update_faces(m.face_normals[:, 1] > -0.5); m.remove_unreferenced_vertices(); p.add('plastico_branco', m)
    p.box('aco_polido', -0.03, 0.03, 0.03, 0.034, 0.03, 0.036)
    for xs in (-1, 1):
        cam = [(xs * 0.083, 0.004, z) for z in (-0.03, 0.03)] + [(xs * 0.12, 0.002, 0.04), (xs * 0.16, 0.002, 0.0), (xs * 0.12, 0.002, -0.04), (xs * 0.083, 0.004, -0.031)]
        for a, b in zip(cam[1:], cam[2:]): p.seg('plastico_branco', a, b, 0.003, 0.002)


@item('kit_costura', 'Lata de costura', 'loot', 'remedios', recurso='tecido', valor=2, peso_kg=0.3, empilha=3,
      onde=['casas', 'motel', 'galeria'], efeito='sutura ferimentos; conserta roupas e mochilas')
def kit_costura(M):
    p = M.base; r, h = 0.075, 0.05
    torno(p, 'lata', [(r - 0.003, 0.0), (r, 0.003), (r, h - 0.012)], 40)
    torno(p, 'plastico_azul', [(r + 0.002, h - 0.016), (r + 0.002, h - 0.001), (r - 0.002, h), (0.0, h)], 40)
    img = Image.new('RGB', (512, 512), (40, 90, 170)); d = ImageDraw.Draw(img)
    d.ellipse([40, 40, 472, 472], outline=(240, 220, 140), width=10)
    for i in range(12): d.ellipse([100 + (i % 4) * 85, 140 + (i // 4) * 85, 160 + (i % 4) * 85, 200 + (i // 4) * 85], fill=[(220, 80, 70), (250, 220, 120), (240, 240, 230)][i % 3])
    texto_c(d, (256, 100), 'COSTURA', 46, (250, 240, 210))
    mat_imagem('tampa_costura', img, 0.35, 0.3)
    p.cyl('tampa_costura', r - 0.008, h, h + 0.0006, sec=40); p.uv['tampa_costura'] = uv_plano(-r, r, -r, r)
    for i, (cor, a) in enumerate((('tecido_vermelho', 0.4), ('papel', 2.4))):
        cx, cz = r + 0.03 + i * 0.035, 0.03 * math.sin(a)
        torno(p, 'madeira_crua', [(0.009, 0.0), (0.009, 0.003), (0.006, 0.004), (0.006, 0.026), (0.009, 0.027), (0.009, 0.03)], 16, 'y', (cx, 0, cz))
        anel(p, cor, 0.006, 0.0085, 0.004, 0.026, 16, 'y', (cx, 0, cz))


@item('bateria_carro', 'Bateria de carro', 'loot', 'energia', recurso='energia', valor=20, peso_kg=15.0, empilha=1,
      onde=['posto', 'garagem', 'quartel', 'estacao'], efeito='guarda energia do gerador ou do cata-vento; liga o rádio')
def bateria_carro(M):
    p = M.base; X, H, Z = 0.13, 0.19, 0.088
    p.cham('plastico_preto', -X, X, 0, H, -Z, Z, 0.006)
    p.cham('plastico_cinza', -X - 0.002, X + 0.002, H - 0.02, H + 0.008, -Z - 0.002, Z + 0.002, 0.004)
    for i in range(6): p.cyl('plastico_amarelo', 0.009, H + 0.008, H + 0.014, x=-X + 0.035 + i * 0.038, z=0.0, sec=12)
    for xs, cor in ((-1, 'plastico_preto'), (1, 'plastico_vermelho')):
        torno(p, 'aco', [(0.009, H + 0.008), (0.008, H + 0.03), (0.0, H + 0.031)], 14, 'y', (xs * (X - 0.03), 0, -Z + 0.03))
        p.cham(cor, xs * (X - 0.03) - 0.018, xs * (X - 0.03) + 0.018, H + 0.008, H + 0.012, -Z + 0.012, -Z + 0.048, 0.002)
    p.box('papel', -0.07, 0.07, 0.06, 0.13, Z, Z + 0.002)
    p.box('plastico_vermelho', -0.07, 0.07, 0.115, 0.13, Z + 0.002, Z + 0.0025)
    varrer(p, 'plastico_preto', Polygon([(-0.006, -0.003), (0.006, -0.003), (0.006, 0.003), (-0.006, 0.003)]),
           [(-0.07, H + 0.008, 0.035), (-0.06, H + 0.05, 0.035), (0.06, H + 0.05, 0.035), (0.07, H + 0.008, 0.035)])
