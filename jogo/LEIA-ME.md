# Recomeço: marco M0 (fundação)

Começo do jogo de sobrevivência zumbi + comunidade + construção de cidade descrito em
[docs/plano-jogo-sobrevivencia.md](../docs/plano-jogo-sobrevivencia.md).

Fica dentro do mesmo projeto Godot do pacote de assets, para usar os kits e os props
direto, sem copiar nada. No menu do `GameAssets.exe` é o botão **Jogar Recomeço (teste do M0)**.
Se depois o jogo for para um repositório próprio, basta levar esta pasta e apontar para os
kits usados.

## O que já tem

- **Mapa de teste:** um cruzamento com 5 kits do pacote, cada um em ruínas com uma
  intensidade e uma semente: mercado (supermercado), padaria, delegacia, posto de gasolina
  e casa de dois andares (casa-americana). Asfalto, faixas, calçadas com meio-fio, postes
  apagados e lixo espalhado com itens de `props/mobilias` e `props/loot`.
- **Natureza tomando conta** (`mundo/natureza.gd`): árvores (muitas mortas), arbustos, mato,
  flores e pedras do pacote `props/natureza` (Quaternius, CC0), espalhados por semente nos
  terrenos e nas frestas de calçada e asfalto. Mato e flores em MultiMesh.
- **Ruínas geradas na hora** (`mundo/ruinas.gd`): caem algumas telhas (a lista do que caiu
  fica no prédio, para o reparo do M2), parte dos vidros quebra, tudo ganha encardido
  (mais forte perto do chão, com escorridos nas paredes), algumas portas ficam abertas e
  aparece entulho dentro e na calçada. A mesma semente estraga sempre do mesmo jeito.
- **LOD:** os GLB já ganham níveis de detalhe automáticos na importação do Godot. Por cima
  disso, cada prédio vira um bloco simples a partir de 220 m e o entulho pequeno some a
  partir de 70 m.
- **As 3 vistas** (`cameras/vistas.gd`), com uma câmera só que desliza entre elas:
  - **1ª pessoa:** nos olhos (1,65 m).
  - **3ª pessoa (V):** atrás do ombro direito; encostada em parede, aproxima sozinha.
  - **Vista de cima (Tab):** modo prefeito, com a grade de 2 m projetada no chão, cursor
    no lote e ficha do prédio ao clicar (dados em `dados/predios.json`).
- Contador de fps no canto, para medir os 60 fps pedidos no M0.

No plano, o modo prefeito só destrava quando chega o primeiro sobrevivente. No M0 ele fica
liberado para testar.

## Controles

| Vista | Teclas |
|---|---|
| A pé (1ª e 3ª) | WASD andar, Shift correr, Ctrl devagar, Espaço pular, E ou clique abre portas, V troca 1ª/3ª |
| De cima | WASD move, Q/E ou botão direito arrastando giram, roda aproxima, Espaço volta ao sobrevivente, clique num prédio mostra a ficha |
| Sempre | Tab entra e sai da vista de cima, Esc pausa (continuar, menu, sair) |

## Arquivos

| Arquivo | Para quê |
|---|---|
| `jogo.tscn`, `jogo.gd` | Cena principal: mundo, entrada, HUD e pausa |
| `dados/mapa_teste.json` | Ruas e quais kits ficam em cada quadra (com ruína e semente) |
| `dados/predios.json` | Dados de jogo por kit: nome, função, saque, capacidade, reparo |
| `mundo/predio.gd` | Monta um kit a partir do `building_layout.json`, com colisão e portas |
| `mundo/ruinas.gd`, `mundo/encardido.gdshader` | Variante em ruínas |
| `mundo/ruas.gd` | Asfalto, calçadas, faixas e postes |
| `mundo/natureza.gd` | Árvores, mato, flores e pedras |
| `personagem/sobrevivente.gd` | Corpo e movimento do sobrevivente (boneco provisório) |
| `cameras/vistas.gd` | As 3 vistas e a troca suave |

Para trocar um prédio do mapa, mude o `kit` em `dados/mapa_teste.json` (qualquer pasta de
`kits/`) e acrescente a ficha dele em `dados/predios.json`.

## Ainda não tem (próximos marcos)

Zumbis, saque, inventário, necessidades e dia/noite são o M1. O boneco é o
`player_scale_ref` dos kits até entrar o pacote CC0 de personagens.
