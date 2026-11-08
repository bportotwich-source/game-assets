# Arma 20: lanca improvisada (receita: cabo de vassoura + faca de cozinha + fita adesiva). A ponta do cabo e serrada ao meio,
# a espiga da faca (sem as talas) entra no corte e fica presa com prego, duas abracadeiras de mangueira, fita prata e arame.
# Executado por gerar_armas.py depois de arma20_machadinha.py. Desenho proprio, sem marca.
# Plano de lado: x frente (ponta da faca), y cima (fio da faca para baixo), z direita. Pivo na mao de tras.
CORES.update({'tinta_cabo': (64, 96, 118), 'aco_cozinha': (150, 152, 156), 'arame': (128, 130, 128), 'pano_xadrez': (120, 44, 40)})
METAL.update({'tinta_cabo': (0.0, 0.55), 'aco_cozinha': (0.85, 0.34), 'arame': (0.8, 0.45), 'pano_xadrez': (0.0, 0.9)})

LX0, LX1 = -0.448, 0.922          # cabo: rosca de tras ate a ponta serrada
LR = 0.0125                       # raio do cabo
XB, LB = 0.925, 0.2               # calcanhar da lamina e comprimento
Y_TIP = -0.016


def _tubo3d(pts, r, sec=8):
    """Tubo de raio r ao longo de uma curva 3D (quadros por transporte paralelo), com tampas."""
    P = np.asarray(pts, float); n = len(P)
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
    a = np.cross(T[0], [0, 1, 0] if abs(T[0][1]) < 0.9 else [1, 0, 0]); a /= np.linalg.norm(a); N = [a]
    for i in range(1, n):
        v = N[-1] - np.dot(N[-1], T[i]) * T[i]; N.append(v / np.linalg.norm(v))
    V = []
    for i in range(n):
        b = np.cross(T[i], N[i])
        for k in range(sec):
            t = 2 * math.pi * k / sec; V.append(P[i] + r * (math.cos(t) * N[i] + math.sin(t) * b))
    V += [P[0], P[-1]]; F = []
    for i in range(n - 1):
        for j in range(sec):
            a0 = i * sec + j; a1 = i * sec + (j + 1) % sec; F += [[a0, a1, a0 + sec], [a1, a1 + sec, a0 + sec]]
    c0, c1 = n * sec, n * sec + 1
    for j in range(sec): F += [[c0, (j + 1) % sec, j], [c1, (n - 1) * sec + j, (n - 1) * sec + (j + 1) % sec]]
    m = trimesh.Trimesh(np.array(V), np.array(F), process=True); trimesh.repair.fix_normals(m); return m


def _l_dorso(u):
    return 0.006 if u < 0.12 else 0.006 - (0.006 - Y_TIP) * ((u - 0.12) / 0.08) ** 1.8


def _l_fio(u):
    return -0.034 + 0.001 * u / 0.1 if u < 0.1 else -0.033 + (Y_TIP + 0.033) * ((u - 0.1) / 0.1) ** 2.2


def _l_secao(u, so_fio=False):
    ys, ye = _l_dorso(u), _l_fio(u); t = 0.0011 * (1 - 0.45 * u / LB); ym = (ys + ye) / 2
    if so_fio:
        h = min(0.004, (ys - ye) * 0.4); return [(0.00042, ye + h), (0.00009, ye - 0.00005), (-0.00009, ye - 0.00005), (-0.00042, ye + h)]
    pts = [(t, ys - 0.0004), (t, ys - 0.0025), (t * 0.8, ym), (0.00035, ye + 0.005), (0.00008, ye)]
    return [(z, y) for z, y in pts] + [(-z, y) for z, y in pts[::-1]] + [(-t * 0.6, ys), (t * 0.6, ys)]


def _anel_fita(x0, x1, r, mat, q, inc=(0.0, 0.0), esp=0.0004):
    m = tubo_x(r, r + esp, x0, x1, sec=28)
    xc = (x0 + x1) / 2
    m.apply_transform(TF.rotation_matrix(math.radians(inc[0]), [0, 1, 0], point=[xc, 0, 0]) @ TF.rotation_matrix(math.radians(inc[1]), [0, 0, 1], point=[xc, 0, 0]))
    q.add(mat, m)


def _faca_lanca(q):
    us = list(np.linspace(0.0, LB - 0.003, 60))
    sec = [(XB + u, _l_secao(u)) for u in us]
    ult = sec[-1][1]; cz = np.mean([p[0] for p in ult]); cy = np.mean([p[1] for p in ult])
    sec.append((XB + LB, [(cz + (z - cz) * 0.1, cy + (y - cy) * 0.1) for z, y in ult]))
    q.add('aco_cozinha', _loft_x(sec))
    q.add('aco_inox', _loft_x([(XB + u, _l_secao(u, True)) for u in np.linspace(0.004, LB - 0.012, 56)]))
    # reforco (bolster) e espiga com os furos dos rebites que sobraram
    q.add('aco_cozinha', solido(arred([(XB - 0.008, -0.012), (XB + 0.001, -0.034), (XB + 0.003, -0.034), (XB + 0.003, 0.0065), (XB - 0.008, 0.0065)], 0.0015),
                                -0.0034, 0.0034, 0.0008))
    esp = solido(arred([(0.81, -0.0085), (XB - 0.007, -0.0105), (XB - 0.007, 0.0055), (0.81, 0.0035)], 0.002), -0.0012, 0.0012)
    q.add('aco_cozinha', menos(esp, *[cil_z(0.0021, -0.01, 0.01, x, -0.002, 14) for x in (0.83, 0.876)]))


def _cabo_lanca(q):
    # miolo de madeira, rosca de plastico atras, tinta gasta por cima (lascas mostram a madeira) e corte serrado na ponta
    fenda = caixa(0.802, 1.0, -0.03, 0.03, -0.0016, 0.0016)
    furo_g = cil_z(0.0026, -0.02, 0.02, -0.405, 0.0, 16)
    miolo = torno_x([(0.0, -0.4205), (LR - 0.0004, -0.4205), (LR - 0.0004, 0.79), (LR, 0.795), (LR, LX1 - 0.004), (LR - 0.0012, LX1), (0.0, LX1)], 30)
    pregos = cil_z(0.0012, -0.02, 0.02, 0.876, -0.002, 10)
    q.add('madeira_clara', menos(miolo, fenda, furo_g, pregos))
    rng = np.random.default_rng(21)
    lascas = []
    for x in list(rng.uniform(-0.41, 0.78, 16)) + list(rng.uniform(-0.33, -0.16, 6)) + list(rng.uniform(0.7, 0.79, 6)):
        a = rng.uniform(0, 2 * math.pi); s = trimesh.creation.icosphere(1, radius=rng.uniform(0.0025, 0.006))
        s.apply_scale([rng.uniform(1.2, 2.6), 1, 1]); s.apply_translation([x, LR * math.cos(a), LR * math.sin(a)]); lascas.append(s)
    tinta = tubo_x(LR - 0.0004, LR, -0.42, 0.79, sec=30)
    q.add('tinta_cabo', menos(tinta, furo_g, *lascas))
    prof = [(0.0, LX0)]
    for k in range(8):                                                   # rosca de plastico (ponta da vassoura)
        x = LX0 + 0.003 + k * 0.0026; prof += [(0.0078, x), (0.0091, x + 0.0013)]
    prof += [(0.0078, -0.4255), (0.0095, -0.4245), (LR - 0.0006, -0.421), (LR - 0.0006, -0.4195), (0.0, -0.4195)]
    q.add('polimero_cinza', torno_x(prof, 24))
    # cordao no furo de pendurar
    th = np.linspace(0, 2 * math.pi, 40)
    laco = [(-0.405, -0.024 + 0.024 * math.cos(t), 0.024 * math.sin(t) * 0.8) for t in th]
    q.add('corda_cabo', _tubo3d(laco, 0.0016, 8))
    q.add('corda_cabo', trimesh.creation.icosphere(2, radius=0.0042).apply_scale([1, 1.2, 1]).apply_translation([-0.405, -0.049, 0]))
    for dz in (-0.004, 0.004):
        q.add('corda_cabo', _tubo3d([(-0.405, -0.051, dz * 0.5), (-0.403, -0.06, dz), (-0.401, -0.068, dz * 1.6)], 0.0015, 8))
    # empunhadura de tras: fita prata
    for k, x in enumerate(np.arange(-0.33, -0.17, 0.0165)):
        _anel_fita(x, x + 0.024, LR + 0.00005 + 0.0003 * (k % 2), 'fita_cinza', q, (rng.uniform(-3, 3), rng.uniform(-2, 2)))
    q.add('fita_cinza', solido(arred([(-0.178, LR - 0.002), (-0.158, LR - 0.003), (-0.152, LR - 0.0005), (-0.17, LR + 0.0006)], 0.001), -0.009, 0.009, 0.0002)
          .apply_transform(TF.rotation_matrix(0.25, [1, 0, 0], point=[0, 0, 0])))
    # empunhadura da frente: tira de pano (camisa velha) enrolada em espiral
    for k, x in enumerate(np.arange(0.12, 0.29, 0.0115)):
        _anel_fita(x, x + 0.016, LR + 0.0001, 'pano_xadrez', q, (0.0, 7.0), esp=0.0011)
    q.add('pano_xadrez', _tubo3d([(0.296, LR + 0.0008, 0.0), (0.305, LR - 0.003, 0.006), (0.312, LR - 0.012, 0.009), (0.316, LR - 0.024, 0.011)], 0.0017, 8)
          .apply_scale([1, 1, 1]))


def _amarracao(q):
    rng = np.random.default_rng(7)
    for x in np.arange(0.806, 0.848, 0.0075):                            # fita sobre a fenda (de tras)
        _anel_fita(x, x + 0.016, LR + 0.0001, 'fita_cinza', q, (rng.uniform(-6, 6), rng.uniform(-3, 3)))
    for x in np.arange(0.897, 0.917, 0.0065):                            # fita na boca do corte
        _anel_fita(x, x + 0.012, LR + 0.0001, 'fita_cinza', q, (rng.uniform(-6, 6), rng.uniform(-3, 3)))
    q.add('fita_cinza', solido(arred([(0.842, -LR - 0.012), (0.858, -LR - 0.014), (0.856, -LR + 0.0005), (0.845, -LR + 0.0005)], 0.0015), -0.0004, 0.0004)
          .apply_transform(TF.rotation_matrix(0.35, [0, 1, 0], point=[0.85, 0, 0])))      # ponta da fita descolando
    for xc in (0.862, 0.889):                                            # abracadeiras de mangueira
        q.add('aco_inox', tubo_x(LR + 0.0005, LR + 0.0012, xc - 0.0045, xc + 0.0045, sec=32))
        for i in range(5):
            a = 0.6 + i * 0.75
            q.add('aco_oxidado', caixa(xc - 0.0028, xc + 0.0028, -0.0004, 0.0004, -0.0004, 0.0004).apply_translation([0, 0, 0])
                  .apply_transform(TF.rotation_matrix(a, [1, 0, 0])).apply_translation([0, (LR + 0.0012) * math.cos(a), (LR + 0.0012) * math.sin(a)]))
        q.add('aco_inox', solido(arred([(xc - 0.0062, LR + 0.0006), (xc + 0.0062, LR + 0.0006), (xc + 0.0062, LR + 0.0062), (xc - 0.0062, LR + 0.0062)], 0.0012),
                                 -0.0052, 0.0052, 0.0005))
        q.add('aco_inox', trimesh.creation.cylinder(radius=0.0026, segment=[[xc, LR + 0.0042, -0.0075], [xc, LR + 0.0042, 0.0062]], sections=14))
        q.add('aco_inox', trimesh.creation.cylinder(radius=0.0041, segment=[[xc, LR + 0.0042, 0.0062], [xc, LR + 0.0042, 0.0092]], sections=6))
        q.add('aco_oxidado', caixa(xc - 0.0004, xc + 0.0004, LR + 0.0042 - 0.0026, LR + 0.0042 + 0.0026, 0.0089, 0.0094))
    # prego atravessando cabo e espiga, com a ponta entortada do outro lado
    q.add('aco_oxidado', cil_z(0.0012, -LR - 0.0016, LR + 0.0012, 0.876, -0.002, 10))
    q.add('aco_oxidado', cil_z(0.0032, LR + 0.0005, LR + 0.0013, 0.876, -0.002, 18))
    q.add('aco_oxidado', _tubo3d([(0.876, -0.002, -LR - 0.0012), (0.8765, -0.002, -LR - 0.0026), (0.879, -0.002, -LR - 0.0032), (0.888, -0.003, -LR - 0.0031)], 0.0011, 8))
    # arame enrolado por cima da fita, com o rabicho torcido
    t = np.linspace(0, 6 * 2 * math.pi, 300); rw = LR + 0.0012
    hel = np.stack([0.813 + 0.028 * t / t[-1], rw * np.cos(t), rw * np.sin(t)], 1)
    q.add('arame', _tubo3d(hel, 0.0007, 6))
    for s in (0, 1):
        tt = np.linspace(0, 1, 30)
        q.add('arame', _tubo3d([(0.8415 + 0.0008 * math.cos(9 * u * math.pi + s * math.pi), rw + 0.001 + 0.011 * u, 0.0008 * math.sin(9 * u * math.pi + s * math.pi) + 0.004 * u)
                                for u in tt], 0.0006, 6))


def _lanca(A):
    A.pivo = (-0.25, 0.0, 0.0)
    _cabo_lanca(A.base)
    am = A.parte('amarracao', (0.86, 0.0, 0.0), explodir=(0.0, 0.06, 0.0), tipo='remove', direcao=[0.0, 1.0, 0.0],
                 descricao='fita, arame, prego e abraçadeiras (a fita afrouxa com o uso: refaça com "refazer_fita"; tirar solta a faca)')
    _amarracao(am)
    fc = A.parte('faca', (XB, 0.0, 0.0), explodir=(0.12, 0.0, 0.0), tipo='remove', direcao=[1.0, 0.0, 0.0], item='faca_cozinha',
                 descricao='faca de cozinha sem as talas; a espiga fica dentro do corte do cabo. Troque quando quebrar (volta como sucata)')
    _faca_lanca(fc)
    A.encaixe('mao_frente', (0.2, 0.0, 0.0), 'mao', descricao='onde a mão da frente segura (pano enrolado); a de trás fica no pivô (fita)')
    A.encaixe('ponta', (XB + LB, Y_TIP, 0.0), 'efeito', descricao='ponta da faca (teste de acerto da estocada)')
    A.encaixe('fio_meio', (XB + 0.09, -0.033, 0.0), 'efeito', descricao='meio do fio (golpe de lado)')
    A.encaixe('cabo_tras', (LX0, 0.0, 0.0), 'efeito', descricao='ponta de trás do cabo (firmar no chão contra um avanço)')
    A.anim('estocar', 0.55, [(None, 't', pose([(0, (0, 0, 0)), (0.12, (-0.08, 0.0, 0)), (0.26, (0.32, 0.01, 0)), (0.36, (0.32, 0.01, 0)), (0.55, (0, 0, 0))])),
                             (None, 'r', (0, 0, 1), pose([(0, 0), (0.12, 2), (0.26, -2), (0.55, 0)]))],
           desc='estocada rápida com as duas mãos: acerto entre 0,2 e 0,3 s no encaixe ponta (a ~1,4 m do corpo)')
    A.anim('estocar_forte', 1.0, [(None, 't', pose([(0, (0, 0, 0)), (0.42, (-0.18, 0.02, 0)), (0.5, (-0.18, 0.02, 0)), (0.64, (0.45, 0.0, 0)), (0.78, (0.45, 0.0, 0)), (1.0, (0, 0, 0))])),
                                  (None, 'r', (0, 0, 1), pose([(0, 0), (0.42, 4), (0.64, -3), (1.0, 0)]))],
           desc='recolhe o corpo e enfia com tudo (atravessa e pode prender): acerto entre 0,56 e 0,7 s')
    A.anim('golpe_lateral', 0.8, [(None, 'r', (0, 1, 0), pose([(0, 0), (0.25, 35), (0.48, -40), (0.8, 0)])), (None, 'r', (1, 0, 0), pose([(0, 0), (0.25, 90), (0.6, 90), (0.8, 0)]))],
           desc='vira o fio para o lado e varre (corta, empurra e afasta dois zumbis de uma vez)')
    A.anim('empurrar', 0.6, [(None, 'r', (0, 1, 0), pose([(0, 0), (0.15, 75), (0.45, 75), (0.6, 0)])),
                             (None, 't', pose([(0, (0, 0, 0)), (0.15, (0.15, -0.05, 0.25)), (0.3, (0.32, -0.05, 0.25)), (0.45, (0.15, -0.05, 0.25)), (0.6, (0, 0, 0))]))],
           desc='segura o cabo atravessado na frente do peito e empurra (derruba quem chegou perto demais)')
    A.anim('firmar', 1.2, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 28), (1.2, 28)])), (None, 't', pose([(0, (0, 0, 0)), (0.4, (0.05, -0.32, 0)), (1.2, (0.05, -0.32, 0))]))],
           desc='apoia a ponta de trás no chão e aponta para cima: quem correr para cima se espeta (fica parado no fim)')
    A.anim('refazer_fita', 2.6, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 10), (2.2, 10), (2.6, 0)])), (None, 't', pose([(0, (0, 0, 0)), (0.4, (-0.55, -0.05, 0)), (2.2, (-0.55, -0.05, 0)), (2.6, (0, 0, 0))]))],
           desc='traz a ponta para perto e passa mais fita (gasta 1 fita adesiva e devolve a durabilidade)')
    A.anim('inspecionar', 2.4, [(None, 't', pose([(0, (0, 0, 0)), (0.5, (-0.6, 0.05, 0)), (1.9, (-0.6, 0.05, 0)), (2.4, (0, 0, 0))])),
                                (None, 'r', (1, 0, 0), pose([(0, 0), (0.5, 0), (1.2, 180), (1.9, 360), (2.4, 360)])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.5, 12), (1.9, 12), (2.4, 0)]))],
           desc='traz a ponta para perto e gira olhando a faca e a amarração')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.8), (3.0, 0)])), (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.002, 0)), (3.0, (0, 0, 0))]))],
           laco=True, desc='respiração leve parado')


@arma('lanca_improvisada', 'Lança improvisada', 'armas', 'lanca', classe='corpo_a_corpo', calibre='lâmina', capacidade='-', dano=48, dano_golpe_forte=80,
      alcance_m=1.6, tiros_por_s=1.4, precisao=1.0, ruido_m=2, durabilidade=900, peso_kg=0.95, raridade='comum', valor_troca=8, duas_maos=True,
      prende_no_alvo=0.35, empurra=True, receita={'faca_cozinha': 1, 'fita_adesiva': 1, 'cabo_madeira': 1}, bancada=False,
      reparo={'fita_adesiva': 1}, onde=['casas', 'quartel', 'abrigo'],
      descricao='Cabo de vassoura com uma faca de cozinha enfiada na ponta serrada, presa com prego, abraçadeiras, fita prata e arame. '
                'Mantém o zumbi a 1,5 m, mas a faca pode prender no alvo e a fita afrouxa com o uso. Feita na hora, sem bancada; '
                'o cabo pode vir de vassoura, rodo ou enxada.')
def lanca_improvisada(A): _lanca(A)
