"""Gera os móveis de quarto (cômoda, criado-mudo, guarda-roupa): modelo, UVs, bake das texturas e o GLB do jogo
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
GERADOR = 'moveis_realistas/quarto/gerar.py'
# lado da textura de cada grupo dentro do GLB
TEXTURA = {'comoda': {'A': 2048, 'B': 1024}, 'criado_mudo': {'A': 1024}, 'guarda_roupa': {'A': 2048, 'B': 1024, 'C': 2048}}
NOME = {'comoda': 'Cômoda de 3 gavetas', 'criado_mudo': 'Criado-mudo', 'guarda_roupa': 'Guarda-roupa de 2 portas'}
PARTES = {
    'comoda': [dict(no=f'gaveta_{i}', origem=[0, 0, 0], tipo='gaveta', desliza=[0, 0, 0.3]) for i in (1, 2, 3)],
    'criado_mudo': [dict(no='gaveta', origem=[0, 0, 0], tipo='gaveta', desliza=[0, 0, 0.26])],
    'guarda_roupa': [dict(no='porta_esq', origem=[-0.5, 0, 0.292], tipo='porta', eixo='y', abre_graus=-105),
                     dict(no='porta_dir', origem=[0.5, 0, 0.292], tipo='porta', eixo='y', abre_graus=105),
                     dict(no='gaveta', origem=[0, 0, 0], tipo='gaveta', desliza=[0, 0, 0.4])],
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
    r.update(nome=NOME[forma], tamanho_m=tam, triangulos=tris, kb=round(os.path.getsize(arq) / 1024, 1), gerador=GERADOR, partes=PARTES[forma])
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{forma} {tris} tris {r['kb']} KB {tam}")


if __name__ == '__main__':
    qual = sys.argv[1] if len(sys.argv) > 1 else 'todas'
    if qual == 'todas':                 # uma forma por processo (cada bake começa de um Blender limpo)
        for f in modelo.FORMAS:
            subprocess.run([sys.executable, os.path.abspath(__file__), f] + sys.argv[2:4], check=True)
    else:
        gerar(qual, int(sys.argv[2]) if len(sys.argv) > 2 else 2048, *sys.argv[3:4])
