from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import admin, reports, timer
from .database import create_db_and_tables

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(admin.router, prefix="/admin")
app.include_router(reports.router)
app.include_router(timer.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()