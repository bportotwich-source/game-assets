# Itens de decoração

112 móveis e objetos low poly para mobiliar o interior dos prédios dos kits: camas, sofás, mesas, cozinha, banheiro, eletrônicos, luzes e miudezas. Somam 58,338 triângulos (a maioria tem entre 100 e 1.500).

## Convenções
- **GLB**, 1 unidade = 1 m, Y para cima, frente do móvel virada para **+Z** (como as paredes dos kits).
- **Escala** conferida com o padrão do pacote (`PADRAO_METRICAS.md`): cama de casal 1,63 × 2,11 m, geladeira 1,80 m de altura, balcão de cozinha 0,86 m, porta 0,88 × 1,95 m.
- **Pivô** conforme onde o item fica (campo `montagem` no catálogo):
  - `floor`: centro da base, no chão.
  - `wall`: centro de baixo da face de trás, para encostar na parede (quadros, espelhos, aquecedores, tomadas, prateleiras, cortinas, janelas).
  - `ceiling`: centro do topo, para pendurar no teto (luminária e ventilador de teto).
- **Materiais** de cor sólida com nomes simples (`White`, `Brown`, `Grey 2`, `Blue`...), sem texturas, para trocar a cor fácil no motor.
- Itens com partes móveis vêm em peças separadas dentro do mesmo GLB: portas de geladeira, balcões e armários, gavetas das cômodas, tampa do cofre.
- As portas e janelas daqui são decorativas. As aberturas dos kits já têm portas e janelas próprias no tamanho certo; use estas só onde não houver abertura (por exemplo um armário embutido ou uma janela falsa).

## Arquivos
- `<categoria>/<item>.glb`: os modelos.
- `catalogo.json`: lista com nome em português, categoria, montagem, tamanho em metros (largura × altura × profundidade), triângulos e número de partes. Bom para um editor ou para o jogo montar menus.
- `converter_fbx.py` + `montagem.json`: script do Blender (módulo `bpy`) que gerou os GLB a partir dos FBX originais (escala 0,19, pivô, limpeza de animação e mapas normais vazios).

## Categorias
| Pasta | Categoria | Itens | Conteúdo |
|---|---|---|---|
| `banheiro/` | Banheiro | 7 | Banheira, Box de chuveiro, Pia de banheiro, Porta-papel, Rolos de papel, Vaso sanitário, Porta-toalha |
| `camas/` | Camas | 4 | Cama de casal, Cama de solteiro, Beliche, Treliche |
| `tapetes/` | Tapetes | 3 | Tapete A, Tapete B, Tapete C |
| `cadeiras/` | Cadeiras e poltronas | 5 | Cadeira A, Cadeira B, Banqueta, Banquinho, Poltrona |
| `portas/` | Portas | 3 | Porta A, Porta B, Porta C |
| `comodas/` | Cômodas | 2 | Cômoda, Criado-mudo |
| `eletronicos/` | Eletrônicos | 12 | Console A, Console B, Console C, Console D, Teclado, Notebook, Monitor, Gabinete de PC, Celular, TV antiga, TV de tela plana, Tablet |
| `cozinha/` | Cozinha | 18 | Liquidificador, Balcão A, Balcão B, Balcão C, Balcão D, Balcão E, Balcão F, Balcão com pia, Lava-louças, Geladeira A, Geladeira B, Chaleira, Papel-toalha, Faqueiro, Micro-ondas, Fogão, Torradeira, Máquina de lavar |
| `luzes/` | Luzes | 5 | Luminária de teto, Abajur de pé A, Abajur de pé B, Abajur de mesa, Arandela |
| `diversos/` | Diversos | 31 | Despertador, Lixeira, Livros A, Livros B, Tigela, Vassoura, Ventilador de teto, Relógio de parede, Cortinas, Ventilador, Copo, Globo, Aspirador robô, Escada de mão, Interruptor, Espelho A, Espelho B, Caneca, Frigideira, Planta grande, Planta pequena, Prato, Panela, Aquecedor A, Aquecedor B, Cofre A, Cofre B, Tomada, Caixa de som, Vaso, Grade de ventilação |
| `estantes/` | Estantes | 7 | Armário estreito, Armário de 2 portas, Estante estreita, Estante larga, Estante baixa, Prateleira A, Prateleira B |
| `sofas/` | Sofás | 4 | Sofá de 2 lugares, Namoradeira, Poltrona baixa, Sofá grande |
| `mesas/` | Mesas | 8 | Escrivaninha, Mesa oval, Mesa redonda, Mesa redonda alta, Mesa A, Mesinha, Mesa de centro, Rack baixo |
| `janelas/` | Janelas | 3 | Janela A, Janela B, Janela C |

## Origem
Convertidos do pacote "Low Poly Household Items" (112 FBX), enviado por Bruno em 7/11/2026. O zip não traz arquivo de licença; antes de distribuir um jogo com estes itens, confirme a licença na página de onde o pacote foi baixado.
