from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.database import get_connection


router = APIRouter(
    prefix="/recipe-ingredients",
    tags=["Recipe Ingredients"],
)


# ==========================
# Pydantic Models
# ==========================

class RecipeIngredientCreate(BaseModel):
    recipe_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=3,
    )
    unit_id: int = Field(gt=0)
    optional: bool = False


class RecipeIngredientUpdate(BaseModel):
    quantity: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=3,
    )
    unit_id: int = Field(gt=0)
    optional: bool = False


class RecipeIngredientResponse(BaseModel):
    recipe_ingredient_id: int
    recipe_id: int
    recipe_name: str
    product_id: int
    product_name: str
    quantity: float
    unit_id: int
    unit_name: str
    optional: bool


# ==========================
# Helper Function
# ==========================

def recipe_ingredient_to_dict(row) -> dict:
    return {
        "recipe_ingredient_id": row[0],
        "recipe_id": row[1],
        "recipe_name": row[2],
        "product_id": row[3],
        "product_name": row[4],
        "quantity": float(row[5]),
        "unit_id": row[6],
        "unit_name": row[7],
        "optional": row[8],
    }


# ==========================
# GET ALL RECIPE INGREDIENTS
# ==========================

@router.get(
    "",
    response_model=list[RecipeIngredientResponse],
)
def get_recipe_ingredients():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ri.recipeingredientid,
                    ri.recipeid,
                    r.recipename,
                    ri.productid,
                    p.productname,
                    ri.quantity,
                    ri.unitid,
                    u.unitname,
                    ri.optional
                FROM recipeingredient ri
                INNER JOIN recipe r
                    ON ri.recipeid = r.recipeid
                INNER JOIN products p
                    ON ri.productid = p.productid
                INNER JOIN units u
                    ON ri.unitid = u.unitid
                ORDER BY
                    r.recipename,
                    p.productname;
                """
            )

            recipe_ingredients = cursor.fetchall()

    return [
        recipe_ingredient_to_dict(row)
        for row in recipe_ingredients
    ]


# ==========================
# GET INGREDIENTS FOR ONE RECIPE
# ==========================

@router.get(
    "/recipe/{recipe_id}",
    response_model=list[RecipeIngredientResponse],
)
def get_ingredients_for_recipe(recipe_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT recipeid
                FROM recipe
                WHERE recipeid = %s;
                """,
                (recipe_id,),
            )

            recipe = cursor.fetchone()

            if recipe is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recipe not found",
                )

            cursor.execute(
                """
                SELECT
                    ri.recipeingredientid,
                    ri.recipeid,
                    r.recipename,
                    ri.productid,
                    p.productname,
                    ri.quantity,
                    ri.unitid,
                    u.unitname,
                    ri.optional
                FROM recipeingredient ri
                INNER JOIN recipe r
                    ON ri.recipeid = r.recipeid
                INNER JOIN products p
                    ON ri.productid = p.productid
                INNER JOIN units u
                    ON ri.unitid = u.unitid
                WHERE ri.recipeid = %s
                ORDER BY
                    ri.optional,
                    p.productname;
                """,
                (recipe_id,),
            )

            recipe_ingredients = cursor.fetchall()

    return [
        recipe_ingredient_to_dict(row)
        for row in recipe_ingredients
    ]


# ==========================
# GET SINGLE RECIPE INGREDIENT
# ==========================

@router.get(
    "/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
)
def get_recipe_ingredient(recipe_ingredient_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ri.recipeingredientid,
                    ri.recipeid,
                    r.recipename,
                    ri.productid,
                    p.productname,
                    ri.quantity,
                    ri.unitid,
                    u.unitname,
                    ri.optional
                FROM recipeingredient ri
                INNER JOIN recipe r
                    ON ri.recipeid = r.recipeid
                INNER JOIN products p
                    ON ri.productid = p.productid
                INNER JOIN units u
                    ON ri.unitid = u.unitid
                WHERE ri.recipeingredientid = %s;
                """,
                (recipe_ingredient_id,),
            )

            recipe_ingredient = cursor.fetchone()

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    return recipe_ingredient_to_dict(recipe_ingredient)


# ==========================
# CREATE RECIPE INGREDIENT
# ==========================

@router.post(
    "",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recipe_ingredient(
    ingredient: RecipeIngredientCreate,
):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO recipeingredient
                    (
                        recipeid,
                        productid,
                        quantity,
                        unitid,
                        optional
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING recipeingredientid;
                    """,
                    (
                        ingredient.recipe_id,
                        ingredient.product_id,
                        ingredient.quantity,
                        ingredient.unit_id,
                        ingredient.optional,
                    ),
                )

                recipe_ingredient_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT
                        ri.recipeingredientid,
                        ri.recipeid,
                        r.recipename,
                        ri.productid,
                        p.productname,
                        ri.quantity,
                        ri.unitid,
                        u.unitname,
                        ri.optional
                    FROM recipeingredient ri
                    INNER JOIN recipe r
                        ON ri.recipeid = r.recipeid
                    INNER JOIN products p
                        ON ri.productid = p.productid
                    INNER JOIN units u
                        ON ri.unitid = u.unitid
                    WHERE ri.recipeingredientid = %s;
                    """,
                    (recipe_ingredient_id,),
                )

                created_ingredient = cursor.fetchone()

        return recipe_ingredient_to_dict(created_ingredient)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This ingredient already exists in the recipe",
        )

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe, product, or unit not found",
        )


# ==========================
# UPDATE RECIPE INGREDIENT
# ==========================

@router.put(
    "/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
)
def update_recipe_ingredient(
    recipe_ingredient_id: int,
    ingredient: RecipeIngredientUpdate,
):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE recipeingredient
                    SET
                        quantity = %s,
                        unitid = %s,
                        optional = %s
                    WHERE recipeingredientid = %s
                    RETURNING recipeingredientid;
                    """,
                    (
                        ingredient.quantity,
                        ingredient.unit_id,
                        ingredient.optional,
                        recipe_ingredient_id,
                    ),
                )

                updated = cursor.fetchone()

                if updated is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Recipe ingredient not found",
                    )

                cursor.execute(
                    """
                    SELECT
                        ri.recipeingredientid,
                        ri.recipeid,
                        r.recipename,
                        ri.productid,
                        p.productname,
                        ri.quantity,
                        ri.unitid,
                        u.unitname,
                        ri.optional
                    FROM recipeingredient ri
                    INNER JOIN recipe r
                        ON ri.recipeid = r.recipeid
                    INNER JOIN products p
                        ON ri.productid = p.productid
                    INNER JOIN units u
                        ON ri.unitid = u.unitid
                    WHERE ri.recipeingredientid = %s;
                    """,
                    (recipe_ingredient_id,),
                )

                updated_ingredient = cursor.fetchone()

        return recipe_ingredient_to_dict(updated_ingredient)

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit not found",
        )


# ==========================
# DELETE RECIPE INGREDIENT
# ==========================

@router.delete(
    "/{recipe_ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recipe_ingredient(recipe_ingredient_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM recipeingredient
                WHERE recipeingredientid = %s
                RETURNING recipeingredientid;
                """,
                (recipe_ingredient_id,),
            )

            deleted_ingredient = cursor.fetchone()

    if deleted_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)