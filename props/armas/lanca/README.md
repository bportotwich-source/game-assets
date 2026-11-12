# Lança improvisada (refeita no nível da M4A1)

A lança do jogo, no id `lanca_improvisada`, com os mesmos pontos (`mao_frente`, `amarracao`, `faca`)
e animações da antiga (`arma21_lanca.py`). Desenho próprio, sem marcas.

Cabo de vassoura pintado de azul, com a tinta lascada mostrando a madeira, rosca de plástico e cordão
de pendurar atrás, pega de pano vermelho enrolado e um trecho de fita prata. Na ponta serrada, uma
faca de cozinha presa com prego, duas abraçadeiras, fita e arame (as voltas da fita e do pano vêm do
relevo da textura).

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é a lança inteira |
| `materiais.py` | cabo pintado, pano, fita, plástico e aço de cozinha (usa classes dos bastões) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: origem, id, nós |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | pontos e animações tirados da lança antiga |

Números: 16.514 triângulos e 1 conjunto 2048. Versão leve com 4.000 e 1 conjunto 1024.

Cuidado: classe de material com nome começando em `tinta` é tratada pela fábrica como gravação
pintada e sai da versão leve. Por isso a tinta do cabo se chama `cabo_pintado`.
