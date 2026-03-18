from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from ..database import engine
from ..models import Game, Player, PlayerGame

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ADMIN_USER = "admin"
ADMIN_PASSWORD = "poker123"


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASSWORD:

        response = RedirectResponse("/admin", status_code=302)
        response.set_cookie("admin", "true")

        return response

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials"}
    )


@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("admin")

    return response


@router.get("/")
async def admin_home(request: Request):
    if not require_admin(request):
        return RedirectResponse("login")

    with Session(engine) as session:
        players = session.exec(select(Player)).all()

    return templates.TemplateResponse(
        "admin.html", 
        {
            "request": request,
            "players": players
        }
    )


@router.post("/game")
def create_game(
    request: Request,
    date: str = Form(...),
    buyin_value: str = Form(...),
    rebuy_value: str = Form(...),
    addon_value: str = Form(...),
    player_id: list[str] = Form(...),
    position: list[int] = Form(...),
    rebuys: list[int] = Form(...),
    addons: list[int] = Form(...),
    winnings: list[int] = Form(...),
):

    if not require_admin(request):
        return RedirectResponse("login")

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

        for i in range(len(player_id)):
            result = PlayerGame(
                game_id=game.id,
                player_id=player_id[i],
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
