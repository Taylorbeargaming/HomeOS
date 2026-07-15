-- =====================================================================
-- HomeOS - Complete corrected V1 schema
-- Intended for a NEW EMPTY PostgreSQL database.
-- This script does not drop or alter existing objects.
-- =====================================================================

BEGIN;


-- ============================================
-- HomeOS - PostgreSQL extensions
-- Run first.
-- ============================================

CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================
-- HomeOS - Units
-- Units are created before Products because
-- Products reference a default UnitID.
-- ============================================

CREATE TABLE units
(
    unitid          BIGSERIAL,
    unitname        CITEXT NOT NULL,
    abbreviation    CITEXT NOT NULL,
    createddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    isactive        BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT pk_units
        PRIMARY KEY (unitid),

    CONSTRAINT uq_units_unitname
        UNIQUE (unitname),

    CONSTRAINT uq_units_abbreviation
        UNIQUE (abbreviation),

    CONSTRAINT ck_units_unitname_notblank
        CHECK (CHAR_LENGTH(BTRIM(unitname::TEXT)) > 0),

    CONSTRAINT ck_units_abbreviation_notblank
        CHECK (CHAR_LENGTH(BTRIM(abbreviation::TEXT)) > 0)
);


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


-- ============================================
-- HomeOS - Shopping Lists
-- Stores one shopping session/list. List names
-- are intentionally not unique because names
-- such as "Weekly Shop" may be reused.
-- ============================================

CREATE TABLE shoppinglist
(
    shoppinglistid  BIGSERIAL,
    listname        VARCHAR(100) NOT NULL,
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    completeddate   TIMESTAMPTZ,
    createddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateddate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_shoppinglist
        PRIMARY KEY (shoppinglistid),

    CONSTRAINT ck_shoppinglist_listname_notblank
        CHECK (CHAR_LENGTH(BTRIM(listname)) > 0),

    CONSTRAINT ck_shoppinglist_completeddate
        CHECK (completed OR completeddate IS NULL)
);


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


-- ============================================
-- HomeOS - Recipes
-- Category remains constrained text rather than
-- a PostgreSQL enum so categories can evolve
-- without a database type migration.
-- ============================================

CREATE TABLE recipe
(
    recipeid         BIGSERIAL,
    recipename       CITEXT NOT NULL,
    category         VARCHAR(50) NOT NULL,
    instructions     TEXT,
    notes            TEXT,
    createddate      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updateddate      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_recipe
        PRIMARY KEY (recipeid),

    CONSTRAINT uq_recipe_recipename
        UNIQUE (recipename),

    CONSTRAINT ck_recipe_recipename_notblank
        CHECK (CHAR_LENGTH(BTRIM(recipename::TEXT)) > 0),

    CONSTRAINT ck_recipe_category_notblank
        CHECK (CHAR_LENGTH(BTRIM(category)) > 0)
);


-- ============================================
-- HomeOS - Recipe Ingredients
-- An ingredient may use a unit different from
-- the Product's inventory/default unit.
-- ============================================

CREATE TABLE recipeingredient
(
    recipeingredientid  BIGSERIAL,
    recipeid            BIGINT NOT NULL,
    productid           BIGINT NOT NULL,
    quantity            NUMERIC(12,3) NOT NULL,
    unitid              BIGINT NOT NULL,
    optional            BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_recipeingredient
        PRIMARY KEY (recipeingredientid),

    CONSTRAINT fk_recipeingredient_recipe
        FOREIGN KEY (recipeid)
        REFERENCES recipe(recipeid)
        ON DELETE CASCADE,

    CONSTRAINT fk_recipeingredient_product
        FOREIGN KEY (productid)
        REFERENCES products(productid)
        ON DELETE RESTRICT,

    CONSTRAINT fk_recipeingredient_unit
        FOREIGN KEY (unitid)
        REFERENCES units(unitid)
        ON DELETE RESTRICT,

    CONSTRAINT uq_recipeingredient_recipe_product
        UNIQUE (recipeid, productid),

    CONSTRAINT ck_recipeingredient_quantity_positive
        CHECK (quantity > 0)
);

CREATE INDEX idx_recipeingredient_productid
    ON recipeingredient (productid);

CREATE INDEX idx_recipeingredient_unitid
    ON recipeingredient (unitid);


-- ============================================
-- HomeOS - Timestamp and completion triggers
-- Run after all tables have been created.
-- ============================================

CREATE OR REPLACE FUNCTION set_updateddate()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    NEW.updateddate = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_units_updateddate
BEFORE UPDATE ON units
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_products_updateddate
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_shoppinglist_updateddate
BEFORE UPDATE ON shoppinglist
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_shoppinglistitem_updateddate
BEFORE UPDATE ON shoppinglistitem
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_inventory_updateddate
BEFORE UPDATE ON inventory
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_recipe_updateddate
BEFORE UPDATE ON recipe
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE OR REPLACE FUNCTION set_shoppinglist_completeddate()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.completed THEN
        IF TG_OP = 'INSERT' THEN
            NEW.completeddate = COALESCE(NEW.completeddate, CURRENT_TIMESTAMP);
        ELSE
            NEW.completeddate = COALESCE(NEW.completeddate, OLD.completeddate, CURRENT_TIMESTAMP);
        END IF;
    ELSE
        NEW.completeddate = NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_shoppinglist_completeddate
BEFORE INSERT OR UPDATE OF completed, completeddate ON shoppinglist
FOR EACH ROW
EXECUTE FUNCTION set_shoppinglist_completeddate();


-- ============================================
-- HomeOS - Initial units
-- Safe to run more than once.
-- ============================================

INSERT INTO units (unitname, abbreviation)
VALUES
    ('Each', 'ea'),
    ('Gram', 'g'),
    ('Kilogram', 'kg'),
    ('Millilitre', 'ml'),
    ('Litre', 'L')
ON CONFLICT (unitname)
DO UPDATE SET
    abbreviation = EXCLUDED.abbreviation,
    isactive = TRUE;

COMMIT;

-- Build completed. Run reference/verify_schema.sql to inspect the result.
