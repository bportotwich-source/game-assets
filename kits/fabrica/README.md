# Kit 29: fábrica europeia de tijolo (alto detalhe)

Fábrica de tijolo com galpão de cobertura em dente de serra, escritório de 3 andares na frente, 2 chaminés redondas e pátio murado. Feita no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original.

## O conjunto
- **Galpão** de 20 × 16 m. O piso fica a 0,3 m do chão, sobre um embasamento de pedra.
  - Paredes de tijolo com pilastras nos encontros dos módulos, embasamento de pedra que para nas portas e pilares de canto com cimalha e capa.
  - Janelas altas em arco abatido, com aduelas de tijolo escuro, fecho de pedra, peitoril de pedra com pingadeira e caixilho de aço de muitos vidros.
  - Frente e fundos com topo reto, cachorrada de tijolo (fiadas escalonadas e dentículos) e capa de pedra. Na frente há também uma fileira de janelas altas acima da cobertura.
  - As laterais acompanham o dente de serra e têm uma faixa inclinada de tijolo escuro.
- **Cobertura em dente de serra** com 4 dentes de 4 m. A telha de aço tem nervuras, e na crista de cada dente há uma vidraça vertical com montantes, travessas e rufo. Nos vales há calhas de zinco, que saem pelas laterais em funis e condutores até o chão. As bordas têm capa e testeira de zinco.
- **Estrutura de aço aparente**: vigas de vale em perfil I com enrijecedores, 6 pilares com chapa de base e mãos-francesas, tesouras inclinadas sob as terças e montantes que seguram as vidraças. Há 12 luminárias industriais penduradas nas vigas.
- **Portão de carga** em arco pleno de 3,2 m, com 2 folhas de tábuas, forro, travessas, mão-francesa, dobradiças compridas e argola de ferro. Em cima fica uma bandeira em leque com raios de aço. Na frente há uma rampa de concreto com cantoneiras.
- **Portas de serviço** nas 2 laterais e nos fundos, com caixilho de aço, bandeira em arco, soleira, degraus de pedra e luminária pescoço de ganso.
- **Escritório** de 10 × 8 m e 3 andares, encostado na frente do galpão:
  - tijolo com pilastras em L nas quinas da frente, faixa moldurada no 1º andar e peitoril corrido no 2º;
  - janelas de guilhotina com bandeira em arco, verga de aduelas de pedra com fecho e peitoril de pedra;
  - porta de entrada com vidro e grade, ombreiras de pedra em blocos, verga em arco, degraus e 2 arandelas;
  - platibanda com faixa de pedra, cachorrada e capa;
  - caixa d'água de madeira no terraço, com aduelas, cintas de ferro, tampa cônica e escada, sobre uma torre de aço;
  - no 1º andar, janelas que dão para dentro do galpão.
- **Dentro do escritório**:
  - escada de 2 lances do térreo ao 2º andar, com corrimão, balaústres e guarda-corpo em volta dos vãos;
  - saguão e hall da escada com piso xadrez, salas com tacos;
  - porta de aço do térreo para o galpão;
  - portas internas almofadadas com guarnição, e rodapés que param nas portas.
- **Pátio**: 2 chaminés redondas de 24 m, cada uma com base quadrada com almofadas e cimalha de pedra, fuste cônico com cintas de ferro, 2 anéis de pedra, coroa de tijolo em balanço, escada de grampos e para-raios. Há também um muro de tijolo com pilares e capa de pedra, um portão de ferro de 2 folhas com lanças e caminhos de concreto.

Números: 118 peças, 456 posições, 18 portas, cerca de 249 mil triângulos no montado.

## Montagem
O galpão ocupa x de -10 a 10 e z de -10 a 6. O escritório ocupa x de -10 a 0 e z de 6 a 14, com a frente para +Z.
- Paredes do galpão (pivô na face externa, na cota do piso):
  - `h_back_*` são as dos fundos e `h_front_*` as da frente. `h_front_gate` é o módulo de 4 m do portão.
  - `h_side_*_r0`, `_r1`, `_l0` e `_l1` são as laterais, com topo inclinado (r = direita e l = esquerda, 0 = primeira metade do dente e 1 = segunda).
  - `h_pier_low` e `h_pier_high` são os pilares de canto.
- Cobertura (pivô no eixo do módulo, no vale do dente, na cota do piso):
  - `roof_tooth` é o módulo de 2 m de um dente, com a vidraça. `roof_tooth_end` é o último dente, que encosta na frente e no escritório.
  - `rafter`, `girder` e `column` formam a estrutura de aço.
  - `verge_r*` e `verge_l*` são os arremates das laterais, com o condutor.
- Escritório:
  - `o_g_*`, `o_u1_*` e `o_u2_*` são as paredes do térreo, do 1º e do 2º andar, e `o_parapet` é a platibanda.
  - A parede do fundo do escritório (z = 6) é também a parede do galpão e vai girada 180°. `o_g_door_in` é a porta para o galpão.
  - `o_corner_*` são as quinas da frente e `o_corner_back_*` as do fundo.
- Escada: `stair` sobe para -Z e `stair_both` é o 2º lance, girado 180°. Os vãos nas lajes estão em `building_layout.json` (`stair_holes`). `rail_*` são os guarda-corpos.
- Pisos: `floor_<tipo>_<g|u|r>` são as placas de 2 × 2 m. `_e####` param na face interna das paredes externas (flags x-, x+, z-, z+), e `_h#` têm vão de escada.
- Portas: a folha da direita do portão de carga e a do portão de ferro vão giradas 180° e abrem com ângulo negativo.

## Texturas (PBR, embutidas nos GLB como JPEG)
`brick`, `brick2`, `trim`, `plinth`, `plaster`, `floor`, `concrete`, `membrane`, `marble`, `gatewood`, `wood` e `tank`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador entra pelo portão do pátio, sobe a rampa e passa o portão de carga até o galpão; entra pelas 3 portas de serviço (direita, esquerda e fundos) e cruza o galpão; entra pela porta do escritório até o saguão; vai do saguão ao hall da escada; sobe o 1º lance (3,5 m) e o 2º (6,7 m); no 1º andar passa do patamar para a sala dos fundos; e passa da sala dos fundos do térreo para o galpão.

No visitante, é o prédio 29 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/fabrica/gerar_kit.py        # escreve em out/ ao lado do script
python kits/fabrica/verificar_flicker.py
```
