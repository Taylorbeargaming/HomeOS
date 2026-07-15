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
