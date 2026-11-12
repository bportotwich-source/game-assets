# Arremessáveis (coquetel molotov, bomba de pregos, isca sonora)

Os três arremessáveis do jogo refeitos no nível de detalhe da M4A1, com desenho próprio e sem marcas.
Mesmos ids, nós e animações dos antigos, então o jogo usa sem mudar nada.

| id | o que é | nós que mexem |
|---|---|---|
| `coquetel_molotov` | garrafa de vidro verde transparente com combustível dentro, rótulo velho, pano no gargalo amarrado com barbante | `pavio` (com `chama`), `quebra` |
| `bomba_pregos` | lata com pregos presos por duas voltas de fita, fita em cruz na tampa e pavio verde | `pavio` (com `chama`) |
| `isca_sonora` | despertador de corda com duas campainhas, vidro transparente, chave de corda atrás | `ponteiro_horas`, `ponteiro_minutos`, `ponteiro_alarme`, `martelo`, `som` |

## Gerar

```
python3 gerar.py <id> 1024 saida/<id>      # modelo, UVs e bake
python3 jogo.py <id> saida/<id>            # armas/<id>.glb, armas/<id>_leve.glb e catálogo
python3 ver.py <função de modelo.py> /tmp/r   # renders só da forma
```

Mudou o modelo ou as classes de material: apague a pasta de saída antes.

## Notas

- O vidro da garrafa e o do relógio são peças separadas (`vidro`) de material liso transparente
  (`lisos` em config.py); o do relógio fica fora da versão leve (`fora_leve`), para não tapar o mostrador.
- A peça principal de cada modelo não pode ter o nome do id (a fábrica dá esse nome ao nó raiz):
  por isso `rotulo`, `lata` e `caixa`.
- A garrafa tem um rebaixo de 1,4 mm onde vai o rótulo; papel colado rente ao vidro assa manchado.
