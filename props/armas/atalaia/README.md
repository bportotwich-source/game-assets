# Fuzil Atalaia .308 de precisão (refeito no nível da M4A1)

O fuzil semiautomático .308 do jogo, nos ids `fuzil_308_precisao` (cano longo) e
`fuzil_308_precisao_curto`, com os mesmos nós, encaixes e animações do antigo
(`arma13_precisao.py`). Receptores, ferrolho, alavanca, controles e punho são as peças da M4A1
(`../m4a1/modelo.py`) aumentadas 10 % (o fuzil .308 é maior que o 5,56 em tudo) e pintadas de
verde-oliva. São peças próprias, em `montagem.py`: o guarda-mão octogonal com trilho contínuo e
duas fileiras de fendas, o cano pesado com rosca na boca e o carregador de caixa de 20.

| Arquivo | Para quê |
|---|---|
| `montagem.py` | escolhe, aumenta e desloca as peças da M4A1 (158 mm para a frente) e faz as peças próprias |
| `materiais.py` | as classes verde-oliva e o quadriculado do punho no lugar novo |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós (com os que mudaram de lugar), origem, ids |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto*.json` | nós e animações tirados dos dois fuzis antigos |

Para o curto: `VARIANTE=curto` nos dois comandos. O grupo de textura A (receptores, controles,
punho) é igual nos dois: copie `atalaia_A_*` da saída do longo para a pasta `tex/` do curto com o
nome `atalaia_curto_A_*` e só o grupo B (cano, guarda-mão, carregador) é assado.

Números: 26.158 triângulos o longo e 23.774 o curto, 2 conjuntos 2048. Com a coronha de precisão
(20.888), a luneta 5-25× (6.528), as miras rebatíveis e o freio de boca antigos são cerca de
56,5 mil na mão. Versão leve com 6.000 e 1 conjunto 1024.

## O que mudou de propósito

- O punho e o gatilho ficam onde estavam; o receptor termina 37 mm mais atrás e o trilho fica
  6,5 mm mais alto. Os nós `encaixe_mira`, `encaixe_alca`, `mira_ferro`, `encaixe_massa`,
  `encaixe_coronha`, `saida_estojo`, `carregador`, `gatilho`, `seletor`, `tampa_janela` e
  `retem_ferrolho` foram para o lugar das peças novas (`config.py`).
- A boca, o fim do guarda-mão e os encaixes de lanterna, laser, bipé e empunhadura não mudaram.
- A gravação do seletor só tem SEGURO e SEMI.
- A coronha de precisão, a luneta 5-25×, as miras rebatíveis e o freio de boca continuam sendo os
  acessórios antigos.
- `../m4a1/texturas.py` passou a aceitar a classe `verde_grip` no quadriculado do punho.
