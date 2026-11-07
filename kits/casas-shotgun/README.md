# Kit modular: casas shotgun

Cinco casas estreitas coladas em fileira, cada uma de uma cor, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhados próprios.

## O conjunto
- **Fileira:** 20 × 12 m, cinco casas de 4 × 12 m (rosa, amarela, verde, lilás e azul), um pavimento de 3,0 m, piso elevado 60 cm sobre treliça branca.
- **Fachada:** tábuas sobrepostas na cor de cada casa, guarnições brancas, venezianas, porta com bandeira de vidro e oitão de 45° na frente e nos fundos com veneziana pontuda.
- **Telhado:** duas águas por casa, cumeeira no meio de cada uma, sem beiral onde duas casas se encontram (água-furtada). Telhas marrons e cinza alternadas.
- **Varanda:** 2 m de fundo em toda a largura de cada casa, deque de madeira, treliça, 2 colunas com mãos-francesas, guarda-corpo, telhado de uma água e escada de 3 degraus até a porta.
- **Cada casa (cômodos em fila, portas alinhadas):** sala na frente, quarto, cozinha com porta para o quintal e escada de concreto, e banheiro de 2 × 2 m no canto da cozinha.
- **Paredes entre as casas:** internas. Só as casas das pontas têm janelas nas laterais.
- **Portas:** 25, contando 3 internas por casa, a da frente e a dos fundos de cada uma.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Fileira em x de -10 a 10 e z de -6 a 6 (frente para +Z). Casa `n` em x de -10 + 4n a -6 + 4n.
- **Paredes:** `wall_<cor>_*` têm 3,62 m desde o chão: treliça até 0,6 m, rodapé externo na linha do piso e tábuas até o friso. Pisos em y = 0,6 e forro do sótão em y = 3,6.
- **Telhado:** `roof_slope*` (beiral de 0,4 m, nas pontas da fileira) e `roof_valley*` (sem beiral, entre duas casas) em y = 2,6, com a face interna encontrando a parede a 3,6 m. As peças `_g` usam telha cinza. `gable_<cor>` em y = 3,62.
- **Varanda:** `porch_*` têm pivô no centro da casa, na face da fachada, no chão. `porch_skirt_side` fecha a treliça nas pontas.
- **Cores:** `a` rosa, `b` amarela, `c` verde, `d` lilás, `e` azul.

## Texturas (embutidas nos GLB, UVs em metros)
- `siding_a` a `siding_e`: tábuas sobrepostas de 20 cm, uma por cor.
- `shingle` e `shingle_g`: telha asfáltica marrom e cinza.
- `deck`: tábuas do deque.
- `plaster`: interno.

## Peças (67)
| Grupo | Peças |
|---|---|
| Paredes (para cada cor `a` a `e`) | `wall_<cor>_window`, `wall_<cor>_small`, `wall_<cor>_door`, `wall_<cor>_door_back`, `wall_<cor>_plain`, `gable_<cor>` |
| Cantos e fundos | `corner_board`, `back_steps` |
| Telhado (com e sem `_g`) | `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `roof_valley`, `roof_valley_end`, `roof_valley_end_l`, `ridge_cap`, `ridge_cap_end` |
| Varanda | `porch_deck`, `porch_skirt_side`, `porch_post`, `porch_beam`, `porch_roof`, `porch_roof_g`, `porch_rail`, `porch_rail_side`, `porch_steps` |
| Pisos | `floor_tile`, `floor_tile_bath` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_front`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a fileira montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
