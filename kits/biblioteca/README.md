# Kit modular: biblioteca

Biblioteca pública neoclássica em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O conjunto
- **Bloco:** 20 × 16 m de pedra calcária sobre um pódio de granito de 1,2 m com respiros gradeados. Tem dois andares (4,2 m e 4,0 m), cunhais com silhares, cordão de pedra entre os andares, cornija e balaustrada em todo o topo.
- **Janelas:** retangulares com cornija sobre consolos no térreo e em arco com pedra de fecho no andar de cima.
- **Pórtico:** 14 × 4 m na frente, com seis colunas de 7,3 m e capitel de volutas, entablamento, forro com caixotões, frontão triangular, telhado de metal em duas águas e escadaria de 7 degraus em toda a largura.
- **Cúpula:** tambor de 7,8 m de diâmetro com oito janelas e pilastras, cornija, cúpula de cobre e lanterna com bola e haste dourada. Fica sobre o salão central e é forrada por dentro.
- **Dentro:**
  - porta dupla de 1,8 × 3,05 m com bandeira de vidro;
  - salão central de 8 × 8 m com pé-direito duplo até a cúpula;
  - sala de leitura na ala esquerda e acervo na ala direita, ligados ao salão por vãos largos;
  - escada reta de 24 degraus junto à parede da direita;
  - escritório e banheiro nos fundos;
  - no andar de cima, galerias abertas com balaustrada em volta do vazio e da escada.
- **Fundos:** porta de serviço com patamar e escada.
- **Portas:** 5 (as duas folhas da frente, a de serviço e as do escritório e do banheiro).

## Montagem
- **Grade:** módulo de 2 m, parede externa de 0,3 m, interna de 0,12 m, laje de 0,2 m. Y para cima, 1 unidade = 1 m. Bloco em x de -10 a 10 e z de -8 a 8 (frente para +Z). Pórtico em x de -7 a 7 e z de 8 a 12,2, mais os degraus.
- **Níveis:** piso principal em y = 1,2, andar de cima em 5,4, topo do telhado em 9,4.
- **Paredes:** `lib_wall_*` são do térreo (de 0 a 5,37, com o pódio e o cordão). `lib_wall_up_*` vão em y = 5,37 e sobem até 9,36. `lib_wall_door` tem 4 m e fica no meio da frente.
- **Topo:** `cornice` em y = 9,4, com pivô na face externa da parede.
- **Vazios:** o andar de cima não tem `floor_tile` no vazio do salão (x e z de -4 a 4) nem na faixa da escada (x de 8 a 10, z de -4 a 4). `balustrade` vai na borda, com o vazio para +Z local, e `newel` vai nos cantos.
- **Cúpula:** `dome_ring` e `dome` vão em (0; 9,4; 0) no lugar dos `roof_tile` do meio. `lib_stair` tem pivô no meio da borda de cima, no piso de baixo, e sobe para +Z.
- **Pórtico:** `portico_floor`, `portico_entablature` e `pediment` têm pivô em (0, 0, 8); as colunas ficam em z = 11,6.

## Alto detalhe
Versão refeita com `scripts/detalhe/retrofit.py`, sem mudar planta nem encaixes:
- **Janelas:** caixilho com batente, folhas de guilhotina com baguetes e vidro, peitoril com caimento e pingadeira.
- **Portas:** almofadas rebaixadas e chanfradas, vidro com baguetes nas portas envidraçadas, maçaneta e dobradiças.
- **Texturas PBR** (cor + normal + ORM, ladrilho de 2 m, JPEG dentro dos GLB, UVs em metros): `stone` (fachada de pedra), `plaster` (interno).
- Montado com cerca de 113 mil triângulos (antes 93 mil).

## Peças (31)
| Grupo | Peças |
|---|---|
| Paredes | `lib_wall_window`, `lib_wall_plain`, `lib_wall_door`, `lib_wall_backdoor`, `lib_wall_up_window`, `lib_wall_up_plain`, `lib_corner` |
| Topo | `cornice`, `cornice_corner`, `roof_tile` |
| Cúpula | `dome_ring`, `dome` |
| Pórtico | `portico_floor`, `column`, `portico_entablature`, `pediment` |
| Interior | `floor_tile`, `floor_tile_bath`, `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_wide`, `interior_wall_end`, `balustrade`, `balustrade_end`, `newel`, `lib_stair` |
| Exterior | `back_steps` |
| Portas | `door_leaf_front`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com a biblioteca montada e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
