"""Molduras internas em geometria, aplicadas direto nos GLB das pecas de parede de um kit.

Os kits antigos tinham rodape e guarnicao como caixas lisas e nada no teto nem em volta das janelas por dentro;
o resto era pintado pelo shader do acabamento. Aqui cada face interna de parede lisa ('plaster') ganha:

  - rodape de 15 cm com perfil (meia-cana no pe, corpo, friso e topo arredondado), no lugar da caixa de 10 cm;
  - sanca de 9 x 7,5 cm no encontro com o teto;
  - guarnicao de porta: pernas com perfil e cordao externo, soco no pe e verga com friso e capa;
  - guarnicao de janela por dentro: pernas e verga iguais, peitoril com nariz e avental embaixo.

Como acha onde por: junta os triangulos de 'plaster' de cada face em pe (plano z constante da peca), e o que falta
no retangulo da face sao os vaos. Vao que chega no piso e porta, o resto e janela. O rodape para nas guarnicoes.

Tudo entra num no so por peca, 'molduras', com o material 'trim' da propria peca (ou do kit). Rodar de novo refaz
o no e nao muda mais nada. Uso:
    python3 scripts/detalhe/molduras.py kits/casa-americana [--teto 2.8]
"""
import os, sys, glob
import numpy as np, trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from trimesh.visual import TextureVisuals

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
NO = 'molduras'
FORA = ('garage', 'stair', 'gable', 'roof', 'floor', 'ceiling', 'chimney', 'porch', 'leaf', 'corner', 'ridge', 'deck', 'slab')

# perfis em (d, y): d = para fora da parede, y = altura
RODAPE = [(0, 0), (0.03, 0), (0.03, 0.006), (0.026, 0.014), (0.018, 0.02), (0.018, 0.105), (0.014, 0.112), (0.014, 0.122), (0.009, 0.136), (0.006, 0.15), (0, 0.15)]
SANCA = [(0, 0), (0.075, 0), (0.075, -0.012), (0.066, -0.018), (0.058, -0.034), (0.044, -0.052), (0.026, -0.064), (0.016, -0.07), (0.016, -0.082), (0.008, -0.09), (0, -0.09)]
# guarnicao em (u, d): u = afastando do vao, d = para fora da parede
PERNA = [(0, 0), (0, 0.012), (0.008, 0.016), (0.02, 0.016), (0.026, 0.02), (0.06, 0.02), (0.066, 0.026), (0.084, 0.026), (0.09, 0.02), (0.09, 0)]
LARG = 0.09
CAPA = [(0, 0), (0.03, 0), (0.042, 0.012), (0.042, 0.03), (0, 0.03)]
NARIZ = lambda r: [(-r, 0), (0.04, 0), (0.05, -0.008), (0.05, -0.024), (0.04, -0.032), (-r, -0.032)]
AVENTAL = [(0, 0), (0.016, 0), (0.016, -0.07), (0.008, -0.085), (0, -0.085)]


def _extr(pts, comp, mapa):
    """Extruda o poligono pts por comp e leva (a, b, h) para (x, y, z) com mapa."""
    m = trimesh.creation.extrude_polygon(Polygon(pts).buffer(0), comp)
    a, b, h = m.vertices.T
    m.vertices = np.stack(mapa(a, b, h), 1)
    if m.volume < 0: m.invert()
    return m


def _caixa(x0, x1, y0, y1, zf, sg, d0, d1):
    z0, z1 = sorted((zf + sg * d0, zf + sg * d1))
    return trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0], transform=trimesh.transformations.translation_matrix([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]))


def ao_longo(perfil, x0, x1, y0, zf, sg):
    """Perfil (d, y) corrido ao longo de x, na face zf virada para sg."""
    return _extr(perfil, x1 - x0, lambda a, b, h: (x0 + h, y0 + b, zf + sg * a))


def perna(xe, lado, ya, yb, zf, sg):
    return _extr(PERNA, yb - ya, lambda a, b, h: (xe + lado * a, ya + h, zf + sg * b))


def _intervalos(geom, y0, y1):
    """Trechos de x em que a face tem parede na faixa de altura y0..y1."""
    g = geom.intersection(box(-99, y0, 99, y1)); out = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty or p.geom_type != 'Polygon': continue
        a, _, b, _ = p.bounds
        if b - a > 0.03: out.append([a, b])
    out.sort(); junto = []
    for a, b in out:
        if junto and a <= junto[-1][1] + 1e-3: junto[-1][1] = max(junto[-1][1], b)
        else: junto.append([a, b])
    return junto


def _tirar(trechos, bloqueios):
    for c, d in bloqueios:
        novo = []
        for a, b in trechos:
            if d <= a or c >= b: novo.append([a, b]); continue
            if c - a > 0.03: novo.append([a, c])
            if b - d > 0.03: novo.append([d, b])
        trechos = novo
    return trechos


def faces_de_parede(sc):
    """Faces em pe de 'plaster': lista de (z, sinal, poligono em (x, y))."""
    por = {}
    for n in sc.graph.nodes_geometry:
        T, g = sc.graph[n]; m = sc.geometry[g]
        if n == NO or not np.allclose(T, np.eye(4)) or getattr(m.visual.material, 'name', '') != 'plaster': continue
        nz = m.face_normals[:, 2]
        for f in np.nonzero(np.abs(nz) > 0.99)[0]:
            t = m.vertices[m.faces[f]]
            por.setdefault((round(float(t[:, 2].mean()), 3), int(np.sign(nz[f]))), []).append(Polygon(t[:, :2]))
    out = []
    for (z, sg), ps in por.items():
        u = unary_union([p.buffer(1e-4) for p in ps if p.area > 1e-6])
        if u.area > 0.5: out.append((z, sg, u))
    return out


def _quadros(sc):
    """Caixas das geometrias 'frame' (batentes), para a guarnicao encostar nelas."""
    out = []
    for n in sc.graph.nodes_geometry:
        T, g = sc.graph[n]; m = sc.geometry[g]
        if n != NO and np.allclose(T, np.eye(4)) and getattr(m.visual.material, 'name', '') == 'frame': out.append(m.bounds)
    return out


def _sem_rodape_antigo(sc):
    """Tira a caixa de rodape antiga (triangulos de 'trim' ate 13 cm do piso, colados na parede)."""
    for n in list(sc.graph.nodes_geometry):
        T, g = sc.graph[n]; m = sc.geometry[g]
        if n == NO or not np.allclose(T, np.eye(4)) or getattr(m.visual.material, 'name', '') != 'trim': continue
        comp = trimesh.graph.connected_component_labels(m.face_adjacency, node_count=len(m.faces))
        manter = np.ones(len(m.faces), bool)
        for c in np.unique(comp):
            v = m.vertices[np.unique(m.faces[comp == c])]
            if v[:, 1].max() <= 0.13 and v[:, 1].min() >= -0.01 and np.ptp(v[:, 2]) <= 0.03: manter[comp == c] = False
        if manter.all(): continue
        if not manter.any(): sc.delete_geometry(g); continue
        m.update_faces(manter); m.remove_unreferenced_vertices()


def moldurar(path, teto, mat_trim):
    sc = trimesh.load(path, force='scene', process=False)
    if NO in sc.graph.nodes_geometry: sc.delete_geometry(sc.graph[NO][1])
    faces = faces_de_parede(sc)
    if not faces: return 0
    _sem_rodape_antigo(sc)
    quadros = _quadros(sc); partes = []
    for zf, sg, u in faces:
        x0, y0, x1, y1 = u.bounds
        if y0 > 0.05 or y1 - y0 < 2.0: continue                       # so parede que nasce no piso
        vaos = [h for h in getattr(box(x0, y0, x1, y1).difference(u), 'geoms', [box(x0, y0, x1, y1).difference(u)]) if not h.is_empty and h.area > 0.15]
        bloqueios = []
        for h in vaos:
            a, b, c, d = h.bounds
            if c - a < 0.4 or d - b < 0.5 or d > y1 - 0.02 and b > 0.3: continue
            porta = b < 0.1
            for q in quadros:                                         # batente que avanca sobre a parede: a guarnicao encosta nele
                if q[0][1] < d and q[1][1] > b and q[0][0] < c and q[1][0] > a:
                    a, c, d = min(a, q[0][0]), max(c, q[1][0]), max(d, q[1][1])
            if a - LARG < x0 - 0.02 or c + LARG > x1 + 0.02: continue  # nao cabe a guarnicao
            pe = 0.19 if porta else b
            for xe, lado in ((a, -1), (c, 1)):
                partes.append(perna(xe, lado, pe, d, zf, sg))
                if porta: partes.append(_caixa(min(xe, xe + lado * 0.1), max(xe, xe + lado * 0.1), 0, 0.19, zf, sg, 0, 0.032))
            partes.append(_caixa(a - LARG - 0.008, c + LARG + 0.008, d, d + 0.02, zf, sg, 0, 0.03))            # filete
            partes.append(_caixa(a - LARG, c + LARG, d + 0.02, d + 0.12, zf, sg, 0, 0.022))                     # friso
            partes.append(ao_longo(CAPA, a - LARG - 0.02, c + LARG + 0.02, d + 0.12, zf, sg))                   # capa
            if porta: bloqueios.append((a - 0.1, c + 0.1))
            else:
                rec = 0.0
                for q in quadros:
                    if q[0][0] < c and q[1][0] > a: rec = max(rec, min(abs(zf - q[0][2]), abs(zf - q[1][2])))
                partes.append(ao_longo(NARIZ(min(rec, 0.2)), a - LARG - 0.03, c + LARG + 0.03, b + 0.032, zf, sg))   # peitoril
                partes.append(ao_longo(AVENTAL, a - LARG + 0.01, c + LARG - 0.01, b, zf, sg))
        for a, b in _tirar(_intervalos(u, 0.0, 0.05), bloqueios):
            partes.append(ao_longo(RODAPE, a, b, 0.0, zf, sg))
        if teto - 1e-3 <= y1 <= teto + 0.35:                            # parede mais alta que isso e de outro pe-direito: fica sem sanca
            for a, b in _intervalos(u, teto - 0.05, teto):
                partes.append(ao_longo(SANCA, a, b, teto, zf, sg))
    if not partes: return 0
    m = trimesh.util.concatenate(partes); m.unmerge_vertices()
    uv = None
    if getattr(mat_trim, 'baseColorTexture', None) is not None:
        n = np.abs(m.vertex_normals); ax = n.argmax(1); v = m.vertices
        uv = np.where((ax == 0)[:, None], v[:, [2, 1]], np.where((ax == 1)[:, None], v[:, [0, 2]], v[:, [0, 1]])) / 2
    m.visual = TextureVisuals(uv=uv, material=mat_trim)
    sc.add_geometry(m, node_name=NO, geom_name=NO)
    sc.export(path, include_normals=True)
    from detalhe import glb_jpeg
    glb_jpeg(path)
    return len(m.faces)


def material_trim(pasta):
    for f in sorted(glob.glob(os.path.join(pasta, 'pieces', 'interior_wall*.glb')) + glob.glob(os.path.join(pasta, 'pieces', '*.glb'))):
        sc = trimesh.load(f, force='scene', process=False)
        for n in sc.graph.nodes_geometry:
            m = sc.geometry[sc.graph[n][1]]
            if n != NO and getattr(m.visual.material, 'name', '') == 'trim': return m.visual.material
    raise SystemExit('kit sem material trim: ' + pasta)


def kit(pasta, teto):
    mat = material_trim(pasta); tot = 0
    for f in sorted(glob.glob(os.path.join(pasta, 'pieces', '*.glb'))):
        nome = os.path.basename(f)[:-4]
        if any(t in nome for t in FORA): continue
        n = moldurar(f, teto, mat)
        if n: print(f'  {nome}: {n} triângulos de moldura'); tot += n
    print(f'{os.path.basename(pasta)}: {tot} triângulos')


if __name__ == '__main__':
    a = sys.argv[1:]; teto = 2.8
    if '--teto' in a: i = a.index('--teto'); teto = float(a[i + 1]); del a[i:i + 2]
    for p in a: kit(p.rstrip('/'), teto)
