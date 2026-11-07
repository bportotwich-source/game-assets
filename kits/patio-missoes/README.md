# Kit 25: pátio de missão (alto detalhe)

Conjunto em estilo missão do sudoeste em volta de um pátio fechado: casa principal com arcada, 3 casitas geminadas de terraço, um ateliê, portão em arco com campanário e muros com capa de telha. Feito no padrão de alto detalhe com a biblioteca [`scripts/detalhe/detalhe.py`](../../scripts/detalhe/detalhe.py). Segue o [padrão de medidas](../../PADRAO_METRICAS.md). Arte original.

## O conjunto
- **Pátio** de 24 × 18 m com lajotas de barro e chafariz octogonal com bacia e taça.
- **Casa principal** de 12 × 8 m em reboco grosso com barrado, pé-direito de 3,9 m e piso a 0,15 m. Telhado de duas águas a 25° com **telhas capa-canal modeladas uma a uma**, beirais com caibros aparentes, forro de tábuas, beirada nas pontas e cumeeira argamassada. Óculo redondo nos oitões, janelas em arco com caixilho de madeira, grades de ferro (rejas) nas janelas dos fundos e das laterais.
- **Arcada** de 2,6 m na frente da casa: 6 arcos plenos sobre pilares com impostas e barrado, piso de lajota com degrau de bocel, telhado de uma água em telha, caibros e lanterna pendente na porta.
- **Dentro da casa**: sala, cozinha com porta lateral para o pátio, 2 quartos e banheiro (piso de ladrilho), forro de varas entre vigas roliças, portas internas de tábua com verga de madeira.
- **3 casitas** geminadas de 6 × 6 m e o **ateliê** de 6 × 6 m: terraço com platibanda arredondada, manta com caimento, gárgulas (canales) de madeira, vigas roliças que atravessam a parede, lareira de canto (kiva) com chaminé de 2 manilhas, alpendre de telha com mãos-francesas sobre a porta e degrau de lajota.
- **Portão** de 2,4 m em arco pleno com folhas de tábua cravejadas, campanário curvo (espadaña) com nicho e sino de bronze. Muros de 1,8 m com capa de telha de duas águas e pilares com pináculo.

Números: 65 peças, 311 posições, 12 portas, cerca de 178 mil triângulos no montado.

## Montagem
Casitas em x de -12 a -6 (unidades centradas em z -6, 0 e 6, paredes-meias em z ±3); ateliê em x de 6 a 12 e z de 3 a 9; casa em x de -4 a 8 e z de -9 a -1, arcada até z 1,6; portão em z 9. As paredes têm pivô no centro inferior da face externa, na cota do piso.
- `c_wall_*` são módulos de 2 m das casitas com platibanda (`_side` sem pontas de viga, para os oitões); `c_roof_*` é a laje inteira de cada casita.
- `m_roof*` são faixas de 2 m de uma água (pivô na face da parede; `_end_l/_r` têm a beirada da ponta), `m_ridge` é uma peça só.
- `m_ceiling` é um forro de 2 × 2 m; as variantes `m_ceiling_eXXXX` param na face interna das paredes externas (flags x-, x+, z-, z+).
- `arcade_*` têm pivô na face da casa (`arcade_arch` na frente da arcada); `_end_l/_r` fecham as pontas.
- Portas: a folha da direita do portão vai girada 180° e abre com -80°.

## Texturas (PBR, embutidas nos GLB como JPEG)
`render`, `plaster`, `tile_clay`, `saltillo`, `pavers`, `wood`, `planks`, `plinth` e `roofdeck`. Ladrilho de 2 m, UV em metros / 2. Os PNG soltos (`*_albedo`, `*_normal`, `*_orm`) estão na pasta.

## Testes
- `verificar_flicker.py`: TOTAL 0 com tudo montado e com `SOLO=1` (cada peça sozinha).
- Godot 4.3: o jogador entra pelo portão e cruza o pátio até a arcada; passa pela arcada, entra pela porta principal, cruza a sala e entra no banheiro pela porta interna; entra numa casita e no ateliê pela porta; sai da cozinha pela porta lateral para o pátio. No visitante é o prédio 25 (use `]` / Page Down).

## Regenerar
```
pip install trimesh shapely numpy pillow scipy rtree mapbox_earcut manifold3d bpy
python kits/patio-missoes/gerar_kit.py        # escreve em out/ ao lado do script
python kits/patio-missoes/verificar_flicker.py
```
