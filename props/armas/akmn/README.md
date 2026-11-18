# Fuzil AKMN 7,62 e peças táticas (modelos de terceiros, CC BY 4.0)

Primeira arma do pacote que **não** foi modelada aqui. Os modelos são de **suspensy** e têm licença
**CC BY 4.0** (uso livre, inclusive comercial, com crédito):

- AKMN: https://sketchfab.com/3d-models/akmn-8a32337fe2eb4d528f82021d44e13bc8
- AKMN Zenitco: https://sketchfab.com/3d-models/akmn-zenitco-da587952abc9430fb2a2ae731c28daac
- Autor: suspensy (ArtStation https://www.artstation.com/artwork/P463rB); licença https://creativecommons.org/licenses/by/4.0/

O crédito vai no campo `credito` do catálogo, na descrição de cada item e nos créditos do Recomeço.
Mudanças feitas aqui: as malhas foram separadas em partes móveis e acessórios, postas na escala,
orientação e origem do jogo, as texturas foram reempacotadas (ORM, normal OpenGL) e algumas peças
ganharam textura própria; animações e encaixes vêm do Brasa 7,62. Os FBX e as texturas originais
(downloads do Sketchfab, uns 260 MB) ficam fora do repositório, na pasta do projeto.

| Id | O que é |
|---|---|
| `fuzil_akmn` | o fuzil com coronha e guarda-mão de madeira, punho de baquelite e freio inclinado |
| `fuzil_akmn_tatico` | o mesmo GLB com as peças táticas montadas por padrão |
| `coronha_madeira_akmn`, `guarda_mao_madeira_akmn`, `punho_akmn`, `freio_akmn` | as peças que vêm no AKMN |
| `coronha_rebativel_akmn`, `guarda_mao_longo_akmn`, `punho_tatico_akmn`, `carregador_762_30_polimero`, `trilho_lateral_akmn`, `batente_akmn` | as peças táticas (do AKMN Zenitco) |

Partes móveis e animações iguais às do Brasa (`tampa`, `gatilho`, `seletor`, `ferrolho`, `carregador`;
`atirar`, `recarregar`, `recarregar_vazia`, `inspecionar`, `trocar_modo`...), com os pivôs medidos no
AKMN. Encaixes: os do Brasa (cano, carregador, trilho lateral, baioneta, bandoleira, empunhadura,
lanterna e laser no guarda-mão longo) mais `encaixe_punho` (punho trocável) e `encaixe_mira_trilho`
(mira em cima do trilho de montagem lateral). Aceita os acessórios do Brasa que não dependem do
formato do receptor: freio, compensador e supressor 7,62, todos os carregadores 7,62, mira e luneta
de montagem lateral, empunhaduras, lanternas, lasers, tiras de borracha e baioneta. O carregador de
polímero novo também serve no Brasa. Os dois punhos também entram no Brasa, nos fuzis de alumínio (5,56, M4A1,
.308 de precisão) e na carabina .308: ver `../punhos/README.md` (campo `ajuste` do encaixe e o adaptador).

## Como refazer

Precisa de `pip install bpy pillow numpy`. Extraia `source/akm_2026.zip` (de `akmn.zip`) e
`source/akm.zip` (de `akmn-zenitco.zip`); cada FBX tem a pasta `textures/` ao lado.

    python3 importar.py <akm.fbx> <akm_zntc2.fbx> <saida>     # cenas, texturas, medidas e esqueletos
    python3 jogo.py tudo <saida>                              # catálogo, acessórios, fuzil, versões leves, CATALOGO.md
    python3 foto.py fuzil_akmn_tatico /tmp/f.png encaixe_mira_trilho=mira_holografica vista=34

| Arquivo | Para quê |
|---|---|
| `config.py` | que malha do FBX vai para que peça, ids, nomes, acessórios e padrões |
| `importar.py` | FBX -> cenas do Blender na origem do jogo; mede pivôs e encaixes (`medidas.json`) e escreve `esqueleto.json` (nós e animações do Brasa nas medidas do AKMN) |
| `jogo.py` | catálogo e GLBs (usa `../m4a1/fabrica.py`) |
| `foto.py` | foto de conferência de qualquer arma do catálogo montada com acessórios |

Números: fuzil 37,8 mil triângulos (receptor e cano em 2048); na mão com as peças de madeira ~45 mil,
com as táticas ~57 mil. O guarda-mão longo sozinho tem 30,5 mil. Versões leves de 6 mil com 1 conjunto 1024.

Atenção: as peças táticas reproduzem produtos reais e trazem as gravações do fabricante na textura
(nomes em russo na coronha, no guarda-mão e no trilho).
