from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import ForeignKeyViolation

from app.database import get_connection


router = APIRouter(
    prefix="/inventory-transactions",
    tags=["Inventory Transactions"],
)


# ==========================
# Pydantic Models
# ==========================

class InventoryTransactionCreate(BaseModel):
    inventory_id: int
    quantity_change: float
    transaction_type: str
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None


class InventoryTransactionUpdate(BaseModel):
    quantity_change: float
    transaction_type: str
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
# Helper Function
# ==========================

def transaction_to_dict(row):
    return {
        "transaction_id": str(row[0]),
        "inventory_id": row[1],
        "quantity_change": float(row[2]),
        "transaction_type": row[3],
        "notes": row[4],
        "transaction_date": row[5],
    }


# ==========================
# GET ALL
# ==========================

@router.get("", response_model=list[InventoryTransactionResponse])
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
                ORDER BY transactiondate DESC;
                """
            )

            rows = cursor.fetchall()

    return [transaction_to_dict(row) for row in rows]


# ==========================
# GET ONE
# ==========================

@router.get("/{transaction_id}", response_model=InventoryTransactionResponse)
def get_transaction(transaction_id: str):
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

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return transaction_to_dict(row)


# ==========================
# CREATE
# ==========================

@router.post(
    "",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(transaction: InventoryTransactionCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
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
                        transaction.notes,
                        transaction.transaction_date,
                    ),
                )

                created = cursor.fetchone()

        return transaction_to_dict(created)

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="Inventory item not found",
        )


# ==========================
# UPDATE
# ==========================

@router.put("/{transaction_id}", response_model=InventoryTransactionResponse)
def update_transaction(
    transaction_id: str,
    transaction: InventoryTransactionUpdate,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE inventorytransaction
                SET
                    quantitychange = %s,
                    transactiontype = %s,
                    notes = %s,
                    transactiondate = COALESCE(%s, transactiondate)
                WHERE transactionid = %s
                RETURNING
                    transactionid,
                    inventoryid,
                    quantitychange,
                    transactiontype,
                    notes,
                    transactiondate;
                """,
                (
                    transaction.quantity_change,
                    transaction.transaction_type,
                    transaction.notes,
                    transaction.transaction_date,
                    transaction_id,
                ),
            )

            updated = cursor.fetchone()

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return transaction_to_dict(updated)


# ==========================
# DELETE
# ==========================

@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(transaction_id: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM inventorytransaction
                WHERE transactionid = %s
                RETURNING transactionid;
                """,
                (transaction_id,),
            )

            deleted = cursor.fetchone()

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)