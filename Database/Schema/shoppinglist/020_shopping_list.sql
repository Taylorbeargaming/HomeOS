-- ============================================
-- HomeOS - Shopping List
-- ============================================
-- This is simply metadata about the list.
-- ============================================
-- Version: 1.0
-- ============================================
-- Version History
-- 11/07/2026 - Initial Version, table creation. Refer to DatabaseDesign.md for details.
-- ============================================

CREATE TABLE ShoppingList (
    ShoppingListID BIGSERIAL PRIMARY KEY,

    Name VARCHAR(100) NOT NULL UNIQUE
    CHECK (length(trim(Name)) > 0),

    Completed BOOLEAN NOT NULL DEFAULT FALSE,

    CreatedDate TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UpdatedDate TIMESTAMPTZ NOT NULL DEFAULT NOW()
);