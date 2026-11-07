# Kit 24: armazém com celeiro (alto detalhe)

Armazém de secos e molhados com fachada falsa e, ao lado, um celeiro vermelho de telhado holandês. Primeiro kit novo feito direto no padrão de alto detalhe do bangalô, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py). Segue o [padrão de medidas](../../PADRAO_METRICAS.md). Arte original: o letreiro ("ARMAZÉM · SECOS & MOLHADOS · FUNDADO EM 1908") é uma textura própria desenhada pelo gerador.

## O conjunto
- **Loja** de 10 × 14 m sobre base de pedra (piso a 0,45 m), pé-direito de 3,4 m, paredes de tábuas sobrepostas em geometria.
- **Fachada falsa** de 7,4 m: 35 fiadas de tábuas, cornija com coroa, capa e mísulas, cantoneiras altas e retorno da cornija nas quinas. Atrás dela fica o telhado de duas águas a 30° com telhas em fiadas, calhas K, pontas de caibro e testeiras inclinadas no frontão dos fundos (com veneziana).
- **Frente**: 4 vitrines com bandeira de 4 vidros e almofada embaixo (as das pontas deslocadas para o centro, por causa da cantoneira alta), porta dupla de meio vidro com bandeira, letreiro de 5,8 × 2 m com moldura.
- **Varanda** de 2,6 m: deck de tábuas com frestas, saia de ripas, escada de madeira de 3 m com banzos, 4 pilares chanfrados com base, capitel e mãos-francesas curvas, guarda-corpo com balaústres, telhado de chapa com nervuras, forro de frisos, caibros aparentes, rufo na parede, calha e 2 condutores. Lanterna pendente na porta.
- **Dentro da loja**: salão de vendas de 10 × 8 m com forro de chapa estampada, depósito de 6 × 6 m com porta lateral, escritório e banheiro; 3 portas internas.
- **Corredor de carga** de 2,4 m entre a loja e o celeiro: porta lateral da loja com degraus de pedra, porta de serviço do celeiro com rampa.
- **Celeiro** de 12 × 12 m em tábua e mata-junta (sarrafos em geometria), baldrame de concreto, telhado holandês (60° e 22°) de chapa com nervuras a cada 0,4 m, cumeeira, calhas e 4 condutores. Portão de 3,6 × 3,3 m com 2 folhas em X, porta do palheiro, capuz da talha com viga e gancho, porta dos fundos, 8 janelas. Dentro: piso de concreto em placas, paredes e forro de tábuas, caibros e tirantes aparentes.

Números: 69 peças, 259 posições, 10 portas, cerca de 112 mil triângulos no montado.

## Montagem
Loja em x de -10 a 0 e z de -7 a 7 (frente para +Z), varanda em z de 7 a 9,6; celeiro em x de 2,4 a 14,4 e z de -7 a 5 (piso a 0,15 m). As paredes têm pivô no centro inferior da face externa, na cota do piso de cada prédio.
- Telhado da loja em faixas de 2 m (`roof_store*`), com pivô na face da parede lateral; `_front` termina atrás da fachada falsa e `_back` tem a beirada inclinada do frontão (`_r` é a versão do lado direito). `ridge_store` é uma peça só.
- `front_*` são os módulos de 7,32 m da fachada falsa. `corner_tall` e `cornice_end`/`cornice_end_l` vão nas quinas da frente.
- `porch_roof*`, `porch_beam*`, `porch_deck`, `porch_skirt*` têm pivô na face da parede da frente; `porch_steps` na borda do deck.
- `barn_roof` é uma faixa de 2 m do telhado holandês inteiro, com pivô no eixo do celeiro; `barn_roof_end` tem a testeira da ponta (gire 180° nos fundos). `barn_wall_bigdoor` é um módulo de 4 m.
- Portas: a folha da direita das portas duplas vai girada 180° e abre com -85°.

## Texturas (PBR, embutidas nos GLB como JPEG)
`siding`, `shingles`, `plaster`, `cap`, `deck`, `floor`, `stone`, `barn`, `planks` e `sign` (o letreiro, com UV própria de 0 a 1). Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Peças (69)
| Grupo | Peças |
|---|---|
| Fachada falsa | `front_display`, `front_display_l`, `front_display_r`, `front_door`, `front_plain`, `corner_tall`, `cornice_end`, `cornice_end_l`, `sign_board` |
| Paredes da loja | `wall_siding_window`, `wall_siding_small_window`, `wall_siding_plain`, `wall_siding_door`, `corner_siding`, `store_gable_back`, `stone_steps`, `downspout` |
| Telhado da loja | `roof_store`, `roof_store_front`, `roof_store_front_r`, `roof_store_back`, `roof_store_back_r`, `ridge_store`, `stovepipe` |
| Varanda | `porch_deck`, `porch_skirt`, `porch_skirt_side`, `porch_steps`, `porch_post`, `porch_post_end_l`, `porch_post_end_r`, `porch_beam`, `porch_beam_end_l`, `porch_beam_end_r`, `porch_rail`, `porch_rail_side`, `porch_roof`, `porch_roof_end_l`, `porch_roof_end_r`, `downspout_porch`, `porch_lantern` |
| Interior da loja | `floor_tile`, `floor_tile_bath`, `ceiling_tin`, `ceiling_tin_front`, `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Celeiro | `barn_wall_plain`, `barn_wall_window`, `barn_wall_door`, `barn_wall_bigdoor`, `barn_corner`, `barn_floor`, `barn_ramp`, `barn_ramp_small`, `barn_gable_front`, `barn_gable_back`, `barn_roof`, `barn_roof_end`, `downspout_barn`, `wall_lantern` |
| Portas | `door_leaf_store`, `door_leaf_back`, `door_leaf_interior`, `barn_door_leaf`, `barn_door_small` |
| Referência | `player_scale_ref` |

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador sobe a escada da varanda e entra na loja pela porta dupla; entra no celeiro pelo portão e sai pela porta dos fundos; sai do depósito pela porta lateral, desce os degraus, cruza o corredor e entra no celeiro pela porta de serviço; o guarda-corpo segura o jogador na varanda. No visitante é o prédio 24 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
python kits/armazem/gerar_kit.py        # escreve em out/ ao lado do script
python kits/armazem/verificar_flicker.py
```
