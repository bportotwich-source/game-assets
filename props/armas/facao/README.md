# Facão (refeito no nível da M4A1)

O facão do jogo, no id `facao`, com os mesmos pontos (`cinto`, `ponta`, `fio_meio`) e animações do
antigo (`arma19_facao.py`). Desenho próprio, sem marcas de fabricante.

Lâmina de 34 cm de aço carbono escurecido que alarga na ponta, com desbaste, fio polido e gravação;
espiga inteira aparente entre duas talas de madeira com veio, presas por três rebites de latão
vazados; bico no fim do cabo; ilhós de aço e fiel de couro com passador.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é o facão inteiro |
| `materiais.py` | aço da lâmina, madeira com veio, couro (usa classes do Brasa e do arco recurvo) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: origem, id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | pontos e animações tirados do facão antigo |

A lâmina tem 3 mm de espessura: fina demais para o desgaste de quina do bake (sai manchado), por isso a
classe `aco_facao` tem desgaste 0 e o brilho fica só no fio.

O contorno da lâmina é o mesmo do antigo, então a bainha de lona (`bainha_lona_facao`, ainda antiga)
continua servindo.
