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

## Materiais: de onde vêm e onde entram

| Material | Fase | Grade | Peso | Achado em | Também sai de | Entra em |
|---|---|---|---|---|---|---|
| Carretel de linha e anzóis (`linha_pesca`) | 1 | 1×1 | 0,1 kg | casa_barcos, casas, supermercado, parque_trailers | - | vara de pesca, armadilha de linha e costura de ferimento |
| Garrafa PET vazia 2 L (`garrafa_pet`) | 1 | 1×2 | 0,05 kg | casas, rua, supermercado, diner, posto | - | filtro de água, coletor, armadilha de garrafa e isca |
| Garrafa de álcool 70 % (`alcool`) | 1 | 1×2 | 1,0 kg | supermercado, clinica, casas, posto | - | desinfeta ferimento, acende fogo, combustível da lamparina e do molotov |
| Lata vazia (`lata_vazia`) | 1 | 1×1 | 0,06 kg | casas, rua, supermercado, diner, abrigo | comer Lata de feijão (`lata_feijao`) (1), comer Lata de milho (`lata_milho`) (1) | Alarme de latas |
| Lona dobrada (`lona`) | 1 | 2×2 | 2,5 kg | armazem, fazenda, garagem, parque_trailers, posto | - | Coletor de água da chuva, Torre de vigia |
| Pacote de abraçadeiras de nylon (`abracadeiras`) | 1 | 1×1 | 0,1 kg | garagem, casas, fabrica, cinema, supermercado | - | amarra rápido: armadilhas, lanternas na arma, reparos |
| Pedra de amolar (`pedra_amolar`) | 1 | 1×1 | 0,4 kg | casas, fazenda, serraria, casa_de_campo | - | recupera o fio de facas, facão, machado e lança (sem bancada) |
| Pote de parafusos e porcas (`pote_parafusos`) | 1 | 1×1 | 0,9 kg | garagem, casas, fabrica, serraria | - | fixa peças: armas, bancadas, portas reforçadas |
| Punhado de pedras (`pedras`) | 1 | 1×1 | 2,0 kg | rua, parque, fazenda, casa_barcos, serraria | - | Fogueira de pedras |
| Punhado de sucata (`sucata_metal`) | 1 | 2×1 | 1,2 kg | ferrovelho, garagem, posto, fabrica, rua | desmontar Carcaça de carro depenada (`carcaca_carro`) (12), desmontar Pilha de sucata (`pilha_sucata`) (8), desmontar Carrinho de compras (`carrinho_compras`) (3), desmontar Arquivo de aço 4 gavetas (`arquivo_aco`) (4), desmontar Estante de aço (5 prateleiras) (`estante_metal`) (4) | 1 sucata: base de quase toda receita de metal |
| Rolo de arame liso (`arame_liso`) | 1 | 1×1 | 1,0 kg | armazem, fazenda, serraria, garagem, casa_de_campo | - | Armário de armas de madeira com tela |
| Trapos amarrados (`trapos`) | 1 | 1×1 | 0,3 kg | casas, lavanderia, hotel, motel, garagem | desmontar Pilha de roupas dobradas (`roupas`) (3), desmontar Cama de solteiro (`cama_solteiro`) (2), desmontar Cama de casal (`cama_casal`) (3) | curativo, tocha, filtro, remendo e pavio de molotov |
| Cano de PVC (`tubo_pvc`) | 2 | 4×1 | 0,6 kg | casas, armazem, fabrica, piscina, fazenda | - | calhas, coletor de chuva, irrigação da horta e filtros |
| Corrente com cadeado (`corrente_cadeado`) | 2 | 2×1 | 2,2 kg | garagem, armazem, delegacia, estacao, parque_trailers | - | Armário de armas de madeira com tela |
| Lata de cola de contato (`cola_contato`) | 2 | 1×1 | 0,3 kg | casas, garagem, serraria, escolinha | - | cola couro, borracha e madeira: proteções, reparo de botas e mochila |
| Molas e engrenagens (`engrenagens`) | 2 | 1×1 | 0,6 kg | fabrica, garagem, relojoaria, casas | desmontar Relógio de parede parado (`relogio_parede`) (2), desmontar Máquina de lavar (`maquina_lavar`) (3), desmontar Vitrola com discos (`vitrola`) (2) | mecanismos: armadilhas, besta, bomba d'água, cata-vento |
| Par de dobradiças (`dobradicas`) | 2 | 1×1 | 0,4 kg | casas, garagem, serraria, armazem | desmontar Guarda-roupa 2 portas (`guarda_roupa`) (2), desmontar Armário aéreo de cozinha (`armario_aereo`) (2) | Armário de armas de madeira com tela, Baú de madeira com cadeado |
| Retalho de couro (`couro`) | 2 | 2×1 | 0,5 kg | casas, fazenda, mansao, concessionaria, cinema | desmontar Poltrona (`poltrona`) (2), desmontar Sofá 3 lugares (`sofa`) (3), desmontar Mesa de booth com dois sofás (`mesa_booth`) (2) | protetor de braço anti-mordida, coldre, alças e botas |
| Rolo de fio elétrico (`fio_eletrico`) | 2 | 1×1 | 0,8 kg | casas, fabrica, garagem, cinema, hotel | desmontar Cordão de luzes (`cordao_luzes`) (1), desmontar Abajur (`abajur`) (1) | ligar luzes, alarmes, gerador e painel solar (10 m) |
| Saco de carvão (`carvao`) | 2 | 2×2 | 3,0 kg | supermercado, posto, casas, diner, armazem | fazer Fogueira de pedras (`fogueira`) (1) | combustível da forja e do defumador; carvão moído vai no filtro de água |
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

