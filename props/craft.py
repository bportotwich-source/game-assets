"""Arvore de craft e de armazenamento do Recomeco, gerada dos catalogos (props/loot e props/mobilias).

Uso:  python props/craft.py          escreve props/CRAFT.md e confere as receitas
      python props/craft.py --checar so confere (sai com erro se um ingrediente nao existir)

Confere que todo ingrediente de 'constroi' e 'craft', toda 'ferramenta' e todo 'obtem_de' e o id de um item
de loot ou de uma mobilia. Recursos coletados no mundo (terra, palha...) ficam na lista COLETADOS.
"""
import os, sys, json, re
AQUI = os.path.dirname(os.path.abspath(__file__))
COLETADOS = {'terra': 'terra (cavar com pá)', 'palha': 'palha (fardo de feno)', 'colchão de uma cama': 'colchão tirado de uma cama'}
FASES = {1: 'Fase 1 · Sozinho', 2: 'Fase 2 · Abrigo', 3: 'Fase 3 · Assentamento', 4: 'Fase 4 · Vila', 5: 'Fase 5 · Cidade nova'}


def carregar():
    itens = {}
    for g in ('loot', 'mobilias'):
        for r in json.load(open(os.path.join(AQUI, g, 'catalogo.json'), encoding='utf-8'))['itens']: itens[r['id']] = r
    armas = os.path.join(AQUI, 'armas', 'catalogo.json')
    if os.path.exists(armas):
        a = json.load(open(armas, encoding='utf-8'))
        for g in ('armas', 'acessorios', 'municao'):
            for r in a.get(g, []): itens.setdefault(r['id'], dict(r, grupo='armas'))
    return itens


def receita(r):
    """(ingredientes, ferramenta, estacao, tempo) de um item, venha de 'constroi' (mobilias) ou de 'craft' (loot)."""
    if 'craft' in r:
        c = r['craft']; return c.get('ingredientes', {}), c.get('ferramenta'), c.get('estacao'), c.get('tempo_s')
    if 'constroi' in r: return r['constroi'], r.get('ferramenta'), None, r.get('tempo_s')
    return None


def checar(itens):
    erros = []
    def ok(x): return x in itens or x in COLETADOS or x in (None, 'nenhuma', 'mao')
    for r in itens.values():
        rc = receita(r)
        if rc:
            ing, fer, est, _ = rc
            erros += [f"{r['id']}: ingrediente '{k}' não existe" for k in ing if not ok(k)]
            if fer and not ok(fer) and not any(ok(f.strip()) for f in re.split(r' ou |\(', fer)[:1]): erros.append(f"{r['id']}: ferramenta '{fer}' não existe")
            if est and not ok(est): erros.append(f"{r['id']}: estação '{est}' não existe")
        for o in r.get('obtem_de', []):
            alvo = o.get('desmontar') or o.get('consumir') or o.get('fazer')
            if alvo not in itens and alvo != 'ruina': erros.append(f"{r['id']}: obtem_de '{alvo}' não existe")
        if r.get('estoque') and r['estoque']['item'] not in itens: erros.append(f"{r['id']}: estoque de '{r['estoque']['item']}' não existe")
    return erros


def nome(itens, k):
    if k in itens: return f"{itens[k]['nome']} (`{k}`)"
    return COLETADOS.get(k, k)


def md(itens):
    v = lambda x: re.sub(r'(\d)\.(\d)', r'\1,\2', str(x))
    L = ['# Árvore de craft e armazenamento', '',
         'Gerado por `props/craft.py` a partir dos catálogos. Mostra, fase a fase, o que o jogador fabrica ou constrói, com quê, e onde guarda.',
         'Ingredientes são ids do loot (`props/loot/catalogo.json`); estações e construções são mobílias (`props/mobilias/catalogo.json`).', '',
         '## Receitas por fase', '']
    com = [r for r in itens.values() if receita(r)]
    for f in sorted(FASES):
        lista = [r for r in com if r.get('fase', 2 if r['lote'] >= 8 else 1) == f]
        if not lista: continue
        L += [f'### {FASES[f]}', '', '| Item | Lote | Ingredientes | Ferramenta | Estação | Tempo |', '|---|---|---|---|---|---|']
        for r in sorted(lista, key=lambda r: (r['lote'], r['nome'])):
            ing, fer, est, t = receita(r)
            L.append(f"| {r['nome']} (`{r['id']}`) | {r['lote']} | {', '.join(f'{q}× {nome(itens, k)}' for k, q in ing.items())} | "
                     f"{nome(itens, fer) if fer and fer != 'nenhuma' else 'à mão'} | {nome(itens, est) if est else '-'} | {v(t) + ' s' if t else '-'} |")
        L.append('')
    mats = [r for r in itens.values() if r.get('obtem_de') or (r.get('grupo') == 'loot' and r.get('lote', 0) >= 13)]
    if mats:
        L += ['## Materiais: de onde vêm e onde entram', '', '| Material | Fase | Grade | Peso | Achado em | Também sai de | Entra em |', '|---|---|---|---|---|---|---|']
        usos = {}
        for r in com:
            for k in receita(r)[0]: usos.setdefault(k, []).append(r['nome'])
        for r in sorted(mats, key=lambda r: (r.get('fase', 1), r['nome'])):
            de = ', '.join(f"{'desmontar' if 'desmontar' in o else 'comer' if 'consumir' in o else 'fazer'} {nome(itens, o.get('desmontar') or o.get('consumir') or o.get('fazer')) if (o.get('desmontar') or o.get('consumir') or o.get('fazer')) in itens else 'ruínas'} ({o['qtd']})"
                           for o in r.get('obtem_de', [])) or '-'
            cel = r.get('celulas'); L.append(f"| {r['nome']} (`{r['id']}`) | {r.get('fase', '-')} | {f'{cel[0]}×{cel[1]}' if cel else '-'} | {v(r.get('peso_kg', '-'))} kg | "
                                             f"{', '.join(r.get('onde', [])) or '-'} | {de} | {', '.join(sorted(set(usos.get(r['id'], [])))) or r.get('efeito', '-')} |")
        L.append('')
    arm = [r for r in itens.values() if r.get('categoria') == 'armazenamento']
    if arm:
        L += ['## Armazenamento do abrigo', '', '| Peça | Fase | Guarda | Grade | Vagas de armas | Prateleiras | Estoque |', '|---|---|---|---|---|---|---|']
        for r in sorted(arm, key=lambda r: (r.get('fase', 1), r['nome'])):
            vg = {}
            for a in r.get('vagas_armas', []): vg[a['tipo']] = vg.get(a['tipo'], 0) + 1
            g = r.get('grade'); e = r.get('estoque')
            L.append(f"| {r['nome']} (`{r['id']}`) | {r.get('fase', '-')} | {', '.join(r.get('aceita') or []) or ('tudo' if r.get('conteiner') else '-')} | {f'{g[0]}×{g[1]}' if g else '-'} | "
                     f"{', '.join(f'{n} {t}' for t, n in vg.items()) or '-'} | {len(r.get('exibe', [])) or '-'} | {f'até {e['max']} × {nome(itens, e['item'])}' if e else '-'} |")
        L.append('')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    itens = carregar(); erros = checar(itens)
    for e in erros: print('ERRO', e)
    if '--checar' not in sys.argv:
        open(os.path.join(AQUI, 'CRAFT.md'), 'w', encoding='utf-8').write(md(itens)); print('props/CRAFT.md escrito')
    sys.exit(1 if erros else 0)
