# Carregadores avulsos (refeitos no nível da M4A1)

Os 26 carregadores e tambores que o jogador troca na tela da arma e o carregador rápido do
revólver, nos mesmos ids e encaixes dos antigos. Desenho próprio, sem marcas.

Cada um nasce do carregador que já vem na arma refeita, no tamanho do avulso (mesma boca,
mesmos lábios, mesmo encaixe): `montagem.py` carrega o modelo da arma (`../<arma>/modelo.py`,
com as cores dela) e muda o comprimento (`ML`), o arco (Brasa) ou o número gravado. Os que não
têm par na arma são peças de `montagem.py`: tambores de 60 (5,56), 75 (7,62) e 50 (Ciclone), o
de 60 de quatro fileiras, a caixa de 25 do .22 e o carregador rápido do .38.

`config.py` diz, para cada id, a função, a origem (o nó `carregador` da arma, onde fica o
encaixe) e a descrição. No fim as peças viram uma malha só, `carregador`.

    python3 gerar.py <id> 1024 saida && python3 jogo.py <id> saida
