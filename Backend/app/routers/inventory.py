from decimal import Decimal

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import (
    ForeignKeyViolation,
    RestrictViolation,
    UniqueViolation,
)

from app.database import get_connection


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


# ==========================
# Pydantic Models
# ==========================

class InventoryCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=3,
    )


class InventoryUpdate(BaseModel):
    quantity: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=3,
    )


class InventoryResponse(BaseModel):
    inventory_id: int
    product_id: int
    product_name: str
    quantity: float
    unit_id: int
    unit_name: str


# ==========================
# Helper Function
# ==========================

def inventory_to_dict(row) -> dict:
    return {
        "inventory_id": row[0],
        "product_id": row[1],
        "product_name": row[2],
        "quantity": float(row[3]),
        "unit_id": row[4],
        "unit_name": row[5],
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
                    i.inventoryid,
                    i.productid,
                    p.productname,
                    i.quantity,
                    p.unitid,
                    u.unitname
                FROM inventory i
                INNER JOIN products p
                    ON i.productid = p.productid
                INNER JOIN units u
                    ON p.unitid = u.unitid
                ORDER BY p.productname;
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
                    i.inventoryid,
                    i.productid,
                    p.productname,
                    i.quantity,
                    p.unitid,
                    u.unitname
                FROM inventory i
                INNER JOIN products p
                    ON i.productid = p.productid
                INNER JOIN units u
                    ON p.unitid = u.unitid
                WHERE i.inventoryid = %s;
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
                    RETURNING inventoryid;
                    """,
                    (
                        item.product_id,
                        item.quantity,
                    ),
                )

                inventory_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO inventorytransaction
                    (
                        inventoryid,
                        quantitychange,
                        transactiontype,
                        notes
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        'InitialStock',
                        'Initial stock created with inventory item'
                    );
                    """,
                    (
                        inventory_id,
                        item.quantity,
                    ),
                )

                cursor.execute(
                    """
                    SELECT
                        i.inventoryid,
                        i.productid,
                        p.productname,
                        i.quantity,
                        p.unitid,
                        u.unitname
                    FROM inventory i
                    INNER JOIN products p
                        ON i.productid = p.productid
                    INNER JOIN units u
                        ON p.unitid = u.unitid
                    WHERE i.inventoryid = %s;
                    """,
                    (inventory_id,),
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
            detail="Product not found",
        )


# ==========================
# UPDATE INVENTORY ITEM
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
                SET quantity = %s
                WHERE inventoryid = %s
                RETURNING inventoryid;
                """,
                (
                    item.quantity,
                    inventory_id,
                ),
            )

            updated = cursor.fetchone()

            if updated is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventory item not found",
                )

            cursor.execute(
                """
                SELECT
                    i.inventoryid,
                    i.productid,
                    p.productname,
                    i.quantity,
                    p.unitid,
                    u.unitname
                FROM inventory i
                INNER JOIN products p
                    ON i.productid = p.productid
                INNER JOIN units u
                    ON p.unitid = u.unitid
                WHERE i.inventoryid = %s;
                """,
                (inventory_id,),
            )

            updated_item = cursor.fetchone()

    return inventory_to_dict(updated_item)


# ==========================
# DELETE INVENTORY ITEM
# ==========================

@router.delete(
    "/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_inventory_item(inventory_id: int):
    try:
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

    except (ForeignKeyViolation, RestrictViolation):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This inventory item cannot be deleted because it has "
                "inventory transaction history."
            ),
        )