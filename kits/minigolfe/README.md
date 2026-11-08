# Kit 50: minigolfe (alto detalhe)

Minigolfe de bairro com o clube de reboco creme e a bola de golfe gigante no telhado, 5 buracos de grama sintética com moinho e farol, green de treino, lago com ponte de madeira e pátio com guarda-sóis. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto.

## O conjunto
- **Clube** (8 × 6 m, piso a 0,15 m, paredes até 3,2 m):
  - reboco creme sobre embasamento de tijolo com capa, friso branco sob o beiral, azulejo por dentro até 1,1 m e rodapé verde que para nas portas;
  - porta da frente com vidros, guarnição larga e arandela; porta dos fundos; janelas de guilhotina; janela de atendimento com balcão de fora, mãos-francesas e toldo listrado de vermelho e branco; placa redonda com pictograma de taco e bolinha;
  - telhado de 4 águas de telhas verdes com topo plano, espigões, testeira, calhas com condutores e mureta; no topo, a bola de golfe gigante (com covinhas) sobre o tee amarelo;
  - dentro, balcão com caixa e suporte de cartões, 2 estantes de tacos, 2 caixotes de bolinhas coloridas, estante, geladeira de bebidas, banco, vaso e lixeira.
- **5 buracos**: laje de concreto, grama sintética, borda de tijolo com capa, tapete do tee com bolinha e marcadores, placa do tee com 1 a 5 pontos (sem números), copo com aro branco e bandeirinha de cor própria; obstáculos de tijolo, pino e lombada de grama.
- **Moinho holandês** de 8 faces: base de pedra com o túnel por onde passa o buraco 2, corpo de reboco com cantoneiras, galeria de madeira com guarda-corpo e mãos-francesas, porta, janelinhas, capuz vermelho com cumeeira, eixo e 4 pás de treliça com lona.
- **Farol** listrado de vermelho e branco sobre pedras: plinto de concreto, porta, janelinhas, galeria com guarda-corpo, lanterna de vidro com montantes e lâmpada, cúpula vermelha e para-raios.
- **Green de treino** de forma livre com 3 copos e bolinhas.
- **Lago** com parede e beira de pedra, água transparente, pedras e juncos; **ponte de madeira em arco** com encontros de pedra, longarinas curvas, tábuas e corrimãos curvos.
- **Pátio e jardim**: passeios de placas de concreto, leito de saibro do campo, gramado, 2 mesas com guarda-sol de 8 gomos e 4 cadeiras, postes de lanterna, bancos, lixeiras, arbustos, palmeiras, mastro com bandeirola (sem símbolos) e gradil de ferro com lanças e pilares de tijolo na entrada.

Números: 46 peças, 89 posições, 2 portas, cerca de 144 mil triângulos no montado.

## Montagem
Os passeios, o pátio e o piso do clube ficam em 0,15 e o gramado em 0,05, com a frente para +Z (entrada do gradil em x = 6 a 8,5, z = 14,5). O clube vai de x = 10 a 18 e de z = 2 a 8; o moinho fica em (-12, 2) e o farol em (1,4, -7,4); o lago fica em (-2, 5,25) com a ponte de x = -4,8 a 0,8. O terreno vai de x = -20 a 20 e de z = -15 a 15.
- **Módulos de parede** (pivô no meio da face externa, na cota do piso; 2 m): `c_plain`, `c_win`, `c_door`, `c_door_b`, `c_svc`, `c_sign`. Os finais `_l` e `_r` são os módulos das quinas, encurtados 25 cm; `_ea` e `_eb` fazem a capa e o friso passarem da ponta para fechar a quina.
- **Cobertura, piso e rodapé** (pivô na origem, cota do piso): `c_roof`, `c_floor`, `c_plan`.
- **Peças inteiras** (pivô na origem): `hole_1` a `hole_5`, `practice`, `windmill`, `lighthouse`, `pond`, `bridge`, `fence`, `site`.
- **Portas** (pivô na dobradiça): `door_front`, `door_back`.
- **Clube**: `counter`, `register`, `score_stand`, `putter_rack`, `ball_bin`, `fridge`, `shelves`, `bench_in`, `plant`, `trash_can`.
- **Pátio**: `umbrella_r`, `umbrella_y`, `bench`, `lamp_post`, `flag_pole`, `palm`, `palm_b`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render`, `plaster`, `concrete`, `stone`, `brick`, `wood`, `dkwood`, `deck`, `roof_g` (telhas), `turf`, `turf2`, `grass`, `grass2`, `sand`, `rock`, `mill_w` e `bark`. Ladrilho de 2 m, UV em metros / 2. A água é um material transparente.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 6 caminhos:
  - do pátio, entra pela porta da frente e atravessa o clube até os caixotes de bolinhas;
  - anda pelo passeio do meio, passa pela ponte sobre o lago e chega à parede do clube;
  - anda pela grama do buraco 2 até a boca do túnel do moinho;
  - do passeio dos fundos até a base do farol;
  - anda pelo passeio da frente de uma ponta à outra até o gradil;
  - entra pela porta dos fundos e atravessa o clube até o balcão.

No visitante, é o prédio 50 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/minigolfe/gerar_kit.py        # escreve em out/ ao lado do script
python kits/minigolfe/verificar_flicker.py
```
