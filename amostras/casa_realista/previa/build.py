import sys, os, json, struct, shutil, glob
from PIL import Image
SRC = sys.argv[1]; OUT = sys.argv[2]; REPO = '/home/user/game-assets'
os.makedirs(OUT + '/novo', exist_ok=True); os.makedirs(OUT + '/atual', exist_ok=True)
shutil.copy(SRC + '/casa_sem_tex.glb', OUT + '/novo/casa.glb')
def glb_json(p):
    d = open(p, 'rb').read(); n = struct.unpack('<I', d[12:16])[0]; return json.loads(d[20:20 + n])
res = {}; disco = 0; vram = 0
for f in sorted(glob.glob(SRC + '/tex/casa_*_cor.png')):
    g = os.path.basename(f).split('_')[1]
    im = Image.open(f); r = im.width; res[g] = r; alfa = im.mode == 'RGBA'
    vram += r * r * ((1.0 if alfa else 0.5) + 1.0 + 0.5) * 4 / 3
    for t in sorted({r, min(r, 2048), min(r, 1024)}):
        os.makedirs(f'{OUT}/tex/{t}', exist_ok=True)
        for tipo, q in (('cor', 88), ('orm', 86), ('normal', 92)):
            dst = f'{OUT}/tex/{t}/casa_{g}_{tipo}.webp'
            src = f'{SRC}/tex/casa_{g}_{tipo}.png'
            if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
                i2 = Image.open(src)
                if t != r: i2 = i2.resize((t, t), Image.LANCZOS)
                i2.save(dst, 'WEBP', quality=q, method=4)
            if t == r: disco += os.path.getsize(dst)
LADR = sys.argv[3] if len(sys.argv) > 3 else None
v_lad = 0
if LADR:
    os.makedirs(OUT + '/tex/lad', exist_ok=True)
    for f in sorted(glob.glob(LADR + '/*_cor.png')):
        n = os.path.basename(f)[:-8]; r = Image.open(f).width; v_lad += r * r * 2.0 * 4 / 3
        for tipo, q in (('cor', 88), ('orm', 86), ('normal', 92)):
            Image.open(f'{LADR}/{n}_{tipo}.png').save(f'{OUT}/tex/lad/{n}_{tipo}.webp', 'WEBP', quality=q, method=4)
print('VRAM ladrilhos MB', v_lad / 1048576)
pecas = json.load(open(SRC + '/pecas.json'))
j = glb_json(OUT + '/novo/casa.glb')
prims = {n['name']: len(j['meshes'][n['mesh']]['primitives']) for n in j['nodes'] if 'mesh' in n}
A = {'wall_siding_window': 'kits/bangalo/pieces', 'wall_siding_door': 'kits/bangalo/pieces', 'door_leaf_front': 'kits/bangalo/pieces', 'floor_tile': 'kits/bangalo/pieces',
     'interior_wall_plain': 'kits/bangalo/pieces', 'comoda': 'props/mobilias', 'lampiao': 'props/mobilias', 'lata_feijao': 'props/loot'}
old = {}
for k, d in A.items():
    p = f'{REPO}/{d}/{k}.glb'; shutil.copy(p, f'{OUT}/atual/{k}.glb'); jj = glb_json(p)
    tr = 0
    for m in jj['meshes']:
        for pr in m['primitives']:
            tr += jj['accessors'][pr['indices']]['count'] // 3
    old[k] = (tr, sum(len(m['primitives']) for m in jj['meshes']))
def novo(*ns): return sum(pecas[n]['tris'] for n in ns), sum(prims[n] for n in ns)
px = lambda g: f'{res[g]} px'
linhas = [('Parede com janela (2 m)', old['wall_siding_window'], novo('parede_janela', 'janela_folha'), px('A')),
          ('Parede com porta (2 m)', old['wall_siding_door'], novo('parede_porta'), px('B')),
          ('Porta da frente', old['door_leaf_front'], novo('porta_frente'), f'{res["C"]} px, com a folha da janela'),
          ('Piso (4 módulos de 2 m)', tuple(4 * x for x in old['floor_tile']), novo('piso_1', 'piso_2', 'piso_3', 'piso_4'), px('D')),
          ('Parede interna (2 módulos)', tuple(2 * x for x in old['interior_wall_plain']), novo('parede_interna_1', 'parede_interna_2'), px('E')),
          ('Cômoda com 3 gavetas', old['comoda'], novo('comoda', 'gaveta_1', 'gaveta_2', 'gaveta_3'), px('F')),
          ('Lampião', old['lampiao'], novo('lampiao'), f'{res["G"]} px, com a lata'),
          ('Lata de feijão', old['lata_feijao'], novo('lata_feijao'), '')]
tab = [dict(nome=n, tris_a=a[0], mat_a=a[1], tris_n=b[0], mat_n=b[1], tex=t) for (n, a, b, t) in linhas]
tab.append(dict(nome='Amostra inteira', tris_a=sum(r['tris_a'] for r in tab), mat_a=sum(r['mat_a'] for r in tab), tris_n=sum(r['tris_n'] for r in tab), mat_n=sum(r['mat_n'] for r in tab), tex=f'{len(res)} conjuntos'))
# texturas de hoje: as do kit inteiro (compartilhadas)
v_old = 0
for f in glob.glob(REPO + '/kits/bangalo/*_albedo.png'):
    r = Image.open(f).width; v_old += r * r * 2.0 * 4 / 3
mb = lambda b: f'{b / 1048576:.0f} MB'
conta = [(mb(vram), 'de memória de vídeo só para esta amostra, contra ' + f'{v_old / 1048576:.1f}'.replace('.', ',') + ' MB das texturas da casa inteira hoje'),
         (mb(disco), 'a mais no instalador, só para estes 4 m de fachada, o canto de sala e os 3 objetos'),
         (f'{tab[-1]["tris_n"] / tab[-1]["tris_a"]:.1f}×', 'os triângulos: ' + f'{tab[-1]["tris_a"]:,}'.replace(',', '.') + ' hoje, ' + f'{tab[-1]["tris_n"]:,}'.replace(',', '.') + ' na versão realista'),
         (f'{tab[-1]["mat_a"]} → {tab[-1]["mat_n"]}', 'chamadas de desenho da amostra: cai, porque cada peça usa um conjunto só de texturas')]
atual = [dict(arq='wall_siding_window.glb', pos=[[-1, 0, 0]]), dict(arq='wall_siding_door.glb', pos=[[1, 0, 0]]), dict(arq='door_leaf_front.glb', pos=[[0.53, 0.015, -0.18]]),
         dict(arq='floor_tile.glb', pos=[[-1, 0, -1.3], [1, 0, -1.3], [-1, 0, -3.3], [1, 0, -3.3]]), dict(arq='interior_wall_plain.glb', pos=[[-1.94, 0, -1.3, 90], [-1.94, 0, -3.3, 90]]),
         dict(arq='comoda.glb', pos=[[-1.63, 0, -1.7, 90]], movel=True), dict(arq='lampiao.glb', pos=[[-1.66, 0.85, -1.45, 20]], movel=True), dict(arq='lata_feijao.glb', pos=[[-1.60, 0.85, -1.92, -55]], movel=True)]
shutil.copy(REPO + '/kits/bangalo/building_assembled.glb', OUT + '/atual/bangalo.glb')
D = dict(res=res, tabela=tab, conta=conta, atual=atual)
h = open(os.path.dirname(os.path.abspath(__file__)) + '/modelo.html').read().replace('/*DADOS*/{}', json.dumps(D, ensure_ascii=False))
open(OUT + '/index.html', 'w').write(h)
print(json.dumps(dict(res=res, conta=conta, tab=tab), ensure_ascii=False, indent=0))
tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print('total', tot // 1024, 'KB', sum(len(fs) for _, _, fs in os.walk(OUT)), 'arquivos')
