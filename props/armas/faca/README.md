# Faca de combate (refeita no nível da M4A1)

A faca do jogo, no id `faca_combate`, com os mesmos pontos (`cinto`, `ponta`, `fio_meio`) e animações
da antiga (`arma18_faca.py`). Desenho próprio, sem marcas de fabricante.

Lâmina de 18 cm de aço escurecido com ponta recortada, falso fio, desbaste plano, fio polido, serrilha
perto do cabo, cava do dedo, sulco dos dois lados e gravações; guarda de aço com o braço de baixo
curvado para a frente; espaçador de aço; cabo de polímero pontilhado com frisos e cavas para os dedos;
pomo com quebra-vidro, furo e cordão.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é a faca inteira |
| `materiais.py` | só junta as classes das outras armas (aço do Brasa, pega dos arcos, cordão da besta) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: origem, id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | pontos e animações tirados da faca antiga |

Números: 15.045 triângulos e 1 conjunto 2048. Versão leve com 3.000 e 1 conjunto 1024.

O contorno da lâmina é o mesmo da antiga, então a bainha de cinto (`bainha_cinto_faca`, ainda antiga)
continua servindo.
