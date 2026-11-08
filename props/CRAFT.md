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
| Baú de madeira com cadeado (`bau_madeira`) | 14 | 5× Tábua de madeira (`tabua`), 1× Par de dobradiças (`dobradicas`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
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
| Armário de armas de madeira com tela (`armario_armas_abrigo`) | 14 | 8× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`), 1× Par de dobradiças (`dobradicas`), 1× Corrente com cadeado (`corrente_cadeado`), 1× Rolo de arame liso (`arame_liso`) | Martelo de unha (`martelo`) | - | - |
| Estante de despensa com caixotes (`despensa`) | 14 | 10× Tábua de madeira (`tabua`), 1× Caixa de pregos (`caixa_pregos`) | Martelo de unha (`martelo`) | - | - |
| Colete de placas de sucata (`colete_sucata`) | 15 | 1× Chapa de metal ondulada (`chapa_metal`), 2× Retalho de couro (`couro`), 1× Pote de parafusos e porcas (`pote_parafusos`), 1× Rolo de corda (`corda`) | Martelo de unha (`martelo`) | Bancada de trabalho com morsa (`bancada_trabalho`) | 240 s |

## Materiais: de onde vêm e onde entram

| Material | Fase | Grade | Peso | Achado em | Também sai de | Entra em |
|---|---|---|---|---|---|---|
| Armadilha de laço (`armadilha_laco`) | 1 | 2×1 | 0,4 kg | abrigo | - | montada no mato pega coelho ou pombo (comida 2) em até 1 dia; zumbi pisa e fica preso 5 s |
| Bolsa de cintura de pano (`bolsa_cintura`) | 1 | 2×1 | 0,3 kg | abrigo | - | +3 × 2 células de acesso rápido (usar sem abrir a mochila) |
| Caneca de lata com alça de arame (`caneca_lata`) | 1 | 1×1 | 0,1 kg | abrigo | - | ferve 0,4 L de água na fogueira (água fervida não dá doença) |
| Capacete de panela acolchoado (`capacete_panela`) | 1 | 2×2 | 1,0 kg | abrigo | - | +20 de proteção na cabeça; tira 10 % da audição |
| Carretel de linha e anzóis (`linha_pesca`) | 1 | 1×1 | 0,1 kg | casa_barcos, casas, supermercado, parque_trailers | - | Bolsa de cintura de pano, Vara de pesca improvisada |
| Colete de revistas e fita (`colete_revistas`) | 1 | 3×2 | 1,4 kg | abrigo | - | +15 de proteção contra mordida no tronco e nos braços; desgasta a cada mordida |
| Curativo de pano fervido (`curativo_improvisado`) | 1 | 1×1 | 0,05 kg | abrigo | - | para sangramento (cura 15); 20 % de chance de infeccionar se o pano não foi fervido |
| Filtro de água de garrafa (`filtro_garrafa`) | 1 | 1×2 | 0,6 kg | abrigo | - | tira a sujeira da água de chuva ou do rio (ainda precisa ferver); 20 litros antes de trocar o carvão |
| Fogareiro de lata (`fogareiro_lata`) | 1 | 1×1 | 0,3 kg | abrigo | - | cozinha e ferve água com gravetos ou carvão (fumaça baixa, chama escondida) |
| Garrafa PET vazia 2 L (`garrafa_pet`) | 1 | 1×2 | 0,05 kg | casas, rua, supermercado, diner, posto | - | Filtro de água de garrafa |
| Garrafa de álcool 70 % (`alcool`) | 1 | 1×2 | 1,0 kg | supermercado, clinica, casas, posto | - | Curativo de pano fervido, Lamparina de lata, Tocha de pano e álcool |
| Kit de acender fogo (`kit_fogo`) | 1 | 1×1 | 0,15 kg | abrigo, casa_de_campo, parque_trailers | - | acende fogueira sem isqueiro (30 usos); funciona molhado |
| Kit de reparo improvisado (`kit_reparo`) | 1 | 2×1 | 0,8 kg | abrigo, garagem | - | repara arma branca (+40 % de durabilidade) ou barricada (+60 de vida); 3 usos |
| Lamparina de lata (`lamparina_lata`) | 1 | 1×1 | 0,25 kg | abrigo | - | luz fraca de 3 m por 6 horas (gasta álcool); dá para deixar acesa no abrigo |
| Lata vazia (`lata_vazia`) | 1 | 1×1 | 0,06 kg | casas, rua, supermercado, diner, abrigo | comer Lata de feijão (`lata_feijao`) (1), comer Lata de milho (`lata_milho`) (1) | Alarme de latas, Caneca de lata com alça de arame, Fogareiro de lata, Lamparina de lata |
| Lona dobrada (`lona`) | 1 | 2×2 | 2,5 kg | armazem, fazenda, garagem, parque_trailers, posto | - | Coletor de água da chuva, Mochila de lona improvisada, Torre de vigia |
| Mochila de lona improvisada (`mochila_lona`) | 1 | 2×3 | 0,8 kg | abrigo | - | mochila de 4 × 4 células (a de loja tem 5 × 6); faz barulho de lona ao correr |
| Pacote de abraçadeiras de nylon (`abracadeiras`) | 1 | 1×1 | 0,1 kg | garagem, casas, fabrica, cinema, supermercado | - | amarra rápido: armadilhas, lanternas na arma, reparos |
| Pedra de amolar (`pedra_amolar`) | 1 | 1×1 | 0,4 kg | casas, fazenda, serraria, casa_de_campo | - | recupera o fio de facas, facão, machado e lança (sem bancada) |
| Pote de parafusos e porcas (`pote_parafusos`) | 1 | 1×1 | 0,9 kg | garagem, casas, fabrica, serraria | - | Colete de placas de sucata, Kit de reparo improvisado |
| Punhado de pedras (`pedras`) | 1 | 1×1 | 2,0 kg | rua, parque, fazenda, casa_barcos, serraria | - | Filtro de água de garrafa, Fogueira de pedras, Kit de acender fogo |
| Punhado de sucata (`sucata_metal`) | 1 | 2×1 | 1,2 kg | ferrovelho, garagem, posto, fabrica, rua | desmontar Carcaça de carro depenada (`carcaca_carro`) (12), desmontar Pilha de sucata (`pilha_sucata`) (8), desmontar Carrinho de compras (`carrinho_compras`) (3), desmontar Arquivo de aço 4 gavetas (`arquivo_aco`) (4), desmontar Estante de aço (5 prateleiras) (`estante_metal`) (4) | Kit de acender fogo |
| Rolo de arame liso (`arame_liso`) | 1 | 1×1 | 1,0 kg | armazem, fazenda, serraria, garagem, casa_de_campo | - | Armadilha de laço, Armário de armas de madeira com tela, Caneca de lata com alça de arame, Kit de reparo improvisado |
| Tala de tábua e pano (`tala_improvisada`) | 1 | 2×1 | 0,6 kg | abrigo | - | trata perna ou braço quebrado: volta a correr em 1 dia em vez de 4 |
| Tocha de pano e álcool (`tocha`) | 1 | 3×1 | 0,5 kg | abrigo | - | luz de 6 m por 10 min; afasta um zumbi encostado (fogo), mas a chama chama outros de longe |
| Trapos amarrados (`trapos`) | 1 | 1×1 | 0,3 kg | casas, lavanderia, hotel, motel, garagem | desmontar Pilha de roupas dobradas (`roupas`) (3), desmontar Cama de solteiro (`cama_solteiro`) (2), desmontar Cama de casal (`cama_casal`) (3) | Bolsa de cintura de pano, Capacete de panela acolchoado, Curativo de pano fervido, Filtro de água de garrafa, Kit de acender fogo, Kit de reparo improvisado, Lamparina de lata, Mochila de lona improvisada, Tala de tábua e pano, Tocha de pano e álcool |
| Vara de pesca improvisada (`vara_pesca`) | 1 | 5×1 | 0,4 kg | abrigo, casa_barcos | - | pesca no lago (comida 3 a cada 20 min, em silêncio) |
| Cano de PVC (`tubo_pvc`) | 2 | 4×1 | 0,6 kg | casas, armazem, fabrica, piscina, fazenda | - | calhas, coletor de chuva, irrigação da horta e filtros |
| Colete de placas de sucata (`colete_sucata`) | 2 | 3×3 | 4,5 kg | abrigo, ferrovelho | - | +35 de proteção; pesado (correr cansa 30 % mais rápido) e barulhento |
| Corrente com cadeado (`corrente_cadeado`) | 2 | 2×1 | 2,2 kg | garagem, armazem, delegacia, estacao, parque_trailers | - | Armário de armas de madeira com tela |
| Lata de cola de contato (`cola_contato`) | 2 | 1×1 | 0,3 kg | casas, garagem, serraria, escolinha | - | cola couro, borracha e madeira: proteções, reparo de botas e mochila |
| Molas e engrenagens (`engrenagens`) | 2 | 1×1 | 0,6 kg | fabrica, garagem, relojoaria, casas | desmontar Relógio de parede parado (`relogio_parede`) (2), desmontar Máquina de lavar (`maquina_lavar`) (3), desmontar Vitrola com discos (`vitrola`) (2) | mecanismos: armadilhas, besta, bomba d'água, cata-vento |
| Par de dobradiças (`dobradicas`) | 2 | 1×1 | 0,4 kg | casas, garagem, serraria, armazem | desmontar Guarda-roupa 2 portas (`guarda_roupa`) (2), desmontar Armário aéreo de cozinha (`armario_aereo`) (2) | Armário de armas de madeira com tela, Baú de madeira com cadeado |
| Retalho de couro (`couro`) | 2 | 2×1 | 0,5 kg | casas, fazenda, mansao, concessionaria, cinema | desmontar Poltrona (`poltrona`) (2), desmontar Sofá 3 lugares (`sofa`) (3), desmontar Mesa de booth com dois sofás (`mesa_booth`) (2) | Colete de placas de sucata |
| Rolo de fio elétrico (`fio_eletrico`) | 2 | 1×1 | 0,8 kg | casas, fabrica, garagem, cinema, hotel | desmontar Cordão de luzes (`cordao_luzes`) (1), desmontar Abajur (`abajur`) (1) | ligar luzes, alarmes, gerador e painel solar (10 m) |
| Saco de carvão (`carvao`) | 2 | 2×2 | 3,0 kg | supermercado, posto, casas, diner, armazem | fazer Fogueira de pedras (`fogueira`) (1) | Filtro de água de garrafa, Kit de acender fogo |
| Tijolos (`tijolo`) | 2 | 1×1 | 2,4 kg | fabrica, ruinas, casas, armazem | desmontar ruínas (6) | Prateleira de tábuas e tijolos |
| Motor elétrico pequeno (`motor_eletrico`) | 3 | 2×1 | 1,6 kg | casas, fabrica, garagem, lavanderia | desmontar Máquina de lavar (`maquina_lavar`) (1), desmontar Aquecedor a óleo (`aquecedor`) (1), desmontar Compressor de ar com tanque (`compressor_ar`) (1) | gera energia girando (cata-vento, bicicleta-gerador) ou move bomba d'água |
| Placa de circuito (`placa_circuito`) | 3 | 1×1 | 0,2 kg | casas, escritorio, cinema, delegacia, correios | desmontar Rack com TV (`rack_tv`) (2), desmontar TV de tubo com tela rachada (`tv_tubo`) (2), desmontar Rádio portátil (`radio_portatil`) (1) | eletrônica: rádio, holofote, painel solar |
| Saco de cimento 25 kg (`cimento`) | 4 | 3×2 | 25,0 kg | armazem, fabrica, garagem_vertical, ruinas | - | muralha de concreto, cisterna, reforma de prédios (fase 4) |

## Armazenamento do abrigo

| Peça | Fase | Guarda | Grade | Vagas de armas | Prateleiras | Estoque |
|---|---|---|---|---|---|---|
| Baú de madeira com cadeado (`bau_madeira`) | 1 | tudo | 8×5 | - | - | - |
| Caixa de ferramentas de metal (`caixa_ferramentas`) | 1 | ferramentas, materiais, armas | 4×2 | - | - | - |
| Caixa organizadora empilhável (`caixa_organizadora`) | 1 | tudo | 4×3 | - | - | - |
| Lenheiro coberto (`lenheiro`) | 1 | - | - | - | - | até 30 × Feixe de lenha (`lenha`) |
| Prateleira de tábuas e tijolos (`prateleira_improvisada`) | 1 | tudo | 6×3 | - | 3 | - |
| Suporte de parede para armas (`rack_armas_parede`) | 1 | - | - | 4 longa, 3 branca | - | - |
| Armário de armas de madeira com tela (`armario_armas_abrigo`) | 2 | armas, municao, acessorios | 6×4 | 6 longa, 4 curta, 3 branca | 1 | - |
| Caixote militar verde (`caixa_militar`) | 2 | tudo | 6×4 | - | - | - |
| Cofre de armas de aço (`cofre_armas`) | 2 | armas, municao, acessorios, remedios | 6×5 | 6 longa, 4 curta | 1 | - |
| Estante aramada com rodinhas (`estante_aramada`) | 2 | tudo | 6×4 | - | 4 | - |
| Estante de despensa com caixotes (`despensa`) | 2 | comida, agua, remedios | 8×4 | - | 4 | - |
| Pallet de sucata separada (`pallet_sucata`) | 2 | - | - | - | - | até 60 × Punhado de sucata (`sucata_metal`) |
| Pallet de tijolos (`pallet_tijolos`) | 2 | - | - | - | - | até 120 × Tijolos (`tijolo`) |
| Pallet de tábuas cintadas (`pallet_tabuas`) | 2 | - | - | - | - | até 48 × Tábua de madeira (`tabua`) |
| Pilha de sacos de areia no pallet (`pallet_sacos_areia`) | 2 | - | - | - | - | até 18 × Saco de areia (`saco_areia`) |
| Pallet de sacos de cimento (`pallet_cimento`) | 4 | - | - | - | - | até 20 × Saco de cimento 25 kg (`cimento`) |

