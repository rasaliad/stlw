#!/bin/bash

# Script de despliegue para servidores sin Docker
set -e

echo "🚀 Iniciando despliegue sin Docker..."

# Variables (ajusta según tu configuración)
BACKEND_DIR="/ruta/al/backend"
FRONTEND_DIR="/ruta/al/frontend"
BACKEND_SERVICE="nombre-servicio-backend"  # nombre en systemd/supervisor/pm2
FRONTEND_SERVICE="nombre-servicio-frontend"

# Actualizar código
echo "📦 Actualizando código..."
git pull origin main

# Backend
echo "🔧 Actualizando Backend..."
cd $BACKEND_DIR
# Si tienes requirements.txt actualizado
pip install -r requirements.txt

# Reiniciar backend (ajusta según tu configuración)
# systemctl restart $BACKEND_SERVICE
# supervisorctl restart $BACKEND_SERVICE
# pm2 restart $BACKEND_SERVICE

# Frontend
echo "🎨 Actualizando Frontend..."
cd $FRONTEND_DIR
npm install
npm run build

# Reiniciar frontend
# systemctl restart $FRONTEND_SERVICE
# pm2 restart $FRONTEND_SERVICE

echo "✅ Despliegue completado"