# Kit 43: cinema drive-in dos anos 50 (alto detalhe)

Cinema ao ar livre dos anos 50, com a lanchonete oval no meio do pátio, o telão na ponta e as fileiras de rampas em arco viradas para ele. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: o telão mostra uma paisagem pintada, o cardápio e o letreiro só têm pictogramas.

## O conjunto
- **Lanchonete** em forma de estádio (trecho reto de 6 m e pontas redondas de raio 4 m, 8 facetas em cada ponta), com piso a 0,15 m, forro a 3 m e platibanda até 3,75 m:
  - reboco creme com rodapé de azulejo vermelho (a capa do azulejo para nas portas), 3 frisos vermelhos no alto e rufo na platibanda;
  - frente com 2 janelas em fita de alumínio e porta dupla de vidro com bandeira, sob uma marquise oval com testeira vermelha, 2 tubos de neon e luzes embaixo;
  - fundos com 2 módulos de janelinhas de projeção (visor de vidro, guilhotina de aço levantada e capuz) e uma janela;
  - pontas com janelas, janelinhas altas de vidro canelado nos banheiros e 3 portas de serviço de chapa com arandela;
  - no teto, lanterna vermelha com venezianas e telhadinho de 2 águas, 2 respiros e ralos.
- **Dentro**:
  - **Salão** de piso xadrez vermelho e creme: balcão de lanches de azulejo vermelho com frisos cromados, caixa registradora e bisnagas; atrás, bancada com pipoqueira, refrigeradora de 4 torneiras, chapa de cachorro-quente, cafeteira e copos. Quadro de cardápio pendurado com 5 pictogramas e bolinhas de preço. 3 mesas com banquetas giratórias, 2 fliperamas, jukebox de arco, carrinho de condimentos e lixeira.
  - **Banheiros** masculino e feminino, cada um com porta para fora: vasos, mictórios com divisória, box com divisória, pias com espelho.
  - **Cabine de projeção** com porta para o salão: 2 projetores com chaminé mirando o telão pelas janelinhas, bancada de rebobinar e estante de latas de filme.
- **Telão** de 20 × 9 m com paisagem pintada (céu em 2 faixas, sol, mesas de pedra, estrada e cacto), moldura preta e rufo; embaixo, parede de tábuas com mata-juntas; atrás, 6 pilares de aço com escoras, travessas, contraventamento, passarela com guarda-corpo e escada de marinheiro.
- **Pátio**:
  - 4 fileiras de rampas de brita em arco (subida curta para o telão, descida longa); a 2ª fileira se divide em 2 trechos para contornar a lanchonete;
  - carros genéricos dos anos 50 em 4 cores (rabos de peixe, capota de 2 cores, cromados, rodas de faixa branca), já inclinados como na rampa, com vagas vazias no meio;
  - postes de alto-falante entre as vagas, com 2 alto-falantes de janela e lampadinha;
  - postes de luz com 2 refletores; calçada de placas em volta da lanchonete.
- **Parquinho** de areia com borda de dormente, embaixo do telão: balanço de 3 lugares, escorregador e gira-gira.
- **Entrada**: rua com faixa amarela, calçada com juntas, entrada de asfalto com 2 faixas e setas, ilha com a bilheteria (casinha de reboco com telhado de 4 águas vermelho, neon, janela de atendimento com vidro de correr, porta e balcão por dentro) e letreiro luminoso sem texto (rolo de filme, estrela, tira de filme e seta com lâmpadas apontando para a entrada).
- **Cerca** de tábuas em volta de tudo, gramado, árvores e arbustos.

Números: 57 peças, 200 posições, 7 portas, cerca de 149 mil triângulos no montado.

## Montagem
A lanchonete fica na origem, com a frente para +Z e o piso em 0,15. O trecho reto vai de x = -3 a 3 (módulos de 2 m em z = ±4); os centros das pontas ficam em x = ±3. O telão fica em z = -18. As rampas são arcos com centro em (0, -40); a borda da frente de cada fileira tem raio 26,6, 33, 46,6 e 52,6 (a altura da rampa está em `building_layout.json`). A cerca vai de x = -21 a 21 e de z = -23 a 18,5, com o portão entre x = 11 e 19. O terreno vai de x = -24 a 24 e de z = -26 a 25.
- **Paredes retas** (pivô na face externa, cota do piso): `w_win`, `w_port`, `w_door2`, `w_plain`.
- **Facetas das pontas** (pivô no centro da face externa, já cortadas em meia-esquadria): `f_win`, `f_high`, `f_door`, `f_plain`. A posição e o giro de cada uma estão no layout.
- **Anéis e cobertura** (pivô na origem, cota do piso): `trims`, `roof`; `front_canopy` tem o pivô na face da parede da frente.
- **Dentro** (pivô na origem, cota do piso): `floor`, `plan`, `snack_counter`; `ceiling_light` vai no forro.
- **Portas** (pivô na dobradiça): `door_leaf_glass` (2 folhas), `door_leaf_metal` (3 portas das pontas), `door_leaf_int` (cabine de projeção) e `door_leaf_booth` (bilheteria).
- **Móveis**: `projector`, `rewind_bench`, `film_rack`, `menu_board`, `table_stools`, `arcade`, `jukebox`, `condiments`, `trash_can`, `wc`, `urinal`, `sink_bank`, `sink_one`.
- **Pátio**: `screen` e `ramp_0` a `ramp_3` (pivô na origem); `car_a` a `car_d` (pivô entre os eixos, frente +Z), `speaker_post` (pivô no topo da rampa), `lot_lamp`.
- **Parquinho e entrada**: `swing_set`, `slide`, `merry_go_round`, `ticket_booth`, `marquee_sign`.
- **Cerca e terreno**: `fence_w` (2,5 m), `fence_w2` (2 m), `fence_w15` (1,5 m), `fence_post` (mourão do fim), `site`, `tree`, `tree_b`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render` (reboco), `plaster`, `concrete`, `asphalt`, `gravel`, `gravel_r` (brita das rampas), `grass`, `wood`, `dkwood`, `boards`, `membrane`, `curb` e `sand`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 7 caminhos:
  - da rua, pela faixa de entrada ao lado da bilheteria, até o pátio;
  - da calçada da frente, pela porta dupla, atravessa o salão até a parede da cabine de projeção;
  - do gramado da frente, sobe e desce as rampas das fileiras 4 e 3 entre os carros até a lanchonete;
  - de fora, entra pela porta do banheiro masculino;
  - de fora, entra pela porta do banheiro feminino;
  - do salão, entra na cabine de projeção até a parede do fundo;
  - de fora, entra na bilheteria pela porta dos fundos.

No visitante, é o prédio 43 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/cinema-drive-in/gerar_kit.py        # escreve em out/ ao lado do script
python kits/cinema-drive-in/verificar_flicker.py
```
