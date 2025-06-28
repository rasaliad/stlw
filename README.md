# STL Fullstack Application

Aplicación fullstack moderna con Docker que se conecta a Firebird 2.5 existente en Windows.

## Arquitectura

- **Backend**: FastAPI (Python 3.12) con conexión a Firebird 2.5
- **Frontend**: Next.js 14 con TypeScript, Tailwind CSS y shadcn/ui
- **Base de Datos**: Firebird 2.5 (existente en Windows, NO en Docker)
- **Containerización**: Docker y Docker Compose

## Características

### Backend (FastAPI)
- ✅ Conexión a Firebird 2.5 usando firebird-driver
- ✅ Autenticación JWT
- ✅ CORS configurado
- ✅ Endpoints CRUD para usuarios
- ✅ Manejo de errores y validaciones
- ✅ Documentación automática con Swagger

### Frontend (Next.js 14)
- ✅ TypeScript para type safety
- ✅ Tailwind CSS + shadcn/ui para componentes
- ✅ Tema claro/oscuro
- ✅ Dashboard responsive
- ✅ Tabla de usuarios con filtros
- ✅ Autenticación con JWT
- ✅ Manejo de estados y errores

### Docker
- ✅ Configuración para desarrollo con hot reload
- ✅ Healthchecks para ambos servicios
- ✅ Conexión a Firebird Windows via host.docker.internal
- ✅ Variables de entorno configurables

## Prerequisitos

1. **Firebird 2.5** instalado en Windows en puerto 3050
2. **Docker** y **Docker Compose** instalados
3. Base de datos en `C:\\App\\STL\\Datos\\DATOS_STL.FDB`

## Configuración Inicial

### 1. Crear tabla de usuarios en Firebird

Conectar a tu base de datos Firebird y ejecutar:

```sql
CREATE TABLE USERS (
    ID INTEGER NOT NULL PRIMARY KEY,
    USERNAME VARCHAR(50) NOT NULL UNIQUE,
    EMAIL VARCHAR(100) NOT NULL,
    HASHED_PASSWORD VARCHAR(255) NOT NULL,
    IS_ACTIVE SMALLINT DEFAULT 1,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE GENERATOR GEN_USERS_ID;
SET GENERATOR GEN_USERS_ID TO 0;

SET TERM ^ ;
CREATE TRIGGER USERS_BI FOR USERS
ACTIVE BEFORE INSERT POSITION 0
AS
BEGIN
  IF (NEW.ID IS NULL) THEN
    NEW.ID = GEN_ID(GEN_USERS_ID,1);
END^
SET TERM ; ^
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales de Firebird:

```env
FIREBIRD_USER=tu_usuario
FIREBIRD_PASSWORD=tu_password
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
```

## Instalación y Ejecución

### Desarrollo con Docker

```bash
# Clonar y entrar al proyecto
git clone <repo>
cd stl-fullstack

# Construir y levantar servicios
docker-compose up --build

# O en segundo plano
docker-compose up -d --build
```

### URLs de Desarrollo

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Health Check Backend**: http://localhost:8000/health

### Desarrollo Local (sin Docker)

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Estructura del Proyecto

```
stl-fullstack/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py      # Autenticación
│   │   │   │   └── users.py     # CRUD usuarios
│   │   │   └── routes.py        # Router principal
│   │   ├── core/
│   │   │   ├── config.py        # Configuración
│   │   │   ├── database.py      # Conexión Firebird
│   │   │   └── security.py      # JWT y passwords
│   │   ├── models/
│   │   │   └── user.py          # Modelo Usuario
│   │   ├── schemas/
│   │   │   └── user.py          # Schemas Pydantic
│   │   ├── services/
│   │   │   └── user_service.py  # Lógica de negocio
│   │   └── main.py              # App principal
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/              # Componentes shadcn/ui
│   │   │   ├── dashboard.tsx
│   │   │   ├── login-form.tsx
│   │   │   ├── theme-provider.tsx
│   │   │   ├── theme-toggle.tsx
│   │   │   └── user-table.tsx
│   │   ├── lib/
│   │   │   ├── api.ts           # Cliente HTTP
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── user.ts
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Login de usuario
- `GET /api/v1/auth/me` - Obtener usuario actual

### Usuarios  
- `GET /api/v1/users/` - Listar usuarios (paginado)
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/{id}` - Obtener usuario por ID
- `PUT /api/v1/users/{id}` - Actualizar usuario
- `DELETE /api/v1/users/{id}` - Eliminar usuario

## Configuración de Red

### Desde Docker a Firebird Windows
- Host: `host.docker.internal`
- Puerto: `3050`

### Desde WSL a Firebird Windows  
- Host: `172.19.176.1` (o la IP de tu adaptador vEthernet)
- Puerto: `3050`

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Reconstruir un servicio específico
docker-compose up --build backend

# Ejecutar comando en contenedor
docker-compose exec backend bash
docker-compose exec frontend sh

# Parar servicios
docker-compose down

# Limpiar todo
docker-compose down -v --remove-orphans
```

## Credenciales por Defecto

Crear un usuario inicial directamente en Firebird:

```sql
INSERT INTO USERS (USERNAME, EMAIL, HASHED_PASSWORD, IS_ACTIVE) 
VALUES ('admin', 'admin@stl.com', '$2b$12$ejemplo_hash_bcrypt', 1);
```

O usar el endpoint de registro desde la API.

## Solución de Problemas

### Error de conexión a Firebird
1. Verificar que Firebird esté corriendo en puerto 3050
2. Verificar firewall de Windows
3. Comprobar que la ruta de la base de datos sea correcta
4. Verificar credenciales en `.env`

### Problemas con Docker
1. Verificar que Docker Desktop esté corriendo
2. Limpiar caché: `docker system prune -a`
3. Verificar puertos disponibles (3000, 8000)

### Hot Reload no funciona
1. Verificar volúmenes en docker-compose.yml
2. Reiniciar servicios: `docker-compose restart`

## Instalación en Servidor de Producción

### Prerequisitos del Servidor
1. Docker y Docker Compose instalados
2. Firebird 2.5 instalado localmente
3. Git instalado
4. Puerto 3000 y 8000 disponibles

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo

# 2. Configurar variables de entorno
cp .env.server.example .env
# Editar .env con las credenciales correctas del servidor

# 3. Construir y ejecutar con Docker
docker-compose -f docker-compose.server.yml up -d --build

# 4. Ver logs
docker-compose -f docker-compose.server.yml logs -f

# 5. Detener servicios
docker-compose -f docker-compose.server.yml down
```

### Actualización del Código

```bash
# Actualizar desde GitHub
git pull origin main

# Reconstruir y reiniciar servicios
docker-compose -f docker-compose.server.yml up -d --build
```

## Próximos Pasos

- [ ] Implementar integración con API SAP-STL
- [ ] Crear sincronización de datos
- [ ] Implementar más entidades del dominio
- [ ] Agregar tests unitarios y de integración  
- [ ] Implementar paginación en frontend
- [ ] Agregar gráficos con Recharts
- [ ] Configurar CI/CD
- [ ] Implementar logging avanzado
- [ ] Agregar validaciones de formularios
- [ ] Implementar roles y permisos