# Kit modular: supermercado

Supermercado de bairro térreo em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e cobertura próprios.

## O prédio
- **Prédio:** 24 × 16 m, térreo de loja com 4,0 m do piso ao topo da cobertura (3,75 m livres), piso 15 cm acima do chão e platibanda até 5,0 m.
- **Fachada:** tijolo com pilastras verticais, rodapé de concreto, faixa branca de cornija, rufo verde na platibanda e quinas de tijolo. A frente tem 10 vitrines com toldos verdes e o letreiro MERCADO acima da entrada.
- **Entrada:** caixa de vidro de 4 × 2 m com porta dupla de vidro de 1,8 × 2,4 m, aberta para o salão por dois vãos de 1,6 m.
- **Salão de vendas:** 24 × 10 m, livre, com 3 pilares de aço e saída de emergência na lateral esquerda.
- **Fundos:** depósito de 14 × 6 m com porta dupla de carga (1,8 × 2,8 m) sob marquise, corredor de funcionários, escritório, banheiro e copa com porta de serviço.
- **Cobertura:** plana, com 3 condicionadores de ar, 2 condensadoras pequenas e 3 respiros.
- **Portas:** 13 (2 de vidro, 2 de carga, 2 de serviço e 7 internas).

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m. Y para cima, 1 unidade = 1 m. Prédio em x de -12 a 12 e z de -8 a 8 (frente para +Z); entrada de vidro em x de -2 a 2 e z de 8 a 10.
- **Paredes externas:** pivô no centro inferior da face externa, na cota do piso (0,15 m). Cada módulo já traz pilastras, rodapé, cornija e rufo, e vai até o topo da platibanda.
- **Cobertura:** `roof_tile_flat` (2 × 2 m) tem pivô no centro da face de cima, a 4,0 m do piso. Os equipamentos ficam sobre essa face.
- **Entrada e letreiro:** `vestibule` e `roof_sign` têm pivô no centro da fachada, na cota do piso. `awning` usa o mesmo pivô da vitrine.
- **Portas internas:** as paredes internas têm 3,75 m e encostam na laje.

## Texturas (embutidas nos GLB, UVs em metros)
- `brick`: tijolo das paredes e quinas.
- `stone`: rodapé de concreto e vergas.
- `plaster`: interno.
- `sign`: o letreiro, mapeado na placa inteira.

## Peças (28)
| Grupo | Peças |
|---|---|
| Paredes externas | `wall_storefront`, `wall_entry`, `wall_brick_ribbed`, `wall_brick_window`, `wall_brick_small_window`, `wall_brick_door`, `wall_dock_door`, `corner_brick` |
| Fachada | `awning`, `roof_sign`, `vestibule` |
| Piso e cobertura | `floor_tile`, `floor_tile_bath`, `floor_tile_concrete`, `roof_tile_flat`, `steel_column` |
| Equipamentos da cobertura | `roof_hvac`, `ac_unit`, `roof_vent` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_doorway` |
| Portas | `door_leaf_glass`, `door_leaf_steel`, `door_leaf_service`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, texturas `*_texture.png`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o prédio montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
