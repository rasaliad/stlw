# Savepoint - 2025-07-03

## Resumen del Trabajo Realizado

### 1. Implementación POST /Transaction/DeliveryNotes
- ✅ Servicio `sap_delivery_service.py` creado
- ✅ Lee de vista `vw_pedidos_to_sap` donde estatus=3 y estatus_erp=2
- ✅ Actualiza pedidos: estatus_erp=3 en éxito (200/204)
- ✅ Modo dry_run para pruebas
- ✅ Integrado en sincronización automática cada 5 minutos

### 2. Fix de Logging y Unicode
- ✅ Configuración de logging en `main.py`
- ✅ Eliminados emojis Unicode que causaban errores en Windows Server
- ✅ Logs detallados para debugging de sincronizaciones
- ✅ Variable LOG_LEVEL configurable

### 3. Implementación PROCUREMENT_ORDERS
- ✅ Sincroniza desde `/Transaction/ProcurementOrders`
- ✅ Guarda en tablas STL_GOODS_RECEIPTS (mismas que GOODS_RECEIPTS)
- ✅ Diferenciado por campo tipoRecepcion
- ✅ Fix de manejo de fechas (datetime y strings ISO)

### 4. Deployment
- ✅ Scripts para Windows Server sin Docker
- ✅ Configuración nssm para logs
- ✅ Git workflows establecidos

## Estado Actual del Sistema

### Sincronizaciones Activas:
- DELIVERY_NOTES: cada 5 minutos (envía pedidos a SAP)
- PROCUREMENT_ORDERS: cada 1 minuto
- GOODS_RECEIPTS: cada 1 minuto
- DISPATCHES: cada 1 minuto
- ITEMS: cada 1 minuto

### Archivos Clave Modificados:
```
backend/app/services/sap_delivery_service.py (nuevo)
backend/app/services/optimized_sync_service.py
backend/app/services/background_sync_service.py
backend/app/services/sap_stl_client.py
backend/app/main.py
backend/app/api/endpoints/sap_delivery.py (nuevo)
```

## Configuración para Desarrollo Dual (PC Casa + Laptop)

### En PC con Windows 11 + Docker Desktop:
1. `git clone https://github.com/rasaliad/stlw.git`
2. Configurar `.env` con Firebird local o remoto
3. `docker-compose up -d`
4. Acceder a http://localhost:3000 y http://localhost:8000/docs

### Flujo de Sincronización:
1. Siempre: `git pull origin main` antes de empezar
2. Trabajar normalmente
3. Al terminar: `git add . && git commit -m "mensaje" && git push origin main`

## Pendientes (TODO List):
1. Arreglar DialogTitle faltante en componentes React
2. Implementar sincronización manual por módulo
3. Funcionalidad de exportación de datos
4. Mejorar manejo de errores en sincronizaciones

## Últimos Commits:
- Fix error de fecha en PROCUREMENT_ORDERS - manejo de datetime
- Implementar sincronización de PROCUREMENT_ORDERS
- Agregar logging detallado para debugging
- Fix Unicode emoji errors in Windows Server
- Implementar logging completo para sincronización automática
- Restore verbose logging for debugging SAP synchronization

## Notas Importantes:
- El servidor de producción está en Windows Server sin Docker
- Base de datos Firebird 2.5 con limitaciones de CHAR padding
- API SAP-STL puede cambiar de URL (usar túnel cloudflare)
- Fechas deben ser ISO format: 2025-07-01T00:00:00Z