# Mobílias e itens de loot

Modelos **originais**, gerados por script (`gerar_props.py`, Python + trimesh, com a biblioteca de alto detalhe `scripts/detalhe`), para mobiliar os kits e servir de saque no jogo **Recomeço** (`docs/plano-jogo-sobrevivencia.md`).
Ficam separados de `props/decoracao/` (pacote de terceiros da PR #48): aqui tudo é feito do zero e pode ser usado sem restrição.

```
props/
  gerar_props.py        gera tudo:  python props/gerar_props.py   (ou só alguns ids: python props/gerar_props.py geladeira sofa)
  CATALOGO.md           tabelas em português (gerado)
  mobilias/<id>.glb     mobilias/catalogo.json
  loot/<id>.glb         loot/catalogo.json
```

## Convenções

- Y para cima, 1 unidade = 1 m, frente para **+Z**, medidas reais (o jogador tem 1,8 m, ver `PADRAO_METRICAS.md`).
- `montagem: floor`: pivô no centro da base. `montagem: wall`: pivô no centro de baixo da face de trás (armário de banheiro; `altura_sugerida_m` diz onde pendurar).
- Loot fica **deitado na pose de repouso**, pivô no centro da base, pronto para pôr numa prateleira ou no chão. Ferramentas e armas têm `pega`: o ponto (m) onde a mão segura.
- **Partes móveis** (portas, gavetas, tampas) são nós separados do GLB, com a origem na dobradiça. O catálogo diz o que fazer com cada uma:
  - `tipo: porta` ou `tampa`: girar `abre_graus` em torno do `eixo` (`y` ou `x`) do próprio nó.
  - `tipo: gaveta`: deslizar o vetor `desliza` (m).
  - No Godot: `var n = cena.get_node("porta_geladeira"); n.rotation.y = deg_to_rad(110)` (animar com um Tween).
- Materiais com nome (`madeira`, `esmalte`, `inox`, `tecido_sofa`, ...) para trocar cor na engine. Madeira, tecidos, papelão, ferrugem e granito têm textura PBR (cor + normal + ORM). Rótulos de latas e caixas são artes próprias com marcas inventadas (Vale Verde, Bom Prato, Mar Azul, Fonte Clara...).
- Campos de jogo no catálogo:
  - mobílias: `conteiner` (pode ser revistado), `slots`, `saque` (grupos da tabela de saque), `barricada` (dá para empurrar contra uma porta), `deitar`, `sentar`, `estacao`, `comodos`.
  - loot: `recurso` (os 6 do MVP: comida, agua, madeira, sucata, remedios, combustivel; ou ferramenta/arma/energia), `valor` (quanto rende), `peso_kg`, `empilha`, `efeito`, `onde` (prédios), `arma` e `dano`.

## Lista completa proposta

O **lote 1** (feito) cobre o que o jogador mais encontra e revista: cozinha, quarto, sala, banheiro e depósito, e o loot dos 6 recursos do MVP.

| Lote | Mobílias | Loot |
|---|---|---|
| **1 (feito)** | geladeira, fogão, balcão com pia, estante de aço, guarda-roupa, cômoda, criado-mudo, cama de casal, cama de solteiro, mesa de jantar, cadeira, sofá, armário de banheiro, caixote | lata de feijão, sardinha, arroz, cereal, garrafa de água, galão de água, kit médico, comprimidos, atadura, martelo, pé de cabra, machado, chave inglesa, lanterna, taco, tábua, pregos, fita adesiva, chapa ondulada, cano, galão de gasolina, pilhas |
| 2. Casa completa | armário aéreo de cozinha, pia e vaso de banheiro, banheira/box, estante de livros, rack com TV, poltrona, escrivaninha, berço, máquina de lavar, aquecedor | mochila, roupas, sabão, livro, rádio portátil, vela e fósforos, isqueiro, garrafa de vidro, panela, faca de cozinha |
| 3. Comércio e serviços | gôndola de supermercado, balcão de caixa, freezer horizontal, prateleira de padaria, mesa de escritório, arquivo de aço, armário de vestiário, maca, carrinho de compras | caixa de cereal grande, saco de farinha, saco de sementes, enlatados variados, seringa, máscara, kit de costura, bateria de carro |
| 4. Sobrevivência e oficina | bancada de trabalho, fogareiro, beliche de abrigo, mesa de rádio, gerador, tambor de 200 L, pallet | serrote, pá, enxada, corda, arame farpado, sacos de areia, peças de motor |

O lote 4 conversa com o kit de construções de sobrevivência (seção 9 do plano). Cada lote entra como uma PR.
Armas de verdade (fogo, arcos, facas, facão, lança), com partes, acessórios e animações, ficam em `props/armas/` (ver o README de lá).
