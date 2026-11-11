# Mutirão 12 detalhada

A espingarda de bombeamento Mutirão refeita no método da M4A1, igual às submetralhadoras
(`../smg/`, `../ciclone/`): modelada por script no Blender (módulo `bpy`), com recortes de
verdade (janela de ejeção com o ferrolho por trás, janela de carga com o elevador, painéis
rebaixados do receptor, fendas do trilho, protetor de calor furado, vãos entre os anéis da
telha), quinas chanfradas e texturas PBR assadas (cor, oclusão/rugosidade/metal e relevo)
com desgaste nas arestas, sujeira nos cantos, pontilhado no punho e gravações. Desenho
próprio, sem marcas de fabricante; as gravações são em português.

Entra no lugar da `espingarda_12` antiga e da curta (`espingarda_12_curta`), com as mesmas
medidas, os mesmos nós e as mesmas animações (a telha bombeia e leva o ferrolho, o elevador
sobe). O jogo e os acessórios (coronhas retrátil e fixa, choke, freio dentado, prolongador
do tubo, lanterna de cano, porta-cartuchos, laser e empunhadura na telha) continuam valendo
sem mudança.

| Arquivo | O que é |
| --- | --- |
| `../armas/espingarda_12.glb` e `espingarda_12_curta.glb` | arma do jogo: 9 peças em nós próprios, 2 conjuntos de textura 2048 px (A: receptor, alojamento do gatilho e punho; B: cano, tubo, protetor, telha, ferrolho, elevador, tampa, gatilho) |
| `../armas/espingarda_12_leve.glb` e `espingarda_12_curta_leve.glb` | versão leve para ver de longe ou no chão: uma malha só, cerca de 6 mil triângulos, 1 conjunto de textura 1024 px (campo `arquivo_leve` do catálogo) |

A curta não é só outra cor: `VARIANTE=curta` muda as medidas em `modelo.py` (cano, tubo,
protetor e telha menores) e usa `esqueleto_curta.json`; por isso ela tem bake próprio dos
dois grupos.

## Como refazer

```
pip install bpy pillow numpy shapely
python3 gerar.py 2048 saida                          # modelo, UVs e bake (uns 6 min em 4 núcleos)
python3 jogo.py saida                                # GLB do jogo, versão leve e catálogo
VARIANTE=curta python3 gerar.py 2048 saida_curta
VARIANTE=curta python3 jogo.py saida_curta
python3 foto.py saida/mutirao.blend fotos/mutirao esq 34d perto   # renders de conferência
```

- `modelo.py`: as peças, em milímetros (usa as primitivas de `../m4a1/lib.py`).
- `materiais.py`: aço oxidado do cano, aço do ferrolho, anel vermelho da trava e o
  pontilhado do punho, somados aos de `../m4a1/texturas.py`.
- `config.py`: origem, peças de cada nó, variantes (id e descrição).
- `gerar.py` e `jogo.py`: chamam `../m4a1/fabrica.py`.
- `esqueleto.json` e `esqueleto_curta.json`: os nós e as animações das espingardas antigas
  (`../m4a1/tirar_esqueleto.py`), que garantem que nada muda para o jogo.
- `ver.py`: renders rápidos só da forma, sem textura.
