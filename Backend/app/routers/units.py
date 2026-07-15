from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.database import get_connection


router = APIRouter(
    prefix="/units",
    tags=["Units"],
)


# ==========================
# Pydantic Models
# ==========================

class UnitCreate(BaseModel):
    unit_name: str = Field(min_length=1, max_length=255)
    abbreviation: str = Field(min_length=1, max_length=20)


class UnitUpdate(BaseModel):
    unit_name: str = Field(min_length=1, max_length=255)
    abbreviation: str = Field(min_length=1, max_length=20)
    is_active: bool = True


class UnitResponse(BaseModel):
    unit_id: int
    unit_name: str
    abbreviation: str
    is_active: bool


# ==========================
# Helper Function
# ==========================

def unit_to_dict(row) -> dict:
    return {
        "unit_id": row[0],
        "unit_name": row[1],
        "abbreviation": row[2],
        "is_active": row[3],
    }


# ==========================
# GET ALL UNITS
# ==========================

@router.get("", response_model=list[UnitResponse])
def get_units():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    unitid,
                    unitname,
                    abbreviation,
                    isactive
                FROM units
                ORDER BY unitname;
                """
            )

            units = cursor.fetchall()

    return [unit_to_dict(row) for row in units]


# ==========================
# GET SINGLE UNIT
# ==========================

@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    unitid,
                    unitname,
                    abbreviation,
                    isactive
                FROM units
                WHERE unitid = %s;
                """,
                (unit_id,),
            )

            unit = cursor.fetchone()

    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        )

    return unit_to_dict(unit)


# ==========================
# CREATE UNIT
# ==========================

@router.post(
    "",
    response_model=UnitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_unit(unit: UnitCreate):
    unit_name = unit.unit_name.strip()
    abbreviation = unit.abbreviation.strip()

    if not unit_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unit name cannot be blank",
        )

    if not abbreviation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Abbreviation cannot be blank",
        )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO units
                    (
                        unitname,
                        abbreviation
                    )
                    VALUES
                    (
                        %s,
                        %s
                    )
                    RETURNING
                        unitid,
                        unitname,
                        abbreviation,
                        isactive;
                    """,
                    (
                        unit_name,
                        abbreviation,
                    ),
                )

                created_unit = cursor.fetchone()

        return unit_to_dict(created_unit)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A unit with this name or abbreviation already exists",
        )


# ==========================
# UPDATE UNIT
# ==========================

@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(unit_id: int, unit: UnitUpdate):
    unit_name = unit.unit_name.strip()
    abbreviation = unit.abbreviation.strip()

    if not unit_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unit name cannot be blank",
        )

    if not abbreviation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Abbreviation cannot be blank",
        )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE units
                    SET
                        unitname = %s,
                        abbreviation = %s,
                        isactive = %s
                    WHERE unitid = %s
                    RETURNING
                        unitid,
                        unitname,
                        abbreviation,
                        isactive;
                    """,
                    (
                        unit_name,
                        abbreviation,
                        unit.is_active,
                        unit_id,
                    ),
                )

                updated_unit = cursor.fetchone()

        if updated_unit is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found",
            )

        return unit_to_dict(updated_unit)

    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A unit with this name or abbreviation already exists",
        )


# ==========================
# DELETE UNIT
# ==========================

@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_unit(unit_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM units
                    WHERE unitid = %s
                    RETURNING unitid;
                    """,
                    (unit_id,),
                )

                deleted_unit = cursor.fetchone()

        if deleted_unit is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This unit cannot be deleted because it is assigned "
                "to a product or recipe ingredient."
            ),
        )