# Catálogo de mobílias e loot

Gerado por `props/gerar_props.py` a partir de `mobilias/catalogo.json` e `loot/catalogo.json`. Medidas em metros (largura × altura × profundidade).

## Mobílias

| Item | Lote | Cômodo | Medidas | Revistar | Partes móveis | Uso no jogo | Triângulos |
|---|---|---|---|---|---|---|---|
| Geladeira duplex (`geladeira`) | 1 | Cozinha | 0,70 × 1,76 × 0,71 | 12 espaços: comida, agua, remedios | porta_geladeira, porta_freezer | barricada | 1780 |
| Fogão 4 bocas (`fogao`) | 1 | Cozinha | 0,56 × 0,98 × 0,64 | 4 espaços: comida, utensilios | gaveta, porta_forno | - | 4784 |
| Balcão com pia (`balcao_pia`) | 1 | Cozinha | 1,22 × 1,23 × 0,63 | 6 espaços: utensilios, limpeza, ferramentas | porta_esq, porta_dir | - | 2408 |
| Estante de aço (5 prateleiras) (`estante_metal`) | 1 | Depósito | 1,02 × 1,90 × 0,42 | 10 espaços: ferramentas, materiais, comida | - | - | 5264 |
| Guarda-roupa 2 portas (`guarda_roupa`) | 1 | Quarto | 1,05 × 2,00 × 0,61 | 10 espaços: roupas, tecido, mochila | porta_esq, porta_dir, gaveta | barricada | 2444 |
| Cômoda 3 gavetas (`comoda`) | 1 | Quarto | 0,93 × 0,85 × 0,47 | 6 espaços: roupas, remedios, pilhas | gaveta_1, gaveta_2, gaveta_3 | - | 2100 |
| Criado-mudo (`criado_mudo`) | 1 | Quarto | 0,47 × 0,56 × 0,42 | 3 espaços: remedios, pilhas, livros | gaveta | - | 1740 |
| Cama de casal (`cama_casal`) | 1 | Quarto | 1,48 × 1,05 × 1,98 | - | - | dormir | 11820 |
| Cama de solteiro (`cama_solteiro`) | 1 | Quarto | 0,98 × 1,05 × 1,98 | - | - | dormir | 10076 |
| Mesa de jantar (`mesa_jantar`) | 1 | Sala | 1,40 × 0,76 × 0,80 | - | - | barricada | 1820 |
| Cadeira de madeira (`cadeira`) | 1 | Sala | 0,42 × 0,95 × 0,48 | - | - | sentar | 1872 |
| Sofá 3 lugares (`sofa`) | 1 | Sala | 1,93 × 0,88 × 0,87 | 2 espaços: moedas, pilhas | - | barricada, dormir, sentar | 12624 |
| Armário de banheiro com espelho (`armario_banheiro`) | 1 | Banheiro | 0,52 × 0,70 × 0,17 | 4 espaços: remedios, higiene | porta_espelho | - | 348 |
| Caixote de madeira (`caixa_madeira`) | 1 | Depósito | 0,84 × 0,56 × 0,64 | 8 espaços: comida, materiais, ferramentas, armas | tampa | barricada | 1972 |
| Armário aéreo de cozinha (`armario_aereo`) | 2 | Cozinha | 0,82 × 0,64 × 0,37 | 6 espaços: comida, utensilios | porta_esq, porta_dir | - | 912 |
| Pia de coluna (`pia_banheiro`) | 2 | Banheiro | 0,54 × 1,00 × 0,45 | - | - | - | 2780 |
| Vaso sanitário com caixa (`vaso_sanitario`) | 2 | Banheiro | 0,40 × 0,81 × 0,63 | 1 espaços: remedios, moedas | assento, tampa_caixa | - | 2940 |
| Banheira (`banheira`) | 2 | Banheiro | 1,60 × 0,62 × 0,74 | - | - | - | 798 |
| Estante de livros (`estante_livros`) | 2 | Sala | 0,93 × 1,83 × 0,34 | 8 espaços: livros | - | barricada | 7000 |
| Rack com TV (`rack_tv`) | 2 | Sala | 1,40 × 1,18 × 0,45 | 3 espaços: pilhas, eletronicos | porta_esq | - | 912 |
| Poltrona (`poltrona`) | 2 | Sala | 0,87 × 0,98 × 0,85 | 1 espaços: moedas | - | sentar | 6272 |
| Escrivaninha com luminária (`escrivaninha`) | 2 | Escritório | 1,20 × 1,19 × 0,62 | 4 espaços: livros, pilhas, remedios | gaveta_1, gaveta_2, gaveta_3, gaveta_centro | - | 2256 |
| Berço (`berco`) | 2 | Quarto | 1,28 × 0,95 × 0,72 | 2 espaços: roupas, remedios | - | - | 4628 |
| Máquina de lavar (`maquina_lavar`) | 2 | Lavanderia | 0,60 × 0,85 × 0,61 | 3 espaços: roupas, limpeza | gaveta_sabao, porta | barricada | 2340 |
| Aquecedor a óleo (`aquecedor`) | 2 | Quarto | 0,51 × 0,60 × 0,29 | - | - | - | 6400 |
| Gôndola de supermercado (`gondola`) | 3 | Loja | 1,00 × 1,65 × 0,88 | 16 espaços: comida, agua, higiene, limpeza | - | - | 1568 |
| Balcão de caixa com registradora (`balcao_caixa`) | 3 | Loja | 1,84 × 1,15 × 0,64 | 4 espaços: moedas, pilhas, remedios | gaveta_dinheiro | barricada | 1064 |
| Freezer horizontal (`freezer_horizontal`) | 3 | Loja | 1,50 × 0,90 × 0,66 | 10 espaços: comida | tampa_esq, tampa_dir | - | 976 |
| Prateleira de pães (`prateleira_padaria`) | 3 | Loja | 1,22 × 1,63 × 0,52 | 6 espaços: comida | - | - | 12560 |
| Mesa de escritório (`mesa_escritorio`) | 3 | Escritório | 1,40 × 1,14 × 0,73 | 3 espaços: pilhas, livros, moedas | gaveta | - | 952 |
| Arquivo de aço 4 gavetas (`arquivo_aco`) | 3 | Escritório | 0,47 × 1,33 × 0,65 | 6 espaços: livros, mapas, moedas | gaveta_1, gaveta_2, gaveta_3, gaveta_4 | barricada | 1000 |
| Armário de vestiário (3 portas) (`armario_vestiario`) | 3 | Escritório | 0,90 × 1,85 × 0,52 | 9 espaços: roupas, mochila, armas, remedios | porta_1, porta_2, porta_3 | barricada | 984 |
| Maca hospitalar (`maca`) | 3 | Saúde | 0,75 × 1,90 × 1,93 | - | - | dormir | 2300 |
| Carrinho de compras (`carrinho_compras`) | 3 | Loja | 0,56 × 1,02 × 1,00 | 6 espaços: comida | - | barricada | 1544 |
| Bancada de trabalho com morsa (`bancada_trabalho`) | 4 | Oficina | 1,80 × 1,75 × 0,76 | 6 espaços: ferramentas, materiais | gaveta | - | 4724 |
| Fogareiro a gás de camping (`fogareiro`) | 4 | Abrigo | 0,75 × 0,21 × 0,34 | - | - | - | 996 |
| Beliche de abrigo (`beliche`) | 4 | Abrigo | 0,94 × 1,75 × 2,03 | - | - | dormir | 7568 |
| Mesa de rádio amador (`mesa_radio`) | 4 | Abrigo | 1,20 × 0,96 × 0,64 | - | - | - | 1320 |
| Gerador portátil a gasolina (`gerador`) | 4 | Oficina | 0,68 × 0,56 × 0,53 | - | - | - | 3332 |
| Tambor de 200 L (`tambor_200l`) | 4 | Depósito | 0,60 × 0,88 × 0,60 | 4 espaços: combustivel, agua, materiais | - | barricada | 1952 |
| Pallet de madeira (`pallet`) | 4 | Depósito | 1,20 × 0,14 × 0,80 | - | - | barricada | 1340 |
| Barricada de tábuas para porta (`barricada_porta`) | 5 | Barricadas e alarmes | 1,30 × 2,14 × 0,08 | - | tabua_1, tabua_2, tabua_3, tabua_4, tabua_5, tabua_6 | - | 2800 |
| Barricada de tábuas para janela (`barricada_janela`) | 5 | Barricadas e alarmes | 1,27 × 1,56 × 0,08 | - | tabua_1, tabua_2, tabua_3, tabua_4, tabua_5 | - | 2428 |
| Alarme de latas (`alarme_latas`) | 5 | Barricadas e alarmes | 1,06 × 0,79 × 0,11 | - | - | - | 3140 |
| Fogueira de pedras (`fogueira`) | 5 | Abrigo | 0,88 × 0,45 × 0,85 | - | - | - | 8200 |
| Colchão no chão (`colchao_chao`) | 5 | Abrigo | 1,41 × 0,27 × 2,19 | - | - | dormir | 3972 |
| Caixa de papelão de mudança (`caixa_papelao`) | 5 | Depósito | 0,50 × 0,37 × 0,40 | 4 espaços: utensilios, roupas, materiais | aba_esq, aba_dir, aba_frente, aba_tras | - | 208 |
| Lixeira de rua com rodas (`lixeira`) | 5 | Rua e quintal | 0,61 × 1,05 × 0,84 | 5 espaços: comida, utensilios, materiais | tampa | barricada | 3060 |
| Mala de viagem (`mala_viagem`) | 5 | Quarto | 0,75 × 0,25 × 0,52 | 5 espaços: roupas, remedios, utensilios | tampa | - | 2696 |
| Pilha de sucata (`pilha_sucata`) | 5 | Rua e quintal | 1,70 × 0,59 × 1,64 | - | - | - | 4040 |
| Toco de rachar lenha (`toco_lenha`) | 5 | Rua e quintal | 1,09 × 0,50 × 0,74 | - | - | - | 1668 |
| Pichação "NÃO ENTRE" (`pichacao_nao_entre`) | 6 | Sinais do fim do mundo | 1,80 × 0,90 × 0,00 | - | - | - | 12 |
| Pichação "INFECTADOS LÁ DENTRO" (`pichacao_infectados`) | 6 | Sinais do fim do mundo | 1,80 × 0,90 × 0,00 | - | - | - | 12 |
| Pichação "FOMOS PARA A IGREJA" (`pichacao_igreja`) | 6 | Sinais do fim do mundo | 1,80 × 0,90 × 0,00 | - | - | - | 12 |
| Marca de busca em X na porta (`marca_busca`) | 6 | Sinais do fim do mundo | 0,70 × 0,70 × 0,00 | - | - | - | 12 |
| Riscos de contagem de dias (`contagem_dias`) | 6 | Sinais do fim do mundo | 1,00 × 0,50 × 0,00 | - | - | - | 12 |
| Mancha de sangue seco (`mancha_sangue`) | 6 | Sinais do fim do mundo | 1,20 × 0,00 × 1,20 | - | - | - | 12 |
| Cacos de vidro no chão (`cacos_vidro`) | 6 | Sinais do fim do mundo | 1,27 × 0,03 × 1,20 | - | - | - | 748 |
| Louça quebrada (`louca_quebrada`) | 6 | Sinais do fim do mundo | 0,86 × 0,08 × 0,76 | - | - | - | 844 |
| Papéis espalhados (`papeis_espalhados`) | 6 | Sinais do fim do mundo | 1,58 × 0,01 × 1,44 | - | - | - | 212 |
| Cadeira quebrada (`cadeira_quebrada`) | 6 | Sinais do fim do mundo | 1,66 × 0,42 × 0,44 | - | - | - | 490 |
| Barricada arrombada (`barricada_arrombada`) | 6 | Sinais do fim do mundo | 1,38 × 2,18 × 1,29 | - | - | - | 2760 |
| Mural de desaparecidos (`mural_desaparecidos`) | 6 | Sinais do fim do mundo | 1,20 × 0,90 × 0,04 | - | - | - | 452 |
| Cartaz de evacuação (`cartaz_evacuacao`) | 6 | Sinais do fim do mundo | 0,50 × 0,70 × 0,01 | - | - | - | 132 |
| Carro abandonado (`carro_abandonado`) | 6 | Rua e quintal | 1,92 × 1,41 × 4,51 | 6 espaços: combustivel, comida, ferramentas, mapas | porta | - | 5540 |
| Carrinho de bebê virado (`carrinho_bebe`) | 6 | Rua e quintal | 1,85 × 0,60 × 1,14 | 2 espaços: roupas, comida | - | - | 4436 |
| Bicicleta caída (`bicicleta`) | 6 | Rua e quintal | 1,03 × 0,58 × 1,70 | - | - | - | 2592 |
| Cone de trânsito (`cone_transito`) | 6 | Rua e quintal | 0,38 × 0,72 × 0,38 | - | - | - | 428 |
| Cavalete de bloqueio (`cavalete_bloqueio`) | 6 | Rua e quintal | 1,20 × 1,10 × 0,63 | - | - | barricada | 312 |
| Fita de isolamento com cones (`fita_isolamento`) | 6 | Rua e quintal | 3,38 × 0,72 × 0,39 | - | - | - | 1192 |
| Hidrante de calçada (`hidrante`) | 6 | Rua e quintal | 0,38 × 0,74 × 0,32 | - | - | - | 1804 |
| Telefone público (`orelhao`) | 6 | Rua e quintal | 0,90 × 2,02 × 0,50 | - | - | - | 4024 |
| Banco de praça (`banco_praca`) | 6 | Rua e quintal | 1,80 × 0,89 × 0,63 | - | - | sentar | 472 |
| Lixo espalhado na calçada (`lixo_espalhado`) | 6 | Rua e quintal | 1,64 × 0,53 × 1,48 | 1 espaços: comida | - | - | 2748 |
| Varal com roupas (`varal_roupas`) | 6 | Rua e quintal | 2,87 × 1,90 × 0,60 | 3 espaços: roupas | - | - | 1768 |
| Churrasqueira de quintal (`churrasqueira`) | 6 | Rua e quintal | 0,60 × 1,06 × 0,63 | - | tampa | - | 2192 |
| Cerca de madeira quebrada (`cerca_quebrada`) | 6 | Rua e quintal | 2,09 × 1,12 × 1,10 | - | - | - | 814 |
| Mangueira de jardim enrolada (`mangueira_jardim`) | 6 | Rua e quintal | 0,80 × 0,04 × 0,82 | - | - | - | 4324 |

## Loot

| Item | Lote | Categoria | Recurso | Rende | Peso | Empilha | Efeito | Aparece em |
|---|---|---|---|---|---|---|---|---|
| Lata de feijão (`lata_feijao`) | 1 | Comida | comida | 1 | 0,45 kg | 10 | fome -25 | supermercado, casas, galeria, diner, armazem |
| Lata de sardinha (`lata_sardinha`) | 1 | Comida | comida | 1 | 0,13 kg | 12 | fome -15 | supermercado, casas, diner |
| Pacote de arroz 1 kg (`pacote_arroz`) | 1 | Comida | comida | 2 | 1,0 kg | 5 | precisa cozinhar: rende 4 refeições | supermercado, casas, armazem, padaria |
| Caixa de flocos de milho (`caixa_cereal`) | 1 | Comida | comida | 1 | 0,3 kg | 4 | fome -20 | supermercado, casas, escolinha |
| Garrafa de água 1,5 L (`garrafa_agua`) | 1 | Água | agua | 1 | 1,55 kg | 6 | sede -40 | supermercado, casas, posto, diner, galeria |
| Galão de água 5 L (`galao_agua`) | 1 | Água | agua | 4 | 5,2 kg | 1 | sede -40 por uso, 5 usos | supermercado, posto, quartel, galeria |
| Kit de primeiros socorros (`kit_medico`) | 1 | Remédios | remedios | 6 | 0,8 kg | 1 | cura 60 e para sangramento | quartel, escolinha, casas, motel, galeria |
| Frasco de comprimidos (`frasco_remedio`) | 1 | Remédios | remedios | 3 | 0,08 kg | 10 | cura doença / alivia dor | casas, motel, quartel, galeria |
| Rolo de atadura (`atadura`) | 1 | Remédios | remedios | 1 | 0,03 kg | 10 | para sangramento | casas, quartel, escolinha, motel |
| Martelo de unha (`martelo`) | 1 | Ferramentas | ferramenta | 4 | 0,6 kg | 1 | constrói e repara; arma corpo a corpo leve (dano 20) | casas, garagem, armazem, quartel |
| Pé de cabra (`pe_de_cabra`) | 1 | Armas improvisadas | ferramenta | 5 | 1,2 kg | 1 | abre portas trancadas e caixotes; arma corpo a corpo (dano 30) | garagem, quartel, estacao, armazem |
| Machado (`machado`) | 1 | Armas improvisadas | ferramenta | 8 | 1,6 kg | 1 | corta lenha e arromba; arma corpo a corpo forte (dano 45) | quartel, armazem, casa_de_campo, garagem |
| Chave inglesa (`chave_inglesa`) | 1 | Ferramentas | ferramenta | 3 | 0,45 kg | 1 | desmonta sucata e repara geradores (dano 15) | garagem, posto, quartel, casas |
| Lanterna (`lanterna`) | 1 | Ferramentas | ferramenta | 4 | 0,3 kg | 1 | luz na mão (gasta pilhas) | casas, quartel, posto, correios |
| Taco de madeira (`taco_madeira`) | 1 | Armas improvisadas | arma | 3 | 0,9 kg | 1 | arma corpo a corpo de alcance médio (dano 25) | casas, escolinha, garagem |
| Tábua de madeira (`tabua`) | 1 | Materiais de construção | madeira | 1 | 2,0 kg | 10 | barricadas e construção (1 madeira) | armazem, casas, estacao, quartel, deposito |
| Caixa de pregos (`caixa_pregos`) | 1 | Materiais de construção | sucata | 2 | 0,5 kg | 5 | construção: 20 pregos | armazem, garagem, casas, deposito |
| Fita adesiva prata (`fita_adesiva`) | 1 | Materiais de construção | sucata | 2 | 0,2 kg | 5 | repara armas e barricadas; ingrediente de receitas | casas, garagem, galeria, correios |
| Chapa de metal ondulada (`chapa_metal`) | 1 | Materiais de construção | sucata | 2 | 4,0 kg | 4 | construção: 2 sucata (muros e telhados) | armazem, posto, estacao, quartel |
| Cano de ferro (`cano_metal`) | 1 | Armas improvisadas | sucata | 2 | 1,4 kg | 4 | 1 sucata ou arma corpo a corpo (dano 22) | garagem, armazem, estacao, posto |
| Galão de gasolina 20 L (`galao_gasolina`) | 1 | Combustível | combustivel | 10 | 16,0 kg | 1 | abastece gerador (8 horas) | posto, garagem, quartel, armazem |
| Cartela de pilhas AA (`pilhas`) | 1 | Energia | energia | 3 | 0,1 kg | 10 | 4 cargas para lanterna e rádio | casas, correios, galeria, posto, supermercado |
| Mochila (`mochila`) | 2 | Roupas e equipamento | equipamento | 1 | 0,9 kg | 1 | +8 espaços no inventário | casas, escolinha, motel, estacao |
| Pilha de roupas dobradas (`roupas`) | 2 | Roupas e equipamento | tecido | 2 | 1,2 kg | 3 | aquece à noite; vira atadura ou tecido para receitas | casas, motel, galeria |
| Sabonete embrulhado (`sabao`) | 2 | Higiene | higiene | 1 | 0,09 kg | 10 | evita doença na base (saneamento) | casas, motel, supermercado |
| Livro técnico (`livro`) | 2 | Utensílios | conhecimento | 1 | 0,6 kg | 5 | pesquisa: desbloqueia projetos | biblioteca, escolinha, casas, correios |
| Rádio portátil (`radio_portatil`) | 2 | Luz e eletrônicos | equipamento | 1 | 0,9 kg | 1 | ouve chamados de sobreviventes | casas, correios, quartel, posto |
| Vela e caixa de fósforos (`vela_fosforos`) | 2 | Luz e eletrônicos | luz | 1 | 0,15 kg | 6 | luz sem pilha por 4 horas; acende fogueira | casas, igreja, supermercado, motel |
| Isqueiro (`isqueiro`) | 2 | Luz e eletrônicos | ferramenta | 1 | 0,02 kg | 10 | acende fogueira e molotov (muitos usos) | casas, posto, diner, motel |
| Garrafa de vidro vazia (`garrafa_vidro`) | 2 | Utensílios | sucata | 1 | 0,4 kg | 4 | guarda água fervida; ingrediente do molotov | casas, diner, galeria, supermercado |
| Panela com tampa (`panela`) | 2 | Utensílios | ferramenta | 2 | 1,1 kg | 1 | cozinhar na fogueira; ferver água | casas, diner, padaria, motel |
| Faca de cozinha (`faca_cozinha`) | 2 | Armas improvisadas | arma | 2 | 0,15 kg | 1 | arma rápida e silenciosa; corta comida e tecido (dano 18) | casas, diner, padaria |
| Caixa de leite longa vida (`caixa_leite`) | 3 | Comida | comida | 1 | 1,05 kg | 6 | fome -10, sede -15 | supermercado, casas, diner, padaria |
| Saco de farinha 5 kg (`saco_farinha`) | 3 | Comida | comida | 8 | 5,0 kg | 1 | padaria da base: rende 20 pães | padaria, supermercado, armazem |
| Saco de sementes (`saco_sementes`) | 3 | Agricultura | sementes | 10 | 1,0 kg | 4 | planta 1 canteiro da horta | armazem, supermercado, casa_de_campo |
| Lata de milho (`lata_milho`) | 3 | Comida | comida | 1 | 0,3 kg | 10 | fome -20 | supermercado, casas, diner, armazem |
| Seringa com antibiótico (`seringa`) | 3 | Remédios | remedios | 5 | 0,02 kg | 10 | cura infecção (raro) | quartel, enfermaria, casas |
| Máscara de proteção (`mascara`) | 3 | Roupas e equipamento | equipamento | 1 | 0,05 kg | 10 | reduz chance de doença ao limpar prédios | quartel, casas, enfermaria, galeria |
| Lata de costura (`kit_costura`) | 3 | Remédios | tecido | 2 | 0,3 kg | 3 | sutura ferimentos; conserta roupas e mochilas | casas, motel, galeria |
| Bateria de carro (`bateria_carro`) | 3 | Energia | energia | 20 | 15,0 kg | 1 | guarda energia do gerador ou do cata-vento; liga o rádio | posto, garagem, quartel, estacao |
| Arco e flechas (`arco`) | 4 | Armas improvisadas | arma | 1 | 1,0 kg | 1 | arma silenciosa à distância (flechas reaproveitáveis) (dano 35) | casa_de_campo, galeria, armazem |
| Lança improvisada (`lanca`) | 4 | Armas improvisadas | arma | 1 | 1,4 kg | 1 | alcance longo para manter zumbis longe (receita: cabo + faca + fita) (dano 32) | quartel, casas |
| Facão (`facao`) | 4 | Armas improvisadas | ferramenta | 5 | 0,7 kg | 1 | corta mato e arma forte e silenciosa (dano 38) | casa_de_campo, armazem, garagem |
| Serrote (`serrote`) | 4 | Ferramentas | ferramenta | 4 | 0,6 kg | 1 | corta tábuas: dobra a madeira de móveis desmontados | garagem, armazem, casas |
| Pá (`pa`) | 4 | Agricultura | ferramenta | 4 | 1,8 kg | 1 | cava hortas, valas e covas; arma pesada (dano 26) | armazem, casa_de_campo, garagem, quartel |
| Enxada (`enxada`) | 4 | Agricultura | ferramenta | 4 | 1,5 kg | 1 | prepara canteiros da horta (+50% colheita) (dano 28) | armazem, casa_de_campo |
| Rolo de corda (`corda`) | 4 | Materiais de construção | material | 1 | 1,5 kg | 3 | armadilhas, escalar e amarrar barricadas (10 m) | armazem, quartel, garagem, estacao |
| Rolo de arame farpado (`arame_farpado`) | 4 | Materiais de construção | sucata | 3 | 6,0 kg | 1 | defesa: segura e fere zumbis no muro | armazem, casa_de_campo, quartel |
| Saco de areia (`saco_areia`) | 4 | Materiais de construção | material | 1 | 18,0 kg | 1 | defesa: 3 sacos = 1 m de trincheira à prova de mordida | quartel, armazem, estacao |
| Caixa de peças de motor (`peca_motor`) | 4 | Energia | pecas | 1 | 2,5 kg | 2 | repara o gerador e a subestação (marco da fase 4) | posto, garagem, estacao |
| Feixe de lenha (`lenha`) | 5 | Materiais de construção | madeira | 2 | 4,0 kg | 5 | queima 2 h na fogueira ou rende 2 madeira | armazem, padaria, casas, quartel, abrigo |
| Pacote de salgadinho (`salgadinho`) | 5 | Comida | comida | 1 | 0,1 kg | 8 | fome -10, sede +5 (leve, não estraga) | posto, supermercado, diner, galeria, casas |
| Barra de chocolate (`barra_chocolate`) | 5 | Comida | comida | 1 | 0,09 kg | 10 | fome -10 e ânimo +5 | posto, supermercado, galeria, casas, escolinha |
| Cantil de alumínio (`cantil`) | 5 | Água | equipamento | 1 | 0,35 kg | 1 | leva 1 L de água; pode ir ao fogo para ferver | quartel, casas, armazem, galeria |
| Saco de dormir enrolado (`saco_dormir`) | 5 | Roupas e equipamento | equipamento | 1 | 1,6 kg | 1 | dormir em qualquer lugar (recupera 85% da energia) | casas, armazem, quartel, galeria |
| Molho de chaves com etiqueta (`chave_casa`) | 5 | Chaves e pistas | chave | 1 | 0,05 kg | 1 | abre uma porta trancada (a casa escrita na etiqueta) | casas, motel, escritorio, quartel |
| Mapa da cidade dobrado (`mapa_cidade`) | 5 | Chaves e pistas | mapa | 1 | 0,08 kg | 1 | revela os prédios do bairro no mapa do jogo | posto, correios, estacao, casas, biblioteca |
| Bilhete de sobrevivente (`bilhete`) | 5 | Chaves e pistas | pista | 1 | 0,01 kg | 1 | pista do 1º sobrevivente: marca um encontro no mapa (fim da fase 1) | casas, igreja, posto, escolinha, supermercado |
