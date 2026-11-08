"""Gerador dos VEICULOS do Recomeco: carros em pecas separadas (cada peca e um no e tambem um item de loot),
partes que abrem (portas, capo, porta-malas...), compartimentos com grade de saque e as ferramentas de oficina.

Uso:  python props/veiculos/gerar_veiculos.py                 (gera tudo)
      python props/veiculos/gerar_veiculos.py sedan_rumo      (so o carro)
      python props/veiculos/gerar_veiculos.py ferramentas     (so as ferramentas)
      DESGASTE=0.6 python props/veiculos/gerar_veiculos.py   (sujeira da pintura, 0 = limpo, 1 = muito sujo; padrao 0,35)

Saida:
  props/veiculos/<modelo>.glb              o carro inteiro: um no por peca, com origem na dobradica ou no ponto de fixacao
  props/veiculos/pecas/<id>.glb            cada peca sozinha, deitada, pivo no centro da base (item de loot)
  props/veiculos/ferramentas/<id>.glb      ferramentas e materiais de oficina (loot)
  props/veiculos/catalogo.json             modelos (encaixes, partes, compartimentos), pecas e ferramentas
  props/veiculos/CATALOGO.md               tabelas em portugues

Convencoes (docs/veiculos.md, secao 11): Y para cima, 1 unidade = 1 m, frente do carro para +Z, lado esquerdo (motorista) em +X,
pivo do carro no chao no meio dos eixos. O jogo usa VehicleBody3D (frente +Z) com uma VehicleWheel3D em cada no roda_*.
"""
import os, sys, math, json, re
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(AQUI, '..'))
import gerar_props as gp
from gerar_props import P, torno, anel, cyl_eixo, fofo, circ, varrer
from detalhe import MATS, TEX, KIND, GT, tex_set, PBRMaterial, glb_jpeg
import numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFilter

TF = trimesh.transformations
DESGASTE = float(os.environ.get('DESGASTE', '0.35'))
COR_PINTURA = (128, 26, 20)       # cor padrao da lataria (sRGB); o jogo troca pelo baseColorFactor

# ============================================================================ materiais
CORES = {
    'pintura': (255, 255, 255),           # a cor vem do baseColorFactor (o jogo sorteia)
    'cromado': (214, 216, 220), 'aco_escuro': (62, 64, 68), 'aco_galv': (150, 152, 150), 'ferro_fundido': (70, 70, 72),
    'aluminio': (168, 170, 172), 'aluminio_fundido': (150, 150, 146), 'tinta_motor': (40, 52, 70), 'chassi': (30, 30, 30),
    'borracha': (22, 22, 22), 'pneu': (30, 30, 31), 'plastico_preto': (34, 34, 35), 'plastico_cinza': (98, 100, 102),
    'plastico_prata': (176, 178, 180), 'painel': (48, 48, 50), 'vinil': (52, 50, 48), 'forro_porta': (96, 92, 86),
    'tecido_banco': (104, 92, 78), 'carpete': (46, 44, 42), 'forro_teto': (186, 180, 168), 'chumbo': (110, 112, 116),
    'cobre': (176, 104, 60), 'vermelho_borne': (150, 16, 12), 'bateria_caixa': (40, 40, 42), 'bateria_tampa': (196, 190, 170),
    'radiador_colmeia': (120, 122, 118), 'amarelo_tampa': (210, 160, 20), 'laranja_ferramenta': (196, 80, 20),
    'azul_ferramenta': (30, 70, 150), 'verde_lata': (40, 90, 50), 'refletor': (230, 232, 236), 'fio_preto': (20, 20, 20),
    'fio_vermelho': (140, 16, 12), 'mola_amarela': (180, 150, 40), 'caliper': (90, 92, 96), 'disco_freio': (120, 118, 116),
    'placa': (226, 228, 228), 'madeira_cabo': (150, 102, 62),
}
METAL = {'cromado': (1.0, 0.1), 'aco_escuro': (0.7, 0.5), 'aco_galv': (0.8, 0.45), 'ferro_fundido': (0.6, 0.65), 'aluminio': (0.85, 0.35),
         'aluminio_fundido': (0.7, 0.55), 'tinta_motor': (0.2, 0.5), 'chumbo': (0.6, 0.55), 'cobre': (0.9, 0.35), 'refletor': (1.0, 0.04),
         'radiador_colmeia': (0.6, 0.5), 'plastico_prata': (0.55, 0.35), 'caliper': (0.5, 0.5), 'disco_freio': (0.8, 0.4),
         'placa': (0.5, 0.4)}
FOSCO = {'borracha': 0.9, 'pneu': 0.88, 'chassi': 0.85, 'plastico_preto': 0.62, 'plastico_cinza': 0.55, 'painel': 0.7, 'vinil': 0.55,
         'forro_porta': 0.7, 'bateria_caixa': 0.5, 'bateria_tampa': 0.55, 'fio_preto': 0.5, 'fio_vermelho': 0.5, 'madeira_cabo': 0.6}
TRANSP = {'vidro': ((150, 172, 168), 0.32, 0.04), 'lente_farol': ((236, 240, 240), 0.22, 0.03), 'lente_lanterna': ((150, 10, 8), 0.78, 0.08),
          'lente_pisca': ((210, 110, 10), 0.72, 0.08), 'lente_re': ((236, 236, 236), 0.5, 0.08), 'plastico_translucido': ((226, 224, 210), 0.72, 0.4),
          'espelho_retrovisor': None}
TECIDOS = [('tecido_banco', 'tecido', 0.4, 768), ('carpete', 'tecido', 0.5, 512), ('forro_teto', 'tecido', 0.5, 512)]


def _tex_pintura(seed=3, px=256, tile=2.0):
    """Pintura gasta: casca de laranja fina e, na faixa de baixo da imagem (v < 0,5), a sujeira que sobe da rua (o UV da lataria
    poe a altura do carro nessa faixa). Branca: a cor vem do baseColorFactor. DESGASTE controla a sujeira."""
    n = int(px * tile); d = DESGASTE
    f = GT.fbm(n, n, 0.08 * px, 4, seed); g = GT.noise(n, n, 0.003 * px, 0.003 * px, seed + 1)
    rows = np.linspace(0, 1, n)[:, None]                         # 0 = topo da imagem
    baixo = np.clip((rows - 0.62) / 0.38, 0, 1)                  # sujeira so nos ultimos ~0,55 m de altura do carro
    suj = np.clip(baixo ** 1.8 * (0.55 + 0.45 * f) * (1.1 * d + 0.05), 0, 0.85)
    alb = np.ones((n, n, 3)) * (0.985 - 0.02 * f[..., None])
    alb = GT.lerp(alb, np.ones((1, 1, 3)) * np.array([0.62, 0.56, 0.48]), suj[..., None])
    hm = 0.00002 * g + 0.00003 * f
    rough = 0.30 + 0.04 * f + 0.45 * suj
    return alb, hm, rough, 0.4, 0.05


def _tex_lente(seed, px=1024, tile=0.2, horizontal=False):
    """Lente de farol: frisos (prismas) que espalham a luz."""
    n = int(px * tile); yy, xx = np.mgrid[0:n, 0:n] / px
    a = yy if horizontal else xx
    fr = 0.5 + 0.5 * np.cos(a * 2 * np.pi / 0.008)
    fr2 = 0.5 + 0.5 * np.cos((xx if horizontal else yy) * 2 * np.pi / 0.025)
    hm = 0.0004 * fr + 0.00015 * fr2
    return np.ones((n, n, 3)), hm, np.full((n, n), 0.05), 1.2, 0.0


def _tex_colmeia(seed, px=1024, tile=0.12):
    """Colmeia do radiador: aletas finas verticais e tubos horizontais."""
    n = int(px * tile); yy, xx = np.mgrid[0:n, 0:n] / px
    al = (np.abs(((xx / 0.0025) % 1) - 0.5) < 0.12).astype(float)
    tb = (np.abs(((yy / 0.012) % 1) - 0.5) < 0.18).astype(float)
    hm = 0.0008 * np.maximum(al * 0.6, tb)
    c = GT.rgb(CORES['radiador_colmeia'])[None, None] * (0.45 + 0.55 * np.maximum(al, tb)[..., None])
    return c, hm, 0.5 + 0.2 * (1 - al), 1.5, 0.002


UV = {}          # material -> funcao (v, n) -> uv (padrao: projecao em caixa com o ladrilho)
LADRILHO = {}


def uv_pintura(v, n):
    """Lataria: u ao longo do carro, v = altura na faixa de baixo da textura (sujeira sobe da rua); tetos e capo na faixa de cima."""
    uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1)
    lado = ax != 1
    uv[:, 0] = np.where(ax == 0, v[:, 2], v[:, 0]) / 2.0
    uv[lado, 1] = 0.5 - np.clip(v[lado, 1], 0, 1.5) / 1.5 * 0.5 + 0.0       # y=0 -> 0.5 (fundo da faixa), y=1,5 -> 0
    uv[~lado, 0] = v[~lado, 0] / 2.0
    uv[~lado, 1] = 0.5 + 0.5 * ((v[~lado, 2] / 2.0) % 1.0)
    return uv


def lin(c):
    """Cor sRGB (0-255) -> fator linear do glTF."""
    return [((x / 255) ** 2.2) for x in c]


def materiais():
    gp.materiais()
    gp.CORES.update(CORES)
    for k, c in CORES.items():
        met, rough = METAL.get(k, (0.0, FOSCO.get(k, 0.5)))
        MATS[k] = PBRMaterial(name=k, baseColorFactor=lin(c) + [1.0], metallicFactor=met, roughnessFactor=rough)
    def tex(k, fn, metal=0.0, tile=None, uvf=None, fator=None):
        r = fn(); px = r[-1] if len(r) == 7 else None
        alb, hm, rough, nstr, aod = r[:5]
        p_m = int(alb.shape[0] / (tile or 1.0))
        a, nm, o = tex_set(alb, hm, rough, nstr, aod, p_m)
        TEX[k] = (a, nm, o)
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=fator or [255, 255, 255, 255], metallicFactor=metal, roughnessFactor=1.0)
        if uvf: UV[k] = uvf
        elif tile: LADRILHO[k] = tile
    tex('pintura', lambda: _tex_pintura(), metal=0.25, tile=2.0, uvf=uv_pintura, fator=lin(COR_PINTURA) + [1.0])
    tex('radiador_colmeia', lambda: _tex_colmeia(5), metal=0.5, tile=0.12)
    for i, (k, kind, tile, px) in enumerate(TECIDOS):
        r = gp._ruido_tex(CORES[k], 201 + 7 * i, px, tile, kind)
        a, nm, o = tex_set(*r, px); TEX[k] = (a, nm, o); LADRILHO[k] = tile
        MATS[k] = PBRMaterial(name=k, baseColorTexture=a, normalTexture=nm, occlusionTexture=o, metallicRoughnessTexture=o,
                              baseColorFactor=[255, 255, 255, 255], metallicFactor=0.0, roughnessFactor=1.0)
    for k, val in TRANSP.items():
        if val is None: continue
        c, alpha, rough = val
        MATS[k] = PBRMaterial(name=k, baseColorFactor=lin(c) + [alpha], alphaMode='BLEND',
                              metallicFactor=0.1, roughnessFactor=rough, doubleSided=True)
    for k, hor in (('lente_farol', False), ('lente_lanterna', True), ('lente_pisca', True)):
        r = _tex_lente(7, horizontal=hor); a, nm, o = tex_set(*r, int(1024))
        TEX[k] = (a, nm, None); LADRILHO[k] = 0.2; m = MATS[k]
        MATS[k] = PBRMaterial(name=k, baseColorFactor=m.baseColorFactor, alphaMode='BLEND', normalTexture=nm,
                              metallicFactor=0.1, roughnessFactor=m.roughnessFactor, doubleSided=True)
    MATS['espelho_retrovisor'] = PBRMaterial(name='espelho_retrovisor', baseColorFactor=[0.9, 0.92, 0.94, 1], metallicFactor=1.0, roughnessFactor=0.03)
    MATS['lampada'] = PBRMaterial(name='lampada', baseColorFactor=[1, 0.95, 0.85, 1], emissiveFactor=[0.0, 0.0, 0.0], metallicFactor=0, roughnessFactor=0.2)


def mat_imagem(nome, img, rough=0.45, metal=0.0, alpha=False):
    TEX[nome] = (img, None, None)
    MATS[nome] = PBRMaterial(name=nome, baseColorTexture=img, baseColorFactor=[255, 255, 255, 255], metallicFactor=metal, roughnessFactor=rough,
                             alphaMode='MASK' if alpha else None)


class V(P):
    """Peca de veiculo: UV por material (lataria, ladrilhos proprios) calculada nas coordenadas do carro."""
    def scene(s, name):
        for k in s.parts:
            if k in UV and k not in s.uv: s.uv[k] = UV[k]
            if k in LADRILHO and k not in s.uv: s.uv[k] = gp.uv_caixa(LADRILHO[k])
        return P.scene(s, name)


# ============================================================================ estrutura do modelo
class Veiculo:
    """Carroceria fixa (base) + partes (cada uma vira um no). Uma parte pode ter pai (retrovisor dentro da porta)."""
    def __init__(s):
        s.base = V(); s.partes = []; s.encaixes = []; s.compartimentos = []
    def parte(s, no, origem, tipo, pai=None, **info):
        q = V(); s.partes.append(dict(no=no, origem=list(map(float, origem)), tipo=tipo, pai=pai, geo=q, **info)); return q
    def achar(s, no):
        for p in s.partes:
            if p['no'] == no: return p
    def compartimento(s, id, nome, grade, abre_por=None, **info):
        s.compartimentos.append(dict(id=id, nome=nome, grade=list(grade), abre_por=abre_por, **info))


def _local(piece, T):
    """Copia a peca com as malhas transformadas por T; a UV continua calculada nas coordenadas originais (do carro)."""
    q = V(); q.uv = {}
    Ti = np.linalg.inv(T)
    for k, ms in piece.parts.items():
        for m in ms: mm = m.copy(); mm.apply_transform(T); q.add(k, mm)
    fs = dict(piece.uv)
    for k in piece.parts:
        if k not in fs:
            if k in UV: fs[k] = UV[k]
            elif k in LADRILHO: fs[k] = gp.uv_caixa(LADRILHO[k])
    for k, f in fs.items():
        q.uv[k] = (lambda f, Ti: (lambda v, n: f(trimesh.transform_points(v, Ti), (Ti[:3, :3] @ n.T).T)))(f, Ti)
    return q


def _cena(sc, piece, prefixo, pai):
    for gname, g in piece.scene(prefixo).geometry.items():
        sc.add_geometry(g, node_name=gname, geom_name=gname, parent_node_name=pai)


def exportar_modelo(mod, raiz):
    Vc = Veiculo(); mod['fn'](Vc)
    nome = mod['id']; sc = trimesh.Scene(); base = sc.graph.base_frame
    sc.graph.update(frame_from=base, frame_to=nome, matrix=np.eye(4))
    pos = {nome: np.zeros(3)}
    _cena(sc, Vc.base, nome, nome)
    for pt in Vc.partes:
        pai = pt['pai'] or nome; o = np.array(pt['origem'])
        sc.graph.update(frame_from=pai, frame_to=pt['no'], matrix=TF.translation_matrix(o - pos[pai])); pos[pt['no']] = o
        _cena(sc, _local(pt['geo'], TF.translation_matrix(-o)), f"{nome}_{pt['no']}", pt['no'])
    for e in Vc.encaixes:
        pai = e.get('pai') or nome; o = np.array(e['pos'])
        sc.graph.update(frame_from=pai, frame_to=e['no'], matrix=TF.translation_matrix(o - pos[pai])); pos[e['no']] = o
    os.makedirs(raiz, exist_ok=True)
    arq = os.path.join(raiz, f'{nome}.glb'); sc.export(arq); glb_jpeg(arq)
    b = sc.bounds; tris = sum(len(g.faces) for g in sc.geometry.values())
    reg = {k: v for k, v in mod.items() if k != 'fn'}
    reg.update(arquivo=f'{nome}.glb', tamanho_m=[round(float(x), 3) for x in (b[1] - b[0])], triangulos=int(tris), kb=round(os.path.getsize(arq) / 1024, 1))
    reg['partes'] = []
    for pt in Vc.partes:
        r = {k: v for k, v in pt.items() if k not in ('geo', 'origem', 'pai', 'repouso')}
        r['pai'] = pt['pai'] or nome; r['origem_m'] = [round(c, 4) for c in pt['origem']]
        r['triangulos'] = int(sum(len(m.faces) for ms in pt['geo'].parts.values() for m in ms))
        reg['partes'].append(r)
    reg['encaixes'] = [{k: v for k, v in e.items() if k != 'pos'} | {'posicao_m': [round(float(c), 4) for c in e['pos']]} for e in Vc.encaixes]
    reg['compartimentos'] = Vc.compartimentos
    return reg, Vc


def exportar_peca_solta(Vc, pt, raiz, item):
    """A peca sozinha como item de loot: deitada (repouso = rotacao em graus [x, y, z]) e com pivo no centro da base."""
    o = np.array(pt['origem']); T = TF.translation_matrix(-o)
    rx, ry, rz = pt.get('repouso', (0, 0, 0))
    R = TF.euler_matrix(math.radians(rx), math.radians(ry), math.radians(rz), 'sxyz')
    filhos = [q for q in Vc.partes if q['pai'] == pt['no']]
    pecas = [pt['geo']] + [q['geo'] for q in filhos]
    tmp = [_local(pc, R @ T) for pc in pecas]
    vs = np.vstack([m.vertices for pc in tmp for ms in pc.parts.values() for m in ms])
    lo, hi = vs.min(0), vs.max(0); c = np.array([(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2])
    sc = trimesh.Scene(); F = TF.translation_matrix(-c) @ R @ T
    for i, pc in enumerate(pecas):
        _cena(sc, _local(pc, F), f"{item['id']}_{i}" if i else item['id'], None)
    pasta = os.path.join(raiz, 'pecas'); os.makedirs(pasta, exist_ok=True)
    arq = os.path.join(pasta, f"{item['id']}.glb"); sc.export(arq); glb_jpeg(arq)
    b = sc.bounds
    return dict(item, arquivo=f"pecas/{item['id']}.glb", tamanho_m=[round(float(x), 3) for x in (b[1] - b[0])],
                triangulos=int(sum(len(g.faces) for g in sc.geometry.values())), kb=round(os.path.getsize(arq) / 1024, 1))


# ============================================================================ ferramentas (loot de oficina)
FERRAMENTAS = {}
def ferramenta(id, nome, **dados):
    def deco(fn): FERRAMENTAS[id] = dict(id=id, nome=nome, grupo='loot', categoria='oficina', montagem='floor', fn=fn, **dados); return fn
    return deco


def exportar_ferramenta(it, raiz):
    p = V(); it['fn'](p)
    vs = np.vstack([m.vertices for ms in p.parts.values() for m in ms]); lo, hi = vs.min(0), vs.max(0)
    p = _local(p, TF.translation_matrix([-(lo[0] + hi[0]) / 2, -lo[1], -(lo[2] + hi[2]) / 2]))
    sc = trimesh.Scene(); _cena(sc, p, it['id'], None)
    pasta = os.path.join(raiz, 'ferramentas'); os.makedirs(pasta, exist_ok=True)
    arq = os.path.join(pasta, f"{it['id']}.glb"); sc.export(arq); glb_jpeg(arq)
    b = sc.bounds
    reg = {k: v for k, v in it.items() if k != 'fn'}
    reg.update(arquivo=f"ferramentas/{it['id']}.glb", tamanho_m=[round(float(x), 3) for x in (b[1] - b[0])],
               triangulos=int(sum(len(g.faces) for g in sc.geometry.values())), kb=round(os.path.getsize(arq) / 1024, 1))
    return reg


# ============================================================================ catalogo
MODELOS = {}
def modelo(id, nome, **dados):
    def deco(fn): MODELOS[id] = dict(id=id, nome=nome, fn=fn, **dados); return fn
    return deco


CABECALHO = {
    'escala': '1 unidade = 1 m, Y para cima, frente do carro para +Z, lado esquerdo (motorista) em +X; pivô no chão, no meio dos eixos',
    'design': 'docs/veiculos.md',
    'partes': 'cada parte é um nó do GLB. tipo porta/tampa: gira abre_graus (com sinal) em torno do eixo local, a origem é a dobradiça. '
              'tipo roda: origem no centro do cubo (VehicleWheel3D). tipo peca: origem no ponto de fixação. '
              'peca = id do item de loot que a parte vira ao ser desmontada (null = não sai).',
    'campos_jogo': {'obrigatoria': 'o carro não anda sem ela', 'ferramentas': 'itens necessários para tirar e pôr',
                    'tempo_s': '[tirar, pôr] em segundos', 'depende_de': 'partes que têm de estar abertas ou fora antes',
                    'padrao': 'peças do mesmo padrão servem em outros modelos', 'carga_maos': 'carregada com as duas mãos, não vai na mochila',
                    'celulas': 'tamanho na grade [largura, altura]'},
}


def catalogo_md(cat):
    L = ['# Catálogo de veículos', '', 'Gerado por `props/veiculos/gerar_veiculos.py`. Design completo em [`docs/veiculos.md`](../../docs/veiculos.md). '
         'Medidas em metros (largura × altura × comprimento).', '']
    for m in cat['modelos']:
        L += [f"## {m['nome']} (`{m['id']}`)", '', m.get('descricao', ''), '',
              f"Medidas {' × '.join(f'{x:.2f}' for x in m['tamanho_m'])} m · {m['triangulos']} triângulos · {m['kb'] / 1024:.1f} MB", '',
              '| Nó | Tipo | Vira o item | Precisa para andar | Abre | Ferramentas | Tempo (tirar / pôr) |', '|---|---|---|---|---|---|---|']
        for p in m['partes']:
            ab = f"{p['abre_graus']}° em {p['eixo']}" if p.get('abre_graus') else '-'
            t = ' / '.join(f'{x} s' for x in p['tempo_s']) if p.get('tempo_s') else '-'
            p = dict(p, ferramentas=[f.replace('|', ' ou ') for f in p.get('ferramentas', [])])
            L.append(f"| `{p['no']}` | {p['tipo']} | {('`' + p['peca'] + '`') if p.get('peca') else '-'} | {'sim' if p.get('obrigatoria') else '-'} | {ab} | "
                     f"{', '.join(p.get('ferramentas', [])) or '-'} | {t} |")
        L += ['', '| Compartimento | Grade | Abre por |', '|---|---|---|']
        for c in m['compartimentos']:
            L.append(f"| {c['nome']} (`{c['id']}`) | {c['grade'][0]} × {c['grade'][1]} | {('`' + c['abre_por'] + '`') if c.get('abre_por') else 'sempre aberto'} |")
        L.append('')
    L += ['## Peças (loot)', '', '| Item | Padrão | Peso | Grade | Função | Triângulos |', '|---|---|---|---|---|---|']
    for p in cat['pecas']:
        g = 'carga nas mãos' if p.get('carga_maos') else (f"{p['celulas'][0]} × {p['celulas'][1]}" if p.get('celulas') else '-')
        L.append(f"| {p['nome']} (`{p['id']}`) | {p['padrao']} | {p['peso_kg']} kg | {g} | {p['efeito']} | {p['triangulos']} |")
    L += ['', '## Ferramentas e materiais de oficina (loot)', '', '| Item | Peso | Grade | Para que serve | Aparece em | Triângulos |', '|---|---|---|---|---|---|']
    for p in cat['ferramentas']:
        L.append(f"| {p['nome']} (`{p['id']}`) | {p['peso_kg']} kg | {p['celulas'][0]} × {p['celulas'][1]} | {p['efeito']} | {', '.join(p['onde'])} | {p['triangulos']} |")
    open(os.path.join(AQUI, 'CATALOGO.md'), 'w', encoding='utf-8').write(re.sub(r'(\d)\.(\d)', r'\1,\2', '\n'.join(L)) + '\n')


for _f in sorted(os.listdir(AQUI)):
    if re.match(r'(veiculo\d+_|ferramentas).*\.py$', _f):
        exec(compile(open(os.path.join(AQUI, _f), encoding='utf-8').read(), _f, 'exec'), globals())


def main(ids):
    materiais(); raiz = AQUI
    arq = os.path.join(raiz, 'catalogo.json')
    cat = json.load(open(arq, encoding='utf-8')) if (ids and os.path.exists(arq)) else {'modelos': [], 'pecas': [], 'ferramentas': []}
    feitos = set()   # peça que mais de um modelo usa sai do primeiro (o sedã), para não mudar a cada modelo novo
    for id_, mod in MODELOS.items():
        if ids and id_ not in ids: continue
        reg, Vc = exportar_modelo(mod, raiz)
        print(f"{id_}: {reg['triangulos']} tris {reg['kb']:.0f} KB {reg['tamanho_m']}")
        cat['modelos'] = [m for m in cat['modelos'] if m['id'] != id_] + [reg]
        for pt in Vc.partes:
            it = pt.get('item')
            if not it or it['id'] in feitos: continue
            feitos.add(it['id']); r = exportar_peca_solta(Vc, pt, raiz, it)
            cat['pecas'] = [p for p in cat['pecas'] if p['id'] != it['id']] + [r]
            print(f"  peca {it['id']:22s} {r['triangulos']:7d} tris {r['kb']:7.1f} KB {r['tamanho_m']}")
    if not ids or 'ferramentas' in ids:
        cat['ferramentas'] = []
        for id_, it in FERRAMENTAS.items():
            r = exportar_ferramenta(it, raiz); cat['ferramentas'].append(r)
            print(f"  ferramenta {id_:22s} {r['triangulos']:7d} tris {r['kb']:7.1f} KB {r['tamanho_m']}")
    for m in cat['modelos']:
        for p in m['partes']: p.pop('item', None)
    json.dump(dict(CABECALHO, **cat), open(arq, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    catalogo_md(cat)


if __name__ == '__main__':
    main(sys.argv[1:])
