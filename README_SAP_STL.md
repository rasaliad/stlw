# 🔗 Integración SAP-STL

## 📋 Resumen

Este sistema proporciona integración completa con la API SAP-STL externa, incluyendo sincronización de datos y modo simulación para desarrollo.

## ✅ Estado Actual

- **✅ Items**: 616 sincronizados correctamente
- **✅ Despachos**: 2 sincronizados con datos simulados
- **✅ Recepciones**: 3 sincronizadas con datos simulados
- **✅ Modo Simulación**: Funcionando mientras servidor externo no está disponible

## 🎛️ Configuración

### Variables de Entorno

```bash
# API SAP-STL
SAP_STL_URL=https://dependent-vehicle-victory-por.trycloudflare.com
SAP_STL_USERNAME=STLUser
SAP_STL_PASSWORD=7a6T9IVeUdf5bvRIv

# Modo simulación (true/false)
USE_MOCK_SAP_DATA=true
```

## 🔄 Modos de Operación

### 1. Modo Simulación (Actual)
- **Cuándo usar**: Mientras el servidor SAP-STL no esté disponible
- **Configuración**: `USE_MOCK_SAP_DATA=true`
- **Datos**: Utiliza respuestas JSON predefinidas de los archivos de ejemplo
- **Ventajas**: Permite desarrollo y testing sin dependencia externa

### 2. Modo Real
- **Cuándo usar**: Cuando el servidor SAP-STL esté disponible
- **Configuración**: `USE_MOCK_SAP_DATA=false`
- **URL**: Cambiar a servidor productivo cuando esté listo
- **Autenticación**: Funciona con credenciales reales

## 🚀 Endpoints Principales

### Sincronización
```bash
# Sincronizar todas las entidades
GET /api/sap-stl/sync-now

# Sincronizar entidad específica
POST /api/sap-stl/sync/items
POST /api/sap-stl/sync/dispatches
POST /api/sap-stl/sync/goods_receipts
```

### Configuración
```bash
# Ver estado actual
GET /api/sap-stl/config/status

# Cambiar modo simulación
POST /api/sap-stl/config/mock-mode?enabled=true

# Probar conexión
GET /api/sap-stl/test-connection
```

### Consulta de Datos
```bash
# Items sincronizados
GET /api/sap-stl/items?limit=10&search=BADIA

# Despachos
GET /api/sap-stl/dispatches?tipo_despacho=201

# Recepciones de mercancía
GET /api/sap-stl/goods-receipts?tipo_recepcion=102

# Resumen analítico
GET /api/sap-stl/analytics/summary
```

## 📊 Estructura de Datos

### Items (STL_ITEMS)
- Código producto, descripción
- Familia de productos
- Días de vencimiento
- Unidades de medida

### Despachos (STL_DISPATCHES + STL_DISPATCH_LINES)
- Número de despacho, tipo
- Cliente, fechas
- Líneas de productos con cantidades

### Recepciones (STL_GOODS_RECEIPTS + STL_GOODS_RECEIPT_LINES)
- Número de documento, tipo recepción
- Proveedor, fecha
- Líneas de productos recibidos

## 🔧 Transición a Servidor Real

Cuando esté disponible el servidor definitivo:

1. **Actualizar URL**:
   ```bash
   SAP_STL_URL=http://servidor-productivo:puerto
   ```

2. **Desactivar simulación**:
   ```bash
   USE_MOCK_SAP_DATA=false
   ```

3. **Verificar credenciales**:
   ```bash
   SAP_STL_USERNAME=usuario-productivo
   SAP_STL_PASSWORD=password-productivo
   ```

4. **Probar conexión**:
   ```bash
   curl -X GET "http://localhost:8000/api/sap-stl/test-connection"
   ```

## 🧪 Testing

### Probar Modo Simulación
```bash
# Activar simulación
curl -X POST "http://localhost:8000/api/sap-stl/config/mock-mode?enabled=true"

# Sincronizar datos simulados
curl -X GET "http://localhost:8000/api/sap-stl/sync-now"

# Ver resultados
curl -X GET "http://localhost:8000/api/sap-stl/analytics/summary"
```

### Probar Modo Real
```bash
# Desactivar simulación
curl -X POST "http://localhost:8000/api/sap-stl/config/mock-mode?enabled=false"

# Probar conexión real
curl -X GET "http://localhost:8000/api/sap-stl/test-connection"
```

## 📈 Monitoreo

### Logs Importantes
```bash
# Ver logs del contenedor
docker logs stl_backend | grep -i "sap\|sync\|mock"
```

### Métricas de Sincronización
- Items sincronizados
- Despachos procesados
- Recepciones importadas
- Errores y tiempo de procesamiento

## 🔒 Seguridad

- ✅ Autenticación Bearer Token
- ✅ Credenciales en variables de entorno
- ✅ Validación de datos con Pydantic
- ✅ Manejo de errores y timeouts

## 📝 Notas Técnicas

- **Firebird Database**: Almacenamiento local de datos sincronizados
- **Async/Await**: Operaciones asíncronas para mejor rendimiento
- **Pydantic Models**: Validación automática de datos
- **Docker**: Containerización completa del sistema
- **FastAPI**: API REST moderna con documentación automática

---

**Estado**: ✅ Funcionando en modo simulación  
**Próximo paso**: Transición a servidor productivo cuando esté disponible