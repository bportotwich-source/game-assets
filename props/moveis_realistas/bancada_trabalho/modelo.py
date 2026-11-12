"""Bancada de trabalho com morsa: a bancada de oficina das garagens. Cantoneira de aço pintada, tampo de
pranchas grossas com uma chapa de bater, morsa de ferro fundido, gaveta de chapa que abre (nó `gaveta`),
painel perfurado atrás com as ferramentas penduradas e prateleira embaixo com a caixa de ferramentas.
Medidas em mm, coordenadas do jogo (ver ../base.py): x largura, y altura, +z a frente."""
import math
import lib
from base import G, caixa, cil, planta, perfil, frente, cut, bevel, parte

H = 900                     # em cima do tampo
ESP = 50                    # pranchas do tampo
XT, ZT = 900, 350
PX, PZ = 840, 300           # eixo dos pés
PAINEL_Z = -344             # face da frente do painel perfurado
TOPO = 1750
MX, MZ = 600, 200           # morsa: meio, e a face do mordente fixo


def _torno(prof, mat, x=0, y=0, z=0, n=24, eixo=(0, 1, 0)):
    """Perfil em (raio, altura ao longo do eixo)."""
    return lib.lathe([(h, r) for r, h in prof], mat, n=n, c0=G(x, y, z), eixo=G(*eixo))


def _fio(pts, r, mat, fechado=False, res=3):
    return lib.fio([G(*p) for p in pts], r, mat, fechado=fechado, res=res)


def _cantoneira_pe(sx, sz, y0, y1):
    """Pé de cantoneira 50 × 50 × 5, as abas viradas para dentro."""
    x, z = sx * PX, sz * PZ
    return [caixa(min(x, x - sx * 50), max(x, x - sx * 50), y0, y1, min(z, z - sz * 5), max(z, z - sz * 5), 'aco_verde', 1.2),
            caixa(min(x, x - sx * 5), max(x, x - sx * 5), y0, y1, min(z, z - sz * 50), max(z, z - sz * 50), 'aco_verde', 1.2)]


def _estrutura():
    p = []
    yt = H - ESP
    for sx in (-1, 1):
        for sz in (-1, 1):
            p += _cantoneira_pe(sx, sz, 0, yt)
            p.append(caixa(sx * PX - 38 - sx * 14, sx * PX + 38 - sx * 14, 0, 5, sz * PZ - 38 - sz * 14, sz * PZ + 38 - sz * 14, 'aco_verde', 1.0))   # sapata
        for y in (yt - 50, 190):                                                                         # travessas laterais
            p.append(caixa(sx * (PX - 7.5) - 2.5, sx * (PX - 7.5) + 2.5, y, y + 50, -PZ + 5, PZ - 5, 'aco_verde', 1.2))
            p.append(caixa(min(sx * (PX - 5), sx * (PX - 50)), max(sx * (PX - 5), sx * (PX - 50)), y + 45, y + 50, -PZ + 5, PZ - 5, 'aco_verde', 1.0))
        p.append(caixa(326 if sx > 0 else -PX + 5, PX - 5 if sx > 0 else -326, yt - 50, yt, PZ - 10, PZ - 5, 'aco_verde', 1.2))   # travessa da frente, aberta para a gaveta
        p.append(caixa(sx * 322 - 4, sx * 322 + 4, yt - 172, yt, -PZ + 10, PZ - 10, 'chapa_cinza', 1.0))                  # caixa da gaveta
        p.append(caixa(sx * (PX - 20) - 16, sx * (PX - 20) + 16, H, TOPO, PAINEL_Z - 32, PAINEL_Z - 6, 'aco_verde', 1.5))   # montantes do painel
    p.append(caixa(-326, 326, yt - 176, yt - 172, -PZ + 10, PZ - 10, 'chapa_cinza', 1.0))
    p.append(caixa(-PX + 5, PX - 5, yt - 50, yt, -PZ + 5, -PZ + 10, 'aco_verde', 1.2))                                           # travessas de trás e de baixo
    for sz in (-1, 1):
        p.append(caixa(-PX + 5, PX - 5, 190, 240, sz * (PZ - 7.5) - 2.5, sz * (PZ - 7.5) + 2.5, 'aco_verde', 1.2))
    for k, d in enumerate((0, 7, -5, 4)):                                                                           # prateleira de baixo
        z0 = -PZ + 8 + k * 146
        p.append(caixa(-PX + 8 - d, PX - 8 - d + 4, 240, 262, z0, z0 + 143, 'pinho_x', 2.0))
    p.append(caixa(-PX - 4, PX + 4, TOPO - 30, TOPO, PAINEL_Z - 34, PAINEL_Z - 4, 'aco_verde', 1.5))                # travessa de cima do painel
    return p


def _painel():
    return [caixa(-PX + 4, PX - 4, H + 2, TOPO - 28, PAINEL_Z - 6, PAINEL_Z, 'eucatex', 0.8)]


def _tampo():
    p = []
    for k, d in enumerate((0, 10, -7)):
        z0 = -ZT + k * 234
        p.append(caixa(-XT - d, XT + (6 - d), H - ESP, H, z0, z0 + 231, 'tampo_x', 3.0))
    return p


def _gaveta():
    y0, y1 = H - ESP - 166, H - ESP - 6
    cx = caixa(-306, 306, y0 + 6, y1 - 14, -PZ + 40, ZT - 42, 'chapa_cinza')
    cut(cx, caixa(-303, 303, y0 + 9, y1, -PZ + 43, ZT - 45, 'chapa_cinza'))
    p = [cx, caixa(-316, 316, y0, y1, ZT - 42, ZT - 22, 'aco_verde', 2.5)]                                          # frente
    for s in (-1, 1):                                                                                               # puxador de barra
        p.append(cil((s * 110, (y0 + y1) / 2, ZT - 22), (s * 110, (y0 + y1) / 2, ZT + 6), 5, 'aco_ferramenta', n=10))
    p.append(cil((-128, (y0 + y1) / 2, ZT + 6), (128, (y0 + y1) / 2, ZT + 6), 7, 'aco_ferramenta', n=12))
    for k, (x, z, a) in enumerate(((-200, 60, 0.3), (-40, -80, -0.5), (150, 30, 1.2))):                             # o que se vê lá dentro
        dx, dz = 90 * math.cos(a), 90 * math.sin(a)
        p.append(cil((x - dx, y0 + 16, z - dz), (x + dx, y0 + 16, z + dz), 7, 'aco_ferramenta', n=8, r1=5))
    p.append(caixa(40, 150, y0 + 9, y0 + 50, -200, -110, 'plastico_bege', 3.0))
    return p


def _morsa():
    y = H
    p = [_torno([(0, 0), (92, 0), (92, 12), (78, 20), (0, 20)], 'esmalte_azul', MX, y, MZ - 50, n=28)]              # base giratória
    for a in (0.6, 2.7, 4.6):
        bx, bz = MX + 78 * math.cos(a), MZ - 50 + 78 * math.sin(a)
        p.append(cil((bx, y + 10, bz), (bx, y + 22, bz), 9, 'ferro_preto', n=6))
    p.append(perfil([(MZ - 105, y + 18), (MZ - 105, y + 72), (MZ - 62, y + 80), (MZ - 44, y + 132), (MZ, y + 132), (MZ, y + 62), (MZ + 14, y + 62), (MZ + 14, y + 18)],
                    MX - 56, MX + 56, 'esmalte_azul', 5.0))                                                         # corpo fixo, com a bigorninha atrás
    p.append(caixa(MX - 48, MX + 48, y + 80, y + 83, MZ - 100, MZ - 60, 'trilho_batido', 1.0))
    p.append(caixa(MX - 60, MX + 60, y + 100, y + 134, MZ, MZ + 7, 'aco_lamina', 1.0))                              # mordentes
    ab = 34                                                                                                         # abertura
    zm = MZ + 7 + ab
    p.append(caixa(MX - 60, MX + 60, y + 100, y + 134, zm, zm + 7, 'aco_lamina', 1.0))
    p.append(perfil([(zm + 7, y + 132), (zm + 36, y + 132), (zm + 58, y + 82), (zm + 58, y + 30), (zm + 7, y + 30)], MX - 56, MX + 56, 'esmalte_azul', 5.0))
    p.append(caixa(MX - 24, MX + 24, y + 30, y + 74, MZ - 90, zm + 50, 'trilho_batido', 2.0))                       # viga do mordente móvel
    zf = zm + 58
    p.append(cil((MX, y + 52, zf), (MX, y + 52, zf + 14), 21, 'esmalte_azul', n=18, r1=18))
    p.append(cil((MX, y + 52, zf + 14), (MX, y + 52, zf + 40), 15, 'aco_ferramenta', n=16))                         # cabeça do fuso
    p.append(cil((MX - 105, y + 52, zf + 27), (MX + 70, y + 52, zf + 27), 6.5, 'aco_ferramenta', n=12))             # manípulo
    for x in (MX - 105, MX + 70):
        p.append(_torno([(0, -11), (7, -9), (11, -4), (11, 4), (7, 9), (0, 11)], 'aco_ferramenta', x, y + 52, zf + 27, n=12, eixo=(1, 0, 0)))
    p.append(cil((MX + 70, y + 12, MZ - 50), (MX + 125, y + 12, MZ - 30), 5, 'aco_ferramenta', n=8))                # trava da base
    return p


def _chapa():
    """Chapa de bater em cima do tampo, parafusada."""
    p = [caixa(-430, -70, H, H + 4, -70, 250, 'trilho', 1.2)]
    for x in (-410, -90):
        for z in (-50, 230):
            p.append(cil((x, H + 4, z), (x, H + 7, z), 7, 'ferro_preto', n=8, r1=5))
    return p


# ---------------------------------------------------------------- ferramentas
def _chave(x, y, L, R, mat='aco_ferramenta'):
    """Chave combinada pendurada pelo anel: contorno de frente, boca para baixo."""
    w, Rj, s = R * 0.75, R * 1.25, R * 1.05
    pts = [(R * math.cos(math.radians(a)), L + R * math.sin(math.radians(a))) for a in range(-70, 251, 20)]
    pts.append((-w / 2, Rj * 0.95))
    pts += [(Rj * math.cos(math.radians(a)), Rj * math.sin(math.radians(a))) for a in range(125, 246, 20)]
    pts += [(-s / 2, -Rj * 0.93), (-s / 2, -Rj * 0.05), (s / 2, -Rj * 0.05), (s / 2, -Rj * 0.93)]
    pts += [(Rj * math.cos(math.radians(a)), Rj * math.sin(math.radians(a))) for a in range(295, 416, 20)]
    pts.append((w / 2, Rj * 0.95))
    z0 = PAINEL_Z + 6
    o = frente([(x + a, y - L + b) for a, b in pts], z0, z0 + 5, mat, 0.8)
    cut(o, cil((x, y, z0 - 5), (x, y, z0 + 10), R * 0.62, mat, n=12))
    return [o, _gancho(x, y + R * 0.62 - 2)]


def _gancho(x, y, c=26):
    z = PAINEL_Z
    return _fio([(x, y + 14, z), (x, y + 14, z + 6), (x, y, z + 8), (x, y, z + c), (x, y + 7, z + c + 3)], 1.8, 'aco_ferramenta')


def _martelo(x, y):
    z = PAINEL_Z + 24
    p = [cil((x - 52, y, z), (x - 12, y, z), 15, 'aco_ferramenta', n=14, r1=17),                                    # face
         cil((x - 16, y, z), (x + 16, y, z), 17, 'aco_ferramenta', n=14),
         cil((x + 12, y, z), (x + 34, y, z), 13, 'aco_ferramenta', n=14, r1=10),
         _torno([(0, 0), (10, 2), (15, 10), (15, 18), (10, 26), (0, 28)], 'aco_ferramenta', x + 30, y, z, n=14, eixo=(1, 0, 0)),   # bola
         cil((x, y - 14, z), (x, y - 120, z), 10, 'faia_y', n=12, r1=11),
         cil((x, y - 120, z), (x, y - 300, z), 11, 'faia_y', n=12, r1=14),
         cil((x, y - 300, z), (x, y - 312, z), 14, 'faia_y', n=12, r1=10)]
    for dx in (-36, 26):
        p.append(_gancho(x + dx, y - 16, 44))
    return p


def _arco_serra(x, y):
    z = PAINEL_Z + 14
    p = [_fio([(x - 170, y - 6, z), (x - 170, y + 84, z), (x - 150, y + 100, z), (x + 130, y + 100, z), (x + 150, y + 84, z), (x + 150, y + 10, z)], 6.0, 'aco_verde'),
         caixa(x - 176, x + 156, y - 6, y + 7, z - 0.5, z + 0.5, 'aco_lamina'),
         cil((x - 184, y, z), (x - 170, y, z), 7, 'aco_ferramenta', n=6),                                           # borboleta
         frente([(x + 148, y + 28), (x + 176, y + 30), (x + 190, y + 10), (x + 202, y - 62), (x + 196, y - 78), (x + 168, y - 76), (x + 160, y - 30), (x + 146, y - 12)],
                z - 11, z + 11, 'plastico_preto', 5.0)]
    for dx in (-90, 60):
        p.append(_gancho(x + dx, y + 108))
    return p


def _chaves_fenda(x, y):
    """Régua de madeira com as chaves de fenda enfiadas."""
    z = PAINEL_Z
    p = [caixa(x - 150, x + 150, y, y + 18, z, z + 44, 'pinho_x', 2.0)]
    for k, (mat, c, r) in enumerate((('isolante_vermelho', 150, 2.8), ('plastico_amarelo', 120, 2.4), ('plastico_azul', 180, 3.2), ('isolante_vermelho', 100, 2.2), ('plastico_preto', 140, 2.8))):
        xc = x - 116 + k * 58
        p.append(cil((xc, y - c, z + 24), (xc, y + 26, z + 24), r, 'aco_ferramenta', n=8))
        p.append(_torno([(0, 0), (9, 0), (12, 6), (13, 30), (11, 40), (13, 52), (13, 84), (8, 92), (0, 92)], mat, xc, y + 24, z + 24, n=12))
    return p


def _alicate(x, y):
    z = PAINEL_Z + 16
    p = []
    for s in (-1, 1):
        p.append(cil((x + s * 4, y - 8, z), (x + s * 3, y - 62, z), 6.5, 'aco_ferramenta', n=8, r1=3.5))            # bico para baixo
        p.append(cil((x - s * 4, y + 8, z), (x - s * 26, y + 130, z), 7.5, 'plastico_azul', n=10, r1=8.5))
    p.append(cil((x, y, z - 6), (x, y, z + 6), 12, 'aco_ferramenta', n=12))
    p.append(_gancho(x, y + 26, 22))
    return p


def _lima(x, z, a):
    y = H + 4
    dx, dz = math.cos(a), math.sin(a)
    pt = lambda t: (x + dx * t, y, z + dz * t)
    lam = caixa(-100, 110, y - 2.5, y + 2.5, -12, 12, 'aco_lamina', 0.6)
    lam.rotation_euler = (0, 0, -a)
    lam.location = lib.P(*G(x, 0, z))
    return [lam, cil(pt(-100), pt(-210), 13, 'faia_x', n=12, r1=10), cil(pt(-96), pt(-110), 12, 'latao', n=12)]


def _almotolia(x, z):
    y = H
    return [_torno([(0, 0), (40, 0), (43, 5), (43, 58), (36, 70), (9, 96), (7, 104), (0, 104)], 'esmalte_vermelho', x, y, z, n=22),
            cil((x, y + 100, z), (x + 60, y + 190, z + 24), 4.0, 'latao', n=8, r1=2.0),
            cil((x - 46, y + 40, z), (x - 43, y + 40, z), 12, 'latao', n=10)]


def _lata_parafusos(x, z):
    y = H
    lata = cil((x, y, z), (x, y + 95, z), 52, 'lata', n=22)
    cut(lata, cil((x, y + 6, z), (x, y + 110, z), 50.5, 'lata', n=22))
    p = [lata]
    for k in range(9):
        a = k * 2.4
        r = 12 + (k * 13) % 26
        p.append(cil((x + r * math.cos(a), y + 52 + (k % 3) * 6, z + r * math.sin(a)), (x + r * math.cos(a) + 8, y + 66 + (k % 3) * 6, z + r * math.sin(a) + 5), 9, 'ferro_preto', n=6))
    return p


def _porcas(x, z):
    p = []
    for k, (dx, dz, r) in enumerate(((0, 0, 11), (34, 18, 9), (-22, 30, 13), (52, -20, 8))):
        o = cil((x + dx, H, z + dz), (x + dx, H + r * 0.8, z + dz), r, 'ferro_preto', n=6)
        cut(o, cil((x + dx, H - 2, z + dz), (x + dx, H + 20, z + dz), r * 0.5, 'ferro_preto', n=8))
        p.append(o)
    p.append(cil((x - 70, H + 6, z - 20), (x - 10, H + 6, z - 44), 5, 'ferro_preto', n=8))                           # parafuso deitado
    p.append(cil((x - 82, H + 6, z - 15), (x - 70, H + 6, z - 20), 10, 'ferro_preto', n=6))
    return p


def _trena(x, z):
    y = H
    o = frente([(x - 36, y), (x + 36, y), (x + 36, y + 44), (x + 18, y + 70), (x - 18, y + 70), (x - 36, y + 50)], z - 17, z + 17, 'plastico_amarelo', 7.0)
    return [o, caixa(x + 36, x + 58, y + 3, y + 5, z - 10, z + 10, 'lata'), cil((x, y + 34, z + 17), (x, y + 34, z + 19), 15, 'plastico_preto', n=14)]


def _caixa_ferramentas(x, z):
    """Caixa de ferramentas de chapa, tampa de duas águas, na prateleira de baixo."""
    y = 262
    w, d = 230, 105
    p = [caixa(x - w, x + w, y, y + 150, z - d, z + d, 'esmalte_vermelho', 3.0),
         perfil([(z - d - 2, y + 150), (z + d + 2, y + 150), (z + d + 2, y + 176), (z + 40, y + 212), (z - 40, y + 212), (z - d - 2, y + 176)], x - w - 2, x + w + 2, 'esmalte_vermelho', 2.5),
         _fio([(x - 80, y + 212, z), (x - 80, y + 240, z), (x + 80, y + 240, z), (x + 80, y + 212, z)], 5.0, 'aco_ferramenta')]
    for s in (-1, 1):
        p.append(caixa(x + s * 140 - 16, x + s * 140 + 16, y + 126, y + 172, z + d, z + d + 6, 'lata', 1.5))         # fechos
    return p


def _galao(x, z):
    y = 262
    p = [caixa(x - 85, x + 85, y, y + 250, z - 60, z + 60, 'tambor', 8.0),
         cil((x + 45, y + 250, z), (x + 45, y + 272, z), 20, 'plastico_preto', n=14)]
    p.append(_fio([(x - 50, y + 250, z), (x - 50, y + 276, z), (x + 5, y + 276, z), (x + 5, y + 250, z)], 4.5, 'lata'))
    return p


def _rolo_fio(x, z):
    y = 262
    p = []
    for k in range(5):
        r = 120 - (k % 2) * 9
        pts = [(x + r * math.cos(i * math.pi / 12 + k), y + 8 + k * 11, z + r * 0.8 * math.sin(i * math.pi / 12 + k)) for i in range(24)]
        p.append(_fio(pts, 6.0, 'isolante_preto', fechado=True, res=1))
    return p


def _ferramentas():
    y = H + 560
    p = (_martelo(-650, y + 190) + _arco_serra(-300, y + 80) + _chaves_fenda(180, y - 190) + _alicate(-560, y - 220)
         + _chave(60, y + 190, 190, 15) + _chave(150, y + 190, 215, 17) + _chave(240, y + 190, 240, 19.5) + _chave(335, y + 190, 270, 22))
    p += _lima(-240, 60, 0.35) + _almotolia(-720, -230) + _lata_parafusos(-560, -230) + _porcas(130, -60) + _trena(250, 150)
    return p


def _prateleira():
    return _caixa_ferramentas(-420, 20) + _galao(380, -90) + _rolo_fio(120, 60)


def montar():
    parte('estrutura', _estrutura(), origem=G(0, 0, 0), grupo='A')
    parte('painel', _painel(), origem=G(0, 0, 0), grupo='A')
    parte('tampo', _tampo(), origem=G(0, 0, 0), grupo='B')
    parte('gaveta', _gaveta(), origem=G(0, 0, 0), grupo='B')
    parte('morsa', _morsa() + _chapa(), origem=G(0, 0, 0), grupo='B')
    parte('ferramentas', _ferramentas(), origem=G(0, 0, 0), grupo='C')
    parte('prateleira', _prateleira(), origem=G(0, 0, 0), grupo='C')
