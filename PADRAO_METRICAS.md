# Padrão de medidas dos kits de prédios

Todo kit de prédio do pacote segue estas medidas, para que peças de kits diferentes se encaixem e o jogador se mova do mesmo jeito em qualquer prédio. 1 unidade = 1 metro, eixo Y para cima.

## Jogador de referência
| Medida | Valor |
|---|---|
| Altura da cápsula | 1,8 m |
| Raio da cápsula | 0,3 m (largura 0,6 m) |
| Altura dos olhos (câmera 1ª pessoa) | 1,6 m |
| Degrau máximo que sobe sem pular | 0,3 m (stepOffset / floor snap) |
| Rampa máxima andável | 35° |

O kit traz a peça `player_scale_ref` (cápsula azul) para conferir escala.

## Grade
| Medida | Valor |
|---|---|
| Grade de encaixe (snap) | 1 m; peças de parede ocupam 2 m |
| Módulo de fachada / parede | 2,0 m de largura |
| Planta do prédio | múltiplos de 2 m (ex.: 8×6 m, 10×8 m) |
| Cômodo mínimo | 4×4 m (2×2 módulos) |

## Alturas
| Medida | Valor |
|---|---|
| Andar a andar (residencial) | 3,0 m |
| Térreo residencial | 3,2 m |
| Térreo comercial / loja (kits futuros) | 4,0 m |
| Laje (piso + teto) | 0,2 m, topo do piso na cota do andar |
| Pé-direito livre | 2,8 m (térreo 3,0 m) |
| Parede interna | 2,8 m (vai do piso até o teto) |
| Cornija + platibanda | 1,4 m acima da última laje |

Cota do andar n: `térreo + (n−1) × 3,0`. Ex.: 1º andar 3,2 m, 2º 6,2 m, 3º 9,2 m.

## Paredes
| Medida | Valor |
|---|---|
| Parede externa | 0,3 m (face externa no limite da planta, espessura para dentro) |
| Parede interna | 0,12 m, centrada na linha da grade |
| Revestimento interno | 0,02 m, material `plaster` |

## Aberturas
| Abertura | Largura × altura | Observação |
|---|---|---|
| Porta interna | 0,9 × 2,1 m | folha `door_leaf_interior` 0,86 × 2,08 |
| Porta de entrada | 1,1 × 2,4 m | folha `door_leaf_entrance` 0,96 × 2,32 |
| Porta dupla / loja (futuro) | 2,0 × 2,4 m | ocupa um módulo inteiro |
| Porta de sacada | 0,9 × 2,3 m | começa 0,05 m acima do piso |
| Janela | 0,9 × 1,45 m | peitoril a 0,85 m do piso |

A folha de porta tem o pivô na dobradiça, para abrir girando em Y.

## Circulação
| Espaço | Largura livre | Uso |
|---|---|---|
| Passagem mínima | 0,9 m | porta, um jogador de cada vez |
| Corredor estreito | 1,2 m | corredor de serviço, 1ª pessoa |
| Corredor padrão | 2,0 m | um módulo; dois personagens passam, câmera em 3ª pessoa cabe |
| Corredor largo / saguão | 4,0 m | combate, multidões, câmera livre |
| Beco entre prédios | 2,0 m mínimo, 4,0 m recomendado | |
| Calçada | 2,0 m (uma peça `sidewalk_tile`) | |
| Faixa de rua | 3,0 m por pista | |

Largura livre é medida entre as faces internas das paredes. Em jogo de 3ª pessoa, use 2,0 m como mínimo em tudo que o jogador percorre.

## Escadas
| Medida | Valor |
|---|---|
| Espelho (altura do degrau) | 0,18 m (aceito 0,15–0,20) |
| Piso do degrau | ≥ 0,2 m |
| Largura livre | 1,2 m |
| Vão na laje | 2,7 × 4,0 m (núcleo de 4×4 m) |
| Altura livre sobre a escada | ≥ 2,2 m |
| Corrimão / guarda-corpo | 0,9 m |

Escada interna padrão: em U, com patamar, dentro de um núcleo de 4×4 m. Dois lances de 1,2 m de largura lado a lado, 9 degraus cada, 2 m de comprimento; patamar de 1,7 m ao fundo. Peças: `stairs_u_3m` (andar de 3 m) e `stairs_u_3m2` (térreo de 3,2 m), laje com vão `stair_core_slab` e guarda-corpo `stair_core_rail`.

## Prédio de apartamentos (planta de referência)
| Espaço | Medida |
|---|---|
| Planta do prédio | 16 × 10 m (8 × 5 módulos) |
| Núcleo de escada | 4 × 4 m, no centro do fundo |
| Hall de andar | 4 × 2 m na frente do núcleo, com as portas dos apartamentos |
| Apartamento | 6 × 10 m + quarto extra de 2 × 4 m (cerca de 68 m²) |
| Sala + cozinha | 6 × 6 m, com varanda na fachada |
| Quarto de casal | 4 × 4 m |
| Quarto de solteiro / escritório | 2 × 4 m |
| Banheiro | 2 × 2 m |
| Circulação interna | 2 × 2 m, liga sala, quarto e banheiro |

Paredes internas sempre em linhas da grade de 2 m, para que qualquer cômodo seja múltiplo do módulo.

## Escada externa (de incêndio)
| Medida | Valor |
|---|---|
| Largura livre do lance | 0,9 m |
| Espelho / piso | 0,176 m / 0,235 m (17 degraus por andar de 3 m) |
| Comprimento do lance | 4,0 m (dois módulos) |
| Guarda-corpo e corrimão | 1,0 m |
| Acesso | uma porta de sacada por andar na passagem; lance do térreo até a calçada; última plataforma no nível do terraço com abertura de 1,2 m na platibanda |

Os lances ficam empilhados no mesmo sentido: sobe, sai de lado na plataforma, volta pela passagem e pega o próximo lance.

## Varandas e externos
| Medida | Valor |
|---|---|
| Profundidade de sacada | 0,8 m |
| Plataforma de escada externa | 2,0 m de profundidade: 1,0 m de passagem junto à parede + 1,0 m para a escada |
| Guarda-corpo | 0,9 m |

## Colisão
Paredes, lajes e escadas são caixas simples, então podem usar a própria malha como colisor. Para escadas, um colisor em rampa (plano inclinado) deixa o movimento mais suave que os degraus.

## Encaixe sem flicker
Duas faces no mesmo plano, viradas para o mesmo lado e com cores ou texturas diferentes, piscam na tela (z-fighting). Regras para que as peças combinem sem isso:
- Nada termina exatamente na face de outra peça visível. Use recuo de pelo menos 2 cm, ou faça a peça entrar inteira dentro da outra.
- Lajes: a camada de piso vai até a borda do módulo; o corpo da laje fica 2 cm para dentro.
- Paredes internas que encostam na externa usam `interior_wall_end` (1,7 m), que para na face interna.
- Cantos externos: a coluna de canto envolve as pontas das duas paredes (1 cm a mais para dentro, 3 cm para fora).
- Peitoris, soleiras e degraus ficam 1 a 3 cm acima ou abaixo de pisos e plataformas vizinhos, nunca na mesma cota.
- Detalhes dentro da própria peça também seguem a regra, porque a peça precisa ficar limpa sozinha (modo explodido, catálogo, editor da engine):
  - peitoril 1,5 cm acima do fundo da abertura; verga 1 cm acima do topo da abertura; travessas da janela atrás do vidro, nunca no mesmo plano;
  - faixa entre andares e capitel do pilar sobem 1,5 cm acima do topo do módulo (escondem a borda da laje e nunca ficam no nível do topo da parede);
  - rodapés, faixas e embasamentos encostam na face da parede, sem entrar nela, para que as pontas não coincidam com a ponta da parede.

O script `verificar_flicker.py` (na pasta do kit) monta o prédio e lista todo par de faces coplanares visíveis. Rode após mudar uma peça; o resultado esperado é `TOTAL 0`. Com `SOLO=1` ele testa cada peça sozinha; sem a variável, testa o prédio montado. As duas verificações precisam dar zero.

## Nomes
`grupo_variante` em snake_case: `wall_*` (fachada), `corner_*`, `cornice_*`, `roof_*`, `floor_*`, `stairs_*`, `interior_wall_*`, `door_leaf_*`, adereços pelo nome do objeto. Materiais com nome fixo (`brick`, `stone`, `plaster`, `floor`...) para recolorir variações.

## Emendas invisíveis
- Paredes e lajes como malha fechada em grade retangular: sem triângulos finos e sem vértice no meio de aresta vizinha (junção em T).
- Contorno do estilo toon feito em tela (profundidade + normal) ou casco invertido, nunca por aresta de cada peça.

## Variedade entre prédios
- O padrão fixa só o que o jogador usa: alturas de andar, portas, corredores, escadas, módulo de 2 m e espessuras de parede.
- Cada prédio novo muda tamanho, planta (cômodos, número de apartamentos, posição da escada), número de andares e estilo. Não repetir a planta de outro kit.
- Telhados inclinados (mansarda): o sótão conta como andar de 3 m; paredes internas que encostam no telhado acompanham a inclinação com 1 cm de folga.
