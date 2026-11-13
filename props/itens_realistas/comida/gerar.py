"""Gera a comida embalada: modelo, UVs, bake das texturas e o GLB do jogo em
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
GERADOR = 'itens_realistas/comida/gerar.py'
TEXTURA = {'lata_feijao': 512, 'lata_milho': 512, 'lata_sardinha': 512, 'pacote_arroz': 1024, 'caixa_cereal': 1024,
           'caixa_leite': 512, 'salgadinho': 1024, 'barra_chocolate': 512, 'arroz_cozido': 512,
           'saco_farinha': 1024, 'pao_velho': 1024, 'pao_caseiro': 512, 'carne_crua': 1024, 'carne_defumada': 512, 'cesto_legumes': 1024}   # lado da textura no GLB
ESTADO_DE = {'arroz_cozido': ('pacote_arroz', 'cozido')}


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
