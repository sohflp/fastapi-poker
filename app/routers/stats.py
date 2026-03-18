from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from sqlalchemy import text 
from sqlmodel import Session, select, desc
from ..database import engine
from ..models import Player, Game, PlayerGame

from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

SQL_LEADERBOARD = text("""
WITH
    player_stats AS (
        SELECT
            p.id,
            p.name,
            SUM(CASE WHEN pg.position = 1 THEN 1 ELSE 0 END) AS first_count,
            SUM(CASE WHEN pg.position = 2 THEN 1 ELSE 0 END) AS second_count,
            SUM(CASE WHEN pg.position = 3 THEN 1 ELSE 0 END) AS third_count
        FROM Player p
        LEFT JOIN PlayerGame pg ON p.id = pg.player_id
        GROUP BY p.id, p.name
    ),
    player_points AS (
        SELECT
            id,
            name,
            first_count || "-" || second_count || "-" || third_count AS podium,
            (first_count * 10) + (second_count * 5) + (third_count * 2) AS total_points
        FROM player_stats
    )
SELECT
    RANK() OVER (
        ORDER BY total_points DESC
    ) AS rank,
    id,
    name,
    podium,
    total_points
FROM player_points
ORDER BY rank, podium desc;
""")

SQL_GAME_HISTORY = text("""
WITH 
    game_dates AS (
        SELECT DISTINCT date
        FROM game
    ),

    players AS (
        SELECT id AS player_id
        FROM Player
    ),

    -- All combinations: player × date
    player_dates AS (
        SELECT
            p.player_id,
            d.date
        FROM players p
        CROSS JOIN game_dates d
    ),

    -- Points per game
    points_per_game AS (
        SELECT
            pg.player_id,
            g.date,
            CASE
                WHEN pg.position = 1 THEN 10
                WHEN pg.position = 2 THEN 5
                WHEN pg.position = 3 THEN 2
                ELSE 0
            END AS points
        FROM PlayerGame pg
        JOIN game g ON pg.game_id = g.id
    ),

    -- Cumulative points ONLY where games exist
    cumulative_points AS (
        SELECT
            player_id,
            date,
            SUM(points) OVER (
                PARTITION BY player_id
                ORDER BY date
            ) AS total_points
        FROM points_per_game
    )

-- Final: fill missing dates
SELECT
    pd.player_id,
    COALESCE(
        (
            SELECT cp.total_points
            FROM cumulative_points cp
            WHERE cp.player_id = pd.player_id
              AND cp.date <= pd.date
            ORDER BY cp.date DESC
            LIMIT 1
        ),
        0
    ) AS total_points
FROM player_dates pd
ORDER BY pd.player_id, pd.date DESC;
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

        # Calculate player leaderboard
        leaderboard = session.exec(SQL_LEADERBOARD).fetchall()

        # Calculate game dates and results
        game_dates = []
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

            game_dates.append(game.date)
            game_results.append({
                "game": game,
                "results": results
            })

        # Calculate player performance history
        game_history = session.exec(SQL_GAME_HISTORY).fetchall()
        player_history = {
            "labels": game_dates,
            "datasets": [
                {
                    "label": f"{player.rank}. {player.name}",
                    "data": [
                        history.total_points
                        for history in game_history
                        if history.player_id == player.id
                    ],
                    "hidden": True if player.rank > 5 else False
                }
                for player in leaderboard
            ]
        }

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "leaderboard": leaderboard,
            "game_results": game_results,
            "player_history": player_history
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
