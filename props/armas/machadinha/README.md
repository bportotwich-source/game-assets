# Machadinha tática (refeita no nível da M4A1)

A machadinha do jogo, no id `machadinha_tatica`, com os mesmos pontos (`capa`, `fio_meio`,
`ponta_tras`) e animações da antiga (`arma20_machadinha.py`). Desenho próprio, sem marcas.

Cabeça e espiga numa peça só de aço escurecido: fio curvo com barba, fio polido, ponta de trás para
arrombar, três furos de alívio e gravação. Talas de polímero verde-oliva presas com três pinos vazados,
cordão cor de areia enrolado no meio do cabo (as voltas vêm do relevo da textura), furo e argola de
cordão no pé.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é a machadinha inteira |
| `materiais.py` | aço da cabeça e cordão enrolado (usa classes da besta e do Brasa) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: origem, id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | pontos e animações tirados da machadinha antiga |

Números: 17.225 triângulos e 1 conjunto 2048. Versão leve com 4.000 e 1 conjunto 1024.

O contorno da cabeça é o mesmo da antiga, então a capa da lâmina (`capa_machadinha`, ainda antiga)
continua servindo.
