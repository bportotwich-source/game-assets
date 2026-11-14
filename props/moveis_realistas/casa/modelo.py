"""Mesa de lanchonete com dois sofás, vitrola de móvel, máquina de lavar de frente e banheira de pé no nível realista.

Medidas em mm nas coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente. As medidas de fora e os nós que
abrem (tampa da vitrola, porta e gaveta de sabão da máquina) são os dos móveis antigos de props/mobilias."""
import math, os, random, importlib.util
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte, letreiro


def _carregar(nome, pasta):
    spec = importlib.util.spec_from_file_location(nome, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', pasta, 'modelo.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


q = _carregar('modelo_quarto', 'quarto')
sala = _carregar('modelo_sala', 'sala')
_torno, _fio = q._torno, q._fio
_mover = sala._mover


def _anel(prof, mat, x=0, y=0, z=0, n=20, eixo=(0, 1, 0)):
    """Torneado fechado em anel (o perfil volta ao começo), sem tampar o meio."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo), anel=True)


# ---------------------------------------------------------------------------- MESA DE LANCHONETE (BOOTH)
def _banco(s):
    """Sofá de um lado da mesa; s = +1 na frente (z > 0), -1 atrás. Encosto na ponta de fora."""
    X, ZF, ZE = 640, 420, 950                       # meia largura, borda do assento, fundo do encosto
    p = []
    z0, z1 = sorted((s * ZF, s * (ZE - 44)))
    p.append(caixa(-X, X, 0, 90, z0 + 20, z1, 'plastico_preto'))                         # rodapé recuado
    p.append(caixa(-X, X, 90, 400, z0, z1, 'vinil_vermelho', 6.0))                      # frente da base, forrada
    p.append(caixa(-X + 4, X - 4, 96, 116, *sorted((s * (ZF - 3.5), s * (ZF - 0.3))), 'cromo', 1.0))   # friso de cromo
    a, b = sorted((s * (ZF - 15), s * (ZE - 125)))
    p.append(caixa(-X + 10, X - 10, 400, 470, a, b, 'vinil_vermelho', 22.0))           # almofada do assento
    p.append(_fio([(-X + 12, 436, s * (ZF - 16)), (X - 12, 436, s * (ZF - 16))], 5.5, 'vinil_vermelho', res=1))   # vivo da almofada
    # encosto em gomos verticais, inclinado para fora
    n = 7
    w = (2 * X - 20) / n
    for k in range(n):
        x0 = -X + 10 + k * w
        g = caixa(x0 + 2, x0 + w - 2, 470, 1110, -55, 55, 'vinil_vermelho', 26.0)
        _mover(g, lambda x, y, z: (x, y, s * (ZE - 140) + z * s + s * (y - 470) * 0.10))
        p.append(g)
    # costas de madeira (dá para a outra mesa) e tampo de cromo
    c = caixa(-X, X, 0, 1170, -22, 22, 'nogueira_y')
    _mover(c, lambda x, y, z: (x, y, s * (ZE - 22) + z))
    p.append(c)
    p.append(caixa(-X, X, 1150, 1170, *sorted((s * (ZE - 140), s * ZE)), 'cromo', 4.0))
    for x in (-X, X):                                                         # laterais em madeira
        p.append(caixa(x - 12, x + 12, 0, 480, z0, z1, 'nogueira_y', 3.0))
    return p


def mesa_booth():
    p = _banco(1) + _banco(-1)
    TX, TZ, TY = 560, 330, 740
    p.append(caixa(-TX, TX, TY - 30, TY, -TZ, TZ, 'formica', 6.0))                       # tampo de fórmica
    aro = caixa(-TX - 3, TX + 3, TY - 32, TY - 3, -TZ - 3, TZ + 3, 'cromo', 4.0)          # aro canelado de cromo
    cut(aro, caixa(-TX + 1, TX - 1, TY - 40, TY + 5, -TZ + 1, TZ - 1, 'cromo'))
    p.append(aro)
    p.append(caixa(-TX + 40, TX - 40, TY - 60, TY - 30, -TZ + 40, TZ - 40, 'compensado'))   # quadro de baixo
    p.append(_torno([(0, 0), (240, 0), (250, 6), (240, 14), (60, 28), (40, 40), (40, 60), (0, 60)], 'cromo', 0, 0, 0, n=32))   # pé
    p.append(_torno([(36, 60), (36, TY - 90), (0, TY - 90)], 'cromo', 0, 0, 0, n=20))
    p.append(_torno([(0, TY - 95), (120, TY - 95), (130, TY - 70), (0, TY - 60)], 'cromo', 0, 0, 0, n=20))
    # o que ficou na mesa: porta-guardanapo, açucareiro, saleiro, catchup e um prato
    x, z = 420, -40
    p.append(caixa(x - 55, x + 55, TY, TY + 8, z - 40, z + 40, 'inox', 2.0))
    for dz in (-38, 38):
        p.append(frente([(x - 55, TY + 8), (x + 55, TY + 8), (x + 45, TY + 110), (x - 45, TY + 110)], z + dz - 1.5, z + dz + 1.5, 'inox'))
    p.append(caixa(x - 50, x + 50, TY + 8, TY + 95, z - 34, z + 34, 'folha_sulfite'))
    p.append(_torno([(0, 0), (34, 0), (36, 6), (36, 100), (34, 104), (0, 104)], 'vidro_fosco', x - 130, TY, z, n=16))     # açucareiro
    p.append(_torno([(0, 0), (37, 0), (38, 10), (20, 34), (0, 36)], 'inox', x - 130, TY + 104, z, n=16))
    p.append(_torno([(0, 0), (18, 0), (19, 50), (16, 60), (0, 62)], 'vidro_fosco', x - 210, TY, z - 20, n=12))          # saleiro
    p.append(_torno([(0, 0), (19, 0), (20, 6), (12, 18), (0, 20)], 'inox', x - 210, TY + 60, z - 20, n=12))
    p.append(_torno([(0, 0), (30, 0), (32, 8), (32, 140), (12, 170), (11, 190), (0, 190)], 'vermelho', x - 200, TY, z + 60, n=14))   # catchup
    p.append(_torno([(0, 0), (12, 0), (12, 22), (4, 30), (0, 30)], 'liner_branco', x - 200, TY + 190, z + 60, n=10))
    p.append(_torno([(0, 0), (80, 0), (110, 10), (125, 18), (122, 20), (100, 14), (0, 8)], 'louca', -220, TY, 60, n=28))   # prato
    p.append(_torno([(0, 0), (34, 0), (40, 6), (44, 90), (41, 90), (0, 6)], 'vidro_fosco', -40, TY, -150, n=16))         # copo
    parte('booth', p, origem=G(0, 0, 0), grupo='A')


# ---------------------------------------------------------------------------- VITROLA
def vitrola():
    X, Z0, Z1, YB, YT = 520, -250, 250, 190, 650
    p = []
    for sx in (-1, 1):                                                        # pés palito inclinados
        for sz in (-1, 1):
            a = (sx * (X - 70), YB, sz * (200 - 50))
            b = (sx * (X - 30), 0, sz * 205)
            p.append(cil(a, b, 20, 'nogueira_y', n=10, r1=12))
            p.append(_torno([(0, 0), (13, 0), (13, 30), (0, 30)], 'latao', b[0], 0, b[2], n=10))
    c = caixa(-X, X, YB, YT, Z0, Z1, 'nogueira_x', 5.0)
    cut(c, caixa(-X + 20, X - 20, YT - 140, YT + 5, Z0 + 20, Z1 - 20, 'nogueira_x'))   # poço do toca-discos e do rádio
    p.append(c)
    p.append(caixa(-X + 20, X - 20, YT - 141, YT - 130, Z0 + 20, Z1 - 20, 'feltro'))    # fundo do poço
    # frente: dois alto-falantes de tecido com ripas e, no meio, o nicho de discos
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 150, sx * (X - 30)))
        p.append(caixa(x0, x1, YB + 30, YT - 30, Z1, Z1 + 1.5, 'tela_som'))
        for k in range(6):
            xx = x0 + 18 + k * (x1 - x0 - 36) / 5
            p.append(caixa(xx - 6, xx + 6, YB + 30, YT - 30, Z1 + 1.5, Z1 + 14, 'nogueira_y', 2.0))
        p.append(caixa(x0 - 4, x1 + 4, YB + 22, YB + 30, Z1, Z1 + 14, 'nogueira_x', 1.5))
        p.append(caixa(x0 - 4, x1 + 4, YT - 30, YT - 22, Z1, Z1 + 14, 'nogueira_x', 1.5))
    n = caixa(-140, 140, YB + 20, YT - 150, Z1 - 230, Z1 + 1, 'nogueira_x')
    cut(c, n)
    p.append(caixa(-140, 140, YB + 20, YB + 22, Z1 - 230, Z1, 'nogueira_x'))
    rnd = random.Random(33)
    for k in range(9):                                                        # discos em pé no nicho
        x = -125 + k * 28 + rnd.uniform(-3, 3)
        t = rnd.uniform(-0.15, 0.25) if k > 5 else 0
        o = caixa(-3, 3, 0, 265, -135, 135, f'capa_disco_{k % 3 + 1}' if k % 4 else 'papelao')
        _mover(o, lambda a, b, cz: (x + a + b * math.sin(t), YB + 22 + b * math.cos(t), Z1 - 170 + cz * 0.6))
        p.append(o)
    # toca-discos: prato, disco, braço e botões; rádio com mostrador à direita
    px, pz, py = -150, 10, YT - 130
    p.append(caixa(-X + 30, 120, py, py + 20, Z0 + 30, Z1 - 30, 'chapa_cinza', 3.0))
    p.append(_torno([(0, 0), (150, 0), (152, 4), (152, 18), (148, 22), (0, 22)], 'aco_polido', px, py + 20, pz, n=36))
    p.append(_torno([(0, 0), (148, 0), (148, 2), (0, 2)], 'disco', px, py + 42, pz, n=36))
    p.append(_torno([(0, 0), (44, 0), (44, 2.2), (0, 2.2)], 'rotulo_vermelho', px, py + 42.2, pz, n=24))
    p.append(_torno([(0, 0), (4, 0), (4, 20), (0, 22)], 'aco_polido', px, py + 44, pz, n=8))
    bx, bz = 60, -150
    p.append(_torno([(0, 0), (22, 0), (22, 30), (14, 40), (0, 40)], 'aco_polido', bx, py + 20, bz, n=14))
    p.append(_fio([(bx, py + 58, bz), (bx - 30, py + 58, bz + 80), (bx - 110, py + 52, bz + 170), (bx - 135, py + 50, bz + 185)], 4.0, 'aco_polido', res=2))
    p.append(caixa(bx - 150, bx - 125, py + 44, py + 54, bz + 175, bz + 205, 'plastico_preto', 2.0))   # cápsula
    p.append(caixa(bx + 30, bx + 40, py + 20, py + 90, bz + 40, bz + 50, 'aco_polido'))                # descanso
    rx0 = 160
    p.append(caixa(rx0, X - 30, py, py + 40, Z0 + 30, Z1 - 30, 'chapa_cinza', 3.0))
    p.append(caixa(rx0 + 20, X - 50, py + 40, py + 42, Z0 + 60, Z0 + 230, 'mostrador'))                # escala do rádio
    for k in range(9):
        zz = Z0 + 75 + k * 18
        p.append(caixa(rx0 + 30, X - 60, py + 42, py + 42.6, zz, zz + 1.5, 'tinta_preta'))
    p.append(caixa(rx0 + 130, rx0 + 133, py + 42, py + 44, Z0 + 70, Z0 + 220, 'vermelho'))             # ponteiro
    for k in range(4):
        p.append(_torno([(0, 0), (20, 0), (20, 16), (16, 22), (0, 22)], 'baquelite', rx0 + 50 + k * 50, py + 40, Z1 - 90, n=14))
    for x in (-X + 120, X - 120):
        p.append(cil((x - 30, YT + 2, Z0 + 4), (x + 30, YT + 2, Z0 + 4), 7, 'latao', n=10))           # dobradiças
    parte('vitrola', p, origem=G(0, 0, 0), grupo='A')
    t = [caixa(-X, X, YT, YT + 30, Z0, Z1, 'nogueira_x', 5.0)]                  # tampa
    t.append(caixa(-60, 60, YT + 4, YT + 18, Z1, Z1 + 12, 'latao', 3.0))
    t.append(caixa(-X + 30, X - 30, YT - 4, YT, Z0 + 30, Z1 - 30, 'feltro'))
    parte('tampa', t, origem=G(0, YT, Z0), grupo='B')


# ---------------------------------------------------------------------------- MÁQUINA DE LAVAR
def maquina_lavar():
    X, Z0, Z1, H = 298, -300, 290, 850
    DY, DR = 400, 175                                                         # centro e raio da escotilha
    c = caixa(-X, X, 22, H - 20, Z0, Z1, 'esmalte_lavar', 6.0)
    cut(c, cil((0, DY, Z1 - 60), (0, DY, Z1 + 10), DR - 15, 'esmalte_lavar', n=40))
    cut(c, caixa(-X + 30, -X + 200, H - 110, H - 40, Z1 - 200, Z1 + 10, 'esmalte_lavar'))   # vão da gaveta de sabão
    p = [c]
    p.append(caixa(-X - 2, X + 2, H - 22, H, Z0 - 2, Z1 + 2, 'laminado_branco', 5.0))   # tampo
    p.append(_anel([(DR - 15, -60), (DR - 15, 0), (DR - 4, 4), (DR - 30, 16), (DR - 45, 4), (DR - 45, -60)], 'borracha', 0, DY, Z1 - 40, n=40, eixo=(0, 0, 1)))  # sanfona
    p.append(_torno([(0, -300), (DR - 46, -300), (DR - 46, -40), (DR - 50, -40), (DR - 50, -296), (0, -296)], 'inox', 0, DY, Z1 - 20, n=32, eixo=(0, 0, 1)))  # tambor
    for k in range(3):                                                        # aletas do tambor
        a = k * 2.094
        p.append(caixa(-12, 12, 0, 30, -250, -60, 'inox', 4.0))
        _mover(p[-1], lambda x, y, z: (x * math.cos(a) - (y - DR + 46) * math.sin(a), DY + x * math.sin(a) + (y - DR + 46) * math.cos(a), Z1 - 20 + z))
    for k in range(4):                                                        # pés
        p.append(_torno([(0, 0), (24, 0), (24, 10), (10, 14), (10, 26), (0, 26)], 'plastico_preto', (-1) ** k * (X - 50), 0, (1 if k < 2 else -1) * 240, n=12))
    p.append(caixa(-X + 10, X - 10, 22, 90, Z1 - 3, Z1 + 1, 'esmalte_lavar', 2.0))     # tampa do filtro
    p.append(caixa(X - 120, X - 30, 40, 80, Z1 + 1, Z1 + 2, 'plastico_cinza', 1.0))
    # painel: mostrador, botão grande e botões; nome
    p.append(caixa(-X + 210, X - 10, H - 115, H - 30, Z1, Z1 + 2, 'plastico_cinza', 2.0))
    p.append(_torno([(0, 0), (38, 0), (38, 18), (34, 26), (0, 26)], 'plastico_cinza', X - 80, H - 72, Z1 + 2, n=24, eixo=(0, 0, 1)))
    p.append(caixa(X - 82, X - 78, H - 100, H - 62, Z1 + 26, Z1 + 30, 'tinta_preta'))
    p.append(caixa(-X + 230, -X + 340, H - 95, H - 55, Z1 + 2, Z1 + 3, 'vidro_escuro', 1.0))
    for k in range(3):
        p.append(caixa(-X + 360 + k * 40, -X + 385 + k * 40, H - 90, H - 78, Z1 + 2, Z1 + 8, 'tecla', 2.0))
    for k in range(8):
        a = math.radians(200 + k * 20)
        p.append(caixa(-1.5, 1.5, 0, 6, 0, 0.6, 'tinta_preta'))
        _mover(p[-1], lambda x, y, z: (X - 80 + 48 * math.cos(a) + x, H - 72 + 48 * math.sin(a) + y, Z1 + 2 + z))
    p.append(letreiro('LAVAMAX 8', 18, -X + 40, H - 150, Z1 + 0.6, 'tinta_preta', 'LEFT'))
    for y in (300, 600):                                                      # mangueiras atrás
        p.append(_fio([(-200, y, Z0), (-200, y, Z0 - 30), (-220, y - 120, Z0 - 40), (-230, 30, Z0 - 40)], 9, 'mangueira', res=2))
    parte('maquina', p, origem=G(0, 0, 0), grupo='A')
    g = [caixa(-X + 32, -X + 198, H - 108, H - 42, Z1 - 190, Z1 - 4, 'pvc_branco', 3.0)]   # gaveta de sabão
    g.append(caixa(-X + 30, -X + 200, H - 110, H - 40, Z1 - 4, Z1 + 4, 'esmalte_lavar', 3.0))
    g.append(caixa(-X + 70, -X + 160, H - 60, H - 52, Z1 + 4, Z1 + 10, 'plastico_cinza', 2.0))
    parte('gaveta_sabao', g, origem=G(0, 0, 0), grupo='B')
    d = [_anel([(DR - 40, 0), (DR + 10, 0), (DR + 22, 10), (DR + 22, 30), (DR + 10, 44), (DR - 30, 48), (DR - 40, 40)], 'aco_polido', 0, DY, Z1, n=40, eixo=(0, 0, 1))]  # aro
    d.append(_torno([(0, 30), (DR - 38, 30), (DR - 40, 12), (DR - 70, -40), (0, -70)], 'vidro_escuro', 0, DY, Z1, n=32, eixo=(0, 0, 1)))   # vidro abaulado
    d.append(caixa(DR + 4, DR + 40, DY - 50, DY + 50, Z1 + 20, Z1 + 46, 'plastico_cinza', 8.0))         # puxador
    parte('porta', d, origem=G(-DR - 22, DY, Z1 + 20), grupo='B')


# ---------------------------------------------------------------------------- BANHEIRA DE PÉ
def _estadio(o, meia_reta):
    """Estica um torneado redondo (eixo y) num estádio: as pontas redondas, os lados retos ao longo de x."""
    return _mover(o, lambda x, y, z: (x + math.copysign(meia_reta, x) if abs(x) > 0.5 else x, y, z))


def banheira():
    R, S, Y0 = 360, 430, 130                       # raio das pontas, meia reta, altura do fundo
    fora = [(0, Y0), (250, Y0), (282, Y0 + 20), (330, Y0 + 220), (352, 560), (360, 600), (372, 612), (375, 618)]
    dentro = [(375, 618), (366, 622), (350, 616), (338, 580), (318, 330), (270, Y0 + 45), (230, Y0 + 32), (0, Y0 + 30)]
    casco = _torno(fora + dentro[1:], 'banheira_fora', n=36)                   # um torneado só (o torno tampa as pontas abertas)
    tmp = _torno([(0, 0), (1, 0), (0, 1)], 'louca', n=3)
    casco.data.materials.append(tmp.data.materials[0])
    lib.bpy.data.objects.remove(tmp)
    for f in casco.data.polygons:                                            # da borda para dentro é louça
        if f.index // 36 >= len(fora) - 1:
            f.material_index = 1
    p = [_estadio(casco, S)]
    for sx in (-1, 1):                                                        # pés de garra
        for sz in (-1, 1):
            x, z = sx * (S + 120), sz * 190
            o = [_torno([(0, 0), (36, 0), (40, 12), (34, 30), (24, 40), (26, 70), (34, 100), (48, Y0 + 20), (0, Y0 + 20)], 'latao', x, 0, z, n=14)]
            for k in range(3):                                                # dedos
                a = math.radians(-35 + k * 35) + (0 if sx > 0 else math.pi)
                o.append(cil((x, 18, z), (x + 52 * math.cos(a), 6, z + 52 * math.sin(a) * sz), 11, 'latao', n=8, r1=7))
            p += o
    # torneira de telefone na borda da esquerda, ralo e tampa de corrente
    x = -S - R + 20
    for dz in (-75, 75):
        p.append(_torno([(0, 0), (22, 0), (22, 6), (13, 12), (12, 90), (0, 90)], 'latao', x, 618, dz, n=12))
        p.append(_torno([(0, 0), (12, 0), (12, 26), (0, 26)], 'louca', x, 708, dz, n=10))
        for k in range(4):                                                    # cruzeta
            a = k * math.pi / 2 + 0.3
            p.append(cil((x, 728, dz), (x + 38 * math.cos(a), 728, dz + 38 * math.sin(a)), 5, 'latao', n=8))
    p.append(cil((x, 670, -75), (x, 670, 75), 13, 'latao', n=12))
    p.append(_fio([(x, 682, 0), (x + 10, 750, 0), (x + 70, 772, 0), (x + 130, 735, 0)], 11, 'latao', res=2))
    p.append(_torno([(0, 0), (15, 0), (15, 26), (0, 26)], 'latao', x + 134, 704, 0, n=12))
    p.append(_torno([(0, 0), (34, 0), (34, 4), (0, 4)], 'latao', -S - 80, Y0 + 31, 0, n=16))       # ralo
    p.append(_torno([(0, 0), (40, 0), (36, 18), (0, 18)], 'borracha', -S + 60, Y0 + 31, 120, n=16))   # tampa solta
    p.append(_fio([(-S + 60, Y0 + 50, 120), (-S - 20, Y0 + 40, 90), (-S - 80, Y0 + 36, 30), (-S - 80, Y0 + 36, 0)], 2.5, 'latao', res=3))
    parte('banheira', p, origem=G(0, 0, 0), grupo='A')


FORMAS = {'mesa_booth': mesa_booth, 'vitrola': vitrola, 'maquina_lavar': maquina_lavar, 'banheira': banheira}
