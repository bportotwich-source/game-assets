# Arma 17: faca de combate (lamina de ponta recortada com fio liso e serrilha perto do cabo, sulco, guarda de aco, cabo
# arredondado com cavas para os dedos e pomo com quebra-vidro) e bainha rigida de cinto com tira de trava.
# Executado por gerar_armas.py depois de arma17_besta.py (usa corpo_x de arma03). Desenho proprio, sem marca.
# Plano de lado: x frente (ponta), y cima (dorso), z espessura. Pivo no meio do cabo.

F_PONTA = 0.178                      # comprimento da lamina (x da ponta)


def _dorso(x):
    if x <= 0.105: return 0.012
    s = (x - 0.105) / (F_PONTA - 0.105); return 0.012 - 0.0112 * (1 - (1 - s) ** 2)


def _fio(x):
    if x < 0.008: return -0.0165
    if x < 0.016: s = (x - 0.008) / 0.008; return -0.0165 + 0.0045 * math.sin(math.pi * s) - 0.0025 * s   # cava (choil)
    if x <= 0.12: return -0.019
    s = (x - 0.12) / (F_PONTA - 0.12); return -0.019 + 0.0198 * s ** 2.2


def _esp(x):
    return 0.0026 if x <= 0.1 else 0.0026 - 0.002 * ((x - 0.1) / (F_PONTA - 0.1)) ** 1.3


def _loft_x(secoes):
    """secoes = [(x, [(z, y), ...]), ...] com o mesmo numero de pontos (aneis fechados): solido estanque com tampas."""
    n = len(secoes[0][1]); V = []
    for x, pts in secoes: V += [[x, y, z] for z, y in pts]
    V += [[secoes[0][0], np.mean([p[1] for p in secoes[0][1]]), 0.0], [secoes[-1][0], np.mean([p[1] for p in secoes[-1][1]]), 0.0]]
    F = []; m_ = len(secoes)
    for i in range(m_ - 1):
        for j in range(n):
            a0 = i * n + j; a1 = i * n + (j + 1) % n; b0 = a0 + n; b1 = a1 + n; F += [[a0, a1, b0], [a1, b1, b0]]
    c0, c1 = m_ * n, m_ * n + 1
    for j in range(n): F += [[c0, (j + 1) % n, j], [c1, (m_ - 1) * n + j, (m_ - 1) * n + (j + 1) % n]]
    m = trimesh.Trimesh(np.array(V), np.array(F), process=True); trimesh.repair.fix_normals(m); return _fix(m)


def _secao_lamina(x):
    yt, yb, t = _dorso(x), _fio(x), _esp(x); e = 0.00015
    yg = yb + 0.45 * (yt - yb)                                                  # fim do desbaste (chanfro principal)
    sc = 0.0 if x <= 0.105 else (x - 0.105) / (F_PONTA - 0.105)
    sw = 0.0006 + 0.0035 * sc; tt = t * (1 - 0.75 * sc) if sc else t * 0.82   # falso fio no recorte da ponta
    yg = min(yg, yt - sw - 0.0004)
    return [(tt, yt), (-tt, yt), (-t, yt - sw), (-t, yg), (-e, yb), (e, yb), (t, yg), (t, yt - sw)]


def _secao_fio(x):
    yt, yb, t = _dorso(x), _fio(x), _esp(x); e = 0.00015; yg = yb + 0.45 * (yt - yb)
    h = min(0.0032, 0.35 * (yt - yb)); z1 = e + (t - e) * h / max(yg - yb, 1e-4); o = 0.00005
    return [(z1 + o, yb + h), (-(z1 + o), yb + h), (-(e + o), yb - o), (e + o, yb - o)]


def _contorno_lamina(folga=0.0):
    xs = np.linspace(0.0, F_PONTA, 80)
    pts = [(x, _dorso(x)) for x in xs] + [(x, _fio(x)) for x in xs[::-1]]
    return Polygon(pts).buffer(folga, 12) if folga else Polygon(pts)


CONT_CABO_F = Polygon(suave([(-0.007, 0.011), (-0.06, 0.0135), (-0.11, 0.0128), (-0.125, 0.0112), (-0.127, -0.006), (-0.122, -0.019),
                             (-0.105, -0.0185), (-0.09, -0.0215), (-0.075, -0.0185), (-0.06, -0.0215), (-0.045, -0.0185), (-0.03, -0.0215),
                             (-0.016, -0.018), (-0.007, -0.0185)], 3))
LARG_CABO_F = lambda x: 0.0108 + 0.0016 * math.exp(-((x + 0.07) / 0.035) ** 2)


def _faca(A):
    q = A.base
    xs = list(np.linspace(-0.004, F_PONTA - 0.0015, 90))
    ult = _secao_lamina(F_PONTA - 0.0015); yc = float(np.mean([y for _, y in ult]))
    lam = _loft_x([(x, _secao_lamina(max(x, 0.0))) for x in xs] + [(F_PONTA, [(z * 0.1, yc + (y - yc) * 0.1) for z, y in ult])])
    xf = list(np.linspace(0.016, F_PONTA - 0.0015, 80))
    fio = _loft_x([(x, _secao_fio(x)) for x in xf])
    dentes = [cil_z(0.0027, -0.01, 0.01, x, _fio(x) - 0.0011, 18) for x in np.linspace(0.021, 0.047, 6)]   # serrilha perto do cabo
    sulco = [solido(LineString([(0.03, 0.0035), (0.092, 0.0035)]).buffer(0.0026, 12), zs * 0.0026 - 0.0007 if zs > 0 else -0.02, 0.02 if zs > 0 else -0.0026 + 0.0007)
             for zs in (1, -1)]
    q.add('aco_fosfatado', menos(lam, *dentes, *sulco))
    q.add('aco_inox', menos(fio, *dentes))
    # guarda de aco (o braco de baixo curva para a frente e protege o dedo)
    gd = Polygon(suave([(-0.008, 0.019), (0.0005, 0.019), (0.0005, -0.023), (0.007, -0.031), (0.0045, -0.036), (-0.003, -0.032), (-0.008, -0.025)], 2))
    q.add('aco_oxidado', solido(gd, -0.0068, 0.0068, 0.0018))
    q.add('aco_oxidado', caixa(-0.004, 0.0005, -0.016, 0.012, -0.0034, 0.0034))
    # cabo: nucleo de polimero com aneis de borracha, espacador de aco e pomo com quebra-vidro e furo do fiel
    cabo = corpo_x(CONT_CABO_F, -0.0075, -0.125, LARG_CABO_F, n=2.3, fatias=120, voltas=44, raio_tras=0.002, raio_frente=0.0015)
    q.add('polimero_grip', cabo)
    pele = corpo_x(CONT_CABO_F, -0.0075, -0.125, lambda x: LARG_CABO_F(x) + 0.0005, n=2.3, fatias=120, voltas=44, raio_tras=0.002, raio_frente=0.0015)
    for x in np.arange(-0.112, -0.02, 0.0085): q.add('borracha', inter([pele, caixa(x, x + 0.0032, -1, 1, -1, 1)]))
    q.add('aco_oxidado', inter([corpo_x(CONT_CABO_F, -0.0075, -0.125, lambda x: LARG_CABO_F(x) + 0.0003, n=2.3, fatias=120, voltas=44), caixa(-0.0125, -0.0095, -1, 1, -1, 1)]))
    pomo = Polygon(suave([(-0.124, 0.0125), (-0.132, 0.012), (-0.138, 0.006), (-0.138, -0.012), (-0.131, -0.0195), (-0.124, -0.0195)], 2))
    pm = menos(corpo_x(pomo, -0.124, -0.1385, lambda x: 0.0118, n=2.6, fatias=30, voltas=40, raio_tras=0.002, raio_frente=0.0005),
               cil_z(0.0028, -0.02, 0.02, -0.1305, -0.0045, 18))
    q.add('aco_oxidado', pm)
    q.add('aco_oxidado', torno_x([(0.004, -0.1375), (0.0035, -0.142), (0.0, -0.1465)], 6, -0.002))           # quebra-vidro
    q.add('nylon', trimesh.creation.torus(0.0085, 0.0016, major_sections=28, minor_sections=8).apply_transform(
        TF.translation_matrix([-0.1375, -0.0045, 0]) @ TF.rotation_matrix(math.pi / 2, [0, 0, 1]) @ TF.rotation_matrix(math.pi / 2, [1, 0, 0])))   # fiel (cordão)
    A.pivo = (-0.065, -0.003, 0.0)
    A.encaixe('cinto', (0.06, 0.0, -0.0105), 'bainha_faca', aceita=['bainha_cinto_faca'], descricao='a faca entra na bainha pelo pivô (a bainha tem o encaixe "arma")')
    A.encaixe('ponta', (F_PONTA, 0.0012, 0.0), 'efeito', descricao='ponta da lâmina (teste de acerto da estocada)')
    A.encaixe('fio_meio', (0.09, -0.019, 0.0), 'efeito', descricao='meio do fio (teste de acerto do golpe de corte)')
    A.anim('golpear', 0.55, [(None, 'r', (0, 1, 0), pose([(0, 0), (0.12, 38), (0.3, -55), (0.55, 0)])), (None, 'r', (1, 0, 0), pose([(0, 0), (0.12, 10), (0.3, -25), (0.55, 0)])),
                             (None, 't', pose([(0, (0, 0, 0)), (0.12, (-0.03, 0.02, 0)), (0.3, (0.08, -0.03, 0)), (0.55, (0, 0, 0))]))],
           desc='corte de lado (da direita para a esquerda): o acerto vale entre 0,15 e 0,3 s, use o encaixe fio_meio')
    A.anim('estocar', 0.5, [(None, 't', pose([(0, (0, 0, 0)), (0.1, (-0.05, 0.0, 0)), (0.22, (0.24, 0.01, 0)), (0.32, (0.24, 0.01, 0)), (0.5, (0, 0, 0))])),
                            (None, 'r', (0, 0, 1), pose([(0, 0), (0.1, 4), (0.22, -3), (0.5, 0)]))],
           desc='estocada para a frente (mais dano em zumbi, mas a faca pode prender: acerto entre 0,18 e 0,3 s no encaixe ponta)')
    A.anim('golpe_baixo', 0.6, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.15, 50), (0.35, -40), (0.6, 0)])),
                                (None, 't', pose([(0, (0, 0, 0)), (0.15, (-0.02, 0.1, 0)), (0.35, (0.1, -0.08, 0)), (0.6, (0, 0, 0))]))],
           desc='golpe de cima para baixo (na cabeça de zumbi caído)')
    A.anim('sacar', 0.6, [(None, 't', pose([(0, (-0.05, -0.35, 0.06)), (0.3, (0.0, -0.06, 0.01)), (0.6, (0, 0, 0))])), (None, 'r', (0, 0, 1), pose([(0, -85), (0.3, -20), (0.6, 0)]))],
           desc='tira da bainha na cintura e traz para a frente')
    A.anim('guardar', 0.6, [(None, 't', pose([(0, (0, 0, 0)), (0.3, (0.0, -0.06, 0.01)), (0.6, (-0.05, -0.35, 0.06))])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.3, -20), (0.6, -85)]))],
           desc='volta para a bainha')
    A.anim('inspecionar', 2.2, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.6, 180), (1.4, 180), (2.2, 360)])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.6, 15), (1.6, 15), (2.2, 0)]))],
           desc='gira a faca na mão olhando os dois lados da lâmina')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 1.0), (3.0, 0)])), (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))],
           laco=True, desc='respiração leve parado')


@arma('faca_combate', 'Faca de combate', 'armas', 'faca', classe='corpo_a_corpo', calibre='lâmina', capacidade='-', dano=45, dano_estocada=60, alcance_m=0.6, tiros_por_s=1.8,
      precisao=1.0, ruido_m=1, durabilidade=3000, peso_kg=0.32, raridade='incomum', valor_troca=30, prende_no_alvo=0.15,
      onde=['quartel', 'casa_de_campo', 'delegacia', 'armazem', 'loja_caca'],
      descricao='Lâmina de 18 cm de aço escurecido com ponta recortada, fio liso e serrilha perto do cabo para cortar corda. Cabo de borracha com '
                'cavas e pomo com quebra-vidro. Não faz barulho e não gasta munição, mas é preciso chegar muito perto.')
def faca_combate(A): _faca(A)


@_acessorio('bainha_cinto_faca', 'Bainha de cinto (faca de combate)', 'bainha', 'bainha_faca', peso_kg=0.14, raridade='comum', valor_troca=8,
            modificadores={'sacar_s': 0.85}, onde=['quartel', 'casa_de_campo', 'armazem'],
            descricao='Bainha rígida moldada com ilhoses, furo de dreno na ponta, passador de cinto e tira com botão de pressão por cima do cabo.')
def bainha_cinto_faca(A):
    q = A.base
    sil = _contorno_lamina(0.0042).union(sbox(-0.004, -0.0225, 0.012, 0.0165)).intersection(sbox(-0.0045, -0.05, 0.3, 0.05))
    corpo = menos(solido(sil, -0.0078, 0.0078, 0.0028), cil_z(0.0018, -0.02, 0.02, F_PONTA - 0.004, 0.0002, 12))
    q.add('polimero', corpo)
    q.add('polimero', solido(sil.buffer(0.0018).difference(sil.buffer(-0.0035)), -0.0018, 0.0018, 0.0006))   # aba das bordas (costura termomoldada)
    borda = sil.buffer(-0.0022).exterior
    for k in np.linspace(0.04, 0.96, 12):
        p = borda.interpolate(k, normalized=True)
        for zs in (-1, 1): q.add('aco_inox', cil_z(0.0021, min(zs * 0.0078, zs * 0.0086), max(zs * 0.0078, zs * 0.0086), p.x, p.y, 12))
    # boca reforcada e tira com botao de pressao por cima do cabo
    q.add('polimero', solido(arred([(-0.006, -0.025), (0.008, -0.025), (0.008, 0.019), (-0.006, 0.019)], 0.003), -0.0088, 0.0088, 0.0012))
    tira = menos(corpo_x(CONT_CABO_F, -0.016, -0.034, lambda x: LARG_CABO_F(x) + 0.0021, n=2.3, fatias=20, voltas=40),
                 corpo_x(CONT_CABO_F, -0.01, -0.04, lambda x: LARG_CABO_F(x) + 0.0003, n=2.3, fatias=20, voltas=40), caixa(-1, 1, -1, 0.002, -1, 1))
    q.add('nylon', tira)
    q.add('nylon', solido(arred([(-0.034, 0.002), (-0.016, 0.002), (-0.002, -0.006), (0.004, -0.006), (0.004, -0.021), (-0.03, -0.018)], 0.003), -0.0132, -0.0098, 0.0008))
    q.add('nylon', solido(arred([(-0.034, 0.002), (-0.016, 0.002), (-0.002, -0.006), (0.004, -0.006), (0.004, -0.021), (-0.03, -0.018)], 0.003), 0.0098, 0.0132, 0.0008))
    q.add('aco_inox', cil_z(0.0045, 0.0132, 0.0152, -0.023, -0.009, 20))
    # passador de cinto (atras, lado z-) com parafusos
    q.add('nylon_coldre', solido(arred([(0.01, -0.016), (0.062, -0.016), (0.062, 0.052), (0.01, 0.052)], 0.004), -0.0118, -0.0078, 0.0012))
    q.add('nylon_coldre', solido(arred([(0.01, 0.03), (0.062, 0.03), (0.062, 0.052), (0.01, 0.052)], 0.004), -0.0168, -0.0118, 0.0012))
    for (x, y) in ((0.02, -0.008), (0.052, -0.008), (0.02, 0.008), (0.052, 0.008)): q.add('aco_inox', cil_z(0.0025, -0.0125, -0.0115, x, y, 12))
    A.encaixe('arma', (-0.065, -0.003, 0.0), 'efeito', descricao='ponha a faca aqui (pivô da faca) para guardá-la na bainha')
    A.pivo = (0.06, 0.0, -0.0105)
