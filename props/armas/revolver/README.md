# Revólver Vigia .38 detalhado

O revólver refeito no método da M4A1 (ver `../guardia/README.md`): tambor com câmaras,
canaletas e entalhes de parada recortados, estrela do extrator com os seis cartuchos, cano
com costela estriada e proteção da vareta, cão de espora, talas de nogueira com veio e
quadriculado no relevo da textura, aço azulado gasto nas arestas. Desenho próprio, sem
marcas de fabricante.

Entra no lugar do `revolver_38` antigo com as mesmas medidas, os mesmos nós (punho, cao,
gatilho, trava, braco, tambor, extrator, encaixes) e as mesmas animações. Tem versão leve
(`../armas/revolver_38_leve.glb`, campo `arquivo_leve`).

```
python3 gerar.py 2048 saida      # modelo, UVs e bake (uns 6 min em 4 núcleos)
python3 jogo.py saida            # GLB do jogo, versão leve e catálogo
python3 foto.py saida/revolver.blend fotos/revolver esq 34d cabo
```

`modelo.py` são as peças, `materiais.py` o aço azulado e a nogueira, `config.py` o que a
fábrica (`../m4a1/fabrica.py`) precisa saber, `esqueleto.json` os nós e animações do antigo.
