# Kit 46: torre residencial art déco (alto detalhe)

Torre de apartamentos art déco de 18 andares, com fuste baixo de 14 × 14 m, recuo no 12º andar com terraço e fuste alto de 10 × 10 m coroado por uma faixa de terracota, pináculos e uma casa de máquinas com pirâmide e mastro (cerca de 70 m com o mastro). Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: o indicador do elevador não tem números e as caixas de correio não têm etiquetas.

## O conjunto
- **Fachada**:
  - saguão (andar 0, pé-direito de 4,2 m) de pedra clara sobre embasamento de granito, que para nas portas; janelas altas de bronze com bandeira gradeada e verga esculpida; portal de bronze com porta dupla, bandeira em raios de sol, molduras escalonadas, leque de pedra e 2 arandelas; porta de serviço nos fundos;
  - 1º andar (3,3 m) de pedra com janelas de aço, painéis canelados e cornija em meia-esquadria nas quinas;
  - fuste (andares 2 a 17, 3,1 m) de tijolo escuro com meios pilares de pedra salientes em cada módulo, janelas de caixilho de aço com 2 montantes, travessas e basculante, peitoril de pedra e painel de terracota com 2 chevrons embaixo; no meio da frente e dos fundos, vão cego com faixa de terracota canelada;
  - pilares de canto mais largos, que no recuo e na coroa sobem em pináculos escalonados;
  - platibanda do terraço com friso de chevrons e capa de pedra;
  - coroa de terracota com caneluras e friso em zigue-zague;
  - casa de máquinas de pedra com aletas de terracota, venezianas de bronze, porta e pilares escalonados; telhado em pirâmide de ardósia com rufos de bronze, mastro com anéis, esferas e farol vermelho.
- **Marquise** sobre o portal: laje de bronze com testeira em degraus, leque dourado, luzes embutidas e tirantes.
- **Dentro**:
  - **Saguão** com piso de granilite em leque a partir da porta (faixa, borda e filetes de latão), lambri de mármore com rodapé escuro, recepção curva com frisos de bronze e tampo de mármore, caixas de correio de latão, 2 sofás de couro, poltronas, mesa de centro de espelho, tapete, 3 lustres deco de anéis escalonados, vasos e relógio sem números. Nos fundos, sala de correio com estantes de encomendas e corredor de serviço com contêineres de lixo.
  - **1º andar**: salão social com sinuca, estantes, sofá e poltronas, mesa de jogos, carrinho de bar e palmeiras em vaso; biblioteca; lavanderia.
  - **Andares 2 a 11**: corredor com carpete e luminárias deco; 2 apartamentos de frente (hall, quarto, banheiro, sala com cozinha linear e geladeira, mesa de jantar, sofá, poltrona, rádio-vitrola, guarda-roupa) e 2 de fundos (banheiro, sala com cozinha no núcleo, quarto comprido ao longo da fachada dos fundos com escrivaninha e guarda-roupa no nicho atrás do núcleo).
  - **Andares 12 a 17**: 2 estúdios de frente (banheiro, cama, cozinha, mesinha, sofá de 2 lugares), lavanderia com lavadoras e secadoras e depósito com estantes, cadeiras empilhadas e bicicleta. No 12º andar, o corredor termina em portas de vidro para o terraço dos 2 lados.
  - **Banheiros** com banheira, cortina, chuveiro, vaso, pia de coluna e espelho.
  - **Núcleo**: escada em U com corrimãos de bronze e guarda-corpo de barras (a do saguão é de pedra com bocel de latão); elevador com portas de bronze com leque em relevo, indicador de ponteiro e botoeira; no último andar, escada de marinheiro até o alçapão da casa de máquinas.
- **Terraço** do recuo: piso de placas, floreiras com arbustos, árvores em vaso nos cantos, bancos, mesinhas de pedra e balizadores de luz.
- **Cobertura**: manta, alçapão, respiros e, dentro da casa de máquinas, máquina do elevador, quadro de comando e luminária.
- **Calçada** de placas com 10 árvores em grelhas de ferro, postes deco de fuste canelado, bancos, hidrante, bicicletário, guia, rua com faixa amarela tracejada e gramado nas bordas.

Números: 65 peças, 942 posições, 184 portas, cerca de 1,09 milhão de triângulos no montado (a maior parte são as portas almofadadas e as janelas, repetidas em 18 andares).

## Montagem
O prédio fica na origem, com a frente para +Z. Os pisos estão em `levels` do `building_layout.json`: saguão em 0,15, 1º andar em 4,35, andar 2 em 7,65 e depois de 3,1 em 3,1 m; o terraço do recuo fica em 38,65 e a cobertura em 57,25. O fuste baixo vai de -7 a 7 (andares 0 a 11) e o alto de -5 a 5 (12 a 17). Os módulos de fachada têm 2 m (centros de -6 a 6 no fuste baixo, de -4 a 4 no alto).
- **Módulos de fachada** (pivô no meio da face externa, cota do piso): `g_win`, `g_door`, `g_svc`, `g_plain` (saguão), `c_win`, `c_plain` (1º andar), `f_win`, `f_plain`, `f_door` (fuste), `parapet` (terraço) e `crown` (coroa).
- **Quinas** (pivô na quina externa): `corner_g`, `corner_c`, `corner`, `corner_par`, `corner_crown`.
- **Lajes e plantas** (pivô na origem, cota do piso): `floor_0`, `slab_1`, `slab_low`, `slab_up`, `slab_roof`; `plan_0`, `plan_1`, `plan_low`, `plan_up`; escadas `stair_0`, `stair_1`, `stair` e `roof_ladder`.
- **Móveis por ambiente** (pivô na origem, cota do piso): `lobby`, `mailroom`, `service`, `club`, `library`, `apt_front`, `apt_back`, `studio`, `laundry`, `storage` e os espelhos `*_r`; `chandelier` e `chandelier_s` vão no piso, sob o ponto do forro.
- **Portas** (pivô na dobradiça): `door_portal` (2 folhas), `door_entry`, `door_room`, `door_bath`, `door_stair`, `door_svc`, `door_terrace`, `door_roof`.
- **Cobertura e fora**: `terrace`, `crown_top`, `marquee`, `site`, `tree_grate`, `tree`, `tree_b`, `lamp_post`, `bench`, `hydrant`, `bike_rack`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`stone` (cantaria), `brick_d`, `terra`, `granite`, `plaster`, `terrazzo`, `marble`, `parquet`, `carpet`, `carpet2`, `concrete`, `asphalt`, `curb`, `grass`, `membrane`, `paver`, `roof_d` (ardósia), `dkwood` e `wood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 10 caminhos:
  - da calçada, pelo portal, atravessa o saguão até a parede dos fundos;
  - do saguão, pela porta da escada, sobe o primeiro lance até o patamar;
  - atravessa o salão do 1º andar até a parede dos fundos;
  - do corredor do andar 4, entra no apartamento de frente e vai até a fachada;
  - do corredor do andar 5, entra no apartamento de fundos até a parede do quarto;
  - da sala do apartamento de fundos, entra no quarto até a fachada dos fundos;
  - no andar 7, sobe o lance da escada até o patamar;
  - do corredor do andar 14, entra no estúdio até a fachada;
  - do corredor do andar 12, sai pela porta de vidro para o terraço até a platibanda;
  - da calçada dos fundos, pela porta de serviço, até a parede do saguão.

No visitante, é o prédio 46 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/torre-art-deco/gerar_kit.py        # escreve em out/ ao lado do script
python kits/torre-art-deco/verificar_flicker.py
```
