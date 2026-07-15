-- ============================================
-- HomeOS - Inventory Transactions
-- Immutable history of inventory quantity
-- changes. Inventory history must not disappear
-- when an Inventory row is deleted.
-- ============================================

CREATE TABLE inventorytransaction
(
    transactionid      UUID NOT NULL DEFAULT gen_random_uuid(),
    inventoryid        BIGINT NOT NULL,
    quantitychange     NUMERIC(12,3) NOT NULL,
    transactiontype    VARCHAR(30) NOT NULL,
    notes              TEXT,
    transactiondate    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    createddate        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_inventorytransaction
        PRIMARY KEY (transactionid),

    CONSTRAINT fk_inventorytransaction_inventory
        FOREIGN KEY (inventoryid)
        REFERENCES inventory(inventoryid)
        ON DELETE RESTRICT,

    CONSTRAINT ck_inventorytransaction_quantitychange_nonzero
        CHECK (quantitychange <> 0),

    CONSTRAINT ck_inventorytransaction_transactiontype
        CHECK
        (
            transactiontype IN
            (
                'Purchase',
                'Consumption',
                'Waste',
                'Adjustment',
                'TransferIn',
                'TransferOut',
                'InitialStock'
            )
        ),

    CONSTRAINT ck_inventorytransaction_quantitychange_sign
        CHECK
        (
            (transactiontype IN ('Purchase', 'TransferIn', 'InitialStock')
                AND quantitychange > 0)
            OR
            (transactiontype IN ('Consumption', 'Waste', 'TransferOut')
                AND quantitychange < 0)
            OR
            (transactiontype = 'Adjustment'
                AND quantitychange <> 0)
        )
);

CREATE INDEX idx_inventorytransaction_inventoryid
    ON inventorytransaction (inventoryid);

CREATE INDEX idx_inventorytransaction_transactiondate
    ON inventorytransaction (transactiondate DESC);
