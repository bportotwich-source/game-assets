# Kit 53: parque de trailers (alto detalhe)

Parque de casas-trailer com seis trailers mobiliados em duas fileiras ao longo de uma rua de asfalto, cada um com varanda, garagem coberta, carro e quintal. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto; carros genéricos, sem marca.

## O conjunto
- **Trailer** (12 × 4 m, piso a 0,8 m): revestimento de chapa pintada com cordões de alumínio canelado em duas cores e faixa de acabamento, cantoneiras, janelas de correr de alumínio com molduras, toldos canelados em 2 janelas, ar-condicionado de janela, porta branca com janelinha, luminária, medidor de luz, portinhola do aquecedor, saia canelada com respiros e portinhola, engate com macaco.
  - Seis combinações de cor: creme com amarelo, azul com marinho, creme com rosa, creme com laranja, sálvia com creme e amarelo-claro com azul.
  - **Telhado** (peça separada): arqueado, com emendas, calhas de borda, respiros e suspiro; forro com plafons.
  - **Dentro**: sala com sofá, poltrona, mesa de centro, tapete e rack com TV de tubo; cozinha com armários, fogão de 4 bocas, coifa, cuba, armário aéreo, geladeira e mesinha com 2 cadeiras; banheiro com box, vaso, gabinete com espelho e azulejo; quarto com cama de casal, criado-mudo com abajur e cômoda com espelho. Divisórias com vãos guarnecidos, pisos de carpete, vinílico e ladrilho, rodapé que para nos vãos.
- **Lote**: varanda de madeira com tábuas, pilares, guarda-corpo de balaústres e escada de 4 degraus; toldo de alumínio sobre a varanda; garagem coberta de aço com 6 pilares e calha; depósito de chapa com portas de correr; botijões de gás sobre laje; poste de energia; lixeira com rodas; mesa de piquenique e churrasqueira ou cadeiras de praia e varal; floreira e treliça em alguns lotes.
- **Parque**: rua de asfalto com faixa tracejada e balão no fundo, entradas de cascalho, 2 lombadas, 4 postes de madeira com luminária, placa de entrada com pictogramas de trailer, árvore e sol, caixas de correio coletivas, caçamba, cerca de mourão com 2 travessas, árvores e arbustos.

Números: 58 peças, 228 posições, 6 portas, cerca de 207 mil triângulos no montado.

## Montagem
O gramado fica em 0,05, o cascalho em 0,07 e o asfalto em 0,09. A rua corre ao longo de Z (x = -2,5 a 2,5), com a entrada em z = 16 e o balão no fundo. O terreno vai de x = -22 a 22 e de z = -16 a 16.
- **Trailer** (pivô no centro, no chão): comprimento em X local, porta em +Z local, engate em -X local, piso a 0,8 m. Os lotes estão em `building_layout.json` (`lots`): a oeste em x = -10 (z = -10, -1, 8) e a leste em x = 10 girados 180° (z = -8, 1, 10). Todas as peças do lote (`deck`, `deck_awning`, `carport`) usam o mesmo pivô e giro do trailer.
- **Peças do trailer**: `trailer_a` a `trailer_f` (casca nas 6 cores), `trailer_roof`, `trailer_in` (piso, divisórias, rodapés e azulejo), `door_trailer` (pivô na dobradiça).
- **Móveis**: `sofa`, `armchair`, `coffee_table`, `tv_stand`, `rug`, `kitchen`, `fridge`, `dinette`, `chair_d`, `trash_can`, `shower`, `wc`, `vanity`, `towel_bar`, `bed`, `nightstand`, `dresser`, `plant`.
- **Lote e parque**: `deck`, `deck_awning`, `carport`, `shed`, `propane`, `power_post`, `wheelie_bin`, `picnic_table`, `grill`, `lawn_chair`, `lawn_chair_r`, `clothesline`, `planter`, `lattice`, `car_sedan_r`, `car_wagon_b`, `car_pickup_y`, `car_hatch_g`, `car_coupe_t`, `car_sedan_w`, `fence`, `sign_board`, `mailboxes`, `dumpster`, `speed_bump`, `street_light`, `tree`, `tree_b`, `bush`, `site`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`asphalt`, `gravel`, `grass`, `dirt`, `concrete`, `render`, `plaster`, `panel`, `cab`, `carpet`, `carpet_b`, `wood`, `dkwood`, `deck`, `pallet`, `brick` e `bark`. Ladrilho de 2 m, UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 6 caminhos:
  - da varanda, entra pela porta e atravessa a sala até a parede do fundo;
  - da cozinha, passa pelo corredor e entra no quarto até o ar-condicionado;
  - do corredor, entra no banheiro até o box;
  - anda pela rua inteira da entrada até a cerca do fundo;
  - sobe a escada da varanda e anda até o guarda-corpo;
  - entra num trailer da fileira leste até a parede do fundo.

No visitante, é o prédio 53 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/parque-trailers/gerar_kit.py        # escreve em out/ ao lado do script
python kits/parque-trailers/verificar_flicker.py
```
