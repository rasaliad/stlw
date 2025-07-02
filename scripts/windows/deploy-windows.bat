@echo off
echo Deteniendo servicios...
nssm stop STL-Frontend
nssm stop STL-Backend

echo Actualizando codigo...
git pull origin main

echo Instalando dependencias del frontend...
cd frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudieron instalar las dependencias
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
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudieron instalar las dependencias del backend
    pause
    exit /b 1
)
cd ..

echo Reiniciando servicios...
nssm start STL-Backend
timeout /t 5
nssm start STL-Frontend

echo Deploy completado!
echo.
echo IMPORTANTE: Ejecuta este SQL en Firebird (solo la primera vez):
echo INPUT backend\sql\add_delivery_notes_sync_config.sql;
echo.
pause