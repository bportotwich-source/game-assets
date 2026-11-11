# Bastões com pregos e com arame farpado (refeitos no nível da M4A1)

Os dois bastões do jogo, nos ids `bastao_pregos` e `bastao_arame`, com os mesmos pontos (`mao_cima`,
`barril`, `ponta`) e animações dos antigos (`arma22_bastao.py`). Desenho próprio, sem marcas.

Taco de freixo claro com pomo, cabo fino enrolado em fita isolante (as voltas vêm do relevo da
textura) e barril grosso com mossas de uso. Na parte grossa, ou uns vinte pregos batidos, alguns
entortados e enferrujados, ou arame farpado de dois fios torcidos, com farpas de quatro pontas e as
pontas amarradas.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar_pregos()` e `montar_arame()` |
| `materiais.py` | madeira do taco, fita, pregos e arame (o veio da madeira é o do facão) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: origem, ids |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py pregos 2048 saida_pregos` (ou `arame`) |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py pregos saida_pregos` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto_pregos.json`, `esqueleto_arame.json` | pontos e animações tirados dos bastões antigos |

Números: com pregos 12.308 triângulos, com arame 33.968, cada um com 1 conjunto 2048. Versões leves
com 4.000 e 3.824 triângulos e 1 conjunto 1024.
