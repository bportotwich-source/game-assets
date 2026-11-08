# Kit 49: serraria (alto detalhe)

Serraria de beira de mata com o galpão da serra, um queimador cônico de serragem, galpão aberto de tábuas, pilhas de toras e um pátio de terra cercado. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original e sem nenhum texto.

## O conjunto
- **Galpão da serra** (12 × 10 m, piso a 0,15 m, beiral a 5 m):
  - tábuas pintadas de cinza com mata-juntas a cada 40 cm, embasamento de concreto, faixa de pingadeira, cantoneiras de tábua e guarnições largas;
  - portão de correr de 4 m (aberto) com trilho, roldanas e travessas em Z; porta de tábuas lateral com arandela; janelas de 4 vidros com peitoril; abertura da esteira;
  - telhado de 2 águas de chapa ondulada (nervuras em geometria), cumeeira, testeiras, lanternim de janelas com telhado próprio e tesouras de madeira à vista;
  - dentro, serra de fita com volantes e protetores, carro porta-toras sobre trilhos com cabeçotes e uma tora, mesa de roletes com tábua, refiladeira, 2 carrinhos de tábuas, bancada com painel de ferramentas, tambores e luminárias.
- **Queimador cônico** (8,4 m de base, 11,5 m de altura): chapa enferrujada com costuras e aros, base de concreto, portinhola, boca da esteira, escada de marinheiro e cúpula de tela no topo.
- **Esteira de serragem** em treliça de cantoneira, do galpão até a boca do queimador, com roletes, correia com serragem, chapas laterais, funil e cavalete contraventado.
- **Galpão aberto** (16 × 8 m): laje, pilares de madeira sobre blocos, vigas, mãos-francesas, tirantes, caibros, cumeeira e telhado de chapa ondulada; 8 pilhas de tábuas tabicadas.
- **Escritório** (4 × 4 m): tábua e mata-junta, telhado de chapa com cumeeira ao longo de Z, forro, porta com arandela e degrau; dentro, mesa, cadeira, cadeira de visita, arquivo e fogão a lenha com cano até a chaminé.
- **Pátio**: 2 pilhas de toras com estacas, carregadeira amarela segurando uma tora, caminhão de toras (capô vermelho, 3 eixos, 7 toras nos fueiros), paletes com fardos cintados, montes de serragem, tambores, poste de madeira com luminária, terra batida, cascalho, gramado, cerca de mourão com porteira aberta e pinheiros.

Números: 48 peças, 95 posições, 2 portas, cerca de 77 mil triângulos no montado.

## Montagem
O pátio fica em 0 e os pisos em 0,15, com a frente para +Z (porteira em z = 17,5). O galpão da serra vai de x = -12 a 0 e de z = -14 a -4; o queimador fica em (9, -9); o galpão aberto vai de x = -14 a 2 e de z = 2 a 10; o escritório vai de x = 12 a 16 e de z = 6 a 10. O terreno vai de x = -24 a 24 e de z = -18 a 18.
- **Módulos de parede** (pivô no meio da face externa, na cota do piso; 2 m): galpão `m_plain`, `m_win`, `m_door`, `m_chute`, `m_bay` (4 m, portão de correr); escritório `o_plain`, `o_win`, `o_door`. Os finais `_l` e `_r` são os módulos das quinas, encurtados 22 cm no lado esquerdo ou direito.
- **Coberturas e pisos** (pivô na origem, cota do piso): `m_roof`, `m_floor`, `o_roof`, `o_floor`.
- **Peças inteiras** (pivô na origem): `burner`, `conveyor`, `lumber_shed`, `fence`, `site`.
- **Portas** (pivô na dobradiça): `door_plank`, `door_back`.
- **Máquinas e móveis**: `band_saw`, `carriage`, `roller_table`, `edger`, `lumber_cart`, `workbench`, `drum`, `fl_light` (pivô no teto), `desk`, `office_chair`, `guest_chair`, `file_cab`, `wood_stove`.
- **Pátio**: `stack_a`, `stack_b`, `pallet_stack`, `log_pile`, `log_pile_b`, `sawdust_pile`, `loader`, `log_truck`, `yard_light`, `pine`, `pine_b`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`planks` (tábuas, madeira, forro), `render` (concreto, terra, cascalho, chapa enferrujada) e `stone`. Ladrilho de 2 m, UV em metros / 2.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 6 caminhos:
  - da frente, pelo corredor do galpão aberto, entra pelo portão de correr até o carro porta-toras;
  - do pátio, entra pela porta lateral e atravessa o galpão até a parede do outro lado;
  - da frente, sobe o degrau e entra no escritório até a mesa;
  - do pátio até a base do queimador;
  - anda junto da cerca da frente de uma ponta à outra;
  - passa entre o queimador e o caminhão até os pinheiros do fundo.

No visitante, é o prédio 49 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/serraria/gerar_kit.py        # escreve em out/ ao lado do script
python kits/serraria/verificar_flicker.py
```
