from collections import defaultdict

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select, desc
from ..database import engine
from ..models import Player, Game, PlayerGame
from ..services.sql import (
    SQL_PLAYER_HISTORY
)

from datetime import datetime

POINTS_MAP = {
    1: 10,
    2: 6,
    3: 4,
    4: 3,
    5: 2,
    6: 1
}

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
        players = session.exec(select(Player)).all()
        player_games = session.exec(select(PlayerGame)).all()

        stats = defaultdict(lambda: {
            "points": 0,
            "games": 0,
            "wins": 0,
            "positions": defaultdict(int)
        })

        for pg in player_games:
            player_id = pg.player_id
            pos = pg.position

            stats[player_id]["games"] += 1
            stats[player_id]["positions"][pos] += 1

            # Points
            stats[player_id]["points"] += POINTS_MAP.get(pos, 0)

            # Wins
            if pos == 1:
                stats[player_id]["wins"] += 1

        # Build final result list
        results = []

        for p in players:
            s = stats.get(p.id, {})

            results.append({
                "name": p.name,
                "points": s.get("points", 0),
                "games": s.get("games", 0),
                "wins": s.get("wins", 0),
                "positions": dict(s.get("positions", {}))
            })

        # 🔥 Sort leaderboard
        results.sort(
            key=lambda x: (
                x["points"],   # primary
                x["wins"],     # tie-breaker
                x["games"]     # activity
            ),
            reverse=True
        )

    return templates.TemplateResponse(
        "reports/leaderboard.html",
        {
            "request": request,
            "results": results
        }
    )


@router.get("/games")
def games(request: Request, period: int | None = None):

    with Session(engine) as session:
        games = session.exec(select(Game).order_by(desc("date"))).all()
        players = session.exec(select(Player)).all()
        player_games = session.exec(select(PlayerGame)).all()

        # Create a lookup table for players
        player_lookup = {p.id: p.name for p in players}

        # Build final result list
        results = []

        for game in games:
            ranking = [
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

            results.append({
                "game": game,
                "ranking": ranking
            })

    return templates.TemplateResponse(
        "reports/games.html",
        {
            "request": request,
            "results": results
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
        results.sort(
            key=lambda x: (
                x["net"],
                x["games"]
            ),
            reverse=True
        )

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
