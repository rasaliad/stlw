@echo off
echo ========================================
echo DIAGNOSTICO STL - ESTADO DEL SISTEMA
echo ========================================
echo.

echo [1] VERSIONES INSTALADAS:
echo -------------------------
python --version 2>nul || echo Python NO ENCONTRADO
node --version 2>nul || echo Node.js NO ENCONTRADO
npm --version 2>nul || echo NPM NO ENCONTRADO
git --version 2>nul || echo Git NO ENCONTRADO
echo.

echo [2] SERVICIOS STL:
echo ------------------
sc query STL-Backend 2>nul || echo Servicio STL-Backend NO EXISTE
sc query STL-Frontend 2>nul || echo Servicio STL-Frontend NO EXISTE
echo.

echo [3] PUERTOS EN USO:
echo -------------------
echo Puerto 8000 (Backend):
netstat -ano | findstr :8000
echo.
echo Puerto 3000 (Frontend):
netstat -ano | findstr :3000
echo.

echo [4] DIRECTORIOS STL:
echo --------------------
if exist C:\stlw echo Encontrado: C:\stlw
if exist C:\stl echo Encontrado: C:\stl
if exist %USERPROFILE%\stlw echo Encontrado: %USERPROFILE%\stlw
if exist D:\stlw echo Encontrado: D:\stlw
if exist D:\stl echo Encontrado: D:\stl
echo.

echo [5] PROCESOS PYTHON/NODE:
echo ------------------------
echo Procesos Python:
tasklist | findstr python
echo.
echo Procesos Node:
tasklist | findstr node
echo.

echo [6] VARIABLES DE ENTORNO STL:
echo -----------------------------
echo FIREBIRD_HOST=%FIREBIRD_HOST%
echo FIREBIRD_DATABASE=%FIREBIRD_DATABASE%
echo FIREBIRD_USER=%FIREBIRD_USER%
echo.

echo [7] ARCHIVOS DE CONFIGURACION:
echo ------------------------------
if exist C:\stlw\backend\.env echo Encontrado: C:\stlw\backend\.env
if exist C:\stlw\frontend\.env.local echo Encontrado: C:\stlw\frontend\.env.local
echo.

pause