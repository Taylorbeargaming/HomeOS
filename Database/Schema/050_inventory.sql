-- ============================================
-- HomeOS - Inventory
-- Stores current quantity only. The display
-- unit is obtained from Products.UnitID, so a
-- second UnitID is not stored here.
-- ============================================

CREATE TABLE inventory
(
    inventoryid     BIGSERIAL,
    productid       BIGINT NOT NULL,
    quantity        NUMERIC(12,3) NOT NULL DEFAULT 0,
    createddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_inventory
        PRIMARY KEY (inventoryid),

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (productid)
        REFERENCES products(productid)
        ON DELETE RESTRICT,

    CONSTRAINT uq_inventory_product
        UNIQUE (productid),

    CONSTRAINT ck_inventory_quantity_nonnegative
        CHECK (quantity >= 0)
);
