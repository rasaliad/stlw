# Script para instalar Docker en Windows Server 2019
# Ejecutar como Administrador

Write-Host "=== Instalando Docker en Windows Server 2019 ===" -ForegroundColor Green

# Instalar el módulo Docker-Microsoft PackageManagement Provider
Install-Module -Name DockerMsftProvider -Repository PSGallery -Force

# Instalar el paquete Docker
Install-Package -Name docker -ProviderName DockerMsftProvider -Force

# Reiniciar el servidor (necesario)
Write-Host "`nDocker instalado. Es necesario reiniciar el servidor." -ForegroundColor Yellow
$response = Read-Host "¿Deseas reiniciar ahora? (S/N)"
if ($response -eq 'S' -or $response -eq 's') {
    Restart-Computer -Force
}