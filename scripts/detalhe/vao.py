"""Vao da janela rebocado por dentro.

A parede dos kits e uma grade: camada interna de reboco (2 cm) e o resto da espessura com o material de fora
(tabua, tijolo...). Nas faces do vao (ombreiras, peitoril e verga) o material de fora ia ate a face interna, entao
de dentro de casa aparecia um friso de tabua verde/tijolo entre o reboco e o marco da janela.

Este script corta cada face do vao no plano de tras do marco (o ponto mais interno do caixilho, do peitoril
interno etc.) e passa a parte de dentro para 'plaster' (UV em metros / 2, como o resto do reboco). A parte de fora,
escondida pelo marco e pela guarnicao, fica como estava. So mexe nas pecas *win* das pastas dadas; mantem os nos
'folha' das janelas. Rodar de novo nao muda nada.

Uso:  python3 scripts/detalhe/vao.py kits/bangalo kits/three-flats ...
"""
import os, sys, glob
import numpy as np, trimesh
from trimesh.intersections import slice_faces_plane
from trimesh.visual import TextureVisuals

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FIXOS = {'plaster', 'glass', 'gglass', 'jal', 'glass_f', 'frost', 'mirror'}


def _faces_vao(m, lim):
    v = m.vertices[m.faces]; fn = m.face_normals; c = v.mean(1)
    zmin, zmax = v[..., 2].min(1), v[..., 2].max(1)
    lateral = (np.abs(fn[:, 0]) > 0.99) | (np.abs(fn[:, 1]) > 0.99)
    return np.nonzero(lateral & (zmax - zmin > 0.1) & (zmax <= 0.001) & (zmax >= -0.003) & (np.abs(c[:, 0]) < lim)
                      & (c[:, 1] > max(v[..., 1].min() + 0.02, 0.05)))[0]


def _uv(v, n):
    if abs(n[0]) > 0.5: return np.c_[v[:, 2], v[:, 1]] / 2
    return np.c_[v[:, 0], v[:, 2]] / 2


def rebocar(path):
    sc = trimesh.load(path, force='scene', process=False)
    raiz = {}
    for n in sc.graph.nodes_geometry:
        T, g = sc.graph[n]
        if np.allclose(T, np.eye(4)): raiz[sc.geometry[g].visual.material.name] = g
    if 'plaster' not in raiz: return 0
    lim = max(abs(sc.bounds[:, 0]).max() - 0.02, 0.3)
    # vao: faces fundas do material de fora; plano: o ponto mais de dentro das pecas do vao
    cand = {mat: _faces_vao(sc.geometry[g], lim) for mat, g in raiz.items() if mat not in FIXOS}
    cand = {k: v for k, v in cand.items() if len(v)}
    if not cand: return 0
    pts = np.vstack([sc.geometry[raiz[k]].vertices[sc.geometry[raiz[k]].faces[f]].reshape(-1, 3) for k, f in cand.items()])
    x0, x1, y0, y1 = pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max()
    zf = None
    for n in sc.graph.nodes_geometry:
        T, g = sc.graph[n]; m = sc.geometry[g]
        if m.visual.material.name in FIXOS or m.visual.material.name in cand: continue
        v = trimesh.transform_points(m.vertices, T)
        dentro = v[(v[:, 0] > x0 - 0.01) & (v[:, 0] < x1 + 0.01) & (v[:, 1] > y0 - 0.01) & (v[:, 1] < y1 + 0.01)]
        if len(dentro): zf = dentro[:, 2].min() if zf is None else min(zf, dentro[:, 2].min())
    if zf is None: return 0
    pl = sc.geometry[raiz['plaster']]; novos_v, novos_f, novos_uv = [], [], []; mud = 0
    for mat, fs in cand.items():
        m = sc.geometry[raiz[mat]]; v = m.vertices[m.faces]
        fs = fs[v[fs, :, 2].min(1) < zf - 0.003]
        if not len(fs): continue
        sub = trimesh.Trimesh(m.vertices, m.faces[fs], process=False)
        # parte de fora (z >= zf) fica com o material; parte de dentro vira reboco
        fora_v, fora_f = slice_faces_plane(sub.vertices, sub.faces, plane_normal=[0, 0, 1], plane_origin=[0, 0, zf])[:2]
        den_v, den_f = slice_faces_plane(sub.vertices, sub.faces, plane_normal=[0, 0, -1], plane_origin=[0, 0, zf])[:2]
        nrm = trimesh.Trimesh(den_v, den_f, process=False).face_normals
        for f, nn in zip(den_f, nrm):
            b = sum(len(x) for x in novos_v); vv = den_v[f]
            novos_v.append(vv); novos_f.append(np.arange(3) + b); novos_uv.append(_uv(vv, nn))
        # refaz a malha do material de fora sem as faces cortadas, mais a parte de fora com UV interpolado da original
        keep = np.setdiff1d(np.arange(len(m.faces)), fs)
        fora = trimesh.Trimesh(fora_v, fora_f, process=False)
        muv = getattr(m.visual, 'uv', None)
        nm = trimesh.Trimesh(np.vstack([m.vertices, fora.vertices]), np.vstack([m.faces[keep], fora.faces + len(m.vertices)]), process=False)
        if muv is not None:
            fuv = _uv_interp(m.vertices[m.faces[fs]], muv[m.faces[fs]], sub.face_normals, fora)
            nm.visual = TextureVisuals(uv=np.vstack([muv, fuv]), material=m.visual.material)
        else:
            nm.visual = TextureVisuals(material=m.visual.material)
        sc.geometry[raiz[mat]] = nm; mud += len(fs)
    if not mud: return 0
    nv = np.vstack(novos_v); nf = np.vstack(novos_f) + len(pl.vertices)
    p2 = trimesh.Trimesh(np.vstack([pl.vertices, nv]), np.vstack([pl.faces, nf]), process=False)
    puv = getattr(pl.visual, 'uv', None)
    p2.visual = TextureVisuals(uv=None if puv is None else np.vstack([puv, np.vstack(novos_uv)]), material=pl.visual.material)
    sc.geometry[raiz['plaster']] = p2
    sc.export(path, include_normals=True)
    from detalhe import glb_jpeg
    glb_jpeg(path)
    return mud


def _uv_interp(tri, tuv, fnorm, fora):
    """UV dos vertices cortados: interpola na face original que contem o ponto (as faces do vao sao planas)."""
    uv = np.zeros((len(fora.vertices), 2))
    for i, p in enumerate(fora.vertices):
        bc = trimesh.triangles.points_to_barycentric(tri, np.repeat(p[None], len(tri), 0))
        d = np.abs(np.einsum('ij,ij->i', fnorm, p - tri[:, 0]))
        j = np.argmin(np.where(np.all(bc > -1e-4, axis=1), d, 1e9))
        uv[i] = bc[j] @ tuv[j]
    return uv


if __name__ == '__main__':
    for a in sys.argv[1:]:
        n = 0
        for f in sorted(glob.glob(os.path.join(a.rstrip('/'), 'pieces', '*.glb'))):
            if 'win' in os.path.basename(f): n += bool(rebocar(f))
        print(a, n, 'pecas com o vao rebocado por dentro')
