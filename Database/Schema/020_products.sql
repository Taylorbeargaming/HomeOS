-- ============================================
-- HomeOS - Products
-- A Product is a reusable item definition.
-- UnitID is the Product's default measurement
-- unit and is used when inventory is displayed.
-- ============================================

CREATE TABLE products
(
    productid       BIGSERIAL,
    productname     CITEXT NOT NULL,
    unitid          BIGINT NOT NULL,
    notes           TEXT,
    createddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    isactive        BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT pk_products
        PRIMARY KEY (productid),

    CONSTRAINT uq_products_productname
        UNIQUE (productname),

    CONSTRAINT ck_products_productname_notblank
        CHECK (CHAR_LENGTH(BTRIM(productname::TEXT)) > 0),

    CONSTRAINT fk_products_unit
        FOREIGN KEY (unitid)
        REFERENCES units(unitid)
        ON DELETE RESTRICT
);

CREATE INDEX idx_products_unitid
    ON products (unitid);
