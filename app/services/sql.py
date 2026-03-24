from sqlalchemy import text 

SQL_LEADERBOARD = text("""
WITH
    player_stats AS (
        SELECT
            p.id,
            p.name,
            SUM(CASE WHEN pg.position = 1 THEN 1 ELSE 0 END) AS `1st_count`,
            SUM(CASE WHEN pg.position = 2 THEN 1 ELSE 0 END) AS `2nd_count`,
            SUM(CASE WHEN pg.position = 3 THEN 1 ELSE 0 END) AS `3rd_count`
        FROM Player p
        LEFT JOIN PlayerGame pg ON p.id = pg.player_id
        GROUP BY p.id, p.name
    ),
    player_points AS (
        SELECT
            id,
            name,
            `1st_count` || "-" || `2nd_count` || "-" || `3rd_count` AS podium,
            (`1st_count` * 10) + (`2nd_count` * 5) + (`3rd_count` * 2) AS total_points
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

SQL_F1_LEADERBOARD = text("""
WITH
    player_stats AS (
        SELECT
            p.id,
            p.name,
            SUM(CASE WHEN pg.position = 1 THEN 1 ELSE 0 END) AS `1st_count`,
            SUM(CASE WHEN pg.position = 2 THEN 1 ELSE 0 END) AS `2nd_count`,
            SUM(CASE WHEN pg.position = 3 THEN 1 ELSE 0 END) AS `3rd_count`,
            SUM(CASE WHEN pg.position = 4 THEN 1 ELSE 0 END) AS `4th_count`,
            SUM(CASE WHEN pg.position = 5 THEN 1 ELSE 0 END) AS `5th_count`,
            SUM(CASE WHEN pg.position = 6 THEN 1 ELSE 0 END) AS `6th_count`
        FROM Player p
        LEFT JOIN PlayerGame pg ON p.id = pg.player_id
        GROUP BY p.id, p.name
    ),
    player_points AS (
        SELECT
            id,
            name,
            `1st_count` || "-" ||
            `2nd_count` || "-" ||
            `3rd_count` || "-" ||
            `4th_count` || "-" ||
            `5th_count` || "-" ||
            `6th_count` AS podium,
            (`1st_count` * 10) + 
            (`2nd_count` * 6) + 
            (`3rd_count` * 4) + 
            (`4th_count` * 3) + 
            (`5th_count` * 2) + 
            (`6th_count` * 1) AS total_points
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

SQL_PLAYER_HISTORY = text("""
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