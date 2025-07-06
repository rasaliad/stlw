# Contexto del Proyecto STL Warehouse Management System

## 🏭 Descripción General
Sistema de gestión de almacén fullstack que integra una aplicación web moderna con el API de SAP-STL para sincronización de datos entre Firebird 2.5 y SAP Business One.

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: FastAPI (Python)
- **Base de Datos**: Firebird 2.5 (Windows)
- **Autenticación**: JWT
- **ORM**: SQLAlchemy con driver fdb
- **Sincronización**: APScheduler para tareas automáticas
- **API Externa**: SAP-STL API (cloudflare tunnels)

### Frontend
- **Framework**: Next.js 14 con App Router
- **UI Components**: shadcn/ui + Radix UI
- **Estilos**: Tailwind CSS
- **Estado**: React hooks
- **Tablas**: TanStack Table v8

### Infraestructura
- **Desarrollo**: Docker Compose
- **Producción**: Windows Server con nssm (sin Docker)
- **Base de Datos**: Firebird 2.5 en `C:\App\STL\Datos\DATOS_STL.FDB`

## 📊 Módulos Implementados

### 1. Autenticación y Usuarios
- ✅ Login con JWT
- ✅ Roles: ADMINISTRADOR, OPERADOR
- ✅ Gestión de usuarios con CRUD completo

### 2. Sincronización con SAP-STL (GET - Entrada de datos)
- ✅ **ITEMS**: Productos maestros
- ✅ **DISPATCHES**: Órdenes/Despachos desde SAP
- ✅ **GOODS_RECEIPTS**: Recepciones desde SAP
- ✅ **PROCUREMENT_ORDERS**: Órdenes de compra desde SAP
- ✅ Sincronización automática configurable por módulo
- ✅ Detección de cambios con hash MD5
- ✅ Manejo de fechas ISO y conversión para Firebird

### 3. Envío de datos a SAP (POST - Salida de datos)
- ✅ **DELIVERY_NOTES** (`/Transaction/DeliveryNotes`)
  - Lee de `vw_pedidos_to_sap` donde estatus=3 y estatus_erp=2
  - Actualiza tabla `pedidos`: estatus_erp=3 si éxito
  - Sincronización automática cada 5 minutos

- ✅ **GOODS_RECEIPTS_SENT** (`/Transaction/GoodsReceipt`)
  - Lee de `vw_recepcion_to_sap` donde estatus=3 y estatus_erp=2
  - Actualiza tabla `recepciones`: estatus_erp=3 si éxito
  - Sincronización automática cada 5 minutos
  - Modo dry_run para pruebas

### 4. Gestión de Pedidos STL
- ✅ CRUD completo de pedidos locales
- ✅ Cambio de estatus con validaciones
- ✅ Interfaz simple sin paginación
- ✅ Búsqueda y filtros por fecha

### 5. Panel de Configuración
- ✅ Configuración de sincronización por entidad
- ✅ Intervalos personalizables
- ✅ Habilitación/deshabilitación por módulo
- ✅ Logs de última sincronización

## 🔄 Flujo de Sincronización

### Entrada (GET desde SAP)
1. Scheduler ejecuta según intervalo configurado
2. Cliente SAP obtiene datos del endpoint
3. Servicio optimizado compara con hash MD5
4. Inserta/actualiza solo registros modificados
5. Actualiza timestamp de sincronización

### Salida (POST hacia SAP)
1. Vista SQL filtra registros pendientes (estatus=3, estatus_erp=2)
2. Servicio agrupa por documento (cabecera + líneas)
3. Formatea fechas a ISO (2025-07-03T00:00:00Z)
4. Envía a SAP o muestra JSON (dry_run)
5. Actualiza estatus_erp=3 solo si respuesta exitosa (200/204)

## 🗄️ Estructura de Base de Datos

### Tablas principales
- `STL_ITEMS`: Productos sincronizados
- `STL_DISPATCHES` / `STL_DISPATCH_LINES`: Despachos
- `STL_GOODS_RECEIPTS` / `STL_GOODS_RECEIPT_LINES`: Recepciones
- `STL_SYNC_CONFIG`: Configuración de sincronización
- `pedidos` / `pedidos_detalle`: Pedidos locales
- `recepciones` / `recepciones_detalle`: Recepciones locales

### Vistas importantes
- `vw_pedidos_to_sap`: Pedidos listos para enviar a SAP
- `vw_recepcion_to_sap`: Recepciones listas para enviar a SAP

### Campos clave para sincronización
- `estatus`: Estado del documento (3 = listo para enviar)
- `estatus_erp`: Estado en SAP (2 = pendiente, 3 = enviado)
- `mensaje_erp`: Respuesta de SAP
- `numero_solucion_erp`: Código HTTP de respuesta

## 🚀 Deployment

### Desarrollo (Docker)
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

### Producción (Windows Server)
- Backend como servicio Windows con nssm
- Frontend con PM2 o IIS
- Logs en archivos separados: backend.log, backend-error.log
- Scripts: `deploy-windows-server.bat`

## 📝 Convenciones del Proyecto

### Backend
- Servicios singleton con instancia global
- Manejo de errores con try/catch y logging
- Fechas siempre en formato ISO para SAP
- Limpieza de strings para Firebird (CHAR padding)
- Transacciones explícitas con commit/rollback

### Frontend
- Componentes funcionales con TypeScript
- Shadcn/ui para UI consistente
- Formularios con validación client-side
- Manejo de estados de carga y errores
- Notificaciones toast para feedback

### Git
- Commits descriptivos en español
- Savepoints para hitos importantes
- Scripts SQL versionados
- Archivos .env excluidos

## 🔧 Pendientes (TODO)
1. ❌ Arreglar DialogTitle faltante en componentes React
2. ❌ Implementar sincronización manual por módulo
3. ❌ Funcionalidad de exportación de datos
4. ❌ Dashboard con métricas de sincronización
5. ❌ Manejo de conflictos en sincronización bidireccional

## 📌 Notas Importantes
- Firebird 2.5 tiene limitaciones con campos CHAR (padding)
- SAP-STL API cambia URL frecuentemente (túnel cloudflare)
- Fechas deben convertirse de/hacia ISO format
- Windows Server requiere quitar emojis de logs (cp1252)
- Modo dry_run siempre por defecto para seguridad

## 🔐 Credenciales Default
- **Backend**: admin / admin123
- **Firebird**: sysdba / masterkey
- **SAP-STL**: STLUser / 7a6T9IVeUdf5bvRIv

---
*Última actualización: 2025-07-03*