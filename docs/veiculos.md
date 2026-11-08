# Veículos no Recomeço: design

Documento de design dos veículos do jogo [Recomeço](plano-jogo-sobrevivencia.md). Diz como os carros se comportam, de que peças eles são feitos, como o jogador desmonta carros abandonados e monta um carro que anda, como funcionam o combustível e o porta-malas, e como isso entra no código do jogo.

Os modelos 3D ficam em [`props/veiculos/`](../props/veiculos/). O primeiro é o **sedã Rumo**, um sedã compacto de 4 portas genérico dos anos 80/90, desenho próprio e sem marca.

## 1. O papel do carro no jogo

O carro não é um item de começo de jogo. É uma conquista da fase 2 (Abrigo) em diante, e muda o jeito de jogar:

| O carro dá | O carro cobra |
|---|---|
| Ir longe e voltar antes da noite (saques em prédios distantes) | Combustível, que é raro e acaba |
| Carregar muito: porta-malas, banco de trás e peças grandes | Barulho: motor, buzina e alarme chamam zumbis |
| Fugir de uma horda e atropelar zumbis soltos | Cada batida e cada zumbi atropelado estraga peças |
| Abrigo de emergência: trancado e com os vidros inteiros, aguenta alguns minutos | Manutenção: bateria descarrega, pneu fura, radiador vaza |
| Barricada: um carro empurrado fecha uma rua | Ninguém dirige sem as peças certas no lugar |

Regra de ouro: **o mundo está cheio de carros, mas quase nenhum anda.** Cada carro abandonado é um armário de peças e de saque. O jogador junta, de vários carros, as peças boas até ter um carro inteiro.

## 2. Carros no mundo

### 2.1 Estados de um carro abandonado

Cada carro parado na rua é sorteado com uma semente (posição no mapa + semente do mundo), então volta igual quando o jogador retorna. O estado define o que está faltando e em que condição está o resto.

| Estado | Chance | Como está | Peças |
|---|---|---|---|
| Parado | 35% | Inteiro, empoeirado, às vezes trancado | Todas no lugar. Bateria 0 a 30% de carga. Tanque 0 a 12 L. Pneus 40 a 90% (alguns murchos). Trancado em 50%; com alarme em 15% dos trancados. Chave no contato ou no quebra-sol em 10% |
| Saqueado | 30% | Portas e porta-malas abertos, sobre tijolos | Faltam 0 a 4 rodas (o carro fica sobre tijolos), bateria falta em 70%, tanque 0 a 3 L (tampa aberta, já sifonado), porta-malas quase vazio |
| Batido | 20% | Frente ou traseira amassada, para-brisa trincado | Para-choque, faróis e radiador da zona batida de 0 a 40%. Motor 20 a 70% se bateu de frente. Resto normal |
| Queimado | 10% | Só a carcaça | Quase nada aproveitável: aros de aço e o motor como sucata |
| Intacto | 5% | Limpo, com chave, porta-malas cheio | Tudo de 70 a 100%, tanque 10 a 30 L |

O estado aparece no modelo: peça que falta é um nó escondido, peça quebrada troca de material (farol estilhaçado, vidro trincado), e carro saqueado fica apoiado em tijolos.

### 2.2 Onde ficam

- Ruas e cruzamentos: parados no meio da pista, batidos uns nos outros, alguns subindo na calçada (sinal do pânico da fuga).
- Estacionamentos dos kits (supermercado, motel, hotel, clínica, rodoviária).
- Garagens das casas: carros "Parado" e "Intacto" ficam mais nas garagens fechadas.
- Concessionária, oficina e ferro-velho: muitas peças soltas e carros sem peças, mas também a **talha** para tirar motor (ver 4.4).
- Posto de gasolina: carros com o tanque vazio (foram abastecer e não deu tempo).

## 3. As peças do carro

Cada peça é um nó separado no modelo, com nome fixo (o **encaixe**). Quando o jogador tira a peça, ela vira um item de loot com a condição que tinha. Quando põe a peça num encaixe vazio, o nó volta a aparecer.

### 3.1 Lista de peças do sedã Rumo

"Precisa para andar" diz se o carro anda sem ela. "Padrão" diz em que carros a peça serve (peças do mesmo padrão servem em modelos diferentes, ver 3.4).

| Encaixe | Peça (item) | Precisa para andar | O que faz | Peso | Grade | Ferramenta | Tempo (tirar / pôr) |
|---|---|---|---|---|---|---|---|
| `motor` | Motor 1.6 (`motor_1_6`) | Sim | Potência. Condição baixa = falha, menos força, mais consumo | 118 kg | não cabe: só com talha | jogo de chaves + talha | 240 s / 300 s |
| `bateria` | Bateria 12 V (`bateria_12v`) | Sim, para dar partida | Partida, faróis, buzina, rádio. Guarda carga | 14 kg | 2 × 2 | jogo de chaves (ou chave inglesa) | 15 s / 20 s |
| `alternador` | Alternador (`alternador`) | Não, mas a bateria acaba | Recarrega a bateria com o motor ligado | 5 kg | 2 × 2 | jogo de chaves | 45 s / 60 s |
| `radiador` | Radiador (`radiador`) | Não, mas o motor ferve | Esfria o motor. Sem ele, ou vazio, o motor superaquece em 2 min e perde condição | 6 kg | 4 × 3 | jogo de chaves | 60 s / 75 s |
| `tanque` | Tanque de combustível 45 L (`tanque_45l`) | Sim | Guarda o combustível. Furado, vaza 1 L por minuto | 9 kg | 5 × 3 | jogo de chaves + macaco | 90 s / 120 s |
| `escapamento` | Escapamento com silencioso (`escapamento`) | Não | Sem ele o motor faz o dobro de barulho | 8 kg | 6 × 1 | jogo de chaves + macaco | 60 s / 75 s |
| `roda_de` `roda_dd` `roda_te` `roda_td` | Roda aro 14 com pneu (`roda_aro14`) | Sim, as 4 | Pneu cheio anda bem; murcho ou furado anda devagar e puxa para o lado | 16 kg | 3 × 3 | chave de roda + macaco | 40 s / 50 s |
| `estepe` | Roda aro 14 com pneu (`roda_aro14`) | Não | Roda de reserva, fica embaixo do assoalho do porta-malas | 16 kg | 3 × 3 | nenhuma | 5 s / 5 s |
| `porta_de` `porta_dd` | Porta dianteira esquerda / direita (`porta_dianteira_e`, `porta_dianteira_d`) | Não | Proteção contra zumbis, vidro, bolsa da porta | 22 kg | carga nas mãos | jogo de chaves | 60 s / 75 s |
| `porta_te` `porta_td` | Porta traseira esquerda / direita (`porta_traseira_e`, `porta_traseira_d`) | Não | Igual às dianteiras | 18 kg | carga nas mãos | jogo de chaves | 60 s / 75 s |
| `capo` | Capô (`capo`) | Não | Protege o motor: sem capô, a batida de frente e a chuva vão direto no motor | 14 kg | carga nas mãos | jogo de chaves | 30 s / 40 s |
| `tampa_porta_malas` | Tampa do porta-malas (`tampa_porta_malas`) | Não | Sem ela, o que está no porta-malas pode ser pego por qualquer um e molha | 10 kg | carga nas mãos | jogo de chaves | 30 s / 40 s |
| `para_choque_d` `para_choque_t` | Para-choque dianteiro / traseiro (`para_choque_dianteiro`, `para_choque_traseiro`) | Não | Absorve a primeira parte de cada batida e atropelamento | 7 kg | 7 × 1 | jogo de chaves | 40 s / 50 s |
| `paralama_e` `paralama_d` | Para-lama dianteiro esquerdo / direito (`paralama_e`, `paralama_d`) | Não | Protege a roda e o farol de lado | 5 kg | 4 × 2 | jogo de chaves | 60 s / 70 s |
| `farol_e` `farol_d` | Farol (`farol`) | Não | Luz à noite (cada um ilumina um lado) | 2 kg | 2 × 1 | jogo de chaves | 20 s / 25 s |
| `lanterna_e` `lanterna_d` | Lanterna traseira (`lanterna_traseira`) | Não | Luz de freio e de ré (avisa companheiros, não muda o jogo) | 1 kg | 2 × 1 | jogo de chaves | 15 s / 20 s |
| `retrovisor_e` `retrovisor_d` | Retrovisor (`retrovisor`) | Não | Mostra o que vem atrás na vista de 1ª pessoa | 0,8 kg | 1 × 1 | nenhuma (arranca) ou jogo de chaves | 5 s / 20 s |
| `para_brisa` | Para-brisa (`para_brisa`) | Não | Sem ele, ou estilhaçado, não se vê bem e o zumbi entra pela frente | 12 kg | carga nas mãos | jogo de chaves | 90 s / 120 s (30% de quebrar ao tirar) |
| `vidro_traseiro` | Vidro traseiro (`vidro_traseiro`) | Não | Igual ao para-brisa, atrás | 8 kg | carga nas mãos | jogo de chaves | 90 s / 120 s |
| `banco_motorista` | Banco dianteiro (`banco_dianteiro`) | Sim | Sem banco não dá para dirigir | 15 kg | carga nas mãos | jogo de chaves | 60 s / 70 s |
| `banco_passageiro` | Banco dianteiro (`banco_dianteiro`) | Não | Leva 1 passageiro | 15 kg | carga nas mãos | jogo de chaves | 60 s / 70 s |
| `banco_traseiro` | Banco traseiro (`banco_traseiro`) | Não | Leva 3 passageiros. Sem ele, o espaço vira carga | 20 kg | carga nas mãos | jogo de chaves | 60 s / 70 s |
| `volante` | Volante (`volante`) | Sim | Tirar o volante é a trava antifurto do fim do mundo: ninguém leva o seu carro | 2,5 kg | 2 × 2 | jogo de chaves | 30 s / 30 s |

Partes que abrem e fecham mas não saem como loot: `tampa_combustivel` (portinhola do tanque), `porta_luvas`, `assoalho_porta_malas` (tampa sobre o estepe), `quebra_sol_e` `quebra_sol_d` (onde às vezes está a chave).

### 3.2 Condição

Toda peça tem **condição de 0 a 100%**. Ela vem do estado do carro abandonado, cai com o uso e com batidas, e sobe com reparo.

| Peça | Acima de 60% | 30 a 60% | Abaixo de 30% | 0% |
|---|---|---|---|---|
| Motor | Normal | -20% de força, +15% de consumo, 10% de falha na partida | -45% de força, +30% de consumo, 35% de falha, morre às vezes em marcha lenta | Não liga |
| Bateria (carga e condição separadas) | Partida na hora | Partida em 1 a 3 tentativas | Só com chupeta ou carro empurrado (tranco) | Não segura carga |
| Alternador | Recarrega 10% por minuto | 5% por minuto | 2% por minuto | Não recarrega |
| Radiador | Normal | Vaza: perde água, motor esquenta em 8 min | Vaza muito: esquenta em 3 min | Igual a não ter |
| Tanque | Normal | Vaza 0,2 L/min | Vaza 1 L/min | Não guarda |
| Pneu (cada roda) | Normal | Murcho: -15% de velocidade, puxa um pouco | Furado: máx. 25 km/h, puxa forte, aro estraga | Só aro: máx. 15 km/h, faísca e barulho |
| Portas, capô, vidros | Inteiros | Amassados (só visual) | Abrem com zumbi forçando 2× mais rápido | Caem (viram loot com 0%) |
| Faróis | Luz cheia | Luz fraca | Pisca | Quebrado, sem luz |

### 3.3 Itens de oficina (loot novo)

Ferramentas e materiais que o jogador acha em garagens, oficinas, postos, ferro-velho e porta-malas.

| Item | Para que serve |
|---|---|
| Chave de roda em cruz (`chave_de_roda`) | Tira e põe rodas |
| Macaco sanfona (`macaco_sanfona`) | Ergue o carro para trocar roda, tanque e escapamento. O `macaco_jacare` que já existe faz o mesmo e mais rápido |
| Caixa com jogo de chaves (`jogo_de_chaves`) | Ferramenta geral: quase toda peça pede. A `chave_inglesa` que já existe serve só para a bateria |
| Mangueira para sifão (`mangueira_sifao`) | Puxa combustível de um tanque para um galão (1 L a cada 6 s). Barulho baixo |
| Cabos de chupeta (`cabos_chupeta`) | Dá partida com a bateria de outro carro (ou do gerador) |
| Bomba de ar manual (`bomba_ar`) | Enche pneu murcho (de 30 para 100% em 40 s) |
| Kit de remendo de pneu (`kit_remendo_pneu`) | Conserta pneu furado: volta para 60%. 5 usos |
| Óleo de motor 1 L (`oleo_motor`) | +15% de condição do motor (até 70%). Motor sem troca perde 1% por hora rodando |
| Velas de ignição (jogo de 4) (`velas_ignicao`) | Motor com falha: +20% de condição (até 80%) e -10% de falha na partida |
| Chave de carro (`chave_carro`) | Abre e liga **um** carro específico (o item guarda qual). Achada no quebra-sol, no contato, em gavetas de casas e em zumbis |
| Kit de ligação direta (`kit_ligacao_direta`) | Liga o carro sem chave (ver 5.2) |

Já existem e entram no sistema: `galao_gasolina` (leva 20 L), `bateria_carro` (serve como `bateria_12v`), `peca_motor` (repara motor e alternador, +25%), `fita_adesiva` (tapa o radiador ou o tanque por 1 dia de jogo), `galao_agua` e `garrafa_agua` (enchem o radiador), `pe_de_cabra` (força porta-malas e arranca peça sem ferramenta, ver 4.3), `macaco_jacare`, `chave_inglesa`.

### 3.4 Padrões: peças que servem em mais de um carro

Cada peça tem um `padrao`. Peças do mesmo padrão servem em qualquer modelo que aceite esse padrão. Assim, quando vierem os próximos carros, o jogador pode pôr o motor de uma perua num sedã.

| Padrão | Peças | Serve em |
|---|---|---|
| `compacto_1_6` | motor, alternador, radiador, escapamento | sedã Rumo e os próximos compactos (hatch, perua) |
| `aro14_4furos` | roda, estepe | sedã, hatch, perua |
| `bateria_12v` | bateria | todos os carros e o gerador da base |
| `sedan_rumo` | portas, capô, tampa, para-choques, para-lamas, vidros | só o sedã Rumo (carroceria é de cada modelo) |
| `universal` | faróis, lanternas, retrovisores, bancos, volante | qualquer carro |

## 4. Desmontar e montar

### 4.1 Mirar e agir, como nos móveis

O carro usa o mesmo jeito de interagir que os móveis já usam (`movel.gd`): cada parte tem a sua caixinha de colisão, o jogador mira nela e aperta **E**.

- **E** numa porta, no capô, no porta-malas, no porta-luvas ou na portinhola do tanque: abre ou fecha (anima girando na dobradiça).
- **Segurar E** numa peça, com a ferramenta certa no inventário: desmonta. Aparece uma barra de progresso com o tempo da tabela 3.1. Se o jogador se mexer, toma dano ou soltar, para (o progresso fica guardado na peça por 1 min).
- **Segurar E** num encaixe vazio (ele aparece como um contorno da peça) com a peça na mão ou no inventário: monta.
- Sem a ferramenta, o rótulo diz qual falta: "Precisa de chave de roda e macaco".

### 4.2 Tela da oficina

Com o capô aberto, ou mirando no carro e apertando **O**, abre a tela da oficina ao lado do inventário (mesma interface em grade):

- À esquerda, o carro de cima e de lado com cada encaixe marcado: verde (bom), amarelo (gasto), vermelho (ruim), contorno vazio (falta).
- Passar o mouse mostra peça, condição e o que ela faz. Arrastar uma peça da mochila ou do porta-malas para um encaixe monta (com o mesmo tempo); arrastar do encaixe para a grade desmonta.
- Embaixo: combustível (L), carga da bateria, água do radiador, e o diagnóstico em frases curtas: "Não liga: falta bateria", "Vai ferver: radiador vazando".

### 4.3 Ordem e regras

- Peças por cima saem primeiro: para tirar o **motor**, o capô tem de estar aberto (ou fora) e o radiador e a bateria fora. Para tirar o **tanque** ou o **escapamento**, o carro tem de estar no macaco. Para tirar o **estepe**, abre o porta-malas e o assoalho.
- O **tanque** com combustível derrama ao ser tirado (perde tudo e faz poça inflamável). Sifone antes.
- Carro **trancado**: abre com a chave, com o kit de ligação direta (também destrava, 20 s), quebrando o vidro (qualquer arma, barulho alto, 15% de alarme) ou forçando o porta-malas com o pé de cabra (12 s, barulho médio, a tampa fica com 50%).
- **Arrancar** sem ferramenta, com o pé de cabra: faróis, lanternas, retrovisores, para-choques e para-lamas saem em metade do tempo, mas com -40% de condição e muito barulho.
- Cada ação faz barulho (raio em que os zumbis ouvem): chave de roda 15 m, jogo de chaves 10 m, pé de cabra 35 m, vidro quebrando 40 m, alarme 150 m por 30 s.

### 4.4 Peças grandes

- **Carga nas mãos** (portas, capô, tampa, vidros grandes, bancos): o jogador carrega com as duas mãos, sem arma, a 60% da velocidade, e pode largar a qualquer momento (tecla G). Essas peças não entram na mochila: vão no porta-malas, se couberem na grade, no banco de trás ou no chão.
- **Motor**: não vai no inventário. Precisa de uma **talha** (a do ferro-velho e a da oficina da concessionária já existem nos kits; na base, a talha entra como estação da fase 2). Com a talha, o motor sai do carro, fica pendurado e pode ser baixado no carro de destino se os dois estiverem embaixo da talha, ou no carrinho de oficina, ou na caçamba de uma picape (próximo veículo).
- Rodas e bateria podem ir na mochila (se couberem na grade), mas pesam: cada roda a mais deixa o passo mais lento.

## 5. Dirigir

### 5.1 Entrar e sair

- **E** na porta do motorista: abre a porta e senta (animação curta). Se houver zumbi colado na porta, não entra.
- **E** dentro do carro: sai pela porta mais próxima livre. Sair com o carro andando acima de 15 km/h machuca.
- Passageiros da comunidade (fase 3) ocupam o banco do passageiro e o de trás, e saem para lutar quando o carro para.

### 5.2 Partida

| Situação | Como liga | Chance |
|---|---|---|
| Com a chave | Segurar **W** por 1 s (o motor de arranque gira) | 100%, menos a falha do motor e a da bateria (3.2) |
| Sem chave, com kit de ligação direta | Segurar **E** mirando no painel, 20 s | 70%. Falha queima um fusível: mais 20 s |
| Bateria fraca, com cabos de chupeta | Outro carro ligado ou bateria carregada ao lado, 10 s | Como com a chave |
| Bateria fraca, sem nada | Tranco: empurrar o carro a 10 km/h (ladeira ou 2 pessoas) e soltar a embreagem | 60% |

O motor de arranque faz barulho de 30 m em cada tentativa.

### 5.3 Comandos

| Tecla | Ação |
|---|---|
| W / S | Acelera / freia, e dá ré com o carro parado |
| A / D | Vira |
| Espaço | Freio de mão |
| H | Buzina (120 m de barulho: chama zumbis de propósito, para tirá-los de um lugar) |
| L | Faróis |
| V | 1ª pessoa (no banco, vê o painel e os retrovisores) e 3ª pessoa (atrás do carro) |
| Tab | Vista de cima: o carro aparece no mapa |
| E | Sair |

### 5.4 Física

Usa o `VehicleBody3D` do Godot, com uma roda (`VehicleWheel3D`) em cada encaixe `roda_*` do modelo. A frente do carro é +Z no modelo, que é o que o `VehicleBody3D` espera.

| Parâmetro | Sedã Rumo |
|---|---|
| Massa vazio | 1080 kg (cada peça tirada desconta o peso dela; carga no porta-malas soma) |
| Centro de massa | 0,45 m do chão |
| Tração | Dianteira |
| Força do motor | 3200 N máx., vezes o fator de condição do motor |
| Velocidade máxima | 140 km/h na estrada, mas a rua cheia de carros e entulho segura bem menos |
| Freio | 40 (freio de mão trava as traseiras) |
| Direção | 32° parado, caindo para 8° a 100 km/h |
| Rodas | Raio 0,31 m, largura 0,185 m. Suspensão: curso 0,15 m, rigidez 40, compressão 0,85, retorno 0,9 |
| Atrito do pneu | Asfalto 2,6, terra 1,8, grama 1,4, lama 0,9. Pneu murcho ×0,85, furado ×0,5 |

### 5.5 Barulho

O carro emite barulho (o mesmo sinal de ruído que os zumbis ouvem):

| Fonte | Raio |
|---|---|
| Motor em marcha lenta | 25 m |
| Andando | 25 m + 0,6 m por km/h (60 m a 60 km/h) |
| Sem escapamento | ×2 |
| Buzina | 120 m |
| Alarme | 150 m por 30 s |
| Batida | 50 m |

## 6. Combustível

- **Tanque de 45 L**, com medidor no painel (1ª pessoa) e na tela da oficina.
- **Consumo**: 8 L a cada 100 km andando, mais 0,8 L por hora de jogo com o motor ligado parado. Motor ruim gasta até 30% a mais. O mapa é pequeno, então um tanque cheio dura muitas saídas; a falta vem de encontrar combustível, não da distância.
- **Onde achar**:
  - Tanques de carros abandonados, com a mangueira de sifão e um galão: 0 a 12 L cada (tabela 2.1). É a fonte principal.
  - Galões de gasolina (20 L) em garagens, postos e quartéis.
  - Posto de gasolina: o tanque enterrado tem muito combustível, mas a bomba é elétrica. Precisa de energia (gerador da base ligado ao posto, fase 2) ou de uma bomba manual (craft da bancada, fase 2).
- **Abastecer**: E na portinhola do tanque com um galão no inventário: 1 L a cada 3 s.
- **Disputa com a base**: o mesmo combustível alimenta o gerador da base (o `galao_gasolina` já diz "abastece gerador por 8 horas"). Usar no carro é tirar luz da base. Essa escolha é parte do jogo.
- **Gasolina velha** (fase 4 em diante): combustível de tanque de carro abandonado estraga depois de 90 dias de jogo (-20% de força, +20% de falha de partida). Do posto, não. Isso empurra o jogador para o posto e para a refinaria improvisada do fim do jogo.

## 7. Porta-malas e compartimentos

Cada compartimento é uma grade, igual à das gavetas e portas de móveis: abre sozinha, tem o seu saque e mostra o painel de saque à direita do inventário.

| Compartimento | Grade | Como abre | Saque em carro abandonado |
|---|---|---|---|
| Porta-malas | 9 × 5 | E na tampa (trancado: chave, ligação direta ou pé de cabra) | Mala ou mochila de fuga (roupas, comida, remédios) 30%, macaco sanfona 50%, chave de roda 50%, garrafa de água 25%, óleo de motor 20%, cabos de chupeta 15%, cobertor ou saco de dormir 15%, galão de gasolina 10%, caixa com jogo de chaves 10% |
| Fundo do porta-malas | 3 × 3 (só o estepe) | E no assoalho, com o porta-malas aberto | Estepe 60% (menos nos saqueados) |
| Porta-luvas | 3 × 2 | E no porta-luvas, de dentro ou pela porta aberta | Mapa da cidade, lanterna, pilhas, isqueiro, bilhete, chave de casa, remédio |
| Bolsas das portas dianteiras | 3 × 1 cada | E na porta aberta | Garrafa de água, salgadinho, chave de carro (2%) |
| Console | 2 × 1 | E entre os bancos | Isqueiro, pilhas, moedas (sucata) |
| Quebra-sol | 1 × 1 cada | E no quebra-sol, sentado | Chave do próprio carro (10% em carro trancado) |
| Banco de trás | 8 × 4 | Sempre aberto (coisas jogadas no banco) | Mochila, roupas, caixas de papelão |

Regras do porta-malas:

- Itens do carro do jogador ficam guardados no carro (persistem): o porta-malas é o baú que anda.
- **Carga pesada** pesa no carro: cada 100 kg no porta-malas e no banco de trás tiram 5% da aceleração.
- Sem a tampa, o porta-malas fica aberto: chuva estraga comida e papel, e zumbis não pegam nada, mas outros sobreviventes (fase 3) podem pegar.
- Banco traseiro tirado: o espaço vira uma grade de carga de 9 × 4, mas o carro leva só 1 passageiro.

## 8. Dano

### 8.1 Batidas

Cada colisão com impacto acima de 8 km/h gera dano = (velocidade do impacto em km/h - 8) × 1,2, distribuído pela zona que bateu:

| Zona | Para onde vai o dano |
|---|---|
| Frente | para-choque dianteiro 40%, faróis 15%, radiador 20%, capô 15%, motor 10%. Sem para-choque, a parte dele vai para o radiador e o motor |
| Traseira | para-choque traseiro 50%, lanternas 15%, tampa do porta-malas 25%, tanque 10% |
| Lados | portas daquele lado 60%, vidros 25%, retrovisor 15% |
| Embaixo (subir em entulho, meio-fio rápido) | escapamento 50%, tanque 30%, rodas 20% |

Batida acima de 60 km/h também machuca o motorista (vida).

### 8.2 Zumbis

- **Atropelar**: abaixo de 20 km/h o zumbi cai e levanta; de 20 a 45 km/h fica no chão com dano grande; acima de 45 km/h morre. Cada atropelamento dá 2 a 6 de dano na frente (zona Frente) e deixa sangue na pintura.
- **Carro parado com gente dentro**: os zumbis batem nos vidros. Cada pancada tira 8% do vidro. Vidro a 0% quebra e o zumbi alcança quem está naquele banco. Com tudo inteiro, o carro aguenta 2 a 4 minutos de uma horda pequena: dá tempo de dar partida ou de esperar o grupo passar.
- **Portas abertas** deixam o zumbi entrar direto.

### 8.3 Reparo

| Reparo | Com | Efeito |
|---|---|---|
| Motor, alternador | `peca_motor` | +25% |
| Motor | `oleo_motor`, `velas_ignicao` | +15% / +20% (com teto) |
| Pneu | `kit_remendo_pneu` + `bomba_ar` | Furado volta a 60% |
| Radiador, tanque | `fita_adesiva` | Para o vazamento por 1 dia de jogo |
| Lataria (portas, capô, para-lamas, para-choques) | Bancada de solda (fase 2, lote 15) + `chapa_metal` | +30% |
| Vidros | Não tem conserto: troca por outro de carro abandonado | |

## 9. O que fica guardado (salvar o jogo)

Cada carro que o jogador mexeu guarda um registro; os outros são recriados pela semente.

```json
{
  "modelo": "sedan_rumo",
  "semente": 48213,
  "posicao": [12.4, 0.0, -30.2], "rotacao_y": 1.57,
  "cor": [0.42, 0.08, 0.06],
  "trancado": false, "chave": "chave_carro#48213",
  "combustivel_l": 17.5, "bateria_carga": 0.82, "radiador_agua": 1.0,
  "encaixes": {
    "motor": {"id": "motor_1_6", "condicao": 64},
    "roda_de": {"id": "roda_aro14", "condicao": 88},
    "roda_dd": null,
    "porta_de": {"id": "porta_dianteira_e", "condicao": 40, "vidro": 100}
  },
  "abertas": ["porta_malas"],
  "grades": {"porta_malas": [{"id": "macaco_sanfona", "qtd": 1, "x": 0, "y": 0, "w": 3, "h": 1}]}
}
```

## 10. Como entra no código do jogo

O código fica no repositório privado `recomeco`. Os arquivos novos:

| Arquivo | O que faz |
|---|---|
| `jogo/veiculos/veiculo.gd` | `VehicleBody3D`. Carrega `props/veiculos/<modelo>.glb`, põe uma `VehicleWheel3D` em cada nó `roda_*`, lê os encaixes do catálogo, guarda o estado (seção 9), calcula massa, força, consumo, barulho e dano |
| `jogo/veiculos/partes_veiculo.gd` | Caixinhas de colisão na camada 2 em cada parte que abre e em cada encaixe, igual ao `movel.gd`, com os rótulos ("Abrir porta-malas", "Desmontar farol (precisa de jogo de chaves)") |
| `jogo/veiculos/dirigir.gd` | Entrar, sair, partida, comandos, câmera de 1ª e 3ª pessoa no carro, integração com as 3 vistas |
| `jogo/interface/tela_oficina.gd` | Tela da oficina (4.2), ao lado do inventário em grade |
| `jogo/mundo/carros_abandonados.gd` | Espalha carros pelas ruas e estacionamentos com semente e estado (seção 2) |

Mudanças em código que já existe (combinar antes com a thread do jogo, porque o inventário e os zumbis estão sendo mexidos lá):

- `inventario.gd`: carregar também `props/veiculos/catalogo.json` (lista `pecas` e `ferramentas`), no mesmo formato do loot.
- `grade.gd`: nada; as grades do carro são `Grade` comuns.
- Barulho: o carro usa o mesmo sinal de ruído que os zumbis da PR do combate ouvem.

### 10.1 Etapas

| Etapa | Entrega |
|---|---|
| V1 | Sedã dirigível no mapa de teste: entrar, sair, partida com chave, combustível, câmeras, barulho |
| V2 | Peças: encaixes, montar e desmontar com ferramenta, condição, tela da oficina |
| V3 | Carros abandonados com estados e semente, porta-malas e compartimentos com saque, sifão |
| V4 | Dano por zona, atropelamento, zumbis nos vidros, reparos |
| Depois | Próximos modelos: hatch, perua, picape (caçamba e guincho), van, moto; talha e carrinho de oficina na base |

## 11. Convenções do modelo 3D

- Y para cima, 1 unidade = 1 m, **frente para +Z**. O pivô do carro fica no chão, no meio entre os eixos.
- O lado esquerdo do carro (motorista, volante à esquerda) é **+X**.
- Cada encaixe é um nó com o nome da tabela 3.1, com a origem:
  - nas portas, no capô, na tampa e nas portinholas: no eixo da dobradiça. O catálogo diz `eixo` e `abre_graus` (com sinal), igual às partes dos móveis;
  - nas rodas: no centro do cubo (é ali que entra a `VehicleWheel3D`);
  - nas outras peças: no ponto de fixação (centro da base da peça).
- Cada peça também sai sozinha como GLB de loot em `props/veiculos/pecas/<id>.glb`, deitada e com o pivô no centro da base, igual aos outros itens de loot.
- Materiais com nome fixo para o jogo trocar: `pintura` (a cor do carro vem do `baseColorFactor`, para sortear cores), `vidro`, `cromado`, `borracha`, `plastico_preto`, `lente_farol`, `lente_lanterna`.
