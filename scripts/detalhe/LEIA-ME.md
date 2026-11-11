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

## Correções de montagem (`montagem.py`)

Roda direto nos GLB das peças de um kit, depois de gerar: `python3 scripts/detalhe/montagem.py kits/<kit>`. Rodar de novo não muda nada.

- **Teto sem sulcos.** O corpo da laje é recuado 2 cm de cada lado para não piscar com as paredes, e isso deixava um sulco de 4 cm no teto a cada módulo. O script estende a face de baixo do corpo até a borda do piso (vale para lajes comuns e para a laje do núcleo de escada).
- **Batente sob a folha da janela.** Fecha a fresta de 1 a 2 cm entre o peitoril e a folha com uma ripa fina: por dentro na guilhotina, por fora na folha de abrir. O nó `folha` não muda.
- **Folha de porta na altura do vão.** `python3 scripts/detalhe/montagem.py --porta <folha.glb> <altura>` estica a folha até a altura pedida.

O `building_assembled.glb` (prévia do prédio inteiro) não é refeito por este script.

## Folhas de porta lisas (`portas.py`)

`python3 scripts/detalhe/portas.py kits/<kit>/pieces/door_leaf_x.glb` troca uma folha que era só uma caixa por uma folha com almofadas em relevo, maçaneta e dobradiças, com a mesma largura, altura, pivô e materiais. Folha que já tem relevo é pulada. Já aplicado no diner, no posto e na porta de aço do supermercado; se o `gerar_kit.py` desses kits rodar de novo, rode o script outra vez.

## Quinas arredondadas (`quinas.py`)

`python3 scripts/detalhe/quinas.py kits/<kit>` arredonda as arestas em pé, de fora, a 90 graus (alvenaria 10 mm, madeira 4 mm; um chanfro só, com normais de arco, que sombreia como redondo), direto nos GLB das peças. Uma aresta só muda se estiver à mostra em todos os lugares onde a peça aparece no `building_layout.json`; emenda entre módulos fica viva. Nós, materiais e UV são mantidos e o nó `molduras` não é tocado. `--so-contar` só lista. Precisa de `bpy` e `rtree`. Já aplicado nos 13 kits do jogo.
