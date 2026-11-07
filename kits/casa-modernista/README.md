# Kit 27: casa modernista (alto detalhe)

Casa térrea modernista dos anos 50, de pilar e viga, com garagem coberta ao lado. Feita no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original.

## O conjunto
- **Corpo** de 14 × 10 m, piso a 0,2 m sobre um embasamento de concreto, pé-direito de 2,9 m.
- **Paredes**: tábuas verticais com junta em V, reboco branco, janelas altas em fita (bandeira de 2,15 m até o forro) e paredes de vidro do piso ao forro nos fundos, com montantes de aço e 2 portas de correr envidraçadas. Pingadeira metálica na base e pilares de aço nas quinas.
- **Telhado plano** com cascalho, beiral de 1 m, testeira escura com rufo metálico, domos de iluminação em acrílico e respiros. As vigas de madeira laminada ficam aparentes: atravessam as paredes e saem em balanço sob o beiral. O forro de tábuas é contínuo de dentro para fora.
- **Frente**: porta amarela lisa com 3 visores escalonados e puxador vertical, arandelas, muro de cobogó, floreira de pedra, poste com 3 globos e corrente de chuva no canto.
- **Lareira** de pedra com banco e consolo, e chaminé de pedra do lado de fora da parede esquerda.
- **Garagem coberta** de 6 × 6 m no lado direito, com pilares de aço, vigas e laje no chão. A porta de serviço liga a garagem à casa.
- **Dentro**: sala e jantar abertos para o pátio dos fundos, cozinha, 2 quartos e 2 banheiros com piso de pastilhas. As portas internas são lisas, com guarnição, e os rodapés param nas portas.
- **Fora**: caminho de placas de concreto na frente e pátio de placas nos fundos.

Números: 49 peças, 194 posições, 10 portas, cerca de 82 mil triângulos no montado.

## Montagem
O corpo ocupa x de -7 a 7 e z de -5 a 5, com a frente para +Z. A garagem vai de x 7 a 13 e z de -4 a 2.
- `wall_*` são os módulos de 2 m das paredes externas (`boards`, `render`, `window`, `clerestory`, `glass`, `glass_door`, `entry`, `side_door`), com pivô na face externa e na cota do piso.
- `corner` é o pilar de aço das quinas.
- Telhado: `deck` são placas de 2 × 2 m; as variantes `deck_e####` têm testeira nas bordas (flags x-, x+, z-, z+), `deck_sky` tem o domo e `deck_vent` o respiro. `beam` vai em x par, ao longo de Z.
- Garagem: `cp_deck*`, `cp_post`, `cp_beam` e `slab`.
- `interior_wall_*` são as paredes internas de 2 m, lisas ou com vão de porta, e as `_end_` encostam nas paredes externas.
- `floor_tile` e `floor_tile_bath` são as placas de piso de 2 × 2 m.

## Texturas (PBR, embutidas nos GLB como JPEG)
`boards`, `render`, `roofdeck` (cascalho), `ceiling`, `fascia`, `concrete`, `breeze`, `stone2`, `floor`, `door`, `plaster` e `beam`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador entra pela porta amarela e cruza a sala até a parede dos fundos; sai para o pátio pela porta de vidro; entra pela porta de serviço vindo da garagem e atravessa o corredor e a sala; entra nos 2 banheiros, no quarto da frente e na cozinha pelas portas internas.

No visitante, é o prédio 27 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
python kits/casa-modernista/gerar_kit.py        # escreve em out/ ao lado do script
python kits/casa-modernista/verificar_flicker.py
```
