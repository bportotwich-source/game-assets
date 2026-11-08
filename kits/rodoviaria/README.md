# Kit 39: rodoviária streamline moderne (alto detalhe)

Rodoviária térrea no estilo streamline moderne, de reboco claro com faixas horizontais, uma quina arredondada com as portas de entrada sob uma marquise curva, totem de esquina e plataforma coberta para os ônibus. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: o totem e as placas usam só pictogramas.

## O conjunto
- **Prédio** de 20 × 12 m, com pé-direito de 4,5 m e platibanda até 5,9 m, com:
  - piso 0,15 m acima do chão, no nível da calçada;
  - paredes de reboco com rodapé de pedra, 3 frisos horizontais verdes e capa de cerâmica, que param nas portas;
  - janelas em fita de ponta a ponta com basculante, peitoril e, por dentro, peitoril de madeira;
  - painéis altos de bloco de vidro na frente e janelas altas de bloco de vidro nas laterais e nos fundos;
  - portas duplas de vidro com bandeira para a plataforma;
  - portas de serviço com arandela redonda e uma doca de bagagem com porta de enrolar aberta e defensas;
  - quinas vivas com os frisos em meia-esquadria.
- **Quina arredondada** de 4 m de raio, em 6 faces, com as 2 portas de vidro da entrada. Sobre ela, uma **marquise** em leque com bordo arredondado, faixa verde com 3 filetes de neon, forro com luzes embutidas e tirantes.
- **Totem** de esquina sem texto: lâmina de reboco com nervuras, bordas de chapa verde com neon, disco com pictograma de ônibus e coroamento com 3 anéis.
- **Cobertura**: laje com manta, rufo contínuo (inclusive no arco), lanternim de claraboia sobre o salão, 2 condensadoras, exaustores, alçapão, ralos e passarela.
- **Plataforma coberta** no lado oeste: laje de concreto com cantos arredondados, faixa verde com filetes brancos, forro com luminárias, 4 pilares de aço com base e capitel, condutores, e 4 postes de baia com discos coloridos.
- **Dentro**:
  - **Salão de espera** com piso de granilite com juntas de latão, bancos duplos, banco de parede, armários de bagagem, banca de jornais com toldo, quadro de partidas sem texto, relógio de parede, pendentes de globo, bebedouro, lixeiras e vasos.
  - **Bilheteria** com 2 guichês de grade e escritório (mesa, cofre e arquivo).
  - **Café** com balcão, banquetas e cozinha nos fundos, aberto para o salão por uma passagem de 3 m.
  - **Bagagem** com balcão, prateleiras e carrinho, ligada à doca.
  - **Banheiros** masculino e feminino com cabines, vasos e bancada de pias, piso de ladrilho.
  - **Acabamentos**: portas internas com guarnição e rodapés que param nas portas.
- **Terreno**:
  - rua com faixas e travessia de pedestres;
  - pátio dos ônibus com baias pintadas e batentes de roda;
  - pátio de serviço e faixa de táxi com placa de pictograma;
  - calçadas com juntas, plataforma com faixa amarela, covas de árvore com grade e gramado com guia;
  - postes, balizadores, bicicletário e árvores.

Números: 52 peças, 116 posições, 12 portas, cerca de 110 mil triângulos no montado.

## Montagem
O prédio vai de x = -10 a 10 e de z = -6 a 6, com a frente para +Z. A quina arredondada tem o centro em (6, 2) e raio 4. O piso fica em 0,15, o forro em 4,5 e o topo da platibanda em 5,9.
- **Paredes** (módulos de 2 m, pivô na face externa, na cota do piso; cada módulo tem a altura inteira): `w_rib` (janela em fita), `w_gb` (bloco de vidro alto), `w_high` (janela alta), `w_door2` (porta dupla), `w_svc` (porta de serviço), `w_dock` (doca) e `w_plain`; `corner`, com pivô na quina externa; `arc_wall` (quina arredondada, pivô no centro do arco).
- **Fora**: `marquee` (pivô no centro do arco), `pylon`, `roof`, `canopy` (plataforma), `bay_pole_1` a `_4` e `site` (pivô na origem).
- **Dentro** (pivô na origem): `floor` e `plan` (paredes internas, cabines e guichês).
- **Portas**: `door_leaf_arc` (entrada da quina), `door_leaf_glass` (plataforma), `door_leaf_metal` (serviço) e `door_leaf_interior`.
- **Móveis**: `bench_double`, `bench_wall`, `lockers`, `kiosk`, `depart_board`, `wall_clock`, `pendant_globe`, `water_fountain`, `trash_bin`, `planter`, `stool`, `cafe_counter`, `back_kitchen`, `bag_shelf`, `bag_cart`, `office_desk`, `safe`, `file_cab`, `sink_bank` e `urinal` (avulso).
- **Terreno**: `lamp_post`, `bollard`, `taxi_sign`, `bike_rack`, `wheel_stop`, `tree` e `tree_b`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render`, `plaster`, `terrazzo`, `lino`, `wood`, `dkwood`, `concrete`, `curb`, `asphalt`, `grass` e `membrane`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 7 caminhos:
  - da calçada da esquina, entra pela porta da quina e atravessa o salão;
  - do salão, sai pela porta dupla para a plataforma;
  - do salão, entra no banheiro masculino;
  - do salão, entra no banheiro feminino;
  - do pátio de serviço, entra pela porta dos fundos no café;
  - do pátio, sobe pela doca, passa pela bagagem e chega ao salão;
  - pela porta de serviço dos fundos, entra no escritório da bilheteria.

No visitante, é o prédio 39 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/rodoviaria/gerar_kit.py        # escreve em out/ ao lado do script
python kits/rodoviaria/verificar_flicker.py
```
