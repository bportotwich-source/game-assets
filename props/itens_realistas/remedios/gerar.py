"""Gera os remédios: modelo, UVs, bake das texturas e o GLB do jogo em
props/loot, e atualiza o registro em props/loot/catalogo.json.

uso: python3 gerar.py [forma|todas] [resolução] [saída]     (precisa de: pip install bpy pillow numpy)
REASSAR=A força o bake de novo."""
import sys, os, json, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.join(AQUI, '..', '..', 'moveis_realistas')]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

PROPS = os.path.dirname(os.path.dirname(AQUI))
GERADOR = 'itens_realistas/remedios/gerar.py'
TEXTURA = {'kit_medico': 1024, 'frasco_remedio': 512, 'atadura': 512, 'seringa': 512, 'kit_costura': 1024, 'alcool': 512,
           'curativo_improvisado': 512, 'tala_improvisada': 1024, 'ervas': 512, 'remedio_ervas': 512}   # lado da textura no GLB
ESTADO_DE = {'remedio_ervas': ('frasco_remedio', 'ervas')}
SO_GLB = {'ervas'}                      # item que só existe no jogo (itens_extra.json): grava o GLB, sem registro no catálogo


def medir(arq):
    """Tamanho (m) e triângulos do GLB."""
    j, _ = empacotar.ler_glb(arq)
    mn, mx = [1e9] * 3, [-1e9] * 3

    def andar(i, base_):
        n = j['nodes'][i]
        t = [a + b for a, b in zip(base_, n.get('translation', [0, 0, 0]))]
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
    tris = sum(j['accessors'][p['indices']]['count'] // 3 for m in j['meshes'] for p in m['primitives'])
    return [round(b - a, 3) for a, b in zip(mn, mx)], tris


def gerar(forma, res=1024, saida=os.path.join(AQUI, 'saida')):
    pasta = os.path.join(saida, forma)
    fabrica.gerar(dict(nome=forma, montar=modelo.FORMAS[forma], origem=(0, 0, 0)), res, pasta)
    tex = os.path.join(pasta, 'tex_glb')
    os.makedirs(tex, exist_ok=True)
    lado = TEXTURA.get(forma, 512)
    for f in os.listdir(os.path.join(pasta, 'tex')):
        im = Image.open(os.path.join(pasta, 'tex', f))
        (im.resize((lado, lado), Image.LANCZOS) if im.width > lado else im).save(os.path.join(tex, f))
    arq = os.path.join(PROPS, 'loot', f'{forma}.glb')
    empacotar.main(os.path.join(pasta, f'{forma}_sem_tex.glb'), tex, arq, 'webp')
    tam, tris = medir(arq)
    arq_cat = os.path.join(PROPS, 'loot', 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    if forma in SO_GLB:
        print(f"{forma} {tris} tris {round(os.path.getsize(arq) / 1024, 1)} KB {tam}")
        return
    if forma in ESTADO_DE:              # o mesmo item em outro estado: entra em "estados" do item de origem, não é item de saque
        dono, nome = ESTADO_DE[forma]
        r = next(x for x in cat['itens'] if x['id'] == dono)
        r.setdefault('estados', {})[nome] = f'loot/{forma}.glb'
        r = dict(kb=round(os.path.getsize(arq) / 1024, 1))
    else:
        r = next(x for x in cat['itens'] if x['id'] == forma)
        r.update(tamanho_m=tam, triangulos=tris, kb=round(os.path.getsize(arq) / 1024, 1), gerador=GERADOR)
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{forma} {tris} tris {r['kb']} KB {tam}")


if __name__ == '__main__':
    qual = sys.argv[1] if len(sys.argv) > 1 else 'todas'
    if qual == 'todas':                 # uma forma por processo (cada bake começa de um Blender limpo)
        for f in modelo.FORMAS:
            subprocess.run([sys.executable, os.path.abspath(__file__), f] + sys.argv[2:4], check=True)
    else:
        gerar(qual, int(sys.argv[2]) if len(sys.argv) > 2 else 1024, *sys.argv[3:4])
