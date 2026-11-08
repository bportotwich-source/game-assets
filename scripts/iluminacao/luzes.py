"""Luzes dos interiores: acha as luminarias de cada kit e grava kits/<kit>/luzes.json.

1. Luminarias: as partes de vidro/lampada das pecas (materiais lamp_*, light, bulb, tube_*), menos as dos veiculos. Cada pedaco solto vira
   uma luz no centro dele; pedacos a menos de 0,4 m um do outro sao a mesma luminaria.
2. Comodos sem luminaria: luzes de teto geradas (uma a cada ~25 m2), porque os kits antigos nao tem luminarias.
   Os comodos vem de scripts/ambientacao/comodos.py; os de fora (patio, rua, telhado) nao ganham luz gerada.
3. A cor depende do perfil do kit em scripts/ambientacao/kits.json: casa = lampada quente, o resto = mais neutra.

O Godot (visitar/main.gd) cria uma OmniLight3D por luz e faz brilhar os materiais listados em 'materiais'.

Uso: python3 scripts/iluminacao/luzes.py [kit ...]     (sem argumentos: todos os kits)
"""
import json, math, os, sys
import numpy as np, trimesh

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'scripts', 'ambientacao'))
import comodos as CM

QUENTE = [1.0, 0.82, 0.62]
NEUTRA = [1.0, 0.93, 0.84]
FORA = [1.0, 0.86, 0.66]


VEICULOS = ('car_', 'ambulance', 'truck', 'food_truck', 'bus', 'van_', 'pickup', 'fire_engine', 'engine_', 'trailer_car', 'tractor', 'forklift')   # farois nao sao luminarias


def eh_lampada(nome):
    n = (nome or '').lower()
    return n.startswith('lamp') or n in ('light', 'bulb', 'tube_g', 'tube_w', 'globe', 'lamp_glass') or n.startswith('bulb')


def luminarias(kit):
    lay = json.load(open(os.path.join(kit, 'building_layout.json')))
    cache, pontos, mats = {}, [], set()
    for e in lay['placements']:
        nome = e['piece']
        if nome.startswith('player_scale') or 'door' in e or nome.startswith(VEICULOS): continue
        if nome not in cache:
            f = os.path.join(kit, 'pieces', nome + '.glb'); cache[nome] = []
            if os.path.exists(f):
                sc = trimesh.load(f, force='scene')
                for no in sc.graph.nodes_geometry:
                    T, g = sc.graph[no]; geo = sc.geometry[g]
                    mn = getattr(getattr(geo.visual, 'material', None), 'name', '')
                    if not eh_lampada(mn) or len(geo.faces) == 0: continue
                    mats.add(mn)
                    for parte in geo.split(only_watertight=False):
                        b = parte.bounds; c = (b[0] + b[1]) / 2
                        cache[nome].append((T @ np.array([c[0], c[1], c[2], 1.0]))[:3])
        if not cache[nome]: continue
        R = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); R[:3, 3] = e['pos']
        for c in cache[nome]: pontos.append((R @ np.append(c, 1.0))[:3])
    # junta os pedacos da mesma luminaria
    juntos = []
    for p in pontos:
        for j in juntos:
            if np.linalg.norm(j['c'] / j['n'] - p) < 0.4: j['c'] = j['c'] + p; j['n'] += 1; break
        else: juntos.append(dict(c=np.array(p, float), n=1))
    return [j['c'] / j['n'] for j in juntos], sorted(mats)


def onde(res, p):
    """(andar, comodo) do ponto p, ou (andar, None) se nao cai em nenhum comodo."""
    u = int((p[0] - res['x0']) / CM.CEL); v = int((p[2] - res['z0']) / CM.CEL)
    for an in res['andares']:
        if an['y'] - 0.3 <= p[1] <= an['teto'] + 0.2:
            if not (0 <= u < res['nx'] and 0 <= v < res['nz']): return an, None
            best = None
            for du in range(-3, 4):                       # a luminaria fica sobre o comodo, mas pode cair numa celula ocupada
                for dv in range(-3, 4):
                    a, b = u + du, v + dv
                    if 0 <= a < res['nx'] and 0 <= b < res['nz'] and an['rotulo'][a, b] >= 0:
                        d = du * du + dv * dv
                        if best is None or d < best[0]: best = (d, int(an['rotulo'][a, b]))
            return an, (best[1] if best else None)
    return None, None


def externo(res, an, cid):
    cel = np.argwhere(an['rotulo'] == cid)
    return cel[:, 0].min() <= 1 or cel[:, 1].min() <= 1 or cel[:, 0].max() >= res['nx'] - 2 or cel[:, 1].max() >= res['nz'] - 2


def gerar(nome_kit, perfil):
    kit = os.path.join(RAIZ, 'kits', nome_kit)
    res = CM.analisar(kit)
    lamps, mats = luminarias(kit)
    cor = QUENTE if perfil == 'casa' else NEUTRA
    luzes, com_luz = [], set()
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(res['malha'])
    for p in lamps:
        an, cid = onde(res, p)
        if an is not None and p[1] < an['y'] + 0.5: continue       # perto do chao: farol, luz de sinalizacao, nao ilumina o comodo
        dentro = an is not None and cid is not None and not externo(res, an, cid)
        if dentro:
            c = next(c for c in an['comodos'] if c['id'] == cid); com_luz.add((an['andar'], cid))
            alc = float(np.clip(math.sqrt(c['area']) * 1.2 + 1.5, 3.5, 9.0))
            luzes.append(dict(pos=[round(float(v), 3) for v in (p[0], p[1] - 0.08, p[2])], alcance=round(alc, 1), energia=1.0, cor=cor,
                              tipo='luminaria', andar=an['andar'], comodo=cid))
        else:
            luzes.append(dict(pos=[round(float(v), 3) for v in (p[0], p[1] - 0.08, p[2])], alcance=6.0, energia=0.8, cor=FORA,
                              tipo='externa', andar=an['andar'] if an else 0, comodo=None))
    for an in res['andares']:
        for c in an['comodos']:
            if (an['andar'], c['id']) in com_luz or c['area'] < 2.0 or externo(res, an, c['id']): continue
            piso = c.get('piso', '')
            if piso.startswith('roof') or '_roof' in piso: continue
            x0, z0, x1, z1 = c['caixa']; w, d = x1 - x0, z1 - z0
            nx = max(1, round(w / 5.0)); nz = max(1, round(d / 5.0))
            if nx * nz * 25 < c['area'] * 0.5: nx, nz = max(1, math.ceil(w / 5.0)), max(1, math.ceil(d / 5.0))
            y = min(an['teto'] - 0.45, an['y'] + 4.0)
            cel = np.argwhere(an['rotulo'] == c['id'])
            pts = np.stack([res['xs'][cel[:, 0]], res['zs'][cel[:, 1]]], 1)
            area_luz = c['area'] / (nx * nz)
            alc = float(np.clip(math.sqrt(area_luz) * 1.25 + 1.5, 3.5, 9.0))
            for i in range(nx):
                for j in range(nz):
                    alvo = np.array([x0 + (i + 0.5) * w / nx, z0 + (j + 0.5) * d / nz])
                    q = pts[np.argmin(((pts - alvo) ** 2).sum(1))]         # celula do comodo mais perto (comodos em L)
                    # teto de verdade logo acima (forro, laje ou telhado): o Godot poe ali um plafon simples
                    loc, _, _ = ray.intersects_location([[q[0], an['y'] + 1.2, q[1]]], [[0, 1.0, 0]], multiple_hits=True)
                    acima = sorted(v for v in loc[:, 1] if v > an['y'] + 1.9) if len(loc) else []
                    teto = float(acima[0]) if acima else float(y + 0.45)
                    yl = min(teto - 0.22, y + 0.25) if teto - an['y'] < 4.6 else y
                    luzes.append(dict(pos=[round(float(q[0]), 3), round(float(yl), 3), round(float(q[1]), 3)], alcance=round(alc, 1), energia=0.85, cor=cor,
                                      tipo='gerada', teto=round(teto, 3), andar=an['andar'], comodo=c['id']))
    out = dict(kit=nome_kit, gerado_por='scripts/iluminacao/luzes.py',
               convencao="pos em metros no espaço do prédio (o mesmo do building_layout.json); alcance em metros; tipo 'luminaria' = luz de uma luminária do kit, "
                         "'gerada' = luz de teto num cômodo sem luminária (teto = altura do teto ali, onde o Godot põe um plafon), 'externa' = luminária fora dos cômodos (varanda, poste, fachada)",
               materiais=mats, luzes=luzes)
    json.dump(out, open(os.path.join(kit, 'luzes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = {t: sum(1 for l in luzes if l['tipo'] == t) for t in ('luminaria', 'gerada', 'externa')}
    print(f"{nome_kit}: {n['luminaria']} de luminária, {n['gerada']} geradas, {n['externa']} externas ({', '.join(mats) or 'sem material de lâmpada'})", flush=True)


def main(kits):
    cfgs = json.load(open(os.path.join(RAIZ, 'scripts', 'ambientacao', 'kits.json'), encoding='utf-8'))
    todos = sorted(k for k in os.listdir(os.path.join(RAIZ, 'kits')) if os.path.exists(os.path.join(RAIZ, 'kits', k, 'building_layout.json')))
    for k in kits or todos:
        gerar(k, cfgs.get(k, {}).get('perfil', 'comercial'))


if __name__ == '__main__':
    main(sys.argv[1:])
