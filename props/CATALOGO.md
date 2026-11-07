# Catálogo de mobílias e loot

Gerado por `props/gerar_props.py` a partir de `mobilias/catalogo.json` e `loot/catalogo.json`. Medidas em metros (largura × altura × profundidade).

## Mobílias

| Item | Cômodo | Medidas | Revistar | Partes móveis | Uso no jogo | Triângulos |
|---|---|---|---|---|---|---|
| Geladeira duplex (`geladeira`) | Cozinha | 0,70 × 1,76 × 0,71 | 12 espaços: comida, agua, remedios | porta_geladeira, porta_freezer | barricada | 1780 |
| Fogão 4 bocas (`fogao`) | Cozinha | 0,56 × 0,98 × 0,64 | 4 espaços: comida, utensilios | gaveta, porta_forno | - | 4784 |
| Balcão com pia (`balcao_pia`) | Cozinha | 1,22 × 1,23 × 0,63 | 6 espaços: utensilios, limpeza, ferramentas | porta_esq, porta_dir | - | 2408 |
| Estante de aço (5 prateleiras) (`estante_metal`) | Depósito | 1,02 × 1,90 × 0,42 | 10 espaços: ferramentas, materiais, comida | - | - | 5264 |
| Guarda-roupa 2 portas (`guarda_roupa`) | Quarto | 1,05 × 2,00 × 0,61 | 10 espaços: roupas, tecido, mochila | porta_esq, porta_dir, gaveta | barricada | 2444 |
| Cômoda 3 gavetas (`comoda`) | Quarto | 0,93 × 0,85 × 0,47 | 6 espaços: roupas, remedios, pilhas | gaveta_1, gaveta_2, gaveta_3 | - | 2100 |
| Criado-mudo (`criado_mudo`) | Quarto | 0,47 × 0,56 × 0,42 | 3 espaços: remedios, pilhas, livros | gaveta | - | 1740 |
| Cama de casal (`cama_casal`) | Quarto | 1,48 × 1,05 × 1,98 | - | - | dormir | 11820 |
| Cama de solteiro (`cama_solteiro`) | Quarto | 0,98 × 1,05 × 1,98 | - | - | dormir | 10076 |
| Mesa de jantar (`mesa_jantar`) | Sala | 1,40 × 0,76 × 0,80 | - | - | barricada | 1820 |
| Cadeira de madeira (`cadeira`) | Sala | 0,42 × 0,95 × 0,48 | - | - | sentar | 1872 |
| Sofá 3 lugares (`sofa`) | Sala | 1,93 × 0,88 × 0,87 | 2 espaços: moedas, pilhas | - | barricada, dormir, sentar | 12624 |
| Armário de banheiro com espelho (`armario_banheiro`) | Banheiro | 0,52 × 0,70 × 0,17 | 4 espaços: remedios, higiene | porta_espelho | - | 348 |
| Caixote de madeira (`caixa_madeira`) | Depósito | 0,84 × 0,56 × 0,64 | 8 espaços: comida, materiais, ferramentas, armas | tampa | barricada | 1972 |

## Loot

| Item | Categoria | Recurso | Rende | Peso | Empilha | Efeito | Aparece em |
|---|---|---|---|---|---|---|---|
| Lata de feijão (`lata_feijao`) | Comida | comida | 1 | 0,45 kg | 10 | fome -25 | supermercado, casas, galeria, diner, armazem |
| Lata de sardinha (`lata_sardinha`) | Comida | comida | 1 | 0,13 kg | 12 | fome -15 | supermercado, casas, diner |
| Pacote de arroz 1 kg (`pacote_arroz`) | Comida | comida | 2 | 1,0 kg | 5 | precisa cozinhar: rende 4 refeições | supermercado, casas, armazem, padaria |
| Caixa de flocos de milho (`caixa_cereal`) | Comida | comida | 1 | 0,3 kg | 4 | fome -20 | supermercado, casas, escolinha |
| Garrafa de água 1,5 L (`garrafa_agua`) | Água | agua | 1 | 1,55 kg | 6 | sede -40 | supermercado, casas, posto, diner, galeria |
| Galão de água 5 L (`galao_agua`) | Água | agua | 4 | 5,2 kg | 1 | sede -40 por uso, 5 usos | supermercado, posto, quartel, galeria |
| Kit de primeiros socorros (`kit_medico`) | Remédios | remedios | 6 | 0,8 kg | 1 | cura 60 e para sangramento | quartel, escolinha, casas, motel, galeria |
| Frasco de comprimidos (`frasco_remedio`) | Remédios | remedios | 3 | 0,08 kg | 10 | cura doença / alivia dor | casas, motel, quartel, galeria |
| Rolo de atadura (`atadura`) | Remédios | remedios | 1 | 0,03 kg | 10 | para sangramento | casas, quartel, escolinha, motel |
| Martelo de unha (`martelo`) | Ferramentas | ferramenta | 4 | 0,6 kg | 1 | constrói e repara; arma corpo a corpo leve (dano 20) | casas, garagem, armazem, quartel |
| Pé de cabra (`pe_de_cabra`) | Armas improvisadas | ferramenta | 5 | 1,2 kg | 1 | abre portas trancadas e caixotes; arma corpo a corpo (dano 30) | garagem, quartel, estacao, armazem |
| Machado (`machado`) | Armas improvisadas | ferramenta | 8 | 1,6 kg | 1 | corta lenha e arromba; arma corpo a corpo forte (dano 45) | quartel, armazem, casa_de_campo, garagem |
| Chave inglesa (`chave_inglesa`) | Ferramentas | ferramenta | 3 | 0,45 kg | 1 | desmonta sucata e repara geradores (dano 15) | garagem, posto, quartel, casas |
| Lanterna (`lanterna`) | Ferramentas | ferramenta | 4 | 0,3 kg | 1 | luz na mão (gasta pilhas) | casas, quartel, posto, correios |
| Taco de madeira (`taco_madeira`) | Armas improvisadas | arma | 3 | 0,9 kg | 1 | arma corpo a corpo de alcance médio (dano 25) | casas, escolinha, garagem |
| Tábua de madeira (`tabua`) | Materiais de construção | madeira | 1 | 2,0 kg | 10 | barricadas e construção (1 madeira) | armazem, casas, estacao, quartel, deposito |
| Caixa de pregos (`caixa_pregos`) | Materiais de construção | sucata | 2 | 0,5 kg | 5 | construção: 20 pregos | armazem, garagem, casas, deposito |
| Fita adesiva prata (`fita_adesiva`) | Materiais de construção | sucata | 2 | 0,2 kg | 5 | repara armas e barricadas; ingrediente de receitas | casas, garagem, galeria, correios |
| Chapa de metal ondulada (`chapa_metal`) | Materiais de construção | sucata | 2 | 4,0 kg | 4 | construção: 2 sucata (muros e telhados) | armazem, posto, estacao, quartel |
| Cano de ferro (`cano_metal`) | Armas improvisadas | sucata | 2 | 1,4 kg | 4 | 1 sucata ou arma corpo a corpo (dano 22) | garagem, armazem, estacao, posto |
| Galão de gasolina 20 L (`galao_gasolina`) | Combustível | combustivel | 10 | 16,0 kg | 1 | abastece gerador (8 horas) | posto, garagem, quartel, armazem |
| Cartela de pilhas AA (`pilhas`) | Energia | energia | 3 | 0,1 kg | 10 | 4 cargas para lanterna e rádio | casas, correios, galeria, posto, supermercado |
