from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.database import get_connection


router = APIRouter(
    prefix="/shopping-lists",
    tags=["Shopping Lists"],
)


# ==========================
# Pydantic Models
# ==========================

class ShoppingListCreate(BaseModel):
    list_name: str = Field(min_length=1, max_length=100)


class ShoppingListUpdate(BaseModel):
    list_name: str = Field(min_length=1, max_length=100)
    completed: bool


class ShoppingListResponse(BaseModel):
    shopping_list_id: int
    list_name: str
    completed: bool


# ==========================
# Helper Function
# ==========================

def shopping_list_to_dict(row):
    return {
        "shopping_list_id": row[0],
        "list_name": row[1],
        "completed": row[2],
    }


# ==========================
# GET ALL
# ==========================

@router.get("", response_model=list[ShoppingListResponse])
def get_shopping_lists():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    shoppinglistid,
                    listname,
                    completed
                FROM shoppinglist
                ORDER BY createddate DESC;
                """
            )

            rows = cursor.fetchall()

    return [shopping_list_to_dict(row) for row in rows]


# ==========================
# GET ONE
# ==========================

@router.get("/{shopping_list_id}", response_model=ShoppingListResponse)
def get_shopping_list(shopping_list_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    shoppinglistid,
                    listname,
                    completed
                FROM shoppinglist
                WHERE shoppinglistid = %s;
                """,
                (shopping_list_id,),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Shopping list not found",
        )

    return shopping_list_to_dict(row)


# ==========================
# CREATE
# ==========================

@router.post(
    "",
    response_model=ShoppingListResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shopping_list(shopping_list: ShoppingListCreate):
    list_name = shopping_list.list_name.strip()

    if not list_name:
        raise HTTPException(
            status_code=422,
            detail="List name cannot be blank",
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO shoppinglist
                (
                    listname
                )
                VALUES
                (
                    %s
                )
                RETURNING
                    shoppinglistid,
                    listname,
                    completed;
                """,
                (list_name,),
            )

            created = cursor.fetchone()

    return shopping_list_to_dict(created)


# ==========================
# UPDATE
# ==========================

@router.put("/{shopping_list_id}", response_model=ShoppingListResponse)
def update_shopping_list(
    shopping_list_id: int,
    shopping_list: ShoppingListUpdate,
):
    list_name = shopping_list.list_name.strip()

    if not list_name:
        raise HTTPException(
            status_code=422,
            detail="List name cannot be blank",
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE shoppinglist
                SET
                    listname = %s,
                    completed = %s
                WHERE shoppinglistid = %s
                RETURNING
                    shoppinglistid,
                    listname,
                    completed;
                """,
                (
                    list_name,
                    shopping_list.completed,
                    shopping_list_id,
                ),
            )

            updated = cursor.fetchone()

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Shopping list not found",
        )

    return shopping_list_to_dict(updated)


# ==========================
# DELETE
# ==========================

@router.delete(
    "/{shopping_list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_shopping_list(shopping_list_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM shoppinglist
                WHERE shoppinglistid = %s
                RETURNING shoppinglistid;
                """,
                (shopping_list_id,),
            )

            deleted = cursor.fetchone()

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Shopping list not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)