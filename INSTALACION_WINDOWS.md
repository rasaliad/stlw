# Guía de Instalación STL en Windows Server (Sin Docker)

## Requisitos Previos

### Software Requerido
- Windows Server 2016 o superior
- Python 3.12
- Node.js 18 LTS
- Firebird 2.5 (ya debe estar instalado)
- Git para Windows

### Puertos Necesarios
- 3000: Frontend (Next.js)
- 8000: Backend (FastAPI)
- 3050: Firebird (por defecto)

## 1. Instalación de Python 3.12

### Si Python NO está instalado:
1. Descargar Python 3.12 desde https://www.python.org/downloads/
2. Durante la instalación:
   - ✅ Marcar "Add Python to PATH" (MUY IMPORTANTE)
   - ✅ Marcar "Install for all users"
3. Verificar instalación:
   ```cmd
   python --version
   pip --version
   ```

### Si Python está instalado pero no en PATH:
1. Ejecutar `scripts\windows\buscar-python.bat` para encontrarlo
2. Ejecutar como Administrador `scripts\windows\instalar-python-path.bat`
3. Cerrar y abrir nueva ventana de comandos
4. Verificar con `python --version`

## 2. Instalación de Node.js 18

1. Descargar Node.js 18 LTS desde https://nodejs.org/
2. Instalar con opciones por defecto
3. Verificar instalación:
   ```cmd
   node --version
   npm --version
   ```

## 3. Clonar el Proyecto

```cmd
cd C:\
git clone https://github.com/tu-usuario/stlw.git
cd stlw
```

## 4. Configuración del Backend

### 4.1 Crear entorno virtual
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
```

### 4.2 Instalar dependencias
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Configurar variables de entorno
Crear archivo `backend\.env`:
```env
# Base de datos Firebird
FIREBIRD_HOST=localhost
FIREBIRD_DATABASE=C:/path/to/your/database.fdb
FIREBIRD_USER=SYSDBA
FIREBIRD_PASSWORD=masterkey
FIREBIRD_CHARSET=WIN1252

# API
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_HOSTS=["http://localhost:3000","http://NOMBRE-SERVIDOR:3000"]

# Zona horaria
TZ=America/Santo_Domingo
```

### 4.4 Probar el backend
```cmd
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Verificar en: http://localhost:8000/docs

## 5. Configuración del Frontend

### 5.1 Instalar dependencias
```cmd
cd ..\frontend
npm install
```

### 5.2 Configurar variables de entorno
Crear archivo `frontend\.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 5.3 Construir para producción
```cmd
npm run build
```

### 5.4 Probar el frontend
```cmd
npm start
```
Verificar en: http://localhost:3000

## 6. Configurar como Servicios de Windows

### 6.1 Instalar NSSM (Non-Sucking Service Manager)
1. Descargar NSSM desde https://nssm.cc/download
2. Extraer en `C:\nssm`
3. Agregar `C:\nssm\win64` al PATH del sistema

### 6.2 Crear servicio para Backend
```cmd
cd C:\stlw\backend
venv\Scripts\activate
pip install pywin32

nssm install STL-Backend
```
En la ventana de NSSM:
- Path: `C:\stlw\backend\venv\Scripts\python.exe`
- Startup directory: `C:\stlw\backend`
- Arguments: `-m uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 6.3 Crear servicio para Frontend
```cmd
nssm install STL-Frontend
```
En la ventana de NSSM:
- Path: `C:\Program Files\nodejs\node.exe`
- Startup directory: `C:\stlw\frontend`
- Arguments: `node_modules\next\dist\bin\next start -p 3000`

### 6.4 Iniciar servicios
```cmd
nssm start STL-Backend
nssm start STL-Frontend
```

## 7. Scripts de Mantenimiento

### 7.1 Crear `C:\stlw\scripts\start-stl.bat`
```batch
@echo off
echo Iniciando STL Sistema...
net start STL-Backend
timeout /t 5
net start STL-Frontend
echo STL Sistema iniciado.
pause
```

### 7.2 Crear `C:\stlw\scripts\stop-stl.bat`
```batch
@echo off
echo Deteniendo STL Sistema...
net stop STL-Frontend
net stop STL-Backend
echo STL Sistema detenido.
pause
```

### 7.3 Crear `C:\stlw\scripts\restart-stl.bat`
```batch
@echo off
echo Reiniciando STL Sistema...
net stop STL-Frontend
net stop STL-Backend
timeout /t 3
net start STL-Backend
timeout /t 5
net start STL-Frontend
echo STL Sistema reiniciado.
pause
```

### 7.4 Crear `C:\stlw\scripts\update-stl.bat`
```batch
@echo off
echo Actualizando STL Sistema...

REM Detener servicios
net stop STL-Frontend
net stop STL-Backend

REM Actualizar código
cd C:\stlw
git pull

REM Backend
cd backend
venv\Scripts\activate
pip install -r requirements.txt

REM Frontend
cd ..\frontend
npm install
npm run build

REM Reiniciar servicios
net start STL-Backend
timeout /t 5
net start STL-Frontend

echo Actualización completada.
pause
```

## 8. Configuración del Firewall

Abrir puertos en Windows Firewall:
```cmd
netsh advfirewall firewall add rule name="STL Backend" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="STL Frontend" dir=in action=allow protocol=TCP localport=3000
```

## 9. Acceso al Sistema

- Frontend: http://NOMBRE-SERVIDOR:3000
- Backend API: http://NOMBRE-SERVIDOR:8000/docs
- Usuario inicial: admin / admin123

## 10. Solución de Problemas

### Error: "Module not found"
```cmd
cd C:\stlw\backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Port already in use"
```cmd
netstat -ano | findstr :8000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Logs de servicios
```cmd
nssm status STL-Backend
nssm status STL-Frontend
```

### Reinstalar servicio
```cmd
nssm remove STL-Backend confirm
nssm remove STL-Frontend confirm
```

## 11. Backup y Restauración

### Backup de configuración
```batch
xcopy C:\stlw\backend\.env C:\backup\stl\ /Y
xcopy C:\stlw\frontend\.env.local C:\backup\stl\ /Y
```

### Tareas programadas
Usar el Programador de Tareas de Windows para:
- Backup diario de archivos .env
- Reinicio automático de servicios si fallan
- Limpieza de logs antiguos