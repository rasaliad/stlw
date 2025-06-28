#!/bin/bash

# Script de instalación para el servidor STL

echo "=== Instalación de STL en el servidor ==="

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker no está instalado. Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker instalado. Por favor, cierra sesión y vuelve a entrar para aplicar los cambios."
    exit 1
fi

# Verificar si docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose no está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Verificar si Git está instalado
if ! command -v git &> /dev/null; then
    echo "Git no está instalado. Instalando Git..."
    sudo apt-get update && sudo apt-get install -y git
fi

# Clonar o actualizar el repositorio
if [ -d "stlw" ]; then
    echo "Actualizando código desde GitHub..."
    cd stlw
    git pull origin main
else
    echo "Clonando repositorio..."
    git clone https://github.com/rasaliad/stlw.git
    cd stlw
fi

# Configurar variables de entorno
if [ ! -f ".env" ]; then
    echo "Configurando variables de entorno..."
    cp .env.server.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con las credenciales correctas:"
    echo "    nano .env"
    echo ""
    echo "Asegúrate de configurar:"
    echo "  - FIREBIRD_DATABASE: Ruta completa a tu base de datos .FDB"
    echo "  - FIREBIRD_USER y FIREBIRD_PASSWORD"
    echo "  - SECRET_KEY: Una clave segura para JWT"
    echo ""
    read -p "Presiona Enter cuando hayas configurado el .env..."
fi

# Construir y ejecutar los contenedores
echo "Construyendo y ejecutando contenedores Docker..."
docker-compose -f docker-compose.server.yml down
docker-compose -f docker-compose.server.yml up -d --build

# Esperar a que los servicios estén listos
echo "Esperando a que los servicios estén listos..."
sleep 10

# Verificar el estado
echo ""
echo "=== Estado de los servicios ==="
docker-compose -f docker-compose.server.yml ps

echo ""
echo "=== Verificando salud de los servicios ==="
curl -s http://localhost:8000/health || echo "Backend no responde aún"
echo ""

echo ""
echo "✅ Instalación completada!"
echo ""
echo "URLs de acceso:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - Documentación API: http://localhost:8000/docs"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: docker-compose -f docker-compose.server.yml logs -f"
echo "  - Detener: docker-compose -f docker-compose.server.yml down"
echo "  - Reiniciar: docker-compose -f docker-compose.server.yml restart"
echo ""