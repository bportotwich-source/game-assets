#!/usr/bin/env python3
"""Leva os ladrilhos assados por amostras/casa_realista/ladrilho.py para materiais/.

Uso: python3 scripts/materiais/publicar.py <pasta com os PNG do ladrilho.py>

Grava <nome>_albedo.webp, <nome>_normal.webp, <nome>_orm.webp, o .import de cada um
(textura comprimida na placa de vídeo, com mipmaps) e materiais/materiais.json.
"""
import json, os, sys
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = os.path.join(RAIZ, 'materiais')
# nome no ladrilho.py -> (nome na biblioteca, lado em pixels, descrição)
MATERIAIS = {
    'siding':   ('tabua_verde', 2048, 'Tábua de fachada pintada de verde, fiadas de 20 cm, tinta descascando no veio'),
    'brick':    ('tijolo_vermelho', 2048, 'Tijolo aparente vermelho, fiada de 6,25 cm, junta de argamassa'),
    'shingles': ('telha_asfaltica', 2048, 'Telha asfáltica cinza, fiadas de 20 cm'),
    'floor':    ('assoalho', 2048, 'Assoalho de tábua envernizada de 10 cm, gasto'),
    'deck':     ('deck', 2048, 'Tábua de varanda sem verniz, acinzentada'),
    'plaster':  ('reboco_claro', 1024, 'Reboco pintado claro, com trincas finas'),
    'cap':      ('pedra_clara', 1024, 'Pedra clara de capa e peitoril'),
    'tinta':    ('tinta_creme', 1024, 'Madeira pintada de creme, para molduras, caixilhos e portas'),
    'siding_w': ('tabua_branca', 2048, 'Tábua de fachada pintada de branco, para receber a cor de cada casa'),
    'render':   ('reboco_externo', 2048, 'Reboco de fachada claro, com manchas de chuva, para receber a cor de cada casa'),
    'rooftile': ('telha_barro', 2048, 'Telha plana de barro, fiadas de 20 cm'),
    'ashlar':   ('cantaria', 2048, 'Pedra aparelhada clara, blocos de 50 x 25 cm'),
    'block':    ('bloco', 1024, 'Bloco de concreto aparente, 40 x 20 cm'),
    'concrete': ('concreto', 1024, 'Concreto liso de calçada, soleira e base'),
}
QUALIDADE = {'albedo': 90, 'orm': 88, 'normal': 94}
IMPORT = '''[remap]

importer="texture"
type="CompressedTexture2D"

[params]

compress/mode=2
compress/high_quality=false
compress/normal_map=%d
mipmaps/generate=true
detect_3d/compress_to=0
'''


def main():
    origem = sys.argv[1]
    os.makedirs(SAIDA, exist_ok=True)
    lib = {}
    arq = os.path.join(SAIDA, 'materiais.json')
    antigo = json.load(open(arq))['materiais'] if os.path.exists(arq) else {}
    for fonte, (nome, lado, desc) in MATERIAIS.items():
        if not os.path.exists(os.path.join(origem, f'{fonte}_cor.png')):      # não assado nesta pasta: mantém o que já está
            if nome in antigo:
                lib[nome] = antigo[nome]
            continue
        for tipo_fonte, tipo in (('cor', 'albedo'), ('normal', 'normal'), ('orm', 'orm')):
            im = Image.open(os.path.join(origem, f'{fonte}_{tipo_fonte}.png')).convert('RGB')
            if im.width != lado:
                im = im.resize((lado, lado), Image.LANCZOS)
            dst = os.path.join(SAIDA, f'{nome}_{tipo}.webp')
            im.save(dst, 'WEBP', quality=QUALIDADE[tipo], method=6)
            open(dst + '.import', 'w').write(IMPORT % (1 if tipo == 'normal' else 0))
            if tipo == 'albedo':
                media = [round(v / 255, 3) for v in im.resize((1, 1), Image.BOX).getpixel((0, 0))]
        lib[nome] = dict(descricao=desc, lado_m=2.0, pixels=lado, origem=fonte, cor_media=media)
    json.dump(dict(gerado_por='scripts/materiais/publicar.py', convencao='ladrilho de 2 m que emenda nos quatro lados; UV em metros / 2, igual às peças dos kits; normal OpenGL; ORM = oclusão, rugosidade, metálico', materiais=lib),
              open(os.path.join(SAIDA, 'materiais.json'), 'w'), ensure_ascii=False, indent=1)
    mem = sum(v['pixels'] ** 2 * 2 * 4 / 3 for v in lib.values()) / 1048576
    print(f'{len(lib)} materiais, {mem:.0f} MB de memória de vídeo')


if __name__ == '__main__':
    main()
