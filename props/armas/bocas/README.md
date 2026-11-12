# Bocas de cano (refeitas no nível da M4A1)

As bocas antigas que o jogo monta nas armas, nos mesmos ids e medidas de fora. Desenho próprio, sem
marcas. Uma peça só por id (malha `<id>_boca`), sem nós nem animações.

| id | O que é |
|---|---|
| `supressor_556_tan` | supressor 5,56 de pintura cerâmica caramelo, com gola recartilhada e trava de engate |
| `supressor_762_gasto` | supressor grosso de aço, usado |
| `quebra_chamas_556` | gaiola de 5 fendas, fechada embaixo |
| `freio_boca_308` | três câmaras abertas para os lados e dois furos em cima |
| `freio_rompimento_12` | abraçadeira, janelas laterais e coroa de oito dentes de aço |
| `protetor_rosca_308`, `protetor_rosca_9mm` | capas recartilhadas da rosca |

`modelo.py` (peças em mm, `../m4a1/lib.py`), `materiais.py`, `config.py`, `ver.py` e:
`python3 gerar.py <id> 512 saida && python3 jogo.py <id> saida` (1024 nos supressores).

De 1.396 a 2.968 triângulos, 1 conjunto de textura cada.
