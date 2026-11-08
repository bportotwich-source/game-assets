# Kit 35: parque com casa de barcos (alto detalhe)

Pavilhão de madeira à beira de um lago, dentro de um parque com ponte de pedra, praça com chafariz e gradil. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto em placas.

## O conjunto
- **Pavilhão** de 8 × 10 m em estilo stick, com:
  - piso 0,45 m acima do chão, sobre embasamento de pedra;
  - paredes de 3,4 m;
  - telhado de 2 águas a 45°, com os frontões para a frente e os fundos.
- **Paredes** de tábua e mata-junta verde:
  - testeira no pé com pingadeira, que para nas portas;
  - friso no topo;
  - cantoneiras nas quinas.
- **Janelas de guilhotina** 2 sobre 2:
  - peitoril, avental e guarnições lisas;
  - frontãozinho sobre mísulas recortadas.
  - Embaixo da varanda, as janelas são mais baixas, com cornija simples.
- **Portas**:
  - porta dupla na frente, com vidro, almofadas e bandeira, sob um chapéu de 2 águas com mísulas curvas, escamas e lanterna;
  - 2 portas-balcão de 10 vidros para a varanda;
  - porta de serviço com escada de pedra na lateral.
- **Telhado**:
  - telhas de madeira em fiadas;
  - pontas dos caibros aparentes, testeira e calhas com condutores;
  - cumeeira com rolo de chapa;
  - lanternim com venezianas, cúpula de cobre e cata-vento (seta e rosa dos ventos sem letras);
  - chaminé de tijolo com chapéu.
- **Frontões**:
  - escamas pintadas;
  - testeiras recortadas com gotas;
  - na frente, tesoura decorativa com fusos, pendente e pináculo;
  - nos fundos, veneziana redonda.
- **Varanda e deck**:
  - varanda coberta de 2,4 m ao longo da fachada do lago, com postes, mãos-francesas, friso de fusos e treliça embaixo do piso;
  - cobertura de chapa com juntas em pé, forro de tábuas, calha e condutor;
  - deck aberto sobre o lago, em estacas, com guarda-corpo, 2 escadas e 3 mesas com ombrelones.
- **Parque**:
  - lago de 2 lobos com borda de blocos de pedra, pedras soltas e 3 barcos a remo;
  - ponte em arco de cantaria, com aduelas, piso de lajes, balaústres e 4 lampiões;
  - praça redonda com chafariz de 2 taças e cortinas d'água;
  - caminhos de saibro com guias de tijolo;
  - gradil de ferro em pilares de pedra, com portão em arco e lampiões;
  - calçada, 7 lampiões, 5 bancos, 9 árvores, arbustos, lixeiras e pedestal com urna.
- **Dentro**:
  - **Salão** com balcão de café (frente almofadada, tampo de madeira, apoio de pés de latão, vitrine e caixa sem texto), quadro de cardápio sem texto, 3 mesas e pendentes.
  - **Depósito de barcos** com prateleira de 2 canoas e remos.
  - **Escritório**, com escrivaninha e porta de serviço para fora.
  - **Acabamentos**: piso de tábuas, forro de tábuas, portas internas almofadadas com guarnição, e rodapés que param nas portas.

Números: 76 peças, 188 posições, 9 portas, cerca de 222 mil triângulos no montado.

## Montagem
O pavilhão vai de x = -4 a 4 e de z = -5 a 5, com a frente para +Z. O piso fica em 0,45 e o frechal em 3,85. A varanda vai até x = -6,4 e o deck até x = -9,5 (de z = -4 a 3). O parque vai de x = -24 a 10 e de z = -12,5 a 17,5, e a água fica em 0,1.
- **Paredes** (módulos de 2 m, pivô na face externa, na cota do piso):
  - Tipos: `w_plain`, `w_win`, `w_vwin` (janela sob a varanda), `w_fdoor` (porta-balcão), `w_bdoor` (serviço) e `w_door_l` / `w_door_r` (as 2 metades da porta dupla).
- **Quinas**: `corner`, com pivô na quina externa e a testeira, a pedra e o friso em meia-esquadria.
- **Frontões**: `gable_front` e `gable_back`, com pivô no eixo, na cota do frechal.
- **Telhado** (pivô na cota do frechal):
  - `roof_eave` são as águas; `_a` e `_b` são as pontas, com testeira inclinada;
  - `ridge` é a cumeeira, `cupola` o lanternim e `chimney` a chaminé;
  - `downspout` são os condutores.
- **Entrada**: `hood` (chapéu), `front_steps` e `service_steps`.
- **Portas**: `door_leaf_main`, `door_leaf_french`, `door_leaf_back` e `door_leaf_interior`.
- **Varanda**: `veranda` é a varanda com o deck inteiro, com pivô na face da parede do lago, na cota do piso. `porch_lantern` são as lanternas do forro.
- **Interior**:
  - `pw_hall` é a parede entre o salão e os fundos, e `pw_office` a do escritório;
  - `counter`, `menu_board`, `cafe_table`, `boat_rack`, `desk` e `pendant`.
- **Pisos**: `floor_wood` (piso) e `floor_ceil` (forro), placas de 2 × 2 m. `_e…` marca o recuo em cm de cada lado (x-, x+, z-, z+).
- **Parque**:
  - peças com pivô na origem do parque: `water`, `pond_rim`, `bridge`, `plaza`, `paths`, `lawn` e `sidewalk`;
  - `fountain`, com pivô no centro da praça;
  - `fence` (módulo de 2 m com pilar), `fence_np` (sem pilar), `fence_pier` e `gate`;
  - `lamp_post`, `bench`, `tree`, `tree_b`, `bush`, `monument`, `rowboat`, `umbrella_table_*` e `bin`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`boards`, `stone`, `shingles`, `scale`, `floor`, `plaster`, `ceil`, `deck`, `brick`, `rimstone`, `bstone`, `carve`, `paving`, `gravel`, `grass`, `concrete` e `wood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 8 caminhos:
  - o jogador vem da praça, sobe os degraus e entra pela porta dupla até o salão;
  - do salão, entra no depósito;
  - sai pela porta-balcão, atravessa a varanda e vai até o deck;
  - desce a escada do deck e segue pelo gramado;
  - atravessa a ponte sobre o lago;
  - entra pela porta de serviço até o escritório;
  - vai do depósito para o escritório e sai pela porta de serviço;
  - sobe a escada da varanda e percorre a varanda até o fim.

No visitante, é o prédio 35 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/casa-barcos/gerar_kit.py        # escreve em out/ ao lado do script
python kits/casa-barcos/verificar_flicker.py
```
