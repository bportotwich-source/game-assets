# Kit 59: condomínio de apartamentos (alto detalhe)

Condomínio de apartamentos de bairro com 2 prédios iguais de 3 andares, um escritório de locação, uma garagem coberta e um estacionamento. Cada prédio tem uma escada central fechada e 2 apartamentos por andar, o que dá 12 apartamentos no total.

Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). A arte é original e não tem nenhum texto: a placa da entrada e a vaga acessível usam só pictogramas. Os carros são genéricos e não têm marca.

## O conjunto
- **Prédios** (24 × 12 m, pavimentos de 3,0 m, frechal a 9,15 m):
  - **Fachadas**:
    - Térreo de tijolo vermelho, com embasamento de concreto, fiada saliente e cunhais de tijolo nas quinas.
    - Andares de tábuas sobrepostas bege em geometria, com faixa branca em cada laje e cantoneiras nas quinas.
    - Janelas de guilhotina com guarnição larga, verga com capa, peitoril com pingadeira, guarnição interna e peitoril interno.
    - Varanda de canto embutida em cada apartamento, com porta de correr, deck de tábuas, guarda-corpo branco e arandela.
  - **Telhado** de 4 águas a 26°:
    - Fiadas de telha asfáltica em geometria, capas na cumeeira e nos espigões, cumeeira ventilada e respiros.
    - Testeira, friso, forro do beiral com respiros, calhas com meia-esquadria e 4 condutores.
  - **Entrada**: porta de vidro do hall sob uma cobertura de telha com mãos-francesas, luminária e 2 arandelas.
- **Hall e escada** (todas as portas abrem):
  - Escada em U de concreto com piso de granilite e focinho de borracha: 16 espelhos de 18,75 cm por andar e patamar no fundo.
  - Corrimão de madeira nas paredes, guarda-corpo de aço com balaústres e guarda-corpo do último andar.
  - Caixas de correio embutidas na parede embaixo do lance.
- **Apartamentos** (sala, cozinha, copa, 2 quartos, banheiro, closet e varanda), todos mobiliados:
  - **Sala**: sofá, poltrona, mesa de centro, tapete, rack com TV, abajur de piso, planta e quadro abstrato.
  - **Cozinha em L**: armários de base e aéreos, tampo escuro com frontão de azulejo, pia dupla embaixo da janela, lava-louças, fogão com micro-ondas e exaustor, e geladeira.
  - **Copa**: mesa com 4 cadeiras e pendente.
  - **Quarto de casal**: cama de casal, 2 criados com abajur, cômoda com TV e quadro.
  - **Quarto 2**: cama de solteiro, escrivaninha com cadeira e guarda-roupa.
  - **Banheiro**: banheira com azulejo, chuveiro e cortina, gabinete com cuba e espelho, vaso, lavadora e secadora empilhadas e toalheiro.
  - **Closet**: prateleiras com cabideiro e roupas.
  - **Acabamentos**: pisos de carpete, vinílico e cerâmica, rodapé que para nas portas, portas de 5 almofadas com batente e guarnição, porta de entrada de 6 almofadas, luminárias de teto e detector de fumaça.
- **Escritório de locação** (10 × 8 m, térreo):
  - Tijolo até o peitoril e tábuas em cima, com telhado de 4 águas e varanda com 4 colunas.
  - Balcão de atendimento com 2 computadores, sala do gerente, espera com sofá e estante de folhetos.
  - Copa com pia, frigobar e micro-ondas, bebedouro e banheiro.
- **Lote**:
  - Estacionamento de asfalto com 18 vagas, faixas, batentes, vaga acessível e setas no acesso.
  - Garagem coberta de aço para 8 vagas, com 10 carros genéricos no total.
  - Calçadas com juntas, canteiros, grama, cercas vivas, árvores, arbustos e postes de LED.
  - Quiosque de caixas de correio, lixeira de tijolo com portão e 2 caçambas, condensadoras atrás dos prédios, mesas de piquenique, bicicletário, bancos, cerca de madeira nos fundos, placa monumento sem texto e rua.

## Peças
| Peça | O que é |
|---|---|
| `shell_g`, `shell_t` | Envoltória do térreo (tijolo) e de um andar (tábuas), com janelas, portas de correr, faixa e rodapé |
| `slab_g`, `slab_t`, `attic` | Contrapiso do térreo; laje com forro, luminárias e deck das varandas; forro do último andar |
| `walls_g`, `walls_t` | Paredes internas com batentes e rodapés (o térreo tem a parede embaixo da escada com as caixas de correio) |
| `stair`, `hall_rail` | Escada em U entre 2 pavimentos e guarda-corpo do último andar |
| `apt_r`, `apt_l` | Mobília e equipamentos do apartamento da direita e do da esquerda (espelhado) |
| `patio_*`, `balc_*`, `rail_*` | Mobília do pátio do térreo e da varanda, e guarda-corpo da varanda |
| `roof`, `entry_canopy` | Telhado de 4 águas com calhas e condutores, e cobertura da porta do hall |
| `office_shell`, `office_ceil`, `office_furn`, `office_roof` | Escritório de locação: envoltória e divisórias, forro, mobília e telhado com varanda |
| `door_unit`, `door_int`, `door_hall` | Folhas de porta (pivô na dobradiça) |
| `site`, `carport`, `mailboxes`, `dumpster_enc`, `fence`, `ac_home`, `picnic`, `monument`, `hedge`, `bike_rack`, `wheel_stop`, `lamp_pole`, `tree`, `tree_b`, `bush`, `bench`, `trash_can`, `car_*` | Lote e objetos externos |

Números: 51 peças, 268 posições (65 portas) e cerca de 615 mil triângulos no conjunto montado.

## Como gerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python3 gerar_kit.py              # gera out/ (pecas, texturas, montado e layout)
python3 verificar_flicker.py      # confere faces coplanares (TOTAL 0)
SOLO=1 python3 verificar_flicker.py
```
O `building_layout.json` traz cada peça com posição, giro, etiquetas (`floor0` a `floor3`, `predio_a`, `predio_b`, `escritorio`, `roof`, `ext`, `rua`) e o giro de abertura das portas. Os 2 prédios ficam em `grid.buildings`.
