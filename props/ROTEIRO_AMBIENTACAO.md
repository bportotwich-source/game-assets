# Ambientação dos prédios

Cada kit de `kits/` tem um `ambientacao.json` com os móveis e itens de `props/` já posicionados dentro dele: sala com sofá e rack, cozinha com geladeira e fogão, cela com colchão no chão, galpão com porta-pallet e empilhadeira, e assim por diante. O jogo e o "Visitar os prédios prontos" leem esse arquivo e põem cada GLB no lugar.

## Como é gerado

```
python3 scripts/ambientacao/ambientar.py              # todos os kits
python3 scripts/ambientacao/ambientar.py padaria diner
python3 scripts/ambientacao/comodos.py kits/padaria --png planta.png   # só ver os cômodos detectados
```

1. **Cômodos** (`comodos.py`): monta as peças do `building_layout.json` (sem as folhas de porta), lança raios de cima para achar o piso livre de cada andar, corta a malha a 0,5, 1,0 e 1,6 m para achar paredes e móveis fixos, marca os vãos de porta e separa as áreas livres em cômodos. Também anota a peça de piso de cada cômodo (`floor_tile_bath` indica banheiro ou cozinha, `porch_deck` varanda, `garage_floor` garagem, `roof_*` telhado).
2. **Tipo de cada cômodo** (`kits.json`): cada kit tem um perfil.
   - `perfil: casa`: os cômodos molhados viram banheiro (pequeno) ou cozinha; os outros, pela ordem de tamanho, viram sala, jantar, lavanderia... no térreo e quarto, quarto de criança, quarto de solteiro... nos andares de cima. `seq: "apto"` faz o andar inteiro de apartamento (sala, quarto, cozinha...). `casas_x` separa casas lado a lado (brownstones, shotgun, vitorianas, duplex).
   - perfil comercial (padrão): o maior cômodo é o `principal` (salão do diner, nave da igreja, galpão da fábrica...) e os outros seguem `seq` pela ordem de tamanho.
   - Em todos: cômodo pequeno vira banheiro ou lavabo, estreito vira corredor, e área de fora (que encosta na borda do terreno) vira `externo` (quintal, pátio, estacionamento, campo do minigolfe, pátio do drive-in...).
   - `andares` muda o perfil num andar (`"2+"` vale do andar 2 para cima), `ignorar_andares` pula sótãos sem acesso e `comodos` força o tipo do cômodo que contém um ponto `[x, z]`.
3. **Itens de cada tipo** (`TIPOS` em `ambientar.py`): lista de `(item, quantidade, regra, chance)`. A quantidade cresce com a área do cômodo (até 3 vezes). Todo cômodo também pode ganhar sinais do fim do mundo (cacos, papéis, manchas, cadeira quebrada, pichação, marca de busca).
4. **Posição**:
   - `parede`: encostado numa parede, de costas para ela;
   - `centro`: no meio do cômodo, com 0,6 m livres em volta (gôndolas, bancos da igreja, carteiras, poltronas do cinema);
   - `livre`: em qualquer lugar livre e girado ao acaso (entulho, loot no chão);
   - `muro`: pendurado na parede, na `altura_sugerida_m` do item.
   - Mesas ganham cadeiras em volta, viradas para elas.
   - Nada fica a menos de 0,9 m de uma porta, em cima de outro item ou atravessando parede (grade de 25 cm).
   - O sorteio usa uma semente fixa por kit, então rodar de novo dá o mesmo resultado.

## O arquivo

```json
{
 "kit": "padaria",
 "niveis": {"0": 0.0, "1": 4.0, "2": 7.0},
 "comodos": [{"andar": 0, "comodo": 1, "tipo": "padaria_loja", "area_m2": 38.6, "centro": [0.04, 2.86], "itens": 9}],
 "itens": [{"item": "vitrine_tortas", "grupo": "mobilias", "arquivo": "props/mobilias/vitrine_tortas.glb", "pos": [3.1, 0.0, 4.2], "rotY": 180, "andar": 0, "comodo": "padaria_loja"}]
}
```

- `pos` está no espaço do prédio (o mesmo do `building_layout.json`), em metros. `rotY` em graus, no mesmo sentido das peças do kit.
- Itens de parede (`montagem: wall`) já vêm na altura certa, com o pivô na face de trás.
- Os dados de jogo de cada item (contêiner, saque, coleta, barricada...) estão no `catalogo.json` de `props/`, pelo `item`.

## Ajustar

- Um cômodo com o tipo errado: acrescente em `kits.json` uma regra `{"andar": 0, "ponto": [x, z], "tipo": "cozinha"}` (o `comodos.py --png` mostra os números e o centro de cada cômodo).
- Um tipo com itens de menos ou de mais: mude a lista em `TIPOS`.
- Itens únicos de um prédio só: `"extras": {"tipo": [["item", 1, "parede", 1.0]]}` no kit.
