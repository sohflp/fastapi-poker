from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from ..database import engine
from ..models import Game, PlayerGame

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def admin_home(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")

    return templates.TemplateResponse("admin.html", {"request": request})


@router.post("/game")
def create_game(
    request: Request,
    date: str = Form(...),
    buyin_value: str = Form(...),
    rebuy_value: str = Form(...),
    addon_value: str = Form(...),
    player_name: list[str] = Form(...),
    position: list[int] = Form(...),
    rebuys: list[int] = Form(...),
    addons: list[int] = Form(...),
    winnings: list[int] = Form(...),
):

    if not require_admin(request):
        return RedirectResponse("/login")

    with Session(engine) as session:
        game = Game(
            date=date,
            buyin_value=buyin_value,
            rebuy_value=rebuy_value,
            addon_value=addon_value,
        )
        session.add(game)
        session.commit()
        session.refresh(game)

        for i in range(len(player_name)):
            result = PlayerGame(
                game_id=game.id,
                player_name=player_name[i],
                position=position[i],
                rebuys=rebuys[i],
                addons=addons[i],
                winnings=winnings[i],
            )

            session.add(result)

        session.commit()

    return RedirectResponse("/stats", status_code=302)


def require_admin(request: Request):
    if request.cookies.get("admin") != "true":
        return False

    return True