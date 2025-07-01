#!/bin/bash

# Script de despliegue automático
set -e

echo "🚀 Iniciando despliegue..."

# Commit y push de cambios locales
echo "📦 Subiendo cambios a Git..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# Si tienes SSH configurado al servidor remoto:
# ssh usuario@servidor-remoto << 'EOF'
# cd /ruta/al/proyecto
# git pull origin main
# docker-compose down
# docker-compose build --no-cache
# docker-compose up -d
# echo "✅ Despliegue completado"
# EOF

echo "✅ Cambios subidos a Git. Ejecuta en el servidor:"
echo "git pull origin main && docker-compose down && docker-compose build --no-cache && docker-compose up -d"