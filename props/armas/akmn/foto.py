"""Foto de conferência de uma arma do catálogo montada com acessórios (GLBs do jogo, encaixes do catálogo).
uso: python3 foto.py <arma> <saida.png> [encaixe=acessorio ...] [vista=dir|esq|34|perto]
Sem encaixe=..., monta os padrões do catálogo; encaixe=- tira o padrão."""
import sys, os, json, math
import bpy
from mathutils import Vector, Matrix
ARMAS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat = json.load(open(os.path.join(ARMAS, 'catalogo.json'), encoding='utf-8'))
arma_id, saida = sys.argv[1], sys.argv[2]
args = dict(a.split('=') for a in sys.argv[3:])
vista = args.pop('vista', 'dir')
W = next(x for x in cat['armas'] if x['id'] == arma_id)
AC = {x['id']: x for x in cat['acessorios']}
bpy.ops.wm.read_factory_settings(use_empty=True)
REPOUSO = {}


def importar(arq):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ARMAS, arq))
    novos = [o for o in bpy.data.objects if o not in antes]
    sys.path.insert(0, os.path.join(ARMAS, 'm4a1'))
    import empacotar
    j, _ = empacotar.ler_glb(os.path.join(ARMAS, arq))
    trs = {n.get('name'): n for n in j['nodes']}
    for o in novos:                                    # pose de repouso: TRS dos nós do GLB (o importador deixa uma animação aplicada)
        n = trs.get(o.name)
        if n is None:
            continue
        o.rotation_mode = 'QUATERNION'
        x, y, z = n.get('translation', [0, 0, 0]); qx, qy, qz, qw = n.get('rotation', [0, 0, 0, 1])
        REPOUSO[o] = (Vector((x, -z, y)), (qw, qx, -qz, qy))
    return next(o for o in novos if o.parent is None), novos


raiz, objs = importar(W['arquivo'])
monta = {e['no']: e.get('padrao') for e in W['encaixes'] if 'aceita' in e}
monta.update({k: (None if v == '-' else v) for k, v in args.items()})
nos = {o.name: o for o in objs}
for e in W['encaixes']:
    ac = monta.get(e['no'])
    if not ac:
        continue
    r, novos = importar(AC[ac]['arquivo'])
    r.parent = nos[e['no']]
    r.matrix_parent_inverse = Matrix.Identity(4)
    r.location = (0, 0, 0); r.rotation_mode = 'QUATERNION'; r.rotation_quaternion = (1, 0, 0, 0)
    if e.get('substitui'):
        for o in [nos[e['substitui']]] + list(nos[e['substitui']].children_recursive):
            if o.type == 'MESH' and o not in novos:
                o.hide_render = True
    for o in novos:
        if o.type == 'MESH':
            nos.setdefault(o.name, o)
for o in bpy.data.objects:                             # pose de repouso (sem a animação que o importador deixa ativa)
    if o.animation_data:
        o.animation_data.action = None
for o, (t, q) in REPOUSO.items():
    if o.parent is None or o.parent.name not in [e['no'] for e in W['encaixes']]:
        o.location, o.rotation_quaternion = t, q
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 32; sc.cycles.use_denoising = True
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.75, 0.76, 0.78, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.9
for i, (p, e) in enumerate((((-0.6, 0.4, 0.9), 30), ((0.8, -0.3, 0.6), 18), ((0.2, 0.8, -0.4), 8))):
    l = bpy.data.lights.new(f'l{i}', 'AREA'); l.energy = e; l.size = 0.7
    lo = bpy.data.objects.new(f'l{i}', l); sc.collection.objects.link(lo); lo.location = p
    lo.rotation_euler = (-Vector(p)).to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = 'ORTHO'
sc.view_settings.view_transform = 'Standard'
C = Vector((0, 0.17, 0.02))
V = {'dir': ((2, 0, 0), 1.0, (1800, 800)), 'esq': ((-2, 0, 0), 1.0, (1800, 800)), '34': ((-1.2, 1.3, 0.7), 0.85, (1600, 1000)),
     'perto': ((1.6, -0.6, 0.6), 0.42, (1600, 1100)), 'cima': ((0.001, 0, 2), 1.0, (1800, 700))}
p, s, r = V[vista]
cam.location = Vector(p) + C; cd.ortho_scale = s
cam.rotation_euler = (-Vector(p)).to_track_quat('-Z', 'Y' if vista != 'cima' else 'Y').to_euler()
if vista == 'perto':
    cam.location = Vector(p) + Vector((0, 0.05, 0.06))
sc.render.resolution_x, sc.render.resolution_y = r
sc.render.filepath = saida
bpy.ops.render.render(write_still=True)
