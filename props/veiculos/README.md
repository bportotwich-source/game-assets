# Veículos

Carros originais do Recomeço, feitos em peças separadas para o jogador desmontar carros abandonados e montar um carro que anda. Como os carros se comportam no jogo (peças, condição, montagem, combustível, porta-malas, dano) está em [`docs/veiculos.md`](../../docs/veiculos.md). A lista completa de partes, peças e ferramentas, gerada junto com os modelos, está em [`CATALOGO.md`](CATALOGO.md).

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `sedan_rumo.glb` | O sedã Rumo inteiro: 38 partes, cada uma um nó (portas, capô, porta-malas, para-choques, faróis, lanternas, retrovisores, 4 rodas e o estepe, motor, alternador, radiador, bateria, escapamento, tanque, bancos, volante, porta-luvas, assoalho do porta-malas, portinhola do tanque, quebra-sóis) e 19 pontos para o jogo (câmera de 1ª pessoa, assentos, saídas, bocal do tanque, luzes, macaco, talha) |
| `hatch_brisa.glb` | O hatch Brisa, da família Rumo: mesma frente, portas dianteiras, motor, rodas, tanque e interior do sedã (as peças trocam entre os dois), com a traseira curta e a tampa traseira que abre com o vidro |
| `picape_lida.glb` | A picape Lida, desenho próprio com a mecânica do Rumo: frente quadrada e alta, faróis duplos, para-choques cromados, alargadores nas rodas, cabine simples, caçamba aberta (10 × 6 casas, 600 kg) com assoalho frisado, caixas de roda, ganchos e o estepe preso, tampa que cai para trás |
| `van_jornada.glb` | A van Jornada, desenho próprio com a mecânica do Rumo: bico curto e redondo, para-brisa grande, teto alto contínuo com nervuras, baú (10 × 8 casas, 650 kg) com assoalho de compensado, forração, trilhos de amarrar, divisória com grade, poço do estepe e duas portas atrás que abrem para os lados |
| `pecas/<id>.glb` | Cada peça que sai do carro, sozinha, deitada e com o pivô no centro da base: é o item de loot (55 peças; as que os carros dividem aparecem uma vez só, geradas pelo sedã) |
| `ferramentas/<id>.glb` | Ferramentas e materiais da oficina: chave de roda, macaco sanfona, caixa com jogo de chaves, mangueira de sifão, cabos de chupeta, bomba de ar, kit de remendo, óleo, velas, chave de carro e kit de ligação direta |
| `catalogo.json` | Dados de jogo: o modelo (física, combustível, partes com dobradiças e regras de montagem, compartimentos com grade e saque, pontos) e as listas `pecas` e `ferramentas` no mesmo formato do loot (`celulas`, `peso_kg`, `empilha`, `onde`, `efeito`) |
| `gerar_veiculos.py` | Gera tudo. Materiais, exportação, catálogo |
| `veiculo01_sedan.py`, `sedan_forma.py` | O sedã: perfis e seções da carroceria, e cada peça |
| `veiculo03_picape.py`, `picape_forma.py` | A picape: cabine simples, a caçamba cortada na casca e montada por dentro |
| `veiculo04_van.py`, `van_forma.py` | A van: o teto sobe atrás da cabine para o baú, as portas de trás são regiões extras da casca |
| `veiculo02_hatch.py`, `hatch_forma.py` | O hatch: usa as funções do sedã e troca só a traseira (perfil, tampa, lanternas, porta-malas) |
| `forma.py` | Ferramentas de forma: seções lofadas, booleanos, regiões de painel, varreduras |
| `ferramentas.py` | As ferramentas de oficina |

## Gerar

```
pip install trimesh shapely numpy pillow scipy manifold3d mapbox_earcut
python props/veiculos/gerar_veiculos.py                 # tudo (uns 25 s)
python props/veiculos/gerar_veiculos.py sedan_rumo      # só um carro e as peças dele (sedan_rumo, hatch_brisa, picape_lida, van_jornada)
python props/veiculos/gerar_veiculos.py ferramentas     # só as ferramentas
DESGASTE=0.7 python props/veiculos/gerar_veiculos.py   # pintura mais suja (0 = limpa, 1 = muito suja; padrão 0,35)
```

## Como o modelo é feito

- A carroceria é uma casca só: a parte de baixo (capô, laterais, porta-malas) e a cabine são lofts de seções suavizadas ao longo do carro, unidas e ocadas. Os vidros, as caixas de roda e os buracos dos faróis são cortados com booleanos exatos.
- Depois a casca é dividida por **regiões**: cada porta, o capô, a tampa do porta-malas e os para-lamas ficam com o pedaço de chapa dentro da sua região, e a carroceria perde a região mais 4 mm de vão. Por isso as peças, montadas, formam uma superfície contínua, e quando uma sai sobra o buraco certo. O friso lateral, os vidros das portas e o miolo das portas (batente e forro) são divididos pelas mesmas regiões.
- Cada parte tem a origem na dobradiça (portas, capô, tampas), no centro do cubo (rodas) ou no ponto de fixação (resto). O catálogo diz `eixo` e `abre_graus` com sinal, igual às partes dos móveis, então o `movel.gd` do jogo já sabe abrir.

## Convenções

- Y para cima, 1 unidade = 1 m, frente do carro para **+Z** (o que o `VehicleBody3D` do Godot espera), lado esquerdo (motorista) em **+X**. Pivô no chão, no meio dos eixos.
- Material `pintura`: textura clara com a sujeira que sobe da rua; a cor vem do `baseColorFactor`, que o jogo sorteia de `cores_sorteio`.
- Outros materiais com nome fixo: `vidro`, `cromado`, `borracha`, `pneu`, `plastico_preto`, `lente_farol`, `lente_lanterna`, `lente_pisca`, `lente_re`, `lampada` (o jogo acende pelo `emission`), `chassi`.
- Sem marcas nem textos: emblema liso, placas lisas, mostradores só com riscos e ícones.

## Próximos veículos

Os quatro modelos estão prontos (sedã, hatch, picape e van). Um modelo novo entra como um `veiculoNN_<nome>.py` com `@modelo(...)` e uma `<nome>_forma.py` que carrega `sedan_forma.py` e troca o que muda: só a traseira, como `hatch_forma.py`, ou também a frente (`FAROL`, `GRADE`, `SUFIXO_FRENTE`, perfis), como `picape_forma.py` e `van_forma.py`.
