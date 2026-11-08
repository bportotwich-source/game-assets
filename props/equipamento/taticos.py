# Coletes taticos (espaco "colete_tatico"): cada um abre a propria grade no inventario ("grade") e diz como ela se divide nas
# bolsas do modelo ("bolsos"). Vao por cima do colete de protecao (k maior que o dos coletes). Exportados deitados (DEITAR).

def _bolsa_em(p, T, u, y, k, fazer, gira=0.0):
    q = P(); fazer(q); p.merge(q, T.quadro(u, y, k) @ TF.rotation_matrix(gira, [0, 0, 1]))


def _bolsos(*pares):
    return [{'nome': n, 'celulas': c} for n, c in pares]


# ---------------------------------------------------------------------------- peitoral leve (chest rig)
@equip('peitoral_carregadores', 'Peitoral de carregadores', 'colete_tatico', valor=2, peso_kg=0.9, celulas=[3, 2], raridade='incomum', fase=2,
       onde=['delegacia', 'armazem', 'casas', 'estacao'], grade=[4, 2],
       bolsos=_bolsos(('porta-carregador 1', [1, 2]), ('porta-carregador 2', [1, 2]), ('porta-carregador 3', [1, 2]), ('porta-carregador 4', [1, 2])),
       protecao=0, penalidade={}, valor_troca=35,
       efeito='grade de 4 × 2 no peito (quatro porta-carregadores de 1 × 2); recarregar daqui é mais rápido que da mochila')
def peitoral_carregadores(M):
    p = M.base; T = Tronco(A=0.2, B=0.15); tec = 'cordura_coiote'; k = 0.0
    pn = ret_arred(-0.15, 0.15, 0.1, 0.27, 0.02)
    p.add(tec, painel(T, pn, k, 0.012, infla=0.003)); cinta_borda(p, T, 'nylon_coiote', pn, k + 0.002, 0.003, 120)
    for i, u in enumerate((-0.105, -0.035, 0.035, 0.105)):
        _bolsa_em(p, T, u, 0.115, k + 0.012, lambda q: bolsa_carregador(q, tec, 0.064, 0.115, 0.034, tampa=(i in (0, 3))))
    p.add('velcro_coiote', painel(T, ret_arred(-0.13, 0.13, 0.245, 0.262, 0.003), k + 0.0125, 0.0018, passo=0.02))
    # arnes em H: alcas finas por cima dos ombros que cruzam em X nas costas, cinta de cintura
    C = T.costas()
    for lado in (-1, 1):
        a = T.pt(lado * 0.12, 0.26, 0.008); b = T.pt(C + lado * 0.1, 0.06, 0.004)
        pts = curva([a, a + [0, 0.06, -0.03], (lado * 0.1, 0.5, 0.0), (lado * 0.05, 0.4, -0.15), (0.0, 0.25, -0.16), b], 50)
        N = nrm((pts - [0, 0.25, 0]) * [0.4, 1, 1])
        p.add('nylon_coiote', fita(pts, N, 0.035, 0.004))
        q = P(); q.cham('nylon_preto', -0.022, 0.022, -0.008, 0.008, 0.0, 0.006, 0.002); p.merge(q, quadro(pts[4] + N[4] * 0.003, N[4], nrm(pts[6] - pts[2])))
        u = np.linspace(lado * 0.15, lado * (C - 0.02), 40)
        p.add('nylon_coiote', fita(T.pt(u, 0.15, 0.004), T.normal(u), 0.025, 0.003, lat=np.tile([0, 1.0, 0], (40, 1))))
        q = P(); fivela(q, (0.0, 0.0, 0.0), 0.025); p.merge(q, T.quadro(lado * 0.22, 0.15, 0.007))
    _vestir_peito(M, 0.3, 'por cima do colete: gire girar_graus e ponha peito_m no centro do peito (já está afastado para caber o colete)')


# ---------------------------------------------------------------------------- colete de pesca (civil, muitos bolsos)
@equip('colete_pesca', 'Colete de pesca multibolsos', 'colete_tatico', valor=1, peso_kg=0.6, celulas=[3, 2], raridade='comum', fase=1,
       onde=['casas', 'casa_de_campo', 'casa_barcos', 'garagem', 'galeria', 'fazenda'], grade=[5, 2],
       bolsos=_bolsos(*[(f'bolso {i + 1}', [1, 1]) for i in range(10)]), protecao=3, penalidade={}, valor_troca=10,
       efeito='grade de 5 × 2 de bolsinhos de 1 × 1 (bom para munição, remédio e ferramentas pequenas); quase não protege')
def colete_pesca(M):
    p = M.base; T = Tronco(A=0.18, B=0.13); C = T.costas(); tec = 'cordura_caqui'
    cava = lambda lado: SPoint(lado * 0.27, 0.36).buffer(0.085, quad_segs=10)
    for lado in (-1, 1):
        a, b = sorted((lado * 0.012, lado * 0.25))
        meia = SPoly([(a, 0.0), (b, 0.0), (b, 0.44), (a, 0.44)]).difference(cava(lado)).difference(SPoint(0, 0.47).buffer(0.095, quad_segs=10))
        meia = meia.buffer(-0.01).buffer(0.01, quad_segs=4)
        p.add(tec, painel(T, meia, 0.002, 0.004, passo=0.014)); cinta_borda(p, T, 'nylon_coiote', meia, 0.003, 0.0028, 150)
        # bolsos: 3 grandes embaixo (2 com tampa, 1 de ziper), 2 no peito
        _bolsa_em(p, T, lado * 0.075, 0.03, 0.006, lambda q: bolsa_tampa(q, tec, 0.085, 0.1, 0.03, velcro=tec))
        _bolsa_em(p, T, lado * 0.175, 0.03, 0.006, lambda q: bolsa_tampa(q, tec, 0.08, 0.1, 0.028, ziper=True, velcro=tec))
        _bolsa_em(p, T, lado * 0.07, 0.165, 0.006, lambda q: bolsa_tampa(q, tec, 0.075, 0.085, 0.024, velcro=tec))
        _bolsa_em(p, T, lado * 0.06, 0.28, 0.006, lambda q: bolsa_tampa(q, tec, 0.06, 0.07, 0.018, ziper=True, velcro=tec))
        _bolsa_em(p, T, lado * 0.15, 0.17, 0.006, lambda q: bolsa_pistola(q, tec, 0.04, 0.08, 0.022))
        q = P(); anel(q, 'aluminio_escuro', 0.008, 0.0105, -0.0015, 0.0015, 16, 'z'); p.merge(q, T.quadro(lado * 0.12, 0.38, 0.008))   # argola
    # ziper do meio, gola e costas de tela
    for lado in (-1, 1):
        p.add('nylon_preto', painel(T, ret_arred(min(0, lado * 0.014), max(0, lado * 0.014), 0.0, 0.42, 0.002), 0.004, 0.003, passo=0.02))
    for y in np.arange(0.01, 0.42, 0.006):
        q = P(); q.box('aluminio_escuro', -0.006, 0.006, 0.0, 0.003, 0.0, 0.0035); p.merge(q, T.quadro(0.0, y, 0.004))
    q = P(); q.cham('aluminio_escuro', -0.005, 0.005, 0.0, 0.02, 0.0, 0.006, 0.0015); p.merge(q, T.quadro(0.006, 0.36, 0.006))
    costas = affinity.translate(SPoly([(-0.17, 0.0), (0.17, 0.0), (0.17, 0.3), (0.12, 0.46), (-0.12, 0.46), (-0.17, 0.3)]), C, 0).buffer(-0.01).buffer(0.01, quad_segs=4)
    p.add('malha_caqui', painel(T, costas, 0.002, 0.003, passo=0.016))
    p.add(tec, painel(T, affinity.translate(ret_arred(-0.17, 0.17, 0.0, 0.08, 0.008), C, 0), 0.003, 0.004, passo=0.02))        # bolsa das costas
    for lado in (-1, 1):
        pts, N = alca_ombro(p, T, tec, lado, 0.13, 0.4, 0.11, 0.44, 0.003, w=0.06, t=0.004, x_ombro=0.12, y_ombro=0.5)
        tira_lateral(p, T, tec, lado, 0.24, C - 0.16, 0.0, 0.2, 0.001, 0.003)
    _vestir_peito(M, 0.3, 'vestido sem colete de proteção por baixo: gire girar_graus e ponha peito_m no centro do peito')


# ---------------------------------------------------------------------------- colete de carga (tela, medio)
@equip('colete_carga', 'Colete de carga de tela', 'colete_tatico', valor=2, peso_kg=1.4, celulas=[3, 3], raridade='incomum', fase=2,
       onde=['delegacia', 'armazem', 'estacao', 'quartel'], grade=[4, 3],
       bolsos=_bolsos(('porta-carregador duplo esquerdo', [2, 2]), ('porta-carregador duplo direito', [2, 2]), ('rádio', [1, 1]),
                      ('lanterna', [1, 1]), ('utilitária esquerda', [1, 1]), ('utilitária direita', [1, 1])),
       protecao=4, penalidade={}, valor_troca=45,
       efeito='grade de 4 × 3: dois porta-carregadores duplos (2 × 2), rádio, lanterna e duas utilitárias de 1 × 1')
def colete_carga(M):
    p = M.base; T = Tronco(A=0.2, B=0.152); C = T.costas(); tec = 'cordura_preta'; k = 0.0
    cava = lambda lado: SPoint(lado * 0.29, 0.36).buffer(0.09, quad_segs=10)
    for lado in (-1, 1):
        a, b = sorted((lado * 0.01, lado * 0.27))
        meia = SPoly([(a, 0.0), (b, 0.0), (b, 0.43), (a, 0.43)]).difference(cava(lado)).difference(SPoint(0, 0.47).buffer(0.1, quad_segs=10))
        meia = meia.buffer(-0.01).buffer(0.01, quad_segs=4)
        p.add('malha_preta', painel(T, meia, k, 0.004, passo=0.016)); cinta_borda(p, T, 'nylon_preto', meia, k + 0.002, 0.0035, 150)
        # duas fileiras de bolsas
        for j, u in enumerate((0.065, 0.165)):
            _bolsa_em(p, T, lado * u, 0.035, k + 0.004, lambda q: bolsa_carregador(q, tec, 0.09, 0.12, 0.042, mags=2, tampa=True))
        _bolsa_em(p, T, lado * 0.065, 0.23, k + 0.004, lambda q: bolsa_tampa(q, tec, 0.075, 0.075, 0.035, velcro='velcro_preto'))
        if lado > 0:
            _bolsa_em(p, T, 0.17, 0.215, k + 0.004, lambda q: (bolsa_tampa(q, tec, 0.065, 0.11, 0.04, fivela=True), cyl_eixo(q, 'pc_preto', 0.006, 0.11, 0.2, 'y', (0.018, 0, 0.02), 10), cyl_eixo(q, 'pc_preto', 0.004, 0.2, 0.25, 'y', (0.018, 0, 0.02), 8)))
        else:
            def lant(q):
                bolsa_corpo(q, tec, 0.04, 0.09, 0.036)
                cyl_eixo(q, 'aluminio_escuro', 0.015, 0.07, 0.115, 'y', (0, 0, 0.018), 18); cyl_eixo(q, 'aluminio_escuro', 0.017, 0.105, 0.125, 'y', (0, 0, 0.018), 18)
                q.add('elastico_preto', tubo(curva([(-0.02, 0.08, 0.02), (0, 0.084, 0.04), (0.02, 0.08, 0.02)], 12), 0.0022))
            _bolsa_em(p, T, -0.17, 0.215, k + 0.004, lant)
    for y in np.arange(0.01, 0.42, 0.006):
        q = P(); q.box('nylon_preto', -0.007, 0.007, 0.0, 0.003, 0.0, 0.0035); p.merge(q, T.quadro(0.0, y, k + 0.003))
    costas = affinity.translate(SPoly([(-0.18, 0.0), (0.18, 0.0), (0.18, 0.3), (0.13, 0.46), (-0.13, 0.46), (-0.18, 0.3)]), C, 0).buffer(-0.01).buffer(0.01, quad_segs=4)
    p.add('malha_preta', painel(T, costas, k, 0.004, passo=0.016)); cinta_borda(p, T, 'nylon_preto', costas, k + 0.002, 0.0035, 150)
    _bolsa_em(p, T, C, 0.05, k + 0.004, lambda q: bolsa_tampa(q, tec, 0.2, 0.14, 0.05, velcro='velcro_preto', ziper=True))          # bolsa das costas
    for lado in (-1, 1):
        alca_ombro(p, T, tec, lado, 0.14, 0.4, 0.11, 0.44, 0.004, w=0.06, t=0.01, x_ombro=0.13, y_ombro=0.52)
        tira_lateral(p, T, 'nylon_preto', lado, 0.26, C - 0.17, 0.04, 0.09, 0.001, 0.003)
        tira_lateral(p, T, 'nylon_preto', lado, 0.26, C - 0.17, 0.14, 0.19, 0.001, 0.003)
        q = P(); fivela(q, (0.0, 0.0, 0.0), 0.05); p.merge(q, T.quadro(lado * 0.285, 0.065, 0.004))
    _vestir_peito(M, 0.3, 'por cima do colete: gire girar_graus e ponha peito_m no centro do peito')


# ---------------------------------------------------------------------------- colete de assalto (pesado)
@equip('colete_assalto', 'Colete de assalto com bolsas', 'colete_tatico', valor=3, peso_kg=2.6, celulas=[3, 3], raridade='raro', fase=3,
       onde=['armazem', 'delegacia', 'estacao'], grade=[5, 3],
       bolsos=_bolsos(('carregadores (3 duplos)', [3, 2]), ('granada esquerda', [1, 1]), ('granada direita', [1, 1]),
                      ('primeiros socorros', [1, 2]), ('administrativa (mapa e bloco)', [2, 1]), ('lanterna e faca', [1, 1]), ('bolsa de despejo', [1, 1]),
                      ('hidratação (costas)', [1, 1])),
       protecao=8, penalidade={'cansaco_correr': 1.05}, valor_troca=80,
       efeito='grade de 5 × 3: três porta-carregadores duplos, duas de granada, primeiros socorros, administrativa, lanterna, despejo e bolsa de água nas costas')
def colete_assalto(M):
    p = M.base; T = Tronco(A=0.2, B=0.152); C = T.costas(); tec = 'cordura_coiote'; k = 0.0
    fr = SPoly([(-0.21, 0.0), (0.21, 0.0), (0.21, 0.27), (0.15, 0.38), (0.1, 0.42), (-0.1, 0.42), (-0.15, 0.38), (-0.21, 0.27)]).difference(SPoint(0, 0.47).buffer(0.09, quad_segs=10))
    fr = fr.buffer(-0.012).buffer(0.012, quad_segs=4)
    p.add(tec, painel(T, fr, k, 0.008, infla=0.003)); cinta_borda(p, T, 'nylon_coiote', fr, k + 0.003, 0.0035, 170)
    tr = affinity.translate(SPoly([(-0.2, 0.0), (0.2, 0.0), (0.2, 0.3), (0.14, 0.45), (-0.14, 0.45), (-0.2, 0.3)]), C, 0).buffer(-0.012).buffer(0.012, quad_segs=4)
    p.add(tec, painel(T, tr, k, 0.008, infla=0.003)); cinta_borda(p, T, 'nylon_coiote', tr, k + 0.003, 0.0035, 170)
    molle(p, T, tec, C - 0.17, C + 0.17, 0.27, 3, k + 0.011)
    K = k + 0.011
    for u in (-0.1, 0.0, 0.1):                                                      # tres porta-carregadores duplos
        _bolsa_em(p, T, u, 0.02, K, lambda q: bolsa_carregador(q, tec, 0.096, 0.125, 0.044, mags=2, mag='polimero_mag_coiote'))
    def granada(q):
        bolsa_corpo(q, tec, 0.06, 0.08, 0.05, 0.5)
        q.hull(tec, [(sx * 0.032, y, z) for sx in (-1, 1) for (y, z) in ((0.085, 0.004), (0.088, 0.04), (0.055, 0.054), (0.055, 0.05))])
        q.cham('nylon_preto', -0.01, 0.01, 0.03, 0.065, 0.052, 0.056, 0.0015); q.cham('nylon_preto', -0.012, 0.012, 0.03, 0.04, 0.05, 0.058, 0.002)
    for lado in (-1, 1): _bolsa_em(p, T, lado * 0.19, 0.02, K, granada)
    _bolsa_em(p, T, -0.1, 0.175, K, lambda q: bolsa_tampa(q, tec, 0.085, 0.11, 0.045, velcro='velcro_coiote', cruz=True))       # primeiros socorros
    def admin(q):
        bolsa_tampa(q, tec, 0.14, 0.1, 0.022, ziper=True, velcro='velcro_coiote')
        q.cham('plastico_transp', -0.06, 0.06, 0.012, 0.055, 0.022, 0.0245, 0.003)
        for x_ in (-0.05, -0.042): cyl_eixo(q, 'pc_preto', 0.0035, 0.06, 0.1, 'y', (x_, 0, 0.026), 8)
    _bolsa_em(p, T, 0.065, 0.175, K, admin)
    def lanterna_faca(q):
        bolsa_corpo(q, tec, 0.04, 0.1, 0.03)
        cyl_eixo(q, 'aluminio_escuro', 0.014, 0.08, 0.125, 'y', (0, 0, 0.016), 18)
        q.cham('nylon_preto', -0.006, 0.006, 0.02, 0.09, 0.03, 0.034, 0.0015)
    _bolsa_em(p, T, 0.19, 0.175, K, lanterna_faca)
    # bolsa de despejo enrolada no quadril e bolsa de hidratacao atras com mangueira pelo ombro
    def despejo(q):
        for x_ in np.linspace(-0.04, 0.04, 5): cyl_eixo(q, tec, 0.028, x_ - 0.009, x_ + 0.009, 'x', (0, 0.03, 0.028), 18)
        q.box('nylon_preto', -0.012, 0.012, 0.0, 0.065, 0.054, 0.058)
    _bolsa_em(p, T, -0.25, 0.0, K - 0.005, despejo)
    _bolsa_em(p, T, C, 0.05, K, lambda q: (bolsa_tampa(q, tec, 0.22, 0.2, 0.05, velcro='velcro_coiote', ziper=True)))
    a = T.pt(C - 0.09, 0.27, K + 0.04)
    for lado in (-1, 1):
        pts, N = alca_ombro(p, T, tec, lado, 0.1, 0.38, 0.1, 0.42, 0.004, w=0.075, t=0.014, x_ombro=0.12, y_ombro=0.53)
        p.add('velcro_coiote', fita(pts[14:20], N[14:20], 0.05, 0.0155, lat=np.tile([1.0, 0, 0], (6, 1)))) if lado > 0 else None
        tira_lateral(p, T, tec, lado, 0.2, C - 0.18, 0.0, 0.2, 0.0, 0.006)
        molle(p, T, tec, min(lado * 0.23, lado * (C - 0.2)), max(lado * 0.23, lado * (C - 0.2)), 0.04, 3, 0.006)
        q = P(); fivela(q, (0.0, 0.0, 0.0), 0.05); p.merge(q, T.quadro(lado * 0.215, 0.1, 0.008))
    pts = curva([a, a + [0.04, 0.12, 0.03], (0.13, 0.555, -0.03), (0.13, 0.55, 0.05), T.pt(0.1, 0.4, 0.03), T.pt(0.12, 0.3, 0.03)], 50)
    p.add('borracha', tubo(pts, 0.0055, 10)); q = P(); cyl_eixo(q, 'pc_preto', 0.008, -0.025, 0.0, 'y', (0, 0, 0), 12); p.merge(q, TF.translation_matrix(pts[-1]))
    p.add('velcro_coiote', painel(T, ret_arred(-0.07, 0.07, 0.31, 0.37, 0.006), k + 0.0115, 0.002, passo=0.02))
    _vestir_peito(M, 0.3, 'por cima do colete: gire girar_graus e ponha peito_m no centro do peito')
