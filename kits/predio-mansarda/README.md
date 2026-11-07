# Kit modular: casas geminadas de pedra com mansarda

Duas casas coladas em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), mas com tamanho, planta e altura próprios (não repete o prédio de tijolos).

## O conjunto
- Volume de 18 × 12 m: Casa A (esquina, 10 × 12 m) e Casa B (8 × 12 m), separadas por parede de divisa.
- Térreo elevado 54 cm (3 degraus de 18 cm), térreo de 3,2 m, 2 andares de 3 m e sótão de 3 m dentro da mansarda.
- Casa A: térreo com hall, estúdio de frente, depósito e bicicletário; andares 1 e 2 com apartamento de 3 quartos (sala na quina); sótão com 2 estúdios.
- Casa B: escada em U na quina do fundo; térreo com hall, apartamento de 1 quarto e depósito; andares 1, 2 e sótão com apartamento de 2 quartos (sala na quina da frente).
- 64 portas com folha (internas, entradas, portas-janela da sacada).

## Grade e medidas
Módulo 2 m, parede externa 0,3 m, interna 0,12 m, laje 0,2 m. Eixo Y para cima, 1 unidade = 1 m. A mansarda inclina 1 m para dentro a cada 3 m de altura; as peças do sótão (`interior_wall_end_attic`) acompanham essa inclinação.

## Pivôs
- Fachada, cornija, mansarda, sacada: centro inferior da face externa, fachada para +Z. Cantos: na quina do prédio, faces +Z e +X.
- Paredes internas: centro inferior, espessura centrada na grade. Folhas de porta: na dobradiça.
- Lajes, telhado (`roof_tile`, `roof_cap_a/b`), chaminé: centro da base.

## Alto detalhe
Versão refeita com `scripts/detalhe/retrofit.py`, sem mudar planta nem encaixes:
- **Janelas:** caixilho com batente, folhas de guilhotina com baguetes e vidro, peitoril com caimento e pingadeira.
- **Portas:** almofadas rebaixadas e chanfradas, vidro com baguetes nas portas envidraçadas, maçaneta e dobradiças.
- **Texturas PBR** (cor + normal + ORM, ladrilho de 2 m, JPEG dentro dos GLB, UVs em metros): `ashlar` e `rustic` (pedra) na fachada, `plaster` no interno; o zinco da mansarda mantém a textura antiga.
- Montado com cerca de 176 mil triângulos (antes 75 mil).

## Peças (41)
| Grupo | Peças |
|---|---|
| Térreo | `wall_ground_arch_window`, `wall_ground_rect_window`, `wall_ground_plain`, `wall_ground_arch_door`, `wall_ground_rect_door` (com escadinha), `corner_ground` |
| Andares | `wall_ashlar_window`, `wall_ashlar_balconette`, `wall_ashlar_french`, `wall_ashlar_plain`, `corner_ashlar`, `balcony_band`, `balcony_side_rail` |
| Topo | `cornice_mansard`, `cornice_mansard_corner`, `mansard_dormer`, `mansard_plain`, `mansard_corner`, `roof_tile`, `roof_cap_a`, `roof_cap_b`, `chimney` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_168_29`, `stair_core_slab_192_192_29`, `stair_core_rail`, `stair_core_rail_attic`, `stairs_u_3m_192_168`, `stairs_u_3m_192_192`, `stairs_u_3m2_192_168`, `stairs_u_3m2_192_192` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_end_attic` e versões `_ground` |
| Portas | `door_leaf_entrance`, `door_leaf_entrance_b`, `door_leaf_interior`, `door_leaf_balcony` |
| Referência | `player_scale_ref` (cápsula de 1,8 m, não vai no jogo) |

As escadas vão de parede a parede da caixa de 4 m. Nos nomes, `_192_168` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; nas lajes, o último número é a faixa de laje atrás do patamar.

## Arquivos
`pieces/*.glb`, `building_layout.json` (posições, rotações, tags e portas `door: {closed, open}`), `building_assembled.glb`, `gerar_kit.py` (gerador), `verificar_flicker.py` (teste: montado e `SOLO=1`, ambos TOTAL 0). Scripts de porta para Godot e Unity em `../../scripts/`.
