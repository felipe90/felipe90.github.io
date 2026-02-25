#!/bin/bash

# Vibe Watcher - Monitorea cambios y actualiza el diario atomáticamente
# Uso: ./vibe-watcher.sh [intervalo_en_segundos]

INTERVAL=${1:-60}
PROJECT_DIR="$(pwd)"
JOURNEY_FILE="$PROJECT_DIR/VIBE_CODING_JOURNEY.md"

echo "🌊 Vibe Watcher iniciado en $PROJECT_DIR"
echo "👀 Monitoreando cada $INTERVAL segundos..."

# Guardar el estado inicial de modificación
LAST_RUN_TIME=$(date +%s)

while true; do
  # Buscar archivos modificados recientemente (excluyendo .git, node_modules y el propio diario)
  MODIFIED_FILES=$(find . -type f -not -path '*/.*' -not -name "VIBE_CODING_JOURNEY.md" -newermt "@$LAST_RUN_TIME" 2>/dev/null)

  if [ -n "$MODIFIED_FILES" ]; then
    echo "✨ Cambios detectados en:"
    echo "$MODIFIED_FILES"
    
    echo "🤖 Invocando a Gemini para actualizar el diario..."
    
    # Ejecutar Gemini en modo headless (no interactivo)
    # Le pasamos el contexto de los archivos modificados
    PROMPT="He detectado cambios en estos archivos: $MODIFIED_FILES. Por favor, analiza lo que ha pasado y añade una entrada concisa a VIBE_CODING_JOURNEY.md siguiendo el formato existente."
    
    # Usamos npx para asegurar que usamos la versión instalada
    npx -y @google/gemini-cli --prompt "$PROMPT"
    
    if [ $? -eq 0 ]; then
      echo "✅ Diario actualizado con éxito."
    else
      echo "❌ Error al intentar actualizar el diario con Gemini."
    fi
    
    # Actualizar la marca de tiempo para la próxima revisión
    LAST_RUN_TIME=$(date +%s)
  fi

  sleep "$INTERVAL"
done
