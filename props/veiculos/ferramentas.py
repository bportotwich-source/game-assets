# Ferramentas e materiais de oficina (loot) para desmontar, montar e manter os carros. Carregado por gerar_veiculos.py.
# Itens deitados na pose de repouso; a exportação põe o pivô no centro da base.
from forma import tubo as _tubo, varrer_caminho as _varrer, menos as _menos, chaikin as _chaikin, caixa as _caixa, cil_x as _cilx
from forma import suavizar_caminho as _suave

_ONDE_OF = ['garagem', 'posto', 'concessionaria', 'ferro_velho', 'porta_malas']


def _cy(r, y0, y1, x=0.0, z=0.0, sec=24):
    c = trimesh.creation.cylinder(radius=r, height=y1 - y0, sections=sec); c.apply_transform(TF.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    c.apply_translation([x, (y0 + y1) / 2, z]); return c


def _cz(r, z0, z1, x=0.0, y=0.0, sec=24):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sec); c.apply_translation([x, y, (z0 + z1) / 2]); return c


def _bobina(r, larg, voltas, rfio, y0=0.0, n=220, x0=0.0, z0=0.0):
    """Cabo ou mangueira enrolado deitado (espiral em planta, subindo devagar)."""
    pts = []
    for t in np.linspace(0, voltas * 2 * math.pi, n):
        rr = r + larg * (t / (voltas * 2 * math.pi)) * (0.5 + 0.5 * math.sin(3 * t))
        pts.append((x0 + rr * math.cos(t), y0 + rfio + 0.6 * rfio * (math.sin(t * 0.5) + 1) * 0.5 + 1.6 * rfio * (t / (voltas * 2 * math.pi)), z0 + rr * math.sin(t)))
    return pts


@ferramenta('chave_de_roda', 'Chave de roda em cruz', peso_kg=1.3, celulas=[2, 2], empilha=1, onde=_ONDE_OF,
            efeito='tira e põe as rodas (com o macaco)', recurso='ferramenta', valor=1, arma=True, dano=14)
def chave_de_roda(p):
    L = 0.19; y = 0.012
    for a in range(4):
        ang = a * math.pi / 2; d = np.array([math.cos(ang), 0, math.sin(ang)])
        p.add('aco_escuro', _tubo([d * 0.02 + [0, y, 0], d * (L - 0.03) + [0, y, 0]], 0.0095, 12))
        q = d * (L - 0.015) + [0, y, 0]
        if a < 3:
            r = (0.0115, 0.0125, 0.0135)[a]
            c = _tubo([d * (L - 0.035) + [0, y, 0], d * L + [0, y, 0]], r + 0.004, 16); p.add('cromado', c)
            p.add('chassi', _tubo([d * (L - 0.004) + [0, y, 0], d * (L + 0.0005) + [0, y, 0]], r * 0.7, 6))
        else:
            p.add('aco_escuro', trimesh.convex.convex_hull(np.array([d * (L - 0.03) + [0, y - 0.009, 0], d * (L - 0.03) + [0, y + 0.009, 0],
                                                                     d * (L + 0.01) + [0, y - 0.002, 0], d * (L + 0.01) + [0, y + 0.002, 0],
                                                                     d * (L - 0.01) + np.cross(d, [0, 1, 0]) * 0.008 + [0, y, 0], d * (L - 0.01) - np.cross(d, [0, 1, 0]) * 0.008 + [0, y, 0]])))
    p.add('aco_escuro', trimesh.creation.icosphere(2, 0.017).apply_translation([0, y, 0]))


@ferramenta('macaco_sanfona', 'Macaco sanfona', peso_kg=3.2, celulas=[3, 1], empilha=1, onde=_ONDE_OF,
            efeito='ergue o carro para trocar roda, tanque e escapamento', recurso='ferramenta', valor=1, ergue_m=0.32, tempo_erguer_s=20)
def macaco_sanfona(p):
    # fechado e deitado para guardar: base comprida, braços quase na horizontal
    p.add('aco_galv', _cham(-0.17, 0.17, 0.0, 0.012, -0.05, 0.05, 0.004))
    for s in (-1, 1): p.add('aco_galv', _cx(-0.17, 0.17, 0.012, 0.03, s * 0.05 - (0.003 if s > 0 else 0), s * 0.05 + (0.003 if s < 0 else 0)))
    for s in (-1, 1):
        for z in (-0.04, 0.04):
            p.add('aco_galv', _tubo([(s * 0.16, 0.025, z), (0.0, 0.065, z)], 0.006, 8))
            p.add('aco_galv', _tubo([(0.0, 0.065, z), (s * 0.16, 0.105, z)], 0.006, 8))
    p.add('aco_galv', _cham(-0.06, 0.06, 0.10, 0.118, -0.045, 0.045, 0.004))
    for s in (-1, 1): p.add('borracha', _cx(-0.05, 0.05, 0.118, 0.124, s * 0.02 - 0.004, s * 0.02 + 0.004))
    rosca = _cilx(0.007, -0.24, 0.20, 0.065, 0.0, 12); p.add('aco', rosca)
    for x in np.linspace(-0.20, 0.18, 40): p.add('aco', _cilx(0.0085, x, x + 0.003, 0.065, 0.0, 10))
    for x in (-0.16, 0.16): p.add('aco_escuro', _cilx(0.016, x - 0.012, x + 0.012, 0.065, 0.0, 6))
    p.add('aco_escuro', trimesh.creation.torus(0.016, 0.005, 20, 8).apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0])).apply_translation([-0.26, 0.065, 0.0]))


@ferramenta('jogo_de_chaves', 'Caixa com jogo de chaves', peso_kg=6.5, celulas=[3, 2], empilha=1, onde=_ONDE_OF + ['oficina', 'fabrica'],
            efeito='ferramenta geral da oficina: quase toda peça pede', recurso='ferramenta', valor=1)
def jogo_de_chaves(p):
    W, H, D = 0.42, 0.16, 0.20
    p.add('azul_ferramenta', _cham(-W / 2, W / 2, 0.0, H * 0.7, -D / 2, D / 2, 0.01))
    p.add('azul_ferramenta', _cham(-W / 2 - 0.002, W / 2 + 0.002, H * 0.7, H, -D / 2 - 0.002, D / 2 + 0.002, 0.012))
    p.add('chassi', _cx(-W / 2 - 0.003, W / 2 + 0.003, H * 0.7 - 0.002, H * 0.7 + 0.002, -D / 2 - 0.003, D / 2 + 0.003))
    for x in (-0.14, 0.14):                                                         # fechos
        p.add('cromado', _cham(x - 0.022, x + 0.022, H * 0.55, H * 0.82, D / 2 + 0.0, D / 2 + 0.008, 0.003))
    for x in (-0.11, 0.11): p.add('aco_escuro', _cy(0.008, H, H + 0.03, x, 0.0, 10))
    p.add('plastico_preto', _tubo([(-0.11, H + 0.03, 0.0), (-0.09, H + 0.05, 0.0), (0.09, H + 0.05, 0.0), (0.11, H + 0.03, 0.0)], 0.011, 12))
    for x in (-W / 2 + 0.03, W / 2 - 0.03):
        for z in (-D / 2 + 0.03, D / 2 - 0.03): p.add('borracha', _cy(0.012, -0.004, 0.0, x, z, 12))
    p.add('cromado', _cx(-0.03, 0.03, H * 0.35, H * 0.45, D / 2, D / 2 + 0.003))


@ferramenta('mangueira_sifao', 'Mangueira para sifão', peso_kg=0.5, celulas=[2, 2], empilha=1, onde=['garagem', 'posto', 'ferro_velho', 'fazenda'],
            efeito='puxa combustível de um tanque para um galão (1 L a cada 6 s)', recurso='ferramenta', valor=1, litros_por_s=1 / 6)
def mangueira_sifao(p):
    p.add('plastico_translucido', _tubo(_bobina(0.075, 0.03, 3.2, 0.008, n=170), 0.008, 8))
    p.add('borracha', trimesh.creation.capsule(0.05, 0.022, (8, 16)).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])).apply_translation([0.135, 0.024, 0.0]))
    p.add('plastico_translucido', _tubo([(0.08, 0.02, 0.0), (0.105, 0.024, 0.0)], 0.008, 10))


@ferramenta('cabos_chupeta', 'Cabos de chupeta', peso_kg=1.6, celulas=[2, 2], empilha=1, onde=_ONDE_OF,
            efeito='dá partida com a bateria de outro carro ou do gerador', recurso='ferramenta', valor=1)
def cabos_chupeta(p):
    p.add('fio_vermelho', _tubo(_bobina(0.085, 0.02, 2.6, 0.006, n=140), 0.006, 8))
    p.add('fio_preto', _tubo(_bobina(0.07, 0.02, 2.6, 0.006, n=140, z0=0.004), 0.006, 8))
    for (x, z, ang, cor) in ((0.13, 0.04, 0.3, 'vermelho_borne'), (0.13, -0.02, -0.2, 'plastico_preto'), (-0.12, 0.08, 2.5, 'vermelho_borne'), (-0.13, -0.05, 3.6, 'plastico_preto')):
        g = V()
        g.add(cor, _cham(0.0, 0.09, 0.006, 0.026, -0.013, 0.013, 0.006))
        g.add(cor, _cham(0.0, 0.09, 0.028, 0.044, -0.011, 0.011, 0.005))
        g.add('cobre', _cx(0.09, 0.12, 0.018, 0.022, -0.009, 0.009)); g.add('cobre', _cx(0.09, 0.12, 0.030, 0.034, -0.009, 0.009))
        g.add('aco', _cilx(0.004, 0.035, 0.045, 0.027, -0.0, 8).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0], [0.04, 0.027, 0])))
        T = TF.translation_matrix([x, 0, z]) @ TF.rotation_matrix(ang, [0, 1, 0])
        for k, ms in g.parts.items():
            for m in ms: mm = m.copy(); mm.apply_transform(T); p.add(k, mm)


@ferramenta('bomba_ar', 'Bomba de ar manual', peso_kg=1.4, celulas=[3, 1], empilha=1, onde=['garagem', 'posto', 'loja', 'porta_malas'],
            efeito='enche pneu murcho (de 30 para 100% em 40 s)', recurso='ferramenta', valor=1)
def bomba_ar(p):
    r = 0.022; y = 0.03
    p.add('plastico_preto', _cilx(r, -0.17, 0.16, y, 0.0, 24))
    p.add('plastico_preto', _cilx(r + 0.004, 0.15, 0.17, y, 0.0, 24))
    p.add('aco', _cilx(0.006, 0.17, 0.21, y, 0.0, 10))
    p.add('plastico_preto', _cham(0.205, 0.225, y - 0.012, y + 0.012, -0.07, 0.07, 0.008))
    p.add('aco_galv', _cham(-0.21, -0.16, 0.0, 0.012, -0.06, 0.06, 0.004))
    p.add('borracha', _tubo(_suave([(-0.16, y - 0.01, 0.02), (-0.10, 0.012, 0.06), (0.05, 0.010, 0.065), (0.12, 0.012, 0.045)], 3), 0.005, 8))
    p.add('cromado', _cilx(0.008, 0.12, 0.15, 0.012, 0.045, 10))
    p.add('plastico_branco', _cy(0.018, y + r - 0.002, y + r + 0.004, -0.05, 0.0, 20))


@ferramenta('kit_remendo_pneu', 'Kit de remendo de pneu', peso_kg=0.3, celulas=[1, 1], empilha=1, usos=5, onde=['garagem', 'posto', 'porta_malas', 'loja'],
            efeito='conserta pneu furado: volta para 60% (5 usos)', recurso='ferramenta', valor=1)
def kit_remendo_pneu(p):
    p.add('plastico_vermelho', _cham(-0.08, 0.08, 0.0, 0.035, -0.05, 0.05, 0.006))
    p.add('plastico_vermelho', _cham(-0.081, 0.081, 0.035, 0.045, -0.051, 0.051, 0.006))
    p.add('plastico_preto', _cx(-0.03, 0.03, 0.045, 0.047, -0.02, 0.02))
    for k in range(3): p.add('borracha', _cx(-0.06 + k * 0.012, -0.055 + k * 0.012, 0.047, 0.052, 0.01, 0.045))
    p.add('plastico_preto', _cham(0.0, 0.07, 0.046, 0.066, -0.045, -0.025, 0.006))
    p.add('aco', _cilx(0.003, 0.07, 0.11, 0.056, -0.035, 8))


@ferramenta('oleo_motor', 'Óleo de motor 1 L', peso_kg=0.95, celulas=[1, 1], empilha=2, onde=_ONDE_OF + ['supermercado'],
            efeito='+15% de condição do motor (até 70%)', recurso='manutencao', valor=1)
def oleo_motor(p):
    pts = _chaikin([(0, 0), (0.05, 0.0), (0.055, 0.01), (0.055, 0.17), (0.04, 0.19), (0.02, 0.205), (0.0, 0.205)], 2, fechado=False)
    m = trimesh.creation.revolve(np.array(pts), sections=40)
    if m.volume < 0: m.invert()
    m.apply_transform(TF.rotation_matrix(-math.pi / 2, [1, 0, 0])); m.apply_transform(np.diag([1.0, 1.0, 0.6, 1.0])); p.add('amarelo_tampa', m)
    p.add('plastico_preto', _cy(0.017, 0.205, 0.232, 0.0, 0.0, 20))
    p.add('azul_ferramenta', _cx(-0.056, 0.056, 0.05, 0.13, 0.034, 0.0345 + 0.0))
    p.add('plastico_branco', _cx(-0.04, 0.04, 0.10, 0.115, 0.0345, 0.0355))
    # deitado
    for k in list(p.parts):
        for mm in p.parts[k]: mm.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1]))


@ferramenta('velas_ignicao', 'Velas de ignição (jogo de 4)', peso_kg=0.3, celulas=[1, 1], empilha=2, onde=['garagem', 'posto', 'concessionaria', 'ferro_velho'],
            efeito='+20% de condição do motor (até 80%) e menos falha na partida', recurso='manutencao', valor=1)
def velas_ignicao(p):
    p.add('papelao', _cham(-0.06, 0.06, 0.0, 0.03, -0.05, 0.05, 0.003))
    p.add('azul_ferramenta', _cx(-0.061, 0.061, 0.01, 0.022, 0.0505, 0.051))
    for k in range(4):
        z = -0.0375 + k * 0.025; y = 0.03 + 0.011
        p.add('plastico_branco', _cilx(0.0075, -0.025, 0.03, y, z, 16))
        p.add('aco', _cilx(0.0095, -0.04, -0.025, y, z, 6))
        p.add('aco', _cilx(0.007, -0.058, -0.04, y, z, 12))
        p.add('aco_escuro', _cilx(0.0025, 0.03, 0.045, y, z, 8))


@ferramenta('chave_carro', 'Chave de carro', peso_kg=0.03, celulas=[1, 1], empilha=1, unico=True, onde=['carro', 'quebra_sol', 'zumbi', 'casa'],
            efeito='abre e liga um carro específico (o item guarda qual)', recurso='chave', valor=1)
def chave_carro(p):
    p.add('plastico_preto', _cham(-0.015, 0.015, 0.0, 0.008, -0.02, 0.012, 0.004))
    lam = _caixa(-0.004, 0.004, 0.0025, 0.0055, 0.012, 0.062)
    p.add('aco', lam)
    for k in range(5): p.add('aco', _cx(-0.004, -0.0005 + 0.0003 * (k % 2), 0.0025, 0.0055, 0.02 + k * 0.008, 0.024 + k * 0.008))
    p.add('aco', trimesh.creation.torus(0.012, 0.0015, 24, 6).apply_translation([0, 0.004, -0.035]).apply_transform(np.eye(4)) if False else
          trimesh.creation.torus(0.012, 0.0015, 24, 6).apply_transform(TF.rotation_matrix(math.pi / 2, [1, 0, 0])).apply_translation([0, 0.0016, -0.033]))
    p.add('papelao', _cham(-0.012, 0.012, 0.0, 0.002, -0.085, -0.045, 0.001))
    p.add('fio_vermelho', _cx(-0.0008, 0.0008, 0.0005, 0.0015, -0.048, -0.022))


@ferramenta('kit_ligacao_direta', 'Kit de ligação direta', peso_kg=0.35, celulas=[2, 1], empilha=1, onde=['garagem', 'ferro_velho', 'delegacia', 'zumbi'],
            efeito='liga o carro sem chave: 20 s, 70% de chance (falha queima um fusível)', recurso='ferramenta', valor=1)
def kit_ligacao_direta(p):
    p.add('amarelo_tampa', _cilx(0.012, -0.12, -0.02, 0.012, 0.0, 6))
    p.add('aco', _cilx(0.003, -0.02, 0.09, 0.012, 0.0, 8))
    p.add('aco', _cx(0.085, 0.10, 0.011, 0.013, -0.004, 0.004))
    for k, cor in enumerate(('fio_vermelho', 'fio_preto', 'fio_vermelho')):
        z = 0.03 + k * 0.012
        p.add(cor, _tubo(_suave([(-0.11, 0.004, z), (-0.03, 0.006, z + 0.01), (0.04, 0.004, z - 0.005), (0.10, 0.005, z + 0.004)], 3), 0.0025, 6))
        p.add('vermelho_borne' if cor == 'fio_vermelho' else 'plastico_preto', _cham(0.10, 0.13, 0.0, 0.012, z - 0.006, z + 0.006, 0.003))
    p.add('fita_preta', anel(V(), 'x', 0.012, 0.022, 0.0, 0.018, 24).parts['x'][0].apply_translation([-0.07, 0.0, 0.075]) if False else
          trimesh.creation.annulus(0.012, 0.022, 0.018, sections=24).apply_transform(TF.rotation_matrix(0, [1, 0, 0])).apply_translation([-0.07, 0.009, 0.075]))
