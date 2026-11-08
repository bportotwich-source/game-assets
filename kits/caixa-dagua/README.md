# Kit 41: caixa-d'água de aço (alto detalhe)

Caixa-d'água dos anos 1930 sobre uma torre de aço de 4 pernas, com casa de bombas de tijolo embaixo e pátio de brita cercado. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: a placa do portão leva só o pictograma de uma gota.

## O conjunto
- **Torre** de 23,4 m:
  - 4 pernas inclinadas (meio-vão de 5,6 m na base e 2,85 m no topo), de perfil composto de 4 cantoneiras com treliça nas 4 faces e chapas de nó;
  - blocos de fundação chanfrados, placa de base e chumbadores;
  - vigas treliçadas horizontais em 3 níveis (6,6, 12,3 e 18 m), com banzos, diagonais e montantes;
  - contraventamento em X com tirantes redondos, esticadores e anel no cruzamento, nas 4 faces e nos 4 vãos;
  - anel de apoio de chapa com abas e 32 enrijecedores;
  - tubo de subida central de 1,1 m com flanges aparafusadas.
- **Reservatório** de 8 m de diâmetro:
  - costado de 4 anéis de chapa de 1,75 m, com junta sobreposta e 2 fileiras de rebites, e 12 costuras verticais rebitadas, desencontradas de um anel para o outro;
  - fundo em bacia com bocal do tubo de subida;
  - teto cônico com beiral, testeira e 24 nervuras, respiro de cogumelo, alçapão com guarda-corpo, pináculo com bola e para-raios de cobre;
  - passarela de grade em volta da base, com rodapé, guarda-corpo de 2 tubos, 24 montantes e 16 consolos diagonais até o anel de apoio.
- **Escadas de marinheiro** com gaiola de aros: uma ao longo da perna da frente até a passarela (passa por um vão na grade) e outra no costado até o teto, seguida de uma escada de telhado até o alçapão.
- **Casa de bombas** de 6 × 4 m, de tijolo com embasamento de concreto:
  - caixilhos de aço de 3 × 4 vidros com basculante, peitoril inclinado e verga de concreto;
  - porta de chapa com veneziana, visor e barra, soleira e arandela;
  - laje com forro, manta, platibanda com rufo, faixa de concreto, luva do tubo de subida, buzinote e condutor.
- **Dentro da casa de bombas**: o tubo de subida desce até o registro de gaveta com volante; curva e coletor até 2 bombas centrífugas azuis com motores aletados em bases de concreto, válvulas de retenção, manômetros; quadro elétrico com 3 chaves de faca e luzes; bancada com morsa e ferramentas; extintor; 2 luminárias industriais pendentes; ralo no piso.
- **Terreno**:
  - pátio de 20 × 20 m de brita, cercado de tela em losango com 3 fios de arame farpado nos braços dos mourões;
  - portão de carros de 2 folhas (4 m) e portão de pedestres;
  - calçada de concreto em volta da casa e caminho de placas até o portão;
  - poste de luz, placa azul com gota, armário elétrico, tampa de inspeção;
  - gramado, calçada com meio-fio e rebaixo, rua com faixa amarela, árvores e arbustos.

Números: 51 peças, 155 posições, 4 portas, cerca de 195 mil triângulos no montado.

## Montagem
A casa de bombas vai de x = -3 a 3 e de z = -2 a 2, com a frente para +Z e o piso em 0,15. A torre e o reservatório têm o centro em (0, 0). As pernas pousam em y = 0,94 e chegam ao anel em 23,4; o costado vai de 24 a 31 e o ápice do teto fica em 33,6. A cerca vai de x = -10 a 10 e de z = -10 a 10, e o terreno de x = -16 a 16 e de z = -14 a 22.
- **Casa de bombas** (módulos de 2 m, pivô na face externa, na cota do piso): `w_win`, `w_door` e `w_plain` nas fachadas da frente e dos fundos; `w_win_r` e `w_plain_l` nas laterais, que encostam por dentro das outras (ponta encurtada). `ph_roof` e `ph_floor` com pivô na origem; `downspout` na face dos fundos.
- **Equipamentos**: `valve_set` (pivô na origem), `pumpset`, `el_panel`, `workbench`, `extinguisher` e `pendant_lamp` (no forro).
- **Torre** (pivô na origem, no chão; cada peça é a da quina +X +Z ou da face +Z, girada 4 vezes em 90°): `leg`, `strut_1` a `strut_3`, `brace_0` a `brace_3`; `ring_girder` (na cota do anel), `riser`, `ladder_leg`.
- **Reservatório** (pivô no centro): `tank_course_a` / `tank_course_b` / `tank_course_top` (base de cada anel), `tank_bottom` e `balcony` (base do costado), `tank_roof` e `roof_ladder` (topo do costado), `ladder_tank`.
- **Cerca** (pivô no chão; trechos ao longo de +X com o lado de fora em +Z): `fence_panel` (2,5 m), `fence_panel_s`, `fence_panel_m`, `fence_post`, `fence_post_t` (terminal).
- **Portas e portões** (pivô na dobradiça): `door_leaf_steel`, `gate_leaf` (folha do portão de carros) e `gate_leaf_p` (pedestres).
- **Terreno**: `site` (pivô na origem), `light_pole`, `sign_plate`, `el_cabinet`, `manhole`, `tree`, `tree_b`, `bush` e `bush_s`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`brick`, `concrete`, `plaster`, `gravel`, `asphalt`, `grass`, `membrane`, `wood` e `dkwood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 5 caminhos:
  - da calçada, passa pelo portão de pedestres, segue o caminho, entra pela porta da casa de bombas e para na bancada;
  - da calçada, passa pelo portão de carros, por baixo da torre, até a cerca dos fundos;
  - dentro da casa de bombas, atravessa até a parede oeste;
  - na passarela do reservatório, anda até o guarda-corpo e desliza junto dele sem cair;
  - atrás da casa, vai até a cerca dos fundos.

No visitante, é o prédio 41 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/caixa-dagua/gerar_kit.py        # escreve em out/ ao lado do script
python kits/caixa-dagua/verificar_flicker.py
```
