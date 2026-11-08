# Armas do Recomeço

Armas, acessórios e munição **originais** para o jogo **Recomeço** (`docs/plano-jogo-sobrevivencia.md`), gerados por script
(`gerar_armas.py`, Python + trimesh + booleanos manifold, primitivas de `props/gerar_props.py` e `scripts/detalhe`).
Nenhum modelo copia uma arma comercial: formas, nomes e marcas (Sentinela, Guardião...) são inventados.

As ferramentas que também servem de arma (martelo, pé de cabra, machado, chave inglesa, taco, cano) continuam em `props/loot/`.
Aqui ficam as armas de verdade: divididas em partes, com encaixes para acessórios e animações.

```
props/armas/
  gerar_armas.py          gera tudo:  python props/armas/gerar_armas.py   (ou só alguns ids)
  armaNN_<nome>.py        uma arma e os seus acessórios por arquivo (o gerador carrega todos)
  catalogo.json           dados de jogo de tudo (gerado)      CATALOGO.md  tabelas em português (gerado)
  armas/<id>.glb          armas com partes móveis, encaixes e animações
  acessorios/<id>.glb     miras, supressores, lanternas, carregadores...
  municao/<id>.glb        cartuchos, estojos, caixas
  efeitos/<id>.glb        clarão de boca
  godot/arma.gd           script pronto: monta a arma, põe acessórios, atira, recarrega
```

## Convenções

- Y para cima, 1 unidade = 1 m, medidas reais (o jogador tem 1,8 m, ver `PADRAO_METRICAS.md`).
- **Posição de tiro:** o cano aponta para **-Z** (a frente da câmera no Godot), o lado direito da arma é **+X**.
- **Pivô na empunhadura:** a origem da arma é o centro do punho, na altura do dedo médio. Basta pôr a arma como filha do osso da mão
  (ou de um nó na frente da câmera, em 1ª pessoa).
- **Partes:** cada peça que se mexe é um nó do GLB com origem no eixo (gatilho) ou na posição de repouso (ferrolho, cano, carregador).
  O catálogo diz como cada uma anda: `desliza` (`curso_m`), `gira` (`curso_graus`), `remove` (`direcao`).
- **Encaixes:** nós vazios `encaixe_<tipo>` com a mesma orientação da arma. O acessório entra como **filho do nó, com transformação
  identidade** (o pivô do acessório já é o ponto de encaixe). O `tipo` do encaixe tem que bater com o `encaixe` do acessório;
  `aceita` lista os compatíveis e `padrao` o que vem montado. Encaixes ficam presos à peça certa (a mira de ferrolho anda com o
  ferrolho, o supressor anda com o cano, o carregador trocado anda com a animação de recarga).
- **Pontos de efeito:** `boca_fogo` (clarão e origem do tiro, raycast para -Z), `saida_estojo` (onde nasce o estojo ejetado),
  `mira_ferro` (linha de visada), e nos acessórios `olho` (centro da lente), `feixe` (SpotLight3D da lanterna), `laser`.
- **Trilho padrão do Recomeço:** 21 mm de largura com fendas a cada 10 mm. Lanternas, lasers, empunhaduras e bipés usam o mesmo trilho
  em todas as armas.
- **Animações glTF** embutidas, só das peças da arma (as mãos virão com os personagens). O nó raiz da arma também se mexe (coice,
  giro da recarga, inspeção). No Godot ficam no `AnimationPlayer` da cena importada. Nomes padrão:
  `atirar`, `atirar_ultimo`, `vazia`, `recarregar`, `recarregar_vazia`, `inspecionar`, `ocioso` (e os específicos de cada arma, como
  `engatilhar` e `atirar_armado` do revólver). Cada parte e encaixe traz `explodir_m`, um deslocamento para mostrar a arma desmontada.
- **Materiais com nome** (`aco_oxidado`, `polimero`, `latao`, `aluminio_preto`...) para trocar a cor na engine (ex.: versão bege
  ou inox). Punho pontilhado e recartilhados têm textura PBR própria (cor + normal + ORM).

## Dados de jogo (catalogo.json)

| Campo | O que é |
|---|---|
| `dano` | dano por tiro (zumbi comum tem 100 de vida; cabeça ×2,5) |
| `alcance_m`, `alcance_max_m` | alcance efetivo (depois disso o dano cai) e máximo |
| `capacidade`, `municao` | tiros por carregador e id do cartucho |
| `tiros_por_s`, `modo` | cadência máxima e modo de disparo |
| `recarga_s`, `recarga_vazia_s` | tempo de recarga (bate com a animação) |
| `precisao`, `recuo` | de 0 a 1 |
| `ruido_m` | raio em que os zumbis ouvem o tiro (o barulho é o maior custo de uma arma de fogo no Recomeço) |
| `durabilidade` | tiros (ou golpes) até precisar de reparo na bancada |
| `peso_kg`, `raridade`, `valor_troca`, `onde` | peso, raridade, preço na troca e prédios onde aparece |
| `modificadores` (acessórios) | multiplicadores aplicados à arma, ex.: supressor `ruido_m ×0,3` |
| `receita` (improvisados) | o que gasta para fazer na bancada |

## Uso no Godot

```gdscript
var arma := ArmaRecomeco.new()
arma.id = "pistola_9mm"
arma.acessorios = {"encaixe_boca": "supressor_9mm", "encaixe_trilho": "lanterna_pistola"}
$Camera3D/Mao.add_child(arma)
arma.atirar()                     # anima, mostra o clarão e ejeta um estojo
arma.atributo("ruido_m")          # 60 × 0,3 = 18 m com o supressor
arma.recarregar()
```

## Lista completa (roteiro)

Uma arma por vez, sempre **junto com os seus acessórios**. Ordem atual (fotos de referência do Bruno, só inspiração): espingarda 12, carabina .308 (chassi e caça), fuzil 5,56, fuzil estilo AK, submetralhadoras compacta e de tambor, rifle .22, sinalizadora, fuzil de precisão 7,62 e pistola de serviço com trilho.

A espingarda recarrega **um cartucho por vez** (`recarga_por_cartucho`, a animação `recarregar` é de um cartucho) e solta a casca no bombeamento (`estojo_s` = 0,36 s).

| # | Arma | Partes móveis | Acessórios novos | Situação |
|---|---|---|---|---|
| 1 | **Pistola Sentinela 9 mm** | ferrolho, cano, gatilho, carregador | mira de ponto vermelho compacta, supressor 9 mm, supressor de garrafa PET, compensador, protetor de rosca, lanterna de trilho, laser, lanterna com laser, carregador 15 e estendido 24; cartucho, estojo, caixa de 50, clarão | **feita** |
| 2 | **Revólver Vigia .38** de 6 tiros | braço e tambor (abre de lado e gira 60° por tiro), extrator com estrela, cão, gatilho, trava, talas | carregador rápido, mira de ponto vermelho para revólver, talas de madeira e empunhadura de borracha, coldre de couro; cartucho, estojo e caixa de 50 .38 | **feita** |
| 3 | **Espingarda Mutirão 12** de bombeamento, longa e curta | telha (bombeia), ferrolho, gatilho, elevador, tampa do tubo | coronha retrátil e fixa (sem coronha = só punho), mira de ponto vermelho de tubo com tampas basculantes, choke estendido, freio dentado de arrombamento, lanterna de cano, prolongador do tubo (+1), porta-cartuchos lateral (6), bandoleira; cartuchos 12 de chumbo e balote, casca e caixa de 25 | **feita** |
| 4 | Espingarda de cano duplo (e versão de cano serrado) | canos basculantes, cães, extrator | cinta de cartuchos, coronha encurtada | |
| 5 | **Carabina Paciência .308** de ferrolho, de chassi e de caça (coronha de nogueira) | ferrolho (levanta 60° e corre), gatilho, carregador, apoio de rosto | luneta 3-9× e 4× com anéis de trilho, bipé dobrável, freio de boca, supressor de fuzil, protetor de rosca, carregadores de 10 e 5 (e a mira de tubo e a bandoleira da espingarda); cartucho, estojo e caixa de 20 .308 | **feita** |
| 6 | Fuzil 5,56 (semi e automático) | ferrolho, alavanca de manejo, carregador, retém, seletor, tampa da janela | mira holográfica, ponto vermelho tubular, luneta 1-6×, miras de ferro rebatíveis, empunhadura vertical e angulada, lanterna de fuzil, laser, bipé, coronha retrátil e fixa, quebra-chamas, compensador, supressor, carregadores de 30 e 60 tambor 60, tambor tático 60 com janela, módulo laser caramelo, lanterna compacta, empunhaduras curta, quadrada e cilíndrica, batente de mão; versão bicolor preta e caramelo | **feita** |
| 7 | **Fuzil Brasa 7,62** de receptor estampado (estilo AK) | tampa do receptor (sai), transportador com alavanca à direita, seletor de alavanca, gatilho, carregador (engancha na frente e gira) | coronhas de madeira, polímero, rebatível de tubo, retrátil com adaptador e leve vazada (preta e caramelo); guarda-mãos de madeira, polímero com nervuras e de quatro trilhos (libera empunhadura e lanterna); tampa com trilho (libera mira holográfica e lunetas); freio inclinado, freio de três câmaras, supressor 7,62; mira de ponto e luneta 4× de montagem lateral; baioneta; carregadores de 30 (aço) e 40 (polímero), tambor de 75; cartucho, estojo e caixa de 20 7,62×39. Novos para o 5,56 também: empunhadura vertical curta, coronha leve vazada e miras rebatíveis de polímero, em preto e caramelo | **feita** |
| 8 | Submetralhadora 9 mm compacta | ferrolho, alavanca, coronha dobrável, carregador | empunhadura frontal, supressor integral, carregador 30 (usa a munição 9 mm da pistola) | |
| 9 | Rifle .22 de caça (silencioso, para caça pequena) | ferrolho, carregador rotativo | luneta 4× pequena, supressor .22, munição .22 | |
| 10 | Pistola sinalizadora | cano basculante, cão | cartuchos de sinal (vermelho para socorro, verde para chamar sobreviventes, que também atrai zumbis) | |
| 11 | Arco recurvo de madeira | corda e braços (flexionam) | flechas (ponta de caça, ponta improvisada de prego), aljava, mira de pinos, estabilizador | |
| 12 | Arco composto | polias, cabos, corda | flechas de carbono, soltador, mira de pinos com luz | |
| 13 | Besta | corda, braços, trava, gatilho | virotes, luneta pequena, estribo de armar | |
| 14 | Faca de combate | - | bainha de cinto | |
| 15 | Facão | - | bainha de lona | |
| 16 | Machadinha tática | - | capa da lâmina | |
| 17 | Lança improvisada (faca presa num cabo) | - | receita: cabo + faca + fita | |
| 18 | Bastão com pregos / com arame farpado (melhoria do taco do loot) | - | receita na bancada | |
| 19 | Coquetel molotov, bomba de pregos (lata), isca sonora (despertador) | pavio, ponteiro | - | |

O arco, a lança e o facão do lote 4 de `props/loot/` são itens de loot simples (uma peça só); aqui eles ganham a versão completa, com partes, acessórios e animações.

## Verificação

- Todos os GLB passam no validador glTF oficial da Khronos (0 erros).
- Prévia 3D com as armas, os acessórios trocáveis e as animações: link na PR.
