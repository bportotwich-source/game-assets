# Biblioteca de alto detalhe

`detalhe.py` junta as ferramentas do kit piloto (hoje o [kit 7, bangalô](../../kits/bangalo/)) para os kits usarem em vez de copiar código.

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe'))
from detalhe import *
configurar(cores={'siding': (118, 146, 104)}, texturas={'siding': 'siding', 'brick': 'brick', 'plaster': 'plaster'}, out=OUT)
configurar_tabuas(base=0.12, topo=2.72, expo=0.2)   # se o kit tiver tábuas em geometria
configurar_telhado(tv=0.08, bump=0.022, graus=30)    # se tiver telhas em fiadas
```

- Tipos de textura (`texturas`): `siding`, `brick`, `stone`, `stone2`, `shingles`, `roof_tiles`, `plaster`, `render`, `planks`, `deck`, `paint`. Todas PBR (cor + normal + ORM), ladrilho de 2 m, UV em metros / 2.
- Regras que valem para todo kit de alto detalhe:
  - As tábuas em geometria começam em `base` e têm 0,2 m de exposição, a mesma fase da textura `siding`. Guarnições e cimalhas não podem ter a borda de baixo numa linha `base + 0,2·k`, porque aí ficam coplanares com a borda de uma tábua.
  - As tábuas param 1,2 mm antes da ponta do módulo. Assim a ponta delas não fica coplanar com a ponta das molduras.
  - Telhado fino (`tv` de 8 cm): a parede sobe só até a face de baixo da telha, e a testeira cobre a ponta.
  - Depois de exportar, chame `glb_jpeg(arquivo)` em cada GLB.
- Lista completa de funções no topo de `detalhe.py`.
