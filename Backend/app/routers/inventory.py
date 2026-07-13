from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.database import get_connection


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


# ==========================
# Pydantic Models
# ==========================

class InventoryCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0)


class InventoryUpdate(BaseModel):
    quantity: float = Field(ge=0)


class InventoryResponse(BaseModel):
    inventory_id: int
    product_id: int
    quantity: float


# ==========================
# Helper Function
# ==========================

def inventory_to_dict(row) -> dict:
    return {
        "inventory_id": row[0],
        "product_id": row[1],
        "quantity": float(row[2]),
    }


# ==========================
# GET ALL INVENTORY
# ==========================

@router.get("", response_model=list[InventoryResponse])
def get_inventory():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    inventoryid,
                    productid,
                    quantity
                FROM inventory
                ORDER BY inventoryid;
                """
            )

            inventory = cursor.fetchall()

    return [inventory_to_dict(row) for row in inventory]


# ==========================
# GET SINGLE INVENTORY ITEM
# ==========================

@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory_item(inventory_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    inventoryid,
                    productid,
                    quantity
                FROM inventory
                WHERE inventoryid = %s;
                """,
                (inventory_id,),
            )

            item = cursor.fetchone()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return inventory_to_dict(item)


# ==========================
# CREATE INVENTORY ITEM
# ==========================

@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory_item(item: InventoryCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO inventory
                    (
                        productid,
                        quantity
                    )
                    VALUES
                    (
                        %s,
                        %s
                    )
                    RETURNING
                        inventoryid,
                        productid,
                        quantity;
                    """,
                    (
                        item.product_id,
                        item.quantity,
                    ),
                )

                created_item = cursor.fetchone()

        return inventory_to_dict(created_item)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product already exists in inventory",
        )

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product does not exist",
        )


# ==========================
# UPDATE INVENTORY
# ==========================

@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory_item(
    inventory_id: int,
    item: InventoryUpdate,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE inventory
                SET
                    quantity = %s
                WHERE inventoryid = %s
                RETURNING
                    inventoryid,
                    productid,
                    quantity;
                """,
                (
                    item.quantity,
                    inventory_id,
                ),
            )

            updated_item = cursor.fetchone()

    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return inventory_to_dict(updated_item)


# ==========================
# DELETE INVENTORY ITEM
# ==========================

@router.delete(
    "/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_inventory_item(inventory_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM inventory
                WHERE inventoryid = %s
                RETURNING inventoryid;
                """,
                (inventory_id,),
            )

            deleted_item = cursor.fetchone()

    if deleted_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)