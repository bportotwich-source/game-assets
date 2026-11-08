# Lote 6: ambientacao, sinais do fim do mundo e rua/quintal. Executado por gerar_props.py (mesmas funcoes e materiais).
CORES.update({'pintura_carro': (34, 52, 46), 'cromo': (200, 202, 206), 'vidro_carro': (20, 26, 30), 'farol': (230, 230, 220),
              'lanterna_carro': (110, 8, 6), 'banco_carro': (60, 44, 34), 'laranja': (200, 70, 8), 'branco_refletivo': (230, 230, 226),
              'hidrante': (90, 6, 4), 'cortica': (170, 120, 70), 'concreto': (150, 146, 138), 'tinta_branca': (220, 220, 214),
              'tecido_carrinho': (40, 54, 80), 'louca': (236, 236, 230), 'vidro_caco': (190, 220, 220), 'grama_seca': (120, 110, 60),
              'tijolo': (140, 64, 44), 'mangueira': (8, 36, 12), 'quadro_bici': (120, 20, 20)})
METALICOS.update({'pintura_carro': (0.35, 0.55), 'cromo': (1.0, 0.12), 'hidrante': (0.3, 0.5), 'quadro_bici': (0.4, 0.4)})
FOSCOS.update({'vidro_carro': 0.08, 'farol': 0.15, 'lanterna_carro': 0.3, 'laranja': 0.55, 'branco_refletivo': 0.4, 'louca': 0.2,
               'vidro_caco': 0.05, 'tinta_branca': 0.6, 'mangueira': 0.5})
TEX_PROPRIAS += [('banco_carro', 'tecido', 0.5, 768), ('tecido_carrinho', 'tecido', 0.5, 768), ('cortica', 'papelao', 0.5, 512),
                 ('concreto', 'granito', 1.0, 384), ('tijolo', 'papelao', 0.5, 512), ('grama_seca', 'tecido', 0.5, 512)]


def mat_decal(nome, img, rough=0.85):
    """Decalque com transparencia (pichacao, mancha): PNG RGBA, alphaMode MASK. O glb_jpeg mantem PNG quando ha alfa."""
    TEX[nome] = (img, None, None)
    MATS[nome] = PBRMaterial(name=nome, baseColorTexture=img, baseColorFactor=[255, 255, 255, 255], alphaMode='MASK', alphaCutoff=0.4,
                             metallicFactor=0.0, roughnessFactor=rough)


def _spray(linhas, cor, tam=(1024, 512), fonte_px=150, gira=-4, escorre=True, seed=1):
    rng = np.random.default_rng(seed); im = Image.new('RGBA', tam, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = fonte(fonte_px); y = tam[1] / (len(linhas) + 1)
    for i, l in enumerate(linhas):
        cy = y * (i + 1); w = d.textlength(l, font=f)
        while w > tam[0] - 60 and fonte_px > 40: fonte_px -= 10; f = fonte(fonte_px); w = d.textlength(l, font=f)
        for k in range(3):                                                                    # tinta irregular (3 passadas)
            ox, oy = rng.integers(-3, 4), rng.integers(-3, 4)
            d.text((tam[0] / 2 + ox, cy + oy), l, font=f, fill=cor + (200 + 25 * k,), anchor='mm', stroke_width=3 - k, stroke_fill=cor + (150,))
        if escorre:
            x0 = tam[0] / 2 - w / 2
            for _ in range(int(w / 60)):
                x = x0 + rng.uniform(0, w); y0 = cy + fonte_px * 0.32; L = rng.uniform(20, 110)
                d.line([(x, y0), (x, y0 + L)], fill=cor + (230,), width=int(rng.integers(3, 7))); d.ellipse([x - 4, y0 + L - 3, x + 4, y0 + L + 5], fill=cor + (230,))
    for _ in range(400):                                                                      # respingos
        x, yy = rng.uniform(0, tam[0]), rng.uniform(0, tam[1]); r = rng.uniform(0.5, 2.2)
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=cor + (int(rng.uniform(60, 200)),))
    return im.rotate(gira, resample=Image.BICUBIC)


def _decal_parede(M, nome, img, W, H):
    mat_decal(nome, img); p = M.base
    p.box(nome, -W / 2, W / 2, 0, H, 0.0, 0.002); p.uv[nome] = lambda v, n: np.stack([(v[:, 0] + W / 2) / W, v[:, 1] / H], 1)


def _decal_chao(M, nome, img, W, D, y=0.002):
    mat_decal(nome, img, 0.6); p = M.base
    p.box(nome, -W / 2, W / 2, 0.0, y, -D / 2, D / 2); p.uv[nome] = uv_plano(-W / 2, W / 2, -D / 2, D / 2)


SINAIS = dict(comodos=['casas', 'rua', 'galeria', 'supermercado', 'igreja', 'escolinha'], ambiente=True, colisao='nenhuma', decalque=True)


# ---------------------------------------------------------------------------- SINAIS DO FIM DO MUNDO
@item('pichacao_nao_entre', 'Pichação "NÃO ENTRE"', 'mobilias', 'sinais', montagem='wall', altura_sugerida_m=0.9, **SINAIS)
def pichacao_nao_entre(M): _decal_parede(M, 'spray_nao_entre', _spray(['NÃO ENTRE'], (150, 10, 8), seed=2), 1.8, 0.9)


@item('pichacao_infectados', 'Pichação "INFECTADOS LÁ DENTRO"', 'mobilias', 'sinais', montagem='wall', altura_sugerida_m=0.8, **SINAIS)
def pichacao_infectados(M): _decal_parede(M, 'spray_infectados', _spray(['INFECTADOS', 'LÁ DENTRO'], (20, 20, 20), seed=3, gira=3), 1.8, 0.9)


@item('pichacao_igreja', 'Pichação "FOMOS PARA A IGREJA"', 'mobilias', 'sinais', montagem='wall', altura_sugerida_m=0.9,
      pista='aponta para a igreja (sobreviventes)', **SINAIS)
def pichacao_igreja(M):
    im = _spray(['FOMOS PARA', 'A IGREJA  →'], (230, 230, 225), seed=4, gira=-2)
    _decal_parede(M, 'spray_igreja', im, 1.8, 0.9)


@item('marca_busca', 'Marca de busca em X na porta', 'mobilias', 'sinais', montagem='wall', altura_sugerida_m=1.2,
      significado='equipe de resgate já passou: data, grupo, mortos e perigo', **SINAIS)
def marca_busca(M):
    im = Image.new('RGBA', (512, 512), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (200, 70, 10)
    for k in range(3):
        d.line([(60 + k, 60), (452 + k, 452)], fill=c + (230,), width=16); d.line([(452 + k, 60), (60 + k, 452)], fill=c + (230,), width=16)
    for txt, xy in (('12/3', (256, 95)), ('G2', (95, 256)), ('2', (256, 425)), ('!', (420, 256))):
        texto_c(d, xy, txt, 64, c + (240,))
    _decal_parede(M, 'spray_busca', im.rotate(2, resample=Image.BICUBIC), 0.7, 0.7)


@item('contagem_dias', 'Riscos de contagem de dias', 'mobilias', 'sinais', montagem='wall', altura_sugerida_m=1.1,
      significado='alguém se escondeu aqui por semanas', **SINAIS)
def contagem_dias(M):
    im = Image.new('RGBA', (768, 384), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rng = np.random.default_rng(6)
    for g in range(7):
        x0 = 30 + g * 105; y0 = 60 + (g % 2) * 140 if g > 3 else 60
        y0 = 60 if g < 4 else 210; x0 = 30 + (g % 4) * 180
        for k in range(4): x = x0 + k * 26 + rng.integers(-3, 3); d.line([(x, y0), (x + rng.integers(-6, 6), y0 + 110)], fill=(30, 26, 24, 235), width=6)
        if g < 6: d.line([(x0 - 12, y0 + 85), (x0 + 100, y0 + 20)], fill=(30, 26, 24, 235), width=6)
    texto_c(d, (650, 330), 'DIA 33', 40, (30, 26, 24, 230), False)
    _decal_parede(M, 'risco_carvao', im, 1.0, 0.5)


@item('mancha_sangue', 'Mancha de sangue seco', 'mobilias', 'sinais', comodos=['casas', 'rua', 'clinica', 'galeria'], ambiente=True, colisao='nenhuma')
def mancha_sangue(M):
    im = Image.new('RGBA', (512, 512), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rng = np.random.default_rng(8); c = (70, 14, 10)
    for _ in range(26):
        x, y = rng.normal(256, 60, 2); r = rng.uniform(15, 70); d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=c + (int(rng.uniform(150, 220)),))
    for _ in range(4):                                                                        # arrasto
        x, y = rng.normal(256, 30, 2); d.line([(x, y), (x + rng.uniform(100, 220), y + rng.uniform(-40, 40))], fill=c + (130,), width=int(rng.uniform(10, 26)))
    for _ in range(90):
        x, y = rng.normal(256, 140, 2); r = rng.uniform(2, 7); d.ellipse([x - r, y - r, x + r, y + r], fill=c + (200,))
    _decal_chao(M, 'sangue_seco', im, 1.2, 1.2)


@item('cacos_vidro', 'Cacos de vidro no chão', 'mobilias', 'sinais', comodos=['casas', 'galeria', 'supermercado', 'rua', 'posto'], ambiente=True,
      colisao='nenhuma', barulho='alto ao pisar (atrai zumbis); agachado não faz barulho', armadilha=True)
def cacos_vidro(M):
    p = M.base; rng = np.random.default_rng(12)
    for i in range(60):
        r = abs(rng.normal(0, 0.28)); a = rng.uniform(0, 2 * math.pi); cx, cz = r * math.cos(a), r * math.sin(a)
        s = rng.uniform(0.012, 0.07) * (1.5 if i < 6 else 1); n = int(rng.integers(3, 6))
        pts = [(cx + s * math.cos(t) * rng.uniform(0.5, 1), cz + s * math.sin(t) * rng.uniform(0.5, 1)) for t in np.sort(rng.uniform(0, 2 * math.pi, n))]
        poly = Polygon(pts).convex_hull
        if poly.area > 1e-6: extrudar_xz(p, 'vidro_caco', poly, 0.0, 0.003)
    for i in range(4):                                                                        # pedaço de caixilho
        pass
    t = P(); t.cham('madeira_branca', -0.25, 0.25, 0.0, 0.03, -0.02, 0.02, 0.004); t.cham('madeira_branca', -0.25, -0.21, 0.0, 0.03, -0.02, 0.3, 0.004)
    p.merge(t, trimesh.transformations.translation_matrix([0.15, 0, -0.25]) @ trimesh.transformations.rotation_matrix(0.5, [0, 1, 0]))


@item('louca_quebrada', 'Louça quebrada', 'mobilias', 'sinais', comodos=['cozinha', 'diner', 'casas'], ambiente=True, colisao='nenhuma',
      barulho='médio ao pisar')
def louca_quebrada(M):
    p = M.base; rng = np.random.default_rng(14)
    def caco_prato(cx, cz, a0, a1, r=0.12, y=0.0):
        pts = [(cx, cz)] + [(cx + r * math.cos(a), cz + r * math.sin(a)) for a in np.linspace(a0, a1, 8)]
        extrudar_xz(p, 'louca', Polygon(pts), y, y + 0.006)
        pts2 = [(cx + (r + 0.0) * math.cos(a), cz + (r + 0.0) * math.sin(a)) for a in np.linspace(a0, a1, 8)] + \
               [(cx + (r - 0.012) * math.cos(a), cz + (r - 0.012) * math.sin(a)) for a in np.linspace(a1, a0, 8)]
        extrudar_xz(p, 'tinta_azul', Polygon(pts2), y + 0.006, y + 0.0068)
    caco_prato(0.0, 0.0, 0.3, 2.1); caco_prato(0.06, 0.05, 2.4, 3.6); caco_prato(-0.12, -0.08, 4.0, 5.2)
    caco_prato(0.2, -0.15, 0.0, 1.0, 0.1); caco_prato(-0.3, 0.12, 1.0, 3.0, 0.1)
    for k in range(18):                                                                       # lascas
        cx, cz = rng.normal(0, 0.18, 2); s = rng.uniform(0.01, 0.03)
        extrudar_xz(p, 'louca', Polygon([(cx, cz), (cx + s, cz + s * 0.3), (cx + s * 0.4, cz + s)]), 0.0, 0.005)
    anel(p, 'louca', 0.033, 0.038, 0.0, 0.05, 20, 'z', (0.3, 0.035, 0.2))                       # xícara deitada sem asa
    torno(p, 'louca', [(0.033, -0.0), (0.033, 0.003)], 20, 'z', (0.3, 0.035, 0.2 - 0.0))


@item('papeis_espalhados', 'Papéis espalhados', 'mobilias', 'sinais', comodos=['escritorio', 'delegacia', 'correios', 'escolinha', 'casas'], ambiente=True, colisao='nenhuma')
def papeis_espalhados(M):
    p = M.base; rng = np.random.default_rng(15)
    img = Image.new('RGB', (256, 340), (240, 236, 224)); d = ImageDraw.Draw(img)
    for y in range(30, 320, 14): d.line([(20, y), (20 + rng.integers(120, 220), y)], fill=(120, 120, 130), width=3)
    d.rectangle([20, 20, 120, 60], fill=(60, 60, 80)); mat_imagem('folha_texto', img, 0.9)
    for i in range(14):
        x, z = rng.normal(0, 0.35, 2); a = rng.uniform(0, math.pi); y = 0.0005 * i
        t = P(); t.box('folha_texto' if i % 3 else 'papel', -0.105, 0.105, 0, 0.0006, -0.148, 0.148)
        t.uv['folha_texto'] = uv_plano(-0.105, 0.105, -0.148, 0.148)
        q = P(); q.merge(t, trimesh.transformations.translation_matrix([x, y, z]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]))
        for k, ms in q.parts.items():
            for m in ms: p.add(k, m)
    p.uv['folha_texto'] = lambda v, n: np.stack([(v[:, 0] * 7.3) % 1, (v[:, 2] * 5.1) % 1], 1)
    p.cham('cartela', -0.12, 0.12, 0.0, 0.015, -0.16, 0.16, 0.002)                              # pasta caida


@item('cadeira_quebrada', 'Cadeira quebrada', 'mobilias', 'sinais', comodos=['casas', 'escolinha', 'diner', 'escritorio'], ambiente=True,
      colisao='caixa', desmonta={'madeira': 1})
def cadeira_quebrada(M):
    p = M.base; mat = 'madeira'
    t = P()                                                                                   # cadeira caida de lado, sem uma perna
    t.cham(mat, -0.21, 0.21, 0.44, 0.48, -0.2, 0.2, 0.006)
    for x, z in ((-0.18, -0.17), (0.18, -0.17), (-0.18, 0.17)): t.cham(mat, x - 0.02, x + 0.02, 0.0, 0.44, z - 0.02, z + 0.02, 0.004)
    t.cham(mat, 0.16, 0.2, 0.3, 0.44, 0.15, 0.19, 0.004)                                       # toco da perna quebrada
    for x in (-0.18, 0.18): t.cham(mat, x - 0.02, x + 0.02, 0.48, 0.92, -0.19, -0.15, 0.004)
    for y in (0.62, 0.78, 0.9): t.cham(mat, -0.18, 0.18, y - 0.03, y, -0.19, -0.16, 0.004)
    p.merge(t, trimesh.transformations.translation_matrix([0, 0.2, 0]) @ trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]))
    p.cham(mat, 0.25, 0.7, 0.0, 0.04, 0.2, 0.24, 0.004)                                        # perna solta
    p.hull(mat, [(0.7, 0.0, 0.2), (0.7, 0.04, 0.24), (0.74, 0.02, 0.22), (0.7, 0.0, 0.24), (0.72, 0.04, 0.2)])


@item('barricada_arrombada', 'Barricada arrombada', 'mobilias', 'sinais', montagem='wall', comodos=['casas', 'galeria', 'supermercado', 'motel'],
      vao_m=[0.9, 2.1, 0.0], ambiente=True, colisao='caixa', desmonta={'madeira': 2},
      significado='alguém tentou se proteger aqui e não deu certo')
def barricada_arrombada(M):
    p = M.base
    for xs in (-1, 1):
        p.cham('madeira_crua', xs * 0.55 - 0.035, xs * 0.55 + 0.035, 0.04, 2.18, 0.0, 0.03, 0.004)
    p.uv['madeira_crua'] = uv_veio_vertical
    _prancha(p, -0.15, 1.95, 0.03, 1.3, 0.03, seed=3)                                          # inteira no alto
    t = P(); _prancha(t, 0.0, 0.0, 0.0, 0.7, 0.0, seed=5)                                     # metade pendurada num prego
    p.merge(t, trimesh.transformations.translation_matrix([-0.55, 1.4, 0.03]) @ _rz(-1.25) @ trimesh.transformations.translation_matrix([0.33, 0, 0]))
    t = P(); _prancha(t, 0.0, 0.0, 0.0, 0.55, 0.0, seed=7)
    p.merge(t, trimesh.transformations.translation_matrix([0.55, 0.9, 0.03]) @ _rz(math.pi + 0.5) @ trimesh.transformations.translation_matrix([0.26, 0, 0]))
    for i, (x, z, a) in enumerate(((0.1, 0.5, 0.3), (-0.2, 0.75, -0.6), (0.3, 0.9, 1.2))):          # tabuas partidas no chao
        t = P(); _prancha(t, 0, 0, 0, 0.6 + 0.1 * i, 0.0, seed=20 + i)
        p.merge(t, trimesh.transformations.translation_matrix([x, 0.0, z]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]) @
                trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    p.uv['madeira_crua'] = uv_caixa(TILE)
    for i in range(10):
        a = i * 1.3; r = 0.2 + (i % 3) * 0.12
        p.cham('madeira_crua', r * math.cos(a) - 0.03, r * math.cos(a) + 0.03, 0.0, 0.01, 0.5 + r * math.sin(a) - 0.008, 0.5 + r * math.sin(a) + 0.008, 0.002)


@item('mural_desaparecidos', 'Mural de desaparecidos', 'mobilias', 'sinais', montagem='wall', altura_sugerida_m=1.0,
      comodos=['igreja', 'correios', 'estacao', 'rodoviaria', 'galeria', 'delegacia'], ambiente=True, colisao='nenhuma',
      pista='pode ter o rosto de um sobrevivente que ainda está vivo')
def mural_desaparecidos(M):
    p = M.base; W, H = 1.2, 0.9; rng = np.random.default_rng(21)
    p.cham('madeira_escura', -W / 2, W / 2, 0, H, 0.0, 0.025, 0.004)
    p.box('cortica', -W / 2 + 0.03, W / 2 - 0.03, 0.03, H - 0.03, 0.025, 0.028)
    for k in range(5):                                                                        # fotos com nomes (rostos em silhueta)
        img = Image.new('RGB', (200, 260), (245, 242, 232)); d = ImageDraw.Draw(img); c = tuple(int(v) for v in rng.integers(60, 200, 3))
        d.rectangle([14, 14, 186, 190], fill=c); d.ellipse([70, 40, 130, 110], fill=(230, 200, 170)); d.ellipse([45, 110, 155, 230], fill=(230, 200, 170))
        d.rectangle([14, 190, 186, 200], fill=(245, 242, 232))
        nm = ['ANA', 'JOÃO', 'LÍVIA', 'RAUL', 'TETÊ'][k]; texto_c(d, (100, 225), f'{nm}?', 30, (30, 30, 50))
        mat_imagem(f'foto_desap_{k}', img, 0.6)
        x = -0.45 + k * 0.22 + rng.uniform(-0.02, 0.02); y = 0.5 + (k % 2) * 0.15
        t = P(); t.box(f'foto_desap_{k}', -0.07, 0.07, -0.09, 0.09, 0.0, 0.0012); t.uv[f'foto_desap_{k}'] = lambda v, n: np.stack([(v[:, 0] + 0.07) / 0.14, (v[:, 1] + 0.09) / 0.18], 1)
        m = list(t.parts.values())[0][0].copy(); m.apply_transform(trimesh.transformations.translation_matrix([x, y, 0.029]) @ _rz(rng.uniform(-0.12, 0.12)))
        p.add(f'foto_desap_{k}', m)
        p.uv[f'foto_desap_{k}'] = (lambda x, y: (lambda v, n: np.stack([(v[:, 0] - x + 0.07) / 0.14, (v[:, 1] - y + 0.09) / 0.18], 1)))(x, y)
        torno(p, 'plastico_vermelho', [(0.006, 0), (0.006, 0.004), (0.002, 0.008)], 10, 'z', (x, y + 0.075, 0.03))
    img = Image.new('RGB', (256, 192), (250, 236, 150)); d = ImageDraw.Draw(img)
    for i, l in enumerate(['Procuro minha', 'irmã. Deixe', 'recado aqui.']): d.text((14, 20 + i * 50), l, font=fonte(30, False), fill=(40, 40, 80))
    mat_imagem('recado_mural', img, 0.8)
    for x, y in ((-0.35, 0.18), (0.25, 0.2), (0.42, 0.72)):
        q = P(); q.box('recado_mural', x - 0.07, x + 0.07, y - 0.05, y + 0.05, 0.028, 0.029)
        p.add('recado_mural', list(q.parts.values())[0][0])
    cs = np.array([(-0.35, 0.18), (0.25, 0.2), (0.42, 0.72)])
    def uvr(v, n):
        k = np.argmin(((v[:, None, :2] - cs[None]) ** 2).sum(-1), axis=1); c = cs[k]
        return np.stack([(v[:, 0] - c[:, 0]) / 0.14 + 0.5, (v[:, 1] - c[:, 1]) / 0.1 + 0.5], 1)
    p.uv['recado_mural'] = uvr


@item('cartaz_evacuacao', 'Cartaz de evacuação', 'mobilias', 'sinais', montagem='wall', altura_sugerida_m=1.2,
      comodos=['rua', 'galeria', 'estacao', 'rodoviaria', 'escolinha', 'correios'], ambiente=True, colisao='nenhuma',
      pista='marca o ponto de resgate abandonado (estação de trem)')
def cartaz_evacuacao(M):
    img = Image.new('RGBA', (600, 840), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (600, 0), (600, 700), (520, 840), (0, 840)], fill=(236, 230, 214, 255))
    d.rectangle([0, 0, 600, 140], fill=(170, 20, 16, 255)); texto_c(d, (300, 70), 'AVISO OFICIAL', 60, (255, 255, 255, 255))
    for i, l in enumerate(['EVACUAÇÃO', 'OBRIGATÓRIA']): texto_c(d, (300, 220 + i * 80), l, 70, (30, 30, 30, 255), larg=560)
    for i, l in enumerate(['Dirija-se à estação de trem.', 'Leve água e documentos.', 'Não abra a porta para', 'pessoas feridas.']):
        texto_c(d, (300, 420 + i * 52), l, 36, (40, 40, 40, 255), False, larg=540)
    d.rectangle([60, 650, 540, 720], outline=(170, 20, 16, 255), width=6); texto_c(d, (300, 685), 'PONTO DE RESGATE: PLATAFORMA 1', 28, (170, 20, 16, 255), larg=460)
    rng = np.random.default_rng(3)
    for _ in range(40): x, y = rng.uniform(0, 600), rng.uniform(0, 840); r = rng.uniform(8, 30); d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 180, 140, 60))
    _decal_parede(M, 'cartaz_evac', img, 0.5, 0.7)
    for x, y in ((-0.23, 0.68), (0.23, 0.68), (-0.23, 0.02)): cyl_eixo(M.base, 'aco_polido', 0.004, 0.002, 0.005, 'z', (x, y, 0), 10)


# ---------------------------------------------------------------------------- RUA E QUINTAL
RUA = dict(comodos=['rua'], ambiente=True)


def _roda(p, c, r, w, eixo='x', murcha=0.0, mat_aro='cromo'):
    cx, cy, cz = c
    perf = [(r * 0.62, -w / 2), (r * 0.92, -w / 2), (r, -w / 2 + 0.03), (r, w / 2 - 0.03), (r * 0.92, w / 2), (r * 0.62, w / 2), (r * 0.64, 0)]
    m = P(); torno(m, 'borracha', perf, 32, 'x' if eixo == 'x' else 'z', (0, 0, 0))
    torno(m, mat_aro, [(r * 0.63, -w / 2 + 0.02), (r * 0.6, -w / 2 + 0.03), (r * 0.25, -w / 2 + 0.05), (r * 0.18, -w / 2 + 0.02), (0.0, -w / 2 + 0.02)], 24,
          'x' if eixo == 'x' else 'z', (0, 0, 0))
    torno(m, mat_aro, [(r * 0.63, w / 2 - 0.02), (r * 0.6, w / 2 - 0.03), (r * 0.25, w / 2 - 0.05), (r * 0.18, w / 2 - 0.02), (0.0, w / 2 - 0.02)], 24,
          'x' if eixo == 'x' else 'z', (0, 0, 0))
    T = trimesh.transformations.translation_matrix([cx, cy, cz])
    if murcha: T = T @ np.diag([1, 1 - murcha, 1, 1])
    p.merge(m, T)


@item('carro_abandonado', 'Carro abandonado', 'mobilias', 'rua', conteiner=True, saque=['combustivel', 'comida', 'ferramentas', 'mapas'], slots=6,
      comodos=['rua', 'posto', 'estacionamento', 'garagem'], ambiente=True, colisao='caixa', obstaculo=True,
      coleta={'recurso': 'combustivel', 'total': 2, 'ferramenta': 'mangueira e galão', 'segundos_por_unidade': 10}, barulho='alarme pode disparar')
def carro_abandonado(M):
    p = M.base; X = 0.84; m = 'pintura_carro'
    def ext_x(q, mat, poly, x0, x1):
        e = trimesh.creation.extrude_polygon(poly, x1 - x0); e.vertices = np.stack([e.vertices[:, 2] + x0, e.vertices[:, 1], e.vertices[:, 0]], 1)
        if e.volume < 0: e.invert()
        q.add(mat, e)
    perfil = Polygon([(-2.12, 0.33), (-2.18, 0.5), (-2.14, 0.86), (-1.25, 0.92), (1.05, 0.93), (2.02, 0.82), (2.16, 0.62), (2.13, 0.33)]).buffer(0.04, 4).buffer(-0.03, 4)
    for zc in (-1.32, 1.3): perfil = perfil.difference(Point(zc, 0.31).buffer(0.4, 24))
    ext_x(p, m, perfil, -X, X)
    for xs in (-1, 1):                                                                        # frisos, maçanetas, retrovisor
        p.box('cromo', *sorted((xs * X, xs * (X + 0.006))), 0.66, 0.685, -1.9, 1.9)
        p.cham('cromo', *sorted((xs * X, xs * (X + 0.02))), 0.8, 0.82, -0.35, -0.22, 0.004)
        p.cham(m, *sorted((xs * (X - 0.02), xs * (X + 0.12))), 0.95, 1.05, 0.82, 0.92, 0.015)
    p.hull('vidro_carro', [(x, 0.92, z) for x in (-0.8, 0.8) for z in (-1.24, 0.95)] + [(x, 1.36, z) for x in (-0.67, 0.67) for z in (-0.85, 0.34)])
    p.cham(m, -0.7, 0.7, 1.35, 1.41, -0.89, 0.38, 0.02)
    for xs in (-1, 1):
        for (z0, z1) in ((0.94, 0.34), (-0.12, -0.2), (-1.23, -0.85)):
            p.seg(m, (xs * 0.79, 0.93, z0), (xs * 0.675, 1.37, z1), 0.06, 0.07)
        p.seg(m, (xs * 0.8, 0.93, -1.24), (xs * 0.8, 0.93, 0.95), 0.05, 0.04)
    for xs in (-1, 1):                                                                        # faróis e lanternas
        torno(p, 'cromo', [(0.095, 0.0), (0.095, 0.02), (0.085, 0.03)], 24, 'z', (xs * 0.58, 0.66, 2.12))
        torno(p, 'farol', [(0.08, 0.02), (0.07, 0.04), (0.0, 0.045)], 24, 'z', (xs * 0.58, 0.66, 2.12))
        p.cham('lanterna_carro', *sorted((xs * 0.4, xs * 0.78)), 0.68, 0.8, -2.17, -2.13, 0.01)
    p.cham('cromo', -0.88, 0.88, 0.36, 0.48, 2.12, 2.24, 0.03); p.cham('cromo', -0.88, 0.88, 0.36, 0.48, -2.26, -2.14, 0.03)  # para-choques
    p.cham('esmalte_escuro', -0.45, 0.45, 0.52, 0.74, 2.16, 2.19, 0.01)                         # grade
    for x in np.linspace(-0.4, 0.4, 12): p.box('cromo', x - 0.004, x + 0.004, 0.53, 0.73, 2.185, 2.195)
    p.cham('esmalte_escuro', -0.25, 0.25, 0.4, 0.5, -2.27, -2.25, 0.004)                        # placa sem texto
    for xs in (-1, 1):
        for zc, mur in ((-1.32, 0.0), (1.3, 0.28 if xs > 0 else 0.0)):
            _roda(p, (xs * 0.74, 0.32 * (1 - mur * 0.5), zc), 0.32, 0.2, murcha=mur)
    p.cham('esmalte_escuro', -0.75, 0.75, 0.15, 0.35, -2.0, 2.0, 0.03)                          # assoalho
    p.cham('banco_carro', -0.72, 0.72, 0.5, 0.95, -1.15, -0.75, 0.05)                           # bancos vistos pelo vidro
    for xs in (-1, 1): p.cham('banco_carro', xs * 0.38 - 0.27, xs * 0.38 + 0.27, 0.5, 1.15, -0.15, 0.05, 0.05)
    torno(p, 'plastico_preto', [(0.19, 0.0), (0.19, 0.03), (0.16, 0.035)], 28, 'z', (0.38, 1.0, 0.55))   # volante
    for k in range(4):                                                                        # ferrugem e sujeira
        x0 = -X - 0.002; z0 = -1.9 + k * 1.0
        p.box('ferrugem', -X - 0.003, -X, 0.36, 0.48 + 0.05 * (k % 2), z0, z0 + 0.25 + 0.1 * k)
    q = M.parte('porta', (X + 0.002, 0.6, 0.93), 'porta', eixo='y', abre_graus=-60)
    pp = Polygon([(-0.13, 0.36), (0.93, 0.36), (0.93, 0.92), (-0.13, 0.92)])
    ext_x(q, m, pp, X - 0.002, X + 0.045)
    q.hull('vidro_carro', [(X + 0.0, 0.93, z) for z in (-0.12, 0.88)] + [(X - 0.12, 1.32, z) for z in (-0.18, 0.36)] +
           [(X + 0.012, 0.93, z) for z in (-0.12, 0.88)])
    q.box('cromo', X + 0.045, X + 0.05, 0.66, 0.685, -0.13, 0.93); q.cham('cromo', X + 0.04, X + 0.06, 0.8, 0.82, -0.08, 0.05, 0.004)
    q.box('banco_carro', X - 0.01, X - 0.002, 0.4, 0.88, -0.1, 0.9)


@item('carrinho_bebe', 'Carrinho de bebê virado', 'mobilias', 'rua', comodos=['rua', 'casas', 'galeria'], ambiente=True, colisao='caixa',
      saque=['roupas', 'comida'], conteiner=True, slots=2)
def carrinho_bebe(M):
    p = M.base; t = P()
    t.hull('tecido_carrinho', [(x, y, z) for x in (-0.26, 0.26) for y in (0.45, 0.75) for z in (-0.35, 0.35)] + [(x, 0.4, z) for x in (-0.22, 0.22) for z in (-0.3, 0.3)])
    for a in np.linspace(0.0, math.pi * 0.55, 6):                                             # capota sanfonada
        varrer(t, 'tecido_carrinho', Polygon([(-0.01, -0.03), (0.01, -0.03), (0.01, 0.03), (-0.01, 0.03)]),
               [(x, 0.75 + 0.3 * math.sin(a), -0.35 + 0.3 * (1 - math.cos(a))) for x in np.linspace(-0.27, 0.27, 2)])
    for xs in (-1, 1):
        t.seg('aco', (xs * 0.24, 0.45, -0.3), (xs * 0.24, 0.12, -0.38), 0.02); t.seg('aco', (xs * 0.24, 0.45, 0.3), (xs * 0.24, 0.12, 0.38), 0.02)
        t.seg('aco', (xs * 0.24, 0.6, -0.33), (xs * 0.24, 1.0, -0.62), 0.02)
        for z in (-0.38, 0.38): _roda(t, (xs * 0.27, 0.12, z), 0.12, 0.04)
    cyl_eixo(t, 'plastico_preto', 0.018, -0.26, 0.26, 'x', (0, 1.0, -0.62), 12)
    p.merge(t, trimesh.transformations.translation_matrix([0.0, 0.27, 0]) @ trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]))
    fofo(p, 'cobertor', 0.55, 0.03, 0.1, 0.25, 0.03, 0.2, 0.5, 0.5, (10, 16))
    fofo(p, 'travesseiro', 0.4, 0.03, -0.25, 0.1, 0.03, 0.08, 0.5, 0.5, (10, 12))


@item('bicicleta', 'Bicicleta caída', 'mobilias', 'rua', comodos=['rua', 'casas', 'escolinha', 'garagem'], ambiente=True, colisao='nenhuma',
      desmonta={'sucata': 2})
def bicicleta(M):
    p = M.base; t = P(); R = 0.33; q = 'quadro_bici'
    for z in (-0.52, 0.52):
        anel(t, 'borracha', R - 0.025, R, -0.018, 0.018, 40, 'x', (0, R, z))
        anel(t, 'cromo', R - 0.04, R - 0.025, -0.012, 0.012, 40, 'x', (0, R, z))
        for k in range(18):
            a = k / 18 * 2 * math.pi; t.seg('aco_polido', (0, R, z), (0, R + (R - 0.035) * math.sin(a), z + (R - 0.035) * math.cos(a)), 0.003)
        cyl_eixo(t, 'aco', 0.02, -0.04, 0.04, 'x', (0, R, z), 12)
    A, B, C, D = (0, R, -0.52), (0, R + 0.02, -0.05), (0, 0.85, -0.12), (0, 0.85, 0.38)
    for a, b in ((A, B), (B, C), (C, D), (B, D), (A, C), (D, (0, R, 0.52))): t.seg(q, a, b, 0.032)
    t.seg('cromo', D, (0, 1.0, 0.36), 0.026); cyl_eixo(t, 'cromo', 0.012, -0.28, 0.28, 'x', (0, 1.0, 0.33), 10)
    for xs in (-1, 1): cyl_eixo(t, 'borracha', 0.016, *sorted((xs * 0.2, xs * 0.29)), 'x', (0, 1.0, 0.33), 10)
    t.seg('cromo', C, (0, 0.95, -0.14), 0.024); fofo(t, 'esmalte_escuro', 0, 0.97, -0.14, 0.07, 0.03, 0.13, 0.4, 0.4, (10, 14))
    cyl_eixo(t, 'aco', 0.08, -0.03, 0.03, 'x', (0, R + 0.02, -0.05), 24)
    for s in (-1, 1): t.seg('aco', (s * 0.03, R + 0.02, -0.05), (s * 0.08, R + 0.02 + 0.16 * s, -0.05 + 0.04 * s), 0.02)
    p.merge(t, trimesh.transformations.translation_matrix([0.04, 0.0, 0]) @ trimesh.transformations.rotation_matrix(-math.pi / 2 + 0.06, [0, 0, 1]) @
            trimesh.transformations.translation_matrix([0, 0, 0]))


@item('cone_transito', 'Cone de trânsito', 'mobilias', 'rua', comodos=['rua', 'posto', 'garagem', 'estacao'], ambiente=True, colisao='caixa', portatil=True, peso_kg=1.0)
def cone_transito(M):
    p = M.base
    p.cham('laranja', -0.19, 0.19, 0.0, 0.03, -0.19, 0.19, 0.01)
    torno(p, 'laranja', [(0.14, 0.03), (0.13, 0.08), (0.035, 0.7), (0.028, 0.72)], 32)
    for y0, y1 in ((0.28, 0.36), (0.46, 0.53)):
        r0 = 0.14 - (y0 - 0.03) / 0.67 * 0.105; r1 = 0.14 - (y1 - 0.03) / 0.67 * 0.105
        torno(p, 'branco_refletivo', [(r0 + 0.002, y0), (r1 + 0.002, y1)], 32, fechar=False)


@item('cavalete_bloqueio', 'Cavalete de bloqueio', 'mobilias', 'rua', comodos=['rua', 'estacao', 'delegacia', 'quartel'], ambiente=True, colisao='caixa',
      obstaculo=True, barricada=True, portatil=True, peso_kg=9.0)
def cavalete_bloqueio(M):
    p = M.base; L = 1.2
    img = Image.new('RGB', (1024, 128), (240, 240, 236)); d = ImageDraw.Draw(img)
    for i in range(-2, 12): d.polygon([(i * 100, 128), (i * 100 + 64, 128), (i * 100 + 128 + 64, 0), (i * 100 + 128, 0)], fill=(200, 70, 8))
    mat_imagem('faixa_zebrada', img, 0.45)
    for y in (0.75, 0.45):
        p.cham('faixa_zebrada', -L / 2, L / 2, y, y + 0.17, -0.012, 0.012, 0.004)
    p.uv['faixa_zebrada'] = lambda v, n: np.stack([(v[:, 0] + L / 2) / L, ((v[:, 1] - 0.45) % 0.3) / 0.17], 1)
    for xs in (-1, 1):
        for zs in (-1, 1): p.seg('tinta_branca', (xs * 0.5, 1.0, 0.0), (xs * 0.5, 0.0, zs * 0.3), 0.04, 0.03)
    p.cham('tinta_branca', -0.55, 0.55, 0.96, 1.0, -0.03, 0.03, 0.006)
    torno(p, 'lanterna_carro', [(0.05, 1.0), (0.05, 1.02), (0.045, 1.08), (0.0, 1.1)], 20, 'y', (0.42, 0, 0))
    p.box('esmalte_escuro', 0.38, 0.46, 1.0, 1.015, -0.03, 0.03)


@item('fita_isolamento', 'Fita de isolamento com cones', 'mobilias', 'rua', comodos=['rua', 'delegacia', 'clinica', 'galeria'], ambiente=True, colisao='nenhuma',
      comprimento_m=3.0)
def fita_isolamento(M):
    p = M.base; X = 1.5
    for xs in (-1, 1):
        t = P(); cone_transito(type('M', (), {'base': t})())
        p.merge(t, trimesh.transformations.translation_matrix([xs * X, 0, 0]))
    img = Image.new('RGB', (1024, 64), (240, 200, 20)); d = ImageDraw.Draw(img)
    for i in range(-2, 22): d.polygon([(i * 50, 64), (i * 50 + 25, 64), (i * 50 + 25 + 64, 0), (i * 50 + 64, 0)], fill=(20, 20, 20))
    mat_imagem('fita_zebra', img, 0.5)
    pts = [(x, 0.66 - 0.06 * (1 - (x / X) ** 2), 0.0) for x in np.linspace(-X + 0.03, X - 0.03, 24)]
    for a, b in zip(pts[:-1], pts[1:]): p.seg('fita_zebra', a, b, 0.002, 0.05)
    p.uv['fita_zebra'] = lambda v, n: np.stack([(v[:, 0] + X) / (2 * X) * 6 % 1, (v[:, 1] - 0.58) / 0.1], 1)
    pts = [(X - 0.03 + 0.05 * s, 0.66 - 0.6 * s, 0.05 + 0.15 * s) for s in np.linspace(0, 1, 6)]                 # ponta solta
    for a, b in zip(pts[:-1], pts[1:]): p.seg('fita_zebra', a, b, 0.05, 0.002)


@item('hidrante', 'Hidrante de calçada', 'mobilias', 'rua', comodos=['rua'], ambiente=True, colisao='caixa',
      coleta={'recurso': 'agua', 'total': 6, 'ferramenta': 'chave_inglesa', 'segundos_por_unidade': 4}, observacao='água só enquanto a rede tiver pressão')
def hidrante(M):
    p = M.base; h = 'hidrante'
    torno(p, h, [(0.13, 0.0), (0.13, 0.04), (0.1, 0.05), (0.1, 0.08), (0.12, 0.09), (0.12, 0.11), (0.095, 0.12), (0.095, 0.5), (0.115, 0.51),
                 (0.115, 0.54), (0.1, 0.55), (0.1, 0.6), (0.06, 0.66), (0.03, 0.68), (0.03, 0.71), (0.0, 0.72)], 32)
    for k in range(8): a = k / 8 * 2 * math.pi; cyl_eixo(p, 'aco', 0.009, 0.095, 0.105, 'y', (0.11 * math.cos(a), 0, 0.11 * math.sin(a)), 8) if False else \
        p.cyl('aco', 0.009, 0.11, 0.125, x=0.11 * math.cos(a), z=0.11 * math.sin(a), sec=8)
    for xs in (-1, 1):
        torno(p, h, [(0.05, 0.0), (0.05, 0.05), (0.055, 0.06), (0.055, 0.08), (0.0, 0.085)], 20, 'x', (xs * 0.09, 0.38, 0)) if xs > 0 else \
            torno(p, h, [(0.0, -0.085), (0.055, -0.08), (0.055, -0.06), (0.05, -0.05), (0.05, 0.0)], 20, 'x', (-0.09, 0.38, 0))
        p.cham('aco', *sorted((xs * 0.17, xs * 0.19)), 0.36, 0.4, -0.02, 0.02, 0.003)
    torno(p, h, [(0.065, 0.0), (0.065, 0.06), (0.07, 0.07), (0.07, 0.1), (0.0, 0.105)], 20, 'z', (0, 0.32, 0.08))
    torno(p, 'aco', [(0.0, 0.0), (0.02, 0.0), (0.02, 0.02)], 5, 'y', (0, 0.72, 0))


@item('orelhao', 'Telefone público', 'mobilias', 'rua', comodos=['rua', 'posto', 'estacao', 'rodoviaria'], ambiente=True, colisao='caixa',
      interacao='fone mudo; às vezes toca de madrugada (evento)')
def orelhao(M):
    p = M.base
    p.cyl('aco_pintado', 0.04, 0.0, 1.95, sec=16); p.cyl('concreto', 0.15, 0.0, 0.04, sec=24)
    t = P(); fofo(t, 'tinta_amarela', 0, 0, 0, 0.45, 0.5, 0.42, 0.6, 0.6, (24, 32))
    ext = t.parts['tinta_amarela'][0]
    ext = trimesh.intersections.slice_mesh_plane(ext, [0, -0.55, -1], [0, -0.2, 0.12], cap=False)   # concha aberta na frente
    inn = ext.copy(); inn.apply_scale(0.95); inn.invert()
    T = trimesh.transformations.translation_matrix([0, 1.55, -0.12]) @ np.diag([1, 1, 0.55, 1])
    for mm, mt in ((ext, 'tinta_amarela'), (inn, 'tinta_amarela')):
        mm = mm.copy(); mm.apply_transform(T); p.add(mt, mm)
    p.cham('aco_pintado', -0.13, 0.13, 1.2, 1.62, -0.24, -0.16, 0.012)                         # aparelho
    p.cham('esmalte_escuro', -0.1, 0.1, 1.42, 1.58, -0.165, -0.16, 0.004)
    for i in range(4):
        for j in range(3): p.cham('aco_polido', -0.05 + j * 0.035 - 0.012, -0.05 + j * 0.035 + 0.012, 1.3 + i * 0.03, 1.32 + i * 0.03, -0.162, -0.155, 0.003)
    varrer(p, 'plastico_preto', circ(0.025, 10), [(-0.16, 1.3, -0.15), (-0.18, 1.42, -0.13), (-0.16, 1.54, -0.15)])   # fone pendurado
    varrer(p, 'aco', circ(0.006, 6), [(-0.16, 1.3, -0.15), (-0.08, 1.0, -0.1), (-0.05, 0.85, -0.12), (0.0, 1.0, -0.16), (0.08, 1.22, -0.17)])


@item('banco_praca', 'Banco de praça', 'mobilias', 'rua', comodos=['rua', 'praca', 'estacao', 'rodoviaria', 'igreja'], ambiente=True, colisao='caixa', sentar=True)
def banco_praca(M):
    p = M.base; L = 1.8
    for xs in (-1, 1):                                                                        # pés de ferro fundido
        x = xs * 0.75
        varrer(p, 'esmalte_escuro', Polygon([(-0.02, -0.03), (0.02, -0.03), (0.02, 0.03), (-0.02, 0.03)]),
               [(x, 0.0, 0.25), (x, 0.42, 0.2), (x, 0.43, -0.2), (x, 0.88, -0.32)])
        varrer(p, 'esmalte_escuro', Polygon([(-0.02, -0.03), (0.02, -0.03), (0.02, 0.03), (-0.02, 0.03)]), [(x, 0.0, -0.24), (x, 0.42, -0.2)])
        varrer(p, 'esmalte_escuro', Polygon([(-0.02, -0.025), (0.02, -0.025), (0.02, 0.025), (-0.02, 0.025)]), [(x, 0.42, 0.22), (x, 0.62, 0.25), (x, 0.64, 0.05)])
    for k in range(5): p.cham('madeira', -L / 2, L / 2, 0.42, 0.45, 0.2 - k * 0.09 - 0.04, 0.2 - k * 0.09 + 0.04, 0.006)
    for k in range(3):
        y = 0.55 + k * 0.11; z = -0.23 - k * 0.03; p.cham('madeira', -L / 2, L / 2, y, y + 0.08, z - 0.015, z + 0.015, 0.006)
    p.uv['madeira'] = uv_caixa(TILE)


@item('lixo_espalhado', 'Lixo espalhado na calçada', 'mobilias', 'rua', comodos=['rua', 'diner', 'posto', 'galeria'], ambiente=True, colisao='nenhuma',
      saque=['comida'], conteiner=True, slots=1, barulho='latas fazem barulho ao chutar')
def lixo_espalhado(M):
    p = M.base; rng = np.random.default_rng(31)
    fofo(p, 'saco_lixo', 0, 0.2, 0, 0.3, 0.22, 0.26, 0.7, 0.6, (14, 18)); torno(p, 'saco_lixo', [(0.04, 0.38), (0.02, 0.46), (0.05, 0.5)], 12)
    fofo(p, 'saco_lixo', 0.42, 0.12, -0.2, 0.22, 0.13, 0.18, 0.7, 0.6, (12, 16))
    for i in range(7):                                                                        # latas amassadas e garrafas
        x, z = rng.uniform(-0.8, 0.8), rng.uniform(-0.6, 0.6); a = rng.uniform(0, math.pi)
        t = P()
        if i % 2: anel(t, 'lata', 0.0, 0.033, -0.06, 0.06, 18, 'x', (0, 0.033, 0)); torno(t, 'lata', [(0.033, -0.062), (0.033, 0.062)], 18, 'x', (0, 0.033, 0))
        else: torno(t, 'pet', [(0.0, -0.13), (0.04, -0.13), (0.042, 0.04), (0.015, 0.1), (0.014, 0.13), (0.0, 0.13)], 18, 'x', (0, 0.042, 0))
        p.merge(t, trimesh.transformations.translation_matrix([x, 0, z]) @ trimesh.transformations.rotation_matrix(a, [0, 1, 0]) @ np.diag([1, 1 - 0.3 * (i % 3 == 1), 1, 1]))
    for i in range(10):
        x, z = rng.uniform(-0.9, 0.9), rng.uniform(-0.7, 0.7); t = P(); t.box('papel' if i % 2 else 'papelao', -0.07, 0.07, 0, 0.002, -0.05, 0.05)
        p.merge(t, trimesh.transformations.translation_matrix([x, 0.001 * i, z]) @ trimesh.transformations.rotation_matrix(rng.uniform(0, 3), [0, 1, 0]))
    t = P(); t.cham('papelao', -0.15, 0.15, 0.0, 0.2, -0.12, 0.12, 0.004)
    p.merge(t, trimesh.transformations.translation_matrix([-0.45, 0, 0.3]) @ trimesh.transformations.rotation_matrix(0.4, [0, 1, 0]) @ trimesh.transformations.rotation_matrix(0.3, [1, 0, 0]))


@item('varal_roupas', 'Varal com roupas', 'mobilias', 'rua', comodos=['quintal', 'casas', 'abrigo', 'motel'], ambiente=True, colisao='nenhuma',
      saque=['roupas'], conteiner=True, slots=3)
def varal_roupas(M):
    p = M.base; X = 1.4; H = 1.8
    for xs in (-1, 1):
        p.cham('madeira_crua', xs * X - 0.035, xs * X + 0.035, 0.0, H + 0.1, -0.035, 0.035, 0.005)
        p.cham('madeira_crua', xs * X - 0.03, xs * X + 0.03, H, H + 0.05, -0.3, 0.3, 0.005)
    p.uv['madeira_crua'] = uv_veio_vertical
    cores = ['cobertor', 'lencol', 'tecido_sofa', 'tecido_cadeira', 'tecido_almofada', 'cobertor_cinza']
    for zs in (-1, 1):
        z = zs * 0.25; pts = [(x, H + 0.02 - 0.08 * (1 - (x / X) ** 2), z) for x in np.linspace(-X, X, 20)]
        varrer(p, 'corda', circ(0.003, 6), pts)
        for k, (x0, w, h) in enumerate(((-1.2, 0.5, 0.7), (-0.55, 0.35, 0.45), (-0.1, 0.9, 0.95), (0.85, 0.35, 0.5))):
            if zs > 0 and k == 2: continue
            yc = H - 0.08 * (1 - ((x0 + w / 2) / X) ** 2)
            mt = cores[(k + (zs > 0) * 2) % len(cores)]
            t = P()
            for i in range(6):
                xa = x0 + w * i / 6; xb = x0 + w * (i + 1) / 6
                t.box(mt, xa, xb, yc - h, yc, z - 0.006 + 0.012 * math.sin(i * 1.3), z + 0.006 + 0.012 * math.sin(i * 1.3))
            p.merge(t)
            for xc in (x0 + 0.03, x0 + w - 0.03): p.cham('plastico_azul', xc - 0.008, xc + 0.008, yc - 0.03, yc + 0.02, z - 0.012, z + 0.012, 0.003)


@item('churrasqueira', 'Churrasqueira de quintal', 'mobilias', 'rua', comodos=['quintal', 'casas', 'abrigo'], ambiente=True, colisao='caixa',
      estacao='cozinhar (como a fogueira, com menos fumaça)', usa='lenha', portatil=True, peso_kg=12.0)
def churrasqueira(M):
    p = M.base
    torno(p, 'esmalte_escuro', [(0.0, 0.55), (0.18, 0.56), (0.27, 0.62), (0.29, 0.72), (0.295, 0.78)], 32, fechar=False)
    torno(p, 'esmalte_escuro', [(0.0, 0.55), (0.18, 0.555)], 32)
    anel(p, 'aco', 0.283, 0.3, 0.77, 0.79, 32)
    for k in range(13): x = -0.26 + k * 0.043; p.seg('aco_polido', (x, 0.765, -math.sqrt(max(0, 0.27 ** 2 - x ** 2))), (x, 0.765, math.sqrt(max(0, 0.27 ** 2 - x ** 2))), 0.005)
    for k in range(3):
        a = k / 3 * 2 * math.pi + 0.5
        p.seg('aco', (0.2 * math.cos(a), 0.58, 0.2 * math.sin(a)), (0.32 * math.cos(a), 0.0, 0.32 * math.sin(a)), 0.022)
    for zs in (-1, 1): _roda(p, (0.3 * math.cos(0.5), 0.06, zs * 0.06 + 0.32 * math.sin(0.5)), 0.06, 0.03) if zs < 0 else None
    q = M.parte('tampa', (0, 0.79, -0.29), 'tampa', eixo='x', abre_graus=-100)
    torno(q, 'esmalte_escuro', [(0.296, 0.79), (0.28, 0.86), (0.22, 0.95), (0.12, 1.0), (0.0, 1.01)], 32)
    torno(q, 'madeira_escura', [(0.03, 1.01), (0.03, 1.05), (0.0, 1.055)], 12)
    for i in range(4):                                                                        # brasas apagadas
        p.sphere('esmalte_escuro', 0.03, -0.1 + i * 0.07, 0.6, 0.05 * (i % 2), 1)


@item('cerca_quebrada', 'Cerca de madeira quebrada', 'mobilias', 'rua', comodos=['quintal', 'rua', 'fazenda'], ambiente=True, colisao='caixa',
      modulo_m=2.0, desmonta={'madeira': 3}, passagem='brecha de 0,6 m: zumbis e jogador passam agachados')
def cerca_quebrada(M):
    p = M.base; X = 1.0; rng = np.random.default_rng(41)
    for xs in (-1, 1): p.cham('madeira_branca', xs * X - 0.045, xs * X + 0.045, 0.0, 1.05, -0.045, 0.045, 0.006)
    p.cham('madeira_branca', -X, X, 0.25, 0.32, 0.045, 0.07, 0.004)
    p.cham('madeira_branca', -X, -0.25, 0.8, 0.87, 0.045, 0.07, 0.004)
    t = P(); t.cham('madeira_branca', 0.0, 0.7, -0.035, 0.035, 0.0, 0.025, 0.004)
    p.merge(t, trimesh.transformations.translation_matrix([-0.25, 0.835, 0.045]) @ _rz(-0.75))
    for k in range(13):
        x = -X + 0.1 + k * 0.142
        if 4 <= k <= 7:
            if k == 5:
                t = P(); t.cham('madeira_branca', -0.04, 0.04, 0.0, 1.1, 0.0, 0.02, 0.004)
                p.merge(t, trimesh.transformations.translation_matrix([x + 0.3, 0.0, 0.4]) @ trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]) @
                        trimesh.transformations.rotation_matrix(0.0, [0, 0, 1]))
            elif k == 6:
                p.hull('madeira_branca', [(x - 0.04, 0.0, 0.07), (x + 0.04, 0.0, 0.07), (x - 0.04, 0.0, 0.09), (x + 0.04, 0.0, 0.09),
                                          (x - 0.04, 0.35, 0.07), (x + 0.01, 0.42, 0.08), (x + 0.04, 0.33, 0.09)])
            continue
        top = 1.1 + rng.uniform(-0.02, 0.02)
        p.cham('madeira_branca', x - 0.04, x + 0.04, 0.02, top - 0.05, 0.07, 0.09, 0.004)
        p.hull('madeira_branca', [(x - 0.04, top - 0.05, 0.07), (x + 0.04, top - 0.05, 0.07), (x - 0.04, top - 0.05, 0.09), (x + 0.04, top - 0.05, 0.09),
                                  (x, top, 0.07), (x, top, 0.09)])
    for k in range(6):
        p.box('grama_seca', -X + rng.uniform(0, 2 * X) - 0.04, -X + rng.uniform(0, 2 * X) + 0.04, 0.0, 0.003, 0.1, 0.3)


@item('mangueira_jardim', 'Mangueira de jardim enrolada', 'mobilias', 'rua', comodos=['quintal', 'casas', 'fazenda'], ambiente=True, colisao='nenhuma',
      portatil=True, peso_kg=3.0, uso='tirar gasolina de carros (com galão) e regar a horta')
def mangueira_jardim(M):
    p = M.base; r = 0.012
    pts = []
    for k in range(5):
        R = 0.2 + k * 0.026
        pts += [(R * math.cos(a), r + 0.0 + 0.002 * k, R * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    pts += [(0.32 + 0.1 * s, r, 0.3 * s) for s in np.linspace(0.05, 1.5, 10)]
    varrer(p, 'mangueira', circ(r, 10), pts)
    torno(p, 'latao', [(0.016, 0.0), (0.016, 0.03), (0.012, 0.035), (0.012, 0.06)], 16, 'z', (0.47, r, 0.45))
