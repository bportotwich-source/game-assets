# Plano de desenvolvimento: jogo de sobrevivência e comunidade

> Nome provisório: **Recomeço**. Documento de planejamento, sem código ainda.
> Data: 7 de novembro de 2026. Motor: Godot 4.3. Base de assets: os 24 kits deste repositório.

## 1. Resumo e recomendação

O jogador acorda sozinho numa cidade pequena tomada por zumbis. Ele junta recursos, transforma um prédio abandonado em abrigo, encontra outros sobreviventes e, com eles, reconstrói uma comunidade que cresce até virar uma cidade nova.

**Recomendação de escopo:** fazer um jogo **híbrido em duas câmeras sobre o mesmo mundo**.

- **A pé** (terceira pessoa, com opção de primeira pessoa): explorar, saquear, lutar e conversar. Aproveita direto o que já existe: todos os kits são entráveis, têm portas que abrem e escala real.
- **Modo prefeito** (vista de cima, inclinada): planejar a base, posicionar construções no grid de 2 m, distribuir tarefas e acompanhar os números da comunidade. É aqui que entra o estilo de construção de cidade das referências.

O jogador começa só com a câmera a pé. O modo prefeito é **desbloqueado** quando a base tem o primeiro sobrevivente além dele (fim da fase 1). Assim o jogo começa simples, como sobrevivência, e vai virando gestão aos poucos, sem dois jogos separados.

**MVP:** uma cidadezinha (cerca de 400 × 400 m) montada com uns 15 kits, de 2 a 3 horas de jogo, indo do "sozinho" até "vila de 20 pessoas com rádio funcionando". Estimativa: **cerca de 7 meses** para uma pessoa trabalhando com IA, dividido em 6 marcos (seção 10).

O que **não** entra no MVP: mapa-múndi com várias cidades, facções inimigas humanas, multiplayer, veículos dirigíveis, clima e estações. Ficam para depois porque cada um sozinho é quase do tamanho do MVP.

## 2. Conceito

| Item | Definição |
|---|---|
| Gênero | Sobrevivência + gestão de base/comunidade + construção de cidade |
| Visual | Estilizado "toon" com contorno, cores quentes de dia e cidade iluminada à noite. É o visual que os kits já têm |
| Plataforma | PC (Windows), build pelo CI do GitHub como hoje |
| Sessão típica | 30 a 60 min; um "dia" de jogo dura de 12 a 15 min em velocidade normal |
| Público | Quem gosta de sobrevivência com construção e de city builders aconchegantes, mas quer tensão |

**Tom:** esperança no meio do fim do mundo. O apocalipse é o ponto de partida, não o tema. O que o jogador vê crescer é a comunidade; os zumbis são a pressão que torna cada escolha importante.

## 3. Pilares

1. **Cada prédio conta.** O mundo é feito de prédios reais e entráveis. Um supermercado é comida, um posto é combustível, o quartel dos bombeiros é uma base forte. Saquear, ocupar e restaurar prédios é o centro do jogo.
2. **Pessoas, não unidades.** Cada sobrevivente tem nome, história curta, habilidades, um traço de personalidade e necessidades. Perder alguém dói.
3. **Do caos à ordem.** A cidade começa em ruínas e escura. O progresso é visível: muros, hortas, luz elétrica voltando rua por rua.
4. **A noite é perigosa.** O ciclo dia/noite define o ritmo: de dia explora e constrói, à noite defende. A cada 7 dias vem uma horda maior.

## 4. Os ciclos de jogo

### 4.1 Ciclo de sobrevivência (minutos)
Fome, sede, energia (sono), saúde e ferimentos. Comer, beber, dormir e se tratar. Barulho atrai zumbis; correr cansa; a noite reduz a visão. Simples de propósito: são 4 barras, sem micro-gestão de vitaminas ou temperatura no MVP.

### 4.2 Ciclo de exploração e saque (10 a 20 min)
Escolher um prédio no mapa, ir até ele, entrar, revistar contêineres (armários, geladeiras, prateleiras), lidar com zumbis lá dentro e voltar antes de escurecer. Cada tipo de prédio tem uma tabela de saque (seção 6). Prédios já saqueados ficam marcados e só repõem pouco com o tempo. Isso força a expansão para longe da base.

### 4.3 Ciclo da base (1 dia de jogo)
Ocupar um prédio, limpar, barricar portas e janelas, montar estações (bancada, fogão, cama, coletor de água, horta) e depois construções novas no terreno em volta. As construções usam **peças dos kits**: o jogador pode erguer uma casa nova com as mesmas paredes, telhados e portas, encaixadas no grid de 2 m.

### 4.4 Ciclo da comunidade (vários dias)
Encontrar sobreviventes (em eventos no mapa, pelo rádio, ou eles chegam sozinhos quando a base é atrativa), convencer a entrar, dar moradia e tarefa. Cada pessoa tem **necessidades** (comida, água, abrigo, segurança, convívio) que viram um número de **moral**. Moral alta: trabalham melhor e atraem mais gente. Moral baixa: brigas, preguiça, gente indo embora. Pedidos e reclamações aparecem como cartões com nome e foto, no estilo de um conselheiro.

### 4.5 Ciclo da cidade (semanas de jogo)
Com 10+ pessoas, o modo prefeito ganha força: pintar **áreas** (moradia, cultivo, oficina, defesa) que se preenchem sozinhas quando há recursos e gente; puxar **trilhas e ruas** (só cresce o que está ligado); restaurar **serviços** (água encanada, energia, saneamento, lixo) que liberam prédios melhores; erguer **marcos** (torre de rádio, muralha, mercado) que mudam a fase do jogo.

### 4.6 Ciclo de ameaça
Zumbis vagam pelo mapa em grupos pequenos e são atraídos por barulho e luz. A cada 7 dias, uma **horda** ataca a base pelos lados mais expostos. Entre hordas, o jogador decide: gastar em defesa ou em crescimento. Esse é o conflito principal de recursos do jogo.

## 5. Fases de progressão

| Fase | Pessoas | Câmera | O que o jogador faz | Termina quando |
|---|---|---|---|---|
| 1. Sozinho | 1 | A pé | Sobreviver, achar um abrigo, barricar | Ocupa um prédio e recruta o 1º sobrevivente |
| 2. Abrigo | 2 a 5 | A pé + prefeito básico | Estações de trabalho, tarefas, primeira horda | Sobrevive à 1ª horda e tem horta + água |
| 3. Assentamento | 6 a 20 | As duas | Muro, áreas de moradia e cultivo, oficina | Ergue o marco **Torre de rádio** |
| 4. Vila | 20 a 60 | Mais prefeito | Restaurar água e energia, escola, enfermaria | Religa a **subestação** e ilumina o centro |
| 5. Cidade nova | 60+ | Prefeito | Retomar bairros inteiros, comércio, ônibus | (pós-MVP) |

O MVP vai até o fim da fase 3 e mostra o começo da 4. O desbloqueio por **marco** (um prédio especial que muda a fase) dá metas claras ao jogador e ao desenvolvimento.

## 6. Como os kits entram no jogo

Os kits viram **prédios do mundo**. Cada um ganha um arquivo de jogo com: função, tabela de saque, capacidade, custo de reparo e se pode ser ocupado.

| Kit | Papel no mundo | Saque principal | Depois de ocupado |
|---|---|---|---|
| Quartel de bombeiros | Base inicial sugerida | Ferramentas, machados, kit médico | Base forte com galpão e alojamento |
| Supermercado | Prédio de risco alto | Comida enlatada, água | Depósito central |
| Posto de gasolina | Recurso raro | Combustível, salgadinhos | Gerador / garagem |
| Padaria | Produção | Farinha, lenha | Padaria da comunidade |
| Diner | Encontro | Comida, utensílios | Cozinha comunitária (moral) |
| Armazém com celeiro | Fazenda | Sementes, ferramentas agrícolas | Celeiro e hortas |
| Igreja | Abrigo seguro | Velas, tecido | Refeitório / reuniões (moral) |
| Escolinha | Pessoas | Livros, cadernos | Escola (crianças viram aprendizes) |
| Biblioteca | Conhecimento | Livros técnicos | Pesquisa: desbloqueia projetos |
| Correios | Comunicação | Rádios, pilhas | Torre de rádio (marco da fase 3) |
| Estação de trem | Ponto de chegada | Caixas de carga variadas | Entrada de sobreviventes / comércio (pós-MVP) |
| Galeria comercial | "Masmorra" grande | Muito de tudo, muitos zumbis | Mercado (fase 4+) |
| Motel | Moradia rápida | Roupa de cama, sabão | 12 quartos para moradores |
| Torre escalonada | "Masmorra" vertical | Saque raro nos andares altos | Mirante (revela o mapa) |
| Casas (bangalô, americana, duplex, shotgun, casa de campo, enxaimel) | Moradia | Comida, roupas, remédios | Casas para famílias |
| Prédios de apartamentos (tijolos, mansarda, three-flats, sobrados) | Moradia densa | Variado | Muitas moradias de uma vez |

### 6.1 O que falta em cada kit para virar prédio de jogo
1. **Variante em ruínas.** Gerada por script: tira algumas peças (vidros, telhas, partes de parede), põe tábuas pregadas, entulho e manchas. Reparar = recolocar as peças originais, uma por vez. O visual de "a cidade voltando" sai de graça.
2. **Pontos de interesse.** Marcar no `building_layout.json` onde ficam contêineres de saque, pontos de barricada (portas e janelas já têm tags) e pontos de entrada de zumbis.
3. **LODs.** O prédio montado em alto detalhe tem perto de 80 mil triângulos e até 19 MB. Uma cidade com 50 prédios precisa de 3 níveis: alto (perto, a pé), médio (meia distância) e um bloco simples para a vista de cima de longe. Pode ser gerado com o Blender sem interface, como já fazemos nos recortes.
4. **Miniatura.** Render automático do prédio isolado num pedestal, para os cartões do menu de construção.
5. **Arquivo de dados do jogo.** Um `.tres` ou JSON por prédio com função, saque e custos.

### 6.2 O editor de montagem
O editor (PR #35) vira a ferramenta de **construção dentro do jogo**. O mesmo código que encaixa peças no grid de 2 m serve para:
- **Desenvolvimento:** montar prédios novos e variações sem programar.
- **Jogador:** no modo prefeito, construir com "plantas" prontas (uma casa de 2 módulos, um muro, uma torre de vigia) e, mais tarde, montar peça por peça.
- **Prédios esticáveis:** como nos cartões das referências, uma casa pode ser esticada de 2 em 2 m no comprimento, porque as paredes já são módulos repetíveis.

## 7. Modo prefeito: como o estilo das referências se traduz

Das referências, aproveitamos **ideias de interface e de sistema**, com arte e nomes próprios:

| Ideia de interface | Como fica no Recomeço |
|---|---|
| Barra superior com população, dinheiro, aprovação, relógio e velocidade | Sobreviventes, estoque (comida, água, materiais), **moral**, hora e dia, pausar / 1x / 2x / 3x |
| Medidores de serviços (energia, água, esgoto, lixo) | Água, energia, saneamento (doença) e **defesa** |
| Barra inferior por categorias | Trilhas e muros, Moradia, Comida, Oficinas, Serviços, Defesa, Marcos, Demolir |
| Cartões de prédio com custo e capacidade | Cartão com custo em materiais, moradores ou vagas de trabalho e tempo de obra |
| Prédios que se esticam com o mouse | Prédios montados com módulos de 2 m, esticáveis |
| Pintar zonas que só crescem perto de ruas | Pintar áreas que só crescem **dentro do muro e ligadas a uma trilha** |
| Recado de um conselheiro | Cartões dos moradores: "Estamos sem camas! Precisamos de mais moradia." |
| Lista de primeiros passos | Tutorial em metas curtas que somem quando cumpridas |
| Cidade acesa à noite | A luz é um recurso: base iluminada é mais segura, mas atrai zumbis de longe |

Visual da interface: painéis claros com cantos arredondados e ícones desenhados, para contrastar com o mundo escuro e sujo. Fica aconchegante sem perder a tensão.

## 8. Arquitetura técnica em Godot 4

### 8.1 Princípios
- **Separar simulação de visual.** A comunidade, os recursos e as hordas rodam numa simulação com passo fixo (por exemplo 4 vezes por segundo de jogo). A cena 3D só mostra o estado. Isso permite acelerar o tempo, salvar fácil e testar regras sem abrir o jogo.
- **Tudo por dados.** Prédios, receitas, itens, traços de personalidade e eventos ficam em arquivos (`.tres` ou JSON). Balancear o jogo vira editar tabelas.
- **GDScript primeiro.** Só passar algo para C# ou GDExtension se medir que está lento (provavelmente só a movimentação de hordas).

### 8.2 Módulos
| Módulo | Responsabilidade |
|---|---|
| `Mundo` | Carrega o mapa da cidade, prédios (com LOD), terreno, ruas, vegetação |
| `Grid` | Grid de 2 m: ocupação, o que é construível, ligação por trilha, área dentro do muro |
| `Construcao` | Plantas, obras em andamento, reparo de ruínas (reaproveita o editor) |
| `Inventario` | Itens, estoque da base, contêineres de saque |
| `Sobrevivente` | Necessidades, habilidades, traços, humor, rotina |
| `IA_Moradores` | Escolha de tarefa por utilidade (comer, dormir, trabalhar, defender) + navegação |
| `IA_Zumbis` | Grupos que vagam, atração por som e luz, hordas com campo de fluxo até a base |
| `Combate` | Corpo a corpo, armas de fogo simples, barulho, dano em barricadas |
| `Tempo` | Relógio, dia/noite, velocidade, agenda das hordas |
| `Eventos` | Encontros, pedidos, chegada de sobreviventes, marcos |
| `UI` | HUD a pé, modo prefeito, cartões, menus de construção |
| `Salvar` | Estado inteiro em JSON versionado |

### 8.3 Pontos de desempenho
- **Hordas:** zumbis distantes como `MultiMeshInstance3D` com animação por textura (sem esqueleto); só os próximos viram personagens completos. Meta: 200 zumbis visíveis a 60 fps.
- **Navegação:** `NavigationServer3D` para moradores; para hordas, um campo de fluxo no grid de 2 m (barato para centenas de agentes).
- **Prédios:** LOD automático do Godot + "visibility range" por prédio; interiores só carregam quando o jogador está perto.
- **Iluminação:** luzes de rua e janelas como emissivo + poucas luzes reais perto da câmera.

### 8.4 Organização no repositório
Recomendo **um repositório novo para o jogo** (por exemplo `recomeco`), com este pacote de assets entrando como submódulo ou cópia por script. Motivos: os kits continuam um pacote reutilizável para outros jogos, e o jogo pode ter seu próprio CI, versões e builds.

## 9. Assets que faltam além dos kits

Em ordem de prioridade:

1. **Personagens** (maior lacuna): protagonista, 6 a 8 modelos de sobreviventes com variação de cor e roupa, 3 a 4 tipos de zumbi (comum, rápido, pesado, "gritador" que chama outros). Animações: andar, correr, agachar, atacar, morrer, carregar, trabalhar (martelar, cavar, cozinhar), sentar, dormir. Recomendação: começar com **pacotes CC0** de personagens estilizados e animações (Quaternius, Kenney) para não travar, e trocar por modelos próprios no estilo dos kits a partir do marco 5.
2. **Objetos de interior e saque:** armários, geladeiras, prateleiras, camas, mesas, caixas, sacos. Muitos são simples e podem ser gerados por script como as peças dos kits.
3. **Construções de sobrevivência:** barricadas de tábua, muro de sucata, portão, torre de vigia, horta, coletor de chuva, fogueira, bancada, gerador, cata-vento, caixa d'água. É um **kit 25** nos mesmos moldes dos outros.
4. **Ruínas e entulho:** carros abandonados, lixo, entulho, árvores caídas, cercas quebradas, postes.
5. **Terreno e natureza:** grama, terra, asfalto rachado, calçadas, árvores e arbustos (alguns tomando conta das ruas).
6. **Interface:** ícones de recursos e categorias, retratos dos sobreviventes, cartões.
7. **Som:** ambiente (vento, pássaros de dia, silêncio pesado à noite), passos, zumbis, combate, construção, trilha calma para o modo prefeito e tensa para hordas.

## 10. Escopo do MVP

### Entra
- 1 mapa: cidadezinha de cerca de 400 × 400 m com uns 15 kits (cerca de 40 prédios, repetindo os kits de casas)
- Câmera a pé + modo prefeito
- 4 necessidades do jogador, saque, inventário, 10 receitas de produção
- 6 recursos: comida, água, madeira, sucata, remédios, combustível
- Ocupar prédio, barricar, reparar ruínas
- 15 construções (do kit 25) + 3 áreas pintáveis (moradia, cultivo, defesa)
- Até 20 sobreviventes gerados, com 8 traços e 5 tarefas (coletar, cultivar, cozinhar, construir, vigiar)
- Moral da comunidade e cartões de pedido
- 3 tipos de zumbi, hordas a cada 7 dias
- 2 marcos: Torre de rádio (fim da fase 3) e Subestação (começo da fase 4)
- Salvar e carregar, tutorial curto
- Build de Windows pelo CI

### Não entra (pós-MVP)
Várias cidades e mapa de viagem, facções humanas, comércio entre comunidades, veículos, estações do ano e clima, crianças crescendo, multiplayer, modo criativo livre.

### Meta do MVP
Um jogador novo consegue ir do primeiro dia até ligar a torre de rádio em 2 a 3 horas, e quer continuar jogando.

## 11. Roteiro em marcos

Estimativas para uma pessoa com ajuda de IA, trabalhando com frequência. Cada marco termina com uma build jogável pelo CI.

| Marco | Duração | Entrega | Pronto quando |
|---|---|---|---|
| **M0. Fundação** | 2 semanas | Repositório do jogo, mapa de teste com 5 kits, LODs e ruínas geradas por script, câmera a pé e de cima | Dá para andar pela cidade e trocar de câmera a 60 fps |
| **M1. Sobrevivente** | 5 semanas | Necessidades, saque, inventário, combate corpo a corpo, 1 tipo de zumbi, dia/noite | Dá para sobreviver 3 dias sozinho e morrer de jeitos diferentes |
| **M2. Abrigo** | 5 semanas | Ocupar e barricar, reparar ruínas, estações de trabalho, kit 25 (construções), 1ª horda | Uma base barricada aguenta (ou não) uma horda |
| **M3. Comunidade** | 6 semanas | Sobreviventes com IA de tarefas, moral, cartões de pedido, recrutamento | 5 moradores vivem sozinhos por 3 dias sem o jogador mandar |
| **M4. Prefeito** | 5 semanas | Modo prefeito completo: barra de categorias, áreas pintáveis, trilhas, serviços de água e energia, marcos | A base cresce de 5 para 20 pessoas pelo modo prefeito |
| **M5. MVP fechado** | 5 semanas | Mapa final, 3 tipos de zumbi, tutorial, balanceamento, som, salvar/carregar, personagens próprios | Testadores vão do dia 1 até a torre de rádio |

Total: cerca de 28 semanas (7 meses). Depois do MVP, a ordem sugerida é: fase 4 completa (vila), um segundo mapa com viagem, e facções humanas.

## 12. Riscos e como reduzir

| Risco | Como reduzir |
|---|---|
| Escopo crescer demais (dois gêneros num só) | Marcos fechados; nada da lista "não entra" antes do MVP |
| Desempenho com prédios em alto detalhe + hordas | LOD no M0, medir 60 fps a cada marco, hordas em MultiMesh |
| IA dos moradores ficar burra ou travar | IA por utilidade simples, com tela de depuração mostrando o que cada um "pensa" |
| Personagens e animações atrasarem tudo | Pacotes CC0 desde o M1; arte própria só no M5 |
| Balanceamento | Tudo por tabelas; simulação acelerada sem gráficos para testar 30 dias em segundos |

## 13. Próximos passos

1. Bruno revisa este plano e escolhe a câmera principal (a recomendação é o híbrido).
2. Criar o repositório do jogo e começar o **M0**.
3. Em paralelo, no pacote de assets: script de **ruínas** e de **LOD** para os kits, e o **kit 25** de construções de sobrevivência.
