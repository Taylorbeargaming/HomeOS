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
