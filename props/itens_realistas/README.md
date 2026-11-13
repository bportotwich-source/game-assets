# Itens realistas

Itens de saque e de craft refeitos no nível de detalhe das armas e das estações (etapa 3 do plano dos
modelos realistas): formas torneadas em Blender (`bpy`), texturas assadas com a biblioteca da M4A1
(`props/armas/m4a1`) e as classes de material das estações (`props/moveis_realistas`).

## agua/

Vasilhas de água, com um GLB para cada estado, para o jogo mostrar o que a vasilha tem dentro:

| Vasilha | Vazia | Com água suja | Com água limpa |
|---|---|---|---|
| Garrafa PET de 2 L (deitada) | `garrafa_pet` | `garrafa_pet_agua_suja` | `garrafa_pet_agua_limpa` |
| Garrafa de água de 1,5 L (lacrada) | | | `garrafa_agua` |
| Galão de 5 L | `galao_vazio` | `galao_agua_suja` | `galao_agua` |
| Garrafa de vidro | `garrafa_vidro` | `garrafa_vidro_agua_suja` | `garrafa_vidro_agua_limpa` |
| Cantil de alumínio (não se vê dentro) | `cantil` | `cantil` | `cantil` |
| Caneca de lata | `caneca_lata` | `caneca_lata_agua_suja` | `caneca_lata_agua_limpa` |

De cada forma sai um bake só. Os estados são o mesmo GLB sem a malha `agua` (vazio) ou com ela em outra
cor (marrom turva ou azul clara). Plástico e vidro saem com material liso transparente (`casca`) e a água,
lisa e opaca por dentro, para não brigar com a transparência da casca no jogo. No catálogo, os estados
extras ficam no campo `estados` do item da vasilha (não são itens à parte).

```
pip install bpy pillow numpy
python3 agua/ver.py formas.png                 # confere as formas, sem assar
python3 agua/gerar.py todas 1024 /tmp/agua     # assa e grava os 14 GLBs em props/loot
python3 agua/foto.py foto.png ../loot/galao_vazio.glb ../loot/galao_agua.glb
```

## comida/

Comida embalada, no mesmo tamanho e posição dos antigos (latas e caixas em pé, pacotes deitados). Rótulos de
desenho próprio, sem marcas, com os dizeres em português:

| Item | Arquivo | O que tem |
|---|---|---|
| Lata de feijão | `lata_feijao` | lata com recravação, argola de abrir e rótulo de papel marrom com faixa creme |
| Lata de milho | `lata_milho` | lata baixa, rótulo verde com faixa amarela |
| Lata de sardinha | `lata_sardinha` | lata retangular de cantos redondos, tampa estampada e argola |
| Pacote de arroz | `pacote_arroz` | saco plástico cheio, soldas achatadas nas pontas, faixa azul |
| Caixa de flocos de milho | `caixa_cereal` | caixa de papelão com a tigela na frente e tabela no verso e na lateral |
| Caixa de leite | `caixa_leite` | longa vida de 1 L com as orelhas dobradas, solda em cima e tampa de rosca |
| Pacote de salgadinho | `salgadinho` | saco metalizado estufado com as soldas prateadas |
| Barra de chocolate | `barra_chocolate` | luva de papel, papel alumínio rasgado numa ponta e os tabletes à mostra |
| Tigela de arroz cozido | `arroz_cozido` | tigela esmaltada de friso azul; é o pacote de arroz depois da panela (`estados` do `pacote_arroz`) |
| Saco de farinha 5 kg | `saco_farinha` | saco de papel cheio, faixa azul impressa e as duas bocas costuradas com barbante |
| Saco de pão francês | `pao_velho` | saco de papel pardo de padaria com a boca aberta e cinco pães com o corte em cima |
| Pão caseiro | `pao_caseiro` | filão com quatro talhos abertos e a casca manchada do forno |
| Carne crua embrulhada | `carne_crua` | bife com capa de gordura e marmoreio sobre o papel de açougue aberto |
| Carne defumada | `carne_defumada` | peça escura amarrada com barbante em gomos, ponta cortada e laço de pendurar |
| Cesto de legumes | `cesto_legumes` | cesto de vime com alça trançada e forro de pano, alface, tomates e cenouras com rama |

```
python3 comida/ver.py formas.png lata_feijao             # confere as formas, sem assar
python3 comida/gerar.py todas 2048 /tmp/comida           # assa e grava os 15 GLBs em props/loot (~30 min)
```

O bake fica guardado na pasta de saída: depois de mudar um modelo, apague `<saída>/<forma>` antes de gerar de novo.

## remedios/

Remédios, no mesmo lugar e tamanho próximo dos antigos. Usa as classes e as funções de `comida/`.

| Item | Arquivo | O que tem |
|---|---|---|
| Kit de primeiros socorros | `kit_medico` | maleta de plástico vermelha com cruz, junta da tampa, dois fechos, alça e dobradiças |
| Frasco de comprimidos | `frasco_remedio` | frasco laranja com rótulo e tampa branca estriada |
| Rolo de atadura | `atadura` | rolo de gaze com as voltas à mostra, ponta solta e presilha de metal |
| Seringa com antibiótico | `seringa` | corpo graduado com o remédio dentro, êmbolo, aba de dedo e agulha |
| Lata de costura | `kit_costura` | lata aberta forrada, com carretéis, alfineteiro, tesoura, fita métrica, botões e dedal |
| Garrafa de álcool 70 % | `alcool` | garrafa oval de plástico com rótulo e tampa vermelha de bico |
| Curativo de pano fervido | `curativo_improvisado` | três panos dobrados amarrados com uma tira |
| Tala de tábua e pano | `tala_improvisada` | duas tábuas com três amarras de pano, acolchoado e rolo de tira |
| Maço de ervas | `ervas` | talos amarrados com barbante e folhas em lança (item só do jogo: grava o GLB, sem registro no catálogo) |
| Remédio de ervas | `remedio_ervas` | vidro verde com rolha, cordão e rótulo de papel (`estados` do `frasco_remedio`) |

```
python3 remedios/ver.py formas.png seringa                 # confere as formas, sem assar
python3 remedios/gerar.py todas 1024 /tmp/remedios         # assa e grava os 10 GLBs em props/loot (~10 min)
```

## ferramentas/

Ferramentas e materiais de craft, no mesmo tamanho, posição e ponto de pega dos antigos (o jogo não muda):

| Item | Arquivo | O que tem |
|---|---|---|
| Martelo de unha | `martelo` | cabeça de aço com unha fendida, cabo de madeira torneado |
| Machado | `machado` | lâmina em cunha com fio polido, cabo curvo com pomo |
| Serrote | `serrote` | lâmina com dentes de verdade, punho fechado de madeira com três rebites |
| Tábua | `tabua` | cantos gastos, uma ponta lascada, pregos velhos |
| Caixa de pregos | `caixa_pregos` | caixa de papelão aberta com etiqueta e os pregos dentro |
| Cano de ferro | `cano_metal` | tubo oco com rosca numa ponta e luva na outra |
| Chapa de metal ondulada | `chapa_metal` | zinco com ferrugem ao longo das ondas, canto dobrado, parafusos de telhado |
| Punhado de sucata | `sucata_metal` | cantoneira, chapa recortada, toco de cano, vergalhão, mola, parafuso, porcas e arruelas |
| Pá de bico | `pa` | lâmina abaulada com pisantes e ponta lixada, encaixe que morre na lâmina, punho em D de aço com travessa de madeira |
| Enxada | `enxada` | olho forjado com nervura, lâmina fechada para o lado do cabo, fio amolado; deitada apoia na quina da lâmina |
| Faca de cozinha | `faca_cozinha` | lâmina de chef afinando até o fio, gola forjada, talas pretas com três rebites e a espiga aparecendo |
| Facão | `facao` | lâmina larga na ponta com chanfro amolado, talas de madeira escura, rebites de latão e ilhós do cordão |

```
python3 ferramentas/ver.py formas.png                    # confere as formas, sem assar
python3 ferramentas/gerar.py todas 2048 /tmp/ferr        # assa e grava os 12 GLBs em props/loot (~20 min)
python3 ferramentas/foto.py foto.png ../loot/martelo.glb ../loot/machado.glb
```
