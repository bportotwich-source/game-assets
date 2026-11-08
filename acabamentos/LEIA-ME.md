# Acabamentos internos

Papel de parede, azulejo, lambri e piso por cômodo, sem mexer nas peças dos kits.

- `*_albedo.png`, `*_normal.png`, `*_orm.png`: texturas de 1 × 1 m feitas por `scripts/acabamento/texturas.py`. Uma camada por acabamento, na ordem de `camadas.json`.
- `estilos.json`: os estilos de parede (camada de cima, camada de baixo, altura da troca, cores, rodapé, sanca) e de piso. Saem de `scripts/acabamento/mapa.py`.
- `acabamento.gdshader` + `acabamento.gd`: no Godot, `preload("res://acabamentos/acabamento.gd").aplicar(predio, kit)` troca os materiais de parede lisa (`plaster`) e de piso genérico (`floor`) pelo shader. O shader lê `kits/<kit>/acabamento.json` para saber o estilo de cada cômodo.

Cada kit precisa de `kits/<kit>/acabamento.json`: `python3 scripts/acabamento/mapa.py <kit>` (usa os cômodos e tipos da ambientação). No visitar, a tecla K liga e desliga o acabamento.
