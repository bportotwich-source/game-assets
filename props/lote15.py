# Lote 15: itens feitos a mao (fase 1, Sozinho): o que o sobrevivente fabrica com os materiais do lote 13, sem bancada.
# Executado por gerar_props.py (usa as mesmas funcoes e materiais dos lotes anteriores).
# craft = {ingredientes {id: qtd}, estacao ('mao' = sem estacao, ou id de mobilia), ferramenta (id do loot), tempo_s}
# equipa = espaco do inventario do Recomeco onde o item e vestido (capacete, colete, colete_tatico, mochila); grade = inventario proprio
CORES.update({'revista_capa': (150, 40, 30), 'fita_crepe': (210, 190, 140), 'aco_escovado': (120, 122, 124), 'pavio': (226, 216, 190),
              'chama': (255, 150, 40), 'bambu': (176, 150, 80), 'acolchoado': (70, 66, 60), 'rafia_verde': (40, 70, 44)})
METALICOS.update({'aco_escovado': (0.85, 0.5)})
FOSCOS.update({'fita_crepe': 0.8, 'pavio': 0.95})
TEX_PROPRIAS += [('fita_crepe', 'papelao', 0.25, 1024), ('acolchoado', 'tecido', 0.25, 1024), ('rafia_verde', 'tecido', 0.5, 768),
                 ('bambu', 'couro', 0.5, 512)]
EMISSIVOS.update({'chama': [1.0, 0.55, 0.12]})


def _craft(ing, est='mao', fer=None, t=30):
    d = {'ingredientes': ing, 'estacao': est, 'tempo_s': t}
    if fer: d['ferramenta'] = fer
    return d


def _chama(p, c, h=0.08, r=0.022):
    """Labareda: dois lobulos alongados emissivos (parte que o jogo pode trocar por particulas)."""
    torno(p, 'chama', [(0.0, 0.0), (r, h * 0.2), (r * 0.8, h * 0.5), (r * 0.35, h * 0.85), (0.0, h)], 12, 'y', c)
    torno(p, 'chama', [(0.0, 0.0), (r * 0.6, h * 0.15), (r * 0.4, h * 0.6), (0.0, h * 1.25)], 10, 'y', (c[0] + r * 0.3, c[1], c[2]))


# ---------------------------------------------------------------------------- LUZ E FOGO
@item('tocha', 'Tocha de pano e álcool', 'loot', 'ferramentas', recurso='ferramenta', valor=1, peso_kg=0.5, empilha=3, celulas=[3, 1], fase=1,
      onde=['abrigo'], efeito='luz de 6 m por 10 min; afasta um zumbi encostado (fogo), mas a chama chama outros de longe',
      craft=_craft({'lenha': 1, 'trapos': 1, 'alcool': 1}, t=20), luz_m=6, dura_min=10, pega=[-0.2, 0.02, 0], arma=True, dano=12)
def tocha(M):
    p = M.base; L = 0.6; r = 0.018
    q = P()
    torno(q, 'madeira_lenha', [(r * 0.9, 0.0), (r, 0.02), (r * 1.1, L * 0.75), (r * 1.15, L)], 12)
    fofo(q, 'trapo_bege', 0.0, L * 0.88, 0.0, 0.036, 0.075, 0.036, 0.5, 0.6, (12, 16)); _amassar(q, 'trapo_bege', 0.004, 60.0, 3)
    fofo(q, 'carvao', 0.0, L * 0.93, 0.0, 0.03, 0.04, 0.03, 0.5, 0.6, (10, 12))
    for y in (L * 0.8, L * 0.95): anel(q, 'galvanizado', 0.036, 0.0385, y, y + 0.004, 16)
    p.merge(q, trimesh.transformations.translation_matrix([-L / 2, 0.04, 0]) @ _rot(-math.pi / 2, [0, 0, 1]))


@item('lamparina_lata', 'Lamparina de lata', 'loot', 'eletronicos', recurso='ferramenta', valor=1, peso_kg=0.25, empilha=2, celulas=[1, 1], fase=1,
      onde=['abrigo'], efeito='luz fraca de 3 m por 6 horas (gasta álcool); dá para deixar acesa no abrigo', usa='alcool',
      craft=_craft({'lata_vazia': 1, 'trapos': 1, 'alcool': 1}, fer='faca_cozinha', t=40), luz_m=3)
def lamparina_lata(M):
    p = M.base; R, H = 0.038, 0.075
    anel(p, 'lata', R - 0.0006, R, 0.004, H, 32)
    torno(p, 'lata', [(R - 0.003, 0.0), (R + 0.0008, 0.002), (R + 0.0008, 0.005), (0.0, 0.004)], 32)
    for y in np.linspace(0.015, H - 0.01, 5): anel(p, 'lata', R - 0.0004, R + 0.0007, y, y + 0.0025, 32)
    torno(p, 'lata', [(R, H - 0.001), (R, H), (0.008, H + 0.004), (0.006, H + 0.012), (0.0, H + 0.012)], 32)        # tampa furada (fundo de outra lata)
    anel(p, 'galvanizado', 0.0055, 0.0068, H, H + 0.016, 12)
    torno(p, 'pavio', [(0.0045, H + 0.004), (0.0045, H + 0.022), (0.003, H + 0.026)], 10)
    torno(p, 'carvao', [(0.0035, H + 0.024), (0.002, H + 0.03)], 10)
    _chama(p, (0.0, H + 0.026, 0.0), 0.028, 0.007)
    varrer(p, 'galvanizado', circ(0.0014, 6), [(-R - 0.001, H - 0.02, 0.0), (-R - 0.012, H + 0.04, 0.0), (0.0, H + 0.075, 0.0), (R + 0.012, H + 0.04, 0.0), (R + 0.001, H - 0.02, 0.0)])
    for xs in (-1, 1): anel(p, 'galvanizado', 0.0015, 0.003, -0.002, 0.002, 8, 'x', (xs * R, H - 0.02, 0))


@item('fogareiro_lata', 'Fogareiro de lata', 'loot', 'utensilios', recurso='ferramenta', valor=1, peso_kg=0.3, empilha=1, celulas=[1, 1], fase=1,
      onde=['abrigo'], efeito='cozinha e ferve água com gravetos ou carvão (fumaça baixa, chama escondida)', usa='lenha',
      craft=_craft({'lata_vazia': 2}, fer='faca_cozinha', t=60), estacao_portatil='fogão')
def fogareiro_lata(M):
    p = M.base; R, H = 0.055, 0.12
    anel(p, 'lata', R - 0.0008, R, 0.0, H, 40)
    for k in range(10):                                                                     # furos de ar em baixo e em cima (bordas recortadas)
        a = k * 2 * math.pi / 10
        for (y, rr) in ((0.016, 0.0065), (H - 0.016, 0.005)):
            c = np.array([math.cos(a), 0, math.sin(a)])
            torno(p, 'carvao', [(rr, 0.0), (rr, 0.0006)], 12, 'z', (0, 0, 0)); m = p.parts['carvao'][-1]
            m.apply_transform(trimesh.transformations.rotation_matrix(-a + math.pi / 2, [0, 1, 0])); m.apply_translation(c * (R - 0.0001) + [0, y, 0])
    anel(p, 'ferrugem', R - 0.0002, R + 0.0004, 0.03, 0.05, 40)
    anel(p, 'lata', 0.038, 0.0395, 0.03, H - 0.01, 32)                                        # lata interna (camara)
    torno(p, 'lata', [(0.0395, 0.03), (R - 0.001, 0.034), (R - 0.001, 0.036), (0.0395, 0.034)], 32)
    for k in range(3):                                                                       # 3 apoios dobrados para a panela
        a = k * 2 * math.pi / 3 + 0.4
        p.hull('lata', [(R * math.cos(a + d), H, R * math.sin(a + d)) for d in (-0.15, 0.15)] + [(R * 0.8 * math.cos(a + d), H + 0.018, R * 0.8 * math.sin(a + d)) for d in (-0.12, 0.12)])
    rng = np.random.default_rng(6)
    for i in range(6):                                                                       # gravetos e brasa
        a = rng.uniform(0, 6.3); c = np.array([0.012 * math.cos(a), 0.05 + i * 0.008, 0.012 * math.sin(a)])
        p.seg('madeira_lenha', c - [0.028, 0, 0.01], c + [0.028, 0.004, 0.01], 0.008, 0.008)
    fofo(p, 'brasa', 0.0, 0.045, 0.0, 0.03, 0.008, 0.03, 0.6, 0.6, (8, 12))


@item('kit_fogo', 'Kit de acender fogo', 'loot', 'ferramentas', recurso='ferramenta', valor=2, peso_kg=0.15, empilha=1, celulas=[1, 1], fase=1,
      onde=['abrigo', 'casa_de_campo', 'parque_trailers'], efeito='acende fogueira sem isqueiro (30 usos); funciona molhado',
      craft=_craft({'pedras': 1, 'sucata_metal': 1, 'trapos': 1, 'carvao': 1}, fer='pedra_amolar', t=90), usos=30)
def kit_fogo(M):
    p = M.base
    q = P(); q.cham('tinta_preta', -0.035, 0.035, 0.0, 0.03, -0.028, 0.028, 0.006)                          # latinha de pastilha com tampa
    for (a, b) in ((-0.035, 0.035),): q.cham('lata', a - 0.001, b + 0.001, 0.02, 0.032, -0.029, 0.029, 0.005)
    p.merge(q, trimesh.transformations.translation_matrix([-0.04, 0, 0.01]))
    fofo(p, 'pedra_escura', 0.03, 0.012, -0.02, 0.028, 0.012, 0.018, 0.6, 0.7, (10, 14))                  # pederneira
    q = P(); q.cham('aco_escovado', -0.035, 0.035, 0.0, 0.004, -0.01, 0.01, 0.001)                          # fuzil de aco (lima cortada) com cabo de corda
    _torcido(q, 'corda', [(-0.035, 0.002, -0.01), (-0.05, 0.002, -0.025), (-0.06, 0.002, 0.0), (-0.05, 0.002, 0.025), (-0.035, 0.002, 0.01)], 0.003)
    p.merge(q, trimesh.transformations.translation_matrix([0.04, 0.0, 0.035]) @ _rot(0.5, [0, 1, 0]))
    fofo(p, 'carvao', -0.01, 0.006, -0.05, 0.03, 0.006, 0.018, 0.5, 0.4, (8, 12))                          # pano carbonizado dobrado
    fofo(p, 'trapo_bege', -0.06, 0.008, -0.045, 0.02, 0.008, 0.02, 0.6, 0.6, (8, 10))                     # chumaco


# ---------------------------------------------------------------------------- AGUA, COMIDA E SAUDE
@item('filtro_garrafa', 'Filtro de água de garrafa', 'loot', 'agua', recurso='ferramenta', valor=2, peso_kg=0.6, empilha=1, celulas=[1, 2], fase=1,
      onde=['abrigo'], efeito='tira a sujeira da água de chuva ou do rio (ainda precisa ferver); 20 litros antes de trocar o carvão',
      craft=_craft({'garrafa_pet': 1, 'trapos': 1, 'carvao': 1, 'pedras': 1}, fer='faca_cozinha', t=120), usos=20)
def filtro_garrafa(M):
    """Garrafa cortada de cabeca para baixo, com camadas (pano, carvao, areia, pedrisco) e um pote embaixo pingando."""
    p = M.base; r = 0.054; H0 = 0.12
    perfil = [(0.017, 0.0), (0.03, 0.02), (r * 0.98, 0.07), (r, 0.09), (r, 0.24)]                     # gargalo para baixo
    q = P(); m = trimesh.creation.revolve(np.array([(a - 0.001, b) for a, b in perfil] + [(a, b) for a, b in perfil[::-1]], float), sections=28)
    if m.volume < 0: m.invert()
    m.apply_transform(_rot(-math.pi / 2, [1, 0, 0])); q.add('pet', m)
    torno(q, 'plastico_cinza', [(0.0155, -0.018), (0.0155, 0.004), (0.013, 0.006)], 20)                   # tampa furada
    for i, (y0, y1, mat, rr) in enumerate(((0.004, 0.04, 'trapo_bege', 0.025), (0.04, 0.1, 'carvao', r * 0.97), (0.1, 0.15, 'areia', r * 0.99), (0.15, 0.185, 'pedra_rio', r * 0.99))):
        torno(q, mat, [(min(rr, 0.017 + (y0 / 0.07) * 0.037), y0), (min(rr, 0.017 + (y1 / 0.07) * 0.037), y1)], 28)
    p.merge(q, trimesh.transformations.translation_matrix([0, H0, 0]))
    anel(p, 'pet', r * 0.92, r * 0.94, 0.0, H0 + 0.01, 28)                                               # pote de baixo (fundo da garrafa)
    torno(p, 'pet', [(r * 0.94, 0.0), (r * 0.94, 0.003)], 28)
    torno(p, 'agua', [(r * 0.9, 0.003), (r * 0.9, 0.055)], 28)
    torno(p, 'agua', [(0.0025, H0 - 0.03), (0.003, H0 - 0.022), (0.0, H0 - 0.014)], 8)                   # gota
    _torcido(p, 'corda', [(-r * 0.95, H0 + 0.02, 0.0), (0.0, H0 + 0.018, -r * 0.95), (r * 0.95, H0 + 0.02, 0.0), (0.0, H0 + 0.022, r * 0.95), (-r * 0.95, H0 + 0.02, 0.0)], 0.0025)


@item('caneca_lata', 'Caneca de lata com alça de arame', 'loot', 'utensilios', recurso='ferramenta', valor=1, peso_kg=0.1, empilha=2, celulas=[1, 1], fase=1,
      onde=['abrigo'], efeito='ferve 0,4 L de água na fogueira (água fervida não dá doença)',
      craft=_craft({'lata_vazia': 1, 'arame_liso': 1}, t=25))
def caneca_lata(M):
    p = M.base; R, H = 0.042, 0.12
    anel(p, 'lata', R - 0.0006, R, 0.004, H, 32)
    torno(p, 'lata', [(R - 0.003, 0.0), (R + 0.0008, 0.002), (R + 0.0008, 0.005), (0.0, 0.004)], 32)
    anel(p, 'lata', R - 0.0006, R + 0.0016, H - 0.003, H, 32)
    for y in np.linspace(0.02, H - 0.02, 8): anel(p, 'lata', R - 0.0004, R + 0.0007, y, y + 0.0025, 32)
    anel(p, 'carvao', R - 0.0003, R + 0.0004, 0.004, 0.035, 32)                                          # fuligem de fogo
    torno(p, 'agua', [(R - 0.002, 0.004), (R - 0.002, H * 0.7)], 28)
    varrer(p, 'galvanizado', circ(0.0016, 6), [(R + 0.0015, H - 0.012, -0.012), (R + 0.03, H - 0.03, -0.01), (R + 0.032, 0.03, 0.0), (R + 0.0015, 0.02, 0.012)])
    for y in (H - 0.012, 0.02): anel(p, 'galvanizado', R + 0.0008, R + 0.0024, y - 0.002, y + 0.002, 32)


@item('curativo_improvisado', 'Curativo de pano fervido', 'loot', 'remedios', recurso='remedios', valor=1, peso_kg=0.05, empilha=6, celulas=[1, 1], fase=1,
      onde=['abrigo'], efeito='para sangramento (cura 15); 20 % de chance de infeccionar se o pano não foi fervido',
      craft=_craft({'trapos': 2, 'alcool': 1}, est='fogueira', t=45))
def curativo_improvisado(M):
    p = M.base
    for k, (x, a) in enumerate(((-0.025, 0.1), (0.028, -0.2))):                                       # dois rolos de tira
        q = P(); anel(q, 'trapo_bege', 0.004, 0.019, -0.022, 0.022, 20, 'z', (0, 0.019, 0))
        for kk in range(4): anel(q, 'trapo_bege', 0.007 + kk * 0.003, 0.0075 + kk * 0.003, -0.0225, 0.0225, 20, 'z', (0, 0.019, 0))
        q.box('trapo_bege', -0.0005, 0.06, 0.0, 0.0012, -0.022, 0.022)
        p.merge(q, trimesh.transformations.translation_matrix([x, 0, 0]) @ _rot(a, [0, 1, 0]))
    torno(p, 'plastico_branco', [(0.012, 0.0), (0.012, 0.004)], 16, 'y', (0.0, 0, 0.045))              # alfinete de fralda
    varrer(p, 'aco_polido', circ(0.0008, 5), [(-0.02, 0.002, 0.05), (0.01, 0.002, 0.05), (0.02, 0.002, 0.046), (0.01, 0.002, 0.042), (-0.02, 0.002, 0.043)])


@item('tala_improvisada', 'Tala de tábua e pano', 'loot', 'remedios', recurso='remedios', valor=1, peso_kg=0.6, empilha=2, celulas=[2, 1], fase=1,
      onde=['abrigo'], efeito='trata perna ou braço quebrado: volta a correr em 1 dia em vez de 4',
      craft=_craft({'tabua': 1, 'trapos': 2}, fer='serrote', t=60))
def tala_improvisada(M):
    p = M.base; L = 0.42
    for z in (-0.035, 0.035):
        p.cham('madeira_crua', -L / 2, L / 2, 0.0, 0.012, z - 0.022, z + 0.022, 0.002)
    for x in (-0.14, 0.0, 0.14):                                                                       # tiras amarrando
        t = np.linspace(0, 2 * math.pi, 22)
        pts = np.stack([np.full_like(t, x) + 0.003 * np.sin(2 * t), 0.006 + 0.011 * np.sin(t), 0.062 * np.cos(t)], 1)
        varrer(p, 'trapo_xadrez', Polygon([(-0.012, -0.0012), (0.012, -0.0012), (0.012, 0.0012), (-0.012, 0.0012)]), pts)
        fofo(p, 'trapo_xadrez', x, 0.02, 0.0, 0.01, 0.006, 0.01, 0.5, 0.5, (8, 10))
    fofo(p, 'acolchoado', 0.0, 0.016, 0.0, L / 2 - 0.02, 0.005, 0.03, 0.3, 0.3, (10, 20))


# ---------------------------------------------------------------------------- CACA E PESCA
@item('armadilha_laco', 'Armadilha de laço', 'loot', 'agricultura', recurso='ferramenta', valor=1, peso_kg=0.4, empilha=3, celulas=[2, 1], fase=1,
      onde=['abrigo'], efeito='montada no mato pega coelho ou pombo (comida 2) em até 1 dia; zumbi pisa e fica preso 5 s',
      craft=_craft({'arame_liso': 1, 'tabua': 1}, fer='faca_cozinha', t=60), montar='chão (grama ou mato)')
def armadilha_laco(M):
    p = M.base
    p.cham('madeira_crua', -0.12, 0.12, 0.0, 0.02, -0.02, 0.02, 0.003)                                    # estaca deitada com ponta
    p.hull('madeira_crua', [(0.12, 0.0, -0.02), (0.12, 0.02, -0.02), (0.12, 0.0, 0.02), (0.12, 0.02, 0.02), (0.17, 0.01, 0.0)])
    p.cham('madeira_escura', -0.125, -0.115, 0.0, 0.022, -0.022, 0.022, 0.001)
    cyl_eixo(p, 'galvanizado', 0.0016, -0.1, -0.02, 'x', (0, 0.021, 0), 6)                              # arame enrolado na estaca
    for x in np.linspace(-0.1, -0.03, 10): anel(p, 'galvanizado', 0.0205, 0.023, x, x + 0.002, 12, 'x', (0, 0.01, 0))
    t = np.linspace(0, 2 * math.pi, 30)
    pts = np.stack([-0.05 + 0.0 * t - 0.09 + 0.07 * np.cos(t), 0.002 + 0.0 * t, 0.07 + 0.065 * np.sin(t)], 1)
    varrer(p, 'galvanizado', circ(0.0012, 6), [(-0.05, 0.02, 0.0), (-0.1, 0.005, 0.03)] + [tuple(x) for x in pts])
    torno(p, 'galvanizado', [(0.003, 0.0), (0.003, 0.006)], 10, 'y', (-0.07, 0, 0.005))                    # olhal do laco


@item('vara_pesca', 'Vara de pesca improvisada', 'loot', 'agricultura', recurso='ferramenta', valor=1, peso_kg=0.4, empilha=1, celulas=[5, 1], fase=1,
      onde=['abrigo', 'casa_barcos'], efeito='pesca no lago (comida 3 a cada 20 min, em silêncio)',
      craft=_craft({'lenha': 1, 'linha_pesca': 1}, fer='faca_cozinha', t=45), pega=[-0.55, 0.02, 0])
def vara_pesca(M):
    p = M.base; L = 1.6
    torno(p, 'bambu', [(0.014, 0.0), (0.012, L * 0.5), (0.006, L * 0.95), (0.004, L)], 12, 'x', (-L / 2, 0.015, 0))
    for x in np.linspace(-L / 2 + 0.2, L / 2 - 0.1, 6): anel(p, 'bambu', 0.006 + 0.008 * (1 - (x + L / 2) / L), 0.009 + 0.008 * (1 - (x + L / 2) / L), x, x + 0.01, 12, 'x', (0, 0.015, 0))
    q = P(); torno(q, 'madeira_crua', [(0.02, -0.012), (0.02, 0.012)], 16, 'z'); anel(q, 'linha_verde', 0.008, 0.018, -0.01, 0.01, 16, 'z')
    p.merge(q, trimesh.transformations.translation_matrix([-L / 2 + 0.25, 0.03, 0.02]))                    # carretel amarrado
    for x in (-L / 2 + 0.21, -L / 2 + 0.29): anel(p, 'fita_prata', 0.0135, 0.016, x, x + 0.025, 12, 'x', (0, 0.015, 0))
    varrer(p, 'linha_verde', circ(0.0005, 5), [(-L / 2 + 0.25, 0.05, 0.02), (L / 2 - 0.004, 0.02, 0.0), (L / 2 + 0.02, 0.0, 0.05), (L / 2 - 0.05, 0.002, 0.1)])
    torno(p, 'plastico_vermelho', [(0.0, 0.0), (0.008, 0.004), (0.006, 0.014), (0.0, 0.02)], 12, 'y', (L / 2 - 0.05, 0.0, 0.1))


# ---------------------------------------------------------------------------- REPARO E EQUIPAMENTO
@item('kit_reparo', 'Kit de reparo improvisado', 'loot', 'ferramentas', recurso='ferramenta', valor=3, peso_kg=0.8, empilha=1, celulas=[2, 1], fase=1,
      onde=['abrigo', 'garagem'], efeito='repara arma branca (+40 % de durabilidade) ou barricada (+60 de vida); 3 usos',
      craft=_craft({'fita_adesiva': 1, 'pote_parafusos': 1, 'arame_liso': 1, 'trapos': 1}, t=30), usos=3)
def kit_reparo(M):
    p = M.base; X, Z = 0.13, 0.07
    fofo(p, 'rafia_verde', 0.0, 0.03, 0.0, X, 0.03, Z, 0.3, 0.2, (12, 20)); _amassar(p, 'rafia_verde', 0.002, 50.0, 8)        # bolsinha de lona
    p.box('plastico_preto', -X + 0.01, X - 0.01, 0.058, 0.062, -0.002, 0.002)                                    # ziper
    p.cham('aco_polido', X - 0.03, X - 0.015, 0.056, 0.064, -0.008, 0.008, 0.001)
    anel(p, 'fita_prata', 0.024, 0.036, 0.0, 0.028, 28, 'y', (-X - 0.035, 0, 0.02))
    anel(p, 'papelao', 0.022, 0.024, 0.0005, 0.0275, 20, 'y', (-X - 0.035, 0, 0.02))
    _rolo_fio(p, 'galvanizado', 0.03, 0.0, 0.012, 0.001, voltas=5, camadas=2, c=(X + 0.04, 0, 0.02))
    _parafuso(p, (-0.03, 0.004, Z + 0.02), 0.04, 0.004); _porca(p, (0.03, 0.0, Z + 0.02))


@item('colete_revistas', 'Colete de revistas e fita', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=1.4, empilha=1, celulas=[3, 2], fase=1,
      onde=['abrigo'], efeito='+15 de proteção contra mordida no tronco e nos braços; desgasta a cada mordida', equipa='colete', protecao=15,
      craft=_craft({'livro': 2, 'fita_adesiva': 2, 'corda': 1}, t=90))
def colete_revistas(M):
    p = M.base; rng = np.random.default_rng(15)
    capas = [(150, 40, 30), (30, 70, 130), (200, 160, 30), (40, 110, 60)]
    for k, (x, z, w, d, a) in enumerate(((-0.12, 0.08, 0.2, 0.27, 0.05), (0.12, 0.08, 0.2, 0.27, -0.05), (-0.11, -0.2, 0.19, 0.2, 0.1), (0.11, -0.2, 0.19, 0.2, -0.08))):
        img = Image.new('RGB', (256, 340), capas[k]); dd = ImageDraw.Draw(img)
        texto_c(dd, (128, 40), ['VIDA & CASA', 'MOTOR', 'PESCA HOJE', 'JARDIM'][k], 30, (255, 255, 255), larg=230)
        dd.rectangle([30, 80, 226, 260], fill=tuple(min(255, c + 60) for c in capas[k])); mat_imagem(f'capa_rev_{k}', img, 0.5)
        q = P(); q.cham('papelao', -w / 2, w / 2, 0.0, 0.016, -d / 2, d / 2, 0.003)
        q.box(f'capa_rev_{k}', -w / 2 + 0.001, w / 2 - 0.001, 0.016, 0.0165, -d / 2 + 0.001, d / 2 - 0.001)
        q.uv[f'capa_rev_{k}'] = lambda v, n, w=w, d=d: np.stack([(v[:, 0] + w / 2) / w, (v[:, 2] + d / 2) / d], 1)
        T = trimesh.transformations.translation_matrix([x, 0.0, z]) @ _rot(a, [0, 1, 0])
        for kk, ms in q.parts.items():
            for mm in ms: mm.apply_transform(T)
            p.parts.setdefault(kk, []).extend(ms)
        f = q.uv.get(f'capa_rev_{k}')
        if f: p.uv[f'capa_rev_{k}'] = (lambda f, Ti: (lambda v, n: f(trimesh.transform_points(v, Ti), n)))(f, np.linalg.inv(T))
    for z in (0.12, 0.02, -0.15, -0.25):                                                                  # voltas de fita prata
        p.box('fita_prata', -0.24, 0.24, 0.016, 0.0175, z - 0.022, z + 0.022)
    for xs in (-1, 1):                                                                                     # alcas de corda
        _torcido(p, 'corda', [(xs * 0.08, 0.018, 0.21), (xs * 0.1, 0.04, 0.27), (xs * 0.14, 0.05, 0.3), (xs * 0.17, 0.03, 0.26), (xs * 0.17, 0.018, 0.2)], 0.005)


@item('colete_sucata', 'Colete de placas de sucata', 'loot', 'roupas', recurso='equipamento', valor=2, peso_kg=4.5, empilha=1, celulas=[3, 3], fase=2,
      onde=['abrigo', 'ferrovelho'], efeito='+35 de proteção; pesado (correr cansa 30 % mais rápido) e barulhento', equipa='colete', protecao=35,
      craft=_craft({'chapa_metal': 1, 'couro': 2, 'pote_parafusos': 1, 'corda': 1}, est='bancada_trabalho', fer='martelo', t=240))
def colete_sucata(M):
    p = M.base
    fofo(p, 'couro', 0.0, 0.01, 0.0, 0.25, 0.01, 0.32, 0.25, 0.15, (10, 24))                                # base de couro
    rng = np.random.default_rng(2)
    for i in range(3):                                                                                       # escamas de chapa (3 fileiras)
        for j in range(4):
            x = -0.16 + j * 0.105 + (0.05 if i % 2 else 0.0); z = 0.2 - i * 0.16
            if abs(x) > 0.22: continue
            q = P(); w, d = 0.1, 0.13
            xs_ = np.linspace(-w / 2, w / 2, 9); top = [(xx, 0.004 + 0.004 * math.cos(xx * 2 * math.pi / 0.076)) for xx in xs_]
            m = trimesh.creation.extrude_polygon(Polygon(top + [(xx, yy - 0.0015) for xx, yy in top[::-1]]).buffer(0), d)
            m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 1] + 0.02 + i * 0.003, m.vertices[:, 2] - d / 2], 1)
            if m.volume < 0: m.invert()
            q.add('ferrugem' if (i + j) % 3 else 'galvanizado', m)
            for (dx, dz) in ((-0.035, -0.05), (0.035, -0.05)): torno(q, 'aco', [(0.005, 0.0), (0.004, 0.003)], 6, 'y', (dx, 0.028 + i * 0.003, dz))
            p.merge(q, trimesh.transformations.translation_matrix([x, 0.0, z]) @ _rot(rng.uniform(-0.05, 0.05), [0, 1, 0]))
    for xs in (-1, 1):
        varrer(p, 'couro', Polygon([(-0.02, -0.002), (0.02, -0.002), (0.02, 0.002), (-0.02, 0.002)]), [(xs * 0.12, 0.02, 0.3), (xs * 0.14, 0.06, 0.36), (xs * 0.18, 0.06, 0.38), (xs * 0.2, 0.02, 0.32)])
        p.cham('aco', xs * 0.25 - 0.015, xs * 0.25 + 0.015, 0.0, 0.02, -0.05, -0.02, 0.003)                  # fivelas laterais


@item('capacete_panela', 'Capacete de panela acolchoado', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=1.0, empilha=1, celulas=[2, 2], fase=1,
      onde=['abrigo'], efeito='+20 de proteção na cabeça; tira 10 % da audição', equipa='capacete', protecao=20,
      craft=_craft({'panela': 1, 'trapos': 2, 'corda': 1}, fer='faca_cozinha', t=60))
def capacete_panela(M):
    p = M.base; R = 0.105; H = 0.12
    anel(p, 'aco_escovado', R - 0.0015, R, 0.0, H, 40, chanfro=0.0008)
    torno(p, 'aco_escovado', [(R, H - 0.0015), (R, H), (0.0, H)], 40)
    anel(p, 'aco_escovado', R, R + 0.004, 0.0, 0.006, 40, chanfro=0.001)                                    # borda enrolada
    for y in (0.04, 0.08): anel(p, 'carvao', R - 0.0002, R + 0.0004, y, y + 0.002, 40)                       # riscos de uso
    fofo(p, 'acolchoado', 0.0, H - 0.03, 0.0, R - 0.006, 0.026, R - 0.006, 0.3, 0.6, (12, 24))                # forro de pano dentro
    _amassar(p, 'acolchoado', 0.003, 70.0, 4)
    for xs in (-1, 1):                                                                                        # cabos viram presilhas da tira
        p.cham('plastico_preto', xs * R - 0.01, xs * R + 0.01, 0.03, 0.05, -0.012, 0.012, 0.003)
        p.parts['plastico_preto'][-1].apply_translation([xs * 0.012, 0, 0])
        _torcido(p, 'corda', [(xs * (R + 0.02), 0.04, 0.0), (xs * (R + 0.03), 0.006, 0.03), (xs * (R + 0.02), 0.005, 0.08), (0.0, 0.005, R + 0.04)], 0.004)
    for i, (x, z, a) in enumerate(((0.03, 0.05, 0.2), (-0.05, -0.02, -0.4))):
        p.hull('fita_prata', [(x - 0.03, H + 0.0003, z - 0.01), (x + 0.03, H + 0.0003, z - 0.01), (x - 0.03, H + 0.0012, z + 0.01), (x + 0.03, H + 0.0012, z + 0.01)])


@item('mochila_lona', 'Mochila de lona improvisada', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=0.8, empilha=1, celulas=[2, 3], fase=1,
      onde=['abrigo'], efeito='mochila de 4 × 4 células (a de loja tem 5 × 6); faz barulho de lona ao correr', equipa='mochila', grade=[4, 4],
      craft=_craft({'lona': 1, 'corda': 1, 'trapos': 1}, fer='kit_costura', t=180), pega=[0, 0.36, -0.06])
def mochila_lona(M):
    p = M.base
    fofo(p, 'lona_azul', 0.0, 0.2, 0.0, 0.16, 0.2, 0.09, 0.35, 0.3, (16, 24)); _amassar(p, 'lona_azul', 0.006, 30.0, 9)
    fofo(p, 'lona_azul', 0.0, 0.36, 0.0, 0.1, 0.06, 0.08, 0.6, 0.6, (12, 16)); _amassar(p, 'lona_azul', 0.006, 30.0, 10)     # boca franzida
    _torcido(p, 'corda', [(-0.1, 0.33, 0.07), (-0.04, 0.32, 0.09), (0.04, 0.32, 0.09), (0.1, 0.33, 0.07), (0.1, 0.34, -0.07), (-0.1, 0.33, -0.07), (-0.1, 0.33, 0.07)], 0.005)
    _torcido(p, 'corda', [(0.0, 0.33, 0.09), (0.02, 0.26, 0.1), (-0.01, 0.2, 0.1)], 0.005)                              # ponta do no
    for xs in (-1, 1):                                                                                                  # alcas de corda acolchoadas com pano
        cam = [(xs * 0.06, 0.34, -0.085), (xs * 0.08, 0.36, -0.13), (xs * 0.1, 0.25, -0.15), (xs * 0.12, 0.08, -0.12), (xs * 0.13, 0.02, -0.08)]
        _torcido(p, 'corda', cam, 0.006)
        varrer(p, 'trapo_xadrez', circ(0.014, 10), [(xs * 0.085, 0.33, -0.14), (xs * 0.1, 0.25, -0.15), (xs * 0.115, 0.14, -0.135)])
    fofo(p, 'trapo_cinza', 0.0, 0.12, 0.085, 0.09, 0.07, 0.025, 0.4, 0.3, (10, 14))                                    # bolso costurado
    for x in np.linspace(-0.08, 0.08, 9): p.box('linha_verde', x - 0.004, x + 0.004, 0.19, 0.192, 0.1, 0.106)       # pesponto


@item('bolsa_cintura', 'Bolsa de cintura de pano', 'loot', 'roupas', recurso='equipamento', valor=1, peso_kg=0.3, empilha=1, celulas=[2, 1], fase=1,
      onde=['abrigo'], efeito='+3 × 2 células de acesso rápido (usar sem abrir a mochila)', equipa='colete_tatico', grade=[3, 2],
      craft=_craft({'trapos': 3, 'linha_pesca': 1, 'corda': 1}, fer='kit_costura', t=120))
def bolsa_cintura(M):
    p = M.base
    fofo(p, 'trapo_xadrez', 0.0, 0.05, 0.0, 0.11, 0.05, 0.04, 0.35, 0.25, (12, 20)); _amassar(p, 'trapo_xadrez', 0.003, 50.0, 12)
    p.hull('trapo_xadrez', [(x, 0.1, z) for x in (-0.11, 0.11) for z in (-0.035, 0.035)] + [(x, 0.06, 0.045) for x in (-0.1, 0.1)])  # aba
    torno(p, 'madeira_escura', [(0.008, 0.0), (0.008, 0.004)], 12, 'z', (0.0, 0.065, 0.045))                                         # botao
    _torcido(p, 'corda', [(-0.11, 0.07, -0.03), (-0.2, 0.04, -0.06), (-0.3, 0.01, -0.02), (-0.34, 0.006, 0.04)], 0.005)
    _torcido(p, 'corda', [(0.11, 0.07, -0.03), (0.2, 0.04, -0.06), (0.28, 0.01, -0.03), (0.33, 0.006, 0.02)], 0.005)
