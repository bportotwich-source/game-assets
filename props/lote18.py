# Lote 18: comunidade (fase 3, Assentamento): o abrigo vira um lugar onde varias pessoas vivem.
# Executado por gerar_props.py (usa as mesmas funcoes e materiais dos lotes anteriores).
# Campos: moradores (quantas pessoas a peca abriga), higiene / moral (bonus da comunidade), energia_w (geracao eletrica),
#         precisa_achar (peca que nao se fabrica: so achando nas ruinas), marco (peca que muda a fase do jogo).
#         produz, trabalha, ponto_uso e estacao seguem o lote 16.
CORES.update({'lona_verde': (22, 40, 18), 'balde_zinco': (120, 124, 126), 'cal': (220, 218, 208), 'pele_coelho': (120, 100, 80),
              'painel_moldura': (150, 152, 156), 'mastro_vermelho': (120, 14, 10), 'mastro_branco': (210, 210, 206),
              'luz_vermelha': (255, 20, 10), 'plastico_estufa': (230, 236, 236), 'muda': (24, 60, 14), 'carne_crua': (130, 30, 28),
              'cenoura': (200, 70, 10), 'alface': (60, 120, 30), 'cesto': (150, 110, 60), 'pedra_poco': (90, 86, 80)})
METALICOS.update({'balde_zinco': (0.85, 0.4), 'painel_moldura': (0.9, 0.35), 'mastro_vermelho': (0.3, 0.5), 'mastro_branco': (0.3, 0.5)})
FOSCOS.update({'lona_verde': 0.9, 'cal': 0.95, 'pele_coelho': 0.95, 'muda': 0.8, 'alface': 0.7, 'cesto': 0.85})
TEX_PROPRIAS += [('lona_verde', 'couro', 0.5, 512), ('pedra_poco', 'barro', 0.4, 512), ('cesto', 'xadrez', 0.12, 512)]
TRANSP.update({'plastico_estufa': ((235, 242, 240), 0.38, 0.25)})
EMISSIVOS.update({'luz_vermelha': [1.0, 0.1, 0.05]})


def _tela(p, x0, x1, y0, y1, z, nx, ny, mat='tela_galinheiro', r=0.0015):
    """Tela de arame num plano z constante: fios cruzados (como no galinheiro do lote 11)."""
    for y in np.linspace(y0, y1, ny): p.box(mat, x0, x1, y - r, y + r, z - r, z + r)
    for x in np.linspace(x0, x1, nx): p.box(mat, x - r, x + r, y0, y1, z - r, z + r)


def _ondulada(p, mat, x0, x1, z0, z1, y, onda=0.076, a=0.009, incl=0.0):
    """Chapa ondulada deitada (telhado): ondas ao longo de x, comprimento em z; incl sobe o lado z0 (caimento)."""
    xs = np.linspace(x0, x1, max(8, int((x1 - x0) / onda * 8)))
    top = [(x, a * math.cos((x - x0) * 2 * math.pi / onda)) for x in xs]
    m = trimesh.creation.extrude_polygon(Polygon(top + [(x, yy - 0.0012) for x, yy in top[::-1]]).buffer(0), z1 - z0)
    v = m.vertices.copy(); zz = v[:, 2] + z0
    m.vertices = np.stack([v[:, 0], v[:, 1] + y + incl * (z1 - zz) / max(z1 - z0, 1e-6), zz], 1)
    if m.volume < 0: m.invert()
    p.add(mat, m)


def _balde(p, c, r0=0.12, r1=0.15, h=0.26, mat='balde_zinco', alca=True):
    x, y, z = c
    torno(p, mat, [(0.0, y), (r0, y), (r1, y + h), (r1 - 0.004, y + h), (r0 - 0.004, y + 0.006), (0.0, y + 0.006)], 28, 'y', (x, 0, z))
    anel(p, mat, r1 - 0.002, r1 + 0.004, y + h - 0.012, y + h, 28, 'y', (x, 0, z))
    for k in (0.33, 0.66): anel(p, mat, r0 + (r1 - r0) * k, r0 + (r1 - r0) * k + 0.003, y + h * k - 0.006, y + h * k + 0.006, 28, 'y', (x, 0, z))
    if alca: varrer(p, 'aco', circ(0.003, 6), [(x - r1, y + h - 0.02, z)] + [(x - r1 * math.cos(t), y + h + 0.1 * math.sin(t), z) for t in np.linspace(0.3, math.pi - 0.3, 9)] + [(x + r1, y + h - 0.02, z)])


def _mastro_trelica(p, x, z, y0, y1, w=0.3, passo=0.45, mat='mastro_vermelho', r=0.014):
    """Mastro triangular de trelica (3 montantes, diagonais em zigue-zague)."""
    cs = [(x + w / math.sqrt(3) * math.cos(a), z + w / math.sqrt(3) * math.sin(a)) for a in (math.pi / 2, math.pi / 2 + 2 * math.pi / 3, math.pi / 2 + 4 * math.pi / 3)]
    for cx, cz in cs: p.add(mat, trimesh.creation.cylinder(radius=r, segment=[(cx, y0, cz), (cx, y1, cz)], sections=8))
    k = 0
    for y in np.arange(y0, y1 - passo / 2, passo):
        for i in range(3):
            a, b = cs[i], cs[(i + 1) % 3]; ya, yb = (y, y + passo) if (k + i) % 2 == 0 else (y + passo, y)
            p.add(mat, trimesh.creation.cylinder(radius=r * 0.55, segment=[(a[0], ya, a[1]), (b[0], yb, b[1])], sections=6))
            p.add(mat, trimesh.creation.cylinder(radius=r * 0.55, segment=[(a[0], y, a[1]), (b[0], y, b[1])], sections=6))
        k += 1
    return cs


# ---------------------------------------------------------------------------- MORAR JUNTO
@item('barraca_lona', 'Barraca de lona com cumeeira', 'mobilias', 'comunidade', comodos=['abrigo', 'fazenda', 'rua', 'parque'],
      constroi={'lona': 2, 'corda': 1, 'lenha': 3}, ferramenta='nenhuma', fase=3, moradores=2, deitar=True, ponto_uso=[0.0, 0.0, 1.3],
      estacao='moradia (abriga 2 moradores; protege da chuva, mas não do frio forte nem de zumbi)')
def barraca_lona(M):
    p = M.base; L, W, H = 2.4, 1.9, 1.45; rng = np.random.default_rng(3)
    for x in (-L / 2 + 0.05, L / 2 - 0.05):                                                          # forquilhas e cumeeira
        p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.035, segment=[(x, 0.0, 0.0), (x, H + 0.1, 0.0)], sections=10))
        for s in (-1, 1): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.02, segment=[(x, H - 0.02, 0.0), (x + s * 0.04, H + 0.16, 0.0)], sections=8))
    p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.03, segment=[(-L / 2 - 0.15, H + 0.03, 0.0), (L / 2 + 0.15, H + 0.03, 0.0)], sections=10))
    for zs in (-1, 1):                                                                              # duas aguas de lona
        q = P(); n = 10
        for i in range(n):
            x0, x1 = -L / 2 + i * L / n, -L / 2 + (i + 1) * L / n
            q.hull('lona_verde', [(x, H - t * (H - 0.06), zs * t * W / 2 + d) for x in (x0, x1) for t in (0.0, 1.0) for d in (0.0, zs * 0.004)])
        _amassar(q, 'lona_verde', 0.01, 6.0, 4 + zs, sub=2)
        p.merge(q)
        for x in np.linspace(-L / 2, L / 2, 5):                                                     # ilhoses, cordas e estacas
            a = (x, 0.06, zs * W / 2); b = (x, 0.0, zs * (W / 2 + 0.35))
            p.add('corda', trimesh.creation.cylinder(radius=0.004, segment=[a, b], sections=6))
            p.add('madeira_crua', trimesh.creation.cone(radius=0.018, height=0.22, sections=8, transform=_alinha((x, 0.09, zs * (W / 2 + 0.38)), np.array([0, -1.0, zs * 0.25]))))
            anel(p, 'latao_velho', 0.008, 0.012, 0.0, 0.004, 10, 'x', (x, 0.07, zs * W / 2))
    q = P(); q.hull('lona_verde', [(-L / 2 + 0.02 + d, y, z) for d in (0.0, 0.004) for (y, z) in ((H, 0.0), (0.04, -W / 2), (0.04, W / 2))])   # fundo fechado
    p.merge(q)
    for s in (-1, 1):                                                                               # abas da frente enroladas e amarradas
        p.add('lona_verde', trimesh.creation.cylinder(radius=0.05, segment=[(L / 2 + 0.03, 0.15, s * W / 2 * 0.9), (L / 2 + 0.03, H - 0.08, s * 0.06)], sections=12))
        p.add('corda', trimesh.creation.torus(0.052, 0.005, major_sections=14, minor_sections=6, transform=_alinha((L / 2 + 0.03, 0.75, s * (W / 2 * 0.9 - (0.75 - 0.15) / (H - 0.23) * (W / 2 * 0.9 - 0.06))), np.array([0.0, H - 0.23, -s * (W / 2 * 0.9 - 0.06)]))))
    p.box('lona_azul', -L / 2 + 0.05, L / 2 - 0.05, 0.0, 0.006, -W / 2 + 0.1, W / 2 - 0.1)          # forro do chao
    for z in (-0.4, 0.4):                                                                           # dois colchonetes com cobertor
        fofo(p, 'colchao', -0.1, 0.05, z, 0.9, 0.04, 0.3, 0.15, 0.15, (10, 16))
        fofo(p, 'cobertor', 0.05, 0.1, z, 0.6, 0.04, 0.31, 0.3, 0.3, (10, 16)); _amassar(p, 'cobertor', 0.01, 10.0, int(z * 10) + 9, sub=0)
        fofo(p, 'travesseiro', -0.8, 0.11, z, 0.14, 0.05, 0.2, 0.3, 0.3, (8, 12))
    _balde(p, (0.95, 0.006, -0.55), 0.08, 0.1, 0.16, 'balde_zinco', False)


@item('latrina', 'Latrina de tábuas com fossa', 'mobilias', 'comunidade', comodos=['abrigo', 'fazenda'],
      constroi={'tabua': 10, 'caixa_pregos': 1, 'chapa_metal': 1}, ferramenta='pa', fase=3, higiene=2, ponto_uso=[0.0, 0.0, 0.85],
      estacao='latrina (fossa longe da água: sem ela a comunidade adoece; cal tira o cheiro)')
def latrina(M):
    p = M.base; X, Z, H = 0.5, 0.55, 2.1
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_escura', xs * X - 0.05 * (xs > 0), xs * X + 0.05 * (xs < 0), 0.0, H + (0.12 if zs < 0 else -0.05) , zs * Z - 0.05 * (zs > 0), zs * Z + 0.05 * (zs < 0), 0.004)
    for xs in (-1, 1):                                                                              # paredes de tabua em pe (laterais e fundo)
        for k, z in enumerate(np.linspace(-Z + 0.05, Z - 0.05, 6)):
            hh = H - 0.05 + (Z - z) / (2 * Z) * 0.17
            p.cham('madeira', xs * X - 0.018 * (xs > 0) + xs * 0.0, xs * X + 0.018 * (xs < 0), 0.04, hh, z - 0.088, z + 0.088 - 0.006, 0.003)
    for x in np.linspace(-X + 0.07, X - 0.07, 6): p.cham('madeira', x - 0.08, x + 0.08 - 0.006, 0.04, H + 0.12, -Z - 0.0, -Z + 0.018, 0.003)
    p.cham('madeira', -X, X, H + 0.02, H + 0.12, Z - 0.05, Z, 0.003)                                  # verga da porta
    _ondulada(p, 'telha_ondulada', -X - 0.12, X + 0.12, -Z - 0.15, Z + 0.15, H + 0.14, incl=0.17)   # telhado com caimento para tras
    p.cham('madeira', -X, X, 0.0, 0.04, -Z, Z, 0.004)                                                 # piso
    p.cham('madeira', -X + 0.02, X - 0.02, 0.04, 0.46, -Z + 0.02, -Z + 0.42, 0.004)                   # caixa do assento
    p.cham('madeira_crua', -X + 0.02, X - 0.02, 0.46, 0.49, -Z + 0.02, -Z + 0.44, 0.004)
    anel(p, 'madeira_escura', 0.11, 0.135, 0.488, 0.494, 24, 'y', (0, 0, -Z + 0.24))
    torno(p, 'fuligem', [(0.11, 0.489), (0.0, 0.489)], 24, 'y', (0, 0, -Z + 0.24))                    # buraco
    q = P(); q.cham('madeira', -0.15, 0.15, 0.0, 0.025, -0.15, 0.15, 0.004)                          # tampa do buraco encostada
    p.merge(q, trimesh.transformations.translation_matrix([0.25, 0.65, -Z + 0.05]) @ _rot(-1.35, [1, 0, 0]) @ trimesh.transformations.translation_matrix([0, 0, 0.15]))
    _balde(p, (-0.28, 0.04, 0.05), 0.09, 0.11, 0.2, 'balde_zinco', True)                              # balde de cal com caneca
    torno(p, 'cal', [(0.0, 0.2), (0.105, 0.2)], 20, 'y', (-0.28, 0.04, 0.05))
    torno(p, 'lata', [(0.0, 0.0), (0.035, 0.0), (0.035, 0.08), (0.032, 0.08), (0.032, 0.004), (0.0, 0.004)], 14, 'y', (-0.33, 0.245, 0.07))
    p.cham('aco', -X + 0.03, -X + 0.06, 0.9, 0.94, -0.1, 0.1, 0.002)                                  # prego com papel (folhas de revista)
    p.cham('papel', -X + 0.06, -X + 0.065, 0.78, 0.94, -0.06, 0.06, 0.001)
    q = M.parte('porta', (X - 0.02, 0.05, Z), 'porta', eixo='y', abre_graus=-100)
    for k, x in enumerate(np.linspace(-2 * X + 0.12, -0.08, 5)): q.cham('madeira', x - 0.08, x + 0.08 - 0.006, 0.0, H - 0.08, 0.0, 0.02, 0.003)
    for y in (0.25, H - 0.35): q.cham('madeira_escura', -2 * X + 0.06, -0.04, y, y + 0.1, 0.02, 0.042, 0.004)
    q.seg('madeira_escura', (-2 * X + 0.1, 0.35, 0.03), (-0.08, H - 0.4, 0.03), 0.09, 0.02)
    m = trimesh.creation.extrude_polygon(Point(0, 0).buffer(0.07).difference(Point(0.035, 0.02).buffer(0.06)), 0.004)   # lua recortada
    m.apply_translation([-X + 0.02, H - 0.25, 0.021]); q.add('fuligem', m)
    q.cham('aco', -2 * X + 0.12, -2 * X + 0.16, 1.0, 1.1, 0.02, 0.05, 0.004)                           # trinco
    for y in (0.3, H - 0.3): q.cham('aco', -0.06, 0.02, y - 0.02, y + 0.02, 0.02, 0.026, 0.002)        # dobradicas
    _mover(q, (X - 0.02, 0.05, Z))


@item('chuveiro_balde', 'Chuveiro de balde com cortina de lona', 'mobilias', 'comunidade', comodos=['abrigo', 'fazenda'],
      constroi={'lenha': 4, 'lona': 1, 'corda': 1, 'lata_vazia': 1, 'pallet': 1}, ferramenta='martelo', fase=3, higiene=2, ponto_uso=[0.0, 0.0, 0.0],
      estacao='banho (um balde de 10 L por banho; banho quente se a água vier do fogão)')
def chuveiro_balde(M):
    p = M.base; X, Z, H = 0.5, 0.5, 2.25
    for xs in (-1, 1):
        for zs in (-1, 1): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.04, segment=[(xs * X, 0.0, zs * Z), (xs * X, H, zs * Z)], sections=10))
    for zs in (-1, 1): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.03, segment=[(-X - 0.05, H - 0.05, zs * Z), (X + 0.05, H - 0.05, zs * Z)], sections=10))
    for xs in (-1, 1): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.03, segment=[(xs * X, H - 0.12, -Z - 0.05), (xs * X, H - 0.12, Z + 0.05)], sections=10))
    p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.035, segment=[(-X - 0.05, H + 0.02, 0.0), (X + 0.05, H + 0.02, 0.0)], sections=10))   # travessa do balde
    for x0, x1 in ((-X, X),):                                                                        # pallet como piso
        for z in np.linspace(-Z + 0.06, Z - 0.06, 7): p.cham('madeira_crua', x0 + 0.02, x1 - 0.02, 0.1, 0.12, z - 0.045, z + 0.045, 0.003)
        for x in (x0 + 0.06, 0.0, x1 - 0.06): p.cham('madeira_crua', x - 0.045, x + 0.045, 0.0, 0.1, -Z + 0.02, Z - 0.02, 0.004)
    for lado in range(3):                                                                            # cortina de lona em 3 lados (frente aberta)
        q = P(); n = 8
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            if lado == 0: pts = [(-X + 2 * X * t, y, -Z - 0.045 - d) for t in (t0, t1) for y in (0.35, H - 0.1) for d in (0.0, 0.004)]
            else:
                xs = -1 if lado == 1 else 1; pts = [(xs * (X + 0.045 + d), y, -Z + 2 * Z * t) for t in (t0, t1) for y in (0.35, H - 0.1) for d in (0.0, 0.004)]
            q.hull('lona_azul', pts)
        _amassar(q, 'lona_azul', 0.012, 5.0, 20 + lado, sub=2); p.merge(q)
    for x in np.linspace(-X + 0.1, X - 0.1, 5): anel(p, 'aco', 0.034, 0.038, -0.006, 0.006, 10, 'z', (x, H - 0.1, -Z - 0.045))   # argolas na trave
    _balde(p, (0.0, H + 0.055, 0.0), 0.15, 0.17, 0.28, 'balde_zinco', True)
    torno(p, 'lata', [(0.012, H + 0.055), (0.012, H - 0.06), (0.05, H - 0.1), (0.05, H - 0.11), (0.0, H - 0.11)], 16, 'y', (0, 0, 0))   # crivo de lata furada
    for k in range(12): a = k * 2 * math.pi / 12; p.box('fuligem', 0.03 * math.cos(a) - 0.003, 0.03 * math.cos(a) + 0.003, H - 0.1115, H - 0.1095, 0.03 * math.sin(a) - 0.003, 0.03 * math.sin(a) + 0.003)
    p.add('corda', trimesh.creation.cylinder(radius=0.004, segment=[(0.06, H + 0.1, 0.0), (0.3, 1.35, 0.25)], sections=6))   # cordinha da valvula
    torno(p, 'madeira_crua', [(0.0, 1.29), (0.015, 1.3), (0.015, 1.35), (0.0, 1.36)], 10, 'y', (0.3, 0, 0.25))
    torno(p, 'plastico_vermelho', [(0.0, 0.12), (0.06, 0.12), (0.07, 0.2), (0.0, 0.2)], 16, 'y', (-0.3, 0, -0.3))   # bacia de sabao
    p.cham('cera', -0.34, -0.27, 0.2, 0.225, -0.32, -0.27, 0.008)


@item('tanque_lavar', 'Tanque de lavar de cimento', 'mobilias', 'comunidade', comodos=['abrigo', 'fazenda', 'casas'],
      constroi={'cimento': 1, 'tijolo': 10, 'tubo_pvc': 1}, ferramenta='nenhuma', fase=3, higiene=1, trabalha=1, ponto_uso=[0.0, 0.0, 0.6],
      estacao='lavanderia (roupas e ataduras limpas: menos doença na comunidade)')
def tanque_lavar(M):
    p = M.base; X, Z, H = 0.6, 0.32, 0.88
    for x in (-X + 0.12, X - 0.12):                                                                 # pes de tijolo
        for k in range(8): p.cham('tijolo', x - 0.11, x + 0.11, k * 0.072, k * 0.072 + 0.065, -Z + 0.04 + 0.03 * (k % 2), Z - 0.04 - 0.03 * ((k + 1) % 2), 0.004)
    y0 = 0.58; p.cham('concreto', -X, X, y0, y0 + 0.05, -Z, Z, 0.008)                                 # fundo da bacia
    for xs in (-1, 1): p.cham('concreto', xs * X - 0.05 * (xs > 0), xs * X + 0.05 * (xs < 0), y0, H, -Z, Z, 0.008)
    p.cham('concreto', -X, X, y0, H + 0.08, -Z, -Z + 0.06, 0.008)                                    # encosto alto
    p.cham('concreto', -X, X, y0, H, Z - 0.05, Z, 0.008)
    p.cham('concreto', -0.03, 0.03, y0, H - 0.02, -Z, Z, 0.006)                                       # divisoria: bacia e esfregador
    for k in range(9):                                                                               # esfregador ondulado inclinado
        z = -Z + 0.1 + k * 0.045
        p.add('concreto', trimesh.creation.cylinder(radius=0.012, segment=[(0.04, H - 0.09 - k * 0.012, z), (X - 0.05, H - 0.09 - k * 0.012, z)], sections=8))
    p.hull('concreto', [(x, y, z) for x in (0.03, X - 0.05) for (y, z) in ((H - 0.1, -Z + 0.06), (H - 0.21, Z - 0.05), (y0 + 0.05, Z - 0.05), (y0 + 0.05, -Z + 0.06))])
    p.box('agua', -X + 0.05, -0.03, y0 + 0.05, y0 + 0.16, -Z + 0.06, Z - 0.05)
    torno(p, 'pvc', [(0.02, y0 - 0.2), (0.02, y0 + 0.05)], 12, 'y', (-0.3, 0, 0.0))                      # ralo e cano de PVC
    p.seg('pvc', (-0.3, y0 - 0.2, 0.0), (-0.3, y0 - 0.2, -Z - 0.12), 0.04, 0.04); p.seg('pvc', (-0.3, y0 - 0.2, -Z - 0.12), (-0.3, 0.0, -Z - 0.12), 0.04, 0.04)   # desce atras
    _balde(p, (0.55, 0.0, 0.55), 0.12, 0.15, 0.26, 'plastico_azul', True)                            # balde e roupa torcida
    for i in range(3): fofo(p, 'trapo_cinza' if i % 2 else 'trapo_xadrez', 0.3 + i * 0.07, H - 0.06 - i * 0.03, -0.05 + i * 0.06, 0.08, 0.03, 0.05, 0.4, 0.5, (8, 10))
    p.cham('cera', -0.2, -0.13, H, H + 0.025, -Z + 0.02, -Z + 0.06, 0.008)                               # barra de sabao no encosto


@item('mesa_refeitorio', 'Mesa comprida do refeitório com bancos', 'mobilias', 'comunidade', comodos=['abrigo', 'igreja', 'escolinha', 'fazenda'],
      constroi={'tabua': 10, 'caixa_pregos': 1}, ferramenta='martelo', estacao_obra='bancada_carpintaria', fase=3, sentar=8, moral=1,
      estacao='refeitório (8 lugares; comer junto melhora o moral da comunidade)')
def mesa_refeitorio(M):
    p = M.base; L, W, H = 2.6, 0.8, 0.76; rng = np.random.default_rng(18)
    for k, z in enumerate(np.linspace(-W / 2 + 0.1, W / 2 - 0.1, 4)): p.cham('madeira', -L / 2 + 0.01 * (k % 2), L / 2 - 0.01 * ((k + 1) % 2), H - 0.04, H, z - 0.095, z + 0.095, 0.004)
    for x in (-L / 2 + 0.25, L / 2 - 0.25):                                                          # cavaletes em X com travessa
        p.cham('madeira_escura', x - 0.04, x + 0.04, H - 0.09, H - 0.04, -W / 2 + 0.04, W / 2 - 0.04, 0.004)
        for s in (-1, 1): p.seg('madeira_escura', (x, H - 0.08, s * (W / 2 - 0.08)), (x, 0.03, -s * (W / 2 - 0.05)), 0.06, 0.06)
        p.cham('madeira_escura', x - 0.04, x + 0.04, 0.0, 0.04, -W / 2 + 0.03, W / 2 - 0.03, 0.004)
    p.cham('madeira_escura', -L / 2 + 0.25, L / 2 - 0.25, 0.3, 0.36, -0.03, 0.03, 0.004)
    for zs in (-1, 1):                                                                               # bancos
        zb = zs * (W / 2 + 0.25)
        for z in (zb - 0.08, zb + 0.08): p.cham('madeira', -L / 2 + 0.05, L / 2 - 0.05, 0.42, 0.45, z - 0.075, z + 0.075, 0.004)
        for x in (-L / 2 + 0.25, 0.0, L / 2 - 0.25):
            for s in (-1, 1): p.seg('madeira_escura', (x + s * 0.06, 0.42, zb), (x + s * 0.12, 0.0, zb), 0.05, 0.1)
    for i, x in enumerate(np.linspace(-L / 2 + 0.3, L / 2 - 0.3, 4)):                                   # pratos de lata e canecas
        for zs in (-1, 1):
            torno(p, 'lata', [(0.0, H), (0.1, H), (0.12, H + 0.025), (0.115, H + 0.025), (0.095, H + 0.004), (0.0, H + 0.004)], 20, 'y', (x, 0, zs * 0.22))
            if (i + (zs > 0)) % 2: torno(p, 'massa', [(0.0, H + 0.004), (0.07, H + 0.006), (0.0, H + 0.03)], 14, 'y', (x + 0.01, 0, zs * 0.22))   # comida
            torno(p, 'lata', [(0.0, H), (0.035, H), (0.035, H + 0.09), (0.032, H + 0.09), (0.032, H + 0.004), (0.0, H + 0.004)], 14, 'y', (x + 0.16, 0, zs * 0.3))
    torno(p, 'aco', [(0.0, H), (0.15, H), (0.17, H + 0.2), (0.165, H + 0.2), (0.145, H + 0.006), (0.0, H + 0.006)], 28, 'y', (0.0, 0, 0.0))   # panela no meio
    for s in (-1, 1): varrer(p, 'aco', circ(0.006, 6), [(s * 0.165, H + 0.17, -0.03), (s * 0.21, H + 0.17, -0.02), (s * 0.21, H + 0.17, 0.02), (s * 0.165, H + 0.17, 0.03)])
    torno(p, 'massa', [(0.0, H + 0.15), (0.16, H + 0.15)], 24, 'y', (0, 0, 0))
    p.seg('madeira_crua', (0.05, H + 0.16, 0.0), (0.2, H + 0.32, 0.1), 0.02, 0.012)                    # concha de pau


@item('panelao_tripe', 'Panelão no tripé sobre fogueira', 'mobilias', 'comunidade', comodos=['abrigo', 'fazenda', 'rua', 'parque'],
      constroi={'lenha': 3, 'corrente_cadeado': 1, 'pedras': 8, 'sucata_metal': 4}, ferramenta='martelo', estacao_obra='forja_tambor', fase=3,
      trabalha=1, ponto_uso=[0.0, 0.0, 0.8], luz_m=6,
      estacao='cozinha comunitária (uma panela alimenta 10 moradores; sopa rende mais que comer cada lata sozinho)')
def panelao_tripe(M):
    p = M.base; rng = np.random.default_rng(81); Hc = 1.75
    for k in range(10):                                                                              # roda de pedras
        a = k * 2 * math.pi / 10 + rng.uniform(-0.1, 0.1); r = 0.42
        fofo(p, 'pedra', r * math.cos(a), 0.06, r * math.sin(a), rng.uniform(0.08, 0.11), rng.uniform(0.06, 0.08), rng.uniform(0.07, 0.1), 0.3, 0.3, (6, 8))
    torno(p, 'cinza_fogueira', [(0.0, 0.0), (0.36, 0.0), (0.3, 0.025), (0.0, 0.035)], 20, 'y', (0, 0, 0))
    for k in range(5):                                                                               # lenha em tenda com brasa
        a = k * 2 * math.pi / 5
        p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.035, segment=[(0.28 * math.cos(a), 0.03, 0.28 * math.sin(a)), (0.05 * math.cos(a), 0.2, 0.05 * math.sin(a))], sections=8))
    fofo(p, 'brasa', 0.0, 0.04, 0.0, 0.16, 0.04, 0.16, 0.5, 0.5, (8, 12))
    pes = []
    for k in range(3):                                                                               # tripe de varas amarradas
        a = math.pi / 2 + k * 2 * math.pi / 3; b = (0.85 * math.cos(a), 0.0, 0.85 * math.sin(a)); pes.append(b)
        p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.035, segment=[b, (0.0 - 0.12 * math.cos(a), Hc + 0.2, -0.12 * math.sin(a))], sections=10))
    _torcido(p, 'corda', [(0.06 * math.cos(t), Hc + 0.02 + 0.02 * t, 0.06 * math.sin(t)) for t in np.linspace(0, 4 * math.pi, 20)], 0.008)
    for k in range(9):                                                                               # corrente
        y = Hc - 0.02 - k * 0.055; t = trimesh.creation.torus(0.022, 0.006, major_sections=10, minor_sections=6)
        t.apply_transform(_rot(math.pi / 2, [1, 0, 0]) if k % 2 else _rot(math.pi / 2, [0, 1, 0]) @ _rot(math.pi / 2, [1, 0, 0])); t.vertices[:, 1] *= 1.4
        t.apply_translation([0, y, 0]); p.add('aco', t)
    yb = Hc - 0.53                                                                                   # panelao de aluminio com alca
    torno(p, 'aco', [(0.0, 0.32), (0.2, 0.32), (0.27, 0.4), (0.28, 0.62), (0.29, 0.64), (0.27, 0.64), (0.265, 0.4), (0.0, 0.335)], 32, 'y', (0, 0, 0))
    varrer(p, 'aco', circ(0.006, 6), [(-0.29, 0.6, 0.0)] + [(-0.29 * math.cos(t), 0.6 + (yb - 0.6) * math.sin(t), 0.0) for t in np.linspace(0.2, math.pi - 0.2, 9)] + [(0.29, 0.6, 0.0)])
    torno(p, 'massa', [(0.0, 0.58), (0.27, 0.58)], 28, 'y', (0, 0, 0))                                   # sopa
    for k in range(5): fofo(p, 'cenoura', rng.uniform(-0.15, 0.15), 0.585, rng.uniform(-0.15, 0.15), 0.025, 0.01, 0.025, 0.5, 0.5, (5, 6))
    p.seg('madeira_crua', (0.1, 0.6, 0.05), (0.32, 0.95, 0.15), 0.025, 0.015)                         # colher de pau
    for i, (x, z) in enumerate(((0.75, -0.3), (0.82, 0.0), (0.7, 0.3))):                                 # tocos para sentar e lenha de reserva
        anel(p, 'madeira_lenha', 0.0, 0.17, 0.0, 0.4, 16, 'y', (x + 0.3, 0, z * 1.6)) if i == 1 else None
    for k in range(4): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.04, segment=[(-0.75, 0.04 + 0.075 * (k // 2), -0.5 + 0.09 * (k % 2) + 0.045 * (k // 2)), (-0.35, 0.04 + 0.075 * (k // 2), -0.62 + 0.09 * (k % 2) + 0.045 * (k // 2))], sections=8))


@item('maca_campanha', 'Maca de campanha dobrável', 'mobilias', 'comunidade', comodos=['abrigo', 'clinica', 'igreja', 'escolinha'],
      constroi={'cano_metal': 3, 'lona': 1, 'corda': 1}, ferramenta='chave_inglesa', estacao_obra='bancada_costura', fase=3, deitar=True,
      ponto_uso=[0.0, 0.0, 0.55], estacao='enfermaria (ferido deitado aqui sara 2× mais rápido; 3 macas e uma mesa de enfermaria viram hospital de campanha)')
def maca_campanha(M):
    p = M.base; L, W, H = 1.95, 0.66, 0.45
    for zs in (-1, 1):                                                                               # tubos laterais com punhos
        p.add('aco_pintado', trimesh.creation.cylinder(radius=0.016, segment=[(-L / 2 - 0.1, H, zs * W / 2), (L / 2 + 0.1, H, zs * W / 2)], sections=12))
        for xs in (-1, 1): p.add('borracha', trimesh.creation.cylinder(radius=0.02, segment=[(xs * (L / 2 + 0.0), H, zs * W / 2), (xs * (L / 2 + 0.1), H, zs * W / 2)], sections=12))
    for x in (-L / 2 + 0.25, 0.0, L / 2 - 0.25):                                                     # pernas em X
        for s in (-1, 1): p.add('aco_pintado', trimesh.creation.cylinder(radius=0.012, segment=[(x + s * 0.18, H - 0.01, -W / 2 + 0.02), (x - s * 0.18, 0.02, -W / 2 + 0.02)], sections=8))
        for s in (-1, 1): p.add('aco_pintado', trimesh.creation.cylinder(radius=0.012, segment=[(x + s * 0.18, H - 0.01, W / 2 - 0.02), (x - s * 0.18, 0.02, W / 2 - 0.02)], sections=8))
        for s in (-1, 1): p.add('aco_pintado', trimesh.creation.cylinder(radius=0.01, segment=[(x + s * 0.18, 0.02, -W / 2 + 0.02), (x + s * 0.18, 0.02, W / 2 - 0.02)], sections=8))
        cyl_eixo(p, 'aco', 0.014, -W / 2 - 0.0, -W / 2 + 0.04, 'z', (x, H / 2, 0), 10); cyl_eixo(p, 'aco', 0.014, W / 2 - 0.04, W / 2, 'z', (x, H / 2, 0), 10)
    q = P()                                                                                          # lona com leve barriga
    for i in range(12):
        x0, x1 = -L / 2 + 0.02 + i * (L - 0.04) / 12, -L / 2 + 0.02 + (i + 1) * (L - 0.04) / 12
        for j in range(4):
            z0, z1 = -W / 2 + j * W / 4, -W / 2 + (j + 1) * W / 4
            sag = lambda z: -0.03 * (1 - (2 * z / W) ** 2)
            q.hull('lona_verde', [(x, H + sag(z) + d, z) for x in (x0, x1) for z in (z0, z1) for d in (-0.004, 0.0)])
    p.merge(q)
    for zs in (-1, 1): p.cham('lona_verde', -L / 2 + 0.02, L / 2 - 0.02, H - 0.03, H + 0.025, zs * W / 2 - 0.022, zs * W / 2 + 0.022, 0.01)   # bainha no tubo
    fofo(p, 'cobertor_cinza', 0.25, H + 0.03, 0.0, 0.55, 0.035, 0.34, 0.3, 0.3, (10, 14)); _amassar(p, 'cobertor_cinza', 0.01, 9.0, 31, sub=0)
    fofo(p, 'travesseiro', -0.75, H + 0.02, 0.0, 0.16, 0.05, 0.24, 0.3, 0.3, (8, 12))
    torno(p, 'atadura', [(0.0, -0.035), (0.035, -0.035), (0.035, 0.035), (0.0, 0.035)], 14, 'z', (0.85, H + 0.035, 0.18))   # rolo de atadura


# ---------------------------------------------------------------------------- AGUA, COMIDA E ENERGIA
@item('poco_sarilho', 'Poço de pedra com sarilho', 'mobilias', 'comunidade', comodos=['abrigo', 'fazenda', 'rua'],
      constroi={'pedras': 24, 'cimento': 2, 'lenha': 4, 'corda': 1, 'chapa_metal': 1}, ferramenta='pa', fase=3, trabalha=1, ponto_uso=[0.0, 0.0, 0.95],
      produz={'item': 'galao_agua', 'qtd': 4, 'a_cada_min': 60, 'consome': {}},
      estacao='poço (água sem fim, mas precisa ferver ou filtrar; cavar leva 2 dias de 3 moradores)')
def poco_sarilho(M):
    p = M.base; R0, R1, H = 0.5, 0.72, 0.78; rng = np.random.default_rng(44)
    anel(p, 'fuligem', R0 - 0.02, R0, -0.9, H - 0.02, 24, 'y', (0, 0, 0))                                 # parede interna e agua no fundo
    torno(p, 'agua', [(0.0, -0.55), (R0 - 0.02, -0.55)], 24, 'y', (0, 0, 0))
    n = 18
    for k in range(5):                                                                               # fiadas de pedra desencontradas
        y0 = k * 0.15
        for i in range(n):
            a0 = (i + 0.5 * (k % 2)) * 2 * math.pi / n + 0.015; a1 = (i + 1 + 0.5 * (k % 2)) * 2 * math.pi / n - 0.015
            r0, r1 = R0, R1 + rng.uniform(-0.02, 0.02); yy0 = y0 + 0.006; yy1 = y0 + 0.145 + (0.02 if k == 4 else 0)
            pts = [(r * math.cos(a), y, r * math.sin(a)) for r in (r0, r1) for a in (a0, (a0 + a1) / 2, a1) for y in (yy0, yy1)]
            p.hull('pedra_poco', pts)
    anel(p, 'concreto', R0 - 0.01, R1 + 0.03, H - 0.0, H + 0.04, 36, 'y', (0, 0, 0))                     # coroa de cimento
    for xs in (-1, 1):                                                                               # esteios e telhadinho
        p.cham('madeira_escura', xs * (R1 - 0.03) - 0.06, xs * (R1 - 0.03) + 0.06, 0.0, 2.08, -0.06, 0.06, 0.006)
    for zs in (-1, 1):
        for k, x in enumerate(np.linspace(-R1 - 0.18, R1 + 0.18, 9)):                                    # tabuas do telhado em duas aguas
            p.hull('madeira', [(xx, y + d, zs * z) for xx in (x - 0.095, x + 0.095 - 0.006) for (y, z) in ((2.13, 0.0), (1.8, 0.64)) for d in (0.0, 0.022)])
    p.cham('madeira_escura', -R1 - 0.22, R1 + 0.22, 2.08, 2.14, -0.035, 0.035, 0.004)                     # cumeeira
    for xs in (-1, 1): p.cham('madeira_escura', xs * (R1 - 0.03) - 0.05, xs * (R1 - 0.03) + 0.05, 1.82, 1.9, -0.45, 0.45, 0.004)
    q = M.parte('sarilho', (0.0, 1.3, 0.0), 'porta', eixo='x', abre_graus=360, gira_livre=True)       # rolo com corda enrolada e manivela
    q.add('madeira_lenha', trimesh.creation.cylinder(radius=0.07, segment=[(-R1 + 0.04, 0, 0), (R1 - 0.04, 0, 0)], sections=16))
    for k in range(14): q.add('corda', trimesh.creation.torus(0.077, 0.008, major_sections=18, minor_sections=6, transform=trimesh.transformations.translation_matrix([-0.12 + k * 0.016, 0, 0]) @ _rot(math.pi / 2, [0, 1, 0])))
    q.add('aco', trimesh.creation.cylinder(radius=0.014, segment=[(-R1 - 0.1, 0, 0), (R1 + 0.15, 0, 0)], sections=10))
    q.cham('aco', R1 + 0.13, R1 + 0.16, -0.02, 0.28, -0.02, 0.02, 0.003)
    q.add('madeira_escura', trimesh.creation.cylinder(radius=0.02, segment=[(R1 + 0.16, 0.25, 0), (R1 + 0.3, 0.25, 0)], sections=10))
    _mover(q, (0.0, 1.3, 0.0))
    p.add('corda', trimesh.creation.cylinder(radius=0.007, segment=[(0.06, 1.3 - 0.075, 0.0), (0.06, 0.72, 0.0)], sections=6))   # corda descendo ao balde
    _balde(p, (0.06, 0.38, 0.0), 0.12, 0.14, 0.24, 'balde_zinco', True)
    _balde(p, (0.95, 0.0, 0.35), 0.12, 0.14, 0.24, 'balde_zinco', True)


@item('coelheira', 'Coelheira de tábuas e tela', 'mobilias', 'agricultura', comodos=['abrigo', 'fazenda', 'casas'],
      constroi={'tabua': 6, 'caixa_pregos': 1, 'arame_liso': 1, 'chapa_metal': 1}, ferramenta='martelo', fase=3, trabalha=1, ponto_uso=[0.0, 0.0, 0.7],
      produz={'item': 'carne_crua', 'qtd': 2, 'a_cada_min': 2880, 'consome': {'restos de comida': 2, 'palha': 1}},
      estacao='criação (2 casais de coelhos dão carne e couro a cada 2 dias, se tiver capim e restos)')
def coelheira(M):
    p = M.base; X, Z, Y0, H = 0.75, 0.33, 0.5, 0.55
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_escura', xs * X - 0.05 * (xs > 0), xs * X + 0.05 * (xs < 0), 0.0, Y0 + H + (0.08 if zs < 0 else 0.0), zs * Z - 0.05 * (zs > 0), zs * Z + 0.05 * (zs < 0), 0.004)
    p.cham('madeira', -X, X, Y0, Y0 + 0.025, -Z, Z, 0.003)                                            # piso, fundo e laterais
    for z in np.linspace(-Z + 0.05, Z - 0.05, 4): p.cham('madeira', -X, X, Y0, Y0 + 0.025, z - 0.07, z + 0.07, 0.003)
    for k, y in enumerate(np.arange(Y0 + 0.03, Y0 + H + 0.05, 0.1)): p.cham('madeira', -X + 0.02, X - 0.02, y, y + 0.095, -Z, -Z + 0.018, 0.003)
    for xs in (-1, 1):
        for y in np.arange(Y0 + 0.03, Y0 + H, 0.1): p.cham('madeira', xs * X - 0.018 * (xs > 0), xs * X + 0.018 * (xs < 0), y, y + 0.095, -Z + 0.02, Z - 0.02, 0.003)
    p.cham('madeira', 0.1, 0.12, Y0 + 0.02, Y0 + H, -Z + 0.02, Z - 0.02, 0.003)                       # divisoria: ninho fechado a direita
    p.cham('madeira', 0.12, X - 0.05, Y0 + 0.02, Y0 + H, Z - 0.025, Z - 0.005, 0.003)
    m = trimesh.creation.extrude_polygon(Point(0, 0).buffer(0.09), 0.004); m.apply_transform(_rot(math.pi / 2, [0, 1, 0])); m.apply_translation([0.124, Y0 + 0.15, 0.0]); p.add('fuligem', m)   # passagem
    p.cham('madeira_escura', -X + 0.04, 0.1, Y0 + H - 0.04, Y0 + H, Z - 0.03, Z, 0.003); p.cham('madeira_escura', -X + 0.04, 0.1, Y0 + 0.02, Y0 + 0.06, Z - 0.03, Z, 0.003)
    _tela(p, -X + 0.05, 0.09, Y0 + 0.06, Y0 + H - 0.04, Z - 0.015, 18, 9)
    fofo(p, 'palha', -0.35, Y0 + 0.04, 0.0, 0.3, 0.03, 0.2, 0.6, 0.6, (8, 12)); fofo(p, 'palha', 0.42, Y0 + 0.05, -0.05, 0.25, 0.05, 0.2, 0.6, 0.6, (8, 12))
    for k, (x, z, s) in enumerate(((-0.4, 0.05, 1.0), (-0.15, -0.1, 0.85))):                          # dois coelhos
        fofo(p, 'pele_coelho', x, Y0 + 0.1, z, 0.12 * s, 0.075 * s, 0.075 * s, 0.4, 0.5, (10, 12))
        fofo(p, 'pele_coelho', x + 0.11 * s, Y0 + 0.15, z, 0.055 * s, 0.05 * s, 0.045 * s, 0.4, 0.5, (8, 10))
        for dz in (-0.018, 0.018): fofo(p, 'pele_coelho', x + 0.1 * s, Y0 + 0.23, z + dz * s, 0.018 * s, 0.06 * s, 0.01 * s, 0.5, 0.5, (6, 8))
        fofo(p, 'branco_tel', x - 0.12 * s, Y0 + 0.12, z, 0.025, 0.025, 0.025, 0.5, 0.5, (6, 6))
    torno(p, 'terracota', [(0.0, Y0 + 0.025), (0.07, Y0 + 0.025), (0.08, Y0 + 0.07), (0.07, Y0 + 0.07), (0.06, Y0 + 0.035), (0.0, Y0 + 0.035)], 18, 'y', (-0.6, 0, -0.18))   # cocho de barro
    torno(p, 'pet', [(0.0, 0.0), (0.045, 0.0), (0.045, 0.22), (0.015, 0.27), (0.015, 0.3), (0.0, 0.3)], 16, 'y', (-0.65, Y0 + 0.2, Z - 0.05))   # bebedouro de garrafa
    q = M.parte('tampa', (0.0, Y0 + H + 0.08, -Z - 0.03), 'tampa', eixo='x', abre_graus=-80)          # telhado que abre (chapa sobre tabuas)
    q.cham('madeira', -X - 0.06, X + 0.06, 0.0, 0.02, 0.0, 2 * Z + 0.12, 0.003)
    _ondulada(q, 'telha_ondulada', -X - 0.08, X + 0.08, -0.02, 2 * Z + 0.16, 0.03)
    q.cham('madeira_escura', -0.08, 0.08, -0.02, 0.0, 2 * Z + 0.08, 2 * Z + 0.12, 0.003)
    q.parts = {k: [m.apply_transform(_rot(-0.12, [1, 0, 0])) or m for m in ms] for k, ms in q.parts.items()}
    _mover(q, (0.0, Y0 + H + 0.08, -Z - 0.03))


@item('estufa', 'Estufa de cano e plástico', 'mobilias', 'agricultura', comodos=['abrigo', 'fazenda'],
      constroi={'tubo_pvc': 8, 'rolo_plastico': 2, 'tabua': 6, 'terra': 10}, ferramenta='pa', fase=3, trabalha=1, ponto_uso=[0.0, 0.0, 0.0],
      produz={'item': 'cesto_legumes', 'qtd': 1, 'a_cada_min': 1440, 'consome': {'galao_agua': 1}},
      estacao='estufa (canteiros que produzem até no inverno; com adubo rendem 50 % mais)')
def estufa(M):
    p = M.base; L, W, H = 4.0, 2.4, 2.1; rng = np.random.default_rng(7)
    arco = lambda t: (W / 2 * math.cos(t), 0.15 + (H - 0.15) * math.sin(t))
    ts = np.linspace(0, math.pi, 17)
    xs = np.linspace(-L / 2, L / 2, 6)
    for x in xs: varrer(p, 'pvc', circ(0.016, 8), [(x, arco(t)[1], arco(t)[0]) for t in ts], cap=True)   # arcos de cano
    for x in xs:
        for zs in (-1, 1): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.025, segment=[(x, 0.0, zs * W / 2), (x, 0.3, zs * W / 2)], sections=8))
    for zs in (-1, 1): p.cham('madeira_escura', -L / 2 - 0.05, L / 2 + 0.05, 0.0, 0.15, zs * W / 2 - 0.03, zs * W / 2 + 0.03, 0.004)   # base de tabua
    p.add('pvc', trimesh.creation.cylinder(radius=0.016, segment=[(-L / 2, H, 0), (L / 2, H, 0)], sections=8))   # cumeeira
    for t in (0.5, math.pi - 0.5): p.add('pvc', trimesh.creation.cylinder(radius=0.012, segment=[(-L / 2, arco(t)[1], arco(t)[0]), (L / 2, arco(t)[1], arco(t)[0])], sections=8))
    q = P()                                                                                          # plastico em gomos, com barriga entre os arcos
    for i in range(len(xs) - 1):
        for j in range(len(ts) - 1):
            t0, t1 = ts[j], ts[j + 1]; pts = []
            for x, fx in ((xs[i], 0.0), ((xs[i] + xs[i + 1]) / 2, 1.0), (xs[i + 1], 0.0)):
                for t in (t0, t1):
                    rr = 1.0 - 0.012 * fx; z, y = arco(t); pts += [(x, 0.15 + (y - 0.15) * rr + 0.02, z * rr + 0.02 * math.cos(t)), (x, 0.15 + (y - 0.15) * rr + 0.024, z * rr + 0.024 * math.cos(t))]
            q.hull('plastico_estufa', pts[:4] + pts[4:8]); q.hull('plastico_estufa', pts[4:])
    p.merge(q)
    q = P()                                                                                          # fundo fechado
    poly = Polygon([(arco(t)[0], arco(t)[1]) for t in ts] + [(-W / 2, 0.15), (W / 2, 0.15)]).buffer(0)
    m = trimesh.creation.extrude_polygon(poly, 0.004); m.apply_transform(_rot(math.pi / 2, [0, 1, 0])); m.apply_translation([-L / 2 - 0.02, 0, 0]); q.add('plastico_estufa', m)
    p.merge(q)
    for s in (-1, 1):                                                                                # frente: abas enroladas e porta aberta
        p.add('plastico_estufa', trimesh.creation.cylinder(radius=0.05, segment=[(L / 2 + 0.03, 0.2, s * (W / 2 - 0.15)), (L / 2 + 0.03, H - 0.2, s * 0.25)], sections=10))
        p.add('pvc', trimesh.creation.cylinder(radius=0.016, segment=[(L / 2, 0.0, s * 0.45), (L / 2, 1.85, s * 0.45)], sections=8))
    p.add('pvc', trimesh.creation.cylinder(radius=0.016, segment=[(L / 2, 1.85, -0.45), (L / 2, 1.85, 0.45)], sections=8))
    for zs in (-1, 1):                                                                               # dois canteiros elevados com plantas
        zc = zs * 0.62
        for xs_ in (-1, 1): p.cham('madeira_crua', -L / 2 + 0.2, L / 2 - 0.3, 0.0, 0.32, zc + xs_ * 0.38 - 0.02 * (xs_ > 0), zc + xs_ * 0.38 + 0.02 * (xs_ < 0), 0.004)
        for xx in (-L / 2 + 0.2, L / 2 - 0.3): p.cham('madeira_crua', xx - 0.02 * (xx > 0), xx + 0.02 * (xx < 0), 0.0, 0.32, zc - 0.38, zc + 0.38, 0.004)
        p.box('terra', -L / 2 + 0.22, L / 2 - 0.32, 0.0, 0.28, zc - 0.36, zc + 0.36)
        for x in np.arange(-L / 2 + 0.4, L / 2 - 0.4, 0.32):
            for dz in (-0.18, 0.18):
                tipo = int((x + 3) * 3 + zs) % 3; cx, cz = x + rng.uniform(-0.03, 0.03), zc + dz
                if tipo == 0:                                                                        # alface
                    for k in range(6): a = k * 2 * math.pi / 6; fofo(p, 'alface', cx + 0.05 * math.cos(a), 0.31, cz + 0.05 * math.sin(a), 0.07, 0.025, 0.05, 0.5, 0.4, (6, 8))
                elif tipo == 1:                                                                      # tomateiro com estaca
                    p.add('madeira_crua', trimesh.creation.cylinder(radius=0.008, segment=[(cx, 0.28, cz), (cx, 0.95, cz)], sections=6))
                    for k in range(7): fofo(p, 'muda', cx + rng.uniform(-0.08, 0.08), 0.4 + k * 0.08, cz + rng.uniform(-0.08, 0.08), 0.07, 0.03, 0.06, 0.5, 0.4, (6, 8))
                    for k in range(3): p.sphere('tomate', 0.025, cx + rng.uniform(-0.06, 0.06), 0.5 + rng.uniform(0, 0.3), cz + rng.uniform(-0.06, 0.06), 1)
                else:                                                                                # cenoura (rama)
                    for k in range(5): p.seg('muda', (cx, 0.28, cz), (cx + rng.uniform(-0.06, 0.06), 0.42, cz + rng.uniform(-0.06, 0.06)), 0.012, 0.004)
    _balde(p, (L / 2 - 0.15, 0.0, 0.05), 0.12, 0.15, 0.26, 'plastico_azul', True)                     # regador de galao
    p.add('pvc', trimesh.creation.cylinder(radius=0.01, segment=[(-L / 2 + 0.1, H - 0.25, 0.0), (L / 2 - 0.2, H - 0.25, 0.0)], sections=6))   # mangueira de gotejamento


@item('painel_solar', 'Painéis solares no cavalete com baterias', 'mobilias', 'energia', comodos=['abrigo', 'fazenda', 'casas'],
      constroi={'lenha': 4, 'fio_eletrico': 2, 'bateria_carro': 2, 'placa_circuito': 1, 'tabua': 2}, ferramenta='chave_inglesa', estacao_obra='bancada_eletronica',
      fase=3, energia_w=300, precisa_achar='placas solares (telhados das casas, do posto e da concessionária)',
      estacao='energia (2 placas de 150 W carregam as baterias de dia: luz, rádio e cerca elétrica à noite)')
def painel_solar(M):
    p = M.base; ang = math.radians(32); Wp, Lp, gap = 1.0, 1.6, 0.04
    img = Image.new('RGB', (512, 820), (14, 24, 52)); d = ImageDraw.Draw(img)
    for i in range(6):
        for j in range(10):
            x0, y0 = 8 + i * 83, 8 + j * 80; d.rectangle([x0, y0, x0 + 78, y0 + 75], fill=(18, 34, 78))
            for k in range(1, 4): d.line([x0, y0 + k * 19, x0 + 78, y0 + k * 19], fill=(60, 74, 110), width=1)
            for cx, cy in ((x0, y0), (x0 + 78, y0), (x0, y0 + 75), (x0 + 78, y0 + 75)): d.polygon([(cx - 6, cy), (cx, cy - 6), (cx + 6, cy), (cx, cy + 6)], fill=(200, 206, 214))
    for i in (2, 4): d.line([8 + i * 83 - 3, 0, 8 + i * 83 - 3, 820], fill=(170, 176, 186), width=3)
    mat_imagem('celulas_solares', img, 0.18, 0.2)
    y0, z0 = 0.55, 0.55                                                                              # borda de baixo do painel, na frente
    R = _rot(-(math.pi / 2 - ang), [1, 0, 0])                                                         # plano do painel: comprimento sobe para tras
    def T(x, u, w=0.0):                                                                             # u ao longo da inclinacao, w normal ao plano
        return (x, y0 + u * math.sin(ang) + w * math.cos(ang), z0 - u * math.cos(ang) + w * math.sin(ang))
    for s in (-1, 1):
        x0, x1 = (-Wp - gap / 2, -gap / 2) if s < 0 else (gap / 2, Wp + gap / 2)
        p.hull('celulas_solares', [T(x, u, w) for x in (x0 + 0.02, x1 - 0.02) for u in (0.02, Lp - 0.02) for w in (0.0, 0.006)])
        for u0, u1 in ((0.0, 0.02), (Lp - 0.02, Lp)): p.hull('painel_moldura', [T(x, u, w) for x in (x0, x1) for u in (u0, u1) for w in (-0.03, 0.009)])
        for xa, xb in ((x0, x0 + 0.02), (x1 - 0.02, x1)): p.hull('painel_moldura', [T(x, u, w) for x in (xa, xb) for u in (0.0, Lp) for w in (-0.03, 0.009)])
        p.hull('plastico_branco', [T(x, u, w) for x in ((x0 + x1) / 2 - 0.06, (x0 + x1) / 2 + 0.06) for u in (Lp * 0.85 - 0.04, Lp * 0.85 + 0.04) for w in (-0.06, -0.03)])   # caixa de juncao
    def uvf(v, n):
        x = v[:, 0]; u = (v[:, 1] - y0) * math.sin(ang) - (v[:, 2] - z0) * math.cos(ang)
        xa = np.where(x < 0, -Wp - gap / 2 + 0.02, gap / 2 + 0.02)
        return np.stack([(x - xa) / (Wp - 0.04), (u - 0.02) / (Lp - 0.04)], 1)
    p.uv['celulas_solares'] = uvf
    top = T(0, Lp - 0.15, -0.04); bot = T(0, 0.15, -0.04)
    for x in (-Wp - gap / 2 + 0.15, -0.1, 0.1, Wp + gap / 2 - 0.15):                                  # cavalete de caibros
        p.seg('madeira_crua', (x, top[1], top[2]), (x, 0.0, top[2]), 0.06, 0.06)
        p.seg('madeira_crua', (x, bot[1], bot[2]), (x, 0.0, bot[2]), 0.06, 0.06)
        p.seg('madeira_crua', (x, 0.2, bot[2]), (x, 0.2, top[2]), 0.045, 0.045)
    for (yy, zz) in (top[1:], bot[1:]): p.seg('madeira_crua', (-Wp - gap / 2, yy - 0.03, zz), (Wp + gap / 2, yy - 0.03, zz), 0.06, 0.06)
    p.seg('madeira_crua', (-Wp, 0.2, top[2]), (Wp, 1.0, top[2]), 0.04, 0.04)                          # mao-francesa diagonal
    xc, zc = 1.45, 0.4                                                                               # caixote com 2 baterias e controlador
    for xs in (-1, 1): p.cham('madeira_crua', xc + xs * 0.32 - 0.02 * (xs > 0), xc + xs * 0.32 + 0.02 * (xs < 0), 0.0, 0.32, zc - 0.25, zc + 0.25, 0.003)
    for zs in (-1, 1):
        for y in (0.0, 0.11, 0.22): p.cham('madeira_crua', xc - 0.32, xc + 0.32, y, y + 0.095, zc + zs * 0.25 - 0.02 * (zs > 0), zc + zs * 0.25 + 0.02 * (zs < 0), 0.003)
    for k, x in enumerate((xc - 0.15, xc + 0.15)):
        p.cham('plastico_preto', x - 0.12, x + 0.12, 0.02, 0.24, zc - 0.09, zc + 0.09, 0.008)
        for dx, cor in ((-0.07, 'plastico_vermelho'), (0.07, 'plastico_preto')): torno(p, cor, [(0.0, 0.24), (0.013, 0.24), (0.011, 0.265), (0.0, 0.265)], 10, 'y', (x + dx, 0, zc - 0.04))
    p.cham('plastico_cinza', xc + 0.36, xc + 0.38, 0.4, 0.58, zc - 0.08, zc + 0.08, 0.002)              # controlador de carga na tabua
    p.cham('madeira_crua', xc + 0.32, xc + 0.36, 0.0, 0.7, zc - 0.1, zc + 0.1, 0.003)
    p.cham('plastico_preto', xc + 0.38, xc + 0.383, 0.5, 0.56, zc - 0.06, zc + 0.02, 0.0005)
    for k, cor in enumerate(('folha_verde', 'tinta_amarela', 'folha_verde')): p.box(cor, xc + 0.38, xc + 0.386, 0.43, 0.44, zc - 0.05 + k * 0.025, zc - 0.04 + k * 0.025)
    a = T(-0.06, Lp * 0.85, -0.06); b = T(0.06, Lp * 0.85, -0.06)
    for c0, off in ((a, -0.01), (b, 0.01)):                                                          # cabos das placas ate o controlador
        varrer(p, 'fio_vermelho' if off < 0 else 'plastico_preto', circ(0.005, 6), [c0, (c0[0], c0[1] - 0.2, c0[2] + 0.05), (0.6, 0.35, -0.1 + off), (xc + 0.2, 0.36, zc - 0.2 + off), (xc + 0.37, 0.45, zc + off)], cap=False)
    for k, x in enumerate((xc - 0.15, xc + 0.15)):
        varrer(p, 'fio_vermelho', circ(0.004, 6), [(x - 0.07, 0.265, zc - 0.04), (x - 0.03, 0.35, zc - 0.02), (xc + 0.37, 0.48, zc - 0.05)], cap=False)


@item('cata_vento', 'Cata-vento de bomba d\'água em torre', 'mobilias', 'energia', comodos=['fazenda', 'abrigo'],
      constroi={'cano_metal': 8, 'chapa_metal': 6, 'engrenagens': 1, 'tambor_200l': 1}, ferramenta='chave_inglesa', estacao_obra='forja_tambor',
      fase=3, produz={'item': 'galao_agua', 'qtd': 2, 'a_cada_min': 60, 'consome': {}}, precisa_achar='bomba de poço (ferro-velho ou fazenda)',
      estacao='bomba de vento (puxa água do lençol sem ninguém trabalhar; enche o tambor ao lado)')
def cata_vento(M):
    p = M.base; H = 5.2; B = 0.85; T0 = 0.16
    pes = [(sx * B, sz * B) for sx in (-1, 1) for sz in (-1, 1)]
    top = lambda x, z: (x / B * T0, z / B * T0)
    for x, z in pes:                                                                                 # 4 pernas de cantoneira afunilando
        tx, tz = top(x, z); p.add('galvanizado', trimesh.creation.cylinder(radius=0.022, segment=[(x, 0.0, z), (tx, H, tz)], sections=6))
        p.cham('concreto', x - 0.12, x + 0.12, -0.02, 0.1, z - 0.12, z + 0.12, 0.01)
    lv = np.linspace(0.0, H - 0.4, 6)
    for i in range(len(lv) - 1):                                                                     # travessas e diagonais em X por face
        for (a, b) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            def at(c, y): f = 1 - (1 - T0 / B) * y / H; return (c[0] * B * f, y, c[1] * B * f)
            for y in (lv[i + 1],): p.add('galvanizado', trimesh.creation.cylinder(radius=0.012, segment=[at(a, y), at(b, y)], sections=6))
            p.add('galvanizado', trimesh.creation.cylinder(radius=0.008, segment=[at(a, lv[i]), at(b, lv[i + 1])], sections=6))
            p.add('galvanizado', trimesh.creation.cylinder(radius=0.008, segment=[at(b, lv[i]), at(a, lv[i + 1])], sections=6))
    p.box('madeira', -0.35, 0.35, H - 0.02, H + 0.02, -0.35, 0.35)                                   # plataforma de manutencao
    q = M.parte('cabeca', (0.0, H + 0.02, 0.0), 'porta', eixo='y', abre_graus=360, gira_livre=True)   # cabeca que vira com o vento
    anel(q, 'aco_pintado', 0.0, 0.08, 0.0, 0.2, 16, 'y', (0, 0, 0))
    q.cham('aco_pintado', -0.08, 0.08, 0.12, 0.28, -0.2, 0.45, 0.01)                                  # caixa de engrenagens
    q.add('aco', trimesh.creation.cylinder(radius=0.03, segment=[(0, 0.2, 0.45), (0, 0.2, 0.62)], sections=10))
    rot = P()                                                                                        # rotor de 18 pas curvas
    anel(rot, 'aco_pintado', 0.0, 0.16, -0.06, 0.06, 18, 'z', (0, 0, 0))
    for ra in (0.45, 1.15): anel(rot, 'aco_pintado', ra, ra + 0.025, -0.012, 0.012, 48, 'z', (0, 0, 0))
    for k in range(18):
        a = k * 2 * math.pi / 18
        pts = []
        for r in (0.3, 1.2):
            w = 0.07 + 0.11 * (r - 0.3) / 0.9
            for s in (-1, 1): pts.append((r * math.cos(a) - s * w * math.sin(a), r * math.sin(a) + s * w * math.cos(a), s * 0.04))
        for (xx, yy, zz) in list(pts): pts.append((xx, yy, zz + 0.006))
        rot.hull('galvanizado', pts)
        rot.add('aco_pintado', trimesh.creation.cylinder(radius=0.008, segment=[(0.12 * math.cos(a), 0.12 * math.sin(a), 0), (0.47 * math.cos(a), 0.47 * math.sin(a), 0)], sections=5))
    q.merge(rot, trimesh.transformations.translation_matrix([0, 0.2, 0.68]))
    q.seg('aco_pintado', (0, 0.2, -0.15), (0, 0.25, -1.55), 0.04, 0.04)                               # rabo-leme
    q.hull('tinta_vermelha', [(s * 0.004, y, z) for s in (-1, 1) for (y, z) in ((0.05, -1.0), (0.75, -1.1), (0.7, -1.9), (0.0, -1.85))])
    _mover(q, (0.0, H + 0.02, 0.0))
    p.add('aco', trimesh.creation.cylinder(radius=0.01, segment=[(0, 0.3, 0), (0, H, 0)], sections=6))   # haste da bomba
    torno(p, 'aco_pintado', [(0.0, 0.0), (0.09, 0.0), (0.09, 0.08), (0.05, 0.12), (0.05, 0.6), (0.06, 0.62), (0.0, 0.64)], 16, 'y', (0, 0, 0))
    p.seg('aco_pintado', (0.0, 0.5, 0.0), (0.6, 0.5, 0.95), 0.05, 0.05)                               # bica ate o tambor
    _tambor(p, (0.75, 0.0, 1.25), 0.29, 0.88, 'tambor_azul', False, False)
    torno(p, 'agua', [(0.0, 0.78), (0.28, 0.78)], 24, 'y', (0.75, 0, 1.25))
    for y in np.arange(0.3, H - 0.4, 0.3): p.cham('aco', -0.15, 0.15, y, y + 0.025, -B * (1 - (1 - T0 / B) * y / H) - 0.02, -B * (1 - (1 - T0 / B) * y / H) + 0.01, 0.003)   # degraus


@item('torre_radio', 'Torre de rádio da comunidade', 'mobilias', 'comunidade', comodos=['abrigo', 'igreja', 'delegacia', 'quartel'],
      constroi={'cano_metal': 10, 'fio_eletrico': 4, 'radio_portatil': 1, 'placa_circuito': 2, 'bateria_carro': 1, 'arame_liso': 2},
      ferramenta='chave_inglesa', estacao_obra='bancada_eletronica', fase=3, trabalha=1, ponto_uso=[0.6, 0.0, 1.0], marco=True,
      estacao='marco da fase Assentamento → Vila (chama sobreviventes de longe; abre trocas com outras comunidades e o mapa regional)')
def torre_radio(M):
    p = M.base; H = 8.0; rng = np.random.default_rng(90)
    p.cham('concreto', -0.35, 0.35, 0.0, 0.15, -0.35, 0.35, 0.02)
    cs = _mastro_trelica(p, 0.0, 0.0, 0.15, H, 0.32, 0.5, 'mastro_vermelho', 0.016)
    for k, y in enumerate(np.arange(0.15, H, 1.0)):                                                  # faixas brancas (pintura de aviacao) nos montantes
        if k % 2:
            for cx, cz in cs: anel(p, 'mastro_branco', 0.0, 0.019, y, y + 1.0, 8, 'y', (cx, 0, cz))
    p.add('aco', trimesh.creation.cylinder(radius=0.012, segment=[(0, H, 0), (0, H + 1.6, 0)], sections=8))   # antena vertical
    for s in (-1, 1):                                                                                # dipolo com isoladores
        p.add('aco', trimesh.creation.cylinder(radius=0.008, segment=[(0, H - 0.3, 0), (s * 1.1, H - 0.3, 0)], sections=6))
        anel(p, 'louca', 0.0, 0.02, s * 0.2 - 0.03, s * 0.2 + 0.03, 10, 'x', (0, H - 0.3, 0))
    for k in range(3):                                                                               # yagi direcional virada para a cidade
        z = 0.15 + k * 0.28; p.add('aco', trimesh.creation.cylinder(radius=0.006, segment=[(-0.45 + k * 0.05, H - 1.0, z), (0.45 - k * 0.05, H - 1.0, z)], sections=6))
    p.add('aco', trimesh.creation.cylinder(radius=0.01, segment=[(0, H - 1.0, 0.0), (0, H - 1.0, 0.75)], sections=6))
    torno(p, 'luz_vermelha', [(0.0, H + 1.6), (0.04, H + 1.62), (0.035, H + 1.7), (0.0, H + 1.72)], 12, 'y', (0, 0, 0))   # luz de topo
    for k in range(3):                                                                               # estais de cabo com esticadores e estacas
        a = math.pi / 2 + k * 2 * math.pi / 3 + 0.3; ax, az = 3.2 * math.cos(a), 3.2 * math.sin(a)
        for y in (H * 0.5, H * 0.92):
            cx, cz = cs[k]; p.add('aco', trimesh.creation.cylinder(radius=0.004, segment=[(cx, y, cz), (ax, 0.12, az)], sections=5))
        p.cham('concreto', ax - 0.15, ax + 0.15, -0.02, 0.1, az - 0.15, az + 0.15, 0.01)
        p.add('aco_pintado', trimesh.creation.cylinder(radius=0.012, segment=[(ax, 0.1, az), (ax + (cs[k][0] - ax) * 0.06, 0.5, az + (cs[k][1] - az) * 0.06)], sections=6))
    p.add('plastico_preto', trimesh.creation.cylinder(radius=0.01, segment=[(cs[0][0], H - 0.3, cs[0][1] + 0.02), (cs[0][0], 0.9, cs[0][1] + 0.02)], sections=6))   # cabo coaxial descendo
    xr, zr = 0.0, 1.1                                                                                # mesa de radio sob toldo de lona
    for x in (-0.55, 0.55):
        for z in (zr - 0.3, zr + 0.3): p.cham('madeira_escura', xr + x - 0.03, xr + x + 0.03, 0.0, 0.74, z - 0.03, z + 0.03, 0.003)
    p.cham('madeira', xr - 0.62, xr + 0.62, 0.74, 0.78, zr - 0.36, zr + 0.36, 0.004)
    p.cham('plastico_preto', xr - 0.25, xr + 0.15, 0.78, 0.94, zr - 0.25, zr + 0.0, 0.01)              # radio com mostrador e botoes
    p.box('jukebox_luz', xr - 0.2, xr - 0.02, 0.86, 0.91, zr + 0.0, zr + 0.003)
    for k in range(4): torno(p, 'aco_polido', [(0.0, 0.0), (0.012, 0.0), (0.012, 0.015), (0.0, 0.015)], 10, 'z', (xr + 0.03 + (k % 2) * 0.05, 0.83 + 0.06 * (k // 2), zr))
    p.add('plastico_preto', trimesh.creation.cylinder(radius=0.004, segment=[(cs[0][0], 0.9, cs[0][1] + 0.02), (xr - 0.2, 0.9, zr - 0.25)], sections=6))
    torno(p, 'plastico_preto', [(0.0, 0.0), (0.03, 0.0), (0.03, 0.05), (0.0, 0.06)], 12, 'y', (xr + 0.3, 0.78, zr - 0.1))   # microfone de mesa
    p.add('aco', trimesh.creation.cylinder(radius=0.005, segment=[(xr + 0.3, 0.84, zr - 0.1), (xr + 0.3, 0.95, zr - 0.05)], sections=6))
    p.sphere('plastico_preto', 0.025, xr + 0.3, 0.97, zr - 0.04, 1)
    p.cham('plastico_preto', xr - 0.55, xr - 0.31, 0.0, 0.2, zr - 0.1, zr + 0.08, 0.008)                # bateria de carro no chao
    p.cham('papel', xr + 0.2, xr + 0.5, 0.78, 0.782, zr + 0.05, zr + 0.3, 0.0005)                     # caderno de frequencias
    q = P()                                                                                          # toldo de lona amarrado no mastro
    q.hull('lona_azul', [(x, y + d, z) for x in (xr - 0.85, xr + 0.85) for (y, z) in ((1.95, 0.25), (1.75, zr + 0.65)) for d in (0.0, 0.004)])
    _amassar(q, 'lona_azul', 0.01, 6.0, 5, sub=2); p.merge(q)
    for x in (xr - 0.8, xr + 0.8): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.025, segment=[(x, 0.0, zr + 0.62), (x, 1.76, zr + 0.62)], sections=8))


# ---------------------------------------------------------------------------- LOOT DA COMUNIDADE
@item('carne_crua', 'Carne crua embrulhada', 'loot', 'comida', recurso='comida', valor=3, peso_kg=0.8, empilha=4, celulas=[1, 1], fase=3,
      efeito='estraga em 2 dias: cozinhe no panelão ou defume', onde=['fazenda'],
      obtem_de=[{'fazer': 'coelheira', 'qtd': 2}])
def carne_crua(M):
    p = M.base
    fofo(p, 'carne_crua', 0.0, 0.03, 0.0, 0.1, 0.03, 0.07, 0.4, 0.4, (10, 12))
    q = P(); fofo(q, 'papel', 0.0, 0.028, 0.0, 0.13, 0.03, 0.095, 0.3, 0.3, (10, 14)); _amassar(q, 'papel', 0.006, 30.0, 2, sub=0)
    for k in ('papel',): q.parts[k] = [m.slice_plane([0, 0, 0.02], [0, 0, -1]) for m in q.parts[k]]
    p.merge(q)
    _torcido(p, 'corda', [(-0.02, 0.064, -0.1), (-0.02, 0.066, 0.0), (-0.02, 0.064, 0.1)], 0.003)


@item('cesto_legumes', 'Cesto de legumes da estufa', 'loot', 'comida', recurso='comida', valor=4, peso_kg=2.5, empilha=1, celulas=[2, 2], fase=3,
      efeito='alface, tomate e cenoura: comida fresca que espanta a fraqueza', onde=['fazenda'],
      obtem_de=[{'fazer': 'estufa', 'qtd': 1}])
def cesto_legumes(M):
    p = M.base; rng = np.random.default_rng(12)
    torno(p, 'cesto', [(0.0, 0.0), (0.13, 0.0), (0.17, 0.16), (0.175, 0.17), (0.165, 0.17), (0.125, 0.008), (0.0, 0.008)], 28, 'y', (0, 0, 0))
    for y in (0.05, 0.1, 0.15): anel(p, 'cesto', 0.14 + y * 0.25, 0.146 + y * 0.25, y - 0.006, y + 0.006, 28, 'y', (0, 0, 0))
    varrer(p, 'cesto', circ(0.008, 6), [(-0.17, 0.17, 0.0)] + [(-0.17 * math.cos(t), 0.17 + 0.17 * math.sin(t), 0.0) for t in np.linspace(0.15, math.pi - 0.15, 11)] + [(0.17, 0.17, 0.0)])
    for k in range(5): p.sphere('tomate', 0.032, rng.uniform(-0.09, 0.09), 0.15 + rng.uniform(0, 0.02), rng.uniform(-0.09, 0.09), 1)
    for k in range(4):
        a = rng.uniform(0, 2 * math.pi); c = np.array([0.04 * math.cos(a), 0.15, 0.04 * math.sin(a)]); d = np.array([math.cos(a + 1.2), 0.15, math.sin(a + 1.2)])
        p.add('cenoura', trimesh.creation.cone(radius=0.016, height=0.15, sections=10, transform=_alinha(c, d)))
    for k in range(5): a = k * 2 * math.pi / 5; fofo(p, 'alface', -0.06 + 0.04 * math.cos(a), 0.18, 0.05 + 0.04 * math.sin(a), 0.06, 0.03, 0.045, 0.5, 0.4, (6, 8))


@item('rolo_plastico', 'Rolo de plástico transparente', 'loot', 'materiais', recurso='sucata', valor=2, peso_kg=4.0, empilha=1, celulas=[1, 3], fase=3,
      efeito='cobre estufas e janelas sem vidro', onde=['fazenda', 'supermercado', 'galeria', 'serraria'])
def rolo_plastico(M):
    p = M.base; L = 0.6; R = 0.08
    anel(p, 'papelao', 0.035, 0.04, -L / 2 - 0.01, L / 2 + 0.01, 16, 'x', (0, R, 0))
    for k, r in enumerate(np.linspace(0.042, R, 5)): anel(p, 'plastico_estufa', r - 0.004, r, -L / 2, L / 2, 32, 'x', (0, R, 0))
    q = P(); q.hull('plastico_estufa', [(x, y, z) for x in (-L / 2, L / 2) for (y, z) in ((0.0, 0.0), (0.0, 0.18), (0.003, 0.0), (0.003, 0.18))]); p.merge(q)   # ponta solta no chao
    p.cham('fita_crepe', -0.05, 0.05, R * 2 - 0.002, R * 2 + 0.002, -0.02, 0.02, 0.001)
