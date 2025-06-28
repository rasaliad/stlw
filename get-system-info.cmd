@echo off
echo === INFORMACION DEL SISTEMA WINDOWS ===
echo.

echo --- Sistema Operativo ---
systeminfo | findstr /B /C:"Nombre del sistema operativo" /C:"Version" /C:"Tipo de sistema"

echo.
echo --- Docker ---
docker version
docker-compose version

echo.
echo --- Firebird ---
sc query | findstr /i "firebird"
echo.
echo Puerto 3050:
netstat -an | findstr :3050

echo.
echo --- Direcciones IP ---
ipconfig | findstr /i "IPv4"

echo.
echo --- Espacio en Disco ---
wmic logicaldisk get size,freespace,caption

echo.
echo === FIN DEL REPORTE ===
pause