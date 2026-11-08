# Arma 9: submetralhadora Ciclone 9 mm (aceita tambor). Executado por gerar_armas.py (plano de lado: x frente, y cima, z direita).
# Desenho proprio inspirado nas fotos do Bruno: corpo de cima longo e baixo (cano alto, na linha do ombro) com guarda-mao de fendas ovais,
# chassi de baixo em V: laco do guarda-mato inclinado como o punho, painel triangular rebaixado e o carregador inclinado na frente.

CX0, CX1 = -0.112, 0.258          # corpo de cima em x (o guarda-mao vai de 0.17 ate a frente)
CY0, CY1 = -0.02, 0.022           # fundo e topo do corpo de cima (o trilho fica por cima)
CW = 0.0165                       # meia largura do corpo de cima
C_XM = 0.296                      # fim da rosca do cano (encaixe da boca)
CRAKE = math.radians(18.0)        # inclinacao do punho, do laco do guarda-mato e do carregador
GX0 = -0.036                      # frente do punho no topo
CMAG = (0.124, CY0)               # topo do carregador (centro)
CANG = CRAKE                      # carregador inclinado como o punho (embaixo vai para tras)
CDIR = np.array([-math.sin(CANG), -math.cos(CANG)])
CHX, CHY, CHZ = CX0 + 0.004, 0.004, CW + 0.004     # dobradica da coronha (lado direito)


def _carregador_ciclone(q, cap=30, mat='polimero'):
    """Carregador reto de pistola, fileira dupla, base com ressalto. cap 17 / 30."""
    L = {17: 0.098, 30: 0.162}[cap]
    corpo = _paralelo(CMAG, L, 0.0158, CDIR)
    q.add(mat, solido(arred(list(corpo.exterior.coords)[:-1], 0.0028), -0.0108, 0.0108, 0.0012))
    for zs in (-1, 1):
        nerv = _paralelo(np.array(CMAG) + CDIR * 0.07, L - 0.08, 0.0035, CDIR)
        q.add(mat, solido(arred(list(nerv.exterior.coords)[:-1], 0.003), min(zs * 0.0108, zs * 0.0114), max(zs * 0.0108, zs * 0.0114), 0.0003))
    n = np.array([-CDIR[1], CDIR[0]])
    for k in range(int((L - 0.08) / 0.02)):
        c = np.array(CMAG) + CDIR * (0.075 + k * 0.02) - n * 0.009
        q.add('aco_oxidado', cil_z(0.0015, -0.0112, -0.0106, c[0], c[1], 12))                         # furos de contagem
    fim = np.array(CMAG) + CDIR * L
    base = [fim + n * 0.0215 - CDIR * 0.001, fim - n * 0.0175 - CDIR * 0.001, fim - n * 0.0175 + CDIR * 0.0095, fim + n * 0.0225 + CDIR * 0.0095]
    q.add(mat, solido(Polygon([tuple(x) for x in base]).buffer(0.0016, join_style=1), -0.0128, 0.0128, 0.0016))
    q.merge(_cartucho_9mm_malha(16), TF.translation_matrix([CMAG[0] - 0.0105, CMAG[1] - 0.004, 0.0025]))
    for zs in (-1, 1): q.add('aco_oxidado', caixa(CMAG[0] - 0.014, CMAG[0] + 0.01, CMAG[1] - 0.003, CMAG[1] + 0.0015, zs * 0.0062 - 0.0012, zs * 0.0062 + 0.0012))


def _tambor_ciclone(q, mat='polimero'):
    """Tambor de 50: pescoco curto que entra no poco e disco de lado (eixo z) com tampa recartilhada da corda."""
    corpo = _paralelo(CMAG, 0.118, 0.0158, CDIR)
    q.add(mat, solido(arred(list(corpo.exterior.coords)[:-1], 0.0028), -0.0108, 0.0108, 0.0012))
    c = np.array(CMAG) + CDIR * 0.152; R = 0.046
    disco = torno_x([(0.0, -0.021), (R - 0.006, -0.021), (R, -0.015), (R, 0.015), (R - 0.006, 0.021), (0.0, 0.021)], 64)
    disco.apply_transform(TF.rotation_matrix(-math.pi / 2, [0, 1, 0])); disco.apply_translation([c[0], c[1], 0])
    q.add(mat, disco)
    for zs in (-1, 1):
        q.add(mat, cil_z(R - 0.008, min(zs * 0.021, zs * 0.0225), max(zs * 0.021, zs * 0.0225), c[0], c[1], 64))         # tampas
        for i in range(10):                                                                                   # nervuras radiais
            a = i * 2 * math.pi / 10
            r = caixa(0.012, R - 0.011, -0.0012, 0.0012, min(zs * 0.0225, zs * 0.0236), max(zs * 0.0225, zs * 0.0236))
            r.apply_transform(TF.rotation_matrix(a, [0, 0, 1])); r.apply_translation([c[0], c[1], 0]); q.add(mat, r)
    q.add('recartilhado', cil_z(0.011, 0.0225, 0.03, c[0], c[1], 40))                                       # botao da corda (direita)
    q.add('aco_oxidado', solido(arred([(c[0] - 0.009, c[1] - 0.0015), (c[0] + 0.009, c[1] - 0.0015), (c[0] + 0.009, c[1] + 0.0015),
                                       (c[0] - 0.009, c[1] + 0.0015)], 0.001), 0.03, 0.0315))                 # alavanca da corda
    for k in range(5):                                                                                         # janela de contagem
        a = math.radians(200 + k * 14)
        q.add('lente_clara', caixa(-0.002, 0.002, -0.0012, 0.0012, -0.0237, -0.0232).apply_transform(TF.rotation_matrix(a, [0, 0, 1]))
              .apply_translation([c[0] + 0.033 * math.cos(a), c[1] + 0.033 * math.sin(a), 0]))
    q.merge(_cartucho_9mm_malha(16), TF.translation_matrix([CMAG[0] - 0.0105, CMAG[1] - 0.004, 0.0025]))


def _corpo_ciclone(p, mat_c='aluminio_preto', mat_b='polimero'):
    # ---- corpo de cima: caixa longa e baixa, guarda-mao com 2 fileiras de fendas ovais, janela grande do estojo a direita
    lado = arred([(CX0, CY1), (CX1, CY1), (CX1, CY0 + 0.004), (CX1 - 0.004, CY0), (CX0 + 0.004, CY0), (CX0, CY0 + 0.004)], 0.002)
    sec = Polygon([(-CW, CY0), (CW, CY0), (CW, CY1 - 0.004), (CW - 0.004, CY1), (-CW + 0.004, CY1), (-CW, CY1 - 0.004)])
    corpo = inter([solido(lado, -CW, CW), ext_x(sec, CX0 - 0.01, CX1 + 0.01)])
    cortes = [solido(arred([(0.098, -0.011), (0.142, -0.011), (0.142, 0.013), (0.098, 0.013)], 0.002), CW - 0.006, CW + 0.01)]   # janela do estojo
    for zs in (-1, 1):
        zz = (min(zs * (CW - 0.0018), zs * (CW + 0.01)), max(zs * (CW - 0.0018), zs * (CW + 0.01)))
        for x0 in (0.176, 0.206):                                                                         # fendas ovais do guarda-mao
            for (y0, y1) in ((0.004, 0.012), (-0.012, -0.004)):
                cortes.append(solido(arred([(x0, y0), (x0 + 0.024, y0), (x0 + 0.024, y1), (x0, y1)], 0.0039), *zz))
        cortes.append(solido(arred([(0.236, 0.004), (0.25, 0.004), (0.25, 0.012), (0.236, 0.012)], 0.0039), *zz))
        cortes.append(solido(arred([(0.158, -0.0025), (0.168, -0.0025), (0.168, 0.0025), (0.158, 0.0025)], 0.0024), *zz))     # furo pequeno
        cortes.append(solido(arred([(CX0 + 0.02, 0.0115), (0.09, 0.0115), (0.09, 0.0135), (CX0 + 0.02, 0.0135)], 0.0008),
                             min(zs * (CW - 0.0006), zs * (CW + 0.01)), max(zs * (CW - 0.0006), zs * (CW + 0.01))))          # emenda de cima
    cortes.append(solido(arred([(0.03, -0.0065), (0.095, -0.0065), (0.095, -0.0015), (0.03, -0.0015)], 0.0015), -CW - 0.01, -CW + 0.0018))  # trilho da alavanca (esq.)
    p.add(mat_c, menos(corpo, *cortes))
    trilho(p, mat_c, CX0 + 0.004, CX1 - 0.004, CY1, False)
    trilho(p, mat_c, 0.178, CX1 - 0.004, CY0, True)
    # cano com porca e rosca 9 mm
    p.add('aco_cano', torno_x([(0.0, CX1 - 0.01), (0.0105, CX1 - 0.01), (0.0105, CX1 + 0.008), (0.0078, CX1 + 0.011), (0.0078, C_XM - 0.012), (0.0068, C_XM - 0.0118)], 40))
    rosca_x(p, 'aco_cano', 0.0068, C_XM - 0.0118, C_XM, 0.001)
    p.add('aco_cano', tubo_x(0.0045, 0.0068, C_XM - 0.0004, C_XM, sec=32))
    # ---- corpo de baixo (polimero): placa alta com o laco do guarda-mato (paralelogramo inclinado como o punho),
    #      barra de baixo, poco do carregador inclinado na frente e o painel triangular rebaixado
    t = math.tan(CRAKE)
    gx = lambda y: GX0 - (CY0 - y) * t                       # frente do punho em cada altura
    fr_x = lambda y: CMAG[0] + 0.0222 - (CY0 - y) * t          # frente do chassi: segue a frente do carregador
    fora = [(GX0 - 0.046, CY0 + 0.001), (fr_x(CY0) + 0.004, CY0 + 0.001), (fr_x(-0.116), -0.116), (fr_x(-0.116) - 0.03, -0.12),
            (0.04, -0.124), (gx(-0.128) - 0.004, -0.13), (gx(-0.128) - 0.012, -0.1)]
    chassi = arred(fora, 0.0035)
    ya, yb = -0.035, -0.114
    laco = arred([(gx(ya) + 0.004, ya), (0.022, ya), (0.022 - (yb - ya) * -t, yb), (gx(yb) + 0.004, yb)], 0.006)
    poco = _paralelo(CMAG, 0.3, 0.0166, CDIR)
    m_ch = menos(solido(chassi, -CW + 0.0006, CW - 0.0006, 0.0022), solido(laco, -0.05, 0.05), solido(poco, -0.0114, 0.0114))
    # barra de baixo e frente do laco mais finas que o corpo
    barra = Polygon([(gx(yb) - 0.02, yb - 0.0005), (0.06, yb - 0.0005), (0.075, -0.15), (gx(yb) - 0.02, -0.15)])
    finos = [solido(barra, 0.0078, 0.05), solido(barra, -0.05, -0.0078)]
    # painel triangular rebaixado nos dois lados (ponta para baixo) e chanfro em V ao redor
    tri = Polygon([(0.034, -0.03), (0.1, -0.03), (0.06, -0.1)]).buffer(-0.004, join_style=2).buffer(0.002)
    for zs in (-1, 1):
        finos.append(solido(tri, min(zs * (CW - 0.0018), zs * (CW + 0.01)), max(zs * (CW - 0.0018), zs * (CW + 0.01))))
    p.add(mat_b, menos(m_ch, *finos))
    for zs in (-1, 1):                                                                                     # fundo do painel com textura
        p.add('polimero_pontos' if mat_b == 'polimero' else 'polimero_pontos_tan',
              solido(tri.buffer(-0.0005), min(zs * (CW - 0.0019), zs * (CW - 0.0017)), max(zs * (CW - 0.0019), zs * (CW - 0.0017))))
    # punho inclinado com pontilhado
    CAB = suave([(GX0 - 0.046, CY0), (GX0, CY0), (gx(-0.05), -0.05), (gx(-0.1) - 0.002, -0.1), (gx(-0.128) - 0.003, -0.128), (gx(-0.138) - 0.008, -0.138),
                 (gx(-0.138) - 0.038, -0.138), (gx(-0.13) - 0.044, -0.13), (gx(-0.08) - 0.044, -0.08), (GX0 - 0.044, -0.03)], 3)
    larg = lambda y: 0.0128 + 0.0016 * GT.smooth(-0.035, -0.06, y)
    p.add(mat_b, punho_redondo(CAB, CY0, -0.138, larg, n=2.6, fatias=100, voltas=52, raio_base=0.004))
    pont = punho_redondo(CAB, CY0, -0.138, lambda y: larg(y) + 0.0004, n=2.6, fatias=100, voltas=52, raio_base=0.004)
    area = solido(CAB.buffer(-0.0035, join_style=1).intersection(sbox(-1, -0.13, 1, -0.045)), -0.05, 0.05)
    p.add('polimero_pontos' if mat_b == 'polimero' else 'polimero_pontos_tan', inter([pont, area]))
    # pinos e parafusos, retem do carregador, base da dobradica, argola
    for zs in (-1, 1):
        for (x, y, z) in ((GX0 - 0.03, -0.006, CW), (0.03, -0.006, CW), (0.075, 0.004, CW), (0.155, -0.008, CW), (0.215, -0.016, CW),
                          (0.088, -0.108, CW - 0.0006), (0.035, -0.11, 0.0078), (0.006, -0.04, CW - 0.0006)):
            p.add('aco_oxidado', cil_z(0.0024, min(zs * (z - 0.001), zs * (z + 0.0006)), max(zs * (z - 0.001), zs * (z + 0.0006)), x, y, 16))
        p.add('aco_oxidado', solido(arred([(0.024, -0.042), (0.03, -0.042), (0.03, -0.052), (0.024, -0.052)], 0.0015),
                                    min(zs * 0.005, zs * (CW - 0.0003)), max(zs * 0.005, zs * (CW - 0.0003)), 0.0005))    # retem do carregador
    p.add(mat_c, caixa(CX0 - 0.006, CX0 + 0.012, -0.012, 0.016, CW - 0.002, CHZ + 0.0035))                                      # bloco da dobradica
    p.add('aco_oxidado', _cil_y(0.0035, -0.014, 0.018, CHX, CHZ, 20))
    argola = Point(0.0, 0.0).buffer(0.0055, 24).difference(Point(0.0, 0.0).buffer(0.0033, 24))
    p.add('aco_oxidado', solido(affinity.translate(argola, CX0 + 0.012, -0.006), -CW - 0.004, -CW - 0.0005, 0.0006))   # argola esquerda


def _coronha_ciclone(q, mat='polimero'):
    """Coronha de esqueleto: barra de cima reta (apoio do rosto), barra de baixo inclinada, soleira com borracha."""
    X, Z = CHX, 0.0                     # aberta fica no meio; dobrada fica do lado direito
    sup = LineString([(X - 0.004, 0.011), (X - 0.22, 0.011)]).buffer(0.0085, cap_style=2)
    inf = LineString([(X - 0.004, -0.006), (X - 0.08, -0.03), (X - 0.2, -0.06)]).buffer(0.0068, cap_style=1, join_style=1)
    sol = arred([(X - 0.232, 0.019), (X - 0.212, 0.019), (X - 0.212, -0.075), (X - 0.232, -0.075)], 0.004)
    furo = arred([(X - 0.229, 0.002), (X - 0.216, 0.002), (X - 0.216, -0.05), (X - 0.229, -0.05)], 0.004)
    q.add(mat, solido(unary_union([sup, inf, sol.difference(furo)]), Z - 0.011, Z + 0.011, 0.003))
    q.add('borracha', solido(arred([(X - 0.239, 0.019), (X - 0.231, 0.019), (X - 0.231, -0.075), (X - 0.239, -0.075)], 0.003), Z - 0.0145, Z + 0.0145, 0.003))
    for y in np.arange(-0.07, 0.016, 0.006): q.add('borracha', caixa(X - 0.2405, X - 0.2385, y, y + 0.0025, Z - 0.0125, Z + 0.0125))
    q.add(mat, caixa(X - 0.014, X + 0.004, -0.008, 0.016, -0.011, CHZ + 0.0055))                                # cabeca da dobradica
    q.add('aco_oxidado', cil_z(0.0032, CHZ + 0.0055, CHZ + 0.007, X - 0.006, 0.004, 16))                                # botao da trava


@arma('smg_ciclone_9mm', 'Submetralhadora Ciclone 9 mm', 'armas', 'submetralhadora', classe='fogo', calibre='9 mm', municao='municao_9mm', capacidade=30,
      dano=28, alcance_m=40, alcance_max_m=150, modo='semiautomático, rajada de 2 e automático', tiros_por_s=18, recarga_s=2.0, recarga_vazia_s=2.5,
      precisao=0.66, recuo=0.16, ruido_m=120, durabilidade=6000, peso_kg=2.7, raridade='muito raro', valor_troca=190, onde=['quartel'],
      estojo_s=0.02, descricao='Submetralhadora de cano alto, na linha do ombro: o coice vai reto para trás e quase não levanta. Atira muito rápido, '
                               'aceita carregador de pistola longo e o tambor de 50. A coronha dobra para o lado.')
def smg_ciclone_9mm(A):
    A.pivo = (GX0 - 0.022, -0.08, 0.0)
    _corpo_ciclone(A.base)
    gat = A.parte('gatilho', (-0.012, -0.028, 0), explodir=(0.0, -0.05, 0), tipo='gira', eixo='z', curso_graus=-12, descricao='puxa para trás')
    _gatilho_em(gat, -0.012, -0.028)
    sel = A.parte('seletor', (-0.05, -0.008, 0), explodir=(0, 0, 0.04), tipo='gira', eixo='z', curso_graus=-120,
                  descricao='dos dois lados: trava (0°), semi (-40°), rajada de 2 (-80°), automático (-120°)')
    for zs in (-1, 1):
        lev = arred([(-0.056, -0.012), (-0.036, -0.011), (-0.028, -0.007), (-0.034, -0.004), (-0.056, -0.004)], 0.0015)
        sel.add('aco_oxidado', solido(lev, min(zs * (CW + 0.0006), zs * (CW + 0.0024)), max(zs * (CW + 0.0006), zs * (CW + 0.0024)), 0.0004))
        sel.add('aco_oxidado', cil_z(0.0048, min(zs * (CW - 0.0004), zs * (CW + 0.0018)), max(zs * (CW - 0.0004), zs * (CW + 0.0018)), -0.05, -0.008, 20))
    fr = A.parte('ferrolho', (0, 0, 0), explodir=(0.0, 0.0, 0.05), tipo='desliza', curso_m=-0.04, descricao='ferrolho visto pela janela da direita')
    fr.add('aco_fosfatado', caixa(0.06, 0.15, -0.0105, 0.0125, CW - 0.0062, CW - 0.0056)); fr.add('aco_inox', caixa(0.128, 0.14, -0.002, 0.004, CW - 0.0056, CW - 0.005))
    al = A.parte('alavanca', (0, 0, 0), explodir=(0, 0, -0.05), tipo='desliza', curso_m=-0.06, descricao='alavanca de manejo dobrável do lado esquerdo')
    al.add('aco_oxidado', caixa(0.085, 0.093, -0.0058, -0.0022, -CW + 0.0005, -CW + 0.0025))
    al.add(  'polimero', solido(arred([(0.083, -0.008), (0.097, -0.008), (0.097, 0.0005), (0.083, 0.0005)], 0.002), -CW - 0.012, -CW + 0.0005, 0.0015))   # pega
    co = A.parte('coronha', (CHX, CHY, CHZ), explodir=(-0.08, 0, 0), tipo='gira', eixo='y', curso_graus=180, descricao='coronha de esqueleto: dobra para a direita (180°)')
    _coronha_ciclone(co)
    car = A.parte('carregador', (CMAG[0], CMAG[1], 0), explodir=(0, -0.12, 0), tipo='remove', direcao=[float(CDIR[0]), float(CDIR[1]), 0.0], municao='municao_9mm',
                  capacidade=30, descricao='carregador de 30 na frente do guarda-mato')
    _carregador_ciclone(car, 30)
    YM = CY1 + 0.0055
    A.encaixe('encaixe_mira', (0.03, YM, 0), 'trilho_mira', explodir=(0, 0.07, 0),
              aceita=['mira_holografica', 'mira_reflexa', 'mira_ponto_vermelho_tubo', 'luneta_1_6'], descricao='trilho de cima')
    A.encaixe('encaixe_alca', (CX0 + 0.018, YM, 0), 'alca_trilho', explodir=(-0.02, 0.05, 0), aceita=['alca_rebativel', 'alca_polimero', 'alca_polimero_tan'],
              padrao='alca_rebativel', rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira no encaixe_mira')
    A.encaixe('encaixe_massa', (CX1 - 0.016, YM, 0), 'massa_trilho', explodir=(0.02, 0.05, 0), aceita=['massa_rebativel', 'massa_polimero', 'massa_polimero_tan'],
              padrao='massa_rebativel', rebate_com='encaixe_mira', descricao='deita (animação "dobrar" do acessório) quando há mira no encaixe_mira')
    A.encaixe('encaixe_boca', (C_XM, 0, 0), 'boca_rosca_9mm', explodir=(0.06, 0, 0),
              aceita=['protetor_rosca_9mm', 'supressor_9mm', 'supressor_9mm_tan', 'supressor_9mm_verde', 'supressor_9mm_cinza', 'compensador_9mm', 'supressor_garrafa'],
              padrao='protetor_rosca_9mm')
    A.encaixe('encaixe_carregador', (CMAG[0], CMAG[1], 0), 'carregador_ciclone', pai='carregador', substitui='carregador',
              aceita=['carregador_ciclone_30', 'carregador_ciclone_17', 'tambor_ciclone_50'], descricao='filho do nó carregador; ao pôr um carregador aqui, esconda o original')
    A.encaixe('encaixe_empunhadura', (0.218, CY0 - 0.0055, 0), 'mlok_baixo', explodir=(0, -0.06, 0),
              aceita=['empunhadura_reta', 'empunhadura_reta_tan', 'empunhadura_curta', 'empunhadura_curta_tan', 'empunhadura_dobravel', 'empunhadura_vertical', 'batente_mao'],
              padrao='empunhadura_reta', descricao='trilho curto de baixo')
    A.encaixe('encaixe_lanterna', (0.2, 0.0, CW + 0.0005), 'mlok_lado', explodir=(0, 0, 0.06), aceita=['lanterna_compacta', 'lanterna_fuzil'], descricao='lado direito do guarda-mão')
    A.encaixe('encaixe_laser', (0.2, 0.0, -CW - 0.0005), 'mlok_esq', explodir=(0, 0, -0.06), aceita=['modulo_laser', 'modulo_laser_tan', 'laser_fuzil'], descricao='lado esquerdo da frente')
    A.encaixe('encaixe_bandoleira', (CX0 + 0.012, -0.006, -CW - 0.004), 'bandoleira', explodir=(0, 0, -0.04), aceita=['bandoleira'])
    A.encaixe('ombro', (CHX - 0.239, -0.03, 0), 'efeito', pai='coronha', descricao='ponto da soleira que encosta no ombro')
    A.encaixe('boca_fogo', (C_XM, 0, 0), 'efeito', descricao='clarão de boca e origem do disparo (-Z)')
    A.encaixe('saida_estojo', (0.12, 0.004, CW + 0.002), 'efeito', descricao='onde nasce o estojo (sai para a direita)')
    A.encaixe('mira_ferro', (CX0 + 0.018, YM + 0.0195, 0), 'mira', descricao='centro do furo da alça: câmera de 1ª pessoa olha daqui pela ponta da massa (-Z)')
    A.anim('atirar', 0.055, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.006, -12), (0.03, -12), (0.05, 0)])),
                             ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.005, (0, 0, 0)), (0.024, (-0.04, 0, 0)), (0.048, (0, 0, 0))])),
                             (None, 't', pose([(0, (0, 0, 0)), (0.006, (0, 0, 0)), (0.02, (-0.007, 0.0003, 0)), (0.055, (0, 0, 0))])),
                             (None, 'r', (0, 0, 1), pose([(0, 0), (0.006, 0), (0.02, 0.6), (0.055, 0)]))],
           desc='um tiro (repita a 18 por segundo no automático): ferrolho recua 40 mm; o coice vai reto para trás e quase não levanta')
    A.anim('atirar_ultimo', 0.06, [('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.006, -12), (0.03, -12), (0.05, 0)])),
                                   ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.005, (0, 0, 0)), (0.024, (-0.04, 0, 0)), (0.06, (-0.04, 0, 0))]))],
           desc='último tiro: o ferrolho fica aberto atrás')
    d = CDIR
    sai = pose([(0, (0, 0, 0)), (0.2, (0, 0, 0)), (0.5, (float(d[0] * 0.24), float(d[1] * 0.24), 0)), (1.25, (float(d[0] * 0.24), float(d[1] * 0.24), 0)),
                (1.6, (0, 0, 0))])
    giro = (None, 'r', (1, 0, 0), pose([(0, 0), (0.18, -20), (1.7, -20), (2.0, 0)]))
    A.anim('recarregar', 2.0, [('carregador', 't', sai), giro], desc='aperta o retém atrás do poço, o carregador cai (0,5 s) e o novo entra (1,6 s); troque o nó entre 0,5 e 1,25 s')
    A.anim('recarregar_vazia', 2.5, [('carregador', 't', sai), giro,
                                     ('ferrolho', 't', pose([(0, (-0.04, 0, 0)), (1.85, (-0.04, 0, 0)), (2.05, (0, 0, 0))])),
                                     ('alavanca', 't', pose([(0, (0, 0, 0)), (1.7, (0, 0, 0)), (1.85, (-0.06, 0, 0)), (2.0, (0, 0, 0))]))],
           desc='igual à recarga e no fim puxa a alavanca da esquerda para soltar o ferrolho')
    A.anim('trocar_modo', 0.5, [('seletor', 'r', (0, 0, 1), pose([(0, 0), (0.12, -40), (0.2, -40), (0.32, -80), (0.4, -80), (0.5, -120)]))],
           desc='trava -> semi -> rajada -> automático')
    A.anim('dobrar_coronha', 0.5, [('coronha', 'r', (0, 1, 0), pose([(0, 0), (0.5, 180)]))], desc='dobra a coronha para a direita (aperte o botão da dobradiça)')
    A.anim('abrir_coronha', 0.5, [('coronha', 'r', (0, 1, 0), pose([(0, 180), (0.5, 0)]))], desc='abre a coronha')
    A.anim('inspecionar', 2.6, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -35), (1.3, -35), (1.7, 30), (2.2, 30), (2.6, 0)])),
                                (None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 8), (2.2, 8), (2.6, 0)])),
                                ('alavanca', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.7, (-0.025, 0, 0)), (1.0, (-0.025, 0, 0)), (1.1, (0, 0, 0))])),
                                ('ferrolho', 't', pose([(0, (0, 0, 0)), (0.5, (0, 0, 0)), (0.7, (-0.025, 0, 0)), (1.0, (-0.025, 0, 0)), (1.1, (0, 0, 0))]))],
           desc='puxa a alavanca até ver o cartucho pela janela, solta e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.5), (3.0, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))], laco=True, desc='respiração leve parado')


def smg_ciclone_9mm_tan(A):
    """Chassi, punho e coronha areia; corpo de cima, trilhos e carregador pretos."""
    smg_ciclone_9mm(A)
    _recolore(A.base, {'polimero': 'polimero_tan', 'polimero_pontos': 'polimero_pontos_tan'})
    for pt in A.partes:
        if pt['no'] == 'coronha': _recolore(pt['peca'], {'polimero': 'polimero_tan'})


REG['smg_ciclone_9mm_tan'] = dict(REG['smg_ciclone_9mm'], id='smg_ciclone_9mm_tan', nome='Submetralhadora Ciclone 9 mm (areia)', fn=smg_ciclone_9mm_tan,
                                  valor_troca=200, descricao='A mesma Ciclone com chassi, punho e coronha cor de areia; corpo de cima e carregador pretos.')


@_acessorio('carregador_ciclone_17', 'Carregador da Ciclone (17)', 'carregador', 'carregador_ciclone', capacidade=17, municao='municao_9mm', peso_kg=0.09,
            raridade='incomum', valor_troca=8, modificadores={'recarga_s': 0.95}, descricao='Carregador curto de pistola: some dentro do poço, a arma fica baixa.')
def carregador_ciclone_17(A): _carregador_ciclone(A.base, 17); A.pivo = (CMAG[0], CMAG[1], 0)


@_acessorio('carregador_ciclone_30', 'Carregador da Ciclone (30)', 'carregador', 'carregador_ciclone', capacidade=30, municao='municao_9mm', peso_kg=0.14,
            raridade='incomum', valor_troca=12, descricao='Carregador longo de 30. Vem na arma.')
def carregador_ciclone_30(A): _carregador_ciclone(A.base, 30); A.pivo = (CMAG[0], CMAG[1], 0)


@_acessorio('tambor_ciclone_50', 'Tambor da Ciclone (50)', 'carregador', 'carregador_ciclone', capacidade=50, municao='municao_9mm', peso_kg=0.55,
            raridade='muito raro', valor_troca=45, modificadores={'recarga_s': 1.25, 'tempo_mirar': 1.08}, onde=['quartel'],
            descricao='Tambor de 50 tiros com botão de corda do lado e janelinha de contagem. Pesa e demora para trocar, mas segura uma horda.')
def tambor_ciclone_50(A): _tambor_ciclone(A.base); A.pivo = (CMAG[0], CMAG[1], 0)
