# 🧪 Guía de Pruebas de Sincronización SAP-STL

## 📋 Comandos de Prueba

### 1. Ver Estado Actual
```bash
# Ver configuración actual
curl -X GET "http://localhost:8000/api/sap-stl/config/status"

# Ver resumen de datos
curl -X GET "http://localhost:8000/api/sap-stl/analytics/summary"
```

### 2. Limpiar Datos

#### Limpiar TODO
```bash
curl -X DELETE "http://localhost:8000/api/sap-stl/data/clean"
```

#### Limpiar Solo Items
```bash
curl -X DELETE "http://localhost:8000/api/sap-stl/data/clean?entity_type=items"
```

#### Limpiar Solo Despachos
```bash
curl -X DELETE "http://localhost:8000/api/sap-stl/data/clean?entity_type=dispatches"
```

#### Limpiar Solo Recepciones
```bash
curl -X DELETE "http://localhost:8000/api/sap-stl/data/clean?entity_type=goods_receipts"
```

### 3. Sincronizar Datos

#### Sincronizar Todo
```bash
curl -X GET "http://localhost:8000/api/sap-stl/sync-now"
```

#### Sincronizar Solo Items
```bash
curl -X POST "http://localhost:8000/api/sap-stl/sync/items"
```

### 4. Cambiar Modo Simulación

#### Activar Modo Simulación
```bash
curl -X POST "http://localhost:8000/api/sap-stl/config/mock-mode?enabled=true"
```

#### Desactivar Modo Simulación (usar servidor real)
```bash
curl -X POST "http://localhost:8000/api/sap-stl/config/mock-mode?enabled=false"
```

## 🔄 Flujo de Prueba Completo

### Prueba 1: Limpiar y Recargar Todo
```bash
# 1. Ver estado inicial
curl -X GET "http://localhost:8000/api/sap-stl/analytics/summary"

# 2. Limpiar todos los datos
curl -X DELETE "http://localhost:8000/api/sap-stl/data/clean"

# 3. Verificar que está vacío
curl -X GET "http://localhost:8000/api/sap-stl/analytics/summary"

# 4. Sincronizar todo
curl -X GET "http://localhost:8000/api/sap-stl/sync-now"

# 5. Verificar datos cargados
curl -X GET "http://localhost:8000/api/sap-stl/analytics/summary"
```

### Prueba 2: Actualización Incremental
```bash
# 1. Sincronizar (no debe insertar duplicados)
curl -X GET "http://localhost:8000/api/sap-stl/sync-now"

# 2. Verificar que solo se actualizaron
curl -X GET "http://localhost:8000/api/sap-stl/analytics/summary"
```

### Prueba 3: Verificar Datos Específicos
```bash
# Buscar items específicos
curl -X GET "http://localhost:8000/api/sap-stl/items?search=BADIA"

# Ver despachos
curl -X GET "http://localhost:8000/api/sap-stl/dispatches?limit=5"

# Ver recepciones
curl -X GET "http://localhost:8000/api/sap-stl/goods-receipts?limit=5"

# Ver líneas de un despacho específico
curl -X GET "http://localhost:8000/api/sap-stl/dispatches/1/lines"
```

## 📊 Datos Disponibles en Modo Simulación

### Items
- **Fuente**: `/app/response_Items.json`
- **Cantidad**: 610 items reales
- **Incluye**: Productos de diferentes categorías (carnes, especias, mariscos, etc.)

### Despachos
- **Cantidad**: 2 despachos simulados
- **Incluye**: Líneas de productos con cantidades

### Recepciones
- **Cantidad**: 3 recepciones simuladas
- **Incluye**: Proveedores y líneas de productos recibidos

## 🔧 Scripts SQL Disponibles

### Limpiar Todo
```sql
-- Archivo: /backend/sql/clean_stl_data.sql
DELETE FROM STL_GOODS_RECEIPT_LINES;
DELETE FROM STL_GOODS_RECEIPTS;
DELETE FROM STL_DISPATCH_LINES;
DELETE FROM STL_DISPATCHES;
DELETE FROM STL_ITEMS;
```

### Limpiar Solo Items
```sql
-- Archivo: /backend/sql/clean_items_only.sql
DELETE FROM STL_ITEMS;
```

## 🐛 Solución de Problemas

### El archivo JSON no se carga
```bash
# Copiar archivo al contenedor
docker cp response_Items.json stl_backend:/app/response_Items.json

# Reiniciar contenedor
docker-compose restart backend
```

### Verificar logs
```bash
# Ver logs del backend
docker logs stl_backend | tail -50

# Ver logs específicos de sincronización
docker logs stl_backend | grep -i "sync\|mock"
```

## 📝 Notas Importantes

1. **Modo Simulación**: Por defecto está activado (`USE_MOCK_SAP_DATA=true`)
2. **Datos Únicos**: El sistema respeta las claves únicas:
   - Items: `codigoProducto`
   - Despachos: `numeroDespacho + tipoDespacho`
   - Recepciones: `numeroDocumento + tipoRecepcion`
3. **Sincronización Incremental**: Si ejecutas sync varias veces, no duplica datos
4. **Persistencia**: Los datos se mantienen entre reinicios del contenedor