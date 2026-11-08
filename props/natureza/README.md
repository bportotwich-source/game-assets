# Natureza (Stylized Nature MegaKit, Quaternius)

116 modelos de natureza estilizada: 40 árvores (comum, morta, pinheiro, pinheiro gigante, bétula, cerejeira, torta, alta), 6 arbustos, 10 plantas, 11 tipos de mato e trevo, 18 flores, 4 cogumelos e 27 pedras, pedrinhas e pedras de caminho.

- **Origem:** Stylized Nature MegaKit [Pro], de Quaternius (https://quaternius.com), comprado pelo Bruno no itch.io.
- **Licença:** CC0 1.0 (domínio público), ver `LICENCA_Quaternius_CC0.txt`. Pode ficar neste repositório público e ir no jogo.
- **Formato:** glTF (`.gltf` + `.bin`) com as texturas PNG compartilhadas ao lado. As texturas de 2048 px (cascas e pedras) foram reduzidas para 1024 px.
- **Escala:** 1 unidade = 1 m, Y para cima, pivô na base. O mato vem grande (até 1,9 m) e o jogo usa ele em 0,5 a 0,6.
- `catalogo.json`: id, tipo (arvore, arbusto, planta, mato, flor, cogumelo, pedra) e tamanho de cada modelo.

No Recomeço, `jogo/mundo/natureza.gd` espalha estes modelos pelos terrenos vazios e pelas frestas das calçadas.
