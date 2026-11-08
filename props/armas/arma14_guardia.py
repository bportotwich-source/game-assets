# Arma 13: pistola de servico Guardia 9 mm (acao dupla/simples, armacao de aluminio cor de areia, ferrolho aberto em cima,
# cao externo, alavanca de desarmar o cao no ferrolho, trilho no guarda-po, cano com rosca) e seus acessorios.
# Executado por gerar_armas.py (plano de lado: x frente, y cima, z direita). Desenho proprio, inspirado na foto do Bruno.
CORES.update({'fde': (118, 106, 86), 'polimero_fde': (112, 100, 80), 'nylon_coldre': (58, 60, 54)})
METAL.update({'fde': (0.3, 0.5), 'polimero_fde': (0.0, 0.62), 'nylon_coldre': (0.0, 0.9)})
TEX_EXTRA += [('polimero_pontos_fde', lambda: _tex_pontos(431, 'polimero_fde'), 0.0)]

GL = 0.205                       # comprimento do ferrolho (x = 0 atras)
GY0, GY1, GW = -0.0135, 0.0162, 0.0098    # ferrolho: base, topo, meia largura
GC0, GC1 = 0.064, 0.187          # abertura de cima do ferrolho (o cano aparece)
GR = 0.0068                      # raio do cano (igual a rosca da Sentinela: aceita os mesmos acessorios de boca)
GCF = 0.034                      # curso do ferrolho
GCAO = 48                        # cao armado (graus, para tras)
GTRAVA = 55                      # alavanca de desarmar o cao (graus, para baixo)
GP_TRAVA = (0.019, 0.0062)       # eixo da alavanca (no ferrolho)
GP_CAO = (-0.007, -0.019)        # eixo do cao
GP_GAT = (0.071, -0.0195)        # pino do gatilho
G_AN = math.radians(17)
G_D = np.array([-math.sin(G_AN), -math.cos(G_AN)])     # eixo do carregador (desce e vai um pouco para tras)
G_N = np.array([-G_D[1], G_D[0]])                       # normal (frente)
G_T = np.array([0.02, -0.016])                          # topo do carregador (centro)
G_ML, G_MW, G_MZ = 0.112, 0.0154, 0.0088                # carregador: comprimento, meia largura (frente-tras), meia espessura
G_TRILHO = (0.166, -0.036)
def _contorno_cabo_g(fr=0.005, tr=0.0158, belly=0.0012, palma=0.0016, ytopo=-0.0245):
    """Contorno do cabo (vista de lado) a partir do eixo do carregador: frente com barriga leve, costas com apoio da palma."""
    f = lambda t, e=0.0: G_T + G_N * (G_MW + fr + e) + G_D * t
    c = lambda t, e=0.0: G_T - G_N * (G_MW + tr + e) + G_D * t
    tf = (G_T[1] + G_N[1] * (G_MW + fr) - ytopo) / -G_D[1]
    tc = (G_T[1] - G_N[1] * (G_MW + tr) - ytopo) / -G_D[1]
    pts = [f(tf), f(0.03), f(0.055, belly), f(0.08, belly * 0.5), f(0.104), f(G_ML + 0.0015, -0.0035), c(G_ML + 0.0015, -0.002),
           c(0.104, palma), c(0.088, palma), c(0.06), c(0.03), c(tc)]
    return suave([tuple(map(float, p)) for p in pts], 3)


CABO_G = _contorno_cabo_g()
G_YB = CABO_G.bounds[1]
LARG_NUC_G = lambda y: 0.0118
LARG_TALA_G = lambda y: 0.0118 + 0.0038 * GT.smooth(-0.029, -0.041, y) + 0.0006 * math.exp(-((y + 0.085) / 0.02) ** 2)


def _perfil_car_g(folga=0.0, extra=0.0):
    a = G_T - G_N * G_MW; b = G_T + G_N * G_MW; L = G_ML + extra
    return Polygon([tuple(a), tuple(b), tuple(b + G_D * L), tuple(a + G_D * L)]).buffer(folga, join_style=2)


# ---------------------------------------------------------------------------- ferrolho, cano, cao, alavanca
def _ferrolho_g(q, mat='fde'):
    """Ferrolho com a parte de cima aberta (o cano aparece do peito ate o nariz), serrilhas atras, nariz fechado com a massa,
    alca de mira em cauda de andorinha, extrator na direita."""
    lado = arred([(0.0, GY0), (GL - 0.003, GY0), (GL, GY0 + 0.003), (GL, GY1 - 0.004), (GL - 0.006, GY1), (0.003, GY1), (0.0, GY1 - 0.003)], 0.0008)
    sec = arred([(-GW, GY0), (GW, GY0), (GW, GY1 - 0.0055), (GW - 0.0055, GY1), (-GW + 0.0055, GY1), (-GW, GY1 - 0.0055)], 0.0045)
    planta = Polygon([(0, -GW), (GL - 0.012, -GW), (GL, -GW + 0.0012), (GL, GW - 0.0012), (GL - 0.012, GW), (0, GW)])
    corpo = inter([solido(lado, -GW, GW), ext_x(sec, -0.01, GL + 0.01), ext_y(planta, GY0 - 0.01, GY1 + 0.01)])
    aberto = arred([(GC0, 0.04), (GC0, 0.0108), (GC0 + 0.008, 0.0028), (GC1 - 0.008, 0.0028), (GC1, 0.0108), (GC1, 0.04)], 0.003)
    cortes = [solido(aberto, -0.03, 0.03),
              caixa(GC0, GC0 + 0.034, -0.0005, 0.03, 0.0, 0.03),                      # janela de ejecao (direita)
              cil_x(GR + 0.0004, 0.05, GL + 0.01, sec=40),                               # caminho do cano
              cil_x(0.0036, GL - 0.012, GL + 0.01, -0.0074, sec=20),                     # guia da mola no nariz
              caixa(0.004, 0.18, GY0 - 0.01, -0.0085, -0.0072, 0.0072),                  # canal da armacao por baixo
              caixa(-0.01, 0.0012, -0.0075, 0.0085, -0.0042, 0.0042)]                    # rebaixo do cao
    for zs in (-1, 1):
        for i in range(9):                                                            # serrilhas de tras (em pe)
            x = 0.008 + i * 0.0032
            cortes.append(caixa(x - 0.0006, x + 0.0006, GY0 + 0.0028, GY1 - 0.0035, min(zs * (GW - 0.0008), zs * 0.03), max(zs * (GW - 0.0008), zs * 0.03)))
        for i in range(6):                                                            # serrilhas da frente (embaixo da abertura)
            x = 0.152 + i * 0.0032
            cortes.append(caixa(x - 0.0006, x + 0.0006, GY0 + 0.0028, 0.0045, min(zs * (GW - 0.0008), zs * 0.03), max(zs * (GW - 0.0008), zs * 0.03)))
    q.add(mat, menos(corpo, *cortes))
    q.add('aco_oxidado', cil_x(0.0016, -0.0006, 0.0, 0.002, 0.0, 16))                                      # ponta do percussor
    # alca de mira em cauda de andorinha (entalhe em U, dois pontos brancos) e massa de mira no nariz (um ponto branco)
    yt = GY1 + 0.0068
    alca = arred([(0.011, GY1 - 0.002), (0.025, GY1 - 0.002), (0.025, yt - 0.001), (0.0235, yt), (0.0115, yt), (0.011, yt - 0.0015)], 0.0006)
    entalhe = ext_x(Polygon([(-0.0016, GY1 + 0.0048)] + [(0.0016 * math.cos(a), GY1 + 0.0048 + 0.0016 * math.sin(a)) for a in np.linspace(0, -math.pi, 9)][::-1] +
                            [(0.0016, GY1 + 0.0048), (0.0016, yt + 0.003), (-0.0016, yt + 0.003)]).buffer(0), 0.0, 0.04)
    q.add('aco_oxidado', menos(solido(alca, -0.0068, 0.0068, 0.0007), entalhe))
    for zs in (-1, 1):
        d = trimesh.creation.cylinder(radius=0.0009, height=0.0006, sections=12); d.apply_transform(TF.rotation_matrix(-math.pi / 2, [0, 1, 0]))
        d.apply_translation([0.0108, GY1 + 0.0042, zs * 0.0036]); q.add('tinta_branca', d)
    mas = arred([(0.189, GY1 - 0.0015), (0.2, GY1 - 0.0015), (0.199, GY1 + 0.0052), (0.1915, GY1 + 0.0052)], 0.0005)
    q.add('aco_oxidado', solido(mas, -0.0016, 0.0016, 0.0004))
    d = trimesh.creation.cylinder(radius=0.001, height=0.0006, sections=12); d.apply_transform(TF.rotation_matrix(-math.pi / 2, [0, 1, 0]))
    d.apply_translation([0.1912, GY1 + 0.0034, 0]); q.add('tinta_branca', d)
    # extrator (direita) e pino do percussor
    q.add('aco_oxidado', solido(arred([(0.046, 0.0015), (0.064, 0.0015), (0.064, 0.0058), (0.046, 0.0058)], 0.0008), GW - 0.0004, GW + 0.0005, 0.0002))
    q.add('aco_inox', cil_z(0.0011, GW - 0.0002, GW + 0.0006, 0.05, 0.0037, 10))
    for zs in (-1, 1): q.add('aco_inox', cil_z(0.0012, min(zs * (GW - 0.0002), zs * (GW + 0.0003)), max(zs * (GW - 0.0002), zs * (GW + 0.0003)), 0.04, -0.006, 10))


def _alavanca_g(q, mat='aco_oxidado'):
    """Alavanca ambidestra de trava/desarme do cao: tambor no ferrolho e aba estriada para tras (em cima = fogo)."""
    px, py = GP_TRAVA
    aba = arred([(px - 0.002, py - 0.0038), (px - 0.016, py + 0.0028), (px - 0.0175, py + 0.0068), (px - 0.0135, py + 0.0078), (px + 0.003, py + 0.0035)], 0.0014)
    for zs in (-1, 1):
        z0, z1 = sorted((zs * GW, zs * (GW + 0.0019)))
        q.add(mat, cil_z(0.0045, z0, z1, px, py, 28))
        q.add(mat, solido(aba, *sorted((zs * GW, zs * (GW + 0.0024))), 0.0005))
        for i in range(4):
            x = px - 0.0145 + i * 0.0022
            q.add(mat, caixa(x - 0.0004, x + 0.0004, py + 0.0028, py + 0.0072, *sorted((zs * (GW + 0.0023), zs * (GW + 0.0029)))))
        zp = zs * (GW + 0.0019)
        q.add('tinta_vermelha', cil_z(0.0011, *sorted((zp, zp + zs * 0.0002)), px + 0.004, py + 0.0004, 12))   # ponto vermelho (fogo)


def _cano_g(q, mat='aco_cano'):
    cano = torno_x([(0.0074, 0.06), (0.0074, 0.088), (GR, 0.094), (GR, GL + 0.004)], 48)
    q.add(mat, menos(cano, cil_x(0.0045, 0.05, GL + 0.03, sec=24)))
    q.add(mat, solido(arred([(0.07, -0.0105), (0.094, -0.0105), (0.094, -0.004), (0.07, -0.004)], 0.0012), -0.0045, 0.0045, 0.0005))   # bloco de trava
    for zs in (-1, 1): q.add(mat, solido(arred([(0.075, -0.0108), (0.086, -0.0108), (0.086, -0.0055), (0.075, -0.0055)], 0.0008),
                                          *sorted((zs * 0.0045, zs * 0.0072)), 0.0003))                                                       # orelhas da trava
    rosca_x(q, mat, GR, GL + 0.004, GL + 0.016, 0.001)
    q.add(mat, tubo_x(0.0045, 0.0064, GL + 0.016, GL + 0.017, sec=32))
    q.add('latao', torno_x([(0.0045, 0.062), (0.0045, 0.066)], 24))                                    # culote do cartucho na camara


def _cao_g(q, mat='aco_oxidado'):
    """Cao de anel (furo redondo na espora) com serrilhas atras; desenhado abaixado (desarmado)."""
    cx, cy = GP_CAO
    perfil = arred([(cx - 0.004, cy - 0.006), (cx + 0.0055, cy - 0.004), (cx + 0.0068, cy + 0.01), (cx + 0.0062, cy + 0.033), (cx + 0.002, cy + 0.0375),
                    (cx - 0.0052, cy + 0.0365), (cx - 0.0072, cy + 0.031), (cx - 0.0055, cy + 0.012)], 0.0016)
    anel = Point(cx - 0.0002, cy + 0.0305).buffer(0.0026, 32)
    q.add(mat, solido(perfil.difference(anel), -0.0031, 0.0031, 0.0007))
    for i in range(5):
        y = cy + 0.02 + i * 0.0022
        q.add(mat, caixa(cx - 0.0078, cx - 0.0062, y - 0.0004, y + 0.0004, -0.0031, 0.0031))
    q.add('aco_inox', cil_z(0.0022, -0.0034, 0.0034, cx, cy, 16))


# ---------------------------------------------------------------------------- armacao, cabo, carregador
def _armacao_g(p, mat='fde'):
    alto = arred([(-0.0148, -0.0045), (-0.0015, -0.0045), (-0.0015, -0.0134), (0.1895, -0.0134), (0.1925, -0.016), (0.1925, -0.027), (0.189, -0.0305),
                  (0.1005, -0.0305), (0.1005, -0.0345), (0.044, -0.0345), (0.038, -0.03), (-0.0105, -0.03), (-0.0185, -0.0235), (-0.021, -0.0175),
                  (-0.019, -0.0128)], 0.0012)
    ch = solido(alto, -0.0094, 0.0094, 0.0011)
    ch = menos(ch, caixa(-0.0165, 0.0005, -0.027, 0.01, -0.0034, 0.0034),               # janela do cao
               caixa(0.062, 0.082, -0.036, -0.016, -0.0032, 0.0032))                   # fenda do gatilho
    p.add(mat, ch)
    # guarda-mato de frente quase reta com gancho pequeno
    fora = arred([(0.04, -0.033), (0.1005, -0.033), (0.1045, -0.0365), (0.1035, -0.0475), (0.0985, -0.0528), (0.06, -0.0528), (0.04, -0.051),
                  (0.026, -0.046), (0.028, -0.034)], 0.0028)
    dentro = arred([(0.05, -0.0338), (0.0965, -0.0338), (0.0975, -0.0462), (0.0935, -0.0488), (0.062, -0.0488), (0.0515, -0.0445), (0.047, -0.0385)], 0.0034)
    p.add(mat, solido(fora.difference(dentro), -0.0052, 0.0052, 0.0013))
    p.add(mat, solido(arred([(0.0985, -0.0528), (0.1035, -0.0528), (0.1035, -0.0505), (0.0985, -0.0505)], 0.0008), -0.0052, 0.0052, 0.0005))
    # cabo: nucleo da armacao (costas e frente estriadas) com o poco do carregador, talas na parte 'talas'
    nuc = punho_redondo(CABO_G, -0.026, G_YB, LARG_NUC_G, n=2.4, fatias=110, voltas=56, raio_base=0.004)
    p.add(mat, menos(nuc, solido(_perfil_car_g(0.0006), -G_MZ - 0.0004, G_MZ + 0.0004)))
    for i in range(9):                                                                 # estrias da frente do cabo
        t = 0.035 + i * 0.0075; c = G_T + G_N * (G_MW + 0.0046) + G_D * t
        g = caixa(-0.0004, 0.0004, -0.004, 0.004, -0.0065, 0.0065); g.apply_transform(TF.rotation_matrix(-G_AN, [0, 0, 1])); g.apply_translation([c[0] + 0.0004, c[1], 0])
        p.add(mat, g)
    # trilho do guarda-po (3 fendas), retem do carregador (esquerda), alavanca de desmontagem, pinos, olhal
    trilho(p, mat, 0.125, 0.186, -0.0305, True, 0.019, 0.02)
    p.add(mat, solido(arred([(0.037, -0.044), (0.047, -0.044), (0.047, -0.0355), (0.037, -0.0355)], 0.0028), -0.0124, -0.0108, 0.0005))
    for x in np.linspace(0.039, 0.045, 4): p.add(mat, caixa(x - 0.0003, x + 0.0003, -0.043, -0.0365, -0.0127, -0.0123))
    p.add('aco_oxidado', cil_z(0.0058, -0.0104, -0.0094, 0.083, -0.0205, 28))
    p.add('aco_oxidado', solido(arred([(0.079, -0.0285), (0.097, -0.0285), (0.097, -0.0245), (0.079, -0.0245)], 0.0016), -0.0106, -0.0094, 0.0004))
    p.add('aco_inox', cil_z(0.0024, 0.0094, 0.0102, 0.083, -0.0205, 16))
    for (x, y) in ((GP_GAT[0], GP_GAT[1]), (GP_CAO[0], GP_CAO[1]), (-0.012, -0.024), (0.052, -0.016)):
        for zs in (-1, 1): p.add('aco_inox', cil_z(0.0014, min(zs * 0.0092, zs * 0.0098), max(zs * 0.0092, zs * 0.0098), x, y, 12))
    b0 = G_T + G_D * G_ML - G_N * (G_MW + 0.008)
    p.add('aco_oxidado', solido(Point(b0[0] - 0.002, b0[1] + 0.003).buffer(0.0042, 24).difference(Point(b0[0] - 0.002, b0[1] + 0.003).buffer(0.0025, 24)),
                                -0.0028, 0.0028, 0.0004))


def _talas_g(q, mat='polimero_fde', mat_x='polimero_pontos_fde', parafusos=True):
    """Talas que abracam o cabo (lisas na borda, pontilhado no meio, dois parafusos)."""
    cabo_com_talas(q, CABO_G, -0.026, G_YB, LARG_NUC_G, LARG_TALA_G, mat, mat, mat_x, borda=0.0046, borda_xadrez=0.0028,
                   n=2.4, raio_base=0.004, nucleo=False)
    if parafusos:
        for px, py in ((0.0064, -0.045), (-0.0138, -0.111)):
            zc = z_superficie(CABO_G, px, py, LARG_TALA_G, 2.4)
            for zs in (-1, 1):
                m = torno_x([(0.0, -0.0006), (0.0026, -0.0006), (0.0026, 0.0002), (0.0019, 0.0008), (0.0, 0.0009)], 20)
                m.apply_transform(TF.rotation_matrix(-zs * math.pi / 2, [0, 1, 0])); m.apply_translation([px, py, zs * zc]); q.add('aco_oxidado', m)
                q.add('aco_inox', caixa(px - 0.0017, px + 0.0017, py - 0.0003, py + 0.0003, zs * (zc + 0.0006) - 0.0003, zs * (zc + 0.0006) + 0.0003))


def _carregador_g(q, cap=17, extra=0.0, mat_base='polimero_fde'):
    """Carregador de aco de fila dupla com furos de contagem, labios, cartucho no topo e base de polimero (mais longa no de 20)."""
    corpo = solido(_perfil_car_g(0, extra), -G_MZ, G_MZ, 0.0012)
    furos = []
    for i in range(int(cap / 3)):
        c = G_T - G_N * 0.0105 + G_D * (0.022 + i * 0.0145)
        furos.append(cil_z(0.0011, -0.02, 0.0, c[0], c[1], 10))
    q.add('aco_oxidado', menos(corpo, *furos))
    L = G_ML + extra; b0 = G_T + G_D * L
    base = arred([tuple(b0 - G_N * 0.0178 - G_D * 0.001), tuple(b0 + G_N * 0.0186 - G_D * 0.001), tuple(b0 + G_N * 0.0194 + G_D * 0.0045),
                  tuple(b0 + G_N * 0.0182 + G_D * 0.0072), tuple(b0 - G_N * 0.0178 + G_D * 0.0072)], 0.0016)
    q.add(mat_base, solido(base, -0.0126, 0.0126, 0.0022))
    if extra:                                                                           # luva de polimero do estendido (acompanha o cabo)
        a = G_T + G_D * (G_ML - 0.002); luva = Polygon([tuple(a - G_N * 0.0168), tuple(a + G_N * 0.0176), tuple(b0 + G_N * 0.0186), tuple(b0 - G_N * 0.0178)])
        q.add(mat_base, solido(arred(list(luva.exterior.coords)[:-1], 0.0025), -0.0142, 0.0142, 0.0035))
    xc, yc = G_T[0] + 0.002, G_T[1] + 0.0022
    q.merge(_cartucho_9mm_malha(), TF.translation_matrix([xc - 0.01, yc + 0.0028, 0]) @ TF.rotation_matrix(math.radians(-3), [0, 0, 1]))
    for zs in (-1, 1): q.add('aco_oxidado', caixa(G_T[0] - 0.013, G_T[0] + 0.006, G_T[1] - 0.001, G_T[1] + 0.0034, zs * 0.0048 - 0.0012, zs * 0.0048 + 0.0012))


def _gatilho_g(q):
    """Gatilho de acao dupla: lamina longa e curva (ponta para a FRENTE) com estrias na face."""
    px, py = GP_GAT
    d = [(0.001, -0.0005), (-0.001, -0.007), (-0.0022, -0.014), (-0.0016, -0.0205), (0.0016, -0.0248)]
    lam = LineString([(px + a, py + b) for a, b in d]).buffer(0.0019, cap_style=1, join_style=1)
    q.add('aco_oxidado', solido(lam, -0.0032, 0.0032, 0.0011))
    for i in range(5):
        y = py - 0.009 - i * 0.0024
        q.add('aco_oxidado', caixa(px - 0.0048, px - 0.0038, y - 0.0003, y + 0.0003, -0.0029, 0.0029))
    q.add('aco_inox', cil_z(0.0018, -0.0034, 0.0034, px, py, 14))


def _retem_g(q, mat='aco_oxidado'):
    """Retem do ferrolho (esquerda): alavanca comprida sobre o cabo com apoio estriado para o polegar."""
    lev = arred([(0.026, -0.0185), (0.06, -0.0178), (0.063, -0.0152), (0.058, -0.0138), (0.036, -0.0141), (0.03, -0.0128), (0.024, -0.0138)], 0.0008)
    q.add(mat, solido(lev, -0.0108, -0.0094, 0.0004))
    for x in np.linspace(0.027, 0.034, 4): q.add(mat, caixa(x - 0.0003, x + 0.0003, -0.0178, -0.014, -0.011, -0.0106))


# ---------------------------------------------------------------------------- a arma
def _guardia(A, mat='fde', mat_tala='polimero_fde', mat_x='polimero_pontos_fde', talas_padrao='talas_guardia'):
    A.pivo = (0.004, -0.068, 0.0)
    _armacao_g(A.base, mat)
    tal = A.parte('talas', (0, 0, 0), explodir=(-0.03, -0.02, 0), tipo='fixa', descricao='talas do cabo (trocáveis)')
    _talas_g(tal, mat_tala, mat_x)
    gat = A.parte('gatilho', (GP_GAT[0], GP_GAT[1], 0), explodir=(0.05, -0.03, 0), tipo='gira', eixo='z', curso_graus=-16,
                  descricao='ação dupla: puxada longa arma e solta o cão; depois do 1º tiro a puxada é curta')
    _gatilho_g(gat)
    cao = A.parte('cao', (GP_CAO[0], GP_CAO[1], 0), explodir=(-0.03, 0.04, 0), tipo='gira', eixo='z', curso_graus=GCAO,
                  descricao=f'cão externo de anel: arma {GCAO}° para trás (o ferrolho arma no tiro)')
    _cao_g(cao)
    cano = A.parte('cano', (0, 0, 0), explodir=(0.06, 0.07, 0), tipo='desliza', curso_m=0.0045, descricao='recua 4,5 mm reto com o ferrolho (bloco de trava cai)')
    _cano_g(cano)
    fer = A.parte('ferrolho', (0, 0, 0), explodir=(-0.04, 0.035, 0), tipo='desliza', curso_m=GCF,
                  descricao=f'recua {int(GCF * 1000)} mm ao atirar; fica travado atrás com o carregador vazio')
    _ferrolho_g(fer, mat)
    trv = A.parte('trava', (GP_TRAVA[0], GP_TRAVA[1], 0), pai='ferrolho', explodir=(0, 0.02, 0.04), tipo='gira', eixo='z', curso_graus=GTRAVA,
                  descricao='alavanca dos dois lados do ferrolho: para baixo trava e desarma o cão com segurança; volta sozinha para cima (fogo)')
    _alavanca_g(trv)
    ret = A.parte('retem', (0.024, -0.0138, 0), explodir=(0, 0, -0.04), tipo='gira', eixo='z', curso_graus=5,
                  descricao='retém do ferrolho: sobe quando o carregador esvazia, baixar solta o ferrolho')
    _retem_g(ret)
    car = A.parte('carregador', (G_T[0], G_T[1], 0), explodir=(-0.02, -0.07, 0), tipo='remove', direcao=[round(float(c), 3) for c in rot([G_D[0], G_D[1], 0])],
                  municao='municao_9mm', capacidade=17, descricao='sai pelo fundo do cabo ao apertar o retém (atrás do guarda-mato, esquerda)')
    _carregador_g(car, 17)
    A.encaixe('encaixe_empunhadura', (-0.004, -0.075, 0), 'talas_guardia', substitui='talas', explodir=(-0.03, -0.02, 0),
              aceita=[talas_padrao] + [t for t in ('talas_guardia', 'talas_guardia_preta', 'talas_guardia_madeira', 'talas_guardia_borracha') if t != talas_padrao],
              descricao='ao pôr talas aqui, esconda as malhas do nó talas')
    A.encaixe('encaixe_boca', (GL + 0.016, 0, 0), 'boca_rosca_9mm', pai='cano', explodir=(0.06, 0, 0),
              aceita=['protetor_rosca_9mm', 'supressor_9mm', 'supressor_9mm_tan', 'supressor_9mm_verde', 'supressor_9mm_cinza', 'compensador_9mm', 'supressor_garrafa'],
              descricao='rosca do cano (a mesma da Sentinela): sem nada fica a rosca à mostra')
    A.encaixe('encaixe_trilho', (G_TRILHO[0], G_TRILHO[1], 0), 'trilho_curto', explodir=(0.02, -0.05, 0), aceita=['lanterna_pistola', 'laser_pistola', 'combo_lanterna_laser'],
              descricao='trilho de 3 fendas embaixo do guarda-pó')
    A.encaixe('encaixe_carregador', (G_T[0], G_T[1], 0), 'carregador_guardia', pai='carregador', substitui='carregador',
              aceita=['carregador_guardia_17', 'carregador_guardia_20'], descricao='filho do nó carregador; ao pôr um carregador aqui, esconda as malhas do nó carregador')
    A.encaixe('cinto', (0.02, 0.05, -0.025), 'coldre_guardia', aceita=['coldre_guardia'], descricao='a arma entra no coldre pelo pivô (o coldre tem o encaixe "arma")')
    A.encaixe('saida_estojo', (0.075, 0.009, GW + 0.002), 'efeito', descricao='onde nasce o estojo ejetado (vai para +X e para cima, aos 0,04 s)')
    A.encaixe('boca_fogo', (GL + 0.017, 0, 0), 'efeito', pai='cano', descricao='clarão de boca e origem do disparo (raycast para -Z)')
    A.encaixe('mira_ferro', (0.018, GY1 + 0.0052, 0), 'mira', pai='ferrolho', descricao='centro do entalhe da alça: câmera de 1ª pessoa olha daqui pela ponta da massa (-Z)')
    # ---- animacoes (tempos em s; x = frente)
    fer_t = lambda ks: ('ferrolho', 't', pose([(t, (dx, 0, 0)) for t, dx in ks]))
    can_t = lambda ks: ('cano', 't', pose([(t, (dx, 0, 0)) for t, dx in ks]))
    cao_r = lambda ks: ('cao', 'r', (0, 0, 1), pose(ks))
    gat_r = lambda ks: ('gatilho', 'r', (0, 0, 1), pose(ks))
    coice = [(None, 'r', (0, 0, 1), pose([(0, 0), (0.025, 0), (0.05, 8), (0.15, 0)])),
             (None, 't', pose([(0, (0, 0, 0)), (0.025, (0, 0, 0)), (0.05, (-0.013, 0.004, 0)), (0.15, (0, 0, 0))]))]
    ciclo = [fer_t([(0, 0), (0.02, 0), (0.045, -GCF), (0.1, 0)]), can_t([(0, 0), (0.02, 0), (0.03, -0.0045), (0.09, -0.0045), (0.1, 0)])]
    A.anim('atirar_dupla', 0.36, [gat_r([(0, 0), (0.2, -16), (0.26, -16), (0.34, 0)]), cao_r([(0, 0), (0.2, GCAO), (0.22, 0), (0.24, GCAO), (0.36, GCAO)])] +
           [fer_t([(0, 0), (0.22, 0), (0.245, -GCF), (0.3, 0)]), can_t([(0, 0), (0.22, 0), (0.23, -0.0045), (0.29, -0.0045), (0.3, 0)]),
            (None, 'r', (0, 0, 1), pose([(0, 0), (0.225, 0), (0.25, 8), (0.36, 0)])),
            (None, 't', pose([(0, (0, 0, 0)), (0.225, (0, 0, 0)), (0.25, (-0.013, 0.004, 0)), (0.36, (0, 0, 0))]))],
           desc='1º tiro com o cão abaixado (ação dupla): puxada longa, o cão sobe e cai (0,22 s), o ferrolho volta e deixa o cão armado; estojo aos 0,24 s')
    A.anim('atirar', 0.15, [gat_r([(0, 0), (0.02, -7), (0.06, -7), (0.12, 0)]), cao_r([(0, GCAO), (0.02, 0), (0.04, GCAO), (0.15, GCAO)])] + ciclo + coice,
           desc='tiro com o cão armado (ação simples): puxada curta, recuo e o cão fica armado de novo; estojo aos 0,04 s')
    A.anim('atirar_ultimo', 0.15, [gat_r([(0, 0), (0.02, -7), (0.06, -7), (0.12, 0)]), cao_r([(0, GCAO), (0.02, 0), (0.04, GCAO), (0.15, GCAO)]),
                                   fer_t([(0, 0), (0.02, 0), (0.045, -GCF), (0.07, -GCF + 0.003), (0.15, -GCF + 0.003)]),
                                   can_t([(0, 0), (0.03, -0.0045), (0.15, -0.0045)]),
                                   ('retem', 'r', (0, 0, 1), pose([(0, 0), (0.05, 0), (0.06, 5), (0.15, 5)]))] + coice,
           desc='último tiro: o ferrolho fica travado atrás no retém')
    A.anim('vazia', 0.1, [fer_t([(0, -GCF + 0.003), (0.1, -GCF + 0.003)]), can_t([(0, -0.0045), (0.1, -0.0045)]), cao_r([(0, GCAO), (0.1, GCAO)]),
                          ('retem', 'r', (0, 0, 1), pose([(0, 5), (0.1, 5)]))], laco=True, desc='pose parada: ferrolho travado atrás, carregador vazio')
    A.anim('desarmar', 0.5, [('trava', 'r', (0, 0, 1), pose([(0, 0), (0.12, GTRAVA), (0.32, GTRAVA), (0.42, 0)])),
                             cao_r([(0, GCAO), (0.12, GCAO), (0.16, 0), (0.5, 0)])],
           desc='abaixa a alavanca do ferrolho: o cão cai sem disparar (0,16 s) e a alavanca volta para cima; o próximo tiro é de ação dupla')
    A.anim('armar', 0.35, [cao_r([(0, 0), (0.25, GCAO), (0.35, GCAO)])], desc='arma o cão com o polegar (o próximo tiro é de ação simples)')
    dm = tuple(np.array([G_D[0], G_D[1], 0]) * 0.17)
    car_t = lambda ks: ('carregador', 't', pose(ks))
    troca = car_t([(0, (0, 0, 0)), (0.15, (0, 0, 0)), (0.3, tuple(np.array([G_D[0], G_D[1], 0]) * 0.02)), (0.5, dm), (0.9, dm),
                   (1.15, tuple(np.array([G_D[0], G_D[1], 0]) * 0.01)), (1.22, (0, 0, 0))])
    A.anim('recarregar', 1.6, [troca, (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, -18), (1.3, -18), (1.6, 0)])),
                               (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 10), (1.3, 10), (1.6, 0)]))],
           desc='troca tática: solta o carregador (0,3 s), o novo entra (1,2 s); trocar o nó carregador entre 0,5 e 0,9 s')
    A.anim('recarregar_vazia', 2.1, [troca, fer_t([(0, -GCF + 0.003), (1.45, -GCF + 0.003), (1.5, -GCF), (1.58, 0)]),
                                     can_t([(0, -0.0045), (1.5, -0.0045), (1.58, 0)]), cao_r([(0, GCAO), (2.1, GCAO)]),
                                     ('retem', 'r', (0, 0, 1), pose([(0, 5), (1.45, 5), (1.5, 0)])),
                                     (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, -18), (1.3, -18), (1.5, -8), (1.7, -8), (2.1, 0)])),
                                     (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 10), (1.3, 10), (1.5, 4), (1.7, 4), (2.1, 0)]))],
           desc='recarga vazia: troca o carregador e baixa o retém (1,5 s); o ferrolho fecha e deixa o cão armado')
    A.anim('inspecionar', 2.6, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -55), (1.1, -55), (1.5, 30), (2.0, 30), (2.6, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 12), (1.1, 12), (1.5, 8), (2.0, 8), (2.6, 0)])),
                                fer_t([(0, 0), (0.5, 0), (0.65, -0.012), (0.95, -0.012), (1.05, 0)])],
           desc='gira a arma, puxa o ferrolho até ver o cartucho na câmara (pela abertura de cima) e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.8), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


_DADOS_G = dict(classe='fogo', calibre='9 mm', municao='municao_9mm', capacidade=17, dano=34, alcance_m=28, alcance_max_m=55, modo='semiautomático (ação dupla e simples)',
                tiros_por_s=4.0, recarga_s=1.6, recarga_vazia_s=2.1, precisao=0.76, recuo=0.26, ruido_m=60, durabilidade=900, peso_kg=0.98,
                raridade='raro', valor_troca=55, onde=['quartel', 'delegacia', 'posto', 'banco'])


@arma('pistola_guardia_9mm', 'Pistola Guardiã 9 mm', 'armas', 'pistola',
      descricao='Pistola de serviço de armação de alumínio cor de areia: ferrolho aberto em cima, cão externo, alavanca que desarma o cão, '
                'trilho para lanterna e cano com rosca. Mais pesada que a Sentinela, coice mais manso e 17 tiros.', **_DADOS_G)
def pistola_guardia_9mm(A): _guardia(A)


PRETA_G = {'fde': 'aluminio_preto', 'polimero_fde': 'polimero', 'polimero_pontos_fde': 'polimero_pontos'}


@arma('pistola_guardia_9mm_preta', 'Pistola Guardiã 9 mm (preta)', 'armas', 'pistola',
      descricao='A mesma Guardiã toda preta (alumínio anodizado e talas pretas). Aceita os mesmos acessórios.', **_DADOS_G)
def pistola_guardia_9mm_preta(A):
    _guardia(A, 'aluminio_preto', 'polimero', 'polimero_pontos', talas_padrao='talas_guardia_preta')
    for pt in A.partes:
        if pt['no'] == 'carregador': _recolore(pt['peca'], PRETA_G)


# ---------------------------------------------------------------------------- acessorios
_P_TALA = (-0.004, -0.075, 0)


@_acessorio('talas_guardia', 'Talas pontilhadas (Guardiã)', 'empunhadura', 'talas_guardia', peso_kg=0.04, raridade='comum', modificadores={},
            descricao='As talas cor de areia que vêm na Guardiã: borda lisa e pontilhado no meio.')
def talas_guardia(A): _talas_g(A.base); A.pivo = _P_TALA


@_acessorio('talas_guardia_preta', 'Talas pontilhadas pretas (Guardiã)', 'empunhadura', 'talas_guardia', peso_kg=0.04, raridade='comum', modificadores={},
            descricao='As mesmas talas em polímero preto (vêm na Guardiã preta).')
def talas_guardia_preta(A): _talas_g(A.base, 'polimero', 'polimero_pontos'); A.pivo = _P_TALA


@_acessorio('talas_guardia_madeira', 'Talas de nogueira (Guardiã)', 'empunhadura', 'talas_guardia', peso_kg=0.05, raridade='incomum', valor_troca=12,
            modificadores={}, onde=['casas', 'casa_de_campo'], descricao='Talas de nogueira com quadriculado e medalhão liso: bonitas, mas escorregam um pouco com a mão suada.')
def talas_guardia_madeira(A):
    cabo_com_talas(A.base, CABO_G, -0.026, G_YB, LARG_NUC_G, LARG_TALA_G, 'nogueira', 'nogueira', 'madeira_punho', borda=0.0046, borda_xadrez=0.004,
                   n=2.4, raio_base=0.004, nucleo=False, medalhao=(-0.0037, -0.078, 0.0055, 'aco_inox'), parafuso=(-0.0138, -0.111))
    A.pivo = _P_TALA


@_acessorio('talas_guardia_borracha', 'Empunhadura de borracha (Guardiã)', 'empunhadura', 'talas_guardia', peso_kg=0.07, raridade='incomum', valor_troca=14,
            modificadores={'recuo': 0.85, 'precisao': 1.04}, onde=['quartel', 'delegacia'],
            descricao='Borracha que abraça o cabo inteiro, com apoio para os dedos na frente: segura melhor o coice e não escorrega.')
def talas_guardia_borracha(A):
    q = A.base
    dedos = _contorno_cabo_g(0.0069, 0.0172, belly=0.0, palma=0.0018)
    f = lambda t: G_T + G_N * (G_MW + 0.0069 + 0.0036) + G_D * t
    dedos = dedos.difference(unary_union([Point(*f(t)).buffer(0.0052, 24) for t in (0.044, 0.066, 0.088)])).buffer(0.0012).buffer(-0.0012)
    larg = lambda y: 0.0128 + 0.0036 * GT.smooth(-0.029, -0.041, y)
    yb = dedos.bounds[1]
    q.add('borracha_grip', punho_redondo(dedos, -0.026, yb, larg, n=2.2, fatias=110, voltas=56, raio_base=0.0045))
    for zs in (-1, 1):
        zc = z_superficie(dedos, -0.0138, -0.111, larg, 2.2)
        q.add('aco_oxidado', cil_z(0.0024, *sorted((zs * (zc - 0.0004), zs * (zc + 0.0006))), -0.0138, -0.111, 16))
    A.pivo = _P_TALA


def _carregador_g_acessorio(A, cap, extra, mat_base='polimero_fde'):
    _carregador_g(A.base, cap, extra, mat_base); A.pivo = (G_T[0], G_T[1], 0)


@_acessorio('carregador_guardia_17', 'Carregador 9 mm da Guardiã (17)', 'carregador', 'carregador_guardia', capacidade=17, municao='municao_9mm',
            peso_kg=0.1, raridade='incomum', valor_troca=10, modificadores={}, descricao='Carregador de aço de 17 tiros com base cor de areia (vem na Guardiã).')
def carregador_guardia_17(A): _carregador_g_acessorio(A, 17, 0.0)


@_acessorio('carregador_guardia_20', 'Carregador 9 mm estendido da Guardiã (20)', 'carregador', 'carregador_guardia', capacidade=20, municao='municao_9mm',
            peso_kg=0.12, raridade='raro', valor_troca=18, modificadores={'recarga_s': 1.05}, onde=['quartel', 'delegacia'],
            descricao='Carregador de 20 com luva de polímero que continua o cabo (sobra embaixo e dá apoio ao dedinho).')
def carregador_guardia_20(A): _carregador_g_acessorio(A, 20, 0.018)


@_acessorio('coldre_guardia', 'Coldre de náilon com trava (Guardiã)', 'coldre', 'coldre_guardia', peso_kg=0.24, raridade='incomum', valor_troca=12,
            modificadores={'tempo_sacar': 0.75}, onde=['quartel', 'delegacia', 'posto'],
            descricao='Coldre de cinto de náilon com fivela sobre o cão e reforço de polímero. Leva a Guardiã (até com lanterna curta) sem ocupar a mochila.')
def coldre_guardia(A):
    q = A.base
    sil = arred([(-0.022, -0.026), (-0.016, 0.022), (0.04, 0.022), (0.212, 0.019), (0.222, 0.004), (0.222, -0.05), (0.196, -0.058), (0.108, -0.058),
                 (0.1, -0.064), (0.05, -0.066), (0.03, -0.045), (-0.004, -0.04)], 0.007)
    q.add('nylon_coldre', solido(sil, -0.021, 0.021, 0.009))
    q.add('polimero', solido(arred([(0.17, -0.054), (0.218, -0.054), (0.218, 0.012), (0.17, 0.012)], 0.004), -0.0214, 0.0214, 0.002))   # ponteira moldada
    pts = list(sil.buffer(-0.0055).exterior.coords)
    for i in range(0, len(pts) - 1, 2):                                                        # pesponto em volta
        a, b = np.array(pts[i]), np.array(pts[i + 1]); c = (a + b) / 2
        for zs in (-1, 1): q.add('costura', caixa(c[0] - 0.0011, c[0] + 0.0011, c[1] - 0.0004, c[1] + 0.0004, zs * 0.0217 - 0.0003, zs * 0.0217 + 0.0003))
    q.add('nylon_coldre', solido(arred([(-0.01, 0.018), (0.032, 0.018), (0.032, 0.085), (-0.01, 0.085)], 0.004), -0.028, -0.021, 0.001))    # passador do cinto
    tira = arred([(-0.018, 0.016), (-0.004, 0.016), (0.0, 0.03), (-0.006, 0.042), (-0.02, 0.04)], 0.003)                                     # tira com botão sobre o cão
    q.add('nylon_coldre', solido(tira, -0.023, 0.023, 0.002))
    for zs in (-1, 1): q.add('aco_oxidado', cil_z(0.0045, *sorted((zs * 0.023, zs * 0.0246)), -0.009, 0.034, 20))
    A.encaixe('arma', (-0.006, -0.068, 0.0), 'efeito', descricao='ponha a arma aqui (pivô da arma) para guardá-la no coldre')
    A.pivo = (0.01, 0.05, -0.025)
