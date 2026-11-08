# Kit 33: clínica de bairro (alto detalhe)

Prédio de clínica de 2 andares em tijolo vermelho, com marquise na entrada e cobertura plana. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto em placas.

## O conjunto
- **Prédio** de 24 × 10 m, com:
  - piso do térreo 0,15 m acima do chão, no mesmo nível da calçada;
  - 2 andares de 3,4 m (laje de 0,25 m);
  - platibanda de 0,95 m.
- **Fachada de tijolo** com faixas de concreto aparente:
  - faixa de peitoril com pingadeira, faixa de verga e faixa na linha de cada laje;
  - embasamento de concreto com chanfro, que para nas portas e vitrines.
- **Janelas de alumínio bronze**:
  - marco recuado, montante central e travessa;
  - vidro fixo embaixo e basculante em cima, com caixilho saliente e alavanca;
  - rufo de peitoril e peitoril interno.
  - Os banheiros têm janela alta, com uma folha só.
- **Platibanda**:
  - cachorrada de tijolos salientes sobre uma fiada contínua;
  - rufo de alumínio com pingadeiras dos dois lados e cobre-juntas;
  - por dentro, manta subindo 30 cm, com perfil de arremate.
- **Entrada**:
  - 2 vitrines de alumínio com rodapé de chapa e bandeira;
  - porta dupla de vidro com barra antipânico e puxador.
- **Marquise de concreto** (6,6 × 5,3 m):
  - testeira com rufo e pingadeira;
  - forro de gesso com 6 luminárias embutidas;
  - 2 pilares de tijolo com frisos, base e capitel de concreto;
  - condutor descendo atrás de um pilar.
- **Saídas de emergência** nas 2 pontas do corredor, cada uma com:
  - porta de chapa com visor, barra antipânico e mola;
  - luminária de parede e patamar de concreto.
- **Cobertura plana**:
  - manta com emendas;
  - 2 condensadoras grandes, com venezianas, grades de ventilador e dutos;
  - 2 exaustores, 3 respiros e 4 ralos;
  - alçapão com barras de segurança amarelas;
  - 3 buzinotes nos fundos, com caixa coletora, condutor, abraçadeiras, bica e bloco de respingo.
- **Terreno**:
  - calçada com juntas, rebaixo de guia com piso tátil e 2 balizadores;
  - pista de embarque de asfalto e ilha com 2 postes de luz;
  - placa de identificação em pedestal, sem texto;
  - 2 bancos, 7 árvores, arbustos, gramado e sebe nos fundos.
- **Dentro**:
  - **Térreo**: recepção com balcão em L, de madeira e laminado, e piso de granilite com juntas metálicas.
  - **Corredor central** de 2 m, com salas dos 2 lados: 8 no térreo e 10 no 1º andar.
  - **Banheiros**: um por andar, com ladrilho.
  - **Escada em U** de concreto:
    - 2 lances de 10 degraus com faixa antiderrapante e patamar no meio;
    - laje inclinada com forro e parede entre os lances;
    - corrimãos de tubo de aço.
  - **Acabamentos**: piso vinílico em placas de 2 tons, portas internas almofadadas com guarnição, e rodapés que param nas portas.

Números: 95 peças, 435 posições, 24 portas, cerca de 158 mil triângulos no montado.

## Montagem
O prédio vai de x = -12 a 12 e de z = -5 a 5, com a frente para +Z. O piso do térreo fica em 0,15, o do 1º andar em 3,55 e a cobertura em 6,95.
- **Paredes** (módulos de 2 m, pivô na face externa, na cota do piso):
  - `w_g_*` são as do térreo e `w_u_*` as do 1º andar.
  - Tipos: `plain`, `win`, `wc` (janela alta), `store` (vitrine), `door` (saída) e `entry` / `entry_r` (as 2 metades da porta dupla).
- **Quinas**: `corner_g`, `corner_u` e `corner_p`, com pivô na quina externa e as faixas em meia-esquadria.
- **Platibanda**: `parapet`, com pivô na face externa, na cota da cobertura.
- **Entrada**:
  - `canopy` é a marquise, com pivô na fachada, no eixo da entrada.
  - As portas são `door_leaf_glass` (entrada) e `door_leaf_exit` (saídas).
- **Escada**:
  - `flight` é um lance que sobe para -Z (o segundo vai girado 180°), e `landing` é o patamar.
  - `stair_closure` são os fechamentos de baixo.
  - Corrimãos: `hrail_wall`, `hrail_mid` e `rail_a`.
  - O vão na laje está em `building_layout.json` (`stair_holes`).
- **Interior**:
  - `cw_*` são as paredes do corredor (`_d` = com porta), e `pw_*` as divisórias entre as salas.
  - `counter` é o balcão e `door_leaf_interior` a porta interna.
- **Pisos**: `floor_<tipo>_<g|u|r>` são as placas de 2 × 2 m (g = térreo, u = 1º andar, r = cobertura). Os tipos são `vct`, `terrazzo`, `wc` e `membrane`. `_e…` marca o recuo em cm de cada lado (x-, x+, z-, z+), e `_h#` tem vão de escada.
- **Cobertura**: `rtu`, `exhaust`, `vent`, `drain`, `hatch` e `downspout`.
- **Terreno**: `sidewalk`, `curb_ramp`, `drive`, `island`, `lawn_*`, `exit_pad`, `pole_light`, `bollard`, `bench`, `sign`, `tree`, `tree_b`, `bush` e `hedge`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`brick`, `precast`, `plaster`, `concrete`, `vct`, `vct2`, `terrazzo`, `membrane`, `asphalt` e `wood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 12 caminhos:
  - o jogador vem da pista, sobe o rebaixo de guia e entra pelas 2 folhas da porta até o corredor;
  - da recepção, entra na sala dos fundos;
  - sai pelas 2 saídas de emergência;
  - sobe o 1º lance até o patamar (1,85 m) e o 2º até o 1º andar (3,55 m), seguindo até uma sala da frente;
  - entra em salas do térreo e do 1º andar e no banheiro de cima;
  - passa pela pista, embaixo da marquise.

No visitante, é o prédio 33 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/clinica/gerar_kit.py        # escreve em out/ ao lado do script
python kits/clinica/verificar_flicker.py
```
