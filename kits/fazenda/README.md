# Kit 44: fazenda americana (alto detalhe)

Sede de fazenda com casa de 2 andares, varanda, celeiro vermelho de telhado holandês, silo, cata-vento e horta. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto.

## O conjunto
- **Casa** de 10 × 8 m, 2 andares de 3 m sobre embasamento de pedra (piso a 0,6 m):
  - tábuas sobrepostas brancas, cinta entre os andares, friso sob o beiral, cantoneiras e venezianas verdes;
  - telhado de 2 águas a 40° de telhas, com calhas, condutores, testeiras, forro do beiral, cumeeira e 2 chaminés de tijolo com rufo;
  - oitões de tábuas com janelinha do sótão;
  - porta da frente almofadada com arandela, porta dos fundos com escadinha.
- **Varanda** na frente: deck de tábuas a 0,57 m, 6 colunas torneadas, guarda-corpo de balaústres, escada e telhado de 1 água com forro, calha e 2 lanternas.
- **Dentro**:
  - **Térreo**: hall com escada reta de 16 degraus (corrimão, balaústres e pilar de arranque torneado); sala com lareira de tijolo, sofá, poltrona, cadeira de balanço, mesinha com lampião, estante e tapete; cozinha de piso xadrez com fogão a lenha, pia com bomba, geladeira de gelo, armário e mesa com cadeiras; cabideiro no hall.
  - **Em cima**: 2 quartos com cama de ferro, cômoda, guarda-roupa, baú e tapete; banheiro com banheira de pés, vaso com caixa alta e pia de coluna; guarda-corpo em volta do vão da escada.
- **Celeiro** de 16 × 18 m: tábuas verticais vermelhas com mata-juntas, telhado holandês de chapa ondulada, rufos, calhas e cúpula com venezianas e cata-vento; portão de 2 folhas com X, porta do palheiro com capuz da talha, 3 portas de serviço e janelas de caixilho. Dentro: corredor de concreto com canaleta, baias, jiraus com fardos de feno, garfos no suporte e carrinho de mão.
- **Fora**:
  - silo de concreto com cúpula, escada com gaiola e tubo de carga;
  - cata-vento de 4 pés com bomba e tanque de água para o gado;
  - horta cercada de pique com portão: milho, tomates, repolhos, abóboras e espantalho;
  - carroça de feno, poço com bomba de mão, pilha de lenha, varal, pomar, caixa de correio;
  - cerca de 3 travessas em volta de tudo, gramado, pátio de brita, entrada e estrada com faixa amarela.

Números: 97 peças, 436 posições, 13 portas, cerca de 291 mil triângulos no montado.

## Montagem
A casa fica na origem, com a frente para +Z: x de -5 a 5, z de -4 a 4, pisos em 0,6 e 3,6, beiral em 6,57 e cumeeira em 9,93. A varanda vai até z = 6,4. O celeiro ocupa x de -14 a 2 e z de -31 a -13, com o portão na frente (z = -13) e piso em 0,15. O silo fica em (-16,95; -25), o cata-vento em (-25; -6) e a horta entre x = -22 e -10. O terreno vai de x = -34 a 30 e de z = -36 a 28 (os números estão em `building_layout.json`).
- **Paredes da casa** (pivô na face externa, cota do andar): `h_win0`, `h_win0_ns`, `h_door0`, `h_plain0`, `h_win1`, `h_win1_ns`, `h_small1`, `h_plain1` (as `_ns` não têm veneziana do lado do condutor), `h_corner`, `h_gable`.
- **Telhado da casa**: `roof_slope`, `roof_ridge`, `chimney_stack`, `downspout_house`, `slab2`.
- **Dentro** (pivô na origem): `floor0`, `slab1`, `plan0`, `plan1`, `stair`, `stair_rail`, `fireplace`, `chimney_breast`.
- **Varanda**: `porch_deck`, `porch_steps`, `porch_post`, `porch_rail_18`, `porch_rail_19`, `porch_rail_side`, `porch_roof`, `back_steps`.
- **Portas** (pivô na dobradiça): `door_leaf_front`, `door_leaf_back`, `door_leaf_int` (5), `barn_door_leaf` (2), `barn_door_small` (3), `picket_gate`.
- **Móveis**: `sofa`, `armchair`, `rocking_chair`, `side_table`, `bookcase`, `hall_tree`, `rug`, `rug_s`, `wood_stove`, `sink_cabinet`, `icebox`, `hutch`, `kitchen_table`, `bed`, `dresser`, `wardrobe`, `chest`, `clawfoot_tub`, `toilet_tank`, `pedestal_sink`.
- **Celeiro**: `barn_wall_plain`, `barn_wall_window`, `barn_wall_door`, `barn_wall_bigdoor`, `barn_corner`, `barn_gable_front`, `barn_gable_back`, `barn_roof`, `barn_roof_end`, `cupola`, `downspout_barn`, `barn_floor`, `barn_ramp`, `barn_ramp_small`, `lofts`, `stalls`, `bale`, `tool_rack`, `wheelbarrow`.
- **Fora**: `silo`, `windmill`, `stock_tank`, `garden`, `picket`, `picket_1`, `picket_post`, `rail_fence`, `rail_fence_2`, `rail_post`, `hay_wagon`, `hand_pump`, `woodpile`, `clothesline`, `mailbox`, `site`, `tree`, `tree_b`, `tree_f`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`siding`, `barn`, `shingles`, `stone`, `brick`, `plaster`, `ceiling`, `floor`, `deck`, `planks`, `wood`, `dkwood`, `rail`, `cap`, `concrete`, `silo_c`, `gravel`, `asphalt`, `grass` e `soil`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 7 caminhos:
  - da estrada, sobe a entrada até o pátio;
  - da frente, sobe a escada da varanda e entra pela porta da frente até o hall;
  - do hall, entra na sala pela porta;
  - do hall, entra na cozinha pela porta;
  - do pátio, entra no celeiro pelo portão grande;
  - entra na horta pelo portão;
  - dos fundos, sobe a escadinha e entra pela porta dos fundos.

No visitante, é o prédio 44 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/fazenda/gerar_kit.py        # escreve em out/ ao lado do script
python kits/fazenda/verificar_flicker.py
```
