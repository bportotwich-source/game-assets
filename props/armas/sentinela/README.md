# Sentinela 9 mm detalhada

A pistola Sentinela refeita no método da M4A1, igual à Guardiã (`../guardia/`): modelada por
script no Blender (módulo `bpy`), com recortes de verdade (serrilhas, janela de ejeção,
rebaixo da mira com tampa parafusada, fendas do trilho, cavas dos dedos), quinas chanfradas
e texturas PBR assadas (cor, oclusão/rugosidade/metal e relevo) com desgaste nas arestas,
sujeira nos cantos, pontilhado no punho e gravações. Desenho próprio, sem marcas de
fabricante; as gravações são em português.

Entra no lugar da `pistola_9mm` antiga e das três cores (`_tan`, `_verde`, `_cinza`), com as
mesmas medidas, os mesmos nós e as mesmas animações. O jogo e os acessórios (mira de
ferrolho, ponte de mira, supressores, lanterna de trilho, carregadores) continuam valendo
sem mudança.

| Arquivo | O que é |
| --- | --- |
| `../armas/pistola_9mm.glb` (e `_tan`, `_verde`, `_cinza`) | arma do jogo: 14 peças em nós próprios, 2 conjuntos de textura 2048 px (A: armação, punho, gatilho, carregador, cano; B: ferrolho, miras, alavancas) |
| `../armas/pistola_9mm_leve.glb` (e as cores) | versão leve para ver de longe ou no chão: uma malha só, cerca de 6 mil triângulos, 1 conjunto de textura 1024 px (campo `arquivo_leve` do catálogo) |

As cores são o mesmo modelo com outro bake: muda o polímero da armação e o cano fica
dourado, como na Sentinela antiga.

## Como refazer

```
pip install bpy pillow numpy shapely
python3 gerar.py 2048 saida                    # modelo, UVs e bake (uns 6 min em 4 núcleos)
python3 jogo.py saida                          # GLB do jogo, versão leve e catálogo
VARIANTE=tan python3 gerar.py 2048 saida_tan   # idem para verde e cinza
VARIANTE=tan python3 jogo.py saida_tan
python3 foto.py saida/sentinela.blend fotos/sentinela esq 34d perto   # renders de conferência
```

- `modelo.py`: as peças, em milímetros (usa as primitivas de `../m4a1/lib.py`).
- `materiais.py`: aço nitretado do ferrolho, polímero da armação (cor por `VARIANTE`), aço do
  cano e o pontilhado do punho, somados aos de `../m4a1/texturas.py`.
- `config.py`: origem, peças de cada nó, variantes (id e descrição).
- `gerar.py` e `jogo.py`: chamam `../m4a1/fabrica.py`.
- `esqueleto.json`: os nós e as animações da Sentinela antiga
  (`../m4a1/tirar_esqueleto.py`), que garantem que nada muda para o jogo.
- `ver.py`: renders rápidos só da forma, sem textura.
