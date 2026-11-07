# Kit modular: torre escalonada com terraços

Torre residencial de 9 andares em três recuos, com terraço em cada recuo e na cobertura, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e fachada próprios.

## O prédio
- **Recuo 1:** 24 × 16 m, térreo de 4,0 m e andares 1 a 3 de 3,0 m.
- **Recuo 2:** 20 × 12 m, andares 4 a 6. Recua 2 m em todos os lados.
- **Recuo 3:** 16 × 10 m, andares 7 e 8. Recua 2 m na frente e nos lados; o fundo fica alinhado com o recuo 2.
- **Cobertura:** terraço com guarda-corpo e casa de escada.
- **Térreo:** hall de entrada com marquise de ripas, 2 lojas com vitrines e porta própria, e bicicletário com porta nos fundos.
- **Andares 1 a 3:** 4 apartamentos por andar. Os da frente têm sala com cozinha, 2 quartos e banheiro; os do fundo têm sala, 2 quartos e banheiro de suíte.
- **Andares 4 a 6:** 2 apartamentos de 2 quartos, com corredor interno e banheiro. No 4º andar, sala e quartos abrem para o terraço do recuo 1.
- **Andares 7 e 8:** 2 apartamentos de 1 quarto. No 7º andar, sala e quarto abrem para o terraço do recuo 2.
- **Núcleo:** escada em U (x de -2 a 2, z de -6 a -2), elevador ao lado (porta de pouso em cada andar, fechada) e shafts técnicos. Escada de 4 m com 24 degraus e de 3 m com 18, todos de 16,7 cm.
- **Portas:** 113, contando as internas, as de terraço, as das lojas e a do hall.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Frente para +Z.
- **Fachadas e guarda-corpos:** pivô no centro inferior da face externa, com a fachada para +Z. A faixa verde de cada peça desce 5 cm abaixo do piso e esconde a borda da laje.
- **Terraços:** `terrace_tile` no lugar de `floor_tile` onde o recuo de cima não cobre, com `parapet` e `corner_parapet` na borda.
- **Cobertura:** `roof_hut` tem pivô no centro da base e porta para +Z. `core_lintel` apoia a parede de fundo do recuo 2 sobre o vão da escada.

## Texturas (embutidas nos GLB, UVs em metros)
- `panel`: painel claro da fachada.
- `plaster`: interno.

## Peças (39)
| Grupo | Peças |
|---|---|
| Térreo | `storefront`, `storefront_door`, `wall_ground_panel`, `wall_ground_window`, `wall_ground_door`, `corner_ground`, `entrance_canopy` |
| Andares | `wall_ribbon`, `wall_ribbon_small`, `wall_ribbon_door`, `wall_tower_panel`, `corner_tower` |
| Terraços e cobertura | `terrace_tile`, `parapet`, `corner_parapet`, `roof_hut`, `stair_core_slab_roof_192_192_29` |
| Pisos, escada e elevador | `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_192_29`, `stair_core_slab_192_192_5`, `stair_core_rail`, `core_lintel`, `stairs_u_4m_192_192`, `stairs_u_3m_192_192`, `elevator_door`, `elevator_door_tall` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` e as versões `_tall` (3,8 m) |
| Portas | `door_leaf_entrance`, `door_leaf_back`, `door_leaf_interior`, `door_leaf_terrace` |
| Referência | `player_scale_ref` |

As escadas vão de parede a parede da caixa de 4 m. Nos nomes, `_192_168` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; nas lajes, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}` e a lista de recuos), `building_assembled.glb`, textura `panel_texture.png` e `plaster_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a torre montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
