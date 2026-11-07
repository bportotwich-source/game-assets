# Kit modular: three-flats

Dois prédios de três apartamentos lado a lado, em peças 3D (GLB), estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md), com tamanho, planta e fachadas próprios.

## O conjunto
- **Prédio A (tijolo):** 8 × 16 m, fachada de tijolo vermelho, bay window redonda de três andares e cornija de metal com mísulas.
- **Prédio B (pedra cinza):** 8 × 16 m, fachada de pedra cinza, bay window chanfrada e cornija de pedra. As janelas têm verga alta com cornijinha.
- **Base:** porão meio enterrado com janelinhas gradeadas, embasamento de pedra clara e escadinha de pedra de 7 degraus até a entrada, com muretas e corrimão.
- **Andares:** piso do 1º andar em y = 1,2 e pé-direito de 3 m. Frisos de pedra marcam cada andar, e o terraço é plano com platibanda.
- **Dentro, por andar:** um apartamento (sala na bay window, cozinha, dois quartos e banheiro) e o hall com escada em U de parede a parede, que vai até o 3º andar.
- **Fundos:** varandas de madeira em cada andar, com escada externa em U entre elas, postes até a cobertura e uma escada reta do quintal até a varanda mais baixa.
- **Portas:** 32, contando entradas, portas dos fundos e internas.

## Montagem
- **Grade:** módulo de 2 m, parede de 0,3 m. Y para cima, 1 unidade = 1 m. O prédio A ocupa x de -8 a 0 e o B, de 0 a 8; ambos vão de z = -8 a 8, com a frente para +Z.
- **Níveis:** os pisos ficam em `lvl(n) = 1,2 + 3n` e o terraço em y = 10,2. As paredes do térreo vão do chão até 4,17; as de cima começam em `lvl(n) - 0,03` (o piso dentro da peça fica em 0,03).
- **Paredes:** `wall_{a|b}{andar}_{window|plain|backdoor|entry}`. O andar 0 inclui o porão.
- **Bay windows:** `bay_{a|b}{andar}` têm pivô no centro dos 4 m da frente que elas ocupam. `bay_top_*` (cornija em volta da bay) fica em y = 10,2.
- **Platibanda:** `cornice_*` na frente e `parapet_*` nos fundos atravessam os cantos. Nas laterais vão `parapet_side_*`; as `_lo`/`_hi` param 0,3 m antes do canto.
- **Varandas:** `porch_deck*` têm pivô no meio da borda junto à parede. `porch_stair` fica 0,9 m à direita, na borda de fora (z = -9,6).

## Alto detalhe
Versão refeita com `scripts/detalhe/retrofit.py`, sem mudar planta nem encaixes:
- **Janelas:** caixilho com batente, folhas de guilhotina com baguetes e vidro, peitoril com caimento e pingadeira.
- **Portas:** almofadas rebaixadas e chanfradas, vidro com baguetes nas portas envidraçadas, maçaneta e dobradiças.
- **Texturas PBR** (cor + normal + ORM, ladrilho de 2 m, JPEG dentro dos GLB, UVs em metros): `brick` (prédio de tijolo), `grey` (prédio de pedra cinza), `plaster` (interno).
- Montado com cerca de 103 mil triângulos (antes 47 mil).

## Peças (70)
| Grupo | Peças |
|---|---|
| Paredes | `wall_a0..a2_*`, `wall_b0..b2_*`, `corner_a`, `corner_b` |
| Bay windows | `bay_a0..a2`, `bay_b0..b2`, `bay_top_a`, `bay_top_b` |
| Platibanda | `cornice_metal`, `cornice_stone`, `parapet_a`, `parapet_b`, `parapet_side_*` |
| Entrada | `stoop_a`, `stoop_b` |
| Fundos | `porch_deck`, `porch_deck_low`, `porch_deck_top`, `porch_posts`, `porch_roof`, `porch_stair`, `porch_landing_rail`, `porch_ground_stair` |
| Interior | `floor_tile`, `floor_tile_bath`, `roof_tile`, `stairs_u_3m_*`, `stair_core_slab_*`, `stair_guard`, `interior_wall_*` |
| Portas | `door_leaf_entry`, `door_leaf_entry_b`, `door_leaf_back`, `door_leaf_interior` |
| Referência | `player_scale_ref` |

## Arquivos
`pieces/*.glb`, `building_layout.json` (com portas `door: {closed, open}`), `building_assembled.glb`, `gerar_kit.py` e `verificar_flicker.py`. O teste dá TOTAL 0 com os prédios montados e com `SOLO=1`. Os scripts de porta estão em `../../scripts/`.
