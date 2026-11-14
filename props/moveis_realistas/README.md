# Móveis refeitos no nível da M4A1

Móveis modelados no Blender por script (`bpy`), com texturas PBR assadas (desgaste nas arestas,
sujeira nos cantos, letreiros), pelo mesmo método das armas de `props/armas/m4a1`. Cada móvel
substitui o de mesmo id em `props/mobilias/` (mesmas medidas, mesmos nós de porta), então o
jogo e a ambientação dos kits continuam valendo. O registro em `mobilias/catalogo.json` ganha
`"gerador"`, e o `gerar_props.py` deixa esses itens como estão.

```
moveis_realistas/
  base.py                    primitivas em mm nas coordenadas do jogo (x largura, y altura, +z frente)
  armario_armas/
    modelo.py                as peças: corpo, interior, porta_esq, porta_dir
    materiais.py             classes de material (tinta sobre aço, feltro, zincado...)
    gerar.py                 monta, assa e grava props/mobilias/armario_armas.glb + catálogo
    ver.py, foto.py          fotos de conferência (formas sem textura; GLB pronto)
```

Refazer: `pip install bpy pillow numpy`, depois `python3 moveis_realistas/armario_armas/gerar.py 2048 /tmp/saida`
(cerca de 9 min em 4 núcleos; `REASSAR=A` refaz só um grupo de textura).

## Armário de armas de aço (`armario_armas`)

1,0 × 1,9 × 0,5 m, 12,5 mil triângulos, 3 conjuntos de textura (carcaça 2048, interior 1024, portas 2048).
Duas portas com venezianas (`porta_esq`, `porta_dir`, origem na dobradiça). Dentro: bandeja de borracha
para as coronhas, barra com 5 berços para os canos, prateleira de feltro para pistolas e prateleira de munição.

### Vagas (`vagas_armas` no catálogo)

É o que o jogo usa para pôr as armas **à mostra** dentro do armário (em vez de uma tela de saque).
Medidas em metros, no espaço do móvel. `parte` é o índice da porta (em `partes`) que cobre a vaga.

| tipo | quantas | como a peça fica |
|---|---|---|
| `longa` | 5 | em pé: coronha na bandeja (`pos`), eixo do cano passando pelo berço (`apoio` = [altura, z]), girada `giro_graus` (55°) para mostrar o perfil; até `comprimento_max_m` |
| `curta` | 4 | pistola, revólver ou submetralhadora curta em pé na prateleira de feltro, de perfil, centrada em `pos` |
| `prateleira` | 6 | caixas de munição e miudezas, centradas em `pos`; até `largura_max_m` |

## Bancada de carpintaria com morsa (`bancada_carpintaria`)

2,04 × 1,13 × 0,83 m, 8,8 mil triângulos, 3 conjuntos de textura (estrutura 2048, tampo e morsa 2048,
ferragens e ferramentas 1024). Caibros e tábuas aparafusados, morsa de madeira na frente com uma tábua presa,
prateleira embaixo com sobras, serrote pendurado na ponta direita, plaina, esquadro, grampo sargento,
lata de pregos e lápis. Nós: `estrutura`, `tampo`, `morsa`, `ferragens`, `ferramentas` (as ferramentas ficam
num nó só delas, para o jogo poder escondê-las). O sufixo das classes de madeira (`_x`, `_y`, `_z`) diz para
que lado corre o veio. Refazer: `python3 moveis_realistas/bancada_carpintaria/gerar.py 2048 /tmp/saida` (cerca de 10 min).

## Forja de tambor com fole (`forja_tambor`)

2,08 × 0,82 × 0,60 m, 6,9 mil triângulos, 3 conjuntos de textura (tambor, tijolos e carvão 2048; fole 1024;
bigorna e ferramentas 1024). Tambor de 200 L enferrujado sobre duas fiadas de tijolos, boca forrada de barro
rachado, carvão, fole de couro num cavalete soprando por um cano, bigorna de trilho pregada num toco, martelo e tenaz.
Nós: `fornalha`, `carvao`, `brasa`, `fole`, `bigorna`, `ferramentas`. A malha `brasa` brilha sozinha e o jogo só a
mostra com a forja acesa; `ponto_fogo` no catálogo diz onde nascem a chama e a luz. O envelhecimento de cada classe
(ferrugem escorrida, fuligem, casca, couro enrugado, barro rachado) está em `forja_tambor/materiais.py` (`VELHO`).

## Fogueira de pedras (`fogueira`)

0,95 × 0,44 × 0,90 m, 7,6 mil triângulos, 2 conjuntos de textura 1024 (pedras e cinza; lenha). Roda de pedras de rio
tisnadas por dentro, cama de cinza com miolo de carvão, seis achas em tenda com o pé já queimado e três tocos
carbonizados. Nós: `pedras`, `cinzas`, `lenha`, `brasa` (brilha sozinha; o jogo só a mostra com o fogo aceso).
As pedras são esferas amassadas por ruído (`modelo.pedra`), que servem para outras peças.

## Bancada de eletrônica (`bancada_eletronica`)

1,52 × 1,29 × 0,62 m, 12,9 mil triângulos, 2 conjuntos de textura 2048 (estrutura e tampo; bateria e o que fica em cima).
Mesa de tábuas com prateleira alta e painel de compensado, bateria de carro embaixo com os cabos subindo até a régua
de bornes, rádio de válvulas aberto, placa de circuito com trilhas, ferro de solda no suporte de mola, multímetro com
as pontas, carretéis de fio, gaveteiro de pecinhas, luminária, chaves e alicate. Nós: `estrutura`, `tampo`, `bateria`,
`ferramentas`.


## Bancada de trabalho com morsa (`bancada_trabalho`)

1,82 × 1,75 × 0,74 m, 15,3 mil triângulos, 3 conjuntos de textura (estrutura e painel 2048; tampo, gaveta e morsa 2048;
ferramentas e prateleira 1024). A bancada de oficina das garagens: cantoneira pintada com ferrugem, tampo de três
pranchas com chapa de bater, morsa de ferro fundido com base giratória, painel perfurado (os furos são da textura,
classe `eucatex`) com martelo, arco de serra, alicate, chaves combinadas e chaves de fenda, e embaixo a caixa de
ferramentas, um galão e um rolo de fio. Nós: `estrutura`, `painel`, `tampo`, `gaveta` (desliza 0,35 m para a frente,
como no catálogo), `morsa`, `ferramentas`, `prateleira`.


## Caixote grande de tábuas (`caixote_grande`)

1,53 × 0,69 × 0,78 m, 9,4 mil triângulos, 3 conjuntos de textura (corpo 2048; tampa 1024; ferragens e alças 1024).
Caixa de guardar grande feita à mão: tábuas pregadas em sarrafos, três patins embaixo, tampa de cinco tábuas com três
travessas, duas dobradiças de cinta, aldrava na frente, alças de corda nos lados e ESTOQUE pintado na frente.
Oco por dentro. Nós: `corpo`, `letreiro`, `ferragens`, `alcas`, `tampa` (origem na dobradiça de trás, abre −100° em x)
com `tampa_ferragens` dentro. No jogo é um contêiner de uma grade só de **10 × 6** (60 espaços), construído com
8 tábuas, 2 caixas de pregos e 1 par de dobradiças, com martelo, sem bancada (fase 1).

## Baú de aço com cadeado (`bau_aco`)

1,58 × 0,69 × 0,75 m, 14,0 mil triângulos, 3 conjuntos de textura (chapas onduladas e fundo 2048; armação e tampa 2048;
ferragens 1024). Armação de cantoneira rebitada, pintada de amarelo de obra e lascada, fechada com chapa ondulada
galvanizada (classe `zinco`: ferrugem escorrida e pé comido), dois patins de tubo, tampa de chapa com aba e nervuras,
três dobradiças, alças de vergalhão e porta-cadeado com o cadeado de latão pendurado. Oco por dentro.
Nós: `corpo`, `armacao`, `ferragens`, `tampa` (origem no eixo das dobradiças, abre −100° em x) com `tampa_ferragens`
dentro. No jogo é o maior contêiner: uma grade só de **12 × 8** (96 espaços), construído na forja de tambor com
4 chapas de metal, 2 canos, 1 par de dobradiças e 1 corrente com cadeado, com martelo (fase 2).
A chapa ondulada sai de `modelo._ondulada` e serve para outras peças.

## Mesa de costura com máquina manual (`bancada_costura`)

1,11 × 1,13 × 0,61 m, 13,0 mil triângulos, 3 conjuntos de textura (mesa e quadro 2048; máquina 2048; panos, carretéis e
miudezas 1024). Mesa de pés torneados com gavetinha fixa, máquina de costura de ferro esmaltado com volante e manivela
(sem marca), quadro de linhas atrás com os carretéis, panos dobrados, tesoura, alfineteiro, fita métrica, lata de
botões e um cesto de vime com rolos de pano embaixo. Nós: `mesa`, `tampo`, `maquina`, `linhas`, `miudezas`, `cesto`.
Classes novas: `esmalte_preto`, `dourado`, `pano_*` (trama por textura) e `vime`.

## Mesa de enfermaria improvisada (`mesa_enfermaria`)

2,44 × 1,82 × 0,72 m, 8,6 mil triângulos, 3 conjuntos de textura (cavaletes, tábuas e caixote 2048; colchão e roupa de
cama 1024; soro e miudezas 1024). Tábuas sobre dois cavaletes, colchão de listras, lençol, cobertor de lã e travesseiro,
um frasco de soro pendurado num pau amarrado à cabeceira e um caixote-criado com cruz vermelha: bacia de ágata, frascos,
ataduras e bandeja de instrumentos. Nós: `estrado`, `caixote`, `cama`, `soro`, `miudezas`.
Atenção: `lib.lathe` fecha as pontas do perfil no eixo; um anel solto vira tampa (foi o que escondeu a bacia).

## Fogão a lenha de tambor (`fogao_tambor`)

1,52 × 2,40 × 0,60 m, 6,5 mil triângulos, 3 conjuntos de textura (tambor e chaminé 2048; chapa, porta e panelas 1024;
lenha e brasa 1024). Tambor de 200 litros deitado em berços de aço sobre pés de tijolo, chapa de cozinhar com duas
bocas de tampa, porta da fornalha com frestas que brilham, chaminé de tubo emendado até 2,4 m com chapéu, panela de
alumínio, chaleira de ágata azul, atiçador e lenha empilhada ao lado. Nós: `tambor`, `chamine`, `chapa`,
`porta_fornalha` (origem na dobradiça, abre −100° em y), `panelas`, `lenha` e `brasa` (emissiva, some com o fogo
apagado). `ponto_fogo` no catálogo. Classes novas: `chamine`, `aluminio`, `chapa_fogao`.

## Defumador de tábuas (`defumador`)

0,95 × 1,85 × 0,92 m, 11,9 mil triângulos, 3 conjuntos de textura (base e caixa 2048; telhado e porta 2048; carne,
cinza e brasa 1024). Base de tijolo com a boca do fogo na frente e verga de aço, caixa de tábuas com frestas
enegrecida de baixo para cima, telhado de duas águas de zinco ondulado, porta de tábuas com travessa em Z, dobradiças
de cinta e ferrolho, varas por dentro com mantas de carne penduradas, cinza, tocos queimados e brasa.
Nós: `base`, `caixa`, `telhado`, `porta` (origem na dobradiça, abre −110° em y), `dentro`, `fogo`, `brasa` (emissiva).
Classes novas: `fumo_x/_y/_z` (tábua com fuligem que sobe com a altura), `zinco` ondulado por textura, `carne_seca`,
`cinza_fogo`.
## Filtro de água em barril (`filtro_barril`)

0,66 × 1,11 × 0,81 m, 6,4 mil triângulos, 2 conjuntos de textura (blocos, tábuas, tambor e letreiro 2048; pano, corda,
torneira, mangueira e galão 1024). Tambor de 200 L em pé sobre dois blocos de concreto e três tábuas, a boca coberta por
um pano amarrado com duas voltas de corda de sisal (encardido no meio, por onde entra a água suja), ÁGUA FILTRADA pintado
a pincel, torneira de latão num cano de PVC marrom, mangueira de nível presa com abraçadeiras e um galão de 5 L aparando
a água. Nós: `estrado`, `tambor`, `letreiro`, `pano`, `torneira`, `galao`. Classes novas: `tambor_agua` (envelhecimento em
`materiais.tambor_velho(pé)`: ferrugem, pé comido e calcário escorrendo da boca), `bloco`, `pvc`, `sisal`, `pano_filtro`.
`modelo._sem_tampas` tira as tampas que o `lib.lathe` põe nas pontas (para folhas abertas, como o pano).
No jogo é estação que produz sozinha: 5 garrafas de água da chuva viram 1 galão de água a cada hora.

## Alambique de panela (`alambique`)

1,35 × 1,01 × 0,65 m, 7,4 mil triângulos, 2 conjuntos de textura (fornalha de tijolos e tambor 2048; panela, cano de cobre, garrafas e brasa 1024).
Fornalha de tijolos aberta na frente com lenha, panelão de alumínio tisnado com a tampa vedada de barro e um termômetro,
capacete e cano de cobre com azinhavre que sobe, atravessa e desce em serpentina na água de um tambor de 200 L, ladrão de
PVC, e a saída embaixo pingando num garrafão, com três garrafas arrolhadas ao lado. Nós: `fornalha`, `tambor`, `panela`,
`serpentina`, `garrafas`, `brasa` (brilha sozinha; o jogo só a mostra enquanto há o que destilar). `ponto_fogo` e `ponto_uso`
ficam na boca da fornalha. Classes novas: `panela_alu`, `cobre_velho`, `agua_tambor`, `vidro_verde`, `pinga`, `rolha`.

## Mesa de recarga de munição (`bancada_municao`)

1,21 × 1,35 × 0,65 m, 14,0 mil triângulos, 3 conjuntos de textura (estrutura e tampo 2048; prensa, balança e cápsulas 1024; latas, caixas,
chumbo, luminária, prateleira, caixote e balde 1024). Bancada alta de caibros e pranchas com painel e prateleira atrás,
prensa de recarga de ferro fundido vermelho com alavanca, balança de pólvora de braço, bloco de madeira com as cápsulas em
pé (as três primeiras filas já com projétil), lata de PÓLVORA, caixinhas de espoleta, lingotes de chumbo, concha e molde,
tabela de cargas pregada no painel, luminária de garra; na prateleira latas, caixas de munição, cartuchos de espingarda e
o manual; embaixo um caixote de MUNIÇÃO e um balde de cápsulas vazias. Nós: `estrutura`, `tampo`, `prensa`, `balanca`,
`capsulas`, `miudezas`, `prateleira`, `embaixo`. Classes novas: `papelao`, `caixa_verde`, `caixa_azul`, `papel` (pautado e
escrito por textura), `cartucho`, `latao_fosco`, `letra_preta`. `modelo._letra_curva` pinta um letreiro numa lata redonda.

## Energia da base: gerador, banco de baterias, carregador de pilhas e lâmpada no poste

Quatro peças do degrau 3 do Recomeço (primeira eletricidade). Os números de energia ficam no catálogo
(`energia_w`, `tanque_l`, `litros_h`, `ruido_m`, `bateria_wh`, `consumo_w`, `luz_m`, `ponto_luz`) e o jogo os lê em
`jogo/sistemas/energia.gd`.

| id | medidas | triângulos | texturas | o que é |
|---|---|---|---|---|
| `gerador` | 0,69 × 0,55 × 0,55 m | 6,2 mil | 2 × 1024 | Gerador portátil a gasolina: quadro de tubo com pés de borracha, tanque vermelho com tampa, medidor e letreiro GASOLINA, motor de um cilindro com aletas, partida de corda, alternador, escape e painel com duas tomadas, voltímetro e chave. Substitui o gerador simples do lote 4 (mesmo id e medidas). Nós: `estrutura`, `tanque`, `motor`, `painel`. 2000 W, tanque de 20 L, 2,5 L/h, barulho a 35 m. |
| `banco_baterias` | 0,82 × 0,93 × 0,39 m | 5,5 mil | 2 × 1024 | Estante de tábuas com telhadinho, duas baterias de carro de 12 V ligadas por cabos vermelho e preto, controlador de CARGA com mostrador e três luzes, chave-faca e barra de bornes. Nós: `estrutura`, `baterias`, `quadro`. Guarda 1200 Wh. |
| `carregador_pilhas` | 0,52 × 0,75 × 0,32 m | 3,5 mil | 1 × 1024 | Mesinha de pinho com o carregador de quatro baias (pilhas dentro, luzes de carga), fonte, copo com pilhas, pilhas soltas e um rolo de fio na prateleira de baixo. Nós: `estrutura`, `carregador`. Estação elétrica de 50 W. |
| `lampada_poste` | 0,66 × 1,90 × 0,74 m | 2,8 mil | 1 × 1024 | Caibro em pé numa cruzeta com quatro mãos-francesas, braço com o refletor de lata e a lâmpada pendurada, interruptor e fio grampeado até um rolo no pé. Nós: `poste`, `luminaria`. `ponto_luz` é o centro da lâmpada. 60 W, ilumina 8 m. |

A mesa de costura (`bancada_costura`) ganhou receita de construção (4 tábuas, 1 caixa de pregos, 1 engrenagens, 2 sucatas; martelo).

## Móveis de casa: quarto (`quarto/`: `comoda`, `criado_mudo`, `guarda_roupa`)

Primeiro lote das mobílias das casas no nível realista. As três peças são um conjunto só, de madeira escura
envernizada (classes `nogueira_x/_y/_z`: verniz gasto nas quinas, manchas foscas, poeira nas faces de cima), com
laterais de montantes e almofada, tampo moldurado, puxadores de alça de latão com espelho e fechaduras
(`latao_puxador`). As gavetas são caixas de verdade, de madeira clara por dentro (`forro_*`). Medidas de fora e nós
que abrem são os mesmos dos móveis antigos, então a ambientação dos kits e o jogo continuam valendo.

| id | medidas | triângulos | texturas | nós que abrem |
|---|---|---|---|---|
| `comoda` | 0,93 × 0,85 × 0,47 m | 9,5 mil | corpo 2048, gavetas 1024 | `gaveta_1`, `gaveta_2`, `gaveta_3` (deslizam 0,30 m) |
| `criado_mudo` | 0,47 × 0,56 × 0,42 m | 4,0 mil | 1 × 1024 | `gaveta` (desliza 0,26 m); nicho aberto embaixo, pés torneados |
| `guarda_roupa` | 1,05 × 2,00 × 0,61 m | 9,9 mil | corpo 2048, dentro 1024, portas e gaveta 2048 | `porta_esq`, `porta_dir` (origem na quina de fora, ±105° em y), `gaveta` (0,40 m) |
| `cama_casal` | 1,49 × 1,05 × 1,99 m | 12,0 mil | madeira 2048, roupa de cama 2048 | nenhum (nós `estrutura` e `roupa_de_cama`) |
| `cama_solteiro` | 0,99 × 1,05 × 1,99 m | 9,4 mil | madeira 2048, roupa de cama 2048 | nenhum |

O guarda-roupa tem cornija em degraus, portas de duas almofadas com dobradiças e botões de latão, e dentro (nó
`dentro`) o maleiro, o varão e quatro cabides vazios. Refazer: `python3 moveis_realistas/quarto/gerar.py todas 2048 /tmp/saida`
(cerca de 16 min; `gerar.py comoda` faz uma só; apague `<saída>/<forma>` depois de mudar o modelo). Fotos:
`python3 quarto/ver.py x.png comoda [aberto]` (formas) e `python3 quarto/foto.py x.png comoda [aberto]` (GLB pronto).
As camas têm cabeceira de almofadas com chapéu em arco, pés com pináculo torneado, longarinas com rosetas de latão,
estrado, colchão de listras, lençol dobrado sobre a colcha de matelassê (`colcha_vinho` na de casal, `colcha_azul` na de
solteiro) e travesseiros. O pano sai de `_coberta` (folha amarrotada que cai pelas bordas) e `_travesseiro`.
Os próximos móveis de madeira de casa devem usar as mesmas classes e os ajudantes de `quarto/modelo.py`
(`_gaveta`, `_puxador`, `_fechadura`, `_almofada_lado`, `_tampo`, `_saia`).

## Móveis de casa: sala (`sala/`: `cadeira`, `mesa_jantar`, `estante_livros`, `poltrona`, `sofa`)

O mesmo conjunto de nogueira dos móveis de quarto (`sala/modelo.py` carrega `quarto/modelo.py` e usa os ajudantes dele;
`sala/materiais.py` encadeia `quarto/materiais.py`).

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `cadeira` | 0,42 × 0,93 × 0,45 m | 3,4 mil | 1 × 1024 | Pés da frente torneados, pés de trás e montantes numa peça só deitada para trás, chapéu curvo, tábua central recortada, travessas e assento estofado verde com tachas. Nós: `armacao`, `assento`. |
| `mesa_jantar` | 1,40 × 0,76 × 0,80 m | 4,3 mil | 1 × 2048 | Tampo de quatro tábuas de quina boleada, saias com cordão e quatro pés torneados em balaústre. |
| `estante_livros` | 0,93 × 1,83 × 0,35 m | 12,5 mil | estante 2048, livros 1024 | Laterais de almofada, cornija, rodapé de mísula e cinco níveis de livros (nó `livros`, separado do nó `estante` para o jogo poder esconder): lombadas arredondadas com filetes dourados e etiquetas, vãos, livros tombados e pilhas deitadas. |
| `poltrona` | 0,87 × 0,98 × 0,85 m | 6,4 mil | 1 × 1024 | Braços de rolo com tachas na frente, encosto deitado, almofadas soltas estufadas e pés de madeira (torneados na frente). Nós: `estofado`, `pes`. |
| `sofa` | 1,93 × 0,88 × 0,86 m | 9,7 mil | 1 × 1024 | O mesmo conjunto da poltrona com três lugares e um par de pés no meio. |

Poltrona e sofá saem de `_estofado(W, H, D, lugares)`, com `_fofo` (almofadão de quinas redondas, estufado) e `_braco`.

Classes novas: `estofado_verde` (gasto no meio do assento), `estofado_mostarda` (desbotado e encardido), `capa_1..6`, `papel_livro`, `tacha`. Os livros saem de `_livro` e `_por`
com semente fixa. Refazer: `python3 moveis_realistas/sala/gerar.py todas 2048 /tmp/saida`.

## Móveis de casa: cozinha (`cozinha/`: `balcao_pia`, `armario_aereo`, `geladeira`, `fogao`)

Armários de madeira pintada de creme (`cozinha/materiais.py` encadeia `quarto/materiais.py`), com as mesmas dobradiças
e os mesmos nós `porta_esq` e `porta_dir` dos antigos.

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `balcao_pia` | 1,22 × 1,19 × 0,63 m | 3,9 mil | corpo 2048, portas 1024 | Carcaça com prateleira e rodapé recuado, tampo de granito escuro com frontão, cuba de inox encaixada com ralo, torneira de bica alta e dois registros. Nós: `corpo`, `tampo`, `torneira`, `porta_esq`, `porta_dir`. |
| `armario_aereo` | 0,82 × 0,64 × 0,38 m | 2,1 mil | 2 × 1024 | Carcaça com prateleira, cimalha e duas portas de moldura com puxador de alça. |
| `geladeira` | 0,70 × 1,76 × 0,71 m | 4,2 mil | corpo 2048, portas 1024 | Duplex de chapa esmaltada de quina redonda: vãos forrados de plástico, prateleiras de arame, gaveta de legumes, termostato; portas `porta_geladeira` e `porta_freezer` com forro, prateleiras, borracha e puxador em pé. |
| `fogao` | 0,56 × 0,98 × 0,65 m | 8,1 mil | corpo 2048, porta e gaveta 1024 | Mesa de inox com quatro bocas e grades de ferro, espelho atrás, cinco botões, forno com grade; `porta_forno` com visor de vidro escuro abre para baixo e `gaveta` de panelas desliza. |

Classes novas: `tinta_creme` (amarelada de gordura, escorridos, lascada nas quinas), `pedra_pia` (granito de pintas), `ralo`,
`esmalte_cozinha` (chapa branca encardida, ferrugem nas quinas), `liner`, `esmalte_forno`, `ferro_grade`, `baquelite`, `vidro_forno`.
As portas saem de `_porta` e a caixa de `_carcaca`. Refazer: `python3 moveis_realistas/cozinha/gerar.py todas 2048 /tmp/saida`.

## Móveis de casa: banheiro (`banheiro/`: `pia_banheiro`, `vaso_sanitario`, `armario_banheiro`)

Louça branca torneada (`banheiro/materiais.py` encadeia `cozinha/materiais.py`); as bacias saem de `_oval`, um perfil
girado e esticado em z. Mesmos nós que abrem dos antigos.

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `pia_banheiro` | 0,54 × 0,99 × 0,45 m | 2,1 mil | 1 × 1024 | Pia de coluna: bacia oval com mesa dos metais, coluna torneada, bica curva, dois registros de cruzeta e ralo. |
| `vaso_sanitario` | 0,40 × 0,80 × 0,79 m | 2,3 mil | 2 × 1024 | Bacia oval com pé, água, caixa acoplada oca com alavanca; `assento` (assento e tampa) levanta e `tampa_caixa` desliza (esconderijo). |
| `armario_banheiro` | 0,52 × 0,70 × 0,18 m | 1,4 mil | 2 × 1024 | Armário de parede de madeira pintada com duas prateleiras de vidro fosco, luminária em cima e `porta_espelho` com espelho manchado. |

Classes novas: `louca` (encardida, escorridos), `agua_vaso`, `espelho` (prata descascada e véu de poeira), `vidro_fosco`.
Refazer: `python3 moveis_realistas/banheiro/gerar.py todas 2048 /tmp/saida`.

## Depósito e loja (`deposito/`: `estante_metal`, `caixa_madeira`, `caixa_papelao`, `arquivo_aco`)

Aço pintado gasto, tábua crua e papelão (`deposito/materiais.py` encadeia `quarto/materiais.py`). Mesmos nós que abrem
dos antigos.

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `estante_metal` | 1,03 × 1,90 × 0,43 m | 2,2 mil | 2 × 1024 | Estante de cantoneira furada com 5 prateleiras de chapa dobrada, travessas e sapatas; nó `carga` com caixas guardadas. |
| `caixa_madeira` | 0,85 × 0,56 × 0,65 m | 4,0 mil | 2 × 1024 | Caixote de tábuas com frestas, sarrafos de reforço e pregos; `tampa` de tábuas levanta pela dobra de trás. |
| `caixa_papelao` | 0,50 × 0,37 × 0,40 m | 0,7 mil | 1 × 1024 | Caixa de mudança com fita parda e cantos amassados; as quatro abas (`aba_esq`, `aba_dir`, `aba_frente`, `aba_tras`) abrem uma a uma. |
| `arquivo_aco` | 0,47 × 1,33 × 0,65 m | 2,4 mil | 2 × 1024 | Arquivo de chapa com 4 gavetas ocas (`gaveta_1` embaixo, como no antigo), puxador embutido, porta-etiqueta e fechadura. |

Classes novas: `aco_arquivo`, `aco_estante`, `fita_parda`. Refazer: `python3 moveis_realistas/deposito/gerar.py todas 2048 /tmp/saida`.

## Decoração (`decoracao/`: `quadro_familia`, `relogio_parede`, `vaso_planta_morta`, `abajur`)

Peças de ambiente sem partes que abrem (`decoracao/materiais.py` encadeia `banheiro/materiais.py`). Os de parede têm
a parede em z = 0 e a base em y = 0, como os antigos.

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `quadro_familia` | 0,60 × 0,45 × 0,03 m | 0,8 mil | 1 × 1024 | Moldura de nogueira com filete dourado, passe-partout e foto desbotada de uma família de cinco em silhueta, com manchas de umidade. |
| `relogio_parede` | 0,32 × 0,32 × 0,045 m | 1,8 mil | 1 × 1024 | Caixa redonda preta, mostrador com os 12 números e as marcas dos minutos, ponteiros parados às 3:17 e o de segundos vermelho. |
| `vaso_planta_morta` | 0,37 × 0,80 × 0,52 m | 3,0 mil | 2 × 1024 | Vaso de barro com pratinho e salitre, terra seca com torrões, quatro caules secos com folhas enroladas e folhas caídas em volta. |
| `abajur` | 0,35 × 0,60 × 0,62 m | 2,5 mil | 1 × 1024 | Base de cerâmica azul torneada, haste e soquete de latão, lâmpada, cúpula de linho com aranha de arame, fio e tomada. |

Classes novas: `foto_papel`, `foto_sombra`, `foto_meio`, `foto_pele`, `passepartout`, `terracota`, `terra_seca`, `galho_seco`,
`folha_seca`, `ceramica_azul`, `cupula`, `vidro_lampada`. Sem vidro na frente do quadro e do relógio (os antigos tinham uma
placa transparente). Refazer: `python3 moveis_realistas/decoracao/gerar.py todas 2048 /tmp/saida`.

## Escritório e TV (`escritorio/`: `mesa_escritorio`, `rack_tv`, `tv_tubo`, `calendario_parede`)

`escritorio/materiais.py` encadeia `decoracao/materiais.py`. Mesmos nós que abrem dos antigos (`gaveta`; `porta_esq`).

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `mesa_escritorio` | 1,40 × 1,14 × 0,72 m | 9,0 mil | 2 × 1024 | Tampo de fórmica, pés de painel de aço, monitor de tubo bege, teclado com as teclas uma a uma, mouse, papéis e porta-lápis; `gaveta` de aço com resma, grampeador e pilhas. |
| `rack_tv` | 1,40 × 1,18 × 0,46 m | 2,9 mil | 2 × 1024 | Rack de nogueira com pés palito, videocassete, fitas e caixa no lado aberto, TV de tela plana em cima; `porta_esq` almofadada com puxador de botão. |
| `tv_tubo` | 0,66 × 0,85 × 0,64 m | 1,9 mil | 1 × 1024 | Gabinete de madeira com pés, tela com trincas saindo da pancada, botões giratórios, grade do alto-falante, costas do tubo e antena de dois braços. |
| `calendario_parede` | 0,30 × 0,45 × 0,02 m | 1,6 mil | 1 × 1024 | Folha de outubro com paisagem, dias 1 a 16 riscados e o 17 circulado (o dia do surto), pendurada num prego. |

Classes novas: `aco_mesa`, `formica`, `tecla`, `vidro_caco`, `cal_*`. Refazer: `python3 moveis_realistas/escritorio/gerar.py todas 2048 /tmp/saida`.

## Diversos (`diversos/`: `lixeira`, `mala_viagem`, `aquecedor`, `desenho_crianca`)

`diversos/materiais.py` encadeia `escritorio/materiais.py`. Mesmos nós que abrem dos antigos (`tampa`).

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `lixeira` | 0,62 × 1,04 × 0,88 m | 2,8 mil | 2 × 1024 | Lixeira de rua de plástico verde desbotado com nervuras, rodas e alça atrás, saco de lixo dentro; `tampa` levanta pela dobradiça de trás. |
| `mala_viagem` | 0,76 × 0,29 × 0,47 m | 2,3 mil | 2 × 1024 | Mala de náilon azul com forro, alças, fechos de latão e roupas dobradas dentro; `tampa` abre pela costura de trás. |
| `aquecedor` | 0,62 × 0,60 × 0,35 m | 3,7 mil | 1 × 1024 | Aquecedor a óleo de 9 elementos esmaltados, caixa de comando com dois botões e luz piloto, fio e pés com rodinhas. |
| `desenho_crianca` | 0,30 × 0,23 m | 1,2 mil | 1 × 1024 | Folha presa com fita crepe: casa, sol, passarinhos e a família de palitos em giz de cera. |

Classes novas: `plastico_verde`, `saco_lixo`, `mala_azul`, `forro_mala`, `roupa_*`, `jeans`, `giz_*`, `folha_sulfite`, `fita_crepe`.
Refazer: `python3 moveis_realistas/diversos/gerar.py todas 2048 /tmp/saida`.


## Loja, vestiário e lanchonete (`loja/`: `gondola`, `balcao_caixa`, `armario_vestiario`, `banqueta_giratoria`)

`loja/materiais.py` encadeia `diversos/materiais.py`. Mesmos nós que abrem dos antigos (`gaveta_dinheiro`, `porta_1..3`).

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `gondola` | 1,00 × 1,65 × 0,89 m | 14 mil | 2 × 1024 | Módulo dupla face de chapa pintada: montantes com cremalheira nas pontas (dois módulos lado a lado fecham um montante), painéis de fundo com vinco, 3 prateleiras por lado em mãos-francesas, canaletas amarelas de preço com etiquetas, rodapé e pés niveladores; sobras de latas, caixas e garrafas espalhadas. |
| `balcao_caixa` | 1,84 × 1,15 × 0,64 m | 9 mil | 2 × 1024 | Balcão de fórmica branca com cantoneiras, tampo de granito, esteira com roletes e bastão divisor, balança e leitor de código, registradora bege com teclado e visor, visor do cliente no poste, impressora de cupom; nicho com maços de sacolas; `gaveta_dinheiro` com notas presas e moedas. |
| `armario_vestiario` | 0,90 × 1,85 × 0,54 m | 5,3 mil | 2 × 1024 | Armário de aço cinza-verde de 3 portas com venezianas estampadas, puxador de alavanca, plaquetas numeradas, porta-etiqueta e cadeado na 2; dentro: prateleira, varão com ganchos, toalha, mochila e botas. |
| `banqueta_giratoria` | 0,41 × 0,79 × 0,41 m | 4,6 mil | 1 × 1024 | Banqueta de lanchonete cromada: base de cúpula, coluna, anel de pés com 3 raios, aro frisado com tachas e assento de vinil vermelho com vivo e costuras. |

Classes novas: `gondola_branca`, `etiqueta_amarela`, `laminado_branco`, `granito`, `armario_verde`, `cromo`, `vinil_vermelho`, `sacola`, `cedula_*`, `vidro_visor`.
Refazer: `python3 moveis_realistas/loja/gerar.py todas 2048 /tmp/saida`.

## Depósito, espera, biblioteca e hotel (`servicos/`: `pallet`, `banco_espera`, `estante_biblioteca`, `frigobar`)

`servicos/materiais.py` encadeia `loja/materiais.py`; os livros usam o `_livro` de `sala/modelo.py`. Mesmo nó que abre do antigo (`porta` do frigobar).

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `pallet` | 1,20 × 0,15 × 0,80 m | 3 mil | 1 × 1024 | Pallet de pinho cru: 3 tábuas de baixo, 9 tacos com carimbo HT, 7 tábuas de cima pregadas (uma partida e afundada no meio). |
| `banco_espera` | 1,92 × 0,85 × 0,53 m | 2,8 mil | 1 × 1024 | Longarina de tubo grafite com pés em T e sapatas, 3 conchas de polipropileno azul aparafusadas, braços entre os lugares, senha e copo esquecidos. |
| `estante_biblioteca` | 1,04 × 2,25 × 0,64 m | 10,6 mil | 2 × 1024 | Estante dupla face de nogueira com laterais almofadadas, cornija e placas de latão (HISTÓRIA / LITERATURA); livros dos dois lados com vãos de saque e pilhas deitadas. |
| `frigobar` | 0,48 × 0,55 × 0,55 m | 3,9 mil | 2 × 1024 | Minibar de hotel folheado de nogueira com puxador e plaqueta de latão, caixa interna branca, prateleira de arame, latas, garrafas e chocolate; porta com gaxeta e garrafinhas; grade e compressor atrás. |

Classes novas: `assento_azul`, `aco_banco`, `liner_branco`, `chocolate` (e `capa_*`, `papel_livro` repetidas da sala). Refazer: `python3 moveis_realistas/servicos/gerar.py todas 2048 /tmp/saida`.

## Sinais de saque, pilha de livros e tambor (`sinais/`: `cacos_vidro`, `louca_quebrada`, `papeis_espalhados`, `cadeira_quebrada`, `pilha_livros`, `tambor_200l`)

`sinais/materiais.py` encadeia `servicos/materiais.py`. A cadeira quebrada é a `cadeira` realista de `sala/modelo.py` caída de lado, sem o pé da frente da direita (que fica solto no chão).

| id | medidas | triângulos | texturas | o que tem |
|---|---|---|---|---|
| `tambor_200l` | 0,59 × 0,89 × 0,59 m | 2,5 mil | 1 × 1024 | Tambor de aço azul com aros de rolagem, frisos, bujões na tampa, ferrugem subindo da base e escorrido. |
| `cacos_vidro` | 0,98 × 0,03 × 0,81 m | 0,9 mil | 1 × 512 | 55 cacos espalhados e o canto do caixilho branco com um pedaço de vidro preso. |
| `louca_quebrada` | 0,78 × 0,07 × 0,60 m | 1,1 mil | 1 × 512 | Pedaços de prato com friso azul, lascas e a xícara deitada com a asa solta ao lado. |
| `papeis_espalhados` | 0,98 × 0,02 × 0,95 m | 1,3 mil | 1 × 1024 | 14 folhas A4 com a ponta levantada, linhas de texto e carimbo azul, e uma pasta parda. |
| `cadeira_quebrada` | 1,43 × 0,42 × 0,48 m | 3,6 mil | 1 × 1024 | A cadeira de nogueira com assento verde, caída de lado, com o toco lascado e o pé solto no chão. |
| `pilha_livros` | 0,50 × 0,25 × 0,34 m | 0,7 mil | 1 × 512 | Sete livros deitados empilhados meio tortos e um caído ao lado. |

Classes novas: `lasca`, `pasta_parda`, `carimbo_azul` (e `estofado_verde`, `tacha` repetidas da sala). Refazer: `python3 moveis_realistas/sinais/gerar.py todas 2048 /tmp/saida`.

## casa/ (lote 15)

Mesa de lanchonete com dois sofás (`mesa_booth`), vitrola de móvel (`vitrola`, tampa abre), máquina de lavar de frente
(`maquina_lavar`, porta e gaveta de sabão) e banheira de pé (`banheira`). Materiais encadeados de `sinais/`.
A casca da banheira é um torneado só esticado em estádio (`_estadio`), com a louça de dentro como segundo material:
dois torneados abertos levam tampa nas pontas e cobrem o vão. Aros abertos (sanfona e aro da porta) usam `_anel`.
`python3 gerar.py todas`.
