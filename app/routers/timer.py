from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/timer")
async def timer(request: Request):
    return templates.TemplateResponse("timer.html", {"request": request})
