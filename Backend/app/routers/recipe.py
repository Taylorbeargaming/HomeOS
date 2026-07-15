from typing import Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import UniqueViolation

from app.database import get_connection


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# ==========================
# Pydantic Models
# ==========================

class RecipeCreate(BaseModel):
    recipe_name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=50)
    instructions: Optional[str] = None
    notes: Optional[str] = None


class RecipeUpdate(BaseModel):
    recipe_name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=50)
    instructions: Optional[str] = None
    notes: Optional[str] = None


class RecipeResponse(BaseModel):
    recipe_id: int
    recipe_name: str
    category: str
    instructions: Optional[str]
    notes: Optional[str]


# ==========================
# Helper Functions
# ==========================

def recipe_to_dict(row) -> dict:
    return {
        "recipe_id": row[0],
        "recipe_name": row[1],
        "category": row[2],
        "instructions": row[3],
        "notes": row[4],
    }


def clean_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned_value = value.strip()

    return cleaned_value or None


# ==========================
# GET ALL RECIPES
# ==========================

@router.get("", response_model=list[RecipeResponse])
def get_recipes():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    recipeid,
                    recipename,
                    category,
                    instructions,
                    notes
                FROM recipe
                ORDER BY recipename;
                """
            )

            recipes = cursor.fetchall()

    return [recipe_to_dict(row) for row in recipes]


# ==========================
# GET SINGLE RECIPE
# ==========================

@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
def get_recipe(recipe_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    recipeid,
                    recipename,
                    category,
                    instructions,
                    notes
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

    return recipe_to_dict(recipe)


# ==========================
# CREATE RECIPE
# ==========================

@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recipe(recipe: RecipeCreate):
    recipe_name = recipe.recipe_name.strip()
    category = recipe.category.strip()
    instructions = clean_optional_text(recipe.instructions)
    notes = clean_optional_text(recipe.notes)

    if not recipe_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Recipe name cannot be blank",
        )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category cannot be blank",
        )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO recipe
                    (
                        recipename,
                        category,
                        instructions,
                        notes
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING
                        recipeid,
                        recipename,
                        category,
                        instructions,
                        notes;
                    """,
                    (
                        recipe_name,
                        category,
                        instructions,
                        notes,
                    ),
                )

                created_recipe = cursor.fetchone()

        return recipe_to_dict(created_recipe)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A recipe with this name already exists",
        )


# ==========================
# UPDATE RECIPE
# ==========================

@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
):
    recipe_name = recipe.recipe_name.strip()
    category = recipe.category.strip()
    instructions = clean_optional_text(recipe.instructions)
    notes = clean_optional_text(recipe.notes)

    if not recipe_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Recipe name cannot be blank",
        )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category cannot be blank",
        )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE recipe
                    SET
                        recipename = %s,
                        category = %s,
                        instructions = %s,
                        notes = %s
                    WHERE recipeid = %s
                    RETURNING
                        recipeid,
                        recipename,
                        category,
                        instructions,
                        notes;
                    """,
                    (
                        recipe_name,
                        category,
                        instructions,
                        notes,
                        recipe_id,
                    ),
                )

                updated_recipe = cursor.fetchone()

        if updated_recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

        return recipe_to_dict(updated_recipe)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A recipe with this name already exists",
        )


# ==========================
# DELETE RECIPE
# ==========================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recipe(recipe_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM recipe
                WHERE recipeid = %s
                RETURNING recipeid;
                """,
                (recipe_id,),
            )

            deleted_recipe = cursor.fetchone()

    if deleted_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)