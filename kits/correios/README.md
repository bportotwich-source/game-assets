# Kit modular: agência dos correios

Agência dos correios de um pavimento em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e telhado próprios.

## O conjunto
- **Prédio:** 16 × 12 m de tijolo vermelho sobre embasamento de pedra clara de 90 cm, com moldura no topo do embasamento. Tem cunhais com pedras de quina alternadas e uma faixa de pedra sob o beiral.
- **Janelas:** em arco, com moldura de pedra, peitoril e pedra de fecho. No banheiro há uma janelinha alta.
- **Telhado:** quatro águas a 30° com telha cinza, beiral de 0,5 m, cumeeiras de canto e cumeeira de 4 m. Em cima ficam uma cúpula redonda (base branca, oito colunas, domo de cobre, cata-vento) e duas chaminés de tijolo.
- **Entrada:** porta dupla em arco com bandeira de vidro, pilastras, entablamento e placa. Na frente há um patamar de pedra com escada de 5 degraus entre muretas e uma rampa de 6 m ao longo da fachada, com corrimão.
- **Doca de carga:** na lateral esquerda, com duas portas duplas, plataforma de concreto na altura do piso, para-choques de borracha, escada e marquise de metal sobre dois pilares.
- **Fundos:** porta de serviço com escada.
- **Dentro:** pé-direito de 4,5 m.
  - Saguão do público na frente, com paredes de caixas postais e dois guichês com balcão e grade de latão.
  - Sala de triagem atrás.
  - Sala do agente e banheiro à direita, mais um almoxarifado aberto para a triagem.
- **Portas:** 11 folhas (2 na entrada, 4 na doca, 1 nos fundos e 4 internas).

## Montagem
- **Grade:** módulo de 2 m, parede de 0,3 m. Y para cima, 1 unidade = 1 m. Prédio em x de -8 a 8 e z de -6 a 6, com a frente para +Z.
- **Níveis:** piso em y = 0,9 e forro em 5,4. As paredes externas têm pivô no chão e sobem até 5,58, entrando no telhado.
- **Paredes:** `wall_entry` tem 4 m e fica no meio da frente. As paredes junto aos cantos são lisas, para as pedras de quina caberem.
- **Telhado:** `roof_main_*` (frente e fundos) e `roof_hip_*` (laterais) têm pivô na face da parede, em y = 0,9. `hip_cap` vai nos cantos e `ridge_cap` no centro.
- **Cúpula e chaminés:** pivô no chão (alturas absolutas). A cúpula fica no centro da cumeeira; as chaminés ficam em (-4,5; 0) e (5; -3,2).
- **Doca:** `loading_dock` tem pivô na face da parede esquerda, em z = -2, com rotação -90.

## Alto detalhe
Versão refeita com `scripts/detalhe/retrofit.py`, sem mudar planta nem encaixes:
- **Janelas:** caixilho com batente, folhas de guilhotina com baguetes e vidro, peitoril com caimento e pingadeira.
- **Portas:** almofadas rebaixadas e chanfradas, vidro com baguetes nas portas envidraçadas, maçaneta e dobradiças.
- **Texturas PBR** (cor + normal + ORM, ladrilho de 2 m, JPEG dentro dos GLB, UVs em metros): `brick` (fachada), `shingle` (telhado), `plaster` (interno). As janelas em arco continuam como eram.
- Montado com cerca de 40 mil triângulos (antes 30 mil).

## Peças (42)
| Grupo | Peças |
|---|---|
| Paredes | `wall_window`, `wall_plain`, `wall_small`, `wall_backdoor`, `wall_dock`, `wall_entry`, `po_corner` |
| Telhado | `roof_main_*`, `roof_hip_*`, `hip_cap`, `ridge_cap`, `cupola`, `chimney_left`, `chimney_right` |
| Exterior | `entry_stair` (escada e rampa), `back_steps`, `loading_dock` |
| Interior | `floor_tile`, `floor_tile_bath`, `ceiling_tile`, `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end`, `interior_wall_boxes`, `interior_wall_counter` |
| Portas | `door_leaf_entry`, `door_leaf_dock`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com o prédio montado e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
