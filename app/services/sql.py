from sqlalchemy import text 
from .points import POINTS_MAP

SQL_PLAYER_HISTORY = text(f"""
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
                WHEN pg.position = 1 THEN {POINTS_MAP[1]}
                WHEN pg.position = 2 THEN {POINTS_MAP[2]}
                WHEN pg.position = 3 THEN {POINTS_MAP[3]}
                WHEN pg.position = 4 THEN {POINTS_MAP[4]}
                WHEN pg.position = 5 THEN {POINTS_MAP[5]}
                WHEN pg.position = 6 THEN {POINTS_MAP[6]}
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