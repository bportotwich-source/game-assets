# Kit modular: padaria

Padaria de esquina de dois andares, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O prédio
-## O prédio
- Planta de 12 × 10 m. Térreo de loja com 4,0 m, 1º andar de 3,0 m e sótão sob telhado de duas águas (inclinação de 0,84 m por metro, cerca de 40°), com a cumeeira paralela à fachada.
- **Térreo:** a loja e o café ocupam toda a frente (12 × 4 m), com 5 vitrines, porta, toldo listrado e letreiro. Tem banheiro de cliente no café. Atrás ficam a produção (6 × 6 m, piso cerâmico) com forno de alvenaria embutido e porta de carga nos fundos, o depósito de secos e o hall de funcionários com a escada.
- **1º andar (apoio):** corredor de 2 m, com confeitaria, escritório e sala de funcionários na frente, e estoque de farinha, vestiário e banheiro de funcionários no fundo.
- **Sótão:** depósito aberto, com duas lucarnas e janela nos oitões.
- **Chaminé do forno:** sobe dentro da parede do 1º andar e sai pela água de trás do telhado.
- **Escada:** degrau de 16,7 cm; o lance de 4 m tem 24 degraus.
- **Portas:** 12, contando as internas, a porta da loja e a porta de carga.

vôs
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m.
- **Fachada, toldo, faixa e letreiro:** pivô no centro inferior da face externa, com a fachada para +Z. Toldo, faixa e letreiro ficam na cota da rua.
- **Telhado:** `roof_slope*` tem pivô no beiral, na face da fachada e na cota do piso do sótão. O beiral avança 0,4 m e a peça chega à cumeeira 5 m para dentro. `roof_slope_end` e `roof_slope_end_l` passam 0,3 m do oitão.
- **Oitão:** `gable_wall` é uma peça única de 10 m, colocada na face lateral.

## Texturas (embutidas nos GLB, UVs em metros)
- **Fachada:** `render`, reboco laranja.
- **Telhado:** `roof_tiles`, telha de barro em fiadas de 0,25 m.
- **Toldo:** `canvas`, listras de 0,25 m.
- **Letreiro:** `sign`, com "PADARIA"; para trocar o texto, troque a imagem.
- **Interno:** `plaster`.
- **Chaminé:** `brick`.

## Peças (45)
| Grupo | Peças |
|---|---|
| Loja | `shopfront_window`, `shopfront_door`, `shop_fascia`, `shop_sign`, `awning`, `wall_render_shop_window`, `wall_render_shop_plain`, `wall_render_shop_small_window`, `wall_render_shop_door`, `corner_shop` |
| Produção | `bake_oven` (forno de alvenaria, pivô na parede), `oven_flue` (chaminé do forno, pivô na base) |
| 1º andar | `wall_render_window`, `wall_render_small_window`, `wall_render_balconette`, `wall_render_plain`, `corner_render` |
| Sótão e telhado | `knee_wall`, `knee_wall_dormer`, `corner_knee`, `gable_wall`, `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `roof_slope_dormer`, `ridge_cap`, `ridge_cap_end` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_168_29`, `stair_core_slab_192_168_5`, `stair_core_rail`, `stairs_u_4m_192_168`, `stairs_u_3m_192_168` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` e as versões `_shop` (3,8 m) |
| Portas | `door_leaf_shop`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

As escadas vão de parede a parede da caixa de 4 m. Nos nomes, `_192_168` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; nas lajes, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o prédio montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
