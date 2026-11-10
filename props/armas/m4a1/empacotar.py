"""Coloca as texturas PBR no GLB exportado sem imagens.
uso: python3 empacotar.py entrada.glb pasta_tex saida.glb [webp|jpg|png] [tamanho]"""
import sys, os, io, json, struct
from PIL import Image


def ler_glb(caminho):
    d = open(caminho, 'rb').read()
    n = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20 + n])
    resto = d[20 + n:]
    m = struct.unpack('<I', resto[0:4])[0]
    return j, bytearray(resto[8:8 + m])


def gravar_glb(caminho, j, bin_):
    while len(bin_) % 4:
        bin_.append(0)
    j['buffers'][0]['byteLength'] = len(bin_)
    js = json.dumps(j, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(bin_)
    with open(caminho, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A) + js)
        f.write(struct.pack('<II', len(bin_), 0x004E4942) + bin_)


def codificar(caminho, fmt, tam, q):
    im = Image.open(caminho).convert('RGB')
    if tam and im.width != tam:
        im = im.resize((tam, tam), Image.LANCZOS)
    b = io.BytesIO()
    if fmt == 'webp':
        im.save(b, 'WEBP', quality=q, method=6)
        return b.getvalue(), 'image/webp'
    if fmt == 'jpg':
        im.save(b, 'JPEG', quality=q, subsampling=0, optimize=True)
        return b.getvalue(), 'image/jpeg'
    im.save(b, 'PNG', optimize=True)
    return b.getvalue(), 'image/png'


def main(entrada, pasta, saida, fmt='webp', tam=0):
    j, bin_ = ler_glb(entrada)
    j.setdefault('images', [])
    j.setdefault('textures', [])
    j.setdefault('samplers', [])
    j['samplers'].append({'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497})
    samp = len(j['samplers']) - 1

    def textura(arq, q):
        dados, mime = codificar(os.path.join(pasta, arq), fmt, tam, q)
        while len(bin_) % 4:
            bin_.append(0)
        j['bufferViews'].append({'buffer': 0, 'byteOffset': len(bin_), 'byteLength': len(dados)})
        bin_.extend(dados)
        j['images'].append({'bufferView': len(j['bufferViews']) - 1, 'mimeType': mime, 'name': arq[:-4]})
        img = len(j['images']) - 1
        t = {'sampler': samp, 'name': arq[:-4]}
        if fmt == 'webp':
            t['extensions'] = {'EXT_texture_webp': {'source': img}}
        else:
            t['source'] = img
        j['textures'].append(t)
        return len(j['textures']) - 1

    for m in j['materials']:
        nome = m['name']
        if not os.path.exists(os.path.join(pasta, nome + '_cor.png')):
            continue
        cor = textura(nome + '_cor.png', 88)
        orm = textura(nome + '_orm.png', 86)
        nor = textura(nome + '_normal.png', 92)
        m['pbrMetallicRoughness'] = {'baseColorTexture': {'index': cor}, 'metallicRoughnessTexture': {'index': orm},
                                     'metallicFactor': 1.0, 'roughnessFactor': 1.0}
        m['normalTexture'] = {'index': nor}
        m['occlusionTexture'] = {'index': orm}
        m.pop('doubleSided', None)
    if fmt == 'webp':
        for k in ('extensionsUsed', 'extensionsRequired'):
            j.setdefault(k, [])
            if 'EXT_texture_webp' not in j[k]:
                j[k].append('EXT_texture_webp')
    gravar_glb(saida, j, bin_)
    print(saida, os.path.getsize(saida) // 1024, 'KB')


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3] if len(a) > 3 else 'webp', int(a[4]) if len(a) > 4 else 0)
