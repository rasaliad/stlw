@echo off
echo Deteniendo servicios...
nssm stop STL-Frontend
nssm stop STL-Backend

echo Resolviendo conflictos de git...
del scripts\windows\deploy-windows.bat 2>nul
git reset --hard HEAD
git clean -fd

echo Actualizando codigo...
git pull origin main

echo Instalando dependencias del frontend...
cd frontend
if not exist package.json (
    echo ERROR: No se encuentra package.json en frontend
    pause
    exit /b 1
)
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudieron instalar las dependencias del frontend
    pause
    exit /b 1
)

echo Reconstruyendo frontend...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo construir el frontend
    pause
    exit /b 1
)
cd ..

echo Instalando dependencias del backend...
cd backend
if not exist requirements.txt (
    echo ERROR: No se encuentra requirements.txt en backend
    pause
    exit /b 1
)
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudieron instalar las dependencias del backend
    pause
    exit /b 1
)
cd ..

echo Reiniciando servicios...
nssm start STL-Backend
timeout /t 10
nssm start STL-Frontend

echo.
echo ===================================
echo  DEPLOY COMPLETADO EXITOSAMENTE
echo ===================================
echo.
echo IMPORTANTE: Ejecuta este SQL en Firebird (solo la primera vez):
echo INPUT 'C:\App\stlw\backend\sql\add_delivery_notes_sync_config.sql';
echo.
echo Nuevas funcionalidades disponibles:
echo - Dropdown de cambio de estatus en STL Despachos
echo - Envio automatico de pedidos a SAP cada 5 minutos
echo - Endpoints: /api/v1/sap/delivery/...
echo.
pause