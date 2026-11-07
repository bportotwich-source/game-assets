# Kit modular: sobrados geminados

Três sobrados de tijolo colados em fileira, com térreo de pedra marrom e escadaria alta até o andar nobre, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e cobertura próprios.

## O prédio
- **Fileira:** 18 × 14 m, três casas de 6 × 14 m. Casa A (x de -9 a -3) com 3 andares, casa B (x de -3 a 3) com 2 e casa C (x de 3 a 9) com 4. Todos os andares têm 3,0 m.
- **Fachada:**
  - Térreo (jardim) de pedra marrom, com porta para o jardim na frente e porta para o quintal nos fundos.
  - Andares de tijolo com vergas de pedra, frisos creme entre os andares e janelas altas no andar nobre.
  - Porta principal no 1º andar com bandeira de vidro, pilastras de pedra e cornija sobre mísulas. Cada casa tem uma cor de porta.
  - Escadaria (stoop) de pedra: 17 degraus de 17,6 cm, patamar de 1,2 m e corrimão de ferro, avançando 5,7 m da fachada.
- **Cobertura:** telhado plano em cada casa, com cornija creme de mísulas em toda borda que não encosta numa casa mais alta. A cornija morre na parede da vizinha mais alta. Chaminé e alçapão em cada telhado.
- **Cada casa, em todo andar:**
  - Cômodo da frente (4 × 4 m) e, ao lado, vestíbulo (andar nobre) ou banheiro (térreo e andares de cima), embaixo da escadaria no térreo.
  - Corredor de 2 m de lado a lado, escada em U em núcleo de 4 × 4 m, passagem lateral e cômodo dos fundos de 6 × 4 m.
- **Paredes entre as casas:** internas onde as duas casas têm o andar; acima da casa mais baixa viram parede externa de tijolo, sem janela.
- **Portas:** 36, contando as internas, as 3 portas principais, as 3 do jardim e as 3 dos fundos.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Fileira em x de -9 a 9 e z de -7 a 7 (frente para +Z). Andar `n` na altura 3·n.
- **Paredes externas:** pivô no centro inferior da face externa, com a fachada para +Z. `corner_stone` e `corner_brick` vão em cada canto externo de cada andar, inclusive onde uma casa sobe acima da vizinha.
- **Escadaria:** `stoop` tem pivô na face da fachada, no centro do módulo da porta (x = borda da casa + 5), no chão. Atrás dela vai `wall_stone_stoop`, sem friso.
- **Cornija:** `cornice` na altura do telhado, com pivô como as paredes. `cornice_corner` nos cantos. `cornice_end_l` e `cornice_end_r` param 3 cm antes do canto da casa vizinha mais alta.
- **Escada:** `stairs_u_3m_*` com pivô no centro da borda aberta do núcleo (z = 1), núcleo de z -3 a 1. `stair_guard` no último andar, sobre o lance que desce.

## Texturas (embutidas nos GLB, UVs em metros)
- `brick`: tijolo vermelho-escuro, fiadas de 12,5 cm.
- `stone`: pedra marrom em fiadas de 37,5 cm (8 por andar).
- `plaster`: interno.

## Peças (36)
| Grupo | Peças |
|---|---|
| Térreo de pedra | `wall_stone_window`, `wall_stone_door`, `wall_stone_plain`, `wall_stone_stoop`, `corner_stone` |
| Andares de tijolo | `wall_brick_window`, `wall_brick_parlor_window`, `wall_brick_small_window`, `wall_brick_entry`, `wall_brick_plain`, `corner_brick` |
| Cobertura | `cornice`, `cornice_corner`, `cornice_end_l`, `cornice_end_r`, `roof_tile`, `chimney`, `roof_hatch` |
| Entrada | `stoop` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab_168_192_29`, `stair_core_slab_192_192_29`, `stairs_u_3m_168_192`, `stairs_u_3m_192_192`, `stair_guard` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_front`, `door_leaf_front_b`, `door_leaf_front_c`, `door_leaf_garden`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

Nos nomes da escada, `_168_192` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; na laje, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a fileira montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
