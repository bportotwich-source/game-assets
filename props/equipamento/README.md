# Equipamentos vestíveis do Recomeço

Capacetes, coletes de proteção e coletes táticos **originais** para os espaços de equipamento do inventário do jogo
(`capacete`, `colete`, `colete_tatico`). Gerados por script (`gerar_equipamento.py`, Python + trimesh + booleanos manifold), com as
primitivas e materiais de `props/gerar_props.py` e o padrão de alto detalhe dos kits (tecido cordura, velcro, malha, camuflado e
tinta granulada em textura PBR própria; bolsas, fivelas, costuras, fitas MOLLE e trilhos em geometria). Nenhuma marca real.

```
props/equipamento/
  gerar_equipamento.py   gera tudo:  python props/equipamento/gerar_equipamento.py   (ou só alguns ids)
  capacetes.py           capacetes      coletes.py  coletes de proteção      taticos.py  coletes táticos
  catalogo.json          dados de jogo (gerado)      CATALOGO.md  tabelas em português (gerado)
  <id>.glb               os modelos
```

## Convenções

- Y para cima, 1 unidade = 1 m, medidas reais (jogador de 1,8 m, `PADRAO_METRICAS.md`). Frente do equipamento para **+Z**.
- **Pose de repouso (como o item é achado no saque e fotografado para o ícone):** capacetes em pé, apoiados na borda; coletes
  **deitados de costas no chão** (frente para cima, gola para -Z), para a foto de cima do ícone mostrar a frente com as bolsas.
  Pivô no centro da base, como o loot.
- **Vestir no personagem:** o campo `vestir` diz como. Capacete: `cabeca_m` é o ponto do GLB que vai no centro da cabeça (sem girar).
  Colete: gire `girar_graus` (90° em X põe de pé) e ponha `peito_m` no centro do peito. Os coletes táticos já são um pouco
  maiores que os de proteção, para caberem por cima.
- **Viseiras** (capacete de moto e de choque) são nós separados com origem no eixo, descritos em `partes`
  (`tipo: gira`, `eixo`, `abre_graus`), como as portas das mobílias.
- **Materiais com nome** (`cordura_coiote`, `cordura_verde`, `camo_mata`, `pc_vermelho`...) para trocar a cor na engine.

## Dados de jogo (catalogo.json)

| Campo | O que é |
|---|---|
| `equipa` | espaço onde veste: `capacete`, `colete` ou `colete_tatico` (o `inventario.gd` do jogo já lê) |
| `celulas` | tamanho do item na grade do inventário `[largura, altura]` |
| `grade` | só coletes táticos: a grade que ele abre quando vestido (o jogo usa esse valor no lugar do 4 × 2 padrão) |
| `bolsos` | como essa grade se divide nas bolsas do modelo (informação; a soma das células bate com a grade) |
| `protecao`, `protege` | pontos de proteção contra mordida e golpe, e as partes do corpo cobertas |
| `balistico` | até que tiro segura: `nenhum`, `pistola`, `fuzil` |
| `durabilidade` | mordidas/golpes até precisar de reparo |
| `penalidade` | multiplicadores enquanto vestido: `cansaco_correr`, `ruido_passos`, `audicao`, `visao` |
| `peso_kg`, `raridade`, `valor_troca`, `onde`, `fase` | como no resto do pacote |

## Lista

| Espaço | Item | Células | Grade | Proteção |
|---|---|---|---|---|
| capacete | Capacete de obra (`capacete_obra`) | 2×2 | - | 22 |
| capacete | Capacete de ciclismo (`capacete_ciclismo`) | 2×2 | - | 12 |
| capacete | Capacete de moto fechado, viseira móvel (`capacete_moto`) | 2×2 | - | 40 |
| capacete | Capacete balístico de corte alto (`capacete_militar`) | 2×2 | - | 55 |
| capacete | Capacete de choque, viseira e protetor de nuca (`capacete_choque`) | 2×2 | - | 45 |
| colete | Colete à prova de balas policial (`colete_policial`) | 3×3 | - | 38 |
| colete | Colete porta-placas (`colete_portaplacas`) | 3×3 | - | 60 |
| colete | Colete militar de cobertura total (`colete_militar`) | 3×4 | - | 80 |
| colete_tatico | Peitoral de carregadores (`peitoral_carregadores`) | 3×2 | 4×2 | 0 |
| colete_tatico | Colete de pesca multibolsos (`colete_pesca`) | 3×2 | 5×2 | 3 |
| colete_tatico | Colete de carga de tela (`colete_carga`) | 3×3 | 4×3 | 4 |
| colete_tatico | Colete de assalto com bolsas (`colete_assalto`) | 3×3 | 5×3 | 8 |

Os improvisados continuam no loot (lote 15): `capacete_panela`, `colete_revistas`, `colete_sucata`, `bolsa_cintura`.

## Uso no jogo

O Recomeço lê `props/loot/catalogo.json` e `props/armas/catalogo.json`; basta acrescentar `props/equipamento/catalogo.json` na
lista de `carregar_catalogo()` e a pasta no `scripts/baixar_assets.sh`. Os campos `equipa`, `celulas` e `grade` já são os que o
inventário usa.
