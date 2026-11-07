# Catálogo de armas, acessórios e munição

Gerado por `props/armas/gerar_armas.py` a partir de `catalogo.json`. Medidas em metros (largura × altura × comprimento).

## Armas

| Arma | Calibre | Tiros | Dano | Alcance | Cadência | Ruído | Durab. | Peso | Encaixes | Animações |
|---|---|---|---|---|---|---|---|---|---|---|
| Pistola Sentinela 9 mm (`pistola_9mm`) | 9 mm | 15 | 34 | 25 m | 4,0/s | 60 m | 600 | 0,78 kg | mira, boca, trilho, carregador | atirar, atirar_ultimo, vazia, recarregar, recarregar_vazia, inspecionar, ocioso |

## Acessórios

| Acessório | Tipo | Encaixe | Efeito no jogo | Peso | Raridade | Triângulos |
|---|---|---|---|---|---|---|
| Protetor de rosca 9 mm (`protetor_rosca_9mm`) | Boca do cano | `boca_rosca_9mm` | - | 0,01 kg | comum | 640 |
| Supressor 9 mm (`supressor_9mm`) | Boca do cano | `boca_rosca_9mm` | ruido_m ×0,3, dano ×0,95, alcance_m ×1,05, recuo ×0,85 | 0,2 kg | raro | 4056 |
| Compensador 9 mm (`compensador_9mm`) | Boca do cano | `boca_rosca_9mm` | recuo ×0,7, ruido_m ×1,15 | 0,04 kg | incomum | 548 |
| Supressor improvisado (garrafa PET) (`supressor_garrafa`) | Boca do cano | `boca_rosca_9mm` | ruido_m ×0,55, precisao ×0,8 | 0,08 kg | comum | 2672 |
| Lanterna tática de trilho (`lanterna_pistola`) | Trilho | `trilho_curto` | - | 0,11 kg | incomum | 4468 |
| Mira laser de trilho (`laser_pistola`) | Trilho | `trilho_curto` | precisao_sem_mirar ×1,35 | 0,06 kg | raro | 848 |
| Lanterna com laser (`combo_lanterna_laser`) | Trilho | `trilho_curto` | precisao_sem_mirar ×1,35 | 0,15 kg | muito raro | 1208 |
| Mira de ponto vermelho compacta (`mira_ponto_vermelho_compacta`) | Miras | `mira_ferrolho` | precisao_mirando ×1,25, tempo_mirar ×0,85 | 0,03 kg | raro | 540 |
| Carregador 9 mm (15) (`carregador_9mm`) | Carregadores | `carregador_9mm` | - | 0,09 kg | comum | 1192 |
| Carregador 9 mm estendido (24) (`carregador_9mm_estendido`) | Carregadores | `carregador_9mm` | recarga_s ×1,1 | 0,13 kg | raro | 1386 |

## Munição e efeitos

| Item | Tipo | Descrição | Triângulos |
|---|---|---|---|
| Cartucho 9 mm (`municao_9mm`) | Munição | Um cartucho (deitado, pivô no centro). No inventário conta por unidade. | 672 |
| Estojo 9 mm (vazio) (`estojo_9mm`) | Estojos | Estojo ejetado: o jogo cria um em saida_estojo a cada tiro (corpo rígido pequeno, some depois de uns segundos). | 496 |
| Caixa de munição 9 mm (50) (`caixa_municao_9mm`) | Caixas de munição | Caixa de papelão com bandeja de 50 cartuchos. A tampa abre (nó "tampa", animação "abrir"). | 14004 |
| Clarão de boca (`clarao_boca`) | Efeitos | Mostrar por 1 ou 2 quadros no encaixe boca_fogo a cada tiro; girar ao acaso em -Z e variar a escala (0,8 a 1,2). Material emissivo com transparência. | 372 |

## Compatibilidade

- **Pistola Sentinela 9 mm**, `encaixe_mira`: mira_ponto_vermelho_compacta
- **Pistola Sentinela 9 mm**, `encaixe_boca`: protetor_rosca_9mm, supressor_9mm, compensador_9mm, supressor_garrafa
- **Pistola Sentinela 9 mm**, `encaixe_trilho`: lanterna_pistola, laser_pistola, combo_lanterna_laser
- **Pistola Sentinela 9 mm**, `encaixe_carregador`: carregador_9mm, carregador_9mm_estendido
