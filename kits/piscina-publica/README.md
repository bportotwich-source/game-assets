# Kit 45: piscina pública dos anos 50 (alto detalhe)

Clube de piscina de bairro: vestiário de tijolo na frente, deck de concreto cercado por gradil atrás, piscina de 25 m com raias, trampolins, escorregador e área de jatos. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: a flâmula do mastro é inventada (campo verde-água com uma boia), os quadros do saguão só têm pictogramas e o relógio não tem números.

## O conjunto
- **Vestiário** de 20 × 8 m, piso a 0,15 m, forro a 3 m:
  - tijolo com embasamento de concreto, cinta de concreto no peitoril das janelas altas, friso sob o beiral, vergas e soleiras de concreto (o embasamento e a cinta param nas portas);
  - janelas altas de caixilho de aço com vidro canelado;
  - telhado de 4 águas a 24° de telhas em fiadas, com espigões, cumeeira, testeira e calha em meia-esquadria, forro do beiral com respiros, 4 condutores, 2 respiros de chapa e 2 tubos de ventilação;
  - frente com porta dupla de vidro e bandeira sob uma marquise azul de 2 colunas, guichê da bilheteria com balcão, passa-troco e toldo;
  - fundos com porta de vidro do saguão, 2 portas de chapa dos vestiários, arandelas e boias de salvamento.
- **Dentro** (azulejo até 1,5 m com rodapé e capa):
  - **Saguão** de granilite com faixa: caixa com bancada sob o guichê, balcão, portinhola, caixa registradora e banqueta; banco, bebedouro, relógio, 2 quadros de pictogramas, vasos, lixeira e capacho.
  - **Vestiário masculino**: piso xadrez, 2 armários de aço, 2 bancos, 3 chuveiros com divisórias e mureta, 2 boxes de vaso, 2 mictórios com divisórias, pias com espelho e toalheiro.
  - **Vestiário feminino**: o mesmo, com os boxes na parede leste e uma segunda bancada de pias no lugar dos mictórios.
- **Piscina** de 25 × 12 m (1 m na parte rasa, 3,6 m na funda), com borda boleada, faixa de azulejo na linha d'água, 5 raias pintadas no fundo com alvos nas cabeceiras, água transparente, 4 raias de boias, 5 blocos de largada, 4 escadinhas de inox e 3 degraus na ponta rasa.
- **Deck** de concreto com juntas e ralos:
  - trampolins de 1 m e de 3 m (torre de aço com escada);
  - escorregador de calha em curva com torre e escada;
  - 2 cadeiras de salva-vidas com guarda-sol;
  - 3 mesas com guarda-sol e 4 cadeiras cada uma, 8 espreguiçadeiras;
  - área de jatos com cogumelo de água, arco de chuveiros e bicos no chão;
  - mastro com flâmula, relógio de poste, 2 chuveirinhos, 4 boias de resgate, filtros de areia com bomba, lixeiras.
- **Gradil** de ferro em volta do deck, gramado com canteiros e arbustos, calçada, rua com faixa amarela, postes, bancos de praça, bicicletário e árvores.

Números: 76 peças, 285 posições, 7 portas, cerca de 191 mil triângulos no montado.

## Montagem
O vestiário fica na origem, com a frente para +Z (rua): x de -10 a 10, z de -4 a 4. As divisórias do saguão ficam em x = -4 e 4, com as portas em z = -2,4. A piscina vai de x = -14 a 11 e de z = -24 a -12, com o deck em 0,12 e a água em -0,13. O gradil vai de x = -18 a 18 e de z = -30 a 4. A área de jatos fica em (14; -0,6). O terreno vai de x = -24 a 24 e de z = -36 a 18 (os números estão em `building_layout.json`).
- **Paredes** (pivô na face externa, no chão): frente e fundos com `w_win`, `w_win_s`, `w_ticket`, `w_entry` (4 m), `w_gdoor` (4 m), `w_door`, `w_end_l` e `w_end_r` (as das pontas, com o azulejo parando na lateral); laterais com `w_side` (1,85 m); quinas `w_corner` e `w_corner_b`.
- **Telhado** (pivô na origem): `roof_main` (frente e fundos), `roof_end` (pontas, no fim da cumeeira), `roof_ridge`, `roof_vent`, `vent_pipe`, `downspout`; `ceiling` e `ceiling_light`.
- **Fachada**: `entry_canopy`, `wall_lamp`, `lifebuoy_wall`.
- **Dentro**: `floor_lobby`, `floor_lr` (os 2 vestiários, girado 180°), `partition`, `cashier`, `lobby_bench`, `fountain`, `wall_clock`, `poster`, `poster_b`, `plant_pot`, `trash_can`, `lockers`, `lr_bench`, `shower_bay`, `stalls`, `wc`, `urinal`, `urinal_screen`, `sink_bank`, `towel_disp`.
- **Portas** (pivô na dobradiça): `door_leaf_glass` (2 folhas), `door_leaf_back`, `door_leaf_metal` (2), `door_leaf_int` (2).
- **Piscina e deck**: `deck`, `coping`, `basin` (pivô na origem); `ladder`, `start_block`, `lane_rope`, `lane_anchor`, `board_1m`, `board_3m`, `water_slide` (pivô na borda da água, local +Z para dentro da piscina); `guard_chair`, `umbrella_table`, `lounger`, `splash_pad`, `flagpole`, `pole_clock`, `foot_shower`, `buoy_post`, `filters`.
- **Gradil e terreno**: `fence_2`, `fence_195`, `fence_end`, `site`, `lamp_post`, `park_bench`, `bike_rack`, `tree`, `tree_b`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`brick`, `concrete`, `plaster`, `shingles`, `deck`, `pool_w`, `terrazzo`, `grass`, `asphalt`, `curb`, `wood`, `dkwood` e `soil`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta. A água (`water`) e os jatos (`spray`) usam material transparente (alphaMode BLEND).

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 7 caminhos:
  - da rua, pela calçada e pela porta dupla, atravessa o saguão e sai pela porta dos fundos no deck;
  - do saguão, entra no vestiário masculino;
  - do saguão, entra no vestiário feminino;
  - do vestiário masculino, sai pela porta de chapa no deck;
  - do vestiário feminino, sai pela porta de chapa no deck;
  - anda pelo deck oeste, entre a piscina e o gradil, até o fundo;
  - do deck, entra na área de jatos.

No visitante, é o prédio 45 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/piscina-publica/gerar_kit.py        # escreve em out/ ao lado do script
python kits/piscina-publica/verificar_flicker.py
```
