@echo off
REM Script de despliegue para Windows Server
echo ===================================
echo  Desplegando STL en Windows Server
echo ===================================

REM Configurar rutas (AJUSTA ESTAS RUTAS)
set BACKEND_DIR=C:\ruta\al\backend
set FRONTEND_DIR=C:\ruta\al\frontend
set BACKEND_SERVICE=STL-Backend
set FRONTEND_SERVICE=STL-Frontend

REM Actualizar código
echo [1/5] Actualizando codigo...
git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo actualizar el codigo
    pause
    exit /b 1
)

REM Backend
echo [2/5] Actualizando Backend...
cd %BACKEND_DIR%
pip install -r requirements.txt

echo [3/5] Reiniciando servicio Backend...
net stop "%BACKEND_SERVICE%" 2>nul
net start "%BACKEND_SERVICE%"
if %ERRORLEVEL% NEQ 0 (
    echo ADVERTENCIA: No se pudo reiniciar el servicio backend
    echo Intenta reiniciarlo manualmente
)

REM Frontend
echo [4/5] Actualizando Frontend...
cd %FRONTEND_DIR%
call npm install
call npm run build

echo [5/5] Reiniciando servicio Frontend...
net stop "%FRONTEND_SERVICE%" 2>nul
net start "%FRONTEND_SERVICE%"
if %ERRORLEVEL% NEQ 0 (
    echo ADVERTENCIA: No se pudo reiniciar el servicio frontend
    echo Intenta reiniciarlo manualmente
)

echo ===================================
echo  Despliegue completado
echo ===================================
pause