# Lote 4: sobrevivencia e oficina. Executado por gerar_props.py (usa as mesmas funcoes e materiais).
CORES.update({'tinta_verde': (40, 70, 44), 'tinta_azul': (30, 56, 100), 'lona': (110, 112, 78), 'areia': (196, 170, 120),
              'corda': (186, 160, 110), 'pena': (230, 226, 216), 'motor': (80, 82, 86)})
METALICOS.update({'tinta_verde': (0.2, 0.5), 'tinta_azul': (0.25, 0.5), 'motor': (0.7, 0.45)})
TEX_PROPRIAS += [('lona', 'tecido', 0.5, 768), ('corda', 'tecido', 0.25, 1024)]


def _torcido(p, mat, caminho, r, voltas=3):
    """Corda: tubo ao longo do caminho com sulcos em espiral (3 pernas)."""
    cam = np.array(caminho, float); varrer(p, mat, circ(r, 10), cam)
    L = np.cumsum(np.r_[0, np.linalg.norm(np.diff(cam, axis=0), axis=1)])
    for k in range(voltas):
        pts = []
        for s in np.linspace(0, L[-1], max(8, int(L[-1] / (r * 2.5)))):
            i = int(np.clip(np.searchsorted(L, s), 1, len(cam) - 1)); i0 = i - 1
            d = cam[i] - cam[i0]; d = d / (np.linalg.norm(d) + 1e-9); a = np.cross(d, [0, 1, 0])
            if np.linalg.norm(a) < 1e-6: a = np.cross(d, [1, 0, 0])
            a /= np.linalg.norm(a); b = np.cross(d, a); ang = s / (r * 6) * 2 * math.pi + k * 2 * math.pi / voltas
            f_ = (s - L[i0]) / max(L[i] - L[i0], 1e-9)
            pts.append(cam[i0] + (cam[i] - cam[i0]) * f_ + (a * math.cos(ang) + b * math.sin(ang)) * r * 0.92)
        for u, v in zip(pts[:-1], pts[1:]): p.seg(mat, u, v, r * 0.35, r * 0.35)


# ---------------------------------------------------------------------------- MOBILIAS
@item('bancada_trabalho', 'Bancada de trabalho com morsa', 'mobilias', 'oficina', conteiner=True, saque=['ferramentas', 'materiais'], slots=6,
      comodos=['garagem', 'quartel', 'armazem'], estacao='bancada (receitas de armas, barricadas e reparos)')
def bancada_trabalho(M):
    p = M.base; X, Z, H, mat = 0.9, 0.35, 0.9, 'madeira_crua'
    for k in range(6): p.cham(mat, -X, X, H - 0.06, H, -Z + k * (2 * Z / 6) + 0.002, -Z + (k + 1) * (2 * Z / 6) - 0.002, 0.004)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham(mat, xs * (X - 0.07) - 0.04, xs * (X - 0.07) + 0.04, 0.0, H - 0.06, zs * (Z - 0.06) - 0.04, zs * (Z - 0.06) + 0.04, 0.005)
        p.cham(mat, xs * (X - 0.07) - 0.03, xs * (X - 0.07) + 0.03, 0.15, 0.22, -Z + 0.06, Z - 0.06, 0.004)
    for zs in (-1, 1): p.cham(mat, -X + 0.07, X - 0.07, 0.15, 0.22, zs * (Z - 0.06) - 0.03, zs * (Z - 0.06) + 0.03, 0.004)
    for k in range(5): p.cham(mat, -X + 0.08, X - 0.08, 0.22, 0.24, -Z + 0.08 + k * 0.11, -Z + 0.17 + k * 0.11, 0.003)
    p.cham(mat, -X, X, H, 1.75, -Z - 0.02, -Z + 0.0, 0.004)                                  # painel de ferramentas
    for i in range(16):
        for j in range(8): cyl_eixo(p, 'esmalte_escuro', 0.003, -Z + 0.0, -Z + 0.0005, 'z', (-X + 0.08 + i * 0.105, H + 0.1 + j * 0.09, 0), 6)
    for i, x in enumerate((-0.6, -0.45, -0.3)):                                          # ferramentas penduradas (silhuetas)
        cyl_eixo(p, 'aco', 0.003, -Z, -Z + 0.04, 'z', (x, 1.55, 0), 6)
    p.cham('madeira', -0.62, -0.58, 1.25, 1.53, -Z + 0.01, -Z + 0.03, 0.006); p.cham('aco', -0.65, -0.55, 1.5, 1.54, -Z + 0.005, -Z + 0.035, 0.004)
    p.cham('plastico_vermelho', -0.47, -0.43, 1.32, 1.45, -Z + 0.01, -Z + 0.03, 0.006); p.cham('aco_polido', -0.456, -0.444, 1.45, 1.54, -Z + 0.015, -Z + 0.025, 0.002)
    p.cham('tinta_azul', 0.45, 0.75, H, H + 0.03, -0.1, 0.2, 0.004)                         # morsa
    p.cham('tinta_azul', 0.52, 0.68, H + 0.03, H + 0.12, -0.05, 0.02, 0.006); p.cham('tinta_azul', 0.52, 0.68, H + 0.03, H + 0.12, 0.08, 0.15, 0.006)
    for z0 in (0.02, 0.08): p.box('aco_polido', 0.53, 0.67, H + 0.08, H + 0.12, z0 - 0.005 if z0 > 0.05 else z0, z0 + 0.005 if z0 < 0.05 else z0)
    cyl_eixo(p, 'aco_polido', 0.008, 0.15, 0.3, 'z', (0.6, H + 0.07, 0), 12)
    cyl_eixo(p, 'aco_polido', 0.005, 0.52, 0.68, 'x', (0, H + 0.07, 0.3), 8)
    p.cham('ferrugem', -0.4, -0.1, H, H + 0.002, -0.05, 0.2, 0.001)
    g = M.parte('gaveta', (0, 0, 0), 'gaveta', desliza=[0, 0, 0.35])
    g.cham(mat, -0.3, 0.3, H - 0.2, H - 0.07, Z - 0.02, Z, 0.004); carcaca(g, mat, -0.28, 0.28, H - 0.19, H - 0.08, -Z + 0.05, Z - 0.02, t=0.012, topo=False)
    puxador_barra(g, 'aco', H - 0.135, -0.08, 0.08, Z, eixo='x')
    p.box(mat, -0.31, -0.29, H - 0.2, H - 0.06, -Z + 0.05, Z - 0.02); p.box(mat, 0.29, 0.31, H - 0.2, H - 0.06, -Z + 0.05, Z - 0.02)


@item('fogareiro', 'Fogareiro a gás de camping', 'mobilias', 'abrigo', comodos=['abrigo', 'casas'], estacao='fogão (cozinhar, ferver água)', portatil=True,
      peso_kg=3.0)
def fogareiro(M):
    p = M.base; X, Z, H = 0.28, 0.16, 0.09
    p.cham('tinta_verde', -X, X, 0.0, H, -Z, Z, 0.008)
    p.box('esmalte_escuro', -X + 0.01, X - 0.01, H - 0.002, H + 0.001, -Z + 0.01, Z - 0.01)
    for xs in (-1, 1):
        cx = xs * 0.13
        torno(p, 'aco', [(0.05, H), (0.045, H + 0.012), (0.035, H + 0.02)], 20, 'y', (cx, 0, 0))
        for a in range(4):
            ang = a * math.pi / 2 + math.pi / 4; dx, dz = math.cos(ang), math.sin(ang)
            p.seg('esmalte_escuro', (cx + dx * 0.04, H + 0.03, dz * 0.04), (cx + dx * 0.09, H + 0.03, dz * 0.09), 0.006, 0.008)
        torno(p, 'plastico_preto', [(0.014, 0), (0.014, 0.012), (0, 0.014)], 14, 'z', (cx, H * 0.5, Z))
    for xs in (-1, 1): p.cham('tinta_verde', *sorted((xs * X, xs * (X - 0.01))), H, H + 0.12, -Z, -Z + 0.01, 0.003)
    p.cham('tinta_verde', -X, X, H, H + 0.12, -Z - 0.01, -Z, 0.003)
    torno(p, 'tinta_amarela', [(0.0, 0.0), (0.034, 0.0), (0.035, 0.01), (0.035, 0.13), (0.03, 0.15), (0.012, 0.16), (0.012, 0.175), (0.0, 0.176)], 24, 'x', (X + 0.01, 0.035, 0.0))
    for x in np.linspace(-0.2, 0.2, 6): p.box('borracha', x - 0.01, x + 0.01, 0.025, 0.065, Z, Z + 0.001)


def _cama_simples(p, y, X, Z, mat):
    p.cham(mat, -X, X, y - 0.06, y, -Z, -Z + 0.04, 0.004); p.cham(mat, -X, X, y - 0.06, y, Z - 0.04, Z, 0.004)
    p.cham(mat, -X, -X + 0.04, y - 0.06, y, -Z, Z, 0.004); p.cham(mat, X - 0.04, X, y - 0.06, y, -Z, Z, 0.004)
    for z in np.linspace(-Z + 0.12, Z - 0.12, 8): p.box('madeira_crua', -X + 0.04, X - 0.04, y - 0.03, y - 0.01, z - 0.04, z + 0.04)
    fofo(p, 'colchao', 0, y + 0.06, 0, X - 0.045, 0.075, Z - 0.05, 0.15, 0.12, (12, 32))
    fofo(p, 'cobertor', 0, y + 0.075, 0.25, X - 0.03, 0.07, Z - 0.3, 0.12, 0.1, (12, 28))
    fofo(p, 'travesseiro', 0, y + 0.16, -Z + 0.22, X - 0.15, 0.05, 0.15, 0.35, 0.45, (12, 20), rot_x=-0.15)


@item('beliche', 'Beliche de abrigo', 'mobilias', 'abrigo', deitar=True, comodos=['quartel', 'abrigo', 'motel'], estacao='cama (2 moradores)', vagas=2)
def beliche(M):
    p = M.base; X, Z, mat = 0.47, 0.99, 'aco_pintado'
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham(mat, xs * (X - 0.02) - 0.022, xs * (X - 0.02) + 0.022, 0.0, 1.75, zs * (Z - 0.02) - 0.022, zs * (Z - 0.02) + 0.022, 0.004)
    _cama_simples(p, 0.35, X, Z, mat); _cama_simples(p, 1.25, X, Z, mat)
    for zs in (-1, 1):
        for y in (1.45, 1.65): cyl_eixo(p, mat, 0.012, -X + 0.02, X - 0.02, 'x', (0, y, zs * (Z - 0.02)), 10)
    cyl_eixo(p, mat, 0.012, -Z + 0.5, Z - 0.02, 'z', (X - 0.02, 1.5, 0), 10)
    for y in np.arange(0.5, 1.3, 0.25): cyl_eixo(p, mat, 0.011, -X - 0.0, X + 0.0, 'x', (0, y, Z + 0.03), 10)
    for xs in (-1, 1): p.cham(mat, xs * (X - 0.06) - 0.015, xs * (X - 0.06) + 0.015, 0.4, 1.35, Z + 0.015, Z + 0.045, 0.003)


@item('mesa_radio', 'Mesa de rádio amador', 'mobilias', 'abrigo', comodos=['correios', 'quartel', 'abrigo'], estacao='rádio (recruta sobreviventes, eventos)',
      usa='energia')
def mesa_radio(M):
    p = M.base; X, Z = 0.6, 0.32
    p.cham('madeira_escura', -X, X, 0.72, 0.75, -Z, Z, 0.005)
    for xs in (-1, 1):
        for zs in (-1, 1): p.cham('madeira_escura', xs * (X - 0.04) - 0.025, xs * (X - 0.04) + 0.025, 0.0, 0.72, zs * (Z - 0.04) - 0.025, zs * (Z - 0.04) + 0.025, 0.004)
    p.cham('madeira_escura', -X + 0.04, X - 0.04, 0.64, 0.72, -Z + 0.03, -Z + 0.05, 0.004)
    x0, x1, y0, y1, z0, z1 = -0.35, 0.15, 0.75, 0.95, -0.28, 0.0
    p.cham('motor', x0, x1, y0, y1, z0, z1, 0.008)
    p.box('esmalte_escuro', x0 + 0.02, x1 - 0.02, y0 + 0.02, y1 - 0.02, z1, z1 + 0.003)
    p.box('lamp_glass', x0 + 0.04, x0 + 0.2, y1 - 0.09, y1 - 0.04, z1 + 0.003, z1 + 0.005)
    for i in range(18): p.box('esmalte_escuro', x0 + 0.05 + i * 0.008, x0 + 0.0505 + i * 0.008, y1 - 0.085, y1 - 0.06 if i % 3 else y1 - 0.05, z1 + 0.005, z1 + 0.006)
    torno(p, 'aco_polido', [(0.035, 0), (0.035, 0.02), (0.028, 0.03), (0.0, 0.031)], 24, 'z', (x1 - 0.1, y0 + 0.09, z1 + 0.003))
    for k in range(4): torno(p, 'plastico_preto', [(0.012, 0), (0.012, 0.015), (0.0, 0.017)], 14, 'z', (x0 + 0.05 + k * 0.05, y0 + 0.05, z1 + 0.003))
    p.cham('motor', 0.22, 0.48, 0.75, 0.88, -0.28, -0.06, 0.008)                           # fonte
    for i in range(8): p.box('esmalte_escuro', 0.24, 0.46, 0.77 + i * 0.012, 0.774 + i * 0.012, -0.0605, -0.059)
    torno(p, 'plastico_preto', [(0.04, 0.75), (0.035, 0.76), (0.008, 0.77)], 20, 'y', (0.3, 0, 0.12))
    p.seg('plastico_preto', (0.3, 0.77, 0.12), (0.3, 0.88, 0.1), 0.01, 0.01)
    p.cham('plastico_preto', 0.28, 0.32, 0.88, 0.96, 0.08, 0.11, 0.012)
    varrer(p, 'plastico_preto', circ(0.003, 6), [(0.3, 0.76, 0.1), (0.2, 0.752, 0.05), (0.1, 0.752, -0.0), (0.0, 0.76, 0.0)])
    p.cham('papel', -0.5, -0.38, 0.75, 0.752, 0.02, 0.24, 0.001)


@item('gerador', 'Gerador portátil a gasolina', 'mobilias', 'oficina', comodos=['posto', 'quartel', 'garagem'], estacao='gerador (energia, faz barulho)',
      usa='combustivel', peso_kg=45.0)
def gerador(M):
    p = M.base; X, Z = 0.32, 0.25; m = 'motor'
    for xs in (-1, 1):
        for zs in (-1, 1): cyl_eixo(p, 'aco', 0.014, 0.0, 0.55, 'y', (xs * X, 0, zs * Z), 12)
        cyl_eixo(p, 'aco', 0.014, -Z, Z, 'z', (xs * X, 0.55, 0), 12); cyl_eixo(p, 'aco', 0.014, -Z, Z, 'z', (xs * X, 0.02, 0), 12)
    for zs in (-1, 1): cyl_eixo(p, 'aco', 0.014, -X, X, 'x', (0, 0.02, zs * Z), 12)
    cyl_eixo(p, 'aco', 0.014, -X, X, 'x', (0, 0.55, 0.0), 12)
    p.cham('tinta_amarela', -0.25, 0.22, 0.42, 0.54, -0.18, 0.18, 0.04)                    # tanque
    torno(p, 'plastico_preto', [(0.03, 0.54), (0.03, 0.56), (0.025, 0.565)], 20, 'y', (0.05, 0, 0.0))
    cyl_eixo(p, m, 0.12, -0.28, -0.04, 'x', (0, 0.24, 0.0), 28)                             # alternador
    for x in np.linspace(-0.26, -0.06, 9): anel(p, m, 0.12, 0.128, x, x + 0.008, 28, 'x', (0, 0.24, 0))
    p.cham(m, -0.04, 0.2, 0.07, 0.36, -0.13, 0.13, 0.02)                                     # motor
    for y in np.linspace(0.25, 0.35, 5): p.box(m, 0.0, 0.18, y, y + 0.008, 0.13, 0.15)
    p.cham('esmalte_escuro', 0.2, 0.3, 0.12, 0.3, -0.12, 0.0, 0.02)                          # escapamento
    cyl_eixo(p, 'aco', 0.015, 0.3, 0.34, 'x', (0, 0.16, -0.06), 12)
    p.cham('tinta_amarela', 0.2, 0.3, 0.12, 0.3, 0.02, 0.15, 0.015)
    torno(p, 'plastico_preto', [(0.0, 0.0), (0.014, 0.0), (0.014, 0.05), (0.0, 0.05)], 12, 'x', (0.3, 0.25, 0.08))
    p.cham('plastico_preto', -0.3, -0.27, 0.3, 0.45, -0.12, 0.12, 0.006)                     # painel
    for i, z in enumerate((-0.07, 0.0, 0.07)):
        cyl_eixo(p, 'plastico_vermelho' if i == 0 else 'plastico_preto', 0.012, -0.315, -0.3, 'x', (0, 0.4, z), 14)
    p.box('lamp_glass', -0.306, -0.3, 0.34, 0.355, -0.02, 0.02)


@item('tambor_200l', 'Tambor de 200 L', 'mobilias', 'deposito', conteiner=True, saque=['combustivel', 'agua', 'materiais'], slots=4, barricada=True,
      comodos=['posto', 'garagem', 'armazem', 'estacao'], estacao='coletor de chuva ou fogueira de lata')
def tambor_200l(M):
    p = M.base; r, h = 0.29, 0.88
    perf = [(r - 0.01, 0.0), (r, 0.008), (r, 0.02), (r + 0.004, 0.026), (r, 0.034)]
    for y in (h / 3, 2 * h / 3): perf += [(r, y - 0.02), (r + 0.008, y - 0.01), (r + 0.008, y + 0.01), (r, y + 0.02)]
    perf += [(r, h - 0.034), (r + 0.004, h - 0.026), (r, h - 0.02), (r, h - 0.008), (r - 0.01, h), (r - 0.012, h - 0.008), (0.0, h - 0.008)]
    torno(p, 'tinta_azul', perf, 40)
    anel(p, 'ferrugem', r - 0.0005, r + 0.001, 0.05, 0.16, 40)
    p.cyl('aco', 0.028, h - 0.008, h - 0.0, x=0.17, z=0.0, sec=16); p.cyl('aco', 0.014, h - 0.008, h - 0.002, x=-0.18, z=0.05, sec=12)


@item('pallet', 'Pallet de madeira', 'mobilias', 'deposito', comodos=['armazem', 'supermercado', 'estacao', 'posto'], desmontavel='4 madeira',
      barricada=True)
def pallet(M):
    p = M.base; X, Z, mat = 0.6, 0.4, 'madeira_crua'; H = 0.144
    for zz in (-Z + 0.05, 0.0, Z - 0.05):
        for xx in (-X + 0.05, 0.0, X - 0.05): p.cham(mat, xx - 0.05, xx + 0.05, 0.022, 0.122, zz - 0.05, zz + 0.05, 0.004)
    for zz in (-Z + 0.05, 0.0, Z - 0.05): p.cham(mat, -X, X, 0.0, 0.022, zz - 0.05, zz + 0.05, 0.003)
    for i, xx in enumerate(np.linspace(-X + 0.05, X - 0.05, 7)): p.cham(mat, xx - 0.05, xx + 0.05, 0.122, H, -Z, Z, 0.003)
    for xx in np.linspace(-X + 0.05, X - 0.05, 7):
        for zz in (-Z + 0.05, 0.0, Z - 0.05): p.cyl('aco', 0.004, H - 0.0005, H + 0.001, x=xx, z=zz, sec=6)


# ---------------------------------------------------------------------------- LOOT
@item('arco', 'Arco e flechas', 'loot', 'armas', recurso='arma', valor=1, peso_kg=1.0, empilha=1, arma=True, dano=35, distancia=True,
      onde=['casa_de_campo', 'galeria', 'armazem'], efeito='arma silenciosa à distância (flechas reaproveitáveis)', pega=[0, 0.02, 0])
def arco(M):
    p = M.base; y = 0.02
    cam = [(0.6 * math.sin(t) * 1.0, y, 0.12 * math.cos(t) - 0.12) for t in np.linspace(-1.2, 1.2, 15)]
    perf = Polygon([(-0.011, -0.008), (0.011, -0.008), (0.011, 0.008), (-0.011, 0.008)])
    varrer(p, 'madeira', perf, cam)
    p.cham('fita_preta', -0.05, 0.05, y - 0.014, y + 0.014, -0.03, 0.0, 0.006)
    a, b = np.array(cam[0]), np.array(cam[-1]); p.seg('fita_preta', a, b, 0.0016, 0.0016)
    for k in range(3):
        z = 0.08 + k * 0.03; L = 0.7
        cyl_eixo(p, 'madeira_crua', 0.004, -L / 2, L / 2, 'x', (0, 0.006, z), 8)
        torno(p, 'aco', [(0.0, 0.0), (0.006, 0.0), (0.0, 0.03)], 8, 'x', (L / 2, 0.006, z))
        for s in (-1, 1): p.hull('pena', [(-L / 2 + 0.01, 0.006, z), (-L / 2 + 0.1, 0.006, z), (-L / 2 + 0.02, 0.006 + s * 0.012, z), (-L / 2 + 0.08, 0.006 + s * 0.008, z), (-L / 2 + 0.05, 0.006, z + 0.001)])


@item('lanca', 'Lança improvisada', 'loot', 'armas', recurso='arma', valor=1, peso_kg=1.4, empilha=1, arma=True, dano=32,
      onde=['quartel', 'casas'], efeito='alcance longo para manter zumbis longe (receita: cabo + faca + fita)', pega=[-0.3, 0.02, 0])
def lanca(M):
    p = M.base; L = 1.6; y = 0.018
    cyl_eixo(p, 'madeira_crua', 0.016, -L / 2, L / 2 - 0.12, 'x', (0, y, 0), 14)
    lam = Polygon([(L / 2 - 0.15, -0.012), (L / 2 - 0.03, -0.012), (L / 2, 0.0), (L / 2 - 0.05, 0.016), (L / 2 - 0.15, 0.016)])
    extrudar_xz(p, 'aco_polido', lam, y - 0.0015, y + 0.0015)
    for x in np.linspace(L / 2 - 0.2, L / 2 - 0.1, 9): anel(p, 'fita_prata', 0.0158, 0.0185, x, x + 0.012, 16, 'x', (0, y, 0))
    for x in np.linspace(-L / 2 + 0.1, -L / 2 + 0.35, 14): anel(p, 'tecido_cinza', 0.0158, 0.0182, x, x + 0.017, 16, 'x', (0, y, 0))


@item('facao', 'Facão', 'loot', 'armas', recurso='ferramenta', valor=5, peso_kg=0.7, empilha=1, arma=True, dano=38,
      onde=['casa_de_campo', 'armazem', 'garagem'], efeito='corta mato e arma forte e silenciosa', pega=[-0.2, 0.012, 0])
def facao(M):
    p = M.base
    lam = Polygon([(-0.12, -0.02), (0.3, -0.026), (0.36, -0.012), (0.37, 0.006), (0.33, 0.02), (-0.12, 0.018)])
    extrudar_xz(p, 'aco', lam, 0.009, 0.0125)
    extrudar_xz(p, 'aco_polido', Polygon([(-0.11, -0.02), (0.3, -0.026), (0.36, -0.012), (0.36, -0.006), (0.3, -0.014), (-0.11, -0.01)]), 0.0088, 0.0127)
    p.cham('madeira_escura', -0.27, -0.12, 0.0, 0.022, -0.017, 0.018, 0.006)
    for x in (-0.24, -0.15): p.cyl('cobre', 0.004, 0.021, 0.0225, x=x, z=0.0, sec=10)
    p.cham('aco', -0.125, -0.115, 0.0, 0.022, -0.026, 0.026, 0.002)


@item('serrote', 'Serrote', 'loot', 'ferramentas', recurso='ferramenta', valor=4, peso_kg=0.6, empilha=1,
      onde=['garagem', 'armazem', 'casas'], efeito='corta tábuas: dobra a madeira de móveis desmontados', pega=[-0.27, 0.012, 0])
def serrote(M):
    p = M.base
    lam = Polygon([(-0.2, -0.06), (0.32, -0.035), (0.34, -0.02), (0.34, 0.0), (-0.2, 0.06)])
    extrudar_xz(p, 'aco_polido', lam, 0.0105, 0.0115)
    dentes = [(x, -0.06 + (x + 0.2) / 0.52 * 0.025) for x in np.linspace(-0.2, 0.32, 70)]
    pts = []
    for i, (x, z) in enumerate(dentes): pts.append((x, z - (0.004 if i % 2 else 0.0)))
    extrudar_xz(p, 'aco', Polygon(pts + [(0.32, -0.03), (-0.2, -0.055)]).buffer(0), 0.0106, 0.0114)
    cabo = Polygon([(-0.32, -0.06), (-0.19, -0.065), (-0.19, 0.07), (-0.3, 0.075), (-0.34, 0.03)]).difference(Polygon([(-0.29, -0.035), (-0.22, -0.035), (-0.22, 0.04), (-0.28, 0.045)]))
    extrudar_xz(p, 'madeira', cabo, 0.0, 0.022)
    for z in (-0.04, 0.05): p.cyl('cobre', 0.005, 0.021, 0.023, x=-0.2, z=z, sec=10)


@item('pa', 'Pá', 'loot', 'agricultura', recurso='ferramenta', valor=4, peso_kg=1.8, empilha=1, arma=True, dano=26,
      onde=['armazem', 'casa_de_campo', 'garagem', 'quartel'], efeito='cava hortas, valas e covas; arma pesada', pega=[-0.3, 0.02, 0])
def pa(M):
    p = M.base; y = 0.02
    cyl_eixo(p, 'madeira_crua', 0.017, -0.6, 0.38, 'x', (0, y, 0), 14)
    varrer(p, 'plastico_preto', circ(0.01, 10), [(-0.6, y, -0.06), (-0.7, y, -0.06), (-0.7, y, 0.06), (-0.6, y, 0.06)])
    p.cham('plastico_preto', -0.71, -0.68, y - 0.013, y + 0.013, -0.06, 0.06, 0.008); p.seg('madeira_crua', (-0.6, y, 0), (-0.62, y, -0.055), 0.02, 0.02); p.seg('madeira_crua', (-0.6, y, 0), (-0.62, y, 0.055), 0.02, 0.02)
    torno(p, 'aco', [(0.02, 0.0), (0.02, 0.1), (0.017, 0.14)], 14, 'x', (0.36, y, 0))
    lam = Polygon([(0.5, -0.12), (0.76, -0.12), (0.83, 0.0), (0.76, 0.12), (0.5, 0.12), (0.47, 0.0)])
    m = trimesh.creation.extrude_polygon(lam, 0.003); m.vertices = np.stack([m.vertices[:, 0], 0.002 + m.vertices[:, 2] + 0.035 * (np.abs(m.vertices[:, 1]) / 0.12) ** 2, -m.vertices[:, 1]], 1)
    p.add('aco', _fix(m))
    p.hull('aco', [(0.47, y + dy, dz) for dy in (-0.012, 0.012) for dz in (-0.02, 0.02)] + [(0.53, 0.004, dz) for dz in (-0.05, 0.05)])


@item('enxada', 'Enxada', 'loot', 'agricultura', recurso='ferramenta', valor=4, peso_kg=1.5, empilha=1, arma=True, dano=28,
      onde=['armazem', 'casa_de_campo'], efeito='prepara canteiros da horta (+50% colheita)', pega=[-0.3, 0.018, 0])
def enxada(M):
    p = M.base; y = 0.018
    cyl_eixo(p, 'madeira_crua', 0.016, -0.7, 0.62, 'x', (0, y, 0), 14)
    p.cham('aco', 0.58, 0.64, 0.0, 0.04, -0.025, 0.025, 0.006)
    lam = Polygon([(0.59, 0.02), (0.63, 0.02), (0.65, 0.2), (0.62, 0.21), (0.57, 0.2)])
    m = trimesh.creation.extrude_polygon(lam, 0.0035); m.vertices = np.stack([m.vertices[:, 0], 0.001 + m.vertices[:, 2], m.vertices[:, 1]], 1)
    p.add('aco', _fix(m))
    blade = Polygon([(0.52, 0.17), (0.72, 0.17), (0.73, 0.24), (0.51, 0.24)])
    m = trimesh.creation.extrude_polygon(blade, 0.003); m.vertices = np.stack([m.vertices[:, 0], 0.001 + m.vertices[:, 2], m.vertices[:, 1]], 1)
    p.add('aco', _fix(m)); p.box('aco_polido', 0.51, 0.73, 0.001, 0.0041, 0.236, 0.242)


@item('corda', 'Rolo de corda', 'loot', 'materiais', recurso='material', valor=1, peso_kg=1.5, empilha=3,
      onde=['armazem', 'quartel', 'garagem', 'estacao'], efeito='armadilhas, escalar e amarrar barricadas (10 m)')
def corda(M):
    p = M.base; R, r = 0.1, 0.006
    for k in range(5):
        rr = R - 0.012 * (k % 2); y0 = r + (k // 2) * 0.011
        cam = [(rr * math.cos(a), y0 + 0.002 * math.sin(3 * a), rr * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 41)]
        _torcido(p, 'corda', cam, r)
    _torcido(p, 'corda', [(R, r, 0), (R + 0.05, r, 0.03), (R + 0.11, r, 0.02)], r)
    p.cham('fita_preta', -0.012, 0.012, 0.0, 0.035, R - 0.03, R + 0.01, 0.006)


@item('arame_farpado', 'Rolo de arame farpado', 'loot', 'materiais', recurso='sucata', valor=3, peso_kg=6.0, empilha=1,
      onde=['armazem', 'casa_de_campo', 'quartel'], efeito='defesa: segura e fere zumbis no muro')
def arame_farpado(M):
    p = M.base; R, L = 0.2, 0.3
    voltas = 9; pts = [((t / (2 * math.pi * voltas) - 0.5) * L, R + R * math.sin(t), R * math.cos(t)) for t in np.linspace(0, 2 * math.pi * voltas, voltas * 24)]
    for a, b in zip(pts[:-1], pts[1:]): p.seg('ferrugem', a, b, 0.003, 0.003)
    for i in range(0, len(pts), 4):
        c = np.array(pts[i])
        for d in ((0.012, 0.012, 0), (-0.012, 0.012, 0)): p.seg('aco', c, c + np.array([d[0], d[1] * math.cos(i), d[1] * math.sin(i)]), 0.0015, 0.0015)


@item('saco_areia', 'Saco de areia', 'loot', 'materiais', recurso='material', valor=1, peso_kg=18.0, empilha=1,
      onde=['quartel', 'armazem', 'estacao'], efeito='defesa: 3 sacos = 1 m de trincheira à prova de mordida')
def saco_areia(M):
    p = M.base
    fofo(p, 'lona', 0, 0.065, 0, 0.3, 0.065, 0.17, 0.35, 0.2, (16, 28))
    fofo(p, 'lona', 0.29, 0.05, 0.0, 0.03, 0.035, 0.12, 0.5, 0.4, (10, 14))
    _torcido(p, 'corda', [(0.3, 0.07, -0.13), (0.31, 0.09, 0.0), (0.3, 0.07, 0.13)], 0.004)


@item('peca_motor', 'Caixa de peças de motor', 'loot', 'energia', recurso='pecas', valor=1, peso_kg=2.5, empilha=2,
      onde=['posto', 'garagem', 'estacao'], efeito='repara o gerador e a subestação (marco da fase 4)')
def peca_motor(M):
    p = M.base; X, H, Z = 0.14, 0.09, 0.1
    for (a0, a1, b0, b1) in ((-X, X, -Z, -Z + 0.006), (-X, X, Z - 0.006, Z), (-X, -X + 0.006, -Z, Z), (X - 0.006, X, -Z, Z)):
        p.box('papelao', a0, a1, 0.0, H, b0, b1)
    p.box('papelao', -X, X, 0.0, 0.004, -Z, Z)
    for s, ang in ((-1, 0.35), (1, -0.25)):
        m = trimesh.creation.box(extents=[0.002, 0.09, 2 * Z]); m.apply_translation([0, 0.045, 0])
        m.apply_transform(trimesh.transformations.rotation_matrix(s * (math.pi / 2 + ang), [0, 0, 1])); m.apply_translation([s * X, H, 0]); p.add('papelao', m)
    for i, (x, z) in enumerate(((-0.07, -0.04), (-0.03, 0.04), (0.02, -0.05))):         # velas de ignicao
        c = (x, 0.06, z)
        torno(p, 'aco_polido', [(0.0, 0.0), (0.006, 0.0), (0.007, 0.014), (0.01, 0.016), (0.01, 0.026)], 6, 'y', c)
        torno(p, 'plastico_branco', [(0.008, 0.026), (0.007, 0.05), (0.004, 0.065)], 16, 'y', c)
    cyl_eixo(p, 'motor', 0.035, -0.002, 0.03, 'z', (0.07, 0.06, 0.0), 24)                  # engrenagem
    for k in range(16):
        a = k * 2 * math.pi / 16; p.box('motor', 0.07 + 0.038 * math.cos(a) - 0.004, 0.07 + 0.038 * math.cos(a) + 0.004, 0.06 + 0.038 * math.sin(a) - 0.004, 0.06 + 0.038 * math.sin(a) + 0.004, -0.002, 0.03)
    p.box('tinta_vermelha', -X + 0.03, X - 0.03, 0.03, 0.06, Z, Z + 0.001)
