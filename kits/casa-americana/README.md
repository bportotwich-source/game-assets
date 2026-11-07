# Kit modular: casa americana

Sobrado americano com a frente em oitão, varanda coberta e garagem ao lado, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhados próprios.

## O prédio
- **Casa:** 8 × 12 m, térreo e 1º andar de 3,0 m, telhado de duas águas a 45° com a cumeeira perpendicular à rua (oitão virado para a frente). Revestimento de tábuas sobrepostas azul-acinzentadas, cantoneiras e molduras brancas, venezianas escuras, telha asfáltica cinza-escura, faixa branca na linha do piso e testeira sob o beiral.
- **Varanda:** 8 × 2,4 m em toda a frente, piso de tábuas 18 cm acima do chão, colunas e guarda-corpo brancos, telhado de uma água e degrau na frente da porta.
- **Chaminé:** de tijolo, do lado de fora da parede esquerda, com peito de 1,6 m até 4,2 m e chaminé de 0,9 m que passa da cumeeira.
- **Térreo:** hall de entrada, sala de estar com a parede da chaminé, sala de jantar e cozinha integradas (passagem larga sem porta), porta dos fundos, corredor até a escada, lavabo, lavanderia com porta para a garagem e escada em U.
- **1º andar:** quarto principal e quarto 2 na frente, quarto 3 nos fundos, banheiro e hall em volta da escada, com guarda-corpo sobre o lance que desce.
- **Sótão:** fechado, sem acesso (espaço de telhado). O oitão da frente tem veneziana de ventilação e o dos fundos, janela pequena e veneziana.
- **Garagem:** 4 × 6 m, recuada 6 m da frente da casa, com oitão próprio virado para a rua, portão duplo branco com almofadas e visores, janela lateral e janela no oitão de trás.
- **Escada:** 18 degraus de 16,7 cm, de parede a parede da caixa de 4 m.
- **Portas:** 12, contando as internas, a da frente, a dos fundos, a da garagem e as 2 folhas do portão.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Casa em x de -4 a 4 e z de -6 a 6 (frente para +Z); varanda em z de 6 a 8,4; garagem em x de 4 a 8 e z de -6 a 0.
- **Fachadas:** pivô no centro inferior da face externa, com a fachada para +Z. As paredes do 1º andar (`wall_siding_upper_*`) têm 3,02 m, para a borda da laje do sótão nunca dividir face com elas.
- **Telhado da casa:** `roof_slope*` tem pivô no beiral, na face da parede, e vai a 5,0 m de altura, girado ±90° nas paredes laterais. A face de baixo do telhado encontra a parede a 6,0 m (sem platibanda). Beiral de 0,4 m, cumeeira 4 m para dentro. `roof_slope_end` e `roof_slope_end_l` passam 0,3 m dos oitões.
- **Oitões:** `gable_front` e `gable_back` são peças únicas de 8 m, colocadas a 6,02 m, em cima das paredes.
- **Varanda:** todas as peças `porch_*` têm pivô no centro do módulo, na face da parede da frente, no chão. As versões `_end_l` e `_end_r` fecham as pontas.
- **Telhado da garagem:** `garage_roof*` com o mesmo pivô do telhado da casa, colocado a 2,2 m de altura. As versões `_house` têm beiral de 0,25 m, que entra na parede da casa.

## Texturas (embutidas nos GLB, UVs em metros)
- `siding`: tábuas sobrepostas de 20 cm.
- `shingle`: telha asfáltica em fiadas de 20 cm.
- `deck`: tábuas do piso da varanda.
- `brick`: tijolo da chaminé.
- `plaster`: interno.

## Peças (63)
| Grupo | Peças |
|---|---|
| Térreo | `wall_siding_window`, `wall_siding_small_window`, `wall_siding_plain`, `wall_siding_door`, `wall_siding_door_back` (com degrau), `wall_siding_door_inner`, `corner_board` |
| 1º andar | `wall_siding_upper_window`, `wall_siding_upper_small_window`, `wall_siding_upper_plain`, `corner_board_upper` |
| Telhado | `gable_front`, `gable_back`, `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `ridge_cap`, `ridge_cap_end`, `chimney_exterior` |
| Varanda | `porch_deck`, `porch_deck_end_l`, `porch_deck_end_r`, `porch_post`, `porch_beam`, `porch_beam_end_l`, `porch_beam_end_r`, `porch_roof`, `porch_roof_end_l`, `porch_roof_end_r`, `porch_rail`, `porch_rail_end_l`, `porch_rail_end_r`, `porch_rail_side`, `porch_steps` |
| Garagem | `wall_garage_plain`, `wall_garage_window`, `corner_garage`, `garage_gable_front`, `garage_gable_back`, `garage_door_leaf`, `garage_floor`, `garage_roof`, `garage_roof_end`, `garage_roof_end_l`, `garage_roof_house`, `garage_roof_house_end`, `garage_roof_house_end_l`, `garage_ridge_cap`, `garage_ridge_cap_end` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_168_29`, `stairs_u_3m_192_168`, `stair_guard` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_wide`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_front`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

Nos nomes da escada, `_192_168` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; na laje, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a casa montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
