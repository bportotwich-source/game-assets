"""Gera o banco de baterias: modelo, UVs, bake das texturas e o GLB do jogo
(props/mobilias/banco_baterias.glb), e cria ou atualiza o registro em props/mobilias/catalogo.json
(receita, energia, medidas e "gerador", para o gerar_props.py não o refazer).

uso: python3 gerar.py [resolução] [saída]        (precisa de: pip install bpy pillow numpy)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo;
REASSAR=A,B força os grupos listados. Grupos: A estante de tábuas, B baterias e quadro."""
import sys, os, json
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

ID = 'banco_baterias'
PROPS = os.path.dirname(os.path.dirname(AQUI))
CFG = dict(nome=ID, montar=modelo.montar, origem=(0, 0, 0))
TAMANHO = {'A': 1024, 'B': 1024}        # textura de cada grupo dentro do GLB

# O que o jogo lê (ver props/CRAFT.md e, no Recomeço, jogo/sistemas/energia.gd).
# Reserva da rede da base: guarda 1200 Wh da sobra do gerador (ou do sol e do vento) para gastar depois.
REGISTRO = dict(
    nome='Banco de baterias', grupo='mobilias', categoria='energia', montagem='floor', lote=20,
    comodos=['abrigo', 'garagem', 'oficina'], fase=3, bateria_wh=1200,
    constroi={'bateria_carro': 2, 'tabua': 3, 'fio_eletrico': 1, 'caixa_pregos': 1}, ferramenta='chave_inglesa',
    estacao='energia (guarda 1200 Wh: a sobra do gerador fica para a noite, com ele desligado e em silêncio)')


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
