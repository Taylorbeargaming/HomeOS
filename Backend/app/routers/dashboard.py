from fastapi import APIRouter

from app.database import get_connection

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("")
def get_dashboard():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM products;")
            products = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM inventory;")
            inventory = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM shoppinglist;")
            shopping_lists = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM recipe;")
            recipes = cursor.fetchone()[0]

    return {
        "products": products,
        "inventory": inventory,
        "shopping_lists": shopping_lists,
        "recipes": recipes,
    }