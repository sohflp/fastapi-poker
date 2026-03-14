from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from ..database import engine
from ..models import Game, PlayerGame

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

BUY_IN_VALUE = 30

@router.get("/")
async def admin_home(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")

    return templates.TemplateResponse("admin.html", {"request": request})


@router.post("/game")
def create_game(
    request: Request,
    date: str = Form(...),
    player_name: list[str] = Form(...),
    rebuys: list[int] = Form(...),
    addons: list[int] = Form(...),
    position: list[int] = Form(...),
    profit: list[float] = Form(...)
):

    if not require_admin(request):
        return RedirectResponse("/login")

    with Session(engine) as session:
        game = Game(date=date, buy_in_value=BUY_IN_VALUE)
        session.add(game)
        session.commit()
        session.refresh(game)

        for i in range(len(player_name)):
            result = PlayerGame(
                game_id=game.id,
                player_name=player_name[i],
                rebuys=rebuys[i],
                addons=addons[i],
                position=position[i],
                winnings=profit[i]
            )

            session.add(result)

        session.commit()

    return RedirectResponse("/stats", status_code=302)


def require_admin(request: Request):
    if request.cookies.get("admin") != "true":
        return False

    return True