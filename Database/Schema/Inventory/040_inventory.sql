-- ============================================
-- HomeOS - Inventory
-- ============================================
-- Stores inventory information for each product.
-- Historical changes are stored separately in
-- InventoryTransactions.
-- Version: 1.0
-- ============================================
-- Version History
-- 11/07/2026 - Intial Version, table creation. Refer to DatabaseDesign.md for details.
-- ============================================

CREATE TABLE Inventory
(
    InventoryID     BIGSERIAL,
    ProductID       BIGINT NOT NULL,
    Quantity        NUMERIC(10,2) NOT NULL,
    UnitID          BIGINT NOT NULL,
    CreatedDate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT PK_Inventory
        PRIMARY KEY (InventoryID),

    CONSTRAINT FK_Inventory_Product
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID),
        ON DELETE RESTRICT,

    CONSTRAINT FK_Inventory_Unit
        FOREIGN KEY (UnitID)
        REFERENCES Units(UnitID),
        On DELETE RESTRICT,

    CONSTRAINT UQ_Inventory_Product
        UNIQUE (ProductID),

    CONSTRAINT CK_Inventory_Quantity
        CHECK (Quantity >= 0)
);