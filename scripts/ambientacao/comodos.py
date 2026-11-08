"""Detecta os comodos de um kit a partir das pecas montadas (sem depender do texto do README).

Para cada andar: monta as pecas do building_layout.json (sem as folhas de porta), corta a malha em
3 alturas (0,5 / 1,0 / 1,6 m acima do piso) para achar paredes e moveis fixos, lanca raios de cima
para achar o piso livre, marca os vaos de porta e separa as areas livres em comodos (flood fill).

Uso: python3 scripts/ambientacao/comodos.py kits/padaria [--png saida.png]
"""
import json, math, os, sys
from collections import deque
import numpy as np, trimesh

CEL = 0.25          # tamanho da celula da grade (m)


def carregar_kit(kit):
    lay = json.load(open(os.path.join(kit, 'building_layout.json')))
    cache, malhas, portas, niveis = {}, [], [], {}
    for e in lay['placements']:
        nome = e['piece']
        if nome.startswith('player_scale'): continue
        T = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); T[:3, 3] = e['pos']
        for t in e.get('tags', []):
            if t.startswith('floor') and t[5:].isdigit():
                eh_piso = any(p in nome for p in ('floor', 'slab', 'deck', 'tile')) and 'ceiling' not in nome and 'stair' not in nome
                niveis.setdefault(int(t[5:]), []).append((0 if eh_piso else 1, e['pos'][1]))
        if nome not in cache:
            f = os.path.join(kit, 'pieces', nome + '.glb')
            if not os.path.exists(f): cache[nome] = None; continue
            sc = trimesh.load(f, force='scene'); cache[nome] = sc.to_geometry() if hasattr(sc, 'to_geometry') else sc.dump(concatenate=True)
        m = cache[nome]
        if m is None or len(m.faces) == 0: continue
        if 'door' in e or 'door_leaf' in nome or nome.startswith('leaf') or '_leaf' in nome:
            b = m.bounds; c = (b[0] + b[1]) / 2; w = b[1][0] - b[0][0]
            pc = T @ np.array([c[0], 0, c[2], 1.0]); eixo = T[:3, :3] @ np.array([1.0, 0, 0])
            portas.append(dict(c=pc[:3], eixo=eixo, larg=max(w, 0.8), y=e['pos'][1])); continue
        mm = m.copy(); mm.apply_transform(T); malhas.append((nome, mm))
        if 'door' in nome and 'doorway' in nome or nome.endswith('_doorway') or 'arch' in nome:
            portas.append(dict(c=np.array(e['pos'], float), eixo=T[:3, :3] @ np.array([1.0, 0, 0]), larg=1.0, y=e['pos'][1], vao=True))
    lv = {}
    for k, v in niveis.items():
        pisos = [y for t, y in v if t == 0]
        lv[k] = min(pisos) if pisos else min(y for _, y in v)
    return lay, malhas, portas, dict(sorted(lv.items()))


def analisar(kit):
    lay, malhas, portas, niveis = carregar_kit(kit)
    tudo = trimesh.util.concatenate([m for _, m in malhas])
    nomes = np.array([n for n, _ in malhas]); dono = np.repeat(np.arange(len(malhas)), [len(m.faces) for _, m in malhas])   # face -> peca
    lo, hi = tudo.bounds; x0, z0 = lo[0] - 0.5, lo[2] - 0.5
    nx, nz = int((hi[0] - x0 + 0.5) / CEL) + 1, int((hi[2] - z0 + 0.5) / CEL) + 1
    xs = x0 + (np.arange(nx) + 0.5) * CEL; zs = z0 + (np.arange(nz) + 0.5) * CEL
    gx, gz = np.meshgrid(xs, zs, indexing='ij')
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(tudo)
    andares = []
    lvs = sorted(set(round(v, 2) for v in niveis.values())) or [0.0]
    for i, y in enumerate(lvs):
        teto = lvs[i + 1] if i + 1 < len(lvs) else y + 3.0
        y_raio = min(y + 1.95, teto - 0.25)
        org = np.stack([gx.ravel(), np.full(gx.size, y_raio), gz.ravel()], 1); d = np.tile([0, -1.0, 0], (len(org), 1))
        loc, idx, tri = ray.intersects_location(org, d, multiple_hits=True)
        alto = np.full(gx.size, -1e9)                                    # primeiro obstaculo abaixo do raio
        peca_piso = np.full(gx.size, -1)
        if len(idx):
            ok = loc[:, 1] < y_raio - 1e-4
            np.maximum.at(alto, idx[ok], loc[ok, 1])
            top = ok & (np.abs(loc[:, 1] - alto[idx]) < 1e-5); peca_piso[idx[top]] = dono[tri[top]]
        piso = (alto > y - 0.12) & (alto < y + 0.35)
        livre = piso.reshape(nx, nz).copy()
        for h in (0.5, 1.0, 1.6):                                         # paredes e moveis fixos
            sec = tudo.section(plane_origin=[0, y + h, 0], plane_normal=[0, 1, 0])
            if sec is None: continue
            for ent in sec.entities:
                pts = sec.vertices[ent.points]
                for a, b in zip(pts[:-1], pts[1:]):
                    L = np.linalg.norm(b - a); n = max(2, int(L / (CEL * 0.4)) + 1)
                    for t in np.linspace(0, 1, n):
                        p = a + (b - a) * t; ix = int((p[0] - x0) / CEL); iz = int((p[2] - z0) / CEL)
                        if 0 <= ix < nx and 0 <= iz < nz: livre[ix, iz] = False
        porta = np.zeros_like(livre)
        for pt in portas:
            if abs(pt['y'] - y) > 0.6: continue
            c = pt['c']; e = pt['eixo'] / (np.linalg.norm(pt['eixo']) + 1e-9); nrm = np.array([-e[2], 0, e[0]])
            rel = np.stack([gx - c[0], gz - c[2]], -1)
            ao_longo = rel @ e[[0, 2]]; atraves = rel @ nrm[[0, 2]]
            porta |= (np.abs(ao_longo) <= pt['larg'] / 2 + 0.05) & (np.abs(atraves) <= 0.35)
        livre &= ~porta
        rot = -np.ones((nx, nz), int); comodos = []
        for ix in range(nx):
            for iz in range(nz):
                if not livre[ix, iz] or rot[ix, iz] >= 0: continue
                k = len(comodos); fila = deque([(ix, iz)]); rot[ix, iz] = k; cel = []
                while fila:
                    a, b = fila.popleft(); cel.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        u, v = a + da, b + db
                        if 0 <= u < nx and 0 <= v < nz and livre[u, v] and rot[u, v] < 0: rot[u, v] = k; fila.append((u, v))
                comodos.append(cel)
        lista = []
        for k, cel in enumerate(comodos):
            a = np.array(cel); area = len(cel) * CEL * CEL
            if area < 1.0: rot[a[:, 0], a[:, 1]] = -1; continue
            cx, cz = xs[a[:, 0]].mean(), zs[a[:, 1]].mean()
            pp = peca_piso.reshape(nx, nz)[a[:, 0], a[:, 1]]; pp = pp[pp >= 0]
            piso_nome = str(nomes[np.bincount(pp).argmax()]) if len(pp) else ''
            lista.append(dict(id=k, area=round(area, 1), centro=[round(cx, 2), round(cz, 2)], piso=piso_nome,
                              caixa=[round(xs[a[:, 0]].min() - CEL / 2, 2), round(zs[a[:, 1]].min() - CEL / 2, 2), round(xs[a[:, 0]].max() + CEL / 2, 2), round(zs[a[:, 1]].max() + CEL / 2, 2)]))
        andares.append(dict(andar=i, y=y, teto=teto, rotulo=rot, porta=porta, comodos=lista))
    return dict(kit=os.path.basename(kit.rstrip('/')), x0=x0, z0=z0, nx=nx, nz=nz, xs=xs, zs=zs, andares=andares, malha=tudo)


def png(res, saida):
    from PIL import Image, ImageDraw
    an = res['andares']; s = 6; W = res['nx'] * s; H = res['nz'] * s
    img = Image.new('RGB', (W * len(an) + 10 * (len(an) - 1), H + 20), (255, 255, 255)); d = ImageDraw.Draw(img)
    rng = np.random.default_rng(1); cores = [tuple(int(c) for c in rng.integers(90, 240, 3)) for _ in range(400)]
    for i, a in enumerate(an):
        ox = i * (W + 10)
        for ix in range(res['nx']):
            for iz in range(res['nz']):
                r = a['rotulo'][ix, iz]; c = (60, 60, 60) if r < 0 else cores[r % 400]
                if a['porta'][ix, iz]: c = (230, 40, 40)
                if r < 0 and not a['porta'][ix, iz]: c = (235, 235, 235)
                d.rectangle([ox + ix * s, iz * s, ox + ix * s + s - 1, iz * s + s - 1], fill=c)
        for c in a['comodos']:
            px = ox + (c['centro'][0] - res['x0']) / CEL * s; pz = (c['centro'][1] - res['z0']) / CEL * s
            d.text((px - 6, pz - 5), str(c['id']), fill=(0, 0, 0))
        d.text((ox + 2, H + 4), f"andar {a['andar']} (y={a['y']})", fill=(0, 0, 0))
    img.save(saida)


if __name__ == '__main__':
    r = analisar(sys.argv[1])
    for a in r['andares']:
        print(f"andar {a['andar']} y={a['y']}: " + '; '.join(f"#{c['id']} {c['area']}m² c={c['centro']}" for c in a['comodos']))
    if '--png' in sys.argv: png(r, sys.argv[sys.argv.index('--png') + 1])
