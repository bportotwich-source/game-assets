"""Folha da janela como peca propria, para o jogo abrir a janela de verdade.

Nas pecas de janela a folha (vidro + montantes e travessas da folha) vinha junta com a parede, o marco e o
peitoril. Este script tira esses triangulos do lugar e poe num no proprio dentro do mesmo GLB:

  <peca>.glb
    <peca>_<material>        parede, marco, peitoril... (como antes, sem a folha)
    folha                    no vazio com a origem no eixo de abertura
      folha_<material>       vidro e caixilho da folha
    folha_2 ...              (janelas de batente com mais de uma folha)

A aparencia nao muda: os mesmos triangulos, os mesmos materiais, so trocam de no.
Como cada folha abre fica em kits/<kit>/janelas.json:
  "desliza": guilhotina. A folha de baixo sobe 'curso_m' metros no eixo Y local da peca (fica por dentro da de cima).
  "gira":    batente. A origem do no esta na dobradica (lado 'dobradica', borda externa da folha);
             gire em Y ate 'angulo_graus' (o sinal ja abre para dentro da casa, sentido -Z da peca).

Como acha a folha: os vidros da peca viram "panos"; o pano mais baixo e a folha que abre. Se ha outro pano
em cima dele noutro plano (z), e guilhotina; se ha varios panos lado a lado embaixo, e batente (um por pano).
Bandeiras e basculantes de cima ficam fixos. Entra na folha todo triangulo cujos 3 vertices caem na caixa do
pano (+7 cm de lado, +9 cm embaixo, +3,2 cm de profundidade): pega a folha e deixa marco e parede de fora.

Uso:  python3 scripts/detalhe/folhas.py kits/bangalo kits/three-flats ...   (pecas *win* de cada kit)
Rodar de novo numa peca ja separada nao muda nada (ela ja tem o no 'folha').
"""
import json, os, sys, glob
import numpy as np, trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _panos(glass):
    g = glass.copy(); g.merge_vertices(merge_tex=True, merge_norm=True)
    lab = trimesh.graph.connected_component_labels(g.face_adjacency, node_count=len(g.faces))
    out = []
    for l in np.unique(lab):
        f = np.nonzero(lab == l)[0]; v = glass.vertices[glass.faces[f].ravel()]
        lo, hi = v.min(0), v.max(0)
        if (hi[0] - lo[0]) < 0.08 or (hi[1] - lo[1]) < 0.08: continue
        out.append({'faces': f, 'lo': lo, 'hi': hi, 'zc': (lo[2] + hi[2]) / 2})
    return out


def _abertura(panos):
    if not panos: return []
    y0 = min(p['lo'][1] for p in panos)
    baixo = sorted([p for p in panos if p['lo'][1] <= y0 + 0.05], key=lambda p: p['lo'][0])
    if len(baixo) == 1:
        p = baixo[0]; w = p['hi'][0] - p['lo'][0]
        cima = [q for q in panos if q is not p and q['lo'][1] > p['hi'][1] - 0.1 and abs(q['zc'] - p['zc']) >= 0.03
                and min(q['hi'][0], p['hi'][0]) - max(q['lo'][0], p['lo'][0]) > 0.5 * w]
        if cima:
            q = min(cima, key=lambda q: q['lo'][1])
            return [(p, {'tipo': 'desliza', 'curso_m': round(float(q['hi'][1] - p['hi'][1]), 3)})]
        return [(p, {'tipo': 'gira', 'dobradica': 'esquerda', 'angulo_graus': 85})]
    res = []
    for i, p in enumerate(baixo):
        d = 'direita' if i == len(baixo) - 1 else 'esquerda'
        res.append((p, {'tipo': 'gira', 'dobradica': d, 'angulo_graus': 85 if d == 'esquerda' else -85}))
    return res


def separar(path):
    """Separa a(s) folha(s) de uma peca de janela. Devolve a lista de folhas (para o janelas.json) ou None."""
    sc = trimesh.load(path, force='scene', process=False)
    nos = list(sc.graph.nodes_geometry)
    if any(n == 'folha' or n.startswith('folha_') for n in sc.graph.nodes): return 'ja'
    geos = {}
    for n in nos:
        T, gname = sc.graph[n]; g = sc.geometry[gname].copy()
        if not np.allclose(T, np.eye(4)): g.apply_transform(T)
        geos[n] = g
    glass = [n for n, g in geos.items() if g.visual.material.name == 'glass']
    if not glass: return None
    panos = _panos(geos[glass[0]])
    ab = _abertura(panos)
    if not ab: return None
    usado = {n: np.zeros(len(g.faces), bool) for n, g in geos.items()}
    folhas = []
    for i, (p, info) in enumerate(ab):
        lo = p['lo'] - [0.07, 0.09, 0.0]; hi = p['hi'] + [0.07, 0.07, 0.0]
        za, zb = p['zc'] - 0.032, p['zc'] + 0.032
        partes = {}
        for n, g in geos.items():
            if n in glass:
                sel = np.zeros(len(g.faces), bool); sel[p['faces']] = True
            else:
                v = g.vertices[g.faces]                                   # (F, 3, 3)
                sel = np.all((v[..., 0] >= lo[0]) & (v[..., 0] <= hi[0]) & (v[..., 1] >= lo[1]) & (v[..., 1] <= hi[1])
                             & (v[..., 2] >= za) & (v[..., 2] <= zb), axis=1)
            sel &= ~usado[n]
            if sel.any(): usado[n] |= sel; partes[n] = np.nonzero(sel)[0]
        vs = np.vstack([geos[n].vertices[geos[n].faces[f]].reshape(-1, 3) for n, f in partes.items()])
        flo, fhi = vs.min(0), vs.max(0)
        if info['tipo'] == 'desliza':
            piv = np.array([(flo[0] + fhi[0]) / 2, flo[1], (flo[2] + fhi[2]) / 2])
        else:
            piv = np.array([flo[0] if info['dobradica'] == 'esquerda' else fhi[0], flo[1], fhi[2]])
        nome = 'folha' if i == 0 else f'folha_{i + 1}'
        folhas.append((nome, piv, partes, dict(no=nome, **info, eixo_m=[round(float(c), 3) for c in piv],
                                                largura_m=round(float(fhi[0] - flo[0]), 3), altura_m=round(float(fhi[1] - flo[1]), 3))))
    out = trimesh.Scene()
    for n, g in geos.items():
        keep = np.nonzero(~usado[n])[0]
        if len(keep) == 0: continue
        m = g.submesh([keep], append=True) if len(keep) < len(g.faces) else g
        m.visual.material = g.visual.material
        out.add_geometry(m, node_name=n, geom_name=n)
    for nome, piv, partes, _ in folhas:
        T = np.eye(4); T[:3, 3] = piv
        out.graph.update(frame_from=out.graph.base_frame, frame_to=nome, matrix=T)
        for n, f in partes.items():
            g = geos[n]; m = g.submesh([f], append=True); m.visual.material = g.visual.material
            m.apply_translation(-piv); mat = g.visual.material.name
            out.add_geometry(m, node_name=f'{nome}_{mat}', geom_name=f'{nome}_{mat}', parent_node_name=nome)
    out.export(path, include_normals=True)
    from detalhe import glb_jpeg
    glb_jpeg(path)
    return [f[3] for f in folhas]


def kit(pasta):
    js = os.path.join(pasta, 'janelas.json')
    dados = json.load(open(js)) if os.path.exists(js) else {}
    for f in sorted(glob.glob(os.path.join(pasta, 'pieces', '*.glb'))):
        n = os.path.basename(f)[:-4]
        if 'win' not in n: continue
        r = separar(f)
        if r == 'ja' or r is None: continue
        dados[n] = r
    leia = ('Folhas de janela separadas por scripts/detalhe/folhas.py. Cada peca tem nos "folha" (e "folha_2"...) com a '
            'origem no eixo. desliza: subir curso_m em Y. gira: girar em Y ate angulo_graus na dobradica (o sinal ja abre para '
            'dentro, -Z). eixo_m e a origem do no na peca.')
    dados = {'_leia': leia, **{k: v for k, v in sorted(dados.items()) if k != '_leia'}}
    json.dump(dados, open(js, 'w'), indent=1, ensure_ascii=False)
    return len(dados) - 1


if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(a, kit(a.rstrip('/')), 'pecas de janela')
