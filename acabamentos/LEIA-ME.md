# Acabamentos internos

Papel de parede, azulejo, lambri e piso por cômodo, sem mexer nas peças dos kits.

- `*_albedo.png`, `*_normal.png`, `*_orm.png`: texturas de 1 × 1 m feitas por `scripts/acabamento/texturas.py`. Uma camada por acabamento, na ordem de `camadas.json`.
- `estilos.json`: os estilos de parede (camada de cima, camada de baixo, altura da troca, cores, rodapé, sanca) e de piso. Saem de `scripts/acabamento/mapa.py`.
- `acabamento.gdshader` + `acabamento.gd`: no Godot, `preload("res://acabamentos/acabamento.gd").aplicar(predio, kit)` troca os materiais de parede lisa (`plaster`) e de piso genérico (`floor`) pelo shader. O shader lê `kits/<kit>/acabamento.json` para saber o estilo de cada cômodo.

Cada kit precisa de `kits/<kit>/acabamento.json`: `python3 scripts/acabamento/mapa.py <kit>` (usa os cômodos e tipos da ambientação). No visitar, a tecla K liga e desliga o acabamento.

Todos os 61 kits já têm `acabamento.json`. Nos kits mais novos, o piso já vem por cômodo (carpete, vinílico, taco), então só as paredes lisas mudam. O pé-direito de cada cômodo é a mediana da altura do teto em até 40 pontos do cômodo; acima de 5 m (galpões, átrios) não há sanca.

## Mapa fino (cantos, portas e escadas)

O mapa de 0,25 m é maior que a parede interna (12 cm) e não fica alinhado com ela. As células que pegavam parede herdavam o cômodo mais perto e erravam o lado: faixa do papel do vizinho nos cantos e ao lado das portas, piso entrando pela soleira, retalhos na caixa de escada.

- `acabamento.json` traz agora o campo `fino`: o mesmo desenho com célula de 0,0625 m, comprimido (gzip + base64). Cada célula livre fica com o cômodo de onde se chega nela sem atravessar parede. No vão de uma porta ou passagem a parede fica como a peça veio (batente) e o piso troca no meio do vão. Caixa de escada e vazios fechados ganham o estilo 19 (pintura lisa, sem rodapé nem sanca).
- O campo `mapa` antigo continua no arquivo, para quem ainda não lê o fino. `ACABAMENTO_MAPA_ANTIGO=1` força o antigo no `acabamento.gd`, para comparar.
- Peças de escada (`stair*`, `escada*`, `step*`) ficam fora do acabamento: espelho, banzo e lateral são faces em pé de `plaster` e pegavam papel, lambri e azulejo.
- Cômodo pequeno com escada dentro que a ambientação chamou de banheiro, lavabo, depósito ou vazio é tratado como corredor (só no acabamento; o `ambientacao.json` não muda).

Ainda aberto: nos kits que já trazem piso próprio em módulos de 2 m (ladrilho `tile`/`slate`, mármore), o piso não acompanha as paredes quando o cômodo não cai na linha do módulo (casas-vitorianas, casa-reboco).

## Molduras modeladas

`python3 scripts/detalhe/molduras.py kits/<kit> --teto <pé-direito>` põe nas peças de parede do kit, em geometria, a guarnição de porta e de janela, o rodapé com perfil e a sanca (um nó `molduras` por peça, com o material `trim` do kit). Depois é preciso gerar o `acabamento.json` de novo: ele passa a trazer `molduras_modeladas: true` e o shader deixa de pintar rodapé e sanca por cima. Feito nos 13 prédios do jogo. O lambri e o friso dele continuam pintados, porque mudam de cômodo para cômodo.
