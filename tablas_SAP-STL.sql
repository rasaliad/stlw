/******************************************************************************/
/****        Generated by IBExpert 2025.2.4.1 6/29/2025 1:09:07 AM         ****/
/******************************************************************************/

SET SQL DIALECT 3;

SET NAMES ISO8859_1;

CREATE DATABASE 'C:\App\STL\Datos\DATOS_STL.FDB'
USER 'SYSDBA' PASSWORD 'masterkey'
PAGE_SIZE 16384
DEFAULT CHARACTER SET ISO8859_1 COLLATION ISO8859_1;



/******************************************************************************/
/****                                Tables                                ****/
/******************************************************************************/



CREATE TABLE STL_DISPATCH_LINES (
    ID               INTEGER NOT NULL,
    DISPATCH_ID      INTEGER NOT NULL,
    CODIGO_PRODUCTO  VARCHAR(50),
    NOMBRE_PRODUCTO  VARCHAR(255),
    ALMACEN          VARCHAR(20),
    CANTIDAD_UMB     DECIMAL(18,6),
    LINE_NUM         INTEGER,
    UOM_CODE         VARCHAR(20),
    UOM_ENTRY        INTEGER,
    CREATED_AT       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE STL_DISPATCHES (
    ID               INTEGER NOT NULL,
    NUMERO_DESPACHO  INTEGER,
    NUMERO_BUSQUEDA  INTEGER,
    FECHA_CREACION   VARCHAR(50),
    FECHA_PICKING    TIMESTAMP,
    FECHA_CARGA      VARCHAR(50),
    CODIGO_CLIENTE   VARCHAR(50),
    NOMBRE_CLIENTE   VARCHAR(255),
    TIPO_DESPACHO    INTEGER NOT NULL,
    CREATED_AT       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SYNC_STATUS      VARCHAR(20) DEFAULT 'PENDING',
    LAST_SYNC_AT     TIMESTAMP
);

CREATE TABLE STL_GOODS_RECEIPT_LINES (
    ID                    INTEGER NOT NULL,
    RECEIPT_ID            INTEGER NOT NULL,
    CODIGO_PRODUCTO       VARCHAR(50),
    NOMBRE_PRODUCTO       VARCHAR(255),
    CODIGO_FAMILIA        INTEGER,
    NOMBRE_FAMILIA        VARCHAR(100),
    CANTIDAD              DECIMAL(18,6),
    UNIDAD_DE_MEDIDA_UMB  VARCHAR(20),
    LINE_NUM              INTEGER,
    UOM_ENTRY             INTEGER,
    UOM_CODE              VARCHAR(20),
    DIAS_VENCIMIENTO      INTEGER,
    CREATED_AT            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE STL_GOODS_RECEIPTS (
    ID                INTEGER NOT NULL,
    NUMERO_DOCUMENTO  INTEGER,
    NUMERO_BUSQUEDA   INTEGER,
    FECHA             TIMESTAMP,
    TIPO_RECEPCION    INTEGER,
    CODIGO_SUPLIDOR   VARCHAR(50),
    NOMBRE_SUPLIDOR   VARCHAR(255),
    CREATED_AT        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SYNC_STATUS       VARCHAR(20) DEFAULT 'PENDING',
    LAST_SYNC_AT      TIMESTAMP
);

CREATE TABLE STL_ITEMS (
    ID                     INTEGER NOT NULL,
    CODIGO_PRODUCTO        VARCHAR(50),
    DESCRIPCION_PRODUCTO   VARCHAR(255),
    CODIGO_PRODUCTO_ERP    VARCHAR(50),
    CODIGO_FAMILIA         INTEGER,
    NOMBRE_FAMILIA         VARCHAR(100),
    DIAS_VENCIMIENTO       INTEGER,
    CODIGO_UMB             VARCHAR(20),
    DESCRIPCION_UMB        VARCHAR(100),
    CODIGO_FORMA_EMBALAJE  VARCHAR(20),
    NOMBRE_FORMA_EMBALAJE  VARCHAR(100),
    CREATED_AT             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SYNC_STATUS            VARCHAR(20) DEFAULT 'PENDING',
    LAST_SYNC_AT           TIMESTAMP
);

CREATE TABLE STL_SYNC_CONFIG (
    ID                     INTEGER NOT NULL,
    ENTITY_TYPE            VARCHAR(50) NOT NULL,
    SYNC_ENABLED           VARCHAR(1) DEFAULT 'Y',
    SYNC_INTERVAL_MINUTES  INTEGER DEFAULT 60,
    LAST_SYNC_AT           TIMESTAMP,
    NEXT_SYNC_AT           TIMESTAMP,
    BATCH_SIZE             INTEGER DEFAULT 100,
    MAX_RETRIES            INTEGER DEFAULT 3,
    API_ENDPOINT           VARCHAR(255),
    CREATED_AT             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE STL_SYNC_LOG (
    ID               INTEGER NOT NULL,
    ENTITY_TYPE      VARCHAR(50) NOT NULL,
    ENTITY_ID        VARCHAR(100),
    OPERATION        VARCHAR(20) NOT NULL,
    STATUS           VARCHAR(20) NOT NULL,
    ERROR_MESSAGE    BLOB SUB_TYPE TEXT SEGMENT SIZE 80,
    SYNC_DATE        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PROCESSING_TIME  INTEGER,
    RETRY_COUNT      INTEGER DEFAULT 0,
    LAST_RETRY_AT    TIMESTAMP
);



/******************************************************************************/
/****                             Primary keys                             ****/
/******************************************************************************/

ALTER TABLE STL_DISPATCHES ADD CONSTRAINT PK_STL_DISPATCHES PRIMARY KEY (ID);
ALTER TABLE STL_DISPATCH_LINES ADD CONSTRAINT PK_STL_DISPATCH_LINES PRIMARY KEY (ID);
ALTER TABLE STL_GOODS_RECEIPTS ADD CONSTRAINT PK_STL_GOODS_RECEIPTS PRIMARY KEY (ID);
ALTER TABLE STL_GOODS_RECEIPT_LINES ADD CONSTRAINT PK_STL_GOODS_RECEIPT_LINES PRIMARY KEY (ID);
ALTER TABLE STL_ITEMS ADD CONSTRAINT PK_STL_ITEMS PRIMARY KEY (ID);
ALTER TABLE STL_SYNC_CONFIG ADD CONSTRAINT PK_STL_SYNC_CONFIG PRIMARY KEY (ID);
ALTER TABLE STL_SYNC_LOG ADD CONSTRAINT PK_STL_SYNC_LOG PRIMARY KEY (ID);


/******************************************************************************/
/****                             Foreign keys                             ****/
/******************************************************************************/

ALTER TABLE STL_DISPATCH_LINES ADD CONSTRAINT FK_STL_DISPATCH_LINES FOREIGN KEY (DISPATCH_ID) REFERENCES STL_DISPATCHES (ID);
ALTER TABLE STL_GOODS_RECEIPT_LINES ADD CONSTRAINT FK_STL_GOODS_RECEIPT_LINES FOREIGN KEY (RECEIPT_ID) REFERENCES STL_GOODS_RECEIPTS (ID);


/******************************************************************************/
/****                               Indices                                ****/
/******************************************************************************/

CREATE INDEX IDX_STL_DISPATCH_CLIENT ON STL_DISPATCHES (CODIGO_CLIENTE);
CREATE INDEX IDX_STL_DISPATCH_DATE ON STL_DISPATCHES (FECHA_PICKING);
CREATE INDEX IDX_STL_DISPATCH_NUM ON STL_DISPATCHES (NUMERO_DESPACHO);
CREATE INDEX IDX_STL_DISPATCH_SYNC ON STL_DISPATCHES (SYNC_STATUS, LAST_SYNC_AT);
CREATE INDEX IDX_STL_DISPATCH_TYPE ON STL_DISPATCHES (TIPO_DESPACHO);
CREATE INDEX IDX_STL_DISPATCH_LINES_DISPATCH ON STL_DISPATCH_LINES (DISPATCH_ID);
CREATE INDEX IDX_STL_DISPATCH_LINES_PRODUCT ON STL_DISPATCH_LINES (CODIGO_PRODUCTO);
CREATE INDEX IDX_STL_RECEIPT_DATE ON STL_GOODS_RECEIPTS (FECHA);
CREATE INDEX IDX_STL_RECEIPT_NUM ON STL_GOODS_RECEIPTS (NUMERO_DOCUMENTO);
CREATE INDEX IDX_STL_RECEIPT_SUPPLIER ON STL_GOODS_RECEIPTS (CODIGO_SUPLIDOR);
CREATE INDEX IDX_STL_RECEIPT_SYNC ON STL_GOODS_RECEIPTS (SYNC_STATUS, LAST_SYNC_AT);
CREATE INDEX IDX_STL_RECEIPT_TYPE ON STL_GOODS_RECEIPTS (TIPO_RECEPCION);
CREATE INDEX IDX_STL_RECEIPT_LINES_PRODUCT ON STL_GOODS_RECEIPT_LINES (CODIGO_PRODUCTO);
CREATE INDEX IDX_STL_RECEIPT_LINES_RECEIPT ON STL_GOODS_RECEIPT_LINES (RECEIPT_ID);
CREATE UNIQUE INDEX IDX_STL_ITEMS_CODIGO ON STL_ITEMS (CODIGO_PRODUCTO);
CREATE INDEX IDX_STL_ITEMS_FAMILIA ON STL_ITEMS (CODIGO_FAMILIA);
CREATE INDEX IDX_STL_ITEMS_SYNC ON STL_ITEMS (SYNC_STATUS, LAST_SYNC_AT);
CREATE UNIQUE INDEX IDX_STL_SYNC_CONFIG_ENTITY ON STL_SYNC_CONFIG (ENTITY_TYPE);
CREATE INDEX IDX_STL_SYNC_LOG_DATE ON STL_SYNC_LOG (SYNC_DATE);
CREATE INDEX IDX_STL_SYNC_LOG_ENTITY ON STL_SYNC_LOG (ENTITY_TYPE, ENTITY_ID);
CREATE INDEX IDX_STL_SYNC_LOG_STATUS ON STL_SYNC_LOG (STATUS);
