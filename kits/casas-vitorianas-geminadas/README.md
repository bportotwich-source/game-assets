# Kit 61: casas geminadas vitorianas (alto detalhe)

Par de casas geminadas de tijolo no estilo inglês, uma espelhada na outra. Cada casa tem térreo elevado, 1 andar e sótão, anexo da cozinha nos fundos, jardim na frente e quintal atrás. A rua fica na frente.

Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). A arte é original e não tem nenhum texto. Os carros são genéricos e não têm marca.

## O conjunto
- **Casas** (12,8 × 9 m o par, mais o anexo de 2,8 × 4,2 m de cada casa; pavimentos de 3,0 m, piso do térreo a 0,45 m):
  - **Fachadas** de tijolo vermelho:
    - Embasamento de tijolo escuro com capa de pedra.
    - Faixas de tijolo amarelo na altura das vergas e faixa de pedra no nível do andar.
    - Janelas de guilhotina 2 sobre 2 com peitoril e verga de pedra (com fecho no térreo).
    - Janela de vitral geométrico na escada.
  - **Bay window** chanfrada de 2 andares em cada casa: 3 janelas por andar, peitoril e verga de pedra corridos, dentilhões e telhadinho de ardósia.
  - **Empena** de 55° em cima de cada bay, com janela do sótão, lambrequim recortado, pináculo e pendente.
  - **Porta da frente** de 4 almofadas, com aldrava, abertura de cartas e bandeira em leque. Tem arco pleno com aduelas alternadas de pedra e tijolo, 3 degraus de pedra e muretas laterais.
  - **Telhado** de 4 águas de 40°:
    - Ardósia em fiadas com degrau.
    - Cumeeiras e espigões de barro com crista.
    - Forro e testeira no beiral, calhas de ferro com meia-esquadria e condutores.
    - 4 chaminés com fiadas em balanço e potes de barro: a da parede de meia, as 2 laterais e a do fogão no anexo.
- **Por dentro** (em cada casa):
  - **Térreo**: hall com ladrilho xadrez e barra de terracota, sala com a bay, sala de jantar, cozinha e área de serviço no anexo.
  - **Andar**: quarto da frente com a bay, quarto dos fundos e banheiro.
  - **Sótão**: quarto embaixo do telhado, com forro inclinado.
  - **Escada em U** de madeira com passadeira e varões de latão, balaústres torneados, pilares com pinha e corrimão de mogno. Embaixo do lance há almofadas fechando o vão.
  - **Acabamentos**: rodapé alto, sanca, rodameio no hall, rosetas com pendente, assoalho, ladrilho de barro na cozinha e sextavado no banheiro.
  - **Lareiras** na parede de meia, com moldura de mármore, inserção de ferro, azulejos e espelho.
  - **Móveis**:
    - Sala: sofá Chesterfield, poltronas e estante.
    - Jantar: mesa de mogno com 6 cadeiras e aparador.
    - Cozinha: fogão a lenha de ferro, pia Belfast e guarda-louça.
    - Quartos e banheiro: cama de latão, banheira de pés, pia de coluna e vaso de descarga alta.
- **Jardim e rua**:
  - Na frente: mureta com capa de pedra e pilares, portão de ferro, caminho de ladrilho xadrez com meio-fio de corda, gramado, canteiro na bay, cerca viva e lixeiras de rodinhas.
  - No lado: corredor lateral com portão de tábuas.
  - Nos fundos: pátio de lajotas, gramado, caminho de cascalho, galpão de jardim, varal, banco, vasos e cerca de tábuas.
  - Na rua: calçadas, guias, faixa tracejada, postes de lanterna, árvores e 5 carros genéricos estacionados.

## Peças
| Peça | O que é |
|---|---|
| `shell_0_*`, `shell_1_*`, `shell_a_*` | Envoltória do térreo (com o anexo, degraus e porta), do andar e do sótão (meia-água, empena e parede de meia até o telhado) |
| `slab_0_*`, `slab_1_*`, `slab_a_*` | Contrapiso do térreo com pisos; laje com forro e pisos do andar e do sótão |
| `walls_0_*`, `walls_1_*`, `walls_a_*` | Paredes internas com batentes, rodapés, sancas e peitos de lareira |
| `stair_0_*`, `stair_1_*`, `rail_a_*` | Escada em U entre 2 pavimentos e guarda-corpo do sótão |
| `furn_0_*`, `furn_1_*`, `furn_a_*` | Mobília de cada pavimento |
| `roof_*`, `out_roof_*` | Telhado principal (com empena, bay, calhas e chaminés) e cobertura do anexo (com o forro da cozinha) |
| `site_*`, `party_front`, `street` | Lote de cada casa, mureta entre os jardins e a rua |
| `door_front`, `door_int`, `door_back`, `gate_iron`, `gate_wood`, `shed_door` | Folhas de porta e portões (pivô na dobradiça) |
| `hedge`, `bin_g`, `bin_b`, `shed`, `washing_line`, `garden_bench`, `pot_plant`, `fence*`, `post`, `street_lamp`, `tree`, `tree_b`, `bush`, `car_*` | Objetos do jardim e da rua |

`_r` é a casa da direita e `_l` é a espelhada (casa da esquerda).

Números: 65 peças, 130 posições (24 portas e portões) e cerca de 296 mil triângulos no conjunto montado.

## Como gerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python3 gerar_kit.py              # gera out/ (peças, texturas, montado e layout)
python3 verificar_flicker.py      # confere faces coplanares (TOTAL 0)
SOLO=1 python3 verificar_flicker.py
```
O `building_layout.json` traz cada peça com posição, giro, etiquetas (`floor0`, `floor1`, `floor2` para o sótão, `roof`, `ext`, `rua`, `casa_d`, `casa_e`) e o giro de abertura das portas. As medidas da bay window ficam em `grid.bay_window`.
