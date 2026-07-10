-- ============================================
-- HomeOS - Units
-- ============================================
-- Stores all units of measurement recognised
-- by HomeOS.
-- ============================================

CREATE TABLE Units
(
    UnitID          BIGSERIAL,
    Name            CITEXT NOT NULL,
    Abbreviation    CITEXT NOT NULL,
    CreatedDate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedDate     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsActive        BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT PK_Units
        PRIMARY KEY (UnitID),

    CONSTRAINT UQ_Units_Name
        UNIQUE (Name),

    CONSTRAINT UQ_Units_Abbreviation
        UNIQUE (Abbreviation),

    CONSTRAINT CK_Units_Name_NotBlank
        CHECK (LENGTH(TRIM(Name)) > 0),

    CONSTRAINT CK_Units_Abbreviation_NotBlank
        CHECK (LENGTH(TRIM(Abbreviation)) > 0)
);