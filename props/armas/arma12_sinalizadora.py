# Arma 11: pistola sinalizadora (um tiro, cano basculante, cao externo) e cartuchos de sinal vermelho e verde.
# Executado por gerar_armas.py (plano de lado: x frente, y cima, z direita). Desenho proprio inspirado na foto do Bruno:
# armacao de aluminio laranja, cano curto e grosso que bascula para baixo, cao preto, guarda-mato redondo, cabo curvo com talas pretas.
CORES.update({'aluminio_laranja': (214, 92, 34), 'casco_vermelho': (176, 30, 26), 'casco_verde': (36, 128, 58)})
METAL.update({'aluminio_laranja': (0.35, 0.42), 'casco_vermelho': (0.0, 0.45), 'casco_verde': (0.0, 0.45)})
EMISSIVOS.update({'sinal_vermelho': (1.0, 0.1, 0.05), 'sinal_verde': (0.15, 1.0, 0.2),
                  'clarao_sinal_vermelho': (0.9, 0.08, 0.04), 'clarao_sinal_verde': (0.08, 0.85, 0.15)})


_materiais_antes_12 = materiais
def materiais():
    _materiais_antes_12()
    for k, a in (('clarao_sinal_vermelho', 0.22), ('clarao_sinal_verde', 0.22)):
        MATS[k].baseColorFactor = list(EMISSIVOS[k]) + [a]

SR = 0.0145                     # raio de fora do cano
SB = 0.0106                     # raio da alma (calibre 12 de sinal)
SL = 0.118                      # comprimento do cano
SH = (0.024, -0.021)            # dobradica do cano
SGIRO = -42                     # quanto o cano bascula (graus, a boca desce)
SCAO = 34                       # cao armado (graus, para tras)
CABO_S = suave([(-0.016, -0.012), (-0.024, -0.026), (-0.031, -0.05), (-0.04, -0.075), (-0.052, -0.098), (-0.06, -0.112), (-0.072, -0.121), (-0.088, -0.118),
                (-0.093, -0.105), (-0.086, -0.086), (-0.075, -0.064), (-0.064, -0.04), (-0.056, -0.018), (-0.049, 0.002), (-0.04, 0.004)], 3)
LARG_NUC_S = lambda y: 0.0108
LARG_TALA_S = lambda y: 0.0108 + 0.0026 * GT.smooth(-0.03, -0.042, y)


def _cartucho_sinal(cor='casco_vermelho', sec=32, vazio=False):
    """Cartucho de sinal deitado em x (base em x = 0): culote de latao com aro e espoleta, casco de plastico, fecho estrelado."""
    q = P()
    q.add('latao', torno_x([(0.0, 0.0), (0.0119, 0.0), (0.0119, 0.0016), (0.0103, 0.0019), (0.0103, 0.013), (0.0, 0.013)], sec))
    q.add('aco_inox', torno_x([(0.0, -0.0001), (0.0028, -0.0001), (0.0028, 0.0005)], 16))
    casco = torno_x([(0.0, 0.012), (0.0101, 0.012), (0.0101, 0.064), (0.0094, 0.066), (0.0, 0.066)], sec)
    if vazio: casco = menos(casco, cil_x(0.0088, 0.014, 0.07, sec=sec))
    q.add(cor, casco)
    if not vazio:
        q.add(cor, torno_x([(0.0, 0.0655), (0.0086, 0.0655), (0.0072, 0.0668), (0.0, 0.0672)], sec))
        for i in range(6):                                                        # dobras do fecho estrelado
            d = caixa(0.0662, 0.0672, -0.0003, 0.0003, 0.0, 0.0085); d.apply_transform(TF.rotation_matrix(i * math.pi / 3, [1, 0, 0])); q.add('borracha', d)
    for x in (0.03, 0.046): q.add('tinta_branca', tubo_x(0.0101, 0.0103, x, x + 0.004, sec=sec))     # faixas de identificacao
    return q


def _armacao_sinal(p, mat='aluminio_laranja'):
    fora = arred([(-0.05, -0.004), (-0.046, 0.011), (-0.036, 0.0172), (0.0, 0.0172), (0.0, -0.0156), (0.04, -0.0156), (0.046, -0.019),
                  (0.044, -0.028), (0.03, -0.032), (0.0, -0.031), (-0.027, -0.027)], 0.003)
    corpo = solido(fora, -0.0125, 0.0125, 0.0018)
    corpo = menos(corpo, caixa(-0.046, -0.014, -0.012, 0.03, -0.0038, 0.0038),                # janela do cao
                  caixa(0.008, 0.05, -0.034, -0.0154, -0.0066, 0.0066),                         # garfo da dobradica (o ressalto do cano entra aqui)
                  caixa(-0.006, 0.012, -0.034, -0.02, -0.003, 0.003))                           # fenda do gatilho
    p.add(mat, corpo)
    # guarda-mato redondo
    anel = affinity.scale(Point(0.004, -0.05).buffer(0.0225, 48).difference(Point(0.004, -0.05).buffer(0.0185, 48)), 1.08, 0.94)
    p.add(mat, solido(anel.difference(sbox(-1, -0.029, 1, 1)), -0.0045, 0.0045, 0.0012))
    # cabo curvo: nucleo laranja + talas pretas quadriculadas com parafuso
    cabo_com_talas(p, CABO_S, 0.004, -0.121, LARG_NUC_S, LARG_TALA_S, mat, 'polimero', 'polimero_grip', borda=0.0024, borda_xadrez=0.003,
                   n=2.4, raio_base=0.007, parafuso=(-0.06, -0.068))
    p.add('aco_inox', cil_z(0.0042, -0.0095, 0.0095, -0.08, -0.113, 24))                        # olhal do cordao
    p.add('borracha', cil_z(0.0024, -0.01, 0.01, -0.08, -0.113, 16))
    # pino da dobradica, bucha do percussor, pinos da armacao
    p.add('aco_inox', cil_z(0.0032, -0.0128, 0.0128, SH[0], SH[1], 20))
    p.add('aco_oxidado', torno_x([(0.0, -0.0006), (0.0024, -0.0006), (0.0024, 0.0003), (0.0, 0.0003)], 16))
    for zs in (-1, 1):
        for (x, y) in ((-0.03, -0.004), (0.004, -0.024), (-0.02, -0.018), (0.032, -0.025)):
            p.add('aco_oxidado', cil_z(0.0016, min(zs * 0.0124, zs * 0.0132), max(zs * 0.0124, zs * 0.0132), x, y, 14))
    for x in np.linspace(-0.035, -0.012, 7):                                                     # estrias do topo (pegar a mira)
        p.add(mat, caixa(x - 0.0007, x + 0.0007, 0.0172, 0.0181, -0.004, 0.004))


def _cano_sinal(q, mat='aluminio_laranja'):
    perf = [(SB, 0.0), (SR, 0.0), (SR, SL - 0.004), (SR - 0.0015, SL), (SB + 0.0012, SL), (SB, SL - 0.0012)]
    q.add(mat, torno_x(perf, 56))
    q.add(mat, solido(arred([(0.009, -0.025), (0.039, -0.025), (0.039, -0.008), (0.009, -0.008)], 0.004), -0.0062, 0.0062, 0.0008))   # ressalto da dobradica
    q.add(mat, solido(arred([(0.0, 0.012), (0.014, 0.012), (0.014, 0.0172), (0.0, 0.0172)], 0.001), -0.004, 0.004, 0.0005))         # dente da trava
    q.add('aco_inox', torno_x([(SB, 0.0), (SB + 0.0018, 0.0), (SB + 0.0018, 0.0025), (SB, 0.0025)], 48))                          # anel extrator
    for x in (0.07, 0.074, 0.078): q.add(mat, tubo_x(SR - 0.0002, SR + 0.0004, x, x + 0.0015, sec=56))                             # aneis de pega


def _cao_sinal(q):
    perfil = arred([(-0.035, -0.009), (-0.025, -0.007), (-0.021, 0.006), (-0.024, 0.02), (-0.034, 0.03), (-0.049, 0.031), (-0.05, 0.026),
                    (-0.04, 0.021), (-0.033, 0.01), (-0.037, -0.002)], 0.0016)
    q.add('aco_oxidado', solido(perfil, -0.0032, 0.0032, 0.0008))
    for i in range(5):                                                                          # serrilhas da espora
        a = -0.04 - i * 0.0022
        q.add('aco_oxidado', caixa(a - 0.0005, a + 0.0005, 0.0285, 0.0322, -0.0034, 0.0034))
    q.add('aco_inox', cil_z(0.0022, -0.0036, 0.0036, -0.03, -0.004, 16))


def _trava_sinal(q):
    lev = arred([(-0.009, 0.004), (0.006, 0.006), (0.008, 0.012), (0.002, 0.016), (-0.009, 0.013)], 0.0018)
    q.add('aco_oxidado', solido(lev, -0.0142, -0.0126, 0.0004))
    q.add('aco_oxidado', cil_z(0.0028, -0.0145, -0.0122, -0.004, 0.009, 16))


def _sinalizadora(A, mat='aluminio_laranja'):
    A.pivo = (-0.058, -0.06, 0.0)
    _armacao_sinal(A.base, mat)
    cano = A.parte('cano', (SH[0], SH[1], 0), explodir=(0.04, 0.02, 0), tipo='gira', eixo='z', curso_graus=SGIRO,
                   descricao='bascula para baixo (a boca desce) e mostra a culatra para trocar o cartucho')
    _cano_sinal(cano, mat)
    car = A.parte('cartucho', (0, 0, 0), pai='cano', explodir=(-0.08, 0.02, 0), tipo='remove', direcao=[-1.0, 0.0, 0.0], municao='cartucho_sinal_vermelho',
                  capacidade=1, descricao='cartucho de sinal na câmara; sai para trás com o cano aberto')
    car.merge(_cartucho_sinal('casco_vermelho'), np.eye(4))
    cao = A.parte('cao', (-0.03, -0.004, 0), explodir=(-0.02, 0.04, 0), tipo='gira', eixo='z', curso_graus=SCAO, descricao='cão externo: armar puxando para trás')
    _cao_sinal(cao)
    gat = A.parte('gatilho', (0.002, -0.027, 0), explodir=(0, -0.04, 0), tipo='gira', eixo='z', curso_graus=-12, descricao='gatilho')
    _gatilho_em(gat, 0.002, -0.027, larg=0.0028)
    tr = A.parte('trava', (-0.004, 0.009, 0), explodir=(0, 0, -0.04), tipo='gira', eixo='z', curso_graus=28, descricao='alavanca da esquerda que solta o cano')
    _trava_sinal(tr)
    A.encaixe('encaixe_cartucho', (0, 0, 0), 'cartucho_sinal', pai='cano', substitui='cartucho', aceita=['cartucho_sinal_vermelho', 'cartucho_sinal_verde'],
              padrao='cartucho_sinal_vermelho', descricao='filho do cano; o cartucho escolhido troca o nó cartucho (vermelho = socorro, verde = chamar)')
    A.encaixe('mira_ferro', (-0.036, 0.0185, 0), 'mira', descricao='linha de visada pelas estrias do topo e o dente do cano (mira grossa, só para apontar)')
    A.encaixe('boca_fogo', (SL, 0, 0), 'efeito', pai='cano', descricao='origem do sinal (-Z): solta o efeito sinal_luz_* que sobe ~80 m')
    A.encaixe('saida_estojo', (-0.01, 0.012, 0), 'efeito', descricao='o estojo vazio sai daqui na recarga (aos 0,7 s)')
    cao_r = lambda ks: ('cao', 'r', (0, 0, 1), pose(ks))
    cano_r = lambda ks: ('cano', 'r', (0, 0, 1), pose(ks))
    car_t = lambda ks: ('cartucho', 't', pose([(t, (dx, dy, 0)) for t, dx, dy in ks]))
    A.anim('atirar', 0.7, [cao_r([(0, SCAO), (0.03, 0), (0.7, 0)]), ('gatilho', 'r', (0, 0, 1), pose([(0, 0), (0.03, -12), (0.15, -12), (0.3, 0)])),
                           (None, 'r', (0, 0, 1), pose([(0, 0), (0.03, 0), (0.08, 14), (0.45, 0)])),
                           (None, 't', pose([(0, (0, 0, 0)), (0.03, (0, 0, 0)), (0.07, (-0.02, 0.006, 0)), (0.45, (0, 0, 0))]))],
           desc='o cão cai (0,03 s) e o coice levanta bem a boca: o sinal sai em boca_fogo')
    A.anim('armar', 0.4, [cao_r([(0, 0), (0.3, SCAO), (0.4, SCAO)])], desc='puxa o cão para trás com o polegar')
    A.anim('recarregar', 2.8, [('trava', 'r', (0, 0, 1), pose([(0, 0), (0.15, 28), (0.35, 28), (0.45, 0), (2.25, 0), (2.35, 28), (2.45, 0)])),
                               cano_r([(0, 0), (0.2, 0), (0.45, SGIRO), (2.1, SGIRO), (2.3, 0)]),
                               car_t([(0, 0, 0), (0.5, 0, 0), (0.62, -0.025, 0), (0.75, -0.07, -0.02), (0.9, -0.1, -0.12), (1.3, -0.1, -0.12),
                                      (1.5, -0.07, 0.0), (1.75, -0.03, 0.0), (1.95, 0, 0)]),
                               cao_r([(0, 0), (2.4, 0), (2.7, SCAO), (2.8, SCAO)]),
                               (None, 'r', (1, 0, 0), pose([(0, 0), (0.3, 18), (2.2, 18), (2.6, 0)]))],
           desc='solta a trava, o cano bascula (0,45 s), o estojo sai (0,62 a 0,9 s), o cartucho novo entra (1,5 a 1,95 s; trocar o nó entre 0,9 e 1,3 s), '
                'fecha o cano (2,3 s) e arma o cão (2,7 s)')
    A.anim('inspecionar', 2.4, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.4, -30), (1.0, -30), (1.4, 35), (1.9, 35), (2.4, 0)])),
                                cano_r([(0, 0), (0.5, 0), (0.7, SGIRO * 0.6), (1.1, SGIRO * 0.6), (1.3, 0)]),
                                ('trava', 'r', (0, 0, 1), pose([(0, 0), (0.45, 0), (0.55, 28), (0.65, 0)]))],
           desc='abre o cano até ver a cor do cartucho, fecha e mostra o outro lado')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 0.6), (3.0, 0)]))], laco=True, desc='respiração leve parado')


@arma('pistola_sinalizadora', 'Pistola sinalizadora', 'armas', 'pistola', classe='fogo', calibre='sinal 12', municao='cartucho_sinal_vermelho',
      municoes=['cartucho_sinal_vermelho', 'cartucho_sinal_verde'], capacidade=1, dano=25, dano_fogo=8, alcance_m=15, alcance_max_m=60,
      modo='tiro único, cão externo', acao='basculante', tiros_por_s=0.3, recarga_s=2.8, precisao=0.4, recuo=0.35, ruido_m=90, durabilidade=800,
      peso_kg=0.45, raridade='incomum', valor_troca=45, onde=['posto', 'quartel_bombeiros', 'casa_de_campo', 'armazem', 'estacao'], estojo_s=0.7,
      descricao='Pistola de sinal de alumínio laranja, um tiro por vez. Não é arma: o sinal sobe uns 80 m e brilha 7 s. Vermelho pede socorro; '
                'verde chama sobreviventes para a sua posição, mas os zumbis também veem. De perto, o cartucho queima o alvo.')
def pistola_sinalizadora(A): _sinalizadora(A)


@arma('cartucho_sinal_vermelho', 'Cartucho de sinal vermelho', 'municao', 'municao', calibre='sinal 12', peso_kg=0.03, empilha=12, raridade='incomum',
      estojo='estojo_sinal', efeito='sinal_luz_vermelha', sobe_m=80, brilha_s=7, visto_m=1500, atrai_zumbis_m=250, uso='socorro',
      descricao='Sinal de socorro: quem está no rádio ou nas torres vê de longe. Zumbis num raio de 250 m vão para onde ele cai.')
def cartucho_sinal_vermelho(A): A.base.merge(_cartucho_sinal('casco_vermelho'), np.eye(4)); A.pivo = (0, 0, 0)


@arma('cartucho_sinal_verde', 'Cartucho de sinal verde', 'municao', 'municao', calibre='sinal 12', peso_kg=0.03, empilha=12, raridade='raro',
      estojo='estojo_sinal', efeito='sinal_luz_verde', sobe_m=80, brilha_s=7, visto_m=1500, atrai_zumbis_m=300, uso='chamar_sobreviventes',
      descricao='Chama sobreviventes para a sua posição (pode render um novo morador). Mas o brilho verde também atrai os zumbis num raio de 300 m.')
def cartucho_sinal_verde(A): A.base.merge(_cartucho_sinal('casco_verde'), np.eye(4)); A.pivo = (0, 0, 0)


@arma('estojo_sinal', 'Estojo de sinal (vazio)', 'municao', 'estojo', calibre='sinal 12', peso_kg=0.01,
      descricao='Estojo vazio que sai na recarga (o jogo cria um em saida_estojo).')
def estojo_sinal(A): A.base.merge(_cartucho_sinal('casco_vermelho', 24, vazio=True), np.eye(4)); A.pivo = (0, 0, 0)


def _sinal_luz(A, nucleo, halo):
    q = A.base
    q.add(nucleo, trimesh.creation.icosphere(3, 0.03))
    q.add(halo, trimesh.creation.icosphere(2, 0.075))
    for i in range(4):                                                         # rastro de fumaca/brilho para baixo
        q.add(halo, trimesh.creation.icosphere(1, 0.025 - i * 0.004).apply_translation([0, -0.06 - i * 0.05, 0]))
    A.pivo = (0, 0, 0)


@arma('sinal_luz_vermelha', 'Luz do sinal vermelho', 'efeitos', 'efeito', descricao='Bola de luz que sobe até ~80 m e desce devagar por 7 s. '
      'Pôr uma luz omnidirecional vermelha forte no centro e piscar a escala (0,9 a 1,1). Material emissivo com transparência no halo.')
def sinal_luz_vermelha(A): _sinal_luz(A, 'sinal_vermelho', 'clarao_sinal_vermelho')


@arma('sinal_luz_verde', 'Luz do sinal verde', 'efeitos', 'efeito', descricao='Igual ao vermelho, em verde. Pôr uma luz omnidirecional verde forte no centro.')
def sinal_luz_verde(A): _sinal_luz(A, 'sinal_verde', 'clarao_sinal_verde')


CXS = dict(x0=-0.04, x1=0.04, y0=0.0, y1=0.074, z0=-0.027, z1=0.027)
ATLAS_S = {'topo': (0, 0), 'lado+': (0, 240), 'lado-': (0, 560), 'ponta+': (360, 240), 'ponta-': (360, 560)}


def _arte_caixa_sinal(cor, nome):
    im = _arte_caixa(CXS, 'SINAL', '6 CARTUCHOS', nome, cor=cor, atlas=ATLAS_S)
    d = ImageDraw.Draw(im)
    L = int((CXS['x1'] - CXS['x0']) * PXM); P_ = int((CXS['z1'] - CXS['z0']) * PXM)
    d.rectangle([0, 0, L, P_], fill=(236, 230, 212)); d.rectangle([0, 0, 96, P_], fill=cor)
    texto_c(d, (48, P_ // 2), 'SOS' if 'VERMELHO' in nome else 'AQUI', 30, (250, 240, 220), larg=84)
    cx = 96 + (L - 96) // 2
    texto_c(d, (cx, 40), 'GUARDIÃO', 38, cor, larg=L - 116)
    texto_c(d, (cx, 92), 'SINAL ' + nome.split()[-1], 30, (40, 30, 26), larg=L - 116)
    texto_c(d, (cx, 138), '6 CARTUCHOS', 24, (40, 30, 26), larg=L - 116)
    texto_c(d, (cx, 178), 'SOBE 80 m · 7 s', 20, (90, 70, 60), False, larg=L - 116)
    d.rectangle([106, P_ - 22, L - 10, P_ - 12], fill=cor)
    return im


@arma('caixa_sinal_vermelho', 'Caixa de sinais vermelhos (6)', 'municao', 'caixa', calibre='sinal 12', municao='cartucho_sinal_vermelho', quantidade=6,
      peso_kg=0.22, empilha=4, raridade='incomum', onde=['posto', 'quartel_bombeiros', 'armazem'],
      descricao='Caixa de papelão com 6 cartuchos de sinal vermelho em pé. A tampa abre (nó "tampa", animação "abrir").')
def caixa_sinal_vermelho(A):
    caixa_municao(A, 'rotulo_sinal_vermelho', CXS, _arte_caixa_sinal((170, 34, 28), 'VERMELHO'), _cartucho_sinal('casco_vermelho', 20),
                  3, 2, 0.025, 0.025, faltam=(), bandeja=0.04, atlas=ATLAS_S)


@arma('caixa_sinal_verde', 'Caixa de sinais verdes (6)', 'municao', 'caixa', calibre='sinal 12', municao='cartucho_sinal_verde', quantidade=6,
      peso_kg=0.22, empilha=4, raridade='raro', onde=['quartel_bombeiros', 'estacao'],
      descricao='Caixa de papelão com 6 cartuchos de sinal verde em pé. A tampa abre (nó "tampa", animação "abrir").')
def caixa_sinal_verde(A):
    caixa_municao(A, 'rotulo_sinal_verde', CXS, _arte_caixa_sinal((34, 120, 56), 'VERDE'), _cartucho_sinal('casco_verde', 20),
                  3, 2, 0.025, 0.025, faltam=(5,), bandeja=0.04, atlas=ATLAS_S)
