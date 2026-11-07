# Kit modular: quartel de bombeiros

Quartel com galpão de tijolo de 3 portões e anexo de madeira branca, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhados próprios.

## O prédio
- **Galpão:** 16 × 12 m, paredes de tijolo de 6 m (dois níveis de 3 m), telhado de metal de duas águas a cerca de 27°, com a cumeeira paralela à rua. Oitões de tijolo com veneziana redonda e mastro de sirene na cumeeira.
- **Frente do galpão:** 3 portões de 3,6 × 4,2 m com 2 folhas vermelhas cada, porta de pedestre, faixa e letreiro BOMBEIROS sobre os portões.
- **Térreo do galpão:** área dos caminhões de piso de concreto. No fundo, oficina, escada em U, depósito de equipamento (vãos largos) com porta para fora e banheiro.
- **Mezanino (3 m):** galeria de 2 m com guarda-corpo e vigas de aço sobre a área dos caminhões, 2 alojamentos, banheiro e o buraco do mastro de descida, com guarda em dois lados. O mastro de latão vai do chão até o forro.
- **Anexo:** 8 × 10 m, um pavimento, tábuas brancas, venezianas vermelhas, telhado de duas águas com telha asfáltica e oitão para a rua. Escritório e sala de plantão na frente (porta com cobertura), cozinha no fundo com porta para o quintal e porta para o galpão.
- **Portas:** 18, contando as internas, as 6 folhas dos portões, a de pedestre, a dos fundos do galpão, a da frente e a dos fundos do anexo.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Galpão em x de -2 a 14 e z de -7 a 5; anexo em x de -10 a -2 e z de -3 a 7 (frente para +Z).
- **Paredes do galpão:** `wall_hall_*` têm 6,02 m, com faixa em 3 m e friso no topo. `wall_hall_bay` ocupa 4 m. Onde o anexo encosta, a parede vira `wall_hall_party` (0 a 3 m, reboco dos dois lados) com `wall_hall_upper` em cima.
- **Telhado do galpão:** `hall_slope*` em y = 5,0, com a face interna encontrando a parede a 6,0 m, beiral de 0,45 m e cumeeira 6 m para dentro (z = -1). `gable_hall` em y = 6,02.
- **Anexo:** paredes `wing_wall_*` de 3,02 m. `wing_slope*` em y = 2,0, cumeeira em x = -6. Do lado do galpão vai `wing_slope_wall*`, sem beiral, encostado na parede. `wing_gable` em y = 3,02.
- **Mezanino:** pisos em y = 3, forro em y = 6 sobre os quartos e `attic_wall` em z = -3 fechando o vão até o telhado. As peças `_end` param dentro da parede externa.
- **Escada:** `stairs_u_3m_192_192` com pivô em (6, 0, -3), núcleo de z -7 a -3.

## Texturas (embutidas nos GLB, UVs em metros)
- `brick`: tijolo, fiadas de 12,5 cm.
- `metal_roof`: telha metálica com junta a cada 50 cm.
- `siding`: tábuas sobrepostas de 20 cm.
- `shingle`: telha asfáltica.
- `sign`: letreiro BOMBEIROS.
- `plaster`: interno.

## Peças (61)
| Grupo | Peças |
|---|---|
| Galpão | `wall_hall_window`, `wall_hall_door`, `wall_hall_high_window`, `wall_hall_small_window`, `wall_hall_plain`, `wall_hall_upper`, `wall_hall_party`, `wall_hall_party_door`, `wall_hall_party_end`, `wall_hall_bay`, `corner_hall`, `hall_sign` |
| Telhado do galpão | `gable_hall`, `hall_slope`, `hall_slope_end`, `hall_slope_end_l`, `hall_ridge_cap`, `hall_ridge_cap_end`, `siren_mast` |
| Anexo | `wing_wall_window`, `wing_wall_small_window`, `wing_wall_plain`, `wing_wall_door_hood`, `wing_wall_door_back`, `wing_corner_board`, `wing_gable` |
| Telhado do anexo | `wing_slope`, `wing_slope_end`, `wing_slope_end_l`, `wing_slope_wall`, `wing_slope_wall_end`, `wing_slope_wall_end_l`, `wing_ridge_cap`, `wing_ridge_cap_end` |
| Mezanino e mastro | `gallery_rail`, `gallery_rail_end`, `gallery_beam`, `gallery_beam_end`, `gallery_post`, `floor_tile_pole`, `pole_guard`, `fire_pole`, `attic_wall`, `attic_wall_end` |
| Pisos e escada | `apparatus_floor`, `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_192_29`, `stairs_u_3m_192_192`, `stair_guard` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_wide`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `bay_door_leaf`, `door_leaf_hall`, `door_leaf_front`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o quartel montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
