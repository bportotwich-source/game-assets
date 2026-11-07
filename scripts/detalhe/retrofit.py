"""Leva um kit antigo para o alto detalhe sem reescrever o gerador inteiro.

No gerar_kit.py do kit, logo antes de montar o dicionario `pieces`, chame:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe'))
    import retrofit; retrofit.aplicar(globals(), {'brick': 'brick', 'siding': 'siding', 'sign': None, ...}, tabuas=0.14)

O que muda:
  - materiais: as texturas viram PBR (cor + normal + ORM, ladrilho de 2 m) pelo tipo indicado; None mantem a textura antiga
    (letreiros, xadrez...) com a UV antiga. As cores do kit (COL) continuam as mesmas.
  - window(): caixilho com batente, 2 folhas de guilhotina com baguetes, vidro, peitoril com nariz e pingadeira.
    Mesmo volume da janela antiga (o peitoril e a verga ficam no mesmo lugar), para nao criar sobreposicoes novas.
  - door_leaf(): porta com almofadas rebaixadas e chanfradas (Blender), vidro com baguetes se tiver vidro, macaneta e dobradicas.
  - wall_with_opening() com material de tabuas: tabuas sobrepostas em geometria a partir de `tabuas` (m), com buracos nos vaos.
  - Piece ganha cham/prof e exporta pela biblioteca; depois de exportar, chame retrofit.finalizar(pasta) para trocar PNG por JPEG.
"""
import os, sys, glob, math
import numpy as np, trimesh
from trimesh.visual import TextureVisuals
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detalhe as D

def aplicar(g, tipos, tabuas=None, tabuas_mats=None, portas=True, janelas=True, cores=None):
    old_TEX, old_MATS, old_Piece = dict(g.get('TEX', {})), dict(g.get('MATS', {})), g['Piece']
    base = {k: v for k, v in g['COL'].items()}; base.update(cores or {}); cores = base   # cores: troca a cor-base de um material texturizado
    D.configurar(cores=cores, texturas={k: t for k, t in tipos.items() if t})
    kept = {k: old_TEX[k] for k, t in tipos.items() if not t and k in old_TEX}
    for k in kept: D.MATS[k] = old_MATS[k]
    for k, m in old_MATS.items():          # materiais que so o kit tem (cores especiais) continuam
        if k not in D.MATS: D.MATS[k] = m
    SIGN = g.get('SIGN', (0, 0, 1, 1))

    class Piece(D.Piece, old_Piece):
        def __init__(s): D.Piece.__init__(s)
        def scene(s, name):
            sc = trimesh.Scene()
            for k, ms in s.parts.items():
                m = trimesh.util.concatenate(ms); m.unmerge_vertices()
                if k in kept:                       # textura antiga, UV antiga
                    v = m.vertices; n = np.repeat(m.face_normals, 3, axis=0); uv = np.zeros((len(v), 2)); ax = np.argmax(np.abs(n), axis=1)
                    uv[ax == 0] = v[ax == 0][:, [2, 1]]; uv[ax == 2] = v[ax == 2][:, [0, 1]]; uv[ax == 1] = v[ax == 1][:, [0, 2]]
                    tw, th = kept[k][1], kept[k][2]; uv[:, 0] /= tw; uv[ax != 1, 1] /= th; uv[ax == 1, 1] /= tw
                    if k == 'sign': uv = np.stack([(v[:, 0] - SIGN[0]) / SIGN[2], (v[:, 1] - SIGN[1]) / SIGN[3]], 1)
                    m.visual = TextureVisuals(uv=uv, material=D.MATS[k]); sc.add_geometry(m, node_name=f'{name}_{k}', geom_name=f'{name}_{k}')
                else:
                    q = D.Piece(); q.parts = {k: [m]}; q.uv = s.uv
                    for nm, gg in q.scene(name).geometry.items(): sc.add_geometry(gg, node_name=nm, geom_name=nm)
            return sc
    g['Piece'] = Piece; g['MATS'] = D.MATS
    g['TEX'] = dict(D.TEX); g['TEX'].update(kept)
    for nm in ('prof_x', 'prof_y', 'prof_z', 'crect', 'arc', 'bl_detail', 'tbox', 'sash', 'board', 'siding_field', 'gutter_run', 'gutter_profile', 'downspout', 'baseboard', 'door_casing'):
        g.setdefault(nm, getattr(D, nm))

    if janelas:
        old_window = g['window']
        def window(p, ow, oy0, oy1, lintel='trim', mull=True, sill_top=None, glass=True, **kw):
            if not glass or sill_top is not None or oy1 - oy0 < 0.5 or ow < 0.35 or ow > 1.5:   # vitrines e janelas largas ficam como eram
                return old_window(p, ow, oy0, oy1, lintel=lintel, mull=mull, sill_top=sill_top, glass=glass, **kw)
            x = ow / 2; f = 0.05
            p.box('frame', -x, -x + f, oy0, oy1, -0.2, -0.04); p.box('frame', x - f, x, oy0, oy1, -0.2, -0.04); p.box('frame', -x, x, oy1 - f, oy1, -0.2, -0.04)
            tall = oy1 - oy0 > 1.0
            if tall:   # guilhotina
                mid = oy0 + 0.02 + (oy1 - f - oy0 - 0.02) * 0.5
                p.box('frame', -x + f, -x + f + 0.012, oy0 + 0.02, oy1 - f, -0.105, -0.095); p.box('frame', x - f - 0.012, x - f, oy0 + 0.02, oy1 - f, -0.105, -0.095)
                D.sash(p, -x + f, x - f, oy0 + 0.025, mid + 0.02, -0.15, -0.11, 1, 0.075)
                D.sash(p, -x + f + 0.012, x - f - 0.012, mid - 0.02, oy1 - f, -0.09, -0.05, (3 if ow >= 0.85 else 2) if mull else 1, 0.05)
            else:      # janela baixa (basculante/fixa): uma folha com baguetes
                D.sash(p, -x + f, x - f, oy0 + 0.025, oy1 - f, -0.13, -0.08, (3 if ow >= 0.85 else 2) if mull else 1, 0.06)
            st = oy0 + 0.015
            p.box('trim', -x + f, x - f, st - 0.03, st, -0.2, 0.0)
            # peitoril no mesmo volume do antigo (x +-0.08, st-0.08..st, z -0.05..0.08), agora com caimento e pingadeira
            D.prof_x(p, 'trim', -x - 0.08, x + 0.08, [(-0.05, st - 0.08), (0.06, st - 0.08), (0.08, st - 0.07), (0.08, st - 0.05), (0.065, st - 0.035), (0.0, st - 0.01), (-0.05, st - 0.01)])
            if lintel: p.cham(lintel, -x - 0.06, x + 0.06, oy1 + 0.01, oy1 + 0.15, -0.02, 0.04, 0.008)
        g['window'] = window

    if portas:
        def door_leaf(w=0.96, h=2.32, glass=True, mat='door', **kw):
            p = Piece(); t = 0.05; slab = D.tbox(0, w, 0, h, -t / 2, t / 2); cut = []
            m = 0.12 * (w / 0.94); y_top = h - 0.13
            if glass:
                gy0 = h * 0.62; cut.append(D.tbox(m, w - m, gy0, y_top, -t, t))
                panels = [(0.18, gy0 - 0.14)]
            else:
                n = 5 if mat in ('frame', 'door_int', 'trim') else 3
                step = (h - 0.32) / n; panels = [(0.16 + i * step + 0.02, 0.16 + (i + 1) * step - 0.02) for i in range(n)]
            for (a, b) in panels:
                for z in (t / 2, -t / 2): cut.append(D.tbox(m, w - m, a, b, z - 0.01, z + 0.01))
            p.add(mat, D.bl_detail(slab, cut, bevel=0.004, segments=1 if not glass else 2))
            if glass:
                p.box('glass', m - 0.004, w - m + 0.004, gy0 - 0.004, y_top + 0.004, -0.004, 0.004)
                p.cham(mat, w / 2 - 0.013, w / 2 + 0.013, gy0, y_top, -0.013, 0.013, 0.004)
                p.cham(mat, m, w - m, (gy0 + y_top) / 2 - 0.013, (gy0 + y_top) / 2 + 0.013, -0.013, 0.013, 0.004)
            for z in (1, -1):
                p.cham('brass' if 'brass' in D.MATS else 'metal', w - 0.12, w - 0.07, 0.9, 1.1, z * t / 2 - 0.005 * (z < 0), z * t / 2 + 0.005 * (z > 0), 0.004)
                p.sphere('brass' if 'brass' in D.MATS else 'metal', 0.028, w - 0.095, 1.0, z * (t / 2 + 0.05))
                p.seg('brass' if 'brass' in D.MATS else 'metal', (w - 0.095, 1.0, z * t / 2), (w - 0.095, 1.0, z * (t / 2 + 0.04)), 0.015)
            for yy in (0.25, h - 0.35): p.cyl('brass' if 'brass' in D.MATS else 'metal', 0.008, yy, yy + 0.1, 0.0, t / 2 + 0.002, 8)
            return p
        g['door_leaf'] = door_leaf

    if tabuas is not None:
        D.configurar_tabuas(tabuas, tabuas + 2.0, 0.2)
        smats = set(tabuas_mats or [k for k, t in tipos.items() if t == 'siding'])
        for k in smats: D.KIND[k] = 'siding'
        old_wwo = g['wall_with_opening']
        def wall_with_opening(p, mat, ow, oy0, oy1, h, inner='plaster', t=None, centered=False, **kw):
            kw2 = dict(kw)
            if t is not None: kw2['t'] = t
            r = old_wwo(p, mat, ow, oy0, oy1, h, inner=inner, centered=centered, **kw2)
            if mat in smats and not centered and h > tabuas + 0.4:
                D.NC = int((h - tabuas) // 0.2)
                holes = [(-ow / 2 - 0.03, ow / 2 + 0.03, min(oy0, oy0 if oy0 > 0.1 else -1.0), oy1 + 0.05)] if ow > 0 else []
                D.siding_field(p, holes, mat=mat)
            return r
        g['wall_with_opening'] = wall_with_opening

def finalizar(pasta):
    """Troca PNG por JPEG em todos os GLB da pasta (pieces/ e o montado)."""
    for f in glob.glob(os.path.join(pasta, '**', '*.glb'), recursive=True): D.glb_jpeg(f)

def montar(pieces, L, caminho):
    """Exporta o predio montado a partir das cenas de cada peca (mantem as UVs proprias de cada peca, como a fase das tabuas),
    juntando tudo por material. Troca PNG por JPEG no fim."""
    bym = {}
    for e in L:
        if e['piece'] == 'player_scale_ref' or e['piece'] not in pieces: continue
        Tm = trimesh.transformations.rotation_matrix(math.radians(e['rotY']), [0, 1, 0]); Tm[:3, 3] = e['pos']
        for nm, gg in pieces[e['piece']].scene(e['piece']).geometry.items():
            gg = gg.copy(); gg.apply_transform(Tm); bym.setdefault(gg.visual.material.name, []).append(gg)
    sc = trimesh.Scene()
    for k, gs in bym.items():
        m = trimesh.util.concatenate(gs); m.visual.material = D.MATS.get(k, gs[0].visual.material)
        sc.add_geometry(m, node_name=f'building_{k}', geom_name=f'building_{k}')
    sc.export(caminho, include_normals=True); D.glb_jpeg(caminho)
    return sum(len(gg.faces) for gg in sc.geometry.values())
