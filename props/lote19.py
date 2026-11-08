# Lote 19: vila e cidade (fases 4 e 5): o assentamento volta a ter rua acesa, feira, muralha e prefeitura.
# Executado por gerar_props.py (usa as mesmas funcoes e materiais dos lotes anteriores).
# Campos novos: consumo_w (energia que a peca gasta), troca (ponto de comercio com caravanas), raio_m (alcance do efeito).
#         marco, moral, energia_w, produz, vida, modulo_m e estacao seguem os lotes 16 a 18.
CORES.update({'poste_cinza': (110, 112, 110), 'luminaria': (40, 42, 44), 'lampada_sodio': (255, 160, 60), 'transformador': (60, 80, 66),
              'isolador': (120, 40, 20), 'pa_turbina': (220, 222, 220), 'tinta_placa': (200, 190, 150), 'barro_cru': (150, 96, 60),
              'vela': (236, 228, 200), 'chama_vela': (255, 180, 60), 'flor_amarela': (230, 180, 20), 'flor_vermelha': (180, 20, 20),
              'lousa_preco': (20, 26, 22), 'areia_filtro': (190, 170, 120), 'cascalho': (110, 106, 100), 'pao_casca': (150, 80, 30)})
METALICOS.update({'luminaria': (0.6, 0.5), 'transformador': (0.5, 0.5), 'poste_cinza': (0.1, 0.8)})
FOSCOS.update({'barro_cru': 0.95, 'tinta_placa': 0.85, 'vela': 0.6, 'lousa_preco': 0.9, 'pao_casca': 0.75})
TEX_PROPRIAS += [('barro_cru', 'barro', 0.5, 512), ('poste_cinza', 'barro', 1.0, 512)]
EMISSIVOS.update({'lampada_sodio': [1.0, 0.62, 0.25], 'chama_vela': [1.0, 0.7, 0.25]})


def _placa(nome, linhas, larg_px=1024, alt_px=512, fundo=(200, 190, 150), cor=(40, 30, 20), tam=(150, 90)):
    """Material com texto pintado a mao (placas de madeira, lousas)."""
    img = Image.new('RGB', (larg_px, alt_px), fundo); d = ImageDraw.Draw(img)
    n = len(linhas)
    for i, t in enumerate(linhas):
        texto_c(d, (larg_px // 2, int(alt_px * (i + 0.5) / n)), t, tam[min(i, len(tam) - 1)], cor, larg=larg_px - 60)
    mat_imagem(nome, img, 0.85)


def _uv_frente(x0, x1, y0, y1):
    return lambda v, n: np.stack([(v[:, 0] - x0) / (x1 - x0), (v[:, 1] - y0) / (y1 - y0)], 1)


# ---------------------------------------------------------------------------- RUA ACESA
@item('poste_luz', 'Poste de luz restaurado', 'mobilias', 'cidade', comodos=['rua', 'abrigo', 'praca'],
      constroi={'cano_metal': 2, 'fio_eletrico': 3, 'placa_circuito': 1}, ferramenta='chave_inglesa', estacao_obra='bancada_eletronica', fase=4,
      luz_m=15, consumo_w=60, moral=1, estacao='iluminação (rua acesa à noite: zumbi é visto de longe e os moradores andam sem medo)')
def poste_luz(M):
    p = M.base; H = 6.5
    torno(p, 'poste_cinza', [(0.0, 0.0), (0.13, 0.0), (0.11, H * 0.5), (0.08, H), (0.0, H)], 8, 'y', (0, 0, 0))   # poste de concreto octogonal
    torno(p, 'concreto', [(0.0, -0.02), (0.26, -0.02), (0.26, 0.06), (0.15, 0.1), (0.0, 0.1)], 16, 'y', (0, 0, 0))
    for y in np.arange(2.4, H - 0.6, 0.38): p.add('aco', trimesh.creation.cylinder(radius=0.012, segment=[(0.0, y, 0.1), (0.0, y, 0.2)], sections=6))   # degraus de vergalhao
    varrer(p, 'aco_pintado', circ(0.03, 10), [(0.0, H - 0.4, 0.06)] + [(0.0, H - 0.4 + 0.35 * math.sin(t), 0.06 + 1.2 * (1 - math.cos(t * 0.9))) for t in np.linspace(0.1, 1.5, 10)], cap=True)   # braco curvo
    zc, yc = 1.38, H - 0.06
    q = P(); q.hull('luminaria', [(sx * w, y, z) for sx in (-1, 1) for (w, y, z) in ((0.1, 0.05, -0.25), (0.16, 0.08, 0.0), (0.16, 0.06, 0.3), (0.12, 0.0, 0.32), (0.12, -0.02, -0.25))])
    q.hull('lampada_sodio', [(sx * 0.12, -0.025, z) for sx in (-1, 1) for z in (-0.18, 0.26)] + [(sx * 0.09, -0.05, z) for sx in (-1, 1) for z in (-0.12, 0.2)])
    p.merge(q, trimesh.transformations.translation_matrix([0, yc, zc]))
    p.cham('aco_pintado', -0.1, 0.1, 2.4, 2.75, -0.17, -0.09, 0.008)                                 # caixa de emenda com fiacao refeita
    for k, cor in enumerate(('fio_vermelho', 'plastico_preto')):
        varrer(p, cor, circ(0.006, 6), [(-0.03 + 0.06 * k, 2.75, -0.13), (-0.05 + 0.1 * k, 3.3, -0.12), (-0.02 + 0.04 * k, H - 0.45, -0.07), (0.0, H - 0.4, 0.02)], cap=False)
    for k in range(3): anel(p, 'fita_preta', 0.118, 0.124, 1.6 + k * 0.05, 1.62 + k * 0.05, 8, 'y', (0, 0, 0))   # fitas de emenda
    _placa('placa_poste', ['N.º 12'], 256, 128, (220, 220, 210), (20, 20, 20), (90,))
    p.box('placa_poste', -0.08, 0.08, 2.0, 2.08, 0.125, 0.128); p.uv['placa_poste'] = _uv_frente(-0.08, 0.08, 2.0, 2.08)


@item('subestacao', 'Subestação religada', 'mobilias', 'cidade', comodos=['rua', 'fabrica', 'cidade'],
      constroi={'fio_eletrico': 10, 'placa_circuito': 4, 'motor_eletrico': 2, 'cimento': 6, 'arame_farpado': 2},
      ferramenta='chave_inglesa', estacao_obra='bancada_eletronica', fase=4, marco=True, energia_w=20000, trabalha=2, ponto_uso=[1.0, 0.0, 1.9],
      precisa_achar='transformador (subestação do bairro industrial)', raio_m=200,
      estacao='marco da fase Vila → Cidade nova (devolve luz às casas num raio de 200 m: postes, geladeiras e o rádio da torre)')
def subestacao(M):
    p = M.base; X, Z = 1.6, 1.4
    p.cham('concreto', -X, X, 0.0, 0.2, -Z, Z, 0.02)                                                 # base
    p.cham('transformador', -0.6, 0.6, 0.2, 1.65, -0.45, 0.45, 0.02)                                  # tanque do transformador
    for zs in (-1, 1):                                                                               # radiadores de aletas
        for k, x in enumerate(np.linspace(-0.5, 0.5, 9)): p.box('transformador', x - 0.008, x + 0.008, 0.3, 1.45, zs * 0.45 - 0.22 * (zs < 0), zs * 0.45 + 0.22 * (zs > 0))
        p.cham('transformador', -0.55, 0.55, 1.42, 1.48, zs * 0.45 - 0.22 * (zs < 0), zs * 0.45 + 0.22 * (zs > 0), 0.006)
    anel(p, 'transformador', 0.0, 0.22, -0.3, 0.3, 24, 'x', (0, 1.95, 0.0))                           # conservador de oleo
    for x in (-0.25, 0.25): p.cham('transformador', x - 0.03, x + 0.03, 1.65, 1.8, -0.03, 0.03, 0.004)
    for k, x in enumerate((-0.35, 0.0, 0.35)):                                                       # buchas de porcelana com saias
        for j in range(6): torno(p, 'isolador', [(0.03, 1.65 + j * 0.06), (0.07, 1.67 + j * 0.06), (0.05, 1.71 + j * 0.06), (0.03, 1.71 + j * 0.06)], 16, 'y', (x, 0, 0.25))
        p.add('cobre', trimesh.creation.cylinder(radius=0.012, segment=[(x, 2.0, 0.25), (x, 2.12, 0.25)], sections=8))
        varrer(p, 'cobre', circ(0.008, 6), [(x, 2.12, 0.25), (x * 1.3, 2.5, 0.6), (x * 1.6, 2.9, 1.2)], cap=False)
    for k, x in enumerate((-0.25, 0.25)):                                                            # buchas de baixa
        for j in range(3): torno(p, 'isolador', [(0.025, 1.65 + j * 0.05), (0.05, 1.665 + j * 0.05), (0.035, 1.7 + j * 0.05), (0.025, 1.7 + j * 0.05)], 14, 'y', (x, 0, -0.25))
    p.cham('aco_pintado', 0.85, 1.4, 0.2, 1.6, -0.35, 0.25, 0.01)                                     # quadro de disjuntores
    p.cham('aco_pintado', 0.86, 1.39, 0.22, 1.58, 0.25, 0.28, 0.004)
    p.cham('aco', 1.3, 1.33, 0.8, 1.0, 0.28, 0.3, 0.003)
    _placa('placa_perigo', ['PERIGO', 'ALTA TENSÃO', 'RELIGADA PELA VILA'], 512, 512, (230, 190, 30), (20, 20, 20), (120, 70, 44))
    p.box('placa_perigo', 0.95, 1.3, 1.1, 1.45, 0.281, 0.284); p.uv['placa_perigo'] = _uv_frente(0.95, 1.3, 1.1, 1.45)
    for k, cor in enumerate(('folha_verde', 'tinta_amarela', 'folha_verde')): torno(p, cor, [(0.0, 0.0), (0.015, 0.0), (0.012, 0.01), (0.0, 0.012)], 10, 'z', (0.98 + k * 0.05, 0.95, 0.28))   # luzes do quadro
    for x0, z0, x1, z1 in ((-X, -Z, X, -Z), (X, -Z, X, Z), (-X, Z, X, Z), (-X, -Z, -X, Z)):           # cerca de tela com postes
        L = math.hypot(x1 - x0, z1 - z0); n = int(L / 0.9) + 1
        for k in range(n + 1):
            t = k / n; px, pz = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            p.add('galvanizado', trimesh.creation.cylinder(radius=0.022, segment=[(px, 0.2, pz), (px, 2.3, pz)], sections=8))
            p.add('galvanizado', trimesh.creation.cylinder(radius=0.01, segment=[(px, 2.3, pz), (px + 0.0, 2.55, pz)], sections=6))
        if z0 == z1 == Z: continue                                                                    # frente: portao aberto (abaixo)
        q = P(); _tela(q, 0.0, L, 0.25, 2.25, 0.0, int(L / 0.06), 34, 'galvanizado', 0.0012)
        for y in (2.35, 2.45, 2.55): q.add('aco', trimesh.creation.cylinder(radius=0.0018, segment=[(0, y, 0), (L, y, 0)], sections=4))
        ang = math.atan2(z1 - z0, x1 - x0)
        p.merge(q, trimesh.transformations.translation_matrix([x0, 0, z0]) @ _rot(-ang, [0, 1, 0]))
    q = P(); _tela(q, 0.0, X - 0.5, 0.25, 2.25, 0.0, int((X - 0.5) / 0.06), 34, 'galvanizado', 0.0012)   # frente parcial e folha aberta
    p.merge(q, trimesh.transformations.translation_matrix([-X, 0, Z])); p.merge(q, trimesh.transformations.translation_matrix([0.5, 0, Z]))
    q = P(); _tela(q, 0.0, 1.0, 0.25, 2.25, 0.0, 17, 34, 'galvanizado', 0.0012)
    p.merge(q, trimesh.transformations.translation_matrix([-X + X - 0.5, 0, Z]) @ _rot(-1.2, [0, 1, 0]))
    for x in (-0.5, 0.5): p.add('galvanizado', trimesh.creation.cylinder(radius=0.03, segment=[(x, 0.2, Z), (x, 2.3, Z)], sections=8))
    p.add('plastico_preto', trimesh.creation.cylinder(radius=0.02, segment=[(1.12, 0.2, -0.05), (1.12, 0.05, -Z - 0.3)], sections=8))   # cabo que sai para a vila


@item('turbina_eolica', 'Turbina eólica pequena no mastro', 'mobilias', 'energia', comodos=['abrigo', 'fazenda', 'cidade'],
      constroi={'cano_metal': 6, 'motor_eletrico': 1, 'chapa_metal': 3, 'fio_eletrico': 4, 'bateria_carro': 2}, ferramenta='chave_inglesa',
      estacao_obra='bancada_eletronica', fase=4, energia_w=1000, estacao='energia (1 kW com vento: liga a cerca, o rádio e as geladeiras da vila)')
def turbina_eolica(M):
    p = M.base; H = 8.0
    p.cham('concreto', -0.4, 0.4, -0.02, 0.15, -0.4, 0.4, 0.02)
    torno(p, 'galvanizado', [(0.0, 0.15), (0.1, 0.15), (0.075, H), (0.0, H)], 16, 'y', (0, 0, 0))        # mastro tubular afinando
    for y in (2.5, 5.0): anel(p, 'galvanizado', 0.085, 0.11, y, y + 0.03, 16, 'y', (0, 0, 0))
    torno(p, 'galvanizado', [(0.13, 0.15), (0.2, 0.15), (0.2, 0.18), (0.13, 0.18)], 16, 'y', (0, 0, 0))   # flange com parafusos
    for k in range(8): a = k * math.pi / 4; torno(p, 'aco', [(0.0, 0.18), (0.012, 0.18), (0.012, 0.2), (0.0, 0.2)], 6, 'y', (0.17 * math.cos(a), 0, 0.17 * math.sin(a)))
    for k in range(4):                                                                               # estais
        a = k * math.pi / 2 + math.pi / 4; ax, az = 3.5 * math.cos(a), 3.5 * math.sin(a)
        p.add('aco', trimesh.creation.cylinder(radius=0.004, segment=[(0.06 * math.cos(a), H * 0.62, 0.06 * math.sin(a)), (ax, 0.1, az)], sections=5))
        p.cham('concreto', ax - 0.12, ax + 0.12, -0.02, 0.1, az - 0.12, az + 0.12, 0.01)
    p.add('plastico_preto', trimesh.creation.cylinder(radius=0.012, segment=[(0.08, 0.3, 0.0), (0.08, H - 0.2, 0.0)], sections=6))
    p.cham('aco_pintado', 0.06, 0.26, 1.0, 1.35, -0.1, 0.1, 0.008)                                      # caixa do retificador
    q = M.parte('cabeca', (0.0, H, 0.0), 'porta', eixo='y', abre_graus=360, gira_livre=True)           # gondola + rotor + leme
    torno(q, 'pa_turbina', [(0.0, -0.18), (0.11, -0.16), (0.13, 0.25), (0.1, 0.5), (0.0, 0.56)], 20, 'z', (0, 0.12, 0))
    torno(q, 'galvanizado', [(0.0, 0.0), (0.06, 0.0), (0.06, 0.12), (0.0, 0.12)], 12, 'y', (0, 0, 0))
    q.seg('galvanizado', (0, 0.12, -0.18), (0, 0.15, -1.3), 0.04, 0.04)
    q.hull('pa_turbina', [(s * 0.004, y, z) for s in (-1, 1) for (y, z) in ((0.0, -0.95), (0.45, -1.1), (0.4, -1.6), (-0.1, -1.55))])
    rot = M.parte('rotor', (0.0, H + 0.12, 0.6), 'porta', eixo='z', abre_graus=360, gira_livre=True)
    torno(rot, 'pa_turbina', [(0.0, 0.0), (0.12, 0.0), (0.1, 0.12), (0.04, 0.22), (0.0, 0.24)], 20, 'z', (0, 0, 0))   # cubo (nariz)
    for k in range(3):                                                                               # 3 pas torcidas
        a = math.pi / 2 + k * 2 * math.pi / 3; pts = []
        for r, w, tw in ((0.1, 0.09, 0.5), (0.5, 0.12, 0.35), (1.2, 0.08, 0.15), (1.7, 0.04, 0.05)):
            for s in (-1, 1):
                cx, cy = r * math.cos(a), r * math.sin(a); tx, ty = -math.sin(a), math.cos(a)
                pts.append((cx + s * w * tx * math.cos(tw), cy + s * w * ty * math.cos(tw), 0.04 + s * w * math.sin(tw)))
        for i in range(len(pts) // 2 - 1): rot.hull('pa_turbina', pts[2 * i:2 * i + 4] + [(x, y, z + 0.012) for x, y, z in pts[2 * i:2 * i + 4]])
    _mover(rot, (0.0, H + 0.12, 0.6)); _mover(q, (0.0, H, 0.0))


@item('tratamento_agua', 'Estação de tratamento de água em tambores', 'mobilias', 'cidade', comodos=['abrigo', 'fazenda', 'cidade'],
      constroi={'tambor_200l': 3, 'tubo_pvc': 6, 'pedras': 6, 'carvao': 4, 'tabua': 6}, ferramenta='chave_inglesa', estacao_obra='bancada_carpintaria',
      fase=4, trabalha=1, ponto_uso=[0.0, 0.0, 1.1], produz={'item': 'galao_agua', 'qtd': 10, 'a_cada_min': 60, 'consome': {'alcool': 1}},
      estacao='água tratada (decanta, filtra em areia e carvão e clora: 50 L por hora, sem doença; liga no poço ou no cata-vento)')
def tratamento_agua(M):
    p = M.base; X = 1.5
    for i, (x, y) in enumerate(((-1.0, 0.9), (0.0, 0.6), (1.0, 0.3))):                                 # 3 tambores em degraus sobre estrado
        for xs in (-1, 1):
            for zs in (-1, 1): p.cham('madeira_escura', x + xs * 0.32 - 0.04, x + xs * 0.32 + 0.04, 0.0, y, zs * 0.32 - 0.04, zs * 0.32 + 0.04, 0.004)
        for z in np.linspace(-0.32, 0.32, 5): p.cham('madeira_crua', x - 0.4, x + 0.4, y - 0.025, y, z - 0.06, z + 0.06, 0.003)
        _tambor(p, (x, y, 0.0), 0.29, 0.88, ('tambor_azul', 'tambor_azul', 'plastico_branco')[i], False, False)
        torno(p, ('agua', 'areia_filtro', 'agua')[i], [(0.0, y + 0.8), (0.28, y + 0.8)], 24, 'y', (x, 0, 0))
        if i == 1:
            torno(p, 'cascalho', [(0.0, y + 0.74), (0.28, y + 0.74)], 24, 'y', (x, 0, 0))
        if i != 1: torno(p, 'aco_pintado', [(0.0, y + 0.88), (0.3, y + 0.88), (0.3, y + 0.92), (0.0, y + 0.93)], 24, 'y', (x, 0, 0.0))
    for i, (x, y) in enumerate(((-1.0, 0.9), (0.0, 0.6), (1.0, 0.3))):                                 # etiquetas pintadas nos tambores
        nm = f'etiqueta_agua_{i + 1}'; _placa(nm, [('1 DECANTA', '2 FILTRA', '3 CLORO')[i]], 512, 160, (230, 230, 220), (20, 40, 120), (90,))
        p.box(nm, x - 0.13, x + 0.13, y + 0.4, y + 0.48, 0.2915, 0.2945); p.uv[nm] = _uv_frente(x - 0.13, x + 0.13, y + 0.4, y + 0.48)
    for (x0, y0), (x1, y1) in (((-1.0, 0.9 + 0.2), (0.0, 0.6 + 0.85)), ((0.0, 0.6 + 0.15), (1.0, 0.3 + 0.85))):   # canos de ligacao
        p.seg('pvc', (x0 + 0.3, y0, 0.0), (x0 + 0.5, y0, 0.0), 0.05, 0.05); p.seg('pvc', (x0 + 0.5, y0, 0.0), (x0 + 0.5, y1, 0.0), 0.05, 0.05)
        p.seg('pvc', (x0 + 0.5, y1, 0.0), (x1 - 0.05, y1, 0.0), 0.05, 0.05)
    p.seg('pvc', (-1.5, 1.95, 0.0), (-1.0, 1.95, 0.0), 0.05, 0.05); p.seg('pvc', (-1.0, 1.95, 0.0), (-1.0, 1.82, 0.0), 0.05, 0.05)   # entrada do poco
    for k, z in enumerate((-0.15, 0.15)):                                                            # torneiras de saida e galoes
        p.seg('pvc', (1.29, 0.4, z), (1.42, 0.4, z), 0.03, 0.03)
        torno(p, 'latao_velho', [(0.0, 0.0), (0.015, 0.0), (0.015, 0.06), (0.0, 0.06)], 10, 'y', (1.44, 0.34, z)); p.cham('latao_velho', 1.4, 1.47, 0.42, 0.44, z - 0.005, z + 0.005, 0.002)
        p.cham('galao_azul', 1.3 + 0.0, 1.58, 0.0, 0.3, z - 0.11, z + 0.11, 0.02)
    p.cham('plastico_branco', -1.45, -1.25, 0.0, 0.3, 0.45, 0.65, 0.01)                                # balde de cloro (alcool/hipoclorito)


@item('muralha_concreto', 'Módulo de muralha de blocos com passarela', 'mobilias', 'defesa', comodos=['abrigo', 'cidade', 'rua'],
      constroi={'cimento': 4, 'tijolo': 20, 'cano_metal': 2, 'arame_farpado': 1, 'tabua': 4}, ferramenta='pa', fase=4, vida=3000, modulo_m=2,
      bloqueia='passagem e visao', atirar_por_cima=True, vagas=2, estacao='muralha (aguenta horda grande; moradores andam e atiram da passarela)')
def muralha_concreto(M):
    p = M.base; X, H, T = 1.0, 2.6, 0.2; rng = np.random.default_rng(19)
    p.cham('concreto', -X, X, -0.05, 0.12, -T / 2 - 0.08, T / 2 + 0.08, 0.01)                          # sapata
    for k, y in enumerate(np.arange(0.12, H, 0.2)):                                                  # blocos de concreto desencontrados
        off = 0.2 * (k % 2); xs_ = np.arange(-X - off, X, 0.4)
        for x in xs_:
            x0, x1 = max(x, -X) + 0.005, min(x + 0.4, X) - 0.005
            if x1 - x0 < 0.03: continue
            p.cham('concreto_bloco', x0, x1, y + 0.005, y + 0.195, -T / 2 + rng.uniform(-0.004, 0.004), T / 2, 0.006)
    p.cham('concreto', -X, X, H, H + 0.08, -T / 2 - 0.02, T / 2 + 0.02, 0.008)                         # cinta de topo
    for x in (-X + 0.15, 0.0, X - 0.15):                                                             # suporte em Y do arame farpado
        for s in (-1, 1): p.seg('aco', (x, H + 0.08, 0.0), (x, H + 0.5, s * 0.22), 0.025, 0.025)
    for s in (-1, 1):
        for y, z in ((H + 0.3, s * 0.13), (H + 0.45, s * 0.2)):
            p.add('aco', trimesh.creation.cylinder(radius=0.0025, segment=[(-X, y, z), (X, y, z)], sections=4))
            for x in np.arange(-X + 0.06, X, 0.12): p.seg('aco', (x - 0.012, y - 0.012, z), (x + 0.012, y + 0.012, z), 0.003, 0.003)
    for i, x in enumerate((-0.6, 0.6)):                                                              # passarela de tabua atras (lado -Z) com mao-francesa
        p.seg('madeira_escura', (x, 1.5, -T / 2 - 0.02), (x, 0.9, -T / 2 - 0.62), 0.08, 0.06)
        p.cham('madeira_escura', x - 0.04, x + 0.04, 1.46, 1.54, -T / 2 - 0.75, -T / 2, 0.004)
    for z in np.linspace(-T / 2 - 0.1, -T / 2 - 0.7, 4): p.cham('madeira', -X, X, 1.54, 1.58, z - 0.075, z + 0.075, 0.003)
    _estencil = 'tinta_branca'
    for k, x in enumerate((-0.8, -0.65, -0.5)): p.box(_estencil, x - 0.004, x + 0.004, 1.7, 2.0, T / 2 + 0.0005, T / 2 + 0.001)   # riscos de contagem pintados
    p.seg(_estencil, (-0.86, 1.75, T / 2 + 0.001), (-0.44, 1.95, T / 2 + 0.001), 0.008, 0.001)


@item('portao_guarita', 'Portão principal de chapa com guarita', 'mobilias', 'defesa', comodos=['abrigo', 'cidade', 'rua'],
      constroi={'chapa_metal': 8, 'cano_metal': 6, 'cimento': 6, 'tijolo': 20, 'dobradicas': 4, 'corrente_cadeado': 1, 'tabua': 6}, ferramenta='chave_inglesa',
      estacao_obra='forja_tambor', fase=4, vida=2500, modulo_m=4, bloqueia='passagem e visao', trabalha=1, ponto_uso=[2.7, 2.0, 0.0],
      estacao='portão (abre para carros e caravanas; o vigia da guarita vê a estrada e fecha o portão)')
def portao_guarita(M):
    p = M.base; W, H = 4.0, 2.6
    for xs in (-1, 1):                                                                               # pilares de concreto
        p.cham('concreto', xs * (W / 2) - 0.2 * (xs < 0) + 0.0, xs * (W / 2) + 0.2 * (xs > 0), 0.0, H + 0.3, -0.2, 0.2, 0.01)
        p.cham('concreto', xs * (W / 2) - 0.22 * (xs < 0) - 0.02 * (xs > 0), xs * (W / 2) + 0.22 * (xs > 0) + 0.02 * (xs < 0), H + 0.3, H + 0.38, -0.22, 0.22, 0.01)
    for xs in (-1, 1):                                                                               # duas folhas de chapa ondulada em quadro de cano
        q = M.parte('porta_esq' if xs < 0 else 'porta_dir', (xs * (W / 2 - 0.01), 0.05, 0.0), 'porta', eixo='y', abre_graus=-95 * xs * -1)
        x0, x1 = (0.02, W / 2 - 0.03) if xs < 0 else (-(W / 2 - 0.03), -0.02)
        for xx in (x0, x1): q.add('aco_pintado', trimesh.creation.cylinder(radius=0.025, segment=[(xx, 0.05, 0.0), (xx, H - 0.05, 0.0)], sections=10))
        for y in (0.05, H / 2, H - 0.05): q.add('aco_pintado', trimesh.creation.cylinder(radius=0.025, segment=[(x0, y, 0.0), (x1, y, 0.0)], sections=10))
        q.add('aco_pintado', trimesh.creation.cylinder(radius=0.018, segment=[(x0, 0.08, 0.0), (x1, H - 0.08, 0.0)] if xs < 0 else [(x1, 0.08, 0.0), (x0, H - 0.08, 0.0)], sections=8))
        xs_ = np.linspace(min(x0, x1), max(x0, x1), int(abs(x1 - x0) / 0.076 * 8)); a = 0.012
        top = [(x, a * math.cos(x * 2 * math.pi / 0.076)) for x in xs_]
        m = trimesh.creation.extrude_polygon(Polygon(top + [(x, y - 0.0015) for x, y in top[::-1]]).buffer(0), H - 0.2)
        m.vertices = np.stack([m.vertices[:, 0], m.vertices[:, 2] + 0.1, m.vertices[:, 1] + 0.04], 1)
        if m.volume < 0: m.invert()
        q.add('chapa_pintada', m)
        for y in (0.4, H - 0.4): q.cham('aco', (x0 if xs < 0 else x1) - 0.04, (x0 if xs < 0 else x1) + 0.04, y - 0.05, y + 0.05, -0.04, 0.04, 0.006)   # dobradicas
        if xs < 0:                                                                                   # trinco, corrente e cadeado na folha esquerda
            q.cham('aco', x1 - 0.2, x1 + 0.05, 1.2, 1.25, 0.04, 0.07, 0.004)
            for k in range(6):
                t = trimesh.creation.torus(0.018, 0.005, major_sections=10, minor_sections=6)
                t.apply_transform(_rot(math.pi / 2, [0, 1, 0]) if k % 2 else np.eye(4)); t.apply_translation([x1 - 0.02 + k * 0.025, 1.18 - 0.03 * (k % 3), 0.08]); q.add('aco', t)
            q.cham('latao_velho', x1 + 0.1, x1 + 0.15, 1.06, 1.12, 0.065, 0.09, 0.006)
        _mover(q, (xs * (W / 2 - 0.01), 0.05, 0.0))
    _placa('placa_portao', ['VILA RECOMEÇO', 'BUZINE E ESPERE'], 1024, 384, (30, 50, 30), (230, 220, 180), (110, 70))
    p.box('placa_portao', -1.2, 1.2, H + 0.42, H + 1.02, 0.02, 0.03); p.uv['placa_portao'] = _uv_frente(-1.2, 1.2, H + 0.42, H + 1.02)
    p.cham('madeira_escura', -1.25, 1.25, H + 0.38, H + 1.06, -0.0, 0.02, 0.006)
    for xs in (-1, 1): p.seg('aco', (xs * 1.15, H + 0.38, 0.01), (xs * (W / 2 - 0.1), H + 0.3, 0.0), 0.03, 0.03)
    gx = W / 2 + 0.9                                                                                 # guarita elevada a direita
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_escura', gx + xs * 0.6 - 0.05, gx + xs * 0.6 + 0.05, 0.0, 3.9, zs * 0.6 - 0.05, zs * 0.6 + 0.05, 0.004)
    p.cham('madeira', gx - 0.68, gx + 0.68, 1.95, 2.0, -0.68, 0.68, 0.004)                              # piso
    p.cham('madeira', gx - 0.68, gx + 0.68, 2.0, 2.9, -0.68, -0.66, 0.003)                                 # parede do fundo
    for xs in (-1, 1):
        for y in np.arange(2.0, 2.95, 0.15):
            if xs < 0 or y < 2.5: p.cham('madeira', gx + xs * 0.68 - 0.02 * (xs > 0), gx + xs * 0.68 + 0.02 * (xs < 0), y, y + 0.14, -0.66, 0.66, 0.003)
    for y in np.arange(2.0, 2.5, 0.15): p.cham('madeira', gx - 0.66, gx + 0.66, y, y + 0.14, 0.66, 0.68, 0.003)   # peitoril da frente
    _ondulada(p, 'telha_ondulada', gx - 0.8, gx + 0.8, -0.8, 0.8, 3.92, incl=0.2)
    for k in range(9): p.cham('madeira_crua', gx + 0.7, gx + 0.74, 0.1 + k * 0.21, 0.14 + k * 0.21, -0.25, 0.25, 0.003)   # escada
    for zs in (-1, 1): p.cham('madeira_escura', gx + 0.7, gx + 0.76, 0.0, 2.1, zs * 0.27 - 0.03, zs * 0.27 + 0.03, 0.003)
    p.sphere('vidro_holofote', 0.05, gx + 0.3, 3.0, 0.62, 1)   # lampiao do vigia


# ---------------------------------------------------------------------------- VIDA DE VILA
@item('banca_feira', 'Banca de feira com toldo', 'mobilias', 'cidade', comodos=['praca', 'rua', 'cidade'],
      constroi={'tabua': 6, 'lona': 1, 'lenha': 4, 'caixa_pregos': 1}, ferramenta='martelo', fase=4, trabalha=1, ponto_uso=[0.0, 0.0, -0.8],
      troca=True, moral=1, estacao='feira (moradores e caravanas trocam excedente: comida por munição, remédio por ferramenta)')
def banca_feira(M):
    p = M.base; L, W, H = 2.0, 0.8, 0.85; rng = np.random.default_rng(23)
    for xs in (-1, 1):
        _cavalete(p, xs * 0.7, H - 0.03, 0.3, 'madeira_escura')
    for z in np.linspace(-W / 2 + 0.1, W / 2 - 0.1, 4): p.cham('madeira', -L / 2, L / 2, H - 0.03, H, z - 0.095, z + 0.095, 0.003)
    for xs in (-1, 1):                                                                               # postes e toldo listrado inclinado
        for zs in (-1, 1): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.03, segment=[(xs * (L / 2 + 0.05), 0.0, zs * (W / 2 + 0.1)), (xs * (L / 2 + 0.05), 2.05 + 0.25 * (zs < 0), zs * (W / 2 + 0.1))], sections=8))
    q = P()
    for i in range(10):
        x0, x1 = -L / 2 - 0.12 + i * (L + 0.24) / 10, -L / 2 - 0.12 + (i + 1) * (L + 0.24) / 10
        q.hull('lona_listrada' if i % 2 else 'lona_crua', [(x, y + d, z) for x in (x0, x1) for (y, z) in ((2.33, -W / 2 - 0.25), (2.02, W / 2 + 0.35)) for d in (0.0, 0.006)])
    for i in range(10):                                                                              # franja recortada na frente
        x0, x1 = -L / 2 - 0.12 + i * (L + 0.24) / 10, -L / 2 - 0.12 + (i + 1) * (L + 0.24) / 10
        q.hull('lona_listrada' if i % 2 else 'lona_crua', [(x0, 2.02, W / 2 + 0.35), (x1, 2.02, W / 2 + 0.35), ((x0 + x1) / 2, 1.9, W / 2 + 0.36), (x0, 2.02, W / 2 + 0.354), (x1, 2.02, W / 2 + 0.354)])
    p.merge(q)
    for k, (x, cor) in enumerate(((-0.65, 'tomate'), (-0.2, 'laranja'), (0.25, 'cenoura'), (0.7, 'alface'))):   # caixotes inclinados com produtos
        c = P()
        for zs in (-1, 1): c.cham('madeira_crua', -0.2, 0.2, 0.0, 0.14, zs * 0.15 - 0.012 * (zs > 0), zs * 0.15 + 0.012 * (zs < 0), 0.002)
        for xs in (-1, 1): c.cham('madeira_crua', xs * 0.2 - 0.012 * (xs > 0), xs * 0.2 + 0.012 * (xs < 0), 0.0, 0.16, -0.15, 0.15, 0.002)
        c.box('madeira_crua', -0.19, 0.19, 0.0, 0.01, -0.14, 0.14)
        for j in range(14):
            if cor in ('tomate', 'laranja'): c.sphere(cor, 0.032, rng.uniform(-0.15, 0.15), 0.1 + rng.uniform(0, 0.05), rng.uniform(-0.1, 0.1), 1)
            elif cor == 'cenoura': c.add(cor, trimesh.creation.cone(radius=0.016, height=0.15, sections=8, transform=_alinha((rng.uniform(-0.12, 0.12), 0.12, rng.uniform(-0.1, 0.1)), np.array([rng.uniform(-1, 1), 0.2, rng.uniform(-0.3, 0.3)]))))
            elif j < 6: fofo(c, cor, rng.uniform(-0.11, 0.11), 0.12, rng.uniform(-0.08, 0.08), 0.07, 0.05, 0.06, 0.5, 0.4, (6, 8))
        p.merge(c, trimesh.transformations.translation_matrix([x, H, 0.1]) @ _rot(0.25, [1, 0, 0]))
    torno(p, 'aco_pintado', [(0.0, 0.0), (0.12, 0.0), (0.13, 0.02), (0.0, 0.02)], 20, 'y', (0.4, H, -0.28))  # balanca de prato
    p.cham('tinta_vermelha', 0.32, 0.48, H, H + 0.14, -0.38, -0.2, 0.01); torno(p, 'aco_polido', [(0.0, 0.14), (0.17, 0.15), (0.0, 0.17)], 20, 'y', (0.4, H, -0.28))
    _placa('lousa_feira', ['HOJE', '3 TOMATES = 1 BALA', 'PÃO NA TROCA'], 512, 384, (24, 32, 28), (230, 230, 220), (80, 46))
    xl = L / 2 + 0.55                                                                                # cavalete da lousa ao lado da banca
    p.box('lousa_feira', xl - 0.35, xl + 0.35, 0.95, 1.45, W / 2 + 0.12, W / 2 + 0.125); p.uv['lousa_feira'] = _uv_frente(xl - 0.35, xl + 0.35, 0.95, 1.45)
    p.cham('madeira_escura', xl - 0.38, xl + 0.38, 0.92, 1.48, W / 2 + 0.1, W / 2 + 0.12, 0.004)
    for s in (-1, 1): p.seg('madeira_escura', (xl + s * 0.3, 0.0, W / 2 + 0.45), (xl + s * 0.3, 1.0, W / 2 + 0.12), 0.04, 0.03)


@item('ponto_onibus', 'Ponto da caravana (abrigo de ônibus reformado)', 'mobilias', 'cidade', comodos=['rua', 'cidade'],
      constroi={'cano_metal': 4, 'chapa_metal': 2, 'tabua': 4}, ferramenta='chave_inglesa', fase=5, troca=True, sentar=3,
      estacao='ponto da caravana (a carroça e o ônibus da vila passam aqui: leva moradores e traz comércio de outras comunidades)')
def ponto_onibus(M):
    p = M.base; L, D, H = 2.6, 1.1, 2.4
    for x in (-L / 2 + 0.05, L / 2 - 0.05):                                                          # 4 colunas
        for z in (-D / 2 + 0.05, D / 2 - 0.05): p.cham('aco_pintado', x - 0.04, x + 0.04, 0.0, H - (0.0 if z < 0 else 0.12), z - 0.04, z + 0.04, 0.006)
    _ondulada(p, 'chapa_galv', -L / 2 - 0.1, L / 2 + 0.1, -D / 2 - 0.1, D / 2 + 0.25, H - 0.02, incl=0.0)
    q = P(); q.hull('aco_pintado', [(x, y, z) for x in (-L / 2 - 0.1, L / 2 + 0.1) for (y, z) in ((H, -D / 2 - 0.1), (H - 0.12, D / 2 + 0.25), (H - 0.06, -D / 2 - 0.1), (H - 0.16, D / 2 + 0.25))])
    p.merge(q)
    for x0, x1 in ((-L / 2 + 0.09, -0.4), (-0.4, 0.3), (0.3, L / 2 - 0.09)):                         # fundo: um vidro inteiro, um quebrado tapado com tabua, um vazio
        p.cham('aco_pintado', x0, x1, 0.3, 0.34, -D / 2 + 0.02, -D / 2 + 0.08, 0.004); p.cham('aco_pintado', x0, x1, H - 0.22, H - 0.18, -D / 2 + 0.02, -D / 2 + 0.08, 0.004)
    p.box('vidro_prateleira', -L / 2 + 0.09, -0.4, 0.34, H - 0.22, -D / 2 + 0.048, -D / 2 + 0.054)
    for y in np.arange(0.36, H - 0.25, 0.2): p.cham('madeira_crua', -0.38, 0.28, y, y + 0.18, -D / 2 + 0.06, -D / 2 + 0.08, 0.003)
    _placa('horario_caravana', ['CARAVANA', 'SEG · QUA · SÁB', 'SAI 7h  VOLTA 17h', 'IGREJA › FAZENDA › PORTO'], 512, 640, (232, 228, 214), (30, 30, 30), (90, 56, 48, 40))
    p.box('horario_caravana', 0.45, 1.05, 0.9, 1.65, -D / 2 + 0.081, -D / 2 + 0.084); p.uv['horario_caravana'] = _uv_frente(0.45, 1.05, 0.9, 1.65)
    p.cham('madeira_escura', 0.42, 1.08, 0.87, 1.68, -D / 2 + 0.06, -D / 2 + 0.081, 0.004)
    for x in (-0.8, 0.8): p.cham('aco_pintado', x - 0.03, x + 0.03, 0.0, 0.45, -D / 2 + 0.15, -D / 2 + 0.35, 0.004)   # banco de ripas
    for z in np.linspace(-D / 2 + 0.15, -D / 2 + 0.38, 3): p.cham('madeira', -1.05, 1.05, 0.45, 0.48, z - 0.035, z + 0.035, 0.003)
    p.add('aco_pintado', trimesh.creation.cylinder(radius=0.03, segment=[(L / 2 + 0.35, 0.0, D / 2), (L / 2 + 0.35, 2.7, D / 2)], sections=10))   # placa do ponto
    _placa('placa_ponto', ['P'], 256, 256, (20, 60, 140), (240, 240, 240), (200,))
    p.cham('aco_pintado', L / 2 + 0.17, L / 2 + 0.53, 2.25, 2.61, D / 2 + 0.03, D / 2 + 0.045, 0.004)
    p.box('placa_ponto', L / 2 + 0.19, L / 2 + 0.51, 2.27, 2.59, D / 2 + 0.045, D / 2 + 0.048); p.uv['placa_ponto'] = _uv_frente(L / 2 + 0.19, L / 2 + 0.51, 2.27, 2.59)
    fofo(p, 'mala_azul', -0.6, 0.56, -D / 2 + 0.27, 0.2, 0.1, 0.12, 0.2, 0.2, (8, 10))                  # trouxa esperando a caravana


@item('forno_comunitario', 'Forno de barro comunitário', 'mobilias', 'cidade', comodos=['praca', 'abrigo', 'fazenda', 'padaria'],
      constroi={'tijolo': 30, 'terra': 8, 'palha': 2, 'cano_metal': 1}, ferramenta='pa', fase=4, trabalha=1, ponto_uso=[0.0, 0.0, 1.3], moral=1,
      produz={'item': 'pao_caseiro', 'qtd': 12, 'a_cada_min': 120, 'consome': {'saco_farinha': 1, 'lenha': 2}},
      estacao='padaria da vila (12 pães por fornada com 1 saco de farinha; dia de pão levanta o moral)')
def forno_comunitario(M):
    p = M.base; X, Z, H0 = 0.85, 0.85, 0.85
    for k, y in enumerate(np.arange(0.0, H0, 0.085)):                                                 # base de tijolo
        for s, (a0, a1, b0, b1) in enumerate(((-X, X, Z - 0.11, Z), (-X, X, -Z, -Z + 0.11), (-X, -X + 0.11, -Z + 0.11, Z - 0.11), (X - 0.11, X, -Z + 0.11, Z - 0.11))):
            ln = (a1 - a0) if s < 2 else (b1 - b0); n = max(1, int(ln / 0.22)); off = 0.11 * (k % 2)
            for i in range(n + 1):
                t0 = -off + i * ln / n; t1 = t0 + ln / n
                t0, t1 = max(t0, 0.0), min(t1, ln)
                if t1 - t0 < 0.03: continue
                if s < 2: p.cham('tijolo', a0 + t0 + 0.004, a0 + t1 - 0.004, y + 0.004, y + 0.08, b0, b1, 0.004)
                else: p.cham('tijolo', a0, a1, y + 0.004, y + 0.08, b0 + t0 + 0.004, b0 + t1 - 0.004, 0.004)
    p.cham('madeira_escura', -X + 0.11, X - 0.11, 0.3, 0.34, -Z + 0.11, Z - 0.11, 0.004)                  # vao de lenha embaixo
    for k in range(9): p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.045, segment=[(-0.5 + (k % 5) * 0.2 + 0.1 * (k // 5), 0.39 + 0.08 * (k // 5), Z - 0.1), (-0.5 + (k % 5) * 0.2 + 0.1 * (k // 5), 0.39 + 0.08 * (k // 5), -Z + 0.2)], sections=8))
    p.cham('concreto', -X - 0.03, X + 0.03, H0, H0 + 0.08, -Z - 0.03, Z + 0.03, 0.01)                     # laje
    R = 0.72; Hd = 0.62                                                                               # cupula de barro
    torno(p, 'barro_cru', [(R * math.cos(t), H0 + 0.08 + Hd * math.sin(t)) for t in np.linspace(0, math.pi / 2, 12)], 32, 'y', (0, 0, -0.05))
    _amassar(p, 'barro_cru', 0.008, 8.0, 3, sub=1)
    boca = Polygon([(0.24 * math.cos(t), 0.26 * math.sin(t)) for t in np.linspace(0, math.pi, 16)] + [(-0.24, 0.0)]).buffer(0)
    m = trimesh.creation.extrude_polygon(boca, 0.04); m.apply_translation([0, H0 + 0.08, 0.62]); p.add('fuligem', m)   # boca escurecida
    m = trimesh.creation.extrude_polygon(boca.buffer(0.05).difference(boca), 0.06); m.apply_translation([0, H0 + 0.08, 0.6]); p.add('tijolo', m)  # arco de tijolo
    fofo(p, 'brasa', 0.0, H0 + 0.1, 0.35, 0.16, 0.03, 0.12, 0.5, 0.5, (8, 10))
    torno(p, 'barro_cru', [(0.1, H0 + 0.5), (0.1, H0 + 1.0), (0.12, H0 + 1.02), (0.0, H0 + 1.02)], 14, 'y', (0.0, 0, -0.35))   # chamine
    p.add('madeira_crua', trimesh.creation.cylinder(radius=0.02, segment=[(X + 0.05, 1.55, 0.25), (X + 0.4, 0.32, 0.25)], sections=8))   # pa de forno encostada
    p.hull('madeira_crua', [(X + 0.4 + dx, y, 0.25 + dz) for dz in (-0.17, 0.17) for (dx, y) in ((0.0, 0.32), (0.09, 0.0))] + [(X + 0.415 + dx, y, 0.25 + dz) for dz in (-0.17, 0.17) for (dx, y) in ((0.0, 0.32), (0.09, 0.0))])
    for k in range(5): p.merge(_pao(), trimesh.transformations.translation_matrix([-0.6 + k * 0.13, H0 + 0.08, 0.72]))   # paes esfriando na laje


def _pao():
    q = P(); fofo(q, 'pao_casca', 0.0, 0.035, 0.0, 0.055, 0.04, 0.09, 0.4, 0.4, (10, 12))
    for k in range(3): q.box('pao', -0.04, 0.04, 0.07, 0.074, -0.05 + k * 0.04, -0.044 + k * 0.04)   # cortes no topo
    return q


@item('placa_boas_vindas', 'Placa de boas-vindas da vila', 'mobilias', 'cidade', comodos=['rua', 'cidade'],
      constroi={'tabua': 8, 'lenha': 2, 'caixa_pregos': 1}, ferramenta='martelo', fase=4, moral=1,
      estacao='entrada da vila (sobreviventes que chegam sabem que ali tem gente; a população se atualiza sozinha)')
def placa_boas_vindas(M):
    p = M.base; L, H0, H1 = 2.6, 0.9, 2.0
    for x in (-L / 2 + 0.15, L / 2 - 0.15):
        p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.07, segment=[(x, 0.0, 0.0), (x, H1 + 0.25, 0.0)], sections=12))
        torno(p, 'madeira_crua', [(0.0, H1 + 0.25), (0.07, H1 + 0.25), (0.0, H1 + 0.35)], 12, 'y', (x, 0, 0))
    _placa('placa_vila', ['BEM-VINDO À', 'VILA RECOMEÇO', 'FUNDADA NO ANO 1 · POP. 47'], 1024, 448, (200, 186, 140), (60, 30, 20), (64, 120, 46))
    for k, y in enumerate(np.arange(H0, H1, 0.2)): p.cham('madeira', -L / 2, L / 2, y + 0.005, y + 0.195, 0.07, 0.1, 0.004)
    p.box('placa_vila', -L / 2 + 0.05, L / 2 - 0.05, H0 + 0.02, H1 - 0.02, 0.1005, 0.101); p.uv['placa_vila'] = _uv_frente(-L / 2 + 0.05, L / 2 - 0.05, H0 + 0.02, H1 - 0.02)
    p.cham('madeira_escura', -L / 2 - 0.05, L / 2 + 0.05, H1, H1 + 0.06, 0.05, 0.13, 0.004)
    p.cham('madeira_escura', -L / 2 - 0.05, L / 2 + 0.05, H0 - 0.06, H0, 0.05, 0.13, 0.004)
    q = P(); q.cham('madeira_crua', -0.32, 0.32, 0.0, 0.16, 0.0, 0.025, 0.003)                            # tabuinha da populacao pendurada
    _placa('placa_pop', ['47'], 256, 128, (220, 210, 170), (120, 20, 10), (100,))
    q.box('placa_pop', -0.1, 0.1, 0.02, 0.14, 0.0251, 0.0255)
    for s in (-1, 1): q.add('corda', trimesh.creation.cylinder(radius=0.004, segment=[(s * 0.25, 0.16, 0.012), (s * 0.25, 0.33, 0.012)], sections=5))
    p.merge(q, trimesh.transformations.translation_matrix([0.7, H0 - 0.4, 0.1])); p.uv['placa_pop'] = _uv_frente(0.6, 0.8, H0 - 0.38, H0 - 0.26)
    rng = np.random.default_rng(8)                                                                   # canteiro de pedras com flores
    for k in range(14):
        a = k * 2 * math.pi / 14; fofo(p, 'pedra', 1.4 * math.cos(a) * 0.9, 0.05, 0.55 + 0.35 * math.sin(a), 0.08, 0.06, 0.07, 0.3, 0.3, (6, 8))
    p.hull('terra', [(x * 1.2, 0.0, 0.55 + z * 0.3) for x in (-1, 1) for z in (-1, 1)] + [(x * 1.05, 0.07, 0.55 + z * 0.22) for x in (-1, 1) for z in (-1, 1)])
    for k in range(22):
        x, z = rng.uniform(-1.0, 1.0), 0.55 + rng.uniform(-0.2, 0.2); h = rng.uniform(0.15, 0.3)
        p.seg('muda', (x, 0.06, z), (x, 0.06 + h, z), 0.006, 0.006)
        p.sphere('flor_amarela' if k % 3 else 'flor_vermelha', 0.025, x, 0.06 + h, z, 1)
        fofo(p, 'muda', x + 0.02, 0.06 + h * 0.4, z, 0.03, 0.008, 0.015, 0.5, 0.5, (5, 6))


@item('memorial', 'Memorial aos que se foram', 'mobilias', 'cidade', comodos=['praca', 'igreja', 'abrigo', 'cidade'],
      constroi={'tabua': 6, 'pedras': 10, 'vela_fosforos': 2}, ferramenta='martelo', fase=4, moral=3, raio_m=30,
      estacao='memorial (moradores visitam e o luto passa mais rápido; quem morre na vila ganha um nome aqui)')
def memorial(M):
    p = M.base; L, H = 1.8, 1.7; rng = np.random.default_rng(31)
    p.cham('pedra_escura', -L / 2 - 0.15, L / 2 + 0.15, 0.0, 0.25, -0.35, 0.25, 0.02)                    # base de pedra
    for k in range(10): fofo(p, 'pedra', rng.uniform(-L / 2, L / 2), 0.05, rng.uniform(0.3, 0.5), 0.09, 0.06, 0.08, 0.3, 0.3, (6, 8))
    for x in (-L / 2 + 0.06, L / 2 - 0.06): p.cham('madeira_escura', x - 0.06, x + 0.06, 0.25, H + 0.35, -0.3, -0.18, 0.006)
    for y in np.arange(0.35, H, 0.2): p.cham('madeira', -L / 2, L / 2, y + 0.005, y + 0.195, -0.18, -0.15, 0.003)   # painel de tabuas
    p.hull('madeira_escura', [(x, y, z) for x in (-L / 2 - 0.12, L / 2 + 0.12) for (y, z) in ((H + 0.3, -0.24), (H + 0.42, -0.24), (H + 0.3, -0.04), (H + 0.33, -0.04))])  # telhadinho
    nomes = ['ANA', 'SEU JORGE', 'TIÃO', 'MARIA C.', 'DUDU', 'IRMÃ LÚCIA', 'PEDRO', 'DONA ZÉLIA', 'RAFA', 'BETO', 'LIA', 'CABO SOUZA']
    img = Image.new('RGB', (1024, 768), (150, 110, 70)); d = ImageDraw.Draw(img)
    texto_c(d, (512, 70), 'NÃO ESQUECEMOS', 80, (240, 236, 220), larg=980)
    for i, nmx in enumerate(nomes): texto_c(d, (256 + 512 * (i % 2), 190 + 90 * (i // 2)), nmx, 54, (245, 240, 225), larg=460)
    mat_imagem('nomes_memorial', img, 0.85)
    p.box('nomes_memorial', -L / 2 + 0.05, L / 2 - 0.05, 0.4, H - 0.05, -0.149, -0.147); p.uv['nomes_memorial'] = _uv_frente(-L / 2 + 0.05, L / 2 - 0.05, 0.4, H - 0.05)
    for k in range(7):                                                                               # fotos presas com prego
        x, y = rng.uniform(-L / 2 + 0.2, L / 2 - 0.2), rng.uniform(0.5, H - 0.2); a = rng.uniform(-0.2, 0.2)
        q = P(); q.box('papel', -0.06, 0.06, -0.08, 0.08, 0.0, 0.002); q.box('cartela' if k % 2 else 'revista_capa', -0.05, 0.05, -0.06, 0.07, 0.002, 0.0025)
        p.merge(q, trimesh.transformations.translation_matrix([x, y, -0.146]) @ _rot(a, [0, 0, 1]))
    for k in range(9):                                                                               # velas acesas e flores no degrau
        x = -L / 2 + 0.15 + k * (L - 0.3) / 8; hh = rng.uniform(0.06, 0.16)
        torno(p, 'vela', [(0.0, 0.25), (0.022, 0.25), (0.022, 0.25 + hh), (0.0, 0.25 + hh + 0.004)], 12, 'y', (x, 0, 0.05 + 0.08 * (k % 2)))
        torno(p, 'chama_vela', [(0.0, 0.0), (0.01, 0.012), (0.0, 0.04)], 8, 'y', (x, 0.25 + hh + 0.006, 0.05 + 0.08 * (k % 2)))
    for k in range(3):
        x = rng.uniform(-0.6, 0.6)
        for j in range(5):
            a = rng.uniform(-0.5, 0.5); p.seg('muda', (x, 0.26, 0.15), (x + 0.25 * math.sin(a), 0.3, 0.15 + 0.25 * math.cos(a)), 0.006, 0.006)
            p.sphere('flor_vermelha' if (j + k) % 2 else 'flor_amarela', 0.03, x + 0.27 * math.sin(a), 0.3, 0.15 + 0.27 * math.cos(a), 1)
    for x in (-L / 2 - 0.4, L / 2 + 0.4):                                                            # duas cruzes de galho
        p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.025, segment=[(x, 0.0, -0.1), (x, 1.0, -0.1)], sections=8))
        p.add('madeira_lenha', trimesh.creation.cylinder(radius=0.02, segment=[(x - 0.22, 0.72, -0.1), (x + 0.22, 0.72, -0.1)], sections=8))
        _torcido(p, 'corda', [(x - 0.03, 0.7, -0.07), (x + 0.03, 0.74, -0.07), (x - 0.03, 0.74, -0.07)], 0.004)


# ---------------------------------------------------------------------------- LOOT
@item('pao_caseiro', 'Pão caseiro do forno da vila', 'loot', 'comida', recurso='comida', valor=3, peso_kg=0.4, empilha=6, celulas=[1, 1], fase=4,
      efeito='mata a fome e dá +moral; dura 4 dias', onde=['padaria', 'fazenda'], obtem_de=[{'fazer': 'forno_comunitario', 'qtd': 12}])
def pao_caseiro(M):
    M.base.merge(_pao())
