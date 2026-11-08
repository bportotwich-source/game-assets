# Kit 58: hospital de 7 andares (alto detalhe)

Hospital de bairro em L, com 7 pavimentos. O térreo tem saguão, consultórios e pronto-socorro com entrada de ambulâncias. Os andares 1 a 6 são de internação, com 15 quartos por andar. Na cobertura ficam a casa de máquinas e um heliponto elevado. O lote tem estacionamento, ambulâncias e carros.

Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto: a sinalização usa só pictogramas. A cruz do hospital é branca sobre azul (não é o emblema da Cruz Vermelha), o heliponto tem uma cruz em vez de letra e os veículos são genéricos.

## O conjunto
- **Prédio** (planta em L de 24 × 12 m mais uma ala de 10 × 12 m, pé-direito de 3,6 m, 25,35 m até a cobertura):
  - **Fachadas**:
    - Térreo de pedra aparelhada, com embasamento e cornija de pedra.
    - Andares de tijolo bege, com cunhais de pedra nas quinas e faixa de pedra em cada laje.
    - Janelas de alumínio de guilhotina com bandeira fixa, peitoril e verga de pedra com fecho, e peitoril interno.
    - Janela alta da escada acima do patamar.
    - Platibanda de tijolo com capa de pedra e cornija de 3 degraus.
  - **Entradas** (todas as portas abrem):
    - Entrada principal com vitrine de alumínio, porta dupla de vidro e marquise de vidro em pilares de aço.
    - Pronto-socorro com porta dupla de vidro, sob a marquise de concreto das ambulâncias.
    - Porta de vidro para o estacionamento (oeste) e porta de serviço (leste).
- **Térreo**:
  - **Saguão**:
    - Recepção com balcão alto, 2 computadores e cadeiras.
    - Longarinas de espera com mesas de centro, plantas, máquina de bebidas, bebedouro e totem de senha.
    - Cadeiras de rodas, tapete de entrada e pilares revestidos.
  - **5 consultórios**, cada um com banheiro, maca, mesa com computador, cadeiras e negatoscópio.
  - **Pronto-socorro**, separado do saguão por porta dupla de vai-e-vem:
    - 6 leitos com trilhos e cortinas, painel de cabeceira com monitor e suporte de soro.
    - Balcão central de enfermagem e carrinho de emergência.
    - Triagem com mesa e balança, espera, macas, cadeiras de rodas, estante e pia.
- **Andares de internação** (1 a 6, iguais):
  - Corredor em L com corrimão de madeira, faixa de proteção, rodapé que para nas portas e luminárias no forro.
  - **15 quartos**:
    - Porta de laminado com visor, chapa de chute e alavanca.
    - Banheiro com azulejo e faixa colorida, vaso, lavatório com espelho, chuveiro com cortina, banco rebatível, barras de apoio e cordão de chamada.
    - Cama hospitalar com cabeceira levantada, grades, rodízios e suporte de soro.
    - Painel de cabeceira com gases, tomadas, luz de leitura e monitor de sinais vitais.
    - Cortina de privacidade no trilho em U, mesa de cabeceira, mesa de refeição, poltrona, TV, roupeiro, relógio e álcool em gel.
  - **Posto de enfermagem** com balcões nas 2 faces do corredor, computadores, armário de medicamentos, pia, quadro branco sem escrita e prontuários.
  - **Corredor**: carrinhos de medicação e de emergência, carrinho de roupa de cama e cadeira de rodas.
- **Circulação**:
  - **Escada** de 2 lances de granilite em todos os andares até a cobertura. Tem 18 espelhos de 20 cm, pisos de 28 cm, focinho antiderrapante, corrimão de madeira nas paredes e guarda-corpo de aço com balaústres.
  - **2 elevadores** com portas de inox, botoeira e indicador de setas, em todos os andares. São só fachada: não sobem.
  - Sinal de saída com pictograma.
- **Cobertura**:
  - Manta com rufos, ralos e respiros.
  - **Casa de máquinas** de tijolo, com porta para a cobertura, veneziana, exaustor e escada de marinheiro.
  - 3 condensadoras e uma unidade de tratamento de ar.
  - Placas luminosas da cruz na platibanda e biruta com luz de obstáculo.
  - **Heliponto elevado** (10,4 m de diâmetro, 1,8 m acima da cobertura):
    - Pilares e vigas de aço.
    - Pintura com anel amarelo, círculo de toque e cruz branca.
    - Luzes de borda e rede de proteção.
    - Escada de aço com patamar.
- **Lote**:
  - Praça de concreto com canteiros, bancos e placa monumento sem texto.
  - Acesso de ambulâncias com faixas pintadas, sob marquise de concreto com faixa azul, placa e protetores nos pilares, com 2 ambulâncias genéricas.
  - Estacionamento com vagas, batentes e 11 carros.
  - Postes de LED, balizadores, árvores, arbustos e rua.

## Peças
| Peça | O que é |
|---|---|
| `shell_g`, `shell_t` | Envoltória do térreo e de um andar tipo (fachadas, janelas, faixas, cunhais, rodapé) |
| `slab_g`, `slab_1`, `slab_t` | Contrapiso do térreo; laje com forro e luminárias sobre o térreo; laje dos andares (também a da cobertura) |
| `walls_g`, `walls_t` | Paredes internas do térreo e do andar tipo, com batentes, balcões, corrimão e portas dos elevadores |
| `room_ward_*`, `room_exam_*` | Quarto de internação e consultório, por tamanho (moldura local: a face do corredor fica em z = 0) |
| `stair` | Escada de 2 lances entre 2 pavimentos |
| `nurse_station`, `corridor_props`, `lobby`, `er` | Posto de enfermagem, objetos do corredor, saguão e pronto-socorro |
| `roof`, `helipad`, `ac_unit`, `ahu`, `windsock`, `cross_sign` | Cobertura e casa de máquinas, heliponto, condensadora, unidade de ar, biruta e placa da cruz |
| `canopy_entr`, `canopy_amb`, `ambulance` | Marquise de vidro, marquise das ambulâncias e ambulância |
| `door_room`, `door_bath`, `door_stair`, `door_glass`, `door_glass_1`, `door_service`, `door_double` | Folhas de porta (pivô na dobradiça) |
| `site`, `lamp_pole`, `bollard`, `monument_sign`, `park_bench`, `trash_can`, `tree`, `tree_b`, `bush`, `wheel_stop`, `car_*` | Lote e objetos externos |

Números: 54 peças, 466 posições no `building_layout.json` (206 delas são portas) e cerca de 1,02 milhão de triângulos no montado. Texturas PBR de 2 m (albedo, normal e ORM).

## Como gerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx
python3 gerar_kit.py              # gera out/ (pecas, texturas, montado e layout)
python3 verificar_flicker.py      # confere faces coplanares (TOTAL 0)
SOLO=1 python3 verificar_flicker.py
```
O `building_layout.json` traz cada peça com posição, giro, etiquetas (`floor0` a `floor7`, `roof`, `ext`, `rua`) e o giro de abertura das portas.
