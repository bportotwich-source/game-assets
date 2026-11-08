# Catálogo de veículos

Gerado por `props/veiculos/gerar_veiculos.py`. Design completo em [`docs/veiculos.md`](../../docs/veiculos.md). Medidas em metros (largura × altura × comprimento).

## Sedã Rumo (`sedan_rumo`)

Sedã compacto de 4 portas dos anos 80/90, desenho próprio e sem marca. Todas as peças da tabela 3,1 do design são nós separados; portas, capô, porta-malas, porta-luvas, assoalho do porta-malas, portinhola do tanque e quebra-sóis abrem.

Medidas 2,08 × 1,55 × 4,50 m · 224550 triângulos · 11,1 MB

| Nó | Tipo | Vira o item | Precisa para andar | Abre | Ferramentas | Tempo (tirar / pôr) |
|---|---|---|---|---|---|---|
| `capo` | tampa | `capo` | - | -68° em x | jogo_de_chaves | 30 s / 40 s |
| `tampa_porta_malas` | tampa | `tampa_porta_malas` | - | 72° em x | jogo_de_chaves | 30 s / 40 s |
| `porta_de` | porta | `porta_dianteira_e` | - | -66° em y | jogo_de_chaves | 60 s / 75 s |
| `porta_dd` | porta | `porta_dianteira_d` | - | 66° em y | jogo_de_chaves | 60 s / 75 s |
| `porta_te` | porta | `porta_traseira_e` | - | -66° em y | jogo_de_chaves | 60 s / 75 s |
| `porta_td` | porta | `porta_traseira_d` | - | 66° em y | jogo_de_chaves | 60 s / 75 s |
| `paralama_e` | peca | `paralama_e` | - | - | jogo_de_chaves | 60 s / 70 s |
| `paralama_d` | peca | `paralama_d` | - | - | jogo_de_chaves | 60 s / 70 s |
| `tampa_combustivel` | tampa | - | - | -80° em y | - | - |
| `para_brisa` | peca | `para_brisa` | - | - | jogo_de_chaves | 90 s / 120 s |
| `vidro_traseiro` | peca | `vidro_traseiro` | - | - | jogo_de_chaves | 90 s / 120 s |
| `para_choque_d` | peca | `para_choque_dianteiro` | - | - | jogo_de_chaves | 40 s / 50 s |
| `para_choque_t` | peca | `para_choque_traseiro` | - | - | jogo_de_chaves | 40 s / 50 s |
| `farol_e` | peca | `farol` | - | - | jogo_de_chaves | 20 s / 25 s |
| `farol_d` | peca | `farol` | - | - | jogo_de_chaves | 20 s / 25 s |
| `lanterna_e` | peca | `lanterna_traseira` | - | - | jogo_de_chaves | 15 s / 20 s |
| `lanterna_d` | peca | `lanterna_traseira` | - | - | jogo_de_chaves | 15 s / 20 s |
| `retrovisor_e` | peca | `retrovisor` | - | - | - | 5 s / 20 s |
| `retrovisor_d` | peca | `retrovisor` | - | - | - | 5 s / 20 s |
| `roda_de` | roda | `roda_aro14` | sim | - | chave_de_roda, macaco_sanfona ou macaco_jacare | 40 s / 50 s |
| `roda_dd` | roda | `roda_aro14` | sim | - | chave_de_roda, macaco_sanfona ou macaco_jacare | 40 s / 50 s |
| `roda_te` | roda | `roda_aro14` | sim | - | chave_de_roda, macaco_sanfona ou macaco_jacare | 40 s / 50 s |
| `roda_td` | roda | `roda_aro14` | sim | - | chave_de_roda, macaco_sanfona ou macaco_jacare | 40 s / 50 s |
| `estepe` | peca | `roda_aro14` | - | - | - | 5 s / 5 s |
| `motor` | peca | `motor_1_6` | sim | - | jogo_de_chaves, talha | 240 s / 300 s |
| `alternador` | peca | `alternador` | - | - | jogo_de_chaves | 45 s / 60 s |
| `radiador` | peca | `radiador` | - | - | jogo_de_chaves | 60 s / 75 s |
| `bateria` | peca | `bateria_12v` | sim | - | jogo_de_chaves ou chave_inglesa | 15 s / 20 s |
| `escapamento` | peca | `escapamento` | - | - | jogo_de_chaves, macaco_sanfona ou macaco_jacare | 60 s / 75 s |
| `tanque` | peca | `tanque_45l` | sim | - | jogo_de_chaves, macaco_sanfona ou macaco_jacare | 90 s / 120 s |
| `banco_motorista` | peca | `banco_dianteiro` | sim | - | jogo_de_chaves | 60 s / 70 s |
| `banco_passageiro` | peca | `banco_dianteiro` | - | - | jogo_de_chaves | 60 s / 70 s |
| `banco_traseiro` | peca | `banco_traseiro` | - | - | jogo_de_chaves | 60 s / 70 s |
| `volante` | peca | `volante` | sim | - | jogo_de_chaves | 30 s / 30 s |
| `porta_luvas` | tampa | - | - | -75° em x | - | - |
| `assoalho_porta_malas` | tampa | - | - | 75° em x | - | - |
| `quebra_sol_e` | tampa | - | - | -80° em x | - | - |
| `quebra_sol_d` | tampa | - | - | -80° em x | - | - |

| Compartimento | Grade | Abre por |
|---|---|---|
| Porta-malas (`porta_malas`) | 9 × 5 | `tampa_porta_malas` |
| Fundo do porta-malas (`fundo_porta_malas`) | 3 × 3 | `assoalho_porta_malas` |
| Porta-luvas (`porta_luvas`) | 3 × 2 | `porta_luvas` |
| Bolsa da porta do motorista (`bolsa_porta_de`) | 3 × 1 | `porta_de` |
| Bolsa da porta do passageiro (`bolsa_porta_dd`) | 3 × 1 | `porta_dd` |
| Console (`console`) | 2 × 1 | sempre aberto |
| Quebra-sol do motorista (`quebra_sol_e`) | 1 × 1 | `quebra_sol_e` |
| Quebra-sol do passageiro (`quebra_sol_d`) | 1 × 1 | `quebra_sol_d` |
| Banco de trás (`banco_tras`) | 8 × 4 | sempre aberto |

## Peças (loot)

| Item | Padrão | Peso | Grade | Função | Triângulos |
|---|---|---|---|---|---|
| Capô (`capo`) | sedan_rumo | 14 kg | carga nas mãos | protege o motor de batidas e da chuva | 3334 |
| Tampa do porta-malas (`tampa_porta_malas`) | sedan_rumo | 10 kg | carga nas mãos | fecha e tranca o porta-malas | 2162 |
| Porta dianteira esquerda (`porta_dianteira_e`) | sedan_rumo | 22 kg | carga nas mãos | protege o motorista; vidro e bolsa da porta | 9910 |
| Porta dianteira direita (`porta_dianteira_d`) | sedan_rumo | 22 kg | carga nas mãos | protege o passageiro; vidro e bolsa da porta | 9880 |
| Porta traseira esquerda (`porta_traseira_e`) | sedan_rumo | 18 kg | carga nas mãos | protege quem vai atrás | 6576 |
| Porta traseira direita (`porta_traseira_d`) | sedan_rumo | 18 kg | carga nas mãos | protege quem vai atrás | 6490 |
| Para-lama dianteiro esquerdo (`paralama_e`) | sedan_rumo | 5 kg | 4 × 2 | protege a roda e o farol de lado | 5560 |
| Para-lama dianteiro direito (`paralama_d`) | sedan_rumo | 5 kg | 4 × 2 | protege a roda e o farol de lado | 5534 |
| Para-brisa (`para_brisa`) | sedan_rumo | 12 kg | carga nas mãos | protege a frente da cabine (30% de quebrar ao tirar) | 2552 |
| Vidro traseiro (`vidro_traseiro`) | sedan_rumo | 8 kg | carga nas mãos | protege a traseira da cabine | 1856 |
| Para-choque dianteiro (`para_choque_dianteiro`) | sedan_rumo | 7 kg | 7 × 1 | absorve a primeira parte das batidas de frente | 7864 |
| Para-choque traseiro (`para_choque_traseiro`) | sedan_rumo | 7 kg | 7 × 1 | absorve a primeira parte das batidas de trás | 7688 |
| Farol com pisca (`farol`) | universal | 2 kg | 2 × 1 | ilumina um lado da frente à noite | 1408 |
| Lanterna traseira (`lanterna_traseira`) | universal | 1 kg | 2 × 1 | luz de freio, de ré e pisca | 504 |
| Retrovisor (`retrovisor`) | universal | 0,8 kg | 1 × 1 | mostra o que vem atrás | 114 |
| Roda aro 14 com pneu (`roda_aro14`) | aro14_4furos | 16 kg | 3 × 3 | roda de aço com pneu 185/70; também é o estepe | 9344 |
| Motor 1,6 (`motor_1_6`) | compacto_1_6 | 118 kg | carga nas mãos | dá força ao carro; condição baixa falha, perde força e gasta mais | 6624 |
| Alternador (`alternador`) | compacto_1_6 | 5 kg | 2 × 2 | recarrega a bateria com o motor ligado | 532 |
| Radiador (`radiador`) | compacto_1_6 | 6 kg | 4 × 3 | esfria o motor; sem ele o motor ferve em 2 minutos | 992 |
| Bateria 12 V (`bateria_12v`) | bateria_12v | 14 kg | 2 × 2 | dá partida e alimenta faróis, buzina e rádio; serve no gerador da base | 696 |
| Escapamento com silencioso (`escapamento`) | compacto_1_6 | 8 kg | 6 × 1 | sem ele o motor faz o dobro de barulho | 2092 |
| Tanque de combustível 45 L (`tanque_45l`) | sedan_rumo | 9 kg | 5 × 3 | guarda 45 L de combustível | 172 |
| Banco dianteiro (`banco_dianteiro`) | universal | 15 kg | carga nas mãos | sem o banco do motorista não dá para dirigir | 6256 |
| Banco traseiro (`banco_traseiro`) | universal | 20 kg | carga nas mãos | leva 3 passageiros; sem ele o espaço vira carga | 6028 |
| Volante (`volante`) | universal | 2,5 kg | 2 × 2 | tirar o volante trava o carro contra roubo | 1208 |

## Ferramentas e materiais de oficina (loot)

| Item | Peso | Grade | Para que serve | Aparece em | Triângulos |
|---|---|---|---|---|---|
| Chave de roda em cruz (`chave_de_roda`) | 1,3 kg | 2 × 2 | tira e põe as rodas (com o macaco) | garagem, posto, concessionaria, ferro_velho, porta_malas | 784 |
| Macaco sanfona (`macaco_sanfona`) | 3,2 kg | 3 × 1 | ergue o carro para trocar roda, tanque e escapamento | garagem, posto, concessionaria, ferro_velho, porta_malas | 2408 |
| Caixa com jogo de chaves (`jogo_de_chaves`) | 6,5 kg | 3 × 2 | ferramenta geral da oficina: quase toda peça pede | garagem, posto, concessionaria, ferro_velho, porta_malas, oficina, fabrica | 568 |
| Mangueira para sifão (`mangueira_sifao`) | 0,5 kg | 2 × 2 | puxa combustível de um tanque para um galão (1 L a cada 6 s) | garagem, posto, ferro_velho, fazenda | 3016 |
| Cabos de chupeta (`cabos_chupeta`) | 1,6 kg | 2 × 2 | dá partida com a bateria de outro carro ou do gerador | garagem, posto, concessionaria, ferro_velho, porta_malas | 5056 |
| Bomba de ar manual (`bomba_ar`) | 1,4 kg | 3 × 1 | enche pneu murcho (de 30 para 100% em 40 s) | garagem, posto, loja, porta_malas | 952 |
| Kit de remendo de pneu (`kit_remendo_pneu`) | 0,3 kg | 1 × 1 | conserta pneu furado: volta para 60% (5 usos) | garagem, posto, porta_malas, loja | 212 |
| Óleo de motor 1 L (`oleo_motor`) | 0,95 kg | 1 × 1 | +15% de condição do motor (até 70%) | garagem, posto, concessionaria, ferro_velho, porta_malas, supermercado | 2184 |
| Velas de ignição (jogo de 4) (`velas_ignicao`) | 0,3 kg | 1 × 1 | +20% de condição do motor (até 80%) e menos falha na partida | garagem, posto, concessionaria, ferro_velho | 728 |
| Chave de carro (`chave_carro`) | 0,03 kg | 1 × 1 | abre e liga um carro específico (o item guarda qual) | carro, quebra_sol, zumbi, casa | 460 |
| Kit de ligação direta (`kit_ligacao_direta`) | 0,35 kg | 2 × 1 | liga o carro sem chave: 20 s, 70% de chance (falha queima um fusível) | garagem, ferro_velho, delegacia, zumbi | 1544 |
