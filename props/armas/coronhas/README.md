# Coronhas de troca (refeitas no nível da M4A1)

As coronhas que o jogador troca na tela da arma (tecla K), nos mesmos ids, encaixes e nós das
antigas. Desenho próprio, sem marcas.

| id | o que é |
|---|---|
| `coronha_fixa_ar`, `coronha_fixa_12` | fixa inteiriça de polímero (fuzis 5,56/.308 e espingarda), painéis rebaixados, soleira de borracha |
| `coronha_leve_ar` (+`_tan`) | tubo de 5 posições com a coronha leve de quadro vazado (nó `soleira`, estender/recolher) |
| `coronha_leve_ak` (+`_tan`) | adaptador de aço do 7,62 + o mesmo tubo e coronha leve |
| `coronha_retratil_ak` | adaptador de aço + tubo e coronha retrátil da M4A1 |
| `coronha_polimero_ak` | fixa de polímero no desenho da de madeira do Brasa, painel rebaixado |
| `coronha_rebativel_ak` | quadro de tubos de aço soldados que dobra para a esquerda (nó `dobra`, dobrar/abrir) |

`montagem.py` tem as peças (mm, `../m4a1/lib.py`; tubo nas coordenadas da M4A1, adaptador do
7,62 a partir de u = -165), `config.py` a origem (encaixe_coronha) e os nós de cada id.

    python3 gerar.py <id> 1024 saida && python3 jogo.py <id> saida
    VARIANTE=tan python3 gerar.py coronha_leve_ar_tan 1024 saida_tan && VARIANTE=tan python3 jogo.py coronha_leve_ar_tan saida_tan

As duas fixas são o mesmo modelo: gere uma vez e rode o `jogo.py` dos dois ids na mesma saída.
De 3,4 a 12 mil triângulos, 1 conjunto de textura 1024 cada.
