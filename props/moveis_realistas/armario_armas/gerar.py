"""Gera o armário de armas de aço: modelo, UVs, bake das texturas e o GLB do jogo
(props/mobilias/armario_armas.glb), e atualiza o registro em props/mobilias/catalogo.json
(medidas, portas, vagas das armas e "gerador", para o gerar_props.py não o refazer).

uso: python3 gerar.py [resolução] [saída]        (precisa de: pip install bpy pillow numpy)
Um grupo de textura que já tem os arquivos na pasta de saída não é assado de novo;
REASSAR=A,B força os grupos listados. Grupos: A carcaça, B interior, C portas."""
import sys, os, json, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import base
import materiais, modelo
import fabrica, empacotar
from PIL import Image

ID = 'armario_armas'
PROPS = os.path.dirname(os.path.dirname(AQUI))
CFG = dict(nome=ID, montar=modelo.montar, origem=(0, 0, 0))
TAMANHO = {'A': 2048, 'B': 1024, 'C': 2048}        # textura de cada grupo dentro do GLB


def vagas():
    """Onde cada coisa fica à mostra, em metros, no espaço do móvel. "parte" é a porta que a cobre.
    longa: em pé, coronha na bandeja (pos) e cano no berço (apoio = [altura, z]); curta: em pé na
    prateleira, de perfil; prateleira: qualquer outro item (caixas de munição...)."""
    m = modelo
    v = [dict(tipo='longa', parte=int(x >= 0), pos=[x / 1000, m.BANDEJA_Y / 1000, m.BERCO_Z / 1000 + 0.06],
              apoio=[m.BARRA_Y / 1000, m.BERCO_Z / 1000], giro_graus=55, comprimento_max_m=1.14) for x in m.VAGAS_X]
    v += [dict(tipo='curta', parte=int(x >= 0), pos=[x / 1000, m.PRAT1_Y / 1000 + 0.001, -0.005], comprimento_max_m=0.36) for x in (-360, -120, 120, 360)]
    v += [dict(tipo='prateleira', parte=int(x >= 0), pos=[x / 1000, m.PRAT2_Y / 1000 + 0.001, -0.03], largura_max_m=0.15) for x in (-400, -240, -80, 80, 240, 400)]
    return v


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
    m = modelo
    r.update(nome='Armário de armas de aço', tamanho_m=tam, triangulos=tris, kb=round(os.path.getsize(arq) / 1024, 1),
             gerador='moveis_realistas/armario_armas/gerar.py', slots=16, grade=[16, 6], vagas_armas=vagas(),
             aceita=['armas', 'municao', 'acessorios'],
             partes=[dict(no='porta_esq', origem=[-m.W / 1000, 0, m.EIXO_Z / 1000], tipo='porta', eixo='y', abre_graus=-110),
                     dict(no='porta_dir', origem=[m.W / 1000, 0, m.EIXO_Z / 1000], tipo='porta', eixo='y', abre_graus=110)])
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{ID} {tris} tris {r['kb']} KB {tam}")


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2048, *sys.argv[2:3])
