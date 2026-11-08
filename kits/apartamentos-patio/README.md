# Kit 56: apartamentos com pátio e piscina (alto detalhe)

Prédio de apartamentos dos anos 60, de 2 pavimentos, com duas alas de reboco verde-claro viradas uma para a outra e um pátio com piscina no meio. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto (só pictogramas). Os carros são genéricos e não têm marca.

## O conjunto
- **Duas alas** (7 × 19,5 m cada, paredes de 25 cm, pavimentos de 3,0 m):
  - A ala oeste vai de x = -12 a -5. A ala leste é a mesma, girada 180°.
  - **Fachadas do pátio**: janelas de correr com moldura saliente de reboco claro e peitoril com pingadeira, portas com batente, soleira de alumínio, arandela cilíndrica e plaqueta lisa, e faixas coloridas nas quinas.
  - **Fachada dos fundos**: basculantes de palhetas de vidro.
  - **Fachada da rua**: lisa, com estrela atômica de chapa e ondas em relevo. Não tem nenhum letreiro.
- **Galerias** no 1º andar: laje em balanço, pilares magenta com base de aço e guarda-corpo de barras com painel de losangos. A marquise da cobertura tem faixa colorida e forro.
- **Escadas de aço abertas** (uma por ala): banzos rosa, degraus de chapa dobrada com enchimento de concreto e bocel, corrimãos nos 2 lados, patamar ligado à galeria e base de concreto.
- **Cobertura**: laje com forro, manta, cascalho, platibanda com capa e rufo, buzinotes, condensadoras, respiros e antena de TV.
- **Garagem coberta** no térreo da frente da ala oeste:
  - Coluna de tubo, batentes de concreto com faixa amarela, armários de chapa no fundo, torneira, extintor e luminárias.
  - Parede de cobogó do lado do pátio.
  - Uma perua estacionada.
- **Escritório da administração** no térreo da frente da ala leste:
  - Vitrine de alumínio com marquise e porta para a rua, mesa, cadeiras, arquivo, bebedouro, mural, quadro de chaves e relógio.
  - Uma porta interna leva à **lavanderia**: lavadoras, secadoras, mesa de dobrar roupa, tanque e banco.
- **10 apartamentos mobiliados**, todos com a mesma planta:
  - **Sala**: sofá, mesa de centro em rim, poltrona, móvel de TV, luminária de tripé, tapete redondo, quadros e plantas.
  - **Cozinha em L**: fogão com coifa e geladeira arredondada.
  - **Copa**: mesa com cadeiras.
  - **Quarto**: cama, criados-mudos, cômoda e armário embutido de correr.
  - **Banheiro rosa**: azulejo com filete, banheira com cortina, vaso, gabinete e armário com espelho.
  - Detalhes: rodapés que param nas portas, tomadas, interruptores, termostato e plafons.
- **Pátio**:
  - Piscina azulejada com borda, escada de inox, degraus, luzes e água translúcida.
  - Espreguiçadeiras, mesa com guarda-sol e cadeiras de arame, 2 mesas de piquenique e churrasqueira.
  - 2 palmeiras em canteiros, floreiras, luminárias de globo e caixas de correio.
  - Muretas de cobogó com portão de ferro na rua, e muro com portão de serviço nos fundos.
- **Rua**: calçada de placas, guia rebaixada na garagem, asfalto com faixa tracejada, postes curvos, hidrante, caçamba no beco dos fundos, muros de divisa de blocos e 2 carros estacionados.

Números: 72 peças, 271 posições, 35 portas, cerca de 343 mil triângulos no montado.

## Montagem
- **Níveis**: o térreo fica em 0,15, o 1º andar em 3,15 e a cobertura em 6,15. O piso do pátio fica em 0,13.
- **Posição**: a rua fica na frente (+Z). As alas vão de z = -9,75 a 9,75, e o pátio de x = -5 a 5.
- **Alas** (pivô na origem, y = piso do pavimento): `envelope_w_ground`, `envelope_w_upper`, `envelope_e_ground`, `envelope_e_upper`, `ground_slab`, `slab_1`, `roof`, `gallery`, `stair_ext`.
- **Apartamento**: `unit_shell` é a casca interna, com pisos, paredes internas, armário e azulejo. Ela é posicionada pelo centro do apartamento (z = 6,4, 0 ou -6,4) e girada 180° na ala leste.
- **Móveis do apartamento**: `kitchen`, `bathroom`, `dinette`, `sofa_o`, `sofa_t`, `armchair_m`, `armchair_t`, `coffee_table`, `tv_console`, `floor_lamp`, `rug_m`, `rug_y`, `bed_g`, `bed_p`, `nightstand`, `dresser`, `plant`, `wall_art`.
- **Portas** (pivô na dobradiça): `door_unit`, `door_unit_t`, `door_int`, `door_office`, `gate`, `gate_rear`.
- **Garagem, escritório e lavanderia**: `carport`, `carport_screen`, `office_room`, `office_desk`, `office_chair`, `guest_chair`, `file_cabinet`, `water_cooler`, `bench_office`, `washer`, `dryer`, `folding_table`, `utility_sink`.
- **Pátio**: `pool`, `court_walls`, `lounger`, `umbrella_table`, `picnic_m`, `picnic_t`, `bbq`, `palm`, `bed_planting`, `planter`, `mailboxes`, `garden_lamp`.
- **Cobertura**: `ac_unit`, `vent_stack`, `tv_antenna`.
- **Rua**: `site`, `side_wall`, `street_lamp`, `hydrant`, `trash_can`, `dumpster`, `car_wagon_t`, `car_sedan_p`, `car_coupe_y`.

## Texturas (PBR, embutidas nos GLB como JPEG)
Os materiais com textura são `asphalt`, `bark`, `block`, `carpet`, `carpet_b`, `ceil`, `conc_d`, `conc_s`, `concrete`, `coping`, `curb`, `deck`, `dirt`, `dkwood`, `grass`, `gravel`, `membrane`, `mulch`, `palm_t`, `plaster`, `stucco`, `stucco_w`, `teak` e `wood`. O ladrilho é de 2 m, com UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, percursos testados:
  - da rua, pelo portão, até o fundo do pátio;
  - do portão dos fundos até o pátio;
  - da porta do apartamento, pela sala, até o quarto e o banheiro;
  - pela escada até o patamar, na galeria de ponta a ponta e para dentro de um apartamento do 1º andar;
  - na garagem até os armários;
  - da rua até o escritório, e do escritório até a lavanderia.

No visitante, é o prédio 56 (use `]` ou Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/apartamentos-patio/gerar_kit.py        # escreve em out/ ao lado do script
python kits/apartamentos-patio/verificar_flicker.py
```
