# Kit modular: estação de trem

Estação ferroviária de cidade pequena em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O conjunto
- **Prédio:** 24 × 8 m de tijolo sobre embasamento de pedra clara, com cunhais de pedra de quina e faixa de pedra sob o beiral.
- **Janelas:** em arco na fachada da rua e nas pontas; retangulares com verga de pedra do lado da plataforma.
- **Telhado:** duas águas a 35° em telha de barro, com empenas de tijolo (uma com óculo de veneziana) e cumeeira. Os beirais são apoiados em mãos-francesas de madeira: 1 m do lado da rua e 2,5 m sobre a plataforma.
- **Torre do relógio:** 4 × 4 m na ponta oeste, com 11 m de parede, quatro relógios, janelas em arco, cornija de pedra e telhado em pirâmide de telha de barro com pináculo.
- **Rua:** porta dupla com coberta de duas águas e escada de 3 degraus; porta de carga com rampa.
- **Plataforma:** de 0,4 m de altura com borda de pedra e faixa amarela, e um trecho de trilho com lastro, dormentes e trilhos de bitola 1,435 m.
- **Dentro:** pé-direito de 4,2 m.
  - Sala de espera, com guichê de venda na parede da bilheteria.
  - Bilheteria, com porta para a plataforma e porta para o depósito.
  - Depósito de cargas, com portas para a rua e para a plataforma e um banheiro no canto.
  - Sala do telégrafo na base da torre.
- **Portas:** 13 folhas.

## Montagem
- **Grade:** módulo de 2 m, parede de 0,3 m. Y para cima, 1 unidade = 1 m. O salão vai de x = -12 a 12 e z = -4 a 4, com a rua em +Z e os trilhos em -Z; a torre vai de x = -16 a -12 e z = -2 a 2.
- **Níveis:** piso em y = 0,45 e forro em 4,65. As paredes têm pivô no chão e sobem até 4,87; as empenas começam aí.
- **Telhado:** `roof_front*` e `roof_back*` têm pivô na linha da cumeeira (z = 0), no chão; as de trás vão com rotação 180. As `_end`/`_end_l` levam o beiral da empena.
- **Mãos-francesas:** `eave_bracket_*` vão nas juntas dos módulos (x par).
- **Torre:** `tower_wall` serve nas três faces livres. `tower_wall_east` encosta na `wall_tower_end` do salão, costas com costas, com as passagens alinhadas.
- **Plataforma e trilho:** `platform` (6 m), `platform_tower` (8 m) e `track` têm pivô na borda e seguem para fora com rotação 180.

## Texturas (embutidas nos GLB, UVs em metros)
- `brick`: paredes.
- `roof`: telha de barro.
- `plaster`: interno.

## Peças (47)
| Grupo | Peças |
|---|---|
| Paredes | `wall_window`, `wall_rect`, `wall_small`, `wall_door`, `wall_entry`, `wall_freight`, `wall_plain`, `wall_tower_end`, `corner_hall`, `gable_vent`, `gable_plain` |
| Telhado | `roof_front`, `roof_front_end`, `roof_front_end_l`, `roof_back`, `roof_back_end`, `roof_back_end_l`, `ridge_cap`, `eave_bracket_front`, `eave_bracket_back`, `entry_hood` |
| Torre | `tower_wall`, `tower_wall_east`, `corner_tower`, `tower_cornice`, `tower_roof`, `tower_floor`, `tower_ceiling` |
| Interior | `floor_waiting`, `floor_freight`, `floor_washroom`, `ceiling_hall`, `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway`, `interior_wall_counter` |
| Exterior | `entry_steps`, `freight_ramp`, `platform`, `platform_tower`, `track` |
| Portas | `door_leaf_entry`, `door_leaf_freight`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a estação montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
