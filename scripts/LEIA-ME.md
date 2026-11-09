# Scripts de porta

Os mesmos princípios valem para qualquer engine:
- Cada folha de porta (`door_leaf_interior`, `door_leaf_entrance`, `door_leaf_balcony`, `door_leaf_hut`) é uma peça separada com o pivô na dobradiça. Abrir = girar em Y.
- No `building_layout.json`, cada porta tem `"door": {"closed": graus, "open": graus}`. O ângulo de abertura é `open - closed` (positivo ou negativo, conforme o lado do cômodo).
- A folha precisa de um colisor de caixa próprio, separado da parede, para bloquear o jogador quando fechada.

Atenção ao sentido: o kit usa Y para cima e giro positivo anti-horário visto de cima (padrão glTF/Godot). A Unity gira no sentido contrário, por isso `KitDoor.cs` aplica `-openAngle`.

| Engine | Porta | Jogador |
|---|---|---|
| Godot 4 | `godot/door.gd` (num Node3D pai da folha) | `godot/interactor.gd` (num RayCast3D da câmera, ação "interact") |
| Unity | `unity/KitDoor.cs` (na folha, com BoxCollider) | `unity/DoorInteractor.cs` (na câmera, tecla E) |

## Vidro das janelas (scripts/detalhe/vidro.py)

Todo vidro de janela e porta sai **transparente** e igual em todos os kits: material `glass` (o jogo procura esse
nome para quebrar o vidro), quase incolor, alpha 0.16, `alphaMode BLEND`, liso. Vidros especiais mantêm nome e tom
(`gglass` guarda-corpo, `jal` basculante, `glass_f`/`frost` jateado mais fosco). `detalhe.glb_jpeg()` aplica isso
sozinho em todo gerador; para reaplicar nos GLB prontos: `python3 scripts/detalhe/vidro.py kits/`.
