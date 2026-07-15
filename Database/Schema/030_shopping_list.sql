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
