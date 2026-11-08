# Arma 18: facao (lamina longa de aco carbono escurecido que alarga na ponta, fio claro, espiga inteira aparente entre talas de
# madeira presas com rebites de latao, bico no fim do cabo e fiel de couro) e bainha de lona com ponteira e boca de couro.
# Executado por gerar_armas.py depois de arma18_faca.py (usa _loft_x, corpo_x). Desenho proprio, sem marca.
# Plano de lado: x frente (ponta), y cima (dorso), z espessura. Pivo no meio do cabo.
CORES.update({'lona': (150, 140, 104), 'lona_escura': (110, 104, 78)})
METAL.update({'lona': (0.0, 0.96), 'lona_escura': (0.0, 0.96)})

FC_PONTA = 0.34


def _dorso_c(x):
    if x <= 0.22: return 0.0135 + 0.0025 * (x / 0.22)
    s = (x - 0.22) / (FC_PONTA - 0.22); return 0.016 - 0.011 * s ** 1.8


def _fio_c(x):
    if x < 0.012: return -0.017
    if x <= 0.27: return -0.017 - 0.013 * ((x - 0.012) / 0.258) ** 1.4
    s = (x - 0.27) / (FC_PONTA - 0.27); return -0.03 + 0.035 * s ** 1.7


def _esp_c(x): return 0.0015 if x < 0 else 0.0015 - 0.0006 * (x / FC_PONTA)


def _sec_c(x):
    yt, yb, t = _dorso_c(x), _fio_c(x), _esp_c(max(x, 0)); e = 0.00012; yg = yb + 0.3 * (yt - yb)
    return [(t * 0.8, yt), (-t * 0.8, yt), (-t, yt - 0.0007), (-t, yg), (-e, yb), (e, yb), (t, yg), (t, yt - 0.0007)]


def _sec_fio_c(x):
    yt, yb, t = _dorso_c(x), _fio_c(x), _esp_c(x); e = 0.00012; yg = yb + 0.3 * (yt - yb)
    h = min(0.0035, 0.3 * (yt - yb)); z1 = e + (t - e) * h / (yg - yb); o = 0.00005
    return [(z1 + o, yb + h), (-(z1 + o), yb + h), (-(e + o), yb - o), (e + o, yb - o)]


def _contorno_facao(folga=0.0):
    xs = np.linspace(0.0, FC_PONTA, 90)
    pg = Polygon([(x, _dorso_c(x)) for x in xs] + [(x, _fio_c(x)) for x in xs[::-1]])
    return pg.buffer(folga, 12) if folga else pg


CONT_CABO_C = Polygon(suave([(-0.002, 0.0135), (-0.06, 0.0152), (-0.11, 0.0145), (-0.128, 0.0125), (-0.138, 0.004), (-0.142, -0.012), (-0.136, -0.026),
                             (-0.128, -0.022), (-0.115, -0.0165), (-0.07, -0.0185), (-0.03, -0.0165), (-0.008, -0.0185), (-0.002, -0.017)], 3))
LARG_CABO_C = lambda x: 0.0098 + 0.0012 * math.exp(-((x + 0.07) / 0.04) ** 2)
REBITES_C = [(-0.025, -0.001), (-0.07, -0.0015), (-0.112, -0.001)]


def _facao(A):
    q = A.base
    xs = list(np.linspace(-0.002, FC_PONTA - 0.002, 120)); ult = _sec_c(FC_PONTA - 0.002); yc = float(np.mean([y for _, y in ult]))
    lam = _loft_x([(x, _sec_c(x)) for x in xs] + [(FC_PONTA, [(z * 0.1, yc + (y - yc) * 0.1) for z, y in ult])])
    q.add('aco_fosfatado', lam)
    q.add('aco_inox', _loft_x([(x, _sec_fio_c(x)) for x in np.linspace(0.014, FC_PONTA - 0.002, 110)]))
    # espiga inteira aparente (aco) entre as talas, rebites de latao e furo do fiel
    furo = cil_z(0.0035, -0.02, 0.02, -0.13, -0.008, 18)
    q.add('aco_oxidado', menos(solido(CONT_CABO_C.buffer(0.0005), -0.0015, 0.0015, 0.0003), furo))
    nucleo = corpo_x(CONT_CABO_C, -0.002, -0.142, LARG_CABO_C, n=2.2, fatias=130, voltas=44, raio_tras=0.003, raio_frente=0.0012)
    talas = menos(nucleo, caixa(-1, 1, -1, 1, -0.0015, 0.0015), furo, *[cil_z(0.0026, -0.02, 0.02, x, y, 16) for x, y in REBITES_C])
    q.add('nogueira', talas)
    for x, y in REBITES_C:
        zt = LARG_CABO_C(x) * 0.93
        q.add('latao', menos(cil_z(0.0026, -zt, zt, x, y, 20), cil_z(0.0012, -0.02, 0.02, x, y, 12)))
    q.add('aco_inox', menos(cil_z(0.0036, -0.0102, 0.0102, -0.13, -0.008, 20), cil_z(0.0028, -0.02, 0.02, -0.13, -0.008, 18)))   # ilhos do fiel
    # fiel de couro (laco passando pelo furo e pendendo para baixo)
    pts = _catmull([(-0.13, -0.008 + 0.002, 0.004), (-0.136, -0.016, 0.012), (-0.145, -0.04, 0.006), (-0.15, -0.065, 0.0), (-0.145, -0.04, -0.006),
                    (-0.136, -0.016, -0.012), (-0.13, -0.008 + 0.002, -0.004)], 6)
    for i in range(len(pts) - 1): q.add('couro', _haste(pts[i], pts[i + 1], 0.0016, 8))
    q.add('couro_escuro', cil_z(0.0034, -0.003, 0.003, -0.15, -0.058, 14))           # passador do fiel
    A.pivo = (-0.065, 0.0, 0.0)
    A.encaixe('cinto', (0.12, 0.0, -0.012), 'bainha_facao', aceita=['bainha_lona_facao'], descricao='o facão entra na bainha pelo pivô (a bainha tem o encaixe "arma")')
    A.encaixe('ponta', (FC_PONTA, 0.005, 0.0), 'efeito', descricao='ponta da lâmina')
    A.encaixe('fio_meio', (0.22, -0.026, 0.0), 'efeito', descricao='parte larga do fio, onde o golpe pesa (teste de acerto)')
    A.anim('golpear', 0.6, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.15, 35), (0.32, -45), (0.6, 0)])), (None, 'r', (1, 0, 0), pose([(0, 0), (0.15, 25), (0.32, -15), (0.6, 0)])),
                            (None, 't', pose([(0, (0, 0, 0)), (0.15, (-0.04, 0.06, 0)), (0.32, (0.08, -0.07, 0)), (0.6, (0, 0, 0))]))],
           desc='golpe na diagonal (de cima à direita para baixo à esquerda): acerto entre 0,18 e 0,32 s no encaixe fio_meio')
    A.anim('golpe_forte', 1.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (0.4, 80), (0.48, 80), (0.66, -50), (1.0, 0)])),
                                (None, 't', pose([(0, (0, 0, 0)), (0.4, (-0.08, 0.14, 0)), (0.48, (-0.08, 0.14, 0)), (0.66, (0.1, -0.1, 0)), (1.0, (0, 0, 0))]))],
           desc='levanta acima da cabeça e desce com força (corta galho e cabeça de zumbi): acerto entre 0,52 e 0,66 s; gasta mais fôlego')
    A.anim('cortar_mato', 0.5, [(None, 'r', (0, 1, 0), pose([(0, 0), (0.12, 40), (0.3, -40), (0.5, 0)])), (None, 'r', (1, 0, 0), pose([(0, 0), (0.12, -70), (0.3, -70), (0.5, 0)]))],
           desc='golpe baixo de lado para abrir caminho no mato')
    A.anim('sacar', 0.65, [(None, 't', pose([(0, (-0.1, -0.38, 0.06)), (0.35, (0.0, -0.06, 0.01)), (0.65, (0, 0, 0))])), (None, 'r', (0, 0, 1), pose([(0, -90), (0.35, -20), (0.65, 0)]))],
           desc='tira da bainha na cintura')
    A.anim('guardar', 0.65, [(None, 't', pose([(0, (0, 0, 0)), (0.3, (0.0, -0.06, 0.01)), (0.65, (-0.1, -0.38, 0.06))])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.3, -20), (0.65, -90)]))],
           desc='volta para a bainha')
    A.anim('inspecionar', 2.2, [(None, 'r', (1, 0, 0), pose([(0, 0), (0.6, 180), (1.4, 180), (2.2, 360)])), (None, 'r', (0, 0, 1), pose([(0, 0), (0.6, 12), (1.6, 12), (2.2, 0)]))],
           desc='vira o facão olhando o fio dos dois lados')
    A.anim('ocioso', 3.0, [(None, 'r', (0, 0, 1), pose([(0, 0), (1.5, 1.0), (3.0, 0)])), (None, 't', pose([(0, (0, 0, 0)), (1.5, (0, 0.0015, 0)), (3.0, (0, 0, 0))]))],
           laco=True, desc='respiração leve parado')


@arma('facao', 'Facão de mato', 'armas', 'facao', classe='corpo_a_corpo', calibre='lâmina', capacidade='-', dano=60, dano_golpe_forte=90, alcance_m=0.85,
      tiros_por_s=1.3, precisao=1.0, ruido_m=2, durabilidade=2600, peso_kg=0.62, raridade='comum', valor_troca=22, corta_vegetacao=True, prende_no_alvo=0.1,
      onde=['casa_de_campo', 'fazenda', 'armazem', 'loja_caca', 'galpao'],
      descricao='Lâmina de 34 cm de aço carbono escurecido que alarga na ponta para pesar no golpe. Talas de madeira com rebites de latão e fiel de couro. '
                'Alcança mais que a faca e abre caminho no mato, mas o golpe é mais lento.')
def facao(A): _facao(A)


@_acessorio('bainha_lona_facao', 'Bainha de lona (facão)', 'bainha', 'bainha_facao', peso_kg=0.18, raridade='comum', valor_troca=6, modificadores={'sacar_s': 0.9},
            onde=['casa_de_campo', 'fazenda', 'armazem'],
            descricao='Bainha de lona costurada com ponteira e boca de couro, passador largo de cinto e tira com fivela por cima do cabo.')
def bainha_lona_facao(A):
    q = A.base
    sil = _contorno_facao(0.0055).union(sbox(-0.006, -0.026, 0.02, 0.0215)).intersection(sbox(-0.0065, -0.06, 0.5, 0.06))
    q.add('lona', solido(sil, -0.0085, 0.0085, 0.0045))
    borda = sil.buffer(-0.0026).exterior                                                  # costura dupla nas bordas
    for k in np.linspace(0.0, 1.0, 150, endpoint=False):
        p = borda.interpolate(k, normalized=True); p2 = borda.interpolate(k + 0.003, normalized=True)
        for zs in (-1, 1):
            z = zs * 0.0083
            q.add('costura', _haste([p.x, p.y, z], [p2.x, p2.y, z], 0.00045, 5))
    # ponteira e boca de couro
    q.add('couro', inter([solido(sil.buffer(0.0007), -0.0092, 0.0092, 0.0045), caixa(FC_PONTA - 0.05, 1, -1, 1, -1, 1)]))
    q.add('couro_escuro', inter([solido(sil.buffer(0.0007), -0.0092, 0.0092, 0.0045), caixa(-1, 0.028, -1, 1, -1, 1)]))
    for y in (0.012, -0.018):
        for zs in (-1, 1): q.add('latao', cil_z(0.0018, min(zs * 0.0091, zs * 0.0097), max(zs * 0.0091, zs * 0.0097), 0.012, y, 12))
    # passador de cinto (atras, z-) e tira com fivela por cima do cabo
    q.add('lona_escura', solido(arred([(0.06, -0.02), (0.13, -0.02), (0.13, 0.068), (0.06, 0.068)], 0.004), -0.0125, -0.0085, 0.0015))
    q.add('lona_escura', solido(arred([(0.06, 0.04), (0.13, 0.04), (0.13, 0.068), (0.06, 0.068)], 0.004), -0.0175, -0.0125, 0.0015))
    for x in (0.066, 0.124):
        for y in np.linspace(-0.016, 0.064, 18): q.add('costura', caixa(x - 0.0004, x + 0.0004, y, y + 0.0025, -0.0127, -0.0123))
    tira = menos(corpo_x(CONT_CABO_C, -0.02, -0.04, lambda x: LARG_CABO_C(x) + 0.0022, n=2.2, fatias=20, voltas=40),
                 corpo_x(CONT_CABO_C, -0.012, -0.046, lambda x: LARG_CABO_C(x) + 0.0004, n=2.2, fatias=20, voltas=40), caixa(-1, 1, -1, 0.004, -1, 1))
    q.add('couro', tira)
    for zs in (-1, 1):
        q.add('couro', solido(arred([(-0.04, 0.004), (-0.02, 0.004), (-0.002, -0.006), (0.006, -0.006), (0.006, -0.022), (-0.034, -0.02)], 0.003),
                              min(zs * 0.0122, zs * 0.0088), max(zs * 0.0122, zs * 0.0088), 0.0008))
    q.add('aco_inox', menos(solido(arred([(-0.036, -0.002), (-0.024, -0.002), (-0.024, 0.01), (-0.036, 0.01)], 0.002), 0.0122, 0.0142, 0.0004),
                            solido(arred([(-0.034, 0.0), (-0.026, 0.0), (-0.026, 0.008), (-0.034, 0.008)], 0.001), 0.0, 0.02)))   # fivela
    A.encaixe('arma', (-0.065, 0.0, 0.0), 'efeito', descricao='ponha o facão aqui (pivô do facão) para guardá-lo na bainha')
    A.pivo = (0.12, 0.0, -0.012)
