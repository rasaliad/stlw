@echo off
echo ========================================
echo VERIFICACION DE REQUISITOS STL
echo ========================================
echo.

set PYTHON_OK=0
set NODE_OK=0
set FIREBIRD_OK=0
set GIT_OK=0
set ERRORS=0

echo [1] Verificando Python...
python --version >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    echo [OK] Python instalado - Version: %PYTHON_VER%
    
    REM Verificar si es Python 3.11 o superior
    for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VER%") do (
        if %%a GEQ 3 if %%b GEQ 11 (
            echo      Version compatible
            set PYTHON_OK=1
        ) else (
            echo      [ADVERTENCIA] Se recomienda Python 3.11 o superior
            set PYTHON_OK=1
        )
    )
) else (
    echo [ERROR] Python NO instalado
    echo        Descargar desde: https://www.python.org/downloads/
    set /a ERRORS+=1
)
echo.

echo [2] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=1 delims=v" %%i in ('node --version') do set NODE_VER=%%i
    echo [OK] Node.js instalado - Version: v%NODE_VER%
    
    REM Verificar si es Node 16 o superior
    for /f "tokens=1 delims=." %%a in ("%NODE_VER%") do (
        if %%a GEQ 16 (
            echo      Version compatible
            set NODE_OK=1
        ) else (
            echo      [ADVERTENCIA] Se recomienda Node.js 16 o superior
            set NODE_OK=1
        )
    )
) else (
    echo [ERROR] Node.js NO instalado
    echo        Descargar desde: https://nodejs.org/
    set /a ERRORS+=1
)
echo.

echo [3] Verificando Git...
git --version >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Git instalado
    git --version
    set GIT_OK=1
) else (
    echo [ERROR] Git NO instalado
    echo        Descargar desde: https://git-scm.com/download/win
    set /a ERRORS+=1
)
echo.

echo [4] Verificando Firebird...
set FIREBIRD_FOUND=0
if exist "C:\Program Files\Firebird\Firebird_2_5\bin\fbclient.dll" (
    echo [OK] Firebird 2.5 encontrado en Program Files
    set FIREBIRD_OK=1
    set FIREBIRD_FOUND=1
)
if exist "C:\Program Files (x86)\Firebird\Firebird_2_5\bin\fbclient.dll" (
    echo [OK] Firebird 2.5 encontrado en Program Files (x86)
    set FIREBIRD_OK=1
    set FIREBIRD_FOUND=1
)
if %FIREBIRD_FOUND%==0 (
    echo [ADVERTENCIA] Firebird 2.5 no encontrado en rutas estandar
    echo               Verificar instalacion manual
)
echo.

echo [5] Verificando puertos disponibles...
netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo [ADVERTENCIA] Puerto 8000 en uso (Backend)
    set /a ERRORS+=1
) else (
    echo [OK] Puerto 8000 disponible (Backend)
)

netstat -an | findstr :3000 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo [ADVERTENCIA] Puerto 3000 en uso (Frontend)
    set /a ERRORS+=1
) else (
    echo [OK] Puerto 3000 disponible (Frontend)
)
echo.

echo [6] Verificando herramientas adicionales...
where nssm >nul 2>&1
if %errorlevel%==0 (
    echo [OK] NSSM instalado (para servicios)
) else (
    echo [INFO] NSSM no instalado - Necesario para crear servicios
    echo        Descargar desde: https://nssm.cc/download
)
echo.

echo ========================================
echo RESULTADO DE VERIFICACION
echo ========================================
if %PYTHON_OK%==1 if %NODE_OK%==1 if %GIT_OK%==1 if %ERRORS%==0 (
    echo [EXITOSO] Sistema listo para instalar STL
    echo.
    echo Siguiente paso: Clonar repositorio y seguir INSTALACION_WINDOWS.md
) else (
    echo [ATENCION] Revisar los puntos marcados arriba
    if %ERRORS% GTR 0 echo            Errores encontrados: %ERRORS%
)
echo.
pause