from decimal import Decimal
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
    shopping_list_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=3,
    )
    notes: Optional[str] = None


class ShoppingListItemUpdate(BaseModel):
    quantity: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=3,
    )
    completed: bool
    notes: Optional[str] = None


class ShoppingListItemResponse(BaseModel):
    shopping_list_item_id: int
    shopping_list_id: int
    list_name: str
    product_id: int
    product_name: str
    quantity: float
    unit_name: str
    completed: bool
    notes: Optional[str]


# ==========================
# Helper Function
# ==========================

def shopping_list_item_to_dict(row) -> dict:
    return {
        "shopping_list_item_id": row[0],
        "shopping_list_id": row[1],
        "list_name": row[2],
        "product_id": row[3],
        "product_name": row[4],
        "quantity": float(row[5]),
        "unit_name": row[6],
        "completed": row[7],
        "notes": row[8],
    }


# ==========================
# GET ALL SHOPPING LIST ITEMS
# ==========================

@router.get(
    "",
    response_model=list[ShoppingListItemResponse],
)
def get_shopping_list_items():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    sli.shoppinglistitemid,
                    sli.shoppinglistid,
                    sl.listname,
                    sli.productid,
                    p.productname,
                    sli.quantity,
                    u.unitname,
                    sli.completed,
                    sli.notes
                FROM shoppinglistitem sli
                INNER JOIN shoppinglist sl
                    ON sli.shoppinglistid = sl.shoppinglistid
                INNER JOIN products p
                    ON sli.productid = p.productid
                INNER JOIN units u
                    ON p.unitid = u.unitid
                ORDER BY
                    sl.createddate DESC,
                    sli.shoppinglistitemid;
                """
            )

            shopping_list_items = cursor.fetchall()

    return [
        shopping_list_item_to_dict(row)
        for row in shopping_list_items
    ]


# ==========================
# GET ITEMS FOR ONE SHOPPING LIST
# ==========================

@router.get(
    "/list/{shopping_list_id}",
    response_model=list[ShoppingListItemResponse],
)
def get_items_for_shopping_list(shopping_list_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT shoppinglistid
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

            cursor.execute(
                """
                SELECT
                    sli.shoppinglistitemid,
                    sli.shoppinglistid,
                    sl.listname,
                    sli.productid,
                    p.productname,
                    sli.quantity,
                    u.unitname,
                    sli.completed,
                    sli.notes
                FROM shoppinglistitem sli
                INNER JOIN shoppinglist sl
                    ON sli.shoppinglistid = sl.shoppinglistid
                INNER JOIN products p
                    ON sli.productid = p.productid
                INNER JOIN units u
                    ON p.unitid = u.unitid
                WHERE sli.shoppinglistid = %s
                ORDER BY
                    sli.completed,
                    p.productname;
                """,
                (shopping_list_id,),
            )

            shopping_list_items = cursor.fetchall()

    return [
        shopping_list_item_to_dict(row)
        for row in shopping_list_items
    ]


# ==========================
# GET SINGLE SHOPPING LIST ITEM
# ==========================

@router.get(
    "/{shopping_list_item_id}",
    response_model=ShoppingListItemResponse,
)
def get_shopping_list_item(shopping_list_item_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    sli.shoppinglistitemid,
                    sli.shoppinglistid,
                    sl.listname,
                    sli.productid,
                    p.productname,
                    sli.quantity,
                    u.unitname,
                    sli.completed,
                    sli.notes
                FROM shoppinglistitem sli
                INNER JOIN shoppinglist sl
                    ON sli.shoppinglistid = sl.shoppinglistid
                INNER JOIN products p
                    ON sli.productid = p.productid
                INNER JOIN units u
                    ON p.unitid = u.unitid
                WHERE sli.shoppinglistitemid = %s;
                """,
                (shopping_list_item_id,),
            )

            shopping_list_item = cursor.fetchone()

    if shopping_list_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found",
        )

    return shopping_list_item_to_dict(shopping_list_item)


# ==========================
# CREATE SHOPPING LIST ITEM
# ==========================

@router.post(
    "",
    response_model=ShoppingListItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shopping_list_item(
    item: ShoppingListItemCreate,
):
    notes = item.notes.strip() if item.notes else None

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
                    RETURNING shoppinglistitemid;
                    """,
                    (
                        item.shopping_list_id,
                        item.product_id,
                        item.quantity,
                        notes,
                    ),
                )

                shopping_list_item_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT
                        sli.shoppinglistitemid,
                        sli.shoppinglistid,
                        sl.listname,
                        sli.productid,
                        p.productname,
                        sli.quantity,
                        u.unitname,
                        sli.completed,
                        sli.notes
                    FROM shoppinglistitem sli
                    INNER JOIN shoppinglist sl
                        ON sli.shoppinglistid = sl.shoppinglistid
                    INNER JOIN products p
                        ON sli.productid = p.productid
                    INNER JOIN units u
                        ON p.unitid = u.unitid
                    WHERE sli.shoppinglistitemid = %s;
                    """,
                    (shopping_list_item_id,),
                )

                created_item = cursor.fetchone()

        return shopping_list_item_to_dict(created_item)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product is already on the shopping list",
        )

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shopping list or product not found",
        )


# ==========================
# UPDATE SHOPPING LIST ITEM
# ==========================

@router.put(
    "/{shopping_list_item_id}",
    response_model=ShoppingListItemResponse,
)
def update_shopping_list_item(
    shopping_list_item_id: int,
    item: ShoppingListItemUpdate,
):
    notes = item.notes.strip() if item.notes else None

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
                RETURNING shoppinglistitemid;
                """,
                (
                    item.quantity,
                    item.completed,
                    notes,
                    shopping_list_item_id,
                ),
            )

            updated = cursor.fetchone()

            if updated is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Shopping list item not found",
                )

            cursor.execute(
                """
                SELECT
                    sli.shoppinglistitemid,
                    sli.shoppinglistid,
                    sl.listname,
                    sli.productid,
                    p.productname,
                    sli.quantity,
                    u.unitname,
                    sli.completed,
                    sli.notes
                FROM shoppinglistitem sli
                INNER JOIN shoppinglist sl
                    ON sli.shoppinglistid = sl.shoppinglistid
                INNER JOIN products p
                    ON sli.productid = p.productid
                INNER JOIN units u
                    ON p.unitid = u.unitid
                WHERE sli.shoppinglistitemid = %s;
                """,
                (shopping_list_item_id,),
            )

            updated_item = cursor.fetchone()

    return shopping_list_item_to_dict(updated_item)


# ==========================
# DELETE SHOPPING LIST ITEM
# ==========================

@router.delete(
    "/{shopping_list_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_shopping_list_item(
    shopping_list_item_id: int,
):
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

            deleted_item = cursor.fetchone()

    if deleted_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)