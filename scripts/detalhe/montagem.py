"""Correcoes de montagem que valem para qualquer kit, aplicadas direto nos GLB das pecas.

1. Teto sem sulcos (fechar_laje). O corpo da laje e recuado 2 cm de cada lado para nao piscar com as paredes, entao
   de dentro do comodo aparecia um sulco de 4 cm no teto a cada modulo. Aqui a face de baixo do corpo ganha uma aba
   ate a borda do piso de cima. A aba fica no mesmo plano da face de baixo, lado a lado com a do vizinho (sem
   sobrepor), e por cima das paredes ela fica escondida.

2. Batente sob a folha da janela (batente_folha). Entre o peitoril e a travessa de baixo da folha (guilhotina ou de abrir)
   sobrava uma fresta de 1 a 2 cm por onde se via a rua. Aqui entra uma ripa fina encostada na folha, cobrindo a fresta: por dentro na guilhotina,
   por fora na folha de abrir (que gira para dentro). O no 'folha' nao muda, a janela continua abrindo.

3. Folha de porta na altura do vao (esticar_folha). Estica a folha em Y ate a altura pedida.

Rodar de novo nao muda nada. Uso:
    python3 scripts/detalhe/montagem.py kits/padaria kits/delegacia ...
    python3 scripts/detalhe/montagem.py --porta kits/casas-vitorianas/pieces/door_leaf_back.glb 2.275
"""
import os, sys, glob, json
import numpy as np, trimesh
from trimesh.visual import TextureVisuals

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MARCA_LAJE, MARCA_BAT = 'aba_teto', 'batente_folha'


def _salvar(sc, path):
    sc.export(path, include_normals=True)
    from detalhe import glb_jpeg
    glb_jpeg(path)


def _raiz(sc):
    """Geometrias sem transformacao (fora dos nos 'folha'): nome do no -> (geometria, malha)."""
    out = {}
    for n in sc.graph.nodes_geometry:
        T, g = sc.graph[n]
        if np.allclose(T, np.eye(4)): out[n] = (g, sc.geometry[g])
    return out


def _juntar(m, v, f, uv):
    """Devolve a malha m com os triangulos (v, f) a mais, mantendo material e UV."""
    nm = trimesh.Trimesh(np.vstack([m.vertices, v]), np.vstack([m.faces, f + len(m.vertices)]), process=False)
    muv = getattr(m.visual, 'uv', None)
    nm.visual = TextureVisuals(uv=None if muv is None else np.vstack([muv, uv]), material=m.visual.material)
    nm.metadata.update(m.metadata)
    return nm


def _quad_baixo(x0, x1, z0, z1, y):
    """Retangulo horizontal virado para baixo."""
    v = np.array([[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]], float)
    return v, np.array([[0, 1, 2], [0, 2, 3]]), v[:, [0, 2]] / 2


def _caixa(x0, x1, y0, y1, z0, z1):
    return trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0],
                                transform=trimesh.transformations.translation_matrix([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]))


def fechar_laje(path):
    sc = trimesh.load(path, force='scene', process=False)
    raiz = _raiz(sc); feito = 0
    for n, (g, m) in raiz.items():
        caixa = len(np.unique(np.round(m.vertices, 4), axis=0)) == 8 and len(m.faces) == 12
        if not caixa and m.visual.material.name != 'plaster': continue                                   # corpo da laje
        b = m.bounds; alt = b[1][1] - b[0][1]
        if alt < 0.05 or alt > 0.3 or min(b[1][0] - b[0][0], b[1][2] - b[0][2]) < 1.0: continue          # so lajes
        if sc.bounds[1][1] - sc.bounds[0][1] > 0.4: continue                                              # peca chata
        # piso de cima: as geometrias apoiadas no topo do corpo (piso, rejunte...), com a planta maior
        capa = None
        for n2, (g2, m2) in raiz.items():
            if n2 == n: continue
            c = m2.bounds
            if abs(c[0][1] - b[1][1]) < 0.005 and c[0][0] <= b[0][0] + 1e-3 and c[1][0] >= b[1][0] - 1e-3 and c[0][2] <= b[0][2] + 1e-3 and c[1][2] >= b[1][2] - 1e-3:
                capa = c if capa is None else np.array([np.minimum(capa[0], c[0]), np.maximum(capa[1], c[1])])
        if capa is None: continue
        ex = [b[0][0] - capa[0][0], capa[1][0] - b[1][0]]; ez = [b[0][2] - capa[0][2], capa[1][2] - b[1][2]]
        ok = lambda d: 0.004 < d < 0.06
        xs = [capa[0][0] if ok(ex[0]) else b[0][0], b[0][0], b[1][0], capa[1][0] if ok(ex[1]) else b[1][0]]
        zs = [capa[0][2] if ok(ez[0]) else b[0][2], b[0][2], b[1][2], capa[1][2] if ok(ez[1]) else b[1][2]]
        y = b[0][1]; V, F, U = [], [], []; base = 0
        if caixa:
            trechos = {0: [(b[0][2], b[1][2])], 1: [(b[0][2], b[1][2])], 2: [(b[0][0], b[1][0])], 3: [(b[0][0], b[1][0])]}
        else:
            # corpo recortado (laje do nucleo de escada): so os trechos da borda de baixo que estao no contorno
            fb = m.faces[(m.face_normals[:, 1] < -0.99) & (np.abs(m.triangles[:, :, 1].mean(1) - y) < 1e-4)]
            if not len(fb): continue
            e = np.sort(np.vstack([fb[:, [0, 1]], fb[:, [1, 2]], fb[:, [2, 0]]]), axis=1)
            vr = np.round(m.vertices, 4); _, inv = np.unique(vr, axis=0, return_inverse=True); e = np.sort(inv.reshape(-1)[e], axis=1)
            ue, cnt = np.unique(e, axis=0, return_counts=True); uv_ = np.unique(vr, axis=0)
            borda = uv_[ue[cnt == 1]]                                    # (n, 2, 3)
            trechos = {0: [], 1: [], 2: [], 3: []}
            for p0, p1 in borda:
                if abs(p0[0] - b[0][0]) < 1e-3 and abs(p1[0] - b[0][0]) < 1e-3: trechos[0].append(tuple(sorted((p0[2], p1[2]))))
                if abs(p0[0] - b[1][0]) < 1e-3 and abs(p1[0] - b[1][0]) < 1e-3: trechos[1].append(tuple(sorted((p0[2], p1[2]))))
                if abs(p0[2] - b[0][2]) < 1e-3 and abs(p1[2] - b[0][2]) < 1e-3: trechos[2].append(tuple(sorted((p0[0], p1[0]))))
                if abs(p0[2] - b[1][2]) < 1e-3 and abs(p1[2] - b[1][2]) < 1e-3: trechos[3].append(tuple(sorted((p0[0], p1[0]))))
        def _add(x0, x1, z0, z1):
            nonlocal base
            if x1 - x0 < 1e-4 or z1 - z0 < 1e-4: return
            v, f, u = _quad_baixo(x0, x1, z0, z1, y); V.append(v); F.append(f + base); U.append(u); base += 4
        toca = lambda lado, c: any(abs(t[0] - c) < 1e-3 or abs(t[1] - c) < 1e-3 for t in trechos[lado])
        for t0, t1 in trechos[0]: _add(xs[0], xs[1], t0, t1)
        for t0, t1 in trechos[1]: _add(xs[2], xs[3], t0, t1)
        for t0, t1 in trechos[2]: _add(t0, t1, zs[0], zs[1])
        for t0, t1 in trechos[3]: _add(t0, t1, zs[2], zs[3])
        for i, lx, cx_ in ((0, 0, b[0][0]), (2, 1, b[1][0])):            # cantos
            for j, lz, cz_ in ((0, 2, b[0][2]), (2, 3, b[1][2])):
                if toca(lx, cz_) and toca(lz, cx_): _add(xs[i], xs[i + 1], zs[j], zs[j + 1])
        if not V: continue
        sc.geometry[g] = _juntar(m, np.vstack(V), np.vstack(F), np.vstack(U)); feito += 1
    if feito: _salvar(sc, path)
    return feito


def _raio_z(malhas, x, y):
    for m in malhas:
        if m.ray.intersects_any([[x, y, 5.0]], [[0, 0, -1.0]])[0]: return True
    return False


def batente_folha(path, folhas):
    """folhas: lista do janelas.json da peca (guilhotina 'desliza' e de abrir 'gira')."""
    sc = trimesh.load(path, force='scene', process=False)
    raiz = _raiz(sc)
    alvo = next((n for n, (g, m) in raiz.items() if m.visual.material.name == 'frame'), None) or \
           next((n for n, (g, m) in raiz.items() if m.visual.material.name == 'trim'), None)
    if alvo is None: return 0
    todas = []
    for n in sc.graph.nodes_geometry:
        T, g = sc.graph[n]; mm = sc.geometry[g]
        todas.append(trimesh.Trimesh(trimesh.transform_points(mm.vertices, T), mm.faces, process=False))
    feito = 0
    for fo in folhas:
        if fo.get('tipo') not in ('desliza', 'gira'): continue
        pts = []
        for n in sc.graph.nodes_geometry:
            T, g = sc.graph[n]
            if np.allclose(T[:3, 3], fo['eixo_m'], atol=2e-3) and not np.allclose(T, np.eye(4)):
                if sc.geometry[g].visual.material.name == 'sash' or 'sash' in n: pts.append(trimesh.transform_points(sc.geometry[g].vertices, T))
        if not pts: continue
        p = np.vstack(pts); x0, x1 = p[:, 0].min(), p[:, 0].max(); yb = p[:, 1].min(); z0 = p[:, 2].min(); z1 = p[:, 2].max()
        xc = (x0 + x1) / 2 + 0.013
        ys = np.arange(yb - 0.04, yb + 0.03, 0.0005)
        livre = [y for y in ys if not _raio_z(todas, xc, y)]
        if not livre or max(livre) - min(livre) < 0.0012: continue
        ya, yt = min(livre), max(livre)
        # guilhotina: ripa por dentro. Folha de abrir gira para dentro, entao a ripa vai por fora.
        za, zb = (z0 - 0.013, z0 - 0.001) if fo['tipo'] == 'desliza' else (z1 + 0.001, z1 + 0.013)
        cx = _caixa(x0 + 0.001, x1 - 0.001, ya - 0.006, yt + 0.007, za, zb)
        g, m = raiz[alvo]
        m = sc.geometry[g]
        sc.geometry[g] = _juntar(m, cx.vertices, cx.faces, np.zeros((len(cx.vertices), 2)))
        feito += 1
    if feito: _salvar(sc, path)
    return feito


def esticar_folha(path, altura):
    sc = trimesh.load(path, force='scene', process=False)
    h = sc.bounds[1][1]
    porta = max(m.bounds[1][1] for m in sc.geometry.values())
    if abs(porta - altura) < 0.002: return 0
    k = altura / porta
    for g, m in list(sc.geometry.items()):
        v = m.vertices.copy(); v[:, 1] *= k
        nm = trimesh.Trimesh(v, m.faces, process=False); nm.visual = m.visual; nm.metadata.update(m.metadata)
        sc.geometry[g] = nm
    _salvar(sc, path)
    return 1


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--porta':
        print(a[1], 'esticada' if esticar_folha(a[1], float(a[2])) else 'ja estava na altura')
        sys.exit(0)
    for kit in a:
        kit = kit.rstrip('/'); nl = nb = 0
        jp = os.path.join(kit, 'janelas.json'); J = json.load(open(jp, encoding='utf-8')) if os.path.exists(jp) else {}
        for f in sorted(glob.glob(os.path.join(kit, 'pieces', '*.glb'))):
            nome = os.path.basename(f)[:-4]
            nl += bool(fechar_laje(f))
            if isinstance(J.get(nome), list): nb += batente_folha(f, J[nome])
        print(kit, nl, 'lajes com o teto fechado,', nb, 'folhas com batente')
