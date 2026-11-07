# game-assets

Pacote de assets 3D modulares e originais para montar cenários de jogos. As peças são GLB no estilo toon com contorno preto, na escala real do jogador (1 unidade = 1 m, Y para cima), e todos os prédios dá para entrar.

## Estrutura
| Pasta | Conteúdo |
|---|---|
| [`PADRAO_METRICAS.md`](PADRAO_METRICAS.md) | Padrão de medidas comum a todos os kits: jogador, módulo de 2 m, andares, portas, corredores, escadas e regras contra flicker |
| [`kits/predio-tijolos/`](kits/predio-tijolos/) | Prédio de tijolos de 16 × 10 m: térreo + 3 andares, 2 apartamentos por andar, escada de incêndio usável (38 peças) |
| [`kits/predio-mansarda/`](kits/predio-mansarda/) | Duas casas geminadas de pedra de 18 × 12 m, com mansarda, lucarnas e sótão habitável (41 peças) |
| [`kits/padaria/`](kits/padaria/) | Padaria de 12 × 10 m: loja e café com toldo e letreiro, produção com forno de alvenaria, apoio no 1º andar e sótão sob telhado de duas águas (45 peças) |
| [`kits/casa-enxaimel/`](kits/casa-enxaimel/) | Casa enxaimel de 10 × 8 m com garagem anexa de 4 × 8 m: térreo de pedra, 1º andar em enxaimel, 3 quartos, sótão com 2 lucarnas e portão duplo (49 peças) |
| [`kits/torre-escalonada/`](kits/torre-escalonada/) | Torre residencial de 9 andares em 3 recuos (24 × 16, 20 × 12 e 16 × 10 m): lojas no térreo, 4 tipos de apartamento, terraços em cada recuo, elevador e terraço na cobertura (39 peças) |
| [`kits/casa-de-campo/`](kits/casa-de-campo/) | Casa de campo de 14 × 8 m com sótão habitável: tábuas horizontais, base de tijolo, varanda de 12 m, telhado de 50° com 2 lucarnas, lareira e chaminé externa (42 peças) |
| [`kits/bangalo/`](kits/bangalo/) | Bangalô térreo de 14 × 12 m: telhado de quatro águas a 30°, varanda de 10 m com frontão, pilares de tijolo e colunas cônicas, sala com lareira, 2 quartos (44 peças) |
| [`kits/supermercado/`](kits/supermercado/) | Supermercado de 24 × 16 m: tijolo com pilastras, vitrines com toldos, entrada de vidro, salão de vendas, depósito com portas de carga, área de funcionários e cobertura com equipamentos (28 peças) |
| [`kits/galeria/`](kits/galeria/) | Galeria comercial de 24 × 26 m com 3 andares: 30 lojas em volta de um átrio com abóbada de vidro, ponte e escadas rolantes, entrada em pele de vidro com lanterna (41 peças) |
| [`kits/casa-americana/`](kits/casa-americana/) | Casa americana de 8 × 12 m com 2 andares e frente em oitão: tábuas sobrepostas azul-acinzentadas, varanda coberta em toda a frente, chaminé de tijolo do lado de fora e garagem de 4 × 6 m com portão duplo (63 peças) |
| [`kits/duplex/`](kits/duplex/) | Duplex de 16 × 12 m: duas casas espelhadas de 2 andares sob um telhado de duas águas, oitão central sobre as duas garagens, tábuas amarelas, venezianas azul-marinho e cobertura sobre cada porta (42 peças) |
| [`kits/diner/`](kits/diner/) | Diner de aço inox de 20 × 8 m: pontas arredondadas, faixa contínua de janelas, vestíbulo de vidro, letreiro no telhado, salão com piso xadrez, cozinha, depósito e 2 banheiros (25 peças) |
| [`kits/brownstones/`](kits/brownstones/) | Sobrados geminados: três casas de tijolo de 6 × 14 m em fileira, com 3, 2 e 4 andares, térreo de pedra marrom, escadaria alta até o andar nobre, cornijas creme com mísulas e escada em U em cada casa (36 peças) |
| [`kits/quartel-bombeiros/`](kits/quartel-bombeiros/) | Quartel de bombeiros: galpão de tijolo de 16 × 12 m com 3 portões, telhado de metal, mezanino com alojamentos e mastro de descida, e anexo de madeira branca com escritório e cozinha (61 peças) |
| [`visitar/`](visitar/) + `project.godot` | Projeto Godot 4 para andar dentro de qualquer kit em primeira pessoa, com colisão e portas que abrem |
| [`scripts/`](scripts/) | Portas que abrem e fecham: Godot 4 (`godot/`) e Unity (`unity/`) |

Cada kit tem:
- `pieces/*.glb`: as peças soltas.
- `building_layout.json`: a montagem, com posição, rotação, tags e portas.
- `building_assembled.glb`: o prédio montado.
- As texturas.
- `gerar_kit.py`: o gerador em Python (trimesh, shapely, numpy, Pillow).
- `verificar_flicker.py`: o teste de sobreposição.

## Como usar
1. Importe os `.glb` na engine. Godot e Unity (com glTFast) leem direto.
2. Monte o prédio peça por peça seguindo `building_layout.json`, ou use `building_assembled.glb` pronto.
3. Para o visual toon, use contorno em tela (pós-processo por profundidade e normal) ou casco invertido. Contorno por aresta de cada peça desenha as emendas entre os módulos.
4. Para as portas, siga `scripts/LEIA-ME.md`.

## Andar dentro dos prédios (Godot 4)
1. Baixe o repositório e abra a pasta dele no Godot 4.3 ou mais novo (Importar, escolha `project.godot`). A primeira abertura importa todas as peças e leva alguns minutos.
2. Aperte F5. O jogo começa na frente da galeria.
3. Clique para prender o mouse. WASD anda, Shift corre, Espaço pula, E ou clique abre e fecha portas, F liga o voo (Espaço sobe, Q desce), Esc solta o mouse.
4. As teclas [ e ] (ou Page Up e Page Down) trocam de prédio; 1 a 9 e 0 vão direto aos 10 primeiros. Para começar em outro, mude `kit` no nó `Main` de `visitar/main.tscn`.

O prédio é montado na hora a partir do `building_layout.json`, com colisão exata em cada peça. O jogador segue o padrão (cápsula de 1,8 m, olhos a 1,65 m) e passa por soleiras e degraus de até 35 cm sem pular, inclusive nas escadas rolantes.

## Regenerar um kit
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut
python kits/predio-mansarda/gerar_kit.py      # escreve em out/ ao lado do script
python kits/predio-mansarda/verificar_flicker.py
```
