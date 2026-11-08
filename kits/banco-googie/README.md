# Kit 42: banco googie dos anos 50 (alto detalhe)

Agência bancária térrea no estilo googie, sob uma cobertura de cascas onduladas que avança sobre o drive-thru. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: o totem leva só um pictograma de moedas e uma estrela.

## O conjunto
- **Prédio** de 18 × 12 m, com piso a 0,15 m e paredes até 3,6 m:
  - frente toda de vidro: montantes dourados com aletas, painel turquesa embaixo, travessa da bandeira e porta dupla de vidro com barras cromadas e soleira de latão;
  - paredes laterais de pedra rústica; fundos de tijolo, com janelas altas em fita e porta de serviço com aba e arandela;
  - janela do caixa do drive-thru na parede leste, com gaveta de aço, aba com luz, alto-falante e botão;
  - cofre noturno na parede oeste;
  - faixa de vidro (clerestório) entre o topo das paredes e a casca, nas 4 fachadas, com montantes a cada 1 m e postes nas quinas.
- **Cobertura**: 9 cascas abobadadas de 3 m, inclinadas para a frente (4,25 m atrás e cerca de 5 m na frente), com capa branca, nervuras turquesa nos vales, testeira turquesa com filete dourado, gárgulas nos fundos e luzes redondas embutidas no forro. Ela cobre a calçada em volta do prédio e as 2 faixas do drive-thru.
- **Colunas em V** amarelas, que sobem do pé até os vales da casca: 4 na frente, 1 na ilha e 2 do lado leste.
- **Dentro**:
  - **Saguão** de granilite em placas de 1 m com filetes de latão e estrela de 8 pontas; lustres sputnik pendurados na casca. Na mobília: sofá baixo, 2 poltronas tulipa, mesa de centro em rim, relógio-estrela na parede de pedra, 2 mesas de preencher em bumerangue, organizador de fila com cordão, porta-folhetos e vasos de cuia.
  - **Balcão de 4 caixas** de nogueira com filetes dourados e tampo de mármore, vidro com passa-documentos, porta-canetas e apoio de pés; atrás, bancada com gavetas de dinheiro, somadoras, luminárias e banquetas.
  - **Grade baixa** com portinhola, separando o saguão da área dos funcionários; a porta redonda da caixa-forte fica à vista.
  - **Caixa-forte** com marco de aço, colar polido e porta redonda com volante e dobradiça; dentro, cofres de aluguel com portinhas de latão e carrinho de malotes. Cofre na área dos caixas.
  - **Gerência** com visor de vidro e porta de vidro: mesa de nogueira, cadeira giratória, 2 cadeiras de concha, arquivo e vaso.
  - **Copa** com mesa redonda, cadeiras de concha, armários, pia, cafeteira, geladeira arredondada e armários de aço.
  - **Cabine do drive-thru** com visor, bancada com microfone e terminal do tubo pneumático.
  - A área de serviço tem forro a 3 m com luminárias.
- **Drive-thru**: 2 faixas com setas, ilha com terminal de tubo pneumático e balizadores; o tubo sobe, corre sob a casca com tirantes, atravessa a parede de pedra e desce até a cabine.
- **Terreno**:
  - calçada coberta de placas em volta do prédio e caminho até a calçada da rua;
  - gramado com 2 canteiros em rim, pedras e iucas, palmeiras e luminárias de cogumelo;
  - totem turquesa com caixa luminosa, aleta em bumerangue e estrela atômica;
  - estacionamento com vagas pintadas e batentes, viela nos fundos com gramado e árvores;
  - calçada com juntas e rua com faixa amarela.

Números: 71 peças, 144 posições, 7 portas, cerca de 129 mil triângulos no montado.

## Montagem
O prédio vai de x = -10 a 8 e de z = -6 a 6, com a frente para +Z e o piso em 0,15. A cobertura vai de x = -11 a 16 e de z = -7,2 a 8,6. A parte de baixo da casca, sobre o piso, é `RH0 + RS·(z − RZ0) + RA·sen(π·u) − RT`, com `u` a fração de `(x − RX0) / 3` (os valores estão em `building_layout.json`). O terreno vai de x = -26 a 20 e de z = -16 a 18.
- **Fachadas** (módulos de 2 m, pivô na face externa, na cota do piso):
  - frente: `g_win` e `g_door`;
  - fundos: `b_win`, `b_door` e `b_plain`;
  - laterais: `s_plain`, `s_teller` (janela do drive-thru) e as pontas encurtadas `s_plain_fa` / `s_plain_fb` (na frente) e `s_plain_ba` / `s_plain_bb` (nos fundos).
- **Clerestório e cobertura** (pivô na origem, cota do piso): `clerestory`, `roof`.
- **Colunas** (pivô no pé, no chão): `vcol_f` (frente), `vcol_i` (ilha), `vcol_e1` e `vcol_e2` (lado leste).
- **Dentro** (pivô na origem, cota do piso): `floor`, `plan`, `core_ceil`, `rail_low`, `teller_counter`. `vault_frame` tem o pivô no centro do vão.
- **Portas** (pivô na dobradiça): `door_leaf_glass` (2 folhas), `door_leaf_back`, `door_leaf_office`, `door_leaf_int`, `vault_leaf` e `gate_c`.
- **Móveis**: `deposit_boxes`, `deposit_boxes_s`, `cash_cart`, `safe_box`, `check_desk`, `sofa`, `tulip_chair`, `coffee_table`, `sputnik` (no forro), `star_clock`, `planter_bowl`, `queue_posts`, `brochure_rack`, `exec_desk`, `office_chair`, `shell_chair`, `table_round`, `kitchenette`, `lockers`, `file_cab`, `stool` e `booth_desk`.
- **Drive-thru e terreno**:
  - `tube_kiosk`, `tube_run` (pivô na origem, cota do piso) e `bollard_y`;
  - `site` (pivô na origem), `totem`, `disc_lamp`, `night_drop`, `planter_box`, `trash_bin` e `wheel_stop`;
  - vegetação: `palm`, `palm_b`, `yucca`, `yucca_s`, `boulder`, `boulder_s`, `bush`, `tree` e `tree_b`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`fstone` (pedra rústica), `brick`, `plaster`, `concrete`, `asphalt`, `terrazzo`, `grass`, `lino`, `walnut`, `wood`, `curb` e `roofw`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 7 caminhos:
  - da calçada da rua, pelo caminho e pela porta de vidro, atravessa o saguão até a grade;
  - do saguão, passa pela portinhola até o cofre da área dos caixas;
  - percorre a faixa 1 do drive-thru sob a cobertura, da rua até a viela;
  - da viela, entra pela porta dos fundos na copa e vai até a parede da frente;
  - da área dos funcionários, entra na gerência;
  - da área dos funcionários, passa pela porta redonda e entra na caixa-forte até os cofres;
  - atravessa o saguão de leste a oeste até a parede de pedra.

No visitante, é o prédio 42 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/banco-googie/gerar_kit.py        # escreve em out/ ao lado do script
python kits/banco-googie/verificar_flicker.py
```
