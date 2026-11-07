# Kit 28: delegacia de polícia (alto detalhe)

Delegacia de polícia de 3 andares, de tijolo e pedra, com pavilhão central de cantaria e terraço. Feita no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original.

## O conjunto
- **Corpo** de 18 × 12 m com 3 andares. O piso do térreo fica a 0,6 m, sobre um embasamento de granito. Cada andar tem 3,2 m, com laje de 0,25 m.
- **Térreo** de pedra rusticada em 6 fiadas chanfradas, que dobram as quinas. As janelas de guilhotina têm grade de ferro, peitoril de pedra com pingadeira e verga em arco abatido de aduelas com fecho. As celas têm janelas altas e estreitas, também com grade.
- **Andares de cima** de tijolo, com cunhais de pedra alternados nas quinas. No 1º andar há uma faixa moldurada, e no 2º um peitoril corrido que passa sob as janelas.
- **Cornija** com arquitrave, friso, dentículos, modilhões e coroa, e **platibanda** de tijolo com capa de pedra.
- **Pavilhão central** de cantaria, de 6 m, que avança 1 m. Ele tem:
  - porta dupla almofadada com vidros e grade, bandeira, pilastras e entablamento com placa lisa;
  - janelas com moldura de pedra, frontão triangular no meio do 1º andar, cornijas retas nas laterais e fecho no 2º;
  - pilastras nas quinas, com capitel no último andar;
  - ático com painéis, relógio e mastro de bandeira.
- **Escadaria** de granito com 4 degraus, muretas e 2 postes de ferro com 3 globos.
- **Fundos**: porta de serviço com degraus, cobertura metálica e 2 arandelas.
- **Terraço** plano com manta e juntas. Nele ficam a casa de máquinas da escada (tijolo, porta de aço e arandela), 2 condensadoras com grade do ventilador, ralos, respiros e uma torre de rádio treliçada com antenas e parabólica.
- **Dentro**:
  - escada em U de 3 lances, do térreo ao terraço, com corrimão, balaústres e guarda-corpo em volta dos vãos;
  - saguão e corredores com piso xadrez;
  - salas com tacos e banheiros com pastilhas;
  - no térreo, 3 celas com grade de aço e portas de grade.
  - As portas internas são almofadadas, com guarnição, e os rodapés param nas portas.

Números: 131 peças, 543 posições, 27 portas, cerca de 216 mil triângulos no montado.

## Montagem
O corpo ocupa x de -9 a 9 e z de -6 a 6, com a frente para +Z. O pavilhão vai de x -3 a 3 e de z 6 a 7, e a escadaria vai até z 9,4.
- Paredes externas (pivô na face externa, na cota do piso do andar):
  - `g_wall_*` são as do térreo, de -0,6 até a face de baixo da laje.
  - `u1_wall_*` e `u2_wall_*` são as do 1º e do 2º andar, de -0,25 até a face de baixo da laje de cima.
  - `parapet` é a platibanda, com pivô na cota do terraço.
- Os módulos `_pvl` e `_pvr` são os vizinhos do pavilhão. As molduras deles terminam em meia-esquadria na quina interna.
- Pavilhão:
  - `pv_*` são os módulos da frente;
  - `pv_side_*` são as paredes laterais de 1 m;
  - `pv_filler_*` são os enchimentos da quina interna;
  - `corner_pv_*` são as quinas.
- Quinas do corpo: `corner_g`, `corner_u1`, `corner_u2` e `corner_parapet`.
- Escada:
  - `stair` sobe para -Z e `stair_both` (corrimão dos 2 lados) é o lance do meio, girado 180°.
  - Os vãos nas lajes estão em `building_layout.json` (`stair_holes`).
  - `rail_*` são os guarda-corpos.
- Pisos:
  - `floor_<tipo>_<g|u|r>` são as placas de 2 × 2 m (g = térreo, u = andar, r = terraço).
  - `_half` são as placas de 2 × 1 m do pavilhão.
  - `_e####` param na face interna das paredes externas (flags x-, x+, z-, z+), e `_h#` têm vão de escada.
- Celas: `cell_front`, `cell_front_end` e `door_leaf_cell`.
- Portas: a folha da direita da porta dupla vai girada 180° e abre com -85°.

## Texturas (PBR, embutidas nos GLB como JPEG)
`rust`, `ashlar`, `trim`, `plinth`, `brick`, `floor`, `plaster`, `membrane`, `concrete`, `stone2`, `marble` e `wood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador sobe a escadaria, entra pela porta dupla e cruza o saguão e o corredor; entra no hall pela porta e sobe os 3 lances até o terraço (3,8, 7,0 e 10,2 m); sai da casa de máquinas para o terraço; passa pela porta do corredor das celas e entra numa cela; entra pela porta dos fundos e cruza o corredor das celas; no 1º andar vai do corredor ao hall.

No visitante, é o prédio 28 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/delegacia/gerar_kit.py        # escreve em out/ ao lado do script
python kits/delegacia/verificar_flicker.py
```
