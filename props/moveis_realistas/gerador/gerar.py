"""Gera o gerador portátil a gasolina: modelo, UVs, bake das texturas e o GLB do jogo
(props/mobilias/gerador.glb), e cria ou atualiza o registro em props/mobilias/catalogo.json
(receita, energia, medidas e "gerador", para o gerar_props.py não o refazer).

uso: python3 gerar.py [resolução] [saída]        (precisa de: pip install bpy pillow numpy)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo;
REASSAR=A,B força os grupos listados. Grupos: A quadro e tanque, B motor e painel."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

ID = 'gerador'
PROPS = os.path.dirname(os.path.dirname(AQUI))
CFG = dict(nome=ID, montar=modelo.montar, origem=(0, 0, 0))
TAMANHO = {'A': 1024, 'B': 1024}        # textura de cada grupo dentro do GLB

# O que o jogo lê (ver props/CRAFT.md e, no Recomeço, jogo/sistemas/energia.gd).
# Fonte de energia do degrau 3: 2000 W enquanto tem gasolina (20 L dão 8 h), e o barulho chama zumbis a 35 m.
# Acha-se no mapa (posto, delegacia), leva-se na mochila, ou monta-se na forja.
REGISTRO = dict(
    nome='Gerador portátil a gasolina', grupo='mobilias', categoria='energia', montagem='floor', lote=4,
    comodos=['posto', 'quartel', 'garagem', 'abrigo'], usa='combustivel', peso_kg=45.0, fase=3,
    energia_w=2000, tanque_l=20, litros_h=2.5, ruido_m=35,
    constroi={'motor_eletrico': 1, 'peca_motor': 2, 'chapa_metal': 2, 'cano_metal': 1, 'fio_eletrico': 1},
    ferramenta='chave_inglesa', estacao_obra='forja_tambor',
    estacao='energia (2000 W ligado e com gasolina: 20 L dão 8 h; o barulho chama zumbis de até 35 m)')


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
