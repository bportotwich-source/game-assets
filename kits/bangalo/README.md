# Kit modular: bangalô com varanda

Bangalô térreo de estilo americano em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O prédio
- **Casa:** 14 × 12 m, um só pavimento com pé-direito de 2,8 m, piso elevado 0,45 m sobre base de tijolo e forro plano. Não tem sótão habitável.
- **Telhado:** quatro águas a 30°, telha asfáltica escura, beiral de 0,5 m com testeira, cumeeira curta de 2 m ao longo de X e capas nas quatro arestas.
- **Fachada:** tábuas horizontais verdes, molduras e cantoneiras creme, frisos no rodapé e sob o beiral, chaminé externa de tijolo na lateral esquerda e uma janela com cobertura de telha sobre mãos-francesas na lateral direita.
- **Varanda:** 10 × 2,5 m na frente, com telhado de duas águas e frontão de tábuas com veneziana. O telhado da varanda morre no telhado principal em dois rincões. Tem 4 pilares de tijolo com capa de pedra e colunas cônicas brancas, muretas de tábuas entre os pilares, forro pintado e escada de tijolo de 2 degraus. Nos fundos, outra escada de tijolo leva à porta da cozinha.
- **Planta:** sala de 8 × 6 m com lareira e porta de entrada, jantar, cozinha com despensa e porta dos fundos, corredor, banheiro e 2 quartos.
- **Portas:** 10, contando as internas, a da frente e a dos fundos.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m. Y para cima, 1 unidade = 1 m. Casa em x de -7 a 7 e z de -6 a 6 (frente para +Z); varanda em x de -5 a 5 e z de 6 a 8,5.
- **Paredes externas:** pivô no centro inferior da face externa, na cota do piso (0,45 m). A base de tijolo desce até o chão dentro da peça, e a parede sobe 18 cm para dentro do telhado.
- **Forro:** `ceiling_tile` (2 × 2 m) tem pivô no centro da face de cima, a 3,0 m do piso.
- **Telhado:** cada água é feita de faixas de 2 m. `roof_main_*` são as águas da frente e dos fundos, e `roof_hip_*` as laterais triangulares. O número é a distância do centro do módulo ao meio da fachada; `_l` é a versão espelhada. O pivô fica na face da fachada, na cota do piso, como as paredes. `hip_cap` vai nos quatro cantos, com o mesmo pivô e a mesma rotação de `corner_siding`. `ridge_cap` vai no centro da casa.
- **Varanda:** `porch_gable`, `porch_roof`, `porch_ceiling` e `porch_deck` têm pivô na face da fachada, na cota do piso. `porch_front_wall` e `porch_base_steps` têm pivô na face externa da frente da varanda. `porch_pier` tem pivô no centro do pilar. `porch_side_wall` e `porch_beam_side` saem da fachada ao longo de +X local (rotação -90°).
- **Chaminé:** pivô no centro da face da parede, no chão.

## Texturas (embutidas nos GLB, UVs em metros)
- `siding`: tábuas horizontais de 0,2 m.
- `shingles`: telha asfáltica em fiadas de 0,2 m.
- `brick`: base, pilares, escadas, lareira e chaminé.
- `plaster`: interno.

## Peças (44)
| Grupo | Peças |
|---|---|
| Paredes externas | `wall_siding_window`, `wall_siding_small_window`, `wall_siding_plain`, `wall_siding_door`, `wall_siding_window_hood`, `corner_siding`, `fireplace`, `chimney`, `brick_steps` |
| Telhado | `roof_main_0`, `roof_main_2`, `roof_main_2_l`, `roof_main_4`, `roof_main_4_l`, `roof_main_6`, `roof_main_6_l`, `roof_hip_1`, `roof_hip_1_l`, `roof_hip_3`, `roof_hip_3_l`, `roof_hip_5`, `roof_hip_5_l`, `hip_cap`, `ridge_cap` |
| Varanda | `porch_deck`, `porch_front_wall`, `porch_base_steps`, `porch_side_wall`, `porch_pier`, `porch_beam_side`, `porch_ceiling`, `porch_gable`, `porch_roof` |
| Piso e forro | `floor_tile`, `floor_tile_bath`, `ceiling_tile` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_front`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a casa montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
