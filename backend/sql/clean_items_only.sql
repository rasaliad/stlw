-- ========================================
-- SCRIPT PARA LIMPIAR SOLO ITEMS SAP-STL
-- ========================================
-- Este script elimina solo los items, manteniendo despachos y recepciones

-- Limpiar solo items
DELETE FROM STL_ITEMS;

-- Reiniciar generador de ID (opcional)
-- SET GENERATOR GEN_STL_ITEMS_ID TO 0;

-- Confirmar limpieza
SELECT COUNT(*) AS ITEMS_RESTANTES FROM STL_ITEMS;