# Kit 55: loft industrial convertido (alto detalhe)

Antigo armazém de tijolo de 7 pavimentos convertido em lofts, com café e portaria no térreo, escada de incêndio externa e cobertura com caixa d'água de madeira e deck. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto (só pictogramas); carros e food truck genéricos, sem marca.

## O conjunto
- **Prédio** (20 × 14 m, paredes de tijolo de 45 cm, térreo de 4,2 m e 6 andares de 3,4 m):
  - **Fachadas**: pilares de tijolo salientes e painéis rebaixados em cada vão de 3 m, janelas de aço de fábrica com grade de 4 × 5 vidros e báscula central inclinada, peitoris de pedra com pingadeira, vergas de tijolos em pé com cantoneira de aço, vãos cegos nos fundos (onde fica o núcleo), embasamento de pedra que para nas portas, faixa de pedra no alto do térreo.
  - **Térreo**: 4 vitrines de madeira pintada com rodapé almofadado, bandeira e testeira com frisos dourados, 2 portas com bandeiras laterais (café e portaria), porta de serviço de aço nos fundos com luminária.
  - **Platibanda**: cachorrada no topo de cada painel, fiada de cachorros, 2 faixas de tijolo, capa de pedra, manta subindo por dentro com rufo.
- **Estrutura interna**: pilares de madeira com sapata e capitel de aço (colunas de ferro fundido no térreo), 2 vigas mestras, barrotes a cada 80 cm, forro de tábuas, piso de tábuas corridas, ladrilho no hall e xadrez na portaria.
- **Núcleo**: escada em U de concreto com bocel de aço, corrimãos e guarda-corpo central, poço do elevador com portas de aço escovado em todos os andares, hall com porta corta-fogo da escada e porta de tábuas do loft.
- **Loft** (um por andar, cores alternadas): cozinha de parede com geladeira, armários, pia sob a janela, fogão com coifa e prateleiras abertas; ilha com 3 banquetas; mesa de jantar com 6 cadeiras; sofá em L, mesa de centro, tapete, poltrona, luminária de arco e móvel de TV; quarto atrás de divisória de aço e vidro com cama, criados-mudos e arara de roupas; escrivaninha, estante alta, banco de entrada com cabideiro; banheiro em caixa aberta com chuveiro de vidro, vaso, bancada e espelho; pendentes e plantas.
- **Café**: balcão de tábuas com tampo de mármore, vitrine de bolos, caixa, balcão dos fundos com máquina de espresso, moedor e xícaras, lousa com pictograma de xícara, banco estofado corrido, mesas de bistrô e pendentes verdes. **Portaria**: caixas de correio de latão, banco, tapete, bicicletário com 2 bicicletas.
- **Escada de incêndio** na face leste: 6 plataformas de grelha de 1,75 m (largas o bastante para o jogador) com chapa por baixo, guarda-corpo de balaústres e mãos-francesas, 5 lances em zigue-zague, portas de saída envidraçadas, escada basculante recolhida no 1º andar e escada de marinheiro até a cobertura.
- **Cobertura**: casa de máquinas de tijolo com porta, janela e poço do elevador mais alto; caixa d'água de aduelas com cintas e teto cônico sobre torre de aço contraventada, plataforma e escadas; deck de madeira com pergolado, varal de luzes, floreiras de aço corten, espreguiçadeiras, mesa e guarda-sol; 3 condensadoras.
- **Rua**: calçadas de placas com covas de árvore e grelhas, guias, rua com faixa, vielas, toldo listrado do café, marquise de aço da portaria, postes, banco, bicicletário, hidrante, lixeiras, caçamba, food truck amarelo com janela de serviço e 2 carros.

Números: 83 peças, 331 posições, 29 portas, cerca de 400 mil triângulos no montado.

## Montagem
O térreo fica em 0,15 e os andares em 4,35, 7,75, 11,15, 14,55, 17,95 e 21,35; a cobertura em 24,75 (`levels` em `building_layout.json`). O prédio vai de x = -10 a 10 e de z = -7 a 7, com a rua na frente (+Z) e a escada de incêndio na face leste (x = 10).
- **Envoltória** (pivô na origem, y = piso do pavimento): `envelope_ground`, `envelope_storey` (andares 1 a 6), `parapet` (na cobertura).
- **Lajes e núcleo**: `ground_slab`, `slab_1`, `slab_storey`, `slab_roof`, `core_ground`, `core_storey`, `stair_ground`, `stair_1`, `stair_storey`, `elev_door`, `post_iron`, `post_timber`.
- **Portas** (pivô na dobradiça): `door_shop`, `door_service`, `door_stair`, `door_loft`, `door_bath`, `door_fire_escape`, `door_roof`.
- **Loft**: `kitchen`, `island`, `dining`, `sofa_a`, `sofa_b`, `rug_a`, `rug_b`, `coffee_table`, `armchair`, `floor_lamp`, `tv_unit`, `partition`, `bed_a`, `bed_b`, `nightstand`, `wardrobe`, `desk`, `office_chair`, `bookcase`, `bathroom`, `coat_bench`, `pendant`, `plant`.
- **Térreo**: `cafe_counter`, `banquette`, `bistro_1`, `bistro_2`, `pendant_long`, `mailboxes`, `bench_lobby`, `rug_lobby`, `bike_rack`, `bicycle_b`, `bicycle_r`.
- **Escada de incêndio** (pivô em x = 10, y = piso): `fe_platform_low`, `fe_platform_a`, `fe_platform_b`, `fe_stair` (pivô no eixo da faixa, sobe para +Z ou -Z com rotação de 180°), `fe_ladder`, `fe_roof_ladder`.
- **Cobertura**: `bulkhead`, `water_tower`, `roof_deck`, `lounger`, `planter_box`, `umbrella`, `hvac`.
- **Rua**: `site`, `awning`, `entry_canopy`, `street_lamp`, `tree`, `tree_grate`, `bench`, `hydrant`, `trash_can`, `dumpster`, `food_truck`, `car_sedan_b`, `car_hatch_g`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`asphalt`, `bark`, `brick`, `brick_i`, `cab`, `carpet`, `carpet_b`, `conc_d`, `conc_s`, `concrete`, `coping`, `deck`, `dirt`, `dkwood`, `floor_w`, `grass`, `gravel`, `membrane`, `pallet`, `panel`, `plaster`, `render`, `stone`, `tank_w`, `tile_h`, `timber`, `wood`. Ladrilho de 2 m, UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: café e portaria da rua aos fundos, escada do térreo ao 6º andar e à cobertura, loft de ponta a ponta, saída para a escada de incêndio, plataformas e lances da escada de incêndio, porta da cobertura até o deck.

No visitante, é o prédio 55 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/loft-industrial/gerar_kit.py        # escreve em out/ ao lado do script
python kits/loft-industrial/verificar_flicker.py
```
