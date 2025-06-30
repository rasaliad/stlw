@echo off
echo ========================================
echo LIMPIEZA COMPLETA DE STL
echo ========================================
echo.
echo ADVERTENCIA: Esto eliminara toda la instalacion anterior
echo Presione Ctrl+C para cancelar o cualquier tecla para continuar
echo.
pause

echo [1] Deteniendo servicios...
net stop STL-Backend 2>nul
net stop STL-Frontend 2>nul
timeout /t 3

echo [2] Eliminando servicios Windows...
echo Eliminando con NSSM...
nssm remove STL-Backend confirm 2>nul
nssm remove STL-Frontend confirm 2>nul
echo Eliminando con SC...
sc delete STL-Backend 2>nul
sc delete STL-Frontend 2>nul
timeout /t 2

echo [3] Matando procesos...
echo Terminando procesos Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo Terminando procesos Node...
taskkill /F /IM node.exe 2>nul
timeout /t 2

echo [4] Eliminando directorios...
echo Eliminando C:\stlw...
rmdir /S /Q C:\stlw 2>nul
echo Eliminando C:\stl...
rmdir /S /Q C:\stl 2>nul
echo Eliminando %USERPROFILE%\stlw...
rmdir /S /Q %USERPROFILE%\stlw 2>nul
echo Eliminando D:\stlw...
rmdir /S /Q D:\stlw 2>nul
echo Eliminando D:\stl...
rmdir /S /Q D:\stl 2>nul

echo [5] Limpiando reglas de firewall...
netsh advfirewall firewall delete rule name="STL Backend" 2>nul
netsh advfirewall firewall delete rule name="STL Frontend" 2>nul
netsh advfirewall firewall delete rule name="STL-Backend" 2>nul
netsh advfirewall firewall delete rule name="STL-Frontend" 2>nul

echo [6] Limpiando tareas programadas...
schtasks /delete /tn "STL Backup" /f 2>nul
schtasks /delete /tn "STL Restart" /f 2>nul
schtasks /delete /tn "STL-Backup" /f 2>nul
schtasks /delete /tn "STL-Restart" /f 2>nul

echo [7] Limpiando variables de entorno del usuario...
setx FIREBIRD_HOST "" 2>nul
setx FIREBIRD_DATABASE "" 2>nul
setx FIREBIRD_USER "" 2>nul
setx FIREBIRD_PASSWORD "" 2>nul

echo.
echo ========================================
echo LIMPIEZA COMPLETADA
echo ========================================
echo.
echo Recomendaciones:
echo - Reiniciar el servidor para limpiar completamente
echo - Verificar manualmente si quedan archivos en otras ubicaciones
echo - Ejecutar diagnostico-stl.bat para confirmar limpieza
echo.
pause