# Instalación en Windows Server

## Prerequisitos

1. **Windows Server 2016/2019/2022** o **Windows 10/11 Pro**
2. **Docker Desktop para Windows** instalado
3. **Git para Windows** instalado
4. **Firebird 2.5** instalado y ejecutándose en puerto 3050
5. **PowerShell 5.0+** (incluido en Windows)

## Instalación Rápida

1. **Abrir PowerShell como Administrador**
   - Click derecho en PowerShell → "Ejecutar como administrador"

2. **Ejecutar el script de instalación**
   ```powershell
   # Descargar el proyecto
   git clone https://github.com/rasaliad/stlw.git
   cd stlw
   
   # Ejecutar instalador
   .\install-windows.ps1
   ```

## Instalación Manual

### 1. Clonar el repositorio
```powershell
git clone https://github.com/rasaliad/stlw.git
cd stlw
```

### 2. Configurar variables de entorno
```powershell
# Copiar archivo de ejemplo
Copy-Item .env.windows.example .env

# Editar con notepad
notepad .env
```

Configurar en `.env`:
```env
# Ruta de la base de datos (usar / o \\)
FIREBIRD_DATABASE=C:/App/STL/Datos/DATOS_STL.FDB
# o
FIREBIRD_DATABASE=C:\\App\\STL\\Datos\\DATOS_STL.FDB

FIREBIRD_USER=sysdba
FIREBIRD_PASSWORD=tu_password
SECRET_KEY=genera-una-clave-segura-de-32-caracteres
```

### 3. Configurar Firewall (como Administrador)
```powershell
# Permitir puertos
New-NetFirewallRule -DisplayName "STL Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "STL Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

### 4. Ejecutar con Docker
```powershell
# Construir y ejecutar
docker-compose -f docker-compose.windows.yml up -d --build

# Ver logs
docker-compose -f docker-compose.windows.yml logs -f
```

## Verificar la Instalación

1. **Backend API**: http://localhost:8000/health
2. **Frontend**: http://localhost:3000
3. **Documentación API**: http://localhost:8000/docs

## Comandos Útiles

```powershell
# Ver estado de los contenedores
docker-compose -f docker-compose.windows.yml ps

# Ver logs en tiempo real
docker-compose -f docker-compose.windows.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose.windows.yml logs -f backend
docker-compose -f docker-compose.windows.yml logs -f frontend

# Reiniciar servicios
docker-compose -f docker-compose.windows.yml restart

# Detener servicios
docker-compose -f docker-compose.windows.yml down

# Actualizar desde GitHub
git pull origin main
docker-compose -f docker-compose.windows.yml up -d --build
```

## Solución de Problemas

### Docker Desktop no inicia
- Asegúrate de tener virtualización habilitada en BIOS
- Verifica que Hyper-V esté habilitado
- Reinicia Docker Desktop

### Error de conexión a Firebird
- Verifica que Firebird esté ejecutándose: `Get-Service Firebird*`
- Verifica el puerto: `netstat -an | findstr :3050`
- Asegúrate de usar `host.docker.internal` en Docker

### Puertos ocupados
```powershell
# Ver qué proceso usa un puerto
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Matar proceso por PID
taskkill /PID <numero_pid> /F
```

### Permisos de PowerShell
Si no puedes ejecutar scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Información del Sistema

Para obtener información del sistema Windows:
```powershell
# Ejecutar script de información
.\get-windows-info.ps1

# O el archivo .bat
get-windows-info.bat
```