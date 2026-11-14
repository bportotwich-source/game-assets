# M4A1 detalhada (teste de modelagem)

Fuzil M4A1 modelado por script no Blender (módulo `bpy`), com cada peça em um objeto
próprio e texturas PBR assadas (cor, oclusão/rugosidade/metal, relevo). Desenho próprio,
sem marcas de fabricante; as gravações são em português.

- `m4a1.glb`: 73 peças (47 da arma clássica e 26 de acessórios), 7 conjuntos de textura
  2048 px em WebP. Origem no punho, cano para -Z, como as outras armas.
- A arma clássica usa os grupos de textura A a D; os acessórios usam E (frente),
  F (miras e laser) e G (coronhas, punho e carregadores).

## Acessórios e o que cada um substitui

Todas as peças estão no mesmo arquivo, já na posição de montagem. Para montar uma
variação, mostre as peças do acessório e esconda as que ele substitui.

| Encaixe | Opções (peças) |
| --- | --- |
| Guarda-mão | clássico (`guarda_mao_superior`, `guarda_mao_inferior`, `anel_delta`, `tampa_guarda_mao`, `base_massa`, `pino_base_massa_1/2`, `pino_massa`, `zarelho_frontal`) ou longo (`guarda_mao_longo`, `porca_cano`, `bloco_gas`) |
| Boca do cano | `quebra_chamas` + `arruela_boca` ou `supressor` |
| Mira | `alca_transporte` (com `alca_mira`, `botao_deriva`, `tambor_elevacao`, `porca_alca_1/2`), `luneta` + `suporte_luneta`, ou `mira_prismatica` + `tampa_lente_frente` + `tampa_lente_tras` + `suporte_prismatica` |
| Mira reflex a 45° | `mira_reflex` + `suporte_45` (só com o guarda-mão longo) |
| Laser | `modulo_laser` (só com o guarda-mão longo) |
| Lanterna | `lanterna` + `trilho_esquerdo` (só com o guarda-mão longo) |
| Empunhadura | `empunhadura_angulada` ou `empunhadura_vertical`, com `trilho_baixo` (só com o guarda-mão longo) |
| Carregador | `carregador` (com `transportador`, `cartucho_1/2`), `carregador_polimero` ou `carregador_tambor` |
| Punho | `punho` ou `punho_vazado` |
| Alavanca de manejo | `alavanca_manejo` + `trava_alavanca` ou `alavanca_ambi` |
| Tubo da coronha | `tubo_coronha` ou `tubo_coronha_vermelho` |
| Coronha | `coronha` + `trava_coronha` + `zarelho_traseiro`, `coronha_moderna` + `trava_coronha_moderna`, ou `coronha_fixa` |

## Como refazer

```
pip install bpy pillow numpy
python3 gerar.py 2048 saida          # modelo, UVs e bake (uns 30 min em 4 núcleos)
python3 empacotar.py saida/m4a1_sem_tex.glb saida/tex m4a1.glb webp
```

`lib.py` tem as primitivas, `modelo.py` a arma clássica, `acessorios.py` os acessórios,
`texturas.py` os materiais procedurais e o bake. `ver_ac.py` e `foto.py` fazem renders de
conferência. Um grupo de textura que já existe em `saida/tex` não é assado de novo;
`REASSAR=E,F` força os grupos listados.

## Versões de jogo (peças trocáveis)

A M4A1 do jogo é uma arma base com encaixes, como o fuzil Vigília (que é feito das mesmas
peças): `troca.py` diz o que vai em cada GLB e `gerar_troca.py` gera tudo.

```
python3 gerar_troca.py catalogo                 # registros no catalogo.json (sem Blender)
python3 gerar_troca.py base 2048 saida_base     # props/armas/armas/fuzil_m4a1.glb (receptores, cano, punho, carregador de metal)
python3 gerar_troca.py <acessorio> 1024 saida_x # props/armas/acessorios/<acessorio>.glb
python3 gerar.py 1024 saida_m4                  # a M4A1 inteira, para as versões leves
python3 gerar_troca.py montagens saida_m4       # fuzil_m4a1_luneta/_tatico (cópias da base) e as 3 versões leves
```

Encaixes da base: os do Vigília, nos mesmos lugares (punho, mira, alça, massa, boca, carregador,
coronha, empunhadura, lanterna, laser, bipé, bandoleira), mais `encaixe_guarda_mao`,
`encaixe_alavanca` (dentro do nó `alavanca`) e `encaixe_mira_45`. Empunhadura, lanterna, laser,
bipé, bandoleira, massa e mira a 45° pedem o guarda-mão longo (`requer`); a alça rebatível não
cabe com a alça de transporte (`proibe`).

| Acessório | Peças da M4A1 | Encaixe |
| --- | --- | --- |
| `guarda_mao_classico_m4` | guarda-mão superior e inferior, anel delta, tampa, base de massa com pinos, zarelho da frente | `guarda_mao_m4` |
| `guarda_mao_longo_m4` | guarda-mão longo, porca do cano, bloco de gás baixo | `guarda_mao_m4` |
| `alca_transporte_m4` | alça de transporte com a mira, tambor e botão (nó `olho` no furo; `ferro`: não deita as outras miras) | `trilho_mira` |
| `luneta_m4` | luneta 2-8× e suporte (campo `optica`) | `trilho_mira` |
| `mira_prismatica_m4` | mira prismática 3×, tampas e suporte (campo `optica`) | `trilho_mira` |
| `mira_45_m4` | mira reflex e suporte a 45° | `mira_45_m4` |
| `punho_vazado_m4` | punho vazado | `punho_ar` |
| `alavanca_ambi_m4` | alavanca de manejo ambidestra | `alavanca_ar` |
| `coronha_moderna_ar` | tubo vermelho, placa, porca e coronha moderna | `coronha_ar` |

O resto das montagens antigas usa os acessórios que já existem: `quebra_chamas_556`,
`supressor_556`, `coronha_retratil_ar` (a coronha da M4A1), `coronha_fixa_ar`, `carregador_556_30`,
`tambor_556_60_tatico`, `empunhadura_angulada`, `empunhadura_vertical`, `lanterna_compacta` e
`modulo_laser`.

| id | Peças de fábrica |
| --- | --- |
| `fuzil_m4a1` | guarda-mão clássico, alça de transporte, quebra-chamas, coronha retrátil |
| `fuzil_m4a1_luneta` | guarda-mão longo, luneta, supressor, empunhadura angulada, carregador de polímero, coronha fixa |
| `fuzil_m4a1_tatico` | guarda-mão longo, prismática, mira a 45°, supressor, laser, lanterna, empunhadura vertical, tambor de 60, punho vazado, alavanca ambidestra, coronha moderna |

As três montagens usam o mesmo modelo base (GLB copiado com a raiz renomeada); a versão leve
de cada uma (chão, armário) é a montagem de fábrica inteira numa malha só, e o `tamanho_m` do
catálogo é o dela.
