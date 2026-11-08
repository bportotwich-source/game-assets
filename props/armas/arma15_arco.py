# Arma 14: arco recurvo de madeira (desmontavel: punho laminado + bracos recurvos) com flechas, aljava de arco, mira de pinos e
# estabilizador. Executado por gerar_armas.py (plano de lado: x frente = para onde a flecha vai, y cima, z direita). Desenho proprio.
# O arco fica em pe; a corda esta atras (x negativo, do lado do arqueiro). Os bracos giram no encaixe do punho e cada metade da
# corda e filha do seu braco: puxar = bracos giram para tras e as duas metades da corda se encontram no ponto de puxada.
CORES.update({'madeira_clara': (198, 160, 112), 'fibra_preta': (30, 30, 32), 'corda_arco': (46, 44, 40), 'pena_laranja': (226, 112, 30),
              'pena_branca': (226, 224, 214), 'haste_madeira': (186, 146, 96), 'tinta_verde_fosca': (64, 92, 52), 'fibra_verde': (60, 210, 80), 'espuma': (70, 72, 70)})
METAL.update({'madeira_clara': (0.0, 0.5), 'fibra_preta': (0.0, 0.35), 'corda_arco': (0.0, 0.85), 'pena_laranja': (0.0, 0.7), 'pena_branca': (0.0, 0.7),
              'haste_madeira': (0.0, 0.6), 'tinta_verde_fosca': (0.0, 0.7), 'fibra_verde': (0.0, 0.3), 'espuma': (0.0, 0.95)})
EMISSIVOS.update({'pino_verde': (0.2, 1.0, 0.3), 'pino_laranja': (1.0, 0.5, 0.05), 'pino_vermelho': (1.0, 0.1, 0.05)})

AY_FLECHA = 0.03                 # altura da flecha no apoio (e do ponto de encaixe na corda)
AX_CORDA = -0.19                 # corda em repouso (altura de armado ~ 19 cm do punho)
AX_PUXADA = -0.55                # ponto de puxada (ancora no rosto)
A_BRACO = 11.0                   # quanto cada braco gira na puxada (graus)
P_BRACO = (0.022, 0.245)         # eixo do braco de cima (o de baixo e espelhado em y)
L_FLECHA = 0.72


def _catmull(pts, n=12):
    P = np.array(pts, float); P = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return np.array(out)


def _fita(pts, meia_larg, meia_esp, ch=0.35):
    """Lamina varrida ao longo de uma curva no plano xy: secao retangular chanfrada (espessura no plano, largura em z).
    meia_larg(s), meia_esp(s) com s de 0 a 1 ao longo da curva."""
    pts = np.asarray(pts, float); n = len(pts)
    d = np.gradient(pts, axis=0); d /= np.linalg.norm(d, axis=1)[:, None]; nor = np.stack([-d[:, 1], d[:, 0]], 1)
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]); S = L / L[-1]
    V = []
    for i in range(n):
        a, b = meia_esp(S[i]), meia_larg(S[i]); c = min(a, b) * ch
        for u, w in ((a, b - c), (a - c, b), (-a + c, b), (-a, b - c), (-a, -b + c), (-a + c, -b), (a - c, -b), (a, -b + c)):
            p = pts[i] + nor[i] * u; V.append([p[0], p[1], w])
    V += [list(np.r_[pts[0], 0.0]), list(np.r_[pts[-1], 0.0])]; F = []
    for i in range(n - 1):
        for j in range(8):
            a0 = i * 8 + j; a1 = i * 8 + (j + 1) % 8; b0 = a0 + 8; b1 = a1 + 8; F += [[a0, a1, b0], [a1, b1, b0]]
    c0, c1 = n * 8, n * 8 + 1
    for j in range(8): F += [[c0, (j + 1) % 8, j], [c1, (n - 1) * 8 + j, (n - 1) * 8 + (j + 1) % 8]]
    m = trimesh.Trimesh(np.array(V), np.array(F), process=True); trimesh.repair.fix_normals(m); return m


def _haste(p0, p1, r, sec=10):
    return trimesh.creation.cylinder(radius=r, segment=[list(p0), list(p1)], sections=sec)


# ---------------------------------------------------------------------------- bracos e corda
LINHA_BRACO = _catmull([(0.022, 0.235), (0.02, 0.29), (0.004, 0.36), (-0.03, 0.44), (-0.08, 0.52), (-0.13, 0.585), (-0.166, 0.628),
                        (-0.18, 0.66), (-0.172, 0.69), (-0.148, 0.712), (-0.118, 0.724)], 14)
ESP_B = lambda s: 0.0052 - 0.0022 * s
LARG_B = lambda s: 0.0205 - 0.0125 * s ** 1.3


def _encosto_corda():
    """Ponto do braco de cima onde a corda deixa a barriga (lado do arqueiro) e a ponta (entalhe da corda)."""
    P = LINHA_BRACO; d = np.gradient(P, axis=0); d /= np.linalg.norm(d, axis=1)[:, None]; nor = np.stack([-d[:, 1], d[:, 0]], 1)
    k = int(np.argmin(P[:, 0]))                                   # ponto mais para tras da curva
    s = k / (len(P) - 1)
    lado = -1 if nor[k][0] > 0 else 1                             # barriga = lado que aponta para tras (-x)
    enc = P[k] + nor[k] * lado * (ESP_B(s) + 0.0012)
    ponta = P[-3] + nor[-3] * lado * (ESP_B(1.0) + 0.0012)
    return enc, ponta, k, lado, nor


N_CORDA, PONTA_CORDA, K_ENC, LADO_B, NOR_B = _encosto_corda()


def _braco(q, cima=True):
    """Braco recurvo laminado: miolo de madeira clara com faces de fibra preta, pe com parafuso e ponta de reforco com entalhe."""
    P = LINHA_BRACO.copy()
    m_fora = _fita(P, LARG_B, ESP_B); m_mio = _fita(P, lambda s: LARG_B(s) + 0.0003, lambda s: ESP_B(s) * 0.45)
    pe = arred([(-0.006, 0.232), (0.034, 0.232), (0.034, 0.3), (-0.006, 0.3)], 0.003)
    for m, mat in ((m_fora, 'fibra_preta'), (m_mio, 'madeira_clara')): q.add(mat, m)
    q.add('madeira_clara', inter([_fita(P, lambda s: LARG_B(s) + 0.0004, lambda s: ESP_B(s) + 0.0004), solido(pe, -0.03, 0.03)]))   # pe de madeira
    q.add('aco_inox', cil_z(0.0045, -0.0215, 0.0215, P_BRACO[0] - 0.006, P_BRACO[1] + 0.018, 24))                                       # parafuso do pe
    # ponta de reforco (polimero claro) e o pedaco de corda que dorme na barriga ate o encosto
    q.add('plastico_branco', inter([_fita(P, lambda s: LARG_B(s) + 0.0006, lambda s: ESP_B(s) + 0.0007), solido(sbox(-1, 0.695, 1, 1), -0.03, 0.03)]))
    a = int(K_ENC); seg = [P[i] + NOR_B[i] * LADO_B * (ESP_B(i / (len(P) - 1)) + 0.0012) for i in range(a, len(P) - 2)]
    for i in range(len(seg) - 1): q.add('corda_arco', _haste(np.r_[seg[i], 0.0], np.r_[seg[i + 1], 0.0], 0.0012, 8))
    q.add('corda_arco', trimesh.creation.torus(0.004, 0.0011, major_sections=16, minor_sections=6).apply_transform(
        TF.translation_matrix([PONTA_CORDA[0], PONTA_CORDA[1], 0]) @ TF.rotation_matrix(math.pi / 2, [0, 1, 0])))       # laco da corda na ponta
    if not cima: _espelha_y(q)


def _espelha_y(q):
    M = np.diag([1.0, -1.0, 1.0, 1.0])
    for ms in q.parts.values():
        for m in ms: m.apply_transform(M); m.invert()


def _corda(q, cima=True):
    """Metade da corda: do encosto no braco ate o ponto de encaixe da flecha, com reforco (serving) e anel de latao no meio."""
    n0 = np.array([N_CORDA[0], N_CORDA[1], 0.0]); c = np.array([AX_CORDA, AY_FLECHA if cima else AY_FLECHA, 0.0])
    if not cima: n0 = np.array([N_CORDA[0], -N_CORDA[1], 0.0])
    q.add('corda_arco', _haste(n0, c, 0.0013, 8))
    d = (c - n0) / np.linalg.norm(c - n0)
    q.add('polimero', _haste(c - d * 0.075, c, 0.0016, 10))                                         # reforco onde a flecha encaixa
    if cima:
        q.add('latao', _haste(c + np.array([0, 0.0085, 0]), c + np.array([0, 0.0115, 0]), 0.0024, 12))   # anel de encaixe (acima da flecha)


def _angulo_corda(sy=1):
    """Giro (local, filho do braco) de uma metade da corda para chegar ao ponto de puxada. sy = 1 cima, -1 baixo."""
    ab = A_BRACO * sy; th = math.radians(ab); R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    pv = np.array([P_BRACO[0], sy * P_BRACO[1]]); nk = np.array([N_CORDA[0], sy * N_CORDA[1]])
    nw = pv + R @ (nk - pv)
    c0 = np.array([AX_CORDA, AY_FLECHA]) - nk; c1 = np.array([AX_PUXADA, AY_FLECHA]) - nw
    a0 = math.atan2(c0[1], c0[0]); a1 = math.atan2(c1[1], c1[0])
    d = math.degrees(a1 - a0); d = (d + 180) % 360 - 180
    return d - ab


ANG_CORDA = _angulo_corda(1)
ANG_CORDA_B = _angulo_corda(-1)


# ---------------------------------------------------------------------------- punho (riser)
CONT_PUNHO = suave([(0.026, 0.262), (0.036, 0.2), (0.042, 0.13), (0.044, 0.06), (0.032, 0.03), (0.026, 0.0), (0.03, -0.04), (0.04, -0.07),
                    (0.044, -0.13), (0.04, -0.2), (0.028, -0.262), (-0.008, -0.262), (-0.008, -0.17), (-0.014, -0.1), (-0.024, -0.062),
                    (-0.042, -0.035), (-0.046, -0.01), (-0.036, 0.012), (-0.016, 0.024), (-0.012, 0.1), (-0.01, 0.17), (-0.008, 0.262)], 3)
LARG_PUNHO = lambda y: 0.0132 + 0.0022 * math.exp(-((y + 0.015) / 0.03) ** 2) - 0.0016 * GT.smooth(0.18, 0.262, abs(y))


def _punho_arco(p):
    corpo = punho_redondo(CONT_PUNHO, 0.262, -0.262, LARG_PUNHO, n=2.5, fatias=160, voltas=48, raio_base=0.003, raio_topo=0.003)
    janela = arred([(-0.03, AY_FLECHA - 0.005), (0.06, AY_FLECHA - 0.005), (0.06, 0.16), (-0.03, 0.15)], 0.004)
    corte = solido(janela, -0.03, 0.0015)                                                         # janela de mira (corta o lado esquerdo)
    corpo = menos(corpo, corte)
    p.add('nogueira', corpo)
    pele = punho_redondo(CONT_PUNHO, 0.262, -0.262, lambda y: LARG_PUNHO(y) + 0.0003, n=2.5, fatias=160, voltas=48, raio_base=0.003, raio_topo=0.003)
    pele = menos(pele, corte)
    for z0 in (-0.0055, 0.0045):                                                                  # lamelas claras (madeira laminada)
        p.add('madeira_clara', inter([pele, caixa(-1, 1, -1, 1, z0, z0 + 0.0016)]))
    p.add('couro', inter([punho_redondo(CONT_PUNHO, 0.262, -0.262, lambda y: LARG_PUNHO(y) + 0.0009, n=2.5, fatias=160, voltas=48), caixa(-1, 1, -0.062, 0.016, -1, 1)]))
    # apoio da flecha (prateleira com pelo) e placa de encosto, buchas de rosca (mira, estabilizador, aljava)
    p.add('borracha', caixa(-0.024, 0.03, AY_FLECHA - 0.0062, AY_FLECHA - 0.0048, -0.008, 0.0015))
    p.add('couro_escuro', caixa(-0.012, 0.012, AY_FLECHA - 0.004, AY_FLECHA + 0.018, 0.0015, 0.0025))
    for (x, y) in ((0.012, 0.1), (0.012, 0.13)):
        p.add('latao', cil_z(0.0032, 0.0128, 0.0136, x, y, 16))
    p.add('latao', torno_x([(0.0045, 0.0), (0.0045, 0.004)], 16, -0.09, 0.0, 0.04))
    for y in (-0.15, 0.2): p.add('latao', cil_z(0.0032, 0.0122, 0.0132, 0.012, y, 16))
    # encaixe dos bracos (bolsos de aco)
    for s in (1, -1):
        y0, y1 = (0.228, 0.262) if s > 0 else (-0.262, -0.228)
        p.add('aco_oxidado', menos(caixa(-0.012, 0.034, y0, y1, -0.016, 0.016), caixa(-0.01, 0.032, y0 - 0.01 if s < 0 else y0 + 0.004, y1 + 0.01 if s > 0 else y1 - 0.004, -0.0125, 0.0125)))


# ---------------------------------------------------------------------------- flecha
def _flecha(q, ponta='caca', cor_pena='pena_laranja', haste='fibra_preta'):
    """Flecha deitada em x: entalhe em x = 0, ponta em L_FLECHA. ponta = 'caca' (3 laminas), 'prego' (prego amarrado), 'campo'."""
    r = 0.0039; L = L_FLECHA
    q.add(haste, cil_x(r, 0.008, L - 0.03, sec=16))
    q.add('plastico_branco', menos(torno_x([(0.0, 0.0), (0.0042, 0.0), (0.0042, 0.006), (r, 0.012)], 16), caixa(-0.001, 0.0045, -0.0014, 0.0014, -0.01, 0.01)))
    q.add(cor_pena if cor_pena != 'pena_laranja' else 'pena_branca', tubo_x(r, r + 0.0002, 0.1, 0.112, sec=16))          # faixa
    for i in range(3):                                                                              # penas (3 a 120 graus)
        pena = solido(arred([(0.02, 0.0), (0.095, 0.0), (0.09, 0.011), (0.05, 0.013), (0.03, 0.008)], 0.003), -0.0004, 0.0004)
        pena.apply_translation([0, r - 0.0005, 0]); pena.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 3, [1, 0, 0]))
        q.add(cor_pena if i else 'pena_branca', pena)
    if ponta == 'caca':
        q.add('aco_inox', torno_x([(r, L - 0.031), (0.0046, L - 0.026), (0.0042, L - 0.012), (0.0, L + 0.012)], 16))
        for i in range(3):
            lam = solido(Polygon([(L - 0.024, 0.0), (L + 0.01, 0.0), (L - 0.018, 0.0125)]), -0.0004, 0.0004)
            lam.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 3 + math.pi / 6, [1, 0, 0])); q.add('aco_inox', lam)
    elif ponta == 'prego':
        q.add('haste_madeira', cil_x(r + 0.0003, L - 0.032, L - 0.002, sec=16))
        q.add('aco_oxidado', cil_x(0.0016, L - 0.03, L + 0.03, sec=10)); q.add('aco_oxidado', torno_x([(0.0016, L + 0.03), (0.0, L + 0.038)], 10))
        q.add('aco_oxidado', cil_x(0.0034, L - 0.032, L - 0.03, sec=12))                            # cabeca do prego
        for x in np.linspace(L - 0.03, L - 0.006, 8): q.add('fita_cinza', tubo_x(r + 0.0002, r + 0.0011, x, x + 0.0025, sec=14))   # fita
    else:
        q.add('aco_inox', torno_x([(r, L - 0.031), (0.0042, L - 0.026), (0.0042, L - 0.008), (0.0, L + 0.004)], 16))


# ---------------------------------------------------------------------------- o arco
def _arco(A):
    A.pivo = (-0.008, -0.022, 0.0)
    _punho_arco(A.base)
    bc = A.parte('braco_cima', (P_BRACO[0], P_BRACO[1], 0), explodir=(0, 0.1, 0), tipo='gira', eixo='z', curso_graus=A_BRACO,
                 descricao='braço de cima: flexiona para trás na puxada (a ponta recurva)')
    _braco(bc, True)
    bb = A.parte('braco_baixo', (P_BRACO[0], -P_BRACO[1], 0), explodir=(0, -0.1, 0), tipo='gira', eixo='z', curso_graus=-A_BRACO,
                 descricao='braço de baixo: espelho do de cima')
    _braco(bb, False)
    cc = A.parte('corda_cima', (N_CORDA[0], N_CORDA[1], 0), pai='braco_cima', explodir=(-0.05, 0, 0), tipo='gira', eixo='z', curso_graus=ANG_CORDA,
                 descricao='metade de cima da corda (filha do braço de cima)')
    _corda(cc, True)
    cb = A.parte('corda_baixo', (N_CORDA[0], -N_CORDA[1], 0), pai='braco_baixo', explodir=(-0.05, 0, 0), tipo='gira', eixo='z', curso_graus=ANG_CORDA_B,
                 descricao='metade de baixo da corda (filha do braço de baixo)')
    _corda(cb, False)
    fl = A.parte('flecha', (AX_CORDA, AY_FLECHA, 0), explodir=(0.0, 0.03, -0.05), tipo='remove', direcao=[0.0, 0.0, -1.0], municao='flecha_caca',
                 capacidade=1, descricao='flecha encaixada na corda e deitada no apoio')
    _flecha(fl, 'caca')
    for ms in fl.parts.values():
        for m in ms: m.apply_translation([AX_CORDA, AY_FLECHA, 0])
    A.encaixe('encaixe_flecha', (AX_CORDA, AY_FLECHA, 0), 'flecha', pai='flecha', substitui='flecha', aceita=['flecha_caca', 'flecha_prego', 'flecha_campo'],
              descricao='filho do nó flecha: a flecha escolhida troca a malha do nó flecha (anda na puxada)')
    A.encaixe('encaixe_mira', (0.012, 0.115, 0.0136), 'rosca_mira_arco', explodir=(0, 0, 0.06), aceita=['mira_pinos_arco'],
              descricao='buchas de latão do lado direito, acima da janela')
    A.encaixe('encaixe_estabilizador', (0.044, -0.09, 0), 'rosca_estabilizador', explodir=(0.08, 0, 0), aceita=['estabilizador_arco', 'estabilizador_curto_arco'],
              descricao='bucha na frente do punho, abaixo da mão')
    A.encaixe('encaixe_aljava', (0.012, 0.025, 0.0132), 'aljava_arco', explodir=(0, 0, 0.08), aceita=['aljava_arco'],
              descricao='buchas do lado direito (em cima e embaixo): aljava presa no arco com 4 flechas')
    A.encaixe('mira_ferro', (AX_PUXADA - 0.07, AY_FLECHA + 0.072, -0.004), 'mira', descricao='olho do arqueiro com o arco puxado (âncora no canto da boca): mire pela ponta da flecha')
    A.encaixe('boca_fogo', (AX_PUXADA + L_FLECHA, AY_FLECHA, 0), 'efeito', descricao='de onde a flecha sai no "soltar" (projétil para -Z, sem clarão e quase sem ruído)')
    br = lambda ks: [('braco_cima', 'r', (0, 0, 1), pose(ks)), ('braco_baixo', 'r', (0, 0, 1), pose([(t, -a) for t, a in ks]))]
    cd = lambda ks: [('corda_cima', 'r', (0, 0, 1), pose(ks)), ('corda_baixo', 'r', (0, 0, 1), pose([(t, a * ANG_CORDA_B / ANG_CORDA) for t, a in ks]))]
    fl_t = lambda ks: ('flecha', 't', pose([(t, (dx, 0, 0)) for t, dx in ks]))
    D = AX_PUXADA - AX_CORDA
    A.anim('puxar', 0.9, br([(0, 0), (0.15, 0), (0.8, A_BRACO), (0.9, A_BRACO)]) + cd([(0, 0), (0.15, 0), (0.8, ANG_CORDA), (0.9, ANG_CORDA)]) +
           [fl_t([(0, 0), (0.15, 0), (0.8, D), (0.9, D)]), (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 3), (0.9, 0)]))],
           desc='puxa a corda até a âncora (0,8 s): os braços flexionam e a flecha recua junto')
    A.anim('segurar', 1.0, br([(0, A_BRACO), (0.5, A_BRACO - 0.3), (1.0, A_BRACO)]) + cd([(0, ANG_CORDA), (0.5, ANG_CORDA - 1.0), (1.0, ANG_CORDA)]) +
           [fl_t([(0, D), (0.5, D + 0.01), (1.0, D)])], laco=True, desc='segurando puxado (treme de leve; cansa o braço depois de alguns segundos)')
    A.anim('soltar', 0.45, br([(0, A_BRACO), (0.03, -1.2), (0.08, 0.8), (0.14, -0.4), (0.22, 0.15), (0.32, 0)]) +
           cd([(0, ANG_CORDA), (0.03, -2.5), (0.08, 1.6), (0.14, -0.8), (0.22, 0.3), (0.32, 0)]) +
           [fl_t([(0, D), (0.03, 0.0), (0.06, 0.9), (0.45, 0.9)]), (None, 'r', (0, 0, 1), pose([(0, 0), (0.03, -2), (0.2, 0)]))],
           desc='solta: a corda volta e vibra; esconda o nó flecha aos 0,03 s e lance o projétil em boca_fogo')
    A.anim('encaixar', 1.3, [('flecha', 't', pose([(0, (0.1, -0.32, 0.12)), (0.35, (0.1, -0.32, 0.12)), (0.75, (0.12, -0.05, 0.03)), (1.05, (0.01, 0.0, 0.0)),
                                                   (1.2, (0, 0, 0))])), (None, 'r', (1, 0, 0), pose([(0, 0), (0.3, -15), (1.0, -15), (1.3, 0)]))],
           desc='pega uma flecha (da aljava ou das costas), deita no apoio (0,75 s) e encaixa na corda (1,2 s); mostre o nó flecha aos 0,35 s')
    A.anim('inspecionar', 2.4, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.5, 50), (1.2, 50), (1.6, -40), (2.0, -40), (2.4, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.5, 10), (2.0, 10), (2.4, 0)]))], desc='gira o arco para conferir os braços e a corda')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.8), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


@arma('arco_recurvo', 'Arco recurvo de madeira', 'armas', 'arco', classe='arco', calibre='flecha', municao='flecha_caca', capacidade=1, dano=70,
      alcance_m=35, alcance_max_m=70, modo='um tiro (puxar, segurar e soltar)', tiros_por_s=0.6, recarga_s=1.3, recarga_vazia_s=1.3, precisao=0.7, recuo=0.05,
      ruido_m=6, durabilidade=1500, peso_kg=1.2, raridade='incomum', valor_troca=45, flecha_volta=0.7, forca_lb=40,
      onde=['casa_de_campo', 'parque', 'galeria', 'armazem'],
      descricao='Arco desmontável de punho de nogueira laminada e braços recurvos (40 lb). Quase não faz barulho, a flecha pode ser recuperada (70%) '
                'e mata zumbi com um tiro na cabeça. Puxar e segurar cansa: não dá para manter mirado muito tempo.')
def arco_recurvo(A): _arco(A)


# ---------------------------------------------------------------------------- municao: flechas
for _id, _nome, _p, _cor, _dano, _desc in (
        ('flecha_caca', 'Flecha de caça', 'caca', 'pena_laranja', 1.0, 'Haste de fibra com ponta de 3 lâminas: corta fundo, mas a ponta pode quebrar ao recuperar.'),
        ('flecha_prego', 'Flecha improvisada (prego)', 'prego', 'pena_branca', 0.7, 'Prego amarrado na ponta com fita: fácil de fazer na bancada, erra mais e quebra fácil.'),
        ('flecha_campo', 'Flecha de ponta de campo', 'campo', 'tinta_verde_fosca', 0.8, 'Ponta de aço simples: entra menos, mas quase sempre dá para usar de novo.')):
    REG[_id] = dict(id=_id, nome=_nome, grupo='municao', categoria='municao', calibre='flecha', peso_kg=0.03, empilha=24, multiplicador_dano=_dano,
                    raridade='comum' if _p != 'caca' else 'incomum', onde=['casa_de_campo', 'parque', 'armazem'], encaixe='flecha',
                    descricao=_desc + ' Pivô no entalhe (ponto que encosta na corda).',
                    fn=(lambda p, c: (lambda A: (_flecha(A.base, p, c), setattr(A, 'pivo', (0, 0, 0)))))(_p, _cor))


# ---------------------------------------------------------------------------- acessorios
@_acessorio('mira_pinos_arco', 'Mira de pinos (arco)', 'mira', 'rosca_mira_arco', peso_kg=0.12, raridade='raro', valor_troca=35, usa='nada',
            modificadores={'precisao_mirando': 1.35}, onde=['casa_de_campo', 'galeria'], linha_de_visada='encaixe "olho": alinhe o pino da distância com o alvo',
            descricao='Haste aparafusada no lado direito do punho com um aro e 3 pinos de fibra (verde 10 m, laranja 20 m, vermelho 30 m) que brilham com pouca luz.')
def mira_pinos_arco(A):
    q = A.base; z0 = 0.0136; xa = 0.085; yc = 0.105; zc = -0.004
    q.add('aluminio_preto', solido(arred([(0.004, 0.09), (0.03, 0.09), (0.03, 0.14), (0.004, 0.14)], 0.003), z0, z0 + 0.005, 0.001))        # placa
    q.add('aluminio_preto', caixa(0.03, xa - 0.01, 0.1, 0.11, z0 + 0.0005, z0 + 0.0045))                                                    # haste
    q.add('aluminio_preto', solido(arred([(xa - 0.012, yc - 0.012), (xa - 0.006, yc - 0.012), (xa - 0.006, yc + 0.012), (xa - 0.012, yc + 0.012)], 0.002), zc, z0 + 0.0045, 0.0008))
    aro = Point(0.0, 0.0).buffer(0.0175, 40).difference(Point(0.0, 0.0).buffer(0.0145, 40))
    m = ext_x(affinity.translate(affinity.rotate(aro, 0), zc, yc), xa - 0.005, xa + 0.005); q.add('aluminio_preto', m)
    for i, (dy, mat) in enumerate(((0.006, 'pino_verde'), (0.0, 'pino_laranja'), (-0.006, 'pino_vermelho'))):
        q.add('aco_inox', _haste([xa, yc + dy, zc + 0.0148], [xa, yc + dy, zc + 0.0008], 0.0006, 8))
        q.add(mat, trimesh.creation.icosphere(2, 0.0011).apply_translation([xa, yc + dy, zc]))
    for (x, y) in ((0.012, 0.1), (0.012, 0.13)): q.add('aco_inox', cil_z(0.0022, z0 + 0.005, z0 + 0.0062, x, y, 12))
    A.encaixe('olho', (AX_PUXADA - 0.07, yc, zc), 'mira', descricao='olho na âncora: pino de cima (verde) = 10 m, do meio = 20 m, de baixo = 30 m')
    A.pivo = (0.012, 0.115, 0.0136)


def _estab(A, L):
    q = A.base; x0, y = 0.044, -0.09
    q.add('latao', torno_x([(0.003, x0 - 0.004), (0.003, x0 + 0.002)], 16, y))
    q.add('borracha', torno_x([(0.0, x0), (0.009, x0), (0.0105, x0 + 0.004), (0.0105, x0 + 0.02), (0.0075, x0 + 0.026), (0.0, x0 + 0.026)], 28, y))   # amortecedor
    q.add('fibra_preta', cil_x(0.0065, x0 + 0.025, x0 + L - 0.03, y, 0, 24))
    q.add('aco_oxidado', torno_x([(0.0, x0 + L - 0.032), (0.012, x0 + L - 0.032), (0.0135, x0 + L - 0.028), (0.0135, x0 + L - 0.004), (0.011, x0 + L), (0.0, x0 + L)], 32, y))
    for xx in np.linspace(x0 + L - 0.026, x0 + L - 0.008, 4): q.add('aco_oxidado', tubo_x(0.0133, 0.0139, xx, xx + 0.0018, y, sec=32))
    A.pivo = (x0, y, 0)


@_acessorio('estabilizador_arco', 'Estabilizador longo (arco)', 'estabilizador', 'rosca_estabilizador', peso_kg=0.2, raridade='raro', valor_troca=25,
            modificadores={'precisao': 1.12, 'tremor': 0.75}, onde=['galeria', 'casa_de_campo'],
            descricao='Haste de fibra de 30 cm com amortecedor e peso na ponta: o arco treme menos segurando puxado e a mão sente menos o tiro.')
def estabilizador_arco(A): _estab(A, 0.3)


@_acessorio('estabilizador_curto_arco', 'Estabilizador curto (arco)', 'estabilizador', 'rosca_estabilizador', peso_kg=0.12, raridade='incomum', valor_troca=14,
            modificadores={'precisao': 1.05, 'tremor': 0.88}, onde=['galeria', 'casa_de_campo'],
            descricao='Versão de 12 cm: ajuda menos, mas não enrosca nos galhos nem nas portas.')
def estabilizador_curto_arco(A): _estab(A, 0.12)


@_acessorio('aljava_arco', 'Aljava de arco (4 flechas)', 'aljava', 'aljava_arco', peso_kg=0.25, raridade='incomum', valor_troca=18, leva=4, municao='flecha_caca',
            modificadores={'recarga_s': 0.8}, onde=['casa_de_campo', 'galeria', 'armazem'],
            descricao='Aljava presa no lado direito do arco: capuz de espuma que cobre as pontas em cima e garra de borracha embaixo. 4 flechas à mão.')
def aljava_arco(A):
    q = A.base; zq = 0.04; xs = [-0.012, -0.002, 0.008, 0.018]
    q.add('aluminio_preto', caixa(0.006, 0.018, -0.15, 0.2, 0.0132, 0.017))                                     # barra de montagem
    q.add('aluminio_preto', caixa(0.008, 0.016, -0.12, -0.105, 0.017, zq + 0.004))
    q.add('aluminio_preto', caixa(0.008, 0.016, 0.17, 0.185, 0.017, zq + 0.004))
    capuz = torno_x([(0.0, 0.0), (0.024, 0.0), (0.026, 0.01), (0.024, 0.05), (0.016, 0.07), (0.0, 0.074)], 32)
    capuz.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])); capuz.apply_scale([1.0, 1.0, 0.55])
    capuz.apply_translation([0.003, 0.31, zq]); q.add('polimero', capuz)                                     # capuz (cobre as pontas)
    q.add('espuma', inter([torno_x([(0.0, 0.0), (0.022, 0.0), (0.022, 0.012), (0.0, 0.012)], 32).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])).apply_scale([1, 1, 0.55]).apply_translation([0.003, 0.309, zq]), caixa(-1, 1, -1, 1, -1, 1)]))
    q.add('aluminio_preto', caixa(0.0, 0.008, 0.18, 0.33, zq + 0.01, zq + 0.014))
    q.add('borracha', solido(arred([(-0.02, -0.16), (0.026, -0.16), (0.026, -0.145), (-0.02, -0.145)], 0.003), zq - 0.008, zq + 0.008, 0.002))   # garra
    for x in xs:
        f = P(); _flecha(f, 'caca')
        T = TF.translation_matrix([x, -0.36, zq]) @ TF.rotation_matrix(math.pi / 2, [0, 0, 1])
        q.merge(f, T)
    A.pivo = (0.012, 0.025, 0.0132)
