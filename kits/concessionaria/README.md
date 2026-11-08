# Kit 47: concessionária de carros seminovos (alto detalhe)

Loja de carros seminovos dos anos 70/80, com showroom de vidro, oficina de bloco pintado ao lado, passagem coberta entre os dois e um pátio cheio de carros, bandeirolas, bandeiras de pena, boneco inflável e um totem. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original, sem nenhum texto: as placas só têm pictogramas (carro e chave inglesa), o painel do totem tem lâmpadas em losangos e seta, e os cartões de preço e as placas dos carros são lisos.

## O conjunto
- **Showroom** (14 × 10 m, piso a 0,15 m, forro a 3,6 m):
  - vidro de piso a forro com montantes de aço escuro, travessa, tampas de pressão e rodapé de bloco escuro; faixa de chapa branca com pingadeira no alto;
  - porta dupla de vidro com bandeira na frente; porta de vidro com vidros laterais para a passagem; fundos de reboco com 2 janelas de alumínio e porta de serviço com arandela;
  - cobertura em cunha de chapa branca com beiral largo (1,6 m na frente), manta, rufo escuro, calha nos fundos com 2 condutores, luzes no beiral e placa de pictograma de carro num mastro.
- **Dentro do showroom**:
  - salão de porcelanato em 2 tons com luminárias embutidas no forro: carro no prato giratório (aro cromado e luzes no rodapé), carro no chão, mesa de vendas com cadeiras, sofá de courvin com mesinha, expositor de folhetos sem texto, bebedouro e vasos;
  - nos fundos, divisória com portas e frente de vidro: banheiro (vaso e pia com espelho), sala de fechamento (mesa, cadeiras e arquivo), sala do gerente (mesa, cadeiras, estante e vaso) e copa (bancada com pia, cafeteira, micro-ondas e armários, geladeira, mesa com 2 cadeiras) com porta para fora.
- **Oficina** (10 × 10 m, platibanda a 5,6 m):
  - bloco pintado de grafite por fora e cinza claro por dentro, base de concreto e rufo;
  - 2 portões de enrolar com caixa do rolo, motor, trilhos e cantoneiras pintadas (um aberto, outro meio baixado), porta de chapa com capuz e arandela na frente e na lateral, janelas de aço com vidro aramado;
  - laje sobre vigas treliçadas aparentes, luminárias fluorescentes penduradas, 2 claraboias, ar-condicionado e chaminé no teto; caixa luminosa com chave inglesa e carro sobre os portões;
  - dentro, 2 elevadores de 2 colunas (um com carro levantado, outro baixado com picape), bancada com morsa, painel de ferramentas e luminária, armário de ferramentas, prateleira de pneus, pilha de pneus, compressor, tambores, macaco jacaré, enrolador de mangueira, faixas amarelas e manchas de óleo no piso;
  - escritório de peças com porta e visor de vidro: mesa, cadeira, arquivo e estante com caixas.
- **Passagem coberta** entre o showroom e a oficina, com piso de placas e luz.
- **Pátio**:
  - asfalto com vagas pintadas, setas e 2 entradas rebaixadas na calçada;
  - 12 carros genéricos sem marca em 5 tipos (sedã, perua, cupê, picape e hatch) e várias cores, com caixas de roda, cabine de vidro com colunas, grade, faróis retangulares, piscas, lanternas, frisos, maçanetas, retrovisores, bancos e painel por dentro, rodas com calota; os do pátio têm cartão de preço liso no painel; cachos de balões em 3 deles;
  - bandeirolas coloridas em cordas entre os postes e da quina do showroom; 6 bandeiras de pena com faixa e estrela; boneco inflável com soprador;
  - totem numa ilha de grama com meio-fio: caixa luminosa com pictograma de carro, painel de lâmpadas e estrela;
  - postes de 2 refletores, balizadores amarelos nos portões, lixeiras, calçada com juntas, rua com faixa amarela dupla, gramado, árvores e arbustos.

Números: 88 peças, 168 posições, 11 portas, cerca de 144 mil triângulos no montado.

## Montagem
O pátio fica em 0 e os pisos dos prédios em 0,15, com a frente para +Z (rua em z = 13,2 a 18). O showroom vai de x = -16 a -2 e de z = -11 a -1; a oficina, de x = 0 a 10 e de z = -11 a -1. As salas dos fundos do showroom começam na divisória em z = -7,8. O terreno vai de x = -19 a 19 e de z = -14 a 18.
- **Módulos do showroom** (pivô no meio da face externa, cota do piso; 2 m): `s_win`, `s_door2`, `s_door1`, `s_plain`, `s_win_s`, `s_door_s`. Os finais `_l` e `_r` são os módulos das quinas, encurtados 25 cm no lado esquerdo ou direito para encostar na parede da frente ou dos fundos.
- **Módulos da oficina** (mesmo pivô): `k_plain`, `k_win`, `k_win_n`, `k_door` (2 m) e `k_bay`, `k_bay_half` (4 m, portão de enrolar).
- **Coberturas, pisos e plantas** (pivô na origem, cota do piso): `sr_roof`, `link_roof`, `g_roof`, `sr_floor`, `g_floor`, `sr_plan`, `g_plan`; `svc_sign` vai na face da parede da frente da oficina.
- **Portas** (pivô na dobradiça): `door_glass` (3 folhas), `door_metal`, `door_metal_g` (2) e `door_int` (5).
- **Móveis**: `turntable`, `desk`, `office_chair`, `guest_chair`, `sofa`, `side_table`, `plant`, `brochure_rack`, `water_cooler`, `bookcase`, `file_cab`, `kitchenette`, `fridge`, `table_set`, `wc`, `sink_one`.
- **Oficina**: `lift_up`, `lift_down`, `workbench`, `tool_chest`, `tire_rack`, `tire_stack`, `compressor`, `drum`, `drum_r`, `floor_jack`, `parts_shelf`, `hose_reel`, `fl_light` (pivô no teto).
- **Carros** (pivô no meio entre os eixos, chão, frente +Z): `car_sedan_*`, `car_wagon_*`, `car_coupe_*`, `car_hatch_*`, `car_pickup_*`; os `*_svc` não têm cartão de preço. No elevador levantado, o carro vai 1,75 m acima do piso.
- **Pátio**: `site`, `pennants` (pivô na origem), `pylon_sign`, `lot_lamp`, `flag_r`, `flag_b`, `flag_y`, `flag_g`, `tube_man`, `balloons` (no teto do carro), `bollard`, `trash_can`, `tree`, `tree_b`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render` (reboco), `plaster`, `block_d` e `block_l` (bloco), `concrete`, `conc_f` (piso da oficina), `asphalt`, `curb`, `grass`, `carpet`, `wood` e `dkwood`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 9 caminhos:
  - da rua, pela entrada, atravessa o pátio, entra pela porta dupla do showroom e vai até o fundo da sala do gerente;
  - do showroom, pela porta de vidro, atravessa a passagem coberta e a oficina até a parede do outro lado;
  - do pátio, entra pela baia do portão aberto e passa por baixo do carro levantado até a prateleira de pneus;
  - da rua, pela saída, entra pela porta da frente da oficina até o armário de ferramentas;
  - da oficina, entra no escritório de peças até a estante;
  - do salão, entra na sala de fechamento até as cadeiras;
  - do salão, entra no banheiro até a parede do fundo;
  - do salão, entra na copa e sai pela porta dos fundos;
  - da frente, anda pelo pátio lateral entre a oficina e os carros.

No visitante, é o prédio 47 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/concessionaria/gerar_kit.py        # escreve em out/ ao lado do script
python kits/concessionaria/verificar_flicker.py
```
