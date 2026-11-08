# Kit 38: mansão de tijolo com torreão (alto detalhe)

Casa grande de 2 andares no estilo rainha Ana, de tijolo vermelho e pedra, com um torreão redondo na quina da frente, varanda, porte-cochère lateral e jardim com chafariz. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto.

## O conjunto
- **Casa** de 14 × 12 m e 2 andares de 3,3 m, com:
  - piso do térreo 0,75 m acima do chão, sobre um embasamento de pedra com capa chanfrada e respiros de ferro;
  - paredes de tijolo com cunhais de pedra alternados nas quinas e faixa de pedra entre os andares;
  - janelas de guilhotina 2 sobre 2, com peitoril de pedra, verga em arco plano com fecho e, por dentro, peitoril de madeira, guarnição e avental;
  - porta da frente com 2 janelas laterais e bandeira em cima;
  - porta da cozinha nos fundos e porta lateral com arandela, as duas com patamar de pedra e escada com corrimão de ferro;
  - 2 portas-balcão de 2 folhas no 2º andar, para as sacadas;
  - cornija com modilhões e dentículos, friso de pedra e calha;
  - 4 condutores.
- **Torreão** de 12 faces e 2 m de raio na quina da frente: 2 andares abertos para a biblioteca e a suíte, um 3º nível acima do beiral com cornija própria, janelas de guilhotina, telhado cônico de ardósia com espigões e pináculo de cobre.
- **Telhado**:
  - 4 águas de ardósia a 45°, com fiadas em geometria e rincões com capa;
  - mirante plano no topo, com manta, alçapão e gradil de ferro com pinhas;
  - 5 trapeiras com frontão e janela de guilhotina;
  - 3 chaminés: 2 encostadas nas fachadas laterais e 1 que sai do sótão, todas com coroamento e potes de barro.
- **Varanda da frente**: base de tijolo, piso de tábuas, 4 colunas toscanas, balaustradas torneadas, forro de lambri com lanterna e escada de pedra com muretas e urnas. O teto é a sacada do 2º andar.
- **Porte-cochère** sobre a entrada de carros: 2 pilares de tijolo com faixas de pedra, vigas, forro de lambri com lanterna, sacada com balaustrada em cima e patamar da porta lateral.
- **Dentro**:
  - **Hall central** com piso xadrez de mármore, escadaria reta com pisos de carvalho, balaústres torneados, corrimão e pilares com pinha, console com espelho, relógio de pé e lustres.
  - **Sala de estar**: lareira, tapete, sofá, 2 poltronas, mesa de chá, abajur de pé e piano.
  - **Sala de jantar**: mesa com toalha, 6 cadeiras, candelabros, aparador e lareira.
  - **Biblioteca**: 2 estantes de livros, escrivaninha, globo e banco estofado no torreão.
  - **Cozinha**: piso de ladrilho, fogão a lenha, pia, geladeira de madeira, mesa de trabalho e despensa.
  - **2º andar**:
    - 3 quartos com cama de dossel, criados-mudos, guarda-roupa e lareira, e a cômoda na suíte;
    - banheiro com banheira de pés, vaso de caixa alta e pia de coluna.
  - **Acabamentos**: sancas e medalhões no forro, radiadores, portas internas almofadadas com guarnição, rodapés que param nas portas e passagens largas para a sala de estar e a biblioteca.
- **Terreno**:
  - gramado e entrada de carros de cascalho, que passa sob o porte-cochère até o galpão;
  - caminhos de tijolo e um anel em volta do chafariz de 2 bacias, com cortina d'água;
  - gradil de ferro com mureta de tijolo e pilares com bola de pedra ou lanterna;
  - portão de carros e portão de pedestres;
  - calçada da rua com juntas;
  - canteiros de flores, cerca viva, árvores, buxinhos em vasos, arbustos, postes de ferro e bancos de jardim;
  - galpão de jardim de tábuas com porta, janela e prateleira de vasos.

Números: 92 peças, 250 posições, 18 portas e portões, cerca de 337 mil triângulos no montado.

## Montagem
A casa vai de x = -7 a 7 e de z = -6 a 6, com a frente para +Z. O piso do térreo fica em 0,75, o do 2º andar em 4,05, e o topo das paredes em 7,35. O torreão tem o centro na quina (7, 6). O terreno vai de x = -15 a 12 e de z = -12 a 19.
- **Fachadas** (módulos de 2 m, pivô na face externa, na cota do piso do andar; cada módulo tem a altura do andar inteiro):
  - térreo: `w0_win`, `w0_plain`, `w0_chim` (atrás da chaminé), `w0_door` (porta da frente), `w0_bdoor` (cozinha) e `w0_sdoor` (lateral);
  - 2º andar: `w1_win`, `w1_plain`, `w1_chim` e `w1_bal` (porta-balcão);
  - `corner0` / `corner1`, com pivô na quina externa.
- **Torreão** (pivô no centro): `turret0`, `turret1`, `turret2` (anéis), `turret_floor`, `turret_slab`, `turret_top`, `turret_roof` e `window_seat`.
- **Telhado** (pivô na face da parede, cota 7,35):
  - `roof`, `roof_l1` / `_l3` / `_l5` e `roof_r1` / `_r3` / `_r5`, onde o número é a distância até o rincão;
  - `hip`, `roof_turret` (canto junto do torreão), `roof_deck`, `dormer`;
  - `chimney` (pivô na fachada, no chão), `chimney_roof` e `downspout`.
- **Anexos** (pivô na face da parede, no chão): `porch`, `porte_cochere` e `back_stoop`.
- **Dentro** (pivô na origem): `floor_ground`, `floor_upper`, `ceiling_attic`, `plan_ground`, `plan_upper`, `stair` e `stair_rail`.
- **Portas**: `door_leaf_front`, `door_leaf_back` (cozinha e lateral), `door_leaf_french` (portas-balcão), `door_leaf_interior`, `door_leaf_shed`, `gate_leaf` e `gate_leaf_s`.
- **Móveis**: `fireplace`, `parlor_set`, `piano`, `dining_set`, `sideboard`, `chandelier`, `chandelier_s`, `bookcase`, `desk`, `globe`, `bedroom_set`, `wardrobe`, `dresser`, `clawfoot_tub`, `toilet`, `pedestal_sink`, `radiator`, `kitchen_range`, `counter_sink`, `icebox`, `work_table`, `pantry`, `console` e `grandfather_clock`.
- **Terreno**: `site` (pivô na origem), `fountain`, `fence_pier`, `fence_pier_lamp`, `fence_*` (trechos de gradil, pelo comprimento em cm), `shed`, `hedge`, `tree`, `tree_b`, `bush`, `topiary`, `lamp_post` e `garden_bench`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`brick`, `stone`, `shingles`, `plaster`, `planks` e `render`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 10 caminhos:
  - do caminho da frente, sobe a escada da varanda, entra pela porta e atravessa o hall;
  - da calçada, passa pelo portão de pedestres;
  - sobe a escadaria do hall até o 2º andar;
  - do hall de cima, entra no quarto da frente;
  - do hall de cima, entra no banheiro;
  - do hall de cima, sai pela porta-balcão para a sacada da varanda;
  - sobe a escadinha dos fundos e entra na cozinha;
  - do hall, entra na biblioteca;
  - da entrada de carros, entra no galpão;
  - da sala de estar, sai pela porta lateral para o patamar do porte-cochère.

No visitante, é o prédio 38 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/mansao/gerar_kit.py        # escreve em out/ ao lado do script
python kits/mansao/verificar_flicker.py
```
