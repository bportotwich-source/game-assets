# Arma 5: fuzil semiautomatico/automatico 5,56 com seus acessorios. Executado por gerar_armas.py
# (plano de lado: x frente, y cima, z direita). Desenho proprio, inspirado nas fotos do Bruno; nenhum fuzil comercial copiado.

FX0, FX1 = -0.02, 0.17          # receptor superior em x
FY1 = 0.018                     # topo do receptor (base do trilho)
FW = 0.0128                     # meia largura do receptor superior
MAG_X, MAG_Y = 0.105, -0.016    # topo do carregador (centro)
CF = 0.08                       # curso do transportador do ferrolho
F_XM = FX1 + 0.368              # boca do cano (cano de 368 mm)


def _cartucho_556(sec=20, vazio=False):
    q = P()
    est = torno_x([(0.0, 0.0), (0.0048, 0.0), (0.0048, 0.001), (0.0041, 0.0013), (0.0041, 0.0019), (0.0048, 0.0025), (0.0045, 0.0365),
                   (0.0032, 0.0395), (0.0032, 0.0445), (0.0, 0.0445)], sec)
    if vazio: est = menos(est, cil_x(0.0028, 0.004, 0.05, sec=sec), cil_x(0.0041, 0.004, 0.036, sec=sec))
    q.add('latao', est)
    if not vazio:
        q.add('cobre_bala', torno_x([(0.0028, 0.042), (0.0028, 0.0475), (0.0024, 0.0515), (0.0014, 0.055), (0.0004, 0.057), (0.0, 0.0572)], sec))
    q.add('aco_inox', torno_x([(0.0, -0.00005), (0.0019, -0.00005), (0.0019, 0.0004)], max(8, sec // 2)))
    return q


def _cabo_fuzil(p, dx, dy):
    """Punho de pistola arredondado (mesmo desenho da espingarda), deslocado."""
    cabo = affinity.translate(CABO12, dx, dy); lg = lambda y: LARG12(y - dy)
    p.add('polimero', punho_redondo(cabo, -0.0435 + dy, -0.1555 + dy, lg, n=2.3, fatias=110, voltas=56, raio_base=0.005))
    pont = punho_redondo(cabo, -0.0435 + dy, -0.1555 + dy, lambda y: lg(y) + 0.0004, n=2.3, fatias=110, voltas=56, raio_base=0.005)
    p.add('polimero_grip', inter([pont, solido(cabo.buffer(-0.0026, join_style=1).intersection(sbox(-1, -0.146 + dy, 1, -0.06 + dy)), -0.05, 0.05)]))


def _receptores(p):
    # receptor superior: corpo com assistente do ferrolho, janela de ejecao, protecao do estojo, trilho
    sup = solido(arred([(FX0, -0.012), (FX1, -0.012), (FX1, FY1), (FX0, FY1)], 0.0015), -FW, FW, 0.0014)
    sup = menos(sup, caixa(0.06, 0.122, -0.0085, 0.0085, 0.0, 0.03), cil_x(0.0083, FX0 - 0.01, 0.15, 0.0, 0, 32),
                caixa(FX0 - 0.01, 0.025, 0.006, 0.0135, -0.0045, 0.0045))                       # canal da alavanca de manejo
    p.add('aluminio_receptor', sup)
    p.add('aluminio_receptor', solido(arred([(0.01, -0.004), (0.04, -0.004), (0.045, 0.004), (0.01, 0.006)], 0.002), FW - 0.001, FW + 0.0075, 0.0018))   # assistente
    p.add('aco_inox', cil_x(0.0045, 0.0, 0.012, 0.001, FW + 0.0045, 20))
    p.add('aluminio_receptor', solido(arred([(0.122, -0.0085), (0.13, -0.0085), (0.13, 0.008), (0.122, 0.008)], 0.001), FW - 0.001, FW + 0.004, 0.0006))  # defletor
    trilho(p, 'aluminio_receptor', FX0 + 0.004, FX1, FY1, False)
    # receptor inferior: poco do carregador, guarda-mato, anel da coronha, pinos
    inf = arred([(FX0, -0.0118), (0.15, -0.0118), (0.152, -0.026), (0.14, -0.034), (0.14, -0.052), (0.136, -0.058), (0.072, -0.058),
                 (0.068, -0.048), (0.004, -0.046), (-0.041, -0.0465), (-0.046, -0.042), (-0.036, -0.022), (FX0, -0.0165)], 0.002)
    ib = solido(inf, -0.0118, 0.0118, 0.0016)
    ib = menos(ib, solido(Polygon([(0.0765, -0.012), (0.1335, -0.012), (0.1335, -0.07), (0.0765, -0.07)]), -0.0105, 0.0105),
               caixa(0.028, 0.05, -0.06, -0.03, -0.004, 0.004))
    p.add('aluminio_receptor', ib)
    for zs in (-1, 1): p.add('aluminio_receptor', solido(arred([(0.072, -0.058), (0.138, -0.058), (0.14, -0.052), (0.07, -0.052)], 0.001),
                                                          min(zs * 0.0118, zs * 0.0128), max(zs * 0.0118, zs * 0.0128), 0.0003))   # borda do poco
    fora = arred([(-0.002, -0.044), (0.068, -0.046), (0.068, -0.052), (0.058, -0.066), (0.012, -0.069), (-0.004, -0.058)], 0.005)
    dentro = arred([(0.008, -0.048), (0.06, -0.0495), (0.06, -0.053), (0.052, -0.0615), (0.014, -0.0635), (0.006, -0.056)], 0.004)
    p.add('aluminio_receptor', solido(fora.difference(dentro), -0.0058, 0.0058, 0.0014))
    for (x, y) in ((0.018, -0.03), (0.04, -0.03), (0.14, -0.016), (-0.012, -0.016)):
        for zs in (-1, 1): p.add('aco_inox', cil_z(0.002, min(zs * 0.0117, zs * 0.0125), max(zs * 0.0117, zs * 0.0125), x, y, 16))
    p.add('aluminio_receptor', cil_x(0.0165, FX0 - 0.006, FX0, -0.003, 0, 40))                        # anel da coronha
    _cabo_fuzil(p, -0.004, -0.0015)
    # guarda-mao M-LOK preto com trilho em cima, cano e bloco de gas por dentro
    X0, X1 = FX1 + 0.002, 0.45
    sec_f = arred([(-0.019, -0.03), (0.019, -0.03), (0.019, FY1), (-0.019, FY1)], 0.008)
    sec_d = sec_f.buffer(-0.0022, join_style=1)
    gm = menos(ext_x(sec_f, X0, X1), ext_x(sec_d, X0 - 0.01, X1 + 0.01))
    fendas = []
    for x in np.arange(X0 + 0.03, X1 - 0.03, 0.04):
        fendas.append(solido(LineString([(x, -0.006), (x + 0.024, -0.006)]).buffer(0.0035, 12), -0.03, 0.03))
        fendas.append(ext_y(LineString([(x, 0.0), (x + 0.024, 0.0)]).buffer(0.0035, 12), -0.04, -0.02))
        for zs in (-1, 1):
            g = solido(LineString([(x + 0.003, 0.0), (x + 0.021, 0.0)]).buffer(0.0024, 12), -0.003, 0.003)
            g.apply_transform(TF.rotation_matrix(zs * math.radians(45), [1, 0, 0])); g.apply_translation([0, -0.024, zs * 0.016]); fendas.append(g)
    p.add('aluminio_preto', menos(gm, *fendas))
    trilho(p, 'aluminio_preto', X0 + 0.003, X1 - 0.002, FY1, False)
    p.add('aluminio_preto', menos(ext_x(sec_f.buffer(0.0006, join_style=1), FX1, FX1 + 0.01), cil_x(0.012, FX1 - 0.01, FX1 + 0.02, sec=32)))  # porca do cano
    p.add('aco_oxidado', torno_x([(0.0105, FX1 - 0.002), (0.0105, FX1 + 0.03), (0.0092, FX1 + 0.04), (0.0092, F_XM - 0.015), (0.0075, F_XM - 0.014)], 48))
    rosca_x(p, 'aco_oxidado', 0.0075, F_XM - 0.014, F_XM - 0.0004, 0.001)
    p.add('aco_oxidado', tubo_x(0.0028, 0.0075, F_XM - 0.0004, F_XM, sec=32))
    for zs in (-1, 1): p.add('aco_inox', cil_z(0.0045, min(zs * 0.019, zs * 0.0205), max(zs * 0.019, zs * 0.0205), X1 - 0.025, -0.006, 20))   # copos QD


def _transportador(q):
    q.add('aco_fosfatado', cil_x(0.0081, 0.005, 0.145, 0.0, 0, 32))
    q.add('aco_fosfatado', menos(caixa(0.04, 0.13, -0.006, 0.0068, 0.0, 0.0083), *[caixa(x, x + 0.003, -0.007, 0.007, 0.006, 0.01) for x in np.arange(0.07, 0.12, 0.007)]))
    q.add('aco_inox', cil_x(0.0055, 0.145, 0.152, 0.0, 0, 24))                                    # cabeca do ferrolho
    q.add('aco_oxidado', caixa(0.06, 0.1, 0.0075, 0.0105, -0.0025, 0.0025))                         # chave do gas


def _alavanca(q):
    q.add('aluminio_preto', caixa(FX0 - 0.002, 0.03, 0.0075, 0.0125, -0.004, 0.004))
    t = arred([(FX0 - 0.022, 0.0065), (FX0 - 0.002, 0.0065), (FX0 - 0.002, 0.0135), (FX0 - 0.022, 0.0135)], 0.003)
    q.add('aluminio_preto', solido(t, -0.017, 0.017, 0.0012))
    for zs in (-1, 1): q.add('aluminio_preto', solido(arred([(FX0 - 0.026, 0.007), (FX0 - 0.012, 0.007), (FX0 - 0.012, 0.013), (FX0 - 0.026, 0.013)], 0.002),
                                                      min(zs * 0.012, zs * 0.021), max(zs * 0.012, zs * 0.021), 0.0012))


def _carregador_curvo(q, cap=30):
    """Carregador curvo de polimero: corpo em arco (curva para a frente), nervuras, base e cartucho no topo."""
    R = 0.48; cx, cy = MAG_X + R, MAG_Y; L = 0.18 if cap >= 30 else 0.1; fi = L / R
    th = np.linspace(math.pi, math.pi + fi, 40)
    fr = [(cx + (R - 0.029) * math.cos(t), cy + (R - 0.029) * math.sin(t)) for t in th]
    tr = [(cx + (R + 0.029) * math.cos(t), cy + (R + 0.029) * math.sin(t)) for t in th]
    perfil = Polygon(fr + tr[::-1]).buffer(0)
    q.add('polimero', solido(arred(list(perfil.exterior.coords)[:-1], 0.002), -0.0102, 0.0102, 0.0012))
    for k in np.linspace(0.25, 0.85, 4):                                                          # nervuras
        t = math.pi + fi * k; c, s_ = math.cos(t), math.sin(t)
        pts = [(cx + (R - 0.022) * c, cy + (R - 0.022) * s_), (cx + (R + 0.022) * c, cy + (R + 0.022) * s_)]
        for zs in (-1, 1): q.add('polimero', solido(LineString(pts).buffer(0.0016, cap_style=1), min(zs * 0.0102, zs * 0.0112), max(zs * 0.0102, zs * 0.0112)))
    t = math.pi + fi; c, s_ = math.cos(t), math.sin(t)
    b0 = np.array([cx + R * c, cy + R * s_]); d = np.array([c, s_])
    base = [b0 + d * 0.032 + np.array([-s_, c]) * 0.002, b0 - d * 0.032 + np.array([-s_, c]) * 0.002,
            b0 - d * 0.033 + np.array([s_, -c]) * 0.008, b0 + d * 0.033 + np.array([s_, -c]) * 0.008]
    q.add('polimero', solido(Polygon([tuple(x) for x in base]).buffer(0.0015, join_style=1), -0.0118, 0.0118, 0.0015))
    for zs in (-1, 1): q.add('aco_oxidado', caixa(MAG_X - 0.026, MAG_X + 0.022, MAG_Y - 0.003, MAG_Y + 0.0012, zs * 0.006 - 0.0012, zs * 0.006 + 0.0012))
    q.merge(_cartucho_556(14), TF.translation_matrix([MAG_X - 0.026, MAG_Y - 0.0035, 0.002]))


def _tambor_60(q):
    """Tambor de 60 com o eixo ao longo do cano: torre de alimentacao em cima, corpo redondo com cinta larga, tampa abaulada na frente com disco central e travas."""
    q.add('polimero', solido(arred([(MAG_X - 0.029, MAG_Y), (MAG_X + 0.029, MAG_Y), (MAG_X + 0.03, -0.074), (MAG_X - 0.03, -0.074)], 0.002),
                             -0.0102, 0.0102, 0.0012))                                                  # torre
    for zs in (-1, 1):                                                                             # nervuras da torre
        for x in (MAG_X - 0.012, MAG_X + 0.012):
            q.add('polimero', solido(arred([(x - 0.0016, -0.03), (x + 0.0016, -0.03), (x + 0.0016, -0.07), (x - 0.0016, -0.07)], 0.0008),
                                     min(zs * 0.0102, zs * 0.0112), max(zs * 0.0102, zs * 0.0112)))
    Rd, cyy = 0.05, -0.118; x0, x1 = MAG_X - 0.03, MAG_X + 0.062                                # tambor um pouco a frente da torre
    q.add('polimero', solido(arred([(MAG_X - 0.034, -0.062), (MAG_X + 0.034, -0.062), (MAG_X + 0.036, -0.08), (MAG_X - 0.036, -0.08)], 0.004),
                             -0.019, 0.019, 0.004))                                                    # pescoco que abraca o tambor
    q.add('polimero', torno_x([(0.0, x0), (Rd - 0.004, x0), (Rd - 0.001, x0 + 0.002), (Rd, x0 + 0.005), (Rd, x1 - 0.006),
                               (Rd + 0.002, x1 - 0.004), (Rd + 0.002, x1 - 0.001), (Rd, x1), (0.0, x1)], 72, y=cyy))       # corpo e borda da tampa
    q.add('polimero', tubo_x(Rd - 0.0035, Rd + 0.0006, x0 + 0.03, x0 + 0.05, y=cyy, sec=72, ch=0.0008))   # cinta larga
    q.add('polimero', torno_x([(0.0, x1 + 0.0045), (Rd - 0.016, x1 + 0.0045), (Rd - 0.011, x1 + 0.0025), (Rd - 0.004, x1 + 0.0005), (Rd - 0.003, x1 - 0.0005)],
                              72, y=cyy))                                                                # tampa abaulada
    q.add('polimero', torno_x([(0.0, x1 + 0.0075), (0.024, x1 + 0.0075), (0.0255, x1 + 0.0065), (0.0255, x1 + 0.003)], 64, y=cyy))   # disco central
    q.add('aluminio_preto', tubo_x(0.0256, 0.0264, x1 + 0.0035, x1 + 0.0055, y=cyy, sec=64))
    for k in range(8):                                                                             # travas da tampa na borda
        a = k * math.pi / 4; yy, zz = cyy + (Rd + 0.0012) * math.sin(a), (Rd + 0.0012) * math.cos(a)
        m = caixa(x1 - 0.008, x1 - 0.001, -0.002, 0.002, -0.0018, 0.0018); m.apply_transform(TF.rotation_matrix(a, [1, 0, 0])); m.apply_translation([0, yy, zz])
        q.add('polimero', m)
    q.add('polimero', torno_x([(0.0, x0 - 0.004), (Rd - 0.012, x0 - 0.004), (Rd - 0.006, x0 - 0.002), (Rd - 0.005, x0 + 0.001)], 72, y=cyy))  # fundo
    q.merge(_cartucho_556(14), TF.translation_matrix([MAG_X - 0.026, MAG_Y - 0.0035, 0.002]))


def _carregador_60(q):
    """Carregador longo de 60 (quatro fileiras): topo fino que entra no poco, corpo mais largo embaixo, levemente curvo, de aluminio."""
    R = 0.62; cx, cy = MAG_X + R, MAG_Y; L = 0.25; fi = L / R; k0 = 0.075 / L
    def faixa(ka, kb, meia, n=40):
        th = np.linspace(math.pi + fi * ka, math.pi + fi * kb, n)
        fr = [(cx + (R - meia) * math.cos(t), cy + (R - meia) * math.sin(t)) for t in th]
        tr = [(cx + (R + meia) * math.cos(t), cy + (R + meia) * math.sin(t)) for t in th]
        return Polygon(fr + tr[::-1]).buffer(0)
    topo = faixa(0.0, k0 + 0.03, 0.029, 20)
    q.add('aluminio_preto', solido(arred(list(topo.exterior.coords)[:-1], 0.0015), -0.0102, 0.0102, 0.001))
    corpo = faixa(k0, 1.0, 0.0305, 50)
    q.add('aluminio_preto', solido(arred(list(corpo.exterior.coords)[:-1], 0.004), -0.0175, 0.0175, 0.005))
    for zs in (-1, 1):                                                                             # caneluras ao longo do corpo
        for off in (-0.017, -0.004, 0.009):
            th = np.linspace(math.pi + fi * (k0 + 0.06), math.pi + fi * 0.94, 30)
            pts = [(cx + (R + off) * math.cos(t), cy + (R + off) * math.sin(t)) for t in th]
            q.add('aluminio_preto', solido(LineString(pts).buffer(0.0028, cap_style=1), min(zs * 0.0175, zs * 0.0186), max(zs * 0.0175, zs * 0.0186), 0.0005))
    t = math.pi + fi; c, s_ = math.cos(t), math.sin(t)
    b0 = np.array([cx + R * c, cy + R * s_]); d = np.array([c, s_]); nn = np.array([s_, -c])
    base = [b0 + d * 0.034 - nn * 0.002, b0 - d * 0.034 - nn * 0.002, b0 - d * 0.035 + nn * 0.009, b0 + d * 0.035 + nn * 0.009]
    q.add('polimero', solido(Polygon([tuple(x) for x in base]).buffer(0.002, join_style=1), -0.0195, 0.0195, 0.002))   # base de polimero
    for zs in (-1, 1): q.add('aco_oxidado', caixa(MAG_X - 0.026, MAG_X + 0.022, MAG_Y - 0.003, MAG_Y + 0.0012, zs * 0.006 - 0.0012, zs * 0.006 + 0.0012))
    q.merge(_cartucho_556(14), TF.translation_matrix([MAG_X - 0.026, MAG_Y - 0.0035, 0.002]))


def _seletor(q):
    q.add('aco_oxidado', cil_z(0.004, -0.0128, -0.0118, 0.02, -0.025, 20))
    q.add('aco_oxidado', solido(arred([(0.02, -0.0275), (0.034, -0.0262), (0.034, -0.0238), (0.02, -0.0225)], 0.001), -0.0136, -0.0128, 0.0003))


@arma('fuzil_556', 'Fuzil Vigília 5,56', 'armas', 'fuzil', classe='fogo', calibre='5,56', municao='municao_556', capacidade=30, dano=42,
      alcance_m=80, alcance_max_m=400, modo='semiautomático e automático (seletor)', tiros_por_s=11, recarga_s=2.2, recarga_vazia_s=2.6,
      precisao=0.8, recuo=0.35, ruido_m=160, durabilidade=3000, peso_kg=3.3, raridade='raro', valor_troca=170, onde=['quartel', 'delegacia'],
      estojo_s=0.02, descricao='Fuzil de receptor de alumínio, guarda-mão M-LOK e trilho contínuo em cima. Seletor de tiro automático, '
                               'muitos encaixes. Rajadas gastam munição rápido e chamam a horda a 160 m.')
def fuzil_556(A):
    A.pivo = (-0.037, -0.093, 0.0)
    _receptores(A.base)
    gat = A.parte('gatilho', (0.037, -0.037, 0), explodir=(0.0, -0.06, 0), tipo='gira', eixo='x', curso_graus=-12, descricao='puxa para trás')
    _gatilho_em(gat, 0.037, -0.037)
    sel = A.parte('seletor', (0.02, -0.025, 0), explodir=(0, 0, -0.04), tipo='gira', eixo='z', curso_graus=90, descricao='trava / semi (90°) / auto (180°)')
    _seletor(sel)
    tr = A.parte('ferrolho', (0, 0, 0), explodir=(-0.05, 0.05, 0.04), tipo='desliza', curso_m=-CF, descricao='transportador: recua 80 mm a cada tiro; fica atrás com o carregador vazio')
    _transportador(tr)
    av = A.parte('alavanca', (0, 0, 0), explodir=(-0.06, 0.04, 0), tipo='desliza', curso_m=-0.065, descricao='alavanca de manejo (puxa e solta)')
    _alavanca(av)
    tj = A.parte('tampa_janela', (0.06, -0.0085, FW), explodir=(0, -0.01, 0.04), tipo='gira', eixo='x', curso_graus=100, descricao='abre no primeiro tiro e fica aberta')
    tj.add('aluminio_receptor', menos(caixa(0.0605, 0.1215, -0.0083, 0.0083, FW, FW + 0.0012), *[caixa(x, x + 0.0015, -0.01, 0.01, FW + 0.0008, FW + 0.002) for x in (0.07, 0.11)]))
    tj.add('aco_inox', cil_x(0.0008, 0.06, 0.122, -0.0085, FW, 10))
    rf = A.parte('retem_ferrolho', (0.06, -0.022, -0.0118), explodir=(0, 0, -0.03), tipo='gira', eixo='z', curso_graus=-8, descricao='retém do ferrolho (esquerda)')
    rf.add('aluminio_receptor', solido(arred([(0.052, -0.026), (0.07, -0.028), (0.072, -0.02), (0.056, -0.018)], 0.001), -0.0136, -0.0118, 0.0004))
    car = A.parte('carregador', (MAG_X, MAG_Y, 0), explodir=(0.02, -0.1, 0), tipo='remove', direcao=[0.12, -0.99, 0.0], municao='municao_556', capacidade=30,
                  descricao='carregador curvo de 30')
    _carregador_curvo(car, 30)
    A.encaixe('encaixe_mira', (0.08, FY1 + 0.0055, 0), 'trilho_mira', explodir=(0, 0.07, 0),
              aceita=['mira_holografica', 'mira_ponto_vermelho_tubo', 'luneta_1_6', 'luneta_4x'])
    A.encaixe('encaixe_alca', (FX0 + 0.012, FY1 + 0.0055, 0), 'alca_trilho', explodir=(-0.02, 0.05, 0), aceita=['alca_rebativel'], padrao='alca_rebativel',
              rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira ou luneta no encaixe_mira')
    A.encaixe('encaixe_massa', (0.425, FY1 + 0.0055, 0), 'massa_trilho', explodir=(0.02, 0.05, 0), aceita=['massa_rebativel'], padrao='massa_rebativel',
              rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira ou luneta no encaixe_mira')
    A.encaixe('encaixe_boca', (F_XM - 0.014, 0, 0), 'boca_556', explodir=(0.08, 0, 0), aceita=['quebra_chamas_556', 'compensador_556', 'supressor_556'],
              padrao='quebra_chamas_556')
    A.encaixe('encaixe_carregador', (MAG_X, MAG_Y, 0), 'carregador_556', pai='carregador', substitui='carregador', aceita=['carregador_556_30', 'carregador_556_60', 'tambor_556_60'],
              descricao='filho do nó carregador; ao pôr um carregador aqui, esconda as malhas do nó carregador')
    A.encaixe('encaixe_coronha', (FX0 - 0.006, -0.003, 0), 'coronha_ar', explodir=(-0.08, 0, 0), aceita=['coronha_retratil_ar', 'coronha_fixa_ar'],
              padrao='coronha_retratil_ar')
    A.encaixe('encaixe_empunhadura', (0.3, -0.03, 0), 'mlok_baixo', explodir=(0, -0.06, 0), aceita=['empunhadura_vertical', 'empunhadura_angulada'])
    A.encaixe('encaixe_lanterna', (0.4, -0.006, 0.019), 'mlok_lado', explodir=(0, 0, 0.06), aceita=['lanterna_fuzil'])
    A.encaixe('encaixe_laser', (0.4, -0.006, -0.019), 'mlok_esq', explodir=(0, 0, -0.06), aceita=['laser_fuzil'],
              descricao='lado esquerdo do guarda-mão (a lanterna fica no direito)')
    A.encaixe('encaixe_bipe', (0.43, -0.03, 0), 'bipe', explodir=(0, -0.06, 0), aceita=['bipe'])
    A.encaixe('encaixe_bandoleira', (0.425, -0.006, -0.0205), 'bandoleira', explodir=(0, 0, -0.04), aceita=['bandoleira'])
    A.encaixe('boca_fogo', (F_XM, 0, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('saida_estojo', (0.09, 0.0, FW + 0.002), 'efeito', descricao='onde nasce o estojo (vai para a direita e um pouco para trás)')
    A.encaixe('mira_ferro', (FX0 + 0.012, FY1 + 0.0055 + 0.0195, 0), 'mira', descricao='centro do furo da alça: câmera de 1ª pessoa olha daqui pela ponta da massa (-Z) sem mira acoplada')
    aberta = ('tampa_janela', 'r', (1, 0, 0), pose([(0, 100), (0.1, 100)]))
    A.anim('atirar', 0.09, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.01, -12), (0.05, -12), (0.08, 0)])),
                            ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.008, (0, 0, 0)), (0.035, (-CF, 0, 0)), (0.075, (0, 0, 0))])),
                            ('tampa_janela', 'r', (1, 0, 0), pose([(0, 0), (0.01, 100), (0.09, 100)])),
                            (None, 'r', (0, 0, 1), pose([(0, 0), (0.01, 0), (0.03, 2.5), (0.09, 0)])),
                            (None, 't', pose([(0, (0, 0, 0)), (0.01, (0, 0, 0)), (0.03, (-0.012, 0.002, 0)), (0.09, (0, 0, 0))]))],
           desc='um tiro (repita em rajada a 11 por segundo): transportador recua 80 mm, coice leve; a tampa da janela abre')
    A.anim('atirar_ultimo', 0.1, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.01, -12), (0.05, -12), (0.08, 0)])),
                                  ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.008, (0, 0, 0)), (0.035, (-CF, 0, 0)), (0.06, (-CF + 0.003, 0, 0)), (0.1, (-CF + 0.003, 0, 0))])),
                                  ('retem_ferrolho', 'r', (0, 0, 1), pose([(0, 0), (0.05, -8), (0.1, -8)])),
                                  ('tampa_janela', 'r', (1, 0, 0), pose([(0, 0), (0.01, 100), (0.1, 100)])),
                                  (None, 'r', (0, 0, 1), pose([(0, 0), (0.01, 0), (0.03, 2.5), (0.1, 0)]))], desc='último tiro: o ferrolho fica preso atrás')
    A.anim('vazia', 0.1, [('ferrolho', 't', pose([(0, (-CF + 0.003, 0, 0)), (0.1, (-CF + 0.003, 0, 0))])), aberta,
                          ('retem_ferrolho', 'r', (0, 0, 1), pose([(0, -8), (0.1, -8)]))], laco=True, desc='pose parada: ferrolho atrás')
    dm = (0.02, -0.22, 0)
    troca = ('carregador', 't', pose([(0, (0, 0, 0)), (0.2, (0, 0, 0)), (0.35, (0.002, -0.02, 0)), (0.6, dm), (1.3, dm), (1.6, (0.0, -0.012, 0)), (1.72, (0, 0, 0))]))
    A.anim('recarregar', 2.2, [troca, (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, 18), (1.85, 18), (2.2, 0)])),
                               (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 8), (1.85, 8), (2.2, 0)]))],
           desc='aperta o retém, carregador cai (0,35 s), novo entra (1,72 s); trocar o nó carregador entre 0,6 e 1,3 s')
    A.anim('recarregar_vazia', 2.6, [troca, ('ferrolho', 't', pose([(0, (-CF + 0.003, 0, 0)), (1.95, (-CF + 0.003, 0, 0)), (2.0, (0, 0, 0))])), aberta,
                                     ('retem_ferrolho', 'r', (0, 0, 1), pose([(0, -8), (1.9, -8), (1.95, 0)])),
                                     (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, 18), (1.85, 18), (2.0, 4), (2.6, 0)])),
                                     (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 8), (1.85, 8), (2.6, 0)]))],
           desc='troca o carregador e bate no retém: o ferrolho fecha (2,0 s)')
    A.anim('trocar_modo', 0.5, [('seletor', 'r', (0, 0, 1), pose([(0, 0), (0.12, 90), (0.25, 90), (0.37, 180), (0.5, 180)]))],
           desc='seletor: trava -> semi -> auto (no jogo, pare na posição escolhida)')
    A.anim('inspecionar', 2.8, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -30), (1.2, -30), (1.6, 35), (2.3, 35), (2.8, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 8), (2.3, 8), (2.8, 0)])),
                                ('alavanca', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.65, (-0.03, 0, 0)), (0.95, (-0.03, 0, 0)), (1.05, (0, 0, 0))])),
                                ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.65, (-0.03, 0, 0)), (0.95, (-0.03, 0, 0)), (1.05, (0, 0, 0))])),
                                ('tampa_janela', 'r', (1, 0, 0), pose([(0, 0), (0.55, 0), (0.6, 100), (2.8, 100)]))],
           desc='puxa a alavanca até ver o cartucho na câmara, solta e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.5), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


# ---------------------------------------------------------------------------- acessorios do fuzil
@_acessorio('coronha_retratil_ar', 'Coronha retrátil (fuzil)', 'coronha', 'coronha_ar', peso_kg=0.42, raridade='incomum', valor_troca=20,
            modificadores={'recuo': 0.65, 'precisao': 1.3}, posicoes=5, onde=['quartel', 'delegacia'],
            descricao='Tubo com coronha de polímero de 5 posições (mesma peça da espingarda). Nó "soleira", animações estender/recolher.')
def coronha_retratil_ar(A): coronha_retratil_12(A)


@_acessorio('coronha_fixa_ar', 'Coronha fixa (fuzil)', 'coronha', 'coronha_ar', peso_kg=0.6, raridade='comum', valor_troca=12,
            modificadores={'recuo': 0.6, 'precisao': 1.35}, onde=['quartel'], descricao='Coronha inteiriça de polímero com soleira de borracha.')
def coronha_fixa_ar(A): coronha_fixa_12(A)


@_acessorio('mira_holografica', 'Mira holográfica', 'mira', 'trilho_mira', peso_kg=0.32, raridade='muito raro', valor_troca=80, usa='pilhas',
            autonomia_min=1000, modificadores={'precisao_mirando': 1.35, 'tempo_mirar': 0.7}, onde=['quartel'], linha_de_visada='encaixe "olho"',
            descricao='Janela retangular com retículo de anel e ponto: mira com os dois olhos abertos, a mais rápida para perto.')
def mira_holografica(A):
    q = A.base; yc = 0.026
    q.add('aluminio_preto', solido(arred([(-0.045, -0.0005), (0.045, -0.0005), (0.045, 0.012), (-0.045, 0.012)], 0.003), -0.0135, 0.0135, 0.0015))
    for zs in (-1, 1): q.add('aluminio_preto', caixa(-0.035, 0.035, -0.0058, 0.0, min(zs * 0.0106, zs * 0.0135), max(zs * 0.0106, zs * 0.0135)))
    q.add('aluminio_preto', solido(arred([(-0.045, 0.004), (-0.015, 0.004), (-0.015, 0.016), (-0.045, 0.016)], 0.003), -0.016, 0.016, 0.002))   # caixa das pilhas
    janela = arred([(-0.012, 0.01), (0.032, 0.01), (0.032, 0.046), (-0.012, 0.046)], 0.005)
    capuz = menos(solido(janela, -0.018, 0.018, 0.002), solido(arred([(-0.03, 0.013), (0.05, 0.013), (0.05, 0.0425), (-0.03, 0.0425)], 0.003), -0.015, 0.015))
    q.add('aluminio_preto', capuz)
    q.add('lente_clara', caixa(0.0, 0.0012, 0.013, 0.0425, -0.015, 0.015)); q.add('lente_clara', caixa(0.03, 0.0312, 0.013, 0.0425, -0.015, 0.015))
    for i in range(24):                                                                               # anel do reticulo
        a = i * 2 * math.pi / 24; q.add('ponto_vermelho', caixa(0.0304, 0.0306, yc + 0.0028 + 0.0045 * math.sin(a) - 0.0002, yc + 0.0028 + 0.0045 * math.sin(a) + 0.0002,
                                                                     0.0045 * math.cos(a) - 0.0002, 0.0045 * math.cos(a) + 0.0002))
    q.add('ponto_vermelho', caixa(0.0304, 0.0306, yc + 0.0026, yc + 0.003, -0.0002, 0.0002))
    for x in (-0.042, -0.034, -0.026): q.add('borracha', caixa(x, x + 0.005, 0.0105, 0.0125, -0.006, 0.006))
    q.add('aco_oxidado', cil_z(0.0045, 0.0135, 0.018, 0.02, -0.0035, 6))
    A.encaixe('olho', (-0.012, yc + 0.0028, 0), 'mira', descricao='linha de visada'); A.pivo = (0, 0, 0)


@_acessorio('luneta_1_6', 'Luneta 1-6×', 'mira', 'trilho_mira', peso_kg=0.55, raridade='muito raro', valor_troca=110, aumento=[1, 6],
            modificadores={'precisao_mirando': 1.5, 'tempo_mirar': 1.1, 'alcance_m': 1.5}, usa='pilhas', autonomia_min=6000, onde=['quartel'],
            linha_de_visada='encaixe "olho"; zoom de 1× a 6×', descricao='Luneta curta de aumento variável: em 1× serve para perto, em 6× para longe.')
def luneta_1_6(A): _luneta(A, -0.135, 0.13, 0.015, 0.0178, 0.0205, True)


def _rebativel(A, frente):
    q = A.base; L = 0.024
    q.add('aluminio_preto', solido(arred([(-L / 2, -0.0005), (L / 2, -0.0005), (L / 2, 0.006), (-L / 2, 0.006)], 0.0015), -0.0105, 0.0105, 0.001))
    for zs in (-1, 1): q.add('aluminio_preto', caixa(-L / 2 + 0.002, L / 2 - 0.002, -0.0058, 0.0, min(zs * 0.0106, zs * 0.013), max(zs * 0.0106, zs * 0.013)))
    q.add('aco_oxidado', cil_z(0.002, -0.013, 0.014, 0, -0.003, 12))
    pa = A.parte('lamina', (0.0, 0.006, 0), explodir=(0, 0.03, 0), tipo='gira', eixo='z', curso_graus=-85 if frente else 85, descricao='rebate (animação dobrar)')
    if frente:
        # massa: orelhas de protecao e poste com a ponta na MESMA altura do centro do furo da alca (y = 0,0195): linha de visada reta
        lam = arred([(-0.004, 0.005), (0.004, 0.005), (0.004, 0.0215), (0.003, 0.0235), (-0.003, 0.0235), (-0.004, 0.0215)], 0.0012)
        pa.add('aluminio_preto', menos(solido(lam, -0.009, 0.009, 0.001), solido(arred([(-0.01, 0.0095), (0.01, 0.0095), (0.01, 0.026), (-0.01, 0.026)], 0.002), -0.0065, 0.0065)))
        pa.add('aluminio_preto', caixa(-0.0012, 0.0012, 0.009, 0.0195, -0.0011, 0.0011))
        pa.add('tinta_branca', caixa(-0.0013, 0.0013, 0.0185, 0.0196, -0.0005, 0.0005))
    else:
        # alca: furo de 4,4 mm com o centro em y = 0,0195 e chanfro do lado do olho (o furo parece maior olhando de tras)
        lam = arred([(-0.004, 0.005), (0.004, 0.005), (0.004, 0.024), (-0.004, 0.024)], 0.0012)
        pa.add('aluminio_preto', menos(solido(lam, -0.009, 0.009, 0.001), cil_x(0.0022, -0.01, 0.01, 0.0195, 0, 20),
                                       torno_x([(0.0, -0.0045), (0.0045, -0.0045), (0.0022, -0.0015), (0.0, -0.0015)], 24, 0.0195, 0.0)))
        pa.add('recartilhado', cil_z(0.004, 0.009, 0.013, 0.0, 0.009, 16))
    A.anim('dobrar', 0.25, [('lamina', 'r', (0, 0, 1), pose([(0, 0), (0.25, -85 if frente else 85)]))], desc='rebate a mira')
    A.pivo = (0, 0, 0)


@_acessorio('alca_rebativel', 'Alça de mira rebatível', 'mira', 'alca_trilho', peso_kg=0.04, raridade='comum', modificadores={},
            descricao='Alça de furo (ferro) que rebate para não atrapalhar a luneta. Vem no fuzil.')
def alca_rebativel(A): _rebativel(A, False)


@_acessorio('massa_rebativel', 'Massa de mira rebatível', 'mira', 'massa_trilho', peso_kg=0.03, raridade='comum', modificadores={},
            descricao='Massa de mira com ponta branca, rebatível. Vem no fuzil.')
def massa_rebativel(A): _rebativel(A, True)


def _base_mlok(q, L=0.03):
    q.add('polimero', solido(arred([(-L / 2, -0.004), (L / 2, -0.004), (L / 2, 0.0), (-L / 2, 0.0)], 0.0012), -0.009, 0.009, 0.0008))
    for x in (-L / 4, L / 4): q.add('aco_inox', cil_z(0.0022, -0.0095, -0.0088, x, -0.002, 12).apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0], point=[x, -0.002, -0.009])))


@_acessorio('empunhadura_vertical', 'Empunhadura vertical', 'empunhadura', 'mlok_baixo', peso_kg=0.09, raridade='incomum', valor_troca=15,
            modificadores={'recuo': 0.85, 'precisao_rajada': 1.25}, onde=['quartel', 'delegacia'],
            descricao='Empunhadura arredondada com apoio de dedos, presa por M-LOK: segura o cano nas rajadas. Guarda pilhas na tampa de baixo.')
def empunhadura_vertical(A):
    q = A.base; _base_mlok(q, 0.04)
    cont = suave([(-0.016, -0.004), (0.016, -0.004), (0.015, -0.03), (0.017, -0.045), (0.014, -0.075), (0.016, -0.09), (0.012, -0.096), (-0.012, -0.096),
                  (-0.014, -0.08), (-0.012, -0.05), (-0.015, -0.02)], 3)
    q.add('polimero', punho_redondo(cont, -0.004, -0.096, lambda y: 0.0125 + 0.001 * math.exp(-((y + 0.05) / 0.02) ** 2), n=2.2, fatias=80, voltas=48, raio_base=0.004))
    q.add('polimero_grip', inter([punho_redondo(cont, -0.004, -0.096, lambda y: 0.013 + 0.001 * math.exp(-((y + 0.05) / 0.02) ** 2), n=2.2, fatias=80, voltas=48, raio_base=0.004),
                                  solido(cont.buffer(-0.003).intersection(sbox(-1, -0.085, 1, -0.02)), -0.05, 0.05)]))
    q.add('recartilhado', trimesh.creation.cylinder(radius=0.0095, segment=[[0, -0.0955, 0], [0, -0.099, 0]], sections=32))
    A.pivo = (0, 0, 0)


@_acessorio('empunhadura_angulada', 'Empunhadura angulada', 'empunhadura', 'mlok_baixo', peso_kg=0.06, raridade='incomum', valor_troca=12,
            modificadores={'recuo': 0.9, 'tempo_mirar': 0.9}, onde=['quartel', 'galeria'],
            descricao='Rampa angulada para a palma da mão: a mão vai mais à frente e o fuzil sobe à mira mais rápido.')
def empunhadura_angulada(A):
    q = A.base; _base_mlok(q, 0.07)
    cont = suave([(-0.036, -0.004), (0.036, -0.004), (0.032, -0.012), (0.02, -0.03), (0.008, -0.037), (-0.004, -0.034), (-0.032, -0.012)], 3)
    q.add('polimero', corpo_x(cont, 0.037, -0.037, lambda x: 0.0105 + 0.002 * GT.smooth(-0.02, 0.01, x), n=2.4, fatias=70, voltas=40, raio_tras=0.003, raio_frente=0.003))
    for x in np.arange(-0.02, 0.014, 0.006): q.add('polimero', inter([corpo_x(cont, 0.037, -0.037, lambda x: 0.0115, n=2.4, fatias=70, voltas=40), caixa(x, x + 0.002, -0.05, -0.015, -1, 1)]))
    A.pivo = (0, 0, 0)


@_acessorio('lanterna_fuzil', 'Lanterna de fuzil', 'lanterna', 'mlok_lado', peso_kg=0.16, raridade='incomum', valor_troca=30, usa='pilhas',
            autonomia_min=90, luz={'alcance_m': 60, 'angulo_graus': 16, 'lumens': 1000}, modificadores={}, onde=['quartel', 'delegacia', 'posto'],
            liga_desliga='SpotLight3D no encaixe "feixe" (para -Z)', descricao='Lanterna de 1000 lm presa no lado direito do guarda-mão, com botão de cauda.')
def lanterna_fuzil(A):
    q = A.base; zl = 0.0185
    q.add('polimero', solido(arred([(-0.016, -0.009), (0.016, -0.009), (0.016, 0.009), (-0.016, 0.009)], 0.002), 0.0, 0.006, 0.001))
    q.add('aluminio_preto', solido(arred([(-0.012, -0.007), (0.012, -0.007), (0.012, 0.007), (-0.012, 0.007)], 0.002), 0.005, zl - 0.01, 0.001))
    q.add('aluminio_preto', torno_x([(0.0, -0.06), (0.0105, -0.06), (0.0115, -0.058), (0.0115, 0.008), (0.0145, 0.015), (0.0145, 0.03), (0.0, 0.03)], 40, 0.0, zl))
    for x in np.linspace(-0.05, -0.006, 12): q.add('aluminio_preto', tubo_x(0.0113, 0.0122, x, x + 0.0016, 0.0, zl, sec=40))
    q.add('aco_inox', tubo_x(0.0102, 0.0147, 0.0292, 0.0305, 0.0, zl, sec=40))
    q.add('refletor', torno_x([(0.0035, 0.016), (0.0104, 0.0292)], 32, 0.0, zl)); q.add('led_lanterna', cil_x(0.003, 0.0158, 0.0166, 0.0, zl, 16))
    q.add('lente', cil_x(0.0104, 0.0289, 0.0295, 0.0, zl, 40))
    q.add('borracha', torno_x([(0.0, -0.068), (0.008, -0.068), (0.0098, -0.064), (0.0098, -0.06), (0.0, -0.06)], 32, 0.0, zl))
    A.encaixe('feixe', (0.0305, 0.0, zl), 'efeito', descricao='SpotLight3D aqui (-Z)'); A.pivo = (0, 0, 0)


def _para_lado(A):
    """Acessorio desenhado para cima (garra em y = 0) vira para o lado esquerdo: ganha um trilho curto de M-LOK e gira -90 graus em x
    (o "baixo" do acessorio passa a apontar para +z, contra o guarda-mao)."""
    trilho(A.base, 'aluminio_preto', -0.03, 0.03, -0.0055, False)
    R = TF.rotation_matrix(-math.pi / 2, [1, 0, 0]) @ TF.translation_matrix([0, 0.0055, 0])
    for ms in A.base.parts.values():
        for m in ms: m.apply_transform(R)
    for e in A.encaixes: e['pos'] = list(trimesh.transform_points([e['pos']], R)[0])
    A.pivo = (0, 0, 0)


@_acessorio('laser_fuzil', 'Caixa de laser e luz', 'laser', 'mlok_esq', peso_kg=0.2, raridade='muito raro', valor_troca=70, usa='pilhas',
            autonomia_min=300, luz={'alcance_m': 25, 'angulo_graus': 30, 'lumens': 300}, modificadores={'precisao_sem_mirar': 1.4},
            onde=['quartel'], liga_desliga='laser no encaixe "laser" e luz no encaixe "feixe" (para -Z)',
            descricao='Caixa presa no lado esquerdo do guarda-mão (trilho curto de M-LOK) com laser vermelho e luz auxiliar, chave de 3 posições e tampas das lentes.')
def laser_fuzil(A):
    q = A.base
    q.add('aluminio_preto', caixa(-0.02, 0.02, 0.0, 0.006, -0.0135, 0.0135))
    for zs in (-1, 1): q.add('aluminio_preto', caixa(-0.018, 0.018, -0.0058, 0.0, min(zs * 0.0106, zs * 0.0135), max(zs * 0.0106, zs * 0.0135)))
    q.add('chassi_tan', solido(arred([(-0.045, 0.005), (0.028, 0.005), (0.032, 0.01), (0.032, 0.034), (-0.04, 0.034), (-0.048, 0.026)], 0.004), -0.017, 0.017, 0.003))
    for zc, raio, mat in ((-0.007, 0.0045, 'lente_laser'), (0.007, 0.0065, 'lente')):
        q.add('aluminio_preto', tubo_x(raio, raio + 0.0015, 0.031, 0.036, 0.02, zc, sec=24)); q.add(mat, cil_x(raio, 0.0335, 0.034, 0.02, zc, 24))
    q.add('led_lanterna', cil_x(0.002, 0.0325, 0.0332, 0.02, 0.007, 12))
    q.add('aluminio_preto', cil_z(0.006, 0.017, 0.021, -0.02, 0.022, 24))                                    # chave rotativa
    q.add('borracha', caixa(-0.05, -0.044, 0.012, 0.028, -0.008, 0.008))
    for k in (0.012, 0.026): q.add('recartilhado', cil_z(0.0035, -0.0195, -0.017, k - 0.03, 0.026, 16))       # ajustes do laser
    A.encaixe('laser', (0.036, 0.02, -0.007), 'efeito', descricao='origem do laser (-Z)'); A.encaixe('feixe', (0.036, 0.02, 0.007), 'efeito', descricao='SpotLight3D (-Z)')
    _para_lado(A)


@_acessorio('quebra_chamas_556', 'Quebra-chamas 5,56', 'boca', 'boca_556', peso_kg=0.05, raridade='comum', modificadores={'clarao': 0.4},
            descricao='Gaiola com 5 fendas que esconde o clarão (vem no fuzil): à noite o tiro não denuncia tanto a posição.')
def quebra_chamas_556(A):
    q = A.base; R = 0.0105; L = 0.055
    c = torno_x([(0.0, 0.0), (R - 0.001, 0.0), (R, 0.001), (R, L - 0.002), (R - 0.0015, L), (0.0, L)], 48)
    cortes = [cil_x(0.0058, 0.006, L + 0.01, sec=32), cil_x(0.0028, -0.01, 0.02, sec=20), cil_x(0.0076, -0.001, 0.014, sec=32)]
    for i in range(5):
        g = caixa(0.025, L + 0.01, -0.0014, 0.0014, 0.0, 0.02); g.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 5 + math.pi / 2, [1, 0, 0])); cortes.append(g)
    q.add('aco_oxidado', menos(c, *cortes)); q.add('aco_oxidado', tubo_x(0.0076, 0.011, -0.006, -0.0005, sec=6)); A.pivo = (0, 0, 0)


@_acessorio('compensador_556', 'Compensador 5,56', 'boca', 'boca_556', peso_kg=0.07, raridade='incomum', valor_troca=18,
            modificadores={'recuo': 0.7, 'ruido_m': 1.15}, onde=['quartel'], descricao='Janelas no topo e nos lados seguram o cano nas rajadas.')
def compensador_556(A):
    q = A.base; R = 0.011; L = 0.05
    c = solido(arred([(0, -R), (L, -R), (L, R), (0, R)], 0.003), -R, R, 0.0025)
    cortes = [cil_x(0.0032, -0.01, L + 0.01, sec=20), cil_x(0.0076, -0.001, 0.013, sec=32)]
    for x in (0.02, 0.03, 0.04):
        cortes.append(caixa(x - 0.0025, x + 0.0025, 0.0, 0.02, -0.004, 0.004))
        cortes.append(caixa(x - 0.003, x + 0.003, -0.0045, 0.0045, -0.02, 0.02))
    q.add('aco_oxidado', menos(c, *cortes)); A.pivo = (0, 0, 0)


@_acessorio('supressor_556', 'Supressor 5,56', 'boca', 'boca_556', peso_kg=0.45, raridade='muito raro', valor_troca=110, durabilidade=5000,
            modificadores={'ruido_m': 0.35, 'recuo': 0.85, 'clarao': 0.1}, onde=['quartel'],
            descricao='Supressor de encaixe rápido com garras: o tiro cai para 56 m e quase não aparece clarão.')
def supressor_556(A):
    q = A.base; L = 0.17; R = 0.02
    tubo = torno_x([(0.0, -0.006), (R - 0.003, -0.006), (R, -0.003), (R, L - 0.004), (R - 0.004, L), (0.0, L)], 56)
    q.add('aluminio_preto', menos(tubo, cil_x(0.0034, -0.02, L + 0.01, sec=24), cil_x(0.0115, -0.01, 0.06, sec=40)))
    q.add('recartilhado', tubo_x(R - 0.0002, R + 0.0006, 0.0, 0.016, sec=56))
    for i in range(6): x = 0.035 + i * 0.019; q.add('aco_oxidado', tubo_x(R - 0.0002, R + 0.00025, x, x + 0.001, sec=56))
    q.add('aco_oxidado', solido(arred([(-0.004, R - 0.002), (0.014, R - 0.002), (0.014, R + 0.003), (-0.004, R + 0.003)], 0.001), -0.003, 0.003, 0.0005))   # trava
    A.pivo = (0, 0, 0)


@_acessorio('carregador_556_30', 'Carregador 5,56 (30)', 'carregador', 'carregador_556', capacidade=30, municao='municao_556', peso_kg=0.13,
            raridade='incomum', valor_troca=12, modificadores={}, onde=['quartel', 'delegacia'], descricao='Carregador curvo de polímero, 30 tiros.')
def carregador_556_30(A): _carregador_curvo(A.base, 30); A.pivo = (MAG_X, MAG_Y, 0)


@_acessorio('tambor_556_60', 'Tambor 5,56 (60)', 'carregador', 'carregador_556', capacidade=60, municao='municao_556', peso_kg=0.6,
            raridade='muito raro', valor_troca=60, modificadores={'recarga_s': 1.4, 'tempo_mirar': 1.15}, onde=['quartel'],
            descricao='Tambor de 60 com o eixo ao longo do cano e tampa abaulada na frente: o dobro de tiros, mas pesado e lento para trocar.')
def tambor_556_60(A): _tambor_60(A.base); A.pivo = (MAG_X, MAG_Y, 0)


@_acessorio('carregador_556_60', 'Carregador longo 5,56 (60)', 'carregador', 'carregador_556', capacidade=60, municao='municao_556', peso_kg=0.45,
            raridade='muito raro', valor_troca=50, modificadores={'recarga_s': 1.2, 'tempo_mirar': 1.08}, onde=['quartel'],
            descricao='Carregador longo de alumínio com quatro fileiras: 60 tiros num pente só. Mais leve que o tambor, mas bate no chão quando deitado.')
def carregador_556_60(A): _carregador_60(A.base); A.pivo = (MAG_X, MAG_Y, 0)


@arma('municao_556', 'Cartucho 5,56', 'municao', 'municao', calibre='5,56', peso_kg=0.012, empilha=60, raridade='incomum', estojo='estojo_556',
      onde=['quartel', 'delegacia'], descricao='Cartucho de fuzil 5,56 (deitado, pivô no centro).')
def municao_556(A): A.base.merge(_cartucho_556(24), TF.translation_matrix([-0.0286, 0.0048, 0])); A.pivo = (0, 0, 0)


@arma('estojo_556', 'Estojo 5,56 (vazio)', 'municao', 'estojo', calibre='5,56', peso_kg=0.006, descricao='Estojo ejetado a cada tiro, para a direita.')
def estojo_556(A): A.base.merge(_cartucho_556(20, vazio=True), TF.translation_matrix([-0.0222, 0, 0])); A.pivo = (0, 0, 0)


CX556 = dict(x0=-0.042, x1=0.042, y0=0.0, y1=0.062, z0=-0.027, z1=0.027)
ATLAS556 = {'topo': (0, 0), 'lado+': (0, 230), 'lado-': (0, 490), 'ponta+': (360, 230), 'ponta-': (360, 490)}


@arma('caixa_municao_556', 'Caixa de munição 5,56 (20)', 'municao', 'caixa', calibre='5,56', municao='municao_556', quantidade=20,
      peso_kg=0.27, empilha=6, raridade='raro', onde=['quartel', 'delegacia'],
      descricao='Caixa de papelão com bandeja de 20 cartuchos 5,56 em pé. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_556(A):
    caixa_municao(A, 'rotulo_556', CX556, _arte_caixa(CX556, '5,56', '20 CARTUCHOS', 'PONTA FINA 55 gr', cor=(70, 70, 30), atlas=ATLAS556),
                  _cartucho_556(12), 5, 4, 0.0142, 0.0118, faltam=(6, 13), bandeja=0.04, atlas=ATLAS556)


# ============================================================================ acessorios novos (fotos do Bruno) e versao bicolor
def _recolore(q, mapa):
    """Troca materiais de uma peca (base ou parte): mapa = {material_antigo: material_novo}."""
    novo = {}
    for k, ms in q.parts.items(): novo.setdefault(mapa.get(k, k), []).extend(ms)
    q.parts = novo
    q.uv = {mapa.get(k, k): f for k, f in q.uv.items()}


TAN = {'aluminio_preto': 'chassi_tan', 'polimero': 'polimero_tan', 'polimero_grip': 'polimero_grip_tan'}


def _em_tan(A, mapa=TAN):
    _recolore(A.base, mapa)
    for pt in A.partes: _recolore(pt['peca'], mapa)


def _cil_y(r, y0, y1, x=0.0, z=0.0, sec=32):
    return trimesh.creation.cylinder(radius=r, segment=[[x, y0, z], [x, y1, z]], sections=sec)


def _garra_trilho(q, L=0.044, alavanca=True):
    """Garra de trilho preta (abraca o trilho de 21 mm por baixo do acessorio), com alavanca de trava e parafusos."""
    q.add('aluminio_preto', caixa(-L / 2, L / 2, 0.0, 0.006, -0.0135, 0.0135))
    for zs in (-1, 1): q.add('aluminio_preto', caixa(-L / 2 + 0.002, L / 2 - 0.002, -0.0058, 0.0, min(zs * 0.0106, zs * 0.0135), max(zs * 0.0106, zs * 0.0135)))
    q.add('aco_oxidado', cil_z(0.0022, -0.016, 0.016, 0.0, -0.003, 16))                                     # barra transversal
    for x in (-L / 2 + 0.008, L / 2 - 0.008): q.add('aco_oxidado', cil_z(0.0028, -0.0145, -0.0135, x, 0.002, 6))   # parafusos sextavados
    if alavanca:
        q.add('aluminio_preto', solido(arred([(-0.006, -0.006), (0.006, -0.006), (0.004, 0.004), (0.0015, 0.012), (-0.0015, 0.012), (-0.004, 0.004)], 0.0012),
                                       0.0135, 0.0158, 0.0005))


@_acessorio('modulo_laser', 'Módulo de mira laser', 'laser', 'mlok_esq', peso_kg=0.24, raridade='muito raro', valor_troca=80, usa='pilhas',
            autonomia_min=360, luz={'alcance_m': 20, 'angulo_graus': 28, 'lumens': 250}, modificadores={'precisao_sem_mirar': 1.5},
            onde=['quartel'], liga_desliga='laser no encaixe "laser" e luz no encaixe "feixe" (para -Z)',
            descricao='Caixa caramelo com laser e luz: botão de disparo quadriculado, seletor giratório, tampa da lente presa por cordão e '
                      'tampa de pilha recartilhada atrás. Presa por garra num trilho curto de M-LOK no lado esquerdo do guarda-mão.')
def modulo_laser(A):
    q = A.base; _garra_trilho(q, 0.05)
    corpo = arred([(-0.036, 0.006), (0.034, 0.006), (0.034, 0.044), (0.029, 0.05), (-0.031, 0.05), (-0.036, 0.045)], 0.003)
    q.add('chassi_tan', solido(corpo, -0.017, 0.017, 0.0022))
    for zs in (-1, 1): q.add('chassi_tan', solido(arred([(-0.036, 0.006), (0.034, 0.006), (0.034, 0.011), (-0.036, 0.011)], 0.001),
                                                  min(zs * 0.017, zs * 0.0176), max(zs * 0.017, zs * 0.0176), 0.0003))     # rodape
    # frente: tampa recartilhada da luz e cone do laser com tampa presa
    yl = 0.033
    q.add('chassi_tan', tubo_x(0.0, 0.0105, 0.034, 0.037, yl, -0.0065, sec=48))
    q.add('recartilhado', tubo_x(0.0, 0.0102, 0.037, 0.049, yl, -0.0065, sec=48)); q.add('chassi_tan', tubo_x(0.0, 0.0072, 0.049, 0.0515, yl, -0.0065, sec=40))
    q.add('chassi_tan', torno_x([(0.0, 0.034), (0.0078, 0.034), (0.0078, 0.037), (0.0058, 0.047), (0.0, 0.047)], 40, yl, 0.0085))
    q.add('aluminio_preto', tubo_x(0.0028, 0.0042, 0.0465, 0.0475, yl, 0.0085, sec=24)); q.add('lente_laser', cil_x(0.0028, 0.0462, 0.0468, yl, 0.0085, 20))
    q.add('borracha', solido(LineString([(0.036, yl + 0.011), (0.042, yl + 0.0175), (0.048, yl + 0.016), (0.05, yl + 0.0105)]).buffer(0.0012, cap_style=1), -0.002, 0.004))   # cordao
    # tras: tampa da pilha recartilhada (cone) e botao do ajuste de altura em cima
    q.add('recartilhado', torno_x([(0.0, -0.036), (0.0085, -0.036), (0.0085, -0.039), (0.0068, -0.05), (0.0, -0.05)], 40, 0.02, 0.0))
    q.add('chassi_tan', tubo_x(0.0, 0.0062, -0.052, -0.05, 0.02, 0.0, sec=32))
    q.add('recartilhado', _cil_y(0.0075, 0.05, 0.056, -0.015, 0.0, 40)); q.add('chassi_tan', _cil_y(0.0058, 0.056, 0.058, -0.015, 0.0, 32))
    q.add('aco_oxidado', caixa(-0.0185, -0.0115, 0.0575, 0.0588, -0.0007, 0.0007))                         # fenda do ajuste
    # lado esquerdo: botao de disparo quadriculado e seletor giratorio
    q.add('chassi_tan', solido(arred([(-0.028, 0.012), (-0.01, 0.012), (-0.01, 0.03), (-0.028, 0.03)], 0.003), -0.0185, -0.017, 0.0005))
    q.add('borracha', solido(arred([(-0.0265, 0.0135), (-0.0115, 0.0135), (-0.0115, 0.0285), (-0.0265, 0.0285)], 0.002), -0.0195, -0.0183, 0.0004))
    for i in range(4):
        for j in range(4):
            m = trimesh.creation.icosphere(1, radius=0.0011); m.apply_scale([1, 1, 0.6]); m.apply_translation([-0.0245 + i * 0.0037, 0.0155 + j * 0.0037, -0.0195]); q.add('borracha', m)
    q.add('chassi_tan', cil_z(0.0085, -0.0188, -0.017, 0.016, 0.021, 40))
    q.add('aluminio_preto', menos(cil_z(0.0065, -0.0212, -0.0185, 0.016, 0.021, 40),
                                  caixa(0.009, 0.023, 0.0205, 0.0215, -0.023, -0.0205).apply_transform(TF.rotation_matrix(math.radians(-40), [0, 0, 1], point=[0.016, 0.021, 0]))))
    for ang in (150, 30):                                                                           # setas L / R gravadas
        a = math.radians(ang); q.add('aco_oxidado', caixa(-0.0006, 0.0006, -0.0018, 0.0018, -0.0001, 0.0001)
                                    .apply_transform(TF.rotation_matrix(a, [0, 0, 1])).apply_translation([0.016 + 0.011 * math.cos(a), 0.021 - 0.011 * math.sin(a) - 0.002, -0.0171]))
    q.add('chassi_tan', cil_z(0.0032, -0.0182, -0.017, 0.027, 0.043, 24))                                # parafuso de canto
    # lado direito: placa de aviso
    q.add('plastico_branco', caixa(-0.024, 0.012, 0.016, 0.042, 0.0172, 0.0176))
    q.add('tinta_vermelha', caixa(-0.021, 0.009, 0.036, 0.039, 0.0176, 0.0178))
    A.encaixe('laser', (0.0475, yl, 0.0085), 'efeito', descricao='origem do laser (-Z)')
    A.encaixe('feixe', (0.0515, yl, -0.0065), 'efeito', descricao='SpotLight3D (-Z)')
    _para_lado(A)


@_acessorio('lanterna_compacta', 'Lanterna compacta de trilho', 'lanterna', 'mlok_lado', peso_kg=0.11, raridade='incomum', valor_troca=24, usa='pilhas',
            autonomia_min=60, luz={'alcance_m': 45, 'angulo_graus': 20, 'lumens': 600}, modificadores={}, onde=['quartel', 'delegacia', 'posto'],
            liga_desliga='SpotLight3D no encaixe "feixe" (para -Z)',
            descricao='Lanterna curta com garra de trilho, corpo recartilhado e coroa dentada na frente (serve para quebrar vidro).')
def lanterna_compacta(A):
    q = A.base; zl = 0.02
    q.add('aluminio_preto', solido(arred([(-0.014, -0.008), (0.014, -0.008), (0.014, 0.008), (-0.014, 0.008)], 0.002), 0.0, 0.005, 0.001))
    q.add('aluminio_preto', solido(arred([(-0.012, -0.0065), (0.012, -0.0065), (0.012, 0.0065), (-0.012, 0.0065)], 0.002), 0.004, zl - 0.009, 0.001))
    for x in (-0.007, 0.007): q.add('aco_oxidado', cil_x(0.0016, x - 0.0015, x + 0.0015, 0.0075, 0.0045, 6))
    q.add('aluminio_preto', torno_x([(0.0, -0.038), (0.0095, -0.038), (0.0105, -0.036), (0.0105, 0.004), (0.0128, 0.01), (0.0128, 0.024), (0.0, 0.024)], 40, 0.0, zl))
    q.add('recartilhado', tubo_x(0.0, 0.0108, -0.03, -0.004, 0.0, zl, sec=40))
    coroa = tubo_x(0.0098, 0.0132, 0.024, 0.031, 0.0, zl, sec=48)
    for i in range(6):
        g = caixa(0.027, 0.034, -0.0025, 0.0025, 0.0, 0.02); g.apply_transform(TF.rotation_matrix(i * math.pi / 3, [1, 0, 0])); g.apply_translation([0, 0, zl]); coroa = menos(coroa, g)
    q.add('aluminio_preto', coroa)
    q.add('refletor', torno_x([(0.0032, 0.013), (0.0096, 0.0238)], 32, 0.0, zl)); q.add('led_lanterna', cil_x(0.0028, 0.0128, 0.0135, 0.0, zl, 16))
    q.add('lente', cil_x(0.0097, 0.0236, 0.0242, 0.0, zl, 40))
    q.add('borracha', torno_x([(0.0, -0.045), (0.0068, -0.045), (0.0085, -0.042), (0.0085, -0.038), (0.0, -0.038)], 32, 0.0, zl))
    A.encaixe('feixe', (0.031, 0.0, zl), 'efeito', descricao='SpotLight3D aqui (-Z)'); A.pivo = (0, 0, 0)


@_acessorio('empunhadura_curta', 'Empunhadura curta inclinada', 'empunhadura', 'mlok_baixo', peso_kg=0.05, raridade='incomum', valor_troca=12,
            modificadores={'recuo': 0.9, 'tempo_mirar': 0.92}, onde=['quartel', 'galeria'],
            descricao='Empunhadura baixa inclinada para a frente, com nervuras para os dedos: segura firme sem pesar.')
def empunhadura_curta(A):
    q = A.base; _base_mlok(q, 0.05)
    cont = suave([(-0.026, -0.004), (0.03, -0.004), (0.026, -0.012), (0.016, -0.036), (0.008, -0.047), (-0.004, -0.048), (-0.014, -0.04), (-0.024, -0.014)], 3)
    lg = lambda y: 0.011 + 0.001 * GT.smooth(-0.004, -0.03, y)
    q.add('polimero', punho_redondo(cont, -0.004, -0.048, lg, n=2.4, fatias=60, voltas=44, raio_base=0.004))
    nerv = punho_redondo(cont, -0.004, -0.048, lambda y: lg(y) + 0.0009, n=2.4, fatias=60, voltas=44, raio_base=0.004)
    for y in (-0.016, -0.024, -0.032, -0.04):
        q.add('polimero', inter([nerv.copy(), caixa(-0.03, 0.001, y - 0.002, y, -1, 1)]))
    A.pivo = (0, 0, 0)


@_acessorio('empunhadura_quadrada', 'Empunhadura vertical quadrada', 'empunhadura', 'mlok_baixo', peso_kg=0.1, raridade='incomum', valor_troca=15,
            modificadores={'recuo': 0.82, 'precisao_rajada': 1.3}, onde=['quartel', 'delegacia'],
            descricao='Empunhadura alta de seção quadrada com cantos chanfrados, sulcos e tampa recartilhada (guarda pilha reserva).')
def empunhadura_quadrada(A):
    q = A.base; _base_mlok(q, 0.044)
    q.add('polimero', solido(arred([(-0.022, -0.004), (0.022, -0.004), (0.022, -0.011), (0.0135, -0.03), (-0.0135, -0.024), (-0.022, -0.011)], 0.002),
                             -0.0135, 0.0135, 0.0015))                                                     # cabeca inclinada
    sec = arred([(-0.0135, -0.0135), (0.0135, -0.0135), (0.0135, 0.0135), (-0.0135, 0.0135)], 0.004)
    corpo = ext_y(sec, -0.106, -0.02)
    cortes = []
    for y in (-0.044, -0.064, -0.084):
        cortes.append(menos(ext_y(sec.buffer(0.002), y, y + 0.0014), ext_y(sec.buffer(-0.001), y - 0.001, y + 0.003)))
    q.add('polimero', menos(corpo, *cortes))
    q.add('polimero', ext_y(sec.buffer(0.0006), -0.11, -0.106))
    q.add('recartilhado', _cil_y(0.0125, -0.118, -0.11, 0.0, 0.0, 48)); q.add('aluminio_preto', _cil_y(0.0105, -0.1195, -0.118, 0.0, 0.0, 40))
    A.pivo = (0, 0, 0)


@_acessorio('empunhadura_cilindrica', 'Empunhadura cilíndrica recartilhada', 'empunhadura', 'mlok_baixo', peso_kg=0.12, raridade='raro', valor_troca=18,
            modificadores={'recuo': 0.84, 'precisao_rajada': 1.28}, onde=['quartel'],
            descricao='Cilindro de alumínio recartilhado preso num bloco inclinado: a mão fica um pouco mais à frente.')
def empunhadura_cilindrica(A):
    q = A.base; _base_mlok(q, 0.044)
    q.add('aluminio_preto', solido(arred([(0.022, -0.004), (-0.022, -0.004), (-0.02, -0.012), (-0.004, -0.03), (0.016, -0.03), (0.02, -0.014)], 0.002),
                                   -0.011, 0.011, 0.0015))                                                 # bloco inclinado
    L = 0.09; r = 0.0155
    perf = [(0.0, 0.0), (r - 0.002, 0.0), (r, 0.002), (r, L - 0.003), (r - 0.003, L), (0.0, L)]
    m = []
    m.append(('aluminio_preto', torno_x(perf, 56)))
    for a, b in ((0.012, 0.038), (0.044, 0.078)): m.append(('recartilhado', tubo_x(0.0, r + 0.0005, a, b, sec=56)))
    for a in (0.0385, 0.0415): m.append(('aluminio_preto', tubo_x(0.0, r + 0.0008, a, a + 0.0015, sec=56)))
    M = TF.translation_matrix([0.006, -0.026, 0]) @ TF.rotation_matrix(math.radians(-100), [0, 0, 1])     # pe do cilindro inclinado para tras
    for mat, g in m: q.add(mat, g.apply_transform(M))
    A.pivo = (0, 0, 0)


@_acessorio('batente_mao', 'Batente de mão', 'empunhadura', 'mlok_baixo', peso_kg=0.04, raridade='incomum', valor_troca=10,
            modificadores={'recuo': 0.92, 'tempo_mirar': 0.9}, onde=['quartel', 'galeria'],
            descricao='Gancho vazado na frente do guarda-mão: a mão encosta nele e não escorrega para o cano quente.')
def batente_mao(A):
    q = A.base; _base_mlok(q, 0.06)
    # gancho atras (lado da mao) e rampa subindo para a frente: a mao empurra contra o gancho
    esp = lambda pts: [(-x, y) for x, y in pts]
    fora = suave(esp([(-0.036, -0.004), (0.036, -0.004), (0.042, -0.012), (0.042, -0.03), (0.034, -0.044), (0.022, -0.046), (0.012, -0.036), (-0.02, -0.012),
                      (-0.036, -0.008)]), 3)
    furo = suave(esp([(0.012, -0.0115), (0.031, -0.0115), (0.035, -0.02), (0.033, -0.033), (0.025, -0.037), (0.018, -0.03)]), 3)
    q.add('polimero', solido(Polygon(fora).difference(Polygon(furo)), -0.0075, 0.0075, 0.0018))
    q.add('polimero', solido(LineString([(-0.032, -0.0055), (0.034, -0.0055)]).buffer(0.0008), -0.0085, 0.0085))   # aba fina de cima
    A.pivo = (0, 0, 0)


# variantes caramelo para a versao bicolor
@_acessorio('empunhadura_curta_tan', 'Empunhadura curta inclinada (caramelo)', 'empunhadura', 'mlok_baixo', peso_kg=0.05, raridade='incomum', valor_troca=12,
            modificadores={'recuo': 0.9, 'tempo_mirar': 0.92}, onde=['quartel'], descricao='A mesma empunhadura curta, em polímero caramelo.')
def empunhadura_curta_tan(A): empunhadura_curta(A); _em_tan(A)


@_acessorio('coronha_retratil_ar_tan', 'Coronha retrátil caramelo', 'coronha', 'coronha_ar', peso_kg=0.25, raridade='raro', valor_troca=24,
            modificadores={'recuo': 0.7, 'precisao': 1.25}, onde=['quartel'], descricao='Coronha retrátil de 5 posições em polímero caramelo.')
def coronha_retratil_ar_tan(A): coronha_retratil_12(A); _em_tan(A, {'polimero': 'polimero_tan'})


@_acessorio('supressor_556_tan', 'Supressor 5,56 caramelo', 'boca', 'boca_556', peso_kg=0.45, raridade='muito raro', valor_troca=90,
            modificadores={'ruido_m': 0.3, 'clarao': 0.05, 'recuo': 0.85}, onde=['quartel'],
            descricao='O mesmo supressor com pintura cerâmica caramelo: o tiro é ouvido a 50 m em vez de 160.')
def supressor_556_tan(A): supressor_556(A); _em_tan(A)


@_acessorio('carregador_556_30_tan', 'Carregador 5,56 (30) caramelo', 'carregador', 'carregador_556', capacidade=30, municao='municao_556', peso_kg=0.13,
            raridade='incomum', valor_troca=12, modificadores={}, onde=['quartel'], descricao='Carregador curvo de polímero caramelo, 30 tiros.')
def carregador_556_30_tan(A): _carregador_curvo(A.base, 30); _em_tan(A); A.pivo = (MAG_X, MAG_Y, 0)


NOVOS = {'encaixe_mira': [], 'encaixe_boca': ['supressor_556_tan'], 'encaixe_carregador': ['carregador_556_30_tan'],
         'encaixe_coronha': ['coronha_retratil_ar_tan'], 'encaixe_laser': ['modulo_laser'], 'encaixe_lanterna': ['lanterna_compacta'],
         'encaixe_empunhadura': ['empunhadura_curta', 'empunhadura_curta_tan', 'empunhadura_quadrada', 'empunhadura_cilindrica', 'batente_mao']}


def _aceita_novos(A):
    for e in A.encaixes:
        for n in NOVOS.get(e['no'], []):
            if n not in e.get('aceita', []): e['aceita'].append(n)


def fuzil_556_bicolor(A):
    fuzil_556(A); _aceita_novos(A)
    _recolore(A.base, TAN)
    for pt in A.partes:
        if pt['no'] == 'carregador': _recolore(pt['peca'], {'polimero': 'polimero_tan'})
    padrao = {'encaixe_mira': 'luneta_1_6', 'encaixe_boca': 'supressor_556_tan', 'encaixe_coronha': 'coronha_retratil_ar_tan',
              'encaixe_empunhadura': 'empunhadura_curta_tan', 'encaixe_lanterna': 'lanterna_compacta'}
    for e in A.encaixes:
        if e['no'] in padrao: e['padrao'] = padrao[e['no']]


REG['fuzil_556_bicolor'] = dict(REG['fuzil_556'], id='fuzil_556_bicolor', nome='Fuzil Vigília 5,56 bicolor', fn=fuzil_556_bicolor, raridade='muito raro',
                                valor_troca=230, onde=['quartel'],
                                descricao='O mesmo fuzil com guarda-mão, punho, carregador e coronha caramelo e receptor preto. Vem montado com '
                                          'luneta 1-6×, supressor, lanterna compacta e empunhadura curta.')
_f556 = REG['fuzil_556']['fn']
def _fuzil_556_com_novos(A): _f556(A); _aceita_novos(A)
REG['fuzil_556']['fn'] = _fuzil_556_com_novos
