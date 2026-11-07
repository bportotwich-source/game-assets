# Kit modular: casa de campo com sótão

Casa de campo de um pavimento e meio, com sótão habitável, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O prédio
- **Casa:** 14 × 8 m, piso elevado 0,6 m sobre base de tijolo, térreo de 3,0 m e sótão sob telhado de duas águas a 50° (1,2 m por metro), com a cumeeira paralela à fachada.
- **Fachada:** tábuas horizontais, cantoneiras e molduras brancas, testeira no beiral, 2 lucarnas na frente e chaminé externa de tijolo no oitão esquerdo.
- **Varanda:** 12 × 2 m na frente, com piso de tábuas, saia de treliça, pilares a cada 2 m, guarda-corpo, telhado próprio e escada de 2 degraus. Nos fundos, outra escada leva à porta da sala.
- **Térreo:** hall de entrada, sala de 6 × 8 m com lareira, cozinha e jantar de 6 × 4 m, banheiro, despensa e escada em U.
- **Sótão:** 2 quartos nos oitões, banheiro sob a lucarna da direita, patamar e um nicho de guarda-volumes. As divisórias acompanham a inclinação do telhado.
- **Escada:** 18 degraus de 16,7 cm.
- **Portas:** 9, contando as internas, a da frente e a dos fundos.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Casa em x de -7 a 7 e z de -4 a 4 (frente para +Z); varanda em x de -5 a 7 e z de 4 a 6.
- **Paredes do térreo:** pivô no centro inferior da face externa, na cota do piso (0,6 m). A base de tijolo desce até o chão dentro da própria peça.
- **Telhado:** `roof_slope*` tem pivô no beiral, na face da fachada e na cota do piso do sótão (3,6 m). Beiral de 0,4 m, cumeeira 4 m para dentro. `roof_slope_end` e `roof_slope_end_l` passam 0,3 m do oitão.
- **Varanda:** `porch_roof*` tem pivô na face da parede, na cota do piso. `porch_deck` tem pivô no centro do módulo.
- **Divisórias do sótão:** `attic_partition_full` (de fachada a fachada, com porta) e `attic_partition_bath` correm ao longo de Z e têm o topo 1 cm abaixo do telhado.
- **Chaminé:** pivô no centro da face do oitão, no chão.

## Texturas (embutidas nos GLB, UVs em metros)
- `siding`: tábuas horizontais de 0,2 m.
- `shingles`: telha asfáltica em fiadas de 0,2 m.
- `brick`: base, lareira e chaminé.
- `plaster`: interno.

## Peças (42)
| Grupo | Peças |
|---|---|
| Térreo | `wall_siding_window`, `wall_siding_small_window`, `wall_siding_plain`, `wall_siding_door`, `corner_siding`, `fireplace`, `chimney` |
| Sótão e telhado | `knee_wall`, `knee_wall_dormer`, `corner_knee`, `gable_siding_center`, `gable_siding_pair`, `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `roof_slope_dormer`, `ridge_cap`, `ridge_cap_end` |
| Varanda | `porch_deck`, `porch_post`, `porch_rail`, `porch_skirt`, `porch_roof`, `porch_roof_end`, `porch_roof_end_l`, `steps` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_192_29`, `stair_core_rail`, `stairs_u_3m_192_192` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway`, `attic_partition_full`, `attic_partition_bath`, `attic_wall_bath` |
| Portas | `door_leaf_front`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

As escadas vão de parede a parede da caixa de 4 m. Nos nomes, `_192_168` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; nas lajes, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a casa montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
