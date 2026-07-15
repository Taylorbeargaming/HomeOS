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
