# Kit modular: posto de gasolina

Posto com loja de conveniência e cobertura sobre as bombas, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e cobertura próprios.

## O conjunto
- **Loja:** 14 × 8 m, um pavimento, paredes de bloco pintado de 4 m, faixa azul no topo e platibanda azul com friso branco em volta do telhado plano. Dois aparelhos de ar-condicionado no telhado.
  - Frente com vitrine de vidro e caixilho de alumínio, porta dupla de vidro abrindo para fora e vitrine virando nas duas laterais.
  - Salão de vendas na frente (14 × 4 m). No fundo, depósito de 6 × 4 m com porta de serviço e cobertura metálica, escritório e 2 banheiros.
- **Cobertura:** 18 × 10 m, a 5 m de altura livre, sobre 4 pilares revestidos. Beiral azul de 1,1 m com faixa branca e luminárias embaixo.
- **Ilhas:** 2 ilhas de concreto de 7,2 m com faixas e balizadores amarelos, 2 bombas em cada.
- **Totem:** placa POSTO 24 HORAS sobre 2 pernas, a 4,2 m.
- **Cercado de lixo:** muro de bloco de 1,8 m em 3 lados.
- **Portas:** 7, contando as 2 folhas da entrada, a de serviço e as 4 internas.

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m (até o forro, 3,8 m). Y para cima, 1 unidade = 1 m. Loja em x de -7 a 7 e z de -10 a -2; cobertura em x de -9 a 9 e z de 2 a 12 (frente para +Z).
- **Paredes da loja:** pivô no centro inferior da face externa, com a fachada para +Z. `parapet` e `parapet_corner` vão em y = 4, com o pivô como as paredes.
- **Cobertura:** `canopy_panel` (2 × 2 m) tem pivô no centro, no chão. `canopy_fascia` tem pivô na linha da borda, no chão, com o lado de fora para +Z, e `canopy_fascia_corner` vai nos cantos. `canopy_column` vai em cima da ilha (y = 0,15).
- **Ilhas e bombas:** `pump_island` tem pivô no centro; `fuel_pump` em cima da ilha.

## Texturas (embutidas nos GLB, UVs em metros)
- `block`: bloco pintado de 50 × 20 cm.
- `sign`: placa do totem.
- `plaster`: interno.

## Peças (30)
| Grupo | Peças |
|---|---|
| Loja | `wall_store_storefront`, `wall_store_entry`, `wall_store_small_window`, `wall_store_service_door`, `wall_store_plain`, `corner_store`, `parapet`, `parapet_corner`, `roof_tile`, `ac_unit` |
| Pisos | `store_floor`, `storage_floor`, `floor_tile`, `floor_tile_bath` |
| Cobertura e bombas | `canopy_panel`, `canopy_fascia`, `canopy_fascia_corner`, `canopy_column`, `pump_island`, `fuel_pump` |
| Terreno | `price_pylon`, `dumpster_enclosure` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_glass`, `door_leaf_service`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o posto montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
