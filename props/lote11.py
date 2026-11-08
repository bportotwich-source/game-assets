# Lote 11: itens unicos de trabalho (oficina, garagem, concessionaria, fabrica, serraria, fazenda, armazem, ferro-velho, caixa d'agua).
# Executado por gerar_props.py (mesmas funcoes e materiais).
CORES.update({'amarelo_maquina': (150, 100, 6), 'verde_maquina': (20, 52, 30), 'laranja_seg': (170, 50, 4), 'feno': (170, 130, 50),
              'graxa': (16, 14, 12), 'tela_galinheiro': (120, 122, 118), 'palha': (190, 150, 70), 'azul_racao': (14, 34, 90),
              'calota': (200, 202, 206), 'pano_espantalho': (70, 46, 30), 'xadrez': (110, 20, 16), 'chapa_galv': (150, 156, 160)})
METALICOS.update({'amarelo_maquina': (0.35, 0.45), 'verde_maquina': (0.35, 0.5), 'laranja_seg': (0.3, 0.5), 'graxa': (0.4, 0.6),
                  'tela_galinheiro': (0.7, 0.5), 'calota': (0.9, 0.22), 'chapa_galv': (0.8, 0.38)})
FOSCOS.update({'feno': 0.95, 'palha': 0.95, 'azul_racao': 0.85, 'pano_espantalho': 0.95, 'xadrez': 0.95})
TEX_PROPRIAS += [('feno', 'tecido', 0.3, 512), ('xadrez', 'tecido', 0.3, 512), ('pano_espantalho', 'tecido', 0.25, 512)]

_rx = lambda ang, c=(0, 0, 0): trimesh.transformations.rotation_matrix(ang, [1, 0, 0], point=c)
_ry = lambda ang, c=(0, 0, 0): trimesh.transformations.rotation_matrix(ang, [0, 1, 0], point=c)
_tr = lambda x, y, z: trimesh.transformations.translation_matrix([x, y, z])


# ---------------------------------------------------------------------------- OFICINA / GARAGEM / CONCESSIONARIA
@item('elevador_automotivo', 'Elevador automotivo de duas colunas', 'mobilias', 'oficina', comodos=['garagem', 'posto', 'concessionaria', 'ferro_velho'],
      ambiente=True, colisao='caixa', obstaculo=True, modulo_m=4.0, usa='energia', observacao='sem energia fica travado no alto: bom esconderijo')
def elevador_automotivo(M):
    p = M.base; X = 1.55
    for xs in (-1, 1):
        x = xs * X
        p.cham('aco', x - 0.25, x + 0.25, 0.0, 0.02, -0.3, 0.3, 0.005)                       # base aparafusada
        for dx in (-0.18, 0.18):
            for dz in (-0.22, 0.22): p.cyl('aco_polido', 0.012, 0.02, 0.035, x=x + dx, z=dz, sec=6)
        p.cham('amarelo_maquina', x - 0.14, x + 0.14, 0.02, 3.1, -0.16, 0.16, 0.01)          # coluna
        p.box('graxa', x - 0.1, x + 0.1, 0.1, 3.0, -0.165, -0.155) if False else None
        p.box('esmalte_escuro', x - xs * 0.14 - 0.005, x - xs * 0.14 + 0.005, 0.2, 2.9, -0.06, 0.06)   # trilho interno
        p.cham('aco_pintado', x - 0.2, x + 0.2, 1.1, 1.35, -0.2, 0.2, 0.01)                 # carro do braco
        for zs in (-1, 1):                                                                 # bracos articulados
            a = p.seg('aco_pintado', (x - xs * 0.05, 1.22, zs * 0.12), (x - xs * 0.75, 1.2, zs * 0.85), 0.11, 0.07)
            p.cyl('borracha', 0.06, 1.24, 1.29, x=x - xs * 0.75, z=zs * 0.85, sec=14); p.cyl('aco', 0.03, 1.2, 1.24, x=x - xs * 0.75, z=zs * 0.85, sec=10)
        for k in range(18): p.box('esmalte_escuro', x - xs * 0.15, x - xs * 0.135, 0.3 + k * 0.14, 0.34 + k * 0.14, 0.04, 0.08)   # cremalheira das travas
    p.cham('amarelo_maquina', -X - 0.14, X + 0.14, 3.1, 3.22, -0.12, 0.12, 0.01)            # travessa superior
    p.cham('aco_pintado', X + 0.14, X + 0.36, 1.0, 1.4, -0.12, 0.12, 0.012)                 # unidade hidraulica
    p.cyl('esmalte_escuro', 0.08, 1.4, 1.7, x=X + 0.25, z=0.0, sec=16)
    p.cham('tinta_vermelha', X + 0.18, X + 0.26, 1.2, 1.3, 0.12, 0.14, 0.004)               # botao
    p.seg('borracha', (X + 0.2, 1.68, 0.0), (X + 0.1, 3.16, 0.0), 0.02)                     # mangueira hidraulica
    p.seg('borracha', (-X - 0.1, 3.16, 0.0), (-X - 0.1, 1.4, 0.05), 0.02)
    p.cham('graxa', -0.6, 0.4, 0.0, 0.002, -0.4, 0.3, 0.001)                               # mancha de oleo


@item('carrinho_ferramentas', 'Carrinho de ferramentas com gavetas', 'mobilias', 'oficina', comodos=['garagem', 'posto', 'concessionaria', 'fabrica', 'quartel'],
      conteiner=True, slots=4, saque=['ferramentas', 'materiais'], colisao='caixa', barricada=True)
def carrinho_ferramentas(M):
    p = M.base; X, Z0, Z1, H = 0.36, -0.23, 0.23, 0.98
    carcaca(p, 'tinta_vermelha', -X, X, 0.12, H, Z0, Z1, t=0.015)
    p.cham('borracha', -X - 0.01, X + 0.01, H, H + 0.015, Z0 - 0.01, Z1 + 0.01, 0.004)     # tapete do tampo
    for xs in (-1, 1): puxador_barra(p, 'cromo', xs * (X + 0.05), 0.3, 0.9, 0.0, afast=0.04, eixo='z') if False else p.seg('cromo', (xs * X, 0.8, Z0 + 0.03), (xs * (X + 0.06), 0.8, Z0 + 0.03), 0.02)
    p.seg('cromo', (-X - 0.06, 0.8, Z0 + 0.03), (-X - 0.06, 0.8, Z1 - 0.03), 0.022); p.seg('cromo', (-X, 0.8, Z1 - 0.03), (-X - 0.06, 0.8, Z1 - 0.03), 0.02)
    for xs in (-1, 1):
        for zs in (-1, 1):
            x, z = xs * (X - 0.05), zs * (Z1 - 0.05)
            p.cham('aco', x - 0.03, x + 0.03, 0.105, 0.12, z - 0.03, z + 0.03, 0.003); p.box('aco', x - 0.006, x + 0.006, 0.075, 0.105, z - 0.02, z + 0.02)
            _roda(p, (x, 0.05, z), 0.05, 0.035, 'x', mat_aro='aco')
    alt = [0.07, 0.07, 0.09, 0.12, 0.18, 0.21]; y = H - 0.02
    for j, h in enumerate(alt):
        y0 = y - h; q = M.parte(f'gaveta_{j + 1}', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.32]) if j in (0, 2, 4) else p
        q.cham('tinta_vermelha', -X + 0.01, X - 0.01, y0 + 0.004, y - 0.004, Z1 - 0.012, Z1 + 0.005, 0.003)
        q.box('cromo', -X + 0.05, X - 0.05, y - 0.03, y - 0.018, Z1 + 0.005, Z1 + 0.02)
        if q is not p:
            q.box('aco', -X + 0.03, X - 0.03, y0 + 0.01, y0 + 0.016, Z0 + 0.03, Z1 - 0.012)
            for i in range(5): q.seg('aco_polido', (-X + 0.08 + i * 0.12, y0 + 0.025, Z0 + 0.08), (-X + 0.08 + i * 0.12 + 0.03, y0 + 0.025, Z1 - 0.06), 0.018, 0.012)
        y = y0
    p.cham('aco_polido', -0.2, 0.05, H + 0.015, H + 0.03, -0.1, -0.06, 0.004); p.cyl('borracha', 0.016, H + 0.015, H + 0.03, x=0.05, z=-0.08, sec=10) if False else None
    p.seg('aco_polido', (-0.25, H + 0.03, 0.05), (0.05, H + 0.03, 0.12), 0.02, 0.008); p.cham('borracha', 0.05, 0.16, H + 0.02, H + 0.042, 0.1, 0.15, 0.006)


@item('compressor_ar', 'Compressor de ar com tanque', 'mobilias', 'oficina', comodos=['garagem', 'posto', 'fabrica', 'ferro_velho'], ambiente=True, colisao='caixa',
      usa='energia', barulho='alto', desmonta={'sucata': 4, 'peca_motor': 1})
def compressor_ar(M):
    p = M.base
    torno(p, 'tinta_vermelha', [(0.0, -0.6), (0.12, -0.59), (0.2, -0.55), (0.22, -0.5), (0.22, 0.5), (0.2, 0.55), (0.12, 0.59), (0.0, 0.6)], 32, 'x', (0, 0.32, 0))
    for xs in (-0.4, 0.4):
        p.seg('aco_pintado', (xs, 0.13, -0.2), (xs, 0.13, 0.2), 0.04, 0.03)
        p.seg('aco_pintado', (xs, 0.13, -0.18), (xs, 0.25, -0.12), 0.03); p.seg('aco_pintado', (xs, 0.13, 0.18), (xs, 0.25, 0.12), 0.03)
    _roda(p, (-0.42, 0.11, 0.24), 0.11, 0.05, 'z', mat_aro='aco'); _roda(p, (-0.42, 0.11, -0.24), 0.11, 0.05, 'z', mat_aro='aco')
    p.cham('borracha', 0.36, 0.44, 0.0, 0.13, -0.18, 0.18, 0.01)
    p.cham('esmalte_escuro', -0.3, 0.1, 0.53, 0.58, -0.15, 0.15, 0.01)                     # base do motor
    cyl_eixo(p, 'aco_pintado', 0.1, -0.28, 0.0, 'x', (0, 0.68, 0.0), 20)                    # motor
    for k in range(8): cyl_eixo(p, 'aco_pintado', 0.105, -0.27 + k * 0.03, -0.26 + k * 0.03, 'x', (0, 0.68, 0.0), 20)
    p.cham('aco', 0.05, 0.2, 0.58, 0.72, -0.08, 0.08, 0.01)                                 # cabecote
    for k in range(6): p.box('aco', 0.06, 0.19, 0.72 + k * 0.016, 0.728 + k * 0.016, -0.09, 0.09)   # aletas
    torno(p, 'tela_galinheiro', [(0.13, -0.04), (0.13, 0.04)], 24, 'z', (0.02, 0.68, 0.12), fechar=False)   # grade da polia
    cyl_eixo(p, 'aco_polido', 0.012, 0.12, 0.42, 'x', (0, 0.76, 0.0), 8); p.cyl('aco_polido', 0.012, 0.52, 0.76, x=0.42, z=0.0, sec=8)
    torno(p, 'esmalte', [(0.04, 0.0), (0.04, 0.012)], 20, 'z', (0.3, 0.6, 0.2)); torno(p, 'vidro_escuro', [(0.035, 0.012), (0.035, 0.014)], 20, 'z', (0.3, 0.6, 0.2))
    p.cyl('aco_polido', 0.01, 0.32, 0.42, x=0.3, z=0.17, sec=8)
    pts = [(0.5, 0.35, 0.15), (0.6, 0.3, 0.3), (0.55, 0.05, 0.45), (0.2, 0.02, 0.5), (-0.1, 0.02, 0.42), (-0.15, 0.03, 0.25)]
    for a, b in zip(pts[:-1], pts[1:]): p.seg('laranja_seg', a, b, 0.016)


@item('painel_ferramentas', 'Painel de ferramentas na parede', 'mobilias', 'oficina', montagem='wall', altura_sugerida_m=1.1,
      comodos=['garagem', 'oficina', 'fabrica', 'serraria', 'armazem', 'fazenda'], conteiner=True, slots=3, saque=['ferramentas'], colisao='nenhuma')
def painel_ferramentas(M):
    p = M.base; X, H = 0.9, 0.9
    p.cham('madeira_crua', -X, X, 0.0, H, 0.0, 0.018, 0.004)
    for i in range(1, 30):
        for j in range(1, 14): p.box('esmalte_escuro', -X + i * 0.06 - 0.004, -X + i * 0.06 + 0.004, j * 0.064 - 0.004, j * 0.064 + 0.004, 0.018, 0.0185)
    def contorno(x0, x1, y0, y1): p.box('tinta_vermelha', x0, x1, y0, y1, 0.0185, 0.019)
    # martelo
    contorno(-0.78, -0.72, 0.25, 0.7); p.cham('madeira', -0.765, -0.735, 0.27, 0.6, 0.02, 0.04, 0.006); p.cham('aco', -0.81, -0.69, 0.6, 0.66, 0.02, 0.05, 0.006)
    # serrote
    hull_pts = [(-0.62, 0.75, 0.02), (-0.62, 0.75, 0.023), (-0.6, 0.25, 0.02), (-0.6, 0.25, 0.023), (-0.5, 0.25, 0.02), (-0.5, 0.25, 0.023), (-0.52, 0.65, 0.02), (-0.52, 0.65, 0.023)]
    p.hull('aco_polido', hull_pts); p.cham('madeira', -0.64, -0.5, 0.65, 0.8, 0.018, 0.04, 0.01)
    # chaves combinadas
    for k in range(7):
        x = -0.36 + k * 0.055; L = 0.16 + k * 0.025; p.cham('tela_galinheiro', x - 0.004, x + 0.004, 0.76, 0.8, 0.018, 0.05, 0.002)
        p.cham('aco_polido', x - 0.01, x + 0.01, 0.72 - L, 0.72, 0.022, 0.03, 0.003); p.cyl('aco_polido', 0.017, 0.715, 0.73, x=x, z=0.026, sec=10) if False else p.cham('aco_polido', x - 0.017, x + 0.017, 0.7, 0.74, 0.022, 0.03, 0.006)
    # chaves de fenda
    for k in range(5):
        x = 0.1 + k * 0.06; p.cham('tela_galinheiro', x - 0.02, x + 0.02, 0.72, 0.74, 0.018, 0.06, 0.002)
        p.cyl(['tinta_amarela', 'tinta_vermelha', 'plastico_preto'][k % 3], 0.015, 0.6, 0.72, x=x, z=0.05, sec=10); p.cyl('aco_polido', 0.004, 0.42 - k * 0.02, 0.6, x=x, z=0.05, sec=6)
    # alicates
    for k in range(2):
        x = 0.48 + k * 0.12
        for s in (-1, 1): p.seg('tinta_vermelha', (x, 0.62, 0.03), (x + s * 0.035, 0.38, 0.03), 0.02, 0.012)
        p.seg('aco', (x - 0.012, 0.62, 0.03), (x + 0.012, 0.72, 0.03), 0.025, 0.012); p.cham('tela_galinheiro', x - 0.004, x + 0.004, 0.62, 0.64, 0.018, 0.05, 0.002)
    contorno(0.72, 0.84, 0.3, 0.75)                                                          # contorno vazio: a ferramenta sumiu
    p.cham('madeira_crua', -X, X, 0.06, 0.08, 0.018, 0.2, 0.004)                             # prateleira
    for x in np.linspace(-0.7, 0.4, 6): torno(p, ['lata', 'tinta_azul', 'lata'][int(x * 10) % 3], [(0.04, 0.08), (0.04, 0.17), (0.035, 0.175)], 16, 'y', (x, 0, 0.12))


@item('macaco_jacare', 'Macaco jacaré', 'loot', 'ferramentas', recurso='ferramenta', valor=4, peso_kg=12, empilha=1, onde=['garagem', 'posto', 'concessionaria', 'ferro_velho'],
      efeito='ergue carro e escombros (passagem bloqueada) e serve de barricada pesada', pega=[-0.45, 0.25, 0])
def macaco_jacare(M):
    p = M.base
    for zs in (-1, 1):
        p.cham('tinta_vermelha', -0.25, 0.25, 0.03, 0.12, zs * 0.1 - 0.012, zs * 0.1 + 0.012, 0.004)
        p.seg('tinta_vermelha', (-0.15, 0.1, zs * 0.08), (0.2, 0.24, zs * 0.08), 0.05, 0.012)
    p.cham('tinta_vermelha', -0.22, 0.25, 0.1, 0.12, -0.1, 0.1, 0.004)
    for x, z in ((-0.2, -0.12), (-0.2, 0.12)): _roda(p, (x, 0.04, z), 0.04, 0.025, 'z', mat_aro='aco')
    for x, z in ((0.22, -0.12), (0.22, 0.12)): _roda(p, (x, 0.03, z), 0.03, 0.02, 'z', mat_aro='aco')
    torno(p, 'aco', [(0.0, 0.0), (0.055, 0.0), (0.06, 0.012), (0.045, 0.02)], 20, 'y', (0.21, 0.24, 0.0))
    p.cyl('aco_pintado', 0.03, 0.08, 0.2, x=-0.05, z=0.0, sec=14)
    p.seg('aco', (-0.24, 0.1, 0.0), (-0.85, 0.32, 0.0), 0.03); p.seg('borracha', (-0.75, 0.29, 0.0), (-0.88, 0.33, 0.0), 0.04)


@item('totem_ofertas', 'Totem de ofertas da concessionária', 'mobilias', 'concessionaria', comodos=['concessionaria', 'posto', 'rua'], ambiente=True,
      colisao='caixa', pista='"0 km, sai hoje!"; anúncio da última semana antes do fim')
def totem_ofertas(M):
    p = M.base
    img = Image.new('RGB', (512, 1024), (250, 250, 246)); d = ImageDraw.Draw(img); d.rectangle([0, 0, 512, 220], fill=(170, 20, 20))
    texto_c(d, (256, 80), 'OFERTA', 90, (255, 255, 255)); texto_c(d, (256, 170), 'DA SEMANA', 56, (255, 230, 120))
    texto_c(d, (256, 330), 'SEDÃ 0 KM', 64, (30, 30, 30)); texto_c(d, (256, 470), 'ENTRADA', 54, (60, 60, 60)); texto_c(d, (256, 560), 'ZERO', 110, (170, 20, 20))
    texto_c(d, (256, 720), '60x sem juros', 54, (30, 30, 30)); d.rectangle([40, 820, 472, 960], fill=(250, 200, 40)); texto_c(d, (256, 890), 'SAI HOJE!', 76, (30, 30, 30))
    mat_imagem('totem_arte', img, 0.5)
    p.cham('aco_pintado', -0.35, 0.35, 0.0, 0.08, -0.25, 0.25, 0.02)
    p.cham('esmalte', -0.3, 0.3, 0.08, 1.85, -0.06, 0.06, 0.015)
    for zs in (-1, 1):
        p.box('totem_arte', -0.27, 0.27, 0.15, 1.8, *sorted((zs * 0.06, zs * 0.062)))
    p.uv['totem_arte'] = lambda v, n: np.stack([(v[:, 0] * np.sign(v[:, 2] + 1e-9) + 0.27) / 0.54, (v[:, 1] - 0.15) / 1.65], 1)
    for k in range(6): p.seg(['tinta_vermelha', 'tinta_amarela', 'tinta_azul'][k % 3], (0, 1.85, 0), (-0.9 + k * 0.36, 1.6 - abs(k - 2.5) * 0.05, 0.0), 0.004) if False else None
    for k in range(9):                                                                     # bandeirolas
        x = -0.3 + k * 0.075; p.hull(['tinta_vermelha', 'tinta_amarela', 'tinta_azul'][k % 3], [(x, 1.85, 0.0), (x + 0.07, 1.85, 0.0), (x + 0.035, 1.75, 0.0), (x, 1.85, 0.002), (x + 0.07, 1.85, 0.002), (x + 0.035, 1.75, 0.002)])
    p.seg('corda', (-0.3, 1.85, 0.001), (0.37, 1.85, 0.001), 0.006) if 'corda' in CORES else p.seg('plastico_branco', (-0.3, 1.85, 0.001), (0.37, 1.85, 0.001), 0.006)


# ---------------------------------------------------------------------------- FABRICA
@item('torno_mecanico', 'Torno mecânico', 'mobilias', 'fabrica', comodos=['fabrica', 'garagem', 'serraria'], ambiente=True, colisao='caixa', obstaculo=True,
      usa='energia', estacao='oficina avançada (peças de motor e armas melhores)', desmonta={'sucata': 10, 'peca_motor': 2})
def torno_mecanico(M):
    p = M.base; L = 0.95
    for x in (-L + 0.15, L - 0.2):
        p.cham('verde_maquina', x - 0.18, x + 0.18, 0.0, 0.85, -0.25, 0.25, 0.02)             # pedestais
        p.cham('esmalte_escuro', x - 0.2, x + 0.2, 0.0, 0.05, -0.27, 0.27, 0.01)
    p.cham('verde_maquina', -L, L, 0.75, 0.85, -0.32, 0.32, 0.01)                             # bandeja de cavaco
    p.box('graxa', -L + 0.05, L - 0.05, 0.85, 0.852, -0.3, 0.3)
    p.cham('verde_maquina', -L + 0.05, L - 0.05, 0.85, 1.0, -0.15, 0.08, 0.01)               # barramento
    p.cham('aco_polido', -L + 0.05, L - 0.05, 1.0, 1.02, -0.14, -0.1, 0.004); p.cham('aco_polido', -L + 0.05, L - 0.05, 1.0, 1.02, 0.04, 0.08, 0.004)
    cyl_eixo(p, 'aco_polido', 0.015, -L + 0.1, L - 0.1, 'x', (0, 0.9, 0.12), 10); cyl_eixo(p, 'aco_polido', 0.012, -L + 0.1, L - 0.1, 'x', (0, 0.82, 0.12), 10)
    p.cham('verde_maquina', -L, -L + 0.45, 0.85, 1.45, -0.25, 0.2, 0.02)                     # cabecote
    for k in range(3):
        for j in range(2): cyl_eixo(p, 'esmalte_escuro', 0.008, 0.2, 0.25, 'z', (-L + 0.08 + k * 0.12, 1.1 + j * 0.18, 0), 6); p.sphere('esmalte_escuro', 0.02, -L + 0.08 + k * 0.12, 1.1 + j * 0.18, 0.26)
    cyl_eixo(p, 'aco', 0.1, -L + 0.45, -L + 0.55, 'x', (0, 1.17, -0.03), 24)                  # placa
    for a in (0, 2.09, 4.19): p.cham('aco_polido', -L + 0.55, -L + 0.6, 1.17 + 0.06 * math.sin(a) - 0.015, 1.17 + 0.06 * math.sin(a) + 0.015, -0.03 + 0.06 * math.cos(a) - 0.015, -0.03 + 0.06 * math.cos(a) + 0.015, 0.003)
    cyl_eixo(p, 'aco_polido', 0.025, -L + 0.55, 0.15, 'x', (0, 1.17, -0.03), 14)             # peca presa
    p.cham('verde_maquina', 0.1, 0.4, 1.0, 1.08, -0.18, 0.12, 0.01); p.cham('verde_maquina', 0.15, 0.35, 1.08, 1.15, -0.12, 0.08, 0.01)   # carro
    p.cham('aco', 0.2, 0.3, 1.15, 1.22, -0.1, 0.02, 0.006); p.cham('aco_polido', 0.23, 0.27, 1.16, 1.19, -0.16, -0.06, 0.003)
    for x, z in ((0.25, 0.18), (0.32, 0.12)): cyl_eixo(p, 'aco_polido', 0.008, 0.12, 0.25, 'z', (x, 1.04, 0), 6); torno(p, 'aco', [(0.04, 0.0), (0.04, 0.012)], 16, 'z', (x, 1.04, 0.25))
    p.cham('verde_maquina', L - 0.35, L - 0.1, 1.0, 1.22, -0.12, 0.06, 0.01)                 # contraponta
    cyl_eixo(p, 'aco_polido', 0.022, L - 0.55, L - 0.35, 'x', (0, 1.17, -0.03), 12)
    torno(p, 'aco', [(0.0, 0.0), (0.06, 0.0), (0.06, 0.015)], 16, 'x', (L - 0.1, 1.17, -0.03))
    p.seg('esmalte_escuro', (-L + 0.2, 1.45, 0.0), (-L + 0.2, 1.75, 0.15), 0.012); p.cham('esmalte_escuro', -L + 0.12, -L + 0.28, 1.72, 1.82, 0.1, 0.22, 0.01)   # luminaria
    p.cham('tinta_vermelha', -L + 0.2, -L + 0.3, 0.95, 1.0, 0.2, 0.23, 0.004)


@item('esteira_rolante', 'Esteira de roletes', 'mobilias', 'fabrica', comodos=['fabrica', 'armazem', 'correios', 'supermercado'], ambiente=True,
      colisao='caixa', modulo_m=2.0, desmonta={'sucata': 6})
def esteira_rolante(M):
    p = M.base; X, Z = 1.0, 0.3
    for zs in (-1, 1):
        p.cham('amarelo_maquina', -X, X, 0.7, 0.82, zs * Z - 0.02, zs * Z + 0.02, 0.006)
        for x in (-X + 0.1, X - 0.1):
            p.cham('aco_pintado', x - 0.025, x + 0.025, 0.0, 0.72, zs * (Z - 0.02) - 0.025, zs * (Z - 0.02) + 0.025, 0.004)
            p.cham('borracha', x - 0.04, x + 0.04, 0.0, 0.015, zs * (Z - 0.02) - 0.04, zs * (Z - 0.02) + 0.04, 0.004)
    for x in (-X + 0.1, X - 0.1): p.seg('aco_pintado', (x, 0.25, -Z + 0.02), (x, 0.25, Z - 0.02), 0.03, 0.03)
    for k in range(25): cyl_eixo(p, 'aco_polido', 0.024, -Z + 0.02, Z - 0.02, 'z', (-X + 0.04 + k * 0.08, 0.79, 0), 12)
    rng = np.random.default_rng(71)
    for x, w, h in ((-0.6, 0.38, 0.26), (0.15, 0.3, 0.22)):
        c = P(); c.cham('papelao', -w / 2, w / 2, 0.0, h, -w / 2 * 0.8, w / 2 * 0.8, 0.006); c.box('fita_prata', -w / 2, w / 2, h, h + 0.001, -0.025, 0.025)
        p.merge(c, _tr(x, 0.815, 0) @ _ry(rng.uniform(-0.2, 0.2)))


@item('relogio_ponto', 'Relógio de ponto com cartões', 'mobilias', 'fabrica', montagem='wall', altura_sugerida_m=1.2, comodos=['fabrica', 'armazem', 'serraria', 'correios', 'quartel'],
      ambiente=True, colisao='nenhuma', pista='os cartões mostram quem bateu o ponto no último dia (nomes de sobreviventes)')
def relogio_ponto(M):
    p = M.base
    p.cham('verde_maquina', -0.15, 0.15, 0.0, 0.42, 0.0, 0.2, 0.02); p.cham('aco_polido', -0.13, 0.13, 0.25, 0.4, 0.2, 0.205, 0.004)
    img = Image.new('RGB', (256, 256), (244, 240, 228)); d = ImageDraw.Draw(img)
    for h in range(12): a = h / 12 * 2 * math.pi; d.line([(128 + 100 * math.sin(a), 128 - 100 * math.cos(a)), (128 + 118 * math.sin(a), 128 - 118 * math.cos(a))], fill=(20, 20, 20), width=8)
    mat_imagem('mostrador_ponto', img, 0.4)
    torno(p, 'mostrador_ponto', [(0.065, 0.0), (0.065, 0.002)], 32, 'z', (0, 0.325, 0.205))
    p.uv['mostrador_ponto'] = lambda v, n: np.stack([(v[:, 0] + 0.065) / 0.13, (v[:, 1] - 0.26) / 0.13], 1)
    p.seg('esmalte_escuro', (0, 0.325, 0.21), (0.03, 0.355, 0.21), 0.006, 0.002); p.seg('esmalte_escuro', (0, 0.325, 0.21), (-0.045, 0.31, 0.21), 0.004, 0.002)
    p.cham('esmalte_escuro', -0.05, 0.05, 0.12, 0.14, 0.14, 0.22, 0.004)                     # fenda do cartao
    p.cham('aco', 0.13, 0.2, 0.08, 0.13, 0.08, 0.18, 0.01)                                  # alavanca
    for xs in (-1, 1):                                                                    # porta-cartoes dos dois lados
        x0 = xs * 0.3
        p.cham('aco_pintado', x0 - 0.18, x0 + 0.18, -0.25, 0.55, 0.0, 0.03, 0.006)
        for j in range(8):
            y = -0.22 + j * 0.095; p.box('aco', x0 - 0.17, x0 + 0.17, y, y + 0.01, 0.03, 0.06)
            for i in range(5):
                if (i + j * 3 + xs) % 4 == 0: continue
                p.box('papel' if 'papel' in CORES else 'plastico_branco', x0 - 0.16 + i * 0.066, x0 - 0.11 + i * 0.066, y + 0.005, y + 0.1, 0.04, 0.042)


@item('paleteira', 'Paleteira manual', 'mobilias', 'armazem', comodos=['armazem', 'fabrica', 'supermercado', 'correios', 'serraria'], ambiente=True,
      colisao='caixa', interacao='arrasta pallets e móveis pesados (monta barricadas mais rápido)', desmonta={'sucata': 5})
def paleteira(M):
    p = M.base
    for xs in (-1, 1):
        x = xs * 0.18
        p.cham('amarelo_maquina', x - 0.08, x + 0.08, 0.045, 0.085, -0.65, 0.5, 0.006)
        p.box('amarelo_maquina', x - 0.08, x - 0.074, 0.02, 0.045, -0.65, 0.5); p.box('amarelo_maquina', x + 0.074, x + 0.08, 0.02, 0.045, -0.65, 0.5)
        cyl_eixo(p, 'borracha', 0.035, x - 0.04, x + 0.04, 'x', (0, 0.035, -0.6), 14)         # roletes da ponta
        p.hull('amarelo_maquina', [(x - 0.08, 0.02, -0.65), (x + 0.08, 0.02, -0.65), (x - 0.08, 0.085, -0.65), (x + 0.08, 0.085, -0.65), (x - 0.06, 0.04, -0.72), (x + 0.06, 0.04, -0.72), (x - 0.06, 0.07, -0.72), (x + 0.06, 0.07, -0.72)])
    p.cham('amarelo_maquina', -0.27, 0.27, 0.02, 0.2, 0.5, 0.62, 0.01)                      # corpo
    p.cyl('aco_polido', 0.04, 0.2, 0.42, x=0.0, z=0.6, sec=16); p.cyl('amarelo_maquina', 0.05, 0.42, 0.48, x=0.0, z=0.6, sec=16)
    for xs in (-1, 1): _roda(p, (xs * 0.08, 0.08, 0.62), 0.08, 0.05, 'x', mat_aro='aco')
    p.seg('amarelo_maquina', (0.0, 0.48, 0.6), (0.0, 1.15, 0.85), 0.04)                      # timao
    p.hull('borracha', [(-0.16, 1.15, 0.84), (0.16, 1.15, 0.84), (-0.16, 1.2, 0.86), (0.16, 1.2, 0.86), (-0.14, 1.35, 0.92), (0.14, 1.35, 0.92), (-0.14, 1.3, 0.9), (0.14, 1.3, 0.9)])
    p.seg('aco_polido', (0.0, 1.2, 0.86), (0.08, 1.25, 0.84), 0.015)


# ---------------------------------------------------------------------------- SERRARIA
@item('pilha_tabuas', 'Pilha de tábuas da serraria', 'mobilias', 'serraria', comodos=['serraria', 'armazem', 'fazenda', 'deposito'], ambiente=True, colisao='caixa',
      coleta={'recurso': 'tabua', 'total': 12, 'ferramenta': 'nenhuma', 'segundos_por_unidade': 3}, barricada=True)
def pilha_tabuas(M):
    p = M.base; rng = np.random.default_rng(73); L = 1.2
    for x in (-0.9, 0.0, 0.9): p.cham('madeira_escura', -0.55 + x * 0 - 0.55 + 0.55, 0.55, 0.0, 0.08, -0.04, 0.04, 0.006) if False else p.cham('madeira_escura', -0.55, 0.55, 0.0, 0.08, x - 0.04, x + 0.04, 0.006)
    y = 0.08
    for camada in range(7):
        n = 4; larg = 0.24
        for i in range(n):
            if camada == 6 and i in (1, 3): continue
            x = -0.48 + i * 0.26 + rng.uniform(-0.01, 0.01); dz = rng.uniform(-0.06, 0.06)
            p.cham('madeira_crua', x, x + larg, y, y + 0.045, -L + dz, L + dz, 0.004)
        y += 0.045
        if camada in (2, 5):
            for z in (-0.9, 0.0, 0.9): p.cham('madeira_escura', -0.52, 0.52, y, y + 0.025, z - 0.02, z + 0.02, 0.004)
            y += 0.025
    for z in (-0.9, 0.9): p.box('fita_preta' if 'fita_preta' in CORES else 'aco', -0.53, 0.53, y, y + 0.002, z - 0.012, z + 0.012)


@item('pilha_toras', 'Pilha de toras', 'mobilias', 'serraria', comodos=['serraria', 'fazenda', 'casa_de_campo', 'rua'], ambiente=True, colisao='caixa', obstaculo=True,
      coleta={'recurso': 'lenha', 'total': 10, 'ferramenta': 'machado', 'segundos_por_unidade': 8}, barulho='médio (machado)')
def pilha_toras(M):
    p = M.base; rng = np.random.default_rng(74); L = 1.4
    linhas = [(5, 0.17), (4, 0.16), (3, 0.15)]; y = 0.0
    for j, (n, r) in enumerate(linhas):
        for i in range(n):
            x = (i - (n - 1) / 2) * 0.34; rr = r * rng.uniform(0.9, 1.08); yy = r + j * 0.29
            dz = rng.uniform(-0.12, 0.12); _tora(p, (x, yy, -L + dz), (x, yy, L + dz), rr)
    for xs in (-1, 1): p.seg('madeira_escura', (xs * 0.95, 0.0, -0.8), (xs * 0.88, 0.75, -0.8), 0.07); p.seg('madeira_escura', (xs * 0.95, 0.0, 0.8), (xs * 0.88, 0.75, 0.8), 0.07)


@item('cavalete_serra', 'Cavalete de serrar lenha', 'mobilias', 'serraria', comodos=['serraria', 'fazenda', 'casa_de_campo', 'abrigo', 'quintal'], colisao='caixa',
      estacao='lenha (corta toras em lenha mais rápido)', constroi={'tabua': 3, 'caixa_pregos': 1})
def cavalete_serra(M):
    p = M.base
    for z in (-0.35, 0.35):
        for s in (-1, 1): p.seg('madeira_crua', (s * 0.32, 0.0, z), (-s * 0.06, 0.85, z), 0.06, 0.04)
    p.seg('madeira_crua', (0.0, 0.42, -0.4), (0.0, 0.42, 0.4), 0.05, 0.04)
    for z in (-0.35, 0.35): p.seg('madeira_crua', (-0.17, 0.42, z), (0.17, 0.42, z), 0.03, 0.02)
    _tora(p, (0.0, 0.79, -0.7), (0.0, 0.79, 0.65), 0.11)
    p.add('madeira_crua', trimesh.creation.cylinder(radius=0.1, segment=[(0.0, 0.79, 0.68), (0.0, 0.79, 0.7)], sections=14)) if False else None
    p.hull('aco_polido', [(0.0, 0.83, 0.5), (0.0, 0.83, 0.502), (0.0, 1.02, 0.55), (0.0, 1.02, 0.552), (0.55, 1.12, 0.55), (0.55, 1.12, 0.552), (0.55, 1.0, 0.5), (0.55, 1.0, 0.502)])
    p.cham('madeira', 0.53, 0.68, 0.98, 1.16, 0.49, 0.56, 0.012)
    for k in range(14): p.box('madeira_crua', -0.12 + k * 0.03, -0.1 + k * 0.03, 0.0, 0.004, 0.45, 0.6)   # serragem
    for k in range(4): p.box('madeira_crua', -0.3 + k * 0.17, -0.28 + k * 0.17, 0.0, 0.006, -0.2 + k * 0.05, -0.1 + k * 0.05)


@item('serra_fita', 'Serra de fita industrial', 'mobilias', 'serraria', comodos=['serraria', 'fabrica'], ambiente=True, colisao='caixa', obstaculo=True,
      usa='energia', barulho='muito alto', estacao='serraria (toras viram tábuas)', desmonta={'sucata': 12, 'peca_motor': 1})
def serra_fita(M):
    p = M.base; H = 2.1
    p.cham('verde_maquina', -0.35, 0.35, 0.0, 0.08, -0.4, 0.4, 0.02)
    p.cham('verde_maquina', -0.12, 0.12, 0.08, H, -0.38, -0.18, 0.02)                        # coluna
    for yc in (0.45, H - 0.35):
        torno(p, 'verde_maquina', [(0.0, -0.08), (0.34, -0.08), (0.36, -0.06), (0.36, 0.06), (0.34, 0.08), (0.0, 0.08)], 40, 'z', (0, yc, 0.0))
    for y0, y1 in ((0.1, 0.85), (H - 0.75, H)): p.cham('verde_maquina', -0.38, 0.38, y0, y1, -0.1, -0.08, 0.02) if False else None
    p.box('aco_polido', 0.34, 0.352, 0.45, H - 0.35, -0.003, 0.003); p.box('aco_polido', -0.352, -0.34, 0.45, H - 0.35, -0.003, 0.003)   # fita
    p.cham('aco_polido', -0.5, 0.5, 0.95, 1.0, -0.45, 0.45, 0.006)                           # mesa
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('verde_maquina', xs * 0.42 - 0.03, xs * 0.42 + 0.03, 0.08, 0.95, zs * 0.38 - 0.03, zs * 0.38 + 0.03, 0.005)
    p.cham('verde_maquina', 0.3, 0.4, 1.0, 1.5, -0.04, 0.04, 0.006); p.cham('amarelo_maquina', 0.3, 0.42, 1.0, 1.4, 0.04, 0.06, 0.004)   # guia
    p.cham('amarelo_maquina', -0.5, -0.46, 1.0, 1.06, -0.45, 0.45, 0.004)                    # guia de corte
    cyl_eixo(p, 'aco_pintado', 0.12, -0.4, -0.1, 'z', (-0.25, 0.3, 0), 20)                   # motor
    p.cham('tinta_vermelha', -0.15, -0.05, 1.2, 1.3, -0.2, -0.17, 0.006); p.cham('esmalte', -0.14, -0.06, 1.22, 1.28, -0.17, -0.165, 0.003)
    p.cham('madeira_crua', -0.2, 0.45, 1.0, 1.08, 0.1, 0.4, 0.008)                           # tabua no meio do corte
    for k in range(18): p.box('madeira_crua', -0.4 + k * 0.045, -0.385 + k * 0.045, 0.0, 0.005, 0.3 + (k % 3) * 0.05, 0.42 + (k % 3) * 0.05)


# ---------------------------------------------------------------------------- FAZENDA
@item('fardo_feno', 'Fardo de feno', 'mobilias', 'fazenda', comodos=['fazenda', 'armazem', 'celeiro', 'rua'], colisao='caixa', barricada=True, sentar=True,
      coleta={'recurso': 'palha', 'total': 4, 'ferramenta': 'nenhuma', 'segundos_por_unidade': 3}, observacao='queima rápido: bom para fogueira de sinal')
def fardo_feno(M):
    p = M.base
    fofo(p, 'feno', 0.0, 0.2, 0.0, 0.45, 0.2, 0.25, e1=0.18, e2=0.18)
    for x in (-0.22, 0.22):
        anel(p, 'corda' if 'corda' in CORES else 'papelao', 0.0, 0.0, 0, 0, 4) if False else None
        p.box('lona' if 'lona' in CORES else 'papelao', x - 0.008, x + 0.008, 0.0, 0.405, -0.252, -0.248); p.box('lona', x - 0.008, x + 0.008, 0.0, 0.405, 0.248, 0.252)
        p.box('lona', x - 0.008, x + 0.008, 0.402, 0.406, -0.25, 0.25)
    rng = np.random.default_rng(75)
    for k in range(40):
        a = np.array([rng.uniform(-0.45, 0.45), rng.uniform(0.02, 0.4), rng.choice([-0.255, 0.255])]); b = a + [rng.uniform(-0.05, 0.05), rng.uniform(-0.06, 0.02), rng.uniform(-0.02, 0.02) + np.sign(a[2]) * 0.03]
        p.seg('palha', tuple(a), tuple(b), 0.004, 0.002)


@item('cocho', 'Cocho de água para animais', 'mobilias', 'fazenda', comodos=['fazenda', 'celeiro', 'quintal'], colisao='caixa', barricada=True,
      coleta={'recurso': 'agua', 'total': 8, 'ferramenta': 'balde ou garrafa (ferver antes!)', 'segundos_por_unidade': 4}, observacao='água parada: suja, só fervida')
def cocho(M):
    p = M.base; X, Z = 0.9, 0.35
    perfil = [(0.0, 0.08), (0.25, 0.1), (0.32, 0.2), (0.35, 0.55), (0.33, 0.55), (0.3, 0.22), (0.23, 0.12), (0.0, 0.1)]
    poly = Polygon([(z, y) for z, y in perfil] + [(-z, y) for z, y in perfil[::-1]]).buffer(0)
    m = trimesh.creation.extrude_polygon(poly, 2 * X); m.vertices = np.stack([m.vertices[:, 2] - X, m.vertices[:, 1], m.vertices[:, 0]], 1)
    if m.volume < 0: m.invert()
    p.add('chapa_galv', m)
    for xs in (-1, 1):
        prof = Polygon([(z, y) for z, y in perfil[:4]] + [(-z, y) for z, y in perfil[:4][::-1]]).buffer(0)
        e = trimesh.creation.extrude_polygon(prof, 0.01); e.vertices = np.stack([e.vertices[:, 2] + xs * X - (0.01 if xs > 0 else 0), e.vertices[:, 1], e.vertices[:, 0]], 1)
        if e.volume < 0: e.invert()
        p.add('chapa_galv', e)
        p.cham('aco_pintado', xs * (X - 0.15) - 0.03, xs * (X - 0.15) + 0.03, 0.0, 0.1, -0.3, 0.3, 0.005)
    for x in (-X, X): anel(p, 'chapa_galv', 0.0, 0.0, 0, 0, 4) if False else None
    p.box('agua_suja' if 'agua_suja' in CORES else 'vidro_escuro', -X + 0.01, X - 0.01, 0.42, 0.425, -0.32, 0.32)
    for x in np.linspace(-0.7, 0.7, 5): p.box('folha_verde', x - 0.05, x + 0.04, 0.426, 0.428, -0.1 + (x % 0.2), 0.0 + (x % 0.2))


@item('galinheiro', 'Galinheiro de tela', 'mobilias', 'fazenda', comodos=['fazenda', 'quintal', 'abrigo'], colisao='caixa', modulo_m=2.0,
      constroi={'tabua': 6, 'arame_farpado': 0, 'chapa_metal': 2, 'caixa_pregos': 1}, estacao='criação (ovos: 1 comida por dia se tiver ração)',
      partes_obs='portinhola abre')
def galinheiro(M):
    p = M.base; X, Z, H = 0.95, 0.7, 1.4
    for x in (-X, 0.0, X):
        for z in (-Z, Z): p.cham('madeira_crua', x - 0.035, x + 0.035, 0.0, H, z - 0.035, z + 0.035, 0.005)
    for y in (0.05, H - 0.05):
        for z in (-Z, Z): p.cham('madeira_crua', -X, X, y - 0.03, y + 0.03, z - 0.025, z + 0.025, 0.004)
        for x in (-X, X): p.cham('madeira_crua', x - 0.025, x + 0.025, y - 0.03, y + 0.03, -Z, Z, 0.004)
    for k in range(5):                                                                     # telhado de chapa
        c = P(); _chapa_ondulada(c, 0.5, 0.5, 'chapa_galv')
        p.merge(c, _tr(-X + 0.2 + k * 0.4 - 0.25 + 0.25, H + 0.05, -Z - 0.1) @ _rx(-math.pi / 2 + 0.12) @ _tr(0, 0, 0)) if False else None
    tel = P()
    for k in range(4):
        x0 = -X - 0.1 + k * 0.53; tel.cham('chapa_galv', x0, x0 + 0.55, H + 0.03, H + 0.05, -Z - 0.15, Z + 0.15, 0.004)
        for z in np.linspace(-Z - 0.15, Z + 0.15, 22): tel.box('chapa_galv', x0, x0 + 0.55, H + 0.05, H + 0.06, z - 0.012, z + 0.012)
    p.merge(tel, _rx(0.08, (0, H, 0)))
    for z in (-Z, Z):                                                                     # tela hexagonal (fios)
        for y in np.linspace(0.12, H - 0.1, 14): p.box('tela_galinheiro', -X, X, y - 0.0015, y + 0.0015, z - 0.0015, z + 0.0015)
        for x in np.linspace(-X, X, 30): p.box('tela_galinheiro', x - 0.0015, x + 0.0015, 0.08, H - 0.08, z - 0.0015, z + 0.0015)
    for y in np.linspace(0.12, H - 0.1, 14): p.box('tela_galinheiro', X - 0.0015, X + 0.0015, y - 0.0015, y + 0.0015, -Z, Z)
    p.cham('madeira', -X + 0.05, -0.1, 0.0, 0.75, -Z + 0.05, Z - 0.05, 0.01)                 # casinha dos ninhos
    p.cham('madeira_escura', -X + 0.03, -0.08, 0.75, 0.8, -Z + 0.03, Z - 0.03, 0.006)
    for k in range(3):
        z = -Z + 0.25 + k * 0.45; p.cham('palha', -0.15, -0.09, 0.35, 0.45, z - 0.15, z + 0.15, 0.03) if False else p.cham('esmalte_escuro', -0.11, -0.095, 0.4, 0.6, z - 0.1, z + 0.1, 0.01)
    p.seg('madeira_crua', (-0.1, 0.4, 0.0), (0.5, 0.02, 0.0), 0.12, 0.02)                    # rampa
    for k in range(5): p.box('madeira_escura', 0.0 + k * 0.1, 0.1 + k * 0.1, 0.33 - k * 0.063, 0.345 - k * 0.063, -0.06, 0.06)
    for k in range(30): p.box('palha', -0.0 + (k % 6) * 0.15 - 0.4, (k % 6) * 0.15 - 0.36, 0.0, 0.004, -0.6 + (k // 6) * 0.25, -0.56 + (k // 6) * 0.25)
    q = M.parte('portinhola', (X, 0, 0.0), 'porta', eixo='y', abre_graus=-100)
    q.cham('madeira_crua', X - 0.02, X + 0.02, 0.1, 1.1, 0.02, 0.6, 0.004) if False else None
    for y in (0.15, 1.05): q.cham('madeira_crua', X + 0.01, X + 0.04, y - 0.025, y + 0.025, 0.02, 0.62, 0.004)
    for z in (0.02, 0.62): q.cham('madeira_crua', X + 0.01, X + 0.04, 0.12, 1.08, z - 0.0, z + 0.04, 0.004)
    for y in np.linspace(0.18, 1.02, 10): q.box('tela_galinheiro', X + 0.024, X + 0.027, y - 0.0015, y + 0.0015, 0.04, 0.62)
    for z in np.linspace(0.05, 0.6, 9): q.box('tela_galinheiro', X + 0.024, X + 0.027, 0.15, 1.05, z - 0.0015, z + 0.0015)


@item('carrinho_mao', 'Carrinho de mão', 'mobilias', 'fazenda', comodos=['fazenda', 'quintal', 'serraria', 'armazem', 'abrigo', 'rua'], colisao='caixa',
      conteiner=True, slots=4, saque=['materiais', 'ferramentas'], interacao='leva 4 espaços extras de recursos (anda devagar)', desmonta={'sucata': 3})
def carrinho_mao(M):
    p = M.base
    cacamba = Polygon([(-0.32, 0.0), (0.32, 0.0), (0.45, 0.28), (-0.4, 0.28)])
    def faces(t):
        out = P()
        bot = trimesh.creation.box(extents=[0.64, 0.004, 0.42]); bot.apply_translation([0, 0.002, 0]); out.add('tinta_verde', bot)
        for zs in (-1, 1):
            s = trimesh.creation.extrude_polygon(cacamba, 0.004); s.vertices[:, 2] += zs * (0.21 + 0.002) - 0.002
            if s.volume < 0: s.invert()
            out.add('tinta_verde', s)
        for xa, xb in ((-0.32, -0.4), (0.32, 0.45)):
            h = trimesh.convex.convex_hull(np.array([(xa, 0, -0.21), (xa, 0, 0.21), (xb, 0.28, -0.3), (xb, 0.28, 0.3), (xa + 0.004 * np.sign(xa), 0, -0.21), (xb + 0.004 * np.sign(xa), 0.28, 0.3)]))
            out.add('tinta_verde', h)
        return out
    c = faces(0)
    p.merge(c, _tr(0.05, 0.38, 0))
    anel(p, 'tinta_verde', 0.0, 0.0, 0, 0, 4) if False else None
    p.box('tinta_verde', -0.36, 0.5, 0.655, 0.67, -0.3, -0.28); p.box('tinta_verde', -0.36, 0.5, 0.655, 0.67, 0.28, 0.3)
    p.box('terra' if 'terra' in CORES else 'papelao', -0.25, 0.35, 0.5, 0.52, -0.2, 0.2)
    for zs in (-1, 1):
        p.seg('aco_pintado', (0.65, 0.3, zs * 0.08), (-0.6, 0.62, zs * 0.25), 0.03)          # bracos
        p.cyl('borracha', 0.02, 0.0, 0.001, x=0, z=0) if False else p.seg('borracha', (-0.58, 0.615, zs * 0.245), (-0.85, 0.68, zs * 0.3), 0.04)
        p.seg('aco_pintado', (-0.2, 0.38, zs * 0.2), (-0.25, 0.0, zs * 0.2), 0.025)          # pes
        p.cham('aco_pintado', -0.28, -0.2, 0.0, 0.015, zs * 0.2 - 0.03, zs * 0.2 + 0.03, 0.004)
    _roda(p, (0.62, 0.2, 0), 0.2, 0.09, 'z', mat_aro='aco_pintado')
    for zs in (-1, 1): p.seg('aco_pintado', (0.62, 0.2, zs * 0.06), (0.4, 0.38, zs * 0.12), 0.025)


@item('tarro_leite', 'Tarro de leite', 'mobilias', 'fazenda', comodos=['fazenda', 'celeiro', 'armazem', 'padaria'], colisao='caixa', conteiner=True, slots=1,
      saque=['agua'], interacao='guarda 20 L de água (reservatório portátil)', pega=[0, 0.75, 0])
def tarro_leite(M):
    p = M.base
    torno(p, 'chapa_galv', [(0.0, 0.0), (0.16, 0.0), (0.17, 0.02), (0.17, 0.48), (0.16, 0.5), (0.1, 0.6), (0.08, 0.64), (0.08, 0.68), (0.0, 0.68)], 32)
    for y in (0.08, 0.45): anel(p, 'chapa_galv', 0.168, 0.176, y, y + 0.02, 32)
    torno(p, 'chapa_galv', [(0.0, 0.66), (0.095, 0.66), (0.095, 0.7), (0.07, 0.73), (0.03, 0.76), (0.0, 0.76)], 24)
    for xs in (-1, 1):
        p.seg('chapa_galv', (xs * 0.1, 0.58, 0.0), (xs * 0.16, 0.62, 0.0), 0.02, 0.01); p.seg('chapa_galv', (xs * 0.16, 0.62, 0.0), (xs * 0.16, 0.55, 0.0), 0.02, 0.01)


@item('espantalho', 'Espantalho', 'mobilias', 'fazenda', comodos=['fazenda', 'quintal', 'abrigo'], ambiente=True, colisao='caixa',
      observacao='de longe parece um zumbi parado: sobreviventes novos levam susto', constroi={'roupas': 1, 'palha': 2, 'tabua': 1})
def espantalho(M):
    p = M.base; rng = np.random.default_rng(76)
    p.cham('madeira_crua', -0.035, 0.035, 0.0, 1.85, -0.035, 0.035, 0.005); p.cham('madeira_crua', -0.6, 0.6, 1.4, 1.46, -0.03, 0.03, 0.005)
    fofo(p, 'xadrez', 0.0, 1.25, 0.0, 0.22, 0.25, 0.13, e1=0.4, e2=0.5)                      # camisa
    for xs in (-1, 1):
        fofo(p, 'xadrez', xs * 0.36, 1.42, 0.0, 0.2, 0.07, 0.07, e1=0.6, e2=0.6)
        for k in range(6): p.seg('palha', (xs * 0.55, 1.43 + rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03)), (xs * 0.68, 1.38 + rng.uniform(-0.06, 0.04), rng.uniform(-0.05, 0.05)), 0.008, 0.003)
    fofo(p, 'pano_espantalho', 0.0, 0.92, 0.0, 0.2, 0.12, 0.12, e1=0.5, e2=0.5)              # calca
    for xs in (-1, 1):
        fofo(p, 'pano_espantalho', xs * 0.1, 0.65, 0.0, 0.08, 0.25, 0.08, e1=0.6, e2=0.6)
        for k in range(5): p.seg('palha', (xs * 0.1 + rng.uniform(-0.03, 0.03), 0.41, rng.uniform(-0.03, 0.03)), (xs * 0.11 + rng.uniform(-0.06, 0.06), 0.3, rng.uniform(-0.05, 0.05)), 0.008, 0.003)
    fofo(p, 'lona' if 'lona' in CORES else 'papelao', 0.0, 1.62, 0.0, 0.12, 0.14, 0.12, e1=0.6, e2=0.6)   # cabeca de saco
    p.box('esmalte_escuro', -0.06, -0.03, 1.65, 1.68, 0.115, 0.12); p.box('esmalte_escuro', 0.03, 0.06, 1.65, 1.68, 0.115, 0.12)
    for k in range(5): p.box('esmalte_escuro', -0.05 + k * 0.022, -0.04 + k * 0.022, 1.57 + (k % 2) * 0.01, 1.58 + (k % 2) * 0.01, 0.11, 0.118)
    torno(p, 'palha', [(0.0, 1.72), (0.26, 1.72), (0.26, 1.735), (0.12, 1.74), (0.11, 1.84), (0.0, 1.85)], 24)   # chapeu
    for k in range(12): a = k / 12 * 2 * math.pi; p.seg('palha', (0.25 * math.cos(a), 1.725, 0.25 * math.sin(a)), (0.3 * math.cos(a + 0.1), 1.71, 0.3 * math.sin(a + 0.1)), 0.006, 0.003)


@item('saco_racao', 'Saco de ração', 'loot', 'agricultura', recurso='racao', valor=2, peso_kg=10, empilha=1, onde=['fazenda', 'armazem', 'celeiro', 'supermercado'],
      efeito='alimenta galinhas (5 dias); em último caso, comida ruim (fome -10, enjoo)', pega=[0, 0.3, 0])
def saco_racao(M):
    p = M.base
    img = Image.new('RGB', (512, 512), (230, 222, 196)); d = ImageDraw.Draw(img); d.rectangle([0, 0, 512, 140], fill=(20, 60, 150))
    texto_c(d, (256, 70), 'RAÇÃO', 90, (255, 255, 255)); texto_c(d, (256, 230), 'AVES', 80, (20, 60, 150)); d.ellipse([170, 290, 340, 430], fill=(200, 120, 40)); d.polygon([(330, 340), (380, 360), (330, 380)], fill=(240, 180, 40))
    texto_c(d, (256, 470), '25 kg', 54, (40, 40, 40)); mat_imagem('racao_arte', img, 0.85)
    fofo(p, 'azul_racao', 0.0, 0.1, 0.0, 0.3, 0.1, 0.2, e1=0.3, e2=0.25)
    p.hull('racao_arte', [(-0.24, 0.2, -0.15), (0.24, 0.2, -0.15), (-0.24, 0.2, 0.15), (0.24, 0.2, 0.15), (-0.24, 0.202, -0.15), (0.24, 0.202, -0.15), (-0.24, 0.202, 0.15), (0.24, 0.202, 0.15)])
    p.uv['racao_arte'] = lambda v, n: np.stack([(v[:, 0] + 0.24) / 0.48, 1 - (v[:, 2] + 0.15) / 0.3], 1)
    for k in range(8): p.box('azul_racao', 0.28 + (k % 2) * 0.01, 0.3, 0.06, 0.14, -0.18 + k * 0.045, -0.16 + k * 0.045)


# ---------------------------------------------------------------------------- ARMAZEM
@item('porta_pallet', 'Estante porta-pallet', 'mobilias', 'armazem', comodos=['armazem', 'supermercado', 'fabrica', 'correios'], conteiner=True, slots=8,
      saque=['materiais', 'comida', 'ferramentas'], colisao='caixa', modulo_m=2.0, interacao='dá para escalar (2 níveis): vigia dentro do armazém')
def porta_pallet(M):
    p = M.base; X, Z, H = 1.3, 0.55, 3.6
    for xs in (-1, 1):
        for zs in (-1, 1):
            x, z = xs * X, zs * Z; p.cham('tinta_azul', x - 0.04, x + 0.04, 0.0, H, z - 0.04, z + 0.04, 0.004)
            for k in range(40): p.box('esmalte_escuro', x - 0.012, x + 0.012, 0.1 + k * 0.085, 0.13 + k * 0.085, z + zs * 0.04, z + zs * 0.0405)
            p.cham('aco', x - 0.07, x + 0.07, 0.0, 0.008, z - 0.07, z + 0.07, 0.002)
        for k in range(9): p.seg('tinta_azul', (xs * X, 0.15 + k * 0.38, -Z + 0.04), (xs * X, 0.15 + (k + 1) * 0.38, Z - 0.04) if k % 2 == 0 else (xs * X, 0.15 + (k + 1) * 0.38, -Z + 0.04), 0.025, 0.02) if False else None
        for k in range(8):
            y0 = 0.2 + k * 0.42; p.seg('tinta_azul', (xs * X, y0, -Z + 0.04 if k % 2 else Z - 0.04), (xs * X, y0 + 0.42, Z - 0.04 if k % 2 else -Z + 0.04), 0.025, 0.02)
    rng = np.random.default_rng(77)
    for y in (0.15, 1.35, 2.55):
        for zs in (-1, 1): p.cham('laranja_seg', -X, X, y, y + 0.12, zs * Z - 0.03, zs * Z + 0.03, 0.006)
        if y > 3: continue
        for i, x in enumerate((-0.65, 0.65)):
            pal = P(); pallet(type('M', (), {'base': pal, 'parte': lambda s, *a, **k: P()})()) if 'pallet' in ITENS else None
            p.merge(pal, _tr(x, y + 0.12, 0))
            tipo = rng.integers(0, 3)
            if tipo == 0:
                for a in range(2):
                    for b in range(2):
                        for c in range(2): p.cham('papelao', x - 0.55 + a * 0.55, x - 0.02 + a * 0.55, y + 0.27 + c * 0.38, y + 0.63 + c * 0.38, -0.5 + b * 0.5, -0.02 + b * 0.5, 0.008)
            elif tipo == 1:
                for a in range(2):
                    for b in range(2): p.cyl('tinta_azul', 0.26, y + 0.27, y + 1.07, x=x - 0.27 + a * 0.54, z=-0.27 + b * 0.54, sec=20)
            else:
                for c in range(4): fofo(p, 'lona', x, y + 0.36 + c * 0.17, 0, 0.5, 0.09, 0.4, e1=0.3, e2=0.3)


@item('empilhadeira', 'Empilhadeira', 'mobilias', 'armazem', comodos=['armazem', 'fabrica', 'serraria', 'supermercado'], ambiente=True, colisao='caixa',
      obstaculo=True, conteiner=True, slots=2, saque=['combustivel'], coleta={'recurso': 'combustivel', 'total': 2, 'ferramenta': 'mangueira e galão', 'segundos_por_unidade': 10},
      desmonta={'sucata': 15, 'bateria_carro': 1, 'peca_motor': 2}, observacao='com bateria e gás, ergue escombros pesados')
def empilhadeira(M):
    p = M.base; X = 0.55
    p.cham('amarelo_maquina', -X, X, 0.25, 1.05, -0.9, 0.55, 0.06)                          # chassi
    p.cham('esmalte_escuro', -X - 0.01, X + 0.01, 0.25, 0.75, -1.15, -0.85, 0.08)           # contrapeso
    p.cham('graxa', -X + 0.08, X - 0.08, 1.05, 1.12, -0.85, 0.0, 0.02)
    fofo(p, 'vinil_maca' if 'vinil_maca' in CORES else 'plastico_preto', 0.0, 1.2, -0.4, 0.26, 0.06, 0.22, e1=0.3, e2=0.3)   # banco
    p.hull('plastico_preto', [(-0.24, 1.2, -0.62), (0.24, 1.2, -0.62), (-0.24, 1.65, -0.68), (0.24, 1.65, -0.68), (-0.24, 1.2, -0.56), (0.24, 1.2, -0.56), (-0.24, 1.65, -0.62), (0.24, 1.65, -0.62)])
    cyl_eixo(p, 'plastico_preto', 0.022, 0.0, 0.35, 'z', (0, 1.25, 0.15), 8) if False else p.seg('plastico_preto', (0, 1.05, 0.25), (0, 1.38, 0.05), 0.05)
    anel(p, 'plastico_preto', 0.15, 0.17, -0.015, 0.015, 24, 'y', (0, 1.4, 0.04))
    for xs in (-1, 1):                                                                    # gaiola de protecao
        for z in (-0.75, 0.42): p.seg('esmalte_escuro', (xs * (X - 0.04), 1.05, z), (xs * (X - 0.04), 2.15, z * 0.9), 0.06)
        p.seg('esmalte_escuro', (xs * (X - 0.04), 2.15, -0.68), (xs * (X - 0.04), 2.15, 0.38), 0.06)
    for z in np.linspace(-0.6, 0.3, 6): p.seg('esmalte_escuro', (-X + 0.04, 2.15, z), (X - 0.04, 2.15, z), 0.04)
    for xs in (-1, 1):
        _roda(p, (xs * (X - 0.05), 0.27, 0.35), 0.27, 0.2, 'x', mat_aro='amarelo_maquina'); _roda(p, (xs * (X - 0.08), 0.22, -0.8), 0.22, 0.16, 'x', mat_aro='amarelo_maquina')
        p.cham('esmalte_escuro', xs * 0.32 - 0.05, xs * 0.32 + 0.05, 0.05, 2.5, 0.62, 0.7, 0.01)   # mastro
    p.cham('esmalte_escuro', -0.38, 0.38, 2.42, 2.5, 0.62, 0.7, 0.01); p.cham('esmalte_escuro', -0.38, 0.38, 0.4, 0.46, 0.62, 0.7, 0.01)
    p.cyl('aco_polido', 0.04, 0.3, 1.8, x=0.0, z=0.66, sec=14)
    p.cham('esmalte_escuro', -0.42, 0.42, 0.08, 0.6, 0.72, 0.78, 0.01)                      # avental
    for xs in (-1, 1):
        x = xs * 0.24; p.cham('aco_pintado', x - 0.05, x + 0.05, 0.08, 0.6, 0.78, 0.82, 0.004); p.cham('aco_pintado', x - 0.05, x + 0.05, 0.03, 0.08, 0.78, 1.85, 0.008)
    for xs in (-1, 1): p.cham('farol' if 'farol' in CORES else 'plastico_branco', xs * 0.4 - 0.05, xs * 0.4 + 0.05, 2.1, 2.18, 0.4, 0.45, 0.01)
    p.cyl('tinta_vermelha', 0.13, 0.95, 1.55, x=0.0, z=-1.0, sec=18) if False else cyl_eixo(p, 'plastico_branco', 0.13, -0.35, 0.35, 'x', (0, 1.0, -1.0), 18)   # botijao de gas


# ---------------------------------------------------------------------------- FERRO-VELHO / CAIXA D'AGUA
@item('carcaca_carro', 'Carcaça de carro depenada', 'mobilias', 'ferrovelho', comodos=['ferro_velho', 'rua', 'garagem', 'fazenda'], ambiente=True, colisao='caixa',
      obstaculo=True, coleta={'recurso': 'sucata', 'total': 10, 'ferramenta': 'chave_inglesa', 'segundos_por_unidade': 6}, barulho='médio ao desmontar',
      interacao='empilhada vira muro (3 carcaças = 1 muro forte)')
def carcaca_carro(M):
    p = M.base; rng = np.random.default_rng(78)
    W, L = 0.86, 2.15
    base = Polygon([(-L, 0.3), (L, 0.3), (L + 0.05, 0.55), (L - 0.15, 0.78), (0.9, 0.82), (0.45, 1.28), (-0.95, 1.3), (-1.4, 0.85), (-L - 0.05, 0.8), (-L - 0.05, 0.5)])
    casca = base.difference(Polygon([(-L + 0.06, 0.36), (L - 0.06, 0.36), (L - 0.06, 0.74), (0.85, 0.76), (0.4, 1.22), (-0.9, 1.24), (-1.35, 0.8), (-L + 0.06, 0.76)]))
    janelas = [Polygon([(0.72, 0.84), (0.4, 1.2), (-0.2, 1.21), (-0.2, 0.84)]), Polygon([(-0.28, 0.84), (-0.28, 1.21), (-0.88, 1.22), (-1.25, 0.84)])]
    portas = [Polygon([(0.75, 0.36), (0.75, 0.82), (-0.2, 0.82), (-0.2, 0.36)])]
    for zs in (-1, 1):
        lado = base
        for j in janelas: lado = lado.difference(j)
        for d_ in portas if zs > 0 else []: lado = lado.difference(d_)
        m = trimesh.creation.extrude_polygon(lado.buffer(0), 0.02); m.vertices[:, 2] += zs * W - (0.02 if zs > 0 else 0)
        if m.volume < 0: m.invert()
        p.add('pintura_carro', m)
        for k in range(5): x = rng.uniform(-L + 0.2, L - 0.3); y = rng.uniform(0.38, 0.7); p.box('ferrugem', x, x + rng.uniform(0.15, 0.4), y, y + rng.uniform(0.06, 0.15), *sorted((zs * (W + 0.001), zs * (W + 0.003))))
    for zz in (-W + 0.02, W - 0.02):
        for a, b in ((0.82, 0.36), (-0.24, 0.36)): pass
    p.cham('ferrugem', -L - 0.05, L + 0.05, 0.3, 0.36, -W, W, 0.01)                         # assoalho
    p.cham('pintura_carro', 0.85, L, 0.74, 0.78, -W, W, 0.01) if False else None            # capo arrancado: motor aberto
    p.hull('pintura_carro', [(-0.95, 1.28, -W), (-0.95, 1.28, W), (0.45, 1.26, -W), (0.45, 1.26, W), (-0.95, 1.3, -W), (-0.95, 1.3, W), (0.45, 1.28, -W), (0.45, 1.28, W)])   # teto
    p.hull('pintura_carro', [(-L - 0.05, 0.78, -W), (-L - 0.05, 0.78, W), (-1.4, 0.83, -W), (-1.4, 0.83, W), (-L - 0.05, 0.8, -W), (-L - 0.05, 0.8, W), (-1.4, 0.85, -W), (-1.4, 0.85, W)])   # porta-malas
    for xs in (-1, 1): p.cham('pintura_carro', xs * L - 0.05, xs * L + 0.05, 0.3, 0.75, -W, W, 0.01); p.cham('cromo', xs * (L + 0.05) - 0.03, xs * (L + 0.05) + 0.03, 0.36, 0.46, -W - 0.02, W + 0.02, 0.012)
    for x0, x1 in ((0.75, 0.9), (-0.24, -0.2), (-1.3, -1.2)):
        for zs in (-1, 1): p.hull('pintura_carro', [(x0, 0.8, zs * W), (x1, 0.8, zs * W), (x0 - 0.3 * (x0 > 0.5) + 0.05 * (x0 < -1), 1.27, zs * W * 0.98), (x1 - 0.3 * (x0 > 0.5) + 0.05 * (x0 < -1), 1.27, zs * W * 0.98), (x0, 0.8, zs * (W - 0.03)), (x1, 0.8, zs * (W - 0.03))])
    p.cham('esmalte_escuro', 1.0, 1.9, 0.36, 0.6, -0.45, 0.45, 0.03)                          # bloco do motor que sobrou
    for k in range(4): p.cyl('graxa', 0.04, 0.6, 0.66, x=1.15 + k * 0.17, z=0.0, sec=10)
    for k in range(4):
        x = -1.35 if k < 2 else 1.25; z = (-1 if k % 2 else 1) * (W - 0.1)
        p.cham('tijolo' if 'tijolo' in CORES else 'pedra', x - 0.12, x + 0.12, 0.0, 0.3, z - 0.1, z + 0.1, 0.01)   # sobre blocos, sem rodas
    p.cham('tecido_cadeira', -0.75, -0.2, 0.36, 0.5, -W + 0.1, -0.05, 0.03); p.cham('ferrugem', -0.85, -0.75, 0.36, 0.95, -W + 0.1, -0.05, 0.02)
    for k in range(9): p.seg('aco', (-0.7 + k * 0.06, 0.5, -0.05), (-0.68 + k * 0.06, 0.5, -W + 0.12), 0.006)  # molas do banco rasgado


@item('pilha_calotas', 'Pilha de calotas e peças', 'mobilias', 'ferrovelho', comodos=['ferro_velho', 'garagem', 'posto'], ambiente=True, colisao='caixa',
      coleta={'recurso': 'sucata', 'total': 4, 'ferramenta': 'nenhuma', 'segundos_por_unidade': 3}, barulho='alto (lata batendo)',
      interacao='pendurada num fio vira alarme barulhento')
def pilha_calotas(M):
    p = M.base; rng = np.random.default_rng(79)
    for k in range(9):
        c = P(); torno(c, 'calota', [(0.0, 0.05), (0.1, 0.045), (0.17, 0.025), (0.19, 0.0), (0.18, -0.005)], 28, 'y', (0, 0, 0))
        for a in np.linspace(0, 2 * math.pi, 8, endpoint=False): c.seg('aco', (0.06 * math.cos(a), 0.042, 0.06 * math.sin(a)), (0.15 * math.cos(a), 0.03, 0.15 * math.sin(a)), 0.012, 0.004)
        ang = rng.uniform(0.3, 1.4) if k > 3 else rng.uniform(0, 0.2)
        x, z = rng.uniform(-0.35, 0.35), rng.uniform(-0.3, 0.3); y = 0.02 + (0.2 if k > 3 else k * 0.03)
        p.merge(c, _tr(x, y, z) @ _ry(rng.uniform(0, 6.28)) @ _rx(ang))
    for k in range(2): _roda(p, (0.35 - k * 0.65, 0.1 + k * 0.0, -0.25 + k * 0.45), 0.3, 0.19, 'z' if k else 'x', murcha=0.6) if False else None
    t = P(); _roda(t, (0, 0, 0), 0.32, 0.2, 'x', mat_aro='ferrugem'); p.merge(t, _tr(0.45, 0.1, -0.1) @ trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]))
    for k in range(3): p.seg('ferrugem', (rng.uniform(-0.5, 0.5), 0.01, rng.uniform(-0.4, 0.4)), (rng.uniform(-0.5, 0.5), 0.03, rng.uniform(-0.4, 0.4)), 0.03, 0.01)
    cyl_eixo(p, 'ferrugem', 0.025, -0.55, 0.2, 'x', (0, 0.03, 0.35), 10)


@item('bomba_agua_manual', 'Bomba d\'água manual', 'mobilias', 'fazenda', comodos=['fazenda', 'quintal', 'caixa_dagua', 'patio_missoes', 'rua'], ambiente=True,
      colisao='caixa', coleta={'recurso': 'agua', 'total': 99, 'ferramenta': 'nenhuma', 'segundos_por_unidade': 6}, barulho='baixo (rangido)',
      estacao='água sem fim (poço): o lugar mais disputado da cidade', observacao='água de poço: ferver antes de beber')
def bomba_agua_manual(M):
    p = M.base
    p.cham('pedra' if 'pedra' in CORES else 'granito', -0.45, 0.45, 0.0, 0.12, -0.45, 0.45, 0.03)
    torno(p, 'verde_maquina', [(0.0, 0.12), (0.12, 0.12), (0.12, 0.14), (0.06, 0.18), (0.06, 0.95), (0.08, 0.97), (0.08, 1.12), (0.06, 1.15), (0.0, 1.16)], 24)
    for y in (0.4, 0.9): anel(p, 'verde_maquina', 0.06, 0.075, y, y + 0.03, 24)
    p.seg('verde_maquina', (0.0, 0.85, 0.05), (0.0, 0.78, 0.3), 0.05); p.seg('verde_maquina', (0.0, 0.78, 0.3), (0.0, 0.7, 0.34), 0.045)   # bica
    p.seg('verde_maquina', (0.0, 1.12, -0.04), (0.0, 1.25, -0.08), 0.03); p.seg('aco', (0.0, 1.22, -0.08), (0.0, 1.1, -0.7), 0.035)   # alavanca
    p.seg('borracha', (0.0, 1.11, -0.6), (0.0, 1.08, -0.78), 0.045)
    torno(p, 'chapa_galv', [(0.0, 0.12), (0.14, 0.12), (0.16, 0.36), (0.155, 0.37), (0.13, 0.14)], 24, 'y', (0, 0, 0.35), fechar=False)   # balde
    p.cyl('agua_suja' if 'agua_suja' in CORES else 'vidro_escuro', 0.145, 0.12, 0.3, x=0.0, z=0.35, sec=24)
    p.seg('aco', (-0.155, 0.36, 0.35), (0.0, 0.5, 0.35), 0.006); p.seg('aco', (0.155, 0.36, 0.35), (0.0, 0.5, 0.35), 0.006)
    p.box('agua_suja' if 'agua_suja' in CORES else 'vidro_escuro', -0.3, 0.2, 0.12, 0.122, 0.2, 0.44)
