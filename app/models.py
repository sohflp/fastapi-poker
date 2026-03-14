from typing import Optional
from sqlmodel import SQLModel, Field

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str

class PlayerGame(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    player_name: str
    game_id: int
    rebuys: int = 0
    addons: int = 0
    position: int | None = None
    winnings: float = 0