# Fuzil Brasa 7,62 e 7,62 tático (refeitos no nível da M4A1)

O fuzil 7,62 do jogo, no id `fuzil_762`, com os mesmos nós, encaixes e animações do antigo
(`arma06_ak.py`), mais os três acessórios que vêm montados nele: `coronha_madeira_ak`,
`guarda_mao_madeira_ak` e `freio_ak`. Desenho próprio, sem marcas de fabricante.

Receptor estampado com rebites, covas acima do poço e trilho lateral; tampa nervurada com janela
de ejeção; transportador polido com alavanca de manejo; seletor de alavanca; alça tangente e torre
da massa com orelhas; bloco de gás, vareta de limpeza, carregador curvo de aço com um cartucho à
vista; punho arredondado de baquelite quadriculado; coronha e guarda-mão de madeira laminada.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é o fuzil; `coronha_madeira()`, `guarda_mao_madeira()` e `freio()` são os acessórios |
| `materiais.py` | aço oxidado, madeira laminada (folhas em pé) e baquelite quadriculada |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, ids (arma e acessórios) |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida`; `... 1024 saida_coronha coronha` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida`; `... saida_coronha coronha` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura); `MONTAR=montar,coronha_madeira,...` e `FOTO_ACESSORIOS=pasta` mostram o fuzil montado |
| `esqueleto*.json` | nós e animações tirados do fuzil e dos acessórios antigos |

Acessórios: `coronha` e `guarda_mao` em 1024, `freio` em 512. Gere os acessórios antes do fuzil
(o `ref_coronha` do fuzil sai da coronha).

Números: fuzil 35.877 triângulos e 2 conjuntos 2048; com coronha (7.100), guarda-mão (9.084) e
freio (1.448) são 53,5 mil na mão. Versão leve com 6.000 e 1 conjunto 1024.

## Fuzil tático (`fuzil_762_tatico`)

O mesmo fuzil, preto e bem usado, com punho e carregador de polímero e o recado "NÃO DESISTA"
riscado na chapa. Sai com `VARIANTE=tatico` (`esqueleto_tatico.json`):

    VARIANTE=tatico python3 gerar.py 2048 saida_tatico && VARIANTE=tatico python3 jogo.py saida_tatico

As peças que vêm montadas nele são acessórios à parte, cada um em 1024, na versão nova
(sem `VARIANTE`) e na usada (`VARIANTE=gasto`, id com `_gasto`, que é a que o fuzil traz):

| Nome no `gerar.py` | id | Triângulos |
|---|---|---|
| `coronha_esq` | `coronha_esqueleto_ak[_gasto]` | 7.086 |
| `guarda_mao_fendas` | `guarda_mao_fendas_ak[_gasto]` | 9.024 |
| `tampa_trilho` | `tampa_trilho_ak[_gasto]` (entra no lugar da tampa do fuzil) | 3.324 |

    VARIANTE=gasto python3 gerar.py 1024 saida_coronha_esq coronha_esq && VARIANTE=gasto python3 jogo.py saida_coronha_esq coronha_esq

Números: fuzil 35.499 triângulos; na mão, com as três peças e os acessórios antigos (supressor,
lanterna, mira reflexa, tiras de borracha), 57 mil. Para ver montado:
`FOTO_MONTAR=a.blend,b.blend python3 foto.py saida_tatico/brasa_tatico.blend prefixo esq`.

## O que mudou de propósito

- A alavanca do seletor é mais curta: no modo semi ela não sai mais para baixo do receptor.
- A tampa vai até o bloco da alça, e a folha da alça deita sobre um bloco mais alto (a linha de
  visada e o nó `mira_ferro` não mudaram).
- A coronha ficou 15 mm mais baixa na soleira.
- No tático, o supressor, a lanterna, a mira reflexa e as tiras de borracha continuam sendo os
  modelos antigos, assim como os outros acessórios do 7,62 (carregadores avulsos, outras coronhas).
