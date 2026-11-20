"""Acerta o comprimento das coronhas nos GLB já gerados, sem refazer o modelo.

Pedido do Bruno (2026-11-20): "O tamanho da coronha das armas grandes está ideal? Ela passa a medida
ideal para a personagem segurá-la no ombro sem entrar dentro do tronco?" — "Podemos ajeitar elas".

A medida que conta é a do gatilho até a soleira (ref_gatilho -> ref_coronha ao longo do cano). Para a
Amber (1,68 m), da dobra do cotovelo até o dedo no gatilho dá 34 cm; fuzis de adulto ficam por volta de
34 a 36 cm. Quatro coronhas passavam disso (a de madeira do Brasa 7,62 tinha 47 cm e saía pelas costas)
e a da Faísca 9 mm vinha fechada (18 cm).

O que faz:
  encolher   aperta a coronha ao longo do comprimento (eixo +Z da peça, para trás) só no trecho do meio
             [z1, z2]: a frente (encaixe) e a soleira ficam com a forma de antes. Vértices, normais e
             tangentes da malha; os nós com posição (soleira, monopé, apoio de rosto, ombro, ref_coronha)
             andam junto. A textura fica um pouco mais apertada nesse trecho.
  mover      anda nós de uma arma (ref_coronha da arma, coronha de varetas aberta).
Rode de novo depois de gerar as coronhas/armas outra vez pelo Blender (gerar.py/jogo.py), senão elas
voltam ao tamanho antigo; o script sabe se já rodou (marca "coronha_ajustada" no extras do GLB).

uso: python3 ajustar_coronhas.py          (aplica a tabela abaixo)
     python3 ajustar_coronhas.py --medir  (só mede gatilho -> soleira das armas com coronha)
"""
import json
import os
import struct
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))

# coronha avulsa: quanto encurtar (m) e o trecho que encolhe, em z da peça (0 = encaixe, + = para trás)
ENCOLHER = {
    'acessorios/coronha_madeira_ak.glb': dict(delta=0.118, z1=0.03, z2=0.30),           # 47,3 -> 35,5 cm
    'acessorios/coronha_esqueleto_ak.glb': dict(delta=0.086, z1=0.03, z2=0.28),         # 44,1 -> 35,5
    'acessorios/coronha_esqueleto_ak_gasto.glb': dict(delta=0.086, z1=0.03, z2=0.28),
    'acessorios/coronha_fixa_ar.glb': dict(delta=0.079, z1=0.03, z2=0.30),              # 42,9 -> 35,0
    'acessorios/coronha_precisao_ar.glb': dict(delta=0.033, z1=0.03, z2=0.24),          # 38,8 -> 35,5
    'acessorios/coronha_precisao_ar_preta.glb': dict(delta=0.033, z1=0.03, z2=0.24),
}
# armas: a mesma conta no ref_coronha da arma (o da coronha montada por padrão) e na versão leve,
# que tem a coronha junto na malha (z da peça = z da arma - z do encaixe_coronha)
ARMAS = {
    'armas/fuzil_762.glb': 'acessorios/coronha_madeira_ak.glb',
    'armas/fuzil_762_tatico.glb': 'acessorios/coronha_esqueleto_ak_gasto.glb',
    'armas/fuzil_m4a1_luneta.glb': 'acessorios/coronha_fixa_ar.glb',
    'armas/fuzil_m4a1_luneta_leve.glb': 'acessorios/coronha_fixa_ar.glb',
    'armas/fuzil_308_precisao.glb': 'acessorios/coronha_precisao_ar.glb',
    'armas/fuzil_308_precisao_curto.glb': 'acessorios/coronha_precisao_ar.glb',
}
# Faísca 9 mm: a coronha de varetas já tem o curso de abrir (-130 mm, animação "estender"); passa a
# vir aberta. O nó "coronha" leva a soleira, as varetas e o "ombro"; o ref_coronha da arma vai junto.
ABRIR = {'armas/smg_9mm.glb': 0.13, 'armas/smg_9mm_tan.glb': 0.13}
# Empunhadura frontal (grip reto) longe demais para o braço esquerdo da Amber alcançar com a coronha
# no ombro (faltavam 9 cm na M4A1 tática e 3 cm na Ciclone): o encaixe anda para trás no trilho.
# Anda o nó encaixe_empunhadura, o ref_guarda_mao da arma, o catálogo e, na versão leve, os vértices
# do grip (embaixo do trilho, entre z_de e z_ate).
GRIP_PARA_TRAS = {
    'armas/fuzil_m4a1_tatico.glb': dict(d=0.097, z_de=-0.39, z_ate=-0.285, y_ate=0.05),
    'armas/smg_ciclone_9mm.glb': dict(d=0.025, z_de=-0.32, z_ate=-0.235, y_ate=0.035),
    'armas/smg_ciclone_9mm_tan.glb': dict(d=0.025, z_de=-0.32, z_ate=-0.235, y_ate=0.035),
}


def ler(p):
    b = open(p, 'rb').read()
    n = struct.unpack('<I', b[12:16])[0]
    g = json.loads(b[20:20 + n])
    o = 20 + n
    m = struct.unpack('<I', b[o:o + 4])[0]
    return g, bytearray(b[o + 8:o + 8 + m])


def gravar(p, g, binario):
    js = json.dumps(g, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    js += b' ' * ((4 - len(js) % 4) % 4)
    binario = bytes(binario) + b'\0' * ((4 - len(binario) % 4) % 4)
    g['buffers'][0]['byteLength'] = len(binario)
    js = json.dumps(g, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    js += b' ' * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(binario)
    with open(p, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A) + js)
        f.write(struct.pack('<II', len(binario), 0x004E4942) + binario)


def _vista(g, binario, acc):
    a = g['accessors'][acc]
    bv = g['bufferViews'][a['bufferView']]
    passo = bv.get('byteStride', 0) or (16 if a['type'] == 'VEC4' else 12)
    ini = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n = a['count']
    comp = 4 if a['type'] == 'VEC4' else 3
    arr = np.ndarray((n, passo // 4), dtype=np.float32, buffer=binario, offset=ini)
    return arr[:, :comp], a


def _mapa(z, delta, z1, z2):
    s = (z2 - z1 - delta) / (z2 - z1)
    return np.where(z < z1, z, np.where(z > z2, z - delta, z1 + (z - z1) * s))


def encolher_malha(g, binario, prim, delta, z1, z2, z0=0.0):
    s = (z2 - z1 - delta) / (z2 - z1)
    pos, apos = _vista(g, binario, prim['attributes']['POSITION'])
    z = pos[:, 2] - z0
    meio = (z >= z1) & (z <= z2)
    pos[:, 2] = _mapa(z, delta, z1, z2) + z0
    if 'NORMAL' in prim['attributes']:
        nor, _ = _vista(g, binario, prim['attributes']['NORMAL'])
        nz = nor[meio].copy()
        nz[:, 2] /= s
        nz /= np.linalg.norm(nz, axis=1, keepdims=True) + 1e-12
        nor[meio] = nz
    if 'TANGENT' in prim['attributes']:
        tan, _ = _vista(g, binario, prim['attributes']['TANGENT'])
        tz = tan[meio, :3].copy()
        tz[:, 2] *= s
        tz /= np.linalg.norm(tz, axis=1, keepdims=True) + 1e-12
        tan[meio, :3] = tz
    apos['min'] = [float(v) for v in pos.min(axis=0)]
    apos['max'] = [float(v) for v in pos.max(axis=0)]


def _ja(g):
    return bool(g.get('asset', {}).get('extras', {}).get('coronha_ajustada'))


def _marcar(g, o_que):
    g.setdefault('asset', {}).setdefault('extras', {})['coronha_ajustada'] = o_que


def coronha(arq, delta, z1, z2):
    p = os.path.join(AQUI, arq)
    g, b = ler(p)
    if _ja(g):
        print('já ajustada:', arq)
        return
    for nd in g['nodes']:
        t = nd.get('translation')
        if 'mesh' in nd and (not t or abs(t[2]) < 1e-9):
            for prim in g['meshes'][nd['mesh']]['primitives']:
                encolher_malha(g, b, prim, delta, z1, z2)
        elif t:
            t[2] = float(_mapa(np.array(t[2]), delta, z1, z2))
    _marcar(g, {'encurtou_m': delta})
    gravar(p, g, b)
    print('coronha %s: -%.1f cm' % (arq, delta * 100))


def arma(arq, coronha_arq):
    p = os.path.join(AQUI, arq)
    if not os.path.exists(p):
        return False
    g, b = ler(p)
    if _ja(g):
        print('já ajustada:', arq)
        return False
    c = ENCOLHER[coronha_arq]
    nos = {nd.get('name', ''): nd for nd in g['nodes']}
    enc = nos.get('encaixe_coronha')
    if arq.endswith('_leve.glb'):
        z0 = (enc or {}).get('translation', [0, 0, 0.015])[2] if enc else 0.015
        for m in g['meshes']:
            for prim in m['primitives']:
                encolher_malha(g, b, prim, c['delta'], c['z1'], c['z2'], z0)
    rc = nos.get('ref_coronha')
    if rc and rc.get('translation'):
        rc['translation'][2] -= c['delta']
    _marcar(g, {'encurtou_m': c['delta']})
    gravar(p, g, b)
    print('arma %s: ref_coronha -%.1f cm' % (arq, c['delta'] * 100))
    return True


def abrir(arq, curso):
    p = os.path.join(AQUI, arq)
    g, b = ler(p)
    if _ja(g):
        print('já ajustada:', arq)
        return False
    nos = {nd.get('name', ''): nd for nd in g['nodes']}
    nos['coronha']['translation'][2] += curso
    # o ref_coronha é filho do nó coronha (anda com ele); só mexe se estiver solto na arma
    filhos = [g['nodes'][i].get('name') for i in nos['coronha'].get('children', [])]
    if 'ref_coronha' not in filhos:
        nos['ref_coronha']['translation'][2] += curso
    _marcar(g, {'coronha_aberta_m': curso})
    gravar(p, g, b)
    print('arma %s: coronha aberta +%.0f mm' % (arq, curso * 1000))
    return True


def grip_para_tras(arq, d, z_de, z_ate, y_ate):
    feitas = []
    for f in (arq, arq.replace('.glb', '_leve.glb')):
        p = os.path.join(AQUI, f)
        if not os.path.exists(p):
            continue
        g, b = ler(p)
        if g.get('asset', {}).get('extras', {}).get('grip_ajustado'):
            print('já ajustada:', f)
            continue
        nos = {nd.get('name', ''): nd for nd in g['nodes']}
        for n in ('encaixe_empunhadura', 'ref_guarda_mao'):
            if n in nos and nos[n].get('translation'):
                nos[n]['translation'][2] += d
        if f.endswith('_leve.glb'):
            for m in g['meshes']:
                for prim in m['primitives']:
                    pos, apos = _vista(g, b, prim['attributes']['POSITION'])
                    sel = (pos[:, 2] >= z_de) & (pos[:, 2] <= z_ate) & (pos[:, 1] <= y_ate) & (np.abs(pos[:, 0]) < 0.03)
                    pos[sel, 2] += d
                    apos['min'] = [float(v) for v in pos.min(axis=0)]
                    apos['max'] = [float(v) for v in pos.max(axis=0)]
        g.setdefault('asset', {}).setdefault('extras', {})['grip_ajustado'] = d
        gravar(p, g, b)
        print('grip de %s: %.1f cm para trás' % (f, d * 100))
        feitas.append(f)
    if arq not in feitas:
        return
    pc = os.path.join(AQUI, 'catalogo.json')
    c = json.load(open(pc, encoding='utf-8'))
    for a in c['armas']:
        if a.get('arquivo') == arq:
            for e in a.get('pontos_ref', []) + a.get('encaixes', []):
                if e.get('no') in ('ref_guarda_mao', 'encaixe_empunhadura') and e.get('posicao_m'):
                    e['posicao_m'][2] = round(e['posicao_m'][2] + d, 4)
    open(pc, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')


def catalogo(feitas):
    """Atualiza o ref_coronha e o tamanho_m no catalogo.json das armas ajustadas agora."""
    p = os.path.join(AQUI, 'catalogo.json')
    txt = open(p, encoding='utf-8').read()
    c = json.loads(txt)
    mexeu = 0
    for a in c['armas']:
        arq = a.get('arquivo', '')
        d = 0.0
        if arq not in feitas:
            continue
        if arq in ARMAS:
            d = -ENCOLHER[ARMAS[arq]]['delta']
        elif arq in ABRIR:
            d = ABRIR[arq]
        if not d:
            continue
        for e in a.get('pontos_ref', []) + a.get('encaixes', []):
            if e.get('no') == 'ref_coronha' and e.get('posicao_m'):
                e['posicao_m'][2] = round(e['posicao_m'][2] + d, 4)
        if a.get('tamanho_m'):
            a['tamanho_m'][2] = round(a['tamanho_m'][2] + d, 3)
        mexeu += 1
    if mexeu:
        open(p, 'w', encoding='utf-8').write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
    print('catálogo: %d armas' % mexeu)


def medir():
    for arq in sorted(os.listdir(os.path.join(AQUI, 'armas'))):
        if not arq.endswith('.glb') or arq.endswith('_leve.glb'):
            continue
        g, _ = ler(os.path.join(AQUI, 'armas', arq))
        nos = {nd.get('name', ''): nd.get('translation', [0, 0, 0]) for nd in g['nodes']}
        if 'ref_coronha' in nos and 'ref_gatilho' in nos:
            print('%-28s %.1f cm (só o z; a medida certa é no app, com a coronha montada)' % (arq, (nos['ref_coronha'][2] - nos['ref_gatilho'][2]) * 100))


if __name__ == '__main__':
    if '--medir' in sys.argv:
        medir()
        sys.exit(0)
    for arq, c in ENCOLHER.items():
        coronha(arq, **c)
    feitas = [arq for arq, cor in ARMAS.items() if arma(arq, cor)]
    feitas += [arq for arq, curso in ABRIR.items() if abrir(arq, curso)]
    catalogo(feitas)
    for arq, c in GRIP_PARA_TRAS.items():
        grip_para_tras(arq, **c)
