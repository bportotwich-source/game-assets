# Kit modular: sobrado com padaria

Sobrado estreito com loja no térreo, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O prédio
- Planta de 8 × 8 m. Térreo de loja com 4,0 m (padrão para comércio), 1º andar de 3,0 m e sótão sob um telhado de duas águas a 45°, com a cumeeira paralela à fachada.
- **Térreo:** loja de 8 × 4 m com vitrines, porta e toldo listrado. Atrás ficam a cozinha da padaria (4 × 4 m, com porta de serviço nos fundos) e a escada em U.
- **1º andar:** apartamento com sala na quina (duas janelas com grade), quarto, hall, cozinha e banheiro.
- **Sótão:** espaço aberto com uma lucarna na frente, janela nos dois oitões e parede de 1,3 m sob o beiral.
- **Escada:** degrau de 16,7 cm nos dois lances. O de 4 m tem 24 degraus.
- **Portas:** 8, contando as internas, a porta da loja e a porta dos fundos.

## Grade e pivôs
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m.
- **Fachada, toldo, faixa e letreiro:** pivô no centro inferior da face externa, com a fachada para +Z. Toldo, faixa e letreiro ficam na cota da rua.
- **Telhado:** `roof_slope*` tem pivô no beiral, na face da fachada e na cota do piso do sótão. O beiral avança 0,4 m e a peça chega à cumeeira 4 m para dentro. `roof_slope_end` e `roof_slope_end_l` passam 0,3 m do oitão.
- **Oitão:** `gable_wall` é uma peça única de 8 m, colocada na face lateral.

## Texturas (embutidas nos GLB, UVs em metros)
- **Fachada:** `render`, reboco laranja.
- **Telhado:** `roof_tiles`, telha de barro em fiadas de 0,25 m.
- **Toldo:** `canvas`, listras de 0,25 m.
- **Letreiro:** `sign`, com "PADARIA"; para trocar o texto, troque a imagem.
- **Interno:** `plaster`.
- **Chaminé:** `brick`.

## Peças (43)
| Grupo | Peças |
|---|---|
| Loja | `shopfront_window`, `shopfront_door`, `shop_fascia`, `shop_sign`, `awning`, `wall_render_shop_window`, `wall_render_shop_plain`, `wall_render_shop_door`, `corner_shop` |
| 1º andar | `wall_render_window`, `wall_render_small_window`, `wall_render_balconette`, `wall_render_plain`, `corner_render` |
| Sótão e telhado | `knee_wall`, `knee_wall_dormer`, `corner_knee`, `gable_wall`, `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `roof_slope_dormer`, `ridge_cap`, `ridge_cap_end`, `chimney` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab`, `stair_core_rail`, `stairs_u_4m`, `stairs_u_3m` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` e as versões `_shop` (3,8 m) |
| Portas | `door_leaf_shop`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o prédio montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
