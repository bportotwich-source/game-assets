# Kit modular: diner

Lanchonete americana de aço inox, com pontas arredondadas, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e cobertura próprios.

## O prédio
- **Corpo:** 20 × 8 m, um pavimento, paredes de 3,5 m. Trecho reto de 12 m e duas pontas em meia-lua de 4 m de raio.
- **Fachada:**
  - Rodapé esmaltado vermelho e aço frisado abaixo das janelas.
  - Faixa contínua de janelas, inclusive nas curvas.
  - Faixa azul com frisos e cornija arredondada de aço, que forma uma mureta baixa em volta da cobertura plana.
- **Entrada:** vestíbulo de aço e vidro na frente, com porta de vidro para fora e outra porta para o salão.
- **Cobertura:** letreiro DINER sobre pernas de aço, chaminé da cozinha e alçapão de manutenção.
- **Salão:** toda a frente e as duas pontas arredondadas, com piso xadrez no trecho reto e vermelho nas pontas.
- **Fundos:**
  - Cozinha de 6 × 4 m, com passa-pratos largo para o salão, porta para o salão e porta de serviço para fora.
  - Depósito com porta para a cozinha.
  - 2 banheiros com porta para o salão.
- **Portas:** 7, contando as internas, as 2 da entrada e a de serviço.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m. Y para cima, 1 unidade = 1 m. Trecho reto em x de -6 a 6 e z de -4 a 4 (frente para +Z); pontas com centro em x = ±6.
- **Paredes retas:** pivô no centro inferior da face externa, com a fachada para +Z.
- **Curvas:** `wall_diner_curve`, `floor_curve` e `roof_curve` cobrem 30° cada uma, com pivô no centro do círculo. Com `rotY` = 0, a peça começa na frente (+Z) e gira para +X. A ponta direita usa `rotY` 0, 30, …, 150 com centro em x = 6, e a esquerda, 180 a 330 com centro em x = -6.
- **Cobertura:** laje plana com topo a 3,5 m (`roof_flat` 2 × 2 m e `roof_curve`). A cornija das paredes sobe até 3,66 m. Paredes internas de 3,3 m, até o forro.
- **Vestíbulo:** `vestibule` tem pivô no centro do módulo da porta, na face da fachada, e avança 1,8 m.

## Texturas (embutidas nos GLB, UVs em metros)
- `checker`: piso xadrez de 25 cm.
- `sign`: letreiro DINER.
- `plaster`: interno.

## Peças (25)
| Grupo | Peças |
|---|---|
| Paredes | `wall_diner_window`, `wall_diner_small_window`, `wall_diner_plain`, `wall_diner_door`, `wall_diner_service_door`, `wall_diner_curve` |
| Pisos e cobertura | `floor_checker`, `floor_tile_bath`, `floor_curve`, `roof_flat`, `roof_curve` |
| Entrada e cobertura | `vestibule`, `roof_sign`, `vent_stack`, `roof_hatch` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_wide`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_front`, `door_leaf_vestibule`, `door_leaf_service`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o prédio montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
