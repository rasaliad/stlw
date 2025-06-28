# Script PowerShell para obtener información del sistema Windows

Write-Host "=== INFORMACION DEL SISTEMA WINDOWS ===" -ForegroundColor Green

# Sistema Operativo
Write-Host "`n--- Sistema Operativo ---" -ForegroundColor Yellow
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture, BuildNumber

# Hardware
Write-Host "`n--- Hardware ---" -ForegroundColor Yellow
Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, TotalPhysicalMemory, NumberOfProcessors

# Docker Desktop
Write-Host "`n--- Docker ---" -ForegroundColor Yellow
docker version 2>&1
docker-compose version 2>&1

# Firebird
Write-Host "`n--- Firebird ---" -ForegroundColor Yellow
Get-Service -Name "Firebird*" -ErrorAction SilentlyContinue

# Puerto 3050
Write-Host "`n--- Puerto Firebird (3050) ---" -ForegroundColor Yellow
netstat -an | findstr :3050

# Adaptadores de red
Write-Host "`n--- Adaptadores de Red ---" -ForegroundColor Yellow
Get-NetIPAddress | Where-Object { $_.AddressFamily -eq 'IPv4' } | Select-Object InterfaceAlias, IPAddress

# Espacio en disco
Write-Host "`n--- Espacio en Disco ---" -ForegroundColor Yellow
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free

Write-Host "`n=== FIN DEL REPORTE ===" -ForegroundColor Green