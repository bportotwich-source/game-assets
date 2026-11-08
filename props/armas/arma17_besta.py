# Arma 16: besta recurva (coronha esqueletada de polimero, caixa do gatilho com trava de corda, trilho de voo com canaleta,
# cabeca de aluminio com bracos recurvos de fibra) com virotes, luneta pequena de distancias, estribo de armar e miras rebativeis.
# Executado por gerar_armas.py depois de arma16_composto.py (usa _catmull, _fita, _haste, _luneta, _rebativel). Desenho proprio.
# Plano de lado: x frente, y cima, z direita. A besta fica deitada: os bracos abrem para os lados (em z) no plano y = LY.
# O modelo parado esta ARMADO e carregado (corda na trava, virote no trilho). "atirar" leva bracos e corda para a posicao
# desarmada; "armar" traz de volta. Cada metade da corda e filha do seu braco e gira na ponta dele (eixo y).
CORES.update({'polimero_oliva': (78, 82, 60), 'virote_vermelho': (190, 40, 30)})
METAL.update({'polimero_oliva': (0.0, 0.6), 'virote_vermelho': (0.0, 0.5)})

LY = 0.0385                      # plano dos bracos, da corda e do centro do virote
Y_TRILHO = 0.034                 # topo do trilho de voo
X_ARMADA = 0.06                  # corda na trava
X_SOLTA = 0.36                   # corda em repouso (desarmada)
RAIZ_B = (0.545, 0.045)          # eixo do braco direito no plano (x, z)
L_VIROTE = 0.43
Y_MIRA = 0.0635                  # topo dos trilhos de mira (atras e na ponte da frente)


def _roty(p, c, graus):
    """Gira o ponto (x, z) em torno de c (x, z) pelo eixo +y (mao direita)."""
    t = math.radians(graus); dx, dz = p[0] - c[0], p[1] - c[1]
    return np.array([c[0] + dx * math.cos(t) + dz * math.sin(t), c[1] - dx * math.sin(t) + dz * math.cos(t)])


def _angy(v): return math.degrees(math.atan2(-v[1], v[0]))


LINHA_BB = _catmull([(0.535, 0.03), (0.55, 0.075), (0.546, 0.13), (0.528, 0.185), (0.5, 0.235), (0.474, 0.27), (0.458, 0.297), (0.452, 0.318),
                     (0.458, 0.334), (0.474, 0.343)], 12)
ESP_BB = lambda s: 0.0048 - 0.0016 * s
LARG_BB = lambda s: 0.0115 - 0.0035 * s


def _nock_besta():
    P = LINHA_BB; d = np.gradient(P, axis=0); d /= np.linalg.norm(d, axis=1)[:, None]; nor = np.stack([-d[:, 1], d[:, 0]], 1)
    k = int(np.argmin(P[:, 0])); s = k / (len(P) - 1); lado = -1 if nor[k][0] > 0 else 1
    return P[k] + nor[k] * lado * (ESP_BB(s) + 0.0014)


N_SOLTA = _nock_besta()
L_CORDA_B = float(np.linalg.norm(N_SOLTA - np.array([X_SOLTA, 0.0])))


def _acha_armado():
    a0, a1 = -70.0, 0.0                                              # braco direito gira negativo (ponta vai para tras)
    for _ in range(60):
        am = (a0 + a1) / 2; n = _roty(N_SOLTA, RAIZ_B, am)
        if np.linalg.norm(n - np.array([X_ARMADA, 0.0])) > L_CORDA_B: a1 = am
        else: a0 = am
    return (a0 + a1) / 2


A_ARMADO = _acha_armado()                                            # giro do braco direito de solto -> armado
N_ARMADA = _roty(N_SOLTA, RAIZ_B, A_ARMADO)
G_BRACO = -A_ARMADO                                                  # na animacao: armado (0) -> solto (G_BRACO) no braco direito
G_CORDA = ((_angy(np.array([X_SOLTA, 0.0]) - N_SOLTA) - _angy(np.array([X_ARMADA, 0.0]) - N_ARMADA) + 180) % 360 - 180) - G_BRACO


def _espelha_z(q):
    M = np.diag([1.0, 1.0, -1.0, 1.0])
    for ms in q.parts.values():
        for m in ms: m.apply_transform(M); m.invert()


def _no_plano_bracos(m):
    """Malha feita no plano xy (y = z de verdade, largura em z) -> deitada no plano dos bracos."""
    m.apply_transform(TF.translation_matrix([0, LY, 0]) @ TF.rotation_matrix(math.pi / 2, [1, 0, 0])); return m


# ---------------------------------------------------------------------------- coronha, caixa do gatilho e trilho
CONT_CORONHA = Polygon(suave([(-0.075, 0.034), (-0.16, 0.036), (-0.3, 0.03), (-0.392, 0.036), (-0.402, 0.03), (-0.404, -0.078), (-0.39, -0.086),
                              (-0.33, -0.072), (-0.2, -0.05), (-0.11, -0.04), (-0.07, -0.03), (-0.06, 0.0)], 3))
JANELA_CORONHA = Polygon(suave([(-0.13, 0.016), (-0.3, 0.012), (-0.33, -0.005), (-0.33, -0.05), (-0.3, -0.058), (-0.2, -0.038), (-0.135, -0.026),
                                (-0.12, -0.006)], 3))
CONT_PUNHO_B = Polygon(suave([(-0.012, -0.02), (-0.052, -0.02), (-0.066, -0.06), (-0.08, -0.112), (-0.072, -0.124), (-0.042, -0.124),
                              (-0.036, -0.1), (-0.022, -0.06)], 3))


def _corpo_besta(p):
    # coronha esqueletada com apoio de rosto e soleira de borracha
    cor = solido(CONT_CORONHA.difference(JANELA_CORONHA), -0.017, 0.017, 0.004)
    p.add('polimero_oliva', cor)
    p.add('borracha', solido(Polygon(suave([(-0.404, 0.032), (-0.42, 0.03), (-0.422, -0.08), (-0.404, -0.08)], 2)), -0.0185, 0.0185, 0.004))
    for y in np.linspace(-0.07, 0.022, 9): p.add('borracha', caixa(-0.4235, -0.4205, y, y + 0.003, -0.016, 0.016))
    p.add('polimero', solido(arred([(-0.29, 0.03), (-0.16, 0.032), (-0.16, 0.05), (-0.27, 0.05)], 0.008), -0.0125, 0.0125, 0.004))   # apoio de rosto
    for x in (-0.25, -0.19): p.add('aluminio_preto', cil_x(0.003, x, x + 0.004, 0.026, 0.0, 12).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1], point=[x, 0.026, 0])))
    p.add('aco_inox', cil_z(0.0032, -0.0172, 0.0172, -0.36, -0.03, 16))                       # pino da bandoleira
    # caixa do gatilho (receptor) com a canaleta de voo no topo
    rec = solido(arred([(-0.08, -0.022), (0.12, -0.022), (0.17, -0.015), (0.17, Y_TRILHO), (-0.08, Y_TRILHO)], 0.004), -0.021, 0.021, 0.003)
    canal = caixa(-0.2, 0.3, Y_TRILHO - 0.012, 0.1, -0.0036, 0.0036)
    p.add('polimero', menos(rec, canal))
    for zs in (-1, 1):                                                                      # paredes da trava (a corda passa na frente)
        p.add('polimero', solido(arred([(0.018, Y_TRILHO - 0.002), (0.058, Y_TRILHO - 0.002), (0.055, 0.05), (0.024, 0.052)], 0.003),
                                min(zs * 0.0062, zs * 0.0145), max(zs * 0.0062, zs * 0.0145), 0.001))
        p.add('aco_inox', cil_z(0.0021, min(zs * 0.0145, zs * 0.0156), max(zs * 0.0145, zs * 0.0156), 0.042, 0.03, 12))
    for zs in (-1, 1):                                                                      # paineis rebaixados e parafusos do receptor
        a, b = min(zs * 0.0203, zs * 0.0213), max(zs * 0.0203, zs * 0.0213)
        p.add('polimero_oliva', solido(arred([(0.062, -0.014), (0.15, -0.012), (0.158, 0.0), (0.158, 0.024), (0.07, 0.024)], 0.005), a, b, 0.0004))
        for (x, y) in ((-0.07, 0.026), (-0.07, -0.012), (0.012, 0.026), (0.165, 0.026), (0.12, -0.016)):
            p.add('aco_inox', cil_z(0.0019, min(zs * 0.021, zs * 0.0216), max(zs * 0.021, zs * 0.0216), x, y, 12))
        p.add('tinta_vermelha', caixa(0.0, 0.006, 0.006, 0.011, min(zs * 0.0209, zs * 0.0213), max(zs * 0.0209, zs * 0.0213)))                # marca F da trava de seguranca
    # suporte do trilho de mira (atras da trava) e trilho
    p.add('polimero', solido(arred([(-0.078, Y_TRILHO - 0.003), (0.016, Y_TRILHO - 0.003), (0.012, Y_MIRA - 0.0055), (-0.074, Y_MIRA - 0.0055)], 0.003),
                             -0.012, 0.012, 0.0015))
    trilho(p, 'aluminio_preto', -0.078, 0.014, Y_MIRA - 0.0055, False)
    # punho (pistola) e guarda-mato
    p.add('polimero_grip', punho_redondo(CONT_PUNHO_B, -0.019, -0.124, lambda y: 0.0145, n=2.4, fatias=90, voltas=40, raio_base=0.005))
    gm = Polygon(suave([(0.05, -0.021), (0.05, -0.03), (0.035, -0.05), (-0.01, -0.052), (-0.024, -0.048), (-0.026, -0.04), (-0.012, -0.042),
                        (0.03, -0.042), (0.04, -0.03), (0.04, -0.021)], 2))
    p.add('polimero', solido(gm, -0.006, 0.006, 0.0015))
    # trilho de voo (aluminio) com a parte de baixo moldada como guarda-mao e abas que protegem os dedos
    sec = Polygon([(-0.02, Y_TRILHO), (-0.0036, Y_TRILHO), (-0.0036, Y_TRILHO - 0.012), (0.0036, Y_TRILHO - 0.012), (0.0036, Y_TRILHO), (0.02, Y_TRILHO),
                   (0.021, Y_TRILHO - 0.002), (0.021, 0.004), (0.0185, -0.004), (-0.0185, -0.004), (-0.021, 0.004), (-0.021, Y_TRILHO - 0.002)])
    tr = ext_x(sec, 0.165, 0.51)
    for x in np.linspace(0.36, 0.46, 4): tr = menos(tr, solido(LineString([(x - 0.008, 0.016), (x + 0.008, 0.016)]).buffer(0.0045, 12), -0.03, 0.03))
    p.add('aluminio_preto', tr)
    p.add('fibra_preta', caixa(0.165, 0.51, Y_TRILHO - 0.0122, Y_TRILHO - 0.0112, -0.0036, 0.0036))   # fundo da canaleta (fita de deslize)
    fe = Polygon(suave([(0.165, -0.004), (0.34, -0.004), (0.34, -0.012), (0.325, -0.03), (0.2, -0.032), (0.18, -0.026), (0.165, -0.015)], 3))
    p.add('polimero_oliva', solido(fe, -0.0195, 0.0195, 0.004))
    for x in np.linspace(0.205, 0.315, 8): p.add('borracha', solido(arred([(x, -0.031), (x + 0.006, -0.031), (x + 0.006, -0.012), (x, -0.012)], 0.002), -0.0205, 0.0205, 0.001))
    for zs in (-1, 1):                                                                      # aba de protecao dos dedos
        p.add('polimero_oliva', solido(arred([(0.17, 0.0), (0.335, 0.0), (0.33, 0.018), (0.175, 0.018)], 0.004), min(zs * 0.0205, zs * 0.03), max(zs * 0.0205, zs * 0.03), 0.002))
        p.add('tinta_vermelha', caixa(0.33, 0.333, 0.002, 0.016, min(zs * 0.0298, zs * 0.0302), max(zs * 0.0298, zs * 0.0302)))
        placa_mlok(p, 'aluminio_preto', 0.37, 0.45, 0.004, zs * 0.021, zs, alt=0.014, esp=0.0035)
    placa_mlok_baixo(p, 'aluminio_preto', 0.355, 0.47, -0.004, esp=0.004)
    # cabeca (aluminio): bolsos dos bracos dos dois lados e ponte de baixo; parafusos dos bracos
    p.add('aluminio_preto', solido(arred([(0.5, -0.016), (0.585, -0.016), (0.6, 0.0), (0.59, 0.022), (0.5, 0.022)], 0.008), -0.062, 0.062, 0.004))
    for zs in (-1, 1):
        pod = solido(arred([(0.505, 0.022), (0.582, 0.022), (0.59, 0.03), (0.58, 0.056), (0.52, 0.057), (0.505, 0.048)], 0.007), min(zs * 0.02, zs * 0.064), max(zs * 0.02, zs * 0.064), 0.004)
        fenda = solido(Polygon([(0.4, LY - 0.0122), (0.62, LY - 0.0122), (0.62, LY + 0.0122), (0.4, LY + 0.0122)]), min(zs * 0.026, zs * 0.08), max(zs * 0.026, zs * 0.08))
        p.add('aluminio_preto', menos(pod, fenda))
        p.add('aco_inox', _haste([RAIZ_B[0], -0.022, zs * RAIZ_B[1]], [RAIZ_B[0], 0.064, zs * RAIZ_B[1]], 0.0036, 14))
        p.add('aluminio_preto', _haste([RAIZ_B[0], 0.06, zs * RAIZ_B[1]], [RAIZ_B[0], 0.066, zs * RAIZ_B[1]], 0.0072, 6))      # cabeca sextavada
        p.add('borracha', _haste([0.584, LY, zs * 0.052], [0.594, LY, zs * 0.052], 0.0065, 18))                                      # amortecedor de braco
    # ponte da massa (por cima do virote) com trilho curto
    for zs in (-1, 1):
        p.add('aluminio_preto', solido(arred([(0.478, Y_TRILHO - 0.002), (0.512, Y_TRILHO - 0.002), (0.512, Y_MIRA - 0.0055), (0.478, Y_MIRA - 0.0055)], 0.003),
                                       min(zs * 0.0175, zs * 0.0215), max(zs * 0.0175, zs * 0.0215), 0.001))
    p.add('aluminio_preto', solido(arred([(0.478, Y_MIRA - 0.0105), (0.512, Y_MIRA - 0.0105), (0.512, Y_MIRA - 0.0055), (0.478, Y_MIRA - 0.0055)], 0.002), -0.0215, 0.0215, 0.001))
    trilho(p, 'aluminio_preto', 0.478, 0.512, Y_MIRA - 0.0055, False)
    p.add('aluminio_preto', cil_x(0.0065, 0.596, 0.606, 0.0, 0.0, 20))                       # bucha do estribo


def _braco_besta(q):
    """Braco direito (filho do no, deitado): laminado de fibra com faces de carbono, ponta recurva de reforco e laco da corda."""
    P = LINHA_BB
    m = _fita(P, LARG_BB, ESP_BB, 0.3); q.add('fibra_preta', _no_plano_bracos(m))
    f = inter([_fita(P, lambda s: LARG_BB(s) + 0.0002, lambda s: ESP_BB(s) * 0.55, 0.3), caixa(-1, 1, -1, 1, -LARG_BB(0) * 0.6, LARG_BB(0) * 0.6)])
    q.add('carbono', _no_plano_bracos(inter([_fita(P, lambda s: LARG_BB(s) + 0.0003, lambda s: ESP_BB(s) + 0.0003, 0.3), caixa(-1, 1, -1, 1, -0.0042, 0.0042)])))
    q.add('plastico_branco', _no_plano_bracos(inter([_fita(P, lambda s: LARG_BB(s) + 0.0005, lambda s: ESP_BB(s) + 0.0006, 0.3), solido(sbox(-1, 0.33, 1, 1), -0.03, 0.03)])))
    q.add('corda_arco', trimesh.creation.torus(0.0042, 0.0012, major_sections=16, minor_sections=6).apply_transform(
        TF.translation_matrix([N_SOLTA[0], LY, N_SOLTA[1]])))
    for ms in q.parts.values():                                                              # vai para a posicao armada
        for mm in ms: mm.apply_transform(TF.rotation_matrix(math.radians(A_ARMADO), [0, 1, 0], point=[RAIZ_B[0], LY, RAIZ_B[1]]))


def _corda_besta(q):
    n = np.array([N_ARMADA[0], LY, N_ARMADA[1]]); c = np.array([X_ARMADA, LY, 0.0]); d = (c - n) / np.linalg.norm(c - n)
    q.add('corda_arco', _haste(n, c + d * 0.0015, 0.0017, 10))
    q.add('polimero', _haste(c - d * 0.05, c + d * 0.0015, 0.0021, 12))                        # reforco central (onde a trava segura)
    q.add('polimero', _haste(n + d * 0.004, n + d * 0.045, 0.0021, 12))
    pm = n + d * 0.08
    for k in range(6):                                                                         # silenciador de fios de borracha
        a = k * math.pi / 3; v = np.array([math.sin(a) * 0.0035, math.cos(a) * 0.008, math.sin(a) * 0.006])
        q.add('borracha', _haste(pm, pm + v, 0.0009, 6))


def _virote(q, ponta='caca', cor='virote_vermelho', haste='carbono', ):
    """Virote deitado em x: entalhe (nock em meia-lua) em x = 0, ponta em L_VIROTE. Pena impar para baixo (corre na canaleta)."""
    r = 0.0045; L = L_VIROTE
    q.add(haste, cil_x(r, 0.008, L - 0.012, sec=18))
    q.add('plastico_branco', menos(torno_x([(0.0, 0.0), (r + 0.0003, 0.0), (r + 0.0003, 0.012), (r, 0.014)], 18), cil_z(0.0034, -0.01, 0.01, -0.0012, 0.0, 16)))
    q.add('aluminio_preto' if haste == 'carbono' else 'latao', tubo_x(r - 0.0002, r + 0.0004, L - 0.016, L - 0.01, sec=18))
    for i in range(3):
        v = solido(arred([(0.03, 0.0), (0.085, 0.0), (0.082, 0.006), (0.068, 0.0095), (0.05, 0.0085)], 0.003), -0.0004, 0.0004)
        v.apply_translation([0, r - 0.0005, 0]); v.apply_transform(TF.rotation_matrix(math.pi + i * 2 * math.pi / 3, [1, 0, 0]))
        q.add('tinta_branca' if i == 0 else cor, v)
    q.add('tinta_branca', tubo_x(r, r + 0.0002, 0.1, 0.11, sec=18))
    if ponta == 'caca':
        q.add('aco_inox', torno_x([(r + 0.0004, L - 0.011), (0.0052, L - 0.004), (0.0045, L + 0.016), (0.0, L + 0.032)], 18))
        for i in range(3):
            lam = solido(Polygon([(L - 0.002, 0.0), (L + 0.03, 0.0), (L + 0.004, 0.0135), (L - 0.002, 0.012)]), -0.0004, 0.0004)
            lam.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 3 + math.pi / 3, [1, 0, 0])); q.add('aco_inox', lam)
    elif ponta == 'prego':
        q.add('aco_oxidado', cil_x(0.0018, L - 0.03, L + 0.034, sec=10)); q.add('aco_oxidado', torno_x([(0.0018, L + 0.034), (0.0, L + 0.042)], 10))
        for x in np.linspace(L - 0.03, L - 0.004, 9): q.add('fita_cinza', tubo_x(r + 0.0002, r + 0.0012, x, x + 0.0024, sec=16))
    else:
        q.add('aco_inox', torno_x([(r + 0.0004, L - 0.011), (0.005, L - 0.004), (0.005, L + 0.008), (0.0, L + 0.02)], 18))


# ---------------------------------------------------------------------------- a besta
def _besta(A):
    A.pivo = (-0.04, -0.06, 0.0)
    _corpo_besta(A.base)
    br = A.parte('braco_dir', (RAIZ_B[0], LY, RAIZ_B[1]), explodir=(0, 0, 0.08), tipo='gira', eixo='y', curso_graus=G_BRACO,
                 descricao='braço direito: com a besta armada fica dobrado para trás; abre no disparo')
    _braco_besta(br)
    be = A.parte('braco_esq', (RAIZ_B[0], LY, -RAIZ_B[1]), explodir=(0, 0, -0.08), tipo='gira', eixo='y', curso_graus=-G_BRACO, descricao='braço esquerdo (espelho)')
    _braco_besta(be); _espelha_z(be)
    cd = A.parte('corda_dir', (N_ARMADA[0], LY, N_ARMADA[1]), pai='braco_dir', explodir=(-0.04, 0.02, 0), tipo='gira', eixo='y', curso_graus=G_CORDA,
                 descricao='metade direita da corda (filha do braço direito)')
    _corda_besta(cd)
    ce = A.parte('corda_esq', (N_ARMADA[0], LY, -N_ARMADA[1]), pai='braco_esq', explodir=(-0.04, 0.02, 0), tipo='gira', eixo='y', curso_graus=-G_CORDA,
                 descricao='metade esquerda da corda')
    _corda_besta(ce); _espelha_z(ce)
    tv = A.parte('trava_corda', (0.04, 0.03, 0), explodir=(0, 0.04, 0), tipo='gira', eixo='z', curso_graus=-30,
                 descricao='garras que seguram a corda armada; abrem para trás quando o gatilho solta')
    for zs in (-1, 1):
        tv.add('aco_inox', solido(arred([(0.034, 0.026), (0.048, 0.026), (0.066, 0.036), (0.068, 0.046), (0.062, 0.047), (0.056, 0.04), (0.036, 0.036)], 0.0012),
                                  min(zs * 0.0047, zs * 0.0060), max(zs * 0.0047, zs * 0.0060), 0.0003))
    tv.add('aco_inox', cil_z(0.0024, -0.0062, 0.0062, 0.04, 0.03, 14))
    tv.add('tinta_laranja', solido(arred([(0.03, 0.037), (0.038, 0.037), (0.04, 0.047), (0.032, 0.047)], 0.001), -0.0015, 0.0015, 0.0003))   # alavanca contra disparo em vazio
    gt = A.parte('gatilho', (0.022, -0.02, 0), explodir=(0.03, -0.04, 0), tipo='gira', eixo='z', curso_graus=-12, descricao='puxa para trás ao atirar')
    gt.add('aco_oxidado', solido(Polygon(suave([(0.016, -0.02), (0.026, -0.02), (0.025, -0.03), (0.022, -0.04), (0.016, -0.045), (0.014, -0.043), (0.018, -0.032), (0.017, -0.024)], 2)),
                                 -0.0035, 0.0035, 0.0008))
    sg = A.parte('seguranca', (0.003, 0.0085, 0.021), explodir=(0, 0, 0.04), tipo='gira', eixo='z', curso_graus=50,
                 descricao='trava de segurança (dos dois lados): para a frente = F (dispara), para trás = S; arma sozinha ao armar')
    for zs in (-1, 1):
        sg.add('polimero', solido(arred([(-0.004, 0.006), (0.016, 0.006), (0.016, 0.011), (-0.004, 0.011)], 0.0022), min(zs * 0.021, zs * 0.0245), max(zs * 0.021, zs * 0.0245), 0.0008))
    vr = A.parte('virote', (X_ARMADA, LY, 0), explodir=(0.0, 0.05, 0), tipo='remove', direcao=[0.0, 1.0, 0.0], municao='virote_caca', capacidade=1,
                 descricao='virote deitado no trilho com a nock encostada na corda armada')
    _virote(vr)
    for ms in vr.parts.values():
        for m in ms: m.apply_translation([X_ARMADA, LY, 0])
    A.encaixe('encaixe_virote', (X_ARMADA, LY, 0), 'virote', pai='virote', substitui='virote', aceita=['virote_caca', 'virote_campo', 'virote_prego'],
              descricao='filho do nó virote: o virote escolhido troca a malha (nock na corda)')
    A.encaixe('encaixe_mira', (-0.032, Y_MIRA, 0), 'trilho_mira', explodir=(0, 0.07, 0), padrao='luneta_besta',
              aceita=['luneta_besta', 'luneta_4x', 'luneta_4x_22', 'mira_ponto_vermelho_tubo', 'mira_holografica', 'mira_reflexa'])
    A.encaixe('encaixe_alca', (-0.066, Y_MIRA, 0), 'alca_trilho', explodir=(-0.02, 0.05, 0), aceita=['alca_rebativel'], padrao='alca_rebativel',
              rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira ou luneta no encaixe_mira')
    A.encaixe('encaixe_massa', (0.495, Y_MIRA, 0), 'massa_trilho', explodir=(0.02, 0.05, 0), aceita=['massa_rebativel'], padrao='massa_rebativel',
              rebate_com='encaixe_mira', descricao='na ponte por cima do virote; deita quando há mira ou luneta')
    A.encaixe('mira_ferro', (-0.066, Y_MIRA + 0.0195, 0), 'mira', descricao='centro do furo da alça: câmera de 1ª pessoa olha daqui pela ponta da massa (-Z)')
    A.encaixe('encaixe_estribo', (0.606, 0.0, 0), 'estribo_besta', explodir=(0.08, 0, 0), aceita=['estribo_besta'], padrao='estribo_besta',
              descricao='bucha na frente da cabeça: estribo para pôr o pé e armar')
    A.encaixe('encaixe_lanterna', (0.41, 0.004, 0.021), 'mlok_lado', explodir=(0, 0, 0.06), aceita=ACEITA_LANTERNA, descricao='placa de M-LOK do lado direito do trilho')
    A.encaixe('encaixe_laser', (0.41, 0.004, -0.021), 'mlok_esq', explodir=(0, 0, -0.06), aceita=ACEITA_LASER, descricao='placa de M-LOK do lado esquerdo do trilho')
    A.encaixe('encaixe_empunhadura', (0.4125, -0.004, 0), 'mlok_baixo', explodir=(0, -0.06, 0), aceita=ACEITA_EMPUNHADURA,
              descricao='placa de M-LOK embaixo do trilho, na frente do guarda-mão (os dedos ficam longe da corda)')
    A.encaixe('boca_fogo', (0.6, LY, 0), 'efeito', descricao='de onde o virote sai (projétil para -Z, sem clarão, estalo seco)')
    # ---- animacoes
    def solta(ks):
        """ks = [(t, f)]: f = 0 armada, 1 solta (desarmada)."""
        return [('braco_dir', 'r', (0, 1, 0), pose([(t, f * G_BRACO) for t, f in ks])), ('braco_esq', 'r', (0, 1, 0), pose([(t, -f * G_BRACO) for t, f in ks])),
                ('corda_dir', 'r', (0, 1, 0), pose([(t, f * G_CORDA) for t, f in ks])), ('corda_esq', 'r', (0, 1, 0), pose([(t, -f * G_CORDA) for t, f in ks]))]
    trava = lambda ks: ('trava_corda', 'r', (0, 0, 1), pose(ks))
    gat = lambda ks: ('gatilho', 'r', (0, 0, 1), pose(ks))
    seg = lambda ks: ('seguranca', 'r', (0, 0, 1), pose(ks))
    A.anim('atirar', 0.5, solta([(0, 0), (0.06, 0), (0.085, 1.04), (0.12, 0.97), (0.16, 1.015), (0.22, 0.995), (0.3, 1.0), (0.5, 1.0)]) +
           [gat([(0, 0), (0.05, -12), (0.25, -12), (0.4, 0)]), trava([(0, 0), (0.06, 0), (0.08, -30), (0.5, -30)]),
            ('virote', 't', pose([(0, (0, 0, 0)), (0.06, (0, 0, 0)), (0.085, (X_SOLTA - X_ARMADA, 0, 0)), (0.11, (0.9, 0, 0)), (0.5, (0.9, 0, 0))])),
            (None, 'r', (0, 0, 1), pose([(0, 0), (0.09, 2.0), (0.3, 0)])), (None, 't', pose([(0, (0, 0, 0)), (0.09, (-0.008, 0, 0)), (0.3, (0, 0, 0))]))],
           desc='dispara: o gatilho solta a trava, a corda bate na frente e vibra, o virote voa (esconda o nó virote aos 0,09 s). Termina desarmada')
    A.anim('vazia', 0.1, solta([(0, 1), (0.1, 1)]) + [trava([(0, -30), (0.1, -30)])], desc='pose desarmada (depois de atirar, até armar de novo)')
    A.anim('armar', 2.8, solta([(0, 1), (0.6, 1), (1.0, 0.82), (1.5, 0.35), (1.85, 0.03), (1.95, 0)]) +
           [trava([(0, -30), (1.85, -30), (1.95, 0)]), seg([(0, 0), (1.95, 0), (2.05, 50), (2.8, 50)]),
            (None, 'r', (0, 0, 1), pose([(0, 0), (0.5, -72), (2.1, -72), (2.8, 0)])), (None, 't', pose([(0, (0, 0, 0)), (0.5, (0.05, -0.25, 0)), (2.1, (0.05, -0.25, 0)), (2.8, (0, 0, 0))]))],
           desc='põe o pé no estribo (ponta para baixo), puxa a corda com as duas mãos até a trava (1,95 s); a segurança vai para S sozinha. Sem estribo: 3,6 s')
    A.anim('destravar', 0.2, [seg([(0, 50), (0.2, 0)])], desc='polegar empurra a segurança para F')
    A.anim('travar', 0.2, [seg([(0, 0), (0.2, 50)])], desc='segurança para S')
    A.anim('carregar', 1.2, [('virote', 't', pose([(0, (0.05, 0.12, 0.1)), (0.3, (0.05, 0.12, 0.1)), (0.7, (0.06, 0.012, 0.0)), (0.95, (0.02, 0.0, 0.0)), (1.1, (0, 0, 0))])),
                             (None, 'r', (1, 0, 0), pose([(0, 0), (0.3, -12), (0.95, -12), (1.2, 0)]))],
           desc='deita um virote no trilho (pena ímpar na canaleta) e empurra até a nock encostar na corda; mostre o nó virote aos 0,3 s')
    A.anim('inspecionar', 2.4, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.5, 45), (1.2, 45), (1.6, -35), (2.0, -35), (2.4, 0)])),
                                (None, 'r', (0, 1, 0), pose([(0, 0), (0.5, 20), (2.0, 20), (2.4, 0)]))], desc='vira a besta para olhar os braços e a corda')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.6), (3.0, 0)])), (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))],
           laco=True, desc='respiração leve parado')


@arma('besta_recurva', 'Besta recurva', 'armas', 'besta', classe='besta', calibre='virote', municao='virote_caca', capacidade=1, dano=110,
      alcance_m=45, alcance_max_m=80, modo='um tiro (armar com o pé no estribo)', tiros_por_s=0.2, recarga_s=1.2, armar_s=2.8, armar_sem_estribo_s=3.6,
      precisao=0.88, recuo=0.15, ruido_m=10, durabilidade=1400, peso_kg=3.4, raridade='raro', valor_troca=95, virote_volta=0.7, forca_lb=165,
      fica_armada=True, onde=['casa_de_campo', 'galeria', 'armazem', 'loja_caca'],
      descricao='Besta de 165 lb com braços recurvos e coronha esqueletada: atira forte e quase sem barulho, e pode ficar armada esperando '
                '(sem cansar o braço). Armar é lento: pé no estribo e puxar com as duas mãos. Mantenha os dedos embaixo das abas do guarda-mão.')
def besta_recurva(A): _besta(A)


# ---------------------------------------------------------------------------- municao: virotes
for _id, _nome, _p, _cor, _h, _dano, _desc in (
        ('virote_caca', 'Virote de caça', 'caca', 'virote_vermelho', 'carbono', 1.0, 'Haste de carbono com ponta de 3 lâminas: atravessa fundo.'),
        ('virote_campo', 'Virote de ponta de campo', 'campo', 'pena_branca', 'carbono', 0.8, 'Ponta simples de aço: quase sempre dá para usar de novo.'),
        ('virote_prego', 'Virote improvisado (prego)', 'prego', 'pena_laranja', 'haste_madeira', 0.65, 'Haste de cabo de vassoura com um prego preso com fita: feito na bancada, erra mais.')):
    REG[_id] = dict(id=_id, nome=_nome, grupo='municao', categoria='municao', calibre='virote', peso_kg=0.03, empilha=12, multiplicador_dano=_dano,
                    raridade='incomum' if _p == 'caca' else 'comum', onde=['casa_de_campo', 'armazem', 'galeria'], encaixe='virote',
                    descricao=_desc + ' Pivô na nock (ponto que encosta na corda).',
                    fn=(lambda p, c, h: (lambda A: (_virote(A.base, p, c, h), setattr(A, 'pivo', (0, 0, 0)))))(_p, _cor, _h))


# ---------------------------------------------------------------------------- acessorios
@_acessorio('luneta_besta', 'Luneta de besta (distâncias)', 'mira', 'trilho_mira', peso_kg=0.32, raridade='incomum', valor_troca=40, aumento=[3, 3],
            modificadores={'precisao_mirando': 1.4, 'tempo_mirar': 1.1, 'alcance_m': 1.2}, usa='pilhas', onde=['casa_de_campo', 'galeria', 'loja_caca'],
            linha_de_visada='encaixe "olho"; 3× fixa; pontos de 20, 30, 40 e 50 m abaixo do centro',
            descricao='Luneta curta de 3× com retículo de vários pontos (um para cada distância: o virote cai bem mais que uma bala) e iluminação vermelha.')
def luneta_besta(A):
    _luneta(A, -0.105, 0.105, 0.0127, 0.017, 0.0165, False)
    q = A.base; yc = 0.028; x = -0.105 + 0.006
    for k in range(1, 5):
        q.add('ponto_vermelho', cil_x(0.00045, x - 0.0002, x + 0.0002, yc - k * 0.0017, 0, 8))
        q.add('aluminio_preto', caixa(x - 0.0001, x + 0.0001, yc - k * 0.0017 - 0.00012, yc - k * 0.0017 + 0.00012, -0.0016 - 0.0003 * k, -0.0008))
        q.add('aluminio_preto', caixa(x - 0.0001, x + 0.0001, yc - k * 0.0017 - 0.00012, yc - k * 0.0017 + 0.00012, 0.0008, 0.0016 + 0.0003 * k))
    q.add('tinta_branca', caixa(0.03, 0.034, yc + 0.0127 + 0.0001, yc + 0.0129, -0.006, 0.006))


@_acessorio('estribo_besta', 'Estribo de besta', 'estribo', 'estribo_besta', peso_kg=0.18, raridade='comum', valor_troca=8, modificadores={'armar_s': 0.78},
            onde=['casa_de_campo', 'armazem'], descricao='Alça de aço com sapata de borracha na frente da besta: pé dentro, ponta no chão, e dá para armar bem mais rápido.')
def estribo_besta(A):
    q = A.base; x0 = 0.606
    q.add('aluminio_preto', torno_x([(0.0, x0), (0.0095, x0), (0.0095, x0 + 0.014), (0.007, x0 + 0.018), (0.0, x0 + 0.018)], 24))
    pts = _catmull([(x0 + 0.012, -0.004, 0.04), (x0 + 0.04, -0.012, 0.075), (x0 + 0.1, -0.03, 0.08), (x0 + 0.14, -0.04, 0.05), (x0 + 0.15, -0.042, 0.0),
                    (x0 + 0.14, -0.04, -0.05), (x0 + 0.1, -0.03, -0.08), (x0 + 0.04, -0.012, -0.075), (x0 + 0.012, -0.004, -0.04)], 8)
    for i in range(len(pts) - 1): q.add('aco_oxidado', _haste(pts[i], pts[i + 1], 0.0058, 12))
    for zs in (-1, 1):
        q.add('aco_oxidado', solido(arred([(x0 - 0.002, -0.012), (x0 + 0.02, -0.012), (x0 + 0.02, 0.012), (x0 - 0.002, 0.012)], 0.004), min(zs * 0.034, zs * 0.046), max(zs * 0.034, zs * 0.046), 0.001))
        q.add('aco_oxidado', caixa(x0 + 0.012, x0 + 0.02, -0.006, 0.006, -0.046 if zs < 0 else 0.0, 0.0 if zs < 0 else 0.046))
    for i in range(len(pts) // 2 - 12, len(pts) // 2 + 12):                                  # sapata de borracha na curva da frente
        q.add('borracha', _haste(pts[i], pts[i + 1], 0.0085, 14))
    A.pivo = (x0, 0.0, 0.0)
