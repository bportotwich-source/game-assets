# Punhos de pistola dos fuzis (refeitos no nível da M4A1) e a troca entre armas

`punho_ar`, `punho_cavas` e `punho_reto` (e os `_tan`, caramelo), nos mesmos ids e no mesmo encaixe
(`encaixe_punho`, tipo `punho_ar`) dos antigos. Desenho próprio, sem marcas. São montados nas
coordenadas da M4A1 e recortados pela linha de baixo do receptor dela, por isso assentam sem folga.

| Id | O que é |
|---|---|
| `punho_ar` | o original: polímero quadriculado dos lados, ressalto do dedo médio, base oca com o parafuso |
| `punho_cavas` | borracha com grão de pedrinhas, três cavas para os dedos, palma cheia e sapata na base |
| `punho_reto` | mais em pé, rabo de castor, painéis de pontilhado fino, nervuras e tampa do compartimento |
| `adaptador_punho_762` | sapata de aço que o jogo põe sozinho quando um punho de 7,62 entra num fuzil de alumínio (não é item) |

    python3 gerar.py <id> 1024 saida && python3 jogo.py <id> saida          # VARIANTE=tan para os caramelo
    python3 encaixes.py                                                    # encaixes e ajustes no catálogo e nos GLBs

De 2.780 a 5.226 triângulos, 1 conjunto de textura 1024 cada.

## Punho de uma arma na outra (`encaixes.py`)

- **Punhos do AKMN (`punho_akmn`, `punho_tatico_akmn`, modelos de suspensy, CC BY 4.0) nos fuzis de
  alumínio** (5,56, M4A1, .308 de precisão, carabina .308): o `encaixe_punho` dessas armas ganhou o
  campo `ajuste`, que diz onde o punho de outro tipo fica:

      "ajuste": {"punho_ak": {"posicao_m": [0, -0.048, 0.017], "inclinacao_graus": 10.0, "com": "adaptador_punho_762"}}

  O jogo põe o acessório em `posicao_m` (em relação ao nó do encaixe), gira `inclinacao_graus` para
  trás em volta do eixo X (o punho fica no ângulo da mão da arma) e monta a peça `com` ao lado, sem
  ajuste. O centro do punho cai na origem da arma, que é onde a mão fecha.
- **Brasa 7,62 (`fuzil_762`, `fuzil_762_tatico`)**: o punho, que era fixo, foi para o nó `punho` e
  nasceu o `encaixe_punho` (tipo `punho_ak`), que aceita os dois punhos do AKMN. O `ajuste` sobe o
  punho 19 mm, porque o receptor do Brasa fica mais alto em relação à mão.
- **Carabina .308 de chassi (`carabina_308`)**: mesma coisa, com `encaixe_punho` do tipo `punho_ar`:
  aceita os punhos dos fuzis e, com o adaptador, os do AKMN.

Ficaram de fora: pistolas, submetralhadoras, espingarda e rifle .22 (o punho é parte do corpo ou
da coronha) e os punhos de alumínio no AKMN e no Brasa (não há adaptador nesse sentido).
