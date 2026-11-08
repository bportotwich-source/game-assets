# Kit 40: observatório neoclássico (alto detalhe)

Observatório de pedra calcária com um pavilhão central, 2 alas e 3 cúpulas de cobre, sobre um terraço alto com balaustrada e escadarias. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: o ático leva só um medalhão com planeta e estrelas.

## O conjunto
- **Prédio** térreo de pedra, com piso a 1,95 m do chão (sobre o terraço) e pé-direito de 4,05 m:
  - pavilhão central de 10 × 12 m e 2 alas de 6 × 8 m;
  - embasamento rusticado em 3 fiadas de blocos chanfrados, com capa moldurada que para nas portas;
  - cunhais alternados nas quinas;
  - janelas altas de 2 folhas de guilhotina com bandeira, moldura de pedra com orelhas, friso, cornija, peitoril com mísulas e avental; por dentro, peitoril de madeira, guarnição e avental;
  - porta principal de 2 folhas almofadadas com bandeira em leque, moldura com mísulas e cornija;
  - porta dos fundos com 2 arandelas;
  - entablamento contínuo com arquitrave de 2 faixas, friso com dentículos e cornija;
  - balaustrada na cobertura, com pedestais e balaústres torneados.
- **Pórtico** de 4 colunas jônicas com volutas, 2 pilastras, viga do entablamento, forro em caixotões com rosáceas douradas e 2 lanternas pendentes. Em cima, um ático liso com moldura e medalhão (planeta com anel e estrelas).
- **Cobertura** de lajotas com ralos, onde se anda entre as 3 cúpulas:
  - cúpula grande sobre um tambor de 16 faces: casca de cobre com nervuras, forro interno com costelas de madeira, fenda aberta com ombreiras de ferro e portinhola amarela recolhida;
  - 2 cúpulas menores sobre tambores de 12 faces, com a fenda fechada pela portinhola;
  - os tambores têm pilastras nas quinas, janelinhas com moldura, plinto, cornija com dentículos, trilho de ferro da cúpula e porta para a cobertura.
- **Dentro**:
  - **Saguão** com piso de mármore xadrez e faixa vermelha, sancas, medalhões e lustres. Tem uma escadaria de pedra maciça em lance reto, com pisos de mármore, guarda-corpos de pedra e pedestais com bola, que sobe direto para a sala da cúpula. Na mobília: planetário mecânico num pedestal de mármore, 2 vitrines com instrumentos e rochas, globo celeste, 4 quadros de mapa estelar sem texto, balcão de recepção, banco e relógio regulador.
  - Arcos largos com moldura de pedra e fecho, para as alas.
  - **Biblioteca** (ala oeste): estantes baixas sob as janelas, estantes altas, 2 mesas de leitura com feltro verde e abajures de banqueiro, 12 cadeiras e esfera armilar.
  - **Sala de instrumentos** (ala leste): 2 vitrines longas, meteorito sobre pedestal, cavalete com órbitas a giz e esfera armilar.
  - **Sala da cúpula grande**, com assoalho de carvalho:
    - telescópio refrator numa coluna de ferro fundido, com montagem equatorial, tubo creme com faixas de latão, buscador, ocular e contrapeso;
    - cadeira de observação de degraus;
    - mesa de cartas com mapa celeste, cadeira, arquivo de mapas, relógio e quadro estelar;
    - gradil em volta do vão da escada.
  - **Cúpulas menores**: luneta de latão na coluna e cadeira.
- **Terreno**:
  - terraço de 30 × 21 m e 1,8 m de altura, com muro de arrimo de pedra rusticada, capa, lajotas e balaustrada com pedestais e urnas;
  - escadarias de 12 degraus na frente e nos fundos, com muretas em rampa e pedestais;
  - gramado, caminho de cascalho com meio-fio e praça redonda com raios de pedra e esfera armilar;
  - 4 canteiros de flores com borda de buxo;
  - postes de ferro com globo, bancos, 2 lunetas públicas no terraço, urnas, árvores, ciprestes e arbustos.

Números: 55 peças, 182 posições, 6 portas, cerca de 458 mil triângulos no montado.

## Montagem
O pavilhão central vai de x = -5 a 5 e de z = -6 a 6, as alas vão até x = ±11 (z de -4 a 4), e o pórtico avança até z = 8,4, com a frente para +Z. O terraço fica em 1,8, o piso em 1,95, o forro em 6,0 e a cobertura em 6,45. A cúpula grande tem o centro em (0, 0) e as menores em (±8, 0). O terreno vai de x = -22 a 22 e de z = -17 a 26.
- **Fachadas** (módulos de 2 m, pivô na face externa, na cota do piso; cada módulo tem a altura inteira): `w_win`, `w_door` (porta principal), `w_bdoor` (fundos) e `w_plain`; `corner`, com pivô na quina externa.
- **Frisos e cobertura** (pivô na origem, cota do piso): `trims` (capa do embasamento, entablamento, dentículos, balaustrada e ático), `portico`, `roof`.
- **Cúpulas** (pivô no centro): `drum_main` / `drum_wing` (na cota da cobertura) e `dome_main` / `dome_wing` (sobre o trilho do tambor).
- **Dentro** (pivô na origem): `floor`, `plan` (paredes com os arcos), `stair` e `hole_rail` (na sala da cúpula).
- **Portas**: `door_leaf_front` (2 folhas), `door_leaf_back`, `door_leaf_drum` e `door_leaf_drum_s`.
- **Instrumentos e móveis**: `telescope`, `telescope_s`, `observer_chair`, `chart_desk`, `flat_file`, `reg_clock`, `star_panel`, `star_panel_s`, `orrery`, `display_case`, `display_case_l`, `celestial_globe`, `bookcase`, `bookcase_low`, `reading_table`, `chair`, `hall_bench`, `reception`, `meteorite`, `armillary`, `armillary_s`, `easel_chart`, `chandelier` e `porch_lantern`.
- **Terreno**: `site` (pivô na origem), `urn`, `lamp_post`, `coin_telescope`, `garden_bench`, `tree`, `tree_b`, `cypress`, `bush` e `bush_s`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`stone`, `stone_r`, `paver`, `plaster`, `oak`, `dkwood`, `concrete`, `gravel`, `grass` e `membrane`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 7 caminhos:
  - do caminho do gramado, sobe a escadaria da frente, atravessa o pórtico e o saguão, sai pela porta dos fundos e desce a escadaria de trás;
  - do saguão, passa pelo arco até a biblioteca;
  - do saguão, passa pelo arco até a sala de instrumentos;
  - sobe a escadaria do saguão até a sala da cúpula grande;
  - da sala da cúpula, sai pela porta para a cobertura e vai até o ático;
  - da cobertura, entra numa cúpula menor;
  - do terraço dos fundos, entra pela porta dos fundos e atravessa o saguão até o pórtico.

No visitante, é o prédio 40 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/observatorio/gerar_kit.py        # escreve em out/ ao lado do script
python kits/observatorio/verificar_flicker.py
```
