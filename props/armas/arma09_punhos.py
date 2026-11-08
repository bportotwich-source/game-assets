# Punhos de pistola trocáveis do fuzil 5,56 (encaixe_punho): o original, um emborrachado com cavas e base larga,
# e um reto liso de polímero com rabo de castor. Desenho próprio (fotos do Bruno só como inspiração).
PU_D = (-0.004, -0.0015)                     # mesmo deslocamento do _cabo_fuzil


def _tex_pedrinhas(cor, seed=611, px=6000, tile=0.03):
    """Borracha com textura de pedrinhas: relevo arredondado miudo (~1 mm) e irregular."""
    n = int(round(tile * px)); g = GT.noise(n, n, 0.0004 * px, 0.0004 * px, seed); f = GT.fbm(n, n, 0.004 * px, 3, seed + 5)
    ped = GT.smooth(-1.2, 1.6, g)
    c = GT.rgb(CORES[cor])[None, None]
    alb = c * (0.9 + 0.06 * ped[..., None] + 0.02 * f[..., None]); hm = 0.00025 * ped + 0.00002 * f
    return alb, hm, 0.88 - 0.1 * ped, 1.3, 0.0004, tile, px


TEX_EXTRA += [('borracha_pedrinhas', lambda: _tex_pedrinhas('borracha'), 0.0), ('borracha_pedrinhas_tan', lambda: _tex_pedrinhas('polimero_tan'), 0.0)]


def _pu(pts):
    return affinity.translate(suave(pts, 4), *PU_D)


def _frente_cavas():
    """Frente do punho com o ressalto do dedo medio no alto e duas cavas: (x, y) de cima para baixo."""
    pts = []
    for y in np.linspace(-0.0435, -0.147, 40):
        t = (y + 0.0435) / -0.1035
        x = 0.0045 - 0.029 * t
        x += 0.0042 * math.exp(-((y + 0.056) / 0.0055) ** 2)                         # ressalto embaixo do guarda-mato
        x += 0.0034 * math.exp(-((y + 0.082) / 0.0065) ** 2) + 0.0034 * math.exp(-((y + 0.108) / 0.0065) ** 2) \
            + 0.0024 * math.exp(-((y + 0.133) / 0.007) ** 2)                         # tres gomos entre os dedos
        pts.append((x, y))
    return pts


def _punho_cavas(A, mat='borracha_pedrinhas', base='polimero'):
    q = A.base
    costas = [(-0.0275, -0.149), (-0.032, -0.152), (-0.07, -0.152), (-0.074, -0.146), (-0.066, -0.12), (-0.0565, -0.09), (-0.049, -0.068),
              (-0.0455, -0.058), (-0.05, -0.0515), (-0.051, -0.0465), (-0.046, -0.0435)]          # palma cheia e rabo de castor curto
    perfil = _pu(_frente_cavas() + costas)
    y0, y1 = -0.0435 + PU_D[1], -0.152 + PU_D[1]
    larg = lambda y: 0.0126 + 0.0034 * GT.smooth(y0 - 0.002, y0 - 0.026, y) + 0.0016 * math.exp(-((y - y0 + 0.06) / 0.022) ** 2)
    q.add(mat, punho_redondo(perfil, y0, y1, larg, n=2.2, fatias=120, voltas=60, raio_base=0.004))
    # base larga e redonda (apoio da mao), com tampa e parafuso no fundo
    yb = y1 + 0.004
    disco = trimesh.creation.cylinder(radius=1.0, height=1.0, sections=48); disco.apply_scale([0.031, 0.0085, 0.0215])
    disco.apply_translation([-0.052 + PU_D[0] + 0.003, yb - 0.0075, 0])
    borda = trimesh.creation.icosphere(3, radius=1.0); borda.apply_scale([0.032, 0.006, 0.0225]); borda.apply_translation([-0.052 + PU_D[0] + 0.003, yb - 0.0075, 0])
    q.add(base, inter([uniao([disco, borda]), caixa(-1, 1, yb - 0.0122, yb - 0.003, -1, 1)]))
    q.add(base, menos(_cil_y(0.016, yb - 0.0045, yb + 0.004, -0.052 + PU_D[0] + 0.002, 0.0, 40), _cil_y(0.002, yb - 0.02, yb + 0.02, 0, 0, 8)))
    q.add('aco_inox', _cil_y(0.0032, yb - 0.0126, yb - 0.0118, -0.052 + PU_D[0] + 0.003, 0.0, 20))
    q.add('aco_oxidado', caixa(-0.052 + PU_D[0] + 0.0004, -0.052 + PU_D[0] + 0.0056, yb - 0.0128, yb - 0.0124, -0.0005, 0.0005))
    A.pivo = PU_ORIG


def _punho_reto(A, mat='polimero', tex='polimero_pontos'):
    q = A.base
    frente = [(0.0045, -0.0435), (0.0062, -0.0485), (0.006, -0.0535), (0.0015, -0.0585), (-0.0035, -0.07)]
    frente += [(-0.0035 - 0.25 * (-0.07 - y), y) for y in np.linspace(-0.08, -0.146, 6)]
    costas = [(-0.023, -0.1515), (-0.028, -0.155), (-0.066, -0.155), (-0.0705, -0.15), (-0.063, -0.12), (-0.054, -0.088), (-0.0485, -0.066),
              (-0.049, -0.0575), (-0.056, -0.0505), (-0.0605, -0.0465), (-0.0585, -0.0425), (-0.046, -0.042), (-0.0365, -0.0435)]   # rabo de castor
    perfil = _pu(frente + costas)
    y0, y1 = -0.0435 + PU_D[1], -0.155 + PU_D[1]
    larg = lambda y: 0.0118 + 0.0026 * GT.smooth(y0 - 0.004, y0 - 0.03, y)
    corpo = punho_redondo(perfil, y0 + 0.0008, y1, larg, n=2.9, fatias=120, voltas=60, raio_base=0.0035)
    furo = cil_z(0.0018, -0.03, 0.03, -0.0545 + PU_D[0], -0.0475 + PU_D[1], 16)                   # furo da bandoleira no rabo de castor
    q.add(mat, menos(corpo, furo))
    # painel texturizado dos lados (borda lisa) e tampa do compartimento embaixo
    area = perfil.buffer(-0.0045, join_style=1).intersection(sbox(-1, y1 + 0.012, 1, y0 - 0.026))
    pont = punho_redondo(perfil, y0 + 0.0008, y1, lambda y: larg(y) + 0.00035, n=2.9, fatias=120, voltas=60, raio_base=0.0035)
    q.add(tex, inter([pont, solido(area, -0.05, 0.05)]))
    q.add(mat, solido(arred([(x + PU_D[0], y + PU_D[1]) for (x, y) in [(-0.064, -0.1535), (-0.028, -0.1535), (-0.0245, -0.1575), (-0.067, -0.1575)]], 0.0012),
                      -0.0105, 0.0105, 0.0008))                                                       # tampa do compartimento
    q.add('aco_oxidado', caixa(-0.0285 + PU_D[0], -0.0265 + PU_D[0], -0.1555 + PU_D[1], -0.1525 + PU_D[1], -0.004, 0.004))   # trava da tampa
    A.pivo = PU_ORIG


TAN_PU = {'polimero': 'polimero_tan', 'polimero_grip': 'polimero_grip_tan', 'polimero_pontos': 'polimero_pontos_tan', 'borracha_pedrinhas': 'borracha_pedrinhas_tan'}
_DADOS_PU = dict(raridade='incomum', valor_troca=10, onde=['quartel', 'galeria', 'delegacia'])


@_acessorio('punho_ar', 'Punho original do fuzil', 'punho', 'punho_ar', peso_kg=0.07, modificadores={}, raridade='comum', valor_troca=5,
            descricao='O punho que vem no fuzil: polímero com área pontilhada.')
def punho_ar(A): _cabo_fuzil(A.base, *PU_D); A.pivo = PU_ORIG


@_acessorio('punho_ar_tan', 'Punho original do fuzil (caramelo)', 'punho', 'punho_ar', peso_kg=0.07, modificadores={}, raridade='comum', valor_troca=5,
            descricao='O punho original em caramelo.')
def punho_ar_tan(A): _cabo_fuzil(A.base, *PU_D); _em_tan(A, TAN_PU); A.pivo = PU_ORIG


@_acessorio('punho_cavas', 'Punho emborrachado com cavas', 'punho', 'punho_ar', peso_kg=0.09, modificadores={'recuo': 0.95, 'estabilidade_mirando': 1.1},
            descricao='Borracha com textura de pedrinhas em toda a volta, ressalto para o dedo médio, cavas para os outros dedos e base larga '
                      'que apoia a mão. Não escorrega com a mão suada ou molhada.', **_DADOS_PU)
def punho_cavas(A): _punho_cavas(A)


@_acessorio('punho_cavas_tan', 'Punho emborrachado com cavas (caramelo)', 'punho', 'punho_ar', peso_kg=0.09,
            modificadores={'recuo': 0.95, 'estabilidade_mirando': 1.1}, descricao='O punho emborrachado com cavas em caramelo.', **_DADOS_PU)
def punho_cavas_tan(A): _punho_cavas(A); _em_tan(A, TAN_PU)


@_acessorio('punho_reto', 'Punho reto de polímero', 'punho', 'punho_ar', peso_kg=0.06, modificadores={'tempo_mirar': 0.95},
            descricao='Punho mais em pé e liso, com rabo de castor que protege a mão, painel de textura fina dos lados e compartimento '
                      'com tampa no fundo (cabe pilha ou bilhete).', **_DADOS_PU)
def punho_reto(A): _punho_reto(A)


@_acessorio('punho_reto_tan', 'Punho reto de polímero (caramelo)', 'punho', 'punho_ar', peso_kg=0.06, modificadores={'tempo_mirar': 0.95},
            descricao='O punho reto de polímero em caramelo.', **_DADOS_PU)
def punho_reto_tan(A): _punho_reto(A); _em_tan(A, TAN_PU)
