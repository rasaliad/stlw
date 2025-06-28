@echo off
echo === INFORMACION DEL SISTEMA WINDOWS ===
echo.

echo --- Sistema Operativo ---
wmic os get Caption,Version,OSArchitecture,BuildNumber /format:list

echo.
echo --- Hardware ---
wmic computersystem get Manufacturer,Model,TotalPhysicalMemory,NumberOfProcessors /format:list
wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors /format:list

echo.
echo --- Docker ---
docker version 2>nul || echo Docker no esta instalado
docker-compose version 2>nul || echo Docker Compose no esta instalado

echo.
echo --- Firebird ---
sc query | findstr /i "firebird"
echo.
echo Puerto 3050:
netstat -an | findstr :3050

echo.
echo --- Adaptadores de Red ---
ipconfig /all | findstr /i "IPv4 Ethernet Adapter Description"

echo.
echo --- Espacio en Disco ---
wmic logicaldisk get size,freespace,caption

echo.
echo === FIN DEL REPORTE ===
pause