# Modo Mobiliar

Tela do GameAssets.exe para arrumar os móveis dos prédios prontos com o mouse
(menu inicial, "Mobiliar os prédios").

- **Catálogo** embaixo, por cômodo, com busca. Clique numa peça e depois no prédio.
- **Móvel de chão**: grade de 25 cm; perto de uma parede, encosta de costas nela.
- **Item de parede** (quadro, relógio, armário aéreo): gruda na face real da parede,
  na altura sugerida do catálogo. Shift + roda muda a altura.
- **Verde** cabe, **vermelho** não cabe (janela, porta, outro móvel, parede).
- Clique num móvel para escolher; clique de novo (ou M) para mover. R gira,
  Delete apaga, Ctrl+D duplica, Ctrl+Z desfaz, setas empurram.
- **"N com problema"** leva para a próxima peça mal colocada do prédio.
- **"Encostar tudo"** cola na parede os quadros soltos no ar e fecha o vão atrás
  dos móveis. O que sobrar marcado (em cima de janela, por exemplo) é para mover ou apagar.
- **Paredes cortadas** esconde as paredes entre a câmera e o ponto para onde ela olha.

## Onde salva

O formato é o `kits/<kit>/ambientacao.json` que o modo Visitar e o Recomeço já leem,
com `"editado_a_mao": true` (o `scripts/ambientacao/ambientar.py` não sorteia por cima
de um prédio assim, só com `--forcar`).

- Rodando pelo código-fonte no Godot: grava direto em `kits/<kit>/ambientacao.json`.
- No .exe: grava em `mobilias/<kit>/ambientacao.json`, na pasta do .exe. Essa versão
  passa a valer no Mobiliar e no Visitar. Para ir para o jogo, o arquivo precisa
  ser copiado para `kits/<kit>/` no repositório.

Fontes Barlow em `fontes/` (SIL OFL 1.1, ver `fontes/LEIAME.md`).
