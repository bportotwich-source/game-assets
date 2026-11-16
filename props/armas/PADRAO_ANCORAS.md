# Padrão de âncoras das armas (versão 1)

Toda arma do pacote segue este padrão para que as mãos, os dedos e os braços do personagem peguem nela do mesmo jeito,
em 1ª pessoa e de fora. Os pontos são nós vazios `ref_*` dentro do GLB, gravados por `pontos_ref.py` (que o
`gerar_armas.py` chama sozinho) e listados no `catalogo.json` (campo `pontos_ref` de cada arma, bloco `padrao_ancoras`).

```
python props/armas/pontos_ref.py              # grava os pontos de todas as armas e acessórios e confere o padrão
python props/armas/pontos_ref.py fuzil_m4a1   # só algumas
python props/armas/pontos_ref.py --conferir   # só confere (sai com erro se alguma arma estiver fora)
```

## 1. Eixos da arma

| Eixo | Sentido |
|---|---|
| origem | centro do punho, na altura do dedo médio (é onde fica `ref_punho`) |
| −Z | para a boca do cano |
| +X | lado direito de quem segura |
| +Y | para cima |
| unidade | metro, escala real (`PADRAO_METRICAS.md`) |

Cada `ref_*` é um nó com posição **e** orientação. Sem giro, os eixos do nó são os da arma. Só o `ref_punho` gira:
o −Y dele desce ao longo do punho, inclinado para trás pelo ângulo medido na malha (campo `inclinacao_graus`).

Os pontos ficam **presos à peça certa**: o `ref_carregador` é filho do carregador, o `ref_manejo` da alavanca ou do
ferrolho, o `ref_guarda_mao` da espingarda é filho da telha. Assim a mão anda junto quando a animação mexe a peça.
Um acessório montado que traz o seu próprio ponto (empunhadura frontal, coronha trocada, guarda-mão da M4A1) vale no
lugar do da arma.

## 2. Os pontos

| Ponto | Mão | Onde fica | Como a mão pega |
|---|---|---|---|
| `ref_punho` | direita | centro do punho, altura do dedo médio | palma encostada no lado direito do punho; médio, anelar e mínimo fecham em volta do contorno medido; polegar pelo lado esquerdo |
| `ref_gatilho` | direita (indicador) | face da frente do gatilho, no meio da tecla | a polpa da ponta do indicador encosta aqui; o indicador sai reto pelo lado da armação |
| `ref_guarda_mao` | esquerda | fuzis: embaixo do guarda-mão; espingarda de bomba: embaixo da telha; pistola: lado esquerdo do punho | fuzil: mão em **U** embaixo do guarda-mão (os dedos encostam dos lados, não fecham por cima); empunhadura vertical: mão fechada nela; pistola: fechada por fora dos dedos da direita |
| `ref_coronha` | ombro direito | centro da soleira da coronha montada | a soleira encosta no ombro |
| `ref_mira` | olho | centro da alça da mira aberta (com luneta ou ponto vermelho vale o nó `olho` do acessório) | mirando, fica no centro da tela |
| `ref_cano` | — | boca do cano | origem do tiro e do clarão |
| `ref_carregador` | esquerda | onde a mão pega o carregador (ou o tambor, a entrada de cartuchos, o virote) | palma do lado esquerdo do carregador, dedos para a frente |
| `ref_manejo` | a do catálogo | onde a mão pega a peça que alimenta a arma | ver o jeito abaixo |
| `ref_corda` | direita | arco e besta: encaixe da flecha na corda | dedos em gancho na corda |

### Jeitos do `ref_manejo`

No catálogo, o ponto traz `mao` (esquerda/direita), `jeito` e `peca`:

| Jeito | Armas | Como |
|---|---|---|
| `lado` | alavanca de manejo (M4A1, 5,56, .308 de precisão, SMG), manete do ferrolho (AK, AKMN, FAL, carabinas, .22) | mão direita pelo lado direito, vindo de baixo |
| `esquerda` | ferrolho das pistolas, manete esquerda da Ciclone | mão esquerda pelo lado esquerdo, atrás |
| `baixo` | telha da espingarda | mão esquerda por baixo, palma para cima |
| `polegar` | cão do revólver e da sinalizadora | o polegar direito puxa o cão; a mão continua no punho |

## 3. Pontos obrigatórios por tipo

| Grupo | Categorias | Pontos |
|---|---|---|
| ombro | fuzil, carabina, rifle, submetralhadora, espingarda | punho, gatilho, guarda_mao, coronha (se tiver coronha), mira, cano, carregador, manejo |
| mão | pistola, revólver | punho, gatilho, guarda_mao, mira, cano, carregador, manejo |
| besta | besta | punho, gatilho, guarda_mao, coronha, mira, cano, carregador |
| arco | arco | punho (mão esquerda), corda, mira, cano |
| duas mãos | lança, bastão | punho, guarda_mao |
| uma mão | faca, facão, machadinha, arremessáveis | punho |

## 4. Regras de geometria (o que `--conferir` mede)

| Regra | Limite |
|---|---|
| `ref_punho` na origem | < 2 mm |
| ângulo do punho | 3° a 40° |
| `ref_gatilho` à frente do punho | 0,5 a 8,5 cm |
| `ref_gatilho` de altura | −0,5 a 7 cm |
| `ref_gatilho` até o meio do punho (alcance do indicador) | ≤ 10,5 cm |
| `ref_gatilho` no meio | ≤ 6 mm para os lados |
| apoio à frente do gatilho (armas de ombro) | ≥ 6 cm |
| apoio até o punho (o braço alcança) | ≤ 55 cm |
| apoio da pistola | lado esquerdo do punho, ≤ 5 cm para a frente ou para trás |
| `ref_coronha` atrás do punho | ≥ 10 cm, ≤ 2 cm para os lados |
| `ref_mira` acima do punho e no meio | ≥ 1,5 cm acima, ≤ 6 mm para os lados |
| boca do cano | à frente da mira |
| `ref_manejo` até o punho | ≤ 45 cm, com mão e jeito no catálogo |

## 5. Mãos, dedos e braços no jogo (1ª pessoa)

O jogo mede as mãos em cima destes pontos com `jogo/testes/verificar_padrao_maos.tscn` (Recomeço), e o app de
animações tem o mesmo verificador (tecla Shift+P). Os limites ficam em `jogo/dados/padrao_maos.json`:

| Medida | Limite | Estados |
|---|---|---|
| osso da mão até o alvo do IK | ≤ 1,5 cm | pronta, mirando |
| meio da palma direita até `ref_punho` | ≤ 5 cm | pronta, mirando |
| ponta do indicador até `ref_gatilho` | ≤ 2 cm | pronta, mirando |
| meio da palma esquerda até `ref_guarda_mao` | ≤ 5,5 cm | pronta, mirando |
| palma até `ref_manejo` no exame (X) | ≤ 5,5 cm | exame |
| palma esquerda até `ref_carregador` na recarga (R) | ≤ 6 cm | recarga |
| dedo ou palma dentro da malha | ≤ 4 mm | pronta, mirando |
| ângulo do cotovelo | 35° a 177° | todos |
| cotovelo para cima | ≤ 0,35 | pronta |
| dobra do pulso | ≤ 65° | todos |
| braço dentro do tronco | ≤ 1,5 cm | todos |
| mãos na tela | ≥ 1 | pronta |
| linha de visada no centro da tela | ≤ 3% da altura | mirando |
| arma longe do olho | ≥ 7 cm | mirando |

## 6. Arma nova

1. Modele com a origem no centro do punho e o cano para −Z.
2. Dê nome às peças que mexem: `gatilho`, `carregador` (ou `tambor`, `entrada_cartucho`), `alavanca` ou `ferrolho`
   (ou `telha`, `cao`), `mira_ferro`, `boca_fogo`, e os `encaixe_*`.
3. Rode `python props/armas/pontos_ref.py <id>`. Se a conferência apontar algo, corrija o modelo ou ponha um ajuste
   no dicionário `AJUSTE` do `pontos_ref.py` (posição `d` ou `inclinacao` do punho).
4. No Recomeço, rode o verificador com `ids=<id>` e olhe as fotos.
