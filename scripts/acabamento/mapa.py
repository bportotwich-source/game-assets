"""Acabamento por comodo: escolhe papel de parede, azulejo, lambri e piso de cada comodo e grava
kits/<kit>/acabamento.json, que o Godot usa para pintar as paredes e pisos do kit sem mexer nas pecas.

Como funciona
  - Os comodos e seus tipos vem de scripts/ambientacao (comodos.py e o ambientacao.json do kit).
  - Para cada andar, uma grade de 0,25 m diz o estilo de parede e de piso de cada celula. As celulas de parede e
    de porta recebem o comodo mais perto (ate 0,5 m), para a face da parede achar o comodo para onde ela olha.
  - O shader acabamento.gdshader troca so os materiais listados em 'materiais' (paredes lisas e pisos genericos):
    na parede, le a celula 0,2 m na frente da face; no piso, a celula embaixo. Fora dos comodos, fica o material original.
  - Os estilos (camadas, altura do lambri/azulejo, cores) estao em ESTILOS e vao para acabamentos/estilos.json.
  - Mapa fino ('fino' no json, celula de 0,0625 m, comprimido): a grade de 0,25 m e maior que a parede interna (12 cm) e
    nao fica alinhada com ela, entao as celulas que pegam parede erravam o lado (faixa do papel do vizinho nos cantos e ao
    lado das portas, piso entrando pela soleira, retalhos na caixa de escada). No mapa fino cada celula livre recebe o
    comodo de onde se chega nela sem atravessar parede; nos vaos entre dois comodos a parede fica sem acabamento (batente)
    e o piso troca no meio do vao; caixa de escada e vazios fechados ficam com pintura lisa propria. O campo 'mapa' antigo continua no arquivo para quem ainda nao le o fino.

Uso: python3 scripts/acabamento/mapa.py [kit ...]     (sem argumentos: todos os kits)
"""
import base64, gzip, json, math, os, sys
from collections import deque
import numpy as np, trimesh
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'scripts', 'ambientacao'))
import comodos as CM

CAMADAS = json.load(open(os.path.join(RAIZ, 'acabamentos', 'camadas.json')))['camadas']
L = {n: i for i, n in enumerate(CAMADAS)}

# Estilo de parede: camada de baixo ate 'altura' (m acima do piso), camada de cima, cores (multiplicam a textura),
# e se tem rodape pintado (faixa de 12 cm) e sanca (faixa sombreada no alto).
def P(cima, cor_cima=(1, 1, 1), baixo=None, altura=0.0, cor_baixo=(1, 1, 1), rodape=True, sanca=True):
    return dict(cima=L[cima], cor_cima=list(cor_cima), baixo=L[baixo or cima], altura=altura, cor_baixo=list(cor_baixo), rodape=rodape, sanca=sanca)

TINTA = {'branco': (0.97, 0.96, 0.93), 'creme': (0.98, 0.93, 0.80), 'salvia': (0.78, 0.86, 0.76), 'azul': (0.76, 0.84, 0.92), 'rosa': (0.98, 0.84, 0.82),
         'amarelo': (1.0, 0.92, 0.70), 'cinza': (0.85, 0.86, 0.86), 'verde': (0.70, 0.82, 0.70), 'bege': (0.92, 0.86, 0.76), 'pessego': (1.0, 0.86, 0.74)}
PAREDES = [
    P('pintura', TINTA['branco']),                                                     # 0 neutro
    P('papel_listrado', baixo='lambri_madeira', altura=0.9),                           # 1 sala antiga
    P('papel_damasco', baixo='lambri_madeira', altura=0.9),                            # 2 sala / jantar
    P('papel_floral'),                                                                 # 3 quarto
    P('pintura', TINTA['azul']),                                                       # 4 quarto
    P('papel_infantil', baixo='lambri_tabuado', altura=0.9, cor_baixo=TINTA['branco']), # 5 quarto de crianca
    P('pintura', TINTA['amarelo'], baixo='azulejo_branco', altura=1.5),                # 6 cozinha
    P('pintura', TINTA['salvia'], baixo='azulejo_metro', altura=1.5),                  # 7 cozinha
    P('pintura', TINTA['branco'], baixo='azulejo_verde', altura=2.0, sanca=False),     # 8 banheiro
    P('pintura', TINTA['branco'], baixo='azulejo_branco', altura=2.0, sanca=False),    # 9 banheiro
    P('pintura', TINTA['creme'], baixo='lambri_tabuado', altura=1.0),                  # 10 corredor / lavanderia
    P('papel_losango'),                                                                # 11 escritorio / sala
    P('pintura', TINTA['pessego']),                                                    # 12 sala
    P('pintura', TINTA['verde'], baixo='pintura', altura=1.2, cor_baixo=(0.52, 0.66, 0.56), sanca=False),   # 13 reparticao (meia parede verde)
    P('pintura', TINTA['creme'], baixo='pintura', altura=1.2, cor_baixo=(0.62, 0.52, 0.42), sanca=False),   # 14 comercio (meia parede marrom)
    P('pintura', TINTA['branco'], baixo='azulejo_branco', altura=1.6, sanca=False),    # 15 clinica / cozinha comercial
    P('pintura', TINTA['cinza'], rodape=False, sanca=False),                           # 16 deposito, garagem
    P('pintura', TINTA['rosa']),                                                       # 17 quarto
    P('pintura', TINTA['bege'], baixo='lambri_madeira', altura=1.0),                   # 18 escritorio formal
    P('pintura', TINTA['branco'], rodape=False, sanca=False),                          # 19 caixa de escada e vazios fechados (mapa fino)
]
NEUTRO = 19
PISOS = [dict(camada=L[n], cor=list(c)) for n, c in [
    ('tabua_corrida', (1, 1, 1)),            # 0
    ('taco', (1, 1, 1)),                     # 1
    ('ceramica_bege', (1, 1, 1)),            # 2
    ('ladrilho_xadrez', (1, 1, 1)),          # 3
    ('vinilico', (1, 1, 1)),                 # 4
    ('cimento_queimado', (1, 1, 1)),         # 5
    ('tabua_corrida', (0.72, 0.62, 0.55)),   # 6 tabua escura
]]

# tipo do comodo -> (estilos de parede possiveis, estilos de piso possiveis); a escolha e fixa por comodo (hash)
POR_TIPO = {
    'sala': ([1, 2, 11, 12], [0, 1]), 'jantar': ([2, 1, 12], [1, 0]), 'quarto': ([3, 4, 17], [0, 1, 6]), 'quarto_crianca': ([5], [0, 1]),
    'quarto_solteiro': ([4, 17, 3], [0, 6]), 'cozinha': ([6, 7], [3, 2]), 'banheiro': ([8, 9], [3, 2]), 'lavabo': ([9, 8], [3]),
    'lavanderia': ([10], [2]), 'corredor': ([10, 0], [0, 1]), 'escritorio': ([18, 11, 13], [1, 4]), 'deposito': ([16], [5]), 'garagem': ([16], [5]),
    'sotao': ([0], [6]), 'quarto_hotel': ([2, 3, 11], [0]), 'corredor_hotel': ([18, 10], [0]), 'recepcao': ([18, 14], [4, 3]),
    'clinica': ([15], [4]), 'espera': ([13, 15], [4]), 'cozinha_comercial': ([15], [2]), 'refeitorio': ([14, 15], [4]), 'alojamento': ([13], [4]),
    'vestiario': ([15], [4]), 'delegacia': ([13], [4]), 'cela': ([16], [5]), 'banco': ([18], [4]), 'cofre': ([16], [5]), 'loja': ([14], [4]),
    'mercado': ([14], [4]), 'padaria_loja': ([14, 15], [3, 4]), 'padaria_producao': ([15], [2]), 'diner': ([15, 14], [3]), 'posto_loja': ([14], [4]),
    'oficina': ([16], [5]), 'showroom': ([0], [4]), 'biblioteca': ([18], [0, 1]), 'sala_aula': ([13], [0]), 'correios': ([13], [4]), 'triagem': ([16], [5]),
    'quartel': ([13, 16], [5]), 'igreja': ([0], [0]), 'cinema_foyer': ([2, 18], [4]), 'cinema_sala': ([0], [5]), 'projecao': ([16], [5]),
    'galeria': ([14, 0], [4]), 'saguao_estacao': ([18, 14], [3, 4]), 'caixa_dagua': ([16], [5]), 'casa_barcos': ([10], [6]), 'concha': ([0], [5]),
    'palco_bastidores': ([16], [5]), 'celeiro': ([16], [5]), 'ferro_velho': ([16], [5]), 'observatorio': ([18], [1]), 'skate': ([16], [5]),
    'galpao': ([16], [5]), 'fabrica': ([16], [5]), 'serraria': ([16], [5]), 'arquivo': ([13], [4]), 'trailer': ([12, 4], [4]),
}
FORA = {'vazio', 'patio', 'quintal', 'varanda', 'estacionamento'}

PAREDE_PADRAO = ['plaster']          # so paredes lisas; materiais de parede ja coloridos ficam como estao
PISO_PADRAO = ['floor']              # so o piso generico; os kits novos ja tem piso por comodo


def h(*k):
    v = 2166136261
    for x in k:
        for ch in str(x): v = ((v ^ ord(ch)) * 16777619) & 0xffffffff
    return v


SUB = 4                               # o mapa fino divide cada celula em SUB x SUB
ALCANCE = 0.3                         # ate onde um comodo avanca por celulas livres sem dono (m)
VAO = 2.2                             # maior vao (m) tratado como passagem entre comodos


def mapa_fino(res, an, estilo):
    """Rotulo de comodo por celula fina de um andar e a imagem RGBA (mesma convencao do mapa de 0,25 m).
    estilo: id do comodo -> (parede + 1, piso + 1, pe-direito / 0,02) ou None para comodo sem acabamento."""
    nx, nz = res['nx'] * SUB, res['nz'] * SUB; f = CM.CEL / SUB; x0, z0 = res['x0'], res['z0']; y = an['y']
    solido = np.zeros((nx, nz), bool)
    for h in (0.3, 0.5, 1.0, 1.6, 2.0):
        sec = res['malha'].section(plane_origin=[0, y + h, 0], plane_normal=[0, 1, 0])
        if sec is None: continue
        for ent in sec.entities:
            pts = sec.vertices[ent.points]
            for a, b in zip(pts[:-1], pts[1:]):
                n = max(2, int(np.linalg.norm(b - a) / (f * 0.4)) + 1); t = np.linspace(0, 1, n)[:, None]
                p = a + (b - a) * t; ix = ((p[:, 0] - x0) / f).astype(int); iz = ((p[:, 2] - z0) / f).astype(int)
                ok = (ix >= 0) & (iz >= 0) & (ix < nx) & (iz < nz); solido[ix[ok], iz[ok]] = True
    # vao: celulas livres na linha de uma parede (porta, passagem). Fecha o solido ao longo de x e de z e fica so com
    # o que e fino no outro sentido (um corredor estreito tambem fecha, mas e comprido e sai aqui)
    L = np.ones((int(VAO / f), 1), bool); fino = np.ones((1, int(0.45 / f)), bool)
    def garganta(m, L, fino):
        g = ndimage.binary_closing(np.pad(m, 40), structure=L)[40:-40, 40:-40] & ~m
        return g & ~ndimage.binary_opening(g, structure=fino)
    vao = garganta(solido, L, fino) | garganta(solido, L.T, fino.T)
    rot = np.repeat(np.repeat(an['rotulo'], SUB, 0), SUB, 1)
    rot = np.where(solido | vao, -1, rot)
    # 1) cada comodo avanca pelas celulas livres sem dono (frestas junto das paredes), sem atravessar parede nem vao
    dist = np.where(rot >= 0, 0, 10 ** 6); fila = deque(zip(*np.nonzero(rot >= 0))); lim = int(ALCANCE / f)
    viz = ((1, 0), (-1, 0), (0, 1), (0, -1))
    while fila:
        a, b = fila.popleft(); d = dist[a, b] + 1
        if d > lim: continue
        for da, db in viz:
            u, v = a + da, b + db
            if 0 <= u < nx and 0 <= v < nz and not solido[u, v] and not vao[u, v] and dist[u, v] > d:
                dist[u, v] = d; rot[u, v] = rot[a, b]; fila.append((u, v))
    # 2) vazios fechados que sobram (caixa de escada, vao sobre a escada, armario pequeno): acabamento neutro proprio,
    #    em vez de retalhos dos comodos em volta
    resto = (rot < 0) & ~solido & ~vao
    comp, n = ndimage.label(resto)
    neutro = np.zeros((nx, nz), bool)
    for k in range(1, n + 1):
        m = comp == k
        if m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any(): continue        # aberto para fora
        if m.sum() * f * f < 0.3: continue
        neutro |= m
    # paredes e vaos: comodo livre mais perto (para o piso trocar no meio do vao e para quem amostra dentro de um movel fixo)
    sem = (rot < 0) & ~neutro
    d, (ii, jj) = ndimage.distance_transform_edt(sem, return_indices=True)
    cheio = np.where(sem & (solido | vao) & (d <= SUB + 0.01) & ~neutro[ii, jj], rot[ii, jj], rot)
    img = np.zeros((nz, nx, 4), np.uint8)
    for cid, e in estilo.items():
        if e is None: continue
        m = cheio == cid
        img[m.T] = [e[0], e[1], e[2], 255]
    img[..., 0][vao.T] = 0                                   # batente e ombreira ficam como a peca veio
    img[neutro.T] = [NEUTRO + 1, 0, 0, 255]
    return cheio, img


def gerar(kit, cfg):
    pasta = os.path.join(RAIZ, 'kits', kit)
    amb = json.load(open(os.path.join(pasta, 'ambientacao.json'), encoding='utf-8'))
    tipo = {(c['andar'], c['comodo']): c['tipo'] for c in amb['comodos']}
    res = CM.analisar(pasta)
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(res['malha'])
    nx, nz = res['nx'], res['nz']; n_and = len(res['andares'])
    img = np.zeros((n_and, nz, nx, 4), np.uint8)
    resumo = []; finos = []
    # pegada das escadas: comodo pequeno com escada dentro e patamar, nao banheiro nem deposito
    escadas = [m.bounds for n, m in CM.carregar_kit(pasta)[1] if any(t in n.lower() for t in ('stair', 'escada')) and 'slab' not in n and 'rail' not in n and 'guard' not in n]
    for an in res['andares']:
        a = an['andar']; rot = an['rotulo'].copy()
        # celulas de parede/porta herdam o comodo mais perto (ate 2 celulas)
        vazio = rot < 0
        d, (ii, jj) = ndimage.distance_transform_edt(vazio, return_indices=True)
        cheio = np.where(vazio & (d <= 2.01), rot[ii, jj], rot)
        est = {c['id']: None for c in an['comodos']}
        for c in an['comodos']:
            t = tipo.get((a, c['id']), 'vazio')
            if t in ('banheiro', 'lavabo', 'deposito', 'vazio') and c['area'] <= 16:
                m = an['rotulo'] == c['id']; ix, iz = np.nonzero(m); px, pz = res['xs'][ix], res['zs'][iz]
                for b in escadas:
                    if b[0][1] < an['y'] + 2.0 and b[1][1] > an['y'] + 0.3 and ((px > b[0][0]) & (px < b[1][0]) & (pz > b[0][2]) & (pz < b[1][2])).sum() >= 4:
                        t = 'corredor'; break
            if t in FORA or t not in POR_TIPO: continue
            ps, fs = POR_TIPO[t]
            sp = ps[h(kit, a, c['id'], 'p') % len(ps)]; sf = fs[h(kit, a, c['id'], 'f') % len(fs)]
            # pe-direito: mediana do primeiro obstaculo acima de 2,1 m em ate 40 celulas do comodo
            # (um raio so, no centro, pegava luminaria, dossel de cama ou movel embutido)
            ii, jj = np.nonzero(rot == c['id'])
            if len(ii) > 40:
                sel = np.linspace(0, len(ii) - 1, 40).astype(int); ii, jj = ii[sel], jj[sel]
            org = np.stack([res['xs'][ii], np.full(len(ii), an['y'] + 1.2), res['zs'][jj]], 1)
            loc, idx, _ = ray.intersects_location(org, np.tile([0, 1.0, 0], (len(org), 1)), multiple_hits=True)
            prim = np.full(len(org), np.inf)
            ok = loc[:, 1] > an['y'] + 2.1 if len(loc) else np.zeros(0, bool)
            if ok.any(): np.minimum.at(prim, idx[ok], loc[ok, 1])
            prim = prim[np.isfinite(prim)]
            teto = (float(np.median(prim)) if len(prim) else an['teto'] - 0.2) - an['y']
            m = cheio == c['id']
            est[c['id']] = (sp + 1, sf + 1, int(round(teto / 0.02)) if teto <= 5.0 else 0)
            img[a][m.T] = [est[c['id']][0], est[c['id']][1], est[c['id']][2], 255]
            resumo.append(dict(andar=a, comodo=c['id'], tipo=t, parede=sp, piso=sf, pe_direito=round(float(teto), 2)))
        finos.append(mapa_fino(res, an, est)[1])
    out = dict(kit=kit, gerado_por='scripts/acabamento/mapa.py',
               convencao="mapa: RGBA8 em base64, andar por andar, linha z, coluna x; R = estilo de parede + 1, G = estilo de piso + 1, "
                         "B = pé-direito / 0,02 m (0 = mais de 5 m: sem sanca), A = 255 dentro de um cômodo. Célula (ix, iz) cobre x0 + ix*cel e z0 + iz*cel.",
               x0=round(float(res['x0']), 4), z0=round(float(res['z0']), 4), cel=CM.CEL, nx=nx, nz=nz, niveis=[round(float(an['y']), 3) for an in res['andares']],
               materiais=dict(paredes=cfg.get('paredes', PAREDE_PADRAO), pisos=cfg.get('pisos', PISO_PADRAO)),
               comodos=resumo, mapa=base64.b64encode(img.tobytes()).decode(),
               fino=dict(convencao="mesmo desenho do 'mapa', com célula menor; RGBA8 comprimido com gzip e depois base64",
                         cel=CM.CEL / SUB, nx=nx * SUB, nz=nz * SUB, mapa_gz=base64.b64encode(gzip.compress(np.stack(finos).tobytes(), 9, mtime=0)).decode()))
    json.dump(out, open(os.path.join(pasta, 'acabamento.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(f"{kit}: {len(resumo)} cômodos com acabamento, {n_and} andares", flush=True)


def estilos():
    json.dump(dict(gerado_por='scripts/acabamento/mapa.py', camadas=CAMADAS, paredes=PAREDES, pisos=PISOS),
              open(os.path.join(RAIZ, 'acabamentos', 'estilos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def main(kits):
    estilos()
    cfgs = json.load(open(os.path.join(AQUI, 'kits.json'), encoding='utf-8')) if os.path.exists(os.path.join(AQUI, 'kits.json')) else {}
    todos = sorted(k for k in os.listdir(os.path.join(RAIZ, 'kits')) if os.path.exists(os.path.join(RAIZ, 'kits', k, 'ambientacao.json')))
    for k in kits or todos:
        gerar(k, cfgs.get(k, {}))


if __name__ == '__main__':
    main(sys.argv[1:])
