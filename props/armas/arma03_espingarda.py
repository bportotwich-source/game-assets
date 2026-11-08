# Arma 3: espingarda calibre 12 de bombeamento (tatica e curta) com seus acessorios. Executado por gerar_armas.py
# (mesmas funcoes, plano de lado: x frente, y cima, z direita). Desenho proprio: nenhuma espingarda comercial copiada.
CORES.update({'aluminio_receptor': (44, 45, 48), 'casca_vermelha': (150, 28, 24), 'casca_verde': (44, 84, 52), 'nylon': (52, 54, 48), 'tinta_vermelha': (190, 24, 20)})
METAL.update({'aluminio_receptor': (0.6, 0.42), 'casca_vermelha': (0.0, 0.42), 'casca_verde': (0.0, 0.42), 'nylon': (0.0, 0.92), 'tinta_vermelha': (0.0, 0.5)})

RX0, RX1 = -0.035, 0.205        # receptor em x (atras / frente)
RY0, RY1 = -0.047, 0.017        # receptor em y (baixo / topo)
RW = 0.0145                     # meia largura do receptor
RB, RA = 0.0106, 0.0093         # raio externo do cano e da alma (calibre 12 = 18,5 mm)
TY, TR = -0.025, 0.0125         # eixo e raio do tubo do carregador (embaixo do cano)
C12 = 0.085                     # curso da telha (e do ferrolho)
ESP_LONGA = dict(xm=RX1 + 0.508, xt=RX1 + 0.40, f0=0.295, fl=0.18, xl=0.565, hs1=RX1 + 0.508 - 0.17)
ESP_CURTA = dict(xm=RX1 + 0.356, xt=RX1 + 0.33, f0=0.292, fl=0.155, xl=0.49, hs1=RX1 + 0.356 - 0.13)


def corpo_x(perfil, x_frente, x_tras, meia_larg, n=2.4, fatias=90, voltas=48, raio_tras=0.004, raio_frente=0.004):
    """Igual a punho_redondo, mas fatiado ao longo de x (coronhas, telhas, guarda-maos): em cada x pega a altura do perfil
    e faz uma secao arredondada (superelipse) de largura 2 * meia_larg(x). Solido estanque."""
    sw = affinity.affine_transform(perfil, [0, 1, 1, 0, 0, 0])          # (x, y) -> (y, x)
    m = punho_redondo(sw, x_frente, x_tras, meia_larg, n, fatias, voltas, raio_base=raio_tras, raio_topo=raio_frente)
    v = m.vertices
    m = trimesh.Trimesh(np.stack([v[:, 1], v[:, 0], v[:, 2]], 1), m.faces[:, ::-1].copy(), process=True)
    trimesh.repair.fix_normals(m)
    return _fix(m)


def _cartucho_12(mat='casca_vermelha', sec=28, vazio=False, balote=False):
    """Cartucho 12 deitado em x (base em x = 0): culote de latao alto com aro, casca plastica, fechamento em estrela (6 dobras)
    ou dobra rolada mostrando o balote. vazio = casca ejetada, aberta."""
    q = P()
    q.add('latao', torno_x([(0.0, 0.0), (0.01125, 0.0), (0.01125, 0.0014), (0.0104, 0.0017), (0.0104, 0.0158), (0.0102, 0.0164), (0.0, 0.0164)], sec))
    q.add('aco_inox', torno_x([(0.0, -0.00005), (0.0029, -0.00005), (0.0029, 0.0004)], max(10, sec // 2)))          # espoleta
    q.add('latao', tubo_x(0.0084, 0.0105, 0.0006, 0.0011, sec=sec))                                                     # anel do culote
    if vazio:
        casca = torno_x([(0.0101, 0.015), (0.0101, 0.0655), (0.0104, 0.07), (0.0112, 0.0735), (0.0, 0.0735)], sec)
        casca = menos(casca, cil_x(0.0093, 0.017, 0.08, sec=sec))
        for i in range(6):
            g = caixa(0.0695, 0.08, -0.0006, 0.0006, 0.0, 0.02); g.apply_transform(TF.rotation_matrix(i * math.pi / 3, [1, 0, 0]))
            casca = menos(casca, g)                                                                                         # dobras abertas
        q.add(mat, casca)
    elif balote:
        q.add(mat, menos(torno_x([(0.0101, 0.015), (0.0101, 0.0652), (0.0097, 0.0668), (0.0088, 0.0672), (0.0, 0.0672)], sec),
                         cil_x(0.0086, 0.064, 0.07, sec=sec)))
        q.add('chumbo', torno_x([(0.0086, 0.06), (0.0086, 0.0655), (0.0074, 0.0678), (0.004, 0.069), (0.0, 0.0692)], sec))
    else:
        casca = torno_x([(0.0101, 0.015), (0.0101, 0.0665), (0.0097, 0.0686), (0.0084, 0.0696), (0.0, 0.0688)], sec)
        for i in range(6):                                                                                                  # fechamento em estrela
            g = caixa(0.0675, 0.072, -0.00045, 0.00045, 0.0005, 0.0092); g.apply_transform(TF.rotation_matrix(i * math.pi / 3 + 0.3, [1, 0, 0]))
            casca = menos(casca, g)
        q.add(mat, casca)
    return q


def _tampa_tubo(q, x0, y0):
    """Tampa recartilhada da ponta do tubo do carregador (rosca no tubo)."""
    q.add('aco_oxidado', torno_x([(TR + 0.0006, x0), (TR + 0.0016, x0 + 0.0015), (TR + 0.0016, x0 + 0.0165), (TR - 0.0008, x0 + 0.0205),
                                  (0.0045, x0 + 0.0212), (0.0045, x0 + 0.0195), (0.0, x0 + 0.0195)], 48, y0))
    q.add('recartilhado', tubo_x(TR + 0.0012, TR + 0.0021, x0 + 0.004, x0 + 0.0135, y0, sec=48))
    q.add('aco_inox', cil_x(0.0028, x0 + 0.019, x0 + 0.0214, y0, 0, 16))


def _forma_8(x0, x1, folga=0.0028):
    """Abraçadeira em 8 em volta do cano (y = 0) e do tubo (y = TY)."""
    sec = unary_union([Point(0, 0).buffer(RB + folga, 32), Point(0, TY).buffer(TR + folga * 0.5, 32), sbox(-0.0075, TY, 0.0075, 0)])
    return ext_x(sec, x0, x1)


def _marcacao(nome, linhas, w, h, esquerda=False):
    """Gravacao no receptor: placa fina da cor do receptor com letras claras (textura); u invertido no lado esquerdo."""
    W = 1024; H = max(64, int(W * h / w))
    im = Image.new('RGB', (W, H), CORES['aluminio_receptor']); d = ImageDraw.Draw(im)
    for i, (t, tam) in enumerate(linhas):
        texto_c(d, (W // 2, int(H * (i + 0.5) / len(linhas))), t, tam, (150, 150, 146), i == 0, larg=W - 40)
    mat_imagem(nome, im, 0.42, 0.6)
    def uv(v, n, w=w, h=h):
        x0 = MARCA_X[nome]; u = (v[:, 0] - x0) / w
        return np.stack([1 - u if esquerda else u, (v[:, 1] - MARCA_Y[nome]) / h], 1)
    return uv


MARCA_X, MARCA_Y = {}, {}


def _receptor(p, cfg):
    xm, xt, xl = cfg['xm'], cfg['xt'], cfg['xl']
    perfil = arred([(RX0, 0.004), (RX0 + 0.011, RY1), (RX1, RY1), (RX1, -0.03), (RX1 - 0.013, RY0), (RX0, RY0)], 0.0022)
    rec = solido(perfil, -RW, RW, 0.0016)
    pd = arred([(-0.024, -0.04), (0.112, -0.04), (0.112, -0.0185), (0.108, -0.0145), (-0.018, -0.0145), (-0.024, -0.02)], 0.003)
    pe = arred([(-0.024, -0.04), (0.17, -0.04), (0.185, -0.03), (0.185, 0.009), (-0.012, 0.009), (-0.024, 0.0)], 0.004)
    cortes = [caixa(0.12, 0.2, -0.0125, 0.0115, 0.0, 0.03),                    # janela de ejecao (direita)
              caixa(0.115, RX1 - 0.0004, -0.0125, 0.0115, -0.0115, 0.0115),    # caixa do ferrolho
              caixa(0.09, 0.19, -0.06, -0.0125, -0.0118, 0.0118),              # janela de carga (embaixo)
              solido(pd, RW - 0.0007, RW + 0.01),                              # painel rebaixado (direita, embaixo da janela)
              solido(pe, -RW - 0.01, -RW + 0.0007),                            # painel rebaixado (esquerda)
              caixa(-0.02, 0.2, -0.0109, -0.0101, -RW - 0.01, -RW + 0.0006),   # friso (esquerda)
              caixa(-0.02, 0.112, -0.0109, -0.0101, RW - 0.0006, RW + 0.01)]   # friso (direita)
    p.add('aluminio_receptor', menos(rec, *cortes))
    # gravacoes (nome e calibre) nos paineis rebaixados
    for nome, x0, y0, w, h, z, linhas, esq in (('marca_esp_d', -0.016, -0.0375, 0.12, 0.02, RW - 0.0007, [('MUTIRÃO 12', 92), ('BOMBEAMENTO · RECOMEÇO', 40)], False),
                                                ('marca_esp_e', 0.03, -0.034, 0.13, 0.016, -RW + 0.0007, [('CAL. 12 · CÂMARA 76 mm', 52), ('SÓ CARTUCHO 12', 34)], True)):
        MARCA_X[nome] = x0; MARCA_Y[nome] = y0
        uvf = _marcacao(nome, linhas, w, h, esq)
        p.add(nome, caixa(x0, x0 + w, y0, y0 + h, min(z, z + (0.00008 if z > 0 else -0.00008)), max(z, z + (0.00008 if z > 0 else -0.00008))))
        p.uv[nome] = uvf
    # defletor da janela de ejecao e ressalto do destrave
    p.add('aluminio_receptor', solido(arred([(0.196, -0.0125), (0.204, -0.0125), (0.204, 0.0115), (0.196, 0.0115)], 0.0008), RW - 0.0002, RW + 0.0012, 0.0004))
    trilho(p, 'aluminio_receptor', RX0 + 0.006, RX1 - 0.006, RY1, False)
    for (x, y) in ((0.004, -0.04), (0.078, -0.04)):                            # pinos do grupo do gatilho
        for zs in (-1, 1): p.add('aco_inox', cil_z(0.0021, min(zs * RW, zs * (RW + 0.0007)), max(zs * RW, zs * (RW + 0.0007)), x, y, 16))
    # alojamento do gatilho e guarda-mato (polimero)
    cx = arred([(RX0 + 0.001, RY0 + 0.001), (0.088, RY0 + 0.001), (0.088, -0.052), (0.082, -0.0565), (0.0, -0.0565), (RX0 + 0.001, -0.052)], 0.0015)
    p.add('polimero', menos(solido(cx, -0.0128, 0.0128, 0.0012), caixa(0.03, 0.054, -0.07, -0.045, -0.0042, 0.0042)))
    fora = arred([(0.0, -0.054), (0.084, -0.054), (0.084, -0.061), (0.072, -0.08), (0.06, -0.0855), (0.006, -0.0875), (-0.006, -0.078)], 0.006)
    dentro = arred([(0.009, -0.0565), (0.07, -0.0565), (0.072, -0.063), (0.061, -0.077), (0.012, -0.0805), (0.005, -0.071)], 0.0055)
    p.add('polimero', solido(fora.difference(dentro), -0.0058, 0.0058, 0.0014))
    # trava de seguranca (botao transversal com anel vermelho) e alavanca de destrave da telha
    p.add('aco_oxidado', cil_z(0.0034, -0.0138, 0.0138, 0.021, -0.051, 20))
    p.add('tinta_vermelha', cil_z(0.0035, -0.0142, -0.0132, 0.021, -0.051, 20))
    lev = arred([(0.06, -0.0545), (0.085, -0.0545), (0.09, -0.0505), (0.085, -0.048), (0.064, -0.0505)], 0.0012)
    p.add('aco_oxidado', solido(lev, -0.0136, -0.0126, 0.0003))
    for x in np.linspace(0.078, 0.086, 4): p.add('aco_oxidado', caixa(x - 0.0003, x + 0.0003, -0.054, -0.049, -0.0139, -0.0136))
    # cano: reforco da camara, alma, coroa da boca, massa de mira (conta de latao)
    cano = torno_x([(0.0128, RX1 - 0.002), (0.0128, RX1 + 0.034), (RB, RX1 + 0.05), (RB, xm - 0.0015), (RB - 0.0012, xm)], 48)
    cano = menos(cano, cil_x(RA, RX1 - 0.01, xm + 0.01, sec=40), cil_x(0.0104, RX1 - 0.01, RX1 + 0.07, sec=40))
    p.add('aco_oxidado', cano)
    p.add('aco_oxidado', tubo_x(RA, RA + 0.0006, xm - 0.03, xm - 0.0002, sec=40))                      # rosca do choke (dentro)
    p.add('aco_oxidado', solido(arred([(xm - 0.018, RB - 0.001), (xm - 0.006, RB - 0.001), (xm - 0.007, RB + 0.0022), (xm - 0.016, RB + 0.0022)], 0.0008),
                                -0.0018, 0.0018, 0.0004))
    p.add('latao', trimesh.creation.icosphere(2, 0.0019).apply_translation([xm - 0.0115, RB + 0.0035, 0]))
    # tubo do carregador e abraçadeira da ponta (com olhal da bandoleira)
    p.add('aco_oxidado', cil_x(TR, RX1 - 0.01, xt, TY, 0, 48))
    p.add('aco_oxidado', menos(_forma_8(xt - 0.018, xt), cil_x(TR - 0.001, xt - 0.02, xt + 0.01, TY, 0, 32)))
    p.add('aco_oxidado', solido(arred([(xt - 0.014, TY - TR - 0.001), (xt - 0.004, TY - TR - 0.001), (xt - 0.005, TY - TR - 0.006), (xt - 0.013, TY - TR - 0.006)], 0.001),
                                -0.0035, 0.0035))
    alca = Point(xt - 0.009, TY - TR - 0.0105).buffer(0.0062, 32).difference(Point(xt - 0.009, TY - TR - 0.0105).buffer(0.0041, 32))
    p.add('aco_inox', solido(alca, -0.0013, 0.0013, 0.0004))
    # protetor de calor ventilado em cima do cano
    hs0, hs1 = RX1 + 0.04, cfg['hs1']
    capa = inter([tubo_x(RB + 0.0016, RB + 0.003, hs0, hs1, sec=48, ch=0.0005), caixa(hs0 - 0.01, hs1 + 0.01, -0.004, 0.03, -0.03, 0.03)])
    furos = []
    n = int((hs1 - hs0 - 0.03) / 0.022)
    for i in range(n + 1):
        x = hs0 + 0.015 + i * (hs1 - hs0 - 0.03) / max(n, 1)
        furos.append(solido(LineString([(x - 0.0055, 0.0062), (x + 0.0055, 0.0062)]).buffer(0.0024, 16), -0.03, 0.03))       # lados
        if i < n: furos.append(ext_y(LineString([(x + 0.0055, 0), (x + 0.0165, 0)]).buffer(0.0019, 16), -0.01, 0.03))        # topo
    p.add('aco_fosfatado', menos(capa, *furos))
    for x in (hs0, hs1 - 0.006):
        p.add('aco_fosfatado', inter([tubo_x(RB, RB + 0.0034, x, x + 0.006, sec=48), caixa(x - 1, x + 1, -0.005, 0.03, -0.03, 0.03)]))
        for zs in (-1, 1): p.add('aco_inox', cil_z(0.0013, min(zs * (RB + 0.0025), zs * (RB + 0.0042)), max(zs * (RB + 0.0025), zs * (RB + 0.0042)), x + 0.003, 0.0, 12))


CABO12 = suave([(-0.0365, -0.0435), (0.0045, -0.0435), (0.0035, -0.056), (-0.0035, -0.076), (-0.012, -0.1), (-0.0195, -0.125), (-0.0255, -0.146),
                (-0.0295, -0.1535), (-0.0725, -0.1555), (-0.0755, -0.148), (-0.066, -0.12), (-0.0555, -0.088), (-0.0465, -0.062), (-0.0425, -0.05)])
LARG12 = lambda y: 0.0118 + 0.0032 * GT.smooth(-0.046, -0.07, y) + 0.0012 * math.exp(-((y + 0.1) / 0.022) ** 2)


def _punho_12(p):
    """Punho de pistola arredondado: corpo de polimero, area pontilhada com borda lisa, tampa da base com parafuso."""
    p.add('polimero', punho_redondo(CABO12, -0.0435, -0.1555, LARG12, n=2.3, fatias=110, voltas=56, raio_base=0.005))
    lp = lambda y: LARG12(y) + 0.0004
    pont = punho_redondo(CABO12, -0.0435, -0.1555, lp, n=2.3, fatias=110, voltas=56, raio_base=0.005)
    area = CABO12.buffer(-0.0026, join_style=1).intersection(sbox(-1, -0.146, 1, -0.06))
    p.add('polimero_grip', inter([pont, solido(area, -0.05, 0.05)]))
    p.add('aco_inox', torno_x([(0.0, 0.0), (0.0032, 0.0), (0.0032, 0.0006), (0.0024, 0.0011), (0.0, 0.0012)], 20).apply_transform(
        TF.rotation_matrix(-math.pi / 2, [0, 0, 1])).apply_translation([-0.051, -0.1555, 0]))


def _gatilho_12(q):
    """Gatilho curvo com a ponta para a FRENTE (face da frente concava, com estrias); origem no pino (0.041, -0.05)."""
    lam = LineString([(0.0425, -0.051), (0.0405, -0.0575), (0.0392, -0.064), (0.0398, -0.0698), (0.0428, -0.0735)]).buffer(0.0019, cap_style=1, join_style=1)
    q.add('aco_oxidado', solido(lam, -0.004, 0.004, 0.0012))
    for i in range(4):
        y = -0.06 - i * 0.0022
        q.add('aco_oxidado', caixa(0.0372, 0.0378, y - 0.0003, y + 0.0003, -0.0038, 0.0038))


def _telha(q, cfg):
    """Telha (guarda-mao que bombeia): corpo arredondado com aneis de pega e aba na frente, barras de acao ate o ferrolho."""
    f0 = cfg['f0']; f1 = f0 + cfg['fl']
    perfil = suave([(f0, -0.0115), (f1, -0.0115), (f1 + 0.002, -0.017), (f1 + 0.0015, -0.0505), (f1 - 0.007, -0.0525), (f1 - 0.015, -0.0468),
                    (f0 + 0.016, -0.0468), (f0 + 0.006, -0.0505), (f0 - 0.002, -0.049), (f0 - 0.002, -0.017)], 3)
    larg = lambda x: 0.0198 + 0.0018 * (GT.smooth(f1 - 0.022, f1, x) + GT.smooth(f0 + 0.022, f0, x))
    fora = corpo_x(perfil, f1 + 0.003, f0 - 0.003, larg, n=2.5, fatias=120, voltas=56, raio_tras=0.003, raio_frente=0.003)
    miolo = corpo_x(perfil.buffer(-0.0013), f1 + 0.002, f0 - 0.002, lambda x: larg(x) - 0.0013, n=2.5, fatias=120, voltas=56,
                    raio_tras=0.002, raio_frente=0.002)
    lim0, lim1 = f0 + 0.026, f1 - 0.026
    q.add('polimero', inter([fora, caixa(f0 - 0.01, lim0, -1, 1, -1, 1)]))
    q.add('polimero', inter([fora, caixa(lim1, f1 + 0.01, -1, 1, -1, 1)]))
    q.add('polimero', inter([miolo, caixa(lim0 - 0.001, lim1 + 0.001, -1, 1, -1, 1)]))
    x = lim0 + 0.003
    while x + 0.0045 < lim1:                                                       # aneis de pega
        q.add('polimero', inter([fora, caixa(x, x + 0.0042, -1, 1, -1, 1)])); x += 0.0075
    for zs in (-1, 1):                                                             # barras de acao
        q.add('aco_oxidado', caixa(RX1 - 0.03, f0 + 0.01, -0.0215, -0.0175, min(zs * 0.0114, zs * 0.0134), max(zs * 0.0114, zs * 0.0134)))
    q.add('aco_oxidado', tubo_x(TR + 0.0002, TR + 0.0012, f0 - 0.003, f0 + 0.004, TY, sec=40))   # bucha da telha


def _ferrolho_12(q):
    """Ferrolho (aparece pela janela de ejecao): bloco com face, percussor, unha do extrator e ranhura."""
    b = solido(arred([(0.136, -0.0122), (RX1 - 0.0006, -0.0122), (RX1 - 0.0006, 0.0112), (0.136, 0.0112)], 0.0015), -0.0112, 0.0112, 0.0012)
    b = menos(b, caixa(0.14, 0.188, -0.0035, 0.0035, 0.0095, 0.02), cil_x(0.0012, RX1 - 0.003, RX1 + 0.01, 0, 0, 12),
              *[caixa(0.142, 0.186, y - 0.0004, y + 0.0004, 0.0106, 0.02) for y in (-0.0085, 0.0075)])
    q.add('aco_fosfatado', b)
    q.add('aco_oxidado', solido(arred([(0.19, 0.003), (RX1 + 0.0008, 0.003), (RX1 + 0.0008, 0.0085), (0.19, 0.0085)], 0.0006), 0.0098, 0.0114, 0.0002))
    q.add('aco_oxidado', cil_x(0.0009, RX1 - 0.0012, RX1 - 0.0003, 0, 0, 10))


def _elevador(q):
    lam = arred([(0.095, -0.0446), (0.178, -0.0446), (0.186, -0.0415), (0.178, -0.0405), (0.095, -0.0408)], 0.0008)
    q.add('aco_oxidado', menos(solido(lam, -0.0104, 0.0104, 0.0004), caixa(0.12, 0.165, -0.05, -0.03, -0.0035, 0.0035)))


def _espingarda(A, cfg, curta):
    A.pivo = (-0.033, -0.09, 0.0)
    _receptor(A.base, cfg)
    _punho_12(A.base)
    xm, xt, xl = cfg['xm'], cfg['xt'], cfg['xl']
    gat = A.parte('gatilho', (0.041, -0.05, 0), explodir=(0.02, -0.06, 0), tipo='gira', eixo='x', curso_graus=-12, descricao='puxa para trás')
    _gatilho_12(gat)
    tel = A.parte('telha', (cfg['f0'], TY, 0), explodir=(0.08, -0.05, 0), tipo='desliza', curso_m=-C12,
                  descricao=f'bombeia: puxa {int(C12 * 1000)} mm para trás (ejeta) e volta (põe outro cartucho na câmara)')
    _telha(tel, cfg)
    fer = A.parte('ferrolho', (RX1, 0, 0), pai='telha', explodir=(-0.05, 0.05, 0.03), tipo='desliza', curso_m=-C12,
                  descricao='anda junto com a telha (barras de ação)')
    _ferrolho_12(fer)
    ele = A.parte('elevador', (0.095, -0.0425, 0), explodir=(0.0, -0.05, 0), tipo='gira', eixo='x', curso_graus=12,
                  descricao='levanta o cartucho do tubo até a câmara durante o bombeamento')
    _elevador(ele)
    tam = A.parte('tampa_tubo', (xt, TY, 0), explodir=(0.05, 0, 0), tipo='fixa', descricao='tampa do tubo (troca pelo prolongador)')
    _tampa_tubo(tam, xt, TY)
    A.encaixe('encaixe_mira', (0.1, RY1 + 0.0055, 0), 'trilho_mira', explodir=(0, 0.05, 0), aceita=['mira_ponto_vermelho_tubo'])
    A.encaixe('encaixe_coronha', (RX0, -0.004, 0), 'coronha_12', explodir=(-0.08, 0, 0), aceita=['coronha_retratil_12', 'coronha_fixa_12'],
              **({} if curta else {'padrao': 'coronha_retratil_12'}),
              descricao='sem coronha fica só o punho de pistola (mais curta e leve, mas recua muito)')
    A.encaixe('encaixe_boca', (xm, 0, 0), 'boca_12', explodir=(0.06, 0, 0), aceita=['choke_estendido_12', 'freio_rompimento_12'],
              **({'padrao': 'freio_rompimento_12'} if curta else {}))
    if not curta:
        A.encaixe('encaixe_tubo', (xt, TY, 0), 'tubo_12', substitui='tampa_tubo', explodir=(0.05, 0, 0), aceita=['tampa_tubo_12', 'prolongador_tubo_12'],
                  descricao='ao pôr o prolongador aqui, esconda as malhas do nó tampa_tubo')
    A.encaixe('encaixe_cano', (xl, TY / 2, 0), 'cano_12', explodir=(0.0, 0.0, 0.05), aceita=['lanterna_cano_12'])
    A.encaixe('encaixe_lateral', (0.13, -0.014, -RW), 'lateral_12', explodir=(0.0, 0.0, -0.05), aceita=['porta_cartuchos_lateral_12'])
    A.encaixe('encaixe_bandoleira', (xt - 0.009, TY - TR - 0.0105, 0), 'bandoleira', explodir=(0, -0.04, 0), aceita=['bandoleira'])
    A.encaixe('boca_fogo', (xm, 0, 0), 'efeito', descricao='clarão de boca e origem dos bagos (raycast em cone para -Z)')
    A.encaixe('saida_estojo', (0.165, 0.0, RW), 'efeito', descricao='onde nasce a casca ejetada (aos 0,36 s do "atirar")')
    A.encaixe('entrada_cartucho', (0.14, RY0, 0), 'efeito', descricao='janela de carga: onde a mão empurra cada cartucho')
    A.encaixe('mira_ferro', (RX0 + 0.01, RY1 + 0.0055, 0), 'mira', descricao='linha de visada: topo do trilho -> conta de latão')
    # ---- animacoes
    tel_t = lambda ks: ('telha', 't', pose([(t, (dx, 0, 0)) for t, dx in ks]))
    coice = [(None, 'r', (0, 0, 1), pose([(0, 0), (0.02, 0), (0.06, 10), (0.24, 0)])),
             ('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.02, -12), (0.08, -12), (0.15, 0)]))]
    A.anim('atirar', 0.8, coice + [
        (None, 't', pose([(0, (0, 0, 0)), (0.02, (0, 0, 0)), (0.05, (-0.032, 0.006, 0)), (0.22, (0, 0, 0)), (0.34, (0.0, -0.003, 0)),
                          (0.5, (0.0, -0.003, 0)), (0.62, (0, 0, 0))])),
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.24, 0), (0.36, -6), (0.55, -6), (0.7, 0)])),
        tel_t([(0, 0), (0.26, 0), (0.37, -C12), (0.45, -C12), (0.57, 0), (0.8, 0)]),
        ('elevador', 'r', (0, 0, 1), pose([(0, 0), (0.36, 0), (0.42, 12), (0.5, 12), (0.56, 0)]))],
        desc='tiro e bombeamento: coice, telha para trás (0,37 s: soltar a casca em saida_estojo aos 0,36 s) e para a frente')
    A.anim('atirar_ultimo', 0.6, coice + [
        (None, 't', pose([(0, (0, 0, 0)), (0.02, (0, 0, 0)), (0.05, (-0.032, 0.006, 0)), (0.22, (0, 0, 0))])),
        tel_t([(0, 0), (0.26, 0), (0.37, -C12), (0.6, -C12)])],
        desc='último tiro: bombeia, ejeta e deixa a telha atrás (ação aberta, tubo vazio)')
    A.anim('vazia', 0.1, [tel_t([(0, -C12), (0.1, -C12)])], laco=True, desc='pose parada: ação aberta')
    A.anim('recarregar', 0.55, [
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.12, 26), (0.43, 26), (0.55, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.12, 8), (0.43, 8), (0.55, 0)])),
        ('elevador', 'r', (0, 0, 1), pose([(0, 0), (0.2, 0), (0.26, 6), (0.36, 6), (0.4, 0)]))],
        desc='põe UM cartucho pela janela de carga (0,3 s); repita por cartucho (a recarga pode ser interrompida para atirar)')
    A.anim('recarregar_vazia', 1.3, [
        tel_t([(0, -C12), (0.75, -C12), (0.9, 0), (1.3, 0)]),
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, -35), (0.7, -35), (0.95, 0)])),
        (None, 't', pose([(0, (0, 0, 0)), (0.75, (0, 0, 0)), (0.85, (0.006, -0.002, 0)), (1.0, (0, 0, 0))])),
        ('elevador', 'r', (0, 0, 1), pose([(0, 12), (0.75, 12), (0.85, 0)]))],
        desc='ação aberta: põe um cartucho direto na janela de ejeção (0,45 s) e fecha a telha (0,9 s); depois carregue o tubo')
    A.anim('inspecionar', 2.6, [
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.4, 40), (1.0, 40), (1.5, -40), (2.1, -40), (2.6, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 10), (2.1, 10), (2.6, 0)])),
        tel_t([(0, 0), (1.55, 0), (1.7, -0.03), (1.95, -0.03), (2.05, 0)])],
        desc='mostra a janela de carga, depois a de ejeção e abre a ação até ver o cartucho na câmara')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.6), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


DADOS12 = dict(classe='fogo', calibre='12', municao='municao_12_chumbo', municoes_aceitas=['municao_12_chumbo', 'municao_12_balote'],
               modo='bombeamento (ação manual)', acao='bombeamento', recarga_por_cartucho=True, estojo_s=0.36, bagos=9)


@arma('espingarda_12', 'Espingarda Mutirão 12', 'armas', 'espingarda', capacidade=5, dano=150, dispersao_graus=4.5, alcance_m=15,
      alcance_max_m=40, tiros_por_s=1.3, recarga_s=0.55, recarga_vazia_s=1.3, precisao=0.45, recuo=0.75, ruido_m=110, durabilidade=900,
      peso_kg=3.4, raridade='incomum', valor_troca=70, onde=['quartel', 'casa_de_campo', 'armazem', 'posto', 'delegacia'], **DADOS12,
      descricao='Espingarda de bombeamento com coronha retrátil, punho de pistola, protetor de calor e trilho. 5 no tubo; '
                'a curta distância derruba qualquer zumbi, mas o estrondo chama tudo num raio de 110 m. Recarrega um cartucho por vez.')
def espingarda_12(A): _espingarda(A, ESP_LONGA, False)


@arma('espingarda_12_curta', 'Espingarda Mutirão 12 curta', 'armas', 'espingarda', capacidade=4, dano=150, dispersao_graus=6.0, alcance_m=12,
      alcance_max_m=30, tiros_por_s=1.3, recarga_s=0.55, recarga_vazia_s=1.3, precisao=0.38, recuo=0.85, ruido_m=120, durabilidade=900,
      peso_kg=2.7, raridade='raro', valor_troca=80, onde=['quartel', 'delegacia'], **DADOS12,
      descricao='Versão de cano curto e só punho, com freio dentado na boca: boa para arrombar portas e lutar dentro de casa. '
                'Espalha mais os bagos e coice forte; aceita coronha.')
def espingarda_12_curta(A): _espingarda(A, ESP_CURTA, True)


# ---------------------------------------------------------------------------- acessorios da espingarda
@_acessorio('coronha_retratil_12', 'Coronha retrátil (espingarda)', 'coronha', 'coronha_12', peso_kg=0.42, raridade='incomum', valor_troca=20,
            modificadores={'recuo': 0.6, 'precisao': 1.35}, posicoes=5, onde=['quartel', 'delegacia'],
            descricao='Tubo com coronha de polímero que corre em 5 posições (nó "soleira", animações estender/recolher). Segura o coice no ombro.')
def coronha_retratil_12(A):
    q = A.base
    q.add('aco_oxidado', torno_x([(0.0, -0.003), (0.0172, -0.003), (0.0175, -0.0015), (0.0172, 0.0), (0.0, 0.0)], 48))       # placa de trás
    q.add('aco_oxidado', cil_z(0.0042, -0.0198, -0.0172, -0.0015, -0.0005, 20))                                               # tomada QD
    porca = torno_x([(0.0, -0.013), (0.0168, -0.013), (0.0168, -0.003), (0.0, -0.003)], 48)
    for i in range(6):
        g = caixa(-0.0095, -0.0065, -0.003, 0.03, -0.0022, 0.0022); g.apply_transform(TF.rotation_matrix(i * math.pi / 3, [1, 0, 0])); porca = menos(porca, g)
    q.add('aco_oxidado', porca)
    q.add('aluminio_preto', cil_x(0.0145, -0.215, -0.012, 0, 0, 48))
    q.add('aluminio_preto', torno_x([(0.0, -0.217), (0.0138, -0.217), (0.0145, -0.215), (0.0, -0.215)], 48))
    q.add('aluminio_preto', menos(caixa(-0.21, -0.014, -0.0182, -0.0135, -0.0035, 0.0035),
                                  *[caixa(-0.072 - i * 0.016 - 0.002, -0.072 - i * 0.016 + 0.002, -0.0195, -0.0165, -0.004, 0.004) for i in range(5)]))
    sol = A.parte('soleira', (0, 0, 0), explodir=(-0.08, 0, 0), tipo='desliza', curso_m=-0.064, descricao='corre no tubo, 5 posições de 16 mm')
    perfil = suave([(-0.098, 0.0175), (-0.17, 0.0195), (-0.246, 0.025), (-0.258, 0.026), (-0.2735, 0.024), (-0.276, -0.112), (-0.27, -0.122),
                    (-0.25, -0.123), (-0.2, -0.078), (-0.14, -0.034), (-0.104, -0.022), (-0.097, -0.012)], 3)
    larg = lambda x: 0.0172 + 0.0042 * GT.smooth(-0.1, -0.22, x)
    corpo = corpo_x(perfil, -0.093, -0.28, larg, n=2.6, fatias=130, voltas=56, raio_tras=0.006, raio_frente=0.004)
    furo = arred([(-0.16, -0.044), (-0.205, -0.08), (-0.232, -0.098), (-0.236, -0.05), (-0.226, -0.036), (-0.17, -0.034)], 0.006)
    corpo = menos(corpo, cil_x(0.0148, -0.3, -0.08, 0, 0, 48), solido(furo, -0.05, 0.05), cil_z(0.0045, -0.05, 0.05, -0.257, -0.105, 24))
    sol.add('polimero', inter([corpo, caixa(-0.262, 0.0, -1, 1, -1, 1)]))
    sol.add('borracha', inter([corpo, caixa(-0.3, -0.2618, -1, 1, -1, 1)]))
    lev = arred([(-0.104, -0.019), (-0.138, -0.022), (-0.142, -0.027), (-0.106, -0.027)], 0.0015)
    sol.add('polimero', solido(lev, -0.004, 0.004, 0.0008))
    A.anim('estender', 0.5, [('soleira', 't', pose([(0, (0, 0, 0)), (0.5, (-0.064, 0, 0))]))], desc='abre a coronha até a última posição')
    A.anim('recolher', 0.5, [('soleira', 't', pose([(0, (-0.064, 0, 0)), (0.5, (0, 0, 0))]))], desc='fecha a coronha')
    A.encaixe('ombro', (-0.276, -0.05, 0), 'efeito', pai='soleira', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


@_acessorio('coronha_fixa_12', 'Coronha fixa de polímero (espingarda)', 'coronha', 'coronha_12', peso_kg=0.6, raridade='comum', valor_troca=12,
            modificadores={'recuo': 0.55, 'precisao': 1.4}, onde=['casa_de_campo', 'armazem', 'casas'],
            descricao='Coronha inteiriça com soleira de borracha e porta-bandoleira. Mais pesada e firme que a retrátil.')
def coronha_fixa_12(A):
    q = A.base
    perfil = suave([(0.0, 0.0205), (-0.04, 0.0205), (-0.2, 0.0235), (-0.322, 0.027), (-0.334, 0.024), (-0.338, -0.118), (-0.33, -0.129),
                    (-0.31, -0.128), (-0.22, -0.094), (-0.11, -0.058), (-0.035, -0.045), (0.0, -0.0425)], 3)
    larg = lambda x: 0.0135 + 0.0068 * GT.smooth(-0.01, -0.2, x)
    corpo = corpo_x(perfil, 0.0, -0.342, larg, n=2.5, fatias=150, voltas=56, raio_tras=0.006, raio_frente=0.0015)
    q.add('polimero', inter([corpo, caixa(-0.3225, 0.01, -1, 1, -1, 1)]))
    q.add('borracha', inter([corpo, caixa(-0.36, -0.322, -1, 1, -1, 1)]))
    for zs in (-1, 1):
        q.add('aco_inox', cil_z(0.0024, min(zs * 0.0128, zs * 0.0148), max(zs * 0.0128, zs * 0.0148), -0.012, -0.012, 16))      # parafuso
    stud = cil_x(0.0026, 0, 0.006, sec=16); stud.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])); stud.apply_translation([-0.285, -0.118, 0])
    q.add('aco_inox', stud)
    alca = Point(-0.285, -0.1265).buffer(0.0062, 32).difference(Point(-0.285, -0.1265).buffer(0.0041, 32))
    q.add('aco_inox', solido(alca, -0.0013, 0.0013, 0.0004))
    A.encaixe('ombro', (-0.338, -0.05, 0), 'efeito', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


@_acessorio('tampa_tubo_12', 'Tampa do tubo (espingarda)', 'tubo', 'tubo_12', peso_kg=0.04, raridade='comum', modificadores={},
            descricao='A tampa recartilhada que vem na espingarda.')
def tampa_tubo_12(A): _tampa_tubo(A.base, 0.0, 0.0); A.pivo = (0, 0, 0)


@_acessorio('prolongador_tubo_12', 'Prolongador do tubo (+1)', 'tubo', 'tubo_12', peso_kg=0.15, raridade='raro', valor_troca=18,
            capacidade_extra=1, modificadores={}, onde=['quartel', 'delegacia'],
            descricao='Estende o tubo do carregador até a boca: um cartucho a mais, preso ao cano por uma abraçadeira.')
def prolongador_tubo_12(A):
    q = A.base; L = 0.072
    q.add('aco_oxidado', cil_x(TR, -0.004, L, 0, 0, 48))
    q.add('aco_oxidado', tubo_x(TR, TR + 0.0012, -0.002, 0.008, sec=48, ch=0.0004))
    ab = _forma_8(L - 0.017, L - 0.003); ab.apply_translation([0, -TY, 0])
    q.add('aluminio_preto', menos(ab, cil_x(RB + 0.0004, L - 0.02, L, -TY, 0, 40)))
    for zs in (-1, 1): q.add('aco_inox', cil_z(0.0018, min(zs * 0.0075, zs * 0.0088), max(zs * 0.0075, zs * 0.0088), L - 0.01, -TY / 2, 12))
    _tampa_tubo(q, L, 0.0)
    A.pivo = (0, 0, 0)


@_acessorio('choke_estendido_12', 'Choke estendido com portas', 'boca', 'boca_12', peso_kg=0.07, raridade='raro', valor_troca=22,
            modificadores={'dispersao_graus': 0.6, 'alcance_m': 1.3, 'recuo': 0.9}, onde=['quartel', 'casa_de_campo'],
            descricao='Aperta o tiro: os bagos espalham menos e vão mais longe. As portas no topo seguram o cano.')
def choke_estendido_12(A):
    q = A.base
    c = torno_x([(RA + 0.0003, -0.03), (RB + 0.0012, -0.0005), (RB + 0.0014, 0.0005), (RB + 0.0014, 0.029), (RB + 0.0004, 0.0315), (RA - 0.0012, 0.0318)], 48)
    cortes = [cil_x(RA - 0.0014, -0.04, 0.04, sec=40)]
    for x in (0.008, 0.015, 0.022):
        for a in (-35, 0, 35):
            g = caixa(x - 0.0018, x + 0.0018, 0.0, 0.03, -0.0016, 0.0016); g.apply_transform(TF.rotation_matrix(math.radians(a), [1, 0, 0])); cortes.append(g)
    q.add('aco_oxidado', menos(c, *cortes))
    q.add('recartilhado', tubo_x(RB + 0.001, RB + 0.0019, 0.0245, 0.0295, sec=48))
    A.pivo = (0, 0, 0)


@_acessorio('freio_rompimento_12', 'Freio dentado de arrombamento', 'boca', 'boca_12', peso_kg=0.12, raridade='raro', valor_troca=20,
            modificadores={'recuo': 0.85, 'dano_coronhada': 1.6, 'ruido_m': 1.1}, onde=['quartel', 'delegacia'],
            descricao='Boca com dentes de aço e janelas laterais: segura o cano e serve para quebrar vidro e golpear zumbis de perto.')
def freio_rompimento_12(A):
    q = A.base; R = 0.0148
    c = torno_x([(RA + 0.0003, -0.02), (R - 0.001, -0.004), (R, -0.003), (R, 0.04), (R - 0.0015, 0.042), (RA + 0.0012, 0.042)], 48)
    cortes = [cil_x(RA + 0.0006, -0.03, 0.06, sec=40)]
    for i in range(3):                                                             # dentes: tres vales na coroa
        g = solido(Polygon([(0.026, -0.0), (0.044, -0.008), (0.044, 0.008)]), -0.03, 0.03)
        g = inter([g, caixa(0.02, 0.05, -0.0045, 0.0045, 0, 0.03)]); g.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 3 + math.pi / 2, [1, 0, 0]))
        cortes.append(g)
    for zs in (-1, 1):
        for x in (0.006, 0.016):
            cortes.append(caixa(x, x + 0.0065, -0.0045, 0.0045, min(zs * 0.008, zs * 0.03), max(zs * 0.008, zs * 0.03)))
    q.add('aco_fosfatado', menos(c, *cortes))
    for i in range(3):
        a = i * 2 * math.pi / 3 + math.pi / 6; s = cil_z(0.0018, R - 0.0004, R + 0.0006, 0.034, 0, 12)
        s.apply_transform(TF.rotation_matrix(a, [1, 0, 0])); q.add('aco_inox', s)
    A.pivo = (0, 0, 0)


@_acessorio('lanterna_cano_12', 'Lanterna de cano (espingarda)', 'lanterna', 'cano_12', peso_kg=0.2, raridade='incomum', valor_troca=28,
            usa='pilhas', autonomia_min=80, luz={'alcance_m': 45, 'angulo_graus': 18, 'lumens': 800}, modificadores={},
            onde=['quartel', 'posto', 'delegacia'], liga_desliga='SpotLight3D no encaixe "feixe" (para -Z)',
            descricao='Abraçadeira no cano e no tubo com lanterna de 800 lm do lado direito e botão de pressão.')
def lanterna_cano_12(A):
    q = A.base; yc = -TY / 2                                                        # cano em y = +0.0125, tubo em y = -0.0125 (pivo no meio)
    ab = _forma_8(-0.011, 0.011, 0.0032); ab.apply_translation([0, yc, 0])
    ab = menos(ab, cil_x(RB + 0.0004, -0.02, 0.02, yc, 0, 40), cil_x(TR + 0.0004, -0.02, 0.02, yc + TY, 0, 40))
    q.add('aluminio_preto', ab)
    q.add('aluminio_preto', solido(arred([(-0.011, -0.012), (0.011, -0.012), (0.011, 0.006), (-0.011, 0.006)], 0.002), 0.008, 0.024, 0.0015))
    zl, yl = 0.031, -0.003
    q.add('aluminio_preto', torno_x([(0.0, -0.06), (0.0115, -0.06), (0.0128, -0.058), (0.0128, 0.012), (0.0158, 0.019), (0.0158, 0.03), (0.0, 0.03)], 40, yl, zl))
    for x in np.linspace(-0.05, -0.012, 10): q.add('aluminio_preto', tubo_x(0.0126, 0.0136, x, x + 0.0018, yl, zl, sec=40))
    q.add('recartilhado', tubo_x(0.0157, 0.0163, 0.019, 0.029, yl, zl, sec=40))
    q.add('aco_inox', tubo_x(0.011, 0.0159, 0.0292, 0.0305, yl, zl, sec=40))
    q.add('refletor', torno_x([(0.004, 0.02), (0.0112, 0.0292)], 32, yl, zl))
    q.add('led_lanterna', cil_x(0.0035, 0.0198, 0.0206, yl, zl, 16))
    q.add('lente', cil_x(0.0112, 0.0289, 0.0295, yl, zl, 40))
    q.add('borracha', torno_x([(0.0, -0.068), (0.009, -0.068), (0.0105, -0.064), (0.0105, -0.06), (0.0, -0.06)], 32, yl, zl))
    A.encaixe('feixe', (0.0305, yl, zl), 'efeito', descricao='SpotLight3D aqui (-Z)')
    A.pivo = (0, 0, 0)


@_acessorio('porta_cartuchos_lateral_12', 'Porta-cartuchos lateral (6)', 'porta_cartuchos', 'lateral_12', peso_kg=0.26, raridade='incomum',
            valor_troca=15, leva=6, municao='municao_12_chumbo', modificadores={'recarga_s': 0.85}, onde=['quartel', 'casa_de_campo', 'delegacia'],
            descricao='Placa no lado esquerdo do receptor com 6 cartuchos à mão: recarrega mais rápido e leva 6 tiros a mais na arma.')
def porta_cartuchos_lateral_12(A):
    q = A.base; passo = 0.0228; xs = [(i - 2.5) * passo for i in range(6)]; zc = -0.0032 - 0.0106
    q.add('aluminio_preto', solido(arred([(-0.069, -0.02), (0.069, -0.02), (0.069, 0.02), (-0.069, 0.02)], 0.004), -0.0032, 0.0, 0.0008))
    berco = solido(arred([(-0.0695, -0.016), (0.0695, -0.016), (0.0695, 0.016), (-0.0695, 0.016)], 0.003), -0.0175, -0.0028, 0.0012)
    furos = [trimesh.creation.cylinder(radius=0.0103, height=0.06, sections=32).apply_translation([x, 0, zc]) for x in xs]
    for f in furos: f.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0], point=[0, 0, zc]))
    q.add('polimero', menos(berco, *furos, caixa(-0.08, 0.08, -0.012, 0.012, -0.03, zc - 0.006)))
    Rv = TF.rotation_matrix(math.pi / 2, [0, 0, 1])
    cart = _cartucho_12(sec=20)
    for x in xs: q.merge(cart, TF.translation_matrix([x, -0.036, zc]) @ Rv)
    for x in (-0.058, 0.058): q.add('aco_inox', cil_z(0.0024, -0.0045, -0.0028, x, 0.0, 16))
    A.pivo = (0, 0, 0)


@_acessorio('mira_ponto_vermelho_tubo', 'Mira de ponto vermelho de tubo', 'mira', 'trilho_mira', peso_kg=0.16, raridade='raro', valor_troca=45,
            usa='pilhas', autonomia_min=4000, modificadores={'precisao_mirando': 1.3, 'tempo_mirar': 0.8}, onde=['quartel', 'galeria', 'delegacia'],
            linha_de_visada='encaixe "olho"', descricao='Tubo de 30 mm com tampas basculantes (nós "tampa_frente" e "tampa_tras"), '
            'trava de alavanca no trilho e torres de ajuste. Serve em toda arma com trilho de cima.')
def mira_ponto_vermelho_tubo(A):
    q = A.base; yc = 0.03; R = 0.0145
    q.add('aluminio_preto', solido(arred([(-0.022, -0.0005), (0.022, -0.0005), (0.022, 0.009), (-0.022, 0.009)], 0.0015), -0.0135, 0.0135, 0.0012))
    for zs in (-1, 1):                                                              # garras do trilho
        q.add('aluminio_preto', caixa(-0.02, 0.02, -0.0058, 0.0, min(zs * 0.0106, zs * 0.0135), max(zs * 0.0106, zs * 0.0135)))
    q.add('aco_oxidado', cil_z(0.0028, -0.016, 0.016, 0.0, -0.0035, 16))
    lev = arred([(-0.004, -0.008), (0.024, -0.004), (0.026, 0.0), (-0.002, 0.0)], 0.0015)
    q.add('aluminio_preto', solido(lev, 0.0135, 0.0158, 0.0005))
    q.add('aluminio_preto', solido(arred([(-0.016, 0.006), (0.016, 0.006), (0.012, yc - R + 0.002), (-0.012, yc - R + 0.002)], 0.002), -0.008, 0.008, 0.001))
    corpo = torno_x([(0.0, -0.034), (0.0158, -0.034), (0.0162, -0.031), (0.0162, -0.022), (R, -0.019), (R, 0.022), (0.0172, 0.027), (0.0172, 0.038),
                     (0.0, 0.038)], 56, yc)
    q.add('aluminio_preto', menos(corpo, cil_x(0.0132, -0.04, -0.028, yc, 0, 48), cil_x(0.0152, 0.032, 0.045, yc, 0, 48)))
    q.add('lente', cil_x(0.0133, -0.0285, -0.028, yc, 0, 48)); q.add('lente', cil_x(0.0153, 0.0322, 0.0328, yc, 0, 48))
    q.add('ponto_vermelho', caixa(0.0318, 0.032, yc - 0.0003, yc + 0.0003, -0.0003, 0.0003))
    for (zs, ys) in ((0, 1), (1, 0)):                                               # torres: em cima (altura) e na direita (deriva)
        t = trimesh.creation.cylinder(radius=0.0068, height=0.008, sections=32); t2 = trimesh.creation.cylinder(radius=0.0072, height=0.004, sections=32)
        for m, o in ((t, R + 0.003), (t2, R + 0.008)):
            if ys: m.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0])); m.apply_translation([0.0, yc + o, 0])
            else: m.apply_translation([0.0, yc, o])
        q.add('aluminio_preto', t); q.add('recartilhado', t2)
    q.add('aluminio_preto', solido(arred([(-0.016, yc - 0.004), (-0.004, yc - 0.004), (-0.004, yc + 0.004), (-0.016, yc + 0.004)], 0.002), -0.021, -0.012, 0.001))
    q.add('borracha', cil_z(0.0032, -0.0225, -0.0205, -0.01, yc, 20))               # botao de brilho (esquerda)
    for no, x, s in (('tampa_frente', 0.038, 1), ('tampa_tras', -0.034, -1)):     # tampas basculantes (modeladas abertas)
        hy = yc + 0.0185; tp = A.parte(no, (x, hy, 0), explodir=(0.03 * s, 0.03, 0), tipo='gira', eixo='z', curso_graus=-150 * s,
                                        descricao='tampa basculante (aberta; animação fechar_tampas)')
        disco = torno_x([(0.0, 0.0), (0.0178, 0.0), (0.0178, 0.0035 * s), (0.0, 0.0035 * s)] if s > 0 else
                        [(0.0, 0.0035 * s), (0.0178, 0.0035 * s), (0.0178, 0.0), (0.0, 0.0)], 48, yc)
        disco.apply_translation([x, 0, 0])
        disco = uniao([disco, caixa(x + (0.0 if s > 0 else -0.0035), x + (0.0035 if s > 0 else 0.0), yc + 0.016, hy + 0.003, -0.006, 0.006)])
        disco.apply_transform(TF.rotation_matrix(math.radians(150 * s), [0, 0, 1], point=[x, hy, 0]))
        tp.add('polimero', disco)
    A.anim('fechar_tampas', 0.3, [('tampa_frente', 'r', (0, 0, 1), pose([(0, 0), (0.3, -150)])), ('tampa_tras', 'r', (0, 0, 1), pose([(0, 0), (0.3, 150)]))],
           desc='fecha as duas tampas sobre as lentes')
    A.anim('abrir_tampas', 0.25, [('tampa_frente', 'r', (0, 0, 1), pose([(0, -150), (0.25, 0)])), ('tampa_tras', 'r', (0, 0, 1), pose([(0, 150), (0.25, 0)]))],
           desc='abre as tampas (mola)')
    A.encaixe('olho', (-0.034, yc, 0), 'mira', descricao='ocular: linha de visada')
    A.pivo = (0, 0, 0)


@_acessorio('bandoleira', 'Bandoleira de náilon', 'bandoleira', 'bandoleira', peso_kg=0.15, raridade='comum', valor_troca=6,
            modificadores={'tempo_sacar': 0.85}, onde=['quartel', 'casas', 'armazem', 'galeria'],
            descricao='Correia de náilon com mosquetão: a arma fica pendurada no ombro e libera as mãos para carregar coisas.')
def bandoleira(A):
    q = A.base; ax, ay = -0.83, -0.06                                              # ponta de tras (perto da base da coronha)
    ts = np.linspace(0, 1, 60)
    pts = [(ax * t, -0.009 * (1 - t) + ay * t - 0.11 * 4 * t * (1 - t)) for t in ts]
    tira = LineString(pts).buffer(0.0013, cap_style=2, join_style=1)
    q.add('nylon', solido(tira, -0.0125, 0.0125))
    for t in (0.18, 0.62):                                                          # passadores de regulagem
        i = int(t * 59); x, y = pts[i]
        q.add('polimero', caixa(x - 0.012, x + 0.012, y - 0.0035, y + 0.0035, -0.0145, 0.0145))
    gancho = Point(0, 0).buffer(0.0062, 24).difference(Point(0, 0).buffer(0.0042, 24)).difference(sbox(-0.0015, 0.0, 0.0015, 0.01))
    q.add('aco_inox', solido(gancho, -0.0012, 0.0012, 0.0003))
    q.add('aco_oxidado', solido(arred([(-0.006, -0.012), (0.006, -0.012), (0.004, -0.0055), (-0.004, -0.0055)], 0.001), -0.004, 0.004, 0.0005))
    q.add('aco_inox', solido(Point(ax, ay).buffer(0.0062, 24).difference(Point(ax, ay).buffer(0.0042, 24)), -0.0012, 0.0012, 0.0003))
    A.pivo = (0, 0, 0)


# ---------------------------------------------------------------------------- municao 12
@arma('municao_12_chumbo', 'Cartucho 12 chumbo grosso', 'municao', 'municao', calibre='12', peso_kg=0.04, empilha=25, raridade='comum',
      bagos=9, estojo='estojo_12', onde=['quartel', 'casa_de_campo', 'armazem', 'posto', 'delegacia'],
      descricao='Casca vermelha com 9 bagos: estrago enorme de perto, espalha com a distância.')
def municao_12_chumbo(A): A.base.merge(_cartucho_12(), TF.translation_matrix([-0.0345, 0.0113, 0])); A.pivo = (0, 0, 0)


@arma('municao_12_balote', 'Cartucho 12 balote', 'municao', 'municao', calibre='12', peso_kg=0.042, empilha=25, raridade='incomum',
      bagos=1, estojo='estojo_12', muda={'dano': 120, 'alcance_m': 50, 'dispersao_graus': 0.8, 'precisao': 1.4},
      onde=['quartel', 'casa_de_campo', 'delegacia'], descricao='Casca verde com um projétil só de chumbo: alcance de 50 m e atravessa portas.')
def municao_12_balote(A): A.base.merge(_cartucho_12('casca_verde', balote=True), TF.translation_matrix([-0.0345, 0.0113, 0])); A.pivo = (0, 0, 0)


@arma('estojo_12', 'Casca 12 (vazia)', 'municao', 'estojo', calibre='12', peso_kg=0.008,
      descricao='Casca ejetada no bombeamento (aos 0,36 s do "atirar"). Na bancada vira casca para recarregar.')
def estojo_12(A): A.base.merge(_cartucho_12(vazio=True, sec=24), TF.translation_matrix([-0.036, 0, 0])); A.pivo = (0, 0, 0)


CX12 = dict(x0=-0.0605, x1=0.0605, y0=0.0, y1=0.075, z0=-0.0605, z1=0.0605)
ATLAS12 = {'topo': (0, 0), 'lado+': (500, 0), 'lado-': (500, 312), 'ponta+': (0, 500), 'ponta-': (500, 624)}


@arma('caixa_municao_12', 'Caixa de cartuchos 12 (25)', 'municao', 'caixa', calibre='12', municao='municao_12_chumbo', quantidade=25,
      peso_kg=1.1, empilha=4, raridade='incomum', onde=['quartel', 'casa_de_campo', 'armazem', 'posto', 'delegacia'],
      descricao='Caixa de papelão com 25 cartuchos de chumbo grosso em pé. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_12(A):
    caixa_municao(A, 'rotulo_12', CX12, _arte_caixa(CX12, '12', '25 CARTUCHOS', 'CHUMBO GROSSO 3T · 70 mm', cor=(160, 30, 24), atlas=ATLAS12),
                  _cartucho_12(sec=14), 5, 5, 0.0232, 0.0232, faltam=(4, 9), bandeja=0.03, atlas=ATLAS12)
