# Fuzil Vigília 5,56 (refeito no nível da M4A1)

O fuzil 5,56 do jogo, nos ids `fuzil_556` (preto) e `fuzil_556_bicolor` (guarda-mão, punho, carregador e coronha cor de
caramelo, receptores e cano pretos), com os mesmos nós, encaixes e animações do antigo
(`arma01_fuzil.py`). Não tem modelo próprio: é a M4A1 (`../m4a1/modelo.py`) em outra configuração,
com cano de 16", guarda-mão longo sem trilhos de baixo e de lado, carregador de polímero e gravação
própria. A coronha retrátil sai como acessório (`coronha_retratil_ar` e `coronha_retratil_ar_tan`).

| Arquivo | Para quê |
|---|---|
| `montagem.py` | escolhe e desloca as peças da M4A1 (145 mm para a frente, a origem do fuzil antigo) |
| `materiais.py` | as classes cor de areia e o quadriculado do punho no lugar novo |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, ids (arma e coronha) |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida`; `... 1024 saida_cor coronha` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida`; `... saida_cor coronha` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto*.json` | nós e animações tirados do fuzil e da coronha antigos |

Para o bicolor: `VARIANTE=bicolor` nos dois comandos. Para a coronha cor de areia: `VARIANTE=tan`.
Gere as coronhas antes das armas (o `ref_coronha` da arma sai do acessório).

## O que mudou de propósito

- O trilho de cima fica 6,5 mm mais alto e a rosca da boca termina em u=504, como na M4A1; os nós
  `encaixe_*`, `mira_ferro` e `boca_fogo` foram ajustados para isso.
- As miras dobráveis, o quebra-chamas, as lunetas e as empunhaduras continuam sendo os acessórios
  antigos.
