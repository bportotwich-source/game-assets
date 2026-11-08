# Arma 12: fuzil semiautomatico de precisao .308 (7,62x51), longo e curto, verde-oliva, com coronha de precisao, luneta grande
# e carregadores de caixa. Executado por gerar_armas.py (plano de lado: x frente, y cima, z direita). Desenho proprio inspirado
# nas fotos do Bruno: receptor grande de fuzil .308, guarda-mao octogonal longo com fendas grandes, coronha de precisao com apoio de rosto.
# Usa a municao_308 e os acessorios de boca da carabina .308 (mesma rosca).

QX0, QX1 = -0.024, 0.2          # receptor superior em x
QY1 = 0.021                     # topo do receptor (base do trilho)
QW = 0.0145                     # meia largura do receptor superior
QMX, QMY = 0.125, -0.018        # topo do carregador (centro)
QCF = 0.095                     # curso do transportador
QPU = (-0.022, -0.051, 0.0)     # encaixe do punho
QVERDE = {'polimero': 'polimero_verde', 'polimero_grip': 'polimero_verde'}


def _receptores_q(p, mat='cerakote_verde'):
    sup = solido(arred([(QX0, -0.014), (QX1, -0.014), (QX1, QY1), (QX0, QY1)], 0.0018), -QW, QW, 0.0016)
    sup = menos(sup, caixa(0.07, 0.145, -0.0095, 0.0095, 0.0, 0.03), cil_x(0.0098, QX0 - 0.01, 0.18, 0.0, 0, 36),
                caixa(QX0 - 0.01, 0.03, 0.007, 0.0155, -0.005, 0.005),
                *[caixa(x, x + 0.03, -0.009, 0.006, -QW - 0.01, -QW + 0.0012) for x in (0.08, 0.125)])          # rebaixos de alivio (esquerda)
    p.add(mat, sup)
    p.add(mat, solido(arred([(0.012, -0.005), (0.048, -0.005), (0.054, 0.005), (0.012, 0.007)], 0.002), QW - 0.001, QW + 0.008, 0.0018))   # assistente
    p.add('aco_inox', cil_x(0.005, -0.001, 0.012, 0.001, QW + 0.005, 20))
    p.add(mat, solido(arred([(0.145, -0.0095), (0.154, -0.0095), (0.154, 0.009), (0.145, 0.009)], 0.001), QW - 0.001, QW + 0.0045, 0.0006))   # defletor
    trilho(p, mat, QX0 + 0.004, QX1, QY1, False)
    inf = arred([(QX0, -0.0138), (0.172, -0.0138), (0.177, -0.03), (0.168, -0.04), (0.168, -0.062), (0.162, -0.069), (0.084, -0.069),
                 (0.08, -0.055), (0.004, -0.053), (-0.046, -0.054), (-0.052, -0.049), (-0.042, -0.026), (QX0, -0.019)], 0.0022)
    ib = menos(solido(inf, -0.0138, 0.0138, 0.0018), solido(Polygon([(0.088, -0.014), (0.162, -0.014), (0.162, -0.08), (0.088, -0.08)]), -0.0122, 0.0122),
               caixa(0.032, 0.058, -0.07, -0.036, -0.004, 0.004),
               *[solido(arred([(0.096, -0.03), (0.154, -0.03), (0.154, -0.056), (0.096, -0.056)], 0.004), min(zs * 0.0128, zs * 0.02), max(zs * 0.0128, zs * 0.02))
                 for zs in (-1, 1)])                                                                       # paineis rebaixados do poco
    p.add(mat, ib)
    for zs in (-1, 1): p.add(mat, solido(arred([(0.082, -0.069), (0.166, -0.069), (0.169, -0.062), (0.08, -0.062)], 0.001),
                                          min(zs * 0.0138, zs * 0.015), max(zs * 0.0138, zs * 0.015), 0.0004))            # boca do poco alargada
    fora = arred([(-0.002, -0.051), (0.078, -0.053), (0.078, -0.06), (0.066, -0.076), (0.012, -0.079), (-0.004, -0.066)], 0.005)
    dentro = arred([(0.008, -0.055), (0.07, -0.0565), (0.07, -0.061), (0.06, -0.071), (0.014, -0.0735), (0.006, -0.064)], 0.004)
    p.add(mat, solido(fora.difference(dentro), -0.0062, 0.0062, 0.0014))
    for (x, y) in ((0.02, -0.034), (0.046, -0.034), (0.165, -0.018), (-0.014, -0.018)):
        for zs in (-1, 1): p.add('aco_inox', cil_z(0.0022, min(zs * 0.0137, zs * 0.0146), max(zs * 0.0137, zs * 0.0146), x, y, 16))
    p.add('aco_oxidado', solido(arred([(0.07, -0.05), (0.08, -0.05), (0.08, -0.042), (0.07, -0.042)], 0.0012), 0.012, 0.0152, 0.0004))   # retem do carregador
    p.add(mat, cil_x(0.0175, QX0 - 0.006, QX0, -0.003, 0, 40))


def _guarda_mao_q(p, X1, xm, mat='cerakote_verde'):
    X0 = QX1 + 0.002
    sec_f = arred([(-0.022, -0.034), (0.022, -0.034), (0.022, QY1), (-0.022, QY1)], 0.011, n=1)          # octogonal
    sec_d = sec_f.buffer(-0.0024, join_style=2)
    gm = menos(ext_x(sec_f, X0, X1), ext_x(sec_d, X0 - 0.01, X1 + 0.01))
    fendas = []
    for x in np.arange(X0 + 0.03, X1 - 0.035, 0.046):
        for yy in (0.004, -0.014):
            fendas.append(solido(LineString([(x, yy), (x + 0.03, yy)]).buffer(0.0042, 12), -0.03, 0.03))
        fendas.append(ext_y(LineString([(x, 0.0), (x + 0.03, 0.0)]).buffer(0.0036, 12), -0.05, -0.03))
    p.add(mat, menos(gm, *fendas))
    trilho(p, mat, X0 + 0.003, X1 - 0.002, QY1, False)
    p.add(mat, menos(ext_x(sec_f.buffer(0.0007, join_style=2), X1 - 0.006, X1), ext_x(sec_d, X1 - 0.01, X1 + 0.01)))          # anel da ponta
    p.add(mat, menos(ext_x(sec_f.buffer(0.0007, join_style=2), QX1, QX1 + 0.012), cil_x(0.0135, QX1 - 0.01, QX1 + 0.02, sec=32)))  # porca
    for zs in (-1, 1): p.add('aco_inox', cil_z(0.0045, min(zs * 0.022, zs * 0.0235), max(zs * 0.022, zs * 0.0235), X1 - 0.025, -0.006, 20))   # copos QD
    # cano (mesma rosca da carabina .308) e bloco de gas por dentro
    p.add('aco_oxidado', torno_x([(0.0118, QX1 - 0.002), (0.0118, QX1 + 0.035), (0.0106, QX1 + 0.05), (0.0098, xm - 0.03), (0.0098, xm - 0.016),
                                  (0.0085, xm - 0.015)], 48))
    rosca_x(p, 'aco_oxidado', 0.0085, xm - 0.015, xm - 0.0005, 0.0012)
    p.add('aco_oxidado', tubo_x(0.0039, 0.0075, xm - 0.0005, xm, sec=32))
    p.add('aco_oxidado', caixa(X1 - 0.06, X1 - 0.035, -0.012, 0.012, -0.0125, 0.0125))


def _transportador_q(q):
    q.add('aco_fosfatado', cil_x(0.0095, 0.005, 0.17, 0.0, 0, 32))
    q.add('aco_fosfatado', menos(caixa(0.05, 0.15, -0.007, 0.0078, 0.0, 0.0097), *[caixa(x, x + 0.0035, -0.008, 0.008, 0.007, 0.012) for x in np.arange(0.085, 0.14, 0.008)]))
    q.add('aco_inox', cil_x(0.0064, 0.17, 0.178, 0.0, 0, 24))
    q.add('aco_oxidado', caixa(0.07, 0.115, 0.0088, 0.0122, -0.003, 0.003))


def _alavanca_q(q, mat='cerakote_verde'):
    q.add(mat, caixa(QX0 - 0.002, 0.035, 0.0078, 0.0145, -0.0045, 0.0045))
    q.add(mat, solido(arred([(QX0 - 0.024, 0.0072), (QX0 - 0.002, 0.0072), (QX0 - 0.002, 0.0152), (QX0 - 0.024, 0.0152)], 0.003), -0.019, 0.019, 0.0012))
    for zs in (-1, 1): q.add(mat, solido(arred([(QX0 - 0.03, 0.0078), (QX0 - 0.012, 0.0078), (QX0 - 0.012, 0.0148), (QX0 - 0.03, 0.0148)], 0.002),
                                          min(zs * 0.014, zs * 0.025), max(zs * 0.014, zs * 0.025), 0.0012))


def _carregador_ar10(q, cap=20, mat='polimero'):
    """Carregador de caixa .308 de polimero (fila dupla), quase reto com leve curva, nervuras, janela de contagem, base com ressalto."""
    L = 0.125 if cap >= 20 else 0.072
    R = 1.2; cx, cy = QMX + R, QMY; fi = L / R
    th = np.linspace(math.pi, math.pi + fi, 30)
    fr = [(cx + (R - 0.034) * math.cos(t), cy + (R - 0.034) * math.sin(t)) for t in th]
    tr = [(cx + (R + 0.034) * math.cos(t), cy + (R + 0.034) * math.sin(t)) for t in th]
    perfil = Polygon(fr + tr[::-1]).buffer(0)
    corpo = solido(arred(list(perfil.exterior.coords)[:-1], 0.0025), -0.0118, 0.0118, 0.0014)
    jan = [solido(arred([(QMX - 0.004, y - 0.004), (QMX + 0.004, y - 0.004), (QMX + 0.004, y + 0.004), (QMX - 0.004, y + 0.004)], 0.002), -0.02, -0.0105)
           for y in np.arange(QMY - 0.035, QMY - L + 0.02, -0.014)]
    q.add(mat, menos(corpo, *jan))
    for j in jan: q.add('lente_clara', inter([j, caixa(-1, 1, -1, 1, -0.0107, -0.0103)]))
    for k in np.linspace(0.2, 0.85, 5):
        t = math.pi + fi * k; c, s_ = math.cos(t), math.sin(t)
        pts = [(cx + (R - 0.03) * c, cy + (R - 0.03) * s_), (cx + (R - 0.014) * c, cy + (R - 0.014) * s_)]
        for zs in (-1, 1): q.add(mat, solido(LineString(pts).buffer(0.0015, cap_style=1), min(zs * 0.0118, zs * 0.0127), max(zs * 0.0118, zs * 0.0127)))
    t = math.pi + fi; c, s_ = math.cos(t), math.sin(t)
    b0 = np.array([cx + R * c, cy + R * s_]); d = np.array([c, s_]); nn = np.array([s_, -c])
    base = [b0 + d * 0.037 - nn * 0.002, b0 - d * 0.036 - nn * 0.002, b0 - d * 0.037 + nn * 0.009, b0 + d * 0.039 + nn * 0.009]
    q.add(mat, solido(Polygon([tuple(x) for x in base]).buffer(0.0018, join_style=1), -0.0135, 0.0135, 0.0018))
    q.add('tinta_branca', caixa(QMX + 0.01, QMX + 0.024, QMY - L - 0.0065, QMY - L - 0.003, -0.0137, -0.0135))
    for zs in (-1, 1): q.add('aco_oxidado', caixa(QMX - 0.03, QMX + 0.026, QMY - 0.003, QMY + 0.0012, zs * 0.0068 - 0.0013, zs * 0.0068 + 0.0013))
    q.merge(_cartucho_308(14), TF.translation_matrix([QMX - 0.034, QMY - 0.0045, 0.0025]))


def _seletor_q(q):
    q.add('aco_oxidado', cil_z(0.0042, -0.0148, -0.0136, 0.022, -0.028, 20))
    q.add('aco_oxidado', solido(arred([(0.022, -0.0305), (0.037, -0.0292), (0.037, -0.0268), (0.022, -0.0255)], 0.001), -0.0156, -0.0148, 0.0003))


def _fuzil_precisao(A, X1, xm):
    A.pivo = (-0.04, -0.1, 0.0)
    _receptores_q(A.base); _guarda_mao_q(A.base, X1, xm)
    pu = A.parte('punho', QPU, explodir=(-0.02, -0.06, 0), tipo='troca', descricao='punho de pistola (troca pelo encaixe_punho)')
    _cabo_fuzil(pu, -0.006, -0.0075); _recolore(pu, QVERDE)
    A.encaixe('encaixe_punho', QPU, 'punho_ar', pai='punho', substitui='punho', explodir=(-0.02, -0.08, 0),
              aceita=['punho_ar', 'punho_ar_tan', 'punho_cavas', 'punho_cavas_tan', 'punho_reto', 'punho_reto_tan'],
              descricao='filho do nó punho; ao pôr um punho aqui, esconda as malhas do nó punho')
    gat = A.parte('gatilho', (0.042, -0.043, 0), explodir=(0.0, -0.06, 0), tipo='gira', eixo='z', curso_graus=-10, descricao='gatilho de duas etapas, leve')
    _gatilho_em(gat, 0.042, -0.043)
    sel = A.parte('seletor', (0.022, -0.028, 0), explodir=(0, 0, -0.04), tipo='gira', eixo='z', curso_graus=90, descricao='trava (0°) / semi (90°)')
    _seletor_q(sel)
    tr = A.parte('ferrolho', (0, 0, 0), explodir=(-0.05, 0.05, 0.04), tipo='desliza', curso_m=-QCF, descricao='transportador: recua 95 mm a cada tiro; fica atrás com o carregador vazio')
    _transportador_q(tr)
    av = A.parte('alavanca', (0, 0, 0), explodir=(-0.06, 0.04, 0), tipo='desliza', curso_m=-0.075, descricao='alavanca de manejo ambidestra (puxa e solta)')
    _alavanca_q(av)
    tj = A.parte('tampa_janela', (0.07, -0.0095, QW), explodir=(0, -0.01, 0.04), tipo='gira', eixo='x', curso_graus=100, descricao='abre no primeiro tiro e fica aberta')
    tj.add('cerakote_verde', caixa(0.0705, 0.1445, -0.0093, 0.0093, QW, QW + 0.0012)); tj.add('aco_inox', cil_x(0.0008, 0.07, 0.145, -0.0095, QW, 10))
    rf = A.parte('retem_ferrolho', (0.07, -0.025, -0.0138), explodir=(0, 0, -0.03), tipo='gira', eixo='z', curso_graus=-8, descricao='retém do ferrolho (esquerda)')
    rf.add('cerakote_verde', solido(arred([(0.06, -0.03), (0.08, -0.032), (0.082, -0.022), (0.064, -0.02)], 0.001), -0.0156, -0.0138, 0.0004))
    car = A.parte('carregador', (QMX, QMY, 0), explodir=(0.02, -0.1, 0), tipo='remove', direcao=[0.05, -1.0, 0.0], municao='municao_308', capacidade=20,
                  descricao='carregador de caixa de 20')
    _carregador_ar10(car, 20)
    YM = QY1 + 0.0055
    A.encaixe('encaixe_mira', (0.09, YM, 0), 'trilho_mira', explodir=(0, 0.08, 0),
              aceita=['luneta_5_25', 'luneta_3_9', 'luneta_4x', 'luneta_1_6', 'mira_holografica', 'mira_ponto_vermelho_tubo', 'mira_reflexa'], padrao='luneta_5_25')
    A.encaixe('encaixe_alca', (QX0 + 0.012, YM, 0), 'alca_trilho', explodir=(-0.02, 0.05, 0), aceita=['alca_rebativel', 'alca_polimero', 'alca_polimero_tan'],
              padrao='alca_rebativel', rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira ou luneta no encaixe_mira')
    A.encaixe('encaixe_massa', (X1 - 0.016, YM, 0), 'massa_trilho', explodir=(0.02, 0.05, 0), aceita=['massa_rebativel', 'massa_polimero', 'massa_polimero_tan'],
              padrao='massa_rebativel', rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira ou luneta no encaixe_mira')
    A.encaixe('mira_ferro', (QX0 + 0.012, YM + 0.0195, 0), 'mira', descricao='centro do furo da alça: câmera de 1ª pessoa olha daqui pela ponta da massa (-Z) sem mira acoplada')
    A.encaixe('encaixe_boca', (xm - 0.015, 0, 0), 'boca_308', explodir=(0.08, 0, 0), aceita=['protetor_rosca_308', 'freio_boca_308', 'supressor_308'],
              padrao='freio_boca_308')
    A.encaixe('encaixe_carregador', (QMX, QMY, 0), 'carregador_ar10', pai='carregador', substitui='carregador', aceita=['carregador_ar10_20', 'carregador_ar10_10'],
              descricao='filho do nó carregador; ao pôr um carregador aqui, esconda as malhas do nó carregador')
    A.encaixe('encaixe_coronha', (QX0 - 0.006, -0.003, 0), 'coronha_ar', explodir=(-0.08, 0, 0),
              aceita=['coronha_precisao_ar', 'coronha_precisao_ar_preta', 'coronha_retratil_ar', 'coronha_fixa_ar'], padrao='coronha_precisao_ar')
    A.encaixe('encaixe_empunhadura', (QX1 + 0.12, -0.034, 0), 'mlok_baixo', explodir=(0, -0.06, 0),
              aceita=['empunhadura_vertical', 'empunhadura_angulada', 'empunhadura_curta', 'empunhadura_quadrada'])
    A.encaixe('encaixe_lanterna', (X1 - 0.05, -0.005, 0.022), 'mlok_lado', explodir=(0, 0, 0.06), aceita=['lanterna_fuzil', 'lanterna_compacta'])
    A.encaixe('encaixe_laser', (X1 - 0.05, -0.005, -0.022), 'mlok_esq', explodir=(0, 0, -0.06), aceita=['laser_fuzil', 'modulo_laser', 'modulo_laser_tan'],
              descricao='lado esquerdo do guarda-mão (a lanterna fica no direito)')
    A.encaixe('encaixe_bipe', (X1 - 0.02, -0.034, 0), 'bipe', explodir=(0, -0.06, 0), aceita=['bipe'])
    A.encaixe('encaixe_bandoleira', (X1 - 0.025, -0.006, -0.0235), 'bandoleira', explodir=(0, 0, -0.04), aceita=['bandoleira'])
    A.encaixe('boca_fogo', (xm, 0, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('saida_estojo', (0.105, 0.0, QW + 0.002), 'efeito', descricao='onde nasce o estojo (vai para a direita e um pouco para trás)')
    aberta = ('tampa_janela', 'r', (1, 0, 0), pose([(0, 100), (0.1, 100)]))
    A.anim('atirar', 0.25, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.02, -10), (0.08, -10), (0.14, 0)])),
                            ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.01, (0, 0, 0)), (0.045, (-QCF, 0, 0)), (0.09, (0, 0, 0))])),
                            ('tampa_janela', 'r', (1, 0, 0), pose([(0, 0), (0.012, 100), (0.25, 100)])),
                            (None, 'r', (0, 0, 1), pose([(0, 0), (0.012, 0), (0.04, 5), (0.25, 0)])),
                            (None, 't', pose([(0, (0, 0, 0)), (0.012, (0, 0, 0)), (0.04, (-0.022, 0.003, 0)), (0.25, (0, 0, 0))]))],
           desc='um tiro semiautomático: transportador recua 95 mm, coice forte de .308; a tampa da janela abre')
    A.anim('atirar_ultimo', 0.25, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.02, -10), (0.08, -10), (0.14, 0)])),
                                   ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.01, (0, 0, 0)), (0.045, (-QCF, 0, 0)), (0.07, (-QCF + 0.003, 0, 0)), (0.25, (-QCF + 0.003, 0, 0))])),
                                   ('retem_ferrolho', 'r', (0, 0, 1), pose([(0, 0), (0.06, -8), (0.25, -8)])),
                                   ('tampa_janela', 'r', (1, 0, 0), pose([(0, 0), (0.012, 100), (0.25, 100)])),
                                   (None, 'r', (0, 0, 1), pose([(0, 0), (0.012, 0), (0.04, 5), (0.25, 0)]))], desc='último tiro: o ferrolho fica preso atrás')
    A.anim('vazia', 0.1, [('ferrolho', 't', pose([(0, (-QCF + 0.003, 0, 0)), (0.1, (-QCF + 0.003, 0, 0))])), aberta,
                          ('retem_ferrolho', 'r', (0, 0, 1), pose([(0, -8), (0.1, -8)]))], laco=True, desc='pose parada: ferrolho atrás')
    dm = (0.01, -0.22, 0)
    troca = ('carregador', 't', pose([(0, (0, 0, 0)), (0.2, (0, 0, 0)), (0.35, (0.001, -0.02, 0)), (0.6, dm), (1.4, dm), (1.7, (0.0, -0.012, 0)), (1.82, (0, 0, 0))]))
    A.anim('recarregar', 2.4, [troca, (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, 18), (1.95, 18), (2.4, 0)])),
                               (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 7), (1.95, 7), (2.4, 0)]))],
           desc='aperta o retém, carregador cai (0,35 s), novo entra (1,82 s); trocar o nó carregador entre 0,6 e 1,4 s')
    A.anim('recarregar_vazia', 2.8, [troca, ('ferrolho', 't', pose([(0, (-QCF + 0.003, 0, 0)), (2.05, (-QCF + 0.003, 0, 0)), (2.1, (0, 0, 0))])), aberta,
                                     ('retem_ferrolho', 'r', (0, 0, 1), pose([(0, -8), (2.0, -8), (2.05, 0)])),
                                     (None, 'r', (1, 0, 0), pose([(0, 0), (0.2, 18), (1.95, 18), (2.1, 4), (2.8, 0)])),
                                     (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 7), (1.95, 7), (2.8, 0)]))],
           desc='troca o carregador e bate no retém: o ferrolho fecha (2,1 s)')
    A.anim('trocar_modo', 0.3, [('seletor', 'r', (0, 0, 1), pose([(0, 0), (0.15, 90), (0.3, 90)]))], desc='seletor: trava -> semi')
    A.anim('inspecionar', 2.8, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -30), (1.2, -30), (1.6, 35), (2.3, 35), (2.8, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 8), (2.3, 8), (2.8, 0)])),
                                ('alavanca', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.65, (-0.035, 0, 0)), (0.95, (-0.035, 0, 0)), (1.05, (0, 0, 0))])),
                                ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.65, (-0.035, 0, 0)), (0.95, (-0.035, 0, 0)), (1.05, (0, 0, 0))])),
                                ('tampa_janela', 'r', (1, 0, 0), pose([(0, 0), (0.55, 0), (0.6, 100), (2.8, 100)]))],
           desc='puxa a alavanca até ver o cartucho na câmara, solta e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.5), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


DADOS_Q = dict(classe='fogo', calibre='.308', municao='municao_308', capacidade=20, dano=92, modo='semiautomático', tiros_por_s=3,
               recarga_s=2.4, recarga_vazia_s=2.8, durabilidade=3500, estojo_s=0.02)


@arma('fuzil_308_precisao', 'Fuzil Atalaia .308 de precisão', 'armas', 'fuzil', alcance_m=200, alcance_max_m=800, precisao=0.95, recuo=0.55,
      ruido_m=240, peso_kg=5.6, raridade='muito raro', valor_troca=260, onde=['quartel', 'delegacia'], **DADOS_Q,
      descricao='Fuzil semiautomático .308 de cano longo, verde-oliva, com guarda-mão octogonal, coronha de precisão e luneta 5-25×. '
                'Acerta zumbi a 200 m e dá tiros seguidos sem mexer no ferrolho. Pesado e muito barulhento sem supressor.')
def fuzil_308_precisao(A): _fuzil_precisao(A, 0.56, 0.7)


@arma('fuzil_308_precisao_curto', 'Fuzil Atalaia .308 curto', 'armas', 'fuzil', alcance_m=150, alcance_max_m=600, precisao=0.9, recuo=0.62,
      ruido_m=250, peso_kg=4.9, raridade='muito raro', valor_troca=230, onde=['quartel', 'delegacia'], **DADOS_Q,
      descricao='O mesmo fuzil com cano e guarda-mão curtos: mais fácil de virar dentro de casa, um pouco menos preciso de longe.')
def fuzil_308_precisao_curto(A): _fuzil_precisao(A, 0.43, 0.53)


# ---------------------------------------------------------------------------- acessorios
def _coronha_precisao(A, mat='polimero_verde'):
    """Coronha de precisao fixa (no tubo do fuzil): corpo alto com furo, apoio de rosto que sobe, soleira regulavel e monope de rosca embaixo."""
    q = A.base
    q.add('aco_oxidado', torno_x([(0.0, -0.003), (0.0172, -0.003), (0.0175, -0.0015), (0.0172, 0.0), (0.0, 0.0)], 48))
    perfil = suave([(-0.004, 0.012), (-0.06, 0.014), (-0.26, 0.016), (-0.272, 0.013), (-0.278, -0.112), (-0.27, -0.12), (-0.235, -0.12),
                    (-0.2, -0.08), (-0.12, -0.05), (-0.05, -0.036), (-0.004, -0.024)], 3)
    larg = lambda x: 0.0172 + 0.0028 * GT.smooth(-0.08, -0.2, x)
    co = corpo_x(perfil, 0.0, -0.282, larg, n=2.8, fatias=140, voltas=56, raio_tras=0.005, raio_frente=0.003)
    furo = arred([(-0.075, -0.028), (-0.19, -0.024), (-0.212, -0.05), (-0.196, -0.068), (-0.15, -0.05), (-0.1, -0.035)], 0.008)
    co = menos(co, solido(furo, -0.05, 0.05), cil_z(0.0045, -0.05, 0.05, -0.25, -0.108, 24),
               caixa(-0.215, -0.085, 0.009, 0.03, -0.03, 0.03))                                        # assento do apoio de rosto
    q.add(mat, inter([co, caixa(-0.262, 0.01, -1, 1, -1, 1)]))
    q.add('aco_oxidado', inter([co, caixa(-0.27, -0.262, -1, 1, -1, 1)]))                                # espacador
    q.add('borracha', inter([co, caixa(-0.3, -0.27, -1, 1, -1, 1)]))
    for zs in (-1, 1):
        q.add('aluminio_preto', cil_z(0.0065, min(zs * 0.0195, zs * 0.022), max(zs * 0.0195, zs * 0.022), -0.25, -0.012, 24))    # roda da soleira
        q.add('aluminio_preto', cil_z(0.0062, min(zs * 0.0185, zs * 0.0212), max(zs * 0.0185, zs * 0.0212), -0.15, 0.0, 24))     # roda do apoio
    q.add('recartilhado', trimesh.creation.cylinder(radius=0.009, segment=[[-0.222, -0.098, 0], [-0.222, -0.118, 0]], sections=32))  # monope
    q.add('borracha', trimesh.creation.cylinder(radius=0.0085, segment=[[-0.222, -0.118, 0], [-0.222, -0.123, 0]], sections=32))
    ap = A.parte('apoio_face', (0, 0, 0), explodir=(0, 0.05, 0), tipo='desliza', curso_m=0.015, eixo='y', descricao='apoio de rosto: sobe até 15 mm')
    sec = suave([(-0.088, 0.009), (-0.212, 0.009), (-0.212, 0.024), (-0.2, 0.028), (-0.1, 0.028), (-0.088, 0.022)], 3)
    ap.add(mat, corpo_x(sec, -0.086, -0.214, lambda x: 0.0148, n=3.0, fatias=60, voltas=40, raio_tras=0.003, raio_frente=0.003))
    for x in (-0.115, -0.185): ap.add('aco_inox', trimesh.creation.cylinder(radius=0.003, segment=[[x, -0.004, 0], [x, 0.012, 0]], sections=16))
    A.anim('subir_apoio', 0.4, [('apoio_face', 't', pose([(0, (0, 0, 0)), (0.4, (0, 0.015, 0))]))], desc='sobe o apoio de rosto (para lunetas altas)')
    A.encaixe('ombro', (-0.28, -0.05, 0), 'efeito', descricao='ponto da soleira que encosta no ombro')
    A.pivo = (0, 0, 0)


@_acessorio('coronha_precisao_ar', 'Coronha de precisão (fuzil)', 'coronha', 'coronha_ar', peso_kg=0.95, raridade='raro', valor_troca=45,
            modificadores={'recuo': 0.85, 'precisao_mirando': 1.15, 'tempo_mirar': 1.1}, onde=['quartel'],
            descricao='Coronha fixa alta, verde-oliva, com apoio de rosto que sobe e monopé de rosca: deixa o fuzil quieto deitado. Serve no tubo de qualquer fuzil.')
def coronha_precisao_ar(A): _coronha_precisao(A)


@_acessorio('coronha_precisao_ar_preta', 'Coronha de precisão preta (fuzil)', 'coronha', 'coronha_ar', peso_kg=0.95, raridade='raro', valor_troca=45,
            modificadores={'recuo': 0.85, 'precisao_mirando': 1.15, 'tempo_mirar': 1.1}, onde=['quartel', 'delegacia'],
            descricao='A mesma coronha de precisão, em polímero preto.')
def coronha_precisao_ar_preta(A): _coronha_precisao(A, 'polimero')


@_acessorio('luneta_5_25', 'Luneta 5-25× de precisão', 'mira', 'trilho_mira', peso_kg=0.98, raridade='muito raro', valor_troca=150, aumento=[5, 25],
            modificadores={'precisao_mirando': 1.7, 'tempo_mirar': 1.3, 'alcance_m': 2.2}, onde=['quartel'],
            linha_de_visada='encaixe "olho"; zoom de 5× a 25×', descricao='Luneta comprida de objetiva grande, torres altas e regulagem lateral de foco. '
                                                                           'Ruim para perto: em 5× já não dá para ver dentro de uma sala.')
def luneta_5_25(A): _luneta(A, -0.205, 0.205, 0.017, 0.0262, 0.0215, True)


@_acessorio('carregador_ar10_20', 'Carregador .308 de fuzil (20)', 'carregador', 'carregador_ar10', capacidade=20, municao='municao_308', peso_kg=0.2,
            raridade='raro', valor_troca=20, descricao='Carregador de polímero de 20 tiros .308 com janelinhas de contagem. Não serve na carabina de ferrolho.')
def carregador_ar10_20(A): _carregador_ar10(A.base, 20); A.pivo = (QMX, QMY, 0)


@_acessorio('carregador_ar10_10', 'Carregador .308 de fuzil (10)', 'carregador', 'carregador_ar10', capacidade=10, municao='municao_308', peso_kg=0.13,
            raridade='incomum', valor_troca=12, modificadores={'recarga_s': 0.95},
            descricao='Carregador curto de 10: o fuzil fica mais baixo para atirar deitado.')
def carregador_ar10_10(A): _carregador_ar10(A.base, 10); A.pivo = (QMX, QMY, 0)
