# Kit 48: parque com concha acústica (alto detalhe)

Parque de bairro com uma concha acústica no fundo, palco com banda, bastidores de tijolo, quiosque de lanches e um gramado com bancos de praça virados para o palco. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto: a placa do quiosque tem só um picolé, a placa do gramado tem uma nota musical, as partituras e as embalagens são lisas.

## O conjunto
- **Palco** (22 × 12 m, tablado a 1,2 m do chão):
  - cantos da frente arredondados (raio de 3 m), embasamento de pedra com rodapé de concreto, capa de pedra clara e tablado de madeira;
  - escada de 6 degraus na frente e em cada lateral, com capas de pedra e corrimãos de ferro com pomos;
  - ribalta de lâmpadas em caixinhas na borda da frente.
- **Concha acústica**:
  - 5 arcos semielípticos telescópicos, do maior (9 m de raio, 8,2 m de altura) ao menor; cada arco tem a testa à mostra e o degrau fechado até o arco seguinte;
  - reboco creme por fora, forro de madeira por dentro;
  - no arco da frente, cordão de reboco, friso dourado e uma fileira de 41 lâmpadas; vara com 6 refletores dentro do 3º arco e pináculo dourado no alto.
- **Banda no palco**: bateria num praticável (bumbo, caixa, 2 tons, surdo, chimbal, 2 pratos, banco), piano de armário com 52 teclas e banqueta, 5 cadeiras dobráveis com estantes de partitura, 2 caixas de som e 2 pedestais de microfone.
- **Bastidores** (14 × 6 m, tijolo, piso na altura do palco, platibanda a 5,4 m):
  - embasamento de pedra com capa, friso de tijolo, janelas de guilhotina com verga, porta para o palco e porta lateral com arandela, patamar e escada de concreto com guarda-corpo;
  - laje com manta, rufo, alçapão, 2 exaustores, buzinote e condutor; forro com plafons;
  - dentro, corredor ao longo do palco e 3 portas: 2 camarins (bancada com espelho de lâmpadas, gavetas e potes, 2 cadeiras, arara de figurino com roupas, sofá e baú de turnê) e banheiro de ladrilho (vaso e pia com espelho); rodapés.
- **Quiosque de lanches** (6 × 4 m, tijolo):
  - telhado de 4 águas de telhas com beiral, cumeeira, espigões, testeira, calhas e condutores;
  - 2 janelas de atendimento com balcão de fora, mão-francesa e toldo listrado, placa redonda de picolé, porta dos fundos com arandela;
  - dentro, azulejo até 1,2 m, piso xadrez, balcão com máquina de pipoca, refresqueira de 3 bicos e caixa registradora, geladeira de bebidas, estante com caixas e pia.
- **Parque**:
  - 3 arcos de bancos de praça de ferro fundido com ripas verdes (28 bancos), todos virados para o palco, e um corredor de cascalho com guias no meio;
  - calçada de placas em volta do parque, do palco, dos bastidores e do quiosque, caminhos laterais até as escadas e até a porta dos bastidores;
  - 8 postes de lanterna com varal de luzes entre eles, 4 cangas de piquenique com cesta, pratos e frutas, carrinho de sorvete com guarda-sol, bebedouro, placa de nota musical, lixeiras, árvores, arbustos e cerca viva com passagens.

Números: 57 peças, 226 posições, 6 portas, cerca de 184 mil triângulos no montado.

## Montagem
O gramado fica em 0,05, as calçadas e o piso do quiosque em 0,15 e o tablado e o piso dos bastidores em 1,2. A frente é +Z: o palco vai de x = -11 a 11 e de z = -8 a 4, a concha começa em z = 0 e os bastidores vão de x = -7 a 7 e de z = -14 a -8. O quiosque vai de x = 13 a 19 e de z = -17 a -13. O parque vai de x = -26 a 26 e de z = -22 a 24, e o terreno de x = -28 a 28 e de z = -24 a 26.
- **Palco, concha e terreno** (pivô na origem): `stage`, `shell`, `site`, `string_lights`, `bs_stairs`.
- **Módulos dos bastidores** (pivô no meio da face externa, na cota do piso 1,2; 2 m): `b_plain`, `b_win`, `b_door`, `b_door_s` (porta para o palco). Os finais `_l` e `_r` são os módulos das quinas, encurtados 25 cm no lado esquerdo ou direito.
- **Módulos do quiosque** (mesmo pivô, cota 0,15): `q_plain`, `q_svc` (janela de atendimento com toldo), `q_sign`, `q_door`.
- **Coberturas, pisos e plantas** (pivô na origem, na cota do piso de cada prédio): `bs_roof`, `bs_floor`, `bs_plan`, `ki_roof`, `ki_floor`, `ki_plan`.
- **Portas** (pivô na dobradiça): `door_back` (3) e `door_int` (3).
- **Banda**: `drum_kit`, `piano`, `folding_chair`, `music_stand`, `speaker`, `mic_stand`.
- **Camarins e quiosque**: `makeup_counter`, `clothes_rack`, `trunk`, `sofa`, `guest_chair`, `wc`, `sink_one`, `counter_k`, `popcorn`, `soda`, `register`, `fridge`, `shelves`.
- **Parque**: `bench`, `lamp_post`, `blanket_r`, `blanket_b`, `ice_cream_cart`, `fountain`, `hedge` (2 m), `lawn_sign`, `trash_can`, `tree`, `tree_b`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render` (reboco), `plaster`, `stone`, `brick`, `planks` (madeira, forro da concha), `deck` (tablado), `shingles` (telhado do quiosque) e reboco liso para grama, cascalho e calçada. Ladrilho de 2 m, UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 7 caminhos:
  - da calçada da frente, pelo corredor de cascalho, sobe a escada do palco, atravessa a concha, entra pela porta dos bastidores e vai até o vaso do banheiro;
  - do caminho lateral, sobe a escada da lateral do palco até o pé da concha;
  - do caminho dos fundos, sobe a escada da porta lateral e atravessa o corredor dos bastidores até a outra ponta;
  - do corredor, entra em cada camarim até a bancada;
  - da calçada dos fundos, entra pela porta do quiosque até o balcão;
  - anda pela calçada da frente de uma ponta à outra do parque.

No visitante, é o prédio 48 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/concha-acustica/gerar_kit.py        # escreve em out/ ao lado do script
python kits/concha-acustica/verificar_flicker.py
```
