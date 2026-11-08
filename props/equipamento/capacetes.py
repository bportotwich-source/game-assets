# Capacetes (espaco "capacete" do inventario). Executado por gerar_equipamento.py (mesmas funcoes e materiais).
# Casco em pe apoiado na borda, frente +Z; "vestir.cabeca_m" = onde fica o centro da cabeca no GLB.

def _vestir_cabeca(M, ponto, nota='encaixe no osso da cabeca: ponha este ponto no centro da cabeca, sem girar'):
    M.vestir = dict(nome='cabeca_m', ponto=ponto, girar_graus=[0, 0, 0], nota=nota)


def _almofadas(p, s, t, lugares, mat='espuma_cinza', tam=(0.032, 0.03, 0.009)):
    """Almofadas de espuma presas por velcro dentro do casco."""
    for th, al in lugares:
        q = P(); fofo(q, mat, 0.0, 0.0, -tam[2], tam[0], tam[1], tam[2], 0.35, 0.35, (10, 14))
        p.merge(q, s.quadro(th, al, -t))


def _jugular(p, pontos, encontro, queixo, mat='nylon_preto', w=0.018):
    """Tiras do queixo: de cada ponto de fixacao ate o encontro do lado, depois ate a queixeira."""
    for lado in (-1, 1):
        e = np.array([lado * encontro[0], encontro[1], encontro[2]])
        for a in pontos:
            a = np.array([lado * a[0], a[1], a[2]])
            c = curva([a, (a + e) / 2 + [lado * 0.004, 0, 0], e], 12)
            p.add(mat, fita(c, np.tile([lado, 0, 0], (len(c), 1)), w, 0.0018))
        c = curva([e, (e + np.array(queixo)) / 2 + [lado * 0.02, -0.01, 0], [lado * 0.03, queixo[1], queixo[2]]], 14)
        p.add(mat, fita(c, np.tile([lado, -0.3, 0.3], (len(c), 1)), w, 0.0018))
        p.cham('nylon_preto', e[0] - 0.006, e[0] + 0.006, e[1] - 0.016, e[1] + 0.006, e[2] - 0.012, e[2] + 0.012, 0.002)    # passador


# ---------------------------------------------------------------------------- militar (corte alto)
@equip('capacete_militar', 'Capacete balístico de corte alto', 'capacete', valor=4, peso_kg=1.3, celulas=[2, 2], raridade='raro', fase=2,
       onde=['delegacia', 'armazem', 'estacao', 'quartel'], protecao=55, protege=['cabeca'], durabilidade=240, balistico='pistola',
       penalidade={}, efeito='+55 de proteção na cabeça (segura mordida e tiro de pistola); orelhas livres: não atrapalha a audição',
       trilhos=['lanterna_capacete (trilho lateral)', 'oculos_visao_noturna (frente)'], valor_troca=120)
def capacete_militar(M):
    p = M.base; t = 0.0085
    s = Casco(0.112, 0.146, 0.132, y0=0.0, z0=-0.006, e=0.86)
    borda = borda_suave([(0, 0.16), (0.55, 0.19), (1.0, 0.33), (1.3, 0.48), (1.62, 0.5), (1.95, 0.4), (2.25, 0.12), (2.7, -0.04), (math.pi, -0.08)])
    p.add('tinta_casco_coiote', s.casca(borda, t))
    pr, nr = s.aro(borda, 0, 0, k=-t / 2)
    p.add('borracha', tubo(pr, 0.0056, 10, fechada=True))                                      # friso de borracha da borda
    # suporte frontal do oculos noturno (placa com fenda e 3 parafusos)
    q = P(); q.cham('aluminio_escuro', -0.032, 0.032, -0.024, 0.02, -0.006, 0.0065, 0.003)
    q.cham('pc_preto', -0.012, 0.012, -0.016, 0.008, 0.0055, 0.0085, 0.0015)
    q.cham('aluminio_escuro', -0.017, 0.017, -0.032, -0.018, -0.002, 0.012, 0.003)
    for x, y in ((-0.024, 0.012), (0.024, 0.012), (0.0, -0.026)): cyl_eixo(q, 'cromado', 0.0028, 0.006, 0.0095, 'z', (x, y, 0))
    p.merge(q, s.quadro(0.0, 0.4, 0.0))
    # trilhos laterais curvos (acessorios) com fendas e ponteiras
    for lado in (-1, 1):
        th = lado * np.linspace(0.62, 1.95, 40); al = borda(th) + np.interp(np.abs(th), [0.62, 1.3, 1.95], [0.11, 0.06, 0.09])
        pts = s.pt(th, al, -0.001); n = s.normal(th, al)
        p.add('pc_grafite', fita(pts, n, 0.024, 0.0085, canto=0.3))
        for f in np.linspace(0.06, 0.94, 9):
            i = int(f * 39); q = P(); q.box('pc_preto', -0.004, 0.004, -0.0075, 0.0075, 0.0072, 0.0092)
            p.merge(q, quadro(pts[i] , n[i], nrm(np.gradient(pts, axis=0)[i])))
        for i in (0, 39):
            q = P(); cyl_eixo(q, 'cromado', 0.0035, 0.007, 0.011, 'z'); p.merge(q, quadro(pts[i], n[i]))
    # paineis de velcro (em cima e atras) e cordao elastico
    p.add('velcro_coiote', laje(s.pt, np.linspace(-0.5, 0.5, 16), np.linspace(0.78, 1.12, 8), -0.001, 0.0022))
    p.add('velcro_coiote', laje(s.pt, np.linspace(math.pi - 0.45, math.pi + 0.45, 14), np.linspace(0.22, 0.62, 8), -0.001, 0.0022))
    for lado in (-1, 1):
        p.add('velcro_coiote', laje(s.pt, lado * np.linspace(1.15, 1.75, 10), np.linspace(0.68, 0.9, 5), -0.001, 0.0022))
    th = np.linspace(0.75, 2 * math.pi - 0.75, 90)
    p.add('elastico_preto', tubo(s.pt(th, 0.6 + 0.04 * np.cos(2 * th), 0.0042), 0.0024, 8))
    for a in (0.75, 2 * math.pi - 0.75):
        q = P(); q.cham('nylon_preto', -0.006, 0.006, -0.008, 0.008, -0.001, 0.006, 0.002); p.merge(q, s.quadro(a, 0.6 + 0.04 * math.cos(2 * a), 0))
    # contrapeso atras (bolsinha) e marcador de identificacao (luz vermelha)
    q = P(); bolsa_tampa(q, 'cordura_coiote', 0.085, 0.05, 0.022, velcro='velcro_coiote'); p.merge(q, s.quadro(math.pi, -0.02, 0.0) @ TF.translation_matrix([0, -0.025, 0]))
    q = P(); q.cham('pc_preto', -0.01, 0.01, -0.014, 0.014, 0.0, 0.012, 0.003); q.cham('lente_vermelha', -0.006, 0.006, -0.008, 0.008, 0.011, 0.0135, 0.0015)
    p.merge(q, s.quadro(math.pi, 0.86, 0.002))
    # dentro: almofadas e tiras do queixo
    _almofadas(p, s, t, [(0, 0.5), (0, 1.25), (math.pi, 0.35), (math.pi, 0.85), (0.9, 0.85), (-0.9, 0.85), (2.3, 0.8), (-2.3, 0.8),
                         (1.6, 0.85), (-1.6, 0.85)])
    _jugular(p, [(0.1, 0.02, 0.06), (0.1, 0.0, -0.075)], (0.088, -0.045, -0.004), (0.0, -0.07, 0.06))
    q = P(); fofo(q, 'forro_preto', 0.0, -0.07, 0.062, 0.03, 0.012, 0.018, 0.4, 0.4, (10, 14)); p.merge(q)          # queixeira (tiras recolhidas)
    fivela(p, (0.035, -0.058, 0.06), 0.016, eixo_x=True)
    _vestir_cabeca(M, (0.0, 0.035, 0.0))


def _aba(s, borda, ext, queda, th0=0.0, th1=2 * math.pi, nu=120, nv=7, t=0.0035):
    """Aba (pala) saindo da borda para fora: ext(th) = largura (m), queda = quanto desce na ponta. Espessura t para baixo."""
    def fn(u, v, k):
        al = borda(u); b = s.pt(u, al, -0.0015)
        d = nrm(np.stack([b[:, 0], np.zeros(len(u)), b[:, 2] - s.z0], 1))
        e = ext(u)[:, None]; return b + d * e * v[:, None] + np.stack([0 * u, -queda * v ** 2 * (e[:, 0] / max(e.max(), 1e-6)) + k, 0 * u], 1)
    return laje(fn, np.linspace(th0, th1, nu), np.linspace(0, 1, nv), -t, 0.0)


def _nervura(s, x, z0, z1, k=0.0, n=60):
    """Pontos do casco no plano x = const de z0 a z1 (por cima)."""
    zs = np.linspace(z0, z1, n); ta = no_casco(s, np.stack([np.full(n, x), zs], 1), (0, 2), k, 1)
    return s.pt(ta[:, 0], ta[:, 1], k), s.normal(ta[:, 0], ta[:, 1])


# ---------------------------------------------------------------------------- obra (capacete de seguranca)
@equip('capacete_obra', 'Capacete de obra', 'capacete', valor=1, peso_kg=0.38, celulas=[2, 2], raridade='comum', fase=1,
       onde=['fabrica', 'serraria', 'armazem', 'garagem', 'ferrovelho', 'estacao'], protecao=22, protege=['cabeca'], durabilidade=60,
       balistico='nenhum', penalidade={}, valor_troca=12,
       efeito='+22 de proteção na cabeça contra golpe e mordida; leve e não atrapalha nada; racha depois de alguns golpes fortes')
def capacete_obra(M):
    p = M.base; t = 0.0035
    s = Casco(0.103, 0.128, 0.126, y0=0.0, z0=0.004, e=0.93)
    borda = lambda th: 0.035 + 0.0 * np.asarray(th)
    p.add('abs_amarelo', s.casca(borda, t, nth=128, nal=30))
    p.add('abs_amarelo', _aba(s, borda, lambda u: 0.012 + 0.05 * np.clip(np.cos(u), 0, 1) ** 2 + 0.01 * np.clip(-np.cos(u), 0, 1), 0.014))
    for x, w in ((0.0, 0.016), (-0.04, 0.012), (0.04, 0.012)):                       # nervuras de cima
        pts, n = _nervura(s, x, s.z0 + 0.1 if x == 0 else s.z0 + 0.08, s.z0 - 0.1 if x == 0 else s.z0 - 0.07)
        p.add('abs_amarelo', fita(pts, n, w, 0.0055, canto=0.45))
    for lado in (-1, 1):                                                              # encaixes de protetor auricular
        q = P(); q.cham('abs_amarelo', -0.016, 0.016, -0.006, 0.01, -0.002, 0.006, 0.0025); q.box('pc_preto', -0.011, 0.011, -0.002, 0.006, 0.0045, 0.0065)
        p.merge(q, s.quadro(lado * math.pi / 2, 0.11, 0.0))
    p.add('adesivo_branco', laje(s.pt, np.linspace(-0.26, 0.26, 10), np.linspace(0.42, 0.62, 5), -0.0005, 0.0008))   # etiqueta de inspecao
    for lado in (-1, 1):                                                              # faixas refletivas atras
        p.add('refletivo', laje(s.pt, math.pi + lado * np.linspace(0.3, 0.95, 12), np.linspace(0.5, 0.58, 3), -0.0005, 0.0008))
    # suspensao: carneira (aro de cabeca), 4 tiras cruzadas, catraca atras, testeira
    th = np.linspace(0, 2 * math.pi, 120, endpoint=False)
    aro = np.stack([0.083 * np.sin(th), np.full(120, 0.004), 0.098 * np.cos(th) + 0.004], 1)
    p.add('pc_preto', fita(aro, np.tile([0, 1.0, 0], (120, 1)), 0.0025, 0.022, lat=None, fechada=True) if False else
          fita(aro, nrm(aro * [1, 0, 1] - [0, 0, 0.004]), 0.022, 0.0022, lat=np.tile([0, 1.0, 0], (120, 1)), fechada=True))
    i0 = (th > -0.9) & (th < 0.9)
    tes = aro[(th < 0.9) | (th > 2 * math.pi - 0.9)]
    ang = np.linspace(-0.9, 0.9, 40); tes = np.stack([0.0795 * np.sin(ang), np.full(40, 0.004), 0.0945 * np.cos(ang) + 0.004], 1)
    p.add('forro_preto', fita(tes, -nrm(tes * [1, 0, 1]), 0.026, 0.004, lat=np.tile([0, 1.0, 0], (40, 1))))
    for a in (0.6, 2.4, 3.9, 5.7):
        b = np.array([0.083 * math.sin(a), 0.016, 0.098 * math.cos(a) + 0.004])
        c = curva([b, b * [0.7, 0, 0.7] + [0, 0.07, 0.0012], b * [0.25, 0, 0.25] + [0, 0.1, 0.003], [0, 0.104, 0.004]], 24)
        p.add('nylon_preto', fita(c, nrm(c - [0, 0.0, 0.004]), 0.016, 0.0016))
        q = P(); q.cham('pc_preto', -0.006, 0.006, -0.012, 0.012, -0.007, 0.0, 0.002); p.merge(q, s.quadro(a, 0.1, -t))   # presilha no casco
    q = P(); cyl_eixo(q, 'pc_preto', 0.016, -0.004, 0.012, 'z', (0, 0, 0), 20)
    for i in range(12):
        a = i * math.pi / 6; q.box('pc_preto', 0.0155 * math.cos(a) - 0.0015, 0.0155 * math.cos(a) + 0.0015, 0.0155 * math.sin(a) - 0.0015, 0.0155 * math.sin(a) + 0.0015, -0.003, 0.011)
    p.merge(q, TF.translation_matrix([0, 0.0, -0.097]) @ TF.rotation_matrix(math.pi, [0, 1, 0]))
    _vestir_cabeca(M, (0.0, -0.035, 0.004))


# ---------------------------------------------------------------------------- ciclismo
@equip('capacete_ciclismo', 'Capacete de ciclismo', 'capacete', valor=1, peso_kg=0.28, celulas=[2, 2], raridade='comum', fase=1,
       onde=['casas', 'garagem', 'galeria', 'parque', 'pista_skate', 'escolinha'], protecao=12, protege=['cabeca'], durabilidade=30,
       balistico='nenhum', penalidade={}, valor_troca=6,
       efeito='+12 de proteção na cabeça; muito leve e ventilado; a espuma amassa e perde a proteção depressa')
def capacete_ciclismo(M):
    p = M.base
    s = Casco(0.1, 0.122, 0.138, y0=0.0, z0=-0.012, e=0.84)
    borda = borda_suave([(0, 0.14), (0.7, 0.1), (1.4, 0.02), (2.1, -0.06), (2.7, -0.2), (math.pi, -0.24)])
    eps = s.casca(borda, 0.024, nth=128, nal=30, k=-0.0015); pc = s.casca(lambda th: borda(th) + 0.012, 0.0016, nth=128, nal=30)
    cort = []
    for th, al, L in [(0.28, 0.42, 0.04), (-0.28, 0.42, 0.04), (0.8, 0.45, 0.035), (-0.8, 0.45, 0.035), (0.0, 0.9, 0.05), (0.42, 0.92, 0.045),
                      (-0.42, 0.92, 0.045), (math.pi, 0.6, 0.04), (math.pi - 0.45, 0.45, 0.04), (math.pi + 0.45, 0.45, 0.04),
                      (math.pi - 1.05, 0.35, 0.03), (math.pi + 1.05, 0.35, 0.03), (1.4, 0.7, 0.03), (-1.4, 0.7, 0.03)]:
        q = elipsoide((0, 0, 0), 0.0105, L, 0.06, 0.6, 0.6, (12, 16)); q.apply_transform(s.quadro(th, al, 0.0)); cort.append(q)
    p.add('eps', menos(eps, *cort)); p.add('pc_azul', menos(pc, *cort))
    # faixa branca do casco externo e adesivo refletivo atras
    for lado in (-1, 1):
        th = lado * np.linspace(0.15, 2.7, 60); al = borda(th) + 0.012
        p.add('abs_branco', fita(s.pt(th, al, 0.0002), s.normal(th, al), 0.008, 0.0012))
    q = P(); q.cham('refletivo', -0.025, 0.025, -0.008, 0.008, -0.001, 0.0014, 0.004); p.merge(q, s.quadro(math.pi, 0.05, 0.0))
    p.add('pc_preto', _aba(s, borda, lambda u: 0.035 * np.clip(np.cos(u * 1.6), 0, 1), 0.008, -0.9, 0.9, 40, 5, 0.002))   # pala
    # regulagem atras (catraca) com berco de plastico
    th = np.linspace(-1.7, 1.7, 50) + math.pi
    cam = s.pt(th, borda(th) - 0.0, -0.03)
    p.add('pc_preto', fita(cam, -s.normal(th, borda(th)), 0.012, 0.0025, lat=np.tile([0, 1.0, 0], (50, 1))))
    q = P(); cyl_eixo(q, 'pc_preto', 0.017, -0.006, 0.01, 'z', (0, 0, 0), 24); cyl_eixo(q, 'pc_grafite', 0.012, 0.008, 0.013, 'z', (0, 0, 0), 20)
    for i in range(16):
        a = i * math.pi / 8; q.box('pc_preto', 0.017 * math.cos(a) - 0.001, 0.017 * math.cos(a) + 0.001, 0.017 * math.sin(a) - 0.001, 0.017 * math.sin(a) + 0.001, -0.005, 0.009)
    o = s.pt(math.pi, borda(math.pi), -0.03); p.merge(q, quadro(o + [0, 0.004, -0.008], [0, -0.2, -1]))
    # forro e tiras com divisor em Y
    _almofadas(p, s, 0.026, [(0, 0.5), (0.0, 1.1), (1.2, 0.6), (-1.2, 0.6), (math.pi, 0.5)], 'forro_preto', (0.028, 0.02, 0.004))
    for lado in (-1, 1):
        e = np.array([lado * 0.082, -0.05, 0.02])
        for a in (s.pt(lado * 1.1, borda(lado * 1.1) + 0.03, -0.026), s.pt(lado * 2.2, borda(lado * 2.2) + 0.03, -0.026)):
            c = curva([a, (a + e) / 2, e], 12); p.add('nylon_preto', fita(c, np.tile([lado, 0, 0.0], (12, 1)), 0.014, 0.0014))
        q = P(); q.cham('pc_preto', -0.008, 0.008, -0.012, 0.012, 0.0, 0.005, 0.0015); p.merge(q, quadro(e, [lado, 0, 0]))
        c = curva([e, e + [-lado * 0.015, -0.03, 0.03], [lado * 0.02, -0.08, 0.075]], 14); p.add('nylon_preto', fita(c, np.tile([lado, -0.4, 0.4], (14, 1)), 0.014, 0.0014))
    fivela(p, (0.0, -0.08, 0.077), 0.014)
    _vestir_cabeca(M, (0.0, -0.02, -0.01))


# ---------------------------------------------------------------------------- moto (fechado, com viseira)
@equip('capacete_moto', 'Capacete de moto fechado', 'capacete', valor=2, peso_kg=1.45, celulas=[2, 2], raridade='incomum', fase=1,
       onde=['garagem', 'posto', 'casas', 'concessionaria', 'estacionamento', 'rua'], protecao=40, protege=['cabeca', 'rosto'], durabilidade=120,
       balistico='nenhum', penalidade={'audicao': 0.75, 'visao': 0.85}, valor_troca=30,
       efeito='+40 de proteção na cabeça e no rosto (mordida não pega com a viseira baixada); abafa a audição em 25 % e fecha a visão lateral')
def capacete_moto(M):
    p = M.base; t = 0.006
    s = Casco(0.128, 0.152, 0.158, y0=0.0, z0=0.0, e=0.9)
    borda = borda_suave([(0, -0.62), (0.6, -0.66), (1.4, -0.78), (2.2, -0.72), (math.pi, -0.6)])
    janela = elipsoide((0.0, -0.012, 0.15), 0.086, 0.044, 0.09, 0.3, 0.32, (20, 32))
    p.add('pc_vermelho', menos(s.casca(borda, t, nth=144, nal=40), janela))
    p.add('eps_preto', menos(s.casca(lambda th: borda(th) + 0.03, 0.018, nth=96, nal=26, k=-t), janela))
    # faixas brancas por cima (adesivo) e borda de borracha
    for x in (-0.026, 0.026):
        pts, n = _nervura(s, x, 0.12, -0.15, 0.0003); p.add('adesivo_branco', fita(pts, n, 0.012, 0.0009))
    pr, nr = s.aro(borda, 0, 0, k=-t / 2); p.add('borracha', tubo(pr, 0.0065, 10, fechada=True))
    p.add('forro_preto', tubo(s.aro(lambda th: borda(th) + 0.04, 0, 0, k=-t - 0.018)[0], 0.013, 12, fechada=True))       # rolo do pescoco
    # borracha em volta da janela
    ang = np.linspace(0, 2 * math.pi, 90, endpoint=False)
    xy = np.stack([0.086 * sp(np.cos(ang), 0.3), -0.012 + 0.044 * sp(np.sin(ang), 0.3)], 1)
    ta = no_casco(s, xy, (0, 1), -t / 2, 1); p.add('borracha', tubo(s.pt(ta[:, 0], ta[:, 1], -t / 2), 0.0045, 8, fechada=True))
    # ventilacao do queixo e de cima, aerofolio atras
    q = P(); q.cham('pc_preto', -0.026, 0.026, -0.012, 0.012, -0.002, 0.007, 0.003)
    for y in (-0.006, 0.0, 0.006): q.box('pc_grafite', -0.02, 0.02, y - 0.0014, y + 0.0014, 0.006, 0.0085)
    p.merge(q, s.quadro(0.0, -0.4, 0.0))
    for lado in (-1, 1):
        q = P(); q.cham('pc_preto', -0.01, 0.01, -0.016, 0.016, -0.002, 0.007, 0.003); q.cham('pc_grafite', -0.006, 0.006, -0.004, 0.012, 0.006, 0.009, 0.0015)
        p.merge(q, s.quadro(lado * 0.3, 0.9, 0.0))
    q = P(); q.hull('pc_preto', [(sx * 0.055, 0.0, 0.0) for sx in (-1, 1)] + [(sx * 0.045, -0.004, 0.03) for sx in (-1, 1)] + [(sx * 0.05, 0.02, 0.004) for sx in (-1, 1)])
    p.merge(q, s.quadro(math.pi, 0.15, -0.003) @ TF.rotation_matrix(-0.3, [1, 0, 0]))
    # viseira (parte movel): casca fina por fora da janela, gira no eixo lateral
    piv = s.pt(math.pi / 2, 0.02, 0.0); orig = (0.0, float(piv[1]), float(piv[2]))
    v = M.parte('viseira', orig, 'gira', eixo=[-1, 0, 0], abre_graus=62, nota='viseira fumê: baixada protege o rosto; levante para enxergar melhor à noite')
    reg = elipsoide((0.0, -0.006, 0.16), 0.118, 0.06, 0.1, 0.3, 0.3, (20, 32))
    v.add('viseira_fume', inter(s.casca(lambda th: -0.7 + 0 * th, 0.0028, nth=144, nal=40, k=0.0045), reg))
    for lado in (-1, 1):
        q = P(); cyl_eixo(q, 'pc_preto', 0.017, 0.0, 0.006, 'z', (0, 0, 0), 24); cyl_eixo(q, 'cromado', 0.006, 0.005, 0.008, 'z', (0, 0, 0), 16)
        v.merge(q, s.quadro(lado * math.pi / 2, 0.02, 0.0025))
        q = P(); cyl_eixo(q, 'pc_preto', 0.02, -0.002, 0.003, 'z', (0, 0, 0), 24); p.merge(q, s.quadro(lado * math.pi / 2, 0.02, 0.0))
    q = P(); q.cham('pc_preto', -0.012, 0.012, -0.006, 0.006, 0.0, 0.008, 0.002); v.merge(q, s.quadro(-0.55, -0.32, 0.007))   # puxador
    _vestir_cabeca(M, (0.0, -0.01, 0.0))


# ---------------------------------------------------------------------------- choque (viseira grande e protetor de nuca)
@equip('capacete_choque', 'Capacete de choque com viseira', 'capacete', valor=3, peso_kg=1.6, celulas=[2, 2], raridade='incomum', fase=2,
       onde=['delegacia', 'estacao', 'rodoviaria', 'banco'], protecao=45, protege=['cabeca', 'rosto', 'pescoco'], durabilidade=160,
       balistico='nenhum', penalidade={'audicao': 0.85, 'visao': 0.9}, valor_troca=55,
       efeito='+45 de proteção na cabeça, rosto e nuca (viseira e protetor de nuca seguram mordida); abafa um pouco a audição')
def capacete_choque(M):
    p = M.base; t = 0.0075
    s = Casco(0.118, 0.15, 0.138, y0=0.0, z0=-0.004, e=0.88)
    borda = borda_suave([(0, 0.17), (0.6, 0.12), (1.2, -0.12), (1.7, -0.2), (2.4, -0.28), (math.pi, -0.32)])
    p.add('tinta_casco_preta', s.casca(borda, t))
    pr, nr = s.aro(borda, 0, 0, k=-t / 2); p.add('borracha', tubo(pr, 0.0058, 10, fechada=True))
    th = np.linspace(-1.5, 1.5, 70); p.add('pc_preto', fita(s.pt(th, 0.42, 0.0), s.normal(th, 0.42), 0.02, 0.004))        # faixa de cima da viseira
    # viseira: superficie quase cilindrica afastada do rosto, gira para cima nos cubos laterais
    Rx, Rz, zc = s.a + 0.026, s.c + 0.034, s.z0
    def vfn(u, v, k):
        f = 1 + 0.18 * np.clip(-v / 0.2, 0, 1) ** 1.5
        return np.stack([(Rx + k) * f * np.sin(u), v, zc + (Rz + k) * f * np.cos(u)], -1)
    yp = 0.03; v = M.parte('viseira', (0.0, yp, zc), 'gira', eixo=[-1, 0, 0], abre_graus=75, nota='viseira de policarbonato')
    v.add('viseira_clara', laje(vfn, np.linspace(-1.3, 1.3, 60), np.linspace(-0.19, 0.06, 16), 0.0, 0.004))
    u = np.linspace(-1.3, 1.3, 60); v.add('borracha_viseira', fita(vfn(u, np.full(60, 0.06), 0.002), nrm(vfn(u, np.full(60, 0.06), 0.01) - vfn(u, np.full(60, 0.06), 0)), 0.012, 0.006, lat=np.tile([0, 1.0, 0], (60, 1))))
    for lado in (-1, 1):
        a = vfn(np.array([lado * 1.3]), np.array([0.05]), 0.002)[0]; hub = np.array([lado * (s.a + 0.012), yp, zc])
        q = P(); q.add('pc_preto', fita(curva([a, (a + hub) / 2 + [lado * 0.004, 0, 0], hub], 14), np.tile([lado, 0, 0.0], (14, 1)), 0.026, 0.004)); v.merge(q)
        q = P(); cyl_eixo(q, 'pc_preto', 0.021, 0.0, 0.009, 'z', (0, 0, 0), 28); cyl_eixo(q, 'aluminio_escuro', 0.008, 0.008, 0.012, 'z', (0, 0, 0), 16)
        for i in range(10):
            ag = i * math.pi / 5; q.box('pc_preto', 0.021 * math.cos(ag) - 0.0015, 0.021 * math.cos(ag) + 0.0015, 0.021 * math.sin(ag) - 0.0015, 0.021 * math.sin(ag) + 0.0015, 0.0, 0.009)
        p.merge(q, quadro(hub + [lado * 0.004, 0, 0], [lado, 0, 0]))
    # protetor de nuca acolchoado (painel com pespontos)
    ab = float(np.max(borda(np.array([math.pi]))))
    yb = float(s.pt(math.pi, borda(math.pi))[1])
    def nfn(u, v, k):
        f = 1 + 0.25 * np.clip((yb - v) / 0.16, 0, 1)
        return np.stack([(s.a * 0.92 + k) * f * np.sin(u), v, s.z0 + (s.c * 0.92 + k) * f * np.cos(u)], -1)
    U = np.linspace(math.pi - 1.05, math.pi + 1.05, 40); V = np.linspace(yb - 0.15, yb + 0.02, 12)
    p.add('cordura_preta', laje(nfn, U, V, 0.0, 0.012))
    for y in np.linspace(yb - 0.12, yb - 0.02, 4):
        p.add('costura_escura', tubo(nfn(U, np.full(40, y), 0.0122), 0.0011, 6))
    p.add('nylon_preto', fita(nfn(U, np.full(40, yb - 0.15), 0.0), nrm(nfn(U, np.full(40, yb - 0.15), 0.01) - nfn(U, np.full(40, yb - 0.15), 0)), 0.01, 0.014, lat=np.tile([0, 1.0, 0], (40, 1))))
    _almofadas(p, s, t, [(0, 0.5), (0, 1.25), (math.pi, 0.45), (1.0, 0.8), (-1.0, 0.8), (2.2, 0.75), (-2.2, 0.75)])
    _jugular(p, [(0.1, -0.01, 0.06), (0.1, -0.02, -0.07)], (0.09, -0.06, -0.004), (0.0, -0.085, 0.065))
    q = P(); fofo(q, 'forro_preto', 0.0, -0.085, 0.068, 0.03, 0.013, 0.019, 0.4, 0.4, (10, 14)); p.merge(q)
    _vestir_cabeca(M, (0.0, 0.02, -0.004))
