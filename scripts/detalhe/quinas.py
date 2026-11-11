"""Arredonda as quinas vivas das paredes, direto nos GLB das peças de um kit.

    python3 scripts/detalhe/quinas.py kits/<kit> [--so-contar]

Quina = aresta em pé, de fora (convexa), a 90 graus, com pelo menos 40 cm, em material de alvenaria ou
madeira lisa. Ela só é arredondada se estiver à mostra em TODOS os lugares onde a peça aparece no
building_layout.json: se outra peça continua a mesma face depois da aresta (módulo vizinho), a aresta
fica viva, senão abriria um sulco na emenda. Alvenaria leva raio de 10 mm em 3 passos; madeira, 4 mm em 2.

Mantém nós, materiais e UV. O nó `molduras` não é tocado. Rodar de novo não muda nada (não sobra aresta
viva que passe no teste). Precisa de bpy, trimesh e rtree.
"""
import os, sys, glob, json, math
import numpy as np, trimesh
from trimesh.visual import TextureVisuals
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FORA = ('glass', 'gutter', 'siding', 'shingle', 'roof', 'metal', 'iron', 'brass', 'door', 'steel', 'alu', 'sign', 'lamp', 'light', 'dark', 'awning', 'fabric')
MADEIRA = ('trim', 'frame', 'wood', 'deck', 'post', 'board')
MIN_COMP = 0.4


def _mundo(p):
    a = math.radians(float(p.get('rotY', 0))); c, s = math.cos(a), math.sin(a)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]); t = np.array(p['pos'], float)
    return R, t


def _cena(path):
    sc = trimesh.load(path, force='scene', process=False)
    out = []
    for node in sc.graph.nodes_geometry:
        T, gname = sc.graph[node]
        out.append((node, gname, np.array(T), sc.geometry[gname]))
    return sc, out


def _arestas(g):
    """Cadeias de arestas em pé, convexas, a 90 graus. Devolve [(x, z, y0, y1, n1, n2)] no espaço da malha."""
    v = np.asarray(g.vertices); m = trimesh.Trimesh(v, np.asarray(g.faces), process=False)
    m.merge_vertices(merge_tex=True, merge_norm=True)
    if len(m.faces) == 0: return []
    fn = m.face_normals; adj = m.face_adjacency; ed = m.face_adjacency_edges
    if len(adj) == 0: return []
    n1, n2 = fn[adj[:, 0]], fn[adj[:, 1]]
    a, b = m.vertices[ed[:, 0]], m.vertices[ed[:, 1]]
    d = b - a; comp = np.linalg.norm(d, axis=1)
    ok = (comp > 1e-4) & (np.abs(d[:, 1]) > 0.999 * comp) & (np.abs(n1[:, 1]) < 0.05) & (np.abs(n2[:, 1]) < 0.05)
    ok &= np.abs(np.einsum('ij,ij->i', n1, n2)) < 0.17
    ok &= m.face_adjacency_convex
    grupos = {}
    for i in np.nonzero(ok)[0]:
        k = (round(a[i][0], 3), round(a[i][2], 3))
        grupos.setdefault(k, []).append(i)
    out = []
    for (x, z), idx in grupos.items():
        tr = sorted((min(a[i][1], b[i][1]), max(a[i][1], b[i][1])) for i in idx)
        y0, y1 = tr[0]
        cad = []
        for (c0, c1) in tr[1:]:
            if c0 <= y1 + 1e-3: y1 = max(y1, c1)
            else: cad.append((y0, y1)); y0, y1 = c0, c1
        cad.append((y0, y1))
        i0 = idx[0]
        for (y0, y1) in cad:
            if y1 - y0 >= MIN_COMP: out.append((x, z, y0, y1, n1[i0].copy(), n2[i0].copy()))
    return out


def _bisel(g, cadeias, raio, passos):
    import bpy, bmesh
    v = np.asarray(g.vertices); f = np.asarray(g.faces)
    uv = getattr(g.visual, 'uv', None); uv = None if uv is None else np.asarray(uv)
    bm = bmesh.new(); vs = [bm.verts.new(p) for p in v]; bm.verts.ensure_lookup_table()
    lay = bm.loops.layers.uv.new('uv') if uv is not None else None
    for tri in f:
        try: face = bm.faces.new([vs[i] for i in tri])
        except ValueError: continue
        if lay is not None:
            for lp, i in zip(face.loops, tri): lp[lay].uv = uv[i]
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    sel = []
    for e in bm.edges:
        if len(e.link_faces) != 2: continue
        p, q = e.verts[0].co, e.verts[1].co
        if abs(p.x - q.x) > 1e-4 or abs(p.z - q.z) > 1e-4: continue
        ya, yb = min(p.y, q.y), max(p.y, q.y)
        for (x, z, y0, y1, _, _) in cadeias:
            if abs(p.x - x) < 2e-3 and abs(p.z - z) < 2e-3 and ya >= y0 - 1e-3 and yb <= y1 + 1e-3:
                sel.append(e); break
    if not sel: bm.free(); return None
    res = bmesh.ops.bevel(bm, geom=sel, offset=raio, offset_type='OFFSET', segments=passos, profile=0.5, affect='EDGES', clamp_overlap=True)
    if lay is not None:
        # Na faixa nova as duas faces vizinhas chegam com o mesmo u: sem isto a textura vira um risco.
        # O u segue pela largura da faixa, na escala dos kits (UV = metros / 2).
        for face in res['faces']:
            c = face.calc_center_median()
            x, z, _, _, n1, n2 = min(cadeias, key=lambda k: (k[0] - c.x) ** 2 + (k[1] - c.z) ** 2)
            nb = n1 + n2; t = np.array([nb[2], 0.0, -nb[0]]); t /= np.linalg.norm(t)
            for lp in face.loops:
                co = lp.vert.co
                lp[lay].uv.x += ((co.x - x) * t[0] + (co.z - z) * t[2]) * 0.5
    bmesh.ops.triangulate(bm, faces=bm.faces)
    me = bpy.data.meshes.new('q'); bm.to_mesh(me); bm.free()
    me.set_sharp_from_angle(angle=math.radians(40))
    nl = len(me.loops)
    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    li = np.zeros(nl, int); me.loops.foreach_get('vertex_index', li)
    nor = np.zeros(nl * 3); me.corner_normals.foreach_get('vector', nor); nor = nor.reshape(-1, 3)
    V = co[li]; F = np.arange(nl).reshape(-1, 3)
    UV = None
    if uv is not None:
        UV = np.zeros(nl * 2); me.uv_layers[0].data.foreach_get('uv', UV); UV = UV.reshape(-1, 2)
    bpy.data.meshes.remove(me)
    novo = trimesh.Trimesh(V, F, vertex_normals=nor, process=False)
    novo.visual = TextureVisuals(uv=UV, material=g.visual.material)
    return novo


def kit(pasta, so_contar=False):
    lay = json.load(open(os.path.join(pasta, 'building_layout.json')))
    coloc = {}
    for p in lay['placements']: coloc.setdefault(p['piece'], []).append(_mundo(p))
    # Prédio montado, para saber o que encosta em quê.
    cenas = {}; partes = []
    for nome in coloc:
        arq = os.path.join(pasta, 'pieces', nome + '.glb')
        if not os.path.exists(arq): continue
        cenas[nome] = _cena(arq)
        for (R, t) in coloc[nome]:
            for (_, _, T, g) in cenas[nome][1]:
                vv = trimesh.transform_points(np.asarray(g.vertices), T) @ R.T + t
                partes.append(trimesh.Trimesh(vv, np.asarray(g.faces), process=False))
    mundo = trimesh.util.concatenate(partes)
    prox = trimesh.proximity.ProximityQuery(mundo)
    total = 0; mudadas = 0
    for nome, (sc, itens) in sorted(cenas.items()):
        mudou = False
        for (node, gname, T, g) in itens:
            mat = (getattr(g.visual.material, 'name', '') or '').lower()
            if node == 'molduras' or gname == 'molduras' or any(s in mat for s in FORA): continue
            cad = _arestas(g)
            if not cad: continue
            boas = []
            for (x, z, y0, y1, n1, n2) in cad:
                pts = []
                for (R, t) in coloc[nome]:
                    for fr in (0.2, 0.5, 0.8):
                        m = np.array([x, y0 + (y1 - y0) * fr, z])
                        for q in (m + n2 * 0.02 - n1 * 0.002, m + n1 * 0.02 - n2 * 0.002):
                            pts.append(trimesh.transform_points([q], T)[0] @ R.T + t)
                dist = prox.on_surface(np.array(pts))[1]
                if dist.min() > 0.01: boas.append((x, z, y0, y1, n1, n2))
            if not boas: continue
            total += len(boas); print(f'  {nome} [{mat}]: {len(boas)} de {len(cad)}')
            if so_contar: continue
            madeira = any(s in mat for s in MADEIRA)
            novo = _bisel(g, boas, 0.004 if madeira else 0.010, 2 if madeira else 3)
            if novo is not None:
                sc.geometry[gname] = novo; mudou = True
        if mudou:
            arq = os.path.join(pasta, 'pieces', nome + '.glb'); sc.export(arq, include_normals=True)
            from detalhe import glb_jpeg
            glb_jpeg(arq); mudadas += 1
    print(f'{pasta}: {total} quinas à mostra, {mudadas} peças mudadas')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    for a in args: kit(a.rstrip('/'), '--so-contar' in sys.argv)
