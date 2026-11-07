# Kit 26: vila urbana (alto detalhe)

Vila urbana de 2 andares no estilo das Stadtvillen europeias, num jardim cercado por gradil. Feita no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original.

## O conjunto
- **Corpo** de 14 × 10 m. O piso do térreo fica a 0,75 m, sobre um embasamento de pedra. Cada andar tem 3,2 m, com laje de 0,25 m.
- **Térreo**: reboco rusticado em 6 fiadas chanfradas, que dobram as quinas. As janelas de abrir têm bandeira, moldura de pedra, peitoril com mísulas e aduela. A porta principal é dupla, com bandeira em leque, e a porta dos fundos tem degraus de pedra e arandela.
- **Andar de cima**: reboco rosado com cunhais de pedra alternados, faixa moldurada entre os andares e cornija com modilhões sob o beiral. As janelas têm cornija de coroamento com mísulas e venezianas de palhetas em geometria. As janelas das quinas não têm venezianas, para não bater nos cunhais.
- **Telhado** de 4 águas a 35° em ardósia, com fiadas em geometria, testeira, calhas K em meia-esquadria, 4 condutores, espigões e cumeeira com remates. Ele tem ainda:
  - um frontão triangular de 3,9 m sobre o eixo, com óculo, cornija inclinada, acrotérios e um telhadinho que entra no telhado principal;
  - 3 águas-furtadas com frontão, janela de 2 folhas e ilhargas;
  - 2 chaminés de tijolo com 3 manilhas.
- **Pórtico**: 2 colunas toscanas com êntase carregam a sacada de balaústres torneados, que tem porta dupla envidraçada e lanterna pendente. Na frente há um patamar de pedra com 5 degraus de 0,15 m e muretas laterais.
- **Dentro** há um hall central de 6 m com escada reta de madeira (18 espelhos, corrimão, balaústres e pilarete) e guarda-corpo em volta do vão no andar de cima.
  - No térreo ficam 2 salas, um escritório e a cozinha.
  - No andar de cima ficam 3 quartos e o banheiro, com piso de pastilhas.
  - As portas internas são almofadadas, com guarnição, e os rodapés param nas portas.
- **Jardim** de 18 × 18 m: gradil de ferro com pontas de lança sobre mureta de pedra, pilares com bola, portão de 2 folhas com volutas e caminho de lajes.

Números: 69 peças, 297 posições, 15 portas, cerca de 145 mil triângulos no montado.

## Montagem
O corpo ocupa x de -7 a 7 e z de -5 a 5, com a frente para +Z. O pórtico vai de z 5 a 6,7 e os degraus até 8,2. O gradil fica em x ±9 e em z de -8 a 10.
- `g_wall_*` são as paredes do térreo: pivô na face externa, na cota do piso do térreo, com altura até a face de baixo da laje.
- `u_wall_*` são as paredes do andar de cima: pivô na cota do piso de cima, começando 0,25 m abaixo (dentro da laje), até o beiral.
- `corner_ground` e `corner_upper` são as quinas dos 2 andares, com faixa e cornija em meia-esquadria.
- Telhado:
  - `roof_main_*` e `roof_hip_*` são faixas de 2 m de cada água, com pivô na face da parede e na cota do piso do térreo.
  - `hip_cap` vai nas 4 quinas e `ridge_cap` é uma peça só.
  - `pediment` e `dormer` vão sobre o telhado, com a mesma referência das faixas.
- Lajes do andar de cima:
  - `floor_tile_e####` param na face interna das paredes externas (flags x-, x+, z-, z+).
  - `floor_tile_hole_*` têm o vão da escada.
- Portas: a folha da direita das portas duplas vai girada 180° e abre com -85°.

## Texturas (PBR, embutidas nos GLB como JPEG)
`rust`, `render`, `trim`, `plinth`, `shingles` (ardósia), `floor`, `plaster`, `shutter`, `brick`, `stone2` e `wood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador passa pelo portão, sobe os degraus do pórtico, entra pela porta dupla, cruza o hall e sai pela porta dos fundos; sobe a escada interna até o andar de cima; sai para a sacada (a balaustrada segura o jogador); entra numa sala do térreo e no banheiro do andar de cima pelas portas internas.

No visitante, é o prédio 26 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
python kits/vila-urbana/gerar_kit.py        # escreve em out/ ao lado do script
python kits/vila-urbana/verificar_flicker.py
```
