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
