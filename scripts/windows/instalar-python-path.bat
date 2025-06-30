@echo off
echo ========================================
echo CONFIGURAR PYTHON EN PATH
echo ========================================
echo.
echo NOTA: Este script debe ejecutarse como ADMINISTRADOR
echo.

REM Buscar Python primero
set PYTHON_PATH=
set PYTHON_FOUND=0

REM Verificar ubicaciones comunes
for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%i\python.exe" (
        set PYTHON_PATH=%%i
        set PYTHON_FOUND=1
    )
)

for /d %%i in ("C:\Python*") do (
    if exist "%%i\python.exe" (
        set PYTHON_PATH=%%i
        set PYTHON_FOUND=1
    )
)

for /d %%i in ("C:\Program Files\Python*") do (
    if exist "%%i\python.exe" (
        set PYTHON_PATH=%%i
        set PYTHON_FOUND=1
    )
)

if %PYTHON_FOUND%==0 (
    echo [ERROR] No se encontro Python instalado
    echo.
    echo Instale Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado en: %PYTHON_PATH%
echo.
echo Agregando al PATH del sistema...

REM Agregar Python al PATH del sistema
setx /M PATH "%PATH%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts" 2>nul
if %errorlevel%==0 (
    echo [OK] PATH actualizado correctamente
) else (
    echo [ERROR] No se pudo actualizar el PATH
    echo         Ejecute este script como Administrador
    echo.
    echo Alternativamente, agregue manualmente:
    echo   %PYTHON_PATH%
    echo   %PYTHON_PATH%\Scripts
    echo Al PATH del sistema en Variables de Entorno
)

echo.
echo Verificando instalacion...
"%PYTHON_PATH%\python.exe" --version
"%PYTHON_PATH%\Scripts\pip.exe" --version

echo.
echo IMPORTANTE: Cierre y vuelva a abrir la ventana de comandos
echo            para que los cambios tengan efecto
echo.
pause