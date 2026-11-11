# Arco composto (refeito no nível da M4A1)

O arco composto do jogo, no id `arco_composto`, com os mesmos nós (braços, polias, metades da corda,
cabos, laço D, visor, apoio, flecha), encaixes (mira de pinos com luz, soltador, estabilizador, aljava)
e animações do antigo (`arma16_composto.py`). Desenho próprio, sem marcas de fabricante.

Punho de alumínio anodizado grafite, usinado em treliça (duas longarinas com almas em zigue-zague) e
com filetes laranja; janela de mira, pega de polímero pontilhada, buchas de latão. Bolsos de alumínio
preto com eixo e parafuso de tensão recartilhado; braços divididos de fibra com faixa de carbono,
casquilhos e amortecedores de borracha. Polias excêntricas vazadas, com trilha da corda, módulo
laranja dos cabos e pino de parada. Corda e cabos torcidos com reforços e silenciadores; protetor de
cabos com haste de carbono e deslizador; batente da corda com ponta de borracha; apoio de flecha que
cai; visor na corda; laço D. Flecha fina de carbono com penas verdes e ponta de caça vazada.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é o arco com a flecha |
| `materiais.py` | alumínio grafite e laranja, pega pontilhada, cabos (usa as classes de `../recurvo`) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura) |
| `esqueleto.json` | nós e animações tirados do arco antigo |

O punho e a pega são o grupo de textura A; braços, polias, corda, cabos, visor, apoio e flecha são o B.

Números: 52.667 triângulos e 2 conjuntos 2048. Versão leve com 6.000 e 1 conjunto 1024.

## O que não mudou (as animações dependem disso)

- Eixo dos bolsos e das polias, raio da trilha da corda (45 mm) e do módulo dos cabos (26 mm).
- Ponto de encaixe da flecha, posição do deslizador dos cabos, do visor e do eixo do apoio.

## O que mudou de propósito

- O punho deixou de ser uma barra com dois rasgos e virou treliça usinada.
- A pega ficou mais fina (44 mm de fundo no lugar de 48).
- A janela de mira passa do meio do arco, para a flecha ficar no plano da corda.

Ainda antigos: as flechas soltas (`municao/flecha_carbono*`), a mira de pinos com luz, o soltador de
pulso, os estabilizadores e a aljava.
