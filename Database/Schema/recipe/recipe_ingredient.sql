CREATE TABLE RecipeIngredient (
    RecipeIngredientID SERIAL PRIMARY KEY,

    RecipeID INTEGER NOT NULL,
    ProductID INTEGER NOT NULL,
    Quantity NUMERIC(10,2) NOT NULL,
    UnitID INTEGER NOT NULL,

    Optional BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_recipe
        FOREIGN KEY (RecipeID)
        REFERENCES Recipe(RecipeID)
        ON DELETE CASCADE,

    CONSTRAINT fk_product
        FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID),

    CONSTRAINT fk_unit
        FOREIGN KEY (UnitID)
        REFERENCES Units(UnitID),

    CONSTRAINT uq_recipe_product
        UNIQUE (RecipeID, ProductID)
);