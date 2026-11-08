# Kit 31: casas vitorianas coloridas (alto detalhe)

Fileira de 5 sobrados vitorianos geminados de madeira, cada um com uma cor. Feita no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original.

## O conjunto
- **5 casas** de 6 × 12 m, lado a lado, com 30 m de fileira. Cada casa tem:
  - porão alto de 1,5 m;
  - 2 andares de 3,2 m (laje de 0,2 m);
  - frontão de 50° virado para a rua.
- **Cores**: amarelo, verde-sálvia, verde-água, azul e coral. Cada casa tem uma cor de corpo, uma cor de destaque (porão, escamas, almofadas) e uma cor de porta. O acabamento é creme em todas.
- **Fachada de tábuas sobrepostas** em geometria:
  - **bay window chanfrada** de 2 andares, com 3 guilhotinas por andar, colunetas torneadas nas quinas, almofadas, faixa entre os andares e cornija própria;
  - janelas de guilhotina com peitoril, avental, mísulas, chapéu e frontãozinho no térreo;
  - porta com bandeira de 3 vidros, pilastras com almofada, mísulas e chapéu, e folha com 2 vidros em arco e almofadas;
  - cornija italianizante com friso, faixa de cor, dentículos, mísulas e coroa;
  - pilastras de tábua nas divisas entre as casas e cantoneiras nas quinas das pontas.
- **Porão**: fundação de pedra, almofadas com moldura, respiros com grade e mesa de água com pingadeira. Os frisos param nas escadas.
- **Frontão da rua**:
  - escamas de peixe em fiadas e par de janelas em arco com moldura, peitoril e fecho;
  - tesoura decorativa com fusos, raios e meia-roda;
  - lambrequim recortado nas empenas e pináculo com ponta de ferro.
- **Frontão dos fundos**: tábuas e veneziana redonda.
- **Telhado**:
  - telhas em fiadas a 50° e cumeeira;
  - testeiras nas empenas;
  - rufos de chapa nos vales entre as casas;
  - nas casas das pontas, beiral com cachorros, calha e condutores.
- **Escada de entrada** de 10 degraus:
  - patamar e degraus de madeira;
  - corpo pintado com longarinas e almofadas na cor de destaque;
  - balaústres torneados e corrimão;
  - postes torneados com globo de luz embaixo.
- **Escada dos fundos** no mesmo estilo, para o quintal.
- **Rua**: jardim na frente de cada casa, gradil de ferro com lanças sobre mureta (aberto na escada), calçada com meio-fio e 2 postes de lampião.
- **Dentro de cada casa**:
  - **Térreo**: hall com piso xadrez, sala e jantar juntos, cozinha com ladrilho e hall dos fundos com a escada.
  - **Escada** reta de 18 degraus, com corrimão e balaústres torneados e armário embaixo.
  - **1º andar**: patamar com guarda-corpo, quarto da frente e quarto dos fundos.
  - **Acabamentos**: portas internas almofadadas com guarnição, e rodapés que param nas portas.
  - **Entre as casas**: paredes-meias de 30 cm.
  - **Sótão**: fechado, com forro de gesso.

Números: 193 peças, 646 posições, 30 portas, cerca de 481 mil triângulos no montado.

## Montagem
As casas ficam em x = -12, -6, 0, 6 e 12 (cada uma de -3 a 3 em volta do centro), z de -6 a 6, com a frente para +Z. O piso do térreo fica em 1,5, o do 1º andar em 4,7, e o beiral em 7,9.
- **Peças com cor** (sufixo `_a` a `_e`, uma letra por casa):
  - **Paredes** (pivô na face externa, na cota do piso): `f_g_*` e `f_u_*` são as do térreo e do 1º andar, com os tipos `win`, `plain`, `bay` e `door`. `b_*` são as dos fundos, e as laterais das pontas usam `f_*_win` e `f_*_plain`.
  - **Bay window**: `bay_base`, `bay_g` e `bay_u` (com a cornija), com pivô na face da parede, no eixo do módulo.
  - **Frontões e cornija**: `gable_front` e `gable_back` (pivô no eixo da casa, na cota do beiral; o dos fundos vai girado 180°) e `cornice` (módulo reto).
  - **Divisas e quinas**: `pilaster_g` e `pilaster_u` (na divisa) e `corner_g` e `corner_u` (quinas das pontas).
  - **Escadas e porta**: `stoop`, `back_stoop` e `door_leaf_front`.
- **Telhado** (pivô no plano da parede-meia ou da lateral, na cota do beiral, girado ±90°):
  - `roof_valley*` é a água que desce até um vale, e `roof_eave*` a que tem beiral com calha.
  - `_a` e `_b` são as faixas das pontas, com testeira e avanço de 0,45 m.
  - `ridge` é a cumeeira, `valley` o rufo do vale e `downspout` o condutor.
- **Interior**:
  - `party_g` e `party_u` são as paredes-meias.
  - `iw_*` são as paredes internas de 2 m, e `iw_cross` é a parede entre os quartos.
  - `stair` sobe para -Z (vai girada 180°). O vão na laje está em `building_layout.json` (`stair_holes`, em coordenadas da casa).
  - `rail_*` são os guarda-corpos.
- **Pisos**: `floor_<tipo>_<g|u|c>` são as placas de 2 × 2 m (g = térreo, u = 1º andar, c = forro do sótão). `_e…` marca o recuo em cm de cada lado (x-, x+, z-, z+), e `_h#` tem vão de escada.
- **Rua**: `lawn`, `sidewalk`, `fence`, `fence_post` e `street_lamp`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`siding_a` a `siding_e`, `shingles`, `deck`, `floor`, `attic`, `plaster`, `concrete` e `plinth`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3:
  - o jogador sobe a escada de entrada das casas e entra pela porta até o hall;
  - vai do hall para a sala e da sala para o hall dos fundos;
  - sobe a escada até o 1º andar (4,7 m) e entra no quarto da frente e no dos fundos;
  - sai pela porta dos fundos e desce a escada até o quintal.

No visitante, é o prédio 31 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/casas-vitorianas/gerar_kit.py        # escreve em out/ ao lado do script
python kits/casas-vitorianas/verificar_flicker.py
```
