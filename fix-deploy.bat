@echo off
echo Resolviendo conflictos y actualizando...

REM Eliminar archivos conflictivos
del scripts\windows\deploy-windows.bat 2>nul

REM Forzar actualizacion
git stash
git pull origin main

REM Verificar que tenemos el nuevo script
if exist deploy-windows-server.bat (
    echo Ejecutando deploy corregido...
    call deploy-windows-server.bat
) else (
    echo ERROR: No se encontro deploy-windows-server.bat
    echo Intenta: git pull origin main
    pause
)