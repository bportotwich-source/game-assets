# Fuzil Brasa 7,62 (refeito no nível da M4A1)

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

## O que mudou de propósito

- A alavanca do seletor é mais curta: no modo semi ela não sai mais para baixo do receptor.
- A tampa vai até o bloco da alça, e a folha da alça deita sobre um bloco mais alto (a linha de
  visada e o nó `mira_ferro` não mudaram).
- A coronha ficou 15 mm mais baixa na soleira.
- O `fuzil_762_tatico` e os outros acessórios do 7,62 continuam sendo os modelos antigos.
