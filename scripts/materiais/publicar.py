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
    for fonte, (nome, lado, desc) in MATERIAIS.items():
        for tipo_fonte, tipo in (('cor', 'albedo'), ('normal', 'normal'), ('orm', 'orm')):
            im = Image.open(os.path.join(origem, f'{fonte}_{tipo_fonte}.png')).convert('RGB')
            if im.width != lado:
                im = im.resize((lado, lado), Image.LANCZOS)
            dst = os.path.join(SAIDA, f'{nome}_{tipo}.webp')
            im.save(dst, 'WEBP', quality=QUALIDADE[tipo], method=6)
            open(dst + '.import', 'w').write(IMPORT % (1 if tipo == 'normal' else 0))
        lib[nome] = dict(descricao=desc, lado_m=2.0, pixels=lado, origem=fonte)
    json.dump(dict(gerado_por='scripts/materiais/publicar.py', convencao='ladrilho de 2 m que emenda nos quatro lados; UV em metros / 2, igual às peças dos kits; normal OpenGL; ORM = oclusão, rugosidade, metálico', materiais=lib),
              open(os.path.join(SAIDA, 'materiais.json'), 'w'), ensure_ascii=False, indent=1)
    mem = sum(v['pixels'] ** 2 * 2 * 4 / 3 for v in lib.values()) / 1048576
    print(f'{len(lib)} materiais, {mem:.0f} MB de memória de vídeo')


if __name__ == '__main__':
    main()
