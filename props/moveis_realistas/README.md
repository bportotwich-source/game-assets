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
