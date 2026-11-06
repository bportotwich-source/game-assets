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

## Regenerar um kit
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut
python kits/predio-mansarda/gerar_kit.py      # escreve em out/ ao lado do script
python kits/predio-mansarda/verificar_flicker.py
```
