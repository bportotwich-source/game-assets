# Arma 2: revolver .38 de 6 tiros com seus acessorios. Executado por gerar_armas.py (mesmas funcoes, plano de lado: x frente, y cima, z direita).
CORES.update({'madeira_punho': (96, 52, 30), 'couro': (104, 62, 34), 'couro_escuro': (60, 36, 22), 'costura': (214, 196, 160),
              'aco_azulado': (34, 38, 46)})
METAL.update({'aco_azulado': (0.85, 0.24), 'costura': (0.0, 0.8)})

CY = -0.0125            # eixo do tambor (abaixo do eixo do cano, que e y = 0)
RT = 0.0186             # raio do tambor
RC = 0.0125             # raio do circulo das camaras
TX0, TX1 = 0.0, 0.040   # tambor em x
PIV_BRACO = (0.044, -0.026, 0.0)   # eixo da dobradica do braco (gira para a esquerda, -z)


def _tex_couro(seed, px=1024, tile=0.25):
    n = int(tile * px); g = GT.noise(n, n, 0.004 * px, 0.004 * px, seed); f = GT.fbm(n, n, 0.03 * px, 4, seed + 2)
    poro = GT.smooth(0.8, 1.8, GT.noise(n, n, 0.0012 * px, 0.0012 * px, seed + 4))
    c = GT.rgb(CORES['couro'])[None, None]
    alb = c * (0.88 + 0.1 * f[..., None] + 0.04 * g[..., None] - 0.06 * poro[..., None]); hm = 0.0002 * g + 0.0003 * f - 0.0002 * poro
    return alb, hm, 0.62 + 0.15 * f, 1.0, 0.0008, tile, px


def _tex_madeira_punho(seed, px=4096, tile=0.12):
    """Nogueira com xadrez (quadriculado de empunhadura) em relevo."""
    n = int(tile * px); yy, xx = np.mgrid[0:n, 0:n] / px; p = 0.0016
    d = np.minimum(np.abs(((xx + yy) / p) % 1 - 0.5), np.abs(((xx - yy) / p) % 1 - 0.5))
    veio = GT.noise(n, n, 0.02 * px, 0.002 * px, seed); f = GT.fbm(n, n, 0.01 * px, 3, seed + 1)
    c = GT.rgb(CORES['madeira_punho'])[None, None]
    alb = c * (0.8 + 0.12 * veio[..., None] + 0.06 * f[..., None] + 0.15 * GT.smooth(0.05, 0.3, d)[..., None])
    hm = 0.0003 * GT.smooth(0.03, 0.25, d)
    return alb, hm, 0.55 + 0.2 * (1 - GT.smooth(0.05, 0.3, d)), 1.2, 0.0004, tile, px


_materiais_antes = materiais
def materiais():
    _materiais_antes()
    for i, (k, fn) in enumerate((('couro', _tex_couro), ('madeira_punho', _tex_madeira_punho))):
        alb, hm, rough, nstr, aod, tile, px = fn(401 + i)
        a, nm, o = tex_set(alb, hm, rough, nstr, aod, px)
        TEX[k] = (a, nm, o); gp.UV_ESCALA[k] = tile
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)


def _cartucho_38(sec=24, vazio=False):
    """Cartucho .38 deitado em x (base com aro em x = 0): estojo de latao com aro, projetil de chumbo semi-canto-vivo."""
    q = P()
    est = torno_x([(0.0, 0.0), (0.0055, 0.0), (0.0056, 0.0006), (0.0055, 0.0014), (0.0049, 0.0016), (0.00485, 0.029), (0.0, 0.029)], sec)
    if vazio: est = menos(est, cil_x(0.0044, 0.004, 0.04, sec=sec))
    q.add('latao', est)
    if not vazio:
        q.add('chumbo', torno_x([(0.0045, 0.0285), (0.00455, 0.031), (0.0046, 0.0318), (0.0038, 0.0322), (0.0034, 0.036), (0.0026, 0.038),
                                 (0.0, 0.0386)], sec))
    q.add('aco_inox', torno_x([(0.0, -0.00005), (0.0022, -0.00005), (0.0022, 0.0004)], max(8, sec // 2)))
    return q


def _tambor(q):
    """Tambor com 6 camaras, canaletas, entalhes de parada e chanfro na frente. Origem = eixo do tambor (y = CY) na face de tras."""
    corpo = torno_x([(0.0045, TX0), (RT - 0.0008, TX0), (RT, TX0 + 0.0008), (RT, TX1 - 0.003), (RT - 0.0025, TX1), (0.0045, TX1)], 64)
    cortes = []
    for i in range(6):
        a = i * math.pi / 3
        cortes.append(cil_x(0.00495, TX0 - 0.01, TX1 + 0.01, RC * math.cos(a), RC * math.sin(a), 24))            # camaras
        b = a + math.pi / 6; r = RT + 0.0016
        can = uniao([cil_x(0.0036, 0.011, 0.031, r * math.cos(b), r * math.sin(b), 16),
                     trimesh.creation.icosphere(2, 0.0036).apply_translation([0.011, r * math.cos(b), r * math.sin(b)]),
                     trimesh.creation.icosphere(2, 0.0036).apply_translation([0.031, r * math.cos(b), r * math.sin(b)])])
        cortes.append(can)                                                                                         # canaletas
        s = caixa(0.0035, 0.0075, RT - 0.0012, RT + 0.002, -0.0014, 0.0014); s.apply_transform(TF.rotation_matrix(a - math.pi / 2, [1, 0, 0]))
        cortes.append(s)                                                                                           # parada
    cortes.append(cil_x(0.0099, TX0 - 0.001, TX0 + 0.0016, sec=32))                                               # alojamento da estrela
    t = menos(corpo, *cortes)
    t.apply_translation([0, CY, 0])
    q.add('aco_azulado', t)


def _estrela(q):
    """Estrela do extrator (face de tras do tambor) + vareta do extrator, origem no eixo do tambor."""
    st = Point(0, 0).buffer(0.0098, 32)
    for i in range(6):
        a = i * math.pi / 3; st = st.difference(Point(RC * math.cos(a), RC * math.sin(a)).buffer(0.0045, 16))
    m = trimesh.creation.extrude_polygon(st.buffer(0), 0.0016)
    m.vertices = np.stack([m.vertices[:, 2], CY + m.vertices[:, 0], m.vertices[:, 1]], 1); q.add('aco_azulado', _fix(m))
    q.add('aco_azulado', cil_x(0.0026, 0.0016, TX1 + 0.031, CY, sec=16))                                             # vareta
    q.add('recartilhado', torno_x([(0.0032, TX1 + 0.028), (0.0034, TX1 + 0.03), (0.0034, TX1 + 0.037), (0.0028, TX1 + 0.039)], 20, CY))   # ponta


def _cao(q):
    """Cao (martelo) com espora quadriculada; origem no pino (-0.017, -0.006)."""
    perf = arred([(-0.019, -0.012), (-0.012, -0.008), (-0.0115, 0.004), (-0.008, 0.0095), (-0.0095, 0.012), (-0.017, 0.012), (-0.026, 0.017),
                  (-0.031, 0.0175), (-0.032, 0.0145), (-0.024, 0.009), (-0.021, 0.0), (-0.021, -0.008)], 0.0008)
    q.add('aco_azulado', solido(perf, -0.0034, 0.0034, 0.0007))
    for i in range(6):                                                                             # quadriculado da espora
        x = -0.0305 + i * 0.0016
        q.add('aco_azulado', caixa(x, x + 0.0007, 0.0158 - (x + 0.031) * 0.12, 0.0181 - (x + 0.031) * 0.12, -0.0034, 0.0034))
    q.add('aco_inox', torno_x([(0.0012, -0.009), (0.0012, -0.0065), (0.0008, -0.006)], 12, 0.0, 0.0))  # percussor (nariz do cao)


def _gatilho_rev(q):
    """Gatilho largo e liso: desce do pino e a ponta curva para a FRENTE (o dedo puxa pela face da frente, concava)."""
    lam = LineString([(0.0062, -0.0305), (0.0046, -0.037), (0.0042, -0.0425), (0.0052, -0.0465), (0.0082, -0.0492)]).buffer(0.0019, cap_style=1, join_style=1)
    q.add('aco_azulado', solido(lam, -0.0045, 0.0045, 0.0013))
    for i in range(4):                                                                                       # estrias da face da frente
        y = -0.038 - i * 0.0022
        q.add('aco_azulado', caixa(0.0058, 0.0064, y - 0.0003, y + 0.0003, -0.0043, 0.0043))


def _armacao_rev(p):
    out = [(0.056, 0.0122), (0.056, -0.012), (0.05, -0.024), (0.04, -0.0325), (0.02, -0.0335), (0.021, -0.04), (0.019, -0.05), (0.01, -0.058),
           (-0.003, -0.059), (-0.012, -0.053), (-0.016, -0.06), (-0.025, -0.084), (-0.03, -0.104), (-0.052, -0.104), (-0.054, -0.094),
           (-0.046, -0.06), (-0.036, -0.03), (-0.03, -0.014), (-0.024, -0.002), (-0.02, 0.006), (-0.012, 0.0122)]
    perfil = arred(out, 0.0018)
    guarda = arred([(-0.004, -0.0345), (0.016, -0.0345), (0.0155, -0.0445), (0.008, -0.0525), (-0.003, -0.053), (-0.008, -0.047)], 0.003)
    perfil = perfil.difference(guarda)
    corpo = solido(perfil, -0.0092, 0.0092, 0.0013)
    # escudo de recuo (atras do tambor) e janela do tambor
    escudo = torno_x([(0.0, -0.006), (RT + 0.0008, -0.006), (RT + 0.0008, -0.0012), (0.0, -0.0012)], 64, CY)
    corpo = uniao([corpo, inter([escudo, caixa(-0.01, 0.0, -0.0315, 0.0122, -0.0195, 0.0195)])])
    corpo = menos(corpo, caixa(TX0 - 0.0006, TX1 + 0.0006, CY - RT - 0.0012, CY + RT + 0.0006, -0.03, 0.03),     # janela do tambor
                  caixa(-0.027, -0.0105, -0.012, 0.02, -0.0036, 0.0036),                                       # fenda do cao
                  caixa(0.001, 0.0125, -0.045, -0.026, -0.0047, 0.0047),                                         # fenda do gatilho
                  cil_x(0.0014, -0.02, 0.0, 0.0, 0.0, 10),                                                        # furo do percussor
                  caixa(0.004, 0.038, 0.0105, 0.02, -0.0012, 0.0012))                                            # sulco de mira na ponte
    corpo = menos(corpo, caixa(-0.08, -0.0128, -0.2, -0.033, -0.03, 0.03))           # o cabo chato sai: entra o núcleo arredondado
    p.add('aco_azulado', corpo)
    p.add('aco_azulado', punho_redondo(CABO38, -0.0295, -0.1148, LARG_NUCLEO38, n=2.3, fatias=110, voltas=56, raio_base=0.005))
    # cano com proteção da vareta (lug cheio), mira de rampa com inserto laranja, coroa
    cano = uniao([cil_x(0.0088, 0.05, 0.158, sec=40),
                  solido(arred([(0.052, -0.0065), (0.15, -0.0065), (0.152, -0.016), (0.146, -0.0215), (0.06, -0.0215), (0.052, -0.018)], 0.002),
                         -0.0072, 0.0072, 0.0022),
                  solido(arred([(0.052, 0.006), (0.157, 0.006), (0.157, 0.0108), (0.052, 0.0108)], 0.0008), -0.0036, 0.0036, 0.0006)])
    cano = menos(cano, cil_x(0.0046, 0.03, 0.17, sec=24), cil_x(0.0034, TX1 + 0.001, TX1 + 0.04, CY, 0.0, 16))
    for x in np.arange(0.06, 0.15, 0.0025):                                                                     # estrias da costela
        cano = menos(cano, caixa(x, x + 0.0008, 0.0104, 0.012, -0.004, 0.004))
    p.add('aco_azulado', cano)
    p.add('aco_azulado', tubo_x(0.0046, 0.0082, 0.1578, 0.1592, sec=40, ch=0.0006))
    trilho(p, 'aco_azulado', 0.09, 0.144, -0.0205, True, 0.016, 0.013)                                          # trilho curto embaixo do lug (lanterna/laser)
    rampa = arred([(0.138, 0.0105), (0.155, 0.0105), (0.155, 0.0182), (0.151, 0.0186)], 0.0005)
    p.add('aco_azulado', solido(rampa, -0.0015, 0.0015, 0.0003))
    p.add('tinta_laranja', solido(arred([(0.1505, 0.0148), (0.1545, 0.0148), (0.1545, 0.0181), (0.1505, 0.0181)], 0.0004), -0.00155, 0.00155))
    # alça de mira (entalhe na traseira da ponte), trava do tambor (lado esquerdo), placa lateral, parafusos, pino do cão
    p.add('aco_azulado', solido(arred([(-0.012, 0.0115), (-0.004, 0.0115), (-0.004, 0.0158), (-0.012, 0.0158)], 0.0006), -0.006, -0.0014, 0.0004))
    p.add('aco_azulado', solido(arred([(-0.012, 0.0115), (-0.004, 0.0115), (-0.004, 0.0158), (-0.012, 0.0158)], 0.0006), 0.0014, 0.006, 0.0004))
    for (x, y) in ((0.006, -0.012), (-0.022, -0.028), (0.03, -0.026)):
        p.add('aco_inox', cil_z(0.0019, 0.0091, 0.0099, x, y, 16))
        p.add('aco_oxidado', caixa(x - 0.0017, x + 0.0017, y - 0.0003, y + 0.0003, 0.0097, 0.01))                  # fenda do parafuso
    p.add('aco_azulado', solido(arred([(-0.026, -0.03), (0.04, -0.03), (0.05, -0.022), (0.05, -0.012), (-0.016, -0.004), (-0.026, -0.016)], 0.002),
                                0.0091, 0.0094))                                                                     # placa lateral (direita)
    for zs in (-1, 1): p.add('aco_inox', cil_z(0.0013, min(zs * 0.0092, zs * 0.0098), max(zs * 0.0092, zs * 0.0098), -0.017, -0.006, 12))


CABO38 = suave([(-0.0165, -0.03), (-0.0175, -0.046), (-0.0225, -0.068), (-0.0275, -0.092), (-0.0305, -0.108), (-0.0335, -0.1148),
                (-0.0545, -0.1148), (-0.0582, -0.1085), (-0.0575, -0.096), (-0.0515, -0.066), (-0.043, -0.042), (-0.0355, -0.03)])
LARG_TALA38 = lambda y: 0.0085 + 0.0068 * GT.smooth(-0.03, -0.048, y) + 0.0008 * math.exp(-((y + 0.08) / 0.02) ** 2)
LARG_NUCLEO38 = lambda y: 0.0092 - 0.0016 * GT.smooth(-0.03, -0.045, y)


def _punho_madeira(q):
    """Talas de nogueira que seguem a curva do cabo: borda lisa, quadriculado levantado, medalhão e parafuso.
    Nó próprio para trocar pela empunhadura de borracha. O núcleo de aço (costas e frente do cabo) fica na armação."""
    cabo_com_talas(q, CABO38, -0.0305, -0.1148, LARG_NUCLEO38, LARG_TALA38, 'aco_azulado', 'madeira_escura', 'madeira_punho',
                   borda=0.0018, borda_xadrez=0.0032, n=2.3, raio_base=0.005, medalhao=(-0.0385, -0.058, 0.0048, 'latao'),
                   parafuso=(-0.041, -0.089), nucleo=False)


def _trava(q):
    lev = arred([(-0.012, -0.004), (-0.002, -0.004), (-0.002, 0.0015), (-0.012, 0.0015)], 0.0012)
    q.add('aco_azulado', solido(lev, -0.0112, -0.0092, 0.0005))
    for x in np.linspace(-0.011, -0.003, 6): q.add('aco_azulado', caixa(x, x + 0.0006, -0.0036, 0.0011, -0.0115, -0.0111))


@arma('revolver_38', 'Revólver Vigia .38', 'armas', 'revolver', classe='fogo', calibre='.38', municao='municao_38',
      capacidade=6, dano=45, alcance_m=25, alcance_max_m=50, modo='ação dupla (ou simples com o cão armado)', tiros_por_s=2.5,
      recarga_s=3.4, recarga_vazia_s=3.4, precisao=0.75, recuo=0.45, ruido_m=70, durabilidade=1500, peso_kg=0.95, raridade='comum',
      valor_troca=35, onde=['casas', 'casa_de_campo', 'armazem', 'motel', 'quartel'],
      descricao='Revólver de 6 tiros com tambor que abre de lado. Não engasga nunca e é fácil de achar em casas, mas recarrega devagar '
                'sem o carregador rápido.')
def revolver_38(A):
    A.pivo = (-0.036, -0.07, 0.0)
    _armacao_rev(A.base)
    pun = A.parte('punho', (-0.04, -0.07, 0), explodir=(-0.03, -0.03, 0), tipo='fixa', descricao='talas de madeira (troca pela empunhadura de borracha)')
    _punho_madeira(pun)
    cao = A.parte('cao', (-0.017, -0.006, 0), explodir=(-0.03, 0.04, 0), tipo='gira', eixo='x', curso_graus=38,
                  descricao='arma para trás (38°) e cai no tiro')
    _cao(cao)
    gat = A.parte('gatilho', (0.0045, -0.029, 0), explodir=(0.02, -0.05, 0), tipo='gira', eixo='x', curso_graus=-22, descricao='puxa para trás')
    _gatilho_rev(gat)
    tra = A.parte('trava', (0.0, 0.0, 0.0), explodir=(-0.01, 0.0, -0.03), tipo='desliza', curso_m=0.004, descricao='empurra para a frente para abrir o tambor')
    _trava(tra)
    bra = A.parte('braco', PIV_BRACO, explodir=(0.0, -0.02, -0.06), tipo='gira', eixo='z', curso_graus=-82,
                  descricao='braço do tambor: gira para a esquerda e o tambor sai da armação')
    bra.add('aco_azulado', solido(arred([(TX1 + 0.0004, -0.03), (0.052, -0.03), (0.052, CY + 0.004), (TX1 + 0.0004, CY + 0.004)], 0.0015),
                                  -0.0072, 0.0072, 0.0015))
    bra.add('aco_azulado', cil_x(0.0034, TX1, TX1 + 0.006, CY, 0, 20))
    tam = A.parte('tambor', (0.0, CY, 0.0), pai='braco', explodir=(0.0, -0.01, -0.06), tipo='gira', eixo='z', curso_graus=60,
                  descricao='gira 60° a cada tiro (eixo do tambor, paralelo ao cano)')
    _tambor(tam)
    ext = A.parte('extrator', (0.0, CY, 0.0), pai='tambor', explodir=(-0.05, 0.0, -0.07), tipo='desliza', curso_m=0.022,
                  descricao='vareta empurrada para trás: a estrela tira os 6 estojos de uma vez')
    _estrela(ext)
    cart = _cartucho_38(24)
    for i in range(6):
        a = i * math.pi / 3
        ext.merge(cart, TF.translation_matrix([-0.0012, CY + RC * math.cos(a), RC * math.sin(a)]))
    A.encaixe('encaixe_mira', (0.014, 0.0122, 0), 'mira_revolver', explodir=(0, 0.04, 0), aceita=['mira_ponto_vermelho_revolver'])
    A.encaixe('encaixe_empunhadura', (-0.04, -0.07, 0), 'punho_38', substitui='punho', explodir=(-0.03, -0.03, 0),
              aceita=['empunhadura_madeira_38', 'empunhadura_borracha_38'],
              descricao='ao pôr uma empunhadura aqui, esconda as malhas do nó punho')
    A.encaixe('encaixe_recarga', (-0.0012, CY, 0), 'recarga_38', pai='tambor', aceita=['carregador_rapido_38'],
              descricao='carregador rápido encosta aqui (atrás do tambor aberto) durante a recarga')
    A.encaixe('encaixe_trilho', (0.128, -0.026, 0), 'trilho_curto', explodir=(0.02, -0.05, 0), aceita=['lanterna_pistola', 'laser_pistola', 'combo_lanterna_laser'],
              descricao='trilho curto embaixo da proteção da vareta')
    A.encaixe('boca_fogo', (0.1592, 0, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('mira_ferro', (-0.008, 0.0158, 0), 'mira', descricao='linha de visada: entalhe -> rampa laranja')
    A.encaixe('cinto', (0, 0, 0), 'coldre', aceita=['coldre_revolver'], descricao='a arma entra no coldre pelo pivô (o coldre tem o encaixe "arma")')
    # ---- animacoes. Eixos no plano de lado: (0,0,1) = gira no plano lateral (cao, gatilho); (1,0,0) = em volta do cano
    giro = lambda ks: ('tambor', 'r', (1, 0, 0), pose(ks))
    A.anim('atirar', 0.32, [
        ('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.14, -22), (0.2, -22), (0.3, 0)])),
        ('cao', 'r', (0, 0, 1), pose([(0, 0), (0.13, 38), (0.145, 0), (0.32, 0)])),
        giro([(0, 0), (0.02, 0), (0.13, 60), (0.32, 60)]),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.145, 0), (0.17, 10), (0.32, 0)])),
        (None, 't', pose([(0, (0, 0, 0)), (0.145, (0, 0, 0)), (0.17, (-0.014, 0.006, 0)), (0.32, (0, 0, 0))]))],
        desc='ação dupla: o gatilho arma o cão e gira o tambor 60°, o cão cai (0,145 s) e a arma dá o coice')
    A.anim('engatilhar', 0.35, [('cao', 'r', (0, 0, 1), pose([(0, 0), (0.3, 38), (0.35, 38)])), giro([(0, 0), (0.05, 0), (0.3, 60), (0.35, 60)]),
                                 ('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.3, -10), (0.35, -10)]))],
           desc='polegar arma o cão (ação simples): tambor gira e o gatilho recua um pouco; depois use atirar_armado')
    A.anim('atirar_armado', 0.2, [
        ('gatilho', 'r', (0, 0, 1), pose([(0, -10), (0.02, -22), (0.08, -22), (0.18, 0)])),
        ('cao', 'r', (0, 0, 1), pose([(0, 38), (0.02, 38), (0.035, 0), (0.2, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.035, 0), (0.06, 10), (0.2, 0)])),
        (None, 't', pose([(0, (0, 0, 0)), (0.035, (0, 0, 0)), (0.06, (-0.014, 0.006, 0)), (0.2, (0, 0, 0))]))],
        desc='tiro com o cão já armado: gatilho leve, mais preciso')
    rec = [(0, 0), (0.25, 0), (0.55, -82), (2.7, -82), (3.0, 0), (3.4, 0)]
    A.anim('recarregar', 3.4, [
        ('trava', 't', pose([(0, (0, 0, 0)), (0.15, (0.004, 0, 0)), (0.3, (0.004, 0, 0)), (0.4, (0, 0, 0))])),
        ('braco', 'r', (1, 0, 0), pose(rec)),
        ('extrator', 't', pose([(0, (0, 0, 0)), (0.9, (0, 0, 0)), (1.05, (-0.022, 0, 0)), (1.2, (-0.022, 0, 0)), (1.3, (0, 0, 0))])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.6, 0), (0.85, 60), (1.3, 60), (1.55, -25), (2.6, -25), (3.0, 0), (3.4, 0)])),
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.5, 0), (0.7, -30), (2.6, -30), (3.0, 0)]))],
        desc='abre o tambor (0,55 s), aponta para cima e empurra o extrator (1,05 s: soltar 6 estojos), aponta para baixo, '
             'carrega de 1,6 a 2,5 s (carregador rápido em encaixe_recarga, ou um a um) e fecha (3,0 s)')
    A.anim('inspecionar', 3.2, [
        ('trava', 't', pose([(0, (0, 0, 0)), (0.15, (0.004, 0, 0)), (0.3, (0.004, 0, 0)), (0.4, (0, 0, 0))])),
        ('braco', 'r', (1, 0, 0), pose([(0, 0), (0.3, 0), (0.6, -82), (2.4, -82), (2.7, 0)])),
        giro([(0, 0), (0.7, 0), (1.9, 720), (2.4, 720)]),
        (None, 'r', (1, 0, 0), pose([(0, 0), (0.6, -40), (2.4, -40), (2.8, 0)])),
        (None, 'r', (0, 0, 1), pose([(0, 0), (0.6, 15), (2.4, 15), (2.8, 0)]))],
        desc='abre o tambor, gira as 6 câmaras com o dedo e fecha com um golpe de pulso')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.8), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


# ---------------------------------------------------------------------------- acessorios do revolver
@_acessorio('carregador_rapido_38', 'Carregador rápido .38 (6)', 'recarga', 'recarga_38', capacidade=6, municao='municao_38', peso_kg=0.1,
            raridade='incomum', valor_troca=12, modificadores={'recarga_s': 0.55}, onde=['quartel', 'motel', 'casas'],
            descricao='Segura 6 cartuchos na posição das câmaras: encosta, gira o botão e os 6 entram de uma vez.')
def carregador_rapido_38(A):
    q = A.base
    corpo = torno_x([(0.0, -0.006), (0.0175, -0.006), (0.0185, -0.0045), (0.0185, -0.0015), (0.0165, 0.0), (0.0, 0.0)], 48)
    corpo = menos(corpo, *[cil_x(0.0057, -0.0062, 0.001, -0.0 + RC * math.cos(i * math.pi / 3), RC * math.sin(i * math.pi / 3), 20) for i in range(6)])
    corpo.apply_translation([-0.0, 0, 0]); q.add('aluminio_preto', corpo)
    q.add('aluminio_preto', torno_x([(0.006, -0.006), (0.0065, -0.008), (0.0065, -0.016), (0.0072, -0.018), (0.0072, -0.026), (0.0065, -0.028), (0.0, -0.028)], 32))
    q.add('recartilhado', tubo_x(0.0071, 0.0076, -0.0255, -0.0185, sec=32))
    cart = _cartucho_38(20)
    for i in range(6):
        a = i * math.pi / 3; q.merge(cart, TF.translation_matrix([-0.0045, RC * math.cos(a), RC * math.sin(a)]))
    A.pivo = (-0.0045, 0, 0)        # aro dos cartuchos encostado na face de tras do tambor


@_acessorio('mira_ponto_vermelho_revolver', 'Mira de ponto vermelho para revólver', 'mira', 'mira_revolver', peso_kg=0.12, raridade='raro',
            valor_troca=40, usa='pilhas', autonomia_min=3000, modificadores={'precisao_mirando': 1.3, 'tempo_mirar': 0.8, 'alcance_m': 1.2},
            onde=['quartel', 'galeria', 'casa_de_campo'], linha_de_visada='encaixe "olho"',
            descricao='Tubo de ponto vermelho com base parafusada na ponte do revólver. Mira rápido e acerta mais longe.')
def mira_ponto_vermelho_revolver(A):
    q = A.base
    q.add('aluminio_preto', solido(arred([(-0.018, 0.0), (0.03, 0.0), (0.03, 0.006), (-0.018, 0.006)], 0.001), -0.0055, 0.0055, 0.0008))   # base
    for x in (-0.012, 0.024): q.add('aco_inox', cil_z(0.0015, 0.0055, 0.0062, x, 0.003, 10)).add('aco_inox', cil_z(0.0015, -0.0062, -0.0055, x, 0.003, 10))
    for x0 in (-0.012, 0.016):                                                                                      # aneis
        q.add('aluminio_preto', solido(arred([(x0, 0.005), (x0 + 0.01, 0.005), (x0 + 0.01, 0.034), (x0, 0.034)], 0.001), -0.0165, 0.0165, 0.001))
    yc = 0.0215
    tubo = torno_x([(0.0, -0.03), (0.0135, -0.03), (0.0138, -0.028), (0.0125, -0.022), (0.0125, 0.028), (0.0145, 0.034), (0.0145, 0.044), (0.0, 0.044)], 48, yc)
    q.add('aluminio_preto', menos(tubo, cil_x(0.0115, -0.031, -0.0255, yc, 0, 40), cil_x(0.0128, 0.04, 0.045, yc, 0, 40)))
    q.add('lente', cil_x(0.0116, -0.026, -0.0255, yc, 0, 40)); q.add('lente', cil_x(0.0128, 0.0398, 0.0404, yc, 0, 40))
    q.add('ponto_vermelho', caixa(-0.0258, -0.0256, yc - 0.0002, yc + 0.0002, -0.0002, 0.0002))
    torre = arred([(0.0, yc + 0.012), (0.012, yc + 0.012), (0.012, yc + 0.019), (0.0, yc + 0.019)], 0.002)
    q.add('aluminio_preto', solido(torre, -0.006, 0.006, 0.0015))
    q.add('recartilhado', cil_z(0.0055, 0.0125, 0.0185, 0.006, yc, 24))                                               # botao de brilho
    A.encaixe('olho', (-0.03, yc, 0), 'mira', descricao='ocular: linha de visada')
    A.pivo = (0, 0, 0)


@_acessorio('empunhadura_madeira_38', 'Talas de madeira .38', 'empunhadura', 'punho_38', peso_kg=0.08, raridade='comum',
            modificadores={}, descricao='As talas de nogueira quadriculada que vêm no revólver.')
def empunhadura_madeira_38(A):
    _punho_madeira(A.base); A.pivo = (-0.04, -0.07, 0)


@_acessorio('empunhadura_borracha_38', 'Empunhadura de borracha .38', 'empunhadura', 'punho_38', peso_kg=0.1, raridade='incomum',
            valor_troca=10, modificadores={'recuo': 0.8, 'precisao': 1.05}, onde=['quartel', 'casas'],
            descricao='Borracha com apoio para os dedos e costas fechadas: segura o coice e não escorrega com a mão suada.')
def empunhadura_borracha_38(A):
    q = A.base
    corpo = suave([(-0.0155, -0.03), (-0.0165, -0.046), (-0.0205, -0.055), (-0.0185, -0.064), (-0.0235, -0.073), (-0.0215, -0.082),
                   (-0.0275, -0.091), (-0.0265, -0.1), (-0.0315, -0.117), (-0.034, -0.1205), (-0.056, -0.1205), (-0.0605, -0.113),
                   (-0.0595, -0.098), (-0.0525, -0.066), (-0.0435, -0.04), (-0.036, -0.028)])
    larg = lambda y: 0.0095 + 0.0076 * GT.smooth(-0.029, -0.05, y)
    q.add('borracha_grip', punho_redondo(corpo, -0.0285, -0.1205, larg, n=2.15, fatias=110, voltas=56, raio_base=0.0065))
    q.add('aco_inox', cil_z(0.0018, 0.0158, 0.0168, -0.043, -0.088, 12)).add('aco_inox', cil_z(0.0018, -0.0168, -0.0158, -0.043, -0.088, 12))
    A.pivo = (-0.04, -0.07, 0)


@_acessorio('coldre_revolver', 'Coldre de couro (revólver)', 'coldre', 'coldre', peso_kg=0.22, raridade='comum', valor_troca=8,
            modificadores={'tempo_sacar': 0.7}, onde=['casas', 'casa_de_campo', 'armazem'],
            descricao='Coldre de cinto com presilha de pressão. Leva o revólver sem ocupar espaço na mochila e saca mais rápido.')
def coldre_revolver(A):
    q = A.base
    sil = arred([(-0.02, -0.04), (-0.012, 0.03), (0.06, 0.03), (0.17, 0.018), (0.178, 0.0), (0.176, -0.03), (0.06, -0.04), (0.045, -0.06),
                 (0.0, -0.062)], 0.008)
    q.add('couro', solido(sil, -0.024, 0.024, 0.012))
    q.add('couro_escuro', solido(sil.buffer(-0.003), -0.0244, 0.0244, 0.002))
    pts = list(sil.buffer(-0.005).exterior.coords)
    for i in range(0, len(pts) - 1, 2):                                                       # pesponto em volta
        a, b = np.array(pts[i]), np.array(pts[i + 1]); c = (a + b) / 2
        for zs in (-1, 1): q.add('costura', caixa(c[0] - 0.0012, c[0] + 0.0012, c[1] - 0.0004, c[1] + 0.0004, zs * 0.0247 - 0.0003, zs * 0.0247 + 0.0003))
    q.add('couro', solido(arred([(-0.01, 0.022), (0.03, 0.022), (0.03, 0.075), (-0.01, 0.075)], 0.004), -0.03, -0.024, 0.001))   # passador do cinto
    q.add('couro', solido(arred([(-0.018, 0.028), (-0.005, 0.028), (-0.002, 0.04), (-0.006, 0.048), (-0.02, 0.046)], 0.003), -0.024, 0.024, 0.001))
    for zs in (-1, 1): q.add('aco_inox', cil_z(0.0045, min(zs * 0.024, zs * 0.0262), max(zs * 0.024, zs * 0.0262), -0.012, 0.04, 20))   # botão de pressão
    A.encaixe('arma', (-0.036, -0.07, 0.0), 'efeito', descricao='ponha a arma aqui (pivô da arma) para guardá-la no coldre')
    A.pivo = (0.01, 0.05, -0.027)          # passador do cinto


@arma('municao_38', 'Cartucho .38', 'municao', 'municao', calibre='.38', peso_kg=0.015, empilha=60, raridade='comum',
      onde=['casas', 'casa_de_campo', 'armazem', 'motel', 'quartel'], descricao='Um cartucho .38 (deitado, pivô no centro).')
def municao_38(A):
    A.base.merge(_cartucho_38(28), TF.translation_matrix([-0.0193, 0.0056, 0])); A.pivo = (0, 0, 0)


@arma('estojo_38', 'Estojo .38 (vazio)', 'municao', 'estojo', calibre='.38', peso_kg=0.005,
      descricao='Estojo vazio: no revólver saem os 6 juntos quando o extrator é empurrado (recarregar, 1,05 s).')
def estojo_38(A):
    A.base.merge(_cartucho_38(24, vazio=True), TF.translation_matrix([-0.0145, 0, 0])); A.pivo = (0, 0, 0)


CX38 = dict(x0=-0.06, x1=0.06, y0=0.0, y1=0.046, z0=-0.03, z1=0.03)


@arma('caixa_municao_38', 'Caixa de munição .38 (50)', 'municao', 'caixa', calibre='.38', municao='municao_38', quantidade=50,
      peso_kg=0.78, empilha=4, raridade='comum', onde=['casas', 'casa_de_campo', 'armazem', 'motel', 'quartel'],
      descricao='Caixa de papelão com bandeja de 50 cartuchos .38. A tampa abre (nó "tampa", animação "abrir").')
def caixa_municao_38(A):
    caixa_municao(A, 'rotulo_38', CX38, _arte_caixa(CX38, '.38', '50 CARTUCHOS', 'CHUMBO SEMI-CANTO-VIVO 158 gr', cor=(30, 70, 120)),
                  _cartucho_38(12), 10, 5, 0.0117, 0.0114, faltam=(3, 4, 9), bandeja=0.018)
