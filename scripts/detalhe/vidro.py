"""Vidro transparente igual em todos os kits.

Antes, todo material de vidro saia do gerador como OPACO (alphaMode OPAQUE, alpha 1), com a cor azul-gelo
(150, 186, 204): de dentro nao se via a rua e de fora nao se via o comodo. No jogo, so as janelas "quebradas"
pela ruina ficavam vazadas, por isso umas janelas pareciam transparentes e outras azuis.

Este modulo reescreve so o JSON do GLB (a geometria e as texturas ficam iguais):
  - vidro de janela/porta (glass, glass_w, bglass) vira um unico material 'glass' (o jogo procura esse nome
    para quebrar o vidro), quase incolor, alpha 0.16, liso e com reflexo;
  - vidros especiais continuam com o nome e o tom proprios, mas transparentes: gglass (guarda-corpo verde),
    jal (laminas da janela basculante / galao do bebedouro) glass_f e frost (vidro jateado de vestiario/basculante alto, mais fosco).
  - espelhos (mirror) e lampadas (lamp_glass) nao mudam.

Uso: chamado sozinho por detalhe.glb_jpeg() (todo gerador ja passa por ele) e pela linha de comando para
reaplicar nos GLB prontos:  python scripts/detalhe/vidro.py kits/   (aceita pastas ou arquivos .glb)
"""
import json, os, struct, sys, glob

# nome no GLB -> (novo nome, cor linear RGB, alpha, roughness)
VIDROS = {
    'glass':   ('glass',   (0.86, 0.93, 0.95), 0.16, 0.04),
    'glass_w': ('glass',   (0.86, 0.93, 0.95), 0.16, 0.04),
    'bglass':  ('glass',   (0.86, 0.93, 0.95), 0.16, 0.04),
    'gglass':  ('gglass',  (0.62, 0.84, 0.76), 0.30, 0.05),
    'jal':     ('jal',     (0.80, 0.90, 0.93), 0.24, 0.06),
    'glass_f': ('glass_f', (0.90, 0.93, 0.94), 0.62, 0.45),
    'frost':   ('frost',   (0.90, 0.93, 0.94), 0.62, 0.45),
}


def ajustar_material(m):
    """Ajusta um material glTF (dict) no lugar. Devolve True se mudou."""
    alvo = VIDROS.get(m.get('name', ''))
    if not alvo: return False
    nome, cor, a, rough = alvo
    antes = json.dumps(m, sort_keys=True)
    m['name'] = nome
    pb = m.setdefault('pbrMetallicRoughness', {})
    pb['baseColorFactor'] = [cor[0], cor[1], cor[2], a]
    pb['metallicFactor'] = 0.0
    pb['roughnessFactor'] = rough
    for k in ('baseColorTexture', 'metallicRoughnessTexture'): pb.pop(k, None)
    for k in ('normalTexture', 'occlusionTexture', 'emissiveTexture', 'emissiveFactor', 'alphaCutoff'): m.pop(k, None)
    m['alphaMode'] = 'BLEND'
    m['doubleSided'] = False      # as vidracas sao caixas finas: cada lado ja tem sua face
    return json.dumps(m, sort_keys=True) != antes


def vidro_glb(path):
    """Reescreve os materiais de vidro de um .glb. Devolve quantos materiais mudaram."""
    data = open(path, 'rb').read()
    if data[:4] != b'glTF': return 0
    off = 12; chunks = []
    while off < len(data):
        ln, ty = struct.unpack('<II', data[off:off + 8]); chunks.append((ty, data[off + 8:off + 8 + ln])); off += 8 + ln
    js = json.loads(chunks[0][1])
    n = sum(ajustar_material(m) for m in js.get('materials', []))
    if not n: return 0
    j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((-len(j)) % 4)
    rest = b''.join(struct.pack('<II', len(c), ty) + c for ty, c in chunks[1:])
    open(path, 'wb').write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + len(rest)) + struct.pack('<II', len(j), 0x4E4F534A) + j + rest)
    return n


if __name__ == '__main__':
    arqs = []
    for a in sys.argv[1:] or ['kits']:
        arqs += [a] if a.endswith('.glb') else glob.glob(os.path.join(a, '**', '*.glb'), recursive=True)
    tot = arq = 0
    for f in sorted(arqs):
        n = vidro_glb(f); tot += n; arq += bool(n)
    print(f'{arq} arquivos, {tot} materiais de vidro ajustados')
