# Script PowerShell para obtener información del sistema Windows

Write-Host "=== INFORMACIÓN DEL SISTEMA WINDOWS ===" -ForegroundColor Green

# Sistema Operativo
Write-Host "`n--- Sistema Operativo ---" -ForegroundColor Yellow
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture, BuildNumber

# Hardware
Write-Host "`n--- Hardware ---" -ForegroundColor Yellow
Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, TotalPhysicalMemory, NumberOfProcessors
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors

# Docker Desktop
Write-Host "`n--- Docker ---" -ForegroundColor Yellow
try {
    docker version
    docker-compose version
} catch {
    Write-Host "Docker no está instalado o no está en el PATH" -ForegroundColor Red
}

# WSL
Write-Host "`n--- WSL ---" -ForegroundColor Yellow
try {
    wsl --list --verbose
} catch {
    Write-Host "WSL no está instalado" -ForegroundColor Red
}

# Firebird
Write-Host "`n--- Firebird ---" -ForegroundColor Yellow
$firebirdService = Get-Service -Name "Firebird*" -ErrorAction SilentlyContinue
if ($firebirdService) {
    $firebirdService | Select-Object Name, Status, DisplayName
} else {
    Write-Host "Servicio Firebird no encontrado" -ForegroundColor Red
}

# Verificar puerto 3050
Write-Host "`n--- Puerto Firebird (3050) ---" -ForegroundColor Yellow
netstat -an | findstr :3050

# Variables de entorno relevantes
Write-Host "`n--- Variables de Entorno ---" -ForegroundColor Yellow
Get-ChildItem Env: | Where-Object { $_.Name -match "FIREBIRD|PATH" }

# Adaptadores de red
Write-Host "`n--- Adaptadores de Red ---" -ForegroundColor Yellow
Get-NetIPAddress | Where-Object { $_.AddressFamily -eq 'IPv4' -and $_.IPAddress -ne '127.0.0.1' } | Select-Object InterfaceAlias, IPAddress

# Firewall para Docker
Write-Host "`n--- Reglas de Firewall para puertos 3000, 8000 ---" -ForegroundColor Yellow
Get-NetFirewallPortFilter | Where-Object { $_.LocalPort -in @(3000, 8000, 3050) } | Select-Object Protocol, LocalPort

# Espacio en disco
Write-Host "`n--- Espacio en Disco ---" -ForegroundColor Yellow
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name="Used(GB)";Expression={[math]::Round($_.Used/1GB,2)}}, @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}}, @{Name="Total(GB)";Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}}

Write-Host "`n=== FIN DEL REPORTE ===" -ForegroundColor Green