-- ============================================
-- HomeOS - Products
-- ============================================
-- Stores every product known to HomeOS.
-- Products are generic and do not contain
-- inventory or shopping information.
-- Version: 1.0
-- ============================================
-- Version History
-- 11/07/2026 - Intial Version, table creation. Refer to DatabaseDesign.md for details.
-- ============================================

CREATE TABLE Products
(
    ProductID      BIGSERIAL,
    Name           CITEXT NOT NULL,
    Notes          TEXT,
    CreatedDate    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsActive       BOOLEAN NOT NULL DEFAULT TRUE,

	CONSTRAINT PK_Products PRIMARY KEY (ProductID),
    CONSTRAINT UQ_Product_Name UNIQUE (Name),
    CONSTRAINT CK_Product_Name_NotBlank CHECK (LENGTH(TRIM(Name)) > 0)
);