# Kit 54: garagem vertical (alto detalhe)

Edifício-garagem de concreto com térreo e 3 lajes, rampas retas sobrepostas, torre de escada e elevador e entrada com cabine e cancelas. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto (só pictogramas); carros genéricos, sem marca.

## O conjunto
- **Garagem** (32 × 20 m, pé-direito de 2,85 m): laje do térreo e 3 lajes iguais (a última descoberta), pilares de 50 × 50 cm com chanfro e faixa de cor em cada pavimento (azul, verde, amarelo), vigas aparentes, viga de borda e mureta junto às rampas.
  - **Peitoris** pré-moldados com capa e juntas verticais em todas as bordas, com vão para a porta da torre.
  - **Rampas** retas de 24 m e 11 % na faixa sul, uma sobre a outra, subindo para +X: mureta interna, peitoril externo inclinado, faixa central tracejada e faixas de borda.
  - **Pintura e equipamentos**: vagas de 2,4 m, linhas de corredor, setas, batentes de roda, luminárias fluorescentes, tubo de sprinkler com bicos, abrigos de extintor, espelhos convexos e postes de 2 luminárias no terraço.
- **Torre de escada e elevador** (4,4 × 6,5 m): paredes de concreto com vãos das portas em cada pavimento, porta da rua com verga, janelas com caixilho e peitoril, pano de vidro na face leste com montantes e travessas, escada em U de 2 lances com bocel amarelo, laje inclinada por baixo e guarda-corpos, portas corta-fogo, portas de elevador com botoeira e indicador, laje de cobertura com manta, platibanda com rufo e casa de máquinas com veneziana.
- **Entrada**: cabine de cobrança com janelas e ar-condicionado, 2 cancelas listradas, totem de ticket, caixa de pagamento com pictograma de carro, barra de limite de altura, balizadores e placa vertical vermelha com 3 pictogramas de carro e seta.
- **Em volta**: calçada de placas, guia, rua de asfalto com faixa, rebaixo de entrada, canteiros com grama, árvores e arbustos, postes, lixeiras e 30 carros nas vagas e na rua.

Números: 33 peças, 194 posições, 5 portas, cerca de 117 mil triângulos no montado.

## Montagem
O térreo fica em 0,15 e os pavimentos em 3,0, 5,85 e 8,7 (`levels` em `building_layout.json`). A garagem vai de x = -16 a 16 e de z = -10 a 10; a faixa das rampas vai de x = -12 a 12 e de z = -10 a -4; a torre vai de x = 16,2 a 20,6 e de z = 3,5 a 10. A entrada fica na face oeste (x = -16), com a rua em x < -20. O terreno vai de x = -25 a 24 e de z = -14 a 14.
- **Estrutura** (pivô na origem, y = topo do pavimento): `deck` (lajes 1, 2 e 3), `ramp` (colocada nos pavimentos 0, 1 e 2), `column` (pilar inteiro do térreo à cobertura, nas linhas x = -15,73, -7,2, 0, 7,2, 15,73 e z = -9,73, -4, 1, 9,73), `site`.
- **Torre**: `tower` (casca), `stair_storey` (um pavimento da escada, nos pavimentos 0, 1 e 2), `stair_top` (patamar do terraço), `elev_door`, `door_metal` (pivô na dobradiça).
- **Objetos**: `booth`, `barrier`, `ticket_kiosk`, `pay_station`, `height_bar`, `bollard`, `blade_sign`, `roof_light`, `street_lamp`, `ext_cabinet`, `mirror_convex`, `wheel_stop`, `car_sedan_r`, `car_wagon_b`, `car_pickup_y`, `car_hatch_g`, `car_coupe_t`, `car_sedan_w`, `car_sedan_k`, `car_hatch_o`, `tree`, `bush`, `trash_can`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`asphalt`, `bark`, `brick`, `cab`, `carpet`, `carpet_b`, `conc_d`, `conc_s`, `concrete`, `coping`, `deck`, `dirt`, `dkwood`, `grass`, `gravel`, `pallet`, `panel`, `plaster`, `render`, `wood`. Ladrilho de 2 m, UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 6 caminhos:
  - sobe a rampa do térreo até o 1º pavimento e anda até o peitoril leste;
  - sobe o 1º lance da escada da torre até o patamar intermediário;
  - sai da laje pela porta da torre e desce o lance até o patamar de baixo;
  - atravessa o térreo pelo corredor até a mureta da rampa;
  - atravessa o terraço até a mureta da rampa;
  - anda pela faixa leste do térreo até fora do terreno.

No visitante, é o prédio 54 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/garagem-vertical/gerar_kit.py        # escreve em out/ ao lado do script
python kits/garagem-vertical/verificar_flicker.py
```
