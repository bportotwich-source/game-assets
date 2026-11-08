# Kit 32: sobrado de reboco com garagem (alto detalhe)

Sobrado de 2 andares em reboco claro, com garagem anexa. Feito no padrão de alto detalhe, com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py), e no [padrão de medidas](../../PADRAO_METRICAS.md). Arte original.

## O conjunto
- **Casa** de 8 × 10 m, com:
  - piso do térreo 0,3 m acima do chão;
  - 2 andares de 3,0 m (laje de 0,2 m);
  - telhado de 2 águas a 40°, com a cumeeira no sentido da profundidade e os frontões para a frente e os fundos.
- **Paredes de reboco** com embasamento de tijolo saliente e capa chanfrada. O embasamento para nas portas.
- **Janelas de batente brancas**:
  - marco, montantes, bandeira e folhas com vidro e puxador;
  - peitoril de pedra com pingadeira;
  - verga de tijolos em espelho.
  - Tipos: comum de 2 folhas, larga de 3 folhas e pequena de banheiro, sem bandeira.
- **Porta da frente**:
  - folha com vidro alto, 3 almofadas, puxador, olho mágico e caixa de correio;
  - vidro lateral com travessas;
  - soleira de pedra e verga de tijolo;
  - marquise de 2 águas com telhas, mísulas, testeira e luminária.
- **Escada de entrada** de pedra sobre corpo de tijolo, e outra igual na porta dos fundos.
- **Telhado**:
  - telhas cerâmicas em fiadas;
  - cumeeira de telhas meia-cana;
  - testeiras nas empenas;
  - beiral com calha e condutores;
  - chaminé de tijolo com cintas e capa de pedra.
- **Frontões**: o da frente tem a janela do sótão, e o dos fundos é liso.
- **Garagem anexa** de 4 × 8 m:
  - portão de 2 folhas de tábuas verticais, com travessas e mão-francesa por dentro, 3 vidros no alto, dobradiças e puxador;
  - frontão próprio com respiro de tijolo;
  - janela e porta lateral;
  - água encostada na casa, com rufo de chapa.
- **Jardim**:
  - gramado e caminho de lajotas até a porta;
  - entrada de carro de concreto;
  - cerca de estacas na frente e cerca de tábuas nos fundos;
  - sebe na lateral, arbustos e latas de lixo.
- **Dentro**:
  - **Térreo**: sala com cozinha de ladrilho nos fundos, hall com a escada e lavanderia com porta para o quintal. Uma porta interna liga o hall à garagem.
  - **Escada** reta de 16 degraus, com armário embaixo.
  - **1º andar**: patamar com guarda-corpo torneado, 2 quartos ligados por porta e banheiro de ladrilho.
  - **Acabamentos**: portas internas almofadadas com guarnição, e rodapés que param nas portas.
  - **Sótão**: fechado, com forro.

Números: 100 peças, 218 posições, 12 portas, cerca de 82 mil triângulos no montado.

## Montagem
A casa vai de x = -4 a 4 e de z = -5 a 5, com a frente para +Z. A garagem vai de x = 4 a 8 e de z = -3 a 5. O piso do térreo fica em 0,3, o do 1º andar em 3,3 e o beiral em 6,3. O piso da garagem fica em 0,05 e o beiral dela em 2,75.
- **Paredes da casa** (módulos de 2 m, pivô na face externa, na cota do piso):
  - `w_g_*` são as do térreo e `w_u_*` as do 1º andar.
  - Tipos: `plain`, `win`, `wide`, `small`, `door` (porta da frente), `bdoor` (porta dos fundos) e `din` (porta para a garagem).
- **Quinas**: `corner_g`, `corner_u` e `gcorner` (garagem), com pivô na quina externa.
- **Frontões**: `gable_front` e `gable_back`, com pivô no eixo, na cota do beiral.
- **Chaminé**: `chimney`.
- **Telhado** (pivô na cota do beiral):
  - `roof_eave*` são as águas da casa e `groof_*` as da garagem; `_a` e `_b` são as pontas, com testeira.
  - `ridge` e `gridge` são as cumeeiras.
  - `abutment` é o rufo onde a água da garagem encosta na casa.
  - `downspout` e `gdownspout` são os condutores.
- **Garagem**:
  - `garage_front` é a frente com o vão e o frontão, e `garage_back` o fundo;
  - `garage_leaf` é a folha do portão;
  - `gw_*` são as paredes laterais;
  - `garage_steps` é o degrau da porta interna.
- **Portas**: `door_leaf_front`, `door_leaf_back` e `door_leaf_interior`.
- **Escadas de fora**: `front_steps`, `back_steps` e `canopy`.
- **Interior**:
  - `iw_*` são as paredes internas de 2 m.
  - `rw_bed`, `rw_bath` e `rw_util` são as paredes de comprimento livre.
  - `stair` sobe para -Z. O vão na laje está em `building_layout.json` (`stair_holes`).
  - `rail_*` são os guarda-corpos.
- **Pisos**: `floor_<tipo>_<g|u|c>` são as placas de 2 × 2 m (g = térreo, u = 1º andar, c = forro do sótão). `_e…` marca o recuo em cm de cada lado (x-, x+, z-, z+), e `_h#` tem vão de escada.
- **Jardim**: `lawn_*`, `path`, `drive`, `picket`, `board_fence`, `hedge`, `bush` e `bin`.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render`, `brick`, `cill`, `shingles` (telha cerâmica), `floor`, `plaster`, `concrete`, `paving`, `fencew`, `attic` e `gdoor`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3, 12 caminhos:
  - o jogador entra pela porta da frente e atravessa o hall, e vai do hall para a sala;
  - sobe a escada até o 1º andar (3,3 m), entra nos 2 quartos (inclusive pela porta entre eles) e no banheiro;
  - entra pela porta dos fundos na lavanderia e passa dela para o hall;
  - vai do hall para a garagem pela porta interna;
  - entra na garagem pelo portão e pela porta lateral.

No visitante, é o prédio 32 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d networkx bpy
python kits/casa-reboco/gerar_kit.py        # escreve em out/ ao lado do script
python kits/casa-reboco/verificar_flicker.py
```
