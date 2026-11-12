# Lunetas (refeitas no nível da M4A1)

As seis lunetas que já vêm montadas nas armas do jogo, nos mesmos ids, com o mesmo ponto `olho`,
o mesmo comprimento e a mesma altura de eixo das antigas. Desenho próprio, sem marcas.

| id | Aumento | Vem em | Jeito |
|---|---|---|---|
| `luneta_1_6` | 1 a 6× | fuzil 5,56 bicolor | tubo de 30 mm reto, torres altas, base inteiriça |
| `luneta_3_9` | 3 a 9× | carabina .308 | tubo de 30 mm, sino de 44 mm, torres com tampa, dois anéis |
| `luneta_4x` | 4× | carabina .308 de caça | tubo de 1 polegada, torres com tampa, dois anéis |
| `luneta_4x_22` | 4× | rifle .22 | tubo fino, botões baixos, dois anéis |
| `luneta_5_25` | 5 a 25× | fuzil .308 de precisão | tubo de 34 mm, torres altas, paralaxe do lado, base inteiriça |
| `luneta_besta` | 3× | besta | curta, botão de luz do lado, base inteiriça |

Todas têm ocular com borda de borracha e anel de foco, sela com as torres, anéis de suporte em duas
metades com parafusos e base que abraça o trilho (barra de aperto e porcas do lado esquerdo).

**Lentes e zoom.** As duas lentes são uma malha separada (`<id>_lente`), planas e recuadas 6 mm
dentro do tubo. O catálogo ganha o campo `optica` (tipo, aumento, centro e raio da lente de trás,
centro da lente da frente, retículo): é com ele que o Recomeço desenha o zoom só dentro da lente.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | `SPECS` (medidas de cada uma) e `luneta(id)`, em mm (`../m4a1/lib.py`) |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa, uma entrada por id |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py luneta_3_9 1024 saida` |
| `jogo.py` | GLB em `../acessorios/` e catálogo: `python3 jogo.py luneta_3_9 saida` |
| `ver.py` | renders de conferência da forma |
| `esqueleto_<id>.json` | ponto `olho` tirado de cada luneta antiga |

Números: de 8,7 a 10,4 mil triângulos e 1 conjunto 1024 cada.

Cuidado ao mexer: anel ou luva por cima do corpo precisa de pelo menos 1,5 mm de parede e de corpo
mais fino por baixo; uma superfície a menos de 1,4 mm de outra assa manchada.
