# Kit modular: motel

Motel de dois andares com galerias abertas, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O conjunto
- **Bloco:** 24 × 6 m, dois andares de 3,0 m, reboco creme, rodapé marrom e friso branco na linha do piso, cantoneiras brancas.
- **Quartos:** 12 de 4 × 6 m (6 por andar), cada um com porta numerada e janela larga para a galeria, ar-condicionado de parede sob a janela, quarto e banheiro de 2 × 2 m no fundo com janela alta.
- **Recepção:** no primeiro módulo do térreo, com vitrine de alumínio e porta de vidro, e banheiro no fundo. Em cima dela fica o apartamento do gerente, igual aos quartos.
- **Galerias:** 2 m de fundo na frente dos dois andares, piso de concreto, pilares de aço verdes a cada 4 m e guarda-corpo de aço no andar de cima.
- **Escada:** externa e reta, ao lado da parede da ponta, 18 degraus de concreto sobre longarinas de aço até um patamar de 1,2 × 2 m.
- **Telhado:** plano, cobrindo também a galeria de cima, atrás de uma mansarda de telha verde com platibanda e capa brancas em todo o contorno.
- **Placa:** "MOTEL / TEM VAGA" em dois postes.
- **Portas:** 24 (11 dos quartos e do apartamento, a de vidro da recepção e 12 dos banheiros).

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, parede entre quartos de 0,2 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Bloco em x de -14 a 10 e z de -6 a 0 (frente para +Z), galerias em z de 0 a 2, escada em x de 10 a 11,2.
- **Níveis:** piso do térreo em y = 0,15, andar de cima em 3,15, topo do telhado em 6,15.
- **Paredes:** `wall_*` são do térreo (de 0 a 3,12); `wall_up_*` vão em y = 3,12 e sobem até 6,11, logo abaixo da camada do telhado. As `_back_` (fundos e pontas) levam rodapé e friso; as outras ficam na galeria.
- **Quartos:** porta no módulo da esquerda de cada vão de 4 m, janela no da direita. `party_wall` tem 5,5 m e entra nas paredes da frente e do fundo.
- **Galeria:** `gallery_walk` no chão, `gallery_deck` em y = 3,15, `gallery_rail` na borda (z = 1,92), pilares `gallery_post_low` e `gallery_post_high`. `outdoor_stair` tem pivô no meio da borda de cima, no chão, e sobe para +Z.
- **Telhado:** `roof_tile` em y = 6,15; `mansard` tem pivô na linha da borda (face da parede ou borda da galeria) e se abre para fora; `mansard_corner` fecha os cantos.

## Texturas (embutidas nos GLB, UVs em metros)
- `stucco`: reboco creme.
- `shingle`: telha verde da mansarda.
- `sign`: placa do motel.
- `plaster`: interno.

## Peças (42)
| Grupo | Peças |
|---|---|
| Paredes do térreo | `wall_door`, `wall_window`, `wall_small`, `wall_plain`, `wall_lobby_door`, `wall_lobby_glass`, `wall_back_window`, `wall_back_small`, `wall_back_plain` |
| Paredes de cima | `wall_up_door`, `wall_up_window`, `wall_up_small`, `wall_up_plain`, `wall_up_back_window`, `wall_up_back_small`, `wall_up_back_plain` |
| Cantos | `motel_corner`, `motel_corner_front` |
| Galerias e escada | `gallery_walk`, `gallery_deck`, `gallery_rail`, `gallery_rail_end`, `gallery_landing`, `gallery_post_low`, `gallery_post_high`, `gallery_post_landing`, `outdoor_stair` |
| Telhado | `roof_tile`, `mansard`, `mansard_corner` |
| Interior | `floor_tile`, `floor_tile_bath`, `party_wall`, `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_room`, `door_leaf_glass`, `door_leaf_interior` |
| Exterior | `sign_pylon` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o motel montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
