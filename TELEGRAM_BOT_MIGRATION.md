# Migración del Bot de Telegram - Proyecto Separado

## Resumen

El bot de Telegram ha sido extraído del backend STL principal y movido a un proyecto independiente en `/home/rasaliad/app/stl-telegram-bot/` para mejorar la estabilidad y separación de responsabilidades.

## Cambios Realizados

### Backend STL (Limpieza)

#### Archivos Eliminados:
- `backend/app/services/telegram_bot_service.py`
- `backend/app/api/endpoints/telegram.py`

#### Archivos Modificados:

**1. `requirements.txt`**
- ❌ Removido: `python-telegram-bot==20.7`

**2. `app/api/routes.py`** 
- ❌ Removido: Import y router de telegram

**3. `app/services/background_sync_service.py`**
- ❌ Removido: Job de procesamiento de cola Telegram
- ❌ Removido: Método `process_telegram_queue()`

**4. `app/services/sap_delivery_service.py`**
- ✅ Mantenido: Método `_send_webhook_notification()` 
- ✅ Funciona independientemente del bot

**5. `app/services/sap_goods_receipt_service.py`**
- ✅ Mantenido: Método `_send_webhook_notification()`
- ✅ Funciona independientemente del bot

### Nuevo Proyecto: STL Telegram Bot

#### Estructura del Proyecto:
```
/home/rasaliad/app/stl-telegram-bot/
├── README.md
├── requirements.txt
├── .env.example
├── main.py
└── src/
    ├── __init__.py
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    ├── database/
    │   ├── __init__.py
    │   └── connection.py
    ├── models/
    │   ├── __init__.py
    │   └── telegram_models.py
    ├── services/
    │   ├── __init__.py
    │   └── queue_processor.py
    └── bot/
        ├── __init__.py
        └── telegram_bot.py
```

#### Características del Bot Separado:

**1. Arquitectura Independiente**
- ✅ Servicio standalone con su propio `main.py`
- ✅ Configuración independiente via `.env`
- ✅ Logging separado
- ✅ Manejo de errores aislado

**2. Funcionalidades Completas**
- ✅ Todos los comandos del bot original
- ✅ Sistema de usuarios y verificación
- ✅ Suscripciones a notificaciones
- ✅ Procesamiento de cola de mensajes
- ✅ Consultas al sistema STL

**3. Conexión con STL**
- ✅ Acceso directo a la misma base de datos
- ✅ Lee cola de notificaciones (`STL_TELEGRAM_QUEUE`)
- ✅ Procesa mensajes generados por el backend STL

## Integración Backend ↔ Bot

### Flujo de Notificaciones:

1. **Backend STL** ejecuta operaciones (envío a SAP)
2. **Backend STL** llama `_send_webhook_notification()`
3. Se inserta registro en `STL_TELEGRAM_QUEUE`
4. **Bot independiente** procesa cola cada 60 segundos
5. **Bot** envía notificaciones a usuarios suscritos

### Ventajas de la Separación:

✅ **Estabilidad**: Problemas del bot no afectan al STL
✅ **Escalabilidad**: Bot puede ejecutarse en servidor diferente
✅ **Mantenimiento**: Actualizaciones independientes
✅ **Logs separados**: Debugging más fácil
✅ **Reinicio independiente**: Sin afectar operaciones STL

## Instrucciones de Despliegue

### 1. Configurar Bot Separado

```bash
cd /home/rasaliad/app/stl-telegram-bot/

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env
# Editar .env con:
# - DB_PATH: Ruta a DATOS_STL.FDB
# - TELEGRAM_BOT_TOKEN: Token del bot
```

### 2. Obtener Token del Bot

```sql
-- Obtener token configurado en STL
SELECT BOT_TOKEN FROM STL_TELEGRAM_CONFIG WHERE IS_ACTIVE = 1;
```

### 3. Ejecutar Bot

```bash
# Desarrollo
python main.py

# Producción (con logs)
nohup python main.py > bot.log 2>&1 &
```

### 4. Verificar Funcionamiento

```bash
# Ver logs del bot
tail -f stl_telegram_bot.log

# Verificar cola de mensajes
# (Desde backend STL, endpoint existente)
curl http://localhost:8000/api/v1/telegram/queue
```

## Estado de las Tablas

Las tablas de Telegram **permanecen en la base de datos STL**:
- ✅ `STL_TELEGRAM_USERS`
- ✅ `STL_TELEGRAM_SUBSCRIPTIONS` 
- ✅ `STL_TELEGRAM_QUEUE`
- ✅ `STL_TELEGRAM_COMMANDS`
- ✅ `STL_TELEGRAM_CONFIG`

Ambos proyectos acceden a las mismas tablas:
- **Backend STL**: Escribe en `STL_TELEGRAM_QUEUE`
- **Bot independiente**: Lee y procesa cola

## Próximos Pasos

1. **Configurar y probar bot separado**
2. **Verificar notificaciones automáticas**
3. **Actualizar documentación de producción**
4. **Configurar monitoreo del bot independiente**

## Rollback (Si es necesario)

Si se necesita volver al sistema integrado:
1. Restaurar archivos eliminados del backend STL
2. Restaurar imports en `routes.py`
3. Restaurar `python-telegram-bot` en `requirements.txt`
4. Restaurar job de Telegram en `background_sync_service.py`

---

✅ **Migración completada exitosamente**
🤖 **Bot independiente listo para despliegue**
🔗 **Integración vía base de datos mantenida**