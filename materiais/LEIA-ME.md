# Materiais realistas compartilhados

Catorze materiais de casa feitos no mesmo método da M4A1 (material procedural no Blender, assado em cor, relevo e ORM) e preparados para emendar sozinhos a cada 2 m. Ficam aqui, uma vez só, e qualquer kit pode usar. As peças dos kits não mudam: a troca é feita no Godot, pelo nome do material.

| Material | Lado | O que é |
|---|---|---|
| `tabua_verde` | 2048 px | Tábua de fachada pintada de verde, fiadas de 20 cm, tinta descascando no veio |
| `tijolo_vermelho` | 2048 px | Tijolo aparente, fiada de 6,25 cm |
| `telha_asfaltica` | 2048 px | Telha asfáltica cinza, fiadas de 20 cm |
| `assoalho` | 2048 px | Assoalho de tábua envernizada, gasto |
| `deck` | 2048 px | Tábua de varanda sem verniz |
| `reboco_claro` | 1024 px | Reboco pintado claro, trincas finas |
| `pedra_clara` | 1024 px | Pedra de capa e peitoril |
| `tinta_creme` | 1024 px | Madeira pintada, para molduras, caixilhos e portas |
| `tabua_branca` | 2048 px | Tábua de fachada branca, que recebe a cor de cada casa |
| `reboco_externo` | 2048 px | Reboco de fachada claro, que recebe a cor de cada casa |
| `telha_barro` | 2048 px | Telha plana de barro |
| `cantaria` | 2048 px | Pedra aparelhada clara, blocos de 50 × 25 cm |
| `bloco` | 1024 px | Bloco de concreto aparente |
| `concreto` | 1024 px | Concreto liso de calçada, soleira e base |

Cada material tem `_albedo.webp`, `_normal.webp` (OpenGL, igual ao Godot) e `_orm.webp` (R oclusão, G rugosidade, B metálico). O ladrilho cobre 2 × 2 m, a mesma medida das UVs das peças (metros / 2). Os catorze juntos ocupam cerca de 109 MB de memória de vídeo, valor calculado pelo formato comprimido, e esse custo é o mesmo com uma casa ou com cem.

## Usar num kit

1. Criar `kits/<kit>/materiais.json` com `python3 scripts/materiais/mapear.py <kit>`: ele decide pelo nome do material nas peças e guarda a cor que o kit usa hoje como tom por cima do ladrilho. Dá para ajustar à mão depois (o do bangalô é feito à mão). `sem_uv` projeta o ladrilho pelas três faces, para peças sem UV. `cor` multiplica a cor do ladrilho.
2. No Godot, antes do acabamento por cômodo:

```gdscript
const Realista = preload("res://materiais/realista.gd")
var trocados := Realista.aplicar(predio, "bangalo")
Realista.ligar(trocados, false)   # volta ao original
```

No visitar, a tecla R liga e desliga. Os 13 kits do jogo têm `materiais.json`.

## Refazer ou criar um material

```
python3 amostras/casa_realista/ladrilho.py <saida>     # Blender como módulo (pip install bpy); uns 3 min por material
python3 scripts/materiais/publicar.py <saida>          # grava os .webp, os .import e o materiais.json daqui
```

Os `.import` desta pasta vão para o repositório de propósito: são eles que mandam o Godot guardar as texturas comprimidas na placa de vídeo. Sem eles, cada textura de 2048 px ocuparia 21 MB em vez de 3 a 5.

## O que ainda não está aqui

Quinas arredondadas, portas e janelas em relevo e sujeira própria de cada parede dependem de mexer nas peças e ficam para a etapa seguinte. Metal, vidro, esmalte e pisos frios ainda usam o material simples de cada kit.
