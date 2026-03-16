from typing import Optional
from sqlmodel import SQLModel, Field

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str
    buyin_value: int = 30
    rebuy_value: int = 25
    addon_value: int = 25

class PlayerGame(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    player_id: int
    game_id: int
    position: int | None = None
    rebuys: int = 0
    addons: int = 0
    winnings: int = 0