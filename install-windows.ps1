# Script de instalación para Windows Server
# Ejecutar como Administrador

Write-Host "=== Instalación de STL en Windows Server ===" -ForegroundColor Green

# Verificar si se ejecuta como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host "Haz clic derecho en PowerShell y selecciona 'Ejecutar como administrador'" -ForegroundColor Yellow
    exit 1
}

# Verificar si Docker Desktop está instalado
try {
    docker version | Out-Null
    Write-Host "✓ Docker Desktop detectado" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop no está instalado" -ForegroundColor Red
    Write-Host "Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar si Git está instalado
try {
    git --version | Out-Null
    Write-Host "✓ Git detectado" -ForegroundColor Green
} catch {
    Write-Host "✗ Git no está instalado" -ForegroundColor Red
    Write-Host "Por favor instala Git desde: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Clonar o actualizar el repositorio
if (Test-Path "stlw") {
    Write-Host "Actualizando código desde GitHub..." -ForegroundColor Yellow
    Set-Location stlw
    git pull origin main
} else {
    Write-Host "Clonando repositorio..." -ForegroundColor Yellow
    git clone https://github.com/rasaliad/stlw.git
    Set-Location stlw
}

# Configurar variables de entorno
if (-not (Test-Path ".env")) {
    Write-Host "`nConfigurando variables de entorno..." -ForegroundColor Yellow
    Copy-Item .env.windows.example .env
    
    Write-Host "`n⚠️  IMPORTANTE: Edita el archivo .env con las credenciales correctas:" -ForegroundColor Yellow
    Write-Host "    notepad .env" -ForegroundColor Cyan
    Write-Host "`nAsegúrate de configurar:" -ForegroundColor Yellow
    Write-Host "  - FIREBIRD_DATABASE: Ruta completa a tu base de datos (ej: C:/App/STL/Datos/DATOS_STL.FDB)"
    Write-Host "  - FIREBIRD_USER y FIREBIRD_PASSWORD"
    Write-Host "  - SECRET_KEY: Una clave segura para JWT"
    Write-Host ""
    
    $response = Read-Host "¿Deseas editar el archivo .env ahora? (S/N)"
    if ($response -eq 'S' -or $response -eq 's') {
        notepad .env
        Write-Host "Esperando a que cierres el editor..." -ForegroundColor Yellow
        Read-Host "Presiona Enter cuando hayas guardado el archivo .env"
    }
}

# Verificar puerto 3050 de Firebird
Write-Host "`nVerificando Firebird en puerto 3050..." -ForegroundColor Yellow
$firebirdPort = netstat -an | Select-String ":3050"
if ($firebirdPort) {
    Write-Host "✓ Firebird detectado en puerto 3050" -ForegroundColor Green
} else {
    Write-Host "⚠️  No se detectó Firebird en puerto 3050" -ForegroundColor Yellow
    Write-Host "   Asegúrate de que Firebird esté ejecutándose" -ForegroundColor Yellow
}

# Crear reglas de firewall para los puertos
Write-Host "`nConfigurando reglas de firewall..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "STL Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "STL Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
Write-Host "✓ Reglas de firewall configuradas para puertos 3000 y 8000" -ForegroundColor Green

# Construir y ejecutar los contenedores
Write-Host "`nConstruyendo y ejecutando contenedores Docker..." -ForegroundColor Yellow
docker-compose -f docker-compose.windows.yml down
docker-compose -f docker-compose.windows.yml up -d --build

# Esperar a que los servicios estén listos
Write-Host "`nEsperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar el estado
Write-Host "`n=== Estado de los servicios ===" -ForegroundColor Yellow
docker-compose -f docker-compose.windows.yml ps

Write-Host "`n=== Verificando salud de los servicios ===" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "✓ Backend funcionando correctamente" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend no responde aún" -ForegroundColor Red
}

Write-Host "`n✅ Instalación completada!" -ForegroundColor Green
Write-Host "`nURLs de acceso:" -ForegroundColor Yellow
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Documentación API: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`nComandos útiles:" -ForegroundColor Yellow
Write-Host "  - Ver logs: docker-compose -f docker-compose.windows.yml logs -f" -ForegroundColor Gray
Write-Host "  - Detener: docker-compose -f docker-compose.windows.yml down" -ForegroundColor Gray
Write-Host "  - Reiniciar: docker-compose -f docker-compose.windows.yml restart" -ForegroundColor Gray

Write-Host "`nPresiona cualquier tecla para finalizar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")