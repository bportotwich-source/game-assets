"""Deixa os punhos de pistola passarem de uma arma para a outra (catálogo e GLBs das armas).

uso: python3 encaixes.py            (pode rodar de novo: não repete o que já fez; rode depois de
                                     regenerar o Brasa, a carabina .308 ou as armas de receptor de alumínio)

1. Fuzis de receptor de alumínio (encaixe_punho do tipo punho_ar: 5,56, M4A1, .308 de precisão):
   passam a aceitar os punhos de 7,62 (punho_akmn, punho_tatico_akmn). O encaixe ganha o campo
   "ajuste": por tipo de encaixe do acessório, onde ele fica em relação ao nó (posicao_m), quanto
   gira para trás (inclinacao_graus, em volta do eixo X) e que peça vai junto ("com": o adaptador).
2. Brasa 7,62 (fuzil_762 e _tatico): o punho que era fixo vai para o nó "punho" e nasce o
   encaixe_punho (tipo punho_ak), que aceita os punhos do AKMN.
3. Carabina .308 de chassi (carabina_308): o punho vai para o nó "punho" e nasce o encaixe_punho
   (tipo punho_ar), que aceita os mesmos punhos dos fuzis.
"""
import os, sys, json, math
AQUI = os.path.dirname(os.path.abspath(__file__))
ARMAS = os.path.dirname(AQUI)
sys.path[:0] = [os.path.join(ARMAS, 'm4a1')]
import empacotar

PUNHOS_AR = ['punho_ar', 'punho_ar_tan', 'punho_cavas', 'punho_cavas_tan', 'punho_reto', 'punho_reto_tan', 'punho_vazado_m4']
PUNHOS_762 = ['punho_akmn', 'punho_tatico_akmn']
GRAUS_762 = 8.8                       # inclinação dos punhos de 7,62 como vêm no AKMN (pontos_ref.AJUSTE)
ADAPTADOR = 'adaptador_punho_762'
# arma -> (tipo do encaixe novo, posição do nó punho na arma, o que aceita)
NOVOS = {
    'fuzil_762': ('punho_ak', (0.0, 0.0, 0.0), PUNHOS_762),
    'fuzil_762_tatico': ('punho_ak', (0.0, 0.0, 0.0), PUNHOS_762),
    'carabina_308': ('punho_ar', (0.0, 0.048, -0.017), PUNHOS_AR + PUNHOS_762),
}


def _inclinacao(arma):
    """Ângulo do ref_punho da arma (graus, positivo = base do punho para trás)."""
    j, _ = empacotar.ler_glb(os.path.join(ARMAS, arma['arquivo']))
    n = next(n for n in j['nodes'] if n.get('name') == 'ref_punho')
    return -2 * math.degrees(math.asin(n.get('rotation', [0, 0, 0, 1])[0]))


def abrir_no_punho(arma, pos):
    """No GLB da arma: a malha <id>_punho sai da raiz e vai para o nó novo "punho", com o encaixe_punho ao lado."""
    arq = os.path.join(ARMAS, arma['arquivo'])
    j, bin_ = empacotar.ler_glb(arq)
    nomes = [n.get('name') for n in j['nodes']]
    if 'encaixe_punho' in nomes:
        return False
    im = nomes.index(arma['id'] + '_punho')
    pai = next(n for n in j['nodes'] if im in n.get('children', []))
    assert pai.get('name') == arma['id'], pai.get('name')
    malha = j['nodes'][im]
    t = malha.get('translation', [0, 0, 0])
    malha['translation'] = [t[k] - pos[k] for k in range(3)]
    j['nodes'].append({'name': 'encaixe_punho'})
    j['nodes'].append({'name': 'punho', 'translation': list(pos), 'children': [im, len(j['nodes']) - 1]})
    pai['children'][pai['children'].index(im)] = len(j['nodes']) - 1
    empacotar.gravar_glb(arq, j, bin_)
    return True


def main():
    arq_cat = os.path.join(ARMAS, 'catalogo.json')
    cat = json.load(open(arq_cat, encoding='utf-8'))
    AC = {a['id']: a for a in cat['acessorios']}
    ad = AC[ADAPTADOR]
    ad.update(nome='Adaptador de punho 7,62', categoria='adaptador', peso_kg=0.05, modificadores={},
              uso='o jogo monta sozinho junto com um punho de 7,62 num encaixe punho_ar (campo "ajuste" do encaixe); não é item')
    for a in cat['armas']:
        if a['id'] in NOVOS:
            tipo, pos, aceita = NOVOS[a['id']]
            if abrir_no_punho(a, pos):
                print('nó punho aberto em', a['id'])
            a['encaixes'] = [e for e in a['encaixes'] if e['no'] != 'encaixe_punho']
            i = next((k for k, e in enumerate(a['encaixes']) if e['no'] == 'encaixe_coronha'), len(a['encaixes']))
            a['encaixes'].insert(i, dict(no='encaixe_punho', tipo=tipo, pai='punho', posicao_m=[0.0, 0.0, 0.0], substitui='punho',
                                         aceita=list(aceita), explodir_m=[0.0, -0.08, 0.02],
                                         descricao='filho do nó punho; ao pôr um punho aqui, esconda as malhas do nó punho'))
            if not any(p['no'] == 'punho' for p in a['partes']):
                a['partes'].insert(0, dict(no='punho', tipo='troca', descricao='punho de pistola (troca pelo encaixe_punho)', pai=a['id'],
                                           explodir_m=[0.0, -0.06, 0.02]))
        e = next((e for e in a.get('encaixes', []) if e['no'] == 'encaixe_punho'), None)
        if e is None:
            continue
        graus = round(_inclinacao(a) - GRAUS_762, 1)
        if e['tipo'] == 'punho_ar':
            e['aceita'] = [x for x in e['aceita'] if x not in PUNHOS_762] + PUNHOS_762
            j, _ = empacotar.ler_glb(os.path.join(ARMAS, a['arquivo']))
            p = next(n for n in j['nodes'] if n.get('name') == 'punho')['translation']
            e['ajuste'] = {'punho_ak': dict(posicao_m=[round(-c, 4) for c in p], inclinacao_graus=graus, com=ADAPTADOR)}
        elif a['id'] in NOVOS:                             # Brasa: o receptor fica 19 mm mais alto que no AKMN; o topo plano encosta nele
            e['ajuste'] = {'punho_ak': dict(posicao_m=[0.0, 0.0188, 0.004], inclinacao_graus=0.0)}
        print(a['id'], e['tipo'], e.get('ajuste'))
    doc = ' Um encaixe pode ter "ajuste": {tipo do acessório: {posicao_m, inclinacao_graus, com}} para receber acessório de outro tipo ' \
          '(punho de 7,62 em fuzil de alumínio): o acessório entra deslocado, girado para trás em volta do X e com a peça "com" (adaptador) ao lado.'
    if 'ajuste' not in cat['encaixes']:
        cat['encaixes'] += doc
    json.dump(cat, open(arq_cat, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
