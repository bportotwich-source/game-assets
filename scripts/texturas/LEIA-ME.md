# Texturas novas (proposta)

Gerador de texturas PBR mais ricas para os kits. Ainda **não** foi aplicado em nenhum kit: primeiro escolhemos o estilo.

Prévia antes/depois: https://claude.ai/artifact/Hr2UcmUupLR537kYd2Kjre

## Estilos
- **detalhado**: realista e limpo. Cada peça com seu tom, juntas fundas, bordas chanfradas, granulado.
- **pintado**: pintado à mão, tons em faixas e luz pintada no topo. Combina com o toon + contorno.
- **envelhecido**: detalhado + lascas, rachaduras, musgo, manchas e escorridos.

## Saída
`python3 gerar_texturas.py --px-por-m 256 --saida out` gera, por estilo e material:
`<material>_albedo.png`, `<material>_normal.png` (OpenGL, verde para cima, igual Godot) e
`<material>_orm.png` (R oclusão, G rugosidade, B metálico).

Materiais: brick, stone, stone2, plaster, render, roof_tiles, shingles, siding.
O ladrilho novo tem 2 m (o dobro do original), então no Godot use `uv1_scale = 0.5`
(ver `out/texturas.json`). Cores base em `CORES`, sobrescrevíveis com `--cores cores.json`.

Na prévia há ainda um detalhe no shader, em coordenadas do mundo: variação de tom em grande escala
(esconde a repetição) e, no estilo envelhecido, sujeira subindo do chão. Isso vira um shader Godot
quando o estilo for escolhido.

## demo/
Fontes da prévia (three.js + esbuild, GLBs comprimidos com meshopt, tudo embutido num HTML).
