CREATE TABLE InventoryTransaction (
    TransactionID UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    InventoryID BIGINT NOT NULL
    REFERENCES Inventory(InventoryID)
    ON DELETE CASCADE,

    QuantityChange NUMERIC(10,2) NOT NULL,
    CHECK (QuantityChange <> 0),

    TransactionType VARCHAR(30) NOT NULL CHECK (
        TransactionType IN (
            'Purchase',
            'Consumption',
            'Waste',
            'Adjustment',
            'TransferIn',
            'TransferOut',
            'InitialStock'
        )
    ),

    Notes TEXT,

    TransactionDate TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CreatedAt TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX idx_inventorytransaction_inventory
    	ON InventoryTransaction (InventoryID);

    CREATE INDEX idx_inventorytransaction_date
    	ON InventoryTransaction (TransactionDate);

    CREATE INDEX idx_inventorytransaction_type
    	ON InventoryTransaction (TransactionType);