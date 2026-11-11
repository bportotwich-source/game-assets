# Rifle Pardal .22 (refeito no nível da M4A1)

O rifle .22 do jogo, nos ids `rifle_22` (nogueira) e `rifle_22_sintetico` (polímero preto), com os
mesmos nós, encaixes e animações do antigo (`arma11_rifle22.py`), mais os dois acessórios que vêm
montados nele: `alca_cano_22` e `protetor_rosca_22`. Desenho próprio, sem marcas de fabricante.

Receptor de tubo azulado com trilho, janela de ejeção e trava do lado esquerdo; ferrolho polido
com alavanca de bola e indicador de armado; cano fino com massa de túnel e conta de latão;
carregador rotativo de 10 com base estriada; coronha inteiriça com punho e telha quadriculados
(pontilhados no sintético), soleira de borracha, guarda-mato de aço e placas de fixação na telha.

| Arquivo | Para quê |
|---|---|
| `modelo.py` | as peças, em mm (`../m4a1/lib.py`): `montar()` é o rifle; `alca_cano()` e `protetor_rosca()` são os acessórios |
| `materiais.py` | aço azulado, nogueira quadriculada e polímero pontilhado |
| `config.py` | o que a fábrica (`../m4a1/fabrica.py`) precisa: nós, origem, ids (rifle e acessórios) |
| `gerar.py` | modelo, UVs e bake: `python3 gerar.py 2048 saida`; `... 512 saida_alca alca` |
| `jogo.py` | GLB do jogo, versão leve e catálogo: `python3 jogo.py saida`; `... saida_alca alca` |
| `ver.py`, `foto.py` | renders de conferência (forma e textura); `MONTAR=montar,alca_cano,protetor_rosca` e `FOTO_MONTAR=a.blend,b.blend` mostram o rifle montado |
| `esqueleto*.json` | nós e animações tirados do rifle e dos acessórios antigos |

A coronha é o grupo de textura A e todo o resto é o B. O sintético (`VARIANTE=sintetico`) só troca
o material da coronha: copie os arquivos `pardal_B_*` da saída do rifle de nogueira para a pasta
`tex/` do sintético com o nome `pardal_sintetico_B_*` e só o grupo A é assado.

Números: 35.217 triângulos e 2 conjuntos 2048; com a alça (580), o protetor (672) e a luneta 4×
antiga são cerca de 41,6 mil na mão. Versão leve com 6.000 e 1 conjunto 1024.

## O que mudou de propósito

- A coronha passa por baixo do caminho do ferrolho (o ferrolho aberto não atravessa mais a madeira).
- A trava foi para o lado esquerdo do receptor, para não ficar embaixo da alavanca.
- A massa ganhou túnel de proteção e conta de latão.
- A luneta 4× pequena, o supressor e os carregadores avulsos continuam sendo os modelos antigos.
