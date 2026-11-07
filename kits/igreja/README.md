# Kit modular: igreja

Igreja de madeira com torre frontal e agulha, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O conjunto
- **Nave:** 12 × 16 m, um só salão com pé-direito de 5 m, embasamento de pedra de 45 cm, tábuas sobrepostas, cunhais e friso brancos, três janelas altas em arco de cada lado e oitão dos fundos com janela redonda.
- **Telhado:** duas águas de telha escura, beiral de 0,3 m, cumeeira com capa.
- **Torre (4 × 4 m, na frente):** nártex com porta dupla, pilastras e frontão, janela redonda; sala da torre no nível do coro; estágio do relógio com três mostradores; campanário com aberturas em arco e venezianas; lanterna octogonal aberta e agulha até 24 m com bola e cata-vento.
- **Dentro:** abertura de 1,6 m do nártex para a nave, coro alto de 4 m de fundo sobre vigas e pilares com guarda-corpo, escada reta de 17 degraus junto à parede, porta do coro para a sala da torre, presbitério elevado 45 cm com 3 degraus e porta lateral com escada externa.
- **Portas:** 4 (dupla da frente, lateral e do coro para a torre).

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Nave em x de -6 a 6 e z de -8 a 8; torre em x de -2 a 2 e z de 8 a 12 (frente para +Z).
- **Níveis:** piso da nave em y = 0,45, coro e sala da torre em 3,45, forro da nave em 5,45, forro da torre em 7,47.
- **Paredes da nave:** `nave_wall_*` têm a altura toda (embasamento, tábuas e friso de cima); `nave_wall_belt` leva o friso que cobre a borda da laje do coro.
- **Telhado:** `nave_slope*` em y = 4,45, com a face interna encontrando a parede a 5,45 m. As versões `_tower` param junto à torre.
- **Torre:** `tower_base`, `tower_clock`, `tower_belfry` e `tower_lantern` empilham no centro da torre (0, 0, 10), cada estágio no seu próprio nível; dá para usar só a base com o relógio, ou tirar a lanterna.
- **Coro:** `loft_stair` tem pivô no meio da borda de cima, no piso de baixo, e sobe para +Z.

## Texturas (embutidas nos GLB, UVs em metros)
- `siding`: tábuas sobrepostas brancas.
- `shingle`: telha escura.
- `stone`: embasamento de pedra.
- `plaster`: interno.

## Peças (35)
| Grupo | Peças |
|---|---|
| Nave | `nave_wall_window`, `nave_wall_door`, `nave_wall_plain`, `nave_wall_belt`, `nave_corner`, `gable_nave_back`, `gable_nave_front`, `nave_tower_wall` |
| Telhado | `nave_slope`, `nave_slope_end`, `nave_slope_end_l`, `nave_slope_tower`, `nave_slope_tower_l`, `ridge_cap`, `ridge_cap_end`, `roof_tile` |
| Torre | `tower_base`, `tower_clock`, `tower_belfry`, `tower_lantern` |
| Coro e presbitério | `loft_rail`, `loft_rail_stair`, `loft_rail_end`, `loft_beam`, `loft_beam_end`, `loft_post`, `loft_stair`, `chancel_platform` |
| Exterior | `entry_steps`, `side_steps` |
| Pisos | `floor_tile` |
| Portas | `door_leaf_front`, `door_leaf_side`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a igreja montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
