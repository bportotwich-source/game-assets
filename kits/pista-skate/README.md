# Kit 51: pista de skate (alto detalhe)

Pista de skate de praça com plataforma e bowl, snake run, quarter pipe, obstáculos de rua e um banheiro com marquise. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto.

## O conjunto
- **Plataforma** (14 × 13 m, topo a 1,6 m): muro de arrimo de concreto, piso alisado, capa nas bordas e guarda-corpos de tubo galvanizado.
  - **Bowl** em forma de estádio (12 × 7 m na borda, 2,3 m de fundo): parede reta de 30 cm, transição de 2 m de raio, fundo chato com ralo, coping de tubo de aço e capa de concreto em volta.
  - **Escada** de 9 espelhos com bocel de aço, muretas inclinadas e corrimãos; **bank** de descida de 5 m de largura.
- **Snake run** em S afundado no piso (4,8 m de largura, 1,3 m de fundo no meio), com a profundidade nascendo e morrendo nas pontas e coping de tubo onde é fundo.
- **Quarter pipe** de 1,5 m de raio com coping, chapa de aço, plataforma de 1,2 m com guarda-corpo e escada de marinheiro.
- **Obstáculos de rua**: manual pad, 2 ledges com cantoneira, 2 flat rails e kicker de madeira.
- **Banheiro** (6 × 4 m, bloco de concreto com soco azul): 2 sanitários com portas de batente de aço e pictogramas de pessoa, vaso, mictório, pia com espelho, secador de mão, piso de ladrilho, azulejo até 1,4 m, basculantes altas de vidro fosco, bebedouro na parede com pictograma e laje com marquise sobre 3 pilares de aço com luminárias.
- **Em volta**: 4 torres de refletores com 3 projetores cada, arquibancada de alumínio, bancos, lixeiras, skates no chão e encostados, placa de pictogramas (skate, capacete, proibido bicicleta), cerca de mourão com 3 travessas e entrada aberta, calçada, gramado, árvores e arbustos.

Números: 38 peças, 73 posições, 2 portas, cerca de 70 mil triângulos no montado.

## Montagem
A praça e o piso do banheiro ficam em 0,15 e o gramado em 0,05, com a frente para +Z (entrada da cerca em x = -2 a 2, z = 14). A plataforma vai de x = -18 a -4 e de z = -12 a 1; o snake run segue o eixo x = 7,5 de z = -11,5 a 6,5; o quarter pipe vai de x = 15,5 a 18,2 e de z = -10 a -2; o banheiro vai de x = -18 a -12 e de z = 6 a 10, com a marquise até z = 11,5. O terreno vai de x = -22 a 22 e de z = -16 a 16.
- **Módulos de parede do banheiro** (pivô no meio da face externa, na cota do piso; 2 m): `r_plain`, `r_win`, `r_door_m`, `r_door_f`, `r_fount`. Os finais `_l` e `_r` são os módulos das quinas, encurtados 20 cm; `_ea` e `_eb` fazem a capa do soco passar da ponta para fechar a quina.
- **Laje, piso e divisória** (pivô na origem, cota do piso): `r_roof`, `r_floor`, `r_plan`.
- **Peças inteiras** (pivô na origem): `deck`, `snake`, `quarter_pipe`, `fence`, `site`.
- **Porta** (pivô na dobradiça): `door_back`.
- **Obstáculos e objetos**: `manual_pad`, `ledge`, `flat_rail`, `kicker`, `skate_r`, `skate_b`, `skate_y`, `skate_lean_g`, `skate_lean_p`, `bleacher`, `bench`, `trash_can`, `floodlight`, `sign_board`, `wc`, `urinal`, `sink`, `tree`, `tree_b`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`concrete`, `slab`, `bowl`, `coping`, `cmu`, `cmu2`, `plaster`, `wood`, `dkwood`, `post`, `grass`, `grass2` e `bark`. Ladrilho de 2 m, UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 6 caminhos:
  - sobe a escada até a plataforma e anda até o guarda-corpo do outro lado;
  - entra no sanitário da esquerda até o fundo;
  - entra no sanitário da direita até o fundo;
  - atravessa o snake run da frente até a cerca do fundo;
  - desce da plataforma para dentro do bowl e para na transição do outro lado;
  - anda pela frente da praça de uma ponta à outra até a cerca.

No visitante, é o prédio 51 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/pista-skate/gerar_kit.py        # escreve em out/ ao lado do script
python kits/pista-skate/verificar_flicker.py
```
