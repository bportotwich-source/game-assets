# Arma 19: machadinha tatica (cabeca e espiga numa peca so de aco escurecido: fio curvo com barba, ponta de tras para arrombar,
# furos de alivio; cabo arredondado com talas e cordao enrolado) e capa da lamina com tira de pressao.
# Executado por gerar_armas.py depois de arma19_facao.py. Desenho proprio, sem marca.
# Plano de lado: x frente (para onde o fio aponta), y cima (cabeca em cima), z espessura. Pivo na mao (parte de baixo do cabo).

MY0, MY1 = 0.255, 0.374              # faixa em y da cabeca


def _m_fio(y): return 0.094 - 8.5 * (y - 0.334) ** 2 - (0.012 * ((0.29 - y) / 0.035) if y < 0.29 else 0.0)


def _m_tras(y):
    if y >= 0.3: return -0.02 - 0.062 * max(0.0, 1 - abs(y - 0.341) / 0.033)
    if y >= 0.285: s = (y - 0.285) / 0.015; return 0.021 - 0.041 * s
    return 0.021 + (0.285 - y) * 0.3


def _m_esp(x, xe):
    if x < -0.02: return 0.0065 - 0.0048 * min(1.0, (-0.02 - x) / 0.062)
    if x <= 0.02: return 0.0065
    return 0.0047 - 0.0043 * min(1.0, (x - 0.02) / max(xe - 0.02, 1e-3))


def _m_secao(y, so_fio=False):
    xe = _m_fio(y); xb = _m_tras(y); x2 = max(0.02, xb + 0.004); x1 = (xb + x2) / 2; xg = xe - 0.0045; e = 0.00015
    if so_fio:
        h = 0.0035; z1 = _m_esp(xe - h, xe) + 0.00005
        return [(xe - h, z1), (xe + 0.00005, e + 0.00005), (xe + 0.00005, -e - 0.00005), (xe - h, -z1)]
    pts = [(xb, _m_esp(xb, xe)), (x1, _m_esp(x1, xe)), (x2, _m_esp(x2, xe)), (xg, _m_esp(xg, xe)), (xe, e)]
    return pts + [(x, -z) for x, z in pts[::-1]]


def _loft_y(secoes):
    """secoes = [(y, [(x, z), ...]), ...] com o mesmo numero de pontos: solido estanque com tampas."""
    n = len(secoes[0][1]); V = []
    for y, pts in secoes: V += [[x, y, z] for x, z in pts]
    V += [[np.mean([p[0] for p in secoes[0][1]]), secoes[0][0], 0.0], [np.mean([p[0] for p in secoes[-1][1]]), secoes[-1][0], 0.0]]
    F = []; m_ = len(secoes)
    for i in range(m_ - 1):
        for j in range(n):
            a0 = i * n + j; a1 = i * n + (j + 1) % n; b0 = a0 + n; b1 = a1 + n; F += [[a0, a1, b0], [a1, b1, b0]]
    c0, c1 = m_ * n, m_ * n + 1
    for j in range(n): F += [[c0, (j + 1) % n, j], [c1, (m_ - 1) * n + j, (m_ - 1) * n + (j + 1) % n]]
    m = trimesh.Trimesh(np.array(V), np.array(F), process=True); trimesh.repair.fix_normals(m); return _fix(m)


def _encolhe(pts, k):
    cx = np.mean([p[0] for p in pts]); return [(cx + (x - cx) * k, z * k) for x, z in pts]


CONT_CABO_M = Polygon(suave([(-0.017, 0.312), (0.017, 0.312), (0.0165, 0.24), (0.0155, 0.17), (0.0175, 0.11), (0.016, 0.06), (0.019, 0.025), (0.024, 0.004),
                             (0.018, -0.006), (-0.012, -0.006), (-0.024, 0.002), (-0.021, 0.03), (-0.017, 0.07), (-0.0185, 0.12), (-0.016, 0.2), (-0.0165, 0.26)], 3))
LARG_CABO_M = lambda y: 0.0118 + 0.0012 * math.exp(-((y - 0.1) / 0.05) ** 2)


def _machadinha(A):
    q = A.base
    ys = list(np.linspace(MY0, MY1, 70))
    sec = [(y, _m_secao(y)) for y in ys]
    sec = [(MY0 - 0.0015, _encolhe(sec[0][1], 0.3))] + sec + [(MY1 + 0.0015, _encolhe(sec[-1][1], 0.3))]
    cab = _loft_y(sec)
    furos = [solido(Point(0.045, 0.33).buffer(0.0085, 24), -0.02, 0.02), solido(LineString([(0.04, 0.293), (0.056, 0.282)]).buffer(0.0042, 16), -0.02, 0.02),
             solido(Point(-0.004, 0.34).buffer(0.0042, 20), -0.02, 0.02)]
    q.add('aco_fosfatado', menos(cab, *furos))
    q.add('aco_inox', _loft_y([(y, _m_secao(y, True)) for y in np.linspace(MY0 + 0.004, MY1 - 0.002, 66)]))
    q.add('aco_fosfatado', trimesh.creation.cone(0.0017, 0.006, sections=10).apply_transform(TF.translation_matrix([-0.081, 0.341, 0]) @ TF.rotation_matrix(-math.pi / 2, [0, 1, 0])))
    # espiga (mesma peca de aco) aparente entre as talas; talas arredondadas; cordao enrolado; furo do fiel
    furo_f = cil_z(0.0036, -0.02, 0.02, 0.0, 0.006, 18)
    q.add('aco_fosfatado', menos(solido(CONT_CABO_M.buffer(0.0006).intersection(sbox(-1, -1, 1, 0.31)), -0.0026, 0.0026, 0.0004), furo_f))
    nucleo = menos(punho_redondo(CONT_CABO_M, 0.3, -0.006, LARG_CABO_M, n=2.3, fatias=140, voltas=44, raio_base=0.004, raio_topo=0.0), caixa(-1, 1, 0.2995, 1, -1, 1))
    pinos = [(0.0, 0.27), (0.0, 0.215), (0.0, 0.035)]
    q.add('polimero_oliva', menos(nucleo, caixa(-1, 1, -1, 1, -0.0026, 0.0026), furo_f, *[cil_z(0.003, -0.02, 0.02, x, y, 16) for x, y in pinos]))
    for x, y in pinos:
        zt = LARG_CABO_M(y) * 0.96
        q.add('aco_inox', menos(cil_z(0.003, -zt, zt, x, y, 20), cil_z(0.0013, -0.02, 0.02, x, y, 12)))
    for k, y in enumerate(np.arange(0.065, 0.19, 0.0042)):                       # cordao enrolado (voltas levemente inclinadas)
        fat = punho_redondo(CONT_CABO_M, y + 0.0019, y - 0.0019, lambda yy: LARG_CABO_M(yy) + 0.0019, n=2.3, fatias=4, voltas=36)
        anel = menos(fat, punho_redondo(CONT_CABO_M, y + 0.003, y - 0.003, lambda yy: LARG_CABO_M(yy) - 0.0005, n=2.3, fatias=4, voltas=36))
        anel.apply_transform(TF.rotation_matrix(math.radians(4), [0, 0, 1], point=[0, y, 0]))
        q.add('corda_cabo' if k % 2 else 'lona_escura', anel)
    q.add('corda_cabo', trimesh.creation.torus(0.0085, 0.0017, major_sections=28, minor_sections=8).apply_transform(
        TF.translation_matrix([0.0, -0.002, 0]) @ TF.rotation_matrix(math.pi / 2, [0, 1, 0])))   # fiel
    A.pivo = (0.0, 0.09, 0.0)
    A.encaixe('capa', (0.06, 0.315, 0.0), 'capa_machadinha', explodir=(0.06, 0, 0), aceita=['capa_machadinha'],
              descricao='capa por cima do fio (tirar antes de usar; a animação "tirar_capa" puxa para a frente)')
    A.encaixe('fio_meio', (0.094, 0.334, 0.0), 'efeito', descricao='meio do fio (teste de acerto do golpe)')
    A.encaixe('ponta_tras', (-0.082, 0.341, 0.0), 'efeito', descricao='ponta de trás (golpe de ponta e alavanca para arrombar)')
    A.anim('golpear', 0.65, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 40), (0.38, -62), (0.65, 0)])),
                             (None, 't', pose([(0, (0, 0, 0)), (0.2, (-0.05, 0.05, 0)), (0.38, (0.08, -0.06, 0)), (0.65, (0, 0, 0))]))],
           desc='golpe de cima para baixo na frente: acerto entre 0,26 e 0,38 s no encaixe fio_meio')
    A.anim('golpe_forte', 1.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.42, 95), (0.5, 95), (0.68, -70), (1.0, 0)])),
                                (None, 't', pose([(0, (0, 0, 0)), (0.42, (-0.1, 0.12, 0)), (0.5, (-0.1, 0.12, 0)), (0.68, (0.1, -0.1, 0)), (1.0, (0, 0, 0))]))],
           desc='levanta atrás do ombro e desce com tudo (racha porta e cabeça): acerto entre 0,55 e 0,68 s')
    A.anim('golpe_ponta', 0.6, [(None, 'r', (0, 1, 0), pose([(0, 0), (0.15, 180), (0.6, 180)])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.2, 30), (0.38, -50), (0.6, 0)]))],
           desc='vira a machadinha e bate com a ponta de trás (fura capacete e crânio; pode prender)')
    A.anim('arrombar', 2.0, [(None, 't', pose([(0, (0, 0, 0)), (0.4, (0.12, 0.0, 0)), (1.6, (0.12, 0.0, 0)), (2.0, (0, 0, 0))])),
                             (None, 'r', (0, 1, 0), pose([(0, 0), (0.3, 180), (1.7, 180), (2.0, 0)])),
                             (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, -10), (0.8, 25), (1.0, 18), (1.3, 32), (1.6, 32), (2.0, 0)]))],
           desc='encaixa a ponta de trás na fresta e faz alavanca (porta, janela, tampa de caixa)')
    A.anim('tirar_capa', 0.4, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.2, -10), (0.4, 0)]))], desc='segura firme enquanto a mão puxa a capa (esconda o encaixe capa aos 0,25 s)')
    A.anim('inspecionar', 2.2, [(None, 'r', (0, 1, 0), pose([(0, 0), (0.6, 180), (1.4, 180), (2.2, 360)])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.6, -15), (1.6, -15), (2.2, 0)]))],
           desc='gira a machadinha olhando o fio e a ponta')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 1.0), (3.0, 0)])), (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))],
           laco=True, desc='respiração leve parado')


@arma('machadinha_tatica', 'Machadinha tática', 'armas', 'machadinha', classe='corpo_a_corpo', calibre='lâmina', capacidade='-', dano=70, dano_golpe_forte=105,
      alcance_m=0.7, tiros_por_s=1.1, precisao=1.0, ruido_m=3, durabilidade=3500, peso_kg=0.75, raridade='incomum', valor_troca=40,
      arromba=True, corta_madeira=True, prende_no_alvo=0.2, onde=['quartel', 'quartel_bombeiros', 'delegacia', 'loja_caca', 'armazem'],
      descricao='Cabeça e espiga numa peça só de aço escurecido: fio curvo com barba de um lado e ponta do outro para arrombar portas e janelas. '
                'Cabo com talas e cordão enrolado (dá para desenrolar e usar o cordão). Bate mais forte que o facão, mas alcança menos.')
def machadinha_tatica(A): _machadinha(A)


@_acessorio('capa_machadinha', 'Capa da lâmina (machadinha)', 'capa', 'capa_machadinha', peso_kg=0.07, raridade='comum', valor_troca=4, modificadores={},
            onde=['quartel', 'loja_caca', 'armazem'], descricao='Capa moldada que cobre o fio, com tira de náilon e botão de pressão por cima da cabeça. Não corta a mochila.')
def capa_machadinha(A):
    q = A.base
    ys = np.linspace(MY0 - 0.004, MY1 + 0.004, 40)
    fio = [(_m_fio(min(max(y, MY0), MY1)) + 0.0045, y) for y in ys]
    sil = Polygon([(0.016, MY1 + 0.004)] + fio[::-1] + [(0.024, MY0 - 0.006)]).buffer(0.002, 8)
    corpo = menos(solido(sil, -0.0092, 0.0092, 0.0035), _loft_y([(MY0 - 0.003, _encolhe(_m_secao(MY0), 1.25)), *[(y, [(x, z * 1.25 + (0.0006 if z > 0 else -0.0006)) for x, z in _m_secao(y)])
                                                                                                            for y in np.linspace(MY0, MY1, 40)], (MY1 + 0.003, _encolhe(_m_secao(MY1), 1.25))]))
    q.add('polimero', corpo)
    for y in np.linspace(MY0 + 0.012, MY1 - 0.012, 5):
        x = _m_fio(y) + 0.001
        for zs in (-1, 1): q.add('aco_inox', cil_z(0.0019, min(zs * 0.0092, zs * 0.0099), max(zs * 0.0092, zs * 0.0099), x, y, 12))
    # tira de nailon que passa por cima da cabeca e fecha com botao
    tira = [(0.022, MY1 + 0.0035), (0.0, MY1 + 0.006), (-0.03, MY1 + 0.005), (-0.05, MY1 + 0.0)]
    for zs in (-1, 1):
        q.add('nylon', solido(arred([(0.016, MY1 - 0.012), (0.03, MY1 - 0.012), (0.03, MY1 + 0.004), (0.016, MY1 + 0.004)], 0.002), min(zs * 0.0092, zs * 0.0104), max(zs * 0.0092, zs * 0.0104), 0.0004))
    for i in range(len(tira) - 1):
        a, b = tira[i], tira[i + 1]
        seg = solido(LineString([a, b]).buffer(0.0016, 6, cap_style=2), -0.0104, 0.0104, 0.0005); q.add('nylon', seg)
    q.add('nylon', solido(arred([(-0.056, MY1 - 0.016), (-0.044, MY1 - 0.016), (-0.044, MY1 + 0.002), (-0.056, MY1 + 0.002)], 0.003), -0.0085, 0.0085, 0.001))
    q.add('aco_inox', cil_z(0.0042, 0.0085, 0.0102, -0.05, MY1 - 0.007, 18))
    A.pivo = (0.06, 0.315, 0.0)
