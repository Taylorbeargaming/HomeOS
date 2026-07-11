CREATE TABLE ShoppingListItem (
    ShoppingListItemID BIGSERIAL PRIMARY KEY,

    ShoppingListID BIGINT NOT NULL
        REFERENCES ShoppingList(ShoppingListID)
        ON DELETE CASCADE,

    ProductID BIGINT NOT NULL
        REFERENCES Products(ProductID),

    Quantity NUMERIC(10,2) NOT NULL
        CHECK (Quantity > 0),

    Completed BOOLEAN NOT NULL DEFAULT FALSE,

    Notes TEXT,

    CreatedDate TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UpdatedDate TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_shoppinglistitem_list
    ON ShoppingListItem (ShoppingListID);

CREATE INDEX idx_shoppinglistitem_product
    ON ShoppingListItem (ProductID);

CREATE INDEX idx_shoppinglistitem_completed
    ON ShoppingListItem (Completed);