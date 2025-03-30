import os
from fastapi import FastAPI
from app.routers import item_router, list_router

DEBUG = os.environ.get("DEBUG", "") == "true"

app = FastAPI(
    title="Python Backend Stations",
    debug=DEBUG,
)

if DEBUG:
    from debug_toolbar.middleware import DebugToolbarMiddleware

    # panelsに追加で表示するパネルを指定できる
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=["app.database.SQLAlchemyPanel"],
    )

@app.get("/echo", tags=["Hello"])
def get_echo(message: str, name: str):
    Message = f"{message} {name}!"
    return {"Message": Message}

@app.get("/health", tags=["System"])
def get_health():
    status = "ok"
    return {"status": status}

app.include_router(list_router.router)
app.include_router(item_router.router)