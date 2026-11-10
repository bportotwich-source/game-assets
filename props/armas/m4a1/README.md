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

Ainda não tem os pontos `ref_`, os encaixes e as animações do padrão das outras armas.
