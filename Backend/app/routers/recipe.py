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
# Helper Function
# ==========================

def recipe_to_dict(row):
    return {
        "recipe_id": row[0],
        "recipe_name": row[1],
        "category": row[2],
        "instructions": row[3],
        "notes": row[4],
    }


# ==========================
# GET ALL
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
# GET ONE
# ==========================

@router.get("/{recipe_id}", response_model=RecipeResponse)
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
            status_code=404,
            detail="Recipe not found",
        )

    return recipe_to_dict(recipe)


# ==========================
# CREATE
# ==========================

@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recipe(recipe: RecipeCreate):
    recipe_name = recipe.recipe_name.strip()
    category = recipe.category.strip()

    if not recipe_name:
        raise HTTPException(
            status_code=422,
            detail="Recipe name cannot be blank",
        )

    if not category:
        raise HTTPException(
            status_code=422,
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
                        recipe.instructions,
                        recipe.notes,
                    ),
                )

                created = cursor.fetchone()

        return recipe_to_dict(created)

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="A recipe with this name already exists",
        )


# ==========================
# UPDATE
# ==========================

@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe: RecipeUpdate):
    recipe_name = recipe.recipe_name.strip()
    category = recipe.category.strip()

    if not recipe_name:
        raise HTTPException(
            status_code=422,
            detail="Recipe name cannot be blank",
        )

    if not category:
        raise HTTPException(
            status_code=422,
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
                        recipe.instructions,
                        recipe.notes,
                        recipe_id,
                    ),
                )

                updated = cursor.fetchone()

        if updated is None:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found",
            )

        return recipe_to_dict(updated)

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="A recipe with this name already exists",
        )


# ==========================
# DELETE
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

            deleted = cursor.fetchone()

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)