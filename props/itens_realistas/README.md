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
