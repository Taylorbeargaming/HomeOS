from datetime import datetime
from typing import Optional

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
    completed_date: Optional[datetime]


# ==========================
# Helper Function
# ==========================

def shopping_list_to_dict(row) -> dict:
    return {
        "shopping_list_id": row[0],
        "list_name": row[1],
        "completed": row[2],
        "completed_date": row[3],
    }


# ==========================
# GET ALL SHOPPING LISTS
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
                    completed,
                    completeddate
                FROM shoppinglist
                ORDER BY createddate DESC;
                """
            )

            shopping_lists = cursor.fetchall()

    return [
        shopping_list_to_dict(row)
        for row in shopping_lists
    ]


# ==========================
# GET SINGLE SHOPPING LIST
# ==========================

@router.get(
    "/{shopping_list_id}",
    response_model=ShoppingListResponse,
)
def get_shopping_list(shopping_list_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    shoppinglistid,
                    listname,
                    completed,
                    completeddate
                FROM shoppinglist
                WHERE shoppinglistid = %s;
                """,
                (shopping_list_id,),
            )

            shopping_list = cursor.fetchone()

    if shopping_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    return shopping_list_to_dict(shopping_list)


# ==========================
# CREATE SHOPPING LIST
# ==========================

@router.post(
    "",
    response_model=ShoppingListResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shopping_list(
    shopping_list: ShoppingListCreate,
):
    list_name = shopping_list.list_name.strip()

    if not list_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
                    completed,
                    completeddate;
                """,
                (list_name,),
            )

            created_shopping_list = cursor.fetchone()

    return shopping_list_to_dict(created_shopping_list)


# ==========================
# UPDATE SHOPPING LIST
# ==========================

@router.put(
    "/{shopping_list_id}",
    response_model=ShoppingListResponse,
)
def update_shopping_list(
    shopping_list_id: int,
    shopping_list: ShoppingListUpdate,
):
    list_name = shopping_list.list_name.strip()

    if not list_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
                    completed,
                    completeddate;
                """,
                (
                    list_name,
                    shopping_list.completed,
                    shopping_list_id,
                ),
            )

            updated_shopping_list = cursor.fetchone()

    if updated_shopping_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    return shopping_list_to_dict(updated_shopping_list)


# ==========================
# DELETE SHOPPING LIST
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

            deleted_shopping_list = cursor.fetchone()

    if deleted_shopping_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)