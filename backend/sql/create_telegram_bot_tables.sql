-- Tabla para almacenar usuarios de Telegram
CREATE TABLE STL_TELEGRAM_USERS (
    ID INTEGER NOT NULL PRIMARY KEY,
    TELEGRAM_ID BIGINT NOT NULL UNIQUE,
    TELEGRAM_USERNAME VARCHAR(50),
    TELEGRAM_FIRST_NAME VARCHAR(100),
    TELEGRAM_LAST_NAME VARCHAR(100),
    USER_ID INTEGER, -- FK a tabla USERS (cuando se vincula)
    IS_ACTIVE CHAR(1) DEFAULT 'N' CHECK (IS_ACTIVE IN ('Y', 'N')),
    IS_VERIFIED CHAR(1) DEFAULT 'N' CHECK (IS_VERIFIED IN ('Y', 'N')),
    VERIFICATION_CODE VARCHAR(10), -- Código para vincular con usuario del sistema
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    VERIFIED_AT TIMESTAMP,
    LAST_INTERACTION TIMESTAMP
);

-- Tabla para suscripciones a notificaciones
CREATE TABLE STL_TELEGRAM_SUBSCRIPTIONS (
    ID INTEGER NOT NULL PRIMARY KEY,
    TELEGRAM_USER_ID INTEGER NOT NULL,
    NOTIFICATION_TYPE VARCHAR(50) NOT NULL, -- DELIVERY_NOTES, GOODS_RECEIPTS, ERRORS, etc
    IS_ACTIVE CHAR(1) DEFAULT 'Y' CHECK (IS_ACTIVE IN ('Y', 'N')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_TELEGRAM_SUB_USER FOREIGN KEY (TELEGRAM_USER_ID) 
        REFERENCES STL_TELEGRAM_USERS(ID) ON DELETE CASCADE
);

-- Tabla para mensajes pendientes de enviar
CREATE TABLE STL_TELEGRAM_QUEUE (
    ID INTEGER NOT NULL PRIMARY KEY,
    TELEGRAM_USER_ID INTEGER,
    CHAT_ID BIGINT NOT NULL, -- Para envíos a grupos o canales
    MESSAGE_TYPE VARCHAR(50) NOT NULL, -- NOTIFICATION, ALERT, RESPONSE, etc
    MESSAGE_TEXT VARCHAR(4000) NOT NULL,
    MESSAGE_HTML VARCHAR(4000), -- Mensaje en formato HTML
    PRIORITY INTEGER DEFAULT 5, -- 1=Urgente, 5=Normal, 10=Bajo
    STATUS VARCHAR(20) DEFAULT 'PENDING', -- PENDING, SENT, FAILED, CANCELLED
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SENT_AT TIMESTAMP,
    ERROR_MESSAGE VARCHAR(500),
    RETRY_COUNT INTEGER DEFAULT 0,
    MAX_RETRIES INTEGER DEFAULT 3
);

-- Tabla para historial de comandos del bot
CREATE TABLE STL_TELEGRAM_COMMANDS (
    ID INTEGER NOT NULL PRIMARY KEY,
    TELEGRAM_USER_ID INTEGER NOT NULL,
    COMMAND VARCHAR(100) NOT NULL,
    PARAMETERS VARCHAR(500),
    RESPONSE_TEXT VARCHAR(4000),
    RESPONSE_TIME_MS INTEGER,
    SUCCESS CHAR(1) DEFAULT 'Y' CHECK (SUCCESS IN ('Y', 'N')),
    ERROR_MESSAGE VARCHAR(500),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_TELEGRAM_CMD_USER FOREIGN KEY (TELEGRAM_USER_ID) 
        REFERENCES STL_TELEGRAM_USERS(ID)
);

-- Tabla de configuración del bot
CREATE TABLE STL_TELEGRAM_CONFIG (
    CONFIG_KEY VARCHAR(50) NOT NULL PRIMARY KEY,
    CONFIG_VALUE VARCHAR(500),
    DESCRIPTION VARCHAR(200),
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar configuración inicial
INSERT INTO STL_TELEGRAM_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES ('BOT_TOKEN', '', 'Token del bot de Telegram');
INSERT INTO STL_TELEGRAM_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES ('NOTIFICATION_INTERVAL', '60', 'Intervalo en segundos para enviar notificaciones');
INSERT INTO STL_TELEGRAM_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES ('MAX_RETRIES', '3', 'Máximo de reintentos para mensajes fallidos');
INSERT INTO STL_TELEGRAM_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES ('ENABLE_NOTIFICATIONS', 'Y', 'Habilitar envío de notificaciones');
INSERT INTO STL_TELEGRAM_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES ('ENABLE_QUERIES', 'Y', 'Habilitar consultas via bot');
INSERT INTO STL_TELEGRAM_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES ('WELCOME_MESSAGE', 'Bienvenido al Bot STL Warehouse. Use /start para comenzar.', 'Mensaje de bienvenida');


-- Generadores de secuencia
CREATE GENERATOR GEN_STL_TELEGRAM_USERS_ID;
SET GENERATOR GEN_STL_TELEGRAM_USERS_ID TO 0;

CREATE GENERATOR GEN_STL_TELEGRAM_SUBSCRIP_ID;
SET GENERATOR GEN_STL_TELEGRAM_SUBSCRIP_ID TO 0;

CREATE GENERATOR GEN_STL_TELEGRAM_QUEUE_ID;
SET GENERATOR GEN_STL_TELEGRAM_QUEUE_ID TO 0;

CREATE GENERATOR GEN_STL_TELEGRAM_COMMANDS_ID;
SET GENERATOR GEN_STL_TELEGRAM_COMMANDS_ID TO 0;

-- Triggers para IDs automáticos
SET TERM ^ ;

CREATE TRIGGER STL_TELEGRAM_USERS_BI FOR STL_TELEGRAM_USERS
ACTIVE BEFORE INSERT POSITION 0
AS
BEGIN
    IF (NEW.ID IS NULL) THEN
        NEW.ID = GEN_ID(GEN_STL_TELEGRAM_USERS_ID, 1);
END^

CREATE TRIGGER STL_TELEGRAM_SUBSCRIPTIONS_BI FOR STL_TELEGRAM_SUBSCRIPTIONS
ACTIVE BEFORE INSERT POSITION 0
AS
BEGIN
    IF (NEW.ID IS NULL) THEN
        NEW.ID = GEN_ID(GEN_STL_TELEGRAM_SUBSCRIP_ID, 1);
END^

CREATE TRIGGER STL_TELEGRAM_QUEUE_BI FOR STL_TELEGRAM_QUEUE
ACTIVE BEFORE INSERT POSITION 0
AS
BEGIN
    IF (NEW.ID IS NULL) THEN
        NEW.ID = GEN_ID(GEN_STL_TELEGRAM_QUEUE_ID, 1);
END^

CREATE TRIGGER STL_TELEGRAM_COMMANDS_BI FOR STL_TELEGRAM_COMMANDS
ACTIVE BEFORE INSERT POSITION 0
AS
BEGIN
    IF (NEW.ID IS NULL) THEN
        NEW.ID = GEN_ID(GEN_STL_TELEGRAM_COMMANDS_ID, 1);
END^

SET TERM ; ^

-- Índices para mejorar performance
CREATE INDEX IDX_TELEGRAM_USERS_TG_ID ON STL_TELEGRAM_USERS(TELEGRAM_ID);
CREATE INDEX IDX_TELEGRAM_QUEUE_STATUS ON STL_TELEGRAM_QUEUE(STATUS);
CREATE INDEX IDX_TELEGRAM_QUEUE_CREATED ON STL_TELEGRAM_QUEUE(CREATED_AT);
CREATE INDEX IDX_TELEGRAM_COMMANDS_USER ON STL_TELEGRAM_COMMANDS(TELEGRAM_USER_ID);
CREATE INDEX IDX_TELEGRAM_COMMANDS_CREATED ON STL_TELEGRAM_COMMANDS(CREATED_AT);

COMMIT;
