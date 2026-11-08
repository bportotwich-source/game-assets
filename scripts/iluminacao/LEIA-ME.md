# Iluminação dos interiores

`luzes.py` grava `kits/<kit>/luzes.json` com as luzes de dentro de cada prédio. O modo visitar (`visitar/main.gd`) cria uma `OmniLight3D` para cada uma.

```
python3 scripts/iluminacao/luzes.py            # todos os kits
python3 scripts/iluminacao/luzes.py padaria    # só um
```
Precisa de `trimesh`, `numpy`, `shapely`, `scipy` e `networkx` (os mesmos da ambientação). Rode de novo sempre que um kit mudar.

## De onde vem cada luz
- **luminaria**: as partes de vidro ou lâmpada das peças do kit (materiais `lamp_*`, `light`, `bulb`, `tube_*`). Cada pedaço solto vira uma luz, e pedaços a menos de 0,4 m um do outro contam como a mesma luminária. Faróis de veículos e luzes perto do chão ficam de fora.
- **gerada**: cômodo sem nenhuma luminária ganha luz de teto, uma a cada 25 m² mais ou menos. O campo `teto` diz a altura do teto ali, e o Godot põe um plafon simples nesse ponto. Os cômodos vêm de `scripts/ambientacao/comodos.py`, e os de fora (pátio, rua, telhado) não ganham luz.
- **externa**: luminária fora dos cômodos (varanda, poste, fachada).

A cor sai do perfil do kit em `scripts/ambientacao/kits.json`: casa tem lâmpada quente, o resto tem luz mais neutra. O campo `materiais` lista os materiais de lâmpada do kit, que o Godot faz brilhar quando a luz está acesa.

## No Godot
- Só as 4 luzes internas mais perto do jogador fazem sombra, revistas 4 vezes por segundo, porque sombra de luz pontual é cara. As outras apagam sozinhas a mais de 28 m.
- A luz ambiente cai de 0,55 para 0,22. Ficam ligados a sombra de canto (SSAO), a luz rebatida (SSIL) e o brilho das lâmpadas (glow).
- `visitar/variacao_tom.gdshader` passa por cima das paredes, pisos e tetos e escurece até 14% em manchas grandes, em coordenadas do mundo. Isso tira a cara de "uma cor só" e esconde a repetição das texturas.
- Teclas: **L** acende e apaga as luzes, e **I** troca entre a iluminação nova e a antiga, para comparar.
