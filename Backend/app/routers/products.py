from typing import Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import (
    ForeignKeyViolation,
    RestrictViolation,
    UniqueViolation,
)

from app.database import get_connection


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# ==========================
# Pydantic Models
# ==========================

class ProductCreate(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    unit_id: int
    notes: Optional[str] = None


class ProductUpdate(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    unit_id: int
    notes: Optional[str] = None
    is_active: bool = True


class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    notes: Optional[str]
    is_active: bool
    unit_id: int
    unit_name: str


# ==========================
# Helper Function
# ==========================

def product_to_dict(row) -> dict:
    return {
        "product_id": row[0],
        "product_name": row[1],
        "notes": row[2],
        "is_active": row[3],
        "unit_id": row[4],
        "unit_name": row[5],
    }


# ==========================
# GET ALL PRODUCTS
# ==========================

@router.get("", response_model=list[ProductResponse])
def get_products():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.productid,
                    p.productname,
                    p.notes,
                    p.isactive,
                    p.unitid,
                    u.unitname
                FROM products p
                INNER JOIN units u
                    ON p.unitid = u.unitid
                ORDER BY p.productname;
                """
            )

            products = cursor.fetchall()

    return [product_to_dict(row) for row in products]


# ==========================
# GET SINGLE PRODUCT
# ==========================

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.productid,
                    p.productname,
                    p.notes,
                    p.isactive,
                    p.unitid,
                    u.unitname
                FROM products p
                INNER JOIN units u
                    ON p.unitid = u.unitid
                WHERE p.productid = %s;
                """,
                (product_id,),
            )

            product = cursor.fetchone()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product_to_dict(product)


# ==========================
# CREATE PRODUCT
# ==========================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: ProductCreate):
    product_name = product.product_name.strip()

    if not product_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product name cannot be blank",
        )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO products
                    (
                        productname,
                        notes,
                        unitid
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s
                    )
                    RETURNING productid;
                    """,
                    (
                        product_name,
                        product.notes,
                        product.unit_id,
                    ),
                )

                product_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT
                        p.productid,
                        p.productname,
                        p.notes,
                        p.isactive,
                        p.unitid,
                        u.unitname
                    FROM products p
                    INNER JOIN units u
                        ON p.unitid = u.unitid
                    WHERE p.productid = %s;
                    """,
                    (product_id,),
                )

                created_product = cursor.fetchone()

        return product_to_dict(created_product)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A product with this name already exists",
        )

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Unit ID.",
        )


# ==========================
# UPDATE PRODUCT
# ==========================

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    product_name = product.product_name.strip()

    if not product_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product name cannot be blank",
        )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE products
                    SET
                        productname = %s,
                        notes = %s,
                        unitid = %s,
                        isactive = %s
                    WHERE productid = %s
                    RETURNING productid;
                    """,
                    (
                        product_name,
                        product.notes,
                        product.unit_id,
                        product.is_active,
                        product_id,
                    ),
                )

                updated = cursor.fetchone()

                if updated is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found",
                    )

                cursor.execute(
                    """
                    SELECT
                        p.productid,
                        p.productname,
                        p.notes,
                        p.isactive,
                        p.unitid,
                        u.unitname
                    FROM products p
                    INNER JOIN units u
                        ON p.unitid = u.unitid
                    WHERE p.productid = %s;
                    """,
                    (product_id,),
                )

                updated_product = cursor.fetchone()

        return product_to_dict(updated_product)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A product with this name already exists",
        )

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Unit ID.",
        )


# ==========================
# DELETE PRODUCT
# ==========================

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(product_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM products
                    WHERE productid = %s
                    RETURNING productid;
                    """,
                    (product_id,),
                )

                deleted_product = cursor.fetchone()

        if deleted_product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except RestrictViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product cannot be deleted because it is referenced by other records.",
        )