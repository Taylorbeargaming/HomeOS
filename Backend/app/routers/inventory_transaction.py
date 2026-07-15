from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from psycopg.errors import CheckViolation, ForeignKeyViolation

from app.database import get_connection


router = APIRouter(
    prefix="/inventory-transactions",
    tags=["Inventory Transactions"],
)


TransactionType = Literal[
    "Purchase",
    "Consumption",
    "Waste",
    "Adjustment",
    "TransferIn",
    "TransferOut",
    "InitialStock",
]


POSITIVE_TRANSACTION_TYPES = {
    "Purchase",
    "TransferIn",
    "InitialStock",
}

NEGATIVE_TRANSACTION_TYPES = {
    "Consumption",
    "Waste",
    "TransferOut",
}


# ==========================
# Pydantic Models
# ==========================

class InventoryTransactionCreate(BaseModel):
    inventory_id: int = Field(gt=0)
    quantity_change: Decimal = Field(
        ne=0,
        max_digits=12,
        decimal_places=3,
    )
    transaction_type: TransactionType
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None


class InventoryTransactionResponse(BaseModel):
    transaction_id: str
    inventory_id: int
    quantity_change: float
    transaction_type: str
    notes: Optional[str]
    transaction_date: datetime


# ==========================
# Helper Functions
# ==========================

def transaction_to_dict(row) -> dict:
    return {
        "transaction_id": str(row[0]),
        "inventory_id": row[1],
        "quantity_change": float(row[2]),
        "transaction_type": row[3],
        "notes": row[4],
        "transaction_date": row[5],
    }


def validate_quantity_change(
    transaction_type: str,
    quantity_change: Decimal,
) -> None:
    if (
        transaction_type in POSITIVE_TRANSACTION_TYPES
        and quantity_change <= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"{transaction_type} transactions require "
                "a positive quantity change"
            ),
        )

    if (
        transaction_type in NEGATIVE_TRANSACTION_TYPES
        and quantity_change >= 0
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"{transaction_type} transactions require "
                "a negative quantity change"
            ),
        )


# ==========================
# GET ALL TRANSACTIONS
# ==========================

@router.get(
    "",
    response_model=list[InventoryTransactionResponse],
)
def get_transactions():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    transactionid,
                    inventoryid,
                    quantitychange,
                    transactiontype,
                    notes,
                    transactiondate
                FROM inventorytransaction
                ORDER BY
                    transactiondate DESC,
                    createddate DESC;
                """
            )

            transactions = cursor.fetchall()

    return [
        transaction_to_dict(row)
        for row in transactions
    ]


# ==========================
# GET SINGLE TRANSACTION
# ==========================

@router.get(
    "/{transaction_id}",
    response_model=InventoryTransactionResponse,
)
def get_transaction(transaction_id: UUID):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    transactionid,
                    inventoryid,
                    quantitychange,
                    transactiontype,
                    notes,
                    transactiondate
                FROM inventorytransaction
                WHERE transactionid = %s;
                """,
                (transaction_id,),
            )

            transaction = cursor.fetchone()

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return transaction_to_dict(transaction)


# ==========================
# CREATE TRANSACTION
# ==========================

@router.post(
    "",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction: InventoryTransactionCreate,
):
    validate_quantity_change(
        transaction.transaction_type,
        transaction.quantity_change,
    )

    notes = (
        transaction.notes.strip()
        if transaction.notes
        else None
    )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:

                # Lock the inventory row until this database
                # transaction has completed.
                cursor.execute(
                    """
                    SELECT quantity
                    FROM inventory
                    WHERE inventoryid = %s
                    FOR UPDATE;
                    """,
                    (transaction.inventory_id,),
                )

                inventory = cursor.fetchone()

                if inventory is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Inventory item not found",
                    )

                current_quantity = inventory[0]

                new_quantity = (
                    current_quantity
                    + transaction.quantity_change
                )

                if new_quantity < 0:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "This transaction would make the "
                            "inventory quantity negative"
                        ),
                    )

                cursor.execute(
                    """
                    UPDATE inventory
                    SET quantity = %s
                    WHERE inventoryid = %s;
                    """,
                    (
                        new_quantity,
                        transaction.inventory_id,
                    ),
                )

                cursor.execute(
                    """
                    INSERT INTO inventorytransaction
                    (
                        inventoryid,
                        quantitychange,
                        transactiontype,
                        notes,
                        transactiondate
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        COALESCE(%s, CURRENT_TIMESTAMP)
                    )
                    RETURNING
                        transactionid,
                        inventoryid,
                        quantitychange,
                        transactiontype,
                        notes,
                        transactiondate;
                    """,
                    (
                        transaction.inventory_id,
                        transaction.quantity_change,
                        transaction.transaction_type,
                        notes,
                        transaction.transaction_date,
                    ),
                )

                created_transaction = cursor.fetchone()

        return transaction_to_dict(created_transaction)

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    except CheckViolation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The transaction does not satisfy the "
                "inventory transaction rules"
            ),
        )