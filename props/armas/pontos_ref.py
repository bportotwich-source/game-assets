"""Pontos de referencia das maos (e do ombro e do olho) em cada arma e nos acessorios que mudam a pegada.

Cria nos vazios `ref_*` nos GLBs ja gerados e grava a lista em `pontos_ref` no catalogo.json. Os personagens do Recomeco
usam esses nos como alvo de IK (mao direita, mao esquerda, ombro) e como linha do olho na mira.

    python props/armas/pontos_ref.py            # todas as armas e acessorios do catalogo
    python props/armas/pontos_ref.py fuzil_556  # so alguns ids

O gerar_armas.py chama `aplicar_item` depois de exportar cada item, entao regerar uma arma mantem os pontos.
Nao mexe na malha nem nas animacoes: so acrescenta nos ao JSON do GLB (os indices dos nos existentes nao mudam).

Coordenadas da arma: cano para -Z, lado direito +X, Y para cima, origem no centro do punho (dedo medio).
Os pontos ficam presos a peca certa (a mao da recarga anda com o carregador, a mao de apoio anda com a telha da espingarda).
"""
import json, math, os, struct, sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------- descricao de cada ponto (vai para o catalogo)
DESCR = {
    'ref_punho': 'mão que segura o punho: centro da empunhadura na altura do dedo médio; o -Y do nó desce ao longo do punho '
                 '(inclinado para trás pelo ângulo do punho), o -Z aponta para o cano',
    'ref_gatilho': 'ponta do dedo indicador: face da frente do gatilho, onde o dedo apoia antes de puxar',
    'ref_guarda_mao': 'mão de apoio: palma embaixo do guarda-mão (fuzis, espingardas), na telha da espingarda de bomba, '
                      'ou do lado esquerdo do punho nas pistolas (pegada de duas mãos)',
    'ref_coronha': 'ombro: centro da soleira da coronha montada por padrão (a coronha trocada traz o seu próprio ref_coronha)',
    'ref_mira': 'linha do olho na mira aberta: centro da alça, o olho fica atrás dele no eixo -Z (com luneta ou ponto vermelho, '
                'usar o nó `olho` do acessório)',
    'ref_cano': 'boca do cano: origem do tiro e do clarão (o mesmo lugar de boca_fogo)',
    'ref_carregador': 'mão da recarga: onde a mão esquerda pega o carregador (anda com ele na animação de recarga)',
    'ref_corda': 'mão que puxa a corda (arco e besta): ponto de encaixe da flecha na corda',
}

INCLINACAO = {'pistola': 18, 'revolver': 22, 'fuzil': 22, 'submetralhadora': 16, 'espingarda': 24, 'carabina': 26, 'rifle': 28,
              'besta': 20}

# ajustes finos por arma (id -> {ponto: {'d': (dx,dy,dz) somado, 'inclinacao': graus}})
AJUSTE = {}


# ============================================================================ leitura do GLB
def ler_glb(arq):
    data = open(arq, 'rb').read(); off = 12; ch = []
    while off < len(data):
        ln, ty = struct.unpack('<II', data[off:off + 8]); ch.append([ty, data[off + 8:off + 8 + ln]]); off += 8 + ln
    return json.loads(ch[0][1]), ch[1][1] if len(ch) > 1 else b''


def gravar_glb(arq, js, binb):
    binb = bytearray(binb)
    while len(binb) % 4: binb.append(0)
    j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((-len(j)) % 4)
    out = (struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + (8 + len(binb) if binb else 0)) + struct.pack('<II', len(j), 0x4E4F534A) + j
           + (struct.pack('<II', len(binb), 0x004E4942) + bytes(binb) if binb else b''))
    open(arq, 'wb').write(out)


def _acessor(js, binb, i):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); st = bv.get('byteStride', 4 * n)
    raw = np.frombuffer(binb, np.uint8, count=st * (a['count'] - 1) + 4 * n, offset=off)
    return np.lib.stride_tricks.as_strided(raw.view(np.uint8), shape=(a['count'], 4 * n), strides=(st, 1)).copy().view(np.float32).reshape(-1, n)


def _indices(js, binb, i):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
    dt = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32}[a['componentType']]
    return np.frombuffer(binb, dt, count=a['count'], offset=bv.get('byteOffset', 0) + a.get('byteOffset', 0)).astype(np.int64)


def fatia(T, eixo, c):
    """Pontos onde as arestas dos triangulos T cortam o plano coordenada[eixo] = c."""
    out = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        p, q = T[:, a], T[:, b]; da, db = p[:, eixo] - c, q[:, eixo] - c
        m = (da * db < 0); t = (da[m] / (da[m] - db[m]))[:, None]
        out.append(p[m] + t * (q[m] - p[m]))
    return np.concatenate(out)


def _local(n):
    M = np.eye(4)
    if 'matrix' in n: return np.array(n['matrix']).reshape(4, 4).T
    if 'rotation' in n:
        x, y, z, w = n['rotation']
        M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    if 'scale' in n: M[:3, :3] = M[:3, :3] * np.array(n['scale'])
    if 'translation' in n: M[:3, 3] = n['translation']
    return M


class Glb:
    """Nos com posicao no mundo da arma e os vertices de cada peca (filhos com malha)."""
    def __init__(s, arq):
        s.arq = arq; s.js, s.bin = ler_glb(arq); nos = s.js['nodes']
        s.pai = {}
        for i, n in enumerate(nos):
            for c in n.get('children', []): s.pai[c] = i
        s.W = {}
        def mundo(i):
            if i not in s.W: s.W[i] = (mundo(s.pai[i]) if i in s.pai else np.eye(4)) @ _local(nos[i])
            return s.W[i]
        for i in range(len(nos)): mundo(i)
        s.idx = {n.get('name'): i for i, n in enumerate(nos)}
        s.raiz = s.js['scenes'][s.js.get('scene', 0)]['nodes'][0]

    def tem(s, no): return no in s.idx
    def pos(s, no): return s.W[s.idx[no]][:3, 3].copy()
    def nome_pai(s, no): return s.js['nodes'][s.pai[s.idx[no]]]['name']

    def malha(s, no, fundo=False):
        """Triangulos (mundo, n x 3 x 3) das malhas penduradas no no `no` (filhos diretos com malha; fundo=True desce a arvore)."""
        i0 = s.idx[no]; pilha = list(s.js['nodes'][i0].get('children', [])); out = []
        while pilha:
            i = pilha.pop(); n = s.js['nodes'][i]
            if 'mesh' in n:
                for p in s.js['meshes'][n['mesh']]['primitives']:
                    v = _acessor(s.js, s.bin, p['attributes']['POSITION']).astype(float)
                    v = v @ s.W[i][:3, :3].T + s.W[i][:3, 3]
                    f = (_indices(s.js, s.bin, p['indices']) if 'indices' in p else np.arange(len(v))).reshape(-1, 3)
                    out.append(v[f])
            if fundo and 'mesh' not in n: pilha += n.get('children', [])
        return np.concatenate(out) if out else np.zeros((0, 3, 3))

    def verts(s, no, fundo=False): return s.malha(no, fundo).reshape(-1, 3)

    def verts_base(s):
        """Tudo que nao e peca movel (malhas filhas diretas da raiz)."""
        return s.verts(s.js['nodes'][s.raiz]['name'])

    def verts_tudo(s): return s.verts(s.js['nodes'][s.raiz]['name'], fundo=True)
    def malha_tudo(s): return s.malha(s.js['nodes'][s.raiz]['name'], fundo=True)


# ============================================================================ regras
def _faixa(v, eixo, a, b): return v[(v[:, eixo] >= a) & (v[:, eixo] <= b)]


def ponto_gatilho(g):
    v = g.verts('gatilho', fundo=True)
    v = v[np.abs(v[:, 0]) < 0.012]                                 # so a tecla (corta pinos laterais)
    y0, y1 = v[:, 1].min(), v[:, 1].max()
    y = y0 + 0.45 * (y1 - y0) if (y1 - y0) < 0.04 else y0 + 0.012  # meio da tecla (ou perto da ponta se a peca for longa)
    b = _faixa(v, 1, y - 0.003, y + 0.003)
    return np.array([0.0, y, b[:, 2].min()])                       # face da frente (o cano e -Z)


def inclinacao_punho(g, padrao):
    """Angulo do punho medido na malha: reta pelos centros das fatias horizontais do punho, da base ate a origem."""
    T = g.malha_tudo(); y0 = T[:, :, 1].min()
    ys, cs, ls = [], [], []
    for y in np.arange(max(y0 + 0.006, -0.07), -0.004, 0.004):
        f = fatia(T, 1, y); f = f[(np.abs(f[:, 2]) < 0.06) & (np.abs(f[:, 0]) < 0.03)]
        if len(f) < 6: continue
        ys.append(y); cs.append(0.5 * (f[:, 2].min() + f[:, 2].max())); ls.append(f[:, 2].max() - f[:, 2].min())
    if len(ys) < 3: return padrao
    ys, cs, ls = map(np.array, (ys, cs, ls)); ok = ls < 1.4 * np.median(ls)     # tira fatias que pegam guarda-mato ou carregador
    if ok.sum() < 3: return padrao
    k = np.polyfit(ys[ok], cs[ok], 1)[0]                           # dz/dy: base para tras (+Z) quando y desce -> k negativo
    ang = math.degrees(math.atan(-k))
    return round(ang, 1) if 3 <= ang <= 40 else padrao


def soleira(v):
    """Centro da soleira: fatia mais para tras (+Z) da malha."""
    zmax = v[:, 2].max(); f = v[v[:, 2] > zmax - 0.006]
    return np.array([0.0, 0.5 * (f[:, 1].min() + f[:, 1].max()), zmax])


def apoio_pistola(g):
    """Mao de apoio na pegada de duas maos: lado esquerdo do punho, um pouco abaixo do centro."""
    v = _faixa(g.verts_tudo(), 1, -0.03, 0.0); v = v[np.abs(v[:, 2]) < 0.03]
    return np.array([v[:, 0].min(), -0.012, 0.004])


def carregador_baixo(g, no):
    v = g.verts(no, fundo=True); y0 = v[:, 1].min()
    f = _faixa(v, 1, y0, y0 + 0.03)
    return np.array([0.0, y0 + 0.025, 0.5 * (f[:, 2].min() + f[:, 2].max())])


def coronha_padrao(g, reg, cat_ac):
    """Soleira da coronha: acessorio padrao no encaixe_coronha, ou a malha da propria arma."""
    if g.tem('ombro'): return g.pos('ombro'), g.nome_pai('ombro')
    e = next((e for e in reg.get('encaixes', []) if e['no'] == 'encaixe_coronha'), None)
    if e and e.get('padrao'):
        ga = Glb(os.path.join(AQUI, cat_ac[e['padrao']]['arquivo']))
        return g.pos('encaixe_coronha') + soleira(ga.verts_tudo()), g.nome_pai('encaixe_coronha')
    if e: return None, None                                         # sem coronha montada por padrao
    v = g.verts_base()
    return soleira(v), g.js['nodes'][g.raiz]['name']


def pontos_arma(g, reg, cat_ac):
    """Lista de (no, pai, posicao_mundo, inclinacao_graus)."""
    cat = reg['categoria']; raiz = reg['id']; P = []
    def add(no, pai, pos, inc=0.0):
        if pos is None: return
        a = AJUSTE.get(raiz, {}).get(no, {})
        pos = np.array(pos, float) + np.array(a.get('d', (0, 0, 0)), float)
        P.append((no, pai, pos, a.get('inclinacao', inc)))
    def copia(no_ref, no_orig):
        if g.tem(no_orig): add(no_ref, g.nome_pai(no_orig), g.pos(no_orig))

    if cat in ('pistola', 'revolver', 'fuzil', 'submetralhadora', 'espingarda', 'carabina', 'rifle'):
        add('ref_punho', raiz, (0, 0, 0), inclinacao_punho(g, INCLINACAO[cat]))
        add('ref_gatilho', 'gatilho', ponto_gatilho(g))
        if cat in ('pistola', 'revolver'):
            add('ref_guarda_mao', raiz, apoio_pistola(g))
        elif g.tem('telha'):                                         # espingarda de bomba: a mao anda com a telha
            v = g.verts('telha', fundo=True); v = v[v[:, 1] < v[:, 1].min() + 0.01]       # so a parte de baixo da telha
            add('ref_guarda_mao', 'telha', (0.0, v[:, 1].min(), 0.5 * (v[:, 2].min() + v[:, 2].max())))
        elif g.tem('encaixe_empunhadura'):
            add('ref_guarda_mao', g.nome_pai('encaixe_empunhadura'), g.pos('encaixe_empunhadura'))
        if cat not in ('pistola', 'revolver'):
            pos, pai = coronha_padrao(g, reg, cat_ac); add('ref_coronha', pai, pos)
        copia('ref_mira', 'mira_ferro') if g.tem('mira_ferro') else copia('ref_mira', 'encaixe_mira')
        copia('ref_cano', 'boca_fogo')
        if g.tem('carregador'): add('ref_carregador', 'carregador', carregador_baixo(g, 'carregador'))
        elif g.tem('tambor'): add('ref_carregador', 'tambor', g.pos('tambor'))
        elif g.tem('entrada_cartucho'): copia('ref_carregador', 'entrada_cartucho')
        elif g.tem('cartucho'): add('ref_carregador', 'cartucho', g.pos('cartucho'))
    elif cat == 'besta':
        add('ref_punho', raiz, (0, 0, 0), inclinacao_punho(g, INCLINACAO[cat]))
        add('ref_gatilho', 'gatilho', ponto_gatilho(g))
        copia('ref_guarda_mao', 'encaixe_trilho')
        add('ref_coronha', raiz, soleira(g.verts_base()))
        copia('ref_mira', 'mira_ferro'); copia('ref_cano', 'boca_fogo')
        add('ref_carregador', 'virote', g.pos('virote'))
    elif cat == 'arco':                                              # o arco fica na mao esquerda, a direita puxa a corda
        add('ref_punho', raiz, (0, 0, 0))
        no = 'encaixe_soltador' if g.tem('encaixe_soltador') else 'encaixe_flecha'
        copia('ref_corda', no); copia('ref_mira', 'mira_ferro'); copia('ref_cano', 'boca_fogo')
    elif cat == 'lanca':
        add('ref_punho', raiz, g.pos('cabo_tras') if g.tem('cabo_tras') else (0, 0, 0))
        copia('ref_guarda_mao', 'mao_frente')
    elif cat == 'bastao':
        add('ref_punho', raiz, (0, 0, 0)); copia('ref_guarda_mao', 'mao_cima')
    else:                                                            # facas, machadinha, arremessaveis
        add('ref_punho', raiz, (0, 0, 0))
    return P


def pontos_acessorio(g, reg):
    raiz = reg['id']
    if reg['categoria'] == 'coronha':
        return [('ref_coronha', raiz, soleira(g.verts_tudo()), 0.0)]
    if reg['categoria'] == 'empunhadura' and reg['encaixe'] == 'mlok_baixo':
        v = g.verts_tudo(); y0, y1 = v[:, 1].min(), v[:, 1].max()
        if y1 - y0 > 0.06:                                           # empunhadura vertical: a mao fecha no meio dela
            f = _faixa(v, 1, 0.5 * (y0 + y1) - 0.004, 0.5 * (y0 + y1) + 0.004)
            return [('ref_guarda_mao', raiz, np.array([0.0, 0.5 * (y0 + y1), 0.5 * (f[:, 2].min() + f[:, 2].max())]), 0.0)]
        return [('ref_guarda_mao', raiz, np.array([0.0, y0, 0.5 * (v[:, 2].min() + v[:, 2].max())]), 0.0)]  # batente/curta: palma embaixo
    return []


# ============================================================================ escrita
def _quat_x(graus):
    h = math.radians(-graus) / 2                                   # inclinacao positiva = base do punho para tras (+Z)
    return [math.sin(h), 0.0, 0.0, math.cos(h)]


def injetar(g, pontos):
    js = g.js; nos = js['nodes']
    velhos = {i for i, n in enumerate(nos) if str(n.get('name', '')).startswith('ref_')}
    if velhos:                                                     # refazer: tira os ref_ antigos (sempre os ultimos nos)
        assert min(velhos) == len(nos) - len(velhos), 'ref_ fora do fim da lista de nos'
        for n in nos:
            if 'children' in n:
                n['children'] = [c for c in n['children'] if c not in velhos]
                if not n['children']: n.pop('children')
        del nos[min(velhos):]
        g = Glb.__new__(Glb); g.__dict__.update(_recarregar(js))
    saida = []
    for no, pai, pw, inc in pontos:
        ip = g.idx[pai]; loc = pw - g.W[ip][:3, 3]
        n = {'name': no, 'translation': [round(float(c), 5) for c in loc]}
        if inc: n['rotation'] = [round(c, 6) for c in _quat_x(inc)]
        nos.append(n); nos[ip].setdefault('children', []).append(len(nos) - 1)
        r = {'no': no, 'pai': pai, 'posicao_m': [round(float(c), 4) for c in pw]}
        if inc: r['inclinacao_graus'] = inc
        r['descricao'] = DESCR[no]; saida.append(r)
    return saida


def _recarregar(js):
    g = Glb.__new__(Glb); g.js = js; nos = js['nodes']; g.pai = {}
    for i, n in enumerate(nos):
        for c in n.get('children', []): g.pai[c] = i
    g.W = {}
    def mundo(i):
        if i not in g.W: g.W[i] = (mundo(g.pai[i]) if i in g.pai else np.eye(4)) @ _local(nos[i])
        return g.W[i]
    for i in range(len(nos)): mundo(i)
    g.idx = {n.get('name'): i for i, n in enumerate(nos)}; g.raiz = js['scenes'][js.get('scene', 0)]['nodes'][0]
    return g.__dict__


def aplicar_item(reg, grupo, cat_ac):
    arq = os.path.join(AQUI, reg['arquivo']); g = Glb(arq)
    pts = pontos_arma(g, reg, cat_ac) if grupo == 'armas' else pontos_acessorio(g, reg) if grupo == 'acessorios' else []
    if not pts and not any(str(n.get('name', '')).startswith('ref_') for n in g.js['nodes']): return None
    saida = injetar(g, pts); gravar_glb(arq, g.js, g.bin)
    if saida: reg['pontos_ref'] = saida
    else: reg.pop('pontos_ref', None)
    return saida


def main(ids):
    arq = os.path.join(AQUI, 'catalogo.json'); cat = json.load(open(arq, encoding='utf-8'))
    cat_ac = {r['id']: r for r in cat['acessorios']}
    for grupo in ('armas', 'acessorios'):
        for r in cat[grupo]:
            if ids and r['id'] not in ids: continue
            s = aplicar_item(r, grupo, cat_ac)
            if s: print(f"{r['id']:28s} " + '  '.join(f"{p['no'][4:]}{'∠' + str(p['inclinacao_graus']) if 'inclinacao_graus' in p else ''}" for p in s))
    cat['pontos_ref'] = {k: v for k, v in DESCR.items()}
    json.dump(cat, open(arq, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main(sys.argv[1:])
