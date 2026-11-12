# Árvore de craft e armazenamento

Gerado por `props/craft.py` a partir dos catálogos. Mostra, fase a fase, o que o jogador fabrica ou constrói, com quê, e onde guarda.
Ingredientes são ids do loot (`props/loot/catalogo.json`); estações e construções são mobílias (`props/mobilias/catalogo.json`).

## Receitas por fase

### Fase 1 · Sozinho

| Item | Lote | Ingredientes | Ferramenta | Estação | Tempo |
|---|---|---|---|---|---|
| Alarme de latas (`alarme_latas`) | 5 | 1× Rolo de corda (`corda`), 4× Lata vazia (`lata_vazia`) | à mão | - | - |
| Barricada de tábuas para janela (`barricada_janela`) | 5 | 5× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Barricada de tábuas para porta (`barricada_porta`) | 5 | 6× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Colchão no chão (`colchao_chao`) | 5 | 1× colchão tirado de uma cama | à mão | - | - |
| Fogueira de pedras (`fogueira`) | 5 | 3× Feixe de lenha (`lenha`), 10× Punhado de pedras (`pedras`) | à mão | - | - |
| Baú de madeira com cadeado (`bau_madeira`) | 14 | 5× Tábua de madeira (`tabua`), 1× Par de dobradiças (`dobradicas`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | Bancada de carpintaria com morsa (`bancada_carpintaria`) | - |
| Lenheiro coberto (`lenheiro`) | 14 | 6× Tábua de madeira (`tabua`), 2× Chapa de metal ondulada (`chapa_metal`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Prateleira de tábuas e tijolos (`prateleira_improvisada`) | 14 | 3× Tábua de madeira (`tabua`), 6× Tijolos (`tijolo`) | à mão | - | - |
| Suporte de parede para armas (`rack_armas_parede`) | 14 | 2× Tábua de madeira (`tabua`), 1× Cano de ferro (`cano_metal`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Armadilha de laço (`armadilha_laco`) | 15 | 1× Rolo de arame liso (`arame_liso`), 1× Tábua de madeira (`tabua`) | Faca de cozinha (`faca_cozinha`) | mao | 60 s |
| Bolsa de cintura de pano (`bolsa_cintura`) | 15 | 3× Trapos amarrados (`trapos`), 1× Carretel de linha e anzóis (`linha_pesca`), 1× Rolo de corda (`corda`) | Lata de costura (`kit_costura`) | mao | 120 s |
| Caneca de lata com alça de arame (`caneca_lata`) | 15 | 1× Lata vazia (`lata_vazia`), 1× Rolo de arame liso (`arame_liso`) | à mão | mao | 25 s |
| Capacete de panela acolchoado (`capacete_panela`) | 15 | 1× Panela com tampa (`panela`), 2× Trapos amarrados (`trapos`), 1× Rolo de corda (`corda`) | Faca de cozinha (`faca_cozinha`) | mao | 60 s |
| Colete de revistas e fita (`colete_revistas`) | 15 | 2× Livro técnico (`livro`), 2× Fita adesiva prata (`fita_adesiva`), 1× Rolo de corda (`corda`) | à mão | mao | 90 s |
| Curativo de pano fervido (`curativo_improvisado`) | 15 | 2× Trapos amarrados (`trapos`), 1× Garrafa de álcool 70 % (`alcool`) | à mão | Fogueira de pedras (`fogueira`) | 45 s |
| Filtro de água de garrafa (`filtro_garrafa`) | 15 | 1× Garrafa PET vazia 2 L (`garrafa_pet`), 1× Trapos amarrados (`trapos`), 1× Saco de carvão (`carvao`), 1× Punhado de pedras (`pedras`) | Faca de cozinha (`faca_cozinha`) | mao | 120 s |
| Fogareiro de lata (`fogareiro_lata`) | 15 | 2× Lata vazia (`lata_vazia`) | Faca de cozinha (`faca_cozinha`) | mao | 60 s |
| Kit de acender fogo (`kit_fogo`) | 15 | 1× Punhado de pedras (`pedras`), 1× Punhado de sucata (`sucata_metal`), 1× Trapos amarrados (`trapos`), 1× Saco de carvão (`carvao`) | Pedra de amolar (`pedra_amolar`) | mao | 90 s |
| Kit de reparo improvisado (`kit_reparo`) | 15 | 1× Fita adesiva prata (`fita_adesiva`), 1× Pote de parafusos e porcas (`pote_parafusos`), 1× Rolo de arame liso (`arame_liso`), 1× Trapos amarrados (`trapos`) | à mão | mao | 30 s |
| Lamparina de lata (`lamparina_lata`) | 15 | 1× Lata vazia (`lata_vazia`), 1× Trapos amarrados (`trapos`), 1× Garrafa de álcool 70 % (`alcool`) | Faca de cozinha (`faca_cozinha`) | mao | 40 s |
| Mochila de lona improvisada (`mochila_lona`) | 15 | 1× Lona dobrada (`lona`), 1× Rolo de corda (`corda`), 1× Trapos amarrados (`trapos`) | Lata de costura (`kit_costura`) | mao | 180 s |
| Tala de tábua e pano (`tala_improvisada`) | 15 | 1× Tábua de madeira (`tabua`), 2× Trapos amarrados (`trapos`) | Serrote (`serrote`) | mao | 60 s |
| Tocha de pano e álcool (`tocha`) | 15 | 1× Feixe de lenha (`lenha`), 1× Trapos amarrados (`trapos`), 1× Garrafa de álcool 70 % (`alcool`) | à mão | mao | 20 s |
| Vara de pesca improvisada (`vara_pesca`) | 15 | 1× Feixe de lenha (`lenha`), 1× Carretel de linha e anzóis (`linha_pesca`) | Faca de cozinha (`faca_cozinha`) | mao | 45 s |
| Tábua de pregos (`tabua_pregos`) | 17 | 1× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Caixote grande de tábuas (`caixote_grande`) | 20 | 8× Tábua de madeira (`tabua`), 2× Caixa de pregos (`caixa_pregos`), 1× Par de dobradiças (`dobradicas`) | Martelo de unha (`martelo`) | - | - |

### Fase 2 · Abrigo

| Item | Lote | Ingredientes | Ferramenta | Estação | Tempo |
|---|---|---|---|---|---|
| Canteiro de horta (`canteiro_horta`) | 8 | 4× Tábua de madeira (`tabua`), 2× terra (cavar com pá) | à mão | - | - |
| Coletor de água da chuva (`coletor_chuva`) | 8 | 1× Tambor de 200 L (`tambor_200l`), 1× Lona dobrada (`lona`), 3× Tábua de madeira (`tabua`) | à mão | - | - |
| Muro de sucata (`muro_sucata`) | 8 | 3× Chapa de metal ondulada (`chapa_metal`), 2× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | à mão | - | - |
| Portão de sucata (`portao_sucata`) | 8 | 2× Chapa de metal ondulada (`chapa_metal`), 4× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | à mão | - | - |
| Torre de vigia (`torre_vigia`) | 8 | 16× Tábua de madeira (`tabua`), 2× Caixa de pregos (`caixa_pregos`), 1× Lona dobrada (`lona`) | à mão | - | - |
| Cavalete de serrar lenha (`cavalete_serra`) | 11 | 3× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | à mão | - | - |
| Espantalho (`espantalho`) | 11 | 1× Pilha de roupas dobradas (`roupas`), 2× palha (fardo de feno), 1× Tábua de madeira (`tabua`) | à mão | - | - |
| Galinheiro de tela (`galinheiro`) | 11 | 6× Tábua de madeira (`tabua`), 0× Rolo de arame farpado (`arame_farpado`), 2× Chapa de metal ondulada (`chapa_metal`), 1× Caixa de pregos (`caixa_pregos`) | à mão | - | - |
| Armário de armas de madeira com tela (`armario_armas_abrigo`) | 14 | 8× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`), 1× Par de dobradiças (`dobradicas`), 1× Corrente com cadeado (`corrente_cadeado`), 1× Rolo de arame liso (`arame_liso`) | Martelo de unha (`martelo`) | Bancada de carpintaria com morsa (`bancada_carpintaria`) | - |
| Estante de despensa com caixotes (`despensa`) | 14 | 10× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | Bancada de carpintaria com morsa (`bancada_carpintaria`) | - |
| Colete de placas de sucata (`colete_sucata`) | 15 | 1× Chapa de metal ondulada (`chapa_metal`), 2× Retalho de couro (`couro`), 1× Pote de parafusos e porcas (`pote_parafusos`), 1× Rolo de corda (`corda`) | Martelo de unha (`martelo`) | Bancada de trabalho com morsa (`bancada_trabalho`) | 240 s |
| Alambique de panela (`alambique`) | 16 | 1× Panela com tampa (`panela`), 1× Cano de PVC (`tubo_pvc`), 1× Cano de ferro (`cano_metal`), 1× Tambor de 200 L (`tambor_200l`), 6× Tijolos (`tijolo`) | Chave inglesa (`chave_inglesa`) | - | - |
| Bancada de carpintaria com morsa (`bancada_carpintaria`) | 16 | 6× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | Serrote (`serrote`) | - | - |
| Cama de pallet com colchão (`cama_pallet`) | 16 | 2× Pallet de madeira (`pallet`), 1× Colchão no chão (`colchao_chao`) | à mão | - | - |
| Composteira de pallets (`composteira`) | 16 | 3× Pallet de madeira (`pallet`), 1× Rolo de arame liso (`arame_liso`) | à mão | - | - |
| Defumador de tábuas (`defumador`) | 16 | 8× Tábua de madeira (`tabua`), 1× Chapa de metal ondulada (`chapa_metal`), 1× Caixa de pregos (`caixa_pregos`), 4× Tijolos (`tijolo`) | Martelo de unha (`martelo`) | - | - |
| Filtro de água em barril (`filtro_barril`) | 16 | 1× Tambor de 200 L (`tambor_200l`), 2× Saco de carvão (`carvao`), 4× Punhado de pedras (`pedras`), 2× Trapos amarrados (`trapos`), 1× Cano de PVC (`tubo_pvc`) | Chave inglesa (`chave_inglesa`) | - | - |
| Fogão a lenha de tambor (`fogao_tambor`) | 16 | 1× Tambor de 200 L (`tambor_200l`), 2× Cano de ferro (`cano_metal`), 1× Chapa de metal ondulada (`chapa_metal`), 4× Tijolos (`tijolo`) | Martelo de unha (`martelo`) | - | - |
| Forja de tambor com fole (`forja_tambor`) | 16 | 1× Tambor de 200 L (`tambor_200l`), 8× Tijolos (`tijolo`), 2× Cano de ferro (`cano_metal`), 2× Retalho de couro (`couro`) | Martelo de unha (`martelo`) | - | - |
| Mesa de costura com máquina manual (`bancada_costura`) | 16 | 4× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`), 1× Molas e engrenagens (`engrenagens`), 2× Punhado de sucata (`sucata_metal`) | Martelo de unha (`martelo`) | - | - |
| Mesa de enfermaria improvisada (`mesa_enfermaria`) | 16 | 4× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`), 2× Trapos amarrados (`trapos`) | Martelo de unha (`martelo`) | - | - |
| Barreira de pneus com terra (`barreira_pneus`) | 17 | 6× terra (cavar com pá), 1× Pilha de pneus (`pilha_pneus`) | Pá (`pa`) | - | - |
| Cavalo de frisa de estacas (`cavalo_frisa`) | 17 | 6× Feixe de lenha (`lenha`), 1× Rolo de arame liso (`arame_liso`) | Machado (`machado`) | - | - |
| Cerca de arame farpado (`cerca_arame`) | 17 | 1× Rolo de arame farpado (`arame_farpado`), 3× Feixe de lenha (`lenha`) | Martelo de unha (`martelo`) | - | - |
| Chapa de seteira para janela (`seteira`) | 17 | 2× Chapa de metal ondulada (`chapa_metal`), 2× Tábua de madeira (`tabua`), 1× Pote de parafusos e porcas (`pote_parafusos`) | Chave inglesa (`chave_inglesa`) | - | - |
| Grade de janela de vergalhão (`grade_janela`) | 17 | 3× Cano de ferro (`cano_metal`), 4× Punhado de sucata (`sucata_metal`), 1× Pote de parafusos e porcas (`pote_parafusos`) | Chave inglesa (`chave_inglesa`) | Forja de tambor com fole (`forja_tambor`) | - |
| Parede de sacos de areia (`parede_sacos`) | 17 | 12× Saco de areia (`saco_areia`) | Pá (`pa`) | - | - |
| Porta reforçada com chapa (`porta_reforcada`) | 17 | 2× Chapa de metal ondulada (`chapa_metal`), 3× Tábua de madeira (`tabua`), 1× Pote de parafusos e porcas (`pote_parafusos`), 1× Corrente com cadeado (`corrente_cadeado`) | Chave inglesa (`chave_inglesa`) | Bancada de carpintaria com morsa (`bancada_carpintaria`) | - |
| Sino de alarme de botijão (`sino_alarme`) | 17 | 3× Tábua de madeira (`tabua`), 1× Corrente com cadeado (`corrente_cadeado`), 1× Cano de ferro (`cano_metal`) | Serrote (`serrote`) | - | - |
| Baú de aço com cadeado (`bau_aco`) | 20 | 4× Chapa de metal ondulada (`chapa_metal`), 2× Cano de ferro (`cano_metal`), 1× Par de dobradiças (`dobradicas`), 1× Corrente com cadeado (`corrente_cadeado`) | Martelo de unha (`martelo`) | Forja de tambor com fole (`forja_tambor`) | - |

### Fase 3 · Assentamento

| Item | Lote | Ingredientes | Ferramenta | Estação | Tempo |
|---|---|---|---|---|---|
| Gerador portátil a gasolina (`gerador`) | 4 | 1× Motor elétrico pequeno (`motor_eletrico`), 2× Caixa de peças de motor (`peca_motor`), 2× Chapa de metal ondulada (`chapa_metal`), 1× Cano de ferro (`cano_metal`), 1× Rolo de fio elétrico (`fio_eletrico`) | Chave inglesa (`chave_inglesa`) | Forja de tambor com fole (`forja_tambor`) | - |
| Bancada de eletrônica (`bancada_eletronica`) | 16 | 4× Tábua de madeira (`tabua`), 2× Rolo de fio elétrico (`fio_eletrico`), 1× Placa de circuito (`placa_circuito`), 1× Bateria de carro (`bateria_carro`) | Chave inglesa (`chave_inglesa`) | - | - |
| Mesa de recarga de munição (`bancada_municao`) | 16 | 5× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`), 1× Pote de parafusos e porcas (`pote_parafusos`) | Chave inglesa (`chave_inglesa`) | - | - |
| Fosso com estacas (`fosso_estacas`) | 17 | 4× Feixe de lenha (`lenha`) | Pá (`pa`) | - | - |
| Holofote em poste com bateria (`holofote`) | 17 | 2× Cano de ferro (`cano_metal`), 2× Rolo de fio elétrico (`fio_eletrico`), 1× Bateria de carro (`bateria_carro`), 1× Placa de circuito (`placa_circuito`), 1× Lanterna (`lanterna`) | Chave inglesa (`chave_inglesa`) | Bancada de eletrônica (`bancada_eletronica`) | - |
| Plataforma de tiro de andaime (`plataforma_tiro`) | 17 | 6× Cano de ferro (`cano_metal`), 6× Tábua de madeira (`tabua`), 1× Pote de parafusos e porcas (`pote_parafusos`), 4× Saco de areia (`saco_areia`) | Chave inglesa (`chave_inglesa`) | - | - |
| Barraca de lona com cumeeira (`barraca_lona`) | 18 | 2× Lona dobrada (`lona`), 1× Rolo de corda (`corda`), 3× Feixe de lenha (`lenha`) | à mão | - | - |
| Cata-vento de bomba d'água em torre (`cata_vento`) | 18 | 8× Cano de ferro (`cano_metal`), 6× Chapa de metal ondulada (`chapa_metal`), 1× Molas e engrenagens (`engrenagens`), 1× Tambor de 200 L (`tambor_200l`) | Chave inglesa (`chave_inglesa`) | Forja de tambor com fole (`forja_tambor`) | - |
| Chuveiro de balde com cortina de lona (`chuveiro_balde`) | 18 | 4× Feixe de lenha (`lenha`), 1× Lona dobrada (`lona`), 1× Rolo de corda (`corda`), 1× Lata vazia (`lata_vazia`), 1× Pallet de madeira (`pallet`) | Martelo de unha (`martelo`) | - | - |
| Coelheira de tábuas e tela (`coelheira`) | 18 | 6× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`), 1× Rolo de arame liso (`arame_liso`), 1× Chapa de metal ondulada (`chapa_metal`) | Martelo de unha (`martelo`) | - | - |
| Estufa de cano e plástico (`estufa`) | 18 | 8× Cano de PVC (`tubo_pvc`), 2× Rolo de plástico transparente (`rolo_plastico`), 6× Tábua de madeira (`tabua`), 10× terra (cavar com pá) | Pá (`pa`) | - | - |
| Latrina de tábuas com fossa (`latrina`) | 18 | 10× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`), 1× Chapa de metal ondulada (`chapa_metal`) | Pá (`pa`) | - | - |
| Maca de campanha dobrável (`maca_campanha`) | 18 | 3× Cano de ferro (`cano_metal`), 1× Lona dobrada (`lona`), 1× Rolo de corda (`corda`) | Chave inglesa (`chave_inglesa`) | Mesa de costura com máquina manual (`bancada_costura`) | - |
| Mesa comprida do refeitório com bancos (`mesa_refeitorio`) | 18 | 10× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | Bancada de carpintaria com morsa (`bancada_carpintaria`) | - |
| Painéis solares no cavalete com baterias (`painel_solar`) | 18 | 4× Feixe de lenha (`lenha`), 2× Rolo de fio elétrico (`fio_eletrico`), 2× Bateria de carro (`bateria_carro`), 1× Placa de circuito (`placa_circuito`), 2× Tábua de madeira (`tabua`) | Chave inglesa (`chave_inglesa`) | Bancada de eletrônica (`bancada_eletronica`) | - |
| Panelão no tripé sobre fogueira (`panelao_tripe`) | 18 | 3× Feixe de lenha (`lenha`), 1× Corrente com cadeado (`corrente_cadeado`), 8× Punhado de pedras (`pedras`), 4× Punhado de sucata (`sucata_metal`) | Martelo de unha (`martelo`) | Forja de tambor com fole (`forja_tambor`) | - |
| Poço de pedra com sarilho (`poco_sarilho`) | 18 | 24× Punhado de pedras (`pedras`), 2× Saco de cimento 25 kg (`cimento`), 4× Feixe de lenha (`lenha`), 1× Rolo de corda (`corda`), 1× Chapa de metal ondulada (`chapa_metal`) | Pá (`pa`) | - | - |
| Tanque de lavar de cimento (`tanque_lavar`) | 18 | 1× Saco de cimento 25 kg (`cimento`), 10× Tijolos (`tijolo`), 1× Cano de PVC (`tubo_pvc`) | à mão | - | - |
| Torre de rádio da comunidade (`torre_radio`) | 18 | 10× Cano de ferro (`cano_metal`), 4× Rolo de fio elétrico (`fio_eletrico`), 1× Rádio portátil (`radio_portatil`), 2× Placa de circuito (`placa_circuito`), 1× Bateria de carro (`bateria_carro`), 2× Rolo de arame liso (`arame_liso`) | Chave inglesa (`chave_inglesa`) | Bancada de eletrônica (`bancada_eletronica`) | - |
| Banco de baterias (`banco_baterias`) | 20 | 2× Bateria de carro (`bateria_carro`), 3× Tábua de madeira (`tabua`), 1× Rolo de fio elétrico (`fio_eletrico`), 1× Caixa de pregos (`caixa_pregos`) | Chave inglesa (`chave_inglesa`) | - | - |
| Carregador de pilhas (`carregador_pilhas`) | 20 | 1× Placa de circuito (`placa_circuito`), 1× Rolo de fio elétrico (`fio_eletrico`), 1× Punhado de sucata (`sucata_metal`), 2× Tábua de madeira (`tabua`) | Chave inglesa (`chave_inglesa`) | Bancada de eletrônica (`bancada_eletronica`) | - |
| Lâmpada improvisada no poste (`lampada_poste`) | 20 | 2× Tábua de madeira (`tabua`), 1× Rolo de fio elétrico (`fio_eletrico`), 1× Lata vazia (`lata_vazia`), 1× Fita adesiva prata (`fita_adesiva`) | Martelo de unha (`martelo`) | - | - |

### Fase 4 · Vila

| Item | Lote | Ingredientes | Ferramenta | Estação | Tempo |
|---|---|---|---|---|---|
| Banca de feira com toldo (`banca_feira`) | 19 | 6× Tábua de madeira (`tabua`), 1× Lona dobrada (`lona`), 4× Feixe de lenha (`lenha`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Estação de tratamento de água em tambores (`tratamento_agua`) | 19 | 3× Tambor de 200 L (`tambor_200l`), 6× Cano de PVC (`tubo_pvc`), 6× Punhado de pedras (`pedras`), 4× Saco de carvão (`carvao`), 6× Tábua de madeira (`tabua`) | Chave inglesa (`chave_inglesa`) | Bancada de carpintaria com morsa (`bancada_carpintaria`) | - |
| Forno de barro comunitário (`forno_comunitario`) | 19 | 30× Tijolos (`tijolo`), 8× terra (cavar com pá), 2× palha (fardo de feno), 1× Cano de ferro (`cano_metal`) | Pá (`pa`) | - | - |
| Memorial aos que se foram (`memorial`) | 19 | 6× Tábua de madeira (`tabua`), 10× Punhado de pedras (`pedras`), 2× Vela e caixa de fósforos (`vela_fosforos`) | Martelo de unha (`martelo`) | - | - |
| Módulo de muralha de blocos com passarela (`muralha_concreto`) | 19 | 4× Saco de cimento 25 kg (`cimento`), 20× Tijolos (`tijolo`), 2× Cano de ferro (`cano_metal`), 1× Rolo de arame farpado (`arame_farpado`), 4× Tábua de madeira (`tabua`) | Pá (`pa`) | - | - |
| Placa de boas-vindas da vila (`placa_boas_vindas`) | 19 | 8× Tábua de madeira (`tabua`), 2× Feixe de lenha (`lenha`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Portão principal de chapa com guarita (`portao_guarita`) | 19 | 8× Chapa de metal ondulada (`chapa_metal`), 6× Cano de ferro (`cano_metal`), 6× Saco de cimento 25 kg (`cimento`), 20× Tijolos (`tijolo`), 4× Par de dobradiças (`dobradicas`), 1× Corrente com cadeado (`corrente_cadeado`), 6× Tábua de madeira (`tabua`) | Chave inglesa (`chave_inglesa`) | Forja de tambor com fole (`forja_tambor`) | - |
| Poste de luz restaurado (`poste_luz`) | 19 | 2× Cano de ferro (`cano_metal`), 3× Rolo de fio elétrico (`fio_eletrico`), 1× Placa de circuito (`placa_circuito`) | Chave inglesa (`chave_inglesa`) | Bancada de eletrônica (`bancada_eletronica`) | - |
| Subestação religada (`subestacao`) | 19 | 10× Rolo de fio elétrico (`fio_eletrico`), 4× Placa de circuito (`placa_circuito`), 2× Motor elétrico pequeno (`motor_eletrico`), 6× Saco de cimento 25 kg (`cimento`), 2× Rolo de arame farpado (`arame_farpado`) | Chave inglesa (`chave_inglesa`) | Bancada de eletrônica (`bancada_eletronica`) | - |
| Turbina eólica pequena no mastro (`turbina_eolica`) | 19 | 6× Cano de ferro (`cano_metal`), 1× Motor elétrico pequeno (`motor_eletrico`), 3× Chapa de metal ondulada (`chapa_metal`), 4× Rolo de fio elétrico (`fio_eletrico`), 2× Bateria de carro (`bateria_carro`) | Chave inglesa (`chave_inglesa`) | Bancada de eletrônica (`bancada_eletronica`) | - |

### Fase 5 · Cidade nova

| Item | Lote | Ingredientes | Ferramenta | Estação | Tempo |
|---|---|---|---|---|---|
| Ponto da caravana (abrigo de ônibus reformado) (`ponto_onibus`) | 19 | 4× Cano de ferro (`cano_metal`), 2× Chapa de metal ondulada (`chapa_metal`), 4× Tábua de madeira (`tabua`) | Chave inglesa (`chave_inglesa`) | - | - |

## Estações: o que cada uma fabrica ou produz

| Estação | Fase | Fabrica | Produz sozinha (com um morador) |
|---|---|---|---|
| Alambique de panela (`alambique`) | 2 | - | 1× Garrafa de álcool 70 % (`alcool`) a cada 90 min, gastando 3 comida, 1 lenha |
| Bancada de carpintaria com morsa (`bancada_carpintaria`) | 2 | Armário de armas de madeira com tela, Estante de despensa com caixotes, Baú de madeira com cadeado, Porta reforçada com chapa, Mesa comprida do refeitório com bancos, Estação de tratamento de água em tambores | - |
| Mesa de costura com máquina manual (`bancada_costura`) | 2 | Maca de campanha dobrável | - |
| Composteira de pallets (`composteira`) | 2 | - | 1× Saco de adubo de composto (`adubo`) a cada 1440 min, gastando 4 restos de comida |
| Defumador de tábuas (`defumador`) | 2 | - | 4× Peça de carne defumada (`carne_defumada`) a cada 240 min, gastando 4 carne crua, 1 lenha |
| Filtro de água em barril (`filtro_barril`) | 2 | - | 1× Galão de água 5 L (`galao_agua`) a cada 60 min, gastando 5 agua suja, 1 galao vazio |
| Forja de tambor com fole (`forja_tambor`) | 2 | Gerador portátil a gasolina, Grade de janela de vergalhão, Panelão no tripé sobre fogueira, Cata-vento de bomba d'água em torre, Portão principal de chapa com guarita, Baú de aço com cadeado | - |
| Bancada de eletrônica (`bancada_eletronica`) | 3 | Holofote em poste com bateria, Painéis solares no cavalete com baterias, Torre de rádio da comunidade, Poste de luz restaurado, Subestação religada, Turbina eólica pequena no mastro, Carregador de pilhas | - |
| Cata-vento de bomba d'água em torre (`cata_vento`) | 3 | - | 2× Galão de água 5 L (`galao_agua`) a cada 60 min, gastando  |
| Coelheira de tábuas e tela (`coelheira`) | 3 | - | 2× Carne crua embrulhada (`carne_crua`) a cada 2880 min, gastando 2 restos de comida, 1 palha |
| Estufa de cano e plástico (`estufa`) | 3 | - | 1× Cesto de legumes da estufa (`cesto_legumes`) a cada 1440 min, gastando 1 galao_agua |
| Poço de pedra com sarilho (`poco_sarilho`) | 3 | - | 4× Galão de água 5 L (`galao_agua`) a cada 60 min, gastando  |
| Forno de barro comunitário (`forno_comunitario`) | 4 | - | 12× Pão caseiro do forno da vila (`pao_caseiro`) a cada 120 min, gastando 1 saco_farinha, 2 lenha |
| Estação de tratamento de água em tambores (`tratamento_agua`) | 4 | - | 10× Galão de água 5 L (`galao_agua`) a cada 60 min, gastando 1 alcool |
| Bancada de trabalho com morsa (`bancada_trabalho`) | - | Colete de placas de sucata | - |
| Fogueira de pedras (`fogueira`) | - | Curativo de pano fervido | - |

## Materiais: de onde vêm e onde entram

| Material | Fase | Grade | Peso | Achado em | Também sai de | Entra em |
|---|---|---|---|---|---|---|
| Carretel de linha e anzóis (`linha_pesca`) | 1 | 1×1 | 0,1 kg | casa_barcos, casas, supermercado, parque_trailers | - | Bolsa de cintura de pano, Vara de pesca improvisada |
| Garrafa PET vazia 2 L (`garrafa_pet`) | 1 | 1×2 | 0,05 kg | casas, rua, supermercado, diner, posto | - | Filtro de água de garrafa |
| Garrafa de álcool 70 % (`alcool`) | 1 | 1×2 | 1,0 kg | supermercado, clinica, casas, posto | - | Curativo de pano fervido, Lamparina de lata, Tocha de pano e álcool |
| Lata vazia (`lata_vazia`) | 1 | 1×1 | 0,06 kg | casas, rua, supermercado, diner, abrigo | comer Lata de feijão (`lata_feijao`) (1), comer Lata de milho (`lata_milho`) (1) | Alarme de latas, Caneca de lata com alça de arame, Chuveiro de balde com cortina de lona, Fogareiro de lata, Lamparina de lata, Lâmpada improvisada no poste |
| Lona dobrada (`lona`) | 1 | 2×2 | 2,5 kg | armazem, fazenda, garagem, parque_trailers, posto | - | Banca de feira com toldo, Barraca de lona com cumeeira, Chuveiro de balde com cortina de lona, Coletor de água da chuva, Maca de campanha dobrável, Mochila de lona improvisada, Torre de vigia |
| Pacote de abraçadeiras de nylon (`abracadeiras`) | 1 | 1×1 | 0,1 kg | garagem, casas, fabrica, cinema, supermercado | - | amarra rápido: armadilhas, lanternas na arma, reparos |
| Pedra de amolar (`pedra_amolar`) | 1 | 1×1 | 0,4 kg | casas, fazenda, serraria, casa_de_campo | - | recupera o fio de facas, facão, machado e lança (sem bancada) |
| Pote de parafusos e porcas (`pote_parafusos`) | 1 | 1×1 | 0,9 kg | garagem, casas, fabrica, serraria | - | Chapa de seteira para janela, Colete de placas de sucata, Grade de janela de vergalhão, Kit de reparo improvisado, Mesa de recarga de munição, Plataforma de tiro de andaime, Porta reforçada com chapa |
| Punhado de pedras (`pedras`) | 1 | 1×1 | 2,0 kg | rua, parque, fazenda, casa_barcos, serraria | - | Estação de tratamento de água em tambores, Filtro de água de garrafa, Filtro de água em barril, Fogueira de pedras, Kit de acender fogo, Memorial aos que se foram, Panelão no tripé sobre fogueira, Poço de pedra com sarilho |
| Punhado de sucata (`sucata_metal`) | 1 | 2×1 | 1,2 kg | ferrovelho, garagem, posto, fabrica, rua | desmontar Carcaça de carro depenada (`carcaca_carro`) (12), desmontar Pilha de sucata (`pilha_sucata`) (8), desmontar Carrinho de compras (`carrinho_compras`) (3), desmontar Arquivo de aço 4 gavetas (`arquivo_aco`) (4), desmontar Estante de aço (5 prateleiras) (`estante_metal`) (4) | Carregador de pilhas, Grade de janela de vergalhão, Kit de acender fogo, Mesa de costura com máquina manual, Panelão no tripé sobre fogueira |
| Rolo de arame liso (`arame_liso`) | 1 | 1×1 | 1,0 kg | armazem, fazenda, serraria, garagem, casa_de_campo | - | Armadilha de laço, Armário de armas de madeira com tela, Caneca de lata com alça de arame, Cavalo de frisa de estacas, Coelheira de tábuas e tela, Composteira de pallets, Kit de reparo improvisado, Torre de rádio da comunidade |
| Trapos amarrados (`trapos`) | 1 | 1×1 | 0,3 kg | casas, lavanderia, hotel, motel, garagem | desmontar Pilha de roupas dobradas (`roupas`) (3), desmontar Cama de solteiro (`cama_solteiro`) (2), desmontar Cama de casal (`cama_casal`) (3) | Bolsa de cintura de pano, Capacete de panela acolchoado, Curativo de pano fervido, Filtro de água de garrafa, Filtro de água em barril, Kit de acender fogo, Kit de reparo improvisado, Lamparina de lata, Mesa de enfermaria improvisada, Mochila de lona improvisada, Tala de tábua e pano, Tocha de pano e álcool |
| Cano de PVC (`tubo_pvc`) | 2 | 4×1 | 0,6 kg | casas, armazem, fabrica, piscina, fazenda | - | Alambique de panela, Estação de tratamento de água em tambores, Estufa de cano e plástico, Filtro de água em barril, Tanque de lavar de cimento |
| Corrente com cadeado (`corrente_cadeado`) | 2 | 2×1 | 2,2 kg | garagem, armazem, delegacia, estacao, parque_trailers | - | Armário de armas de madeira com tela, Baú de aço com cadeado, Panelão no tripé sobre fogueira, Porta reforçada com chapa, Portão principal de chapa com guarita, Sino de alarme de botijão |
| Lata de cola de contato (`cola_contato`) | 2 | 1×1 | 0,3 kg | casas, garagem, serraria, escolinha | - | cola couro, borracha e madeira: proteções, reparo de botas e mochila |
| Molas e engrenagens (`engrenagens`) | 2 | 1×1 | 0,6 kg | fabrica, garagem, relojoaria, casas | desmontar Relógio de parede parado (`relogio_parede`) (2), desmontar Máquina de lavar (`maquina_lavar`) (3), desmontar Vitrola com discos (`vitrola`) (2) | Cata-vento de bomba d'água em torre, Mesa de costura com máquina manual |
| Par de dobradiças (`dobradicas`) | 2 | 1×1 | 0,4 kg | casas, garagem, serraria, armazem | desmontar Guarda-roupa 2 portas (`guarda_roupa`) (2), desmontar Armário aéreo de cozinha (`armario_aereo`) (2) | Armário de armas de madeira com tela, Baú de aço com cadeado, Baú de madeira com cadeado, Caixote grande de tábuas, Portão principal de chapa com guarita |
| Peça de carne defumada (`carne_defumada`) | 2 | 1×1 | 0,6 kg | abrigo, fazenda | fazer Defumador de tábuas (`defumador`) (4) | fome -40; dura 10 dias sem estragar |
| Retalho de couro (`couro`) | 2 | 2×1 | 0,5 kg | casas, fazenda, mansao, concessionaria, cinema | desmontar Poltrona (`poltrona`) (2), desmontar Sofá 3 lugares (`sofa`) (3), desmontar Mesa de booth com dois sofás (`mesa_booth`) (2) | Colete de placas de sucata, Forja de tambor com fole |
| Rolo de fio elétrico (`fio_eletrico`) | 2 | 1×1 | 0,8 kg | casas, fabrica, garagem, cinema, hotel | desmontar Cordão de luzes (`cordao_luzes`) (1), desmontar Abajur (`abajur`) (1) | Bancada de eletrônica, Banco de baterias, Carregador de pilhas, Gerador portátil a gasolina, Holofote em poste com bateria, Lâmpada improvisada no poste, Painéis solares no cavalete com baterias, Poste de luz restaurado, Subestação religada, Torre de rádio da comunidade, Turbina eólica pequena no mastro |
| Saco de adubo de composto (`adubo`) | 2 | 2×2 | 8,0 kg | abrigo, fazenda, supermercado | fazer Composteira de pallets (`composteira`) (1) | canteiro adubado rende 50 % mais por 3 colheitas |
| Saco de carvão (`carvao`) | 2 | 2×2 | 3,0 kg | supermercado, posto, casas, diner, armazem | fazer Fogueira de pedras (`fogueira`) (1) | Estação de tratamento de água em tambores, Filtro de água de garrafa, Filtro de água em barril, Kit de acender fogo |
| Tijolos (`tijolo`) | 2 | 1×1 | 2,4 kg | fabrica, ruinas, casas, armazem | desmontar ruínas (6) | Alambique de panela, Defumador de tábuas, Fogão a lenha de tambor, Forja de tambor com fole, Forno de barro comunitário, Módulo de muralha de blocos com passarela, Portão principal de chapa com guarita, Prateleira de tábuas e tijolos, Tanque de lavar de cimento |
| Carne crua embrulhada (`carne_crua`) | 3 | 1×1 | 0,8 kg | fazenda | fazer Coelheira de tábuas e tela (`coelheira`) (2) | estraga em 2 dias: cozinhe no panelão ou defume |
| Cesto de legumes da estufa (`cesto_legumes`) | 3 | 2×2 | 2,5 kg | fazenda | fazer Estufa de cano e plástico (`estufa`) (1) | alface, tomate e cenoura: comida fresca que espanta a fraqueza |
| Motor elétrico pequeno (`motor_eletrico`) | 3 | 2×1 | 1,6 kg | casas, fabrica, garagem, lavanderia | desmontar Máquina de lavar (`maquina_lavar`) (1), desmontar Aquecedor a óleo (`aquecedor`) (1), desmontar Compressor de ar com tanque (`compressor_ar`) (1) | Gerador portátil a gasolina, Subestação religada, Turbina eólica pequena no mastro |
| Placa de circuito (`placa_circuito`) | 3 | 1×1 | 0,2 kg | casas, escritorio, cinema, delegacia, correios | desmontar Rack com TV (`rack_tv`) (2), desmontar TV de tubo com tela rachada (`tv_tubo`) (2), desmontar Rádio portátil (`radio_portatil`) (1) | Bancada de eletrônica, Carregador de pilhas, Holofote em poste com bateria, Painéis solares no cavalete com baterias, Poste de luz restaurado, Subestação religada, Torre de rádio da comunidade |
| Pão caseiro do forno da vila (`pao_caseiro`) | 4 | 1×1 | 0,4 kg | padaria, fazenda | fazer Forno de barro comunitário (`forno_comunitario`) (12) | mata a fome e dá +moral; dura 4 dias |
| Saco de cimento 25 kg (`cimento`) | 4 | 3×2 | 25,0 kg | armazem, fabrica, garagem_vertical, ruinas | - | Módulo de muralha de blocos com passarela, Portão principal de chapa com guarita, Poço de pedra com sarilho, Subestação religada, Tanque de lavar de cimento |

## Armazenamento do abrigo

| Peça | Fase | Guarda | Grade | Vagas de armas | Prateleiras | Estoque |
|---|---|---|---|---|---|---|
| Baú de madeira com cadeado (`bau_madeira`) | 1 | tudo | 8×5 | - | - | - |
| Caixa de ferramentas de metal (`caixa_ferramentas`) | 1 | ferramentas, materiais, armas | 4×2 | - | - | - |
| Caixa organizadora empilhável (`caixa_organizadora`) | 1 | tudo | 4×3 | - | - | - |
| Caixote grande de tábuas (`caixote_grande`) | 1 | tudo | 10×6 | - | - | - |
| Lenheiro coberto (`lenheiro`) | 1 | - | - | - | - | até 30 × Feixe de lenha (`lenha`) |
| Prateleira de tábuas e tijolos (`prateleira_improvisada`) | 1 | tudo | 6×3 | - | 3 | - |
| Suporte de parede para armas (`rack_armas_parede`) | 1 | - | - | 4 longa, 3 branca | - | - |
| Armário de armas de madeira com tela (`armario_armas_abrigo`) | 2 | armas, municao, acessorios | 6×4 | 6 longa, 4 curta, 3 branca | 1 | - |
| Baú de aço com cadeado (`bau_aco`) | 2 | tudo | 12×8 | - | - | - |
| Caixote militar verde (`caixa_militar`) | 2 | tudo | 6×4 | - | - | - |
| Cofre de armas de aço (`cofre_armas`) | 2 | armas, municao, acessorios, remedios | 6×5 | 6 longa, 4 curta | 1 | - |
| Estante aramada com rodinhas (`estante_aramada`) | 2 | tudo | 6×4 | - | 4 | - |
| Estante de despensa com caixotes (`despensa`) | 2 | comida, agua, remedios | 8×4 | - | 4 | - |
| Pallet de sucata separada (`pallet_sucata`) | 2 | - | - | - | - | até 60 × Punhado de sucata (`sucata_metal`) |
| Pallet de tijolos (`pallet_tijolos`) | 2 | - | - | - | - | até 120 × Tijolos (`tijolo`) |
| Pallet de tábuas cintadas (`pallet_tabuas`) | 2 | - | - | - | - | até 48 × Tábua de madeira (`tabua`) |
| Pilha de sacos de areia no pallet (`pallet_sacos_areia`) | 2 | - | - | - | - | até 18 × Saco de areia (`saco_areia`) |
| Pallet de sacos de cimento (`pallet_cimento`) | 4 | - | - | - | - | até 20 × Saco de cimento 25 kg (`cimento`) |

