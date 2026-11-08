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
  - `tipo: porta` ou `tampa`: girar `abre_graus` em torno do `eixo` (`x`, `y` ou `z`) do próprio nó.
  - `tipo: gaveta`: deslizar o vetor `desliza` (m).
  - `tipo: tabua` (barricadas): tábua pregada que o jogo derruba quando a barricada perde vida; `ordem` diz qual cai primeiro (1) e `vida` quanto cada uma aguenta.
  - No Godot: `var n = cena.get_node("porta_geladeira"); n.rotation.y = deg_to_rad(110)` (animar com um Tween).
- Materiais com nome (`madeira`, `esmalte`, `inox`, `tecido_sofa`, ...) para trocar cor na engine. Madeira, tecidos, papelão, ferrugem e granito têm textura PBR (cor + normal + ORM). Rótulos de latas e caixas são artes próprias com marcas inventadas (Vale Verde, Bom Prato, Mar Azul, Fonte Clara...).
- Campos de jogo no catálogo:
  - mobílias: `conteiner` (pode ser revistado), `slots`, `saque` (grupos da tabela de saque), `barricada` (dá para empurrar contra uma porta), `deitar`, `sentar`, `estacao`, `comodos`; barricadas têm `vao`/`vao_m` (largura, altura e altura de início do vão que cobrem), `constroi` e `ferramenta`; pontos de recurso têm `coleta` (recurso, total, ferramenta, segundos por unidade).
  - loot: `recurso` (os 6 do MVP: comida, agua, madeira, sucata, remedios, combustivel; ou ferramenta/arma/energia), `valor` (quanto rende), `peso_kg`, `empilha`, `efeito`, `onde` (prédios), `arma` e `dano`.

## Lotes

109 itens no total (51 mobílias e 58 itens de loot). O campo `lote` do catálogo diz de qual lote é cada um.

| Lote | Mobílias | Loot |
|---|---|---|
| 1. Básico | geladeira duplex, fogão 4 bocas, balcão com pia, estante de aço (5 prateleiras), guarda-roupa 2 portas, cômoda 3 gavetas, criado-mudo, cama de casal, cama de solteiro, mesa de jantar, cadeira de madeira, sofá 3 lugares, armário de banheiro com espelho, caixote de madeira | lata de feijão, lata de sardinha, pacote de arroz 1 kg, caixa de flocos de milho, garrafa de água 1,5 L, galão de água 5 L, kit de primeiros socorros, frasco de comprimidos, rolo de atadura, martelo de unha, pé de cabra, machado, chave inglesa, lanterna, taco de madeira, tábua de madeira, caixa de pregos, fita adesiva prata, chapa de metal ondulada, cano de ferro, galão de gasolina 20 L, cartela de pilhas AA |
| 2. Casa completa | armário aéreo de cozinha, pia de coluna, vaso sanitário com caixa, banheira, estante de livros, rack com TV, poltrona, escrivaninha com luminária, berço, máquina de lavar, aquecedor a óleo | mochila, pilha de roupas dobradas, sabonete embrulhado, livro técnico, rádio portátil, vela e caixa de fósforos, isqueiro, garrafa de vidro vazia, panela com tampa, faca de cozinha |
| 3. Comércio e serviços | gôndola de supermercado, balcão de caixa com registradora, freezer horizontal, prateleira de pães, mesa de escritório, arquivo de aço 4 gavetas, armário de vestiário (3 portas), maca hospitalar, carrinho de compras | caixa de leite longa vida, saco de farinha 5 kg, saco de sementes, lata de milho, seringa com antibiótico, máscara de proteção, lata de costura, bateria de carro |
| 4. Sobrevivência e oficina | bancada de trabalho com morsa, fogareiro a gás de camping, beliche de abrigo, mesa de rádio amador, gerador portátil a gasolina, tambor de 200 L, pallet de madeira | arco e flechas, lança improvisada, facão, serrote, pá, enxada, rolo de corda, rolo de arame farpado, saco de areia, caixa de peças de motor |
| 5. Fase 1 (Sozinho) | barricada de tábuas para porta, barricada de tábuas para janela, alarme de latas, fogueira de pedras, colchão no chão, caixa de papelão de mudança, lixeira de rua com rodas, mala de viagem, pilha de sucata, toco de rachar lenha | feixe de lenha, pacote de salgadinho, barra de chocolate, cantil de alumínio, saco de dormir enrolado, molho de chaves com etiqueta, mapa da cidade dobrado, bilhete de sobrevivente |

As versões completas das armas (fogo, arcos, facas, facão, lança), com partes, acessórios e animações, ficam em `props/armas/`; o arco, a lança e o facão daqui são o loot simples.

O lote 1 fica em `gerar_props.py`; os outros em `lote2.py` a `lote5.py`, que o gerador carrega com as mesmas funções e materiais. Para um lote novo, crie `lote6.py` e acrescente o número no laço do gerador.

Algumas mobílias trazem campos a mais para o jogo: `esconderijo` (vaso sanitário), `modulo_m` (gôndola, encaixa lado a lado), `empurrar` (carrinho), `vagas` (beliche), `desmontavel` (pallet), `usa` (rádio, gerador), `portatil` e `peso_kg` (fogareiro, gerador).
