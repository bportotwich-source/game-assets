# Pistola sinalizadora (refeita no nível da M4A1)

A pistola de sinal do jogo, no id `pistola_sinalizadora`, com os mesmos nós (cano, cartucho, cão,
gatilho, trava) e animações da antiga (`arma12_sinalizadora.py`). Desenho próprio, sem marcas de
fabricante.

Armação e cano de alumínio anodizado laranja; cano curto e grosso que bascula para baixo, com
culatra reforçada, coroa na boca e dente de mira; cão externo serrilhado; alavanca que solta o
cano do lado esquerdo; guarda-mato redondo; cabo curvo com talas pretas quadriculadas presas por
parafuso e olhal de cordão no pé. Gravações: `SINAL 12`, `SÓ CARTUCHO DE SINAL` e o número de série.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é a pistola |
| `materiais.py` | alumínio laranja, talas quadriculadas, casco vermelho do cartucho |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | nós e animações tirados da pistola antiga |

A armação com as talas é o grupo de textura A; cano, cartucho, cão, gatilho e trava são o B.

Números: 19.599 triângulos e 2 conjuntos 2048. Versão leve com 4.000 e 1 conjunto 1024.

## O que mudou de propósito

- A mira de trás virou um entalhe na armação, alinhado com o dente da boca do cano.
- As talas ficaram mais grossas e abauladas, para a mão fechar em volta do cabo.
