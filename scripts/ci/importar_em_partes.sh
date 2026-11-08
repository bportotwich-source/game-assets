#!/usr/bin/env bash
# Importa as peças no Godot em lotes de pastas. A primeira importação de todos
# os kits de uma vez (GLB + texturas extraídas) passa de 14 GB de memória e
# derruba o runner do CI; em lotes cada execução termina e libera a memória.
# Uso: scripts/ci/importar_em_partes.sh ./godot [pastas por lote]
set -u
GODOT=${1:-godot}
LOTE=${2:-4}
mapfile -t DIRS < <(ls -d kits/*/ props/*/ 2>/dev/null | sed 's#/$##')
for d in "${DIRS[@]}"; do touch "$d/.gdignore"; done
for ((i = 0; i < ${#DIRS[@]}; i += LOTE)); do
  for d in "${DIRS[@]:i:LOTE}"; do rm -f "$d/.gdignore"; done
  echo "Lote $((i / LOTE + 1)): ${DIRS[*]:i:LOTE}"
  timeout 1200 "$GODOT" --headless --import > /dev/null 2>&1 || echo "  aviso: saiu com $?"
done
for d in "${DIRS[@]}"; do rm -f "$d/.gdignore"; done
echo "Passada final"
timeout 1200 "$GODOT" --headless --import > /dev/null 2>&1 || echo "  aviso: saiu com $?"
