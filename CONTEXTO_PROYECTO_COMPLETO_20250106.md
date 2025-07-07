# Contexto Completo del Proyecto STL Warehouse - 2025-01-06

## 🏭 Sistema STL Warehouse Management

Sistema fullstack de gestión de almacén que integra:
- **Frontend**: Next.js 14 con shadcn/ui
- **Backend**: FastAPI con Firebird 2.5
- **Integración**: SAP-STL API via cloudflare tunnels
- **Notificaciones**: Bot de Telegram integrado

## 📊 Módulos Implementados

### 1. Autenticación y Usuarios ✅
- Login JWT con roles (ADMINISTRADOR, OPERADOR)
- CRUD completo de usuarios
- Gestión de sesiones

### 2. Sincronización SAP → STL (GET) ✅
Sincronización automática cada X minutos configurable:

| Entidad | Endpoint SAP | Tablas STL | Estado |
|---------|--------------|------------|---------|
| ITEMS | /MasterData/Items | STL_ITEMS | ✅ Optimizado con hash MD5 |
| DISPATCHES | /Transaction/Orders | STL_DISPATCHES + LINES | ✅ Optimizado |
| GOODS_RECEIPTS | /Transaction/GoodsReceipt | STL_GOODS_RECEIPTS + LINES | ✅ Optimizado |
| PROCUREMENT_ORDERS | /Transaction/ProcurementOrders | STL_GOODS_RECEIPTS + LINES | ✅ Optimizado |

### 3. Envío STL → SAP (POST) ✅

#### DELIVERY_NOTES (Pedidos)
- **Vista fuente**: `vw_pedidos_to_sap`
- **Filtro**: `estatus = 3 AND estatus_erp = 2`
- **Endpoint SAP**: `POST /Transaction/DeliveryNotes`
- **Actualiza**: tabla `pedidos` → `estatus_erp = 3` si éxito
- **Clave única**: `numeroBusqueda + tipoDespacho`

#### GOODS_RECEIPTS_SENT (Recepciones)
- **Vista fuente**: `vw_recepcion_to_sap`
- **Filtro**: `estatus = 3 AND estatus_erp = 2`
- **Endpoint SAP**: `POST /Transaction/GoodsReceipt`
- **Actualiza**: tabla `recepciones` → `estatus_erp = 3` si éxito
- **Clave única**: `numeroBusqueda + tipoRecepcion`

### 4. Gestión Local STL ✅
- CRUD de pedidos locales (tabla `pedidos`)
- Estados: Pendiente → En Proceso → Completado
- Interfaz simple sin paginación
- Búsqueda y filtros por fecha

### 5. Bot de Telegram 🆕 ✅

#### Tablas Creadas
- `STL_TELEGRAM_USERS`: Usuarios del bot
- `STL_TELEGRAM_SUBSCRIPTIONS`: Suscripciones a notificaciones
- `STL_TELEGRAM_QUEUE`: Cola de mensajes pendientes
- `STL_TELEGRAM_COMMANDS`: Historial de comandos
- `STL_TELEGRAM_CONFIG`: Configuración (BOT_TOKEN ya configurado)

#### Comandos del Bot
- `/start` - Registrar usuario
- `/vincular <código>` - Vincular con usuario del sistema
- `/status` - Ver estado de cuenta
- `/suscribir <tipo>` - Suscribirse a notificaciones
- `/desuscribir <tipo>` - Cancelar suscripción
- `/consultar <tipo> <valor>` - Consultas (producto, pedido, existencia)
- `/help` - Ver ayuda

#### Tipos de Notificación
- `DELIVERY_NOTES` - Envíos de pedidos a SAP
- `GOODS_RECEIPTS` - Recepciones a SAP
- `ERRORS` - Solo errores
- `ALL` - Todas las notificaciones

#### Integración con Sistema
- Notificaciones automáticas al enviar a SAP (éxito ✅ o error ❌)
- Formato HTML con detalles completos
- Cola procesada cada minuto
- Solo usuarios verificados y activos reciben mensajes

## 🔧 Configuración Técnica

### Backend
```python
# Archivos clave modificados/creados:
- app/services/telegram_bot_service.py (nuevo)
- app/api/endpoints/telegram.py (nuevo)
- app/services/sap_delivery_service.py (notificaciones agregadas)
- app/services/sap_goods_receipt_service.py (notificaciones agregadas)
- app/services/background_sync_service.py (cola Telegram)
- requirements.txt (python-telegram-bot==20.7)
```

### Base de Datos
```sql
-- Tablas de sincronización
STL_ITEMS, STL_DISPATCHES, STL_GOODS_RECEIPTS
STL_DISPATCH_LINES, STL_GOODS_RECEIPT_LINES
STL_SYNC_CONFIG, STL_SYNC_LOG

-- Tablas locales
pedidos, pedidos_detalle
recepciones, recepciones_detalle

-- Tablas Telegram (nuevas)
STL_TELEGRAM_USERS, STL_TELEGRAM_SUBSCRIPTIONS
STL_TELEGRAM_QUEUE, STL_TELEGRAM_COMMANDS
STL_TELEGRAM_CONFIG
```

### Vistas SQL
- `vw_pedidos_to_sap`: Pedidos listos para enviar
- `vw_recepcion_to_sap`: Recepciones listas para enviar

## 📡 API Endpoints

### Sincronización
- `GET /api/v1/sync-config` - Ver configuración
- `PUT /api/v1/sync-config/{entity}` - Actualizar config

### Envío a SAP
- `POST /api/v1/sap/delivery/send-pending-deliveries?dry_run=true`
- `POST /api/v1/sap/goods-receipt/send-pending-receipts?dry_run=true`

### Telegram
- `GET/POST /api/v1/telegram/config` - Configuración bot
- `GET /api/v1/telegram/users` - Lista usuarios
- `POST /api/v1/telegram/users/{id}/activate` - Activar usuario
- `POST /api/v1/telegram/users/{id}/generate-code` - Generar código
- `GET /api/v1/telegram/queue` - Ver cola mensajes
- `GET /api/v1/telegram/bot-status` - Estado del bot

## 🚀 Estado Actual

### ✅ Completado
1. Sincronización bidireccional SAP ↔ STL
2. Envío de pedidos (DeliveryNotes)
3. Envío de recepciones (GoodsReceipts)
4. Bot de Telegram con notificaciones
5. Sistema de autenticación y roles
6. Optimización con hash MD5
7. Modo dry_run para pruebas seguras

### 🔄 En Proceso
1. Activación del bot de Telegram (token configurado, falta inicializar)
2. Pruebas de notificaciones automáticas

### 📝 Pendiente
1. Arreglar DialogTitle en componentes React
2. Sincronización manual por módulo
3. Exportación de datos
4. Dashboard con métricas

## 🔐 Credenciales

### Sistema
- Backend: admin / admin123
- Firebird: sysdba / masterkey

### SAP-STL API
- URL: https://manitoba-sale-dir-beef.trycloudflare.com
- Usuario: STLUser
- Password: 7a6T9IVeUdf5bvRIv

### Telegram Bot
- Token: [YA CONFIGURADO EN BD]
- Requiere activación manual por admin

## 💡 Notas Importantes

1. **Claves únicas corregidas**:
   - Despachos: `numeroBusqueda + tipoDespacho` (NO numeroDespacho)
   - Recepciones: `numeroBusqueda + tipoRecepcion` (NO numeroDocumento)

2. **Formato de fechas**: Siempre ISO (2025-01-06T00:00:00Z)

3. **Windows Server**: Logs sin emojis por encoding cp1252

4. **Docker**: Backend reconstruido con python-telegram-bot

5. **Seguridad**: Bot no se activa automáticamente, requiere:
   - Token en BD ✅
   - Llamada manual a initialize()
   - Usuarios deben ser verificados por admin

## 🎯 Próximos Pasos

1. **Activar Bot Telegram**:
   ```python
   # En main.py después de startup:
   await telegram_bot_service.initialize()
   await telegram_bot_service.start_bot()
   ```

2. **Probar flujo completo**:
   - Usuario se registra con /start
   - Admin genera código de vinculación
   - Usuario usa /vincular <código>
   - Admin activa usuario
   - Usuario se suscribe a notificaciones
   - Sistema envía notificación cuando hay POST a SAP

3. **Desplegar a Producción**:
   - Cambiar dry_run por defecto a false
   - Configurar Windows Server
   - Activar todas las sincronizaciones

---
*Última actualización: 2025-01-06 19:00*