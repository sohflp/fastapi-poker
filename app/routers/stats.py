from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from sqlalchemy import text 
from sqlmodel import Session, select, desc
from ..database import engine
from ..models import Player, Game, PlayerGame

from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

SQL_STATEMENT = text("""
    WITH player_stats AS (
        SELECT
            p.id,
            p.name,
            SUM(CASE WHEN pg.position = 1 THEN 1 ELSE 0 END) AS first_count,
            SUM(CASE WHEN pg.position = 2 THEN 1 ELSE 0 END) AS second_count,
            SUM(CASE WHEN pg.position = 3 THEN 1 ELSE 0 END) AS third_count
        FROM Player p
        LEFT JOIN PlayerGame pg ON p.id = pg.player_id
        GROUP BY p.id, p.name
    )
    SELECT
        RANK() OVER (
            ORDER BY
                first_count DESC,
                second_count DESC,
                third_count DESC
        ) AS overall_position,
        name,
        first_count,
        second_count,
        third_count
    FROM player_stats
    ORDER BY overall_position;
""")


@router.get("/stats")
def stats(request: Request, period: str | None = None):

    with Session(engine) as session:
        # Select all data from all the tables
        games = session.exec(select(Game).order_by(desc(Game.date))).all()
        player_games = session.exec(select(PlayerGame)).all()
        players = session.exec(select(Player)).all()

        # Create a lookup table for players
        player_lookup = {p.id: p.name for p in players}

        # Calculate player stats via custom SQL statement
        player_stats = session.exec(SQL_STATEMENT)
        
        # Calculate game results via Python logic
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
        "stats.html",
        {
            "request": request,
            "player_stats": player_stats,
            "game_results": game_results
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
