# Miras de ponto, de ferro e de pinos (refeitas no nível da M4A1)

As miras antigas que o jogo monta nas armas, nos mesmos ids, encaixes, nós e animações. Desenho
próprio, sem marcas.

| id | O que é | Nós e animações mantidos |
|---|---|---|
| `mira_reflexa`, `mira_reflexa_gasto` | mira de ponto de corpo baixo, janela redonda num capuz inclinado | `olho` |
| `alca_rebativel`, `massa_rebativel` | miras de ferro que deitam | `lamina`, animação `dobrar` |
| `mira_pinos_luz` | mira de 5 pinos de fibra do arco composto, com luz e nível de bolha | `olho` |

Na reflexa a lente é uma malha separada (`<id>_lente`) de vidro transparente, e o catálogo ganha o
campo `optica` (tipo `ponto`): o jogo acende o ponto vermelho nela. Na mira de pinos o vidro do aro
chama-se `vidro` de propósito (o jogo acenderia um ponto em toda malha `_lente`), e as fibras e a
lâmpada são malhas separadas de material aceso. Essas peças lisas (vidro, fibra) são trocadas pela
fábrica depois do bake: `vidro=[...]` e `lisos={...}` em `config.py`.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`); `GASTO = True` troca os metais pelos bem usados |
| `materiais.py` | metais gastos, laranja anodizado, fibras |
| `config.py` | uma entrada por id para a fábrica (`../m4a1/fabrica.py`) |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py <id> 1024 saida` |
| `jogo.py` | GLB em `../acessorios/` e catálogo: `python3 jogo.py <id> saida` |
| `ver.py` | renders de conferência da forma |
| `esqueleto_<id>.json` | nós e animações tirados das miras antigas |

Números: reflexa 2.090 triângulos, alça 1.100, massa 788, pinos 6.392; 1 conjunto 1024 cada.
