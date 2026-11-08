# Kit 36: lanchonete com drive-thru (alto detalhe)

Lanchonete de beira de estrada com mansarda, torre de entrada, salão envidraçado e pista de drive-thru, num terreno com estacionamento. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto em placas, cardápios ou painéis.

## O conjunto
- **Prédio** de 12 × 10 m, com:
  - piso 0,15 m acima do chão, no nível da calçada;
  - paredes de 3,6 m de reboco creme sobre barra de tijolo com capa de pedra, que para nas portas e nos vãos.
- **Mansarda** de telhas a 60° em volta de uma laje plana:
  - rincões nas 4 quinas, com capa;
  - cornija com modilhões e faixa amarela no friso;
  - calhas e 4 condutores;
  - capa de pedra no topo.
  - Na laje, a manta tem 2 condensadoras (grade do ventilador com hélice e aletas), 2 exaustores, alçapão, respiros e piso de serviço.
- **Janelas**:
  - janelas grandes com caixilho bronze, bandeira, verga de pedra e toldo listrado vermelho e branco, com sanefa recortada e braços de ferro;
  - janela alta de vidro jateado no banheiro;
  - grelhas de ventilação nos fundos.
- **Drive-thru**:
  - janela de atendimento com folha corrida aberta e prateleiras de inox dentro e fora;
  - moldura vermelha e marquise de chapa com tirantes e luminária;
  - 2 balizadores amarelos.
- **Torre de entrada** vermelha, com:
  - porta dupla de vidro com bandeira;
  - faixa amarela e sol raiado no alto, sem texto;
  - beiral e telhado em pirâmide de chapa vermelha com juntas em pé, cumeeiras amarelas e pináculo;
  - dentro, vestíbulo com piso xadrez, tapete e forro com luminária.
- **Anexo envidraçado** (salão):
  - mureta de tijolo com capa;
  - caixilhos e cantoneiras amarelos;
  - platibanda vermelha com friso;
  - buzinote e condutor;
  - um milk-shake gigante no telhado.
- **Fundos**: porta de serviço com batente, arandela e soleira de concreto.
- **Terreno**:
  - pista do drive-thru em volta do prédio, com setas e faixa de parada;
  - painel de pedidos com ícones iluminados (lanche, copo, batatas) e barras de preço em branco;
  - interfone e pórtico de altura listrado com correntes;
  - estacionamento com 4 vagas, batentes de roda e faixa de pedestres;
  - calçadas de concreto com juntas, rampa com faixa tátil e pátio de blocos com gradil e 2 mesas com ombrelone;
  - placa num poste com painel de estrelas e um hambúrguer gigante (pão com gergelim, alface, tomate, queijo derretido e carne);
  - 5 postes, ilhas de grama com guia, árvores, arbustos, floreira e lixeiras.
- **Dentro**:
  - **Salão** com:
    - piso xadrez vermelho e creme;
    - forro modular com perfis e luminárias embutidas;
    - 3 cabines (booths) com encosto capitonê;
    - 2 mesas de 4 lugares e pendentes vermelhos;
    - estação de lixo com bandejas.
  - **Balcão** de ladrilho vermelho com faixa amarela, tampo de inox, 3 caixas sem texto, porta-guardanapos e bandejas, sob uma sanca com 4 quadros de cardápio iluminados, só com ícones.
  - **Cozinha** com:
    - piso de lajota;
    - chapa, 2 fritadeiras e estação de escorrer sob coifa de inox com filtros;
    - bancada de preparo, geladeira de 2 portas, máquina de refrigerante e balcão do drive-thru.
  - **2 banheiros** com vaso, lavatório, espelho e porta-toalha.
  - **Acabamentos**: portas internas almofadadas com guarnição, e rodapés que param nas portas.

Números: 95 peças, 201 posições, 5 portas, cerca de 95 mil triângulos no montado.

## Montagem
O prédio vai de x = -6 a 6 e de z = -5 a 5, com a frente para +Z. O piso fica em 0,15, o topo das paredes em 3,75 e o topo da mansarda em 5,14. A torre vai de x = -1,5 a 1,5 e de z = 5 a 7; o anexo, de x = -6 a -2 e de z = 5 a 8. O terreno vai de x = -12 a 13,5 e de z = -12 a 20.
- **Paredes** (módulos de 2 m, pivô na face externa, na cota do piso):
  - `w_plain`, `w_win`, `w_hwin` (banheiro), `w_dt` (drive-thru), `w_bdoor` (serviço), `w_vent` e `w_louver` (grelhas);
  - `w_open_a` / `w_open_b` são os vãos para o anexo e `w_vest_l` / `w_vest_r` os vãos para o vestíbulo da torre.
- **Quinas**: `corner`, com pivô na quina externa e a capa da barra em meia-esquadria.
- **Mansarda** (pivô na face da parede, na cota 3,75):
  - `mans` é a faixa de 2 m; `mans_a` e `mans_b` são as pontas, cortadas no rincão a 45°;
  - `mans_tl` e `mans_tr` são as faixas cortadas pela torre;
  - `hip` é a capa do rincão, com pivô na quina;
  - `roof_flat` é a laje, com pivô no centro.
- **Telhado**: `hvac` e `exhaust_fan`, sobre a laje; `downspout` (no chão) e `downspout_w` (na calçada).
- **Torre e anexo**: `tower` (pivô na face da frente, no eixo, cota do piso), `annex` (pivô na face da frente, em x = -4) e `milkshake`.
- **Portas**: `door_leaf_glass` (torre), `door_leaf_back` e `door_leaf_interior`.
- **Interior**:
  - `pw_rest` é a parede dos banheiros, `pw_div` a divisória entre eles e `pw_kit` a parede da cozinha;
  - `menu_header` (sanca com cardápios), `service_counter`, `drink_station`, `grill_line`, `prep_table`, `fridge` e `dt_counter`;
  - `booth`, `cafe_table`, `table2`, `trash_station`, `pendant` / `pendant_s`, `toilet` e `sink`.
- **Pisos e forros**: placas de 2 × 2 m.
  - `floor_dine` é o xadrez, `floor_kit` a lajota e `floor_half` meio a meio, sob a parede da cozinha.
  - `floor_ceil` / `floor_ceill` são o forro sem e com luminárias.
  - `_e…` marca o recuo em cm de cada lado (x-, x+, z-, z+).
- **Terreno**:
  - peças com pivô na origem do terreno: `asphalt`, `walks`, `lawn`, `markings` e `patio_fence`;
  - `burger_sign`, `dt_menu`, `dt_speaker`, `clearance_bar`, `light_pole`, `bollard`, `wheel_stop`, `bin`, `planter`, `umbrella_table_*`, `tree`, `tree_b` e `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render`, `red`, `brick`, `shingles`, `plaster`, `quarry`, `asphalt`, `concrete`, `paver`, `grass`, `membrane` e `wood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 8 caminhos:
  - o jogador vem do estacionamento, sobe a rampa, entra pela porta da torre e vai até o balcão;
  - do salão, entra no anexo envidraçado;
  - passa pela abertura do balcão e entra na cozinha;
  - da cozinha, sai pela porta de serviço;
  - do salão, entra no banheiro;
  - percorre a pista do drive-thru, passando sob o pórtico e pela janela de atendimento;
  - percorre a pista dos fundos;
  - sobe a guia e entra no pátio.

No visitante, é o prédio 36 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/lanchonete/gerar_kit.py        # escreve em out/ ao lado do script
python kits/lanchonete/verificar_flicker.py
```
