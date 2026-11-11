# Ciclone 9 mm detalhada

A submetralhadora Ciclone refeita no método da M4A1, igual à Faísca (`../smg/`): modelada
por script no Blender (módulo `bpy`), com recortes de verdade (guarda-mão oco com fendas
ovais que deixam ver o cano, janela de ejeção com o ferrolho por trás, trilho da alavanca,
fendas dos trilhos, laço do guarda-mato, painel triangular rebaixado, poço do carregador),
quinas chanfradas e texturas PBR assadas (cor, oclusão/rugosidade/metal e relevo) com
desgaste nas arestas, sujeira nos cantos, pontilhado no punho e no painel e gravações.
Desenho próprio, sem marcas de fabricante; as gravações são em português.

Entra no lugar da `smg_ciclone_9mm` antiga e da areia (`smg_ciclone_9mm_tan`), com as mesmas
medidas, os mesmos nós e as mesmas animações (coronha que dobra para a direita, alavanca da
esquerda, seletor de quatro posições). O jogo e os acessórios (alça e massa rebatíveis,
miras, supressores, empunhaduras, lanterna, laser, carregador de 17 e tambor de 50)
continuam valendo sem mudança.

| Arquivo | O que é |
| --- | --- |
| `../armas/smg_ciclone_9mm.glb` e `smg_ciclone_9mm_tan.glb` | arma do jogo: 11 peças em nós próprios, 2 conjuntos de textura 2048 px (A: chassi, punho e coronha; B: corpo de cima, trilhos, cano, ferrolho, alavanca, seletor, gatilho, carregador) |
| `../armas/smg_ciclone_9mm_leve.glb` e `smg_ciclone_9mm_tan_leve.glb` | versão leve para ver de longe ou no chão: uma malha só, cerca de 6 mil triângulos, 1 conjunto de textura 1024 px (campo `arquivo_leve` do catálogo) |

A areia é o mesmo modelo com outro bake do grupo A: chassi, punho e coronha cor de areia;
corpo de cima, trilhos e carregador pretos, como na Ciclone antiga. O grupo B é o mesmo
arquivo nas duas.

## Como refazer

```
pip install bpy pillow numpy shapely
python3 gerar.py 2048 saida                    # modelo, UVs e bake (uns 6 min em 4 núcleos)
python3 jogo.py saida                          # GLB do jogo, versão leve e catálogo
mkdir -p saida_tan/tex && cp saida/tex/ciclone_B_* saida_tan/tex/    # o grupo B não muda
VARIANTE=tan python3 gerar.py 2048 saida_tan
VARIANTE=tan python3 jogo.py saida_tan
python3 foto.py saida/ciclone.blend fotos/ciclone esq 34d perto   # renders de conferência
```

- `modelo.py`: as peças, em milímetros (usa as primitivas de `../m4a1/lib.py`).
- `materiais.py`: polímero do chassi (cor por `VARIANTE`), aço do cano e do ferrolho e o
  pontilhado do punho e do painel, somados aos de `../m4a1/texturas.py`.
- `config.py`: origem, peças de cada nó, variantes (id e descrição).
- `gerar.py` e `jogo.py`: chamam `../m4a1/fabrica.py`.
- `esqueleto.json`: os nós e as animações da Ciclone antiga (`../m4a1/tirar_esqueleto.py`),
  que garantem que nada muda para o jogo.
- `ver.py`: renders rápidos só da forma, sem textura.
