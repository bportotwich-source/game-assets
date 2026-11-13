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

```
python3 comida/ver.py formas.png lata_feijao             # confere as formas, sem assar
python3 comida/gerar.py todas 2048 /tmp/comida           # assa e grava os 9 GLBs em props/loot (~20 min)
```

O bake fica guardado na pasta de saída: depois de mudar um modelo, apague `<saída>/<forma>` antes de gerar de novo.

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
