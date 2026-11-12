"""Gera o baú de aço: modelo, UVs, bake das texturas e o GLB do jogo
(props/mobilias/bau_aco.glb), e cria ou atualiza o registro em props/mobilias/catalogo.json
(receita, grade, medidas e "gerador", para o gerar_props.py não o refazer).

uso: python3 gerar.py [resolução] [saída]        (precisa de: pip install bpy pillow numpy)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo;
REASSAR=A,B força os grupos listados. Grupos: A chapas onduladas e fundo, B armação e tampa, C ferragens."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

ID = 'bau_aco'
PROPS = os.path.dirname(os.path.dirname(AQUI))
CFG = dict(nome=ID, montar=modelo.montar, origem=(0, 0, 0))
TAMANHO = {'A': 2048, 'B': 2048, 'C': 1024}        # textura de cada grupo dentro do GLB

# O que o jogo lê (ver props/CRAFT.md): a maior caixa de guardar, com uma grade só de 12 × 8
# (maior que o baú da van). Feita na forja de tambor, com chapa, cano, dobradiças e o cadeado.
REGISTRO = dict(
    nome='Baú de aço com cadeado', grupo='mobilias', categoria='armazenamento', montagem='floor', lote=20,
    comodos=['abrigo', 'armazem', 'garagem', 'quartel', 'fabrica'],
    conteiner=True, slots=48, grade=[12, 8], saque=['ferramentas', 'materiais', 'armas', 'municao'], aceita=[],
    barricada=True, fase=2, constroi={'chapa_metal': 4, 'cano_metal': 2, 'dobradicas': 1, 'corrente_cadeado': 1},
    ferramenta='martelo', estacao_obra='forja_tambor',
    estacao='estoque grande da base (96 espaços; o que está dentro conta nas receitas quando a base é sua)')


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
    m = modelo
    r.update(REGISTRO)
    r.update(arquivo=f'mobilias/{ID}.glb', tamanho_m=tam, triangulos=tris, kb=round(os.path.getsize(arq) / 1024, 1),
             gerador=f'moveis_realistas/{ID}/gerar.py',
             partes=[dict(no='tampa', origem=[0, (m.Y1 + 2) / 1000, m.EIXO_Z / 1000], tipo='tampa', eixo='x', abre_graus=-100)])
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{ID} {tris} tris {r['kb']} KB {tam}")


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2048, *sys.argv[2:3])
