"""Gera a mesa de recarga de munição: modelo, UVs, bake das texturas e o GLB do jogo
(props/mobilias/bancada_municao.glb), e atualiza o registro em props/mobilias/catalogo.json.

uso: python3 gerar.py [resolução] [saída]        (precisa de: pip install bpy pillow numpy)
REASSAR=A,B força os grupos listados. Grupos: A estrutura e tampo, B prensa, balança e cápsulas,
C latas, caixas, chumbo, luminária, prateleira, caixote e balde."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

ID = 'bancada_municao'
PROPS = os.path.dirname(os.path.dirname(AQUI))
CFG = dict(nome=ID, montar=modelo.montar, origem=(0, 0, 0))
TAMANHO = {'A': 2048, 'B': 1024, 'C': 1024}        # textura de cada grupo dentro do GLB


def main(res=2048, saida=os.path.join(AQUI, 'saida')):
    fabrica.gerar(CFG, res, saida)
    tex = os.path.join(saida, 'tex_glb')
    os.makedirs(tex, exist_ok=True)
    for f in os.listdir(os.path.join(saida, 'tex')):
        g = f.split('_')[-2]
        im = Image.open(os.path.join(saida, 'tex', f))
        t = min(TAMANHO.get(g, res), im.width)
        (im.resize((t, t), Image.LANCZOS) if t != im.width else im).save(os.path.join(tex, f))
    arq = os.path.join(PROPS, 'mobilias', f'{ID}.glb')
    empacotar.main(os.path.join(saida, f'{ID}_sem_tex.glb'), tex, arq, 'webp')
    tam, tris = fabrica.medir(arq)
    arq_cat = os.path.join(PROPS, 'mobilias', 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    r = next(x for x in cat['itens'] if x['id'] == ID)
    r.update(tamanho_m=tam, triangulos=tris, kb=round(os.path.getsize(arq) / 1024, 1),
             gerador='moveis_realistas/bancada_municao/gerar.py', ponto_uso=[0.0, 0.0, 0.65])
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{ID} {tris} tris {r['kb']} KB {tam}")


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2048, *sys.argv[2:3])
