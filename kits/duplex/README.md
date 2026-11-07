# Kit modular: duplex

Duas casas espelhadas sob um só telhado, com oitão central sobre as duas garagens, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhados próprios.

## O prédio
- **Conjunto:** 16 × 12 m, térreo e 1º andar de 3,0 m, telhado de duas águas a cerca de 37°, com a cumeeira paralela à rua. No centro da frente, um oitão de 8 m cobre as duas garagens, e o telhado dele entra no telhado principal formando os rincões.
- **Acabamento:** tábuas sobrepostas amarelas, cantoneiras e molduras brancas, venezianas azul-marinho e telha asfáltica verde. Cada porta da frente tem uma cobertura em duas águas sobre mãos-francesas e um degrau. A casa A tem porta vermelha e a casa B, azul.
- **Cada casa (8 × 12 m, espelhadas pela parede do meio):**
  - Térreo: hall de entrada com a porta da frente, sala, cozinha e jantar com porta dos fundos (passagens largas sem porta), corredor até a escada em U e garagem de 4 × 6 m com portão duplo, porta para o corredor e porta para o hall.
  - 1º andar: corredor de ponta a ponta com guarda-corpo sobre o lance que desce, quarto principal na frente, quarto 2 em cima da garagem e banheiro de 4 × 4 m nos fundos.
- **Sótão:** fechado, sem acesso. Os oitões dos lados têm janela pequena e veneziana de ventilação, e o oitão da frente, veneziana.
- **Escadas:** 18 degraus de 16,7 cm, de parede a parede da caixa de 4 m.
- **Portas:** 18, contando as internas, as 2 da frente, as 2 dos fundos e as 4 folhas dos portões.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Conjunto em x de -8 a 8 e z de -6 a 6 (frente para +Z). Casa A em x de -8 a 0 e casa B em x de 0 a 8; garagens em x de -4 a 4 e z de 0 a 6.
- **Fachadas:** pivô no centro inferior da face externa, com a fachada para +Z. `wall_garage_front` ocupa 4 m (dois módulos). As paredes do 1º andar (`wall_siding_upper_*`) têm 3,02 m.
- **Telhado principal:** `roof_slope*` tem pivô no beiral, na face da parede, e vai a 5,0 m de altura. Beiral de 0,4 m, cumeeira 6 m para dentro. `roof_slope_behind_gable` não tem beiral e começa 5 cm dentro da parede, para ficar atrás do oitão central.
- **Oitão central:** `gable_cross` vai a 6,02 m, na frente. `cross_slope*` vai a 5,0 m em x = ±4, girado ±90°, com a cumeeira 4 m para dentro (x = 0). As 2 fileiras (z de 2 a 6) entram no telhado principal.
- **Oitões dos lados:** `gable_side` (12 m) a 6,02 m, em x = ±8.

## Texturas (embutidas nos GLB, UVs em metros)
- `siding`: tábuas sobrepostas de 20 cm.
- `shingle`: telha asfáltica verde em fiadas de 20 cm.
- `plaster`: interno.

## Peças (42)
| Grupo | Peças |
|---|---|
| Térreo | `wall_siding_window`, `wall_siding_small_window`, `wall_siding_plain`, `wall_siding_door_hood` (com cobertura e degrau), `wall_siding_door_back`, `wall_garage_front`, `corner_board` |
| 1º andar | `wall_siding_upper_window`, `wall_siding_upper_small_window`, `wall_siding_upper_plain`, `corner_board_upper` |
| Telhado | `gable_side`, `gable_cross`, `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `roof_slope_behind_gable`, `cross_slope`, `cross_slope_end`, `cross_slope_end_l`, `ridge_cap`, `ridge_cap_end`, `cross_ridge_cap`, `cross_ridge_cap_back`, `cross_ridge_cap_end` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `garage_floor`, `stair_core_slab_192_192_29`, `stairs_u_3m_192_192`, `stair_guard` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_wide`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_front`, `door_leaf_front_b`, `door_leaf_back`, `door_leaf_interior`, `garage_door_leaf` |
| Referência | `player_scale_ref` |

Nos nomes da escada, `_192_192` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; na laje, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o conjunto montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
