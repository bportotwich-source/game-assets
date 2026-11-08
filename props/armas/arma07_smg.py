# Arma 8: submetralhadora compacta 9 mm (estilo PDW) com seus acessorios. Executado por gerar_armas.py
# (plano de lado: x frente, y cima, z direita). Desenho proprio inspirado na foto do Bruno; nada copiado de arma comercial.
# Usa a municao 9 mm da pistola e os acessorios de rosca 9 mm (supressor, compensador, protetor).

SX0, SX1 = -0.072, 0.2           # corpo em x (tras / frente)
SY_T, SY_B = 0.026, -0.024       # topo (o trilho fica por cima) e fundo do corpo de cima
SW = 0.0195                      # meia largura do corpo
S_XM = 0.233                     # fim da rosca do cano (encaixe da boca)
SMAG = (0.031, -0.026)           # topo do carregador (centro)
SANG = math.radians(8.0)         # inclinacao do punho e do carregador (embaixo vai para tras)
SDIR = np.array([-math.sin(SANG), -math.cos(SANG)])   # direcao de saida do carregador
SCOR = 0.13                      # curso da coronha (fechada -> aberta)


def _paralelo(c0, L, meia, d=SDIR):
    """Retangulo ao longo de d: comeca no centro c0 e anda L, com meia profundidade 'meia' (plano x, y)."""
    n = np.array([-d[1], d[0]]); c0 = np.array(c0); c1 = c0 + d * L
    return Polygon([tuple(c0 + n * meia), tuple(c1 + n * meia), tuple(c1 - n * meia), tuple(c0 - n * meia)])


def _carregador_smg(q, cap=30, mat='polimero'):
    """Carregador reto de fileira dupla que entra pelo punho; base larga com ressalto de dedo na frente."""
    L = {20: 0.112, 30: 0.142, 40: 0.178}[cap]
    corpo = _paralelo(SMAG, L, 0.0162)
    q.add(mat, solido(arred(list(corpo.exterior.coords)[:-1], 0.003), -0.0105, 0.0105, 0.0012))
    for zs in (-1, 1):                                                                                   # nervura e furos de contagem
        nerv = _paralelo(np.array(SMAG) + SDIR * 0.03, L - 0.05, 0.003)
        q.add(mat, solido(arred(list(nerv.exterior.coords)[:-1], 0.0025), min(zs * 0.0105, zs * 0.0111), max(zs * 0.0105, zs * 0.0111), 0.0003))
    for k in range(int((L - 0.04) / 0.022)):
        c = np.array(SMAG) + SDIR * (0.045 + k * 0.022) + np.array([SDIR[1], -SDIR[0]]) * -0.009
        q.add('aco_oxidado', cil_z(0.0016, -0.0109, -0.0104, c[0], c[1], 12))
    fim = np.array(SMAG) + SDIR * L; n = np.array([-SDIR[1], SDIR[0]])
    base = [fim + n * 0.0195 - SDIR * 0.001, fim - n * 0.0185 - SDIR * 0.001, fim - n * 0.0185 + SDIR * 0.009, fim + n * 0.0215 + SDIR * 0.009]
    q.add(mat, solido(Polygon([tuple(x) for x in base]).buffer(0.0015, join_style=1), -0.0125, 0.0125, 0.0015))
    q.merge(_cartucho_9mm_malha(16), TF.translation_matrix([SMAG[0] - 0.0105, SMAG[1] - 0.004, 0.0025]))
    for zs in (-1, 1): q.add('aco_oxidado', caixa(SMAG[0] - 0.014, SMAG[0] + 0.01, SMAG[1] - 0.003, SMAG[1] + 0.0015, zs * 0.0062 - 0.0012, zs * 0.0062 + 0.0012))


SCABO = suave([(0.003, -0.026), (0.056, -0.026), (0.055, -0.045), (0.052, -0.07), (0.048, -0.1), (0.044, -0.128), (0.038, -0.138),
               (-0.008, -0.138), (-0.014, -0.13), (-0.011, -0.1), (-0.005, -0.07), (-0.001, -0.048), (-0.008, -0.04), (-0.006, -0.026)], 3)


def _corpo_smg(p):
    perfil = arred([(SX0, SY_T), (SX1 - 0.012, SY_T), (SX1, SY_T - 0.01), (SX1, SY_B + 0.01), (SX1 - 0.012, SY_B), (0.118, SY_B),
                    (0.112, -0.034), (-0.014, -0.034), (-0.03, SY_B), (SX0 + 0.008, SY_B + 0.002), (SX0, SY_B + 0.01)], 0.003)
    corpo = solido(perfil, -SW, SW, 0.004)
    porta = solido(arred([(0.03, 0.002), (0.072, 0.002), (0.072, 0.016), (0.03, 0.016)], 0.003), SW - 0.006, SW + 0.01)        # janela do estojo (direita)
    furo_c = _paralelo(SMAG, 0.2, 0.0168)                                                                                       # poco do carregador
    juntas = [solido(arred([(SX0 + 0.01, -0.0045), (SX1 - 0.014, -0.0045), (SX1 - 0.014, -0.0033), (SX0 + 0.01, -0.0033)], 0.0005),
                     min(zs * (SW - 0.0007), zs * (SW + 0.01)), max(zs * (SW - 0.0007), zs * (SW + 0.01))) for zs in (-1, 1)]       # emenda das duas metades
    corpo = menos(corpo, porta, solido(furo_c, -0.0112, 0.0112), *juntas,
                  *[cil_x(0.0046, SX0 - 0.01, SX0 + 0.06, 0.0, zs * 0.0145, 20) for zs in (-1, 1)])                            # furos das varetas da coronha
    p.add('polimero', corpo)
    for zs in (-1, 1):                                                                                                          # paineis em relevo dos lados
        s = (min(zs * SW, zs * (SW + 0.0007)), max(zs * SW, zs * (SW + 0.0007)))
        p.add('polimero', solido(arred([(0.096, -0.016), (0.186, -0.016), (0.186, 0.015), (0.096, 0.015)], 0.005), *s, 0.0003))
        p.add('polimero', solido(arred([(SX0 + 0.012, 0.004), (0.02, 0.004), (0.02, 0.018), (SX0 + 0.012, 0.018)], 0.004), *s, 0.0003))
        for (x, y) in ((0.008, -0.016), (0.1, -0.026), (-0.052, -0.012), (0.17, -0.02)):                                       # pinos
            p.add('aco_oxidado', cil_z(0.0021, min(zs * (SW - 0.001), zs * (SW + 0.0006)), max(zs * (SW - 0.001), zs * (SW + 0.0006)), x, y, 16))
    trilho(p, 'aluminio_preto', SX0 + 0.004, SX1 - 0.008, SY_T, False)
    trilho(p, 'aluminio_preto', 0.13, SX1 - 0.006, SY_B, True)
    lado = P(); trilho(lado, 'aluminio_preto', 0.13, SX1 - 0.006, 0.0, False)                                                  # trilho curto da direita
    R = TF.translation_matrix([0, -0.001, SW]) @ TF.rotation_matrix(math.pi / 2, [1, 0, 0])
    for k, ms in lado.parts.items():
        for m in ms: p.add(k, m.apply_transform(R))
    # cano com ressalto e rosca 9 mm
    p.add('aco_cano', torno_x([(0.0, SX1 - 0.01), (0.0095, SX1 - 0.01), (0.0095, SX1 + 0.008), (0.0078, SX1 + 0.01), (0.0078, S_XM - 0.012), (0.0068, S_XM - 0.0118)], 40))
    rosca_x(p, 'aco_cano', 0.0068, S_XM - 0.0118, S_XM, 0.001)
    p.add('aco_cano', tubo_x(0.0045, 0.0068, S_XM - 0.0004, S_XM, sec=32))
    # guarda-mato e punho
    fora = arred([(0.058, -0.033), (0.118, -0.033), (0.116, -0.04), (0.104, -0.056), (0.066, -0.058), (0.056, -0.05)], 0.004)
    dentro = arred([(0.062, -0.0355), (0.111, -0.0355), (0.108, -0.041), (0.099, -0.052), (0.068, -0.054), (0.061, -0.049)], 0.003)
    p.add('polimero', solido(fora.difference(dentro), -0.0055, 0.0055, 0.0012))
    larg = lambda y: 0.0148 + 0.001 * GT.smooth(-0.04, -0.08, y)
    cabo = punho_redondo(SCABO, -0.026, -0.138, larg, n=2.5, fatias=110, voltas=56, raio_base=0.004)
    poco = solido(_paralelo(SMAG, 0.2, 0.0168), -0.0112, 0.0112)
    p.add('polimero', menos(cabo, poco))
    pont = punho_redondo(SCABO, -0.026, -0.138, lambda y: larg(y) + 0.0004, n=2.5, fatias=110, voltas=56, raio_base=0.004)
    area = solido(SCABO.buffer(-0.0035, join_style=1).intersection(sbox(-1, -0.128, 1, -0.05)), -0.05, 0.05)
    p.add('polimero_grip', menos(inter([pont, area]), poco))                                                  # pontilhado
    # retem do carregador (bota atras do guarda-mato) e trava da coronha atras
    p.add('aco_oxidado', solido(arred([(0.052, -0.036), (0.06, -0.036), (0.06, -0.044), (0.052, -0.044)], 0.0015), -0.012, 0.012, 0.0006))
    p.add('aco_oxidado', solido(arred([(SX0 - 0.002, -0.016), (SX0 + 0.006, -0.016), (SX0 + 0.006, -0.006), (SX0 - 0.002, -0.006)], 0.002), -0.008, 0.008, 0.0008))
    # argola da bandoleira (esquerda, atras)
    argola = Point(SX0 + 0.008, -0.012).buffer(0.0055, 24).difference(Point(SX0 + 0.008, -0.012).buffer(0.0033, 24))
    p.add('aco_oxidado', solido(argola, -SW - 0.004, -SW - 0.0005, 0.0006))


def _ferrolho_smg(q):
    q.add('aco_fosfatado', caixa(0.0, 0.11, 0.003, 0.0155, SW - 0.0045, SW - 0.0039))
    q.add('aco_inox', caixa(0.058, 0.07, 0.006, 0.012, SW - 0.0039, SW - 0.0033))             # extrator


def _alavanca_smg(q):
    """Alavanca de manejo em T atras, embaixo do trilho (puxa para tras)."""
    q.add('polimero', solido(arred([(SX0 - 0.012, 0.014), (SX0 - 0.002, 0.014), (SX0 - 0.002, 0.023), (SX0 - 0.012, 0.023)], 0.002), -0.025, 0.025, 0.0015))
    q.add('aco_oxidado', caixa(SX0 - 0.004, SX0 + 0.03, 0.016, 0.021, -0.003, 0.003))
    for zs in (-1, 1): q.add('polimero', solido(arred([(SX0 - 0.012, 0.0155), (SX0 - 0.006, 0.0155), (SX0 - 0.006, 0.0215), (SX0 - 0.012, 0.0215)], 0.0015),
                                               min(zs * 0.025, zs * 0.0275), max(zs * 0.025, zs * 0.0275), 0.0006))   # pegas


def _seletor_smg(q):
    """Seletor ambidestro: alavanca curta com seta, eixo em (0.012, -0.012)."""
    for zs in (-1, 1):
        lev = arred([(0.003, -0.016), (0.016, -0.0155), (0.026, -0.0105), (0.024, -0.007), (0.012, -0.0085), (0.003, -0.009)], 0.0015)
        q.add('aco_oxidado', solido(lev, min(zs * (SW + 0.0007), zs * (SW + 0.0025)), max(zs * (SW + 0.0007), zs * (SW + 0.0025)), 0.0004))
        q.add('aco_oxidado', cil_z(0.0045, min(zs * (SW + 0.0004), zs * (SW + 0.002)), max(zs * (SW + 0.0004), zs * (SW + 0.002)), 0.012, -0.012, 20))


def _coronha_smg(q):
    """Coronha de duas varetas que corre por dentro do corpo; soleira de polimero com borracha."""
    for zs in (-1, 1): q.add('aco_oxidado', cil_x(0.0042, SX0 - 0.016, SX0 + 0.05, 0.0, zs * 0.0145, 24))
    sol = arred([(SX0 - 0.018, 0.011), (SX0 - 0.004, 0.011), (SX0 - 0.004, -0.004), (SX0 - 0.01, -0.07), (SX0 - 0.018, -0.072)], 0.004)
    q.add('polimero', menos(solido(sol, -0.021, 0.021, 0.004), solido(arred([(SX0 - 0.03, -0.03), (SX0 + 0.01, -0.03), (SX0 + 0.01, -0.052), (SX0 - 0.03, -0.052)], 0.004),
                                                                        -0.0125, 0.0125)))
    q.add('borracha', solido(arred([(SX0 - 0.024, 0.011), (SX0 - 0.0175, 0.011), (SX0 - 0.0175, -0.072), (SX0 - 0.024, -0.072)], 0.003), -0.021, 0.021, 0.003))
    for y in np.arange(-0.066, 0.006, 0.006): q.add('borracha', caixa(SX0 - 0.0252, SX0 - 0.0235, y, y + 0.0025, -0.019, 0.019))


@arma('smg_9mm', 'Submetralhadora Faísca 9 mm', 'armas', 'submetralhadora', classe='fogo', calibre='9 mm', municao='municao_9mm', capacidade=30, dano=28,
      alcance_m=40, alcance_max_m=150, modo='semiautomático e automático (seletor)', tiros_por_s=14, recarga_s=1.9, recarga_vazia_s=2.4,
      precisao=0.62, recuo=0.22, ruido_m=120, durabilidade=5000, peso_kg=1.9, raridade='muito raro', valor_troca=150, onde=['quartel', 'delegacia'],
      estojo_s=0.02, descricao='Arma curta de polímero com o carregador dentro do punho e coronha de varetas que encolhe. Cabe numa mochila, '
                               'atira rápido e usa a mesma munição da pistola: ótima para limpar corredores.')
def smg_9mm(A):
    A.pivo = (0.02, -0.08, 0.0)
    _corpo_smg(A.base)
    gat = A.parte('gatilho', (0.082, -0.03, 0), explodir=(0.0, -0.05, 0), tipo='gira', eixo='z', curso_graus=-12, descricao='puxa para trás')
    _gatilho_em(gat, 0.082, -0.03)
    sel = A.parte('seletor', (0.012, -0.012, 0), explodir=(0, 0, 0.04), tipo='gira', eixo='z', curso_graus=-90,
                  descricao='seletor dos dois lados: trava (0°), semi (-45°), automático (-90°)')
    _seletor_smg(sel)
    fr = A.parte('ferrolho', (0, 0, 0), explodir=(0.0, 0.0, 0.05), tipo='desliza', curso_m=-0.035, descricao='ferrolho visto pela janela da direita')
    _ferrolho_smg(fr)
    al = A.parte('alavanca', (0, 0, 0), explodir=(-0.05, 0.03, 0), tipo='desliza', curso_m=-0.045, descricao='alavanca de manejo em T (puxa para trás)')
    _alavanca_smg(al)
    co = A.parte('coronha', (SX0, 0, 0), explodir=(-0.08, 0, 0), tipo='desliza', curso_m=-SCOR, descricao='coronha de varetas: fechada (0) ou aberta (-130 mm)')
    _coronha_smg(co)
    car = A.parte('carregador', (SMAG[0], SMAG[1], 0), explodir=(0, -0.12, 0), tipo='remove', direcao=[float(SDIR[0]), float(SDIR[1]), 0.0], municao='municao_9mm',
                  capacidade=30, descricao='carregador de 30 que entra pelo punho')
    _carregador_smg(car, 30)
    YM = SY_T + 0.0055
    A.encaixe('encaixe_mira', (0.065, YM, 0), 'trilho_mira', explodir=(0, 0.07, 0),
              aceita=['mira_holografica', 'mira_reflexa', 'mira_ponto_vermelho_tubo'], descricao='trilho de cima')
    A.encaixe('encaixe_alca', (SX0 + 0.018, YM, 0), 'alca_trilho', explodir=(-0.02, 0.05, 0), aceita=['alca_rebativel', 'alca_polimero', 'alca_polimero_tan'],
              padrao='alca_rebativel', rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira no encaixe_mira')
    A.encaixe('encaixe_massa', (SX1 - 0.022, YM, 0), 'massa_trilho', explodir=(0.02, 0.05, 0), aceita=['massa_rebativel', 'massa_polimero', 'massa_polimero_tan'],
              padrao='massa_rebativel', rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira no encaixe_mira')
    A.encaixe('encaixe_boca', (S_XM, 0, 0), 'boca_rosca_9mm', explodir=(0.06, 0, 0),
              aceita=['protetor_rosca_9mm', 'supressor_9mm', 'compensador_9mm', 'supressor_garrafa'], padrao='protetor_rosca_9mm')
    A.encaixe('encaixe_carregador', (SMAG[0], SMAG[1], 0), 'carregador_smg', pai='carregador', substitui='carregador',
              aceita=['carregador_smg_20', 'carregador_smg_30', 'carregador_smg_40'], descricao='filho do nó carregador; ao pôr um carregador aqui, esconda o original')
    A.encaixe('encaixe_empunhadura', (0.168, SY_B - 0.0055, 0), 'mlok_baixo', explodir=(0, -0.06, 0),
              aceita=['empunhadura_reta', 'empunhadura_reta_tan', 'empunhadura_curta', 'empunhadura_curta_tan', 'empunhadura_vertical', 'empunhadura_angulada',
                      'batente_mao'], descricao='trilho curto de baixo')
    A.encaixe('encaixe_lanterna', (0.17, -0.001, SW + 0.0055), 'mlok_lado', explodir=(0, 0, 0.06), aceita=['lanterna_compacta', 'lanterna_fuzil'],
              descricao='trilho curto da direita')
    A.encaixe('encaixe_laser', (0.15, -0.001, -SW), 'mlok_esq', explodir=(0, 0, -0.06), aceita=['modulo_laser', 'laser_fuzil'], descricao='lado esquerdo da frente')
    A.encaixe('encaixe_bandoleira', (SX0 + 0.008, -0.012, -SW - 0.004), 'bandoleira', explodir=(0, 0, -0.04), aceita=['bandoleira'])
    A.encaixe('ombro', (SX0 - 0.024, -0.03, 0), 'efeito', pai='coronha', descricao='ponto da soleira que encosta no ombro')
    A.encaixe('boca_fogo', (S_XM, 0, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('saida_estojo', (0.05, 0.01, SW + 0.002), 'efeito', descricao='onde nasce o estojo (sai para a direita)')
    A.encaixe('mira_ferro', (SX0 + 0.018, YM + 0.0195, 0), 'mira', descricao='centro do furo da alça: câmera de 1ª pessoa olha daqui pela ponta da massa (-Z)')
    A.anim('atirar', 0.07, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.008, -12), (0.04, -12), (0.065, 0)])),
                            ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.006, (0, 0, 0)), (0.03, (-0.035, 0, 0)), (0.06, (0, 0, 0))])),
                            (None, 'r', (0, 0, 1), pose([(0, 0), (0.008, 0), (0.025, 1.6), (0.07, 0)])),
                            (None, 't', pose([(0, (0, 0, 0)), (0.008, (0, 0, 0)), (0.025, (-0.008, 0.001, 0)), (0.07, (0, 0, 0))]))],
           desc='um tiro (repita a 14 por segundo no automático): ferrolho recua 35 mm, coice leve')
    A.anim('atirar_ultimo', 0.07, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.008, -12), (0.04, -12), (0.065, 0)])),
                                   ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.006, (0, 0, 0)), (0.03, (-0.035, 0, 0)), (0.07, (-0.035, 0, 0))]))],
           desc='último tiro: o ferrolho fica aberto atrás')
    d = SDIR
    sai = pose([(0, (0, 0, 0)), (0.2, (0, 0, 0)), (0.5, (float(d[0] * 0.22), float(d[1] * 0.22), 0)), (1.2, (float(d[0] * 0.22), float(d[1] * 0.22), 0)),
                (1.55, (0, 0, 0))])
    giro = (None, 'r', (1, 0, 0), pose([(0, 0), (0.18, -18), (1.65, -18), (1.9, 0)]))
    A.anim('recarregar', 1.9, [('carregador', 't', sai), giro], desc='aperta o retém, o carregador cai pelo punho (0,5 s) e o novo entra (1,55 s); troque o nó entre 0,5 e 1,2 s')
    A.anim('recarregar_vazia', 2.4, [('carregador', 't', sai), giro,
                                     ('ferrolho', 't', pose([(0, (-0.035, 0, 0)), (1.75, (-0.035, 0, 0)), (1.95, (0, 0, 0))])),
                                     ('alavanca', 't', pose([(0, (0, 0, 0)), (1.65, (0, 0, 0)), (1.8, (-0.045, 0, 0)), (1.95, (0, 0, 0))]))],
           desc='igual à recarga e no fim puxa a alavanca em T para soltar o ferrolho')
    A.anim('trocar_modo', 0.4, [('seletor', 'r', (0, 0, 1), pose([(0, 0), (0.15, -45), (0.25, -45), (0.4, -90)]))], desc='trava -> semi -> automático')
    A.anim('estender', 0.4, [('coronha', 't', pose([(0, (0, 0, 0)), (0.4, (-SCOR, 0, 0))]))], desc='abre a coronha (aperte a trava atrás)')
    A.anim('recolher', 0.4, [('coronha', 't', pose([(0, (-SCOR, 0, 0)), (0.4, (0, 0, 0))]))], desc='fecha a coronha')
    A.anim('inspecionar', 2.6, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -35), (1.3, -35), (1.7, 30), (2.2, 30), (2.6, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 8), (2.2, 8), (2.6, 0)])),
                                ('alavanca', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.7, (-0.02, 0, 0)), (1.0, (-0.02, 0, 0)), (1.1, (0, 0, 0))])),
                                ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.7, (-0.02, 0, 0)), (1.0, (-0.02, 0, 0)), (1.1, (0, 0, 0))]))],
           desc='puxa a alavanca até ver o cartucho pela janela, solta e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.5), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


def smg_9mm_tan(A):
    smg_9mm(A); _em_tan(A)
    for pt in A.partes:
        if pt['no'] == 'carregador': _recolore(pt['peca'], {'polimero_tan': 'polimero'})
        if pt['no'] in ('ferrolho', 'alavanca', 'seletor', 'gatilho'): _recolore(pt['peca'], {'polimero_tan': 'polimero', 'chassi_tan': 'aluminio_preto'})
    _recolore(A.base, {'chassi_tan': 'aluminio_preto'})                     # trilhos pretos


REG['smg_9mm_tan'] = dict(REG['smg_9mm'], id='smg_9mm_tan', nome='Submetralhadora Faísca 9 mm caramelo', fn=smg_9mm_tan, valor_troca=160,
                          descricao='A mesma submetralhadora com corpo, punho e coronha caramelo; carregador e trilhos pretos.')


# ---------------------------------------------------------------------------- carregadores
@_acessorio('carregador_smg_20', 'Carregador da submetralhadora (20)', 'carregador', 'carregador_smg', capacidade=20, municao='municao_9mm', peso_kg=0.1,
            raridade='incomum', valor_troca=10, modificadores={'recarga_s': 0.95}, descricao='Curto: fica rente ao fundo do punho, a arma cabe em qualquer bolso de mochila.')
def carregador_smg_20(A): _carregador_smg(A.base, 20); A.pivo = (SMAG[0], SMAG[1], 0)


@_acessorio('carregador_smg_30', 'Carregador da submetralhadora (30)', 'carregador', 'carregador_smg', capacidade=30, municao='municao_9mm', peso_kg=0.13,
            raridade='incomum', valor_troca=12, descricao='Carregador padrão de 30. Vem na arma.')
def carregador_smg_30(A): _carregador_smg(A.base, 30); A.pivo = (SMAG[0], SMAG[1], 0)


@_acessorio('carregador_smg_40', 'Carregador da submetralhadora (40)', 'carregador', 'carregador_smg', capacidade=40, municao='municao_9mm', peso_kg=0.17,
            raridade='raro', valor_troca=22, modificadores={'recarga_s': 1.08}, onde=['quartel'], descricao='Comprido: 40 tiros, mas atrapalha deitar no chão.')
def carregador_smg_40(A): _carregador_smg(A.base, 40); A.pivo = (SMAG[0], SMAG[1], 0)
