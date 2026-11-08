# Arma 7: fuzil de receptor estampado 7,62x39 (estilo AK) com seus acessorios. Executado por gerar_armas.py
# (plano de lado: x frente, y cima, z direita). Desenho proprio inspirado nas fotos do Bruno; nada copiado de fuzil comercial.

KX0, KX1 = -0.075, 0.165        # receptor em x (tras / munhao)
KY0, KY1 = -0.03, 0.006         # fundo e borda de cima do receptor (a tampa fica por cima)
KW = 0.0118                     # meia largura do receptor
KTAMPA = 0.026                  # topo da tampa
K_XM = 0.585                    # boca do cano
KMAG_X, KMAG_Y = 0.092, -0.03   # topo do carregador (centro)
KCF = 0.115                     # curso do ferrolho
GM0 = (0.19, -0.006, 0.0)       # encaixe do guarda-mao
TAMPA0 = (KX1 - 0.022, KY1, 0.0)  # pivo da tampa
MIRA_Y = 0.0365                 # ponta da massa = fundo do entalhe da alca (linha de visada paralela ao cano)


def _cartucho_762(sec=20, vazio=False):
    """Cartucho 7,62x39: estojo conico de aco laqueado, ponta de cobre."""
    q = P()
    est = torno_x([(0.0, 0.0), (0.0056, 0.0), (0.0056, 0.0012), (0.0048, 0.0016), (0.0048, 0.0024), (0.0056, 0.003), (0.005, 0.0305),
                   (0.0043, 0.0325), (0.0043, 0.0387), (0.0, 0.0387)], sec)
    if vazio: est = menos(est, cil_x(0.0039, 0.004, 0.045, sec=sec), cil_x(0.0046, 0.004, 0.03, sec=sec))
    q.add('laca_verde', est)
    if not vazio:
        q.add('cobre_bala', torno_x([(0.0039, 0.036), (0.0039, 0.043), (0.0033, 0.0505), (0.0018, 0.0545), (0.0005, 0.0562), (0.0, 0.0563)], sec))
    q.add('cobre_bala', torno_x([(0.0, -0.00005), (0.0021, -0.00005), (0.0021, 0.0004)], max(8, sec // 2)))
    return q


CORES.update({'laca_verde': (70, 76, 50), 'madeira_ak': (120, 58, 30), 'baquelite': (88, 38, 30)})
METAL.update({'laca_verde': (0.5, 0.42), 'madeira_ak': (0.0, 0.5), 'baquelite': (0.0, 0.42)})


def _receptor_ak(p):
    # caixa estampada: paredes finas, fundo arredondado, rebites e reforco do poco do carregador
    perfil = arred([(KX0, KY1), (KX1, KY1), (KX1, KY0 + 0.004), (KX1 - 0.006, KY0), (KX0 + 0.008, KY0), (KX0, KY0 + 0.008)], 0.002)
    caixa_r = solido(perfil, -KW, KW, 0.0012)
    caixa_r = menos(caixa_r, solido(arred([(KX0 + 0.004, KY0 + 0.0025), (KX1 - 0.004, KY0 + 0.0025), (KX1 - 0.004, KY1 + 0.01), (KX0 + 0.004, KY1 + 0.01)], 0.002),
                                    -KW + 0.0012, KW - 0.0012),
                    caixa(KMAG_X - 0.019, KMAG_X + 0.019, KY0 - 0.01, KY0 + 0.004, -0.0095, 0.0095),               # poco
                    caixa(0.03, 0.06, KY0 - 0.01, KY0 + 0.004, -0.004, 0.004),                                     # fenda do gatilho
                    caixa(0.035, 0.12, KY1 - 0.007, KY1 - 0.001, KW - 0.002, KW + 0.002))                          # trilho do retem (direita)
    p.add('aco_oxidado', caixa_r)
    for zs in (-1, 1):
        s = (min(zs * KW, zs * (KW + 0.0012)), max(zs * KW, zs * (KW + 0.0012)))
        p.add('aco_oxidado', solido(arred([(KMAG_X - 0.03, KY0 + 0.0005), (KMAG_X + 0.028, KY0 + 0.0005), (KMAG_X + 0.024, -0.012), (KMAG_X - 0.024, -0.012)], 0.004),
                                    *s, 0.0004))                                                                 # reforco estampado do poco
        p.add('aco_oxidado', solido(arred([(KX1 - 0.026, KY0 + 0.002), (KX1 - 0.002, KY0 + 0.002), (KX1 - 0.002, KY1 - 0.002), (KX1 - 0.026, KY1 - 0.002)], 0.002),
                                    *s, 0.0004))                                                                 # munhao dianteiro
        for (x, y) in ((KX1 - 0.02, -0.006), (KX1 - 0.008, -0.006), (KX1 - 0.02, -0.02), (KX1 - 0.008, -0.02), (0.005, -0.018), (0.065, -0.018),
                       (KX0 + 0.012, -0.012), (KX0 + 0.012, -0.022), (0.118, -0.024), (0.124, -0.012)):
            p.add('aco_inox' if (x, y) in ((0.005, -0.018), (0.065, -0.018)) else 'aco_oxidado',
                  torno_x([(0.0, 0.0), (0.0021, 0.0), (0.0017, 0.0009), (0.0, 0.0011)], 16).apply_transform(
                      TF.rotation_matrix(-zs * math.pi / 2, [0, 1, 0])).apply_translation([x, y, zs * (KW + 0.0012)]))  # rebites e pinos
    # trilho lateral (cauda de andorinha) no lado esquerdo para a mira lateral
    p.add('aco_oxidado', solido(arred([(0.0, -0.016), (0.085, -0.016), (0.085, 0.002), (0.0, 0.002)], 0.002), -KW - 0.0045, -KW - 0.0002, 0.0014))
    for x in (0.012, 0.075): p.add('aco_inox', cil_z(0.0022, -KW - 0.0052, -KW - 0.0044, x, -0.007, 16))
    # munhao e bloco da alca de mira
    p.add('aco_oxidado', torno_x([(0.0, KX1 - 0.002), (0.0115, KX1 - 0.002), (0.0115, KX1 + 0.038), (0.0095, KX1 + 0.042), (0.0, KX1 + 0.042)], 40, -0.006))
    p.add('aco_oxidado', solido(arred([(KX1 + 0.002, -0.004), (KX1 + 0.05, -0.004), (KX1 + 0.05, 0.018), (KX1 + 0.012, 0.022), (KX1 + 0.002, 0.016)], 0.002),
                                -0.0105, 0.0105, 0.0012))                                                         # base da alca
    # cano, bloco de gas com torre da massa, tubo de gas
    p.add('aco_cano', torno_x([(0.0085, KX1 + 0.04), (0.0085, 0.42), (0.0075, 0.425), (0.0075, K_XM - 0.016), (0.0072, K_XM - 0.015)], 40, -0.006))
    rosca_x(p, 'aco_cano', 0.0072, K_XM - 0.015, K_XM - 0.0004, 0.001, -0.006)
    p.add('aco_cano', tubo_x(0.0029, 0.0072, K_XM - 0.0004, K_XM, -0.006, sec=32))
    p.add('aco_oxidado', solido(arred([(0.405, -0.017), (0.44, -0.017), (0.44, 0.02), (0.41, 0.026), (0.405, 0.02)], 0.003), -0.0095, 0.0095, 0.0015))   # bloco de gas
    p.add('aco_oxidado', menos(cil_x(0.0085, 0.2, 0.41, 0.018, 0, 36), *[cil_z(0.0018, -0.02, 0.02, x, 0.018, 12) for x in (0.385, 0.392, 0.399)]))   # tubo de gas com respiros
    p.add('aco_oxidado', cil_x(0.0025, 0.16, 0.545, -0.0175, 0, 12))                                                  # vareta de limpeza
    p.add('aco_oxidado', cil_x(0.0034, 0.538, 0.548, -0.0175, 0, 12))
    p.add('aco_oxidado', solido(arred([(0.47, -0.017), (0.478, -0.017), (0.478, -0.009), (0.47, -0.009)], 0.001), -0.004, 0.004, 0.0005))  # guia da vareta
    p.add('aco_oxidado', cil_x(0.0095, 0.405, 0.418, 0.018, 0, 36))
    torre = solido(arred([(0.525, -0.018), (0.552, -0.018), (0.552, 0.018), (0.548, MIRA_Y + 0.006), (0.529, MIRA_Y + 0.006), (0.525, 0.018)], 0.003), -0.009, 0.009, 0.0012)
    torre = menos(torre, cil_x(0.0076, 0.5, 0.57, -0.006, 0, 32), solido(arred([(0.53, 0.014), (0.547, 0.014), (0.547, 0.06), (0.53, 0.06)], 0.002), -0.0065, 0.0065))
    p.add('aco_oxidado', torre)                                                                                     # torre da massa (orelhas)
    p.add('aco_inox', caixa(0.536, 0.541, 0.012, MIRA_Y, -0.001, 0.001))                                            # poste da massa
    p.add('tinta_branca', caixa(0.5355, 0.5415, MIRA_Y - 0.0013, MIRA_Y + 0.0001, -0.0011, 0.0011))
    p.add('aco_oxidado', cil_z(0.002, -0.0098, 0.0098, 0.509, -0.0155, 12))                                       # pino da bandoleira/baioneta
    # aneis que prendem o guarda-mao (o guarda-mao e acessorio: encaixe_guarda_mao)
    p.add('aco_oxidado', solido(arred([(0.188, -0.037), (0.2, -0.037), (0.2, 0.008), (0.188, 0.008)], 0.0015), -0.0188, 0.0188, 0.0008))   # anel de tras do guarda-mao
    p.add('aco_oxidado', solido(arred([(0.385, -0.037), (0.397, -0.037), (0.397, 0.008), (0.385, 0.008)], 0.0015), -0.0188, 0.0188, 0.0008))  # anel da frente
    # guarda-mato estampado
    fora = arred([(0.022, KY0 + 0.001), (0.08, KY0 + 0.001), (0.078, KY0 - 0.006), (0.066, KY0 - 0.024), (0.03, KY0 - 0.026), (0.02, KY0 - 0.018)], 0.004)
    dentro = arred([(0.029, KY0 - 0.001), (0.072, KY0 - 0.001), (0.07, KY0 - 0.006), (0.062, KY0 - 0.02), (0.033, KY0 - 0.022), (0.027, KY0 - 0.016)], 0.003)
    p.add('aco_oxidado', solido(fora.difference(dentro), -0.0045, 0.0045, 0.001))
    # retem do carregador (pá atras do poco)
    p.add('aco_oxidado', solido(arred([(KMAG_X - 0.024, KY0 + 0.001), (KMAG_X - 0.02, KY0 + 0.001), (KMAG_X - 0.017, KY0 - 0.016), (KMAG_X - 0.026, KY0 - 0.018)], 0.0015),
                                -0.007, 0.007, 0.0008))
    # cabo de polimero marrom arredondado
    GY = 0.0205   # o topo do cabo entra no fundo do receptor (sem fresta)
    cabo = affinity.translate(CABO12, 0.006, GY); lg = lambda y: LARG12(y - GY) * 0.95
    p.add('baquelite', punho_redondo(cabo, -0.0435 + GY, -0.1555 + GY, lg, n=2.3, fatias=110, voltas=56, raio_base=0.005))
    pont = punho_redondo(cabo, -0.0435 + GY, -0.1555 + GY, lambda y: lg(y) + 0.0004, n=2.3, fatias=110, voltas=56, raio_base=0.005)
    p.add('polimero_grip', inter([pont, solido(cabo.buffer(-0.003, join_style=1).intersection(sbox(-1, -0.1525 + GY, 1, -0.0625 + GY)), -0.05, 0.05)]))   # quadriculado
    # anel da tampa (tras) onde encaixa a coronha
    p.add('aco_oxidado', solido(arred([(KX0 - 0.006, KY0 + 0.004), (KX0 + 0.002, KY0 + 0.004), (KX0 + 0.002, KY1 + 0.008), (KX0 - 0.006, KY1 + 0.008)], 0.002),
                                -KW - 0.0005, KW + 0.0005, 0.001))


def punho_x(perfil, meia, n=2.6):
    """Peca alongada em x (guarda-mao) com secao arredondada: loft do perfil lateral."""
    xs = [c[0] for c in perfil.exterior.coords]
    return corpo_x(perfil, max(xs), min(xs), lambda x: meia, n=n, fatias=80, voltas=40, raio_tras=0.003, raio_frente=0.003)


def _tampa_ak(q):
    """Tampa do receptor com nervuras e o botao do retem atras."""
    sec = Polygon([(KW - 0.0004, KY1 - 0.002)] + [(KW * 0.96 * math.cos(t), KY1 + 0.003 + (KTAMPA - KY1 - 0.003) * math.sin(t)) for t in np.linspace(0, math.pi, 28)]
                  + [(-KW + 0.0004, KY1 - 0.002)]).buffer(0)
    zy = sec                                                                                           # secao (z, y)
    t = ext_x(zy, KX0 + 0.002, KX1 - 0.022)
    t = menos(t, ext_x(zy.buffer(-0.0011), KX0 - 0.01, KX1 - 0.024))
    q.add('aco_oxidado', t)
    for x in np.arange(KX0 + 0.035, KX1 - 0.04, 0.03):                                                  # nervuras estampadas
        q.add('aco_oxidado', inter([ext_x(zy.buffer(0.0006), x, x + 0.006), caixa(x - 0.001, x + 0.007, KY1 + 0.012, 0.05, -1, 1)]))
    q.add('aco_oxidado', solido(arred([(KX0 - 0.004, KY1 + 0.004), (KX0 + 0.004, KY1 + 0.004), (KX0 + 0.004, KY1 + 0.012), (KX0 - 0.004, KY1 + 0.012)], 0.002),
                                -0.0045, 0.0045, 0.0008))                                                  # botao do retem da tampa


def _ferrolho_ak(q):
    q.add('aco_fosfatado', caixa(0.04, 0.155, KY1 - 0.005, KY1 + 0.012, -0.0075, 0.0075))
    q.add('aco_fosfatado', cil_x(0.0068, 0.155, 0.2, 0.018, 0, 32))                                            # pistao (entra no tubo de gas)
    q.add('aco_inox', cil_x(0.0062, 0.14, 0.165, -0.006, 0, 24))                                               # cabeca do ferrolho
    q.add('aco_fosfatado', caixa(0.115, 0.122, KY1 - 0.002, KY1 + 0.004, 0.0075, KW + 0.012))                 # braco da alavanca (direita)
    q.add('aco_fosfatado', torno_x([(0.0, 0.0), (0.0055, 0.0), (0.0062, 0.003), (0.0055, 0.011), (0.0, 0.012)], 24).apply_transform(
        TF.rotation_matrix(math.pi / 2, [0, 1, 0])).apply_translation([0.1185, KY1 + 0.001, KW + 0.012]))       # manopla de manejo


def _seletor_ak(q):
    """Alavanca grande do seletor no lado direito (pivo atras), com o dente de apoio do dedo."""
    lev = arred([(KX0 + 0.012, -0.004), (KX0 + 0.02, -0.009), (0.06, -0.006), (0.075, -0.004), (0.078, 0.0), (0.06, 0.001), (KX0 + 0.02, 0.003), (KX0 + 0.012, 0.002)], 0.002)
    q.add('aco_oxidado', solido(lev, KW + 0.0012, KW + 0.0028, 0.0004))
    q.add('aco_oxidado', solido(arred([(0.068, -0.012), (0.075, -0.012), (0.075, -0.004), (0.068, -0.004)], 0.0015), KW + 0.0012, KW + 0.0052, 0.0006))
    q.add('aco_oxidado', cil_z(0.0045, KW + 0.0012, KW + 0.0035, KX0 + 0.014, -0.0015, 20))


def _gatilho_ak(q): _gatilho_em(q, 0.048, KY0 + 0.004)


def _carregador_ak(q, cap=30, mat='laca_verde', grade=False):
    """Carregador curvo de aco (bem curvo), nervuras estampadas, base com chapa e ressalto de tranca na frente.
    grade=True: corpo de polimero com quadros em relevo dos lados (grade) e base de polimero."""
    R = 0.24; cx, cy = KMAG_X + R, KMAG_Y; L = 0.2 if cap <= 30 else 0.255; fi = L / R
    th = np.linspace(math.pi, math.pi + fi, 50)
    fr = [(cx + (R - 0.031) * math.cos(t), cy + (R - 0.031) * math.sin(t)) for t in th]
    tr = [(cx + (R + 0.031) * math.cos(t), cy + (R + 0.031) * math.sin(t)) for t in th]
    perfil = Polygon(fr + tr[::-1]).buffer(0)
    q.add(mat, solido(arred(list(perfil.exterior.coords)[:-1], 0.0025), -0.0115, 0.0115, 0.0015))
    for zs in (-1, 1):
        if grade:                                                                                          # quadros em relevo (grade)
            nl = 6 if cap <= 30 else 8; dt = (fi - 0.08) / nl
            for i in range(nl):
                for (ra, rb) in ((R - 0.026, R - 0.003), (R + 0.003, R + 0.026)):
                    tt = np.linspace(math.pi + 0.05 + i * dt + 0.006, math.pi + 0.05 + (i + 1) * dt - 0.006, 8)
                    pol = Polygon([(cx + ra * math.cos(t), cy + ra * math.sin(t)) for t in tt] + [(cx + rb * math.cos(t), cy + rb * math.sin(t)) for t in tt[::-1]])
                    q.add(mat, solido(pol.buffer(-0.0012, join_style=2).buffer(0.001, join_style=1, resolution=2), min(zs * 0.0113, zs * 0.0122), max(zs * 0.0113, zs * 0.0122), 0.0004))
            continue
        th2 = np.linspace(math.pi + 0.06, math.pi + fi - 0.05, 30)                                        # nervura curva estampada
        pts = [(cx + (R + 0.012) * math.cos(t), cy + (R + 0.012) * math.sin(t)) for t in th2]
        q.add(mat, solido(LineString(pts).buffer(0.004, cap_style=1), min(zs * 0.0115, zs * 0.0122), max(zs * 0.0115, zs * 0.0122), 0.0004))
    q.add(mat, solido(arred([(KMAG_X + 0.026, KMAG_Y + 0.006), (KMAG_X + 0.036, KMAG_Y + 0.006), (KMAG_X + 0.036, KMAG_Y - 0.004), (KMAG_X + 0.026, KMAG_Y - 0.008)], 0.0015),
                      -0.006, 0.006, 0.0006))                                                                # ressalto da frente (gancho)
    t = math.pi + fi; c, s_ = math.cos(t), math.sin(t)
    b0 = np.array([cx + R * c, cy + R * s_]); d = np.array([c, s_]); nn = np.array([s_, -c])
    base = [b0 + d * 0.034 - nn * 0.001, b0 - d * 0.034 - nn * 0.001, b0 - d * 0.035 + nn * 0.006, b0 + d * 0.035 + nn * 0.006]
    q.add(mat if grade else 'aco_oxidado', solido(Polygon([tuple(x) for x in base]).buffer(0.0015, join_style=1), -0.0128, 0.0128, 0.0012))
    for zs in (-1, 1): q.add(mat, caixa(KMAG_X - 0.028, KMAG_X + 0.024, KMAG_Y - 0.002, KMAG_Y + 0.003, zs * 0.0065 - 0.0014, zs * 0.0065 + 0.0014))
    q.merge(_cartucho_762(14), TF.translation_matrix([KMAG_X - 0.028, KMAG_Y - 0.0035, 0.002]))


def _tambor_ak(q):
    """Tambor de 75 com o eixo ao longo do cano (mesma ideia do tambor do 5,56): torre curta, corpo redondo, tampa com chave."""
    q.add('laca_verde', solido(arred([(KMAG_X - 0.031, KMAG_Y), (KMAG_X + 0.031, KMAG_Y), (KMAG_X + 0.034, -0.085), (KMAG_X - 0.034, -0.085)], 0.002),
                               -0.0115, 0.0115, 0.0012))
    Rd, cyy = 0.058, -0.14; x0, x1 = KMAG_X - 0.04, KMAG_X + 0.07
    q.add('laca_verde', torno_x([(0.0, x0), (Rd - 0.004, x0), (Rd, x0 + 0.004), (Rd, x1 - 0.004), (Rd - 0.004, x1), (0.0, x1)], 72, y=cyy))
    for xb in (x0 + 0.02, (x0 + x1) / 2, x1 - 0.02): q.add('laca_verde', tubo_x(Rd - 0.002, Rd + 0.0018, xb - 0.004, xb + 0.004, y=cyy, sec=72, ch=0.0008))
    q.add('laca_verde', torno_x([(0.0, x1 + 0.006), (Rd - 0.012, x1 + 0.006), (Rd - 0.006, x1 + 0.003), (Rd - 0.005, x1)], 72, y=cyy))
    q.add('aco_oxidado', cil_x(0.014, x1 + 0.005, x1 + 0.012, cyy, 0, 40))
    q.add('aco_oxidado', solido(arred([(-0.022, -0.004), (0.022, -0.004), (0.022, 0.004), (-0.022, 0.004)], 0.003), -0.003, 0.003, 0.001)
          .apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])).apply_translation([x1 + 0.016, cyy, 0]))
    q.add('laca_verde', solido(arred([(KMAG_X - 0.04, -0.07), (KMAG_X + 0.04, -0.07), (KMAG_X + 0.042, -0.092), (KMAG_X - 0.042, -0.092)], 0.004), -0.02, 0.02, 0.004))
    q.merge(_cartucho_762(14), TF.translation_matrix([KMAG_X - 0.028, KMAG_Y - 0.0035, 0.002]))


def _alca_ak(q):
    """Alca de mira de folha (tangente) com cursor e entalhe em V; o centro do entalhe fica em y = MIRA_Y."""
    q.add('aco_oxidado', solido(arred([(KX1 + 0.008, 0.016), (KX1 + 0.058, 0.019), (KX1 + 0.058, 0.0225), (KX1 + 0.008, 0.0215)], 0.0012), -0.0075, 0.0075, 0.0006))
    folha = arred([(KX1 + 0.008, 0.0215), (KX1 + 0.012, 0.0215), (KX1 + 0.012, MIRA_Y + 0.0045), (KX1 + 0.008, MIRA_Y + 0.0045)], 0.0006)
    q.add('aco_oxidado', menos(solido(folha, -0.0075, 0.0075, 0.0003),
                               solido(Polygon([(KX1, MIRA_Y), (KX1 + 0.02, MIRA_Y), (KX1 + 0.02, MIRA_Y + 0.01), (KX1, MIRA_Y + 0.01)]), -0.0012, 0.0012),
                               solido(Polygon([(KX1, MIRA_Y + 0.0035), (KX1 + 0.02, MIRA_Y + 0.0035), (KX1 + 0.02, MIRA_Y + 0.01)]), -0.003, 0.003)))
    q.add('aco_oxidado', caixa(KX1 + 0.009, KX1 + 0.013, MIRA_Y - 0.009, MIRA_Y - 0.004, -0.0085, 0.0085))                         # cursor
    for zs in (-1, 1): q.add('aco_inox', caixa(KX1 + 0.0095, KX1 + 0.0125, MIRA_Y - 0.008, MIRA_Y - 0.005, zs * 0.0085 - 0.0004, zs * 0.0085 + 0.0004))



@arma('fuzil_762', 'Fuzil Brasa 7,62', 'armas', 'fuzil', classe='fogo', calibre='7,62×39', municao='municao_762', capacidade=30, dano=55,
      alcance_m=70, alcance_max_m=350, modo='semiautomático e automático (seletor)', tiros_por_s=10, recarga_s=2.5, recarga_vazia_s=3.0,
      precisao=0.68, recuo=0.5, ruido_m=180, durabilidade=6000, peso_kg=3.6, raridade='raro', valor_troca=160, onde=['quartel', 'delegacia', 'fabrica'],
      estojo_s=0.02, descricao='Fuzil de receptor estampado, guarda-mão e coronha de madeira, tubo de gás por cima do cano. Aguenta sujeira e '
                               'falta de manutenção como nenhum outro, mas coice forte e mira de ferro grosseira.')
def fuzil_762(A):
    A.pivo = (-0.018, -0.09, 0.0)
    _receptor_ak(A.base)
    _alca_ak(A.base)
    tp = A.parte('tampa', TAMPA0, explodir=(0, 0.06, 0), tipo='remove', descricao='tampa do receptor (sai para limpar)')
    _tampa_ak(tp)
    gat = A.parte('gatilho', (0.048, KY0 + 0.004, 0), explodir=(0.0, -0.06, 0), tipo='gira', eixo='x', curso_graus=-12, descricao='puxa para trás')
    _gatilho_ak(gat)
    sel = A.parte('seletor', (KX0 + 0.014, -0.0015, KW), explodir=(0, 0, 0.04), tipo='gira', eixo='z', curso_graus=-14,
                  descricao='alavanca: em cima trava (e fecha a fenda), meio automático (-7°), embaixo semi (-14°)')
    _seletor_ak(sel)
    fr = A.parte('ferrolho', (0, 0, 0), explodir=(-0.06, 0.05, 0.04), tipo='desliza', curso_m=-KCF, descricao='transportador com a alavanca de manejo à direita: recua 115 mm')
    _ferrolho_ak(fr)
    car = A.parte('carregador', (KMAG_X, KMAG_Y, 0), explodir=(0.02, -0.12, 0), tipo='remove', direcao=[0.3, -0.95, 0.0], municao='municao_762', capacidade=30,
                  descricao='carregador de aço de 30: entra pela frente (gancho) e gira para trás até travar')
    _carregador_ak(car, 30)
    A.encaixe('encaixe_mira', (0.045, -0.007, -KW - 0.0045), 'trilho_lateral_ak', explodir=(0, 0, -0.08),
              aceita=['mira_lateral_ak', 'luneta_lateral_ak'], descricao='trilho de cauda de andorinha do lado esquerdo')
    A.encaixe('encaixe_boca', (K_XM - 0.015, -0.006, 0), 'boca_762', explodir=(0.08, 0, 0), aceita=['freio_ak', 'compensador_ak', 'supressor_762'], padrao='freio_ak')
    A.encaixe('encaixe_carregador', (KMAG_X, KMAG_Y, 0), 'carregador_762', pai='carregador', substitui='carregador',
              aceita=['carregador_762_30', 'carregador_762_30_grade', 'carregador_762_40', 'tambor_762_75'], descricao='filho do nó carregador; ao pôr um carregador aqui, esconda o original')
    A.encaixe('encaixe_coronha', (KX0 - 0.006, -0.005, 0), 'coronha_ak', explodir=(-0.08, 0, 0),
              aceita=['coronha_madeira_ak', 'coronha_polimero_ak', 'coronha_rebativel_ak', 'coronha_retratil_ak', 'coronha_leve_ak', 'coronha_leve_ak_tan', 'coronha_esqueleto_ak'],
              padrao='coronha_madeira_ak')
    A.encaixe('encaixe_empunhadura', (0.3, -0.0435, 0), 'mlok_baixo', explodir=(0, -0.06, 0), requer={'encaixe_guarda_mao': ['guarda_mao_trilhos_ak', 'guarda_mao_fendas_ak']},
              aceita=['empunhadura_reta', 'empunhadura_reta_tan', 'empunhadura_vertical', 'empunhadura_angulada', 'empunhadura_curta', 'empunhadura_quadrada',
                      'empunhadura_cilindrica', 'batente_mao'], descricao='trilho de baixo do guarda-mão de quatro trilhos')
    A.encaixe('encaixe_lanterna', (0.33, -0.0045, 0.0245), 'mlok_lado', explodir=(0, 0, 0.06), requer={'encaixe_guarda_mao': ['guarda_mao_trilhos_ak', 'guarda_mao_fendas_ak']},
              aceita=['lanterna_fuzil', 'lanterna_compacta'], descricao='trilho da direita do guarda-mão de quatro trilhos')
    A.encaixe('encaixe_guarda_mao', GM0, 'guarda_mao_ak', explodir=(0, -0.05, 0.05),
              aceita=['guarda_mao_madeira_ak', 'guarda_mao_polimero_ak', 'guarda_mao_trilhos_ak', 'guarda_mao_fendas_ak'], padrao='guarda_mao_madeira_ak')
    A.encaixe('encaixe_enfeite', (0.293, -0.0035, 0), 'guarda_mao_enfeite', explodir=(0, 0.06, 0.04), aceita=['elastico_ak'],
              requer={'encaixe_guarda_mao': ['guarda_mao_madeira_ak', 'guarda_mao_polimero_ak', 'guarda_mao_fendas_ak']}, descricao='tiras de borracha em volta do guarda-mão')
    A.encaixe('encaixe_tampa', TAMPA0, 'tampa_ak', pai='tampa', substitui='tampa', explodir=(0, 0.06, 0), aceita=['tampa_trilho_ak'],
              descricao='filho do nó tampa; a tampa com trilho esconde a tampa original')
    A.encaixe('encaixe_mira_tampa', (0.03, KTAMPA + 0.0055, 0), 'trilho_mira', explodir=(0, 0.07, 0), requer={'encaixe_tampa': 'tampa_trilho_ak'},
              aceita=['mira_holografica', 'mira_reflexa', 'mira_ponto_vermelho_tubo', 'luneta_1_6', 'luneta_4x'], descricao='só existe com a tampa com trilho')
    A.encaixe('encaixe_baioneta', (0.509, -0.0155, 0), 'baioneta_ak', explodir=(0, -0.05, 0), aceita=['baioneta_ak'])
    A.encaixe('encaixe_bandoleira', (0.509, -0.0155, -0.0098), 'bandoleira', explodir=(0, 0, -0.04), aceita=['bandoleira'])
    A.encaixe('boca_fogo', (K_XM, -0.006, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('saida_estojo', (0.11, KY1 + 0.004, KW + 0.002), 'efeito', descricao='onde nasce o estojo (sai para a direita, para a frente e para cima)')
    A.encaixe('mira_ferro', (KX1 + 0.01, MIRA_Y + 0.0012, 0), 'mira', descricao='fundo do entalhe da alça: câmera de 1ª pessoa olha daqui pela ponta da massa (-Z)')
    A.anim('atirar', 0.1, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.01, -12), (0.05, -12), (0.09, 0)])),
                           ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.008, (0, 0, 0)), (0.04, (-KCF, 0, 0)), (0.085, (0, 0, 0))])),
                           (None, 'r', (0, 0, 1), pose([(0, 0), (0.01, 0), (0.03, 3.5), (0.1, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (0.01, (0, 0, 0)), (0.03, (-0.016, 0.003, 0)), (0.1, (0, 0, 0))]))],
           desc='um tiro (repita a 10 por segundo): ferrolho recua 115 mm, coice forte que sobe o cano')
    A.anim('atirar_ultimo', 0.1, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.01, -12), (0.05, -12), (0.09, 0)])),
                                  ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.008, (0, 0, 0)), (0.04, (-KCF, 0, 0)), (0.085, (0, 0, 0))])),
                                  (None, 'r', (0, 0, 1), pose([(0, 0), (0.01, 0), (0.03, 3.5), (0.1, 0)]))],
           desc='último tiro: este fuzil não trava o ferrolho atrás, ele volta à frente com a câmara vazia')
    gira = pose([(0, 0), (0.25, 0), (0.45, 14), (0.7, 14), (1.4, 14), (1.7, 14), (1.95, 0)])
    sai = pose([(0, (0, 0, 0)), (0.25, (0, 0, 0)), (0.45, (0.006, -0.008, 0)), (0.7, (0.03, -0.22, 0)), (1.4, (0.03, -0.22, 0)), (1.7, (0.006, -0.008, 0)),
                (1.95, (0, 0, 0))])
    giro_arma = (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, -22), (2.1, -22), (2.5, 0)]))
    A.anim('recarregar', 2.5, [('carregador', 't', sai), ('carregador', 'r', (0, 0, 1), gira), giro_arma],
           desc='aperta a pá, carregador gira para a frente e cai (0,7 s); o novo engancha na frente e gira para trás (1,95 s); troque o nó entre 0,7 e 1,4 s')
    A.anim('recarregar_vazia', 3.0, [('carregador', 't', sai), ('carregador', 'r', (0, 0, 1), gira), giro_arma,
                                     ('ferrolho', 't', pose([(0, (0, 0, 0)), (2.2, (0, 0, 0)), (2.45, (-KCF, 0, 0)), (2.55, (0, 0, 0))]))],
           desc='igual à recarga e no fim puxa a alavanca de manejo para pôr um cartucho na câmara')
    A.anim('trocar_modo', 0.5, [('seletor', 'r', (0, 0, 1), pose([(0, 0), (0.15, -7), (0.3, -7), (0.45, -14), (0.5, -14)]))],
           desc='seletor: trava -> automático -> semi (no jogo, pare na posição escolhida)')
    A.anim('inspecionar', 2.8, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -35), (1.4, -35), (1.8, 30), (2.4, 30), (2.8, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 8), (2.4, 8), (2.8, 0)])),
                                ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.7, (-0.04, 0, 0)), (1.1, (-0.04, 0, 0)), (1.2, (0, 0, 0))]))],
           desc='puxa a alavanca até ver o cartucho na câmara, solta e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.5), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


# ---------------------------------------------------------------------------- acessorios
@_acessorio('coronha_madeira_ak', 'Coronha de madeira (fuzil 7,62)', 'coronha', 'coronha_ak', peso_kg=0.6, raridade='comum', valor_troca=14,
            modificadores={'recuo': 0.65, 'precisao': 1.3}, onde=['quartel', 'fabrica', 'armazem'],
            descricao='Coronha fixa de madeira com soleira de aço e porta-bandoleira. Vem no fuzil.')
def coronha_madeira_ak(A):
    q = A.base
    perfil = suave([(0.0, 0.012), (-0.03, 0.012), (-0.2, 0.0), (-0.33, -0.012), (-0.338, -0.016), (-0.342, -0.14), (-0.334, -0.148),
                    (-0.3, -0.142), (-0.18, -0.098), (-0.06, -0.05), (-0.01, -0.036), (0.0, -0.035)], 3)
    larg = lambda x: 0.012 + 0.008 * GT.smooth(-0.01, -0.22, x)
    corpo = corpo_x(perfil, 0.0, -0.345, larg, n=2.4, fatias=150, voltas=56, raio_tras=0.004, raio_frente=0.0015)
    q.add('madeira_ak', inter([corpo, caixa(-0.336, 0.01, -1, 1, -1, 1)]))
    q.add('aco_oxidado', inter([corpo_x(perfil, 0.0, -0.345, lambda x: larg(x) + 0.0006, n=2.4, fatias=150, voltas=56, raio_tras=0.004), caixa(-0.36, -0.3355, -1, 1, -1, 1)]))
    q.add('aco_oxidado', caixa(-0.006, 0.006, -0.036, 0.013, -0.0125, 0.0125))                              # chapa que encaixa no receptor
    q.add('aco_oxidado', cil_x(0.0045, -0.346, -0.343, -0.03, 0, 16))                                                    # tampa do compartimento de limpeza
    alca = Point(-0.24, -0.124).buffer(0.0062, 32).difference(Point(-0.24, -0.124).buffer(0.0041, 32))
    q.add('aco_oxidado', solido(alca, -0.0014, 0.0014, 0.0004))
    A.encaixe('ombro', (-0.342, -0.07, 0), 'efeito', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


@_acessorio('coronha_rebativel_ak', 'Coronha rebatível de tubo (fuzil 7,62)', 'coronha', 'coronha_ak', peso_kg=0.45, raridade='raro', valor_troca=26,
            modificadores={'recuo': 0.75, 'precisao': 1.15, 'tempo_mirar': 0.9}, onde=['quartel'],
            descricao='Coronha de tubo de aço com soleira de borracha que dobra para a esquerda (nó "dobra", animações dobrar/abrir).')
def coronha_rebativel_ak(A):
    q = A.base
    q.add('aco_oxidado', caixa(-0.008, 0.006, -0.036, 0.013, -0.0125, 0.0125))
    q.add('aco_oxidado', _cil_y(0.004, -0.034, 0.012, -0.012, -0.0135, 20))   # pino da dobradica
    d = A.parte('dobra', (-0.012, 0, -0.0135), explodir=(-0.06, 0, 0), tipo='gira', eixo='y', curso_graus=-175, descricao='dobra para a esquerda do receptor')
    tubos = [LineString([(-0.014, 0.006), (-0.3, -0.004)]), LineString([(-0.014, -0.03), (-0.17, -0.07), (-0.3, -0.105)])]
    for t in tubos: d.add('aco_oxidado', solido(t.buffer(0.005, cap_style=1, join_style=1), -0.005, 0.005, 0.002))
    d.add('aco_oxidado', solido(LineString([(-0.3, -0.004), (-0.3, -0.105)]).buffer(0.005, cap_style=1), -0.006, 0.006, 0.002))
    d.add('borracha', solido(arred([(-0.312, 0.004), (-0.298, 0.004), (-0.298, -0.12), (-0.312, -0.12)], 0.005), -0.0165, 0.0165, 0.004))   # soleira
    d.add('borracha', inter([solido(tubos[0].buffer(0.0065), -0.0068, 0.0068, 0.002), caixa(-0.2, -0.08, -1, 1, -1, 1)]))              # apoio de rosto
    A.anim('dobrar', 0.5, [('dobra', 'r', (0, 1, 0), pose([(0, 0), (0.5, -175)]))], desc='dobra a coronha para o lado')
    A.anim('abrir', 0.5, [('dobra', 'r', (0, 1, 0), pose([(0, -175), (0.5, 0)]))], desc='abre a coronha')
    A.encaixe('ombro', (-0.312, -0.05, 0), 'efeito', pai='dobra', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


@_acessorio('freio_ak', 'Freio de boca inclinado (7,62)', 'boca', 'boca_762', peso_kg=0.03, raridade='comum', modificadores={'recuo': 0.85},
            descricao='Bocal cortado em diagonal que empurra o gás para cima e segura a subida do cano. Vem no fuzil.')
def freio_ak(A):
    q = A.base; L = 0.03; R = 0.0105
    c = torno_x([(0.0, 0.0), (R - 0.001, 0.0), (R, 0.001), (R, L), (0.0, L)], 40)
    q.add('aco_oxidado', menos(c, cil_x(0.0045, -0.01, L + 0.01, sec=24), cil_x(0.0072, -0.001, 0.012, sec=32),
                               caixa(L - 0.003, L + 0.02, 0.0, 0.03, -0.03, 0.03), caixa(0.012, 0.02, -0.003, 0.03, -0.003, 0.003)))
    q.add('aco_oxidado', solido(arred([(L - 0.003, 0.0), (L + 0.004, 0.0), (L + 0.004, -0.0104), (L - 0.003, -0.0104)], 0.001), -0.0086, 0.0086, 0.0006))   # lábio de baixo
    A.pivo = (0, 0, 0)


@_acessorio('supressor_762', 'Supressor 7,62', 'boca', 'boca_762', peso_kg=0.55, raridade='muito raro', valor_troca=95,
            modificadores={'ruido_m': 0.35, 'clarao': 0.05, 'recuo': 0.8}, onde=['quartel'],
            descricao='Supressor grosso de aço: o tiro é ouvido a 60 m em vez de 180. Esquenta rápido em rajada.')
def supressor_762(A):
    q = A.base; L = 0.19; R = 0.022
    tubo = torno_x([(0.0, -0.006), (R - 0.003, -0.006), (R, -0.003), (R, L - 0.004), (R - 0.004, L), (0.0, L)], 56)
    canais = []                                                                                         # 8 canais rasos na parte de tras
    for i in range(8):
        g = solido(arred([(0.028, -0.0022), (0.07, -0.0022), (0.07, 0.0022), (0.028, 0.0022)], 0.0021), R - 0.0012, R + 0.01)
        g.apply_transform(TF.rotation_matrix(i * math.pi / 4, [1, 0, 0])); canais.append(g)
    q.add('aco_oxidado', menos(tubo, cil_x(0.0045, -0.02, L + 0.01, sec=24), cil_x(0.0114, -0.01, 0.05, sec=40), *canais))
    q.add('recartilhado', tubo_x(R - 0.0002, R + 0.0006, 0.0, 0.018, sec=56))
    for x in (0.1, 0.104): q.add('aco_fosfatado', tubo_x(R - 0.0002, R + 0.0004, x, x + 0.0015, sec=56))   # emenda das duas partes
    A.pivo = (0, 0, 0)


def _montagem_lateral(q):
    """Braco que prende no trilho de cauda de andorinha (lado esquerdo) e sobe por cima da tampa, com alavanca de trava."""
    q.add('aco_oxidado', solido(arred([(-0.045, -0.009), (0.04, -0.009), (0.04, 0.009), (-0.045, 0.009)], 0.002), -0.006, 0.0, 0.001))      # sapata
    braco = arred([(-0.045, 0.004), (0.04, 0.004), (0.04, 0.042), (-0.045, 0.042)], 0.003)
    q.add('aco_oxidado', solido(braco, -0.008, -0.005, 0.001))
    q.add('aco_oxidado', solido(arred([(-0.045, 0.034), (0.04, 0.034), (0.04, 0.042), (-0.045, 0.042)], 0.002), -0.008, KW + 0.0045 + 0.012, 0.001))  # ponte por cima
    q.add('aco_oxidado', solido(arred([(-0.03, -0.004), (0.0, -0.004), (0.004, 0.0), (-0.03, 0.0)], 0.0015), -0.012, -0.008, 0.0006))     # alavanca de trava
    q.add('aco_inox', cil_z(0.0025, -0.0125, -0.0115, -0.03, -0.002, 16))


@_acessorio('mira_lateral_ak', 'Mira de ponto com montagem lateral', 'mira', 'trilho_lateral_ak', peso_kg=0.3, raridade='raro', valor_troca=60,
            modificadores={'precisao_mirando': 1.3, 'tempo_mirar': 0.8}, usa='pilhas', autonomia_min=20000, onde=['quartel'],
            linha_de_visada='encaixe "olho"', descricao='Montagem que prende no trilho do lado esquerdo e põe uma mira de ponto vermelho por cima da tampa.')
def mira_lateral_ak(A):
    q = A.base; _montagem_lateral(q)
    zc = KW + 0.0045                                                     # centro do fuzil, visto do trilho
    yc = 0.042 + 0.016
    q.add('aluminio_preto', torno_x([(0.0, -0.035), (0.013, -0.035), (0.0145, -0.033), (0.0145, 0.03), (0.0165, 0.034), (0.0165, 0.042), (0.0, 0.042)], 48, yc, zc))
    q.add('aluminio_preto', solido(arred([(-0.02, 0.042), (0.02, 0.042), (0.02, yc - 0.01), (-0.02, yc - 0.01)], 0.002), zc - 0.008, zc + 0.008, 0.001))
    q.add('lente', cil_x(0.0125, -0.0335, -0.033, yc, zc, 40)); q.add('lente', cil_x(0.0148, 0.0405, 0.041, yc, zc, 40))
    q.add('ponto_vermelho', cil_x(0.0005, 0.04, 0.0402, yc, zc, 8))
    q.add('recartilhado', _cil_y(0.0055, yc + 0.0135, yc + 0.019, 0.0, zc, 24))
    A.encaixe('olho', (-0.035, yc, zc), 'mira', descricao='linha de visada'); A.pivo = (0, 0, 0)


@_acessorio('luneta_lateral_ak', 'Luneta 4× com montagem lateral', 'mira', 'trilho_lateral_ak', peso_kg=0.6, raridade='muito raro', valor_troca=100, aumento=4,
            modificadores={'precisao_mirando': 1.55, 'tempo_mirar': 1.15, 'alcance_m': 1.6}, onde=['quartel'], linha_de_visada='encaixe "olho"; 4×',
            descricao='Luneta curta de 4× com retículo em divisa, presa na montagem do lado esquerdo.')
def luneta_lateral_ak(A):
    q = A.base; _montagem_lateral(q)
    zc = KW + 0.0045; yc = 0.042 + 0.019
    perf = [(0.0, -0.09), (0.019, -0.09), (0.0205, -0.087), (0.0205, -0.05), (0.0135, -0.035), (0.0135, 0.04), (0.019, 0.055), (0.0195, 0.098), (0.0, 0.098)]
    q.add('aluminio_preto', torno_x(perf, 48, yc, zc))
    q.add('recartilhado', tubo_x(0.0, 0.0212, -0.084, -0.066, yc, zc, sec=48))
    q.add('lente', cil_x(0.0175, -0.0905, -0.09, yc, zc, 40)); q.add('lente', cil_x(0.018, 0.0975, 0.098, yc, zc, 40))
    q.add('recartilhado', _cil_y(0.0065, yc + 0.0135, yc + 0.0215, 0.0, zc, 24))                          # botao de altura
    q.add('recartilhado', cil_z(0.0065, zc + 0.0135, zc + 0.0215, 0.0, yc, 24))                           # botao lateral
    A.encaixe('olho', (-0.092, yc, zc), 'mira', descricao='linha de visada'); A.pivo = (0, 0, 0)


@_acessorio('baioneta_ak', 'Baioneta (fuzil 7,62)', 'baioneta', 'baioneta_ak', peso_kg=0.32, raridade='incomum', valor_troca=18, dano_corpo=40,
            modificadores={'tempo_mirar': 1.05}, onde=['quartel'],
            descricao='Lâmina de 150 mm com anel que encaixa no cano e cabo de polímero: golpe de estocada sem gastar munição.')
def baioneta_ak(A):
    q = A.base
    lam = suave([(0.0, -0.002), (0.15, -0.002), (0.162, 0.002), (0.15, 0.008), (0.0, 0.008)], 2)
    q.add('aco_inox', solido(Polygon(lam), -0.0018, 0.0018, 0.0012))
    q.add('aco_oxidado', caixa(0.0, 0.11, 0.0055, 0.008, -0.0021, 0.0021))                                        # dorso
    q.add('aco_oxidado', tubo_x(0.0076, 0.0095, -0.012, -0.002, 0.0095, 0.0, sec=32))                              # anel do cano
    q.add('aco_oxidado', caixa(-0.012, 0.0, -0.004, 0.006, -0.004, 0.004))                                       # guarda
    cabo = suave([(-0.012, 0.0), (-0.1, 0.002), (-0.112, -0.002), (-0.112, -0.016), (-0.1, -0.02), (-0.012, -0.014)], 3)
    q.add('madeira_ak', corpo_x(cabo, -0.012, -0.112, lambda x: 0.008, n=2.4, fatias=60, voltas=36))
    A.pivo = (0, 0, 0)


@_acessorio('carregador_762_30', 'Carregador 7,62 (30)', 'carregador', 'carregador_762', capacidade=30, municao='municao_762', peso_kg=0.33,
            raridade='incomum', valor_troca=12, modificadores={}, onde=['quartel', 'delegacia', 'fabrica'], descricao='Carregador curvo de aço, 30 tiros.')
def carregador_762_30(A): _carregador_ak(A.base, 30); A.pivo = (KMAG_X, KMAG_Y, 0)


@_acessorio('carregador_762_40', 'Carregador 7,62 (40)', 'carregador', 'carregador_762', capacidade=40, municao='municao_762', peso_kg=0.42,
            raridade='raro', valor_troca=24, modificadores={'recarga_s': 1.08}, onde=['quartel'], descricao='Carregador longo de polímero preto, 40 tiros.')
def carregador_762_40(A): _carregador_ak(A.base, 40, 'polimero'); A.pivo = (KMAG_X, KMAG_Y, 0)


@_acessorio('tambor_762_75', 'Tambor 7,62 (75)', 'carregador', 'carregador_762', capacidade=75, municao='municao_762', peso_kg=1.0,
            raridade='muito raro', valor_troca=70, modificadores={'recarga_s': 1.5, 'tempo_mirar': 1.2}, onde=['quartel'],
            descricao='Tambor de 75 com chave de corda na frente: muito tiro, muito peso.')
def tambor_762_75(A): _tambor_ak(A.base); A.pivo = (KMAG_X, KMAG_Y, 0)


@arma('municao_762', 'Cartucho 7,62×39', 'municao', 'municao', calibre='7,62×39', peso_kg=0.016, empilha=60, raridade='incomum', estojo='estojo_762',
      onde=['quartel', 'delegacia', 'fabrica'], descricao='Cartucho de estojo de aço laqueado verde e ponta de cobre.')
def municao_762(A): A.base.merge(_cartucho_762(24), TF.translation_matrix([-0.028, 0.0056, 0])); A.pivo = (0, 0, 0)


@arma('estojo_762', 'Estojo 7,62×39 (vazio)', 'municao', 'estojo', calibre='7,62×39', peso_kg=0.007, empilha=100, raridade='comum',
      descricao='Estojo de aço deflagrado: cai do fuzil. Aço não vale recarregar, mas serve de sucata.')
def estojo_762(A): A.base.merge(_cartucho_762(20, vazio=True), TF.translation_matrix([-0.0194, 0, 0])); A.pivo = (0, 0, 0)


CX762 = dict(x0=-0.045, x1=0.045, y0=0.0, y1=0.062, z0=-0.03, z1=0.03)
ATLAS762 = {'topo': (0, 0), 'lado+': (0, 250), 'lado-': (0, 520), 'ponta+': (380, 250), 'ponta-': (380, 520)}


@arma('caixa_municao_762', 'Caixa de munição 7,62×39 (20)', 'municao', 'caixa', calibre='7,62×39', municao='municao_762', quantidade=20,
      peso_kg=0.36, empilha=6, raridade='raro', onde=['quartel', 'fabrica'],
      descricao='Caixa de papelão com bandeja de 20 cartuchos 7,62 em pé. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_762(A):
    caixa_municao(A, 'rotulo_762', CX762, _arte_caixa(CX762, '7,62×39', '20 CARTUCHOS', 'ESTOJO DE AÇO 123 gr', cor=(110, 40, 30), atlas=ATLAS762),
                  _cartucho_762(12), 5, 4, 0.0158, 0.0126, faltam=(3, 11), bandeja=0.036, atlas=ATLAS762)


# ---------------------------------------------------------------------------- pecas modulares (como no video do Bruno)
def _desloca(A, d):
    """Move tudo de um acessorio desenhado nas coordenadas do fuzil para a origem do encaixe (d = -encaixe)."""
    T = TF.translation_matrix(d)
    for q in [A.base] + [p['peca'] for p in A.partes]:
        for ms in q.parts.values():
            for m in ms: m.apply_transform(T)
    for p in A.partes: p['origem'] = list(np.array(p['origem']) + d)
    for e in A.encaixes: e['pos'] = list(np.array(e['pos']) + d)
    A.pivo = (0, 0, 0)


GM_BAIXO = arred([(0.2, -0.035), (0.25, -0.0365), (0.36, -0.0365), (0.385, -0.035), (0.39, -0.022), (0.39, 0.006), (0.2, 0.006), (0.195, -0.022)], 0.004)
GM_FURO = lambda: [cil_x(0.0098, 0.15, 0.45, -0.006, 0, 32), cil_x(0.0032, 0.15, 0.45, -0.0175, 0, 12)]   # cano e vareta


def _gm_cima(mat, q):
    q.add(mat, menos(torno_x([(0.0, 0.205), (0.0112, 0.21), (0.0118, 0.23), (0.0118, 0.37), (0.0105, 0.385), (0.0, 0.385)], 40, 0.018, 0.0),
                     cil_x(0.0088, 0.19, 0.4, 0.018, 0, 36), caixa(0.19, 0.4, -0.02, 0.012, -0.02, 0.02)))


@_acessorio('guarda_mao_madeira_ak', 'Guarda-mão de madeira (fuzil 7,62)', 'guarda_mao', 'guarda_mao_ak', peso_kg=0.25, raridade='comum', valor_troca=8,
            modificadores={}, onde=['quartel', 'fabrica'], descricao='Guarda-mão de madeira envernizada com apoio de dedos. Vem no fuzil.')
def guarda_mao_madeira_ak(A):
    q = A.base
    baixo = menos(punho_x(GM_BAIXO, 0.0175), *GM_FURO())
    for zs in (-1, 1): baixo = menos(baixo, solido(arred([(0.215, -0.0115), (0.37, -0.0115), (0.37, -0.0075), (0.215, -0.0075)], 0.001),
                                                   min(zs * 0.0162, zs * 0.021), max(zs * 0.0162, zs * 0.021)))   # sulco do polegar
    q.add('madeira_ak', baixo); _gm_cima('madeira_ak', q)
    _desloca(A, -np.array(GM0))


@_acessorio('guarda_mao_polimero_ak', 'Guarda-mão de polímero com nervuras', 'guarda_mao', 'guarda_mao_ak', peso_kg=0.2, raridade='incomum', valor_troca=12,
            modificadores={'precisao_rajada': 1.05}, onde=['quartel'], descricao='Guarda-mão preto de polímero com nervuras horizontais para a mão não escorregar.')
def guarda_mao_polimero_ak(A):
    q = A.base
    q.add('polimero', menos(punho_x(GM_BAIXO, 0.0175), *GM_FURO()))
    for zs in (-1, 1):
        for y in np.arange(-0.03, -0.001, 0.0032):
            q.add('polimero', solido(arred([(0.24, y), (0.375, y), (0.375, y + 0.0013), (0.24, y + 0.0013)], 0.0006),
                                     min(zs * 0.0165, zs * 0.0182), max(zs * 0.0165, zs * 0.0182)))
    _gm_cima('polimero', q)
    _desloca(A, -np.array(GM0))


@_acessorio('guarda_mao_trilhos_ak', 'Guarda-mão de quatro trilhos', 'guarda_mao', 'guarda_mao_ak', peso_kg=0.38, raridade='raro', valor_troca=30,
            modificadores={'recuo': 0.97}, onde=['quartel'],
            descricao='Caixa de alumínio que envolve cano e tubo de gás, com trilhos em cima, embaixo e dos lados e furos de ventilação.')
def guarda_mao_trilhos_ak(A):
    q = A.base; X0, X1 = 0.198, 0.39
    sec = arred([(-0.019, -0.038), (0.019, -0.038), (0.019, 0.029), (-0.019, 0.029)], 0.006)
    corpo = menos(ext_x(sec, X0, X1), ext_x(sec.buffer(-0.002), X0 - 0.01, X1 + 0.01))
    furos = []
    for x in np.arange(X0 + 0.018, X1 - 0.012, 0.022):
        for y in (-0.024, -0.006, 0.012): furos.append(cil_z(0.0042, -0.03, 0.03, x, y, 16))
    q.add('aluminio_preto', menos(corpo, *furos))
    trilho(q, 'aluminio_preto', X0 + 0.004, X1 - 0.004, 0.029, False)
    trilho(q, 'aluminio_preto', X0 + 0.004, X1 - 0.004, -0.038, True)
    for zs in (-1, 1):
        lado = P(); trilho(lado, 'aluminio_preto', X0 + 0.02, X1 - 0.004, 0.0, False)
        R = TF.translation_matrix([0, -0.0045, zs * 0.019]) @ TF.rotation_matrix(zs * math.pi / 2, [1, 0, 0])
        for k, ms in lado.parts.items():
            for m in ms: q.add(k, m.apply_transform(R))
    _desloca(A, -np.array(GM0))


@_acessorio('tampa_trilho_ak', 'Tampa com trilho (fuzil 7,62)', 'tampa', 'tampa_ak', peso_kg=0.22, raridade='raro', valor_troca=28, modificadores={},
            onde=['quartel'], descricao='Tampa do receptor reforçada, travada na frente e atrás, com trilho em cima para mira ou luneta (encaixe_mira_tampa).')
def tampa_trilho_ak(A):
    q = A.base; _tampa_ak(q)
    q.add('aco_oxidado', solido(arred([(KX0 + 0.004, KTAMPA - 0.004), (KX1 - 0.026, KTAMPA - 0.004), (KX1 - 0.026, KTAMPA), (KX0 + 0.004, KTAMPA)], 0.001),
                                -0.0095, 0.0095, 0.0006))
    trilho(q, 'aco_oxidado', KX0 + 0.008, KX1 - 0.03, KTAMPA, False)
    q.add('aco_oxidado', solido(arred([(KX1 - 0.03, KY1 + 0.002), (KX1 - 0.012, KY1 + 0.002), (KX1 - 0.012, KY1 + 0.012), (KX1 - 0.03, KTAMPA)], 0.002),
                                -0.0098, 0.0098, 0.001))                                                      # trava da frente no bloco da alca
    _desloca(A, -np.array(TAMPA0))


@_acessorio('coronha_polimero_ak', 'Coronha de polímero (fuzil 7,62)', 'coronha', 'coronha_ak', peso_kg=0.5, raridade='incomum', valor_troca=14,
            modificadores={'recuo': 0.65, 'precisao': 1.3}, onde=['quartel', 'fabrica'],
            descricao='Coronha fixa de polímero preto com rebaixo dos lados (mais leve que a de madeira) e soleira de borracha.')
def coronha_polimero_ak(A):
    q = A.base
    perfil = suave([(0.0, 0.012), (-0.03, 0.012), (-0.2, 0.0), (-0.33, -0.012), (-0.338, -0.016), (-0.342, -0.14), (-0.334, -0.148),
                    (-0.3, -0.142), (-0.18, -0.098), (-0.06, -0.05), (-0.01, -0.036), (0.0, -0.035)], 3)
    larg = lambda x: 0.012 + 0.008 * GT.smooth(-0.01, -0.22, x)
    corpo = corpo_x(perfil, 0.0, -0.345, larg, n=2.4, fatias=150, voltas=56, raio_tras=0.004, raio_frente=0.0015)
    furo = LineString([(-0.12, -0.03), (-0.28, -0.05)]).buffer(0.011, cap_style=1)
    rebaixo = [solido(furo, 0.0168, 0.05), solido(furo, -0.05, -0.0168)]
    q.add('polimero', menos(inter([corpo, caixa(-0.33, 0.01, -1, 1, -1, 1)]), *rebaixo))
    q.add('borracha', inter([corpo_x(perfil, 0.0, -0.345, lambda x: larg(x) + 0.0004, n=2.4, fatias=150, voltas=56, raio_tras=0.004), caixa(-0.36, -0.3295, -1, 1, -1, 1)]))
    q.add('aco_oxidado', caixa(-0.006, 0.006, -0.036, 0.013, -0.0125, 0.0125))
    A.encaixe('ombro', (-0.342, -0.07, 0), 'efeito', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


@_acessorio('coronha_retratil_ak', 'Coronha retrátil com adaptador (fuzil 7,62)', 'coronha', 'coronha_ak', peso_kg=0.55, raridade='raro', valor_troca=30,
            modificadores={'recuo': 0.68, 'precisao': 1.28}, posicoes=5, onde=['quartel'],
            descricao='Adaptador de aço que recebe o tubo e a coronha retrátil de 5 posições (a mesma do fuzil 5,56). Nó "soleira", animações estender/recolher.')
def coronha_retratil_ak(A):
    coronha_retratil_12(A); _adaptador_ak(A)


@_acessorio('compensador_ak', 'Freio de três câmaras (7,62)', 'boca', 'boca_762', peso_kg=0.12, raridade='raro', valor_troca=30,
            modificadores={'recuo': 0.72, 'ruido_m': 1.1}, onde=['quartel'],
            descricao='Freio grosso de três janelas e coroa dentada: corta muito o coice, mas faz mais barulho para quem está do lado.')
def compensador_ak(A):
    q = A.base; L = 0.072; R = 0.0125
    c = torno_x([(0.0, 0.0), (R - 0.0015, 0.0), (R, 0.0015), (R, L - 0.0015), (R - 0.0015, L), (0.0, L)], 48)
    cortes = [cil_x(0.0048, -0.01, L + 0.01, sec=24), cil_x(0.0072, -0.001, 0.012, sec=32)]
    for k in range(3):
        x = 0.018 + k * 0.017
        cortes.append(solido(arred([(x, -0.0085), (x + 0.011, -0.0085), (x + 0.011, 0.0085), (x, 0.0085)], 0.002), -0.03, 0.03))
    for i in range(6):
        g = caixa(L - 0.005, L + 0.01, -0.0018, 0.0018, 0.0, 0.03); g.apply_transform(TF.rotation_matrix(i * math.pi / 3, [1, 0, 0])); cortes.append(g)
    q.add('aco_oxidado', menos(c, *cortes))
    A.pivo = (0, 0, 0)


# ---------------------------------------------------------------------------- acessorios que servem no 5,56 e na AK (fotos do Bruno)
def _mira_polimero(A, frente):
    """Mira rebativel de polimero: caixa comprida com mola aparente, tambor de ajuste lateral na alca e a mesma linha de visada
    das miras de aluminio (centro do furo / ponta do poste em y = 0,0195)."""
    q = A.base; L = 0.036
    q.add('polimero', solido(arred([(-L / 2, -0.0005), (L / 2, -0.0005), (L / 2 - 0.004, 0.0075), (-L / 2 + 0.004, 0.008)], 0.002), -0.0105, 0.0105, 0.0012))
    for zs in (-1, 1): q.add('polimero', caixa(-L / 2 + 0.003, L / 2 - 0.003, -0.0058, 0.0, min(zs * 0.0106, zs * 0.013), max(zs * 0.0106, zs * 0.013)))
    q.add('aco_oxidado', torno_x([(0.0, 0.0), (0.0042, 0.0), (0.0042, 0.0016), (0.0, 0.0016)], 20).apply_transform(
        TF.rotation_matrix(math.pi / 2, [0, 1, 0])).apply_translation([L / 2 - 0.008, -0.002, 0.0135]))          # parafuso da garra
    q.add('aco_oxidado', caixa(L / 2 - 0.0085, L / 2 - 0.0075, -0.0058, 0.0018, 0.0148, 0.0152))
    for i in range(5):                                                                                       # mola aparente
        m = trimesh.creation.annulus(r_min=0.0022, r_max=0.003, height=0.0007, sections=16); m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1]))
        m.apply_translation([-0.003 + i * 0.0012, 0.006, 0]); q.add('mola', m)
    q.add('aco_inox', cil_z(0.0015, -0.0108, 0.0108, -0.006, 0.006, 12))
    pa = A.parte('lamina', (-0.006, 0.006, 0), explodir=(0, 0.03, 0), tipo='gira', eixo='z', curso_graus=-85 if frente else 85, descricao='rebate (mola)')
    if frente:
        lam = arred([(-0.01, 0.005), (-0.002, 0.005), (-0.002, 0.0215), (-0.003, 0.025), (-0.009, 0.025), (-0.01, 0.0215)], 0.0012)
        pa.add('polimero', menos(solido(lam, -0.0085, 0.0085, 0.001), solido(arred([(-0.02, 0.0095), (0.01, 0.0095), (0.01, 0.03), (-0.02, 0.03)], 0.002), -0.006, 0.006),
                                 cil_z(0.0022, -0.02, 0.02, -0.006, 0.0075, 12)))
        pa.add('aco_oxidado', caixa(-0.0072, -0.0048, 0.009, 0.0195, -0.0011, 0.0011))
        pa.add('tinta_branca', caixa(-0.0073, -0.0047, 0.0185, 0.0196, -0.0005, 0.0005))
    else:
        lam = arred([(-0.01, 0.005), (-0.002, 0.005), (-0.002, 0.0245), (-0.01, 0.0245)], 0.0012)
        pa.add('polimero', menos(solido(lam, -0.009, 0.009, 0.001), cil_x(0.0022, -0.02, 0.01, 0.0195, 0, 20),
                                 torno_x([(0.0, -0.0145), (0.0045, -0.0145), (0.0022, -0.0115), (0.0, -0.0115)], 24, 0.0195, 0.0),
                                 solido(Polygon([(-0.0095, 0.008), (-0.0025, 0.008), (-0.006, 0.014)]), -0.02, 0.02)))     # janela triangular
        pa.add('recartilhado', cil_z(0.0048, 0.009, 0.0135, -0.006, 0.012, 24))                                 # tambor de ajuste
        pa.add('polimero', cil_z(0.0032, 0.0135, 0.0142, -0.006, 0.012, 20))
    A.anim('dobrar', 0.2, [('lamina', 'r', (0, 0, 1), pose([(0, 0), (0.2, -85 if frente else 85)]))], desc='rebate a mira')
    A.pivo = (0, 0, 0)


@_acessorio('alca_polimero', 'Alça rebatível de polímero', 'mira', 'alca_trilho', peso_kg=0.03, raridade='incomum', valor_troca=10, modificadores={},
            descricao='Alça de furo de polímero com mola (deita e levanta sozinha) e tambor de ajuste lateral.')
def alca_polimero(A): _mira_polimero(A, False)


@_acessorio('massa_polimero', 'Massa rebatível de polímero', 'mira', 'massa_trilho', peso_kg=0.025, raridade='incomum', valor_troca=8, modificadores={},
            descricao='Massa de polímero com mola e orelhas que protegem o poste.')
def massa_polimero(A): _mira_polimero(A, True)


@_acessorio('alca_polimero_tan', 'Alça rebatível de polímero (caramelo)', 'mira', 'alca_trilho', peso_kg=0.03, raridade='incomum', valor_troca=10, modificadores={},
            descricao='A mesma alça de polímero, em caramelo.')
def alca_polimero_tan(A): _mira_polimero(A, False); _em_tan(A, {'polimero': 'polimero_tan'})


@_acessorio('massa_polimero_tan', 'Massa rebatível de polímero (caramelo)', 'mira', 'massa_trilho', peso_kg=0.025, raridade='incomum', valor_troca=8, modificadores={},
            descricao='A mesma massa de polímero, em caramelo.')
def massa_polimero_tan(A): _mira_polimero(A, True); _em_tan(A, {'polimero': 'polimero_tan'})


def _empunhadura_reta(A):
    """Empunhadura vertical curta e reta: secao retangular arredondada, painel texturizado dos lados, nervuras atras, porcas da garra."""
    q = A.base; _base_mlok(q, 0.034)
    q.add('polimero', solido(arred([(-0.018, -0.004), (0.018, -0.004), (0.018, -0.011), (-0.018, -0.011)], 0.002), -0.0112, 0.0112, 0.0012))
    cont = suave([(-0.015, -0.01), (0.016, -0.01), (0.0145, -0.04), (0.0135, -0.07), (0.011, -0.076), (-0.011, -0.076), (-0.0135, -0.07), (-0.0145, -0.04)], 3)
    lg = lambda y: 0.0108 - 0.0006 * GT.smooth(-0.01, -0.07, y)
    q.add('polimero', punho_redondo(cont, -0.01, -0.076, lg, n=3.2, fatias=70, voltas=48, raio_base=0.004))
    pan = punho_redondo(cont, -0.01, -0.076, lambda y: lg(y) + 0.0005, n=3.2, fatias=70, voltas=48, raio_base=0.004)
    q.add('polimero_grip', inter([pan, solido(arred([(-0.009, -0.024), (0.011, -0.024), (0.011, -0.066), (-0.009, -0.066)], 0.005), -0.05, 0.05)]))
    for y in np.arange(-0.05, -0.07, -0.004): q.add('polimero', inter([pan.copy(), caixa(-0.03, -0.012, y - 0.0012, y, -1, 1)]))
    for x in (-0.004, 0.004):
        q.add('aco_oxidado', torno_x([(0.0, 0.0), (0.003, 0.0), (0.003, 0.0018), (0.0, 0.0018)], 6).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0]))
              .apply_translation([0.0, -0.0075, 0.0112]).apply_translation([x, 0, 0]))
    A.pivo = (0, 0, 0)


@_acessorio('empunhadura_reta', 'Empunhadura vertical curta', 'empunhadura', 'mlok_baixo', peso_kg=0.07, raridade='incomum', valor_troca=12,
            modificadores={'recuo': 0.87, 'precisao_rajada': 1.2}, onde=['quartel', 'delegacia'],
            descricao='Empunhadura reta e curta, com painel áspero dos lados e nervuras atrás; presa por duas porcas.')
def empunhadura_reta(A): _empunhadura_reta(A)


@_acessorio('empunhadura_reta_tan', 'Empunhadura vertical curta (caramelo)', 'empunhadura', 'mlok_baixo', peso_kg=0.07, raridade='incomum', valor_troca=12,
            modificadores={'recuo': 0.87, 'precisao_rajada': 1.2}, onde=['quartel'], descricao='A mesma empunhadura curta, em caramelo.')
def empunhadura_reta_tan(A): _empunhadura_reta(A); _em_tan(A)


def _coronha_leve(A):
    """Coronha leve de polimero sobre tubo: caixa do tubo em cima, parte de baixo angulosa vazada, alavanca, tomada QD e soleira de borracha."""
    q = A.base
    q.add('aluminio_preto', cil_x(0.0145, -0.2, -0.012, 0, 0, 48))
    q.add('aco_oxidado', torno_x([(0.0, -0.013), (0.0168, -0.013), (0.0168, -0.003), (0.0, -0.003)], 48))
    sol = A.parte('soleira', (0, 0, 0), explodir=(-0.08, 0, 0), tipo='desliza', curso_m=-0.064, descricao='corre no tubo, 5 posições de 16 mm')
    perfil = arred([(-0.085, 0.019), (-0.245, 0.021), (-0.25, 0.016), (-0.25, -0.112), (-0.236, -0.118), (-0.214, -0.112), (-0.17, -0.042),
                    (-0.12, -0.028), (-0.085, -0.022)], 0.006)
    larg = lambda x: 0.0175 + 0.0015 * GT.smooth(-0.1, -0.2, x)
    corpo = corpo_x(perfil, -0.085, -0.25, larg, n=3.4, fatias=110, voltas=48, raio_tras=0.003, raio_frente=0.004)
    janelas = [solido(arred([(-0.226, -0.03), (-0.214, -0.03), (-0.214, -0.098), (-0.226, -0.098)], 0.004), -0.05, 0.05),
               solido(Polygon([(-0.205, -0.03), (-0.205, -0.085), (-0.175, -0.035)]).buffer(0.002), -0.05, 0.05),
               solido(arred([(-0.15, -0.028), (-0.118, -0.024), (-0.118, -0.018), (-0.15, -0.02)], 0.002), -0.05, 0.05)]
    sol.add('polimero', menos(corpo, cil_x(0.0148, -0.3, -0.06, 0, 0, 48), *janelas))
    for y in np.arange(-0.04, -0.11, -0.006):                                                              # nervuras na frente da parte de baixo
        x = -0.214 + (y + 0.112) * 0.62
        sol.add('polimero', inter([corpo_x(perfil, -0.085, -0.25, lambda x_: larg(x_) + 0.0006, n=3.4, fatias=110, voltas=48), caixa(x - 0.006, x + 0.004, y - 0.0012, y, -1, 1)]))
    pad = arred([(-0.262, 0.024), (-0.248, 0.024), (-0.248, -0.118), (-0.262, -0.122)], 0.005)
    sol.add('borracha', solido(pad, -0.0195, 0.0195, 0.004))
    for y in np.arange(0.016, -0.11, -0.008): sol.add('borracha', caixa(-0.2635, -0.2615, y - 0.0015, y, -0.017, 0.017))
    sol.add('aco_oxidado', solido(arred([(-0.15, -0.03), (-0.11, -0.03), (-0.106, -0.036), (-0.15, -0.036)], 0.002), -0.006, 0.006, 0.0008))   # alavanca
    for zs in (-1, 1): sol.add('aco_oxidado', torno_x([(0.0045, 0.0), (0.0045, 0.002)], 24).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0]))
                               .apply_translation([-0.205, -0.06, zs * (larg(-0.205) - 0.0004)]))           # tomada QD
    A.anim('estender', 0.5, [('soleira', 't', pose([(0, (0, 0, 0)), (0.5, (-0.064, 0, 0))]))], desc='abre a coronha até a última posição')
    A.anim('recolher', 0.5, [('soleira', 't', pose([(0, (-0.064, 0, 0)), (0.5, (0, 0, 0))]))], desc='fecha a coronha')
    A.encaixe('ombro', (-0.262, -0.05, 0), 'efeito', pai='soleira', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


_LEVE = dict(peso_kg=0.3, raridade='raro', valor_troca=28, modificadores={'recuo': 0.66, 'precisao': 1.3}, posicoes=5, onde=['quartel'])


@_acessorio('coronha_leve_ar', 'Coronha leve vazada (fuzil 5,56)', 'coronha', 'coronha_ar', descricao='Coronha leve de polímero com parte de baixo vazada e soleira de borracha; corre no tubo em 5 posições.', **_LEVE)
def coronha_leve_ar(A): _coronha_leve(A)


@_acessorio('coronha_leve_ar_tan', 'Coronha leve vazada caramelo (fuzil 5,56)', 'coronha', 'coronha_ar', descricao='A mesma coronha leve, em caramelo.', **_LEVE)
def coronha_leve_ar_tan(A): _coronha_leve(A); _em_tan(A, {'polimero': 'polimero_tan'})


def _adaptador_ak(A):
    _desloca(A, np.array([-0.032, 0.0, 0.0]))
    q = A.base
    q.add('aco_oxidado', caixa(-0.008, 0.006, -0.036, 0.013, -0.0125, 0.0125))
    q.add('aco_oxidado', solido(arred([(-0.034, -0.016), (-0.006, -0.02), (-0.006, 0.014), (-0.034, 0.016)], 0.003), -0.016, 0.016, 0.002))
    q.add('aco_oxidado', solido(arred([(-0.024, -0.02), (-0.012, -0.02), (-0.012, -0.034), (-0.024, -0.034)], 0.002), -0.006, 0.006, 0.0008))


@_acessorio('coronha_leve_ak', 'Coronha leve vazada com adaptador (fuzil 7,62)', 'coronha', 'coronha_ak', descricao='Adaptador de aço com a coronha leve vazada.', **_LEVE)
def coronha_leve_ak(A): _coronha_leve(A); _adaptador_ak(A)


@_acessorio('coronha_leve_ak_tan', 'Coronha leve vazada caramelo com adaptador (fuzil 7,62)', 'coronha', 'coronha_ak', descricao='Adaptador com a coronha leve caramelo.', **_LEVE)
def coronha_leve_ak_tan(A): _coronha_leve(A); _em_tan(A, {'polimero': 'polimero_tan'}); _adaptador_ak(A)


# o 5,56 tambem aceita os acessorios novos
NOVOS.setdefault('encaixe_coronha', []).extend(['coronha_leve_ar', 'coronha_leve_ar_tan'])
NOVOS.setdefault('encaixe_empunhadura', []).extend(['empunhadura_reta', 'empunhadura_reta_tan'])
NOVOS.setdefault('encaixe_alca', []).extend(['alca_polimero', 'alca_polimero_tan'])
NOVOS.setdefault('encaixe_massa', []).extend(['massa_polimero', 'massa_polimero_tan'])
NOVOS.setdefault('encaixe_mira', []).append('mira_reflexa')


# ---------------------------------------------------------------------------- versao tatica (foto de referencia do Bruno, so inspiracao)
@_acessorio('carregador_762_30_grade', 'Carregador 7,62 de polímero (30)', 'carregador', 'carregador_762', capacidade=30, municao='municao_762', peso_kg=0.25,
            raridade='incomum', valor_troca=14, onde=['quartel'], descricao='Carregador preto de polímero com quadros em relevo dos lados: mais leve que o de aço.')
def carregador_762_30_grade(A): _carregador_ak(A.base, 30, 'polimero', grade=True); A.pivo = (KMAG_X, KMAG_Y, 0)


@_acessorio('coronha_esqueleto_ak', 'Coronha vazada fixa (fuzil 7,62)', 'coronha', 'coronha_ak', peso_kg=0.42, raridade='raro', valor_troca=24,
            modificadores={'recuo': 0.68, 'precisao': 1.28}, onde=['quartel'],
            descricao='Coronha fixa de polímero com o miolo vazado em triângulo, apoio de rosto reto, soleira de borracha e furo de bandoleira.')
def coronha_esqueleto_ak(A):
    q = A.base
    fora = suave([(0.0, 0.013), (-0.04, 0.013), (-0.285, 0.006), (-0.296, 0.004), (-0.298, -0.122), (-0.29, -0.13), (-0.27, -0.128),
                  (-0.05, -0.046), (-0.012, -0.037), (0.0, -0.036)], 2)
    vao = arred([(-0.075, -0.006), (-0.262, -0.006), (-0.262, -0.098), (-0.085, -0.036)], 0.006)
    q.add('polimero', solido(fora.difference(vao), -0.0155, 0.0155, 0.0045))
    for zs in (-1, 1):                                                                                   # rebaixo comprido do apoio de rosto
        q.add('polimero_grip', solido(arred([(-0.24, 0.0005), (-0.07, 0.003), (-0.07, 0.0065), (-0.24, 0.0045)], 0.0015),
                                      min(zs * 0.0154, zs * 0.0162), max(zs * 0.0154, zs * 0.0162), 0.0003))
    q.add('borracha', solido(arred([(-0.312, 0.006), (-0.296, 0.006), (-0.296, -0.132), (-0.312, -0.132)], 0.005), -0.017, 0.017, 0.004))   # soleira
    for y in np.arange(-0.12, 0.0, 0.008): q.add('borracha', caixa(-0.3135, -0.311, y, y + 0.003, -0.015, 0.015))                      # ranhuras da soleira
    q.add('polimero', menos(solido(arred([(-0.29, -0.06), (-0.27, -0.06), (-0.27, -0.035), (-0.29, -0.035)], 0.004), -0.017, 0.017, 0.002),
                            solido(arred([(-0.286, -0.056), (-0.274, -0.056), (-0.274, -0.039), (-0.286, -0.039)], 0.003), -0.03, 0.03)))   # furo da bandoleira
    q.add('aco_oxidado', caixa(-0.006, 0.006, -0.036, 0.013, -0.0125, 0.0125))                                                        # chapa que encaixa no receptor
    A.encaixe('ombro', (-0.312, -0.06, 0), 'efeito', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


@_acessorio('guarda_mao_fendas_ak', 'Guarda-mão de fendas (fuzil 7,62)', 'guarda_mao', 'guarda_mao_ak', peso_kg=0.3, raridade='raro', valor_troca=26,
            modificadores={'recuo': 0.98}, onde=['quartel'],
            descricao='Guarda-mão de polímero com fendas de encaixe, trilho curto embaixo e do lado direito (empunhadura e lanterna) e tampa do tubo de gás com janelas.')
def guarda_mao_fendas_ak(A):
    q = A.base
    baixo = menos(punho_x(GM_BAIXO, 0.0185, n=3.4), *GM_FURO())
    fendas = []
    for x0 in (0.215, 0.262, 0.309):                                                                    # fendas dos lados
        fendas.append(solido(arred([(x0, -0.022), (x0 + 0.036, -0.022), (x0 + 0.036, -0.014), (x0, -0.014)], 0.0038), -0.03, 0.03))
    for x0 in (0.215, 0.25): fendas.append(caixa(x0, x0 + 0.028, -0.05, -0.03, -0.004, 0.004))         # fendas de baixo
    q.add('polimero', menos(baixo, *fendas))
    trilho(q, 'aluminio_preto', 0.285, 0.386, -0.0362, True)
    lado = P(); trilho(lado, 'aluminio_preto', 0.31, 0.386, 0.0, False)
    R = TF.translation_matrix([0, -0.0045, 0.0182]) @ TF.rotation_matrix(math.pi / 2, [1, 0, 0])
    for k, ms in lado.parts.items():
        for m in ms: q.add(k, m.apply_transform(R))
    sec = arred([(-0.0125, 0.0062), (0.0125, 0.0062), (0.0125, 0.03), (-0.0125, 0.03)], 0.0065)       # tampa do tubo de gas (z, y)
    cima = menos(ext_x(sec, 0.205, 0.385), cil_x(0.0088, 0.19, 0.4, 0.018, 0, 36))
    janelas = [solido(arred([(x0, 0.014), (x0 + 0.04, 0.014), (x0 + 0.04, 0.022), (x0, 0.022)], 0.0038), -0.03, 0.03) for x0 in (0.235, 0.29)]
    q.add('polimero', menos(cima, *janelas))
    q.add('aluminio_preto', menos(ext_x(sec.buffer(0.0008), 0.372, 0.385), cil_x(0.0088, 0.3, 0.4, 0.018, 0, 36)))   # capa de metal da ponta
    _desloca(A, -np.array(GM0))


@_acessorio('mira_reflexa', 'Mira reflexa de tubo inclinado', 'mira', 'trilho_mira', peso_kg=0.28, raridade='muito raro', valor_troca=75,
            modificadores={'precisao_mirando': 1.3, 'tempo_mirar': 0.72}, onde=['quartel', 'delegacia'], linha_de_visada='encaixe "olho"',
            descricao='Mira de ponto com corpo baixo e janela redonda em capuz inclinado; o ponto acende sozinho (sem pilha).')
def mira_reflexa(A):
    q = A.base; yc = 0.033
    q.add('aluminio_preto', solido(arred([(-0.034, -0.0005), (0.03, -0.0005), (0.03, 0.009), (-0.034, 0.009)], 0.002), -0.0135, 0.0135, 0.001))   # base
    for zs in (-1, 1): q.add('aluminio_preto', caixa(-0.028, 0.026, -0.0058, 0.0, min(zs * 0.0106, zs * 0.0135), max(zs * 0.0106, zs * 0.0135)))
    for x in (-0.02, 0.014):                                                                            # porcas da braçadeira (esquerda)
        q.add('aco_oxidado', cil_z(0.0055, -0.0175, -0.0135, x, 0.002, 20))
        q.add('aco_oxidado', solido(arred([(x - 0.009, -0.003), (x + 0.009, -0.003), (x + 0.009, 0.004), (x - 0.009, 0.004)], 0.002), -0.0185, -0.0172, 0.0004))
    corpo = arred([(-0.034, 0.008), (0.006, 0.008), (0.006, 0.024), (-0.034, 0.02)], 0.004)
    q.add('aluminio_preto', solido(corpo, -0.0125, 0.0125, 0.002))                                    # corpo baixo (atras)
    cap = menos(cil_x(0.0185, 0.0, 0.032, yc, 0, 48), cil_x(0.0145, -0.01, 0.04, yc, 0, 48))
    cap = cap.apply_transform(TF.translation_matrix([0.016, yc, 0]) @ TF.rotation_matrix(math.radians(-8), [0, 0, 1]) @ TF.translation_matrix([-0.016, -yc, 0]))
    q.add('aluminio_preto', cap)                                                                       # capuz redondo inclinado
    q.add('aluminio_preto', solido(arred([(0.0, 0.008), (0.032, 0.008), (0.03, yc - 0.012), (0.002, yc - 0.012)], 0.003), -0.012, 0.012, 0.001))
    q.add('lente_clara', cil_x(0.0145, 0.026, 0.0275, yc, 0, 48))
    q.add('ponto_vermelho', caixa(0.0262, 0.0264, yc - 0.0004, yc + 0.0004, -0.0004, 0.0004))
    q.add('aco_oxidado', cil_z(0.005, 0.0125, 0.0155, -0.012, 0.016, 24))                             # botão de ajuste (direita)
    q.add('aco_oxidado', caixa(-0.0128, -0.0112, 0.0135, 0.0145, 0.0155, 0.0157))
    q.add('tinta_branca', caixa(0.012, 0.018, yc + 0.0145, yc + 0.0175, -0.004, 0.004))                # janela de luz em cima
    A.encaixe('olho', (-0.02, yc, 0), 'mira', descricao='linha de visada'); A.pivo = (0, 0, 0)


@_acessorio('elastico_ak', 'Tiras de borracha no guarda-mão', 'enfeite', 'guarda_mao_enfeite', peso_kg=0.01, raridade='comum', valor_troca=1, modificadores={},
            onde=['casa', 'armazem'], descricao='Duas tiras de câmara de pneu cruzadas no guarda-mão: seguram o fio da lanterna e marcam a arma de um sobrevivente.')
def elastico_ak(A):
    q = A.base
    for ang in (14, -14):                                                                               # duas tiras cruzadas em X
        anel = menos(cil_x(0.0215, -0.004, 0.004, 0.0, 0, 40), cil_x(0.0195, -0.01, 0.01, 0.0, 0, 40))
        anel.apply_scale([1, 1.62, 1])
        anel.apply_transform(TF.rotation_matrix(math.radians(ang), [0, 0, 1]))
        q.add('borracha_marrom', anel)
    A.pivo = (0, 0, 0)


CORES.update({'borracha_marrom': (58, 40, 30)}); METAL.update({'borracha_marrom': (0.0, 0.75)})


def fuzil_762_tatico(A):
    fuzil_762(A)
    _recolore(A.base, {'baquelite': 'polimero'})
    for pt in A.partes:
        if pt['no'] == 'carregador': pt['peca'].parts.clear(); _carregador_ak(pt['peca'], 30, 'polimero', grade=True)
    padrao = {'encaixe_tampa': 'tampa_trilho_ak', 'encaixe_mira_tampa': 'mira_reflexa', 'encaixe_guarda_mao': 'guarda_mao_fendas_ak',
              'encaixe_coronha': 'coronha_esqueleto_ak', 'encaixe_boca': 'supressor_762', 'encaixe_lanterna': 'lanterna_compacta',
              'encaixe_enfeite': 'elastico_ak'}
    for e in A.encaixes:
        if e['no'] in padrao: e['padrao'] = padrao[e['no']] + ('_gasto' if padrao[e['no']] in GASTOS else '')
        for i in list(e.get('aceita', [])):
            if i in GASTOS and i + '_gasto' not in e['aceita']: e['aceita'].append(i + '_gasto')
        if 'requer' in e:
            e['requer'] = {k: sorted(set(v if isinstance(v, list) else [v]) | {x + '_gasto' for x in (v if isinstance(v, list) else [v]) if x in GASTOS})
                           for k, v in e['requer'].items()}
    _desgasta(A); _rabisco_receptor(A.base)


REG['fuzil_762_tatico'] = dict(REG['fuzil_762'], id='fuzil_762_tatico', nome='Fuzil Brasa 7,62 tático', fn=fuzil_762_tatico, raridade='muito raro',
                               valor_troca=220, onde=['quartel'],
                               descricao='O mesmo fuzil todo preto e bem usado (pintura gasta, riscos, ferrugem e um rabisco na chapa): punho e '
                                         'carregador de polímero, coronha vazada, guarda-mão de fendas com tiras de borracha, tampa com trilho e '
                                         'mira reflexa, supressor e lanterna.')


# ---------------------------------------------------------------------------- desgaste de sobrevivente (texturas por script)
def _riscos(n, px, seed, qtd, comp, horiz=0.7):
    """Mascara de riscos finos (repete nas bordas para ladrilhar)."""
    rng = np.random.default_rng(seed); im = Image.new('L', (n, n), 0); d = ImageDraw.Draw(im)
    for _ in range(qtd):
        x, y = rng.uniform(0, n, 2); a = rng.normal(0, 0.35) if rng.random() < horiz else rng.uniform(0, math.pi)
        L = rng.uniform(0.3, 1.0) * comp * px; dx, dy = math.cos(a) * L, math.sin(a) * L
        cor = int(rng.uniform(90, 255)); w = 1 if rng.random() < 0.8 else 2
        for ox in (-n, 0, n):
            for oy in (-n, 0, n): d.line([(x + ox, y + oy), (x + dx + ox, y + dy + oy)], fill=cor, width=w)
    return np.asarray(im, np.float64) / 255.0


def _tex_gasto(seed, base, metal=True, px=1024, tile=0.16):
    """Pintura/oxidacao gasta: manchas de metal claro onde a mao esfrega, riscos, pontos de ferrugem e sujeira escura."""
    n = int(tile * px)
    gasto = GT.smooth(0.66, 0.8, GT.fbm(n, n, 0.02 * px, 5, seed))                       # manchas de desgaste
    risco = _riscos(n, px, seed + 1, 110, 0.03)
    sujo = GT.smooth(0.45, 0.85, GT.fbm(n, n, 0.012 * px, 4, seed + 2))
    poro = GT.smooth(0.25, 1.6, GT.noise(n, n, 0.0007 * px, 0.0007 * px, seed + 4))
    c = GT.rgb(CORES[base])[None, None]
    claro = GT.rgb((96, 95, 92) if metal else tuple(min(255, int(v * 1.5) + 12) for v in CORES[base]))[None, None]
    alb = c * (0.92 + 0.08 * poro[..., None])
    alb = GT.lerp(alb, claro, ((0.3 if metal else 0.15) * gasto + 0.45 * risco * (0.35 + 0.65 * gasto))[..., None].clip(0, 1))
    if metal:
        ferr = GT.smooth(0.8, 0.9, GT.fbm(n, n, 0.006 * px, 4, seed + 3)) * (1 - gasto)
        alb = GT.lerp(alb, GT.rgb((74, 50, 36))[None, None], (0.45 * ferr)[..., None])
    else: ferr = 0 * sujo
    alb = GT.lerp(alb, GT.rgb((52, 46, 38))[None, None], (0.22 * sujo * (1 - gasto))[..., None])
    hm = -0.00004 * risco + 0.00002 * poro + 0.00003 * ferr
    rough = (0.42 if metal else 0.7) + 0.25 * sujo - 0.15 * risco - 0.1 * gasto + 0.3 * ferr
    return alb, hm, rough, 1.0, 0.0002, tile, px


TEX_EXTRA += [('aco_gasto', lambda: _tex_gasto(401, 'aco_oxidado'), 0.7), ('polimero_gasto', lambda: _tex_gasto(402, 'polimero', False), 0.0),
              ('aluminio_gasto', lambda: _tex_gasto(403, 'aluminio_preto'), 0.6), ('cano_gasto', lambda: _tex_gasto(404, 'aco_cano', tile=0.1), 0.8)]
GASTO = {'aco_oxidado': 'aco_gasto', 'aco_fosfatado': 'aco_gasto', 'polimero': 'polimero_gasto', 'aluminio_preto': 'aluminio_gasto',
         'aco_cano': 'cano_gasto', 'baquelite': 'polimero_gasto'}


def _desgasta(A):
    _recolore(A.base, GASTO)
    for pt in A.partes: _recolore(pt['peca'], GASTO)


def _rabisco(txt, alt, seed=7):
    """Texto riscado a ponta de faca: letras finas, tortas e de tamanhos diferentes (poligonos no plano x, y; base em y = 0)."""
    rng = np.random.default_rng(seed); f = fonte(120, False); polys = []; x = 0.0; esc = alt / 120
    for ch in txt:
        if ch == ' ': x += 45 * esc; continue
        w = int(f.getlength(ch)) + 20; im = Image.new('L', (w, 170), 0); ImageDraw.Draw(im).text((10, 10), ch, font=f, fill=255)
        a = (np.asarray(im) > 128); rects = []
        for r in range(a.shape[0]):
            c = np.flatnonzero(np.diff(np.r_[0, a[r].astype(int), 0]))
            for c0, c1 in zip(c[::2], c[1::2]): rects.append(sbox(c0, -r - 1, c1, -r))
        g = unary_union(rects).simplify(1.2)
        g = affinity.translate(g, 0, 150); g = affinity.skew(g, xs=rng.uniform(-12, 4), origin=(0, 0))
        g = affinity.rotate(g, rng.uniform(-9, 9), origin='centroid'); s_ = rng.uniform(0.85, 1.12)
        g = affinity.scale(g, s_ * esc, s_ * esc, origin=(0, 0)); g = affinity.translate(g, x, rng.uniform(-0.08, 0.08) * alt)
        polys.append(g); x += (w - 14) * esc * s_
    return unary_union(polys)


def _rabisco_receptor(q, txt='NÃO DESISTA'):
    """Rabisco claro riscado no lado esquerdo do receptor (fino, quase rente a chapa)."""
    g = _rabisco(txt, 0.0075)
    b = g.bounds; g = affinity.translate(g, -b[0], -b[1]); b = g.bounds
    k = min(1.0, 0.046 / b[2]); g = affinity.scale(g, -k, k, origin=(0, 0))                             # lido de fora pelo lado esquerdo
    g = affinity.translate(g, 0.111, -0.0262)                                                            # em cima do reforco do poco
    q.add('risco_claro', solido(g, -KW - 0.00145, -KW - 0.00105))


CORES.update({'risco_claro': (150, 146, 136)}); METAL.update({'risco_claro': (0.8, 0.35)})


# versoes gastas (mesma peca com as texturas de desgaste) dos acessorios que vem no fuzil tatico
GASTOS = ['tampa_trilho_ak', 'mira_reflexa', 'guarda_mao_fendas_ak', 'coronha_esqueleto_ak', 'supressor_762', 'lanterna_compacta', 'carregador_762_30_grade']
for _i in GASTOS:
    _r = REG[_i]
    REG[_i + '_gasto'] = dict(_r, id=_i + '_gasto', nome=_r['nome'] + ' (gasto)', fn=(lambda f: (lambda A: (f(A), _desgasta(A))))(_r['fn']),
                              valor_troca=max(1, int(_r.get('valor_troca', 10) * 0.8)), descricao=_r.get('descricao', '') + ' Peça usada, com a pintura gasta.')
