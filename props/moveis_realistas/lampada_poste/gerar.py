"""Gera a lâmpada improvisada no poste: modelo, UVs, bake das texturas e o GLB do jogo
(props/mobilias/lampada_poste.glb), e cria ou atualiza o registro em props/mobilias/catalogo.json
(receita, energia, medidas e "gerador", para o gerar_props.py não o refazer).

uso: python3 gerar.py [resolução] [saída]        (precisa de: pip install bpy pillow numpy)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo;
REASSAR=A,B força os grupos listados. Grupos: A tudo."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

ID = 'lampada_poste'
PROPS = os.path.dirname(os.path.dirname(AQUI))
CFG = dict(nome=ID, montar=modelo.montar, origem=(0, 0, 0))
TAMANHO = {'A': 1024}        # textura de cada grupo dentro do GLB

# O que o jogo lê (ver props/CRAFT.md e, no Recomeço, jogo/sistemas/energia.gd).
# Luz que o jogador põe onde quiser na base: 60 W, acende só com energia na rede.
REGISTRO = dict(
    nome='Lâmpada improvisada no poste', grupo='mobilias', categoria='energia', montagem='floor', lote=20,
    comodos=['abrigo', 'rua'], fase=3, usa='energia', consumo_w=60, luz_m=8,
    ponto_luz=[c / 1000 for c in modelo.LUZ], colisao='nenhuma',
    constroi={'tabua': 2, 'fio_eletrico': 1, 'lata_vazia': 1, 'fita_adesiva': 1}, ferramenta='martelo',
    estacao='iluminação (acende 8 m em volta enquanto a rede da base tem energia)')


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
    r = next((x for x in cat['itens'] if x['id'] == ID), None)
    if r is None:
        r = dict(id=ID)
        cat['itens'].append(r)
    r.update(REGISTRO)
    r.update(arquivo=f'mobilias/{ID}.glb', tamanho_m=tam, triangulos=tris, kb=round(os.path.getsize(arq) / 1024, 1),
             gerador=f'moveis_realistas/{ID}/gerar.py')
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{ID} {tris} tris {r['kb']} KB {tam}")


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2048, *sys.argv[2:3])
