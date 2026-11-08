# Lote 14: armazenamento funcional do abrigo (armas, comida, caixas com inventario e paletes de material de construcao).
# Executado por gerar_props.py (usa as mesmas funcoes e materiais dos lotes anteriores).
# Campos de jogo deste lote:
#   grade [w, h]        inventario em grade do conteiner (mesmas celulas de 0,28 m de jogo/sistemas/grade.gd)
#   aceita              categorias que o conteiner aceita (vazio = qualquer item)
#   vagas_armas         [{tipo, pos, rot_y}] onde cada arma fica exposta: tipo longa (fuzil, espingarda, carabina, rifle, arco, besta),
#                       curta (pistola, revolver, smg compacta) ou branca (faca, facao, machadinha, bastao); pos e o ponto de apoio
#                       da arma (coronha no chao do rack / gancho), cano para cima nas longas
#   exibe               [{y, x, z}] tampos de prateleira onde o jogo poe os modelos dos itens guardados (x e z = [min, max])
#   estoque             {item, max} paletes e pilhas: o material que guardam e quanto cabe
#   partes tipo camada  camadas do estoque (o jogo esconde de cima para baixo conforme o estoque cai; 'unidades' por camada)
#   empilhavel          caixas que encaixam uma em cima da outra (altura_m)
#   constroi/ferramenta receita para o jogador fazer (os ingredientes sao ids do loot)
CORES.update({'tela_galinheiro': (60, 62, 64), 'verde_caixa': (18, 34, 14), 'plastico_azul_cx': (10, 40, 110), 'tampa_cinza': (70, 74, 78),
              'cromado': (200, 202, 206), 'cofre': (16, 18, 20), 'feltro': (14, 30, 18), 'fita_cinta': (6, 6, 6), 'madeira_lenha': (120, 84, 52),
              'telha_ondulada': (90, 92, 88), 'etiqueta': (236, 230, 210)})
METALICOS.update({'tela_galinheiro': (0.8, 0.5), 'cromado': (1.0, 0.12), 'cofre': (0.6, 0.35), 'telha_ondulada': (0.6, 0.55)})
FOSCOS.update({'verde_caixa': 0.75, 'plastico_azul_cx': 0.45, 'tampa_cinza': 0.5, 'feltro': 0.95, 'fita_cinta': 0.5})
TEX_PROPRIAS += [('verde_caixa', 'tecido', 1.0, 256), ('feltro', 'tecido', 0.5, 512), ('madeira_lenha', 'couro', 0.5, 512)]


def _mover(q, d):
    """Leva uma parte montada em coordenadas locais (origem no eixo) para as coordenadas da montagem, mantendo a UV local."""
    d = np.array(d, float)
    for ms in q.parts.values():
        for m in ms: m.apply_translation(d)
    for k, f in list(q.uv.items()): q.uv[k] = (lambda f: (lambda v, n: f(v - d, n)))(f)


def _tab_h(p, x0, x1, y0, y1, z0, z1, mat='madeira_crua', pregos=True, c=0.003):
    """Tabua horizontal ao longo de x, com dois pregos em cada ponta."""
    p.cham(mat, x0, x1, y0, y1, z0, z1, c)
    if pregos:
        for x in (x0 + 0.03, x1 - 0.03):
            for z in (z0 + (z1 - z0) * 0.3, z0 + (z1 - z0) * 0.7):
                torno(p, 'aco', [(0.0045, 0), (0.0045, 0.0012), (0.0028, 0.0022)], 10, 'y', (x, y1 - 0.0002, z))


def _caixa_rotulo(texto, fundo, cor):
    img = Image.new('RGB', (512, 160), fundo); d = ImageDraw.Draw(img); texto_c(d, (256, 80), texto, 76, cor, larg=480); return img


def _lata_simples(p, c, r=0.038, h=0.11, mat='lata', rot=None):
    anel(p, mat, r - 0.002, r, c[1], c[1] + h, 20, 'y', (c[0], 0, c[2]))
    torno(p, 'lata', [(r - 0.002, c[1] + h - 0.004), (r + 0.001, c[1] + h - 0.002), (r + 0.001, c[1] + h), (0.0, c[1] + h - 0.003)], 20, 'y', (c[0], 0, c[2]))
    torno(p, 'lata', [(r - 0.003, c[1]), (r + 0.001, c[1] + 0.002), (r + 0.001, c[1] + 0.004), (0.0, c[1] + 0.003)], 20, 'y', (c[0], 0, c[2]))


# ---------------------------------------------------------------------------- ARMAS
@item('armario_armas_abrigo', 'Armário de armas de madeira com tela', 'mobilias', 'armazenamento', comodos=['abrigo', 'casas', 'quartel', 'fazenda'],
      conteiner=True, slots=12, grade=[6, 4], saque=['armas', 'municao'], aceita=['armas', 'municao', 'acessorios'], trancado=True, tranca='cadeado',
      ferramenta='martelo', constroi={'tabua': 8, 'caixa_pregos': 1, 'dobradicas': 1, 'corrente_cadeado': 1, 'arame_liso': 1}, fase=2,
      estacao='arsenal (guarda e mostra as armas da base; moradores pegam daqui para a vigia)', barricada=True,
      vagas_armas=[{'tipo': 'longa', 'pos': [round(-0.42 + k * 0.168, 3), 0.11, -0.12], 'rot_y': 0} for k in range(6)] +
                  [{'tipo': 'curta', 'pos': [round(x, 3), 1.42, -0.2], 'rot_y': 0} for x in (-0.36, -0.12, 0.12, 0.36)] +
                  [{'tipo': 'branca', 'pos': [round(x, 3), 1.72, -0.2], 'rot_y': 0} for x in (-0.3, 0.0, 0.3)],
      exibe=[{'y': 1.265, 'x': [-0.5, 0.5], 'z': [-0.21, 0.15]}])
def armario_armas_abrigo(M):
    p = M.base; X, Z0, Z1, H = 0.55, -0.24, 0.2, 2.0
    for xs in (-1, 1):                                                               # montantes 2x2"
        for z in (Z0, Z1 - 0.045):
            p.cham('madeira_crua', xs * X - 0.045 * (xs > 0), xs * X + 0.045 * (xs < 0), 0.0, H, z, z + 0.045, 0.004)
    for y in np.arange(0.0, H - 0.01, 0.14):                                          # fundo de tabuas horizontais
        _tab_h(p, -X, X, y, y + 0.135, Z0 - 0.02, Z0, pregos=False)
    for xs in (-1, 1):                                                               # laterais de tabua
        for y in np.arange(0.0, H - 0.01, 0.14):
            p.cham('madeira_crua', (X if xs > 0 else -X - 0.02), (X + 0.02 if xs > 0 else -X), y, y + 0.135, Z0 - 0.02, Z1, 0.003)
    _tab_h(p, -X - 0.02, X + 0.02, H, H + 0.025, Z0 - 0.02, Z1 + 0.01)                   # tampo
    _tab_h(p, -X, X, 0.0, 0.1, Z0, Z1 - 0.05)                                          # base (onde apoiam as coronhas)
    p.cham('feltro', -X + 0.01, X - 0.01, 0.1, 0.105, Z0 + 0.01, Z1 - 0.06, 0.002)
    # pente de cima: tabua com 6 entalhes que seguram os canos
    poly = sbox(-X, X, -0.1, 0.0)
    for k in range(6): poly = poly.difference(sbox(-0.42 + k * 0.168 - 0.028, -0.42 + k * 0.168 + 0.028, -0.065, 0.001).union(Point(-0.42 + k * 0.168, -0.065).buffer(0.028, 12)))
    extrudar_xz(p, 'madeira', affinity.translate(poly, 0, 0), 0.92, 0.945)
    p.parts['madeira'][-1].apply_translation([0, 0, -0.05])
    p.cham('feltro', -X + 0.01, X - 0.01, 0.945, 0.95, Z0 + 0.0, Z0 + 0.04, 0.001)
    # prateleira de municao e painel de ganchos (pistolas e facas)
    _tab_h(p, -X, X, 1.24, 1.265, Z0, Z1 - 0.05)
    p.cham('madeira_escura', -X + 0.01, X - 0.01, 1.3, 1.9, Z0 - 0.002, Z0 + 0.012, 0.002)
    for x in np.arange(-X + 0.05, X - 0.04, 0.06):
        for y in np.arange(1.33, 1.89, 0.06): cyl_eixo(p, 'plastico_preto', 0.004, Z0 + 0.0115, Z0 + 0.0125, 'z', (x, y, 0), 6)
    for x in (-0.36, -0.12, 0.12, 0.36):                                              # ganchos de pistola (duplos)
        for dx in (-0.025, 0.025): varrer(p, 'aco_polido', circ(0.003, 8), [(x + dx, 1.45, Z0 + 0.012), (x + dx, 1.45, Z0 + 0.07), (x + dx, 1.47, Z0 + 0.08)])
    for x in (-0.3, 0.0, 0.3):                                                        # barra magnetica das facas
        p.cham('plastico_preto', x - 0.12, x + 0.12, 1.7, 1.74, Z0 + 0.012, Z0 + 0.03, 0.004)
        for xx in (x - 0.11, x + 0.11): torno(p, 'aco_polido', [(0.005, 0), (0.005, 0.002)], 10, 'z', (xx, 1.72, Z0 + 0.03))
    for k, x in enumerate((-0.4, -0.22, 0.05, 0.3)):                                  # caixas de municao na prateleira
        q = P(); q.cham('verde_caixa' if k % 2 else 'cartela', -0.07, 0.07, 0.0, 0.08 + 0.02 * (k % 2), -0.05, 0.05, 0.004)
        q.cham('aco', -0.025, 0.025, 0.08 + 0.02 * (k % 2), 0.09 + 0.02 * (k % 2), -0.008, 0.008, 0.002)
        p.merge(q, trimesh.transformations.translation_matrix([x, 1.265, -0.08]))
    # portas: quadro de sarrafo com tela de galinheiro, abrem para fora
    for nome, hx, sgn in (('porta_esq', -X - 0.02, 1), ('porta_dir', X + 0.02, -1)):
        q = M.parte(nome, (hx, 0, Z1 + 0.01), 'porta', eixo='y', abre_graus=-115 * sgn)
        x0, x1 = sorted((hx, sgn * 0.003))
        for (a0, a1, b0, b1) in ((x0, x0 + 0.06, 0.05, H - 0.02), (x1 - 0.06, x1, 0.05, H - 0.02), (x0, x1, 0.05, 0.13), (x0, x1, H - 0.1, H - 0.02), (x0, x1, 1.0, 1.08)):
            q.cham('madeira_crua', a0, a1, b0, b1, Z1, Z1 + 0.025, 0.003)
        q.seg('madeira_crua', (x0 + 0.04, 0.12, Z1 + 0.028), (x1 - 0.04, 0.99, Z1 + 0.028), 0.05, 0.02)         # mao-francesa
        for (y0, y1) in ((0.13, 1.0), (1.08, H - 0.1)):                                  # tela hexagonal (fios cruzados)
            for k, u in enumerate(np.arange(x0 + 0.06, x1 - 0.07, 0.045)):
                for yy in np.arange(y0, y1 - 0.03, 0.07):
                    q.seg('tela_galinheiro', (u, yy, Z1 + 0.026), (u + 0.0225, yy + 0.035, Z1 + 0.026), 0.0014, 0.0014)
                    q.seg('tela_galinheiro', (u + 0.045, yy, Z1 + 0.026), (u + 0.0225, yy + 0.035, Z1 + 0.026), 0.0014, 0.0014)
                    q.seg('tela_galinheiro', (u + 0.0225, yy + 0.035, Z1 + 0.026), (u + 0.0225, yy + 0.07, Z1 + 0.026), 0.0014, 0.0014)
        for y in (0.3, H - 0.3):                                                         # dobradicas
            q.cham('galvanizado', hx - 0.004 if sgn > 0 else hx - 0.06, hx + 0.06 if sgn > 0 else hx + 0.004, y, y + 0.07, Z1 + 0.025, Z1 + 0.028, 0.001)
        xa = x1 - 0.02 if sgn > 0 else x0 + 0.02
        p_ = q; p_.cham('galvanizado', xa - 0.015, xa + 0.015, 1.0, 1.08, Z1 + 0.025, Z1 + 0.03, 0.002)    # porta-cadeado
        anel(q, 'galvanizado', 0.006, 0.01, Z1 + 0.03, Z1 + 0.045, 12, 'z', (xa, 1.04, 0))
    # cadeado pendurado
    p.cham('latao', -0.02, 0.02, 0.95, 0.995, Z1 + 0.04, Z1 + 0.058, 0.004)
    varrer(p, 'aco_polido', circ(0.003, 8), [(-0.012, 0.995, Z1 + 0.049), (-0.012, 1.03, Z1 + 0.049), (0.0, 1.045, Z1 + 0.049), (0.012, 1.03, Z1 + 0.049), (0.012, 0.995, Z1 + 0.049)])


@item('cofre_armas', 'Cofre de armas de aço', 'mobilias', 'armazenamento', comodos=['delegacia', 'mansao', 'casas', 'concessionaria'],
      conteiner=True, slots=14, grade=[6, 5], saque=['armas', 'municao', 'moedas'], aceita=['armas', 'municao', 'acessorios', 'remedios'],
      trancado=True, tranca='segredo (achar o bilhete com a combinação; arrombar leva 10 min e faz muito barulho)', peso_kg=280, fase=2,
      estacao='arsenal blindado (à prova de saqueadores e de incêndio)',
      vagas_armas=[{'tipo': 'longa', 'pos': [round(-0.25 + k * 0.1, 3), 0.1, -0.12], 'rot_y': 0} for k in range(6)] +
                  [{'tipo': 'curta', 'pos': [round(x, 3), 1.1, 0.22], 'rot_y': 0} for x in (-0.18, -0.06, 0.06, 0.18)],
      exibe=[{'y': 1.32, 'x': [-0.3, 0.3], 'z': [-0.2, 0.15]}])
def cofre_armas(M):
    p = M.base; X, Z0, Z1, H = 0.36, -0.24, 0.2, 1.55
    carcaca(p, 'cofre', -X, X, 0.03, H, Z0, Z1, t=0.05)
    p.cham('cofre', -X - 0.005, X + 0.005, 0.0, 0.035, Z0 - 0.005, Z1 + 0.005, 0.006)
    p.box('feltro', -X + 0.05, X - 0.05, 0.08, H - 0.05, Z0 + 0.008, Z0 + 0.012)
    for xs in (-1, 1): p.box('feltro', xs * (X - 0.05) - 0.002 * (xs > 0), xs * (X - 0.05) + 0.002 * (xs < 0), 0.08, H - 0.05, Z0, Z1)
    p.box('feltro', -X + 0.05, X - 0.05, 0.08, 0.1, Z0, Z1)
    p.cham('feltro', -X + 0.05, X - 0.05, 0.75, 0.8, Z0, Z0 + 0.09, 0.006)                                       # pente
    for k in range(6): cyl_eixo(p, 'fita_cinta', 0.016, Z0 + 0.0, Z0 + 0.092, 'z', (-0.25 + k * 0.1, 0.8, 0), 14)
    p.cham('cofre', -X + 0.05, X - 0.05, 1.3, 1.32, Z0, Z1 - 0.01, 0.003); p.box('feltro', -X + 0.05, X - 0.05, 1.32, 1.322, Z0, Z1 - 0.01)
    p.cham('verde_caixa', -0.25, -0.08, 1.322, 1.41, -0.15, -0.03, 0.005); p.cham('cartela', 0.0, 0.18, 1.322, 1.38, -0.15, -0.02, 0.004)
    # porta grossa com pinos, manopla de 5 raios e disco do segredo
    q = M.parte('porta', (X, 0, Z1), 'porta', eixo='y', abre_graus=-105)
    q.cham('cofre', -2 * X + 0.002, 0.0, 0.035, H - 0.002, 0.0, 0.11, 0.012)
    q.cham('cofre', -2 * X + 0.06, -0.06, 0.1, H - 0.07, -0.06, 0.0, 0.006)                                   # miolo (entra no vao)
    for y in np.linspace(0.25, H - 0.25, 4):
        for xx in (-2 * X + 0.06, -0.06): cyl_eixo(q, 'cromado', 0.014, xx - 0.05 if xx < -X else xx, xx + 0.05 if xx > -X else xx, 'x', (0, y, -0.03), 14)
    c = (-X, 0.95, 0.11)
    torno(q, 'cromado', [(0.06, 0.0), (0.058, 0.01), (0.05, 0.014), (0.02, 0.016)], 36, 'z', c)                     # disco
    for k in range(50):
        a = k * 2 * math.pi / 50; q.box('esmalte', c[0] + 0.054 * math.cos(a) - 0.0007, c[0] + 0.054 * math.cos(a) + 0.0007, c[1] + 0.054 * math.sin(a) - 0.0045 * (1 + (k % 5 == 0)),
                                        c[1] + 0.054 * math.sin(a) + 0.0045 * (1 + (k % 5 == 0)), c[2] + 0.0105, c[2] + 0.0115)
    torno(q, 'cromado', [(0.035, 0.0), (0.035, 0.012), (0.03, 0.02)], 24, 'z', (-X, 0.95, 0.11 + 0.014))
    cm = (-X, 0.7, 0.11); torno(q, 'cromado', [(0.03, 0.0), (0.03, 0.03), (0.02, 0.04)], 24, 'z', cm)                # manopla
    for k in range(5):
        a = k * 2 * math.pi / 5 + 0.3; e = (cm[0] + 0.12 * math.cos(a), cm[1] + 0.12 * math.sin(a), cm[2] + 0.03)
        varrer(q, 'cromado', circ(0.007, 10), [(cm[0], cm[1], cm[2] + 0.03), e]); q.sphere('cromado', 0.014, *e, sub=2)
    img = Image.new('RGB', (512, 128), (16, 18, 20)); d = ImageDraw.Draw(img); texto_c(d, (256, 64), 'FORTALEZA', 70, (200, 170, 90)); mat_imagem('marca_cofre', img, 0.4, 0.6)
    q.box('marca_cofre', -X - 0.15, -X + 0.15, 1.3, 1.375, 0.11, 0.1105); q.uv['marca_cofre'] = lambda v, n: np.stack([(v[:, 0] + X + 0.15) / 0.3, (v[:, 1] - 1.3) / 0.075], 1)
    _mover(q, (X, 0, Z1))
    for y in (0.25, H - 0.25): p.cyl('cofre', 0.018, y - 0.06, y + 0.06, x=X + 0.012, z=Z1 + 0.02, sec=14)


@item('rack_armas_parede', 'Suporte de parede para armas', 'mobilias', 'armazenamento', montagem='wall', altura_sugerida_m=1.05,
      comodos=['abrigo', 'casas', 'fazenda', 'casa_de_campo'], constroi={'tabua': 2, 'cano_metal': 1, 'caixa_pregos': 1}, ferramenta='martelo', fase=1,
      estacao='rack (mostra até 4 armas longas deitadas e 3 armas brancas)',
      vagas_armas=[{'tipo': 'longa', 'pos': [0.0, round(0.12 + k * 0.2, 3), 0.07], 'rot_y': 90, 'deitada': True} for k in range(4)] +
                  [{'tipo': 'branca', 'pos': [round(x, 3), 0.9, 0.04], 'rot_y': 0} for x in (-0.3, 0.0, 0.3)])
def rack_armas_parede(M):
    p = M.base; W = 1.1
    for xs in (-1, 1):                                                                 # duas tabuas verticais
        x = xs * 0.4; p.cham('madeira_escura', x - 0.06, x + 0.06, 0.0, 1.0, 0.0, 0.022, 0.003)
        for y in (0.08, 0.92):
            torno(p, 'aco', [(0.006, 0), (0.006, 0.002), (0.004, 0.004)], 10, 'z', (x, y, 0.0215))
        for k in range(4):                                                             # ganchos de cano dobrado com borracha
            y = 0.12 + k * 0.2
            varrer(p, 'ferrugem', circ(0.008, 10), [(x, y, 0.022), (x, y, 0.09), (x, y + 0.02, 0.105), (x, y + 0.045, 0.1)])
            anel(p, 'borracha', 0.008, 0.011, 0.04, 0.09, 12, 'z', (x, y, 0))
    p.cham('madeira_escura', -W / 2, W / 2, 0.86, 0.94, 0.022, 0.04, 0.003)              # travessa de cima com pregos para facas
    for x in (-0.3, 0.0, 0.3):
        for dx in (-0.03, 0.03): cyl_eixo(p, 'aco', 0.0025, 0.04, 0.085, 'z', (x + dx, 0.905, 0), 8)
    img = Image.new('RGB', (512, 96), (92, 60, 40)); d = ImageDraw.Draw(img); texto_c(d, (256, 48), 'NÃO TOCAR', 56, (230, 220, 200)); mat_imagem('placa_rack', img, 0.8)
    p.box('placa_rack', -0.16, 0.16, 0.95, 0.99, 0.022, 0.024); p.uv['placa_rack'] = lambda v, n: np.stack([(v[:, 0] + 0.16) / 0.32, (v[:, 1] - 0.95) / 0.04], 1)


# ---------------------------------------------------------------------------- PRATELEIRAS
@item('prateleira_improvisada', 'Prateleira de tábuas e tijolos', 'mobilias', 'armazenamento', comodos=['abrigo', 'casas', 'garagem'],
      conteiner=True, slots=9, grade=[6, 3], saque=['comida', 'utensilios', 'materiais'], aceita=[], constroi={'tabua': 3, 'tijolo': 6}, ferramenta='nenhuma', fase=1,
      estacao='prateleira (estoque visível; comida guardada aqui não estraga com rato)',
      exibe=[{'y': round(y, 3), 'x': [-0.68, 0.68], 'z': [-0.13, 0.13]} for y in (0.08, 0.465, 0.85)])
def prateleira_improvisada(M):
    p = M.base; X = 0.75; rng = np.random.default_rng(14)
    y = 0.0
    for nivel in range(3):
        if nivel:
            for x in (-0.6, 0.0, 0.6):                                                  # pilares de 2 tijolos furados
                for k in range(2):
                    q = P(); q.cham('tijolo', -0.045, 0.045, 0.0, 0.18, -0.095, 0.095, 0.004)
                    for zz in (-0.05, 0.0, 0.05): cyl_eixo(q, 'carvao', 0.012, -0.0455, 0.0455, 'x', (0, 0.09, zz), 10)
                    p.merge(q, trimesh.transformations.translation_matrix([x + rng.uniform(-0.006, 0.006), y + k * 0.182, 0]) @ _rot(rng.uniform(-0.03, 0.03), [0, 1, 0]))
            y += 0.365
        else:
            for x in (-0.6, 0.0, 0.6): p.cham('tijolo', x - 0.095, x + 0.095, 0.0, 0.057, -0.045, 0.045, 0.004)
            y = 0.057
        for z0 in (-0.15, 0.0):
            p.cham('madeira_crua', -X + rng.uniform(0, 0.02), X - rng.uniform(0, 0.02), y, y + 0.024, z0 + 0.002, z0 + 0.148, 0.003)
        y += 0.024


@item('despensa', 'Estante de despensa com caixotes', 'mobilias', 'armazenamento', comodos=['abrigo', 'casas', 'diner', 'armazem', 'supermercado'],
      conteiner=True, slots=16, grade=[8, 4], saque=['comida', 'agua'], aceita=['comida', 'agua', 'remedios'], fase=2,
      constroi={'tabua': 10, 'caixa_pregos': 1}, ferramenta='martelo',
      estacao='despensa comunitária (a cozinha e os moradores tiram a comida daqui; mostra quantos dias de comida tem a base)',
      exibe=[{'y': round(y, 3), 'x': [-0.58, 0.58], 'z': [-0.18, 0.18]} for y in (0.12, 0.54, 0.96, 1.38)])
def despensa(M):
    p = M.base; X, Z = 0.6, 0.2; rng = np.random.default_rng(22)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira', xs * X - 0.045 * (xs > 0), xs * X + 0.045 * (xs < 0), 0.0, 1.85, zs * Z - 0.045 * (zs > 0), zs * Z + 0.045 * (zs < 0), 0.004)
        for y in (0.1, 1.82): p.cham('madeira', xs * X - 0.02 * (xs > 0), xs * X + 0.02 * (xs < 0), y - 0.06, y, -Z, Z, 0.003)
    for zs in (-1,):                                                                  # contraventamento em X atras
        p.seg('madeira', (-X + 0.04, 0.1, zs * Z + 0.01), (X - 0.04, 1.78, zs * Z + 0.01), 0.05, 0.018)
        p.seg('madeira', (X - 0.04, 0.1, zs * Z + 0.01), (-X + 0.04, 1.78, zs * Z + 0.01), 0.05, 0.018)
    rotulos = [('FEIJÃO', (150, 40, 30)), ('ARROZ', (230, 220, 190)), ('ENLATADOS', (40, 80, 140)), ('ÁGUA', (30, 120, 170)),
               ('REMÉDIOS', (200, 30, 30)), ('SEMENTES', (60, 120, 40)), ('FARINHA', (220, 200, 150)), ('VELAS', (240, 200, 60))]
    for nivel, y in enumerate((0.1, 0.52, 0.94, 1.36)):
        for k in range(4): _tab_h(p, -X, X, y, y + 0.02, -Z + k * 0.1, -Z + k * 0.1 + 0.095, 'madeira_crua')
        if nivel == 3: continue
        for c in range(2):                                                             # 2 caixotes por nivel
            idx = nivel * 2 + c; x0 = -0.56 + c * 0.58
            q = P(); w, h, d = 0.5, 0.26, 0.34
            for (a0, a1) in ((0.0, 0.08), (0.1, 0.18), (0.2, 0.26)):
                q.cham('madeira_crua', 0.0, w, a0, a1, d - 0.012, d, 0.002); q.cham('madeira_crua', 0.0, w, a0, a1, 0.0, 0.012, 0.002)
                q.cham('madeira_crua', 0.0, 0.012, a0, a1, 0.0, d, 0.002); q.cham('madeira_crua', w - 0.012, w, a0, a1, 0.0, d, 0.002)
            q.box('madeira_crua', 0.012, w - 0.012, 0.0, 0.01, 0.012, d - 0.012)
            for xx in (0.0, w - 0.03): q.cham('madeira', xx, xx + 0.03, 0.0, h, d, d + 0.012, 0.002)
            q.cham('madeira', w / 2 - 0.06, w / 2 + 0.06, 0.2, 0.225, d + 0.004, d + 0.02, 0.006)             # alca recortada
            nm = f'etiq_desp_{idx}'; mat_imagem(nm, _caixa_rotulo(rotulos[idx][0], (236, 230, 210), (40, 30, 26)), 0.85)
            q.box(nm, 0.1, w - 0.1, 0.1, 0.18, d + 0.0121, d + 0.0126); q.uv[nm] = lambda v, n, w=w: np.stack([(v[:, 0] - 0.1) / (w - 0.2), (v[:, 1] - 0.1) / 0.08], 1)
            for i in range(5):                                                         # conteudo aparecendo por cima
                cx, cz = 0.06 + (i % 3) * 0.17, 0.07 + (i // 3) * 0.16
                if idx in (2, 0): _lata_simples(q, (cx + 0.03, 0.01, cz + 0.03), 0.038, 0.11 + 0.08 * (i % 2))
                elif idx == 3: torno(q, 'pet', [(0.04, 0.01), (0.042, 0.03), (0.042, 0.26), (0.016, 0.3), (0.014, 0.32)], 18, 'y', (cx + 0.03, 0, cz + 0.03))
                else: fofo(q, 'papelao' if idx != 1 else 'colchao', cx + 0.04, 0.1, cz + 0.04, 0.06, 0.09, 0.05, 0.4, 0.3, (10, 14))
            p.merge(q, trimesh.transformations.translation_matrix([x0, y + 0.02, -Z + 0.01]) @ _rot(rng.uniform(-0.03, 0.03), [0, 1, 0]))
            p.uv.update(q.uv)
    img = Image.new('RGB', (768, 160), (236, 230, 210)); d = ImageDraw.Draw(img)
    texto_c(d, (384, 50), 'ESTOQUE · COMIDA PARA', 44, (40, 30, 26)); texto_c(d, (384, 118), '12 DIAS', 64, (150, 30, 20)); mat_imagem('placa_estoque', img, 0.85)
    p.box('placa_estoque', -0.3, 0.3, 1.74, 1.86, Z + 0.001, Z + 0.004); p.uv['placa_estoque'] = lambda v, n: np.stack([(v[:, 0] + 0.3) / 0.6, (v[:, 1] - 1.74) / 0.12], 1)


@item('estante_aramada', 'Estante aramada com rodinhas', 'mobilias', 'armazenamento', comodos=['supermercado', 'diner', 'clinica', 'abrigo', 'galeria'],
      conteiner=True, slots=10, grade=[6, 4], saque=['comida', 'limpeza', 'utensilios'], aceita=[], empurrar=True, barricada=True, fase=2,
      estacao='estoque móvel (empurra até a porta numa emergência)',
      exibe=[{'y': round(y, 3), 'x': [-0.43, 0.43], 'z': [-0.21, 0.21]} for y in (0.2, 0.62, 1.04, 1.46)])
def estante_aramada(M):
    p = M.base; X, Z = 0.45, 0.23; m = 'cromado'
    for xs in (-1, 1):
        for zs in (-1, 1):
            x, z = xs * (X - 0.012), zs * (Z - 0.012)
            p.cyl(m, 0.0125, 0.1, 1.6, x=x, z=z, sec=14)
            for y in np.arange(0.12, 1.58, 0.05): anel(p, m, 0.0124, 0.0132, y, y + 0.006, 10, 'y', (x, 0, z))
            torno(p, 'plastico_preto', [(0.014, 1.6), (0.014, 1.61), (0.01, 1.615)], 14, 'y', (x, 0, z))
            torno(p, 'plastico_cinza', [(0.018, 0.085), (0.024, 0.1)], 14, 'y', (x, 0, z))                       # rodinha com garfo
            p.cham('aco', x - 0.022, x + 0.022, 0.03, 0.085, z - 0.006, z + 0.006, 0.003)
            cyl_eixo(p, 'borracha', 0.032, x - 0.012, x + 0.012, 'x', (0, 0.032, z + 0.012), 18)
    for y in (0.2, 0.62, 1.04, 1.46):                                                   # grades de arame
        for x in np.linspace(-X + 0.025, X - 0.025, 22): cyl_eixo(p, m, 0.0022, -Z + 0.012, Z - 0.012, 'z', (x, y - 0.004, 0), 6)
        for z in np.linspace(-Z + 0.02, Z - 0.02, 6): cyl_eixo(p, m, 0.003, -X + 0.012, X - 0.012, 'x', (0, y - 0.009, z), 6)
        for zs in (-1, 1): p.cham(m, -X + 0.01, X - 0.01, y - 0.03, y, zs * (Z - 0.012) - 0.003, zs * (Z - 0.012) + 0.003, 0.0015)
        for xs in (-1, 1): p.cham(m, xs * (X - 0.012) - 0.003, xs * (X - 0.012) + 0.003, y - 0.03, y, -Z + 0.01, Z - 0.01, 0.0015)


# ---------------------------------------------------------------------------- CAIXAS COM INVENTARIO
def _ferragem_canto(p, x, y, z, sx, sy, sz, s=0.05, mat='aco_pintado'):
    p.cham(mat, min(x, x - sx * s), max(x, x - sx * s), min(y, y - sy * s), max(y, y - sy * s), z - 0.003 * sz if sz else z, z + 0.003, 0.002)


@item('bau_madeira', 'Baú de madeira com cadeado', 'mobilias', 'armazenamento', comodos=['abrigo', 'casas', 'mansao', 'fazenda', 'casa_barcos'],
      conteiner=True, slots=15, grade=[8, 5], saque=['roupas', 'ferramentas', 'moedas', 'lembrancas'], aceita=[], trancado=True, tranca='cadeado',
      barricada=True, sentar=True, fase=1, constroi={'tabua': 5, 'dobradicas': 1, 'caixa_pregos': 1}, ferramenta='martelo',
      estacao='baú pessoal (cada morador tem o seu; mexer no baú dos outros baixa a moral)')
def bau_madeira(M):
    p = M.base; X, Z, H = 0.48, 0.26, 0.42
    for y in (0.02, 0.15, 0.28):
        for zs in (-1, 1): p.cham('madeira', -X, X, y, y + 0.125, zs * Z - 0.022 * (zs > 0), zs * Z + 0.022 * (zs < 0), 0.004)
        for xs in (-1, 1): p.cham('madeira', xs * X - 0.022 * (xs > 0), xs * X + 0.022 * (xs < 0), y, y + 0.125, -Z + 0.02, Z - 0.02, 0.004)
    p.box('madeira', -X + 0.02, X - 0.02, 0.02, 0.04, -Z + 0.02, Z - 0.02)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_escura', xs * X - 0.03 * (xs > 0), xs * X + 0.03 * (xs < 0), 0.0, 0.03, zs * Z - 0.03 * (zs > 0), zs * Z + 0.03 * (zs < 0), 0.004)
    for x in (-X + 0.12, X - 0.12):                                                     # cintas de ferro com rebites
        p.cham('aco_pintado', x - 0.022, x + 0.022, 0.02, H, Z, Z + 0.004, 0.001); p.cham('aco_pintado', x - 0.022, x + 0.022, 0.02, H, -Z - 0.004, -Z, 0.001)
        for y in np.linspace(0.06, H - 0.04, 5): torno(p, 'aco', [(0.005, 0), (0.004, 0.003)], 10, 'z', (x, y, Z + 0.004))
    for xs in (-1, 1):                                                                  # alcas laterais
        varrer(p, 'aco', circ(0.006, 8), [(xs * (X + 0.005), 0.3, -0.06), (xs * (X + 0.04), 0.27, -0.05), (xs * (X + 0.04), 0.27, 0.05), (xs * (X + 0.005), 0.3, 0.06)])
        for zz in (-0.06, 0.06): p.cham('aco', xs * X - 0.004 * (xs > 0), xs * X + 0.004 * (xs < 0), 0.28, 0.32, zz - 0.02, zz + 0.02, 0.002)
    p.cham('aco_pintado', -0.035, 0.035, H - 0.08, H - 0.01, Z, Z + 0.008, 0.002)                 # trinco
    anel(p, 'aco', 0.006, 0.011, Z + 0.008, Z + 0.025, 12, 'z', (0, H - 0.04, 0))
    p.cham('latao', -0.022, 0.022, H - 0.13, H - 0.08, Z + 0.015, Z + 0.035, 0.005)                      # cadeado
    varrer(p, 'aco_polido', circ(0.0032, 8), [(-0.013, H - 0.08, Z + 0.025), (-0.013, H - 0.045, Z + 0.025), (0.013, H - 0.045, Z + 0.025), (0.013, H - 0.08, Z + 0.025)])
    q = M.parte('tampa', (0, H, -Z - 0.01), 'tampa', eixo='x', abre_graus=-100)                  # tampa abaulada
    for k in range(7):
        a0, a1 = -math.pi / 2 + k * math.pi / 7, -math.pi / 2 + (k + 1) * math.pi / 7
        z0, z1 = Z * math.sin(a0) * 1.04, Z * math.sin(a1) * 1.04; y0, y1 = 0.08 * math.cos(a0), 0.08 * math.cos(a1)
        q.hull('madeira', [(x, y, z) for x in (-X - 0.01, X + 0.01) for (y, z) in ((y0, z0), (y1, z1), (y0 - 0.018, z0 * 0.93), (y1 - 0.018, z1 * 0.93))])
    for x in (-X + 0.12, X - 0.12):
        pts = [(x, 0.08 * math.cos(a) + 0.003, Z * math.sin(a) * 1.05) for a in np.linspace(-math.pi / 2, math.pi / 2, 16)]
        for a, b in zip(pts[:-1], pts[1:]): q.seg('aco_pintado', a, b, 0.044, 0.004)
    q.cham('aco_pintado', -0.03, 0.03, -0.05, 0.0, Z + 0.004, Z + 0.012, 0.002)                     # aldrava
    for x in (-0.3, 0.3): cyl_eixo(p, 'aco', 0.008, x - 0.05, x + 0.05, 'x', (0, H, -Z - 0.01), 12)       # dobradicas
    _mover(q, (0, H, 0))


@item('caixa_militar', 'Caixote militar verde', 'mobilias', 'armazenamento', comodos=['quartel', 'delegacia', 'abrigo', 'armazem', 'estacao'],
      conteiner=True, slots=10, grade=[6, 4], saque=['municao', 'remedios', 'ferramentas', 'comida'], aceita=[], empilhavel=True, altura_m=0.38,
      carregar=2, barricada=True, fase=2, estacao='caixa de suprimentos (2 moradores carregam; empilha em 3)')
def caixa_militar(M):
    p = M.base; X, Z, H = 0.45, 0.24, 0.3
    p.cham('verde_caixa', -X, X, 0.0, H, -Z, Z, 0.008)
    for xs in (-1, 1): p.cham('verde_caixa', xs * X - 0.03 * (xs > 0), xs * X + 0.03 * (xs < 0), 0.0, H, -Z - 0.012, Z + 0.012, 0.006)   # cabeceiras
    for zs in (-1, 1):
        for y in (0.06, H - 0.06): p.cham('verde_caixa', -X + 0.03, X - 0.03, y - 0.018, y + 0.018, zs * Z - 0.012 * (zs < 0), zs * Z + 0.012 * (zs > 0), 0.004)  # sarrafos
    img = Image.new('RGB', (1024, 256), (18, 34, 14)); d = ImageDraw.Draw(img)
    texto_c(d, (512, 80), 'SUPRIMENTOS · DEFESA CIVIL', 64, (210, 200, 150), larg=980); texto_c(d, (512, 180), 'LOTE 07-B   ·   34 kg', 52, (210, 200, 150))
    mat_imagem('estencil_militar', img, 0.8)
    p.box('estencil_militar', -X + 0.06, X - 0.06, 0.09, H - 0.09, Z + 0.0005, Z + 0.001); p.uv['estencil_militar'] = lambda v, n: np.stack([(v[:, 0] + X - 0.06) / (2 * X - 0.12), (v[:, 1] - 0.09) / (H - 0.18)], 1)
    for xs in (-1, 1):                                                                  # alcas de corda
        for zz in (-0.08, 0.08): p.cham('verde_caixa', xs * (X + 0.012) - 0.004, xs * (X + 0.012) + 0.004, 0.2, 0.24, zz - 0.015, zz + 0.015, 0.002)
        _torcido(p, 'corda', [(xs * (X + 0.016), 0.22, -0.08), (xs * (X + 0.04), 0.2, -0.05), (xs * (X + 0.045), 0.195, 0.0), (xs * (X + 0.04), 0.2, 0.05), (xs * (X + 0.016), 0.22, 0.08)], 0.008)
        for zs in (-1, 1): p.cham('aco_pintado', xs * (X + 0.01) - 0.012, xs * (X + 0.01) + 0.012, 0.12, 0.18, zs * (Z + 0.012) - 0.004, zs * (Z + 0.012) + 0.004, 0.002)  # fecho
    q = M.parte('tampa', (0, H, -Z), 'tampa', eixo='x', abre_graus=-105)
    q.cham('verde_caixa', -X, X, 0.0, 0.08, 0.0, 2 * Z, 0.008)
    for x in (-X + 0.15, 0.0, X - 0.15): q.cham('verde_caixa', x - 0.03, x + 0.03, 0.08, 0.1, 0.02, 2 * Z - 0.02, 0.004)
    _mover(q, (0, H, -Z))


@item('caixa_organizadora', 'Caixa organizadora empilhável', 'mobilias', 'armazenamento', comodos=['casas', 'abrigo', 'garagem', 'escolinha', 'galeria'],
      conteiner=True, slots=6, grade=[4, 3], saque=['utensilios', 'roupas', 'higiene', 'pilhas'], aceita=[], empilhavel=True, altura_m=0.31,
      portatil=True, peso_kg=1.6, fase=1, estacao='caixa de estoque (empilha em 4; tampa travada não deixa a água entrar)')
def caixa_organizadora(M):
    p = M.base; X0, Z0, X1, Z1, H = 0.27, 0.19, 0.3, 0.215, 0.29
    perfil = lambda y: (X0 + (X1 - X0) * y / H, Z0 + (Z1 - Z0) * y / H)
    pts_o = [(sx * perfil(y)[0], y, sz * perfil(y)[1]) for y in (0.0, H) for sx in (-1, 1) for sz in (-1, 1)]
    o = trimesh.convex.convex_hull(np.array(pts_o)); i_ = trimesh.convex.convex_hull(np.array([(sx * (perfil(y)[0] - 0.004), y + 0.006 if y == 0 else y + 0.01, sz * (perfil(y)[1] - 0.004)) for y in (0.0, H) for sx in (-1, 1) for sz in (-1, 1)]))
    corpo = o.difference(i_); p.add('plastico_azul_cx', corpo)
    for xs in (-1, 1):
        for k in range(4): p.hull('plastico_azul_cx', [(xs * (X0 + 0.003 + (X1 - X0) * y / H), y, z) for y in (0.03, H - 0.04) for z in (-0.12 + k * 0.08 - 0.008, -0.12 + k * 0.08 + 0.008)])  # nervuras
    p.cham('plastico_azul_cx', -X1 - 0.008, X1 + 0.008, H - 0.02, H, -Z1 - 0.008, Z1 + 0.008, 0.004)                  # aba de apoio
    q = M.parte('tampa', (0, H, 0), 'tampa', eixo='x', abre_graus=0, remover=True)
    q.cham('tampa_cinza', -X1 - 0.01, X1 + 0.01, 0.0, 0.02, -Z1 - 0.01, Z1 + 0.01, 0.006)
    q.cham('tampa_cinza', -X0 + 0.02, X0 - 0.02, 0.02, 0.026, -Z0 + 0.02, Z0 - 0.02, 0.004)                           # rebaixo de encaixe
    for xs in (-1, 1):                                                                   # travas
        q.cham('plastico_branco', xs * (X1 + 0.004) - 0.01, xs * (X1 + 0.004) + 0.01, -0.035, 0.012, -0.05, 0.05, 0.003)
    _mover(q, (0, H, 0))
    img = Image.new('RGB', (384, 160), (250, 250, 250)); d = ImageDraw.Draw(img)
    texto_c(d, (192, 50), 'PILHAS / LUZ', 44, (20, 20, 20)); d.line([(30, 100), (354, 100)], fill=(20, 20, 20), width=3); texto_c(d, (192, 130), 'não abrir à noite', 26, (120, 20, 20), False)
    mat_imagem('fita_crepe_cx', img, 0.85)
    p.box('fita_crepe_cx', -0.12, 0.12, 0.15, 0.25, Z1 * 0.5 + Z0 * 0.5 + 0.005, Z1 * 0.5 + Z0 * 0.5 + 0.0055)
    p.uv['fita_crepe_cx'] = lambda v, n: np.stack([(v[:, 0] + 0.12) / 0.24, (v[:, 1] - 0.15) / 0.1], 1)


@item('caixa_ferramentas', 'Caixa de ferramentas de metal', 'mobilias', 'armazenamento', comodos=['garagem', 'oficina', 'abrigo', 'posto', 'serraria'],
      conteiner=True, slots=6, grade=[4, 2], saque=['ferramentas', 'materiais'], aceita=['ferramentas', 'materiais', 'armas'], portatil=True, peso_kg=4.0,
      fase=1, estacao='caixa de ferramentas (leva junto as ferramentas para consertar barricadas fora da base)')
def caixa_ferramentas(M):
    p = M.base; X, Z, H = 0.25, 0.11, 0.17
    p.cham('tinta_vermelha', -X, X, 0.0, H, -Z, Z, 0.005)
    p.box('aco', -X + 0.004, X - 0.004, 0.004, H + 0.0005, -Z + 0.004, Z - 0.004)
    for zs in (-1, 1): p.cham('tinta_vermelha', -X - 0.002, X + 0.002, H - 0.012, H, zs * Z - 0.002 * (zs < 0), zs * Z + 0.002 * (zs > 0), 0.002)
    for xs in (-1, 1): p.cham('aco_polido', xs * 0.15 - 0.02, xs * 0.15 + 0.02, H - 0.05, H - 0.01, Z, Z + 0.008, 0.002)   # fechos
    for x in np.linspace(-X + 0.05, X - 0.05, 5): p.cham('tinta_vermelha', x - 0.012, x + 0.012, 0.02, H - 0.03, -Z - 0.002, -Z, 0.001)
    q = M.parte('tampa', (0, H, -Z), 'tampa', eixo='x', abre_graus=-110)
    q.hull('tinta_vermelha', [(x, y, z) for x in (-X, X) for (y, z) in ((0.0, 0.0), (0.0, 2 * Z), (0.045, 0.03), (0.045, 2 * Z - 0.03))])
    for x in (-0.08, 0.08): q.cham('aco', x - 0.012, x + 0.012, 0.04, 0.06, Z - 0.012, Z + 0.012, 0.003)
    varrer(q, 'plastico_preto', circ(0.011, 12), [(-0.08, 0.055, Z), (-0.07, 0.09, Z), (0.07, 0.09, Z), (0.08, 0.055, Z)])     # alca
    _mover(q, (0, H, -Z))
    for k, (x, c) in enumerate(((-0.17, 'madeira'), (-0.05, 'tinta_amarela'), (0.1, 'plastico_preto'))):
        p.cham(c, x - 0.02, x + 0.05, H - 0.04, H + 0.008, -0.05 + 0.03 * k, -0.03 + 0.03 * k, 0.005)            # cabos aparecendo


# ---------------------------------------------------------------------------- PALETES E PILHAS DE MATERIAL
def _base_pallet(p, X=0.6, Z=0.4):
    for z in np.linspace(-Z + 0.05, Z - 0.05, 5): p.cham('madeira_crua', -X, X, 0.122, 0.144, z - 0.05, z + 0.05, 0.003)
    for x in (-X + 0.05, 0.0, X - 0.05):
        p.cham('madeira_crua', x - 0.05, x + 0.05, 0.0, 0.022, -Z, Z, 0.003)
        for z in (-Z + 0.05, 0.0, Z - 0.05): p.cham('madeira_crua', x - 0.05, x + 0.05, 0.022, 0.122, z - 0.05, z + 0.05, 0.003)
    for x in (-X + 0.05, 0.0, X - 0.05):
        for z in np.linspace(-Z + 0.05, Z - 0.05, 5): torno(p, 'aco', [(0.005, 0), (0.004, 0.0015)], 8, 'y', (x, 0.144, z))
    return 0.144


def _cinta(p, x, y0, y1, Z, mat='fita_cinta'):
    for zs in (-1, 1): p.box(mat, x - 0.008, x + 0.008, y0, y1, zs * Z - 0.0012 * (zs < 0), zs * Z + 0.0012 * (zs > 0))
    p.box(mat, x - 0.008, x + 0.008, y1, y1 + 0.0012, -Z - 0.0012, Z + 0.0012)
    p.cham('aco_polido', x - 0.012, x + 0.012, y1 - 0.0, y1 + 0.004, Z * 0.4 - 0.015, Z * 0.4 + 0.015, 0.001)


def _pallet_camadas(M, n, alt, fazer, unidades, base=True):
    y = _base_pallet(M.base) if base else 0.0
    for k in range(n):
        q = M.parte(f'camada_{k + 1}', (0, y + k * alt, 0), 'camada', ordem=n - k, unidades=unidades)
        fazer(q, k, y + k * alt); _mover(q, (0, y + k * alt, 0))
    return y + n * alt


@item('pallet_tabuas', 'Pallet de tábuas cintadas', 'mobilias', 'armazenamento', comodos=['armazem', 'serraria', 'abrigo', 'fabrica'],
      estoque={'item': 'tabua', 'max': 48}, desmontavel='48 tábuas + 4 madeira', barricada=False, fase=2,
      estacao='estoque de madeira da obra (construções tiram daqui; a camada de cima some quando acaba)')
def pallet_tabuas(M):
    rng = np.random.default_rng(31)
    def camada(q, k, y):
        for i in range(8):
            z = -0.36 + i * 0.103; L = 1.5 - rng.uniform(0, 0.04)
            q.cham('madeira_crua', -L / 2, L / 2, 0.0, 0.0245, z - 0.049, z + 0.049, 0.002)
            for x in rng.uniform(-0.6, 0.6, 2): torno(q, 'madeira_escura', [(0.008, 0.0), (0.011, 0.0004)], 10, 'y', (x, 0.0245, z + rng.uniform(-0.02, 0.02)))
    top = _pallet_camadas(M, 6, 0.025, camada, 8)
    for x in (-0.55, 0.0, 0.55): _cinta(M.base, x, 0.144, top, 0.42)
    img = Image.new('RGB', (384, 192), (236, 230, 210)); d = ImageDraw.Draw(img)
    texto_c(d, (192, 50), 'PINUS 2,5×10', 44, (40, 30, 26)); texto_c(d, (192, 120), '48 pç · 1,50 m', 40, (40, 30, 26)); mat_imagem('etiq_tabuas', img, 0.85)
    M.base.box('etiq_tabuas', -0.2, -0.05, 0.16, 0.235, 0.4275, 0.428); M.base.uv['etiq_tabuas'] = lambda v, n: np.stack([(v[:, 0] + 0.2) / 0.15, (v[:, 1] - 0.16) / 0.075], 1)


@item('pallet_tijolos', 'Pallet de tijolos', 'mobilias', 'armazenamento', comodos=['armazem', 'fabrica', 'abrigo', 'ruinas'],
      estoque={'item': 'tijolo', 'max': 120}, fase=2, estacao='estoque de tijolos (fogão, forno, forja e muros)')
def pallet_tijolos(M):
    def camada(q, k, y):
        for i in range(6):                                                              # 6 x 4 tijolos deitados por camada, amarracao alternada
            for j in range(4):
                if k % 2 == 0: x, z, sx, sz = -0.5 + i * 0.2, -0.3 + j * 0.2, 0.095, 0.045
                else: x, z, sx, sz = -0.45 + i * 0.18, -0.3 + j * 0.2, 0.045, 0.095
                if k % 2 == 1 and i == 5: continue
                q.cham('tijolo', x - sx, x + sx, 0.0, 0.056, z - sz, z + sz, 0.004)
    top = _pallet_camadas(M, 5, 0.057, camada, 24)
    for x in (-0.3, 0.3): _cinta(M.base, x, 0.144, top, 0.4)


@item('pallet_cimento', 'Pallet de sacos de cimento', 'mobilias', 'armazenamento', comodos=['armazem', 'fabrica', 'garagem_vertical'],
      estoque={'item': 'cimento', 'max': 20}, fase=4, estacao='estoque de cimento (muralha, cisterna e reformas da fase Vila)')
def pallet_cimento(M):
    rng = np.random.default_rng(41); _mat_cimento()
    def camada(q, k, y):
        for i in range(4):
            if k % 2 == 0: x, z, a = (-0.3 if i < 2 else 0.3), (-0.2 if i % 2 == 0 else 0.2), 0.0
            else: x, z, a = (-0.3 if i < 2 else 0.3), (-0.2 if i % 2 == 0 else 0.2), 0.0
            fofo(q, 'rot_cimento', x + rng.uniform(-0.01, 0.01), 0.055, z, 0.29, 0.055, 0.19, 0.2, 0.08, (12, 20)); _amassar(q, 'rot_cimento', 0.002, 30.0, k * 4 + i, sub=0)
            f = uv_atlas(-0.3, 0.3, 0.0, 0.11, -0.2, 0.2, frente='y')                       # um rotulo por saco
            q.uv['rot_cimento'] = lambda v, n, f=f: f(np.stack([(v[:, 0] + 0.6) % 0.6 - 0.3, v[:, 1], (v[:, 2] + 0.4) % 0.4 - 0.2], 1), n)
    _pallet_camadas(M, 5, 0.105, camada, 4)


@item('pallet_sucata', 'Pallet de sucata separada', 'mobilias', 'armazenamento', comodos=['ferrovelho', 'garagem', 'abrigo', 'posto'],
      estoque={'item': 'sucata_metal', 'max': 60}, fase=2, estacao='estoque de sucata (chapas embaixo, peças miúdas no caixote)')
def pallet_sucata(M):
    y = _base_pallet(M.base)
    def camada(q, k, y):
        if k < 3:                                                                          # chapas onduladas
            L, Wd, a = 1.15, 0.78, 0.008; xs = np.linspace(-Wd / 2, Wd / 2, 41)
            top = [(x, a + a * math.cos(x * 2 * math.pi / 0.076)) for x in xs]; pts = top + [(x, yy - 0.0015) for x, yy in top[::-1]]
            m = trimesh.creation.extrude_polygon(Polygon(pts).buffer(0), L); m.vertices = np.stack([m.vertices[:, 2] - L / 2, m.vertices[:, 1] + 0.0015, m.vertices[:, 0]], 1)
            if m.volume < 0: m.invert()
            m.apply_transform(_rot(0.02 * (k - 1), [0, 1, 0])); q.add('ferrugem' if k != 1 else 'galvanizado', m)
        else:                                                                              # caixote de pecas miudas por cima
            carcaca(q, 'madeira_crua', -0.35, 0.35, 0.0, 0.25, -0.25, 0.25, t=0.02, topo=False, fundo=True)
            q.box('madeira_crua', -0.33, 0.33, 0.0, 0.02, -0.25, 0.0)
            q.box('madeira_crua', -0.35, 0.35, 0.0, 0.25, 0.23, 0.25)
            rng = np.random.default_rng(5)
            for i in range(14):
                c = (rng.uniform(-0.28, 0.28), rng.uniform(0.17, 0.24), rng.uniform(-0.18, 0.18))
                if i % 3 == 0: _porca(q, c, 0.012, 0.009)
                elif i % 3 == 1: q.seg('ferrugem', c, (c[0] + rng.uniform(-0.1, 0.1), c[1] + 0.01, c[2] + rng.uniform(-0.1, 0.1)), 0.012, 0.012)
                else: _engrenagem(q, c, 0.03, 14, 0.008, 'aco', 0.3)
            img = Image.new('RGB', (384, 128), (184, 150, 106)); d = ImageDraw.Draw(img); texto_c(d, (192, 64), 'PEÇAS', 72, (30, 20, 16)); mat_imagem('estencil_pecas', img, 0.9)
            q.box('estencil_pecas', -0.15, 0.15, 0.06, 0.16, 0.2501, 0.2506); q.uv['estencil_pecas'] = lambda v, n: np.stack([(v[:, 0] + 0.15) / 0.3, (v[:, 1] - 0.06) / 0.1], 1)
    for k in range(4):
        q = M.parte(f'camada_{k + 1}', (0, y + k * 0.018, 0), 'camada', ordem=4 - k, unidades=15)
        camada(q, k, y); _mover(q, (0, y + k * 0.018, 0))


@item('pallet_sacos_areia', 'Pilha de sacos de areia no pallet', 'mobilias', 'armazenamento', comodos=['quartel', 'abrigo', 'estacao', 'armazem'],
      estoque={'item': 'saco_areia', 'max': 18}, fase=2, estacao='estoque de sacos de areia (trincheiras e paredes de defesa)')
def pallet_sacos_areia(M):
    def camada(q, k, y):
        for i in range(6):
            if k % 2 == 0: x, z, rot = -0.3 + (i % 2) * 0.6, -0.27 + (i // 2) * 0.27, 0.0
            else: x, z, rot = -0.4 + (i % 3) * 0.4, -0.2 + (i // 3) * 0.4, math.pi / 2
            s = P(); fofo(s, 'lona', 0, 0.065, 0, 0.29, 0.065, 0.14 if k % 2 == 0 else 0.13, 0.35, 0.2, (12, 22)); _amassar(s, 'lona', 0.004, 25.0, k * 7 + i, sub=0)
            fofo(s, 'lona', 0.28, 0.05, 0.0, 0.03, 0.035, 0.1, 0.5, 0.4, (8, 10))
            q.merge(s, trimesh.transformations.translation_matrix([x, 0, z]) @ _rot(rot, [0, 1, 0]) @ _rot(0.05 * ((i + k) % 3 - 1), [0, 1, 0]))
    _pallet_camadas(M, 3, 0.115, camada, 6)


@item('lenheiro', 'Lenheiro coberto', 'mobilias', 'armazenamento', comodos=['abrigo', 'casa_de_campo', 'fazenda', 'casas'],
      estoque={'item': 'lenha', 'max': 30}, constroi={'tabua': 6, 'chapa_metal': 2, 'caixa_pregos': 1}, ferramenta='martelo', fase=1,
      estacao='lenheiro (lenha guardada seca queima o dobro; chuva estraga a lenha do chão)')
def lenheiro(M):
    p = M.base; X, Z, H = 0.8, 0.3, 1.5; rng = np.random.default_rng(51)
    for xs in (-1, 1):
        for zs, h in ((-1, H), (1, H - 0.15)): p.cham('madeira_escura', xs * X - 0.045 * (xs > 0), xs * X + 0.045 * (xs < 0), 0.0, h, zs * Z - 0.045 * (zs > 0), zs * Z + 0.045 * (zs < 0), 0.004)
        p.seg('madeira_escura', (xs * (X - 0.02), 0.2, -Z + 0.02), (xs * (X - 0.02), 1.0, Z - 0.02), 0.04, 0.03)        # mao-francesa lateral
    for z in (-Z + 0.06, 0.0, Z - 0.06): _tab_h(p, -X, X, 0.1, 0.125, z - 0.05, z + 0.05, 'madeira_escura')         # estrado
    for x in (-X + 0.05, 0.0, X - 0.05): p.cham('madeira_escura', x - 0.04, x + 0.04, 0.0, 0.1, -Z, Z, 0.004)
    for zs, h in ((-1, H), (1, H - 0.15)): p.cham('madeira_escura', -X - 0.05, X + 0.05, h - 0.06, h, zs * Z - 0.04 * (zs > 0), zs * Z + 0.04 * (zs < 0), 0.004)
    ang = math.atan2(0.15, 2 * Z + 0.2)                                                                 # telhado de chapa caindo para a frente
    L, Wd, a = 2 * Z + 0.3, 2 * X + 0.2, 0.009; xs_ = np.linspace(-Wd / 2, Wd / 2, 61)
    top = [(x, a + a * math.cos(x * 2 * math.pi / 0.076)) for x in xs_]; pts = top + [(x, yy - 0.0015) for x, yy in top[::-1]]
    m = trimesh.creation.extrude_polygon(Polygon(pts).buffer(0), L); m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 1], m.vertices[:, 2] - L / 2], 1)
    if m.volume < 0: m.invert()
    m.apply_transform(_rot(ang, [1, 0, 0])); m.apply_translation([0, H - 0.075, 0.0]); p.add('telha_ondulada', m)
    def camada(q, k, y):                                                                                 # toras rachadas empilhadas
        for i in range(9):
            for j in range(2):
                x = -X + 0.12 + i * 0.17 + rng.uniform(-0.01, 0.01); z0 = -Z + 0.03 + j * 0.29
                r = rng.uniform(0.05, 0.065); yy = 0.06
                pts_ = [(r * math.cos(t), r * math.sin(t)) for t in np.linspace(0, 2 * math.pi * (0.5 if (i + j + k) % 3 == 0 else 1.0), 12)]
                poly = Polygon(pts_ + ([(0, 0)] if (i + j + k) % 3 == 0 else [])).buffer(0)
                giro = rng.uniform(0, 6.3)
                mm = trimesh.creation.extrude_polygon(poly, 0.27); mm.apply_transform(_rot(giro, [0, 0, 1])); mm.apply_translation([x, yy, z0])
                q.add('madeira_lenha', mm)
                for e in (z0, z0 + 0.27):                                                  # topos claros (madeira cortada)
                    tt = trimesh.creation.extrude_polygon(poly.buffer(-0.004), 0.002); tt.apply_transform(_rot(giro, [0, 0, 1])); tt.apply_translation([x, yy, e - 0.001]); q.add('madeira_crua', tt)
    for k in range(4):
        q = M.parte(f'camada_{k + 1}', (0, 0.125 + k * 0.115, 0), 'camada', ordem=4 - k, unidades=8 if k < 3 else 6)
        camada(q, k, 0); _mover(q, (0, 0.125 + k * 0.115, 0))
