"""Gera os móveis de banheiro (pia de coluna, vaso sanitário, armário com espelho): modelo, UVs, bake das texturas e o GLB do jogo
em props/mobilias, e atualiza o registro em props/mobilias/catalogo.json (medidas, partes que abrem e
"gerador", para o gerar_props.py não os refazer).

uso: python3 gerar.py [forma|todas] [resolução] [saída]     (precisa de: pip install bpy pillow numpy)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo; REASSAR=A,B força.
Depois de mudar o modelo, apague <saída>/<forma> antes de gerar."""
import sys, os, json, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

PROPS = os.path.dirname(os.path.dirname(AQUI))
GERADOR = 'moveis_realistas/banheiro/gerar.py'
# lado da textura de cada grupo dentro do GLB
TEXTURA = {'pia_banheiro': {'A': 1024}, 'vaso_sanitario': {'A': 1024, 'B': 1024}, 'armario_banheiro': {'A': 1024, 'B': 1024}}
NOME = {'pia_banheiro': 'Pia de coluna', 'vaso_sanitario': 'Vaso sanitário com caixa', 'armario_banheiro': 'Armário de banheiro com espelho'}
PARTES = {
    'vaso_sanitario': [{'no': 'assento', 'origem': [0, 0.4, -0.15], 'tipo': 'tampa', 'eixo': 'x', 'abre_graus': -95},
                       {'no': 'tampa_caixa', 'origem': [0, 0.78, 0], 'tipo': 'gaveta', 'desliza': [0, 0.12, 0.04]}],
    'armario_banheiro': [{'no': 'porta_espelho', 'origem': [-0.25, 0, 0.143], 'tipo': 'porta', 'eixo': 'y', 'abre_graus': -100}],
}


def gerar(forma, res=2048, saida=os.path.join(AQUI, 'saida')):
    pasta = os.path.join(saida, forma)
    fabrica.gerar(dict(nome=forma, montar=modelo.FORMAS[forma], origem=(0, 0, 0)), res, pasta)
    tex = os.path.join(pasta, 'tex_glb')
    os.makedirs(tex, exist_ok=True)
    for f in os.listdir(os.path.join(pasta, 'tex')):
        g = f.split('_')[-2]
        im = Image.open(os.path.join(pasta, 'tex', f))
        t = min(TEXTURA[forma].get(g, res), im.width)
        (im.resize((t, t), Image.LANCZOS) if t != im.width else im).save(os.path.join(tex, f))
    arq = os.path.join(PROPS, 'mobilias', f'{forma}.glb')
    empacotar.main(os.path.join(pasta, f'{forma}_sem_tex.glb'), tex, arq, 'webp')
    tam, tris = fabrica.medir(arq)
    arq_cat = os.path.join(PROPS, 'mobilias', 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    r = next(x for x in cat['itens'] if x['id'] == forma)
    r.update(nome=NOME[forma], tamanho_m=tam, triangulos=tris, kb=round(os.path.getsize(arq) / 1024, 1), gerador=GERADOR)
    if forma in PARTES:
        r['partes'] = PARTES[forma]
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{forma} {tris} tris {r['kb']} KB {tam}")


if __name__ == '__main__':
    qual = sys.argv[1] if len(sys.argv) > 1 else 'todas'
    if qual == 'todas':                 # uma forma por processo (cada bake começa de um Blender limpo)
        for f in modelo.FORMAS:
            subprocess.run([sys.executable, os.path.abspath(__file__), f] + sys.argv[2:4], check=True)
    else:
        gerar(qual, int(sys.argv[2]) if len(sys.argv) > 2 else 2048, *sys.argv[3:4])
