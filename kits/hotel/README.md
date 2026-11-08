# Kit 37: hotel de 12 andares (alto detalhe)

Hotel urbano com embasamento de 2 andares, marquise de entrada e uma torre de 10 andares com sacadas, num terreno com pista de embarque em laço. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto no letreiro, nas placas ou nas bandeiras.

## O conjunto
- **Embasamento** de 16 × 16 m e 2 andares de 3,6 m, com:
  - piso 0,15 m acima do chão, no nível da calçada;
  - paredes de tijolo com embasamento de pedra que para nas portas;
  - vitrines altas no térreo, com bandeira, rodapé de alumínio e verga de concreto;
  - porta dupla de vidro com puxadores dourados;
  - janelas de 2 folhas no 2º andar, com peitoril e verga;
  - faixas de concreto nas lajes, platibanda com faixa e capa;
  - porta de serviço nos fundos, com batente e arandela.
- **Marquise** em balanço sobre a pista: 2 pilares de tijolo, 4 tirantes de aço até a fachada, faixa com friso dourado, forro com luzes embutidas, teto verde com arbustos e 3 claraboias redondas.
- **Terraço** no teto do embasamento: piso de placas, floreiras com árvores e sebes, espreguiçadeiras e balizadores de luz. Os quartos do 3º andar saem direto para ele.
- **Torre** de 12 × 12 m e 10 andares de 3 m, com:
  - reboco creme e faixa de concreto em cada laje, com quinas em meia-esquadria;
  - janelas de alumínio com peitoril e soleira;
  - portas de correr para as sacadas (a partir do 4º andar), com guarda-corpo de vidro verde, corrimão de aço, piso de deck, mesinha e banquetas;
  - janelas estreitas no fim do corredor;
  - um pano de vidro azul com montantes sobre a escada e o elevador, nos fundos.
- **Cobertura**: platibanda com capa e faixa, casa de máquinas com porta e arandela, 2 condensadoras (grade, hélice e aletas), 3 exaustores, para-raios e um letreiro sem texto (painel azul com estrela e círculos dourados, moldura e luzes em cima).
- **Dentro**:
  - **Saguão** com piso de pedra, 6 pilares redondos com base e capitel, recepção de madeira com tampo de pedra e computadores, painel de ripas com estrela dourada, sala de estar (tapete, 2 sofás, 2 poltronas, mesa de centro e abajur), vasos com árvores e um carrinho de bagagem.
  - **Salão do 2º andar** com assoalho, bar (estante de garrafas com espelho, balcão com apoio de pés e 3 banquetas), 5 mesas redondas com toalha e 4 cadeiras, e bufê com rechauds.
  - Nos fundos do embasamento, escritório e depósito com portas para o saguão.
  - **Andar tipo** (10 vezes): corredor de carpete com luzes, 5 quartos e o núcleo com escada em U (degraus de concreto com bocel, corrimãos nas paredes e guarda-corpo central) e elevador com portas de aço e botoeira.
  - **Quartos**: cama de casal com cabeceira estofada, criados-mudos com abajur, TV sobre aparador, guarda-roupa no hall, poltrona e mesinha junto da janela (ou escrivaninha, nos quartos dos fundos).
  - **Banheiros** com box de vidro e chuveiro, vaso, bancada com cuba, torneira, espelho e piso de cerâmica.
  - **Acabamentos**: portas internas almofadadas com guarnição, e rodapés que param nas portas.
- **Terreno**:
  - pista de embarque em laço até a marquise, com calçada de embarque e faixa amarela;
  - ilha de grama com 3 mastros de bandeiras lisas;
  - calçadas de concreto com juntas em volta do prédio e na rua, gramados com guia;
  - postes, bancos, balizadores, bicicletário, árvores e arbustos.

Números: 60 peças, 644 posições, 120 portas, cerca de 518 mil triângulos no montado (a maior parte são os 10 andares de quartos mobiliados).

## Montagem
O embasamento vai de x = -8 a 8 e de z = -6 a 10, com a frente para +Z. A torre vai de x = -6 a 6 e de z = -6 a 6, com os fundos alinhados com os do embasamento. O piso do térreo fica em 0,15, o do 2º andar em 3,75, o terraço e o 1º andar da torre em 7,35, e a cobertura em 37,35. O terreno vai de x = -13 a 13 e de z = -9 a 22.
- **Torre** (módulos de 2 m, pivô na face externa, na cota do piso de cada andar; cada módulo tem a altura do andar inteiro, 3 m):
  - `t_win`, `t_bal` (porta da sacada), `t_plain`, `t_curt` (pano de vidro), `t_cwin_l` / `t_cwin_r` (janela estreita do corredor, lado oeste / leste);
  - `t_corner`, com pivô na quina externa;
  - `balcony`, com pivô na face da fachada, no eixo da porta;
  - `slab_typ` (laje com pisos e forro, pivô no centro), `plan_floor` (paredes, banheiros, elevador e luzes do andar), `stair_tower`;
  - `room_front`, `room_front_c` e `room_back` (móveis do quarto, pivô no canto do banheiro), com `room_front_r` / `room_back_r` espelhados.
- **Embasamento** (pivô na face externa, na cota do piso):
  - térreo: `pg_glass`, `pg_door_l` / `pg_door_r` (as 2 metades da porta dupla), `pg_svc` e `pg_plain`;
  - 2º andar: `pu_win`, `pu_plain`, `pu_plain_np` (sem platibanda, sob a torre) e `pu_plain_e` (ponta junto da torre);
  - `p_corner`, `floor_ground`, `floor_podium`, `plan_ground`, `plan_podium`, `stair_podium` e `column`.
- **Topo**: `terrace` (pivô na origem, cota 7,35), `slab_roof` e `roof_top` (cota 37,35).
- **Portas**: `door_leaf_glass` (entrada), `door_leaf_back` (serviço e casa de máquinas), `door_leaf_interior` e `door_leaf_bath`.
- **Interior**: `reception`, `lobby_panel`, `lounge`, `luggage_cart`, `planter_tree`, `bar`, `table_set` e `buffet`.
- **Terreno**: `canopy` (pivô na fachada, x = 0, no chão), `site` (pivô na origem), `flagpole_r` / `_w` / `_b`, `lamp_post`, `bench`, `bollard`, `bike_rack`, `tree`, `tree_b` e `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render`, `brick`, `plaster`, `stone_f`, `wood`, `dkwood`, `paver`, `concrete`, `asphalt`, `grass`, `membrane`, `carpet` e `carpet2`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 9 caminhos:
  - o jogador vem da pista, passa sob a marquise, entra pela porta de vidro e atravessa o saguão;
  - do saguão, passa pela porta da escada e sobe até o patamar;
  - sobe o segundo lance da escada da torre e chega ao andar de cima;
  - do corredor, entra num quarto da frente até a sacada;
  - do hall do quarto, entra no banheiro;
  - do corredor, entra num quarto dos fundos;
  - sai de um quarto do 3º andar para o terraço;
  - na cobertura, sai da casa de máquinas até a platibanda;
  - entra pela porta de serviço, atravessa o escritório e chega ao saguão.

No visitante, é o prédio 37 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/hotel/gerar_kit.py        # escreve em out/ ao lado do script
python kits/hotel/verificar_flicker.py
```
