@echo off
echo ========================================
echo BUSCANDO PYTHON EN EL SISTEMA
echo ========================================
echo.

set PYTHON_FOUND=0
set PYTHON_PATH=

echo [1] Buscando en PATH del sistema...
python --version 2>nul
if %errorlevel%==0 (
    echo [OK] Python encontrado en PATH
    where python
    set PYTHON_FOUND=1
) else (
    echo Python NO esta en el PATH
)
echo.

echo [2] Buscando en ubicaciones comunes...
echo.

REM Buscar en Program Files
echo Verificando C:\Program Files\Python*
for /d %%i in ("C:\Program Files\Python*") do (
    if exist "%%i\python.exe" (
        echo [ENCONTRADO] %%i\python.exe
        "%%i\python.exe" --version
        set PYTHON_PATH=%%i
        set PYTHON_FOUND=1
    )
)

REM Buscar en Program Files (x86)
echo Verificando C:\Program Files (x86)\Python*
for /d %%i in ("C:\Program Files (x86)\Python*") do (
    if exist "%%i\python.exe" (
        echo [ENCONTRADO] %%i\python.exe
        "%%i\python.exe" --version
        set PYTHON_PATH=%%i
        set PYTHON_FOUND=1
    )
)

REM Buscar en C:\ directamente
echo Verificando C:\Python*
for /d %%i in ("C:\Python*") do (
    if exist "%%i\python.exe" (
        echo [ENCONTRADO] %%i\python.exe
        "%%i\python.exe" --version
        set PYTHON_PATH=%%i
        set PYTHON_FOUND=1
    )
)

REM Buscar en AppData Local
echo Verificando %LOCALAPPDATA%\Programs\Python\*
for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%i\python.exe" (
        echo [ENCONTRADO] %%i\python.exe
        "%%i\python.exe" --version
        set PYTHON_PATH=%%i
        set PYTHON_FOUND=1
    )
)

REM Buscar instalaciones de Anaconda/Miniconda
echo Verificando Anaconda/Miniconda...
if exist "%USERPROFILE%\Anaconda3\python.exe" (
    echo [ENCONTRADO] %USERPROFILE%\Anaconda3\python.exe
    "%USERPROFILE%\Anaconda3\python.exe" --version
    set PYTHON_PATH=%USERPROFILE%\Anaconda3
    set PYTHON_FOUND=1
)
if exist "%USERPROFILE%\Miniconda3\python.exe" (
    echo [ENCONTRADO] %USERPROFILE%\Miniconda3\python.exe
    "%USERPROFILE%\Miniconda3\python.exe" --version
    set PYTHON_PATH=%USERPROFILE%\Miniconda3
    set PYTHON_FOUND=1
)

echo.
echo ========================================
echo RESULTADO
echo ========================================
if %PYTHON_FOUND%==1 (
    echo Python SI esta instalado en el sistema
    echo.
    if defined PYTHON_PATH (
        echo Para agregarlo al PATH permanentemente:
        echo 1. Panel de Control - Sistema - Configuracion avanzada
        echo 2. Variables de entorno - PATH - Editar
        echo 3. Agregar: %PYTHON_PATH%
        echo 4. Agregar: %PYTHON_PATH%\Scripts
        echo.
        echo O ejecutar como administrador:
        echo setx /M PATH "%%PATH%%;%PYTHON_PATH%;%PYTHON_PATH%\Scripts"
    )
) else (
    echo Python NO esta instalado en el sistema
    echo.
    echo Descargar desde: https://www.python.org/downloads/
    echo - Elegir Python 3.11 o 3.12
    echo - Marcar "Add Python to PATH" durante instalacion
)
echo.
pause