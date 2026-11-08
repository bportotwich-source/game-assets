# Lote 10: itens unicos de comida e comercio (diner, lanchonete, padaria, posto, supermercado, cinema, hotel, motel, estacao, rodoviaria).
# Executado por gerar_props.py (mesmas funcoes e materiais).
CORES.update({'vinil_vermelho': (110, 8, 10), 'vinil_creme': (220, 206, 170), 'formica': (200, 210, 206), 'jukebox_luz': (255, 170, 60),
              'massa': (230, 214, 170), 'pao': (170, 100, 40), 'oleo_amarelo': (200, 150, 10), 'poltrona_cinema': (90, 10, 16),
              'pipoca': (250, 236, 190), 'ouro_hotel': (190, 150, 60), 'verde_estacao': (24, 60, 40), 'azul_vending': (10, 40, 110)})
METALICOS.update({'ouro_hotel': (0.9, 0.3), 'verde_estacao': (0.3, 0.5), 'azul_vending': (0.3, 0.45)})
FOSCOS.update({'vinil_vermelho': 0.35, 'vinil_creme': 0.35, 'formica': 0.3, 'massa': 0.8, 'pao': 0.75, 'pipoca': 0.9})
TEX_PROPRIAS += [('poltrona_cinema', 'tecido', 0.25, 1024)]
EMISSIVOS.update({'jukebox_luz': [1.0, 0.55, 0.15]})


# ---------------------------------------------------------------------------- DINER / LANCHONETE
@item('banqueta_giratoria', 'Banqueta giratória de balcão', 'mobilias', 'diner', comodos=['diner', 'lanchonete', 'cinema_drive_in', 'padaria'], sentar=True, colisao='caixa')
def banqueta_giratoria(M):
    p = M.base
    torno(p, 'inox', [(0.2, 0.0), (0.2, 0.015), (0.06, 0.03), (0.04, 0.05)], 32); p.cyl('inox', 0.035, 0.05, 0.68, sec=20)
    anel(p, 'inox', 0.16, 0.175, 0.3, 0.32, 32); [p.seg('inox', (0.03 * math.cos(a), 0.31, 0.03 * math.sin(a)), (0.165 * math.cos(a), 0.31, 0.165 * math.sin(a)), 0.012) for a in (0, 2.1, 4.2)]
    torno(p, 'inox', [(0.19, 0.68), (0.2, 0.7), (0.2, 0.72)], 32, fechar=False)
    torno(p, 'vinil_vermelho', [(0.0, 0.7), (0.19, 0.7), (0.2, 0.73), (0.19, 0.77), (0.15, 0.785), (0.0, 0.79)], 32)
    for k in range(8): a = k / 8 * 2 * math.pi; p.sphere('inox', 0.005, 0.2 * math.cos(a), 0.71, 0.2 * math.sin(a), 0)


@item('mesa_booth', 'Mesa de booth com dois sofás', 'mobilias', 'diner', comodos=['diner', 'lanchonete'], sentar=True, vagas=4, colisao='caixa', modulo_m=2.0)
def mesa_booth(M):
    p = M.base; X = 0.6
    torno(p, 'inox', [(0.22, 0.0), (0.22, 0.02), (0.05, 0.04), (0.04, 0.72)], 24)
    p.cham('formica', -X, X, 0.72, 0.75, -0.35, 0.35, 0.008); anel(p, 'inox', 0.0, 0.0001, 0.72, 0.7201, 4) if False else None
    for zs in (-1, 1): p.box('inox', -X, X, 0.72, 0.75, *sorted((zs * 0.35, zs * 0.355)))
    for xs in (-1, 1): p.box('inox', *sorted((xs * X, xs * (X + 0.005))), 0.72, 0.75, -0.355, 0.355)
    for zs in (-1, 1):
        z0 = zs * 0.45; z1 = zs * 0.95
        p.cham('vinil_vermelho', -X - 0.05, X + 0.05, 0.0, 0.45, *sorted((z0, z1)), 0.01)
        p.cham('vinil_creme', -X - 0.03, X + 0.03, 0.45, 0.52, *sorted((z0 + zs * 0.02, z1 - zs * 0.12)), 0.03)
        p.cham('vinil_vermelho', -X - 0.05, X + 0.05, 0.45, 1.15, *sorted((z1 - zs * 0.12, z1)), 0.02)
        for x in np.linspace(-X + 0.05, X - 0.05, 6): p.cham('vinil_creme', x - 0.09, x + 0.09, 0.55, 1.08, *sorted((z1 - zs * 0.135, z1 - zs * 0.12)), 0.03)
        p.box('inox', -X - 0.05, X + 0.05, 1.15, 1.17, *sorted((z1 - zs * 0.12, z1)))
    for x, mat in ((-0.15, 'vidro_prateleira'), (0.0, 'aco_polido'), (0.12, 'tinta_vermelha')): p.cyl(mat, 0.025, 0.75, 0.86, x=x, z=0.0, sec=14)
    p.cham('papel', 0.3, 0.5, 0.75, 0.752, -0.15, 0.15, 0.001)


@item('jukebox', 'Jukebox', 'mobilias', 'diner', comodos=['diner', 'lanchonete', 'motel', 'galeria'], colisao='caixa', usa='energia', luz_m=3,
      interacao='toca música: moral +10 na base, mas atrai zumbis num raio grande', barulho='muito alto')
def jukebox(M):
    p = M.base; X, Z = 0.42, 0.3
    perfil = Polygon([(-X, 0.0), (X, 0.0), (X, 1.15)] + [(X * math.cos(a), 1.15 + 0.42 * math.sin(a)) for a in np.linspace(0, math.pi, 24)] + [(-X, 1.15)])
    e = trimesh.creation.extrude_polygon(perfil, 2 * Z); e.apply_translation([0, 0, -Z]); p.add('madeira_escura', e)
    arco = Polygon([(X * 0.86 * math.cos(a), 1.15 + 0.36 * math.sin(a)) for a in np.linspace(0, math.pi, 24)] + [(-X * 0.86, 1.0), (X * 0.86, 1.0)]).buffer(0)
    for r_, mat, dz in ((1.0, 'jukebox_luz', 0.0), (0.86, 'cromo', 0.004), (0.74, 'jukebox_luz', 0.008)):
        a_ = affinity.scale(arco, r_, r_, origin=(0, 1.15)); a_ = a_.difference(affinity.scale(arco, r_ - 0.08, r_ - 0.08, origin=(0, 1.15))) if r_ < 1 else a_.difference(affinity.scale(arco, 0.92, 0.92, origin=(0, 1.15)))
        m = trimesh.creation.extrude_polygon(a_.buffer(0), 0.02); m.apply_translation([0, 0, Z + dz]); p.add(mat, m)
    p.cham('vidro_prateleira', -0.3, 0.3, 0.9, 1.3, Z - 0.05, Z + 0.01, 0.01)
    for k in range(12): torno(p, 'disco', [(0.11, 0.0), (0.11, 0.004)], 24, 'y', (0, 0.95 + k * 0.02, Z - 0.15))
    p.cham('cromo', -0.32, 0.32, 0.7, 0.88, Z, Z + 0.04, 0.01)
    for i in range(4):
        for j in range(5): p.cham('plastico_branco', -0.28 + j * 0.115, -0.2 + j * 0.115, 0.74 + i * 0.035, 0.765 + i * 0.035, Z + 0.04, Z + 0.045, 0.002)
    p.cham('tecido_cadeira', -0.3, 0.3, 0.15, 0.6, Z - 0.002, Z + 0.004, 0.006)
    for x in np.linspace(-0.27, 0.27, 9): p.box('cromo', x - 0.008, x + 0.008, 0.15, 0.6, Z + 0.004, Z + 0.012)
    for xs in (-1, 1): p.cham('cromo', xs * X - 0.03, xs * X + 0.03, 0.0, 1.15, -Z + 0.05, Z - 0.05, 0.01)


@item('chapa_lanchonete', 'Chapa de lanchonete', 'mobilias', 'diner', comodos=['diner', 'lanchonete', 'cinema_drive_in'], colisao='caixa', usa='combustivel',
      estacao='cozinha (cozinha 4 refeições de uma vez)')
def chapa_lanchonete(M):
    p = M.base; X, Z = 0.6, 0.35
    p.cham('inox', -X, X, 0.0, 0.85, -Z, Z, 0.008)
    for x in (-0.3, 0.3): almofadada(p, 'inox', x - 0.28, x + 0.28, 0.1, 0.75, Z, Z + 0.012, borda=0.03); puxador_barra(p, 'inox', 0.65, x - 0.15, x + 0.15, Z + 0.012, eixo='x')
    p.cham('esmalte_escuro', -X + 0.02, X - 0.02, 0.85, 0.9, -Z + 0.1, Z - 0.02, 0.004)
    p.cham('inox', -X, X, 0.85, 1.0, -Z, -Z + 0.1, 0.005); p.cham('inox', -X, -X + 0.02, 0.85, 0.95, -Z, Z, 0.004); p.cham('inox', X - 0.02, X, 0.85, 0.95, -Z, Z, 0.004)
    p.box('inox', -X + 0.03, X - 0.03, 0.86, 0.87, Z - 0.015, Z + 0.06)
    for k in range(6): torno(p, 'plastico_preto', [(0.02, 0.0), (0.02, 0.02), (0.0, 0.024)], 14, 'z', (-0.45 + k * 0.18, 0.8, Z + 0.012))
    for x in (-0.2, 0.15): p.cham('esmalte_escuro', x, x + 0.14, 0.9, 0.905, -0.1, 0.05, 0.005)
    p.cham('inox', 0.3, 0.42, 0.9, 0.903, 0.05, 0.12, 0.001); p.seg('madeira_escura', (0.36, 0.905, 0.12), (0.36, 0.91, 0.3), 0.02, 0.015)


@item('vitrine_tortas', 'Vitrine giratória de tortas', 'mobilias', 'diner', comodos=['diner', 'padaria', 'lanchonete'], conteiner=True, slots=2, saque=['comida'], colisao='caixa')
def vitrine_tortas(M):
    p = M.base
    torno(p, 'inox', [(0.22, 0.0), (0.22, 0.04), (0.2, 0.05)], 32)
    anel(p, 'vidro_prateleira', 0.2, 0.205, 0.05, 0.75, 40); torno(p, 'inox', [(0.21, 0.75), (0.2, 0.8), (0.04, 0.84), (0.03, 0.88)], 32)
    p.cyl('inox', 0.008, 0.05, 0.75, sec=10)
    for k, y in enumerate((0.08, 0.32, 0.56)):
        torno(p, 'vidro_prateleira', [(0.0, y), (0.19, y), (0.19, y + 0.006), (0.0, y + 0.006)], 32)
        for j in range(2 - (k == 2)):
            a = j * math.pi + k
            torno(p, 'pao', [(0.0, y + 0.006), (0.09, y + 0.006), (0.095, y + 0.03), (0.08, y + 0.05), (0.0, y + 0.055)], 24, 'y', (0.09 * math.cos(a), 0, 0.09 * math.sin(a)))
            torno(p, 'tinta_vermelha' if k % 2 else 'massa', [(0.0, y + 0.053), (0.075, y + 0.05), (0.0, y + 0.058)], 24, 'y', (0.09 * math.cos(a), 0, 0.09 * math.sin(a)))


@item('maquina_refrigerante', 'Máquina de refrigerante de balcão', 'mobilias', 'diner', comodos=['diner', 'lanchonete', 'cinema', 'posto'], colisao='caixa',
      coleta={'recurso': 'agua', 'total': 2, 'ferramenta': 'nenhuma', 'segundos_por_unidade': 5}, observacao='xarope adoçado: sede -20 e ânimo +5')
def maquina_refrigerante(M):
    p = M.base; X, Z = 0.35, 0.3
    p.cham('inox', -X, X, 0.0, 0.7, -Z, Z, 0.012)
    p.cham('tinta_vermelha', -X + 0.02, X - 0.02, 0.4, 0.68, Z - 0.01, Z + 0.005, 0.01)
    for k in range(4):
        x = -0.24 + k * 0.16; p.cham('plastico_branco', x - 0.05, x + 0.05, 0.43, 0.65, Z + 0.005, Z + 0.01, 0.006)
        p.cham('inox', x - 0.025, x + 0.025, 0.35, 0.4, Z - 0.03, Z + 0.04, 0.006); p.cyl('inox', 0.008, 0.31, 0.35, x=x, z=Z + 0.02, sec=8)
    p.cham('inox', -X + 0.02, X - 0.02, 0.0, 0.03, Z - 0.05, Z + 0.15, 0.004)
    for x in np.linspace(-0.3, 0.3, 14): p.box('esmalte_escuro', x - 0.008, x + 0.008, 0.03, 0.032, Z - 0.03, Z + 0.13)


@item('fritadeira', 'Fritadeira industrial', 'mobilias', 'diner', comodos=['diner', 'lanchonete', 'cinema_drive_in'], colisao='caixa',
      coleta={'recurso': 'combustivel', 'total': 1, 'ferramenta': 'galão', 'segundos_por_unidade': 20}, observacao='óleo velho vira combustível de lampião')
def fritadeira(M):
    p = M.base; X, Z = 0.25, 0.35
    p.cham('inox', -X, X, 0.0, 0.88, -Z, Z, 0.008)
    p.box('esmalte_escuro', -X + 0.03, X - 0.03, 0.82, 0.88, -Z + 0.05, Z - 0.08); p.box('oleo_amarelo', -X + 0.035, X - 0.035, 0.8, 0.84, -Z + 0.055, Z - 0.085)
    for xs in (-1, 1):
        x = xs * 0.1
        carcaca(p, 'aco_polido', x - 0.08, x + 0.08, 0.84, 0.96, -0.22, 0.14, t=0.004, topo=False)
        p.seg('plastico_preto', (x, 0.92, 0.14), (x, 0.98, 0.42), 0.025)
    p.cham('inox', -X, X, 0.88, 1.05, -Z, -Z + 0.06, 0.005)
    for k in range(2): torno(p, 'plastico_preto', [(0.022, 0.0), (0.022, 0.02), (0.0, 0.024)], 14, 'z', (-0.1 + k * 0.2, 0.7, Z))


# ---------------------------------------------------------------------------- PADARIA
@item('masseira', 'Masseira de padaria', 'mobilias', 'padaria', comodos=['padaria', 'diner'], colisao='caixa', usa='energia',
      estacao='padaria da base (farinha + água + lenha = 20 pães)')
def masseira(M):
    p = M.base; m = 'esmalte'
    p.cham(m, -0.35, 0.35, 0.0, 0.55, -0.3, 0.3, 0.02)
    anel(p, 'inox', 0.3, 0.315, 0.55, 0.85, 40, 'y', (0, 0, 0.05)); torno(p, 'inox', [(0.0, 0.56), (0.3, 0.56)], 40, 'y', (0, 0, 0.05))
    fofo(p, 'massa', 0.0, 0.65, 0.05, 0.25, 0.09, 0.25, 0.7, 0.7, (14, 20))
    p.cham(m, -0.12, 0.12, 0.55, 1.25, -0.42, -0.28, 0.02); p.cham(m, -0.12, 0.12, 1.05, 1.25, -0.42, 0.12, 0.03)
    varrer(p, 'aco_polido', circ(0.015, 10), [(0.0, 1.05, 0.05), (0.0, 0.8, 0.05), (0.06, 0.68, 0.08), (0.0, 0.62, 0.12)])
    for k in range(2): torno(p, 'plastico_preto' if k else 'tinta_verde', [(0.015, 0.0), (0.015, 0.012)], 12, 'x', (0.12, 1.15 - k * 0.04, -0.3))


@item('carrinho_assadeiras', 'Carrinho de assadeiras', 'mobilias', 'padaria', comodos=['padaria', 'diner', 'supermercado'], conteiner=True, slots=4, saque=['comida'],
      portatil=True, peso_kg=25.0, colisao='caixa')
def carrinho_assadeiras(M):
    p = M.base; X, Z = 0.24, 0.34; rng = np.random.default_rng(47)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('inox', xs * X - 0.012, xs * X + 0.012, 0.08, 1.7, zs * Z - 0.012, zs * Z + 0.012, 0.003); _roda(p, (xs * X, 0.05, zs * Z), 0.05, 0.025, mat_aro='aco')
        for k in range(12): p.box('inox', xs * X - 0.01 * xs - 0.004, xs * X - 0.01 * xs + 0.004, 0.2 + k * 0.12, 0.208 + k * 0.12, -Z, Z)
    for y in (0.08, 1.7):
        for zs in (-1, 1): p.box('inox', -X, X, y, y + 0.02, zs * Z - 0.01, zs * Z + 0.01)
    for k in range(12):
        if rng.random() < 0.35: continue
        y = 0.21 + k * 0.12; p.box('aco', -X + 0.015, X - 0.015, y, y + 0.012, -Z + 0.01, Z - 0.01)
        for i in range(3):
            for j in range(4):
                if rng.random() < 0.3: continue
                fofo(p, 'pao', -0.13 + i * 0.13, y + 0.04, -0.25 + j * 0.17, 0.05, 0.03, 0.07, 0.6, 0.6, (8, 10))


@item('pao_velho', 'Saco de pão francês', 'loot', 'comida', recurso='comida', valor=1, peso_kg=0.4, empilha=4, onde=['padaria', 'supermercado', 'diner', 'casas'],
      efeito='fome -15; endurece em 3 dias (ainda comível na sopa)')
def pao_velho(M):
    p = M.base
    fofo(p, 'papel', 0, 0.06, 0, 0.12, 0.06, 0.18, 0.4, 0.3, (12, 18))
    for k, (x, z) in enumerate(((-0.05, 0.16), (0.05, 0.2))):
        fofo(p, 'pao', x, 0.06, z + 0.03, 0.04, 0.035, 0.08, 0.6, 0.6, (10, 12))
        for j in range(3): p.box('massa', x - 0.02, x + 0.02, 0.093, 0.096, z + 0.02 * j, z + 0.02 * j + 0.006)


# ---------------------------------------------------------------------------- POSTO
@item('expositor_oleo', 'Expositor de óleo de motor', 'mobilias', 'posto', comodos=['posto', 'garagem', 'concessionaria'], conteiner=True, slots=3,
      saque=['combustivel', 'materiais'], colisao='caixa')
def expositor_oleo(M):
    p = M.base; X, Z = 0.45, 0.22
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('aco_pintado', xs * X - 0.015, xs * X + 0.015, 0.0, 1.5, zs * Z - 0.015, zs * Z + 0.015, 0.003)
    for k, y in enumerate((0.1, 0.55, 1.0)):
        p.box('aco_pintado', -X, X, y, y + 0.02, -Z, Z)
        for i in range(7):
            for j in range(2):
                x = -0.38 + i * 0.125; z = -0.1 + j * 0.2
                t = P(); t.cham('oleo_amarelo' if (i + k) % 3 else 'tinta_azul', -0.05, 0.05, 0, 0.25, -0.035, 0.035, 0.012)
                torno(t, 'plastico_preto', [(0.016, 0.25), (0.016, 0.28)], 12, 'y', (0.025, 0, 0))
                t.box('papel', -0.04, 0.04, 0.05, 0.18, 0.035, 0.037)
                p.merge(t, trimesh.transformations.translation_matrix([x, y + 0.02, z]))


@item('freezer_sorvete', 'Freezer de sorvete com tampa de vidro', 'mobilias', 'posto', comodos=['posto', 'supermercado', 'diner', 'galeria'], conteiner=True, slots=3,
      saque=['comida'], colisao='caixa', barricada=True, observacao='sorvete derretido: só o picolé de água (sede -10)')
def freezer_sorvete(M):
    p = M.base; X, Z, H = 0.6, 0.33, 0.85
    p.cham('esmalte', -X, X, 0.06, H, -Z, Z, 0.02); p.cham('plastico_preto', -X + 0.02, X - 0.02, 0.0, 0.06, -Z + 0.02, Z - 0.02, 0.006)
    img = Image.new('RGB', (1024, 256), (250, 250, 250)); d = ImageDraw.Draw(img); d.rectangle([0, 0, 1024, 70], fill=(30, 110, 200))
    texto_c(d, (512, 36), 'GELADINHO', 50, (255, 255, 255))
    for k in range(6): x = 90 + k * 170; d.ellipse([x - 50, 110, x + 50, 210], fill=[(240, 90, 120), (250, 200, 60), (120, 200, 90), (160, 100, 60), (240, 240, 230), (90, 160, 240)][k]); d.rectangle([x - 6, 200, x + 6, 250], fill=(220, 190, 140))
    mat_imagem('freezer_arte', img, 0.4)
    p.box('freezer_arte', -X + 0.02, X - 0.02, 0.2, H - 0.1, Z, Z + 0.002); p.uv['freezer_arte'] = lambda v, n: np.stack([(v[:, 0] + X) / (2 * X), (v[:, 1] - 0.2) / (H - 0.3)], 1)
    p.box('esmalte_escuro', -X + 0.04, X - 0.04, H - 0.05, H - 0.04, -Z + 0.04, Z - 0.04)
    for k in range(2):
        q = M.parte(f'tampa_{k + 1}', (0, 0, 0), 'gaveta', desliza=[(0.5 if k == 0 else -0.5), 0, 0])
        x0 = -X + 0.03 + k * (X - 0.03); x1 = x0 + X - 0.03
        q.cham('inox', x0, x1, H, H + 0.025, -Z + 0.01, Z - 0.01, 0.004); q.box('vidro_prateleira', x0 + 0.02, x1 - 0.02, H + 0.025, H + 0.027, -Z + 0.03, Z - 0.03)


@item('calibrador_pneu', 'Calibrador de pneus', 'mobilias', 'posto', comodos=['posto', 'garagem', 'concessionaria'], ambiente=True, colisao='caixa')
def calibrador_pneu(M):
    p = M.base
    p.cham('concreto', -0.2, 0.2, 0.0, 0.1, -0.2, 0.2, 0.01); p.cyl('tinta_vermelha', 0.05, 0.1, 1.2, sec=20)
    p.cham('tinta_vermelha', -0.16, 0.16, 1.2, 1.55, -0.1, 0.1, 0.03)
    torno(p, 'aco_polido', [(0.09, 0.0), (0.09, 0.02), (0.0, 0.022)], 28, 'z', (0, 1.4, 0.1))
    torno(p, 'esmalte', [(0.08, 0.021), (0.08, 0.024)], 28, 'z', (0, 1.4, 0.1))
    for k in range(7): a = math.pi * (0.8 + 1.4 * k / 6); p.seg('esmalte_escuro', (0.065 * math.cos(a), 1.4 + 0.065 * math.sin(a), 0.125), (0.075 * math.cos(a), 1.4 + 0.075 * math.sin(a), 0.125), 0.003, 0.001)
    p.seg('plastico_vermelho', (0, 1.4, 0.126), (0.05, 1.44, 0.126), 0.004, 0.001)
    varrer(p, 'borracha', circ(0.008, 8), [(0.12, 1.3, 0.05)] + [(0.25 + 0.08 * math.cos(a), 0.9 + 0.35 * math.sin(a) + a * 0.05, 0.05) for a in np.linspace(0.5, 2 * math.pi * 2, 30)] + [(0.2, 0.3, 0.1)])
    p.cham('aco_polido', 0.18, 0.22, 0.25, 0.32, 0.08, 0.12, 0.005)


@item('pilha_pneus', 'Pilha de pneus', 'mobilias', 'posto', comodos=['posto', 'garagem', 'ferro_velho', 'concessionaria', 'rua'], ambiente=True, colisao='caixa',
      barricada=True, desmonta={'material': 2}, observacao='pneus queimam por horas (sinal de fumaça)')
def pilha_pneus(M):
    p = M.base; rng = np.random.default_rng(53)
    for k in range(5):
        t = P(); torno(t, 'borracha', [(0.2, 0.0), (0.3, 0.0), (0.33, 0.04), (0.33, 0.15), (0.3, 0.19), (0.2, 0.19), (0.215, 0.095)], 32)
        for j in range(16): a = j / 16 * 2 * math.pi; t.box('plastico_preto', 0.329, 0.334, 0.04, 0.15, -0.02, 0.02) if False else None
        p.merge(t, trimesh.transformations.translation_matrix([rng.uniform(-0.03, 0.03), k * 0.19, rng.uniform(-0.03, 0.03)]))
    t = P(); torno(t, 'borracha', [(0.2, 0.0), (0.3, 0.0), (0.33, 0.04), (0.33, 0.15), (0.3, 0.19), (0.2, 0.19), (0.215, 0.095)], 32)
    p.merge(t, trimesh.transformations.translation_matrix([0.55, 0.31, 0.1]) @ trimesh.transformations.rotation_matrix(math.pi / 2 - 0.25, [1, 0, 0]) @ trimesh.transformations.translation_matrix([0, -0.095, 0]))


# ---------------------------------------------------------------------------- SUPERMERCADO
@item('geladeira_bebidas', 'Geladeira vertical de bebidas', 'mobilias', 'loja', comodos=['supermercado', 'posto', 'diner', 'lanchonete', 'galeria'], conteiner=True, slots=6,
      saque=['agua', 'comida'], colisao='caixa', barricada=True, usa='energia')
def geladeira_bebidas(M):
    p = M.base; X, Z0, Z1, H = 0.35, -0.3, 0.32, 2.0; rng = np.random.default_rng(59)
    carcaca(p, 'esmalte', -X, X, 0.1, H, Z0, Z1, t=0.03); p.cham('esmalte_escuro', -X, X, 0.0, 0.1, Z0, Z1, 0.006)
    p.cham('tinta_vermelha', -X, X, H - 0.25, H, Z1 - 0.02, Z1 + 0.005, 0.01)
    for k, y in enumerate((0.15, 0.5, 0.85, 1.2, 1.5)):
        p.box('aco', -X + 0.03, X - 0.03, y, y + 0.01, Z0 + 0.03, Z1 - 0.05)
        if k == 4: continue
        for i in range(5):
            for j in range(3):
                if rng.random() < 0.3: continue
                x = -0.24 + i * 0.12; z = -0.18 + j * 0.15; mat = ['pet', 'tinta_vermelha', 'tinta_verde'][(i + k) % 3]
                if mat == 'pet': torno(p, 'pet', [(0.03, y + 0.01), (0.03, y + 0.2), (0.012, y + 0.26), (0.012, y + 0.28)], 14, 'y', (x, 0, z))
                else: anel(p, mat, 0.0, 0.032, y + 0.01, y + 0.13, 14, 'y', (x, 0, z))
    q = M.parte('porta', (X, 0, Z1 + 0.01), 'porta', eixo='y', abre_graus=100)
    for (a0, a1, b0, b1) in ((-X, X, 0.1, 0.15), (-X, X, H - 0.3, H - 0.25), (-X, -X + 0.04, 0.1, H - 0.25), (X - 0.04, X, 0.1, H - 0.25)): q.cham('esmalte', a0, a1, b0, b1, Z1, Z1 + 0.03, 0.004)
    q.box('vidro_prateleira', -X + 0.04, X - 0.04, 0.15, H - 0.3, Z1 + 0.012, Z1 + 0.018); puxador_barra(q, 'aco_polido', -X + 0.07, 0.8, 1.4, Z1 + 0.03)


@item('cesta_compras', 'Cesta de compras', 'mobilias', 'loja', comodos=['supermercado', 'posto', 'galeria'], conteiner=True, slots=2, saque=['comida', 'higiene'],
      portatil=True, peso_kg=0.6, ambiente=True, colisao='nenhuma', uso='carrega +4 itens de comida (ocupa as duas mãos)')
def cesta_compras(M):
    p = M.base; X, Z, H = 0.22, 0.15, 0.22; m = 'plastico_vermelho'
    p.cham(m, -X + 0.02, X - 0.02, 0.0, 0.01, -Z + 0.02, Z - 0.02, 0.003)
    for k in range(6):
        y = 0.02 + k * 0.035
        f_ = y / H; xx = X - 0.02 + 0.02 * f_; zz = Z - 0.02 + 0.02 * f_
        for zs in (-1, 1): p.box(m, -xx, xx, y, y + 0.015, *sorted((zs * zz, zs * (zz - 0.006))))
        for xs in (-1, 1): p.box(m, *sorted((xs * xx, xs * (xx - 0.006))), y, y + 0.015, -zz, zz)
    for xs in (-1, 1):
        for zs in (-1, 1): p.seg(m, (xs * (X - 0.02), 0.0, zs * (Z - 0.02)), (xs * X, H, zs * Z), 0.012)
    for zs in (-1, 1): p.box(m, -X, X, H - 0.012, H, *sorted((zs * Z, zs * (Z - 0.008))))
    for xs in (-1, 1): varrer(p, 'plastico_preto', circ(0.006, 8), [(xs * X, H, -0.06), (xs * (X + 0.02), H + 0.12, -0.03), (xs * (X + 0.02), H + 0.12, 0.03), (xs * X, H, 0.06)])
    anel(p, 'lata', 0.0, 0.035, 0.01, 0.12, 14, 'y', (-0.1, 0, 0.0)); p.cham('cartela', 0.0, 0.15, 0.01, 0.2, -0.05, 0.03, 0.004)


# ---------------------------------------------------------------------------- CINEMA
@item('poltronas_cinema', 'Fileira de poltronas de cinema', 'mobilias', 'cinema', comodos=['cinema', 'concha'], sentar=True, vagas=4, colisao='caixa', modulo_m=2.0)
def poltronas_cinema(M):
    p = M.base; w = 0.55; n = 4
    for k in range(n + 1):
        x = -n * w / 2 + k * w
        p.hull('esmalte_escuro', [(x - 0.03, 0.0, -0.25), (x + 0.03, 0.0, -0.25), (x - 0.03, 0.0, 0.2), (x + 0.03, 0.0, 0.2), (x - 0.03, 0.65, -0.35), (x + 0.03, 0.65, -0.35),
                                  (x - 0.03, 0.65, 0.15), (x + 0.03, 0.65, 0.15)])
        p.cham('madeira_escura', x - 0.04, x + 0.04, 0.65, 0.69, -0.35, 0.2, 0.012)
    for k in range(n):
        x = -n * w / 2 + (k + 0.5) * w
        dobrada = k == 2
        if dobrada: p.cham('poltrona_cinema', x - 0.22, x + 0.22, 0.25, 0.65, -0.05, 0.05, 0.03)
        else: p.cham('poltrona_cinema', x - 0.23, x + 0.23, 0.38, 0.48, -0.15, 0.25, 0.04)
        t = P(); t.cham('poltrona_cinema', x - 0.24, x + 0.24, 0.0, 0.62, -0.06, 0.04, 0.04)
        p.merge(t, trimesh.transformations.translation_matrix([0, 0.45, -0.25]) @ trimesh.transformations.rotation_matrix(-0.2, [1, 0, 0]))
        p.box('ouro_velho', x - 0.03, x + 0.03, 0.95, 0.98, -0.37, -0.355)
    p.box('pipoca', 0.3, 0.32, 0.0, 0.01, 0.3, 0.33)
    for k in range(10): x, z = np.random.default_rng(k).uniform(-1.0, 1.0), np.random.default_rng(k + 100).uniform(0.2, 0.5); p.sphere('pipoca', 0.01, x, 0.008, z, 0)


@item('carrinho_pipoca', 'Carrinho de pipoca', 'mobilias', 'cinema', comodos=['cinema', 'cinema_drive_in', 'concha', 'casa_barcos', 'galeria'], colisao='caixa',
      conteiner=True, slots=2, saque=['comida', 'combustivel'], estacao='estoura milho (lata de milho = 3 comida leve)')
def carrinho_pipoca(M):
    p = M.base; X, Z = 0.4, 0.3
    p.cham('tinta_vermelha', -X, X, 0.25, 0.95, -Z, Z, 0.01)
    for xs in (-1, 1): _roda(p, (xs * (X + 0.02), 0.25, 0.0), 0.25, 0.04, mat_aro='ouro_hotel')
    p.cham('aco', -X + 0.05, -X + 0.15, 0.0, 0.25, -0.05, 0.05, 0.006)
    carcaca(p, 'ouro_hotel', -X, X, 0.95, 1.6, -Z, Z, t=0.02, fundo=False)
    for (x0, x1, z0, z1) in ((-X + 0.02, X - 0.02, Z - 0.005, Z), (-X + 0.02, X - 0.02, -Z, -Z + 0.005), (-X, -X + 0.005, -Z, Z), (X - 0.005, X, -Z, Z)):
        p.box('vidro_prateleira', x0, x1, 0.97, 1.58, z0, z1)
    p.hull('pipoca', [(x, 0.97, z) for x in (-X + 0.03, X - 0.03) for z in (-Z + 0.03, Z - 0.03)] + [(0, 1.25, 0)] + [(x, 1.12, z) for x in (-0.25, 0.25) for z in (-0.15, 0.15)])
    torno(p, 'inox', [(0.12, 1.45), (0.1, 1.38), (0.0, 1.37)], 20, fechar=False); p.cyl('inox', 0.008, 1.45, 1.6, sec=8)
    p.hull('tinta_vermelha', [(x, 1.6, z) for x in (-X - 0.04, X + 0.04) for z in (-Z - 0.04, Z + 0.04)] + [(x, 1.75, z) for x in (-0.15, 0.15) for z in (-0.1, 0.1)])
    p.cham('ouro_hotel', -0.08, 0.08, 1.75, 1.85, -0.04, 0.04, 0.02)
    for x in np.linspace(-X + 0.05, X - 0.05, 6): p.box('tinta_branca', x - 0.03, x + 0.03, 0.3, 0.9, Z, Z + 0.003)


@item('projetor_filme', 'Projetor de filme com rolos', 'mobilias', 'cinema', comodos=['cinema', 'cinema_drive_in', 'escolinha'], colisao='caixa', usa='energia',
      desmonta={'pecas': 2, 'sucata': 2}, interacao='projeta o último filme (evento: moral +20 numa noite de cinema)')
def projetor_filme(M):
    p = M.base; m = 'esmalte_escuro'
    p.cham(m, -0.3, 0.3, 0.0, 0.08, -0.35, 0.35, 0.01); p.cyl(m, 0.07, 0.08, 0.95, sec=20)
    p.cham('verde_estacao', -0.16, 0.16, 0.95, 1.3, -0.3, 0.3, 0.03)
    torno(p, 'aco_polido', [(0.06, 0.0), (0.06, 0.2), (0.05, 0.22), (0.045, 0.3)], 20, 'z', (0, 1.12, 0.3))
    torno(p, 'vidro_escuro', [(0.04, 0.3), (0.04, 0.302)], 20, 'z', (0, 1.12, 0.3))
    for z, y in ((0.18, 1.55), (-0.28, 1.5)):
        anel(p, 'aco_polido', 0.2, 0.22, -0.02, 0.02, 40, 'x', (0, y, z)); anel(p, 'disco', 0.05, 0.19, -0.015, 0.015, 40, 'x', (0, y, z))
        for k in range(3): a = k / 3 * 2 * math.pi; p.seg('aco_polido', (0, y, z), (0, y + 0.2 * math.sin(a), z + 0.2 * math.cos(a)), 0.012)
        p.seg(m, (0, y, z), (0, 1.25, z * 0.6), 0.03)
    varrer(p, 'disco', Polygon([(-0.0008, -0.017), (0.0008, -0.017), (0.0008, 0.017), (-0.0008, 0.017)]), [(0.0, 1.35, 0.18), (0.0, 1.2, 0.25), (0.0, 1.05, 0.0), (0.0, 1.3, -0.28)])


# ---------------------------------------------------------------------------- HOTEL / MOTEL
@item('balcao_recepcao', 'Balcão de recepção com quadro de chaves', 'mobilias', 'hotel', comodos=['hotel', 'motel', 'rodoviaria', 'clinica'], conteiner=True, slots=4,
      saque=['chaves', 'moedas', 'papel'], colisao='caixa', modulo_m=2.0)
def balcao_recepcao(M):
    p = M.base; X, m = 1.0, 'madeira_escura'
    p.cham(m, -X, X, 0.0, 1.1, 0.1, 0.5, 0.01); p.cham('granito', -X - 0.03, X + 0.03, 1.1, 1.14, 0.08, 0.55, 0.008)
    for x in np.linspace(-X + 0.25, X - 0.25, 4): almofadada(p, m, x - 0.22, x + 0.22, 0.12, 1.0, 0.5, 0.52, borda=0.05)
    p.cham(m, -X, X, 0.0, 0.75, -0.25, 0.1, 0.01)
    torno(p, 'ouro_hotel', [(0.04, 1.14), (0.04, 1.15), (0.038, 1.17), (0.02, 1.2), (0.004, 1.21)], 20, 'y', (0.5, 0, 0.35)); p.cyl('ouro_hotel', 0.004, 1.21, 1.22, x=0.5, z=0.35, sec=8)
    p.cham('cartela', -0.5, -0.2, 1.14, 1.17, 0.2, 0.45, 0.003)
    W = 1.2; y0 = 1.2                                                                         # quadro de chaves atrás (na parede)
    p.cham(m, -W / 2, W / 2, y0, y0 + 0.8, -0.65, -0.62, 0.005)
    for i in range(8):
        for j in range(3):
            x = -W / 2 + 0.1 + i * 0.143; y = y0 + 0.15 + j * 0.25
            p.cham('ouro_hotel', x - 0.004, x + 0.004, y, y + 0.04, -0.62, -0.58, 0.002)
            if (i + j) % 3: p.cham('ouro_hotel', x - 0.006, x + 0.006, y - 0.09, y - 0.01, -0.6, -0.595, 0.002); p.cham('madeira', x - 0.015, x + 0.015, y - 0.15, y - 0.08, -0.6, -0.59, 0.006)


@item('carrinho_bagagem', 'Carrinho de bagagem de hotel', 'mobilias', 'hotel', comodos=['hotel', 'motel', 'estacao', 'rodoviaria'], conteiner=True, slots=4, saque=['roupas', 'remedios'],
      portatil=True, peso_kg=20.0, colisao='caixa', uso='carrega 3x mais saque (devagar e barulhento)')
def carrinho_bagagem(M):
    p = M.base; X, Z = 0.5, 0.3; g = 'ouro_hotel'
    p.cham('tapete', -X, X, 0.12, 0.17, -Z, Z, 0.01)
    for xs in (-1, 1):
        for zs in (-1, 1): _roda(p, (xs * (X - 0.08), 0.06, zs * (Z - 0.06)), 0.06, 0.03, mat_aro='aco')
    pts = [(-X + 0.03, 0.17, 0)] + [(-X + 0.03, 1.3, 0)] + [((X - 0.03) * math.cos(a) * -1, 1.3 + 0.55 * math.sin(a), 0) for a in np.linspace(0, math.pi, 16)] + [(X - 0.03, 1.3, 0), (X - 0.03, 0.17, 0)]
    for zs in (-1, 1): p.cyl(g, 0.016, 0.17, 1.3, x=-X + 0.03, z=zs * (Z - 0.03), sec=12); p.cyl(g, 0.016, 0.17, 1.3, x=X - 0.03, z=zs * (Z - 0.03), sec=12)
    varrer(p, g, circ(0.018, 12), [((X - 0.03) * math.cos(a), 1.3 + 0.3 * math.sin(a), 0) for a in np.linspace(0, math.pi, 18)])
    cyl_eixo(p, g, 0.018, -X + 0.03, X - 0.03, 'x', (0, 1.3, 0), 12)
    for xs in (-1, 1): cyl_eixo(p, g, 0.014, -Z + 0.03, Z - 0.03, 'z', (xs * (X - 0.03), 1.3, 0), 10)
    t = P(); mala_viagem(type('M', (), {'base': t, 'parte': lambda s, *a, **k: P()})())
    p.merge(t, trimesh.transformations.translation_matrix([0.0, 0.17, 0.0]) @ trimesh.transformations.rotation_matrix(0.1, [0, 1, 0]) @ np.diag([0.9, 1, 0.9, 1]))
    p.cham('mala_azul', -0.3, 0.1, 0.43, 0.75, -0.12, 0.12, 0.03); p.cham('tinta_vermelha', 0.15, 0.4, 0.43, 0.58, -0.15, 0.1, 0.02)


@item('carrinho_camareira', 'Carrinho de camareira', 'mobilias', 'hotel', comodos=['hotel', 'motel', 'clinica'], conteiner=True, slots=4, saque=['higiene', 'roupas', 'tecido'],
      portatil=True, peso_kg=30.0, colisao='caixa')
def carrinho_camareira(M):
    p = M.base; X, Z = 0.55, 0.25
    carcaca(p, 'plastico_cinza', -X, X, 0.1, 1.0, -Z, Z, t=0.02, fundo=True)
    for xs in (-1, 1):
        for zs in (-1, 1): _roda(p, (xs * (X - 0.06), 0.05, zs * (Z - 0.05)), 0.05, 0.025, mat_aro='aco')
    for k, y in enumerate((0.12, 0.42, 0.72)):
        p.box('plastico_cinza', -X + 0.02, X - 0.02, y, y + 0.015, -Z + 0.01, Z)
        for i in range(4): fofo(p, 'lencol' if (i + k) % 2 else 'travesseiro', -0.36 + i * 0.24, y + 0.06, 0.02, 0.1, 0.045, 0.17, 0.3, 0.2, (8, 10))
    varrer(p, 'lona_crua', Polygon([(-0.004, -0.15), (0.004, -0.15), (0.004, 0.15), (-0.004, 0.15)]), [(X + 0.02, 0.2, 0.0), (X + 0.04, 1.0, 0.0)])
    fofo(p, 'lona_crua', X + 0.2, 0.55, 0.0, 0.18, 0.45, 0.2, 0.6, 0.6, (12, 14))
    for k in range(3): torno(p, ['plastico_branco', 'plastico_azul', 'tinta_amarela'][k], [(0.04, 1.0), (0.04, 1.18), (0.015, 1.22), (0.015, 1.25)], 14, 'y', (-0.4 + k * 0.12, 0, 0))


@item('frigobar', 'Frigobar', 'mobilias', 'hotel', comodos=['hotel', 'motel', 'escritorio'], conteiner=True, slots=2, saque=['comida', 'agua'], colisao='caixa', portatil=True, peso_kg=20.0)
def frigobar(M):
    p = M.base; X, Z0, Z1, H = 0.24, -0.24, 0.22, 0.55; rng = np.random.default_rng(61)
    carcaca(p, 'madeira_escura', -X, X, 0.03, H, Z0, Z1, t=0.03); p.box('plastico_preto', -X + 0.02, X - 0.02, 0.0, 0.03, Z0 + 0.02, Z1 - 0.02)
    p.box('aco', -X + 0.03, X - 0.03, 0.27, 0.28, Z0 + 0.03, Z1 - 0.03)
    for y in (0.06, 0.28):
        for i in range(4):
            if rng.random() < 0.3: continue
            x = -0.16 + i * 0.1; torno(p, ['pet', 'ambar', 'vidro_prateleira'][i % 3], [(0.022, y), (0.022, y + 0.14), (0.009, y + 0.18), (0.009, y + 0.2)], 12, 'y', (x, 0, -0.05))
    q = M.parte('porta', (-X, 0, Z1 + 0.012), 'porta', eixo='y', abre_graus=-105)
    q.cham('madeira_escura', -X, X, 0.03, H, Z1, Z1 + 0.03, 0.006); q.cham('ouro_hotel', X - 0.06, X - 0.03, 0.3, 0.45, Z1 + 0.03, Z1 + 0.045, 0.004)
    for y in (0.15, 0.35): q.box('aco', -X + 0.04, X - 0.04, y, y + 0.012, Z1 - 0.05, Z1)


# ---------------------------------------------------------------------------- ESTACAO / RODOVIARIA
@item('quadro_horarios', 'Quadro de horários de partida', 'mobilias', 'estacao', montagem='wall', altura_sugerida_m=2.0, comodos=['estacao', 'rodoviaria'], ambiente=True,
      colisao='nenhuma', pista='o último trem de resgate (pista da fase 4)')
def quadro_horarios(M):
    p = M.base; W, H = 1.8, 0.9
    img = Image.new('RGB', (1200, 600), (20, 22, 24)); d = ImageDraw.Draw(img); am = (250, 200, 60)
    texto_c(d, (600, 50), 'PARTIDAS', 50, (240, 240, 230))
    for i, (h, dest, st) in enumerate((('06:40', 'CAPITAL', 'CANCELADO'), ('09:15', 'PORTO NOVO', 'CANCELADO'), ('13:20', 'VALE ALTO', 'CANCELADO'),
                                       ('17:05', 'RESGATE · PLAT. 1', 'EMBARQUE'), ('21:30', '----', '----'))):
        y = 120 + i * 92
        d.text((50, y), h, font=fonte(48), fill=am); d.text((260, y), dest, font=fonte(48), fill=am); d.text((850, y), st, font=fonte(40), fill=(250, 90, 60) if st == 'CANCELADO' else am)
        d.line([(30, y + 75), (1170, y + 75)], fill=(50, 52, 54), width=3)
    mat_imagem('horarios_img', img, 0.4)
    p.cham('verde_estacao', -W / 2 - 0.05, W / 2 + 0.05, -0.05, H + 0.05, 0.0, 0.08, 0.01)
    p.box('horarios_img', -W / 2, W / 2, 0, H, 0.08, 0.082); p.uv['horarios_img'] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)


@item('relogio_estacao', 'Relógio de plataforma (dupla face)', 'mobilias', 'estacao', montagem='wall', altura_sugerida_m=2.6, comodos=['estacao', 'rodoviaria', 'rua'], ambiente=True,
      colisao='nenhuma', parado_em='3:17')
def relogio_estacao(M):
    p = M.base; R = 0.25
    p.cham('verde_estacao', -0.04, 0.04, 0.3, 0.38, 0.0, 0.5, 0.01); p.seg('verde_estacao', (0, 0.1, 0.02), (0, 0.32, 0.35), 0.03)
    for zs in (-1, 1):
        zc = 0.5 + zs * 0.0
    anel(p, 'verde_estacao', R - 0.02, R, -0.07, 0.07, 48, 'z', (0, 0.05, 0.75), chanfro=0.008)
    for zs in (-1, 1):
        torno(p, 'mostrador', [(R - 0.02, 0.0), (R - 0.02, 0.003)], 48, 'z', (0, 0.05, 0.75 + zs * 0.06))
        for ang, L, w in ((-(3 + 17 / 60) / 12 * 2 * math.pi, 0.11, 0.012), (-(17 / 60) * 2 * math.pi, 0.17, 0.008)):
            a = -ang * zs; p.seg('esmalte_escuro', (0, 0.05, 0.75 + zs * 0.064), (L * math.sin(a), 0.05 + L * math.cos(a), 0.75 + zs * 0.064), w, 0.003)
    p.uv['mostrador'] = lambda v, n: np.stack([(v[:, 0] * np.sign(v[:, 2] - 0.75 + 1e-9) + R - 0.02) / (2 * (R - 0.02)), (v[:, 1] - 0.05 + R - 0.02) / (2 * (R - 0.02))], 1)
    p.seg('verde_estacao', (0, 0.32, 0.5), (0, 0.32, 0.75), 0.04); p.cyl('verde_estacao', 0.02, 0.28, 0.33, x=0, z=0.75, sec=10)


@item('maquina_lanches', 'Máquina de lanches', 'mobilias', 'estacao', comodos=['estacao', 'rodoviaria', 'escolinha', 'clinica', 'hotel', 'galeria', 'delegacia'], conteiner=True,
      slots=4, saque=['comida', 'agua'], ferramenta='pe_de_cabra (quebra o vidro: barulho)', colisao='caixa', barricada=True)
def maquina_lanches(M):
    p = M.base; X, Z0, Z1, H = 0.45, -0.4, 0.4, 1.8; rng = np.random.default_rng(67)
    p.cham('azul_vending', -X, X, 0.0, H, Z0, Z1, 0.015)
    p.box('esmalte_escuro', -X + 0.04, 0.2, 0.35, H - 0.06, Z1 - 0.3, Z1 - 0.005)
    for k in range(5):
        y = 0.42 + k * 0.26; p.box('aco', -X + 0.04, 0.2, y, y + 0.008, Z1 - 0.3, Z1 - 0.02)
        for i in range(5):
            if rng.random() < 0.35: continue
            x = -X + 0.09 + i * 0.12; c = ['tinta_vermelha', 'tinta_amarela', 'tinta_verde', 'cartela', 'rotulo_chocolate' if False else 'tinta_azul'][int(rng.integers(0, 5))]
            p.cham(c, x - 0.04, x + 0.04, y + 0.01, y + 0.16, Z1 - 0.12, Z1 - 0.07, 0.01)
            varrer(p, 'aco_polido', circ(0.003, 6), [(x + 0.03 * math.cos(a), y + 0.03 + 0.03 * math.sin(a), Z1 - 0.28 + a * 0.02) for a in np.linspace(0, 12, 40)])
    p.box('vidro_prateleira', -X + 0.03, 0.21, 0.33, H - 0.05, Z1 - 0.004, Z1 + 0.002)
    for (a, b, L) in ((-0.1, 1.2, 0.2), (0.0, 1.0, 0.25), (-0.2, 0.9, 0.18)): p.seg('vidro_caco', (a, b, Z1 + 0.003), (a + L * 0.7, b + L * 0.5, Z1 + 0.003), 0.003, 0.001)
    p.cham('esmalte_escuro', 0.24, X - 0.03, 0.9, 1.4, Z1 - 0.005, Z1 + 0.01, 0.006)
    for i in range(4):
        for j in range(3): p.cham('aco_polido', 0.27 + j * 0.05, 0.31 + j * 0.05, 1.0 + i * 0.06, 1.04 + i * 0.06, Z1 + 0.01, Z1 + 0.02, 0.003)
    p.cham('esmalte_escuro', 0.27, 0.4, 1.3, 1.36, Z1 + 0.01, Z1 + 0.012, 0.002)
    p.cham('esmalte_escuro', -X + 0.06, 0.18, 0.1, 0.28, Z1 - 0.005, Z1 + 0.01, 0.008)


@item('carrinho_plataforma', 'Carrinho de carga de plataforma', 'mobilias', 'estacao', comodos=['estacao', 'correios', 'armazem', 'fabrica'], conteiner=True, slots=4,
      saque=['materiais', 'comida', 'roupas'], portatil=True, peso_kg=60.0, colisao='caixa')
def carrinho_plataforma(M):
    p = M.base; X, Z = 0.9, 0.45
    for k in range(9): p.cham('madeira_crua', -X, X, 0.38, 0.42, -Z + k * 0.1, -Z + k * 0.1 + 0.095, 0.004)
    for zs in (-1, 1): p.cham('aco_pintado', -X, X, 0.3, 0.38, zs * (Z - 0.03) - 0.03, zs * (Z - 0.03) + 0.03, 0.005)
    for xs in (-1, 1): _roda(p, (xs * (X - 0.25), 0.25, 0.0), 0.25, 0.05, mat_aro='aco_pintado') if False else None
    for xs in (-0.5, 0.5):
        for zs in (-1, 1): _roda(p, (xs * 1.0, 0.18, zs * (Z + 0.04)), 0.18, 0.05, eixo='x', mat_aro='aco_pintado')
        cyl_eixo(p, 'aco', 0.02, -Z - 0.06, Z + 0.06, 'z', (xs, 0.18, 0), 10)
    p.seg('aco_pintado', (X, 0.38, -0.2), (X + 0.6, 0.85, -0.05), 0.03); p.seg('aco_pintado', (X, 0.38, 0.2), (X + 0.6, 0.85, 0.05), 0.03)
    cyl_eixo(p, 'aco_pintado', 0.02, -0.08, 0.08, 'z', (X + 0.6, 0.85, 0), 10)
    for xs in (-1, 1): p.cham('aco_pintado', xs * X - 0.02, xs * X + 0.02, 0.42, 1.0, -Z, Z, 0.004)
    t = P(); caixa_madeira(type('M', (), {'base': t, 'parte': lambda s, *a, **k: P()})()) if 'caixa_madeira' in globals() else None
    p.merge(t, trimesh.transformations.translation_matrix([-0.3, 0.42, 0.0]))
    p.cham('lona_crua', 0.15, 0.75, 0.42, 0.7, -0.3, 0.3, 0.05)
