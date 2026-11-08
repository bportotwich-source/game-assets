# Kit 34: banco com colunas (alto detalhe)

Banco neoclássico em cantaria de calcário, com pórtico de 4 colunas jônicas, frontão e telhado de cobre. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto em placas ou no frontão.

## O conjunto
- **Corpo** de 12 × 12 m, com:
  - piso 1,2 m acima do chão, sobre embasamento de granito;
  - pé-direito de 6,3 m até o entablamento;
  - pórtico de 3,5 m na frente.
- **Paredes de cantaria** em 2 camadas (pedra por fora, gesso por dentro):
  - embasamento de granito com capa moldurada, que para na porta dos fundos;
  - faixa de peitoril nas laterais e nos fundos.
- **Janelas**:
  - em arco nas laterais e nos fundos, com caixilho bronzeado, pinázios retos e radiais, moldura com impostas, chave e peitoril com mísulas;
  - retangulares sob o pórtico, de guilhotina, com moldura de orelhas e cornija sobre mísulas.
- **Pórtico**:
  - 4 colunas jônicas, cada uma com plinto, base ática, fuste de 24 caneluras com êntase, astrágalo, óvulos, volutas e ábaco;
  - antas nas quinas da frente, com base e capitel em meia-esquadria;
  - entablamento com arquitrave de 3 faixas, friso, dentículos, corona e cimalha, que dá a volta no prédio;
  - forro de caixotões;
  - escadaria de 8 degraus com blocos laterais e piso de mármore xadrez.
- **Porta principal** de 2 folhas de bronze:
  - almofadas com rosetas, vidro gradeado no alto e puxador vertical;
  - bandeira gradeada, moldura com orelhas e cornija.
- **Frontões** na frente e nos fundos:
  - tímpano recuado;
  - cornija inclinada;
  - acrotérios de palmeta;
  - na frente, medalhão liso com ramos.
- **Telhado** de cobre com patina a 22°, com juntas em pé, antefixas no beiral e cumeeira.
- **Fundos**: porta de serviço com bandeira e escada de pedra com guarda-corpo de ferro.
- **Rua**:
  - calçada;
  - relógio de rua;
  - 2 postes de luz e 2 lanternas na escadaria;
  - 2 bancos, 2 vasos de pedra, arbustos e gramado.
- **Dentro**:
  - **Salão** com teto de caixotões (grelha de vigas, molduras e rosetas), piso de mármore e 4 pendentes de bronze.
  - **Balcão dos caixas**:
    - base de mármore e tampo de madeira;
    - grades de latão com 6 guichês;
    - passagem para a área de trás junto à parede direita.
  - **Área de trás**, com forro mais baixo:
    - cofre com porta de aço (volante, anéis e trincos) e parede de cofres de aluguel;
    - corredor até a porta dos fundos;
    - escritório com piso de madeira.
  - **Acabamentos**: portas internas almofadadas com guarnição, e rodapés que param nas portas.

Números: 59 peças, 153 posições, 6 portas, cerca de 138 mil triângulos no montado.

## Montagem
O corpo vai de x = -6 a 6 e de z = -7,5 a 4,5, com a frente para +Z; o pórtico vai até z = 8. O piso fica em 1,2, o entablamento em 7,5 e o beiral em 8,75.
- **Paredes** (módulos de 2 m, pivô na face externa, na cota do piso):
  - `s_plain`, `s_arch` e `s_bdoor` são as laterais e os fundos, com o embasamento descendo até o chão.
  - `f_plain`, `f_rect`, `f_door_l` e `f_door_r` são a frente, sob o pórtico; as 2 últimas são as metades da porta principal.
- **Quinas**: `corner` (fundos) e `anta` (frente), com pivô na quina externa.
- **Pórtico**:
  - `column`, com pivô no centro, no estilobato;
  - `portico_ent` é o entablamento do pórtico com o forro;
  - `podium` é o embasamento com a escadaria.
- **Entablamento**: `ent` (módulo de 2 m) e `ent_corner`, com pivô na face externa, na cota 7,5.
- **Frontões**: `pediment_front` e `pediment_back`, com pivô no eixo, na cota do beiral.
- **Telhado**: `roof_strip` (faixa de 2 m, do beiral à cumeeira) e `ridge`.
- **Portas**: `door_leaf_bronze` (principal), `door_leaf_back` e `door_leaf_interior`, além de `vault_door`.
- **Fundos**: `back_steps`.
- **Interior**:
  - `pw_*` é a parede entre o salão e a área de trás, e `pz_*` as divisórias da área de trás;
  - `teller` é o balcão dos caixas e `deposit_boxes` a parede de cofres;
  - `coffers` é o teto do salão e `back_ceiling` o forro da área de trás;
  - `pendant` é o pendente.
- **Pisos**: `floor_<tipo>` são as placas de 2 × 2 m. Os tipos são `marble`, `vault` e `wood`. `_e…` marca o recuo em cm de cada lado (x-, x+, z-, z+).
- **Rua**: `sidewalk`, `lawn_*`, `lantern_post`, `street_clock`, `street_lamp`, `bench`, `urn` e `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`stone`, `carve`, `granite`, `marble`, `marble2`, `plaster`, `wood` e `concrete`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 6 caminhos:
  - o jogador vem da calçada, sobe a escadaria e entra pela porta principal até o balcão dos caixas;
  - sobe a escadaria entre as colunas até a frente do pórtico;
  - passa pela passagem do balcão e entra no escritório;
  - vai do salão pelo corredor até a porta dos fundos e desce a escada;
  - sobe a escada dos fundos e entra pelo corredor até o salão;
  - entra no cofre pela porta de aço.

No visitante, é o prédio 34 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/banco/gerar_kit.py        # escreve em out/ ao lado do script
python kits/banco/verificar_flicker.py
```
