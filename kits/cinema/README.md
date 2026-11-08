# Kit 30: cinema de rua (alto detalhe)

Cinema de rua dos anos 20, de terracota e tijolo, com bloco de 3 andares na frente, marquise iluminada e sala de projeção com plateia em degraus, palco e boca de cena dourada. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem marcas nem textos.

## O conjunto
- **Bloco da frente** de 14 × 8 m com 3 andares de 3,4 m (laje de 0,25 m). O piso do térreo fica a 0,15 m.
  - Fachada de terracota com meio-pilares nos encontros dos módulos e pilares em L nas quinas, que viram pináculos na platibanda.
  - Térreo com 3 portas duplas de bronze e vidro com bandeira de grade, vitrine da loja, porta do escritório, porta da loja e quadro de cartaz iluminado (sem texto). O embasamento de pedra para nas portas.
  - Janelas de guilhotina em arco pleno com bandeira de rendilhado, aduelas, peitoril com pingadeira e almofada embaixo; faixa moldurada no 1º andar e cimalha no 2º.
  - Platibanda com arcada cega de 3 arcos, faixa, capa e meio-pináculos com coroa e bola.
  - Laterais e fundos de tijolo, com janelas de guilhotina.
- **Marquise** de 7,4 m, com quadros de letreiro em branco na frente e nos lados (para o jogo pôr o texto), molduras douradas, fileiras de lâmpadas, forro com grade de lâmpadas, crista e tirantes de ferro.
- **Letreiro vertical** vermelho com chanfro, molduras douradas, medalhões em branco (sem letras), lâmpadas nas bordas, coroa com pinha e mãos-francesas.
- **Calçada** com bilheteria redonda com tambor de granito, vidro curvo com montantes de bronze, balcão, cornija dourada e cúpula com pinha, e 2 postes de 3 globos.
- **Dentro do bloco**:
  - saguão com piso de mármore e balcão de doces;
  - escada de 2 lances do térreo ao 2º andar, com corrimão, balaústres e guarda-corpo;
  - no 1º andar, o foyer de cima com 2 portas almofadadas de couro para a sala;
  - no 2º andar, a cabine de projeção com projetor e 2 visores;
  - salas com tacos, portas internas almofadadas com guarnição e rodapés que param nas portas.
- **Sala** de 14 × 18 m e 9 m de pé-direito:
  - paredes de tijolo com meias pilastras, fiada de tijolo escuro, cachorrada e capa; gesso colorido por dentro;
  - plateia em estádio: corredor de entrada no nível do 1º andar e 12 degraus de 0,9 m que descem até a orquestra, no nível do chão, com carpete e borda de latão;
  - fileiras de poltronas de veludo com pés de ferro fundido, braços de madeira e encosto com casca de madeira, e corredores de 1 m;
  - palco com tablado de madeira, frisos e almofadas douradas, ribalta e 2 escadinhas;
  - boca de cena de gesso com arco abatido, aduelas, pilastras e coroamento dourados, cortinas de veludo com abraçadeiras, bambinela e tela com moldura preta;
  - lustre de latão de 2 anéis e 6 arandelas;
  - 2 saídas de emergência laterais na altura da orquestra, com verga em arco, bandeira de aço, degrau e luminária.
- **Terraços** de manta com ralos, respiros e 3 condensadoras.

Números: 114 peças, 479 posições, 17 portas, cerca de 224 mil triângulos no montado.

## Montagem
O bloco da frente ocupa x de -7 a 7 e z de -2 a 6, com a frente para +Z. A sala ocupa x de -7 a 7 e z de -20 a -2.
- Fachada (pivô na face externa, na cota do piso do andar): `f_g_*` (térreo: `doors`, `door`, `vitrine`, `poster`), `f_u1_window`, `f_u2_window`, `f_parapet` e as quinas `f_corner_*`.
- Laterais e fundos do bloco: `s_*` e `back_corner_*`.
- A parede entre o bloco e a sala (z = -2) vai girada 180°: `b_g_plain`, `b_u1_door` (portas da sala no 1º andar), `b_u2_port` (visores da cabine) e `b_parapet`.
- Sala: `a_wall_plain`, `a_wall_door` (saída, em z = -15) e `a_pier` (quinas do fundo), todos com pivô na cota do saguão.
- Plateia (pivô no eixo, na cota do saguão): `aisle_floor` (corredor de cima), `tier_00` a `tier_11`, `orchestra_floor`, `stage`, `stage_steps`, `proscenium`, `curtain_side`, `valance` e `screen`. `seat_row` é uma fileira de 4 poltronas de 2 m, com pivô na borda da frente do degrau. Os degraus estão em `building_layout.json` (`auditorium`).
- Escada: `stair` sobe para -Z e `stair_both` é o 2º lance, girado 180°. Os vãos nas lajes estão em `building_layout.json` (`stair_holes`). `rail_*` são os guarda-corpos.
- Pisos: `floor_<tipo>_<g|u|r>` são as placas de 2 × 2 m. `_e####` param na face interna das paredes externas (flags x-, x+, z-, z+), e `_h#` têm vão de escada.
- Portas: a folha da direita das portas duplas vai girada 180° e abre com -85°.

## Texturas (PBR, embutidas nos GLB como JPEG)
`terra`, `terra2`, `brick`, `brick2`, `trim`, `plinth`, `plaster`, `aplaster`, `floor`, `concrete`, `membrane`, `marble`, `carpet`, `wood` e `stagefl`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador entra da calçada pelas portas duplas (a bilheteria fica na frente da porta do meio), pela porta da loja e pela do escritório; sobe os 2 lances (3,55 e 6,95 m); no 1º andar vai do hall ao foyer e passa pela porta da sala até o corredor de cima; desce o corredor da plateia, degrau por degrau, até a orquestra; e sai pela porta de emergência lateral para a rua.

No visitante, é o prédio 30 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/cinema/gerar_kit.py        # escreve em out/ ao lado do script
python kits/cinema/verificar_flicker.py
```
