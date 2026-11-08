# Veiculo 1: sedã Rumo (sedã compacto de 4 portas, anos 80/90, desenho próprio e sem marca).
# Carregado por gerar_veiculos.py (exec nos globais: V, Veiculo, modelo, MATS, torno, anel, cyl_eixo, fofo...).
import sedan_forma as SF
_SF_SEDAN = SF
from forma import (chaikin, loft, menos, uniao, inter, prisma_zy, prisma_xz, prisma_xy, caixa, cil_x, espelhar_x, tubo,
                   varrer_caminho, suavizar_caminho)
from shapely.geometry import Polygon as _Pg, box as _sbox, Point as _Pt
from shapely.ops import unary_union as _uu

_G = SF.FOLGA


def _mx(m):
    """Espelha uma malha no lado direito (-X)."""
    return espelhar_x(m)


def _ambos(m):
    return [m, _mx(m)]


def _cx(x0, x1, y0, y1, z0, z1):
    return caixa(x0, x1, y0, y1, z0, z1)


def _cham(x0, x1, y0, y1, z0, z1, c=0.01):
    q = V(); q.cham('x', x0, x1, y0, y1, z0, z1, c); return q.parts['x'][0]


class _Divisor:
    """Distribui malhas pelas regioes dos paineis: o que cai numa regiao vai para a parte; a carroceria perde a regiao + folga."""
    def __init__(s, regioes):
        s.reg = regioes        # [(no, R0, Rg)]
    def dividir(s, m, mat, Vc, so=None):
        resto = m
        for (no, R0, Rg) in s.reg:
            if so and no not in so: continue
            q = inter(resto, R0)
            if len(q.faces): Vc.achar(no)['geo'].add(mat, q)
            resto = menos(resto, Rg)
        if len(resto.faces): Vc.base.add(mat, resto)


def _janelas(borda=0.0):
    """Aberturas de todos os vidros (solidos): laterais dos dois lados, para-brisa e traseiro."""
    lat = []
    for fn in getattr(SF, 'JANELAS', (SF.janela_dianteira, SF.janela_traseira, SF.janela_terceira)):
        m = prisma_zy(fn(borda), 0.30, 1.2); lat += [m, _mx(m)]
    def topo(z0, z1, rec):
        zs = np.linspace(z0, z1, 30)
        pts = [(SF.quina_cabine(z)[0] - rec, z) for z in zs]
        pg = _Pg(pts + [(-x, z) for (x, z) in pts[::-1]])
        return prisma_xz(pg, 0.80, 2.0)
    ps = topo(SF.ZWS + 0.05 - borda, SF.Z_TOPO_PARABRISA + borda, 0.065 - borda)
    tr = SF.vidro_tras_vao(borda) if hasattr(SF, 'vidro_tras_vao') else topo(SF.Z_VIDRO_TRAS - borda, SF.ZBL + 0.055 - borda, SF.REC_VIDRO_TRAS - borda)
    return lat, ps, tr


def _carroceria(Vc, recortes=()):
    fora = uniao([SF.corpo_baixo(), SF.corpo_cabine()])
    dentro = uniao([SF.corpo_baixo(SF.T), SF.corpo_cabine(0.022)])
    casca = menos(fora, dentro)
    caixas = []
    for zc in (SF.EIXO_D, SF.EIXO_T):
        c = cil_x(SF.R_CAIXA, 0.50, 1.2, SF.Y_CAIXA, zc, 64); caixas += [c, _mx(c)]
    casca = menos(casca, *caixas)
    lat, ps, tr = _janelas()
    casca = menos(casca, *lat, ps, tr, *recortes)
    if hasattr(SF, 'vazios'): casca = menos(casca, *SF.vazios())     # caçamba da picape
    # portinhola do tanque (lado esquerdo, atras da porta traseira)
    zt, yt_ = SF.Z_BOCAL, 0.80
    rec = prisma_zy(_Pg(_Pt(zt, yt_).buffer(0.075, 16).exterior.coords).intersection(_sbox(zt - 0.09, yt_ - 0.062, zt + 0.09, yt_ + 0.062)), 0.70, 1.2)
    rec_g = prisma_zy(_Pt(zt, yt_).buffer(0.075 + _G, 16).intersection(_sbox(zt - 0.09 - _G, yt_ - 0.062 - _G, zt + 0.09 + _G, yt_ + 0.062 + _G)), 0.70, 1.2)
    tampinha = inter(casca, rec); casca = menos(casca, rec_g)
    # regioes dos paineis
    R = []
    R.append(('capo', SF.regiao_capo(), SF.regiao_capo(_G)))
    if SF.TAMPA: R.append(('tampa_porta_malas', SF.regiao_tampa(), SF.regiao_tampa(_G)))
    if hasattr(SF, 'regioes_extra'): R += SF.regioes_extra()      # portas de trás da van
    for qual, nomes in [q for q in (('d', ('porta_de', 'porta_dd')), ('t', ('porta_te', 'porta_td'))) if q[0] in getattr(SF, 'PORTAS', 'dt')]:
        for lado, no in zip((1, -1), nomes):
            R.append((no, SF.regiao_porta(qual, lado), SF.regiao_porta(qual, lado, _G)))
    for lado, no in ((1, 'paralama_e'), (-1, 'paralama_d')):
        R.append((no, SF.regiao_paralama(lado), SF.regiao_paralama(lado, _G)))
    Vc._div = D = _Divisor(R)
    D.dividir(casca, 'pintura', Vc)
    Vc.achar('tampa_combustivel')['geo'].add('pintura', tampinha)
    # vidros (camada dentro da espessura da chapa, 6 a 14 mm abaixo da superficie)
    camada = menos(SF.corpo_cabine(0.006, pontas=0.0), SF.corpo_cabine(0.014, desce=0.03, pontas=-0.01))
    latv, psv, trv = _janelas(0.012)
    Vc.achar('para_brisa')['geo'].add('vidro', inter(camada, psv))
    vt = SF.vidro_tras_vidro() if hasattr(SF, 'vidro_tras_vidro') else inter(camada, trv)
    if Vc.achar('vidro_traseiro'): Vc.achar('vidro_traseiro')['geo'].add('vidro', vt)
    else: D.dividir(vt, 'vidro', Vc, so=('porta_te', 'porta_td'))    # van: os vidros de trás ficam nas portas
    for m in latv:
        D.dividir(inter(camada, m), 'vidro', Vc, so=('porta_de', 'porta_dd', 'porta_te', 'porta_td'))
    # espessura das portas e dos batentes: o miolo entre a chapa e x = 0,70 vira batente pintado, com o forro na face de dentro
    arcos = []
    for zc in (SF.EIXO_D, SF.EIXO_T):
        arcos += [cil_x(SF.R_CAIXA + 0.025, 0.48, 1.2, SF.Y_CAIXA, zc, 48), cil_x(SF.R_CAIXA + 0.025, -1.2, -0.48, SF.Y_CAIXA, zc, 48)]
    dentro2 = menos(dentro, *arcos)
    for s in (1, -1):
        zm = getattr(SF, 'Z_MIOLO', -1.42)
        faixa = _cx(0.70, 1.2, 0.0, 2.0, zm, 0.72) if s > 0 else _cx(-1.2, -0.70, 0.0, 2.0, zm, 0.72)
        miolo = menos(inter(dentro2, faixa), *lat)
        face = _cx(0.70, 0.713, 0, 2, -3, 3) if s > 0 else _cx(-0.713, -0.70, 0, 2, -3, 3)
        D.dividir(inter(miolo, face), 'forro_porta', Vc, so=('porta_de', 'porta_dd', 'porta_te', 'porta_td'))
        D.dividir(menos(miolo, face), 'pintura', Vc, so=('porta_de', 'porta_dd', 'porta_te', 'porta_td'))
    # caixas de roda (banheiras) e o fundo pintado de preto
    for zc in (SF.EIXO_D, SF.EIXO_T):
        for s in (1, -1):
            a, b = (0.49, 0.86) if s > 0 else (-0.86, -0.49)
            a2, b2 = (0.51, 1.2) if s > 0 else (-1.2, -0.51)
            tb = menos(cil_x(SF.R_CAIXA + 0.018, a, b, SF.Y_CAIXA, zc, 64), cil_x(SF.R_CAIXA, a2, b2, SF.Y_CAIXA, zc, 64))
            Vc.base.add('chassi', inter(tb, dentro))   # so dentro da chapa: nao briga com a pintura na borda do arco
    return fora, dentro


def _frisos(Vc, fora):
    """Friso lateral de borracha (y 0,50 a 0,535) dividido pelos paineis, e a calha cromada do teto."""
    zs = np.linspace(SF.ZR + 0.12, 2.0, 140)
    an = []
    for z in zs:
        w = SF.hw(z) * SF.fx(z)
        an.append([(w - 0.004, 0.498, z), (w + 0.006, 0.500, z), (w + 0.011, 0.508, z), (w + 0.011, 0.527, z), (w + 0.006, 0.535, z), (w - 0.004, 0.537, z)])
    m = loft(an)
    cx = []
    for zc in (SF.EIXO_D, SF.EIXO_T):
        c = cil_x(SF.R_CAIXA + 0.012, 0.4, 1.2, SF.Y_CAIXA, zc, 48); cx += [c, _mx(c)]
    for mm in _ambos(m):
        Vc._div.dividir(menos(mm, *cx), 'borracha', Vc)
    # calha do teto
    zs = np.linspace(0.40, SF.Z_CALHA, 60); an = []
    for z in zs:
        x, y = SF.quina_cabine(z); y = min(y + 0.012, SF.ytop(z) - 0.01)
        an.append([(x - 0.006, y, z), (x + 0.008, y - 0.002, z), (x + 0.010, y - 0.012, z), (x - 0.004, y - 0.010, z)])
    for mm in _ambos(loft(an)):
        Vc.base.add('cromado', mm)


def _partes_carroceria(Vc):
    """Declara as partes que a casca vai preencher (ordem = ordem dos nos)."""
    yb_ = SF.yt(SF.Z_CAPO); fr = SF.SUFIXO_FRENTE
    Vc.parte('capo', (0, yb_ - 0.01, SF.Z_CAPO), 'tampa', eixo='x', abre_graus=-68, repouso=(0, 0, 0),
             item=PECA['capo' + fr], peca='capo' + fr, **REG['capo'])
    if SF.TAMPA:                      # a van não tem tampa: abre pelas portas de trás
        zd, ab = SF.TAMPA[:2]; yd = SF.TAMPA[2] if len(SF.TAMPA) > 2 else (SF.yt(zd) - 0.01 if zd < SF.ZBL else SF.ytop(zd) - 0.01)
        it = PECA[SF.ITEM_TAMPA] if hasattr(SF, 'ITEM_TAMPA') else PECA['tampa_porta_malas']
        Vc.parte('tampa_porta_malas', (0, yd, zd), 'tampa', eixo='x', abre_graus=ab, item=it, peca=it['id'], **REG['tampa_porta_malas'])
    sx = getattr(SF, 'SUFIXO_TRAS', '')
    for no, z, s, it in (('porta_de', 0.605, 1, 'porta_dianteira_e' + fr), ('porta_dd', 0.605, -1, 'porta_dianteira_d' + fr),
                         ('porta_te', -0.50, 1, 'porta_traseira_e' + sx), ('porta_td', -0.50, -1, 'porta_traseira_d' + sx)):
        if no[-2] == 't' and 't' not in getattr(SF, 'PORTAS', 'dt'): continue
        Vc.parte(no, (s * 0.80, 0.60, z), 'porta', eixo='y', abre_graus=-66 * s, repouso=(0, 0, 90 * s),
                 item=PECA[it], peca=it, **REG['porta_d' if no[-2] == 'd' else 'porta_t'])
    for no, s, it in (('paralama_e', 1, 'paralama_e' + fr), ('paralama_d', -1, 'paralama_d' + fr)):
        Vc.parte(no, (s * 0.80, 0.55, 1.27), 'peca', repouso=(0, 0, 90 * s), item=PECA[it], peca=it, **REG['paralama'])
    Vc.parte('tampa_combustivel', (SF.x_lado(SF.Z_BOCAL + 0.09, 1.0) - 0.03, 0.80, SF.Z_BOCAL + 0.09), 'tampa', eixo='y', abre_graus=-80, peca=None)
    Vc.parte('para_brisa', (0, 1.0 + SF.DY_CINTURA, SF.ZWS - 0.09), 'peca', repouso=(-62, 0, 0), item=PECA['para_brisa' + fr], peca='para_brisa' + fr, **REG['para_brisa'])
    if getattr(SF, 'VIDRO_TRAS', 0) is None: return    # van: sem vidro traseiro solto
    if hasattr(SF, 'VIDRO_TRAS'):     # vidro preso na tampa (hatch): é filho da tampa e abre junto
        o, rep, iv = SF.VIDRO_TRAS[:3]; pai = SF.VIDRO_TRAS[3] if len(SF.VIDRO_TRAS) > 3 else 'tampa_porta_malas'
        Vc.parte('vidro_traseiro', o, 'peca', pai=pai, repouso=rep, item=PECA[iv], peca=iv, **REG['vidro_traseiro'])
    else:
        Vc.parte('vidro_traseiro', (0, 1.0, -1.62), 'peca', repouso=(55, 0, 0), item=PECA['vidro_traseiro'], peca='vidro_traseiro', **REG['vidro_traseiro'])


# ============================================================================ dados de jogo das pecas
def _peca(id, nome, peso, padrao, efeito, celulas=None, carga_maos=False, onde=('ferro_velho', 'concessionaria', 'posto', 'garagem'), **extra):
    d = dict(id=id, nome=nome, grupo='loot', categoria='veiculo', montagem='floor', recurso='peca_veiculo', valor=1, peso_kg=peso,
             empilha=1, padrao=padrao, efeito=efeito, onde=list(onde), **extra)
    if carga_maos: d['carga_maos'] = True
    else: d['celulas'] = list(celulas)
    return d


PECA = {
    'motor_1_6': _peca('motor_1_6', 'Motor 1.6', 118, 'compacto_1_6', 'dá força ao carro; condição baixa falha, perde força e gasta mais', carga_maos=True, talha=True),
    'bateria_12v': _peca('bateria_12v', 'Bateria 12 V', 14, 'bateria_12v', 'dá partida e alimenta faróis, buzina e rádio; serve no gerador da base',
                         (2, 2), aceita=['bateria_carro']),
    'alternador': _peca('alternador', 'Alternador', 5, 'compacto_1_6', 'recarrega a bateria com o motor ligado', (2, 2)),
    'radiador': _peca('radiador', 'Radiador', 6, 'compacto_1_6', 'esfria o motor; sem ele o motor ferve em 2 minutos', (4, 3)),
    'tanque_45l': _peca('tanque_45l', 'Tanque de combustível 45 L', 9, 'compacto_1_6', 'guarda 45 L de combustível', (5, 3)),
    'escapamento': _peca('escapamento', 'Escapamento com silencioso', 8, 'compacto_1_6', 'sem ele o motor faz o dobro de barulho', (6, 1)),
    'roda_aro14': _peca('roda_aro14', 'Roda aro 14 com pneu', 16, 'aro14_4furos', 'roda de aço com pneu 185/70; também é o estepe', (3, 3),
                        onde=['ferro_velho', 'concessionaria', 'posto', 'garagem', 'porta_malas']),
    'porta_dianteira_e': _peca('porta_dianteira_e', 'Porta dianteira esquerda', 22, 'familia_rumo', 'protege o motorista; vidro e bolsa da porta', carga_maos=True),
    'porta_dianteira_d': _peca('porta_dianteira_d', 'Porta dianteira direita', 22, 'familia_rumo', 'protege o passageiro; vidro e bolsa da porta', carga_maos=True),
    'porta_traseira_e': _peca('porta_traseira_e', 'Porta traseira esquerda', 18, 'sedan_rumo', 'protege quem vai atrás', carga_maos=True),
    'porta_traseira_d': _peca('porta_traseira_d', 'Porta traseira direita', 18, 'sedan_rumo', 'protege quem vai atrás', carga_maos=True),
    'capo': _peca('capo', 'Capô', 14, 'familia_rumo', 'protege o motor de batidas e da chuva', carga_maos=True),
    'tampa_porta_malas': _peca('tampa_porta_malas', 'Tampa do porta-malas', 10, 'sedan_rumo', 'fecha e tranca o porta-malas', carga_maos=True),
    'para_choque_dianteiro': _peca('para_choque_dianteiro', 'Para-choque dianteiro', 7, 'familia_rumo', 'absorve a primeira parte das batidas de frente', (7, 1)),
    'para_choque_traseiro': _peca('para_choque_traseiro', 'Para-choque traseiro', 7, 'sedan_rumo', 'absorve a primeira parte das batidas de trás', (7, 1)),
    'paralama_e': _peca('paralama_e', 'Para-lama dianteiro esquerdo', 5, 'familia_rumo', 'protege a roda e o farol de lado', (4, 2)),
    'paralama_d': _peca('paralama_d', 'Para-lama dianteiro direito', 5, 'familia_rumo', 'protege a roda e o farol de lado', (4, 2)),
    'farol': _peca('farol', 'Farol com pisca', 2, 'familia_rumo', 'ilumina um lado da frente à noite', (2, 1)),
    'lanterna_traseira': _peca('lanterna_traseira', 'Lanterna traseira', 1, 'universal', 'luz de freio, de ré e pisca', (2, 1)),
    'retrovisor': _peca('retrovisor', 'Retrovisor', 0.8, 'universal', 'mostra o que vem atrás', (1, 1)),
    'para_brisa': _peca('para_brisa', 'Para-brisa', 12, 'familia_rumo', 'protege a frente da cabine (30% de quebrar ao tirar)', carga_maos=True),
    'vidro_traseiro': _peca('vidro_traseiro', 'Vidro traseiro', 8, 'sedan_rumo', 'protege a traseira da cabine', carga_maos=True),
    'banco_dianteiro': _peca('banco_dianteiro', 'Banco dianteiro', 15, 'universal', 'sem o banco do motorista não dá para dirigir', carga_maos=True),
    'banco_traseiro': _peca('banco_traseiro', 'Banco traseiro', 20, 'universal', 'leva 3 passageiros; sem ele o espaço vira carga', carga_maos=True),
    'volante': _peca('volante', 'Volante', 2.5, 'universal', 'tirar o volante trava o carro contra roubo', (2, 2)),
}
_JC = ['jogo_de_chaves']
REG = {   # regras de montagem (docs/veiculos.md, tabela 3.1)
    'motor': dict(obrigatoria=True, ferramentas=_JC + ['talha'], tempo_s=[240, 300], depende_de=['capo:aberto', 'radiador:fora', 'bateria:fora']),
    'bateria': dict(obrigatoria=True, ferramentas=['jogo_de_chaves|chave_inglesa'], tempo_s=[15, 20], depende_de=['capo:aberto']),
    'alternador': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[45, 60], depende_de=['capo:aberto']),
    'radiador': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[60, 75], depende_de=['capo:aberto']),
    'tanque': dict(obrigatoria=True, ferramentas=_JC + ['macaco_sanfona|macaco_jacare'], tempo_s=[90, 120], depende_de=['carro:no_macaco']),
    'escapamento': dict(obrigatoria=False, ferramentas=_JC + ['macaco_sanfona|macaco_jacare'], tempo_s=[60, 75], depende_de=['carro:no_macaco']),
    'roda': dict(obrigatoria=True, ferramentas=['chave_de_roda', 'macaco_sanfona|macaco_jacare'], tempo_s=[40, 50], depende_de=['carro:no_macaco']),
    'estepe': dict(obrigatoria=False, ferramentas=[], tempo_s=[5, 5], depende_de=['tampa_porta_malas:aberta', 'assoalho_porta_malas:aberto']),
    'porta_d': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[60, 75], depende_de=[]),
    'porta_t': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[60, 75], depende_de=[]),
    'capo': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[30, 40], depende_de=['capo:aberto']),
    'tampa_porta_malas': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[30, 40], depende_de=['tampa_porta_malas:aberta']),
    'para_choque': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[40, 50], depende_de=[]),
    'paralama': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[60, 70], depende_de=['farol:fora']),
    'farol': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[20, 25], depende_de=['capo:aberto']),
    'lanterna': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[15, 20], depende_de=['tampa_porta_malas:aberta']),
    'retrovisor': dict(obrigatoria=False, ferramentas=[], tempo_s=[5, 20], depende_de=[]),
    'para_brisa': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[90, 120], depende_de=[], quebra_ao_tirar=0.3),
    'vidro_traseiro': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[90, 120], depende_de=[], quebra_ao_tirar=0.3),
    'banco_motorista': dict(obrigatoria=True, ferramentas=_JC, tempo_s=[60, 70], depende_de=['porta_de:aberta']),
    'banco_passageiro': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[60, 70], depende_de=['porta_dd:aberta']),
    'banco_traseiro': dict(obrigatoria=False, ferramentas=_JC, tempo_s=[60, 70], depende_de=['porta_te|porta_td:aberta']),
    'volante': dict(obrigatoria=True, ferramentas=_JC, tempo_s=[30, 30], depende_de=['porta_de:aberta']),
}


def _fator(c): return [round(x, 4) for x in lin(c)]


def _frente_propria(sufixo, padrao, quem):
    """Cria as peças da frente de um modelo com desenho próprio (capô, portas dianteiras, para-lamas, para-brisa, para-choque e faróis):
    mesmo peso, tamanho e efeito das do sedã, outro id e outro padrão."""
    for base in ('capo', 'porta_dianteira_e', 'porta_dianteira_d', 'paralama_e', 'paralama_d', 'para_brisa', 'para_choque_dianteiro', 'farol'):
        it = dict(PECA[base]); it.update(id=base + sufixo, nome=f"{it['nome']} {quem}", padrao=padrao)
        PECA[base + sufixo] = it


@modelo('sedan_rumo', 'Sedã Rumo', classe='compacto', portas=4, lugares=5,
        descricao='Sedã compacto de 4 portas dos anos 80/90, desenho próprio e sem marca. Todas as peças da tabela 3.1 do design são nós '
                  'separados; portas, capô, porta-malas, porta-luvas, assoalho do porta-malas, portinhola do tanque e quebra-sóis abrem.',
        fisica=dict(massa_kg=1080, centro_massa_m=[0, 0.45, 0.05], tracao='dianteira', forca_motor_n=3200, freio=40,
                    direcao_graus=[32, 8], vel_max_kmh=140, roda_raio_m=SF.R_RODA, roda_largura_m=0.185,
                    suspensao=dict(curso_m=0.15, rigidez=40, compressao=0.85, retorno=0.9), atrito_pneu=dict(asfalto=2.6, terra=1.8, grama=1.4, lama=0.9)),
        combustivel=dict(tanque_l=45, consumo_l_100km=8, marcha_lenta_l_h=0.8, bocal='tampa_combustivel'),
        bateria=dict(capacidade_ah=45), cor_padrao=_fator(COR_PINTURA),
        # cores em sRGB, guardadas como fator linear do glTF (o que vai direto no baseColorFactor)
        cores_sorteio=[_fator(c) for c in [COR_PINTURA, (40, 62, 98), (205, 200, 184), (44, 82, 56), (196, 196, 198), (34, 34, 36),
                                           (218, 208, 176), (120, 136, 156)]])
def sedan_rumo(Vc):
    global SF
    SF = _SF_SEDAN
    _partes_carroceria(Vc)
    X0 = SF.x_lado(0.50, 1.0) - 0.07
    Vc.parte('para_choque_d', (0, 0.315, SF.ZF), 'peca', item=PECA['para_choque_dianteiro'], peca='para_choque_dianteiro', **REG['para_choque'])
    Vc.parte('para_choque_t', (0, 0.315, SF.ZR), 'peca', item=PECA['para_choque_traseiro'], peca='para_choque_traseiro', **REG['para_choque'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'farol_{l}', (s * 0.58, 0.61, 2.03), 'peca', item=PECA['farol'], peca='farol', **REG['farol'])
    for s, l in ((1, 'e'), (-1, 'd')):
        Vc.parte(f'lanterna_{l}', (s * 0.66, 0.73, -2.19), 'peca', item=PECA['lanterna_traseira'], peca='lanterna_traseira', **REG['lanterna'])
    for s, l, pai in ((1, 'e', 'porta_de'), (-1, 'd', 'porta_dd')):
        Vc.parte(f'retrovisor_{l}', (s * X0, 0.955 + SF.DY_CINTURA, 0.50), 'peca', pai=pai, item=PECA['retrovisor'], peca='retrovisor', **REG['retrovisor'])
    for no, s, zc in (('roda_de', 1, SF.EIXO_D), ('roda_dd', -1, SF.EIXO_D), ('roda_te', 1, SF.EIXO_T), ('roda_td', -1, SF.EIXO_T)):
        Vc.parte(no, (s * SF.X_RODA, SF.Y_RODA, zc), 'roda', repouso=(0, 0, 90), item=PECA['roda_aro14'], peca='roda_aro14',
                 tracao=zc > 0, direcao=zc > 0, **REG['roda'])
    Vc.parte('estepe', (0, 0.36, -1.90), 'peca', repouso=(0, 0, 0), item=PECA['roda_aro14'], peca='roda_aro14', **REG['estepe'])
    Vc.parte('motor', (0, 0.26, ZM), 'peca', item=PECA['motor_1_6'], peca='motor_1_6', **REG['motor'])
    Vc.parte('alternador', (-0.22, 0.50, ZM + 0.16), 'peca', item=PECA['alternador'], peca='alternador', **REG['alternador'])
    Vc.parte('radiador', (0, 0.37, 1.905), 'peca', repouso=(90, 0, 0), item=PECA['radiador'], peca='radiador', **REG['radiador'])
    Vc.parte('bateria', (0.30, 0.565, 0.93), 'peca', item=PECA['bateria_12v'], peca='bateria_12v', **REG['bateria'])
    Vc.parte('escapamento', (0, 0.165, -0.5), 'peca', item=PECA['escapamento'], peca='escapamento', **REG['escapamento'])
    Vc.parte('tanque', (0, 0.125, -0.83), 'peca', item=PECA['tanque_45l'], peca='tanque_45l', **REG['tanque'])
    Vc.parte('banco_motorista', (0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_motorista'])
    Vc.parte('banco_passageiro', (-0.37, 0.29, -0.28), 'peca', item=PECA['banco_dianteiro'], peca='banco_dianteiro', **REG['banco_passageiro'])
    Vc.parte('banco_traseiro', (0, 0.30, -1.13), 'peca', item=PECA['banco_traseiro'], peca='banco_traseiro', **REG['banco_traseiro'])
    Vc.parte('volante', (0.37, 0.82, 0.06), 'peca', repouso=(-68, 0, 0), item=PECA['volante'], peca='volante', **REG['volante'])
    Vc.parte('porta_luvas', (-0.375, 0.586, 0.215), 'tampa', eixo='x', abre_graus=-75, peca=None)
    Vc.parte('assoalho_porta_malas', (0, 0.478, -1.748), 'tampa', eixo='x', abre_graus=75, peca=None)
    Vc.parte('quebra_sol_e', (0.38, *_quebra_sol()), 'tampa', eixo='x', abre_graus=-80, peca=None)
    Vc.parte('quebra_sol_d', (-0.38, *_quebra_sol()), 'tampa', eixo='x', abre_graus=-80, peca=None)

    fora, dentro = _carroceria(Vc, _recortes())
    _frisos(Vc, fora)
    p = Vc.base
    _grade(p); _limpadores(p); _cofre(p); _cubos_e_suspensao(p)
    _para_choque(Vc.achar('para_choque_d')['geo'], True); _para_choque(Vc.achar('para_choque_t')['geo'], False)
    _placa_traseira(Vc.achar('tampa_porta_malas')['geo'])
    for s, l in ((1, 'e'), (-1, 'd')):
        _farol(Vc.achar(f'farol_{l}')['geo'], s); _lanterna(Vc.achar(f'lanterna_{l}')['geo'], s)
        _retrovisor(Vc.achar(f'retrovisor_{l}')['geo'], s)
    for no, s in (('porta_de', 1), ('porta_dd', -1)):
        _macaneta(Vc.achar(no)['geo'], s, -0.30, -0.17, chave=True); _porta_dentro(Vc.achar(no)['geo'], s, True)
    for no, s in (('porta_te', 1), ('porta_td', -1)):
        _macaneta(Vc.achar(no)['geo'], s, -1.16, -1.03); _porta_dentro(Vc.achar(no)['geo'], s, False)
    for no, s, zc in (('roda_de', 1, SF.EIXO_D), ('roda_dd', -1, SF.EIXO_D), ('roda_te', 1, SF.EIXO_T), ('roda_td', -1, SF.EIXO_T)):
        q = V(); _roda(q); g = Vc.achar(no)['geo']
        for k, ms in q.parts.items():
            for m in ms:
                mm = m.copy()
                if s < 0: mm = _mx(mm)
                mm.apply_translation([s * SF.X_RODA, SF.Y_RODA, zc]); g.add(k, mm)
    q = V(); _roda(q); g = Vc.achar('estepe')['geo']
    for k, ms in q.parts.items():
        for m in ms:
            mm = m.copy(); mm.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])); mm.apply_translation([0, 0.36, -1.90]); g.add(k, mm)
    _motor(Vc.achar('motor')['geo']); _alternador(Vc.achar('alternador')['geo']); _radiador(Vc.achar('radiador')['geo'])
    _bateria(Vc.achar('bateria')['geo']); _escapamento(Vc.achar('escapamento')['geo']); _tanque(Vc.achar('tanque')['geo']); _bocal(p)
    _banco_dianteiro(Vc.achar('banco_motorista')['geo'], 0.37); _banco_dianteiro(Vc.achar('banco_passageiro')['geo'], -0.37)
    _banco_traseiro(Vc.achar('banco_traseiro')['geo'])
    _painel(Vc, dentro); _forro_e_cabine(Vc, dentro); _porta_malas(Vc, dentro)
    _fundo_preto(Vc)
    # pontos para o jogo (nos vazios)
    for no, pos in (('camera_1a_pessoa', (0.37, 1.13, -0.32)), ('assento_motorista', (0.37, 0.48, -0.30)), ('assento_passageiro', (-0.37, 0.48, -0.30)),
                    ('assento_traseiro_e', (0.40, 0.50, -1.12)), ('assento_traseiro_m', (0.0, 0.50, -1.12)), ('assento_traseiro_d', (-0.40, 0.50, -1.12)),
                    ('saida_motorista', (1.35, 0.0, -0.05)), ('saida_passageiro', (-1.35, 0.0, -0.05)), ('saida_traseira_e', (1.35, 0.0, -0.95)),
                    ('saida_traseira_d', (-1.35, 0.0, -0.95)), ('bocal_tanque', (0.79, 0.80, -1.86)), ('saida_escape', (-0.43, 0.19, -2.33)),
                    ('luz_farol_e', (0.58, 0.614, 2.09)), ('luz_farol_d', (-0.58, 0.614, 2.09)), ('luz_freio_e', (0.66, 0.77, -2.25)),
                    ('luz_freio_d', (-0.66, 0.77, -2.25)), ('macaco_e', (0.70, 0.22, -0.20)), ('macaco_d', (-0.70, 0.22, -0.20)),
                    ('talha_motor', (0.0, 1.40, ZM))):
        Vc.encaixes.append(dict(no=no, pos=pos, tipo='ponto'))
    SAQ = {
        'porta_malas': [['mochila', 0.30], ['macaco_sanfona', 0.5], ['chave_de_roda', 0.5], ['garrafa_agua', 0.25], ['oleo_motor', 0.2], ['cabos_chupeta', 0.15],
                        ['saco_dormir', 0.15], ['galao_gasolina', 0.1], ['jogo_de_chaves', 0.1], ['roupas', 0.3], ['lata_feijao', 0.2]],
        'porta_luvas': [['mapa_cidade', 0.4], ['lanterna', 0.3], ['pilhas', 0.3], ['isqueiro', 0.25], ['bilhete', 0.2], ['chave_casa', 0.1], ['frasco_remedio', 0.15]],
        'bolsa': [['garrafa_agua', 0.2], ['salgadinho', 0.2], ['chave_carro', 0.02]],
        'console': [['isqueiro', 0.3], ['pilhas', 0.2]],
        'quebra_sol': [['chave_carro', 0.10]],
        'banco': [['mochila', 0.1], ['roupas', 0.2], ['caixa_papelao', 0.1]],
    }
    Vc.compartimento('porta_malas', 'Porta-malas', (9, 5), 'tampa_porta_malas', saque=SAQ['porta_malas'], tranca=True)
    Vc.compartimento('fundo_porta_malas', 'Fundo do porta-malas', (3, 3), 'assoalho_porta_malas', so_aceita=['roda_aro14'], parte='estepe')
    Vc.compartimento('porta_luvas', 'Porta-luvas', (3, 2), 'porta_luvas', saque=SAQ['porta_luvas'])
    Vc.compartimento('bolsa_porta_de', 'Bolsa da porta do motorista', (3, 1), 'porta_de', saque=SAQ['bolsa'])
    Vc.compartimento('bolsa_porta_dd', 'Bolsa da porta do passageiro', (3, 1), 'porta_dd', saque=SAQ['bolsa'])
    Vc.compartimento('console', 'Console', (2, 1), None, saque=SAQ['console'])
    Vc.compartimento('quebra_sol_e', 'Quebra-sol do motorista', (1, 1), 'quebra_sol_e', saque=SAQ['quebra_sol'])
    Vc.compartimento('quebra_sol_d', 'Quebra-sol do passageiro', (1, 1), 'quebra_sol_d', saque=SAQ['quebra_sol'])
    Vc.compartimento('banco_tras', 'Banco de trás', (8, 4), None, saque=SAQ['banco'], vira_carga_sem='banco_traseiro', carga_sem_banco=[9, 4])


def _porta_dentro(q, s, dianteira):
    """Forro de dentro da porta: apoio de braço, maçaneta interna, manivela do vidro, pino da trava, bolsa e alto-falante."""
    def L(m): return m if s > 0 else _mx(m)
    z0, z1 = (0.56, -0.36) if dianteira else (-0.55, -1.22)
    x = 0.70
    q.add('vinil', L(_cham(x - 0.055, x + 0.002, 0.62, 0.665, z1 + 0.06, (z0 + z1) / 2 + 0.05, 0.015)))
    zm = (z1 + 0.10) if False else (z0 - 0.17)
    q.add('chassi', L(_cx(x - 0.004, x + 0.001, 0.73, 0.775, zm - 0.06, zm + 0.02)))
    q.add('cromado', L(_cham(x - 0.012, x - 0.003, 0.742, 0.762, zm - 0.055, zm + 0.0, 0.003)))
    zc = (z0 + z1) / 2 - 0.08
    q.add('plastico_cinza', L(cil_x(0.03, x - 0.012, x, 0.72, zc, 20)))
    q.add('plastico_cinza', L(_cham(x - 0.022, x - 0.012, 0.712, 0.728, zc - 0.075, zc, 0.004)))
    q.add('plastico_preto', L(cil_x(0.011, x - 0.05, x - 0.022, 0.72, zc - 0.07, 12)))
    q.add('plastico_preto', L(_cil_y(0.006, SF.yt(z1 + 0.08) - 0.005, SF.yt(z1 + 0.08) + 0.025, 0.735, z1 + 0.08, 8)))
    if dianteira:
        q.add('forro_porta', L(_cham(x - 0.045, x, 0.36, 0.48, z1 + 0.10, z0 - 0.25, 0.01)))
        q.add('chassi', L(_cx(x - 0.044, x - 0.034, 0.40, 0.475, z1 + 0.11, z0 - 0.26)))
        q.add('plastico_preto', L(cil_x(0.07, x - 0.006, x + 0.001, 0.42, z0 - 0.12, 32)))
        for k in range(5): q.add('chassi', L(_cx(x - 0.008, x - 0.006, 0.37 + k * 0.022, 0.375 + k * 0.022, z0 - 0.18, z0 - 0.06)))


def _fundo_preto(Vc):
    """O fundo da lataria (faces viradas para baixo, abaixo de 0,4 m) vira tinta de chassi."""
    for g in [Vc.base] + [p['geo'] for p in Vc.partes]:
        if 'pintura' not in g.parts: continue
        novas, pretas = [], []
        for m in g.parts['pintura']:
            fn = m.face_normals; c = m.triangles_center
            sel = (fn[:, 1] < -0.6) & (c[:, 1] < 0.40)
            if sel.any():
                pretas.append(m.submesh([np.where(sel)[0]], append=True))
                if (~sel).any(): novas.append(m.submesh([np.where(~sel)[0]], append=True))
            else: novas.append(m)
        g.parts['pintura'] = novas
        if pretas: g.parts.setdefault('chassi', []).extend(pretas)


# ============================================================================ luzes, grade, para-choques e detalhes de fora
def _zf(x, frente=True):
    return SF.z_ponta(abs(x), frente, k=1.0)


def _casca_contorno(xa, xb, y0, y1, d0, d1, frente=True, n=14):
    """Solido convexo que segue o contorno da frente (ou traseira) entre |x| = xa e xb, de d0 a d1 para fora da superficie
    (d negativo = para dentro)."""
    pts = []; sg = 1 if frente else -1
    for x in np.linspace(xa, xb, n):
        zs = _zf(x, frente)
        e = 0.002; z2 = _zf(min(x + e, 0.835), frente); t = np.array([e, 0, z2 - zs]); t /= np.linalg.norm(t)
        nrm = np.array([t[2], 0, -t[0]]) * sg
        if nrm[2] * sg < 0: nrm = -nrm
        for y in (y0, y1):
            for d in (d0, d1):
                pts.append(np.array([x, y, zs]) + nrm * d)
    return trimesh.convex.convex_hull(np.array(pts))


def _recortes():
    """Buracos na lataria para faróis, grade e lanternas (antes de dividir os painéis)."""
    r = []
    for s in (1, -1):
        h = _casca_contorno(*SF.FAROL, 0.06, -0.09); r.append(h if s > 0 else _mx(h))
        t = _casca_contorno(*SF.LANTERNA, 0.06, -getattr(SF, 'LANTERNA_FUNDO', 0.08), frente=False); r.append(t if s > 0 else _mx(t))
    xg, ga, gb = SF.GRADE; r.append(_cx(-xg, xg, ga, gb, SF.ZF - 0.12, 2.2))
    return r


def _farol(q, s):
    """Farol retangular com refletores cromados, lâmpadas, lente de frisos e pisca âmbar na quina (o tamanho vem de SF.FAROL)."""
    def L(m): return m if s > 0 else _mx(m)
    xa, xb, ya, yb = SF.FAROL; xd = xb - SF.FAROL_PISCA; yc = (ya + yb) / 2; n = SF.FAROL_N
    C = _casca_contorno
    q.add('plastico_preto', L(menos(C(xa + 0.003, xb - 0.003, ya + 0.003, yb - 0.003, -0.004, -0.03), C(xa + 0.01, xb - 0.01, ya + 0.01, yb - 0.01, 0.02, -0.05))))
    q.add('refletor', L(C(xa + 0.007, xb - 0.006, ya + 0.006, yb - 0.006, -0.022, -0.035)))
    q.add('plastico_preto', L(C(xa + 0.01, xb - 0.01, ya + 0.01, yb - 0.01, -0.035, -0.10)))
    q.add('plastico_preto', L(C(xd - 0.003, xd + 0.003, ya + 0.006, yb - 0.006, -0.005, -0.03, n=2)))
    larg = (xd - xa) / n; k = min((yb - ya) / 0.157, larg / 0.1525)
    for i in range(n):
        xc = xa + (xd - xa) * ((0.28, 0.72)[i] if n == 2 else (i + 0.5) / n)
        zc = _zf(xc) - 0.020
        bowl = trimesh.creation.revolve(np.array([(0.0, -0.05), (0.03, -0.045), (0.055, -0.03), (0.062, -0.012), (0.0, -0.012)]) * k, sections=32)
        if bowl.volume < 0: bowl.invert()
        bowl.apply_translation([xc, yc, zc]); q.add('refletor', L(bowl))
        lp = trimesh.creation.icosphere(2, 0.012); lp.apply_translation([xc, yc, zc - 0.03 * k]); q.add('lampada', L(lp))
        if n > 1 and i < n - 1 and SF.GRADE_ESTILO != 'frisos':                       # filete cromado entre os dois faróis quadrados
            q.add('cromado', L(C(xa + larg * (i + 1) - 0.003, xa + larg * (i + 1) + 0.003, ya + 0.007, yb - 0.007, -0.001, -0.03, n=2)))
    q.add('lente_farol', L(C(xa + 0.007, xd - 0.002, ya + 0.007, yb - 0.007, -0.002, -0.008)))
    q.add('lente_pisca', L(C(xd + 0.002, xb - 0.006, ya + 0.007, yb - 0.007, -0.002, -0.008)))


def _lanterna(q, s):
    def L(m): return m if s > 0 else _mx(m)
    q.add('plastico_preto', L(menos(_casca_contorno(0.506, 0.812, 0.638, 0.815, -0.004, -0.03, frente=False), _casca_contorno(0.512, 0.806, 0.644, 0.809, 0.02, -0.05, frente=False))))
    q.add('refletor', L(_casca_contorno(0.508, 0.810, 0.640, 0.813, -0.02, -0.032, frente=False)))
    q.add('plastico_preto', L(_casca_contorno(0.512, 0.806, 0.644, 0.809, -0.032, -0.08, frente=False)))
    q.add('lente_lanterna', L(_casca_contorno(0.510, 0.808, 0.726, 0.811, -0.002, -0.009, frente=False)))
    q.add('lente_pisca', L(_casca_contorno(0.624, 0.808, 0.642, 0.721, -0.002, -0.009, frente=False)))
    q.add('lente_re', L(_casca_contorno(0.510, 0.619, 0.642, 0.721, -0.002, -0.009, frente=False)))
    q.add('cromado', L(_casca_contorno(0.510, 0.808, 0.721, 0.726, 0.0, -0.006, frente=False)))
    q.add('cromado', L(_casca_contorno(0.619, 0.624, 0.642, 0.721, 0.0, -0.006, frente=False, n=2)))


def _grade(p):
    """Grade entre os faróis (o tamanho vem de SF.GRADE). frisos: a do sedã; barras: três barras grossas prateadas; fenda: uma
    abertura estreita com uma barra cromada no meio."""
    zf = SF.ZF; xg, ga, gb = SF.GRADE; est = SF.GRADE_ESTILO; ym = (ga + gb) / 2
    p.add('plastico_preto', _cx(-xg + 0.002, xg - 0.002, ga + 0.002, gb - 0.002, zf - 0.09, zf - 0.035))
    p.add('chassi', _cx(-xg + 0.018, xg - 0.018, ga + 0.016, gb - 0.016, zf - 0.04, zf - 0.03))
    if est == 'frisos':
        for i in range(5):
            y = ga + 0.020 + i * 0.0275
            p.add('plastico_preto', _cham(-xg + 0.016, xg - 0.016, y, y + 0.012, zf - 0.04, zf - 0.006, 0.003))
        for x in (-0.25, 0.0, 0.25):
            p.add('plastico_preto', _cx(x - 0.006, x + 0.006, ga + 0.016, gb - 0.016, zf - 0.04, zf - 0.008))
        p.add('cromado', _cham(-xg, xg, gb - 0.008, gb, zf - 0.03, zf - 0.002, 0.002))
    elif est == 'barras':
        h = gb - ga; nb = 3
        for i in range(nb):
            y = ga + h * (i + 1) / (nb + 1)
            p.add('plastico_prata', _cham(-xg + 0.012, xg - 0.012, y - 0.016, y + 0.016, zf - 0.045, zf - 0.004, 0.006))
        for x in np.linspace(-xg + 0.07, xg - 0.07, 9):
            p.add('plastico_preto', _cx(x - 0.005, x + 0.005, ga + 0.016, gb - 0.016, zf - 0.04, zf - 0.012))
        p.add('plastico_prata', _cham(-xg, xg, gb - 0.012, gb, zf - 0.03, zf - 0.002, 0.003))
        p.add('plastico_prata', _cham(-xg, xg, ga, ga + 0.012, zf - 0.03, zf - 0.002, 0.003))
    else:
        p.add('cromado', _cham(-xg + 0.01, xg - 0.01, ym - 0.008, ym + 0.008, zf - 0.04, zf - 0.006, 0.004))
        for x in np.linspace(-xg + 0.05, xg - 0.05, 12):
            p.add('plastico_preto', _cx(x - 0.004, x + 0.004, ga + 0.012, gb - 0.012, zf - 0.04, zf - 0.010))
    ye = ym if est != 'fenda' else gb + 0.035
    e = trimesh.creation.cylinder(radius=0.034, height=0.012, sections=32); e.apply_translation([0, ye, zf - 0.002]); p.add('cromado', e)
    e = trimesh.creation.cylinder(radius=0.026, height=0.006, sections=32); e.apply_translation([0, ye, zf + 0.007]); p.add('pintura', e)


def _caminho_ponta(frente, zlim, off, n=96):
    """Caminho em planta que contorna a frente (ou traseira) a 'off' m da lataria, de um lado (zlim) ao outro."""
    zs = np.linspace(zlim, SF.ZF if frente else SF.ZR, 900)
    xs = np.array([SF.hw(z) * SF.fx(z) for z in zs])
    lado = np.column_stack([xs, zs]); outro = lado[::-1].copy(); outro[:, 0] *= -1
    # frente: +x -> centro -> -x; traseira: -x -> centro -> +x (assim o 'lado' do perfil aponta para fora nas duas pontas)
    esp = lado.copy(); esp[:, 0] *= -1
    pl = np.vstack([lado, outro[1:]]) if frente else np.vstack([esp, lado[::-1][1:]])
    from shapely.geometry import LineString as _LS
    ls = _LS(pl); pts = [ls.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, n)]
    P = np.array(pts); out = []
    for i in range(len(P)):
        t = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]; t /= np.linalg.norm(t)
        nrm = np.array([t[1], -t[0]])
        cen = np.array([0.0, 0.0])
        if np.dot(nrm, P[i] - cen) < 0: nrm = -nrm
        out.append(P[i] + nrm * off)
    return np.array(out)


def _para_choque(q, frente):
    """Para-choque de plástico preto texturizado que envolve as quinas, com faixa de borracha, entradas de ar e suporte de placa."""
    y0 = 0.315
    cam = _caminho_ponta(frente, 1.74 if frente else SF.Z_PC_TRAS, 0.0)
    path = [(x, y0, z) for x, z in cam]
    perf = chaikin([(-0.035, 0.0), (0.035, 0.0), (0.058, 0.02), (0.062, 0.09), (0.058, 0.165), (0.035, 0.185), (-0.035, 0.185)], 2)
    q.add(getattr(SF, 'MAT_PARA_CHOQUE', 'plastico_preto'), varrer_caminho(perf, path))
    perf2 = chaikin([(0.058, 0.082), (0.068, 0.085), (0.070, 0.10), (0.068, 0.115), (0.058, 0.118)], 1, fechado=True)
    q.add('borracha', varrer_caminho(perf2, path[6:-6]))
    perf3 = [(0.0705, 0.0985), (0.072, 0.0985), (0.072, 0.1015), (0.0705, 0.1015)]
    q.add('cromado', varrer_caminho(perf3, path[10:-10]))
    zc = (SF.ZF if frente else SF.ZR); sg = 1 if frente else -1
    zface = zc + sg * 0.062
    if frente:
        for x0 in (-0.62, -0.30, 0.02, 0.34):                         # entradas de ar embaixo
            q.add('chassi', _cx(x0, x0 + 0.28, y0 + 0.022, y0 + 0.058, zface - 0.02, zface + 0.002))
        q.add('plastico_preto', _cx(-0.215, 0.215, 0.338, 0.488, zface - 0.01, zface + 0.006))      # suporte da placa
        q.add('placa', _cham(-0.2, 0.2, 0.345, 0.48, zface + 0.006, zface + 0.010, 0.003))
        for x in (-0.17, 0.17): q.add('cromado', _cx(x - 0.006, x + 0.006, 0.465, 0.471, zface + 0.010, zface + 0.013))
        q.add('aco_escuro', tubo([(0.45, y0 + 0.01, zface - 0.04), (0.45, y0 - 0.02, zface - 0.03), (0.45, y0 - 0.02, zface + 0.0)], 0.008))
    else:
        for x in (-0.66, 0.66): q.add('lente_lanterna', _cx(x - 0.05, x + 0.05, y0 + 0.07, y0 + 0.11, zface - 0.004, zface + 0.002))   # olhos de gato


def _placa_traseira(q):
    z = SF.ZR - 0.004
    q.add('plastico_preto', _cx(-0.215, 0.215, 0.648, 0.797, z - 0.006, z + 0.002))
    q.add('placa', _cham(-0.2, 0.2, 0.655, 0.79, z - 0.010, z - 0.006, 0.003))
    q.add('plastico_preto', _cham(-0.495, 0.495, 0.80, 0.832, z - 0.016, z + 0.004, 0.004))        # friso preto com a fechadura
    q.add('lente_re', _cx(-0.08, 0.08, 0.802, 0.812, z - 0.018, z - 0.014))
    c = trimesh.creation.cylinder(radius=0.013, height=0.012, sections=20); c.apply_translation([0, 0.816, z - 0.02]); q.add('cromado', c)


def _macaneta(q, s, z0, z1, y=None, chave=False):
    y = 0.835 + SF.DY_CINTURA if y is None else y
    z = (z0 + z1) / 2; x = SF.x_lado(z, 1.0) - 0.012
    def L(m): return m if s > 0 else _mx(m)
    q.add('plastico_preto', L(_cham(x - 0.004, x + 0.010, y - 0.022, y + 0.022, z0, z1, 0.004)))
    q.add('chassi', L(_cx(x + 0.004, x + 0.011, y - 0.014, y + 0.010, z0 + 0.015, z1 - 0.015)))
    q.add('cromado', L(_cham(x + 0.009, x + 0.020, y - 0.004, y + 0.012, z0 + 0.008, z1 - 0.008, 0.003)))
    if chave:
        c = cil_x(0.011, x, x + 0.016, y, z1 + 0.025, 20); q.add('cromado', L(c))
        q.add('chassi', L(_cx(x + 0.0155, x + 0.0165, y - 0.006, y + 0.006, z1 + 0.023, z1 + 0.027)))


def _retrovisor(q, s):
    dy = SF.DY_CINTURA
    def L(m): return (m if s > 0 else _mx(m)).apply_translation([0, dy, 0])
    x0 = SF.x_lado(0.50, 1.0) - 0.07
    q.add('plastico_preto', L(trimesh.convex.convex_hull(np.array([[x0, 0.955, 0.56], [x0, 0.955, 0.44], [x0, 1.04, 0.56], [x0, 1.0, 0.47],
                                                                    [x0 + 0.06, 0.965, 0.55], [x0 + 0.06, 0.965, 0.46], [x0 + 0.06, 1.01, 0.54]]))))
    q.add('plastico_preto', L(tubo([(x0 + 0.05, 0.985, 0.505), (x0 + 0.11, 0.99, 0.50), (x0 + 0.15, 1.0, 0.49)], 0.014)))
    corpo = trimesh.convex.convex_hull(np.array([[x0 + a, y, z] for a in (0.12, 0.27) for y in (0.955, 1.07) for z in (0.43, 0.50)] +
                                                [[x0 + 0.13, 0.96, 0.53], [x0 + 0.13, 1.065, 0.53], [x0 + 0.25, 0.97, 0.52], [x0 + 0.25, 1.06, 0.52]]))
    q.add('plastico_preto', L(corpo))
    q.add('espelho_retrovisor', L(_cx(x0 + 0.128, x0 + 0.262, 0.962, 1.063, 0.426, 0.432)))


def _limpadores(p):
    d = SF.ZWS - 0.64                     # tudo segue a base do para-brisa
    yc = SF.yt(0.66 + d) + 0.012
    p.add('plastico_preto', _cx(-0.72, 0.72, yc - 0.02, yc - 0.004, 0.63 + d, 0.695 + d))          # grade do torpedo
    for i in range(22):
        x = -0.66 + i * 0.062; p.add('chassi', _cx(x, x + 0.03, yc - 0.0045, yc - 0.002, 0.645 + d, 0.685 + d))
    for x0, x1 in ((0.32, -0.25), (-0.30, -0.80)):
        cyl = trimesh.creation.cylinder(radius=0.016, height=0.03, sections=16); cyl.apply_transform(TF.rotation_matrix(-math.pi / 2, [1, 0, 0]))
        cyl.apply_translation([x0, yc + 0.005, 0.67 + d]); p.add('plastico_preto', cyl)
        z1 = 0.60 + d; y1 = SF.ytop(z1) + 0.012
        p.add('plastico_preto', tubo([(x0, yc + 0.02, 0.67 + d), ((x0 + x1) / 2, y1 + 0.01, z1 + 0.02), (x1, y1 + 0.005, z1)], 0.006))
        a = np.array([x0 + 0.02, SF.ytop(0.58 + d) + 0.012, 0.58 + d]); b = np.array([x1, SF.ytop(0.56 + d) + 0.012, 0.56 + d])
        for k in range(12):
            q0, q1 = a + (b - a) * k / 12, a + (b - a) * (k + 1) / 12
            p.add('borracha', trimesh.convex.convex_hull(np.array([q0, q1, q0 + [0, 0.012, 0.004], q1 + [0, 0.012, 0.004], q0 + [0, 0.004, 0.01], q1 + [0, 0.004, 0.01]])))
    ya = SF.yt(0.665 + d)
    p.add('cromado', _cil_y(0.012, ya - 0.01, ya + 0.005, -0.70, 0.665 + d, 16))
    p.add('aco_escuro', tubo([(-0.70, ya, 0.665 + d), (-0.71, ya + 0.62, 0.635 + d)], 0.003, 6))           # antena no pé da coluna
    p.add('cromado', trimesh.creation.icosphere(1, 0.006).apply_translation([-0.71, ya + 0.62, 0.635 + d]))


# ============================================================================ rodas, freios e suspensao
def _roda(q):
    """Roda aro 14 de aço com calota e pneu 185/70 com banda de rodagem em blocos. Origem no centro, lado de fora em +X."""
    perf = [(0.176, -0.080), (0.19, -0.088), (0.215, -0.093), (0.25, -0.095), (0.272, -0.092), (0.285, -0.084), (0.2895, -0.070), (0.2895, 0.070),
            (0.285, 0.084), (0.272, 0.092), (0.25, 0.095), (0.215, 0.093), (0.19, 0.088), (0.176, 0.080)]
    m = trimesh.creation.revolve(np.array([(r, x) for r, x in perf] + [perf[0]]), sections=72)
    if m.volume < 0: m.invert()
    m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); q.add('pneu', m)
    for xs in (-1, 1):                                                         # frisos do flanco
        a = trimesh.creation.revolve(np.array([(0.232, 0.0), (0.236, 0.0), (0.236, 0.003), (0.232, 0.003), (0.232, 0.0)]), sections=72)
        if a.volume < 0: a.invert()
        a.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); a.apply_translation([xs * 0.0945 - (0.003 if xs > 0 else 0), 0, 0]); q.add('pneu', a)
    N = 60
    for (x0, x1, fase, lb) in ((-0.022, 0.022, 0.0, 0.020), (0.029, 0.083, 0.5, 0.022), (-0.083, -0.029, 0.5, 0.022)):
        bl = trimesh.convex.convex_hull(np.array([[x, y, z] for x in (x0, x1) for (y, z) in
                                                  ((0.2885, -lb / 2), (0.2885, lb / 2), (0.3045, -lb / 2 + 0.002), (0.3045, lb / 2 - 0.002))]))
        for k in range(N):
            b = bl.copy(); b.apply_transform(TF.rotation_matrix(2 * math.pi * (k + fase) / N, [1, 0, 0])); q.add('pneu', b)
    aro = [(0.168, -0.072), (0.183, -0.072), (0.186, -0.066), (0.172, -0.060), (0.168, -0.040), (0.168, 0.040), (0.172, 0.060), (0.186, 0.066),
           (0.183, 0.072), (0.168, 0.072), (0.160, 0.066), (0.160, -0.066)]
    m = trimesh.creation.revolve(np.array(aro + [aro[0]]), sections=64)
    if m.volume < 0: m.invert()
    m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); q.add('aco_galv', m)
    disco = cil_x(0.162, 0.012, 0.020, 0, 0, 48)
    furos = [cil_x(0.012, 0.0, 0.03, 0.052 * math.sin(a), 0.052 * math.cos(a), 12) for a in np.arange(4) * math.pi / 2 + math.pi / 4]
    furos += [cil_x(0.022, 0.0, 0.03, 0.115 * math.sin(a), 0.115 * math.cos(a), 16) for a in np.arange(8) * math.pi / 4]
    furos += [cil_x(0.03, 0.0, 0.03, 0, 0, 24)]
    q.add('aco_galv', menos(disco, *furos))
    for a in np.arange(4) * math.pi / 2 + math.pi / 4:                          # porcas
        q.add('aco_escuro', cil_x(0.0095, 0.020, 0.036, 0.052 * math.sin(a), 0.052 * math.cos(a), 6))
    cal = trimesh.creation.revolve(np.array([(0.0, 0.068), (0.10, 0.064), (0.170, 0.058), (0.172, 0.064), (0.165, 0.070), (0.10, 0.074), (0.0, 0.074), (0.0, 0.068)]), sections=64)
    if cal.volume < 0: cal.invert()
    cal.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0]))
    rasgos = []
    for k in range(8):
        r = _cx(0.0, 0.2, -0.012, 0.012, 0.105, 0.150); r.apply_transform(TF.rotation_matrix(2 * math.pi * k / 8, [1, 0, 0])); rasgos.append(r)
    q.add('plastico_prata', menos(cal, *rasgos))
    m = trimesh.creation.revolve(np.array([(0.0, 0.074), (0.052, 0.074), (0.058, 0.080), (0.0, 0.084), (0.0, 0.074)]), sections=48)
    if m.volume < 0: m.invert()
    m.apply_transform(TF.rotation_matrix(math.pi / 2, [0, 1, 0])); q.add('plastico_prata', m)
    q.add('chassi', cil_x(0.045, 0.0835, 0.0845, 0, 0, 40))


def _cubos_e_suspensao(p):
    for zc, dianteira in ((SF.EIXO_D, True), (SF.EIXO_T, False)):
        for s in (1, -1):
            def L(m): return m if s > 0 else _mx(m)
            xw = SF.X_RODA; y = SF.Y_RODA
            p.add('aco_escuro', L(cil_x(0.045, xw - 0.08, xw - 0.002, y, zc, 24)))              # cubo
            for a in np.arange(4) * math.pi / 2 + math.pi / 4:
                p.add('aco', L(cil_x(0.006, xw - 0.002, xw + 0.03, y + 0.052 * math.sin(a), zc + 0.052 * math.cos(a), 8)))
            if dianteira:
                p.add('disco_freio', L(menos(cil_x(0.118, xw - 0.07, xw - 0.05, y, zc, 48), cil_x(0.05, xw - 0.08, xw - 0.04, y, zc, 24))))
                cal = trimesh.convex.convex_hull(np.array([[x, y + r * math.sin(a), zc - r * math.cos(a)] for x in (xw - 0.095, xw - 0.035)
                                                           for a in (0.5, 0.9, 1.3) for r in (0.075, 0.125)]))
                p.add('caliper', L(cal))
                p.add('aco_escuro', L(tubo([(xw - 0.10, y + 0.05, zc - 0.02), (xw - 0.13, y + 0.30, zc - 0.03)], 0.025, 16)))
                p.add('aco', L(tubo([(xw - 0.13, y + 0.30, zc - 0.03), (xw - 0.15, y + 0.42, zc - 0.035)], 0.011, 10)))
                hel = [(xw - 0.13 + 0.06 * math.cos(t) - 0.02 * t / 30, y + 0.20 + 0.20 * t / 30, zc - 0.03 + 0.06 * math.sin(t)) for t in np.linspace(0, 30, 160)]
                p.add('mola_amarela', L(tubo(hel, 0.0065, 8)))
                p.add('aco_escuro', L(tubo([(xw - 0.06, y - 0.08, zc), (0.28, y - 0.10, zc - 0.10)], 0.018, 10)))     # bandeja
                p.add('aco_escuro', L(tubo([(xw - 0.06, y - 0.08, zc), (0.28, y - 0.09, zc + 0.14)], 0.014, 10)))
                p.add('aco_escuro', L(tubo([(xw - 0.08, y + 0.02, zc - 0.12), (0.30, y + 0.0, zc - 0.16)], 0.010, 10)))   # barra de direção
                p.add('borracha', L(tubo([(0.32, y + 0.0, zc - 0.155), (0.40, y - 0.01, zc - 0.165)], 0.02, 12)))
                p.add('aco_escuro', L(tubo([(xw - 0.09, y, zc), (0.42, y - 0.04, zc + 0.04)], 0.014, 10)))                 # semieixo
                p.add('borracha', L(tubo([(xw - 0.16, y - 0.007, zc + 0.01), (xw - 0.10, y - 0.001, zc)], 0.035, 14)))
                p.add('chassi', L(_cil_y(0.075, y + 0.40, y + 0.44, xw - 0.16, zc - 0.035, 24)))                         # torre
            else:
                p.add('disco_freio', L(cil_x(0.11, xw - 0.10, xw - 0.04, y, zc, 48)))           # tambor
                p.add('chassi', L(cil_x(0.112, xw - 0.11, xw - 0.10, y, zc, 48)))
                p.add('aco_escuro', L(tubo([(xw - 0.10, y - 0.02, zc - 0.05), (xw - 0.12, y + 0.26, zc - 0.08)], 0.02, 12)))
                hel = [(xw - 0.20 + 0.055 * math.cos(t), y - 0.04 + 0.24 * t / 28, zc + 0.07 + 0.055 * math.sin(t)) for t in np.linspace(0, 28, 150)]
                p.add('mola_amarela', L(tubo(hel, 0.006, 8)))
                p.add('aco_escuro', L(tubo([(xw - 0.11, y, zc), (xw - 0.17, y - 0.08, zc + 0.30)], 0.025, 10)))          # braço arrastado
    p.add('aco_escuro', tubo([(-0.56, SF.Y_RODA - 0.09, SF.EIXO_T + 0.30), (0.56, SF.Y_RODA - 0.09, SF.EIXO_T + 0.30)], 0.035, 16))   # eixo de torção
    p.add('aco_escuro', tubo([(-0.30, SF.Y_RODA - 0.10, SF.EIXO_D - 0.14), (0.30, SF.Y_RODA - 0.10, SF.EIXO_D - 0.14)], 0.012, 10))  # caixa de direção
    p.add('aco_escuro', _cx(-0.55, 0.55, 0.205, 0.235, SF.EIXO_D - 0.30, SF.EIXO_D + 0.28))                                       # agregado


# ============================================================================ motor e mecânica
def _cil_y(r, y0, y1, x, z, sec=24):
    c = trimesh.creation.cylinder(radius=r, height=y1 - y0, sections=sec); c.apply_transform(TF.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    c.apply_translation([x, (y0 + y1) / 2, z]); return c


def _cil_z(r, z0, z1, x, y, sec=24):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sec); c.apply_translation([x, y, (z0 + z1) / 2]); return c


ZM = 1.30      # centro do motor (transversal)


def _motor(q):
    """Motor 1.6 de 4 cilindros transversal, câmbio acoplado à esquerda (+X). Origem no centro da base do bloco."""
    xa, xb = -0.24, 0.22
    q.add('ferro_fundido', _cham(xa, xb, 0.33, 0.62, ZM - 0.12, ZM + 0.11, 0.012))
    for i in range(5):
        x = xa + 0.03 + i * 0.1; q.add('ferro_fundido', _cham(x - 0.01, x + 0.01, 0.34, 0.60, ZM + 0.105, ZM + 0.125, 0.004))
    q.add('aluminio_fundido', _cham(xa + 0.01, xb - 0.01, 0.26, 0.335, ZM - 0.10, ZM + 0.09, 0.015))          # cárter
    for x in np.linspace(xa + 0.04, xb - 0.04, 8): q.add('aluminio_fundido', _cx(x - 0.003, x + 0.003, 0.27, 0.33, ZM + 0.088, ZM + 0.096))
    q.add('aco', _cil_y(0.012, 0.255, 0.265, 0.0, ZM, 6))
    q.add('aluminio', _cham(xa + 0.005, xb - 0.005, 0.62, 0.70, ZM - 0.115, ZM + 0.10, 0.01))                 # cabeçote
    q.add('tinta_motor', _cham(xa + 0.02, xb - 0.02, 0.70, 0.765, ZM - 0.095, ZM + 0.075, 0.025))             # tampa de válvulas
    for k in range(6): q.add('tinta_motor', _cx(xa + 0.06 + k * 0.055, xa + 0.07 + k * 0.055, 0.762, 0.772, ZM - 0.06, ZM + 0.04))
    q.add('plastico_preto', _cil_y(0.022, 0.765, 0.795, -0.12, ZM - 0.06, 20))                                # tampa do óleo
    q.add('amarelo_tampa', _cil_y(0.008, 0.70, 0.80, 0.16, ZM + 0.09, 10))                                     # vareta
    q.add('amarelo_tampa', trimesh.creation.torus(0.014, 0.004, 16, 6).apply_transform(TF.rotation_matrix(math.pi / 2, [0, 0, 1])).apply_translation([0.16, 0.815, ZM + 0.09]))
    for k in range(4):                                                                                        # admissão
        x = -0.16 + k * 0.105
        q.add('aluminio_fundido', tubo([(x, 0.665, ZM - 0.115), (x, 0.66, ZM - 0.20), (x * 0.6, 0.62, ZM - 0.27)], 0.022, 14))
    q.add('aluminio_fundido', _cham(-0.18, 0.18, 0.56, 0.66, ZM - 0.34, ZM - 0.25, 0.02))
    q.add('aluminio', _cil_z(0.04, ZM - 0.40, ZM - 0.33, 0.0, 0.64, 24))
    for k in range(4):                                                                                        # escape
        x = -0.16 + k * 0.105
        q.add('ferro_fundido', tubo([(x, 0.64, ZM + 0.10), (x, 0.62, ZM + 0.17), (x * 0.4, 0.52, ZM + 0.20), (0.0, 0.42, ZM + 0.19)], 0.019, 12))
    q.add('aco_galv', _cham(-0.20, 0.20, 0.52, 0.67, ZM + 0.205, ZM + 0.215, 0.004))
    polias = [((ZM - 0.02, 0.38), 0.075), ((ZM + 0.16, 0.56), 0.045), ((ZM - 0.04, 0.56), 0.05)]
    for (z, y), r in polias[:1] + polias[2:]:
        q.add('aco', cil_x(r, xa - 0.05, xa - 0.025, y, z, 32)); q.add('aco_escuro', cil_x(r * 0.4, xa - 0.06, xa - 0.02, y, z, 16))
    from shapely.geometry import MultiPoint
    hull = MultiPoint([(z + r * math.cos(a), y + r * math.sin(a)) for (z, y), r in polias for a in np.linspace(0, 2 * math.pi, 40)]).convex_hull
    cam = [(xa - 0.0375, y, z) for (z, y) in list(hull.exterior.coords)]
    q.add('borracha', varrer_caminho([(-0.004, -0.011), (0.004, -0.011), (0.004, 0.011), (-0.004, 0.011)], cam, normal_ref=(1, 0, 0)))
    q.add('plastico_preto', _cham(xa - 0.035, xa - 0.002, 0.42, 0.74, ZM - 0.12, ZM + 0.08, 0.01))            # capa da correia dentada
    q.add('plastico_preto', cil_x(0.035, xb + 0.0, xb + 0.06, 0.66, ZM - 0.02, 20))                           # distribuidor
    q.add('plastico_cinza', cil_x(0.040, xb + 0.06, xb + 0.09, 0.66, ZM - 0.02, 20))
    for k in range(4):
        x = -0.16 + k * 0.105
        q.add('plastico_preto', _cil_y(0.009, 0.765, 0.79, x, ZM - 0.01, 10))
        q.add('fio_preto', tubo([(x, 0.79, ZM - 0.01), (x + 0.02, 0.80, ZM + 0.02), ((x + xb + 0.09) / 2, 0.79, ZM + 0.03), (xb + 0.09, 0.67 + k * 0.006, ZM - 0.02)], 0.005, 6))
    q.add('aluminio_fundido', trimesh.convex.convex_hull(np.array([[xb, y, z] for y in (0.30, 0.64) for z in (ZM - 0.13, ZM + 0.11)] +
                                                                   [[xb + 0.24, y, z] for y in (0.32, 0.56) for z in (ZM - 0.10, ZM + 0.08)])))
    for k in range(5): q.add('aluminio_fundido', _cx(xb + 0.03 + k * 0.045, xb + 0.04 + k * 0.045, 0.30, 0.62, ZM + 0.09, ZM + 0.12))
    q.add('aluminio_fundido', cil_x(0.08, xb + 0.24, xb + 0.30, 0.45, ZM, 28))
    for (x, z) in ((-0.20, ZM + 0.13), (0.40, ZM + 0.14), (0.0, ZM - 0.16)):
        q.add('borracha', _cil_y(0.03, 0.42, 0.47, x, z, 16))
    q.add('borracha', tubo(suavizar_caminho([(-0.10, 0.70, ZM + 0.10), (-0.14, 0.72, ZM + 0.30), (-0.30, 0.68, ZM + 0.45), (-0.42, 0.66, 1.86)], 3), 0.02, 14))
    q.add('borracha', tubo(suavizar_caminho([(-0.20, 0.42, ZM + 0.08), (-0.10, 0.40, ZM + 0.30), (0.40, 0.42, 1.80), (0.46, 0.44, 1.86)], 3), 0.02, 14))
    q.add('plastico_preto', _cham(-0.62, -0.30, 0.58, 0.74, 1.40, 1.66, 0.025))                               # filtro de ar
    q.add('plastico_preto', _cham(-0.625, -0.295, 0.655, 0.67, 1.395, 1.665, 0.006))
    for (x, z) in ((-0.61, 1.41), (-0.31, 1.41), (-0.61, 1.65), (-0.31, 1.65)): q.add('aco', _cil_y(0.006, 0.735, 0.75, x, z, 8))
    q.add('borracha', tubo(suavizar_caminho([(-0.30, 0.68, 1.50), (-0.12, 0.70, 1.42), (-0.02, 0.69, ZM - 0.20), (0.0, 0.66, ZM - 0.36)], 3), 0.035, 18))


def _alternador(q):
    x, y, z = -0.265, 0.56, ZM + 0.16
    q.add('aluminio_fundido', cil_x(0.062, x + 0.005, x + 0.11, y, z, 28))
    q.add('aco', cil_x(0.045, x - 0.025, x, y, z, 32)); q.add('aco_escuro', cil_x(0.018, x - 0.035, x + 0.005, y, z, 16))
    for k in range(10):
        a = k * 2 * math.pi / 10
        q.add('aluminio_fundido', _cx(x + 0.01, x + 0.10, y + 0.062 * math.sin(a) - 0.004, y + 0.062 * math.sin(a) + 0.004, z + 0.062 * math.cos(a) - 0.004, z + 0.062 * math.cos(a) + 0.004))
    q.add('aco_escuro', cil_x(0.03, x + 0.11, x + 0.125, y, z, 16))
    q.add('cobre', _cil_y(0.006, y + 0.06, y + 0.08, x + 0.07, z, 8))
    q.add('aluminio_fundido', _cx(x + 0.03, x + 0.08, y - 0.09, y - 0.05, z - 0.02, z + 0.02))


def _radiador(q):
    zr = 1.905
    q.add('radiador_colmeia', _cx(-0.47, 0.47, 0.38, 0.715, zr - 0.012, zr + 0.012))
    for (a, b) in ((0.47, 0.53), (-0.53, -0.47)):
        q.add('plastico_preto', _cham(a, b, 0.37, 0.725, zr - 0.03, zr + 0.025, 0.01))
    q.add('plastico_preto', _cil_y(0.022, 0.725, 0.745, 0.50, zr, 16))
    q.add('aco', _cil_y(0.026, 0.745, 0.755, 0.50, zr, 16))
    q.add('plastico_preto', _cil_z(0.022, zr - 0.08, zr - 0.03, -0.50, 0.66, 14))
    q.add('plastico_preto', _cil_z(0.022, zr - 0.08, zr - 0.03, 0.50, 0.44, 14))
    cf = menos(_cham(-0.44, 0.44, 0.39, 0.705, zr - 0.075, zr - 0.012, 0.02), _cil_z(0.155, zr - 0.08, zr, -0.20, 0.55, 40), _cil_z(0.155, zr - 0.08, zr, 0.20, 0.55, 40))
    q.add('plastico_preto', cf)
    for xc in (-0.20, 0.20):
        q.add('aco_escuro', _cil_z(0.045, zr - 0.13, zr - 0.05, xc, 0.55, 24))
        for k in range(7):
            a = k * 2 * math.pi / 7
            pa = trimesh.convex.convex_hull(np.array([[xc + r * math.cos(a + d), 0.55 + r * math.sin(a + d), zr - 0.04 - 0.012 * (d / 0.35)]
                                                      for r in (0.045, 0.148) for d in (-0.18, 0.18)]))
            q.add('plastico_preto', pa)


def _bateria(q):
    x0, x1, z0, z1, y0 = 0.18, 0.42, 0.84, 1.015, 0.565
    y1 = y0 + 0.175
    q.add('bateria_caixa', _cham(x0, x1, y0, y1, z0, z1, 0.008))
    for k in range(5): q.add('bateria_caixa', _cx(x0 - 0.003, x0 + 0.002, y0 + 0.02, y1 - 0.02, z0 + 0.025 + k * 0.03, z0 + 0.035 + k * 0.03))
    q.add('bateria_tampa', _cham(x0 + 0.005, x1 - 0.005, y1 - 0.004, y1 + 0.012, z0 + 0.005, z1 - 0.005, 0.005))
    for k in range(6): q.add('plastico_cinza', _cil_y(0.011, y1 + 0.012, y1 + 0.02, x0 + 0.03 + k * 0.036, (z0 + z1) / 2, 12))
    for x, cor in ((x0 + 0.025, 'vermelho_borne'), (x1 - 0.025, 'plastico_preto')):
        q.add('chumbo', _cil_y(0.009, y1 + 0.012, y1 + 0.032, x, z1 - 0.03, 12))
        q.add(cor, _cham(x - 0.02, x + 0.02, y1 + 0.026, y1 + 0.05, z1 - 0.055, z1 - 0.008, 0.006))
    q.add('plastico_preto', tubo([(x0 + 0.06, y1 + 0.012, (z0 + z1) / 2), (x0 + 0.08, y1 + 0.07, (z0 + z1) / 2), (x1 - 0.08, y1 + 0.07, (z0 + z1) / 2), (x1 - 0.06, y1 + 0.012, (z0 + z1) / 2)], 0.006, 8))
    q.add('amarelo_tampa', _cx(x0 + 0.02, x1 - 0.02, y0 + 0.07, y0 + 0.12, z1 + 0.0, z1 + 0.002))


def _escapamento(q):
    cam = suavizar_caminho([(0.0, 0.42, ZM + 0.19), (0.0, 0.30, ZM + 0.26), (-0.02, 0.17, ZM + 0.10), (-0.05, 0.165, 0.6), (-0.05, 0.165, -0.20),
                            (-0.06, 0.165, -0.55), (-0.08, 0.165, -1.6), (-0.15, 0.17, -1.86)], 3)
    q.add('aco_galv', tubo(cam, 0.024, 14))
    q.add('aco_galv', _cham(-0.12, 0.02, 0.135, 0.205, -0.55, -0.20, 0.03))                                   # ressonador
    q.add('aco_galv', _cham(-0.50, -0.10, 0.115, 0.225, -2.17, -1.86, 0.035))                                  # silencioso
    q.add('aco_galv', tubo([(-0.40, 0.17, -2.17), (-0.42, 0.18, -2.25), (-0.43, 0.19, -2.32)], 0.022, 14))
    q.add('ferrugem', _cil_z(0.026, -2.33, -2.30, -0.43, 0.19, 16))
    for x, z in ((-0.05, -0.40), (-0.30, -1.95)): q.add('borracha', _cil_y(0.008, 0.20, 0.235, x, z, 8))


def _tanque(q):
    q.add('aco_galv', _cham(-0.40, 0.40, 0.125, 0.222, -1.00, -0.66, 0.03))
    for z in (-0.86, -0.80): q.add('aco_galv', _cx(-0.40, 0.40, 0.12, 0.125, z - 0.004, z + 0.004))
    for x in (-0.30, 0.30): q.add('aco_escuro', _cx(x - 0.015, x + 0.015, 0.115, 0.224, -1.01, -0.65))          # cintas
    q.add('aco_galv', _cil_y(0.03, 0.222, 0.232, 0.30, -0.95, 20))


def _bocal(p):
    """Bocal do tanque atrás da portinhola: copo, tampa e a mangueira até o tanque (segue Z_BOCAL e a lateral do modelo)."""
    dz = SF.Z_BOCAL + 1.86; dx = SF.x_lado(SF.Z_BOCAL, 1.0) - 0.8085
    T = TF.translation_matrix([dx, 0, dz])
    p.add('chassi', menos(_cx(0.715, 0.778, 0.735, 0.865, -1.958, -1.762), _cx(0.725, 0.9, 0.745, 0.855, -1.948, -1.772)).apply_transform(T))
    p.add('plastico_preto', cil_x(0.034, 0.725, 0.745, 0.80, -1.86, 24).apply_transform(T))
    p.add('plastico_preto', _cx(0.742, 0.752, 0.79, 0.81, -1.89, -1.83).apply_transform(T))
    p.add('borracha', tubo(suavizar_caminho([(0.36, 0.20, -0.95), (0.50, 0.30, -1.10), (0.62 + dx, 0.55, -1.55 + dz * 0.5), (0.70 + dx, 0.74, -1.80 + dz),
                                             (0.74 + dx, 0.80, -1.86 + dz)], 3), 0.024, 14))


def _cofre(p):
    """O que fica no cofre do motor preso à carroceria."""
    p.add('chassi', _cx(-0.58, 0.58, 0.71, 0.745, 1.955, 1.99))
    p.add('chassi', _cx(-0.58, 0.58, 0.32, 0.36, 1.955, 1.99))
    for s in (1, -1): p.add('chassi', _cx(s * 0.53 - 0.03, s * 0.53 + 0.03, 0.32, 0.745, 1.955, 1.99))
    p.add('aco_escuro', _cx(-0.05, 0.05, 0.73, 0.75, 1.93, 1.955))                                           # fecho do capô
    p.add('chassi', _cx(0.16, 0.44, 0.545, 0.565, 0.82, 1.035))                                              # bandeja da bateria
    p.add('fio_vermelho', tubo(suavizar_caminho([(0.205, 0.80, 0.985), (0.24, 0.84, 1.05), (0.30, 0.72, 1.20), (0.36, 0.62, 1.32)], 3), 0.008, 8))
    p.add('fio_preto', tubo(suavizar_caminho([(0.395, 0.80, 0.985), (0.44, 0.78, 1.0), (0.52, 0.70, 0.90)], 3), 0.008, 8))
    p.add('chassi', _cil_z(0.105, 0.735, 0.84, 0.50, 0.66, 36))                                             # servo-freio
    p.add('aluminio', _cil_z(0.03, 0.84, 0.97, 0.50, 0.66, 16))
    p.add('plastico_translucido', _cham(0.46, 0.56, 0.70, 0.76, 0.86, 0.92, 0.01))
    p.add('plastico_translucido', _cham(-0.64, -0.48, 0.60, 0.78, 0.76, 0.96, 0.02))                        # água do limpador
    p.add('plastico_preto', _cil_y(0.022, 0.78, 0.80, -0.56, 0.86, 16))
    p.add('plastico_translucido', _cham(-0.46, -0.30, 0.62, 0.76, 1.64, 1.78, 0.02))                        # expansão do radiador
    p.add('amarelo_tampa', _cil_y(0.024, 0.76, 0.785, -0.38, 1.71, 16))
    p.add('plastico_preto', _cham(-0.42, -0.26, 0.66, 0.73, 0.78, 0.92, 0.01))                              # caixa de fusíveis
    p.add('chassi', _cx(-0.70, 0.70, 0.30, 0.885, 0.715, 0.735))                                             # corta-fogo


# ============================================================================ interior e porta-malas
def _mostrador():
    """Mostradores sem marca: velocímetro e conta-giros com riscos, combustível e temperatura com ícones simples."""
    W, H = 1024, 320; im = Image.new('RGB', (W, H), (18, 18, 20)); d = ImageDraw.Draw(im)
    def disco(cx, cy, r, n, a0=-225, a1=45, verm=None):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 10, 12), outline=(90, 90, 92), width=4)
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n); l = 0.16 if k % 2 == 0 else 0.09
            cor = (220, 60, 40) if verm is not None and k >= verm else (230, 230, 226)
            d.line([cx + r * 0.86 * math.cos(a), cy + r * 0.86 * math.sin(a), cx + r * (0.86 - l) * math.cos(a), cy + r * (0.86 - l) * math.sin(a)], fill=cor, width=5 if k % 2 == 0 else 3)
        a = math.radians(a0 + 12); d.line([cx, cy, cx + r * 0.7 * math.cos(a), cy + r * 0.7 * math.sin(a)], fill=(240, 120, 30), width=6)
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(40, 40, 42))
    disco(300, 165, 140, 22); disco(724, 165, 140, 16, verm=13)
    for cx, ic in ((90, 'gota'), (934, 'term')):
        d.rounded_rectangle([cx - 60, 60, cx + 60, 270], 12, fill=(10, 10, 12), outline=(90, 90, 92), width=3)
        for k in range(5): d.line([cx - 30, 90 + k * 40, cx + 30, 90 + k * 40], fill=(220, 220, 216), width=3)
        d.line([cx - 40, 240, cx + 30, 110], fill=(240, 120, 30), width=5)
        if ic == 'gota': d.rectangle([cx - 12, 248, cx + 12, 266], fill=(200, 200, 196))
        else: d.ellipse([cx - 10, 248, cx + 10, 266], fill=(200, 200, 196))
    return im


def _painel(Vc, dentro):
    p = Vc.base
    perfil = chaikin([(0.74, 0.58), (0.74, 0.935), (0.60, 0.95), (0.42, 0.935), (0.27, 0.905), (0.215, 0.87), (0.21, 0.80), (0.245, 0.69),
                      (0.31, 0.60), (0.42, 0.52), (0.60, 0.48), (0.74, 0.47)], 2)
    corpo = inter(prisma_zy(_Pg(perfil), -0.79, 0.79), dentro)
    corpo = menos(corpo, _cx(-0.58, -0.17, 0.59, 0.73, 0.22, 0.48), _cx(0.195, 0.545, 0.80, 0.925, 0.15, 0.30))
    p.add('painel', corpo)
    p.add('painel', inter(_cx(-0.575, -0.175, 0.595, 0.725, 0.47, 0.48), dentro))                        # fundo do porta-luvas
    p.add('painel', trimesh.convex.convex_hull(np.array([[x, y, z] for x in (0.17, 0.57) for (y, z) in ((0.925, 0.20), (0.975, 0.215), (0.985, 0.42), (0.925, 0.45))])))
    p.add('chassi', _cx(0.195, 0.545, 0.80, 0.925, 0.30, 0.31))
    mat_imagem('mostrador', _mostrador(), rough=0.3)
    q = trimesh.Trimesh(vertices=[[0.54, 0.808, 0.299], [0.20, 0.808, 0.299], [0.20, 0.918, 0.299], [0.54, 0.918, 0.299]], faces=[[0, 2, 1], [0, 3, 2], [0, 1, 2], [0, 2, 3]], process=False)
    p.add('mostrador', q); p.uv['mostrador'] = lambda v, n: np.column_stack([(0.54 - v[:, 0]) / 0.34, (v[:, 1] - 0.808) / 0.11])
    for x0 in (-0.16, 0.02, 0.58, -0.70):                                                                    # saídas de ar
        x1 = x0 + 0.14 if x0 > -0.6 else x0 + 0.10
        if x0 >= 0.58: x1 = 0.68
        zc = 0.235 if -0.3 < x0 < 0.3 else 0.30
        p.add('chassi', _cx(x0, x1, 0.80, 0.86, zc - 0.006, zc + 0.01))
        for k in range(5): p.add('plastico_preto', _cx(x0 + 0.004, x1 - 0.004, 0.805 + k * 0.012, 0.810 + k * 0.012, zc - 0.012, zc))
    p.add('chassi', _cx(-0.10, 0.10, 0.69, 0.745, 0.255, 0.27))                                               # rádio
    p.add('plastico_preto', _cham(-0.098, 0.098, 0.692, 0.743, 0.25, 0.258, 0.003))
    p.add('lente_pisca', _cx(-0.05, 0.03, 0.71, 0.73, 0.2475, 0.25))
    for x in (-0.075, 0.075): p.add('plastico_cinza', _cil_z(0.011, 0.235, 0.25, x, 0.717, 16))
    for x in (-0.07, 0.0, 0.07): p.add('plastico_cinza', _cil_z(0.016, 0.28, 0.30, x, 0.635, 20))
    p.add('chassi', _cx(-0.10, 0.10, 0.60, 0.67, 0.29, 0.30))
    gl = Vc.achar('porta_luvas')['geo']
    gl.add('painel', _cham(-0.582, -0.168, 0.586, 0.734, 0.205, 0.225, 0.006))
    gl.add('cromado', _cx(-0.40, -0.34, 0.705, 0.715, 0.198, 0.205))
    d = np.array([0.0, 0.14, -0.34]); d /= np.linalg.norm(d); base = np.array([0.37, 0.68, 0.40]); pc = np.array([0.37, 0.82, 0.06])
    p.add('plastico_preto', tubo([base, pc - d * 0.05], 0.045, 20))
    p.add('plastico_preto', tubo([pc - d * 0.12 + [0.04, 0, 0], pc - d * 0.10 + [0.16, -0.01, 0]], 0.008, 8))   # alavanca da seta
    vol = Vc.achar('volante')['geo']
    R = trimesh.geometry.align_vectors([0, 0, 1], d)
    aro = trimesh.creation.torus(0.185, 0.016, 48, 10); aro.apply_transform(R); aro.apply_translation(pc + d * 0.06); vol.add('vinil', aro)
    cubo = trimesh.creation.cylinder(radius=0.06, height=0.05, sections=32); cubo.apply_transform(R); cubo.apply_translation(pc + d * 0.03); vol.add('plastico_preto', cubo)
    for a in (math.radians(-20), math.radians(200), math.radians(270)):
        v = R[:3, :3] @ np.array([math.cos(a), math.sin(a), 0])
        vol.add('plastico_preto', tubo([pc + d * 0.05 + v * 0.05, pc + d * 0.065 + v * 0.175], 0.012, 10))
    for x, w in ((0.47, 0.035), (0.37, 0.045), (0.27, 0.045)):                                                # pedais
        p.add('aco_escuro', tubo([(x, 0.72, 0.42), (x, 0.50, 0.50), (x, 0.40, 0.46)], 0.008, 8))
        p.add('borracha', _cham(x - w, x + w, 0.36, 0.44, 0.45, 0.47, 0.006).apply_transform(TF.rotation_matrix(math.radians(-25), [1, 0, 0], [x, 0.40, 0.46])))
    p.add('carpete', _cham(-0.13, 0.13, 0.28, 0.42, -0.70, 0.72, 0.05))                                    # túnel
    p.add('borracha', trimesh.creation.cone(0.07, 0.11, 16).apply_transform(TF.rotation_matrix(-math.pi / 2, [1, 0, 0])).apply_translation([0.0, 0.42, -0.05]))
    p.add('aco_escuro', tubo([(0.0, 0.48, -0.05), (0.0, 0.62, -0.09)], 0.007, 8))
    p.add('plastico_preto', trimesh.creation.icosphere(2, 0.026).apply_translation([0.0, 0.64, -0.095]))
    p.add('plastico_preto', _cham(-0.10, 0.10, 0.40, 0.48, -0.62, -0.20, 0.02))                            # console
    p.add('chassi', _cx(-0.08, 0.08, 0.465, 0.481, -0.58, -0.40))
    p.add('plastico_preto', tubo([(0.0, 0.48, -0.34), (0.0, 0.55, -0.12)], 0.016, 10))                      # freio de mão
    p.add('aco_escuro', _cil_z(0.006, -0.12, -0.09, 0.0, 0.552, 8))


def _banco_dianteiro(q, x):
    q.add('aco_escuro', _cx(x - 0.20, x - 0.17, 0.29, 0.31, -0.62, 0.05)); q.add('aco_escuro', _cx(x + 0.17, x + 0.20, 0.29, 0.31, -0.62, 0.05))
    q.add('aco_escuro', _cham(x - 0.23, x + 0.23, 0.31, 0.37, -0.52, -0.02, 0.02))
    fofo(q, 'tecido_banco', x, 0.42, -0.26, 0.245, 0.065, 0.25, 0.3, 0.25, (16, 24))
    for s in (-1, 1): fofo(q, 'vinil', x + s * 0.215, 0.445, -0.28, 0.04, 0.06, 0.24, 0.4, 0.35, (12, 16))
    fofo(q, 'tecido_banco', x, 0.78, -0.56, 0.24, 0.30, 0.065, 0.3, 0.25, (20, 20), rot_x=-0.22)
    for s in (-1, 1): fofo(q, 'vinil', x + s * 0.215, 0.76, -0.54, 0.04, 0.27, 0.06, 0.35, 0.35, (14, 14), rot_x=-0.22)
    for s in (-0.08, 0.08): q.add('aco', tubo([(x + s, 1.06, -0.61), (x + s, 1.14, -0.63)], 0.006, 8))
    fofo(q, 'tecido_banco', x, 1.19, -0.635, 0.13, 0.085, 0.05, 0.35, 0.3, (14, 14), rot_x=-0.22)
    q.add('plastico_preto', _cham(x + (0.23 if x > 0 else -0.25), x + (0.25 if x > 0 else -0.23), 0.35, 0.42, -0.50, -0.40, 0.006))


def _banco_traseiro(q):
    fofo(q, 'tecido_banco', 0.0, 0.43, -1.13, 0.47, 0.075, 0.25, 0.25, 0.2, (16, 32))
    q.add('chassi', _cx(-0.46, 0.46, 0.30, 0.37, -1.36, -0.90))
    fofo(q, 'tecido_banco', 0.0, 0.70, -1.45, 0.47, 0.27, 0.07, 0.25, 0.2, (20, 32), rot_x=-0.38)
    for x in (-0.57, 0.57): fofo(q, 'tecido_banco', x, 0.83, -1.50, 0.10, 0.14, 0.065, 0.3, 0.3, (12, 12), rot_x=-0.38)
    for x in (-0.42, 0.42):
        fofo(q, 'tecido_banco', x, 0.98, -1.555, 0.12, 0.06, 0.05, 0.35, 0.3, (12, 12), rot_x=-0.38)


def _quebra_sol():
    """(y, z) da dobradiça dos quebra-sóis: logo atrás da borda de cima do para-brisa, encostada no forro."""
    zv = SF.Z_TOPO_PARABRISA - 0.025
    return round(SF.ytop(zv) - 0.028, 3), round(zv, 3)


def _forro_e_cabine(Vc, dentro):
    p = Vc.base
    teto = menos(SF.corpo_cabine(0.022, pontas=0.03), SF.corpo_cabine(0.034, desce=0.03, pontas=0.02))
    p.add('forro_teto', inter(teto, _cx(-0.62, 0.62, 1.255, 2.0, SF.Z_FORRO_TRAS, 0.25)))
    T = lambda m, dy, dz=0.0: m.apply_translation([0, dy, dz])
    dl = SF.ytop(-0.47) - 1.389                                                                              # a luz segue o teto
    p.add('plastico_translucido', T(_cham(-0.08, 0.08, 1.335, 1.355, -0.52, -0.42, 0.01), dl))               # luz de teto
    yv, zv = _quebra_sol(); dy, dz = yv - 1.336, zv + 0.215                                                  # o resto segue a borda do para-brisa
    p.add('plastico_preto', T(_cham(-0.12, 0.12, 1.255, 1.315, -0.235, -0.20, 0.01), dy, dz))                # retrovisor interno
    p.add('espelho_retrovisor', T(_cx(-0.115, 0.115, 1.26, 1.31, -0.2355, -0.2345), dy, dz))
    p.add('plastico_preto', T(tubo([(0.0, 1.31, -0.215), (0.0, 1.345, -0.205)], 0.008, 8), dy, dz))
    for no, xc in (('quebra_sol_e', 0.38), ('quebra_sol_d', -0.38)):
        g = Vc.achar(no)['geo']
        g.add('forro_teto', T(_cham(xc - 0.18, xc + 0.18, 1.316, 1.336, -0.40, -0.215, 0.008), dy, dz))
        if xc < 0: g.add('espelho_retrovisor', T(_cx(xc - 0.07, xc + 0.07, 1.3155, 1.3165, -0.36, -0.27), dy, dz))
    tipo = getattr(SF, 'TIPO', 'sedan')
    p.add('carpete', inter(dentro, _cx(-0.79, 0.79, 0.0, 0.29, getattr(SF, 'Z_PISO_TRAS', -1.72), 0.735)))   # carpete do piso
    if tipo == 'sedan':
        p.add('chassi', inter(dentro, _cx(-0.79, 0.79, 0.478, 0.955, -1.745, -1.72)))                      # parede atrás do banco
        p.add('carpete', inter(dentro, _cx(-0.79, 0.79, 0.935, 0.955, -1.72, -1.46)))                      # tampão traseiro
        for x in (-0.45, 0.45):
            p.add('plastico_preto', _cil_y(0.06, 0.955, 0.962, x, -1.60, 28))
            for k in range(4): p.add('chassi', _cx(x - 0.05, x + 0.05, 0.962, 0.964, -1.64 + k * 0.025, -1.632 + k * 0.025))
    for s in (1, -1):                                                                                       # cintos
        def L(m): return m if s > 0 else _mx(m)
        p.add('plastico_preto', L(_cham(0.66, 0.70, 1.13, 1.19, -0.47, -0.43, 0.008)))
        p.add('fio_preto', L(trimesh.convex.convex_hull(np.array([[0.655, 1.16, -0.445], [0.66, 1.16, -0.41], [0.585, 0.45, -0.20], [0.59, 0.45, -0.165], [0.66, 1.165, -0.43]]))))


def _porta_malas(Vc, dentro):
    p = Vc.base
    ass = Vc.achar('assoalho_porta_malas')['geo']
    ass.add('carpete', inter(dentro, _cx(-0.79, 0.79, 0.458, 0.478, -2.24, -1.748)))
    ass.add('plastico_preto', _cx(-0.06, 0.06, 0.478, 0.486, -2.10, -2.06))
    p.add('carpete', menos(inter(dentro, _cx(-0.79, 0.79, 0.43, 0.458, -2.24, -1.748)), _cx(-0.60, 0.60, 0.40, 0.46, -2.2, -1.75)))   # aba do poço
    p.add('chassi', inter(dentro, _cx(-0.79, 0.79, 0.24, 0.27, -2.24, -1.70)))                              # fundo do poço
    for s in (1, -1):
        def L(m): return m if s > 0 else _mx(m)
        p.add('carpete', L(inter(dentro, _cx(0.64, 0.66, 0.478, 0.90, -2.15, -1.76))))
    p.add('aco_escuro', _cx(-0.03, 0.03, 0.62, 0.66, -2.235, -2.21))                                        # fechadura
