# Lote 16: bancadas e estacoes do abrigo (fase 2): onde se fabrica o que nao da para fazer a mao.
# Executado por gerar_props.py (usa as mesmas funcoes e materiais dos lotes anteriores).
# Campos: estacao (texto do jogo), constroi/ferramenta (receita da propria estacao), produz {item, qtd, a_cada_min, consome}
#         (estacoes que geram recurso sozinhas com um morador trabalhando), trabalha (vagas de morador), ponto_uso [x, y, z]
#         (onde o personagem fica de pe para usar, na frente da peca). O que cada estacao fabrica sai em CRAFT.md (craft.estacao).
CORES.update({'tambor_azul': (8, 30, 80), 'tambor_preto': (12, 12, 14), 'fuligem': (14, 13, 12), 'trilho': (60, 58, 56), 'couro_fole': (70, 40, 20),
              'barro_forno': (120, 70, 44), 'tecido_estampa': (150, 90, 40), 'esmalte_branco': (220, 220, 214), 'latao_velho': (150, 110, 50),
              'verde_compostagem': (40, 34, 20), 'carne_seca': (80, 22, 14), 'erva': (40, 80, 30), 'cobre_bobina': (150, 80, 40)})
METALICOS.update({'tambor_azul': (0.3, 0.5), 'tambor_preto': (0.4, 0.6), 'trilho': (0.9, 0.55), 'latao_velho': (0.9, 0.4), 'cobre_bobina': (0.95, 0.35)})
FOSCOS.update({'fuligem': 0.95, 'carne_seca': 0.6, 'erva': 0.8, 'esmalte_branco': 0.3})
TEX_PROPRIAS += [('couro_fole', 'couro', 0.25, 1024), ('barro_forno', 'barro', 0.5, 512), ('tecido_estampa', 'xadrez', 0.5, 768),
                 ('verde_compostagem', 'barro', 0.5, 512)]


def _cavalete(p, x, H=0.78, Z=0.32, mat='madeira_crua'):
    """Cavalete de serrar: travessa em cima e quatro pernas abertas em A."""
    p.cham(mat, x - 0.04, x + 0.04, H - 0.09, H, -Z - 0.05, Z + 0.05, 0.004)
    for zs in (-1, 1):
        for xs in (-1, 1): p.seg(mat, (x + xs * 0.03, H - 0.07, zs * Z), (x + xs * 0.17, 0.02, zs * (Z + 0.08)), 0.045, 0.045)
        p.seg(mat, (x - 0.12, 0.25, zs * (Z + 0.06)), (x + 0.12, 0.25, zs * (Z + 0.06)), 0.07, 0.02)


def _tambor(p, c, R=0.29, H=0.88, mat='tambor_azul', deitado=False, tampa=True):
    """Tambor de 200 L com frisos; deitado = eixo x."""
    eixo = 'x' if deitado else 'y'; x, y, z = c
    if deitado:
        anel(p, mat, R - 0.002, R, x - H / 2, x + H / 2, 40, 'x', (0, y, z))
        for k in (-0.3, 0.0, 0.3): anel(p, mat, R - 0.001, R + 0.006, x + k * H - 0.01, x + k * H + 0.01, 40, 'x', (0, y, z))
        for s in (-1, 1): anel(p, mat, R - 0.004, R + 0.004, x + s * H / 2 - 0.012 * (s > 0), x + s * H / 2 + 0.012 * (s < 0), 40, 'x', (0, y, z))
    else:
        anel(p, mat, R - 0.002, R, y, y + H, 40, 'y', (x, 0, z))
        for k in (0.3, 0.65): anel(p, mat, R - 0.001, R + 0.006, y + k * H - 0.01, y + k * H + 0.01, 40, 'y', (x, 0, z))
        for yy in (y, y + H - 0.02): anel(p, mat, R - 0.004, R + 0.004, yy, yy + 0.02, 40, 'y', (x, 0, z))
        torno(p, mat, [(R - 0.002, y + 0.01), (R - 0.002, y + 0.014)], 40, 'y', (x, 0, z))
        if tampa: torno(p, mat, [(R - 0.002, y + H - 0.016), (R - 0.002, y + H - 0.012)], 40, 'y', (x, 0, z))


def _chamine(p, x0, y0, z0, alt, r=0.06, mat='tambor_preto'):
    anel(p, mat, r - 0.002, r, y0, y0 + alt, 20, 'y', (x0, 0, z0))
    for y in np.arange(y0 + 0.4, y0 + alt, 0.5): anel(p, mat, r, r + 0.004, y, y + 0.02, 20, 'y', (x0, 0, z0))
    torno(p, mat, [(r + 0.06, y0 + alt + 0.05), (0.0, y0 + alt + 0.11)], 20, 'y', (x0, 0, z0))            # chapeu
    for k in range(3):
        a = k * 2 * math.pi / 3; p.seg(mat, (x0 + r * math.cos(a), y0 + alt - 0.01, z0 + r * math.sin(a)), (x0 + (r + 0.05) * math.cos(a), y0 + alt + 0.055, z0 + (r + 0.05) * math.sin(a)), 0.006, 0.006)


def _frasco(p, c, r=0.025, h=0.08, mat='ambar', tampa='plastico_branco'):
    torno(p, mat, [(r, c[1]), (r, c[1] + h * 0.8), (r * 0.55, c[1] + h * 0.9), (r * 0.5, c[1] + h)], 16, 'y', (c[0], 0, c[2]))
    torno(p, tampa, [(r * 0.55, c[1] + h), (r * 0.55, c[1] + h + 0.014)], 14, 'y', (c[0], 0, c[2]))


# ---------------------------------------------------------------------------- OFICINAS
@item('bancada_carpintaria', 'Bancada de carpintaria de cavaletes', 'mobilias', 'oficina', comodos=['abrigo', 'serraria', 'garagem', 'fazenda'],
      constroi={'tabua': 6, 'caixa_pregos': 1}, ferramenta='serrote', fase=2, trabalha=1, ponto_uso=[0.0, 0.0, 0.75],
      estacao='carpintaria (tábuas viram móveis, barricadas reforçadas, cabos de ferramenta e flechas)')
def bancada_carpintaria(M):
    p = M.base; X, Z, H = 1.0, 0.4, 0.86
    for x in (-0.7, 0.7): _cavalete(p, x, H - 0.045, 0.3)
    q = P(); almofadada(q, 'madeira_escura', -X, X, -Z, Z, 0.0, 0.045, borda=0.1, n=2)                     # porta velha deitada como tampo
    q.parts['madeira_escura'] = [m.apply_transform(_rot(-math.pi / 2, [1, 0, 0])) or m for m in q.parts['madeira_escura']]
    p.merge(q, trimesh.transformations.translation_matrix([0, H, 0]))
    torno(p, 'latao', [(0.025, 0.0), (0.03, 0.012)], 16, 'z', (-0.45, H - 0.02, Z + 0.002))                 # macaneta que sobrou
    # serrote, esquadro, grampo sargento e tabua sendo cortada
    p.cham('madeira_crua', -0.2, 0.9, H + 0.045, H + 0.07, -0.25, -0.11, 0.003)
    p.hull('aco', [(0.3, H + 0.072, -0.08), (0.68, H + 0.072, -0.03), (0.68, H + 0.072, 0.04), (0.3, H + 0.072, 0.07)] + [(x, H + 0.073, z) for x, z in ((0.3, -0.08), (0.68, 0.04))])
    p.cham('madeira', 0.18, 0.3, H + 0.07, H + 0.095, -0.03, 0.08, 0.008)
    p.cham('aco', -0.75, -0.45, H + 0.045, H + 0.049, 0.1, 0.14, 0.001); p.cham('aco', -0.75, -0.71, H + 0.045, H + 0.049, 0.14, 0.32, 0.001)
    q = P(); q.cham('aco_pintado', -0.012, 0.012, -0.12, 0.08, -0.008, 0.008, 0.002); q.cham('aco_pintado', -0.012, 0.012, 0.06, 0.08, -0.008, 0.08, 0.002)
    q.cham('aco_pintado', -0.012, 0.012, -0.12, -0.1, -0.008, 0.08, 0.002); cyl_eixo(q, 'aco_polido', 0.005, -0.1, 0.06, 'y', (0, 0, 0.07), 10)
    q.cham('madeira', -0.015, 0.015, -0.18, -0.12, 0.055, 0.085, 0.006)
    p.merge(q, trimesh.transformations.translation_matrix([0.0, H + 0.06, -Z + 0.02]))
    for x, z in ((-0.9, -0.3), (0.85, 0.3)): torno(p, 'madeira_crua', [(0.0, 0.0), (0.03, 0.0)], 8, 'y', (x, H + 0.045, z))   # serragem
    rng = np.random.default_rng(3)
    for i in range(40):
        x, z = rng.uniform(-1.1, 1.1), rng.uniform(-0.5, 0.5); fofo(p, 'madeira_crua', x, 0.002, z, rng.uniform(0.01, 0.03), 0.002, rng.uniform(0.005, 0.015), 0.7, 0.7, (4, 6))


@item('bancada_costura', 'Mesa de costura com máquina manual', 'mobilias', 'oficina', comodos=['abrigo', 'casas', 'galeria', 'hotel'],
      fase=2, trabalha=1, ponto_uso=[0.0, 0.0, 0.6], sentar=True,
      estacao='costura (roupas, mochilas, coletes acolchoados, sacos e lona de barraca)')
def bancada_costura(M):
    p = M.base; X, Z, H = 0.55, 0.3, 0.76
    p.cham('madeira', -X, X, H - 0.03, H, -Z, Z, 0.006)
    for xs in (-1, 1):                                                                                      # pes de ferro fundido em lira
        x = xs * (X - 0.07)
        p.cham('aco_pintado', x - 0.012, x + 0.012, 0.0, 0.03, -Z + 0.02, Z - 0.02, 0.004)
        for zs in (-1, 1): p.seg('aco_pintado', (x, 0.03, zs * (Z - 0.03)), (x, H - 0.04, zs * (Z - 0.06)), 0.02, 0.03)
        if xs > 0: torno(p, 'aco_pintado', [(0.09, 0.0), (0.09, 0.02)], 24, 'x', (x, 0.42, 0))
    p.seg('aco_pintado', (-X + 0.07, 0.12, 0.0), (X - 0.07, 0.12, 0.0), 0.025, 0.025)
    p.cham('aco_pintado', -0.2, 0.2, 0.06, 0.08, 0.05, 0.25, 0.004)                                          # pedal
    for x in np.linspace(-0.18, 0.18, 10): p.box('aco_pintado', x - 0.004, x + 0.004, 0.08, 0.082, 0.06, 0.24)
    anel(p, 'aco_pintado', 0.18, 0.2, X - 0.12, X - 0.1, 32, 'x', (0, 0.42, 0.0))                             # volante grande
    for k in range(5):
        a = k * 2 * math.pi / 5; p.seg('aco_pintado', (X - 0.11, 0.42, 0.0), (X - 0.11, 0.42 + 0.18 * math.sin(a), 0.18 * math.cos(a)), 0.012, 0.012)
    varrer(p, 'couro_fole', circ(0.004, 6), [(X - 0.11, 0.6, 0.0), (X - 0.1, H + 0.1, -0.05)])               # correia
    # maquina: braco curvo preto com frisos dourados
    m = 'esmalte_escuro'; y0 = H
    p.cham(m, -0.22, 0.2, y0, y0 + 0.04, -0.09, 0.09, 0.01)
    p.cham(m, 0.08, 0.2, y0 + 0.04, y0 + 0.24, -0.06, 0.06, 0.02)
    p.cham(m, -0.2, 0.2, y0 + 0.2, y0 + 0.28, -0.055, 0.055, 0.025)
    p.cham(m, -0.24, -0.16, y0 + 0.1, y0 + 0.29, -0.05, 0.05, 0.015)
    cyl_eixo(p, 'aco_polido', 0.004, y0 + 0.04, y0 + 0.1, 'y', (-0.2, 0, 0.0), 8)                           # agulha e calcador
    p.cham('aco_polido', -0.215, -0.185, y0 + 0.04, y0 + 0.05, -0.02, 0.02, 0.002)
    torno(p, 'aco_polido', [(0.07, 0.0), (0.07, 0.025), (0.05, 0.03)], 28, 'x', (0.2, y0 + 0.2, 0))           # volante da maquina
    torno(p, 'madeira_escura', [(0.0, y0 + 0.28), (0.004, y0 + 0.28), (0.004, y0 + 0.33)], 8, 'y', (0.0, 0, -0.02))
    torno(p, 'tecido_almofada', [(0.012, y0 + 0.33), (0.012, y0 + 0.36)], 16, 'y', (0.0, 0, -0.02))         # carretel de linha
    img = Image.new('RGB', (512, 96), (34, 34, 36)); d = ImageDraw.Draw(img); texto_c(d, (256, 48), 'PRIMAVERA', 60, (200, 160, 70)); mat_imagem('marca_costura', img, 0.3)
    p.box('marca_costura', -0.12, 0.1, y0 + 0.21, y0 + 0.265, 0.0551, 0.0556); p.uv['marca_costura'] = lambda v, n: np.stack([(v[:, 0] + 0.12) / 0.22, (v[:, 1] - y0 - 0.21) / 0.055], 1)
    fofo(p, 'tecido_estampa', -0.35, H + 0.01, 0.05, 0.16, 0.01, 0.2, 0.4, 0.2, (8, 16)); _amassar(p, 'tecido_estampa', 0.004, 40.0, 1, sub=0)
    fofo(p, 'lona_azul', 0.4, H + 0.02, -0.1, 0.12, 0.02, 0.15, 0.4, 0.3, (8, 16))
    p.cham('aco_polido', 0.3, 0.42, H, H + 0.006, 0.15, 0.17, 0.002)                                       # tesoura simplificada
    anel(p, 'plastico_preto', 0.008, 0.014, H, H + 0.006, 14, 'y', (0.28, 0, 0.14)); anel(p, 'plastico_preto', 0.008, 0.014, H, H + 0.006, 14, 'y', (0.28, 0, 0.19))


@item('mesa_enfermaria', 'Mesa de enfermaria improvisada', 'mobilias', 'saude', comodos=['abrigo', 'clinica', 'igreja', 'escolinha'],
      constroi={'tabua': 4, 'caixa_pregos': 1, 'trapos': 2}, ferramenta='martelo', fase=2, trabalha=1, deitar=True, ponto_uso=[0.0, 0.0, 0.55],
      estacao='enfermaria (curativos melhores, tala, remédio de ervas; morador ferido se recupera 2× mais rápido deitado aqui)')
def mesa_enfermaria(M):
    p = M.base; X, Z, H = 0.95, 0.32, 0.78
    for x in (-0.65, 0.65): _cavalete(p, x, H - 0.03, 0.22)
    for z in np.linspace(-Z + 0.05, Z - 0.05, 5): _tab_h(p, -X, X, H - 0.03, H, z - 0.06, z + 0.06)
    fofo(p, 'cobertor_cinza', 0.05, H + 0.03, 0.0, 0.85, 0.03, 0.29, 0.25, 0.15, (10, 24)); _amassar(p, 'cobertor_cinza', 0.005, 25.0, 2, sub=0)
    fofo(p, 'lencol', 0.05, H + 0.062, 0.0, 0.8, 0.008, 0.27, 0.3, 0.15, (8, 20))
    fofo(p, 'travesseiro', -0.72, H + 0.1, 0.0, 0.16, 0.045, 0.24, 0.35, 0.3, (12, 16))
    # caixote-criado ao lado com frascos, bacia e lanterna
    q = P(); carcaca(q, 'madeira_crua', -0.22, 0.22, 0.0, 0.5, -0.17, 0.17, t=0.02)
    q.box('madeira_crua', -0.2, 0.2, 0.24, 0.26, -0.17, 0.17)
    for i, (x, z, mat) in enumerate(((-0.14, -0.08, 'ambar'), (-0.08, 0.06, 'pet'), (-0.02, -0.06, 'ambar'))): _frasco(q, (x, 0.5, z), 0.022, 0.075 + 0.02 * (i % 2), mat)
    torno(q, 'esmalte_branco', [(0.07, 0.5), (0.11, 0.54), (0.115, 0.545), (0.11, 0.545), (0.065, 0.505)], 28, 'y', (0.08, 0, 0.0))     # bacia esmaltada
    anel(q, 'esmalte_escuro', 0.112, 0.116, 0.54, 0.545, 28, 'y', (0.08, 0, 0.0))
    torno(q, 'agua', [(0.09, 0.51), (0.1, 0.53)], 24, 'y', (0.08, 0, 0.0))
    for k in range(3): q.cham('atadura', -0.18 + k * 0.08, -0.12 + k * 0.08, 0.26, 0.3, -0.1, 0.1, 0.012)        # rolos de atadura na prateleira
    p.merge(q, trimesh.transformations.translation_matrix([X + 0.3, 0, 0.0]))
    img = Image.new('RGB', (256, 256), (240, 240, 236)); d = ImageDraw.Draw(img); d.rectangle([98, 40, 158, 216], fill=(180, 20, 20)); d.rectangle([40, 98, 216, 158], fill=(180, 20, 20)); mat_imagem('cruz_enf', img, 0.6)
    p.box('cruz_enf', X + 0.2, X + 0.4, 0.2, 0.4, 0.1701, 0.1706); p.uv['cruz_enf'] = lambda v, n: np.stack([(v[:, 0] - X - 0.2) / 0.2, (v[:, 1] - 0.2) / 0.2], 1)


@item('forja_tambor', 'Forja de tambor com fole', 'mobilias', 'oficina', comodos=['abrigo', 'ferrovelho', 'fazenda', 'fabrica'],
      constroi={'tambor_200l': 1, 'tijolo': 8, 'cano_metal': 2, 'couro': 2}, ferramenta='martelo', fase=2, trabalha=1, ponto_uso=[0.0, 0.0, 0.7],
      estacao='forja (aço vira lâmina, ponta de lança, ferradura e pregos; precisa de carvão)', usa='carvao', luz_m=5, ruido_m=25)
def forja_tambor(M):
    p = M.base; R = 0.29
    _tambor(p, (0, 0, 0), R, 0.62, 'tambor_preto', tampa=False)
    torno(p, 'barro_forno', [(R - 0.005, 0.62), (R - 0.005, 0.5), (0.12, 0.42), (0.08, 0.5), (0.08, 0.62)], 36)  # revestimento de barro em funil
    fofo(p, 'carvao', 0.0, 0.53, 0.0, 0.16, 0.04, 0.16, 0.6, 0.6, (10, 16))
    fofo(p, 'brasa', 0.0, 0.565, 0.0, 0.08, 0.015, 0.08, 0.6, 0.6, (8, 12))
    for k in range(3):                                                                                           # 3 pes de vergalhao
        a = k * 2 * math.pi / 3; p.seg('ferrugem', (R * 0.8 * math.cos(a), 0.02, R * 0.8 * math.sin(a)), (R * 1.1 * math.cos(a), -0.0, R * 1.1 * math.sin(a)), 0.03, 0.03)
    anel(p, 'ferrugem', 0.02, 0.025, R - 0.01, R + 0.42, 14, 'x', (0, 0.42, 0))                                 # cano de ar ate o fole
    q = P()                                                                                                       # fole de couro em cavalete baixo
    q.cham('madeira_escura', -0.2, 0.2, 0.0, 0.025, -0.12, 0.12, 0.004)
    q.hull('couro_fole', [(x, y, z) for x in (-0.2, 0.18) for (y, z) in ((0.025, -0.12), (0.025, 0.12))] + [(0.18, 0.1, -0.1), (0.18, 0.1, 0.1), (-0.2, 0.03, 0.0)])
    q.cham('madeira_escura', -0.2, 0.2, 0.1, 0.12, -0.12, 0.12, 0.004); q.parts['madeira_escura'][-1].apply_transform(_rot(-0.22, [0, 0, 1], (-0.2, 0.11, 0)))
    q.cham('madeira_escura', 0.18, 0.4, 0.1, 0.12, -0.02, 0.02, 0.004); q.parts['madeira_escura'][-1].apply_transform(_rot(-0.22, [0, 0, 1], (-0.2, 0.11, 0)))
    for xx in (-0.15, 0.15): q.cham('madeira_crua', xx - 0.03, xx + 0.03, -0.38, 0.0, -0.1, 0.1, 0.004)
    p.merge(q, trimesh.transformations.translation_matrix([R + 0.6, 0.42, 0.0]) @ _rot(math.pi, [0, 1, 0]))
    # bigorna de trilho sobre toco, ao lado
    torno(p, 'madeira_lenha', [(0.17, 0.0), (0.17, 0.5)], 18, 'y', (-0.75, 0, 0.15)); torno(p, 'madeira_crua', [(0.16, 0.5), (0.16, 0.502)], 18, 'y', (-0.75, 0, 0.15))
    prof_z(p, 'trilho', -0.12, 0.12, [(-0.06, 0.0), (0.06, 0.0), (0.06, 0.012), (0.012, 0.02), (0.012, 0.07), (0.035, 0.078), (0.035, 0.11), (-0.035, 0.11), (-0.035, 0.078), (-0.012, 0.07), (-0.012, 0.02), (-0.06, 0.012)])
    p.parts['trilho'][-1].apply_transform(_rot(math.pi / 2, [0, 1, 0])); p.parts['trilho'][-1].apply_translation([-0.75, 0.502, 0.15])
    p.hull('trilho', [(-0.75 + 0.12, 0.58, 0.15 + dz) for dz in (-0.035, 0.035)] + [(-0.75 + 0.12, 0.612, 0.15 + dz) for dz in (-0.035, 0.035)] + [(-0.75 + 0.22, 0.605, 0.15)])  # chifre
    q = P(); cyl_eixo(q, 'madeira', 0.012, 0.0, 0.3, 'x', (0, 0, 0), 10); q.cham('aco', 0.28, 0.33, -0.022, 0.022, -0.016, 0.016, 0.004)   # martelo
    p.merge(q, trimesh.transformations.translation_matrix([-0.9, 0.625, 0.25]) @ _rot(0.4, [0, 1, 0]))
    q = P(); cyl_eixo(q, 'aco', 0.005, 0.0, 0.4, 'x', (0, 0, 0), 8); cyl_eixo(q, 'aco', 0.005, 0.0, 0.4, 'x', (0, 0.012, 0), 8)            # tenaz
    p.merge(q, trimesh.transformations.translation_matrix([-0.1, 0.64, 0.05]) @ _rot(-0.3, [0, 1, 0]))


@item('fogao_tambor', 'Fogão a lenha de tambor', 'mobilias', 'cozinha', comodos=['abrigo', 'casas', 'fazenda', 'casa_de_campo'],
      constroi={'tambor_200l': 1, 'cano_metal': 2, 'chapa_metal': 1, 'tijolo': 4}, ferramenta='martelo', fase=2, trabalha=1, ponto_uso=[0.0, 0.0, 0.65],
      estacao='cozinha (refeições que rendem 2× a comida crua e alegram os moradores; aquece o cômodo)', usa='lenha', luz_m=2, aquece=True)
def fogao_tambor(M):
    p = M.base; R = 0.29; L = 0.88; y = R + 0.22
    _tambor(p, (0, y, 0), R, L, 'tambor_preto', deitado=True)
    for s in (-1, 1): torno(p, 'tambor_preto', [(R - 0.003, 0.0), (R - 0.003, 0.003)], 40, 'x', (s * (L / 2 - 0.004), y, 0))
    for xs in (-1, 1):                                                                                           # pes de tijolo
        for k in range(2): p.cham('tijolo', xs * 0.3 - 0.095, xs * 0.3 + 0.095, k * 0.058, k * 0.058 + 0.057, -0.2, 0.2, 0.004)
        p.hull('ferrugem', [(xs * 0.3 + dx, 0.115, dz) for dx in (-0.08, 0.08) for dz in (-0.22, 0.22)] + [(xs * 0.3 + dx, y - R * 0.8, dz) for dx in (-0.05, 0.05) for dz in (-0.18, 0.18)])
    p.cham('ferrugem', -0.38, 0.38, y + R - 0.01, y + R + 0.006, -0.22, 0.22, 0.003)                             # chapa de cima (chapa de cozinhar)
    q = M.parte('porta_fornalha', (-L / 2 - 0.005, y - 0.1, 0.13), 'porta', eixo='y', abre_graus=-100)
    q.cham('tambor_preto', -L / 2 - 0.012, -L / 2 - 0.004, y - 0.1, y + 0.08, -0.13, 0.13, 0.003)
    varrer(q, 'aco_polido', circ(0.006, 8), [(-L / 2 - 0.012, y + 0.04, -0.1), (-L / 2 - 0.05, y + 0.04, -0.08), (-L / 2 - 0.05, y + 0.04, -0.04), (-L / 2 - 0.012, y + 0.04, -0.02)])
    p.cham('fuligem', -L / 2 - 0.006, -L / 2 - 0.002, y - 0.15, y - 0.14, -0.15, 0.15, 0.001)
    _chamine(p, L / 2 - 0.12, y + R - 0.01, 0.0, 1.5)
    q = P(); torno(q, 'aco_pintado', [(0.12, 0.0), (0.13, 0.12), (0.135, 0.12)], 28); torno(q, 'aco_pintado', [(0.125, 0.12), (0.06, 0.135), (0.0, 0.14)], 28)     # panela
    for xs in (-1, 1): q.cham('plastico_preto', xs * 0.13 - 0.03 * (xs > 0), xs * 0.13 + 0.03 * (xs < 0), 0.09, 0.105, -0.015, 0.015, 0.004)
    p.merge(q, trimesh.transformations.translation_matrix([-0.15, y + R + 0.006, 0.0]))
    q = P(); torno(q, 'lata', [(0.06, 0.0), (0.07, 0.16), (0.04, 0.2), (0.012, 0.22)], 24)                        # chaleira
    varrer(q, 'lata', circ(0.008, 8), [(0.06, 0.1, 0), (0.1, 0.16, 0), (0.13, 0.19, 0)])
    p.merge(q, trimesh.transformations.translation_matrix([0.15, y + R + 0.006, 0.08]))
    rng = np.random.default_rng(11)
    for i in range(5): p.seg('madeira_lenha', (-0.7 + rng.uniform(-0.05, 0.05), 0.04 + i * 0.045 * (i < 3), -0.1 + i * 0.05), (-0.7 + rng.uniform(-0.05, 0.05), 0.04 + i * 0.045 * (i < 3), 0.25 + i * 0.03), 0.06, 0.06)


@item('defumador', 'Defumador de tábuas', 'mobilias', 'cozinha', comodos=['abrigo', 'fazenda', 'casa_de_campo', 'casa_barcos'],
      constroi={'tabua': 8, 'chapa_metal': 1, 'caixa_pregos': 1, 'tijolo': 4}, ferramenta='martelo', fase=2, trabalha=1,
      estacao='defumador (carne e peixe duram 10 dias em vez de 2)', usa='lenha',
      produz={'item': 'carne_defumada', 'qtd': 4, 'a_cada_min': 240, 'consome': {'carne crua': 4, 'lenha': 1}})
def defumador(M):
    p = M.base; X, Z, H = 0.4, 0.35, 1.7
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_escura', xs * X - 0.045 * (xs > 0), xs * X + 0.045 * (xs < 0), 0.3, H, zs * Z - 0.045 * (zs > 0), zs * Z + 0.045 * (zs < 0), 0.004)
    for y in np.arange(0.3, H - 0.05, 0.14):                                                                    # costado de tabuas com frestas
        for xs in (-1, 1): p.cham('madeira_escura', xs * X - 0.02 * (xs > 0), xs * X + 0.02 * (xs < 0), y, y + 0.125, -Z, Z, 0.003)
        p.cham('madeira_escura', -X, X, y, y + 0.125, -Z - 0.02, -Z, 0.003)
    for x in (-0.25, 0.0, 0.25):                                                                                 # base de tijolos com boca de fogo
        for k in range(5):
            if x == 0.0 and k < 3: continue                                                       # boca de fogo
            p.cham('tijolo', x - 0.095, x + 0.095, k * 0.058, k * 0.058 + 0.057, -Z + 0.02, -Z + 0.11, 0.004)
        for k in range(5):
            if x == 0.0 and k < 3: continue                                                       # boca de fogo
            p.cham('tijolo', x - 0.095, x + 0.095, k * 0.058, k * 0.058 + 0.057, Z - 0.11, Z - 0.02, 0.004)
    p.hull('ferrugem', [(x, H, z) for x in (-X - 0.05, X + 0.05) for z in (-Z - 0.08, Z + 0.08)] + [(x, H + 0.12, z) for x in (-X - 0.05, X + 0.05) for z in (-0.05, 0.05)])
    p.hull('fuligem', [(x, H - 0.001, z) for x in (-X - 0.03, X + 0.03) for z in (-Z - 0.06, Z + 0.06)] + [(x, H + 0.1, z) for x in (-X - 0.03, X + 0.03) for z in (-0.04, 0.04)])
    p.parts['fuligem'].pop()
    for y in (1.35, 1.55):                                                                                       # varas com pecas penduradas
        cyl_eixo(p, 'madeira_crua', 0.012, -X, X, 'x', (0, y, 0), 10)
        for k, x in enumerate(np.linspace(-0.28, 0.28, 5)):
            varrer(p, 'corda', circ(0.002, 5), [(x, y, 0.0), (x, y - 0.06, 0.0)])
            if (k + int(y * 10)) % 2: fofo(p, 'carne_seca', x, y - 0.14, 0.0, 0.04, 0.08, 0.025, 0.6, 0.5, (10, 12))
            else: fofo(p, 'carne_seca', x, y - 0.12, 0.0, 0.025, 0.06, 0.045, 0.5, 0.5, (10, 12))
    q = M.parte('porta', (X, 0.3, Z + 0.005), 'porta', eixo='y', abre_graus=-110)
    for x in np.arange(-X, X - 0.01, 0.135): q.cham('madeira_escura', x, x + 0.13, 0.3, H - 0.02, Z, Z + 0.02, 0.003)
    for y in (0.5, H - 0.25): q.cham('madeira_escura', -X + 0.02, X - 0.02, y, y + 0.1, Z + 0.02, Z + 0.04, 0.003)
    q.cham('aco', -X + 0.03, -X + 0.06, 0.95, 1.05, Z + 0.04, Z + 0.06, 0.003)
    fofo(p, 'brasa', 0.0, 0.03, 0.0, 0.1, 0.02, 0.15, 0.6, 0.6, (8, 12))


@item('filtro_barril', 'Filtro de água em barril', 'mobilias', 'agua', comodos=['abrigo', 'fazenda', 'casas'],
      constroi={'tambor_200l': 1, 'carvao': 2, 'pedras': 4, 'trapos': 2, 'tubo_pvc': 1}, ferramenta='chave_inglesa', fase=2,
      estacao='filtro (água de chuva ou do rio fica limpa; ainda precisa ferver se alguém estiver doente)', conteiner=True, slots=1, saque=['agua'], grade=[2, 1],
      produz={'item': 'galao_agua', 'qtd': 1, 'a_cada_min': 60, 'consome': {'agua suja': 5}})
def filtro_barril(M):
    p = M.base; R = 0.29
    for xs in (-1, 1):                                                                                           # estrado de blocos
        for zs in (-1, 1):
            p.cham('cimento_saco', xs * 0.18 - 0.1, xs * 0.18 + 0.1, 0.0, 0.2, zs * 0.12 - 0.07, zs * 0.12 + 0.07, 0.006)
    _tambor(p, (0, 0.2, 0), R, 0.88, 'tambor_azul', tampa=False)
    torno(p, 'agua', [(R - 0.004, 0.2 + 0.82), (R - 0.004, 0.2 + 0.825)], 36)
    perfil = [(0.03, 1.02), (0.035, 1.08), (0.22, 1.24), (0.23, 1.26)]                                       # funil (galao cortado) encaixado na boca
    m = trimesh.creation.revolve(np.array([(r - 0.003, y) for r, y in perfil] + [(r, y) for r, y in perfil[::-1]], float), sections=32)
    if m.volume < 0: m.invert()
    m.apply_transform(_rot(-math.pi / 2, [1, 0, 0])); p.add('plastico_branco', m)
    for k in range(3):
        a = k * 2 * math.pi / 3; p.seg('madeira_crua', (0.0, 1.085, 0.0), (0.3 * math.cos(a), 1.085, 0.3 * math.sin(a)), 0.03, 0.02)  # apoio de sarrafos
    img = Image.new('RGB', (512, 768), (236, 230, 210)); d = ImageDraw.Draw(img)
    for i, (t, c) in enumerate((('PEDRA', (120, 118, 110)), ('AREIA', (196, 170, 120)), ('CARVÃO', (30, 30, 30)), ('PANO', (230, 220, 190)), ('CASCALHO', (120, 118, 110)))):
        d.rectangle([20, 20 + i * 140, 140, 140 + i * 140], fill=c); texto_c(d, (320, 80 + i * 140), t, 60, (40, 30, 26))
    mat_imagem('camadas_filtro', img, 0.85)
    p.box('camadas_filtro', -0.11, 0.11, 0.45, 0.78, R + 0.006, R + 0.008); p.uv['camadas_filtro'] = lambda v, n: np.stack([(v[:, 0] + 0.11) / 0.22, (v[:, 1] - 0.45) / 0.33], 1)
    _torcido(p, 'corda', [(-R - 0.008, 0.62, 0.0), (0.0, 0.62, -R - 0.008), (R + 0.008, 0.62, 0.0), (0.0, 0.62, R + 0.008), (-R - 0.008, 0.62, 0.0)], 0.004)
    cyl_eixo(p, 'latao_velho', 0.012, R - 0.01, R + 0.07, 'z', (0, 0.3, 0), 12)                                # torneira
    torno(p, 'latao_velho', [(0.012, 0.0), (0.008, -0.05)], 12, 'y', (0, 0.3, R + 0.06))
    p.cham('latao_velho', -0.02, 0.02, 0.31, 0.325, R + 0.04, R + 0.08, 0.004)
    q = P(); torno(q, 'galao_azul', [(0.1, 0.0), (0.11, 0.25), (0.05, 0.3)], 24)                              # galao embaixo da torneira
    p.merge(q, trimesh.transformations.translation_matrix([0.0, 0.0, R + 0.17]))


@item('bancada_eletronica', 'Bancada de eletrônica', 'mobilias', 'oficina', comodos=['abrigo', 'correios', 'cinema', 'delegacia'],
      constroi={'tabua': 4, 'fio_eletrico': 2, 'placa_circuito': 1, 'bateria_carro': 1}, ferramenta='chave_inglesa', fase=3, trabalha=1,
      ponto_uso=[0.0, 0.0, 0.6], sentar=True, usa='energia',
      estacao='eletrônica (rádio de longo alcance, holofote, alarme elétrico, carregador de pilhas; desbloqueia o marco da torre de rádio)')
def bancada_eletronica(M):
    p = M.base; X, Z, H = 0.75, 0.32, 0.78
    p.cham('madeira_escura', -X, X, H - 0.035, H, -Z, Z, 0.004)
    for xs in (-1, 1): carcaca(p, 'madeira_escura', xs * X - 0.36 * (xs > 0), xs * X + 0.36 * (xs < 0), 0.0, H - 0.035, -Z + 0.01, Z - 0.02, t=0.02, topo=False)
    p.cham('madeira_escura', -X, X, H, H + 0.42, -Z, -Z + 0.02, 0.004)                                         # painel de fundo
    for x in np.arange(-X + 0.05, X - 0.04, 0.06):
        for y in np.arange(H + 0.05, H + 0.4, 0.06): cyl_eixo(p, 'plastico_preto', 0.004, -Z + 0.0195, -Z + 0.0205, 'z', (x, y, 0), 6)
    q = P(); q.cham('aco_pintado', -0.17, 0.17, 0.0, 0.14, -0.12, 0.12, 0.006)                                  # radio aberto com valvulas
    q.cham('esmalte_escuro', -0.16, 0.16, 0.02, 0.12, 0.12, 0.125, 0.002)
    for k in range(2): torno(q, 'aco_polido', [(0.016, 0.0), (0.016, 0.012), (0.012, 0.018)], 16, 'z', (-0.08 + k * 0.16, 0.06, 0.125))
    q.box('vidro_escuro', -0.03, 0.05, 0.05, 0.1, 0.125, 0.127)
    p.merge(q, trimesh.transformations.translation_matrix([-0.35, H, -0.1]))
    for k in range(3): torno(p, 'vidro_prateleira', [(0.012, 0.0), (0.012, 0.04), (0.008, 0.055)], 12, 'y', (-0.42 + k * 0.05, H + 0.14, -0.15))
    q = P(); q.cham('esmalte_escuro', -0.1, 0.1, 0.0, 0.002, -0.07, 0.07, 0.001)
    p.merge(q, trimesh.transformations.translation_matrix([0.1, H, 0.1]))
    # bateria de carro, jacares e ferro de solda no suporte
    q = P(); q.cham('plastico_preto', -0.13, 0.13, 0.0, 0.18, -0.09, 0.09, 0.008); q.cham('plastico_cinza', -0.13, 0.13, 0.18, 0.2, -0.09, 0.09, 0.004)
    for xs, mat in ((-1, 'fio_vermelho'), (1, 'fio_azul')): torno(q, 'aco', [(0.012, 0.2), (0.01, 0.225)], 12, 'y', (xs * 0.08, 0, 0.04))
    p.merge(q, trimesh.transformations.translation_matrix([0.5, H, -0.12]))
    for k, mat in enumerate(('fio_vermelho', 'fio_azul')):
        varrer(p, mat, circ(0.003, 6), [(0.42 + k * 0.16, H + 0.225, -0.08), (0.4 + k * 0.1, H + 0.24, 0.0), (0.25 + k * 0.05, H + 0.01, 0.12)])
        p.cham(mat, 0.23 + k * 0.05, 0.26 + k * 0.05, H, H + 0.012, 0.11, 0.15, 0.003)
    varrer(p, 'aco', circ(0.002, 6), [(0.2, H + 0.002, -0.05), (0.16, H + 0.05, -0.03), (0.12, H + 0.05, 0.0), (0.12, H + 0.002, 0.03)])       # suporte em espiral (simples)
    q = P(); torno(q, 'plastico_vermelho', [(0.0, 0.0), (0.012, 0.0), (0.012, 0.12), (0.006, 0.13)], 14, 'x'); cyl_eixo(q, 'aco_polido', 0.002, 0.13, 0.2, 'x', (0, 0, 0), 8)
    p.merge(q, trimesh.transformations.translation_matrix([0.02, H + 0.04, -0.01]) @ _rot(0.3, [0, 1, 0]))
    torno(p, 'esmalte_branco', [(0.0, H + 0.42), (0.03, H + 0.42), (0.1, H + 0.36), (0.1, H + 0.35)], 20, 'y', (0.0, 0, -0.05))                # luminaria
    p.seg('aco_pintado', (0.0, H + 0.42, -0.05), (-0.05, H + 0.5, -Z + 0.02), 0.01, 0.01)


@item('bancada_municao', 'Mesa de recarga de munição', 'mobilias', 'oficina', comodos=['abrigo', 'delegacia', 'quartel', 'casa_de_campo'],
      constroi={'tabua': 5, 'caixa_pregos': 1, 'pote_parafusos': 1}, ferramenta='chave_inglesa', fase=3, trabalha=1, ponto_uso=[0.0, 0.0, 0.6],
      estacao='recarga (cápsulas vazias + pólvora + chumbo viram munição; 1 erro em 20 dá tiro falho)')
def bancada_municao(M):
    p = M.base; X, Z, H = 0.6, 0.3, 0.9
    p.cham('madeira', -X, X, H - 0.045, H, -Z, Z, 0.004)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira', xs * (X - 0.05) - 0.035, xs * (X - 0.05) + 0.035, 0.0, H - 0.045, zs * (Z - 0.05) - 0.035, zs * (Z - 0.05) + 0.035, 0.004)
    p.cham('madeira', -X + 0.05, X - 0.05, 0.2, 0.225, -Z + 0.05, Z - 0.05, 0.004)
    # prensa de recarga (estrutura em O, haste, alavanca)
    q = P(); q.cham('esmalte_escuro', -0.06, 0.06, 0.0, 0.02, -0.06, 0.06, 0.006)
    for zs in (-1, 1): q.cham('esmalte_escuro', -0.03, 0.03, 0.02, 0.28, zs * 0.045 - 0.015, zs * 0.045 + 0.015, 0.006)
    q.cham('esmalte_escuro', -0.04, 0.04, 0.24, 0.3, -0.06, 0.06, 0.008); cyl_eixo(q, 'aco_polido', 0.012, 0.06, 0.24, 'y', (0, 0, 0), 14)
    torno(q, 'latao_velho', [(0.012, 0.3), (0.012, 0.36), (0.014, 0.37)], 14)
    varrer(q, 'aco_polido', circ(0.007, 8), [(0.0, 0.12, 0.06), (0.0, 0.2, 0.18), (0.0, 0.32, 0.3)]); q.sphere('plastico_preto', 0.02, 0.0, 0.32, 0.3, sub=2)
    p.merge(q, trimesh.transformations.translation_matrix([-0.3, H, -0.08]))
    for k in range(3):                                                                                           # caixas de capsulas e potes
        _frasco(p, (0.05 + k * 0.08, H, -0.18), 0.03, 0.09, 'pet' if k else 'ambar', 'tinta_vermelha')
    q = P(); q.cham('plastico_cinza', -0.1, 0.1, 0.0, 0.025, -0.06, 0.06, 0.004)                                 # bandeja com cartuchos em pe
    for i in range(6):
        for j in range(4): torno(q, 'latao_velho', [(0.0045, 0.02), (0.0045, 0.05), (0.003, 0.058)], 10, 'y', (-0.075 + i * 0.03, 0, -0.045 + j * 0.03))
    p.merge(q, trimesh.transformations.translation_matrix([0.35, H, 0.05]))
    q = P(); q.cham('aco', -0.06, 0.06, 0.0, 0.03, -0.04, 0.04, 0.004); q.box('vidro_escuro', -0.04, 0.04, 0.03, 0.032, -0.025, 0.025)      # balanca de po
    p.merge(q, trimesh.transformations.translation_matrix([0.05, H, 0.12]))


@item('alambique', 'Alambique de panela', 'mobilias', 'oficina', comodos=['abrigo', 'fazenda', 'casa_de_campo'],
      constroi={'panela': 1, 'tubo_pvc': 1, 'cano_metal': 1, 'tambor_200l': 1, 'tijolo': 6}, ferramenta='chave_inglesa', fase=2, trabalha=1, usa='lenha',
      estacao='alambique (fruta podre ou grão viram álcool: remédio, lamparina, molotov e combustível do gerador)',
      produz={'item': 'alcool', 'qtd': 1, 'a_cada_min': 90, 'consome': {'comida': 3, 'lenha': 1}})
def alambique(M):
    p = M.base
    for k in range(4):                                                                                           # fornalha de tijolos
        for i, (x, z, sx, sz) in enumerate(((-0.2, 0, 0.045, 0.095), (0.2, 0, 0.045, 0.095), (0, -0.2, 0.095, 0.045))):
            p.cham('tijolo', x - sx, x + sx, k * 0.058, k * 0.058 + 0.057, z - sz, z + sz, 0.004)
    fofo(p, 'brasa', 0.0, 0.03, 0.0, 0.1, 0.02, 0.1, 0.6, 0.6, (8, 12))
    y0 = 0.232
    torno(p, 'cobre', [(0.16, y0), (0.2, y0 + 0.05), (0.2, y0 + 0.22), (0.16, y0 + 0.27), (0.05, y0 + 0.31), (0.04, y0 + 0.37)], 32)   # panela-caldeira
    anel(p, 'fuligem', 0.199, 0.2015, y0 + 0.04, y0 + 0.12, 32)
    torno(p, 'cobre', [(0.04, y0 + 0.37), (0.06, y0 + 0.4), (0.06, y0 + 0.44), (0.02, y0 + 0.47)], 24)                            # capacete
    for xs in (-1, 1): p.cham('cobre', xs * 0.2 - 0.03 * (xs > 0), xs * 0.2 + 0.03 * (xs < 0), y0 + 0.18, y0 + 0.2, -0.015, 0.015, 0.004)
    cam = [(0.02, y0 + 0.46, 0.0), (0.2, y0 + 0.5, 0.0), (0.55, y0 + 0.4, 0.0)]                                                  # alonga ate a serpentina
    varrer(p, 'cobre', circ(0.009, 10), cam)
    _tambor(p, (0.85, 0.0, 0.0), 0.29, 0.88, 'tambor_azul')                                                       # tambor de agua fria com serpentina
    torno(p, 'agua', [(0.284, 0.86), (0.284, 0.862)], 36, 'y', (0.85, 0, 0))
    t = np.linspace(0, 2 * math.pi * 4, 160); serp = np.stack([0.85 + 0.2 * np.cos(t), 0.82 - t / t[-1] * 0.6, 0.2 * np.sin(t)], 1)
    varrer(p, 'cobre', circ(0.008, 8), [(0.55, y0 + 0.4, 0.0), (0.65, 0.86, 0.0), (1.05, 0.86, 0.0)] + [tuple(x) for x in serp[1:]])
    varrer(p, 'cobre', circ(0.008, 8), [(1.05, 0.22, 0.0), (1.18, 0.22, 0.0), (1.2, 0.18, 0.0)])
    q = P(); torno(q, 'vidro_prateleira', [(0.04, 0.0), (0.045, 0.12), (0.015, 0.15), (0.012, 0.18)], 18); torno(q, 'agua', [(0.04, 0.003), (0.044, 0.06)], 18)
    p.merge(q, trimesh.transformations.translation_matrix([1.2, 0.0, 0.0]))


@item('composteira', 'Composteira de pallets', 'mobilias', 'agricultura', comodos=['abrigo', 'fazenda', 'casas'],
      constroi={'pallet': 3, 'arame_liso': 1}, ferramenta='nenhuma', fase=2,
      estacao='composteira (restos de comida viram adubo: canteiros dão 50 % mais)',
      produz={'item': 'adubo', 'qtd': 1, 'a_cada_min': 1440, 'consome': {'restos de comida': 4}})
def composteira(M):
    p = M.base; W = 1.2; rng = np.random.default_rng(7)
    def pallet_em_pe(q):
        for x in np.linspace(-0.55, 0.55, 5): q.cham('madeira_crua', x - 0.05, x + 0.05, 0.0, 0.8, 0.0, 0.022, 0.003)
        for y in (0.05, 0.4, 0.75): q.cham('madeira_crua', -0.6, 0.6, y - 0.05, y + 0.05, 0.022, 0.122, 0.003)
    for (T) in (trimesh.transformations.translation_matrix([0, 0, -0.6]),
                trimesh.transformations.translation_matrix([-0.6, 0, 0]) @ _rot(math.pi / 2, [0, 1, 0]),
                trimesh.transformations.translation_matrix([0.6, 0, 0]) @ _rot(-math.pi / 2, [0, 1, 0])):
        q = P(); pallet_em_pe(q); p.merge(q, T)
    for (x, z) in ((-0.6, -0.6), (0.6, -0.6)):
        for y in (0.2, 0.6): _rolo_fio(p, 'galvanizado', 0.05, 0.0, 0.02, 0.0012, voltas=3, camadas=1, c=(x, y, z))
    fofo(p, 'verde_compostagem', 0.0, 0.18, -0.06, 0.52, 0.22, 0.48, 0.5, 0.4, (12, 20)); _amassar(p, 'verde_compostagem', 0.02, 12.0, 3, sub=0)
    for i in range(14):                                                                                          # cascas e folhas por cima
        x, z = rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.3)
        fofo(p, 'erva' if i % 3 else 'tinta_amarela', x, 0.38 + rng.uniform(-0.02, 0.02), z, rng.uniform(0.02, 0.05), 0.006, rng.uniform(0.015, 0.03), 0.6, 0.6, (6, 8))
    q = P(); cyl_eixo(q, 'madeira', 0.014, 0.0, 1.1, 'y', (0, 0, 0), 10); q.cham('aco', -0.1, 0.1, -0.05, 0.0, -0.01, 0.01, 0.003)     # forcado encostado
    for x in (-0.08, -0.027, 0.027, 0.08): q.seg('aco', (x, -0.02, 0), (x, -0.25, 0.01), 0.008, 0.008)
    p.merge(q, trimesh.transformations.translation_matrix([0.45, 0.25, 0.35]) @ _rot(0.35, [0, 0, 1]) @ trimesh.transformations.translation_matrix([0, 0, 0]))


@item('cama_pallet', 'Cama de pallet com colchão', 'mobilias', 'abrigo', comodos=['abrigo', 'casas', 'galeria'], deitar=True, vagas=1,
      constroi={'pallet': 2, 'colchao_chao': 1}, ferramenta='nenhuma', fase=2,
      estacao='cama (morador com cama própria ganha +10 de moral; dorme fora do chão frio)')
def cama_pallet(M):
    p = M.base
    for z in (-0.6, 0.6):
        _base_pallet_q = P(); _base_pallet(_base_pallet_q, 0.5, 0.6)
        p.merge(_base_pallet_q, trimesh.transformations.translation_matrix([0, 0, z * 0.835]))
    fofo(p, 'colchao', 0.0, 0.144 + 0.09, 0.0, 0.46, 0.09, 0.96, 0.15, 0.12, (12, 28))
    fofo(p, 'lencol', 0.0, 0.144 + 0.18, 0.2, 0.47, 0.012, 0.7, 0.3, 0.2, (10, 24)); _amassar(p, 'lencol', 0.006, 20.0, 5, sub=0)
    fofo(p, 'cobertor', 0.05, 0.144 + 0.2, 0.35, 0.45, 0.03, 0.45, 0.25, 0.2, (10, 24)); _amassar(p, 'cobertor', 0.01, 18.0, 6, sub=0)
    fofo(p, 'travesseiro', 0.0, 0.144 + 0.22, -0.75, 0.3, 0.05, 0.16, 0.35, 0.3, (12, 16))
    q = P(); q.cham('madeira_crua', -0.2, 0.2, 0.0, 0.4, -0.15, 0.15, 0.004); q.box('madeira_crua', -0.18, 0.18, 0.2, 0.22, -0.15, 0.15)   # caixote-criado
    torno(q, 'esmalte_branco', [(0.02, 0.4), (0.02, 0.48)], 12); torno(q, 'chama', [(0.0, 0.48), (0.005, 0.49), (0.0, 0.51)], 8)
    p.merge(q, trimesh.transformations.translation_matrix([0.75, 0, -0.75]))


# ---------------------------------------------------------------------------- o que as estacoes produzem
@item('carne_defumada', 'Peça de carne defumada', 'loot', 'comida', recurso='comida', valor=3, peso_kg=0.6, empilha=4, celulas=[1, 1], fase=2,
      onde=['abrigo', 'fazenda'], efeito='fome -40; dura 10 dias sem estragar', obtem_de=[{'fazer': 'defumador', 'qtd': 4}])
def carne_defumada(M):
    p = M.base
    fofo(p, 'carne_seca', 0.0, 0.028, 0.0, 0.09, 0.028, 0.05, 0.5, 0.45, (12, 18)); _amassar(p, 'carne_seca', 0.003, 60.0, 2)
    fofo(p, 'esmalte_branco', 0.05, 0.03, 0.0, 0.03, 0.022, 0.04, 0.6, 0.5, (8, 10))                       # capa de gordura
    _torcido(p, 'corda', [(-0.03, 0.0, -0.05), (-0.03, 0.06, -0.02), (-0.03, 0.06, 0.02), (-0.03, 0.0, 0.05)], 0.0025)
    _torcido(p, 'corda', [(-0.03, 0.06, 0.0), (-0.05, 0.07, 0.0), (-0.09, 0.05, 0.0)], 0.0025)


@item('adubo', 'Saco de adubo de composto', 'loot', 'agricultura', recurso='material', valor=2, peso_kg=8.0, empilha=1, celulas=[2, 2], fase=2,
      onde=['abrigo', 'fazenda', 'supermercado'], efeito='canteiro adubado rende 50 % mais por 3 colheitas', obtem_de=[{'fazer': 'composteira', 'qtd': 1}])
def adubo(M):
    p = M.base
    fofo(p, 'rafia_verde', 0.0, 0.1, 0.0, 0.18, 0.1, 0.12, 0.3, 0.2, (14, 22)); _amassar(p, 'rafia_verde', 0.006, 30.0, 4)
    fofo(p, 'rafia_verde', 0.0, 0.215, 0.0, 0.1, 0.03, 0.06, 0.6, 0.5, (10, 14))                           # boca torcida
    _torcido(p, 'corda', [(-0.06, 0.205, -0.06), (0.0, 0.2, -0.065), (0.06, 0.205, -0.06), (0.065, 0.2, 0.0), (0.06, 0.205, 0.06), (-0.06, 0.205, 0.06)], 0.003)
    fofo(p, 'verde_compostagem', 0.2, 0.01, 0.06, 0.06, 0.012, 0.05, 0.6, 0.6, (8, 12))
