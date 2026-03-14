from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import auth, admin, pages
from .database import create_db_and_tables

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(admin.router, prefix="/admin")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()