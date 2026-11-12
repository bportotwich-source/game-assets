"""Gera os itens de água: modelo, UVs, bake das texturas e os GLBs do jogo em props/loot, um por
estado (vazio, com água suja, com água limpa), e atualiza o registro em props/loot/catalogo.json.

De cada forma sai um bake só. Os estados são o mesmo GLB com a malha "agua" tirada (vazio) ou com
outra cor (suja, limpa). Plástico e vidro saem com material liso transparente; a água, lisa e opaca.

uso: python3 gerar.py [forma|todas] [resolução] [saída]     (precisa de: pip install bpy pillow numpy)
REASSAR=A força o bake de novo."""
import sys, os, json, shutil, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(AQUI, '..', '..', 'moveis_realistas')]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

PROPS = os.path.dirname(os.path.dirname(AQUI))
GERADOR = 'itens_realistas/agua/gerar.py'
TEXTURA = 512                      # lado da textura dentro do GLB (assa maior e reduz)


def _liso(nome, cor, rug, **mais):
    return dict(name=nome, pbrMetallicRoughness=dict(baseColorFactor=cor, metallicFactor=0.0, roughnessFactor=rug), **mais)


TRANSP = dict(alphaMode='BLEND', doubleSided=True)
PET = _liso('pet', [0.80, 0.90, 0.95, 0.20], 0.08, **TRANSP)
PET_AZUL = _liso('pet_azul', [0.30, 0.55, 0.90, 0.30], 0.10, **TRANSP)
VIDRO = _liso('vidro_garrafa', [0.20, 0.42, 0.18, 0.40], 0.06, **TRANSP)
# cores em linear (no jogo ficam mais claras): água limpa azul, água suja marrom turva
LIMPA = _liso('agua_limpa', [0.07, 0.25, 0.42, 1.0], 0.05)
SUJA = _liso('agua_suja', [0.09, 0.06, 0.02, 1.0], 0.30)

# forma: (material da casca, {arquivo: (cor da água ou None para vazio, nós tirados)})
FORMAS = {
    'garrafa_pet':   (PET, {'garrafa_pet': (None, ['agua']), 'garrafa_pet_agua_suja': (SUJA, []), 'garrafa_pet_agua_limpa': (LIMPA, [])}),
    'garrafa_agua':  (PET, {'garrafa_agua': (LIMPA, [])}),
    'galao_agua':    (PET_AZUL, {'galao_agua': (LIMPA, []), 'galao_agua_suja': (SUJA, []), 'galao_vazio': (None, ['agua'])}),
    'garrafa_vidro': (VIDRO, {'garrafa_vidro': (None, ['agua', 'rolha']), 'garrafa_vidro_agua_suja': (SUJA, []), 'garrafa_vidro_agua_limpa': (LIMPA, [])}),
    'cantil':        (None, {'cantil': (None, [])}),
    'caneca_lata':   (None, {'caneca_lata': (None, ['agua']), 'caneca_lata_agua_suja': (SUJA, []), 'caneca_lata_agua_limpa': (LIMPA, [])}),
}


def tirar_nos(arq, nomes):
    """Tira do GLB os nós dados (folhas) e o que só eles usavam: malha, acessores e bytes."""
    j, bin_ = empacotar.ler_glb(arq)
    fica = [i for i, n in enumerate(j['nodes']) if n.get('name') not in nomes]
    assert len(fica) == len(j['nodes']) - len(nomes), (nomes, [n.get('name') for n in j['nodes']])
    novo = {v: k for k, v in enumerate(fica)}
    j['nodes'] = [j['nodes'][i] for i in fica]
    for n in j['nodes']:
        if 'children' in n:
            n['children'] = [novo[c] for c in n['children'] if c in novo]
    for s in j['scenes']:
        s['nodes'] = [novo[c] for c in s['nodes'] if c in novo]
    malhas = sorted({n['mesh'] for n in j['nodes'] if 'mesh' in n})
    nm = {v: k for k, v in enumerate(malhas)}
    j['meshes'] = [j['meshes'][i] for i in malhas]
    for n in j['nodes']:
        if 'mesh' in n:
            n['mesh'] = nm[n['mesh']]
    usados = set()
    for m in j['meshes']:
        for p in m['primitives']:
            usados.update(p['attributes'].values())
            usados.add(p['indices'])
    acc = sorted(usados)
    na = {v: k for k, v in enumerate(acc)}
    j['accessors'] = [j['accessors'][i] for i in acc]
    for m in j['meshes']:
        for p in m['primitives']:
            p['attributes'] = {k: na[v] for k, v in p['attributes'].items()}
            p['indices'] = na[p['indices']]
    vistas = sorted({a['bufferView'] for a in j['accessors']} | {im['bufferView'] for im in j.get('images', []) if 'bufferView' in im})
    nv = {v: k for k, v in enumerate(vistas)}
    saida = bytearray()
    novas = []
    for i in vistas:
        v = dict(j['bufferViews'][i])
        while len(saida) % 4:
            saida.append(0)
        ini = v.get('byteOffset', 0)
        dados = bin_[ini:ini + v['byteLength']]
        v['byteOffset'] = len(saida)
        saida += dados
        novas.append(v)
    j['bufferViews'] = novas
    for a in j['accessors']:
        a['bufferView'] = nv[a['bufferView']]
    for im in j.get('images', []):
        if 'bufferView' in im:
            im['bufferView'] = nv[im['bufferView']]
    empacotar.gravar_glb(arq, j, saida)


def medir(arq):
    """Tamanho (m) e triângulos do GLB, com todas as malhas (as de material liso também)."""
    j, _ = empacotar.ler_glb(arq)
    mn, mx, tris = [1e9] * 3, [-1e9] * 3, 0

    def andar(i, base):
        n = j['nodes'][i]
        t = [a + b for a, b in zip(base, n.get('translation', [0, 0, 0]))]
        if 'mesh' in n:
            for p in j['meshes'][n['mesh']]['primitives']:
                a = j['accessors'][p['attributes']['POSITION']]
                for k in range(3):
                    mn[k] = min(mn[k], a['min'][k] + t[k])
                    mx[k] = max(mx[k], a['max'][k] + t[k])
        for c in n.get('children', []):
            andar(c, t)
    for r in j['scenes'][0]['nodes']:
        andar(r, [0, 0, 0])
    for m in j['meshes']:
        tris += sum(j['accessors'][p['indices']]['count'] // 3 for p in m['primitives'])
    return [round(b - a, 3) for a, b in zip(mn, mx)], tris


def gerar(forma, res=1024, saida=os.path.join(AQUI, 'saida')):
    casca, estados = FORMAS[forma]
    pasta = os.path.join(saida, forma)
    fabrica.gerar(dict(nome=forma, montar=modelo.FORMAS[forma], origem=(0, 0, 0)), res, pasta)
    inteiro = os.path.join(pasta, f'{forma}.glb')
    tex = os.path.join(pasta, 'tex_glb')
    os.makedirs(tex, exist_ok=True)
    for f in os.listdir(os.path.join(pasta, 'tex')):
        im = Image.open(os.path.join(pasta, 'tex', f))
        (im.resize((TEXTURA, TEXTURA), Image.LANCZOS) if im.width > TEXTURA else im).save(os.path.join(tex, f))
    empacotar.main(os.path.join(pasta, f'{forma}_sem_tex.glb'), tex, inteiro, 'webp')
    arq_cat = os.path.join(PROPS, 'loot', 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    r = next(x for x in cat['itens'] if x['id'] == forma)
    extras = {}
    for nome, (agua, fora) in estados.items():
        arq = os.path.join(PROPS, 'loot', f'{nome}.glb')
        shutil.copyfile(inteiro, arq)
        lisos = {'casca': casca} if casca else {}
        if agua:
            lisos['agua'] = agua
        if lisos:
            fabrica.materiais_lisos(arq, lisos)
        tirar_nos(arq, fora)            # também enxuga as UVs que as malhas lisas deixaram de usar
        tam, tris = medir(arq)
        kb = round(os.path.getsize(arq) / 1024, 1)
        print(f'{nome} {tris} tris {kb} KB {tam}')
        if nome == forma:
            r.update(tamanho_m=tam, triangulos=tris, kb=kb, gerador=GERADOR)
        else:
            extras[nome[len(forma) + 1:] if nome.startswith(forma + '_') else nome] = f'loot/{nome}.glb'
    if extras:
        r['estados'] = extras          # o mesmo item em outro estado (o jogo escolhe o GLB pelo que tem dentro)
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    qual = sys.argv[1] if len(sys.argv) > 1 else 'todas'
    if qual == 'todas':                 # uma forma por processo (cada bake começa de um Blender limpo)
        for f in FORMAS:
            subprocess.run([sys.executable, os.path.abspath(__file__), f] + sys.argv[2:4], check=True)
    else:
        gerar(qual, int(sys.argv[2]) if len(sys.argv) > 2 else 1024, *sys.argv[3:4])
