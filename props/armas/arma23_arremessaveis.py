# Arma 22: arremessaveis improvisados: coquetel molotov (garrafa + pano), bomba de pregos (lata com fita e pavio) e
# isca sonora (despertador de duas campainhas que toca ao cair). Executado por gerar_armas.py depois de arma22_bastao.py.
# Desenho proprio, sem marca. Plano: x frente, y cima, z direita. Pivo no centro da mao.
CORES.update({'pano_sujo': (184, 168, 138), 'pano_queimado': (40, 34, 30), 'papel_rotulo': (196, 182, 140), 'aco_lata': (172, 172, 168),
              'pavio_verde': (46, 104, 52), 'tinta_relogio': (120, 30, 26), 'mostrador': (232, 226, 206)})
METAL.update({'pano_sujo': (0.0, 0.95), 'pano_queimado': (0.0, 0.95), 'papel_rotulo': (0.0, 0.8), 'aco_lata': (0.9, 0.35),
              'pavio_verde': (0.0, 0.8), 'tinta_relogio': (0.2, 0.35), 'mostrador': (0.0, 0.45)})
TRANSP.update({'vidro_verde': ((70, 120, 70), 0.32, 0.05), 'combustivel': ((150, 82, 14), 0.85, 0.1)})

ROT_Y = TF.rotation_matrix(math.pi / 2, [0, 0, 1])          # eixo x -> eixo y


def _torno_y(prof, sec=32):
    """Solido de revolucao em torno do eixo y; prof = [(r, y), ...] (comeca e termina no eixo)."""
    return torno_x(prof, sec).apply_transform(ROT_Y)


def _arremessar(A, desc):
    A.anim('arremessar', 0.9, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.35, 70), (0.45, 70), (0.62, -40), (0.9, -40)])),
                               (None, 't', pose([(0, (0, 0, 0)), (0.35, (-0.18, 0.22, 0)), (0.45, (-0.18, 0.22, 0)), (0.62, (0.35, 0.1, 0)), (0.9, (0.35, 0.1, 0))]))],
           desc=desc)


def _ocioso(A):
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 1.2), (3.0, 0)])), (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.002, 0)), (3.0, (0, 0, 0))]))],
           laco=True, desc='respiração leve parado')


# ---------------------------------------------------------------------------- coquetel molotov
def _molotov(A):
    q = A.base
    ext = [(0.0, 0.0), (0.03, 0.0), (0.0335, 0.004), (0.0335, 0.14), (0.031, 0.16), (0.022, 0.178), (0.0135, 0.194), (0.0125, 0.224),
           (0.0148, 0.226), (0.0148, 0.236), (0.0125, 0.238)]
    inn = [(0.0095, 0.238), (0.0095, 0.196), (0.0185, 0.18), (0.028, 0.161), (0.0305, 0.141), (0.0305, 0.007), (0.0, 0.0045)]
    q.add('vidro_verde', _torno_y(ext + inn, 40))
    q.add('combustivel', _torno_y([(0.0, 0.0048), (0.0302, 0.0048), (0.0302, 0.104), (0.0, 0.104)], 40))
    rot = menos(_torno_y([(0.0, 0.055), (0.0337, 0.055), (0.0337, 0.118), (0.0, 0.118)], 40), _torno_y([(0.0, 0.05), (0.03355, 0.05), (0.03355, 0.12), (0.0, 0.12)], 40),
                caixa(-1, -0.012, -1, 1, -1, 1), caixa(-0.02, 0.02, 0.1, 0.2, -1, 1).apply_transform(TF.rotation_matrix(0.5, [0, 0, 1], point=[0, 0.1, 0])))
    q.add('papel_rotulo', rot)                                          # rotulo rasgado
    pv = A.parte('pavio', (0.0, 0.236, 0.0), explodir=(0.0, 0.06, 0.0), tipo='remove', direcao=[0.0, 1.0, 0.0], item='roupas',
                 descricao='pano enfiado no gargalo e amarrado com barbante: é o pavio (acenda antes de jogar)')
    pv.add('pano_sujo', _torno_y([(0.0, 0.2), (0.0093, 0.2), (0.0093, 0.24), (0.0, 0.24)], 16))
    rng = np.random.default_rng(23)
    for k in range(9):
        s = trimesh.creation.icosphere(2, radius=rng.uniform(0.007, 0.011)); s.apply_scale([rng.uniform(0.8, 1.4), rng.uniform(0.5, 0.9), rng.uniform(0.8, 1.4)])
        s.apply_transform(TF.rotation_matrix(rng.uniform(0, 3), [0, 1, 0])); s.apply_translation([rng.uniform(-0.009, 0.009), 0.244 + rng.uniform(0, 0.016), rng.uniform(-0.009, 0.009)])
        pv.add('pano_queimado' if k in (7, 8) else 'pano_sujo', s)
    rabo = _catmull([(0.004, 0.252), (0.014, 0.255), (0.0195, 0.245), (0.0172, 0.226), (0.019, 0.2), (0.026, 0.184), (0.0335, 0.168)], 10)
    for ang, k in ((0.9, 1.0), (-1.9, 0.75)):                           # duas pontas do pano caindo pelo gargalo
        rb = np.array([(p[0] * (1 if i < 2 else k), p[1] + (0 if k == 1.0 else 0.012 * (i / len(rabo)))) for i, p in enumerate(rabo)])
        pv.add('pano_sujo', _fita(rb, lambda s: 0.011 - 0.004 * s, lambda s: 0.0009, 0.2).apply_transform(TF.rotation_matrix(ang, [0, 1, 0])))
    pv.add('corda_cabo', trimesh.creation.torus(0.0182, 0.0012, major_sections=32, minor_sections=6).apply_transform(
        TF.translation_matrix([0, 0.211, 0]) @ TF.rotation_matrix(math.pi / 2, [1, 0, 0])))
    A.pivo = (0.0, 0.09, 0.0)
    A.encaixe('chama', (0.0, 0.262, 0.0), 'efeito', pai='pavio', descricao='onde nasce a chama do pano aceso')
    A.encaixe('quebra', (0.0, 0.0, 0.0), 'efeito', descricao='fundo da garrafa: ao bater, quebra e espalha o fogo (raio do efeito em dados.raio_m)')
    A.anim('acender', 1.4, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.35, 35), (1.1, 35), (1.4, 0)])),
                            (None, 't', pose([(0, (0, 0, 0)), (0.35, (0.05, 0.04, -0.06)), (1.1, (0.05, 0.04, -0.06)), (1.4, (0, 0, 0))]))],
           desc='inclina o gargalo para a outra mão com o isqueiro; ligue a chama aos 0,8 s no encaixe chama')
    _arremessar(A, 'joga por cima do ombro; solte aos 0,6 s (vira objeto físico, quebra ao bater)')
    A.anim('inspecionar', 2.2, [(None, 'r', (0, 1, 0), pose([(0, 0), (1.1, 180), (2.2, 360)])), (None, 'r', (1, 0, 0), pose([(0, 0), (0.5, 18), (1.0, -18), (1.5, 18), (2.2, 0)]))],
           desc='gira a garrafa vendo o combustível balançar')
    _ocioso(A)


# ---------------------------------------------------------------------------- bomba de pregos (lata)
def _bomba_pregos(A):
    q = A.base
    prof = [(0.0, 0.0), (0.035, 0.0), (0.0372, 0.003), (0.0372, 0.008)]
    for y in np.arange(0.014, 0.098, 0.009): prof += [(0.0368, y), (0.0372, y + 0.0045)]
    prof += [(0.0372, 0.104), (0.0382, 0.107), (0.0382, 0.112), (0.0355, 0.112), (0.0352, 0.108), (0.0, 0.108)]
    q.add('aco_lata', _torno_y(prof, 44))
    for k in range(10):                                                  # pregos por fora, presos com fita
        a = 2 * math.pi * k / 10 + 0.15
        x, z = 0.0386 * math.cos(a), 0.0386 * math.sin(a)
        q.add('aco_prego', trimesh.creation.cylinder(radius=0.00125, segment=[[x, 0.012, z], [x, 0.099, z]], sections=8))
        q.add('aco_prego', trimesh.creation.cylinder(radius=0.0032, segment=[[x * 1.005, 0.099, z * 1.005], [x * 1.005, 0.1006, z * 1.005]], sections=12))
    rng = np.random.default_rng(41)
    for y0, y1 in ((0.022, 0.046), (0.066, 0.09)):
        for k, y in enumerate(np.arange(y0, y1 - 0.006, 0.0075)):
            m = tubo_x(0.04, 0.0405 + 0.0002 * (k % 2), y, y + 0.012, sec=40).apply_transform(ROT_Y)
            m.apply_transform(TF.rotation_matrix(math.radians(rng.uniform(-3, 3)), [1, 0, 0], point=[0, y, 0])); q.add('fita_cinza', m)
    for a in (0.3, 0.3 + math.pi / 2):                                   # fita em X na tampa, descendo pelos lados
        R = TF.rotation_matrix(a, [0, 1, 0])
        q.add('fita_cinza', caixa(-0.0385, 0.0385, 0.112, 0.1125, -0.012, 0.012).apply_transform(R))
        for s in (-1, 1):
            q.add('fita_cinza', caixa(s * 0.0386 - 0.0002, s * 0.0386 + 0.0002, 0.094, 0.1125, -0.012, 0.012).apply_transform(R))
    pv = A.parte('pavio', (0.0, 0.1125, 0.0), explodir=(0.0, 0.05, 0.0), tipo='remove', direcao=[0.0, 1.0, 0.0],
                 descricao='pavio verde saindo da tampa: acende e queima ~4 s')
    pts = _catmull([(0.0, 0.106, 0.0), (0.0, 0.122, 0.0), (0.006, 0.138, 0.002), (0.016, 0.148, 0.004), (0.026, 0.15, 0.006)], 10)
    pv.add('pavio_verde', _tubo3d([(p[0], p[1], 0.0015 + 0.002 * i / len(pts)) for i, p in enumerate(pts)], 0.0017, 8))
    A.pivo = (0.0, 0.055, 0.0)
    A.encaixe('chama', (0.026, 0.15, 0.003), 'efeito', pai='pavio', descricao='ponta do pavio (faísca)')
    A.anim('acender', 1.2, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.3, 25), (0.9, 25), (1.2, 0)])),
                            (None, 't', pose([(0, (0, 0, 0)), (0.3, (0.04, 0.05, -0.05)), (0.9, (0.04, 0.05, -0.05)), (1.2, (0, 0, 0))]))],
           desc='traz o pavio para o isqueiro; ligue a faísca aos 0,7 s (explode 4 s depois)')
    _arremessar(A, 'joga por cima do ombro; solte aos 0,6 s (rola até explodir)')
    _ocioso(A)


# ---------------------------------------------------------------------------- isca sonora (despertador)
def _anel_z(r0, r1, z0, z1, sec=48):
    return menos(cil_z(r1, z0, z1, 0, 0, sec), cil_z(r0, z0 - 0.001, z1 + 0.001, 0, 0, sec))


def _isca(A):
    q = A.base
    q.add('tinta_relogio', cil_z(0.045, -0.015, 0.012, 0, 0, 48))
    q.add('aco_inox', _anel_z(0.0405, 0.0465, 0.011, 0.0185, 48))
    q.add('aco_inox', _anel_z(0.042, 0.0458, -0.017, -0.014, 48))
    q.add('mostrador', cil_z(0.0408, 0.011, 0.0128, 0, 0, 48))
    q.add('lente_clara', cil_z(0.0408, 0.0172, 0.0178, 0, 0, 48))
    for k in range(60):                                                  # marcas do mostrador
        a = 2 * math.pi * k / 60; g = k % 5 == 0; L = 0.0055 if g else 0.0022; w = 0.0011 if g else 0.0004
        m = caixa(-w, w, 0.0345 - L, 0.0345, 0.0128, 0.0131).apply_transform(TF.rotation_matrix(a, [0, 0, 1])); q.add('polimero', m)
    for s in (-1, 1):                                                    # campainhas, pes e chaves de corda
        R = TF.translation_matrix([s * 0.031, 0.047, -0.002]) @ TF.rotation_matrix(-s * math.radians(38), [0, 0, 1])
        sino = menos(_torno_y([(0.0, 0.0), (0.0215, 0.0), (0.0222, 0.0025), (0.0195, 0.012), (0.012, 0.0185), (0.0, 0.0205)], 36),
                     _torno_y([(0.0, -0.001), (0.0205, -0.001), (0.0182, 0.011), (0.011, 0.0172), (0.0, 0.019)], 36))
        q.add('aco_inox', sino.apply_transform(R))
        q.add('aco_inox', trimesh.creation.cylinder(radius=0.0022, segment=[[s * 0.024, 0.039, -0.002], [s * 0.031 + s * 0.0123 * math.sin(math.radians(38)), 0.047 + 0.0195 * math.cos(math.radians(38)), -0.002]], sections=10))
        q.add('aco_inox', trimesh.creation.cone(0.006, 0.014, sections=16).apply_transform(
            TF.translation_matrix([s * 0.028, -0.036, 0.0]) @ TF.rotation_matrix(math.pi / 2 + s * math.radians(25), [0, 0, 1]) @ TF.rotation_matrix(math.pi / 2, [0, 1, 0])))
        q.add('aco_inox', cil_z(0.0016, -0.025, -0.015, s * 0.016, -0.004, 10))
        q.add('aco_inox', solido(arred([(s * 0.016 - 0.008, -0.004), (s * 0.016 - 0.005, -0.009), (s * 0.016 + 0.005, -0.009), (s * 0.016 + 0.008, -0.004),
                                        (s * 0.016 + 0.005, 0.001), (s * 0.016 - 0.005, 0.001)], 0.002), -0.0265, -0.0245, 0.0003))
    alca = [(-0.032 * math.cos(t), 0.044 + 0.04 * math.sin(t), -0.009) for t in np.linspace(0.25, math.pi - 0.25, 30)]
    q.add('aco_inox', _tubo3d(alca, 0.0019, 8))
    q.add('polimero', caixa(0.012, 0.02, 0.043, 0.048, -0.006, 0.0))     # botao de desligar o alarme
    pos = {'ponteiro_horas': (0.019, 0.0018, 0.0136, 'polimero', 65), 'ponteiro_minutos': (0.03, 0.0012, 0.0142, 'polimero', 200),
           'ponteiro_alarme': (0.025, 0.0007, 0.0133, 'tinta_vermelha', 300)}
    for no, (L, w, z, mat, ang) in pos.items():
        pt = A.parte(no, (0.0, 0.0, 0.0), explodir=(0.0, 0.0, 0.03), tipo='gira', eixo='z', curso_graus=-360,
                     descricao='ponteiro do alarme (a corda gira ele até a hora de tocar)' if 'alarme' in no else 'ponteiro')
        m = solido(Polygon([(-w * 1.5, -0.006), (w * 1.5, -0.006), (w, L * 0.9), (0.0, L), (-w, L * 0.9)]), z, z + 0.0004)
        pt.add(mat, m.apply_transform(TF.rotation_matrix(-math.radians(ang), [0, 0, 1])))
    q.add('aco_inox', cil_z(0.0022, 0.0128, 0.0152, 0, 0, 16))
    mt = A.parte('martelo', (0.0, 0.043, -0.002), explodir=(0.0, 0.03, 0.0), tipo='gira', eixo='z', curso_graus=24,
                 descricao='martelinho entre as campainhas (balança rápido quando toca)')
    mt.add('aco_inox', trimesh.creation.cylinder(radius=0.0012, segment=[[0, 0.043, -0.002], [0, 0.072, -0.002]], sections=8))
    mt.add('aco_inox', trimesh.creation.icosphere(2, radius=0.0035).apply_translation([0, 0.073, -0.002]))
    A.pivo = (0.0, 0.0, -0.005)
    A.encaixe('som', (0.0, 0.06, 0.0), 'efeito', descricao='de onde sai o toque (atrai zumbis num raio de dados.ruido_m)')
    A.anim('dar_corda', 1.4, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.3, -30), (1.1, -30), (1.4, 0)])),
                              ('ponteiro_alarme', 'r', (0, 0, 1), pose([(0, 0), (0.4, 0), (1.0, -120), (1.4, -120)]))],
           desc='vira o relógio, gira a chave e põe o alarme para daqui a pouco')
    A.anim('tocar', 0.24, [('martelo', 'r', (0, 0, 1), pose([(0, -12), (0.06, 12), (0.12, -12), (0.18, 12), (0.24, -12)])),
                           (None, 't', pose([(0, (0, 0, 0)), (0.06, (0.0006, 0, 0)), (0.12, (0, 0, 0.0006)), (0.18, (-0.0006, 0, 0)), (0.24, (0, 0, 0))]))],
           laco=True, desc='toque do alarme: martelo bate nas campainhas e o relógio treme (repita durante dados.toque_s)')
    A.anim('arremessar', 0.8, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.3, -40), (0.5, 30), (0.8, 30)])),
                               (None, 't', pose([(0, (0, 0, 0)), (0.3, (-0.12, -0.15, 0)), (0.5, (0.3, 0.05, 0)), (0.8, (0.3, 0.05, 0))]))],
           desc='joga por baixo para não quebrar; solte aos 0,45 s (toca ao parar no chão)')
    _ocioso(A)


@arma('coquetel_molotov', 'Coquetel molotov', 'armas', 'arremessavel', classe='arremessavel', calibre='fogo', capacidade='-', dano=40, dano_por_s=12,
      raio_m=2.5, queima_s=8, alcance_m=18, tiros_por_s=0.5, precisao=0.8, ruido_m=10, durabilidade=1, peso_kg=0.7, raridade='incomum', valor_troca=14, empilha=3,
      receita={'garrafa_vidro': 1, 'galao_gasolina': 0.25, 'roupas': 1}, bancada=False, onde=['posto', 'garagem', 'abrigo'],
      descricao='Garrafa de vidro com combustível e um pano enfiado no gargalo, amarrado com barbante. Acenda o pano e jogue: '
                'quebra ao bater e deixa uma poça de fogo por alguns segundos. Ilumina a noite, mas chama atenção.')
def coquetel_molotov(A): _molotov(A)


@arma('bomba_pregos', 'Bomba de pregos (lata)', 'armas', 'arremessavel', classe='arremessavel', calibre='estilhaços', capacidade='-', dano=90,
      raio_m=4.0, pavio_s=4, alcance_m=15, tiros_por_s=0.4, precisao=0.75, ruido_m=60, durabilidade=1, peso_kg=0.6, raridade='raro', valor_troca=20, empilha=3,
      receita={'lata_feijao': 1, 'caixa_pregos': 1, 'fita_adesiva': 1, 'sucata': 1}, bancada=True, onde=['abrigo', 'garagem'],
      descricao='Lata vazia fechada com fita, cheia de pregos por dentro e por fora, com um pavio verde na tampa. '
                'Acenda, jogue e corra: estoura 4 s depois e derruba um grupo, mas o estrondo atrai tudo num raio grande.')
def bomba_pregos(A): _bomba_pregos(A)


@arma('isca_sonora', 'Isca sonora (despertador)', 'armas', 'arremessavel', classe='arremessavel', calibre='som', capacidade='-', dano=0,
      alcance_m=14, tiros_por_s=0.5, precisao=0.9, ruido_m=35, durabilidade=30, toque_s=20, atraso_s=3, peso_kg=0.35, raridade='comum', valor_troca=5, empilha=2,
      reutilizavel=True, onde=['casas', 'motel', 'hotel', 'abrigo'],
      descricao='Despertador de corda com duas campainhas. Dê corda, jogue longe e ele toca por uns 20 s: os zumbis vão atrás do barulho. '
                'Dá para pegar de volta e usar de novo, se ninguém pisar nele.')
def isca_sonora(A): _isca(A)
