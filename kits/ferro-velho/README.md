# Kit 52: ferro-velho (alto detalhe)

Ferro-velho de beira de estrada: pátio de terra cercado por muro de chapa ondulada, escritório de reboco com placa no telhado, fileiras de carros batidos, carros prensados, fardos de sucata, guincho e alpendre de peças. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto; carros genéricos, sem marca.

## O conjunto
- **Pátio** (36 × 24 m): terra batida com faixas de cascalho e manchas de óleo, calçada e gramado do lado de fora.
- **Muro de chapa ondulada** (2,4 m): chapas de cores e ferrugens diferentes, postes de tubo, travessas, braços inclinados com 3 fios de arame farpado e **portão de correr de tela** aberto na frente (x = -4 a 2).
- **Escritório** (6 × 8 m, reboco com platibanda): soco de concreto, janelas de correr com grade de ferro, peitoril e verga, ar-condicionado de parede com dreno, porta da frente e dos fundos com luminária, rufo, buzinotes e condutores, unidade de ar na laje e **placa no telhado** com pictogramas de carro e chave.
  - Dentro: piso de ladrilho xadrez, forro com luminárias, rodapé que para nas portas, balcão com caixa registradora, prateleiras de peças usadas, mesa com cadeira giratória, arquivo de aço, cadeiras de espera, bebedouro, lixeira e planta.
- **Carros**: 2 fileiras de carros batidos sem rodas sobre blocos de concreto (sedã, perua, hatch, cupê e picape, em cores desbotadas com ferrugem), alguns com capô aberto e motor à mostra, pilhas de 2 e 3 carros prensados, um carro inteiro e **guincho** com lança e gancho.
- **Sucata**: pilha de 6 fardos de carro prensado com cintas de aço, fardo solto, monte de sucata, motores sobre paletes, pilhas e monte de pneus, tambores.
- **Alpendre de peças** encostado no muro do fundo (14 × 4 m): pilares de aço, telhado de chapa ondulada, estantes de peças e rack de pneus.
- **Poste de luz** de madeira com luminárias.

Números: 54 peças, 84 posições, 2 portas, cerca de 112 mil triângulos no montado.

## Montagem
A terra do pátio fica em 0,05 e o piso do escritório e as calçadas em 0,15, com a frente para +Z (portão em z = 12). O muro vai de x = -18 a 18 e de z = -12 a 12; o escritório vai de x = 10 a 16 e de z = 3 a 11, com a frente para -X; o alpendre vai de x = -6 a 8 e de z = -12 a -8. O terreno vai de x = -21 a 21 e de z = -15 a 15.
- **Módulos de parede do escritório** (pivô no meio da face externa, na cota do piso; 2 m): `o_plain`, `o_win`, `o_door`, `o_door_b`, `o_ac_r_eb`. Os finais `_l` e `_r` são os módulos das quinas, encurtados; `_ea` e `_eb` fazem o soco passar da ponta para fechar a quina.
- **Cobertura, piso e rodapé** (pivô na origem, cota do piso): `o_roof`, `o_floor`, `o_plan`.
- **Peças inteiras** (pivô na origem): `site`, `fence`, `gate`, `lean_to`.
- **Porta** (pivô na dobradiça): `door_metal`.
- **Objetos**: `junk_sedan_r`, `junk_sedan_t`, `junk_wagon_b`, `junk_hatch_g`, `junk_coupe_o`, `junk_pickup_y`, `car_ok`, `car_stack_2`, `car_stack_3`, `tow_truck`, `bale`, `bale_pile`, `scrap_heap`, `engine_pallet`, `engine_pallet_b`, `tire_stack`, `tire_stack_b`, `tire_heap`, `tire_rack`, `drum_r`, `drum_b`, `drum_y`, `parts_rack`, `parts_rack_b`, `light_pole`, `counter`, `register`, `shelves`, `desk`, `office_chair`, `guest_chair`, `file_cab`, `water_cooler`, `trash_can`, `plant`, `tree`, `bush`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render`, `plaster`, `concrete`, `block`, `wood`, `dkwood`, `pallet`, `rust`, `rust_d`, `sheet_c`, `dirt`, `gravel`, `grass`, `bark` e `tile_a`. Ladrilho de 2 m, UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 5 caminhos:
  - entra pela porta da frente do escritório, atravessa e sai pela dos fundos até o muro;
  - entra pelo portão e atravessa o pátio até o fundo do alpendre;
  - anda pelo corredor entre as fileiras de carros da frente ao fundo;
  - anda por dentro do muro da frente até a quina do escritório;
  - atravessa o alpendre de uma ponta à outra até o muro.

No visitante, é o prédio 52 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/ferro-velho/gerar_kit.py        # escreve em out/ ao lado do script
python kits/ferro-velho/verificar_flicker.py
```
