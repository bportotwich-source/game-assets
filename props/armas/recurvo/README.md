# Arco recurvo (refeito no nível da M4A1)

O arco recurvo do jogo, no id `arco_recurvo`, com os mesmos nós (braços, metades da corda, flecha),
encaixes (mira de pinos, estabilizador, aljava) e animações do antigo (`arma15_arco.py`). Desenho
próprio, sem marcas de fabricante.

Punho de madeira laminada esculpido, com folhas empilhadas de frente para trás e uma faixa de bordo
entre dois filetes pretos; janela de mira que sobe em rampa, prateleira com feltro e placa de couro
onde a flecha encosta; buchas de latão para a mira, a aljava e o estabilizador. Braços de fibra preta
com o miolo de bordo à vista nos cantos, assentados na frente do punho e presos por manípulos
recartilhados; pontas com reforço claro e entalhes para o laço da corda. Corda torcida com reforço no
meio e anel de latão. Flecha de carbono com 3 penas de plástico (uma branca), entalhe laranja e ponta
de caça de 3 lâminas vazadas. Gravações: tamanho e força no punho e nos braços, número de série.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é o arco com a flecha |
| `materiais.py` | laminado do punho, fibra, bordo, corda torcida, penas |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | nós e animações tirados do arco antigo |

O punho e a flecha são o grupo de textura A; os braços e a corda são o B.

Números: 30.638 triângulos e 2 conjuntos 2048. Versão leve com 6.000 e 1 conjunto 1024.

## O que não mudou (as animações dependem disso)

- Eixo dos braços, ponto em que a corda deixa o braço e ponto de encaixe da flecha na corda.
- Linha do meio, largura e espessura dos braços.

## O que mudou de propósito

- Os braços assentam na frente do punho (lado do alvo), presos por manípulo, como num arco
  desmontável de verdade; antes entravam num bolso de aço.
- O punho ficou mais fino na pega (58 mm de fundo) e sem a faixa de couro.
- A janela de mira passa do meio do arco, para a flecha ficar no plano da corda.

Ainda antigos: as flechas soltas (`municao/flecha_*`), a mira de pinos, os estabilizadores e a aljava.
