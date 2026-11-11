"""Tira de um GLB de arma os nós (nome, pai, posição) e as animações, para a arma refeita
entrar no lugar com os mesmos nós e as mesmas animações (ver guardia/jogo.py).
Rodar ANTES de sobrescrever o GLB antigo.

uso: python3 tirar_esqueleto.py armas/<id>.glb <pasta da arma>/esqueleto.json
"""
import sys, json
import numpy as np
import empacotar

TIPOS = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}


def main(arq, saida):
    j, b = empacotar.ler_glb(arq)
    nos = j['nodes']
    pai = {f: i for i, n in enumerate(nos) for f in n.get('children', [])}
    raiz = j['scenes'][j.get('scene', 0)]['nodes'][0]

    def acc(i):
        a = j['accessors'][i]
        v = j['bufferViews'][a['bufferView']]
        n = TIPOS[a['type']]
        o = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        x = np.frombuffer(bytes(b[o:o + a['count'] * n * 4]), np.float32).reshape(a['count'], n)
        return [round(float(k), 6) for k in x[:, 0]] if n == 1 else [[round(float(k), 6) for k in l] for l in x]

    lista = []

    def desce(i):
        for f in nos[i].get('children', []):
            n = nos[f]
            if not n['name'].startswith('ref_') and 'mesh' not in n:      # sem as malhas; os pontos ref_* são medidos de novo
                assert 'rotation' not in n and 'scale' not in n, n['name']
                lista.append({'no': n['name'], 'pai': None if pai[f] == raiz else nos[pai[f]]['name'],
                              'posicao': [round(float(k), 6) for k in n.get('translation', [0, 0, 0])]})
            desce(f)
    desce(raiz)
    anims = []
    for a in j.get('animations', []):
        fx = []
        for c in a['channels']:
            s = a['samplers'][c['sampler']]
            no = c['target']['node']
            fx.append({'no': None if no == raiz else nos[no]['name'], 'caminho': c['target']['path'],
                       'interp': s.get('interpolation', 'LINEAR'), 't': acc(s['input']), 'v': acc(s['output'])})
        anims.append({'nome': a['name'], 'faixas': fx})
    json.dump({'origem': arq.replace('\\', '/').split('/')[-1], 'nos': lista, 'animacoes': anims},
              open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(lista), 'nós,', len(anims), 'animações:', ', '.join(a['nome'] for a in anims))
    for n in lista:
        print(' ', n['no'], n['pai'], n['posicao'])


if __name__ == '__main__':
    main(*sys.argv[1:3])
