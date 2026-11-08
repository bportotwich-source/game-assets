# Mobílias e itens de loot

Modelos **originais**, gerados por script (`gerar_props.py`, Python + trimesh, com a biblioteca de alto detalhe `scripts/detalhe`), para mobiliar os kits e servir de saque no jogo **Recomeço** (`docs/plano-jogo-sobrevivencia.md`).
Ficam separados de `props/decoracao/` (pacote de terceiros da PR #48): aqui tudo é feito do zero e pode ser usado sem restrição.

```
props/
  gerar_props.py        gera tudo:  python props/gerar_props.py   (ou só alguns ids: python props/gerar_props.py geladeira sofa)
  CATALOGO.md           tabelas em português (gerado)
  mobilias/<id>.glb     mobilias/catalogo.json
  loot/<id>.glb         loot/catalogo.json
  veiculos/             carros em peças que viram loot, porta-malas e ferramentas de oficina (veiculos/README.md, design em docs/veiculos.md)
```

## Convenções

- Y para cima, 1 unidade = 1 m, frente para **+Z**, medidas reais (o jogador tem 1,8 m, ver `PADRAO_METRICAS.md`).
- `montagem: floor`: pivô no centro da base. `montagem: wall`: pivô no centro de baixo da face de trás (armário de banheiro; `altura_sugerida_m` diz onde pendurar).
- Loot fica **deitado na pose de repouso**, pivô no centro da base, pronto para pôr numa prateleira ou no chão. Ferramentas e armas têm `pega`: o ponto (m) onde a mão segura.
- **Partes móveis** (portas, gavetas, tampas) são nós separados do GLB, com a origem na dobradiça. O catálogo diz o que fazer com cada uma:
  - `tipo: porta` ou `tampa`: girar `abre_graus` em torno do `eixo` (`x`, `y` ou `z`) do próprio nó.
  - `tipo: gaveta`: deslizar o vetor `desliza` (m).
  - `tipo: tabua` (barricadas): tábua pregada que o jogo derruba quando a barricada perde vida; `ordem` diz qual cai primeiro (1) e `vida` quanto cada uma aguenta.
  - No Godot: `var n = cena.get_node("porta_geladeira"); n.rotation.y = deg_to_rad(110)` (animar com um Tween).
- Materiais com nome (`madeira`, `esmalte`, `inox`, `tecido_sofa`, ...) para trocar cor na engine. Madeira, tecidos, papelão, ferrugem e granito têm textura PBR (cor + normal + ORM). Rótulos de latas e caixas são artes próprias com marcas inventadas (Vale Verde, Bom Prato, Mar Azul, Fonte Clara...).
- Campos de jogo no catálogo:
  - mobílias: `conteiner` (pode ser revistado), `slots`, `saque` (grupos da tabela de saque), `barricada` (dá para empurrar contra uma porta), `deitar`, `sentar`, `estacao`, `comodos`; barricadas têm `vao`/`vao_m` (largura, altura e altura de início do vão que cobrem), `constroi` e `ferramenta`; pontos de recurso têm `coleta` (recurso, total, ferramenta, segundos por unidade).
  - loot: `recurso` (os 6 do MVP: comida, agua, madeira, sucata, remedios, combustivel; ou ferramenta/arma/energia), `valor` (quanto rende), `peso_kg`, `empilha`, `efeito`, `onde` (prédios), `arma` e `dano`.

## Lotes

275 itens no total (206 mobílias e 69 itens de loot). O campo `lote` do catálogo diz de qual lote é cada um.

| Lote | Mobílias | Loot |
|---|---|---|
| 1. Básico | geladeira duplex, fogão 4 bocas, balcão com pia, estante de aço (5 prateleiras), guarda-roupa 2 portas, cômoda 3 gavetas, criado-mudo, cama de casal, cama de solteiro, mesa de jantar, cadeira de madeira, sofá 3 lugares, armário de banheiro com espelho, caixote de madeira | lata de feijão, lata de sardinha, pacote de arroz 1 kg, caixa de flocos de milho, garrafa de água 1,5 L, galão de água 5 L, kit de primeiros socorros, frasco de comprimidos, rolo de atadura, martelo de unha, pé de cabra, machado, chave inglesa, lanterna, taco de madeira, tábua de madeira, caixa de pregos, fita adesiva prata, chapa de metal ondulada, cano de ferro, galão de gasolina 20 L, cartela de pilhas AA |
| 2. Casa completa | armário aéreo de cozinha, pia de coluna, vaso sanitário com caixa, banheira, estante de livros, rack com TV, poltrona, escrivaninha com luminária, berço, máquina de lavar, aquecedor a óleo | mochila, pilha de roupas dobradas, sabonete embrulhado, livro técnico, rádio portátil, vela e caixa de fósforos, isqueiro, garrafa de vidro vazia, panela com tampa, faca de cozinha |
| 3. Comércio e serviços | gôndola de supermercado, balcão de caixa com registradora, freezer horizontal, prateleira de pães, mesa de escritório, arquivo de aço 4 gavetas, armário de vestiário (3 portas), maca hospitalar, carrinho de compras | caixa de leite longa vida, saco de farinha 5 kg, saco de sementes, lata de milho, seringa com antibiótico, máscara de proteção, lata de costura, bateria de carro |
| 4. Sobrevivência e oficina | bancada de trabalho com morsa, fogareiro a gás de camping, beliche de abrigo, mesa de rádio amador, gerador portátil a gasolina, tambor de 200 L, pallet de madeira | arco e flechas, lança improvisada, facão, serrote, pá, enxada, rolo de corda, rolo de arame farpado, saco de areia, caixa de peças de motor |
| 5. Fase 1 (Sozinho) | barricada de tábuas para porta, barricada de tábuas para janela, alarme de latas, fogueira de pedras, colchão no chão, caixa de papelão de mudança, lixeira de rua com rodas, mala de viagem, pilha de sucata, toco de rachar lenha | feixe de lenha, pacote de salgadinho, barra de chocolate, cantil de alumínio, saco de dormir enrolado, molho de chaves com etiqueta, mapa da cidade dobrado, bilhete de sobrevivente |
| 6. Sinais do fim e rua | pichação "NÃO ENTRE", pichação "INFECTADOS LÁ DENTRO", pichação "FOMOS PARA A IGREJA", marca de busca em X na porta, riscos de contagem de dias, mancha de sangue seco, cacos de vidro no chão, louça quebrada, papéis espalhados, cadeira quebrada, barricada arrombada, mural de desaparecidos, cartaz de evacuação, carro abandonado, carrinho de bebê virado, bicicleta caída, cone de trânsito, cavalete de bloqueio, fita de isolamento com cones, hidrante de calçada, telefone público, banco de praça, lixo espalhado na calçada, varal com roupas, churrasqueira de quintal, cerca de madeira quebrada, mangueira de jardim enrolada | - |
| 7. Vida de antes | quadro de família na parede, bola de futebol murcha, casinha de cachorro vazia, vaso com planta morta, relógio de parede parado, calendário na data do surto, tV de tubo com tela rachada, abajur, tapete de sala, vitrola com discos, fruteira com frutas podres, desenho de criança na parede, pilha de livros no chão | porta-retrato de família, ursinho de pelúcia |
| 8. Abrigo vivo e construções | lampião a querosene, cordão de luzes, mapa da cidade com alfinetes, quadro de tarefas da comunidade, estoque de latas empilhadas, galões de água enfileirados, canteiro de horta, balde com pé de tomate, coletor de água da chuva, muro de sucata, portão de sucata, torre de vigia | - |
| 9. Prédios públicos | banco de igreja, altar com toalha, castiçal alto, púlpito de madeira, harmônio de pedal, pia batismal de pedra, quadro de hinos, estante alta de biblioteca (dupla face), mesa de leitura com luminárias verdes, fichário de catálogo, carrinho de livros, globo terrestre de mesa, carteira escolar com banco, mesa do professor, lousa com giz, estufa a lenha, cabideiro com lancheiras, caixa de correio de rua, carrinho de correspondência, balança de balcão, escaninho de triagem de cartas, mesa com máquina de escrever, armário de armas, quadro de procurados e avisos, banco de espera (3 lugares), cadeira de rodas, suporte de soro, armário de remédios com vidro, biombo hospitalar, balança médica com régua, carrinho de emergência, parede de cofres de aluguel, pedestais de fila com cordão, armário de equipamento de bombeiro, carretel de mangueira de incêndio | saco de correspondência, extintor de incêndio |
| 10. Comida e comércio | banqueta giratória de balcão, mesa de booth com dois sofás, jukebox, chapa de lanchonete, vitrine giratória de tortas, máquina de refrigerante de balcão, fritadeira industrial, masseira de padaria, carrinho de assadeiras, expositor de óleo de motor, freezer de sorvete com tampa de vidro, calibrador de pneus, pilha de pneus, geladeira vertical de bebidas, cesta de compras, fileira de poltronas de cinema, carrinho de pipoca, projetor de filme com rolos, balcão de recepção com quadro de chaves, carrinho de bagagem de hotel, carrinho de camareira, frigobar, quadro de horários de partida, relógio de plataforma (dupla face), máquina de lanches, carrinho de carga de plataforma | saco de pão francês |
| 11. Trabalho | elevador automotivo de duas colunas, carrinho de ferramentas com gavetas, compressor de ar com tanque, painel de ferramentas na parede, totem de ofertas da concessionária, torno mecânico, esteira de roletes, relógio de ponto com cartões, paleteira manual, pilha de tábuas da serraria, pilha de toras, cavalete de serrar lenha, serra de fita industrial, fardo de feno, cocho de água para animais, galinheiro de tela, carrinho de mão, tarro de leite, espantalho, estante porta-pallet, empilhadeira, carcaça de carro depenada, pilha de calotas e peças, bomba d'água manual | macaco jacaré, saco de ração |
| 12. Lazer | canoa no cavalete, boia salva-vidas na parede, balanço de parquinho, barraca de camping abandonada, guarda-sol fechado com base, telescópio refrator no tripé, carta celeste na parede, espreguiçadeira, cadeira alta de salva-vidas, escada de piscina, boia de piscina murcha, placa de regras da piscina, bandeirinha de buraco do minigolfe, estante de partitura, caixa de som de palco, microfone no pedestal, cadeira dobrável de plateia, poste de alto-falante do drive-in | remo de madeira, colete salva-vidas, skate, taco de minigolfe |

As versões completas das armas (fogo, arcos, facas, facão, lança), com partes, acessórios e animações, ficam em `props/armas/`; o arco, a lança e o facão daqui são o loot simples.

O lote 1 fica em `gerar_props.py`; os outros em `lote2.py` a `lote12.py`, que o gerador carrega com as mesmas funções e materiais (o laço vai até o lote 19). Para um lote novo, crie `lote13.py`; categorias novas entram no dicionário `NOMES` de `gerar_props.py`.

Os lotes 6 a 12 trazem os itens únicos de cada tipo de prédio. Quem os põe dentro dos prédios é `scripts/ambientacao/` (ver `ROTEIRO_AMBIENTACAO.md`).

Algumas mobílias trazem campos a mais para o jogo: `esconderijo` (vaso sanitário), `modulo_m` (gôndola, encaixa lado a lado), `empurrar` (carrinho), `vagas` (beliche), `desmontavel` (pallet), `usa` (rádio, gerador), `portatil` e `peso_kg` (fogareiro, gerador).
