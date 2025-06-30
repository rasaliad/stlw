-- ========================================
-- AGREGAR ROLES AL SISTEMA DE USUARIOS
-- ========================================

-- Agregar campo ROLE a la tabla USERS
ALTER TABLE USERS ADD ROLE VARCHAR(20) DEFAULT 'OPERADOR';

-- Crear índice para búsquedas por rol
CREATE INDEX IDX_USERS_ROLE ON USERS(ROLE);

-- Actualizar usuario admin para que tenga rol de administrador
UPDATE USERS SET ROLE = 'ADMIN' WHERE USERNAME = 'admin';

COMMIT;