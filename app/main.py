import uvicorn

from fastapi import FastAPI, Request
from app.api.endpoints.product import router as router_products
from app.api.endpoints.auth import router as router_auth
from app.api.endpoints.user import router as router_users
from app.api.endpoints.diary import router as router_diary
from app.api.endpoints.recipe import router as router_recipe
from app.api.endpoints.weight import router as router_weidht



app = FastAPI()

app.include_router(router=router_products)
app.include_router(router=router_auth)
app.include_router(router=router_users)
app.include_router(router=router_diary)
app.include_router(router=router_recipe)
app.include_router(router=router_weidht)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )