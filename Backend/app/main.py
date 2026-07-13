from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
from app.routers import products
from app.routers import units
from app.routers import inventory
from app.routers import inventory_transaction   
from app.routers import shopping_list
from app.routers import shopping_list_item
from app.routers import recipe  
from app.routers import recipe_ingredient


app = FastAPI(title="HomeOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(units.router)
app.include_router(inventory.router)
app.include_router(inventory_transaction.router)
app.include_router(shopping_list.router)    
app.include_router(shopping_list_item.router)   
app.include_router(recipe.router)
app.include_router(recipe_ingredient.router)

@app.get("/")
def root():
    return {"message": "HomeOS API is running"}
