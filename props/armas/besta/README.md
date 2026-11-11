# Besta recurva (refeita no nível da M4A1)

A besta do jogo, no id `besta_recurva`, com os mesmos nós (braços, metades da corda, trava, gatilho,
segurança, virote), encaixes (luneta, alça e massa rebatíveis, estribo, trilho curto) e animações da
antiga (`arma17_besta.py`). Desenho próprio, sem marcas de fabricante. O modelo parado está armado e
carregado, como o antigo.

Coronha esqueletada de polímero verde-oliva com soleira de borracha frisada e apoio de rosto; caixa do
gatilho preta com painéis verdes, parafusos, gravações, trava de corda de aço e segurança dos dois
lados; punho pontilhado; trilho de voo de alumínio com canaleta e fita de deslize; guarda-mão com
frisos de borracha e abas que protegem os dedos; UM trilho curto embaixo (lanterna ou laser); cabeça
de alumínio com bolsos, parafusos e batentes de borracha; braços recurvos de fibra com faixa de
carbono e ponta de reforço; corda torcida com reforços e silenciadores; virote de carbono com penas e
ponta de caça.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é a besta com o virote |
| `materiais.py` | polímero oliva, alumínio da cabeça, corda (usa as classes de `../composto` e `../recurvo`) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | nós e animações tirados da besta antiga |

A coronha, a caixa do gatilho e o punho são o grupo de textura A; trilho de voo, cabeça, braços, corda,
trava, gatilho, segurança e virote são o B.

Números: 37.220 triângulos e 2 conjuntos 2048. Versão leve com 6.000 e 1 conjunto 1024.

## O que não mudou (as animações dependem disso)

- Eixo dos braços na cabeça, ponto onde a corda deixa o braço, posição da corda armada e solta.
- Eixos da trava, do gatilho e da segurança; posição do virote; altura dos trilhos de mira.

Ainda antigos: os virotes soltos (`municao/virote_*`), a luneta da besta, a alça e a massa rebatíveis
e o estribo.
