# Kit modular: casa enxaimel com garagem

Casa de família em enxaimel, com garagem anexa, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhados próprios.

## O prédio
- **Casa:** 10 × 8 m, térreo e 1º andar de 3,0 m, sótão sob telhado de duas águas a 45°, com a cumeeira paralela à fachada. Térreo de pedra, 1º andar e oitões em enxaimel (vigas aparentes com cruzes de Santo André), venezianas abertas, telha de barro vermelha, 2 lucarnas na frente e chaminé.
- **Térreo:** hall de entrada com cobertura sobre a porta, sala e jantar de 4 × 8 m com porta para o quintal e porta para a garagem, cozinha em L, lavanderia, lavabo e escada em U.
- **1º andar:** suíte principal, 2 quartos, banheiro, hall e corredor.
- **Sótão:** espaço aberto, com 2 lucarnas e janela em cada oitão.
- **Garagem:** 4 × 8 m, avança 2 m à frente da casa, com telhado próprio de duas águas (cumeeira perpendicular à da casa), portão duplo de madeira, janela lateral e janela no oitão de trás.
- **Escada:** 18 degraus de 16,7 cm por andar.
- **Portas:** 13, contando as internas, a porta da frente, a dos fundos, a da garagem e as 2 folhas do portão.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Casa em x de -5 a 5 e z de -4 a 4 (frente para +Z); garagem em x de -9 a -5 e z de -2 a 6.
- **Fachadas:** pivô no centro inferior da face externa, com a fachada para +Z.
- **Telhado da casa:** `roof_slope*` tem pivô no beiral, na face da fachada e na cota do piso do sótão. Beiral de 0,4 m, cumeeira 4 m para dentro. `roof_slope_end` e `roof_slope_end_l` passam 0,3 m do oitão.
- **Telhado da garagem:** `garage_roof*` com o mesmo pivô, colocado a 2,0 m de altura e girado ±90°. As versões `_house` têm beiral de 0,25 m, que entra na parede da casa.
- **Oitões:** `gable_timbered` (8 m) e `garage_gable_front` / `garage_gable_back` (4 m) são peças únicas.

## Alto detalhe
Versão refeita com `scripts/detalhe/retrofit.py`, sem mudar planta nem encaixes:
- **Janelas:** caixilho com batente, folhas de guilhotina com baguetes e vidro, peitoril com caimento e pingadeira.
- **Portas:** almofadas rebaixadas e chanfradas, vidro com baguetes nas portas envidraçadas, maçaneta e dobradiças.
- **Texturas PBR** (cor + normal + ORM, ladrilho de 2 m, JPEG dentro dos GLB, UVs em metros): `render` (reboco entre as madeiras), `stone2` (embasamento de pedra), `roof_tiles` (telhado), `plaster` (interno).
- Montado com cerca de 47 mil triângulos (antes 24 mil).

## Peças (49)
| Grupo | Peças |
|---|---|
| Térreo de pedra | `wall_stone_window`, `wall_stone_small_window`, `wall_stone_plain`, `wall_stone_door` (com cobertura), `wall_stone_door_back`, `wall_stone_door_inner`, `corner_stone` |
| 1º andar enxaimel | `wall_timber_window`, `wall_timber_small_window`, `wall_timber_plain`, `corner_timber` |
| Sótão e telhado | `knee_wall`, `knee_wall_dormer`, `corner_knee`, `gable_timbered`, `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `roof_slope_dormer`, `ridge_cap`, `ridge_cap_end`, `chimney` |
| Garagem | `wall_garage_plain`, `wall_garage_window`, `corner_garage`, `garage_gable_front`, `garage_gable_back`, `garage_door_leaf`, `garage_floor`, `garage_roof`, `garage_roof_end`, `garage_roof_end_l`, `garage_roof_house`, `garage_roof_house_end`, `garage_ridge_cap`, `garage_ridge_cap_end` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_168_29`, `stair_core_rail`, `stairs_u_3m_192_168` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_front`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

As escadas vão de parede a parede da caixa de 4 m. Nos nomes, `_192_168` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; nas lajes, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a casa montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
