from collections import defaultdict

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
def dashboard(request: Request, period: int | None = None):

    with Session(engine) as session:
        games = session.exec(select(Game)).all()
        players = session.exec(select(Player)).all()
        player_games = session.exec(select(PlayerGame)).all()

        total_games = len(games)
        total_players = len(players)

        total_buyins = len(player_games)  # each entry = one buy-in
        total_rebuys = sum(pg.rebuys for pg in player_games)
        total_addons = sum(pg.addons for pg in player_games)

        # Build lookup: game_id → values
        game_lookup = {
            g.id: {
                "buyin": g.buyin_value,
                "rebuy": g.rebuy_value,
                "addon": g.addon_value
            }
            for g in games
        }

        total_collected = 0

        for pg in player_games:
            game = game_lookup.get(pg.game_id, {})

            total_collected += (
                game.get("buyin", 0) +
                pg.rebuys * game.get("rebuy", 0) +
                pg.addons * game.get("addon", 0)
            )

    return templates.TemplateResponse(
        "reports/dashboard.html",
        {
            "request": request,
            "total_games": total_games,
            "total_players": total_players,
            "total_collected": total_collected,
            "total_buyins": total_buyins,
            "total_rebuys": total_rebuys,
            "total_addons": total_addons
        }
    )


@router.get("/leaderboard")
def stats(request: Request, period: int | None = None):

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
def stats(request: Request, period: int | None = None):

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


@router.get("/finance")
def stats(request: Request, period: int | None = None):

    with Session(engine) as session:
        # Select all data from all the tables
        players = session.exec(select(Player)).all()
        games = session.exec(select(Game)).all()
        player_games = session.exec(select(PlayerGame)).all()

        # Game values lookup
        game_lookup = {
            g.id: {
                "buyin": g.buyin_value,
                "rebuy": g.rebuy_value,
                "addon": g.addon_value
            }
            for g in games
        }

        stats = defaultdict(lambda: {
            "games": 0,
            "rebuys": 0,
            "addons": 0,
            "winnings": 0,
            "expenses": 0
        })

        for pg in player_games:
            game = game_lookup.get(pg.game_id, {})

            stats[pg.player_id]["games"] += 1
            stats[pg.player_id]["rebuys"] += pg.rebuys
            stats[pg.player_id]["addons"] += pg.addons
            stats[pg.player_id]["winnings"] += pg.winnings

            stats[pg.player_id]["expenses"] += (
                game.get("buyin", 0)
                + pg.rebuys * game.get("rebuy", 0)
                + pg.addons * game.get("addon", 0)
            )

        results = []
        for p in players:
            s = stats.get(p.id, {})

            winnings = s.get("winnings", 0)
            expenses = s.get("expenses", 0)

            net = winnings - expenses

            roi = (net / expenses * 100) if expenses > 0 else 0

            results.append({
                "name": p.name,
                "games": s.get("games", 0),
                "rebuys": s.get("rebuys", 0),
                "addons": s.get("addons", 0),
                "winnings": winnings,
                "expenses": expenses,
                "net": net,
                "roi": round(roi, 1)
            })

        # 🔥 Sort: Net Profit DESC, then Games DESC
        results.sort(key=lambda x: (x["net"], x["games"]), reverse=True)

    return templates.TemplateResponse(
        "reports/finance.html",
        {
            "request": request,
            "results": results
        }
    )

@router.get("/performance")
def stats(request: Request, period: int | None = None):

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
