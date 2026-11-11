# Guardiã 9 mm detalhada (piloto das armas no nível da M4A1)

A pistola Guardiã refeita com o método da M4A1 (`../m4a1/`): modelada por script no
Blender (módulo `bpy`), com recortes de verdade (serrilhas, janelas, fendas do trilho,
estrias do cabo), quinas chanfradas e texturas PBR assadas (cor, oclusão/rugosidade/metal
e relevo) com desgaste nas arestas, sujeira nos cantos, quadriculado nas talas e gravações.
Desenho próprio, sem marcas de fabricante; as gravações são em português.

Ela entra no lugar da `pistola_guardia_9mm` antiga, com as mesmas medidas, os mesmos nós
e as mesmas animações. O jogo, os acessórios (talas, carregadores, bocas de cano, lanterna
de trilho, coldre) e os pontos das mãos continuam valendo sem mudança.

| Arquivo | O que é |
| --- | --- |
| `../armas/pistola_guardia_9mm.glb` | arma do jogo: 19 peças em nós próprios, 2 conjuntos de textura 2048 px (A: armação, talas, gatilho, carregador; B: ferrolho, cano, miras, cão, alavancas) |
| `../armas/pistola_guardia_9mm_leve.glb` | versão leve para ver de longe ou no chão: uma malha só, cerca de 6 mil triângulos, 1 conjunto de textura 1024 px assado da detalhada (campo `arquivo_leve` do catálogo) |

A `pistola_guardia_9mm_preta` é o mesmo modelo assado com outro acabamento (alumínio
anodizado, ferrolho oxidado e talas pretas): `VARIANTE=preta` nos dois comandos abaixo, com
outra pasta de saída. Ela também tem a versão leve (`pistola_guardia_9mm_preta_leve.glb`).
Os acessórios da Guardiã continuam saindo do `../arma14_guardia.py`.

## Orçamento do piloto

| | Teto do plano | Guardiã |
| --- | --- | --- |
| Triângulos na mão | 60 mil | ver `triangulos` no catálogo |
| Texturas na mão | 2 conjuntos 2048 | 2 conjuntos 2048 |
| Triângulos da versão leve | 6 mil | ver `triangulos_leve` no catálogo |
| Texturas da versão leve | 1 conjunto 1024 | 1 conjunto 1024 |

## Como refazer

```
pip install bpy pillow numpy shapely
python3 gerar.py 2048 saida          # modelo, UVs e bake (uns 7 min em 4 núcleos)
python3 jogo.py saida                # GLB do jogo, versão leve e catálogo
python3 foto.py saida/guardia.blend fotos/guardia esq 34d perto boca   # renders de conferência

VARIANTE=preta python3 gerar.py 2048 saida_preta    # a Guardiã preta
VARIANTE=preta python3 jogo.py saida_preta
```

- `modelo.py`: as peças, em milímetros (usa as primitivas de `../m4a1/lib.py`).
- `materiais.py`: as classes de material da pistola (pintura areia sobre alumínio e sobre
  aço, polímero areia, aço do cano) e o quadriculado das talas, somados aos de
  `../m4a1/texturas.py`. Com `VARIANTE=preta`, as mesmas classes ficam pretas.
- `config.py`: o que é só da Guardiã: origem, peças de cada nó, variantes (id e descrição).
- `gerar.py` e `jogo.py`: chamam `../m4a1/fabrica.py`, que é igual para toda arma refeita.
  `gerar` monta, desdobra, assa e salva `guardia.blend` (um grupo de textura que já existe
  em `saida/tex` não é assado de novo; `REASSAR=A,B` força). `jogo` põe as peças nos nós de
  `esqueleto.json`, grava as animações, mede os pontos `ref_*`, faz a versão leve e atualiza
  o `catalogo.json` (a arma fica com `"gerador": "guardia/jogo.py"`, e o `gerar_armas.py`
  não a sobrescreve).
- `esqueleto.json`: os nós (posições) e as animações da Guardiã antiga, tirados do GLB que
  o `arma14_guardia.py` gerava (`../m4a1/tirar_esqueleto.py`). É o que garante que nada muda
  para o jogo.
- `ver.py`: renders rápidos só da forma, sem textura.

## Para as próximas armas

Copiar `config.py`, `gerar.py`, `jogo.py` e `materiais.py` para a pasta da arma nova,
escrever o `modelo.py`, tirar o `esqueleto.json` do GLB antigo ANTES de sobrescrever
(`python3 ../m4a1/tirar_esqueleto.py ../armas/<id>.glb esqueleto.json`) e rodar os comandos
acima. As primitivas, os materiais, o bake, a versão leve e a troca no catálogo já estão
resolvidos na fábrica.
