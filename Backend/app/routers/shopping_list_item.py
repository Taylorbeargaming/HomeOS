from typing import Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.database import get_connection


router = APIRouter(
    prefix="/shopping-list-items",
    tags=["Shopping List Items"],
)


# ==========================
# Pydantic Models
# ==========================

class ShoppingListItemCreate(BaseModel):
    shopping_list_id: int
    product_id: int
    quantity: float = Field(gt=0)
    notes: Optional[str] = None


class ShoppingListItemUpdate(BaseModel):
    quantity: float = Field(gt=0)
    completed: bool
    notes: Optional[str] = None


class ShoppingListItemResponse(BaseModel):
    shopping_list_item_id: int
    shopping_list_id: int
    product_id: int
    quantity: float
    completed: bool
    notes: Optional[str]


# ==========================
# Helper Function
# ==========================

def shopping_list_item_to_dict(row):
    return {
        "shopping_list_item_id": row[0],
        "shopping_list_id": row[1],
        "product_id": row[2],
        "quantity": float(row[3]),
        "completed": row[4],
        "notes": row[5],
    }


# ==========================
# GET ALL
# ==========================

@router.get("", response_model=list[ShoppingListItemResponse])
def get_shopping_list_items():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    shoppinglistitemid,
                    shoppinglistid,
                    productid,
                    quantity,
                    completed,
                    notes
                FROM shoppinglistitem
                ORDER BY shoppinglistitemid;
                """
            )

            rows = cursor.fetchall()

    return [shopping_list_item_to_dict(row) for row in rows]


# ==========================
# GET ONE
# ==========================

@router.get("/{shopping_list_item_id}", response_model=ShoppingListItemResponse)
def get_shopping_list_item(shopping_list_item_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    shoppinglistitemid,
                    shoppinglistid,
                    productid,
                    quantity,
                    completed,
                    notes
                FROM shoppinglistitem
                WHERE shoppinglistitemid = %s;
                """,
                (shopping_list_item_id,),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Shopping list item not found",
        )

    return shopping_list_item_to_dict(row)


# ==========================
# CREATE
# ==========================

@router.post(
    "",
    response_model=ShoppingListItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shopping_list_item(item: ShoppingListItemCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO shoppinglistitem
                    (
                        shoppinglistid,
                        productid,
                        quantity,
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
                        shoppinglistitemid,
                        shoppinglistid,
                        productid,
                        quantity,
                        completed,
                        notes;
                    """,
                    (
                        item.shopping_list_id,
                        item.product_id,
                        item.quantity,
                        item.notes,
                    ),
                )

                created = cursor.fetchone()

        return shopping_list_item_to_dict(created)

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="This product is already on the shopping list",
        )

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="Shopping list or product not found",
        )


# ==========================
# UPDATE
# ==========================

@router.put("/{shopping_list_item_id}", response_model=ShoppingListItemResponse)
def update_shopping_list_item(
    shopping_list_item_id: int,
    item: ShoppingListItemUpdate,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE shoppinglistitem
                SET
                    quantity = %s,
                    completed = %s,
                    notes = %s
                WHERE shoppinglistitemid = %s
                RETURNING
                    shoppinglistitemid,
                    shoppinglistid,
                    productid,
                    quantity,
                    completed,
                    notes;
                """,
                (
                    item.quantity,
                    item.completed,
                    item.notes,
                    shopping_list_item_id,
                ),
            )

            updated = cursor.fetchone()

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Shopping list item not found",
        )

    return shopping_list_item_to_dict(updated)


# ==========================
# DELETE
# ==========================

@router.delete(
    "/{shopping_list_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_shopping_list_item(shopping_list_item_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM shoppinglistitem
                WHERE shoppinglistitemid = %s
                RETURNING shoppinglistitemid;
                """,
                (shopping_list_item_id,),
            )

            deleted = cursor.fetchone()

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Shopping list item not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)