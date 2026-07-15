-- ============================================
-- HomeOS - Shopping List Items
-- Completed currently represents whether the
-- item has been purchased/ticked off.
-- ============================================

CREATE TABLE shoppinglistitem
(
    shoppinglistitemid  BIGSERIAL,
    shoppinglistid      BIGINT NOT NULL,
    productid           BIGINT NOT NULL,
    quantity            NUMERIC(12,3) NOT NULL,
    completed           BOOLEAN NOT NULL DEFAULT FALSE,
    notes               TEXT,
    createddate         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateddate         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_shoppinglistitem
        PRIMARY KEY (shoppinglistitemid),

    CONSTRAINT fk_shoppinglistitem_list
        FOREIGN KEY (shoppinglistid)
        REFERENCES shoppinglist(shoppinglistid)
        ON DELETE CASCADE,

    CONSTRAINT fk_shoppinglistitem_product
        FOREIGN KEY (productid)
        REFERENCES products(productid)
        ON DELETE RESTRICT,

    CONSTRAINT uq_shoppinglistitem_list_product
        UNIQUE (shoppinglistid, productid),

    CONSTRAINT ck_shoppinglistitem_quantity_positive
        CHECK (quantity > 0)
);

-- The unique constraint already provides an index beginning with
-- ShoppingListID. This separate index supports lookups by ProductID.
CREATE INDEX idx_shoppinglistitem_productid
    ON shoppinglistitem (productid);
