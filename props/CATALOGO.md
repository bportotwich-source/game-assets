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
| Quadro de família na parede (`quadro_familia`) | 7 | Vida de antes | 0,60 × 0,45 × 0,03 | - | - | - | 236 |
| Bola de futebol murcha (`bola_futebol`) | 7 | Vida de antes | 0,22 × 0,19 × 0,22 | - | - | - | 320 |
| Casinha de cachorro vazia (`casinha_cachorro`) | 7 | Vida de antes | 1,34 × 0,98 × 1,26 | - | - | - | 3016 |
| Vaso com planta morta (`vaso_planta_morta`) | 7 | Vida de antes | 0,66 × 0,77 × 0,67 | - | - | - | 5680 |
| Relógio de parede parado (`relogio_parede`) | 7 | Vida de antes | 0,32 × 0,32 × 0,04 | - | - | - | 1236 |
| Calendário na data do surto (`calendario_parede`) | 7 | Vida de antes | 0,30 × 0,45 × 0,02 | - | - | - | 1004 |
| TV de tubo com tela rachada (`tv_tubo`) | 7 | Vida de antes | 0,66 × 0,85 × 0,64 | - | - | - | 492 |
| Abajur (`abajur`) | 7 | Vida de antes | 0,34 × 0,60 × 0,62 | - | - | - | 828 |
| Tapete de sala (`tapete_sala`) | 7 | Vida de antes | 2,10 × 0,01 × 1,40 | - | - | - | 732 |
| Vitrola com discos (`vitrola`) | 7 | Vida de antes | 1,04 × 0,74 × 0,51 | - | tampa | - | 824 |
| Fruteira com frutas podres (`fruteira_podre`) | 7 | Vida de antes | 0,44 × 0,29 × 0,34 | - | - | - | 2956 |
| Desenho de criança na parede (`desenho_crianca`) | 7 | Vida de antes | 0,30 × 0,23 × 0,00 | - | - | - | 24 |
| Pilha de livros no chão (`pilha_livros`) | 7 | Vida de antes | 0,51 × 0,26 × 0,39 | 2 espaços: livros | - | - | 448 |
| Lampião a querosene (`lampiao`) | 8 | Abrigo | 0,19 × 0,33 × 0,15 | - | - | - | 1028 |
| Cordão de luzes (`cordao_luzes`) | 8 | Abrigo | 3,01 × 0,32 × 0,10 | - | - | - | 2292 |
| Mapa da cidade com alfinetes (`mapa_alfinetes`) | 8 | Abrigo | 1,26 × 0,91 × 0,05 | - | - | - | 1548 |
| Quadro de tarefas da comunidade (`quadro_tarefas`) | 8 | Abrigo | 1,18 × 0,85 × 0,07 | - | - | - | 328 |
| Estoque de latas empilhadas (`estoque_latas`) | 8 | Abrigo | 0,39 × 0,44 × 0,15 | 8 espaços: comida | - | - | 7840 |
| Galões de água enfileirados (`galoes_fila`) | 8 | Abrigo | 1,24 × 0,35 × 0,36 | 4 espaços: agua | - | - | 2124 |
| Canteiro de horta (`canteiro_horta`) | 8 | Abrigo | 1,90 × 0,75 × 0,90 | - | - | - | 9820 |
| Balde com pé de tomate (`vaso_tomate`) | 8 | Abrigo | 0,34 × 1,00 × 0,36 | - | - | - | 3948 |
| Coletor de água da chuva (`coletor_chuva`) | 8 | Abrigo | 1,04 × 1,55 × 1,04 | - | - | - | 1540 |
| Muro de sucata (`muro_sucata`) | 8 | Abrigo | 2,05 × 2,12 × 0,10 | - | - | - | 4668 |
| Portão de sucata (`portao_sucata`) | 8 | Abrigo | 2,04 × 2,20 × 0,26 | - | folha_esq, folha_dir | - | 2084 |
| Torre de vigia (`torre_vigia`) | 8 | Abrigo | 2,12 × 4,95 × 2,34 | - | - | - | 2802 |
| Banco de igreja (`banco_igreja`) | 9 | Igreja | 2,97 × 0,94 × 0,87 | - | - | barricada, sentar | 648 |
| Altar com toalha (`altar`) | 9 | Igreja | 2,08 × 1,63 × 0,97 | 3 espaços: velas, tecido | - | - | 2696 |
| Castiçal alto (`castical`) | 9 | Igreja | 0,14 × 1,52 × 0,14 | - | - | - | 664 |
| Púlpito de madeira (`pulpito`) | 9 | Igreja | 0,80 × 1,25 × 0,80 | - | - | - | 184 |
| Harmônio de pedal (`harmonio`) | 9 | Igreja | 1,34 × 1,45 × 0,83 | - | - | - | 4008 |
| Pia batismal de pedra (`pia_batismal`) | 9 | Igreja | 0,68 × 0,96 × 0,68 | - | - | - | 792 |
| Quadro de hinos (`quadro_hinos`) | 9 | Igreja | 0,50 × 0,87 × 0,05 | - | - | - | 288 |
| Estante alta de biblioteca (dupla face) (`estante_biblioteca`) | 9 | Biblioteca | 1,00 × 2,25 × 0,64 | 6 espaços: livros | - | barricada | 2748 |
| Mesa de leitura com luminárias verdes (`mesa_leitura`) | 9 | Biblioteca | 2,40 × 1,16 × 1,00 | - | - | - | 1908 |
| Fichário de catálogo (`fichario_catalogo`) | 9 | Biblioteca | 1,04 × 1,24 × 0,54 | 2 espaços: mapas, papel | gaveta_1_3, gaveta_3_1 | - | 4572 |
| Carrinho de livros (`carrinho_livros`) | 9 | Biblioteca | 0,80 × 0,98 × 0,48 | 3 espaços: livros | - | - | 4384 |
| Globo terrestre de mesa (`globo_terrestre`) | 9 | Biblioteca | 0,33 × 0,41 × 0,30 | - | - | - | 3740 |
| Carteira escolar com banco (`carteira_escolar`) | 9 | Escola | 0,66 × 0,78 × 0,80 | 1 espaços: livros, papel | - | sentar | 632 |
| Mesa do professor (`mesa_professor`) | 9 | Escola | 1,30 × 0,91 × 0,78 | 4 espaços: livros, remedios, papel | gaveta_esq_1, gaveta_dir_1 | - | 2520 |
| Lousa com giz (`lousa_escola`) | 9 | Escola | 2,50 × 1,22 × 0,08 | - | - | - | 404 |
| Estufa a lenha (`estufa_lenha`) | 9 | Escola | 0,80 × 2,41 × 0,90 | - | portinhola | - | 1196 |
| Cabideiro com lancheiras (`cabide_lancheiras`) | 9 | Escola | 1,60 × 0,67 × 0,12 | 2 espaços: comida | - | - | 880 |
| Caixa de correio de rua (`caixa_correio_rua`) | 9 | Correios | 0,50 × 1,30 × 0,54 | 3 espaços: papel, mapas, pistas | portinhola | - | 566 |
| Carrinho de correspondência (`carrinho_correspondencia`) | 9 | Correios | 0,97 × 1,00 × 0,76 | 4 espaços: papel, roupas, pistas | - | - | 5668 |
| Balança de balcão (`balanca_correio`) | 9 | Correios | 0,36 × 0,32 × 0,30 | - | - | - | 404 |
| Escaninho de triagem de cartas (`estante_triagem`) | 9 | Correios | 1,84 × 1,63 × 0,66 | 3 espaços: papel, pistas, chaves | - | - | 1000 |
| Mesa com máquina de escrever (`mesa_maquina_escrever`) | 9 | Delegacia | 1,40 × 1,06 × 0,78 | 3 espaços: papel, chaves, armas | gaveta_1 | - | 2308 |
| Armário de armas (`armario_armas`) | 9 | Delegacia | 1,00 × 1,90 × 0,50 | 6 espaços: armas, municao | porta_esq, porta_dir | barricada | 1268 |
| Quadro de procurados e avisos (`quadro_procurados`) | 9 | Delegacia | 1,20 × 0,90 × 0,04 | - | - | - | 488 |
| Banco de espera (3 lugares) (`banco_espera`) | 9 | Delegacia | 1,90 × 0,86 × 0,53 | - | - | sentar | 352 |
| Cadeira de rodas (`cadeira_rodas`) | 9 | Saúde | 0,67 × 1,00 × 0,90 | - | - | sentar | 2180 |
| Suporte de soro (`suporte_soro`) | 9 | Saúde | 0,60 × 1,95 × 0,65 | - | - | - | 1424 |
| Armário de remédios com vidro (`armario_remedios`) | 9 | Saúde | 0,90 × 1,80 × 0,42 | 6 espaços: remedios | porta_esq, porta_dir | - | 2396 |
| Biombo hospitalar (`biombo`) | 9 | Saúde | 1,67 × 1,73 × 0,24 | - | - | - | 1320 |
| Balança médica com régua (`balanca_medica`) | 9 | Saúde | 0,40 × 2,00 × 0,55 | - | - | - | 400 |
| Carrinho de emergência (`carrinho_emergencia`) | 9 | Saúde | 0,90 × 1,09 × 0,59 | 5 espaços: remedios | gaveta_1 | - | 4180 |
| Parede de cofres de aluguel (`cofres_aluguel`) | 9 | Banco | 1,60 × 2,00 × 0,47 | 8 espaços: moedas, joias, pistas, remedios | cofre_2_4, cofre_5_7, cofre_6_2 | - | 10356 |
| Pedestais de fila com cordão (`pedestal_fila`) | 9 | Banco | 1,50 × 0,98 × 0,30 | - | - | - | 988 |
| Armário de equipamento de bombeiro (`armario_bombeiro`) | 9 | Quartel de bombeiros | 0,96 × 2,14 × 0,60 | 4 espaços: roupas, ferramentas, remedios | - | - | 3540 |
| Carretel de mangueira de incêndio (`carretel_mangueira`) | 9 | Quartel de bombeiros | 0,77 × 0,89 × 1,50 | - | - | - | 3284 |
| Banqueta giratória de balcão (`banqueta_giratoria`) | 10 | Diner e lanchonete | 0,41 × 0,79 × 0,41 | - | - | sentar | 1172 |
| Mesa de booth com dois sofás (`mesa_booth`) | 10 | Diner e lanchonete | 1,30 × 1,17 × 1,90 | - | - | sentar | 1312 |
| Jukebox (`jukebox`) | 10 | Diner e lanchonete | 0,90 × 1,57 × 0,65 | - | - | - | 3084 |
| Chapa de lanchonete (`chapa_lanchonete`) | 10 | Diner e lanchonete | 1,20 × 1,00 × 0,76 | - | - | - | 1496 |
| Vitrine giratória de tortas (`vitrine_tortas`) | 10 | Diner e lanchonete | 0,44 × 0,88 × 0,44 | 2 espaços: comida | - | - | 2152 |
| Máquina de refrigerante de balcão (`maquina_refrigerante`) | 10 | Diner e lanchonete | 0,70 × 0,70 × 0,75 | - | - | - | 780 |
| Fritadeira industrial (`fritadeira`) | 10 | Diner e lanchonete | 0,50 × 1,05 × 0,77 | - | - | - | 344 |
| Masseira de padaria (`masseira`) | 10 | Padaria | 0,70 × 1,25 × 0,79 | - | - | - | 1664 |
| Carrinho de assadeiras (`carrinho_assadeiras`) | 10 | Padaria | 0,56 × 1,72 × 0,78 | 4 espaços: comida | - | - | 21936 |
| Expositor de óleo de motor (`expositor_oleo`) | 10 | Posto | 0,93 × 1,50 × 0,47 | 3 espaços: combustivel, materiais | - | - | 4580 |
| Freezer de sorvete com tampa de vidro (`freezer_sorvete`) | 10 | Posto | 1,20 × 0,88 × 0,66 | 3 espaços: comida | tampa_1, tampa_2 | barricada | 224 |
| Calibrador de pneus (`calibrador_pneu`) | 10 | Posto | 0,54 × 1,65 × 0,40 | - | - | - | 1040 |
| Pilha de pneus (`pilha_pneus`) | 10 | Posto | 1,24 × 0,97 × 0,68 | - | - | barricada | 2688 |
| Geladeira vertical de bebidas (`geladeira_bebidas`) | 10 | Loja | 0,70 × 2,00 × 0,69 | 6 espaços: agua, comida | porta | barricada | 3324 |
| Cesta de compras (`cesta_compras`) | 10 | Loja | 0,49 × 0,35 × 0,31 | 2 espaços: comida, higiene | - | - | 624 |
| Fileira de poltronas de cinema (`poltronas_cinema`) | 10 | Cinema | 2,28 × 1,06 × 0,93 | - | - | sentar | 892 |
| Carrinho de pipoca (`carrinho_pipoca`) | 10 | Cinema | 0,90 × 1,85 × 0,68 | 2 espaços: comida, combustivel | - | - | 2082 |
| Projetor de filme com rolos (`projetor_filme`) | 10 | Cinema | 0,60 × 1,77 × 1,10 | - | - | - | 1812 |
| Balcão de recepção com quadro de chaves (`balcao_recepcao`) | 10 | Hotel e motel | 2,06 × 2,00 × 1,20 | 4 espaços: chaves, moedas, papel | - | - | 3972 |
| Carrinho de bagagem de hotel (`carrinho_bagagem`) | 10 | Hotel e motel | 1,00 × 1,62 × 0,60 | 4 espaços: roupas, remedios | - | - | 6316 |
| Carrinho de camareira (`carrinho_camareira`) | 10 | Hotel e motel | 1,48 × 1,25 × 0,50 | 4 espaços: higiene, roupas, tecido | - | - | 7212 |
| Frigobar (`frigobar`) | 10 | Hotel e motel | 0,48 × 0,55 × 0,51 | 2 espaços: comida, agua | porta | - | 964 |
| Quadro de horários de partida (`quadro_horarios`) | 10 | Estação e rodoviária | 1,90 × 1,00 × 0,08 | - | - | - | 56 |
| Relógio de plataforma (dupla face) (`relogio_estacao`) | 10 | Estação e rodoviária | 0,50 × 0,58 × 0,82 | - | - | - | 1116 |
| Máquina de lanches (`maquina_lanches`) | 10 | Estação e rodoviária | 0,90 × 1,80 × 0,82 | 4 espaços: comida, agua | - | barricada | 8624 |
| Carrinho de carga de plataforma (`carrinho_plataforma`) | 10 | Estação e rodoviária | 2,44 × 1,00 × 1,34 | 4 espaços: materiais, comida, roupas | - | - | 5608 |
| Elevador automotivo de duas colunas (`elevador_automotivo`) | 11 | Oficina | 3,71 × 3,22 × 1,82 | - | - | - | 1608 |
| Carrinho de ferramentas com gavetas (`carrinho_ferramentas`) | 11 | Oficina | 0,85 × 1,02 × 0,49 | 4 espaços: ferramentas, materiais | gaveta_1, gaveta_3, gaveta_5 | barricada | 4356 |
| Compressor de ar com tanque (`compressor_ar`) | 11 | Oficina | 1,21 × 0,81 × 0,77 | - | - | - | 3408 |
| Painel de ferramentas na parede (`painel_ferramentas`) | 11 | Oficina | 1,80 × 0,90 × 0,20 | 3 espaços: ferramentas | - | - | 6980 |
| Totem de ofertas da concessionária (`totem_ofertas`) | 11 | Concessionária | 0,72 × 1,85 × 0,50 | - | - | - | 196 |
| Torno mecânico (`torno_mecanico`) | 11 | Fábrica | 1,95 × 1,82 × 0,64 | - | - | - | 2004 |
| Esteira de roletes (`esteira_rolante`) | 11 | Fábrica | 2,00 × 1,08 × 0,64 | - | - | - | 1776 |
| Relógio de ponto com cartões (`relogio_ponto`) | 11 | Fábrica | 0,96 × 0,80 × 0,22 | - | - | - | 1328 |
| Paleteira manual (`paleteira`) | 11 | Armazém | 0,54 × 1,35 × 1,64 | - | - | - | 2142 |
| Pilha de tábuas da serraria (`pilha_tabuas`) | 11 | Serraria | 1,10 × 0,45 × 2,52 | - | - | barricada | 1564 |
| Pilha de toras (`pilha_toras`) | 11 | Serraria | 1,98 × 0,88 × 3,04 | - | - | - | 2064 |
| Cavalete de serrar lenha (`cavalete_serra`) | 11 | Serraria | 1,03 × 1,18 × 1,36 | - | - | - | 524 |
| Serra de fita industrial (`serra_fita`) | 11 | Serraria | 1,00 × 2,11 × 0,97 | - | - | - | 1532 |
| Fardo de feno (`fardo_feno`) | 11 | Fazenda | 0,90 × 0,41 × 0,61 | - | - | barricada, sentar | 2568 |
| Cocho de água para animais (`cocho`) | 11 | Fazenda | 1,80 × 0,55 × 0,70 | - | - | barricada | 260 |
| Galinheiro de tela (`galinheiro`) | 11 | Fazenda | 2,14 × 1,54 × 1,72 | - | portinhola | - | 4128 |
| Carrinho de mão (`carrinho_mao`) | 11 | Fazenda | 1,68 × 0,71 × 0,65 | 4 espaços: materiais, ferramentas | - | - | 1104 |
| Tarro de leite (`tarro_leite`) | 11 | Fazenda | 0,35 × 0,76 × 0,35 | 1 espaços: agua | - | - | 1200 |
| Espantalho (`espantalho`) | 11 | Fazenda | 1,36 × 1,85 × 0,60 | - | - | - | 14884 |
| Estante porta-pallet (`porta_pallet`) | 11 | Armazém | 2,74 × 3,60 × 1,24 | 8 espaços: materiais, comida, ferramentas | - | - | 28240 |
| Empilhadeira (`empilhadeira`) | 11 | Armazém | 1,20 × 2,50 × 3,00 | 2 espaços: combustivel | - | - | 6448 |
| Carcaça de carro depenada (`carcaca_carro`) | 11 | Ferro-velho | 4,46 × 1,30 × 1,76 | - | - | - | 1152 |
| Pilha de calotas e peças (`pilha_calotas`) | 11 | Ferro-velho | 1,32 × 0,42 × 0,89 | - | - | - | 3788 |
| Bomba d'água manual (`bomba_agua_manual`) | 11 | Fazenda | 0,90 × 1,25 × 1,29 | - | - | - | 1124 |
| Canoa no cavalete (`canoa`) | 12 | Casa de barcos | 4,80 × 1,06 × 0,87 | - | - | - | 1920 |
| Boia salva-vidas na parede (`boia_salva_vidas`) | 12 | Casa de barcos | 0,76 × 0,76 × 0,16 | - | - | - | 1214 |
| Balanço de parquinho (`balanco`) | 12 | Casa de barcos | 2,70 × 2,25 × 1,46 | - | - | - | 1536 |
| Barraca de camping abandonada (`barraca_camping`) | 12 | Casa de barcos | 2,75 × 1,18 × 1,50 | 3 espaços: roupas, comida, remedios | - | dormir | 4440 |
| Guarda-sol fechado com base (`guarda_sol`) | 12 | Piscina | 0,50 × 2,34 × 0,50 | - | - | - | 620 |
| Telescópio refrator no tripé (`telescopio`) | 12 | Observatório | 1,33 × 1,67 × 1,01 | - | - | - | 1384 |
| Carta celeste na parede (`mapa_estrelas`) | 12 | Observatório | 1,26 × 0,91 × 0,03 | - | - | - | 56 |
| Espreguiçadeira (`espreguicadeira`) | 12 | Piscina | 0,67 × 0,88 × 1,81 | - | - | barricada, dormir | 1048 |
| Cadeira alta de salva-vidas (`cadeira_salva_vidas`) | 12 | Piscina | 1,32 × 2,92 × 1,32 | - | - | sentar | 800 |
| Escada de piscina (`escada_piscina`) | 12 | Piscina | 0,59 × 1,99 × 0,56 | - | - | - | 640 |
| Boia de piscina murcha (`boia_piscina`) | 12 | Piscina | 0,94 × 0,23 × 0,94 | - | - | - | 1008 |
| Placa de regras da piscina (`placa_regras_piscina`) | 12 | Piscina | 0,54 × 0,71 × 0,03 | - | - | - | 184 |
| Bandeirinha de buraco do minigolfe (`bandeira_buraco`) | 12 | Minigolfe | 0,60 × 0,75 × 0,60 | - | - | - | 536 |
| Estante de partitura (`estante_partitura`) | 12 | Concha acústica | 0,54 × 1,47 × 0,50 | - | - | - | 208 |
| Caixa de som de palco (`caixa_som`) | 12 | Concha acústica | 1,34 × 0,95 × 1,02 | - | - | barricada | 1032 |
| Microfone no pedestal (`microfone_pedestal`) | 12 | Concha acústica | 0,75 × 1,51 × 0,53 | - | - | - | 556 |
| Cadeira dobrável de plateia (`cadeira_dobravel`) | 12 | Concha acústica | 0,44 × 0,86 × 0,45 | - | - | sentar | 336 |
| Poste de alto-falante do drive-in (`poste_som_drivein`) | 12 | Drive-in | 0,73 × 1,27 × 0,53 | - | - | - | 876 |
| Armário de armas de madeira com tela (`armario_armas_abrigo`) | 14 | Armazenamento do abrigo | 1,15 × 2,10 × 0,86 | 12 espaços: armas, municao | porta_esq, porta_dir | barricada | 26644 |
| Cofre de armas de aço (`cofre_armas`) | 14 | Armazenamento do abrigo | 0,76 × 1,55 × 0,60 | 14 espaços: armas, municao, moedas | porta | - | 4292 |
| Suporte de parede para armas (`rack_armas_parede`) | 14 | Armazenamento do abrigo | 1,10 × 1,00 × 0,11 | - | - | - | 1952 |
| Prateleira de tábuas e tijolos (`prateleira_improvisada`) | 14 | Armazenamento do abrigo | 1,49 × 0,86 × 0,30 | 9 espaços: comida, utensilios, materiais | - | - | 2364 |
| Estante de despensa com caixotes (`despensa`) | 14 | Armazenamento do abrigo | 1,20 × 1,86 × 0,41 | 16 espaços: comida, agua | - | - | 20656 |
| Estante aramada com rodinhas (`estante_aramada`) | 14 | Armazenamento do abrigo | 0,92 × 1,61 × 0,50 | 10 espaços: comida, limpeza, utensilios | - | barricada | 14240 |
| Baú de madeira com cadeado (`bau_madeira`) | 14 | Armazenamento do abrigo | 1,05 × 0,51 × 0,57 | 15 espaços: roupas, ferramentas, moedas, lembrancas | tampa | barricada, sentar | 2416 |
| Caixote militar verde (`caixa_militar`) | 14 | Armazenamento do abrigo | 1,01 × 0,40 × 0,51 | 10 espaços: municao, remedios, ferramentas, comida | tampa | barricada | 1616 |
| Caixa organizadora empilhável (`caixa_organizadora`) | 14 | Armazenamento do abrigo | 0,63 × 0,32 × 0,45 | 6 espaços: utensilios, roupas, higiene, pilhas | tampa | - | 292 |
| Caixa de ferramentas de metal (`caixa_ferramentas`) | 14 | Armazenamento do abrigo | 0,50 × 0,27 × 0,23 | 6 espaços: ferramentas, materiais | tampa | - | 776 |
| Pallet de tábuas cintadas (`pallet_tabuas`) | 14 | Armazenamento do abrigo | 1,50 × 0,30 × 0,85 | - | camada_1, camada_2, camada_3, camada_4, camada_5, camada_6 | - | 7432 |
| Pallet de tijolos (`pallet_tijolos`) | 14 | Armazenamento do abrigo | 1,20 × 0,43 × 0,80 | - | camada_1, camada_2, camada_3, camada_4, camada_5 | - | 6316 |
| Pallet de sacos de cimento (`pallet_cimento`) | 14 | Armazenamento do abrigo | 1,20 × 0,68 × 0,80 | - | camada_1, camada_2, camada_3, camada_4, camada_5 | - | 17228 |
| Pallet de sucata separada (`pallet_sucata`) | 14 | Armazenamento do abrigo | 1,20 × 0,45 × 0,80 | - | camada_1, camada_2, camada_3, camada_4 | - | 4624 |
| Pilha de sacos de areia no pallet (`pallet_sacos_areia`) | 14 | Armazenamento do abrigo | 1,21 × 0,51 × 1,00 | - | camada_1, camada_2, camada_3 | - | 21388 |
| Lenheiro coberto (`lenheiro`) | 14 | Armazenamento do abrigo | 1,80 × 1,53 × 0,89 | - | camada_1, camada_2, camada_3, camada_4 | - | 11164 |
| Bancada de carpintaria de cavaletes (`bancada_carpintaria`) | 16 | Oficina | 2,23 × 1,00 × 0,94 | - | - | - | 3044 |
| Mesa de costura com máquina manual (`bancada_costura`) | 16 | Oficina | 1,10 × 1,12 × 0,60 | - | - | sentar | 2352 |
| Mesa de enfermaria improvisada (`mesa_enfermaria`) | 16 | Saúde | 2,42 × 0,93 × 0,66 | - | - | dormir | 4908 |
| Forja de tambor com fole (`forja_tambor`) | 16 | Oficina | 2,01 × 0,68 × 0,61 | - | - | - | 3640 |
| Fogão a lenha de tambor (`fogao_tambor`) | 16 | Cozinha | 1,22 × 2,40 × 0,67 | - | porta_fornalha | - | 4012 |
| Defumador de tábuas (`defumador`) | 16 | Cozinha | 0,90 × 1,82 × 0,86 | - | porta | - | 7328 |
| Filtro de água em barril (`filtro_barril`) | 16 | Água | 0,60 × 1,26 × 0,87 | 1 espaços: agua | - | - | 8952 |
| Bancada de eletrônica (`bancada_eletronica`) | 16 | Oficina | 1,50 × 1,29 × 0,64 | - | - | sentar | 4820 |
| Mesa de recarga de munição (`bancada_municao`) | 16 | Oficina | 1,20 × 1,27 × 0,60 | - | - | - | 3036 |
| Alambique de panela (`alambique`) | 16 | Oficina | 1,49 × 0,88 × 0,59 | - | - | - | 6704 |
| Composteira de pallets (`composteira`) | 16 | Agricultura | 1,30 × 1,33 × 1,25 | - | - | - | 8084 |
| Cama de pallet com colchão (`cama_pallet`) | 16 | Abrigo | 1,45 × 0,51 × 2,20 | - | - | dormir | 5872 |
| Cavalo de frisa de estacas (`cavalo_frisa`) | 17 | Defesa da base | 1,90 × 0,97 × 0,97 | - | - | - | 1104 |
| Cerca de arame farpado (`cerca_arame`) | 17 | Defesa da base | 2,10 × 1,24 × 0,11 | - | - | - | 2820 |
| Parede de sacos de areia (`parede_sacos`) | 17 | Defesa da base | 2,04 × 1,03 × 0,42 | - | - | - | 14080 |
| Barreira de pneus com terra (`barreira_pneus`) | 17 | Defesa da base | 1,99 × 0,44 × 0,88 | - | - | - | 9024 |
| Tábua de pregos (`tabua_pregos`) | 17 | Defesa da base | 1,00 × 0,09 × 0,31 | - | - | - | 2588 |
| Fosso com estacas (`fosso_estacas`) | 17 | Defesa da base | 2,56 × 1,05 × 1,43 | - | - | - | 3180 |
| Porta reforçada com chapa (`porta_reforcada`) | 17 | Defesa da base | 1,06 × 2,18 × 0,21 | - | porta | - | 1516 |
| Grade de janela de vergalhão (`grade_janela`) | 17 | Defesa da base | 1,05 × 1,56 × 0,04 | - | - | - | 12808 |
| Chapa de seteira para janela (`seteira`) | 17 | Defesa da base | 1,01 × 1,64 × 0,10 | - | tampa_fenda | - | 1596 |
| Holofote em poste com bateria (`holofote`) | 17 | Defesa da base | 0,85 × 2,88 × 0,90 | - | cabeca | - | 1536 |
| Sino de alarme de botijão (`sino_alarme`) | 17 | Defesa da base | 1,30 × 2,30 × 0,84 | - | - | - | 3728 |
| Plataforma de tiro de andaime (`plataforma_tiro`) | 17 | Defesa da base | 2,09 × 2,50 × 1,06 | - | - | - | 8528 |

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
| Porta-retrato de família (`porta_retrato`) | 7 | Vida de antes | lembranca | 1 | 0,3 kg | 1 | ânimo +5 se guardado; pode identificar um sobrevivente procurado (mural) | casas, motel, escritorio |
| Ursinho de pelúcia (`ursinho`) | 7 | Vida de antes | lembranca | 1 | 0,25 kg | 1 | acalma uma criança sobrevivente (moral +10) | casas, escolinha, clinica, motel |
| Saco de correspondência (`saco_correio`) | 9 | Chaves e pistas | pista | 1 | 4,0 kg | 1 | cartas e pacotes: chance de remédios, pilhas ou uma pista de sobreviventes | correios, estacao, rodoviaria |
| Extintor de incêndio (`extintor`) | 9 | Ferramentas | ferramenta | 1 | 6,0 kg | 1 | apaga fogo; jato atordoa zumbis (barulho baixo); arma pesada (dano 20) | quartel, galeria, hotel, escolinha, posto, fabrica, supermercado |
| Saco de pão francês (`pao_velho`) | 10 | Comida | comida | 1 | 0,4 kg | 4 | fome -15; endurece em 3 dias (ainda comível na sopa) | padaria, supermercado, diner, casas |
| Macaco jacaré (`macaco_jacare`) | 11 | Ferramentas | ferramenta | 4 | 12 kg | 1 | ergue carro e escombros (passagem bloqueada) e serve de barricada pesada | garagem, posto, concessionaria, ferro_velho |
| Saco de ração (`saco_racao`) | 11 | Agricultura | racao | 2 | 10 kg | 1 | alimenta galinhas (5 dias); em último caso, comida ruim (fome -10, enjoo) | fazenda, armazem, celeiro, supermercado |
| Remo de madeira (`remo`) | 12 | Armas improvisadas | arma | 2 | 1,4 kg | 1 | arma corpo a corpo longa (empurra zumbis); rema a canoa (dano 14) | casa_de_barcos, parque, garagem |
| Colete salva-vidas (`colete_salva_vidas`) | 12 | Roupas e equipamento | equipamento | 1 | 0,8 kg | 1 | flutua (atravessa o lago); +5 de proteção leve | casa_de_barcos, piscina, parque |
| Skate (`skate`) | 12 | Utensílios | equipamento | 2 | 2,2 kg | 1 | anda 40% mais rápido no asfalto (rodinhas fazem barulho); arma leve (dano 10) | pista_skate, casas, escolinha, rua |
| Taco de minigolfe (`taco_golfe`) | 12 | Armas improvisadas | arma | 2 | 0,5 kg | 1 | arma corpo a corpo leve (quebra fácil) (dano 12) | minigolfe, mansao, casas |
| Punhado de sucata (`sucata_metal`) | 13 | Materiais de construção | sucata | 1 | 1,2 kg | 10 | 1 sucata: base de quase toda receita de metal | ferrovelho, garagem, posto, fabrica, rua |
| Pote de parafusos e porcas (`pote_parafusos`) | 13 | Materiais de construção | sucata | 2 | 0,9 kg | 4 | fixa peças: armas, bancadas, portas reforçadas | garagem, casas, fabrica, serraria |
| Molas e engrenagens (`engrenagens`) | 13 | Materiais de construção | pecas | 1 | 0,6 kg | 6 | mecanismos: armadilhas, besta, bomba d'água, cata-vento | fabrica, garagem, relojoaria, casas |
| Placa de circuito (`placa_circuito`) | 13 | Luz e eletrônicos | pecas | 1 | 0,2 kg | 6 | eletrônica: rádio, holofote, painel solar | casas, escritorio, cinema, delegacia, correios |
| Motor elétrico pequeno (`motor_eletrico`) | 13 | Luz e eletrônicos | pecas | 2 | 1,6 kg | 1 | gera energia girando (cata-vento, bicicleta-gerador) ou move bomba d'água | casas, fabrica, garagem, lavanderia |
| Rolo de fio elétrico (`fio_eletrico`) | 13 | Luz e eletrônicos | pecas | 1 | 0,8 kg | 3 | ligar luzes, alarmes, gerador e painel solar (10 m) | casas, fabrica, garagem, cinema, hotel |
| Rolo de arame liso (`arame_liso`) | 13 | Materiais de construção | sucata | 1 | 1,0 kg | 3 | amarrar: armadilhas, cercas, lanças e reparos (20 m) | armazem, fazenda, serraria, garagem, casa_de_campo |
| Corrente com cadeado (`corrente_cadeado`) | 13 | Materiais de construção | sucata | 2 | 2,2 kg | 1 | tranca portão ou armário (zumbi não abre, saqueador precisa de alicate) | garagem, armazem, delegacia, estacao, parque_trailers |
| Par de dobradiças (`dobradicas`) | 13 | Materiais de construção | sucata | 1 | 0,4 kg | 6 | portões, alçapões, tampas de caixote e armários | casas, garagem, serraria, armazem |
| Pacote de abraçadeiras de nylon (`abracadeiras`) | 13 | Materiais de construção | material | 1 | 0,1 kg | 10 | amarra rápido: armadilhas, lanternas na arma, reparos | garagem, casas, fabrica, cinema, supermercado |
| Lata de cola de contato (`cola_contato`) | 13 | Materiais de construção | material | 1 | 0,3 kg | 4 | cola couro, borracha e madeira: proteções, reparo de botas e mochila | casas, garagem, serraria, escolinha |
| Garrafa PET vazia 2 L (`garrafa_pet`) | 13 | Utensílios | material | 1 | 0,05 kg | 4 | filtro de água, coletor, armadilha de garrafa e isca | casas, rua, supermercado, diner, posto |
| Lata vazia (`lata_vazia`) | 13 | Utensílios | sucata | 1 | 0,06 kg | 8 | alarme de latas, lamparina, fogareiro e caneca de ferver água | casas, rua, supermercado, diner, abrigo |
| Cano de PVC (`tubo_pvc`) | 13 | Materiais de construção | material | 1 | 0,6 kg | 4 | calhas, coletor de chuva, irrigação da horta e filtros | casas, armazem, fabrica, piscina, fazenda |
| Lona dobrada (`lona`) | 13 | Materiais de construção | material | 2 | 2,5 kg | 2 | cobre telhado quebrado, barraca, estufa e coletor de chuva (4 × 3 m) | armazem, fazenda, garagem, parque_trailers, posto |
| Trapos amarrados (`trapos`) | 13 | Materiais de construção | material | 1 | 0,3 kg | 10 | curativo, tocha, filtro, remendo e pavio de molotov | casas, lavanderia, hotel, motel, garagem |
| Retalho de couro (`couro`) | 13 | Materiais de construção | material | 1 | 0,5 kg | 6 | protetor de braço anti-mordida, coldre, alças e botas | casas, fazenda, mansao, concessionaria, cinema |
| Saco de carvão (`carvao`) | 13 | Combustível | combustivel | 3 | 3,0 kg | 1 | combustível da forja e do defumador; carvão moído vai no filtro de água | supermercado, posto, casas, diner, armazem |
| Punhado de pedras (`pedras`) | 13 | Materiais de construção | material | 1 | 2,0 kg | 10 | fogueira, forno de barro, peso de armadilha e muro de pedra | rua, parque, fazenda, casa_barcos, serraria |
| Tijolos (`tijolo`) | 13 | Materiais de construção | material | 1 | 2,4 kg | 6 | fogão de tijolo, forno comunitário, forja e muros | fabrica, ruinas, casas, armazem |
| Saco de cimento 25 kg (`cimento`) | 13 | Materiais de construção | material | 3 | 25,0 kg | 1 | muralha de concreto, cisterna, reforma de prédios (fase 4) | armazem, fabrica, garagem_vertical, ruinas |
| Carretel de linha e anzóis (`linha_pesca`) | 13 | Utensílios | material | 1 | 0,1 kg | 6 | vara de pesca, armadilha de linha e costura de ferimento | casa_barcos, casas, supermercado, parque_trailers |
| Garrafa de álcool 70 % (`alcool`) | 13 | Remédios | remedios | 1 | 1,0 kg | 2 | desinfeta ferimento, acende fogo, combustível da lamparina e do molotov | supermercado, clinica, casas, posto |
| Pedra de amolar (`pedra_amolar`) | 13 | Ferramentas | ferramenta | 2 | 0,4 kg | 1 | recupera o fio de facas, facão, machado e lança (sem bancada) | casas, fazenda, serraria, casa_de_campo |
| Tocha de pano e álcool (`tocha`) | 15 | Ferramentas | ferramenta | 1 | 0,5 kg | 3 | luz de 6 m por 10 min; afasta um zumbi encostado (fogo), mas a chama chama outros de longe (dano 12) | abrigo |
| Lamparina de lata (`lamparina_lata`) | 15 | Luz e eletrônicos | ferramenta | 1 | 0,25 kg | 2 | luz fraca de 3 m por 6 horas (gasta álcool); dá para deixar acesa no abrigo | abrigo |
| Fogareiro de lata (`fogareiro_lata`) | 15 | Utensílios | ferramenta | 1 | 0,3 kg | 1 | cozinha e ferve água com gravetos ou carvão (fumaça baixa, chama escondida) | abrigo |
| Kit de acender fogo (`kit_fogo`) | 15 | Ferramentas | ferramenta | 2 | 0,15 kg | 1 | acende fogueira sem isqueiro (30 usos); funciona molhado | abrigo, casa_de_campo, parque_trailers |
| Filtro de água de garrafa (`filtro_garrafa`) | 15 | Água | ferramenta | 2 | 0,6 kg | 1 | tira a sujeira da água de chuva ou do rio (ainda precisa ferver); 20 litros antes de trocar o carvão | abrigo |
| Caneca de lata com alça de arame (`caneca_lata`) | 15 | Utensílios | ferramenta | 1 | 0,1 kg | 2 | ferve 0,4 L de água na fogueira (água fervida não dá doença) | abrigo |
| Curativo de pano fervido (`curativo_improvisado`) | 15 | Remédios | remedios | 1 | 0,05 kg | 6 | para sangramento (cura 15); 20 % de chance de infeccionar se o pano não foi fervido | abrigo |
| Tala de tábua e pano (`tala_improvisada`) | 15 | Remédios | remedios | 1 | 0,6 kg | 2 | trata perna ou braço quebrado: volta a correr em 1 dia em vez de 4 | abrigo |
| Armadilha de laço (`armadilha_laco`) | 15 | Agricultura | ferramenta | 1 | 0,4 kg | 3 | montada no mato pega coelho ou pombo (comida 2) em até 1 dia; zumbi pisa e fica preso 5 s | abrigo |
| Vara de pesca improvisada (`vara_pesca`) | 15 | Agricultura | ferramenta | 1 | 0,4 kg | 1 | pesca no lago (comida 3 a cada 20 min, em silêncio) | abrigo, casa_barcos |
| Kit de reparo improvisado (`kit_reparo`) | 15 | Ferramentas | ferramenta | 3 | 0,8 kg | 1 | repara arma branca (+40 % de durabilidade) ou barricada (+60 de vida); 3 usos | abrigo, garagem |
| Colete de revistas e fita (`colete_revistas`) | 15 | Roupas e equipamento | equipamento | 1 | 1,4 kg | 1 | +15 de proteção contra mordida no tronco e nos braços; desgasta a cada mordida | abrigo |
| Colete de placas de sucata (`colete_sucata`) | 15 | Roupas e equipamento | equipamento | 2 | 4,5 kg | 1 | +35 de proteção; pesado (correr cansa 30 % mais rápido) e barulhento | abrigo, ferrovelho |
| Capacete de panela acolchoado (`capacete_panela`) | 15 | Roupas e equipamento | equipamento | 1 | 1,0 kg | 1 | +20 de proteção na cabeça; tira 10 % da audição | abrigo |
| Mochila de lona improvisada (`mochila_lona`) | 15 | Roupas e equipamento | equipamento | 1 | 0,8 kg | 1 | mochila de 4 × 4 células (a de loja tem 5 × 6); faz barulho de lona ao correr | abrigo |
| Bolsa de cintura de pano (`bolsa_cintura`) | 15 | Roupas e equipamento | equipamento | 1 | 0,3 kg | 1 | +3 × 2 células de acesso rápido (usar sem abrir a mochila) | abrigo |
| Peça de carne defumada (`carne_defumada`) | 16 | Comida | comida | 3 | 0,6 kg | 4 | fome -40; dura 10 dias sem estragar | abrigo, fazenda |
| Saco de adubo de composto (`adubo`) | 16 | Agricultura | material | 2 | 8,0 kg | 1 | canteiro adubado rende 50 % mais por 3 colheitas | abrigo, fazenda, supermercado |
