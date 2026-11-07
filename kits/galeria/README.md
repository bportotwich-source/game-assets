# Kit modular: galeria comercial

Galeria de lojas de 3 andares em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e cobertura próprios.

## O prédio
- **Prédio:** 24 × 26 m, 3 andares de loja com 4,0 m cada, piso 15 cm acima do chão, cobertura plana com platibanda.
- **Fachada:** reboco bege com faixas nos pisos, painéis vermelhos e janelas nos andares de cima. No térreo, vitrines com faixa para letreiro, portas de loja e toldos listrados na loja da esquina.
- **Entrada:** pele de vidro de 8 m na frente, com duas portas duplas de vidro e marquise. Ela sobe acima da cobertura como uma lanterna de vidro com o letreiro GALERIA.
- **Átrio:** 8 × 14 m no centro, aberto nos 3 andares e coberto por uma abóbada de vidro. Uma ponte de 2 m atravessa o átrio no 1º e no 2º andar, e há guarda-corpos de vidro nas bordas.
- **Escadas rolantes:** a primeira sobe do térreo para a ponte do 1º andar, e a segunda sobe da ponte para o 2º andar. Cada uma tem 24 degraus de 16,7 × 25 cm e funciona como escada no jogo.
- **Lojas:** 10 por andar, 30 no total: 3 lojas de 6 × 6 m de cada lado e 4 lojas de esquina de 8 × 4 m. As vitrines de vidro dão para galerias de 2 m em volta do átrio.
- **Serviço:** banheiros e escritório no fundo do térreo, banheiros e depósito nos outros andares, porta de serviço nos fundos.
- **Portas:** 16 (4 de vidro na entrada, 3 de loja e serviço na rua e 9 internas).

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Prédio em x de -12 a 12 e z de -13 a 13 (frente para +Z); átrio em x de -4 a 4 e z de -7 a 7, ponte em z de -1 a 1.
- **Paredes externas:** um módulo de 2 × 4 m por andar, com pivô no centro inferior da face externa, na cota do piso. As versões `_ground` trazem o rodapé até o chão, e as outras trazem a faixa que esconde a borda da laje.
- **Pele de vidro:** `curtain_wall`, `curtain_wall_entry` e `curtain_wall_crown` usam o mesmo pivô das paredes. `crown_roof` vai no topo da lanterna, no meio da frente.
- **Átrio:** `atrium_rail` tem pivô na borda da laje, com o vazio para +Z local. `escalator` tem pivô no pé da escada e sobe para -Z. `skylight_vault` (faixas de 2 m), `skylight_end`, `skylight_curb` e `skylight_curb_end` ficam na cota da cobertura.
- **Vitrines internas:** `shopfront_glass` e `shopfront_door` são centradas na linha da parede, como as paredes internas.

## Texturas (embutidas nos GLB, UVs em metros)
- `render`: reboco com junta a cada metro.
- `stone`: rodapé e degraus.
- `canvas`: toldo listrado.
- `plaster`: interno.
- `sign`: o letreiro.

## Peças (41)
| Grupo | Peças |
|---|---|
| Paredes externas | `wall_render_plain_ground`, `wall_render_window_ground`, `wall_render_small_window_ground`, `wall_render_plain`, `wall_render_window`, `wall_render_small_window`, `wall_render_panel`, `wall_shop_window`, `wall_shop_door`, `awning_striped`, `corner_render_ground`, `corner_render` |
| Entrada de vidro | `curtain_wall`, `curtain_wall_entry`, `curtain_wall_crown`, `entry_canopy`, `crown_roof` |
| Cobertura | `roof_tile_flat`, `parapet`, `corner_parapet`, `skylight_curb`, `skylight_curb_end`, `skylight_vault`, `skylight_end`, `roof_hvac`, `ac_unit` |
| Átrio e lojas | `atrium_rail`, `escalator`, `shopfront_glass`, `shopfront_door` |
| Pisos | `floor_tile_mall`, `floor_tile_shop`, `floor_tile_bath` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_glass`, `door_leaf_shop`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o prédio montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
