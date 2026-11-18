# Lanternas e lasers de arma (refeitos no nível da M4A1)

Todos nos mesmos ids, encaixes e nós (`feixe`, de onde a luz sai; `laser`, de onde sai o raio) dos
antigos. Desenho próprio, sem marcas. O vidro (`<id>_vidro`) é transparente, o LED (`<id>_led`) e
a janela do laser (`<id>_emissor`) são acesos.

| Id | Encaixe | O que é |
|---|---|---|
| `lanterna_compacta`, `_gasto` | lado do guarda-mão | garra com borboleta, corpo recartilhado, coroa dentada, botão atrás |
| `lanterna_fuzil` | lado do guarda-mão | 1000 lm, duas pilhas, pescoço com aletas, suporte de dois anéis |
| `lanterna_pistola` | trilho curto | 600 lm, caixa de alumínio com a pilha atravessada e teclas dos dois lados |
| `laser_pistola` | trilho curto | caixinha de polímero, ajustes de latão, pilha de moeda, etiqueta de aviso |
| `combo_lanterna_laser` | trilho curto | lanterna de 500 lm com o laser pendurado embaixo e chave de três posições |
| `lanterna_cano_12` | cano da espingarda | abraçadeira de duas voltas (cano e tubo) com a lanterna de 800 lm à direita |
| `laser_fuzil` | esquerda do guarda-mão | caixa de alumínio com laser e farolete, seletor, botão e tomada de remoto |

`python3 gerar.py <id> 1024 saida && python3 jogo.py <id> saida`. De 1.555 a 6.146 triângulos,
1 conjunto de textura 1024 cada. As funções novas ficam no fim de `modelo.py` e usam os mesmos
ajudantes (`_farol`, `_emissor`, `_garra_trilho`, `_aletas`).

Armadilha: faixa recartilhada pousada sobre o corpo liso (0,45 mm acima) assa manchada; cada faixa
tem de ser um trecho próprio do torno, sem superfície por baixo.
