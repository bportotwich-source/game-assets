# Faísca 9 mm detalhada

A submetralhadora Faísca refeita no método da M4A1, igual às pistolas (`../guardia/`,
`../sentinela/`): modelada por script no Blender (módulo `bpy`), com recortes de verdade
(janela de ejeção com o ferrolho por trás, fendas de ventilação e de fixação, fendas dos
trilhos, estrias de pega, poço do carregador), quinas chanfradas e texturas PBR assadas
(cor, oclusão/rugosidade/metal e relevo) com desgaste nas arestas, sujeira nos cantos,
pontilhado no punho e gravações. Desenho próprio, sem marcas de fabricante; as gravações
são em português.

Entra no lugar da `smg_9mm` antiga e da caramelo (`smg_9mm_tan`), com as mesmas medidas, os
mesmos nós e as mesmas animações (coronha que estende, alavanca em T, seletor). O jogo e os
acessórios (alça e massa rebatíveis, miras, supressores, empunhadura dobrável, lanterna,
laser, carregadores de 20, 30 e 40) continuam valendo sem mudança.

| Arquivo | O que é |
| --- | --- |
| `../armas/smg_9mm.glb` e `smg_9mm_tan.glb` | arma do jogo: 11 peças em nós próprios, 2 conjuntos de textura 2048 px (A: corpo, punho e soleira; B: trilhos, cano, ferrolho, alavanca, seletor, gatilho, varetas, carregador) |
| `../armas/smg_9mm_leve.glb` e `smg_9mm_tan_leve.glb` | versão leve para ver de longe ou no chão: uma malha só, cerca de 6 mil triângulos, 1 conjunto de textura 1024 px (campo `arquivo_leve` do catálogo) |

A caramelo é o mesmo modelo com outro bake do grupo A: corpo, punho e soleira caramelo;
carregador e trilhos pretos, como na Faísca antiga. O grupo B é o mesmo arquivo nas duas.

## Como refazer

```
pip install bpy pillow numpy shapely
python3 gerar.py 2048 saida                    # modelo, UVs e bake (uns 6 min em 4 núcleos)
python3 jogo.py saida                          # GLB do jogo, versão leve e catálogo
mkdir -p saida_tan/tex && cp saida/tex/faisca_B_* saida_tan/tex/    # o grupo B não muda
VARIANTE=tan python3 gerar.py 2048 saida_tan
VARIANTE=tan python3 jogo.py saida_tan
python3 foto.py saida/faisca.blend fotos/faisca esq 34d perto   # renders de conferência
```

- `modelo.py`: as peças, em milímetros (usa as primitivas de `../m4a1/lib.py`).
- `materiais.py`: polímero do corpo (cor por `VARIANTE`), aço do cano e do ferrolho e o
  pontilhado do punho, somados aos de `../m4a1/texturas.py`.
- `config.py`: origem, peças de cada nó, variantes (id e descrição).
- `gerar.py` e `jogo.py`: chamam `../m4a1/fabrica.py`.
- `esqueleto.json`: os nós e as animações da Faísca antiga (`../m4a1/tirar_esqueleto.py`),
  que garantem que nada muda para o jogo.
- `ver.py`: renders rápidos só da forma, sem textura.
