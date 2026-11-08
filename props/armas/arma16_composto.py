# Arma 15: arco composto (punho de aluminio usinado e vazado, bracos divididos, polias excentricas, cabos com protetor deslizante,
# apoio que cai no disparo, visor na corda e laco D) com flechas de carbono, soltador de pulso, mira de 5 pinos com luz e aljava.
# Executado por gerar_armas.py depois de arma15_arco.py (usa _catmull, _fita, _haste, _espelha_y, _flecha). Desenho proprio.
# Plano de lado: x frente (para onde a flecha vai), y cima, z direita. A corda fica atras (x negativo).
# Cada metade da corda e cada cabo sao filhos do seu braco e giram em torno do eixo da polia (a linha continua tangente a polia);
# na puxada os bracos flexionam, as polias giram e as duas metades da corda se encontram no ponto de puxada.
CORES.update({'aluminio_titanio': (92, 94, 98), 'carbono': (34, 34, 38), 'corda_cabo': (64, 74, 52), 'corda_d': (196, 96, 24), 'vane_verde': (120, 196, 40),
              'feltro': (60, 58, 54)})
METAL.update({'aluminio_titanio': (0.85, 0.34), 'carbono': (0.1, 0.32), 'corda_cabo': (0.0, 0.85), 'corda_d': (0.0, 0.85), 'vane_verde': (0.0, 0.5),
              'feltro': (0.0, 0.98)})
EMISSIVOS.update({'pino_amarelo': (1.0, 0.85, 0.05), 'nock_luz': (1.0, 0.12, 0.04), 'luz_mira': (0.75, 0.9, 1.0)})

AX_C = -0.20                     # corda em repouso (altura de armado ~ 17 cm da garganta do punho)
AX_PUX_C = -0.64                 # ponto de puxada (laco D na ancora)
R_CORDA_P = 0.045                # raio da trilha da corda na polia
R_CABO_P = 0.026                 # raio do modulo dos cabos
C_POLIA = (-0.155, 0.385)        # eixo da polia de cima (a de baixo e espelhada em y)
PK = (0.07, 0.30)                # eixo do bolso do braco de cima
A_BRACO_C = 7.0                  # flexao de cada braco na puxada (graus)
G_POLIA = 150.0                  # giro de cada polia na puxada (graus, relativo ao braco)
P_GUIA = (-0.077, 0.07)          # deslizador do protetor de cabos (x, y)
Z_GUIA = 0.031                   # altura do trilho do protetor (lado direito, longe das penas)
L_FC = 0.74                      # flecha de carbono


def _rot2(p, c, graus):
    t = math.radians(graus); d = np.array(p, float) - np.array(c, float)
    return np.array(c, float) + np.array([d[0] * math.cos(t) - d[1] * math.sin(t), d[0] * math.sin(t) + d[1] * math.cos(t)])


def _tangente(C, r, Pt, sinal):
    """Ponto onde a linha que vai ate Pt encosta no circulo (C, r). sinal = sentido em que a linha sai (produto vetorial)."""
    C = np.array(C, float); Pt = np.array(Pt, float); d = Pt - C; D = np.linalg.norm(d); b = math.atan2(d[1], d[0]); a = math.acos(r / D)
    for t in (b + a, b - a):
        T = C + r * np.array([math.cos(t), math.sin(t)]); u = T - C; w = Pt - T
        if (u[0] * w[1] - u[1] * w[0]) * sinal > 0: return T
    return C + r * np.array([math.cos(b + a), math.sin(b + a)])


def _ang(v): return math.degrees(math.atan2(v[1], v[0]))


def _linha(C, r, P0, Pd, sy, sinal, phi):
    """Metade de corda/cabo filha do braco (que gira phi no bolso), girando em torno do eixo da polia.
    Devolve (T0, P0, giro local em graus, comprimento puxado)."""
    pk = np.array([PK[0], sy * PK[1]]); C0 = np.array(C, float); Cd = _rot2(C0, pk, phi)
    T0 = _tangente(C0, r, P0, sinal); Td = _tangente(Cd, r, Pd, sinal)
    a0 = _ang(np.array(P0) - T0); ad = _ang(np.array(Pd) - Td); g = (ad - a0 + 180) % 360 - 180
    return T0, np.array(P0, float), g - phi, float(np.linalg.norm(np.array(Pd) - Td)), Td


C_POLIA_B = (C_POLIA[0], -C_POLIA[1])
NOCK0 = (AX_C, AY_FLECHA); NOCKD = (AX_PUX_C, AY_FLECHA)
T_CC, _, G_CC, LD_CC, TD_CC = _linha(C_POLIA, R_CORDA_P, NOCK0, NOCKD, 1, 1, A_BRACO_C)
T_CB, _, G_CB, LD_CB, TD_CB = _linha(C_POLIA_B, R_CORDA_P, NOCK0, NOCKD, -1, -1, -A_BRACO_C)
T_KC, _, G_KC, LD_KC, _ = _linha(C_POLIA, R_CABO_P, P_GUIA, P_GUIA, 1, -1, A_BRACO_C)
T_KB, _, G_KB, LD_KB, _ = _linha(C_POLIA_B, R_CABO_P, P_GUIA, P_GUIA, -1, 1, -A_BRACO_C)
_U = (TD_CC - np.array(NOCKD)) / np.linalg.norm(TD_CC - np.array(NOCKD))       # direcao da corda de cima, puxada
S_VISOR = 0.072 / _U[1]                                                        # visor a 7,2 cm acima da flecha com o arco puxado
VISOR0 = np.array([AX_C, AY_FLECHA + S_VISOR]); VISORD = np.array(NOCKD) + S_VISOR * _U
G_VISOR = _ang(_U) - 90.0
OLHO_C = (round(float(VISORD[0]) - 0.03, 4), AY_FLECHA + 0.072, 0.0)


def _no_braco(m, sy=1):
    """Malha feita no referencial do braco de cima (u do bolso para a polia, v normal para fora, z igual) -> plano.
    sy = -1 leva para o braco de baixo (espelho em y)."""
    M = TF.translation_matrix([PK[0], PK[1], 0]) @ TF.rotation_matrix(math.radians(ANG_BRACO), [0, 0, 1]) @ np.diag([1.0, -1.0, 1.0, 1.0])
    m.apply_transform(M); m.invert()
    if sy < 0: m.apply_transform(np.diag([1.0, -1.0, 1.0, 1.0])); m.invert()
    return m


ANG_BRACO = _ang(np.array(C_POLIA) - np.array(PK))           # direcao do braco de cima (do bolso para a polia)
L_BRACO = float(np.linalg.norm(np.array(C_POLIA) - np.array(PK)))


# ---------------------------------------------------------------------------- punho (riser) usinado
LINHA_PUNHO = [(0.086, 0.283), (0.08, 0.24), (0.064, 0.18), (0.047, 0.12), (0.035, 0.06), (0.031, 0.0), (0.035, -0.06), (0.047, -0.12),
               (0.064, -0.18), (0.08, -0.24), (0.086, -0.283)]
CONT_GRIP = suave([(0.016, 0.017), (0.016, -0.094), (-0.002, -0.096), (-0.013, -0.075), (-0.024, -0.042), (-0.032, -0.014), (-0.03, 0.004),
                   (-0.018, 0.014)], 3)


def _punho_composto(p):
    ln = LineString(_catmull(LINHA_PUNHO, 10))
    fora = ln.buffer(0.02, 32, cap_style=1)
    furos = []
    for s in (1, -1):                                                            # vazados (trelica) nos dois lados
        f1 = LineString(_catmull([(0.075, 0.262 * s), (0.064, 0.205 * s), (0.053, 0.16 * s)], 8)).buffer(0.0085, 16)
        f2 = LineString([(0.048, 0.132 * s), (0.04, 0.098 * s)]).buffer(0.0062, 16)
        furos += [f1, f2]
    furos.append(Point(0.041, -0.07).buffer(0.0055, 20))
    perfil = fora.difference(unary_union(furos))
    corpo = solido(perfil, -0.012, 0.012, 0.0022)
    janela = caixa(-0.1, 0.2, AY_FLECHA - 0.012, 0.168, -0.02, 0.0015)          # janela de mira (centro da flecha passa livre)
    corpo = menos(corpo, janela)
    p.add('aluminio_titanio', corpo)
    # frisos usinados no lado de fora e acabamento da janela
    for s in (1, -1):
        friso = LineString(_catmull([(0.083, 0.272 * s), (0.07, 0.215 * s), (0.057, 0.17 * s)], 8)).buffer(0.0125, 16).difference(
            LineString(_catmull([(0.083, 0.272 * s), (0.07, 0.215 * s), (0.057, 0.17 * s)], 8)).buffer(0.0098, 16))
        for z0, z1 in ((0.0115, 0.0128), (-0.0128, -0.0115)):
            p.add('aluminio_laranja', inter([solido(friso, z0, z1), solido(fora, -0.02, 0.02)]))
    # pegada (polimero) presa nas costas do punho
    grip = punho_redondo(CONT_GRIP, 0.017, -0.096, lambda y: 0.0132 - 0.0012 * GT.smooth(-0.02, 0.017, y), n=2.4, fatias=110, voltas=40,
                         raio_base=0.004, raio_topo=0.003)
    p.add('polimero_grip', menos(grip, caixa(0.0165, 0.1, -1, 1, -1, 1)))
    p.add('borracha', inter([punho_redondo(CONT_GRIP, 0.017, -0.096, lambda y: 0.0134, n=2.4, fatias=110, voltas=40, raio_base=0.004),
                             caixa(-0.1, 0.012, -0.086, -0.03, -1, 1)]))                      # faixa de borracha onde ficam os dedos
    for y in (-0.025, -0.07): p.add('aco_inox', cil_z(0.0022, 0.0125, 0.0138, 0.009, y, 12))
    # bolsos dos bracos (aluminio preto, com pino do eixo e parafuso de tensao)
    for s in (1, -1):
        pk = (PK[0], s * PK[1])
        bl = menos(caixa(-0.048, 0.022, -0.016, 0.004, -0.0215, 0.0215), caixa(-0.06, 0.03, -0.0085, 0.02, -0.0185, 0.0185))
        p.add('aluminio_preto', _no_braco(bl, s))
        p.add('aco_inox', cil_z(0.0032, -0.0235, 0.0235, pk[0], pk[1], 16))
        for z in (-0.0235, 0.0235): p.add('aluminio_preto', cil_z(0.0045, z - 0.0008 if z > 0 else z, z if z > 0 else z + 0.0008, pk[0], pk[1], 16))
        # parafuso de tensao do braco (cabeca acima do braco, perto da raiz)
        para = trimesh.creation.cylinder(radius=0.0042, height=0.03, sections=20); para.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0]))
        para.apply_translation([-0.036, 0.0, 0]); p.add('aco_inox', _no_braco(para, s))
        cab = trimesh.creation.cylinder(radius=0.0075, height=0.006, sections=24); cab.apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0]))
        cab.apply_translation([-0.036, 0.0125, 0]); p.add('aluminio_preto', _no_braco(cab, s))
    # protetor de cabos: suporte no lado direito + haste de fibra que vai para tras
    p.add('aluminio_preto', solido(arred([(0.004, 0.058), (0.036, 0.058), (0.036, 0.082), (0.004, 0.082)], 0.003), 0.012, 0.016, 0.0008))
    p.add('aluminio_preto', solido(arred([(0.0, 0.062), (0.016, 0.062), (0.016, 0.078), (0.0, 0.078)], 0.003), 0.015, Z_GUIA + 0.006, 0.0008))
    p.add('fibra_preta', cil_x(0.0036, -0.115, 0.008, P_GUIA[1], Z_GUIA, 20))
    p.add('borracha', cil_x(0.0045, -0.122, -0.113, P_GUIA[1], Z_GUIA, 20))
    # deslizador (rolete duplo) por onde passam os cabos
    gx = P_GUIA[0]
    p.add('polimero', solido(arred([(gx - 0.01, P_GUIA[1] - 0.026), (gx + 0.01, P_GUIA[1] - 0.026), (gx + 0.01, P_GUIA[1] + 0.026), (gx - 0.01, P_GUIA[1] + 0.026)], 0.005),
                             Z_GUIA - 0.0085, Z_GUIA + 0.0105, 0.0012))
    for dz in (-0.0025, 0.0045):
        for dy in (-0.017, 0.017):
            p.add('aco_inox', cil_z(0.0032, Z_GUIA + dz - 0.0018, Z_GUIA + dz + 0.0018, gx, P_GUIA[1] + dy, 16))
    # amortecedor de corda (haste de baixo, ponta de borracha logo na frente da corda)
    p.add('fibra_preta', cil_x(0.0034, AX_C + 0.03, 0.04, -0.13, 0.0, 16))
    p.add('borracha', torno_x([(0.0, AX_C + 0.012), (0.0075, AX_C + 0.012), (0.0095, AX_C + 0.016), (0.0095, AX_C + 0.028), (0.005, AX_C + 0.034), (0.0, AX_C + 0.034)], 24, -0.13))
    p.add('aluminio_preto', cil_x(0.0058, 0.03, 0.05, -0.13, 0.0, 20))
    # bucha do estabilizador (na frente, abaixo da mao) e buchas da mira / aljava
    p.add('aluminio_preto', torno_x([(0.0085, 0.05), (0.0085, 0.068), (0.0065, 0.0705)], 24, -0.1))
    p.add('latao', torno_x([(0.0045, 0.07), (0.0045, 0.071)], 16, -0.1))
    for (x, y) in ((0.056, 0.106), (0.06, 0.148)): p.add('latao', cil_z(0.0028, 0.0118, 0.0128, x, y, 14))
    for (x, y) in ((0.06, -0.112), (0.062, -0.15)): p.add('latao', cil_z(0.0028, 0.0118, 0.0128, x, y, 14))
    # apoio de flecha que cai: corpo preso no lado direito, atras do punho
    ya = AY_FLECHA
    p.add('aluminio_preto', solido(arred([(-0.056, ya - 0.036), (-0.034, ya - 0.036), (-0.034, ya - 0.006), (-0.056, ya - 0.006)], 0.004), 0.003, 0.017, 0.0012))
    p.add('aluminio_preto', solido(arred([(-0.04, ya - 0.012), (0.026, ya - 0.012), (0.026, ya - 0.005), (-0.04, ya - 0.005)], 0.002), 0.012, 0.017, 0.0006))
    p.add('aluminio_laranja', cil_z(0.0052, 0.017, 0.019, -0.046, ya - 0.026, 20))                 # botao de ajuste
    p.add('aco_inox', cil_z(0.0017, 0.0005, 0.003, -0.04, ya - 0.02, 12))


def _braco_c(q, cima=True):
    """Braco dividido: duas laminas de fibra (uma de cada lado da polia), eixo de aco, pontas usinadas e amortecedores."""
    pts = _catmull([(-0.05, 0.0), (0.0, 0.0), (0.09, 0.005), (0.18, 0.004), (L_BRACO + 0.012, 0.0)], 10)
    for z in (-0.0125, 0.0125):
        m = _fita(pts, lambda s: 0.0055, lambda s: 0.0058 - 0.0016 * s, 0.3); m.apply_translation([0, 0, z])
        q.add('fibra_preta', _no_braco(m))
        mm = _fita(pts[6:-14], lambda s: 0.0056, lambda s: 0.0049 - 0.0013 * s, 0.3); mm.apply_translation([0, 0, z])     # faixa decorativa
        q.add('carbono', _no_braco(inter([mm, caixa(-1, 1, 0.0015, 1, -1, 1)])))
        # ponta usinada (casquilho do eixo)
        pt = solido(arred([(L_BRACO - 0.022, -0.0068), (L_BRACO + 0.013, -0.0068), (L_BRACO + 0.013, 0.0068), (L_BRACO - 0.022, 0.0068)], 0.004),
                    z - 0.006, z + 0.006, 0.0012)
        q.add('aluminio_preto', _no_braco(pt))
        # amortecedor de borracha no meio do braco
        amo = solido(arred([(0.085, 0.004), (0.12, 0.0045), (0.115, 0.012), (0.09, 0.011)], 0.002), z - 0.004, z + 0.004, 0.001)
        q.add('borracha', _no_braco(amo))
    q.add('aco_inox', cil_z(0.0034, -0.0198, 0.0198, C_POLIA[0], C_POLIA[1], 18))
    for z in (-0.0198, 0.0198): q.add('aluminio_preto', cil_z(0.0048, z - 0.0012 if z > 0 else z, z if z > 0 else z + 0.0012, C_POLIA[0], C_POLIA[1], 18))
    if not cima: _espelha_y(q)


def _polia(q, cima=True):
    """Polia excentrica: trilha da corda (raio 4,5 cm), modulo dos cabos dos dois lados, vazados e pino de parada."""
    cx, cy = C_POLIA
    lobo = unary_union([Point(cx, cy).buffer(R_CORDA_P + 0.0018, 48), Point(cx + 0.014, cy - 0.012).buffer(0.04, 48)])
    vaz = []
    for k in range(5):                                                                        # raios usinados (5 rasgos em arco)
        a0 = math.radians(k * 72 + 20); arc = [(cx + 0.031 * math.cos(a0 + t), cy + 0.031 * math.sin(a0 + t)) for t in np.linspace(-0.36, 0.36, 9)]
        vaz.append(LineString(arc).buffer(0.0052, 12))
    vaz.append(Point(cx + 0.03, cy - 0.034).buffer(0.0055, 20))
    vaz = unary_union(vaz)
    placa = solido(lobo.difference(vaz), -0.0042, 0.0042, 0.0009)
    placa = menos(placa, menos(cil_z(R_CORDA_P + 0.004, -0.0011, 0.0011, cx, cy, 64), cil_z(R_CORDA_P - 0.0008, -0.002, 0.002, cx, cy, 64)))   # canaleta
    q.add('aluminio_preto', placa)
    for z0, z1 in ((0.0042, 0.0064), (-0.0064, -0.0042)):
        md = Point(cx, cy).buffer(R_CABO_P + 0.0015, 40).union(Point(cx - 0.008, cy + 0.01).buffer(0.019, 32)).difference(
            unary_union([Point(cx + 0.014 * math.cos(math.radians(a)), cy + 0.014 * math.sin(math.radians(a))).buffer(0.0042, 16) for a in (30, 150, 270)]))
        m = solido(md, z0, z1, 0.0006)
        zc = (z0 + z1) / 2
        m = menos(m, menos(cil_z(R_CABO_P + 0.004, zc - 0.0005, zc + 0.0005, cx, cy, 48), cil_z(R_CABO_P - 0.0006, zc - 0.001, zc + 0.001, cx, cy, 48)))
        q.add('aluminio_laranja', m)
    q.add('aluminio_preto', cil_z(0.0062, -0.0071, 0.0071, cx, cy, 24))                      # cubo com rolamento
    q.add('aco_inox', cil_z(0.0016, -0.0074, 0.0074, cx + 0.03, cy - 0.03, 10))              # pino de parada da puxada
    q.add('borracha', cil_z(0.0028, 0.0042, 0.0072, cx + 0.03, cy - 0.03, 14))
    for a in range(0, 360, 60):                                                               # parafusos do modulo
        x, y = cx + 0.016 * math.cos(math.radians(a)), cy + 0.016 * math.sin(math.radians(a))
        for z in (0.0064, -0.0064): q.add('aco_inox', cil_z(0.0011, z - 0.0004 if z > 0 else z, z if z > 0 else z + 0.0004, x, y, 8))
    if not cima: _espelha_y(q)


def _arco_no_circulo(C, r, t0, t1, z, raio, n=14):
    """Pedaco de corda enrolado na polia (de t0 a t1 graus)."""
    ts = np.radians(np.linspace(t0, t1, n)); pts = [np.array([C[0] + r * math.cos(t), C[1] + r * math.sin(t), z]) for t in ts]
    return [_haste(pts[i], pts[i + 1], raio, 8) for i in range(n - 1)]


def _corda_c(q, cima=True):
    """Metade da corda: enrolada na trilha, desce reto ate o ponto de encaixe. O prolongamento (mais fino) fica escondido dentro
    da outra metade com o arco em repouso e e o que cobre a distancia maior com o arco puxado."""
    C = C_POLIA if cima else C_POLIA_B; T = T_CC if cima else T_CB; LD = LD_CC if cima else LD_CB
    n0 = np.array(NOCK0); d = (n0 - T) / np.linalg.norm(n0 - T); L0 = float(np.linalg.norm(n0 - T))
    p0 = np.r_[T, 0.0]; p1 = np.r_[n0, 0.0]; p2 = np.r_[T + d * (LD + 0.004), 0.0]
    q.add('corda_arco', _haste(p0, p1, 0.00135, 10))
    q.add('corda_arco', _haste(p1, p2, 0.0010, 8))
    tT = _ang(T - np.array(C))
    for m in _arco_no_circulo(C, R_CORDA_P - 0.0002, tT - 120 if cima else tT + 120, tT, 0.0, 0.00135): q.add('corda_arco', m)
    q.add('polimero', _haste(p0 + np.r_[d * 0.0, 0.0], p0 + np.r_[d * 0.05, 0.0], 0.0017, 10))          # reforco na saida da polia
    q.add('polimero', _haste(p1 - np.r_[d * 0.06, 0.0], p1, 0.0017, 10))                              # reforco central
    # silenciador de borracha (fios) a 1/3 da corda
    pm = p0 + np.r_[d * (L0 * 0.36), 0.0]
    for k in range(6):
        a = k * math.pi / 3; v = np.array([math.cos(a) * 0.007, 0.0, math.sin(a) * 0.007])
        q.add('borracha', _haste(pm, pm + v + np.r_[d * 0.003, 0.0], 0.0009, 6))


def _cabo(q, cima=True):
    """Duas pernas de cabo saindo do modulo da polia ate o deslizador do protetor (lado direito)."""
    C = C_POLIA if cima else C_POLIA_B; T = T_KC if cima else T_KB
    for zc, zg in ((0.0053, Z_GUIA - 0.0025), (-0.0053, Z_GUIA + 0.0045)):
        p0 = np.r_[T, zc]; p1 = np.r_[P_GUIA, zg]
        q.add('corda_cabo', _haste(p0, p1, 0.0012, 8))
        q.add('polimero', _haste(p0 + (p1 - p0) * 0.02, p0 + (p1 - p0) * 0.2, 0.0015, 8))            # reforco
        tT = _ang(T - np.array(C))
        for m in _arco_no_circulo(C, R_CABO_P - 0.0003, tT, tT + 110 if cima else tT - 110, zc, 0.0012, 10): q.add('corda_cabo', m)


def _laco_d(q):
    x, y = NOCK0
    pts = _catmull([(x, y + 0.0078), (x - 0.007, y + 0.0074), (x - 0.0135, y + 0.003), (x - 0.0135, y - 0.003), (x - 0.007, y - 0.0074), (x, y - 0.0078)], 8)
    for i in range(len(pts) - 1): q.add('corda_d', _haste(np.r_[pts[i], 0.0], np.r_[pts[i + 1], 0.0], 0.0014, 8))
    for dy in (0.0078, -0.0078):
        q.add('corda_d', trimesh.creation.icosphere(1, 0.0026).apply_scale([1.0, 0.7, 1.0]).apply_translation([x, y + dy, 0]))   # nos
    q.add('latao', _haste([x, y + 0.0045, 0], [x, y + 0.0058, 0], 0.0021, 12))                                                # anel de encaixe


def _visor(q):
    """Visor de corda (peep): disco com furo; ja inclinado para ficar de frente para o olho com o arco puxado."""
    m = P()
    m.add('aluminio_laranja', menos(torno_x([(0.0, -0.002), (0.0052, -0.002), (0.006, -0.001), (0.006, 0.001), (0.0052, 0.002), (0.0, 0.002)], 28),
                                    cil_x(0.0017, -0.01, 0.01, 0, 0, 16), caixa(-0.01, 0.01, -0.01, 0.01, -0.0016, -0.0007), caixa(-0.01, 0.01, -0.01, 0.01, 0.0007, 0.0016)))
    m.add('aluminio_preto', tubo_x(0.0017, 0.0022, -0.0022, 0.0022, sec=16))
    T = TF.translation_matrix([VISOR0[0], VISOR0[1], 0]) @ TF.rotation_matrix(math.radians(-G_VISOR), [0, 0, 1])
    q.merge(m, T)


def _apoio(q):
    ya = AY_FLECHA; px, py = -0.04, ya - 0.02
    q.add('aluminio_preto', cil_z(0.0024, 0.0, 0.0035, px, py, 14))
    braco = solido(arred([(px - 0.003, py - 0.003), (px + 0.004, py - 0.004), (-0.014, ya - 0.0075), (-0.019, ya - 0.0045)], 0.0015), -0.0013, 0.0013, 0.0004)
    q.add('aluminio_preto', braco)
    for s in (1, -1):                                                                          # forquilha com feltro
        g = solido(arred([(-0.021, ya - 0.0075), (-0.013, ya - 0.0075), (-0.013, ya - 0.0005), (-0.016, ya + 0.0005)], 0.0008), 0.0, 0.0012)
        g.apply_transform(TF.rotation_matrix(math.radians(28 * s), [1, 0, 0], [0, ya - 0.0075, 0])); q.add('feltro', g)


def _flecha_c(q, cor='vane_verde', luz=True, ponta='caca'):
    """Flecha de carbono deitada em x: entalhe (nock luminoso) em x = 0, ponta em L_FC."""
    r = 0.0031; L = L_FC
    q.add('carbono', cil_x(r, 0.009, L - 0.012, sec=16))
    q.add('nock_luz' if luz else 'plastico_branco', menos(torno_x([(0.0, 0.0), (0.0034, 0.0), (0.0034, 0.009), (r, 0.013)], 16), caixa(-0.001, 0.0042, -0.0012, 0.0012, -0.01, 0.01)))
    q.add('plastico_branco', tubo_x(r, r + 0.00018, 0.013, 0.105, sec=16))                          # adesivo (wrap)
    for i in range(3):
        v = solido(arred([(0.03, 0.0), (0.074, 0.0), (0.072, 0.0055), (0.06, 0.0088), (0.044, 0.0078)], 0.0025), -0.00035, 0.00035)
        v.apply_translation([0, r - 0.0004, 0]); v.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 3, [1, 0, 0]))
        q.add('tinta_laranja' if i == 0 else cor, v)
    q.add('aluminio_preto', tubo_x(r - 0.0002, r + 0.0003, L - 0.016, L - 0.01, sec=16))           # inserto
    if ponta == 'caca':
        q.add('aco_inox', torno_x([(r + 0.0003, L - 0.011), (0.0038, L - 0.006), (0.0034, L + 0.012), (0.0, L + 0.026)], 16))
        for i in range(3):
            lam = solido(Polygon([(L - 0.004, 0.0), (L + 0.024, 0.0), (L + 0.002, 0.0118), (L - 0.004, 0.0104)]), -0.00035, 0.00035)
            lam.apply_transform(TF.rotation_matrix(i * 2 * math.pi / 3 + math.pi / 6, [1, 0, 0])); q.add('aco_inox', lam)
        q.add('aluminio_preto', torno_x([(0.0, L - 0.008), (0.0046, L - 0.008), (0.0046, L - 0.003), (0.0, L - 0.003)], 16))   # anel de trava
    else:
        q.add('aco_inox', torno_x([(r + 0.0003, L - 0.011), (0.0036, L - 0.006), (0.0036, L + 0.006), (0.0, L + 0.016)], 16))


# ---------------------------------------------------------------------------- o arco composto
def _composto(A):
    A.pivo = (-0.014, -0.03, 0.0)
    _punho_composto(A.base)
    bc = A.parte('braco_cima', (PK[0], PK[1], 0), explodir=(0, 0.1, 0), tipo='gira', eixo='z', curso_graus=A_BRACO_C,
                 descricao='braço de cima (duas lâminas): flexiona para baixo na puxada')
    _braco_c(bc, True)
    bb = A.parte('braco_baixo', (PK[0], -PK[1], 0), explodir=(0, -0.1, 0), tipo='gira', eixo='z', curso_graus=-A_BRACO_C, descricao='braço de baixo: espelho do de cima')
    _braco_c(bb, False)
    pc = A.parte('polia_cima', (C_POLIA[0], C_POLIA[1], 0), pai='braco_cima', explodir=(-0.04, 0.05, 0), tipo='gira', eixo='z', curso_graus=G_POLIA,
                 descricao='polia excêntrica de cima: gira 150° na puxada (a corda desenrola, os cabos enrolam)')
    _polia(pc, True)
    pb = A.parte('polia_baixo', (C_POLIA_B[0], C_POLIA_B[1], 0), pai='braco_baixo', explodir=(-0.04, -0.05, 0), tipo='gira', eixo='z', curso_graus=-G_POLIA,
                 descricao='polia de baixo: espelho da de cima')
    _polia(pb, False)
    cc = A.parte('corda_cima', (C_POLIA[0], C_POLIA[1], 0), pai='braco_cima', explodir=(-0.06, 0, 0), tipo='gira', eixo='z', curso_graus=G_CC,
                 descricao='metade de cima da corda (gira no eixo da polia, sempre tangente a ela)')
    _corda_c(cc, True)
    cb = A.parte('corda_baixo', (C_POLIA_B[0], C_POLIA_B[1], 0), pai='braco_baixo', explodir=(-0.06, 0, 0), tipo='gira', eixo='z', curso_graus=G_CB,
                 descricao='metade de baixo da corda')
    _corda_c(cb, False)
    kc = A.parte('cabo_cima', (C_POLIA[0], C_POLIA[1], 0), pai='braco_cima', explodir=(0, 0, 0.05), tipo='gira', eixo='z', curso_graus=G_KC,
                 descricao='cabos de cima: do módulo da polia até o deslizador do protetor')
    _cabo(kc, True)
    kb = A.parte('cabo_baixo', (C_POLIA_B[0], C_POLIA_B[1], 0), pai='braco_baixo', explodir=(0, 0, 0.05), tipo='gira', eixo='z', curso_graus=G_KB,
                 descricao='cabos de baixo')
    _cabo(kb, False)
    ld = A.parte('laco_d', (NOCK0[0], NOCK0[1], 0), explodir=(-0.04, 0, 0), tipo='desliza', eixo='x', curso_m=AX_PUX_C - AX_C,
                 descricao='laço D na corda (onde o soltador engata): vai até a âncora na puxada')
    _laco_d(ld)
    vs = A.parte('visor_corda', (VISOR0[0], VISOR0[1], 0), explodir=(-0.04, 0.03, 0), tipo='desliza', eixo='x', curso_m=AX_PUX_C - AX_C,
                 descricao='visor preso entre os fios da corda: com o arco puxado fica na frente do olho')
    _visor(vs)
    ap = A.parte('apoio', (-0.04, AY_FLECHA - 0.02, 0), explodir=(0, -0.03, -0.04), tipo='gira', eixo='z', curso_graus=-45,
                 descricao='apoio de flecha que cai: segura a flecha na puxada e cai no disparo para as penas passarem livres')
    _apoio(ap)
    fl = A.parte('flecha', (AX_C, AY_FLECHA, 0), explodir=(0.0, 0.03, -0.05), tipo='remove', direcao=[0.0, 0.0, -1.0], municao='flecha_carbono',
                 capacidade=1, descricao='flecha encaixada na corda (embaixo do laço D) e deitada no apoio')
    _flecha_c(fl)
    for ms in fl.parts.values():
        for m in ms: m.apply_translation([AX_C, AY_FLECHA, 0])
    A.encaixe('encaixe_flecha', (AX_C, AY_FLECHA, 0), 'flecha', pai='flecha', substitui='flecha',
              aceita=['flecha_carbono', 'flecha_carbono_campo', 'flecha_caca', 'flecha_prego', 'flecha_campo'],
              descricao='filho do nó flecha: a flecha escolhida troca a malha do nó flecha (anda na puxada)')
    A.encaixe('encaixe_soltador', (AX_C - 0.0125, AY_FLECHA, 0), 'loop_d', pai='laco_d', aceita=['soltador_pulso'], padrao='soltador_pulso',
              descricao='filho do laço D: o soltador engata atrás da corda e anda junto na puxada')
    A.encaixe('encaixe_mira', (0.058, 0.127, 0.0128), 'rosca_mira_composto', explodir=(0, 0, 0.06), aceita=['mira_pinos_luz'], padrao='mira_pinos_luz',
              descricao='duas buchas no lado direito, acima da janela')
    A.encaixe('encaixe_estabilizador', (0.071, -0.1, 0), 'rosca_estabilizador', explodir=(0.08, 0, 0), aceita=['estabilizador_arco', 'estabilizador_curto_arco'],
              descricao='bucha na frente do punho, abaixo da mão (mesmos estabilizadores do arco recurvo)')
    A.encaixe('encaixe_aljava', (0.061, -0.131, 0.0128), 'aljava_composto', explodir=(0, 0, 0.08), aceita=['aljava_composto'],
              descricao='duas buchas do lado direito, abaixo da mão: aljava de 5 flechas')
    A.encaixe('mira_ferro', OLHO_C, 'mira', descricao='olho do arqueiro com o arco puxado, atrás do visor da corda: alinhe o visor com o aro da mira')
    A.encaixe('boca_fogo', (AX_PUX_C + L_FC, AY_FLECHA, 0), 'efeito', descricao='de onde a flecha sai no "soltar" (projétil para -Z, quase sem ruído)')
    # ---- animacoes
    def cur(ks, valor): return [(t, a * valor) for t, a in ks]
    def tudo(ks):
        """ks = [(t, fracao da puxada)]: todas as partes da puxada juntas."""
        D = AX_PUX_C - AX_C; dv = VISORD - VISOR0
        return [('braco_cima', 'r', (0, 0, 1), pose(cur(ks, A_BRACO_C))), ('braco_baixo', 'r', (0, 0, 1), pose(cur(ks, -A_BRACO_C))),
                ('polia_cima', 'r', (0, 0, 1), pose(cur(ks, G_POLIA))), ('polia_baixo', 'r', (0, 0, 1), pose(cur(ks, -G_POLIA))),
                ('corda_cima', 'r', (0, 0, 1), pose(cur(ks, G_CC))), ('corda_baixo', 'r', (0, 0, 1), pose(cur(ks, G_CB))),
                ('cabo_cima', 'r', (0, 0, 1), pose(cur(ks, G_KC))), ('cabo_baixo', 'r', (0, 0, 1), pose(cur(ks, G_KB))),
                ('laco_d', 't', pose([(t, (f * D, 0, 0)) for t, f in ks])),
                ('visor_corda', 't', pose([(t, (f * dv[0], f * dv[1], 0)) for t, f in ks])), ('visor_corda', 'r', (0, 0, 1), pose(cur(ks, G_VISOR)))]
    def flecha(ks): return ('flecha', 't', pose([(t, (f * (AX_PUX_C - AX_C), 0, 0)) for t, f in ks]))
    pux = [(0, 0), (0.15, 0), (0.45, 0.55), (0.75, 0.93), (0.9, 1.0), (1.0, 1.0)]       # pico de forca no meio e o alivio (let-off) no fim
    A.anim('puxar', 1.0, tudo(pux) + [flecha(pux), (None, 'r', (0, 0, 1), pose([(0, 0), (0.45, 2.5), (1.0, 0)]))],
           desc='puxa até a âncora (0,9 s): as polias giram, a força cai no fim (alívio de 80%) e o arco fica leve de segurar')
    seg = [(0, 1.0), (0.75, 0.995), (1.5, 1.0)]
    A.anim('segurar', 1.5, tudo(seg) + [flecha(seg)], laco=True, desc='segurando puxado: com o alívio das polias treme bem menos que o recurvo')
    sol = [(0, 1.0), (0.025, 0.0), (0.06, -0.025), (0.1, 0.012), (0.16, -0.005), (0.24, 0.0)]
    A.anim('soltar', 0.45, tudo(sol) + [('flecha', 't', pose([(0, (AX_PUX_C - AX_C, 0, 0)), (0.025, (0, 0, 0)), (0.05, (0.9, 0, 0)), (0.45, (0.9, 0, 0))])),
                                        ('apoio', 'r', (0, 0, 1), pose([(0, 0), (0.02, 0), (0.05, -45), (0.3, -45), (0.42, 0)])),
                                        (None, 'r', (0, 0, 1), pose([(0, 0), (0.03, -1.5), (0.18, 0)])), (None, 't', pose([(0, (0, 0, 0)), (0.03, (0.006, 0, 0)), (0.2, (0, 0, 0))]))],
           desc='solta: a corda volta, o apoio cai e o arco pula um pouco para a frente; esconda o nó flecha aos 0,025 s e lance o projétil em boca_fogo')
    A.anim('encaixar', 1.3, [('flecha', 't', pose([(0, (0.1, -0.33, 0.12)), (0.35, (0.1, -0.33, 0.12)), (0.75, (0.14, -0.04, 0.03)), (1.05, (0.012, 0.0, 0.0)),
                                                   (1.2, (0, 0, 0))])), (None, 'r', (1, 0, 0), pose([(0, 0), (0.3, -15), (1.0, -15), (1.3, 0)]))],
           desc='pega uma flecha da aljava, deita no apoio (0,75 s) e encaixa a nock na corda embaixo do laço D (1,2 s); mostre o nó flecha aos 0,35 s')
    A.anim('inspecionar', 2.6, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.5, 55), (1.2, 55), (1.7, -45), (2.2, -45), (2.6, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.5, 12), (2.2, 12), (2.6, 0)]))], desc='gira o arco para conferir polias, cabos e corda')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.8), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


@arma('arco_composto', 'Arco composto', 'armas', 'arco', classe='arco', calibre='flecha', municao='flecha_carbono', capacidade=1, dano=95,
      alcance_m=50, alcance_max_m=90, modo='um tiro (puxar, segurar e soltar)', tiros_por_s=0.55, recarga_s=1.3, recarga_vazia_s=1.3, precisao=0.85, recuo=0.04,
      ruido_m=5, durabilidade=1200, peso_kg=1.9, raridade='raro', valor_troca=90, flecha_volta=0.75, forca_lb=60, alivio=0.8,
      requer_conserto=['corda_arco', 'cabo'], onde=['galeria', 'casa_de_campo', 'armazem', 'loja_caca'],
      descricao='Arco de punho de alumínio usinado com polias excêntricas (60 lb, alívio de 80%): a flecha sai mais rápida e reta que no recurvo, '
                'e segurar puxado quase não cansa. Mira de pinos e visor na corda. Polias e cabos precisam de cuidado: corda gasta arrebenta.')
def arco_composto(A): _composto(A)


# ---------------------------------------------------------------------------- municao: flechas de carbono
for _id, _nome, _p, _luz, _dano, _desc in (
        ('flecha_carbono', 'Flecha de carbono (caça)', 'caca', True, 1.15, 'Haste de carbono com ponta de 3 lâminas e nock luminoso (acende no disparo: fácil de achar no mato).'),
        ('flecha_carbono_campo', 'Flecha de carbono (treino)', 'campo', False, 0.85, 'Ponta de campo simples: quase sempre volta inteira.')):
    REG[_id] = dict(id=_id, nome=_nome, grupo='municao', categoria='municao', calibre='flecha', peso_kg=0.028, empilha=24, multiplicador_dano=_dano,
                    raridade='incomum' if _luz else 'comum', onde=['galeria', 'casa_de_campo', 'armazem'], encaixe='flecha',
                    descricao=_desc + ' Serve nos dois arcos. Pivô no entalhe (ponto que encosta na corda).',
                    fn=(lambda p, l: (lambda A: (_flecha_c(A.base, 'vane_verde', l, p), setattr(A, 'pivo', (0, 0, 0)))))(_p, _luz))


# ---------------------------------------------------------------------------- acessorios
@_acessorio('soltador_pulso', 'Soltador de pulso', 'soltador', 'loop_d', peso_kg=0.09, raridade='incomum', valor_troca=20,
            modificadores={'precisao': 1.1, 'tremor': 0.9}, onde=['galeria', 'casa_de_campo'],
            descricao='Cabeça de garras com gatilho de dedo indicador e fita de pulso: engata no laço D, a puxada vem do braço e o disparo é limpo.')
def soltador_pulso(A):
    q = A.base; x0, y0 = AX_C - 0.0125, AY_FLECHA
    # garras (duas) que fecham no laco
    for s in (1, -1):
        g = solido(arred([(x0 + 0.004, y0 + s * 0.0005), (x0 - 0.004, y0 + s * 0.0005), (x0 - 0.012, y0 + s * 0.0055), (x0 - 0.004, y0 + s * 0.0075),
                          (x0 + 0.003, y0 + s * 0.004)], 0.001), -0.0022, 0.0022, 0.0005)
        q.add('aco_inox', g)
    q.add('aluminio_preto', torno_x([(0.0, x0 - 0.05), (0.0062, x0 - 0.05), (0.0075, x0 - 0.04), (0.0075, x0 - 0.016), (0.006, x0 - 0.01), (0.0, x0 - 0.01)], 24, y0))
    q.add('aluminio_laranja', tubo_x(0.0074, 0.0078, x0 - 0.036, x0 - 0.031, y0, sec=24))
    gat = solido(arred([(x0 - 0.032, y0 - 0.006), (x0 - 0.024, y0 - 0.006), (x0 - 0.021, y0 - 0.022), (x0 - 0.027, y0 - 0.024)], 0.0015), -0.0028, 0.0028, 0.0006)
    q.add('aco_inox', gat)                                                              # gatilho (dedo indicador)
    q.add('aluminio_preto', cil_x(0.0026, x0 - 0.1, x0 - 0.05, y0, 0, 14))            # haste ajustavel
    for xx in np.linspace(x0 - 0.095, x0 - 0.06, 6): q.add('aco_inox', tubo_x(0.0026, 0.0029, xx, xx + 0.002, y0, sec=14))
    fita = torno_x([(0.0, 0.0), (0.03, 0.0), (0.03, 0.03), (0.0, 0.03)], 40)          # fita de pulso (aro achatado aberto)
    aro = menos(fita, cil_x(0.028, -0.01, 0.04, 0, 0, 40), caixa(-1, 1, -1, -0.01, -1, 1))
    aro.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])); aro.apply_scale([1.0, 1.0, 0.8])
    aro.apply_translation([x0 - 0.13, y0 - 0.015, 0]); q.add('nylon', aro)
    q.add('nylon', caixa(x0 - 0.115, x0 - 0.095, y0 - 0.004, y0 + 0.004, -0.007, 0.007))
    q.add('aco_inox', caixa(x0 - 0.104, x0 - 0.098, y0 - 0.0045, y0 + 0.0045, -0.0075, 0.0075))
    A.pivo = (x0, y0, 0.0)


@_acessorio('mira_pinos_luz', 'Mira de 5 pinos com luz', 'mira', 'rosca_mira_composto', peso_kg=0.16, raridade='raro', valor_troca=40, usa='pilha_aa',
            modificadores={'precisao_mirando': 1.45}, onde=['galeria', 'casa_de_campo'], linha_de_visada='encaixe "olho": olhe pelo visor da corda e ponha o pino da distância no alvo',
            liga_desliga=True, descricao='Aro com 5 pinos de fibra (10, 20, 30, 40 e 50 m), luz que acende os pinos no escuro e nível de bolha embaixo para não entortar o arco.')
def mira_pinos_luz(A):
    q = A.base; z0 = 0.0128; xa = 0.142; yc = AY_FLECHA + 0.064; R = 0.0215
    q.add('aluminio_preto', solido(arred([(0.044, 0.097), (0.07, 0.097), (0.074, 0.158), (0.048, 0.158)], 0.004), z0, z0 + 0.005, 0.001))       # placa
    for (x, y) in ((0.056, 0.106), (0.06, 0.148)): q.add('aco_inox', cil_z(0.0022, z0 + 0.005, z0 + 0.0062, x, y, 12))
    q.add('aluminio_preto', solido(arred([(0.058, 0.112), (0.124, 0.112), (0.124, 0.126), (0.058, 0.126)], 0.002), z0 + 0.002, z0 + 0.0112, 0.0008))  # barra de cauda de andorinha
    for xx in np.linspace(0.064, 0.118, 10): q.add('tinta_branca', caixa(xx, xx + 0.0004, 0.1255, 0.1262, z0 + 0.004, z0 + 0.009))
    q.add('aluminio_preto', solido(arred([(0.11, 0.106), (0.13, 0.106), (0.13, 0.132), (0.11, 0.132)], 0.003), z0 - 0.001, z0 + 0.016, 0.001))   # carro de ajuste
    q.add('aluminio_laranja', cil_z(0.0058, z0 + 0.016, z0 + 0.024, 0.12, 0.119, 24))                                                        # botao de altura
    for a in range(0, 360, 30):
        x, y = 0.12 + 0.0058 * math.cos(math.radians(a)), 0.119 + 0.0058 * math.sin(math.radians(a))
        q.add('aluminio_laranja', cil_z(0.0007, z0 + 0.016, z0 + 0.024, x, y, 6))
    q.add('aluminio_preto', solido(arred([(0.126, yc - 0.006), (xa + 0.004, yc - 0.006), (xa + 0.004, 0.124), (0.126, 0.124)], 0.003), R - 0.002, z0 + 0.01, 0.0008))  # cotovelo
    aro = Point(0.0, 0.0).buffer(R, 48).difference(Point(0.0, 0.0).buffer(R - 0.003, 48))
    q.add('aluminio_preto', ext_x(affinity.translate(aro, 0.0, yc), xa - 0.008, xa + 0.008))
    q.add('tinta_branca', ext_x(affinity.translate(Point(0, 0).buffer(R - 0.0029, 48).difference(Point(0, 0).buffer(R - 0.0042, 48)), 0.0, yc), xa + 0.0075, xa + 0.008))
    q.add('lente_clara', ext_x(affinity.translate(Point(0, 0).buffer(R - 0.0028, 48), 0.0, yc), xa + 0.0068, xa + 0.0072))                    # lente de cobertura
    for i, (dy, mat) in enumerate(((0.008, 'pino_verde'), (0.004, 'pino_amarelo'), (0.0, 'pino_vermelho'), (-0.004, 'pino_verde'), (-0.008, 'pino_amarelo'))):
        zt = -0.0005 + 0.0003 * i; zb = R - 0.0028
        q.add('aluminio_preto', solido(arred([(xa - 0.003, yc + dy - 0.0009), (xa + 0.002, yc + dy - 0.0009), (xa + 0.002, yc + dy + 0.0009), (xa - 0.003, yc + dy + 0.0009)], 0.0004),
                                       zt + 0.002, zb, 0.0002))
        q.add(mat, _haste([xa, yc + dy, zt], [xa, yc + dy, zt + 0.0025], 0.0006, 8))
        q.add(mat, trimesh.creation.icosphere(2, 0.00095).apply_translation([xa, yc + dy, zt]))
        q.add(mat, _haste([xa - 0.002, yc + dy, zb], [xa - 0.002, yc + dy + 0.0004, R + 0.006], 0.0005, 6))                                 # fibra para fora
    for k in range(5):                                                                          # carretel de fibra do lado direito
        q.add('pino_verde' if k % 2 else 'pino_amarelo', trimesh.creation.torus(0.0048, 0.0005, major_sections=20, minor_sections=6).apply_transform(
            TF.translation_matrix([xa + 0.0, yc + 0.012, R + 0.0055 + 0.0011 * k]) @ TF.rotation_matrix(0.0, [1, 0, 0])))
    q.add('aluminio_preto', cil_z(0.0062, R - 0.001, R + 0.0055, xa, yc + 0.012, 24))
    q.add('aluminio_preto', cil_x(0.0042, xa - 0.006, xa + 0.008, yc + R + 0.0028, 0, 20))     # luz (pilha) em cima do aro
    q.add('luz_mira', cil_x(0.0029, xa + 0.008, xa + 0.0088, yc + R + 0.0028, 0, 16))
    q.add('aluminio_laranja', cil_z(0.0018, 0.0042, 0.0062, xa - 0.002, yc + R + 0.0028, 12))  # botao da luz
    q.add('lente_clara', cil_z(0.0018, -0.006, 0.006, xa, yc - R + 0.0042, 16))                 # nivel de bolha
    q.add('aluminio_preto', solido(arred([(xa - 0.004, yc - R - 0.002), (xa + 0.004, yc - R - 0.002), (xa + 0.004, yc - R + 0.0028), (xa - 0.004, yc - R + 0.0028)], 0.001), -0.008, 0.008))
    q.add('pino_verde', trimesh.creation.icosphere(1, 0.0011).apply_translation([xa, yc - R + 0.0042, 0.0012]))
    A.encaixe('olho', OLHO_C, 'mira', descricao='olho atrás do visor da corda: centralize o aro no visor; pino de cima 10 m ... de baixo 50 m')
    A.pivo = (0.058, 0.127, z0)


@_acessorio('aljava_composto', 'Aljava de arco composto (5 flechas)', 'aljava', 'aljava_composto', peso_kg=0.3, raridade='incomum', valor_troca=20, leva=5,
            municao='flecha_carbono', modificadores={'recarga_s': 0.8}, onde=['galeria', 'casa_de_campo', 'armazem'],
            descricao='Aljava de engate rápido no lado direito: capuz de espuma cobre as pontas em cima e a garra de borracha segura as hastes embaixo.')
def aljava_composto(A):
    q = A.base; z0 = 0.0128; zq = 0.05; xb = 0.057; xs = [xb - 0.022, xb - 0.011, xb, xb + 0.011, xb + 0.022]
    q.add('aluminio_preto', solido(arred([(0.046, -0.16), (0.072, -0.16), (0.07, -0.102), (0.048, -0.102)], 0.004), z0, z0 + 0.005, 0.001))   # placa no punho
    for (x, y) in ((0.06, -0.112), (0.062, -0.15)): q.add('aco_inox', cil_z(0.0022, z0 + 0.005, z0 + 0.0062, x, y, 12))
    q.add('aluminio_preto', solido(arred([(0.049, -0.146), (0.067, -0.146), (0.067, -0.118), (0.049, -0.118)], 0.004), z0 + 0.005, zq - 0.007, 0.001))
    q.add('aluminio_laranja', solido(arred([(0.067, -0.138), (0.082, -0.136), (0.082, -0.128), (0.067, -0.126)], 0.002), zq - 0.016, zq - 0.011, 0.0008))   # trava
    q.add('aluminio_preto', caixa(xb - 0.006, xb + 0.006, -0.25, 0.37, zq - 0.009, zq - 0.006))  # espinha
    capuz = torno_x([(0.0, 0.0), (0.03, 0.0), (0.032, 0.012), (0.03, 0.05), (0.02, 0.07), (0.0, 0.075)], 32)
    capuz.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])); capuz.apply_scale([1.25, 1.0, 0.45])
    capuz.apply_translation([xb, 0.33, zq]); q.add('polimero', capuz)
    esp = torno_x([(0.0, 0.0), (0.028, 0.0), (0.028, 0.014), (0.0, 0.014)], 32)
    esp.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])); esp.apply_scale([1.25, 1.0, 0.45]); esp.apply_translation([xb, 0.329, zq]); q.add('espuma', esp)
    q.add('borracha', solido(arred([(xb - 0.031, -0.2), (xb + 0.031, -0.2), (xb + 0.031, -0.182), (xb - 0.031, -0.182)], 0.004), zq - 0.009, zq + 0.009, 0.002))   # garra
    for i, x in enumerate(xs):
        f = P(); _flecha_c(f, 'vane_verde', True)
        q.merge(f, TF.translation_matrix([x, 0.37 - L_FC - 0.026, zq + (0.0035 if i % 2 else -0.0035)]) @ TF.rotation_matrix(math.pi / 2, [0, 0, 1]))
    A.pivo = (0.061, -0.131, z0)
