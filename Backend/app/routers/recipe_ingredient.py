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
    recipe_id: int
    product_id: int
    quantity: float = Field(gt=0)
    unit_id: int
    optional: bool = False


class RecipeIngredientUpdate(BaseModel):
    quantity: float = Field(gt=0)
    unit_id: int
    optional: bool = False


class RecipeIngredientResponse(BaseModel):
    recipe_ingredient_id: int
    recipe_id: int
    product_id: int
    quantity: float
    unit_id: int
    optional: bool


# ==========================
# Helper Function
# ==========================

def recipe_ingredient_to_dict(row):
    return {
        "recipe_ingredient_id": row[0],
        "recipe_id": row[1],
        "product_id": row[2],
        "quantity": float(row[3]),
        "unit_id": row[4],
        "optional": row[5],
    }


# ==========================
# GET ALL
# ==========================

@router.get("", response_model=list[RecipeIngredientResponse])
def get_recipe_ingredients():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    recipeingredientid,
                    recipeid,
                    productid,
                    quantity,
                    unitid,
                    optional
                FROM recipeingredient
                ORDER BY recipeid;
                """
            )

            rows = cursor.fetchall()

    return [recipe_ingredient_to_dict(row) for row in rows]


# ==========================
# GET ONE
# ==========================

@router.get("/{recipe_ingredient_id}", response_model=RecipeIngredientResponse)
def get_recipe_ingredient(recipe_ingredient_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    recipeingredientid,
                    recipeid,
                    productid,
                    quantity,
                    unitid,
                    optional
                FROM recipeingredient
                WHERE recipeingredientid = %s;
                """,
                (recipe_ingredient_id,),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe ingredient not found",
        )

    return recipe_ingredient_to_dict(row)


# ==========================
# CREATE
# ==========================

@router.post(
    "",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recipe_ingredient(ingredient: RecipeIngredientCreate):
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
                    RETURNING
                        recipeingredientid,
                        recipeid,
                        productid,
                        quantity,
                        unitid,
                        optional;
                    """,
                    (
                        ingredient.recipe_id,
                        ingredient.product_id,
                        ingredient.quantity,
                        ingredient.unit_id,
                        ingredient.optional,
                    ),
                )

                created = cursor.fetchone()

        return recipe_ingredient_to_dict(created)

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="This ingredient already exists in the recipe",
        )

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="Recipe, product or unit not found",
        )


# ==========================
# UPDATE
# ==========================

@router.put("/{recipe_ingredient_id}", response_model=RecipeIngredientResponse)
def update_recipe_ingredient(
    recipe_ingredient_id: int,
    ingredient: RecipeIngredientUpdate,
):
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
                RETURNING
                    recipeingredientid,
                    recipeid,
                    productid,
                    quantity,
                    unitid,
                    optional;
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
            status_code=404,
            detail="Recipe ingredient not found",
        )

    return recipe_ingredient_to_dict(updated)


# ==========================
# DELETE
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

            deleted = cursor.fetchone()

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe ingredient not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)