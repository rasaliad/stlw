# Script para ejecutar STL sin Docker en Windows Server
# Ejecutar como Administrador

Write-Host "=== Configurando STL sin Docker en Windows Server ===" -ForegroundColor Green

# Verificar Python
Write-Host "`nVerificando Python..." -ForegroundColor Yellow
try {
    python --version
    Write-Host "Python detectado" -ForegroundColor Green
} catch {
    Write-Host "Python no está instalado. Descargando..." -ForegroundColor Yellow
    # Descargar Python 3.12
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe" -OutFile "python-installer.exe"
    Write-Host "Instala Python manualmente ejecutando: python-installer.exe" -ForegroundColor Yellow
    Write-Host "Asegúrate de marcar 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}

# Verificar Node.js
Write-Host "`nVerificando Node.js..." -ForegroundColor Yellow
try {
    node --version
    Write-Host "Node.js detectado" -ForegroundColor Green
} catch {
    Write-Host "Node.js no está instalado. Descargando..." -ForegroundColor Yellow
    # Descargar Node.js
    Invoke-WebRequest -Uri "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi" -OutFile "node-installer.msi"
    Write-Host "Instala Node.js ejecutando: msiexec /i node-installer.msi" -ForegroundColor Yellow
    exit 1
}

# Clonar el repositorio si no existe
if (-not (Test-Path "stlw")) {
    git clone https://github.com/rasaliad/stlw.git
}

Set-Location stlw

# Configurar Backend
Write-Host "`n=== Configurando Backend ===" -ForegroundColor Yellow
Set-Location backend

# Crear entorno virtual Python
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activar entorno virtual
& .\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env si no existe
if (-not (Test-Path ".env")) {
    @"
SECRET_KEY=tu-clave-secreta-cambiar-en-produccion
FIREBIRD_HOST=localhost
FIREBIRD_PORT=3050
FIREBIRD_DATABASE=C:/App/STL/Datos/DATOS_STL.FDB
FIREBIRD_USER=sysdba
FIREBIRD_PASSWORD=masterkey
"@ | Out-File -FilePath .env -Encoding UTF8
    
    Write-Host "Edita backend/.env con tus credenciales de Firebird" -ForegroundColor Yellow
    notepad .env
}

# Volver a la raíz
Set-Location ..

# Configurar Frontend
Write-Host "`n=== Configurando Frontend ===" -ForegroundColor Yellow
Set-Location frontend

# Instalar dependencias
npm install

# Crear archivo .env.local si no existe
if (-not (Test-Path ".env.local")) {
    "NEXT_PUBLIC_API_URL=http://localhost:8000" | Out-File -FilePath .env.local -Encoding UTF8
}

Set-Location ..

Write-Host "`n=== Configuración completada ===" -ForegroundColor Green
Write-Host "`nPara ejecutar el sistema:" -ForegroundColor Yellow
Write-Host "`nBackend (en una ventana de PowerShell):" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Gray
Write-Host "`nFrontend (en otra ventana de PowerShell):" -ForegroundColor Cyan
Write-Host "  cd frontend" -ForegroundColor Gray
Write-Host "  npm run dev" -ForegroundColor Gray