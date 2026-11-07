# Kit modular: escolinha

Escola rural de uma sala em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O conjunto
- **Sala:** 8 × 12 m, paredes de tábuas vermelhas de 3,6 m sobre fundação de tijolo de 60 cm, cunhais, friso e moldura do embasamento brancos. Cada lado tem quatro janelas altas de guilhotina, 6 sobre 6.
- **Telhado:** duas águas a 45° com telha cinza e cumeeira ao longo do comprimento. Os oitões da frente e dos fundos têm veneziana em arco.
- **Vestíbulo:** 3 × 2,4 m na frente, com frontão próprio, chapelaria com janelinhas laterais, porta com bandeira de vidro e escada de 4 degraus com corrimão.
- **Cúpula do sino:** sobre a cumeeira, com base de tábuas, campanário aberto com guarda-corpo, sino de latão, telhado em pirâmide, bola e cata-vento.
- **Dentro:** sala única com tablado do professor de 20 cm no fundo e porta dos fundos com pequena cobertura e escada.
- **Chaminé:** de tijolo, sai do forro e atravessa a água da direita.
- **Telheiro de lenha:** separado, 2,4 × 1,8 m, aberto na frente, com telhado de uma água.
- **Portas:** 3 (a do vestíbulo, a da sala e a dos fundos).

## Montagem
- **Grade:** módulo de 2 m, parede de 0,3 m. Y para cima, 1 unidade = 1 m. Sala em x de -4 a 4 e z de -6 a 6 (frente para +Z); vestíbulo em x de -1,5 a 1,5 e z de 6 a 8,4.
- **Níveis:** piso em y = 0,6 e forro em 4,2. As paredes sobem até 4,22.
- **Paredes:** `school_wall_door` tem 4 m e fica no meio da frente, atrás do vestíbulo.
- **Telhado:** `roof_slope*` em y = 3,2, com a face interna encontrando a parede a 4,2 m (as `_end` levam o beiral de 0,3 m da frente e dos fundos); `gable_*` em y = 4,22.
- **Vestíbulo:** `vest_*` têm pivô na sua face da frente (z = 8,4) ou no começo da parede. `vest_slope` fica em y = 2,2.
- **Cúpula e chaminé:** `cupola` tem pivô na linha da cumeeira, no chão (alturas absolutas); `chimney` tem pivô no seu centro, no chão.

## Texturas (embutidas nos GLB, UVs em metros)
- `siding`: tábuas vermelhas.
- `shingle`: telha cinza.
- `brick`: fundação e chaminé.
- `plaster`: interno.

## Peças (32)
| Grupo | Peças |
|---|---|
| Paredes | `school_wall_window`, `school_wall_plain`, `school_wall_door`, `school_wall_backdoor`, `school_corner`, `gable_front`, `gable_back` |
| Telhado | `roof_slope`, `roof_slope_end`, `roof_slope_end_l`, `ridge_cap`, `ridge_cap_end`, `cupola`, `chimney` |
| Vestíbulo | `vest_front`, `vest_side`, `vest_corner`, `vest_gable`, `vest_slope`, `vest_ridge`, `vest_floor`, `vest_ceiling`, `entry_steps` |
| Interior | `floor_tile`, `roof_tile`, `teacher_platform` |
| Exterior | `back_steps`, `woodshed` |
| Portas | `door_leaf_front`, `door_leaf_class`, `door_leaf_back` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a escola montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
