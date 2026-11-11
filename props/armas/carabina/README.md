# Carabina Paciência .308 (refeita no nível da M4A1)

A carabina de ferrolho do jogo, nos ids `carabina_308` (chassi cor de areia) e `carabina_308_caca`
(coronha de nogueira), com os mesmos nós, encaixes e animações da antiga (`arma04_carabina.py`).

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`); `VARIANTE=caca` troca a montagem |
| `materiais.py` | classes de material, pontilhado do punho e quadriculado da nogueira |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, ids |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` (uns 6 min) |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto*.json` | nós e animações tirados da carabina antiga |

Para a de caça: `VARIANTE=caca python3 gerar.py 2048 saida_caca` e `VARIANTE=caca python3 jogo.py saida_caca`.

## Números

| id | triângulos (antes) | leve | texturas |
|---|---|---|---|
| `carabina_308` | 55.544 (59.026) | 6.000 | 2 conjuntos 2048, leve 1 de 1024 |
| `carabina_308_caca` | 36.756 (46.672) | 6.000 | 2 conjuntos 2048, leve 1 de 1024 |

## O que mudou de propósito

- A coronha fica abaixo do caminho do ferrolho e o pente (ou o apoio de rosto) começa atrás dele.
  Na antiga o ferrolho aberto atravessava a coronha.
- As duas vêm com luneta por padrão (acessórios antigos), então não há mira de ferro: o jogo mira
  pelo nó `olho` da luneta.
