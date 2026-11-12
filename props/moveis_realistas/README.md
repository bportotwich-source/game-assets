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

