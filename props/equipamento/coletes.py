# Coletes de protecao (espaco "colete") e funcoes de tronco que os coletes taticos tambem usam.
# Modelados vestidos (frente +Z, y = 0 na barra) e exportados DEITADOS DE COSTAS (M.pose = DEITAR).

def _vestir_peito(M, y=0.3, nota='para vestir: gire girar_graus (XYZ) e ponha peito_m no centro do peito do personagem'):
    M.pose = DEITAR
    M.vestir = dict(nome='peito_m', ponto=(0.0, y, 0.0), girar_graus=[90, 0, 0], nota=nota)


def molle(p, T, mat, u0, u1, y0, linhas, k, passo=0.0381, tacks='costura_escura', larg=0.025, gap=0.0254):
    """Fileiras MOLLE (fita de 25 mm a cada 25 mm, costurada a cada 38 mm) sobre o painel na altura k."""
    for r in range(linhas):
        y = y0 + r * (larg + gap)
        p.add(mat, painel(T, ret_arred(u0, u1, y, y + larg, 0.002, 2), k, 0.0018, passo=0.03))
        for u in np.arange(u0 + 0.004, u1 - 0.002, passo):
            q = P(); q.box(tacks, -0.0018, 0.0018, 0.002, larg - 0.002, 0.0012, 0.0024); p.merge(q, T.quadro(u, y, k))


def alca_ombro(p, T, mat, lado, uf, yf, ub, yb, k, w=0.05, t=0.014, x_ombro=0.1, y_ombro=0.5, almof=True):
    """Alca de ombro acolchoada da frente para as costas por cima do ombro."""
    a = T.pt(lado * uf, yf, k); b = T.pt(T.costas() - lado * ub, yb, k)
    pts = curva([a, a + [0, 0.05, -0.012], (lado * x_ombro, y_ombro - 0.012, 0.06), (lado * x_ombro, y_ombro, 0.0),
                 (lado * x_ombro, y_ombro - 0.012, -0.06), b + [0, 0.05, 0.012], b], 46)
    c = np.array([0, y_ombro - 0.13, 0.0]); N = nrm((pts - c) * [0, 1, 1])
    p.add(mat, fita(pts, N, w, t, canto=0.45, lat=np.tile([1.0, 0, 0], (len(pts), 1))))
    return pts, N


def tira_lateral(p, T, mat, lado, u0, u1, y0, y1, k, t=0.006):
    p.add(mat, painel(T, ret_arred(min(lado * u0, lado * u1), max(lado * u0, lado * u1), y0, y1, 0.008, 3), k, t, passo=0.02))


def cinta_borda(p, T, mat, poly, k, r=0.0032, n=120):
    """Vivo (debrum) contornando o painel: cordao ao longo da borda do poligono."""
    b = poly.exterior; d = np.linspace(0, b.length, n, endpoint=False)
    uv = np.array([b.interpolate(x).coords[0] for x in d])
    p.add(mat, tubo(T.pt(uv[:, 0], uv[:, 1], k), r, 8, fechada=True))


def placa_frente(u=0.13, y0=0.05, y1=0.38, corte=0.05):
    """Contorno de placa balistica com cantos de cima cortados (para o braco)."""
    return SPoly([(-u, y0), (u, y0), (u, y1 - corte), (u - corte, y1), (-u + corte, y1), (-u, y1 - corte)]).buffer(-0.012).buffer(0.012, quad_segs=4)


def desloca_u(poly, du): return affinity.translate(poly, du, 0)


# ---------------------------------------------------------------------------- porta-placas
@equip('colete_portaplacas', 'Colete porta-placas', 'colete', valor=4, peso_kg=6.8, celulas=[3, 3], raridade='raro', fase=2,
       onde=['delegacia', 'armazem', 'estacao'], protecao=60, protege=['tronco'], durabilidade=300, balistico='fuzil',
       penalidade={'cansaco_correr': 1.2}, valor_troca=150,
       efeito='+60 de proteção no tronco (placas seguram mordida e tiro de fuzil); pesado: correr cansa 20 % mais rápido')
def colete_portaplacas(M):
    p = M.base; T = Tronco(); C = T.costas(); tec = 'cordura_verde'
    fr = placa_frente(); tr = desloca_u(placa_frente(0.135, 0.04, 0.4, 0.04), C)
    p.add(tec, painel(T, fr, 0.004, 0.03, infla=0.006))
    p.add(tec, painel(T, tr, 0.004, 0.03, infla=0.006))
    for poly in (fr, tr): cinta_borda(p, T, 'nylon_verde', poly, 0.006)
    # faixa abdominal (cummerbund) com MOLLE dos dois lados
    for lado in (-1, 1):
        u0, u1 = 0.1, C - 0.1
        p.add(tec, painel(T, ret_arred(min(lado * u0, lado * u1), max(lado * u0, lado * u1), 0.05, 0.21, 0.01), 0.002, 0.01, passo=0.02))
        molle(p, T, tec, min(lado * 0.15, lado * (C - 0.14)), max(lado * 0.15, lado * (C - 0.14)), 0.07, 3, 0.012)
        q = P(); fivela(q, (0.0, 0.0, 0.0), 0.025); p.merge(q, T.quadro(lado * 0.128, 0.13, 0.034))
    molle(p, T, tec, -0.105, 0.105, 0.075, 3, 0.0405)
    molle(p, T, tec, C - 0.11, C + 0.11, 0.07, 5, 0.0405)
    # remendo de velcro da frente e alca de resgate atras
    p.add('velcro_verde', painel(T, ret_arred(-0.075, 0.075, 0.245, 0.315, 0.006), 0.0405, 0.0022, passo=0.02))
    q = P()
    pa = curva([T.pt(C - 0.045, 0.37, 0.034), T.pt(C - 0.03, 0.4, 0.06), T.pt(C, 0.41, 0.066), T.pt(C + 0.03, 0.4, 0.06), T.pt(C + 0.045, 0.37, 0.034)], 30)
    p.add('nylon_verde', fita(pa, nrm((pa - [0, 0.37, -0.12]) * [0, 1, 1]), 0.026, 0.004, lat=np.tile([1.0, 0, 0], (30, 1))))
    for lado in (-1, 1):
        pts, N = alca_ombro(p, T, tec, lado, 0.085, 0.33, 0.085, 0.36, 0.03)
        i = len(pts) // 2
        p.add('velcro_verde', fita(pts[i - 8:i + 9], N[i - 8:i + 9], 0.04, 0.0164, canto=0.3, lat=np.tile([1.0, 0, 0], (17, 1))))
        q = P(); q.box('nylon_verde', -0.018, 0.018, -0.03, 0.0, 0.0, 0.004); p.merge(q, quadro(pts[6] + N[6] * 0.014, N[6], nrm(pts[8] - pts[4])))   # passador de cabo
    # barra de baixo: ilhos de dreno
    for u in (-0.08, 0.0, 0.08):
        q = P(); anel(q, 'latao_ilhos', 0.003, 0.0048, 0.0, 0.002, 12, 'z'); p.merge(q, T.quadro(u, 0.07, 0.034))
    _vestir_peito(M)


def _arte_texto(txt, fundo, cor, tam=(1024, 256), fs=170):
    img = Image.new('RGB', tam, fundo); d = ImageDraw.Draw(img)
    texto_c(d, (tam[0] // 2, tam[1] // 2), txt, fs, cor, True, tam[0] - 60)
    return img


def _uv_xy(x0, x1, y0, y1, espelho=False):
    def f(v, n):
        u = (v[:, 0] - x0) / (x1 - x0); return np.stack([1 - u if espelho else u, (v[:, 1] - y0) / (y1 - y0)], 1)
    return f


# ---------------------------------------------------------------------------- policial (macio, nivel pistola)
@equip('colete_policial', 'Colete à prova de balas policial', 'colete', valor=3, peso_kg=2.9, celulas=[3, 3], raridade='incomum', fase=1,
       onde=['delegacia', 'banco', 'estacao', 'rodoviaria', 'correios'], protecao=38, protege=['tronco'], durabilidade=180, balistico='pistola',
       penalidade={}, valor_troca=70,
       efeito='+38 de proteção no tronco (mordida não atravessa; segura tiro de pistola); leve, dá para correr sem cansar mais')
def colete_policial(M):
    p = M.base; T = Tronco(A=0.17, B=0.12); C = T.costas(); tec = 'cordura_marinho'
    pescoco = SPoint(0, 0.47).buffer(0.075, quad_segs=12)
    fr = SPoly([(-0.2, 0.03), (0.2, 0.03), (0.2, 0.25), (0.16, 0.36), (0.12, 0.42), (-0.12, 0.42), (-0.16, 0.36), (-0.2, 0.25)]).difference(pescoco)
    fr = fr.buffer(-0.015).buffer(0.015, quad_segs=5)
    tr = affinity.translate(SPoly([(-0.2, 0.03), (0.2, 0.03), (0.2, 0.3), (0.15, 0.42), (0.11, 0.45), (-0.11, 0.45), (-0.15, 0.42), (-0.2, 0.3)])
                            .buffer(-0.015).buffer(0.015, quad_segs=5), C, 0)
    for poly in (fr, tr):
        p.add(tec, painel(T, poly, 0.003, 0.016, infla=0.004, raio=0.04))
        cinta_borda(p, T, 'nylon_preto', poly, 0.004, 0.0035, 160)
    # faixas laterais elasticas com velcro (duas de cada lado)
    for lado in (-1, 1):
        for y in (0.07, 0.17):
            tira_lateral(p, T, 'elastico_preto', lado, 0.17, C - 0.17, y, y + 0.055, 0.002, 0.004)
            q = P(); q.cham('velcro_marinho', -0.03, 0.03, 0.0, 0.055, 0.0, 0.003, 0.002); p.merge(q, T.quadro(lado * 0.17, y, 0.019))
        pts, N = alca_ombro(p, T, tec, lado, 0.1, 0.36, 0.1, 0.39, 0.016, w=0.06, t=0.008, x_ombro=0.105, y_ombro=0.49)
        i = len(pts) // 2
        p.add('velcro_marinho', fita(pts[i - 12:i + 13], N[i - 12:i + 13], 0.064, 0.0102, canto=0.3, lat=np.tile([1.0, 0, 0], (25, 1))))
    # identificacao frente e costas, porta-caneta e alca de radio
    mat_imagem('texto_policia', _arte_texto('POLÍCIA', (30, 36, 52), (236, 236, 230)), 0.85)
    MATS['texto_policia_costas'] = MATS['texto_policia']; TEX['texto_policia_costas'] = TEX['texto_policia']
    u0, u1, y0, y1 = -0.075, 0.075, 0.27, 0.31
    p.add('texto_policia', painel(T, ret_arred(u0, u1, y0, y1, 0.004), 0.0225, 0.0016, passo=0.01))
    x = T.pt(np.array([u0, u1]), 0.29, 0)[:, 0]; p.uv['texto_policia'] = _uv_xy(x[0], x[1], y0, y1)
    u0, u1, y0, y1 = C - 0.13, C + 0.13, 0.25, 0.32
    p.add('texto_policia_costas', painel(T, ret_arred(u0, u1, y0, y1, 0.005), 0.0225, 0.0016, passo=0.01))
    x = T.pt(np.array([u0, u1]), 0.29, 0)[:, 0]; p.uv['texto_policia_costas'] = _uv_xy(min(x), max(x), y0, y1, espelho=True)
    q = P(); bolsa_tampa(q, tec, 0.045, 0.07, 0.012, velcro='velcro_marinho')
    for i, x_ in enumerate((-0.012, 0.0, 0.012)): cyl_eixo(q, 'pc_preto' if i else 'cromado', 0.0035, 0.06, 0.085, 'y', (x_, 0, 0.006), 10)
    p.merge(q, T.quadro(-0.11, 0.16, 0.019))
    for u in (0.1, 0.13):
        q = P(); q.cham('nylon_preto', -0.006, 0.006, 0.0, 0.05, 0.0, 0.004, 0.0015); p.merge(q, T.quadro(u, 0.3, 0.019))
    _vestir_peito(M)


# ---------------------------------------------------------------------------- militar pesado (cobertura total)
@equip('colete_militar', 'Colete militar de cobertura total', 'colete', valor=5, peso_kg=11.5, celulas=[3, 4], raridade='raro', fase=3,
       onde=['armazem', 'estacao', 'delegacia'], protecao=80, protege=['tronco', 'pescoco', 'ombros', 'virilha'], durabilidade=420,
       balistico='fuzil', penalidade={'cansaco_correr': 1.45, 'ruido_passos': 1.2}, valor_troca=240,
       efeito='+80 de proteção no tronco, pescoço, ombros e virilha (fuzil não atravessa as placas); muito pesado: correr cansa 45 % mais e os passos fazem mais barulho')
def colete_militar(M):
    p = M.base; T = Tronco(A=0.172, B=0.122); C = T.costas(); tec = 'camo_mata'
    fr = placa_frente(0.155, 0.02, 0.4, 0.045); tr = desloca_u(placa_frente(0.155, 0.02, 0.42, 0.035), C)
    for poly in (fr, tr):
        p.add(tec, painel(T, poly, 0.004, 0.034, infla=0.007))
        cinta_borda(p, T, 'nylon_verde', poly, 0.005, 0.0038, 160)
    for lado in (-1, 1):                                                            # laterais blindadas
        lat = ret_arred(min(lado * 0.14, lado * (C - 0.14)), max(lado * 0.14, lado * (C - 0.14)), 0.03, 0.27, 0.02)
        p.add(tec, painel(T, lat, 0.003, 0.022, infla=0.005, raio=0.03))
        molle(p, T, tec, min(lado * 0.17, lado * (C - 0.17)), max(lado * 0.17, lado * (C - 0.17)), 0.06, 4, 0.0305)
        q = P(); fivela(q, (0.0, 0.0, 0.0), 0.025); p.merge(q, T.quadro(lado * 0.15, 0.2, 0.026))
        pts, N = alca_ombro(p, T, tec, lado, 0.09, 0.36, 0.09, 0.39, 0.036, w=0.07, t=0.018, x_ombro=0.11, y_ombro=0.52)
        # ombreira (deltoide) articulada pendurada no ombro
        U = np.linspace(-0.9, 0.9, 16); V = np.linspace(0.0, 0.16, 10)
        def dfn2(u, v, k, lado=lado):
            r = 0.07 + k; a = 0.35 + 1.15 * (v / 0.16)
            return np.stack([lado * (0.185 + r * np.sin(a)), 0.43 + r * np.cos(a), u * 0.085 * (1 + 0.25 * v / 0.16)], -1)
        p.add(tec, laje(dfn2, U, V, 0.0, 0.016))
        for v_ in (0.05, 0.1):
            p.add('costura_escura', tubo(dfn2(U, np.full(16, v_), 0.0164), 0.0012, 6))
        a_ = dfn2(np.array([0.0]), np.array([0.0]), 0.016)[0]; b_ = pts[len(pts) // 2] + [0, 0.018, 0]
        p.add('nylon_verde', fita(curva([b_, (a_ + b_) / 2 + [0, 0.012, 0], a_], 12), np.tile([0, 1.0, 0], (12, 1)), 0.03, 0.003))   # tira que prende a ombreira
    # gola (protetor de pescoco) em pe
    th = np.linspace(-2.3, 2.3, 80)
    gola = np.stack([0.1 * np.sin(th), np.full(80, 0.44), 0.09 * np.cos(th) - 0.005], 1)
    p.add(tec, fita(gola, nrm(gola * [1, 0, 1] + [0, 0, 0.005]), 0.07, 0.02, canto=0.45, lat=np.tile([0, 1.0, 0], (80, 1))))
    p.add('nylon_verde', tubo(gola + [0, 0.035, 0] + nrm(gola * [1, 0, 1]) * 0.01, 0.006, 8))
    # protetor de virilha pendurado na frente
    vir = SPoly([(-0.075, -0.15), (0.075, -0.15), (0.1, 0.04), (-0.1, 0.04)]).buffer(-0.02).buffer(0.02, quad_segs=5)
    p.add(tec, painel(T, vir, 0.03, 0.016, infla=0.004))
    for x_ in (-0.05, 0.05):
        q = P(); q.box('nylon_verde', -0.012, 0.012, -0.01, 0.06, 0.0, 0.003); p.merge(q, T.quadro(x_, 0.0, 0.044))
    molle(p, T, tec, -0.12, 0.12, 0.06, 4, 0.0455)
    molle(p, T, tec, C - 0.12, C + 0.12, 0.06, 5, 0.0455)
    p.add('velcro_verde', painel(T, ret_arred(-0.08, 0.08, 0.28, 0.35, 0.006), 0.0455, 0.0022, passo=0.02))
    q = P(); q.cham('nylon_verde', -0.012, 0.012, -0.05, 0.0, 0.0, 0.006, 0.003); q.add('marcador_vermelho', tubo(curva([(-0.01, -0.05, 0.006), (0, -0.075, 0.012), (0.01, -0.05, 0.006)], 12), 0.004))
    p.merge(q, T.quadro(0.12, 0.33, 0.04))                                          # puxador de soltura rapida
    pa = curva([T.pt(C - 0.05, 0.38, 0.038), T.pt(C - 0.03, 0.41, 0.07), T.pt(C, 0.42, 0.076), T.pt(C + 0.03, 0.41, 0.07), T.pt(C + 0.05, 0.38, 0.038)], 30)
    p.add('nylon_verde', fita(pa, nrm((pa - [0, 0.37, -0.12]) * [0, 1, 1]), 0.03, 0.005, lat=np.tile([1.0, 0, 0], (30, 1))))
    _vestir_peito(M)
