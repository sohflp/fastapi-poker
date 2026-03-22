from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select, desc
from ..database import engine
from ..models import Player, Game, PlayerGame
from ..services.sql import (
    SQL_LEADERBOARD,
    SQL_F1_LEADERBOARD,
    SQL_PLAYER_HISTORY
)

from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def home(request: Request):
    return RedirectResponse("leaderboard")


@router.get("/leaderboard")
def stats(request: Request, period: str | None = None):

    with Session(engine) as session:
        # Select all data from all the tables
        games = session.exec(select(Game).order_by(desc(Game.date))).all()
        player_games = session.exec(select(PlayerGame)).all()
        players = session.exec(select(Player)).all()

        # Create a lookup table for players
        player_lookup = {p.id: p.name for p in players}

        # Calculate player leaderboard
        leaderboard = session.exec(SQL_LEADERBOARD).fetchall()

        # Calculate game results
        game_results = []
        for game in games:
            results = [
                {
                    "name": player_lookup.get(pg.player_id),
                    "position": pg.position,
                    "rebuys": pg.rebuys,
                    "addons": pg.addons,
                    "winnings": pg.winnings
                }
                for pg in player_games
                if pg.game_id == game.id
            ]

            game_results.append({
                "game": game,
                "results": results
            })

    return templates.TemplateResponse(
        "reports/leaderboard.html",
        {
            "request": request,
            "leaderboard": leaderboard,
            "game_results": game_results
        }
    )


@router.get("/f1leaderboard")
def stats(request: Request, period: str | None = None):

    with Session(engine) as session:
        # Select all data from all the tables
        games = session.exec(select(Game).order_by(desc(Game.date))).all()
        player_games = session.exec(select(PlayerGame)).all()
        players = session.exec(select(Player)).all()

        # Create a lookup table for players
        player_lookup = {p.id: p.name for p in players}

        # Calculate player F1 leaderboard
        leaderboard = session.exec(SQL_F1_LEADERBOARD).fetchall()

        # Calculate game results
        game_results = []
        for game in games:
            results = [
                {
                    "name": player_lookup.get(pg.player_id),
                    "position": pg.position,
                    "rebuys": pg.rebuys,
                    "addons": pg.addons,
                    "winnings": pg.winnings
                }
                for pg in player_games
                if pg.game_id == game.id
            ]

            game_results.append({
                "game": game,
                "results": results
            })

    return templates.TemplateResponse(
        "reports/leaderboard.html",
        {
            "request": request,
            "leaderboard": leaderboard,
            "game_results": game_results,
            "f1_mode": True
        }
    )


@router.get("/performance")
def stats(request: Request, period: str | None = None):

    with Session(engine) as session:
        # Select game and player data
        games = session.exec(select(Game).order_by(desc(Game.date))).all()
        players = session.exec(select(Player)).all()

        # Extract game dates only
        game_dates = [game.date for game in games]

        # Select player history
        player_history = session.exec(SQL_PLAYER_HISTORY).fetchall()

        # Combine game, player and performance results for the line chart
        performance = {
            "labels": game_dates,
            "datasets": [
                {
                    "label": player.name,
                    "data": [
                        history.total_points
                        for history in player_history
                        if history.player_id == player.id
                    ],
                    "hidden": False # Update later (if required)
                }
                for player in players
            ]
        }

    return templates.TemplateResponse(
        "reports/performance.html",
        {
            "request": request,
            "performance": performance
        }
    )


# Define a custom filter function
def format_datetime(value, fmt='%d/%m/%Y'):
    if value is None:
        return ""

    # Ensure the value is a datetime object if it comes in as a string
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d') # Adjust format as needed

    return value.strftime(fmt)

# Add the custom filter to the Jinja environment
templates.env.filters["format_datetime"] = format_datetime
