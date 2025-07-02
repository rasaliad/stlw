@echo off
REM Crear paquete de archivos modificados para deploy manual

echo Creando paquete de deployment...

REM Crear carpeta temporal
mkdir deploy-package 2>nul
mkdir deploy-package\backend\app\api\endpoints 2>nul
mkdir deploy-package\frontend\src\app\stl\despachos 2>nul
mkdir deploy-package\frontend\src\components\ui 2>nul

REM Copiar archivos modificados
echo Copiando archivos backend...
copy backend\app\api\endpoints\stl_pedidos.py deploy-package\backend\app\api\endpoints\

echo Copiando archivos frontend...
copy frontend\src\app\stl\despachos\page.tsx deploy-package\frontend\src\app\stl\despachos\
copy frontend\src\components\ui\select.tsx deploy-package\frontend\src\components\ui\
copy frontend\package.json deploy-package\frontend\

REM Crear README
echo Archivos modificados: > deploy-package\README.txt
echo. >> deploy-package\README.txt
echo Backend: >> deploy-package\README.txt
echo - app\api\endpoints\stl_pedidos.py (linea 124: agregado .strip() para limpiar espacios) >> deploy-package\README.txt
echo. >> deploy-package\README.txt
echo Frontend: >> deploy-package\README.txt
echo - src\app\stl\despachos\page.tsx (nuevo dropdown con flujo de estados) >> deploy-package\README.txt
echo - src\components\ui\select.tsx (nuevo componente) >> deploy-package\README.txt
echo - package.json (ya incluye @radix-ui/react-select) >> deploy-package\README.txt
echo. >> deploy-package\README.txt
echo IMPORTANTE: Ejecutar 'npm install' en frontend despues de copiar >> deploy-package\README.txt

REM Comprimir (requiere PowerShell)
powershell Compress-Archive -Path deploy-package\* -DestinationPath deploy-stl-%date:~-4%%date:~-10,2%%date:~-7,2%.zip -Force

echo.
echo Paquete creado: deploy-stl-%date:~-4%%date:~-10,2%%date:~-7,2%.zip
echo.
pause