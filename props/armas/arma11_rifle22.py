# Arma 10: rifle de ferrolho .22 com coronha de nogueira (e versao sintetica), carregador rotativo de 10 e caixa de 25.
# Executado por gerar_armas.py (plano de lado: x frente, y cima, z direita). Desenho proprio, inspirado na foto do Bruno:
# cano fino e comprido, receptor curto com trilho, coronha de madeira com pente alto e punho curvo, soleira preta, luneta pequena.

R2 = 0.0135                     # raio do receptor
K2X0, K2X1 = -0.06, 0.11        # receptor em x
C2 = 0.06                       # curso do ferrolho
LEV2 = -60                      # giro da alavanca
M2X, M2Y = 0.026, -0.012        # topo do carregador (centro)
X2M = 0.58                      # boca do cano (fim da rosca)
YS2 = 0.0215                    # linha das miras de ferro (fundo do entalhe da alca = topo do poste da massa)
XA2 = 0.18                      # alca no cano
XF2 = X2M - 0.035               # massa no cano
r_cano = lambda x: float(np.interp(x, [K2X1 + 0.03, K2X1 + 0.05, X2M - 0.02], [0.0118, 0.0105, 0.0088]))


def _cartucho_22(sec=20, vazio=False):
    """Cartucho .22 de fogo circular deitado em x (base em x = 0): aro, estojo de latao e projetil de chumbo cobreado."""
    q = P()
    est = torno_x([(0.0, 0.0), (0.00345, 0.0), (0.00345, 0.0011), (0.00285, 0.0013), (0.00285, 0.0155), (0.0, 0.0155)], sec)
    if vazio: est = menos(est, cil_x(0.0024, 0.0009, 0.02, sec=sec))
    q.add('latao', est)
    if not vazio:
        q.add('cobre_bala', torno_x([(0.0028, 0.015), (0.0028, 0.0185), (0.0023, 0.0222), (0.0013, 0.0244), (0.0, 0.0251)], sec))
    return q


def _perfil_car22(folga=0.0, baixo=-0.044):
    return Polygon([(M2X - 0.019, M2Y), (M2X + 0.019, M2Y), (M2X + 0.019, baixo), (M2X - 0.019, baixo)]).buffer(folga, join_style=2)


def _rotativo_22(q, mat='polimero'):
    """Carregador rotativo de 10: caixa curta quase rente a coronha, janela clara atras mostrando o rotor e os aros dos cartuchos."""
    corpo = solido(arred(list(_perfil_car22().exterior.coords)[:-1], 0.003), -0.0112, 0.0112, 0.0012)
    janela = caixa(M2X - 0.03, M2X - 0.0155, -0.0395, -0.0165, -0.0092, 0.0092)
    q.add(mat, menos(corpo, janela))
    q.add(mat, solido(arred([(M2X - 0.0205, -0.0475), (M2X + 0.0205, -0.0475), (M2X + 0.0205, -0.0425), (M2X - 0.0205, -0.0425)], 0.002), -0.0122, 0.0122, 0.0012))
    yc = -0.028
    q.add('polimero_cinza', cil_x(0.0028, M2X - 0.0156, M2X + 0.012, yc, 0, 20))                                   # eixo do rotor
    for i in range(5):                                                                                            # pas do rotor
        pa = caixa(M2X - 0.0156, M2X + 0.012, 0.0022, 0.0086, -0.0009, 0.0009)
        pa.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 5, [1, 0, 0])); pa.apply_translation([0, yc, 0]); q.add('polimero_cinza', pa)
        a = (i + 0.5) * 2 * math.pi / 5                                                                           # aros dos cartuchos entre as pas
        q.add('latao', cil_x(0.0034, M2X - 0.0156, M2X - 0.0145, yc + 0.0068 * math.cos(a), 0.0068 * math.sin(a), 16))
    q.add('lente_clara', caixa(M2X - 0.0158, M2X - 0.0152, -0.0393, -0.0167, -0.009, 0.009))
    q.add('tinta_branca', caixa(M2X + 0.006, M2X + 0.014, -0.046, -0.0445, -0.0124, -0.0122))
    q.merge(_cartucho_22(16), TF.translation_matrix([M2X - 0.016, M2Y - 0.0035, 0.0]))


def _caixa25_22(q, mat='polimero'):
    """Carregador de caixa de 25: topo do mesmo tamanho do rotativo, corpo comprido com nervuras e base mais larga."""
    q.add(mat, solido(arred(list(_perfil_car22(0, -0.046).exterior.coords)[:-1], 0.003), -0.0112, 0.0112, 0.0012))
    corpo = arred([(M2X - 0.017, -0.04), (M2X + 0.017, -0.04), (M2X + 0.022, -0.124), (M2X - 0.012, -0.124)], 0.003)
    q.add(mat, solido(corpo, -0.0102, 0.0102, 0.0012))
    for zs in (-1, 1):
        for k in range(5):
            y = -0.055 - k * 0.013; dx = (0.04 + y) * -0.06
            q.add(mat, caixa(M2X - 0.013 + dx, M2X + 0.013 + dx, y - 0.0011, y + 0.0011, min(zs * 0.0102, zs * 0.0109), max(zs * 0.0102, zs * 0.0109)))
    q.add(mat, solido(arred([(M2X - 0.015, -0.131), (M2X + 0.026, -0.131), (M2X + 0.026, -0.122), (M2X - 0.015, -0.122)], 0.002), -0.0122, 0.0122, 0.0015))
    q.add('tinta_branca', caixa(M2X - 0.01, M2X + 0.004, -0.128, -0.125, -0.0123, -0.0121))
    q.merge(_cartucho_22(16), TF.translation_matrix([M2X - 0.016, M2Y - 0.0035, 0.0]))


def _receptor_22(p):
    corpo = torno_x([(0.0, K2X0), (R2 - 0.002, K2X0), (R2, K2X0 + 0.002), (R2, K2X1 - 0.002), (R2 - 0.001, K2X1)], 56)
    corpo = menos(corpo, caixa(0.03, 0.08, -0.004, 0.03, 0.003, 0.03),                          # janela de ejecao
                  caixa(M2X - 0.0195, M2X + 0.0195, -0.03, -0.006, -0.0116, 0.0116),             # poco do carregador
                  caixa(-0.054, -0.03, -0.006, 0.006, 0.004, 0.03),                               # entalhe da alavanca
                  cil_x(0.0078, K2X0 - 0.01, 0.09, sec=36))                                       # caminho do ferrolho
    p.add('aco_oxidado', corpo)
    trilho(p, 'aluminio_preto', K2X0 + 0.006, K2X1 - 0.004, R2 - 0.001, False)
    p.add('aco_oxidado', solido(arred([(-0.058, -0.004), (-0.036, -0.004), (-0.036, 0.002), (-0.058, 0.002)], 0.001), R2 - 0.003, R2 + 0.0012, 0.0004))  # trava
    p.add('tinta_vermelha', cil_z(0.0012, R2 + 0.0011, R2 + 0.0013, -0.04, -0.001, 12))
    for x in (K2X0 + 0.012, K2X1 - 0.012):
        p.add('aco_inox', cil_z(0.0016, R2 - 0.0005, R2 + 0.0004, x, -0.007, 12))                        # pinos do receptor
    # cano fino e comprido com rosca na boca
    cano = torno_x([(0.0118, K2X1 - 0.002), (0.0118, K2X1 + 0.03), (0.0105, K2X1 + 0.05), (0.0088, X2M - 0.02), (0.0088, X2M - 0.0125), (0.0072, X2M - 0.012)], 48)
    p.add('aco_fosfatado', menos(cano, cil_x(0.0029, K2X1 - 0.01, X2M + 0.01, sec=20)))
    rosca_x(p, 'aco_fosfatado', 0.0072, X2M - 0.012, X2M - 0.0005, 0.0009)
    p.add('aco_fosfatado', tubo_x(0.0029, 0.0062, X2M - 0.0005, X2M, sec=28))
    # massa de rampa com capuz (topo do poste em YS2, conta de latao)
    rb = r_cano(XF2)
    p.add('aco_oxidado', solido(arred([(XF2 - 0.02, rb - 0.003), (XF2 + 0.007, rb - 0.003), (XF2 + 0.007, rb + 0.0062), (XF2 - 0.004, rb + 0.0062)], 0.0012),
                                -0.0036, 0.0036, 0.0006))
    p.add('aco_oxidado', caixa(XF2 - 0.0008, XF2 + 0.0008, rb + 0.005, YS2 - 0.0008, -0.0007, 0.0007))
    p.add('latao', trimesh.creation.icosphere(2, 0.00085).apply_translation([XF2, YS2 - 0.00085, 0]))
    capuz = menos(tubo_x(0.0058, 0.0066, XF2 - 0.009, XF2 + 0.007, YS2 - 0.0012, sec=32), caixa(XF2 - 0.02, XF2 + 0.02, -0.1, rb + 0.004, -0.02, 0.02))
    p.add('aco_oxidado', capuz)


def _ferrolho_22(q):
    q.add('aco_inox', cil_x(0.0074, K2X0 + 0.004, 0.088, 0, 0, 36))
    q.add('aco_oxidado', solido(arred([(0.074, 0.003), (0.088, 0.003), (0.088, 0.0062), (0.074, 0.0062)], 0.0004), 0.0068, 0.0079, 0.0002))   # extrator
    q.add('aco_oxidado', torno_x([(0.0, -0.088), (0.0065, -0.088), (0.0098, -0.082), (0.0098, K2X0 - 0.0005), (0.0, K2X0 - 0.0005)], 36))      # capa
    q.add('tinta_vermelha', tubo_x(0.0, 0.0022, -0.0885, -0.088, sec=16))
    dirc = np.array([0.0, -0.45, 0.89]); dirc /= np.linalg.norm(dirc); x = -0.042
    p0 = np.array([x, 0.0, 0.005]); p1 = p0 + dirc * 0.04
    q.add('aco_oxidado', trimesh.creation.cylinder(radius=0.003, segment=[p0, p1], sections=20))
    q.add('aco_oxidado', solido(arred([(x - 0.006, -0.0035), (x + 0.006, -0.0035), (x + 0.006, 0.0035), (x - 0.006, 0.0035)], 0.0018), 0.005, 0.0098, 0.0005))
    q.add('aco_oxidado', trimesh.creation.icosphere(3, 0.0072).apply_translation(p1 + dirc * 0.0035))


def _coronha_22(p, mad='nogueira', quad='madeira_punho'):
    """Coronha inteirica: pente alto (estilo Monte Carlo), punho curvo, telha fina com ponta arredondada, soleira preta."""
    perfil = suave([(0.33, -0.005), (0.15, -0.002), (0.0, -0.002), (-0.07, 0.0), (-0.11, 0.006), (-0.19, 0.0125), (-0.31, 0.0175), (-0.334, 0.0185),
                    (-0.35, 0.0145), (-0.35, -0.11), (-0.337, -0.117), (-0.29, -0.104), (-0.2, -0.08), (-0.15, -0.074), (-0.122, -0.08), (-0.104, -0.096),
                    (-0.088, -0.098), (-0.076, -0.086), (-0.064, -0.064), (-0.052, -0.044), (-0.047, -0.036), (0.08, -0.036), (0.22, -0.031), (0.31, -0.025), (0.328, -0.019)], 3)
    larg = lambda x: (0.0158 - 0.0036 * math.exp(-((x + 0.1) / 0.045) ** 2) + 0.0026 * GT.smooth(-0.15, -0.26, x) - 0.0026 * GT.smooth(0.2, 0.33, x))
    co = corpo_x(perfil, 0.334, -0.352, larg, n=2.4, fatias=210, voltas=56, raio_tras=0.006, raio_frente=0.007)
    co = menos(co, cil_x(R2 + 0.0004, K2X0 - 0.012, K2X1 + 0.002, sec=56), cil_x(0.0122, K2X1, 0.36, sec=40), solido(_perfil_car22(0.0008, -0.06), -0.0118, 0.0118),
               caixa(-0.036, -0.008, -0.06, -0.01, -0.005, 0.005), caixa(-0.058, -0.026, -0.03, 0.01, 0.01, 0.04))
    p.add(mad, inter([co, caixa(-0.339, 0.4, -1, 1, -1, 1)]))
    p.add('borracha', inter([co, caixa(-0.4, -0.339, -1, 1, -1, 1)]))
    xz = corpo_x(perfil, 0.334, -0.352, lambda x: larg(x) + 0.0004, n=2.4, fatias=210, voltas=56, raio_tras=0.006, raio_frente=0.007)
    for a in (arred([(-0.054, -0.03), (-0.07, -0.026), (-0.106, -0.08), (-0.09, -0.088), (-0.068, -0.062)], 0.004),
              arred([(0.13, -0.008), (0.25, -0.01), (0.25, -0.025), (0.13, -0.028)], 0.006)):
        p.add(quad, inter([xz, solido(a, -0.05, 0.05)]))
    # guarda-mato, retem do carregador e pinos da bandoleira
    fora = arred([(-0.054, -0.0325), (0.001, -0.0325), (-0.001, -0.046), (-0.015, -0.06), (-0.046, -0.062), (-0.058, -0.05)], 0.005)
    dentro = arred([(-0.047, -0.0365), (-0.005, -0.0365), (-0.007, -0.046), (-0.017, -0.0555), (-0.043, -0.057), (-0.051, -0.048)], 0.004)
    p.add('aco_oxidado', solido(fora.difference(dentro), -0.005, 0.005, 0.0012))
    p.add('aco_oxidado', solido(arred([(0.0005, -0.043), (0.0065, -0.043), (0.0065, -0.0345), (0.0005, -0.0345)], 0.001), -0.0035, 0.0035, 0.0005))
    # placas de M-LOK pretas na telha: lanterna (direita), laser (esquerda) e empunhadura (embaixo)
    for zs in (-1, 1): placa_mlok(p, 'polimero', 0.24, 0.30, -0.0155, zs * 0.0175, zs, alt=0.014, esp=0.0055)
    placa_mlok_baixo(p, 'polimero', 0.17, 0.23, -0.0345, meia=0.007, esp=0.006)
    for x, y in ((0.29, -0.026), (-0.28, -0.101)):
        p.add('aco_inox', trimesh.creation.cylinder(radius=0.0024, segment=[[x, y + 0.002, 0], [x, y - 0.0055, 0]], sections=16))
        p.add('aco_inox', solido(Point(x, y - 0.0098).buffer(0.0056, 32).difference(Point(x, y - 0.0098).buffer(0.0037, 32)), -0.0012, 0.0012, 0.0004))


def _rifle22(A, sintetico):
    A.pivo = (-0.078, -0.062, 0.0)
    _receptor_22(A.base)
    _coronha_22(A.base, 'polimero' if sintetico else 'nogueira', 'polimero_grip' if sintetico else 'madeira_punho')
    gpx, gpy = -0.022, -0.034
    gat = A.parte('gatilho', (gpx, gpy, 0), explodir=(0.0, -0.06, 0), tipo='gira', eixo='z', curso_graus=-8, descricao='gatilho leve')
    _gatilho_em(gat, gpx, gpy, larg=0.0035)
    fer = A.parte('ferrolho', (0, 0, 0), explodir=(-0.12, 0.05, 0), tipo='gira_e_desliza', curso_graus=LEV2, curso_m=-C2,
                  descricao=f'levanta a alavanca {abs(LEV2)}° e corre {int(C2 * 1000)} mm para trás (ejeta), volta e abaixa')
    _ferrolho_22(fer)
    car = A.parte('carregador', (M2X, M2Y, 0), explodir=(0, -0.07, 0), tipo='remove', direcao=[0.0, -1.0, 0.0], municao='municao_22',
                  capacidade=10, descricao='carregador rotativo de 10, sai por baixo')
    _rotativo_22(car)
    A.encaixe('encaixe_mira', (0.025, R2 + 0.0045, 0), 'trilho_mira', explodir=(0, 0.07, 0),
              aceita=['luneta_4x_22', 'luneta_4x', 'luneta_3_9', 'mira_ponto_vermelho_tubo', 'mira_reflexa'], padrao=None if sintetico else 'luneta_4x_22')
    A.encaixe('encaixe_alca', (XA2, r_cano(XA2), 0), 'alca_cano_22', explodir=(0, 0.04, 0), aceita=['alca_cano_22'], padrao='alca_cano_22',
              rebate_com='encaixe_mira', descricao='alça de lâmina no cano: deita (animação "dobrar") quando há mira no encaixe_mira')
    A.encaixe('mira_ferro', (XA2, YS2, 0), 'mira', descricao='fundo do entalhe da alça: câmera de 1ª pessoa olha daqui pela conta da massa (-Z)')
    A.encaixe('encaixe_boca', (X2M - 0.012, 0, 0), 'boca_22', explodir=(0.08, 0, 0), aceita=['protetor_rosca_22', 'supressor_22'], padrao='protetor_rosca_22')
    A.encaixe('encaixe_carregador', (M2X, M2Y, 0), 'carregador_22', pai='carregador', substitui='carregador', aceita=['carregador_22_10', 'carregador_22_25'],
              descricao='filho do nó carregador; ao pôr um carregador aqui, esconda as malhas do nó carregador')
    A.encaixe('encaixe_bandoleira', (0.29, -0.0365, 0), 'bandoleira', explodir=(0, -0.05, 0), aceita=['bandoleira'])
    A.encaixe('encaixe_lanterna', (0.27, -0.0155, 0.0175), 'mlok_lado', explodir=(0, 0, 0.06), aceita=ACEITA_LANTERNA, descricao='placa de M-LOK do lado direito da telha')
    A.encaixe('encaixe_laser', (0.27, -0.0155, -0.0175), 'mlok_esq', explodir=(0, 0, -0.06), aceita=ACEITA_LASER, descricao='placa de M-LOK do lado esquerdo da telha')
    A.encaixe('encaixe_empunhadura', (0.2, -0.0345, 0), 'mlok_baixo', explodir=(0, -0.06, 0), aceita=ACEITA_EMPUNHADURA, descricao='placa de M-LOK embaixo da telha')
    A.encaixe('boca_fogo', (X2M, 0, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('saida_estojo', (0.055, 0.008, R2), 'efeito', descricao='onde nasce o estojo (quando o ferrolho volta, aos 0,55 s do "atirar")')
    fr = lambda ks: ('ferrolho', 'r', (1, 0, 0), pose(ks))
    ft = lambda ks: ('ferrolho', 't', pose([(t, (dx, 0, 0)) for t, dx in ks]))
    coice = [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.02, -8), (0.1, -8), (0.2, 0)])),
             (None, 'r', (0, 0, 1), pose([(0, 0), (0.02, 0), (0.05, 1.5), (0.2, 0)])),
             (None, 't', pose([(0, (0, 0, 0)), (0.02, (0, 0, 0)), (0.04, (-0.006, 0.001, 0)), (0.2, (0, 0, 0))]))]
    A.anim('atirar', 1.0, coice + [fr([(0, 0), (0.3, 0), (0.38, LEV2), (0.74, LEV2), (0.82, 0)]),
                                   ft([(0, 0), (0.4, 0), (0.52, -C2), (0.6, -C2), (0.72, 0), (1.0, 0)])],
           desc='tiro (coice pequeno) e manejo do ferrolho: levanta (0,38 s), puxa (0,52 s: soltar o estojo), empurra e abaixa (0,82 s)')
    A.anim('atirar_ultimo', 0.7, coice + [fr([(0, 0), (0.3, 0), (0.38, LEV2), (0.7, LEV2)]), ft([(0, 0), (0.4, 0), (0.52, -C2), (0.7, -C2)])],
           desc='último tiro: o ferrolho fica aberto, atrás')
    A.anim('vazia', 0.1, [fr([(0, LEV2), (0.1, LEV2)]), ft([(0, -C2), (0.1, -C2)])], laco=True, desc='pose parada: ferrolho aberto')
    dm = (0, -0.16, 0)
    troca = ('carregador', 't', pose([(0, (0, 0, 0)), (0.25, (0, 0, 0)), (0.38, (0, -0.015, 0)), (0.55, dm), (1.2, dm), (1.45, (0, -0.01, 0)), (1.56, (0, 0, 0))]))
    A.anim('recarregar', 2.0, [troca, (None, 'r', (1, 0, 0), pose([(0, 0), (0.25, 22), (1.6, 22), (2.0, 0)])),
                               (None, 'r', (0, 0, 1), pose([(0, 0), (0.25, 5), (1.6, 5), (2.0, 0)]))],
           desc='aperta o retém na frente do guarda-mato, o carregador cai (0,38 s), novo entra (1,56 s); trocar o nó entre 0,55 e 1,2 s')
    A.anim('recarregar_vazia', 2.6, [troca, fr([(0, LEV2), (2.05, LEV2), (2.18, 0)]), ft([(0, -C2), (1.8, -C2), (1.95, 0)]),
                                     (None, 'r', (1, 0, 0), pose([(0, 0), (0.25, 22), (1.6, 22), (1.8, -8), (2.2, -8), (2.6, 0)])),
                                     (None, 'r', (0, 0, 1), pose([(0, 0), (0.25, 5), (1.6, 5), (2.3, 0)]))],
           desc='troca o carregador com o ferrolho aberto e fecha o ferrolho (1,95 s) e a alavanca (2,18 s)')
    A.anim('inspecionar', 2.6, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -30), (1.1, -30), (1.5, 35), (2.1, 35), (2.6, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 8), (2.1, 8), (2.6, 0)])),
                                fr([(0, 0), (0.45, 0), (0.55, LEV2), (1.0, LEV2), (1.1, 0)]), ft([(0, 0), (0.57, 0), (0.68, -0.022), (0.88, -0.022), (0.98, 0)])],
           desc='abre um pouco o ferrolho para ver o cartucho na câmara, fecha e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.5), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


DADOS22 = dict(classe='fogo', calibre='.22', municao='municao_22', modo='ferrolho (ação manual)', acao='ferrolho', estojo_s=0.55, capacidade=10,
               dano=34, alcance_m=70, alcance_max_m=250, tiros_por_s=1.1, recarga_s=2.0, recarga_vazia_s=2.6, recuo=0.06, durabilidade=5000)


@arma('rifle_22', 'Rifle Pardal .22', 'armas', 'rifle', precisao=0.88, ruido_m=70, peso_kg=2.7, raridade='comum', valor_troca=55,
      onde=['casa_de_campo', 'armazem', 'casas', 'celeiro'], **DADOS22,
      descricao='Rifle leve de ferrolho na coronha de nogueira, com luneta 4× pequena. Para caça pequena (coelho, pombo): barulho baixo e munição '
                'barata e fácil de achar. Mata zumbi só com tiro na cabeça. Com o supressor quase não se ouve.')
def rifle_22(A): _rifle22(A, False)


@arma('rifle_22_sintetico', 'Rifle Pardal .22 sintético', 'armas', 'rifle', precisao=0.86, ruido_m=70, peso_kg=2.5, raridade='comum', valor_troca=50,
      onde=['casa_de_campo', 'armazem', 'casas', 'delegacia'], **DADOS22,
      descricao='O mesmo rifle numa coronha preta de polímero que não liga para chuva. Vem só com as miras de ferro.')
def rifle_22_sintetico(A): _rifle22(A, True)


# ---------------------------------------------------------------------------- acessorios do .22
@_acessorio('luneta_4x_22', 'Luneta 4× pequena', 'mira', 'trilho_mira', peso_kg=0.26, raridade='comum', valor_troca=30, aumento=[4, 4],
            modificadores={'precisao_mirando': 1.35, 'tempo_mirar': 1.1, 'alcance_m': 1.4}, onde=['casa_de_campo', 'armazem', 'casas'],
            linha_de_visada='encaixe "olho"', descricao='Luneta fina e curta de rifle de caça pequena: 4× fixa, retículo de cruz fina.')
def luneta_4x_22(A): _luneta(A, -0.118, 0.118, 0.0115, 0.0152, 0.0165, False)


@_acessorio('alca_cano_22', 'Alça de lâmina do .22', 'mira', 'alca_cano_22', peso_kg=0.01, raridade='comum', modificadores={},
            descricao='Alça de lâmina com entalhe em U, presa no cano. Deita para trás quando há luneta. Vem no rifle .22.')
def alca_cano_22(A):
    q = A.base; L = 0.02
    sela = menos(solido(arred([(-L / 2, -0.004), (L / 2, -0.004), (L / 2, 0.003), (-L / 2, 0.003)], 0.0015), -0.0055, 0.0055, 0.0008),
                 cil_x(0.0104, -0.02, 0.02, -0.0104, 0, 40))
    q.add('aco_oxidado', sela)
    q.add('aco_oxidado', cil_z(0.0012, -0.0058, 0.0058, 0.0, 0.0018, 12))
    la = A.parte('lamina', (0.0, 0.002, 0), explodir=(0, 0.02, 0), tipo='gira', eixo='z', curso_graus=85, descricao='deita para trás (animação dobrar)')
    h = YS2 - r_cano(XA2)                              # fundo do entalhe na altura da linha de visada
    placa = solido(Polygon([(-0.0011, 0.001), (0.0011, 0.001), (0.0011, h + 0.0034), (-0.0011, h + 0.0034)]), -0.0075, 0.0075, 0.0004)
    u = ext_x(Polygon([(-0.0013, h + 0.0013), (-0.0013, h + 0.01), (0.0013, h + 0.01), (0.0013, h + 0.0013)]).union(Point(0.0, h + 0.0013).buffer(0.0013, 16)), -0.01, 0.01)
    la.add('aco_oxidado', menos(placa, u))
    la.add('tinta_branca', caixa(-0.00115, -0.0011, h - 0.0016, h - 0.0006, -0.0004, 0.0004))
    A.anim('dobrar', 0.25, [('lamina', 'r', (0, 0, 1), pose([(0, 0), (0.25, 85)]))], desc='deita a alça')
    A.pivo = (0, 0, 0)


@_acessorio('protetor_rosca_22', 'Protetor de rosca .22', 'boca', 'boca_22', peso_kg=0.01, raridade='comum', modificadores={},
            descricao='Capinha recartilhada que protege a rosca da boca. Vem no rifle.')
def protetor_rosca_22(A):
    A.base.add('aco_fosfatado', tubo_x(0.003, 0.0088, 0.0, 0.0125, sec=36, ch=0.0006))
    A.base.add('recartilhado', tubo_x(0.0087, 0.0091, 0.002, 0.01, sec=36))
    A.pivo = (0, 0, 0)


@_acessorio('supressor_22', 'Supressor .22', 'boca', 'boca_22', peso_kg=0.16, raridade='raro', valor_troca=70, durabilidade=8000,
            modificadores={'ruido_m': 0.25, 'precisao': 1.04, 'alcance_m': 0.95}, onde=['casa_de_campo', 'armazem'],
            descricao='Tubo fino de alumínio que deixa o .22 quase mudo: o estalo vira um "tec" que zumbi não ouve a 20 m. Bom para caçar sem chamar a horda.')
def supressor_22(A):
    q = A.base; L = 0.155; R = 0.0118
    q.add('aluminio_preto', menos(torno_x([(0.0, 0.0), (R - 0.0015, 0.0), (R, 0.0015), (R, L - 0.003), (R - 0.0025, L), (0.0, L)], 48),
                                  cil_x(0.0072, -0.01, 0.0125, sec=32), cil_x(0.0034, 0.0, L + 0.01, sec=20)))
    for x in (0.004, 0.009): q.add('aluminio_preto', tubo_x(R - 0.0004, R + 0.0005, x, x + 0.0025, sec=48))            # aneis de pega
    q.add('aco_oxidado', tubo_x(0.0034, 0.0065, L - 0.0005, L + 0.0005, sec=32))                                     # tampa da frente
    for i in range(6):
        a = i * math.pi / 3
        q.add('aco_oxidado', cil_x(0.0007, L - 0.0002, L + 0.0008, 0.0085 * math.cos(a), 0.0085 * math.sin(a), 8))   # furos da chave
    A.pivo = (0, 0, 0)


@_acessorio('carregador_22_10', 'Carregador rotativo .22 (10)', 'carregador', 'carregador_22', capacidade=10, municao='municao_22', peso_kg=0.05,
            raridade='comum', descricao='Carregador rotativo curto, quase rente à coronha. A janela de trás mostra quantos cartuchos sobram.')
def carregador_22_10(A): _rotativo_22(A.base); A.pivo = (M2X, M2Y, 0)


@_acessorio('carregador_22_25', 'Carregador .22 (25)', 'carregador', 'carregador_22', capacidade=25, municao='municao_22', peso_kg=0.12,
            raridade='incomum', valor_troca=15, modificadores={'recarga_s': 1.1},
            descricao='Caixa comprida de 25 tiros. Atrapalha deitar o rifle no chão, mas dá para limpar um quintal sem recarregar.')
def carregador_22_25(A): _caixa25_22(A.base); A.pivo = (M2X, M2Y, 0)


@arma('municao_22', 'Cartucho .22', 'municao', 'municao', calibre='.22', peso_kg=0.0035, empilha=100, raridade='comum', estojo='estojo_22',
      descricao='Cartucho pequeno de fogo circular: o mais fácil de achar em casas de campo e lojas. Fraco contra zumbi, ótimo para caça.')
def municao_22(A): A.base.merge(_cartucho_22(24), TF.translation_matrix([-0.0125, 0.0035, 0])); A.pivo = (0, 0, 0)


@arma('estojo_22', 'Estojo .22 (vazio)', 'municao', 'estojo', calibre='.22', peso_kg=0.001,
      descricao='Estojo ejetado: o jogo cria um em saida_estojo a cada tiro (some depois de uns segundos).')
def estojo_22(A): A.base.merge(_cartucho_22(20, vazio=True), TF.translation_matrix([-0.0078, 0, 0])); A.pivo = (0, 0, 0)


CX22 = dict(x0=-0.042, x1=0.042, y0=0.0, y1=0.032, z0=-0.022, z1=0.022)


def _arte_caixa_22(CX, cor=(30, 60, 120), marca='GUARDIÃO'):
    """Arte da caixinha .22 (rasa): a tampa tem pouco fundo, entao o texto de cima vai em 3 linhas pequenas."""
    im = _arte_caixa(CX, '.22', '50 CARTUCHOS', 'PONTA REDONDA 40 gr', cor=cor, marca=marca)
    d = ImageDraw.Draw(im)
    L = int((CX['x1'] - CX['x0']) * PXM); P_ = int((CX['z1'] - CX['z0']) * PXM)
    x, y = ATLAS['topo']
    d.rectangle([x, y, x + L, y + P_], fill=(236, 230, 212)); d.rectangle([x, y, x + 110, y + P_], fill=cor)
    texto_c(d, (x + 55, y + P_ // 2), '.22', 56, (250, 240, 220), larg=96)
    cx = x + 110 + (L - 110) // 2
    texto_c(d, (cx, y + 40), marca, 40, cor, larg=L - 130)
    texto_c(d, (cx, y + 88), '50 CARTUCHOS', 28, (40, 30, 26), larg=L - 130)
    texto_c(d, (cx, y + 124), 'PONTA REDONDA 40 gr', 18, (90, 70, 60), False, larg=L - 130)
    d.rectangle([x + 120, y + P_ - 22, x + L - 10, y + P_ - 12], fill=cor)
    return im


@arma('caixa_municao_22', 'Caixa de munição .22 (50)', 'municao', 'caixa', calibre='.22', municao='municao_22', quantidade=50,
      peso_kg=0.18, empilha=6, raridade='comum', onde=['casa_de_campo', 'armazem', 'casas', 'galeria'],
      descricao='Caixinha de papelão com bandeja de 50 cartuchos .22 em pé. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_22(A):
    caixa_municao(A, 'rotulo_22', CX22, _arte_caixa_22(CX22),
                  _cartucho_22(12), 10, 5, 0.0074, 0.0074, faltam=(4, 17), bandeja=0.02)
