# Arma 4: carabina de ferrolho .308 (versao de chassi e versao de caca com coronha de madeira) com seus acessorios.
# Executado por gerar_armas.py (plano de lado: x frente, y cima, z direita). Desenho proprio, inspirado nas fotos do Bruno.
CORES.update({'nogueira': (112, 66, 36), 'chassi_tan': (146, 122, 88)})
METAL.update({'chassi_tan': (0.25, 0.55)})

RR = 0.0165                     # raio do receptor (tubo)
KX0, KX1 = -0.07, 0.15          # receptor em x
CB = 0.1                        # curso do ferrolho
LEVANTA = -60                   # giro da alavanca (graus, em volta do cano)
CAR_X, CAR_Y = 0.045, -0.016    # topo do carregador (centro)
CAR_ESP = dict(xm=KX1 + 0.56, bipe=0.44, band=0.40)
CAR_CACA = dict(xm=KX1 + 0.53, bipe=0.38, band=0.35)


def _tex_nogueira(seed, px=1024, tile=0.25):
    """Nogueira envernizada: veio comprido (ao longo de x), poros e variacao de tom."""
    n = int(tile * px); veio = GT.noise(n, n, 0.04 * px, 0.0012 * px, seed); f = GT.fbm(n, n, 0.03 * px, 4, seed + 1)
    poro = GT.smooth(0.9, 1.7, GT.noise(n, n, 0.003 * px, 0.0005 * px, seed + 2))
    c = GT.rgb(CORES['nogueira'])[None, None]
    alb = c * (0.88 + 0.09 * veio[..., None] + 0.05 * f[..., None] - 0.04 * poro[..., None])
    hm = 0.00006 * veio - 0.0001 * poro
    return alb, hm, 0.32 + 0.1 * poro + 0.05 * f, 0.6, 0.0002, tile, px


_materiais_antes_04 = materiais
def materiais():
    _materiais_antes_04()
    alb, hm, rough, nstr, aod, tile, px = _tex_nogueira(501)
    a, nm, o = tex_set(alb, hm, rough, nstr, aod, px)
    TEX['nogueira'] = (a, nm, o); gp.UV_ESCALA['nogueira'] = tile
    MATS['nogueira'] = PBRMaterial(name='nogueira', baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                                   baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)


def _cartucho_308(sec=24, vazio=False):
    """Cartucho .308 deitado em x (base em x = 0): estojo de latao com garganta do extrator, ombro, projetil ponta-fina."""
    q = P()
    est = torno_x([(0.0, 0.0), (0.006, 0.0), (0.006, 0.0012), (0.0051, 0.0016), (0.0051, 0.0022), (0.006, 0.0029), (0.0058, 0.039),
                   (0.0044, 0.0426), (0.0044, 0.0513), (0.0, 0.0513)], sec)
    if vazio: est = menos(est, cil_x(0.0036, 0.004, 0.06, sec=sec), cil_x(0.0052, 0.004, 0.038, sec=sec))
    q.add('latao', est)
    if not vazio:
        q.add('cobre_bala', torno_x([(0.0039, 0.049), (0.0039, 0.0565), (0.0034, 0.0625), (0.0022, 0.0675), (0.0007, 0.0708), (0.0, 0.0711)], sec))
    q.add('aco_inox', torno_x([(0.0, -0.00005), (0.0022, -0.00005), (0.0022, 0.0004)], max(8, sec // 2)))
    return q


def _gatilho_em(q, px, py, mat='aco_oxidado', larg=0.004):
    """Gatilho curvo (ponta para a FRENTE, face da frente concava com estrias) com o pino em (px, py)."""
    d = [(0.0015, -0.001), (-0.0005, -0.0075), (-0.0018, -0.014), (-0.0012, -0.0198), (0.0018, -0.0235)]
    lam = LineString([(px + a, py + b) for a, b in d]).buffer(0.0019, cap_style=1, join_style=1)
    q.add(mat, solido(lam, -larg, larg, 0.0012))
    for i in range(4):
        y = py - 0.01 - i * 0.0022
        q.add(mat, caixa(px - 0.0042, px - 0.0036, y - 0.0003, y + 0.0003, -larg + 0.0002, larg - 0.0002))


def _receptor_308(p, xm, fluted):
    corpo = torno_x([(0.0, KX0), (RR - 0.002, KX0), (RR, KX0 + 0.002), (RR, KX1 - 0.002), (RR - 0.001, KX1)], 64)
    corpo = menos(corpo, caixa(0.03, 0.112, -0.004, 0.03, 0.003, 0.03),                 # janela de ejecao (direita, em cima)
                  caixa(0.0, 0.1, -0.03, -0.01, -0.0115, 0.0115),                         # janela do carregador
                  caixa(-0.062, -0.034, -0.007, 0.007, 0.006, 0.03),                       # entalhe da alavanca
                  cil_x(0.0096, KX0 - 0.01, 0.118, sec=40))                                # caminho do ferrolho
    p.add('aco_oxidado', corpo)
    trilho(p, 'aluminio_preto', KX0 + 0.008, KX1 - 0.004, RR - 0.001, False)
    for x in (KX0 + 0.02, KX1 - 0.02):                                                     # parafusos da base do trilho
        p.add('aco_inox', cil_z(0.0018, -0.0001, 0.0001, x, RR + 0.0045).apply_transform(np.eye(4)))
    p.add('aco_oxidado', solido(arred([(0.13, -0.03), (0.15, -0.03), (0.15, -0.012), (0.13, -0.012)], 0.0015), -0.012, 0.012, 0.001))   # garra de recuo
    p.add('aco_oxidado', solido(arred([(-0.06, -0.006), (-0.03, -0.006), (-0.03, 0.002), (-0.06, 0.002)], 0.001), RR - 0.003, RR + 0.0015, 0.0004))  # trava 3 posicoes
    # cano pesado (estriado na versao de chassi) com rosca na boca
    cano = torno_x([(0.0158, KX1 - 0.002), (0.0158, KX1 + 0.04), (0.0145, KX1 + 0.06), (0.0108, xm - 0.03), (0.0108, xm - 0.016), (0.0085, xm - 0.015)], 56)
    cortes = [cil_x(0.0039, KX1 - 0.01, xm + 0.01, sec=24), cil_x(0.006, KX1 - 0.01, KX1 + 0.052, sec=32)]
    if fluted:
        for i in range(6):
            a = i * math.pi / 3
            g = solido(LineString([(KX1 + 0.1, 0.0), (xm - 0.09, 0.0)]).buffer(0.0028, 16), -0.004, 0.004)
            g.apply_translation([0, 0.0142, 0]); g.apply_transform(TF.rotation_matrix(a, [1, 0, 0]))
            cortes.append(g)
    p.add('aco_oxidado', menos(cano, *cortes))
    rosca_x(p, 'aco_oxidado', 0.0085, xm - 0.015, xm - 0.0005, 0.0012)
    p.add('aco_oxidado', tubo_x(0.0039, 0.0075, xm - 0.0005, xm, sec=32))


def _ferrolho_308(q, caca):
    """Ferrolho: corpo, cabeca com extrator, alavanca para a direita/baixo com bola (caca) ou pomo recartilhado (chassi), capa de tras."""
    q.add('aco_inox', cil_x(0.0092, KX0 + 0.005, 0.117, 0, 0, 40))
    for i in range(3):                                                                    # estrias de alivio do corpo
        a = math.pi / 2 + i * 0.5
        g = caixa(0.0, 0.08, -0.0012, 0.0012, 0.0085, 0.0105); g.apply_transform(TF.rotation_matrix(a, [1, 0, 0])); q.add('aco_oxidado', g)
    q.add('aco_oxidado', solido(arred([(0.1, 0.0035), (0.118, 0.0035), (0.118, 0.0075), (0.1, 0.0075)], 0.0005), 0.0085, 0.0098, 0.0002))   # extrator
    q.add('aco_oxidado', torno_x([(0.0, -0.1), (0.008, -0.1), (0.0118, -0.093), (0.0118, KX0 - 0.0005), (0.0, KX0 - 0.0005)], 40))          # capa
    q.add('tinta_vermelha', tubo_x(0.0, 0.0028, -0.1015, -0.1, sec=16))                                                                    # indicador armado
    dirc = np.array([0.0, -0.45, 0.89]); dirc /= np.linalg.norm(dirc); x = -0.048
    p0 = np.array([x, 0.0, 0.006]); p1 = p0 + dirc * 0.048
    q.add('aco_inox', trimesh.creation.cylinder(radius=0.0036, segment=[p0, p1], sections=20))
    q.add('aco_inox', solido(arred([(x - 0.007, -0.004), (x + 0.007, -0.004), (x + 0.007, 0.004), (x - 0.007, 0.004)], 0.002), 0.006, 0.0112, 0.0006))
    if caca:
        q.add('aco_inox', trimesh.creation.icosphere(3, 0.0085).apply_translation(p1 + dirc * 0.004))
    else:
        k = trimesh.creation.cylinder(radius=0.0095, segment=[p1 - dirc * 0.006, p1 + dirc * 0.016], sections=32); q.add('aluminio_preto', k)
        for i in range(10):
            a = i * 2 * math.pi / 10; e = np.cross(dirc, [1, 0, 0]); e /= np.linalg.norm(e); f2 = np.cross(dirc, e)
            c = p1 + dirc * 0.005 + 0.0095 * (math.cos(a) * e + math.sin(a) * f2)
            q.add('aluminio_preto', trimesh.creation.cylinder(radius=0.0012, segment=[c - dirc * 0.009, c + dirc * 0.009], sections=8))


def _perfil_car308(folga=0.0, baixo=-0.105):
    return Polygon([(CAR_X - 0.039, CAR_Y), (CAR_X + 0.039, CAR_Y), (CAR_X + 0.039, baixo), (CAR_X - 0.039, baixo)]).buffer(folga, join_style=2)


def _carregador_308(q, cap):
    """Carregador de caixa (fila dupla): polimero com nervuras, base removivel, labios de aco e cartucho no topo."""
    baixo = -0.105 if cap > 5 else -0.066
    corpo = solido(arred(list(_perfil_car308(0, baixo).exterior.coords)[:-1], 0.002), -0.011, 0.011, 0.0012)
    q.add('polimero', corpo)
    for y in np.arange(CAR_Y - 0.02, baixo + 0.012, -0.012):                                         # nervuras de pega
        for zs in (-1, 1): q.add('polimero', caixa(CAR_X - 0.035, CAR_X + 0.035, y - 0.0012, y + 0.0012, min(zs * 0.011, zs * 0.0118), max(zs * 0.011, zs * 0.0118)))
    q.add('polimero', solido(arred([(CAR_X - 0.042, baixo - 0.006), (CAR_X + 0.043, baixo - 0.006), (CAR_X + 0.043, baixo + 0.003), (CAR_X - 0.042, baixo + 0.003)], 0.002),
                             -0.0128, 0.0128, 0.0015))
    q.add('tinta_branca', caixa(CAR_X - 0.03, CAR_X - 0.018, baixo - 0.003, baixo, -0.013, -0.0128))      # numero da capacidade
    for zs in (-1, 1): q.add('aco_oxidado', caixa(CAR_X - 0.036, CAR_X + 0.03, CAR_Y - 0.003, CAR_Y + 0.0015, zs * 0.007 - 0.0015, zs * 0.007 + 0.0015))
    q.merge(_cartucho_308(16), TF.translation_matrix([CAR_X - 0.037, CAR_Y - 0.0045, 0.0025]))


def _chassi(p):
    """Chassi de aluminio (cor areia), punho de pistola arredondado, guarda-mao M-LOK e coronha de precisao."""
    pf = arred([(-0.077, 0.0), (0.17, 0.0), (0.17, -0.026), (0.094, -0.03), (0.094, -0.053), (-0.001, -0.053), (-0.004, -0.034), (-0.077, -0.034)], 0.002)
    ch = solido(pf, -0.0175, 0.0175, 0.0018)
    ch = menos(ch, cil_x(RR + 0.0003, KX0 - 0.01, KX1 + 0.03, sec=64), solido(_perfil_car308(0.0008), -0.0118, 0.0118),
               caixa(-0.035, -0.012, -0.05, -0.01, -0.0042, 0.0042),
               *[solido(arred([(x, -0.016), (x + 0.03, -0.016), (x + 0.03, -0.024), (x, -0.024)], 0.003), -0.03, -0.0167) for x in (0.1, 0.135)])
    p.add('chassi_tan', ch)
    fora = arred([(-0.066, -0.032), (-0.003, -0.032), (-0.003, -0.046), (-0.013, -0.064), (-0.05, -0.068), (-0.068, -0.058)], 0.005)
    dentro = arred([(-0.055, -0.0365), (-0.009, -0.0365), (-0.009, -0.047), (-0.017, -0.058), (-0.046, -0.061), (-0.057, -0.052)], 0.004)
    p.add('chassi_tan', solido(fora.difference(dentro), -0.0058, 0.0058, 0.0014))
    p.add('aco_oxidado', solido(arred([(-0.006, -0.05), (0.006, -0.05), (0.006, -0.044), (-0.006, -0.044)], 0.001), -0.004, 0.004, 0.0005))  # retem do carregador
    # punho (o mesmo desenho arredondado e pontilhado da espingarda)
    dx, dy = -0.0645, 0.0095
    cabo = affinity.translate(CABO12, dx, dy); lg = lambda y: LARG12(y - dy)
    p.add('polimero', punho_redondo(cabo, -0.0435 + dy, -0.1555 + dy, lg, n=2.3, fatias=110, voltas=56, raio_base=0.005))
    pont = punho_redondo(cabo, -0.0435 + dy, -0.1555 + dy, lambda y: lg(y) + 0.0004, n=2.3, fatias=110, voltas=56, raio_base=0.005)
    p.add('polimero_grip', inter([pont, solido(cabo.buffer(-0.0026, join_style=1).intersection(sbox(-1, -0.146 + dy, 1, -0.06 + dy)), -0.05, 0.05)]))
    # guarda-mao M-LOK: tubo de secao arredondada com fendas nos lados e embaixo, trilho em cima
    X0, X1 = 0.17, 0.5
    sec_f = arred([(-0.022, -0.031), (0.022, -0.031), (0.022, 0.0195), (-0.022, 0.0195)], 0.009)
    sec_d = sec_f.buffer(-0.0025, join_style=1)
    gm = menos(ext_x(sec_f, X0, X1), ext_x(sec_d, X0 - 0.01, X1 + 0.01))
    fendas = []
    for x in np.arange(X0 + 0.035, X1 - 0.03, 0.042):
        fendas.append(solido(LineString([(x, -0.0055), (x + 0.026, -0.0055)]).buffer(0.0036, 12), -0.03, 0.03))
        fendas.append(ext_y(LineString([(x, 0.0), (x + 0.026, 0.0)]).buffer(0.0036, 12), -0.04, -0.02))
    p.add('chassi_tan', menos(gm, *fendas))
    p.add('chassi_tan', menos(ext_x(sec_f.buffer(0.0006, join_style=1), X1 - 0.008, X1), ext_x(sec_d, X1 - 0.01, X1 + 0.01)))   # anel da ponta
    trilho(p, 'chassi_tan', X0 + 0.004, X1 - 0.004, 0.0195, False)
    p.add('aco_inox', cil_z(0.0045, 0.0218, 0.0232, X1 - 0.03, -0.006, 20))                                             # copo QD
    # coronha de precisao: corpo esqueletado, soleira de borracha, regulagem
    perfil = suave([(-0.072, 0.007), (-0.14, 0.009), (-0.33, 0.011), (-0.346, 0.009), (-0.352, -0.112), (-0.34, -0.121), (-0.3, -0.12),
                    (-0.2, -0.07), (-0.12, -0.046), (-0.077, -0.036)], 3)
    larg = lambda x: 0.0168 + 0.0034 * GT.smooth(-0.1, -0.24, x)
    co = corpo_x(perfil, -0.07, -0.356, larg, n=2.6, fatias=150, voltas=56, raio_tras=0.006, raio_frente=0.002)
    furo = arred([(-0.14, -0.03), (-0.27, -0.028), (-0.292, -0.06), (-0.272, -0.092), (-0.215, -0.072)], 0.008)
    co = menos(co, solido(furo, -0.05, 0.05), cil_z(0.0045, -0.05, 0.05, -0.318, -0.105, 24))
    p.add('chassi_tan', inter([co, caixa(-0.3405, 0.0, -1, 1, -1, 1)]))
    p.add('borracha', inter([co, caixa(-0.4, -0.34, -1, 1, -1, 1)]))
    for zs in (-1, 1): p.add('aluminio_preto', cil_z(0.0062, min(zs * 0.019, zs * 0.0215), max(zs * 0.019, zs * 0.0215), -0.205, 0.0, 24))   # roda do apoio
    p.add('aluminio_preto', cil_x(0.0105, -0.08, -0.071, 0.0, 0, 32))


def _apoio_face(q):
    sec = suave([(-0.15, 0.011), (-0.27, 0.011), (-0.27, 0.023), (-0.26, 0.026), (-0.16, 0.026), (-0.15, 0.022)], 3)
    q.add('chassi_tan', corpo_x(sec, -0.148, -0.272, lambda x: 0.0135, n=3.0, fatias=60, voltas=40, raio_tras=0.003, raio_frente=0.003))
    for x in (-0.175, -0.245): q.add('aco_inox', trimesh.creation.cylinder(radius=0.003, segment=[[x, -0.004, 0], [x, 0.012, 0]], sections=16))


def _coronha_caca(p):
    """Coronha inteirica de nogueira: pente, punho de pistola, quadriculados no punho e na telha, soleira, ponteira escura, pinos de bandoleira."""
    perfil = suave([(0.43, -0.006), (0.15, -0.002), (0.0, -0.002), (-0.075, 0.002), (-0.12, 0.008), (-0.2, 0.012), (-0.33, 0.016), (-0.352, 0.016),
                    (-0.362, -0.112), (-0.352, -0.12), (-0.3, -0.112), (-0.16, -0.084), (-0.095, -0.089), (-0.077, -0.083), (-0.062, -0.06),
                    (-0.05, -0.038), (0.1, -0.038), (0.25, -0.034), (0.4, -0.028), (0.428, -0.022)], 3)
    larg = lambda x: (0.0185 + 0.001 * GT.smooth(0.18, 0.1, x) - 0.0042 * math.exp(-((x + 0.1) / 0.045) ** 2) + 0.0028 * GT.smooth(-0.15, -0.26, x)
                      - 0.002 * GT.smooth(0.3, 0.43, x))
    co = corpo_x(perfil, 0.432, -0.366, larg, n=2.4, fatias=220, voltas=60, raio_tras=0.006, raio_frente=0.006)
    cortes = [cil_x(RR + 0.0004, KX0 - 0.012, KX1 + 0.002, sec=64), cil_x(0.0128, KX1, 0.45, sec=48), solido(_perfil_car308(0.0008), -0.0118, 0.0118),
              caixa(-0.04, -0.01, -0.06, -0.01, -0.006, 0.006), caixa(-0.066, -0.03, -0.03, 0.01, 0.012, 0.04)]
    co = menos(co, *cortes)
    p.add('nogueira', inter([co, caixa(-0.352, 0.41, -1, 1, -1, 1)]))
    p.add('polimero', inter([co, caixa(0.41, 0.5, -1, 1, -1, 1)]))                                                      # ponteira
    p.add('borracha', inter([co, caixa(-0.4, -0.352, -1, 1, -1, 1)]))
    p.add('tinta_branca', inter([co, caixa(-0.3535, -0.352, -1, 1, -1, 1)]).apply_transform(np.eye(4)))                # filete da soleira
    lx = lambda x: larg(x) + 0.0004
    xz = corpo_x(perfil, 0.432, -0.366, lx, n=2.4, fatias=220, voltas=60, raio_tras=0.006, raio_frente=0.006)
    areas = [arred([(-0.056, -0.03), (-0.074, -0.026), (-0.108, -0.072), (-0.092, -0.082), (-0.07, -0.064)], 0.004),
             arred([(0.17, -0.01), (0.31, -0.012), (0.31, -0.03), (0.17, -0.033)], 0.006)]
    for a in areas: p.add('madeira_punho', inter([xz, solido(a, -0.05, 0.05)]))
    # ferragem de baixo: guarda-mato de aco e retem do carregador
    fora = arred([(-0.058, -0.0345), (-0.002, -0.0345), (-0.004, -0.048), (-0.018, -0.063), (-0.05, -0.065), (-0.062, -0.052)], 0.005)
    dentro = arred([(-0.05, -0.0385), (-0.008, -0.0385), (-0.01, -0.048), (-0.02, -0.058), (-0.046, -0.06), (-0.055, -0.05)], 0.004)
    p.add('aco_azulado', solido(fora.difference(dentro), -0.0055, 0.0055, 0.0012))
    p.add('aco_azulado', solido(arred([(-0.07, -0.0395), (0.095, -0.0395), (0.095, -0.035), (-0.07, -0.035)], 0.001), -0.0085, 0.0085, 0.0005))
    for x, y in ((0.38, -0.03), (-0.29, -0.107)):                                                                       # pinos da bandoleira
        p.add('aco_inox', trimesh.creation.cylinder(radius=0.0026, segment=[[x, y + 0.002, 0], [x, y - 0.006, 0]], sections=16))
        p.add('aco_inox', solido(Point(x, y - 0.0105).buffer(0.0062, 32).difference(Point(x, y - 0.0105).buffer(0.0041, 32)), -0.0013, 0.0013, 0.0004))


def _carabina(A, cfg, caca):
    A.pivo = (-0.093, -0.08, 0.0) if not caca else (-0.08, -0.068, 0.0)
    xm = cfg['xm']
    _receptor_308(A.base, xm, not caca)
    if caca: _coronha_caca(A.base)
    else:
        _chassi(A.base)
        ap = A.parte('apoio_face', (0, 0, 0), explodir=(0, 0.05, 0), tipo='desliza', curso_m=0.012, eixo='y', descricao='apoio de rosto: sobe até 12 mm')
        _apoio_face(ap)
    gpx, gpy = (-0.024, -0.033) if not caca else (-0.024, -0.036)
    gat = A.parte('gatilho', (gpx, gpy, 0), explodir=(0.0, -0.06, 0), tipo='gira', eixo='x', curso_graus=-8, descricao='gatilho leve de precisão')
    _gatilho_em(gat, gpx, gpy)
    fer = A.parte('ferrolho', (0, 0, 0), explodir=(-0.15, 0.05, 0), tipo='gira_e_desliza', curso_graus=LEVANTA, curso_m=-CB,
                  descricao=f'levanta a alavanca {abs(LEVANTA)}° e corre {int(CB * 1000)} mm para trás (ejeta), volta e abaixa')
    _ferrolho_308(fer, caca)
    car = A.parte('carregador', (CAR_X, CAR_Y, 0), explodir=(0, -0.08, 0), tipo='remove', direcao=[0.0, -1.0, 0.0], municao='municao_308',
                  capacidade=5 if caca else 10, descricao='carregador de caixa, sai por baixo')
    _carregador_308(car, 5 if caca else 10)
    A.encaixe('encaixe_mira', (0.035, RR + 0.0045, 0), 'trilho_mira', explodir=(0, 0.07, 0),
              aceita=['luneta_3_9', 'luneta_4x', 'mira_ponto_vermelho_tubo'], padrao='luneta_4x' if caca else 'luneta_3_9')
    A.encaixe('encaixe_boca', (xm - 0.015, 0, 0), 'boca_308', explodir=(0.08, 0, 0), aceita=['protetor_rosca_308', 'freio_boca_308', 'supressor_308'],
              padrao='freio_boca_308' if not caca else 'protetor_rosca_308')
    A.encaixe('encaixe_carregador', (CAR_X, CAR_Y, 0), 'carregador_308', pai='carregador', substitui='carregador',
              aceita=['carregador_308_5', 'carregador_308_10'] if caca else ['carregador_308_10', 'carregador_308_5'],
              descricao='filho do nó carregador; ao pôr um carregador aqui, esconda as malhas do nó carregador')
    yb = -0.031 if not caca else -0.031
    A.encaixe('encaixe_bipe', (cfg['bipe'], yb, 0), 'bipe', explodir=(0, -0.06, 0), aceita=['bipe'])
    A.encaixe('encaixe_bandoleira', (cfg['band'], yb - 0.0105, 0), 'bandoleira', explodir=(0, -0.05, 0), aceita=['bandoleira'])
    A.encaixe('boca_fogo', (xm, 0, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('saida_estojo', (0.07, 0.01, RR), 'efeito', descricao='onde nasce o estojo (quando o ferrolho volta, aos 0,6 s do "atirar")')
    fr = lambda ks: ('ferrolho', 'r', (1, 0, 0), pose(ks))
    ft = lambda ks: ('ferrolho', 't', pose([(t, (dx, 0, 0)) for t, dx in ks]))
    coice = [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.02, -8), (0.1, -8), (0.2, 0)])),
             (None, 'r', (0, 0, 1), pose([(0, 0), (0.02, 0), (0.06, 6), (0.3, 0)])),
             (None, 't', pose([(0, (0, 0, 0)), (0.02, (0, 0, 0)), (0.05, (-0.028, 0.004, 0)), (0.3, (0, 0, 0))]))]
    A.anim('atirar', 1.2, coice + [fr([(0, 0), (0.38, 0), (0.48, LEVANTA), (0.88, LEVANTA), (0.98, 0)]),
                                   ft([(0, 0), (0.5, 0), (0.62, -CB), (0.72, -CB), (0.86, 0), (1.2, 0)]),
                                   (None, 'r', (1, 0, 0), pose([(0, 0), (0.35, 0), (0.5, -8), (0.9, -8), (1.1, 0)]))],
           desc='tiro e manejo do ferrolho: levanta (0,48 s), puxa (0,62 s: soltar o estojo), empurra e abaixa (0,98 s)')
    A.anim('atirar_ultimo', 0.8, coice + [fr([(0, 0), (0.38, 0), (0.48, LEVANTA), (0.8, LEVANTA)]), ft([(0, 0), (0.5, 0), (0.62, -CB), (0.8, -CB)])],
           desc='último tiro: o ferrolho fica aberto, atrás')
    A.anim('vazia', 0.1, [fr([(0, LEVANTA), (0.1, LEVANTA)]), ft([(0, -CB), (0.1, -CB)])], laco=True, desc='pose parada: ferrolho aberto')
    dm = (0, -0.2, 0)
    troca = ('carregador', 't', pose([(0, (0, 0, 0)), (0.25, (0, 0, 0)), (0.4, (0, -0.02, 0)), (0.6, dm), (1.3, dm), (1.6, (0, -0.012, 0)), (1.72, (0, 0, 0))]))
    A.anim('recarregar', 2.3, [troca, (None, 'r', (1, 0, 0), pose([(0, 0), (0.25, 20), (1.8, 20), (2.3, 0)])),
                               (None, 'r', (0, 0, 1), pose([(0, 0), (0.25, 6), (1.8, 6), (2.3, 0)]))],
           desc='aperta o retém, carregador sai (0,4 s), novo entra (1,72 s); trocar o nó carregador entre 0,6 e 1,3 s')
    A.anim('recarregar_vazia', 3.0, [troca, fr([(0, LEVANTA), (2.3, LEVANTA), (2.45, 0)]), ft([(0, -CB), (2.0, -CB), (2.2, 0)]),
                                     (None, 'r', (1, 0, 0), pose([(0, 0), (0.25, 20), (1.8, 20), (2.0, -8), (2.5, -8), (3.0, 0)])),
                                     (None, 'r', (0, 0, 1), pose([(0, 0), (0.25, 6), (1.8, 6), (2.6, 0)]))],
           desc='troca o carregador com o ferrolho aberto e fecha o ferrolho (2,2 s) e a alavanca (2,45 s)')
    A.anim('inspecionar', 2.8, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -30), (1.2, -30), (1.6, 35), (2.3, 35), (2.8, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 8), (2.3, 8), (2.8, 0)])),
                                fr([(0, 0), (0.5, 0), (0.6, LEVANTA), (1.1, LEVANTA), (1.2, 0)]), ft([(0, 0), (0.62, 0), (0.75, -0.03), (0.95, -0.03), (1.08, 0)])],
           desc='abre o ferrolho até ver o cartucho na câmara, fecha e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.5), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


DADOS308 = dict(classe='fogo', calibre='.308', municao='municao_308', modo='ferrolho (ação manual)', acao='ferrolho', estojo_s=0.62)


@arma('carabina_308', 'Carabina Paciência .308', 'armas', 'carabina', capacidade=10, dano=95, alcance_m=150, alcance_max_m=600,
      tiros_por_s=0.8, recarga_s=2.3, recarga_vazia_s=3.0, precisao=0.93, recuo=0.6, ruido_m=220, durabilidade=2500, peso_kg=6.2,
      raridade='raro', valor_troca=150, onde=['quartel', 'delegacia'], **DADOS308,
      descricao='Carabina de precisão em chassi de alumínio areia: cano pesado estriado, guarda-mão M-LOK, coronha com apoio de rosto. '
                'Derruba um zumbi a 150 m com um tiro na cabeça, mas o estampido se ouve a 220 m.')
def carabina_308(A): _carabina(A, CAR_ESP, False)


@arma('carabina_308_caca', 'Carabina Paciência .308 de caça', 'armas', 'carabina', capacidade=5, dano=95, alcance_m=120, alcance_max_m=500,
      tiros_por_s=0.8, recarga_s=2.3, recarga_vazia_s=3.0, precisao=0.88, recuo=0.7, ruido_m=220, durabilidade=2500, peso_kg=3.9,
      raridade='incomum', valor_troca=110, onde=['casa_de_campo', 'armazem', 'casas'], **DADOS308,
      descricao='A mesma ação na coronha de nogueira quadriculada, com luneta 4×. Mais leve e fácil de achar em sítios e casas de campo.')
def carabina_308_caca(A): _carabina(A, CAR_CACA, True)


# ---------------------------------------------------------------------------- acessorios da carabina
def _aneis_luneta(q, xs, yc, r):
    """Aneis de luneta com base de trilho (pivo = topo do trilho): garras, parafusos transversais e capas com 4 parafusos."""
    for x in xs:
        q.add('aluminio_preto', solido(arred([(x - 0.009, -0.0058), (x + 0.009, -0.0058), (x + 0.009, 0.004), (x - 0.009, 0.004)], 0.001), -0.0135, 0.0135, 0.0008))
        q.add('aluminio_preto', menos(uniao([cil_x(r + 0.0035, x - 0.0065, x + 0.0065, yc, 0, 48),
                                             caixa(x - 0.0065, x + 0.0065, 0.0, yc, -r * 0.7, r * 0.7)]),
                                      cil_x(r + 0.0001, x - 0.01, x + 0.01, yc, 0, 48), caixa(x - 0.02, x + 0.02, -0.01, 0.0, -0.0106, 0.0106)))
        q.add('aco_oxidado', cil_z(0.0026, -0.016, 0.017, x, -0.0035, 16))
        q.add('aco_oxidado', cil_z(0.004, 0.0135, 0.0165, x, -0.0035, 6))                                  # porca sextavada
        for zs in (-1, 1):
            for dx in (-0.0035, 0.0035): q.add('aco_inox', cil_z(0.0014, min(zs * (r + 0.0025), zs * (r + 0.004)), max(zs * (r + 0.0025), zs * (r + 0.004)), x + dx, yc, 10))


def _luneta(A, L0, L1, r, ro, re, zoom):
    q = A.base; yc = 0.034 if ro > 0.02 else 0.028
    perf = [(0.0, L0), (re - 0.0008, L0), (re, L0 + 0.002), (re, L0 + 0.05), (r + 0.002, L0 + 0.068), (r, L0 + 0.075), (r, L1 - 0.105),
            (ro - 0.002, L1 - 0.06), (ro, L1 - 0.05), (ro, L1 - 0.003), (ro - 0.002, L1), (0.0, L1)]
    corpo = torno_x(perf, 64, yc)
    corpo = menos(corpo, cil_x(re - 0.0035, L0 - 0.01, L0 + 0.006, yc, 0, 48), cil_x(ro - 0.0035, L1 - 0.006, L1 + 0.01, yc, 0, 48))
    q.add('aluminio_preto', corpo)
    q.add('lente', cil_x(re - 0.0034, L0 + 0.005, L0 + 0.0056, yc, 0, 48)); q.add('lente', cil_x(ro - 0.0034, L1 - 0.0056, L1 - 0.005, yc, 0, 48))
    q.add('recartilhado', tubo_x(re - 0.0002, re + 0.0006, L0 + 0.008, L0 + 0.02, yc, sec=56))                       # anel do foco
    if zoom:
        q.add('recartilhado', tubo_x(re - 0.0002, re + 0.0008, L0 + 0.03, L0 + 0.046, yc, sec=56))                    # anel do aumento
        q.add('aluminio_preto', solido(arred([(L0 + 0.034, yc + re), (L0 + 0.042, yc + re), (L0 + 0.041, yc + re + 0.006), (L0 + 0.035, yc + re + 0.006)], 0.001),
                                       -0.002, 0.002, 0.0004))
        for i, k in enumerate(np.linspace(L0 + 0.031, L0 + 0.045, 4)): q.add('tinta_branca', caixa(k - 0.0003, k + 0.0003, yc + re + 0.0002, yc + re + 0.0012, -0.004, -0.0028))
    sela = solido(arred([(-0.025, yc - r - 0.001), (0.025, yc - r - 0.001), (0.025, yc + r + 0.001), (-0.025, yc + r + 0.001)], 0.006), -r - 0.001, r + 0.001, 0.003)
    q.add('aluminio_preto', sela)
    for (lado, rt, h) in (('cima', 0.0105 if zoom else 0.008, 0.016), ('dir', 0.0105 if zoom else 0.008, 0.016), ('esq', 0.0125 if zoom else 0.0, 0.012)):
        if rt == 0: continue
        base = trimesh.creation.cylinder(radius=rt * 0.8, height=h * 0.55, sections=32); topo = trimesh.creation.cylinder(radius=rt, height=h * 0.5, sections=48)
        for m, o in ((base, r + h * 0.27), (topo, r + h * 0.75)):
            if lado == 'cima': m.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0.0, yc + o, 0])
            else: m.apply_translation([0.0, yc, o if lado == 'dir' else -o])
        q.add('aluminio_preto', base); q.add('recartilhado' if zoom else 'aluminio_preto', topo)
        if zoom and lado != 'esq':                                                                 # marcas da torre
            for i in range(12):
                a = i * 2 * math.pi / 12; m = caixa(-0.0003, 0.0003, -0.0012, 0.0, rt - 0.0002, rt + 0.0002)
                if lado == 'cima': m.apply_translation([0, yc + r + h * 0.5, 0]); m.apply_transform(TF.rotation_matrix(a, [0, 1, 0], point=[0, 0, 0]))
                else: m.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0, 0, r + h * 0.5]); m.apply_translation([0, yc, 0])
                q.add('tinta_branca', m)
    q.add('ponto_vermelho', cil_x(0.0006, L0 + 0.0058, L0 + 0.0062, yc, 0, 8))                    # reticulo iluminado (centro)
    _aneis_luneta(q, (-0.05, 0.045) if zoom else (-0.04, 0.035), yc, r)
    A.encaixe('olho', (L0, yc, 0), 'mira', descricao='ocular: linha de visada (afastar o olho uns 9 cm)')
    A.pivo = (0, 0, 0)


@_acessorio('luneta_3_9', 'Luneta 3-9× com retículo iluminado', 'mira', 'trilho_mira', peso_kg=0.62, raridade='raro', valor_troca=90,
            aumento=[3, 9], modificadores={'precisao_mirando': 1.6, 'tempo_mirar': 1.35, 'alcance_m': 1.6}, usa='pilhas', autonomia_min=6000,
            onde=['quartel', 'casa_de_campo'], linha_de_visada='encaixe "olho"; zoom de 3× a 9× (FOV da câmera ÷ aumento)',
            descricao='Luneta de 30 mm com objetiva de 44 mm, anel de aumento com alavanca, torres recartilhadas e ajuste lateral. '
                      'Vê zumbis a 300 m, mas o campo de visão fechado deixa o resto cego.')
def luneta_3_9(A): _luneta(A, -0.175, 0.175, 0.015, 0.0245, 0.0205, True)


@_acessorio('luneta_4x', 'Luneta 4× fixa', 'mira', 'trilho_mira', peso_kg=0.38, raridade='incomum', valor_troca=50, aumento=[4, 4],
            modificadores={'precisao_mirando': 1.45, 'tempo_mirar': 1.2, 'alcance_m': 1.4}, onde=['casa_de_campo', 'armazem', 'casas'],
            linha_de_visada='encaixe "olho"; zoom fixo 4×', descricao='Luneta simples de caça de 1 polegada, com tampas nas torres. Robusta e leve.')
def luneta_4x(A): _luneta(A, -0.14, 0.14, 0.0127, 0.0195, 0.018, False)


@_acessorio('bipe', 'Bipé dobrável', 'bipe', 'bipe', peso_kg=0.36, raridade='incomum', valor_troca=30,
            modificadores={'precisao_deitado': 1.5, 'recuo_deitado': 0.6}, onde=['quartel', 'casa_de_campo'],
            descricao='Bipé de pino de bandoleira com pernas de 3 alturas (nós "perna_esq" e "perna_dir"; animações dobrar/abrir). '
                      'Deitado ou apoiado num muro, a arma quase não mexe.')
def bipe(A):
    q = A.base
    q.add('aco_inox', trimesh.creation.cylinder(radius=0.0028, segment=[[0, 0.001, 0], [0, -0.008, 0]], sections=16))
    q.add('aluminio_preto', solido(arred([(-0.018, -0.008), (0.018, -0.008), (0.016, -0.02), (-0.016, -0.02)], 0.003), -0.012, 0.012, 0.002))
    q.add('aluminio_preto', cil_z(0.0055, -0.026, 0.026, 0.0, -0.016, 24))
    q.add('recartilhado', trimesh.creation.cylinder(radius=0.0065, segment=[[0, -0.02, 0], [0, -0.03, 0]], sections=28))     # trava do giro
    for no, zs in (('perna_esq', -1), ('perna_dir', 1)):
        z = zs * 0.021
        pe = A.parte(no, (0.0, -0.016, z), explodir=(0, -0.03, zs * 0.04), tipo='gira', eixo='z', curso_graus=90, descricao='perna: dobra para a frente')
        pe.add('aluminio_preto', solido(arred([(-0.008, -0.026), (0.008, -0.026), (0.008, -0.009), (-0.008, -0.009)], 0.003), z - 0.005, z + 0.005, 0.0012))
        pe.add('aluminio_preto', trimesh.creation.cylinder(radius=0.0062, segment=[[0, -0.024, z], [0, -0.125, z]], sections=28))
        for k in range(3): pe.add('aco_inox', trimesh.creation.cylinder(radius=0.0052, segment=[[0, -0.13 - k * 0.012, z], [0, -0.135 - k * 0.012, z]], sections=24))
        pe.add('aluminio_preto', trimesh.creation.cylinder(radius=0.0046, segment=[[0, -0.125, z], [0, -0.17, z]], sections=24))
        pe.add('borracha', torno_x([(0.0, -0.014), (0.0062, -0.012), (0.0072, -0.004), (0.006, 0.0), (0.0, 0.0)], 28).apply_transform(
            TF.rotation_matrix(math.pi / 2, [0, 0, 1])).apply_translation([0, -0.17, z]))
        pe.add('mola', trimesh.creation.cylinder(radius=0.0015, segment=[[0.006, -0.02, z], [0.006, -0.06, z]], sections=8))
    A.anim('dobrar', 0.4, [(n, 'r', (0, 0, 1), pose([(0, 0), (0.4, 90)])) for n in ('perna_esq', 'perna_dir')], desc='dobra as pernas para a frente')
    A.anim('abrir', 0.3, [(n, 'r', (0, 0, 1), pose([(0, 90), (0.3, 0)])) for n in ('perna_esq', 'perna_dir')], desc='abre as pernas (mola)')
    A.pivo = (0, 0, 0)


@_acessorio('protetor_rosca_308', 'Protetor de rosca .308', 'boca', 'boca_308', peso_kg=0.02, raridade='comum', modificadores={},
            descricao='Capa que protege a rosca do cano. Vem na versão de caça.')
def protetor_rosca_308(A):
    q = A.base
    q.add('aco_oxidado', menos(torno_x([(0.0108, 0.0), (0.0108, 0.0165), (0.0098, 0.018), (0.0045, 0.018)], 40), cil_x(0.004, -0.01, 0.03), cil_x(0.0086, -0.001, 0.015)))
    q.add('recartilhado', tubo_x(0.0106, 0.0112, 0.003, 0.012, sec=40)); A.pivo = (0, 0, 0)


@_acessorio('freio_boca_308', 'Freio de boca .308', 'boca', 'boca_308', peso_kg=0.11, raridade='incomum', valor_troca=25,
            modificadores={'recuo': 0.55, 'ruido_m': 1.2}, onde=['quartel', 'delegacia'],
            descricao='Três câmaras laterais jogam o gás para os lados: o coice cai pela metade e a mira volta rápido. Mais barulho.')
def freio_boca_308(A):
    q = A.base; R = 0.0118; L = 0.068
    c = torno_x([(0.0, 0.0), (R - 0.001, 0.0), (R, 0.001), (R, L - 0.003), (R - 0.003, L), (0.0, L)], 48)
    cortes = [cil_x(0.0043, -0.01, L + 0.01, sec=24), cil_x(0.0087, -0.001, 0.016, sec=32)]
    for x in (0.022, 0.036, 0.05):
        cortes.append(caixa(x, x + 0.0085, -0.007, 0.007, -0.03, 0.03))
    cortes += [cil_z(0.0018, 0.0, 0.03, x, 0, 12).apply_transform(TF.rotation_matrix(-math.pi / 2, [1, 0, 0])) for x in (0.012, 0.016)]
    q.add('aco_oxidado', menos(c, *cortes))
    q.add('aco_oxidado', tubo_x(0.0087, 0.0128, -0.012, -0.002, sec=6))                      # porca de trava sextavada
    A.pivo = (0, 0, 0)


@_acessorio('supressor_308', 'Supressor de fuzil .308', 'boca', 'boca_308', peso_kg=0.55, raridade='muito raro', valor_troca=120, durabilidade=4000,
            modificadores={'ruido_m': 0.35, 'recuo': 0.8, 'precisao': 1.03}, onde=['quartel'],
            descricao='Tubo de aço com defletores soldados: o estampido cai para 77 m. Esquenta rápido e alonga a arma em 19 cm.')
def supressor_308(A):
    q = A.base; L = 0.19; R = 0.0225
    tubo = torno_x([(0.0, 0.0), (R - 0.004, 0.0), (R, 0.004), (R, L - 0.004), (R - 0.004, L), (0.0, L)], 56)
    q.add('aco_fosfatado', menos(tubo, cil_x(0.0048, -0.01, L + 0.01, sec=24), cil_x(0.0087, -0.001, 0.016, sec=32)))
    q.add('recartilhado', tubo_x(R - 0.0002, R + 0.0006, 0.006, 0.022, sec=56))
    for i in range(7): x = 0.04 + i * 0.019; q.add('aco_oxidado', tubo_x(R - 0.0002, R + 0.00025, x, x + 0.0012, sec=56))
    q.add('aco_oxidado', tubo_x(0.0048, 0.009, L - 0.0002, L + 0.001, sec=32))
    A.pivo = (0, 0, 0)


@_acessorio('carregador_308_10', 'Carregador .308 (10)', 'carregador', 'carregador_308', capacidade=10, municao='municao_308', peso_kg=0.2,
            raridade='incomum', valor_troca=15, modificadores={}, onde=['quartel', 'delegacia'], descricao='Carregador de caixa de 10 tiros.')
def carregador_308_10(A): _carregador_308(A.base, 10); A.pivo = (CAR_X, CAR_Y, 0)


@_acessorio('carregador_308_5', 'Carregador .308 (5)', 'carregador', 'carregador_308', capacidade=5, municao='municao_308', peso_kg=0.13,
            raridade='comum', valor_troca=10, modificadores={}, onde=['casa_de_campo', 'armazem'], descricao='Carregador curto de 5 tiros (quase rente à coronha).')
def carregador_308_5(A): _carregador_308(A.base, 5); A.pivo = (CAR_X, CAR_Y, 0)


@arma('municao_308', 'Cartucho .308', 'municao', 'municao', calibre='.308', peso_kg=0.025, empilha=40, raridade='incomum', estojo='estojo_308',
      onde=['quartel', 'casa_de_campo', 'delegacia'], descricao='Cartucho de fuzil .308 (deitado, pivô no centro).')
def municao_308(A): A.base.merge(_cartucho_308(28), TF.translation_matrix([-0.0355, 0.006, 0])); A.pivo = (0, 0, 0)


@arma('estojo_308', 'Estojo .308 (vazio)', 'municao', 'estojo', calibre='.308', peso_kg=0.012,
      descricao='Estojo ejetado ao puxar o ferrolho. Bom para recarregar na bancada.')
def estojo_308(A): A.base.merge(_cartucho_308(24, vazio=True), TF.translation_matrix([-0.0256, 0, 0])); A.pivo = (0, 0, 0)


CX308 = dict(x0=-0.05, x1=0.05, y0=0.0, y1=0.078, z0=-0.033, z1=0.033)
ATLAS308 = {'topo': (0, 0), 'lado+': (0, 280), 'lado-': (0, 600), 'ponta+': (420, 280), 'ponta-': (420, 600)}


@arma('caixa_municao_308', 'Caixa de munição .308 (20)', 'municao', 'caixa', calibre='.308', municao='municao_308', quantidade=20,
      peso_kg=0.55, empilha=4, raridade='raro', onde=['quartel', 'casa_de_campo', 'delegacia'],
      descricao='Caixa de papelão com bandeja de 20 cartuchos .308 em pé. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_308(A):
    caixa_municao(A, 'rotulo_308', CX308, _arte_caixa(CX308, '.308', '20 CARTUCHOS', 'PONTA FINA 150 gr', cor=(40, 70, 46), atlas=ATLAS308),
                  _cartucho_308(12), 5, 4, 0.0168, 0.0142, faltam=(3,), bandeja=0.05, atlas=ATLAS308)
