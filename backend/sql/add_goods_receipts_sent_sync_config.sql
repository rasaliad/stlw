-- Agregar configuración de sincronización para GOODS_RECEIPTS_SENT
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
    'GOODS_RECEIPTS_SENT',
    'Y',  -- Habilitado por defecto
    5,    -- Cada 5 minutos
    NULL,
    CURRENT_TIMESTAMP,
    100,  -- Procesar hasta 100 recepciones por vez
    '/Transaction/GoodsReceipt',
    'Envío de recepciones con estatus=3 y estatus_erp=2 a SAP-STL'
);