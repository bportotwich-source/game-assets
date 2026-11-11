#!/usr/bin/env python3
"""Escreve kits/<kit>/materiais.json: qual material das peças vira qual material de materiais/.

Uso: python3 scripts/materiais/mapear.py <kit> [<kit> ...]

Decide pelo nome do material nas peças (REGRAS). Onde a regra pede, a cor que o kit usa hoje
vira um tom por cima do ladrilho ("cor"), para a casa continuar da cor que era.
Peças sem UV recebem "sem_uv" (o Godot projeta o ladrilho pelas três faces).
"""
import glob, io, json, os, re, struct, sys
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# (expressão no nome, material da biblioteca, usa a cor do kit como tom)
REGRAS = [
    (r'^siding(_\w)?$', 'tabua_branca', True),
    (r'^brick$', 'tijolo_vermelho', False),
    (r'^(shingles?|shingle_g)$', 'TELHA', False),
    (r'^roof_tiles$', 'telha_barro', False),
    (r'^render$', 'reboco_externo', True),
    (r'^plaster$', 'reboco_claro', False),
    (r'^floor$', 'assoalho', False),
    (r'^(deck|attic|fencew)$', 'deck', False),
    (r'^(cap|cill|coping|lime)$', 'pedra_clara', False),
    (r'^(concrete|paving|precast|plinth)$', 'concreto', True),
    (r'^(ashlar|rustic|stone|stone2)$', 'cantaria', True),
    (r'^block$', 'bloco', False),
    (r'^(trim|frame|sash|door_int|lattice|picket|gdoor|garage_door|garage_panel|vent)$', 'tinta_creme', True),
    (r'^(door(_\w)?|shutter(_dark)?|acc_\w|shop_paint|frame2)$', 'tinta_creme', True),
]
SO_COM_UV = {'reboco_claro', 'assoalho', 'tijolo_vermelho', 'TELHA', 'telha_barro', 'bloco'}   # sem UV nessas não vale a pena
PISOS_E_PAREDES_DE_DENTRO = {'plaster', 'floor'}


def lin(c):
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c]


def srgb(c):
    return [1.055 * x ** (1 / 2.4) - 0.055 if x > 0.0031308 else x * 12.92 for x in c]


def media(im):
    return [v / 255 for v in im.convert('RGB').resize((1, 1), Image.BOX).getpixel((0, 0))]


def materiais_do_kit(kit):
    """nome -> dict(cor sRGB média, uv em todas as peças)."""
    M = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, 'kits', kit, 'pieces', '*.glb'))):
        b = open(f, 'rb').read()
        n = struct.unpack('<I', b[12:16])[0]
        j = json.loads(b[20:20 + n])
        bin0 = 20 + n + 8
        com_uv, usados = set(), set()
        for me in j.get('meshes', []):
            for p in me['primitives']:
                usados.add(p.get('material'))
                if 'TEXCOORD_0' in p['attributes']:
                    com_uv.add(p.get('material'))
        for i, m in enumerate(j.get('materials', [])):
            if i not in usados:
                continue
            pb = m.get('pbrMetallicRoughness', {})
            fator = list(pb.get('baseColorFactor', [1, 1, 1, 1])[:3])      # no glTF a cor vem linear
            cor = srgb(fator)
            e = M.setdefault(m['name'], dict(cor=None, uv=True, tex=False))
            e['uv'] &= i in com_uv
            if e['cor'] is None:
                if 'baseColorTexture' in pb:
                    img = j['images'][j['textures'][pb['baseColorTexture']['index']]['source']]
                    if 'bufferView' in img:
                        bv = j['bufferViews'][img['bufferView']]
                        dados = b[bin0 + bv.get('byteOffset', 0): bin0 + bv.get('byteOffset', 0) + bv['byteLength']]
                        t = lin(media(Image.open(io.BytesIO(dados))))
                        cor = srgb([a * c for a, c in zip(fator, t)])
                    e['tex'] = True
                e['cor'] = cor
    return M


def mapear(kit, lib):
    saida = {}
    for nome, e in sorted(materiais_do_kit(kit).items()):
        for exp, alvo, tom in REGRAS:
            if not re.match(exp, nome):
                continue
            if alvo == 'TELHA':
                r, g, bl = e['cor']
                alvo = 'telha_barro' if r > 1.6 * bl else 'telha_asfaltica'
            if nome == 'trim' and e['tex']:
                alvo, tom = 'pedra_clara', True
            if alvo not in lib or (not e['uv'] and (alvo in SO_COM_UV or nome in PISOS_E_PAREDES_DE_DENTRO)):
                break
            d = dict(material=alvo)
            if not e['uv']:
                d['sem_uv'] = True
            if tom:
                base = lin(lib[alvo]['cor_media'])
                t = srgb([min(1.0, a / max(b, 1e-3)) for a, b in zip(lin(e['cor']), base)])
                if min(t) < 0.93:
                    d['cor'] = [round(x, 3) for x in t]
            saida[nome] = d
            break
    return saida


def main():
    lib = json.load(open(os.path.join(RAIZ, 'materiais', 'materiais.json')))['materiais']
    for kit in sys.argv[1:]:
        m = mapear(kit, lib)
        json.dump(dict(kit=kit, gerado_por='scripts/materiais/mapear.py',
                       convencao='nome do material nas peças -> material de materiais/ (ver materiais/LEIA-ME.md). sem_uv: a peça não tem UV, o ladrilho é projetado pelas três faces. cor: multiplica a cor do ladrilho.',
                       materiais=m), open(os.path.join(RAIZ, 'kits', kit, 'materiais.json'), 'w'), ensure_ascii=False, indent=1)
        print(kit, len(m), ' '.join(f'{k}>{v["material"]}' for k, v in m.items()))


if __name__ == '__main__':
    main()
