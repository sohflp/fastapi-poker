from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select
from ..database import engine
from ..models import Player, Game, PlayerGame

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/timer")
async def timer(request: Request):
    return templates.TemplateResponse("timer.html", {"request": request})

@router.get("/stats")
def stats(request: Request, period: str | None = None):

    with Session(engine) as session:
        games = session.exec(select(Game)).all()
        players = session.exec(select(Player)).all()
        player_games = session.exec(select(PlayerGame)).all()

        player_stats = {}

        for pg in player_games:
            if pg.player_id not in player_stats:
                player_stats[pg.player_id] = {
                    "games": 0,
                    "buyins": 0,
                    "rebuys": 0,
                    "addons": 0,
                    "winnings": 0,
                }

            player_stats[pg.player_id]["games"] += 1
            player_stats[pg.player_id]["rebuys"] += pg.rebuys
            player_stats[pg.player_id]["addons"] += pg.addons
            player_stats[pg.player_id]["winnings"] += pg.winnings

        game_results = []

        for game in games:
            results = [
                pg for pg in player_games
                if pg.game_id == game.id
            ]

            game_results.append({
                "game": game,
                "results": results
            })

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "players": players,
            "player_stats": player_stats,
            "game_results": game_results
        }
    )