# Flechas e virotes soltos (refeitos no nível da M4A1)

A munição dos arcos e da besta em `../municao/`: `flecha_caca`, `flecha_campo`, `flecha_prego`,
`flecha_carbono`, `flecha_carbono_campo`, `virote_caca`, `virote_campo` e `virote_prego`. São as
flechas modeladas com os arcos refeitos, uma por id, com a origem no entalhe e os mesmos
comprimentos das antigas. Pontas: caça (3 lâminas vazadas), campo (ogiva) e prego amarrado com fita.

`modelo.py` tem a tabela `SPECS`; `python3 gerar.py <id> 512 saida && python3 jogo.py <id> saida`.
A fábrica grava em `municao/` por causa de `grupo='municao'` em `config.py`.
