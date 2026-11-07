# Kit modular: prédio de apartamentos de tijolos

Prédio residencial em peças 3D (GLB) no estilo toon com contorno. Segue o [padrão de medidas](../../PADRAO_METRICAS.md) comum a todos os prédios do pacote.

## O prédio de exemplo
- Planta de 16 × 10 m: térreo com portaria, depósito e lavanderia (só a estrutura, sem móveis nem adereços de rua), mais 3 andares de apartamentos.
- 2 apartamentos por andar (6 no total), espelhados. Cada um tem sala com cozinha e varanda, quarto de casal, quarto de solteiro/escritório, banheiro e circulação.
- Escada interna em U no núcleo central, do térreo até a casinha do terraço.
- Escada de incêndio usável na lateral direita, do chão ao terraço, com uma porta por andar.

## Grade
Módulo de parede 2 m; andar 3 m; térreo 3,2 m; parede externa 0,3 m; interna 0,12 m; laje 0,2 m. Eixo Y para cima, 1 unidade = 1 m.

## Pivôs
- Paredes externas, cornijas, sacadas, escada de incêndio: centro inferior da face externa, fachada para +Z.
- Paredes internas: centro inferior, espessura centrada na linha da grade.
- Folhas de porta: na dobradiça.
- Lajes, telhado, caixa d'água: centro da base.
- Escada em U: centro da borda aberta do núcleo, na cota do andar de baixo.

## Texturas
Embutidas nos GLB, com UVs projetadas em metros, então continuam sem emenda entre módulos vizinhos.
- `brick` (`brick_texture.png`): bloco de 1×1 m, 8 fiadas de 0,125 m, tijolos de 0,25 m em amarração corrida. Fachada dos andares.
- `stone` (`stone_texture.png`): bloco de 1×0,8 m, blocos de pedra de 1,0×0,4 m em amarração corrida (8 fiadas no térreo de 3,2 m). Térreo, peitoris de pedra, degrau.
- `plaster` (`plaster_texture.png`): reboco fosco de 1×1 m, sem repetição visível. Paredes internas e faces internas das externas; faces horizontais ficam em cor lisa.

## Peças (38)
| Grupo | Peças |
|---|---|
| Fachada térreo | `wall_ground_window`, `wall_ground_door`, `corner_ground` |
| Fachada andares | `wall_brick_window`, `wall_brick_balcony_door`, `wall_brick_plain`, `corner_brick`, `balcony` |
| Topo | `cornice_parapet`, `cornice_parapet_corner`, `cornice_parapet_opening`, `roof_tile`, `roof_stair_core_192_192_29`, `roof_stair_hut`, `water_tower` |
| Pisos e escada | `floor_tile`, `floor_tile_bath`, `stair_core_slab_192_192_29`, `stair_core_rail`, `stairs_u_3m_192_192`, `stairs_u_3m2_192_192` |
| Paredes internas | `interior_wall_plain`, `interior_wall_doorway`, `interior_wall_end` (1,7 m, termina na face interna da parede externa) e as versões `_ground` (3,0 m) |
| Portas | `door_leaf_entrance`, `door_leaf_interior`, `door_leaf_balcony`, `door_leaf_hut` |
| Escada de incêndio | `fire_escape_landing_a`, `fire_escape_landing_b`, `fire_escape_flight_a`, `fire_escape_flight_b`, `fire_escape_flight_ground` (zigue-zague: uma plataforma de 6 × 2 m por andar, com abertura para o lance que chega; os lances alternam de lado a cada andar) |
| Entrada | `entrance_canopy` |
| Referência | `player_scale_ref` (cápsula de 1,8 m, não vai no jogo) |

As escadas vão de parede a parede da caixa de 4 m. Nos nomes, `_192_168` é a distância em cm do centro da caixa até a face da parede à esquerda e à direita; nas lajes, o último número é a faixa de laje atrás do patamar.

## Portas
- 43 portas com folha: internas, entrada, sacadas e casinha do terraço.
- Em `building_layout.json`, cada folha tem a tag `door` e o campo `door: {closed, open}` (ângulos em graus, giro em Y na dobradiça).
- Scripts prontos para abrir e fechar em `../../scripts/` (Godot 4: `door.gd`, `interactor.gd`; Unity: `KitDoor.cs`, `DoorInteractor.cs`).

## Visual contínuo
- Paredes geradas como malha fechada em grade (sem frestas nem junções em T), então módulos vizinhos se encostam sem fenda.
- Use contorno em tela (pós-processo por profundidade e normal) ou casco invertido na engine. Contorno por aresta de cada malha desenha as emendas entre módulos.

## Arquivos
- `pieces/*.glb`: as peças.
- `building_layout.json`: as 596 colocações do prédio de exemplo, com tags (`floor0`–`floor3`, `roof`, `front`, `ext`, `fire_escape`) para mostrar ou esconder partes.
- `building_assembled.glb`: o prédio inteiro numa malha.
- `gerar_kit.py`: gera tudo (Python + trimesh + shapely). As funções `wl()` montam paredes internas sobre a grade; mude a planta ali.
