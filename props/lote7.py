# Lote 7: ambientacao, vida de antes do surto. Executado por gerar_props.py (mesmas funcoes e materiais).
CORES.update({'pelucia': (150, 104, 62), 'pelucia_clara': (214, 186, 150), 'terra_vaso': (60, 42, 30), 'terracota': (150, 70, 40),
              'folha_seca': (110, 86, 40), 'tela_tv': (14, 18, 20), 'madeira_tv': (80, 50, 30), 'tapete': (120, 40, 36),
              'abajur_cupula': (226, 210, 170), 'disco': (12, 12, 12), 'fruta_podre': (80, 64, 28), 'banana_podre': (70, 50, 20),
              'casinha': (80, 14, 9), 'telha_casinha': (60, 60, 64)})
METALICOS.update({'disco': (0.2, 0.25)})
FOSCOS.update({'tela_tv': 0.12, 'abajur_cupula': 0.9, 'fruta_podre': 0.7, 'banana_podre': 0.75, 'terracota': 0.85})
TEX_PROPRIAS += [('pelucia', 'tecido', 0.25, 1024), ('pelucia_clara', 'tecido', 0.25, 1024), ('tapete', 'tecido', 0.5, 768),
                 ('terra_vaso', 'papelao', 0.5, 512), ('abajur_cupula', 'tecido', 0.25, 1024)]
ANTES = dict(ambiente=True, colisao='nenhuma')


def _foto_familia(seed, w=300, h=220, gente=3):
    rng = np.random.default_rng(seed); im = Image.new('RGB', (w, h), (120, 170, 210)); d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.62), w, h], fill=(90, 140, 70))
    d.ellipse([w * 0.7, h * 0.08, w * 0.85, h * 0.28], fill=(250, 230, 150))
    for k in range(gente):
        x = w * (0.2 + 0.6 * k / max(1, gente - 1)); s = rng.uniform(0.7, 1.0) if k else 1.0; c = tuple(int(v) for v in rng.integers(40, 220, 3))
        d.ellipse([x - 40 * s, h * 0.45, x + 40 * s, h * 0.95], fill=c)
        d.ellipse([x - 20 * s, h * 0.45 - 50 * s, x + 20 * s, h * 0.45 - 8 * s], fill=(230, 196, 160))
    for _ in range(300): x, y = rng.uniform(0, w), rng.uniform(0, h); d.point((x, y), fill=(255, 250, 230))
    return im


@item('porta_retrato', 'Porta-retrato de família', 'loot', 'lembrancas', recurso='lembranca', valor=1, peso_kg=0.3, empilha=1,
      onde=['casas', 'motel', 'escritorio'], efeito='ânimo +5 se guardado; pode identificar um sobrevivente procurado (mural)')
def porta_retrato(M):
    p = M.base; X, Z = 0.09, 0.07
    mat_imagem('foto_retrato', _foto_familia(51), 0.4)
    p.cham('madeira_escura', -X, X, 0, 0.02, -Z, Z, 0.004)                                      # deitado (caiu de bruços? não: de costas)
    p.box('foto_retrato', -X + 0.018, X - 0.018, 0.0195, 0.0205, -Z + 0.018, Z - 0.018); p.uv['foto_retrato'] = uv_plano(-X + 0.018, X - 0.018, -Z + 0.018, Z - 0.018)
    p.box('vidro_caco', -X + 0.015, -0.01, 0.021, 0.0215, -Z + 0.015, Z - 0.015)
    for i, (a, b) in enumerate((((-0.01, -0.06), (0.03, 0.01)), ((0.03, 0.01), (0.07, 0.05)), ((0.03, 0.01), (0.0, 0.06)))):
        p.seg('vidro_caco', (a[0], 0.0216, a[1]), (b[0], 0.0216, b[1]), 0.0012, 0.0004)
    p.box('vidro_caco', 0.0, X - 0.015, 0.021, 0.0213, -Z + 0.015, -0.01)


@item('quadro_familia', 'Quadro de família na parede', 'mobilias', 'lembrancas', montagem='wall', altura_sugerida_m=1.4, comodos=['sala', 'quarto', 'casas'], **ANTES)
def quadro_familia(M):
    p = M.base; W, H = 0.6, 0.45
    mat_imagem('foto_quadro', _foto_familia(52, 400, 300, 4), 0.4)
    prof_x(p, 'madeira', -W / 2, W / 2, [(0.0, 0.0), (0.035, 0.0), (0.035, 0.012), (0.02, 0.03), (0.0, 0.03)]) if False else None
    for (x0, x1, y0, y1) in ((-W / 2, W / 2, 0, 0.04), (-W / 2, W / 2, H - 0.04, H), (-W / 2, -W / 2 + 0.04, 0, H), (W / 2 - 0.04, W / 2, 0, H)):
        p.cham('madeira', x0, x1, y0, y1, 0.0, 0.03, 0.008)
    p.box('papel', -W / 2 + 0.04, W / 2 - 0.04, 0.04, H - 0.04, 0.0, 0.012)
    p.box('foto_quadro', -W / 2 + 0.08, W / 2 - 0.08, 0.08, H - 0.08, 0.012, 0.013)
    p.uv['foto_quadro'] = lambda v, n: np.stack([(v[:, 0] + W / 2 - 0.08) / (W - 0.16), (v[:, 1] - 0.08) / (H - 0.16)], 1)
    for k in range(3): p.box('esmalte_escuro', -0.2 + k * 0.17, -0.12 + k * 0.17, H - 0.003, H, 0.0, 0.03)   # poeira no topo


@item('ursinho', 'Ursinho de pelúcia', 'loot', 'lembrancas', recurso='lembranca', valor=1, peso_kg=0.25, empilha=1,
      onde=['casas', 'escolinha', 'clinica', 'motel'], efeito='acalma uma criança sobrevivente (moral +10)')
def ursinho(M):
    p = M.base; c, cl = 'pelucia', 'pelucia_clara'
    fofo(p, c, 0, 0.075, 0, 0.075, 0.075, 0.065, 0.8, 0.8, (16, 20))                          # corpo sentado
    fofo(p, cl, 0, 0.08, 0.05, 0.045, 0.05, 0.02, 0.8, 0.8, (12, 14))
    fofo(p, c, 0, 0.19, 0.0, 0.058, 0.055, 0.052, 0.8, 0.8, (16, 20))                          # cabeça
    fofo(p, cl, 0, 0.18, 0.05, 0.028, 0.022, 0.02, 0.8, 0.8, (10, 12))
    p.sphere('esmalte_escuro', 0.008, 0, 0.19, 0.068, 1)
    for xs in (-1, 1):
        p.sphere('esmalte_escuro', 0.007, xs * 0.022, 0.205, 0.048, 1)
        fofo(p, c, xs * 0.042, 0.24, -0.005, 0.02, 0.02, 0.012, 0.8, 0.8, (10, 12)); fofo(p, cl, xs * 0.042, 0.24, 0.004, 0.012, 0.012, 0.005, 0.8, 0.8, (8, 10))
        fofo(p, c, xs * 0.075, 0.1, 0.03, 0.025, 0.045, 0.025, 0.8, 0.8, (10, 12), rot_x=0.4)
        fofo(p, c, xs * 0.045, 0.03, 0.07, 0.03, 0.028, 0.045, 0.8, 0.8, (10, 12))
        fofo(p, cl, xs * 0.045, 0.03, 0.115, 0.022, 0.022, 0.005, 0.8, 0.8, (8, 10))
    p.cham('tinta_vermelha', -0.04, 0.04, 0.135, 0.15, 0.045, 0.06, 0.003)                      # laço


@item('bola_futebol', 'Bola de futebol murcha', 'mobilias', 'lembrancas', comodos=['quintal', 'rua', 'escolinha', 'casas'], portatil=True, peso_kg=0.4, **ANTES)
def bola_futebol(M):
    p = M.base; ico = trimesh.creation.icosphere(subdivisions=2, radius=0.11); ico.vertices[:, 1] *= 0.86
    ico.apply_translation([0, 0.095, 0]); fc = ico.triangles_center; lab = np.where(np.abs(fc[:, 1] - 0.095 - 0.0) > 0.07, 1, 0)
    rng = np.random.default_rng(2); preto = rng.random(len(fc)) < 0.0
    pent = trimesh.creation.icosphere(subdivisions=0, radius=1).vertices
    escuro = np.array([np.max(np.dot(pent, (c - [0, 0.095, 0]) / np.linalg.norm(c - [0, 0.095, 0]))) > 0.94 for c in fc])
    for mt, mask in (('esmalte', ~escuro), ('esmalte_escuro', escuro)):
        sub = ico.submesh([np.where(mask)[0]], append=True); p.add(mt, sub)


@item('casinha_cachorro', 'Casinha de cachorro vazia', 'mobilias', 'lembrancas', comodos=['quintal', 'casas', 'fazenda'], colisao='caixa', ambiente=True,
      abrigo_pequeno='cabe 1 sobrevivente agachado (esconderijo)')
def casinha_cachorro(M):
    p = M.base; X, Z, H = 0.45, 0.55, 0.6; m = 'casinha'
    p.cham('madeira_crua', -X, X, 0, 0.05, -Z, Z, 0.006)
    for k in range(9):                                                                        # tabuas horizontais
        y = 0.05 + k * 0.062
        p.cham(m, -X, X, y, y + 0.062, -Z, -Z + 0.02, 0.003); p.cham(m, -X, -X + 0.02, y, y + 0.062, -Z, Z, 0.003); p.cham(m, X - 0.02, X, y, y + 0.062, -Z, Z, 0.003)
        porta = abs(0) < 0.2 and y < 0.45
        if porta:
            p.cham(m, -X, -0.18, y, y + 0.062, Z - 0.02, Z, 0.003); p.cham(m, 0.18, X, y, y + 0.062, Z - 0.02, Z, 0.003)
        else: p.cham(m, -X, X, y, y + 0.062, Z - 0.02, Z, 0.003)
    for zs in (-1, 1):                                                                        # oitão
        p.hull(m, [(-X, H - 0.05, zs * Z), (X, H - 0.05, zs * Z), (0, H + 0.33, zs * Z), (-X, H - 0.05, zs * (Z - 0.02)), (X, H - 0.05, zs * (Z - 0.02)), (0, H + 0.33, zs * (Z - 0.02))])
    for xs in (-1, 1):                                                                        # telhado de duas aguas com ripas
        e0, e1 = (xs * (X + 0.1), H - 0.12), (0.0, H + 0.36)
        p.hull('telha_casinha', [(e0[0], e0[1], z) for z in (-Z - 0.08, Z + 0.08)] + [(e1[0], e1[1], z) for z in (-Z - 0.08, Z + 0.08)] +
               [(e0[0], e0[1] + 0.025, z) for z in (-Z - 0.08, Z + 0.08)] + [(e1[0], e1[1] + 0.025, z) for z in (-Z - 0.08, Z + 0.08)])
        for k in range(1, 6):
            f_ = k / 6; x = e0[0] * (1 - f_); y = e0[1] + (e1[1] - e0[1]) * f_ + 0.025
            p.box('telha_casinha', x - 0.015, x + 0.015, y - 0.004, y + 0.012, -Z - 0.08, Z + 0.08)
    fofo(p, 'cobertor_cinza', 0, 0.07, -0.05, 0.32, 0.025, 0.35, 0.6, 0.5, (10, 16))
    varrer(p, 'tinta_vermelha', Polygon([(-0.003, -0.01), (0.003, -0.01), (0.003, 0.01), (-0.003, 0.01)]),
           [(0.55 + 0.08 * math.cos(a), 0.012, 0.4 + 0.08 * math.sin(a)) for a in np.linspace(0, 2 * math.pi * 0.95, 20)])        # coleira
    torno(p, 'aco', [(0.09, 0.0), (0.1, 0.05), (0.085, 0.05), (0.075, 0.008), (0.0, 0.008)], 28, 'y', (-0.6, 0, 0.45), fechar=False)  # vasilha vazia
    torno(p, 'aco', [(0.0, 0.0), (0.09, 0.0)], 28, 'y', (-0.6, 0, 0.45))


@item('vaso_planta_morta', 'Vaso com planta morta', 'mobilias', 'lembrancas', comodos=['sala', 'casas', 'escritorio', 'galeria', 'hotel'], colisao='caixa', ambiente=True,
      desmonta={'terra': 1})
def vaso_planta_morta(M):
    p = M.base; rng = np.random.default_rng(71)
    torno(p, 'terracota', [(0.12, 0.0), (0.13, 0.02), (0.16, 0.3), (0.175, 0.31), (0.175, 0.35), (0.16, 0.355), (0.15, 0.33)], 32, fechar=False)
    torno(p, 'terracota', [(0.0, 0.0), (0.12, 0.0)], 32); torno(p, 'terra_vaso', [(0.0, 0.31), (0.155, 0.31)], 32)
    for k in range(9):                                                                        # galhos secos
        a = k / 9 * 2 * math.pi; L = rng.uniform(0.25, 0.55); t = rng.uniform(0.15, 0.5)
        a0 = np.array([0.02 * math.cos(a), 0.31, 0.02 * math.sin(a)]); a1 = a0 + [L * t * math.cos(a), L, L * t * math.sin(a)]
        p.seg('madeira_escura', a0, a1, 0.008)
        for j in range(3):
            q0 = a0 + (a1 - a0) * (0.4 + 0.2 * j); q1 = q0 + [rng.uniform(-0.08, 0.08), rng.uniform(0.02, 0.08), rng.uniform(-0.08, 0.08)]
            p.seg('madeira_escura', q0, q1, 0.004)
            fofo(p, 'folha_seca', *q1, 0.025, 0.004, 0.012, 0.8, 0.8, (6, 8))
    for k in range(10):                                                                       # folhas caídas
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.2, 0.45)
        fofo(p, 'folha_seca', r * math.cos(a), 0.003, r * math.sin(a), 0.025, 0.003, 0.012, 0.8, 0.8, (6, 8))


@item('relogio_parede', 'Relógio de parede parado', 'mobilias', 'lembrancas', montagem='wall', altura_sugerida_m=1.8,
      comodos=['cozinha', 'sala', 'escolinha', 'estacao', 'escritorio'], parado_em='3:17 (hora do surto)', **ANTES)
def relogio_parede(M):
    p = M.base; R = 0.16
    img = Image.new('RGB', (512, 512), (244, 240, 228)); d = ImageDraw.Draw(img)
    for k in range(60):
        a = k / 60 * 2 * math.pi; r0 = 230 if k % 5 else 210
        d.line([(256 + r0 * math.sin(a), 256 - r0 * math.cos(a)), (256 + 240 * math.sin(a), 256 - 240 * math.cos(a))], fill=(30, 30, 30), width=8 if k % 5 == 0 else 3)
    for h in range(1, 13): a = h / 12 * 2 * math.pi; texto_c(d, (256 + 175 * math.sin(a), 256 - 175 * math.cos(a)), str(h), 52, (30, 30, 30))
    mat_imagem('mostrador', img, 0.4)
    anel(p, 'plastico_preto', R - 0.015, R, 0.0, 0.045, 48, 'z', (0, R, 0), chanfro=0.005)
    torno(p, 'plastico_preto', [(R, 0.0), (R, 0.005)], 48, 'z', (0, R, 0))
    torno(p, 'mostrador', [(R - 0.014, 0.02), (R - 0.014, 0.022)], 48, 'z', (0, R, 0))
    p.uv['mostrador'] = lambda v, n: np.stack([(v[:, 0] + R) / (2 * R), (v[:, 1]) / (2 * R)], 1)
    for ang, L, w in ((-(3 + 17 / 60) / 12 * 2 * math.pi, 0.08, 0.008), (-(17 / 60) * 2 * math.pi, 0.12, 0.006), (-(42 / 60) * 2 * math.pi, 0.13, 0.002)):
        a = -ang
        p.seg('esmalte_escuro' if w > 0.003 else 'plastico_vermelho', (0, R, 0.026), (L * math.sin(a), R + L * math.cos(a), 0.026 + w * 0), w, 0.002)
    p.cyl('aco_polido', 0.008, 0, 0, sec=12) if False else cyl_eixo(p, 'aco_polido', 0.008, 0.022, 0.03, 'z', (0, R, 0), 12)
    torno(p, 'vidro_prateleira', [(R - 0.014, 0.04), (R * 0.6, 0.044), (0.0, 0.045)], 48, 'z', (0, R, 0))


@item('calendario_parede', 'Calendário na data do surto', 'mobilias', 'lembrancas', montagem='wall', altura_sugerida_m=1.3,
      comodos=['cozinha', 'escritorio', 'posto', 'quartel', 'casas'], **ANTES)
def calendario_parede(M):
    p = M.base; W, H = 0.3, 0.42
    img = Image.new('RGB', (360, 504), (246, 244, 236)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 360, 200], fill=(90, 140, 180)); d.polygon([(0, 200), (120, 90), (220, 170), (300, 110), (360, 160), (360, 200)], fill=(60, 110, 70))
    texto_c(d, (180, 230), 'MARÇO', 40, (160, 30, 30))
    for i in range(7): texto_c(d, (30 + i * 50, 270), 'DSTQQSS'[i], 22, (80, 80, 80))
    for k in range(31):
        r, c = divmod(k + 3, 7); x, y = 30 + c * 50, 305 + r * 38; texto_c(d, (x, y), str(k + 1), 22, (40, 40, 40), False)
        if k + 1 <= 12: d.line([(x - 16, y - 12), (x + 16, y + 12)], fill=(30, 30, 30), width=3)
        if k + 1 == 13: d.ellipse([x - 20, y - 18, x + 20, y + 18], outline=(200, 20, 20), width=4)
    mat_imagem('calendario', img, 0.85)
    p.box('calendario', -W / 2, W / 2, 0, H, 0.0, 0.002); p.uv['calendario'] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)
    for k in range(12): cyl_eixo(p, 'aco_polido', 0.005, 0.0, 0.006, 'x', (0, 0, 0), 6) if False else anel(p, 'aco_polido', 0.004, 0.0055, -W / 2 + 0.03 + k * 0.022, -W / 2 + 0.034 + k * 0.022, 10, 'x', (0, H - 0.01, 0.003))
    cyl_eixo(p, 'aco', 0.003, 0.0, 0.02, 'z', (0, H + 0.03, 0), 8)


@item('tv_tubo', 'TV de tubo com tela rachada', 'mobilias', 'lembrancas', comodos=['sala', 'motel', 'casas', 'hotel'], colisao='caixa', ambiente=True,
      desmonta={'sucata': 2, 'pecas': 1}, portatil=True, peso_kg=18.0)
def tv_tubo(M):
    p = M.base; X, H, Z = 0.33, 0.5, 0.2
    p.cham('madeira_tv', -X, X, 0.0, H, -Z, Z, 0.02)
    p.hull('plastico_preto', [(x, y, -Z) for x in (-X + 0.04, X - 0.04) for y in (0.05, H - 0.05)] + [(x, y, -Z - 0.22) for x in (-0.16, 0.16) for y in (0.12, H - 0.12)])
    p.cham('plastico_preto', -X + 0.03, 0.15, 0.04, H - 0.04, Z - 0.005, Z + 0.005, 0.01)
    p.cham('tela_tv', -X + 0.06, 0.12, 0.07, H - 0.07, Z + 0.004, Z + 0.016, 0.03)
    for a, L in ((0.3, 0.17), (1.9, 0.13), (3.7, 0.15), (4.9, 0.1), (2.7, 0.08)):
        p.seg('vidro_caco', (-0.08, 0.27, Z + 0.017), (-0.08 + L * math.cos(a), 0.27 + L * math.sin(a), Z + 0.017), 0.003, 0.0008)
    for y in (0.36, 0.25): torno(p, 'aco_polido', [(0.022, 0.0), (0.022, 0.015), (0.016, 0.022), (0.0, 0.024)], 16, 'z', (0.24, y, Z))
    for k in range(6): p.box('esmalte_escuro', 0.19, 0.29, 0.08 + k * 0.016, 0.086 + k * 0.016, Z, Z + 0.002)
    for xs in (-1, 1): p.seg('aco_polido', (xs * 0.02, H, -0.05), (xs * 0.25, H + 0.35, -0.12), 0.006)


@item('abajur', 'Abajur', 'mobilias', 'lembrancas', comodos=['quarto', 'sala', 'motel', 'hotel'], ambiente=True, colisao='nenhuma', portatil=True, peso_kg=1.5,
      luz_m=3, usa='energia')
def abajur(M):
    p = M.base
    torno(p, 'louca', [(0.08, 0.0), (0.08, 0.015), (0.06, 0.03), (0.09, 0.12), (0.095, 0.2), (0.06, 0.3), (0.02, 0.33), (0.015, 0.36)], 32)
    p.cyl('cobre', 0.006, 0.36, 0.48, sec=10); torno(p, 'lamp_glass', [(0.0, 0.44), (0.03, 0.45), (0.025, 0.5), (0.0, 0.51)], 16)
    torno(p, 'abajur_cupula', [(0.17, 0.38), (0.1, 0.6)], 36, fechar=False); torno(p, 'abajur_cupula', [(0.165, 0.38), (0.095, 0.6)], 36, fechar=False) if False else None
    m = list(p.parts['abajur_cupula'])[-1].copy(); m.invert(); m.apply_scale(1.0); p.add('abajur_cupula', m)
    for k in range(3): a = k / 3 * 2 * math.pi; p.seg('cobre', (0, 0.5, 0), (0.1 * math.cos(a), 0.6, 0.1 * math.sin(a)), 0.003)
    varrer(p, 'plastico_branco', circ(0.003, 6), [(0, 0.005, -0.07), (0, 0.003, -0.25), (0.1, 0.003, -0.45)])


@item('tapete_sala', 'Tapete de sala', 'mobilias', 'lembrancas', comodos=['sala', 'quarto', 'hotel', 'igreja'], ambiente=True, colisao='nenhuma',
      esconde='alçapão ou dinheiro por baixo (evento)')
def tapete_sala(M):
    p = M.base; X, Z = 1.0, 0.7
    img = Image.new('RGB', (1024, 716), (128, 40, 36)); d = ImageDraw.Draw(img)
    for k, c in enumerate(((210, 170, 90), (40, 50, 90), (210, 170, 90))): d.rectangle([30 + k * 30, 30 + k * 30, 994 - k * 30, 686 - k * 30], outline=c, width=12)
    d.ellipse([362, 208, 662, 508], outline=(210, 170, 90), width=14); d.polygon([(512, 248), (612, 358), (512, 468), (412, 358)], fill=(40, 50, 90))
    for k in range(16): x = 160 + k * 46; d.ellipse([x, 100, x + 20, 120], fill=(210, 170, 90)); d.ellipse([x, 596, x + 20, 616], fill=(210, 170, 90))
    rng = np.random.default_rng(5)
    for _ in range(18): x, y = rng.uniform(0, 1024), rng.uniform(0, 716); r = rng.uniform(20, 70); d.ellipse([x - r, y - r, x + r, y + r], fill=(90, 70, 50))  # manchas
    mat_imagem('tapete_img', img, 0.95)
    p.box('tapete_img', -X, X, 0, 0.008, -Z, Z); p.uv['tapete_img'] = uv_plano(-X, X, -Z, Z)
    t = P(); t.box('tapete_img', 0, 0.4, 0, 0.008, -Z, -Z + 0.4)                              # ponta dobrada
    p.uv['tapete_img'] = uv_plano(-X, X, -Z, Z)
    for z in np.linspace(-Z + 0.02, Z - 0.02, 30):
        for xs in (-1, 1): p.box('lencol', *sorted((xs * X, xs * (X + 0.05))), 0, 0.003, z - 0.004, z + 0.004)


@item('vitrola', 'Vitrola com discos', 'mobilias', 'lembrancas', comodos=['sala', 'casas', 'mansao', 'diner'], ambiente=True, colisao='caixa',
      interacao='tocar um disco (moral +5 na base; faz barulho)', usa='energia')
def vitrola(M):
    p = M.base; X, Z = 0.45, 0.25
    for xs in (-1, 1):
        for zs in (-1, 1): p.hull('madeira_escura', [(xs * (X - 0.06), 0.0, zs * (Z - 0.05)), (xs * (X - 0.04), 0.0, zs * (Z - 0.05)), (xs * (X - 0.03), 0.3, zs * (Z - 0.04)), (xs * (X - 0.05), 0.3, zs * (Z - 0.04)),
                                                       (xs * (X - 0.06), 0.0, zs * (Z - 0.03)), (xs * (X - 0.03), 0.3, zs * (Z - 0.02))])
    p.cham('madeira', -X, X, 0.3, 0.65, -Z, Z, 0.015)
    p.cham('tecido_cadeira', -X + 0.05, X - 0.05, 0.34, 0.6, Z - 0.002, Z + 0.003, 0.006)
    for x in np.linspace(-X + 0.08, X - 0.08, 10): p.box('madeira_escura', x - 0.006, x + 0.006, 0.34, 0.6, Z + 0.002, Z + 0.008)
    p.box('esmalte_escuro', -X + 0.03, X - 0.03, 0.649, 0.651, -Z + 0.03, Z - 0.03)
    torno(p, 'disco', [(0.15, 0.651), (0.15, 0.656), (0.0, 0.657)], 40, 'y', (-0.1, 0, 0))
    torno(p, 'tinta_vermelha', [(0.04, 0.6565), (0.0, 0.658)], 24, 'y', (-0.1, 0, 0))
    p.cyl('aco_polido', 0.004, 0.65, 0.68, x=-0.1, z=0, sec=8)
    p.cyl('aco_polido', 0.02, 0.65, 0.68, x=0.2, z=-0.12, sec=14); p.seg('aco_polido', (0.2, 0.68, -0.12), (0.02, 0.665, 0.05), 0.008)
    q = M.parte('tampa', (0, 0.65, -Z), 'tampa', eixo='x', abre_graus=-80)
    q.cham('madeira', -X, X, 0.65, 0.72, -Z, Z, 0.012)
    for k in range(5):                                                                        # discos encostados
        t = P(); t.cham('cartela' if k % 2 else 'papelao', -0.155, 0.155, 0.0, 0.31, -0.003, 0.003, 0.002)
        p.merge(t, trimesh.transformations.translation_matrix([X + 0.07 + k * 0.012, 0.0, 0.0]) @ trimesh.transformations.rotation_matrix(math.pi / 2 - 0.15, [0, 1, 0]) @ _rz(0.12))


@item('fruteira_podre', 'Fruteira com frutas podres', 'mobilias', 'lembrancas', comodos=['cozinha', 'sala', 'diner'], ambiente=True, colisao='nenhuma',
      cheiro='moscas: atrai zumbis de perto', nao_comer=True)
def fruteira_podre(M):
    p = M.base; rng = np.random.default_rng(81)
    torno(p, 'louca', [(0.06, 0.0), (0.06, 0.01), (0.05, 0.015), (0.14, 0.07), (0.15, 0.08), (0.14, 0.08), (0.05, 0.025), (0.0, 0.025)], 36)
    for k in range(5):
        a = k / 5 * 2 * math.pi; r = 0.07
        fofo(p, 'fruta_podre', r * math.cos(a), 0.065, r * math.sin(a), 0.035, 0.03 * (0.7 if k % 2 else 1), 0.035, 0.8, 0.8, (10, 12))
    for k in range(3):                                                                        # bananas pretas
        pts = [(-0.08 + 0.16 * s, 0.1 + 0.03 * math.sin(s * math.pi), 0.02 * k + 0.04 * (s - 0.5) ** 2) for s in np.linspace(0, 1, 8)]
        varrer(p, 'banana_podre', circ(0.016, 8), pts)
    for k in range(8):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.05, 0.25); y = rng.uniform(0.12, 0.3)
        p.sphere('esmalte_escuro', 0.003, r * math.cos(a), y, r * math.sin(a), 0)


@item('desenho_crianca', 'Desenho de criança na parede', 'mobilias', 'lembrancas', montagem='wall', altura_sugerida_m=1.1,
      comodos=['quarto', 'cozinha', 'escolinha', 'casas'], decalque=True, **ANTES)
def desenho_crianca(M):
    img = Image.new('RGBA', (420, 300), (250, 250, 246, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 230, 420, 300], fill=(90, 190, 80, 255)); d.ellipse([320, 20, 400, 100], fill=(250, 210, 40, 255))
    for k in range(10): a = k / 10 * 2 * math.pi; d.line([(360 + 45 * math.cos(a), 60 + 45 * math.sin(a)), (360 + 65 * math.cos(a), 60 + 65 * math.sin(a))], fill=(250, 210, 40, 255), width=5)
    d.polygon([(60, 230), (60, 140), (130, 80), (200, 140), (200, 230)], outline=(200, 40, 40, 255), width=8); d.rectangle([110, 180, 145, 230], outline=(120, 70, 30, 255), width=6)
    for k, x in enumerate((240, 280, 305)):
        h = 70 if k == 0 else 45; d.ellipse([x - 10, 230 - h - 22, x + 10, 230 - h - 2], outline=(30, 30, 30, 255), width=4)
        d.line([(x, 230 - h), (x, 230 - h * 0.35)], fill=(30, 30, 30, 255), width=4); d.line([(x, 230 - h * 0.35), (x - 12, 230)], fill=(30, 30, 30, 255), width=4); d.line([(x, 230 - h * 0.35), (x + 12, 230)], fill=(30, 30, 30, 255), width=4)
        d.line([(x - 16, 230 - h * 0.75), (x + 16, 230 - h * 0.75)], fill=(30, 30, 30, 255), width=4)
    texto_c(d, (120, 40), 'MINHA FAMÍLIA', 26, (40, 80, 200, 255), False)
    mat_decal('desenho_img', img.rotate(3, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0)), 0.9)
    p = M.base; W, H = 0.3, 0.22
    p.box('desenho_img', -W / 2, W / 2, 0, H, 0.0, 0.001); p.uv['desenho_img'] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)
    p.cham('fita_prata', -0.03, 0.03, H - 0.02, H + 0.01, 0.001, 0.0015, 0.0003) if False else p.box('plastico_transp', -0.03, 0.03, H - 0.015, H + 0.01, 0.001, 0.0016)


@item('pilha_livros', 'Pilha de livros no chão', 'mobilias', 'lembrancas', comodos=['sala', 'biblioteca', 'escolinha', 'escritorio', 'casas'], ambiente=True,
      colisao='nenhuma', saque=['livros'], conteiner=True, slots=2)
def pilha_livros(M):
    p = M.base; rng = np.random.default_rng(91); y = 0.0
    for k in range(7):
        w, d_, e = rng.uniform(0.14, 0.2), rng.uniform(0.2, 0.27), rng.uniform(0.02, 0.05); a = rng.uniform(-0.25, 0.25)
        t = P(); c = f'livro_{k % 6 + 1}'
        t.cham(c, -w / 2, w / 2, 0, e, -d_ / 2, d_ / 2, 0.003); t.box('papel', -w / 2 + 0.006, w / 2, 0.003, e - 0.003, -d_ / 2 + 0.004, d_ / 2 - 0.004)
        p.merge(t, trimesh.transformations.translation_matrix([rng.uniform(-0.02, 0.02), y, rng.uniform(-0.02, 0.02)]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]))
        y += e
    t = P(); t.cham('livro_3', -0.09, 0.09, 0, 0.03, -0.12, 0.12, 0.003); t.box('papel', -0.084, 0.09, 0.003, 0.027, -0.116, 0.116)
    p.merge(t, trimesh.transformations.translation_matrix([0.25, 0.0, 0.1]) @ trimesh.transformations.rotation_matrix(0.9, [0, 1, 0]))
