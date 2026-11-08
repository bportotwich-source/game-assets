# Lote 9: itens unicos dos predios publicos (igreja, biblioteca, escola, correios, delegacia, clinica, banco, quartel).
# Executado por gerar_props.py (mesmas funcoes e materiais).
CORES.update({'veludo_vinho': (70, 12, 18), 'ouro_velho': (170, 130, 50), 'toalha_altar': (240, 238, 228), 'abajur_verde': (10, 50, 24),
              'azul_correio': (10, 30, 80), 'lona_crua': (190, 176, 140), 'aco_cofre': (110, 114, 118), 'bege_medico': (210, 206, 192),
              'vermelho_bombeiro': (110, 6, 4), 'amarelo_bombeiro': (200, 150, 10), 'globo_mar': (40, 90, 140), 'globo_terra': (170, 150, 90)})
METALICOS.update({'ouro_velho': (0.9, 0.35), 'azul_correio': (0.3, 0.5), 'aco_cofre': (0.8, 0.35), 'vermelho_bombeiro': (0.3, 0.45),
                  'bege_medico': (0.2, 0.45)})
FOSCOS.update({'abajur_verde': 0.25, 'amarelo_bombeiro': 0.7, 'globo_mar': 0.4, 'globo_terra': 0.5})
TEX_PROPRIAS += [('veludo_vinho', 'tecido', 0.25, 1024), ('toalha_altar', 'tecido', 0.5, 768), ('lona_crua', 'tecido', 0.5, 768)]


def _tabuas_tampo(p, mat, x0, x1, y0, y1, z0, z1, n=3):
    for k in range(n): p.cham(mat, x0, x1, y0, y1, z0 + k * (z1 - z0) / n + 0.002, z0 + (k + 1) * (z1 - z0) / n - 0.002, 0.004)


# ---------------------------------------------------------------------------- IGREJA
@item('banco_igreja', 'Banco de igreja', 'mobilias', 'igreja', comodos=['igreja', 'patio_missoes'], sentar=True, barricada=True, colisao='caixa',
      vagas=5, modulo_m=3.0, desmonta={'madeira': 4})
def banco_igreja(M):
    p = M.base; L = 1.45; m = 'madeira_escura'
    for xs in (-1, 1):                                                                        # cabeceiras recortadas
        x = xs * L
        p.hull(m, [(x - 0.025, 0, -0.27), (x + 0.025, 0, -0.27), (x - 0.025, 0, 0.27), (x + 0.025, 0, 0.27), (x - 0.025, 0.9, -0.3), (x + 0.025, 0.9, -0.3),
                   (x - 0.025, 0.9, -0.2), (x + 0.025, 0.9, -0.2), (x - 0.025, 0.55, 0.27), (x + 0.025, 0.55, 0.27)])
        p.cham(m, x - 0.035, x + 0.035, 0.88, 0.94, -0.32, -0.16, 0.012)
    _tabuas_tampo(p, m, -L, L, 0.43, 0.47, -0.22, 0.26, 3)
    for k in range(4): p.cham(m, -L, L, 0.55 + k * 0.1, 0.63 + k * 0.1, -0.26 - k * 0.012, -0.235 - k * 0.012, 0.005)
    p.cham(m, -L, L, 0.1, 0.16, -0.05, -0.02, 0.005)
    p.cham(m, -L, L, 0.55, 0.62, 0.27, 0.42, 0.004)                                           # porta-livros atrás do encosto? frente
    p.cham(m, -L, L, 0.08, 0.11, 0.38, 0.55, 0.006)                                           # genuflexório
    for xs in (-1, 1): p.cham(m, xs * (L - 0.05) - 0.03, xs * (L - 0.05) + 0.03, 0.0, 0.11, 0.4, 0.52, 0.004)
    p.uv[m] = uv_caixa(TILE)


@item('altar', 'Altar com toalha', 'mobilias', 'igreja', comodos=['igreja', 'patio_missoes'], colisao='caixa', conteiner=True, slots=3, saque=['velas', 'tecido'])
def altar(M):
    p = M.base; X, Z, H = 1.0, 0.45, 1.0; m = 'madeira'
    p.cham(m, -X, X, 0.0, 0.08, -Z, Z, 0.01); p.cham(m, -X + 0.03, X - 0.03, 0.08, H - 0.05, -Z + 0.03, Z - 0.03, 0.01)
    for x in np.linspace(-X + 0.25, X - 0.25, 4): almofadada(p, m, x - 0.2, x + 0.2, 0.2, H - 0.15, Z - 0.03, Z, borda=0.05)
    p.cham(m, -X - 0.03, X + 0.03, H - 0.05, H, -Z - 0.03, Z + 0.03, 0.01)
    p.box('toalha_altar', -X - 0.035, X + 0.035, H, H + 0.006, -Z - 0.035, Z + 0.035)
    for xs in (-1, 1): p.box('toalha_altar', *sorted((xs * (X + 0.035), xs * (X + 0.04))), H - 0.35, H + 0.006, -Z - 0.035, Z + 0.035)
    p.box('ouro_velho', -X - 0.036, X + 0.036, H - 0.36, H - 0.33, -Z - 0.036, Z + 0.036)
    for x in (-0.6, 0.6): castical_peca(p, x, H + 0.006, 0.0, 0.45)
    p.cham('cartela', -0.15, 0.15, H + 0.006, H + 0.05, -0.1, 0.12, 0.006)                      # livro aberto
    for xs in (-1, 1): p.cham('papel', *sorted((0.0, xs * 0.17)), H + 0.05, H + 0.056, -0.09, 0.11, 0.002)


def castical_peca(p, x, y, z, h, vela=True):
    torno(p, 'ouro_velho', [(0.07, 0.0), (0.07, 0.01), (0.03, 0.03), (0.018, 0.06), (0.025, 0.08), (0.012, 0.1), (0.012, h - 0.06), (0.03, h - 0.05),
                            (0.035, h - 0.03), (0.02, h - 0.02), (0.02, h)], 24, 'y', (x, y, z))
    if vela:
        p.cyl('cera', 0.016, y + h, y + h + 0.16, x=x, z=z, sec=14)
        torno(p, 'cera', [(0.019, y + h + 0.12), (0.02, y + h + 0.15)], 14, 'y', (x, 0, z))
        p.cyl('esmalte_escuro', 0.002, y + h + 0.16, y + h + 0.175, x=x, z=z, sec=6)


@item('castical', 'Castiçal alto', 'mobilias', 'igreja', comodos=['igreja', 'mansao', 'patio_missoes'], portatil=True, peso_kg=4.0, luz_m=3, ambiente=True,
      saque_ao_desmontar={'velas': 1})
def castical(M): castical_peca(M.base, 0, 0, 0, 1.35)


@item('pulpito', 'Púlpito de madeira', 'mobilias', 'igreja', comodos=['igreja', 'escolinha', 'concha'], colisao='caixa')
def pulpito(M):
    p = M.base; m = 'madeira_escura'
    p.cham(m, -0.4, 0.4, 0.0, 0.2, -0.4, 0.4, 0.01)                                            # degrau
    pts = [(0.34 * math.cos(a), 0.34 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
    for i in range(8):
        a0, a1 = pts[i], pts[(i + 1) % 8]
        if i in (5, 6): continue                                                              # abertura atrás
        p.hull(m, [(a0[0], 0.2, a0[1]), (a1[0], 0.2, a1[1]), (a0[0] * 0.92, 0.2, a0[1] * 0.92), (a1[0] * 0.92, 0.2, a1[1] * 0.92),
                   (a0[0] * 1.05, 1.15, a0[1] * 1.05), (a1[0] * 1.05, 1.15, a1[1] * 1.05), (a0[0] * 0.97, 1.15, a0[1] * 0.97), (a1[0] * 0.97, 1.15, a1[1] * 0.97)])
        mx, mz = (a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2
        p.cham('ouro_velho', mx - 0.02, mx + 0.02, 0.5, 0.9, mz - 0.02, mz + 0.02, 0.005) if i == 2 else None
    p.hull(m, [(x, 1.15, z) for x in (-0.3, 0.3) for z in (0.05, 0.38)] + [(x, 1.25, z) for x in (-0.3, 0.3) for z in (0.0, 0.05)])   # estante inclinada
    p.box('cartela', -0.15, 0.15, 1.2, 1.23, 0.12, 0.3)


@item('harmonio', 'Harmônio de pedal', 'mobilias', 'igreja', comodos=['igreja', 'escolinha', 'mansao'], colisao='caixa',
      interacao='tocar (moral +10; muito barulho)')
def harmonio(M):
    p = M.base; X, Z = 0.65, 0.28; m = 'madeira_escura'
    p.cham(m, -X, X, 0.0, 0.95, -Z, Z, 0.012)
    for x in (-0.45, 0.0, 0.45): almofadada(p, m, x - 0.17, x + 0.17, 0.25, 0.75, Z, Z + 0.015, borda=0.04)
    p.cham(m, -X - 0.02, X + 0.02, 0.95, 1.0, -Z, Z + 0.2, 0.008)
    for k in range(36): p.cham('esmalte', -0.5 + k * 0.0278, -0.5 + k * 0.0278 + 0.026, 0.985, 1.0, Z + 0.02, Z + 0.17, 0.002)
    for k in range(25):
        if k % 7 in (2, 6): continue
        x = -0.485 + k * 0.04; p.cham('esmalte_escuro', x - 0.007, x + 0.007, 1.0, 1.02, Z + 0.08, Z + 0.17, 0.002)
    p.cham(m, -X, X, 1.0, 1.45, -Z, -Z + 0.1, 0.01)
    for k in range(8): torno(p, 'louca', [(0.012, 0), (0.012, 0.02), (0.006, 0.03)], 12, 'z', (-0.5 + k * 0.14, 1.35, -Z + 0.1))
    p.cham(m, -X + 0.05, X - 0.05, 1.2, 1.24, -Z + 0.1, -Z + 0.2, 0.004)
    for xs in (-1, 1):
        t = P(); t.cham('veludo_vinho', -0.12, 0.12, -0.02, 0.02, 0.0, 0.3, 0.01)
        p.merge(t, trimesh.transformations.translation_matrix([xs * 0.18, 0.06, Z]) @ trimesh.transformations.rotation_matrix(-0.5, [1, 0, 0]))


@item('pia_batismal', 'Pia batismal de pedra', 'mobilias', 'igreja', comodos=['igreja', 'patio_missoes'], colisao='caixa', coleta={'recurso': 'agua', 'total': 1, 'ferramenta': 'nenhuma', 'segundos_por_unidade': 3})
def pia_batismal(M):
    p = M.base
    torno(p, 'pedra', [(0.3, 0.0), (0.3, 0.08), (0.22, 0.1), (0.12, 0.2), (0.1, 0.6), (0.18, 0.7), (0.32, 0.85), (0.34, 0.95), (0.3, 0.96), (0.27, 0.86), (0.0, 0.8)], 36)
    torno(p, 'agua', [(0.0, 0.87), (0.27, 0.87)], 36)


@item('quadro_hinos', 'Quadro de hinos', 'mobilias', 'igreja', montagem='wall', altura_sugerida_m=1.6, comodos=['igreja'], ambiente=True, colisao='nenhuma')
def quadro_hinos(M):
    p = M.base; W, H = 0.5, 0.75; m = 'madeira_escura'
    p.cham(m, -W / 2, W / 2, 0, H, 0, 0.03, 0.006); p.hull(m, [(-W / 2, H, 0), (W / 2, H, 0), (0, H + 0.12, 0), (-W / 2, H, 0.035), (W / 2, H, 0.035), (0, H + 0.12, 0.035)])
    p.box('esmalte_escuro', -W / 2 + 0.04, W / 2 - 0.04, 0.05, H - 0.05, 0.03, 0.032)
    img = Image.new('RGB', (512, 96), (240, 240, 232)); d = ImageDraw.Draw(img)
    mat_imagem('numeros_hino', img, 0.6)
    for k, n in enumerate(('112', '47', '205', '9')):
        img = Image.new('RGB', (256, 96), (20, 20, 20)); d = ImageDraw.Draw(img); texto_c(d, (128, 48), n, 70, (240, 240, 230)); mat_imagem(f'hino_{k}', img, 0.6)
        y = 0.12 + k * 0.15; p.box(f'hino_{k}', -0.18, 0.18, y, y + 0.11, 0.032, 0.036)
        p.uv[f'hino_{k}'] = (lambda y: (lambda v, n: np.stack([(v[:, 0] + 0.18) / 0.36, (v[:, 1] - y) / 0.11], 1)))(y)
        p.cham(m, -0.21, 0.21, y - 0.012, y, 0.03, 0.05, 0.003)


# ---------------------------------------------------------------------------- BIBLIOTECA
@item('estante_biblioteca', 'Estante alta de biblioteca (dupla face)', 'mobilias', 'biblioteca', comodos=['biblioteca', 'escolinha', 'mansao'], conteiner=True,
      slots=6, saque=['livros'], barricada=True, colisao='caixa', modulo_m=1.0)
def estante_biblioteca(M):
    p = M.base; X, H, Z = 0.48, 2.2, 0.3; m = 'madeira_escura'; rng = np.random.default_rng(17)
    for xs in (-1, 1): p.cham(m, xs * X - 0.025 * xs - 0.0125, xs * X - 0.025 * xs + 0.0125, 0.0, H, -Z, Z, 0.004) if False else p.cham(m, *sorted((xs * X, xs * (X - 0.03))), 0.0, H, -Z, Z, 0.005)
    p.cham(m, -X - 0.02, X + 0.02, H, H + 0.05, -Z - 0.02, Z + 0.02, 0.008); p.box(m, -X, X, 0.0, 0.1, -Z + 0.01, Z - 0.01)
    p.box(m, -X + 0.03, X - 0.03, 0.1, H, -0.006, 0.006)
    niveis = [0.1, 0.5, 0.9, 1.3, 1.7]
    for y in niveis[1:] + [H - 0.02]: p.box(m, -X + 0.03, X - 0.03, y, y + 0.022, -Z + 0.005, Z - 0.005)
    for zs in (-1, 1):
        for y in niveis:
            x = -X + 0.04
            while x < X - 0.06:
                w = rng.uniform(0.02, 0.045); h = rng.uniform(0.24, 0.34); d_ = rng.uniform(0.17, 0.24)
                if rng.random() < 0.1: x += w * 2; continue
                c = f'livro_{rng.integers(1, 7)}'; z0, z1 = sorted((zs * 0.008, zs * (0.008 + d_)))
                p.box(c, x, x + w, y + 0.022, y + 0.022 + h, z0, z1); x += w + 0.002
    p.uv.update({f'livro_{i}': uv_caixa(0.25) for i in range(1, 7)})
    for zs in (-1, 1): p.box('ouro_velho', -0.05, 0.05, H - 0.15, H - 0.1, *sorted((zs * Z, zs * (Z + 0.003))))


@item('mesa_leitura', 'Mesa de leitura com luminárias verdes', 'mobilias', 'biblioteca', comodos=['biblioteca', 'escritorio', 'delegacia', 'mansao'], colisao='caixa',
      vagas=4, estacao='pesquisa (lê livros técnicos: desbloqueia projetos)', luz_m=2)
def mesa_leitura(M):
    p = M.base; X, Z, H = 1.2, 0.5, 0.76; m = 'madeira'
    _tabuas_tampo(p, m, -X, X, H - 0.04, H, -Z, Z, 4); p.cham(m, -X + 0.05, X - 0.05, H - 0.14, H - 0.04, -Z + 0.05, Z - 0.05, 0.006)
    for xs in (-1, 1):
        for zs in (-1, 1): pe_torneado(p, m, xs * (X - 0.1), zs * (Z - 0.08), 0.0, H - 0.14, 0.035)
    for x in (-0.6, 0.6):
        torno(p, 'ouro_velho', [(0.07, H), (0.07, H + 0.015), (0.015, H + 0.03), (0.012, H + 0.3)], 20, 'y', (x, 0, 0))
        p.hull('abajur_verde', [(x + dx, H + 0.3, z) for dx in (-0.2, 0.2) for z in (-0.06, 0.06)] + [(x + dx, H + 0.4, z) for dx in (-0.19, 0.19) for z in (-0.02, 0.02)])
        p.box('lamp_glass', x - 0.18, x + 0.18, H + 0.298, H + 0.302, -0.05, 0.05)
    for k, (x, z, a) in enumerate(((-0.9, 0.25, 0.2), (0.3, -0.2, -0.4), (0.95, 0.15, 0.6))):
        t = P(); c = f'livro_{k + 2}'; t.cham(c, -0.1, 0.1, 0, 0.035, -0.14, 0.14, 0.003); t.box('papel', -0.094, 0.1, 0.003, 0.032, -0.135, 0.135)
        p.merge(t, trimesh.transformations.translation_matrix([x, H, z]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]))


@item('fichario_catalogo', 'Fichário de catálogo', 'mobilias', 'biblioteca', comodos=['biblioteca', 'correios', 'delegacia'], conteiner=True, slots=2,
      saque=['mapas', 'papel'], colisao='caixa', pista='fichas apontam livros técnicos raros')
def fichario_catalogo(M):
    p = M.base; X, Z = 0.5, 0.25; m = 'madeira'
    for xs in (-1, 1):
        for zs in (-1, 1): pe_torneado(p, m, xs * (X - 0.05), zs * (Z - 0.05), 0.0, 0.5, 0.03)
    p.cham(m, -X, X, 0.5, 1.2, -Z, Z, 0.008); p.cham(m, -X - 0.02, X + 0.02, 1.2, 1.24, -Z - 0.02, Z + 0.02, 0.006)
    for i in range(5):
        for j in range(5):
            x0 = -X + 0.025 + i * 0.19; y0 = 0.52 + j * 0.135
            nm = f'gaveta_{i}_{j}'
            if (i, j) in ((1, 3), (3, 1)):
                q = M.parte(nm, (0, 0, 0), 'gaveta', desliza=[0, 0, 0.3])
            else: q = p
            q.cham(m, x0, x0 + 0.18, y0, y0 + 0.125, Z - 0.01, Z + 0.01, 0.003)
            q.box('papel', x0 + 0.06, x0 + 0.12, y0 + 0.07, y0 + 0.1, Z + 0.01, Z + 0.012)
            torno(q, 'ouro_velho', [(0.006, 0), (0.006, 0.006), (0.01, 0.012), (0.0, 0.014)], 10, 'z', (x0 + 0.09, y0 + 0.04, Z + 0.01))
            if q is not p:
                carcaca(q, m, x0 + 0.01, x0 + 0.17, y0 + 0.01, y0 + 0.115, -Z + 0.03, Z - 0.01, t=0.008, topo=False)
                for k in range(14): q.box('papel', x0 + 0.02, x0 + 0.16, y0 + 0.018, y0 + 0.1, -Z + 0.05 + k * 0.025, -Z + 0.051 + k * 0.025)


@item('carrinho_livros', 'Carrinho de livros', 'mobilias', 'biblioteca', comodos=['biblioteca', 'escolinha', 'clinica'], conteiner=True, slots=3, saque=['livros'],
      portatil=True, peso_kg=15.0, colisao='caixa')
def carrinho_livros(M):
    p = M.base; X, Z = 0.4, 0.22; m = 'madeira'; rng = np.random.default_rng(23)
    for xs in (-1, 1):
        p.hull(m, [(xs * X, 0.12, z) for z in (-Z, Z)] + [(xs * X, 0.95, z) for z in (-0.06, 0.06)] + [(xs * (X - 0.02), 0.12, z) for z in (-Z, Z)] + [(xs * (X - 0.02), 0.95, z) for z in (-0.06, 0.06)])
        for zs in (-1, 1): _roda(p, (xs * (X - 0.05), 0.05, zs * (Z - 0.03)), 0.05, 0.03, mat_aro='aco')
    for zs in (-1, 1):
        for y0, y1, z0 in ((0.15, 0.45, Z), (0.55, 0.85, 0.12)):
            t = P(); t.cham(m, -X + 0.02, X - 0.02, -0.012, 0.012, 0, z0 * 1.0 + 0.0, 0.003)
            p.box(m, -X + 0.02, X - 0.02, y0, y0 + 0.02, *sorted((0, zs * z0)))
            x = -X + 0.03
            while x < X - 0.05:
                w = rng.uniform(0.025, 0.045); h = rng.uniform(0.2, 0.28)
                p.hull(f'livro_{rng.integers(1, 7)}', [(x, y0 + 0.02, zz) for zz in sorted((zs * 0.01, zs * z0 * 0.95))] + [(x + w, y0 + 0.02, zz) for zz in sorted((zs * 0.01, zs * z0 * 0.95))] +
                       [(x, y0 + 0.02 + h, zz) for zz in sorted((zs * 0.03, zs * z0 * 0.95))] + [(x + w, y0 + 0.02 + h, zz) for zz in sorted((zs * 0.03, zs * z0 * 0.95))])
                x += w + 0.003
    cyl_eixo(p, 'ouro_velho', 0.012, -X, X, 'x', (0, 0.97, 0), 12)


@item('globo_terrestre', 'Globo terrestre de mesa', 'mobilias', 'biblioteca', comodos=['biblioteca', 'escolinha', 'escritorio', 'mansao'], portatil=True, peso_kg=2.0, ambiente=True, colisao='nenhuma')
def globo_terrestre(M):
    p = M.base; R = 0.15; c = (0, 0.24, 0)
    img = Image.new('RGB', (512, 256), (40, 90, 140)); d = ImageDraw.Draw(img); rng = np.random.default_rng(29)
    for _ in range(9):
        x, y = rng.integers(0, 512), rng.integers(40, 216); pts = [(x + 60 * math.cos(a) * rng.uniform(0.4, 1.2), y + 40 * math.sin(a) * rng.uniform(0.4, 1.2)) for a in np.linspace(0, 2 * math.pi, 12)]
        d.polygon(pts, fill=(170, 150, 90))
    for k in range(1, 8): d.line([(0, k * 32), (512, k * 32)], fill=(200, 200, 180), width=1)
    for k in range(12): d.line([(k * 43, 0), (k * 43, 256)], fill=(200, 200, 180), width=1)
    mat_imagem('mapa_globo', img, 0.45)
    s = trimesh.creation.uv_sphere(radius=R, count=[24, 36]); s.apply_translation(c); p.add('mapa_globo', s)
    def uvg(v, n):
        q = v - np.array(c); u = (np.arctan2(q[:, 2], q[:, 0]) / (2 * np.pi)) % 1; return np.stack([_sem_costura(u), 0.5 + np.arcsin(np.clip(q[:, 1] / R, -1, 1)) / np.pi], 1)
    p.uv['mapa_globo'] = uvg
    torno(p, 'madeira_escura', [(0.1, 0.0), (0.1, 0.02), (0.05, 0.04), (0.02, 0.06), (0.015, 0.08)], 24)
    t = P(); anel(t, 'ouro_velho', R + 0.008, R + 0.016, -0.005, 0.005, 40, 'z', (0, 0, 0))
    p.merge(t, trimesh.transformations.translation_matrix(c) @ _rz(0.41))
    p.seg('ouro_velho', (0, 0.08, 0), (0.0, 0.24 - R - 0.012, 0.0), 0.012)


# ---------------------------------------------------------------------------- ESCOLINHA
@item('carteira_escolar', 'Carteira escolar com banco', 'mobilias', 'escolinha', comodos=['escolinha'], sentar=True, colisao='caixa', conteiner=True, slots=1,
      saque=['livros', 'papel'], desmonta={'madeira': 1, 'sucata': 1})
def carteira_escolar(M):
    p = M.base; m = 'madeira'; f = 'esmalte_escuro'
    for xs in (-1, 1):                                                                        # lateral de ferro fundido em S
        x = xs * 0.3
        varrer(p, f, Polygon([(-0.012, -0.02), (0.012, -0.02), (0.012, 0.02), (-0.012, 0.02)]), [(x, 0.0, 0.35), (x, 0.4, 0.3), (x, 0.7, 0.25), (x, 0.72, 0.05)])
        varrer(p, f, Polygon([(-0.012, -0.02), (0.012, -0.02), (0.012, 0.02), (-0.012, 0.02)]), [(x, 0.0, -0.05), (x, 0.4, 0.0), (x, 0.42, -0.25), (x, 0.0, -0.4)])
        varrer(p, f, Polygon([(-0.012, -0.015), (0.012, -0.015), (0.012, 0.015), (-0.012, 0.015)]), [(x, 0.42, -0.3), (x, 0.72, -0.38)])
        p.cham(f, x - 0.02, x + 0.02, 0.0, 0.02, -0.42, 0.38, 0.004)
    t = P(); t.cham(m, -0.33, 0.33, -0.015, 0.015, -0.2, 0.2, 0.005)                          # tampo inclinado
    p.merge(t, trimesh.transformations.translation_matrix([0, 0.73, 0.18]) @ trimesh.transformations.rotation_matrix(0.12, [1, 0, 0]))
    p.cham(m, -0.33, 0.33, 0.6, 0.62, 0.05, 0.35, 0.004); p.cham(m, -0.33, 0.33, 0.62, 0.7, 0.34, 0.36, 0.004)
    torno(p, 'esmalte_escuro', [(0.018, 0.0), (0.018, 0.02), (0.0, 0.021)], 14, 'y', (0.22, 0.735, 0.0)) if False else p.cyl('vidro_escuro', 0.017, 0.745, 0.75, x=0.22, z=0.04, sec=14)
    for k in range(3): p.cham(m, -0.3, 0.3, 0.41, 0.44, -0.36 + k * 0.09, -0.28 + k * 0.09, 0.004)
    for k in range(2): p.cham(m, -0.3, 0.3, 0.55 + k * 0.1, 0.62 + k * 0.1, -0.37 - k * 0.012, -0.35 - k * 0.012, 0.004)


@item('mesa_professor', 'Mesa do professor', 'mobilias', 'escolinha', comodos=['escolinha', 'escritorio', 'correios'], conteiner=True, slots=4,
      saque=['livros', 'remedios', 'papel'], colisao='caixa')
def mesa_professor(M):
    p = M.base; X, Z, H = 0.65, 0.38, 0.76; m = 'madeira'
    _tabuas_tampo(p, m, -X, X, H - 0.035, H, -Z, Z, 3)
    for xs in (-1, 1): carcaca(p, m, *sorted((xs * X, xs * 0.25)), 0.0, H - 0.035, -Z + 0.02, Z - 0.02, t=0.02, topo=False)
    p.cham(m, -0.25, 0.25, 0.4, H - 0.035, -Z + 0.02, -Z + 0.04, 0.004)
    for xs in (-1, 1):
        for j in range(3):
            y0 = 0.05 + j * 0.22; x0, x1 = sorted((xs * (X - 0.02), xs * 0.27))
            q = M.parte(f'gaveta_{"esq" if xs < 0 else "dir"}_{j + 1}', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.3]) if j == 0 else p
            q.cham(m, x0, x1, y0, y0 + 0.2, Z - 0.02, Z, 0.004); pegador(q, 'ouro_velho', (x0 + x1) / 2, y0 + 0.1, Z)
            if q is not p: carcaca(q, m, x0 + 0.01, x1 - 0.01, y0 + 0.01, y0 + 0.18, -Z + 0.05, Z - 0.02, t=0.012, topo=False)
    p.sphere('tomate', 0.04, 0.4, H + 0.04, -0.1, 2) if False else fofo(p, 'tinta_vermelha', 0.4, H + 0.04, -0.1, 0.04, 0.038, 0.04, 0.9, 0.9, (12, 14))   # maçã
    p.seg('madeira_escura', (0.4, H + 0.078, -0.1), (0.405, H + 0.095, -0.1), 0.004)
    for k in range(3):
        t = P(); c = f'livro_{k + 1}'; t.cham(c, -0.09, 0.09, 0, 0.03, -0.13, 0.13, 0.003); p.merge(t, trimesh.transformations.translation_matrix([-0.4, H + k * 0.03, 0.0]) @ trimesh.transformations.rotation_matrix(0.1 * k, [0, 1, 0]))
    castical_peca(p, 0.1, H, -0.25, 0.08, vela=False) if False else p.cyl('cobre', 0.035, H, H + 0.07, x=0.1, z=-0.25, sec=16)   # sino de mão
    torno(p, 'cobre', [(0.04, H), (0.03, H + 0.05), (0.012, H + 0.08), (0.0, H + 0.085)], 20, 'y', (0.1, 0, -0.25)); p.cyl('madeira_escura', 0.01, H + 0.085, H + 0.15, x=0.1, z=-0.25, sec=10)


@item('lousa_escola', 'Lousa com giz', 'mobilias', 'escolinha', montagem='wall', altura_sugerida_m=0.8, comodos=['escolinha', 'quartel', 'abrigo'], ambiente=True, colisao='nenhuma')
def lousa_escola(M):
    p = M.base; W, H = 2.4, 1.1
    img = Image.new('RGB', (1200, 550), (26, 44, 34)); d = ImageDraw.Draw(img); g = (226, 226, 216)
    texto_c(d, (600, 70), 'A  B  C  D  E  F  G  H', 60, g, False)
    d.text((80, 160), '2 + 3 = 5', font=fonte(54, False), fill=g); d.text((80, 240), '7 - 4 = 3', font=fonte(54, False), fill=g)
    d.text((620, 170), 'Prova sexta-feira', font=fonte(46, False), fill=g); d.text((620, 250), 'Não corram no pátio!', font=fonte(46, False), fill=g)
    for _ in range(40): x = np.random.default_rng(_).integers(0, 1200); d.line([(int(x), 380), (int(x) + 80, 470)], fill=(60, 74, 66), width=30)   # apagado
    mat_imagem('lousa_img', img, 0.85)
    p.box('lousa_img', -W / 2, W / 2, 0, H, 0, 0.015); p.uv['lousa_img'] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)
    for (x0, x1, y0, y1) in ((-W / 2 - 0.05, W / 2 + 0.05, -0.05, 0.0), (-W / 2 - 0.05, W / 2 + 0.05, H, H + 0.05), (-W / 2 - 0.05, -W / 2, 0, H), (W / 2, W / 2 + 0.05, 0, H)):
        p.cham('madeira', x0, x1, y0, y1, 0.0, 0.03, 0.006)
    p.cham('madeira', -W / 2, W / 2, -0.07, -0.05, 0.0, 0.08, 0.004)
    p.cham('feltro' if 'feltro' in CORES else 'cobertor_cinza', 0.6, 0.75, -0.05, -0.02, 0.02, 0.07, 0.006)
    for k in range(4): cyl_eixo(p, 'giz', 0.005, -0.4 + k * 0.07, -0.34 + k * 0.07, 'x', (0, -0.044, 0.05), 8)


@item('estufa_lenha', 'Estufa a lenha', 'mobilias', 'escolinha', comodos=['escolinha', 'igreja', 'fazenda', 'abrigo', 'casa_de_campo'], colisao='caixa', usa='lenha',
      estacao='aquecer (frio da noite) e cozinhar', luz_m=2)
def estufa_lenha(M):
    p = M.base; m = 'esmalte_escuro'
    torno(p, m, [(0.2, 0.15), (0.22, 0.17), (0.22, 0.2), (0.26, 0.3), (0.28, 0.5), (0.26, 0.7), (0.22, 0.8), (0.24, 0.82), (0.24, 0.86), (0.18, 0.9), (0.08, 0.92)], 32)
    for k in range(4): a = k / 4 * 2 * math.pi + 0.785; p.seg(m, (0.15 * math.cos(a), 0.17, 0.15 * math.sin(a)), (0.26 * math.cos(a), 0.0, 0.26 * math.sin(a)), 0.03)
    p.cyl(m, 0.06, 0.92, 2.4, sec=20); anel(p, m, 0.06, 0.07, 1.6, 1.63, 20)
    q = M.parte('portinhola', (0.12, 0.4, 0.24), 'porta', eixo='y', abre_graus=-100)
    q.hull(m, [(x, y, 0.24 + 0.03 * math.cos((x + 0.0) * 3)) for x in (-0.12, 0.12) for y in (0.3, 0.52)] + [(x, y, 0.27) for x in (-0.1, 0.1) for y in (0.32, 0.5)])
    for k in range(5): q.box('esmalte', -0.08 + k * 0.035, -0.07 + k * 0.035, 0.36, 0.46, 0.27, 0.275)
    q.cham('cobre', -0.1, -0.06, 0.4, 0.42, 0.27, 0.3, 0.004)
    p.cham('brasa', -0.1, 0.1, 0.32, 0.36, 0.1, 0.24, 0.01)
    p.cham('aco', -0.4, 0.4, 0.0, 0.006, -0.4, 0.5, 0.002)


@item('cabide_lancheiras', 'Cabideiro com lancheiras', 'mobilias', 'escolinha', montagem='wall', altura_sugerida_m=1.2, comodos=['escolinha'], ambiente=True,
      conteiner=True, slots=2, saque=['comida'], colisao='nenhuma')
def cabide_lancheiras(M):
    p = M.base; W = 1.6
    p.cham('madeira', -W / 2, W / 2, 0, 0.12, 0, 0.025, 0.005)
    cores = ['tinta_vermelha', 'tinta_azul', 'tinta_verde', 'tinta_amarela', 'cobertor', 'tecido_sofa']
    for k in range(7):
        x = -W / 2 + 0.12 + k * 0.23; p.seg('ouro_velho', (x, 0.06, 0.025), (x, 0.09, 0.1), 0.012)
        if k in (0, 2, 3, 5):
            c = cores[k % 6]; p.cham(c, x - 0.1, x + 0.1, -0.18, -0.03, 0.03, 0.12, 0.012)
            varrer(p, 'aco', circ(0.003, 6), [(x - 0.04, -0.03, 0.075), (x, 0.06, 0.09), (x + 0.04, -0.03, 0.075)])
        elif k == 4:
            fofo(p, 'cobertor_cinza', x, -0.25, 0.08, 0.12, 0.3, 0.04, 0.6, 0.6, (10, 14))      # casaco pendurado


# ---------------------------------------------------------------------------- CORREIOS
@item('caixa_correio_rua', 'Caixa de correio de rua', 'mobilias', 'correios', comodos=['rua', 'correios', 'rodoviaria', 'estacao'], ambiente=True, colisao='caixa',
      conteiner=True, slots=3, saque=['papel', 'mapas', 'pistas'], ferramenta='pe_de_cabra', pista='cartas nunca entregues contam histórias')
def caixa_correio_rua(M):
    p = M.base; X, Z = 0.25, 0.25; m = 'azul_correio'
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham(m, xs * (X - 0.03) - 0.025, xs * (X - 0.03) + 0.025, 0.0, 0.35, zs * (Z - 0.03) - 0.025, zs * (Z - 0.03) + 0.025, 0.006)
    p.cham(m, -X, X, 0.3, 1.05, -Z, Z, 0.015)
    t = trimesh.creation.cylinder(radius=X, height=2 * Z, sections=32); t.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); t.apply_translation([0, 1.05, 0])
    t = trimesh.intersections.slice_mesh_plane(t, [0, 1, 0], [0, 1.05, 0], cap=True); p.add(m, t)
    q = M.parte('portinhola', (0, 1.1, Z), 'tampa', eixo='x', abre_graus=-60)
    q.cham(m, -0.18, 0.18, 1.05, 1.2, Z - 0.005, Z + 0.025, 0.01); q.cham('aco_polido', -0.08, 0.08, 1.15, 1.17, Z + 0.025, Z + 0.04, 0.004)
    p.box('esmalte_escuro', -0.16, 0.16, 1.07, 1.18, Z - 0.004, Z + 0.001)
    img = Image.new('RGB', (256, 160), (10, 30, 80)); d = ImageDraw.Draw(img); d.rectangle([10, 10, 246, 150], outline=(240, 240, 240), width=5)
    d.polygon([(40, 50), (216, 50), (216, 120), (40, 120)], outline=(240, 240, 240), width=6); d.line([(40, 50), (128, 95), (216, 50)], fill=(240, 240, 240), width=6)
    mat_imagem('selo_correio', img, 0.5)
    p.box('selo_correio', -0.15, 0.15, 0.6, 0.79, Z, Z + 0.002); p.uv['selo_correio'] = lambda v, n: np.stack([(v[:, 0] + 0.15) / 0.3, (v[:, 1] - 0.6) / 0.19], 1)
    p.cham('aco', -0.05, 0.05, 0.4, 0.46, Z, Z + 0.02, 0.004)


@item('carrinho_correspondencia', 'Carrinho de correspondência', 'mobilias', 'correios', comodos=['correios', 'estacao', 'rodoviaria'], conteiner=True, slots=4,
      saque=['papel', 'roupas', 'pistas'], portatil=True, peso_kg=20.0, colisao='caixa')
def carrinho_correspondencia(M):
    p = M.base; X, Z, H = 0.45, 0.32, 0.85
    for xs in (-1, 1):
        for zs in (-1, 1):
            p.cyl('aco_pintado', 0.015, 0.12, H, x=xs * X, z=zs * Z, sec=12); _roda(p, (xs * X, 0.06, zs * Z), 0.06, 0.03, 'x', mat_aro='aco')
    for y in (0.18, H):
        for zs in (-1, 1): cyl_eixo(p, 'aco_pintado', 0.013, -X, X, 'x', (0, y, zs * Z), 12)
        for xs in (-1, 1): cyl_eixo(p, 'aco_pintado', 0.013, -Z, Z, 'z', (xs * X, y, 0), 12)
    p.hull('lona_crua', [(x, 0.2, z) for x in (-X + 0.02, X - 0.02) for z in (-Z + 0.02, Z - 0.02)] + [(x, H - 0.02, z) for x in (-X + 0.02, X - 0.02) for z in (-Z + 0.02, Z - 0.02)])
    for k, (x, z) in enumerate(((-0.2, -0.1), (0.15, 0.08), (0.0, -0.15))): fofo(p, 'lona_crua', x, H + 0.05, z, 0.18, 0.1, 0.14, 0.6, 0.6, (12, 14))
    for k in range(6): p.box('papel', -0.3 + k * 0.1, -0.22 + k * 0.1, H + 0.12, H + 0.125, -0.05, 0.08)


@item('saco_correio', 'Saco de correspondência', 'loot', 'pistas', recurso='pista', valor=1, peso_kg=4.0, empilha=1,
      onde=['correios', 'estacao', 'rodoviaria'], efeito='cartas e pacotes: chance de remédios, pilhas ou uma pista de sobreviventes')
def saco_correio(M):
    p = M.base
    fofo(p, 'lona_crua', 0, 0.12, 0, 0.42, 0.12, 0.2, 0.55, 0.55, (14, 22))
    torno(p, 'lona_crua', [(0.05, -0.0), (0.03, 0.06), (0.06, 0.09)], 14, 'x', (0.42, 0.12, 0))
    anel(p, 'couro' if 'couro' in CORES else 'madeira_escura', 0.032, 0.04, 0.44, 0.47, 14, 'x', (0, 0.12, 0))
    for x in np.linspace(-0.3, 0.3, 3): anel(p, 'azul_correio', 0.2, 0.205, x - 0.015, x + 0.015, 24, 'x', (0, 0.12, 0))
    p.box('papel', -0.1, 0.1, 0.235, 0.238, -0.06, 0.06)


@item('balanca_correio', 'Balança de balcão', 'mobilias', 'correios', comodos=['correios', 'padaria', 'armazem', 'supermercado'], portatil=True, peso_kg=6.0, ambiente=True, colisao='nenhuma')
def balanca_correio(M):
    p = M.base; m = 'esmalte'
    p.cham(m, -0.18, 0.18, 0.0, 0.08, -0.15, 0.15, 0.015)
    p.hull(m, [(x, 0.08, z) for x in (-0.12, 0.12) for z in (-0.13, -0.02)] + [(x, 0.3, z) for x in (-0.1, 0.1) for z in (-0.12, -0.06)])
    torno(p, 'aco_polido', [(0.1, 0.0), (0.1, 0.02), (0.0, 0.021)], 32, 'z', (0, 0.22, -0.055))
    img = Image.new('RGB', (256, 256), (246, 244, 236)); d = ImageDraw.Draw(img)
    for k in range(11): a = math.pi * (0.75 + 1.5 * k / 10); d.line([(128 + 110 * math.cos(a), 128 + 110 * math.sin(a)), (128 + 90 * math.cos(a), 128 + 90 * math.sin(a))], fill=(20, 20, 20), width=4)
    d.line([(128, 128), (128 + 90 * math.cos(math.pi * 1.1), 128 + 90 * math.sin(math.pi * 1.1))], fill=(200, 20, 20), width=5)
    mat_imagem('mostrador_balanca', img, 0.4)
    torno(p, 'mostrador_balanca', [(0.09, 0.0205), (0.09, 0.022)], 32, 'z', (0, 0.22, -0.055)); p.uv['mostrador_balanca'] = lambda v, n: np.stack([(v[:, 0] + 0.09) / 0.18, (v[:, 1] - 0.13) / 0.18], 1)
    p.cyl('aco', 0.015, 0.08, 0.1, x=0, z=0.06, sec=12); p.cham('aco_polido', -0.14, 0.14, 0.1, 0.11, -0.04, 0.15, 0.004)


@item('estante_triagem', 'Escaninho de triagem de cartas', 'mobilias', 'correios', comodos=['correios', 'hotel', 'estacao'], conteiner=True, slots=3,
      saque=['papel', 'pistas', 'chaves'], colisao='caixa')
def estante_triagem(M):
    p = M.base; X, Z = 0.9, 0.3; m = 'madeira'; rng = np.random.default_rng(31)
    p.cham(m, -X, X, 0.0, 0.85, -Z, Z, 0.008); p.cham(m, -X - 0.02, X + 0.02, 0.85, 0.89, -Z - 0.02, Z + 0.04, 0.006)
    n, mrows = 10, 6; cw = 2 * X / n; ch = 0.12
    carcaca(p, m, -X, X, 0.89, 0.89 + mrows * ch + 0.02, -Z, -Z + 0.3, t=0.015)
    for i in range(1, n): p.box(m, -X + i * cw - 0.004, -X + i * cw + 0.004, 0.89, 0.89 + mrows * ch, -Z + 0.01, -Z + 0.3)
    for j in range(1, mrows): p.box(m, -X, X, 0.89 + j * ch - 0.004, 0.89 + j * ch + 0.004, -Z + 0.01, -Z + 0.3)
    for i in range(n):
        for j in range(mrows):
            if rng.random() < 0.5:
                x = -X + i * cw + 0.02; y = 0.89 + j * ch + 0.006
                for k in range(int(rng.integers(1, 4))): p.box('papel', x, x + cw - 0.04, y + k * 0.008, y + 0.004 + k * 0.008, -Z + 0.03, -Z + 0.27)
            img_k = None
    for i in range(n): p.box('papel', -X + i * cw + 0.03, -X + (i + 1) * cw - 0.03, 0.89 + mrows * ch + 0.002, 0.89 + mrows * ch + 0.018, -Z + 0.3, -Z + 0.302)


# ---------------------------------------------------------------------------- DELEGACIA
@item('mesa_maquina_escrever', 'Mesa com máquina de escrever', 'mobilias', 'delegacia', comodos=['delegacia', 'escritorio', 'correios', 'quartel'], conteiner=True,
      slots=3, saque=['papel', 'chaves', 'armas'], colisao='caixa')
def mesa_maquina_escrever(M):
    p = M.base; X, Z, H = 0.7, 0.38, 0.76; m = 'aco_cinza' if 'aco_cinza' in CORES else 'aco_pintado'
    p.cham('madeira', -X, X, H - 0.03, H, -Z, Z, 0.006)
    carcaca(p, m, 0.25, X - 0.02, 0.0, H - 0.03, -Z + 0.02, Z - 0.02, t=0.015, topo=False)
    for xs in (-1,): p.cham(m, -X + 0.02, -X + 0.06, 0.0, H - 0.03, -Z + 0.02, Z - 0.02, 0.004)
    for j in range(3):
        y0 = 0.04 + j * 0.23; q = M.parte('gaveta_1', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.32]) if j == 2 else p
        q.cham(m, 0.27, X - 0.04, y0, y0 + 0.21, Z - 0.02, Z, 0.004); q.cham('aco_polido', 0.42, 0.52, y0 + 0.14, y0 + 0.16, Z, Z + 0.015, 0.003)
        if q is not p:
            carcaca(q, m, 0.28, X - 0.05, y0 + 0.01, y0 + 0.2, -Z + 0.05, Z - 0.02, t=0.01, topo=False)
            q.cham('esmalte_escuro', 0.35, 0.55, y0 + 0.02, y0 + 0.06, -0.1, 0.15, 0.01)        # revólver de serviço? só a caixa
    mx, mz = -0.2, 0.0                                                                          # máquina de escrever
    p.hull('esmalte_escuro', [(mx + x, H, mz + z) for x in (-0.18, 0.18) for z in (-0.12, 0.16)] + [(mx + x, H + 0.11, mz + z) for x in (-0.16, 0.16) for z in (-0.1, 0.0)] +
           [(mx + x, H + 0.05, mz + 0.16) for x in (-0.17, 0.17)])
    for r_ in range(4):
        for k in range(10):
            p.cyl('esmalte', 0.008, H + 0.04 + r_ * 0.012, H + 0.055 + r_ * 0.012, x=mx - 0.13 + k * 0.028 + r_ * 0.006, z=mz + 0.13 - r_ * 0.03, sec=10)
    cyl_eixo(p, 'borracha', 0.025, mx - 0.2, mx + 0.2, 'x', (0, H + 0.13, mz - 0.07), 20)
    p.box('papel', mx - 0.1, mx + 0.1, H + 0.12, H + 0.3, mz - 0.1, mz - 0.098)
    p.cham('papel', 0.3, 0.6, H, H + 0.04, -0.2, 0.1, 0.002); p.cyl('louca', 0.04, H, H + 0.09, x=-0.55, z=0.2, sec=16)


@item('armario_armas', 'Armário de armas', 'mobilias', 'delegacia', comodos=['delegacia', 'quartel'], conteiner=True, slots=6, saque=['armas', 'municao'],
      trancado=True, ferramenta='pe_de_cabra ou chave', colisao='caixa', barricada=True)
def armario_armas(M):
    p = M.base; X, Z0, Z1, H, m = 0.5, -0.22, 0.22, 1.9, 'aco_pintado'
    carcaca(p, m, -X, X, 0.05, H, Z0, Z1, t=0.015)
    for k in range(5):                                                                        # suporte com coronhas
        x = -0.35 + k * 0.175; p.cham('madeira_escura', x - 0.04, x + 0.04, 0.1, 0.35, -0.12, 0.05, 0.01)
        p.cham('esmalte_escuro', x - 0.012, x + 0.012, 0.35, 1.25, -0.06, -0.02, 0.004)
    p.cham(m, -X + 0.015, X - 0.015, 1.3, 1.315, Z0 + 0.01, Z1 - 0.01, 0.002)
    for k in range(4): p.cham('cartela', -0.4 + k * 0.2, -0.25 + k * 0.2, 1.315, 1.4, -0.1, 0.08, 0.004)   # caixas de munição
    p.cham('esmalte_escuro', -X, X, 0.0, 0.05, Z0, Z1, 0.004)
    for nome, hx, sgn in (('porta_esq', -X, 1), ('porta_dir', X, -1)):
        q = M.parte(nome, (hx, 0, Z1 + 0.012), 'porta', eixo='y', abre_graus=-110 * sgn)
        x0, x1 = sorted((hx, sgn * 0.002)); q.cham(m, x0, x1, 0.06, H - 0.01, Z1, Z1 + 0.018, 0.004)
        for y in np.linspace(0.4, 1.6, 9): q.box('esmalte_escuro', x0 + 0.06, x1 - 0.06, y, y + 0.012, Z1 + 0.017, Z1 + 0.02)
        if sgn < 0: q.cham('aco_polido', -0.04, -0.01, 0.9, 1.2, Z1 + 0.018, Z1 + 0.04, 0.005)
    p.cham('aco_polido', -0.02, 0.02, 1.02, 1.08, Z1 + 0.03, Z1 + 0.06, 0.006)                # cadeado
    anel(p, 'aco_polido', 0.012, 0.016, -0.004, 0.004, 14, 'z', (0, 1.095, Z1 + 0.045))


@item('quadro_procurados', 'Quadro de procurados e avisos', 'mobilias', 'delegacia', montagem='wall', altura_sugerida_m=1.1, comodos=['delegacia', 'correios', 'estacao'],
      ambiente=True, colisao='nenhuma')
def quadro_procurados(M):
    p = M.base; W, H = 1.2, 0.9; rng = np.random.default_rng(37)
    p.cham('madeira_escura', -W / 2, W / 2, 0, H, 0, 0.025, 0.004); p.box('cortica', -W / 2 + 0.03, W / 2 - 0.03, 0.03, H - 0.03, 0.025, 0.028)
    for k in range(6):
        img = Image.new('RGB', (200, 270), (236, 226, 196)); d = ImageDraw.Draw(img)
        texto_c(d, (100, 28), 'PROCURADO' if k % 3 else 'AVISO', 30, (40, 30, 20))
        if k % 3: d.rectangle([40, 55, 160, 175], fill=(150, 140, 120)); d.ellipse([75, 70, 125, 125], fill=(90, 80, 70)); d.ellipse([60, 120, 140, 200], fill=(90, 80, 70))
        else:
            for i, l in enumerate(['TOQUE DE', 'RECOLHER', '20h', 'até nova', 'ordem']): texto_c(d, (100, 80 + i * 36), l, 26, (40, 30, 20))
        for i in range(3): d.line([(30, 205 + i * 18), (170, 205 + i * 18)], fill=(90, 80, 70), width=4)
        mat_imagem(f'cartaz_proc_{k}', img, 0.85)
        x = -0.45 + (k % 3) * 0.45 + rng.uniform(-0.03, 0.03); y = 0.48 if k < 3 else 0.08
        p.box(f'cartaz_proc_{k}', x - 0.12, x + 0.12, y, y + 0.33, 0.028, 0.0295)
        p.uv[f'cartaz_proc_{k}'] = (lambda x, y: (lambda v, n: np.stack([(v[:, 0] - x + 0.12) / 0.24, (v[:, 1] - y) / 0.33], 1)))(x, y)
        torno(p, 'plastico_vermelho', [(0.006, 0), (0.006, 0.004), (0.002, 0.008)], 10, 'z', (x, y + 0.31, 0.03))


@item('banco_espera', 'Banco de espera (3 lugares)', 'mobilias', 'delegacia', comodos=['delegacia', 'clinica', 'rodoviaria', 'estacao', 'correios', 'banco'], sentar=True,
      colisao='caixa', vagas=3)
def banco_espera(M):
    p = M.base; m = 'aco_pintado'
    cyl_eixo(p, 'aco_polido', 0.025, -0.95, 0.95, 'x', (0, 0.3, 0.0), 14)
    for xs in (-1, 1):
        x = xs * 0.75; p.seg('aco_polido', (x, 0.3, 0.0), (x, 0.0, 0.25), 0.04, 0.025); p.seg('aco_polido', (x, 0.3, 0.0), (x, 0.0, -0.25), 0.04, 0.025)
    for k in range(3):
        x = -0.6 + k * 0.6
        p.hull('plastico_azul', [(x + dx, 0.42, z) for dx in (-0.25, 0.25) for z in (-0.18, 0.22)] + [(x + dx, 0.45, z) for dx in (-0.24, 0.24) for z in (-0.17, 0.2)])
        p.hull('plastico_azul', [(x + dx, 0.47, -0.2) for dx in (-0.24, 0.24)] + [(x + dx, 0.85, -0.27) for dx in (-0.22, 0.22)] + [(x + dx, 0.47, -0.17) for dx in (-0.24, 0.24)] + [(x + dx, 0.85, -0.24) for dx in (-0.22, 0.22)])
        p.cham(m, x - 0.05, x + 0.05, 0.3, 0.42, -0.08, 0.08, 0.004)
    p.cham('papel', 0.4, 0.55, 0.45, 0.452, -0.05, 0.12, 0.001)


# ---------------------------------------------------------------------------- CLINICA
@item('cadeira_rodas', 'Cadeira de rodas', 'mobilias', 'saude', comodos=['clinica', 'enfermaria', 'casas', 'rodoviaria'], sentar=True, portatil=True, peso_kg=15.0, colisao='caixa',
      uso='leva um sobrevivente ferido mais rápido')
def cadeira_rodas(M):
    p = M.base; X = 0.3
    for xs in (-1, 1):
        x = xs * X
        anel(p, 'borracha', 0.27, 0.3, *sorted((x - 0.015, x + 0.015)), 40, 'x', (0, 0.3, -0.05))
        anel(p, 'aco_polido', 0.23, 0.24, *sorted((x + 0.03 * xs - 0.004, x + 0.03 * xs + 0.004)), 40, 'x', (0, 0.3, -0.05))
        for k in range(12): a = k / 12 * 2 * math.pi; p.seg('aco_polido', (x, 0.3, -0.05), (x, 0.3 + 0.27 * math.sin(a), -0.05 + 0.27 * math.cos(a)), 0.003)
        p.cyl('aco', 0.03, 0.0, 0.06, x=x * 0.85, z=0.32, sec=14) if False else anel(p, 'borracha', 0.0, 0.06, *sorted((x * 0.85 - 0.012, x * 0.85 + 0.012)), 20, 'x', (0, 0.06, 0.32))
        xi = xs * (X - 0.06)
        for a, b in (((xi, 0.12, 0.32), (xi, 0.5, 0.25)), ((xi, 0.5, 0.25), (xi, 0.5, -0.18)), ((xi, 0.5, -0.18), (xi, 0.95, -0.22)), ((xi, 0.95, -0.22), (xi, 0.98, -0.36)),
                     ((xi, 0.5, 0.25), (xi, 0.12, 0.42)), ((xi, 0.68, 0.2), (xi, 0.68, -0.15)), ((xi, 0.5, 0.2), (xi, 0.68, 0.2))):
            p.seg('aco_polido', a, b, 0.022)
        p.cham('borracha', xi - 0.03, xi + 0.03, 0.68, 0.71, -0.15, 0.2, 0.006)
        p.cham('plastico_preto', xi - 0.02, xi + 0.02, 0.97, 1.0, -0.42, -0.32, 0.008)
        p.cham('plastico_preto', xi - 0.06, xi + 0.06, 0.1, 0.12, 0.38, 0.48, 0.004)
    p.hull('vinil_maca', [(x, 0.5, z) for x in (-X + 0.06, X - 0.06) for z in (-0.2, 0.25)] + [(x, 0.47, z) for x in (-X + 0.07, X - 0.07) for z in (-0.18, 0.22)])
    p.hull('vinil_maca', [(x, 0.52, -0.2) for x in (-X + 0.06, X - 0.06)] + [(x, 0.93, -0.24) for x in (-X + 0.06, X - 0.06)] + [(x, 0.75, -0.17) for x in (-X + 0.07, X - 0.07)])


@item('suporte_soro', 'Suporte de soro', 'mobilias', 'saude', comodos=['clinica', 'enfermaria', 'quartel'], portatil=True, peso_kg=4.0, ambiente=True, colisao='nenhuma',
      saque_ao_desmontar={'remedios': 1})
def suporte_soro(M):
    p = M.base
    for k in range(5):
        a = k / 5 * 2 * math.pi; p.seg('aco_polido', (0, 0.08, 0), (0.28 * math.cos(a), 0.04, 0.28 * math.sin(a)), 0.02)
        anel(p, 'plastico_preto', 0.0, 0.03, -0.01, 0.01, 14, 'z', (0.3 * math.cos(a), 0.03, 0.3 * math.sin(a)))
    p.cyl('aco_polido', 0.012, 0.04, 1.95, sec=12)
    for k in range(2):
        a = k * math.pi; p.seg('aco_polido', (0, 1.92, 0), (0.12 * math.cos(a), 1.92, 0.12 * math.sin(a)), 0.008)
        p.seg('aco_polido', (0.12 * math.cos(a), 1.92, 0), (0.12 * math.cos(a), 1.86, 0), 0.006)
    fofo(p, 'plastico_transp', 0.12, 1.72, 0.0, 0.05, 0.12, 0.018, 0.5, 0.5, (12, 14)); fofo(p, 'agua', 0.12, 1.69, 0.0, 0.045, 0.08, 0.012, 0.5, 0.5, (10, 12))
    varrer(p, 'plastico_transp', circ(0.003, 6), [(0.12, 1.6, 0.0), (0.15, 1.2, 0.05), (0.1, 0.9, 0.2), (0.0, 1.0, 0.35)])


@item('armario_remedios', 'Armário de remédios com vidro', 'mobilias', 'saude', comodos=['clinica', 'enfermaria', 'escolinha', 'quartel'], conteiner=True, slots=6,
      saque=['remedios'], trancado=True, ferramenta='pe_de_cabra (quebra o vidro: barulho)', colisao='caixa')
def armario_remedios(M):
    p = M.base; X, Z0, Z1, H, m = 0.45, -0.2, 0.2, 1.8, 'esmalte'; rng = np.random.default_rng(41)
    carcaca(p, m, -X, X, 0.1, H, Z0, Z1, t=0.015); p.cham('esmalte_escuro', -X + 0.01, X - 0.01, 0.0, 0.1, Z0 + 0.01, Z1 - 0.02, 0.004)
    for y in (0.5, 0.9, 1.3): p.box('vidro_prateleira', -X + 0.015, X - 0.015, y, y + 0.008, Z0 + 0.01, Z1 - 0.02)
    for y in (0.12, 0.508, 0.908, 1.308):
        x = -X + 0.04
        while x < X - 0.08:
            if rng.random() < 0.35: x += 0.07; continue
            k = rng.integers(0, 3)
            if k == 0: torno(p, 'ambar', [(0.022, 0), (0.022, 0.08), (0.012, 0.095), (0.012, 0.105)], 14, 'y', (x + 0.025, y, rng.uniform(-0.08, 0.08))); torno(p, 'plastico_branco', [(0.013, y + 0.1), (0.013, y + 0.12)], 14, 'y', (x + 0.025, 0, 0)) if False else None
            elif k == 1: p.cham('plastico_branco', x, x + 0.06, y, y + 0.1, -0.06, 0.04, 0.004); p.box('tinta_vermelha', x, x + 0.06, y + 0.06, y + 0.07, 0.04, 0.042)
            else: p.cham('cartela', x, x + 0.05, y, y + 0.14, -0.04, 0.06, 0.003)
            x += 0.075
    for nome, hx, sgn in (('porta_esq', -X, 1), ('porta_dir', X, -1)):
        q = M.parte(nome, (hx, 0, Z1 + 0.01), 'porta', eixo='y', abre_graus=-100 * sgn)
        x0, x1 = sorted((hx, sgn * 0.003))
        for (a0, a1, b0, b1) in ((x0, x1, 0.4, 0.45), (x0, x1, H - 0.05, H), (x0, x0 + 0.05, 0.4, H), (x1 - 0.05, x1, 0.4, H)): q.cham(m, a0, a1, b0, b1, Z1, Z1 + 0.02, 0.004)
        q.box('vidro_prateleira', x0 + 0.05, x1 - 0.05, 0.45, H - 0.05, Z1 + 0.008, Z1 + 0.012)
        q.cham(m, x0, x1, 0.1, 0.4, Z1, Z1 + 0.02, 0.004)
    img = Image.new('RGB', (128, 128), (250, 250, 250)); d = ImageDraw.Draw(img); d.rectangle([48, 16, 80, 112], fill=(200, 20, 20)); d.rectangle([16, 48, 112, 80], fill=(200, 20, 20))
    mat_imagem('cruz_saude', img, 0.5); p.box('cruz_saude', -0.06, 0.06, 0.2, 0.32, Z1 + 0.021, Z1 + 0.023) if False else None


@item('biombo', 'Biombo hospitalar', 'mobilias', 'saude', comodos=['clinica', 'enfermaria', 'quartel'], portatil=True, peso_kg=8.0, ambiente=True, colisao='caixa')
def biombo(M):
    p = M.base
    for k, (x, a) in enumerate(((-0.55, 0.35), (0.0, 0.0), (0.55, -0.35))):
        t = P()
        for xs in (-1, 1): t.cyl('aco_polido', 0.012, 0.1, 1.75, x=xs * 0.27, z=0, sec=10); anel(t, 'plastico_preto', 0.0, 0.03, -0.01, 0.01, 12, 'x', (xs * 0.27, 0.04, 0)) if False else t.sphere('plastico_preto', 0.03, xs * 0.27, 0.05, 0, 1)
        for y in (0.25, 1.7): cyl_eixo(t, 'aco_polido', 0.01, -0.27, 0.27, 'x', (0, y, 0), 10)
        for i in range(10): t.box('lencol', -0.26 + i * 0.052, -0.21 + i * 0.052, 0.27, 1.68, -0.006 + 0.012 * (i % 2), 0.0 + 0.012 * (i % 2))
        p.merge(t, trimesh.transformations.translation_matrix([x, 0, -abs(a) * 0.25]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]))


@item('balanca_medica', 'Balança médica com régua', 'mobilias', 'saude', comodos=['clinica', 'escolinha', 'enfermaria'], ambiente=True, colisao='caixa')
def balanca_medica(M):
    p = M.base; m = 'esmalte'
    p.cham(m, -0.2, 0.2, 0.0, 0.08, -0.25, 0.25, 0.01); p.cham('borracha', -0.18, 0.18, 0.08, 0.09, -0.22, 0.22, 0.004)
    p.cham(m, -0.04, 0.04, 0.0, 1.3, -0.29, -0.23, 0.008)
    p.cham(m, -0.16, 0.16, 1.3, 1.38, -0.3, -0.22, 0.008)
    for k in range(2):
        y = 1.31 + k * 0.035; cyl_eixo(p, 'aco_polido', 0.004, -0.15, 0.15, 'x', (0, y, -0.215), 8)
        p.cham('aco_polido', -0.05 + 0.08 * k, -0.03 + 0.08 * k, y - 0.012, y + 0.012, -0.225, -0.205, 0.003)
    p.cyl('aco_polido', 0.008, 1.38, 2.0, x=0, z=-0.26, sec=10); cyl_eixo(p, 'aco_polido', 0.006, -0.26, -0.08, 'z', (0, 1.85, 0), 8)


@item('carrinho_emergencia', 'Carrinho de emergência', 'mobilias', 'saude', comodos=['clinica', 'enfermaria'], conteiner=True, slots=5, saque=['remedios'],
      portatil=True, peso_kg=35.0, colisao='caixa')
def carrinho_emergencia(M):
    p = M.base; X, Z, m = 0.38, 0.27, 'tinta_vermelha'
    carcaca(p, m, -X, X, 0.12, 1.0, -Z, Z, t=0.015); p.cham('plastico_cinza', -X - 0.02, X + 0.02, 1.0, 1.04, -Z - 0.02, Z + 0.02, 0.01)
    for xs in (-1, 1):
        for zs in (-1, 1): anel(p, 'borracha', 0.0, 0.05, -0.012, 0.012, 16, 'z', (xs * (X - 0.06), 0.06, zs * (Z - 0.05))) if False else _roda(p, (xs * (X - 0.06), 0.05, zs * (Z - 0.05)), 0.05, 0.025, mat_aro='aco')
    for j in range(4):
        y0 = 0.15 + j * 0.21; q = M.parte(f'gaveta_{j + 1}', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.3]) if j == 0 else p
        q.cham(m, -X + 0.02, X - 0.02, y0, y0 + 0.19, Z - 0.01, Z + 0.01, 0.005); q.cham('plastico_cinza', -0.12, 0.12, y0 + 0.13, y0 + 0.16, Z + 0.01, Z + 0.03, 0.006)
        if q is not p:
            carcaca(q, m, -X + 0.03, X - 0.03, y0 + 0.01, y0 + 0.17, -Z + 0.03, Z - 0.01, t=0.01, topo=False)
            for k in range(5): q.cham('plastico_branco', -0.3 + k * 0.12, -0.2 + k * 0.12, y0 + 0.02, y0 + 0.08, -0.15, 0.15, 0.005)
    p.cham('plastico_cinza', X, X + 0.12, 0.9, 1.0, -0.15, 0.15, 0.01)                          # desfibrilador
    p.cham('esmalte_escuro', X + 0.1, X + 0.121, 0.92, 0.98, -0.1, 0.05, 0.004)
    cyl_eixo(p, 'aco_polido', 0.012, -X + 0.05, X - 0.05, 'x', (0, 1.08, -Z), 10)


# ---------------------------------------------------------------------------- BANCO
@item('cofres_aluguel', 'Parede de cofres de aluguel', 'mobilias', 'banco', montagem='wall', comodos=['banco', 'banco_googie'], conteiner=True, slots=8,
      saque=['moedas', 'joias', 'pistas', 'remedios'], trancado=True, ferramenta='pe_de_cabra (1 cofre por vez, barulho)', colisao='caixa')
def cofres_aluguel(M):
    p = M.base; W, H, D = 1.6, 2.0, 0.45; m = 'aco_cofre'; rng = np.random.default_rng(43)
    p.cham(m, -W / 2, W / 2, 0.0, H, 0.0, D, 0.01)
    cols, rows = 8, 10; cw = W / cols; ch = (H - 0.2) / rows
    for i in range(cols):
        for j in range(rows):
            x0 = -W / 2 + i * cw + 0.006; y0 = 0.1 + j * ch + 0.006
            aberto = (i, j) in ((2, 4), (5, 7), (6, 2))
            q = M.parte(f'cofre_{i}_{j}', (x0, 0, D + 0.008), 'porta', eixo='y', abre_graus=-95) if aberto else p
            q.cham('ouro_velho' if (i + j) % 7 == 0 else m, x0, x0 + cw - 0.012, y0, y0 + ch - 0.012, D, D + 0.012, 0.003)
            torno(q, 'aco_polido', [(0.008, 0), (0.008, 0.008), (0.0, 0.009)], 10, 'z', (x0 + cw * 0.5 - 0.006, y0 + ch * 0.5, D + 0.012))
            torno(q, 'esmalte_escuro', [(0.004, 0), (0.004, 0.002)], 8, 'z', (x0 + cw * 0.5 - 0.006, y0 + ch * 0.25, D + 0.012))
            q.box('ouro_velho', x0 + 0.05, x0 + cw - 0.06, y0 + ch - 0.04, y0 + ch - 0.028, D + 0.012, D + 0.013)
            if aberto:
                p.box('esmalte_escuro', x0, x0 + cw - 0.012, y0, y0 + ch - 0.012, D - 0.002, D + 0.0)
                q.cham(m, x0, x0 + cw - 0.012, y0, y0 + ch - 0.012, D + 0.012, D + 0.0121, 0.0)


@item('pedestal_fila', 'Pedestais de fila com cordão', 'mobilias', 'banco', comodos=['banco', 'banco_googie', 'cinema', 'rodoviaria', 'correios', 'hotel'], ambiente=True,
      colisao='caixa', portatil=True, peso_kg=8.0)
def pedestal_fila(M):
    p = M.base
    for xs in (-1, 1):
        x = xs * 0.6
        torno(p, 'ouro_velho', [(0.15, 0.0), (0.15, 0.02), (0.05, 0.04), (0.025, 0.06), (0.02, 0.9), (0.035, 0.92), (0.04, 0.96), (0.0, 0.98)], 24, 'y', (x, 0, 0))
    pts = [(x, 0.92 - 0.12 * (1 - (x / 0.56) ** 2), 0.0) for x in np.linspace(-0.56, 0.56, 16)]
    varrer(p, 'veludo_vinho', circ(0.016, 10), pts)


# ---------------------------------------------------------------------------- QUARTEL DE BOMBEIROS
@item('armario_bombeiro', 'Armário de equipamento de bombeiro', 'mobilias', 'quartel', comodos=['quartel'], conteiner=True, slots=4,
      saque=['roupas', 'ferramentas', 'remedios'], colisao='caixa', modulo_m=1.0)
def armario_bombeiro(M):
    p = M.base; X, Z = 0.48, 0.3; m = 'vermelho_bombeiro'
    for xs in (-1, 1): p.cham(m, *sorted((xs * X, xs * (X - 0.03))), 0.0, 2.1, -Z, Z, 0.005)
    p.cham(m, -X, X, 2.1, 2.14, -Z, Z, 0.006); p.cham(m, -X, X, 0.0, 0.45, -Z, Z, 0.008)
    p.cham(m, -X, X, 1.75, 1.78, -Z, Z, 0.004); p.box(m, -X, X, 0.45, 2.1, -Z, -Z + 0.02)
    p.cham('madeira_crua', -X + 0.03, X - 0.03, 0.45, 0.5, -Z + 0.02, Z, 0.006)                  # banco de sentar
    fofo(p, 'amarelo_bombeiro', 0, 1.84, 0.0, 0.14, 0.08, 0.17, 0.45, 0.6, (14, 18))             # capacete
    torno(p, 'amarelo_bombeiro', [(0.0, 1.78), (0.2, 1.785), (0.21, 1.79), (0.0, 1.795)], 24, 'y', (0, 0, 0.0))
    p.cyl('aco_polido', 0.01, 1.4, 1.75, x=0, z=0.0, sec=8)
    fofo(p, 'amarelo_bombeiro', 0, 1.2, 0.02, 0.24, 0.32, 0.12, 0.6, 0.6, (14, 18))             # casaco
    for y in (1.0, 1.25): p.box('branco_refletivo', -0.24, 0.24, y, y + 0.04, 0.12, 0.145)
    for xs in (-1, 1): fofo(p, 'amarelo_bombeiro', xs * 0.27, 1.15, 0.02, 0.07, 0.28, 0.08, 0.6, 0.6, (10, 12))
    for xs in (-1, 1):                                                                        # botas
        torno(p, 'borracha', [(0.06, 0.5), (0.06, 0.82), (0.065, 0.84)], 18, 'y', (xs * 0.12, 0, 0.05), fechar=False)
        p.cham('borracha', xs * 0.12 - 0.055, xs * 0.12 + 0.055, 0.5, 0.58, -0.02, 0.2, 0.025)
    fofo(p, 'amarelo_bombeiro', 0, 0.68, 0.0, 0.2, 0.15, 0.1, 0.6, 0.6, (10, 12))              # calça sanfonada


@item('carretel_mangueira', 'Carretel de mangueira de incêndio', 'mobilias', 'quartel', comodos=['quartel', 'galeria', 'hotel', 'fabrica'], ambiente=True, colisao='caixa',
      uso='apaga incêndios; vira corda de escalada (receita)', desmonta={'material': 2})
def carretel_mangueira(M):
    p = M.base; R = 0.38
    for xs in (-1, 1):
        anel(p, 'vermelho_bombeiro', R - 0.02, R, *sorted((xs * 0.25, xs * 0.27)), 40, 'x', (0, 0.48, 0))
        for k in range(6): a = k / 6 * 2 * math.pi; p.seg('vermelho_bombeiro', (xs * 0.26, 0.48, 0), (xs * 0.26, 0.48 + (R - 0.02) * math.sin(a), (R - 0.02) * math.cos(a)), 0.02)
        p.seg('vermelho_bombeiro', (xs * 0.3, 0.48, 0), (xs * 0.3, 0.0, 0.25), 0.04); p.seg('vermelho_bombeiro', (xs * 0.3, 0.48, 0), (xs * 0.3, 0.0, -0.25), 0.04)
    cyl_eixo(p, 'aco', 0.03, -0.33, 0.33, 'x', (0, 0.48, 0), 14)
    anel(p, 'lona_crua', 0.06, R - 0.04, -0.24, 0.24, 40, 'x', (0, 0.48, 0))
    for r_ in np.linspace(0.08, R - 0.05, 6): anel(p, 'lona_crua', r_, r_ + 0.006, -0.245, 0.245, 40, 'x', (0, 0.48, 0))
    varrer(p, 'lona_crua', Polygon([(-0.04, -0.01), (0.04, -0.01), (0.04, 0.01), (-0.04, 0.01)]), [(0.0, 0.48 + R - 0.04, 0.0), (0.0, 0.6, 0.45), (0.1, 0.02, 0.7), (0.4, 0.01, 0.9)])
    torno(p, 'latao', [(0.04, 0.0), (0.035, 0.08), (0.02, 0.2), (0.015, 0.22)], 16, 'z', (0.4, 0.04, 0.9))


@item('extintor', 'Extintor de incêndio', 'loot', 'ferramentas', recurso='ferramenta', valor=1, peso_kg=6.0, empilha=1,
      onde=['quartel', 'galeria', 'hotel', 'escolinha', 'posto', 'fabrica', 'supermercado'], efeito='apaga fogo; jato atordoa zumbis (barulho baixo); arma pesada',
      arma=True, dano=20, pega=[0.12, 0.08, 0])
def extintor(M):
    p = M.base; R = 0.08
    torno(p, 'vermelho_bombeiro', [(0.0, -0.25), (R * 0.95, -0.25), (R, -0.24), (R, 0.15), (R * 0.85, 0.2), (R * 0.4, 0.23), (0.02, 0.24)], 28, 'x', (0, R, 0))
    torno(p, 'aco', [(0.02, 0.24), (0.022, 0.29), (0.0, 0.3)], 14, 'x', (0, R, 0))
    p.cham('aco_polido', 0.25, 0.38, R + 0.02, R + 0.04, -0.015, 0.015, 0.006); p.cham('aco_polido', 0.27, 0.36, R - 0.0, R + 0.015, -0.012, 0.012, 0.004)
    torno(p, 'aco_polido', [(0.008, 0.0), (0.008, 0.02), (0.0, 0.025)], 10, 'z', (0.28, R + 0.03, 0.02))
    varrer(p, 'plastico_preto', circ(0.009, 8), [(0.27, R + 0.02, 0.0), (0.2, R + 0.08, 0.06), (0.0, R + 0.09, 0.09), (-0.15, R + 0.06, 0.08)])
    torno(p, 'plastico_preto', [(0.012, 0.0), (0.02, 0.06), (0.025, 0.065)], 12, 'x', (-0.2, R + 0.06, 0.08))
    img = Image.new('RGB', (512, 160), (110, 6, 4)); d = ImageDraw.Draw(img); d.rectangle([140, 20, 372, 140], fill=(245, 240, 230)); texto_c(d, (256, 60), 'PÓ ABC', 40, (30, 30, 30)); texto_c(d, (256, 110), '6 kg', 34, (30, 30, 30))
    mat_imagem('rotulo_extintor', img, 0.45)
    anel(p, 'rotulo_extintor', R, R + 0.0008, -0.15, 0.08, 28, 'x', (0, R, 0)); p.uv['rotulo_extintor'] = uv_cilindro(-0.15, 0.08, 'x', (0, R, 0))
