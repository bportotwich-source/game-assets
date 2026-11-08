# Kit 57: campo de beisebol infantil (alto detalhe)

Campo de beisebol de bairro para a liga infantil. Tem o campo completo, alambrados, bancos de reservas, arquibancadas e uma cabine de 2 andares (lanchonete e banheiros embaixo, cabine de transmissão em cima). Também tem placar, torres de luz, gaiola de rebatidas, galpão de equipamentos e estacionamento.

Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto: as faixas da cerca e o cardápio usam só pictogramas, e o placar fica apagado, sem números. A bandeira é da liga e os carros são genéricos.

## O conjunto
- **Campo**:
  - Diamante de 18,29 m com 3 bases de lona (com pino de ancoragem), base do batedor de borracha e montinho com placa de borracha e saco de breu.
  - Infield de saibro com arco, círculo da base, caminhos das bases e gramado interno.
  - Gramado listrado em 2 verdes e pista de alerta junto à cerca.
  - Linhas de cal: linhas de falta, caixas do rebatedor e do receptor, caixas dos técnicos e círculos de espera, com tapete e tacos de peso.
- **Alambrados** de tela em losango (arames em geometria):
  - Backstop de 5,5 m com asas de 4 m, travessas, chapa de rodapé e escoras.
  - Cercas laterais de 1,22 m com portão de pedestre.
  - Cerca do outfield em arco (raio de 55 m) com capa amarela e faixas coloridas de pictogramas: bola, estrela, luva, taco, boné e troféu.
  - Postes de falta amarelos de 9 m com tela lateral.
- **Bancos de reservas** (2, telhado azul e vermelho):
  - Construção: piso de concreto, paredes de bloco com capa, porta de serviço nos fundos, frente de alambrado com 2 saídas para o campo, e telha ondulada com testeira, calha e luminária.
  - Dentro: banco corrido com bolsas, cubículos com capacetes, porta-tacos, garrafão térmico, balde de bolas e lixeira.
- **Arquibancadas de alumínio** (3, de 5 fileiras): assentos e pisos de perfil, corredor largo com degraus e corrimão, estrutura de aço e guarda-corpos.
- **Cabine** (6 × 5 m, 2 pavimentos, virada para a base do batedor):
  - **Fachadas**: térreo de bloco pintado com embasamento, andar de cima de tábua e mata-junta, e cinta entre os andares. Telhado de 4 águas com fiadas de telha em geometria, capas, testeira, forro do beiral, cornetas de som e para-raios.
  - **Lanchonete**:
    - Janela de atendimento com balcão de inox, porta de enrolar recolhida e toldo listrado. Na fachada, quadro do cardápio com pictogramas.
    - Atendimento: balcão com caixa, guardanapos e bombas de molho.
    - Cozinha: chapa, rolo de salsicha, geladeira de vidro, freezer, pipoqueira de carrinho, prateleiras e extintor.
  - **2 banheiros** com plaquetas de pictograma: vaso, pia de coluna, espelho, barra de apoio, secador e azulejo.
  - **Cabine de transmissão** (escada externa de aço com patamar):
    - Bancada sob a janela corrida, com mesa de som, microfone, controle do placar, livro de pontuação e rádio.
    - 3 cadeiras, prateleira, frigobar, ventilador, cabideiro e quadro de avisos.
- **Placar** do centro do campo:
  - Colunas de perfil I, painel com dígitos de segmentos apagados, e lâmpadas de bola, strike e out.
  - Pictograma de bola no alto, chapéu de chapa, passarela e escada de marinheiro.
- **Torres de luz** (4, de 18 m): poste cônico galvanizado com degraus, caixa de disjuntores e cruzeta com 6 refletores.
- **Gaiola de rebatidas**: pórticos de tubo, rede nas laterais, no teto e no fundo, grama sintética, tela L e máquina de arremesso. **Galpão de equipamentos**: chapa de madeira com mata-juntas, porta de tábuas em Z, janelinha com grade e telhado de chapa ondulada. Dentro do galpão: carrinho de cal, sacos de cal, estante com bases e cones, mangueira, carrinho de mão e rastelos.
- **Praça e estacionamento**:
  - Praça de concreto com juntas, mesa do apontador, bebedouro, bancos, mesas de piquenique, lixeiras, bicicletário, postes, mastro com a bandeira da liga, árvores e arbustos.
  - Estacionamento com vagas pintadas, batentes, guia e 5 carros.

Números: 56 peças, 118 posições, 9 portas, cerca de 285 mil triângulos no montado.

## Montagem
- **Posição do campo**: a base do batedor fica na origem e o campo se abre para -Z. A 1ª base fica em (12,93; -12,93), a 2ª em (0; -25,86) e a 3ª em (-12,93; -12,93). O montinho fica em z = -14,02.
- **Cercas e estacionamento**: as cercas laterais ficam a 8 m das linhas de falta e a cerca do outfield tem raio de 55 m. O estacionamento fica atrás do backstop (+Z).
- **Cabine**: centro em (10,8; 12,8), girada -140°. A frente local (+Z) olha a base. O térreo fica em 0,15 e o andar de cima em 3,15. As peças da cabine usam o pivô dela (veja `put_f` no gerador).
- **Campo**: `site`, `field`, `chalk`, `home_plate`, `base`, `mound`, `on_deck`.
- **Cercas**: `outfield_fence`, `side_fence_1`, `side_fence_3`, `backstop`, `foul_pole`, `gate_field`.
- **Bancos de reservas** (pivô no meio da frente; o campo fica para +Z): `dugout_b`, `dugout_r`, `dugout_bench`, `helmet_rack`, `bat_rack`, `water_cooler`, `ball_bucket`.
- **Arquibancada** (pivô no meio da frente; a plateia olha para +Z): `bleacher`.
- **Cabine**: `cabin_ground`, `cabin_slab`, `cabin_upper`, `cabin_roof`, `cabin_stair`, `concession`, `menu_board`, `service_window`, `restroom_a`, `restroom_b`, `press_box`.
- **Portas** (pivô na dobradiça): `door_service`, `door_shed`, `gate_field`.
- **Campo e entorno**: `scoreboard`, `light_tower`, `batting_cage`, `shed`, `shed_stuff`, `flagpole`, `scorer_table`, `fountain`, `park_bench`, `picnic_table`, `trash_can`, `bike_rack`, `lamp_post`, `wheel_stop`, `tree`, `tree_b`, `bush_row`, `car_sedan_r`, `car_wagon_b`, `car_hatch_y`, `car_pickup_s`.

## Texturas (PBR, embutidas nos GLB como JPEG)
Os materiais com textura são `asphalt`, `bark`, `bench_w`, `block`, `block_p`, `ceil`, `clay`, `conc_s`, `concrete`, `curb`, `dirt`, `dkwood`, `grass`, `grass2`, `grass_o`, `mulch`, `plaster`, `shingle`, `shingle_c`, `siding`, `track`, `vinyl_f` e `wood`. O ladrilho é de 2 m, com UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
  - O campo tem mais de 100 m de largura, por isso o `SOLO=1` deste kit afasta as peças 200 m uma da outra.
  - O arco da cerca tem 41 trechos. Assim o trecho do meio fica reto em X e nenhum trecho fica quase alinhado ao eixo.
- Godot 4.3, percursos testados:
  - do estacionamento até a praça;
  - pelo portão da cerca lateral para dentro do campo;
  - da base do batedor por cima do montinho;
  - pela porta dos fundos do banco de reservas e para fora, para o campo;
  - pelo corredor da arquibancada até a última fileira;
  - da porta dos fundos até a lanchonete, e para dentro de um banheiro;
  - pela escada até o patamar e para dentro da cabine de transmissão;
  - para dentro do galpão e da gaiola de rebatidas.

No visitante, é o prédio 57 (use `]` ou Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/campo-beisebol/gerar_kit.py        # escreve em out/ ao lado do script
python kits/campo-beisebol/verificar_flicker.py
```
