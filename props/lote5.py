# Lote 5: fase 1 do jogo ("Sozinho": sobreviver, achar abrigo, barricar, achar o 1o sobrevivente).
# Executado por gerar_props.py (usa as mesmas funcoes e materiais).
CORES.update({'casca': (66, 46, 30), 'pedra': (122, 118, 110), 'cinza_fogueira': (58, 56, 54), 'brasa': (150, 30, 6),
              'plastico_verde': (8, 30, 14), 'saco_lixo': (10, 10, 12), 'mala_azul': (8, 14, 34), 'verde_militar': (22, 34, 14), 'forro': (100, 26, 26),
              'nylon': (30, 66, 108), 'tinta_preta': (24, 24, 24), 'cobertor_cinza': (92, 94, 96), 'latao': (190, 150, 70)})
TEXTURAS.update({'casca': 'paint'})
METALICOS.update({'latao': (0.9, 0.3), 'verde_militar': (0.1, 0.6)})
FOSCOS.update({'plastico_verde': 0.5, 'saco_lixo': 0.45, 'mala_azul': 0.38, 'tinta_preta': 0.8, 'brasa': 0.9})
TEX_PROPRIAS += [('pedra', 'granito', 0.5, 512), ('cinza_fogueira', 'papelao', 0.5, 512), ('nylon', 'tecido', 0.5, 768),
                 ('cobertor_cinza', 'tecido', 0.5, 768), ('forro', 'tecido', 0.25, 1024)]
EMISSIVOS.update({'brasa': [1.0, 0.32, 0.04]})


def _rz(ang, c=(0, 0, 0)): return trimesh.transformations.rotation_matrix(ang, [0, 0, 1], point=c)


def _uv_girada(ang, c):
    """Projecao em caixa feita no referencial da tabua (veio ao longo do comprimento mesmo inclinada)."""
    R = _rz(-ang, c)
    def f(v, n):
        vr = trimesh.transform_points(v, R); nr = n @ R[:3, :3].T
        return uv_caixa(TILE)(vr, nr)
    return f


def _prancha(q, cx, cy, z0, L, ang=0.0, W=0.14, T=0.024, seed=0, mat='madeira_crua'):
    """Tabua pregada: chanfrada, com nos, ponta lascada e 2 pregos em cada ponta. Monta direto em q (coordenadas da montagem)."""
    rng = np.random.default_rng(seed); t = P()
    a = rng.uniform(0.0, 0.03)
    t.hull(mat, [(x, y, z) for x in (-L / 2 + a, L / 2 - 0.02) for y in (-W / 2, W / 2) for z in (0.002, T - 0.002)] +
                [(x, y, z) for x in (-L / 2 + a + 0.003, L / 2 - 0.023) for y in (-W / 2 + 0.003, W / 2 - 0.003) for z in (0.0, T)])
    t.hull(mat, [(L / 2 - 0.02, -W / 2, 0.002), (L / 2 - 0.02, W / 2, 0.002), (L / 2 - 0.02, -W / 2, T - 0.002), (L / 2 - 0.02, W / 2, T - 0.002),
                 (L / 2, -W / 2 + 0.02, T * 0.5), (L / 2 - 0.006, W / 2 - 0.035, T * 0.6)])                 # ponta lascada
    for x in rng.uniform(-L / 2 + 0.15, L / 2 - 0.15, 2):
        torno(t, 'madeira_escura', [(0.007, 0), (0.011, 0.0006)], 12, 'z', (x, rng.uniform(-W / 4, W / 4), T - 0.0003))
    for xs in (-1, 1):
        for dy in (-W / 4, W / 4):
            x = xs * (L / 2 - 0.075) + rng.uniform(-0.01, 0.01)
            torno(t, 'aco', [(0.0046, 0), (0.0046, 0.0012), (0.003, 0.0022)], 10, 'z', (x, dy + rng.uniform(-0.006, 0.006), T - 0.0002))
    q.merge(t, trimesh.transformations.translation_matrix([cx, cy, z0]) @ _rz(ang))
    q.uv[mat] = _uv_girada(ang, (cx, cy, z0))


def _barricada(M, sarrafo_h, tabuas, sarrafo_x=0.55):
    """Sarrafos verticais no batente (fixos) + tabuas como partes soltas (o jogo tira uma por vez conforme a vida cai)."""
    p = M.base
    for xs in (-1, 1):
        x = xs * sarrafo_x
        p.cham('madeira_crua', x - 0.035, x + 0.035, 0.04, sarrafo_h, 0.0, 0.03, 0.004)
        p.uv['madeira_crua'] = uv_veio_vertical
        for y in np.linspace(0.12, sarrafo_h - 0.1, 4):
            torno(p, 'aco', [(0.0046, 0), (0.0046, 0.0012), (0.003, 0.0022)], 10, 'z', (x, y, 0.0298))
    for i, (cx, cy, L, ang, cam) in enumerate(tabuas):
        z0 = 0.03 + cam * 0.024
        q = M.parte(f'tabua_{i + 1}', (cx, cy, z0), 'tabua', ordem=len(tabuas) - i, vida=40)
        _prancha(q, cx, cy, z0, L, ang, seed=11 * i + 3)


# ---------------------------------------------------------------------------- MOBILIAS: barricadas e abrigo
@item('barricada_porta', 'Barricada de tábuas para porta', 'mobilias', 'barricadas', montagem='wall',
      comodos=['casas', 'quartel', 'igreja', 'motel', 'abrigo'], vao='porta interna 0,9 × 2,1 m (cobre o batente)', vao_m=[0.9, 2.1, 0.0],
      constroi={'tabua': 6, 'caixa_pregos': 1}, ferramenta='martelo', vida=240,
      estacao='barricada (cada tábua aguenta 40 de dano; a de cima cai primeiro)')
def barricada_porta(M):
    d = math.atan2(1.2, 0.95)
    _barricada(M, 2.18, [(0.0, 0.32, 1.3, 0.025, 0), (0.0, 0.75, 1.28, -0.03, 0), (0.0, 1.18, 1.3, 0.018, 0),
                         (0.0, 1.6, 1.26, -0.022, 0), (0.0, 2.0, 1.3, 0.03, 0), (0.0, 1.05, 1.52, d, 1)])


@item('barricada_janela', 'Barricada de tábuas para janela', 'mobilias', 'barricadas', montagem='wall', altura_sugerida_m=0.78,
      comodos=['casas', 'quartel', 'igreja', 'motel', 'abrigo'], vao='janela 0,9 × 1,45 m (peitoril a 0,85 m)', vao_m=[0.9, 1.45, 0.07],
      constroi={'tabua': 5, 'caixa_pregos': 1}, ferramenta='martelo', vida=200,
      estacao='barricada (deixa frestas para olhar e atirar)')
def barricada_janela(M):
    d = -math.atan2(1.05, 0.9)
    _barricada(M, 1.6, [(0.0, 0.2, 1.26, -0.02, 0), (0.0, 0.58, 1.24, 0.03, 0), (0.0, 0.98, 1.28, -0.015, 0),
                        (0.0, 1.38, 1.24, 0.025, 0), (0.0, 0.8, 1.38, d, 1)])


@item('alarme_latas', 'Alarme de latas', 'mobilias', 'barricadas', montagem='wall', comodos=['casas', 'abrigo', 'quartel'],
      vao='porta 0,9 m', vao_m=[0.9, 2.1, 0.0], constroi={'corda': 1, 'latas vazias': 4}, ferramenta='nenhuma',
      estacao='alarme (zumbi tropeça na linha, as latas batem e acordam o jogador)')
def alarme_latas(M):
    p = M.base; X = 0.48
    for xs in (-1, 1):                                                                       # pregos no batente
        cyl_eixo(p, 'aco', 0.0025, 0.0, 0.035, 'z', (xs * X, 0.18, 0), 8); torno(p, 'aco', [(0.005, 0.034), (0.005, 0.037)], 10, 'z', (xs * X, 0.18, 0))
    varrer(p, 'corda', circ(0.0018, 6), [(-X, 0.18, 0.03), (-0.2, 0.172, 0.03), (0.2, 0.172, 0.03), (X, 0.18, 0.03)])
    cyl_eixo(p, 'aco', 0.0025, 0.0, 0.04, 'z', (X, 0.95, 0), 8); torno(p, 'aco', [(0.005, 0.039), (0.005, 0.042)], 10, 'z', (X, 0.95, 0))
    varrer(p, 'corda', circ(0.0018, 6), [(X, 0.18, 0.034), (X + 0.01, 0.55, 0.036), (X, 0.95, 0.036)])      # linha sobe ao cacho
    for i, (dx, dy, dz) in enumerate(((-0.04, -0.2, 0.05), (0.03, -0.26, 0.06), (-0.01, -0.33, 0.045), (0.05, -0.38, 0.07))):
        c = np.array([X + dx, 0.95 + dy, dz]); top = c + [0, 0.11, 0]
        varrer(p, 'corda', circ(0.0016, 6), [(X, 0.95, 0.038), tuple((np.array([X, 0.95, 0.038]) + top) / 2 + [0, -0.01, 0]), tuple(top)])
        anel(p, 'lata', 0.036, 0.0375, c[1], c[1] + 0.105, 24, 'y', (c[0], 0, c[2]))
        torno(p, 'lata', [(0.0375, c[1]), (0.0375, c[1] + 0.003)], 24, 'y', (c[0], 0, c[2]))
        for y in (0.025, 0.08): anel(p, 'aco_polido', 0.0374, 0.0381, c[1] + y, c[1] + y + 0.004, 24, 'y', (c[0], 0, c[2]))
        p.hull('lata', [(c[0] + 0.03, c[1] + 0.105, c[2] + z) for z in (-0.012, 0.012)] + [(c[0] + 0.05, c[1] + 0.13, c[2] + z) for z in (-0.01, 0.01)] +
               [(c[0] + 0.031, c[1] + 0.104, c[2] + z) for z in (-0.012, 0.012)])                  # tampa dobrada


def _tora(p, a, b, r, mat='casca', topo='madeira_crua'):
    a, b = np.array(a, float), np.array(b, float); d = (b - a) / np.linalg.norm(b - a)
    p.add(mat, trimesh.creation.cylinder(radius=r, segment=[a, b], sections=14))
    for e, s in ((a, -1), (b, 1)):
        p.add(topo, trimesh.creation.cylinder(radius=r * 0.88, segment=[e, e + s * d * 0.003], sections=14))


@item('fogueira', 'Fogueira de pedras', 'mobilias', 'abrigo', comodos=['abrigo', 'rua', 'quartel'], constroi={'lenha': 3, 'pedras': 10},
      estacao='fogueira (cozinhar, ferver água, luz e calor; a luz atrai zumbis à noite)', luz_m=8, ponto_fogo=[0, 0.12, 0], usa='lenha')
def fogueira(M):
    p = M.base; rng = np.random.default_rng(5)
    for i in range(11):
        a = i / 11 * 2 * math.pi + rng.uniform(-0.1, 0.1); r = 0.36 + rng.uniform(-0.02, 0.02)
        s = rng.uniform(0.75, 1.15)
        fofo(p, 'pedra', r * math.cos(a), 0.05 * s, r * math.sin(a), 0.085 * s, 0.06 * s, 0.07 * s, 0.6, 0.55, (10, 14))
    torno(p, 'cinza_fogueira', [(0.3, 0.0), (0.29, 0.012), (0.18, 0.022), (0.0, 0.026)], 28)
    for i in range(5):                                                                        # tenda de toras
        a = i / 5 * 2 * math.pi + 0.3
        _tora(p, (0.24 * math.cos(a), 0.03, 0.24 * math.sin(a)), (0.03 * math.cos(a), 0.42, 0.03 * math.sin(a)), 0.028 + 0.004 * (i % 2))
    for i in range(3):                                                                        # toras queimadas no chao
        a = i * 2.1 + 0.8
        _tora(p, (0.05 * math.cos(a), 0.035, 0.05 * math.sin(a)), (0.25 * math.cos(a + 0.3), 0.03, 0.25 * math.sin(a + 0.3)), 0.025, 'esmalte_escuro', 'brasa')
    for i in range(22):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.0, 0.17)
        p.sphere('brasa' if i % 3 else 'esmalte_escuro', rng.uniform(0.012, 0.022), r * math.cos(a), 0.024, r * math.sin(a), 1)


@item('colchao_chao', 'Colchão no chão', 'mobilias', 'abrigo', deitar=True, comodos=['abrigo', 'casas', 'igreja', 'quartel'],
      estacao='cama improvisada (recupera 70% da energia)', constroi={'colchão de uma cama': 1})
def colchao_chao(M):
    p = M.base
    for i, (x, z, a) in enumerate(((-0.2, -0.45, 0.04), (0.25, 0.5, -0.06), (0.05, 0.1, 0.1))):    # papelão por baixo
        t = P(); t.cham('papelao', -0.45, 0.45, 0.0, 0.006, -0.6, 0.6, 0.002)
        p.merge(t, trimesh.transformations.translation_matrix([x, 0.002 * i, z]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]))
    fofo(p, 'colchao', 0, 0.1, 0, 0.44, 0.08, 0.94, 0.15, 0.12, (12, 32))
    p.uv['colchao'] = uv_caixa(0.5)
    fofo(p, 'cobertor_cinza', 0.04, 0.16, 0.32, 0.47, 0.035, 0.55, 0.35, 0.3, (12, 28), rot_x=0.02)
    fofo(p, 'cobertor_cinza', -0.05, 0.2, -0.05, 0.4, 0.05, 0.12, 0.6, 0.5, (10, 20))                # dobra do cobertor
    fofo(p, 'travesseiro', 0, 0.21, -0.7, 0.3, 0.05, 0.15, 0.35, 0.45, (12, 20), rot_x=-0.1)


# ---------------------------------------------------------------------------- MOBILIAS: contêineres comuns
@item('caixa_papelao', 'Caixa de papelão de mudança', 'mobilias', 'deposito', conteiner=True, saque=['utensilios', 'roupas', 'materiais'],
      slots=4, comodos=['casas', 'deposito', 'correios', 'galeria', 'estacao'], portatil=True, peso_kg=1.5)
def caixa_papelao(M):
    p = M.base; X, H, Z, t = 0.25, 0.36, 0.2, 0.005
    p.box('papelao', -X, X, 0, t, -Z, Z)
    p.box('papelao', -X, X, 0, H, Z - t, Z); p.box('papelao', -X, X, 0, H, -Z, -Z + t)
    p.box('papelao', -X, -X + t, 0, H, -Z + t, Z - t); p.box('papelao', X - t, X, 0, H, -Z + t, Z - t)
    for xs in (-1, 1):                                                                       # alca vazada (borda escura)
        p.box('tinta_preta', xs * X - 0.0005 * xs - 0.0003, xs * X + 0.0008 * xs, H - 0.085, H - 0.055, -0.05, 0.05)
    for x0 in (-0.17, -0.12):                                                                # seta "este lado para cima"
        p.box('tinta_preta', x0, x0 + 0.012, H - 0.15, H - 0.07, Z, Z + 0.0006)
        p.hull('tinta_preta', [(x0 - 0.015, H - 0.07, Z), (x0 + 0.027, H - 0.07, Z), (x0 + 0.006, H - 0.04, Z), (x0 - 0.015, H - 0.07, Z + 0.0006),
                               (x0 + 0.027, H - 0.07, Z + 0.0006), (x0 + 0.006, H - 0.04, Z + 0.0006)])
    p.box('tinta_preta', 0.04, 0.2, H - 0.12, H - 0.105, Z, Z + 0.0006); p.box('tinta_preta', 0.04, 0.16, H - 0.15, H - 0.138, Z, Z + 0.0006)
    p.box('fita_prata', -0.05, 0.05, 0.0, H, Z, Z + 0.0008)
    for nome, o, eixo, ang, caixa in (('aba_esq', (-X, H, 0), 'z', 200, (-X, -0.002, H, H + 0.003, -Z, Z)),        # abas laterais por baixo
                                      ('aba_dir', (X, H, 0), 'z', -200, (0.002, X, H, H + 0.003, -Z, Z)),
                                      ('aba_frente', (0, H + 0.003, Z), 'x', 205, (-X, X, H + 0.003, H + 0.006, 0.001, Z)),
                                      ('aba_tras', (0, H + 0.003, -Z), 'x', -205, (-X, X, H + 0.003, H + 0.006, -Z, -0.001))):
        q = M.parte(nome, o, 'tampa', eixo=eixo, abre_graus=ang)
        q.box('papelao', *caixa)


@item('lixeira', 'Lixeira de rua com rodas', 'mobilias', 'rua', conteiner=True, saque=['comida', 'utensilios', 'materiais'], slots=5,
      barricada=True, comodos=['rua', 'casas', 'diner', 'supermercado', 'padaria'])
def lixeira(M):
    p = M.base; H, Xb, Zb, Xt, Zt = 1.0, 0.25, 0.3, 0.29, 0.36; m = 'plastico_verde'
    def caixa(y0, y1, xa, za, xb, zb, dz=0.0):
        return [(x, y0, z) for x in (-xa, xa) for z in (-za + dz, za + dz)] + [(x, y1, z) for x in (-xb, xb) for z in (-zb, zb)]
    p.hull(m, caixa(0.05, H - 0.2, Xb, Zb, Xb + (Xt - Xb) * 0.8, Zb + (Zt - Zb) * 0.8))
    yr = H - 0.2; xr, zr = Xb + (Xt - Xb) * 0.8, Zb + (Zt - Zb) * 0.8; e = 0.008
    for xs in (-1, 1):
        p.hull(m, [(xs * xr, yr, z) for z in (-zr, zr)] + [(xs * (xr - e), yr, z) for z in (-zr, zr)] +
               [(xs * Xt, H, z) for z in (-Zt, Zt)] + [(xs * (Xt - e), H, z) for z in (-Zt, Zt)])
    for zs in (-1, 1):
        p.hull(m, [(x, yr, zs * zr) for x in (-xr, xr)] + [(x, yr, zs * (zr - e)) for x in (-xr, xr)] +
               [(x, H, zs * Zt) for x in (-Xt, Xt)] + [(x, H, zs * (Zt - e)) for x in (-Xt, Xt)])
    p.cham(m, -Xt - 0.012, Xt + 0.012, H - 0.04, H, Zt - 0.01, Zt + 0.02, 0.006)                 # aba de pegar na frente
    for k, (x, z, s) in enumerate(((-0.1, -0.1, 1.0), (0.12, 0.05, 0.85), (-0.05, 0.18, 0.75))):     # sacos de lixo
        fofo(p, 'saco_lixo', x, yr + 0.04 + 0.03 * k, z, 0.16 * s, 0.12 * s, 0.15 * s, 0.6, 0.7, (12, 16))
        torno(p, 'saco_lixo', [(0.02, 0), (0.012, 0.04), (0.025, 0.06)], 10, 'y', (x, yr + 0.13 + 0.03 * k, z))
    for xs in (-1, 1):                                                                       # rodas atrás
        cyl_eixo(p, 'borracha', 0.1, *sorted((xs * 0.24, xs * 0.3)), 'x', (0, 0.1, -Zb - 0.02), 24)
        cyl_eixo(p, 'plastico_cinza', 0.045, *sorted((xs * 0.3, xs * 0.304)), 'x', (0, 0.1, -Zb - 0.02), 16)
    cyl_eixo(p, 'aco', 0.012, -0.3, 0.3, 'x', (0, 0.1, -Zb - 0.02), 10)
    p.cham(m, -0.2, 0.2, 0.0, 0.06, Zb - 0.08, Zb - 0.02, 0.01)                                # pé da frente
    for x in (-0.12, 0.12): p.cham(m, x - 0.03, x + 0.03, H - 0.06, H, -Zt - 0.06, -Zt, 0.008)  # dobradiças
    cyl_eixo(p, m, 0.018, -Xt + 0.04, Xt - 0.04, 'x', (0, H - 0.06, -Zt - 0.05), 14)            # alça de puxar
    q = M.parte('tampa', (0, H, -Zt), 'tampa', eixo='x', abre_graus=-115)
    q.cham(m, -Xt - 0.015, Xt + 0.015, H, H + 0.035, -Zt - 0.01, Zt + 0.03, 0.01)
    for x in np.linspace(-0.2, 0.2, 5): q.cham(m, x - 0.015, x + 0.015, H + 0.034, H + 0.045, -Zt + 0.05, Zt - 0.05, 0.004)
    q.cham(m, -0.1, 0.1, H + 0.0, H + 0.05, Zt + 0.02, Zt + 0.05, 0.006)


def _ziper(p, X, Z, y0, y1, e=0.012):
    p.box('plastico_preto', -X - 0.002, X + 0.002, y0, y1, Z - e, Z + 0.002); p.box('plastico_preto', -X - 0.002, X + 0.002, y0, y1, -Z - 0.002, -Z + e)
    p.box('plastico_preto', -X - 0.002, -X + e, y0, y1, -Z + e, Z - e); p.box('plastico_preto', X - e, X + 0.002, y0, y1, -Z + e, Z - e)


@item('mala_viagem', 'Mala de viagem', 'mobilias', 'quarto', conteiner=True, saque=['roupas', 'remedios', 'utensilios'], slots=5,
      comodos=['quarto', 'motel', 'estacao', 'casas'], portatil=True, peso_kg=4.0)
def mala_viagem(M):
    p = M.base; X, Z, H, t, m = 0.36, 0.23, 0.12, 0.008, 'mala_azul'
    p.cham(m, -X, X, 0.0, t, -Z, Z, 0.004)
    p.cham(m, -X, X, 0, H, Z - t, Z, 0.004); p.cham(m, -X, X, 0, H, -Z, -Z + t, 0.004)
    p.cham(m, -X, -X + t, 0, H, -Z, Z, 0.004); p.cham(m, X - t, X, 0, H, -Z, Z, 0.004)
    p.box('forro', -X + t, X - t, t, t + 0.002, -Z + t, Z - t)
    for k, (x, c) in enumerate(((-0.17, 'cobertor'), (0.0, 'tecido_sofa'), (0.18, 'lencol'))):        # roupas dobradas
        fofo(p, c, x, t + 0.04, 0.0, 0.085, 0.035 + 0.006 * k, 0.17, 0.3, 0.25, (10, 16))
    _ziper(p, X, Z, H - 0.008, H)
    for xs in (-1, 1): cyl_eixo(p, 'plastico_preto', 0.03, X, X + 0.022, 'x', (0, 0.04, xs * (Z - 0.05)), 18)   # rodinhas
    cyl_eixo(p, 'aco', 0.006, X, X + 0.03, 'x', (0, 0.04, 0), 8)
    for xs in (-1, 1): p.cham('plastico_preto', xs * 0.1 - 0.015, xs * 0.1 + 0.015, 0.04, 0.09, Z, Z + 0.025, 0.005)
    varrer(p, 'plastico_preto', Polygon([(-0.008, -0.012), (0.008, -0.012), (0.008, 0.012), (-0.008, 0.012)]),
           [(-0.1, 0.065, Z + 0.02), (-0.06, 0.065, Z + 0.045), (0.06, 0.065, Z + 0.045), (0.1, 0.065, Z + 0.02)])
    q = M.parte('tampa', (0, H, -Z), 'tampa', eixo='x', abre_graus=-105)
    q.cham(m, -X, X, 2 * H - t, 2 * H, -Z, Z, 0.012)
    q.cham(m, -X, X, H, 2 * H, Z - t, Z, 0.004); q.cham(m, -X, X, H, 2 * H, -Z, -Z + t, 0.004)
    q.cham(m, -X, -X + t, H, 2 * H, -Z, Z, 0.004); q.cham(m, X - t, X, H, 2 * H, -Z, Z, 0.004)
    q.box('forro', -X + t, X - t, 2 * H - t - 0.002, 2 * H - t, -Z + t, Z - t)
    for x in np.linspace(-0.27, 0.27, 6): q.cham(m, x - 0.018, x + 0.018, 2 * H, 2 * H + 0.006, -Z + 0.02, Z - 0.02, 0.003)   # nervuras
    _ziper(q, X, Z, H, H + 0.008)
    q.cham('latao', 0.02, 0.05, H - 0.02, H + 0.02, Z + 0.002, Z + 0.012, 0.003)                     # cursor do zíper


# ---------------------------------------------------------------------------- MOBILIAS: pontos de recurso
@item('pilha_sucata', 'Pilha de sucata', 'mobilias', 'rua', comodos=['rua', 'posto', 'armazem', 'quartel', 'estacao'],
      coleta={'recurso': 'sucata', 'total': 8, 'ferramenta': 'chave_inglesa', 'segundos_por_unidade': 6}, barulho='médio ao desmontar')
def pilha_sucata(M):
    p = M.base; rng = np.random.default_rng(9)
    for i, (x, z, ang, rx) in enumerate(((-0.1, 0.0, 0.3, 0.12), (0.15, -0.1, -0.5, -0.2), (0.0, 0.15, 1.2, 0.35))):   # chapas tortas
        t = P(); W, L = 0.5, 0.8
        xs = np.linspace(-W / 2, W / 2, 25); top = [(x_, 0.008 + 0.008 * math.cos(x_ * 2 * math.pi / 0.076)) for x_ in xs]
        m = trimesh.creation.extrude_polygon(Polygon(top + [(a, b - 0.0015) for a, b in top[::-1]]).buffer(0), L)
        m.vertices = np.stack([m.vertices[:, 2] - L / 2, m.vertices[:, 1], m.vertices[:, 0]], 1)
        if m.volume < 0: m.invert()
        m.vertices[:, 1] += 0.08 * np.maximum(0, m.vertices[:, 0]) ** 2 * 6
        t.add('ferrugem', m)
        T = trimesh.transformations.translation_matrix([x, 0.06 + 0.07 * i, z]) @ trimesh.transformations.rotation_matrix(ang, [0, 1, 0]) @ \
            trimesh.transformations.rotation_matrix(rx, [1, 0, 0])
        p.merge(t, T)
    torno(p, 'borracha', [(0.2, 0.0), (0.3, 0.0), (0.33, 0.04), (0.33, 0.13), (0.3, 0.17), (0.2, 0.17), (0.21, 0.085)], 32, 'y', (0.42, 0, 0.3))  # pneu
    anel(p, 'aco', 0.17, 0.205, 0.04, 0.13, 28, 'y', (0.42, 0, 0.3))
    t = P(); anel(t, 'ferrugem', 0.27, 0.285, -0.42, 0.42, 30, 'y'); torno(t, 'ferrugem', [(0.285, -0.42), (0.285, -0.405)], 30)
    for y in (-0.15, 0.15): anel(t, 'ferrugem', 0.284, 0.295, y - 0.012, y + 0.012, 30, 'y')
    p.merge(t, trimesh.transformations.translation_matrix([-0.45, 0.285, -0.25]) @ trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]) @
            trimesh.transformations.rotation_matrix(0.4, [1, 0, 0]))                           # tambor deitado
    for i in range(5):                                                                        # canos
        a = rng.uniform(0, math.pi); y = 0.12 + 0.05 * i; c = np.array([rng.uniform(-0.3, 0.3), y, rng.uniform(-0.3, 0.3)])
        d = np.array([math.cos(a), rng.uniform(-0.15, 0.15), math.sin(a)]) * rng.uniform(0.35, 0.6)
        mt = 'aco' if i % 2 else 'ferrugem'
        p.add(mt, trimesh.creation.cylinder(radius=0.022, segment=[c - d, c + d], sections=12))
    varrer(p, 'aco', circ(0.002, 6), [(0.3 + 0.1 * math.cos(s), 0.2 + 0.05 * math.sin(3 * s), -0.3 + 0.12 * math.sin(s)) for s in np.linspace(0, 12, 120)])
    for i in range(6):
        p.cham('aco_pintado', *(lambda x, z, s: (x - s, x + s, 0.0, 0.03, z - s * 0.7, z + s * 0.7))(rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(0.04, 0.09)), 0.005)


@item('toco_lenha', 'Toco de rachar lenha', 'mobilias', 'rua', comodos=['rua', 'armazem', 'abrigo', 'casas'],
      estacao='rachar lenha (com machado: 1 tora vira 3 lenhas)', ferramenta='machado')
def toco_lenha(M):
    p = M.base; R, H = 0.24, 0.42
    def aneis(d, w, h):
        d.rectangle([0, 0, w, h], fill=(200, 160, 110)); cx, cy = w * 0.52, h * 0.48
        for r in range(8, int(w * 0.5), 9):
            c = 175 - (r % 27) * 1.6; d.ellipse([cx - r, cy - r * 0.97, cx + r, cy + r * 1.02], outline=(int(c), int(c * 0.78), int(c * 0.52)), width=3)
        for a in (0.4, 2.2, 3.9): d.line([(cx, cy), (cx + math.cos(a) * w * 0.45, cy + math.sin(a) * h * 0.45)], fill=(80, 56, 36), width=4)
        for k in range(14): x = cx + (k * 37) % 160 - 80; y = cy + (k * 53) % 120 - 60; d.line([(x, y), (x + 30, y + 10)], fill=(150, 110, 70), width=3)
    img = Image.new('RGB', (512, 512)); aneis(ImageDraw.Draw(img), 512, 512); mat_imagem('topo_toco', img, 0.8)
    perf = [(R * 1.12, 0.0), (R * 1.04, 0.05), (R, 0.12)] + [(R * (1 + 0.012 * math.sin(i * 1.7)), 0.12 + i * 0.05) for i in range(6)] + [(R * 0.99, H)]
    torno(p, 'casca', perf, 28, fechar=False); p.uv['casca'] = uv_cilindro(0, H)
    torno(p, 'topo_toco', [(R * 0.985, H - 0.002), (R * 0.985, H + 0.002)], 28); p.uv['topo_toco'] = uv_plano(-R, R, -R, R)
    t = P(); _meia_tora(t, 0.3, 0.07)                                                         # lenha em cima do toco
    p.merge(t, trimesh.transformations.translation_matrix([0.0, H + 0.0, 0.02]) @ trimesh.transformations.rotation_matrix(0.25, [0, 1, 0]))
    for x, z, a in ((0.42, 0.1, 1.3), (0.38, -0.12, 1.5), (0.5, 0.0, 1.4), (-0.36, 0.22, -0.3)):        # lenha rachada no chão
        t = P(); _meia_tora(t, 0.3, 0.065)
        p.merge(t, trimesh.transformations.translation_matrix([x, 0.0, z]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]))
    for i in range(12):
        a = i * 0.9; r = 0.3 + (i % 4) * 0.05
        p.cham('madeira_crua', r * math.cos(a) - 0.02, r * math.cos(a) + 0.02, 0.0, 0.004, r * math.sin(a) - 0.006, r * math.sin(a) + 0.006, 0.001)


def _meia_tora(t, L, r):
    """Lenha rachada em quarto de tora, deitada ao longo de x, base em y=0: miolo claro e casca na parte curva."""
    n = 10; arco = [(r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, math.pi / 2, n)]
    def ext(poly, mat):
        m = trimesh.creation.extrude_polygon(poly, L)
        m.vertices = np.stack([m.vertices[:, 2] - L / 2, m.vertices[:, 1], m.vertices[:, 0]], 1)
        if m.volume < 0: m.invert()
        t.add(mat, m)
    # quarto de circulo com o canto vivo para baixo, girado 45 graus para assentar numa face plana
    poly = Polygon([(0, 0)] + arco)
    ext(affinity.translate(poly, -r * 0.35, 0), 'madeira_crua')
    casca = Polygon([(r * math.cos(a), r * math.sin(a)) for a in np.linspace(0, math.pi / 2, n)] +
                    [((r + 0.007) * math.cos(a), (r + 0.007) * math.sin(a)) for a in np.linspace(math.pi / 2, 0, n)])
    ext(affinity.translate(casca, -r * 0.35, 0), 'casca')
    t.uv['madeira_crua'] = uv_caixa(TILE)


# ---------------------------------------------------------------------------- LOOT
@item('lenha', 'Feixe de lenha', 'loot', 'materiais', recurso='madeira', valor=2, peso_kg=4.0, empilha=5,
      onde=['armazem', 'padaria', 'casas', 'quartel', 'abrigo'], efeito='queima 2 h na fogueira ou rende 2 madeira')
def lenha(M):
    p = M.base; L, r = 0.42, 0.065
    for k, (dz, y, rot) in enumerate(((-0.055, 0.0, 0.0), (0.055, 0.0, 0.0), (0.0, 0.055, 0.0))):
        t = P(); _meia_tora(t, L - 0.03 * k, r)
        p.merge(t, trimesh.transformations.translation_matrix([0.01 * k, y, dz]) @ trimesh.transformations.rotation_matrix(0.08 * (k - 1), [0, 1, 0]))
    for x in (-0.12, 0.12):                                                                   # amarração
        anel(p, 'corda', 0.098, 0.105, x - 0.007, x + 0.007, 24, 'x', (0, 0.075, 0))


def _pacote(p, nome, a, b, c, img, crimp_mat, e1=0.25, e2=0.12):
    mat_imagem(nome, img, 0.35)
    fofo(p, nome, 0, b, 0, a, b, c, e1, e2, (14, 28)); p.uv[nome] = uv_atlas(-a, a, 0, 2 * b, -c, c, frente='y')
    for zs in (-1, 1):
        z0, z1 = sorted((zs * (c - 0.006), zs * (c + 0.012)))
        p.cham(crimp_mat, -a + 0.004, a - 0.004, b - 0.003, b + 0.003, z0, z1, 0.001)
        for x in np.linspace(-a + 0.01, a - 0.01, 14): p.box(crimp_mat, x - 0.0015, x + 0.0015, b + 0.003, b + 0.0035, z0, z1)


@item('salgadinho', 'Pacote de salgadinho', 'loot', 'comida', recurso='comida', valor=1, peso_kg=0.1, empilha=8,
      onde=['posto', 'supermercado', 'diner', 'galeria', 'casas'], efeito='fome -10, sede +5 (leve, não estraga)')
def salgadinho(M):
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(220, 120, 20)); d.polygon([(0, h * 0.55), (w, h * 0.35), (w, h), (0, h)], fill=(160, 30, 20))
        texto_c(d, (w / 2, h * 0.22), 'CROCÃO', 52, (255, 240, 120), larg=w - 20); texto_c(d, (w / 2, h * 0.33), 'sabor queijo', 26, (255, 255, 255), False)
        for i in range(9):
            x = 40 + (i * 61) % (w - 80); y = int(h * 0.55) + (i * 43) % int(h * 0.35)
            d.ellipse([x, y, x + 48, y + 30], fill=(244, 190, 70), outline=(190, 110, 30), width=3)
    tras = lambda d, w, h: (d.rectangle([0, 0, w, h], fill=(220, 120, 20)), [d.rectangle([30, 80 + i * 30, w - 30, 90 + i * 30], fill=(255, 230, 190)) for i in range(9)])
    lado = lambda d, w, h: d.rectangle([0, 0, w, h], fill=(160, 30, 20))
    _pacote(M.base, 'rotulo_salgadinho', 0.085, 0.022, 0.12, rotulo_caixa([frente, tras, lado, lado]), 'aco_polido', 0.4, 0.2)


@item('barra_chocolate', 'Barra de chocolate', 'loot', 'comida', recurso='comida', valor=1, peso_kg=0.09, empilha=10,
      onde=['posto', 'supermercado', 'galeria', 'casas', 'escolinha'], efeito='fome -10 e ânimo +5')
def barra_chocolate(M):
    p = M.base; X, Z, H = 0.04, 0.085, 0.011
    def frente(d, w, h):
        d.rectangle([0, 0, w, h], fill=(90, 30, 40)); d.rectangle([0, h * 0.4, w, h * 0.62], fill=(230, 200, 120))
        texto_c(d, (w / 2, h * 0.51), 'TRUFO', 54, (90, 30, 40), larg=w - 20); texto_c(d, (w / 2, h * 0.8), 'ao leite · 90 g', 24, (240, 220, 200), False)
        d.ellipse([w / 2 - 50, h * 0.08, w / 2 + 50, h * 0.33], fill=(140, 70, 40))
    tras = lambda d, w, h: (d.rectangle([0, 0, w, h], fill=(90, 30, 40)), [d.rectangle([30, 60 + i * 34, w - 30, 70 + i * 34], fill=(220, 200, 180)) for i in range(10)])
    lado = lambda d, w, h: d.rectangle([0, 0, w, h], fill=(230, 200, 120))
    mat_imagem('rotulo_chocolate', rotulo_caixa([frente, tras, lado, lado]), 0.4)
    p.cham('rotulo_chocolate', -X, X, 0, H, -Z, Z, 0.002); p.uv['rotulo_chocolate'] = uv_atlas(-X, X, 0, H, -Z, Z, frente='y')
    for zs in (-1, 1):
        z0, z1 = sorted((zs * Z, zs * (Z + 0.012)))
        p.cham('aco_polido', -X + 0.003, X - 0.003, H * 0.4, H * 0.6, z0, z1, 0.0008)


@item('cantil', 'Cantil de alumínio', 'loot', 'agua', recurso='equipamento', valor=1, peso_kg=0.35, empilha=1,
      onde=['quartel', 'casas', 'armazem', 'galeria'], efeito='leva 1 L de água; pode ir ao fogo para ferver', pega=[0, 0.04, 0])
def cantil(M):
    p = M.base
    fofo(p, 'verde_militar', 0, 0.042, 0.0, 0.085, 0.042, 0.11, 0.35, 0.5, (16, 28))
    anel(p, 'verde_militar', 0.016, 0.02, 0.105, 0.135, 20, 'z', (0, 0.042, 0))
    torno(p, 'plastico_preto', [(0.022, 0.13), (0.022, 0.155), (0.016, 0.158)], 20, 'z', (0, 0.042, 0))
    for i in range(10):
        a = i / 10 * 2 * math.pi
        p.box('plastico_preto', 0.0225 * math.cos(a) - 0.0012, 0.0225 * math.cos(a) + 0.0012, 0.042 + 0.0225 * math.sin(a) - 0.0012,
              0.042 + 0.0225 * math.sin(a) + 0.0012, 0.133, 0.153)
    varrer(p, 'aco', circ(0.0012, 6), [(0.02, 0.05, 0.145), (0.045, 0.05, 0.13), (0.06, 0.055, 0.1), (0.07, 0.07, 0.08)])
    anel(p, 'aco_polido', 0.0855, 0.088, -0.006, 0.006, 32, 'z', (0, 0.042, 0))               # costura


@item('saco_dormir', 'Saco de dormir enrolado', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=1.6, empilha=1,
      onde=['casas', 'armazem', 'quartel', 'galeria'], efeito='dormir em qualquer lugar (recupera 85% da energia)')
def saco_dormir(M):
    p = M.base; R, L = 0.11, 0.42
    cyl_eixo(p, 'nylon', R, -L / 2, L / 2, 'x', (0, R, 0), 32)
    for xs in (-1, 1):
        for k, r in enumerate(np.linspace(0.02, R - 0.006, 6)):
            anel(p, 'forro' if k % 2 else 'nylon', r, r + 0.008, xs * (L / 2) - 0.003 + 0.004 * xs, xs * (L / 2) + 0.002 * xs + 0.003, 32, 'x', (0, R + 0.004 * k / 6, 0))
    for x in (-0.12, 0.12):
        anel(p, 'fita_preta', R, R + 0.004, x - 0.012, x + 0.012, 32, 'x', (0, R, 0))
        p.cham('plastico_preto', x - 0.02, x + 0.02, 2 * R, 2 * R + 0.012, -0.012, 0.012, 0.003)
    p.hull('nylon', [(x, y, R) for x in (-L / 2 + 0.01, L / 2 - 0.01) for y in (0.05, 0.13)] + [(x, y, R + 0.012) for x in (-L / 2 + 0.03, L / 2 - 0.03) for y in (0.06, 0.12)])


@item('chave_casa', 'Molho de chaves com etiqueta', 'loot', 'pistas', recurso='chave', valor=1, peso_kg=0.05, empilha=1,
      onde=['casas', 'motel', 'escritorio', 'quartel'], efeito='abre uma porta trancada (a casa escrita na etiqueta)')
def chave_casa(M):
    p = M.base
    anel(p, 'aco_polido', 0.013, 0.0155, 0.0, 0.0025, 32, 'y', (0, 0, 0))
    for k, (ang, mat) in enumerate(((0.35, 'latao'), (-0.5, 'aco_polido'))):
        bl = [(0.022, 0.006), (0.065, 0.006), (0.069, 0.002), (0.069, -0.002)]
        bl += [(x, -0.006 + (0.003 if i % 2 else 0.0)) for i, x in enumerate(np.linspace(0.064, 0.03, 8))] + [(0.022, -0.006)]
        poly = Polygon(bl)
        cabeca = Point(0.012, 0).buffer(0.012, 12).difference(Point(0.004, 0).buffer(0.0035, 8))
        forma = poly.union(cabeca).buffer(0)
        forma = affinity.translate(forma, 0.008, 0); forma = affinity.rotate(forma, math.degrees(ang), origin=(0, 0))
        forma = affinity.translate(forma, 0.012 * math.cos(ang), 0.012 * math.sin(ang))
        extrudar_xz(p, mat, forma, 0.0025 + 0.0022 * k, 0.0047 + 0.0022 * k)
    img = Image.new('RGB', (256, 160), (250, 240, 200)); d = ImageDraw.Draw(img)
    d.rectangle([4, 4, 251, 155], outline=(200, 60, 40), width=6); texto_c(d, (140, 60), 'RUA DAS', 26, (40, 40, 60), False)
    texto_c(d, (140, 105), 'FLORES, 12', 34, (40, 40, 60), larg=200); d.ellipse([16, 66, 40, 90], fill=(120, 110, 90))
    mat_imagem('etiqueta_chave', img, 0.7)
    x0, x1, z0, z1 = -0.075, -0.022, -0.016, 0.018
    p.cham('etiqueta_chave', x0, x1, 0.0, 0.0015, z0, z1, 0.0006); p.uv['etiqueta_chave'] = uv_plano(x0, x1, z0, z1)
    varrer(p, 'corda', circ(0.0008, 5), [(-0.07, 0.0016, 0.0), (-0.04, 0.0018, -0.006), (-0.014, 0.0018, -0.004)])


@item('mapa_cidade', 'Mapa da cidade dobrado', 'loot', 'pistas', recurso='mapa', valor=1, peso_kg=0.08, empilha=1,
      onde=['posto', 'correios', 'estacao', 'casas', 'biblioteca'], efeito='revela os prédios do bairro no mapa do jogo')
def mapa_cidade(M):
    p = M.base; X, Z = 0.075, 0.11
    img = Image.new('RGB', (512, 768), (236, 230, 206)); d = ImageDraw.Draw(img); rng = np.random.default_rng(4)
    d.polygon([(0, 500), (180, 460), (300, 540), (512, 500), (512, 560), (300, 600), (170, 520), (0, 560)], fill=(150, 196, 220))
    for i in range(7):
        y = 40 + i * 100 + rng.integers(-15, 15); d.line([(0, y), (512, y + rng.integers(-20, 20))], fill=(250, 250, 245), width=10 if i % 3 else 18)
    for i in range(5):
        x = 30 + i * 110 + rng.integers(-15, 15); d.line([(x, 0), (x + rng.integers(-30, 30), 768)], fill=(250, 250, 245), width=10 if i % 2 else 16)
    for i in range(26):
        x, y = rng.integers(10, 480), rng.integers(10, 740); d.rectangle([x, y, x + 24, y + 18], fill=(214, 196, 170))
    for x, y in ((150, 140), (360, 330), (90, 650)):
        d.line([(x - 18, y - 18), (x + 18, y + 18)], fill=(190, 20, 20), width=7); d.line([(x - 18, y + 18), (x + 18, y - 18)], fill=(190, 20, 20), width=7)
    d.ellipse([280, 120, 350, 190], outline=(190, 20, 20), width=5)
    d.rectangle([0, 0, 512, 52], fill=(60, 90, 70)); texto_c(d, (256, 26), 'MAPA DA CIDADE', 34, (250, 240, 200))
    for x in (170, 340): d.line([(x, 52), (x, 768)], fill=(200, 192, 170), width=3)
    for y in (256, 512): d.line([(0, y), (512, y)], fill=(200, 192, 170), width=3)
    mat_imagem('mapa_img', img, 0.85)
    for k in range(4):                                                                        # sanfona fechada
        y = k * 0.0018; p.cham('papel' if k < 3 else 'mapa_img', -X, X, y, y + 0.0016, -Z, Z, 0.0005)
    p.uv['mapa_img'] = uv_plano(-X, X, -Z, Z)
    p.hull('papel', [(X, 0.0, z) for z in (-Z, Z)] + [(X + 0.0025, 0.0035, z) for z in (-Z, Z)] + [(X, 0.007, z) for z in (-Z, Z)])
    p.hull('papel', [(-X, 0.0, z) for z in (-Z, Z)] + [(-X - 0.0025, 0.0035, z) for z in (-Z, Z)] + [(-X, 0.007, z) for z in (-Z, Z)])


@item('bilhete', 'Bilhete de sobrevivente', 'loot', 'pistas', recurso='pista', valor=1, peso_kg=0.01, empilha=1,
      onde=['casas', 'igreja', 'posto', 'escolinha', 'supermercado'], efeito='pista do 1º sobrevivente: marca um encontro no mapa (fim da fase 1)')
def bilhete(M):
    p = M.base; X, Z = 0.075, 0.1
    img = Image.new('RGB', (384, 512), (240, 234, 214)); d = ImageDraw.Draw(img)
    for y in range(60, 512, 34): d.line([(10, y), (374, y)], fill=(170, 190, 220), width=2)
    d.line([(40, 0), (40, 512)], fill=(220, 120, 120), width=2)
    f = fonte(26, False)
    for i, l in enumerate(['Se você ler isto:', 'estou na igreja', 'perto da praça.', 'Venha de dia,', 'eles não gostam', 'do sino.', '', '        — Marta']):
        d.text((54 + (i % 2) * 4, 30 + i * 34), l, font=f, fill=(30, 40, 90))
    for k in range(5): x = 300 + k * 7; d.ellipse([x, 420 + k * 3, x + 40, 440 + k * 4], fill=(200, 180, 150))
    mat_imagem('bilhete_img', img, 0.9)
    n = 8; xs = np.linspace(-X, X, n + 1)
    for i in range(n):                                                                        # papel levemente ondulado
        y0 = 0.004 * math.sin((xs[i] + X) / (2 * X) * math.pi) ** 2 * (1 if i < n / 2 else 0.4)
        p.box('bilhete_img', xs[i], xs[i + 1] + 0.0001, y0, y0 + 0.0008, -Z, Z)
    p.uv['bilhete_img'] = uv_plano(-X, X, -Z, Z)
