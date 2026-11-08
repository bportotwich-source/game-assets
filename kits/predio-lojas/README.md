# Kit 60: prédio de apartamentos com lojas (alto detalhe)

Prédio de esquina de 6 andares, com uma mercearia e uma lavanderia no térreo e 2 apartamentos por andar nos 5 andares de cima, o que dá 10 apartamentos. Tem escada interna até o telhado e 2 escadas de incêndio de aço na fachada.

Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). A arte é original e não tem nenhum texto: as testeiras das lojas usam só pictogramas (fruta e máquina de lavar). Os carros são genéricos e não têm marca.

## O conjunto
- **Prédio** (24 × 12 m, 6 pavimentos de 3,0 m, telhado a 18,15 m):
  - **Fachadas** de tijolo vermelho nas 4 faces:
    - Janelas de guilhotina de madeira com peitoril de pedra com pingadeira e verga de pedra com fecho.
    - No térreo, embasamento de pedra, faixa de pedra em toda a volta e quinas em meia-esquadria.
    - Janelas com ar-condicionado em alguns andares.
  - **Cornija** de chapa verde nas 4 faces, com coroa moldurada, dentículos, 78 mísulas com volutas e friso com almofadas.
  - **2 escadas de incêndio** de aço na frente, com 5 plataformas cada:
    - Plataformas de grade com alçapão, guarda-corpo com balaústres e mísulas (no 1º andar, tirantes até a parede).
    - Lances em zigue-zague com degraus de chapa e corrimão.
    - Escada de descida recolhida no 1º andar e escada de gancho por cima da cornija até o telhado.
- **Térreo**:
  - Vitrines de loja com rodapé almofadado, montantes, bandeira de vidrinhos, porta de madeira e vidro, pilastras de ferro fundido, testeira e toldo listrado de lona com armação.
  - **Mercearia**: 3 gôndolas, 7 geladeiras de bebidas, estantes, balcão com caixa registradora e monitor, banca de frutas, freezer de gelo e café.
  - **Lavanderia**: 7 lavadoras, 7 colunas de secadoras, mesa de dobrar, cadeiras de espera, carrinhos de roupa, máquina de sabão e TV.
  - Cada loja tem forro de chapa estampada, depósito com estantes, tanque e aquecedor, e lavabo.
  - **Hall**: porta de madeira com vidro e grade, bandeira, pilastras de pedra, marquise com luminária e caixas de correio embaixo da escada.
  - **Casa de máquinas** nos fundos: caldeira, aquecedor e quadro de medidores.
- **Escada** em U de concreto com piso de granilite, do térreo até a casa da escada no telhado (16 espelhos de 18,75 cm por andar).
- **Apartamentos** (sala, cozinha em L, copa, 2 quartos, banheiro e closet), todos mobiliados:
  - Piso de taco nos quartos e na sala, vinílico na cozinha e ladrilho sextavado no banheiro.
  - Radiadores de ferro embaixo das janelas.
  - Banheira de pés com chuveiro, aro e cortina, e azulejo de metrô.
  - Portas de 5 almofadas e porta de entrada de 6 almofadas.
- **Telhado**:
  - Manta, parapeito de tijolo com capa e rufo.
  - Casa da escada com porta de chapa, arandela e antena.
  - Caixa-d'água de madeira numa torre de aço, com aduelas, 7 aros, tampa cônica e escada.
  - Chaminé e respiros.
- **Esquina**:
  - Calçadas com juntas e caldeiras de árvore, guias, ruas com faixa amarela dupla, faixas de pedestre e linhas de parada.
  - Alçapão do porão na calçada, 2 semáforos, hidrantes, caixa de correio azul, caixa de jornal, postes, lixeiras e bicicletário.
  - 10 carros genéricos estacionados.
  - Quintal de concreto com caçamba, latas de lixo e cerca de madeira.

## Peças
| Peça | O que é |
|---|---|
| `shell_g`, `shell_t` | Envoltória do térreo (vitrines, hall, portas dos fundos) e de um andar (janelas), com rodapé interno |
| `slab_g`, `slab_t1`, `slab_t`, `slab_r` | Contrapiso do térreo com pisos; laje com forro e pisos (`t1` sobre as lojas); laje do telhado com forro do último andar |
| `walls_g`, `walls_t` | Paredes internas com batentes e rodapés (o térreo tem a parede embaixo da escada com as caixas de correio) |
| `stair`, `hall_rail` | Escada em U entre 2 pavimentos e guarda-corpo do vão no telhado |
| `apt_r`, `apt_l` | Mobília do apartamento da direita e do da esquerda (espelhado) |
| `shop_grocery`, `shop_laundry`, `shop_ceil`, `boiler_room` | Mercearia, lavanderia, forros de chapa das lojas com luminárias e casa de máquinas |
| `fe_1_*`, `fe_e_*`, `fe_o_*`, `fe_top_*` | Escada de incêndio por andar (`_r` e `_l`): 1º andar com escada de descida, andares pares e ímpares (o lance muda de lado) e último andar com escada de gancho |
| `roof` | Telhado com parapeito, cornija, casa da escada, caixa-d'água, chaminé e respiros |
| `door_unit`, `door_int`, `door_entry`, `door_shop`, `door_back`, `door_roof` | Folhas de porta (pivô na dobradiça) |
| `site`, `hydrant`, `traffic_signal`, `mailbox_st`, `news_box`, `ac_window`, `trash_bin`, `trash_can`, `dumpster`, `fence`, `bike_rack`, `lamp_pole`, `tree`, `tree_b`, `car_*` | Esquina e objetos externos |

Números: 53 peças, 183 posições (61 portas) e cerca de 850 mil triângulos no conjunto montado.

## Como gerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python3 gerar_kit.py              # gera out/ (peças, texturas, montado e layout)
python3 verificar_flicker.py      # confere faces coplanares (TOTAL 0)
SOLO=1 python3 verificar_flicker.py
```
O `building_layout.json` traz cada peça com posição, giro, etiquetas (`floor0` a `floor6`, `roof`, `ext`, `escada_incendio`, `mercearia`, `lavanderia`, `rua`) e o giro de abertura das portas. As medidas da escada de incêndio ficam em `grid.fire_escape`.
