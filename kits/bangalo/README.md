# Kit 7: bangalô com varanda (alto detalhe)

Bangalô térreo de 14 × 12 m com varanda de 10 m, telhado de quatro águas a 30° e frontão na varanda. Foi o kit piloto do alto detalhe e agora é a versão oficial do kit 7: mesma planta e mesmas posições de antes, com muito mais detalhe. Segue o [padrão de medidas](../../PADRAO_METRICAS.md). As ferramentas de detalhe ficam em [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py).

## O prédio
Sala de 8 × 6 m com lareira e porta de entrada, jantar, cozinha com despensa e porta dos fundos, corredor, banheiro e 2 quartos; 10 portas. Piso elevado 0,45 m sobre base de tijolo, pé-direito de 2,8 m e forro plano.

## O que mudou em relação à primeira versão
| Parte | Antes | Agora |
|---|---|---|
| Fachada | Parede lisa com textura de tábuas | 13 fiadas de tábuas sobrepostas **em geometria** (cada tábua é uma cunha de 2,4 a 0,7 cm), na mesma fase da textura |
| Telhado | Placa com textura de telha | Telhas em fiadas de 0,2 m com **degrau real** de 2,2 cm; cumeeira e espigões com perfil |
| Beiral | Testeira | Testeira chanfrada, **calha K** com cantos em meia-esquadria, 6 **condutores** com cotovelos, abraçadeiras e bloco de respingo, **pontas de caibro** aparentes |
| Janelas | Vidro com caixilho | **Guilhotina** de 2 folhas (a de cima por fora), baguetes 3 ou 2 sobre 1, peitoril com nariz e pingadeira, avental, guarnição larga e verga craftsman com capa |
| Portas | Placa | Portas com **almofadas rebaixadas e chanfradas** (Blender: booleano + bevel); a da frente tem 3 vidros escalonados e prateleira com dentículos; maçaneta, espelho e dobradiças |
| Varanda | Tábua lisa, coluna cônica | Deck com 14 tábuas por módulo e frestas, coluna cônica com base e capitel em degraus (bevel do Blender), pilar com cimalha de tijolo e capa chanfrada, forro de frisos, frontão de tábuas em geometria, terças aparentes e mãos-francesas |
| Escadas | Blocos | Pisos de pedra com **bocel arredondado** e muretas laterais com capa inclinada |
| Chaminé | Caixa | Ombros com pingadeira, cimalha em 2 fiadas, capa de concreto e 2 manilhas de barro |
| Interior | Rodapé reto | Rodapé com perfil, guarnições de porta chanfradas dos dois lados, pastilhas no banheiro, lareira com cornija e mísulas |
| Luz | — | Lanterna pendente na varanda e arandela na porta dos fundos (vidro com emissão) |
| Texturas | Cor lisa | **PBR**: cor + normal + ORM (oclusão, rugosidade, metálico) |

Números: o prédio montado tem cerca de 81 mil triângulos (a primeira versão tinha 12 mil). A peça mais pesada é a porta da frente, com cerca de 2 mil.

## Como é feito
- `gerar_kit.py` usa a biblioteca `scripts/detalhe/detalhe.py`: Python (trimesh, shapely, numpy, Pillow) + **Blender como módulo Python** (`pip install bpy`, sem abrir o Blender) para os booleanos e o bevel das portas e das colunas.
- Ferramentas da biblioteca, usadas por todos os kits de alto detalhe:
  - `prof_x / prof_y / prof_z`: perfil 2D extrudado (molduras, pingadeiras, calhas, rodapés). As pontas ficam retas, então módulos vizinhos encostam sem emenda.
  - `cham`: caixa com todas as arestas chanfradas.
  - `board / siding_field`: tábuas sobrepostas com buracos para janelas e portas.
  - `sheared_courses`: telhas em fiadas sobre qualquer água (quatro águas, duas águas, rincões).
  - `gutter_run` e `downspout`: calha com meia-esquadria e tampas, condutor com cotovelos.
  - `bl_detail`: booleano EXACT + bevel por ângulo no Blender.
  - `glb_jpeg`: troca as texturas PNG embutidas por JPEG, e o arquivo fica cerca de 4 vezes menor.
- Texturas: `../../scripts/texturas/gerar_texturas.py`, estilo `detalhado`, ladrilho de 2 m (UV em metros / 2), 192 px por metro. `siding`, `brick`, `shingles`, `plaster`, `deck`, `floor`, `cap`. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta. Nos GLB elas vão embutidas como JPEG.
- O normal map segue a convenção OpenGL (verde para cima), a mesma do glTF e do Godot.

## Montagem
Casa em x de -7 a 7 e z de -6 a 6 (frente para +Z); varanda em x de -5 a 5 e z de 6 a 8,5. Paredes com pivô no centro inferior da face externa, na cota do piso (0,45 m). Telhado em faixas de 2 m: `roof_main_*` frente e fundos, `roof_hip_*` laterais; o número é a distância do centro do módulo ao meio da fachada e `_l` é a versão espelhada. Além disso:
- `roof_main_*_porch`: águas da frente atrás do telhado da varanda. A calha some onde a varanda cobre e começa logo depois dela.
- `roof_hip_3_chimney`: água lateral esquerda onde a chaminé atravessa o beiral. A calha é interrompida, com tampas.
- `downspout`: pivô na face da parede, no chão; o condutor sai para +Z. Vai a 0,38 m dos 4 cantos, na frente e nos fundos. `downspout_porch` fica na lateral dos 2 pilares da frente da varanda (rotação ±90°).
- `porch_lantern`: pivô no ponto de fixação no forro. `wall_lantern`: pivô na face da parede.
- Paredes externas sobem 3,03 m (o telhado ficou mais fino: 8 cm em vez de 25 cm), e a testeira fica a 3,0 m.

## Peças (56)
| Grupo | Peças |
|---|---|
| Paredes externas | `wall_siding_window`, `wall_siding_small_window`, `wall_siding_plain`, `wall_siding_door`, `wall_siding_window_hood`, `corner_siding`, `fireplace`, `chimney`, `brick_steps`, `downspout` |
| Telhado | `roof_main_0/2/4/6` (+ `_l`, + `_porch`), `roof_hip_1/3/5` (+ `_l`), `roof_hip_3_chimney`, `hip_cap`, `ridge_cap` |
| Varanda | `porch_deck`, `porch_front_wall`, `porch_base_steps`, `porch_side_wall`, `porch_pier`, `porch_beam_side`, `porch_ceiling`, `porch_gable`, `porch_roof`, `porch_lantern`, `downspout_porch` |
| Piso e forro | `floor_tile`, `floor_tile_bath`, `ceiling_tile` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas e luz | `door_leaf_front`, `door_leaf_back`, `door_leaf_interior`, `wall_lantern` |
| Referência | `player_scale_ref` |

## Testes
- `verificar_flicker.py`: TOTAL 0 com a casa montada e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador sai da calçada, sobe os degraus, cruza a varanda e entra na sala pela porta da frente. No visitante, é o prédio 7 (tecla 7).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
python kits/bangalo/gerar_kit.py        # escreve em out/ ao lado do script
python kits/bangalo/verificar_flicker.py
```
