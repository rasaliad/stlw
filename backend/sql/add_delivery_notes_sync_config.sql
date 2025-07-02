-- Agregar configuración de sincronización para DELIVERY_NOTES
INSERT INTO STL_SYNC_CONFIG (
    ENTITY_TYPE,
    SYNC_ENABLED,
    SYNC_INTERVAL_MINUTES,
    LAST_SYNC_AT,
    NEXT_SYNC_AT,
    BATCH_SIZE,
    API_ENDPOINT,
    NOTES
) VALUES (
    'DELIVERY_NOTES',
    'Y',  -- Habilitado por defecto
    5,    -- Cada 5 minutos
    NULL,
    CURRENT_TIMESTAMP,
    100,  -- Procesar hasta 100 pedidos por vez
    '/Transaction/DeliveryNotes',
    'Envío de pedidos con estatus=3 y estatus_erp=2 a SAP-STL'
);